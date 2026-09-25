# -*- coding: utf-8 -*-
"""Provas de curadoria/alinhar_com_o_coletor.py — sem rede, sem escrever no livro real."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import alinhar_com_o_coletor as AL   # noqa: E402

LIVRO = json.loads((AQUI / "italy_contracts_curator.json").read_text(encoding="utf-8"))
TABELA = json.loads((AQUI.parent / "regras" / "italy_contracts_onboarded.json").read_text(encoding="utf-8"))
ISTAT = "IT-T5-090"
NOVO = "^https?://(www\\.)?istat\\.it/(?:comunicato-stampa|notizia)/[a-z0-9]+(?:-[a-z0-9]+)+/?$"


def _livro_antigo():
    """O livro como estava antes da D44 (a istat com o padrao do molde), se ja foi alinhado."""
    livro = copy.deepcopy(LIVRO)
    for c in livro["FONTES"]:
        if c["SOURCE_ID"] == ISTAT and c.get("REPARO_DE_CONTRATO", {}).get("DECISAO") == "D44":
            ant = c["REPARO_DE_CONTRATO"]["ACQUISITION_ANTERIOR"]
            c["ACQUISITION"] = ant
            for k in ("REPARO_DE_CONTRATO", "ROUTE_PROVENANCE"):
                c.pop(k, None)
    return livro


def _c(livro, sid):
    return next(c for c in livro["FONTES"] if c["SOURCE_ID"] == sid)


class TestAlinhar(unittest.TestCase):
    def test_a_istat_passa_a_ter_o_padrao_do_coletor(self):
        antes = _livro_antigo()
        depois, acoes = AL.alinhar(antes, TABELA, "D44", quando="2026-09-25T09:00:00+00:00")
        c = _c(depois, ISTAT)
        self.assertEqual(NOVO, c["ACQUISITION"]["LINK_PATTERN"])
        self.assertEqual(_c(antes, ISTAT)["ACQUISITION"], c["REPARO_DE_CONTRATO"]["ACQUISITION_ANTERIOR"])
        self.assertEqual("D44", c["REPARO_DE_CONTRATO"]["DECISAO"])
        self.assertTrue(c["REPARO_DE_CONTRATO"]["PRECISA_DE_REMEDIR"])
        self.assertNotEqual(_c(antes, ISTAT)["SOURCE_CONTRACT_HASH"], c["SOURCE_CONTRACT_HASH"])
        self.assertEqual([{"SOURCE_ID": ISTAT, "DECISAO": "D44", "ACAO": "APLICA"}],
                         [{k: x[k] for k in ("SOURCE_ID", "DECISAO", "ACAO")} for x in acoes])

    def test_nenhuma_outra_fonte_muda_nem_um_byte(self):
        antes = _livro_antigo()
        depois, _ = AL.alinhar(antes, TABELA, "D44")
        for a, b in zip(antes["FONTES"], depois["FONTES"]):
            if a["SOURCE_ID"] != ISTAT:
                self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True), a["SOURCE_ID"])
        self.assertEqual(len(antes["FONTES"]), len(depois["FONTES"]))

    def test_fonte_divergente_fora_da_decisao_fica_como_esta(self):
        antes = _livro_antigo()
        tabela = copy.deepcopy(TABELA)
        outra = next(l for l in tabela["FONTES"] if l["SOURCE_ID"] != ISTAT and l.get("ACQUISITION")
                     and any(c["SOURCE_ID"] == l["SOURCE_ID"] for c in antes["FONTES"]))
        outra["ACQUISITION"] = dict(outra["ACQUISITION"], LINK_PATTERN="^https?://x\\.it/nova/.+$")
        depois, _ = AL.alinhar(antes, tabela, "D44")
        self.assertEqual(_c(antes, outra["SOURCE_ID"]), _c(depois, outra["SOURCE_ID"]))

    def test_segunda_corrida_nao_muda_nada(self):
        uma, _ = AL.alinhar(_livro_antigo(), TABELA, "D44")
        duas, acoes = AL.alinhar(uma, TABELA, "D44")
        self.assertEqual(uma, duas)
        self.assertEqual(["JA_ALINHADA"], [x["ACAO"] for x in acoes])

    def test_decisao_desconhecida_nao_escreve(self):
        with self.assertRaises(SystemExit):
            AL.alinhar(_livro_antigo(), TABELA, "D99")

    def test_invariante_apanha_fonte_mudada_sem_autorizacao(self):
        antes = _livro_antigo()
        depois = copy.deepcopy(antes)
        depois["FONTES"][0]["NAME"] = "outro nome"
        with self.assertRaises(AL.InvarianteQuebrado):
            AL.invariantes(antes, depois, {ISTAT})

    def test_sem_escrever_o_ficheiro_nao_muda(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "livro.json"
            p.write_text(json.dumps(_livro_antigo(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            antes = p.read_bytes()
            self.assertEqual(0, AL.main(["--decisao", "D44", "--livro", str(p)]))
            self.assertEqual(antes, p.read_bytes())
            self.assertEqual(0, AL.main(["--decisao", "D44", "--livro", str(p), "--escrever"]))
            self.assertEqual(NOVO, _c(json.loads(p.read_text(encoding="utf-8")), ISTAT)["ACQUISITION"]["LINK_PATTERN"])


if __name__ == "__main__":
    unittest.main()
