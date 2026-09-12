# -*- coding: utf-8 -*-
"""C10.8A-F — as sentinelas do teto de GASTO.

Todas medem COMPORTAMENTO. Uma sentinela que procurasse a palavra
`SemOrcamentoFinanceiro` no ficheiro passaria com um `raise` inalcançável — foi
assim que um mutante sobreviveu na C10.8A-R.

    UMA SENTINELA QUE PROCURA A PALAVRA NAO MEDE O QUE ELA FAZ.
"""
import ast
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import coletor as ct                                              # noqa: E402
import scrap_executor as sx                                       # noqa: E402
import scrap_http as http                                         # noqa: E402
import scrap_registo as reg                                       # noqa: E402
import social_envelope as env                                     # noqa: E402
import social_matriz as mz                                        # noqa: E402
reg.carregar_adaptadores()

PLAT, CAPAC = 'YOUTUBE', 'youtube.native_caption'
ATOR = 'fake~ator-pago-do-teste'
MOTIVO = 'FREE_ROUTE_UNAVAILABLE'
BRUTO = os.path.join(RAIZ, 'data/samples/SOCIAL-IT/raw-free/BLUESKY/'
                     'authorFeed-caasrl.bsky.social__07f7506618bbd2b6.txt')


def _fonte(rel):
    return io.open(os.path.join(RAIZ, rel), encoding='utf-8').read()


class _Resultado(object):
    def __init__(self, corpo, rc=0):
        self.returncode, self.stdout, self.stderr = rc, corpo, ''


class _Falso(object):
    """Substitui `subprocess.run` DENTRO do coletor — por BAIXO dos dois tetos."""

    def __init__(self, guiao):
        self.guiao, self.posts, self.gets = list(guiao), [], []

    def __call__(self, cmd, **k):
        url = cmd[-1]
        metodo = cmd[cmd.index('-X') + 1] if '-X' in cmd else 'GET'
        if metodo.upper() == 'POST':
            teto = None
            for parte in url.split('?', 1)[-1].split('&'):
                if parte.startswith('maxTotalChargeUsd='):
                    teto = float(parte.split('=', 1)[1])
            self.posts.append(teto)
            passo = (self.guiao[len(self.posts) - 1]
                     if len(self.guiao) >= len(self.posts) else 0.0)
            if isinstance(passo, Exception):
                return _Resultado('', rc=52)
            return _Resultado(json.dumps({'data': {
                'id': 'run-%d' % len(self.posts), 'status': 'SUCCEEDED',
                'startedAt': '2026-09-12T00:00:00.000Z',
                'finishedAt': '2026-09-12T00:00:05.000Z',
                'buildNumber': '0.0.1',
                'defaultDatasetId': 'ds-%d' % len(self.posts),
                'usageTotalUsd': passo}}))
        self.gets.append(url)
        if '/datasets/' in url:
            return _Resultado(json.dumps([{'id': 'item-1'}]))
        return _Resultado(json.dumps({'data': {'items': []}}))


class _Cenario(object):
    def __init__(self, guiao, *, teto_da_rota=None):
        self.falso, self.teto_da_rota = _Falso(guiao), teto_da_rota

    def rota(self, *, run_id, country_scope='IT', medida=None, **k):
        itens, man = ct.executar(
            ATOR, {'q': 1}, token='TOKEN-FALSO', run_id=run_id, platform=PLAT,
            country=country_scope, mission='C10-8A-F', query='teste',
            source_version='teste', evidence_path='data/samples/t.json',
            wait=60, salvar_raw=False, teto_usd=self.teto_da_rota)
        if medida is not None:
            r = man.get('FINANCIAL_RESERVATION') or {}
            medida['COST_STATE'] = r.get('COST_STATE', 'UNKNOWN')
            medida['ACTUAL_COST_USD'] = r.get('ACTUAL_COST_USD')
            medida['FINANCIAL_RESERVATION'] = r
        if man['STATUS'] == 'FAILED':
            raise RuntimeError(str(man.get('ERROR'))[:120])
        return itens

    def __enter__(self):
        self._run = ct.subprocess.run
        ct.subprocess.run = self.falso
        self._antes = dict(reg._MAPA[(PLAT, CAPAC)])
        reg._MAPA[(PLAT, CAPAC)] = dict(self._antes, ROTA=self.rota)
        return self

    def __exit__(self, *a):
        ct.subprocess.run = self._run
        reg._MAPA[(PLAT, CAPAC)] = self._antes
        return False


