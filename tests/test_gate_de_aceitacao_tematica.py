# -*- coding: utf-8 -*-
"""UM GATE QUE SE DEIXA COMPENSAR E UMA MEDIA COM NOME DE REGRA.

Este gate falha de quatro maneiras que nenhuma excecao denuncia:

    1. uma condicao boa compensa outra ma, e o conjunto «passa»;
    2. uma metrica em falta e lida como zero, e o que rebentou passa;
    3. o gate pontua ficheiros em vez de observacoes, e quatro edicoes do
       mesmo boletim valem quatro creditos;
    4. o limiar muda depois de alguem ver o resultado.

    SEM ALVO DESENHADO ANTES,
    A FLECHA ATERRA SEMPRE NO CENTRO DE ALGUMA COISA.
"""
import copy
import importlib.util
import json
import os
import sys
import unittest
from fractions import Fraction

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

_spec = importlib.util.spec_from_file_location(
    "gate_t", os.path.join(RAIZ, "provas", "gate_de_aceitacao_tematica.py"))
g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g)


def _contrato_no_disco():
    with open(os.path.join(RAIZ, g.SAIDA), encoding="utf-8") as f:
        return json.load(f)


def PERFEITO():
    """Um mecanismo que passa TUDO. Base para mexer uma coisa de cada vez."""
    return {
        "POSITIVE_CAPTURE_RATE": Fraction(11, 11),
        "EXPLICIT_FALSE_NEGATIVE": 0,
        "SPECIFICITY": Fraction(20, 20),
        "PRECISION_T3": Fraction(1, 1),
        "DECISION_COVERAGE": Fraction(31, 31),
        "GROUP_PASS_RATE": Fraction(31, 31),
        "ERROR": 0,
        "FALSE_SUBSTRING_OUTCOME_DEPENDENCY": 0,
    }


