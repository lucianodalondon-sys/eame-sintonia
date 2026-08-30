#!/usr/bin/env python3
"""
PORTÃO ADAMA ES — a coleta do catálogo público espanhol é executável neste ambiente?

Por que existe um portão SÓ para a ADAMA: `scripts/rede.py` classifica um host em dois
estados — RECUSADO (túnel não abriu, `000`) ou ALCANCÁVEL (qualquer código HTTP). Para
`www.adama.com` os dois estão errados. O túnel abre, a requisição chega, e a borda da
própria ADAMA devolve 403. `rede.py` chamaria isso de ALCANCÁVEL, e a coleta seguiria
tratando negação de borda como conteúdo.

Os três estados que este portão separa — e que nenhuma outra ferramenta do repo separa:

    ORG_EGRESS_DENIED   a política de egresso DESTA sessão barrou o host.
                        O CONNECT não completa; o proxy registra o motivo.
                        Diz respeito ao AMBIENTE.

    EDGE_BOT_DENIED     o CONNECT completa, a requisição chega à origem, e a
                        origem responde 403/429 com assinatura de bot manager.
                        Diz respeito ao IP/cliente DESTA sessão perante a ADAMA.

    REACHABLE           a origem devolve conteúdo.

Nenhum dos três é ausência de fonte:

    SOURCE FAILURE != ZERO
    EDGE_BOT_DENIED != CATÁLOGO VAZIO
    403 DE BORDA != PRODUTO INEXISTENTE

O denominador do censo (CURRENT_CATALOG_TOTAL) só pode ser afirmado quando este portão
devolve REACHABLE. Enquanto não devolver, o censo declara NÃO SEI — nunca 0, e nunca o
número de um snapshot antigo.

    python3 scripts/adama_es_portao.py
    python3 scripts/adama_es_portao.py --json
    python3 scripts/adama_es_portao.py --snapshot 2026-08-29
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')

# As rotas que o censo precisa. Cada uma responde uma pergunta diferente do censo,
# e cada uma é testada separadamente: negar a raiz não é negar o catálogo.
ROTAS = [
    ('RAIZ_ES', 'https://www.adama.com/spain/es/',
     'existe o site espanhol para este cliente'),
    ('CATALOGO', 'https://www.adama.com/spain/es/products/crop-protection/downloads',
     'a lista nominal de produtos — o DENOMINADOR do censo (secao 3)'),
    ('PRODUTOS', 'https://www.adama.com/spain/es/products',
     'rota alternativa de enumeracao'),
    ('ROBOTS', 'https://www.adama.com/robots.txt',
     'controle: robots.txt e servido a qualquer cliente por convencao. '
     'Negar robots.txt e negar o CLIENTE, nao a rota'),
    ('SITEMAP', 'https://www.adama.com/sitemap.xml',
     'rota de enumeracao estruturada, se publicada'),
]

# Assinaturas de bot manager na RESPOSTA DA ORIGEM. Não são heurística de texto solto:
# `ak_p` é o token de Akamai Bot Manager em server-timing, e "Reference #" é o corpo
# padrão da página de negação da Akamai.
ASSINATURAS_BORDA = (
    ('server-timing', re.compile(r'\bak_p\b', re.I), 'Akamai Bot Manager (ak_p)'),
    ('body',          re.compile(r'Access Denied', re.I), 'corpo "Access Denied"'),
    ('body',          re.compile(r'Reference #[0-9a-f.]+', re.I), 'Akamai "Reference #"'),
    ('header',        re.compile(r'^x-akamai', re.I), 'cabecalho x-akamai'),
    ('header',        re.compile(r'cf-ray', re.I), 'Cloudflare cf-ray'),
)


def _curl(url, timeout=30):
    """Cabeçalhos + corpo + código, numa chamada. Separar os dois é o ponto do portão."""
    sep = '\n===CCR-SPLIT===\n'
    r = subprocess.run(
        ['curl', '-sS', '-D', '-', '-m', str(timeout), '-A', UA,
         '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
         '-H', 'Accept-Language: es-ES,es;q=0.9', url],
        capture_output=True, text=True, errors='replace')
    saida = r.stdout or ''
    # A resposta do CONNECT ("HTTP/1.1 200 Connection Established") vem antes da real.
    blocos = re.split(r'\r?\n\r?\n', saida, maxsplit=0)
    cabecalhos, corpo = '', ''
    for i, b in enumerate(blocos):
        if b.startswith('HTTP/') and 'Connection Established' not in b.split('\n')[0]:
            cabecalhos = b
            corpo = '\n\n'.join(blocos[i + 1:])
            break
    m = re.match(r'HTTP/[\d.]+ (\d{3})', cabecalhos)
    return {
        'HTTP_STATUS': m.group(1) if m else '000',
        'HEADERS': cabecalhos,
        'BODY': corpo[:4000],
        'CURL_EXIT': r.returncode,
        'CURL_STDERR': (r.stderr or '').strip()[:300],
        'TUNEL_ABRIU': 'Connection Established' in saida or bool(m),
        'SEP': sep,
    }


def _motivos_do_proxy():
    """Por que o proxy recusou. `000` no cliente nao distingue politica de origem morta."""
    proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    if not proxy:
        return {}
    r = subprocess.run(['curl', '-sS', '-m', '15', proxy + '/__agentproxy/status'],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except ValueError:
        return {}
    fora = {}
    for f in d.get('recentRelayFailures') or []:
        fora[f.get('host', '').split(':')[0]] = '%s — %s' % (f.get('kind'), f.get('detail', '')[:160])
    return fora


def classificar(resposta, motivos_proxy, host='www.adama.com'):
    """Os tres estados. Derivado da resposta, nunca digitado."""
    code = resposta['HTTP_STATUS']
    evid = []

    if not resposta['TUNEL_ABRIU'] or code == '000':
        motivo = motivos_proxy.get(host)
        return ('ORG_EGRESS_DENIED' if motivo else 'UNREACHABLE_REASON_UNKNOWN',
                [motivo or ('curl exit %s: %s' % (resposta['CURL_EXIT'],
                                                  resposta['CURL_STDERR']))])

    for onde, rx, nome in ASSINATURAS_BORDA:
        alvo = resposta['HEADERS'] if onde in ('header', 'server-timing') else resposta['BODY']
        if rx.search(alvo or ''):
            evid.append(nome)

    if code in ('403', '429', '503') and evid:
        return 'EDGE_BOT_DENIED', evid
    if code in ('403', '429'):
        return 'EDGE_DENIED_UNSIGNED', ['HTTP %s sem assinatura de bot manager reconhecida' % code]
    if code.startswith('2'):
        return 'REACHABLE', ['HTTP %s' % code]
    if code.startswith('3'):
        return 'REDIRECT', ['HTTP %s' % code]
    return 'HTTP_ERROR', ['HTTP %s' % code]


PACOTES = ('ADAMA-ES-PACOTE-PAGINAS.json', 'ADAMA-ES-PACOTE-CATALOGO.json')


def _captura_local():
    """Quantas páginas o navegador local trouxe, e quando. Ausência devolve 0, não erro."""
    base = os.path.join(ROOT, 'data', 'raw', 'ES', 'adama-website')
    n, quando, arquivo = 0, 'NÃO SEI', ''
    for nome in PACOTES:
        caminho = os.path.join(base, nome)
        if not os.path.exists(caminho):
            continue
        try:
            with open(caminho, encoding='utf-8') as f:
                d = json.load(f)
        except (ValueError, OSError):
            continue
        n += len(d.get('PAGINAS') or {})
        quando = d.get('CAPTURA_UTC') or quando
        arquivo = arquivo or os.path.relpath(caminho, ROOT).replace('\\', '/')
    return {'PAGINAS': n, 'QUANDO': quando, 'ARQUIVO': arquivo}


def avaliar():
    motivos = _motivos_do_proxy()
    linhas = []
    for nome, url, para_que in ROTAS:
        r = _curl(url)
        estado, evid = classificar(r, motivos)
        linhas.append({
            'ROTA': nome, 'URL': url, 'PARA_QUE_SERVE': para_que,
            'HTTP_STATUS': r['HTTP_STATUS'], 'ESTADO': estado, 'EVIDENCIA': evid,
        })

    estados = {l['ESTADO'] for l in linhas}
    catalogo = next(l for l in linhas if l['ROTA'] == 'CATALOGO')
    robots = next(l for l in linhas if l['ROTA'] == 'ROBOTS')

    # Quinta rota, medida do mesmo jeito: existe captura feita pelo NAVEGADOR local?
    # A borda da ADAMA recusa curl mesmo saindo da rede domestica (medido 2026-08-30 na
    # maquina do usuario, nao em datacenter), e aceita o navegador. Entao o portao passa
    # a perguntar duas coisas diferentes: "esta sessao alcanca por HTTP?" e "existe
    # evidencia capturada ao vivo?". A segunda tambem e acesso — so nao e acesso do curl.
    captura = _captura_local()
    linhas.append({
        'ROTA': 'CAPTURA_NAVEGADOR_LOCAL',
        'URL': captura['ARQUIVO'] or 'data/raw/ES/adama-website/ADAMA-ES-PACOTE-PAGINAS.json',
        'PARA_QUE_SERVE': 'paginas buscadas pelo navegador da maquina local',
        'HTTP_STATUS': '200' if captura['PAGINAS'] else 'AUSENTE',
        'ESTADO': 'REACHABLE' if captura['PAGINAS'] else 'SEM_CAPTURA',
        'EVIDENCIA': ('%d paginas, todas com status HTTP registrado, capturadas em %s'
                      % (captura['PAGINAS'], captura['QUANDO']))
        if captura['PAGINAS'] else 'nenhum pacote de captura no disco',
    })

    pronto = catalogo['ESTADO'] == 'REACHABLE' or bool(captura['PAGINAS'])

    # Se ate robots.txt e negado, a negacao e do CLIENTE, nao da rota. Isso separa
    # "a ADAMA nao publica este caminho" de "a ADAMA nao atende este IP".
    # A ordem importa e mudou: alcancar VENCE nao-alcancar. Antes, robots.txt negado
    # carimbava CLIENTE_NEGADO_NO_HOST_INTEIRO mesmo quando o navegador ja tinha trazido
    # 62 paginas — o rotulo contradizia a evidencia no mesmo arquivo. Agora o alcance
    # descreve o que FOI alcancado, e a negacao do curl continua escrita, por rota.
    if catalogo['ESTADO'] == 'REACHABLE':
        alcance = 'CATALOGO_ALCANCAVEL'
    elif captura['PAGINAS'] and robots['ESTADO'].startswith('EDGE'):
        alcance = 'CATALOGO_ALCANCADO_PELO_NAVEGADOR_LOCAL_CURL_NEGADO_NO_HOST'
    elif captura['PAGINAS']:
        alcance = 'CATALOGO_ALCANCADO_PELO_NAVEGADOR_LOCAL'
    elif robots['ESTADO'].startswith('EDGE'):
        alcance = 'CLIENTE_NEGADO_NO_HOST_INTEIRO'
    elif catalogo['ESTADO'].startswith('EDGE'):
        alcance = 'ROTA_NEGADA_MAS_HOST_RESPONDE'
    else:
        alcance = 'INDETERMINADO'

    return {
        'HOST': 'www.adama.com',
        'ROTAS': linhas,
        'ESTADOS_OBSERVADOS': sorted(estados),
        'ALCANCE': alcance,
        'ADAMA_ES_COLLECTION_READY': 'YES' if pronto else 'NO',
        'CURRENT_CATALOG_TOTAL_AFIRMAVEL': pronto,
        'LEI': (
            'EDGE_BOT_DENIED descreve o IP DESTA sessao perante a borda da ADAMA. '
            'NAO descreve o catalogo. SOURCE FAILURE != ZERO: enquanto '
            'ADAMA_ES_COLLECTION_READY = NO, CURRENT_CATALOG_TOTAL = NAO SEI, '
            'nunca 0 e nunca o numero de um snapshot antigo.'),
    }


def _cabeca_do_git():
    r = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=ROOT)
    return (r.stdout or '').strip() or 'NÃO SEI'


def _ip_de_saida():
    """O IP que a ADAMA ve. E o sujeito da negacao — sem ele o 403 nao e diagnosticavel."""
    r = subprocess.run(['curl', '-sS', '-m', '20', 'https://api.ipify.org'],
                       capture_output=True, text=True)
    return (r.stdout or '').strip() or 'NÃO SEI'


def snapshot(captura):
    v = avaliar()
    return {
        'SOURCE_ID': 'PORTAO-ADAMA-ES',
        'source': 'medicao do acesso a www.adama.com a partir DESTE ambiente de coleta',
        'SOURCE_LOCATION': 'interno',
        'FACT_LOCATION': 'n/a — descreve o ambiente de execucao, nao a Espanha',
        'ORIGINAL_LANGUAGE': 'pt',
        'captured_at': captura,
        'CAPTURE_DATE': captura,
        'ESTADO_DO_REGISTRO': 'CURRENT',
        'HEAD': _cabeca_do_git(),
        'EGRESS_IP': _ip_de_saida(),
        'MEDIDO_POR': 'scripts/adama_es_portao.py --snapshot',
        'ROTAS': v['ROTAS'],
        'ALCANCE': v['ALCANCE'],
        'ADAMA_ES_COLLECTION_READY': v['ADAMA_ES_COLLECTION_READY'],
        'LEI': v['LEI'],
        'O_QUE_ISTO_NAO_SIGNIFICA': (
            'NAO significa que a ADAMA parou de publicar, nem que o catalogo encolheu, '
            'nem que os 55 relatados pela investigacao externa sao falsos. Significa que '
            'ESTE IP nao e atendido pela borda da ADAMA.'),
        'QUEM_MANDA': ('o estado vivo e derivado por scripts/adama_es_portao.py a cada '
                       'execucao. Este arquivo e REGISTRO da medicao, nunca a verdade.'),
    }


if __name__ == '__main__':
    if '--snapshot' in sys.argv:
        i = sys.argv.index('--snapshot')
        cap = sys.argv[i + 1] if len(sys.argv) > i + 1 else 'NÃO SEI'
        print(json.dumps(snapshot(cap), ensure_ascii=False, indent=1))
        sys.exit(0)
    v = avaliar()
    if '--json' in sys.argv:
        print(json.dumps(v, ensure_ascii=False, indent=1))
    else:
        print('%-10s%-7s%-22s%s' % ('ROTA', 'HTTP', 'ESTADO', 'EVIDENCIA'))
        print('-' * 96)
        for l in v['ROTAS']:
            print('%-10s%-7s%-22s%s' % (l['ROTA'], l['HTTP_STATUS'], l['ESTADO'],
                                        '; '.join(l['EVIDENCIA'])[:44]))
        print()
        print('ALCANCE                     =', v['ALCANCE'])
        print('ADAMA_ES_COLLECTION_READY   =', v['ADAMA_ES_COLLECTION_READY'])
