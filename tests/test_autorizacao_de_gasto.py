#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DA AUTORIZACAO DE GASTO — nenhuma compra sem quem responda por ela.

    O FORNECEDOR E FALSO SO NA FRONTEIRA EXTERNA.

`coletor._curl` e substituido por um espiao que CONTA os POST e nunca sai da
maquina. Tudo o resto — a guarda, o portao de relevancia, o manifesto, a
rotacao — e o codigo real. Fingir a guarda provaria que o teste passa, nao que
a porta fecha.

    APIFY_REAL_RUNS = 0 · PROVIDER_START_POSTS_REAL = 0 · REAL_COST_USD = 0
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import autorizacao_de_gasto as ag   # noqa: E402
import relevancia_da_fonte as rel   # noqa: E402
import coletor                      # noqa: E402


def decisao(source_id, proposito, resultado, **kw):
    kw.setdefault('motivo', 'medido nesta prova')
    kw.setdefault('metodo', 'PROVA_BARATA_ACERVO')
    if resultado in rel.RESULTADOS_QUE_AFIRMAM:
        kw.setdefault('evidencia', {'file': 'data/samples/x.json', 'line': 1})
    return rel.Decisao(source_id=source_id, proposito=proposito,
                       resultado=resultado, **kw).para_livro()


class ContadorDePost:
    """O fornecedor, fingido SO na fronteira. Conta POST; nunca abre ligacao."""

    def __init__(self):
        self.posts = 0
        self.gets = 0

    def __call__(self, url, *, token, metodo='GET', corpo=None, timeout=300,
                 tentativas=4):
        if str(metodo).upper() == 'POST':
            self.posts += 1
            return {'data': {'id': 'FAKE-RUN-%d' % self.posts, 'status': 'SUCCEEDED',
                             'startedAt': '2026-09-12T00:00:00.000Z',
                             'finishedAt': '2026-09-12T00:00:01.000Z',
                             'defaultDatasetId': 'FAKE-DS', 'buildNumber': '0.0.1',
                             'usageTotalUsd': 0.0}}
        self.gets += 1
        if '/datasets/' in url:
            return []
        return {'data': {}}


class ComFornecedorFalso(unittest.TestCase):
    """⚠️ E A PROVA NAO ESCREVE NA ARVORE.

    `coletor.executar` grava o RAW por omissao (`salvar_raw=True`), e a primeira
    versao desta suite deixou seis ficheiros falsos em `data/samples/raw-paid/`
    — bytes de mentira, com nome de coleta de verdade. Na corrida seguinte, sete
    testes de proveniencia que nada tem a ver com esta missao reprovaram por
    causa deles.

        UMA SUITE QUE ESCREVE NA ARVORE MEDE A CORRIDA ANTERIOR, NAO O CODIGO.

    `_nao_escrever()` desliga a gravacao para toda a suite, e `tearDown` confere
    que nenhum ficheiro novo ficou para tras.
    """

    def setUp(self):
        self.espiao = ContadorDePost()
        self._curl = coletor._curl
        coletor._curl = self.espiao
        self._raiz = coletor.ROOT
        # A MORADA DO RAW MUDA-SE PARA UMA PASTA TEMPORARIA. Os adaptadores
        # chamam `executar` com `salvar_raw=True` por omissao e nao ha por onde
        # lhes passar outra coisa — entao muda-se o destino, nao o contrato.
        import tempfile
        self._raw_dir = coletor.RAW_DIR
        self._tmp = tempfile.mkdtemp(prefix='raw-de-prova-')
        coletor.RAW_DIR = self._tmp
        self._antes_raw = self._listar_raw()
        self.addCleanup(self._repor)
        self.addCleanup(self._conferir_que_nada_ficou)

    def _listar_raw(self):
        d = os.path.join(RAIZ, 'data', 'samples', 'raw-paid')
        return set(os.listdir(d)) if os.path.isdir(d) else set()

    def _conferir_que_nada_ficou(self):
        novos = self._listar_raw() - self._antes_raw
        for n in novos:
            os.remove(os.path.join(RAIZ, 'data', 'samples', 'raw-paid', n))
        assert not novos, 'a prova deixou RAW falso na arvore: %s' % sorted(novos)

    def _repor(self):
        import shutil
        coletor._curl = self._curl
        coletor.RAW_DIR = self._raw_dir
        shutil.rmtree(self._tmp, ignore_errors=True)

    def correr(self, autorizacao, **kw):
        """A porta paga real, com o fornecedor fingido na ponta."""
        return coletor.executar(
            'apify~ator-de-prova', {'q': 'x'},
            token='TOKEN-DE-PROVA', run_id='PROVA-0001',
            platform='INSTAGRAM', country='IT', mission='PROVA',
            query='https://exemplo.it', source_version='prova',
            evidence_path='data/samples/PROVA.json', salvar_raw=False,
            autorizacao=autorizacao,
            proposito=getattr(autorizacao, 'proposito', None),
            source_id=getattr(autorizacao, 'source_id', None),
            motivo_do_gasto=getattr(autorizacao, 'motivo', None),
            teto_usd=getattr(autorizacao, 'max_usd', None), **kw)


