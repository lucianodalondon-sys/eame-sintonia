# -*- coding: utf-8 -*-
"""PAGINA-DO-DOCENTE · os leitores por universidade e as rodadas, sem rede (fixtures reais P5 + sinteticas)."""
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas" / "pagina_docente"))
import leitor as L          # noqa: E402
import rodadas as R         # noqa: E402
import universidades as U   # noqa: E402

FX = RAIZ / "ferramentas" / "pagina_docente" / "fixtures"
ORIGEM = json.loads((FX / "ORIGEM-DAS-FIXTURES.json").read_text(encoding="utf-8"))


def fx(nome):
    return (FX / nome).read_text(encoding="utf-8")


def url_de(nome):
    return ORIGEM[nome]["URL"]


def ler(nome, uni, moldura=frozenset()):
    return L.ler_pagina(fx(nome), url_de(nome), uni, moldura)


class Registo(unittest.TestCase):
    def test_as_19_e_nenhuma_entrada_inventada(self):
        self.assertEqual(19, len(U.UNIVERSIDADES))
        for uni, u in U.UNIVERSIDADES.items():
            self.assertTrue(u["PROVA_ENTRADA"], uni)
            for _, e in u["ENTRADAS"]:
                self.assertTrue(L.mesmo_dominio(e, u["DOMINIO"]), (uni, e))
            self.assertIn(u["FORMA"], R.POR_RODADA)
            self.assertEqual(u["FORMA"] == "MEDIDA_EM_BYTES", bool(u["BLOCO"]), uni)

    def test_nome_do_mur_e_da_consulta2(self):
        self.assertEqual((["toffolatti"], ["silvia", "laura"]), L.partes_do_nome("TOFFOLATTI Silvia Laura"))
        self.assertEqual((["de", "miccolis", "angelini"], ["rita", "milvia"]),
                         L.partes_do_nome("DE MICCOLIS ANGELINI Rita Milvia"))
        self.assertEqual((["zappala"], ["lucia"]), L.partes_do_nome("Lucia Zappalà"))


class AcharNaLista(unittest.TestCase):
    """Bytes reais das listas guardadas pela P5."""

    def test_milano_palermo_verona_padova(self):
        casos = [("milano-lista-disaa.html", "MILANO", "TOFFOLATTI Silvia Laura", "person0000044501"),
                 ("palermo-lista-saaf.html", "PALERMO", "MATIC Slavica", "slavica.matic"),
                 ("verona-lista-dbt.html", "VERONA", "ZACCONE Claudio", "id=54972"),
                 ("padova-lista-dafnae.html", "PADOVA", "DUSO Carlo", "3823C39E7E88165D4708813851177874")]
        for f, uni, nome, pedaco in casos:
            r = L.achar_pessoa(fx(f), url_de(f), {"NOME": nome}, uni)
            self.assertEqual("ACHEI", r["ESTADO"], (uni, r))
            self.assertIn(pedaco, r["URL"])

    def test_udine_o_nome_esta_no_cartao_e_a_lista_tem_paginas(self):
        f = "udine-lista-di4a-p0.html"
        r = L.achar_pessoa(fx(f), url_de(f), {"NOME": "ANNOSCIA Desiderato"}, "UDINE")
        self.assertEqual("ACHEI", r["ESTADO"])
        self.assertIn("0931d0f9a6250eb45671a10467c64cfd", r["URL"])
        self.assertIn("b_start:int=10", L.proximas_paginas(fx(f), url_de(f), "UDINE")[0])

    def test_so_o_sobrenome_nao_acha_e_dois_enderecos_sao_ambiguos(self):
        f = "milano-lista-disaa.html"
        self.assertEqual("NAO_ACHEI", L.achar_pessoa(fx(f), url_de(f), {"NOME": "TOFFOLATTI Mario"}, "MILANO")["ESTADO"])
        html = ('<a href="/persone/mario-rossi/">Mario Rossi</a><a href="/persone/mario-rossi-2/">Mario Rossi</a>'
                '<a href="https://www.unipi.it/persone/mario-rossi/">Mario Rossi</a>')
        self.assertEqual("AMBIGUO", L.achar_pessoa(html, "https://www.agr.unipi.it/", {"NOME": "ROSSI Mario"}, "PISA")["ESTADO"])

    def test_link_de_outro_dominio_nao_serve(self):
        html = '<a href="https://www.exemplo.com/mario-rossi">Mario Rossi</a>'
        self.assertEqual("NAO_ACHEI", L.achar_pessoa(html, "https://www.agr.unipi.it/", {"NOME": "ROSSI Mario"}, "PISA")["ESTADO"])


