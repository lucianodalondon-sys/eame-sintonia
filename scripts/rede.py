#!/usr/bin/env python3
"""
PORTÃO DE REDE — a coleta é executável neste ambiente?

Por que existe: a MISSÃO 11 foi bloqueada por política de egresso, e a 11R mediu o mesmo
bloqueio de novo. Sem este portão a próxima conta gasta metade da sessão descobrindo com
`curl` solto o que uma linha responde — e corre o risco de ler recusa de gateway como
ausência de fonte.

    python3 scripts/rede.py
    python3 scripts/rede.py --json
    python3 scripts/rede.py --snapshot 2026-08-29   # registro CURRENT, derivado

`NETWORK_COLLECTION_READY = NO` **não diz nada sobre as fontes**. Diz que este ambiente
não deixa alcançá-las. `SOURCE FAILURE ≠ ZERO`, e recusa de gateway ≠ fonte morta.
"""
import json
import os
import subprocess
import sys

# Host -> (URL de teste barata, para que serve na coleta espanhola)
HOSTS = [
    ('api.openalex.org', 'https://api.openalex.org/works?per-page=1',
     'ciência e pesquisadores (ES-T5-002) — rota gratuita, sem chave'),
    ('pub.orcid.org', 'https://pub.orcid.org/v3.0/0000-0002-1153-2809/person',
     'identidade que atravessa camadas; fecha FRAGMENTAÇÃO e é o que falta em SCIENCE→VOICE'),
    ('api.ror.org', 'https://api.ror.org/organizations?query=cordoba',
     'localização declarada de instituição — é o que fecha o confundidor de Córdoba'),
    ('www.youtube.com', 'https://www.youtube.com',
     'camada de vídeo (ES-T8-001) — VIDEO FIRST depende disto'),
    ('api.apify.com', 'https://api.apify.com/v2/acts',
     'rota paga de vídeo, transcrição e LinkedIn'),
    ('api.crossref.org', 'https://api.crossref.org/works?rows=1',
     'complemento bibliográfico'),
    ('www.mapa.gob.es', 'https://www.mapa.gob.es',
     'registro espanhol e denominações (ES-T4-00x)'),
]

# Sem estes quatro não existe coleta profunda: ciência, identidade, vídeo e rota paga.
ESSENCIAIS = ('api.openalex.org', 'pub.orcid.org', 'www.youtube.com', 'api.apify.com')


def testar(url, timeout=20):
    """Devolve o código HTTP, ou '000' quando o túnel nem se abriu."""
    r = subprocess.run(
        ['curl', '-sS', '-o', os.devnull, '-w', '%{http_code}', '-m', str(timeout), url],
        capture_output=True, text=True)
    return (r.stdout or '000').strip() or '000'


