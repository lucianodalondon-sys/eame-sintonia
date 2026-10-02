# -*- coding: utf-8 -*-
"""Camada de texto do FAST: o que o Opus recebe ja' vem sem menu/rodape/formulario/"veja tambem",
e o hash do texto descreve exatamente o que foi entregue ao modelo.

Os testes carregam SO as definicoes do passo1 (o ficheiro, quando corre a serio, le o banco no topo).
"""
import collections, hashlib, os, re, sys, unittest
from html.parser import HTMLParser

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = open(os.path.join(RAIZ, "motor", "fast_auto", "passo1_selecionar.py"), encoding="utf-8").read()
NS = {"__name__": "definicoes", "re": re, "os": os, "Counter": collections.Counter,
      "hashlib": hashlib, "HTMLParser": HTMLParser}
exec(FONTE[FONTE.index("LIMITE_ENTREGA_CHARS = int("):FONTE.index("env = dict(os.environ")] + "\n" +
     FONTE[FONTE.index("TAGS_CASCA = {"):FONTE.index("os.makedirs(AQUI")], NS)

PAGINA = """<html><head><title>t</title>
<script>var x=1;</script></head>
<body class="wp-singular post-template-default single navigation">
  <header id="topbar"><a href="/">Home</a><a href="/x">Contatti</a></header>
  <nav><ul><li class="menu-item menu-item-12">Colture</li><li>Mercati</li></ul></nav>
  <div class="cookiebanner cmplz-cookiebanner">Usiamo cookie per migliorare l'esperienza</div>
  <div class="entry-content">
    <h1>Peronospora in Veneto</h1>
    <p>La peronospora della vite e' stata segnalata in Veneto dopo le piogge di fine settembre, con
       sintomi su foglie e grappoli nelle province di Treviso e Padova.</p>
    <p>Secondo il bollettino, la difesa va impostata entro sette giorni dalla comparsa dei sintomi
       visibili, privilegiando i prodotti rameici autorizzati sulla coltura.</p>
  </div>
  <aside class="related"><h3>Leggi anche</h3><a href="/a">Altro articolo sulla soia</a></aside>
  <form class="login-form"><label>Nome utente o indirizzo email</label><input name="u"><button>Accedi</button></form>
  <footer class="site-footer"><p>Sede legale Via Eritrea 21</p><p>Pubblicita</p></footer>
</body></html>"""


class Casca(unittest.TestCase):
    def _texto(self, html, nome="p.html"):
        import tempfile
        p = os.path.join(tempfile.mkdtemp(), nome)
        open(p, "wb").write(html.encode("utf-8"))
        return NS["bruto"](p, "text/html")[1]

    def test_menu_rodape_formulario_relacionados_fora(self):
        t = self._texto(PAGINA)
        for lixo in ["Contatti", "Colture", "Usiamo cookie", "Leggi anche", "Altro articolo sulla soia",
                     "Nome utente o indirizzo email", "Accedi", "Sede legale Via Eritrea 21", "Pubblicita", "var x=1"]:
            self.assertNotIn(lixo, t, "casca entregue ao modelo: %r" % lixo)

    def test_corpo_da_materia_sobrevive_inteiro(self):
        t = self._texto(PAGINA)
        self.assertIn("Peronospora in Veneto", t)
        self.assertIn("segnalata in Veneto dopo le piogge di fine settembre", t)
        self.assertIn("la difesa va impostata entro sette giorni", t)
        self.assertIn("prodotti rameici autorizzati sulla coltura", t)

    def test_wrapper_com_navigation_no_class_nao_engole_a_materia(self):
        # contraprova do defeito medido: casar "navigation" por substring derrubaria a pagina toda
        t = self._texto(PAGINA)
        self.assertGreater(len(t), 400)

    def test_head_sem_fecho_nao_entrega_documento_vazio(self):
        # defeito medido numa prova: <head>/<title> sem </head> deixava o corpo inteiro fora, em silencio
        t = self._texto("<html><head><title>t</title><body><p>Materia sobre a soia no Veneto com texto suficiente</p></body></html>")
        self.assertIn("Materia sobre a soia no Veneto", t)

    def test_fonte_do_texto_e_uma_so(self):
        # nao existe extrator paralelo: a classe que le HTML->texto vive no passo1, e so' la'
        self.assertIn("class T(HTMLParser)", NS["__name__"] == "definicoes" and FONTE)
        for raiz, _, arqs in os.walk(RAIZ):
            if os.sep + ".git" in raiz:
                continue
            for a in arqs:
                if a.endswith(".py") and "extra" in a.lower() and "test" not in a.lower():
                    self.assertNotIn("fast_auto", raiz, "extrator paralelo dentro do FAST: %s" % a)


