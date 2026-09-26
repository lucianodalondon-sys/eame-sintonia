# -*- coding: utf-8 -*-
"""SEGUIR-PESQUISADORES (D85) · quem seguir e como, sem rede: identidade, canais, teto, robots, porta."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas" / "seguir_pesquisadores"))
import pessoas as PE   # noqa: E402
import seguir as S     # noqa: E402

FX = RAIZ / "ferramentas" / "seguir_pesquisadores" / "fixtures"


class Identidade(unittest.TestCase):
    def test_nome_do_mur_e_universidade(self):
        self.assertEqual(("bosco", "domenico"), PE.partir_nome_mur("BOSCO Domenico"))
        self.assertEqual(("de curtis", "filippo"), PE.partir_nome_mur("DE CURTIS Filippo"))
        self.assertTrue(PE.mesma_universidade("TORINO", {"University of Turin"}))
        self.assertTrue(PE.mesma_universidade("Cattolica del Sacro Cuore", {"Università Cattolica del Sacro Cuore"}))
        self.assertFalse(PE.mesma_universidade("TORINO", {"University of Padua"}))

    def test_so_o_nome_nao_liga_e_dois_iguais_sao_ambiguos(self):
        mur = [{"Cognome e Nome": "ROSSI Mario", "Ateneo": "PADOVA", "Fascia": "Ordinario", "SSD 2024": "AGRI-05/A"}]

        def u(oid, nome, inst):
            return {"DOI": "10.1/%s" % oid, "PUBLICADO_EM": "2025-01-01", "NA_CONSULTA_E_NO_TEXTO": ["vite x peronospora"],
                    "AUTORES": [{"OPENALEX_ID": oid, "NOME": nome, "AFILIACAO_ITALIANA_NESTA_OBRA": True,
                                 "ORCID_NO_INDICE": "NAO SEI", "INSTITUICOES_NESTA_OBRA": [{"NOME": inst, "PAIS": "IT"}]}]}
        outra = PE.montar(mur, {"UNIDADES": [u("A1", "Mario Rossi", "University of Pisa")]}, {})
        self.assertEqual("SO_NOME_OUTRA_UNIVERSIDADE", outra[0]["LIGACAO_T6"])
        dois = PE.montar(mur, {"UNIDADES": [u("A1", "Mario Rossi", "University of Padua"),
                                            u("A2", "M. Rossi", "University of Padua")]}, {})
        self.assertEqual("AMBIGUO", dois[0]["LIGACAO_T6"])
        um = PE.montar(mur, {"UNIDADES": [u("A1", "Mario Rossi", "University of Padua")]}, {})
        self.assertEqual(("NOME+UNIVERSIDADE", 1), (um[0]["LIGACAO_T6"], um[0]["PAR_DO_CASCO_RECENTE"]))

    def test_inicial_diferente_nao_liga(self):
        # D85: «Daniele» Bosco nao e «Domenico» Bosco — mas a inicial e a mesma; o nome inteiro nao e exigido,
        # e por isso a UNIVERSIDADE e parte obrigatoria da ligacao
        self.assertFalse(PE.casa_nome("bosco", "domenico", {"Paolo Bosco"}))
        self.assertTrue(PE.casa_nome("bosco", "domenico", {"D. Bosco", "Domenico Bosco"}))


class Canais(unittest.TestCase):
    def test_classificar(self):
        c = lambda u: S.classificar(u)[:3:2]   # noqa: E731  (plataforma, entra?)
        self.assertEqual(("LINKEDIN_PERFIL", False), c("https://www.linkedin.com/in/mario-rossi/"))
        self.assertEqual(("LINKEDIN_POST", True), c("https://www.linkedin.com/posts/x_y-activity-1-a"))
        self.assertEqual(("YOUTUBE", True), c("https://www.youtube.com/@labrossi"))
        self.assertEqual(("X", True), c("https://x.com/rossi"))
        self.assertEqual(("BLUESKY", True), c("https://bsky.app/profile/a.bsky.social"))
        self.assertEqual(("RESEARCHGATE", False), c("https://www.researchgate.net/profile/M-R"))
        self.assertEqual(("PAGINA_INSTITUCIONAL_OU_PESSOAL", True), c("https://www.unipd.it/persone/rossi"))

    def test_dominio_registavel(self):
        self.assertEqual("orcid.org", S.dominio("https://pub.orcid.org/v3.0/x"))
        self.assertEqual("unipd.it", S.dominio("https://www.agraria.unipd.it/p"))

    def test_links_ignoram_mail_e_telefone(self):
        ls = S.links_da_pagina("<a href='mailto:a@b.it'>m</a><a href='tel:1'>t</a><a href='/x'>x</a>", "https://u.it/p")
        self.assertEqual(["https://u.it/x"], ls)


class Transporte(unittest.TestCase):
    def falso(self, respostas, pedidos):
        def f(url):
            pedidos.append(url)
            if url not in respostas:
                raise S.urllib.error.HTTPError(url, 404, "x", {}, None)
            return 200, respostas[url].encode()
        return f

    def test_teto_por_dominio_conta_o_robots(self):
        with tempfile.TemporaryDirectory() as d:
            pedidos = []
            r = {"https://a.it/robots.txt": "User-agent: *\nAllow: /\n"}
            r.update({"https://a.it/p%d" % i: "ok" for i in range(10)})
            t = S.Transporte(Path(d), buscar=self.falso(r, pedidos), pausa=0)
            for i in range(10):
                t.get("https://a.it/p%d" % i, "t")
            self.assertEqual(5, len(pedidos))                 # robots + 4
            self.assertEqual(5, t.conta["a.it"])
            self.assertEqual(6, sum(1 for x in t.registo if x["RESULTADO"] == "TETO_DO_DOMINIO"))

    def test_robots_que_proibe_nao_se_pede(self):
        with tempfile.TemporaryDirectory() as d:
            pedidos = []
            r = {"https://b.it/robots.txt": "User-agent: *\nDisallow: /\n", "https://b.it/p": "ok"}
            t = S.Transporte(Path(d), buscar=self.falso(r, pedidos), pausa=0)
            self.assertEqual((None, None), t.get("https://b.it/p", "t"))
            self.assertEqual(["https://b.it/robots.txt"], pedidos)


class Ensaio(unittest.TestCase):
    def test_fixtures_de_ponta_a_ponta_e_a_porta_numa_copia(self):
        with tempfile.TemporaryDirectory() as d:
            saida = Path(d) / "RODADA-01"
            rc = S.main(["x", "--seco", "--fixtures=%s" % FX, "--pessoas=%s" % (FX / "PESSOAS.json"), "--saida=%s" % saida])
            self.assertEqual(0, rc)
            doc = json.loads((saida / "RESULTADO.json").read_text(encoding="utf-8"))
            self.assertTrue(doc["TETO_RESPEITADO"])
            por = {p["NOME"]: p for p in doc["PESSOAS"]}
            self.assertIn("LINKEDIN_PERFIL", [c["PLATAFORMA"] for c in por["ROSSI Mario"]["NAO_ENTRAM"]])
            self.assertIn("LINKEDIN_POST", [c["PLATAFORMA"] for c in por["ROSSI Mario"]["CANAIS"]])
            self.assertEqual([], por["NERI Paolo"]["CANAIS"])            # sem ORCID
            self.assertEqual([], por["GIALLI Sara"]["CANAIS"])           # dois ORCID
            self.assertEqual("TETO_DO_DOMINIO", por["ROSA Enzo"].get("PENDENTE"))
            fila = Path(d) / "FILA.json"
            fila.write_text(json.dumps({"CANDIDATAS": []}), encoding="utf-8")
            r = S.candidatar([saida], fila)
            linhas = json.loads(fila.read_text(encoding="utf-8"))["CANDIDATAS"]
            self.assertEqual(len(r["CANDIDATAS"]), len(linhas))
            self.assertFalse(any("/in/" in x["URL"] for x in linhas))
            self.assertTrue(all(x["PAIS"] == "IT" and x["PARA_QUE_SERVE"].startswith("D85") for x in linhas))
            self.assertTrue({"YOUTUBE", "LINKEDIN", "CIENCIA", "OUTRO"} <= {x["TIPO"] for x in linhas})


if __name__ == "__main__":
    unittest.main()
