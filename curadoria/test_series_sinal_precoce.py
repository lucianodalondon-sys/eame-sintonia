# -*- coding: utf-8 -*-
"""SERIES DO SINAL PRECOCE — natureza so pelo texto, conferencia da transcricao, extractores e o que conta como serie."""
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import series_sinal_precoce as S   # noqa: E402


class Natureza(unittest.TestCase):
    def test_observacao_previsao_recomendacao(self):
        self.assertEqual(["OBSERVACAO"], S.natureza("Si riscontrano poche catture nelle trappole a feromoni."))
        self.assertIn("PREVISAO", S.natureza("L'aumento dell'umidita possono favorire l'occhio di pavone."))
        self.assertEqual(["RECOMENDACAO"], S.natureza("Si consiglia di intervenire con prodotti rameici."))

    def test_limiar_nao_e_observacao(self):
        f = "Contro la cidia al superamento della soglia di intervento, che e di 10 catture per trappola a settimana"
        self.assertNotIn("OBSERVACAO", S.natureza(f))

    def test_monitorar_e_recomendacao_nao_observacao(self):
        f = "Proseguire il monitoraggio mediante le trappole a feromoni e, alle prime catture, eseguire i campionamenti."
        self.assertEqual(["RECOMENDACAO"], S.natureza(f))

    def test_sem_pista_sem_natureza(self):
        self.assertEqual([], S.natureza("Il consorzio ha sede a Lecce."))


class Confere(unittest.TestCase):
    def test_exato_em_ordem_e_nao(self):
        corrido = "Monte Longobardi varie Accrescimento n. 0 catture di Sarno Prays Citri. n. 4 catture di Ceratitis Capitata"
        self.assertEqual("EXATO", S.confere("n. 4 catture di Ceratitis Capitata", corrido))
        self.assertEqual("EM_ORDEM", S.confere("n. 0 catture di Prays", corrido))
        self.assertIsNone(S.confere("n. 40 catture di Ceratitis", corrido))

    def test_palavras_longe_demais_nao_conferem(self):
        corrido = "n. 4 catture di " + "outra coluna " * 20 + "Ceratitis"
        self.assertIsNone(S.confere("n. 4 catture di Ceratitis", corrido))

    def test_salerno_desconhecido_nao_inventa(self):
        r = S.salerno("N° 30 del 30/09/2026 ... n. 7 catture di Ceratitis", sha="ffffffffffff")
        self.assertEqual("NAO LIDO", r[0]["METRICA"])


class Extractores(unittest.TestCase):
    def test_terre_etruria_ponto(self):
        t = ("Catture adulti: Dato per utenti registrati Grosseto, poggio al vento Torna alla mappa Latitudine: 42.77, "
             "Longitudine: 11.1 Data di campionamento: 07-09-2026 Infestazione attiva: 4%, Pre allerta Catture adulti: "
             "Dato per utenti registrati")
        p = S.terretruria(t)[0]
        self.assertEqual(("Grosseto, poggio al vento", "2026-09-07", "4%", "Pre allerta"),
                         (p["LOCAL"], p["DATA"], p["VALOR"], p["ESTADO"]))
        self.assertIn("utenti registrati", p["CATTURE_ADULTI"])

    def test_apol_linha_com_um_espaco(self):
        t = ("                                  14/09/2026 - 20/09/2026\n   COMPRENSORIO - LE - PIANURA\n\n   SALENTINA SUD\n"
             "INGROSSAMENTO FRUTTI 6              1                  5%              STAZIONARIO             BASSO\n")
        r = S.apol(t)[0]
        self.assertEqual("COMPRENSORIO LE - PIANURA SALENTINA SUD", r["LOCAL"])
        self.assertEqual((6, 1, "5%", "2026-09-14"), (r["COLUNA_1"], r["COLUNA_2"], r["COLUNA_3"], r["DATA"]))
        self.assertIn("NAO SEI", r["METRICA"])

    def test_arif_blocos_pelos_rotulos(self):
        t = ("Notiziario - n. 38 del 16 settembre 2026\nSituazione Fenologica:\nInvaiatura.\nSituazione Fitosanitaria:\n"
             "Aumento del numero di punture di ovodeposizione (Bactrocera oleae).\nProgramma di Difesa:\nIntervenire al "
             "raggiungimento della soglia del 4-5% di infestazione attiva.\n")
        b = S.arif(t)[0]
        self.assertEqual(("Invaiatura.", "2026-09-16"), (b["FASE"], b["DATA"]))
        self.assertIn("Aumento del numero", b["OBSERVACAO"])
        self.assertEqual(1, len(b["LIMIARES"]))
        self.assertEqual(["OBSERVACAO", "RECOMENDACAO"], b["NATUREZA"])


class Series(unittest.TestCase):
    def doc(self, sid, forma, linhas, **k):
        return {"SOURCE_ID": sid, "FORMA": forma, "LINHAS": linhas, **k}

    def test_serie_real_so_com_duas_datas(self):
        docs = [self.doc("IT-T3-005", "TERRETRURIA", [{"LOCAL": "A", "ORGANISMO": "mosca", "METRICA": "I", "VALOR": "0%", "DATA": "2026-09-01"},
                                                     {"LOCAL": "B", "ORGANISMO": "mosca", "METRICA": "I", "VALOR": "1%", "DATA": "2026-09-01"}]),
                self.doc("IT-T3-005", "TERRETRURIA", [{"LOCAL": "A", "ORGANISMO": "mosca", "METRICA": "I", "VALOR": "3%", "DATA": "2026-09-07"}])]
        s = {x["LOCAL_OU_CULTURA"]: x for x in S.series(docs)}
        self.assertTrue(s["A"]["REAL"])
        self.assertFalse(s["B"]["REAL"])

    def test_arif_nao_pareia_se_os_blocos_diferem(self):
        b = lambda i, n, d: {"BLOCO": i, "BOLETIM_N": n, "DATA": d, "FASE": "", "OBSERVACAO": "x", "LIMIARES": []}  # noqa: E731
        docs = [self.doc("IT-T3-008", "ARIF", [b(0, "36", "2026-09-02"), b(1, "36", "2026-09-02")]),
                self.doc("IT-T3-008", "ARIF", [b(0, "38", "2026-09-16")])]
        q = S.series_qualitativas(docs)
        self.assertTrue(all(len(x["POR_DATA"]) == 1 for x in q))
        self.assertTrue(all("SEM PAR" in x["CHAVE"] for x in q))


if __name__ == "__main__":
    unittest.main()
