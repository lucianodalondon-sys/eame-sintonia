#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEDE-37-PREP · a MICRO-SEDE: plano sem rede e corrida com rede SIMULADA (nada sai desta máquina).

Prova: sem portão IT não há pedido; nunca > 5 por domínio; robots manda; a mesma página pede-se uma vez;
quem já tem sede não entra; a corrida só propõe (não recebe contratos, não os escreve)."""
from __future__ import annotations

import hashlib
import inspect
import os
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "ferramentas", "sede37"))
import micro_sede as M  # noqa: E402

NS = {"SOURCE_LOCATION": "NAO SEI"}


def _f(sid, dom, url, hoje="NAO_SEI", sem_rede=NS):
    return {"SOURCE_ID": sid, "DOMINIO": dom, "SEDE_HOJE": hoje, "SEDE_SEM_REDE": dict(sem_rede),
            "CLASSE": "CONTATTI" if url else None, "PAGINA_DE_SEDE_PROVAVEL": url}


PAGINAS = {"FONTES": [
    _f("IT-A-1", "cia.it", "https://www.cia.it/chi-siamo/contatti/"),
    _f("IT-A-2", "cia.it", "https://cia.it/chi-siamo/contatti/"),                    # a mesma, sem www
    _f("IT-B-1", "x.it", "https://x.it/contatti"),
    _f("IT-C-1", "y.it", "https://y.it/contatti", hoje="PAGINA_PROPRIA"),            # ja provada
    _f("IT-D-1", "z.it", "https://z.it/contatti", sem_rede={"SOURCE_LOCATION": "Roma"}),  # provada sem rede
    _f("IT-E-1", "w.it", None),                                                      # sem pagina: NAO SEI
] + [_f("IT-G-%d" % i, "grande.it", "https://grande.it/p%d/contatti" % i) for i in range(6)]}
RODAPE = b"<footer>Sede legale Via Nizza 154 00198 Roma Contatti</footer>"


class Plano(unittest.TestCase):
    def setUp(self):
        self.p = M.plano(PAGINAS)

    def test_so_entra_quem_ainda_precisa(self):
        todas = [s for d in self.p["POR_DOMINIO"].values() for s in d["FONTES"]]
        self.assertNotIn("IT-C-1", todas)
        self.assertNotIn("IT-D-1", todas)
        self.assertEqual(["IT-E-1"], self.p["SEM_PAGINA_DE_SEDE_NAO_SEI"])

    def test_a_mesma_pagina_com_e_sem_www_pede_se_uma_vez(self):
        self.assertEqual(1, self.p["POR_DOMINIO"]["cia.it"]["PAGINAS_DISTINTAS"])
        self.assertEqual(2, self.p["POR_DOMINIO"]["cia.it"]["PEDIDOS_PREVISTOS"])

    def test_nenhuma_ronda_passa_de_5_por_dominio(self):
        for itens in self.p["RONDAS"].values():
            for i in itens:
                self.assertLessEqual(i["PEDIDOS"], 5)
        self.assertEqual(2, self.p["POR_DOMINIO"]["grande.it"]["RONDAS"])


class Corrida(unittest.TestCase):
    def setUp(self):
        self.p = M.plano(PAGINAS)
        self.pedidos = []
        self.saida = tempfile.mkdtemp()

    def _buscar(self, u):
        self.pedidos.append(u)
        return 200, RODAPE, ""

    def _correr(self, portao=lambda: True, permitido=lambda u, rp: True, ronda=1):
        return M.correr(self.p, ronda, self.saida, buscar=self._buscar, robots_de=lambda h: ("rp", "lido"),
                        permitido=permitido, portao=portao, pausa=0)

    def test_sem_portao_it_nao_ha_um_so_pedido(self):
        r = self._correr(portao=lambda: False)
        self.assertFalse(r["CORREU"])
        self.assertEqual([], self.pedidos)

    def test_nunca_passa_de_5_por_dominio(self):
        r = self._correr()
        self.assertLessEqual(r["MAXIMO_POR_DOMINIO"], 5)

    def test_robots_manda(self):
        r = self._correr(permitido=lambda u, rp: "x.it" not in u)
        self.assertNotIn("https://x.it/contatti", self.pedidos)
        self.assertIn("ROBOTS_PROIBE", {p["RESULTADO"] for p in r["PAGINAS"]})

    def test_guarda_os_bytes_com_sha_e_so_propoe(self):
        r = self._correr()
        ok = [p for p in r["PAGINAS"] if p["RESULTADO"] == "OK"]
        self.assertTrue(ok)
        sha = hashlib.sha256(RODAPE).hexdigest()
        self.assertTrue(os.path.exists(os.path.join(self.saida, sha + ".html")))
        self.assertEqual("Roma", ok[0]["SEDE_PROPOSTA"]["SOURCE_LOCATION"])
        self.assertNotIn("contratos", inspect.signature(M.correr).parameters)


if __name__ == "__main__":
    unittest.main()
