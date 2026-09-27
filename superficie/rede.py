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
# ⚠️ «ALCANCA O HOST» NAO E «A ROTA ESTA ABERTA», e a distincao passou a ter
# nome depois de uma medicao: em 2026-09-14 a prova de fogo da Collection pediu
# obras ao OpenAlex dezassete vezes e recebeu, com HTTP 200,
#
#     {"error":"Rate limit exceeded",
#      "message":"Insufficient budget. This request costs $0.001
#                 but you only have $0 remaining."}
#
# Isso nao e reputacao de IP nem bloqueio de rede: e MODELO DE NEGOCIO da
# plataforma. Um portao que so pergunta «o host responde?» diria PASS e mandaria
# o coletor gastar a sessao contra uma porta fechada por dinheiro.
#
#     HOST_ALCANCAVEL != ROTA_GRATUITA != QUOTA_DISPONIVEL.
#
# A descricao abaixo deixa de dizer «rota gratuita, sem chave» — que era uma
# afirmacao sobre o MODELO, feita por um portao que so mede REDE. O estado real
# da capacidade vive em `system-map/data/capacidade-openalex.generated.json`,
# escrito por `provas/a_rota_gratuita_ainda_e_gratuita.py`, que e quem tem o
# direito de responder a essa pergunta — e que responde `NAO SEI` quando o
# ambiente nao o deixa medir.
HOSTS = [
    ('api.openalex.org', 'https://api.openalex.org/works?per-page=1',
     'ciência e pesquisadores (ES-T5-002) — SEM CHAVE. Se a rota continua '
     'GRATUITA e outra pergunta, e nao e esta: ver capacidade-openalex'),
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

# ═════════════════════════════════════════════════════════════════════════
# EGR (2026-09-24) · O PAÍS POR CONSENSO DE TRÊS VERIFICADORES
# ═════════════════════════════════════════════════════════════════════════
# MEDIDO: de 13:05 a 15:05 de 24/09 TUDO o que usa rede parou. A VPN estava em
# IT (ipwho.is = IT, ip-api.com = IT), mas o ÚNICO verificador desta casa
# (`ipinfo.io`) respondia 429 «Rate limit hit» — a cota gratuita, partilhada por
# todas as sessões desta máquina, tinha acabado. 429 -> sem `country` -> UNKNOWN
# -> BLOCKED. O portão fez o que devia; quem falhou foi ter UM só medidor.
#
#     UM PORTÃO COM UM SÓ MEDIDOR FECHA QUANDO O MEDIDOR ADOECE.
#
# A REGRA (decisão do bot Luciano 15:05, delegação do dono — não se inventa outra):
#   * votam ipwho.is, ip-api.com e ifconfig.co; ipinfo.io sai do caminho crítico
#     (é medido e registado como TELEMETRIA, sem voto);
#   * cada verificador vota o SEU país; 429, timeout, resposta inválida ou país
#     ausente = sem voto;
#   * PASS se >= 2 votos válidos = exigido; BLOCKED se >= 2 votos válidos != exigido;
#     UNKNOWN (que continua a BLOQUEAR) se < 2 votos válidos ou empate;
#   * UM discordante não tem veto — e a discordância fica escrita (quem disse o quê).
#
# O dono continua a ser ESTE ficheiro. Guarda do arranque, vigia, missões e
# coletores leem `--portao-de-egresso`/`--egresso`; nenhum pergunta aos serviços.
VERIFICADORES = (
    # (nome, url, campo do país, condição de sucesso escrita pelo próprio serviço)
    ('ipwho.is', 'https://ipwho.is/', 'country_code', ('success', True)),
    ('ip-api.com', 'http://ip-api.com/json/?fields=status,countryCode', 'countryCode',
     ('status', 'success')),
    ('ifconfig.co', 'https://ifconfig.co/json', 'country_iso', None),
)
# Só telemetria: medido e registado, NUNCA vota (esteve em 429 a 24/09).
TELEMETRIA = ('ipinfo.io', 'https://ipinfo.io/json', 'country', None)
# Compatibilidade: quem lia `CHECKER` recebe agora a lista dos que votam.
CHECKER_DE_EGRESSO = ', '.join(v[0] for v in VERIFICADORES)
VOTOS_MINIMOS = 2

# `UNKNOWN` é um valor de primeira classe, e não um buraco. Ele existe para que
# «não consegui medir» NUNCA se confunda com um país.
EGRESSO_DESCONHECIDO = 'UNKNOWN'

# ── A CACHE PARTILHADA (3 minutos) ─────────────────────────────────────────
# Várias sessões e o vigia perguntavam o país ao mesmo serviço a cada poucos
# segundos — foi assim que a cota do ipinfo acabou. Uma medição serve a todos os
# processos durante 3 minutos. Fica FORA do Git, e a gravação é atómica (ficheiro
# temporário na mesma pasta + os.replace): um leitor nunca vê meio ficheiro.
#
# ⚠️ A CACHE É DO AMBIENTE DE REDE, NÃO DA MÁQUINA. Uma prova offline (proxy morto
# em 127.0.0.1:9) não pode ler o «IT» que a sessão ao lado mediu há um minuto pela
# VPN — seria um país que nenhum pedido desta corrida viu. Por isso a chave da
# cache inclui as variáveis de proxy e o CURL_HOME: outro ambiente, outra entrada.
CACHE_SEGUNDOS = 180
_VARIAVEIS_DE_REDE = ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY',
                      'http_proxy', 'https_proxy', 'all_proxy', 'no_proxy', 'CURL_HOME')


