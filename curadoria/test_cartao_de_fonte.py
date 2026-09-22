#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Os 10 testes do cartao da fonte (missao TELEMETRIA-V1, Parte B). Sintetico."""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import lifecycle as LC
import telemetria as T
import cartao_de_fonte as C

AGORA = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)


def _tr(sid, novo, quando, ev=None, reason=""):
    return {"SOURCE_ID": sid, "PREVIOUS_STATE": None, "NEW_STATE": novo,
            "REASON": reason, "EVIDENCE_REF": ev, "OBSERVED_AT": quando.isoformat(),
            "OWNER": "SOURCE_CURATOR", "VERSION": "v1"}


class TestCartao(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cartao-test-"))
        self._orig = {"T_LEDGER": T.LEDGER, "ALLOC": C.ALLOC, "CARACT": C.CARACT,
                      "CONTRATOS": C.CONTRATOS, "CARDS": C.CARDS}
        T.LEDGER = self.tmp / "ledger.json"
        C.ALLOC = self.tmp / "alloc.json"
        C.CARACT = self.tmp / "caract.json"
        C.CONTRATOS = self.tmp / "contratos.json"
        C.CARDS = self.tmp / "cards.json"
        self._alloc([]); self._caract([]); self._contratos([])

    def tearDown(self):
        T.LEDGER = self._orig["T_LEDGER"]
        C.ALLOC = self._orig["ALLOC"]; C.CARACT = self._orig["CARACT"]
        C.CONTRATOS = self._orig["CONTRATOS"]; C.CARDS = self._orig["CARDS"]

    def _ledger(self, tr):
        T.LEDGER.write_text(json.dumps({"TRANSICOES": tr}, ensure_ascii=False), encoding="utf-8")

    def _alloc(self, novas):
        C.ALLOC.write_text(json.dumps({"NOVAS": novas}, ensure_ascii=False), encoding="utf-8")

    def _caract(self, fontes):
        C.CARACT.write_text(json.dumps({"FONTES": fontes}, ensure_ascii=False), encoding="utf-8")

    def _contratos(self, fontes):
        C.CONTRATOS.write_text(json.dumps({"FONTES": fontes}, ensure_ascii=False), encoding="utf-8")

    def _fonte_rica(self, cand="CAND-1", sid="IT-T3-100"):
        self._alloc([{"CANDIDATE_ID": cand, "SOURCE_ID": sid, "NOME": "Consorzio X",
                      "URL": "https://x.it", "TERRITORY": "T3", "FAMILY": "HTML_SITE"}])
        self._caract([{"CANDIDATE_ID": cand, "NOME": "Consorzio X", "URL": "https://x.it",
                       "FAMILY": "HTML_SITE", "CONTENT_TYPES": ["bollettino"],
                       "TOPICS_OBSERVED": ["PHYTOSANITARY"], "GEOGRAPHIES_OBSERVED": ["veneto"],
                       "CROPS_OBSERVED": ["vite"], "SOURCE_PATTERN_STABLE": True,
                       "WHY_RELEVANT": "boletim fitossanitario regional",
                       "CANONICAL_EXAMPLE": "data/samples/x.html",
                       "UPDATE_PATTERN": "WEEKLY"}])

    # 1
    def test_candidate_nao_aparece_como_aprovada(self):
        self._ledger([_tr("CAND-9", "SEMANTIC_REVIEW", AGORA)])  # nao-READY
        s = C.gerar(AGORA)
        self.assertNotIn("CAND-9", s["CARDS"])
        self.assertEqual(s["TOTAL"], 0)

    # 2
    def test_ready_current_aparece(self):
        self._fonte_rica()
        self._ledger([_tr("IT-T3-100", LC.READY_FOR_COLLECTION, AGORA, ev="EV-x-CANARY-1")])
        s = C.gerar(AGORA)
        self.assertIn("IT-T3-100", s["CARDS"])

    # 3
    def test_resumo_aponta_para_evidencia_real(self):
        self._fonte_rica()
        self._ledger([_tr("IT-T3-100", LC.READY_FOR_COLLECTION, AGORA, ev="EV-x-CANARY-1")])
        c = C.gerar(AGORA)["CARDS"]["IT-T3-100"]
        self.assertEqual(c["SUMMARY_EVIDENCE"], "data/samples/x.html")
        self.assertIn("PHYTOSANITARY", c["SOURCE_SUMMARY"] + " " + " ".join(c["EXPECTED_CONTENT"]) + str(c["KNOWN_COVERAGE"]))

    # 4
    def test_ausencia_gera_unknown_nao_invencao(self):
        # READY sem caracterizacao nem alloc -> resumo insuficiente, campos UNKNOWN
        self._ledger([_tr("IT-T9-200", LC.READY_FOR_COLLECTION, AGORA, ev="EV-y-CANARY-1")])
        c = C.gerar(AGORA)["CARDS"]["IT-T9-200"]
        self.assertEqual(c["SOURCE_SUMMARY"], "Fonte admitida, mas descricao editorial ainda insuficiente.")
        self.assertEqual(c["SINTONIA_RELEVANCE"], "UNKNOWN")
        self.assertEqual(c["SUMMARY_CONFIDENCE"], "LOW")

    # 5
    def test_resumo_nao_regenera_sem_mudanca(self):
        self._fonte_rica()
        self._ledger([_tr("IT-T3-100", LC.READY_FOR_COLLECTION, AGORA, ev="EV-x-CANARY-1")])
        C.escrever(C.gerar(AGORA - timedelta(hours=2)))
        c1 = json.load(open(C.CARDS, encoding="utf-8"))["CARDS"]["IT-T3-100"]
        # segunda geracao, evidencia igual -> SUMMARY_CREATED_AT preservado
        s2 = C.gerar(AGORA)
        c2 = s2["CARDS"]["IT-T3-100"]
        self.assertEqual(c1["SUMMARY_CREATED_AT"], c2["SUMMARY_CREATED_AT"])
        self.assertEqual(c1["SUMMARY_EVIDENCE_HASH"], c2["SUMMARY_EVIDENCE_HASH"])

    # 6
    def test_mesma_fonte_nao_cria_dois_cartoes(self):
        self._fonte_rica()
        self._ledger([_tr("IT-T3-100", LC.READY_FOR_COLLECTION, AGORA - timedelta(hours=1), ev="EV-x-CANARY-1"),
                      _tr("IT-T3-100", LC.READY_FOR_COLLECTION, AGORA, ev="EV-x-CANARY-2")])
        s = C.gerar(AGORA)
        self.assertEqual(len([k for k in s["CARDS"] if k == "IT-T3-100"]), 1)
        self.assertEqual(s["TOTAL"], 1)

    # 7
    def test_ready_current_24h_navega_ate_as_fontes(self):
        self._fonte_rica()
        tr = [_tr("IT-T3-100", LC.READY_FOR_COLLECTION, AGORA - timedelta(hours=2), ev="EV-x-CANARY-1")]
        self._ledger(tr)
        C.escrever(C.gerar(AGORA))
        janela = T.ready_sources_janela(tr, AGORA - timedelta(hours=24), AGORA)
        nav = C.cartoes_navegaveis([r["SOURCE_ID"] for r in janela])
        self.assertEqual(len(nav), 1)
        self.assertEqual(nav[0]["SOURCE_NAME"], "Consorzio X")
        self.assertTrue(nav[0]["READY_AT"])

    # 8
    def test_fonte_reclassificada_nao_e_ready_atual(self):
        self._fonte_rica()
        self._ledger([_tr("IT-T3-100", LC.READY_FOR_COLLECTION, AGORA - timedelta(hours=1), ev="EV-x-CANARY-1"),
                      _tr("IT-T3-100", LC.RETRY_AFTER, AGORA)])  # ultima transicao = RETRY
        s = C.gerar(AGORA)
        self.assertNotIn("IT-T3-100", s["CARDS"], "estado atual e RETRY, nao READY")

    # 9
    def test_confidence_segue_criterios(self):
        # HIGH: conteudo + cobertura + estavel
        self._fonte_rica()
        self._ledger([_tr("IT-T3-100", LC.READY_FOR_COLLECTION, AGORA, ev="EV-x-CANARY-1")])
        self.assertEqual(C.gerar(AGORA)["CARDS"]["IT-T3-100"]["SUMMARY_CONFIDENCE"], "HIGH")
        # MEDIUM: conteudo sem cobertura
        self._caract([{"CANDIDATE_ID": "CAND-1", "NOME": "Consorzio X", "URL": "https://x.it",
                       "FAMILY": "HTML_SITE", "CONTENT_TYPES": ["nota"],
                       "TOPICS_OBSERVED": ["SCIENCE"], "GEOGRAPHIES_OBSERVED": [],
                       "CROPS_OBSERVED": [], "SOURCE_PATTERN_STABLE": True}])
        self.assertEqual(C.gerar(AGORA)["CARDS"]["IT-T3-100"]["SUMMARY_CONFIDENCE"], "MEDIUM")

    # 10
    def test_reinicio_nao_perde_resumos(self):
        self._fonte_rica()
        self._ledger([_tr("IT-T3-100", LC.READY_FOR_COLLECTION, AGORA, ev="EV-x-CANARY-1")])
        C.escrever(C.gerar(AGORA))
        # "reiniciar" = reler o ficheiro do disco
        d = json.load(open(C.CARDS, encoding="utf-8"))
        self.assertIn("IT-T3-100", d["CARDS"])
        self.assertEqual(d["CARDS"]["IT-T3-100"]["SOURCE_NAME"], "Consorzio X")


if __name__ == "__main__":
    unittest.main(verbosity=2)
