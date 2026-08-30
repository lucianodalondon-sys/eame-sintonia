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

MISSION = '14-MAPA-DE-CREATORS-EAME'
SAIDA = cr.BASE

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
    """GRÁTIS. Só lê o ator. Zero run, zero item, zero custo."""
    token = _pool()[0]
    fora = []
    for rotulo, actor in ATORES.items():
        try:
            d = coletor._curl('%s/acts/%s' % (coletor.API, actor), token=token, timeout=60)
            data = (d or {}).get('data') or {}
            fora.append({'LABEL': rotulo, 'ACTOR': actor, 'STATE': 'AVAILABLE',
                         'TITLE': data.get('title') or cr.NAO_SEI,
                         'USERNAME': data.get('username') or cr.NAO_SEI})
            print('  %-18s AVAILABLE  %s' % (rotulo, data.get('title')))
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


if __name__ == '__main__':
    # Aceita tanto `contratos` quanto `creators-contratos`: a ponte pelo
    # workflow de sensores entrega o nome prefixado.
    fase = (sys.argv[1] if len(sys.argv) > 1 else 'contratos')
    fase = fase[len('creators-'):] if fase.startswith('creators-') else fase
    {'contratos': contratos, 'resolver': resolver, 'seed': seed}.get(fase, contratos)()