def _colher(*, gasto=None, rede=None, guiao=(0.0,), teto_da_rota=None,
            chamadas=1, modo=sx.NORMAL, permitir_pago=True):
    with _Cenario(guiao, teto_da_rota=teto_da_rota) as c:
        pedido = dict(platform=PLAT, capability=CAPAC, modo=modo,
                      permitir_pago=permitir_pago, motivo_pago=MOTIVO)
        if rede is not None:
            pedido['teto_de_rede'] = rede
        if chamadas == 1:
            if gasto is not None:
                pedido['teto_de_gasto'] = gasto
            return [sx.COLLECT(run_id='t-1', **pedido)], c.falso, None
        with ct.orcamento_financeiro(gasto) as orc:
            saidas = [sx.COLLECT(run_id='t-%d' % (i + 1), **pedido)
                      for i in range(chamadas)]
            return saidas, c.falso, orc


class _Resposta(object):
    def __init__(self, corpo, status=200):
        self._c, self.status, self._lido = corpo.encode('utf-8'), status, False

    def read(self, *a):
        if self._lido:
            return b''
        self._lido = True
        return self._c

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def close(self):
        pass


ROBOTS = '# Hello Friends!\nUser-agent: *\nAllow: /\n'


def _sem_rede(fn):
    """Corre `fn` com o TRANSPORTE falso — nao com `buscar` falso.

    Trocar `http.buscar` seria pousar o fake POR CIMA do portao do robots, do
    teto de rede e de qualquer reserva que `buscar` venha a fazer. Um mutante
    que metesse cobranca dentro de `buscar` sobreviveria — e sobreviveu, na
    primeira versao desta sentinela.

        UM FAKE QUE SUBSTITUI A FUNCAO MEDIDA MEDE O FAKE.
    """
    import urllib.request
    corpo = io.open(BRUTO, encoding='utf-8').read()
    real, gaveta = urllib.request.urlopen, env.RAW_DIR

    def falso(req, *a, **k):
        url = req.full_url if hasattr(req, 'full_url') else str(req)
        return _Resposta(ROBOTS if url.endswith('/robots.txt') else corpo)

    urllib.request.urlopen = falso
    http._ROBOTS.clear()
    env.RAW_DIR = tempfile.mkdtemp(prefix='t-c108af-')
    try:
        return fn()
    finally:
        urllib.request.urlopen = real
        http._ROBOTS.clear()
        shutil.rmtree(env.RAW_DIR, ignore_errors=True)
        env.RAW_DIR = gaveta


# ══════════════════════════════════════════════════════════════════════════
class OGateExisteEVemAntesDoProvider(unittest.TestCase):
    """M1 · M2 — um teto que cobra depois do provider conta o prejuízo."""

    def test_1_limite_zero_nao_chama_o_provider(self):
        saidas, falso, _o = _colher(gasto=0)
        self.assertEqual(falso.posts, [], 'um POST saiu com o saldo a zero')
        self.assertEqual(saidas[0][1].get('RESULT'), 'FINANCIAL_BUDGET_EXHAUSTED')

    def test_2_a_recusa_fica_no_rasto_como_recusa(self):
        saidas, _f, _o = _colher(gasto=0)
        self.assertEqual(saidas[0][1].get('FINANCIAL_CALLS_REFUSED'), 1)
        self.assertEqual(saidas[0][1].get('FINANCIAL_BUDGET_ACTUAL_USD'), 0.0)

    def test_3_uma_chamada_liquida_com_o_custo_real(self):
        saidas, falso, _o = _colher(gasto=1.00, guiao=(0.25,))
        t = saidas[0][1]
        self.assertEqual(len(falso.posts), 1)
        self.assertEqual(t['FINANCIAL_BUDGET_ACTUAL_USD'], 0.25)
        self.assertEqual(t['FINANCIAL_BUDGET_REMAINING_USD'], 0.75)