def caminho_da_cache():
    """`SINTONIA_EGRESSO_CACHE`, ou `%LOCALAPPDATA%` (ou `~/.cache`)/sintonia/egresso-cache.json."""
    if os.environ.get('SINTONIA_EGRESSO_CACHE'):
        return os.environ['SINTONIA_EGRESSO_CACHE']
    base = os.environ.get('LOCALAPPDATA') or os.path.join(os.path.expanduser('~'), '.cache')
    return os.path.join(base, 'sintonia', 'egresso-cache.json')


def chave_do_ambiente(env=None):
    import hashlib
    env = os.environ if env is None else env
    return hashlib.sha256('|'.join('%s=%s' % (k, env.get(k, ''))
                                   for k in _VARIAVEIS_DE_REDE).encode()).hexdigest()[:16]


def ler_cache(agora=None, caminho=None, chave=None):
    """A medição guardada, se for DESTE ambiente e tiver menos de 3 minutos; senão None."""
    import time
    agora = time.time() if agora is None else agora
    try:
        with open(caminho or caminho_da_cache(), encoding='utf-8') as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(d, dict) or d.get('CHAVE_DO_AMBIENTE') != (chave or chave_do_ambiente()):
        return None
    try:
        idade = agora - float(d.get('MEDIDO_EM_EPOCH'))
    except (TypeError, ValueError):
        return None
    if not 0 <= idade < CACHE_SEGUNDOS:
        return None
    return d


