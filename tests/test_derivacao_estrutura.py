#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DERIVACAO-ESTRUTURA (28/09) — o elo 3 do canário 1149, e só ele.

    B1 · `coleta/texto_fonte.py::limpar` deixa de achatar: etiqueta de BLOCO -> `\\n`,
         as outras -> espaço (como antes). Medido no RAW 2272 (CREA, derived:1149):
         1 linha -> 80 linhas, e o `corpo()` que JÁ existe deixa de sair vazio.
    B2 · `executor_texto_de_html.tempo_de_publicacao` ganha UM nível, estreito, no fim:
         `DIV.content-date` irmão de `content-category` dentro de `content-metadata`,
         com valor que seja data completa `DD mmm AAAA` em italiano. Tudo o resto é
         NAO SEI com porquê. Nunca muda o que os cinco níveis da D61 já davam.

O RAW real vem de `tests/fixtures/canario_1149/RAW-2272.html` e só se LÊ (o sha256
é conferido: um byte mexido reprova).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for g in (RAIZ, os.path.join(RAIZ, "leis")):
    if g not in sys.path:
        sys.path.insert(0, g)

import _gavetas  # noqa: E402,F401
from coleta import executor_texto_de_html as ex  # noqa: E402
from coleta import texto_fonte as tf  # noqa: E402
import fato_do_texto as FT  # noqa: E402

NAO_SEI = "NAO SEI"
RAW_2272 = os.path.join(RAIZ, "tests", "fixtures", "canario_1149", "RAW-2272.html")
SHA_2272 = "f2158520f2362956756e31864406962e68ce6632206a4ce56e078e826a953d01"


def _raw():
    with open(RAW_2272, "rb") as fh:
        return fh.read()


def _meta(categoria="COMUNICATO STAMPA", data=" 22 giu 2026 ", classe_data="content-date",
          classe_cat="content-category", classe_meta="content-metadata"):
    """A forma medida no CREA, com as peças trocáveis."""
    cat = '<div class="%s">%s</div>' % (classe_cat, categoria) if categoria is not None else ""
    return ('<div class="%s">%s &nbsp;<span class="material-icons">remove</span>&nbsp; '
            '<div class="%s">%s</div> </div>' % (classe_meta, cat, classe_data, data))


def _pagina(cabeca="", corpo=""):
    return ("<!doctype html><html><head><title>t</title>%s</head><body>"
            "<main>%s<p>Una frase di corpo abbastanza lunga per contare come testo.</p>"
            "</main></body></html>" % (cabeca, corpo)).encode("utf-8")