class OGateFoiEscritoAntesDoResultado(unittest.TestCase):

    def test_ha_um_dono_unico_e_e_o_codigo(self):
        self.assertEqual(g.GATE_OWNER, "provas/gate_de_aceitacao_tematica.py")
        self.assertEqual(g.GATE_VERSION, "V1")

    def test_os_oito_limiares_estao_declarados_com_a_razao_ao_lado(self):
        for chave, c in g.LIMIARES.items():
            self.assertIn("VALOR", c, chave)
            self.assertTrue(c.get("PORQUE"), "%s sem razao escrita" % chave)
            self.assertGreater(len(c["PORQUE"]), 60, chave)

    def test_cada_condicao_do_gate_aponta_para_um_limiar_declarado(self):
        for _nome, op, chave in g.CONDICOES:
            self.assertIn(chave, g.LIMIARES)
            self.assertIn(op, (">=", "<="))
        self.assertEqual(len(g.CONDICOES), 8)

    def test_os_numeros_sao_os_declarados(self):
        L = g.LIMIARES
        self.assertEqual(L["POSITIVE_CAPTURE_MINIMUM"]["VALOR"], Fraction(10, 11))
        self.assertEqual(L["EXPLICIT_FALSE_NEGATIVE_MAX"]["VALOR"], 0)
        self.assertEqual(L["SPECIFICITY_MINIMUM"]["VALOR"], Fraction(18, 20))
        self.assertEqual(L["PRECISION_T3_MINIMUM"]["VALOR"], Fraction(4, 5))
        self.assertEqual(L["DECISION_COVERAGE_MINIMUM"]["VALOR"], Fraction(28, 31))
        self.assertEqual(L["GROUP_PASS_MINIMUM"]["VALOR"], Fraction(28, 31))
        self.assertEqual(L["ERROR_MAX"]["VALOR"], 0)
        self.assertEqual(
            L["KNOWN_FALSE_SUBSTRING_OUTCOME_DEPENDENCY_MAX"]["VALOR"], 0)
        self.assertEqual(g.REACHABILITY_REQUIRED, Fraction(1, 1))

    def test_a_unidade_primaria_e_a_observacao(self):
        self.assertEqual(g.UNIDADE_PRIMARIA, "INDEPENDENT_OBSERVATION")
        self.assertEqual(g.UNIDADE_DIAGNOSTICA, "DOCUMENT")

    # ⚠️ A PRIMEIRA VERSAO PROCURAVA A STRING `THEMATIC_GATE_PASS` NO
    # CONTRATO — e acendia na frase que DEFINE a regra de integracao. Nomear a
    # metrica para explicar a regra nao e trazer o resultado dela para dentro.
    #
    #     UM MARCADOR QUE NAO DISTINGUE A DEFINICAO DO VALOR
    #     REPROVA O TEXTO QUE EXPLICA A REGRA.
    #
    # O que interessa e ESTRUTURAL: o contrato nao pode ter medicao nem
    # veredicto — nem uma chave de aplicacao, nem um booleano de PASS.
    def test_o_contrato_nao_leva_resultado_nenhum_dentro(self):
        """O alvo nao pode conter a flecha."""
        c = g.contrato()
        self.assertNotIn("APLICACAO_AO_BASELINE_CONGELADO", c)

        vereditos = []

        def varre(no, caminho=""):
            if isinstance(no, dict):
                for k, v in no.items():
                    onde = "%s.%s" % (caminho, k)
                    if (k.endswith(("_PASS", "_RESULT", "VEREDICTO"))
                            and not isinstance(v, str)):
                        vereditos.append(onde)
                    if isinstance(v, bool):
                        vereditos.append(onde)
                    varre(v, onde)
            elif isinstance(no, list):
                for i, v in enumerate(no):
                    varre(v, "%s[%d]" % (caminho, i))
        varre(c)
        self.assertEqual(vereditos, [],
                         "o contrato carrega veredicto: %s" % vereditos)

    def test_o_contrato_nao_carrega_os_numeros_do_baseline(self):
        """Se o alvo trouxesse a medicao, deixava de ter sido escrito antes."""
        art = g._json(g.BASELINE)
        bruto = json.dumps(g.contrato(), ensure_ascii=False)
        self.assertNotIn(art["FIRST_VALID_BASELINE_FINGERPRINT"], bruto)
        for chave in ("GROUP_PASS", "GROUP_FAIL", "GROUP_NOT_DECIDED"):
            self.assertNotIn('"%s"' % chave, bruto, chave)

    def test_a_assimetria_do_erro_esta_declarada(self):
        a = g.ASSIMETRIA
        self.assertEqual(
            a["FALSE_NEGATIVE_COST_VS_FALSE_POSITIVE_COST"], "GREATER")
        self.assertIn("ABSTAIN", a["ABSTAIN_VS_NEGATIVO_ERRADO"])
        self.assertTrue(a["MAS"], "abstencao excessiva tambem tem de reprovar")

    def test_o_escopo_nao_promete_eame(self):
        c = g.contrato()
        self.assertEqual(c["EVALUATION_SCOPE"],
                         "ITALIAN_AGRO_INSTITUTIONAL_CORPUS")
        self.assertEqual(set(c["NAO_AUTORIZA"]), {"FRANCE", "SPAIN", "EAME"})
        self.assertEqual(c["THIS_IS_NOT"], "FULL_EAME_PRODUCTION_RELEASE_GATE")

    def test_o_papel_do_gabarito_esta_fixado(self):
        self.assertEqual(g.T3_GROUND_TRUTH_ROLE, "EVALUATION")
        self.assertIn("UM CONJUNTO SO E INDEPENDENTE",
                      g.contrato()["INDEPENDENCIA"])


