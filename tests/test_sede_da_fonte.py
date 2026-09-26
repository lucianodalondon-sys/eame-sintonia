#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEDE-37-PREP — a sede de quem publica, lida em páginas JÁ guardadas, e como entra no contrato.

    SOURCE_LOCATION != FACT_LOCATION.   UNKNOWN FICA UNKNOWN.

As amostras são EXCERTOS REAIS de páginas guardadas na loja do vivo (sha256 em tests/dados/sede37/ORIGEM.json);
quando a página inteira está nesta máquina, o teste lê-a também e confere o sha256. Sem rede, sem escrever.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, "curadoria"), os.path.join(RAIZ, "regras")):
    if p not in sys.path:
        sys.path.insert(0, p)
import _gavetas  # noqa: E402,F401
import sede_da_fonte as S  # noqa: E402
import onboardar_rotas_provadas as ONB  # noqa: E402

DADOS = os.path.join(RAIZ, "tests", "dados", "sede37")
ORIGEM = json.load(open(os.path.join(DADOS, "ORIGEM.json"), encoding="utf-8"))
LOJA = "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/data/collection-store/italy/"


def _amostra(nome):
    b = open(os.path.join(DADOS, nome + ".html"), "rb").read()
    return ("https://exemplo/" + nome, hashlib.sha256(b).hexdigest(), b)


class ComProva(unittest.TestCase):
    def test_arpat_firenze_no_gazetteer_com_contatti_ao_lado(self):
        r = S.sede_das_paginas([_amostra("arpat-1"), _amostra("arpat-2")])
        self.assertEqual(("Firenze", "PROVINCE"), (r["SOURCE_LOCATION"], r["SOURCE_LOCATION_PRECISION"]))
        self.assertIn("50144", r["SOURCE_LOCATION_BASIS"])
        self.assertIn("PAGINA_GUARDADA_DA_PROPRIA_FONTE", r["SOURCE_LOCATION_BASIS"])

    def test_myfruit_comune_fora_do_gazetteer_vira_a_provincia_da_sigla(self):
        r = S.sede_das_paginas([_amostra("myfruit-1"), _amostra("myfruit-2")])
        self.assertEqual(("Modena", "PROVINCE"), (r["SOURCE_LOCATION"], r["SOURCE_LOCATION_PRECISION"]))
        self.assertIn("Spilamberto", r["SOURCE_LOCATION_BASIS"])
        self.assertIn("PROVINCIA da sigla MO", r["SOURCE_LOCATION_BASIS"])

    def test_a_regra_passa_no_leitor_do_contrato(self):
        r = S.sede_das_paginas([_amostra("myfruit-1"), _amostra("myfruit-2")])
        self.assertEqual(("Modena", "PROVINCE"), S.confere(r["SOURCE_LOCATION_RULE"]))
        self.assertTrue(r["SOURCE_LOCATION_RULE"].endswith("— fixo"))

    def test_as_paginas_inteiras_da_loja_dao_o_mesmo(self):
        pags = []
        for nome in ("myfruit-1", "myfruit-2"):
            f = LOJA + ORIGEM[nome]["ORIGINAL"]
            if not os.path.exists(f):
                self.skipTest("a loja do vivo nao esta nesta maquina")
            b = open(f, "rb").read()
            self.assertEqual(ORIGEM[nome]["SHA256"], hashlib.sha256(b).hexdigest())
            pags.append((f, ORIGEM[nome]["SHA256"], b))
        self.assertEqual("Modena", S.sede_das_paginas(pags)["SOURCE_LOCATION"])


    def test_comune_em_maiusculas_confere_com_o_gazetteer(self):
        # IT-T7-043 (Agrofarma): o rodape diz «SEDE Via Giovanni da Procida, 11 20149 - MILANO»
        b = "<footer>SEDE Via Giovanni da Procida, 11 20149 - MILANO</footer>".encode()
        r = S.sede_das_paginas([("u1", "a" * 64, b)])
        self.assertEqual(("Milano", "PROVINCE"), (r["SOURCE_LOCATION"], r["SOURCE_LOCATION_PRECISION"]))


class SemProvaFicaNaoSei(unittest.TestCase):
    def test_morada_de_evento_numa_pagina_so_e_nao_sei(self):
        r = S.sede_das_paginas([_amostra("chianti-evento")])
        self.assertEqual(S.NAO_SEI, r["SOURCE_LOCATION"])
        self.assertIsNone(r["SOURCE_LOCATION_RULE"])
        self.assertEqual("Milano", r["CANDIDATA_NAO_PROVADA"]["COMUNE"])

    def test_nenhuma_pagina_e_nao_sei(self):
        self.assertEqual(S.NAO_SEI, S.sede_das_paginas([])["SOURCE_LOCATION"])

    def test_sigla_fora_da_tabela_declarada_nao_e_palpite(self):
        b = ("<footer>Sede legale Via Roma 1 - 12345 Paesino (ZZ)</footer>").encode()
        r = S.sede_das_paginas([("u1", "a" * 64, b), ("u2", "b" * 64, b)])
        self.assertEqual(S.NAO_SEI, r["SOURCE_LOCATION"])
        self.assertIn("NOT_IN_GAZETTEER", r["SOURCE_LOCATION_BASIS"])

    def test_nao_sei_nao_se_escreve_no_contrato(self):
        self.assertEqual({}, S.campos_para_o_contrato(S.sede_das_paginas([_amostra("chianti-evento")])))

    def test_nunca_sai_lugar_do_facto(self):
        r = S.sede_das_paginas([_amostra("arpat-1"), _amostra("arpat-2")])
        self.assertFalse({k for k in S.campos_para_o_contrato(r) if "FACT" in k})


class APonte(unittest.TestCase):
    P = {"CANARIO": {"URL": "u", "BYTES": 1, "HTML_KIND": "CONTENT", "PARAGRAPH_CHARACTERS": 900}}

    def _c(self, **extra):
        return dict({"SOURCE_ID": "IT-X-1", "ACQUISITION": {"INDEX_URL": "https://x.it/"}}, **extra)

    def test_a_sede_do_contrato_do_curator_vai_para_a_tabela(self):
        r = S.sede_das_paginas([_amostra("arpat-1"), _amostra("arpat-2")])
        linha = ONB.linha_da_tabela(self._c(**S.campos_para_o_contrato(r)), self.P, "2026-09-26T00:00:00")
        self.assertEqual(r["SOURCE_LOCATION_RULE"], linha["SOURCE_LOCATION_RULE"])

    def test_sem_sede_a_tabela_nao_declara_e_o_coletor_le_nao_sei(self):
        linha = ONB.linha_da_tabela(self._c(), self.P, "2026-09-26T00:00:00")
        self.assertNotIn("SOURCE_LOCATION_RULE", linha)


if __name__ == "__main__":
    unittest.main()
