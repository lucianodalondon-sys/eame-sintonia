#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P5 · pessoas pela pagina oficial — sem rede.

O que se guarda:
  · so linkedin.com/in/ e perfil pessoal (company e da organizacao); post de
    Instagram nao e perfil; video solto do YouTube nao e canal;
  · o nome no endereco conta-se sem acento;
  · CREA e Bologna nao sao sementes da P5 (sao da P4);
  · depois da descoberta: tudo o que diz ENTRA esta na fila com a prova da pagina
    oficial da PESSOA, e o rodape da casa nunca entra como pessoa.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "pessoas_docentes"))
import pessoas_docentes as P  # noqa: E402

AQUI = os.path.join(RAIZ, "scripts", "pessoas_docentes")


def _j(nome):
    with open(os.path.join(AQUI, nome), encoding="utf-8") as f:
        return json.load(f)


class AFormaDosLinks(unittest.TestCase):

    def test_1_linkedin_pessoal_sim_empresa_nao(self):
        self.assertEqual(P.social("https://it.linkedin.com/in/mario-rossi-12ab/")[0], "LINKEDIN")
        self.assertEqual(P.social("https://it.linkedin.com/in/mario-rossi-12ab/")[1],
                         "https://www.linkedin.com/in/mario-rossi-12ab")
        self.assertIsNone(P.social("https://www.linkedin.com/company/unimi")[0])
        self.assertIsNone(P.social("https://www.linkedin.com/school/universita-di-padova/")[0])

    def test_2_instagram_perfil_sim_post_nao(self):
        self.assertEqual(P.social("https://www.instagram.com/mario.rossi_agro/")[0], "INSTAGRAM")
        self.assertIsNone(P.social("https://www.instagram.com/p/Cxyz123/")[0])
        self.assertIsNone(P.social("https://www.instagram.com/reel/Cxyz123/")[0])

    def test_3_youtube_canal_sim_video_nao(self):
        self.assertEqual(P.social("https://www.youtube.com/@mariorossi")[0], "YOUTUBE")
        self.assertIsNone(P.social("https://www.youtube.com/watch?v=abc123def45")[0])

    def test_4_nome_no_endereco_sem_acento(self):
        self.assertEqual(P.nome_casa_slug("Prof. Niccolò Pàstore", "niccolo-pastore-1a2b"), 2)
        self.assertEqual(P.nome_casa_slug("Mario Rossi", "agrolab-unipd"), 0)

    def test_5b_marca_d29_nao_acende_por_palavra_solta(self):
        """IPM so como palavra inteira (o \\b perdido virou 0x08 no heredoc e «shipment» passava);
        «cambiamenti climatici» sozinho nao e janela de cultura."""
        import re
        self.assertFalse(re.search(P.D29_TEMAS["FITOSSANIDADE"], "shipment of goods", re.I))
        self.assertTrue(re.search(P.D29_TEMAS["FITOSSANIDADE"], "un approccio IPM per la vite", re.I))
        self.assertFalse(re.search(P.D29_TEMAS["AGROMETEO"], "impatti dei cambiamenti climatici", re.I))
        self.assertTrue(re.search(P.D29_TEMAS["AGROMETEO"], "rete agrometeorologica regionale", re.I))
        with open(P.__file__, encoding="utf-8") as f:
            self.assertNotIn("\x08", f.read())

    def test_5_crea_e_bologna_ficam_com_a_p4(self):
        s = _j("SEMENTES-P5.json")
        hosts = " ".join(x["URL"] for x in s["SEMENTES"])
        self.assertNotIn("crea.gov.it", hosts)
        self.assertNotIn("unibo.it", hosts)
        self.assertIn("crea.gov.it", s["FORA_POR_COORDENACAO"])


@unittest.skipUnless(os.path.exists(os.path.join(AQUI, "DECISOES-P5-V1.json")), "decisoes ainda por escrever")
class ADecisaoEAFila(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.desc = _j("DESCOBERTA-PESSOAS-DOCENTES-V1.json")
        cls.dec = {x["URL"]: x for x in _j("DECISOES-P5-V1.json")["DECISOES"]}
        with open(os.path.join(RAIZ, "candidatas", "FONTES-CANDIDATAS.json"), encoding="utf-8") as f:
            cls.fila = {c["URL"]: c for c in json.load(f)["CANDIDATAS"]}

    def test_6_todo_perfil_achado_tem_decisao_escrita(self):
        urls = {x["URL"] for s in self.desc["SEMENTES"].values() for p in s.get("PESSOAS", [])
                for x in p.get("SOCIAIS", [])}
        for u in urls:
            self.assertIn(u, self.dec, u)
            self.assertIn(self.dec[u]["DECISAO"], ("ENTRA", "FICA_FORA", "JA_CONHECIDO"), u)
            self.assertTrue(self.dec[u]["PORQUE"].strip(), u)

    def test_7_o_que_entra_esta_na_fila_com_a_pagina_da_pessoa(self):
        for u, x in self.dec.items():
            if x["DECISAO"] != "ENTRA":
                continue
            c = self.fila.get(u)
            self.assertIsNotNone(c, u)
            self.assertIn("P5 D24 · IDENTIDADE: a pagina oficial da pessoa", c["NOTA"])
            self.assertIn("descoberta-indireta:site-da-organizacao", c["NOTA"])
            self.assertEqual(c["PAIS"], "IT", u)
            self.assertEqual(c["ESTADO"], "CANDIDATA")

    def test_8_o_rodape_da_casa_nunca_e_pessoa(self):
        for s in self.desc["SEMENTES"].values():
            inst = set(s.get("INSTITUCIONAIS", []))
            for p in s.get("PESSOAS", []):
                for x in p.get("SOCIAIS", []):
                    self.assertNotIn(x["URL"], inst)

    def test_9_todos_os_portoes_que_deixaram_passar_eram_IT(self):
        for p in self.desc["PORTOES"]:
            if p["GATE"] == "PASS":
                self.assertEqual(p["PAIS"], "IT", p)


if __name__ == "__main__":
    unittest.main(verbosity=2)
