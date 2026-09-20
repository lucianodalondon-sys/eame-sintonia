# -*- coding: utf-8 -*-
"""TESTE NUNCA PODE APAGAR STORAGE OPERACIONAL.

Medido em 20/09/2026: o orquestrador criava `ArmazemLocal(RAIZ)` em todos os
modos, a bancada OPERACIONAL escreveu os 107 objectos da Big Collection 2 em
`<repo>/XX/` (residuo de medicao) e o cleanup de um teste apagou-os.

O que se prova aqui:
  1. a raiz dos bytes anda com o modo de persistencia, e no modo OPERACIONAL e
     obrigatoria (falha fechado sem `SINTONIA_ARMAZEM_RAIZ`);
  2. uma raiz declarada DENTRO da arvore e recusada;
  3. a limpeza de medicao recusa fechado qualquer caminho com o marcador
     operacional, a raiz declarada, ou fora do residuo/tempdir do teste;
  4. a sentinela num armazem operacional SOBREVIVE a limpeza do residuo, e so o
     residuo morre — o mesmo gesto que apagou a BC2, agora sem dentes.

    STORAGE OPERACIONAL != RESIDUO DE MEDICAO.
"""
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
from guarda import preservar_coleta as pc  # noqa: E402
from orquestrador import persistencia  # noqa: E402


class ARaizAndaComOModo(unittest.TestCase):

    def test_operacional_sem_raiz_falha_fechado(self):
        with self.assertRaises(pc.ArmazemOperacionalSemRaiz):
            pc.raiz_do_armazem_local(persistencia.OPERACIONAL, {})

    def test_sem_memoria_a_raiz_e_a_arvore_como_sempre(self):
        self.assertEqual(pc.raiz_do_armazem_local(persistencia.AUSENTE, {}),
                         os.path.normpath(os.path.abspath(pc.RAIZ_DA_ARVORE)))

    def test_raiz_dentro_da_arvore_e_recusada_em_qualquer_modo(self):
        dentro = os.path.join(RAIZ, "data", "armazem-que-nao-pode-existir")
        for modo in (persistencia.OPERACIONAL, persistencia.DESCARTAVEL, persistencia.AUSENTE):
            with self.subTest(modo=modo):
                with self.assertRaises(pc.ArmazemOperacionalSemRaiz):
                    pc.raiz_do_armazem_local(modo, {pc.VARIAVEL_DA_RAIZ: dentro})

    def test_operacional_com_raiz_fora_da_arvore_ganha_marcador(self):
        raiz = tempfile.mkdtemp(prefix="armazem-oper-")
        self.addCleanup(shutil.rmtree, raiz, True)
        r = pc.raiz_do_armazem_local(persistencia.OPERACIONAL, {pc.VARIAVEL_DA_RAIZ: raiz})
        self.assertEqual(os.path.normpath(r), os.path.normpath(raiz))
        self.assertTrue(os.path.isfile(os.path.join(raiz, pc.MARCADOR_OPERACIONAL)))

    def test_a_persistencia_ausente_declara_a_raiz_no_recibo(self):
        rt = persistencia.dependencias_do_runtime({})
        self.assertEqual(rt.ESTADO, persistencia.AUSENTE)
        self.assertEqual(os.path.normpath(rt.raiz_do_armazem),
                         os.path.normpath(os.path.abspath(pc.RAIZ_DA_ARVORE)))
        self.assertIn("ARMAZEM_RAIZ", rt.para_json())


