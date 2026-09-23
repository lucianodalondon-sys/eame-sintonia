#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A REGUA T8 (FARMERS & INFLUENCERS) — YT2, 2026-09-23.

Escrita DEPOIS do gabarito (scripts/regua_t8/GABARITO-T8-V1.json, 20 SIM / 28 NAO)
e medida nele por `scripts/regua_t8/medir_regua_t8.py`. Aqui provam-se os quatro
ramos, as tres decisoes de forma (conceito com formas, palavra inteira, transversal)
e a lingua (L1). Sem rede, sem Sala. Os trechos sao dos videos do gabarito
(`TRECHO_QUE_DECIDIU`), repetidos para passar do limiar de legibilidade.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for gaveta in ("admissao", ""):
    sys.path.insert(0, os.path.join(RAIZ, gaveta) if gaveta else RAIZ)
import admissao as A  # noqa: E402

ENCH_IT = " Il servizio di oggi racconta quello che succede in questo periodo dell'anno e ringraziamo chi ci ha ospitato. "
ENCH_EN = " This short piece was recorded this week and we thank everyone who took part in it with us today. "


def v(texto, u="T8"):
    return A._do_universo({"texto": texto}, u, A.PERGUNTAS_DO_UNIVERSO.get(u, []))


# trechos do gabarito (393IJzPlR3s, M3CsNbebgKY) e de negativos (Ya6W2z8LgeE, 1eH49G366Ak)
PODA = ("Siamo nell'azienda dell'Arsac e oggi vi faremo vedere la tecnica di potatura del cordone "
        "speronato nel vigneto, dai primi anni fino alla fase di produzione." + ENCH_IT * 3)
UM_SINAL = ("Il futuro del prodotto e legato all'impegno degli agricoltori calabresi e alla sua "
            "identita locale, un frutto croccante e dolce." + ENCH_IT * 3)
UNIVERSIDADE = ("Al dipartimento dell'universita si studia con la ricerca e con le pubblicazioni: "
                "l'istituto apre le porte agli studenti per il loro studio." + ENCH_IT * 3)
FARM_EN = ("Farmers in the valley started the harvest early this year, and growers say the orchard "
           "yields are good after the spring rain." + ENCH_EN * 3)


class OsQuatroRamos(unittest.TestCase):

    def test_1_valido_dois_conceitos_e_SIM(self):
        r, _, ev = v(PODA)
        self.assertEqual(r, A.SIM)
        self.assertGreaterEqual(ev["sinais"], A.SINAIS_MINIMOS)

    def test_2_insuficiente_um_conceito_e_NAO_SEI(self):
        r, _, ev = v(UM_SINAL)
        self.assertEqual(r, A.NAO_SEI)
        self.assertEqual(ev["sinais"], 1)

    def test_3_incompativel_prova_de_outro_universo_e_NAO(self):
        r, _, ev = v(UNIVERSIDADE)
        self.assertEqual(r, A.NAO)
        self.assertIn("T5", ev["achado_noutro"])

    def test_4_invalido_sem_texto_e_barrado_antes_da_pergunta(self):
        d = A.decidir({"id": "x", "texto": "", "source_id": "IT-T8-001",
                       "url": "https://www.youtube.com/watch?v=x"}, "T8", corrida="t")
        self.assertNotEqual(d.resultado, A.SIM)
        self.assertEqual(d.regra, "legivel", "o item sem texto chegou a pergunta do universo")


