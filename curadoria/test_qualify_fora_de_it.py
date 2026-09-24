#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D31 (24/09): candidata EU/INT entra so com a AUTORIZACAO escrita na propria decisao.

Sem rede, em pastas temporarias. A QUALIFY:
  * com PAIS=EU e NUMERACAO_FORA_DE_IT -> numero EU-T<n>-<seq>, acima do maior EU do Atlas;
  * com PAIS=INT e autorizacao          -> INT-T<n>-<seq>;
  * com PAIS=EU SEM autorizacao          -> BLOCK, como antes (a maquina nao decide numeracao);
  * com PAIS=IT                          -> IT-, como sempre.
"""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F                  # noqa: E402
import lifecycle as LC            # noqa: E402
import worker as W                # noqa: E402


class AQualifyForaDeIT(unittest.TestCase):

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        d = Path(self._td.name)
        for mod, nome, v in ((W, "ALLOCATION", d / "alloc.json"), (LC, "LIVRO", d / "ledger.json"),
                             (F, "FILA", d / "fila.json")):
            self.addCleanup(setattr, mod, nome, getattr(mod, nome))
            setattr(mod, nome, v)
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}), encoding="utf-8")
        self.ficha = {"CANDIDATA_ID": "CAND-9001", "TIPO": "ORGANIZACAO", "NOME": "Xyzzy Europa",
                      "URL": "https://xyzzy.example/", "PAIS": "NAO SEI"}
        self.addCleanup(setattr, W, "_ficha_candidata", W._ficha_candidata)
        W._ficha_candidata = lambda cid: dict(self.ficha)
        self.addCleanup(setattr, W.ASI, "territorio_de", W.ASI.territorio_de)
        W.ASI.territorio_de = lambda c: ("NAO SEI", "o nome nao diz")
        self.addCleanup(setattr, W.DS, "decisao_para", W.DS.decisao_para)

    def _com(self, **dec):
        base = {"TERRITORIO": "T9", "PAIS": "EU", "DECIDIDO_POR": "teste", "PORQUE": "p", "PROVAS": []}
        base.update(dec)
        W.DS.decisao_para = lambda cid, ficha: (base, "decisao semantica valida")
        return W.etapa_qualify("CAND-9001", None)

    def _maior_eu_no_atlas(self, t):
        a = (RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md").read_text(encoding="utf-8", errors="replace")
        return max([int(q) for tt, q in re.findall(r"\bEU-(T\d+)-(\d+)\b", a) if tt == t] or [0])

    def test_eu_com_autorizacao_recebe_numero_eu_acima_do_atlas(self):
        r, det = self._com(NUMERACAO_FORA_DE_IT="D31")
        self.assertEqual(r, "OK", det)
        sid = det["SOURCE_ID_REAL"]
        m = re.match(r"^EU-T9-(\d{3})$", sid)
        self.assertTrue(m, sid)
        self.assertGreater(int(m.group(1)), self._maior_eu_no_atlas("T9"))
        self.assertIn("D31", json.loads(W.ALLOCATION.read_text(encoding="utf-8"))["NOVAS"][0]["ALLOCATED_BY"])

    def test_int_com_autorizacao(self):
        r, det = self._com(PAIS="INT", TERRITORIO="T10", NUMERACAO_FORA_DE_IT="D31")
        self.assertEqual(r, "OK", det)
        self.assertRegex(det["SOURCE_ID_REAL"], r"^INT-T10-\d{3}$")

    def test_eu_sem_autorizacao_continua_bloqueada(self):
        r, det = self._com()
        self.assertEqual(r, "BLOCK")
        self.assertEqual(det["CLASSE"], "SEMANTIC")
        self.assertFalse(W.ALLOCATION.exists() and json.loads(W.ALLOCATION.read_text(encoding="utf-8"))["NOVAS"])

    def test_outro_pais_nao_se_autoriza(self):
        r, det = self._com(PAIS="FR", NUMERACAO_FORA_DE_IT="D31")
        self.assertEqual(r, "BLOCK")

    def test_it_continua_it(self):
        r, det = self._com(PAIS="IT")
        self.assertEqual(r, "OK", det)
        self.assertRegex(det["SOURCE_ID_REAL"], r"^IT-T9-\d{3}$")


class OValidadorDeContratosD31(unittest.TestCase):

    def test_eu_e_int_passam_o_formato_e_outro_prefixo_nao(self):
        import validar_contratos as VC
        import escrever_contratos as EC
        for sid, ok in (("EU-T9-003", True), ("INT-T10-001", True), ("IT-T9-001", True),
                        ("FR-T4-009", False), ("EUX-T9-001", False)):
            c = EC.contrato_html({"SOURCE_ID": sid, "NOME": "x", "TERRITORY": "T9",
                                  "URL": "https://ex.example/news/"}, {})
            c["SOURCE_CONTRACT_VERSION"] = EC.VERSAO
            c["SOURCE_CONTRACT_HASH"] = EC.hash_do_contrato(c)
            with self.subTest(sid=sid):
                self.assertEqual(VC.schema_valid(c)[0], ok, VC.schema_valid(c))


if __name__ == "__main__":
    unittest.main()
