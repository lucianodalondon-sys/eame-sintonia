# -*- coding: utf-8 -*-
"""PUBLISHED_AT sobrevive — e FACT_TIME continua sem fallback.

AQUISICAO-DETALHE-V1 (PASSO 6). Medido no canário de 21/09/2026: 66 de 87
páginas de artigo declaravam a data de publicação no HTML (article:published_time)
e nenhum executor a preservava. Estas provas guardam a régua da Bíblia
(COL-LAW-031) na única forma que interessa — com os casos que a fazem reprovar:

  · a data declarada sai como PUBLISHED_AT, com a base ao lado;
  · «actualizado» (og:updated_time) NÃO é publicação;
  · prosa («Pubblicato il 12 settembre 2026») NUNCA vira data;
  · um valor que não tem forma de data não entra;
  · FACT_TIME não aparece nas medidas: este executor não o conhece.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import executor_texto_de_html as H  # noqa: E402


def pagina(head="", corpo="Testo dell'articolo. " * 60):
    return ("<html><head><title>T</title>%s</head><body><p>%s</p></body></html>" % (head, corpo)).encode("utf-8")


class ADataDeclaradaSobrevive(unittest.TestCase):

    def test_1_article_published_time_sai_com_a_base(self):
        _, m = H.texto_de_html(pagina('<meta property="article:published_time" content="2026-09-20T07:03:21+00:00">'))
        self.assertEqual("2026-09-20T07:03:21+00:00", m["PUBLISHED_AT"])
        self.assertEqual("META_ARTICLE_PUBLISHED_TIME", m["PUBLISHED_AT_BASIS"])

    def test_2_jsonld_datePublished_sai_com_a_base(self):
        _, m = H.texto_de_html(pagina('<script type="application/ld+json">{"@type":"NewsArticle","datePublished":"2026-09-17T14:55:00+00:00"}</script>'))
        self.assertEqual("2026-09-17T14:55:00+00:00", m["PUBLISHED_AT"])
        self.assertEqual("JSONLD_DATE_PUBLISHED", m["PUBLISHED_AT_BASIS"])

    def test_3_time_com_pubdate_sai(self):
        _, m = H.texto_de_html(pagina(corpo='<time datetime="2026-09-04" pubdate>4 settembre</time>' + "x " * 500))
        self.assertEqual("2026-09-04", m["PUBLISHED_AT"])
        self.assertEqual("TIME_DATETIME_PUBDATE", m["PUBLISHED_AT_BASIS"])


class OQueNaoEPublicacaoNaoEntra(unittest.TestCase):

    def test_4_sem_data_declarada_e_None_nao_uma_data_inventada(self):
        _, m = H.texto_de_html(pagina())
        self.assertIsNone(m["PUBLISHED_AT"])
        self.assertIsNone(m["PUBLISHED_AT_BASIS"])

    def test_5_actualizado_nao_e_publicado(self):
        _, m = H.texto_de_html(pagina('<meta property="og:updated_time" content="2026-09-04T20:05:01+02:00">'))
        self.assertIsNone(m["PUBLISHED_AT"], "og:updated_time diz quando mudou, nao quando saiu")

    def test_6_prosa_nunca_vira_data(self):
        _, m = H.texto_de_html(pagina(corpo="Pubblicato il 12 settembre 2026 alle 10:30. " + "x " * 500))
        self.assertIsNone(m["PUBLISHED_AT"])

    def test_7_valor_sem_forma_de_data_nao_entra(self):
        _, m = H.texto_de_html(pagina('<meta property="article:published_time" content="ieri">'))
        self.assertIsNone(m["PUBLISHED_AT"])

    def test_8_fact_time_nao_existe_neste_executor(self):
        _, m = H.texto_de_html(pagina('<meta property="article:published_time" content="2026-09-20T07:03:21+00:00">'))
        self.assertNotIn("FACT_TIME", m, "PUBLISHED_AT != FACT_TIME; o executor nao promove nada a facto")
        self.assertFalse(any(k.startswith("FACT_") for k in m))


if __name__ == "__main__":
    unittest.main()
