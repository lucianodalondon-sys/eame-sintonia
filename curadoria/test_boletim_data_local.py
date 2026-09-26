#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D61/D62/D69 — data e lugar do boletim, do lado do Curator (porta, validador, canario). Nada vai a rede.

- A porta aceita um PDF sem «.pdf» no endereco SO com o porque escrito (PDF_SEM_EXTENSAO), que fica na
  proveniencia; sem ele, recusa como antes.
- O validador aceita FACT_TIME_BASIS sem molde: e o contrato a dizer que o boletim NAO traz o periodo.
- O canario HTML de um boletim que declara BASES pergunta ao motor e mostra os campos; um contrato
  sem BASE fica exactamente como estava.
- D69: o periodo de validade sem ligacao ao facto no texto fica em BULLETIN_PERIOD, e o FACT_TIME NAO SEI."""
from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import canario as CAN               # noqa: E402
import reparar_contrato as RC       # noqa: E402
import validar_contratos as VC      # noqa: E402
from test_reparar_contrato import _contrato  # noqa: E402

INDEX = "https://www.exemplo.it/avvisi"
URL_DOC = {"FROM": "URL", "PATTERN": "^https?://[^/]+/?(.*?)/?$"}


def proposta(**kw):
    p = {"DESFECHO": "PADRAO_NOVO", "INDEX_URL": INDEX, "LINK_PATTERN": r"^https?://www\.exemplo\.it/allegato\.aspx\?pk=\d+$",
         "OUTPUT_TYPE": "PDF", "PDF_SEM_EXTENSAO": "allegato.aspx?pk=N sem extensao; medido %PDF- nos bytes",
         "COMO": "bancada (teste)", "PORQUE": "avisos PDF"}
    p.update(kw)
    return p


class APortaEOPdfSemExtensao(unittest.TestCase):

    def test_sem_o_porque_recusa_como_antes(self):
        p = proposta(); p.pop("PDF_SEM_EXTENSAO")
        with self.assertRaises(RC.ReparoInvalido):
            RC.aplicar(_contrato(), p)

    def test_porque_vazio_recusa(self):
        with self.assertRaises(RC.ReparoInvalido):
            RC.aplicar(_contrato(), proposta(PDF_SEM_EXTENSAO="   "))

    def test_com_o_porque_aceita_e_guarda_na_proveniencia(self):
        novo = RC.aplicar(_contrato(), proposta())
        self.assertEqual("PDF", novo["OUTPUT_TYPE"])
        self.assertIn("sem extensao", novo["REPARO_DE_CONTRATO"]["PDF_SEM_EXTENSAO"])

    def test_padrao_com_pdf_nao_precisa_do_porque(self):
        p = proposta(LINK_PATTERN=r"^https?://www\.exemplo\.it/b/\d+\.pdf$"); p.pop("PDF_SEM_EXTENSAO")
        self.assertNotIn("PDF_SEM_EXTENSAO", RC.aplicar(_contrato(), p)["REPARO_DE_CONTRATO"])


class OValidadorEABaseSemMolde(unittest.TestCase):

    def _ident(self, **kw):
        c = _contrato()
        c["IDENTITY"] = dict({"STRATEGY": "CONTENT_CAPTURE", "CAPTURES": {"doc": URL_DOC},
                              "DOCUMENT_ID": c["SOURCE_ID"] + ":URL:{doc.1}"}, **kw)
        return VC.validar([c])[1]

    def test_fact_time_basis_sem_molde_e_declaracao(self):
        self.assertEqual([], self._ident(FACT_TIME_BASIS="NAO_DECLARADO · o aviso nao declara periodo"))

    def test_sem_fact_time_nem_base_continua_a_reprovar(self):
        self.assertTrue(self._ident())

    def test_base_vazia_nao_conta(self):
        self.assertTrue(self._ident(FACT_TIME_BASIS="  "))


PAGINA_EDICAO = ('<html><body><nav>' + ' '.join('<a href="/m%d">Menu %d</a>' % (i, i) for i in range(6)) + '</nav><main>'
                 '<h1>BOLLETTINO agrometeorologico e fitosanitario</h1><p>Pubblicato il bollettino Settimana 39 '
                 '(22/09/2026 – 29/09/2026)</p><p>' + 'Situazione fitosanitaria di vite, olivo e agrumi in tutta la regione. ' * 40 +
                 '</p></main></body></html>').encode()
LISTA = b'<a href="https://www.exemplo.it/bollettino-settimana-39-2026/">39</a>'
ALVO = "https://www.exemplo.it/bollettino-settimana-39-2026/"


@unittest.skipUnless(shutil.which("node"), "sem node: o canario pergunta ao motor do coletor")
class OCanarioHtmlDeUmBoletim(unittest.TestCase):

    def _contrato(self, com_base=True):
        c = RC.aplicar(_contrato(), {"DESFECHO": "PADRAO_NOVO", "INDEX_URL": INDEX,
                                     "LINK_PATTERN": r"^https?://www\.exemplo\.it/bollettino-settimana-\d+-\d{4}/$",
                                     "COMO": "t", "PORQUE": "t"})
        if com_base:
            sid = c["SOURCE_ID"]
            c["IDENTITY"] = {
                "STRATEGY": "CONTENT_CAPTURE",
                "CAPTURES": {"doc": URL_DOC,
                             "pa": {"FROM": "PAGE_TEXT", "REQUIRED": False, "DEFAULTS": ["x"] * 6,
                                    "PATTERN": r"Settimana\s+\d+\s*\((\d{1,2})/(\d{1,2})/(\d{4})\s*[–-]\s*(\d{1,2})/(\d{1,2})/(\d{4})\)"}},
                "DOCUMENT_ID": sid + ":URL:{doc.1}",
                "BULLETIN_PERIOD": "{pa.3}-{pa.2:MES2}-{pa.1:DIA2}/{pa.6}-{pa.5:MES2}-{pa.4:DIA2}",
                "BULLETIN_PERIOD_BASIS": "VALIDADE_DECLARADA_NA_PAGINA_DA_EDICAO · «Settimana NN (…)»",
                "FACT_TIME_BASIS": "NAO_LIGADO · a pagina da a validade, sem a ligar ao facto (D69)",
                "PUBLISHED_AT_BASIS": "NAO_DECLARADA_NA_PAGINA · so «Ultima modifica»",
            }
        return c

    def _correr(self, c):
        def buscar(u):
            return {INDEX: (200, LISTA, ""), ALVO: (200, PAGINA_EDICAO, "")}.get(u, (404, b"", "HTTP 404"))
        antes, CAN.buscar = CAN.buscar, buscar
        try:
            return CAN.canario_html(c)
        finally:
            CAN.buscar = antes

    def test_d69_validade_fica_como_evidencia_e_fact_time_nao_sei(self):
        r = self._correr(self._contrato())
        self.assertTrue(r["PASS"], r.get("PORQUE"))
        t = r["TEMPOS"]
        self.assertEqual("2026-09-22/2026-09-29", t["BULLETIN_PERIOD"])
        self.assertEqual("NAO SEI", t["FACT_TIME"])
        self.assertIn("BULLETIN_PERIOD", t["FACT_TIME_BASIS"])
        self.assertEqual("NAO SEI", t["PUBLISHED_AT"])
        self.assertIn("Ultima modifica", t["PUBLISHED_AT_BASIS"])
        self.assertNotEqual(t["COLLECTION_TIME"], t["PUBLISHED_AT"])

    def test_contrato_sem_base_fica_como_antes(self):
        r = self._correr(self._contrato(com_base=False))
        self.assertTrue(r["PASS"], r.get("PORQUE"))
        self.assertNotIn("TEMPOS", r, "o canario HTML de um contrato sem BASE nao muda")


LISTA_MOLISE = ('<ul><li><a href="/att/1/E/pdf?mode=download">Bollettino vigilanza del 20-09-2026 &nbsp;(331.09 KB)</a></li>'
                '<li><a href="/att/2/E/pdf?mode=download">Comunicato fitosanitario n&#176;6/2026 (647.22 KB)</a></li></ul>').encode("latin-1")
INDEX_MOLISE = "https://www.regione.molise.it/pagina/18077"


class DA13OTextoDoLinkDoIndice(unittest.TestCase):

    def test_o_canario_le_o_texto_de_cada_ligacao(self):
        t = CAN.textos_das_ligacoes(LISTA_MOLISE, INDEX_MOLISE)
        self.assertEqual("Bollettino vigilanza del 20-09-2026 (331.09 KB)", t["https://www.regione.molise.it/att/1/E/pdf?mode=download"])
        self.assertEqual("Comunicato fitosanitario n°6/2026 (647.22 KB)", t["https://www.regione.molise.it/att/2/E/pdf?mode=download"])

    @unittest.skipUnless(shutil.which("node"), "sem node nesta maquina")
    def test_paridade_com_o_motor_do_coletor(self):
        import json
        import subprocess
        js = ("import {textosDasLigacoes} from './regras/motor_de_rota.mjs';"
              "const [html, aq] = JSON.parse(process.argv[1]);"
              "console.log(JSON.stringify([...textosDasLigacoes(html, aq)]));")
        r = subprocess.run(["node", "--input-type=module", "-e", js,
                            json.dumps([LISTA_MOLISE.decode("latin-1"), {"INDEX_URL": INDEX_MOLISE}])],
                           cwd=AQUI.parent, capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(0, r.returncode, r.stderr[-1500:])
        do_motor = dict(json.loads(r.stdout.strip().splitlines()[-1]))
        self.assertEqual(do_motor, CAN.textos_das_ligacoes(LISTA_MOLISE, INDEX_MOLISE))

    @unittest.skipUnless(shutil.which("node") and shutil.which("pdftotext"), "sem node/pdftotext nesta maquina")
    def test_o_canario_pdf_passa_o_link_ao_motor_base_indice(self):
        from test_canario_pdf import pdf_com_texto
        c = RC.aplicar(_contrato(), {
            "DESFECHO": "PADRAO_NOVO", "INDEX_URL": INDEX_MOLISE, "OUTPUT_TYPE": "PDF",
            "LINK_PATTERN": r"^https?://www\.regione\.molise\.it/att/1/E/pdf\?mode=download$",
            "PDF_SEM_EXTENSAO": "ServeAttachment sem extensao", "COMO": "t", "PORQUE": "t",
            "IDENTITY": {
                "STRATEGY": "CONTENT_CAPTURE",
                "CAPTURES": {"doc": URL_DOC,
                             "lk": {"FROM": "LINK_TEXT", "PATTERN": r"\bdel\s+(\d{1,2})-(\d{1,2})-(\d{4})\b",
                                    "REQUIRED": False, "DEFAULTS": ["x", "x", "x"]}},
                "DOCUMENT_ID": _contrato()["SOURCE_ID"] + ":URL:{doc.1}",
                "PUBLISHED_AT": "{lk.3}-{lk.2:MES2}-{lk.1:DIA2}",
                "PUBLISHED_AT_BASIS": "INDICE · o texto do link da lista",
                "FACT_TIME_BASIS": "NAO_DECLARADO · teste"}})
        pdf = pdf_com_texto("Previsione meteorologica senza data di emissione nel testo", 40)
        rede = {INDEX_MOLISE: (200, LISTA_MOLISE, ""), "https://www.regione.molise.it/att/1/E/pdf?mode=download": (200, pdf, "")}
        antes, CAN.buscar = CAN.buscar, (lambda u: rede.get(u, (404, b"", "HTTP 404")))
        try:
            r = CAN.canario_html(c)
        finally:
            CAN.buscar = antes
        self.assertTrue(r["PASS"], r.get("PORQUE"))
        self.assertEqual("2026-09-20", r["TEMPOS"]["PUBLISHED_AT"])
        self.assertTrue(r["TEMPOS"]["PUBLISHED_AT_BASIS"].startswith("INDICE"))
        self.assertIn("del 20-09-2026", r["TEXTO_DA_LIGACAO"])


if __name__ == "__main__":
    unittest.main()