class OEstudoExternoFoiFeitoEHonesto(unittest.TestCase):

    def test_nenhuma_fonte_prescreve_limiar_universal(self):
        e = g.ESTUDO_EXTERNO
        self.assertEqual(
            e["THERE_IS_A_UNIVERSAL_CLASSIFIER_ACCEPTANCE_THRESHOLD"], "NO")
        self.assertEqual(len(e["SISTEMAS"]), 4)
        for s in e["SISTEMAS"]:
            self.assertEqual(s["PRESCREVE_LIMIAR_UNIVERSAL"], "NO", s["NOME"])
            self.assertTrue(s["FONTES"], s["NOME"])

    def test_os_quatro_sistemas_pedidos_foram_lidos(self):
        nomes = " ".join(s["NOME"] for s in g.ESTUDO_EXTERNO["SISTEMAS"])
        for esperado in ("Document AI", "Azure", "scikit-learn", "NIST"):
            self.assertIn(esperado, nomes)

    def test_a_convergencia_nao_foi_fabricada(self):
        """Onde uma fonte se cala, fica escrito que ela se cala."""
        c = g.ESTUDO_EXTERNO["CONVERGENCIA"]
        self.assertEqual(len(c), 5)
        parciais = [v for v in c.values() if not v.startswith("4 de 4")]
        self.assertTrue(parciais, "consenso perfeito em cinco pontos e suspeito")
        for v in parciais:
            self.assertIn("—", v, "uma convergencia parcial tem de dizer porque")

    def test_o_ponto_fraco_do_estudo_esta_registado(self):
        fracos = " ".join(
            g.ESTUDO_EXTERNO["ONDE_A_CONVERGENCIA_E_MAIS_FRACA_DO_QUE_PARECE"])
        self.assertIn("80%", fracos, "o unico numero encontrado tem de constar")
        self.assertIn("NIST", fracos)

    def test_o_unico_numero_do_estudo_diz_de_que_pagina_veio(self):
        """Uma citacao presa a pagina errada nao e verificavel.

        O «80%» nao esta na pagina de threshold nem na transparency note: esta
        na accuracy-confidence. Enquanto a fonte do numero nao estiver citada,
        quem vier a seguir nao tem como ir la confirmar — e uma afirmacao que
        nao se confirma vale o mesmo que nenhuma.
        """
        azure = [s for s in g.ESTUDO_EXTERNO["SISTEMAS"]
                 if "Azure" in s["NOME"]][0]
        fonte = azure["FONTE_DO_UNICO_NUMERO"]
        self.assertIn("accuracy-confidence", fonte)
        self.assertIn(fonte, azure["FONTES"],
                      "a fonte do numero tem de estar na lista de fontes")

    def test_o_numero_da_azure_vem_declarado_como_estimativa_de_treino(self):
        """O numero so se desqualifica se ficar dito contra o que foi medido."""
        fracos = " ".join(
            g.ESTUDO_EXTERNO["ONDE_A_CONVERGENCIA_E_MAIS_FRACA_DO_QUE_PARECE"])
        self.assertIn("TRAINING DATA", fracos.upper())
        self.assertIn("holdout", fracos)


class NenhumaMediaCompensa(unittest.TestCase):
    """Um hard gate que se compensa nao e um gate."""

    def test_o_perfeito_passa(self):
        r = g.avaliar_gate(PERFEITO())
        self.assertTrue(r["THEMATIC_GATE_PASS"])
        self.assertEqual(r["FAILED_CONDITIONS"], [])
        self.assertEqual(r["VEREDICTO"], "PASS")

    def test_cada_condicao_sozinha_derruba_o_conjunto(self):
        quebras = {
            "POSITIVE_CAPTURE_RATE": Fraction(9, 11),
            "EXPLICIT_FALSE_NEGATIVE": 1,
            "SPECIFICITY": Fraction(17, 20),
            "PRECISION_T3": Fraction(79, 100),
            "DECISION_COVERAGE": Fraction(27, 31),
            "GROUP_PASS_RATE": Fraction(27, 31),
            "ERROR": 1,
            "FALSE_SUBSTRING_OUTCOME_DEPENDENCY": 1,
        }
        for campo, mau in quebras.items():
            m = PERFEITO()
            m[campo] = mau
            r = g.avaliar_gate(m)
            self.assertFalse(r["THEMATIC_GATE_PASS"], campo)
            self.assertEqual(r["FAILED_CONDITIONS"], [campo], campo)

    def test_uma_metrica_em_falta_nao_e_lida_como_zero(self):
        for campo in g.EXIGIDAS:
            m = PERFEITO()
            del m[campo]
            with self.assertRaises(g.MetricaEmFalta, msg=campo):
                g.avaliar_gate(m)

    def test_o_limiar_e_inclusivo_exactamente_no_valor(self):
        m = PERFEITO()
        m["POSITIVE_CAPTURE_RATE"] = Fraction(10, 11)
        m["SPECIFICITY"] = Fraction(18, 20)
        m["PRECISION_T3"] = Fraction(4, 5)
        m["DECISION_COVERAGE"] = Fraction(28, 31)
        m["GROUP_PASS_RATE"] = Fraction(28, 31)
        self.assertTrue(g.avaliar_gate(m)["THEMATIC_GATE_PASS"])

    def test_um_fio_abaixo_do_limiar_reprova(self):
        m = PERFEITO()
        m["GROUP_PASS_RATE"] = Fraction(28, 31) - Fraction(1, 10000)
        self.assertFalse(g.avaliar_gate(m)["THEMATIC_GATE_PASS"])


