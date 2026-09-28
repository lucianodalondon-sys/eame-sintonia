# -*- coding: utf-8 -*-
"""SOCIAL-ATE-A-SALA · C — a lista do canal COM DATA sem chave (o feed), dentro de `canal-youtube`.

Duas metades, e as duas medem-se aqui:
  · HOJE a matriz fecha a rota (`feeds/videos.xml` = PERMITIDA NAO / ROUTE_NOT_ALLOWED, porque
    o robots.txt do YouTube a barra — medido em 08/09, 20/09 e 24/09). Fechada: ZERO pedidos,
    e a fase responde exactamente o que respondia (CREDENTIAL_MISSING sem chave).
  · SE o dono a abrir NA MATRIZ: 1 pedido por canal, pelo transporte canonico
    (`scrap_http.buscar_bytes`: robots vivo + teto do dominio + portao), ate 15 videos com
    NATIVE_ID, PUBLISHED_AT (precisao SECOND) e canal — e o item passa a regua D53.

O feed dos testes e SINTETICO, no formato Atom que o YouTube serve (nenhum byte real do
YouTube esta no repositorio). Sem rede: o transporte e sempre um falso.
"""
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
sys.path.insert(0, str(RAIZ / "curadoria"))
import adaptador_youtube as ay  # noqa: E402
import regua_social as R  # noqa: E402
import scrap_http as http  # noqa: E402
import social_matriz as mz  # noqa: E402
import youtube_oficial as yt  # noqa: E402

CANAL = "UCXUG407gp3CnWnfS3ycijhA"
OUTRO = "UCzzzzzzzzzzzzzzzzzzzzzz"


def entrada(vid, canal=CANAL, publicado="2026-07-09T14:25:29+00:00", titulo="Olio nuovo"):
    return ("<entry><id>yt:video:%s</id><yt:videoId>%s</yt:videoId><yt:channelId>%s</yt:channelId>"
            "<title>%s</title><link rel=\"alternate\" href=\"https://www.youtube.com/watch?v=%s\"/>"
            "<author><name>Olio Officina</name><uri>https://www.youtube.com/channel/%s</uri></author>"
            "<published>%s</published></entry>" % (vid, vid, canal, titulo, vid, canal, publicado))


def feed(*entradas):
    return ("<?xml version=\"1.0\" encoding=\"UTF-8\"?><feed xmlns:yt=\"http://www.youtube.com/xml/schemas/2015\" "
            "xmlns=\"http://www.w3.org/2005/Atom\"><yt:channelId>%s</yt:channelId>%s</feed>"
            % (CANAL, "".join(entradas))).encode("utf-8")


VIDS = ["CsWIA9ud0c%s" % c for c in "ABCDEFGHIJKLMNOPQR"]   # 18 ids com forma de id


class Transporte:
    def __init__(self, corpo=None, erro=None):
        self.corpo, self.erro, self.chamadas, self.autorizacoes = corpo, erro, [], []

    def __call__(self, url, **_):
        self.chamadas.append(url)
        self.autorizacoes.append(http.autorizacao_actual())
        if self.erro:
            raise self.erro
        return self.corpo, {"STATUS": 200, "CONTENT_TYPE": "application/atom+xml"}


def linha_aberta(**mais):
    base = dict(ay.linha_do_feed())
    base.update({"PERMITIDA": "SIM", "ESTADO": "PROVED"}, **mais)
    return base


class _Base(unittest.TestCase):
    def setUp(self):
        self._chave = os.environ.pop(yt.ENV_CHAVE, None)
        self._raw = mock.patch.object(ay.env, "guardar_raw",
                                      lambda plat, chave, corpo: {"PATH": "RAW/%s" % chave, "SHA256": "f" * 64})
        self._raw.start()

    def tearDown(self):
        self._raw.stop()
        if self._chave is not None:
            os.environ[yt.ENV_CHAVE] = self._chave

    def abrir(self, **mais):
        linhas = mz.MATRIZ["YOUTUBE"]["INCREMENTAL"]
        i = next(i for i, l in enumerate(linhas) if l["ROTA"] == ay.ROTA_FEED_DO_CANAL)
        p = mock.patch.dict(linhas[i], linha_aberta(**mais))
        p.start()
        self.addCleanup(p.stop)


