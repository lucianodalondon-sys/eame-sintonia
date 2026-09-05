#!/usr/bin/env python3
"""
COLETA DE CREATORS — a rota que resolve perfil, mede atividade e procura marca.

    py scripts/creator_coleta.py contratos
    py scripts/creator_coleta.py resolver
    py scripts/creator_coleta.py atividade

ONDE ESTE ARQUIVO RODA, E POR QUE NÃO NO CONTÊINER
----------------------------------------------------
No runner residencial. O contêiner da sessão tem egresso restrito — medido
nesta missão: `plataformatierra.es`, `revistamercados.com`, `cibotoday.it`,
`reporterre.net` e `desmog.com` devolveram `EGRESS_BLOCKED`. É a mesma lição
que o catálogo ADAMA já tinha dado (403 da borda Akamai para o contêiner, 200
para o navegador local). A máquina residencial é a rota.

O QUE ELE FAZ E O QUE ELE RECUSA A FAZER
------------------------------------------
FAZ     resolve perfil público a partir de handle QUE UMA FONTE MOSTROU;
        mede seguidores, data do último conteúdo e frequência;
        procura menção de marca no conteúdo público.

RECUSA  inventar handle a partir de nome. Um candidato sem handle de fonte
        entra na fila `BUSCA_POR_NOME` e sai como CANDIDATO — nunca como
        perfil resolvido. `NAME_MATCH != PERSON` já custou a esta casa o
        presidente da Unione Petrolifera promovido a pesquisador de trigo duro.

A ARMADILHA DA COTA QUE SE APRESENTA COMO SUCESSO
---------------------------------------------------
`coletor.executar()` já trata: `SUCCEEDED` + zero itens + "free user run limit
reached" vira `PARTIAL`, e o pool rotaciona a chave. Nada aqui reimplementa
isso.

ATIVIDADE É MEDIDA, NÃO PRESUMIDA
-----------------------------------
`ACTIVITY_STATE` só sai de `NOT_MEASURED` quando existe data de conteúdo real.
Perfil que a rota não conseguiu ler continua `NOT_MEASURED` — nunca `DORMANT`.
Falha de leitura != ausência de atividade.
"""
import contextlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import apify_pool as ap                                      # noqa: E402
import coletor                                               # noqa: E402
import creators as cr                                        # noqa: E402


# ─────────────────────────────────────────────── por que urllib e não curl
# `coletor._curl` chama `curl` por subprocess. No runner Windows isso devolveu
# stdout VAZIO de forma intermitente, e `json.loads(None)` transformou a falha
# num `TypeError` que não diz nada sobre a causa:
#
#     21:53  contratos via _curl   OK
#     21:56  seed      via _curl   TypeError (stdout vazio)
#     22:00  diag      subprocess direto, com -w   OK, 3.463 bytes
#     22:02  contratos via _curl   TypeError, nos TRÊS atores
#
# O mesmo endpoint, com a mesma chave, minutos depois. Isso não é a plataforma
# recusando: é o subprocesso não entregando saída. Trocar por `urllib` remove a
# classe inteira do problema — sem processo filho, sem pipe, sem shell — e o
# resto da casa (`speaker_universo.py`) já prova que urllib funciona nessa
# máquina.
#
# A troca é feita por SUBSTITUIÇÃO de `coletor._curl`, e não por desvio do
# `coletor`: toda a proveniência (RAW antes de normalizar, RUN_MANIFEST,
# ACTOR_VERSION, COST_USD) continua passando pela porta única.
def _http(url, *, token, metodo='GET', corpo=None, timeout=300):
    import urllib.error
    import urllib.request
    dados = json.dumps(corpo).encode('utf-8') if corpo is not None else None
    req = urllib.request.Request(url, data=dados, method=metodo)
    req.add_header('Authorization', 'Bearer %s' % token)
    if dados is not None:
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            bruto = r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        corpo_erro = ''
        try:
            corpo_erro = e.read().decode('utf-8')[:300]
        except Exception:                                    # noqa: BLE001
            pass
        # A mensagem pode carregar a URL, e a URL pode carregar o token.
        raise RuntimeError(ap.redigir('HTTP %d: %s' % (e.code, corpo_erro)))
    if not bruto.strip():
        # Resposta vazia é ESTADO, não zero. Dizer isso é o que faltava.
        raise RuntimeError('resposta VAZIA da plataforma (HTTP 200 sem corpo)')
    return json.loads(bruto)


MISSION = '14-MAPA-DE-CREATORS-EAME'
SAIDA = cr.BASE

# ─────────────────────────────── ISOLAMENTO ENTRE MISSÕES (§3)
# EARLY SIGNAL e CREATOR MAP já rodaram ao mesmo tempo, e os dois escreviam no
# MESMO `data/samples/RUN-MANIFEST.json`. Dois runners gravando o mesmo JSON não
# é uma corrida improvável: é a corrida garantida, porque `pv.gravar()` lê tudo,
# junta e reescreve o arquivo inteiro — quem terminar por último apaga o outro.
#
# A correção não é lock: é NAMESPACE. Cada missão tem o seu manifesto, e o
# `RUN_ID` continua resolvendo dentro dele. Redirecionar `pv.MANIFESTO` (mesma
# técnica da substituição de `coletor._curl`) mantém a porta única do `coletor`
# intacta e tira o ponto de disputa.
import proveniencia as pv                                    # noqa: E402

MANIFESTO_DA_MISSAO = os.path.join(cr.BASE, 'RUN-MANIFEST-CREATORS.json')

# O isolamento tem de ser INTEIRO. Deixar o bruto no `data/samples/raw-paid/`
# partilhado enquanto o manifesto ia para o namespace da missao quebrou os testes
# da casa que exigem que TODO arquivo daquele diretorio resolva pelo manifesto
# GLOBAL — e quebrou com razao: um bruto sem manifesto que o alcance e um arquivo
# orfao. Ou o bruto e global com manifesto global, ou os dois sao da missao.
RAW_DIR_DA_MISSAO = os.path.join(cr.BASE, 'raw-paid')


# ─────────────────────────────── O ESCOPO, E POR QUE ELE EXISTE
# O redirecionamento acima era feito no CORPO DO MODULO. Isso queria dizer que
# IMPORTAR este ficheiro mudava, para o resto do processo, qual manifesto a casa
# inteira lia — e ninguem no outro lado do processo tinha como saber. Medido:
# `pv.carregar()` devolvia 22 execucoes antes de `import creator_coleta` e 7
# depois. Os testes da casa que corriam a seguir liam o manifesto DESTA missao a
# pensar que liam o global.
#
# O namespace por missao continua igual — o que muda e o ALCANCE. Fora do
# `with`, `pv.MANIFESTO` e `coletor` sao os da casa; dentro, sao os da missao; e
# o `finally` devolve-os mesmo que a fase rebente a meio. `tests/
# test_dataset_owner.py` ja provava o padrao em setUp/tearDown; aqui ele vive no
# proprio modulo, que e onde a troca acontece.
def _reconciliar_barrada(*_a, **_k):
    raise RuntimeError(
        'pv.reconciliar() dentro de escopo_da_missao() escreveria os fragmentos de '
        'TODOS os donos dentro do manifesto desta missao. Reconcilie fora do escopo.')


