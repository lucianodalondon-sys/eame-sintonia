# -*- coding: utf-8 -*-
"""PRIMEIRA-VOLTA-VIDEO · a pontuacao (listas de palavras) e a leitura da pagina guardada. Sem rede."""
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas" / "primeira_volta_video"))
import pontuar as P             # noqa: E402
import videos_guardados as V    # noqa: E402


def v(titulo, desc="", dur=200, pub="2026-07-15", leg=("it",)):
    return {"TITULO": titulo, "DESCRICAO": desc, "DURACAO_S": dur, "PUBLICADO": pub,
            "LEGENDAS": [{"LINGUA": x, "AUTO": True} for x in leg]}


class Pontuar(unittest.TestCase):
    def test_termo_com_espaco_e_plural_casam(self):
        # os dois defeitos da 1.a lista: espacos dentro do termo apagados, e plurais em falta
        s = P.sinais(v("AMAP a convegno: la difesa della mosca delle olive"))
        self.assertTrue(s["CULTURA"] and s["PROBLEMA"] and s["VOZ"])
        s = P.sinais(v('Webinar "Patate: strategie sostenibili contro gli elateridi"'))
        self.assertTrue(s["UTIL"])
        self.assertTrue(P.sinais(v("piccoli frutti in Trentino"))["CULTURA"])

    def test_util_pede_as_tres_coisas(self):
        self.assertFalse(P.sinais(v("Vendemmia in Franciacorta"))["UTIL"])          # so cultura+regiao
        self.assertFalse(P.sinais(v("La difesa integrata del pomodoro"))["UTIL"])  # sem voz
        self.assertTrue(P.sinais(v("Intervista all'agronomo: peronospora sulla vite"))["UTIL"])

    def test_curto_recente_e_legenda(self):
        s = P.sinais(v("x", dur=541, pub="2025-09-19", leg=("en",)))
        self.assertEqual((False, False, False), (s["CURTO"], s["RECENTE"], s["LEGENDA_IT"]))
        s = P.sinais(v("x", dur=540, pub="2025-09-20"))
        self.assertEqual((True, True, True), (s["CURTO"], s["RECENTE"], s["LEGENDA_IT"]))

    def test_falsos_positivos_medidos_na_segunda_lista(self):
        # «pero» casava «peronospora»/«però», «riso» casava «risorse», «vite» casava «vitello»
        self.assertFalse(P.sinais(v("Si è parlato della peronospora"))["CULTURA"])
        self.assertFalse(P.sinais(v("Nuove risorse per il vitello"))["CULTURA"])
        self.assertTrue(P.sinais(v("Cimice asiatica nei pereti"))["CULTURA"])
        # o papel da pessoa nao e o problema de que ela fala
        self.assertFalse(P.sinais(v("Intervista a X – Agronomo Fitopatologo, oliveto"))["PROBLEMA"])

    def test_descricao_do_evento_repetida_nao_conta(self):
        ev = "Vite in Campo: potatura invernale; si è parlato anche della peronospora."
        vids = [dict(v("Vite in Campo - Intervista a %s" % n, desc=ev), SOURCE_ID="IT-X", ESTADO="LIDO")
                for n in ("A", "B", "C")]
        part = P.partilhadas_por_canal(vids)
        self.assertEqual(1, len(part))
        s = P.sinais(vids[0], descricao_partilhada=True)
        self.assertFalse(s["PROBLEMA"])
        self.assertTrue(P.sinais(vids[0])["PROBLEMA"])      # sem a regra, a peronospora do evento contava

    def test_duracao_desconhecida_nao_e_curta(self):
        self.assertFalse(P.sinais(v("x", dur=None))["CURTO"])


class Custo(unittest.TestCase):
    def setUp(self):
        import fala_dos_videos as F
        self.F = F

    def test_pedidos_por_video_e_o_teto(self):
        c = self.F.custo(300)                  # 5 min: 4,8 MB -> 1 fatia
        self.assertEqual((3, 1, 4, True), (c["YOUTUBE_COM"], c["GOOGLEVIDEO_COM"], c["BALDE"], c["CABE_NO_TETO"]))
        c = self.F.custo(5634)                 # 94 min a 128 kbit/s: 90 MB -> 2 fatias -> 5 = o teto
        self.assertEqual((2, 5, True), (c["GOOGLEVIDEO_COM"], c["BALDE"], c["CABE_NO_TETO"]))
        self.assertFalse(self.F.custo(9777)["CABE_NO_TETO"])      # 2,7 h: 3 fatias -> 6 > 5
        self.assertFalse(self.F.custo(5634, 160)["CABE_NO_TETO"]) # o pior caso de bitrate nao cabe

    def test_gpu_pela_medida_de_14_09(self):
        self.assertAlmostEqual(460.9 / 34.07, self.F.custo(460.9)["GPU_S"], places=1)

    def test_uma_fonte_por_volta(self):
        xs = [{"SOURCE_ID": s, "VIDEO_ID": "v%d" % i, "DURACAO_S": 60} for i, s in enumerate("AABAC")]
        vs = self.F.voltas_do_maestro(xs)
        self.assertEqual(3, len(vs))
        for v in vs:
            fontes = [x["SOURCE_ID"] for x in v]
            self.assertEqual(len(fontes), len(set(fontes)))
        self.assertEqual(5, sum(len(v) for v in vs))


class Pagina(unittest.TestCase):
    def test_le_o_que_a_pagina_declara(self):
        pr = {"videoDetails": {"videoId": "abcdefghijk", "title": "Oliveto Smart", "channelId": "UCx",
                               "author": "IA", "lengthSeconds": "198", "shortDescription": "Intervista"},
              "microformat": {"playerMicroformatRenderer": {"publishDate": "2026-06-30T00:00:00-07:00"}},
              "captions": {"playerCaptionsTracklistRenderer": {"captionTracks": [{"languageCode": "it", "kind": "asr"}]}}}
        html = "<html><script>var ytInitialPlayerResponse = %s;</script></html>" % json.dumps(pr)
        r = V.retrato(html)
        self.assertEqual(("abcdefghijk", "Oliveto Smart", 198, "2026-06-30T00:00:00-07:00"),
                         (r["VIDEO_ID"], r["TITULO"], r["DURACAO_S"], r["PUBLICADO"]))
        self.assertEqual([{"LINGUA": "it", "AUTO": True}], r["LEGENDAS"])
        self.assertFalse(r["SEM_PLAYER_RESPONSE"])

    def test_pagina_sem_dados_nao_inventa(self):
        r = V.retrato("<html><body>nada</body></html>")
        self.assertTrue(r["SEM_PLAYER_RESPONSE"])
        self.assertEqual((None, None, None, []), (r["TITULO"], r["PUBLICADO"], r["DURACAO_S"], r["LEGENDAS"]))


if __name__ == "__main__":
    unittest.main()
