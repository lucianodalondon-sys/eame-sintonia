# -*- coding: utf-8 -*-
"""Q1 — a quarentena do NAO SEI do detector (D11, opcao C), na porta de admissao.

    UNKNOWN NAO E NEVER. QUARENTENA NAO E DESCARTE. SAI SO POR REGRA PROVADA OU HUMANO.

Sem rede, sem banco; o livro de decisoes e o registo humano vivem em pasta temporaria.
"""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
import orquestrador as ORQ  # noqa: E402
from coleta import executor_texto_de_html as HTMLX  # noqa: E402

SHA = "a" * 64


def _item(retrato=None, **extra):
    """Um DERIVED de HTML como o orquestrador o entrega a porta."""
    e = {"TEXTO": "Difesa integrata del pomodoro: peronospora, larva e fungo nel campo.",
         "SOURCE_ID": "IT-T3-002", "PARENT_SHA256": SHA, "DERIVED_ARTIFACT_ID": 77,
         "RAW_ASSET_ID": 5, "CAPTURED_AT": "2026-09-22T10:00:00Z"}
    if retrato is not None:
        e["RETRATO_DO_DETECTOR"] = retrato
    return dict(ORQ.item_documental_para_a_porta(e, source_id="IT-T3-002"), **extra)


def _retrato(kind):
    return {"CAPA_OU_MATERIA": kind, "HTML_KIND": {"MATERIA_PROVAVEL": "CONTENT",
                                                    "CAPA_PROVAVEL": "NAVIGATION"}.get(kind, "MIXED"),
            "LINKS": 40, "NON_WHITESPACE_CHARACTERS": 2000, "PARAGRAPH_CHARACTERS": 300}


class Isolado(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        d = Path(self.tmp.name)
        self._antes = (adm.LIVRO, adm.QUARENTENA_HUMANA)
        self.addCleanup(self._repor)
        adm.LIVRO = d / "LIVRO.json"
        adm.QUARENTENA_HUMANA = d / "HUMANA.jsonl"

    def _repor(self):
        adm.LIVRO, adm.QUARENTENA_HUMANA = self._antes

    def humano(self, veredito, sha=SHA):
        with adm.QUARENTENA_HUMANA.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"SHA256": sha, "VEREDITO": veredito, "QUEM": "teste",
                                "QUANDO": "2026-09-23T00:00:00Z", "PORQUE": "li"}) + "\n")

    def materia(self, d):
        return d.evidencia["portoes"]["materia"]


class Porta(Isolado):
    def test_nao_sei_do_detector_fica_em_quarentena_e_nao_entra(self):
        d = adm.decidir(_item(_retrato("NAO_SEI")), "T3")
        self.assertEqual((adm.NAO_SEI, "materia"), (d.resultado, d.regra))
        self.assertEqual(adm.QUARENTENA, d.evidencia["estado"])
        self.assertNotEqual(adm.SIM, d.resultado)          # nunca entra na Sala

    def test_quarentena_nao_e_descarte(self):
        d = adm.decidir(_item(_retrato("NAO_SEI")), "T3")
        self.assertNotEqual(adm.NAO, d.resultado)
        adm.escrever([d])
        linha = json.loads(adm.LIVRO.read_text(encoding="utf-8"))["DECISOES"][-1]
        self.assertEqual(adm.QUARENTENA, linha["evidencia"]["estado"])
        self.assertEqual(SHA, linha["evidencia"]["pagina_sha256"])
        self.assertEqual("NAO_SEI", linha["evidencia"]["retrato"]["CAPA_OU_MATERIA"])

    def test_materia_segue_para_as_perguntas_seguintes(self):
        d = adm.decidir(_item(_retrato("MATERIA_PROVAVEL")), "T3")
        self.assertEqual(adm.SIM, self.materia(d)["resultado"])
        self.assertNotEqual("materia", d.regra)

    def test_capa_e_nao_com_a_evidencia(self):
        d = adm.decidir(_item(_retrato("CAPA_PROVAVEL")), "T3")
        self.assertEqual((adm.NAO, "materia"), (d.resultado, d.regra))

    def test_sem_retrato_a_pergunta_nao_se_aplica_e_o_pdf_nao_muda(self):
        d = adm.decidir(_item(None), "T3")
        self.assertEqual(adm.SIM, self.materia(d)["resultado"])
        self.assertNotIn("retrato_do_detector", _item(None))

    def test_a_versao_da_regra_subiu(self):
        # Q1 subiu-a para 6; a V1A para 7. So pode subir.
        self.assertGreaterEqual(int(adm.VERSAO_DA_REGRA), 6)


class Saidas(Isolado):
    def test_sem_regra_nova_nem_humano_continua_em_quarentena(self):
        for _ in range(3):
            self.assertEqual(adm.NAO_SEI, adm.decidir(_item(_retrato("NAO_SEI")), "T3").resultado)

    def test_saida_por_regra_provada_no_replay(self):
        # o detector (dono LD3) foi mudado e provado; no replay o retrato ja diz materia
        self.assertEqual(adm.SIM, self.materia(adm.decidir(_item(_retrato("MATERIA_PROVAVEL")), "T3"))["resultado"])

    def test_saida_por_decisao_humana_registada_materia(self):
        self.humano("MATERIA")
        d = adm.decidir(_item(_retrato("NAO_SEI")), "T3")
        self.assertEqual(adm.SIM, self.materia(d)["resultado"])
        self.assertEqual("teste", self.materia(d)["decisao_humana"]["QUEM"])

    def test_decisao_humana_capa(self):
        self.humano("CAPA")
        self.assertEqual(adm.NAO, adm.decidir(_item(_retrato("NAO_SEI")), "T3").resultado)

    def test_decisao_humana_de_outra_pagina_nao_liberta_esta(self):
        self.humano("MATERIA", sha="b" * 64)
        self.assertEqual(adm.NAO_SEI, adm.decidir(_item(_retrato("NAO_SEI")), "T3").resultado)

    def test_ao_sair_passa_pela_admission_normal(self):
        self.humano("MATERIA")
        d = adm.decidir(_item(_retrato("NAO_SEI"), texto="texto sem nenhuma palavra do universo"), "T3")
        self.assertNotEqual(adm.SIM, d.resultado)          # a regua do universo continua a mandar
        self.assertNotEqual("materia", d.regra)


