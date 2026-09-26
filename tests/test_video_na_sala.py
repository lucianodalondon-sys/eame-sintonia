# -*- coding: utf-8 -*-
"""PROPOSTA 037 · o escritor do video na Sala: UNKNOWN nao gera linha, a partilha diz de quem e.

O banco (com a 037 aplicada) prova-se no ensaio descartavel (`provas/migracao_037_ensaio_descartavel.py`,
so com a LOCK-PESADO); aqui, sem banco: o SQL que se manda e o que a proposta aceita.
"""
import json
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "admissao"))
sys.path.insert(0, os.path.join(RAIZ, "leis"))
import video_na_sala as VS  # noqa: E402
import identidade_do_video as IV  # noqa: E402

ASSET = "LINKEDIN:urn:li:digitalmediaAsset:D4D05AQH1yJW2COxvNQ"
PROPOSTA = os.path.join(RAIZ, "supabase", "propostas", "037_a_sala_diz_qual_video_e_o_mesmo.sql")


class V1Escritor(unittest.TestCase):
    def test_unknown_nao_gera_linha(self):
        self.assertIsNone(VS.sql_de_registo("R", [(0, {"VIDEO_IDENTITY": "NAO SEI"}), (1, {})]))

    def test_a_partilha_leva_de_quem_e(self):
        sql = VS.sql_de_registo("R2", [(0, {"VIDEO_IDENTITY": ASSET, "VIDEO_IDENTITY_BASIS": "ASSET_URN",
                                            "MESMO_VIDEO_QUE": {"SOURCE_ID": "IT-T5-193", "RUN_ID": "R1"}})])
        self.assertIn("'%s'" % ASSET, sql)
        self.assertIn('\'{"RUN_ID": "R1", "SOURCE_ID": "IT-T5-193"}\'::jsonb', sql)
        self.assertIn("on conflict (run_id, ordem) do nothing", sql)

    def test_o_primeiro_vai_com_null(self):
        sql = VS.sql_de_registo("R1", [(3, {"VIDEO_IDENTITY": ASSET, "VIDEO_IDENTITY_BASIS": "b"})])
        self.assertIn("('R1', 3, '%s', 'b', null)" % ASSET, sql)

    def test_aspas_nao_partem_o_sql(self):
        sql = VS.sql_de_registo("R'1", [(0, {"VIDEO_IDENTITY": "YOUTUBE:AbCdEfGhIjK", "VIDEO_IDENTITY_BASIS": "o 'id'"})])
        self.assertIn("'R''1'", sql)
        self.assertIn("'o ''id'''", sql)


class V2AMesmaRegraNosTresSitios(unittest.TestCase):
    def test_lei_escritor_e_proposta_aceitam_o_mesmo_formato(self):
        with open(PROPOSTA, encoding="utf-8") as f:
            sql = f.read()
        regra = re.search(r"video_identity ~ '([^']+)'", sql).group(1)
        for ok in ("YOUTUBE:AbCdEfGhIjK", ASSET):
            self.assertTrue(re.match(regra, ok) and VS.RE_IDENTIDADE.match(ok), ok)
        for mau in ("NAO SEI", "YOUTUBE:curto", "LINKEDIN:urn:li:activity:7507360685509607424"):
            self.assertFalse(re.match(regra, mau), mau)
            self.assertFalse(VS.RE_IDENTIDADE.match(mau), mau)
        self.assertEqual(IV.identidade({"PLATFORM": "YOUTUBE", "NATIVE_ID": "AbCdEfGhIjK"})[0], "YOUTUBE:AbCdEfGhIjK")

    def test_a_proposta_nao_toca_na_sala_nem_esta_nas_migracoes(self):
        with open(PROPOSTA, encoding="utf-8") as f:
            sql = f.read().lower()
        codigo = "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--"))
        self.assertNotIn("alter table public.sala_de_espera ", codigo)
        self.assertNotIn("037_", " ".join(os.listdir(os.path.join(RAIZ, "supabase", "migrations"))))


if __name__ == "__main__":
    unittest.main()