class ORedTeamDoGate(unittest.TestCase):
    """Dez maneiras de tentar passar sem merecer. Todas devem falhar."""

    def _falha(self, m, esperado):
        r = g.avaliar_gate(m)
        self.assertFalse(r["THEMATIC_GATE_PASS"])
        self.assertIn(esperado, r["FAILED_CONDITIONS"])
        return r

    def test_1_precisao_perfeita_com_cobertura_de_10_por_cento(self):
        m = PERFEITO()
        m.update({"PRECISION_T3": Fraction(1, 1),
                  "DECISION_COVERAGE": Fraction(3, 31),
                  "GROUP_PASS_RATE": Fraction(3, 31),
                  "POSITIVE_CAPTURE_RATE": Fraction(1, 11),
                  "SPECIFICITY": Fraction(2, 20)})
        self._falha(m, "DECISION_COVERAGE")

    def test_2_recall_aparente_de_1_com_2_de_11_positivos_decididos(self):
        """Quem so decide dois positivos e acerta os dois nao capturou 11."""
        m = PERFEITO()
        m.update({"POSITIVE_CAPTURE_RATE": Fraction(2, 11),
                  "DECISION_COVERAGE": Fraction(6, 31),
                  "GROUP_PASS_RATE": Fraction(6, 31)})
        self._falha(m, "POSITIVE_CAPTURE_RATE")

    def test_3_28_de_31_acertos_com_um_falso_negativo_explicito(self):
        m = PERFEITO()
        m.update({"GROUP_PASS_RATE": Fraction(28, 31),
                  "EXPLICIT_FALSE_NEGATIVE": 1,
                  "POSITIVE_CAPTURE_RATE": Fraction(10, 11)})
        r = self._falha(m, "EXPLICIT_FALSE_NEGATIVE")
        self.assertEqual(r["FAILED_CONDITIONS"], ["EXPLICIT_FALSE_NEGATIVE"])

    def test_4_10_de_11_positivos_mas_dez_falsos_positivos(self):
        m = PERFEITO()
        m.update({"POSITIVE_CAPTURE_RATE": Fraction(10, 11),
                  "PRECISION_T3": Fraction(10, 20),
                  "SPECIFICITY": Fraction(10, 20),
                  "GROUP_PASS_RATE": Fraction(20, 31)})
        self._falha(m, "PRECISION_T3")

    def test_5_18_de_20_negativos_mas_captura_positiva_ruim(self):
        m = PERFEITO()
        m.update({"SPECIFICITY": Fraction(18, 20),
                  "POSITIVE_CAPTURE_RATE": Fraction(3, 11),
                  "DECISION_COVERAGE": Fraction(21, 31),
                  "GROUP_PASS_RATE": Fraction(21, 31)})
        self._falha(m, "POSITIVE_CAPTURE_RATE")

    def test_6_acuracia_condicional_alta_com_muita_abstencao(self):
        """O gate nao aceita acuracia condicional para aprovar."""
        m = PERFEITO()
        m.update({"DECISION_COVERAGE": Fraction(8, 31),
                  "GROUP_PASS_RATE": Fraction(8, 31),
                  "POSITIVE_CAPTURE_RATE": Fraction(3, 11),
                  "SPECIFICITY": Fraction(5, 20)})
        self._falha(m, "GROUP_PASS_RATE")
        nomes = [n for n, _o, _l in g.CONDICOES]
        self.assertNotIn("CONDITIONAL_ACCURACY", nomes)

    def test_7_um_erro_escondido_como_unknown(self):
        """ERRO nunca vira ABSTAIN. Se virasse, o gate nao o veria."""
        m = PERFEITO()
        m["ERROR"] = 1
        self._falha(m, "ERROR")
        self.assertEqual(
            g.LIMIARES["ERROR_MAX"]["NUNCA_VIRA"], ["NAO", "ABSTAIN", "UNKNOWN"])

    def test_8_36_ficheiros_usados_no_lugar_de_31_observacoes(self):
        """Pontuar por ficheiro infla o denominador e o numerador."""
        m = PERFEITO()
        m.update({"GROUP_PASS_RATE": Fraction(28, 36),
                  "DECISION_COVERAGE": Fraction(28, 36)})
        self._falha(m, "GROUP_PASS_RATE")
        self.assertEqual(g.UNIDADE_PRIMARIA, "INDEPENDENT_OBSERVATION")

    def test_9_acerto_dependente_de_substring_falso(self):
        m = PERFEITO()
        m["FALSE_SUBSTRING_OUTCOME_DEPENDENCY"] = 1
        r = self._falha(m, "FALSE_SUBSTRING_OUTCOME_DEPENDENCY")
        self.assertEqual(r["FAILED_CONDITIONS"],
                         ["FALSE_SUBSTRING_OUTCOME_DEPENDENCY"])

    def test_10_mecanismo_perfeito_offline_com_reachability_zero(self):
        tematico = g.avaliar_gate(PERFEITO())
        self.assertTrue(tematico["THEMATIC_GATE_PASS"])
        alcance = g.avaliar_reachability(0, 36)
        self.assertFalse(alcance["REACHABILITY_GATE_PASS"])
        i = g.avaliar_integracao(alcance, tematico)
        self.assertFalse(i["INTEGRATION_GATE_PASS"])
        self.assertEqual(i["VEREDICTO"], "NOT_READY")

    def test_o_inverso_tambem_nao_passa(self):
        """Linhagem boa com mecanismo mau tambem e NOT_READY."""
        mau = PERFEITO()
        mau["POSITIVE_CAPTURE_RATE"] = Fraction(1, 11)
        i = g.avaliar_integracao(g.avaliar_reachability(36, 36),
                                 g.avaliar_gate(mau))
        self.assertFalse(i["INTEGRATION_GATE_PASS"])