# ══════════════════════════════════════════════════════════════════════════
# FASE 9 · COLETA NORMAL
# ══════════════════════════════════════════════════════════════════════════
class ColetaNormal(ComFornecedorFalso):
    """SIM no proposito certo passa; tudo o resto da ZERO POST."""

    def autorizacao_para(self, livro, source_id='IT-T9-002', proposito='T9'):
        return ag.autorizar(motivo=ag.COLETA_NORMAL, proposito=proposito,
                            source_id=source_id, max_usd=0.05, livro=livro)

    def test_A_sim_no_proposito_certo_deixa_comprar(self):
        livro = [decisao('IT-T9-002', 'T9', rel.SIM)]
        a = self.autorizacao_para(livro)
        itens, man = self.correr(a)
        self.assertEqual(1, self.espiao.posts)
        self.assertEqual(ag.AUTORIZADO, man['AUTORIZACAO_DE_GASTO']['VEREDITO'])
        self.assertEqual('IT-T9-002', man['AUTORIZACAO_DE_GASTO']['SOURCE_ID'])

    def test_B_nao_da_zero_post(self):
        livro = [decisao('IT-T9-002', 'T9', rel.NAO)]
        with self.assertRaises(ag.AutorizacaoInvalida) as c:
            self.autorizacao_para(livro)
        self.assertIn('RELEVANCIA_NAO_AUTORIZA', str(c.exception))
        self.assertEqual(0, self.espiao.posts)

    def test_C_nao_sei_da_zero_post_e_nao_diz_que_a_fonte_nao_serve(self):
        livro = [decisao('IT-T9-002', 'T9', rel.NAO_SEI)]
        with self.assertRaises(ag.AutorizacaoInvalida) as c:
            self.autorizacao_para(livro)
        self.assertEqual(0, self.espiao.posts)
        self.assertIn(rel.NAO_SEI, str(c.exception))
        self.assertNotIn('NOT_RELEVANT', str(c.exception))

    def test_D_erro_da_zero_post_e_continua_a_ser_erro(self):
        livro = [decisao('IT-T9-002', 'T9', rel.ERRO)]
        with self.assertRaises(ag.AutorizacaoInvalida) as c:
            self.autorizacao_para(livro)
        self.assertEqual(0, self.espiao.posts)
        self.assertIn(rel.ERRO, str(c.exception))

    def test_E_nao_avaliada_da_zero_post(self):
        with self.assertRaises(ag.AutorizacaoInvalida) as c:
            self.autorizacao_para([])
        self.assertEqual(0, self.espiao.posts)
        self.assertIn(rel.NAO_AVALIADA, str(c.exception))

    def test_F_sim_em_t3_nao_compra_para_t9(self):
        """A relevancia nao vaza entre propositos, e o dinheiro tambem nao."""
        livro = [decisao('IT-T9-002', 'T3', rel.SIM)]
        with self.assertRaises(ag.AutorizacaoInvalida):
            self.autorizacao_para(livro, proposito='T9')
        self.assertEqual(0, self.espiao.posts)
        # e a mesma decisao compra para T3
        a = self.autorizacao_para(livro, proposito='T3')
        self.correr(a)
        self.assertEqual(1, self.espiao.posts)

    def test_sem_autorizacao_nenhuma_da_zero_post(self):
        with self.assertRaises(ag.GastoRecusado) as c:
            self.correr(None)
        self.assertEqual('AUTORIZACAO_AUSENTE', c.exception.causa)
        self.assertEqual(0, self.espiao.posts)

    def test_a_recusa_nao_e_falha_da_plataforma(self):
        """Uma recusa nossa nao pode sair como corrida FAILED."""
        with self.assertRaises(ag.GastoRecusado):
            self.correr(None)
        self.assertEqual(0, self.espiao.posts)
        self.assertEqual(0, self.espiao.gets)


