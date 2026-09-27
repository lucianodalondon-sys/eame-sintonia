#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A ARESTA DA ROTA DA M2 — declarada nao e observada.

    DECLARED EDGE  !=  OBSERVED EDGE.

A M2 ligou `DERIVED -> STRUCTURED -> ADMISSION` e provou as duas etapas novas
contra Postgres real. O portao passou a exigir que A MESMA rota carregue as
tres etapas — e isso e necessario e nao chega:

    TRES ETAPAS NA MESMA ROTA PODEM SER TRES ACONTECIMENTOS SOLTOS.

Medido, e nao suposto: na corrida que provava a rota, o banco tinha
`STRUCTURED edge_from=DERIVED PASS` e **nenhuma passagem de `DERIVED`** — a
etapa de cima correra noutra corrida, noutro ficheiro. A seta estava desenhada
e o caminho nao tinha sido percorrido.

⚠️ O QUE ESTE FICHEIRO NAO REPETE.
Duas sessoes trabalham nesta branch. O preflight (P1..P5), as duas etapas da
M2, os tres caminhos de falha e a prova negativa de READY ja tem provas
proprias em `tests/test_m2_rota_forward.py` e
`tests/test_o10r_a_verdade_dos_nomes.py`. Repetir aqui seria uma segunda
verdade sobre a mesma pergunta. O que fica e o que so existe deste lado: a
ARESTA medida no banco, e a trava que impede uma mutacao de escrever no
artefato.
"""
import json
import os
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "system-map", "scripts"))
import _gavetas  # noqa: E402,F401
import censo_dos_executores as censo   # noqa: E402
import rastro_da_coleta as rastro      # noqa: E402

ROTA = ("IT-T2-002", "RC-1")
LEDGER = os.path.join(RAIZ, "system-map", "data", "provas-de-execucao.json")


def _p(etapa, estado="PASS", de=None, rota=ROTA):
    return {"ETAPA": etapa, "ESTADO": estado, "EDGE_FROM": de,
            "SOURCE_ID": rota[0], "ROUTE_CLASS_ID": rota[1]}


class OLeitorDevolveARota(unittest.TestCase):
    """Sem a rota de volta, «de que rota e esta passagem?» nao tem resposta."""

    def test_o_select_pede_as_duas_colunas(self):
        class Banco:
            def executa(self, sql):
                self.sql = sql
                return []
        b = Banco()
        rastro.passagens(b, run_id="R")
        self.assertIn("source_id", b.sql)
        self.assertIn("route_class_id", b.sql)

    def test_a_identidade_e_o_par_e_nao_um_id_novo(self):
        self.assertEqual(ROTA, rastro.identidade_da_rota(_p("DERIVED")))

    def test_uma_passagem_anonima_nao_pertence_a_rota_nenhuma(self):
        """UM ID INVENTADO E PIOR DO QUE UNKNOWN — e um ausente tambem nao se
        preenche com o da rota que da jeito."""
        for meia in ({"SOURCE_ID": "IT-T2-002", "ROUTE_CLASS_ID": None},
                     {"SOURCE_ID": None, "ROUTE_CLASS_ID": "RC-1"},
                     {"SOURCE_ID": None, "ROUTE_CLASS_ID": None}):
            self.assertIsNone(rastro.identidade_da_rota(dict(_p("DERIVED"), **meia)))


class AArestaSoContaComOsDoisTopos(unittest.TestCase):
    """UMA SETA DESENHADA NAO E UM CAMINHO PERCORRIDO."""

    COMPLETA = [_p("DERIVED", de="RAW"),
                _p("STRUCTURED", de="DERIVED"),
                _p("ADMISSION", de="STRUCTURED")]

    def test_a_cadeia_inteira_da_as_duas_arestas(self):
        visto = rastro.o_que_a_rota_observou(self.COMPLETA, ROTA)
        self.assertEqual({"DERIVED", "STRUCTURED", "ADMISSION"}, visto["ETAPAS"])
        self.assertIn(("DERIVED", "STRUCTURED"), visto["ARESTAS"])
        self.assertIn(("STRUCTURED", "ADMISSION"), visto["ARESTAS"])

    def test_MUTACAO_sem_a_passagem_de_cima_a_aresta_deixa_de_contar(self):
        """Este era o estado real do banco antes desta missao."""
        sem = [p for p in self.COMPLETA if p["ETAPA"] != "DERIVED"]
        visto = rastro.o_que_a_rota_observou(sem, ROTA)
        self.assertNotIn(("DERIVED", "STRUCTURED"), visto["ARESTAS"])
        self.assertIn(("DERIVED", "STRUCTURED"),
                      visto["ARESTAS_DECLARADAS_SEM_TOPO"])

    def test_o_que_ficou_so_declarado_aparece_e_nao_desaparece(self):
        """Um buraco que some da medicao volta como surpresa.

        ⚠️ O SUJEITO MUDOU, E A LEI NAO. Ate C-MAKE-RAW-OBSERVABLE-V1 este
        teste usava `self.COMPLETA` — onde RAW nao tinha linha — para provar
        que a aresta `RAW -> DERIVED` aparecia como declarada e sem topo. A
        etapa RAW passou a falar, e essa aresta deixou de estar sem topo.

        O que este teste guarda continua a ser o mesmo: o medidor tem de
        MOSTRAR a aresta cujo topo falta, em vez de a calar. Entao ele passa a
        perguntar-lho sobre uma passagem que REALMENTE falta.
        """
        sem_raw = [p for p in self.COMPLETA if p["ETAPA"] != "DERIVED"]
        visto = rastro.o_que_a_rota_observou(sem_raw, ROTA)
        self.assertIn(("DERIVED", "STRUCTURED"),
                      visto["ARESTAS_DECLARADAS_SEM_TOPO"],
                      "uma aresta sem topo deixou de ser visivel na medicao")

    def test_MUTACAO_uma_etapa_que_nao_correu_nao_cobre_nem_liga(self):
        """NOT_RUN deixa linha e nao e passagem. Se contasse, bastava uma linha
        vazia para uma rota parecer coberta."""
        for morto in ("NOT_RUN", "SKIPPED", "NOT_APPLICABLE", "FAIL"):
            with self.subTest(estado=morto):
                mutada = [dict(p, ESTADO=morto) if p["ETAPA"] == "STRUCTURED"
                          else p for p in self.COMPLETA]
                visto = rastro.o_que_a_rota_observou(mutada, ROTA)
                self.assertNotIn("STRUCTURED", visto["ETAPAS"])
                self.assertNotIn(("STRUCTURED", "ADMISSION"), visto["ARESTAS"])

    def test_MUTACAO_a_rota_nao_absorve_passagem_de_outra(self):
        outra = [dict(p, SOURCE_ID="OUTRA-FONTE") for p in self.COMPLETA]
        self.assertEqual(set(),
                         rastro.o_que_a_rota_observou(outra, ROTA)["ETAPAS"])


class OPortaoExigeAsArestas(unittest.TestCase):
    """O portao le o ledger; o ledger le o banco. E so o banco e prova."""

    ROTA_M2 = {"CAMINHO": "coleta/rota_forward_documento.py",
               "FRONTEIRA": "coleta/rota_forward_documento.py",
               "SOURCE_ID": "IT-T2-002", "ROUTE_CLASS_ID": "RC-1",
               "ETAPAS_OBSERVADAS": ["ADMISSION", "DERIVED", "STRUCTURED"],
               "ARESTAS_OBSERVADAS": [["DERIVED", "STRUCTURED"],
                                      ["STRUCTURED", "ADMISSION"]],
               # ⚠️ E A DECLARACAO DE QUE FOI UMA VIAGEM SO.
               # Uma segunda sessao chegou ao mesmo defeito por outro lado e
               # trouxe `END_TO_END`: as arestas recusam a seta desenhada, e
               # esta recusa a composicao de duas provas compativeis. As duas
               # exigencias ficam, e por isso a fixture declara as duas.
               "END_TO_END": True,
               "RUN_UNICO": "RUN-M2-E2E",
               "PROVA": "provas/a_rota_m2_atravessa.py"}

    def _gate(self, forward):
        """O gate DE VERDADE, sobre um ledger de mentira escrito em disco.

        ⚠️ NAO SE SUBSTITUI A FUNCAO QUE LE — substitui-se o FICHEIRO. Trocar a
        funcao saltaria por cima da propria guarda que estas mutacoes existem
        para testar, e o teste passaria a provar o atalho.
        """
        real = censo.PROVAS
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as f:
            json.dump({"SCHEMA": "provas-de-execucao/v1",
                       "PROVADOS": {"x": {"FORWARD_INSTRUMENTED": True,
                                          "GOOD_PATH_PROVED": True,
                                          "FAULT_PATH_PROVED": True,
                                          "FORWARD": forward}}}, f,
                      ensure_ascii=False)
            temporario = f.name
        censo.PROVAS = temporario
        try:
            return censo.medir_tudo()["M2"]["M2_ROUTE"]
        finally:
            censo.PROVAS = real
            os.unlink(temporario)

    def test_com_as_tres_etapas_e_as_duas_arestas_o_portao_abre(self):
        """A lei tem de NAO morder a esmo: ruido ensina a ignorar o alarme."""
        r = self._gate(self.ROTA_M2)
        self.assertEqual("YES", r["M2_ROUTE_OBSERVABILITY_READY"])
        self.assertEqual([], r["ARESTAS_DA_ROTA_M2_NUNCA_OBSERVADAS"])

    def test_MUTACAO_as_tres_etapas_SEM_as_arestas_nao_abrem(self):
        """TRES ETAPAS SOLTAS NAO SAO UMA ROTA."""
        r = self._gate(dict(self.ROTA_M2, ARESTAS_OBSERVADAS=[]))
        self.assertEqual("NO", r["M2_ROUTE_OBSERVABILITY_READY"])
        self.assertEqual([["DERIVED", "STRUCTURED"], ["STRUCTURED", "ADMISSION"]],
                         r["ARESTAS_DA_ROTA_M2_NUNCA_OBSERVADAS"])

    def test_MUTACAO_meia_cadeia_nao_abre(self):
        r = self._gate(dict(self.ROTA_M2,
                            ARESTAS_OBSERVADAS=[["DERIVED", "STRUCTURED"]]))
        self.assertEqual("NO", r["M2_ROUTE_OBSERVABILITY_READY"])


    def test_MUTACAO_E2E_as_arestas_sem_uma_viagem_so_nao_abrem(self):
        """SAME ROUTE CLASS != SAME EXECUTION FLOW.

        As tres etapas e as duas arestas, mas compostas de duas provas: o
        portao continua fechado, e diz porque.
        """
        r = self._gate(dict(self.ROTA_M2, END_TO_END=False))
        self.assertEqual("NO", r["M2_ROUTE_OBSERVABILITY_READY"])
        self.assertTrue(r.get("FALTA_E2E"))
        self.assertIn("unica execucao", r["PORQUE_NAO"])

    def test_o_portao_diz_de_que_rota_fala_e_aponta_a_prova(self):
        r = self._gate(self.ROTA_M2)
        self.assertEqual("IT-T2-002", r["ROTA_MEDIDA"]["SOURCE_ID"])
        self.assertTrue(os.path.exists(
            os.path.join(RAIZ, r["ROTA_MEDIDA"]["PROVA"])))

    def test_o_ledger_publicado_declara_as_arestas_da_rota(self):
        with open(LEDGER, encoding="utf-8") as f:
            d = json.load(f)
        fw = d["PROVADOS"]["coleta/rota_forward_documento.py"]["FORWARD"]
        self.assertEqual([["DERIVED", "STRUCTURED"], ["STRUCTURED", "ADMISSION"]],
                         fw["ARESTAS_OBSERVADAS"])
        self.assertTrue(os.path.exists(
            os.path.join(RAIZ, fw["PROVA_DA_ROTA_NUMA_CORRIDA_SO"])))


class UmaMutacaoNaoEscreveNoArtefato(unittest.TestCase):
    """UM TESTE QUE PERSISTE A PROPRIA MENTIRA DEIXA-A LA DEPOIS DE ACABAR."""

    def test_medir_nao_toca_no_disco(self):
        """⚠️ ISTO ACONTECEU, E FOI APANHADO A MAO.

        Enquanto o censo tinha UMA funcao que media e escrevia, a mutacao da
        paridade correu com o veredito trocado e gravou `PARIDADE: UNKNOWN`
        dentro de `executores.generated.json`. O artefato commitado passou a
        dizer que a prova nao tinha corrido, por causa de um teste.
        """
        alvo = os.path.join(RAIZ, "system-map", "data",
                            "executores.generated.json")
        with open(alvo, encoding="utf-8") as f:
            antes = f.read()
        real = censo.PROVAS
        censo.PROVAS = os.path.join(RAIZ, "nao-existe-de-proposito.json")
        try:
            censo.medir_tudo()
        finally:
            censo.PROVAS = real
        with open(alvo, encoding="utf-8") as f:
            self.assertEqual(antes, f.read(),
                             "medir_tudo() escreveu: uma mutacao consegue "
                             "deixar a mentira commitada")


if __name__ == "__main__":
    unittest.main()
