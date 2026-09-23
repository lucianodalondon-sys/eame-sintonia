#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S1 -- o QUALIFY usa a amostra quando o nome nao decide o territorio.

Medido em 23/09: 105 QUALIFY em BLOCK SEMANTIC, todas com
CONTENT_VALUE_TYPE vazio -- o worker nunca passava amostra a territorio_de.

A rede e cortada na fronteira: o robots (gate_de_rota.robots_de) e o pedido
HTTP (capturador.buscar) sao substituidos por um site falso. Todo o estado
(fila, livro, alocacao, amostras) vive numa pasta temporaria.
"""
import hashlib
import json
import sys
import tempfile
import unittest
import urllib.robotparser
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))

import amostrar as AM          # noqa: E402
import capturador as CAP       # noqa: E402
import fila as F               # noqa: E402
import fonte_nova as FN        # noqa: E402
import gate_de_rota as GATE    # noqa: E402
import lifecycle as LC         # noqa: E402
import worker as W             # noqa: E402

# Nome e endereco que NENHUMA regra de nome reconhece: so a amostra decide.
NOME = "Portale Qzxv"
BASE = "https://www.qzxv-portale.example/"
ITEM = BASE + "notizie/2026/09/bando-graduatoria-misura-quattro"

TEXTO_REGULATORIO = (
    "<html><head><title>Bando misura 4</title></head><body><p>"
    + "Il decreto regionale approva la graduatoria del bando. "
      "La delibera fissa il regolamento e la normativa del bando. " * 12
    + "</p></body></html>").encode("utf-8")
TEXTO_GENERICO = (
    "<html><head><title>Chi siamo</title></head><body><p>"
    + "Benvenuti sul nostro sito, qui trovate orari e contatti utili. " * 12
    + "</p></body></html>").encode("utf-8")


def _indice(links):
    corpo = "".join('<a href="%s">x</a>' % u for u in links)
    return ("<html><body>%s</body></html>" % corpo).encode("utf-8")


def _rp(regras):
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(regras)
    return rp


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="qualify-sem-"))
        self._orig = {(F, "FILA"): F.FILA, (LC, "LIVRO"): LC.LIVRO,
                      (W, "ALLOCATION"): W.ALLOCATION, (W, "EVIDENCIA"): W.EVIDENCIA,
                      (FN, "FILA"): FN.FILA, (AM, "RAIZ"): AM.RAIZ,
                      (AM, "AMOSTRAS"): AM.AMOSTRAS}
        F.FILA = self.tmp / "fila.json"
        LC.LIVRO = self.tmp / "livro.json"
        W.ALLOCATION = self.tmp / "alloc.json"
        W.EVIDENCIA = self.tmp / "evid.json"
        FN.FILA = self.tmp / "candidatas.json"
        AM.RAIZ = self.tmp
        AM.AMOSTRAS = self.tmp / "amostras"
        W.ALLOCATION.write_text(json.dumps({
            "DATASET": "SOURCE-ID-ALLOCATION-V1",
            "MAIOR_POR_TERRITORIO_ANTES": {"T4": 20},
            "ATRIBUIDOS": 0, "NOVAS": []}), encoding="utf-8")
        self.pedidos = []

    def tearDown(self):
        for (mod, attr), v in self._orig.items():
            setattr(mod, attr, v)

    def _site(self, paginas):
        def buscar(url, aceita="*/*"):
            self.pedidos.append(url)
            if url in paginas:
                b = paginas[url]
                return {"OK": True, "STATUS": 200, "FINAL_URL": url,
                        "CONTENT_TYPE": "text/html", "BYTES": len(b),
                        "CORPO": b, "FALHA": None}
            return {"OK": False, "STATUS": 404, "FINAL_URL": url,
                    "CONTENT_TYPE": "", "BYTES": 0, "CORPO": b"",
                    "FALHA": "HTTP_ERROR"}
        return buscar

    def _correr(self, paginas, robots=("User-agent: *", "Disallow:")):
        doc = FN.carregar()
        doc["CANDIDATAS"].append({
            "CANDIDATA_ID": "CAND-9901", "TIPO": "BASE_OFICIAL", "NOME": NOME,
            "URL": BASE, "PAIS": "IT", "ESTADO": "EM_ANALISE", "SOURCE_ID": None})
        FN.gravar(doc)
        F.enfileirar("CAND-9901", F.QUALIFY, priority=30, motivo="teste")
        with mock.patch.object(GATE, "robots_de",
                               lambda host: (_rp(list(robots)), "teste")), \
             mock.patch.object(CAP, "buscar", self._site(paginas)), \
             mock.patch("time.sleep", lambda *_: None):
            return W.correr(max_tarefas=1, pausa=0, verboso=False)[0]

    def _alocadas(self):
        return json.loads(W.ALLOCATION.read_text(encoding="utf-8"))["NOVAS"]

    def _evidencia(self):
        return json.loads(W.EVIDENCIA.read_text(encoding="utf-8"))


class TestAmostraDecide(_Base):

    def test_amostra_regulatoria_da_territorio_com_prova(self):
        r = self._correr({BASE: _indice([ITEM]), ITEM: TEXTO_REGULATORIO})
        self.assertEqual(r["RESULTADO"], "OK", r)
        novas = self._alocadas()
        self.assertEqual(len(novas), 1)
        self.assertIn("T4", json.dumps(novas))
        # a prova e o sha256 dos bytes realmente colhidos
        sha = hashlib.sha256(TEXTO_REGULATORIO).hexdigest()
        self.assertIn(sha, json.dumps(self._evidencia()))
        self.assertNotEqual(LC.estado_de("CAND-9901"), LC.SEMANTIC_REVIEW)

    def test_qualify_com_amostra_nunca_promove_ready(self):
        self._correr({BASE: _indice([ITEM]), ITEM: TEXTO_REGULATORIO})
        self.assertNotIn(LC.READY_FOR_COLLECTION, LC.snapshot().values())


class TestAmostraNaoDecide(_Base):

    def _bloqueou_sem_fabricar(self, r):
        self.assertEqual(r["RESULTADO"], "BLOCK", r)
        self.assertEqual(self._alocadas(), [])
        self.assertEqual(LC.estado_de("CAND-9901"), LC.SEMANTIC_REVIEW)

    def test_amostra_generica_continua_bloqueada(self):
        self._bloqueou_sem_fabricar(
            self._correr({BASE: _indice([ITEM]), ITEM: TEXTO_GENERICO}))

    def test_indice_sem_item_continua_bloqueado(self):
        self._bloqueou_sem_fabricar(self._correr({BASE: _indice([])}))

    def test_site_fora_do_ar_continua_bloqueado(self):
        self._bloqueou_sem_fabricar(self._correr({}))

    def test_robots_proibe_nao_busca_nada(self):
        r = self._correr({BASE: _indice([ITEM]), ITEM: TEXTO_REGULATORIO},
                         robots=("User-agent: *", "Disallow: /"))
        self._bloqueou_sem_fabricar(r)
        self.assertEqual(self.pedidos, [], "robots proibe: nenhum pedido ao site")

    def test_tecto_de_pedidos_por_site(self):
        itens = [BASE + "notizie/2026/09/bando-numero-%d-misura" % i for i in range(8)]
        pag = {BASE: _indice(itens)}
        pag.update({u: TEXTO_REGULATORIO for u in itens})
        self._correr(pag)
        self.assertLessEqual(len(self.pedidos), 2,
                             "indice + 1 item; mais que isso fura o tecto: %s" % self.pedidos)


if __name__ == "__main__":
    unittest.main(verbosity=2)