class OCapDoProviderCabeNoQueResta(unittest.TestCase):
    """M3 — a segunda chamada com o teto original é exposição a dobrar."""

    def test_4_a_segunda_chamada_recebe_o_remaining(self):
        saidas, falso, _o = _colher(gasto=1.00, guiao=(0.25, 0.10), chamadas=2)
        self.assertEqual(falso.posts[0], 1.00)
        self.assertAlmostEqual(falso.posts[1], 0.75, places=6)

    def test_5_o_pedido_do_chamador_e_rebaixado_nunca_elevado(self):
        saidas, falso, _o = _colher(gasto=0.30, guiao=(0.10,), teto_da_rota=5.00)
        self.assertAlmostEqual(falso.posts[0], 0.30, places=6)

    def test_6_um_pedido_menor_que_o_saldo_e_respeitado(self):
        saidas, falso, _o = _colher(gasto=1.00, guiao=(0.10,), teto_da_rota=0.05)
        self.assertAlmostEqual(falso.posts[0], 0.05, places=6)

    def test_7_esgotado_a_proxima_morre_antes_do_provider(self):
        saidas, falso, orc = _colher(gasto=0.30, guiao=(0.30, 0.10), chamadas=2)
        self.assertEqual(len(falso.posts), 1)
        self.assertEqual(saidas[1][1].get('RESULT'), 'FINANCIAL_BUDGET_EXHAUSTED')


class UnknownNaoEZero(unittest.TestCase):
    """M4 · M11 — devolver ao saldo o que talvez tenha saído paga duas vezes."""

    def test_8_post_perdido_vira_UNKNOWN_e_nao_volta(self):
        saidas, _f, _o = _colher(gasto=1.00,
                                 guiao=(ct.PostTalvezCriado('caiu'),))
        t = saidas[0][1]
        self.assertEqual(t['FINANCIAL_BUDGET_UNKNOWN_USD'], 1.00)
        self.assertEqual(t['FINANCIAL_BUDGET_REMAINING_USD'], 0.0)
        self.assertEqual(t['FINANCIAL_BUDGET_ACTUAL_USD'], 0.0)

    def test_9_custo_ilegivel_vira_UNKNOWN_e_nao_zero(self):
        saidas, _f, _o = _colher(gasto=1.00, guiao=(None,))
        t = saidas[0][1]
        self.assertEqual(t.get('COST_STATE'), ct.CUSTO_DESCONHECIDO)
        self.assertIsNone(t.get('ACTUAL_COST_USD'))
        self.assertEqual(t['FINANCIAL_BUDGET_UNKNOWN_USD'], 1.00)

    def test_10_os_tres_estados_nao_colapsam(self):
        _o, nao_correu = sx.COLLECT(platform='LINKEDIN',
                                    capability='linkedin.comments',
                                    run_id='t-notrun')
        self.assertEqual(nao_correu.get('COST_STATE'), 'NOT_RUN')
        self.assertIsNone(nao_correu.get('ACTUAL_COST_USD'))
        zero, _f, _o2 = _colher(gasto=1.00, guiao=(0.0,))
        self.assertEqual(zero[0][1].get('COST_STATE'), ct.CUSTO_LIDO)
        self.assertEqual(zero[0][1].get('ACTUAL_COST_USD'), 0.0)

    def test_11_o_custo_lido_nunca_se_diz_liquidado(self):
        saidas, _f, _o = _colher(gasto=1.00, guiao=(0.25,))
        self.assertEqual(saidas[0][1].get('COST_STATE'), 'READ_NOT_SETTLED')
        self.assertNotEqual(saidas[0][1].get('COST_STATE'), ct.CUSTO_LIQUIDADO)


class OProviderQueFuraOCap(unittest.TestCase):

    def test_12_cobrar_acima_do_cap_nao_e_sucesso_financeiro(self):
        saidas, _f, _o = _colher(gasto=1.00, teto_da_rota=0.20, guiao=(0.55,))
        tent = saidas[0][1]['FINANCIAL_ATTEMPTS'][0]
        self.assertEqual(tent['OUTCOME'], 'PROVIDER_EXCEEDED_CAP')
        self.assertAlmostEqual(tent['PROVIDER_CAP_BREACH_USD'], 0.35, places=6)
        self.assertEqual(saidas[0][1]['FINANCIAL_BUDGET_ACTUAL_USD'], 0.55)


