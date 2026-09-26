#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LEITOR-DATA-YOUTUBE — a data de publicação que a página do YouTube escreve em microdados.

    <meta itemprop="datePublished" content="2025-03-11T13:43:59-07:00">

Medido no acervo (ACERVO-TEMPO-LUGAR, 26/09): 603 das 612 páginas de vídeo fora da Sala
trazem a data só aqui. O leitor (`coleta/executor_texto_de_html.tempo_de_publicacao`)
ganha o nível 3b, DEPOIS do `<time>`: só fala onde a D61 se calava.

    PUBLICATION_TIME != FACT_TIME. `uploadDate` não é lido (é quando o ficheiro subiu).

A amostra é um EXCERTO REAL (as marcas `itemprop` da página guardada no armazém). Quando a
página inteira está nesta máquina, o teste lê-a também e confere o sha256. Sem rede.
"""
from __future__ import annotations

import hashlib
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import _gavetas  # noqa: E402,F401
from coleta import executor_texto_de_html as ex  # noqa: E402
from leis import artefato as art  # noqa: E402

AMOSTRA = os.path.join(RAIZ, "tests", "dados", "leitor-data-yt", "it-t7-015-raw201-itemprop.html")
ORIGINAL = os.path.join(os.path.expanduser("~"), "sintonia-sala-italia", "armazem", "XX", "it-t7-015",
                        "OBSERVATION", "cf60e168c2643cd7-u4178bccb10c88b8f-f-Up25Lyn9I")
ORIGINAL_SHA256 = "cf60e168c2643cd75ae6e17eaf2e001b6f37450ea4f6cb16d7412de4169f64c4"
DATA = "2025-03-11T13:43:59-07:00"


def _pagina(cabeca="", corpo=""):
    return "<html><head>%s</head><body>%s</body></html>" % (cabeca, corpo)


class AmostraReal(unittest.TestCase):
    def test_o_excerto_real_da_a_data_com_base_e_precisao(self):
        with open(AMOSTRA, "rb") as fh:
            r = ex.tempo_de_publicacao(fh.read())
        self.assertEqual((DATA, ex.BASE_ITEMPROP, "INSTANTE", DATA),
                         (r["VALOR"], r["BASE"], r["PRECISAO"], r["ORIGINAL"]))

    def test_a_pagina_inteira_do_armazem_da_o_mesmo(self):
        if not os.path.exists(ORIGINAL):
            self.skipTest("a pagina inteira nao esta nesta maquina (armazem fora do Git)")
        with open(ORIGINAL, "rb") as fh:
            b = fh.read()
        self.assertEqual(ORIGINAL_SHA256, hashlib.sha256(b).hexdigest())
        r = ex.tempo_de_publicacao(b)
        self.assertEqual((DATA, ex.BASE_ITEMPROP), (r["VALOR"], r["BASE"]))

    def test_so_a_publicacao_atravessa_nunca_o_facto(self):
        with open(AMOSTRA, "rb") as fh:
            c = ex.publicacao_para_o_contrato(ex.tempo_de_publicacao(fh.read()))
        self.assertEqual(DATA, c["PUBLISHED_AT"])
        self.assertEqual(ex.BASE_ITEMPROP, c["PUBLISHED_AT_BASIS"])
        self.assertFalse({k for k in c if "FACT" in k.upper()})


class OSitioNaOrdem(unittest.TestCase):
    def test_a_ordem_tem_o_itemprop_depois_do_time_e_antes_do_indice(self):
        o = ex.ORDEM_DA_PUBLICACAO
        self.assertEqual((ex.BASE_JSON_LD, ex.BASE_META, ex.BASE_TIME, ex.BASE_ITEMPROP, ex.BASE_INDICE), o)

    def test_nenhuma_data_ja_lida_muda_o_time_continua_a_mandar(self):
        p = _pagina('<meta itemprop="datePublished" content="2025-01-01T00:00:00Z">',
                    '<time datetime="2026-03-03T10:00:00Z">3</time>')
        r = ex.tempo_de_publicacao(p)
        self.assertEqual(("2026-03-03T10:00:00+00:00", ex.BASE_TIME), (r["VALOR"], r["BASE"]))

    def test_o_itemprop_vem_antes_do_indice(self):
        p = _pagina('<meta itemprop="datePublished" content="2025-01-01">')
        r = ex.tempo_de_publicacao(p, data_no_indice="2026-04-04")
        self.assertEqual(("2025-01-01", ex.BASE_ITEMPROP, "DIA"), (r["VALOR"], r["BASE"], r["PRECISAO"]))


class OQueNaoSeLe(unittest.TestCase):
    def test_upload_date_sozinho_nao_e_publicacao(self):
        r = ex.tempo_de_publicacao(_pagina('<meta itemprop="uploadDate" content="2025-03-11T13:43:59-07:00">'))
        self.assertEqual(art.NAO_SEI, r["VALOR"])
        self.assertIn(ex.BASE_ITEMPROP + ": ausente", r["PORQUE"])

    def test_duas_datas_diferentes_calam_se(self):
        r = ex.tempo_de_publicacao(_pagina('<meta itemprop="datePublished" content="2025-01-01T00:00:00Z">'
                                           '<meta itemprop="datePublished" content="2024-06-01T00:00:00Z">'))
        self.assertEqual(art.NAO_SEI, r["VALOR"])
        self.assertIn("AMBIGUO", r["PORQUE"])

    def test_o_mesmo_instante_em_dois_fusos_nao_e_ambiguo(self):
        r = ex.tempo_de_publicacao(_pagina('<meta itemprop="datePublished" content="2025-03-11T13:43:59-07:00">'
                                           '<meta itemprop="datePublished" content="2025-03-11T20:43:59Z">'))
        self.assertEqual((ex.BASE_ITEMPROP, "INSTANTE"), (r["BASE"], r["PRECISAO"]))

    def test_data_em_prosa_nao_se_le(self):
        r = ex.tempo_de_publicacao(_pagina('<meta itemprop="datePublished" content="11 mar 2025">'))
        self.assertEqual(art.NAO_SEI, r["VALOR"])


if __name__ == "__main__":
    unittest.main()
