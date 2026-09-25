#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O RETORNO.json NAO PODE DIZER SUCCESS NUMA FALHA — FECHAR-ONDA2-B (D60 b).

MEDIDO NA 2.a ONDA (2026-09-25, IT-T2-050, ARPA Campania): o coletor rebentou
com `mkdir ENOENT` (um `?` no nome da pasta) e saiu com codigo 1. O executor
escreveu o envelope da corrida com `ESTADO = SUCCESS` e `ERROS = []`, porque
`coleta/italy_executor.py::declarar` escrevia SUCCESS sempre e `main()` nunca
entregava o resultado do coletor a `colher()`.

Estes testes correm `main()` a serio, com o coletor substituido (sem rede) e o
livro e o balcao numa pasta temporaria.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from coleta import italy_executor as ie  # noqa: E402
import retorno_da_coleta as rdc  # noqa: E402

RUN = "IT-T2-2026-09-25-000000-fechaonda2b0000"
ENOENT = ("Error: ENOENT: no such file or directory, mkdir "
          "'data/collection-store/italy/IT-T2-050/2026-09-25/"
          "https_www.arpacampania.it_?redirect=%2F'")


class _Balcao(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="fo2b-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        livro = os.path.join(self.tmp, ie.LIVRO)
        os.makedirs(os.path.dirname(livro), exist_ok=True)
        open(livro, "w", encoding="utf-8").close()
        self.livro = livro

    def observacao(self):
        with open(self.livro, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"RUN_ID": RUN, "SOURCE_ID": "IT-T2-050",
                                 "DOCUMENT_ID": "IT-T2-050:URL:x",
                                 "RAW_SHA256": "ab" * 32}) + "\n")

    def correr_main(self, coletor: dict):
        """`main()` inteiro; so a ida a fonte e o sitio do balcao mudam."""
        original = ie.colher

        def colher_no_tmp(run_id, ops_root=None, raiz=None, **kw):
            return original(run_id, ops_root=self.tmp, raiz=self.tmp, **kw)

        saida = {}

        def colher_e_guardar(*a, **kw):
            saida.update(colher_no_tmp(*a, **kw))
            return saida

        with mock.patch.object(ie, "correr_coletor", return_value=coletor), \
                mock.patch.object(ie, "colher", side_effect=colher_e_guardar), \
                mock.patch.object(sys, "argv", ["x", "--run-id=%s" % RUN]), \
                mock.patch("sys.stdout"):
            codigo = ie.main()
        with open(os.path.join(self.tmp, saida["DECLAROU_EM"]),
                  encoding="utf-8") as fh:
            return codigo, json.load(fh)


class ORetornoNaoMente(_Balcao):

    def test_1_coletor_rebenta_sem_nada_e_FAILED_com_o_erro(self):
        """O caso da IT-T2-050: codigo 1, zero observacoes."""
        codigo, env = self.correr_main({"CODIGO": 1, "ERRO": ENOENT})
        self.assertEqual(codigo, 1)
        self.assertEqual(env["ESTADO"], rdc.FAILED,
                         "o RETORNO.json disse %s com o coletor a falhar" % env["ESTADO"])
        self.assertEqual(len(env["ERROS"]), 1)
        self.assertEqual(env["ERROS"][0]["MOTIVO"], "COLETOR_FALHOU")
        self.assertIn("ENOENT", env["ERROS"][0]["ERRO"])
        self.assertEqual(rdc.conferir(env, self.tmp), [])

    def test_2_coletor_rebenta_depois_de_colher_e_PARTIAL_e_a_colheita_segue(self):
        self.observacao()
        codigo, env = self.correr_main({"CODIGO": 1, "ERRO": ENOENT})
        self.assertEqual(codigo, 1)
        self.assertEqual(env["ESTADO"], rdc.PARTIAL)
        self.assertEqual(len(env["COLHEITA"]), 1)
        self.assertEqual(len(rdc.so_o_que_entra(env)), 1)
        self.assertEqual(rdc.conferir(env, self.tmp), [])

    def test_3_zero_legitimo_continua_SUCCESS(self):
        """EMPTY_SUCCESS != ERROR: o conserto nao pode fabricar falhas."""
        codigo, env = self.correr_main({"CODIGO": 0, "ERRO": ""})
        self.assertEqual(codigo, 0)
        self.assertEqual(env["ESTADO"], rdc.SUCCESS)
        self.assertEqual(env["ERROS"], [])

    def test_4_sucesso_com_colheita_continua_SUCCESS(self):
        self.observacao()
        _, env = self.correr_main({"CODIGO": 0, "ERRO": "aviso qualquer"})
        self.assertEqual(env["ESTADO"], rdc.SUCCESS)
        self.assertEqual(env["ERROS"], [])

    def test_5_bloqueada_pelo_curator_nao_e_SUCCESS(self):
        """NAO CORREU NAO E CORREU E FALHOU — mas tambem nao e SUCCESS."""
        codigo, env = self.correr_main({
            "CODIGO": 1, "ERRO": "", "CORREU": False,
            "BLOQUEADA_PELO_CURATOR": {"SOURCE_ID": "IT-T2-050",
                                       "MOTIVO": "NAO_ELEGIVEL",
                                       "PORQUE": "sem contrato"}})
        self.assertEqual(codigo, 1)
        self.assertEqual(env["ESTADO"], rdc.FAILED)
        self.assertEqual(env["ERROS"][0]["MOTIVO"], "BLOQUEADA_PELO_CURATOR")
        self.assertIn("NAO_ELEGIVEL", env["ERROS"][0]["ERRO"])
        self.assertEqual(rdc.conferir(env, self.tmp), [])

    def test_6_falha_sem_stderr_ainda_escreve_um_porque(self):
        _, env = self.correr_main({"CODIGO": 3, "ERRO": ""})
        self.assertEqual(env["ESTADO"], rdc.FAILED)
        self.assertIn("codigo 3", env["ERROS"][0]["ERRO"])

    def test_7_colher_sozinho_sem_coletor_continua_como_era(self):
        """A traducao offline (`colher()` sem coletor) nao inventa erros."""
        c = ie.colher(RUN, ops_root=self.tmp, raiz=self.tmp)
        with open(os.path.join(self.tmp, c["DECLAROU_EM"]), encoding="utf-8") as fh:
            env = json.load(fh)
        self.assertEqual(env["ESTADO"], rdc.SUCCESS)
        self.assertEqual(env["ERROS"], [])


if __name__ == "__main__":
    unittest.main()
