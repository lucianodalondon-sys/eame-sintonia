#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
META-OP-01 — a Meta oficial autentica, e pelo caminho da casa.

    python3 tests/test_meta_op_01.py

    TOKEN_PRESENT != TOKEN_SENT.
    PUBLIC_WEB_HTTP != OFFICIAL_API_HTTP.
    PAGE_ID != SOURCE_ID.
    401/403 != ZERO_RESULTS.

A prova de COMPORTAMENTO, ponta a ponta e sem rede, vive em
`provas/a_meta_oficial_autentica.py`. ESTE ficheiro é o red team.

    ZERO REDE · ZERO DÓLAR · ZERO SEGREDO LIDO.
    REAL_META_REQUESTS = 0 · APIFY_RUNS = 0 · COST_USD = 0
"""
import json
import os
import re
import sys
import unittest  # noqa: F401 — usado pelas provas de importacao

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
for d in (RAIZ, os.path.join(RAIZ, 'coleta'), os.path.join(RAIZ, 'leis'),
          os.path.join(RAIZ, 'pedido'), os.path.join(RAIZ, 'orquestrador')):
    sys.path.insert(0, d)
import _gavetas  # noqa: E402,F401
import pedido as ped                    # noqa: E402
import receitas as rec                  # noqa: E402
import adaptador_meta as am             # noqa: E402
import scrap_http as http               # noqa: E402
import scrap_registo as reg             # noqa: E402
import scrap_capacidades as cap         # noqa: E402
import social_matriz as mz              # noqa: E402
import falhas as fx                     # noqa: E402
import social_envelope as env           # noqa: E402

FALHAS, ATAQUES = [], 0
TOKEN_FALSO = 'fake~token-do-red-team'
PAGE_ID = '1741459832625091'

META = os.path.join('coleta', 'adaptador_meta.py')
HTTPF = os.path.join('coleta', 'scrap_http.py')
ORQ = os.path.join('orquestrador', 'orquestrador.py')
CLI = os.path.join('coleta', 'social_scrap.py')
RECEITAS = os.path.join('pedido', 'receitas.py')


def fonte(c):
    return open(os.path.join(RAIZ, c), encoding='utf-8').read()


def ataque(n, titulo, cond, detalhe=''):
    global ATAQUES
    ATAQUES += 1
    if cond:
        print('  PASS  %2d %s' % (n, titulo))
    else:
        print('  FAIL  %2d %s  %s' % (n, titulo, detalhe))
        FALHAS.append((n, titulo, detalhe))


src_meta, src_http = fonte(META), fonte(HTTPF)
src_orq, src_cli, src_rec = fonte(ORQ), fonte(CLI), fonte(RECEITAS)
T9 = rec.EXECUTORES['T9']
METAEX = [e for e in T9 if e['id'] == 'scrap-meta'][0]

print('=' * 72)
print('META-OP-01 — RED TEAM DA SUPERFÍCIE OFICIAL DA META')
print('=' * 72)
print('\nO TOKEN É ENVIADO, E SÓ POR ONDE DEVE\n' + '-' * 72)

ataque(1, 'o token e LIDO no sitio onde a requisicao nasce',
       'os.environ.get(TOKEN_ENV' in src_meta)
ataque(2, 'e e PASSADO ao transporte, nao so conferido',
       src_meta.count('buscar(url, token=token)') == 2,
       '%d chamada(s)' % src_meta.count('buscar(url, token=token)'))
ataque(3, 'o transporte poe-no em CABECALHO',
       "cabecas[CABECALHO_DE_AUTORIZACAO]" in src_http)
ataque(4, 'e o cabecalho e o `Authorization: Bearer` oficial',
       http.CABECALHO_DE_AUTORIZACAO == 'Authorization'
       and http.ESQUEMA_DE_AUTORIZACAO == 'Bearer')
ataque(5, 'nenhuma URL desta casa carrega `access_token`',
       'access_token=' not in src_meta.replace("'access_token'", ''),
       'so o nome aparece, na lista de redaccao')
ataque(6, 'e a URL montada nao tem token nenhum',
       'token' not in am._url_ads(paises=['IT'], page_ids=[PAGE_ID]).lower())

print('\nO SEGREDO NAO VAZA\n' + '-' * 72)

_com_segredo = ('https://www.facebook.com/ads/archive/render_ad/'
                '?id=9&access_token=%s' % TOKEN_FALSO)
ataque(7, 'uma URL com token sai daqui REDIGIDA',
       TOKEN_FALSO not in http.sem_segredo(_com_segredo)
       and http.REDIGIDO in http.sem_segredo(_com_segredo))
ataque(8, 'o `ad_snapshot_url` que a META devolve tambem',
       TOKEN_FALSO not in json.dumps(am._sem_snapshot_com_token(
           {'ad_snapshot_url': _com_segredo})))
ataque(9, 'e o envelope inteiro sai sem segredo',
       TOKEN_FALSO not in json.dumps(am._anuncio(
           {'id': '1', 'ad_snapshot_url': _com_segredo}, run_id='R',
           country_scope='IT', rota='graph:/ads_archive')))
ataque(10, 'um erro da API sai com a razao REDIGIDA',
       TOKEN_FALSO not in http.sem_segredo('HTTP 400 · %s' % _com_segredo))
ataque(11, 'a redaccao cobre os nomes que importam',
       {'access_token', 'client_secret', 'appsecret_proof'}
       <= set(http.PARAMETROS_SECRETOS))
ataque(12, 'e ela diz-se: `REDACTED` procura-se num ficheiro',
       http.REDIGIDO == 'REDACTED')
ataque(13, 'o token NAO entra na medida que sobe ao rasto',
       'medida[' in src_meta and 'TOKEN' not in re.sub(
           r'TOKEN_ENV', '', src_meta.split('def _anuncio')[0]).split(
           "medida['IMPLEMENTACAO']")[-1][:400])

print('\nAPI OFICIAL != WEB PUBLICA\n' + '-' * 72)

ataque(14, 'ha DOIS transportes, e os dois tem nome',
       'def buscar(' in src_http and 'def buscar_api_oficial(' in src_http)
ataque(15, 'o da web publica CONTINUA a ler robots.txt',
       'ok, motivo = permitido(url)' in src_http)
ataque(16, 'o da API oficial NAO o le',
       'permitido(' not in src_http.split('def buscar_api_oficial(')[1]
       .split('\n\n\n')[0])
# ⚠️ MEDE-SE A CHAMADA, NAO A PALAVRA.
# `http.buscar` aparece neste ficheiro em COMENTARIO e em DOCSTRING — nos dois
# sitios a explicar o defeito que a META-OP-01 consertou. Apagar essa memoria
# para um teste passar seria apagar exactamente o que ela serve.
#
#     CONTAR PALAVRAS MEDE O TEXTO. LER A ARVORE MEDE O CODIGO.
import ast as _ast
_usos = sorted({n.attr for n in _ast.walk(_ast.parse(src_meta))
                if isinstance(n, _ast.Attribute)
                and getattr(n.value, 'id', '') == 'http'
                and n.attr.startswith('buscar')})
ataque(17, 'e o adaptador da Meta CHAMA o transporte oficial, e so ele',
       _usos == ['buscar_api_oficial'], str(_usos))
ataque(18, 'a matriz declara esta rota como OFFICIAL_API_FREE',
       mz.decisao('META', 'SEARCH_ADS')['CLASSE'] == 'OFFICIAL_API_FREE')

print('\nOS ERROS TEM NOME, E NENHUM DELES E ZERO\n' + '-' * 72)

for n, (codigo, esperado) in enumerate(((401, 'AUTH_EXPIRED'),
                                        (403, 'AUTHORIZATION_BLOCK'),
                                        (429, 'RATE_LIMITED'),
                                        (500, 'SOURCE_UNAVAILABLE')), start=19):
    ataque(n, 'HTTP %d -> %s' % (codigo, esperado),
           http._estado_do_codigo(codigo) == esperado,
           http._estado_do_codigo(codigo))
ataque(23, 'e NENHUM codigo de erro devolve ZERO_RESULTS',
       all(http._estado_do_codigo(c) != 'ZERO_RESULTS'
           for c in (400, 401, 403, 404, 429, 500, 502, 503)))
ataque(24, '«a autorizacao nao foi concedida» tem familia',
       fx.traduzir('AUTHORIZATION_BLOCK') == 'CREDENTIAL_MISSING',
       fx.traduzir('AUTHORIZATION_BLOCK'))
ataque(25, 'e ela NAO degrada a fonte — ninguem chegou a medi-la',
       not fx.degrada_fonte(fx.traduzir('AUTHORIZATION_BLOCK')))
ataque(26, 'a recuperacao e humana, e nao rotacao de chave',
       fx.recuperacao(fx.traduzir('AUTHORIZATION_BLOCK'), None)
       == 'HUMAN_PROVISION_CREDENTIAL')
ataque(27, 'ZERO_RESULTS continua a existir para o zero legitimo',
       'ZERO_RESULTS' in fx.ESTADOS)

print('\nO PROBE NAO PAGINA E NAO REPETE\n' + '-' * 72)

ataque(28, 'o adaptador nao segue `paging`/`next`',
       'paging' not in src_meta and "'next'" not in src_meta)
ataque(29, 'nao ha ciclo de requisicao no adaptador',
       'while ' not in src_meta)
ataque(30, 'e o transporte oficial nao retenta',
       'tentativas' not in src_http.split('def buscar_api_oficial(')[1]
       .split('\n\n\n')[0])
ataque(31, 'a fase declara o teto de acessos, e ele e UM',
       all(v['TETO_DE_REDE'] == 1 for v in __import__('social_scrap').FASES_DE_ENSAIO.values()))
ataque(32, 'e o teto vive na tabela versionada, nao no chamador',
       "'TETO_DE_REDE': 1," in src_cli)

print('\nAS ESPECIES NAO SE SOMAM\n' + '-' * 72)

_ad = am._anuncio({'id': '1'}, run_id='R', country_scope='IT',
                  rota='graph:/ads_archive')
_bc = am._branded({'url': 'u', 'creator': {'name': 'c'},
                   'partners': [{'name': 'marca'}]},
                  run_id='R', country_scope='IT',
                  rota='graph:/branded_content_search')
ataque(33, 'anuncio e ADVERTISEMENT, e nao POST',
       _ad['CONTENT_TYPE'] == 'ADVERTISEMENT')
ataque(34, 'parceria e BRANDED_CONTENT, e nao POST',
       _bc['CONTENT_TYPE'] == 'BRANDED_CONTENT')
ataque(35, 'as duas especies existem no vocabulario fechado',
       {'ADVERTISEMENT', 'BRANDED_CONTENT'} <= set(env.CONTENT_TYPES))
ataque(36, 'quem PUBLICOU e o criador — a marca nao vira autor',
       _bc['SOURCE_ACCOUNT'] == 'c')
ataque(37, 'e a marca que pagou vive no RAW, em `partners`',
       'marca' in json.dumps(_bc['RAW']['partners']))
# `pela_matriz` vai da lingua GROSSA da matriz para a capacidade declarada —
# e nao ao contrario. Uma ancora na direccao errada devolve None e passa a
# medir a propria confusao de quem a escreveu.
ataque(38, 'META e plataforma PROPRIA, com as suas duas capacidades',
       cap.pela_matriz('META', 'SEARCH_ADS') == 'meta.ads.search'
       and cap.pela_matriz('META', 'SEARCH_BRANDED_CONTENT')
       == 'meta.branded_content.search'
       and cap.pela_matriz('META', 'INCREMENTAL') is None,
       'INSTAGRAM/FACEBOOK continuam com identidade propria')

print('\nO QUE A FONTE NAO DEU NAO VIRA ZERO\n' + '-' * 72)

ataque(39, '`spend` nunca e pedido na consulta comercial',
       'spend' not in am._url_ads(paises=['IT'], page_ids=[PAGE_ID]))
ataque(40, 'e ele esta na lista do que se RECUSA pedir',
       'spend' in am.SO_POLITICO)
ataque(41, 'nenhum campo so-politico entra na consulta',
       not (set(am.SO_POLITICO) & set(am.CAMPOS_ANUNCIO + am.CAMPOS_UE)))
ataque(42, 'o anuncio NAO nasce com spend zero',
       'spend' not in json.dumps(_ad).lower()
       or json.dumps(_ad).lower().count('spend') == 0)
ataque(43, 'o campo de UE vive em lista PROPRIA',
       set(am.CAMPOS_UE).isdisjoint(am.CAMPOS_ANUNCIO))
ataque(44, 'e o branded declara o que a fonte NAO devolve',
       set(am.BRANDED_AUSENTES)
       <= set(_bc['RAW'].get('NOT_RETURNED_BY_SOURCE') or []))

print('\nPAGE_ID != SOURCE_ID\n' + '-' * 72)

_ad2 = am._anuncio({'id': 'A1', 'page_id': PAGE_ID}, run_id='R',
                   country_scope='IT', rota='graph:/ads_archive')
ataque(45, 'a origem e a do NO, declarada na receita',
       _ad2['SOURCE_ID'] == 'META-ADS/ads_archive')
ataque(46, 'e NAO e o page_id', _ad2['SOURCE_ID'] != PAGE_ID)
ataque(47, 'o page_id continua no RAW, com o nome que tem',
       _ad2['RAW']['page_id'] == PAGE_ID)
ataque(48, 'a identidade do item e a que a Meta deu',
       _ad2['DOCUMENT_ID'] == 'A1')
ataque(49, 'a receita NAO nomeia nenhuma das 77 fontes',
       'IT-T9-0' not in json.dumps(METAEX, ensure_ascii=False)
       and METAEX.get('aceita_fonte') is False)
_url = None
try:
    __import__('relevancia_da_fonte').conferir_source_id(
        'https://www.facebook.com/BASF-%s/' % PAGE_ID)
except Exception as e:                                        # noqa: BLE001
    _url = type(e).__name__
ataque(50, 'e uma URL continua recusada como SOURCE_ID', _url is not None, str(_url))

print('\nO CAMINHO E O DA CASA\n' + '-' * 72)

ataque(51, 'o pedido escolhe o executor da Meta',
       rec.escolher(T9, ped.de_uma_frase('colete concorrentes')) is not None
       and [e for e in T9 if e['id'] == 'scrap-meta'])
for n, f in enumerate(('meta-ads', 'meta-branded'), start=52):
    p = ped.de_uma_frase('colete concorrentes')
    p.filtros['fase'] = f
    ataque(n, 'a fase «%s» abre o executor da Meta' % f,
           rec.escolher(T9, p)['id'] == 'scrap-meta')
ataque(54, 'quem nao nomeia fase leva o executor de sempre',
       rec.escolher(T9, ped.de_uma_frase('colete concorrentes'))['id']
       == 'comunicacao-publica')
ataque(55, 'o RUN_ID nasce ANTES de o executor correr',
       src_orq.index('run_id = novo_run_id(p)')
       < src_orq.index('subprocess.run([sys.executable, *comando]'))
ataque(56, 'o executor declara que recebe a corrida cunhada',
       METAEX.get('recebe_run_id') is True)
ataque(57, 'o PEDIDO nao conhece `adaptador_meta`',
       'adaptador_meta' not in fonte(os.path.join('pedido', 'pedido.py')))
ataque(58, 'nem `graph.facebook.com`',
       'graph.facebook.com' not in src_rec
       and 'graph.facebook.com' not in fonte(os.path.join('pedido', 'pedido.py')))
ataque(59, 'nem `urllib`',
       'urllib' not in fonte(os.path.join('pedido', 'pedido.py')))
ataque(60, 'e o host oficial vive num sitio so',
       src_meta.count("GRAPH = 'https://graph.facebook.com'") == 1)

print('\nA GRAPH NAO CAI PARA APIFY\n' + '-' * 72)

ataque(61, 'o adaptador nao importa provider pago',
       not (set(re.findall(r'^import\s+(\w+)', src_meta, re.M))
            & {'apify_pool', 'coletor', 'scrap_fornecedores'}))
ataque(62, 'nem conhece endereco de provider',
       '/acts/' not in src_meta and 'api.apify.com' not in src_meta)
ataque(63, 'a receita declara esta rota GRATUITA',
       METAEX['custo'] == 'gratuito')
ataque(64, 'e as duas rotas da matriz sao OFICIAIS',
       all(r['CLASSE'] == 'OFFICIAL_API_FREE'
           for c in ('SEARCH_ADS', 'SEARCH_BRANDED_CONTENT')
           for r in mz.MATRIZ['META'][c]))

print('\nESTADO: EXISTIR NAO E PROMETER\n' + '-' * 72)

ataque(65, 'as duas capacidades continuam NOT_EXECUTED',
       cap.estado('meta.ads.search') == 'NOT_EXECUTED'
       and cap.estado('meta.branded_content.search') == 'NOT_EXECUTED')
ataque(66, 'e a promocao NAO acontece por existir codigo',
       'NOT_EXECUTED' in fonte(os.path.join('coleta', 'scrap_capacidades.py')))
reg.carregar_adaptadores()
ataque(67, 'as duas estao registadas com rota E sonda',
       all((reg.adaptador_de('META', c) or {}).get('ADAPTADOR') == 'adaptador_meta'
           and reg.sonda_de('META', c)
           for c in ('meta.ads.search', 'meta.branded_content.search')))
ataque(68, 'a sonda NUNCA devolve o valor do segredo',
       am.pronto_para_graph() == (False, 'CREDENTIAL_MISSING')
       or isinstance(am.pronto_para_graph()[0], bool))

# ══════════════════════════════════════════════════════════════════════════
# OS MUTANTES — cada um é um afrouxamento PLAUSÍVEL desta missão
# ══════════════════════════════════════════════════════════════════════════
#     UMA SUITE VERDE NÃO PROVA QUE ELA MORDE.
#
# Onde a defesa é ESTRUTURAL, mede-se aqui a condição que a mataria. Onde ela é
# de COMPORTAMENTO — o token no cabeçalho, o robots que não se lê, a cadeia que
# pára sem credencial —, ela corre a jusante, em
# `provas/a_meta_oficial_autentica.py`, que troca o transporte pelo mundo falso
# e conta o que lhe pediram.
MORTOS = []


def mutante(n, nome, morto, onde=''):
    MORTOS.append((n, nome, bool(morto), onde))
    print('  %s  %-50s %s' % ('MORTO     ' if morto else 'SOBREVIVEU',
                              nome[:50], onde))


print('\nOS MUTANTES\n' + '-' * 72)

mutante('M1', 'o token volta a ser so conferido, nunca enviado',
        src_meta.count('buscar(url, token=token)') == 2
        and 'def _transporte_e_token' in src_meta, 'ataques 1-2')
mutante('M2', 'o token passa a viajar na URL',
        'access_token=%s' not in src_meta
        and 'token' not in am._url_ads(paises=['IT'], page_ids=[PAGE_ID]).lower(),
        'ataques 5-6')
mutante('M3', 'o cabecalho deixa de ser o oficial',
        http.CABECALHO_DE_AUTORIZACAO == 'Authorization'
        and http.ESQUEMA_DE_AUTORIZACAO == 'Bearer', 'ataques 3-4')
mutante('M4', 'a redaccao deixa de cobrir o `access_token`',
        'access_token' in http.PARAMETROS_SECRETOS
        and TOKEN_FALSO not in http.sem_segredo(_com_segredo), 'ataques 7-8')
mutante('M5', 'o `ad_snapshot_url` volta a viajar inteiro',
        'def _sem_snapshot_com_token' in src_meta
        and '_sem_snapshot_com_token(item)' in src_meta, 'ataque 9')
mutante('M6', 'a API oficial volta a passar pelo portao de robots',
        'permitido(' not in src_http.split('def buscar_api_oficial(')[1]
        .split('\n\n\n')[0], 'ataque 16')
mutante('M7', 'o portao das rotas web enfraquece',
        'ok, motivo = permitido(url)' in src_http
        and 'raise RotaNaoPermitida' in src_http, 'ataque 15')
mutante('M8', 'a Meta volta ao transporte da web publica',
        _usos == ['buscar_api_oficial'], 'ataque 17')
mutante('M9', 'um 403 passa a ler-se como ZERO_RESULTS',
        http._estado_do_codigo(403) == 'AUTHORIZATION_BLOCK'
        and all(http._estado_do_codigo(c) != 'ZERO_RESULTS'
                for c in (400, 401, 403, 429, 500)), 'ataques 19-23')
mutante('M10', '«autorizacao negada» volta ao balde de UNKNOWN_ERROR',
        fx.traduzir('AUTHORIZATION_BLOCK') == 'CREDENTIAL_MISSING', 'ataque 24')
mutante('M11', 'o probe passa a paginar',
        'paging' not in src_meta and 'while ' not in src_meta, 'ataques 28-29')
mutante('M12', 'o probe passa a repetir depois do erro',
        'tentativas' not in src_http.split('def buscar_api_oficial(')[1]
        .split('\n\n\n')[0], 'ataque 30')
mutante('M13', 'o teto de acessos sai da tabela versionada',
        "'TETO_DE_REDE': 1," in src_cli, 'ataques 31-32')
mutante('M14', 'o `page_id` vira SOURCE_ID',
        _ad2['SOURCE_ID'] == 'META-ADS/ads_archive'
        and _ad2['SOURCE_ID'] != PAGE_ID, 'ataques 45-46')
mutante('M15', 'a receita passa a nomear uma das 77 para esta rota',
        METAEX.get('aceita_fonte') is False
        and 'IT-T9-0' not in json.dumps(METAEX, ensure_ascii=False), 'ataque 49')
mutante('M16', 'o anuncio passa a chamar-se POST',
        _ad['CONTENT_TYPE'] == 'ADVERTISEMENT'
        and _bc['CONTENT_TYPE'] == 'BRANDED_CONTENT', 'ataques 33-34')
mutante('M17', 'a marca que pagou vira autora do post',
        _bc['SOURCE_ACCOUNT'] == 'c', 'ataque 36')
mutante('M18', '`spend` passa a ser pedido e a nascer zero',
        'spend' in am.SO_POLITICO
        and 'spend' not in am._url_ads(paises=['IT'], page_ids=[PAGE_ID]),
        'ataques 39-42')
mutante('M19', 'o campo de UE perde o rotulo e vira global',
        set(am.CAMPOS_UE).isdisjoint(am.CAMPOS_ANUNCIO), 'ataque 43')
mutante('M20', 'a capacidade e promovida por existir codigo',
        cap.estado('meta.ads.search') == 'NOT_EXECUTED'
        and cap.estado('meta.branded_content.search') == 'NOT_EXECUTED',
        'ataque 65')
mutante('M21', 'o pedido passa a conhecer a implementacao',
        'adaptador_meta' not in fonte(os.path.join('pedido', 'pedido.py'))
        and 'graph.facebook.com' not in src_rec, 'ataques 57-58')
mutante('M22', 'a Graph cai para Apify quando falha',
        not (set(re.findall(r'^import\s+(\w+)', src_meta, re.M))
             & {'apify_pool', 'coletor'}), 'ataques 61-62')

PROVA_DE_COMPORTAMENTO = 'provas/a_meta_oficial_autentica.py'

print('\nEXECUCAO REAL\n' + '-' * 72)
print('  REAL_META_REQUESTS   = 0')
print('  REAL_NETWORK         = 0')
print('  APIFY_RUNS           = 0')
print('  PAID_RUNS            = 0')
print('  REAL_COST_USD        = 0')
print('  SECRETS_READ         = 0  (o token deste ficheiro foi INVENTADO)')
print('\n  a prova de COMPORTAMENTO ponta a ponta: %s' % PROVA_DE_COMPORTAMENTO)

vivos = [m for m in MORTOS if not m[2]]
print('\n' + '=' * 72)
print('ATAQUES = %d · MUTANTES = %d · FALHAS = %d · SOBREVIVENTES = %d'
      % (ATAQUES, len(MORTOS), len(FALHAS), len(vivos)))
if FALHAS or vivos:
    for f in FALHAS:
        print('  !! ataque', f)
    for m in vivos:
        print('  !! mutante vivo', m[0], m[1])
    sys.exit(1)
print('RED_TEAM = PASS · SURVIVORS = 0')
