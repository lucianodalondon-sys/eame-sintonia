#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D32 (1): duplicados entre irmas pela IDENTIDADE DO ITEM (o corpo), nao pela morada.

Paginas no feitio medido na FederUnacoma (24/09): o mesmo corpo de noticia em tres sites, cada um
com o seu rodape. Tudo em pasta descartavel; a etapa do canario e injectada; nada sai a rede."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import fila as F                     # noqa: E402
import irmas_por_item as IPI         # noqa: E402
import lifecycle as LC               # noqa: E402
import ready_split as RS             # noqa: E402
import worker as W                   # noqa: E402
from test_worker_volta_sobrevive import _contrato  # noqa: E402

CORPO = ("Diffusi oggi da FederUnacoma i dati relativi al mercato italiano delle macchine agricole: "
         "nel 2025 le immatricolazioni di trattrici crescono del 7,4 per cento, mentre le mietitrebbie "
         "restano stabili e i rimorchi calano; la federazione attribuisce la ripresa agli incentivi.")


def pagina(site: str, corpo: str = CORPO) -> bytes:
    return ("<html><body><h1>Mercato italiano macchine agricole in ripresa nel 2025</h1>"
            "<p>%s</p><p>Torna alle News</p><p>%s e l'associazione dei costruttori italiani.</p>"
            "</body></html>" % (corpo.replace("per cento", "per&nbsp;cento"), site)).encode()


class AIdentidadeDoItem(unittest.TestCase):

    def test_mesmo_corpo_com_rodapes_diferentes_e_o_mesmo_item(self):
        ids = {IPI.identidade_do_item(pagina(s)) for s in ("Assomao", "Agridigital", "Assotrattori")}
        self.assertEqual(len(ids), 1)
        self.assertIsNotNone(ids.pop())

    def test_corpo_diferente_e_outro_item(self):
        self.assertNotEqual(IPI.identidade_do_item(pagina("Assomao")),
                            IPI.identidade_do_item(pagina("Assomao", CORPO.replace("7,4", "8,1"))))

    def test_paragrafo_curto_nao_identifica(self):
        self.assertIsNone(IPI.identidade_do_item(b"<p>Torna alle News</p><p>Contatti</p>"))
        self.assertIsNone(IPI.identidade_do_item(("<p>%s</p>" % ("x" * (IPI.MINIMO - 1))).encode()))

    def test_so_conta_irma_ready_e_nunca_eu(self):
        i = IPI.identidade_do_item(pagina("Assomao"))
        provas = [{"SOURCE_ID": "IT-T10-046", "DADOS": {"ITEM_ABERTO": {"ITEM_IDENTITY": i}}}]
        self.assertEqual(IPI.irma_que_ja_colhe(i, "IT-T10-045", provas, {"IT-T10-046"}), "IT-T10-046")
        self.assertIsNone(IPI.irma_que_ja_colhe(i, "IT-T10-045", provas, set()))          # nao READY
        self.assertIsNone(IPI.irma_que_ja_colhe(i, "IT-T10-046", provas, {"IT-T10-046"}))  # sou eu
        self.assertIsNone(IPI.irma_que_ja_colhe(None, "IT-T10-045", provas, {"IT-T10-046"}))


IRMA_READY, IRMA_NOVA, OUTRA = "IT-X-201", "IT-X-202", "IT-X-203"
ITEM = {"URL": "https://ex.it/it/news_open.php?EW_ID=14992", "HTTP": 200, "HTML_KIND": "CONTENT",
        "CAPA_OU_MATERIA": RS.MATERIA, "PARAGRAPH_CHARACTERS": 2000}


def etapa(sid, contrato):
    corpo = CORPO.replace("7,4", "9,9") if sid == OUTRA else CORPO
    return "OK", {"PASS": True, "DETAIL_GATE_PASSED": True, "DETAIL_ENUMERATED": 44,
                  "ITEM_ABERTO": dict(ITEM, ITEM_IDENTITY=IPI.identidade_do_item(pagina(sid, corpo)))}


class ATravaNaPromocao(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (LC.LIVRO, F.FILA, W.EVIDENCIA, W.CONTRATOS)
        LC.LIVRO = d / "LEDGER.json"
        F.FILA = d / "QUEUE.json"
        W.EVIDENCIA = d / "EVIDENCE.json"
        self.addCleanup(setattr, W, "PULSO", W.PULSO)
        W.PULSO = d / "WORKER-HEARTBEAT.json"
        W.CONTRATOS = d / "contracts.json"
        W.CONTRATOS.write_text(json.dumps({"FONTES": [_contrato(s) for s in (IRMA_READY, IRMA_NOVA, OUTRA)]}),
                               encoding="utf-8")
        self._etapas = mock.patch.dict(W.ETAPAS, {F.CANARY: etapa})
        self._etapas.start()

    def tearDown(self):
        self._etapas.stop()
        LC.LIVRO, F.FILA, W.EVIDENCIA, W.CONTRATOS = self._antes
        self.tmp.cleanup()

    def _canario(self, *sids):
        for sid in sids:
            LC.registar(sid, LC.CANARY_PENDING, "prova")
            F.enfileirar(sid, F.CANARY, priority=60)
        return {r["SOURCE_ID"]: r for r in W.correr(pausa=0, verboso=False)}

    def test_a_irma_que_colhe_o_mesmo_item_nao_ganha_segundo_ready(self):
        self._canario(IRMA_READY)
        self.assertEqual(LC.estado_de(IRMA_READY), LC.READY_FOR_COLLECTION)
        feitos = self._canario(IRMA_NOVA, OUTRA)
        self.assertEqual(feitos[IRMA_NOVA]["RESULTADO"], "DUPLICADA_DE_IRMA")
        self.assertEqual(LC.estado_de(IRMA_NOVA), LC.CONTRACTED_CANARY_FAILED)
        ult = LC.historia(IRMA_NOVA)[-1]
        self.assertEqual(ult["IRMA_QUE_JA_COLHE"], IRMA_READY)
        self.assertIn("DUPLICADA_DE_IRMA", ult["REASON"])
        # corpo diferente: promove como sempre
        self.assertEqual(LC.estado_de(OUTRA), LC.READY_FOR_COLLECTION)

    def test_sem_irma_ready_a_primeira_promove(self):
        self._canario(IRMA_NOVA)
        self.assertEqual(LC.estado_de(IRMA_NOVA), LC.READY_FOR_COLLECTION)


if __name__ == "__main__":
    unittest.main()