class OQueNaoCustaNaoGasta(unittest.TestCase):
    """M7 · M8 — um teto de dinheiro que trava rota grátis é um teto errado."""

    def test_13_rota_gratuita_corre_com_saldo_zero(self):
        with ct.orcamento_financeiro(0) as orc:
            objetos, trace = _sem_rede(lambda: sx.COLLECT(
                platform='BLUESKY', capability='bluesky.author.incremental',
                run_id='t-free', handle='caasrl.bsky.social', limit=1))
        self.assertEqual(len(objetos), 1)
        self.assertEqual(orc.gasto, 0.0)
        self.assertEqual(trace.get('COST_STATE'), 'FREE_ROUTE_BY_POLICY')

    def test_14_reprocessar_bytes_locais_gasta_zero(self):
        # Sem fake nenhum: os dois tetos a zero sao os vigias. Um fake
        # instalado DEPOIS do teto de rede substituiria o proprio contador.
        with ct.orcamento_financeiro(0) as orc:
            with http.orcamento_de_rede(0) as orede:
                feed = json.loads(io.open(BRUTO, encoding='utf-8').read())
                objetos = [env.envelope(
                    platform='BLUESKY',
                    native_id=(i.get('post') or {}).get('uri'), url=None,
                    content_type='POST', route='reprocess',
                    executor='tests/test_c10_8af', run_id='t-r',
                    country_scope='IT') for i in (feed.get('feed') or [])]
        self.assertGreaterEqual(len(objetos), 1)
        self.assertEqual(orc.gasto, 0.0)
        self.assertEqual(orede.usados, 0)


class OSaldoEDaExecucao(unittest.TestCase):
    """M9 · M10 — reiniciar entre chamadas, ou vazar entre corridas."""

    def test_15_o_saldo_nao_reinicia_entre_chamadas(self):
        saidas, _f, orc = _colher(gasto=1.00, guiao=(0.40, 0.30), chamadas=2)
        self.assertAlmostEqual(orc.gasto, 0.70, places=6)
        self.assertAlmostEqual(orc.restante, 0.30, places=6)

    def test_16_duas_execucoes_nao_partilham_saldo(self):
        a, _f1, _o1 = _colher(gasto=1.00, guiao=(0.40,))
        b, _f2, _o2 = _colher(gasto=2.00, guiao=(0.40,))
        self.assertEqual(a[0][1]['FINANCIAL_BUDGET_AUTHORIZED_USD'], 1.00)
        self.assertEqual(b[0][1]['FINANCIAL_BUDGET_AUTHORIZED_USD'], 2.00)
        self.assertEqual(b[0][1]['FINANCIAL_BUDGET_ACTUAL_USD'], 0.40)

    def test_17_fora_do_bloco_nao_ha_orcamento(self):
        with ct.orcamento_financeiro(1.0):
            self.assertIsNotNone(ct.orcamento_financeiro_actual())
        self.assertIsNone(ct.orcamento_financeiro_actual())

    def test_18_o_saldo_nao_e_global_de_processo(self):
        self.assertFalse(
            [n for n in dir(ct) if n.isupper() and 'ORCAMENTO' in n
             and not n.startswith('_')],
            'nasceu um saldo global de modulo')