class OAlcanceNaoSeFabrica(unittest.TestCase):

    def test_alcance_total_passa(self):
        r = g.avaliar_reachability(36, 36)
        self.assertTrue(r["REACHABILITY_GATE_PASS"])
        self.assertEqual(r["REACHABILITY"], "1")

    def test_um_item_que_nao_chega_reprova(self):
        self.assertFalse(
            g.avaliar_reachability(35, 36)["REACHABILITY_GATE_PASS"])

    def test_denominador_vazio_para_em_vez_de_passar(self):
        with self.assertRaises(g.MetricaEmFalta):
            g.avaliar_reachability(0, 0)

    def test_o_denominador_declarado_bate_com_o_medido(self):
        """Uma constante que ninguem confere e uma constante que deriva."""
        art = g._json(g.BASELINE)
        self.assertEqual(g.REACHABILITY_DENOMINADOR_T3, len(art["CASES"]))
        self.assertEqual(g.reachability_do_baseline(art)["COMPROVADOS"],
                         g.REACHABILITY_DENOMINADOR_T3)

    def test_o_contrato_diz_que_nao_se_inventa_fonte(self):
        self.assertIn("fabricar SOURCE_ID",
                      g.avaliar_reachability(36, 36)["NAO_AUTORIZA"])


class AExtraccaoContaObservacoesENaoFicheiros(unittest.TestCase):

    def test_um_grupo_so_tem_previsao_binaria_se_todos_concordarem(self):
        self.assertEqual(g.previsao_do_grupo(["SIM", "SIM"]), "SIM")
        self.assertEqual(g.previsao_do_grupo(["NAO"]), "NAO")
        self.assertIsNone(g.previsao_do_grupo(["SIM", "NAO"]))
        self.assertIsNone(g.previsao_do_grupo(["SIM", "NAO_SEI"]))
        self.assertIsNone(g.previsao_do_grupo(["NAO_SEI"]))
        self.assertIsNone(g.previsao_do_grupo(["ERRO"]))

    def test_a_extraccao_le_31_observacoes_do_baseline(self):
        art = g._json(g.BASELINE)
        m = g.metricas_do_baseline(art)
        d = m["_DIAGNOSTICO"]
        self.assertEqual(d["GROUP_TOTAL"], 31)
        self.assertEqual(d["GROUP_POSITIVE"], 11)
        self.assertEqual(d["GROUP_NEGATIVE"], 20)
        self.assertEqual(d["GROUP_POSITIVE"] + d["GROUP_NEGATIVE"], 31)

    def test_a_extraccao_nao_recalcula_previsao_nenhuma(self):
        with open(os.path.join(RAIZ, "provas",
                               "gate_de_aceitacao_tematica.py"),
                  encoding="utf-8") as f:
            fonte = f.read()
        for proibido in ("import admissao", "adm.decidir", "in texto"):
            self.assertNotIn(proibido, fonte, proibido)

    def test_o_agrupamento_veio_do_gabarito_e_nao_deste_gate(self):
        art = g._json(g.BASELINE)
        self.assertEqual(art["CANONICAL_OBSERVATION_GROUPING_FOUND"], "YES")
        self.assertIn("T3-GROUND-TRUTH-EVAL-V1", art["GROUPING_SOURCE"])