class AFormaDaRegua(unittest.TestCase):

    def test_5_um_conceito_conta_uma_vez_seja_qual_for_a_forma(self):
        """singular + plural sao UM indicio, e um indicio nao promove."""
        r, _, ev = v("L'agricoltore parla e gli agricoltori ascoltano, poi l'agricoltore torna a casa."
                     + ENCH_IT * 3)
        self.assertEqual(ev["sinais"], 1)
        self.assertEqual(r, A.NAO_SEI)

    def test_6_palavra_inteira_forma_dentro_de_outra_palavra_nao_casa(self):
        """`semina` nao casa em «seminario», `poda` nao casa em «podcast»."""
        r, _, ev = v("Il seminario del podcast e stato registrato nella sala grande della citta."
                     + ENCH_IT * 3)
        self.assertNotEqual(r, A.SIM)
        self.assertFalse(ev.get("palavras"), ev)

    def test_7_o_mesmo_texto_com_a_palavra_inteira_casa(self):
        r, _, ev = v("La semina e la potatura si fanno in questo periodo." + ENCH_IT * 3)
        self.assertEqual(r, A.SIM)

    def test_8_as_formas_estao_separadas_por_barra_e_nenhum_conceito_repete_outro(self):
        formas = [f for t in A.PERGUNTAS_DO_UNIVERSO["T8"] for f in t.split("|")]
        self.assertEqual(len(formas), len(set(formas)), "a mesma forma em dois conceitos")

    def test_9_nenhuma_forma_de_T8_e_termo_de_outro_universo(self):
        formas = {A._dobrar(f) for t in A.PERGUNTAS_DO_UNIVERSO["T8"] for f in t.split("|")}
        for u, termos in A.PERGUNTAS_DO_UNIVERSO.items():
            if u == "T8":
                continue
            for t in termos:
                self.assertNotIn(A._dobrar(t), formas, "%s repete %s" % (t, u))

    def test_10_as_armadilhas_medidas_ficaram_de_fora(self):
        formas = {f for t in A.PERGUNTAS_DO_UNIVERSO["T8"] for f in t.split("|")}
        for mau in ("raccolta", "resa", "campagna", "varieta"):
            self.assertNotIn(mau, formas)


class T8ETransversal(unittest.TestCase):
    """«quem fala e o campo?» nao exclui «fala de praga?»."""

    def test_11_palavras_de_T8_nao_sao_prova_contra_outro_universo(self):
        r, _, ev = v(PODA, "T3")
        self.assertNotEqual(r, A.NAO, "T8 serviu de prova para dizer NAO a T3")
        self.assertNotIn("T8", ev.get("achado_noutro") or {})

    def test_11b_em_ingles_tambem_nao_e_prova_contra_outro_universo(self):
        """⚠️ Nasceu de um mutante (MA1) que so a prova da LISTA apanhava: as
        entradas italianas de T8 levam «|» e nunca casam no teste antigo de
        «outro universo»; as inglesas de forma unica («pruning», «irrigation»)
        casam — e e aqui que a transversalidade se ve no comportamento."""
        t = ("We talk about pruning and irrigation in the valley this spring, and "
             "how the work is organised week by week." + ENCH_EN * 3)
        r, _, ev = v(t, "T3")
        self.assertNotEqual(r, A.NAO, "palavras de T8 serviram de prova para NAO a T3")
        self.assertNotIn("T8", ev.get("achado_noutro") or {})

    def test_12_a_lista_transversal_e_so_T8(self):
        self.assertEqual(A.TRANSVERSAIS, frozenset({"T8"}))
        self.assertEqual(A.PALAVRA_INTEIRA, frozenset({"T8"}))

    def test_13_as_reguas_antigas_continuam_a_casar_por_pedaco(self):
        """palavra inteira e so T8: T3 continua a achar `fitopatolog` em «fitopatologia»."""
        r, _, ev = v("La fitopatologia studia il patogeno e la malattia delle piante." + ENCH_IT * 3, "T3")
        self.assertIn("fitopatolog", ev.get("palavras") or [])


class ALingua(unittest.TestCase):

    def test_14_ingles_usa_a_lista_inglesa_de_T8(self):
        r, _, ev = v(FARM_EN)
        self.assertEqual(r, A.SIM)
        self.assertTrue(set(ev["palavras"]) <= set(A.PERGUNTAS_EN["T8"]))

    def test_15_alemao_e_NAO_SEI_dito(self):
        de = ("Hallo und willkommen zu unserer Sendung. Die Bauern haben die Ernte in diesem Jahr "
              "fruh begonnen und sind mit dem Ertrag sehr zufrieden, sagen sie uns heute. ") * 4
        r, motivo, _ = v(de)
        self.assertEqual(r, A.NAO_SEI)
        self.assertIn("IDIOMA_NAO_SUPORTADO:de", motivo)

    def test_16_o_limiar_continua_dois(self):
        self.assertEqual(A.SINAIS_MINIMOS, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