class Painel(unittest.TestCase):
    AGORA = datetime(2026, 10, 30, tzinfo=timezone.utc)

    def _d(self, item, dias, q=True):
        return {"item": item, "universo": "T3", "resultado": "NAO_SEI" if q else "SIM",
                "regra": "materia" if q else "universo", "quando": (self.AGORA - timedelta(days=dias)).isoformat(),
                "evidencia": {"estado": adm.QUARENTENA} if q else {}}

    def test_tamanho_idade_e_saidas(self):
        p = adm.painel_da_quarentena({"DECISOES": [self._d("a", 5), self._d("b", 3), self._d("b", 1, q=False)]},
                                     self.AGORA)
        self.assertEqual((1, 5.0, 1, False), (p["TAMANHO"], p["MAIS_ANTIGA_DIAS"], p["SAIDAS_NA_JANELA"], p["ALARME"]))

    def test_alarme_quando_cresce_sem_nada_sair(self):
        p = adm.painel_da_quarentena({"DECISOES": [self._d("a", 20), self._d("b", 2)]}, self.AGORA)
        self.assertTrue(p["ALARME"])
        self.assertIn("SEM_SAIDAS", p["PORQUE"][0])

    def test_sem_alarme_se_alguma_saiu_na_janela(self):
        p = adm.painel_da_quarentena({"DECISOES": [self._d("a", 20), self._d("b", 20), self._d("b", 3, q=False)]},
                                     self.AGORA)
        self.assertFalse(p["ALARME"])

    def test_alarme_de_tamanho(self):
        ds = [self._d("i%d" % i, 1) for i in range(adm.QUARENTENA_TAMANHO_MAXIMO + 1)]
        self.assertIn("TAMANHO", adm.painel_da_quarentena({"DECISOES": ds}, self.AGORA)["PORQUE"][0])

    def test_reentrada_conta_a_idade_de_novo(self):
        p = adm.painel_da_quarentena({"DECISOES": [self._d("a", 30), self._d("a", 20, q=False), self._d("a", 2)]},
                                     self.AGORA)
        self.assertEqual(2.0, p["MAIS_ANTIGA_DIAS"])


class Transporte(unittest.TestCase):
    def test_o_derivador_de_html_entrega_o_retrato(self):
        r = HTMLX._retrato(b"<html><body>" + b"<a href='/x'>x</a>" * 50 + b"</body></html>")
        self.assertEqual("CAPA_PROVAVEL", r["CAPA_OU_MATERIA"])

    def test_o_item_da_porta_leva_o_retrato(self):
        self.assertEqual("NAO_SEI", _item(_retrato("NAO_SEI"))["retrato_do_detector"]["CAPA_OU_MATERIA"])

    def test_derivar_um_do_html_devolve_o_retrato(self):
        from unittest import mock
        import guarda.preservar_derivado as PD
        html = (b"<html><body><h1>Difesa</h1><p>" + b"testo lungo della notizia " * 60
                + b"</p></body></html>")
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "p.html"
            f.write_bytes(html)
            with mock.patch.object(PD, "preservar_derivado", return_value={"ESTADO": "INSERTED"}):
                r = HTMLX.derivar_um(5, str(f), armazem=None, memoria=None)
        self.assertEqual("MATERIA_PROVAVEL", r["RETRATO_DO_DETECTOR"]["CAPA_OU_MATERIA"])

    def test_a_derivacao_forward_transporta_o_retrato(self):
        from coleta import derivacao_forward as DF
        ret = _retrato("NAO_SEI")

        def falso(raw_id, caminho, armazem, memoria, **kw):
            return {"ESTADO": "INSERTED", "LINHA_ESCRITA": {"id": 1, "storage_path": "x"},
                    "RETRATO_DO_DETECTOR": ret}
        r = DF.correr([{"RAW_ASSET_ID": 5, "PDF": "p.html", "MEDIA_TYPE": "text/html"}],
                      banco_do_rastro=None, run_id="R", armazem=None, memoria=None, derivar=falso)
        self.assertEqual(ret, r["RESULTADOS"][0]["RETRATO_DO_DETECTOR"])

    def test_a_estruturacao_transporta_o_retrato(self):
        from unittest import mock
        ret = _retrato("NAO_SEI")

        class Armazem:
            def ler(self, caminho):
                return b"texto derivado"
        der = {"RESULTADOS": [{"PORTA": "PASSED", "RAW_ASSET_ID": 5, "SOURCE_ID": "IT-T3-002",
                               "LINHA": {"id": 9, "storage_path": "x", "parent_sha256": SHA},
                               "RETRATO_DO_DETECTOR": ret}]}
        with mock.patch.object(ORQ.pdoc, "preservar_documento",
                               return_value={"ESTADO": ORQ.pdoc.INSERTED}):
            e = ORQ.pela_estruturacao(der, run_id="R", armazem=Armazem(), memoria=None)
        self.assertEqual(ret, e["ESTRUTURADOS"][0]["RETRATO_DO_DETECTOR"])


if __name__ == "__main__":
    unittest.main()
