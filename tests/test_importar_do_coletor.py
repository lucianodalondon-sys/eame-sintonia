# -*- coding: utf-8 -*-
"""LEGACY-99 A · o Curator aprende o contrato HTML que o coletor ja executa.

O canal YouTube NAO se importa daqui: a rota e do Scrap (rota_do_scrap_youtube).

Sem rede e sem livros reais: a tabela e o curador sao ficheiros temporarios, o
portao e a promocao sao dublos, o `remedir` e um dublo.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import importar_do_coletor as I   # noqa: E402
import sha_do_contrato as SHA     # noqa: E402
import collection_gate as CG      # noqa: E402
import ready_split as RS          # noqa: E402

HTML = {"SOURCE_ID": "IT-T5-006", "OWNER": "CNR", "NAME": "CNR", "TERRITORY": "T5", "BATCH_ID": "LOTE-X",
        "OUTPUT_TYPE": "HTML", "CANONICAL_ENTRY_URL": "https://www.cnr.it/it/news",
        "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL", "INDEX_URL": "https://www.cnr.it/it/news",
                        "LINK_PATTERN": "^https?://(www\\.)?cnr\\.it/it/news/\\d+/.+$", "MAX_TARGETS": 5}}
PDF = {"SOURCE_ID": "IT-T4-009", "OUTPUT_TYPE": "PDF",
       "ACQUISITION": {"STRATEGY": "STATIC_ENDPOINT", "URL": "https://x.it/a.pdf"}}
CID = "UCfdN2DQZBfZo-7VgBqotYuQ"
YT_LINHA = {"SOURCE_ID": "IT-T10-017", "OWNER": "Canale", "NAME": "Canale", "TERRITORY": "T10",
            "BATCH_ID": "LOTE-YOUTUBE-CANAL", "OUTPUT_TYPE": "HTML",
            "ACQUISITION": {"STRATEGY": "CUSTOM_ADAPTER", "ADAPTER_ID": "CANAL_PUBLICO_YOUTUBE_V1",
                            "CHANNEL_ID": CID, "MAX_TARGETS": 15}}
YT_CURADOR = {"SOURCE_ID": "IT-T10-017", "BATCH_ID": "LOTE-YOUTUBE-FEED", "OUTPUT_TYPE": "VIDEO_METADATA",
              "LEI_DA_IDENTIDADE": "SOURCE_ID != CHANNEL_ID",
              "IDENTITY": {"DOCUMENT_ID": "IT-T10-017:YT:{video.videoId}"},
              "ACQUISITION": {"STRATEGY": "YOUTUBE_CHANNEL_FEED", "CHANNEL_ID": CID,
                              "FEED_URL": "https://www.youtube.com/feeds/videos.xml?channel_id=" + CID,
                              "MAX_TARGETS": 15}}
PROMO = {"OBSERVED_AT": "2026-09-10T00:00:00+00:00", "EVIDENCE_REF": "EV-1"}
IDENT = {"STRATEGY": "CONTENT_CAPTURE", "DOCUMENT_ID": "IT-T5-006:URL:{doc.1}"}


class ContratoImportado(unittest.TestCase):
    def test_sem_identidade_nao_se_importa(self):
        # o defeito que o ensaio apanhou: a linha nao traz IDENTITY e o canario precisa dela
        with self.assertRaises(I.ImportacaoInvalida):
            I.contrato_importado(HTML, None, PROMO, "t")

    def test_a_identidade_gerada_pelo_coletor_entra_e_a_do_curador_fica(self):
        self.assertEqual(IDENT, I.contrato_importado(HTML, None, PROMO, "t", identidade=IDENT)["IDENTITY"])
        antiga = dict(HTML, IDENTITY={"DOCUMENT_ID": "IT-T5-006:URL:{doc.0}"})
        c = I.contrato_importado(HTML, antiga, PROMO, "t", identidade=IDENT)
        self.assertEqual(antiga["IDENTITY"], c["IDENTITY"])

    def test_a_aquisicao_e_a_da_linha_byte_a_byte(self):
        c = I.contrato_importado(HTML, None, PROMO, "2026-09-25T00:00:00+00:00", identidade=IDENT)
        self.assertEqual(HTML["ACQUISITION"], c["ACQUISITION"])
        self.assertEqual(SHA.do_contrato(HTML), SHA.do_contrato(c))

    def test_proveniencia_separada_da_aquisicao_historica(self):
        c = I.contrato_importado(HTML, None, PROMO, "2026-09-25T00:00:00+00:00", identidade=IDENT)
        p, h = c["PROVENIENCIA_DO_CONTRATO"], c["AQUISICAO_HISTORICA"]
        self.assertEqual("IMPORTADO_DO_COLETOR", p["ORIGEM"])
        self.assertEqual(SHA.do_contrato(HTML), p["SHA256_DA_LINHA"])
        self.assertEqual("2026-09-25T00:00:00+00:00", p["IMPORTADO_EM"])
        self.assertIs(False, h["PROVADA"])
        self.assertEqual("2026-09-10T00:00:00+00:00", h["PROMOVIDA_PELA_REGUA_ANTIGA_EM"])
        self.assertNotIn("IMPORTADO_EM", h)
        self.assertIn("APLICADO_EM", c["CONTRATO_UNICO"])

    def test_se_sobrar_algo_do_contrato_antigo_na_impressao_recusa(self):
        # linha HTML sem OUTPUT_TYPE: o PDF que o curador tinha ficava — outro contrato
        linha = {k: v for k, v in HTML.items() if k != "OUTPUT_TYPE"}
        with self.assertRaises(I.ImportacaoInvalida):
            I.contrato_importado(linha, dict(HTML, OUTPUT_TYPE="PDF"), PROMO, "t", identidade=IDENT)

    def test_pdf_nao_se_importa(self):
        with self.assertRaises(I.ImportacaoInvalida):
            I.contrato_importado(PDF, None, PROMO, "t", identidade=IDENT)

    def test_canal_youtube_nao_se_importa_nem_pela_linha_nem_pelo_curador(self):
        # a rota do canal e do Scrap: a linha do coletor aponta um adapter JS que nao existe
        for linha, atual in ((YT_LINHA, None), (YT_LINHA, YT_CURADOR),
                             (dict(HTML, SOURCE_ID="IT-T10-017"), YT_CURADOR)):
            with self.subTest(atual=bool(atual)), self.assertRaises(I.ImportacaoInvalida):
                I.contrato_importado(linha, atual, PROMO, "t", identidade=IDENT)


class Plano(unittest.TestCase):
    def planear(self, contratos, tabela, motivo, estado="READY_FOR_COLLECTION"):
        ids = sorted(set(motivo))
        ctx = {"livro": {"TRANSICOES": [{"SOURCE_ID": s, "NEW_STATE": estado} for s in ids]},
               "contratos": {c["SOURCE_ID"]: c for c in contratos}}
        with mock.patch.object(CG, "avaliar", side_effect=lambda s, **k: {"MOTIVO": motivo[s]}), \
             mock.patch.object(RS, "ultima_promocao", return_value=PROMO):
            return I.planear(ctx=ctx, tabela={l["SOURCE_ID"]: l for l in tabela})

    def test_sem_contrato_no_curador_com_linha_html_importa(self):
        p = self.planear([], [HTML], {"IT-T5-006": "READY_LEGACY"})
        self.assertEqual([("IT-T5-006", "SEM_CONTRATO_NO_CURATOR")], [(x["SOURCE_ID"], x["CASO"]) for x in p["IMPORTA"]])

    def test_youtube_nunca_se_importa_da_tabela(self):
        for contratos in ([YT_CURADOR], []):
            with self.subTest(no_curador=bool(contratos)):
                p = self.planear(contratos, [YT_LINHA], {"IT-T10-017": "READY_LEGACY"})
                self.assertEqual([], p["IMPORTA"])
                ditos = p["FICA"] + p["PELO_SCRAP"]
                self.assertEqual(1, len(ditos))
                self.assertTrue(ditos[0]["PORQUE"].startswith("ROTA_DO_SCRAP"))

    def test_so_case_e_pdf_ficam_com_o_nome(self):
        p = self.planear([], [PDF], {"IT-T2-001": "READY_LEGACY", "IT-T4-009": "READY_LEGACY"})
        self.assertEqual([], p["IMPORTA"])
        porque = {f["SOURCE_ID"]: f["PORQUE"] for f in p["FICA"]}
        self.assertTrue(porque["IT-T2-001"].startswith("SO_CASE"))
        self.assertTrue(porque["IT-T4-009"].startswith("CANARIO_NAO_PROVA"))

    def test_so_ready_legacy(self):
        p = self.planear([], [HTML], {"IT-T5-006": "ELIGIBLE"})
        self.assertEqual(([], []), (p["IMPORTA"], p["FICA"]))

    def test_quem_ja_tem_contrato_html_no_curador_nao_se_toca(self):
        p = self.planear([dict(HTML)], [HTML], {"IT-T5-006": "READY_LEGACY"})
        self.assertEqual([], p["IMPORTA"])


class Aplicar(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.cur = Path(self.d.name, "cur.json")
        self.tab = Path(self.d.name, "tab.json")
        self.cur.write_text(json.dumps({"FONTES": [YT_CURADOR]}), encoding="utf-8")
        self.cur_antes = self.cur.read_bytes()
        self.tab.write_text(json.dumps({"FONTES": [HTML, YT_LINHA]}), encoding="utf-8")
        self.ps = [mock.patch.object(I, "CURATOR", self.cur), mock.patch.object(I, "TABELA", self.tab),
                   mock.patch.object(I, "planear", return_value={"IMPORTA": [
                       {"SOURCE_ID": "IT-T5-006", "PROMOCAO": PROMO}],
                       "FICA": []})]
        for p in self.ps:
            p.start()

    def tearDown(self):
        for p in self.ps:
            p.stop()
        self.d.cleanup()

    def test_escreve_e_manda_ao_caminho_canonico_nunca_promove(self):
        chamadas = []
        import lifecycle as LC
        with mock.patch.object(LC, "registar", side_effect=AssertionError("importar nao mexe no livro")):
            r = I.aplicar(["IT-T5-006"], quando="t",
                          remedir_fn=lambda ids: (chamadas.append(list(ids)), [{"FEITO": True} for _ in ids])[1],
                          identidades_fn=lambda ids: (self.assertEqual(["IT-T5-006"], ids), {"IT-T5-006": IDENT})[1])
        self.assertEqual([["IT-T5-006"]], chamadas)
        self.assertEqual(1, r["REMEDIDAS"])
        fontes = {c["SOURCE_ID"]: c for c in json.loads(self.cur.read_text(encoding="utf-8"))["FONTES"]}
        self.assertEqual(HTML["ACQUISITION"], fontes["IT-T5-006"]["ACQUISITION"])
        self.assertEqual(IDENT, fontes["IT-T5-006"]["IDENTITY"])
        self.assertEqual(YT_CURADOR, fontes["IT-T10-017"])     # o canal nao se tocou
        self.assertEqual(2, len(fontes))
        self.assertFalse(Path(self.d.name, "cur.json.tmp").exists())

    def test_fora_do_plano_recusa_e_nao_escreve(self):
        for ids in (["IT-T9-999"], ["IT-T10-017"], ["IT-T5-006", "IT-T10-017"]):
            with self.subTest(ids=ids), self.assertRaises(I.ImportacaoInvalida):
                I.aplicar(ids, remedir_fn=lambda x: self.fail("nao devia remedir"))
            self.assertEqual(self.cur_antes, self.cur.read_bytes())

    def test_o_remedir_por_omissao_e_o_de_ready_split(self):
        with mock.patch.object(RS, "remedir", return_value=[{"FEITO": True}]) as rm:
            I.aplicar(["IT-T5-006"], quando="t", identidades_fn=lambda ids: {"IT-T5-006": IDENT})
        self.assertIn("importar nunca promove", rm.call_args.kwargs["motivo"])


if __name__ == "__main__":
    unittest.main()