# ══════════════════════════════════════════════════════════════════════════
# FASE 10 · PROVA DE RELEVANCIA (o probe que quebra o ciclo)
# ══════════════════════════════════════════════════════════════════════════
class ProvaDeRelevancia(ComFornecedorFalso):

    def probe(self, **kw):
        base = dict(motivo=ag.PROVA_DE_RELEVANCIA, proposito='T9',
                    source_id='IT-T9-002', max_execucoes=1, max_usd=0.01,
                    quem_autorizou='luciano',
                    porque='descobrir se a conta publica material tecnico',
                    condicao_de_paragem='1 execucao ou 1 item')
        base.update(kw)
        return ag.autorizar(**base)

    def test_probe_passa_com_a_fonte_ainda_nao_avaliada(self):
        """O ciclo quebrado: nao exige SIM, porque existe para descobrir o SIM."""
        a = self.probe(livro=[])
        itens, man = self.correr(a)
        self.assertEqual(1, self.espiao.posts)
        self.assertEqual(ag.PROVA_DE_RELEVANCIA,
                         man['AUTORIZACAO_DE_GASTO']['MOTIVO_DO_GASTO'])

    def test_probe_nao_promove_a_fonte(self):
        """PROBE != RELEVANCE DECISION."""
        a = self.probe(livro=[])
        self.correr(a)
        # o livro continua vazio: gastar nao escreve decisao nenhuma
        self.assertEqual(rel.NAO_AVALIADA,
                         rel.portao('IT-T9-002', 'T9', [],
                                    custo='gratuito')['ESTADO_DA_RELEVANCIA'])

    def test_probe_sem_autorizacao_humana_e_recusado(self):
        with self.assertRaises(ag.AutorizacaoInvalida) as c:
            self.probe(quem_autorizou='')
        self.assertIn('SEM_AUTORIZACAO_HUMANA', str(c.exception))

    def test_probe_sem_teto_de_execucoes_e_recusado(self):
        with self.assertRaises(ag.AutorizacaoInvalida) as c:
            self.probe(max_execucoes=0)
        self.assertIn('SEM_TETO_DE_EXECUCOES', str(c.exception))

    def test_probe_sem_teto_de_dolares_e_recusado(self):
        with self.assertRaises(ag.AutorizacaoInvalida) as c:
            self.probe(max_usd=None)
        self.assertIn('SEM_TETO_DE_DOLARES', str(c.exception))

    def test_probe_sem_condicao_de_paragem_e_recusado(self):
        with self.assertRaises(ag.AutorizacaoInvalida) as c:
            self.probe(condicao_de_paragem='')
        self.assertIn('SEM_CONDICAO_DE_PARAGEM', str(c.exception))

    def test_probe_sem_fonte_nomeada_e_recusado(self):
        """Um probe que nao nomeia a fonte e coleta com outro nome."""
        with self.assertRaises(ag.AutorizacaoInvalida) as c:
            self.probe(source_id=None)
        self.assertIn('FONTE_AUSENTE', str(c.exception))

    def test_probe_nao_vira_coleta_ilimitada(self):
        a = self.probe(max_execucoes=1)
        self.correr(a)
        with self.assertRaises(ag.GastoRecusado) as c:
            self.correr(a)
        self.assertEqual('AUTORIZACAO_ESGOTADA', c.exception.causa)
        self.assertEqual(1, self.espiao.posts)


