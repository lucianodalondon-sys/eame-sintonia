# -*- coding: utf-8 -*-
"""K1 — receitas V4, canario em copia e as tres politicas medidas. Sem rede."""
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
for p in ("medidas", "curadoria", "scripts/receitas", "scripts/detector_capa"):
    sys.path.insert(0, str(RAIZ / p))
import medir_k1 as K          # noqa: E402
import medir_gabarito as MG   # noqa: E402
import canario_receitas_k1 as CK  # noqa: E402

AQ = {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": "https://a.it/news/", "LINK_PATTERN": "^https://a\\.it/news/.+$"}


class Politicas(unittest.TestCase):
    def pol(self, bem):
        return K.politicas(bem, {"IT-T7-001": {"ACQUISITION": AQ}})

    def test_actual_segue_o_detector(self):
        p = self.pol(set())["ACTUAL"]
        self.assertEqual("BARRADA", p({"CAPA_OU_MATERIA": MG.CAPA}, "https://a.it/news/x", "IT-T7-001"))
        self.assertEqual("RETIDA", p({"CAPA_OU_MATERIA": MG.NS}, "https://a.it/news/x", "IT-T7-001"))
        self.assertEqual("ENTRA", p({"CAPA_OU_MATERIA": MG.MAT}, "https://a.it/news/x", "IT-T7-001"))

    def test_c_retem_a_capa_so_de_fonte_bem_configurada(self):
        cap = {"CAPA_OU_MATERIA": MG.CAPA}
        self.assertEqual("RETIDA", self.pol({"IT-T7-001"})["C"](cap, "https://a.it/news/x", "IT-T7-001"))
        self.assertEqual("BARRADA", self.pol(set())["C"](cap, "https://a.it/news/x", "IT-T7-001"))

    def test_v1_so_manda_na_fonte_bem_configurada(self):
        mat = {"CAPA_OU_MATERIA": MG.MAT}
        self.assertEqual("BARRADA", self.pol({"IT-T7-001"})["V1"](mat, "https://a.it/news/", "IT-T7-001"))
        self.assertEqual("ENTRA", self.pol(set())["V1"](mat, "https://a.it/news/", "IT-T7-001"))
        self.assertEqual("ENTRA", self.pol({"IT-T7-001"})["V1"](mat, "https://a.it/news/x", "IT-T7-001"))


class Canario(unittest.TestCase):
    def test_para_se_o_egresso_nao_for_it_antes_de_qualquer_pedido(self):
        with mock.patch.object(CK, "egresso", return_value={"COUNTRY": "BR"}), \
             mock.patch.object(CK.CAN, "canario_html") as can, mock.patch.object(CK.GATE, "robots_de") as rob:
            r = CK.correr({"IT-T7-001": {"ACQUISITION": AQ}}, ["IT-T7-001", "IT-T7-002"])
        self.assertEqual(1, len(r))
        self.assertIn("EGRESSO_NAO_IT", r[0]["PARADO"])
        can.assert_not_called(), rob.assert_not_called()

    def test_robots_que_proibe_nao_se_bate(self):
        rp = mock.Mock()
        with mock.patch.object(CK, "egresso", return_value={"COUNTRY": "IT"}), \
             mock.patch.object(CK.GATE, "robots_de", return_value=(rp, "User-agent: *")), \
             mock.patch.object(CK.GATE, "permitido", return_value=False), \
             mock.patch.object(CK.CAN, "canario_html") as can, mock.patch.object(CK.time, "sleep"):
            r = CK.correr({"IT-T7-001": {"ACQUISITION": AQ}}, ["IT-T7-001"])
        can.assert_not_called()
        self.assertIn("robots", r[0]["PARADO"])


class BemConfiguradas(unittest.TestCase):
    def test_contrato_mudado_sem_canario_deixa_de_contar(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            pos = d / "POS"
            pos.mkdir()
            prova = {"EVIDENCE_REF": "EV1", "DADOS": {"DETAIL_ENUMERATED": 5, "DETAIL_GATE_PASSED": True,
                     "ITEM_ABERTO": {"URL": "https://a.it/news/um-dois-tres", "HTTP": 200, "HTML_KIND": "CONTENT",
                                     "CAPA_OU_MATERIA": "MATERIA_PROVAVEL", "PARAGRAPH_CHARACTERS": 900}}}
            (pos / "LIFECYCLE-LEDGER-V1.json").write_text(json.dumps({"TRANSICOES": [
                {"SOURCE_ID": "IT-T7-001", "PREVIOUS_STATE": "CANARY_PENDING", "NEW_STATE": "READY_FOR_COLLECTION",
                 "EVIDENCE_REF": "EV1", "OBSERVED_AT": "2026-09-22T00:00:00+00:00"}]}), encoding="utf-8")
            (pos / "LIFECYCLE-EVIDENCE-V1.json").write_text(json.dumps({"PROVAS": [prova]}), encoding="utf-8")
            (pos / "italy_contracts_curator.json").write_text(json.dumps({"FONTES": [
                {"SOURCE_ID": "IT-T7-001", "ACQUISITION": AQ}]}), encoding="utf-8")
            (d / "depois.json").write_text(json.dumps({"FONTES": [
                {"SOURCE_ID": "IT-T7-001", "ACQUISITION": dict(AQ, LINK_PATTERN="^x$")}]}), encoding="utf-8")
            (d / "can.json").write_text(json.dumps({"LINHAS": []}), encoding="utf-8")
            antes, depois, _ = K.bem_configuradas(pos, d / "depois.json", d / "can.json")
        self.assertEqual(({"IT-T7-001"}, set()), (antes, depois))


class ReceitasV4(unittest.TestCase):
    def test_as_paginas_do_controlo_entram_so_rotuladas_e_sem_repetir(self):
        import propor_receitas_v4 as V4
        ctrl = V4.paginas_do_controlo()
        self.assertTrue(ctrl)
        self.assertEqual({"CAPA", "MATERIA"}, {p["VEREDITO"] for p in ctrl})
        todas = V4.paginas()
        self.assertEqual(len(todas), len({p["URL"] for p in todas}))
        self.assertTrue(any(p["ORIGEM"].startswith("controlo-ld2:") for p in todas))

    def test_o_g1_le_a_v4_depois_das_outras(self):
        texto = (RAIZ / "scripts" / "desbloqueio" / "aplicar_desbloqueio.py").read_text(encoding="utf-8")
        i3, i4 = texto.index('"PROPOSTA-RECEITAS-V3.json"'), texto.index('"PROPOSTA-RECEITAS-V4.json"')
        self.assertLess(i3, i4)


class Resultado(unittest.TestCase):
    R = json.loads((RAIZ / "curadoria" / "K1-MEDICAO-V1.json").read_text(encoding="utf-8"))

    def test_v1_nao_barra_nenhuma_noticia_a_mais(self):
        for f, x in self.R["DEPOIS_RECEITAS"]["V1"].items():
            self.assertEqual(self.R["DEPOIS_RECEITAS"]["ACTUAL"][f]["NOTICIAS_BARRADAS"], x["NOTICIAS_BARRADAS"], f)

    def test_c_na_validacao_cega_so_acrescenta_capas_a_quarentena(self):
        a, c = self.R["DEPOIS_RECEITAS"]["ACTUAL"]["CONTROLO_CEGA"], self.R["DEPOIS_RECEITAS"]["C"]["CONTROLO_CEGA"]
        self.assertGreater(c["CAPAS_RETIDAS"], a["CAPAS_RETIDAS"])
        self.assertEqual(a["NOTICIAS_BARRADAS"], c["NOTICIAS_BARRADAS"])


if __name__ == "__main__":
    unittest.main()
