#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D79 · o decisor de versões, sem banco. Cada saída de `versao_do_documento.decidir`."""
import hashlib
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "admissao"))

import versao_do_documento as v          # noqa: E402

R1 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
R2 = "477d63427363" + "0" * 52


def d(id_, pai, sha, receita=R1, producer="texto-de-html", versao="1"):
    return {"id": id_, "producer": producer, "producer_version": versao,
            "parameters_hash": receita, "sha256": sha, "parent_sha256": pai,
            "storage_path_raw": "raw/%s" % id_, "media_type_raw": "text/html"}


class Armazem(object):
    def __init__(self, dados=b"<html>x</html>", erro=None):
        self.dados, self.erro = dados, erro

    def ler(self, caminho):
        if self.erro:
            raise self.erro
        return self.dados


def extrator(texto, versao="1", receita=R2):
    return {"texto-de-html": lambda dados, mt: (texto, versao, receita)}


class ODecisor(unittest.TestCase):

    def test_falta_um_derivado_e_nao_sei(self):
        self.assertEqual(v.decidir(None, d(2, "b", "y"))["ESTADO"], v.NAO_SEI)

    def test_bytes_iguais_e_igual(self):
        self.assertEqual(v.decidir(d(1, "a", "x"), d(2, "a", "y"))["ESTADO"], v.IGUAL)

    def test_mesmo_extrator_texto_igual_e_igual(self):
        r = v.decidir(d(1, "a", "x"), d(2, "b", "x"))
        self.assertEqual((r["ESTADO"], r["COMO"]), (v.IGUAL, v.MESMO_EXTRATOR))

    def test_mesmo_extrator_texto_diferente_e_versao(self):
        r = v.decidir(d(1, "a", "x"), d(2, "b", "y"))
        self.assertEqual((r["ESTADO"], r["COMO"]), (v.MUDOU, v.MESMO_EXTRATOR))

    def test_receita_diferente_com_a_mesma_versao_nao_e_mesmo_extrator(self):
        """O caso IT-T9-011: versao 1 nos dois, parametros diferentes."""
        r = v.decidir(d(1, "a", "x"), d(2, "b", "y", receita=R2))
        self.assertEqual(r["ESTADO"], v.NAO_SEI)

    def test_sem_armazem_e_nao_sei(self):
        r = v.decidir(d(1, "a", "x"), d(2, "b", "y", receita=R2), extratores=extrator("t"))
        self.assertEqual(r["ESTADO"], v.NAO_SEI)

    def test_raw_ilegivel_e_nao_sei(self):
        r = v.decidir(d(1, "a", "x"), d(2, "b", "y", receita=R2),
                      armazem=Armazem(erro=OSError("nao preservado")), extratores=extrator("t"))
        self.assertEqual(r["ESTADO"], v.NAO_SEI)

    def test_extrator_disponivel_nao_e_o_do_derivado_novo_e_nao_sei(self):
        r = v.decidir(d(1, "a", "x"), d(2, "b", "y", receita=R2),
                      armazem=Armazem(), extratores=extrator("t", receita=R1))
        self.assertEqual(r["ESTADO"], v.NAO_SEI)

    def test_reextraido_igual_e_igual(self):
        sha = hashlib.sha256("velho".encode("utf-8")).hexdigest()
        r = v.decidir(d(1, "a", "x"), d(2, "b", sha, receita=R2),
                      armazem=Armazem(), extratores=extrator("velho"))
        self.assertEqual((r["ESTADO"], r["COMO"]), (v.IGUAL, v.REEXTRAIDO_DO_RAW))

    def test_reextraido_diferente_e_versao(self):
        r = v.decidir(d(1, "a", "x"), d(2, "b", "f" * 64, receita=R2),
                      armazem=Armazem(), extratores=extrator("velho"))
        self.assertEqual((r["ESTADO"], r["COMO"]), (v.MUDOU, v.REEXTRAIDO_DO_RAW))

    def test_id_do_derivado(self):
        self.assertEqual(v._derivado_id("derived:66"), 66)
        self.assertIsNone(v._derivado_id("inventado"))
        self.assertIsNone(v._derivado_id("derived:x"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