class OBaselineFoiJulgadoMecanicamente(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        (cls.art, cls.metricas, cls.alcance,
         cls.tematico, cls.integracao) = g.aplicar_ao_baseline()

    def test_o_baseline_julgado_e_o_congelado(self):
        self.assertEqual(self.art["FIRST_VALID_BASELINE_FINGERPRINT"],
                         "f24eceedd1235a1c1909a0d941aea4b87bdf8cba"
                         "6547be762c5785e9ff635a85")

    def test_o_mecanismo_de_hoje_reprova(self):
        self.assertEqual(self.tematico["VEREDICTO"], "FAIL")
        self.assertFalse(self.tematico["THEMATIC_GATE_PASS"])

    def test_as_condicoes_que_falham_estao_nomeadas(self):
        falhadas = set(self.tematico["FAILED_CONDITIONS"])
        self.assertIn("POSITIVE_CAPTURE_RATE", falhadas)
        self.assertIn("FALSE_SUBSTRING_OUTCOME_DEPENDENCY", falhadas)
        # e as duas que ele cumpre ficam a vista, e nao apagadas
        passadas = {l["CONDICAO"] for l in self.tematico["LINHAS"] if l["PASSA"]}
        self.assertIn("EXPLICIT_FALSE_NEGATIVE", passadas)
        self.assertIn("ERROR", passadas)

    def test_o_alcance_tambem_reprova(self):
        self.assertFalse(self.alcance["REACHABILITY_GATE_PASS"])
        self.assertEqual(self.alcance["COMPROVADOS"], 36)

    def test_integracao_e_not_ready(self):
        self.assertEqual(self.integracao["VEREDICTO"], "NOT_READY")

    def test_o_contrato_no_disco_bate_com_o_codigo(self):
        d = _contrato_no_disco()
        self.assertEqual(d["GATE_OWNER"], g.GATE_OWNER)
        self.assertEqual(d["GATE_VERSION"], g.GATE_VERSION)
        self.assertEqual(
            d["APLICACAO_AO_BASELINE_CONGELADO"][
                "CURRENT_ADMISSION_GATE_RESULT"], "FAIL")

    def test_reprovar_nao_autoriza_consertar(self):
        d = _contrato_no_disco()["APLICACAO_AO_BASELINE_CONGELADO"]
        self.assertIn("ADMISSION_CHANGED = NO", d["O_QUE_ISTO_NAO_AUTORIZA"])


class ODocumentoNaoDivergeDoCodigo(unittest.TestCase):
    """Os numeros vivem no codigo. O documento explica e cita.

        UMA LEI EM DOIS SITIOS DIVERGE,
        E A PARTIR DAI NENHUMA DAS DUAS VALE.
    """

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(RAIZ, "docs", "operacao",
                               "GATE-DE-ACEITACAO-TEMATICA-V1.md"),
                  encoding="utf-8") as f:
            cls.doc = f.read()

    def test_a_tabela_do_documento_bate_com_os_limiares(self):
        esperado = {
            "POSITIVE_CAPTURE_RATE": "10/11",
            "SPECIFICITY": "18/20",
            "PRECISION_T3": "4/5",
            "DECISION_COVERAGE": "28/31",
            "GROUP_PASS_RATE": "28/31",
        }
        for metrica, fracao in esperado.items():
            self.assertIn("| %s | ≥ %s |" % (metrica, fracao), self.doc,
                          metrica)
        for metrica in ("EXPLICIT_FALSE_NEGATIVE", "ERROR",
                        "FALSE_SUBSTRING_OUTCOME_DEPENDENCY"):
            self.assertIn("| %s | = 0 |" % metrica, self.doc, metrica)

    def test_o_documento_nomeia_o_dono_e_a_versao(self):
        self.assertIn("GATE_OWNER  = %s" % g.GATE_OWNER, self.doc)
        self.assertIn("GATE_VERSION = %s" % g.GATE_VERSION, self.doc)

    def test_o_documento_nao_e_o_dono_dos_numeros(self):
        self.assertIn("Os números vivem no código", self.doc)

    def test_o_documento_publica_o_veredicto_do_baseline(self):
        self.assertIn("CURRENT_ADMISSION_GATE_RESULT = FAIL", self.doc)
        self.assertIn("ADMISSION_CHANGED = NO", self.doc)

    def test_a_decisao_esta_no_diario(self):
        with open(os.path.join(RAIZ, "docs", "decisoes",
                               "DIARIO-DE-DECISOES.md"), encoding="utf-8") as f:
            diario = f.read()
        self.assertIn("D-040", diario)
        self.assertIn("BIBLE_CHANGE_REQUIRED    = NO", diario)
        self.assertIn("CONTRACT_CHANGE_REQUIRED = YES", diario)


