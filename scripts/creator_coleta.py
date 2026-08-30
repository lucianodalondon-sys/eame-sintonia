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


coletor._curl = _http

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

pv.MANIFESTO = os.path.join(cr.BASE, 'RUN-MANIFEST-CREATORS.json')

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
             'diag': diag, 'atividade': atividade}
    if fase not in FASES:
        print('FASE_DESCONHECIDA=%r · fases validas: %s'
              % (fase, ', '.join(sorted(FASES))))
        raise SystemExit(2)
    FASES[fase]()