def motivos_do_proxy():
    """O proxy registra POR QUE recusou. 000 no cliente não distingue os motivos."""
    proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    if not proxy:
        return {}
    r = subprocess.run(['curl', '-sS', '-m', '15', proxy + '/__agentproxy/status'],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except ValueError:
        return {}
    return {f['host'].split(':')[0]: f.get('detail', '') for f in d.get('recentRelayFailures', [])}


def avaliar():
    linhas = []
    for host, url, para_que in HOSTS:
        code = testar(url)
        linhas.append({'HOST': host, 'HTTP_STATUS': code,
                       'RESULT': 'RECUSADO' if code == '000' else 'ALCANCAVEL',
                       'PARA_QUE_SERVE': para_que})
    motivos = motivos_do_proxy()
    for l in linhas:
        if l['RESULT'] == 'RECUSADO':
            l['MOTIVO_DO_GATEWAY'] = motivos.get(l['HOST'], 'NÃO SEI — o proxy não registrou')
    recusados = [l['HOST'] for l in linhas if l['RESULT'] == 'RECUSADO']
    faltando = [h for h in ESSENCIAIS if h in recusados]
    return {
        'HOSTS': linhas,
        'RECUSADOS': recusados,
        'ESSENCIAIS_RECUSADOS': faltando,
        'NETWORK_COLLECTION_READY': 'NO' if faltando else 'YES',
        'LEI': ('recusa de gateway NÃO é ausência de fonte. NETWORK_COLLECTION_READY = NO '
                'descreve ESTE ambiente, nunca a fonte.'),
    }



def cabeca_do_git():
    """O HEAD em que esta medicao foi feita. Sem isso o snapshot nao e rastreavel."""
    r = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True,
                       cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return (r.stdout or '').strip() or 'NÃO SEI'


def estado_do_proxy():
    """PROXY_STATE: o que o proxy diz de si. Distingue politica de egresso de fonte morta."""
    proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    if not proxy:
        return {'PROXY_CONFIGURADO': False}
    r = subprocess.run(['curl', '-sS', '-m', '15', proxy + '/__agentproxy/status'],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except ValueError:
        return {'PROXY_CONFIGURADO': True, 'STATUS_LEGIVEL': False}
    return {
        'PROXY_CONFIGURADO': True,
        'STATUS_LEGIVEL': True,
        'ENABLED': d.get('enabled'),
        'SELECTIVE': d.get('selective'),
        'RECENT_RELAY_FAILURES': len(d.get('recentRelayFailures') or []),
    }


def snapshot(captura):
    """Registro CURRENT desta medicao. Derivado de avaliar() — nenhum veredito digitado.

    `captura` e a data, passada de fora: o script nao inventa a propria data.
    """
    v = avaliar()
    return {
        'SOURCE_ID': 'PORTAO-DE-REDE-ES-CURRENT',
        'source': 'medicao do ambiente de coleta corrente — nao das fontes',
        'SOURCE_LOCATION': 'interno',
        'FACT_LOCATION': 'n/a — descreve o ambiente de execucao',
        'ORIGINAL_LANGUAGE': 'pt',
        'ESTADO_DO_REGISTRO': 'CURRENT',
        'AMBIENTE': 'CURRENT_COLLECTION_ENVIRONMENT',
        'CAPTURE_DATE': captura,
        'HEAD': cabeca_do_git(),
        'MEDIDO_POR': 'scripts/rede.py --snapshot',
        'PROXY_STATE': estado_do_proxy(),
        'HOSTS': v['HOSTS'],
        'STATUS': 'READY' if v['NETWORK_COLLECTION_READY'] == 'YES' else 'BLOCKED',
        'ESSENCIAIS_RECUSADOS': v['ESSENCIAIS_RECUSADOS'],
        'NETWORK_COLLECTION_READY': v['NETWORK_COLLECTION_READY'],
        'LEI': v['LEI'],
        'O_QUE_ISTO_NAO_SIGNIFICA': (
            'NAO significa que as fontes estao saudaveis, nem que a coleta vai dar certo. '
            'READY descreve o AMBIENTE: o tunel abre e a requisicao chega. '
            'SOURCE FAILURE != ZERO continua valendo na direcao contraria.'),
        'QUEM_MANDA': ('o estado vivo e derivado por scripts/rede.py a cada execucao. '
                       'Este arquivo e REGISTRO da medicao, nunca a fonte da verdade.'),
    }


if __name__ == '__main__':
    if '--snapshot' in sys.argv:
        i = sys.argv.index('--snapshot')
        captura = sys.argv[i + 1] if len(sys.argv) > i + 1 else 'NÃO SEI'
        print(json.dumps(snapshot(captura), ensure_ascii=False, indent=1))
        sys.exit(0)
    v = avaliar()
    if '--json' in sys.argv:
        print(json.dumps(v, ensure_ascii=False, indent=1))
    else:
        print('%-22s%-8s%-12s%s' % ('HOST', 'STATUS', 'RESULTADO', 'PARA QUE SERVE'))
        print('-' * 108)
        for l in v['HOSTS']:
            print('%-22s%-8s%-12s%s' % (l['HOST'], l['HTTP_STATUS'], l['RESULT'],
                                        l['PARA_QUE_SERVE'][:58]))
        print()
        if v['ESSENCIAIS_RECUSADOS']:
            print('essenciais recusados:', ', '.join(v['ESSENCIAIS_RECUSADOS']))
        print('NETWORK_COLLECTION_READY =', v['NETWORK_COLLECTION_READY'])
