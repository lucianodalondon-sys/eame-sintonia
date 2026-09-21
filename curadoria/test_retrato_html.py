#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CAPA != MATERIA, do lado do SOURCE CURATOR.

As mesmas provas que `tests/test_capa_nao_e_materia.py` faz ao Node na linha
f98f234c, feitas ao retrato Python desta arvore — com os mesmos HTMLs
sinteticos, para que os dois leitores nao possam discordar sem um teste dar
vermelho.

    TESTE QUE NUNCA VIU VERMELHO NAO E TESTE.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import retrato_html as RH  # noqa: E402


def listagem_sintetica(n: int = 60) -> str:
    itens = "".join('<li><a href="/news/item-%d-titolo-breve">Titolo %d</a></li>' % (i, i)
                    for i in range(n))
    return ("<html><head><title>News</title></head><body><nav><ul>%s</ul></nav>"
            "</body></html>" % itens)


def artigo_sintetico(janela: str = "dal 01/09/2026 al 07/09/2026", sal: str = "",
                     corpo: str | None = None) -> str:
    corpo = corpo or ("La mosca dell'olivo accelera con il calo termico. " * 40)
    return ("<html><head><title>Bollettino</title>%s</head><body><h1>Bollettino %s</h1>"
            "<p>%s</p><p>%s</p><p>%s</p><a href=\"/a\">a</a><a href=\"/b\">b</a></body></html>"
            % (sal, janela, corpo, corpo, corpo))


DETALHE = {"OUTPUT_TYPE": "HTML",
           "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL"}}


class ORetratoDistingueCapaDeMateria(unittest.TestCase):

    def test_1_uma_listagem_e_CAPA_PROVAVEL(self):
        r = RH.retrato_do_html(listagem_sintetica().encode("utf-8"))
        self.assertEqual("NAVIGATION", r["HTML_KIND"])
        self.assertEqual("CAPA_PROVAVEL", r["CAPA_OU_MATERIA"])
        self.assertEqual(60, r["LINKS"])

    def test_2_um_artigo_e_MATERIA_PROVAVEL(self):
        r = RH.retrato_do_html(artigo_sintetico().encode("utf-8"))
        self.assertEqual("CONTENT", r["HTML_KIND"])
        self.assertEqual("MATERIA_PROVAVEL", r["CAPA_OU_MATERIA"])

    def test_3_pagina_vazia_nao_e_nenhuma_das_duas(self):
        r = RH.retrato_do_html(b"<html><body><script>var x=1;</script></body></html>")
        self.assertEqual("EMPTY", r["HTML_KIND"])
        self.assertEqual("NAO_SEI", r["CAPA_OU_MATERIA"])

    def test_4_o_texto_tem_impressao_propria_e_o_markup_nao_a_move(self):
        a = RH.retrato_do_html(artigo_sintetico().encode("utf-8"))
        b = RH.retrato_do_html(artigo_sintetico(
            sal='<meta name="nonce" content="abc123"><!-- 2026-09-21T01:12:38Z -->').encode("utf-8"))
        c = RH.retrato_do_html(artigo_sintetico(
            corpo="Un testo diverso, con altre parole dentro. " * 40).encode("utf-8"))
        self.assertEqual(a["TEXT_SHA256"], b["TEXT_SHA256"],
                         "markup trocado nao pode mudar a impressao do texto")
        self.assertNotEqual(a["TEXT_SHA256"], c["TEXT_SHA256"],
                            "texto trocado tem de mudar a impressao")

    def test_4b_os_limiares_sao_os_do_coletor(self):
        """Mudar um limiar aqui sem mudar no coletor cria um segundo juiz."""
        self.assertEqual(800, RH.PARAGRAFO_MINIMO)
        self.assertEqual(0.35, RH.PARAGRAFO_FRACCAO)
        self.assertEqual(40, RH.CARACTERES_POR_LIGACAO)
        self.assertEqual("CONTENT", RH.kind_de(1000, 800, 5))
        self.assertEqual("MIXED", RH.kind_de(1000, 799, 5))      # um caractere abaixo
        self.assertEqual("NAVIGATION", RH.kind_de(390, 100, 10))  # 39 por ligacao
        self.assertEqual("MIXED", RH.kind_de(400, 100, 10))       # 40 por ligacao


class OGateBarraACapaSoOndeOContratoDeclaraDetalhe(unittest.TestCase):

    def test_5_contrato_de_detalhe_com_capa_REPROVA(self):
        g = RH.gate_capa_nao_e_materia(DETALHE, RH.retrato_do_html(listagem_sintetica().encode()))
        self.assertIsNotNone(g)
        self.assertTrue(g.startswith("CAPA_NAO_E_MATERIA"), g)

    def test_6_contrato_de_detalhe_com_materia_passa(self):
        self.assertIsNone(RH.gate_capa_nao_e_materia(
            DETALHE, RH.retrato_do_html(artigo_sintetico().encode())))

    def test_7_rota_fixa_nao_e_julgada_pelo_gate(self):
        fixo = {"OUTPUT_TYPE": "HTML", "ACQUISITION": {"STRATEGY": "STATIC_ENDPOINT", "URL": "x"}}
        self.assertIsNone(RH.gate_capa_nao_e_materia(
            fixo, RH.retrato_do_html(listagem_sintetica().encode())),
            "STATIC_ENDPOINT nao declara itens de detalhe")

    def test_8_pdf_nao_e_julgado_pelo_gate(self):
        pdf = {"OUTPUT_TYPE": "PDF", "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL"}}
        self.assertIsNone(RH.gate_capa_nao_e_materia(
            pdf, RH.retrato_do_html(listagem_sintetica().encode())))


if __name__ == "__main__":
    unittest.main()
