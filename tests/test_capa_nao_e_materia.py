# -*- coding: utf-8 -*-
"""CAPA != MATERIA · MARKUP != TEXTO — as duas provas da AQUISICAO-DETALHE-V1.

Medido no canário de 21/09/2026 (10 fontes, 105 observações):

  · a Big Collection tinha guardado, em 9 das 104 fontes de índice, a PRÓPRIA
    listagem como se fosse o documento. O contrato dizia «itens de detalhe»;
    o que chegou foi a capa, e saiu HEALTHY;
  · 2 de 3 DOCUMENT_CHANGED_IN_PLACE eram o mesmo texto visível com bytes
    diferentes — versão nova no armazém por ruído de markup.

Estas provas exigem que as duas coisas tenham nome, e cada uma tem o caso que
a faz REPROVAR: uma listagem sintética tem de ser CAPA_PROVAVEL; um contrato
de detalhe com capa tem de ser barrado; um artigo com markup trocado tem de
sair MARKUP_ONLY — e com o texto trocado, TEXT_CHANGED.

    TESTE QUE NUNCA VIU VERMELHO NAO E TESTE.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RETRATO = os.path.join(RAIZ, "coleta", "retrato_html.mjs").replace("\\", "/")
COLETOR = os.path.join(RAIZ, "coleta", "italy_pilot_collect.mjs").replace("\\", "/")
FONTE_ESTATICA_HTML = "IT-T2-004"   # STATIC_ENDPOINT, OUTPUT HTML, identidade pela janela «dal … al …»


def _node(driver):
    r = subprocess.run(["node", "--input-type=module", "-e", driver],
                       cwd=RAIZ, capture_output=True, text=True, timeout=300,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def listagem_sintetica(n=60):
    itens = "".join('<li><a href="/news/item-%d-titolo-breve">Titolo %d</a></li>' % (i, i) for i in range(n))
    return "<html><head><title>News</title></head><body><nav><ul>%s</ul></nav></body></html>" % itens


def artigo_sintetico(janela="dal 01/09/2026 al 07/09/2026", sal="", corpo=None):
    corpo = corpo or ("La mosca dell'olivo accelera con il calo termico. " * 40)
    return ("<html><head><title>Bollettino</title>%s</head><body><h1>Bollettino %s</h1>"
            "<p>%s</p><p>%s</p><p>%s</p><a href=\"/a\">a</a><a href=\"/b\">b</a></body></html>"
            % (sal, janela, corpo, corpo, corpo))


class ORetratoDistingueCapaDeMateria(unittest.TestCase):

    def retrato(self, html):
        return _node("""
import { pathToFileURL } from "node:url";
const { retratoDoHtml } = await import(pathToFileURL(%s).href);
console.log(JSON.stringify(retratoDoHtml(Buffer.from(%s, "utf8"))));
""" % (json.dumps(RETRATO), json.dumps(html)))

    def test_1_uma_listagem_e_CAPA_PROVAVEL(self):
        r = self.retrato(listagem_sintetica())
        self.assertEqual("NAVIGATION", r["HTML_KIND"])
        self.assertEqual("CAPA_PROVAVEL", r["CAPA_OU_MATERIA"])
        self.assertEqual(60, r["LINKS"])

    def test_2_um_artigo_e_MATERIA_PROVAVEL(self):
        r = self.retrato(artigo_sintetico())
        self.assertEqual("CONTENT", r["HTML_KIND"])
        self.assertEqual("MATERIA_PROVAVEL", r["CAPA_OU_MATERIA"])

    def test_3_pagina_vazia_nao_e_nenhuma_das_duas(self):
        r = self.retrato("<html><body><script>var x=1;</script></body></html>")
        self.assertEqual("EMPTY", r["HTML_KIND"])
        self.assertEqual("NAO_SEI", r["CAPA_OU_MATERIA"])

    def test_4_o_texto_tem_impressao_propria_e_o_markup_nao_a_move(self):
        a = self.retrato(artigo_sintetico())
        b = self.retrato(artigo_sintetico(sal='<meta name="nonce" content="abc123"><!-- 2026-09-21T01:12:38Z -->'))
        c = self.retrato(artigo_sintetico(corpo="Un testo diverso, con altre parole dentro. " * 40))
        self.assertEqual(a["TEXT_SHA256"], b["TEXT_SHA256"], "markup trocado nao pode mudar a impressao do texto")
        self.assertNotEqual(a["TEXT_SHA256"], c["TEXT_SHA256"], "texto trocado tem de mudar a impressao")


class OGateBarraACapaSoOndeOContratoDeclaraDetalhe(unittest.TestCase):

    def gate(self, contrato, html):
        return _node("""
