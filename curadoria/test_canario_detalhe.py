#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CANARIO HTML DO CURATOR EXIGE UM ITEM REAL — e o gate e o que o exige.

    HOMEPAGE 200 NAO BASTA.   INDEX_URL -> DETAIL_LINKS -> ITEM -> BODY UTIL.

Rede simulada: `canario.buscar` e substituido por um dicionario url -> resposta.
Nada sai a rede, nada e guardado, o livro real nao e tocado.

A PROVA POR MUTACAO ESTA ESCRITA: `test_6` neutraliza o gate e mostra que a
mesma capa PASSA. E o teste que diz «o gate e o que barra» — se alguem o
remover do canario, `test_1` fica vermelho e `test_6` fica sem sentido.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import canario as CAN            # noqa: E402
import fila as F                 # noqa: E402
import lifecycle as LC           # noqa: E402
import retrato_html as RH        # noqa: E402
import worker as W               # noqa: E402
from test_retrato_html import artigo_sintetico, listagem_sintetica  # noqa: E402

INDEX = "https://ex.it/news/"
ITEM = "https://ex.it/news/mosca-olivo-calo-termico/"
CONTRATO = {
    "SOURCE_ID": "IT-PROVA-DETALHE", "NAME": "prova", "OUTPUT_TYPE": "HTML",
    "BATCH_ID": "LOTE-HTML-ARTIGO",
    "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL",
                    "INDEX_URL": INDEX,
                    "LINK_PATTERN": r"^https?://ex\.it/news/[a-z0-9]+(?:-[a-z0-9]+)+/?$",
                    "MAX_TARGETS": 1},
    "IDENTITY": {"DOCUMENT_ID": "IT-PROVA-DETALHE:URL:{doc.1}"},
}


def indice_com_itens(n: int = 60) -> str:
    ligacoes = "".join('<li><a href="/news/mosca-olivo-calo-termico/">x</a></li>'
                       if i == 0 else
                       '<li><a href="/news/item-%d-titolo-breve/">Titolo %d</a></li>' % (i, i)
                       for i in range(n))
    return "<html><body><nav><ul>%s</ul></nav></body></html>" % ligacoes


def rede(respostas: dict):
    """url -> HTML. A chave ITEM serve QUALQUER endereco de item do indice: o
    canario abre o primeiro alvo por ordem alfabetica, e o teste nao deve
    depender de qual dos 60 e."""
    def _buscar(url: str):
        r = respostas.get(url)
        if r is None and url != INDEX and url.startswith(INDEX) and ITEM in respostas:
            r = respostas[ITEM]
        if r is None:
            return 404, b"", "HTTP 404"
        return 200, r.encode("utf-8"), ""
    return _buscar


