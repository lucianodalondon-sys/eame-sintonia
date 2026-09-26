# -*- coding: utf-8 -*-
"""FREIO-SOCIAL · o MESMO video partilhado por duas contas diz de quem e — e UNKNOWN nao funde.

Os dois objetos sao os do canario LinkedIn REAL de 24/09 (ISPRA e ARPA Valle d'Aosta),
reduzidos aos campos de identidade (`tests/dados/videos-partilhados-arpa-ispra.json`):
dois POSTS diferentes, o MESMO `ASSET_URN`.
"""
import copy
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, "coleta"), os.path.join(RAIZ, "leis")):
    sys.path.insert(0, p)
import _gavetas  # noqa: E402,F401
import identidade_do_video as IV  # noqa: E402

with open(os.path.join(RAIZ, "tests", "dados", "videos-partilhados-arpa-ispra.json"), encoding="utf-8") as _f:
    ISPRA, ARPA = json.load(_f)["OBJETOS"]


def u(sid, run):
    return {"SOURCE_ID": sid, "RUN_ID": run, "DOCUMENT_ID": "NAO SEI"}


class _Reg(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="dedup-")
        self.addCleanup(shutil.rmtree, self.d, True)
        self.reg = os.path.join(self.d, "VIDEOS.ndjson")

    def linhas(self):
        if not os.path.exists(self.reg):
            return []
        with open(self.reg, encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]


class D1OMesmoVideoEmDuasContas(_Reg):
    def test_a_partilha_diz_de_quem_e_o_video(self):
        [a] = IV.marcar([u("IT-T5-160", "R-ISPRA")], [ISPRA], self.reg)
        [b] = IV.marcar([u("IT-T2-137", "R-ARPA")], [ARPA], self.reg)
        self.assertEqual(a["VIDEO_IDENTITY"], "LINKEDIN:urn:li:digitalmediaAsset:D4D05AQH1yJW2COxvNQ")
        self.assertEqual(a["VIDEO_IDENTITY"], b["VIDEO_IDENTITY"])
        self.assertNotIn("MESMO_VIDEO_QUE", a)
        self.assertEqual(b["MESMO_VIDEO_QUE"]["SOURCE_ID"], "IT-T5-160")
        self.assertEqual(b["MESMO_VIDEO_QUE"]["RUN_ID"], "R-ISPRA")
        self.assertEqual(len(self.linhas()), 1)                     # um video, uma linha

    def test_os_posts_sao_dois_o_video_e_um(self):
        self.assertNotEqual(ISPRA["RAW"]["ACTIVITY_ID"], ARPA["RAW"]["ACTIVITY_ID"])
        self.assertTrue(IV.mesmo_video(IV.identidade(ISPRA)[0], IV.identidade(ARPA)[0]))

    def test_o_mesmo_post_colhido_outra_vez_nao_e_partilha(self):
        IV.marcar([u("IT-T5-160", "R1")], [ISPRA], self.reg)
        [b] = IV.marcar([u("IT-T5-160", "R2")], [ISPRA], self.reg)
        self.assertNotIn("MESMO_VIDEO_QUE", b)

    def test_nada_se_apaga(self):
        us = IV.marcar([u("IT-T5-160", "R"), u("IT-T2-137", "R")], [ISPRA, ARPA], self.reg)
        self.assertEqual(len(us), 2)


class D2UnknownNaoFunde(_Reg):
    def test_sem_asset_urn_fica_nao_sei_e_nao_junta(self):
        a, b = copy.deepcopy(ISPRA), copy.deepcopy(ARPA)
        a["RAW"].pop("ASSET_URN")
        b["RAW"].pop("ASSET_URN")
        x, y = IV.marcar([u("A", "R1"), u("B", "R2")], [a, b], self.reg)
        self.assertEqual((x["VIDEO_IDENTITY"], y["VIDEO_IDENTITY"]), ("NAO SEI", "NAO SEI"))
        self.assertIn("NAO SEI", x["VIDEO_IDENTITY_BASIS"])
        self.assertNotIn("MESMO_VIDEO_QUE", y)
        self.assertEqual(self.linhas(), [])
        self.assertFalse(IV.mesmo_video(None, None))
        self.assertFalse(IV.mesmo_video("NAO SEI", "NAO SEI"))

    def test_o_urn_do_post_nao_e_o_do_video(self):
        a = copy.deepcopy(ISPRA)
        a["RAW"].pop("ASSET_URN")
        self.assertIsNone(IV.identidade(a)[0])                      # a ACTIVITY nao basta

    def test_youtube_pelo_id_e_id_torto_e_nao_sei(self):
        self.assertEqual(IV.identidade({"PLATFORM": "YOUTUBE", "NATIVE_ID": "AbCdEfGhIjK"})[0],
                         "YOUTUBE:AbCdEfGhIjK")
        self.assertIsNone(IV.identidade({"PLATFORM": "YOUTUBE", "NATIVE_ID": "curto"})[0])
        self.assertIsNone(IV.identidade({"PLATFORM": "INSTAGRAM", "NATIVE_ID": "x"})[0])


class D3OScrapCarimba(_Reg):
    def test_fase_social_carimba_e_regista(self):
        import scrap_colheita as sc
        import scrap_executor as sx

        def collect(**kw):
            return [copy.deepcopy(ISPRA)], {"RESULT": "OK", "COST_STATE": "RUN"}
        with mock.patch.dict(os.environ, {"ITALY_OPS_ROOT": self.d}), mock.patch.object(sx, "COLLECT", collect):
            env = sc.colher("video-linkedin", run_id="IT-T5-2026-09-26-050000-0123456789abcdef",
                            fonte="IT-T8-001", pagina_url="https://www.linkedin.com/company/ispra_2/")
        # (IT-T8-001: uma fonte que o Atlas conhece — sem ela a colheita sai CANDIDATA, sem unidades)
        [un] = env["COLHEITA"]
        self.assertEqual(un["VIDEO_IDENTITY"], "LINKEDIN:urn:li:digitalmediaAsset:D4D05AQH1yJW2COxvNQ")
        with open(os.path.join(self.d, IV.REGISTO), encoding="utf-8") as f:
            self.assertEqual(len(f.readlines()), 1)



if __name__ == "__main__":
    unittest.main()