class AConcorrenciaFoiMedida(unittest.TestCase):

    def test_19_as_portas_pagas_de_hoje_sao_seriais(self):
        arranca = ('Thread', 'ThreadPoolExecutor', 'ProcessPoolExecutor',
                   'Pool', 'Process', 'gather', 'create_task')
        for mod in ('coleta/coletor.py', 'coleta/instagram_coleta.py',
                    'regras/sensor_coleta.py', 'coleta/comunicacao_coleta.py'):
            arv = ast.parse(_fonte(mod))
            achados = {getattr(n.func, 'attr', None) or getattr(n.func, 'id', None)
                       for n in ast.walk(arv) if isinstance(n, ast.Call)}
            self.assertFalse(achados & set(arranca),
                             '%s passou a arrancar execucao concorrente' % mod)

    def test_20_duas_reservas_simultaneas_nao_passam_do_teto(self):
        orc = ct.OrcamentoFinanceiro(1.00)
        barreira, vistos, trava = threading.Barrier(2), [], threading.Lock()

        def atacar():
            barreira.wait()
            try:
                r = orc.reservar(pedido=0.80, ator='ataque')
            except ct.SemOrcamentoFinanceiro:
                r = None
            with trava:
                vistos.append(r)

        fios = [threading.Thread(target=atacar) for _ in range(2)]
        for f in fios:
            f.start()
        for f in fios:
            f.join()
        ganhos = [v for v in vistos if v is not None]
        self.assertAlmostEqual(sum(g.cap for g in ganhos), 1.00, places=6)
        self.assertLessEqual(orc.comprometido, 1.00)


class OsDoisGatesSaoDois(unittest.TestCase):
    """M5 · M6 — um eixo a responder pelo outro."""

    def test_21_a_matriz_dos_dois_tetos(self):
        for rede, dinheiro, esperado in ((2, 0, False), (0, 1.00, False),
                                         (2, 1.00, True), (0, 0, False)):
            with self.subTest(rede=rede, dinheiro=dinheiro):
                _s, falso, _o = _colher(gasto=dinheiro, rede=rede, guiao=(0.10,))
                self.assertEqual(bool(falso.posts), esperado)

    def test_22_autorizar_gasto_nao_declara_ate_quanto(self):
        saidas, falso, _o = _colher(gasto=0.50, guiao=(0.10,),
                                    permitir_pago=False)
        self.assertEqual(falso.posts, [])
        self.assertEqual(saidas[0][1]['ROUTER_RECORD']['ESTADO_ORIGINAL'],
                         'PAID_ROUTE_REFUSED')

    def test_23_teto_declarado_nao_dispensa_motivo_canonico(self):
        with _Cenario((0.10,)) as c:
            _o, trace = sx.COLLECT(platform=PLAT, capability=CAPAC, run_id='t-m',
                                   teto_de_gasto=1.00, permitir_pago=True,
                                   motivo_pago='porque sim')
        self.assertEqual(c.falso.posts, [])
        self.assertEqual(trace['ROUTER_RECORD']['ESTADO_ORIGINAL'],
                         'PAID_ROUTE_REFUSED')

    def test_24_o_teto_de_rede_continua_a_nao_conhecer_dinheiro(self):
        fonte = _fonte('coleta/scrap_http.py')
        classe = next(n for n in ast.walk(ast.parse(fonte))
                      if isinstance(n, ast.ClassDef) and n.name == 'OrcamentoDeRede')
        texto = ast.get_source_segment(fonte, classe) or ''
        for proibido in ('USD', 'custo', 'permitir_pago', 'motivo_pago'):
            self.assertNotIn(proibido, texto)

    def test_25_e_o_teto_de_gasto_nao_conta_pedidos(self):
        fonte = _fonte('coleta/coletor.py')
        classe = next(n for n in ast.walk(ast.parse(fonte))
                      if isinstance(n, ast.ClassDef)
                      and n.name == 'OrcamentoFinanceiro')
        texto = ast.get_source_segment(fonte, classe) or ''
        for proibido in ('urlopen', 'create_connection', 'NETWORK_REQUESTS'):
            self.assertNotIn(proibido, texto)