class OCanarioHtmlAbreOItemEJulgaO(unittest.TestCase):

    def canario(self, respostas: dict) -> dict:
        with mock.patch.object(CAN, "buscar", rede(respostas)):
            return CAN.canario_html(CONTRATO)

    def test_1_item_que_e_capa_REPROVA_pelo_gate(self):
        r = self.canario({INDEX: indice_com_itens(), ITEM: listagem_sintetica()})
        self.assertFalse(r["PASS"])
        self.assertEqual("SOURCE_FAILURE", r["CLASSE"])
        self.assertTrue(r["PORQUE"].startswith("CAPA_NAO_E_MATERIA"), r["PORQUE"])
        self.assertIs(False, r["DETAIL_GATE_PASSED"])
        self.assertEqual("CAPA_PROVAVEL", r["ITEM_ABERTO"]["CAPA_OU_MATERIA"])
        self.assertEqual(60, r["DETAIL_ENUMERATED"])

    def test_2_item_que_e_materia_PASSA_com_o_gate_registado(self):
        r = self.canario({INDEX: indice_com_itens(), ITEM: artigo_sintetico()})
        self.assertTrue(r["PASS"], r.get("PORQUE"))
        self.assertIs(True, r["DETAIL_GATE_PASSED"])
        self.assertEqual(RH.GATE_VERSAO, r["DETAIL_GATE"])
        self.assertEqual("MATERIA_PROVAVEL", r["ITEM_ABERTO"]["CAPA_OU_MATERIA"])
        self.assertTrue(r["ITEM_ABERTO"]["URL"].startswith(INDEX))
        self.assertNotEqual(INDEX, r["ITEM_ABERTO"]["URL"], "o item nao e a entrada")
        self.assertTrue(r["DOCUMENT_ID"].startswith("IT-PROVA-DETALHE:URL:news/"), r["DOCUMENT_ID"])

    def test_2b_um_BOM_a_frente_do_html_nao_e_bytes_errados(self):
        with mock.patch.object(CAN, "buscar", lambda u: (200, (b"\xef\xbb\xbf" if u != INDEX else b"")
                               + (indice_com_itens() if u == INDEX else artigo_sintetico()).encode("utf-8"), "")):
            r = CAN.canario_html(CONTRATO)
        self.assertTrue(r["PASS"], r.get("PORQUE"))

    def test_3_item_sem_texto_REPROVA_body_util_e_obrigatorio(self):
        r = self.canario({INDEX: indice_com_itens(),
                          ITEM: "<html><body><script>var x=1;</script></body></html>"})
        self.assertFalse(r["PASS"])
        self.assertTrue(r["PORQUE"].startswith("ITEM_SEM_TEXTO"), r["PORQUE"])
        self.assertEqual("EMPTY", r["ITEM_ABERTO"]["HTML_KIND"])

    def test_4_homepage_200_sem_itens_nao_basta(self):
        r = self.canario({INDEX: artigo_sintetico()})   # 200, texto, e nenhum link de item
        self.assertFalse(r["PASS"])
        self.assertIn("EMPTY_LIST", r["PORQUE"])
        self.assertNotIn("ITEM_ABERTO", r, "sem alvo nao ha item a retratar")

    def test_5_o_padrao_que_devolve_a_propria_entrada_e_ROUTE_FAILURE(self):
        c = dict(CONTRATO, ACQUISITION=dict(CONTRATO["ACQUISITION"],
                                            INDEX_URL="https://ex.it/news/solo-uno/",
                                            LINK_PATTERN=r"^https?://ex\.it/news/solo-uno/?$"))
        pagina = '<html><body><a href="/news/solo-uno/">eu</a><p>%s</p></body></html>' % ("x " * 600)
        with mock.patch.object(CAN, "buscar", rede({"https://ex.it/news/solo-uno/": pagina})):
            r = CAN.canario_html(c)
        self.assertFalse(r["PASS"])
        self.assertEqual("ROUTE_FAILURE", r["CLASSE"])

    def test_6_MUTACAO_com_o_gate_neutralizado_a_capa_passa(self):
        """O gate e o que barra. Neutraliza-lo faz a capa de test_1 passar —
        e por isso test_1 e a prova de que ele esta ligado."""
        with mock.patch.object(RH, "gate_capa_nao_e_materia", return_value=None):
            r = self.canario({INDEX: indice_com_itens(), ITEM: listagem_sintetica()})
        self.assertTrue(r["PASS"], "sem o gate, a capa passaria — e e isso que o gate impede")
        self.assertEqual("CAPA_PROVAVEL", r["ITEM_ABERTO"]["CAPA_OU_MATERIA"],
                         "o retrato continua a dizer capa; so o juiz foi calado")