# ══════════════════════════════════════════════════════════════════════════
# FASE 11 · TRIAL DE CAPACIDADE
# ══════════════════════════════════════════════════════════════════════════
class TrialDeCapacidade(ComFornecedorFalso):

    def trial(self, **kw):
        base = dict(motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9',
                    max_execucoes=1, max_usd=0.10, quem_autorizou='luciano',
                    porque='provar que a rota paga atravessa ponta a ponta',
                    condicao_de_paragem='um POST, e para')
        base.update(kw)
        return ag.autorizar(**base)

    def test_trial_nao_depende_de_relevancia_de_fonte(self):
        """TRIAL mede o CAMINHO, nao a fonte. Por isso nao nomeia fonte."""
        a = self.trial(livro=[])
        self.assertIsNone(a.source_id)
        self.correr(a)
        self.assertEqual(1, self.espiao.posts)

    def test_trial_exige_autorizacao_humana_e_tetos(self):
        for campo, valor, causa in (('quem_autorizou', '', 'SEM_AUTORIZACAO_HUMANA'),
                                    ('max_execucoes', 0, 'SEM_TETO_DE_EXECUCOES'),
                                    ('max_usd', None, 'SEM_TETO_DE_DOLARES'),
                                    ('condicao_de_paragem', '', 'SEM_CONDICAO_DE_PARAGEM')):
            with self.subTest(campo=campo):
                with self.assertRaises(ag.AutorizacaoInvalida) as c:
                    self.trial(**{campo: valor})
                self.assertIn(causa, str(c.exception))

    def test_um_so_post(self):
        a = self.trial(max_execucoes=1)
        self.correr(a)
        with self.assertRaises(ag.GastoRecusado):
            self.correr(a)
        self.assertEqual(1, self.espiao.posts)

    def test_trial_nao_se_apresenta_como_coleta_normal(self):
        """TRIAL != COLLECTION: a autorizacao nao serve para o outro motivo."""
        a = self.trial()
        with self.assertRaises(ag.GastoRecusado) as c:
            coletor.executar(
                'apify~ator', {}, token='T', run_id='R', platform='P', country='IT',
                mission='M', query='q', source_version='v', evidence_path='e',
                salvar_raw=False, autorizacao=a, proposito='T9',
                motivo_do_gasto=ag.COLETA_NORMAL, teto_usd=0.10)
        self.assertEqual('AUTORIZACAO_NAO_COBRE_ESTE_MOTIVO', c.exception.causa)
        self.assertEqual(0, self.espiao.posts)

    def test_coleta_normal_nao_se_disfarca_de_trial(self):
        """O caminho inverso: chamar-se TRIAL nao dispensa a autorizacao de TRIAL."""
        livro = [decisao('IT-T9-002', 'T9', rel.SIM)]
        a = ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                         source_id='IT-T9-002', max_usd=0.05, livro=livro)
        with self.assertRaises(ag.GastoRecusado) as c:
            coletor.executar(
                'apify~ator', {}, token='T', run_id='R', platform='P', country='IT',
                mission='M', query='q', source_version='v', evidence_path='e',
                salvar_raw=False, autorizacao=a, proposito='T9',
                source_id='IT-T9-002', motivo_do_gasto=ag.TRIAL_DE_CAPACIDADE,
                teto_usd=0.05)
        self.assertEqual('AUTORIZACAO_NAO_COBRE_ESTE_MOTIVO', c.exception.causa)