class HojeAMatrizFecha(_Base):
    def test_1_a_linha_do_feed_existe_e_esta_fechada(self):
        linha = ay.linha_do_feed()
        self.assertIsNotNone(linha)
        aberta, porque = ay.feed_aberto_pela_matriz()
        self.assertFalse(aberta)
        self.assertIn("ROUTE_NOT_ALLOWED", porque)

    def test_2_fechada_nao_sai_nenhum_pedido(self):
        t = Transporte(feed(entrada(VIDS[0])))
        medida = {}
        with self.assertRaises(ay._EstadoDaApi) as e:
            ay.youtube_canal_sem_chave(channel_id=CANAL, run_id="R", country_scope="IT", buscar=t, medida=medida)
        self.assertEqual(e.exception.rel["STATE"], "ROUTE_NOT_ALLOWED")
        self.assertEqual(t.chamadas, [])
        self.assertEqual(medida["REQUESTS"], 0)

    def test_3_sem_chave_a_sonda_responde_o_que_respondia(self):
        self.assertEqual(ay.pronto_para_canal(), (False, "CREDENTIAL_MISSING"))

    def test_4_sem_chave_e_fechada_a_fase_continua_CREDENTIAL_MISSING(self):
        with mock.patch.object(ay, "youtube_canal_sem_chave") as feed_:
            with self.assertRaises(ay._EstadoDaApi) as e:
                ay.youtube_uploads(channel_id=CANAL, run_id="R", country_scope="IT")
        self.assertEqual(e.exception.rel["STATE"], "CREDENTIAL_MISSING")
        feed_.assert_not_called()

    def test_5_o_registo_da_fase_usa_a_sonda_nova_que_le_a_chave(self):
        import scrap_registo as reg
        reg.carregar_adaptadores()
        r = reg.adaptador_de("YOUTUBE", "youtube.channel.discovery")
        self.assertIs(r["PRONTO"], ay.pronto_para_canal)
        self.assertTrue(getattr(r["PRONTO"], "LE_A_CHAVE", False))


