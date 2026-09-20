#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes do capturador de REAL_EXAMPLE.

    TODA SONDA PRECISA DE UM CASO QUE A FACA DIZER «NAO».

Uma sonda que nunca reprova nao mede nada. Por isso quase todos estes testes
sao NEGATIVOS: endpoint morto, corpo vazio, muro de login, item de outro
dominio, youtube com id do vizinho. Os positivos existem para provar que a
recusa nao e cega.

Nenhum destes testes abre rede: o transporte e substituido por uma funcao de
mentira. O que se testa e a DECISAO, nao a internet.
"""
from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "curadoria"))
import capturador as C  # noqa: E402


def resposta(status=200, corpo=b"", final=None, ct="text/html", falha=None, ok=None):
    return {"OK": (status == 200 if ok is None else ok), "STATUS": status,
            "FINAL_URL": final or "https://exemplo.it/", "CONTENT_TYPE": ct,
            "BYTES": len(corpo), "CORPO": corpo, "FALHA": falha}


#: Corpo de enchimento. O capturador recusa corpos com menos de 200 bytes
#: (EMPTY_BODY), e com razao: uma pagina de 10 bytes nao tem conteudo. Um
#: fixture minusculo dispararia EMPTY_BODY antes da regra sob teste e faria
#: o teste medir outra coisa — foi o que aconteceu na primeira corrida.
ENCHE = b"<!-- " + b"x" * 400 + b" -->"


class Falso:
    """Transporte de mentira: responde por URL, e conta o que lhe pediram.

    ⚠️ CASA POR IGUALDADE, e so depois por sufixo. A primeira versao casava por
    substring, e `exemplo.it/` — prefixo de TUDO no dominio — ganhava de
    `/doc/rel.pdf`: o mock devolvia o indice no lugar do item, e tres testes
    reprovaram por defeito do HARNESS, nao do capturador.

        UM MOCK QUE RESPONDE A PERGUNTA ERRADA
        REPROVA CODIGO CERTO, E MANDA-NOS «CONSERTA-LO».
    """

    def __init__(self, mapa, defeito=None):
        self.mapa, self.defeito, self.pedidos = mapa, defeito, []

    def __call__(self, url, aceita="*/*"):
        self.pedidos.append(url)
        if url in self.mapa:                       # 1) igualdade exata
            return self.mapa[url]
        for chave in sorted(self.mapa, key=len, reverse=True):
            if url.endswith(chave) or chave in url:   # 2) sufixo, depois substring
                return self.mapa[chave]
        return self.defeito or resposta(404, b"", url, falha="HTTP_ERROR", ok=False)


class TesteFamilia(unittest.TestCase):
    def test_familia_por_endereco(self):
        casos = {
            "https://www.youtube.com/@x": "YOUTUBE",
            "https://it.linkedin.com/company/x": "LINKEDIN",
            "https://www.instagram.com/x": "INSTAGRAM",
            "https://www.facebook.com/x": "FACEBOOK",
            "https://a.it/b/c.pdf": "DIRECT_PDF",
            "https://a.it/noticias": "HTML_SITE",
        }
        for url, esperado in casos.items():
            self.assertEqual(C.familia_de(url), esperado, url)

    def test_assinatura_vence_o_cabecalho(self):
        # ⚠️ o teste que importa: Content-Type diz uma coisa, os bytes dizem outra.
        self.assertEqual(C.assinatura(b"%PDF-1.7 ..."), "PDF")
        self.assertEqual(C.assinatura(b"<!DOCTYPE html><html>"), "HTML")
        self.assertEqual(C.assinatura(b'{"a":1}'), "JSON")


class TestePolicy(unittest.TestCase):
    """FASE 10: LinkedIn e Instagram NAO se tocam. E preciso PROVAR que nao."""

    def test_linkedin_e_instagram_nao_geram_pedido_de_rede(self):
        espiao = Falso({}, resposta(200, b"<html>nunca deveria chegar aqui</html>"))
        antigo, C.buscar = C.buscar, espiao
        try:
            for url in ("https://it.linkedin.com/company/x",
                        "https://www.instagram.com/x"):
                f = C.capturar({"CANDIDATA_ID": "X", "URL": url, "NOME": "n",
                                "PAIS": "IT", "TIPO": "T"})
                self.assertEqual(f["CAPTURE_RESULT"], "NOT_ATTEMPTED")
                self.assertEqual(f["CAPTURE_FAILURE_CLASS"], "POLICY")
                self.assertEqual(f["POLICY_STATUS"], "POLICY_BLOCK")
        finally:
            C.buscar = antigo
        # A prova forte: ZERO pedidos de rede.
        self.assertEqual(espiao.pedidos, [], "tocou numa fonte bloqueada por policy")


class TesteHtml(unittest.TestCase):
    def _capturar(self, mapa, defeito=None, cid="T1"):
        antigo, C.buscar = C.buscar, Falso(mapa, defeito)
        try:
            return C.capturar({"CANDIDATA_ID": cid, "URL": "https://exemplo.it/",
                               "NOME": "n", "PAIS": "IT", "TIPO": "ORGANIZACAO"})
        finally:
            C.buscar = antigo

    def test_endpoint_morto_e_HTTP_ERROR_e_nao_juizo_sobre_a_fonte(self):
        f = self._capturar({}, resposta(500, b"", falha="HTTP_ERROR", ok=False))
        self.assertEqual(f["CAPTURE_RESULT"], "FAILED")
        self.assertEqual(f["CAPTURE_FAILURE_CLASS"], "HTTP_ERROR")
        self.assertEqual(f["REAL_EXAMPLE_URL"], "NAO SEI")

    def test_timeout_tem_classe_propria(self):
        f = self._capturar({}, resposta(None, b"", falha="TIMEOUT", ok=False))
        self.assertEqual(f["CAPTURE_FAILURE_CLASS"], "TIMEOUT")

    def test_html_sem_conteudo_e_NO_ITEM_FOUND_e_nao_REJECT(self):
        pagina = b"<html><body>" + b"<a href='/privacy'>p</a>" * 30 + b"</body></html>"
        f = self._capturar({"exemplo.it/": resposta(200, pagina)})
        self.assertEqual(f["CAPTURE_FAILURE_CLASS"], "NO_ITEM_FOUND")
        self.assertEqual(f["ITEMS_OBSERVED_IN_INDEX"], 0)

    def test_corpo_vazio(self):
        f = self._capturar({"exemplo.it/": resposta(200, b"ab")})
        self.assertEqual(f["CAPTURE_FAILURE_CLASS"], "EMPTY_BODY")

    def test_muro_de_login_no_redirect(self):
        f = self._capturar({"exemplo.it/": resposta(
            200, b"<html>x</html>" + ENCHE, final="https://exemplo.it/login")})
        self.assertEqual(f["CAPTURE_FAILURE_CLASS"], "WALL")

    def test_indice_encontra_item_e_guarda_prova(self):
        indice = (b"<html><a href='/notizie/2026/09/boletim'>b</a>"
                  b"<a href='/privacy'>p</a></html>") + ENCHE
        item = b"<html><head><title>Bollettino 12</title></head>2026-09-15</html>" + ENCHE
        f = self._capturar({"exemplo.it/": resposta(200, indice),
                            "/notizie/2026/09": resposta(
                                200, item, final="https://exemplo.it/notizie/2026/09/boletim")},
                           cid="T_OK")
        self.assertEqual(f["CAPTURE_RESULT"], "CAPTURED")
        self.assertEqual(f["REAL_EXAMPLE_TITLE"], "Bollettino 12")
        self.assertEqual(f["REAL_EXAMPLE_PUBLISHED_AT"], "2026-09-15")
        self.assertEqual(f["ROUTE_FAMILY"], "HTML_PUBLIC")
        self.assertEqual(len(f["REAL_EXAMPLE_SHA256"]), 64)
        # a prova tem de existir no disco, senao a captura e uma afirmacao
        self.assertTrue((C.RAIZ / f["EVIDENCE"]).exists())

    def test_pdf_no_indice_ganha_route_family_de_descoberta(self):
        indice = b"<html><a href='/doc/rel.pdf'>r</a></html>" + ENCHE
        f = self._capturar({"exemplo.it/": resposta(200, indice),
                            "/doc/rel.pdf": resposta(200, b"%PDF-1.4 conteudo" + b" " * 400,
                                                final="https://exemplo.it/doc/rel.pdf")},
                           cid="T_PDF")
        self.assertEqual(f["REAL_EXAMPLE_MEDIA_TYPE"], "PDF")
        self.assertEqual(f["ROUTE_FAMILY"], "PDF_DISCOVERY_PAGE")

    def test_item_de_outro_dominio_nao_conta_como_item_desta_fonte(self):
        # ⚠️ o erro que isto impede: atribuir a esta candidata um PDF alheio.
        indice = b"<html><a href='https://outra.it/notizie/2026/09/x.pdf'>x</a></html>" + ENCHE
        f = self._capturar({"exemplo.it/": resposta(200, indice)})
        self.assertEqual(f["CAPTURE_FAILURE_CLASS"], "NO_ITEM_FOUND")

    def test_redirect_preserva_o_endereco_final(self):
        f = self._capturar({"exemplo.it/": resposta(
            200, b"%PDF-1.4 x" + b" " * 400, final="https://exemplo.it/final.pdf", ct="application/pdf")},
            cid="T_RED")
        self.assertEqual(f["FINAL_URL"], "https://exemplo.it/final.pdf")
        self.assertEqual(f["CAPTURE_RESULT"], "CAPTURED")


class TesteItemVsIndice(unittest.TestCase):
    """A REGRESSAO QUE ESTE BLOCO EXISTE PARA IMPEDIR.

    Na primeira corrida ao vivo, tres candidatas foram dadas como CAPTURED e o
    «item real» guardado era `/notizie` e `/website/newsdipartimenti/` — OUTRA
    LISTAGEM. Isso repetiria o defeito da sonda de 14/09 que esta missao existe
    para corrigir, e poria no Atlas uma amostra que nao e um documento.
    """

    def test_listagem_nao_e_item(self):
        for url in ("https://a.it/notizie",
                    "https://a.it/notizie/",
                    "https://a.it/website/newsdipartimenti/",
                    "https://a.it/comunicati-stampa",
                    "https://a.it/pubblicazioni/",
                    "https://a.it/"):
            self.assertFalse(C.parece_item(url), "aceitou listagem como item: %s" % url)

    def test_item_de_verdade_passa(self):
        for url in ("https://a.it/doc/bollettino-2026-09-15.pdf",
                    "https://a.it/notizie/2026/09/allerta-cimice-asiatica",
                    "https://a.it/pagina2864_reportistica.html",
                    "https://a.it/news/allerta-fitosanitaria-veneto"):
            self.assertTrue(C.parece_item(url), "recusou item real: %s" % url)

    def test_indice_que_so_lista_outras_listas_nao_captura(self):
        indice = (b"<html><a href='/notizie'>n</a>"
                  b"<a href='/comunicati-stampa'>c</a></html>") + ENCHE
        antigo, C.buscar = C.buscar, Falso({"exemplo.it/": resposta(200, indice)})
        try:
            f = C.capturar({"CANDIDATA_ID": "T_IDX", "URL": "https://exemplo.it/",
                            "NOME": "n", "PAIS": "IT", "TIPO": "ORGANIZACAO"})
        finally:
            C.buscar = antigo
        self.assertEqual(f["CAPTURE_FAILURE_CLASS"], "NO_ITEM_FOUND")
        self.assertEqual(f["ITEMS_OBSERVED_IN_INDEX"], 0)


class TestePdfDireto(unittest.TestCase):
    def test_pdf_direto(self):
        antigo, C.buscar = C.buscar, Falso(
            {"x.pdf": resposta(200, b"%PDF-1.5 corpo" + b" " * 400, final="https://a.it/x.pdf")})
        try:
            f = C.capturar({"CANDIDATA_ID": "T_DIR", "URL": "https://a.it/x.pdf",
                            "NOME": "n", "PAIS": "IT", "TIPO": "BASE_OFICIAL"})
        finally:
            C.buscar = antigo
        self.assertEqual(f["CAPTURE_RESULT"], "CAPTURED")
        self.assertEqual(f["ROUTE_FAMILY"], "PDF_DIRECT")
        self.assertEqual(f["DISCOVERY_METHOD"], "URL_DIRETA")


class TesteYoutube(unittest.TestCase):
    # ⚠️ ESTE FIXTURE TEM title/published AO NIVEL DO FEED, DE PROPOSITO.
    # E a forma real do feed do YouTube, e foi o que produziu duas medidas
    # erradas ao vivo: o item ficou com a data de CRIACAO DO CANAL (2015) e a
    # cadencia deu «mediana 0d — DIARIA» por causa do outlier de dez anos.
    #: datas RELATIVAS a hoje: o yield passou a depender da RECENCIA, e um
    #: fixture com datas fixas passaria hoje e reprovaria daqui a uns meses
    #: sem nada ter mudado no codigo. Um teste que caduca sozinho e um
    #: alarme falso a prazo.
    _d = [(datetime.now(timezone.utc) - timedelta(days=n)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
          for n in (3, 10, 17, 24)]
    FEED = ('<?xml version="1.0"?><feed>'
            '<title>Canal Oficial</title><published>2015-02-10T00:00:00+00:00</published>'
            '<entry><title>Video A</title><published>%s</published>'
            '<link href="https://www.youtube.com/watch?v=aaa"/></entry>'
            '<entry><title>Video B</title><published>%s</published>'
            '<link href="https://www.youtube.com/watch?v=bbb"/></entry>'
            '<entry><title>Video C</title><published>%s</published>'
            '<link href="https://www.youtube.com/watch?v=ccc"/></entry>'
            '<entry><title>Video D</title><published>%s</published>'
            '<link href="https://www.youtube.com/watch?v=ddd"/></entry></feed>'
            % tuple(_d)).encode()

    def test_le_externalId_e_mede_cadencia(self):
        pagina = b'x{"externalId":"UC01234567890123456789ab"}x' + ENCHE
        antigo, C.buscar = C.buscar, Falso({
            "youtube.com/@canal": resposta(200, pagina),
            "feeds/videos.xml": resposta(200, self.FEED)})
        try:
            f = C.capturar({"CANDIDATA_ID": "T_YT", "URL": "https://www.youtube.com/@canal",
                            "NOME": "n", "PAIS": "IT", "TIPO": "YOUTUBE"})
        finally:
            C.buscar = antigo
        self.assertEqual(f["CAPTURE_RESULT"], "CAPTURED")
        self.assertEqual(f["CHANNEL_ID"], "UC01234567890123456789ab")
        self.assertEqual(f["REAL_EXAMPLE_TITLE"], "Video A")
        self.assertIn("SEMANAL", f["UPDATE_FREQUENCY_OBSERVED"])
        self.assertEqual(f["EXPECTED_YIELD_INITIAL"], "HIGH")

    def test_nao_usa_titulo_nem_data_do_NIVEL_DO_FEED(self):
        """A REGRESSAO MEDIDA AO VIVO. Se voltar a ler as tags globalmente, o
        item herda o nome e a data de nascimento do canal."""
        pagina = b'x{"externalId":"UC01234567890123456789ab"}x' + ENCHE
        antigo, C.buscar = C.buscar, Falso({
            "youtube.com/@c": resposta(200, pagina),
            "feeds/videos.xml": resposta(200, self.FEED)})
        try:
            f = C.capturar({"CANDIDATA_ID": "T_YT3", "URL": "https://www.youtube.com/@c",
                            "NOME": "n", "PAIS": "IT", "TIPO": "YOUTUBE"})
        finally:
            C.buscar = antigo
        self.assertNotEqual(f["REAL_EXAMPLE_TITLE"], "Canal Oficial")
        self.assertNotIn("2015", f["REAL_EXAMPLE_PUBLISHED_AT"])
        self.assertTrue(f["REAL_EXAMPLE_PUBLISHED_AT"].startswith(self._d[0][:10]))
        self.assertEqual(f["ITEMS_OBSERVED_IN_INDEX"], 4, "contou o feed como entrada")
        self.assertIn("SEMANAL", f["UPDATE_FREQUENCY_OBSERVED"])

    def test_sem_externalId_nao_inventa_id_do_vizinho(self):
        # ⚠️ o HTML traz UM id, mas NAO no campo que nomeia o proprio canal.
        # Um regex generico apanharia-o e o feed responderia 200 com videos
        # reais — de outro canal. Aqui tem de falhar.
        pagina = b'<html>UCzzzzzzzzzzzzzzzzzzzzzz canal vinculado</html>' + ENCHE
        espiao = Falso({"youtube.com/@c": resposta(200, pagina)})
        antigo, C.buscar = C.buscar, espiao
        try:
            f = C.capturar({"CANDIDATA_ID": "T_YT2", "URL": "https://www.youtube.com/@c",
                            "NOME": "n", "PAIS": "IT", "TIPO": "YOUTUBE"})
        finally:
            C.buscar = antigo
        self.assertEqual(f["CAPTURE_FAILURE_CLASS"], "NO_ITEM_FOUND")
        self.assertFalse(any("feeds/videos.xml" in p for p in espiao.pedidos),
                         "pediu o feed de um channelId que o canal nao declarou")

    def test_cadencia_precisa_de_tres_datas(self):
        self.assertEqual(C._cadencia(["2026-09-18T10:00:00+00:00"])[1], "UNKNOWN")


class TesteFacebook(unittest.TestCase):
    def test_muro_e_capability_nao_veredito_sobre_a_fonte(self):
        antigo, C.buscar = C.buscar, Falso({"facebook.com": resposta(
            200, b"<html>login</html>" + ENCHE, final="https://facebook.com/login")})
        try:
            f = C.capturar({"CANDIDATA_ID": "T_FB", "URL": "https://www.facebook.com/p",
                            "NOME": "n", "PAIS": "IT", "TIPO": "FACEBOOK"})
        finally:
            C.buscar = antigo
        self.assertEqual(f["CAPTURE_FAILURE_CLASS"], "WALL")
        self.assertEqual(f["LOGIN_REQUIRED"], "SIM")
        # e NUNCA um juizo sobre a utilidade da fonte
        self.assertNotIn(f["CAPTURE_RESULT"], ("REJECT", "REJECTED"))

    def test_titulo_generico_com_HTTP_200_e_muro(self):
        """MEDIDO AO VIVO: 1 das 20 devolveu 200 com 326 KB e titulo «Facebook».
        Aceita-la registaria a porta da plataforma como prova de entrega."""
        pagina = b"<html><head><title>Facebook</title></head><body>x</body></html>" + ENCHE
        antigo, C.buscar = C.buscar, Falso({"facebook.com": resposta(
            200, pagina, final="https://www.facebook.com/pagina")})
        try:
            f = C.capturar({"CANDIDATA_ID": "T_FB2", "URL": "https://www.facebook.com/pagina",
                            "NOME": "n", "PAIS": "IT", "TIPO": "FACEBOOK"})
        finally:
            C.buscar = antigo
        self.assertEqual(f["CAPTURE_FAILURE_CLASS"], "WALL")
        self.assertEqual(f["REAL_EXAMPLE_URL"], "NAO SEI")

    def test_titulo_da_entidade_passa(self):
        pagina = (b"<html><head><title>Consorzio Vino Chianti Classico | Firenze</title>"
                  b"</head><body>x</body></html>") + ENCHE
        antigo, C.buscar = C.buscar, Falso({"facebook.com": resposta(
            200, pagina, final="https://www.facebook.com/chianticlassico")})
        try:
            f = C.capturar({"CANDIDATA_ID": "T_FB3", "URL": "https://www.facebook.com/chianticlassico",
                            "NOME": "n", "PAIS": "IT", "TIPO": "FACEBOOK"})
        finally:
            C.buscar = antigo
        self.assertEqual(f["CAPTURE_RESULT"], "CAPTURED")
        self.assertIn("Chianti", f["REAL_EXAMPLE_TITLE"])


class TesteNuncaLevanta(unittest.TestCase):
    def test_uma_candidata_doente_nao_trava_o_lote(self):
        def explode(url, aceita="*/*"):
            raise RuntimeError("boom")
        antigo, C.buscar = C.buscar, explode
        try:
            f = C.capturar({"CANDIDATA_ID": "T_X", "URL": "https://a.it/",
                            "NOME": "n", "PAIS": "IT", "TIPO": "T"})
        finally:
            C.buscar = antigo
        self.assertEqual(f["CAPTURE_RESULT"], "FAILED")
        self.assertIn("excecao", f["EVIDENCE"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
