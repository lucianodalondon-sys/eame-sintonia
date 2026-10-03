#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D32 (4): um contrato OUTPUT_TYPE=PDF e julgado pela ESTEIRA DE PDF (pdftotext, o executor da
Collection) e a regua DETAIL/v1 aceita o corpo pela camada de texto. Nada vai a rede: o `buscar`
do canario e trocado por um dicionario."""
import shutil
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "curadoria"))
import canario as C       # noqa: E402
import ready_split as RS  # noqa: E402

INDEX = "https://www.protezionedellepiante.it/category/documenti-tecnici-ufficiali/"
PADRAO = r"^https?://(www\.)?protezionedellepiante\.it/wp-content/uploads/\d{4}/\d{2}/dtu-[^/?#]+\.pdf(\?|#|$)"
PDF1 = "https://www.protezionedellepiante.it/wp-content/uploads/2026/05/dtu-a.pdf"
PDF2 = "https://www.protezionedellepiante.it/wp-content/uploads/2026/06/dtu-b.pdf"


def pdf_com_texto(frase: str, linhas: int) -> bytes:
    """Um PDF minimo e valido, com `linhas` linhas de texto em Helvetica."""
    corpo = "BT /F1 9 Tf 20 800 Td 11 TL " + " ".join("(%s) '" % frase for _ in range(linhas)) + " ET"
    objs = ["<< /Type /Catalog /Pages 2 0 R >>",
            "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R "
            "/Resources << /Font << /F1 5 0 R >> >> >>",
            "<< /Length %d >>\nstream\n%s\nendstream" % (len(corpo), corpo),
            "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out, pos = b"%PDF-1.4\n", []
    for i, o in enumerate(objs, 1):
        pos.append(len(out))
        out += ("%d 0 obj\n%s\nendobj\n" % (i, o)).encode("latin-1")
    xref = len(out)
    out += ("xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)).encode()
    out += b"".join(b"%010d 00000 n \n" % p for p in pos)
    out += ("trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)).encode()
    return out


def contrato(output_type="PDF"):
    return {"SOURCE_ID": "IT-T3-014", "OUTPUT_TYPE": output_type,
            "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": INDEX, "LINK_PATTERN": PADRAO},
            # D47: o canario PDF pergunta a identidade ao motor do coletor, que exige STRATEGY. O bloco
            # abaixo e o que as 574 de 574 fontes do livro do Curator declaram (medido 25/09).
            "IDENTITY": {"STRATEGY": "CONTENT_CAPTURE",
                         "CAPTURES": {"doc": {"FROM": "URL", "PATTERN": "^https?://[^/]+/?(.*?)/?$"}},
                         "DOCUMENT_ID": "IT-T3-014:{doc.1}", "FACT_TIME": "UNKNOWN"}}


PAGINA = ('<a href="/wp-content/uploads/2026/05/dtu-a.pdf">a</a>'
          '<a href="https://www.protezionedellepiante.it/wp-content/uploads/2026/06/dtu-b.pdf">b</a>'
          '<a href="/chi-siamo/">menu</a>').encode()


@unittest.skipUnless(shutil.which("pdftotext"), "sem pdftotext nesta maquina")
class OCanarioDePdf(unittest.TestCase):

    def correr(self, item_bytes, output_type="PDF"):
        rede = {INDEX: (200, PAGINA, None), PDF1: (200, item_bytes, None), PDF2: (200, item_bytes, None)}
        velho = C.buscar
        C.buscar = lambda u: rede.get(u, (404, b"", "HTTP 404"))
        try:
            return C.canario_html(contrato(output_type))
        finally:
            C.buscar = velho

    def regua(self, r):
        return RS.passos_da_promocao({"OBSERVED_AT": datetime.now(timezone.utc).isoformat(), "EVIDENCE_REF": "x"},
                                     {"DADOS": r}, contrato())

    def test_pdf_com_texto_passa_e_a_regua_da_detail(self):
        r = self.correr(pdf_com_texto("Documento tecnico ufficiale difesa integrata vite peronospora", 40))
        self.assertTrue(r["PASS"], r.get("PORQUE"))
        self.assertEqual(r["DETAIL_GATE"], C.PDF_GATE_VERSAO)
        it = r["ITEM_ABERTO"]
        self.assertEqual((it["DOC_KIND"], it["TEXT_LAYER"]), ("PDF", "TEXT_LAYER_PRESENT"))
        self.assertGreaterEqual(it["TEXT_CHARACTERS"], 800)
        self.assertEqual(r["DETAIL_ENUMERATED"], 2)
        self.assertEqual(self.regua(r)["REGUA"], RS.REGUA_CURRENT)

    def test_pdf_com_pouco_texto_reprova(self):
        r = self.correr(pdf_com_texto("Pagina di copertina", 2))
        self.assertFalse(r["PASS"])
        self.assertEqual(r["CLASSE"], "SOURCE_FAILURE")
        self.assertIn("caracteres de texto", r["PORQUE"])

    def test_bytes_que_nao_sao_pdf_reprovam(self):
        r = self.correr(b"<html><body>Pagina di errore</body></html>")
        self.assertFalse(r["PASS"])
        self.assertIn("nao sao PDF", r["PORQUE"])

    def test_pdf_sem_contrato_pdf_continua_a_reprovar_como_html(self):
        r = self.correr(pdf_com_texto("Documento tecnico ufficiale difesa integrata", 40), output_type="HTML")
        self.assertFalse(r["PASS"])
        self.assertIn("BYTE_VALIDATION_FAILED", r["PORQUE"])


class AReguaDoCorpoPdf(unittest.TestCase):
    """O corpo PDF so conta com camada de texto E >= 800 caracteres E o gate passado."""

    def passos(self, **item):
        dados = {"DETAIL_GATE_PASSED": True, "DETAIL_ENUMERATED": 5, "ITEM_ABERTO": dict(item)}
        return RS.passos_da_promocao({"OBSERVED_AT": datetime.now(timezone.utc).isoformat(), "EVIDENCE_REF": "x"},
                                     {"DADOS": dados}, contrato())["PASSOS"]

    def test_camada_de_texto_com_800(self):
        self.assertTrue(self.passos(DOC_KIND="PDF", TEXT_LAYER="TEXT_LAYER_PRESENT", TEXT_CHARACTERS=800)["BODY_UTIL"])

    def test_799_nao_chega(self):
        self.assertFalse(self.passos(DOC_KIND="PDF", TEXT_LAYER="TEXT_LAYER_PRESENT", TEXT_CHARACTERS=799)["BODY_UTIL"])

    def test_imagem_sem_texto_nao_conta(self):
        self.assertFalse(self.passos(DOC_KIND="PDF", TEXT_LAYER="TEXT_LAYER_ABSENT", TEXT_CHARACTERS=5000)["BODY_UTIL"])

    def test_texto_sem_ser_pdf_nao_conta(self):
        self.assertFalse(self.passos(TEXT_LAYER="TEXT_LAYER_PRESENT", TEXT_CHARACTERS=5000)["BODY_UTIL"])


if __name__ == "__main__":
    unittest.main()