class UmEnsaioPagoSemTetoNaoComeca(unittest.TestCase):

    def test_26_trial_com_rota_paga_exige_teto_de_gasto(self):
        saidas, falso, _o = _colher(gasto=None, guiao=(0.10,), modo=sx.TRIAL)
        self.assertEqual(falso.posts, [])
        self.assertEqual(saidas[0][1].get('RESULT'),
                         'PAID_TRIAL_WITHOUT_FINANCIAL_BUDGET')

    def test_27_e_com_teto_o_ensaio_corre(self):
        saidas, falso, _o = _colher(gasto=1.00, guiao=(0.10,), modo=sx.TRIAL)
        self.assertEqual(len(falso.posts), 1)

    def test_28_em_NORMAL_o_caminho_historico_nao_muda(self):
        saidas, falso, _o = _colher(gasto=None, guiao=(0.10,), modo=sx.NORMAL)
        self.assertEqual(len(falso.posts), 1)
        self.assertIsNone(falso.posts[0],
                          'sem teto declarado passou a ir maxTotalChargeUsd')

    def test_29_rota_gratuita_em_TRIAL_nao_exige_teto(self):
        with ct.orcamento_financeiro(0):
            objetos, trace = _sem_rede(lambda: sx.COLLECT(
                platform='BLUESKY', capability='bluesky.author.incremental',
                run_id='t-trial-free', handle='caasrl.bsky.social', limit=1,
                modo=sx.TRIAL))
        self.assertNotEqual(trace.get('RESULT'),
                            'PAID_TRIAL_WITHOUT_FINANCIAL_BUDGET')


class ARecusaChegaComNomeProprio(unittest.TestCase):
    """M13 — um `except` largo a vestir a nossa recusa de fonte indisponível."""

    def test_30_a_recusa_financeira_nao_vira_outro_estado(self):
        saidas, _f, _o = _colher(gasto=0)
        r = saidas[0][1].get('RESULT')
        self.assertEqual(r, 'FINANCIAL_BUDGET_EXHAUSTED')
        for errado in ('SOURCE_UNAVAILABLE', 'BLOCKED', 'ZERO_RESULTS',
                       'UNKNOWN_ERROR', 'NETWORK_BUDGET_EXHAUSTED'):
            self.assertNotEqual(r, errado)

    def test_31_a_recusa_de_rede_no_caminho_pago_nao_vira_FAILED(self):
        saidas, falso, _o = _colher(gasto=1.00, rede=0, guiao=(0.10,))
        self.assertEqual(falso.posts, [])
        self.assertEqual(saidas[0][1].get('RESULT'), 'NETWORK_BUDGET_EXHAUSTED')

    def test_32_e_o_dinheiro_reservado_volta_quando_o_POST_nao_saiu(self):
        with _Cenario((0.10,)) as c:
            with http.orcamento_de_rede(0):
                with ct.orcamento_financeiro(1.00) as orc:
                    _o, _t = sx.COLLECT(platform=PLAT, capability=CAPAC,
                                        run_id='t-rede0', permitir_pago=True,
                                        motivo_pago=MOTIVO)
        self.assertEqual(c.falso.posts, [])
        self.assertEqual(orc.restante, 1.00,
                         'o POST provadamente nao saiu e o dinheiro nao voltou')
        self.assertEqual(orc.desconhecido, 0.0)

    def test_33_os_dois_tetos_falam_a_lingua_canonica(self):
        import falhas
        for estado in ('FINANCIAL_BUDGET_EXHAUSTED', 'NETWORK_BUDGET_EXHAUSTED',
                       'PAID_TRIAL_WITHOUT_FINANCIAL_BUDGET'):
            self.assertEqual(falhas.traduzir(estado), 'BUDGET_EXHAUSTED', estado)
            self.assertEqual(falhas.recuperacao('BUDGET_EXHAUSTED'), 'NO_RETRY')


