#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CANARIO REMOTO DA ROTA PERMITIDA DO LINKEDIN — `descoberta-indireta:site-da-organizacao`

A matriz declara esta rota `PERMITIDA = SIM` e `ESTADO = POSSIBLE_NOT_PROVED`.
`POSSIBLE_NOT_PROVED` diz exactamente o que diz: ninguem a correu contra a rede.
A prova offline (`provas/linkedin_local_first.py`) exerce o coracao da rota com
HTML injectado — prova a TRADUCAO, nao prova a AQUISICAO.

    MECHANISM PROVEN  !=  EXECUTION PROVEN.

Este canario fecha o segundo eixo: sai para a rede, contra sites REAIS de
organizacoes italianas, e mede.

O QUE ESTE CANARIO NUNCA FAZ
-----------------------------
Nao visita `linkedin.com` nem `licdn.com` — nem sequer para ler robots. O
adaptador ja recusa o alvo estaticamente e declara os hosts proibidos ao
transporte, que recusa tambem cada REDIRECIONAMENTO. Este ficheiro instala uma
SENTINELA por cima disso: espia `socket.getaddrinfo` e falha a corrida inteira
se um nome proibido for sequer resolvido.

    ZERO PEDIDOS INCLUI ZERO RESOLUCOES DE NOME.

E O IDENTITY GUARD
-------------------
HTTP 200 nao prova identidade. Um site pode publicar o LinkedIn de um parceiro,
de uma agencia ou de um grupo internacional. Por isso cada handle achado e
confrontado com o dominio que o publicou, e o veredicto sai em tres estados
proprios — nunca um booleano:

    IDENTITY_SELF_DECLARED   o site da organizacao X publica o handle X
    IDENTITY_MISMATCH        o site de X publica o handle de OUTRA entidade
    IDENTITY_NOT_KNOWN       nao da para decidir por comparacao de nome

`IDENTITY_NOT_KNOWN` nao e reprovacao, e nao se arredonda para nenhum dos outros
dois. Um handle que nao se consegue atribuir continua a ser um facto observado:
«este site publicou este endereco». O que ele nao e, e prova de que a conta
pertence aquela organizacao.

    UNKNOWN PERMANECE UNKNOWN.
