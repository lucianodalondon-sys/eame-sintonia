# -*- coding: utf-8 -*-
"""As cinco cicatrizes que o leitor italiano não pode reabrir.

Este ficheiro existe por regressões MEDIDAS, não por simetria. O PASSO 03 trouxe
`scripts/fato_local.py` do piloto italiano, e a versão de lá reabria quatro falsos
positivos fundadores e perdia um foco confirmado em silêncio. Os casos abaixo são
os que a revisão adversarial reproduziu, verbatim.

AS LEIS (decisão de coordenação do PASSO 03):

    EVENTO                != FATO
    LOCAL_DA_FONTE        != LOCAL_DO_FATO
    SEDE                  != LOCAL_DO_FATO
    RISK_WORD             != PHYTOSANITARY_RISK
    GENERIC_PRESENCE      != DISEASE_PRESENCE

E uma que não é sobre falso positivo, mas sobre silêncio:

    RECUSAR é um resultado. DESAPARECER não é.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import fato_local as fl        # noqa: E402
import lugar_do_fato as L      # noqa: E402


def le(texto):
    ok, nao = fl.localizacoes_do_fato(texto)
    return ([(a['FACT_LOCATION'], a['TYPE_OF_EVIDENCE']) for a in ok],
            {r['PLACE'] for r in nao})


class EventoNaoEFato(unittest.TestCase):
    """A cicatriz fundadora: um congresso não é um foco de doença."""

    def test_congresso_com_verbo_depois_do_toponimo(self):
        """A âncora positiva vinha DEPOIS e ganhava por distância."""
        ok, nao = le('Il convegno internazionale organizzato a Bologna ha rilevato sintomi')
        self.assertEqual([], ok, 'o congresso voltou a virar observação de campo')
        self.assertIn('Bologna', nao, 'recusar é um resultado — Bologna tem de aparecer')

    def test_duas_oracoes_cada_lugar_com_a_sua_ancora(self):
        """A trava não pode ser tão larga que mate o lugar legítimo da segunda oração."""
        ok, nao = le('Convegno a Bologna e fusariosi constatata a Grosseto.')
        self.assertEqual([('Grosseto', 'CONFIRMED_FOCUS')], ok)
        self.assertIn('Bologna', nao)


class SedeNaoELocalDoFato(unittest.TestCase):

    def test_sede_legal_com_observacao_na_oracao_seguinte(self):
        ok, nao = le("La sede legale dell'azienda si trova a Bologna, "
                     'dove sono stati osservati sintomi')
        self.assertEqual([], ok, 'a sede da empresa voltou a virar lugar do fato')
        self.assertIn('Bologna', nao)


class RiskWordNaoERiscoFitossanitario(unittest.TestCase):
    """`rischio` sozinho não prova risco agronómico."""

    REAL = ('Prezzi in picchiata per il grano duro di Capitanata. Quotazioni al '
            'ribasso che mettono a rischio le aziende agricole della Provincia di Foggia.')

    def test_noticia_de_preco_nao_vira_afirmacao_fitossanitaria(self):
        """Texto REAL, já versionado em data/samples/SENSOR-PILOT/VIDEOS-A.json."""
        ok, _ = le(self.REAL)
        self.assertEqual([], ok, 'uma notícia de preço voltou a produzir MODELLED_RISK')

    def test_o_artigo_nao_e_sujeito_de_risco(self):
        for t in ('mette a rischio le colture della provincia di Foggia',
                  'a rischio la produzione nella provincia di Foggia'):
            with self.subTest(t=t):
                ok, _ = le(t)
                self.assertNotIn('MODELLED_RISK', [e for _, e in ok],
                                 'âncora ancorada num artigo')

    def test_o_risco_modelado_de_verdade_continua_a_existir(self):
        """A classe não foi removida — foi qualificada."""
        ok, _ = le('Rischio attacchi septoriosi nella provincia di Perugia')
        self.assertEqual([('Perugia', 'MODELLED_RISK')], ok)


class PresencaGenericaNaoEPresencaDeDoenca(unittest.TestCase):

    def test_presenca_de_empresas_nao_e_sintoma_visto(self):
        ok, _ = le('La presenza di aziende agricole in Toscana e significativa')
        self.assertEqual([], ok, 'presença de EMPRESAS voltou a contar como observação')

    def test_presenca_de_tecnicos_nao_e_sintoma_visto(self):
        ok, _ = le('Il progetto prevede la presenza di tecnici in Lombardia')
        self.assertEqual([], ok)

    def test_presenca_media_de_patogeno_continua_a_contar(self):
        """O caso real que justificava a âncora não se perdeu."""
        ok, _ = le('Presenza media di Septoriosi nel frumento in Umbria')
        self.assertEqual([('Umbria', 'FIELD_OBSERVATION')], ok)


class FocoConfirmadoNaoDesaparece(unittest.TestCase):
    """Saltar a primeira oração como se fosse cabeçalho apagava o facto."""

    def test_primeira_oracao_que_relata_nao_e_cabecalho(self):
        ok, _ = le('Constatata fusariosi nella provincia di Grosseto. '
                   'Il tempo resta variabile')
        self.assertEqual([('Grosseto', 'CONFIRMED_FOCUS')], ok,
                         'o foco confirmado desapareceu — e sem sequer entrar nas recusas')

    def test_com_regiao_no_comeco_tambem(self):
        ok, _ = le('Regione Toscana: constatata fusariosi a Grosseto. '
                   'Il grano tenero resta esente')
        self.assertIn('Grosseto', [p for p, _ in ok])

    def test_cabecalho_inerte_continua_a_ser_cabecalho(self):
        """A trava não pode desligar o escopo de documento onde ele é legítimo."""
        ok, _ = le('Provincia di Grosseto - Bollettino Frumento del 2026-04-23. '
                   'Constatata fusariosi nelle aziende monitorate.')
        self.assertTrue(ok, 'o escopo de documento deixou de funcionar')


class OLeitorNaoInventaEspecieQueONucleoNaoConhece(unittest.TestCase):
    """MODELLED_RISK existe no leitor e não no núcleo — e não pode vazar."""

    def test_o_leitor_nao_promove_risco_modelado_a_ocorrencia_observada(self):
        conta = fl.ocorrencia_nao_e_incidencia(['MODELLED_RISK'])
        self.assertEqual(0, conta.get('OBSERVED_OCCURRENCES', 0),
                         'risco modelado passou a contar como ocorrência observada')

    def test_o_nucleo_nao_conhece_a_especie_e_isso_esta_declarado(self):
        self.assertNotIn('MODELLED_RISK', set(L.TIPOS_DE_EVIDENCIA))


if __name__ == '__main__':
    unittest.main()