# ── B1 ────────────────────────────────────────────────────────────────────
class B1AEstruturaDeBlocoSobrevive(unittest.TestCase):

    def test_cada_etiqueta_de_bloco_parte_a_linha(self):
        for tag in tf.BLOCOS:
            with self.subTest(tag=tag):
                if tag in ("br", "hr"):
                    html = b"antes<%s>depois" % tag.encode()
                else:
                    html = b"antes<%s class='x'>meio</%s>depois" % (tag.encode(), tag.encode())
                linhas = tf.limpar(html, "text/html").split("\n")
                self.assertEqual(linhas[0], "antes")
                self.assertEqual(linhas[-1], "depois")

    def test_maiusculas_e_autofechadas_tambem(self):
        self.assertEqual(tf.limpar(b"a<BR/>b<Br >c<P>d</P>", "text/html"), "a\nb\nc\nd")

    def test_inline_continua_a_dar_espaco(self):
        self.assertEqual(tf.limpar(b"<p>a<span>b</span><a href='x'>c</a><b>d</b></p>", "text/html"),
                         "a b c d")

    def test_nome_parecido_nao_e_bloco(self):
        # `<pre>` nao e `<p>`; `<thead>` nao e `<th>`; `<param>`/`<pa>` nao sao `<p>`
        self.assertEqual(tf.limpar(b"a<param>b<thead>c</thead><pa>d</pa>e", "text/html"), "a b c d e")

    def test_linhas_vazias_repetidas_colapsam(self):
        t = tf.limpar(b"<div></div><div>\n\n  </div><p>a</p>\n\n\n<p></p><p>b</p>", "text/html")
        self.assertEqual(t, "a\nb")

    def test_script_style_e_entidades_como_antes(self):
        t = tf.limpar(b"<style>p{}</style><script>x='<p>'</script><p>a&amp;b&nbsp;&nbsp;c</p>",
                      "text/html")
        self.assertEqual(t, "a&b c")

    def test_pdf_nao_passa_pelo_ramo_html(self):
        self.assertTrue(tf.limpar(b"%PDF-1.4 nada", "application/pdf").startswith("[PDF"))

    def test_o_raw_2272_e_o_real(self):
        self.assertEqual(hashlib.sha256(_raw()).hexdigest(), SHA_2272)

    def test_raw_2272_sai_com_estrutura(self):
        t = tf.limpar(_raw(), "text/html")
        linhas = t.split("\n")
        # 80 com a `limpar/2`; 82 com a `limpar/3` (DERIVACAO-ESTRUTURA-V2): os dois
        # `<!--<div class="extension">PDF</div>-->` dos anexos. A régua 2 apagava o
        # `-->` porque a etiqueta atravessava a quebra de bloco — o mesmo buraco do
        # balsâmico; a 3 devolve o que a `limpar()` sempre deu ali («… .pdf PDF» / «-->»).
        # O `corpo()` é o mesmo: 7 705 caracteres nas duas.
        self.assertEqual(len(linhas), 82)
        self.assertEqual(linhas[32], "COMUNICATO STAMPA")
        self.assertEqual(linhas[34], "22 giu 2026")
        self.assertTrue(linhas[35].startswith("Xylella fastidiosa: dalla ricerca CREA"))

    def test_raw_2272_o_corpo_que_ja_existe_deixa_de_estar_cego(self):
        # corpo() NAO foi mexido: e o mesmo filtro por linha. Antes: 0 caracteres.
        c = FT.corpo(tf.limpar(_raw(), "text/html"))
        self.assertGreater(len(c), 5000)
        self.assertIn("Philaenus spumarius", c)

    def test_o_executor_usa_a_mesma_limpar(self):
        texto, estado, _e, _m = ex.extrair(_raw(), "text/html")
        self.assertEqual(texto, tf.limpar(_raw(), "text/html"))


# ── B2 ────────────────────────────────────────────────────────────────────
class B2ANormalizacaoDaDataItaliana(unittest.TestCase):

    POSITIVOS = {
        "22 giu 2026": "2026-06-22", "22 giugno 2026": "2026-06-22", "1 gen 2026": "2026-01-01",
        "1 genn. 2026": "2026-01-01", "3 gennaio 2026": "2026-01-03", "4 feb 2026": "2026-02-04",
        "4 febb 2026": "2026-02-04", "5 febbraio 2026": "2026-02-05", "6 mar 2026": "2026-03-06",
        "7 marzo 2026": "2026-03-07", "8 apr 2026": "2026-04-08", "9 aprile 2026": "2026-04-09",
        "10 mag 2026": "2026-05-10", "11 maggio 2026": "2026-05-11", "12 lug 2026": "2026-07-12",
        "13 luglio 2026": "2026-07-13", "14 ago 2026": "2026-08-14", "15 agosto 2026": "2026-08-15",
        "16 set 2026": "2026-09-16", "17 sett. 2026": "2026-09-17", "18 settembre 2026": "2026-09-18",
        "19 ott 2026": "2026-10-19", "20 ottobre 2026": "2026-10-20", "21 nov 2026": "2026-11-21",
        "22 novembre 2026": "2026-11-22", "23 dic 2026": "2026-12-23", "24 dicembre 2026": "2026-12-24",
        "  22\xa0GIU\xa02026 ": "2026-06-22", "22&nbsp;giu&nbsp;2026": "2026-06-22",
        "29 feb 2024": "2024-02-29",
    }
    VENENOS = (
        "2 settimane fa", "3 settimane fa", "ieri", "Data di aggiornamento: 12 giu 2026",
        "Data di verifica 12 giu 2026", "Data di pubblicazione dell'evento: MERCOLEDÌ 15 ottobre 2026",
        "15/09/2026", "15/09/2026, 14/09/2026, 24/06/2026", "2026-06-22", "6 November 2022",
        "27 September 2026", "22-24 giu 2026", "dal 3 al 5 giu 2026", "lunedì 22 giugno 2026",
        "22 giu", "giu 2026", "22 giu 26", "31 feb 2026", "0 giu 2026", "22 giu 2026 ore 10:00",
        "22 giu 2026 - 24 giu 2026", "", "   ",
    )

    def test_positivos_dia(self):
        for v, iso in self.POSITIVOS.items():
            with self.subTest(v=v):
                self.assertEqual(ex.normalizar_data_italiana(v), (iso, "DIA"))

    def test_os_doze_meses_estao_todos(self):
        self.assertEqual(sorted(set(ex.MESES_IT.values())), list(range(1, 13)))

    def test_venenos_nao_viram_data(self):
        for v in self.VENENOS:
            with self.subTest(v=v):
                iso, porque = ex.normalizar_data_italiana(v)
                self.assertIsNone(iso)
                self.assertTrue(porque)


