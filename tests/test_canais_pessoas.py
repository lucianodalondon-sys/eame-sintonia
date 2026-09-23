#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""YT3 · a descoberta de canais pelo site oficial — sem rede.

O que se guarda:
  · a forma dos links (canal, podcast, newsletter) e a armadilha do anuncio com
    `utm_source=newsletter`;
  · todo o achado novo tem decisao escrita (nada POR_DECIDIR);
  · tudo o que diz ENTRA esta na fila com a prova de identidade na NOTA, e nada
    do que diz FICA_FORA entrou.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "canais_pessoas"))
import canais_pessoas as CP  # noqa: E402

AQUI = os.path.join(RAIZ, "scripts", "canais_pessoas")


def _j(nome):
    with open(os.path.join(AQUI, nome), encoding="utf-8") as f:
        return json.load(f)


class AFormaDosLinks(unittest.TestCase):

    def test_1_as_quatro_formas_de_canal(self):
        for u in ("https://www.youtube.com/@diachem", "https://youtube.com/channel/UC8Uto03To7JFiY6HM1PAb7Q",
                  "https://www.youtube.com/user/federunacoma", "https://m.youtube.com/c/UciIt"):
            self.assertEqual(CP.classificar_link(u, "")[0], "YOUTUBE", u)

    def test_2_video_solto_nao_e_canal(self):
        self.assertIsNone(CP.classificar_link("https://www.youtube.com/watch?v=abc123def45", "")[0])

    def test_3_podcast(self):
        self.assertEqual(CP.classificar_link("https://open.spotify.com/show/0cqa1I9ccmuQ9Db5P3TJ4v", "")[0], "PODCAST")

    def test_4_newsletter_pela_ancora_e_pelo_caminho(self):
        self.assertEqual(CP.classificar_link("https://www.anbi.it/p/newsletter", "")[0], "NEWSLETTER")
        self.assertEqual(CP.classificar_link("https://x.it/iscriviti", "Newsletter")[0], "NEWSLETTER")

    def test_5_a_armadilha_do_anuncio_utm_e_apanhada_na_decisao(self):
        """O classificador marca-o (o caminho tem «newsletter_»); a DECISAO tem de o deixar fora."""
        d = {x["URL"]: x for x in _j("DECISOES-YT3-V1.json")["DECISOES"]}
        anuncio = [u for u in d if "utm_source=newsletter" in u]
        self.assertTrue(all(d[u]["DECISAO"] == "FICA_FORA" for u in anuncio))


class ADecisaoEAFila(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.desc = _j("DESCOBERTA-CANAIS-PESSOAS-V1.json")
        cls.dec = {x["URL"]: x for x in _j("DECISOES-YT3-V1.json")["DECISOES"]}
        with open(os.path.join(RAIZ, "candidatas", "FONTES-CANDIDATAS.json"), encoding="utf-8") as f:
            cls.fila = {c["URL"]: c for c in json.load(f)["CANDIDATAS"]}

    def test_6_todo_achado_novo_tem_decisao_escrita(self):
        novos = [a["URL"] for h in self.desc["HOSTS"].values() for a in h.get("ACHADOS", [])
                 if not a["JA_CONHECIDO"]]
        self.assertTrue(novos)
        for u in novos:
            self.assertIn(u, self.dec, u)
            self.assertIn(self.dec[u]["DECISAO"], ("ENTRA", "FICA_FORA"), u)
            self.assertTrue(self.dec[u]["PORQUE"].strip(), u)

    def test_7_o_que_entra_esta_na_fila_com_a_prova(self):
        for u, x in self.dec.items():
            if x["DECISAO"] != "ENTRA":
                continue
            c = self.fila.get(u)
            self.assertIsNotNone(c, u)
            self.assertIn("IDENTIDADE: a pagina oficial", c["NOTA"])
            self.assertIn("descoberta-indireta:site-da-organizacao", c["NOTA"])
            # IT com prova (ccTLD, P.IVA, morada), ou NAO SEI DECLARADO — nunca IT presumido.
            self.assertTrue(c["PAIS"] == "IT" or "TERRITORIO_POR_PROVAR" in c["NOTA"], (u, c["PAIS"]))
            self.assertEqual(c["ESTADO"], "CANDIDATA")

    def test_8_o_que_fica_fora_nao_entrou(self):
        for u, x in self.dec.items():
            if x["DECISAO"] == "FICA_FORA":
                c = self.fila.get(u)
                self.assertFalse(c and "YT3" in (c.get("NOTA") or ""), u)

    def test_9_todos_os_portoes_de_egresso_passaram_em_IT(self):
        for p in self.desc["PORTOES"]:
            self.assertEqual((p["GATE"], p["PAIS"]), ("PASS", "IT"), p)


if __name__ == "__main__":
    unittest.main(verbosity=2)
