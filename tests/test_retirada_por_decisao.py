"""RETIRADA_POR_DECISAO (D9) — o portao e o coletor recusam, com o motivo escrito.

O pacote G1 (scripts/desbloqueio/aplicar_desbloqueio.py) marca
`ESTADO_CATALOGO = RETIRADA_POR_DECISAO` no livro de contratos do Curator e na
tabela do coletor. Medido pela G1 (8946d898): nenhum dos dois lia a marca — uma
fonte retirada que estivesse na tabela continuaria a ser colhida.

Dois lados, os dois exercitados pelo codigo real:
  1. o portao da Collection (curadoria/collection_gate.py), com livro, provas e
     contratos sinteticos: uma fonte READY_CURRENT e elegivel; a MESMA fonte com a
     marca e recusada com MOTIVO = RETIRADA_POR_DECISAO;
  2. o coletor (regras/italy_contracts.mjs) numa COPIA de regras/ em pasta
     descartavel, com uma linha retirada na tabela: essa fonte nao tem contrato e
     aparece em RETIRADAS_POR_DECISAO. A tabela real nunca e tocada.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import collection_gate as CG   # noqa: E402
import lifecycle as LC         # noqa: E402
import ready_split as RS       # noqa: E402

SID = "IT-T7-901"
REF = "EV-IT-T7-901-CANARY-0001"
T0 = "2026-09-23T10:00:00+00:00"


def _livro():
    return {"TRANSICOES": [
        {"SOURCE_ID": SID, "PREVIOUS_STATE": None, "NEW_STATE": LC.CANARY_PENDING,
         "REASON": "x", "EVIDENCE_REF": None, "OBSERVED_AT": T0, "OWNER": LC.OWNER_CURATOR},
        {"SOURCE_ID": SID, "PREVIOUS_STATE": LC.CANARY_PENDING, "NEW_STATE": LC.READY_FOR_COLLECTION,
         "REASON": "canario resolveu", "EVIDENCE_REF": REF, "OBSERVED_AT": T0,
         "OWNER": LC.OWNER_CURATOR}]}


def _provas():
    return {REF: {"EVIDENCE_REF": REF, "SOURCE_ID": SID, "DADOS": {
        "PASS": True, "DETAIL_GATE_PASSED": True, "DETAIL_ENUMERATED": 12,
        "ITEM_ABERTO": {"URL": "https://ex.it/news/mosca-olivo-calo-termico-2026/", "HTTP": 200,
                        "HTML_KIND": "CONTENT", "CAPA_OU_MATERIA": RS.MATERIA,
                        "PARAGRAPH_CHARACTERS": 3000}}}}


def _contratos(retirada: bool):
    c = {"SOURCE_ID": SID, "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY",
                                           "INDEX_URL": "https://ex.it/news/"}}
    if retirada:
        c["ESTADO_CATALOGO"] = "RETIRADA_POR_DECISAO"
        c["CATALOGO_D9"] = {"DECISAO": "D9", "PORQUE": "fora do universo SINTONIA",
                            "REVERSIVEL": True}
    return {SID: c}


class OPortaoRecusaARetirada(unittest.TestCase):

    def test_sem_marca_a_mesma_fonte_e_elegivel(self):
        v = CG.avaliar(SID, livro=_livro(), evidencias=_provas(), contratos=_contratos(False))
        self.assertTrue(v["COLLECTION_ELIGIBLE"], v)

    def test_com_marca_e_recusada_com_motivo_explicito(self):
        v = CG.avaliar(SID, livro=_livro(), evidencias=_provas(), contratos=_contratos(True))
        self.assertFalse(v["COLLECTION_ELIGIBLE"], v)
        self.assertEqual(v["MOTIVO"], "RETIRADA_POR_DECISAO")
        self.assertIn("D9", v["PORQUE"])
        self.assertFalse(CG.eligible_for_collection(
            SID, livro=_livro(), evidencias=_provas(), contratos=_contratos(True)))


class OColetorRecusaARetirada(unittest.TestCase):

    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node ausente")
        self.tmp = tempfile.TemporaryDirectory()
        self.regras = Path(self.tmp.name) / "regras"
        shutil.copytree(RAIZ / "regras", self.regras)

    def tearDown(self):
        self.tmp.cleanup()

    def _carregar(self, linha_extra: dict | None) -> dict:
        tab = self.regras / "italy_contracts_onboarded.json"
        d = json.loads(tab.read_text(encoding="utf-8"))
        alvo = d["FONTES"][0]["SOURCE_ID"]
        if linha_extra is not None:
            d["FONTES"][0] = dict(d["FONTES"][0], **linha_extra)
        tab.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        js = ("import(%r).then(m => console.log(JSON.stringify({c: Object.keys(m.CONTRACTS), "
              "r: m.RETIRADAS_POR_DECISAO || null, o: m.ONBOARDED_IDS})))"
              % (self.regras / "italy_contracts.mjs").as_uri())
        p = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True,
                           text=True, encoding="utf-8", timeout=120)
        self.assertEqual(p.returncode, 0, p.stderr[-800:])
        return dict(json.loads(p.stdout.strip().splitlines()[-1]), alvo=alvo)

    def test_sem_marca_a_linha_vira_contrato(self):
        r = self._carregar(None)
        self.assertIn(r["alvo"], r["c"])

    def test_linha_retirada_nao_vira_contrato_e_diz_porque(self):
        r = self._carregar({"ESTADO_CATALOGO": "RETIRADA_POR_DECISAO",
                            "CATALOGO_D9": {"DECISAO": "D9", "PORQUE": "fora do universo"}})
        self.assertNotIn(r["alvo"], r["c"], "fonte retirada continua com contrato: seria colhida")
        self.assertNotIn(r["alvo"], r["o"])
        self.assertEqual((r["r"] or {}).get(r["alvo"], {}).get("MOTIVO"), "RETIRADA_POR_DECISAO")


if __name__ == "__main__":
    unittest.main()
