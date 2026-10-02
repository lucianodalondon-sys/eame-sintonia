# -*- coding: utf-8 -*-
"""CODIGO.json da rodada automatica traz a prova do TEXTO LIMPO (pedido do coordenador 02/10 12:0x).

O DONE do dono exige texto limpo; o hash do que o modelo viu (TEXTO_ENTREGUE_SHA256) e gravado pelo passo2 em
FACTS_FAST.DOCUMENTOS. O runner passa a copia-lo para CODIGO.json, por documento, e a dizer se TODOS os documentos o
tem — sem ele, TEXTO_LIMPO_PROVADO = False (nunca verde por omissao).
"""
import importlib.util
import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("rodada_fast", os.path.join(RAIZ, "motor", "fast_auto", "rodada_fast.py"))
RF = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RF)

H = "a" * 64


class TextoEntregueNoCodigo(unittest.TestCase):
    def test_todos_com_hash_prova_o_texto(self):
        F = {"DOCUMENTOS": [
            {"DOCUMENT_ID": "d1", "ESTADO": "PROCESSADO", "TEXTO_ENTREGUE_SHA256": H, "TEXTO_ENTREGUE_CHARS": 10,
             "TEXTO_ARQUIVO_SHA256": H, "CONFERE_COM_DOCUMENTOS": True},
            {"DOCUMENT_ID": "d2", "ESTADO": "PROCESSADO", "TEXTO_ENTREGUE_SHA256": "b" * 64, "TEXTO_ENTREGUE_CHARS": 5,
             "TEXTO_ARQUIVO_SHA256": "b" * 64, "CONFERE_COM_DOCUMENTOS": True}]}
        t = RF.texto_entregue(F)
        self.assertTrue(t["TEXTO_LIMPO_PROVADO"])
        self.assertEqual(t["TEXTO_ENTREGUE_SHA256"], {"d1": H, "d2": "b" * 64})
        self.assertEqual(t["DOCUMENTOS_SEM_HASH"], [])
        self.assertEqual(t["TEXTO_ENTREGUE_CHARS"], 15)

    def test_codigo_antigo_sem_hash_nao_prova(self):
        F = {"DOCUMENTOS": [{"DOCUMENT_ID": "d1", "ESTADO": "PROCESSADO", "TEXTO_CORTADO_EM": None}]}
        t = RF.texto_entregue(F)
        self.assertFalse(t["TEXTO_LIMPO_PROVADO"])
        self.assertEqual(t["DOCUMENTOS_SEM_HASH"], ["d1"])

    def test_um_documento_sem_hash_derruba_a_prova(self):
        F = {"DOCUMENTOS": [
            {"DOCUMENT_ID": "d1", "TEXTO_ENTREGUE_SHA256": H, "CONFERE_COM_DOCUMENTOS": True},
            {"DOCUMENT_ID": "d2", "ESTADO": "ERRO_LLM"}]}
        t = RF.texto_entregue(F)
        self.assertFalse(t["TEXTO_LIMPO_PROVADO"])
        self.assertEqual(t["DOCUMENTOS_SEM_HASH"], ["d2"])

    def test_arquivo_que_nao_confere_derruba_a_prova(self):
        F = {"DOCUMENTOS": [{"DOCUMENT_ID": "d1", "TEXTO_ENTREGUE_SHA256": H, "CONFERE_COM_DOCUMENTOS": False}]}
        t = RF.texto_entregue(F)
        self.assertFalse(t["TEXTO_LIMPO_PROVADO"])
        self.assertEqual(t["DOCUMENTOS_QUE_NAO_CONFEREM"], ["d1"])

    def test_vazio_nao_prova(self):
        self.assertFalse(RF.texto_entregue({"DOCUMENTOS": []})["TEXTO_LIMPO_PROVADO"])


if __name__ == "__main__":
    unittest.main()
