# -*- coding: utf-8 -*-
"""D52 · as 62 ordens de agronomos saem por decisao — so elas, com volta, e o robo deixa de as tentar.

    cd curadoria && py -m unittest test_retirar_por_decisao

Sem rede e sem livro real: um livro montado aqui com as 62 da decisao, as 10 outras fontes do dominio
conaf.it que existem no livro vivo, Palermo (fica activa) e duas de fora.
"""
import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import retirar_por_decisao as R   # noqa: E402
import gatilho_discovery as G     # noqa: E402
import alimentar_fila as AF       # noqa: E402

DEC = R.ler_decisao("D52")
AS_62 = [f["SOURCE_ID"] for f in DEC["FONTES"]]
OUTRAS_CONAF = ["IT-T7-170", "IT-T7-173", "IT-T7-174", "IT-T7-175", "IT-T7-180", "IT-T7-182",
                "IT-T7-185", "IT-T7-194", "IT-T7-203", "IT-T7-219"]
FORA = ["IT-T7-226", "IT-T10-018", "IT-T2-051"]
AGORA = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)


def _contrato(sid):
    return {"SOURCE_ID": sid, "TERRITORY": "T7", "ACQUISITION": {
        "STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL", "INDEX_URL": "https://%s.exemplo.it/" % sid.lower(),
        "LINK_PATTERN": "^x$", "MAX_TARGETS": 1}}


def _livro():
    return {"DATASET": "SOURCE-CURATOR-CONTRACTS-V1", "TOTAL": 75,
            "FONTES": [_contrato(s) for s in AS_62 + OUTRAS_CONAF + FORA]}