@contextlib.contextmanager
def escopo_da_missao():
    """Aponta coletor e proveniencia para o namespace desta missao, e devolve."""
    antes = (pv.MANIFESTO, coletor.RAW_DIR, coletor._curl, pv.reconciliar)
    pv.MANIFESTO = MANIFESTO_DA_MISSAO
    coletor.RAW_DIR = RAW_DIR_DA_MISSAO
    coletor._curl = _http
    # `pv.reconciliar()` deriva o indice a partir de TODOS os fragmentos da casa e
    # grava-o em `pv.MANIFESTO`. Com o manifesto redirecionado, isso despejaria os
    # donos todos dentro do namespace desta missao — em silencio, que e a pior
    # maneira. Nenhum sitio destes scripts chama `registrar(..., reconciliar=True)`
    # hoje, entao isto nao muda comportamento nenhum: transforma um defeito latente
    # num erro que se le. A reconciliacao continua permitida FORA do escopo, que e
    # onde ela faz sentido.
    pv.reconciliar = _reconciliar_barrada
    try:
        yield
    finally:
        pv.MANIFESTO, coletor.RAW_DIR, coletor._curl, pv.reconciliar = antes

# Atores. Os dois primeiros já foram provados nesta casa (piloto de sensores);
# os de Instagram/TikTok são novos e por isso a fase `contratos` existe: entrada
# errada é o erro mais caro já medido aqui (8 execuções, 8 vezes o mesmo
# consultor de cibersegurança, porque o Actor descartou em silêncio o campo que
# não reconhecia).
ATORES = {
    'YOUTUBE_SEARCH':    'streamers~youtube-scraper',
    'INSTAGRAM_PROFILE': 'apify~instagram-profile-scraper',
    'TIKTOK':            'clockworks~tiktok-scraper',
}


def _pool():
    chaves = ap.pool()
    if not chaves:
        print('POOL_EMPTY — APIFY_TOKEN_POOL ausente ou vazia'); raise SystemExit(1)
    return chaves


