#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A META OFICIAL AUTENTICA, E PELO CAMINHO DA CASA? — prova offline.

    python3 provas/a_meta_oficial_autentica.py

A META-BUILD-01 deixou as duas capacidades oficiais da Meta `DECLARED`,
`REGISTERED`, `WIRED` e `NOT_EXECUTED`. Esta prova responde à pergunta
seguinte, que ninguém tinha feito:

    TOKEN_PRESENT  !=  TOKEN_SENT.

Medido antes desta missão: `META_GRAPH_TOKEN` aparecia numa linha só do
repositório — a constante que a SONDA lê. As duas rotas montavam a URL,
chamavam `http.buscar(url)`, e a requisição sairia **anónima**.

O QUE ESTA PROVA MEDE
---------------------
    P0  a cadeia está ligada, e o pedido escolhe o executor da Meta
    P1  o token CHEGA — em cabeçalho, nunca na URL, e nunca no rasto
    P2  o transporte é o da API OFICIAL, e não o da web pública
    P3  o caminho começa no PEDIDO, e pára com o nome certo sem credencial
    P4  um 401/403/429 tem nome próprio — e NENHUM deles é `ZERO_RESULTS`
    P5  `page_id` NÃO vira `SOURCE_ID`, e os dois viajam separados
    P6  ADVERTISEMENT != POST · BRANDED_CONTENT != POST · BRAND != AUTOR
    P7  o campo de UE viaja com rótulo, e o campo político não é pedido
    P8  nenhuma destas duas rotas conhece Apify

O QUE É FALSO AQUI
------------------
Falso: **só o mundo lá fora** — o transporte HTTP. Numa prova ele é uma função
que regista o que lhe pediram; noutra é o `urlopen` do `urllib`, que é a
fronteira mais funda desta casa antes do socket.

    UM FAKE ACIMA DO GATE MEDE O FAKE.

Não é falso — e falsificá-lo invalidaria tudo: `pedido`, `receitas`,
`orquestrador`, `scrap_executor`, `social_rotas`, `scrap_registo`,
`adaptador_meta`, `scrap_http`, `relevancia_da_fonte`, `retorno_da_coleta`.

E NENHUM SEGREDO EXISTE NESTA MÁQUINA
-------------------------------------
`META_GRAPH_TOKEN` está AUSENTE. Esta prova NÃO o procura, não cria conta, não
faz login e não usa token de outra integração. Onde precisa de um token para
medir o encaminhamento, ela inventa um obviamente falso e diz que o inventou.

    REAL_META_REQUESTS = 0 · REAL_NETWORK = 0 · APIFY_RUNS = 0 · COST_USD = 0
