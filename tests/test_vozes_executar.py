# -*- coding: utf-8 -*-
"""VOZES-EXECUTAR — o executor do plano de pedidos e a leitura das provas, SEM rede (buscar e portao injectados)."""
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas" / "vozes"))

import colher_papel as C  # noqa: E402
import ler_provas as L  # noqa: E402

PASS = lambda: {"EGRESS_GATE": "PASS"}          # noqa: E731
ONDA4 = {"myfruit.it", "edagricole.it", "koppert.it", "cnr.it"}


def ficha(fid, alvo, ronda="1", pessoa="Giulia Zuecco"):
    return {"ID": fid, "ALVO": alvo, "RONDA": ronda, "PESSOA": pessoa, "MODO": "BUSCA"}


class Site:
    """Um site de mentira: robots.txt e paginas; conta os pedidos."""

    def __init__(self, robots=b"User-agent: *\nDisallow: /privado/\n", paginas=None):
        self.robots, self.paginas, self.pedidos = robots, paginas or {}, []

    def __call__(self, url):
        self.pedidos.append(url)
        if url.endswith("/robots.txt"):
            return (200, self.robots, "") if self.robots is not None else (0, b"", "URLError")
        return (200, self.paginas[url], "") if url in self.paginas else (404, b"", "HTTP 404")


