# -*- coding: utf-8 -*-
"""JANELAS-68-v2 · A — a trava do reparo: o item aprovado tem de ser NOTICIA DATADA.

O reparo geral da receitas-182 aprovou 9 itens nas fontes de janela; pela leitura humana do titulo,
6 eram paginas fixas (acessibilidade, «Le attivita», viveiros...) e 5 eram noticias com data.
Os bytes reais desses 11 itens estao em tests/fixtures/janelas68_itens (MANIFESTO.json com sha256).
Aqui: os 6 falsos TEM de reprovar com motivo, os 5 bons TEM de passar. Sem rede.
"""
import hashlib
import json
import sys
import unittest
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import reparar_contrato as RC                     # noqa: E402
from test_reparar_contrato import (B, CORPO, NOTICIAS, Site, _contrato, _html,   # noqa: E402
                                   inferir)

FIX = AQUI.parent / "tests" / "fixtures" / "janelas68_itens"
MANIFESTO = json.loads((FIX / "MANIFESTO.json").read_text(encoding="utf-8"))["ITENS"]
HOJE = date(2026, 9, 25)          # o dia da medicao: a nossa visita nao e data de publicacao
ESPERADO = {"IT-T3-060": "2025-12-01", "IT-T9-024": "2023-05-16", "IT-T8-069": "2023-05-16",
            "IT-T2-157": "2026-03-18", "IT-T3-062": "2026-07-28"}
SEM_DATA = "<p>" + ("parola " * 200) + "</p>"


def _bytes(item):
    b = (FIX / (item["SOURCE_ID"] + ".html")).read_bytes()
    assert hashlib.sha256(b).hexdigest() == item["SHA256"], item["SOURCE_ID"]
    return b


class CasosReais(unittest.TestCase):
    def test_sao_seis_falsos_e_cinco_bons(self):
        from collections import Counter
        self.assertEqual({"FALSO": 6, "BOM": 5}, dict(Counter(i["VEREDITO_HUMANO"] for i in MANIFESTO)))

    def test_pagina_fixa_nao_tem_data_de_publicacao(self):
        for i in MANIFESTO:
            if i["VEREDITO_HUMANO"] == "FALSO":
                with self.subTest(i["SOURCE_ID"]):
                    self.assertIsNone(RC.data_de_publicacao(_bytes(i), hoje=HOJE))

    def test_noticia_boa_tem_a_data_certa(self):
        for i in MANIFESTO:
            if i["VEREDITO_HUMANO"] == "BOM":
                with self.subTest(i["SOURCE_ID"]):
                    d = RC.data_de_publicacao(_bytes(i), hoje=HOJE)
                    self.assertIsNotNone(d)
                    self.assertEqual(ESPERADO[i["SOURCE_ID"]], d[0])

    def test_pelo_reparo_inteiro_falso_reprova_com_motivo_e_bom_passa(self):
        for i in MANIFESTO:
            with self.subTest(i["SOURCE_ID"]):
                site = Site({B + "/": (200, _html(NOTICIAS + ["/contatti", "/chi-siamo"])),
                             **{B + n: (200, _bytes(i)) for n in NOTICIAS}})
                p = inferir(_contrato(), site)
                if i["VEREDITO_HUMANO"] == "FALSO":
                    self.assertEqual(("RECUSA", "ITEM_SEM_DATA_DE_PUBLICACAO"),
                                     (p["DESFECHO"], p.get("MOTIVO")), p.get("PORQUE"))
                else:
                    self.assertEqual("PADRAO_NOVO", p["DESFECHO"], p.get("PORQUE"))
                    self.assertEqual(ESPERADO[i["SOURCE_ID"]], p["ITEM_LIDO"]["DATA_DE_PUBLICACAO"])


class Regra(unittest.TestCase):
    def test_item_com_corpo_e_sem_data_reprova(self):
        site = Site({B + "/": (200, _html(NOTICIAS + ["/contatti", "/chi-siamo"])),
                     **{B + n: (200, _html([], SEM_DATA)) for n in NOTICIAS}})
        p = inferir(_contrato(), site)
        self.assertEqual(("RECUSA", "ITEM_SEM_DATA_DE_PUBLICACAO"), (p["DESFECHO"], p["MOTIVO"]))

    def test_data_do_dia_da_visita_ou_futura_nao_prova(self):
        for c in ("2026-09-25", "2026-10-02", "1999-05-01"):
            with self.subTest(c):
                h = '<meta property="article:published_time" content="%sT10:00:00">' % c
                self.assertIsNone(RC.data_de_publicacao(h, hoje=HOJE))

    def test_data_de_atualizacao_sob_o_titulo_nao_e_publicacao(self):
        self.assertIsNone(RC.data_de_publicacao("<h1>Pagina</h1><p>Ultimo aggiornamento 12/03/2026</p>", hoje=HOJE))
        self.assertEqual(("2026-03-12", "DATA_SOB_O_TITULO"),
                         RC.data_de_publicacao("<h1>Notizia</h1><p>12/03/2026</p>", hoje=HOJE))

    def test_formas_de_prova(self):
        casos = {'<script>{"datePublished": "2026-02-03T08:00"}</script>': "DATEPUBLISHED",
                 '<span itemprop="datePublished" content="2026-02-03"></span>': "ITEMPROP_DATEPUBLISHED",
                 "<p>Pubblicato il 3 febbraio 2026</p>": "ROTULO_PUBBLICATO"}
        for h, como in casos.items():
            with self.subTest(como):
                self.assertEqual(("2026-02-03", como), RC.data_de_publicacao(h, hoje=HOJE))

    def test_corpo_dos_testes_antigos_tem_data(self):
        self.assertIsNotNone(RC.data_de_publicacao(CORPO, hoje=HOJE))


if __name__ == "__main__":
    unittest.main()
