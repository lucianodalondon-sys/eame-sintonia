# -*- coding: utf-8 -*-
"""D53 · a rota VIDEO, julgada no recibo do Scrap — o unico dono da rota YouTube.

Prova minima, em CADA item da colheita `canal-youtube`: a pagina publica do video (o
endereco nomeia o NATIVE_ID), o titulo, a data de publicacao e o canal do CONTRATO.
Falta uma = FALHA com o nome dela. Transcricao nao e exigida nem inventada.

Os itens sao os dos adaptadores do Scrap, com os nomes de campo de cada um:
`youtube_oficial.uploads_recentes` (URL, TITLE, SOURCE_ACCOUNT, RAW.CHANNEL_ID).
`julgar()` e pura: sem rede, sem disco, sem banco.
"""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import regua_social as R    # noqa: E402
import ready_split as RS    # noqa: E402

SID = "IT-T10-017"
CANAL = "UCfdN2DQZBfZo-7VgBqotYuQ"
VID = "abcdefghijk"
CONTRATO = {"SOURCE_ID": SID, "NAME": "Canale",
            "ACQUISITION": {"STRATEGY": "SCRAP_FASE", "FASE": "canal-youtube", "PLATFORM": "YOUTUBE",
                            "CHANNEL_ID": CANAL, "FILTROS": {"canal_id": CANAL}}}


def item(**mudar):
    """O objeto de `youtube_oficial.uploads_recentes` (social_envelope.envelope)."""
    ob = {"PLATFORM": "YOUTUBE", "SOURCE_ACCOUNT": CANAL, "NATIVE_ID": VID,
          "URL": "https://www.youtube.com/watch?v=" + VID, "CONTENT_TYPE": "VIDEO",
          "TITLE": "Vendemmia 2026 in Franciacorta", "TEXT": "descricao do autor",
          "PUBLISHED_AT": "2026-09-20T17:00:00Z", "COLLECTED_AT": "2026-09-25T12:00:00+00:00",
          "OWNER_AUTHORIZED": "SIM", "PLATFORM_POLICY_STATUS": "ALLOWED",
          "RAW": {"CHANNEL_ID": CANAL, "API_METHOD": "playlistItems.list"}}
    ob.update(mudar)
    return {"OBSERVACAO": {k: v for k, v in ob.items() if v is not None}}


def env(*itens, fase="canal-youtube"):
    return {"SOURCE_ID_DO_PEDIDO": SID, "FASE": fase, "COLHEITA": list(itens),
            "SUPORTE": [{"ESPECIE": "RUN_RECEIPT", "RESUMO": {"RESULT": "OK"}}]}


def julgar(*itens, contrato=CONTRATO, raw=1):
    return R.julgar(env(*itens), SID, "canal-youtube", raw, contrato=contrato)


class AsQuatroProvas(unittest.TestCase):
    def test_as_quatro_provas_dao_ready_e_a_promocao_e_social(self):
        v, porque = julgar(item(), item(NATIVE_ID="bbbbbbbbbbb", URL="https://youtu.be/bbbbbbbbbbb"))
        self.assertEqual(R.READY, v, porque)
        self.assertIn("D53", porque)
        self.assertIn("transcricao nao exigida", porque)
        promo = {"OBSERVED_AT": "2026-09-25T12:00:00+00:00", "EVIDENCE_REF": "EV-1"}
        dados = {"VEREDITO": v, "FASE": "canal-youtube", "PORQUE": porque}
        self.assertEqual(RS.REGUA_SOCIAL, RS.passos_da_promocao(promo, {"DADOS": dados}, CONTRATO)["REGUA"])

    def test_falta_cada_uma_das_quatro_reprova_com_o_nome_dela(self):
        faltas = {
            "PAGINA_DO_VIDEO": [dict(URL=None), dict(URL="https://www.youtube.com/channel/%s/videos" % CANAL),
                                dict(URL="https://www.youtube.com/watch?v=outrooutroo"),
                                dict(URL="https://evil.example/watch?v=" + VID),
                                dict(NATIVE_ID="curto", URL="https://www.youtube.com/watch?v=curto")],
            "TITULO": [dict(TITLE=None), dict(TITLE="  "), dict(TITLE="NAO SEI"),
                       dict(TITLE="Private video"), dict(TITLE="Deleted video")],
            "DATA_DE_PUBLICACAO": [dict(PUBLISHED_AT="UNKNOWN")],
            "CANAL": [dict(SOURCE_ACCOUNT="UCoutrooutrooutrooutrooo", RAW={"CHANNEL_ID": "UCoutrooutrooutrooutrooo"})],
        }
        for prova, estragos in faltas.items():
            for estraga in estragos:
                with self.subTest(prova=prova, estraga=estraga):
                    v, porque = julgar(item(), item(**estraga))
                    self.assertEqual(R.FALHA, v)
                    # «UNKNOWN» e o «nao sei» do envelope do Scrap: CAMPOS_DO_ITEM so via «NAO SEI»
                    self.assertIn(prova, porque)

    def test_a_prova_do_video_sozinha_nomeia_a_data(self):
        self.assertEqual(["DATA_DE_PUBLICACAO"],
                         R.provas_do_video(item(PUBLISHED_AT="NAO SEI")["OBSERVACAO"], CANAL))

    def test_contrato_sem_canal_nao_prova_o_canal(self):
        v, porque = julgar(item(), contrato={"ACQUISITION": {"STRATEGY": "SCRAP_FASE", "FASE": "canal-youtube"}})
        self.assertEqual(R.FALHA, v)
        self.assertIn("CANAL", porque)

    def test_o_canal_le_se_nos_nomes_de_cada_adaptador(self):
        so_raw = item(SOURCE_ACCOUNT=None)
        do_audio = item(URL=None, SOURCE_URL="https://www.youtube.com/watch?v=" + VID, TITLE=None,
                        RAW={"TITLE": "Vendemmia", "CHANNEL_ID": CANAL}, SOURCE_ACCOUNT=None)
        for it in (so_raw, do_audio):
            with self.subTest(it=sorted(it["OBSERVACAO"])):
                self.assertEqual([], R.provas_do_video(it["OBSERVACAO"], CANAL))

    def test_transcricao_nao_e_exigida_nem_inventada(self):
        v, _ = julgar(item(TEXT=None))
        self.assertEqual(R.READY, v)
        self.assertNotIn("TRANSCRICAO", R.PROVAS_DO_VIDEO)

    def test_outras_fases_nao_pedem_as_provas_do_video(self):
        c = {"ACQUISITION": {"STRATEGY": "SCRAP_FASE", "FASE": "pagina-linkedin"}}
        e = env(item(URL=None, TITLE=None), fase="pagina-linkedin")
        v, porque = R.julgar(e, SID, "pagina-linkedin", 1, contrato=c)
        self.assertEqual(R.READY, v, porque)
        self.assertNotIn("D53", porque)

    def test_visto_nao_e_guardado_continua(self):
        v, porque = julgar(item(), raw=0)
        self.assertEqual(R.FALHA, v)
        self.assertIn("0 linhas RAW", porque)


if __name__ == "__main__":
    unittest.main()
