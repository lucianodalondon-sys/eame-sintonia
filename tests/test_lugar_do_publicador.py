#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LUGAR-DO-PUBLICADOR — a sede de quem publica, do contrato para a Sala (D83).

    1. D83.2: cidade fora do gazetteer -> a PROVINCIA da sigla (Legnaro PD, Rivarolo del Re CR — rodapes reais);
    2. a porta de escrita escreve na TABELA do coletor as fontes que nao estao no Curator (universidades da Sala);
    3. D83.1: a Image Line fica com a sede LEGAL (Roma); a operacional (Faenza) vai so para a base;
    4. a porta da Sala so escreve SOURCE_LOCATION (e a completude), nunca pisa, NAO SEI nao entra.

Os trechos sao os rodapes lidos a mao na medida (ferramentas/lugar_publicador/medida/PROVAS-LIDAS.json).
Sem rede, sem banco.
"""
from __future__ import annotations

import os
import sys
import unittest
from unittest import mock

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "curadoria"))
sys.path.insert(0, os.path.join(RAIZ, "ferramentas", "sede37"))
sys.path.insert(0, os.path.join(RAIZ, "ferramentas", "lugar_publicador"))
import sede_da_fonte as S  # noqa: E402
import escrever_sede as E  # noqa: E402
import preencher_sede_na_sala as P  # noqa: E402

DAFNAE = ("<footer>Amministrazione trasparente Staff CONTATTI Via dell'Università 16, 35020 Legnaro (PD) "
          "Tel. +39 049 827 2664</footer>").encode()
CASALASCO = ("<footer>Copyright © 2026 CASALASCO SOCIETÀ AGRICOLA S.p.A. - A SOCIO UNICO, Sp 32, 26036 RIVAROLO DEL RE "
             "(CR) - ITALY, TEL. +39 0375536211</footer>").encode()
IBBR_UMA_PAGINA = ("<footer>Istituto di Bioscienze e Biorisorse (IBBR/CNR) Via G. Amendola 165/A, I-70126 Bari (Italy) "
                   "Copyright © 2012-2026</footer>").encode()


def _p(b, n=2):
    return [("u%d" % i, ("%d" % i) * 64, b) for i in range(n)]


class D83CidadeViraProvincia(unittest.TestCase):
    def test_legnaro_pd_e_padova_com_precisao_province(self):
        r = S.sede_das_paginas(_p(DAFNAE))
        self.assertEqual(("Padova", "PROVINCE"), (r["SOURCE_LOCATION"], r["SOURCE_LOCATION_PRECISION"]))
        self.assertIn("Legnaro PD", r["SOURCE_LOCATION_RULE"])              # o texto original fica na prova

    def test_rivarolo_del_re_cr_em_maiusculas_e_cremona(self):
        self.assertEqual("Cremona", S.sede_das_paginas(_p(CASALASCO, 3))["SOURCE_LOCATION"])

    def test_uma_pagina_sem_sede_ao_lado_continua_nao_sei(self):
        self.assertEqual(S.NAO_SEI, S.sede_das_paginas(_p(IBBR_UMA_PAGINA, 1))["SOURCE_LOCATION"])

    def test_so_as_siglas_declaradas_e_todas_no_gazetteer(self):
        for sigla, prov in S.PROVINCIA_DA_SIGLA.items():
            self.assertEqual("PROVINCE", S.GAZ.get(prov), sigla)


def _pag(sid, loc="Roma", regra="Roma (sede: Roma, CAP 00195; prova: PAGINA_GUARDADA) — fixo"):
    return {"SOURCE_ID": sid, "SEDE_SEM_REDE": {
        "SOURCE_LOCATION": loc, "SOURCE_LOCATION_BASIS": "PAGINA_GUARDADA_DA_PROPRIA_FONTE · u · sha256 x",
        "SOURCE_LOCATION_PRECISION": "PROVINCE", "SOURCE_LOCATION_RULE": regra}}


class PortaDeEscrita(unittest.TestCase):
    def _livros(self):
        c = {"FONTES": [{"SOURCE_ID": "IT-T10-021", "ACQUISITION": {}}]}
        t = {"FONTES": [{"SOURCE_ID": "IT-T5-028", "ACQUISITION": {"INDEX_URL": "https://di4a.uniud.it/"}},
                        {"SOURCE_ID": "IT-T5-099", "ACQUISITION": {}, "SOURCE_LOCATION_RULE": "Bari (sede) — fixo"}]}
        return c, t

    def test_fora_do_curator_mas_na_tabela_escreve_so_a_tabela(self):
        c, t = self._livros()
        c2, t2, acoes = E.planear({"FONTES": [_pag("IT-T5-028", "Udine", "Udine (sede: Udine, CAP 33100; prova: "
                                                                          "PAGINA_GUARDADA) — fixo")]}, c, t)
        self.assertEqual("APLICA", acoes[0]["ACAO"])
        self.assertTrue(t2["FONTES"][0]["SOURCE_LOCATION_RULE"].startswith("Udine"))
        self.assertEqual(c, c2)                                             # o Curator nao ganha fonte
        self.assertEqual(t["FONTES"][0]["ACQUISITION"], t2["FONTES"][0]["ACQUISITION"])

    def test_na_tabela_com_outra_regra_nao_se_pisa(self):
        c, t = self._livros()
        _, t2, acoes = E.planear({"FONTES": [_pag("IT-T5-099")]}, c, t)
        self.assertEqual("JA_TEM", acoes[0]["ACAO"])
        self.assertEqual("Bari (sede) — fixo", t2["FONTES"][1]["SOURCE_LOCATION_RULE"])

    def test_d83_1_image_line_sede_legal_roma_e_operacional_na_base(self):
        c, t = self._livros()
        c2, _, acoes = E.planear({"FONTES": [_pag("IT-T10-021")]}, c, t)
        self.assertEqual("APLICA", acoes[0]["ACAO"])
        self.assertEqual("Roma", c2["FONTES"][0]["SOURCE_LOCATION"])
        self.assertIn("Faenza", c2["FONTES"][0]["SOURCE_LOCATION_BASIS"])
        self.assertNotIn("Faenza", c2["FONTES"][0]["SOURCE_LOCATION_RULE"])


def _linha(sid="IT-T5-028", loc="NAO SEI"):
    return {"SOURCE_ID": sid, "SOURCE_LOCATION": loc, "COMPLETUDE_TEMPO_LUGAR": {
        "DATA_DO_FATO": "NAO SEI", "LOCAL_DA_FONTE": "PROVADA" if loc != "NAO SEI" else "NAO SEI",
        "LOCAL_DO_FATO": "NAO SEI", "PROVADAS": 2 if loc != "NAO SEI" else 1, "PUBLICACAO": "PROVADA"}}


def _contrato(valor):
    r = {"VALOR": valor, "BASE": "CONTRATO" if valor != "NAO SEI" else "NAO SEI", "PRECISAO": "PROVINCE",
         "ORIGINAL": "x", "PORQUE": "CONTRATO: x"}
    return mock.patch.object(P.CDF, "lugar_da_fonte", return_value=r)


class PortaDaSala(unittest.TestCase):
    def test_ganha_a_sede_e_a_completude_sobe_um(self):
        with _contrato("Udine"):
            revs, _ = P.revisoes_da_linha(_linha())
        self.assertEqual(["source_location", "completude_tempo_lugar"], [r["CAMPO"] for r in revs])
        self.assertEqual(("Udine", "CONTRATO"), (revs[0]["VALOR"], revs[0]["BASE"]))
        self.assertIn('"LOCAL_DA_FONTE": "PROVADA"', revs[1]["VALOR"])
        self.assertIn('"PROVADAS": 2', revs[1]["VALOR"])

    def test_contrato_sem_sede_nao_escreve_nada(self):
        with _contrato("NAO SEI"):
            self.assertEqual([], P.revisoes_da_linha(_linha())[0])
            self.assertEqual([], P.revisoes_da_linha(_linha(loc=""))[0])      # vazio na Sala: NAO SEI nao entra

    def test_nunca_pisa_uma_sede_que_a_sala_ja_tem(self):
        with _contrato("Roma"):
            revs, porque = P.revisoes_da_linha(_linha(loc="Napoli"))
        self.assertEqual([], revs)
        self.assertIn("nao se pisa", porque)

    def test_a_mesma_sede_e_ja_e_assim(self):
        with _contrato("Napoli"):
            self.assertEqual(([], "JA_E_ASSIM"), P.revisoes_da_linha(_linha(loc="Napoli")))

    def test_os_outros_tres_campos_nunca_sao_revistos(self):
        with _contrato("Udine"):
            revs, _ = P.revisoes_da_linha(_linha())
        self.assertFalse({"published_at", "fact_time", "fact_location"} & {r["CAMPO"] for r in revs})


if __name__ == "__main__":
    unittest.main()
