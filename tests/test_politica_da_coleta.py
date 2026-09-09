#!/usr/bin/env python3
"""RT11..RT18 e RT25..RT28 — os contratos de gestao e evolucao.

    O COLLECTION MANAGER NAO E UM SEGUNDO ORQUESTRADOR.
    DISCOVERED NAO E ACTIVE.
    AUTOMATIC LEARNING NAO E AUTOMATIC PROMOTION.
"""
import ast
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import politica_da_coleta as g    # noqa: E402
import fundacao_da_coleta as f  # noqa: E402


class RT_Fronteira(unittest.TestCase):

    # ── RT26 ──────────────────────────────────────────────────────────────
    def test_RT26_o_manager_nao_pode_chamar_executor(self):
        """Medido por AST: nenhum import de executor, coletor ou rota."""
        caminho = os.path.join(RAIZ, 'leis', 'politica_da_coleta.py')
        with open(caminho, encoding='utf-8') as fh:
            arvore = ast.parse(fh.read())
        importados = set()
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                importados |= {a.name.split('.')[0] for a in no.names}
            elif isinstance(no, ast.ImportFrom) and no.module:
                importados.add(no.module.split('.')[0])
        proibidos = {'coletor', 'social_scrap', 'youtube_oficial', 'social_rotas',
                     'apify_pool', 'cdp', 'navegador', 'instagram_coleta',
                     'orquestrador', 'requests', 'urllib'}
        self.assertEqual(importados & proibidos, set(),
                         'o Manager importou executor: virou o segundo orquestrador')

    def test_a_decisao_nao_escolhe_executor_nem_rota_concreta(self):
        d = g.decidir(source_id='S', satisfaction=g.NAO_TENHO)
        self.assertIsNone(d['EXECUTOR'])
        self.assertIsNone(d['ROTA_CONCRETA'])

    # ── RT17 ──────────────────────────────────────────────────────────────
    def test_RT17_a_politica_recomenda_e_nao_dispara(self):
        d = g.decidir(source_id='S', satisfaction=g.NAO_TENHO)
        self.assertEqual(d['MODE'], g.SHADOW)
        self.assertEqual(d['ACAO'], g.FETCH)   # recomenda buscar…
        # …e nao ha nada neste modulo que execute.
        with open(os.path.join(RAIZ, 'leis', 'politica_da_coleta.py'),
                  encoding='utf-8') as fh:
            fonte = fh.read()
        for perigo in ('subprocess', 'os.system', 'popen'):
            self.assertNotIn(perigo, fonte)


class RT_Politica(unittest.TestCase):

    # ── RT19 (lado do codigo) ─────────────────────────────────────────────
    def test_toda_decisao_carrega_versao_e_porque(self):
        for sat in g.SATISFACAO:
            d = g.decidir(source_id='S', satisfaction=sat)
            self.assertTrue(d['POLICY_VERSION'])
            self.assertTrue(d['WHY_NOW'])
            self.assertIn(d['PRIORITY_TIER'], g.TIERS)

    def test_a_politica_e_deterministica(self):
        a = g.decidir(source_id='S', satisfaction=g.JA_TENHO_VELHO, suporta_check=True)
        b = g.decidir(source_id='S', satisfaction=g.JA_TENHO_VELHO, suporta_check=True)
        self.assertEqual(a, b)

    def test_ja_temos_e_fresco_nao_gasta(self):
        d = g.decidir(source_id='S', satisfaction=g.JA_TENHO_FRESCO)
        self.assertEqual(d['ACAO'], g.SKIP)

    # ── RT9 / RT10 ────────────────────────────────────────────────────────
    def test_RT9_quando_a_rota_sabe_perguntar_ela_pergunta_antes_de_baixar(self):
        d = g.decidir(source_id='S', satisfaction=g.JA_TENHO_VELHO, suporta_check=True)
        self.assertEqual(d['ACAO'], g.CHECK, 'baixou sem perguntar se mudou')

    def test_RT10_sem_suporte_a_CHECK_nao_se_finge_que_nada_mudou(self):
        d = g.decidir(source_id='S', satisfaction=g.JA_TENHO_VELHO, suporta_check=False)
        self.assertEqual(d['ACAO'], g.FETCH)
        self.assertNotEqual(d['ACAO'], g.SKIP, 'fingiu unchanged sem poder saber')

    def test_nao_sei_pergunta_em_vez_de_gastar(self):
        d = g.decidir(source_id='S', satisfaction=g.NAO_SEI)
        self.assertEqual(d['ACAO'], g.CHECK)

    def test_o_portao_da_satisfacao_responde_antes_da_coleta(self):
        self.assertEqual(g.satisfacao(True, 1, 24), g.JA_TENHO_FRESCO)
        self.assertEqual(g.satisfacao(True, 48, 24), g.JA_TENHO_VELHO)
        self.assertEqual(g.satisfacao(True, 1, 24, completo=False), g.TENHO_PARTE)
        self.assertEqual(g.satisfacao(False, None, None), g.NAO_TENHO)
        self.assertEqual(g.satisfacao(None, None, None), g.NAO_SEI)


