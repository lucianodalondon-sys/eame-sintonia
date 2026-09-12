#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DA CONVERGENCIA — SCRAP-CV-01.

Duas leis provadas em separado passam a viver na mesma linha:

    SR-02      QUEM / POR QUE / PARA QUE pode gastar?
    C10.8A-F   ATE QUANTO esta execucao pode gastar?

E a pergunta desta suite e se elas continuam a ser DUAS perguntas.

    SPEND_AUTHORIZATION != FINANCIAL_BUDGET != NETWORK_BUDGET

O FORNECEDOR E FALSO SO NA FRONTEIRA EXTERNA
---------------------------------------------
O espiao substitui `subprocess.run` — o processo `curl` que sai da maquina — e
mais nada. Ficam REAIS e por cima dele: `coletor._curl`, o teto de rede, o
orcamento financeiro, `coletor.executar`, a guarda de autorizacao e o portao de
relevancia.

    SE O FAKE FICAR ACIMA DE UM OWNER, A PROVA E INVALIDA.

    NETWORK_REAL = 0 · APIFY_REAL_RUNS = 0 · REAL_COST_USD = 0
"""
import json
import os
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import autorizacao_de_gasto as ag   # noqa: E402
import relevancia_da_fonte as rel   # noqa: E402
import coletor                      # noqa: E402
import scrap_http                   # noqa: E402


def decisao(source_id, proposito, resultado, **kw):
    kw.setdefault('motivo', 'medido nesta prova')
    kw.setdefault('metodo', 'PROVA_BARATA_ACERVO')
    if resultado in rel.RESULTADOS_QUE_AFIRMAM:
        kw.setdefault('evidencia', {'file': 'data/samples/x.json', 'line': 1})
    return rel.Decisao(source_id=source_id, proposito=proposito,
                       resultado=resultado, **kw).para_livro()


class CurlFalso:
    """O mundo externo, e so ele. Conta os POST; nunca abre ligacao.

    Substitui `subprocess.run` DENTRO de `coletor._curl` — portanto o teto de
    rede, que e cobrado uma linha acima, continua a correr de verdade.
    """

    def __init__(self, custos=None):
        self.posts = 0
        self.custos = list(custos or [])
        self.urls = []

    class _R:
        def __init__(self, out):
            self.returncode, self.stdout, self.stderr = 0, out, ''

    def __call__(self, cmd, **k):
        url = cmd[-1]
        self.urls.append(url)
        if '-X' in cmd and cmd[cmd.index('-X') + 1] == 'POST':
            self.posts += 1
            custo = self.custos.pop(0) if self.custos else 0.0
            return self._R(json.dumps({'data': {
                'id': 'FAKE-%d' % self.posts, 'status': 'SUCCEEDED',
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
        self._run = coletor.subprocess.run
        coletor.subprocess.run = self.mundo
        # ── E A PORTA TEM DE SER A PORTA ────────────────────────────────────
        # ⚠️ MEDIDO NA CV-01, na suite inteira e nao aqui isolada:
        # `regras/sensor_coleta.py` faz `coletor._curl = _curl_robusto` no CORPO
        # do modulo. Basta alguem o importar — um teste, um censo — para o
        # transporte da unica porta paga mudar no processo todo. Com ele
        # trocado, fingir o `subprocess` deixa de fingir alguma coisa: o pedido
        # sai por `urllib` e vai MESMO a rede.
        #
        #     UM FAKE QUE JA NAO ESTA NO CAMINHO NAO E UM FAKE. E UM ADORNO.
        #
        # Repor a porta original nao e mockar um owner: e desfazer o mock de
        # outra pessoa, para que o que se mede seja o que se diz que se mede.
        self._curl = coletor._curl
        coletor._curl = coletor._CURL_ORIGINAL
        # A morada do RAW muda-se; o contrato nao. Uma suite que escreve na
        # arvore mede a corrida anterior, nao o codigo.
        self._raw = coletor.RAW_DIR
        self._tmp = tempfile.mkdtemp(prefix='cv01-raw-')
        coletor.RAW_DIR = self._tmp
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
        coletor.subprocess.run = self._run
        coletor._curl = self._curl
        coletor.RAW_DIR = self._raw
        shutil.rmtree(self._tmp, ignore_errors=True)

    # ── os construtores de autorizacao ─────────────────────────────────────
    def trial(self, **kw):
        base = dict(motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9',
                    max_execucoes=1, max_usd=0.10, quem_autorizou='luciano',
                    porque='provar a rota paga', condicao_de_paragem='um POST')
        base.update(kw)
        return ag.autorizar(**base)

    def probe(self, **kw):
        base = dict(motivo=ag.PROVA_DE_RELEVANCIA, proposito='T9',
                    source_id='IT-T9-002', max_execucoes=1, max_usd=0.01,
                    quem_autorizou='luciano', porque='descobrir se serve',
                    condicao_de_paragem='1 execucao')
        base.update(kw)
        return ag.autorizar(**base)

    def normal(self, livro, sid='IT-T9-002', prop='T9', usd=0.05, n=1):
        return ag.autorizar(motivo=ag.COLETA_NORMAL, proposito=prop,
                            source_id=sid, max_usd=usd, max_execucoes=n,
                            livro=livro)

    def comprar(self, autorizacao, *, orcamento=None, rede=None, teto=None, **kw):
        """A porta paga REAL, com os dois tetos reais e o mundo falso na ponta."""
        import contextlib
        base = dict(token='T', run_id='R', platform='P', country='IT',
                    mission='M', query='q', source_version='v',
                    evidence_path='e', salvar_raw=False,
                    autorizacao=autorizacao,
                    proposito=getattr(autorizacao, 'proposito', None),
                    source_id=getattr(autorizacao, 'source_id', None),
                    motivo_do_gasto=getattr(autorizacao, 'motivo', None),
                    teto_usd=teto if teto is not None
                    else getattr(autorizacao, 'max_usd', None))
        base.update(kw)
        with contextlib.ExitStack() as pilha:
            if orcamento is not None:
                pilha.enter_context(coletor.orcamento_financeiro(orcamento))
            if rede is not None:
                pilha.enter_context(scrap_http.orcamento_de_rede(rede))
            return coletor.executar('apify~ator', {}, **base)


# ══════════════════════════════════════════════════════════════════════════
# F · A REPRODUCAO DO DEFEITO — guardada, nao apagada
# ══════════════════════════════════════════════════════════════════════════
class ODefeitoDoMaxUsd(unittest.TestCase):
    """⚠️ ESTE TESTE NASCEU A REPRODUZIR UM DEFEITO, E FICA.

    Na SR-02, `Autorizacao.max_usd` era conferido contra o `teto_usd` de CADA
    chamada e so o numero de execucoes era decrementado. Um limite humano de um
    dolar com duas execucoes representava dois dolares de exposicao:

        max_execucoes = 2 · max_usd = 1.00
        duas chamadas com teto_usd = 1.00
        -> EXPOSICAO REPRESENTADA = 2.00

        CADA POST GANHAVA O LIMITE INTEIRO OUTRA VEZ.

    O conserto nao foi dar um ledger a autorizacao — seria um segundo dono do
    mesmo dinheiro. Foi exigir a RELACAO com o ledger que ja existia.
    """

    def test_a_autorizacao_sozinha_nao_consegue_mais_renovar_o_limite(self):
        a = ag.autorizar(motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9',
                         max_execucoes=2, max_usd=1.00, quem_autorizou='l',
                         porque='p', condicao_de_paragem='2')
        # sem ledger declarado, a compra nao passa: era exactamente aqui que o
        # limite humano renascia inteiro a cada POST.
        with self.assertRaises(ag.GastoRecusado) as c:
            ag.conferir(a, motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9')
        self.assertEqual('SEM_LEDGER_NAO_GASTEI', c.exception.causa)

    def test_o_ledger_nao_pode_declarar_mais_do_que_o_humano_concedeu(self):
        a = ag.autorizar(motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9',
                         max_execucoes=2, max_usd=1.00, quem_autorizou='l',
                         porque='p', condicao_de_paragem='2')
        with self.assertRaises(ag.GastoRecusado) as c:
            ag.conferir(a, motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9',
                        orcamento_autorizado=2.00)
        self.assertEqual('ORCAMENTO_ACIMA_DO_AUTORIZADO', c.exception.causa)

    def test_com_ledger_dentro_do_limite_passa(self):
        a = ag.autorizar(motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9',
                         max_execucoes=2, max_usd=1.00, quem_autorizou='l',
                         porque='p', condicao_de_paragem='2')
        r = ag.conferir(a, motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9',
                        orcamento_autorizado=1.00)
        self.assertEqual(ag.AUTORIZADO, r['VEREDITO'])

    def test_a_autorizacao_nao_ganhou_ledger_proprio(self):
        """O conserto nao pode ter criado um segundo dono do mesmo dinheiro."""
        a = ag.autorizar(motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9',
                         max_execucoes=1, max_usd=0.10, quem_autorizou='l',
                         porque='p', condicao_de_paragem='1')
        for proibido in ('actual_usd', 'remaining_usd', 'committed_usd',
                         'unknown_usd', 'gasto', 'restante', 'comprometido'):
            self.assertFalse(hasattr(a, proibido),
                             'a autorizacao ganhou `%s`: segundo ledger' % proibido)


# ══════════════════════════════════════════════════════════════════════════
# G · MAX RUNS x MAX USD — dois eixos independentes
# ══════════════════════════════════════════════════════════════════════════
class DoisEixosIndependentes(ComMundoFalso):

    def test_duas_execucoes_somam_no_ledger_e_nao_no_limite_humano(self):
        a = self.trial(max_execucoes=2, max_usd=1.00,
                       condicao_de_paragem='2 execucoes')
        self.mundo.custos = [0.40, 0.30]
        with coletor.orcamento_financeiro(1.00) as orc:
            for _ in range(2):
                coletor.executar(
                    'apify~ator', {}, token='T', run_id='R', platform='P',
                    country='IT', mission='M', query='q', source_version='v',
                    evidence_path='e', salvar_raw=False, autorizacao=a,
                    proposito='T9', motivo_do_gasto=ag.TRIAL_DE_CAPACIDADE,
                    teto_usd=1.00)
            self.assertEqual(2, self.mundo.posts)
            self.assertEqual(2, a._gastas, 'AUTH_GASTAS')
            self.assertAlmostEqual(0.70, orc.gasto, places=4)
            self.assertAlmostEqual(0.30, orc.restante, places=4)
            self.assertLessEqual(orc.gasto, 1.00, 'TOTAL_EXPOSURE <= 1.00')

    def test_execucoes_esgotam_antes_do_dinheiro(self):
        """MAX_RUNS e MAX_USD nao sao o mesmo eixo: um pode acabar primeiro."""
        a = self.trial(max_execucoes=1, max_usd=1.00)
        self.mundo.custos = [0.01]
        with coletor.orcamento_financeiro(1.00) as orc:
            self.comprar(a, teto=1.00)
            self.assertGreater(orc.restante, 0.9, 'ainda ha dinheiro')
            with self.assertRaises(ag.GastoRecusado) as c:
                self.comprar(a, teto=1.00, run_id='R2')
            # ⚠️ A recusa diz EXECUCOES, e nao dinheiro. Um sistema que aqui
            # respondesse «sem saldo» mentiria: saldo havia.
            self.assertEqual('AUTORIZACAO_ESGOTADA', c.exception.causa)
        self.assertEqual(1, self.mundo.posts)


# ══════════════════════════════════════════════════════════════════════════
# H · A MATRIZ DOS PORTOES
# ══════════════════════════════════════════════════════════════════════════
class AMatrizDosPortoes(ComMundoFalso):
    """Cada gate recusa pelo SEU motivo, e nenhum se veste do outro."""

    def test_sem_autorizacao_e_com_dinheiro_e_rede_de_sobra(self):
        """Dinheiro disponivel nunca substitui autorizacao."""
        with self.assertRaises(ag.GastoRecusado) as c:
            with coletor.orcamento_financeiro(10.00):
                with scrap_http.orcamento_de_rede(100):
                    coletor.executar(
                        'apify~ator', {}, token='T', run_id='R', platform='P',
                        country='IT', mission='M', query='q', source_version='v',
                        evidence_path='e', salvar_raw=False, teto_usd=0.10)
        self.assertEqual('AUTORIZACAO_AUSENTE', c.exception.causa)
        self.assertEqual(0, self.mundo.posts)

    def test_sem_dinheiro_e_com_autorizacao_e_rede(self):
        """A recusa financeira nao se veste de autorizacao em falta."""
        a = self.trial(max_usd=0.10)
        with coletor.orcamento_financeiro(0.10) as orc:
            orc.reservar(pedido=0.10, ator='x', rota='y', motivo='z')  # esgota
            with self.assertRaises(Exception) as c:
                with scrap_http.orcamento_de_rede(100):
                    coletor.executar(
                        'apify~ator', {}, token='T', run_id='R', platform='P',
                        country='IT', mission='M', query='q', source_version='v',
                        evidence_path='e', salvar_raw=False, autorizacao=a,
                        proposito='T9', motivo_do_gasto=ag.TRIAL_DE_CAPACIDADE,
                        teto_usd=0.10)
        self.assertNotIsInstance(c.exception, ag.GastoRecusado,
                                 'a recusa financeira vestiu-se de autorizacao')
        self.assertEqual(0, self.mundo.posts)
        self.assertEqual(0, a._gastas,
                         'uma execucao autorizada foi queimada por uma compra '
                         'que o dinheiro recusou')

    def test_sem_rede_e_com_autorizacao_e_dinheiro(self):
        """Teto de rede zero: zero POST, e a autorizacao nao se gasta."""
        a = self.trial(max_usd=0.10)
        with self.assertRaises(Exception) as c:
            with coletor.orcamento_financeiro(0.10):
                with scrap_http.orcamento_de_rede(0):
                    coletor.executar(
                        'apify~ator', {}, token='T', run_id='R', platform='P',
                        country='IT', mission='M', query='q', source_version='v',
                        evidence_path='e', salvar_raw=False, autorizacao=a,
                        proposito='T9', motivo_do_gasto=ag.TRIAL_DE_CAPACIDADE,
                        teto_usd=0.10)
        self.assertEqual(0, self.mundo.posts)
        self.assertNotIsInstance(c.exception, ag.GastoRecusado)
        # ⚠️ ESTA LINHA NASCEU DE UM ATAQUE VIVO. A irma financeira deste teste
        # ja exigia a autorizacao intacta; esta nao exigia nada, e o red team
        # mostrou porque: a unidade e consumida imediatamente antes do POST, e o
        # teto de ACESSOS recusa DENTRO do transporte, depois disso. Uma
        # autorizacao de uma execucao morria por uma compra que nunca foi
        # tentada.
        #
        #     UM POST QUE NAO SAIU NAO GASTA UMA AUTORIZACAO.
        self.assertEqual(0, a._gastas,
                         'a rede recusou antes do socket e mesmo assim uma '
                         'execucao autorizada foi queimada')

    def test_o_cap_do_fornecedor_nunca_passa_do_que_resta(self):
        """PROVIDER CAP <= FINANCIAL REMAINING, e nao o teto que o chamador pediu."""
        a = self.trial(max_execucoes=2, max_usd=1.00, condicao_de_paragem='2')
        self.mundo.custos = [0.70, 0.0]
        with coletor.orcamento_financeiro(1.00) as orc:
            for _ in range(2):
                coletor.executar(
                    'apify~ator', {}, token='T', run_id='R', platform='P',
                    country='IT', mission='M', query='q', source_version='v',
                    evidence_path='e', salvar_raw=False, autorizacao=a,
                    proposito='T9', motivo_do_gasto=ag.TRIAL_DE_CAPACIDADE,
                    teto_usd=1.00)          # o chamador pede 1.00 nas DUAS
        caps = [t['PROVIDER_SIDE_CAP'] for t in orc.tentativas if t.get('PROVIDER_SIDE_CAP')]
        self.assertEqual(2, len(caps))
        self.assertAlmostEqual(1.00, caps[0], places=4)
        self.assertLessEqual(caps[1], 0.30 + 1e-9,
                             'o segundo POST recebeu o teto original em vez do saldo')

    def test_a_recusa_de_gasto_nao_e_uma_falha_de_transporte(self):
        """MEDIDO NA CV-01, e era um buraco de verdade.

        `GastoRecusado` herdava de `PermissionError`, que herda de `OSError`. A
        casa inteira tem `except OSError` a apanhar tunel caido — e uma compra
        recusada por falta de autorizacao subia como `TRANSIENT_NETWORK_ERROR`,
        cuja recuperacao canonica e `WAIT`.

            UMA RECUSA QUE PEDE PARA SER REPETIDA NAO E UMA RECUSA.
        """
        import falhas
        e = ag.GastoRecusado('AUTORIZACAO_AUSENTE', 'x')
        self.assertNotIsInstance(e, OSError)
        self.assertNotIsInstance(e, PermissionError)
        # E ela tem nome proprio no vocabulario canonico, com NO_RETRY.
        familia = falhas.traduzir('SPEND_NOT_AUTHORIZED')
        self.assertEqual('BUDGET_EXHAUSTED', familia)
        self.assertEqual('NO_RETRY', falhas.recuperacao(familia))
        self.assertNotEqual(familia, falhas.traduzir('TRANSIENT_NETWORK_ERROR'))

    def test_os_tres_portoes_sobem_com_tres_nomes_diferentes(self):
        """Nenhum dos tres se veste do outro no caminho ate ao executor."""
        import social_rotas
        tres = (scrap_http.SemOrcamentoDeRede, coletor.SemOrcamentoFinanceiro,
                ag.GastoRecusado)
        self.assertEqual(3, len(set(tres)), 'dois portoes partilham a excecao')
        for excecao in tres:
            self.assertTrue(issubclass(excecao, RuntimeError), excecao.__name__)
            self.assertFalse(issubclass(excecao, OSError), excecao.__name__)
        # ⚠️ E aqui NAO se procura a palavra no ficheiro da rota. Procurar
        # `GastoRecusado` no texto acharia tambem um comentario a explicar por
        # que ela passa — e um comentario nao deixa passar nada.
        #
        #     MEDIR O TEXTO NAO E MEDIR O COMPORTAMENTO.
        #
        # Mede-se a COISA: a rota aponta para o mesmo tipo, e o caminho inteiro
        # (rota -> executor -> rasto) esta medido na sentinela C10.8A-F
        # `test_28_em_NORMAL_sem_ledger_ja_nao_se_compra`, que exige
        # `RESULT == SPEND_NOT_AUTHORIZED` e zero POST.
        self.assertIs(ag.GastoRecusado, social_rotas.GastoRecusado)
        self.assertIs(coletor.SemOrcamentoFinanceiro,
                      social_rotas.SemOrcamentoFinanceiro)


# ══════════════════════════════════════════════════════════════════════════
# I · ROTACAO DE CHAVE
# ══════════════════════════════════════════════════════════════════════════
class RotacaoDeChave(ComMundoFalso):

    def test_quatro_chaves_nao_renovam_uma_execucao_autorizada(self):
        a = self.trial(max_execucoes=1, max_usd=0.10)
        with coletor.orcamento_financeiro(0.10) as orc:
            saiu = 0
            for chave in ('k1', 'k2', 'k3', 'k4'):
                try:
                    coletor.executar(
                        'apify~ator', {}, token=chave, run_id='R', platform='P',
                        country='IT', mission='M', query='q', source_version='v',
                        evidence_path='e', salvar_raw=False, autorizacao=a,
                        proposito='T9', motivo_do_gasto=ag.TRIAL_DE_CAPACIDADE,
                        teto_usd=0.10)
                    saiu += 1
                except ag.GastoRecusado:
                    pass
            self.assertEqual(1, saiu)
            self.assertEqual(1, self.mundo.posts)
            self.assertEqual(1, a._gastas)
            self.assertLessEqual(orc.exposto_micros, orc.limite_micros,
                                 'token novo renovou o saldo')


# ══════════════════════════════════════════════════════════════════════════
# J · POST TALVEZ CRIADO
# ══════════════════════════════════════════════════════════════════════════
class OPostQueTalvezSaiu(ComMundoFalso):
    """O POST saiu e a resposta perdeu-se. O dinheiro NAO volta.

    ⚠️ `executar` NAO levanta neste caso, e isso foi MEDIDO, nao presumido: a
    casa trata falha como ESTADO (`STATUS: FAILED` no manifesto), nao como
    excecao. A primeira versao deste teste esperava `RuntimeError` e passaria a
    dar por bom qualquer caminho que nao levantasse — inclusive um que
    devolvesse o dinheiro. Mede-se o manifesto e o saldo.
    """

    def test_a_exposicao_fica_desconhecida_e_a_autorizacao_fica_gasta(self):
        a = self.trial(max_execucoes=2, max_usd=0.20, condicao_de_paragem='2')

        def cai_no_post(cmd, **k):
            if '-X' in cmd and cmd[cmd.index('-X') + 1] == 'POST':
                self.mundo.posts += 1              # o POST SAIU
                r = CurlFalso._R('')
                r.returncode, r.stderr = 56, 'ws_closed_mid_exchange'
                return r
            return CurlFalso._R('{"data": {}}')    # e nenhuma execucao e achada
        coletor.subprocess.run = cai_no_post

        with coletor.orcamento_financeiro(0.20) as orc:
            _itens, m = coletor.executar(
                'apify~ator', {}, token='T', run_id='R', platform='P',
                country='IT', mission='M', query='q', source_version='v',
                evidence_path='e', salvar_raw=False, autorizacao=a,
                proposito='T9', motivo_do_gasto=ag.TRIAL_DE_CAPACIDADE,
                teto_usd=0.20)
            self.assertEqual('FAILED', m['STATUS'])
            self.assertEqual(1, self.mundo.posts, 'o POST saiu')
            self.assertEqual(1, a._gastas,
                             'POST QUE SAIU tem de consumir a autorizacao')
            self.assertGreater(orc.desconhecido, 0,
                               'a exposicao desconhecida desapareceu')
            self.assertLess(orc.restante, 0.20,
                            'o saldo voltou como se nada tivesse saido')
            # ⚠️ E a recusa NAO se veste de fonte: quem le o manifesto tem de
            # conseguir distinguir «o transporte caiu no nosso POST» de «a
            # Apify disse que nao».
            self.assertEqual('NO', m['RUN_ADOPTED_AFTER_TRANSPORT_LOSS'])

    def test_nao_ha_segundo_post_automatico(self):
        a = self.trial(max_execucoes=2, max_usd=0.20, condicao_de_paragem='2')
        posts = []

        def cai(cmd, **k):
            if '-X' in cmd and cmd[cmd.index('-X') + 1] == 'POST':
                posts.append(1)
                r = CurlFalso._R('')
                r.returncode = 56
                return r
            return CurlFalso._R('{"data": {}}')
        coletor.subprocess.run = cai
        with coletor.orcamento_financeiro(0.20):
            coletor.executar(
                'apify~ator', {}, token='T', run_id='R', platform='P',
                country='IT', mission='M', query='q', source_version='v',
                evidence_path='e', salvar_raw=False, autorizacao=a,
                proposito='T9', motivo_do_gasto=ag.TRIAL_DE_CAPACIDADE,
                teto_usd=0.20)
        self.assertEqual(1, len(posts), 'o POST foi repetido: pagou duas vezes')
        self.assertEqual(1, a._gastas,
                         'um POST, uma unidade — nem zero nem duas')


# ══════════════════════════════════════════════════════════════════════════
# K/L/M · PROBE · TRIAL · COLETA NORMAL
# ══════════════════════════════════════════════════════════════════════════
class OsTresMotivos(ComMundoFalso):

    def test_probe_passa_com_a_fonte_nao_avaliada(self):
        a = self.probe()
        self.comprar(a, orcamento=0.01, rede=10)
        self.assertEqual(1, self.mundo.posts)

    def test_probe_nao_promove_a_fonte(self):
        a = self.probe()
        self.comprar(a, orcamento=0.01, rede=10)
        self.assertEqual(rel.NAO_AVALIADA,
                         rel.portao('IT-T9-002', 'T9', [],
                                    custo='gratuito')['ESTADO_DA_RELEVANCIA'])

    def test_trial_nao_nomeia_fonte_e_nao_vira_coleta(self):
        a = self.trial()
        self.assertIsNone(a.source_id)
        self.comprar(a, orcamento=0.10, rede=10)
        self.assertEqual(1, self.mundo.posts)
        # e nao serve para coleta normal
        with self.assertRaises(ag.GastoRecusado) as c:
            ag.conferir(a, motivo=ag.COLETA_NORMAL, proposito='T9',
                        orcamento_autorizado=0.10)
        self.assertEqual('AUTORIZACAO_NAO_COBRE_ESTE_MOTIVO', c.exception.causa)

    def test_coleta_normal_so_com_sim_no_proposito_certo(self):
        livro = [decisao('IT-T9-002', 'T9', rel.SIM)]
        a = self.normal(livro)
        self.comprar(a, orcamento=0.05, rede=10)
        self.assertEqual(1, self.mundo.posts)

    def test_as_quatro_ausencias_dao_zero_post(self):
        for r in (rel.NAO, rel.NAO_SEI, rel.ERRO):
            with self.subTest(resultado=r):
                with self.assertRaises(ag.AutorizacaoInvalida) as c:
                    self.normal([decisao('IT-T9-002', 'T9', r)])
                self.assertIn(r, str(c.exception))
                self.assertNotIn('NOT_RELEVANT', str(c.exception))
        with self.assertRaises(ag.AutorizacaoInvalida) as c:
            self.normal([])
        self.assertIn(rel.NAO_AVALIADA, str(c.exception))
        self.assertEqual(0, self.mundo.posts)

    def test_sim_em_t3_nao_compra_em_t9(self):
        livro = [decisao('IT-T9-002', 'T3', rel.SIM)]
        with self.assertRaises(ag.AutorizacaoInvalida):
            self.normal(livro, prop='T9')
        a = self.normal(livro, prop='T3')
        self.comprar(a, orcamento=0.05, rede=10)
        self.assertEqual(1, self.mundo.posts)


# ══════════════════════════════════════════════════════════════════════════
# M · A UNIDADE AUTORIZADA — quando volta, e quando NAO volta
# ══════════════════════════════════════════════════════════════════════════
class AUnidadeAutorizada(ComMundoFalso):
    """Consumir, devolver, e as duas portas que nao se abrem a qualquer um."""

    def test_consumir_duas_vezes_uma_autorizacao_de_uma_execucao(self):
        """`consumir` NAO confia em ter sido precedido de `conferir`.

        Ela e uma funcao publica: quem a chamar sem passar pela conferencia tem
        de encontrar a mesma parede. Uma guarda que so vale quando outra guarda
        correu antes e uma guarda que nao vale.
        """
        a = self.trial(max_execucoes=1, max_usd=0.10)
        ag.consumir(a)
        with self.assertRaises(ag.GastoRecusado) as c:
            ag.consumir(a)
        self.assertEqual('AUTORIZACAO_ESGOTADA', c.exception.causa)

    def test_devolver_nao_aceita_uma_autorizacao_que_ninguem_concedeu(self):
        """A porta de volta e tao estreita como a de ida.

        Se `devolver` aceitasse um objecto qualquer, bastava fabricar um para
        repor a contagem de uma autorizacao verdadeira — a mesma forja, pelo
        lado de dentro.
        """
        import dataclasses
        a = self.trial(max_execucoes=2, max_usd=0.10, condicao_de_paragem='2')
        ag.consumir(a)
        falsa = dataclasses.replace(a)
        with self.assertRaises(ag.GastoRecusado) as c:
            ag.devolver(falsa, 'porque sim')
        self.assertEqual('AUTORIZACAO_FABRICADA', c.exception.causa)
        self.assertEqual(1, a._gastas, 'a copia mexeu na original')

    def test_uma_recusa_DEPOIS_do_POST_nao_devolve_a_execucao(self):
        """O teto de acessos acaba no meio: o POST SAIU, e ele nao volta atras.

        ⚠️ ESTE E O OUTRO LADO DA LEI, e o lado que se esquece. Devolver a
        unidade e legitimo quando ha PROVA de que nada foi comprado. Aqui nao ha:
        o POST saiu e o que faltou foi a ida seguinte, a de LEITURA.

            AUSENCIA DE NOTICIA NAO E PROVA DE AUSENCIA DE COMPRA.
        """
        a = self.trial(max_execucoes=2, max_usd=0.20, condicao_de_paragem='2')
        with coletor.orcamento_financeiro(0.20):
            with scrap_http.orcamento_de_rede(1):     # chega para o POST, e mais nada
                with self.assertRaises(scrap_http.SemOrcamentoDeRede):
                    self.comprar(a, orcamento=None, teto=0.20)
        self.assertEqual(1, self.mundo.posts, 'o POST saiu')
        self.assertEqual(1, a._gastas,
                         'a execucao voltou depois de o POST ter saido')

    def test_uma_autorizacao_forjada_morre_antes_de_comprometer_dinheiro(self):
        """O gate barato corre primeiro, e nao queima nada ao recusar.

        Uma forja apanhada DEPOIS da reserva ja custou saldo a uma compra que
        nunca ia acontecer — e numa execucao com varias chamadas, esse saldo
        falta a seguir.

            UM GATE BARATO CORRE PRIMEIRO, E NAO QUEIMA NADA AO RECUSAR.
        """
        import dataclasses
        a = self.trial(max_execucoes=1, max_usd=0.10)
        falsa = dataclasses.replace(a, max_execucoes=99)
        with coletor.orcamento_financeiro(0.10) as orc:
            with self.assertRaises(ag.GastoRecusado) as c:
                self.comprar(falsa, orcamento=None, teto=0.10)
        self.assertEqual('AUTORIZACAO_FABRICADA', c.exception.causa)
        self.assertEqual(0, self.mundo.posts)
        self.assertEqual(0, orc.exposto_micros,
                         'a forja comprometeu dinheiro antes de ser apanhada')
        self.assertEqual([], orc.tentativas,
                         'a forja deixou uma tentativa no ledger')


# ══════════════════════════════════════════════════════════════════════════
# N · O TRANSPORTE TROCADO — e o que ele levava consigo
# ══════════════════════════════════════════════════════════════════════════
class OTransporteTrocado(unittest.TestCase):
    """`regras/sensor_coleta.py` substitui o transporte da porta paga.

    A troca esta declarada e tem motivo escrito (o subprocesso `curl` perdia
    stdout no runner). O que NAO estava declarado e o que ela levava consigo: a
    substituicao herdava a porta e perdia as duas politicas que a porta tinha.

        TROCAR O TRANSPORTE NAO PODE TROCAR QUEM CONTA AS IDAS,
        E NAO PODE RESSUSCITAR A RETENTATIVA DO POST.
    """

    def setUp(self):
        import sensor_coleta
        self.sensor = sensor_coleta
        self._curl = coletor._curl
        self.addCleanup(self._repor)

    def _repor(self):
        coletor._curl = self._curl

    def test_o_transporte_substituto_pede_autorizacao_ao_dono_da_rede(self):
        """Teto de acessos ZERO: a ida nao sai, venha por curl ou por urllib."""
        import urllib.request
        saiu = []

        def urlopen_falso(req, *a, **k):
            saiu.append(getattr(req, 'full_url', str(req)))
            raise AssertionError('o pedido SAIU com o teto de acessos a zero')

        real = urllib.request.urlopen
        urllib.request.urlopen = urlopen_falso
        try:
            with scrap_http.orcamento_de_rede(0):
                with self.assertRaises(scrap_http.SemOrcamentoDeRede):
                    self.sensor._curl_robusto('https://api.apify.com/v2/acts/x/runs',
                                              token='T', metodo='POST', corpo={})
        finally:
            urllib.request.urlopen = real
        self.assertEqual([], saiu, 'o transporte substituto ignorou o teto de rede')

    def test_o_transporte_substituto_nao_repete_o_POST(self):
        """MEDIDO NA CV-01: ele repetia ate 4 vezes — e cada repeticao compra.

        `coletor._curl` deixou de repetir POST em 2026-09-02, com a razao
        escrita: se o pedido CHEGOU e so a resposta se perdeu, repetir nao
        repete um pedido perdido, acende uma segunda execucao paga. A
        substituicao ficou com o comportamento anterior — o mesmo POST, pela
        mesma porta, ate 4 compras.

            REPETIR UM GET E BARATO. REPETIR UM POST E COMPRAR DE NOVO.
        """
        import urllib.request
        tentativas = []

        def urlopen_falso(req, *a, **k):
            tentativas.append(req.get_method())
            raise OSError('ws_closed_mid_exchange')

        real = urllib.request.urlopen
        urllib.request.urlopen = urlopen_falso
        try:
            with self.assertRaises(coletor.PostTalvezCriado):
                self.sensor._curl_robusto('https://api.apify.com/v2/acts/x/runs',
                                          token='T', metodo='POST', corpo={})
            self.assertEqual(1, len(tentativas),
                             'o POST saiu %d vezes: comprou %d vezes'
                             % (len(tentativas), len(tentativas)))
            tentativas[:] = []
            with self.assertRaises(RuntimeError):
                self.sensor._curl_robusto('https://api.apify.com/v2/acts/x',
                                          token='T')
            self.assertEqual(4, len(tentativas), 'o GET deixou de retentar')
        finally:
            urllib.request.urlopen = real

    def test_a_porta_guarda_o_seu_transporte_original(self):
        """Sem isto, quem mede nao consegue provar que esta a medir a porta."""
        self.assertTrue(hasattr(coletor, '_CURL_ORIGINAL'))
        self.assertEqual('coletor', coletor._CURL_ORIGINAL.__module__)
        # E a troca do sensor E REAL: importa-lo mudou a porta.
        self.assertIsNot(coletor._CURL_ORIGINAL, self.sensor._curl_robusto)


# ══════════════════════════════════════════════════════════════════════════
# OS DONOS NAO SE MISTURAM
# ══════════════════════════════════════════════════════════════════════════
class OsDonosNaoSeMisturam(unittest.TestCase):

    def test_o_coletor_nao_le_o_livro_de_relevancia(self):
        fonte = open(os.path.join(RAIZ, 'coleta', 'coletor.py'), encoding='utf-8').read()
        self.assertNotIn('import relevancia_da_fonte', fonte)
        self.assertNotIn('LIVRO-DE-RELEVANCIA', fonte)

    def test_o_apify_pool_nao_decide_nada(self):
        fonte = open(os.path.join(RAIZ, 'ferramentas', 'apify_pool.py'),
                     encoding='utf-8').read()
        for proibido in ('relevancia_da_fonte', 'autorizacao_de_gasto',
                         'orcamento_financeiro', 'SOURCE_RELEVANCE'):
            self.assertNotIn(proibido, fonte)

    def test_a_guarda_nao_recebe_token_nem_conta_dinheiro(self):
        """A guarda nao tem credencial e nao tem ledger — MEDIDO, nao lido.

        ⚠️ A primeira versao deste teste procurava a PALAVRA `OrcamentoFinanceiro`
        no ficheiro da lei, e falhava — porque a lei FALA do orcamento no
        cabecalho, exactamente para explicar por que o ledger nao e dela.
        Procurar a palavra encontra a propria defesa da lei. Procura-se a COISA:
        o que o modulo EXPOE e o que ele FAZ.

            MEDIR O TEXTO DA LEI NAO E MEDIR O COMPORTAMENTO DA LEI.
        """
        import inspect
        import types
        for fn in (ag.autorizar, ag.conferir, ag.consumir):
            p = set(inspect.signature(fn).parameters)
            self.assertFalse(p & {'token', 'credencial', 'orcamento', 'ledger'},
                             '%s: %s' % (fn.__name__, p))

        # ── NAO EXPOE NADA DE LEDGER ────────────────────────────────────────
        for nome in ('OrcamentoFinanceiro', 'Reserva', 'reservar', 'liquidar',
                     'desconhecer', 'anular', 'coletor', 'subprocess'):
            self.assertFalse(hasattr(ag, nome),
                             'leis/autorizacao_de_gasto expoe %s' % nome)

        # ── E NAO IMPORTOU O DONO DA EXECUCAO PAGA ──────────────────────────
        importados = [getattr(v, '__name__', '') for v in vars(ag).values()
                      if isinstance(v, types.ModuleType)]
        for proibido in ('coletor', 'apify_pool', 'scrap_http'):
            self.assertNotIn(proibido, importados)

        # ── E NAO CONTA DOLARES: conta EXECUCOES ────────────────────────────
        # `conferir` e de graca e nao mexe em nada; `consumir` gasta UMA unidade
        # e o dinheiro fica exactamente onde estava. Quem soma dolares e o
        # `OrcamentoFinanceiro`, e ele vive noutro ficheiro.
        a = ag.autorizar(motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9',
                         max_execucoes=2, max_usd=0.20,
                         quem_autorizou='humano', porque='medir a guarda',
                         condicao_de_paragem='2 execucoes')
        antes = dict(a.para_o_manifesto())
        ag.conferir(a, motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9',
                    orcamento_autorizado=0.20)
        self.assertEqual(antes, a.para_o_manifesto(),
                         'conferir mexeu no estado: um gate barato queimou algo')
        ag.consumir(a)
        self.assertEqual(antes['MAX_USD'], a.max_usd, 'a guarda mexeu em dolares')
        self.assertEqual(1, a.max_execucoes - a.restantes,
                         'a guarda conta EXECUCOES, e foi so uma')

    def test_o_dono_da_relevancia_nao_conhece_dinheiro(self):
        fonte = open(os.path.join(RAIZ, 'leis', 'relevancia_da_fonte.py'),
                     encoding='utf-8').read()
        for proibido in ('apify_pool', 'APIFY_TOKEN', 'import coletor',
                         'autorizacao_de_gasto'):
            self.assertNotIn(proibido, fonte)

    def test_o_teto_de_rede_continua_dono_unico(self):
        """O coletor PEDE ao dono da rede; nao conta nada."""
        fonte = open(os.path.join(RAIZ, 'coleta', 'coletor.py'), encoding='utf-8').read()
        self.assertIn('scrap_http', fonte)
        self.assertIn('_http.orcamento_actual()', fonte)
        self.assertNotIn('class OrcamentoDeRede', fonte)


if __name__ == '__main__':
    unittest.main(verbosity=2)