class OExecutor(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def corre(self, fichas, site, ronda="1", hora=12, portao=PASS):
        return C.correr({"FICHAS": fichas}, ronda, site, portao, self.tmp, ONDA4, hora, dormir=lambda s: None)

    def test_dois_pedidos_por_dominio_robots_e_alvo(self):
        alvo = "https://www.dafnae.unipd.it/?q=Zuecco"
        site = Site(paginas={alvo: b"<p>Giulia Zuecco, docente</p>"})
        r = self.corre([ficha("V03", alvo)], site)
        self.assertEqual(r["PEDIDOS"], 2)
        self.assertEqual(site.pedidos, ["https://www.dafnae.unipd.it/robots.txt", alvo])
        prova = next(p for p in r["COLHIDAS"][0]["PROVAS"] if p["PAPEL"] == "ALVO")
        self.assertEqual(prova["SHA256"], hashlib.sha256(Path(prova["BYTES_EM"]).read_bytes()).hexdigest())

    def test_teto_dois_no_mesmo_dominio_mesmo_que_o_plano_erre(self):
        a1, a2 = "https://www.conserveitalia.it/a", "https://www.conserveitalia.it/b"
        site = Site(paginas={a1: b"x", a2: b"y"})
        r = self.corre([ficha("V16", a1), ficha("V28", a2)], site)
        self.assertEqual(r["PEDIDOS_POR_DOMINIO"]["conserveitalia.it"], 2)
        self.assertEqual(len(site.pedidos), 2)

    def test_robots_proibe_o_alvo_um_pedido_so(self):
        alvo = "https://www.crpv.it/privado/webinar"
        site = Site(paginas={alvo: b"x"})
        r = self.corre([ficha("V23", alvo, pessoa="NAO SEI")], site)
        self.assertEqual(site.pedidos, ["https://www.crpv.it/robots.txt"])
        self.assertIn("robots", r["COLHIDAS"][0]["PORQUE_PAROU"])

    def test_robots_ilegivel_nao_e_licenca(self):
        site = Site(robots=None)
        r = self.corre([ficha("V05", "https://www.terremerse.it/")], site)
        self.assertEqual(len(site.pedidos), 1)
        self.assertIn("ilegivel", r["COLHIDAS"][0]["PORQUE_PAROU"])

    def test_portao_sem_pass_zero_pedidos(self):
        site = Site()
        r = self.corre([ficha("V05", "https://www.terremerse.it/")], site, portao=lambda: {"EGRESS_GATE": "BLOCKED"})
        self.assertEqual(site.pedidos, [])
        self.assertEqual(r["PEDIDOS"], 0)

    def test_proibidos_onda4_e_noturno_nao_pedem_nada(self):
        site = Site()
        fichas = [ficha("V21", "https://www.isafom.cnr.it/x"), ficha("V10", "https://www.myfruit.it/search-result?q=a"),
                  ficha("V20", "https://terraevita.edagricole.it/?s=Basso"), ficha("V29", "https://www.reterurale.it/")]
        r = self.corre(fichas, site)
        self.assertEqual(site.pedidos, [])
        self.assertEqual({x["ID"] for x in r["RECUSADAS"]}, {"V21", "V10", "V20", "V29"})

    def test_amap_nao_colide_com_arpa_marche(self):
        self.assertFalse(C.mesmo_site("amap.marche.it", "arpa.marche.it"))
        self.assertTrue(C.mesmo_site("terraevita.edagricole.it", "edagricole.it"))

    def test_noturno_so_na_janela_e_na_ronda_noturna(self):
        alvo = "https://www.reterurale.it/"
        f = ficha("V29", alvo, ronda="NOTURNA-1", pessoa="NAO SEI")
        site = Site(paginas={alvo: b"x"})
        self.assertEqual(self.corre([f], site, ronda="NOTURNA-1", hora=12)["PEDIDOS"], 0)
        self.assertEqual(self.corre([f], site, ronda="NOTURNA-1", hora=2)["PEDIDOS"], 2)
        self.assertIsNotNone(C.porque_nao(ficha("V03", "https://www.dafnae.unipd.it/"), "NOTURNA-1", ONDA4, 2))

    def test_sem_rodadas_da_onda4_nao_corre(self):
        with self.assertRaises(SystemExit):
            C.dominios_da_onda4(self.tmp / "nao-existe.txt")


class ALeitura(unittest.TestCase):

    def test_nome_e_papel_no_mesmo_trecho_e_sim(self):
        j = L.julgar("Hanspeter Felder", "Videointervista ad Hanspeter Felder, direttore della Cooperativa")
        self.assertEqual(j["PAPEL_PROVADO"], "SIM")

    def test_nome_sem_papel_e_nao_sei(self):
        j = L.julgar("Pietro Baroncini", "Campagna drupacee 2026, la frutta c'e: il punto di Pietro Baroncini")
        self.assertEqual(j["PAPEL_PROVADO"], "NAO SEI")

    def test_nome_ausente_e_nao_sei_e_acento_nao_engana(self):
        self.assertEqual(L.julgar("Mario Enrico Pe", "nulla qui")["PAPEL_PROVADO"], "NAO SEI")
        self.assertEqual(L.julgar("Mario Enrico Pe", "il prof. Mario Enrico Pè")["PAPEL_PROVADO"], "SIM")

    def test_serie_sem_nome_nunca_e_sim_automatico(self):
        self.assertEqual(L.julgar("NAO SEI (relatores)", "il prof. Rossi")["PAPEL_PROVADO"], "NAO SEI")

    def test_passo1_confere_o_sha256_do_recibo(self):
        tmp = Path(tempfile.mkdtemp())
        b = b"<p>Silvia Toffolati, ricercatrice</p>"
        (tmp / "V04").mkdir()
        (tmp / "V04" / "1_ALVO.bin").write_bytes(b)
        rec = {"COLHIDAS": [{"ID": "V04", "PROVAS": [{"PAPEL": "ALVO", "URL": "u", "SHA256": "0" * 64,
                                                      "BYTES_EM": str(tmp / "V04" / "1_ALVO.bin")}]}]}
        (tmp / "RECIBO-RONDA-1.json").write_text(json.dumps(rec), encoding="utf-8")
        plano = {"FICHAS": [{"ID": "V04", "PESSOA": "Silvia Toffolati"}]}
        self.assertEqual(L.ler_passo1(plano, tmp)["V04"]["PAPEL_PROVADO"], "NAO SEI")
        rec["COLHIDAS"][0]["PROVAS"][0]["SHA256"] = hashlib.sha256(b).hexdigest()
        (tmp / "RECIBO-RONDA-1.json").write_text(json.dumps(rec), encoding="utf-8")
        self.assertEqual(L.ler_passo1(plano, tmp)["V04"]["PAPEL_PROVADO"], "SIM")

    def test_descricao_do_youtube_le_o_json(self):
        b = b'..."shortDescription":"Intervista al prof. Bruno Basso\\nMichigan","isCrawlable"...'
        self.assertIn("prof. Bruno Basso\nMichigan", L.descricao_youtube(b))


if __name__ == "__main__":
    unittest.main()
