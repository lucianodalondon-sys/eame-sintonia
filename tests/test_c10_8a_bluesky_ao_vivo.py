#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.8A — O PRIMEIRO TRIAL AO VIVO, E O QUE ELE ENCONTROU.

A C10.7 construiu o ensaio canonico e provou-o com fornecedor falso. Esta
missao correu-o contra o Bluesky de verdade — duas requisicoes, um objeto — e a
primeira tentativa encontrou um defeito que nenhuma fixture encontraria:

    UM TRANSPORTE QUE CAIU NAO E UMA POLITICA QUE RECUSOU.

O tunel morreu a meio da leitura do `robots.txt`. O portao nao tinha palavra
para isso: caia em `ILEGIVEL`, que vira `False`, que o roteador traduz para
`ROUTE_NOT_ALLOWED`. E o `robots.txt` daquele host, lido a seguir, diz
`Allow: /` e escreve, em ingles, «Crawling the public parts of the API is
allowed».

`ROUTE_NOT_ALLOWED` pede `NO_RETRY`. `TRANSIENT_NETWORK_ERROR` pede `WAIT`.
Chamar a primeira pela segunda ensina a casa a desistir de uma porta aberta.

Estes testes correm todos sobre os BYTES PRESERVADOS. Nenhum toca a rede.
"""
import ast
import io
import json
import os
import re
import socket
import sys
import unittest
import urllib.error

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import falhas as fx                # noqa: E402
import scrap_capacidades as cap    # noqa: E402
import scrap_executor as sx        # noqa: E402
import scrap_http as http          # noqa: E402
import scrap_registo as reg        # noqa: E402
import social_matriz as mz         # noqa: E402
import social_rotas as sr          # noqa: E402
reg.carregar_adaptadores()

PLATAFORMA, CAPACIDADE = 'BLUESKY', 'bluesky.author.incremental'
ALVO = 'caasrl.bsky.social'
RAW = ('data/samples/SOCIAL-IT/raw-free/BLUESKY/'
       'authorFeed-caasrl.bsky.social__07f7506618bbd2b6.txt')
CORRIDA = 'provas/_c108a_ultima_corrida.json'


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


class _SemRede(object):
    """Tranca a rede e conta tentativas. Um teste que PODE sair nao prova zero."""

    def __enter__(self):
        self.tentativas = 0
        self._original = socket.socket
        pai, self_ = self._original, self

        class Trancado(pai):
            def __init__(s, *a, **k):
                self_.tentativas += 1
                raise RuntimeError('SAIDA DE REDE num teste offline')
        socket.socket = Trancado
        return self

    def __exit__(self, *a):
        socket.socket = self._original
        return False


class OPortaoDistingueQuedaDeRecusa(unittest.TestCase):
    """O achado desta missao. Medido ao vivo, provado offline."""

    def setUp(self):
        http._ROBOTS.clear()

    def tearDown(self):
        http._ROBOTS.clear()

    def _com_robots(self, efeito):
        original = http.urllib.request.urlopen

        def falso(req, *a, **k):
            if isinstance(efeito, Exception):
                raise efeito
            return efeito
        http.urllib.request.urlopen = falso
        try:
            return http.permitido('https://exemplo.tld/x')
        finally:
            http.urllib.request.urlopen = original

    def test_1_transporte_caido_nao_e_recusa(self):
        for morte in (urllib.error.URLError('reset'), ConnectionResetError(104, 'x'),
                      TimeoutError('nada'), OSError('nada')):
            with self.subTest(morte=type(morte).__name__):
                http._ROBOTS.clear()
                with self.assertRaises(http.PortaoIndisponivel):
                    self._com_robots(morte)

    def test_2_resposta_ilegivel_continua_a_ser_recusa(self):
        """O controlo negativo. O host RESPONDEU e nos nao percebemos — isso
        continua a ser «nao afirmamos permissao que nao lemos»."""
        http._ROBOTS.clear()
        with self.assertRaises(http.PortaoIndisponivel):
            self._com_robots(urllib.error.URLError('reset'))
        http._ROBOTS.clear()
        ok, porque = self._com_robots(
            urllib.error.HTTPError('u', 500, 'x', {}, None))
        self.assertFalse(ok, 'uma resposta ilegivel passou a permitir')
        self.assertIn('ileg', porque.lower())

    def test_3_404_continua_a_ser_permissivo(self):
        http._ROBOTS.clear()
        ok, porque = self._com_robots(
            urllib.error.HTTPError('u', 404, 'x', {}, None))
        self.assertTrue(ok, 'host sem robots.txt deixou de ser permissivo')

    def test_4_a_queda_nao_fica_guardada_como_proibicao(self):
        """Guardar «indisponivel» em memoria faria um solucco de rede virar uma
        proibicao permanente ate ao fim do processo."""
        http._ROBOTS.clear()
        with self.assertRaises(http.PortaoIndisponivel):
            self._com_robots(urllib.error.URLError('reset'))
        self.assertEqual(http._ROBOTS, {},
                         'a queda ficou memorizada; a tentativa seguinte nunca '
                         'chegaria a perguntar outra vez')

    def test_5_o_roteador_traduz_para_transporte_e_nao_para_politica(self):
        original = sr._rota_executavel

        def rota_que_cai(*a, **k):
            def fn(**kw):
                raise http.PortaoIndisponivel('o tunel caiu')
            return fn
        sr._rota_executavel = rota_que_cai
        try:
            _o, registo = sr.executar(platform='MASTODON',
                                      capability='SEARCH_HASHTAG',
                                      run_id='T-QUEDA')
        finally:
            sr._rota_executavel = original
        self.assertEqual(registo['ESTADO'], 'TRANSIENT_NETWORK_ERROR')
        self.assertNotEqual(registo['ESTADO'], 'ROUTE_NOT_ALLOWED')
        self.assertEqual(fx.recuperacao(registo['ESTADO'], None), 'WAIT',
                         'a queda passou a pedir NO_RETRY')

    def test_6_recusa_de_politica_continua_a_pedir_NO_RETRY(self):
        """O contraste que da sentido ao teste anterior."""
        self.assertEqual(fx.recuperacao('ROUTE_NOT_ALLOWED', None), 'NO_RETRY')
        self.assertNotEqual(fx.recuperacao('ROUTE_NOT_ALLOWED', None),
                            fx.recuperacao('TRANSIENT_NETWORK_ERROR', None))


class ABytesPreservadosSaoAProva(unittest.TestCase):
    """FASE 18 — uma regra pode mudar sem recoletar."""

    def test_7_o_raw_da_corrida_ao_vivo_existe(self):
        caminho = os.path.join(RAIZ, RAW)
        self.assertTrue(os.path.exists(caminho),
                        'o RAW da corrida ao vivo sumiu; sem ele esta missao '
                        'nao tem prova')
        d = json.loads(_fonte(RAW))
        self.assertEqual(len(d.get('feed') or []), 1,
                         'o RAW deixou de ter exactamente o item medido')

    def test_8_reprocessar_os_mesmos_bytes_nao_toca_a_rede(self):
        corpo = _fonte(RAW)
        buscar = http.buscar
        http.buscar = lambda *a, **k: corpo
        try:
            with _SemRede() as rede:
                objetos = reg.rota_de(PLATAFORMA, CAPACIDADE)(
                    handle=ALVO, limit=1, run_id='T-REPROC',
                    country_scope='IT', medida={})
        finally:
            http.buscar = buscar
        self.assertEqual(rede.tentativas, 0, 'o reprocessamento saiu a rede')
        self.assertEqual(len(objetos), 1)
        self.o = objetos[0]

    def _objeto(self):
        corpo = _fonte(RAW)
        buscar = http.buscar
        http.buscar = lambda *a, **k: corpo
        try:
            return reg.rota_de(PLATAFORMA, CAPACIDADE)(
                handle=ALVO, limit=1, run_id='T-REPROC', country_scope='IT',
                medida={})[0]
        finally:
            http.buscar = buscar

    def test_9_o_envelope_nao_fabrica_lugar_nem_lingua(self):
        o = self._objeto()
        self.assertEqual(o['COUNTRY_SCOPE'], 'IT')
        self.assertNotEqual(o['SOURCE_LOCATION'], o['COUNTRY_SCOPE'],
                            'o escopo da busca virou o lugar do facto')
        self.assertEqual(o['SOURCE_LOCATION'], 'UNKNOWN')
        # a lingua SO existe porque a fonte a declarou em `langs`
        bruto = json.loads(_fonte(RAW))['feed'][0]['post']['record']
        self.assertEqual(o['LANGUAGE'], (bruto.get('langs') or [None])[0])

    def test_10_identidade_nao_e_promovida(self):
        o = self._objeto()
        self.assertTrue(o['NATIVE_ID'].startswith('at://'))
        self.assertNotEqual(o['NATIVE_ID'], o['URL'])
        for proibido in ('SOURCE_ID', 'DOCUMENT_ID'):
            self.assertNotIn(proibido, o,
                             'o envelope passou a cunhar %s' % proibido)

    def test_11_o_envelope_aponta_para_o_bruto_com_sha(self):
        import hashlib
        o = self._objeto()
        ref = o['RAW_REFERENCE']
        self.assertEqual(ref['PATH'], RAW)
        with io.open(os.path.join(RAIZ, RAW), 'rb') as f:
            self.assertEqual(ref['SHA256'], hashlib.sha256(f.read()).hexdigest())
        self.assertEqual(ref['PRESERVATION'], 'NOT_PRESERVED',
                         'o disco do runner passou a dizer-se preservado')

    def test_12_a_corrida_ao_vivo_ficou_registada(self):
        d = json.loads(_fonte(CORRIDA))
        self.assertEqual(d['ALVO'], ALVO)
        self.assertIn('cf3aec60', d['ALVO_ORIGEM'],
                      'o alvo deixou de citar a evidencia de onde veio')
        self.assertLessEqual(len(d['PEDIDOS']), d['TETO_DE_PEDIDOS'],
                             'a corrida registada excedeu o proprio teto')


class OTrialNaoPromoveuNada(unittest.TestCase):

    def test_13_o_executor_continua_sem_saber_escrever(self):
        texto = _fonte('coleta/scrap_executor.py')
        arv = ast.parse(texto)
        prosa = {ast.get_docstring(n, clean=False) for n in ast.walk(arv)
                 if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef))}
        prosa.discard(None)
        for p in prosa:
            texto = texto.replace(p, '')
        texto = re.sub(r'(?m)^\s*#.*$', '', texto)
        for proibido in ('open(', 'write_text', 'json.dump', 'DECLARADAS['):
            self.assertNotIn(proibido, texto)

    def test_14_a_promocao_cita_a_prova_ao_vivo(self):
        """Se esta capacidade for promovida, a prova NAO pode continuar a
        apontar para a matriz nem para a C10.7 offline."""
        estado = cap.estado(CAPACIDADE)
        prova = cap.prova(CAPACIDADE)
        if estado in ('PROVEN', 'PARTIAL'):
            self.assertIn('C10-8A', prova,
                          'a capacidade foi promovida e a prova nao aponta '
                          'para o artefato da corrida ao vivo: %s' % prova)
            self.assertTrue(os.path.exists(os.path.join(RAIZ, prova)),
                            'a prova citada nao existe no disco')
        else:
            self.assertEqual(estado, 'NOT_EXECUTED',
                             'estado inesperado: %s' % estado)


class APoliticaEOCustoNaoMudaram(unittest.TestCase):

    def test_15_a_rota_continua_gratuita_e_permitida(self):
        d = mz.decisao(PLATAFORMA, 'INCREMENTAL')
        self.assertEqual(d['DECISAO'], mz.PERMITIDA_SIM)
        self.assertEqual(d['CLASSE'], 'PUBLIC_NATIVE')
        rota = next(r for r in mz.MATRIZ['BLUESKY']['INCREMENTAL']
                    if r['ROTA'] == d['ROTA'])
        self.assertEqual(rota['CUSTO'], 'zero',
                         'a rota do trial deixou de ser declarada gratuita')

    def test_16_nenhuma_credencial_e_pedida(self):
        self.assertIsNone(reg.sonda_de(PLATAFORMA, CAPACIDADE))
        d = json.loads(_fonte(CORRIDA))
        for p in d['PEDIDOS']:
            self.assertNotIn('token', p['URL'].lower())
            self.assertNotIn('key=', p['URL'].lower())

    def test_17_o_trace_da_corrida_diz_TRIAL_e_nao_pago(self):
        t = json.loads(_fonte(CORRIDA))['TRACE']
        self.assertEqual(t['EXECUTION_MODE'], 'TRIAL')
        self.assertIs(t['PAID_PROVIDER_USED'], False)
        self.assertEqual(float(t['COST_USD']), 0.0)
        self.assertEqual(t['CAPABILITY_STATE_BEFORE'],
                         t['CAPABILITY_STATE_AFTER'],
                         'o trial promoveu estado durante a execucao')


class OTetoDePedidosMorde(unittest.TestCase):
    """UM TETO QUE NAO RECUSA NAO E UM TETO.

    A primeira bateria de mutacao provou a necessidade: pondo `if False:` a
    frente do `raise`, o teto deixava de recusar e nenhuma sentinela reparava —
    porque a unica que olhava para ele procurava a PALAVRA `TetoEstourado` no
    ficheiro, e a palavra continuava la.

        UMA SENTINELA QUE PROCURA A PALAVRA NAO MEDE O QUE ELA FAZ.
    """

    def setUp(self):
        sys.path.insert(0, os.path.join(RAIZ, 'provas'))
        import bluesky_trial_ao_vivo as bt
        self.bt = bt
        bt.PEDIDOS[:] = []

    def tearDown(self):
        self.bt.PEDIDOS[:] = []

    def test_18_o_pedido_a_seguir_ao_teto_levanta(self):
        bt = self.bt
        import urllib.request

        class _Resposta(object):
            status = 200

            def read(self):
                return b'{}'

            def close(self):
                pass

        original = urllib.request.urlopen
        urllib.request.urlopen = lambda *a, **k: _Resposta()
        try:
            devolvido = bt._contar_e_limitar()
            try:
                for _ in range(bt.MAX_PEDIDOS):
                    urllib.request.urlopen(
                        urllib.request.Request('https://exemplo.tld/x')).read()
                self.assertEqual(len(bt.PEDIDOS), bt.MAX_PEDIDOS)
                with self.assertRaises(bt.TetoEstourado):
                    urllib.request.urlopen(
                        urllib.request.Request('https://exemplo.tld/x'))
            finally:
                urllib.request.urlopen = devolvido
        finally:
            urllib.request.urlopen = original

    def test_19_o_teto_conta_e_mede_cada_pedido(self):
        """Um contador que nao guarda status nem bytes nao serve de registo."""
        bt = self.bt
        import urllib.request

        class _Resposta(object):
            status = 200

            def read(self):
                return b'{"feed": []}'

            def close(self):
                pass

        original = urllib.request.urlopen
        urllib.request.urlopen = lambda *a, **k: _Resposta()
        try:
            devolvido = bt._contar_e_limitar()
            try:
                urllib.request.urlopen(
                    urllib.request.Request('https://exemplo.tld/y')).read()
            finally:
                urllib.request.urlopen = devolvido
        finally:
            urllib.request.urlopen = original
        self.assertEqual(len(bt.PEDIDOS), 1)
        p = bt.PEDIDOS[0]
        self.assertEqual(p['STATUS'], 200)
        self.assertEqual(p['BYTES'], 12)
        self.assertIsNotNone(p['MS'])
        self.assertIn('exemplo.tld', p['URL'])

    def test_20_a_prova_entra_pelo_executor_e_nao_pela_rota(self):
        """M1: uma prova que chama a rota direto prova a rota, nao a casa."""
        fonte = _fonte('provas/bluesky_trial_ao_vivo.py')
        arv = ast.parse(fonte)
        chamadas = set()
        for n in ast.walk(arv):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            alvo = getattr(f, 'attr', None)
            dono = getattr(getattr(f, 'value', None), 'id', None)
            if alvo:
                chamadas.add('%s.%s' % (dono, alvo) if dono else alvo)
        self.assertIn('sx.COLLECT', chamadas,
                      'a prova deixou de entrar pelo executor')
        for proibido in ('sr.executar', 'sr._executar', 'http.buscar'):
            self.assertNotIn(proibido, chamadas,
                             'a prova passou a chamar %s direto' % proibido)
        # o reprocessamento CHAMA a rota de proposito: e outro acto, e esta
        # dentro de `reprocessar`, que nao usa rede.
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'reprocessar')
        self.assertTrue(any(isinstance(c, ast.Call) for c in ast.walk(fn)))


class OLugarDoFatoNaoVemDoEscopo(unittest.TestCase):
    """M5: `source_location=country_scope` em QUALQUER rota é a mesma mentira."""

    def test_21_nenhuma_rota_aberta_passa_o_escopo_como_lugar(self):
        fonte = _fonte('coleta/adaptador_aberto.py')
        arv = ast.parse(fonte)
        medidas = 0
        for fn in [n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)]:
            for c in ast.walk(fn):
                if not isinstance(c, ast.Call):
                    continue
                if getattr(c.func, 'attr', None) != 'envelope':
                    continue
                medidas += 1
                for kw in c.keywords:
                    if kw.arg != 'source_location':
                        continue
                    self.assertNotEqual(
                        getattr(kw.value, 'id', None), 'country_scope',
                        '%s passa o escopo da busca como lugar do facto'
                        % fn.name)
        self.assertGreaterEqual(medidas, 4,
                                'a sonda nao viu envelopes que cheguem')

    def test_22_o_envelope_recusa_o_escopo_como_lugar(self):
        """Controlo positivo: se alguem o passar, o objeto fica diferente —
        e por isso a sentinela acima tem o que medir."""
        import social_envelope as env
        com = env.envelope(platform='BLUESKY', native_id='a', url='u',
                           content_type='POST', route='r', executor='e',
                           run_id='x', country_scope='IT',
                           source_location='IT')
        sem = env.envelope(platform='BLUESKY', native_id='a', url='u',
                           content_type='POST', route='r', executor='e',
                           run_id='x', country_scope='IT')
        self.assertNotEqual(com['SOURCE_LOCATION'], sem['SOURCE_LOCATION'],
                            'passar `source_location` deixou de mudar o objeto; '
                            'a sentinela do teste anterior mede o nada')
        self.assertEqual(sem['SOURCE_LOCATION'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main(verbosity=2)
