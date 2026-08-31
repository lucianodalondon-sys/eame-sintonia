#!/usr/bin/env python3
"""
QUAL PORTA ABRE — perguntado as tres, e registrado o que cada uma respondeu.

A missao manda testar PRIMEIRO a rota oficial. Testar e medir, nao supor. As
tres portas foram batidas em 30/08/2026 com a mesma pergunta (anuncios na
Espanha) e responderam coisas diferentes.

    META_ADS_LIBRARY_API_ACCESS   graph.facebook.com/vXX/ads_archive
    META_ADS_LIBRARY_UI_ACCESS    www.facebook.com/ads/library (sem login)
    EU_COMMERCIAL_AD_ACCESS       os anuncios comerciais da UE aparecem?

O QUE ESTE ARQUIVO DECIDE
--------------------------
Decide qual rota esta ABERTA hoje, com prova: codigo HTTP, tamanho da resposta
e o corpo do erro quando ha erro. Nada aqui e conclusao sobre a Meta em geral;
e a medida desta maquina, nesta data, sem crachá.

O QUE ELE NAO DECIDE
---------------------
Nao decide que a API "nao existe" nem que "esta quebrada". A API pede um token
de aplicativo do Facebook. Nao ter token e um estado NOSSO, e o nome disso e
`API_TOKEN_AUSENTE` — nao `API_INDISPONIVEL`. Se o cliente entregar um token
amanha, esta mesma funcao passa a dizer outra coisa sem trocar uma linha.

    SEM_CRACHA != PORTA_FECHADA

E nao se resolve isso pegando a conta do usuario: a missao proibe, e com razao.
Token de aplicativo e coisa que o dono da marca emite, nao que o coletor pega.
"""
import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import meta_navegador as nav  # noqa: E402

DEST = os.path.join(ROOT, 'data', 'samples', 'META-EAME', 'META-ROUTE-PROBE-V1.json')

API_ABERTA = 'API_ABERTA'
API_TOKEN_AUSENTE = 'API_TOKEN_AUSENTE'
API_ERRO_OUTRO = 'API_ERRO_OUTRO'
UI_ABERTA_SEM_LOGIN = 'UI_ABERTA_SEM_LOGIN'
UI_BLOQUEADA = 'UI_BLOQUEADA'

PAISES = ['ES', 'IT', 'FR']
VERSOES_API = ['v23.0', 'v21.0']


def _agora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def _curl(url, ua=None):
    cmd = ['curl', '-s', '-o', '-', '-w', '\n@@%{http_code}@@%{size_download}']
    if ua:
        cmd += ['-A', ua]
    cmd += [url]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=60,
                           encoding='utf-8', errors='replace')
    except Exception as e:
        return {'erro': str(e)[:200]}
    saida = p.stdout or ''
    corpo, _, cauda = saida.rpartition('\n@@')
    codigo, _, tam = cauda.partition('@@')
    return {'http': codigo.strip() or None, 'bytes': tam.strip() or None,
            'corpo': corpo.strip()[:400]}


def porta_api(token=None):
    """A rota oficial. Sem token, a Meta responde OAuthException code 1."""
    medidas = []
    for v in VERSOES_API:
        url = ('https://graph.facebook.com/%s/ads_archive'
               '?ad_type=ALL&ad_reached_countries=%%5B%%22ES%%22%%5D'
               '&search_terms=fungicida&limit=5' % v)
        if token:
            url += '&access_token=' + token
        r = _curl(url)
        r['versao'] = v
        r['com_token'] = bool(token)
        medidas.append(r)
    corpos = ' '.join((m.get('corpo') or '') for m in medidas)
    if any(m.get('http') == '200' for m in medidas):
        estado = API_ABERTA
    elif 'OAuthException' in corpos or 'access token' in corpos.lower():
        estado = API_TOKEN_AUSENTE
    else:
        estado = API_ERRO_OUTRO
    return {'estado': estado, 'medidas': medidas,
            'nota': ('A API pede token de aplicativo do Facebook. Este repositorio '
                     'nao tem nenhum, e a missao proibe usar a conta do usuario. '
                     'Isto e ausencia de cracha, nao porta fechada.')}


