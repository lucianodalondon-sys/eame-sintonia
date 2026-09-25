# -*- coding: utf-8 -*-
"""LUGAR-FATO · o extrator de fact_location / fact_time do texto (leis/fato_do_texto.py).

    py -m unittest tests.test_fato_do_texto

Sem rede, sem Sala: textos escritos aqui, com a forma dos 78 da Sala (pagina inteira: menu + corpo + rodape).
"""
import inspect
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "leis"))
import fato_do_texto as FT   # noqa: E402

MENU = "Home\nNotizie\nEmilia-Romagna\nTemi ambientali\n"
RODAPE = ("Dati rilevati dalla stazione di Bologna, Via Po 5, 40139 Bologna tel 051 6223811\n"
          "Iscrizione sul registro stampa del tribunale di Bologna n. 8586")
CORPO_FOCO = "La fusariosi e stata constatata a Grosseto dai tecnici del servizio fitosanitario durante i controlli.\n"


class TestLugar(unittest.TestCase):
    def test_so_o_lugar_do_corpo_ligado_ao_acontecimento(self):
        r = FT.campos_do_fato(MENU + CORPO_FOCO + RODAPE)
        self.assertEqual("Grosseto", r["fact_location"])
        self.assertIn("constatata", r["fact_location_basis"])
        self.assertIn("Grosseto", r["fact_location_basis"], "a base traz o trecho")

    def test_lugar_do_menu_e_do_rodape_nao_conta(self):
        r = FT.campos_do_fato(MENU + "Il servizio pubblica ogni settimana le analisi delle acque di balneazione.\n" + RODAPE)
        self.assertEqual(FT.NAO_SEI, r["fact_location"], r["fact_location_basis"])
        self.assertNotIn("Bologna", r["fact_location"])

    def test_o_lugar_da_fonte_nao_tem_por_onde_entrar(self):
        self.assertNotIn("source_location", inspect.signature(FT.campos_do_fato).parameters)

    def test_mencao_sem_acontecimento_fica_nao_sei_e_diz_quais(self):
        r = FT.campos_do_fato("Il convegno nazionale sulla viticoltura si terra a Firenze con esperti da tutta Italia.\n")
        self.assertEqual(FT.NAO_SEI, r["fact_location"])
        self.assertIn("NAO SEI", r["fact_location_basis"])

    def test_varios_lugares_ficam_todos_cada_um_com_o_trecho(self):
        r = FT.campos_do_fato("Sono stati confermati campioni positivi provenienti da Grosseto, Siena e Arezzo nelle ultime analisi.\n")
        self.assertEqual({"Grosseto", "Siena", "Arezzo"}, set(r["fact_location"].split(FT.SEP)))
        self.assertEqual(3, len(r["EVIDENCIA"]["LUGARES"]))

    def test_texto_so_de_menu(self):
        r = FT.campos_do_fato(MENU)
        self.assertEqual(FT.NAO_SEI, r["fact_location"])
        self.assertIn("não tem corpo", r["fact_location_basis"])


class TestTempo(unittest.TestCase):
    def test_data_escrita_e_ligada_ao_acontecimento(self):
        r = FT.campos_do_fato("Il monitoraggio ha rilevato le prime catture il 12 settembre nei vigneti della zona collinare.\n")
        self.assertEqual("12 settembre", r["fact_time"])
        self.assertIn("DATE_EXACT", r["fact_time_basis"])
        self.assertIn("prime catture", r["fact_time_basis"], "a base traz o trecho")

    def test_a_publicacao_nunca_vira_tempo_do_facto(self):
        t = "Articolo pubblicato sul portale regionale con tutti gli aggiornamenti della settimana in corso.\n"
        r = FT.campos_do_fato(t, "2026-09-23", "meta article:published_time")
        self.assertEqual(FT.NAO_SEI, r["fact_time"])
        self.assertIn("nunca preenche", r["fact_time_basis"])
        r2 = FT.campos_do_fato("Il monitoraggio del 23 settembre 2026 conferma il quadro gia descritto nei giorni precedenti.\n",
                               "2026-09-23", "meta article:published_time")
        self.assertEqual(FT.NAO_SEI, r2["fact_time"], "a data igual a publicacao e carimbo, nao facto")

    def test_relativa_sem_publicacao_provada_e_descartada(self):
        t = "Fusariosi constatata a Grosseto la settimana scorsa, con sintomi osservati in campo dai tecnici.\n"
        for pub, base in ((None, None), ("2026-09-23", "NAO SEI"), ("23/09/2026", "meta")):
            r = FT.campos_do_fato(t, pub, base)
            self.assertEqual(FT.NAO_SEI, r["fact_time"], (pub, base))
            self.assertIn("la settimana scorsa", r["fact_time_basis"])

    def test_relativa_com_publicacao_provada_resolve_e_diz_a_base(self):
        t = "Fusariosi constatata a Grosseto la settimana scorsa, con sintomi osservati in campo dai tecnici.\n"
        r = FT.campos_do_fato(t, "2026-09-23", "meta article:published_time")
        self.assertEqual("2026-W38", r["fact_time"])
        self.assertTrue(r["fact_time_basis"].startswith(FT.RELATIVA))
        r = FT.campos_do_fato("Ieri i tecnici hanno rilevato sintomi di peronospora nei vigneti della provincia.\n",
                              "2026-09-23", "meta article:published_time")
        self.assertEqual("2026-09-22", r["fact_time"])

    def test_serie_de_anos_carimbo_de_lista_e_prazo_nao_sao_tempo_do_facto(self):
        for t in ("Il raccolto registra volumi stabili con il confronto tra le settimane 35-39 del 2024, 2025 e 2026 nei mercati.\n",
                  "1 settembre 2026 Risultati del monitoraggio delle radiazioni ultraviolette in tutta Europa pubblicati oggi.\n",
                  "Il raccolto bio, iniziato da poche settimane e in proseguimento fino a novembre, registra volumi stabili.\n"):
            r = FT.campos_do_fato(t)
            self.assertEqual(FT.NAO_SEI, r["fact_time"], (t, r["fact_time"]))
            self.assertIn("descartadas", r["fact_time_basis"])

    def test_os_quatro_campos_com_os_nomes_combinados(self):
        r = FT.campos_do_fato(CORPO_FOCO)
        self.assertTrue({"fact_location", "fact_location_basis", "fact_time", "fact_time_basis"} <= set(r))
        self.assertTrue(all(isinstance(r[k], str) and r[k] for k in ("fact_location", "fact_location_basis", "fact_time", "fact_time_basis")))


if __name__ == "__main__":
    unittest.main()
