#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O JUIZ do leitor semantico (leis/leitor_semantico.julgar) — deterministico, sem modelo.
Cada teste e uma tentativa de passar uma data que a lei recusa (SOUL §14/§18; INT-LAW-100)."""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "leis"))
import leitor_semantico as L  # noqa: E402

TXT = ("Pubblicato il 25 settembre 2026\nLeggi anche: legge 12 marzo 1990 sui fitofarmaci\n"
       "Il Bollettino fitosanitario relativo al periodo 1-4 settembre 2026 evidenzia una presenza ancora contenuta "
       "della Bactrocera oleae nelle trappole.\nControlli di giovedì 30 aprile: nessuna cattura nei vigneti.\n"
       "Dal 07-09-2026 al 13-09-2026\n")
OK = {"VALOR": "2026-09-01/2026-09-04", "DATA_LITERAL": "1-4 settembre 2026",
      "TRECHO": "Il Bollettino fitosanitario relativo al periodo 1-4 settembre 2026 evidenzia una presenza ancora "
                "contenuta della Bactrocera oleae nelle trappole.", "PAPEL_DA_DATA": "PERIODO_OBSERVADO", "PORQUE": "x"}


class JuizDoLeitor(unittest.TestCase):
    def j(self, **mud):
        return L.julgar(TXT, dict(OK, **mud), "2026-09-20T10:00:00Z")

    def test_leitura_provada_e_aceite_com_posicao(self):
        r = self.j()
        self.assertEqual(r["JUIZ"], "ACEITE")
        self.assertEqual(TXT[r["POSICAO_DA_DATA"]["INICIO"]:r["POSICAO_DA_DATA"]["FIM"]], "1-4 settembre 2026")

    def test_J1_publicacao_nao_e_fact_time(self):
        r = self.j(VALOR="2026-09-25", DATA_LITERAL="25 settembre 2026", TRECHO="Pubblicato il 25 settembre 2026",
                   PAPEL_DA_DATA="PUBLICACAO")
        self.assertEqual((r["VALOR"], r["JUIZ"][:11]), ("NAO SEI", "RECUSADO: J"))

    def test_J1_citacao_de_lei_nao_e_fact_time(self):
        r = self.j(VALOR="1990-03-12", DATA_LITERAL="12 marzo 1990", PAPEL_DA_DATA="CITACAO_DE_NORMA_OU_LEI",
                   TRECHO="Leggi anche: legge 12 marzo 1990 sui fitofarmaci")
        self.assertEqual(r["VALOR"], "NAO SEI")

    def test_J2_trecho_inventado_morre(self):
        r = self.j(TRECHO="Il Bollettino del 1-4 settembre 2026 segnala forte presenza della mosca in tutta la Puglia.")
        self.assertIn("J2", r["JUIZ"])
        self.assertEqual(r["VALOR"], "NAO SEI")

    def test_J3_data_fora_do_trecho_morre(self):
        self.assertIn("J3", self.j(DATA_LITERAL="25 settembre 2026", VALOR="2026-09-25")["JUIZ"])

    def test_J4_data_sem_ano_nao_ganha_ano(self):
        r = self.j(VALOR="2026-04-30", DATA_LITERAL="giovedì 30 aprile", PAPEL_DA_DATA="ACONTECIMENTO",
                   TRECHO="Controlli di giovedì 30 aprile: nessuna cattura nei vigneti.")
        self.assertIn("J4", r["JUIZ"])
        self.assertEqual(r["VALOR"], "NAO SEI")

    def test_J5_valor_que_a_data_nao_diz_morre(self):
        self.assertIn("J5", self.j(VALOR="2026-09-01/2026-09-08")["JUIZ"])
        self.assertIn("J5", self.j(VALOR="2026-09")["JUIZ"])        # menos preciso do que o escrito
        self.assertIn("J5", self.j(VALOR="2025-09-01/2025-09-04")["JUIZ"])

    def test_J6_linha_so_de_data_nao_e_acontecimento(self):
        r = self.j(VALOR="2026-09-07/2026-09-13", DATA_LITERAL="Dal 07-09-2026 al 13-09-2026",
                   TRECHO="Dal 07-09-2026 al 13-09-2026")
        self.assertIn("J6", r["JUIZ"])

    def test_J7_facto_depois_da_captura_morre(self):
        r = L.julgar(TXT, OK, "2026-08-20T10:00:00Z")
        self.assertIn("J7", r["JUIZ"])

    def test_nao_sei_do_modelo_fica_nao_sei(self):
        r = self.j(VALOR="NAO SEI", DATA_LITERAL="", TRECHO="", PAPEL_DA_DATA="OUTRO")
        self.assertEqual((r["VALOR"], r["JUIZ"]), ("NAO SEI", "NAO_SEI_DO_MODELO"))

    def test_literais_que_o_juiz_le(self):
        casos = [("dal 29 Settembre al 3 Ottobre 2025", "2025-09-29/2025-10-03", True),
                 ("Dal 31-08-2026 al 06-09-2026", "2026-08-31/2026-09-06", True),
                 ("settimana 38/2026", "2026-09-14/2026-09-20", True),
                 ("gennaio 2026", "2026-01", True), ("triennio 2024–2026", "2024/2026", True),
                 ("22 settembre", "2026-09-22", False), ("2025", "2026", False), ("14/09/2026", "2026-09-15", False)]
        for lit, v, ok in casos:
            self.assertEqual(L.intervalo_do_valor(v) in L.intervalos_da_literal(lit), ok, (lit, v))


if __name__ == "__main__":
    unittest.main()