# ══════════════════════════════════════════════════════════════════════════
# A AUTORIZACAO NAO SE FABRICA, NAO SE REUSA, NAO SE ESTICA
# ══════════════════════════════════════════════════════════════════════════
class AAutorizacaoNaoSeFabrica(ComFornecedorFalso):

    def test_construir_a_mao_levanta(self):
        with self.assertRaises(ag.AutorizacaoInvalida):
            ag.Autorizacao(motivo=ag.COLETA_NORMAL, proposito='T9',
                           source_id='IT-T9-002', max_execucoes=99, max_usd=99.0,
                           quem_autorizou='eu', porque='porque sim',
                           condicao_de_paragem='nunca')

    def test_um_dicionario_parecido_nao_passa(self):
        falsa = type('Falsa', (), {'motivo': ag.COLETA_NORMAL, 'proposito': 'T9',
                                   'source_id': 'IT-T9-002', 'max_usd': 99.0,
                                   'restantes': 99})()
        with self.assertRaises(ag.GastoRecusado) as c:
            self.correr(falsa)
        self.assertEqual('AUTORIZACAO_FABRICADA', c.exception.causa)
        self.assertEqual(0, self.espiao.posts)

    def test_autorizacao_nao_atravessa_para_outra_fonte(self):
        livro = [decisao('IT-T9-002', 'T9', rel.SIM)]
        a = ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                         source_id='IT-T9-002', max_usd=0.05, livro=livro)
        with self.assertRaises(ag.GastoRecusado) as c:
            coletor.executar(
                'apify~ator', {}, token='T', run_id='R', platform='P', country='IT',
                mission='M', query='q', source_version='v', evidence_path='e',
                salvar_raw=False, autorizacao=a, proposito='T9',
                source_id='IT-T9-008', motivo_do_gasto=ag.COLETA_NORMAL,
                teto_usd=0.05)
        self.assertEqual('AUTORIZACAO_NAO_COBRE_ESTA_FONTE', c.exception.causa)

    def test_autorizacao_nao_atravessa_para_outro_proposito(self):
        livro = [decisao('IT-T9-002', 'T9', rel.SIM)]
        a = ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                         source_id='IT-T9-002', max_usd=0.05, livro=livro)
        with self.assertRaises(ag.GastoRecusado) as c:
            coletor.executar(
                'apify~ator', {}, token='T', run_id='R', platform='P', country='IT',
                mission='M', query='q', source_version='v', evidence_path='e',
                salvar_raw=False, autorizacao=a, proposito='T3',
                source_id='IT-T9-002', motivo_do_gasto=ag.COLETA_NORMAL,
                teto_usd=0.05)
        self.assertEqual('AUTORIZACAO_NAO_COBRE_ESTE_PROPOSITO', c.exception.causa)

    def test_teto_acima_do_autorizado_e_recusado(self):
        livro = [decisao('IT-T9-002', 'T9', rel.SIM)]
        a = ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                         source_id='IT-T9-002', max_usd=0.05, livro=livro)
        with self.assertRaises(ag.GastoRecusado) as c:
            coletor.executar(
                'apify~ator', {}, token='T', run_id='R', platform='P', country='IT',
                mission='M', query='q', source_version='v', evidence_path='e',
                salvar_raw=False, autorizacao=a, proposito='T9',
                source_id='IT-T9-002', motivo_do_gasto=ag.COLETA_NORMAL,
                teto_usd=5.00)
        self.assertEqual('SEM_TETO_NO_FORNECEDOR', c.exception.causa)

    def test_sem_teto_no_fornecedor_e_recusado(self):
        """A unica trava que sobrevive a um defeito nosso e a da plataforma."""
        livro = [decisao('IT-T9-002', 'T9', rel.SIM)]
        a = ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                         source_id='IT-T9-002', max_usd=0.05, livro=livro)
        with self.assertRaises(ag.GastoRecusado) as c:
            coletor.executar(
                'apify~ator', {}, token='T', run_id='R', platform='P', country='IT',
                mission='M', query='q', source_version='v', evidence_path='e',
                salvar_raw=False, autorizacao=a, proposito='T9',
                source_id='IT-T9-002', motivo_do_gasto=ag.COLETA_NORMAL,
                teto_usd=None)
        self.assertEqual('SEM_TETO_NO_FORNECEDOR', c.exception.causa)

    def test_url_nunca_vira_source_id_na_autorizacao(self):
        with self.assertRaises(rel.SourceIdInvalido):
            ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                         source_id='https://instagram.com/basf', max_usd=0.05,
                         livro=[])

    def test_motivo_fora_do_vocabulario_e_recusado(self):
        with self.assertRaises(ag.AutorizacaoInvalida) as c:
            ag.autorizar(motivo='PORQUE_A_APIFY_JA_ESTAVA_CONFIGURADA',
                         proposito='T9', source_id='IT-T9-002', livro=[])
        self.assertIn('MOTIVO_DESCONHECIDO', str(c.exception))