class LerPagina(unittest.TestCase):
    """O corte do BLOCO: a pagina real de Palermo tem Facebook/Instagram/YouTube/LinkedIn/X DA UNIVERSIDADE."""

    def test_palermo_as_redes_da_universidade_nao_sao_da_pessoa(self):
        html = fx("palermo-pessoa-matic.html")
        self.assertIn("facebook.com/universitapalermo", html)
        r = ler("palermo-pessoa-matic.html", "PALERMO")
        self.assertEqual("BLOCO_MEDIDO", r["BLOCO"])
        self.assertEqual([], r["CANAIS"] + r["NAO_ENTRAM"])

    def test_milano_o_youtube_dentro_do_bloco_entra(self):
        r = ler("milano-pessoa-com-youtube.html", "MILANO")
        self.assertEqual(["YOUTUBE"], [c["PLATAFORMA"] for c in r["CANAIS"]])
        self.assertIn("PAGINA OFICIAL DO DOCENTE (MILANO)", r["CANAIS"][0]["PROVA"])

    def test_verona_perfis_ficam_fora_e_nada_entra(self):
        r = ler("verona-pessoa-com-perfis.html", "VERONA")
        self.assertEqual([], r["CANAIS"])
        self.assertEqual({"LINKEDIN_PERFIL", "RESEARCHGATE", "GOOGLE_SCHOLAR", "ORCID"},
                         {c["PLATAFORMA"] for c in r["NAO_ENTRAM"]})

    def test_udine_sito_personale_e_segundo_passo(self):
        r = ler("udine-pessoa-di4a.html", "UDINE")
        self.assertEqual("SITO_PERSONALE", r["PAGINAS_PROPRIAS"][0]["CAMPO"])
        self.assertTrue(r["PAGINAS_PROPRIAS"][0]["URL"].startswith("https://people.uniud.it/"))
        self.assertEqual(R.segundo_passo(r), [r["PAGINAS_PROPRIAS"][0]["URL"]])

    def test_sem_bloco_contas_da_instituicao_saem_e_email_nunca_sai(self):
        base = "https://www.agr.unipi.it/persone/lorenzo-cotrozzi/"
        r = L.ler_pagina(fx("pisa-pessoa-SINTETICA.html"), base, "PISA")
        self.assertEqual("SEM_BLOCO_MEDIDO", r["BLOCO"])
        self.assertEqual({"YOUTUBE", "PAGINA_INSTITUCIONAL_OU_PESSOAL"}, {c["PLATAFORMA"] for c in r["CANAIS"]})
        self.assertEqual({"LINKEDIN_PERFIL", "RESEARCHGATE"}, {c["PLATAFORMA"] for c in r["NAO_ENTRAM"]})
        self.assertEqual(["https://www.larivista.example.org/articolo-123"], [x["URL"] for x in r["EXTERNOS_SEM_ROTULO"]])
        s = json.dumps(r)
        self.assertNotIn("@unipi.it", s)
        self.assertNotIn("2210000", s)
        self.assertNotIn("facebook.com/unipi", s)
        self.assertNotIn("/corsi/", json.dumps(r["PAGINAS_PROPRIAS"]))

    def test_email_e_telefone_no_texto_do_link_nao_saem(self):
        html = ('<main><a href="https://www.youtube.com/@mario-lab">canale di mario.rossi@unipi.it, tel. 050 221 0000</a>'
                '<a href="https://orcid.org/0000-0002-5531-0669">0000-0002-5531-0669</a></main>')
        r = L.ler_pagina(html, "https://www.agr.unipi.it/persone/mario-rossi/", "PISA")
        s = json.dumps(r)
        self.assertNotIn("mario.rossi@", s)
        self.assertNotIn("050 221 0000", s)
        self.assertIn("0000-0002-5531-0669", s)              # o ORCID nao e telefone

    def test_o_nome_tem_de_conferir(self):
        self.assertTrue(L.nome_confere(fx("milano-pessoa-toffolatti.html"), {"NOME": "TOFFOLATTI Silvia Laura"}, "MILANO"))
        self.assertFalse(L.nome_confere(fx("milano-pessoa-com-youtube.html"), {"NOME": "RIGAMONTI Ivo Ercole"}, "MILANO"))

    def test_regra_construida_so_onde_medida(self):
        self.assertEqual("https://www.unimi.it/it/ugov/person/ivo-rigamonti",
                         L.construir({"NOME": "RIGAMONTI Ivo Ercole"}, "MILANO"))
        self.assertEqual("", L.construir({"NOME": "COTROZZI Lorenzo"}, "PISA"))


