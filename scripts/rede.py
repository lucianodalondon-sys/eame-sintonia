#!/usr/bin/env python3
"""
PORTÃO DE REDE — a coleta é executável neste ambiente?

Por que existe: a MISSÃO 11 foi bloqueada por política de egresso, e a 11R mediu o mesmo
bloqueio de novo. Sem este portão a próxima conta gasta metade da sessão descobrindo com
`curl` solto o que uma linha responde — e corre o risco de ler recusa de gateway como
ausência de fonte.

    python3 scripts/rede.py
    python3 scripts/rede.py --json

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


if __name__ == '__main__':
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