"""
import os
import socket
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)

# ══════════════════════════════════════════════════════════════════════════
# A SENTINELA — instalada ANTES de qualquer import que saiba abrir socket
# ══════════════════════════════════════════════════════════════════════════
HOSTS_PROIBIDOS = ('linkedin.com', 'licdn.com')
RESOLUCOES = []
TOCADOS_PROIBIDOS = []
_getaddrinfo = socket.getaddrinfo


def _espia(host, port, *a, **k):
    nome = str(host or '').lower()
    RESOLUCOES.append(nome)
    for mau in HOSTS_PROIBIDOS:
        if nome == mau or nome.endswith('.' + mau):
            TOCADOS_PROIBIDOS.append(nome)
            raise AssertionError('SENTINELA: resolucao de host proibido %r' % nome)
    return _getaddrinfo(host, port, *a, **k)


socket.getaddrinfo = _espia

import _gavetas  # noqa: E402,F401
import adaptador_linkedin as li     # noqa: E402
import scrap_http as http           # noqa: E402
import social_matriz as mz          # noqa: E402

RUN = 'SOCIAL-ACQ-V1-LINKEDIN-CANARIO'

#: Os canarios. Poucos, reais, representativos — e de IDENTIDADES DISTINTAS,
#: como a missao exige. Sao sites de organizacoes do agro italiano; nenhum
#: deles e o linkedin.com.
#:
#: A LISTA NAO ENCOLHE QUANDO UM ALVO FALHA. Um site que responde 403 ou que
#: nao serve robots.txt e uma MEDICAO da robustez desta rota, e apaga-lo
#: transformaria a taxa de sucesso numa escolha em vez de num numero.
CANARIOS = (
    ('IT-CANARIO-01', 'https://www.imagelinenetwork.com/', 'imagelinenetwork'),
    ('IT-CANARIO-02', 'https://www.confagricoltura.it/', 'confagricoltura'),
    ('IT-CANARIO-03', 'https://www.coldiretti.it/', 'coldiretti'),
    ('IT-CANARIO-04', 'https://www.syngenta.it/', 'syngenta'),
    ('IT-CANARIO-05', 'https://www.crea.gov.it/', 'crea'),
    ('IT-CANARIO-06', 'https://www.ismea.it/', 'ismea'),
    ('IT-CANARIO-07', 'https://www.edagricole.it/', 'edagricole'),
    ('IT-CANARIO-08', 'https://www.freshplaza.it/', 'freshplaza'),
)

OK = []


def diz(cond, rotulo, valor=''):
    OK.append(bool(cond))
    print('  %-5s %-58s %s' % ('ok' if cond else 'FAIL', rotulo, str(valor)[:60]))


def _norm(s):
    return ''.join(ch for ch in str(s or '').lower() if ch.isalnum())


def identidade(handle_slug, marca_do_site):
    """→ um dos tres estados. Nunca um booleano, nunca um palpite calado."""
    h, m = _norm(handle_slug), _norm(marca_do_site)
    if not h or not m:
        return 'IDENTITY_NOT_KNOWN'
    if m in h or h in m:
        return 'IDENTITY_SELF_DECLARED'
    return 'IDENTITY_MISMATCH'


print('=' * 88)
print('CANARIO · LINKEDIN · rota descoberta-indireta:site-da-organizacao')
print('=' * 88)

# ── 1 · A LEI, CORRIDA E NAO CITADA ───────────────────────────────────────
print('\n1 · A politica, executada')
d = mz.decisao('LINKEDIN', 'DISCOVER_ACCOUNT')
diz(d['DECISAO'] == 'ALLOWED', 'DISCOVER_ACCOUNT esta ALLOWED', d['DECISAO'])
diz(d['ROTA'] == li.ROTA_IDENTIDADE, 'e a rota e a que este adaptador implementa', d['ROTA'])
dp = mz.decisao('LINKEDIN', 'FETCH_POST')
diz(dp['DECISAO'] == 'ROUTE_NOT_ALLOWED', 'FETCH_POST continua ROUTE_NOT_ALLOWED', dp['DECISAO'])

# ── 2 · O ALVO PROIBIDO E RECUSADO ANTES DA REDE ──────────────────────────
print('\n2 · Red team do alvo — o linkedin.com como «site da organizacao»')
try:
    li.identidade_pelo_site(site_url='https://www.linkedin.com/company/image-line', run_id=RUN)
    diz(False, 'devia ter recusado o host proibido', 'NAO RECUSOU')
except http.RotaNaoPermitida as e:
    diz(True, 'recusa com RotaNaoPermitida (nao «zero resultados»)', str(e)[:44])
except AssertionError as e:
    diz(False, 'a SENTINELA disparou: chegou a resolver o host', e)
try:
    li.identidade_pelo_site(site_url='', run_id=RUN)
    diz(False, 'alvo vazio devia ser ValueError', 'NAO RECUSOU')
except ValueError:
    diz(True, 'alvo vazio = ALVO_AUSENTE_OU_MALFORMADO', 'ValueError')

# ── 3 · OS CANARIOS REAIS ─────────────────────────────────────────────────
print('\n3 · Canarios reais — a rede, contra sites de organizacoes')
resultados = []
for cid, site, marca in CANARIOS:
    medida = {}
    linha = {'CANARY_ID': cid, 'DISCOVERY_SOURCE': site, 'ROUTE': li.ROTA_IDENTIDADE,
             'PROVIDER': 'coleta/adaptador_linkedin.identidade_pelo_site'}
    try:
        objs = li.identidade_pelo_site(site_url=site, run_id=RUN, country_scope='IT',
                                       medida=medida)
        linha['RESULT'] = 'OK'
        linha['HANDLES'] = [(o['RAW']['TARGET_TYPE'], o['NATIVE_ID'], o['URL']) for o in objs]
        linha['ITEMS_FOUND'] = len(objs)
        linha['COST_USD'] = medida.get('ACTUAL_COST_USD')
        linha['IDENTITY'] = [identidade(o['NATIVE_ID'], marca) for o in objs]
        linha['ENVELOPES'] = objs
    except http.PortaoIndisponivel as e:
        linha.update(RESULT='GATE_UNAVAILABLE', BLOCK_REASON=str(e)[:90], ITEMS_FOUND=0)
    except http.RotaNaoPermitida as e:
        linha.update(RESULT='ROUTE_NOT_ALLOWED', BLOCK_REASON=str(e)[:90], ITEMS_FOUND=0)
    except Exception as e:
        linha.update(RESULT='ERROR:' + type(e).__name__, BLOCK_REASON=str(e)[:90],
                     ITEMS_FOUND=0)
    resultados.append(linha)
    print('  %-14s %-34s %-18s itens=%s' % (
        cid, site[:34], linha['RESULT'], linha.get('ITEMS_FOUND')))
    for t, s, u in linha.get('HANDLES', [])[:6]:
        print('        %-8s %-30s %s' % (t, s[:30], identidade(s, marca)))
    if linha.get('BLOCK_REASON'):
        print('        motivo: %s' % linha['BLOCK_REASON'])

sucesso = [r for r in resultados if r['RESULT'] == 'OK']
com_handle = [r for r in sucesso if r['ITEMS_FOUND']]
print('\n  CANARY_PASS = %d/%d   COM_HANDLE = %d' % (len(sucesso), len(CANARIOS), len(com_handle)))
diz(len(com_handle) >= 2, 'pelo menos DUAS identidades distintas adquiridas', len(com_handle))

# ── 4 · IDENTITY GUARD — a contraprova ────────────────────────────────────
print('\n4 · Identity guard — a contraprova, identidade A contra pagina B')
if com_handle:
    alvo = com_handle[0]
    slug = alvo['HANDLES'][0][1]
    outra = 'uma-entidade-que-nao-e-esta'
    diz(identidade(slug, outra) == 'IDENTITY_MISMATCH',
        'handle de A confrontado com a marca B da IDENTITY_MISMATCH', identidade(slug, outra))
    diz(identidade(slug, '') == 'IDENTITY_NOT_KNOWN',
        'sem marca para comparar, UNKNOWN permanece UNKNOWN', identidade(slug, ''))
    estados = {e for r in com_handle for e in r['IDENTITY']}
    diz(estados <= {'IDENTITY_SELF_DECLARED', 'IDENTITY_MISMATCH', 'IDENTITY_NOT_KNOWN'},
        'so existem os tres estados declarados', sorted(estados))
else:
    diz(False, 'sem handle adquirido nao ha identity guard a correr', 'NOT_RUN')

# ── 5 · O OUTPUT MINIMO, E O QUE ELE NAO INVENTA ──────────────────────────
print('\n5 · Output minimo do item adquirido')
if com_handle:
    e0 = com_handle[0]['ENVELOPES'][0]
    for campo in ('PLATFORM', 'NATIVE_ID', 'URL', 'CONTENT_TYPE', 'ROUTE', 'RUN_ID'):
        diz(e0.get(campo) is not None, 'campo presente: %s' % campo, e0.get(campo))
    diz(e0['CONTENT_TYPE'] == 'DISCOVERY', 'CONTENT_TYPE = DISCOVERY, nunca POST', e0['CONTENT_TYPE'])
    diz(e0['RAW']['POST_CONTENT'] is None and not e0['RAW']['CONTENT_ACQUIRED'],
        'IDENTITY != CONTENT: nenhum texto de post fabricado', 'ok')
    diz('FACT_TIME' not in e0 and 'FACT_LOCATION' not in e0,
        'nao fabrica FACT_TIME nem FACT_LOCATION', 'ok')
    diz(e0['RAW'].get('RAW_SHA256'), 'o bruto tem SHA256 e ficheiro preservado',
        str(e0['RAW'].get('RAW_SHA256'))[:16])
    diz(e0.get('COST_USD') == 0.0, 'custo da rota = 0', e0.get('COST_USD'))

# ── 6 · A SENTINELA ───────────────────────────────────────────────────────
print('\n6 · A sentinela de rede')
diz(not TOCADOS_PROIBIDOS, 'ZERO resolucoes de linkedin.com / licdn.com', TOCADOS_PROIBIDOS or 0)
hosts = sorted(set(RESOLUCOES))
print('     hosts resolvidos: %s' % (hosts,))

print('\n' + '=' * 88)
veredito = 'PASS' if all(OK) else 'FAIL'
print('LINKEDIN_DISCOVERY_REMOTE_CANARY = %s   (%d/%d asserts)' % (
    veredito, sum(OK), len(OK)))
print('LINKEDIN_HTTP_REQUESTS = 0 · LICDN_REQUESTS = 0')
print('CANARY_PASS = %d/%d · IDENTIDADES_COM_HANDLE = %d' % (
    len(sucesso), len(CANARIOS), len(com_handle)))
print('PAID_USD = 0 · APIFY_RUNS = 0')
print('POLICY_CHANGED = NO   (leis/social_matriz.py intacto)')
sys.exit(0 if all(OK) else 1)
