# -*- coding: utf-8 -*-
"""D80 · o post de um pesquisador so e PROVADO por pagina oficial (ou lista do dono). Sem rede."""
import hashlib
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, "coleta"), os.path.join(RAIZ, "leis")):
    sys.path.insert(0, p)
import _gavetas  # noqa: E402,F401
import prova_de_post_de_pessoa as PP  # noqa: E402

POST = "https://www.linkedin.com/posts/barbara-menin-6b42a449_ricerca-activity-7507010113581314048-KARA"
PAGINA = ("<html><h1>Seminario IBBA</h1><p>Intervento della dott.ssa Bárbara Menin (CNR-IBBA)</p>"
          "<a href='%s'>il video</a></html>" % POST).encode("utf-8")
OFICIAIS = ("ibba.cnr.it",)


def cand(**k):
    c = {"URL": POST, "ORIGEM": "PAGINA_OFICIAL", "PESSOA_NOME": "Barbara Menin",
         "PROVA_PAGINA": {"URL": "https://ibba.cnr.it/eventi/seminario/", "CLASSE": "EVENTO",
                          "SHA256": hashlib.sha256(PAGINA).hexdigest(), "LIDA_EM": "2026-09-26"}}
    c.update(k)
    return c


class D80(unittest.TestCase):
    def test_pagina_oficial_que_cita_e_liga_prova(self):
        r = PP.julgar(cand(), pagina=PAGINA, hosts_oficiais=OFICIAIS)
        self.assertEqual(r["ESTADO"], "PROVADA", r)
        self.assertEqual(r["ACTIVITY_ID"], "7507010113581314048")

    def test_busca_publica_so_descobre(self):
        r = PP.julgar(cand(ORIGEM="BUSCA_PUBLICA"), pagina=PAGINA, hosts_oficiais=OFICIAIS)
        self.assertEqual(r["ESTADO"], "SO_CANDIDATA")

    def test_pagina_que_nao_e_de_casa_oficial_nao_prova(self):
        r = PP.julgar(cand(), pagina=PAGINA, hosts_oficiais=("outra.it",))
        self.assertEqual(r["ESTADO"], "SO_CANDIDATA")
        self.assertIn("casa oficial", r["PORQUE"])

    def test_sem_o_link_ou_sem_o_nome_nao_prova(self):
        sem_link = PAGINA.replace(b"7507010113581314048", b"7000000000000000000")
        r = PP.julgar(cand(PROVA_PAGINA=dict(cand()["PROVA_PAGINA"], SHA256=hashlib.sha256(sem_link).hexdigest())),
                      pagina=sem_link, hosts_oficiais=OFICIAIS)
        self.assertIn("LINK do post", r["PORQUE"])
        r = PP.julgar(cand(PESSOA_NOME="Giovanna Frugis"), pagina=PAGINA, hosts_oficiais=OFICIAIS)
        self.assertIn("NOME da pessoa", r["PORQUE"])
        r = PP.julgar(cand(PESSOA_NOME="Menin"), pagina=PAGINA, hosts_oficiais=OFICIAIS)   # um pedaco nao basta
        self.assertEqual(r["ESTADO"], "SO_CANDIDATA")

    def test_bytes_trocados_nao_provam(self):
        r = PP.julgar(cand(), pagina=PAGINA + b" ", hosts_oficiais=OFICIAIS)
        self.assertIn("sha256", r["PORQUE"])

    def test_perfil_e_login_sao_recusados_pela_trava_do_coletor(self):
        for u in ("https://www.linkedin.com/in/barbara-menin-6b42a449/",
                  "https://www.linkedin.com/login?session_redirect=x"):
            self.assertEqual(PP.julgar(cand(URL=u), pagina=PAGINA, hosts_oficiais=OFICIAIS)["ESTADO"], "RECUSADA")

    def test_lista_do_dono_prova_com_referencia(self):
        self.assertEqual(PP.julgar(cand(ORIGEM="LISTA_DO_DONO", REF_DO_DONO="D80-lista-1"))["ESTADO"], "PROVADA")
        self.assertEqual(PP.julgar(cand(ORIGEM="LISTA_DO_DONO"))["ESTADO"], "SO_CANDIDATA")

    def test_autor_na_colheita(self):
        perfil = "https://www.linkedin.com/in/barbara-menin-6b42a449"
        self.assertTrue(PP.autor_confere("https://it.linkedin.com/in/barbara-menin-6b42a449?trk=x", perfil))
        self.assertFalse(PP.autor_confere("https://www.linkedin.com/in/outra-pessoa", perfil))
        self.assertIsNone(PP.autor_confere("https://it.linkedin.com/company/ibba", perfil))


if __name__ == "__main__":
    unittest.main()
