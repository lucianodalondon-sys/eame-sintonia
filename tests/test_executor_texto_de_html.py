# -*- coding: utf-8 -*-
"""O EXECUTOR DE TEXTO DE HTML — a espécie que faltava à derivação.

Medido na Big Collection 2 (20/09/2026): 46 observações `text/html` saíram da
etapa DERIVED como NOT_APPLICABLE porque nenhum executor declarava a espécie,
e a Admissão respondeu NAO_SEI a documentos sem texto. Estas provas guardam:

  1. a porta encaminha `text/html` para este executor (e só ela decide);
  2. o texto visível sai, e o invisível (script/style/comentários) não;
  3. entidades e charset não fazem a extracção mentir;
  4. página sem texto visível é TEXT_LAYER_ABSENT — não é sucesso vazio;
  5. as medidas dizem o que medem; HTML_KIND é leitura, não veredito;
  6. o executor não sabe o que é rede, banco ou corrida.

    UM DOCUMENTO SEM TEXTO NÃO É JULGADO. É ADIADO.
"""
import os
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import executor_texto_de_html as H  # noqa: E402
import ingresso as ing  # noqa: E402
import artefato as art  # noqa: E402


class APortaEncaminha(unittest.TestCase):

    def test_text_html_vai_para_este_executor(self):
        mod = ing.executor_para("text/html")
        self.assertIsNotNone(mod, "text/html continua sem executor: NOT_APPLICABLE outra vez")
        self.assertEqual(mod.EXECUTOR_ID, H.EXECUTOR_ID)
        self.assertEqual(ing.executor_para("text/html; charset=utf-8").EXECUTOR_ID, H.EXECUTOR_ID)

    def test_o_pdf_continua_com_o_seu_dono(self):
        self.assertEqual(ing.executor_para("application/pdf").EXECUTOR_ID, "texto-de-pdf")

    def test_a_capacidade_diz_que_nao_vai_a_rede(self):
        self.assertEqual(H.CAPACIDADE["NETWORK_REQUIRED"], "NO")
        self.assertEqual(H.CAPACIDADE["COST_CLASS"], "LOCAL")
        self.assertIn("text/html", H.CAPACIDADE["ACEITA_MEDIA_TYPES"])


class OTextoVisivelSaiEOInvisivelNao(unittest.TestCase):

    HTML = (b"<html><head><title>Bollettino &amp; avvisi</title>"
            b"<style>p{color:red}</style><script>var x = 'NAO';</script></head>"
            b"<body><!-- comentario escondido --><nav><a href='/a'>Home</a><a href='/b'>Menu</a></nav>"
            b"<h1>Mosca dell&#39;olivo</h1><p>Catture   in aumento\n  nel comprensorio.</p>"
            b"<noscript>ative o javascript</noscript><p>Soglia superata.</p></body></html>")

    def test_script_style_e_comentarios_ficam_de_fora(self):
        texto, m = H.texto_de_html(self.HTML)
        self.assertNotIn("color:red", texto)
        self.assertNotIn("var x", texto)
        self.assertNotIn("comentario escondido", texto)
        self.assertNotIn("ative o javascript", texto)

    def test_o_que_uma_pessoa_le_esta_la_e_com_entidades_decodificadas(self):
        texto, m = H.texto_de_html(self.HTML)
        self.assertIn("Bollettino & avvisi", texto)
        self.assertIn("Mosca dell'olivo", texto)
        self.assertIn("Catture in aumento nel comprensorio.", texto)
        self.assertIn("Soglia superata.", texto)
        self.assertEqual(m["TITLE"], "Bollettino & avvisi")
        self.assertEqual(m["LINKS"], 2)

    def test_blocos_viram_linhas_e_o_espaco_normaliza(self):
        texto, _ = H.texto_de_html(b"<div>um</div><div>dois   tres</div><p>quatro</p>")
        self.assertEqual(texto.split("\n"), ["um", "dois tres", "quatro"])

    def test_charset_declarado_e_respeitado_quando_nao_e_utf8(self):
        corpo = "<html><head><meta charset=\"iso-8859-1\"></head><body><p>Città più</p></body></html>"
        texto, _ = H.texto_de_html(corpo.encode("latin-1"))
        self.assertIn("Città più", texto)

    def test_bom_utf8_nao_atrapalha(self):
        texto, _ = H.texto_de_html(b"\xef\xbb\xbf" + "<p>Olá</p>".encode("utf-8"))
        self.assertEqual(texto, "Olá")


class SemTextoNaoESucesso(unittest.TestCase):

    def test_pagina_so_com_script_e_TEXT_LAYER_ABSENT(self):
        tmp = tempfile.mkdtemp()
        p = os.path.join(tmp, "vazia.html")
        with open(p, "wb") as fh:
            fh.write(b"<html><head><script>x()</script></head><body></body></html>")
        texto, estado, erro, m = H.extrair(p)
        self.assertEqual(estado, art.TEXT_LAYER_ABSENT)
        self.assertEqual(m["NON_WHITESPACE_CHARACTERS"], 0)
        self.assertEqual(m["HTML_KIND"], "EMPTY")

    def test_ficheiro_inexistente_e_EXTRACTION_ERROR_e_nao_documento_vazio(self):
        texto, estado, erro, m = H.extrair(os.path.join(tempfile.gettempdir(), "nao-existe-%d.html" % os.getpid()))
        self.assertEqual(estado, art.EXTRACTION_ERROR)
        self.assertTrue(erro)

    def test_derivar_um_sem_texto_devolve_SEM_DERIVADO_e_nao_escreve(self):
        tmp = tempfile.mkdtemp()
        p = os.path.join(tmp, "vazia.html")
        with open(p, "wb") as fh:
            fh.write(b"<html><body><style>a{}</style></body></html>")
        chamado = []

        class ArmazemQueGrita:
            def enviar(self, *a, **k):
                chamado.append(a)
        r = H.derivar_um(1, p, ArmazemQueGrita(), None)
        self.assertEqual(r["ESTADO"], "SEM_DERIVADO")
        self.assertEqual(r["MOTIVO_DO_EXECUTOR"], art.TEXT_LAYER_ABSENT)
        self.assertEqual(chamado, [], "escreveu um derivado sem texto")


class AsMedidasDizemOQueMedem(unittest.TestCase):

    def test_kind_e_leitura_das_medidas(self):
        self.assertEqual(H._kind(0, 0, 0), "EMPTY")
        self.assertEqual(H._kind(2000, 1500, 10), "CONTENT")
        self.assertEqual(H._kind(2000, 100, 120), "NAVIGATION")
        self.assertEqual(H._kind(2000, 100, 5), "MIXED")

    def test_li_e_td_nao_contam_como_paragrafo(self):
        _, m = H.texto_de_html(b"<ul><li>menu um</li><li>menu dois</li></ul><p>corpo</p>")
        self.assertEqual(m["PARAGRAPH_CHARACTERS"], len("corpo"))

    def test_o_executor_nao_conhece_rede_nem_banco(self):
        src = open(os.path.join(RAIZ, "coleta", "executor_texto_de_html.py"), encoding="utf-8").read()
        for proibido in ("urllib", "requests", "http.client", "psycopg", "subprocess", "socket"):
            self.assertNotIn("import " + proibido, src, proibido)


if __name__ == "__main__":
    unittest.main()