class ALimpezaSoApagaResiduo(unittest.TestCase):

    def setUp(self):
        self.oper = tempfile.mkdtemp(prefix="armazem-oper-")
        self.addCleanup(shutil.rmtree, self.oper, True)
        pc.marcar_operacional(self.oper)
        self.sentinela = os.path.join(self.oper, "XX", "it-teste", "DOCUMENT", "sentinela.pdf")
        os.makedirs(os.path.dirname(self.sentinela))
        with open(self.sentinela, "wb") as fh:
            fh.write(b"%PDF-1.4\nsentinela\n")

    def test_recusa_o_armazem_com_marcador(self):
        with self.assertRaises(pc.ArmazemProtegido):
            pc.apagar_armazem_de_medicao(self.oper, env={})
        with self.assertRaises(pc.ArmazemProtegido):
            pc.apagar_armazem_de_medicao(os.path.join(self.oper, "XX"), env={})
        self.assertTrue(os.path.isfile(self.sentinela))

    def test_recusa_a_raiz_declarada_mesmo_sem_marcador(self):
        outra = tempfile.mkdtemp(prefix="armazem-decl-")
        self.addCleanup(shutil.rmtree, outra, True)
        env = {pc.VARIAVEL_DA_RAIZ: outra}
        with self.assertRaises(pc.ArmazemProtegido):
            pc.apagar_armazem_de_medicao(outra, env=env)
        with self.assertRaises(pc.ArmazemProtegido):
            pc.apagar_armazem_de_medicao(os.path.join(outra, "XX"), env=env)
        self.assertTrue(os.path.isdir(outra))

    def test_recusa_qualquer_caminho_que_nao_seja_residuo_nem_tempdir(self):
        alheio = tempfile.mkdtemp(prefix="alheio-")
        self.addCleanup(shutil.rmtree, alheio, True)
        with self.assertRaises(pc.ArmazemProtegido):
            pc.apagar_armazem_de_medicao(alheio, env={})
        self.assertTrue(os.path.isdir(alheio))

    def test_apaga_o_residuo_de_uma_arvore_falsa_e_a_sentinela_sobrevive(self):
        arvore = tempfile.mkdtemp(prefix="arvore-falsa-")
        self.addCleanup(shutil.rmtree, arvore, True)
        residuo = os.path.join(arvore, "XX")
        os.makedirs(os.path.join(residuo, "it-teste"))
        with open(os.path.join(residuo, "it-teste", "residuo.bin"), "wb") as fh:
            fh.write(b"residuo")
        env = {pc.VARIAVEL_DA_RAIZ: self.oper}
        self.assertTrue(pc.apagar_armazem_de_medicao(residuo, env=env, raiz_da_arvore=arvore))
        self.assertFalse(os.path.exists(residuo), "o residuo devia ter morrido")
        self.assertTrue(os.path.isfile(self.sentinela), "a sentinela operacional morreu")
        self.assertFalse(pc.apagar_armazem_de_medicao(residuo, env=env, raiz_da_arvore=arvore),
                         "apagar o que nao existe devolve False, nao erro")

    def test_apaga_dentro_da_pasta_temporaria_do_proprio_teste(self):
        tmp = tempfile.mkdtemp(prefix="do-teste-")
        self.addCleanup(shutil.rmtree, tmp, True)
        alvo = os.path.join(tmp, "armazem")
        os.makedirs(os.path.join(alvo, "XX"))
        self.assertTrue(pc.apagar_armazem_de_medicao(alvo, env={}, dentro_de=tmp))
        self.assertFalse(os.path.exists(alvo))

    def test_o_gesto_que_apagou_a_bc2_ja_nao_chega_ao_operacional(self):
        """`rmtree(RAIZ/"XX")` era o gesto. Hoje o residuo da arvore e uma
        pasta e o operacional e outra, fora da arvore e com marcador — e a
        limpeza canonica nunca sai do residuo."""
        env = {pc.VARIAVEL_DA_RAIZ: self.oper}
        raiz_oper = pc.raiz_do_armazem_local(persistencia.OPERACIONAL, env)
        residuo = os.path.normpath(os.path.join(pc.RAIZ_DA_ARVORE, "XX"))
        self.assertNotEqual(os.path.normpath(raiz_oper), residuo)
        self.assertFalse(os.path.normpath(raiz_oper).startswith(residuo + os.sep))
        with self.assertRaises(pc.ArmazemProtegido):
            pc.apagar_armazem_de_medicao(raiz_oper, env=env)
        self.assertTrue(os.path.isfile(self.sentinela))


if __name__ == "__main__":
    unittest.main()