class OWorkerSoPromoveComOGate(unittest.TestCase):
    """Livro, fila, evidencia e contratos numa pasta descartavel."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (LC.LIVRO, F.FILA, W.EVIDENCIA, W.CONTRATOS)
        LC.LIVRO = d / "LEDGER.json"
        F.FILA = d / "QUEUE.json"
        W.EVIDENCIA = d / "EVIDENCE.json"
        W.CONTRATOS = d / "contracts.json"
        W.CONTRATOS.write_text(json.dumps({"FONTES": [CONTRATO]}), encoding="utf-8")
        LC.registar("IT-PROVA-DETALHE", LC.CANARY_PENDING, "prova")

    def tearDown(self):
        LC.LIVRO, F.FILA, W.EVIDENCIA, W.CONTRATOS = self._antes
        self.tmp.cleanup()

    def _correr(self, respostas: dict) -> dict:
        t = F.enfileirar("IT-PROVA-DETALHE", F.CANARY, priority=60)
        t = F.proxima()
        with mock.patch.object(CAN, "buscar", rede(respostas)):
            return W.executar_uma(t, W._contratos())

    def test_7_capa_nao_promove_e_fica_CANARY_FAILED_com_o_gate_na_evidencia(self):
        r = self._correr({INDEX: indice_com_itens(), ITEM: listagem_sintetica()})
        self.assertEqual("FAIL", r["RESULTADO"])
        self.assertEqual(LC.CONTRACTED_CANARY_FAILED, LC.estado_de("IT-PROVA-DETALHE"))
        ev = json.loads(W.EVIDENCIA.read_text(encoding="utf-8"))["PROVAS"][-1]
        self.assertIs(False, ev["DADOS"]["DETAIL_GATE_PASSED"])
        self.assertTrue(LC.historia("IT-PROVA-DETALHE")[-1]["REASON"].startswith("CAPA_NAO_E_MATERIA"))

    def test_8_materia_promove_e_a_linha_do_livro_diz_que_regua_passou(self):
        r = self._correr({INDEX: indice_com_itens(), ITEM: artigo_sintetico()})
        self.assertEqual("OK", r["RESULTADO"])
        self.assertEqual(LC.READY_FOR_COLLECTION, LC.estado_de("IT-PROVA-DETALHE"))
        linha = LC.historia("IT-PROVA-DETALHE")[-1]
        self.assertIn("gate de detalhe", linha["REASON"])
        self.assertIn(RH.GATE_VERSAO, linha["REASON"])
        ev = json.loads(W.EVIDENCIA.read_text(encoding="utf-8"))["PROVAS"][-1]
        self.assertIs(True, ev["DADOS"]["DETAIL_GATE_PASSED"])
        self.assertEqual(linha["EVIDENCE_REF"], ev["EVIDENCE_REF"])


class EscolherAlvo(unittest.TestCase):
    """HR-6: o canario abre o primeiro item SEM cara de seccao; se todos tem, o 1.o."""

    def test_salta_o_endereco_com_cara_de_seccao(self):
        alvos = ["https://ex.it/news/assemblea-agronomi-udine/",
                 "https://ex.it/news/bando-psr-2026-misura-4/"]
        self.assertEqual(alvos[1], CAN.escolher_alvo(alvos, INDEX))

    def test_todos_com_cara_de_seccao_fica_o_primeiro(self):
        alvos = ["https://ex.it/categorie/blog/curiosita-dalla-natura/",
                 "https://ex.it/categorie/blog/ricette/"]
        self.assertEqual(alvos[0], CAN.escolher_alvo(alvos, INDEX))

    def test_nunca_escolhe_a_propria_entrada(self):
        entrada = "https://ex.it/news/ultime-notizie-dal-consiglio/"
        alvos = [entrada, "https://ex.it/news/zz-bando-psr-2026/"]
        self.assertEqual(alvos[1], CAN.escolher_alvo(alvos, entrada))

    def test_o_canario_abre_o_item_fundo_e_o_gate_continua_a_julgar(self):
        indice = ("<html><body><ul><li><a href='/news/assemblea-agronomi-udine/'>a</a></li>"
                  "<li><a href='/news/nuovo-bando-psr-per-giovani-agricoltori/'>b</a></li>"
                  "</ul></body></html>")
        vistos = []
        def _buscar(u):
            vistos.append(u)
            return 200, (indice if u == INDEX else artigo_sintetico()).encode("utf-8"), ""
        with mock.patch.object(CAN, "buscar", _buscar),                 mock.patch.object(CAN, "_regua_manda", lambda s: True):
            r = CAN.canario_html(CONTRATO)
        self.assertTrue(r["PASS"], r.get("PORQUE"))
        self.assertEqual("https://ex.it/news/nuovo-bando-psr-per-giovani-agricoltori/",
                         r["ITEM_ABERTO"]["URL"])
        self.assertEqual([INDEX, r["ITEM_ABERTO"]["URL"]], vistos)

    def test_item_fundo_que_falha_volta_ao_primeiro_nunca_pior_do_que_hoje(self):
        indice = ("<html><body><ul><li><a href='/news/assemblea-agronomi-udine/'>a</a></li>"
                  "<li><a href='/news/bollettino-nocciolo-n-10-2026/'>b</a></li>"
                  "</ul></body></html>")
        def _buscar(u):
            if u == INDEX:
                return 200, indice.encode("utf-8"), ""
            if "bollettino" in u:
                return 200, b"%PDF-1.7 ...", ""
            return 200, artigo_sintetico().encode("utf-8"), ""
        with mock.patch.object(CAN, "buscar", _buscar),                 mock.patch.object(CAN, "_regua_manda", lambda s: True):
            r = CAN.canario_html(CONTRATO)
        self.assertTrue(r["PASS"], r.get("PORQUE"))
        self.assertEqual("https://ex.it/news/assemblea-agronomi-udine/", r["ITEM_ABERTO"]["URL"])
        self.assertIn("BYTE_VALIDATION_FAILED", r["ALVO_FUNDO_TENTADO"]["PORQUE"])


if __name__ == "__main__":
    unittest.main()