class SeODonoAbrirNaMatriz(_Base):
    def setUp(self):
        super().setUp()
        self.abrir()

    def test_6_um_pedido_so_e_ate_15_videos_com_data_e_canal(self):
        t = Transporte(feed(*[entrada(v) for v in VIDS]))
        objs = ay.youtube_canal_sem_chave(channel_id=CANAL, run_id="R", country_scope="IT", buscar=t)
        self.assertEqual(t.chamadas, [ay.FEED_DO_CANAL % CANAL])
        self.assertEqual(len(objs), 15)
        o = objs[0]
        self.assertEqual(o["NATIVE_ID"], VIDS[0])
        self.assertEqual(o["PUBLISHED_AT"], "2026-07-09T14:25:29+00:00")
        self.assertEqual(o["PUBLISHED_AT_PRECISION"], "SECOND")
        self.assertEqual(o["CHANNEL_ID"], CANAL)
        self.assertEqual(o["FACT_TIME"], "NAO SEI")

    def test_7_entrada_de_outro_canal_ou_sem_id_nao_entra(self):
        t = Transporte(feed(entrada(VIDS[0]), entrada(VIDS[1], canal=OUTRO), entrada("curto")))
        medida = {}
        objs = ay.youtube_canal_sem_chave(channel_id=CANAL, run_id="R", country_scope="IT", buscar=t,
                                          medida=medida)
        self.assertEqual([o["NATIVE_ID"] for o in objs], [VIDS[0]])
        self.assertEqual(sorted(f["PORQUE"] for f in medida["FORA_DO_FEED"]), ["OUTRO_CANAL", "VIDEO_ID_SEM_FORMA"])

    def test_8_data_sem_forma_de_instante_nao_ganha_precisao(self):
        t = Transporte(feed(entrada(VIDS[0], publicado="ontem")))
        o = ay.youtube_canal_sem_chave(channel_id=CANAL, run_id="R", country_scope="IT", buscar=t)[0]
        self.assertEqual(o["PUBLISHED_AT_PRECISION"], "NAO SEI")

    def test_9_robots_a_barrar_e_ROUTE_NOT_ALLOWED_sem_contornar(self):
        t = Transporte(erro=http.RotaNaoPermitida("robots.txt do host barra este caminho"))
        with self.assertRaises(ay._EstadoDaApi) as e:
            ay.youtube_canal_sem_chave(channel_id=CANAL, run_id="R", country_scope="IT", buscar=t)
        self.assertEqual(e.exception.rel["STATE"], "ROUTE_NOT_ALLOWED")
        self.assertIn("robots", e.exception.rel["NATIVE_REASON"])
        self.assertEqual(len(t.chamadas), 1)

    def test_10_sem_decisao_do_dono_na_linha_nao_ha_autorizacao_viva(self):
        t = Transporte(feed(entrada(VIDS[0])))
        ay.youtube_canal_sem_chave(channel_id=CANAL, run_id="R", country_scope="IT", buscar=t)
        self.assertIsNone(t.autorizacoes[0])

    def test_11_com_a_decisao_do_dono_ela_viaja_nomeada(self):
        self.abrir(OWNER_AUTHORIZED="SIM", PLATFORM_POLICY_STATUS="DISALLOWED")
        t = Transporte(feed(entrada(VIDS[0])))
        o = ay.youtube_canal_sem_chave(channel_id=CANAL, run_id="R", country_scope="IT", buscar=t)[0]
        self.assertIsNotNone(t.autorizacoes[0])
        self.assertEqual(t.autorizacoes[0].rota, ay.ROTA_FEED_DO_CANAL)
        self.assertEqual(t.autorizacoes[0].hosts, ("www.youtube.com",))
        self.assertEqual((o["OWNER_AUTHORIZED"], o["PLATFORM_POLICY_STATUS"]), ("SIM", "DISALLOWED"))

    def test_12_o_transporte_por_omissao_e_o_canonico(self):
        """robots/teto/portao IGUAIS: sem `buscar`, e `scrap_http.buscar_bytes` que sai."""
        t = Transporte(feed(entrada(VIDS[0])))
        with mock.patch.object(http, "buscar_bytes", t):
            ay.youtube_canal_sem_chave(channel_id=CANAL, run_id="R", country_scope="IT")
        self.assertEqual(t.chamadas, [ay.FEED_DO_CANAL % CANAL])

    def test_13_a_fase_sem_chave_usa_o_feed_e_a_sonda_fica_pronta(self):
        t = Transporte(feed(entrada(VIDS[0])))
        with mock.patch.object(http, "buscar_bytes", t):
            objs = ay.youtube_uploads(channel_id=CANAL, run_id="R", country_scope="IT", limit=25)
        self.assertEqual([o["NATIVE_ID"] for o in objs], [VIDS[0]])
        self.assertTrue(ay.pronto_para_canal()[0])

    def test_14_DTD_e_recusado_antes_de_ler(self):
        bomba = b'<?xml version="1.0"?><!DOCTYPE f [<!ENTITY a "aaaa">]><feed>&a;</feed>'
        with self.assertRaises(ValueError):
            ay.youtube_canal_sem_chave(channel_id=CANAL, run_id="R", country_scope="IT",
                                       buscar=Transporte(bomba))

    def test_15_canal_sem_forma_recusa_antes_da_rede(self):
        t = Transporte(feed())
        with self.assertRaises(ValueError):
            ay.youtube_canal_sem_chave(channel_id="regionelombardia", run_id="R", country_scope="IT", buscar=t)
        self.assertEqual(t.chamadas, [])

    def _julgar_item_do_feed(self):
        t = Transporte(feed(entrada(VIDS[0])))
        o = ay.youtube_canal_sem_chave(channel_id=CANAL, run_id="R", country_scope="IT", buscar=t)[0]
        sid = "IT-T5-165"
        contrato = {"SOURCE_ID": sid, "NAME": "Olio Officina",
                    "ACQUISITION": {"FASE": "canal-youtube", "CHANNEL_ID": CANAL}}
        env_ = {"SOURCE_ID_DO_PEDIDO": sid, "FASE": "canal-youtube", "COLHEITA": [{"OBSERVACAO": o}],
                "SUPORTE": [{"ESPECIE": "RUN_RECEIPT", "RESUMO": {"RESULT": "OK"}}]}
        return R.julgar(env_, sid, "canal-youtube", 1, contrato=contrato)

    def test_16_o_item_do_feed_passa_a_regua_D53_com_a_decisao_do_dono(self):
        """O robots barra o feed: aberto so com OWNER_AUTHORIZED=SIM escrito na linha (como a D23)."""
        self.abrir(OWNER_AUTHORIZED="SIM", PLATFORM_POLICY_STATUS="DISALLOWED")
        v, porque = self._julgar_item_do_feed()
        self.assertEqual(v, R.READY, porque)

    def test_17_sem_a_decisao_do_dono_escrita_o_item_nao_fica_READY(self):
        v, porque = self._julgar_item_do_feed()
        self.assertEqual(v, R.FALHA)
        self.assertIn("OWNER_AUTHORIZED", porque)


if __name__ == "__main__":
    unittest.main(verbosity=2)