import { pathToFileURL } from "node:url";
const { retratoDoHtml, gateCapaNaoEMateria } = await import(pathToFileURL(%s).href);
console.log(JSON.stringify({ gate: gateCapaNaoEMateria(%s, retratoDoHtml(Buffer.from(%s, "utf8"))) }));
""" % (json.dumps(RETRATO), json.dumps(contrato), json.dumps(html)))["gate"]

    DETALHE = {"OUTPUT_TYPE": "HTML", "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL"}}

    def test_5_contrato_de_detalhe_com_capa_REPROVA(self):
        g = self.gate(self.DETALHE, listagem_sintetica())
        self.assertIsNotNone(g)
        self.assertTrue(g.startswith("CAPA_NAO_E_MATERIA"), g)

    def test_6_contrato_de_detalhe_com_materia_passa(self):
        self.assertIsNone(self.gate(self.DETALHE, artigo_sintetico()))

    def test_7_rota_fixa_nao_e_julgada_pelo_gate(self):
        fixo = {"OUTPUT_TYPE": "HTML", "ACQUISITION": {"STRATEGY": "STATIC_ENDPOINT", "URL": "x"}}
        self.assertIsNone(self.gate(fixo, listagem_sintetica()), "STATIC_ENDPOINT nao declara itens de detalhe")

    def test_8_pdf_nao_e_julgado_pelo_gate(self):
        pdf = {"OUTPUT_TYPE": "PDF", "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL"}}
        self.assertIsNone(self.gate(pdf, listagem_sintetica()))


class OColetorRegistaTextoEMudancaDeMarkup(unittest.TestCase):
    """Três corridas com bytes injectados, numa raiz descartável: o livro real não é tocado."""

    def setUp(self):
        self.ops = tempfile.mkdtemp(prefix=".prova-capa-", dir=os.path.join(RAIZ, "data"))
        self.addCleanup(shutil.rmtree, self.ops, True)

    def correr(self, run_id, html):
        driver = """
import { pathToFileURL } from "node:url";
const { executarRodada } = await import(pathToFileURL(%s).href);
const r = await executarRodada({ runId: %s, apenas: [%s], pularParse: true,
  forcarBuf: () => Buffer.from(%s, "latin1"), nota: "prova capa != materia" });
console.log(JSON.stringify(r.resumo.contadores));
""" % (json.dumps(COLETOR), json.dumps(run_id), json.dumps(FONTE_ESTATICA_HTML), json.dumps(html))
        r = subprocess.run(["node", "--input-type=module", "-e", driver], cwd=RAIZ,
                           capture_output=True, text=True, timeout=300,
                           env={**os.environ, "ITALY_OPS_ROOT": self.ops.replace("\\", "/")})
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        return json.loads(r.stdout.strip().splitlines()[-1])

    def livro(self):
        p = os.path.join(self.ops, "data", "collection-ledger", "italy", "observations.ndjson")
        with io.open(p, encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]

    def test_9_markup_trocado_e_MARKUP_ONLY_e_texto_trocado_e_TEXT_CHANGED(self):
        self.correr("CAPA-PROVA-0001", artigo_sintetico())
        c2 = self.correr("CAPA-PROVA-0002", artigo_sintetico(sal='<meta name="nonce" content="zzz"><!-- outro -->'))
        c3 = self.correr("CAPA-PROVA-0003", artigo_sintetico(corpo="Testo cambiato davvero, con altre frasi. " * 40))
        o1, o2, o3 = self.livro()
        self.assertEqual("BASELINE_DOCUMENT", o1["OBSERVATION_RESULT"])
        self.assertRegex(o1["TEXT_SHA256"], r"^[0-9a-f]{64}$")
        self.assertIsNone(o1["CONTENT_CHANGE"], "sem versao anterior nao ha mudanca a classificar")
        self.assertEqual("DOCUMENT_CHANGED_IN_PLACE", o2["OBSERVATION_RESULT"])
        self.assertEqual("MARKUP_ONLY", o2["CONTENT_CHANGE"])
        self.assertEqual(o1["TEXT_SHA256"], o2["TEXT_SHA256"])
        self.assertNotEqual(o1["RAW_SHA256"], o2["RAW_SHA256"], "os bytes mudaram mesmo — e o RAW novo fica")
        self.assertEqual(1, c2["MARKUP_ONLY_REOBSERVATIONS"])
        self.assertEqual("DOCUMENT_CHANGED_IN_PLACE", o3["OBSERVATION_RESULT"])
        self.assertEqual("TEXT_CHANGED", o3["CONTENT_CHANGE"])
        self.assertEqual(0, c3["MARKUP_ONLY_REOBSERVATIONS"])

    def test_10_o_retrato_e_leitura_e_a_rota_fixa_continua_HEALTHY_com_capa(self):
        """O gate NAO se aplica a STATIC_ENDPOINT: uma capa numa rota fixa e a rota fixa."""
        janela = "<html><body><p>dal 01/09/2026 al 07/09/2026</p>%s</body></html>" % listagem_sintetica()[12:-14]
        c = self.correr("CAPA-PROVA-0004", janela)
        o = self.livro()[-1]
        self.assertEqual("CAPA_PROVAVEL", o["CAPA_OU_MATERIA"])
        self.assertEqual("HEALTHY", o["HEALTH_STATE"])
        self.assertEqual(0, c["LISTING_AS_CONTENT"])


if __name__ == "__main__":
    unittest.main()
