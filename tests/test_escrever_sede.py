#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEDE-37-PREP · a porta que escreve a sede: só os campos da sede, só com prova, nunca pisa, nunca UNKNOWN."""
from __future__ import annotations

import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "ferramentas", "sede37"))
import escrever_sede as E  # noqa: E402

REGRA = "Roma (sede: Roma, CAP 00198; prova: PAGINA_GUARDADA) — fixo"


def _pag(sid, loc="Roma", base="PAGINA_GUARDADA_DA_PROPRIA_FONTE · u · sha256 x", regra=REGRA):
    return {"SOURCE_ID": sid, "SEDE_SEM_REDE": {"SOURCE_LOCATION": loc, "SOURCE_LOCATION_BASIS": base,
                                                "SOURCE_LOCATION_PRECISION": "PROVINCE", "SOURCE_LOCATION_RULE": regra}}


def _livros():
    c = {"FONTES": [{"SOURCE_ID": s, "ACQUISITION": {"INDEX_URL": "https://%s/" % s}} for s in ("IT-A", "IT-B", "IT-C", "IT-D")]}
    c["FONTES"][2]["SOURCE_LOCATION"] = "Milano"                        # IT-C ja tem sede
    t = {"FONTES": [{"SOURCE_ID": "IT-A", "ACQUISITION": {}}]}          # so IT-A esta no coletor
    return c, t


class Porta(unittest.TestCase):
    def test_so_os_campos_da_sede_e_so_com_prova(self):
        c, t = _livros()
        pag = {"FONTES": [_pag("IT-A"), _pag("IT-B"), _pag("IT-D", loc="NAO SEI", regra=None)]}
        c2, t2, acoes = E.planear(pag, c, t, excluir={})
        por = {x["SOURCE_ID"]: x for x in acoes}
        self.assertEqual({"IT-A", "IT-B"}, {s for s, x in por.items() if x["ACAO"] == "APLICA"})
        self.assertNotIn("IT-D", por)                                      # UNKNOWN nao entra
        self.assertEqual(REGRA, t2["FONTES"][0]["SOURCE_LOCATION_RULE"])
        self.assertEqual(c["FONTES"][0]["ACQUISITION"], c2["FONTES"][0]["ACQUISITION"])

    def test_nao_pisa_quem_ja_tem_sede(self):
        c, t = _livros()
        c2, _, acoes = E.planear({"FONTES": [_pag("IT-C")]}, c, t, excluir={})
        self.assertEqual("JA_TEM", acoes[0]["ACAO"])
        self.assertEqual("Milano", c2["FONTES"][2]["SOURCE_LOCATION"])

    def test_pendente_do_dono_fica_de_fora(self):
        c, t = _livros()
        _, _, acoes = E.planear({"FONTES": [_pag("IT-A")]}, c, t, excluir={"IT-A": "decisao do dono"})
        self.assertEqual("PENDENTE_DO_DONO", acoes[0]["ACAO"])

    def test_prova_so_pelo_mesmo_site_nao_e_escrita(self):
        c, t = _livros()
        _, _, acoes = E.planear({"FONTES": [_pag("IT-A", base="MESMO_SITE de IT-X")]}, c, t, excluir={})
        self.assertEqual([], acoes)

    def test_invariante_rebenta_se_outro_campo_mudar(self):
        c, _ = _livros()
        d = {"FONTES": [dict(x) for x in c["FONTES"]]}
        d["FONTES"][0]["ACQUISITION"] = {"INDEX_URL": "https://outro/"}
        with self.assertRaises(E.InvarianteQuebrado):
            E.invariantes(c, d, {"SOURCE_LOCATION"})

    def test_segunda_passagem_e_ja_aplicada(self):
        c, t = _livros()
        pag = {"FONTES": [_pag("IT-A")]}
        c2, t2, _ = E.planear(pag, c, t, excluir={})
        _, _, acoes = E.planear(pag, c2, t2, excluir={})
        self.assertEqual("JA_APLICADA", acoes[0]["ACAO"])


if __name__ == "__main__":
    unittest.main()
