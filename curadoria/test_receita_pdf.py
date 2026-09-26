#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D42 (1): a receita pode ligar a ROTA PDF que ja existe, com o tipo de saida EXPLICITO.

A porta e `reparar_contrato.aplicar` (a da R1): so muda ACQUISITION — e agora tambem OUTPUT_TYPE,
mas so quando a proposta o PEDE, so para HTML/PDF, e so com um padrao que aponte para .pdf. O tipo
anterior fica na proveniencia. Depois, o canario PDF (esteira de PDF da Collection) e a regua
DETAIL/v1 (corpo pela camada de texto) decidem — nada vai a rede: `buscar` e um dicionario."""
from __future__ import annotations

import shutil
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import canario as CAN            # noqa: E402
import ready_split as RS         # noqa: E402
import reparar_contrato as RC    # noqa: E402
from test_canario_pdf import pdf_com_texto   # noqa: E402
from test_reparar_contrato import _contrato  # noqa: E402

INDEX = "https://www.exemplo.it/bollettini/"
PADRAO_PDF = r"^https?://(www\.)?exemplo\.it/pdf/bollettino-\d+\.pdf$"


def proposta(**kw):
    p = {"DESFECHO": "PADRAO_NOVO", "INDEX_URL": INDEX, "LINK_PATTERN": PADRAO_PDF,
         "OUTPUT_TYPE": "PDF", "COMO": "bancada (teste)", "PORQUE": "2 boletins em PDF"}
    p.update(kw)
    return p


class APortaAceitaPdfExplicito(unittest.TestCase):

    def test_pdf_explicito_muda_o_tipo_e_guarda_o_anterior(self):
        base = _contrato()
        self.assertEqual("HTML", base["OUTPUT_TYPE"])
        novo = RC.aplicar(base, proposta())
        self.assertEqual("PDF", novo["OUTPUT_TYPE"])
        self.assertEqual(PADRAO_PDF, novo["ACQUISITION"]["LINK_PATTERN"])
        for bloco in ("REPARO_DE_CONTRATO", "ROUTE_PROVENANCE"):
            self.assertEqual(("PDF", "HTML"), (novo[bloco]["OUTPUT_TYPE"], novo[bloco]["OUTPUT_TYPE_ANTERIOR"]), bloco)
        self.assertNotEqual(base["SOURCE_CONTRACT_HASH"], novo["SOURCE_CONTRACT_HASH"])

    def test_sem_tipo_na_proposta_o_tipo_nao_muda(self):
        p = proposta(LINK_PATTERN=r"^https?://(www\.)?exemplo\.it/news/\d+/[a-z-]+$")
        p.pop("OUTPUT_TYPE")
        novo = RC.aplicar(_contrato(), p)
        self.assertEqual("HTML", novo["OUTPUT_TYPE"])
        self.assertNotIn("OUTPUT_TYPE", novo["REPARO_DE_CONTRATO"])

    def test_o_tipo_nunca_se_adivinha_pelo_padrao(self):
        p = proposta()
        p.pop("OUTPUT_TYPE")        # padrao de .pdf, mas ninguem pediu PDF
        self.assertEqual("HTML", RC.aplicar(_contrato(), p)["OUTPUT_TYPE"])

    def test_tipo_fora_do_vocabulario_recusa(self):
        with self.assertRaises(RC.ReparoInvalido):
            RC.aplicar(_contrato(), proposta(OUTPUT_TYPE="XLSX"))
        # VIDEO_METADATA passa no validador da casa, mas nao e tipo de uma receita de pagina
        with self.assertRaises(RC.ReparoInvalido):
            RC.aplicar(_contrato(), proposta(OUTPUT_TYPE="VIDEO_METADATA"))

    def test_pdf_com_padrao_que_nao_e_pdf_recusa(self):
        with self.assertRaises(RC.ReparoInvalido):
            RC.aplicar(_contrato(), proposta(LINK_PATTERN=r"^https?://(www\.)?exemplo\.it/news/\d+$"))

    def test_a_porta_continua_a_recusar_outros_campos(self):
        # a porta so muda os campos dela (+ OUTPUT_TYPE, porque foi pedido)
        base = _contrato()
        novo = RC.aplicar(base, proposta())
        mexidos = {k for k in set(base) | set(novo) if base.get(k) != novo.get(k)}
        self.assertEqual(set(), mexidos - RC.CAMPOS_QUE_O_REPARO_MUDA - {"OUTPUT_TYPE"})


@unittest.skipUnless(shutil.which("pdftotext"), "sem pdftotext nesta maquina")
class DaPortaAoCanarioPdf(unittest.TestCase):
    """A receita PDF aplicada -> canario pela esteira de PDF -> regua DETAIL/v1 pelo corpo PDF."""

    def test_caminho_inteiro(self):
        novo = RC.aplicar(_contrato(), proposta())
        pagina = ('<a href="../pdf/bollettino-37.pdf">37</a><a href="/pdf/bollettino-38.pdf">38</a>'
                  '<a href="/chi-siamo/">menu</a>').encode()
        pdf = pdf_com_texto("Bollettino fitosanitario difesa integrata vite olivo peronospora", 40)
        rede = {INDEX: (200, pagina, None),
                "https://www.exemplo.it/pdf/bollettino-37.pdf": (200, pdf, None),
                "https://www.exemplo.it/pdf/bollettino-38.pdf": (200, pdf, None)}
        velho = CAN.buscar
        CAN.buscar = lambda u: rede.get(u, (404, b"", "HTTP 404"))
        try:
            r = CAN.canario_html(novo)
        finally:
            CAN.buscar = velho
        self.assertTrue(r["PASS"], r.get("PORQUE"))
        self.assertEqual(2, r["DETAIL_ENUMERATED"])
        regua = RS.passos_da_promocao({"OBSERVED_AT": datetime.now(timezone.utc).isoformat(),
                                       "EVIDENCE_REF": "x"}, {"DADOS": r}, novo)
        self.assertEqual(RS.REGUA_CURRENT, regua["REGUA"], regua)


if __name__ == "__main__":
    unittest.main()
