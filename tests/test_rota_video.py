# -*- coding: utf-8 -*-
"""D53 · a rota VIDEO na regua do Curator, no desenho da D42 (FORMA explicita, regua irma).

Prova minima: pagina publica do video, titulo, data de publicacao, canal. Falta uma =
reprova. Transcricao so quando o Scrap a trouxer: nunca exigida, nunca inventada.
Sem rede: o `buscar` do canario devolve paginas literais.
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import ready_split as RS          # noqa: E402
import validar_contratos as VC    # noqa: E402
import canario as CAN             # noqa: E402
import worker as W                # noqa: E402

CID = "UCfdN2DQZBfZo-7VgBqotYuQ"
VID = "abcdefghijk"
CONTRATO = {"SOURCE_ID": "IT-T10-017", "FORMA": "VIDEO", "OUTPUT_TYPE": "VIDEO",
            "IDENTITY": {"DOCUMENT_ID": "IT-T10-017:YT:{video.videoId}"},
            "ACQUISITION": {"STRATEGY": "CUSTOM_ADAPTER", "ADAPTER_ID": "CANAL_PUBLICO_YOUTUBE_V1",
                            "CHANNEL_ID": CID, "MAX_TARGETS": 15}}
PROMO = {"OBSERVED_AT": "2026-09-25T12:00:00+00:00", "EVIDENCE_REF": "EV-1"}
ITEM = {"URL": "https://www.youtube.com/watch?v=" + VID, "HTTP": 200, "FORMA": "VIDEO",
        "TITULO": "Vendemmia 2026 in Franciacorta", "PUBLICATION_TIME": "2026-09-20T10:00:00-07:00",
        "CANAL": CID, "COLLECTION_TIME": "2026-09-25T11:59:00+00:00", "FACT_TIME": "UNKNOWN"}


def regua(item=ITEM, contrato=CONTRATO):
    return RS.passos_da_promocao(PROMO, {"DADOS": {"ITEM_ABERTO": item, "DETAIL_ENUMERATED": 12}}, contrato)


class Regua(unittest.TestCase):
    def test_as_quatro_provas_dao_video_v1_e_a_regua_e_corrente(self):
        r = regua()
        self.assertEqual("VIDEO/v1", r["REGUA"])
        self.assertTrue(RS.e_corrente(r["REGUA"]))

    def test_falta_cada_uma_das_quatro_provas_reprova(self):
        faltas = {"PAGINA_DO_VIDEO": {"URL": "https://www.youtube.com/channel/%s/videos" % CID},
                  "TITULO": {"TITULO": ""},
                  "DATA_DE_PUBLICACAO": {"PUBLICATION_TIME": None},
                  "CANAL": {"CANAL": "UCoutrooutrooutrooutroo"}}
        for prova, estraga in faltas.items():
            with self.subTest(prova=prova):
                r = regua(dict(ITEM, **estraga))
                self.assertEqual("LEGACY", r["REGUA"])
                self.assertFalse(r["PASSOS"][prova])
                self.assertIn(prova, r["PORQUE"])

    def test_pagina_do_video_com_http_diferente_de_200_reprova(self):
        self.assertEqual("LEGACY", regua(dict(ITEM, HTTP=429))["REGUA"])

    def test_saida_video_tem_de_ser_explicita(self):
        r = regua(contrato=dict(CONTRATO, OUTPUT_TYPE="HTML"))
        self.assertEqual("LEGACY", r["REGUA"])
        self.assertFalse(r["PASSOS"]["SAIDA_VIDEO"])

    def test_os_tres_tempos_ficam_separados(self):
        info = regua()["INFO"]
        self.assertEqual("2026-09-20T10:00:00-07:00", info["PUBLICATION_TIME"])
        self.assertEqual("UNKNOWN", info["FACT_TIME"])
        self.assertEqual("2026-09-25T11:59:00+00:00", info["COLLECTION_TIME"])

    def test_transcricao_nao_e_exigida_nem_inventada(self):
        r = regua()
        self.assertEqual("VIDEO/v1", r["REGUA"])
        self.assertNotIn("TRANSCRICAO", r["PASSOS"])
        self.assertTrue(r["INFO"]["TRANSCRICAO"].startswith("NAO_TRAZIDA"))
        self.assertEqual("texto do scrap", regua(dict(ITEM, TRANSCRICAO="texto do scrap"))["INFO"]["TRANSCRICAO"])

    def test_sem_forma_video_a_mesma_prova_nao_da_video_v1(self):
        sem_forma = {k: v for k, v in CONTRATO.items() if k != "FORMA"}
        self.assertNotEqual("VIDEO/v1", regua(contrato=sem_forma)["REGUA"])

    def test_a_regua_do_html_nao_mudou(self):
        self.assertEqual({"DETAIL/v1", "PAGINA_BOLETIM/v1", "VIDEO/v1"}, set(RS.REGUAS_CORRENTES))
        self.assertEqual("DETAIL/v1", RS.REGUA_CURRENT)


class Validador(unittest.TestCase):
    def test_contrato_video_completo_passa(self):
        self.assertTrue(VC.form_resolved(CONTRATO)[0])

    def test_video_exige_saida_video_canal_e_identidade_pelo_video(self):
        maus = [dict(CONTRATO, OUTPUT_TYPE="HTML"),
                dict(CONTRATO, ACQUISITION=dict(CONTRATO["ACQUISITION"], CHANNEL_ID="nao-e-canal")),
                dict(CONTRATO, ACQUISITION={"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": "https://x.it"}),
                dict(CONTRATO, IDENTITY={"DOCUMENT_ID": "IT-T10-017:URL:{doc.1}"})]
        for c in maus:
            with self.subTest(c=c.get("OUTPUT_TYPE")):
                self.assertFalse(VC.form_resolved(c)[0])

    def test_video_e_saida_conhecida(self):
        self.assertIn("VIDEO", VC.OUTPUTS)


CANAL_PAGINA = ('{"channelId":"%s"} {"videoId":"%s"} {"videoId":"bbbbbbbbbbb"}' % (CID, VID)).encode()
VIDEO_PAGINA = ('<meta name="title" content="Vendemmia 2026 in Franciacorta">'
                '<meta itemprop="datePublished" content="2026-09-20T10:00:00-07:00">'
                '<meta itemprop="channelId" content="%s">' % CID).encode()


class Canario(unittest.TestCase):
    def correr(self, respostas):
        pedidos = []
        it = iter(respostas)
        with mock.patch.object(CAN, "buscar", side_effect=lambda u: (pedidos.append(u), next(it))[1]):
            r = CAN.canario_video(CONTRATO)
        return r, pedidos

    def test_dois_pedidos_canal_e_video_e_nenhum_de_transcricao(self):
        r, pedidos = self.correr([(200, CANAL_PAGINA, ""), (200, VIDEO_PAGINA, "")])
        self.assertEqual(["https://www.youtube.com/channel/%s/videos" % CID,
                          "https://www.youtube.com/watch?v=" + VID], pedidos)
        self.assertTrue(r["PASS"])
        self.assertEqual("IT-T10-017:YT:" + VID, r["DOCUMENT_ID"])

    def test_a_prova_do_canario_passa_na_regua(self):
        r, _ = self.correr([(200, CANAL_PAGINA, ""), (200, VIDEO_PAGINA, "")])
        self.assertEqual("VIDEO/v1", RS.passos_da_promocao(PROMO, {"DADOS": r}, CONTRATO)["REGUA"])

    def test_pagina_sem_data_nao_inventa_data_e_reprova(self):
        sem_data = VIDEO_PAGINA.replace(b'<meta itemprop="datePublished" content="2026-09-20T10:00:00-07:00">', b"")
        r, _ = self.correr([(200, CANAL_PAGINA, ""), (200, sem_data, "")])
        self.assertIsNone(r["ITEM_ABERTO"]["PUBLICATION_TIME"])
        self.assertEqual("LEGACY", RS.passos_da_promocao(PROMO, {"DADOS": r}, CONTRATO)["REGUA"])

    def test_429_no_video_nao_passa(self):
        r, _ = self.correr([(200, CANAL_PAGINA, ""), (429, b"", "HTTP 429")])
        self.assertEqual((False, 429), (r["PASS"], r["HTTP"]))

    def test_canal_sem_videos_para_antes_do_segundo_pedido(self):
        r, pedidos = self.correr([(200, ('{"channelId":"%s"}' % CID).encode(), "")])
        self.assertEqual(1, len(pedidos))
        self.assertEqual("SOURCE_FAILURE", r["CLASSE"])


class Worker(unittest.TestCase):
    def test_forma_video_vai_ao_canario_video(self):
        with mock.patch.object(CAN, "canario_video", return_value={"PASS": True}) as cv, \
             mock.patch.object(CAN, "canario_youtube_canal", side_effect=AssertionError("forma VIDEO")):
            r, _ = W.etapa_canary("IT-T10-017", dict(CONTRATO))
        self.assertEqual("OK", r)
        cv.assert_called_once()


if __name__ == "__main__":
    unittest.main()
