# -*- coding: utf-8 -*-
"""D1 + D14 — o detector que chama CAPA a noticias, e a opcao C da D14 (desligada).

    FALSE_LISTING_AS_ARTICLE NAO SOBE NEM +1. SEM MEDICAO, O GANHO E NAO SEI.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "medidas"))
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
import orquestrador as ORQ  # noqa: E402

SHA = "c" * 64
CAPA = {"CAPA_OU_MATERIA": "CAPA_PROVAVEL", "HTML_KIND": "NAVIGATION", "LINKS": 300,
        "NON_WHITESPACE_CHARACTERS": 3000, "PARAGRAPH_CHARACTERS": 200}


def _item():
    e = {"TEXTO": "Difesa integrata del pomodoro: peronospora, larva e fungo nel campo.",
         "SOURCE_ID": "IT-T7-033", "PARENT_SHA256": SHA, "DERIVED_ARTIFACT_ID": 88,
         "RAW_ASSET_ID": 6, "CAPTURED_AT": "2026-09-22T10:00:00Z", "RETRATO_DO_DETECTOR": CAPA}
    return ORQ.item_documental_para_a_porta(e, source_id="IT-T7-033")


class Isolado(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        antes = (adm.LIVRO, adm.QUARENTENA_HUMANA, adm.D14_C_LIGADA)
        self.addCleanup(lambda: setattr(adm, "LIVRO", antes[0]) or setattr(adm, "QUARENTENA_HUMANA", antes[1])
                        or setattr(adm, "D14_C_LIGADA", antes[2]))
        adm.LIVRO = Path(self.tmp.name) / "LIVRO.json"
        adm.QUARENTENA_HUMANA = Path(self.tmp.name) / "H.jsonl"


class OpcaoC(Isolado):
    def test_desligada_por_omissao_ate_medir(self):
        self.assertFalse(adm.D14_C_LIGADA)
        with mock.patch.object(adm, "_fonte_bem_configurada", return_value=True):
            self.assertEqual(adm.NAO, adm.decidir(_item(), "T7").resultado)

    def test_ligada_capa_de_fonte_bem_configurada_vai_a_quarentena(self):
        adm.D14_C_LIGADA = True
        with mock.patch.object(adm, "_fonte_bem_configurada", return_value=True):
            d = adm.decidir(_item(), "T7")
        self.assertEqual((adm.NAO_SEI, adm.QUARENTENA), (d.resultado, d.evidencia["estado"]))

    def test_ligada_capa_de_fonte_mal_configurada_continua_barrada(self):
        adm.D14_C_LIGADA = True
        with mock.patch.object(adm, "_fonte_bem_configurada", return_value=False):
            self.assertEqual(adm.NAO, adm.decidir(_item(), "T7").resultado)

    def test_a_capa_barrada_guarda_fonte_e_observacao_para_voltar_a_porta(self):
        with mock.patch.object(adm, "_fonte_bem_configurada", return_value=False):
            d = adm.decidir(_item(), "T7")
        self.assertEqual(("IT-T7-033", 6, SHA), (d.evidencia["fonte"], d.evidencia["raw_asset_id"],
                                                d.evidencia["pagina_sha256"]))


class PainelD14(unittest.TestCase):
    def test_barradas_e_retidas_por_fonte_bem_e_mal(self):
        def d(i, fonte, q):
            return {"item": i, "universo": "T7", "regra": "materia", "quando": "2026-09-23T00:00:00+00:00",
                    "resultado": "NAO_SEI" if q else "NAO",
                    "evidencia": dict({"fonte": fonte}, **({"estado": adm.QUARENTENA} if q else {}))}
        livro = {"DECISOES": [d("a", "IT-T7-033", False), d("b", "IT-T2-030", False),
                              d("c", "IT-T7-033", True), d("d", "IT-T2-030", True)]}
        with mock.patch.object(adm, "_fonte_bem_configurada", side_effect=lambda s: s == "IT-T7-033"):
            p = adm.painel_da_quarentena(livro)
        self.assertEqual({"BARRADAS_FONTE_BEM": 1, "BARRADAS_FONTE_MAL": 1,
                          "RETIDAS_FONTE_BEM": 1, "RETIDAS_FONTE_MAL": 1}, p["D14_BARRADAS_VS_RETIDAS"])


class ValidacaoCega(unittest.TestCase):
    CEGA = json.loads((RAIZ / "medidas" / "D1-VALIDACAO-CEGA-V1.json").read_text(encoding="utf-8"))

    def test_foi_sorteada_sem_as_ja_vistas_e_com_a_semente_escrita(self):
        self.assertEqual(23, len(self.CEGA["IDS"]))
        self.assertFalse(set(self.CEGA["IDS"]) & set(self.CEGA["EXCLUIDAS_POR_JA_VISTAS"]))
        self.assertTrue(self.CEGA["SEMENTE"])

    @unittest.skipUnless((Path.home() / "ld2-controlo").is_dir() and (Path.home() / "detector-capa-gabarito").is_dir(),
                         "bytes dos gabaritos fora do Git e ausentes nesta maquina")
    def test_nenhuma_proposta_faz_uma_capa_passar_a_materia(self):
        import medir_detector_moldura as M
        for nome, f in M.PROPOSTAS.items():
            for fatia, v in M.medir(f).items():
                self.assertLessEqual(v["DEPOIS"]["FALSE_LISTING_AS_ARTICLE"],
                                     v["ANTES"]["FALSE_LISTING_AS_ARTICLE"], (nome, fatia))

    def test_o_detector_nao_foi_mudado(self):
        texto = (RAIZ / "curadoria" / "retrato_html.py").read_text(encoding="utf-8")
        self.assertNotIn("_MOLDURA", texto, "D1: a proposta NAO foi aplicada; o detector fica como estava")


if __name__ == "__main__":
    unittest.main()