# ══════════════════════════════════════════════════════════════════════════
# OS DONOS NAO SE MISTURAM
# ══════════════════════════════════════════════════════════════════════════
class OsDonosNaoSeMisturam(unittest.TestCase):

    def test_o_coletor_nao_le_o_livro_de_relevancia(self):
        """A porta que gasta nao pode ter opiniao sobre a fonte."""
        fonte = open(os.path.join(RAIZ, 'coleta', 'coletor.py'), encoding='utf-8').read()
        self.assertNotIn('import relevancia_da_fonte', fonte)
        self.assertNotIn('LIVRO-DE-RELEVANCIA', fonte)
        self.assertNotIn('rel.portao', fonte)

    def test_o_apify_pool_nao_le_o_livro_nem_a_guarda(self):
        """O dono da credencial nao decide nada sobre fonte nem sobre gasto."""
        fonte = open(os.path.join(RAIZ, 'ferramentas', 'apify_pool.py'),
                     encoding='utf-8').read()
        for proibido in ('relevancia_da_fonte', 'LIVRO-DE-RELEVANCIA',
                         'autorizacao_de_gasto', 'SOURCE_RELEVANCE'):
            self.assertNotIn(proibido, fonte)

    def test_a_guarda_nao_recebe_token(self):
        """O dono da autorizacao nao toca na credencial."""
        import inspect
        for fn in (ag.autorizar, ag.conferir_e_consumir):
            p = set(inspect.signature(fn).parameters)
            self.assertFalse(p & {'token', 'chave', 'credencial', 'apify_token'},
                             '%s ganhou acesso a credencial: %s' % (fn.__name__, p))

    def test_o_dono_da_relevancia_nao_conhece_dinheiro(self):
        fonte = open(os.path.join(RAIZ, 'leis', 'relevancia_da_fonte.py'),
                     encoding='utf-8').read()
        for proibido in ('apify_pool', 'APIFY_TOKEN', 'import coletor'):
            self.assertNotIn(proibido, fonte)

    def test_a_guarda_pergunta_ao_dono_da_relevancia_e_nao_o_reimplementa(self):
        fonte = open(os.path.join(RAIZ, 'leis', 'autorizacao_de_gasto.py'),
                     encoding='utf-8').read()
        self.assertIn('import relevancia_da_fonte', fonte)
        self.assertIn('rel.portao(', fonte)
        # nao reimplementa a tabela do portao
        self.assertNotIn('REGRA_DO_PORTAO = ', fonte)


# ══════════════════════════════════════════════════════════════════════════
# OS TRES ADAPTADORES LEVAM A AUTORIZACAO ATE A PORTA
# ══════════════════════════════════════════════════════════════════════════
class OsAdaptadoresTransportam(ComFornecedorFalso):
    """⚠️ ESTA CLASSE NASCEU DE DOIS MUTANTES VIVOS.

    A suite provava a guarda e provava a porta, e nunca provava o CAMINHO entre
    as duas. Por isso `autorizacao=None` no sensor e `proposito='QUALQUER'` no
    Instagram passavam despercebidos: o codigo mutado nunca era corrido.

        PROVAR A PORTA NAO E PROVAR QUEM CHEGA A ELA.

    Cada teste aqui corre o adaptador REAL, com o fornecedor fingido so na
    ponta, e conta os POST que sairiam.
    """

    def test_o_sensor_leva_a_autorizacao_e_compra(self):
        import sensor_coleta
        livro = [decisao('IT-T9-002', 'T9', rel.SIM)]
        a = ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                         source_id='IT-T9-002', max_usd=0.05, livro=livro)
        alvo = sensor_coleta.coletor._curl
        chaves = sensor_coleta.ap.pool
        sensor_coleta.coletor._curl = self.espiao
        # ⚠️ SEM CHAVE NO COFRE, `_rodar` volta antes de chegar a porta — e o
        # teste mediria «nao gastou» sem a guarda ter sido exercida. Uma chave
        # de mentira, que nunca sai da maquina, e o que faz o caminho correr.
        sensor_coleta.ap.pool = lambda *x, **k: ['CHAVE-DE-PROVA']
        try:
            sensor_coleta._rodar(
                'apify~ator', {}, run_id='R', platform='YOUTUBE', country='IT',
                query='q', evidence_path='e', lote='C', autorizacao=a)
        finally:
            sensor_coleta.coletor._curl = alvo
            sensor_coleta.ap.pool = chaves
        self.assertEqual(1, self.espiao.posts,
                         'o sensor nao chegou a comprar com autorizacao valida')

    def test_o_sensor_sem_autorizacao_nao_compra(self):
        import sensor_coleta
        alvo = sensor_coleta.coletor._curl
        chaves = sensor_coleta.ap.pool
        sensor_coleta.coletor._curl = self.espiao
        sensor_coleta.ap.pool = lambda *x, **k: ['CHAVE-DE-PROVA']
        try:
            with self.assertRaises(ag.GastoRecusado):
                sensor_coleta._rodar(
                    'apify~ator', {}, run_id='R', platform='YOUTUBE', country='IT',
                    query='q', evidence_path='e', lote='C')
        finally:
            sensor_coleta.coletor._curl = alvo
            sensor_coleta.ap.pool = chaves
        self.assertEqual(0, self.espiao.posts)

    def test_o_instagram_declara_o_proposito_que_a_autorizacao_cobre(self):
        """Um adaptador que declarasse outro proposito compraria fora do que foi
        autorizado — e a guarda so consegue conferir o que lhe dizem."""
        import instagram_coleta
        livro = [decisao('IT-T9-002', 'T9', rel.SIM)]
        a = ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                         source_id='IT-T9-002', max_usd=0.20, livro=livro)
        alvo = instagram_coleta.coletor._curl
        instagram_coleta.coletor._curl = self.espiao
        chaves = instagram_coleta.ap.pool
        instagram_coleta.ap.pool = lambda *x, **k: ['CHAVE-DE-PROVA']
        try:
            instagram_coleta._rodar('posts', {}, run_id='R', conta=None,
                                    evidencia='e', autorizacao=a)
        finally:
            instagram_coleta.coletor._curl = alvo
            instagram_coleta.ap.pool = chaves
        self.assertEqual(1, self.espiao.posts,
                         'o Instagram nao levou o proposito certo ate a porta')

    def test_o_instagram_sem_autorizacao_nao_compra(self):
        import instagram_coleta
        alvo = instagram_coleta.coletor._curl
        instagram_coleta.coletor._curl = self.espiao
        chaves = instagram_coleta.ap.pool
        instagram_coleta.ap.pool = lambda *x, **k: ['CHAVE-DE-PROVA']
        try:
            with self.assertRaises(ag.GastoRecusado):
                instagram_coleta._rodar('posts', {}, run_id='R', conta=None,
                                        evidencia='e')
        finally:
            instagram_coleta.coletor._curl = alvo
            instagram_coleta.ap.pool = chaves
        self.assertEqual(0, self.espiao.posts)

    def test_a_comunicacao_publica_sem_autorizacao_nao_compra(self):
        import comunicacao_coleta
        alvo = comunicacao_coleta.coletor._curl
        comunicacao_coleta.coletor._curl = self.espiao
        chaves = comunicacao_coleta.ap.pool
        gravar = comunicacao_coleta._gravar
        comunicacao_coleta.ap.pool = lambda *x, **k: ['CHAVE-DE-PROVA']
        # `fase_posts` grava o seu artefato no fim. A prova mede POST, nao
        # escrita — e deixar o ficheiro na arvore faria a corrida seguinte
        # medir esta.
        comunicacao_coleta._gravar = lambda *x, **k: '(prova: nao gravado)'
        try:
            comunicacao_coleta.fase_posts('INSTAGRAM')
        except Exception:                                        # noqa: BLE001
            pass
        finally:
            comunicacao_coleta.coletor._curl = alvo
            comunicacao_coleta.ap.pool = chaves
            comunicacao_coleta._gravar = gravar
        self.assertEqual(0, self.espiao.posts,
                         'a comunicacao publica comprou sem autorizacao')