class TemplateDaRodada(unittest.TestCase):
    def test_linha_curta_repetida_em_3_documentos_sai(self):
        docs = {1: "Corpo A\nAbbonati / rinnova", 2: "Corpo B\nAbbonati / rinnova", 3: "Corpo C\nAbbonati / rinnova"}
        tpl = NS["linhas_de_template"](docs)
        self.assertIn("abbonati / rinnova", tpl)
        self.assertEqual(NS["tira_template"]("Corpo A\nAbbonati / rinnova", tpl)[0], "Corpo A")

    def test_linha_curta_em_dois_documentos_fica(self):
        docs = {1: "Corpo A\nSolo due", 2: "Corpo B\nSolo due"}
        self.assertNotIn("solo due", NS["linhas_de_template"](docs))

    def test_linha_longa_repetida_fica(self):
        longa = "Segundo o bollettino, a defesa deve ser feita em sete dias apos os sintomas visiveis na folha e no cacho"
        docs = {1: "A\n" + longa, 2: "B\n" + longa, 3: "C\n" + longa}
        self.assertNotIn(longa.lower(), NS["linhas_de_template"](docs))

    def test_guarda_nao_corta_o_corpo_em_silencio(self):
        # limpeza que derruba tudo (prosa tambem) tem de ser recusada pela guarda do passo1
        grande = "linha curta\n" * 300 + ("frase de materia bem mais longa que oitenta caracteres para marcar prosa real no documento " * 6)
        tpl = {"linha curta"}
        limpo, _, _ = NS["tira_template"](NS["normaliza"](grande), tpl)
        prosa = sum(len(l) for l in limpo.split("\n") if len(l) >= 80)
        self.assertLess(len(limpo), 0.15 * len(NS["normaliza"](grande)))
        self.assertGreater(prosa, NS["PROSA_MINIMA"])   # e' por isso que o passo1 NAO recusa este caso


class HashDoEntregue(unittest.TestCase):
    def test_hash_do_texto_e_o_hash_do_ficheiro_em_disco(self):
        import tempfile
        texto = "linha um\nlinha dois com acento ção"
        d = tempfile.mkdtemp()
        p = os.path.join(d, "RAW-1.txt")
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(texto)
        bytes_disco = open(p, "rb").read()
        self.assertEqual(hashlib.sha256(texto.encode("utf-8")).hexdigest(), hashlib.sha256(bytes_disco).hexdigest())
        self.assertEqual(texto, open(p, encoding="utf-8").read())

    def test_passo2_hasheia_o_corte_e_nao_o_ficheiro_todo(self):
        src = open(os.path.join(RAIZ, "motor", "fast_auto", "passo2_fatos.py"), encoding="utf-8").read()
        self.assertIn('TEXTO_ENTREGUE_SHA256=hashlib.sha256(corte.encode("utf-8")).hexdigest()', src)
        self.assertIn("CONFERE_COM_DOCUMENTOS", src)
        self.assertIn("LIMITE_ENTREGA_CHARS", src)
        self.assertNotIn("MAX_CHARS = 18000", src)   # o dono do limite e' o passo1
        self.assertIn("tn = norm(corte)", src)       # o TRECHO e' conferido no que o modelo viu


if __name__ == "__main__":
    unittest.main()
