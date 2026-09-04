#!/usr/bin/env python3
"""POR QUE A CAMADA DE LEGENDAS NÃO COMPLETOU — instrumento, não coletor.

    python3 scripts/legendas_diagnostico.py            # microconjunto padrão
    python3 scripts/legendas_diagnostico.py 8          # até 8 vídeos

O QUE ISTO NÃO É
-----------------
Não é um segundo Sintonia Scrap. Ele não abre rota nova, não monta requisição
própria e não escreve nada em `data/samples/YOUTUBE-JANELA/`. Cada porta que ele
usa é uma função do DONO CANÔNICO, `scripts/youtube_janela.py`:

    _por_urllib · _bloqueado · _abrir · _json_embutido · _timedtext

Se o dono mudar, isto muda junto — de propósito. Um diagnóstico que mede uma
rota diferente da rota de produção mede outra coisa.

O QUE ELE ACRESCENTA
---------------------
Um estado explícito por vídeo, em vez de "falhou". A camada de produção grava um
veredito (`CAPTION_STATE`); aqui grava-se o CAMINHO até ele, estágio por estágio,
porque a pergunta desta rodada não é "quantos têm legenda" e sim "onde a corrente
arrebenta":

    BROWSER_START · PAGE_OPEN · CAPTION_ROUTE_FOUND · CAPTION_FETCHED
    CAPTION_PARSED · CAPTION_CHARS · CAPTION_CUES · FAILURE_STAGE · FAILURE_REASON

O REGIME, QUE É O ACHADO
-------------------------
A mesma URL, do mesmo IP, no mesmo dia, devolve três coisas diferentes conforme a
reputação da rede:

    VERDE     HTTP 200 · playabilityStatus=OK            · captionTracks presentes
    ÂMBAR     HTTP 200 · playabilityStatus=LOGIN_REQUIRED · captionTracks AUSENTES
    VERMELHO  HTTP 429 · redirect para google.com/sorry   · nada

ÂMBAR é o estado perigoso: a página vem inteira (1,2 MB), passa em `_bloqueado()`,
traz `ytInitialPlayerResponse` — e não traz faixa nenhuma. Quem lê só `faixas == []`
conclui "vídeo sem legenda" sobre um vídeo legendado.

    FAIXA ZERO EM ÂMBAR MEDE A PORTA, NÃO O VÍDEO.

Por isso este instrumento pausa entre pedidos: cada requisição a mais empurra o IP
para VERMELHO, e VERMELHO não mede nada.
"""
import json
import os
import sys
import time
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import youtube_janela as YJ                                          # noqa: E402
from selo_de_amostra import selar                                    # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-HUMAN-SENSORS')
LOTE = os.path.join(DEST, 'PILOTO-YOUTUBE', 'OBJETOS.json')
SAIDA = os.path.join(DEST, 'LEGENDAS-DIAGNOSTICO.json')

# Segundos entre pedidos. Não é educação: é o que separa medir de ser barrado.
PAUSA = float(os.environ.get('LEG_PAUSA') or 25)

NAO_SEI = 'NÃO SEI'

# ── O GABARITO ─────────────────────────────────────────────────────────────────
# Escolhido FORA do classificador, como a missão exige. Os dois primeiros são
# vídeos públicos notórios com faixa de legenda publicada; o gabarito NÃO vem de
# nenhuma medição nossa de relevância agrícola.
CONTROLES = [
    {'VIDEO_ID': 'jNQXAC9IVRw', 'PAPEL': 'CONTROLE_POSITIVO',
     'POR_QUE': 'vídeo público notório com faixas de legenda publicadas',
     'SOURCE_ID': None, 'TITLE': 'Me at the zoo'},
    {'VIDEO_ID': 'aqz-KE-bpKQ', 'PAPEL': 'CONTROLE_POSITIVO',
     'POR_QUE': 'vídeo público notório com faixas de legenda publicadas',
     'SOURCE_ID': None, 'TITLE': 'Big Buck Bunny'},
]


