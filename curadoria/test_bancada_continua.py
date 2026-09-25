#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A bancada continua (preparar · extra · ingerir) — tudo em pasta descartavel, transporte falso:
nada sai a rede. As travas: teto por anfitriao, robots, portao de egresso; so entra resposta que
cite paginas DO LOTE (URL + sha256 que o robo buscou)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import bancada_continua as BC   # noqa: E402
import bancada_ia as BIA        # noqa: E402

PAG = b"<html><body><a href='/bollettini/1'>1</a></body></html>"


class RobotsFalso:
    def __init__(self, proibe=()):
        self.proibe = proibe


def transporte(pedidos, *, egresso=True, proibe=()):
    def buscar(u):
        pedidos.append(u)
        return 200, PAG, None
    tr = BC.Transporte(buscar=buscar, robots=lambda h: RobotsFalso(proibe), egresso=lambda: egresso,
                       dormir=lambda s: None)
    tr._permitido = lambda url, rp: not any(p in url for p in rp.proibe)
    return tr


def fila(*casos):
    return {"CASOS": [dict({"PERGUNTA": "RECEITA", "JANELA_D29": False, "GATILHO": "REPARO_RECUSADO: X",
                            "ENTRADA": "https://%s.example/" % c.lower()}, CASO=c, **kw) for c, kw in casos]}


class OTransporte(unittest.TestCase):

    def test_teto_por_anfitriao(self):
        pedidos = []
        tr = transporte(pedidos)
        with tempfile.TemporaryDirectory() as d:
            estados = [tr.pegar("https://um.example/p%d" % i, Path(d))["ESTADO"] for i in range(7)]
        self.assertEqual(["LIDO"] * BC.MAX_POR_ANFITRIAO + ["TETO_POR_ANFITRIAO"] * 2, estados)
        self.assertEqual(BC.MAX_POR_ANFITRIAO, len(pedidos))

    def test_robots_proibe_nao_vai_a_rede(self):
        pedidos = []
        tr = transporte(pedidos, proibe=("/privado",))
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual("ROBOTS_PROIBE", tr.pegar("https://um.example/privado/x", Path(d))["ESTADO"])
        self.assertEqual([], pedidos)

    def test_sem_egresso_para(self):
        tr = transporte([], egresso=False)
        with tempfile.TemporaryDirectory() as d, self.assertRaises(SystemExit):
            tr.pegar("https://um.example/", Path(d))

    def test_bytes_guardados_com_sha(self):
        tr = transporte([])
        with tempfile.TemporaryDirectory() as d:
            l = tr.pegar("https://um.example/", Path(d))
            self.assertEqual(PAG, Path(l["BYTES_EM"]).read_bytes())
            import hashlib
            self.assertEqual(hashlib.sha256(PAG).hexdigest(), l["SHA256"])


class PrepararEExtra(unittest.TestCase):

    def test_so_janela_e_no_maximo_duas_paginas(self):
        with tempfile.TemporaryDirectory() as d:
            f = fila(("IT-T3-001", {"JANELA_D29": True}), ("IT-T7-001", {}), ("IT-T2-001", {"JANELA_D29": True}))
            p = BC.preparar(10, so_janela=True, pasta=Path(d), transporte=transporte([]), fila=f)
            lote = json.loads(p.read_text(encoding="utf-8"))
            self.assertEqual(["IT-T3-001", "IT-T2-001"], [c["CASO"] for c in lote["CASOS"]])
            self.assertTrue(all(len(c["PAGINAS"]) <= BC.MAX_POR_CASO_PREPARAR for c in lote["CASOS"]))

    def test_extra_tem_teto_por_caso(self):
        with tempfile.TemporaryDirectory() as d:
            p = BC.preparar(1, pasta=Path(d), transporte=transporte([]), fila=fila(("IT-T3-001", {})))
            pedidos = []
            lote = BC.extra(p, {"IT-T3-001": ["https://a.example/%d" % i for i in range(4)]},
                            transporte=transporte(pedidos))
            extras = [x for x in lote["CASOS"][0]["PAGINAS"] if x["PAPEL"] == "EXTRA"]
            self.assertEqual(["LIDO", "LIDO", "TETO_DE_EXTRAS", "TETO_DE_EXTRAS"], [x["ESTADO"] for x in extras])
            self.assertEqual(2, len(pedidos))


class Ingerir(unittest.TestCase):

    def _lote(self, d):
        return BC.preparar(1, pasta=Path(d), transporte=transporte([]), fila=fila(("IT-T3-001", {})))

    def test_so_entra_resposta_que_cita_paginas_do_lote(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._lote(d)
            props = Path(d) / "P.json"
            entrada = json.loads(p.read_text(encoding="utf-8"))["CASOS"][0]["PAGINAS"][0]["URL"]
            out = BC.ingerir(p, [
                {"CASO": "IT-T3-001", "RESPOSTA": "RECEITA", "PAGINAS_LIDAS": [entrada], "PORQUE": "12 boletins",
                 "INDEX_URL": entrada, "LINK_PATTERN": r"^https://it-t3-001\.example/bollettini/\d+$"},
                {"CASO": "IT-T3-001", "RESPOSTA": "SEM_RECEITA", "PAGINAS_LIDAS": ["https://outra.example/"],
                 "PORQUE": "x"},
                {"CASO": "IT-T9-999", "RESPOSTA": "SEM_RECEITA", "PAGINAS_LIDAS": [entrada], "PORQUE": "x"},
                {"CASO": "IT-T3-001", "RESPOSTA": "TALVEZ", "PAGINAS_LIDAS": [entrada], "PORQUE": "x"},
            ], propostas=props)
            self.assertEqual([{"CASO": "IT-T3-001", "RESPOSTA": "RECEITA"}], out["ENTROU"])
            self.assertEqual(3, len(out["RECUSOU"]))
            p0 = json.loads(props.read_text(encoding="utf-8"))["PROPOSTAS"][0]
            self.assertEqual(64, len(p0["PAGINAS_LIDAS"][0]["SHA256"]))
            self.assertIsNotNone(BIA.proposta_pendente("IT-T3-001", {}, caminho=props))

    def test_receita_que_a_porta_recusa_nao_entra(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._lote(d)
            entrada = json.loads(p.read_text(encoding="utf-8"))["CASOS"][0]["PAGINAS"][0]["URL"]
            out = BC.ingerir(p, [{"CASO": "IT-T3-001", "RESPOSTA": "RECEITA", "PAGINAS_LIDAS": [entrada],
                                  "PORQUE": "x", "INDEX_URL": entrada, "LINK_PATTERN": r"^https://.*$"}],
                             propostas=Path(d) / "P.json")
            self.assertEqual([], out["ENTROU"])
            self.assertIn("propria INDEX_URL", out["RECUSOU"][0]["PORQUE"])


if __name__ == "__main__":
    unittest.main()
