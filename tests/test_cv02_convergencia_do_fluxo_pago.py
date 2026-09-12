#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DA CONVERGENCIA — SCRAP-CV-02.

O fluxo operacional do SINTONIA SCRAP ja atravessava o orquestrador canonico. O
controle de gasto ja estava provado noutra linha. Esta suite pergunta se as duas
coisas passaram a ser UMA, e se continuam a ser TRES perguntas:

    SPEND_AUTHORIZATION != FINANCIAL_BUDGET != NETWORK_BUDGET

O FORNECEDOR E FALSO SO NA FRONTEIRA EXTERNA
---------------------------------------------
O espiao substitui `subprocess.run` — o processo `curl` que sai da maquina — e
mais nada. Ficam REAIS e por cima dele: `coletor._curl`, o teto de rede, o
orcamento financeiro, `coletor.executar`, a guarda de autorizacao e o roteador.

    SE O FAKE FICAR ACIMA DE UM OWNER, A PROVA E INVALIDA.

E A PORTA TEM DE SER A PORTA
-----------------------------
`regras/sensor_coleta.py` troca `coletor._curl` no CORPO do modulo. Basta alguem
importa-lo para o transporte da unica porta paga mudar no processo inteiro — e
entao fingir o `subprocess` deixa de fingir coisa nenhuma: o pedido sai por
`urllib` e vai MESMO a rede.

    UM FAKE QUE JA NAO ESTA NO CAMINHO NAO E UM FAKE. E UM ADORNO.

    NETWORK_REAL = 0 · APIFY_REAL_RUNS = 0 · PAID_REAL_RUNS = 0 · REAL_COST_USD = 0