# ══════════════════════════════════════════════════════════════════════════
# A TOPOLOGIA CONTINUA A SER UMA PORTA SO
# ══════════════════════════════════════════════════════════════════════════
class UmaPortaSo(unittest.TestCase):

    def test_so_ha_uma_primitiva_que_cria_execucao_paga(self):
        import censo_das_portas_de_gasto as censo
        c = censo.medir()
        self.assertEqual(['coleta/coletor.py'], c['PAID_CREATION_PRIMITIVES'],
                         'nasceu uma segunda porta de gasto: %s'
                         % c['PAID_CREATION_PRIMITIVES'])

    def test_toda_a_gente_que_compra_atravessa_a_guarda(self):
        import censo_das_portas_de_gasto as censo
        c = censo.medir()
        sem_guarda = []
        for rel_path in c['PODEM_CRIAR_EXECUCAO_PAGA']:
            t = open(os.path.join(RAIZ, rel_path), encoding='utf-8').read()
            if 'autorizacao' not in t:
                sem_guarda.append(rel_path)
        self.assertEqual([], sem_guarda,
                         'estes compram sem falar de autorizacao: %s' % sem_guarda)

    def test_o_censo_separa_quem_toca_de_quem_compra(self):
        import censo_das_portas_de_gasto as censo
        t = censo.medir()['TOTAIS']
        self.assertGreater(t['MENCIONAM_APIFY'], t['PODEM_CRIAR_EXECUCAO_PAGA'],
                           'tocar a plataforma voltou a ser o mesmo que comprar nela')


if __name__ == '__main__':
    unittest.main(verbosity=2)