def porta_ui_curl():
    """A mesma pagina publica, pedida sem janela grafica."""
    ua = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
          '(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36')
    url = nav.url_biblioteca(active_status='active', ad_type='all', country='ES',
                             q='fungicida', media_type='all')
    r = _curl(url, ua=ua)
    r['url'] = url
    r['estado'] = UI_ABERTA_SEM_LOGIN if r.get('http') == '200' else UI_BLOQUEADA
    return r


def porta_ui_janela(paises=PAISES):
    """A mesma pagina, no Chrome com janela. Uma medida por pais do piloto."""
    estado, versao = nav.navegador_vivo()
    if estado != nav.PORTA_ABERTA:
        return {'estado': estado, 'navegador': versao,
                'nota': 'Chrome com janela nao esta escutando na porta %d.' % nav.PORTA}
    medidas = []
    for pais in paises:
        url = nav.url_biblioteca(active_status='active', ad_type='all',
                                 country=pais, q='fungicida', media_type='all')
        alvo = nav.abrir(url, espera=14)
        try:
            cab = nav.cabecalho(alvo)
            cart = nav.cartoes(alvo)
            medidas.append({
                'country': pais, 'url_pedida': url,
                'url_final': cab.get('url'), 'titulo': cab.get('titulo'),
                'bytes': cab.get('bytes'),
                'resultados_declarados': cab.get('resultados_declarados'),
                'sessao': cab.get('logado'),
                'cartoes_lidos_sem_rolar': cart.get('total'),
            })
        finally:
            nav.fechar(alvo)
    ok = [m for m in medidas if (m.get('cartoes_lidos_sem_rolar') or 0) > 0]
    return {'estado': UI_ABERTA_SEM_LOGIN if ok else UI_BLOQUEADA,
            'navegador': versao, 'medidas': medidas}


def medir(token=None):
    api = porta_api(token)
    curl = porta_ui_curl()
    janela = porta_ui_janela()
    if api['estado'] == API_ABERTA:
        escolhida = 'META_ADS_LIBRARY_API'
    elif janela['estado'] == UI_ABERTA_SEM_LOGIN:
        escolhida = 'META_ADS_LIBRARY_UI_CHROME_COM_JANELA'
    elif curl['estado'] == UI_ABERTA_SEM_LOGIN:
        escolhida = 'META_ADS_LIBRARY_UI_HTTP'
    else:
        escolhida = 'NENHUMA_ABERTA'
    return {
        'dataset_owner': 'META_COMPETITOR_EAME',
        'as_of_date': _agora(),
        'countries': PAISES,
        'api_auth_state': api['estado'],
        'meta_ads_library_api_access': api,
        'meta_ads_library_ui_access_http': curl,
        'meta_ads_library_ui_access_janela': janela,
        'eu_commercial_ad_access': (
            'PROVED' if (janela.get('medidas') and
                         any((m.get('cartoes_lidos_sem_rolar') or 0) > 0
                             for m in janela['medidas'])) else 'NOT_PROVED'),
        'meta_route': escolhida,
        'limitacoes': [
            'Sem token de aplicativo, a rota oficial nao pode ser exercida. '
            'A missao proibe usar a conta do usuario para obter um.',
            'A leitura por janela le o que a pagina publica MOSTRA. Se a Meta '
            'esconder um campo da UI, ele nao existe nesta coleta — e ausencia '
            'de campo na fonte, nao ausencia no mundo.',
            'Rolagem infinita: a contagem so e completa quando a lista para de '
            'crescer. A completude e medida contra o numero que a propria fonte '
            'declara. Ver COMPLETE_MATCHES_SOURCE_COUNT / SHORT_OF_SOURCE_COUNT.',
        ],
    }


def main():
    token = os.environ.get('META_ADS_LIBRARY_TOKEN') or None
    r = medir(token)
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: r[k] for k in
                      ('meta_route', 'api_auth_state', 'eu_commercial_ad_access')},
                     ensure_ascii=False, indent=2))
    print('-> ' + os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