"""
import copy
import json
import os
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import autorizacao_de_gasto as az   # noqa: E402
import coletor as ct                # noqa: E402
import falhas                       # noqa: E402
import scrap_http as http           # noqa: E402

ATOR = 'fake~ator-da-convergencia'
FONTE, PROP = 'IT-T3-001', 'T3'


class CurlFalso(object):
    """O mundo externo, e so ele. Conta os POST; nunca abre ligacao."""

    def __init__(self, custos=None):
        self.posts = 0
        self.tetos = []
        self.custos = list(custos or [])

    class _R(object):
        def __init__(self, out, rc=0, err=''):
            self.returncode, self.stdout, self.stderr = rc, out, err

    def __call__(self, cmd, **k):
        url = cmd[-1]
        if '-X' in cmd and cmd[cmd.index('-X') + 1].upper() == 'POST':
            self.posts += 1
            for parte in url.split('?')[-1].split('&'):
                if parte.startswith('maxTotalChargeUsd='):
                    self.tetos.append(float(parte.split('=', 1)[1]))
            custo = self.custos.pop(0) if self.custos else 0.0
            if custo is not None and self.tetos and custo > self.tetos[-1]:
                custo = self.tetos[-1]          # um provider que respeita o cap
            return self._R(json.dumps({'data': {
                'id': 'R%d' % self.posts, 'status': 'SUCCEEDED',
                'startedAt': '2026-09-12T00:00:00.000Z',
                'finishedAt': '2026-09-12T00:00:01.000Z',
                'defaultDatasetId': 'DS', 'buildNumber': '1',
                'usageTotalUsd': custo}}))
        if '/datasets/' in url:
            return self._R('[]')
        return self._R(json.dumps({'data': {}}))


class ComMundoFalso(unittest.TestCase):
    """O fake fica ABAIXO de todos os owners, e a arvore nao e tocada."""

    def setUp(self):
        self.mundo = CurlFalso()
        self._run = ct.subprocess.run
        ct.subprocess.run = self.mundo
        # Repor a porta original NAO e mockar um owner: e desfazer o mock de
        # outra pessoa, para que o que se mede seja o que se diz que se mede.
        self._curl = ct._curl
        ct._curl = ct._CURL_DA_CASA
        # A morada do RAW muda-se; o contrato nao. Uma suite que escreve na
        # arvore mede a corrida anterior, nao o codigo.
        self._raw = ct.RAW_DIR
        self._tmp = tempfile.mkdtemp(prefix='cv02-raw-')
        ct.RAW_DIR = self._tmp
        self._antes = self._raw_real()
        self.addCleanup(self._repor)
        self.addCleanup(self._sem_residuo)

    def _raw_real(self):
        d = os.path.join(RAIZ, 'data', 'samples', 'raw-paid')
        return set(os.listdir(d)) if os.path.isdir(d) else set()

    def _sem_residuo(self):
        novos = self._raw_real() - self._antes
        for n in novos:
            os.remove(os.path.join(RAIZ, 'data', 'samples', 'raw-paid', n))
        assert not novos, 'a prova deixou RAW falso na arvore: %s' % sorted(novos)

    def _repor(self):
        import shutil
        ct.subprocess.run = self._run
        ct._curl = self._curl
        ct.RAW_DIR = self._raw
        shutil.rmtree(self._tmp, ignore_errors=True)

    # ── os construtores ────────────────────────────────────────────────────
    CAMPOS_TRIAL = {'AUTORIZACAO_HUMANA': 'bateria CV-02',
                    'MAX_PROVIDER_RUNS': 1, 'MAX_START_POSTS': 1,
                    'MAX_USD': 0.10}

    def trial(self, **mud):
        return az.conceder(dict(self.CAMPOS_TRIAL, **mud))

    def campos_normal(self, sid=FONTE, prop=PROP, **mud):
        base = {'VEREDITO': az.AUTORIZA, 'SOURCE_ID': sid, 'PROPOSITO': prop,
                'ESTADO_DA_RELEVANCIA': az.SIM, 'VERSAO_DO_PORTAO': '1',
                'CONTRATO': 'RELEVANCIA_DA_FONTE/v1',
                'DECISAO': {'EVIDENCIA': {'F': 'LIVRO'}},
                'MAX_PROVIDER_RUNS': 1, 'MAX_START_POSTS': 1, 'MAX_USD': 0.10}
        base.update(mud)
        return base

    def normal(self, **mud):
        return az.conceder(self.campos_normal(**mud))

    def comprar(self, autorizacao, *, orcamento=0.10, rede=None, teto=None,
                modo=az.TRIAL, **kw):
        """A porta paga REAL, com os tres portoes reais e o mundo falso na ponta."""
        import contextlib
        base = dict(token='T', run_id='R', platform='YOUTUBE', country='IT',
                    mission='CV-02', query='q', source_version='v',
                    evidence_path='/dev/null', wait=60, salvar_raw=False,
                    modo=modo, autorizacao=autorizacao, teto_usd=teto)
        base.update(kw)
        with contextlib.ExitStack() as pilha:
            if orcamento is not None:
                pilha.enter_context(ct.orcamento_financeiro(orcamento))
            if rede is not None:
                pilha.enter_context(http.orcamento_de_rede(rede))
            return ct.executar(ATOR, {'q': 1}, **base)

    def recusa(self, autorizacao, **kw):
        """→ o estado da recusa. Levanta se a compra passar."""
        with self.assertRaises(az.SemAutorizacaoDeGasto) as c:
            self.comprar(autorizacao, **kw)
        self.assertEqual(0, self.mundo.posts, 'UMA COMPRA NASCEU')
        return c.exception.estado


# ══════════════════════════════════════════════════════════════════════════
# A · A REPRODUCAO DO DEFEITO — guardada, nao apagada
# ══════════════════════════════════════════════════════════════════════════
class ODefeitoDeUmDolarQuePagavaDois(ComMundoFalso):
    """MEDIDO NESTA ARVORE, antes do conserto:

        autorizacao: MAX_PROVIDER_RUNS = 2 · MAX_USD = 1.00
        duas execucoes, cada uma a declarar orcamento de 1.00
        -> EXPOSICAO REPRESENTADA = 2.00

    O limite humano era conferido por presenca e por sinal, nunca contra o que
    a execucao declarava poder comprometer.

        CADA POST GANHAVA O LIMITE INTEIRO OUTRA VEZ.
        UM LIMITE QUE RENASCE A CADA COMPRA NAO E UM LIMITE.
    """

    def test_o_contraexemplo_original_ja_nao_passa(self):
        a = self.trial(MAX_PROVIDER_RUNS=2, MAX_USD=1.00)
        exposto = 0.0
        primeira = True
        for _ in range(2):
            try:
                with ct.orcamento_financeiro(1.00) as orc:   # cada uma declara 1.00
                    self.comprar(a, orcamento=None, teto=1.00)
                    exposto += orc.exposto_micros / float(ct.MICRO)
                primeira = False
            except az.SemAutorizacaoDeGasto:
                pass
        self.assertLessEqual(exposto, 1.00 + 1e-9,
                             'HUMAN_LIMIT_USD = 1.00 e a exposicao passou disso')
        self.assertFalse(primeira, 'a primeira compra tambem foi barrada')

    def test_uma_autorizacao_nao_vale_em_dois_orcamentos(self):
        """A segunda metade do mesmo defeito, um andar acima.

        ⚠️ ENCONTRADO PELO RED TEAM DESTA MISSAO, depois de a relacao
        `AUTHORIZED <= MAX_USD` ja estar instalada:

            autorizacao: MAX_PROVIDER_RUNS = 2 · MAX_USD = 1.00
            DUAS execucoes, cada uma a abrir o SEU orcamento de 1.00
            cada compra custa 0.60 -> EXPOSICAO TOTAL = 1.20

        Cada orcamento sozinho cabia no limite humano. A SOMA nao cabia.

            UM LIMITE CONFERIDO CONTRA UM LEDGER QUE MUDA NAO FOI CONFERIDO.

        E a saida nao foi dar um saldo a guarda: ela guarda um NOME.

            UM NOME NAO E UMA SOMA.
        """
        a = self.trial(MAX_PROVIDER_RUNS=2, MAX_USD=1.00)
        self.mundo.custos = [0.60, 0.60]
        exposto, compradas = 0.0, 0
        for _ in range(2):
            try:
                with ct.orcamento_financeiro(1.00) as orc:
                    self.comprar(a, orcamento=None, teto=1.00)
                    exposto += orc.exposto_micros / float(ct.MICRO)
                    compradas += 1
            except az.SemAutorizacaoDeGasto:
                pass
        self.assertEqual(1, compradas, 'a segunda execucao comprou noutro ledger')
        self.assertLessEqual(exposto, 1.00 + 1e-9,
                             'EXPOSICAO = %.4f sob MAX_USD = 1.00' % exposto)
        self.assertEqual(1, self.mundo.posts)

    def test_duas_compras_no_MESMO_orcamento_continuam_a_passar(self):
        """E a amarra nao pode fechar a porta ao caso legitimo.

        Varias chamadas dentro da MESMA execucao partilham um so saldo — e essa
        e a forma canonica de o fazer nesta casa. O que se recusa e outra
        execucao, nao outra chamada.
        """
        a = self.trial(MAX_PROVIDER_RUNS=2, MAX_USD=1.00)
        self.mundo.custos = [0.30, 0.30]
        with ct.orcamento_financeiro(1.00) as orc:
            for _ in range(2):
                self.comprar(a, orcamento=None, teto=0.50)
            self.assertEqual(2, self.mundo.posts)
            self.assertLessEqual(orc.exposto_micros / float(ct.MICRO), 1.00 + 1e-9)

    def test_a_guarda_nao_ganhou_um_ledger_proprio(self):
        """O conserto NAO foi dar-lhe um ledger. Ela conta EXECUCOES.

            LIMITE HUMANO != LEDGER OPERACIONAL.
        """
        import types
        for nome in ('OrcamentoFinanceiro', 'Reserva', 'reservar', 'liquidar',
                     'desconhecer', 'anular', 'subprocess'):
            self.assertFalse(hasattr(az, nome), 'a guarda expoe %s' % nome)
        modulos = [getattr(v, '__name__', '') for v in vars(az).values()
                   if isinstance(v, types.ModuleType)]
        for proibido in ('coletor', 'apify_pool', 'scrap_http'):
            self.assertNotIn(proibido, modulos)
        a = self.trial(MAX_PROVIDER_RUNS=2)
        antes = a['MAX_USD']
        az.pode_comprar(modo=az.TRIAL, autorizacao=a, orcamento_autorizado=0.10)
        self.assertEqual(0, a._gastas, 'conferir gastou uma unidade')
        az.consumir(a)
        self.assertEqual(antes, a['MAX_USD'], 'a guarda mexeu em dolares')
        self.assertEqual(1, a['MAX_PROVIDER_RUNS'] - a.restantes,
                         'a guarda conta EXECUCOES, e foi so uma')


# ══════════════════════════════════════════════════════════════════════════
# B · A MATRIZ DA AUTORIZACAO — os dez casos que a missao exige
# ══════════════════════════════════════════════════════════════════════════
class AMatrizDaAutorizacao(ComMundoFalso):

    def test_sem_autorizacao_nenhuma(self):
        self.assertEqual(az.SEM_AUTORIZACAO, self.recusa(None))

    def test_autorizacao_valida_compra_uma_vez(self):
        self.comprar(self.trial())
        self.assertEqual(1, self.mundo.posts)

    def test_autorizacao_para_outra_fonte(self):
        a = self.normal(sid='IT-T3-999')
        self.assertEqual(az.FONTE_ERRADA,
                         self.recusa(a, modo=az.NORMAL, source_id=FONTE,
                                     proposito=PROP))

    def test_autorizacao_para_outro_proposito(self):
        a = self.normal(prop='T3')
        self.assertEqual(az.PROPOSITO_ERRADO,
                         self.recusa(a, modo=az.NORMAL, source_id=FONTE,
                                     proposito='T9'))

    def test_autorizacao_copiada_nao_compra(self):
        """COPIAR UMA AUTORIZACAO NAO E RECEBER UMA AUTORIZACAO.

        ⚠️ E HA DUAS MANEIRAS DE A COPIA MORRER, e as duas contam. O selo torna
        a autorizacao imutavel depois de concedida, e `copy` e `deepcopy`
        reconstroem o objecto ESCREVENDO chave a chave — portanto rebentam
        antes de existir copia nenhuma. As que se conseguem construir morrem na
        porta, por nao terem identidade.

        O que NAO pode acontecer, por nenhum caminho, e uma copia comprar.
        """
        a = self.trial()
        mortes = []
        for nome, fazer in (('copy.copy', lambda: copy.copy(a)),
                            ('copy.deepcopy', lambda: copy.deepcopy(a)),
                            ('dict(a)', lambda: dict(a)),
                            ('Autorizacao(a)', lambda: az.Autorizacao(a))):
            with self.subTest(copia=nome):
                try:
                    copia = fazer()
                except az.SemAutorizacaoDeGasto:
                    mortes.append('NAO_SE_CONSEGUE_COPIAR')
                    continue
                mortes.append(self.recusa(copia))
        self.assertEqual(4, len(mortes))
        for morte in mortes:
            self.assertIn(morte, ('NAO_SE_CONSEGUE_COPIAR', az.SEM_AUTORIZACAO))
        self.assertEqual(0, self.mundo.posts, 'uma copia comprou')

    def test_autorizacao_esgotada(self):
        a = self.trial(MAX_PROVIDER_RUNS=1)
        self.comprar(a)
        self.assertEqual(1, self.mundo.posts)
        with self.assertRaises(az.SemAutorizacaoDeGasto):
            self.comprar(a)
        self.assertEqual(1, self.mundo.posts, 'a segunda compra nasceu')

    def test_max_usd_superior_ao_orcamento_passa(self):
        self.comprar(self.trial(MAX_USD=1.00), orcamento=0.10)
        self.assertEqual(1, self.mundo.posts)

    def test_max_usd_igual_ao_orcamento_passa(self):
        self.comprar(self.trial(MAX_USD=0.10), orcamento=0.10)
        self.assertEqual(1, self.mundo.posts)

    def test_max_usd_inferior_ao_orcamento_recusa(self):
        """FINANCIAL_BUDGET.AUTHORIZED <= AUTORIZACAO.MAX_USD."""
        self.assertEqual(az.SEM_AUTORIZACAO,
                         self.recusa(self.trial(MAX_USD=0.05), orcamento=1.00))

    def test_NORMAL_sem_ledger_nao_compra(self):
        """SEM LEDGER NAO SE COMPRA — e o POST nem chega a ser pensado."""
        a = self.normal()
        estado = self.recusa(a, orcamento=None, modo=az.NORMAL,
                             source_id=FONTE, proposito=PROP)
        self.assertEqual(az.SEM_AUTORIZACAO, estado)

    def test_a_autorizacao_nao_muda_depois_de_concedida(self):
        """Trazer um bilhete e entrar com outro."""
        a = self.trial(MAX_USD=0.10)
        for mexer in (lambda: a.__setitem__('MAX_USD', 99.0),
                      lambda: a.update(MAX_USD=99.0),
                      lambda: a.pop('MAX_USD'),
                      lambda: a.setdefault('MAX_ITEMS', 99)):
            with self.subTest():
                with self.assertRaises(az.SemAutorizacaoDeGasto):
                    mexer()
        self.assertEqual(0.10, a['MAX_USD'])


# ══════════════════════════════════════════════════════════════════════════
# C · OS TRES PORTOES SAO TRES, E NENHUM SE VESTE DO OUTRO
# ══════════════════════════════════════════════════════════════════════════
class OsTresPortoesSaoTres(ComMundoFalso):

    def test_a_recusa_de_gasto_nao_e_uma_falha_de_transporte(self):
        """UMA RECUSA QUE PEDE PARA SER REPETIDA NAO E UMA RECUSA."""
        e = az.SemAutorizacaoDeGasto('x', estado=az.SEM_AUTORIZACAO)
        self.assertNotIsInstance(e, OSError)
        self.assertNotIsInstance(e, PermissionError)
        self.assertIsInstance(e, RuntimeError)
        familia = falhas.traduzir(az.SEM_AUTORIZACAO)
        self.assertEqual('BUDGET_EXHAUSTED', familia)
        self.assertEqual('NO_RETRY', falhas.recuperacao(familia))
        self.assertNotEqual(familia, falhas.traduzir('TRANSIENT_NETWORK_ERROR'))
        self.assertEqual('WAIT', falhas.recuperacao(
            falhas.traduzir('TRANSIENT_NETWORK_ERROR')))

    def test_as_ausencias_da_relevancia_nao_caem_no_balde_do_desconhecido(self):
        """NOT_MEASURED != NOT_RELEVANT, e nenhuma delas e UNKNOWN_ERROR."""
        for estado in (az.RELEVANCIA_BARRADA, az.RELEVANCIA_POR_AVALIAR,
                       az.RELEVANCIA_INCERTA, az.RELEVANCIA_COM_ERRO,
                       az.SEM_AUTORIZACAO):
            with self.subTest(estado=estado):
                self.assertEqual('BUDGET_EXHAUSTED', falhas.traduzir(estado))

    def test_as_tres_recusas_sao_tres_tipos_e_nenhuma_e_OSError(self):
        import social_rotas
        tres = (http.SemOrcamentoDeRede, ct.SemOrcamentoFinanceiro,
                az.SemAutorizacaoDeGasto)
        self.assertEqual(3, len(set(tres)), 'dois portoes partilham a excecao')
        for excecao in tres:
            self.assertTrue(issubclass(excecao, RuntimeError), excecao.__name__)
            self.assertFalse(issubclass(excecao, OSError), excecao.__name__)
        # ⚠️ Aqui NAO se procura a palavra no ficheiro da rota: procurar
        # `SemAutorizacaoDeGasto` no texto acharia tambem o comentario que
        # explica por que ela passa, e um comentario nao deixa passar nada.
        self.assertIs(az.SemAutorizacaoDeGasto, social_rotas.SemAutorizacaoDeGasto)
        self.assertIs(ct.SemOrcamentoFinanceiro, social_rotas.SemOrcamentoFinanceiro)

    def test_sem_dinheiro_a_recusa_e_do_dinheiro(self):
        a = self.trial(MAX_USD=0.10)
        with ct.orcamento_financeiro(0.10) as orc:
            orc.reservar(pedido=0.10, ator='x', rota='y', missao='z')  # esgota
            with self.assertRaises(ct.SemOrcamentoFinanceiro):
                self.comprar(a, orcamento=None, teto=0.10)
        self.assertEqual(0, self.mundo.posts)
        self.assertEqual(0, a._gastas,
                         'o dinheiro recusou e mesmo assim queimou a autorizacao')

    def test_sem_rede_a_recusa_e_da_rede_e_a_autorizacao_volta(self):
        """UM POST QUE NAO SAIU NAO GASTA UMA AUTORIZACAO."""
        a = self.trial(MAX_USD=0.10)
        with ct.orcamento_financeiro(0.10) as orc:
            with http.orcamento_de_rede(0):
                with self.assertRaises(http.SemOrcamentoDeRede):
                    self.comprar(a, orcamento=None, teto=0.10)
            self.assertEqual(0, self.mundo.posts)
            self.assertEqual(0.10, orc.restante, 'o dinheiro nao voltou')
            self.assertEqual(0, a._gastas, 'a execucao autorizada foi queimada')

    def test_uma_recusa_DEPOIS_do_POST_nao_devolve_a_execucao(self):
        """AUSENCIA DE NOTICIA NAO E PROVA DE AUSENCIA DE COMPRA."""
        a = self.trial(MAX_PROVIDER_RUNS=2, MAX_USD=0.20)
        with ct.orcamento_financeiro(0.20):
            with http.orcamento_de_rede(1):        # chega para o POST, e mais nada
                with self.assertRaises(http.SemOrcamentoDeRede):
                    self.comprar(a, orcamento=None, teto=0.20)
        self.assertEqual(1, self.mundo.posts, 'o POST saiu')
        self.assertEqual(1, a._gastas, 'a execucao voltou depois de o POST sair')

    def test_o_cap_do_fornecedor_nunca_passa_do_que_resta(self):
        """PROVIDER CAP <= EXECUTION REMAINING."""
        a = self.trial(MAX_PROVIDER_RUNS=2, MAX_USD=1.00)
        self.mundo.custos = [0.70, 0.0]
        with ct.orcamento_financeiro(1.00):
            for _ in range(2):
                self.comprar(a, orcamento=None, teto=1.00)   # pede 1.00 nas DUAS
        self.assertEqual(2, len(self.mundo.tetos))
        self.assertAlmostEqual(1.00, self.mundo.tetos[0], places=4)
        self.assertLessEqual(self.mundo.tetos[1], 0.30 + 1e-9,
                             'o segundo POST recebeu o teto original')


# ══════════════════════════════════════════════════════════════════════════
# D · A ROTACAO DE CHAVE
# ══════════════════════════════════════════════════════════════════════════
class RotacaoDeChave(ComMundoFalso):

    def test_cinco_chaves_nao_renovam_uma_execucao_autorizada(self):
        """ROTACAO DE CHAVE NAO E NOVA AUTORIZACAO.

        MEDIDO nesta arvore antes do conserto: com `MAX_PROVIDER_RUNS = 2` e
        cinco chaves no cofre sairam CINCO POSTs. O limite existia no papel e
        ninguem o contava.
        """
        a = self.trial(MAX_PROVIDER_RUNS=2, MAX_USD=1.00)
        saiu = 0
        with ct.orcamento_financeiro(1.00):
            for chave in ('k1', 'k2', 'k3', 'k4', 'k5'):
                try:
                    self.comprar(a, orcamento=None, token=chave, teto=0.10)
                    saiu += 1
                except az.SemAutorizacaoDeGasto:
                    pass
        self.assertEqual(2, saiu)
        self.assertEqual(2, self.mundo.posts, 'cinco chaves compraram cinco vezes')


# ══════════════════════════════════════════════════════════════════════════
# E · O TRANSPORTE TROCADO, COM A TROCA REALMENTE ACTIVADA
# ══════════════════════════════════════════════════════════════════════════
class OTransporteTrocado(unittest.TestCase):
    """Nao basta inspeccionar o codigo: importa-se o sensor e mede-se."""

    def setUp(self):
        import sensor_coleta
        self.sensor = sensor_coleta
        self._curl = ct._curl
        # ⚠️ ESTA CLASSE IMPORTA O SENSOR DE PROPOSITO, e o import troca
        # `coletor._curl` no processo INTEIRO. Quem vier a seguir — outra
        # bateria, outra prova — herdava a porta trocada por causa DESTA suite.
        #
        #     UMA PROVA NAO DEIXA O PROCESSO PIOR DO QUE O ENCONTROU.
        #
        # Repoe-se a porta da casa. A troca continua a existir e continua a ser
        # medida aqui; o que nao continua e o efeito colateral.
        self.addCleanup(lambda: setattr(ct, '_curl', ct._CURL_DA_CASA))

    def test_carregar_o_sensor_troca_mesmo_a_porta(self):
        """O facto que torna esta classe necessaria, medido e nao presumido.

        ⚠️ NAO SE MEDE COM `import`: o modulo ja esta carregado, e um segundo
        `import` nao volta a correr o corpo dele. Mede-se com `reload`, que
        corre o corpo outra vez — que e exactamente o que acontece da primeira
        vez que alguem, em qualquer sitio, o carrega.
        """
        import importlib
        ct._curl = ct._CURL_DA_CASA
        self.assertIs(ct._curl, ct._CURL_DA_CASA, 'a porta nao estava reposta')
        importlib.reload(self.sensor)
        self.assertIsNot(ct._curl, ct._CURL_DA_CASA,
                         'carregar o sensor deixou de trocar a porta')
        self.assertIs(ct._curl, self.sensor._curl_robusto)
        self.assertEqual('coletor', ct._CURL_DA_CASA.__module__)

    def test_o_transporte_substituto_pede_autorizacao_ao_dono_da_rede(self):
        import urllib.request
        saiu = []

        def urlopen_falso(req, *a, **k):
            saiu.append(getattr(req, 'full_url', str(req)))
            raise AssertionError('o pedido SAIU com o teto de acessos a zero')

        real = urllib.request.urlopen
        urllib.request.urlopen = urlopen_falso
        try:
            with http.orcamento_de_rede(0):
                with self.assertRaises(http.SemOrcamentoDeRede):
                    self.sensor._curl_robusto(
                        'https://api.apify.com/v2/acts/x/runs',
                        token='T', metodo='POST', corpo={})
        finally:
            urllib.request.urlopen = real
        self.assertEqual([], saiu, 'o transporte substituto ignorou o teto de rede')

    def test_o_transporte_substituto_nao_repete_o_POST(self):
        """REPETIR UM GET E BARATO. REPETIR UM POST E COMPRAR DE NOVO."""
        import urllib.request
        tentativas = []

        def urlopen_falso(req, *a, **k):
            tentativas.append(req.get_method())
            raise OSError('ws_closed_mid_exchange')

        real = urllib.request.urlopen
        urllib.request.urlopen = urlopen_falso
        try:
            with self.assertRaises(ct.PostTalvezCriado):
                self.sensor._curl_robusto(
                    'https://api.apify.com/v2/acts/x/runs',
                    token='T', metodo='POST', corpo={})
            self.assertEqual(1, len(tentativas),
                             'o POST saiu %d vezes: comprou %d vezes'
                             % (len(tentativas), len(tentativas)))
            tentativas[:] = []
            with self.assertRaises(RuntimeError):
                self.sensor._curl_robusto('https://api.apify.com/v2/acts/x',
                                          token='T')
            self.assertGreater(len(tentativas), 1, 'o GET deixou de retentar')
        finally:
            urllib.request.urlopen = real

    def test_com_o_sensor_importado_a_prova_continua_offline(self):
        """A troca esta activa e a porta paga continua a ser medida.

        ⚠️ E ESTA E A PROVA DE QUE A SUITE NAO MENTE. Com o transporte trocado,
        um harness que finge `subprocess` deixaria de estar no caminho — e o
        POST sairia por `urllib`, para a rede a serio.
        """
        import importlib
        import urllib.request
        # A troca e ACTIVADA aqui, e nao presumida de quem importou antes: cada
        # prova desta classe repoe a porta ao sair, para nao contaminar as
        # seguintes.
        importlib.reload(self.sensor)
        self.assertIs(ct._curl, self.sensor._curl_robusto, 'a troca nao esta activa')
        saiu = []

        def urlopen_falso(req, *a, **k):
            saiu.append(1)
            raise AssertionError('a prova offline foi a rede')

        real, mundo = urllib.request.urlopen, CurlFalso()
        _run, _raw = ct.subprocess.run, ct.RAW_DIR
        urllib.request.urlopen = urlopen_falso
        ct.subprocess.run = mundo
        ct._curl = ct._CURL_DA_CASA
        ct.RAW_DIR = tempfile.mkdtemp(prefix='cv02-tr-')
        try:
            a = az.conceder({'AUTORIZACAO_HUMANA': 'CV-02', 'MAX_PROVIDER_RUNS': 1,
                             'MAX_START_POSTS': 1, 'MAX_USD': 0.10})
            with ct.orcamento_financeiro(0.10):
                ct.executar(ATOR, {'q': 1}, token='T', run_id='R',
                            platform='YOUTUBE', country='IT', mission='CV-02',
                            query='q', source_version='v',
                            evidence_path='/dev/null', wait=60,
                            salvar_raw=False, modo=az.TRIAL, autorizacao=a,
                            teto_usd=0.10)
            self.assertEqual(1, mundo.posts, 'o POST nao passou pelo fake')
            self.assertEqual([], saiu, 'NETWORK_REAL != 0')
        finally:
            import shutil
            urllib.request.urlopen = real
            ct.subprocess.run, ct.RAW_DIR = _run, _raw
            shutil.rmtree(ct.RAW_DIR if False else '/nonexistent', ignore_errors=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