def _do_lote(n):
    """→ os n primeiros objetos do lote do piloto, com o SOURCE_ID que já é deles."""
    if not os.path.exists(LOTE):
        return []
    with open(LOTE, encoding='utf-8') as f:
        d = json.load(f)
    fora = []
    for i in (d.get('ITEMS') or [])[:n]:
        fora.append({'VIDEO_ID': i['VIDEO_ID'], 'PAPEL': 'DO_LOTE',
                     'POR_QUE': 'objeto do lote do piloto, para medir a rota real',
                     'SOURCE_ID': i.get('SOURCE_ID') or i.get('ACCOUNT_HANDLE'),
                     'TITLE': i.get('TITLE')})
    return fora


def _vazio(alvo):
    return {
        'VIDEO_ID': alvo['VIDEO_ID'], 'PAPEL': alvo['PAPEL'],
        'GABARITO_POR_QUE': alvo['POR_QUE'],
        'SOURCE_ID': alvo.get('SOURCE_ID') or NAO_SEI,
        'TITLE': alvo.get('TITLE') or NAO_SEI,
        'BROWSER_START': 'NAO_TENTADO',   # a rota barata não usa navegador
        'PAGE_OPEN': 'NÃO', 'CAPTION_ROUTE_FOUND': 'NÃO',
        'CAPTION_FETCHED': 'NÃO', 'CAPTION_PARSED': 'NÃO',
        'CAPTION_CHARS': 0, 'CAPTION_CUES': 0,
        'CAPTION_LANGUAGE': NAO_SEI, 'CAPTION_TYPE': 'unknown',
        'FIRST_CUE_TIMESTAMP': NAO_SEI, 'LAST_CUE_TIMESTAMP': NAO_SEI,
        'EXCERPT': NAO_SEI, 'COST_USD': 0.0,
        'REGIME': NAO_SEI, 'PLAYABILITY_STATUS': NAO_SEI,
        'FAILURE_STAGE': NAO_SEI, 'FAILURE_REASON': NAO_SEI,
    }


def medir_um(alvo):
    """Uma passada pela corrente inteira, parando no primeiro elo que arrebenta."""
    r = _vazio(alvo)
    url = 'https://www.youtube.com/watch?v=%s' % alvo['VIDEO_ID']

    try:
        html = YJ._por_urllib(url)
    except urllib.error.HTTPError as e:
        r.update({'REGIME': 'VERMELHO', 'FAILURE_STAGE': 'PAGE_OPEN',
                  'FAILURE_REASON': 'HTTP %d — reputação de rede, não do vídeo' % e.code})
        return r
    except Exception as e:                                           # noqa: BLE001
        r.update({'FAILURE_STAGE': 'PAGE_OPEN',
                  'FAILURE_REASON': '%s: %s' % (type(e).__name__, str(e)[:120])})
        return r

    r['PAGE_OPEN'] = 'SIM'
    r['PAGE_BYTES'] = len(html)
    r['BLOQUEADO_PELO_DONO'] = YJ._bloqueado(html)

    pr = YJ._json_embutido(html, 'ytInitialPlayerResponse')
    if not pr:
        r.update({'REGIME': NAO_SEI, 'FAILURE_STAGE': 'CAPTION_ROUTE_FOUND',
                  'FAILURE_REASON': 'a página abriu e não trouxe ytInitialPlayerResponse'})
        return r

    ps = pr.get('playabilityStatus') or {}
    r['PLAYABILITY_STATUS'] = ps.get('status') or NAO_SEI
    r['PLAYABILITY_REASON'] = ps.get('reason') or NAO_SEI
    r['REGIME'] = 'VERDE' if ps.get('status') == 'OK' else 'ÂMBAR'

    faixas = ((pr.get('captions') or {}).get(
        'playerCaptionsTracklistRenderer') or {}).get('captionTracks') or []
    r['CAPTION_TRACKS'] = [{'LANG': t.get('languageCode'),
                            'KIND': t.get('kind', 'MANUAL')} for t in faixas]

    if not faixas:
        if r['REGIME'] == 'ÂMBAR':
            r.update({'FAILURE_STAGE': 'CAPTION_ROUTE_FOUND',
                      'FAILURE_REASON': ('ENVIRONMENT_FAILURE — player negado (%s). '
                                         'Faixa nenhuma foi declarada porque o player '
                                         'não veio; isto NÃO é NO_CAPTION.'
                                         % r['PLAYABILITY_STATUS'])})
        else:
            r.update({'FAILURE_STAGE': 'NENHUM',
                      'FAILURE_REASON': ('NO_CAPTION — o player veio OK e declarou zero '
                                         'faixas. Este vídeo não tem legenda.')})
        return r

    r['CAPTION_ROUTE_FOUND'] = 'SIM'
    faixa = faixas[0]
    r['CAPTION_LANGUAGE'] = faixa.get('languageCode') or NAO_SEI
    r['CAPTION_TYPE'] = 'auto' if faixa.get('kind') == 'asr' else 'manual'

    try:
        trechos = YJ._timedtext(faixa['baseUrl'])
    except Exception as e:                                           # noqa: BLE001
        r.update({'FAILURE_STAGE': 'CAPTION_FETCHED',
                  'FAILURE_REASON': '%s: %s' % (type(e).__name__, str(e)[:120])})
        return r

    r['CAPTION_FETCHED'] = 'SIM'
    if not trechos:
        r.update({'FAILURE_STAGE': 'CAPTION_PARSED',
                  'FAILURE_REASON': ('faixa declarada e corpo vazio — DECLARADA_MAS_VAZIA, '
                                     'que é confissão, não ausência')})
        return r

    texto = ' '.join(t['TEXTO'] for t in trechos)
    r.update({'CAPTION_PARSED': 'SIM', 'CAPTION_CUES': len(trechos),
              'CAPTION_CHARS': len(texto),
              'FIRST_CUE_TIMESTAMP': trechos[0].get('T_MS'),
              'LAST_CUE_TIMESTAMP': trechos[-1].get('T_MS'),
              'EXCERPT': texto[:220],
              'FAILURE_STAGE': 'NENHUM', 'FAILURE_REASON': 'NENHUM'})
    return r


