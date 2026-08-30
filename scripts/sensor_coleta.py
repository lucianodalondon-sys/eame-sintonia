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
    # Reserva com 100% de sucesso em 333 mil execucoes nos ultimos 30 dias, contrato
    # proprio. Existe porque rota que falha por CONTRATO nao e rota morta.
    'YOUTUBE_TRANSCRIPT_ALT': 'starvibe~youtube-video-transcript',
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


# ── TRANSPORTE ENDURECIDO ────────────────────────────────────────────────────────
# MEDIDO, não suposto: na primeira rodada paralela, 7 de 12 buscas de YouTube voltaram
#
#     TypeError: the JSON object must be str, bytes or bytearray, not NoneType
#
# que é `json.loads(None)` — o `_curl` do `coletor` chama `subprocess.run(curl, ...)` e
# devolve `json.loads(r.stdout)` sem guardar contra `stdout` vazio ou nulo. Com dois
# runners na MESMA máquina disparando curl ao mesmo tempo, isso deixou de ser raro.
#
# O padrão de falha é o que denuncia: as mesmas consultas alternaram SUCCESS e FAILED
# entre os lotes, sem relação com o termo buscado. Falha de transporte, não de rota.
#
#     FALHA DE TRANSPORTE != ROTA MORTA. E o pior: registrada como FAILED, ela vira
#     "o YouTube não devolveu nada" no relatório — que é exatamente a leitura errada
#     que a lei SOURCE FAILURE != ZERO existe para impedir.
#
# A troca é de TRANSPORTE, não de porta: `coletor.executar()` continua sendo a única
# porta paga, continua gravando o RAW antes de normalizar e continua montando o
# manifesto. Só o modo de falar HTTP muda — urllib em vez de subprocesso, sem stdout
# para se perder, com retentativa em queda de rede e NUNCA em recusa da API.
# `coletor.py` não é alterado: um 4xx da Apify é resposta, e resposta não se repete.
def _curl_robusto(url, *, token, metodo='GET', corpo=None, timeout=300, **_):
    import urllib.error
    import urllib.request
    dados = json.dumps(corpo).encode('utf-8') if corpo is not None else None
    cab = {'Authorization': 'Bearer %s' % token}
    if dados is not None:
        cab['Content-Type'] = 'application/json'
    ultimo = ''
    for n in range(4):
        req = urllib.request.Request(url, data=dados, headers=cab, method=metodo)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                bruto = r.read().decode('utf-8', 'replace')
            if not bruto.strip():
                ultimo = 'corpo vazio'
            else:
                return json.loads(bruto)
        except urllib.error.HTTPError as e:
            corpo_erro = ''
            try:
                corpo_erro = e.read().decode('utf-8', 'replace')
            except Exception:                                 # noqa: BLE001
                pass
            if 400 <= e.code < 500:
                # Recusa da API é RESPOSTA, e não se repete. Mas ela precisa CHEGAR ao
                # manifesto: a versão de `executar` da branch default não inspeciona
                # `run['error']`, então devolver o JSON de erro fazia `data` vir vazio e o
                # manifesto registrar apenas `status da plataforma: None` — que se lê como
                # "o ator ficou mudo" quando a plataforma disse exatamente o que estava
                # errado. Levantar é o que faz a mensagem real entrar no campo ERROR.
                detalhe = ''
                try:
                    e_json = (json.loads(corpo_erro) or {}).get('error') or {}
                    detalhe = '%s — %s' % (e_json.get('type'), e_json.get('message'))
                except ValueError:
                    detalhe = corpo_erro[:200]
                raise RuntimeError('API recusou HTTP %d: %s'
                                   % (e.code, ap.redigir(detalhe)[:300]))
            ultimo = 'HTTP %d' % e.code
        except Exception as e:                                # noqa: BLE001
            ultimo = ap.redigir('%s: %s' % (type(e).__name__, e))[:160]
        if n < 3:
            time.sleep(2 ** n)
    raise RuntimeError('transporte falhou apos 4 tentativas: %s' % ultimo)


coletor._curl = _curl_robusto          # a porta continua a mesma; o transporte, não


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


def _hoje():
    import datetime
    return datetime.date.today()


def _dias(n):
    import datetime
    return datetime.timedelta(days=n)


