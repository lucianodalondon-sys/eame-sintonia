# -*- coding: utf-8 -*-
"""Provas de comparar_micro_com_previsao.py — sem rede, sem banco (a consulta e injectada).

    py -m unittest scripts/capa_materia/test_comparar_micro_com_previsao.py
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comparar_micro_com_previsao as C   # noqa: E402

PREV = {"DATASET": "P", "MEDIDO_EM": "2026-09-25T07:33:10Z",
        "TOTAL": {"DOCUMENTOS_NOVOS_POR_CORRIDA_D40_D38": 4},
        "FONTES": [{"SOURCE_ID": "IT-A", "DOCUMENTOS_NOVOS_NA_CORRIDA": 3, "ALVOS_D40": ["https://a.it/1", "https://a.it/2"]},
                   {"SOURCE_ID": "IT-B", "DOCUMENTOS_NOVOS_NA_CORRIDA": 1, "ALVOS_D40": ["https://b.it/1"]},
                   {"SOURCE_ID": "IT-C", "DOCUMENTOS_NOVOS_NA_CORRIDA": 0, "ALVOS_D40": []}]}
CORRIDAS = [("IT-A", "RA"), ("IT-B", "RB"), ("IT-C", "RC")]
OBS = [
    {"RUN_ID": "RA", "SOURCE_ID": "IT-A", "SOURCE_URL": "https://a.it/1", "OBSERVATION_RESULT": "NEW_DOCUMENT"},
    {"RUN_ID": "RA", "SOURCE_ID": "IT-A", "SOURCE_URL": "https://a.it/9", "OBSERVATION_RESULT": "NEW_DOCUMENT"},
    {"RUN_ID": "RA", "SOURCE_ID": "IT-A", "SOURCE_URL": "https://a.it/0", "OBSERVATION_RESULT": "SEEN_AGAIN"},
    {"RUN_ID": "RC", "SOURCE_ID": "IT-C", "SOURCE_URL": "https://c.it/1", "OBSERVATION_RESULT": "DOCUMENT_CHANGED_IN_PLACE"},
    {"RUN_ID": "OUTRA", "SOURCE_ID": "IT-A", "SOURCE_URL": "https://a.it/5", "OBSERVATION_RESULT": "NEW_DOCUMENT"},
]
DEC = [
    {"item": "derived:11", "resultado": "SIM", "regra": "pertence ao universo", "motivo": "fala de vendemmia", "corrida": "RA"},
    {"item": "derived:12", "resultado": "NAO", "regra": "outro universo", "motivo": "impostos", "corrida": "RA"},
    {"item": "derived:13", "resultado": "NAO_SEI", "regra": "legivel", "motivo": "sem texto", "corrida": "RC"},
    {"item": "NAO SEI", "resultado": "NAO_SEI", "regra": "legivel", "motivo": "falha", "corrida": "RB"},
    {"item": "derived:99", "resultado": "SIM", "regra": "x", "motivo": "y", "corrida": "OUTRA"},
]


def banco_falso(sql):
    if "from raw_asset" in sql:
        assert "'RA'" in sql and "'OUTRA'" not in sql
        return [["1", "IT-A", "RA", "https://a.it/1", "11"], ["2", "IT-A", "RA", "https://a.it/9", "12"],
                ["3", "IT-A", "RA", "https://a.it/0", ""], ["4", "IT-C", "RC", "https://c.it/1", "13"]]
    return [["derived:11"]]


class TestComparar(unittest.TestCase):
    def _com_banco(self):
        return C.comparar(CORRIDAS, OBS, DEC, PREV, C.consultar_banco(["RA", "RB", "RC"], banco_falso))

    def test_por_fonte_previsto_contra_real(self):
        f = {x["SOURCE_ID"]: x for x in self._com_banco()["FONTES"]}
        self.assertEqual((3, 2, -1, 1), (f["IT-A"]["PREVISTO_NOVOS"], f["IT-A"]["REAL_NOVOS"],
                                         f["IT-A"]["DIFERENCA"], f["IT-A"]["NOVOS_QUE_ERAM_PREVISTOS"]))
        self.assertEqual((1, 0, -1), (f["IT-B"]["PREVISTO_NOVOS"], f["IT-B"]["REAL_NOVOS"], f["IT-B"]["DIFERENCA"]))
        self.assertEqual((0, 1), (f["IT-C"]["REAL_NOVOS"], f["IT-C"]["REAL_VERSOES_NOVAS"]),
                         "versao nova de um documento ja conhecido nao conta como novo")

    def test_cada_documento_com_o_seu_veredicto(self):
        docs = {d["SOURCE_URL"]: d for d in self._com_banco()["DOCUMENTOS"]}
        self.assertEqual(("SIM", True, True), (docs["https://a.it/1"]["ADMISSION"], docs["https://a.it/1"]["NA_SALA"],
                                               docs["https://a.it/1"]["ESTAVA_NA_PREVISAO"]))
        self.assertEqual(("NAO", False, "impostos"), (docs["https://a.it/9"]["ADMISSION"], docs["https://a.it/9"]["NA_SALA"],
                                                     docs["https://a.it/9"]["MOTIVO"]))
        self.assertNotIn("https://a.it/0", docs, "SEEN_AGAIN nao e documento novo")
        self.assertNotIn("https://a.it/5", docs, "corrida fora da lista nao entra")

    def test_so_as_corridas_pedidas_contam(self):
        t = self._com_banco()["TOTAL"]
        self.assertEqual({"SIM": 1, "NAO": 1, "NAO_SEI": 2}, t["ADMISSION_DAS_CORRIDAS"])
        self.assertEqual("1/3", t["SIM_SOBRE_FONTES"])

    def test_sem_banco_diz_nao_sei_e_nao_inventa(self):
        out = C.comparar(CORRIDAS, OBS, DEC, PREV, None)
        self.assertTrue(all(d["ADMISSION"] == "NAO SEI" for d in out["DOCUMENTOS"]))
        self.assertTrue(out["BANCO"].startswith("NAO_LIDO"))
        self.assertEqual(2, out["TOTAL"]["REAL_NOVOS"], "as contagens por fonte fazem-se na mesma")
        f = {x["SOURCE_ID"]: x for x in out["FONTES"]}
        self.assertEqual({"SIM": 1, "NAO": 1}, f["IT-A"]["ADMISSION_DA_CORRIDA"])

    def test_endereco_ambiguo_no_banco_nao_se_liga_a_sorte(self):
        def dois(sql):
            if "from raw_asset" in sql:
                return [["1", "IT-A", "RA", "https://a.it/1", "11"], ["5", "IT-A", "RA", "https://a.it/1", "12"]]
            return []
        out = C.comparar(CORRIDAS, OBS, DEC, PREV, C.consultar_banco(["RA"], dois))
        d = next(x for x in out["DOCUMENTOS"] if x["SOURCE_URL"] == "https://a.it/1")
        self.assertEqual("NAO SEI", d["ADMISSION"])
        self.assertIn("2 raw_asset", d["LIGACAO"])

    def test_so_le_e_so_escreve_na_saida(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            arv = t / "arvore"
            (arv / "data/collection-ledger/italy").mkdir(parents=True)
            (arv / "data/samples").mkdir(parents=True)
            obs_p = arv / "data/collection-ledger/italy/observations.ndjson"
            obs_p.write_text("".join(json.dumps(o) + "\n" for o in OBS), encoding="utf-8")
            liv_p = arv / "data/samples/LIVRO-DE-DECISOES.json"
            liv_p.write_text(json.dumps({"DECISOES": DEC}), encoding="utf-8")
            prev_p = t / "prev.json"
            prev_p.write_text(json.dumps(PREV), encoding="utf-8")
            antes = {p: p.read_bytes() for p in (obs_p, liv_p, prev_p)}
            self.assertEqual(0, C.main(["--runs", "RA,RB,RC", "--saida", str(t / "saida"), "--arvore", str(arv),
                                        "--previsao", str(prev_p), "--sem-banco"]))
            self.assertEqual(antes, {p: p.read_bytes() for p in antes})
            self.assertEqual({"COMPARACAO-MICRO-COM-PREVISAO-V1.json", "DOCUMENTOS-DO-MICRO.tsv"},
                             {p.name for p in (t / "saida").iterdir()})


if __name__ == "__main__":
    unittest.main()