class Rodadas(unittest.TestCase):
    def correr(self, pasta, n):
        respostas = json.loads((FX / "RESPOSTAS.json").read_text(encoding="utf-8"))

        def falso(url):
            r = respostas.get(url)
            if r is None:
                raise urllib.error.HTTPError(url, 404, "nao ha fixture", {}, None)
            corpo = (FX / r["FICHEIRO"]).read_bytes() if r.get("FICHEIRO") else r.get("TEXTO", "").encode("utf-8")
            return r.get("HTTP", 200), corpo
        pessoas = json.loads((FX / "PESSOAS.json").read_text(encoding="utf-8"))
        saida = pasta / ("RODADA-%02d" % n)
        return R.correr(pessoas, saida, R.S.Transporte(saida, buscar=falso, pausa=0), {}, pasta)

    def test_duas_rodadas(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            r1 = self.correr(d, 1)
            est = {p["NOME"]: p.get("ESTADO") for p in r1["PESSOAS"]}
            # teto: 5 por dominio registavel, contando o robots
            self.assertTrue(r1["TETO_RESPEITADO"])
            self.assertEqual(5, r1["PEDIDOS_POR_DOMINIO"]["unimi.it"])
            self.assertEqual("PENDENTE", est["PIERCE Simon"])
            # regra construida abre outra pessoa: nao se le
            self.assertEqual("NOME_NAO_CONFERE", est["RIGAMONTI Ivo Ercole"])
            # robots que proibe: nada se pede alem do robots
            self.assertEqual("ROBOTS_OU_NAO_LIDO", est["BOSCO Domenico"])
            self.assertEqual(1, r1["PEDIDOS_POR_DOMINIO"]["unito.it"])
            # lista paginada: a 2.a pagina (sintetica) traz a pessoa
            self.assertIn("ffffffff", next(p for p in r1["PESSOAS"] if p["NOME"] == "ZETA Carla")["PASSOS"][0])
            self.assertEqual(["Lucia Zappala"], r1["FORA_DAS_19"])
            self.assertNotIn("FORA Da Prioridade", est)
            # rodada 2: o pendente volta e le-se; o segundo passo abre o site pessoal declarado
            r2 = self.correr(d, 2)
            est2 = {p["NOME"]: p for p in r2["PESSOAS"]}
            self.assertEqual(["YOUTUBE"], [c["PLATAFORMA"] for c in est2["PIERCE Simon"]["CANAIS"]])
            self.assertEqual({"X", "BLUESKY"}, {c["PLATAFORMA"] for c in est2["COTROZZI Lorenzo"]["CANAIS"]})
            self.assertNotIn("TOFFOLATTI Silvia Laura", est2)            # feita: nao se repete
            self.assertIn("ZETA Carla", est2)                             # FALHA de rede volta
            for r in (r1, r2):
                s = json.dumps(r["PESSOAS"])
                self.assertNotIn("mailto", s)
                self.assertNotIn("lab@example.org", s)

    def test_rodada_real_recusa_sem_autorizado(self):
        self.assertEqual(2, R.main(["x", "--rodada=1", "--pessoas=%s" % (FX / "PESSOAS.json"), "--saida=%s" % tempfile.gettempdir()]))


if __name__ == "__main__":
    unittest.main()