class AProvaDeMutacaoMordeMesmo(unittest.TestCase):
    """Quem guarda o guarda.

    A prova de mutacao anuncia SURVIVORS = 0. Esse numero so vale se cada
    mutante tiver mesmo sido aplicado — e uma ancora que deixou de existir num
    refactor produz exactamente o oposto: nenhuma mutacao acontece, nada falha,
    e o relatorio diz zero sobreviventes com toda a confianca.

        UM MUTANTE QUE NAO SE APLICA
        E INDISTINGUIVEL DE UM MUTANTE QUE MORREU.

    Esta suite nao corre a mutacao (isso demora e seria recursivo): verifica o
    que a mutacao precisa para ser verdadeira.
    """

    @classmethod
    def setUpClass(cls):
        # Enquanto a prova de mutacao corre, o ficheiro do dono ESTA alterado
        # de proposito. Estas verificacoes falhariam todas — e matariam todos
        # os mutantes por contabilidade, e nao por o gate ter mudado. Isso
        # daria SURVIVORS = 0 sem provar nada sobre o gate.
        if os.environ.get("SINTONIA_MUTACAO_EM_CURSO"):
            raise unittest.SkipTest(
                "a arvore esta mutada de proposito; estas guardas defendem a "
                "arvore commitada")
        _s = importlib.util.spec_from_file_location(
            "mut_t", os.path.join(RAIZ, "provas", "mutacao_do_gate.py"))
        cls.m = importlib.util.module_from_spec(_s)
        _s.loader.exec_module(cls.m)
        with open(os.path.join(RAIZ, "provas",
                               "gate_de_aceitacao_tematica.py"),
                  encoding="utf-8") as f:
            cls.fonte = f.read()

    def test_cada_ancora_existe_e_e_unica_no_dono(self):
        for mut in self.m.MUTACOES:
            n = self.fonte.count(mut["ONDE"])
            self.assertEqual(n, 1,
                             "ancora de «%s» aparece %d vezes" % (mut["NOME"], n))

    def test_cada_mutacao_muda_mesmo_alguma_coisa(self):
        for mut in self.m.MUTACOES:
            self.assertNotEqual(mut["ONDE"], mut["PARA"], mut["NOME"])
            self.assertNotIn(mut["PARA"], self.fonte, mut["NOME"])

    def test_a_missao_pediu_estes_pontos_e_todos_estao_mutados(self):
        nomes = " ".join(mut["NOME"] for mut in self.m.MUTACOES)
        for pedido in ("positive capture", "false-negative max", "specificity",
                       "precision", "coverage", "group-pass", "error max",
                       "substring dependency", "reachability", "group count"):
            self.assertIn(pedido, nomes, pedido)

    def test_a_prova_de_mutacao_julga_a_suite_do_gate(self):
        self.assertEqual(self.m.SUITE, "tests.test_gate_de_aceitacao_tematica")
        self.assertTrue(self.m.DONO.endswith(g.GATE_OWNER))