class B2ONivelEstreito(unittest.TestCase):

    def test_raw_2272_ganha_a_data_com_base_e_precisao(self):
        r = ex.tempo_de_publicacao(_raw())
        self.assertEqual((r["VALOR"], r["BASE"], r["PRECISAO"], r["ORIGINAL"]),
                         ("2026-06-22", ex.BASE_CONTENT_DATE, "DIA", "22 giu 2026"))
        self.assertEqual(ex.BASE_CONTENT_DATE, "DIV.content-date (irmão de content-category)")
        for base in ex.ORDEM_DA_PUBLICACAO:
            self.assertIn(base + ": ausente", r["PORQUE"])

    def test_a_forma_medida_responde(self):
        r = ex.tempo_de_publicacao(_pagina(corpo=_meta()))
        self.assertEqual((r["VALOR"], r["BASE"], r["PRECISAO"]),
                         ("2026-06-22", ex.BASE_CONTENT_DATE, "DIA"))

    def test_nunca_vira_fact_time(self):
        c = ex.publicacao_para_o_contrato(ex.tempo_de_publicacao(_raw()))
        self.assertEqual(c, {"PUBLISHED_AT": "2026-06-22",
                             "PUBLISHED_AT_BASIS": ex.BASE_CONTENT_DATE,
                             "PUBLISHED_AT_PRECISION": "DIA"})
        self.assertFalse({k for k in c if "FACT" in k.upper()})

    def test_a_ordem_da_d61_nao_mudou_e_o_estreito_e_o_ultimo(self):
        self.assertEqual((ex.BASE_JSON_LD, ex.BASE_META, ex.BASE_TIME, ex.BASE_ITEMPROP,
                          ex.BASE_INDICE), ex.ORDEM_DA_PUBLICACAO)
        self.assertEqual(ex.ORDEM_COMPLETA, ex.ORDEM_DA_PUBLICACAO + (ex.BASE_CONTENT_DATE,))

    # ── nunca muda um valor que os cinco níveis já dão ──
    def test_os_cinco_niveis_continuam_a_mandar(self):
        ld = ('<script type="application/ld+json">%s</script>'
              % json.dumps({"@type": "NewsArticle", "datePublished": "2025-01-01T10:00:00Z"}))
        casos = (
            (_pagina(ld, _meta()), None, ("2025-01-01T10:00:00+00:00", ex.BASE_JSON_LD)),
            (_pagina('<meta property="article:published_time" content="2025-02-02">', _meta()),
             None, ("2025-02-02", ex.BASE_META)),
            (_pagina(corpo='<time datetime="2025-03-03">x</time>' + _meta()), None,
             ("2025-03-03", ex.BASE_TIME)),
            (_pagina('<meta itemprop="datePublished" content="2025-04-04">', _meta()), None,
             ("2025-04-04", ex.BASE_ITEMPROP)),
            (_pagina(corpo=_meta()), "2025-05-05", ("2025-05-05", ex.BASE_INDICE)),
        )
        for pagina, indice, esperado in casos:
            with self.subTest(esperado=esperado):
                r = ex.tempo_de_publicacao(pagina, data_no_indice=indice)
                self.assertEqual(esperado, (r["VALOR"], r["BASE"]))

    def test_um_nivel_de_cima_ambiguo_nao_e_resolvido_pelo_estreito_com_outro_valor(self):
        # dois <time> diferentes: o <time> cala-se (AMBIGUO), e o estreito so fala por ser o ultimo;
        # o porque guarda a ambiguidade de cima, para ninguem a perder de vista
        p = _pagina(corpo='<time datetime="2025-03-03">a</time><time datetime="2025-03-04">b</time>'
                          + _meta())
        r = ex.tempo_de_publicacao(p)
        self.assertEqual(r["BASE"], ex.BASE_CONTENT_DATE)
        self.assertIn("<time datetime>: AMBIGUO", r["PORQUE"])

    # ── venenos: tudo NAO SEI, com porquê ──
    def _nao_sei(self, pagina, *no_porque):
        r = ex.tempo_de_publicacao(pagina)
        self.assertEqual((r["VALOR"], r["BASE"], r["PRECISAO"]), (NAO_SEI, NAO_SEI, NAO_SEI))
        self.assertIn(ex.BASE_CONTENT_DATE, r["PORQUE"])
        for x in no_porque:
            self.assertIn(x, r["PORQUE"])
        c = ex.publicacao_para_o_contrato(r)
        self.assertNotIn("PUBLISHED_AT", c)
        return r

    def test_veneno_relativo(self):
        self._nao_sei(_pagina(corpo=_meta(data="2 settimane fa")), "nao e data completa")

    def test_veneno_rotulo(self):
        self._nao_sei(_pagina(corpo=_meta(data="Data di aggiornamento: 12 giu 2026")))

    def test_veneno_data_de_evento(self):
        self._nao_sei(_pagina(corpo=_meta(
            categoria="EVENTI", data="Data di pubblicazione dell'evento: MERCOLEDÌ 15 ottobre 2026")))

    def test_veneno_intervalo(self):
        self._nao_sei(_pagina(corpo=_meta(data="22-24 giu 2026")))

    def test_veneno_numerica_e_lista(self):
        self._nao_sei(_pagina(corpo=_meta(data="15/09/2026, 14/09/2026, 24/06/2026")))

    def test_veneno_mais_de_um_campo(self):
        self._nao_sei(_pagina(corpo=_meta() + _meta(data="23 giu 2026")), "AMBIGUO, 2 campos")

    def test_veneno_mais_de_um_campo_mesmo_igual(self):
        self._nao_sei(_pagina(corpo=_meta() + _meta()), "AMBIGUO, 2 campos")

    def test_veneno_dois_content_date_no_mesmo_metadata(self):
        dois = ('<div class="content-metadata"><div class="content-category">X</div>'
                '<div class="content-date">22 giu 2026</div><div class="content-date">1 lug 2026</div></div>')
        self._nao_sei(_pagina(corpo=dois), "AMBIGUO")

    def test_veneno_sem_irmao_categoria(self):
        self._nao_sei(_pagina(corpo=_meta(categoria=None)), "sem irmão content-category")

    def test_veneno_categoria_nao_e_irma_mas_sobrinha(self):
        sobrinha = ('<div class="content-metadata"><div class="wrap"><div class="content-category">X</div>'
                    '</div><div class="content-date">22 giu 2026</div></div>')
        self._nao_sei(_pagina(corpo=sobrinha), "sem irmão content-category")

    def test_veneno_fora_de_content_metadata(self):
        solto = ('<div class="content-category">X</div><div class="content-date">22 giu 2026</div>')
        self._nao_sei(_pagina(corpo=solto), "fora de content-metadata")

    def test_veneno_neta_de_content_metadata(self):
        neta = ('<div class="content-metadata"><div class="content-category">X</div>'
                '<div class="linha"><div class="content-date">22 giu 2026</div></div></div>')
        self._nao_sei(_pagina(corpo=neta), "fora de content-metadata")

    def test_veneno_outra_classe_com_date(self):
        for classe in ("event-date", "date", "post-date", "content-date-evento", "data", "entry-date"):
            with self.subTest(classe=classe):
                self._nao_sei(_pagina(corpo=_meta(classe_data=classe)))

    def test_veneno_barra_lateral_de_ultimos_artigos(self):
        lateral = "".join('<div class="sidebar-item"><div class="date">%s</div></div>' % d
                          for d in ("6 nov 2022", "27 set 2026", "3 ott 2026"))
        self._nao_sei(_pagina(corpo=lateral))

    def test_veneno_span_nao_e_div(self):
        span = ('<div class="content-metadata"><span class="content-category">X</span>'
                '<span class="content-date">22 giu 2026</span></div>')
        self._nao_sei(_pagina(corpo=span))

    def test_veneno_pagina_sem_nada(self):
        self._nao_sei(_pagina(), ex.BASE_CONTENT_DATE + ": ausente")


if __name__ == "__main__":
    unittest.main(verbosity=2)
