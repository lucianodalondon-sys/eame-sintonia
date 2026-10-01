#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A prova reversa do pote para o LAB (D156, item F) — atacada sem rede e sem navegador.

    python3 -m unittest tests.test_prova_reversa_do_pote -v

⚠️ DADO SINTETICO DECLARADO: potes de tests/fixtures/pote/ (ids SINT-). O «armazem» e uma pasta temporaria com
um byte inventado; o «pote real» e o sintetico com CORRIDA_SINTETICA = false e o RAW apontado para esse byte.
"""
import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "portoes"))
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))
import _gavetas  # noqa: E402,F401

import entrega_de_teste as ET  # noqa: E402
import prova_reversa_do_pote as PR  # noqa: E402
import publicar_portal_sozinho as P  # noqa: E402

FIX = RAIZ / "tests" / "fixtures" / "pote"
DEMO = json.loads((FIX / "POTE-SINTETICO-PUBLICA-SOZINHO.json").read_text(encoding="utf-8"))
VAZIO = json.loads((FIX / "POTE-SINTETICO-VAZIO.json").read_text(encoding="utf-8"))


class A_ProvaReversa(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="teste-prova-reversa-"))
        self.armazem = self.d / "armazem"
        (self.armazem / "XX").mkdir(parents=True)
        self.byte = b"SINT-RAW-DE-TESTE"
        (self.armazem / "XX" / "raw.pdf").write_bytes(self.byte)

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def pote_real(self):
        p = copy.deepcopy(DEMO)
        p["CORRIDA_SINTETICA"] = False
        for e in p["COMPARTIMENTOS"].values():
            for o in e["OBJETOS"]:
                o["CORRIDA_SINTETICA"] = False
                for pr in o["PROVA"]:
                    pr.update(TRECHO_DA_AFIRMACAO="SINT trecho", RAW_SHA256=hashlib.sha256(self.byte).hexdigest(),
                              RAW_STORAGE_PATH="XX/raw.pdf")
        return p

    def correr(self, pote, sha_no_ar=None, ids=None):
        pasta = self.d / "PARA-O-CASCO"
        if pasta.exists():
            shutil.rmtree(pasta)
        ET.entregar(pasta, json.dumps(pote, ensure_ascii=False).encode("utf-8"), "real")
        sha = P.sha_do_pote(pote)
        esperados = [o["OBJETO_ID"] for _, o in PR.objetos_do_pote(pote)]
        return PR.provar(pasta, "https://x.vercel.app", str(self.armazem), self.d / "saida",
                         dom=lambda url, saida: ((esperados if ids is None else ids), None),
                         no_ar=lambda url: (200, sha if sha_no_ar is None else sha_no_ar))

    def estados(self, r, prefixo):
        return [p["ESTADO"] for p in r["PASSOS"] if p["PASSO"].startswith(prefixo)]

    def test_pote_real_passa_ate_ao_byte(self):
        r = self.correr(self.pote_real())
        self.assertEqual(r["VEREDITO"], "PASS", r["PASSOS"])
        self.assertTrue(self.estados(r, "BYTE") and all(e == "PASS" for e in self.estados(r, "BYTE")))

    def test_sha_no_ar_diferente_reprova(self):
        self.assertEqual(self.correr(self.pote_real(), sha_no_ar="0" * 64)["VEREDITO"], "FAIL")

    def test_objeto_que_falta_no_dom_reprova(self):
        self.assertEqual(self.correr(self.pote_real(), ids=["SINT-OP-1"])["VEREDITO"], "FAIL")

    def test_byte_mudado_no_armazem_reprova(self):
        (self.armazem / "XX" / "raw.pdf").write_bytes(b"outro")
        self.assertIn("FAIL", self.estados(self.correr(self.pote_real()), "BYTE"))

    def test_prova_sem_trecho_reprova(self):
        p = self.pote_real()
        p["COMPARTIMENTOS"]["meeting"]["OBJETOS"][0]["PROVA"][0].pop("TRECHO_DA_AFIRMACAO")
        self.assertEqual(self.correr(p)["VEREDITO"], "FAIL")

    def test_pote_sintetico_nao_finge_o_byte(self):
        r = self.correr(DEMO)
        self.assertTrue(all(e == "NAO SEI" for e in self.estados(r, "BYTE")))
        self.assertNotIn("PASS", self.estados(r, "BYTE"))

    def test_f2_o_vazio_legitimo(self):
        r = self.correr(VAZIO)
        self.assertEqual(r["VEREDITO"], "PASS", r["PASSOS"])
        self.assertEqual(self.estados(r, "VAZIO_LEGITIMO"), ["PASS"])
        self.assertEqual(r["OBJETOS"], 0)

    def test_f2_vazio_sem_o_porque_nao_e_legitimo(self):
        """Zero objetos so e resultado legitimo quando CADA compartimento diz porque esta vazio."""
        p = copy.deepcopy(VAZIO)
        p["COMPARTIMENTOS"]["meeting"]["PORQUE_VAZIO"] = None
        r = self.correr(p)
        self.assertEqual(self.estados(r, "VAZIO_LEGITIMO"), ["FAIL"])
        self.assertEqual(r["VEREDITO"], "FAIL")

    def test_pasta_incompleta_para_no_primeiro_passo(self):
        pasta = self.d / "PARA-O-CASCO"
        ET.entregar(pasta, json.dumps(DEMO).encode(), "sha")
        r = PR.provar(pasta, "https://x.vercel.app", None, self.d / "s", dom=lambda u, s: ([], None),
                      no_ar=lambda u: (200, None))
        self.assertEqual((r["VEREDITO"], r["PASSOS"][0]["PASSO"]), ("FAIL", "SHA_DA_PASTA"))


if __name__ == "__main__":
    unittest.main()
