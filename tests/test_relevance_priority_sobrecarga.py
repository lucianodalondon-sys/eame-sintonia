#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A SOBRECARGA DE `RELEVANCE` E `PRIORITY`, GUARDADA — C-INT-OWNER-01.

⚠️ A DECISAO HUMANA FOI TOMADA EM C-INT-NIGHT-01: opcao A/A, os dois nomes nus
APOSENTADOS. As provas abaixo passaram a guardar a decisao, e nao a espera.

    python3 -m unittest tests.test_relevance_priority_sobrecarga -v

O QUE ESTAS PROVAS SÃO
----------------------
A medição que sustenta `research/intelligence/RELEVANCE-PRIORITY-DECISION-
PACKAGE-V1.md`, escrita como teste para não virar lembrança. Se alguém fundir
dois dos nove conceitos, renomear um dono ou apagar uma fronteira, o teste
falha — e a falha é a informação.

O QUE ELAS NÃO SÃO
------------------
    NAO escolhem dono.       NAKED_RELEVANCE_RETIRED = YES
    NAO implementam nada.    NAKED_PRIORITY_RETIRED  = YES
    NAO criam score, peso, ranking nem formula.

    UM PACOTE DE DECISAO QUE NINGUEM PODE RE-MEDIR
    E UMA OPINIAO COM TABELA.