def _grava(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: data/samples/CREATOR-MAP-EAME/%s' % nome)


def contratos():
    """GRÁTIS. Lê o ator E O SCHEMA DE ENTRADA. Zero run, zero item, zero custo.

    A primeira versão desta fase lia só o ator e dizia AVAILABLE. Isso não é o
    contrato: `AVAILABLE` prova que o ator existe, não que a entrada que vamos
    mandar é a que ele aceita. A lição da casa é literal — o Actor descarta em
    silêncio o campo que não reconhece — e ela mora no INPUT SCHEMA, que vive
    no build, não no ator.
    """
    token = _pool()[0]
    fora = []
    for rotulo, actor in ATORES.items():
        try:
            d = coletor._curl('%s/acts/%s' % (coletor.API, actor), token=token, timeout=60)
            data = (d or {}).get('data') or {}
            campos, obrigatorios = cr.NAO_SEI, cr.NAO_SEI
            bid = ((data.get('taggedBuilds') or {}).get('latest') or {}).get('buildId')
            if bid:
                b = coletor._curl('%s/actor-builds/%s' % (coletor.API, bid),
                                  token=token, timeout=60)
                bd = (b or {}).get('data') or {}
                bruto = ((bd.get('inputSchema') if isinstance(bd.get('inputSchema'), dict)
                          else json.loads(bd.get('inputSchema') or '{}')) or {})
                props = bruto.get('properties') or {}
                campos = sorted(props)
                obrigatorios = bruto.get('required') or []
            fora.append({'LABEL': rotulo, 'ACTOR': actor, 'STATE': 'AVAILABLE',
                         'TITLE': data.get('title') or cr.NAO_SEI,
                         'USERNAME': data.get('username') or cr.NAO_SEI,
                         'INPUT_FIELDS': campos, 'REQUIRED': obrigatorios})
            print('  %-18s AVAILABLE  %s' % (rotulo, data.get('title')))
            print('      campos aceitos: %s' % (
                ', '.join(campos) if isinstance(campos, list) else campos))
            print('      obrigatorios  : %s' % obrigatorios)
        except Exception as e:                               # noqa: BLE001
            fora.append({'LABEL': rotulo, 'ACTOR': actor, 'STATE': 'NOT_REACHED',
                         'ERROR': ap.redigir('%s: %s' % (type(e).__name__, e))[:160]})
            print('  %-18s NOT_REACHED' % rotulo)
    _grava('APIFY-ACTOR-CONTRACTS.json', {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': coletor.agora(),
        'METHOD': 'GET /v2/acts/{actor} — leitura, zero run, zero custo',
        'ACTORS': fora})


def _candidatos():
    return cr.carregar('CREATORS-ES-IT-FR.json')


def resolver():
    """Resolve SÓ quem tem handle vindo de fonte. O resto vira fila de busca."""
    chaves = _pool()
    regs = _candidatos()
    resolvidos, fila = [], []

    for r in regs:
        ig, tt, yt = r.get('INSTAGRAM'), r.get('TIKTOK'), r.get('YOUTUBE')
        alvo = None
        if ig and ig != cr.NAO_SEI:
            alvo = ('INSTAGRAM', ATORES['INSTAGRAM_PROFILE'],
                    {'usernames': [ig.lstrip('@')]})
        elif tt and tt != cr.NAO_SEI:
            alvo = ('TIKTOK', ATORES['TIKTOK'],
                    {'profiles': [tt.lstrip('@')], 'resultsPerPage': 10})
        elif yt and yt != cr.NAO_SEI:
            alvo = ('YOUTUBE', ATORES['YOUTUBE_SEARCH'],
                    {'startUrls': [{'url': 'https://www.youtube.com/channel/%s' % yt}],
                     'maxResults': 10})
        if not alvo:
            # LEI 1 — sem handle de fonte, não se inventa endereço.
            fila.append({'CREATOR_ID': r['CREATOR_ID'], 'NAME': r['NAME'],
                         'COUNTRY': r['COUNTRY'],
                         'STATE': 'QUEUED_NAME_SEARCH',
                         'REASON': 'nenhum handle mostrado por fonte — handle não se infere de nome'})
            continue

        plataforma, actor, entrada = alvo
        run_id = '%s-%s-%s' % (MISSION, r['CREATOR_ID'], plataforma)
        itens, man = coletor.executar(
            actor, entrada, token=chaves[len(resolvidos) % len(chaves)],
            run_id=run_id, platform=plataforma, country=r['COUNTRY'], mission=MISSION,
            query=json.dumps(entrada, ensure_ascii=False),
            source_version=cr.NAO_SEI,
            evidence_path='data/samples/CREATOR-MAP-EAME/CREATOR-RESOLUTION.json')
        coletor.registrar(man, item_count_normalized=len(itens))
        resolvidos.append({'CREATOR_ID': r['CREATOR_ID'], 'NAME': r['NAME'],
                           'PLATFORM': plataforma, 'HANDLE_FROM_SOURCE': ig or tt or yt,
                           'RUN_ID': run_id, 'STATUS': man['STATUS'],
                           'ITEM_COUNT': len(itens),
                           'RAW': man['RAW_EVIDENCE_PATH'],
                           'ITEMS': itens[:3]})
        print('  %-12s %-10s %s itens=%d' % (r['CREATOR_ID'], plataforma,
                                             man['STATUS'], len(itens)))

    _grava('CREATOR-RESOLUTION.json', {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': coletor.agora(),
        'RESOLVED_ATTEMPTS': len(resolvidos), 'QUEUED_NAME_SEARCH': len(fila),
        'NOTE': 'Fila de busca por nome NÃO é perfil resolvido. NAME_MATCH != PERSON.',
        'RESOLUTIONS': resolvidos, 'QUEUE': fila})


# ─────────────────────────────────────────────────────── validação da seed
def _chave(txt):
    """Normaliza para COMPARAR nomes — nunca para gravar.

    O travessão U+2010 e o acento já quebraram uma comparação nesta casa
    (`Mercado‐Blanco` vs `Mercado-Blanco`). Aqui isso é tratado ANTES de
    qualquer igualdade, e o valor original nunca é sobrescrito.
    """
    import unicodedata
    t = unicodedata.normalize('NFKD', (txt or '').lower())
    t = ''.join(c for c in t if not unicodedata.combining(c))
    for travessao in ('\u2010', '\u2011', '\u2012', '\u2013', '\u2014'):
        t = t.replace(travessao, '-')
    return ' '.join(t.replace('.', ' ').replace('_', ' ').replace('-', ' ').split())


def _nome_bate(declarado, perfil):
    """PARCIAL é um estado. Um sobrenome em comum não é 'a mesma pessoa'."""
    a, b = set(_chave(declarado).split()), set(_chave(perfil).split())
    if not a or not b:
        return 'NOT_TESTED'
    if a == b:
        return 'EXACT'
    comuns = a & b
    if len(comuns) >= 2 or (len(comuns) == 1 and min(len(a), len(b)) == 1):
        return 'PARTIAL'
    return 'NO_MATCH'


def seed():
    """Resolve os handles da seed italiana numa execução só.

    Um run com N usernames custa muito menos que N runs, e o que interessa
    aqui é presença, identidade e atividade — não profundidade de conteúdo.
    """
    chaves = _pool()
    cands = cr.carregar('SEED-IT-CANDIDATES.json')
    handles = [ (r['ORIGIN_ID'] or '').lstrip('@') for r in cands ]
    handles = [h for h in handles if h]
    print('SEED_HANDLES=%d' % len(handles))

    run_id = '%s-SEED-IT-INSTAGRAM' % MISSION
    itens, man = coletor.executar(
        ATORES['INSTAGRAM_PROFILE'], {'usernames': handles},
        token=chaves[0], run_id=run_id, platform='INSTAGRAM', country='IT',
        mission=MISSION, query='seed italiana — %d handles' % len(handles),
        source_version=cr.NAO_SEI,
        evidence_path='data/samples/CREATOR-MAP-EAME/SEED-IT-RESOLVED.json')
    coletor.registrar(man, item_count_normalized=len(itens))
    print('STATUS=%s ITENS=%d CUSTO=%s' % (man['STATUS'], len(itens), man['COST_USD']))

    porhandle = {}
    for it in itens:
        u = (it.get('username') or '').lower()
        if u:
            porhandle[u] = it

    fora = []
    for r in cands:
        h = (r['ORIGIN_ID'] or '').lstrip('@').lower()
        it = porhandle.get(h)
        linha = {
            'CREATOR_ID': r['CREATOR_ID'], 'HANDLE': r['ORIGIN_ID'],
            'NAME_FROM_SEED': r['NAME'],
            'CROP_CLAIMED_BY_SEED': r['CROP_CLAIMED_BY_SEED'],
            'SUSPECTED_CHAIN_MISMATCH': r.get('SUSPECTED_CHAIN_MISMATCH'),
        }
        if not it:
            # Falha de leitura != perfil inexistente. O estado diz qual dos dois.
            linha.update({
                'HANDLE_EXISTS': 'NOT_RETURNED_BY_ROUTE',
                'NOTE': 'a rota nao devolveu este handle. NAO significa que o perfil '
                        'nao existe — SOURCE FAILURE != ZERO.',
                'PROFILE_URL': cr.NAO_SEI, 'NAME_MATCH': 'NOT_TESTED',
                'FOLLOWERS': cr.NAO_SEI, 'POSTS_COUNT': cr.NAO_SEI,
                'BIOGRAPHY': cr.NAO_SEI, 'LAST_ACTIVITY_DATE': cr.NAO_SEI,
            })
            fora.append(linha); continue

        posts = it.get('latestPosts') or []
        datas = sorted([p.get('timestamp') for p in posts if p.get('timestamp')], reverse=True)
        linha.update({
            'HANDLE_EXISTS': 'YES',
            'PROFILE_URL': it.get('url') or ('https://www.instagram.com/%s/' % h),
            'PROFILE_FULL_NAME': it.get('fullName') or cr.NAO_SEI,
            'NAME_MATCH': _nome_bate(r['NAME'], it.get('fullName') or ''),
            'FOLLOWERS': it.get('followersCount', cr.NAO_SEI),
            'FOLLOWS': it.get('followsCount', cr.NAO_SEI),
            'POSTS_COUNT': it.get('postsCount', cr.NAO_SEI),
            'VERIFIED': it.get('verified', cr.NAO_SEI),
            'PRIVATE': it.get('private', cr.NAO_SEI),
            'BIOGRAPHY': it.get('biography') or cr.NAO_SEI,
            'EXTERNAL_URL': it.get('externalUrl') or cr.NAO_SEI,
            'BUSINESS_CATEGORY': it.get('businessCategoryName') or cr.NAO_SEI,
            'LATEST_POSTS_SEEN': len(posts),
            'LAST_ACTIVITY_DATE': datas[0] if datas else cr.NAO_SEI,
            'AS_OF_DATE': coletor.agora()[:10],
        })
        fora.append(linha)

    achados = [x for x in fora if x['HANDLE_EXISTS'] == 'YES']
    _grava('SEED-IT-RESOLVED.json', {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': coletor.agora(),
        'RUN_ID': run_id, 'RUN_STATUS': man['STATUS'], 'COST_USD': man['COST_USD'],
        'RAW_EVIDENCE_PATH': man['RAW_EVIDENCE_PATH'],
        'SEED_HANDLES': len(handles), 'RESOLVED': len(achados),
        'NOT_RETURNED': len(fora) - len(achados),
        'LAW': 'handle resolvido != cultura provada. Este arquivo resolve IDENTIDADE '
               'e ATIVIDADE; cultura continua saindo de CONTEUDO.',
        'PROFILES': fora})
    print('RESOLVIDOS=%d de %d' % (len(achados), len(handles)))


def diag():
    """Mede a resposta CRUA da plataforma para uma execução mínima.

    Existe porque `TypeError: the JSON object must be ... not NoneType` no
    manifesto significa que `curl` devolveu stdout vazio — e "curl não falou"
    e "a plataforma recusou" produzem o mesmo FAILED com causas opostas.
    """
    import subprocess
    token = _pool()[0]
    actor = ATORES['INSTAGRAM_PROFILE']
    url = '%s/acts/%s/runs?waitForFinish=60' % (coletor.API, actor)
    corpo = {'usernames': ['davide_gomiero']}
    cmd = ['curl', '-sS', '-w', '\nHTTP_CODE=%{http_code}', '-X', 'POST',
           '-H', 'Authorization: Bearer %s' % token,
           '-H', 'Content-Type: application/json',
           '-d', json.dumps(corpo), url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    saida = ap.redigir(r.stdout or '')
    erro = ap.redigir(r.stderr or '')
    print('RETURNCODE=%s' % r.returncode)
    print('STDOUT_IS_NONE=%s  STDOUT_LEN=%s' % (r.stdout is None, len(r.stdout or '')))
    print('STDERR=%s' % erro[:300])
    print('STDOUT_HEAD=%s' % saida[:600])
    _grava('APIFY-DIAG.json', {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': coletor.agora(),
        'ACTOR': actor, 'INPUT': corpo,
        'RETURNCODE': r.returncode,
        'STDOUT_IS_NONE': r.stdout is None,
        'STDOUT_LEN': len(r.stdout or ''),
        'STDOUT_HEAD': saida[:2000], 'STDERR': erro[:600]})


def atividade():
    """Mede atividade recente dos perfis JÁ resolvidos (§9).

    Só entra aqui quem tem perfil resolvido: medir atividade de um handle que a
    rota não devolveu produziria `DORMANT` para alguém que talvez publique todo
    dia noutro endereço. `ACTIVITY_STATE` só sai de `NOT_MEASURED` com data real.
    """
    import datetime
    chaves = _pool()
    perfis = [p for p in cr.carregar('SEED-IT-RESOLVED.json')
              if p.get('HANDLE_EXISTS') == 'YES']
    # Os handles CORRIGIDOS pela resolução de identidade entram aqui também — e
    # entram primeiro. Medir atividade do handle errado da seed responderia com
    # precisão sobre a pessoa errada, que é pior que não responder.
    for r in cr.carregar('PRIMARY-IDENTITY-RESOLVED.json'):
        h = r.get('INSTAGRAM')
        if h and h != cr.NAO_SEI and not any(
                p['HANDLE'].lower() == h.lower() for p in perfis):
            perfis.insert(0, {'HANDLE': h, 'CREATOR_ID': r.get('CREATOR_ID'),
                              'HANDLE_EXISTS': 'YES',
                              'ORIGIN': 'PRIMARY_IDENTITY_RESOLVED'})
    handles = [p['HANDLE'].lstrip('@') for p in perfis]
    if not handles:
        print('NADA_A_MEDIR=YES · nenhum perfil resolvido'); return
    print('PERFIS_A_MEDIR=%d' % len(handles))

    run_id = '%s-ATIVIDADE-IT' % MISSION
    itens, man = coletor.executar(
        ATORES['INSTAGRAM_PROFILE'],
        {'usernames': handles, 'includeAboutSection': True},
        token=chaves[0], run_id=run_id, platform='INSTAGRAM', country='IT',
        mission=MISSION, query='atividade de %d perfis resolvidos' % len(handles),
        source_version=cr.NAO_SEI,
        evidence_path='data/samples/CREATOR-MAP-EAME/CREATOR-ACTIVITY.json')
    coletor.registrar(man, item_count_normalized=len(itens))
    print('STATUS=%s ITENS=%d CUSTO=%s' % (man['STATUS'], len(itens), man['COST_USD']))

    hoje = datetime.datetime.utcnow()
    fora = []
    porhandle = {(i.get('username') or '').lower(): i for i in itens}
    for p in perfis:
        h = p['HANDLE'].lstrip('@').lower()
        it = porhandle.get(h) or {}
        posts = it.get('latestPosts') or []
        datas = []
        for x in posts:
            t = x.get('timestamp')
            if not t:
                continue
            try:
                datas.append(datetime.datetime.strptime(t[:10], '%Y-%m-%d'))
            except ValueError:
                continue
        datas.sort(reverse=True)
        d30 = len([d for d in datas if (hoje - d).days <= 30])
        d90 = len([d for d in datas if (hoje - d).days <= 90])
        if not datas:
            estado, ultimo = 'NOT_MEASURED', cr.NAO_SEI
        else:
            ultimo = datas[0].strftime('%Y-%m-%d')
            dias = (hoje - datas[0]).days
            estado = ('ACTIVE_RECENT' if dias <= 30 else
                      'ACTIVE_STALE' if dias <= 180 else 'DORMANT')
        fora.append({
            'HANDLE': p['HANDLE'], 'CREATOR_ID': p.get('CREATOR_ID'),
            'ACTIVITY_STATE': estado, 'LAST_ACTIVITY_DATE': ultimo,
            'POSTS_LAST_30D': d30 if datas else cr.NAO_SEI,
            'POSTS_LAST_90D': d90 if datas else cr.NAO_SEI,
            'POSTS_SEEN': len(posts),
            'NOTE': ('sem data de post na amostra — NOT_MEASURED, nunca DORMANT'
                     if not datas else cr.NAO_SEI),
            'AS_OF_DATE': coletor.agora()[:10],
        })
    _grava('CREATOR-ACTIVITY.json', {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': coletor.agora(),
        'RUN_ID': run_id, 'RUN_STATUS': man['STATUS'], 'COST_USD': man['COST_USD'],
        'LAW': 'sem data de conteudo o estado e NOT_MEASURED — nunca DORMANT. '
               'Falha de leitura != ausencia de atividade.',
        'MEASURED': len(fora), 'PROFILES': fora})
    from collections import Counter
    print('ATIVIDADE:', dict(Counter(f['ACTIVITY_STATE'] for f in fora)))


# ─────────────────────────────────────────── §4 · extração por HUB
# Só entram contas de hub que uma FONTE mostrou. Adivinhar o Instagram de uma
# feira a partir do nome dela é o mesmo erro que adivinhar o de uma pessoa — e a
# missão já mediu o preço disso quatro vezes.
HUBS_COM_CONTA_CONFIRMADA = {
    '@agroinfluye': dict(hub='Premios AgroInfluye', pais='ES',
                         url='https://www.instagram.com/agroinfluye/',
                         fonte='nomeada em resultado de busca sobre o premio'),
    '@fieragricolavr': dict(hub='Fieragricola (Verona)', pais='IT',
                            url='https://www.instagram.com/fieragricolavr/',
                            fonte='conta oficial nomeada em busca, ~23 mil seguidores'),
    '@sivalangers': dict(hub='SIVAL (Angers)', pais='FR',
                         url='https://www.instagram.com/sivalangers/',
                         fonte='conta oficial nomeada em busca, 1.316 seguidores'),
    # Resolvida SEM adivinhacao: a conta oficial da Fieragricola mencionou
    # @enovitis_ nas proprias legendas. Uma porta abriu a outra.
    '@enovitis_': dict(hub='Enovitis in Campo', pais='IT',
                       url='https://www.instagram.com/enovitis_/',
                       fonte='mencionada pela conta oficial @fieragricolavr'),
    '@eima_international': dict(hub='EIMA International', pais='IT',
                                url='https://www.instagram.com/eima_international/',
                                fonte='URL de publicacao da conta oficial em busca'),
}

MENCAO = None


def _mencoes(texto):
    """Extrai @handles de uma legenda.

    Uma menção NÃO é um creator: é um CANDIDATO com uma rota de descoberta. A
    conta do prêmio menciona nomeados, patrocinadores, o local do evento e a
    própria organizadora — separar isso é trabalho da validação, não daqui.
    """
    global MENCAO
    if MENCAO is None:
        import re
        MENCAO = re.compile(r'@([A-Za-z0-9._]{2,30})')
    return ['@' + m.rstrip('.') for m in MENCAO.findall(texto or '')]


def hubs():
    """Raspa as contas de hub confirmadas e extrai as menções das legendas."""
    chaves = _pool()
    alvos = list(HUBS_COM_CONTA_CONFIRMADA)
    print('HUBS_COM_CONTA=%d' % len(alvos))

    run_id = '%s-HUBS' % MISSION
    itens, man = coletor.executar(
        ATORES['INSTAGRAM_PROFILE'],
        {'usernames': [h.lstrip('@') for h in alvos]},
        token=chaves[0], run_id=run_id, platform='INSTAGRAM', country='EU',
        mission=MISSION, query='hubs: %s' % ', '.join(alvos),
        source_version=cr.NAO_SEI,
        evidence_path='data/samples/CREATOR-MAP-EAME/HUB-EXTRACTION.json')
    coletor.registrar(man, item_count_normalized=len(itens))
    print('STATUS=%s ITENS=%d CUSTO=%s' % (man['STATUS'], len(itens), man['COST_USD']))

    fora = []
    for it in itens:
        u = '@' + (it.get('username') or '')
        meta = HUBS_COM_CONTA_CONFIRMADA.get(u.lower(), {})
        posts = it.get('latestPosts') or []
        achados = {}
        for post in posts:
            legenda = post.get('caption') or ''
            for m in _mencoes(legenda):
                if m.lower() == u.lower():
                    continue                       # a conta mencionando a si mesma
                achados.setdefault(m.lower(), {'HANDLE': m, 'MENTIONS': 0, 'POSTS': []})
                achados[m.lower()]['MENTIONS'] += 1
                if len(achados[m.lower()]['POSTS']) < 2:
                    achados[m.lower()]['POSTS'].append(post.get('url') or cr.NAO_SEI)
        fora.append({
            'HUB': meta.get('hub', cr.NAO_SEI), 'HUB_HANDLE': u,
            'COUNTRY': meta.get('pais', cr.NAO_SEI),
            'HUB_FOLLOWERS': it.get('followersCount', cr.NAO_SEI),
            'POSTS_READ': len(posts),
            'PEOPLE_DISCOVERED': len(achados),
            'NOTE': 'menção != creator. Cada handle aqui e CANDIDATO com uma rota de '
                    'descoberta, e ainda pode ser patrocinador, local ou organizadora.',
            'MENTIONS': sorted(achados.values(), key=lambda x: -x['MENTIONS']),
        })
        print('  %-22s posts=%-3d mencoes_unicas=%d' % (u, len(posts), len(achados)))

    _grava('HUB-EXTRACTION.json', {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': coletor.agora(),
        'RUN_ID': run_id, 'RUN_STATUS': man['STATUS'], 'COST_USD': man['COST_USD'],
        'LAW': 'So entram contas de hub que uma FONTE mostrou. Adivinhar o Instagram '
               'de uma feira pelo nome dela e o mesmo erro que adivinhar o de uma '
               'pessoa.',
        'HUBS': fora})


# Contas que aparecem em legenda de hub e NÃO são pessoas do setor. Lista
# explícita e curta: patrocinador financeiro, local do evento, organizadora. Não
# é um filtro esperto — é um registro do que já foi visto e conferido.
NAO_E_CREATOR = {'@santander_es', '@agroinfluye', '@agromillora'}


def descobertos():
    """Resolve os handles que a extração por hub revelou.

    Cada um entra como CANDIDATO com rota de descoberta. Resolver identidade aqui
    é o mesmo portão de sempre: o handle veio de uma legenda, não de uma ficha.
    """
    chaves = _pool()
    achados, origem = [], {}
    for h in cr.carregar('HUB-EXTRACTION.json'):
        for m in h.get('MENTIONS') or []:
            handle = m['HANDLE']
            if handle.lower() in NAO_E_CREATOR:
                continue
            if handle.lower() in origem:
                origem[handle.lower()]['HUBS'].append(h['HUB'])
                continue
            origem[handle.lower()] = {'HANDLE': handle, 'HUBS': [h['HUB']],
                                      'COUNTRY': h.get('COUNTRY', cr.NAO_SEI),
                                      'MENTIONS': m['MENTIONS'],
                                      'EVIDENCE_POSTS': m.get('POSTS') or []}
            achados.append(origem[handle.lower()])
    if not achados:
        print('NADA_A_RESOLVER=YES'); return
    print('HANDLES_DESCOBERTOS=%d' % len(achados))

    run_id = '%s-DESCOBERTOS' % MISSION
    itens, man = coletor.executar(
        ATORES['INSTAGRAM_PROFILE'],
        {'usernames': [a['HANDLE'].lstrip('@') for a in achados]},
        token=chaves[0], run_id=run_id, platform='INSTAGRAM', country='ES',
        mission=MISSION, query='%d handles descobertos por hub' % len(achados),
        source_version=cr.NAO_SEI,
        evidence_path='data/samples/CREATOR-MAP-EAME/HUB-DISCOVERED-RESOLVED.json')
    coletor.registrar(man, item_count_normalized=len(itens))
    print('STATUS=%s ITENS=%d CUSTO=%s' % (man['STATUS'], len(itens), man['COST_USD']))

    import datetime
    hoje = datetime.datetime.utcnow()
    porh = {(i.get('username') or '').lower(): i for i in itens}
    fora = []
    for a in achados:
        it = porh.get(a['HANDLE'].lstrip('@').lower()) or {}
        posts = it.get('latestPosts') or []
        datas = []
        for x in posts:
            t = x.get('timestamp')
            if t:
                try:
                    datas.append(datetime.datetime.strptime(t[:10], '%Y-%m-%d'))
                except ValueError:
                    pass
        datas.sort(reverse=True)
        foll = it.get('followersCount')
        if foll is None and not posts:
            estado_handle, estado_ativ, ultimo = 'HANDLE_UNRESOLVED', 'NOT_MEASURED', cr.NAO_SEI
        else:
            estado_handle = 'YES'
            if datas:
                dias = (hoje - datas[0]).days
                estado_ativ = ('ACTIVE_RECENT' if dias <= 30 else
                               'ACTIVE_STALE' if dias <= 180 else 'DORMANT')
                ultimo = datas[0].strftime('%Y-%m-%d')
            else:
                estado_ativ, ultimo = 'NOT_MEASURED', cr.NAO_SEI
        fora.append({
            'HANDLE': a['HANDLE'], 'DISCOVERED_VIA': a['HUBS'],
            'HUB_MENTIONS': a['MENTIONS'], 'EVIDENCE_POSTS': a['EVIDENCE_POSTS'],
            'COUNTRY_OF_HUB': a['COUNTRY'],
            'HANDLE_EXISTS': estado_handle,
            'PROFILE_URL': it.get('url') or cr.NAO_SEI,
            'FULL_NAME': it.get('fullName') or cr.NAO_SEI,
            'BIOGRAPHY': it.get('biography') or cr.NAO_SEI,
            'FOLLOWERS': foll if foll is not None else cr.NAO_SEI,
            'POSTS_COUNT': it.get('postsCount', cr.NAO_SEI),
            'BUSINESS_CATEGORY': it.get('businessCategoryName') or cr.NAO_SEI,
            'EXTERNAL_URL': it.get('externalUrl') or cr.NAO_SEI,
            'ACTIVITY_STATE': estado_ativ, 'LAST_ACTIVITY_DATE': ultimo,
            'POSTS_LAST_30D': len([d for d in datas if (hoje - d).days <= 30]) if datas else cr.NAO_SEI,
            'POSTS_LAST_90D': len([d for d in datas if (hoje - d).days <= 90]) if datas else cr.NAO_SEI,
            'IDENTITY_STATE': 'NOT_PROVED',
            'NOTE': 'descoberto por menção em legenda de hub. Menção != creator: '
                    'CROP, ROLE e ACTUAL_FARMER seguem por provar.',
            'AS_OF_DATE': coletor.agora()[:10],
        })
    resolvidos = [f for f in fora if f['HANDLE_EXISTS'] == 'YES']
    _grava('HUB-DISCOVERED-RESOLVED.json', {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': coletor.agora(),
        'RUN_ID': run_id, 'RUN_STATUS': man['STATUS'], 'COST_USD': man['COST_USD'],
        'DISCOVERED': len(fora), 'RESOLVED': len(resolvidos),
        'NOT_RESOLVED': len(fora) - len(resolvidos),
        'EXCLUDED_NOT_CREATOR': sorted(NAO_E_CREATOR),
        'LAW': 'menção em legenda de hub e ROTA DE DESCOBERTA, nunca prova de papel.',
        'PROFILES': fora})
    from collections import Counter
    print('RESOLVIDOS=%d de %d' % (len(resolvidos), len(fora)))
    print('ATIVIDADE:', dict(Counter(f['ACTIVITY_STATE'] for f in fora)))


# ─────────────────────────────────────── §1-§2 · PROVA DE CULTURA POR CONTEÚDO
# Termos por cultura, em ES/IT/FR/EN. Deliberadamente ESPECÍFICOS: a lição do
# `speaker_universo` vale aqui igual — consulta frouxa não traz mais do mesmo,
# traz OUTRA população. "verde" ou "campo" não entram; "olivar" e "vendimia" sim.
# Termos por cultura. A PRIMEIRA versão desta lista fez casamento por SUBSTRING e
# produziu falsos positivos graves, medidos ao ler o resultado:
#
#     'riz'  (arroz em francês)  casava dentro de nariz, matriz, Beatriz, horizonte
#     'mais' (milho em italiano) casava com o "mais" português de @ironfarmer_rc,
#            que é de Évora e escreve em português — e o perfil saiu "MAIZE PROVED"
#     'serra' (estufa em italiano) casava com serra de montanha
#     'papa'  (batata) casava com papa/papá
#     'riso'  (arroz em italiano) casava com riso/sorriso
#
# É exatamente o erro que o `speaker_universo` documenta e que este arquivo cita:
# consulta frouxa não traz mais do mesmo, traz OUTRA população com cara de
# sucesso. Agora o casamento é por PALAVRA INTEIRA, e os termos curtos ambíguos
# foram REMOVIDOS em vez de "melhorados" — um termo que precisa de contexto para
# não errar não é um termo, é um palpite.
TERMOS_DE_CULTURA = {
    'OLIVE':        ['olivar', 'olivo', 'olivos', 'aceituna', 'aceitunas', 'almazara',
                     'oliveto', 'olivicoltura', 'olivier', 'oliveraie', 'olive grove'],
    'GRAPEVINE':    ['vinedo', 'vinedos', 'vina', 'vendimia', 'viticultura', 'vigneto',
                     'vendemmia', 'vignoble', 'viticoltura', 'vineyard'],
    'CEREALS':      ['trigo', 'cebada', 'cereal', 'cereales', 'siega', 'cosechadora',
                     'grano duro', 'frumento', 'orzo', 'ble', 'orge', 'moisson',
                     'wheat', 'barley'],
    'MAIZE':        ['maiz', 'mais_it_REMOVIDO', 'maize', 'ensilado', 'insilato',
                     'ensilage', 'semis de mais'],
    'RICE':         ['arroz', 'risaia', 'risaie', 'arrozal'],
    'PROTECTED_HORTICULTURE': ['invernadero', 'invernaderos', 'greenhouse',
                               'horticola', 'horticolas'],
    'TOMATO':       ['tomate', 'tomates', 'pomodoro', 'pomodori'],
    'PEPPER':       ['pimiento', 'pimientos', 'peperone', 'poivron'],
    'PISTACHIO':    ['pistacho', 'pistachos', 'pistacchio', 'pistache'],
    'ALMOND':       ['almendro', 'almendros', 'almendra', 'mandorlo', 'amandier'],
    'CITRUS':       ['citricos', 'naranjo', 'naranjos', 'agrumi', 'agrumes'],
    'POTATO':       ['patata', 'patatas', 'pomme de terre'],
    'SUNFLOWER':    ['girasol', 'girasoles', 'girasole', 'tournesol'],
}
TERMOS_DE_CULTURA['MAIZE'] = [t for t in TERMOS_DE_CULTURA['MAIZE']
                              if not t.endswith('_REMOVIDO')]

# Quantos conteúdos distintos mencionando a cultura fazem "recorrente" (classe C).
# Escolhido ANTES de ver o resultado, e registrado aqui por isso.
MINIMO_PARA_RECORRENTE = 2

# Quem FALA de uma cultura não necessariamente a PRODUZ. Para audiências de
# consumidor, mencionar tomate dez vezes prova assunto, não lavoura — um creator
# de comida publica receitas. Nestes casos o achado sai como TOPIC, nunca como
# CROP_FIT.
FACING_QUE_NAO_PROVA_PRODUCAO = ('FOOD_CONSUMER', 'GENERAL_CONSUMER', 'WINE_CONSUMER')

_RX_TERMOS = None


def _normaliza(txt):
    import unicodedata
    t = unicodedata.normalize('NFKD', (txt or '').lower())
    return ''.join(c for c in t if not unicodedata.combining(c))


def _cultura_no_texto(texto):
    """Devolve {cultura: [trechos]} — casamento por PALAVRA INTEIRA."""
    global _RX_TERMOS
    import re
    if _RX_TERMOS is None:
        _RX_TERMOS = {c: re.compile(r'\b(?:%s)\b' % '|'.join(
            re.escape(_normaliza(t)) for t in termos))
            for c, termos in TERMOS_DE_CULTURA.items()}
    plano = _normaliza(texto)
    fora = {}
    for cultura, rx in _RX_TERMOS.items():
        m = rx.search(plano)
        if m:
            i = m.start()
            fora[cultura] = [(texto[max(0, i - 60):i + 80] or '').replace('\n', ' ').strip()]
    return fora


def conteudo():
    """Testa CROP_PROOF por CONTEÚDO nos candidatos que travam por cultura.

    A bio já foi lida numa rodada anterior; aqui o que decide é o que a pessoa
    PUBLICA. Uma bio pode declarar a cultura e o conteúdo desmenti-la — e o
    estado `CONTRADICTED` existe exatamente para esse caso.
    """
    chaves = _pool()
    fichas = cr.carregar('WHO-COULD-MARKETING-CALL.json')
    alvos = []
    for f in fichas:
        if f.get('ACTIVATION_STATE') != 'PROMISING':
            continue
        if not any('MISSING_CROP_PROOF' in str(p) for p in (f.get('WHY_RELEVANT') or [])):
            continue
        h = f.get('HANDLE')
        if h and h != cr.NAO_SEI and h.startswith('@'):
            alvos.append(f)
    if not alvos:
        print('NADA_A_TESTAR=YES'); return
    print('CANDIDATOS_COM_MISSING_CROP_PROOF=%d' % len(alvos))

    run_id = '%s-CROP-PROOF' % MISSION
    itens, man = coletor.executar(
        ATORES['INSTAGRAM_PROFILE'],
        {'usernames': [a['HANDLE'].lstrip('@') for a in alvos]},
        token=chaves[0], run_id=run_id, platform='INSTAGRAM', country='ES',
        mission=MISSION, query='prova de cultura por conteudo, %d perfis' % len(alvos),
        source_version=cr.NAO_SEI,
        evidence_path='data/samples/CREATOR-MAP-EAME/CROP-PROOF.json')
    coletor.registrar(man, item_count_normalized=len(itens))
    print('STATUS=%s ITENS=%d CUSTO=%s' % (man['STATUS'], len(itens), man['COST_USD']))

    porh = {(i.get('username') or '').lower(): i for i in itens}
    fora = []
    for a in alvos:
        h = a['HANDLE'].lstrip('@').lower()
        it = porh.get(h) or {}
        posts = it.get('latestPosts') or []
        achados, provas = {}, []
        for post in posts:
            legenda = post.get('caption') or ''
            for cultura, trechos in _cultura_no_texto(legenda).items():
                achados[cultura] = achados.get(cultura, 0) + 1
                if len(provas) < 12:
                    provas.append({'CROP': cultura,
                                   'CROP_PROOF_URL': post.get('url') or cr.NAO_SEI,
                                   'CROP_PROOF_DATE': (post.get('timestamp') or cr.NAO_SEI)[:10],
                                   'CROP_PROOF_TEXT': trechos[0][:200]})
        recorrentes = sorted([c for c, n in achados.items()
                              if n >= MINIMO_PARA_RECORRENTE])
        pontuais = sorted([c for c, n in achados.items()
                           if n < MINIMO_PARA_RECORRENTE])

        facing = a.get('FACING') or ''
        consumidor = (facing in FACING_QUE_NAO_PROVA_PRODUCAO
                      or a.get('CREATOR_TYPE') in ('FOOD_CREATOR', 'WINE_MEDIA_CREATOR'))
        if not posts:
            estado, tipo, forca = 'NOT_KNOWN', cr.NAO_SEI, cr.NAO_SEI
            motivo = 'a rota nao devolveu conteudo — NAO e ausencia de cultura'
        elif recorrentes and consumidor:
            # Assunto observado, producao NAO provada. Os dois num campo so
            # transformariam um creator de receitas em produtor de tomate.
            estado, tipo, forca = 'NOT_PROVED', cr.NAO_SEI, cr.NAO_SEI
            motivo = ('CROP_TOPIC_OBSERVED (%s) mas o perfil e de audiencia de '
                      'consumidor: mencionar a cultura prova ASSUNTO, nao lavoura'
                      % ','.join(recorrentes))
        elif recorrentes:
            estado = 'PROVED'
            tipo, forca = 'C_RECURRING_FIELD_CONTENT', 'STRONG'
            motivo = ('%d publicacoes distintas mencionam a cultura (minimo %d, '
                      'definido antes da medicao)' % (max(achados.values()),
                                                      MINIMO_PARA_RECORRENTE))
        elif pontuais:
            estado, tipo, forca = 'PARTIAL', 'C_RECURRING_FIELD_CONTENT', 'WEAK'
            motivo = ('mencao unica — falar uma vez da cultura NAO prova cultura')
        else:
            estado, tipo, forca = 'NOT_PROVED', cr.NAO_SEI, cr.NAO_SEI
            motivo = ('nenhuma das %d publicacoes lidas menciona cultura reconhecida'
                      % len(posts))

        fora.append({
            'HANDLE': a['HANDLE'], 'CREATOR_ID': a.get('CREATOR_ID'),
            'COUNTRY': a.get('COUNTRY'), 'CREATOR_TYPE': a.get('CREATOR_TYPE'),
            'N_CONTENT_ITEMS_REVIEWED': len(posts),
            'CONTENT_TYPES_OBSERVED': sorted({p.get('type') or 'UNKNOWN'
                                              for p in posts}) or cr.NAO_SEI,
            'FACING': facing or cr.NAO_SEI,
            'CROPS_RECURRING': recorrentes,
            'CROP_TOPIC_ONLY': recorrentes if consumidor else [],
            'CROPS_MENTIONED_ONCE': pontuais,
            'CROP_PROOF_RESULT': estado,
            'CROP_PROOF_TYPE': tipo, 'CROP_PROOF_STRENGTH': forca,
            'REASON': motivo,
            'EVIDENCE': provas,
            'AS_OF_DATE': coletor.agora()[:10],
        })
        print('  %-28s posts=%-3d %-11s %s' % (a['HANDLE'], len(posts), estado,
                                               ','.join(recorrentes) or '-'))

    from collections import Counter
    _grava('CROP-PROOF.json', {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': coletor.agora(),
        'RUN_ID': run_id, 'RUN_STATUS': man['STATUS'], 'COST_USD': man['COST_USD'],
        'MINIMO_PARA_RECORRENTE': MINIMO_PARA_RECORRENTE,
        'MINIMO_DEFINIDO': 'antes da medicao, e registrado no codigo',
        'LAW': 'hashtag, evento, repost, mencao unica e categoria de premio NAO provam '
               'cultura. So as quatro classes A-D promovem.',
        'TESTED': len(fora),
        'RESULT': dict(Counter(f['CROP_PROOF_RESULT'] for f in fora)),
        'PROFILES': fora})
    print('RESULTADO:', dict(Counter(f['CROP_PROOF_RESULT'] for f in fora)))


# ─────────────────────────────────────── §5 · atividade dos canais franceses
# URLs CONFIRMADAS por fonte. A primeira versao desta missao inferiu
# "youtube.com/@DavidForge" a partir do nome — e a fonte mostrou que o canal
# chama-se "La Chaine Agricole". Inferir endereco de canal e o mesmo erro que
# inferir handle de pessoa.
CANAIS_FR = [
    # §2 · RESOLVIDO POR FONTE, nao inferido. A primeira versao desta missao
    # escreveu "youtube.com/@DavidForge" a partir do nome da pessoa; o canal
    # chama-se "Chaine Agricole". NOME DA PESSOA != NOME DO CANAL.
    dict(creator_id='FR-CR-005', nome='David Forge',
         url='https://www.youtube.com/channel/UC3l2JpG0vN8xMkvvfCwavcQ',
         handle='@chaineagricole',
         fonte='canal oficial "Chaine Agricole" nomeado em resultado de busca, com '
               'channel id; canal secundario "David Forge, les Bonus" tambem existe'),
    dict(creator_id='FR-CR-006', nome='Gilles Van Kempen',
         url='https://www.youtube.com/channel/UCo4pMCeqy3BIuVo82bJxWbg',
         handle='@gillesvk',
         fonte='canal oficial nomeado em resultado de busca'),
]


def franca():
    """Mede atividade recente dos canais franceses de URL confirmada."""
    chaves = _pool()
    if not CANAIS_FR:
        print('NENHUM_CANAL_CONFIRMADO=YES'); return
    print('CANAIS_FR=%d' % len(CANAIS_FR))
    fora = []
    for i, c in enumerate(CANAIS_FR):
        run_id = '%s-FR-%s' % (MISSION, c['creator_id'])
        itens, man = coletor.executar(
            ATORES['YOUTUBE_SEARCH'],
            {'startUrls': [{'url': c['url']}], 'maxResults': 30,
             'sortVideosBy': 'NEWEST'},
            token=chaves[i % len(chaves)], run_id=run_id, platform='YOUTUBE',
            country='FR', mission=MISSION, query=c['url'],
            source_version=cr.NAO_SEI,
            evidence_path='data/samples/CREATOR-MAP-EAME/FR-ACTIVITY.json')
        coletor.registrar(man, item_count_normalized=len(itens))
        import datetime
        hoje = datetime.datetime.utcnow()
        datas = []
        for v in itens:
            t = v.get('date') or v.get('publishedAt') or v.get('uploadDate') or ''
            try:
                datas.append(datetime.datetime.strptime(str(t)[:10], '%Y-%m-%d'))
            except (ValueError, TypeError):
                pass
        datas.sort(reverse=True)
        if datas:
            dias = (hoje - datas[0]).days
            estado = ('ACTIVE_RECENT' if dias <= 30 else
                      'ACTIVE_STALE' if dias <= 180 else 'DORMANT')
            ultimo = datas[0].strftime('%Y-%m-%d')
        else:
            estado, ultimo = 'NOT_MEASURED', cr.NAO_SEI
        fora.append({
            'CREATOR_ID': c['creator_id'], 'NAME': c['nome'],
            'CHANNEL_URL': c['url'], 'HANDLE': c['handle'],
            'URL_SOURCE': c['fonte'],
            'RUN_STATUS': man['STATUS'], 'COST_USD': man['COST_USD'],
            'VIDEOS_READ': len(itens),
            'ACTIVITY_STATE': estado, 'LAST_ACTIVITY_DATE': ultimo,
            'VIDEOS_LAST_30D': len([d for d in datas if (hoje - d).days <= 30]) if datas else cr.NAO_SEI,
            'VIDEOS_LAST_90D': len([d for d in datas if (hoje - d).days <= 90]) if datas else cr.NAO_SEI,
            'TITLES_SAMPLE': [v.get('title') for v in itens[:8]],
            'AS_OF_DATE': coletor.agora()[:10],
        })
        print('  %-22s videos=%-3d %-13s last=%s' % (c['nome'], len(itens), estado, ultimo))
    _grava('FR-ACTIVITY.json', {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': coletor.agora(),
        'LAW': 'so canais de URL CONFIRMADA por fonte. Inferir endereco de canal e o '
               'mesmo erro que inferir handle de pessoa — ja cometido e corrigido '
               'nesta missao (o canal do David Forge chama-se "La Chaine Agricole").',
        'CHANNELS': fora})


if __name__ == '__main__':
    # Aceita tanto `contratos` quanto `creators-contratos`: a ponte pelo
    # workflow de sensores entrega o nome prefixado.
    fase = (sys.argv[1] if len(sys.argv) > 1 else 'contratos')
    fase = fase[len('creators-'):] if fase.startswith('creators-') else fase
    # Fase desconhecida NÃO cai em `contratos`. Um default silencioso faria o
    # workflow relatar sucesso tendo rodado outra coisa — e o log diria
    # "contratos" enquanto o pedido dizia "atividade". Falhar aqui é a diferença
    # entre um erro visível e um artefato que ninguém sabe de onde veio.
    FASES = {'contratos': contratos, 'resolver': resolver, 'seed': seed,
             'diag': diag, 'atividade': atividade, 'hubs': hubs,
             'descobertos': descobertos, 'conteudo': conteudo, 'franca': franca}
    if fase not in FASES:
        print('FASE_DESCONHECIDA=%r · fases validas: %s'
              % (fase, ', '.join(sorted(FASES))))
        raise SystemExit(2)
    with escopo_da_missao():
        FASES[fase]()
