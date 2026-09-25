#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ONDA3-REBASE (DA-15/D67): o bloco B da LEGACY-99 entra INERTE; o A valida pela producao.

    (1) nenhum passo importa ou valida canais YouTube pela rota do B;
    (2) as paginas web do bloco A validam pelo VALIDATE_ROUTE da producao.

Sem rede, sem livros: o robots e substituido, as fontes sao as dos testes da LEGACY-99.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "tests"))
import canario as CAN              # noqa: E402
import escrever_contratos as EC    # noqa: E402
import worker as W                 # noqa: E402
from test_importar_do_coletor import CID, HTML, YT_CURADOR, YT_LINHA  # noqa: E402

LOTES = RAIZ / "ferramentas" / "onda3_pacote" / "LOTES-A-HTML.json"


def _validar(contrato, perguntas):
    with mock.patch.object(W.GATE, "robots_de", return_value=(object(), "lido")), \
         mock.patch.object(W.GATE, "permitido", side_effect=lambda u, rp: perguntas.append(u) or True), \
         mock.patch.object(CAN, "url_da_rota", side_effect=AssertionError("rota do B usada")):
        return W.etapa_validate_route(contrato.get("SOURCE_ID", "IT-X"), contrato)


class BInerte(unittest.TestCase):
    def test_1_molde_novo_de_youtube_nasce_na_rota_da_producao(self):
        c = EC.contrato_youtube({"SOURCE_ID": "IT-T10-017", "NOME": "Canale", "TERRITORY": "T10",
                                 "URL": "https://www.youtube.com/@x"}, {}, CID)
        self.assertNotEqual(CAN.YOUTUBE_CANAL, c["ACQUISITION"].get("ADAPTER_ID"))
        self.assertNotEqual("CUSTOM_ADAPTER", c["ACQUISITION"].get("STRATEGY"))

    def test_1_validate_route_nunca_usa_a_rota_do_b(self):
        perguntas = []
        _validar(YT_CURADOR, perguntas)                                   # contrato de YouTube da producao
        r, _ = _validar({"SOURCE_ID": "IT-T10-017", "ACQUISITION": YT_LINHA["ACQUISITION"]}, perguntas)
        self.assertEqual("FAIL", r)                                       # rota do canal: a producao nao a conhece
        self.assertNotIn("https://www.youtube.com/channel/%s/videos" % CID, perguntas)

    def test_1_o_lote_do_plano_nao_tem_canais_youtube(self):
        d = json.loads(LOTES.read_text(encoding="utf-8"))
        ids = [s for lote in d["LOTES"] for s in lote]
        self.assertEqual(21, len(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn("YOUTUBE", json.dumps(d["LOTES"]))

    def test_2_pagina_web_do_bloco_a_valida_pela_producao(self):
        perguntas = []
        r, info = _validar(HTML, perguntas)
        self.assertEqual("OK", r)
        self.assertEqual([HTML["ACQUISITION"]["INDEX_URL"]], perguntas)


if __name__ == "__main__":
    unittest.main()