def main(limite=None):
    alvos = CONTROLES + _do_lote(2)
    if limite:
        alvos = alvos[:int(limite)]
    linhas = []
    for i, a in enumerate(alvos):
        if i:
            time.sleep(PAUSA)
        r = medir_um(a)
        linhas.append(r)
        print('%-13s %-18s %-9s %-16s cues=%-5d chars=%-6d %s' % (
            r['VIDEO_ID'], r['PAPEL'], r['REGIME'], r['PLAYABILITY_STATUS'],
            r['CAPTION_CUES'], r['CAPTION_CHARS'], r['FAILURE_STAGE']))

    corpo = selar({
        'SOURCE_ID': 'IT-HUMAN-SENSORS/LEGENDAS-DIAGNOSTICO',
        'source': ('rota gratuita do dono canônico scripts/youtube_janela.py '
                   '(_por_urllib → ytInitialPlayerResponse → _timedtext)'),
        'DONO_CANONICO': 'scripts/youtube_janela.py',
        'NOVO_SCRAPER': 'NÃO — este arquivo só chama funções do dono',
        'APIFY_USADO': 'NÃO', 'WHISPER_USADO': 'NÃO', 'API_PAGA_USADA': 'NÃO',
        'COST_USD_TOTAL': 0.0,
        'PAUSA_ENTRE_PEDIDOS_S': PAUSA,
        'TRES_REGIMES': ('VERDE = 200 e playabilityStatus OK, faixas presentes. '
                         'ÂMBAR = 200 e LOGIN_REQUIRED, faixas ausentes porque o player '
                         'foi negado — ENVIRONMENT_FAILURE, nunca NO_CAPTION. '
                         'VERMELHO = 429 com redirect para google.com/sorry.'),
        'ITEMS': linhas})
    os.makedirs(DEST, exist_ok=True)
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('gravado: data/samples/IT-HUMAN-SENSORS/LEGENDAS-DIAGNOSTICO.json · %d vídeos'
          % len(linhas))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else None))
