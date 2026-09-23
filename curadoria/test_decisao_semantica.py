#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S2 -- a decisao semantica (Opus/humano) entra pelo canal, COM PROVA, ou nao entra.

    UMA DECISAO SEM PROVA E UMA OPINIAO. O CANAL IGNORA-A.

Vai pela porta publica do worker (W.correr) com todo o estado numa pasta
temporaria: fila, livro, alocacao, candidatas e o ficheiro de decisoes.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))

import decisao_semantica as DS  # noqa: E402
import fila as F                 # noqa: E402
import fonte_nova as FN          # noqa: E402
import lifecycle as LC           # noqa: E402
import worker as W               # noqa: E402

CAND = "CAND-9950"
NOME = "Portale Qzxv"                      # nenhuma regra de nome o reconhece
URL = "https://www.qzxv-portale.example/"
SHA = "ab" * 32


def _prova(papel, url, sha=SHA):
    return {"PAPEL": papel, "URL": url, "SHA256": sha,
            "BYTES_EM": "fora do Git (teste)"}


def _decisao(**mudar):
    d = {"CANDIDATA_ID": CAND, "URL": URL, "TERRITORIO": "T12", "PAIS": "IT",
         "DECIDIDO_POR": "OPUS", "PORQUE": "organismo pagador da PAC",
         "PROVAS": [_prova("INSTITUCIONAL", URL + "chi-siamo", "a1" * 32),
                    _prova("CONTEUDO", URL + "notizie/2026/09/anticipi-pac", "b2" * 32),
                    _prova("CONTEUDO", URL + "documenti/istruzioni-operative-30", "c3" * 32)]}
    d.update(mudar)
    return d


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="decisao-sem-"))
        self._orig = {(F, "FILA"): F.FILA, (LC, "LIVRO"): LC.LIVRO,
                      (W, "ALLOCATION"): W.ALLOCATION, (W, "EVIDENCIA"): W.EVIDENCIA,
                      (FN, "FILA"): FN.FILA, (DS, "DECISOES"): DS.DECISOES}
        F.FILA = self.tmp / "fila.json"
        LC.LIVRO = self.tmp / "livro.json"
        W.ALLOCATION = self.tmp / "alloc.json"
        W.EVIDENCIA = self.tmp / "evid.json"
        FN.FILA = self.tmp / "candidatas.json"
        DS.DECISOES = self.tmp / "decisoes.json"
        W.ALLOCATION.write_text(json.dumps({
            "DATASET": "SOURCE-ID-ALLOCATION-V1",
            "MAIOR_POR_TERRITORIO_ANTES": {"T12": 7, "T7": 40},
            "ATRIBUIDOS": 0, "NOVAS": []}), encoding="utf-8")

    def tearDown(self):
        for (mod, attr), v in self._orig.items():
            setattr(mod, attr, v)

    def _correr(self, decisoes, nome=NOME, url=URL):
        DS.DECISOES.write_text(json.dumps({"DATASET": "SEMANTIC-DECISIONS-V1",
                                           "DECISOES": decisoes}), encoding="utf-8")
        doc = FN.carregar()
        doc["CANDIDATAS"].append({"CANDIDATA_ID": CAND, "TIPO": "BASE_OFICIAL",
                                  "NOME": nome, "URL": url, "PAIS": "IT",
                                  "ESTADO": "EM_ANALISE", "SOURCE_ID": None})
        FN.gravar(doc)
        F.enfileirar(CAND, F.QUALIFY, priority=30, motivo="teste")
        return W.correr(max_tarefas=1, pausa=0, verboso=False)[0]

    def _novas(self):
        return json.loads(W.ALLOCATION.read_text(encoding="utf-8"))["NOVAS"]

    def _bloqueou(self, r):
        self.assertEqual(r["RESULTADO"], "BLOCK", r)
        self.assertEqual(self._novas(), [], "sem prova valida nao se aloca numero")
        self.assertEqual(LC.estado_de(CAND), LC.SEMANTIC_REVIEW)


