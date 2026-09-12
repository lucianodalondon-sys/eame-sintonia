#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS DOIS EIXOS NAO SE INFEREM UM DO OUTRO.

Um censo que transforma `PARTIAL` em blocker produz uma fila de missoes que
trabalha no que e facil de medir, e nao no que esta a travar.
"""
import importlib.util
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

_spec = importlib.util.spec_from_file_location(
    "portoes_t", os.path.join(RAIZ, "provas", "os_portoes_da_collection.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

_C = {}


def _art():
    """SEMPRE recomputado. Ler o JSON ja deixou seis mutantes vivos (§61)."""
    if "a" not in _C:
        _C["a"] = P.medir()
    return _C["a"]


class OsDoisEixosFicamSeparados(unittest.TestCase):

    def test_partial_nao_vira_blocker_automaticamente(self):
        a = _art()
        partial = a["IMPLEMENTATION_STATE"]["CENSO"].get("PARTIAL", 0)
        self.assertGreater(partial, 0, "o censo declarado ficou vazio")
        self.assertLess(len(a["BLOCKERS"]), partial,
                        "ha tantos blockers quanto leis PARTIAL: os eixos "
                        "colaram-se um ao outro")

    def test_o_eixo_de_implementacao_viaja_como_declaracao(self):
        s = _art()["IMPLEMENTATION_STATE"]
        self.assertEqual(s["NATUREZA"], "DECLARED_BY_BIBLE")
        self.assertIn("nao e observacao", s["O_QUE_ISTO_NAO_E"])

    def test_blocker_tem_de_impedir_uma_propriedade_nomeada(self):
        for g in _art()["GAPS"]:
            if g["CLOSE_GATE"] == P.BLOCKER:
                self.assertTrue(
                    any(p.lower().replace("_", " ") in g["WHY"].lower()
                        or p in g["WHY"] for p in P.PROPRIEDADES),
                    "%s e blocker e nao nomeia propriedade nenhuma"
                    % g["GAP_ID"])


class ONumeroDeLeisVemDoDono(unittest.TestCase):

    def test_o_total_nao_esta_escrito_a_mao(self):
        with open(os.path.join(RAIZ, "provas",
                               "os_portoes_da_collection.py"),
                  encoding="utf-8") as f:
            fonte = f.read()
        self.assertNotIn("LAW_TOTAL = 105", fonte)
        self.assertNotIn("return 105", fonte)
        self.assertEqual(_art()["LAW_TOTAL"], 105,
                         "o registo deixou de ter 105 leis — remedir, nao "
                         "reescrever o numero")

    def test_o_total_segue_o_registo_e_nao_uma_constante(self):
        """Mutante sobrevivente: `return d, L, 105`.

        Conferir o total contra 105 nao apanha um 105 escrito a mao — as duas
        pontas dizem a mesma coisa por acaso.

            UM NUMERO CONFERIDO CONTRA ELE PROPRIO
            NAO E UMA CONFERENCIA: E UM ECO.

        Aqui o registo passa a ter menos leis, e o total TEM de segui-lo.
        """
        real = P._json

        def falso(c):
            import copy
            d = copy.deepcopy(real(c))
            if c == P.LEIS:
                d["LAWS"] = d["LAWS"][:7]
            return d
        P._json = falso
        try:
            _d, L, total = P.leis()
            self.assertEqual(total, 7,
                             "o total nao seguiu o registo: esta escrito a mao")
            self.assertEqual(total, len(L))
        finally:
            P._json = real

    def test_ids_repetidos_rebentam(self):
        real = P._json

        def falso(c):
            import copy
            d = copy.deepcopy(real(c))
            if c == P.LEIS:
                d["LAWS"][1]["id"] = d["LAWS"][0]["id"]
            return d
        P._json = falso
        try:
            with self.assertRaises(P.MedicaoInvalida):
                P.leis()
        finally:
            P._json = real


class ModuloNaoEFluxo(unittest.TestCase):

    def test_ready_tem_modulo_e_nao_tem_fluxo(self):
        r = _art()["CANONICAL_E2E"]["READY"]
        self.assertEqual(r["MODULE_EXISTS"], "YES")
        self.assertEqual(r["FLOW_EXECUTED"], "NO",
                         "um CLI e uma prova viraram uma rota")

    def test_nenhuma_etapa_tem_fluxo_sem_aresta(self):
        for e, v in _art()["CANONICAL_E2E"].items():
            if v["FLOW_EXECUTED"] == "YES":
                self.assertEqual(v["EDGE_EXISTS"], "YES",
                                 "%s atravessa sem aresta declarada" % e)

    def test_o_portao_so_fecha_com_a_estrada_inteira(self):
        a = _art()
        c = a["COLLECTION_CORE_CLOSE"]
        inteira = all(v["FLOW_EXECUTED"] == "YES"
                      for v in a["CANONICAL_E2E"].values())
        self.assertFalse(inteira)
        self.assertEqual(c["VEREDICTO"], "FAIL")
        self.assertEqual(c["CANONICAL_E2E"], "NOT_PROVEN")


class OQueNaoSeSabeFicaUnknown(unittest.TestCase):

    def test_live_nao_herda_do_descartavel(self):
        d = _art()["DB_SCHEMA_VS_LIVE"]
        self.assertEqual(d["MIGRATION_APPLIED_LIVE"], "UNKNOWN")
        self.assertIn("YES", d["MIGRATION_APPLIED_DISPOSABLE"])

    def test_custo_ausente_nao_vira_zero(self):
        o = _art()["OBSERVABILITY"]
        self.assertEqual(o["COST"], "NOT_INSTRUMENTED")
        self.assertNotEqual(o["COST"], 0)
        self.assertIn("nao e zero", o["O_QUE_NOT_INSTRUMENTED_NAO_E"])

    def test_o_numero_de_missoes_ate_a_coleta_grande_e_unknown(self):
        a = _art()
        self.assertEqual(a["MINIMUM_MISSIONS_TO_BIG_COLLECTION_READY"],
                         "UNKNOWN")
        self.assertIn("feeling", a["PORQUE_O_SEGUNDO_E_UNKNOWN"])


class TodoBuracoMedidoERespondido(unittest.TestCase):

    def test_um_buraco_novo_do_censo_rebenta_a_medicao(self):
        """Um buraco que o censo mede e a matriz ignora tem de gritar."""
        real = P._json

        def falso(c):
            import copy
            d = copy.deepcopy(real(c))
            if c == P.BURACOS:
                d["BURACOS"].append({"NOME": "UM_BURACO_QUE_NINGUEM_CLASSIFICOU"})
            return d
        P._json = falso
        try:
            with self.assertRaises(P.MedicaoInvalida):
                P.medir()
        finally:
            P._json = real


class ADagSoTemBlocker(unittest.TestCase):

    def test_nenhuma_missao_nasce_de_divida(self):
        """Uma missao tem de ter PELO MENOS UM blocker ABERTO, e nenhuma divida.

        ⚠️ ESTE TESTE EXIGIA QUE **TODOS** OS SINTOMAS FOSSEM BLOCKER, e isso
        so era verdade enquanto nada fechava. Quando `G-E2E-01` fechou, a
        causa `RC-C` passou a ter um sintoma fechado e outro aberto — e o
        teste reprovou uma fila correcta.

            UM TESTE QUE SO ESTA CERTO ENQUANTO NADA AVANCA
            E UM TESTE QUE MEDE O PRIMEIRO DIA.
        """
        a = _art()
        raizes_com_missao = {m["ROOT_CAUSE"] for m in a["MINIMUM_MISSION_DAG"]}
        for r in a["ROOT_CAUSES"]:
            if r["ROOT_CAUSE_ID"] not in raizes_com_missao:
                continue
            estados = []
            for s in r["SYMPTOMS"]:
                g = next((x for x in a["GAPS"] if x["GAP_ID"] == s), None)
                if g:
                    estados.append(g["CLOSE_GATE"])
                    self.assertNotEqual(
                        g["CLOSE_GATE"], P.DEBT,
                        "%s virou missao e e divida que nao bloqueia" % s)
            self.assertIn(P.BLOCKER, estados,
                          "%s virou missao sem nenhum blocker aberto"
                          % r["ROOT_CAUSE_ID"])

    def test_a_primeira_missao_nao_tem_dependencia_aberta(self):
        """ABERTA — e nao «nenhuma». Uma dependencia ja fechada nao trava.

        A versao anterior exigia lista vazia, e reprovou assim que `RC-B`
        fechou deixando a referencia para tras. A referencia continua certa:
        ela e HISTORIA da ordem, e nao um bloqueio de hoje.
        """
        a = _art()
        primeira = a["MINIMUM_MISSION_DAG"][0]
        rc = next(r for r in a["ROOT_CAUSES"]
                  if r["ROOT_CAUSE_ID"] == primeira["ROOT_CAUSE"])
        abertas = []
        for dep in rc["DEPENDENCIES"]:
            outra = next((x for x in a["ROOT_CAUSES"]
                          if x["ROOT_CAUSE_ID"] == dep), None)
            if outra is None:
                continue
            sintomas = [g for g in a["GAPS"] if g["GAP_ID"] in outra["SYMPTOMS"]]
            if any(g["CLOSE_GATE"] == P.BLOCKER for g in sintomas):
                abertas.append(dep)
        self.assertEqual(abertas, [],
                         "a primeira missao da fila depende de causa ainda "
                         "aberta: %s" % abertas)

    def test_o_scrap_nao_entra_na_fila_do_fecho(self):
        a = _art()
        for m in a["MINIMUM_MISSION_DAG"]:
            self.assertNotIn("SCRAP", m["ID"])
        self.assertEqual(a["SCRAP"]["INTEGRATED"], "NO")
        self.assertEqual(a["SCRAP"]["CHANGED"], "NO")


class ODocumentoNaoEDonoDosNumeros(unittest.TestCase):
    """O JSON e o dono. O Markdown explica.

        DOIS DONOS DE UM NUMERO SAO DUAS VERDADES,
        E A PARTIR DAI NENHUMA DAS DUAS VALE.
    """

    def _md(self):
        with open(os.path.join(RAIZ, "docs", "operacao",
                               "COLLECTION-V1-CLOSE-GATES.md"),
                  encoding="utf-8") as f:
            return f.read()

    def test_o_relato_nao_contradiz_o_artefato(self):
        import json
        caminho = os.path.join(RAIZ, P.SAIDA)
        if not os.path.isfile(caminho):
            self.skipTest("o artefato ainda nao foi gerado")
        with open(caminho, encoding="utf-8") as f:
            a = json.load(f)
        md = self._md()
        self.assertIn("BLOCKERS            = %d" % len(a["BLOCKERS"]), md)
        self.assertIn("COLLECTION_CORE_CLOSE = %s"
                      % a["COLLECTION_CORE_CLOSE"]["VEREDICTO"], md)
        self.assertIn("MISSÕES ATÉ FECHAR  = %s"
                      % a["MINIMUM_MISSIONS_TO_COLLECTION_CORE_CLOSE"], md)

    def test_a_matriz_declara_o_head_e_a_versao_medidos(self):
        with open(os.path.join(RAIZ, "docs", "biblia",
                               "CONFORMIDADE-ITALIA.md"), encoding="utf-8") as f:
            m = f.read()
        self.assertIn("**Bíblia:** `V1.4`", m)
        self.assertIn("**LAW_TOTAL:** `105`", m)
        self.assertNotIn("**Bíblia:** `V1.3`", m,
                         "a matriz ainda anuncia a versao antiga")


if __name__ == "__main__":
    unittest.main()
