#!/usr/bin/env python3
"""
COLETA DO PILOTO DE SENSORES TÉCNICOS — canal e conteúdo das identidades provadas.

    python3 scripts/sensor_coleta.py contratos     # GRÁTIS: lê o contrato de entrada
    python3 scripts/sensor_coleta.py canais        # descobre canal público das pessoas
    python3 scripts/sensor_coleta.py videos        # vídeos dos recortes, por termo técnico
    python3 scripts/sensor_coleta.py transcricao   # transcrição dos vídeos achados

A ORDEM É LEI, E ELA VEM DO ÁRBITRO
------------------------------------
    RECORTE -> IDENTIDADE -> CANAL PÚBLICO -> CONTEÚDO

Este arquivo cuida das duas últimas etapas. As duas primeiras já estão fechadas em
`SPEAKER-UNIVERSE-PILOT-V1.json`: 6 recortes congelados, 12 identidades provadas.

POR QUE `contratos` EXISTE, E POR QUE ELE RODA PRIMEIRO
--------------------------------------------------------
O piloto italiano queimou 8 execuções pagas mandando uma entrada que o ator ignorava — os
8 runs devolveram **o mesmo consultor de cibersegurança**, porque o Actor descartou o campo
que ele não reconhecia e caiu num comportamento padrão. Ninguém errou o alvo: ninguém
tinha lido o contrato.

    MATCH VAZIO NÃO AUTORIZA GASTO. CONTRATO ERRADO != PLATAFORMA ERRADA.

Ler o schema de entrada custa ZERO — é um GET no ator, não um run. Então ele vem antes.

A ROTAÇÃO NÃO É REESCRITA AQUI
-------------------------------
`apify_pool.py` é o dono de "quando trocar de chave e quando não trocar", e `coletor.py` é
a porta única das rotas pagas — grava o RAW antes de normalizar e captura os cinco campos
de execução que a plataforma só dá no objeto do run. Este arquivo COSTURA os dois; não
reimplementa nenhum. Reimplementar criaria duas verdades, e a segunda divergiria na
primeira pressa.

O QUE A COTA GRATUITA FAZ, E POR QUE ISSO NÃO É "SEM RESULTADO"
-----------------------------------------------------------------
Conta gratuita da Apify tem teto de execuções por ator. Ao estourar, o ator devolve
`SUCCEEDED`, `exitCode` limpo e ZERO itens, com `statusMessage: "free user run limit
reached"`. É cota esgotada disfarçada de sucesso. `coletor.executar()` já marca isso como
`PARTIAL`; aqui esse mesmo sinal manda **trocar de posição do pool** e repetir a unidade —
nunca repetir na mesma chave, que só gastaria de novo para receber o mesmo vazio.

IDENTIDADE DE CANAL — o que este arquivo NUNCA faz
----------------------------------------------------
Um resultado de busca por nome NÃO é a pessoa.

    a busca por "Pasquale De Vita" devolveu o presidente da Unione Petrolifera, um
    vendedor de esquadrias e um diretor de TI, todos de nome idêntico.

Então todo candidato a canal sai daqui com `CHANNEL_IDENTITY_STATE` e a evidência que o
sustenta. E `PERSON_OWN_CHANNEL` é separado de `INSTITUTIONAL_CHANNEL_FEATURING_PERSON`:
um vídeo do INRAE em que a pessoa aparece é canal do INRAE, não canal dela.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import apify_pool as ap        # noqa: E402  — dono único da rotação
import coletor                 # noqa: E402  — porta única das rotas pagas
import proveniencia as pv      # noqa: E402

SAMPLES = os.path.join(ROOT, 'data', 'samples')
UNIVERSO = os.path.join(SAMPLES, 'SPEAKER-UNIVERSE-PILOT-V1.json')
SAIDA = os.path.join(SAMPLES, 'SENSOR-PILOT')

MISSION = '13-PILOTO-SENSORES-TECNICOS'

# Atores candidatos. Os cinco primeiros já foram medidos na rodada espanhola; o de busca
# por nome veio do piloto italiano. Nomes no formato da API (til separa dono e ator).
ATORES = {
    'LINKEDIN_SEARCH_BY_NAME': 'harvestapi~linkedin-profile-search-by-name',
    'LINKEDIN_PROFILE_SEARCH': 'harvestapi~linkedin-profile-search',
    'LINKEDIN_PROFILE': 'harvestapi~linkedin-profile-scraper',
    'LINKEDIN_POSTS': 'harvestapi~linkedin-post-search',
    'YOUTUBE_SEARCH': 'streamers~youtube-scraper',
    'YOUTUBE_TRANSCRIPT': 'pintostudio~youtube-transcript-scraper',
    'YOUTUBE_COMMENTS': 'streamers~youtube-comments-scraper',
}


def _carregar_pessoas():
    with open(UNIVERSO, encoding='utf-8') as f:
        d = json.load(f)
    # Só quem tem identidade provada entra na coleta. Quem ficou PARTIAL fica de fora e
    # continua registrado — não é descarte, é não gastar em quem o portão barrou.
    return [p for p in d['PEOPLE'] if p['IDENTITY_STATE'].startswith('IDENTITY_PROVED')]


def _gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    caminho = os.path.join(SAIDA, nome)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return os.path.relpath(caminho, ROOT).replace('\\', '/')


# ══════════════════════════════════════════════════════ FASE 0 · CONTRATOS (grátis)
def contratos():
    """GET no ator. Zero run, zero item, zero custo — e evita a entrada errada."""
    chaves = ap.pool()
    if not chaves:
        print('POOL_EMPTY'); return 1
    token = chaves[0]
    fora = []
    for rotulo, actor in ATORES.items():
        try:
            d = coletor._curl('%s/acts/%s' % (coletor.API, actor),
                              token=token, timeout=60, tentativas=2)
        except Exception as e:                                # noqa: BLE001
            # A MENSAGEM, não só o nome da classe. A primeira versão imprimia só
            # `TypeError` para os sete atores, e um nome de classe sem mensagem não
            # diz o que quebrou — obriga a gastar outra execução para descobrir.
            motivo = ap.redigir('%s: %s' % (type(e).__name__, e))[:300]
            print('%-26s INDISPONIVEL  %s' % (rotulo, motivo))
            fora.append({'LABEL': rotulo, 'ACTOR': actor, 'STATE': 'NOT_REACHED',
                         'REASON': motivo})
            continue
        if d.get('error'):
            print('%-26s RECUSADO      %s' % (rotulo, str(d['error'].get('type'))[:40]))
            fora.append({'LABEL': rotulo, 'ACTOR': actor, 'STATE': 'NOT_FOUND',
                         'REASON': str(d['error'].get('message'))[:200]})
            continue
        a = d.get('data') or {}
        campos, exemplo = [], {}
        # O schema vive no build default. Ler dali é o que revela o nome REAL dos campos.
        try:
            bid = ((a.get('taggedBuilds') or {}).get('latest') or {}).get('buildId')
            if bid:
                b = coletor._curl('%s/actor-builds/%s' % (coletor.API, bid),
                                  token=token, timeout=60, tentativas=2)
                sch = (((b.get('data') or {}).get('inputSchema')) or '')
                if isinstance(sch, str) and sch.strip():
                    sch = json.loads(sch)
                if isinstance(sch, dict):
                    props = sch.get('properties') or {}
                    campos = sorted(props)
                    exemplo = {k: (props[k].get('prefill')
                                   if props[k].get('prefill') is not None
                                   else props[k].get('default'))
                               for k in campos if k in props}
        except Exception as e:                                # noqa: BLE001
            campos = ['LEITURA_DO_SCHEMA_FALHOU: %s' % type(e).__name__]
        print('%-26s OK  %s/%s  campos=%d' % (
            rotulo, a.get('username'), a.get('name'), len(campos)))
        if campos:
            print('      %s' % ', '.join(campos[:14]))
        fora.append({'LABEL': rotulo, 'ACTOR': actor, 'STATE': 'AVAILABLE',
                     'OWNER': a.get('username'), 'NAME': a.get('name'),
                     'INPUT_FIELDS': campos, 'PREFILL': exemplo})
    caminho = _gravar('CONTRATOS-DE-ENTRADA.json', {
        'SOURCE_ID': 'SENSOR-PILOT/CONTRATOS-DE-ENTRADA',
        'source': 'GET /v2/acts/{actor} e /v2/actor-builds/{id} — leitura, zero run',
        'SOURCE_LOCATION': 'Apify', 'FACT_LOCATION': 'n/a — descreve ferramenta',
        'ORIGINAL_LANGUAGE': 'en',
        'APIFY_RUNS': 0, 'ITEMS': 0, 'COST_USD': 0,
        'POR_QUE_EXISTE': ('o piloto italiano gastou 8 execuções mandando entrada que o '
                           'ator ignorava, e os 8 runs devolveram a mesma pessoa errada. '
                           'Ler o contrato custa zero.'),
        'ACTORS': fora,
    })
    print('\ngravado:', caminho)
    return 0


# ══════════════════════════════════════════════════════ execução com rotação de pool
def _rodar(actor, entrada, *, run_id, platform, country, query, evidence_path):
    """Roda pelo coletor, trocando de chave só quando a CHAVE é o problema.

    Devolve (itens, manifesto, posicao_usada). Cota esgotada de uma posição não é
    "sem resultado": é motivo de trocar de posição e repetir a MESMA unidade.
    """
    chaves = ap.pool()
    ultimo = (None, None)
    for pos, token in enumerate(chaves, 1):
        itens, man = coletor.executar(
            actor, entrada, token=token, run_id='%s-p%d' % (run_id, pos),
            platform=platform, country=country, mission=MISSION, query=query,
            source_version='captura de %s' % coletor.agora()[:10],
            evidence_path=evidence_path)
        estado = ap.classificar(status=None if man['STATUS'] == 'FAILED' else 'SUCCEEDED',
                                status_message=str(man.get('ERROR') or ''),
                                itens=itens)
        ultimo = (itens, man)
        if itens:
            return itens, man, pos
        if estado in ap.ROTACIONAM:
            print('      posicao %d esgotada (%s) -> trocando' % (pos, estado))
            continue
        # Vazio sem sinal de cota é resposta legítima da rota: não gastar outra chave.
        return itens, man, pos
    return ultimo[0], ultimo[1], len(chaves)


# ══════════════════════════════════════════════════════ FASE 1 · CANAIS
def canais():
    """Procura canal público das pessoas provadas. LinkedIn por nome + YouTube por nome."""
    pessoas = _carregar_pessoas()
    print('pessoas provadas: %d' % len(pessoas))
    contratos_path = os.path.join(SAIDA, 'CONTRATOS-DE-ENTRADA.json')
    if not os.path.exists(contratos_path):
        print('SEM_CONTRATO_NAO_GASTEI — rode a fase `contratos` primeiro'); return 1
    with open(contratos_path, encoding='utf-8') as f:
        cont = {a['LABEL']: a for a in json.load(f)['ACTORS']}

    achados, manifestos, runs, custo = [], [], 0, 0.0
    for p in pessoas:
        nome, pais = p['NAME'], p['COUNTRY']
        print('  %s (%s · %s)' % (nome, pais, p['CASE_ID']))

        # --- YouTube: onde a pessoa APARECE. Pode ser canal dela ou de instituição.
        yt = cont.get('YOUTUBE_SEARCH')
        if yt and yt['STATE'] == 'AVAILABLE':
            termo = '%s %s' % (nome, (p['INSTITUTION'] or '').split(',')[0])
            entrada = {'searchQueries': [termo], 'maxResults': 12,
                       'maxResultsShorts': 0, 'maxResultStreams': 0}
            rid = 'SENSOR-YT-%s-%s' % (p['CASE_ID'], _slug(nome))
            itens, man, pos = _rodar(
                ATORES['YOUTUBE_SEARCH'], entrada, run_id=rid, platform='YOUTUBE',
                country=pais, query=termo,
                evidence_path='data/samples/SENSOR-PILOT/CANAIS.json')
            runs += 1
            custo += _usd(man)
            manifestos.append(man)
            for v in (itens or []):
                achados.append(_candidato_video(v, p, termo))
            print('      YouTube: %d itens (posicao %d, %s)'
                  % (len(itens or []), pos, man['STATUS']))
        time.sleep(1)

    corpo = _envelope_canais(pessoas, achados, runs, custo, manifestos)
    caminho = _gravar('CANAIS.json', corpo)
    for m in manifestos:
        coletor.registrar(m)
    print('\ngravado: %s · candidatos=%d · runs=%d · custo=%.4f USD'
          % (caminho, len(achados), runs, custo))
    return 0


def _slug(s):
    return ''.join(c if c.isalnum() else '-' for c in (s or '')).strip('-')[:40]


def _usd(man):
    v = man.get('COST_USD')
    return float(v) if isinstance(v, (int, float)) else 0.0


def _candidato_video(v, p, termo):
    """Um item de busca vira CANDIDATO, nunca canal provado."""
    canal = v.get('channelName') or v.get('channelTitle') or pv.NAO_SEI
    titulo = v.get('title') or pv.NAO_SEI
    # A pessoa é DONA do canal, ou APARECE nele? O nome do canal decide o candidato, e a
    # decisão fica explícita — nunca implícita.
    sobren = (p['NAME'] or '').split()[-1].lower()
    parece_dela = sobren and sobren in (canal or '').lower()
    return {
        'PERSON_ID': p['PERSON_ID'], 'NAME': p['NAME'], 'CASE_ID': p['CASE_ID'],
        'COUNTRY_OF_PERSON': p['COUNTRY'],
        'PLATFORM': 'YOUTUBE',
        'SOURCE_URL': v.get('url') or v.get('link') or pv.NAO_SEI,
        'TITLE': titulo,
        'CHANNEL': canal,
        'CHANNEL_URL': v.get('channelUrl') or pv.NAO_SEI,
        'SOURCE_ENTITY': canal,
        'PUBLISHED_AT': v.get('date') or v.get('publishedAt') or pv.NAO_SEI,
        'DURATION': v.get('duration') or pv.NAO_SEI,
        'VIEWS': v.get('viewCount') if v.get('viewCount') is not None else pv.NAO_SEI,
        'DESCRIPTION': (v.get('text') or v.get('description') or '')[:4000] or pv.NAO_SEI,
        'VIDEO_ID': v.get('id') or v.get('videoId') or pv.NAO_SEI,
        'CHANNEL_KIND': ('PERSON_OWN_CHANNEL_CANDIDATE' if parece_dela
                         else 'INSTITUTIONAL_CHANNEL_FEATURING_PERSON_CANDIDATE'),
        'CHANNEL_IDENTITY_STATE': 'NOT_PROVED',
        'CHANNEL_IDENTITY_EVIDENCE': (
            'veio da busca "%s". SEARCH_HIT != PERSON: o nome no resultado não prova que '
            'a pessoa é esta, e o nome do canal não prova que o canal é dela.' % termo),
        'CAPTURED_AT': coletor.agora(),
        'TRANSCRIPT_AVAILABLE': 'NOT_TESTED',
    }


def _envelope_canais(pessoas, achados, runs, custo, manifestos):
    por_pessoa = {}
    for a in achados:
        por_pessoa[a['NAME']] = por_pessoa.get(a['NAME'], 0) + 1
    return {
        'SOURCE_ID': 'SENSOR-PILOT/CANAIS',
        'source': 'busca pública por nome+instituição via Apify, rota YouTube',
        'SOURCE_LOCATION': 'YouTube',
        'FACT_LOCATION': 'NOT_KNOWN — o lugar do fato sai do conteúdo, nunca da busca',
        'ORIGINAL_LANGUAGE': 'multi',
        'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
        'CAPTURED_AT': coletor.agora(),
        'MISSION': MISSION,
        'PEOPLE_QUERIED': len(pessoas),
        'PEOPLE_WITH_AT_LEAST_ONE_HIT': len(por_pessoa),
        'PEOPLE_WITH_ZERO_HITS': [p['NAME'] for p in pessoas
                                  if p['NAME'] not in por_pessoa],
        'CANDIDATES': len(achados),
        'HITS_BY_PERSON': por_pessoa,
        'APIFY_RUNS': runs,
        'COST_USD': round(custo, 6),
        'LEI': ('candidato não é canal. SEARCH_HIT != PERSON, e zero resultado é '
                'NOT_FOUND_IN_THIS_ROUTE, nunca NOT_ON_PLATFORM nem DOES_NOT_EXIST.'),
        'RUN_IDS': [m['RUN_ID'] for m in manifestos],
        'ITEMS': achados,
    }


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'contratos'
    raise SystemExit({'contratos': contratos, 'canais': canais}[cmd]())
