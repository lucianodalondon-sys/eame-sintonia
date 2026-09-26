#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D47 (T2-BOLETINS): o corte do fim da ligacao (`ACQUISITION.STRIP_SUFFIX`) entra pela porta da
receita EXPLICITO, e o canario corta exactamente como o coletor ja cortava.

Medido na ARPAE (IT-T2-051, 25/09): as 60 ligacoes dos boletins agrometeo acabam em `.pdf/view` — a
pagina do Plone classico, nao o PDF. O coletor (`regras/motor_de_rota.mjs` · ligacoesDoIndice) ja
aplicava STRIP_SUFFIX; o canario nao: os dois abririam alvos diferentes. Nada vai a rede."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import canario as CAN            # noqa: E402
import reparar_contrato as RC    # noqa: E402
from test_reparar_contrato import _contrato  # noqa: E402

INDEX = "https://www.exemplo.it/bollettini-2026"
PADRAO = r"^https?://(www\.)?exemplo\.it/bollettini-2026/\d{2}_boll_agro_\d{8}(-\d)?\.pdf$"
PAGINA = ('<a href="bollettini-2026/38_boll_agro_20260921.pdf/view">38</a>'
          '<a href="/bollettini-2026/37_boll_agro_20260914.pdf/view">37</a>'
          '<a href="https://www.exemplo.it/bollettini-2026/15_boll_agro_20260413-2.pdf/view">15</a>'
          '<a href="/bollettini-2026/view">pasta</a><a href="/notizie/uma-noticia-qualquer">n</a>').encode()


def proposta(**kw):
    p = {"DESFECHO": "PADRAO_NOVO", "INDEX_URL": INDEX, "LINK_PATTERN": PADRAO, "OUTPUT_TYPE": "PDF",
         "STRIP_SUFFIX": "/view", "COMO": "bancada (teste)", "PORQUE": "boletins em .pdf/view"}
    p.update(kw)
    return p


class APortaAceitaOCorteExplicito(unittest.TestCase):

    def test_o_corte_pedido_entra_no_contrato_e_na_proveniencia(self):
        novo = RC.aplicar(_contrato(), proposta())
        self.assertEqual("/view", novo["ACQUISITION"]["STRIP_SUFFIX"])
        self.assertEqual("/view", novo["REPARO_DE_CONTRATO"]["STRIP_SUFFIX"])

    def test_sem_corte_pedido_nao_ha_corte(self):
        p = proposta(); p.pop("STRIP_SUFFIX")
        novo = RC.aplicar(_contrato(), p)
        self.assertNotIn("STRIP_SUFFIX", novo["ACQUISITION"])
        self.assertNotIn("STRIP_SUFFIX", novo["REPARO_DE_CONTRATO"])

    def test_corte_vazio_ou_com_espacos_recusa(self):
        for mau in ("", "  ", " /view", 7):
            with self.assertRaises(RC.ReparoInvalido, msg=repr(mau)):
                RC.aplicar(_contrato(), proposta(STRIP_SUFFIX=mau))

    def test_a_porta_continua_a_so_mudar_os_campos_dela(self):
        base = _contrato()
        novo = RC.aplicar(base, proposta())
        mexidos = {k for k in set(base) | set(novo) if base.get(k) != novo.get(k)}
        self.assertEqual(set(), mexidos - RC.CAMPOS_QUE_O_REPARO_MUDA - {"OUTPUT_TYPE"})


class OCanarioCortaComoOColetor(unittest.TestCase):

    def test_sem_corte_nenhum_boletim_casa(self):
        import re
        self.assertEqual([], [h for h in CAN.hrefs_da_entrada(PAGINA, INDEX) if re.match(PADRAO, h)])

    def test_com_corte_os_tres_boletins_casam(self):
        import re
        h = CAN.hrefs_da_entrada(PAGINA, INDEX, "/view")
        alvos = sorted(x for x in h if re.match(PADRAO, x))
        self.assertEqual(["https://www.exemplo.it/bollettini-2026/15_boll_agro_20260413-2.pdf",
                          "https://www.exemplo.it/bollettini-2026/37_boll_agro_20260914.pdf",
                          "https://www.exemplo.it/bollettini-2026/38_boll_agro_20260921.pdf"], alvos)

    def test_o_canario_le_o_corte_do_contrato(self):
        novo = RC.aplicar(_contrato(), proposta())
        vistos = []

        def buscar(u):
            vistos.append(u)
            return (200, PAGINA, "") if u == INDEX else (404, b"", "HTTP 404")
        antes, CAN.buscar = CAN.buscar, buscar
        try:
            CAN.canario_html(novo)
        finally:
            CAN.buscar = antes
        self.assertEqual(INDEX, vistos[0])
        self.assertTrue(vistos[1].endswith(".pdf"), vistos)     # o alvo aberto ja vem sem /view

    # ⚠️ Fora desta paridade, medido e NAO consertado aqui (antes da D47): uma ligacao com
    # `#fragmento` e descartada pelo motor (a regex dele para no `#`) e aproveitada pelo canario (que
    # corta o fragmento). A ARPAE nao tem fragmentos nas 60 ligacoes; fica no relatorio.
    @unittest.skipUnless(shutil.which("node"), "sem node nesta maquina")
    def test_paridade_com_o_motor_do_coletor(self):
        import re
        raiz = AQUI.parent
        js = ("import {ligacoesDoIndice} from './regras/motor_de_rota.mjs';"
              "const [html, aq] = JSON.parse(process.argv[1]);"
              "console.log(JSON.stringify(ligacoesDoIndice(html, aq)));")
        aq = {"INDEX_URL": INDEX, "LINK_PATTERN": PADRAO, "STRIP_SUFFIX": "/view", "MATCH": "URL"}
        r = subprocess.run(["node", "--input-type=module", "-e", js, json.dumps([PAGINA.decode(), aq])],
                           cwd=raiz, capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(0, r.returncode, r.stderr[-1500:])
        do_motor = json.loads(r.stdout.strip().splitlines()[-1])
        do_motor = sorted(do_motor if isinstance(do_motor, list) else do_motor.get("alvos") or do_motor.get("ALVOS") or [])
        do_canario = sorted(x for x in CAN.hrefs_da_entrada(PAGINA, INDEX, "/view") if re.match(PADRAO, x, re.I))
        self.assertEqual(do_motor, do_canario)


if __name__ == "__main__":
    unittest.main()