class TestD52(unittest.TestCase):
    def test_a_decisao_tem_62_cada_uma_com_a_sua_prova(self):
        self.assertEqual(62, len(AS_62))
        self.assertEqual(62, len(set(AS_62)))
        self.assertTrue(all(f["PROVA"].get("EVIDENCE_REF", "").startswith("EV-" + f["SOURCE_ID"]) for f in DEC["FONTES"]))
        self.assertNotIn("IT-T7-226", AS_62, "Palermo fica activa")
        self.assertFalse(set(OUTRAS_CONAF) & set(AS_62))

    def test_so_as_62_mudam_e_so_na_marca(self):
        antes = _livro()
        depois, acoes = R.aplicar(antes, DEC, quando="2026-09-26T00:00:00+00:00")
        mudaram = [a["SOURCE_ID"] for a, b in zip(antes["FONTES"], depois["FONTES"]) if a != b]
        self.assertEqual(sorted(AS_62), sorted(mudaram))
        for a, b in zip(antes["FONTES"], depois["FONTES"]):
            if a["SOURCE_ID"] in AS_62:
                self.assertEqual(R.RETIRADA, b["ESTADO_CATALOGO"])
                self.assertEqual("D52", b["CATALOGO_D9"]["DECISAO"])
                self.assertTrue(b["CATALOGO_D9"]["REVERSIVEL"])
                self.assertEqual({k: v for k, v in b.items() if k not in R.CHAVES}, a)
        self.assertEqual(62, sum(1 for x in acoes if x["ACAO"] == "APLICA"))

    def test_nenhuma_outra_fonte_do_conaf_muda(self):
        antes = _livro()
        depois, _ = R.aplicar(antes, DEC)
        d = {c["SOURCE_ID"]: c for c in depois["FONTES"]}
        a = {c["SOURCE_ID"]: c for c in antes["FONTES"]}
        for s in OUTRAS_CONAF + FORA:
            self.assertEqual(a[s], d[s], s)

    def test_segunda_corrida_nao_muda_nada(self):
        uma, _ = R.aplicar(_livro(), DEC)
        duas, acoes = R.aplicar(uma, DEC)
        self.assertEqual(uma, duas)
        self.assertEqual({"JA_APLICADA"}, {x["ACAO"] for x in acoes})

    def test_reverter_devolve_o_livro_byte_a_byte(self):
        antes = _livro()
        marcado, _ = R.aplicar(antes, DEC)
        de_volta, acoes = R.reverter(marcado, DEC)
        self.assertEqual(json.dumps(antes, ensure_ascii=False, indent=1), json.dumps(de_volta, ensure_ascii=False, indent=1))
        self.assertEqual(62, sum(1 for x in acoes if x["ACAO"] == "REVERTE"))

    def test_outra_marca_nao_e_pisada_nem_revertida(self):
        antes = _livro()
        antes["FONTES"][0]["ESTADO_CATALOGO"] = R.RETIRADA
        antes["FONTES"][0]["CATALOGO_D9"] = {"DECISAO": "D9", "PORQUE": "outra decisao"}
        depois, acoes = R.aplicar(antes, DEC)
        self.assertEqual(antes["FONTES"][0], depois["FONTES"][0])
        self.assertIn("SALTA", {x["ACAO"] for x in acoes if x["SOURCE_ID"] == AS_62[0]})
        volta, _ = R.reverter(depois, DEC)
        self.assertEqual("D9", volta["FONTES"][0]["CATALOGO_D9"]["DECISAO"], "reverter a D52 nao tira a D9")

    def test_invariante_apanha_mudanca_fora_da_marca(self):
        antes = _livro()
        depois = copy.deepcopy(antes)
        depois["FONTES"][0]["TERRITORY"] = "T1"
        with self.assertRaises(R.InvarianteQuebrado):
            R.invariantes(antes, depois, {AS_62[0]})
        with self.assertRaises(R.InvarianteQuebrado):
            R.invariantes(antes, depois, set())

    def test_o_gatilho_deixa_de_as_tentar(self):
        velho = (AGORA - timedelta(days=3)).isoformat()
        estados = {s: "CONTRACTED_CANARY_FAILED" for s in AS_62 + OUTRAS_CONAF + FORA}
        tarefas = [{"SOURCE_ID": s, "TASK_TYPE": "REPAIR_CONTRACT", "STATUS": "FAILED", "UPDATED_AT": velho}
                   for s in estados]
        antes = {c["SOURCE_ID"]: c for c in _livro()["FONTES"]}
        c0 = {x["SOURCE_ID"] for x in G.candidatas_a_reparar(AGORA, estados=estados, contratos=antes, tarefas=tarefas)}
        self.assertTrue(set(AS_62) <= c0, "sem a marca, o gatilho tentaria as 62")
        depois = {c["SOURCE_ID"]: c for c in R.aplicar(_livro(), DEC)[0]["FONTES"]}
        c1 = {x["SOURCE_ID"] for x in G.candidatas_a_reparar(AGORA, estados=estados, contratos=depois, tarefas=tarefas)}
        self.assertFalse(set(AS_62) & c1)
        self.assertEqual(c0 - set(AS_62), c1, "as outras continuam a ser tentadas")

    def test_alimentar_a_mao_tambem_as_salta_e_nao_lhes_escreve_contrato_novo(self):
        feitos = []
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "livro.json"
            p.write_text(json.dumps(R.aplicar(_livro(), DEC)[0]), encoding="utf-8")
            estados = {s: "CONTRACTED_CANARY_FAILED" for s in AS_62 + OUTRAS_CONAF}
            estados[AS_62[1]] = "DEGRADED"
            with mock.patch.object(AF, "CONTRATOS", p), mock.patch.object(AF, "ALLOC", Path(d) / "nao"), \
                    mock.patch.object(AF, "CARACT", Path(d) / "nao"), \
                    mock.patch.object(AF.LC, "snapshot", lambda: estados), \
                    mock.patch.object(AF.F, "enfileirar", lambda sid, tipo, **k: feitos.append((sid, tipo))), \
                    mock.patch.object(AF.F, "metricas", lambda: {}):
                AF.main()
        tocadas = {s for s, _ in feitos}
        self.assertFalse(tocadas & set(AS_62), feitos)
        self.assertEqual(set(OUTRAS_CONAF), tocadas)


if __name__ == "__main__":
    unittest.main()
