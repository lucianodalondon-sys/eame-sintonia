#!/usr/bin/env python3
"""A EVOLUCAO — a espinha, e a porta estreita da promocao.

    APRENDER AUTOMATICAMENTE != PROMOVER AUTOMATICAMENTE.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import evolucao as e  # noqa: E402

BOA = {'METRICA_DECIDIDA_ANTES': 'ready_yield', 'BASELINE_REF': 'B-1'}
APROVA = {'QUEM_APROVOU': 'Luciano', 'COMO_SE_DESFAZ': 'voltar a v3'}


class APortaEEstreitaDePreposito(unittest.TestCase):
    """Cada False aqui e uma maneira conhecida de promover mal."""

    def test_o_caso_bom_passa(self):
        pode, _p = e.pode_promover(BOA, 'CHALLENGER_BETTER', APROVA)
        self.assertTrue(pode)

    def test_empate_nao_promove(self):
        pode, porque = e.pode_promover(BOA, 'NO_DIFFERENCE', APROVA)
        self.assertFalse(pode)
        self.assertIn('so se promove quem ganhou', porque)

    def test_inconclusivo_nao_promove(self):
        """⚠️ «Nao deu para saber» nao e «sao iguais»: a primeira pede mais
        dados, a segunda fecha a questao."""
        pode, _p = e.pode_promover(BOA, 'INCONCLUSIVE', APROVA)
        self.assertFalse(pode)

    def test_sem_baseline_nao_promove(self):
        """Trocar e medir depois nao diz nada: nao se sabe como estava antes."""
        pode, porque = e.pode_promover(
            {'METRICA_DECIDIDA_ANTES': 'x'}, 'CHALLENGER_BETTER', APROVA)
        self.assertFalse(pode)
        self.assertIn('baseline', porque)

    def test_metrica_escolhida_depois_nao_promove(self):
        """⚠️ Escolher a metrica depois de ver os numeros e escolher quem
        ganha. E o erro mais facil de cometer de boa fe."""
        pode, porque = e.pode_promover(
            {'BASELINE_REF': 'B-1'}, 'CHALLENGER_BETTER', APROVA)
        self.assertFalse(pode)
        self.assertIn('depois de ver os numeros', porque)

    def test_sem_humano_com_nome_nao_promove(self):
        pode, porque = e.pode_promover(
            BOA, 'CHALLENGER_BETTER', {'COMO_SE_DESFAZ': 'x'})
        self.assertFalse(pode)
        self.assertIn('humano com nome', porque)

    def test_sem_caminho_de_volta_nao_promove(self):
        """Depois de correr mal, ninguem tem calma para desenhar a volta."""
        pode, porque = e.pode_promover(
            BOA, 'CHALLENGER_BETTER', {'QUEM_APROVOU': 'Luciano'})
        self.assertFalse(pode)
        self.assertIn('volta', porque)


class ASombraNaoToca(unittest.TestCase):

    def test_shadow_e_um_papel_proprio(self):
        self.assertIn('SHADOW', e.PAPEIS)
        self.assertIn('NAO afeta nada', e.PAPEIS['SHADOW'])

    def test_a_razao_esta_escrita(self):
        """Uma sombra que influencia deixou de ser sombra, e a comparacao fica
        contaminada."""
        self.assertIn('contaminada', e.SOMBRA_NAO_TOCA)


class NadaDissoCorreHoje(unittest.TestCase):

    def test_ml_bandit_e_auto_promocao_estao_proibidos(self):
        for p in ('ML_LIVE', 'BANDIT_LIVE', 'AUTO_PROMOTION'):
            self.assertIn(p, e.PROIBIDO_HOJE)

    def test_a_razao_liga_a_fundacao(self):
        self.assertIn('fundacao da coleta ainda nao fechou', e.PORQUE_PROIBIDO)

    def test_o_modulo_nao_importa_nada_que_corra(self):
        """⚠️ Contra o codigo, nao contra a intencao."""
        import inspect
        fonte = inspect.getsource(e)
        for proibido in ('sklearn', 'numpy', 'subprocess', 'requests'):
            self.assertNotIn('import %s' % proibido, fonte)


class ARegistoPermiteDesfazer(unittest.TestCase):

    def test_a_promocao_diz_como_se_desfaz(self):
        self.assertIn('COMO_SE_DESFAZ', e.CAMPOS_DA_PROMOCAO)
        self.assertIn('antes de promover', e.SEM_VOLTA_NAO_SE_PROMOVE)

    def test_ha_registo_de_rollback_ligado_a_promocao(self):
        self.assertIn('PROMOTION_ID', e.CAMPOS_DO_ROLLBACK)
        self.assertIn('VOLTOU_PARA', e.CAMPOS_DO_ROLLBACK)

    def test_a_experiencia_declara_a_metrica_e_a_amostra_minima(self):
        self.assertIn('METRICA_DECIDIDA_ANTES', e.CAMPOS_DA_EXPERIENCIA)
        self.assertIn('AMOSTRA_MINIMA', e.CAMPOS_DA_EXPERIENCIA)

    def test_as_leis_estao_escritas(self):
        junto = ' | '.join(e.LEIS)
        self.assertIn('APRENDER AUTOMATICAMENTE != PROMOVER AUTOMATICAMENTE',
                      junto)
        self.assertIn('SEM BASELINE', junto)
        self.assertIn('TODA PROMOCAO TEM UM HUMANO COM NOME', junto)


if __name__ == '__main__':
    unittest.main(verbosity=2)