"""

import json
import os
import sys
import urllib.error

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import pedido as ped                    # noqa: E402
import receitas as rec                  # noqa: E402
import orquestrador as orq              # noqa: E402
import scrap_executor as scrap          # noqa: E402
import scrap_http as http               # noqa: E402
import scrap_registo as reg             # noqa: E402
import adaptador_meta as am             # noqa: E402
import falhas as fx                     # noqa: E402
import relevancia_da_fonte as rel       # noqa: E402

FALHAS = []
PROVAS = 0

#: Um token OBVIAMENTE falso. Ele existe para medir ENCAMINHAMENTO, e mais nada:
#: nenhuma requisição real sai desta prova, e nenhum segredo desta casa é lido.
TOKEN_FALSO = 'fake~token-da-prova-META-OP-01'

#: As sentinelas da META-DEEP-01, revalidadas nesta missão contra o lote
#: congelado: `1741459832625091` vive no `ACCOUNT_URL` da BASF IT no Facebook,
#: e `bayer_italia` é o handle da BAYER IT no Instagram.
PAGE_ID_BASF_IT = '1741459832625091'
IG_BAYER_IT = 'bayer_italia'

#: Tudo o que a cadeia inteira escreve. Fotografado antes, reposto depois.
ESCRITOS_PELA_CADEIA = (
    os.path.join('data', 'samples', 'LIVRO-DE-DECISOES.json'),
    os.path.join('data', 'samples', 'RUN-MANIFEST.json'),
    os.path.join('data', 'colheita', 'scrap', 'RETORNO.json'),
)


def diz(ok, titulo, detalhe=''):
    global PROVAS
    PROVAS += 1
    print('  %s  %-52s %s' % ('OK   ' if ok else 'FALHA', titulo[:52], detalhe))
    if not ok:
        FALHAS.append('%s · %s' % (titulo, detalhe))
    return ok


class CasaIntacta(object):
    def __init__(self):
        self.antes = {}

    def __enter__(self):
        for r in ESCRITOS_PELA_CADEIA:
            c = os.path.join(RAIZ, r)
            self.antes[r] = open(c, 'rb').read() if os.path.isfile(c) else None
        return self

    def __exit__(self, *a):
        self.repor()
        return False

    def repor(self):
        for r, corpo in self.antes.items():
            c = os.path.join(RAIZ, r)
            if corpo is None:
                if os.path.isfile(c):
                    os.remove(c)
            else:
                os.makedirs(os.path.dirname(c), exist_ok=True)
                with open(c, 'wb') as f:
                    f.write(corpo)

    def confere(self):
        mal = []
        for r, corpo in self.antes.items():
            c = os.path.join(RAIZ, r)
            agora = open(c, 'rb').read() if os.path.isfile(c) else None
            if agora != corpo:
                mal.append(r)
        return mal


CASA = CasaIntacta()


class TransporteFalso(object):
    """O mundo, reduzido ao que ele devolve. Regista TUDO o que lhe pediram.

    A assinatura é a MESMA de `scrap_http.buscar_api_oficial` — se ela mudar,
    esta prova parte, que é exactamente o que uma prova deve fazer quando o
    contrato que ela mede muda.
    """

    def __init__(self, corpo=None, erro=None):
        self.corpo = corpo if corpo is not None else json.dumps({'data': []})
        self.erro = erro
        self.pedidos = []

    def __call__(self, url, *, token=None, **k):
        self.pedidos.append({'URL': url, 'TOKEN': token, 'EXTRA': k})
        if self.erro is not None:
            raise self.erro
        return self.corpo


def com_token(valor=TOKEN_FALSO):
    antes = os.environ.get(am.TOKEN_ENV)
    os.environ[am.TOKEN_ENV] = valor
    return antes


def repor_token(antes):
    if antes is None:
        os.environ.pop(am.TOKEN_ENV, None)
    else:
        os.environ[am.TOKEN_ENV] = antes


def colher(capacidade, transporte, **kw):
    """Corre pelo CAMINHO DA CASA. Nunca chama o adaptador directamente."""
    return scrap.COLLECT(platform='META', capability=capacidade, run_id='PROVA-META',
                         modo=scrap.TRIAL, teto_de_rede=1, transporte=transporte,
                         **kw)


ANUNCIO_FALSO = {
    'id': 'AD-FALSO-1',
    'page_id': PAGE_ID_BASF_IT,
    'page_name': 'BASF Agricultural Solutions Italia',
    'ad_snapshot_url': ('https://www.facebook.com/ads/archive/render_ad/'
                        '?id=AD-FALSO-1&access_token=' + TOKEN_FALSO),
    'ad_creative_bodies': ['nenhuma destas letras veio da Meta'],
    'ad_delivery_start_time': '2026-01-10',
    'eu_total_reach': 12345,
}
PARCERIA_FALSA = {
    'url': 'https://www.instagram.com/p/FALSO000001/',
    'creator': {'name': 'criador.falso', 'id': '1'},
    'partners': [{'name': 'bayer_italia', 'id': '2'}],
    'type': 'IG_MEDIA',
    'creation_date': '2026-01-10',
}


def p0_a_cadeia_esta_ligada():
    print('\nP0 · A CADEIA ESTÁ LIGADA\n' + '-' * 72)
    p = ped.de_uma_frase('colete concorrentes')
    p.filtros['fase'] = 'meta-ads'
    plano = rec.resolver(p)
    e = plano.escolhido or {}
    diz(e.get('id') == 'scrap-meta', 'o PEDIDO escolhe o executor da Meta',
        e.get('id'))
    diz(e.get('custo') == 'gratuito' and rel.custo_e_gratuito(e.get('custo')),
        'e ele declara-se GRATUITO: o preço não é dinheiro', e.get('custo'))
    diz(plano.bloqueia_a_corrida is False and plano.barra_a_observacao is False,
        'o portão foi consultado e deixa passar — não há gasto a guardar',
        plano.relevancia.get('VEREDITO'))
    reg.carregar_adaptadores()
    for cap_ in ('meta.ads.search', 'meta.branded_content.search'):
        a = reg.adaptador_de('META', cap_) or {}
        diz(a.get('ADAPTADOR') == 'adaptador_meta',
            'a capacidade %s está registada' % cap_.split('.', 1)[1],
            str(a.get('ADAPTADOR')))


def p1_o_token_chega():
    print('\nP1 · O TOKEN CHEGA — E SÓ EM CABEÇALHO\n' + '-' * 72)
    antes = com_token()
    try:
        t = TransporteFalso(json.dumps({'data': [ANUNCIO_FALSO]}))
        objetos, trace = colher('meta.ads.search', t, paises=['IT'],
                                page_ids=[PAGE_ID_BASF_IT],
                                janela={'MAX_ITEMS': 5})
        diz(len(t.pedidos) == 1, 'UMA requisição — nem zero, nem duas',
            '%d' % len(t.pedidos))
        pedido_feito = t.pedidos[0] if t.pedidos else {}
        diz(pedido_feito.get('TOKEN') == TOKEN_FALSO,
            'o token CHEGOU ao transporte', 'sim' if pedido_feito.get('TOKEN') else 'NÃO')
        url = pedido_feito.get('URL') or ''
        diz('graph.facebook.com' in url, 'e o destino é a Graph oficial',
            url.split('?')[0])
        diz(TOKEN_FALSO not in url and 'access_token' not in url,
            'e ele NÃO viaja na URL')
        diz(TOKEN_FALSO not in json.dumps(trace),
            'nem no rasto da execução')
        diz(TOKEN_FALSO not in json.dumps(objetos),
            'nem em nenhum objeto colhido')
        diz(trace.get('RESULT') == 'OK' and len(objetos) == 1,
            'e a colheita atravessou', '%s · %d' % (trace.get('RESULT'), len(objetos)))
    finally:
        repor_token(antes)
    CASA.repor()

    # ── E O CABEÇALHO REAL? Medido no transporte verdadeiro, sem rede. ──────
    vistos = {}
    real = http.urllib.request.urlopen

    def espia(req, **k):
        vistos['HEADERS'] = dict(getattr(req, 'headers', {}) or {})
        vistos['URL'] = req.full_url
        raise urllib.error.URLError('a prova não abre ligação nenhuma')

    http.urllib.request.urlopen = espia
    try:
        try:
            http.buscar_api_oficial('https://graph.facebook.com/v21.0/ads_archive?x=1',
                                    token=TOKEN_FALSO)
        except http.EstadoDaApi:
            pass
    finally:
        http.urllib.request.urlopen = real
    cabecas = vistos.get('HEADERS') or {}
    autor = cabecas.get('Authorization') or cabecas.get('authorization') or ''
    diz(autor == 'Bearer %s' % TOKEN_FALSO,
        'o transporte real põe `Authorization: Bearer`',
        autor.split(' ')[0] if autor else 'AUSENTE')
    diz(TOKEN_FALSO not in (vistos.get('URL') or ''),
        'e a URL que sai continua sem segredo nenhum')


def p2_o_transporte_certo():
    print('\nP2 · O TRANSPORTE DA API OFICIAL != O DA WEB PÚBLICA\n' + '-' * 72)
    pedidos = []
    real = http.urllib.request.urlopen

    def espia(req, **k):
        pedidos.append(req.full_url)
        raise urllib.error.URLError('a prova não abre ligação nenhuma')

    http.urllib.request.urlopen = espia
    try:
        try:
            http.buscar_api_oficial('https://graph.facebook.com/v21.0/ads_archive?x=1',
                                    token=TOKEN_FALSO)
        except http.EstadoDaApi:
            pass
        oficiais = list(pedidos)
        pedidos.clear()
        http._ROBOTS.clear()
        try:
            http.buscar('https://exemplo.invalid/pagina')
        except Exception:                                      # noqa: BLE001
            pass
        publicos = list(pedidos)
    finally:
        http.urllib.request.urlopen = real
        http._ROBOTS.clear()

    diz(not any('robots.txt' in u for u in oficiais),
        'a API oficial NÃO vai buscar robots.txt', str(oficiais)[:60])
    diz(len(oficiais) == 1,
        'e gasta UMA ida à rede, que é a da própria API',
        '%d ida(s)' % len(oficiais))
    diz(any('robots.txt' in u for u in publicos),
        'e a web pública CONTINUA a ir buscá-lo — o portão não enfraqueceu',
        str(publicos)[:60])
    diz('buscar_api_oficial' in open(
        os.path.join(RAIZ, 'coleta', 'adaptador_meta.py'), encoding='utf-8').read(),
        'e é o transporte oficial que o adaptador da Meta usa')


def p3_o_caminho_comeca_no_pedido():
    print('\nP3 · O CAMINHO COMEÇA NO PEDIDO\n' + '-' * 72)
    # SEM token: é o estado REAL desta máquina, e é ele que se mede.
    antes = os.environ.pop(am.TOKEN_ENV, None)
    try:
        p = ped.de_uma_frase('colete concorrentes')
        p.filtros['fase'] = 'meta-ads'
        recibo = orq.correr(p)
        recibo.pop('_plano', None)
        saida = recibo.get('SAIDA') or ''
        diz(recibo['ACTOR'] == os.path.join('coleta', 'social_scrap.py'),
            'quem correu foi a CLI do SCRAP, chamada pelo orquestrador',
            recibo['ACTOR'])
        diz('coletar meta-ads' in recibo['COMANDO'],
            'e a fase veio do PEDIDO', recibo['COMANDO'])
        diz('--run-id=%s' % recibo['RUN_ID'] in recibo['COMANDO'],
            'com a corrida cunhada ANTES de o executor correr', recibo['RUN_ID'])
        diz('CREDENTIAL_MISSING' in saida,
            'e a cadeia pára com o nome certo: falta a credencial')
        diz('graph:/ads_archive' in saida,
            'depois de ter escolhido a rota oficial')
        diz(recibo['CAPTURE_METHOD'] == 'gratuito' and recibo['COST_USD'] == 0,
            'custo ZERO medido, e não «NAO SEI»',
            '%s · %r' % (recibo['CAPTURE_METHOD'], recibo['COST_USD']))
    finally:
        if antes is not None:
            os.environ[am.TOKEN_ENV] = antes
    CASA.repor()

    # ── E NENHUMA REQUISIÇÃO SAIU ──────────────────────────────────────────
    objetos, trace = colher('meta.ads.search', None, paises=['IT'],
                            page_ids=[PAGE_ID_BASF_IT], janela={'MAX_ITEMS': 5})
    diz(trace.get('NETWORK_REQUESTS_USED') == 0,
        'ZERO idas à rede: não se bate à porta de quem não se tem chave',
        str(trace.get('NETWORK_REQUESTS_USED')))
    diz(trace.get('RESULT') == 'CREDENTIAL_MISSING' and objetos == [],
        'e o resultado é a recusa, não uma colheita vazia',
        trace.get('RESULT'))
    rr = trace.get('ROUTER_RECORD') or {}
    diz(rr.get('RECOVERY_ACTION') == 'HUMAN_PROVISION_CREDENTIAL',
        'com a recuperação que só gente pode fazer',
        str(rr.get('RECOVERY_ACTION')))


def p4_os_erros_tem_nome():
    print('\nP4 · UM 401 NÃO É ZERO, E NUNCA FOI\n' + '-' * 72)
    antes = com_token()
    try:
        casos = ((401, 'AUTH_EXPIRED'), (403, 'AUTHORIZATION_BLOCK'),
                 (429, 'RATE_LIMITED'), (500, 'SOURCE_UNAVAILABLE'),
                 (400, 'PERMANENT_HTTP_ERROR'))
        for codigo, esperado in casos:
            erro = http.EstadoDaApi({
                'STATE': http._estado_do_codigo(codigo),
                'NATIVE_REASON': 'HTTP %s · corpo da prova' % codigo,
                'RECOVERY_ACTION': None})
            t = TransporteFalso(erro=erro)
            objetos, trace = colher('meta.ads.search', t, paises=['IT'],
                                    page_ids=[PAGE_ID_BASF_IT],
                                    janela={'MAX_ITEMS': 5})
            rr = trace.get('ROUTER_RECORD') or {}
            visto = rr.get('ESTADO_ORIGINAL') or rr.get('ESTADO')
            diz(visto == esperado or fx.traduzir(esperado) == rr.get('ESTADO'),
                'HTTP %d diz-se «%s»' % (codigo, esperado),
                '%s / %s' % (rr.get('ESTADO'), rr.get('ESTADO_ORIGINAL')))
            diz(trace.get('RESULT') != 'ZERO_RESULTS' and objetos == [],
                'e HTTP %d NÃO é ZERO_RESULTS' % codigo, str(trace.get('RESULT')))
            diz(len(t.pedidos) == 1,
                'e não se repete o pedido depois do erro', '%d' % len(t.pedidos))
            CASA.repor()

        # ── E O ZERO LEGÍTIMO CONTINUA A SER ZERO ─────────────────────────
        vazio = TransporteFalso(json.dumps({'data': []}))
        objetos, trace = colher('meta.ads.search', vazio, paises=['IT'],
                                page_ids=[PAGE_ID_BASF_IT],
                                janela={'MAX_ITEMS': 5})
        diz(trace.get('RESULT') == 'ZERO_RESULTS' and objetos == [],
            'uma resposta VAZIA é ZERO_RESULTS — e não um erro',
            str(trace.get('RESULT')))
        diz(not fx.degrada_fonte(fx.traduzir('AUTHORIZATION_BLOCK')),
            'e uma recusa de autorização NÃO degrada a fonte')
        CASA.repor()
    finally:
        repor_token(antes)


def p5_page_id_nao_e_source_id():
    print('\nP5 · PAGE_ID != SOURCE_ID\n' + '-' * 72)
    antes = com_token()
    try:
        t = TransporteFalso(json.dumps({'data': [ANUNCIO_FALSO]}))
        objetos, _ = colher('meta.ads.search', t, paises=['IT'],
                            page_ids=[PAGE_ID_BASF_IT], janela={'MAX_ITEMS': 5})
        o = objetos[0] if objetos else {}
        diz(o.get('SOURCE_ID') == 'META-ADS/ads_archive',
            'a origem é a do NÓ que produziu, declarada na receita',
            str(o.get('SOURCE_ID')))
        diz(o.get('SOURCE_ID') != PAGE_ID_BASF_IT,
            'e NÃO é o page_id')
        diz((o.get('RAW') or {}).get('page_id') == PAGE_ID_BASF_IT,
            'o page_id continua preservado no RAW, com o nome que tem',
            str((o.get('RAW') or {}).get('page_id')))
        diz(o.get('DOCUMENT_ID') == 'AD-FALSO-1',
            'e a identidade do item é a que a Meta deu ao anúncio',
            str(o.get('DOCUMENT_ID')))
        # ── E O SEGREDO QUE A META NOS DEVOLVE? ───────────────────────────
        diz(TOKEN_FALSO not in json.dumps(o),
            'o `ad_snapshot_url` da Meta viaja REDIGIDO')
        diz('REDACTED' in json.dumps(o),
            'e a redacção diz-se, em vez de apagar em silêncio')
        diz(rec.EXECUTORES['T9'][-1].get('aceita_fonte') is False,
            'a receita declara que esta rota NÃO aceita fonte — as contas '
            'não têm ficha')
        CASA.repor()
    finally:
        repor_token(antes)


def p6_as_especies_nao_se_somam():
    print('\nP6 · ADVERTISEMENT != POST · BRANDED != POST\n' + '-' * 72)
    antes = com_token()
    try:
        t = TransporteFalso(json.dumps({'data': [ANUNCIO_FALSO]}))
        anuncios, _ = colher('meta.ads.search', t, paises=['IT'],
                             page_ids=[PAGE_ID_BASF_IT], janela={'MAX_ITEMS': 5})
        diz(anuncios and anuncios[0].get('CONTENT_TYPE') == 'ADVERTISEMENT',
            'o anúncio diz-se ADVERTISEMENT',
            str(anuncios[0].get('CONTENT_TYPE') if anuncios else None))
        CASA.repor()

        b = TransporteFalso(json.dumps({'data': [PARCERIA_FALSA]}))
        parcerias, _ = colher('meta.branded_content.search', b,
                              ig_username=IG_BAYER_IT,
                              janela={'SINCE': '2026-01-01', 'UNTIL': '2026-01-31',
                                      'MAX_ITEMS': 5})
        p0 = parcerias[0] if parcerias else {}
        diz(p0.get('CONTENT_TYPE') == 'BRANDED_CONTENT',
            'e a parceria diz-se BRANDED_CONTENT', str(p0.get('CONTENT_TYPE')))
        diz(p0.get('SOURCE_ACCOUNT') == 'criador.falso',
            'quem PUBLICOU é o criador — a marca não se promove a autor',
            str(p0.get('SOURCE_ACCOUNT')))
        diz(IG_BAYER_IT in json.dumps((p0.get('RAW') or {}).get('partners')),
            'e a marca que pagou vive no RAW, em `partners`')
        diz(p0.get('TEXT') is None,
            'sem legenda inventada: a Meta não a devolve neste nó')
        diz(set(am.BRANDED_AUSENTES) <= set(
            (p0.get('RAW') or {}).get('NOT_RETURNED_BY_SOURCE') or []),
            'e o que a fonte NÃO deu fica escrito, para ninguém ler zero')
        CASA.repor()
    finally:
        repor_token(antes)


def p7_o_campo_de_ue_nao_vira_global():
    print('\nP7 · O CAMPO DE UE TEM RÓTULO, E O POLÍTICO NÃO SE PEDE\n' + '-' * 72)
    diz(not (set(am.SO_POLITICO) & set(am.CAMPOS_ANUNCIO + am.CAMPOS_UE)),
        'nenhum campo SÓ-POLÍTICO entra na consulta comercial',
        str(am.SO_POLITICO[:3]))
    url = am._url_ads(paises=['IT'], page_ids=[PAGE_ID_BASF_IT])
    diz(all(('%s' % c) not in url for c in ('spend', 'impressions', 'currency')),
        'e a URL montada não os pede', url.split('fields=')[-1][:44])
    diz('eu_total_reach' in url,
        'o campo de UE é pedido, e com o nome de UE que tem')
    diz(set(am.CAMPOS_UE).isdisjoint(am.CAMPOS_ANUNCIO),
        'e ele vive numa lista PRÓPRIA — um campo de UE que perde o rótulo '
        'vira um campo global que não existe')


def p8_sem_apify():
    print('\nP8 · NENHUMA DESTAS DUAS CONHECE APIFY\n' + '-' * 72)
    fonte_meta = open(os.path.join(RAIZ, 'coleta', 'adaptador_meta.py'),
                      encoding='utf-8').read()
    # ⚠️ A MEDIDA É A DEPENDÊNCIA, NÃO A PALAVRA.
    # O ficheiro DIZ «Apify» duas vezes: numa linha que explica que ele não a
    # conhece, e em `medida['APIFY_RUNS'] = 0`, que é a DECLARAÇÃO de que não
    # correu nenhuma. Contar palavras faria uma declaração honesta parecer uma
    # dependência — e apagá-la para o teste passar seria pior.
    #
    #     DECLARAR ZERO NÃO É DEPENDER. É DIZER QUE NÃO SE DEPENDE.
    import re as _re
    importa = set(_re.findall(r'^import\s+(\w+)', fonte_meta, _re.M))
    diz(not (importa & {'apify_pool', 'coletor', 'scrap_fornecedores'}),
        'o adaptador da Meta não importa provider pago nenhum',
        str(sorted(importa)))
    diz('/acts/' not in fonte_meta and 'api.apify.com' not in fonte_meta,
        'e não conhece endereço de provider nenhum')
    diz(fonte_meta.count("medida['APIFY_RUNS'] = 0") == 2,
        'o que ele diz sobre Apify é ZERO, uma vez por rota',
        '%d declaração(ões)' % fonte_meta.count("medida['APIFY_RUNS'] = 0"))
    antes = com_token()
    try:
        t = TransporteFalso(json.dumps({'data': [ANUNCIO_FALSO]}))
        _, trace = colher('meta.ads.search', t, paises=['IT'],
                          page_ids=[PAGE_ID_BASF_IT], janela={'MAX_ITEMS': 5})
        med = (trace.get('ROUTER_RECORD') or {}).get('MEDIDA') or {}
        diz(med.get('APIFY_RUNS') == 0 and med.get('COST_USD') == 0,
            'e a medida da corrida declara zero provider e zero dólares',
            '%s · %s' % (med.get('APIFY_RUNS'), med.get('COST_USD')))
        diz(med.get('ROUTE_CLASS') == 'OFFICIAL_API_FREE',
            'com a classe de rota que a matriz declara', str(med.get('ROUTE_CLASS')))
        CASA.repor()
    finally:
        repor_token(antes)


if __name__ == '__main__':
    print('=' * 72)
    print('A META OFICIAL AUTENTICA, E PELO CAMINHO DA CASA? — prova offline')
    print('=' * 72)
    presente = bool(os.environ.get(am.TOKEN_ENV, '').strip())
    print('\nO SEGREDO DESTA MÁQUINA\n' + '-' * 72)
    print('  META_GRAPH_TOKEN  = %s' % ('PRESENTE' if presente else 'ABSENT'))
    print('  (esta prova NÃO o procura, não cria conta e não faz login)')
    with CASA:
        try:
            p0_a_cadeia_esta_ligada()
            p1_o_token_chega()
            p2_o_transporte_certo()
            p3_o_caminho_comeca_no_pedido()
            p4_os_erros_tem_nome()
            p5_page_id_nao_e_source_id()
            p6_as_especies_nao_se_somam()
            p7_o_campo_de_ue_nao_vira_global()
            p8_sem_apify()
        finally:
            CASA.repor()

    print('\nA CASA FICOU COMO ESTAVA\n' + '-' * 72)
    sujos = CASA.confere()
    diz(not sujos, 'os livros desta casa voltaram ao que eram',
        ', '.join(sujos) if sujos else '%d caminho(s)' % len(ESCRITOS_PELA_CADEIA))

    print('\nEXECUÇÃO REAL\n' + '-' * 72)
    print('  REAL_META_REQUESTS   = 0  (nenhum pacote saiu para graph.facebook.com)')
    print('  REAL_NETWORK         = 0')
    print('  APIFY_RUNS           = 0')
    print('  PAID_RUNS            = 0')
    print('  REAL_COST_USD        = 0')
    print('  SECRETS_READ         = 0  (o token usado aqui foi INVENTADO)')

    print('\n' + '=' * 72)
    print('PROVAS = %d · FALHAS = %d' % (PROVAS, len(FALHAS)))
    if FALHAS:
        for f in FALHAS:
            print('  !!', f)
        raise SystemExit(1)
    print('META_OFICIAL = PASS')
