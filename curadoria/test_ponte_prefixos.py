#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D32 (2): a ponte (reconciliar_livros) aceita EU-/INT- como SOURCE_ID; outro prefixo falha fechado."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "curadoria"))
import reconciliar_livros as R   # noqa: E402


class APonteSoAceitaOsPrefixosDecididos(unittest.TestCase):

    CTX = {"ALIAS": {"CAND-0515": "EU-T9-003"}}

    def test_it_eu_int_sao_source_id(self):
        for sid in ("IT-T3-015", "EU-T9-003", "INT-T10-001", "INT-T11-001"):
            with self.subTest(sid=sid):
                self.assertEqual(R.identidade(sid, self.CTX), (sid, "SOURCE_ID"))

    def test_outro_prefixo_falha_fechado(self):
        for sid in ("FR-T4-001", "EUX-T9-001", "INTL-T10-001", "it-T3-015", "EU-T9-3", "EU-9-003"):
            with self.subTest(sid=sid):
                self.assertEqual(R.identidade(sid, self.CTX)[1], "INVALIDO")

    def test_candidata_com_numero_eu_e_alias(self):
        self.assertEqual(R.identidade("CAND-0515", self.CTX), ("EU-T9-003", "ALIAS_DE_CANDIDATA"))


if __name__ == "__main__":
    unittest.main()
