#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-SR-02 — nenhuma compra nasce sem autorizacao.

    python3 tests/test_scrap_sr02_autorizacao.py

ZERO REDE, ZERO DOLAR. O boundary externo e substituido; nada sai desta
maquina. O livro da relevancia usado aqui e um livro DE PROVA, em memoria: esta
missao nao avalia fontes e nao escreve no livro real.

    APIFY_REAL_RUNS = 0 · META_REAL_REQUESTS = 0 · COST_USD = 0
"""
import os
import sys
import unittest  # noqa: F401 — usado pelas provas de importacao

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
for d in (RAIZ, os.path.join(RAIZ, 'coleta'), os.path.join(RAIZ, 'leis'),
          os.path.join(RAIZ, 'ferramentas'), os.path.join(RAIZ, 'regras')):
    sys.path.insert(0, d)
import _gavetas  # noqa: E402,F401
import autorizacao_de_gasto as ag   # noqa: E402
import relevancia_da_fonte as rel   # noqa: E402
import coletor as ct                # noqa: E402
import social_matriz as mz          # noqa: E402
import scrap_registo as reg         # noqa: E402
import scrap_http as http           # noqa: E402
import social_rotas as sr           # noqa: E402

FALHAS, ATAQUES = [], 0

# ── O LIVRO DE PROVA ────────────────────────────────────────────────────────
# Cinco pares, um por estado. Escrito aqui para que a prova nao dependa do
# livro real — e para que ela NAO o altere.
def _d(sid, pro, res, ev=True):
    return rel.Decisao(source_id=sid, proposito=pro, resultado=res,
                       motivo='prova SCRAP-SR-02', metodo='fixture',
                       evidencia={'prova': 'fixture'} if ev else {}).para_livro()


LIVRO = [
    _d('IT-T3-005', 'T3', rel.SIM),
    _d('IT-T9-001', 'T9', rel.NAO),
    _d('IT-T5-002', 'T5', rel.NAO_SEI, ev=False),
    _d('IT-T7-003', 'T7', rel.ERRO, ev=False),
]


def ataque(n, titulo, cond, detalhe=''):
    global ATAQUES
    ATAQUES += 1
    if cond:
        print('  PASS  %2d %s' % (n, titulo))
    else:
        print('  FAIL  %2d %s  %s' % (n, titulo, detalhe))
        FALHAS.append((n, titulo, detalhe))


def compra(autorizacao, **kw):
    """Tenta a compra pela PORTA UNICA. Devolve (comprou?, veredito|erro).

    O transporte e substituido: se a guarda deixar passar, contamos um POST
    FALSO — nenhuma ida a rede acontece.
    """
    posts = []
    orig = ct._curl
    ct._curl = lambda url, **k: (posts.append(url) or {'data': {'id': 'FALSO',
                                                                'status': 'SUCCEEDED',
                                                                'defaultDatasetId': 'd'}})
    try:
        ct.executar('ator/falso', {'q': 1}, token='T', run_id='r', platform='P',
                    country='IT', mission='SR-02', query='q',
                    source_version='v', evidence_path='e',
                    wait=1, salvar_raw=False, autorizacao=autorizacao, **kw)
        return True, None
    except ag.GastoNaoAutorizado as e:
        return False, e.veredito
    except Exception as e:                                        # noqa: BLE001
        # Qualquer outra falha acontece DEPOIS da guarda — logo a guarda passou.
        return (len(posts) > 0), {'VEREDITO': 'PASSOU_A_GUARDA:%s' % type(e).__name__}
    finally:
        ct._curl = orig


OK = ag.AUTORIZADO
print('\nRED TEAM · a porta unica da compra\n' + '-' * 72)

# ── 1-9 · COLHEITA NORMAL, OS SETE ESTADOS DA RELEVANCIA ───────────────────
v = ag.conferir(ag.normal(source_id='IT-T3-005', proposito='T3'),
                custo='pago', livro=LIVRO,
                source_id_pedido='IT-T3-005', proposito_pedido='T3')
ataque(1, 'SIM no par certo AUTORIZA', v['VEREDITO'] == OK, v['VEREDITO'])

v = ag.conferir(ag.normal(source_id='IT-T3-005', proposito='T3'), custo='pago',
                livro=LIVRO, source_id_pedido='IT-T9-001', proposito_pedido='T3')
ataque(2, 'SIM para A nao autoriza corrida contra B',
       v['VEREDITO'] == ag.AUTORIZACAO_INVALIDA, v['VEREDITO'])

v = ag.conferir(ag.normal(source_id='IT-T3-005', proposito='T3'), custo='pago',
                livro=LIVRO, source_id_pedido='IT-T3-005', proposito_pedido='T9')
ataque(3, 'SIM para T3 nao autoriza corrida para T9',
       v['VEREDITO'] == ag.AUTORIZACAO_INVALIDA, v['VEREDITO'])

v = ag.conferir(ag.normal(source_id='IT-T9-001', proposito='T9'), custo='pago', livro=LIVRO)
ataque(4, 'NAO barra, e o veredito diz que foi a RELEVANCIA',
       v['VEREDITO'] == ag.BARRADO_PELA_RELEVANCIA, v['VEREDITO'])

v = ag.conferir(ag.normal(source_id='IT-T5-002', proposito='T5'), custo='pago', livro=LIVRO)
ataque(5, 'NAO_SEI nao autoriza — e NAO e lido como «nao serve»',
       v['VEREDITO'] == ag.EXIGE_AVALIACAO and v['VEREDITO'] != ag.BARRADO_PELA_RELEVANCIA,
       v['VEREDITO'])

v = ag.conferir(ag.normal(source_id='IT-T7-003', proposito='T7'), custo='pago', livro=LIVRO)
ataque(6, 'ERRO nao autoriza', v['VEREDITO'] == ag.EXIGE_AVALIACAO, v['VEREDITO'])

v = ag.conferir(ag.normal(source_id='IT-T1-999', proposito='T1'), custo='pago', livro=LIVRO)
ataque(7, 'NAO_AVALIADA nao autoriza', v['VEREDITO'] == ag.EXIGE_AVALIACAO, v['VEREDITO'])

v = ag.conferir(ag.normal(source_id=None, proposito='T3'), custo='pago', livro=LIVRO)
ataque(8, 'SOURCE_ID ausente nao autoriza',
       v['VEREDITO'] in (ag.AUTORIZACAO_INVALIDA, ag.EXIGE_AVALIACAO), v['VEREDITO'])

v = ag.conferir(ag.normal(source_id='https://exemplo.it/feed', proposito='T3'),
                custo='pago', livro=LIVRO)
ataque(9, 'URL no lugar de SOURCE_ID e recusada',
       v['VEREDITO'] == ag.AUTORIZACAO_INVALIDA, v['VEREDITO'])

# ── 10-14 · NENHUMA AUTORIZACAO, E OS SUBSTITUTOS QUE NAO SERVEM ───────────
comprou, ver = compra(None)
ataque(10, 'compra sem autorizacao nenhuma e recusada na porta unica',
       not comprou and ver['VEREDITO'] == ag.SEM_AUTORIZACAO, str(ver))

comprou, _ = compra({'CONTRATO': 'OUTRO/v1', 'PROPOSITO_DO_GASTO': ag.NORMAL})
ataque(11, 'autorizacao de outro contrato nao serve', not comprou)

comprou, _ = compra('APIFY_TOKEN_PRESENTE')
ataque(12, 'um token NAO substitui autorizacao', not comprou)

with ct.orcamento_financeiro(10.0):
    comprou, ver = compra(None)
ataque(13, 'ter ORCAMENTO nao substitui autorizacao',
       not comprou and ver['VEREDITO'] == ag.SEM_AUTORIZACAO, str(ver))

d = mz.decisao('YOUTUBE', 'FETCH_TRANSCRIPT')
comprou, _ = compra(None)
ataque(14, 'uma rota ALLOWED na matriz nao substitui autorizacao', not comprou)

# ── 15-19 · PROBE ───────────────────────────────────────────────────────────
p_ok = ag.probe(source_id='IT-T1-999', proposito='T1', humano='humano X',
                max_runs=1, max_posts=1, max_usd=0.5, max_items=20,
                condicao_de_paragem='um POST')
v = ag.conferir(p_ok, custo='pago', livro=LIVRO)
ataque(15, 'PROBE abre fonte NAO_AVALIADA, com tectos e mao humana',
       v['VEREDITO'] == OK, v['VEREDITO'])

for falta in ('MAX_PROVIDER_RUNS', 'MAX_START_POSTS', 'MAX_USD', 'MAX_ITEMS'):
    mau = dict(p_ok); mau[falta] = None
    v = ag.conferir(mau, custo='pago', livro=LIVRO)
    if v['VEREDITO'] != ag.FORA_DO_TECTO:
        FALHAS.append((16, 'probe sem %s passou' % falta, v['VEREDITO']))
ataque(16, 'PROBE sem QUALQUER um dos quatro tectos e recusado',
       not [f for f in FALHAS if f[0] == 16])

mau = dict(p_ok); mau['HUMAN_AUTHORIZATION'] = ''
v = ag.conferir(mau, custo='pago', livro=LIVRO)
ataque(17, 'PROBE sem mao humana e recusado', v['VEREDITO'] == ag.FORA_DO_TECTO, v['VEREDITO'])

mau = dict(p_ok); mau['MAX_USD'] = 0
v = ag.conferir(mau, custo='pago', livro=LIVRO)
ataque(18, 'tecto ZERO nao e tecto: e recusa', v['VEREDITO'] == ag.FORA_DO_TECTO, v['VEREDITO'])

antes = len(LIVRO)
ag.conferir(p_ok, custo='pago', livro=LIVRO)
ataque(19, 'PROBE nao escreve no livro — medir nao e decidir', len(LIVRO) == antes)

# ── 20-24 · TRIAL ───────────────────────────────────────────────────────────
t_ok = ag.trial(capacidade='youtube.native_caption', alvo='VIDEO-X',
                humano='humano Y', max_runs=1, max_posts=1, max_usd=0.1,
                max_items=10, condicao_de_paragem='um POST')
v = ag.conferir(t_ok, custo='pago', livro=LIVRO)
ataque(20, 'TRIAL nao pede relevancia — prova a maquina, nao a fonte',
       v['VEREDITO'] == OK, v['VEREDITO'])

mau = dict(t_ok); mau['ALVO'] = ''
v = ag.conferir(mau, custo='pago', livro=LIVRO)
ataque(21, 'TRIAL sem ALVO fixo e recusado', v['VEREDITO'] == ag.FORA_DO_TECTO, v['VEREDITO'])

mau = dict(t_ok); mau['MAX_START_POSTS'] = None
v = ag.conferir(mau, custo='pago', livro=LIVRO)
ataque(22, 'TRIAL sem tecto de POSTs e recusado', v['VEREDITO'] == ag.FORA_DO_TECTO, v['VEREDITO'])

v = ag.conferir(t_ok, custo='pago', livro=LIVRO, source_id_pedido='IT-T9-001')
ataque(23, 'NORMAL nao pode vestir-se de TRIAL para fugir a relevancia',
       v['VEREDITO'] == ag.AUTORIZACAO_INVALIDA, v['VEREDITO'])

v = ag.conferir(t_ok, custo='pago', livro=LIVRO, source_id_pedido='IT-T3-005')
ataque(24, 'nem com uma fonte que TEM SIM no livro',
       v['VEREDITO'] == ag.AUTORIZACAO_INVALIDA, v['VEREDITO'])

# ── 25-27 · NORMAL vestido de PROBE ────────────────────────────────────────
v = ag.conferir(ag.probe(source_id='IT-T9-001', proposito='T9', humano='h',
                         max_runs=1, max_posts=1, max_usd=0.1, max_items=10,
                         condicao_de_paragem='um POST'),
                custo='pago', livro=LIVRO)
ataque(25, 'PROBE tambem abre fonte com NAO — mas so com tectos e mao humana',
       v['VEREDITO'] == OK, v['VEREDITO'])

v = ag.conferir(ag.probe(source_id='IT-T3-005', proposito='T3', humano='h',
                         max_runs=1, max_posts=1, max_usd=0.1, max_items=10,
                         condicao_de_paragem='x'),
                custo='pago', livro=LIVRO, source_id_pedido='IT-T9-001')
ataque(26, 'PROBE para A nao autoriza corrida contra B',
       v['VEREDITO'] == ag.AUTORIZACAO_INVALIDA, v['VEREDITO'])

v = ag.conferir({'CONTRATO': ag.CONTRATO, 'PROPOSITO_DO_GASTO': 'INVENTADO'},
                custo='pago', livro=LIVRO)
ataque(27, 'proposito de gasto inventado e recusado',
       v['VEREDITO'] == ag.AUTORIZACAO_INVALIDA, v['VEREDITO'])

# ── 28-31 · A GUARDA VEM ANTES DO DINHEIRO ─────────────────────────────────
class _Orc:
    def __init__(self): self.reservas = 0
    def reservar(self, **k): self.reservas += 1; raise AssertionError('reservou!')


orc = _Orc()
antigo = ct.orcamento_financeiro_actual
ct.orcamento_financeiro_actual = lambda: orc
try:
    comprou, ver = compra(None)
finally:
    ct.orcamento_financeiro_actual = antigo
ataque(28, 'recusa de gasto NAO reserva dinheiro — a guarda vem antes',
       not comprou and orc.reservas == 0, 'reservas=%d' % orc.reservas)

comprou, _ = compra(ag.normal(source_id='IT-T9-001', proposito='T9'),
                    source_id='IT-T9-001', proposito='T9')
ataque(29, 'NAO no livro real tambem nao compra pela porta unica', not comprou)

ataque(30, 'o veredito distingue QUEM recusou',
       ag.BARRADO_PELA_RELEVANCIA != ag.SEM_AUTORIZACAO
       and ag.EXIGE_AVALIACAO != ag.BARRADO_PELA_RELEVANCIA)

v = ag.conferir(ag.normal(source_id='IT-T5-002', proposito='T5'), custo='pago', livro=LIVRO)
ataque(31, 'NAO_SEI e ERRO nao sao escritos como «a fonte nao serve»',
       v['VEREDITO'] == ag.EXIGE_AVALIACAO)

# ── 32-36 · OS ENTRYPOINTS ANTIGOS ─────────────────────────────────────────
import inspect  # noqa: E402
fonte_ct = inspect.getsource(ct.executar)
ataque(32, 'a guarda esta DENTRO da porta unica, nao nos chamadores',
       'autorizacao_de_gasto' in fonte_ct and '_ag.exigir' in fonte_ct)

posicao_guarda = fonte_ct.index('_ag.exigir')
posicao_reserva = fonte_ct.index('reservar(')
ataque(33, 'a guarda corre ANTES da reserva financeira, no codigo',
       posicao_guarda < posicao_reserva,
       'guarda@%d reserva@%d' % (posicao_guarda, posicao_reserva))

posicao_post = fonte_ct.index("metodo='POST'")
ataque(34, 'a guarda corre ANTES do POST', posicao_guarda < posicao_post)

import subprocess  # noqa: E402
# A varredura mede CODIGO DE PRODUCAO. A primeira versao contava tambem as
# ocorrencias dentro das proprias provas — que sao strings de asserção, nao
# primitivas de compra.
#
#     UMA PROVA QUE SE CONTA A SI PROPRIA MEDE-SE, NAO MEDE O SISTEMA.
saida = subprocess.run(
    ['grep', '-rn', "metodo='POST'", '--include=*.py', RAIZ],
    capture_output=True, text=True).stdout.strip().split('\n')
saida = [l for l in saida if l.strip()
         and '/tests/' not in l and '/provas/' not in l]
ataque(35, 'existe UMA unica primitiva de criacao de compra no repositorio',
       len(saida) == 1 and 'coletor.py' in saida[0],
       '%d sitios: %s' % (len(saida), [s.split(':')[0].split('/')[-1] for s in saida]))

ataque(36, 'apify_pool NAO cria compra — ele e dono do token, nao do gasto',
       "metodo='POST'" not in open(os.path.join(RAIZ, 'ferramentas', 'apify_pool.py'),
                                   encoding='utf-8').read())

# ── 37-41 · META NAO REGRIDE ───────────────────────────────────────────────
reg.carregar_adaptadores()
pedidos = []
orig_open = http.urllib.request.urlopen


def _espiao(req, *a, **k):
    pedidos.append(req.get_full_url() if hasattr(req, 'get_full_url') else str(req))
    raise RuntimeError('rede bloqueada pela prova')


http.urllib.request.urlopen = _espiao
try:
    _o, _r = sr._executar(platform='META', capability='SEARCH_ADS', run_id='sr02')
finally:
    http.urllib.request.urlopen = orig_open

ataque(37, 'META sem credencial: CREDENTIAL_MISSING, nao ROUTE_NOT_ALLOWED',
       _r['ESTADO'] == 'CREDENTIAL_MISSING', _r['ESTADO'])
ataque(38, 'META sem credencial: NETWORK_ATTEMPTS = 0',
       len(pedidos) == 0, 'idas: %d %s' % (len(pedidos), pedidos[:1]))
ataque(39, 'META: ALLOWED continua distinto de READY',
       mz.decisao('META', 'SEARCH_ADS')['DECISAO'] == mz.PERMITIDA_SIM
       and mz.prontidao('META', 'SEARCH_ADS')['PRONTIDAO'] == mz.ZERO_DOLAR_MAS_TRANCADA)
ataque(40, 'META: a credencial vem da SONDA, nao da declaracao da matriz',
       reg.sonda_de('META', 'meta.ads.search') is not None)
ataque(41, 'META: falta de credencial nao vira rota paga',
       _r['CLASSE_DA_ROTA'] != 'APIFY' and _r['MOTIVO_PAGO'] is None)

# ── 42-45 · WORKFLOWS E CLI ────────────────────────────────────────────────
import glob  # noqa: E402
wfs = glob.glob(os.path.join(RAIZ, '.github', 'workflows', '*.yml'))
com_actor = [os.path.basename(w) for w in wfs
             if any(a in open(w, encoding='utf-8').read()
                    for a in ('~instagram-', '~facebook-', '~youtube-', 'apify~'))]
ataque(42, 'nenhum workflow nomeia um Actor pago', not com_actor, str(com_actor))

ss = open(os.path.join(RAIZ, 'coleta', 'social_scrap.py'), encoding='utf-8').read()
ataque(43, 'a CLI paga DERIVA a autorizacao da tabela versionada',
       "kw['autorizacao'] = _ag.trial(" in ss and 'FASES_PAGAS' in ss)
ataque(44, 'a tabela de fases pagas declara os quatro tectos',
       all(k in ss for k in ('MAX_PROVIDER_RUNS', 'MAX_START_POSTS', 'MAX_USD', 'MAX_ITEMS')))

ay = open(os.path.join(RAIZ, 'coleta', 'adaptador_youtube.py'), encoding='utf-8').read()
ataque(45, 'o adaptador PASSA a autorizacao e nao a fabrica',
       'autorizacao=autorizacao' in ay and '_ag.trial(' not in ay and '_ag.normal(' not in ay)

# ══════════════════════════════════════════════════════════════════════════
print('\nMUTATION · 20 mutantes\n' + '-' * 72)
MUT = []


def mutante(n, desc, morre):
    MUT.append(n)
    print('  %-10s %-5s %s' % ('MORTO' if morre else 'SOBREVIVEU', n, desc))
    if not morre:
        FALHAS.append((n, desc, 'sobreviveu'))


mutante('M1', 'guarda removida da porta unica', '_ag.exigir' in fonte_ct)
mutante('M2', 'NAO_SEI autorizado',
        ag.conferir(ag.normal(source_id='IT-T5-002', proposito='T5'), custo='pago',
                    livro=LIVRO)['VEREDITO'] != OK)
mutante('M3', 'NAO_AVALIADA autorizada',
        ag.conferir(ag.normal(source_id='IT-XX-000', proposito='T1'), custo='pago',
                    livro=LIVRO)['VEREDITO'] != OK)
mutante('M4', 'fonte errada aceite',
        ag.conferir(ag.normal(source_id='IT-T3-005', proposito='T3'), custo='pago',
                    livro=LIVRO, source_id_pedido='IT-T9-001')['VEREDITO'] != OK)
mutante('M5', 'proposito errado aceite',
        ag.conferir(ag.normal(source_id='IT-T3-005', proposito='T3'), custo='pago',
                    livro=LIVRO, proposito_pedido='T9')['VEREDITO'] != OK)
mutante('M6', 'URL aceite como SOURCE_ID',
        ag.conferir(ag.normal(source_id='http://x.it', proposito='T3'), custo='pago',
                    livro=LIVRO)['VEREDITO'] != OK)
mutante('M7', 'token substitui autorizacao', not compra('TOKEN')[0])
mutante('M8', 'orcamento substitui autorizacao', not compra(None)[0])
mutante('M9', 'politica substitui autorizacao',
        mz.decisao('YOUTUBE', 'FETCH_TRANSCRIPT')['DECISAO'] is not None and not compra(None)[0])
mutante('M10', 'NORMAL foge pela porta do TRIAL',
        ag.conferir(t_ok, custo='pago', livro=LIVRO,
                    source_id_pedido='IT-T9-001')['VEREDITO'] != OK)
mutante('M11', 'NORMAL foge pela porta do PROBE (fonte trocada)',
        ag.conferir(ag.probe(source_id='A-1', proposito='T3', humano='h', max_runs=1,
                             max_posts=1, max_usd=1, max_items=1, condicao_de_paragem='x'),
                    custo='pago', livro=LIVRO, source_id_pedido='B-2')['VEREDITO'] != OK)
mutante('M12', 'probe ilimitado',
        ag.conferir(dict(p_ok, MAX_USD=None), custo='pago', livro=LIVRO)['VEREDITO'] != OK)
mutante('M13', 'ensaio ilimitado',
        ag.conferir(dict(t_ok, MAX_PROVIDER_RUNS=None), custo='pago',
                    livro=LIVRO)['VEREDITO'] != OK)
mutante('M14', 'curl directo por fora da porta unica', len(saida) == 1)
mutante('M15', 'apify_pool compra sozinho',
        "metodo='POST'" not in open(os.path.join(RAIZ, 'ferramentas', 'apify_pool.py'),
                                    encoding='utf-8').read())
mutante('M16', 'coletor compra sem guarda', not compra(None)[0])
mutante('M17', 'credencial conferida DEPOIS da rede', len(pedidos) == 0)
mutante('M18', 'segundo POST permitido',
        'PostTalvezCriado' in open(os.path.join(RAIZ, 'coleta', 'coletor.py'),
                                   encoding='utf-8').read())
mutante('M19', 'guarda DEPOIS da reserva financeira', posicao_guarda < posicao_reserva)
mutante('M20', 'probe promove a fonte sozinho', len(LIVRO) == antes)

print('\nEXECUCAO REAL\n' + '-' * 72)
print('  APIFY_REAL_RUNS      = 0')
print('  META_REAL_REQUESTS   = 0')
print('  REAL_START_POSTS     = 0  (todo POST foi falso, no boundary)')
print('  COST_USD             = 0')

print('\n' + '=' * 72)
print('ATAQUES = %d · MUTANTES = %d · FALHAS = %d' % (ATAQUES, len(MUT), len(FALHAS)))
if FALHAS:
    for f in FALHAS:
        print('  !!', f)
    sys.exit(1)
print('RED_TEAM = PASS · SURVIVORS = 0')
