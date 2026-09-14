#!/usr/bin/env python3
"""
PORTÃO DE REDE — a coleta é executável neste ambiente?

Por que existe: a MISSÃO 11 foi bloqueada por política de egresso, e a 11R mediu o mesmo
bloqueio de novo. Sem este portão a próxima conta gasta metade da sessão descobrindo com
`curl` solto o que uma linha responde — e corre o risco de ler recusa de gateway como
ausência de fonte.

    python3 superficie/rede.py
    python3 superficie/rede.py --json
    python3 superficie/rede.py --snapshot 2026-08-29   # registro CURRENT, derivado

`NETWORK_COLLECTION_READY = NO` **não diz nada sobre as fontes**. Diz que este ambiente
não deixa alcançá-las. `SOURCE FAILURE ≠ ZERO`, e recusa de gateway ≠ fonte morta.

⚠️ E DESDE `C-SALA-PERSISTENTE-E-PREFLIGHT-REAL-V1` ELE RESPONDE A SEGUNDA
PERGUNTA DO AMBIENTE: **por que país é que esta máquina sai?**

    python3 superficie/rede.py --egresso
    python3 superficie/rede.py --portao-de-egresso IT

POR QUE AQUI, E NÃO NUM FICHEIRO NOVO
--------------------------------------
O `C-ITALIA-FIRST-REAL-COLLECTION-CANARY-V1` mediu que o único medidor de
egresso desta casa vivia DENTRO de `coleta/instagram_janela.py` — ou seja,
dentro de uma rota de aquisição. Exigir `EGRESS_COUNTRY_CODE = IT` *antes* de
adquirir era, por construção, impossível.

    UM PREFLIGHT QUE SÓ CORRE DEPOIS DE COMEÇAR NÃO É UM PREFLIGHT.

O egresso é propriedade do AMBIENTE DE EXECUÇÃO, não da fonte. E o dono do
ambiente já existia: é este ficheiro, que desde o primeiro dia responde «a
coleta é executável neste ambiente?». Criar um `egress_check.py` ao lado seria
um segundo dono da mesma pergunta.

⚠️ O QUE O EGRESSO **NÃO** É
-----------------------------
```
VPN_LOCATION  !=  SOURCE_LOCATION
VPN_LOCATION  !=  FACT_LOCATION
```
Saber que a máquina sai por Itália **não** diz de onde é a fonte nem onde o
facto aconteceu. É propriedade de rede da execução, e mais nada. Quem usar isto
para preencher geografia de dado está a fabricar procedência.
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


# ═════════════════════════════════════════════════════════════════════════
# O EGRESSO — por que país sai esta máquina, e o portão que isso alimenta
# ═════════════════════════════════════════════════════════════════════════

# O serviço é o MESMO que `coleta/instagram_janela.py` já usava: público, sem
# credencial, sem custo. Trazê-lo para aqui não é adotar um fornecedor novo — é
# tirar de dentro de uma rota de aquisição uma pergunta que nunca foi dela.
CHECKER_DE_EGRESSO = 'https://ipinfo.io/json'

# `UNKNOWN` é um valor de primeira classe, e não um buraco. Ele existe para que
# «não consegui medir» NUNCA se confunda com um país.
EGRESSO_DESCONHECIDO = 'UNKNOWN'

# ⚠️ UM SENTINELA, E NÃO `None`.
# A primeira versão usava `bruto=None` para dizer «não me deram corpo, vai medir».
# Só que `None` é TAMBÉM o que `_bruto_do_checker()` devolve quando não houve
# resposta — e a prova do timeout, ao injetar `None`, foi à rede a sério e
# voltou com um país verdadeiro. Um caso de red team passou por acidente.
#
#     DOIS SIGNIFICADOS NO MESMO VALOR É COMO SE LÊ O ERRADO.
#
# Agora `None` quer dizer uma coisa só: o checker não respondeu.
_NAO_FORNECIDO = object()


def _bruto_do_checker(timeout=15):
    """O corpo cru do serviço, ou `None`. Esta é a única costura de rede.

    Fica separada de propósito: as provas injetam corpos — `FR`, `US`, JSON
    partido, campo ausente, minúsculas, espaços — sem depender de VPN nenhuma.

        UM PORTÃO QUE SÓ SE TESTA COM A VPN LIGADA NÃO SE TESTA.
    """
    r = subprocess.run(['curl', '-sS', '-m', str(timeout), CHECKER_DE_EGRESSO],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return r.stdout


def egresso(bruto=_NAO_FORNECIDO, quando='NÃO SEI'):
    """`EGRESS_COUNTRY_CODE` desta máquina, ou `UNKNOWN`. Nunca um palpite.

    ⚠️ O IP PÚBLICO NÃO SAI DAQUI. O serviço devolve-o; este dicionário não o
    carrega, e por isso ele não entra em log, artefato nem registo. A pergunta
    era o PAÍS, e guardar mais do que a pergunta é guardar o que ninguém pediu.

        REGISTAR SÓ O QUE FOI PERGUNTADO.

    A normalização é explícita, e é curta de propósito: tira espaços e sobe a
    caixa. `it` e ` IT ` são o mesmo país; qualquer coisa que não sejam DUAS
    letras não é um país e vira `UNKNOWN`.
    """
    if bruto is _NAO_FORNECIDO:
        bruto = _bruto_do_checker()
    fora = {'EGRESS_COUNTRY_CODE': EGRESSO_DESCONHECIDO,
            'CHECKED_AT': quando, 'CHECKER': CHECKER_DE_EGRESSO}
    if bruto is None:
        fora['PORQUE'] = 'o checker nao respondeu (timeout, rede ou proxy)'
        return fora
    try:
        d = json.loads(bruto)
    except (ValueError, TypeError):
        fora['PORQUE'] = 'o checker respondeu algo que nao e JSON'
        return fora
    if not isinstance(d, dict) or 'country' not in d:
        fora['PORQUE'] = 'a resposta nao traz o campo `country`'
        return fora
    pais = d.get('country')
    if not isinstance(pais, str):
        fora['PORQUE'] = 'o campo `country` nao e texto'
        return fora
    pais = pais.strip().upper()
    if len(pais) != 2 or not pais.isalpha():
        fora['PORQUE'] = 'o campo `country` nao tem a forma de um codigo de pais'
        return fora
    fora['EGRESS_COUNTRY_CODE'] = pais
    fora['PORQUE'] = 'medido pelo checker publico, sem credencial e sem custo'
    return fora


def portao_de_egresso(exigido='IT', bruto=_NAO_FORNECIDO, quando='NÃO SEI'):
    """O PORTÃO. Fecha por omissão, e `UNKNOWN` fecha-o também.

        UNKNOWN != IT.

    Esta é a linha inteira da missão: um preflight que deixa passar o que não
    conseguiu medir não é um preflight, é um carimbo. Qualquer resultado que não
    seja exactamente o país exigido devolve `BLOCKED`.
    """
    e = egresso(bruto=bruto, quando=quando)
    medido = e['EGRESS_COUNTRY_CODE']
    passa = medido == str(exigido).strip().upper()
    e['EGRESS_REQUIRED'] = str(exigido).strip().upper()
    e['EGRESS_GATE'] = 'PASS' if passa else 'BLOCKED'
    if not passa:
        e['PORQUE_BLOQUEADO'] = (
            'EGRESS_COUNTRY_CODE = %s e o exigido e %s. UNKNOWN tambem bloqueia: '
            'nao se adquire material real sobre um ambiente de rede por medir.'
            % (medido, e['EGRESS_REQUIRED']))
    e['O_QUE_ISTO_NAO_PROVA'] = (
        'VPN_LOCATION != SOURCE_LOCATION e VPN_LOCATION != FACT_LOCATION. '
        'Isto prova o ambiente de rede da execucao, nunca a geografia do dado.')
    return e


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
        'captured_at': captura,
        'ESTADO_DO_REGISTRO': 'CURRENT',
        'AMBIENTE': 'CURRENT_COLLECTION_ENVIRONMENT',
        'CAPTURE_DATE': captura,
        'HEAD': cabeca_do_git(),
        'MEDIDO_POR': 'superficie/rede.py --snapshot',
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
        'QUEM_MANDA': ('o estado vivo e derivado por superficie/rede.py a cada execucao. '
                       'Este arquivo e REGISTRO da medicao, nunca a fonte da verdade.'),
    }


if __name__ == '__main__':
    # ── O PORTÃO DE EGRESSO, E ELE SAI COM CÓDIGO ─────────────────────────
    # `exit 1` e não só um texto: um passo de workflow que imprime BLOCKED e
    # devolve zero deixa a aquisição seguinte arrancar.
    #
    #     UM PORTÃO QUE NÃO FECHA A PORTA É UM CARTAZ.
    if '--portao-de-egresso' in sys.argv:
        i = sys.argv.index('--portao-de-egresso')
        exigido = sys.argv[i + 1] if len(sys.argv) > i + 1 else 'IT'
        v = portao_de_egresso(exigido)
        print(json.dumps(v, ensure_ascii=False, indent=1))
        sys.exit(0 if v['EGRESS_GATE'] == 'PASS' else 1)
    if '--egresso' in sys.argv:
        print(json.dumps(egresso(), ensure_ascii=False, indent=1))
        sys.exit(0)
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
