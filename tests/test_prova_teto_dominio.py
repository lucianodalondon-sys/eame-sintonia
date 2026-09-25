#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A prova independente do teto D38 (provas/prova_teto_dominio.py). Offline: lê só ficheiros do repo."""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "provas"))
import prova_teto_dominio as T  # noqa: E402

BC = os.path.join(RAIZ, "ferramentas", "big_collection")
LIVRO_1A = os.path.join(BC, "BC5-1A-ONDA-LIVRO-DE-CORRIDAS.ndjson")
ONDA_1A = os.path.join(BC, "BC5-BIG-COLLECTION-1A-ONDA.json")


def corrida(rid, por_host):
    return json.dumps({"RUN_ID": rid, "CORTESIA": {"PEDIDOS_POR_HOST": por_host}})


R1 = "IT-T7-2026-09-25-010101-00000000000000a1"
R2 = "IT-T7-2026-09-25-010202-00000000000000a2"
R3 = "IT-T7-2026-09-25-010303-00000000000000a3"


class APrimeiraOnda(unittest.TestCase):

    def test_a_1a_onda_reprova_com_cia_it_16(self):
        with open(ONDA_1A, encoding="utf-8") as f:
            ids = T.run_ids_da_onda(f.read())
        with open(LIVRO_1A, encoding="utf-8") as f:
            r = T.verificar(ids, T.ler_livro(f))
        self.assertEqual(len(ids), 18)
        self.assertEqual(r["ESTADO"], "FAIL")
        self.assertEqual(r["DOMINIOS_ACIMA_DO_TETO"], {"cia.it": 16})
        self.assertEqual(len(r["PEDIDOS_POR_DOMINIO"]["cia.it"]["CORRIDAS"]), 5)

    def test_a_cli_sai_com_1_na_1a_onda(self):
        self.assertEqual(T.main(["--livro", LIVRO_1A, "--onda", ONDA_1A]), 1)


class ORegraD38(unittest.TestCase):

    def test_cinco_passa_seis_reprova(self):
        ok = T.verificar([R1, R2], T.ler_livro([corrida(R1, {"a.it": 3}), corrida(R2, {"a.it": 2})]))
        self.assertEqual(ok["ESTADO"], "PASS")
        mau = T.verificar([R1, R2], T.ler_livro([corrida(R1, {"a.it": 3}), corrida(R2, {"a.it": 3})]))
        self.assertEqual(mau["ESTADO"], "FAIL")

    def test_www_e_subdominio_somam_no_mesmo_dominio(self):
        r = T.verificar([R1, R2, R3], T.ler_livro([corrida(R1, {"www.cia.it": 2}), corrida(R2, {"cia.it": 2}),
                                                    corrida(R3, {"toscana.cia.it": 2})]))
        self.assertEqual(r["DOMINIOS_ACIMA_DO_TETO"], {"cia.it": 6})

    def test_nomes_parecidos_sao_dominios_diferentes(self):
        r = T.verificar([R1, R2], T.ler_livro([corrida(R1, {"cia.it": 4}), corrida(R2, {"caf-cia.it": 4})]))
        self.assertEqual(r["ESTADO"], "PASS")

    def test_sufixo_regional_nao_junta_orgaos_diferentes(self):
        r = T.verificar([R1, R2], T.ler_livro([corrida(R1, {"arpa.marche.it": 4}),
                                               corrida(R2, {"www.regione.marche.it": 4})]))
        self.assertEqual(r["ESTADO"], "PASS")
        self.assertIn("arpa.marche.it", r["PEDIDOS_POR_DOMINIO"])
        self.assertIn("regione.marche.it", r["PEDIDOS_POR_DOMINIO"])

    def test_teto_por_parametro(self):
        r = T.verificar([R1], T.ler_livro([corrida(R1, {"a.it": 3})]), teto=2)
        self.assertEqual(r["ESTADO"], "FAIL")


class NaoSeiNaoEZero(unittest.TestCase):

    def test_corrida_da_onda_fora_do_livro_e_nao_sei(self):
        r = T.verificar([R1, R2], T.ler_livro([corrida(R1, {"a.it": 1})]))
        self.assertEqual(r["ESTADO"], "NAO_SEI")
        self.assertEqual(r["CORRIDAS_SEM_LINHA_NO_LIVRO"], [R2])

    def test_corrida_sem_contagem_e_nao_sei(self):
        r = T.verificar([R1], T.ler_livro([json.dumps({"RUN_ID": R1, "CORTESIA": {}})]))
        self.assertEqual(r["ESTADO"], "NAO_SEI")

    def test_onda_vazia_e_nao_sei(self):
        self.assertEqual(T.verificar([], {})["ESTADO"], "NAO_SEI")


class ODominio(unittest.TestCase):

    def test_casos(self):
        casos = {"www.cia.it": "cia.it", "https://www.cia.it/": "cia.it", "cia.it:443": "cia.it",
                 "toscana.cia.it": "cia.it", "agrofarma.federchimica.it": "federchimica.it",
                 "arpa.marche.it": "arpa.marche.it", "agricoltura.regione.emilia-romagna.it": "regione.emilia-romagna.it",
                 "plantgest.imagelinenetwork.com": "imagelinenetwork.com", "WWW.CIA.IT.": "cia.it",
                 "www.gov.uk": "gov.uk", "127.0.0.1": "127.0.0.1"}
        for h, esperado in casos.items():
            self.assertEqual(T.dominio_registavel(h), esperado, h)


if __name__ == "__main__":
    unittest.main(verbosity=1)