class TestDecisaoComProva(_Base):

    def test_decisao_com_prova_multipla_tira_do_block(self):
        r = self._correr([_decisao()])
        self.assertEqual(r["RESULTADO"], "OK", r)
        novas = self._novas()
        self.assertEqual(len(novas), 1)
        self.assertIn("IT-T12-008", json.dumps(novas))
        self.assertIn("OPUS", json.dumps(novas))       # a proveniencia viaja
        self.assertNotIn(LC.READY_FOR_COLLECTION, LC.snapshot().values())

    def test_a_lei_vale_como_prova_do_que_e(self):
        provas = [_prova("LEI", "https://www.normattiva.it/uri-res/N2Ls?urn:x", "d4" * 32),
                  _prova("CONTEUDO", URL + "a", "e5" * 32),
                  _prova("CONTEUDO", URL + "b", "f6" * 32)]
        self.assertEqual(self._correr([_decisao(PROVAS=provas)])["RESULTADO"], "OK")

    def test_decisao_nao_passa_por_cima_do_nome(self):
        """O nome ja decide (Consorzio -> T7): o canal nao e consultado."""
        r = self._correr([_decisao()], nome="Consorzio Qzxv")
        self.assertEqual(r["RESULTADO"], "OK", r)
        self.assertIn("IT-T7-041", json.dumps(self._novas()))


class TestCanalExigePais(unittest.TestCase):
    """O canal, sozinho, recusa a decisao sem pais — nao depende do worker."""

    def test_canal_recusa_decisao_sem_pais(self):
        d = _decisao()
        del d["PAIS"]
        motivo = DS.porque_invalida(d, {"URL": URL})
        self.assertIsNotNone(motivo)
        self.assertIn("PAIS", motivo)

    def test_canal_aceita_pais_da_prova(self):
        for pais in ("IT", "EU", "INT"):
            self.assertIsNone(DS.porque_invalida(_decisao(PAIS=pais), {"URL": URL}), pais)


class TestDecisaoSemProvaIgnorada(_Base):

    def test_sem_decisao_continua_bloqueada(self):
        self._bloqueou(self._correr([]))

    def test_sem_provas(self):
        self._bloqueou(self._correr([_decisao(PROVAS=[])]))

    def test_so_uma_prova_de_conteudo(self):
        d = _decisao()
        d["PROVAS"] = d["PROVAS"][:2]
        self._bloqueou(self._correr([d]))

    def test_sem_prova_institucional(self):
        d = _decisao()
        d["PROVAS"] = [p for p in d["PROVAS"] if p["PAPEL"] == "CONTEUDO"]
        self._bloqueou(self._correr([d]))

    def test_sha256_invalido(self):
        d = _decisao()
        d["PROVAS"][1]["SHA256"] = "nao-e-um-sha"
        self._bloqueou(self._correr([d]))

    def test_mesma_pagina_nao_conta_duas_vezes(self):
        d = _decisao()
        d["PROVAS"][2]["URL"] = d["PROVAS"][1]["URL"]
        self._bloqueou(self._correr([d]))

    def test_bytes_iguais_em_urls_diferentes_contam_uma_vez(self):
        """Tres URLs, a mesma casca de JavaScript: uma prova so."""
        d = _decisao()
        for p in d["PROVAS"]:
            p["SHA256"] = SHA
        self._bloqueou(self._correr([d]))

    def test_sem_pais_a_decisao_nao_vale(self):
        d = _decisao()
        del d["PAIS"]
        self._bloqueou(self._correr([d]))

    def test_fonte_europeia_nao_recebe_numero_italiano(self):
        """Territorio decidido, PAIS=EU pela prova: nada de «IT-» por omissao."""
        r = self._correr([_decisao(PAIS="EU")])
        self._bloqueou(r)
        self.assertIn("PAIS=EU", r.get("PORQUE", ""))

    def test_fonte_internacional_nao_recebe_numero_italiano(self):
        self._bloqueou(self._correr([_decisao(PAIS="INT")]))

    def test_url_de_outra_fonte(self):
        self._bloqueou(self._correr([_decisao(URL="https://outra.example/")]))

    def test_territorio_inexistente(self):
        self._bloqueou(self._correr([_decisao(TERRITORIO="T13")]))

    def test_nao_sei_registado_continua_bloqueado(self):
        self._bloqueou(self._correr([_decisao(TERRITORIO="NAO SEI",
                                              MOTIVO="prova insuficiente")]))

    def test_sem_decidido_por(self):
        self._bloqueou(self._correr([_decisao(DECIDIDO_POR="")]))

    def test_duas_decisoes_para_a_mesma_candidata(self):
        self._bloqueou(self._correr([_decisao(), _decisao(TERRITORIO="T1")]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