class ORastoNaoMente(unittest.TestCase):
    """M12 — um rasto que declara o que não mediu."""

    def test_34_o_rasto_bate_com_o_que_saiu(self):
        for limite, custo in ((1.00, 0.25), (0.50, 0.50), (2.00, 0.0)):
            with self.subTest(limite=limite):
                saidas, _f, _o = _colher(gasto=limite, guiao=(custo,))
                t = saidas[0][1]
                self.assertEqual(t['FINANCIAL_BUDGET_ACTUAL_USD'], custo)
                self.assertAlmostEqual(
                    t['FINANCIAL_BUDGET_REMAINING_USD'], limite - custo, places=6)
                self.assertEqual(t['FINANCIAL_BUDGET_EXHAUSTED'],
                                 limite - custo <= 0)

    def test_35_os_sete_conceitos_estao_no_rasto(self):
        saidas, _f, _o = _colher(gasto=1.00, guiao=(0.25,))
        for campo in ('FINANCIAL_BUDGET_AUTHORIZED_USD',
                      'FINANCIAL_BUDGET_COMMITTED_USD',
                      'FINANCIAL_BUDGET_ACTUAL_USD',
                      'FINANCIAL_BUDGET_UNKNOWN_USD',
                      'FINANCIAL_BUDGET_REMAINING_USD',
                      'FINANCIAL_BUDGET_EXHAUSTED', 'FINANCIAL_CALLS_REFUSED',
                      'FINANCIAL_ATTEMPTS'):
            self.assertIn(campo, saidas[0][1])
        t = saidas[0][1]['FINANCIAL_ATTEMPTS'][0]
        for campo in ('PROVIDER', 'ACTOR', 'MOTIVO_PAGO', 'PROVIDER_SIDE_CAP',
                      'OUTCOME', 'COST_STATE', 'ACTUAL_COST_USD'):
            self.assertIn(campo, t)

    def test_36_sem_teto_o_rasto_nao_inventa_um(self):
        saidas, _f, _o = _colher(gasto=None, guiao=(0.25,))
        for campo in ('FINANCIAL_BUDGET_AUTHORIZED_USD',
                      'FINANCIAL_BUDGET_REMAINING_USD', 'FINANCIAL_ATTEMPTS'):
            self.assertNotIn(campo, saidas[0][1])

    def test_37_o_rasto_nao_leva_o_token(self):
        saidas, _f, _o = _colher(gasto=1.00, guiao=(0.25,))
        self.assertNotIn('TOKEN-FALSO', json.dumps(saidas[0][1], default=str))


class OCensoQueDecidiuODono(unittest.TestCase):

    def test_38_um_unico_POST_compromete_dinheiro_nesta_casa(self):
        achados = []
        for raiz, _d, ficheiros in os.walk(RAIZ):
            if any(x in raiz for x in ('/.git', '/node_modules', '/tests',
                                       '/provas', '__pycache__')):
                continue
            for f in ficheiros:
                if not f.endswith('.py'):
                    continue
                caminho = os.path.join(raiz, f)
                try:
                    arv = ast.parse(io.open(caminho, encoding='utf-8').read())
                except (SyntaxError, UnicodeDecodeError):
                    continue
                for n in ast.walk(arv):
                    # `metodo='POST'` — o CAMPO, e nao so o valor. A primeira
                    # versao desta sonda procurava a string `POST` em qualquer
                    # argumento e acusou `adaptador_aberto.py`, onde ela e o
                    # GRAO do conteudo («um post do Mastodon») e nao um metodo.
                    #
                    #     O VALOR SEM O NOME DO CAMPO E OUTRA COISA.
                    if (isinstance(n, ast.Call) and any(
                            kw.arg == 'metodo'
                            and isinstance(kw.value, ast.Constant)
                            and str(kw.value.value).upper() == 'POST'
                            for kw in n.keywords)):
                        achados.append(os.path.relpath(caminho, RAIZ))
        self.assertEqual(sorted(set(achados)), ['coleta/coletor.py'],
                         'nasceu uma segunda porta que compromete dinheiro: %s'
                         % sorted(set(achados)))

    def test_39_nenhuma_capacidade_paga_tem_adaptador_hoje(self):
        import scrap_capacidades as cap
        com = []
        for nome, d in cap.DECLARADAS.items():
            rotas = (mz.MATRIZ.get(d[0]) or {}).get(cap.da_matriz(nome))
            esc = mz._rota_padrao(rotas) if rotas else None
            if (esc and esc['CLASSE'] in ('APIFY', 'OFFICIAL_API_PAID')
                    and reg.rota_de(d[0], nome)):
                com.append(nome)
        self.assertEqual(com, [],
                         'uma rota paga ganhou adaptador sem passar pela C10.8B: %s'
                         % com)

    def test_40_a_prova_usa_o_contrato_real_e_nao_um_teto_proprio(self):
        fonte = _fonte('provas/orcamento_financeiro.py')
        self.assertIn('teto_de_gasto', fonte)
        self.assertIn('ct.subprocess.run', fonte,
                      'a prova voltou a trocar `_curl` — o fake ficaria ACIMA '
                      'do gate de rede')


if __name__ == '__main__':
    unittest.main(verbosity=2)