class RT_CicloDaFonte(unittest.TestCase):

    # ── RT14 / AS ─────────────────────────────────────────────────────────
    def test_RT14_candidata_descoberta_nao_vira_ACTIVE(self):
        self.assertFalse(g.transicao_permitida('DISCOVERED', 'ACTIVE'))
        self.assertTrue(g.transicao_permitida('DISCOVERED', 'SCREENED'))

    def test_o_caminho_ate_ACTIVE_passa_por_teste(self):
        caminho = ['DISCOVERED', 'SCREENED', 'TRIAL', 'PROBATION', 'ACTIVE']
        for de, para in zip(caminho, caminho[1:]):
            self.assertTrue(g.transicao_permitida(de, para), '%s -> %s' % (de, para))

    # ── RT15 ──────────────────────────────────────────────────────────────
    def test_RT15_teste_ruim_nao_apaga_a_fonte(self):
        self.assertFalse(g.transicao_permitida('TRIAL', 'RETIRED'))
        self.assertTrue(g.transicao_permitida('TRIAL', 'QUARANTINED'))

    # ── RT16 ──────────────────────────────────────────────────────────────
    def test_RT16_papeis_sao_separados(self):
        self.assertIn('EVIDENCE', g.PAPEIS)
        self.assertIn('DISCOVERY', g.PAPEIS)
        self.assertGreater(len(g.PAPEIS), 2,
                           'um papel so apagaria a fonte que e ma para provar '
                           'e boa para descobrir')

    # ── RT25 ──────────────────────────────────────────────────────────────
    def test_RT25_candidata_sem_procedencia_nao_entra(self):
        for campo in ('DISCOVERED_FROM', 'DISCOVERY_METHOD', 'WHY_ADAMA_RELEVANT'):
            self.assertIn(campo, g.CANDIDATA_EXIGE)


class RT_Evolucao(unittest.TestCase):

    # ── RT18 / AX ─────────────────────────────────────────────────────────
    def test_RT18_nao_existe_promocao_automatica(self):
        pode, porque = g.pode_promover_sozinho()
        self.assertFalse(pode)
        self.assertIn('NAO E AUTOMATIC PROMOTION', porque)

    def test_o_rollback_tem_contrato(self):
        for campo in ('FROM_VERSION', 'TO_VERSION', 'WHY', 'BASELINE',
                      'ROLLBACK_TO', 'ROLLBACK_REASON'):
            self.assertIn(campo, g.PROMOCAO_EXIGE)

    # ── RT12 / RT13 / AF ──────────────────────────────────────────────────
    def test_AF_nao_existe_nota_magica_de_fonte(self):
        nomes = [n for n in dir(g) if n.isupper()]
        self.assertNotIn('SOURCE_SCORE', nomes)
        self.assertGreater(len(g.DIMENSOES), 5,
                           'as dimensoes colapsaram numa nota')

    def test_RT12_volume_nao_e_rendimento(self):
        """UNIQUE_YIELD e READY_YIELD existem separados de volume."""
        self.assertIn('UNIQUE_YIELD', g.DIMENSOES)
        self.assertIn('READY_YIELD', g.DIMENSOES)
        self.assertNotIn('VOLUME', g.DIMENSOES)

    def test_orcamento_de_exploracao_nao_foi_inventado(self):
        self.assertIsNone(g.ORCAMENTO_DE_EXPLORACAO,
                          '90/10 e 80/20 sao numeros que alguem inventou')

    def test_sem_historico_diz_sem_historico(self):
        self.assertEqual(g.SEM_HISTORICO, 'NOT_ENOUGH_HISTORY')


class RT_Congelamento(unittest.TestCase):

    # ── RT27 ──────────────────────────────────────────────────────────────
    def test_RT27_a_inteligencia_continua_congelada(self):
        pode, motivo = f.pode_implementar_inteligencia()
        self.assertFalse(pode)
        self.assertIn(f.BLOQUEIO, motivo)

    # ── RT28 ──────────────────────────────────────────────────────────────
    def test_RT28_o_portal_nao_e_requisito_da_fundacao(self):
        """A fronteira da coleta termina em READY."""
        import rastro_da_coleta as r
        for proibida in ('INTELLIGENCE', 'PACKAGE', 'PORTAL', 'DELIVERY', 'SCREEN'):
            self.assertNotIn(proibida, r.ETAPAS,
                             '%s virou etapa da fundacao da coleta' % proibida)
        self.assertEqual(r.ETAPAS[-1], 'READY')


if __name__ == '__main__':
    unittest.main(verbosity=2)
