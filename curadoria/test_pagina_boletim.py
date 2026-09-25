#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D42 (2): «A PAGINA E O BOLETIM» no lado do Curator — forma explicita no contrato, canario que
pergunta a identidade ao MOTOR do coletor (um motor so), regua irma PAGINA_BOLETIM/v1 que o portao
aceita, e o worker a escolher o canario pela FORMA. Nada vai a rede: `buscar` e um dicionario."""
from __future__ import annotations

import copy
import shutil
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import canario as CAN              # noqa: E402
import collection_gate as CG       # noqa: E402
import ready_split as RS           # noqa: E402
import validar_contratos as VC     # noqa: E402
import worker as W                 # noqa: E402
from test_reparar_contrato import _contrato   # noqa: E402

URL = "https://www.exemplo.it/agrometeo/firenze"


def contrato_boletim(**kw):
    c = _contrato("IT-T2-900")
    c.update({
        "FORMA": "PAGINA_E_BOLETIM", "OUTPUT_TYPE": "HTML", "CANONICAL_ENTRY_URL": URL,
        "ACQUISITION": {"STRATEGY": "STATIC_ENDPOINT", "URL": URL, "NAME": "firenze.html"},
        "RECOLLECTION": {"DETAIL_CONTENT": "MUTABLE"},
        "IDENTITY": {
            "STRATEGY": "CONTENT_CAPTURE",
            "DOCUMENT_ID": "IT-T2-900:BOLETIM:{emissao.3}-{emissao.2}-{emissao.1}",
            "SOURCE_DATE": "{emissao.1}/{emissao.2}/{emissao.3}",
            "SOURCE_DATE_ISO": "{emissao.3}-{emissao.2}-{emissao.1}",
            "FACT_TIME": "UNKNOWN",
            "CONTENT_SCOPE": {"START": "Bollettino agrometeorologico", "END": "Fine bollettino"},
            "CAPTURES": {"emissao": {"FROM": "PAGE_TEXT", "PATTERN": "Emesso il (\\d{2})/(\\d{2})/(\\d{4})",
                                     "REQUIRED": False, "DEFAULTS": ["UNKNOWN", "UNKNOWN", "UNKNOWN"]}},
        },
    })
    c.update(kw)
    return c


def pagina(emissao="24/09/2026", corpo="Olivo: mosca in aumento. " * 30, com_boletim=True):
    miolo = ("<h1>Bollettino agrometeorologico</h1><p>%s</p><p>%s</p><p>Fine bollettino</p>"
             % ("Emesso il %s" % emissao if emissao else "Senza data", corpo)) if com_boletim else "<p>manutenzione</p>"
    return ("<html><body><nav><a href='/'>Home</a> Visite: 12</nav>%s<footer>Contatti</footer></body></html>"
            % miolo).encode()


def correr(c, b, st=200):
    velho = CAN.buscar
    CAN.buscar = lambda u: (st, b, None) if u == URL else (404, b"", "HTTP 404")
    try:
        return CAN.canario_pagina_boletim(c)
    finally:
        CAN.buscar = velho


def regua(c, r):
    return RS.passos_da_promocao({"OBSERVED_AT": datetime.now(timezone.utc).isoformat(), "EVIDENCE_REF": "x"},
                                 {"DADOS": r}, c)


class OValidadorDaForma(unittest.TestCase):

    def test_contrato_completo_passa(self):
        ok, mau = VC.validar([contrato_boletim()])
        self.assertEqual([], mau)

    def test_cada_falta_reprova(self):
        faltas = {
            "sem MUTABLE": contrato_boletim(RECOLLECTION={"DETAIL_CONTENT": "IMMUTABLE"}),
            "lista em vez de rota fixa": contrato_boletim(ACQUISITION={"STRATEGY": "HTML_LINK_DISCOVERY",
                                                                        "INDEX_URL": URL, "LINK_PATTERN": "^x$"}),
            "sem recorte": contrato_boletim(IDENTITY=dict(contrato_boletim()["IDENTITY"], CONTENT_SCOPE=None)),
            "hash no DOCUMENT_ID": contrato_boletim(IDENTITY=dict(contrato_boletim()["IDENTITY"],
                                                                  DOCUMENT_ID="IT-T2-900:BOLETIM:SHA:{emissao.1}")),
            "forma desconhecida": contrato_boletim(FORMA="PAGINA_TALVEZ"),
            "saida PDF": contrato_boletim(OUTPUT_TYPE="PDF"),
        }
        for nome, c in faltas.items():
            with self.subTest(nome):
                self.assertFalse(VC.form_resolved(c)[0], nome)

    def test_sem_forma_nada_muda(self):
        self.assertTrue(VC.form_resolved(_contrato())[0])


@unittest.skipUnless(shutil.which("node"), "sem node nesta maquina")
class OCanarioPerguntaAoMotor(unittest.TestCase):

    def test_boletim_com_data_passa_e_a_regua_e_a_irma(self):
        c = contrato_boletim()
        r = correr(c, pagina())
        self.assertTrue(r["PASS"], r.get("PORQUE"))
        it = r["ITEM_ABERTO"]
        self.assertEqual("IT-T2-900:BOLETIM:2026-09-24", it["DOCUMENT_ID"])
        self.assertEqual("2026-09-24", it["SOURCE_DATE_ISO"])
        self.assertTrue(it["DATA_COMPROVADA"])
        self.assertRegex(it["CONTENT_SHA256"], r"^[0-9a-f]{64}$")
        g = regua(c, r)
        self.assertEqual(RS.REGUA_PAGINA_BOLETIM, g["REGUA"], g)
        self.assertTrue(RS.e_corrente(g["REGUA"]))

    def test_sem_data_passa_com_unknown_e_a_regua_diz(self):
        c = contrato_boletim()
        r = correr(c, pagina(emissao=None))
        self.assertTrue(r["PASS"], r.get("PORQUE"))
        self.assertEqual("UNKNOWN", r["ITEM_ABERTO"]["SOURCE_DATE_ISO"])
        self.assertFalse(r["ITEM_ABERTO"]["DATA_COMPROVADA"])
        g = regua(c, r)
        self.assertEqual(RS.REGUA_PAGINA_BOLETIM, g["REGUA"])
        self.assertFalse(g["INFO"]["DATA_COMPROVADA"])

    def test_sem_boletim_na_pagina_reprova(self):
        r = correr(contrato_boletim(), pagina(com_boletim=False))
        self.assertFalse(r["PASS"])
        self.assertIn("IDENTITY_FAILED", r["PORQUE"])

    def test_boletim_curto_reprova(self):
        r = correr(contrato_boletim(), pagina(corpo="Breve."))
        self.assertFalse(r["PASS"])
        self.assertIn("caracteres", r["PORQUE"])

    def test_nao_html_reprova(self):
        r = correr(contrato_boletim(), b"%PDF-1.4 ...")
        self.assertFalse(r["PASS"])
        self.assertIn("BYTE_VALIDATION_FAILED", r["PORQUE"])


class ARegua(unittest.TestCase):

    def test_as_formas_nao_se_misturam(self):
        # uma prova de LISTA num contrato de pagina-boletim nao da DETAIL/v1 (nem nada corrente)
        prova_lista = {"PASS": True, "DETAIL_GATE_PASSED": True, "DETAIL_ENUMERATED": 5,
                       "ITEM_ABERTO": {"URL": "https://x.it/news/a-b-c", "HTTP": 200, "HTML_KIND": "CONTENT",
                                       "CAPA_OU_MATERIA": RS.MATERIA, "PARAGRAPH_CHARACTERS": 2000}}
        self.assertEqual(RS.REGUA_LEGACY, regua(contrato_boletim(), prova_lista)["REGUA"])
        # uma prova de PAGINA-BOLETIM num contrato de lista nao da PAGINA_BOLETIM/v1
        prova_bol = {"PASS": True, "DETAIL_GATE_PASSED": True, "ITEM_ABERTO": {
            "FORMA": "PAGINA_E_BOLETIM", "DOCUMENT_ID": "X:BOLETIM:2026-09-24", "CONTENT_SHA256": "a" * 64,
            "BOLETIM_CARACTERES": 900}}
        self.assertNotIn(regua(_contrato(), prova_bol)["REGUA"], RS.REGUAS_CORRENTES)

    def test_sem_recolha_mutavel_nao_passa(self):
        c = contrato_boletim(RECOLLECTION={"DETAIL_CONTENT": "IMMUTABLE"})
        prova = {"PASS": True, "DETAIL_GATE_PASSED": True, "ITEM_ABERTO": {
            "FORMA": "PAGINA_E_BOLETIM", "DOCUMENT_ID": "X:BOLETIM:2026-09-24", "CONTENT_SHA256": "a" * 64,
            "BOLETIM_CARACTERES": 900}}
        self.assertEqual(RS.REGUA_LEGACY, regua(c, prova)["REGUA"])


class OPortaoEORobo(unittest.TestCase):

    def test_o_portao_aceita_a_regua_irma_e_continua_a_recusar_legacy(self):
        self.assertTrue(RS.e_corrente(RS.REGUA_PAGINA_BOLETIM))
        self.assertTrue(RS.e_corrente(RS.REGUA_CURRENT))
        self.assertFalse(RS.e_corrente(RS.REGUA_LEGACY))
        self.assertFalse(RS.e_corrente("NAO SEI"))

    def test_o_robo_escolhe_o_canario_pela_forma(self):
        with mock.patch.object(CAN, "canario_pagina_boletim", return_value={"PASS": True}) as pb, \
             mock.patch.object(CAN, "canario_html", return_value={"PASS": True}) as ph:
            W.etapa_canary("IT-T2-900", contrato_boletim())
            W.etapa_canary("IT-T7-900", _contrato())
        self.assertEqual(1, pb.call_count)
        self.assertEqual(1, ph.call_count)

    def test_a_validacao_de_rota_le_a_url_da_rota_fixa(self):
        c = contrato_boletim()
        with mock.patch.object(W.GATE, "robots_de", return_value=(mock.Mock(), "User-agent: *")), \
             mock.patch.object(W.GATE, "permitido", return_value=True) as perm:
            r, d = W.etapa_validate_route("IT-T2-900", c)
        self.assertEqual("OK", r, d)
        self.assertEqual(URL, perm.call_args[0][0])


if __name__ == "__main__":
    unittest.main()
