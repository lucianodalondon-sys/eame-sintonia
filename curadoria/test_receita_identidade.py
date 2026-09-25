#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D47 (T2-BOLETINS): a receita pode trazer uma IDENTITY explicita — conferida pelo MOTOR DO COLETOR — e
o canario PDF pergunta a identidade (e os tempos) a esse mesmo motor.

Caso medido: os boletins agrometeo da ARPAE chamam-se `NN_boll_agro_AAAAMMDD.pdf`. O molde antigo
(`IT-T2-051:URL:{caminho}`) nao dava tempo nenhum; com a captura do nome, a PUBLICACAO sai do nome,
o FACTO fica UNKNOWN (esta dentro do PDF, e o coletor nao injecta PDF_TEXT) e a COLETA e do coletor.
Nada vai a rede."""
from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import canario as CAN            # noqa: E402
import reparar_contrato as RC    # noqa: E402
from test_reparar_contrato import _contrato  # noqa: E402

INDEX = "https://www.exemplo.it/bollettini-2026"
PADRAO = r"^https?://(www\.)?exemplo\.it/bollettini-2026/\d{2}_boll_agro_\d{8}(-\d+)?\.pdf$"
IDENT = {
    "STRATEGY": "CONTENT_CAPTURE",
    "CAPTURES": {"b": {"FROM": "URL", "PATTERN": r"/(\d{2})_boll_agro_(\d{4})(\d{2})(\d{2})(?:-\d+)?\.pdf$"}},
    "DOCUMENT_ID": "IT-T7-900:BOLETIM:AGROMETEO:{b.2}-{b.1}",
    "SOURCE_DATE_ISO": "{b.2}-{b.3}-{b.4}",
    "FACT_TIME": "UNKNOWN — o periodo do boletim esta no texto do PDF",
}


def proposta(**kw):
    p = {"DESFECHO": "PADRAO_NOVO", "INDEX_URL": INDEX, "LINK_PATTERN": PADRAO, "OUTPUT_TYPE": "PDF",
         "STRIP_SUFFIX": "/view", "IDENTITY": IDENT, "COMO": "bancada (teste)", "PORQUE": "boletins datados"}
    p.update(kw)
    return p


@unittest.skipUnless(shutil.which("node"), "sem node nesta maquina: a porta recusa (falha fechada)")
class APortaAceitaIdentidadeConferidaPeloMotor(unittest.TestCase):

    def test_identidade_pedida_entra_e_a_anterior_fica_na_proveniencia(self):
        base = _contrato()
        novo = RC.aplicar(base, proposta())
        self.assertEqual(IDENT, novo["IDENTITY"])
        self.assertEqual(base["IDENTITY"], novo["REPARO_DE_CONTRATO"]["IDENTITY_ANTERIOR"])

    def test_sem_identidade_pedida_a_identidade_nao_muda(self):
        base = _contrato()
        p = proposta(); p.pop("IDENTITY")
        novo = RC.aplicar(base, p)
        self.assertEqual(base["IDENTITY"], novo["IDENTITY"])
        self.assertNotIn("IDENTITY_ANTERIOR", novo["REPARO_DE_CONTRATO"])

    def test_o_motor_recusa_identidade_malformada(self):
        mas = [
            dict(IDENT, STRATEGY="ADIVINHAR"),                                    # fora do vocabulario
            dict(IDENT, DOCUMENT_ID="IT-T7-900:{z.1}"),                           # captura que nao existe
            dict(IDENT, CAPTURES={"b": {"FROM": "PDF_TEXTO", "PATTERN": "x"}}),   # leitor fora do vocabulario
            "IT-T7-900:URL",                                                      # nem e objecto
        ]
        for m in mas:
            with self.assertRaises(RC.ReparoInvalido, msg=repr(m)[:80]):
                RC.aplicar(_contrato(), proposta(IDENTITY=m))

    def test_a_porta_so_deixa_mudar_a_identidade_quando_pedida(self):
        base = _contrato()
        novo = RC.aplicar(base, proposta())
        mexidos = {k for k in set(base) | set(novo) if base.get(k) != novo.get(k)}
        self.assertEqual(set(), mexidos - RC.CAMPOS_QUE_O_REPARO_MUDA - {"OUTPUT_TYPE", "IDENTITY"})


@unittest.skipUnless(shutil.which("node") and shutil.which("pdftotext"), "sem node/pdftotext nesta maquina")
class OCanarioPdfPerguntaOsTemposAoMotor(unittest.TestCase):

    def _correr(self, contrato, pdf):
        pagina = b'<a href="bollettini-2026/38_boll_agro_20260921.pdf/view">38</a>'

        def buscar(u):
            if u == INDEX:
                return 200, pagina, ""
            if u.endswith("38_boll_agro_20260921.pdf"):
                return 200, pdf, ""
            return 404, b"", "HTTP 404"
        antes, CAN.buscar = CAN.buscar, buscar
        try:
            return CAN.canario_html(contrato)
        finally:
            CAN.buscar = antes

    def test_publicacao_do_nome_facto_unknown_coleta_a_parte(self):
        from test_canario_pdf import pdf_com_texto
        novo = RC.aplicar(_contrato(), proposta())
        r = self._correr(novo, pdf_com_texto("Bollettino agrometeorologico n. 38 del 21 settembre 2026 pioggia fenologia", 40))
        self.assertTrue(r["PASS"], r.get("PORQUE"))
        self.assertEqual("IT-T7-900:BOLETIM:AGROMETEO:2026-38", r["DOCUMENT_ID"])
        self.assertEqual("2026-09-21", r["TEMPOS"]["PUBLICATION_TIME"])
        self.assertTrue(r["TEMPOS"]["FACT_TIME"].startswith("UNKNOWN"))
        self.assertNotEqual(r["TEMPOS"]["COLLECTION_TIME"], r["TEMPOS"]["PUBLICATION_TIME"])

    def test_captura_que_nao_casa_e_identity_failed(self):
        from test_canario_pdf import pdf_com_texto
        outra = dict(IDENT, CAPTURES={"b": {"FROM": "URL", "PATTERN": r"/(\d{2})_bollettino_(\d{4})(\d{2})(\d{2})\.pdf$"}})
        novo = RC.aplicar(_contrato(), proposta(IDENTITY=outra))
        r = self._correr(novo, pdf_com_texto("Bollettino agrometeorologico n. 38 del 21 settembre 2026 pioggia fenologia", 40))
        self.assertFalse(r["PASS"])
        self.assertIn("IDENTITY_FAILED", r["PORQUE"])

    def test_o_molde_antigo_por_endereco_da_o_mesmo_de_antes(self):
        # o caminho que a JANELA-FORMAS A usava (replace a mao) e o do motor dao o mesmo DOCUMENT_ID
        from test_canario_pdf import pdf_com_texto
        p = proposta(); p.pop("IDENTITY")
        novo = RC.aplicar(_contrato(), p)
        r = self._correr(novo, pdf_com_texto("Bollettino agrometeorologico n. 38 del 21 settembre 2026 pioggia fenologia", 40))
        self.assertTrue(r["PASS"], r.get("PORQUE"))
        caminho = "bollettini-2026/38_boll_agro_20260921.pdf"
        self.assertEqual(novo["IDENTITY"]["DOCUMENT_ID"].replace("{doc.1}", caminho), r["DOCUMENT_ID"])


if __name__ == "__main__":
    unittest.main()