def _registrar_lote(lote, mans):
    """Manifesto POR LOTE. O canônico não é tocado por execução paralela.

    MEDIDO na primeira rodada paralela: os dois runners chamaram `coletor.registrar()`,
    que reescreve `RUN-MANIFEST.json` inteiro. O lote B empurrou primeiro; o lote A caiu
    em `CONFLICT (content): Merge conflict in data/samples/RUN-MANIFEST.json`, o rebase
    parou no meio, e **29 candidatos já pagos ficaram na máquina sem chegar ao
    repositório**. Dinheiro gasto, dado não preservado.

        DOIS DONOS DO MESMO ARQUIVO É UM DONO A MAIS.

    Cada lote passa a escrever `RUNS-{lote}.json`, que só ele toca. A consolidação para o
    `RUN-MANIFEST` canônico acontece depois, num passo único e serializado — onde não há
    corrida possível. Nada se perde: os campos do manifesto são exatamente os mesmos.
    """
    if not mans:
        return
    caminho = os.path.join(SAIDA, 'RUNS-%s.json' % lote)
    antigos = []
    if os.path.exists(caminho):
        try:
            with open(caminho, encoding='utf-8') as f:
                antigos = json.load(f).get('RUNS') or []
        except ValueError:
            antigos = []
    por_id = {r['RUN_ID']: r for r in antigos}
    for m in mans:
        por_id[m['RUN_ID']] = m
    _gravar('RUNS-%s.json' % lote, {
        'SOURCE_ID': 'SENSOR-PILOT/RUNS-%s' % lote,
        'source': 'manifesto de execução do lote %s — fragmento, não o canônico' % lote,
        'SOURCE_LOCATION': 'interno — metadado de coleta',
        'FACT_LOCATION': 'n/a — descreve execução, não fato do mundo',
        'ORIGINAL_LANGUAGE': 'pt', 'CAPTURED_AT': coletor.agora(),
        'PARA_QUE_SERVE': ('fragmento por lote, para dois runners não disputarem o '
                           'RUN-MANIFEST canônico. A consolidação é um passo serializado.'),
        'NUNCA_GRAVAR_TOKEN': 'INPUT guarda consulta e parâmetros. Credencial, jamais.',
        'RUNS': [por_id[k] for k in sorted(por_id)]})


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

    _registrar_lote(lote, mans)
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

    _registrar_lote(lote, mans)
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
    # JANELA. O árbitro congelou 90 dias, extensível a 180 para quem publica pouco. Aqui
    # a extensão não é escolha de conveniência: 90 dias devolvem 6 vídeos em 440 e cobrem
    # só 3 dos 6 recortes; 180 devolvem 16 e cobrem os 6. Transcrever fora da janela seria
    # coletar histórico, que o contrato proíbe nesta etapa.
    #
    # E este número JÁ É UM ACHADO, antes de qualquer transcrição: 440 vídeos existem
    # nestes seis pares, e 16 deles são dos últimos seis meses. A conversa técnica em
    # vídeo nestes pares não é fluxo diário; é fio de água.
    janela = int(os.environ.get('SENSOR_JANELA_DIAS') or 180)
    corte = (_hoje() - _dias(janela)).isoformat()
    urls, alvo, fora_da_janela = [], [], 0
    vistos = set()
    for v in fonte['ITEMS']:
        u, p = v.get('SOURCE_URL'), str(v.get('PUBLISHED_AT') or '')[:10]
        if not u or u == pv.NAO_SEI or u in vistos:
            continue
        if not p or p < corte:
            fora_da_janela += 1
            continue
        vistos.add(u); urls.append({'url': u}); alvo.append(v)
    print('  janela de %d dias (desde %s): %d vídeos · %d fora da janela'
          % (janela, corte, len(urls), fora_da_janela))
    achados, mans, custo = [], [], 0.0
    # UM VÍDEO POR EXECUÇÃO, e o contrato veio da própria recusa da plataforma:
    #
    #     API recusou HTTP 400: invalid-input — Field input.videoUrl is required
    #
    # `videoUrls` (plural, uma lista) é o que rodou na Espanha e está no RUN-MANIFEST;
    # hoje o ator exige `videoUrl` no SINGULAR. O contrato do ator MUDOU entre as duas
    # rodadas, e o schema não pôde ser lido antes porque este ator não publica
    # `inputSchema` no build.
    #
    #     ENTRADA PROVADA ONTEM != ENTRADA VÁLIDA HOJE.
    #
    # A recusa da API acabou sendo a leitura de contrato que faltava — mas só porque ela
    # chegou inteira ao manifesto. Enquanto a mensagem se perdia, isto se lia como
    # "o YouTube não tem legenda", que é uma conclusão sobre a FONTE tirada de um defeito
    # do CHAMADOR.
    for i, u in enumerate(urls):
        rotulo, actor = 'YOUTUBE_TRANSCRIPT', ATORES['YOUTUBE_TRANSCRIPT']
        itens, man, pos = _rodar(
            actor, {'videoUrl': u['url']},
            run_id='SENSOR-TR-%s-%d' % (lote, i), platform='YOUTUBE',
            country='MULTI', query=u['url'],
            evidence_path='data/samples/SENSOR-PILOT/TRANSCRICOES-%s.json' % lote,
            lote=lote)
        # Ator reserva: se o primeiro recusar a ENTRADA (não a rede), tenta o segundo,
        # que tem contrato próprio. Rota que falha por contrato não é rota morta.
        if man and man['STATUS'] == 'FAILED' and 'invalid-input' in str(man.get('ERROR')):
            rotulo, actor = 'YOUTUBE_TRANSCRIPT_ALT', ATORES['YOUTUBE_TRANSCRIPT_ALT']
            itens, man, pos = _rodar(
                actor, {'videoUrl': u['url'], 'url': u['url'],
                        'videoUrls': [u['url']]},
                run_id='SENSOR-TRALT-%s-%d' % (lote, i), platform='YOUTUBE',
                country='MULTI', query=u['url'],
                evidence_path='data/samples/SENSOR-PILOT/TRANSCRICOES-%s.json' % lote,
                lote=lote)
        if not man:
            continue
        mans.append(man); custo += _usd(man)
        prov = _proveniencia(man, actor, lote, 'BATCH-%s-TRANSCRICAO' % lote)
        if not itens:
            # Pedida e vazia é um ESTADO, não uma ausência.
            achados.append(dict(prov, **{
                'SOURCE_URL': u['url'], 'EXTERNAL_ID': pv.NAO_SEI, 'TRANSCRIPT': None,
                'TRANSCRIPT_AVAILABLE': 'REQUESTED_EMPTY',
                'TRANSCRIPT_LANGUAGE': pv.NAO_SEI, 'CAPTION_SOURCE': actor,
                'WHY_EMPTY': str(man.get('ERROR'))[:200]}))
        for t in (itens or []):
            texto = _texto_transcricao(t)
            achados.append(dict(prov, **{
                'SOURCE_URL': t.get('url') or t.get('videoUrl') or u['url'],
                'EXTERNAL_ID': t.get('videoId') or pv.NAO_SEI,
                'TRANSCRIPT': texto,
                'TRANSCRIPT_AVAILABLE': 'YES' if texto else 'REQUESTED_EMPTY',
                'TRANSCRIPT_LANGUAGE': t.get('language') or pv.NAO_SEI,
                'CAPTION_SOURCE': actor,
            }))
        print('      %d/%d %s: %d itens (pos %d, %s)'
              % (i + 1, len(urls), rotulo, len(itens or []), pos, man['STATUS']))
        time.sleep(1)
    _registrar_lote(lote, mans)
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
    # POR QUE OS COMENTÁRIOS NÃO SEGUEM A JANELA DE 180 DIAS, e isso é decisão declarada:
    #
    # 1. a rota de comentários devolve TEMPO RELATIVO ("hace 2 años"), não data. Filtrar
    #    comentário por janela é impossível com o que a fonte dá, e converter relativo em
    #    absoluto inventaria precisão que ela não deu;
    # 2. dos 16 vídeos dentro da janela, apenas 2 declaram qualquer comentário. Um
    #    subexperimento sobre voz de campo rodado em 2 vídeos não responde nada.
    #
    # O filtro que FICA é o do assunto: os 440 vídeos vieram das consultas dos 6 recortes,
    # então todo alvo aqui está ligado a um par crop×issue declarado. É o que o contrato
    # exige — comentário só em conteúdo dos 6 recortes, nunca agrícola genérico.
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
        # `startUrls` é lista de OBJETOS, no formato RequestList da Apify — não lista de
        # texto. A recusa foi explícita: "Items in input.startUrls at positions
        # [0..19] do not contain valid URLs". O RUN-MANIFEST espanhol guardava a entrada
        # como a FRASE "48 vídeos on-topic", não a estrutura, então a forma real nunca
        # esteve preservada. Entrada descrita em prosa não é entrada reproduzível.
        itens, man, pos = _rodar(
            ATORES['YOUTUBE_COMMENTS'],
            {'startUrls': [{'url': u} for u in pedaco],
             'maxComments': 50, 'sortCommentsBy': 'TOP_COMMENTS'},
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
    _registrar_lote(lote, mans)
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