class OQueEstaMissaoNaoFaz(unittest.TestCase):

    def _fonte(self):
        with open(os.path.join(RAIZ, "provas",
                               "gate_de_aceitacao_tematica.py"),
                  encoding="utf-8") as f:
            return f.read()

    def test_o_gate_nao_classifica_nem_le_documento(self):
        fonte = self._fonte()
        for proibido in ("sklearn", "torch", "transformers", "embedding",
                         "open(os.path.join(RAIZ, c[\"BODY_PATH\"]"):
            self.assertNotIn(proibido, fonte, proibido)

    def test_a_admission_nao_foi_tocada(self):
        import subprocess
        d = subprocess.run(["git", "diff", "HEAD", "--stat", "--",
                            "admissao/"], cwd=RAIZ, capture_output=True,
                           text=True).stdout.strip()
        self.assertEqual(d, "", "admissao/ nao pode mudar nesta missao")

    def test_nao_ha_segundo_gate_tematico_concorrente(self):
        """UM CONCEITO, UM DONO — e o conceito aqui e o portao TEMATICO.

        ⚠️ ESTA GUARDA RECUSOU UM FICHEIRO CERTO. Ela procurava a palavra
        `GATE` em qualquer sitio do nome e reprovou
        `COLLECTION-V1-CLOSE-GATES.json`, que mede outra coisa — o que falta
        para fechar a Collection — e nao disputa dono nenhum com o portao
        tematico.

            UM MARCADOR QUE NAO DISTINGUE A PALAVRA DO CONCEITO
            PROTEGE UM DONO E ATROPELA OS VIZINHOS.

        Esta casa ja teve este defeito tres vezes. Agora a guarda nomeia o que
        protege: um segundo artefato de ACEITACAO TEMATICA.
        """
        base = os.path.join(RAIZ, "data", "derivados")
        meu = os.path.basename(g.SAIDA)
        maus = [n for n in os.listdir(base)
                if n != meu
                and "TEMATIC" in n.upper()
                and ("GATE" in n.upper() or "ACEITACAO" in n.upper())]
        self.assertEqual(maus, [],
                         "nasceu um segundo dono do portao tematico")


if __name__ == "__main__":
    unittest.main()
