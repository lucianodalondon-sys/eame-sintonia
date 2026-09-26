# -*- coding: utf-8 -*-
"""LEGACY-99 A+B · o Curator aprende o contrato que o coletor ja executa.

Sem rede e sem livros reais: a tabela e o curador sao ficheiros temporarios, o
portao e a promocao sao dublos, o `remedir` e um dublo. O `buscar` do canario e
trocado por paginas literais.
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
import canario as CAN             # noqa: E402
import worker as W                # noqa: E402
import escrever_contratos as EC   # noqa: E402

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
        yt = I.contrato_importado(YT_LINHA, YT_CURADOR, PROMO, "t", identidade=IDENT)
        self.assertEqual(YT_CURADOR["IDENTITY"], yt["IDENTITY"])

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
        # linha sem OUTPUT_TYPE: o VIDEO_METADATA do curador ficava — outro contrato
        linha = {k: v for k, v in YT_LINHA.items() if k != "OUTPUT_TYPE"}
        with self.assertRaises(I.ImportacaoInvalida):
            I.contrato_importado(linha, YT_CURADOR, PROMO, "t")

    def test_pdf_nao_se_importa(self):
        with self.assertRaises(I.ImportacaoInvalida):
            I.contrato_importado(PDF, None, PROMO, "t", identidade=IDENT)

    def test_youtube_troca_a_rota_e_guarda_o_resto_e_a_anterior(self):
        c = I.contrato_importado(YT_LINHA, YT_CURADOR, PROMO, "t")
        self.assertEqual("CUSTOM_ADAPTER", c["ACQUISITION"]["STRATEGY"])
        self.assertNotIn("FEED_URL", c["ACQUISITION"])
        self.assertEqual("SOURCE_ID != CHANNEL_ID", c["LEI_DA_IDENTIDADE"])
        self.assertEqual(YT_CURADOR["ACQUISITION"], c["PROVENIENCIA_DO_CONTRATO"]["ACQUISITION_ANTERIOR_NO_CURATOR"])
        self.assertEqual(SHA.do_contrato(YT_LINHA), SHA.do_contrato(c))


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

    def test_youtube_do_feed_importa_a_rota_do_canal(self):
        p = self.planear([YT_CURADOR], [YT_LINHA], {"IT-T10-017": "READY_LEGACY"})
        self.assertEqual("YOUTUBE_FEED_PARA_CANAL", p["IMPORTA"][0]["CASO"])

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
        self.tab.write_text(json.dumps({"FONTES": [HTML, YT_LINHA]}), encoding="utf-8")
        self.ps = [mock.patch.object(I, "CURATOR", self.cur), mock.patch.object(I, "TABELA", self.tab),
                   mock.patch.object(I, "planear", return_value={"IMPORTA": [
                       {"SOURCE_ID": "IT-T5-006", "PROMOCAO": PROMO}, {"SOURCE_ID": "IT-T10-017", "PROMOCAO": PROMO}],
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
            r = I.aplicar(["IT-T5-006", "IT-T10-017"], quando="t",
                          remedir_fn=lambda ids: (chamadas.append(list(ids)), [{"FEITO": True} for _ in ids])[1],
                          identidades_fn=lambda ids: (self.assertEqual(["IT-T5-006"], ids), {"IT-T5-006": IDENT})[1])
        self.assertEqual([["IT-T5-006", "IT-T10-017"]], chamadas)
        self.assertEqual(2, r["REMEDIDAS"])
        fontes = {c["SOURCE_ID"]: c for c in json.loads(self.cur.read_text(encoding="utf-8"))["FONTES"]}
        self.assertEqual(HTML["ACQUISITION"], fontes["IT-T5-006"]["ACQUISITION"])
        self.assertEqual(IDENT, fontes["IT-T5-006"]["IDENTITY"])
        self.assertEqual("CUSTOM_ADAPTER", fontes["IT-T10-017"]["ACQUISITION"]["STRATEGY"])
        self.assertEqual(2, len(fontes))
        self.assertFalse(Path(self.d.name, "cur.json.tmp").exists())

    def test_fora_do_plano_recusa_e_nao_escreve(self):
        antes = self.cur.read_bytes()
        with self.assertRaises(I.ImportacaoInvalida):
            I.aplicar(["IT-T9-999"], remedir_fn=lambda ids: self.fail("nao devia remedir"))
        self.assertEqual(antes, self.cur.read_bytes())

    def test_o_remedir_por_omissao_e_o_de_ready_split(self):
        with mock.patch.object(RS, "remedir", return_value=[{"FEITO": True}]) as rm:
            I.aplicar(["IT-T5-006"], quando="t", identidades_fn=lambda ids: {"IT-T5-006": IDENT})
        self.assertIn("importar nunca promove", rm.call_args.kwargs["motivo"])


class CanalYouTube(unittest.TestCase):
    CAN_CONTRATO = {"SOURCE_ID": "IT-T10-017", "IDENTITY": {"DOCUMENT_ID": "IT-T10-017:YT:{video.videoId}"},
                    "ACQUISITION": YT_LINHA["ACQUISITION"]}

    def canario(self, st, corpo):
        with mock.patch.object(CAN, "buscar", return_value=(st, corpo, "" if st == 200 else "HTTP %d" % st)) as b:
            r = CAN.canario_youtube_canal(self.CAN_CONTRATO)
        self.assertEqual("https://www.youtube.com/channel/%s/videos" % CID, b.call_args.args[0])
        return r

    def test_canal_certo_com_videos_passa(self):
        r = self.canario(200, ('{"channelId":"%s"} {"videoId":"abcdefghijk"} {"videoId":"bbbbbbbbbbb"}' % CID).encode())
        self.assertTrue(r["PASS"])
        self.assertEqual("IT-T10-017:YT:abcdefghijk", r["DOCUMENT_ID"])
        self.assertEqual(2, r["ITENS_NO_CANAL"])

    def test_outro_canal_e_route_failure(self):
        r = self.canario(200, b'{"channelId":"UCoutro"} {"videoId":"abcdefghijk"}')
        self.assertEqual((False, "ROUTE_FAILURE"), (r["PASS"], r["CLASSE"]))

    def test_sem_videos_e_empty_list(self):
        r = self.canario(200, ('{"channelId":"%s"}' % CID).encode())
        self.assertEqual((False, "SOURCE_FAILURE"), (r["PASS"], r["CLASSE"]))

    def test_429_nao_e_falha_da_fonte(self):
        r = self.canario(429, b"")
        self.assertEqual((False, 429), (r["PASS"], r["HTTP"]))

    def test_a_rota_do_contrato_e_a_do_canal(self):
        self.assertEqual("https://www.youtube.com/channel/%s/videos" % CID, CAN.url_da_rota(YT_LINHA["ACQUISITION"]))
        self.assertEqual(YT_CURADOR["ACQUISITION"]["FEED_URL"], CAN.url_da_rota(YT_CURADOR["ACQUISITION"]))
        self.assertEqual(HTML["ACQUISITION"]["INDEX_URL"], CAN.url_da_rota(HTML["ACQUISITION"]))

    @unittest.skip("DA-15/D67 (onda3-pacote-v2): o B fica INERTE - a producao manda na rota YouTube (Scrap/SOC2) e no molde novo; o contrario e provado em tests/test_onda3_b_inerte.py")
    def test_o_validate_route_pergunta_ao_robots_pelo_canal_e_nao_pelo_feed(self):
        perguntas = []
        with mock.patch.object(W.GATE, "robots_de", return_value=(object(), "lido")), \
             mock.patch.object(W.GATE, "permitido", side_effect=lambda u, rp: (perguntas.append(u), "/feeds/" not in u)[1]):
            ok, _ = W.etapa_validate_route("IT-T10-017", {"ACQUISITION": YT_LINHA["ACQUISITION"]})
            bloqueado, _ = W.etapa_validate_route("IT-T10-017", YT_CURADOR)
        self.assertEqual(("OK", "BLOCK"), (ok, bloqueado))
        self.assertIn("https://www.youtube.com/channel/%s/videos" % CID, perguntas)

    def test_o_canario_do_worker_usa_o_do_canal(self):
        with mock.patch.object(CAN, "canario_youtube_canal", return_value={"PASS": True}) as cc, \
             mock.patch.object(CAN, "canario_html", side_effect=AssertionError("nao e html")):
            r, _ = W.etapa_canary("IT-T10-017", dict(self.CAN_CONTRATO))
        self.assertEqual("OK", r)
        cc.assert_called_once()

    @unittest.skip("DA-15/D67 (onda3-pacote-v2): o B fica INERTE - a producao manda na rota YouTube (Scrap/SOC2) e no molde novo; o contrario e provado em tests/test_onda3_b_inerte.py")
    def test_o_molde_novo_nasce_na_rota_do_canal_igual_ao_coletor(self):
        c = EC.contrato_youtube({"SOURCE_ID": "IT-T10-017", "NOME": "Canale", "TERRITORY": "T10",
                                 "URL": "https://www.youtube.com/@x"}, {}, CID)
        self.assertEqual(YT_LINHA["ACQUISITION"], c["ACQUISITION"])
        self.assertEqual(SHA.do_contrato(YT_LINHA), SHA.do_contrato(c))
        self.assertNotIn("feeds/videos.xml", json.dumps(c))


if __name__ == "__main__":
    unittest.main()