def gravar_cache(medicao, caminho=None):
    """Gravação atómica: escreve ao lado e troca de uma vez (os.replace)."""
    import tempfile
    caminho = caminho or caminho_da_cache()
    pasta = os.path.dirname(caminho)
    os.makedirs(pasta, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.egresso-', suffix='.tmp', dir=pasta)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(medicao, f, ensure_ascii=False)
        os.replace(tmp, caminho)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


# ⚠️ UM SENTINELA, E NÃO `None`. `None` quer dizer uma coisa só: não respondeu.
_NAO_FORNECIDO = object()


def _pedir(url, timeout=10):
    """(http_status, corpo) pelo curl, ou (None, None). A única costura de rede."""
    r = subprocess.run(['curl', '-sS', '-m', str(timeout), '-w', '\n%{http_code}', url],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        return None, None
    corpo, _, cod = r.stdout.rpartition('\n')
    try:
        return int(cod), corpo
    except ValueError:
        return None, None


def voto(nome, resposta, campo='country', sucesso=None):
    """O voto de UM verificador: {'VERIFICADOR', 'PAIS' (ou None = sem voto), 'PORQUE'}.

    Sem voto: sem resposta, HTTP != 200 (429 incluído), JSON inválido, o serviço
    a dizer que falhou, país ausente ou sem forma de país.
    ⚠️ O IP, a cidade e a organização que o serviço devolve NÃO saem daqui.
    """
    v = {'VERIFICADOR': nome, 'PAIS': None}
    status, corpo = resposta if isinstance(resposta, tuple) else (200, resposta)
    if corpo is None or status is None:
        v['PORQUE'] = 'nao respondeu (timeout, rede ou proxy)'
        return v
    if status != 200:
        v['PORQUE'] = 'HTTP %s%s' % (status, ' (limite de pedidos)' if status == 429 else '')
        return v
    try:
        d = json.loads(corpo)
    except (ValueError, TypeError):
        v['PORQUE'] = 'respondeu algo que nao e JSON'
        return v
    if not isinstance(d, dict):
        v['PORQUE'] = 'o JSON nao e um objeto'
        return v
    if sucesso and d.get(sucesso[0]) != sucesso[1]:
        v['PORQUE'] = 'o proprio servico diz que falhou (%s=%r)' % (sucesso[0], d.get(sucesso[0]))
        return v
    if campo not in d:
        v['PORQUE'] = 'a resposta nao traz o campo `%s`' % campo
        return v
    pais = d.get(campo)
    if not isinstance(pais, str):
        v['PORQUE'] = 'o campo `%s` nao e texto' % campo
        return v
    pais = pais.strip().upper()
    if len(pais) != 2 or not pais.isalpha():
        v['PORQUE'] = 'o campo `%s` nao tem a forma de um codigo de pais' % campo
        return v
    v['PAIS'] = pais
    v['PORQUE'] = 'voto valido'
    return v


def consenso(votos):
    """(país com >= 2 votos válidos — ou UNKNOWN —, discordância). Empate = UNKNOWN."""
    from collections import Counter
    c = Counter(v['PAIS'] for v in votos if v.get('PAIS'))
    fortes = [p for p, n in c.items() if n >= VOTOS_MINIMOS]
    pais = fortes[0] if len(fortes) == 1 else EGRESSO_DESCONHECIDO
    discordancia = ([{'VERIFICADOR': v['VERIFICADOR'], 'DISSE': v['PAIS']}
                     for v in votos if v.get('PAIS') and v['PAIS'] != pais]
                    if len(c) > 1 else [])
    return pais, discordancia


def medir(respostas=None, timeout=10):
    """Pergunta aos TRÊS (em paralelo) e ao ipinfo (telemetria). `respostas` injeta
    {nome: (http_status, corpo)} sem rede — é assim que as provas votam."""
    import time
    if respostas is None:
        from concurrent.futures import ThreadPoolExecutor
        todos = list(VERIFICADORES) + [TELEMETRIA]
        with ThreadPoolExecutor(max_workers=len(todos)) as ex:
            r = list(ex.map(lambda v: _pedir(v[1], timeout), todos))
        respostas = {v[0]: x for v, x in zip(todos, r)}
    votos = [voto(n, respostas.get(n, (None, None)), campo, suc)
             for n, _u, campo, suc in VERIFICADORES]
    tel = voto(TELEMETRIA[0], respostas.get(TELEMETRIA[0], (None, None)), TELEMETRIA[2])
    return {'VOTOS': votos, 'TELEMETRIA': [tel], 'MEDIDO_EM_EPOCH': time.time()}


def egresso(bruto=_NAO_FORNECIDO, quando='NÃO SEI', respostas=None, cache=True):
    """`EGRESS_COUNTRY_CODE` por consenso, ou `UNKNOWN`. Nunca um palpite.

    `bruto` (compatibilidade das provas antigas): o MESMO corpo, na forma
    {"country": ..}, dado a cada verificador — três votos iguais. `respostas`:
    uma resposta por verificador. Com qualquer injeção a cache não é lida nem
    escrita. ⚠️ O IP PÚBLICO NÃO SAI DAQUI: a pergunta era o PAÍS.
    """
    m = None
    if bruto is not _NAO_FORNECIDO:
        m = {'VOTOS': [voto(n, (200, bruto) if bruto is not None else (None, None))
                       for n, *_ in VERIFICADORES], 'TELEMETRIA': []}
    elif respostas is not None:
        m = medir(respostas)
    else:
        if cache:
            m = ler_cache()
            if m is not None:
                m = dict(m, DA_CACHE=True)
        if m is None:
            m = medir()
            if cache:
                try:
                    gravar_cache(dict(m, CHAVE_DO_AMBIENTE=chave_do_ambiente()))
                except OSError:
                    pass            # sem cache a medida continua certa; so fica mais cara
    pais, disc = consenso(m['VOTOS'])
    validos = sum(1 for v in m['VOTOS'] if v.get('PAIS'))
    fora = {'EGRESS_COUNTRY_CODE': pais, 'CHECKED_AT': quando, 'CHECKER': CHECKER_DE_EGRESSO,
            'VOTOS': [{'VERIFICADOR': v['VERIFICADOR'], 'PAIS': v['PAIS'] or EGRESSO_DESCONHECIDO,
                       'PORQUE': v['PORQUE']} for v in m['VOTOS']],
            'VOTOS_VALIDOS': validos, 'DISCORDANCIA': disc,
            'TELEMETRIA_SEM_VOTO': [{'VERIFICADOR': t['VERIFICADOR'],
                                     'PAIS': t['PAIS'] or EGRESSO_DESCONHECIDO,
                                     'PORQUE': t['PORQUE']} for t in m.get('TELEMETRIA', [])],
            'DA_CACHE': bool(m.get('DA_CACHE'))}
    if pais == EGRESSO_DESCONHECIDO:
        fora['PORQUE'] = ('%d voto(s) valido(s) — sao precisos %d iguais; empate ou falta de '
                          'votos e UNKNOWN' % (validos, VOTOS_MINIMOS))
    else:
        fora['PORQUE'] = 'consenso de %d verificadores publicos, sem credencial e sem custo' % (
            sum(1 for v in m['VOTOS'] if v.get('PAIS') == pais))
    return fora


def portao_de_egresso(exigido='IT', bruto=_NAO_FORNECIDO, quando='NÃO SEI', respostas=None,
                      cache=True):
    """O PORTÃO. Fecha por omissão, e `UNKNOWN` fecha-o também.

        UNKNOWN != IT.

    PASS     >= 2 votos válidos = exigido
    BLOCKED  >= 2 votos válidos != exigido — ou UNKNOWN (menos de 2 votos, empate)
    Um discordante não tem veto; fica em DISCORDANCIA.
    """
    e = egresso(bruto=bruto, quando=quando, respostas=respostas, cache=cache)
    exigido = str(exigido).strip().upper()
    a_favor = sum(1 for v in e['VOTOS'] if v['PAIS'] == exigido)
    contra = sum(1 for v in e['VOTOS'] if v['PAIS'] not in (exigido, EGRESSO_DESCONHECIDO))
    passa = a_favor >= VOTOS_MINIMOS
    e['EGRESS_REQUIRED'] = exigido
    e['EGRESS_GATE'] = 'PASS' if passa else 'BLOCKED'
    e['EGRESS_VERDICT'] = ('PASS' if passa else
                           'BLOCKED' if contra >= VOTOS_MINIMOS else EGRESSO_DESCONHECIDO)
    if not passa:
        e['PORQUE_BLOQUEADO'] = (
            'EGRESS_COUNTRY_CODE = %s (votos em %s: %d, noutro pais: %d) e o exigido e %s. '
            'UNKNOWN tambem bloqueia: nao se adquire material real sobre um ambiente de rede '
            'por medir.' % (e['EGRESS_COUNTRY_CODE'], exigido, a_favor, contra, exigido))
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
        v = portao_de_egresso(exigido, cache='--sem-cache' not in sys.argv)
        print(json.dumps(v, ensure_ascii=False, indent=1))
        sys.exit(0 if v['EGRESS_GATE'] == 'PASS' else 1)
    if '--egresso' in sys.argv:
        print(json.dumps(egresso(cache='--sem-cache' not in sys.argv), ensure_ascii=False, indent=1))
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
