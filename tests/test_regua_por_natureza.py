#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ROTEAR PRIMEIRO, JULGAR DEPOIS — a regua de CONHECIMENTO no C8 (dono, Diretoria 01/10/2026).

Auditoria cega do LAB (ROTULOS-CEGOS-V1 e518cfce): 107 materiais uteis perdidos porque a regua de FATO de campo
(C1 afirmacao propria, C2 data do fato, C3 lugar do fato) era exigida a estudos publicados.
Estes testes fixam:
  * C1..C7 NAO afrouxam: um objeto que nao e CONHECIMENTO declarado pelo motor continua na regua de FATO;
  * conhecimento so passa com prova do DOCUMENTO: byte relido = Sala, DOCUMENT_ID = identidade de obra (DOI/OpenAlex),
    tipo de obra DECLARADO pela fonte no registo (editorial/pagina institucional nao passam), titulo literal no texto;
  * conhecimento nunca vira alerta: USO_EXIGE_TEMPO=false, RESULTADO=NO_DEFENSIBLE_ACTION_YET, FACT_TIME vazio;
  * a mesma obra nao e liberada duas vezes (INT-LAW-072).
Texto e registos SINTETICOS.
"""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "pacote"))
sys.path.insert(0, str(RAIZ))
import liberacao_por_criterio as L  # noqa: E402

TITULO = "Sintetico: um fungo sintetico contra uma praga sintetica"
TEXTO = TITULO + ". Resumo sintetico de um estudo em laboratorio, sem data nem lugar de campo."


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.armazem = Path(self.tmp.name)
        self.linhas = {}
        self.o = self.obra("10.9999/sint.1", "article")
        self._lig = L.PORTA.conferir_ligacao
        L.PORTA.conferir_ligacao = lambda lig: []

    def tearDown(self):
        L.PORTA.conferir_ligacao = self._lig
        self.tmp.cleanup()

    def obra(self, doc, tipo, item="SINT-1", titulo=TITULO, texto=TEXTO, aplic="PARCIAL"):
        raw = json.dumps({"title": titulo, "type": tipo}).encode("utf-8")
        nome = hashlib.sha256(raw).hexdigest()[:12] + ".json"
        (self.armazem / nome).write_bytes(raw)
        self.linhas[item] = {"texto": texto, "raw_sha256": hashlib.sha256(raw).hexdigest(),
                             "raw_storage_path": nome, "raw_document_key": doc}
        return {
            "OBJETO_ID": "SINT-O-" + item, "ESPECIE": "SINAL", "ESPECIE_DITA_POR": "INTELLIGENCE",
            "USO_EXIGE_TEMPO": False, "RESULTADO": "NO_DEFENSIBLE_ACTION_YET", "LIGACAO_ADAMA": {},
            "PROVA": [{"ITEM_ID": item, "DOCUMENT_ID": doc, "G0": "BLOQUEADO_EM_G0", "ADMITIDA_POR": "USO_SEM_TEMPO",
                       "FACT_TIME": "NAO SEI", "RAW_SHA256": self.linhas[item]["raw_sha256"],
                       "RAW_STORAGE_PATH": nome}],
            "FORA_DO_CONTRATO": {"ESPECIE_DO_MOTOR": "CONHECIMENTO/ESTUDO (uso sem tempo, P7)",
                                 "INTERPRETACAO_DO_SISTEMA": {"USO": {"G0_FALTA": ["FACT_TIME"]},
                                                              "APLICABILIDADE": {"ESTADO": aplic}}}}

    def conferir(self, o, comp="science", vistos=None):
        return L.conferir_por_natureza(o, comp, self.linhas, self.armazem, set() if vistos is None else vistos, {})

    def liberar(self, *objs):
        pote = {"COMPARTIMENTOS": {"science": {"OBJETOS": list(objs)}}}
        return L.liberar(pote, self.linhas, self.armazem, "IR-SINT")[0]["COMPARTIMENTOS"]["science"]["OBJETOS"]


class Rota(Base):
    def test_estudo_declarado_pelo_motor_vai_a_regua_de_conhecimento(self):
        self.assertEqual(L.natureza_do_objeto(self.o, "science"), "CONHECIMENTO")

    def test_fora_de_science_continua_regua_de_fato(self):
        self.assertEqual(L.natureza_do_objeto(self.o, "archive"), "FATO")

    def test_motor_nao_disse_conhecimento_continua_regua_de_fato(self):
        o = copy.deepcopy(self.o)
        o["FORA_DO_CONTRATO"]["ESPECIE_DO_MOTOR"] = "ANALYTIC_JUDGMENT/ESTUDO"
        self.assertEqual(L.natureza_do_objeto(o, "science"), "FATO")

    def test_uso_que_exige_tempo_continua_regua_de_fato(self):
        o = copy.deepcopy(self.o)
        o["USO_EXIGE_TEMPO"] = True
        self.assertEqual(L.natureza_do_objeto(o, "science"), "FATO")

    def test_g0_bloqueado_por_mais_que_o_tempo_continua_regua_de_fato(self):
        o = copy.deepcopy(self.o)
        o["FORA_DO_CONTRATO"]["INTERPRETACAO_DO_SISTEMA"]["USO"]["G0_FALTA"] = ["FACT_TIME", "SEM_ANO"]
        self.assertEqual(L.natureza_do_objeto(o, "science"), "FATO")

    def test_regua_de_fato_nao_afrouxou_para_quem_nao_e_conhecimento(self):
        o = copy.deepcopy(self.o)
        o["FORA_DO_CONTRATO"]["ESPECIE_DO_MOTOR"] = "SINAL"
        c = self.conferir(o)
        self.assertEqual(c["REGUA"], L.REGUA_FATO)
        self.assertTrue(c["C2_DATA_PROPRIA"].startswith("FALHOU"))
        self.assertTrue(c["C8_DECISAO_DO_DONO"].startswith("FALHOU"))


class ReguaDeConhecimento(Base):
    def test_artigo_com_doi_tipo_declarado_e_titulo_literal_passa(self):
        c = self.conferir(self.o)
        self.assertEqual(c["REGUA"], L.REGUA_CONHECIMENTO)
        self.assertTrue(c["C8_DECISAO_DO_DONO"].startswith(L.PASSOU), c)

    def test_editorial_nao_passa(self):
        c = self.conferir(self.obra("10.9999/sint.2", "editorial", item="SINT-2"))
        self.assertIn("editorial", c["K2_OBRA_CIENTIFICA_DECLARADA_PELA_FONTE"])
        self.assertTrue(c["C8_DECISAO_DO_DONO"].startswith("FALHOU"))

    def test_pagina_institucional_sem_identidade_de_obra_nao_passa(self):
        c = self.conferir(self.obra("SRC:URL:noticia-sintetica", "article", item="SINT-3"))
        self.assertTrue(c["K2_OBRA_CIENTIFICA_DECLARADA_PELA_FONTE"].startswith("FALHOU"))
        self.assertTrue(c["C8_DECISAO_DO_DONO"].startswith("FALHOU"))

    def test_registo_sem_tipo_nao_passa(self):
        c = self.conferir(self.obra("10.9999/sint.4", None, item="SINT-4"))
        self.assertTrue(c["K2_OBRA_CIENTIFICA_DECLARADA_PELA_FONTE"].startswith("FALHOU"))

    def test_titulo_que_nao_esta_no_texto_nao_passa(self):
        c = self.conferir(self.obra("10.9999/sint.5", "article", item="SINT-5", texto="outro texto qualquer"))
        self.assertIn("titulo da obra nao esta literal", c["K1_PROVA_DO_DOCUMENTO"])

    def test_byte_alterado_no_armazem_nao_passa(self):
        (self.armazem / self.linhas["SINT-1"]["raw_storage_path"]).write_bytes(b'{"title": "x", "type": "article"}')
        c = self.conferir(self.o)
        self.assertIn("sha do byte relido", c["K1_PROVA_DO_DOCUMENTO"])

    def test_document_id_diferente_da_sala_nao_passa(self):
        o = copy.deepcopy(self.o)
        o["PROVA"][0]["DOCUMENT_ID"] = "10.9999/outra"
        self.assertIn("DOCUMENT_ID", self.conferir(o)["K1_PROVA_DO_DOCUMENTO"])

    def test_conhecimento_com_fact_time_preenchido_nao_passa_por_esta_regua(self):
        o = copy.deepcopy(self.o)
        o["PROVA"][0]["FACT_TIME"] = "2031-01-01"
        self.assertTrue(self.conferir(o)["K3_SEM_USO_QUE_EXIGE_TEMPO"].startswith("FALHOU"))

    def test_prova_nao_admitida_sem_tempo_nao_passa(self):
        o = copy.deepcopy(self.o)
        o["PROVA"][0]["ADMITIDA_POR"] = "G0_PASSOU"
        self.assertTrue(self.conferir(o)["K3_SEM_USO_QUE_EXIGE_TEMPO"].startswith("FALHOU"))

    def test_mesma_obra_duas_vezes_so_libera_uma(self):
        o2 = copy.deepcopy(self.o)
        o2["OBJETO_ID"] = "SINT-O-dup"
        a, b = self.liberar(self.o, o2)
        self.assertEqual(a["LIBERACAO"], "LIBERADO_PARA_CLIENTE")
        self.assertEqual(b["LIBERACAO"], "NAO_PARA_CLIENTE")
        self.assertIn("INT-LAW-072", b["CONFERENCIA_DE_LIBERACAO"]["K5_SEM_OBRA_DUPLICADA"])

    def test_liberado_cita_a_obra_literal_com_posicao_e_nada_de_data_ou_lugar(self):
        o = self.liberar(self.o)[0]
        p = o["PROVA"][0]
        self.assertEqual(o["NATUREZA_DO_OBJETO"], "CONHECIMENTO")
        self.assertEqual(TEXTO[p["SECAO"]["AFIRMACAO_EM"]:][:len(p["TRECHO_DA_AFIRMACAO"])], p["TRECHO_DA_AFIRMACAO"])
        self.assertNotIn("TRECHO_DA_DATA", p)
        self.assertNotIn("TRECHO_DO_LUGAR", p)
        self.assertEqual(o["RESULTADO"], "NO_DEFENSIBLE_ACTION_YET")
        self.assertIs(o["USO_EXIGE_TEMPO"], False)


class CapSciRotaDeDestino(Base):
    """P1/1B (dono 01/10, PASSO 1 CAP-SCI): a CAP-SCI decide o DESTINO de uma obra provada — cliente so com tema
    provado; tema nao provado ou obra secundaria declarada (editorial) = PRESERVADO_EM_SCIENCE, nunca cliente;
    sem identidade de obra (pagina institucional) continua BLOQUEADO."""

    def test_tema_nao_provado_nao_vai_ao_cliente(self):
        c = self.conferir(self.obra("10.9999/sint.10", "article", item="SINT-10", aplic="TEMA_NAO_PROVADO"))
        self.assertTrue(c["K8_TEMA_PROVADO_CAP_SCI"].startswith("FALHOU"))
        self.assertTrue(c["C8_DECISAO_DO_DONO"].startswith("FALHOU"))
        self.assertEqual(c["DESTINO"], L.DESTINO_PRESERVADO)

    def test_aplicabilidade_ausente_e_nao_sei_nao_cliente(self):
        o = self.obra("10.9999/sint.11", "article", item="SINT-11")
        del o["FORA_DO_CONTRATO"]["INTERPRETACAO_DO_SISTEMA"]["APLICABILIDADE"]
        c = self.conferir(o)
        self.assertIn("NAO SEI", c["K8_TEMA_PROVADO_CAP_SCI"])
        self.assertNotEqual(c["DESTINO"], L.DESTINO_CLIENTE)

    def test_tema_provado_continua_a_ir_ao_cliente(self):
        c = self.conferir(self.obra("10.9999/sint.12", "article", item="SINT-12", aplic="COMPLETA"))
        self.assertEqual(c["DESTINO"], L.DESTINO_CLIENTE)
        self.assertTrue(c["C8_DECISAO_DO_DONO"].startswith(L.PASSOU))

    def test_editorial_e_preservado_nao_cliente(self):
        c = self.conferir(self.obra("10.9999/sint.13", "editorial", item="SINT-13"))
        self.assertTrue(c["C8_DECISAO_DO_DONO"].startswith("FALHOU"))
        self.assertEqual(c["DESTINO"], L.DESTINO_PRESERVADO)

    def test_tipo_desconhecido_continua_bloqueado(self):
        c = self.conferir(self.obra("10.9999/sint.14", "erratum", item="SINT-14"))
        self.assertEqual(c["DESTINO"], L.DESTINO_BLOQUEADO)

    def test_pagina_institucional_continua_bloqueada(self):
        c = self.conferir(self.obra("SRC:URL:noticia-sintetica-2", "article", item="SINT-15"))
        self.assertEqual(c["DESTINO"], L.DESTINO_BLOQUEADO)

    def test_titulo_fora_do_texto_nao_e_preservado(self):
        c = self.conferir(self.obra("10.9999/sint.16", "article", item="SINT-16", texto="outro",
                                    aplic="TEMA_NAO_PROVADO"))
        self.assertEqual(c["DESTINO"], L.DESTINO_BLOQUEADO)

    def test_preservado_fica_no_pote_experimental_nao_para_cliente_com_titulo_literal(self):
        o = self.liberar(self.obra("10.9999/sint.17", "article", item="SINT-17", aplic="TEMA_NAO_PROVADO"))[0]
        self.assertEqual(o["LIBERACAO"], "NAO_PARA_CLIENTE")
        self.assertEqual(o["DESTINO_DO_OBJETO"], L.DESTINO_PRESERVADO)
        p = o["PROVA"][0]
        self.assertEqual(TEXTO[p["SECAO"]["AFIRMACAO_EM"]:][:len(p["TRECHO_DA_AFIRMACAO"])], p["TRECHO_DA_AFIRMACAO"])
        self.assertNotIn("TRECHO_DA_DATA", p)
        self.assertEqual(L.so_liberados({"COMPARTIMENTOS": {"science": {"OBJETOS": [o]}}})["OBJETOS_LIBERADOS"], 0)

    def test_mesma_obra_preservada_nao_conta_duas_vezes(self):
        a = self.obra("10.9999/sint.18", "article", item="SINT-18", aplic="TEMA_NAO_PROVADO")
        b = copy.deepcopy(a)
        b["OBJETO_ID"] = "SINT-O-dup18"
        x, y = self.liberar(a, b)
        self.assertEqual(x["DESTINO_DO_OBJETO"], L.DESTINO_PRESERVADO)
        self.assertNotIn("DESTINO_DO_OBJETO", y)
        self.assertEqual(y["CONFERENCIA_DE_LIBERACAO"]["DESTINO"], L.DESTINO_BLOQUEADO)


if __name__ == "__main__":
    unittest.main()
