#!/usr/bin/env python3
"""
COLETA DO PILOTO DE SENSORES TÉCNICOS — canal e conteúdo das identidades provadas.

    python3 scripts/sensor_coleta.py contratos          # GRÁTIS: schema de entrada
    python3 scripts/sensor_coleta.py canais       A     # canal público das pessoas do lote
    python3 scripts/sensor_coleta.py videos       A     # vídeos dos recortes do lote
    python3 scripts/sensor_coleta.py transcricao  A     # transcrição dos vídeos achados
    python3 scripts/sensor_coleta.py comentarios  A     # comentários dos vídeos on-topic

A ORDEM É LEI, E ELA VEM DO ÁRBITRO
------------------------------------
    RECORTE -> IDENTIDADE -> CANAL PÚBLICO -> CONTEÚDO

Este arquivo cuida das duas últimas etapas. As duas primeiras estão fechadas em
`SPEAKER-UNIVERSE-PILOT-V1.json`: 6 recortes congelados, 12 identidades provadas.

DOIS RUNNERS, UM CONTRATO
--------------------------
Os lotes A e B rodam em máquinas diferentes e executam ESTE MESMO arquivo. A única coisa
que muda entre eles é o universo atribuído — nunca a régua. Mesmos campos, mesma
classificação, mesma dedupe, mesmos critérios congelados. Paralelismo compra tempo, não
permissividade.

A dedupe é GLOBAL por `PLATFORM + EXTERNAL_ID`. Se os dois lotes acharem o mesmo vídeo,
ele é UM objeto lógico com duas rotas de descoberta preservadas em `DISCOVERY_ROUTES` —
nunca dois registros. Rota de descoberta é proveniência; não multiplica evidência.

A rotação de chave é deslocada por lote (`OFFSET_DO_LOTE`) para os dois não baterem na
mesma posição do pool ao mesmo tempo. Sem isso, dois runners esgotariam a posição 1 juntos
e leriam o mesmo `SUCCEEDED` com zero itens como se fosse resposta da rota.

POR QUE `contratos` RODA ANTES DE TUDO
---------------------------------------
O piloto italiano queimou 8 execuções pagas mandando uma entrada que o ator ignorava — os
8 runs devolveram **o mesmo consultor de cibersegurança**, porque o Actor descartou em
silêncio o campo que não reconhecia.

    MATCH VAZIO NÃO AUTORIZA GASTO. CONTRATO ERRADO != PLATAFORMA ERRADA.

Ler o schema custa ZERO — é um GET no ator, não um run.

E onde o schema não pôde ser lido (os três atores de YouTube não publicam `inputSchema` no
build), a entrada NÃO foi adivinhada: ela é a mesma que já rodou com sucesso na Espanha e
está preservada no `RUN-MANIFEST`. Entrada provada vale mais que entrada inferida.

O QUE ESTE ARQUIVO NÃO FAZ
---------------------------
Não classifica sinal, não mede convergência, não declara nada. Ele BUSCA, preserva o RAW e
grava o normalizado. A classificação roda depois, de graça, sobre o artefato — assim um
erro de classificador não custa execução paga e pode ser refeito quantas vezes precisar.
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
RUNNER = os.environ.get('RUNNER_NAME') or 'NOT_KNOWN'

ATORES = {
    'LINKEDIN_SEARCH_BY_NAME': 'harvestapi~linkedin-profile-search-by-name',
    'LINKEDIN_PROFILE_SEARCH': 'harvestapi~linkedin-profile-search',
    'LINKEDIN_PROFILE': 'harvestapi~linkedin-profile-scraper',
    'LINKEDIN_POSTS': 'harvestapi~linkedin-post-search',
    'YOUTUBE_SEARCH': 'streamers~youtube-scraper',
    'YOUTUBE_TRANSCRIPT': 'pintostudio~youtube-transcript-scraper',
    'YOUTUBE_COMMENTS': 'streamers~youtube-comments-scraper',
}

# ── LOTES ────────────────────────────────────────────────────────────────────────
# Divisão determinística por RECORTE, não por pessoa: cada lote leva um recorte de cada
# país, e nenhum recorte fica em dois lotes. Assim um runner que falhar derruba dois
# recortes inteiros e não meia amostra de todos — o buraco fica legível.
LOTES = {
    'A': ['ES-OLIVE-REPILO', 'IT-DURUM_WHEAT-FUSARIUM', 'FR-VINE-DOWNY_MILDEW'],
    'B': ['ES-CEREAL-SEPTORIA', 'IT-VINE-FLAVESCENCE', 'FR-CEREAL-SEPTORIA'],
}
OFFSET_DO_LOTE = {'A': 0, 'B': 2}      # posição inicial no pool, para não colidirem

# ── TERMOS POR RECORTE ───────────────────────────────────────────────────────────
# NA LÍNGUA DO PAÍS, sempre. Buscar "septoria wheat" na França devolve literatura
# internacional, não a conversa técnica francesa. E o CROP e o ISSUE de cada item saem
# DESTA consulta, nunca de leitura livre do título — é o que torna a linha auditável.
TERMOS = {
    'ES-OLIVE-REPILO': ['repilo del olivo', 'Venturia oleaginea olivo',
                        'repilo olivar tratamiento', 'jornada tecnica olivar repilo'],
    'ES-CEREAL-SEPTORIA': ['septoria trigo', 'septoriosis del trigo',
                           'Zymoseptoria tritici trigo', 'jornada tecnica cereal septoria'],
    'IT-VINE-FLAVESCENCE': ['flavescenza dorata vite', 'flavescenza dorata vigneto',
                            'giallumi della vite', 'convegno flavescenza dorata'],
    'IT-DURUM_WHEAT-FUSARIUM': ['fusariosi grano duro', 'micotossine grano duro',
                                'fusariosi della spiga', 'convegno grano duro micotossine'],
    'FR-VINE-DOWNY_MILDEW': ['mildiou de la vigne', 'Plasmopara viticola vigne',
                             'mildiou vigne traitement', 'webinaire mildiou vigne'],
    'FR-CEREAL-SEPTORIA': ['septoriose du ble', 'Zymoseptoria tritici ble',
                           'septoriose ble traitement', 'webinaire septoriose ble'],
}

# Locais para a busca do LinkedIn por nome. País, nunca cidade adivinhada.
LOCAL = {'ES': ['Spain'], 'IT': ['Italy'], 'FR': ['France']}


# ── utilitários ──────────────────────────────────────────────────────────────────
def _curl_compat(url, *, token, timeout=60):
    """`coletor._curl` com só os argumentos que ESTA cópia dele aceita.

    POR QUE ISTO EXISTE — e custou duas execuções para fechar.
    A primeira versão passava `tentativas=2`, que existe no `coletor.py` de uma linha de
    história e NÃO existe no da branch default. Os sete atores voltaram
    `INDISPONIVEL TypeError` e aquilo parecia a Apify recusando tudo.

        FALHA DE ASSINATURA != FONTE INDISPONÍVEL.

    Na segunda execução o erro repetiu idêntico — porque eu tinha escrito o adaptador e
    deixado as chamadas usando `coletor._curl` direto. Função corrigida que o chamador não
    usa é o mesmo defeito de classe que a auditoria já pegou aqui: função testada que o
    pipeline nunca invoca.
    """
    import inspect
    aceita = inspect.signature(coletor._curl).parameters
    extra = {'tentativas': 2} if 'tentativas' in aceita else {}
    return coletor._curl(url, token=token, timeout=timeout, **extra)


def _pessoas(lote=None):
    with open(UNIVERSO, encoding='utf-8') as f:
        d = json.load(f)
    ps = [p for p in d['PEOPLE'] if p['IDENTITY_STATE'].startswith('IDENTITY_PROVED')]
    if lote:
        ps = [p for p in ps if p['CASE_ID'] in LOTES[lote]]
    return ps


def _gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return 'data/samples/SENSOR-PILOT/' + nome


def _ler(nome):
    caminho = os.path.join(SAIDA, nome)
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def _usd(man):
    v = man.get('COST_USD')
    return float(v) if isinstance(v, (int, float)) else 0.0


def _slug(s):
    return ''.join(c if c.isalnum() else '-' for c in (s or '')).strip('-')[:36]


def _proveniencia(man, actor, lote, batch_id):
    """Os campos que todo item carrega. Runner é proveniência técnica, não qualidade."""
    return {
        'COLLECTION_RUN_ID': man['RUN_ID'],
        'BATCH_ID': batch_id,
        'LOTE': lote,
        'RUNNER_NAME': RUNNER,
        'APIFY_ACTOR': actor,
        'CAPTURED_AT': coletor.agora(),
    }


def _rodar(actor, entrada, *, run_id, platform, country, query, evidence_path, lote):
    """Roda pelo coletor, trocando de chave só quando a CHAVE é o problema.

    Começa na posição deslocada do lote para os dois runners não baterem juntos na mesma.
    Cota esgotada de uma posição não é "sem resultado": é motivo de trocar e repetir a
    MESMA unidade — nunca de repetir na mesma chave, que só gastaria para receber o mesmo
    vazio.
    """
    chaves = ap.pool()
    if not chaves:
        return [], None, 0
    n = len(chaves)
    ordem = [(OFFSET_DO_LOTE.get(lote, 0) + i) % n for i in range(n)]
    ultimo = ([], None)
    for tentativa, idx in enumerate(ordem):
        pos = idx + 1
        itens, man = coletor.executar(
            actor, entrada, token=chaves[idx], run_id='%s-p%d' % (run_id, pos),
            platform=platform, country=country, mission=MISSION, query=query,
            source_version='captura de %s' % coletor.agora()[:10],
            evidence_path=evidence_path)
        man['TOKEN_POSITION_USED'] = pos
        man['RUNNER_NAME'] = RUNNER
        estado = ap.classificar(
            status=None if man['STATUS'] == 'FAILED' else 'SUCCEEDED',
            status_message=str(man.get('ERROR') or ''), itens=itens)
        ultimo = (itens, man)
        if itens:
            return itens, man, pos
        if estado in ap.ROTACIONAM:
            print('        posicao %d esgotada (%s) -> trocando' % (pos, estado))
            continue
        return itens, man, pos            # vazio legítimo: não gastar outra chave
    return ultimo[0], ultimo[1], 0


# ══════════════════════════════════════════════════════ FASE 0 · CONTRATOS (grátis)
def contratos(lote=None):
    chaves = ap.pool()
    if not chaves:
        print('POOL_EMPTY'); return 1
    token, fora = chaves[0], []
    for rotulo, actor in ATORES.items():
        try:
            d = _curl_compat('%s/acts/%s' % (coletor.API, actor), token=token)
        except Exception as e:                                # noqa: BLE001
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
        try:
            bid = ((a.get('taggedBuilds') or {}).get('latest') or {}).get('buildId')
            if bid:
                b = _curl_compat('%s/actor-builds/%s' % (coletor.API, bid), token=token)
                sch = ((b.get('data') or {}).get('inputSchema')) or ''
                if isinstance(sch, str) and sch.strip():
                    sch = json.loads(sch)
                if isinstance(sch, dict):
                    props = sch.get('properties') or {}
                    campos = sorted(props)
                    exemplo = {k: (props[k].get('prefill')
                                   if props[k].get('prefill') is not None
                                   else props[k].get('default')) for k in campos}
        except Exception as e:                                # noqa: BLE001
            campos = ['LEITURA_DO_SCHEMA_FALHOU: %s' % type(e).__name__]
        print('%-26s OK  %s/%s  campos=%d' % (rotulo, a.get('username'), a.get('name'),
                                              len(campos)))
        fora.append({'LABEL': rotulo, 'ACTOR': actor, 'STATE': 'AVAILABLE',
                     'OWNER': a.get('username'), 'NAME': a.get('name'),
                     'INPUT_FIELDS': campos, 'PREFILL': exemplo})
    print('\ngravado:', _gravar('CONTRATOS-DE-ENTRADA.json', {
        'SOURCE_ID': 'SENSOR-PILOT/CONTRATOS-DE-ENTRADA',
        'source': 'GET /v2/acts/{actor} e /v2/actor-builds/{id} — leitura, zero run',
        'SOURCE_LOCATION': 'Apify', 'FACT_LOCATION': 'n/a — descreve ferramenta',
        'ORIGINAL_LANGUAGE': 'en', 'CAPTURED_AT': coletor.agora(),
        'APIFY_RUNS': 0, 'ITEMS': 0, 'COST_USD': 0,
        'ONDE_O_SCHEMA_NAO_PODE_SER_LIDO': (
            'os três atores de YouTube não publicam inputSchema no build. A entrada NÃO '
            'foi adivinhada: é a mesma já provada na rodada espanhola, preservada no '
            'RUN-MANIFEST. Entrada provada vale mais que entrada inferida.'),
        'ACTORS': fora}))
    return 0


# ══════════════════════════════════════════════════════ FASE 1 · CANAIS
def canais(lote='A'):
    """Canal público das pessoas do lote: LinkedIn por nome + YouTube por nome."""
    pessoas = _pessoas(lote)
    batch = 'BATCH-%s-CANAIS' % lote
    print('lote %s · %d pessoas · recortes %s' % (lote, len(pessoas), LOTES[lote]))
    achados, mans, custo = [], [], 0.0

    for p in pessoas:
        nome, pais = p['NAME'], p['COUNTRY']
        partes = (nome or '').replace('‐', '-').split()
        first, last = (partes[0] if partes else ''), (partes[-1] if partes else '')
        print('  %s (%s · %s)' % (nome, pais, p['CASE_ID']))

        # --- LinkedIn por nome. Contrato REAL lido na fase `contratos`.
        entrada = {'firstName': first, 'lastName': last, 'locations': LOCAL[pais],
                   'maxItems': 10, 'maxPages': 1, 'profileScraperMode': 'Short',
                   'strictSearch': True}
        itens, man, pos = _rodar(
            ATORES['LINKEDIN_SEARCH_BY_NAME'], entrada,
            run_id='SENSOR-LI-%s-%s' % (lote, _slug(nome)), platform='LINKEDIN',
            country=pais, query='%s %s / %s' % (first, last, LOCAL[pais][0]),
            evidence_path='data/samples/SENSOR-PILOT/CANAIS-%s.json' % lote, lote=lote)
        if man:
            mans.append(man); custo += _usd(man)
            prov = _proveniencia(man, ATORES['LINKEDIN_SEARCH_BY_NAME'], lote, batch)
            for it in (itens or []):
                achados.append(_cand_linkedin(it, p, prov))
            print('      LinkedIn: %d perfis (pos %d, %s)'
                  % (len(itens or []), pos, man['STATUS']))

        # --- YouTube: onde a pessoa aparece. Pode ser canal dela OU de instituição.
        termo = '%s %s' % (nome, (p['INSTITUTION'] or '').split(',')[0])
        entrada = {'searchQueries': [termo], 'maxResults': 10, 'maxResultsShorts': 0,
                   'maxResultStreams': 0, 'videoType': 'video'}
        itens, man, pos = _rodar(
            ATORES['YOUTUBE_SEARCH'], entrada,
            run_id='SENSOR-YT-%s-%s' % (lote, _slug(nome)), platform='YOUTUBE',
            country=pais, query=termo,
            evidence_path='data/samples/SENSOR-PILOT/CANAIS-%s.json' % lote, lote=lote)
        if man:
            mans.append(man); custo += _usd(man)
            prov = _proveniencia(man, ATORES['YOUTUBE_SEARCH'], lote, batch)
            for v in (itens or []):
                achados.append(_cand_video(v, p, termo, prov, rota='PERSON_NAME_SEARCH'))
            print('      YouTube : %d itens (pos %d, %s)'
                  % (len(itens or []), pos, man['STATUS']))
        time.sleep(1)

    for m in mans:
        coletor.registrar(m)
    caminho = _gravar('CANAIS-%s.json' % lote, {
        'SOURCE_ID': 'SENSOR-PILOT/CANAIS-%s' % lote,
        'source': 'busca pública por nome via Apify (LinkedIn por nome + YouTube)',
        'SOURCE_LOCATION': 'LinkedIn e YouTube',
        'FACT_LOCATION': 'NOT_KNOWN — o lugar do fato sai do conteúdo, nunca da busca',
        'ORIGINAL_LANGUAGE': 'multi', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
        'CAPTURED_AT': coletor.agora(), 'MISSION': MISSION,
        'BATCH_ID': batch, 'LOTE': lote, 'RUNNER_NAME': RUNNER,
        'CASES': LOTES[lote],
        'PEOPLE_QUERIED': len(pessoas),
        'CANDIDATES': len(achados),
        'APIFY_RUNS': len(mans), 'COST_USD': round(custo, 6),
        'RUN_IDS': [m['RUN_ID'] for m in mans],
        'LEI': ('candidato não é canal. SEARCH_HIT != PERSON. Zero resultado é '
                'NOT_FOUND_IN_THIS_ROUTE, nunca NOT_ON_PLATFORM nem DOES_NOT_EXIST.'),
        'ITEMS': achados})
    print('\ngravado: %s · candidatos=%d · runs=%d · custo=%.4f USD'
          % (caminho, len(achados), len(mans), custo))
    return 0


def _cand_linkedin(it, p, prov):
    """Um perfil devolvido pela busca é CANDIDATO. O nome não decide a pessoa."""
    nome_perfil = it.get('name') or it.get('fullName') or pv.NAO_SEI
    headline = it.get('headline') or it.get('title') or pv.NAO_SEI
    pos_atual = it.get('currentPosition') or it.get('position') or {}
    empresa = (pos_atual.get('companyName') if isinstance(pos_atual, dict)
               else None) or it.get('companyName') or pv.NAO_SEI
    inst = (p['INSTITUTION'] or '').lower()
    bate_inst = bool(inst) and any(t in str(empresa).lower()
                                  for t in inst.split() if len(t) > 4)
    return dict(prov, **{
        'PERSON_ID': p['PERSON_ID'], 'NAME': p['NAME'], 'CASE_ID': p['CASE_ID'],
        'COUNTRY_OF_PERSON': p['COUNTRY'], 'INSTITUTION': p['INSTITUTION'],
        'SOURCE_PLATFORM': 'LINKEDIN',
        'SOURCE_URL': it.get('linkedinUrl') or it.get('url') or pv.NAO_SEI,
        'EXTERNAL_ID': it.get('id') or it.get('publicIdentifier') or pv.NAO_SEI,
        'PROFILE_NAME': nome_perfil, 'PROFILE_HEADLINE': headline,
        'PROFILE_COMPANY': empresa,
        'PROFILE_LOCATION': it.get('location') or it.get('locationName') or pv.NAO_SEI,
        'SOURCE_ENTITY': empresa,
        'CHANNEL_KIND': 'PERSON_OWN_CHANNEL_CANDIDATE',
        # A instituição bater é evidência FORTE; só o nome bater não é evidência nenhuma.
        'CHANNEL_IDENTITY_STATE': 'PLAUSIBLE' if bate_inst else 'NOT_PROVED',
        'CHANNEL_IDENTITY_EVIDENCE': (
            ('empresa declarada no perfil ("%s") casa com a instituição da ficha ("%s")'
             % (empresa, p['INSTITUTION'])) if bate_inst else
            ('só o nome casa. A busca por "Pasquale De Vita" devolveu o presidente da '
             'Unione Petrolifera, um vendedor de esquadrias e um diretor de TI, todos '
             'de nome idêntico. NAME_MATCH != PERSON.')),
        'DISCOVERY_ROUTES': ['LINKEDIN_NAME_SEARCH'],
    })


def _cand_video(v, p, termo, prov, rota):
    canal = v.get('channelName') or v.get('channelTitle') or pv.NAO_SEI
    sobren = ((p or {}).get('NAME') or '').split()[-1].lower() if p else ''
    parece_dela = bool(sobren) and sobren in str(canal).lower()
    vid = v.get('id') or v.get('videoId') or pv.NAO_SEI
    return dict(prov, **{
        'PERSON_ID': (p or {}).get('PERSON_ID', pv.NAO_SEI),
        'NAME': (p or {}).get('NAME', pv.NAO_SEI),
        'CASE_ID': (p or {}).get('CASE_ID', pv.NAO_SEI),
        'COUNTRY_OF_PERSON': (p or {}).get('COUNTRY', pv.NAO_SEI),
        'INSTITUTION': (p or {}).get('INSTITUTION', pv.NAO_SEI),
        'SOURCE_PLATFORM': 'YOUTUBE',
        'SOURCE_URL': v.get('url') or v.get('link') or pv.NAO_SEI,
        'EXTERNAL_ID': vid,
        'TITLE': v.get('title') or pv.NAO_SEI,
        'CHANNEL': canal,
        'CHANNEL_URL': v.get('channelUrl') or pv.NAO_SEI,
        'SOURCE_ENTITY': canal,
        'PUBLISHED_AT': v.get('date') or v.get('publishedAt') or pv.NAO_SEI,
        'DURATION': v.get('duration') or pv.NAO_SEI,
        'VIEWS': v.get('viewCount') if v.get('viewCount') is not None else pv.NAO_SEI,
        'COMMENTS_COUNT': (v.get('commentsCount')
                           if v.get('commentsCount') is not None else pv.NAO_SEI),
        'DESCRIPTION': (v.get('text') or v.get('description') or '')[:6000] or pv.NAO_SEI,
        'TRANSCRIPT': None,
        'TRANSCRIPT_AVAILABLE': 'NOT_TESTED',
        'CHANNEL_KIND': ('PERSON_OWN_CHANNEL_CANDIDATE' if parece_dela
                         else 'INSTITUTIONAL_CHANNEL_FEATURING_PERSON_CANDIDATE'),
        'CHANNEL_IDENTITY_STATE': 'NOT_PROVED',
        'CHANNEL_IDENTITY_EVIDENCE': 'veio da busca "%s". SEARCH_HIT != PERSON.' % termo,
        'SEARCH_TERM': termo,
        'DISCOVERY_ROUTES': [rota],
        # O lugar do fato NUNCA sai do idioma nem da nacionalidade da pessoa.
        'COUNTRY_OF_FACT': 'NOT_KNOWN',
        'REGION_OF_FACT': 'NOT_KNOWN',
    })


# ══════════════════════════════════════════════════════ FASE 2 · VÍDEOS DO RECORTE
def videos(lote='A'):
    """Vídeos dos recortes do lote, por termo técnico NA LÍNGUA DO PAÍS."""
    batch = 'BATCH-%s-VIDEOS' % lote
    achados, mans, custo = [], [], 0.0
    for caso in LOTES[lote]:
        pais = caso.split('-')[0]
        crop, issue = caso.split('-', 1)[1].rsplit('-', 1)
        termos = TERMOS[caso]
        print('  %s · %d termos' % (caso, len(termos)))
        entrada = {'searchQueries': termos, 'maxResults': 25, 'maxResultsShorts': 0,
                   'maxResultStreams': 0, 'videoType': 'video'}
        itens, man, pos = _rodar(
            ATORES['YOUTUBE_SEARCH'], entrada,
            run_id='SENSOR-VID-%s-%s' % (lote, caso), platform='YOUTUBE',
            country=pais, query=' | '.join(termos),
            evidence_path='data/samples/SENSOR-PILOT/VIDEOS-%s.json' % lote, lote=lote)
        if not man:
            continue
        mans.append(man); custo += _usd(man)
        prov = _proveniencia(man, ATORES['YOUTUBE_SEARCH'], lote, batch)
        for v in (itens or []):
            r = _cand_video(v, None, ' | '.join(termos), prov, rota='CASE_TERM_SEARCH')
            # CROP e ISSUE vêm da CONSULTA que trouxe o item, nunca do título.
            r.update({'CASE_ID': caso, 'CROP': crop, 'ISSUE': issue,
                      'COUNTRY_OF_PERSON': 'NOT_APPLICABLE',
                      'CROP_ISSUE_BASIS': 'declarado pela consulta, não lido do título'})
            achados.append(r)
        print('      %d vídeos (pos %d, %s)' % (len(itens or []), pos, man['STATUS']))
        time.sleep(1)

    for m in mans:
        coletor.registrar(m)
    caminho = _gravar('VIDEOS-%s.json' % lote, {
        'SOURCE_ID': 'SENSOR-PILOT/VIDEOS-%s' % lote,
        'source': 'busca YouTube por termo técnico na língua do país, via Apify',
        'SOURCE_LOCATION': 'YouTube',
        'FACT_LOCATION': 'NOT_KNOWN — sai do conteúdo, nunca da consulta',
        'ORIGINAL_LANGUAGE': 'multi', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
        'CAPTURED_AT': coletor.agora(), 'MISSION': MISSION,
        'BATCH_ID': batch, 'LOTE': lote, 'RUNNER_NAME': RUNNER, 'CASES': LOTES[lote],
        'TERMS_BY_CASE': {c: TERMOS[c] for c in LOTES[lote]},
        'ITEMS_COUNT': len(achados),
        'APIFY_RUNS': len(mans), 'COST_USD': round(custo, 6),
        'RUN_IDS': [m['RUN_ID'] for m in mans],
        'ITEMS': achados})
    print('\ngravado: %s · videos=%d · runs=%d · custo=%.4f USD'
          % (caminho, len(achados), len(mans), custo))
    return 0


# ══════════════════════════════════════════════════════ FASE 3 · TRANSCRIÇÃO
def transcricao(lote='A'):
    """Transcrição dos vídeos do lote. Sem transcrição, título não vira conteúdo."""
    fonte = _ler('VIDEOS-%s.json' % lote)
    if not fonte:
        print('SEM_VIDEOS_NAO_GASTEI — rode a fase `videos` antes'); return 1
    urls, alvo = [], []
    vistos = set()
    for v in fonte['ITEMS']:
        u = v.get('SOURCE_URL')
        if u and u != pv.NAO_SEI and u not in vistos:
            vistos.add(u); urls.append({'url': u}); alvo.append(v)
    print('  %d vídeos únicos para transcrever' % len(urls))
    achados, mans, custo = [], [], 0.0
    # Em lotes de 20: um pedido gigante que falha perde tudo; vinte perde vinte.
    for i in range(0, len(urls), 20):
        pedaco = urls[i:i + 20]
        itens, man, pos = _rodar(
            ATORES['YOUTUBE_TRANSCRIPT'], {'videoUrls': pedaco},
            run_id='SENSOR-TR-%s-%d' % (lote, i // 20), platform='YOUTUBE',
            country='MULTI', query='%d urls' % len(pedaco),
            evidence_path='data/samples/SENSOR-PILOT/TRANSCRICOES-%s.json' % lote,
            lote=lote)
        if not man:
            continue
        mans.append(man); custo += _usd(man)
        prov = _proveniencia(man, ATORES['YOUTUBE_TRANSCRIPT'], lote,
                             'BATCH-%s-TRANSCRICAO' % lote)
        for t in (itens or []):
            achados.append(dict(prov, **{
                'SOURCE_URL': t.get('url') or t.get('videoUrl') or pv.NAO_SEI,
                'EXTERNAL_ID': t.get('videoId') or pv.NAO_SEI,
                'TRANSCRIPT': _texto_transcricao(t),
                'TRANSCRIPT_LANGUAGE': t.get('language') or pv.NAO_SEI,
                'CAPTION_SOURCE': ATORES['YOUTUBE_TRANSCRIPT'],
            }))
        print('      lote %d: %d transcrições (pos %d, %s)'
              % (i // 20, len(itens or []), pos, man['STATUS']))
        time.sleep(1)
    for m in mans:
        coletor.registrar(m)
    com = sum(1 for a in achados if a['TRANSCRIPT'])
    caminho = _gravar('TRANSCRICOES-%s.json' % lote, {
        'SOURCE_ID': 'SENSOR-PILOT/TRANSCRICOES-%s' % lote,
        'source': 'legendas públicas via Apify', 'SOURCE_LOCATION': 'YouTube',
        'FACT_LOCATION': 'NOT_KNOWN', 'ORIGINAL_LANGUAGE': 'multi',
        'CAPTURED_AT': coletor.agora(), 'MISSION': MISSION, 'LOTE': lote,
        'RUNNER_NAME': RUNNER,
        'VIDEOS_REQUESTED': len(urls), 'TRANSCRIPTS_RETURNED': len(achados),
        'TRANSCRIPTS_WITH_TEXT': com,
        'LEI': ('pedida e vazia é REQUESTED_EMPTY, um estado — não ausência. '
                'Transcrição indisponível != vídeo sem conteúdo técnico.'),
        'APIFY_RUNS': len(mans), 'COST_USD': round(custo, 6),
        'RUN_IDS': [m['RUN_ID'] for m in mans], 'ITEMS': achados})
    print('\ngravado: %s · com texto=%d/%d · custo=%.4f USD'
          % (caminho, com, len(achados), custo))
    return 0


def _texto_transcricao(t):
    """O ator devolve formatos diferentes conforme o vídeo. Nenhum é inventado."""
    for chave in ('transcript', 'text', 'captions', 'data'):
        v = t.get(chave)
        if isinstance(v, str) and v.strip():
            return v
        if isinstance(v, list) and v:
            partes = [seg.get('text', '') if isinstance(seg, dict) else str(seg)
                      for seg in v]
            juntos = ' '.join(x for x in partes if x).strip()
            if juntos:
                return juntos
    return None


# ══════════════════════════════════════════════════════ FASE 4 · COMENTÁRIOS
def comentarios(lote='A'):
    """Comentários só de vídeos DOS RECORTES. Nunca conteúdo agrícola genérico."""
    fonte = _ler('VIDEOS-%s.json' % lote)
    if not fonte:
        print('SEM_VIDEOS_NAO_GASTEI — rode a fase `videos` antes'); return 1
    # Só vídeo com comentário declarado e do recorte. Pedir comentário de vídeo com zero
    # comentário é gastar para receber vazio.
    alvos = [v for v in fonte['ITEMS']
             if isinstance(v.get('COMMENTS_COUNT'), int) and v['COMMENTS_COUNT'] > 0]
    alvos.sort(key=lambda v: -(v.get('COMMENTS_COUNT') or 0))
    alvos = alvos[:40]
    print('  %d vídeos com comentário declarado (de %d)'
          % (len(alvos), len(fonte['ITEMS'])))
    if not alvos:
        print('  NADA A PEDIR — nenhum vídeo do lote declara comentário'); return 0
    achados, mans, custo = [], [], 0.0
    por_url = {v['SOURCE_URL']: v for v in alvos}
    for i in range(0, len(alvos), 20):
        pedaco = [v['SOURCE_URL'] for v in alvos[i:i + 20]]
        itens, man, pos = _rodar(
            ATORES['YOUTUBE_COMMENTS'],
            {'startUrls': pedaco, 'maxComments': 50, 'sortCommentsBy': 'TOP_COMMENTS'},
            run_id='SENSOR-CM-%s-%d' % (lote, i // 20), platform='YOUTUBE',
            country='MULTI', query='%d videos' % len(pedaco),
            evidence_path='data/samples/SENSOR-PILOT/COMENTARIOS-%s.json' % lote,
            lote=lote)
        if not man:
            continue
        mans.append(man); custo += _usd(man)
        prov = _proveniencia(man, ATORES['YOUTUBE_COMMENTS'], lote,
                             'BATCH-%s-COMENTARIOS' % lote)
        for c in (itens or []):
            u = c.get('videoUrl') or c.get('url') or ''
            v = por_url.get(u) or {}
            achados.append(dict(prov, **{
                'COMMENT_ID': c.get('cid') or c.get('commentId') or pv.NAO_SEI,
                'VIDEO_ID': v.get('EXTERNAL_ID') or c.get('videoId') or pv.NAO_SEI,
                'SOURCE_URL': u or v.get('SOURCE_URL') or pv.NAO_SEI,
                'SOURCE_PLATFORM': 'YOUTUBE',
                'SOURCE_ENTITY': v.get('CHANNEL') or pv.NAO_SEI,
                'CASE_ID': v.get('CASE_ID') or pv.NAO_SEI,
                'CROP': v.get('CROP') or pv.NAO_SEI,
                'ISSUE': v.get('ISSUE') or pv.NAO_SEI,
                # O texto ORIGINAL fica. Resumir e jogar fora a frase mata a evidência.
                'COMMENT_TEXT_RAW': c.get('comment') or c.get('text') or '',
                'COMMENTER_NAME': c.get('author') or c.get('authorName') or pv.NAO_SEI,
                'COMMENTER_PROFILE_URL': (c.get('authorChannelUrl')
                                          or c.get('authorUrl') or pv.NAO_SEI),
                'COMMENTER_ID': c.get('authorChannelId') or pv.NAO_SEI,
                # Handle não é pessoa. Todo autor entra sem papel resolvido.
                'COMMENTER_ENTITY_KIND': 'UNKNOWN',
                'COMMENTER_IDENTITY_STATE': 'UNVERIFIED',
                'LIKE_COUNT': c.get('voteCount') if c.get('voteCount') is not None
                              else pv.NAO_SEI,
                # A rota devolve tempo relativo ("hace 2 años"), não data. Converter um no
                # outro inventaria precisão que a fonte não deu.
                'DATE': pv.NAO_SEI,
                'DATE_RELATIVE': c.get('publishedTimeText') or c.get('date') or pv.NAO_SEI,
                'COUNTRY_OF_FACT': 'NOT_KNOWN',
                'REGION_OF_FACT': 'NOT_KNOWN',
                'SPEECH_TYPE': 'NOT_CLASSIFIED',
            }))
        print('      lote %d: %d comentários (pos %d, %s)'
              % (i // 20, len(itens or []), pos, man['STATUS']))
        time.sleep(1)
    for m in mans:
        coletor.registrar(m)
    caminho = _gravar('COMENTARIOS-%s.json' % lote, {
        'SOURCE_ID': 'SENSOR-PILOT/COMENTARIOS-%s' % lote,
        'source': 'comentários públicos de vídeos DOS RECORTES, via Apify',
        'SOURCE_LOCATION': 'YouTube', 'FACT_LOCATION': 'NOT_KNOWN',
        'ORIGINAL_LANGUAGE': 'multi', 'CAPTURED_AT': coletor.agora(),
        'MISSION': MISSION, 'LOTE': lote, 'RUNNER_NAME': RUNNER,
        'VIDEOS_ASKED': len(alvos), 'COMMENTS_COLLECTED': len(achados),
        'LEI': ('comentário é FIELD_VOICE_OBSERVED quando cabível, nunca '
                'FIELD_PROBLEM_CONFIRMED. Voz não é incidência.'),
        'APIFY_RUNS': len(mans), 'COST_USD': round(custo, 6),
        'RUN_IDS': [m['RUN_ID'] for m in mans], 'ITEMS': achados})
    print('\ngravado: %s · comentarios=%d · custo=%.4f USD'
          % (caminho, len(achados), custo))
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'contratos'
    lote = (sys.argv[2] if len(sys.argv) > 2 else 'A').upper()
    fn = {'contratos': contratos, 'canais': canais, 'videos': videos,
          'transcricao': transcricao, 'comentarios': comentarios}[cmd]
    raise SystemExit(fn(lote))
