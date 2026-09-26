#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D13 · o crossing do piloto mede as chaves no CAMPO, nao as escreve fixas.

Valores da 1.a rodada real (EXPD78, copia da Sala de 26/09): IT-T3-008 (ARIF
Puglia) tem FACT_TIME e FACT_LOCATION com base e a v2 dizia que faltavam.
Nenhum teste abre a Sala, o banco ou a rede; a referencia ADAMA e fingida.
"""
import importlib.util
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("o_piloto_da_sala", RAIZ / "provas" / "o_piloto_da_sala.py")
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

SUBS = {"AZOXYSTROBIN": {"R1"}}
USOS = [{"REGISTRATION_NUMBER": "R1", "CROP_ON_LABEL": "VITE"}]
VIVOS = [{"num_registrazione": "R1", "produto": "PRODUTO-X"}]


def boletim(**kw):
    b = {"source_id": "IT-T3-008", "run_id": "RUN", "ordem": 1, "raw_observation_id": 7,
         "texto": "trattamento con azoxystrobin",
         "fact_time": "2026-09-07/2026-09-13",
         "fact_time_basis": "CAMPO · ESCRITO_NO_TEXTO · WEEK ancora «7-13 settembre»",
         "fact_location": "Puglia",
         "fact_location_basis": "CAMPO · CITADO · REGION ancora «Puglia»",
         "source_location": "Bari"}
    b.update(kw)
    return b


def cruza(**kw):
    return P.cruzar([boletim(**kw)], SUBS, USOS, VIVOS)[0]


class D13(unittest.TestCase):
    def test_negativo_o_conhecido_nao_e_declarado_em_falta(self):
        c = cruza()
        self.assertEqual(c["JOIN_KEYS_MISSING"], ["CROP"])
        self.assertIn("FACT_TIME", c["JOIN_KEYS_PRESENT"])
        self.assertIn("REGION", c["JOIN_KEYS_PRESENT"])

    def test_sem_crop_continua_not_possible(self):
        self.assertEqual(cruza()["CROSSING_STATE"], "NOT_POSSIBLE")

    def test_negativo_cultura_no_texto_nao_e_crop(self):
        c = cruza(texto="azoxystrobin su VITE e MELO")
        self.assertIn("CROP", c["JOIN_KEYS_MISSING"])
        self.assertEqual(c["CROSSING_STATE"], "NOT_POSSIBLE")

    def test_negativo_valor_sem_base_nao_conta(self):
        c = cruza(fact_time_basis="o coletor declarou · UNKNOWN", fact_location_basis="NAO SEI")
        self.assertEqual(sorted(c["JOIN_KEYS_MISSING"]), ["CROP", "FACT_TIME", "REGION"])

    def test_negativo_source_location_nao_vira_region(self):
        c = cruza(fact_location="NAO SEI", source_location="Puglia")
        self.assertIn("REGION", c["JOIN_KEYS_MISSING"])

    def test_positivo_crop_como_campo_da_candidato_e_nunca_oportunidade(self):
        c = cruza(janela_declarada={"CULTURA": {"VALOR": "VITE", "BASE": "CAMPO"}})
        self.assertEqual(c["JOIN_KEYS_MISSING"], [])
        self.assertEqual(c["CROSSING_STATE"], "CANDIDATE_ALL_KEYS_PRESENT")
        self.assertEqual(c["STATUS"], "EVIDENCE_LINKED_OBSERVATION")

    def test_parcial_com_crop_mas_sem_tempo(self):
        c = cruza(fact_time="NAO SEI", janela_declarada={"CULTURA": {"VALOR": "VITE"}})
        self.assertEqual(c["CROSSING_STATE"], "PARTIAL")

    def test_a_versao_subiu(self):
        self.assertEqual(P.PIPELINE_VERSION, "3")


if __name__ == "__main__":
    unittest.main()
