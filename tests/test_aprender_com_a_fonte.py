#!/usr/bin/env python3
"""APRENDER COM A FONTE — sem numero magico.

    UMA FONTE NAO TEM UMA NOTA.
    TEM VARIAS MEDIDAS, E ELAS DISCORDAM.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import aprender_com_a_fonte as a  # noqa: E402


class SemNumeroMagico(unittest.TestCase):

    def test_source_score_esta_na_lista_do_que_nao_se_cria(self):
        self.assertIn('SOURCE_SCORE', a.NAO_CRIAR)
        self.assertIn('RANKING_UNICO', a.NAO_CRIAR)

    def test_a_razao_esta_escrita(self):
        """Um numero so esconde qual das medidas o produziu."""
        self.assertIn('esconde', a.PORQUE_NAO_CRIAR)

    def test_o_modulo_nao_define_score_nenhum(self):
        """⚠️ Contra o codigo, nao contra a intencao."""
        import inspect
        fonte = inspect.getsource(a)
        corpo = '\n'.join(l for l in fonte.splitlines()
                          if not l.strip().startswith('#'))
        for proibido in ('SOURCE_SCORE =', 'def score', 'def pontuar'):
            self.assertNotIn(proibido, corpo)


class SaudeDaFonteNaoESaudeDaRota(unittest.TestCase):
    """Uma fonte perfeita atras de uma rota partida da o mesmo resultado
    pratico que uma fonte morta — e a causa e completamente diferente."""

    def test_sao_dois_conjuntos_separados(self):
        self.assertEqual(set(a.SAUDE_DA_FONTE) & set(a.SAUDE_DA_ROTA), set())

    def test_a_lei_esta_escrita(self):
        self.assertIn('SAUDE DA FONTE != SAUDE DA ROTA', ' | '.join(a.LEIS))


class OCicloDeVidaNaoSeAchata(unittest.TestCase):

    def test_degraded_quarantined_e_retired_sao_tres(self):
        """A primeira e uma medida, a segunda uma decisao, a terceira um fim."""
        for e in ('DEGRADED', 'QUARANTINED', 'RETIRED'):
            self.assertIn(e, a.CICLO_DE_VIDA)

    def test_ha_degraus_antes_de_activa(self):
        for e in ('DISCOVERED', 'SCREENED', 'TRIAL', 'PROBATION'):
            self.assertIn(e, a.CICLO_DE_VIDA)

    def test_retirar_nao_apaga_historia(self):
        self.assertIn('continua dona do que ja trouxe', a.RETIRAR_NAO_APAGA)


class OQueContaComoBomDependeDoPapel(unittest.TestCase):
    """⚠️ A MESMA MEDIDA, LIDA AO CONTRARIO."""

    def test_repeticao_alta_e_esperada_em_corroboracao(self):
        estado, _porque = a.leitura_da_repeticao('CORROBORATION', 0.9)
        self.assertEqual(estado, 'ESPERADO')

    def test_repeticao_alta_e_atencao_em_descoberta(self):
        estado, _porque = a.leitura_da_repeticao('DISCOVERY', 0.9)
        self.assertEqual(estado, 'ATENCAO')

    def test_sem_papel_nao_se_le_a_taxa(self):
        """Ler uma taxa sem saber para que serve a fonte e inventar um
        julgamento."""
        estado, porque = a.leitura_da_repeticao('NAO_EXISTE', 0.9)
        self.assertEqual(estado, 'UNKNOWN')
        self.assertIn('nao se le', porque)

    def test_os_seis_papeis_existem(self):
        for p in ('EVIDENCE', 'DISCOVERY', 'EARLY_WARNING', 'CORROBORATION',
                  'CONTEXT', 'REFERENCE'):
            self.assertIn(p, a.PAPEIS)


class AsMedidasDizemDeOndeVieram(unittest.TestCase):

    def test_toda_medida_guarda_a_amostra(self):
        """2 em 2 e 200 em 200 dao os dois «100%»."""
        self.assertIn('AMOSTRA', a.CAMPOS_DA_MEDIDA)
        self.assertIn('denominador', a.PORQUE_AMOSTRA)

    def test_toda_medida_diz_como_foi_medida_e_em_que_janela(self):
        self.assertIn('COMO_FOI_MEDIDO', a.CAMPOS_DA_MEDIDA)
        self.assertIn('JANELA', a.CAMPOS_DA_MEDIDA)

    def test_cadencia_declarada_e_observada_sao_duas(self):
        """Um portal que promete semanal e publica mensal nao esta avariado —
        esta a mentir na promessa."""
        self.assertIn('CADENCIA_DECLARADA', a.SAUDE_DA_FONTE)
        self.assertIn('CADENCIA_OBSERVADA', a.SAUDE_DA_FONTE)

    def test_unique_yield_e_ready_yield_sao_dois(self):
        """COLETADO != ADMITIDO. Trazer muito e admitir pouco e trabalho a
        mais, nao valor."""
        self.assertIn('UNIQUE_YIELD', a.RENDIMENTOS)
        self.assertIn('READY_YIELD', a.RENDIMENTOS)
        self.assertIn('COLETADO != ADMITIDO', ' | '.join(a.LEIS))


if __name__ == '__main__':
    unittest.main(verbosity=2)
