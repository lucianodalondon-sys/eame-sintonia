#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.8A-R — O TETO DE ACESSOS EXTERNOS.

A C10.8A declarou `MAX_REAL_HTTP_REQUESTS = 2` e fez sete. O teto existia — numa
variavel de um script de prova. Quando a sonda rebentou e foi preciso repetir,
o teto repetiu-se com ela, zerado.

    UM TETO QUE VIVE NA PROVA MEDE A PROVA.
    DECLARED BUDGET != ENFORCED BUDGET.

E o censo desta missao mediu por que um contador em `scrap_http.buscar` nao
serviria: as catorze capacidades ligadas saem para a rede por TRES portas —
`scrap_http`, `reel_transcricao.baixar` e `cdp` — e so cinco passam pela
primeira. Um teto que cobre metade das portas e uma sugestao.

Nenhum destes testes toca a rede.
"""
import ast
import io
import json
import os
import socket
import sys
import unittest
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import scrap_executor as sx       # noqa: E402
import scrap_http as http         # noqa: E402
import scrap_registo as reg       # noqa: E402
import social_envelope as env     # noqa: E402
reg.carregar_adaptadores()

RAW = ('data/samples/SOCIAL-IT/raw-free/BLUESKY/'
       'authorFeed-caasrl.bsky.social__07f7506618bbd2b6.txt')


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


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


class _Falso(object):
    """O transporte falso, POR BAIXO do teto: ele conta o que realmente saiu."""

    def __init__(self, guiao=()):
        self.guiao, self.chegaram = list(guiao), []

    def __call__(self, req, *a, **k):
        self.chegaram.append(req.full_url if hasattr(req, 'full_url') else str(req))
        efeito = (self.guiao.pop(0) if self.guiao
                  else _Resposta(json.dumps({'feed': []})))
        if isinstance(efeito, Exception):
            raise efeito
        return efeito


class _Cenario(object):
    """Instala o falso por baixo, tranca o socket e desvia a gaveta do RAW."""

    def __init__(self, guiao=()):
        self.falso = _Falso(guiao)

    def __enter__(self):
        import shutil
        import tempfile
        self._shutil = shutil
        http._ROBOTS.clear()
        self._urlopen = urllib.request.urlopen
        self._conectar = socket.create_connection
        self._raw = env.RAW_DIR
        env.RAW_DIR = tempfile.mkdtemp(prefix='t108ar-')
        urllib.request.urlopen = self.falso
        socket.create_connection = lambda *a, **k: (_ for _ in ()).throw(
            RuntimeError('SAIDA DE REDE REAL num teste'))
        return self.falso

    def __exit__(self, *a):
        urllib.request.urlopen = self._urlopen
        socket.create_connection = self._conectar
        self._shutil.rmtree(env.RAW_DIR, ignore_errors=True)
        env.RAW_DIR = self._raw
        http._ROBOTS.clear()
        return False


def _robots():
    return _Resposta('User-agent: *\nAllow: /\n')


def _feed():
    return _Resposta(_fonte(RAW))


def _colher(limite, guiao, **kw):
    with _Cenario(guiao) as falso:
        pedido = dict(platform='BLUESKY', capability='bluesky.author.incremental',
                      run_id='T', modo=sx.TRIAL, handle='x.bsky.social',
                      limit=1, country_scope='IT')
        pedido.update(kw)
        if limite is not None:
            pedido['teto_de_rede'] = limite
        objetos, trace = sx.COLLECT(**pedido)
    return objetos, trace, falso


class OTetoRecusaAntesDaRede(unittest.TestCase):
    """UM TETO QUE NAO RECUSA NAO E UM TETO."""

    def test_1_limite_zero_nao_deixa_sair_nada(self):
        objetos, trace, falso = _colher(0, [_robots(), _feed()])
        self.assertEqual(falso.chegaram, [], 'saiu pedido com limite 0')
        self.assertEqual(objetos, [])
        self.assertEqual(trace['NETWORK_REQUESTS_USED'], 0)

    def test_2_a_tentativa_n_mais_um_morre_antes_do_socket(self):
        objetos, trace, falso = _colher(1, [_robots(), _feed()])
        self.assertEqual(len(falso.chegaram), 1,
                         'a segunda chegou ao transporte')
        self.assertTrue(falso.chegaram[0].endswith('/robots.txt'))
        self.assertTrue(trace['NETWORK_BUDGET_EXHAUSTED'])
        recusadas = [t for t in trace['NETWORK_ATTEMPTS']
                     if t['OUTCOME'] == 'REFUSED_BY_BUDGET']
        self.assertEqual(len(recusadas), 1)
        self.assertFalse(recusadas[0]['COUNTED'],
                         'a recusada foi contada como usada')

    def test_3_o_gate_e_antes_e_nao_depois(self):
        """Cobrar depois da chamada e contar o prejuizo."""
        fonte = _fonte('coleta/scrap_http.py')
        arv = ast.parse(fonte)
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'orcamento_de_rede')
        for interno in ('urlopen_com_teto', 'conectar_com_teto'):
            g = next(n for n in ast.walk(fn) if isinstance(n, ast.FunctionDef)
                     and n.name == interno)
            reservas = [n.lineno for n in ast.walk(g) if isinstance(n, ast.Call)
                        and getattr(n.func, 'attr', None) == 'reservar']
            chamadas = [n.lineno for n in ast.walk(g) if isinstance(n, ast.Call)
                        and getattr(n.func, 'id', None) in ('urlopen_real',
                                                            'conectar_real')]
            with self.subTest(guarda=interno):
                self.assertTrue(reservas and chamadas)
                self.assertLess(min(reservas), max(chamadas),
                                '%s cobra depois de chamar' % interno)

    def test_4_limite_dois_colhe(self):
        objetos, trace, falso = _colher(2, [_robots(), _feed()])
        self.assertEqual(len(falso.chegaram), 2)
        self.assertEqual(len(objetos), 1)
        # `esgotado` quer dizer «nao sobra nenhum», e a 2 de 2 nao sobra mesmo.
        # A colheita correu na mesma: gastar tudo nao e falhar.
        self.assertTrue(trace['NETWORK_BUDGET_EXHAUSTED'])
        self.assertEqual(trace['NETWORK_REQUESTS_REMAINING'], 0)
        self.assertEqual(trace['NETWORK_REQUESTS_REFUSED'], 0)


class TudoOQueSaiConta(unittest.TestCase):

    def test_5_o_robots_conta(self):
        _o, trace, falso = _colher(2, [_robots(), _feed()])
        tipos = [t['TYPE'] for t in trace['NETWORK_ATTEMPTS']]
        self.assertEqual(tipos, [http.PEDIDO_ROBOTS, http.PEDIDO_ROTA])
        self.assertEqual(trace['NETWORK_REQUESTS_USED'], 2)

    def test_6_um_pedido_sem_etiqueta_conta_na_mesma(self):
        """UM PEDIDO QUE NINGUEM CLASSIFICOU NAO E UM QUE NAO ACONTECEU."""
        with _Cenario([_Resposta('{}')]) as falso:
            with http.orcamento_de_rede(1) as orc:
                urllib.request.urlopen(
                    urllib.request.Request('https://exemplo.tld/qualquer'))
        self.assertEqual(orc.usados, 1)
        self.assertEqual(orc.tentativas[0]['TYPE'], http.PEDIDO_DESCONHECIDO)

    def test_7_a_retentativa_e_o_diagnostico_contam(self):
        for tipo in (http.PEDIDO_RETENTATIVA, http.PEDIDO_DIAGNOSTICO,
                     http.PEDIDO_ALTERNATIVA):
            with self.subTest(tipo=tipo):
                with _Cenario([_Resposta('{}')]) as falso:
                    with http.orcamento_de_rede(1) as orc:
                        p = urllib.request.Request('https://exemplo.tld/x')
                        p.tipo_de_pedido = tipo
                        urllib.request.urlopen(p)
                        q = urllib.request.Request('https://exemplo.tld/y')
                        q.tipo_de_pedido = tipo
                        with self.assertRaises(http.SemOrcamentoDeRede):
                            urllib.request.urlopen(q)
                self.assertEqual(len(falso.chegaram), 1)

    def test_8_um_pedido_que_falhou_conta(self):
        """Um 500 gastou a ida. Nao contar seria pagar o bilhete duas vezes."""
        with _Cenario([urllib.error.HTTPError('u', 500, 'x', {}, None)]) as falso:
            with http.orcamento_de_rede(2) as orc:
                try:
                    urllib.request.urlopen(
                        urllib.request.Request('https://exemplo.tld/x'))
                except urllib.error.HTTPError:
                    pass
        self.assertEqual(orc.usados, 1)
        self.assertEqual(orc.tentativas[0]['OUTCOME'], 'HTTPError')

    def test_9_um_timeout_conta(self):
        with _Cenario([TimeoutError('nada')]) as falso:
            with http.orcamento_de_rede(2) as orc:
                try:
                    urllib.request.urlopen(
                        urllib.request.Request('https://exemplo.tld/x'))
                except TimeoutError:
                    pass
        self.assertEqual(orc.usados, 1)

    def test_10_o_socket_cru_tambem_conta(self):
        """`cdp` abre ligacao por `socket.create_connection`, sem passar por
        `scrap_http`. Um teto que so olha para `urlopen` deixa-a de fora."""
        chamadas = []
        real = socket.create_connection
        socket.create_connection = lambda *a, **k: chamadas.append(a) or object()
        try:
            with http.orcamento_de_rede(1) as orc:
                socket.create_connection(('exemplo.tld', 443))
                with self.assertRaises(http.SemOrcamentoDeRede):
                    socket.create_connection(('exemplo.tld', 443))
        finally:
            socket.create_connection = real
        self.assertEqual(len(chamadas), 1)
        self.assertEqual(orc.usados, 1)

    def test_11_uma_ida_nao_conta_duas_vezes(self):
        """`urlopen` abre um socket por dentro. Isso e UM pedido, nao dois."""
        real = socket.create_connection

        def urlopen_que_abre_socket(req, *a, **k):
            socket.create_connection(('exemplo.tld', 443))
            return _Resposta('{}')
        with _Cenario([]) as falso:
            socket.create_connection = lambda *a, **k: object()
            urllib.request.urlopen = urlopen_que_abre_socket
            try:
                with http.orcamento_de_rede(2) as orc:
                    urllib.request.urlopen(
                        urllib.request.Request('https://exemplo.tld/x'))
            finally:
                socket.create_connection = real
        self.assertEqual(orc.usados, 1, 'a mesma ida foi cobrada duas vezes')


class OTetoEDaExecucao(unittest.TestCase):
    """Um contador global de processo faria uma corrida herdar a divida de outra."""

    def test_12_duas_execucoes_nao_partilham_contador(self):
        _o1, t1, _f1 = _colher(2, [_robots(), _feed()])
        _o2, t2, f2 = _colher(2, [_robots(), _feed()])
        self.assertEqual(t1['NETWORK_REQUESTS_USED'], 2)
        self.assertEqual(t2['NETWORK_REQUESTS_USED'], 2)
        self.assertEqual(len(f2.chegaram), 2,
                         'a segunda execucao herdou a divida da primeira')

    def test_13_fora_do_bloco_nao_ha_orcamento(self):
        self.assertIsNone(http.orcamento_actual())
        with http.orcamento_de_rede(1):
            self.assertIsNotNone(http.orcamento_actual())
        self.assertIsNone(http.orcamento_actual())

    def test_14_o_teto_e_total_e_nao_por_host(self):
        with _Cenario([_Resposta('{}'), _Resposta('{}')]) as falso:
            with http.orcamento_de_rede(2) as orc:
                for host in ('a.tld', 'b.tld'):
                    urllib.request.urlopen(
                        urllib.request.Request('https://%s/x' % host))
                with self.assertRaises(http.SemOrcamentoDeRede):
                    urllib.request.urlopen(
                        urllib.request.Request('https://c.tld/x'))
        self.assertEqual(len(falso.chegaram), 2)
        self.assertEqual({t['TARGET'] for t in orc.tentativas if t['COUNTED']},
                         {'a.tld', 'b.tld'})

    def test_15_o_transporte_e_devolvido_mesmo_a_rebentar(self):
        antes = urllib.request.urlopen
        try:
            with http.orcamento_de_rede(1):
                raise RuntimeError('rebentou')
        except RuntimeError:
            pass
        self.assertIs(urllib.request.urlopen, antes,
                      'o teto ficou instalado depois de uma excecao')


class OQueNaoContaNaoConta(unittest.TestCase):

    def test_16_reprocessar_bytes_locais_gasta_zero(self):
        import shutil
        import tempfile
        corpo = _fonte(RAW)
        buscar, raw = http.buscar, env.RAW_DIR
        http.buscar = lambda *a, **k: corpo
        env.RAW_DIR = tempfile.mkdtemp(prefix='t108ar-r-')
        try:
            with http.orcamento_de_rede(2) as orc:
                objetos = reg.rota_de('BLUESKY', 'bluesky.author.incremental')(
                    handle='x', limit=1, run_id='T-R', country_scope='IT',
                    medida={})
        finally:
            http.buscar = buscar
            shutil.rmtree(env.RAW_DIR, ignore_errors=True)
            env.RAW_DIR = raw
        self.assertEqual(orc.usados, 0)
        self.assertEqual(len(objetos), 1)

    def test_17_o_CHECK_nao_gasta_orcamento(self):
        with http.orcamento_de_rede(1) as orc:
            sx.CHECK('BLUESKY', 'bluesky.author.incremental')
            sx.CAPABILITIES()
        self.assertEqual(orc.usados, 0)


class OsDoisEixosNaoSeMisturam(unittest.TestCase):
    """PAID BUDGET != NETWORK BUDGET."""

    def test_18_autorizar_gasto_nao_compra_pedidos(self):
        _o, trace, falso = _colher(1, [_robots(), _feed()],
                                   permitir_pago=True,
                                   motivo_pago='FREE_ROUTE_UNAVAILABLE')
        self.assertEqual(len(falso.chegaram), 1)
        self.assertTrue(trace['NETWORK_BUDGET_EXHAUSTED'])

    def test_19_o_teto_de_rede_nao_conhece_dinheiro(self):
        fonte = _fonte('coleta/scrap_http.py')
        arv = ast.parse(fonte)
        classe = next(n for n in ast.walk(arv) if isinstance(n, ast.ClassDef)
                      and n.name == 'OrcamentoDeRede')
        texto = ast.get_source_segment(fonte, classe) or ''
        for proibido in ('USD', 'custo', 'permitir_pago', 'motivo_pago'):
            self.assertNotIn(proibido, texto,
                             'o teto de rede passou a conhecer dinheiro: %s'
                             % proibido)


class ORastoBateComOQueSaiu(unittest.TestCase):

    def test_20_o_contador_do_runtime_bate_com_o_transporte(self):
        for limite in (0, 1, 2, 3):
            with self.subTest(limite=limite):
                _o, trace, falso = _colher(limite, [_robots(), _feed()])
                self.assertEqual(trace['NETWORK_REQUESTS_USED'],
                                 len(falso.chegaram),
                                 'o rasto diz %s e sairam %d'
                                 % (trace['NETWORK_REQUESTS_USED'],
                                    len(falso.chegaram)))

    def test_21_o_rasto_nao_leva_query_nem_segredo(self):
        with _Cenario([_Resposta('{}')]) as falso:
            with http.orcamento_de_rede(1) as orc:
                urllib.request.urlopen(urllib.request.Request(
                    'https://exemplo.tld/x?token=SEGREDO&q=1'))
        alvo = orc.tentativas[0]['TARGET']
        self.assertEqual(alvo, 'exemplo.tld')
        self.assertNotIn('SEGREDO', json.dumps(orc.para_o_rasto()))

    def test_22_esgotar_o_orcamento_nao_vira_ZERO_RESULTS(self):
        _o, trace, _f = _colher(1, [_robots(), _feed()])
        self.assertNotEqual(trace.get('RESULT'), 'ZERO_RESULTS')
        self.assertEqual(trace.get('RESULT'), 'NETWORK_BUDGET_EXHAUSTED')

    def test_23_sem_teto_o_rasto_nao_inventa_um(self):
        _o, trace, _f = _colher(None, [_robots(), _feed()])
        for campo in ('NETWORK_BUDGET_LIMIT', 'NETWORK_REQUESTS_USED',
                      'NETWORK_ATTEMPTS'):
            self.assertNotIn(campo, trace)


class AProvaDaC108AUsaOContratoReal(unittest.TestCase):

    def test_24_a_prova_passa_o_teto_ao_runtime(self):
        fonte = _fonte('provas/bluesky_trial_ao_vivo.py')
        self.assertIn('teto_de_rede=MAX_PEDIDOS', fonte,
                      'a prova voltou a ter teto so dela')
        self.assertIn("trace.get('NETWORK_REQUESTS_USED')", fonte,
                      'a prova deixou de conferir o contador do runtime')

    def test_25_o_documento_da_C108A_corrigiu_o_veredito(self):
        doc = _fonte('docs/sintonia-scrap/C10-8A-BLUESKY-LIVE-TRIAL.md')
        self.assertIn('C10_8A_BLUESKY_LIVE_TRIAL              = FAIL', doc)
        self.assertIn('BLUESKY_AUTHOR_INCREMENTAL_CAPABILITY  = PROVEN', doc)
        self.assertIn('sete', doc, 'o documento deixou de contar as sete idas')
        self.assertNotIn('`C10_8A_BLUESKY_LIVE_TRIAL = PASS_PROVEN`', doc)

    def test_26_a_capacidade_continua_provada(self):
        import scrap_capacidades as cap
        self.assertEqual(cap.estado('bluesky.author.incremental'), 'PROVEN')
        self.assertIn('C10-8A', cap.prova('bluesky.author.incremental'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
