# -*- coding: utf-8 -*-
"""CANAIS-PESQUISA · os canais YouTube PRESOS na rota antiga de feed tambem vao pelo bloco 4.

Medido no vivo 83de0ccd (26/09 04:06): 9 canais com contrato `YOUTUBE_CHANNEL_FEED` em
RETRY_AFTER (7 de pesquisa: IT-T5-042..050) ficavam fora do plano da LEGACY-99 v5, que so
olha as READY_LEGACY. A troca e a MESMA (bloco 4); so o criterio de entrada muda, e o
`remedir` deles e proprio (o de `ready_split` so age em READY).

Sem rede e sem livros reais: livro de estados e fila sao dublos.
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "tests"))
import importar_do_coletor as I   # noqa: E402
import collection_gate as CG      # noqa: E402
import ready_split as RS          # noqa: E402
import lifecycle as LC            # noqa: E402
import fila as F                  # noqa: E402
from test_youtube_pelo_scrap import feed, C1, C2  # noqa: E402

C3 = "UCtestelegacy99v4ccccccc"


def ctx(estados, contratos):
    return {"livro": {"TRANSICOES": [{"SOURCE_ID": s, "NEW_STATE": e} for s, e in estados.items()]},
            "contratos": contratos}


class PresosNoFeed(unittest.TestCase):
    def test_retry_no_feed_entra_no_plano_os_outros_estados_nao(self):
        c = ctx({"IT-T5-045": "RETRY_AFTER", "IT-T5-046": "REJECTED", "IT-T5-049": "RETRY_AFTER"},
                {"IT-T5-045": feed("IT-T5-045", C1), "IT-T5-046": feed("IT-T5-046", C2),
                 "IT-T5-049": dict(feed("IT-T5-049", C3), ACQUISITION={"STRATEGY": "SCRAP_FASE"})})
        with mock.patch.object(CG, "avaliar", return_value={"MOTIVO": "OUTRO"}):
            p = I.planear(ctx=c, tabela={})
        self.assertEqual([(x["SOURCE_ID"], x["CASO"]) for x in p["PELO_SCRAP"]],
                         [("IT-T5-045", "PRESO_NO_FEED")])

    def test_o_remedir_dos_presos_poe_canary_pending_e_valida_a_rota(self):
        est = {"IT-T5-045": LC.RETRY_AFTER, "IT-T5-050": LC.READY_FOR_COLLECTION}
        reg, fila = [], []
        with mock.patch.object(LC, "estado_de", side_effect=lambda s: est[s]), \
             mock.patch.object(LC, "registar", side_effect=lambda s, e, m, **k: reg.append((s, e))), \
             mock.patch.object(F, "enfileirar", side_effect=lambda s, t, **k: fila.append((s, t)) or {"TASK_ID": "T1"}):
            r = I.remedir_presos(["IT-T5-045", "IT-T5-050"], motivo="teste")
        self.assertEqual(reg, [("IT-T5-045", LC.CANARY_PENDING)])
        self.assertEqual(fila, [("IT-T5-045", F.VALIDATE_ROUTE)])
        self.assertEqual([x["FEITO"] for x in r], [True, False])      # o READY nao e dele

    def test_pelo_scrap_manda_cada_um_ao_seu_remedir(self):
        plano = {"IMPORTA": [], "FICA": [], "PELO_SCRAP": [
            {"SOURCE_ID": "IT-T10-017"}, {"SOURCE_ID": "IT-T5-045", "CASO": "PRESO_NO_FEED"}]}

        class B4:
            @staticmethod
            def rota_do_scrap(nl, nt, ta, dec):
                return [], {"IT-T10-017", "IT-T5-045"}

            @staticmethod
            def invariantes(*a, **k):
                return None
        livro = {"FONTES": [feed("IT-T10-017", C1), feed("IT-T5-045", C2)]}
        with mock.patch.object(I, "planear", return_value=plano), \
             mock.patch.object(I, "CURATOR") as cur, mock.patch.object(I, "TABELA") as tab, \
             mock.patch.object(RS, "remedir", return_value=[{"FEITO": True}]) as rm, \
             mock.patch.object(I, "remedir_presos", return_value=[{"FEITO": True}]) as rp:
            import json
            cur.read_text.return_value = json.dumps(livro)
            tab.read_text.return_value = json.dumps({"FONTES": []})
            cur.with_name.return_value = mock.MagicMock()
            tab.with_name.return_value = mock.MagicMock()
            r = I.pelo_scrap(["IT-T10-017", "IT-T5-045"], bloco4=B4)
        self.assertEqual(rm.call_args[0][0], ["IT-T10-017"])
        self.assertEqual(rp.call_args[0][0], ["IT-T5-045"])
        self.assertEqual(r["REMEDIDAS"], 2)


if __name__ == "__main__":
    unittest.main()