"""
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho


def git(*a):
    return subprocess.check_output(["git"] + list(a), cwd=RAIZ, text=True,
                                   stderr=subprocess.DEVNULL)


def ficheiro(*p):
    return os.path.join(RAIZ, *p)


def texto(rel):
    with open(ficheiro(rel), encoding="utf-8") as f:
        return f.read()


class ARelevanciaEhCincoConceitos(unittest.TestCase):
    """`RELEVANCE_ONE_CONCEPT = NO` — e cada um tem lei, ou não tem dono."""

    #: conceito -> o ficheiro que o possui (None = sem dono, declarado)
    DONOS = {
        "SOURCE_RELEVANCE": "leis/relevancia_da_fonte.py",
        "ITEM_RELEVANCE": "admissao/admissao.py",
        "CASE_RELEVANCE": "leis/adama_relevance.py",
        "USER_DECISION_RELEVANCE": None,
    }

    def test_os_tres_donos_implementados_existem(self):
        for conceito, caminho in self.DONOS.items():
            if caminho:
                self.assertTrue(os.path.exists(ficheiro(caminho)),
                                "%s perdeu o dono %s" % (conceito, caminho))

    def test_a_lei_da_fonte_continua_a_declarar_as_sete_fronteiras(self):
        """⚠️ Esta prova é a espinha do pacote de decisão.

        `leis/relevancia_da_fonte.py` já tinha feito metade desta arbitragem
        antes de ela ser pedida. Se alguém apagar estas linhas, a próxima
        missão volta a concluir «relevância não tem dono».
        """
        lei = texto("leis/relevancia_da_fonte.py")
        for vizinho in ("ITEM_RELEVANCE", "SOURCE_HEALTH", "ACCESSIBILITY",
                        "SOURCE_RELIABILITY", "COST", "COLLECTION_PRIORITY",
                        "CASE_RELEVANCE"):
            self.assertIn("SOURCE_RELEVANCE  != %s" % vizinho, lei,
                          "a fronteira com %s desapareceu da lei" % vizinho)

    def test_as_tres_leis_dizem_que_relevancia_e_do_PAR(self):
        """Nenhuma delas admite `relevante = true` como propriedade da coisa."""
        self.assertIn("NAO EXISTE `relevante = true` NUMA FONTE",
                      texto("leis/relevancia_da_fonte.py"))
        self.assertIn("RELEVANCIA NAO E UM BOOLEANO UNIVERSAL",
                      texto("admissao/admissao.py"))

    def test_os_vocabularios_nao_se_tocam(self):
        """Escalas diferentes provam perguntas diferentes.

        Se um dia `adama_relevance` passar a devolver `AUTORIZA`, os dois
        conceitos fundiram-se — e este teste é o aviso.
        """
        sys.path.insert(0, ficheiro("leis"))
        import adama_relevance as ar
        import relevancia_da_fonte as rf
        self.assertEqual(("AUTORIZA", "BARRA", "EXIGE_AVALIACAO"), rf.VEREDITOS)
        self.assertEqual({"A", "B", "C", "D", "E"}, set(ar.SUPERFICIE))
        self.assertEqual(set(), set(rf.VEREDITOS) & set(ar.SUPERFICIE))

    def test_nenhuma_das_leis_criou_score(self):
        """`INT-LAW-093` e as leis da coleta proíbem-no, e continuam a cumprir."""
        for rel in ("leis/relevancia_da_fonte.py", "leis/adama_relevance.py",
                    "leis/politica_da_coleta.py"):
            baixo = texto(rel).lower()
            for proibido in ("relevance_score", "priority_score",
                             "ranking_unico = calcul"):
                self.assertNotIn(proibido, baixo, "%s ganhou score" % rel)


class APrioridadeEhQuatroConceitos(unittest.TestCase):
    """`PRIORITY_ONE_CONCEPT = NO` — e os três implementados não colidem."""

    def test_a_prioridade_da_necessidade_e_da_collection(self):
        import gestao_da_coleta as g
        self.assertIn("PRIORITY", g.CAMPOS_DA_PRIORIDADE)
        self.assertEqual(
            ("P1_BLOQUEIA_OUTRAS", "P2_NECESSARIA", "P3_DESEJAVEL",
             "P4_OPORTUNISTA", "UNKNOWN"), g.PRIORIDADES)

    def test_a_prioridade_da_politica_CONSOME_a_da_necessidade(self):
        """São matéria-prima e resultado, não sinónimos."""
        sys.path.insert(0, ficheiro("leis"))
        import politica_da_coleta as p
        self.assertIn("REQUIREMENT_PRIORITY", p.DIMENSOES)
        self.assertEqual(10, len(p.DIMENSOES),
                         "as dimensoes mudaram: re-medir o pacote de decisao")

    def test_a_prioridade_comercial_tem_writer_unico_no_motor(self):
        sys.path.insert(0, ficheiro("motor"))
        import v21_comercial as c
        self.assertTrue(callable(c.prioridade))
        for valor in ("SALES_READY", "SALES_PREPARE", "STRATEGIC_OPPORTUNITY",
                      "TO_VALIDATE"):
            self.assertIn(getattr(c, valor), c.SIGNIFICADO,
                          "%s ficou sem significado declarado" % valor)

    def test_a_prioridade_comercial_e_por_portoes_e_nao_por_soma(self):
        sys.path.insert(0, ficheiro("motor"))
        import v21_comercial as c
        self.assertIn("Portões, não soma de pontos", c.prioridade.__doc__)

    def test_o_significado_de_SALES_READY_nao_promete_venda(self):
        """⚠️ A tensão do §4 do pacote, guardada.

        O NOME diz nível C; o SIGNIFICADO declarado é nível B — necessidade,
        catálogo, rótulo, geografia e janela. Se um dia o significado passar a
        falar de venda, stock, preço ou canal, a promessa passou a ser feita
        com dado que não a sustenta.
        """
        sys.path.insert(0, ficheiro("motor"))
        import v21_comercial as c
        frase = c.SIGNIFICADO[c.SALES_READY].lower()
        for palavra_proibida in ("stock", "preço", "preco", "canal",
                                 "cliente", "venda realizada"):
            self.assertNotIn(palavra_proibida, frase,
                             "SALES_READY passou a prometer %s, que dado "
                             "publico nao prova" % palavra_proibida)


class NenhumaFronteiraDeDepartamentoFoiAtravessada(unittest.TestCase):
    """`COLLECTION != INTELLIGENCE != DELIVERY`, medido nos campos."""

    def test_a_intelligence_nao_escreve_prioridade_de_coleta(self):
        for token in ("REQUIREMENT_PRIORITY", "PRIORITY_TIER"):
            try:
                saida = git("grep", "-l", "-I", "--", token, "--",
                            "motor", "superficie")
            except subprocess.CalledProcessError:
                saida = ""
            self.assertEqual("", saida.strip(),
                             "a Intelligence escreve %s: %s" % (token, saida))

    def test_a_collection_nao_escreve_prioridade_comercial(self):
        try:
            saida = git("grep", "-l", "-I", "--", "COMMERCIAL_PRIORITY", "--",
                        "coleta", "admissao", "guarda", "leis", "orquestrador")
        except subprocess.CalledProcessError:
            saida = ""
        self.assertEqual("", saida.strip(),
                         "a Collection escreve COMMERCIAL_PRIORITY: %s" % saida)

    def test_o_portal_le_prioridade_comercial_e_nao_a_recalcula(self):
        """O portal transporta o veredito; não o produz."""
        modelo = texto("italia-portale/client/italy-app-model.js")
        self.assertIn("commercialPriority", modelo)
        for calculo in ("function prioridade", "computeCommercialPriority",
                        "SALES_READY ="):
            self.assertNotIn(calculo, modelo,
                             "o portal passou a calcular prioridade comercial")


class ADecisaoAAFoiAplicadaESeguraSozinha(unittest.TestCase):
    """⚠️ A prova da decisão humana A/A — C-INT-NIGHT-01.

    Aposentar um nome não é dar-lhe um dono. Estas provas guardam a diferença,
    que é exactamente onde a próxima missão pode escorregar.
    """

    def _v3(self):
        import json
        with open(ficheiro("docs/intelligence/"
                           "INTELLIGENCE-CONCEPT-OWNERSHIP-V3.json"),
                  encoding="utf-8") as f:
            return json.load(f)

    def test_os_dois_nomes_nus_nao_sao_conceitos_operacionais(self):
        v3 = self._v3()
        for nome in ("RELEVANCE", "PRIORITY"):
            self.assertNotIn(nome, v3["CONCEITOS"],
                             "%s voltou a ser um conceito" % nome)
            self.assertIn(nome, v3["NOMES_APOSENTADOS"])
            self.assertEqual("RETIRED_AS_OVERLOADED_NAME",
                             v3["NOMES_APOSENTADOS"][nome]["DECISAO"])

    def test_nenhum_nome_nu_ganhou_dono(self):
        """O erro que a opção A existe para impedir."""
        v3 = self._v3()
        for nome, ret in v3["NOMES_APOSENTADOS"].items():
            self.assertNotIn("OWNER", ret,
                             "%s ganhou um dono em vez de ser aposentado" % nome)

    def test_ninguem_ficou_em_HUMAN_DECISION_REQUIRED(self):
        v3 = self._v3()
        pendentes = [k for k, c in v3["CONCEITOS"].items()
                     if c["OWNER"] == "HUMAN_DECISION_REQUIRED"]
        self.assertEqual([], pendentes, "decisao humana por tomar: %s" % pendentes)

    def test_os_nove_conceitos_escondidos_estao_todos_declarados(self):
        v3 = self._v3()
        for nome, ret in v3["NOMES_APOSENTADOS"].items():
            for coberto in ret["COBRIA"]:
                self.assertIn(coberto, v3["CONCEITOS"],
                              "%s cobria %s, que sumiu" % (nome, coberto))

    def test_os_conceitos_especificos_nao_se_fundiram(self):
        """§8 do enunciado, uma linha por par."""
        v3 = self._v3()["CONCEITOS"]
        pares = (("SOURCE_RELEVANCE", "CASE_RELEVANCE"),
                 ("ITEM_RELEVANCE", "USER_DECISION_RELEVANCE"),
                 ("REQUIREMENT_PRIORITY", "COMMERCIAL_PRIORITY"),
                 ("PRIORITY_TIER", "WATCHLIST_PRIORITY"))
        for a, b in pares:
            self.assertIn(a, v3)
            self.assertIn(b, v3)
            self.assertNotEqual(
                (v3[a]["OWNER"], v3[a]["MODULO_DONO"]),
                (v3[b]["OWNER"], v3[b]["MODULO_DONO"]),
                "%s e %s fundiram-se" % (a, b))

    def test_DEFINED_nao_e_IMPLEMENTED(self):
        """A prova respeita a distinção: nem todos os nove correm hoje."""
        v3 = self._v3()["CONCEITOS"]
        self.assertEqual("DEFINED_ONLY",
                         v3["WATCHLIST_PRIORITY"]["CURRENT_IMPLEMENTATION"],
                         "WATCHLIST_PRIORITY ganhou runtime sem missao")
        self.assertEqual("IMPLEMENTED",
                         v3["CASE_RELEVANCE"]["CURRENT_IMPLEMENTATION"])

    def test_o_V2_fica_como_historia_e_nao_foi_reescrito(self):
        """Um censo que muda depois de medido deixa de poder ser conferido."""
        import json
        with open(ficheiro("docs/intelligence/"
                           "INTELLIGENCE-CONCEPT-OWNERSHIP-V2.json"),
                  encoding="utf-8") as f:
            v2 = json.load(f)
        self.assertEqual("HUMAN_DECISION_REQUIRED",
                         v2["CONCEITOS"]["RELEVANCE"]["OWNER"],
                         "o V2 foi reescrito para fingir que sempre soube")
        self.assertEqual("INTELLIGENCE-CONCEPT-OWNERSHIP-V3.json",
                         v2["SUPERSEDED_BY"])

    def test_nenhum_score_foi_criado_por_esta_missao(self):
        """§11 do enunciado, guardado."""
        pacote = texto(
            "research/intelligence/RELEVANCE-PRIORITY-DECISION-PACKAGE-V1.md")
        for proibido in ("relevance_score =", "priority_score =",
                         "0-100", "peso =", "weight ="):
            self.assertNotIn(proibido, pacote.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
