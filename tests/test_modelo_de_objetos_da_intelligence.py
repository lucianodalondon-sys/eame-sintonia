#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O MODELO DE OBJETOS DA INTELLIGENCE, ATACADO — C-INT-OBJECT-MODEL-01.

    python3 -m unittest tests.test_modelo_de_objetos_da_intelligence -v

O que estas provas guardam: que nenhuma coisa da Intelligence consegue subir um
degrau que ninguem lhe autorizou, e que nenhum ecra consegue ganhar um conceito.

O que elas NAO provam: que a Intelligence funciona.

    INTELLIGENCE_RUNTIME_IMPLEMENTED = NO.

O modelo e DECLARADO. Estas provas medem se ele se sustenta e se resiste aos
trinta ataques conhecidos — nao se ha codigo a obedecer-lhe, porque nao ha
codigo. Confundir as duas coisas era o defeito que esta casa ja apanhou cinco
vezes: uma medicao certa lida contra a fotografia errada.
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "provas"))

import modelo_de_objetos_da_intelligence as M          # noqa: E402

MODELO = M.carregar()


def proibida(de, para):
    return M.pode_transitar(MODELO, de, para)[0] == "FORBIDDEN"


def objeto(nome):
    return MODELO["OBJETOS"][nome]


# ══════════════════════════════════════════════════════════════════════════════
class I_OsInvariantesQueNaoSeNegoceiam(unittest.TestCase):
    """§49 · os invariantes, guardados um a um."""

    def test_I0_a_declaracao_sustenta_se(self):
        self.assertEqual(M.incoerencias(MODELO), [])

    def test_I1_cada_objeto_tem_exatamente_um_dono(self):
        for nome, o in MODELO["OBJETOS"].items():
            with self.subTest(objeto=nome):
                self.assertTrue(o["OWNER"], f"{nome} sem dono")
                self.assertNotIn(",", o["OWNER"], "dois donos nao e um dono")

    def test_I2_signal_crossing_hipotese_e_finding_sao_quatro_objetos(self):
        quatro = ["SIGNAL", "CROSSING", "ANALYTIC_HYPOTHESIS",
                  "FINDING / ANALYTIC_JUDGMENT"]
        for n in quatro:
            self.assertIn(n, MODELO["OBJETOS"])
        self.assertEqual(len({MODELO["OBJETOS"][n]["RESPONDE_A_PERGUNTA"]
                              for n in quatro}), 4,
                         "quatro objetos que respondem a mesma pergunta sao um so")

    def test_I3_finding_nao_e_opportunity_nem_recommendation(self):
        self.assertEqual(M.especie(MODELO, "FINDING / ANALYTIC_JUDGMENT"), "ENTITY")
        self.assertEqual(M.especie(MODELO, "OPPORTUNITY"), "ENTITY")
        self.assertEqual(M.especie(MODELO, "ANALYTIC_RECOMMENDATION"), "OUTPUT")
        self.assertNotEqual(objeto("OPPORTUNITY")["RESPONDE_A_PERGUNTA"],
                            objeto("ANALYTIC_RECOMMENDATION")["RESPONDE_A_PERGUNTA"])

    def test_I4_o_item_admitido_e_da_collection(self):
        o = objeto("SOURCE_FACT / READY_ITEM")
        self.assertEqual(o["OWNER"], "COLLECTION")
        self.assertEqual(o["ESPECIE"], "EXTERNAL_REFERENCE")

    def test_I5_o_requisito_nao_nomeia_rota_coletor_nem_executor(self):
        o = objeto("INTELLIGENCE_REQUIREMENT")
        nunca = " ".join(o["NUNCA_E"]).upper()
        for palavra in ("ROTA", "COLETOR", "URL", "EXECUTOR"):
            self.assertIn(palavra, nunca)
        entrada = " ".join(o["ENTRADA_MINIMA"]).upper()
        for palavra in ("ROTA", "COLETOR", "EXECUTOR", "SCRAPER", "ENDPOINT"):
            self.assertNotIn(palavra, entrada,
                             "o requisito nao pode PEDIR o que nao lhe pertence")

    def test_I6_o_portal_nao_possui_nenhum_conceito(self):
        for nome, o in MODELO["OBJETOS"].items():
            with self.subTest(objeto=nome):
                up = str(o["OWNER"]).upper()
                for proibido in M.DONOS_PROIBIDOS:
                    self.assertNotIn(proibido, up)

    def test_I7_so_uma_ferramenta_escreve_e_so_um_campo(self):
        escrevem = {n: f["WRITES"] for n, f in MODELO["FERRAMENTAS"].items()
                    if "nada" not in " ".join(f["WRITES"]).lower()}
        self.assertEqual(list(escrevem), ["VALIDATION"], escrevem)
        self.assertIn("VALIDATION_STATE", " ".join(escrevem["VALIDATION"]))

    def test_I8_toda_transicao_permitida_tem_portao_ou_razao(self):
        for t in MODELO["TRANSICOES_PERMITIDAS"]:
            with self.subTest(t=f"{t['FROM']}->{t['TO']}"):
                self.assertTrue(t["PORQUE"])

    def test_I10_os_ataques_conhecidos_continuam_NOMEADOS(self):
        """A prova que nasceu de uma mutacao que SOBREVIVEU.

        Apaguei a proibicao `OPPORTUNITY(A ou B) -> OPPORTUNITY(C ou D)` e os
        testes continuaram verdes — porque o mundo fechado ja devolvia
        `FORBIDDEN` sozinho. O comportamento estava salvo; a MEMORIA nao.

            UMA PROIBICAO CARREGA DUAS COISAS:
            o comportamento, que o mundo fechado ja garante,
            e a RAZAO ESCRITA, que so ela guarda.

        Perder a razao e perder porque e que alguem, um dia, quis fazer aquilo —
        e uma casa que esquece o ataque volta a discuti-lo do zero.
        """
        obrigatorias = [
            ("SOURCE_FACT / READY_ITEM", "FINDING / ANALYTIC_JUDGMENT"),
            ("SIGNAL", "FINDING / ANALYTIC_JUDGMENT"),
            ("SIGNAL", "OPPORTUNITY"),
            ("CROSSING", "FINDING / ANALYTIC_JUDGMENT"),
            ("CROSSING", "ANALYTIC_RECOMMENDATION"),
            ("ANALYTIC_HYPOTHESIS", "OPPORTUNITY"),
            ("ANALYTIC_HYPOTHESIS", "FINDING / ANALYTIC_JUDGMENT"),
            ("OPPORTUNITY", "SOURCE_FACT / READY_ITEM"),
            ("OPPORTUNITY(A ou B)", "OPPORTUNITY(C ou D)"),
            ("ANALYTIC_RECOMMENDATION", "FINDING / ANALYTIC_JUDGMENT"),
            ("ANALYTIC_RECOMMENDATION", "ACAO"),
            ("qualquer objeto", "COLETOR·ROTA·EXECUTOR"),
            ("NAO SEI", "FALSO"),
            ("NAO SEI", "ZERO"),
            ("FERRAMENTA·PORTAL", "qualquer conceito novo"),
            ("SCORE alto", "transicao proibida"),
            ("APROVACAO HUMANA", "UNKNOWN vira facto"),
            ("SAIDA DE LLM", "evidencia de fonte"),
            ("FINDING / ANALYTIC_JUDGMENT", "FINDING / ANALYTIC_JUDGMENT"),
        ]
        escritas = {(t["FROM"], t["TO"]): t for t in MODELO["TRANSICOES_PROIBIDAS"]}
        for par in obrigatorias:
            with self.subTest(transicao=f"{par[0]} -> {par[1]}"):
                self.assertIn(par, escritas,
                              "o mundo fechado ainda a proibia, e por isso "
                              "apaga-la nao reprovava nada — mas a razao "
                              "desaparecia com ela")
                self.assertTrue(escritas[par]["PORQUE"].strip())

    def test_I9_o_mundo_e_fechado(self):
        """A propriedade que faz o modelo valer: o nao-declarado e proibido."""
        v, porque = M.pode_transitar(MODELO, "SIGNAL", "ANALYTIC_RECOMMENDATION")
        self.assertEqual(v, "FORBIDDEN")
        self.assertIn("mundo e fechado", porque)


# ══════════════════════════════════════════════════════════════════════════════
class RT_OsTrintaAtaques(unittest.TestCase):
    """§48 · RT01–RT30. Cada um tem de morrer, e com razao escrita."""

    def test_RT01_signal_vira_finding_direto(self):
        self.assertTrue(proibida("SIGNAL", "FINDING / ANALYTIC_JUDGMENT"))

    def test_RT02_crossing_vira_finding_direto(self):
        self.assertTrue(proibida("CROSSING", "FINDING / ANALYTIC_JUDGMENT"))

    def test_RT03_hipotese_sem_evidencia(self):
        o = objeto("ANALYTIC_HYPOTHESIS")
        self.assertIn("O_QUE_A_DERRUBA (obrigatorio)", o["ENTRADA_MINIMA"])
        self.assertIn("APOIA_SE_EM", o["ENTRADA_MINIMA"])

    def test_RT04_finding_sem_request(self):
        g4 = next(p for p in MODELO["PORTOES"] if p["GATE"] == "G4")
        self.assertIn("linhagem ate READY_ITEM", " ".join(g4["PROOF_REQUIRED"]))

    def test_RT05_finding_sem_run(self):
        self.assertIn("INTELLIGENCE_RUN", MODELO["OBJETOS"])
        self.assertIn("FINDING", " ".join(objeto("INTELLIGENCE_RUN")["SAIDA_POSSIVEL"]))

    def test_RT06_finding_sem_lineage(self):
        self.assertIn("LINHAGEM", objeto("FINDING / ANALYTIC_JUDGMENT")["ENTRADA_MINIMA"])

    def test_RT07_finding_sem_scope(self):
        self.assertIn("SCOPE", objeto("FINDING / ANALYTIC_JUDGMENT")["ENTRADA_MINIMA"])

    def test_RT08_finding_sem_tempo(self):
        e = objeto("FINDING / ANALYTIC_JUDGMENT")["ENTRADA_MINIMA"]
        self.assertIn("TEMPO", e)
        self.assertIn("GEOGRAFIA", e)

    def test_RT09_source_location_vira_fact_location(self):
        g0 = next(p for p in MODELO["PORTOES"] if p["GATE"] == "G0")
        self.assertIn("SOURCE_LOCATION nunca serve de FACT_LOCATION", g0["HARD_GATES"])

    def test_RT10_publication_time_vira_fact_time(self):
        g0 = next(p for p in MODELO["PORTOES"] if p["GATE"] == "G0")
        self.assertIn("PUBLICATION_TIME nunca serve de FACT_TIME", g0["HARD_GATES"])

    def test_RT11_support_cria_facto(self):
        r = MODELO["RELACOES"]["SUPPORT"]
        self.assertIn("cria o objeto", r["NUNCA"])
        self.assertEqual(M.especie(MODELO, "SUPPORT"), "RELATION")

    def test_RT12_contradiction_e_descartada(self):
        r = MODELO["RELACOES"]["CONTRADICTION"]
        self.assertIn("desaparece", r["NUNCA"])
        self.assertIn("RUN_ID", r["NUNCA"])
        self.assertIn("booleano", " ".join(objeto("CONTRADICTION")["NUNCA_E"]))

    def test_RT13_duas_fontes_dependentes_contam_como_independentes(self):
        g2 = next(p for p in MODELO["PORTOES"] if p["GATE"] == "G2")
        self.assertIn("origens dependentes nao contam como independentes",
                      g2["HARD_GATES"])

    def test_RT14_reversal_apaga_finding_anterior(self):
        rev = MODELO["REVERSAO"]
        self.assertEqual(rev["ESPECIE"].split(" —")[0], "TRANSITION")
        self.assertIn("apaga o estado anterior", rev["NUNCA_FAZ"])
        self.assertIn("reescreve o julgamento passado", rev["NUNCA_FAZ"])

    def test_RT15_opportunity_vira_sales(self):
        self.assertTrue(proibida("OPPORTUNITY(A ou B)", "OPPORTUNITY(C ou D)"))
        self.assertIn("venda", " ".join(objeto("OPPORTUNITY")["NUNCA_E"]))

    def test_RT16_registo_vira_disponibilidade_comercial(self):
        d = MODELO["DOMINIOS_ITALIA"]["REGULATORY"]
        self.assertIn("disponibilidade comercial", d["FORBIDDEN_OUTPUT"])

    def test_RT17_recommendation_vira_facto(self):
        self.assertTrue(proibida("ANALYTIC_RECOMMENDATION", "FINDING / ANALYTIC_JUDGMENT"))
        self.assertTrue(proibida("ANALYTIC_RECOMMENDATION", "ACAO"))

    def test_RT18_attention_item_duplica_finding(self):
        o = objeto("ATTENTION_ITEM")
        self.assertEqual(o["ESPECIE"], "NOT_A_CONCEPT")
        self.assertEqual(o["ESTADOS"], [])
        self.assertIn("FINDING com outro nome", " ".join(o["NUNCA_E"]))

    def test_RT19_future_signal_vira_previsao_certa(self):
        o = objeto("FUTURE_SIGNAL")
        self.assertEqual(o["ESPECIE"], "PROJECTION")
        self.assertIn("uma previsao certa do futuro", o["NUNCA_E"])
        self.assertIn("HORIZONTE declarado", o["ENTRADA_MINIMA"])

    def test_RT20_validation_queue_vira_nova_entidade(self):
        self.assertEqual(M.especie(MODELO, "VALIDATION_STATE"), "STATE")
        self.assertIn("uma fila", objeto("VALIDATION_STATE")["NUNCA_E"])
        self.assertEqual(MODELO["ALIASES"]["VALIDATION_QUEUE"]["CLASSE"],
                         "DIFFERENT_CONCEPT")

    def test_RT21_portal_vira_owner(self):
        for o in MODELO["OBJETOS"].values():
            self.assertNotIn("PORTAL", str(o["OWNER"]).upper())
        self.assertIn("PORTAL NAO E DONO DE NADA",
                      " ".join(MODELO["PRINCIPIO_DAS_FERRAMENTAS"]))

    def test_RT22_ferramenta_cria_conceito_proprio(self):
        """O unico ataque com um caso MEDIDO em producao."""
        self.assertTrue(proibida("FERRAMENTA·PORTAL", "qualquer conceito novo"))
        radar = MODELO["FERRAMENTAS"]["FUTURE RADAR"]
        self.assertIn("STATUS proprio", radar["NEVER_WRITES"])
        self.assertIn("status === null", radar["PORQUE"])

    def test_RT23_score_vence_hard_gate(self):
        self.assertTrue(proibida("SCORE alto", "transicao proibida"))
        self.assertIn("HARD GATE > SCORE", MODELO["INVARIANTES"])
        g4 = next(p for p in MODELO["PORTOES"] if p["GATE"] == "G4")
        self.assertIn("score alto nao substitui prova em falta", g4["HARD_GATES"])

    def test_RT24_llm_vira_fonte_factual(self):
        self.assertTrue(proibida("SAIDA DE LLM", "evidencia de fonte"))
        self.assertEqual(MODELO["AUTONOMIA_IA"]["SER_FONTE"]["AUTORIZADO"], "NAO")
        self.assertEqual(MODELO["AUTONOMIA_IA"]["PROMOTE_FINDING"]["AUTORIZADO"], "NAO")

    def test_RT25_aprovacao_humana_apaga_unknown(self):
        self.assertTrue(proibida("APROVACAO HUMANA", "UNKNOWN vira facto"))
        g4 = next(p for p in MODELO["PORTOES"] if p["GATE"] == "G4")
        self.assertIn("aprovacao humana nao converte UNKNOWN em facto",
                      g4["HARD_GATES"])

    def test_RT26_requirement_escolhe_collector(self):
        self.assertTrue(proibida("qualquer objeto", "COLETOR·ROTA·EXECUTOR"))

    def test_RT27_requirement_escolhe_rota(self):
        o = objeto("INTELLIGENCE_REQUIREMENT")
        self.assertIn("REQUIREMENT_ID", " ".join(o["SAIDA_POSSIVEL"]))
        self.assertEqual(
            M.pode_transitar(MODELO, "INTELLIGENCE_REQUIREMENT",
                             "GAP / SATISFACTION / DECISION / ROTA")[0], "ALLOWED")
        self.assertEqual(
            M.owner(MODELO, "GAP / SATISFACTION / DECISION / ROTA"), "COLLECTION")

    def test_RT28_dominio_cria_segundo_motor(self):
        """Oito dominios, uma espinha. Nenhum dominio declara portoes proprios."""
        for nome, d in MODELO["DOMINIOS_ITALIA"].items():
            with self.subTest(dominio=nome):
                self.assertNotIn("GATE", d)
                self.assertNotIn("PORTOES", d)
                self.assertTrue(d["FORBIDDEN_OUTPUT"])

    def test_RT29_alias_historico_vira_segundo_conceito(self):
        for velho, a in MODELO["ALIASES"].items():
            with self.subTest(alias=velho):
                self.assertNotIn(velho, MODELO["OBJETOS"],
                                 f"{velho} e alias E objeto ao mesmo tempo")
                self.assertTrue(a["PORQUE"])

    def test_RT30_relevance_ou_priority_nu_reaparece(self):
        for nu in ("RELEVANCE", "PRIORITY"):
            with self.subTest(nome=nu):
                self.assertNotIn(nu, MODELO["OBJETOS"])
                self.assertEqual(MODELO["ALIASES"][nu]["CANONICO"],
                                 "RETIRED_AS_OVERLOADED_NAME")


# ══════════════════════════════════════════════════════════════════════════════
class F_AFronteiraComAsOutrasFrentes(unittest.TestCase):
    """O que esta missao NAO fez, guardado por prova."""

    def test_F1_nenhum_runtime_de_intelligence_nasceu(self):
        self.assertFalse((RAIZ / "inteligencia").exists())
        espinha = (RAIZ / "provas" / "espinha_da_intelligence.py").read_text(
            encoding="utf-8")
        self.assertIn("NAO E RUNTIME PRODUTIVO", espinha)

    def test_F2_o_modelo_diz_de_si_que_nao_e_runtime(self):
        fonte = (RAIZ / "provas" / "modelo_de_objetos_da_intelligence.py").read_text(
            encoding="utf-8")
        self.assertIn("NAO E RUNTIME", fonte)
        self.assertIn("IMPLEMENTED = NO", fonte)

    def test_F3_o_modelo_nao_pediu_para_mudar_a_biblia(self):
        self.assertEqual(MODELO["BIBLE_CHANGE_REQUIRED"], "NO")

    def test_F4_a_implementacao_declarada_e_a_medida_e_nunca_melhor(self):
        """DEFINED != IMPLEMENTED != OBSERVED, conferido contra a arbitragem."""
        v3 = json.loads((RAIZ / "docs" / "intelligence" /
                         "INTELLIGENCE-CONCEPT-OWNERSHIP-V3.json").read_text(
                             encoding="utf-8"))
        for nome, o in MODELO["OBJETOS"].items():
            if nome in v3["CONCEITOS"]:
                with self.subTest(objeto=nome):
                    self.assertEqual(o["CURRENT_IMPLEMENTATION"],
                                     v3["CONCEITOS"][nome]["CURRENT_IMPLEMENTATION"])

    def test_F5_o_instrumento_corre_e_aprova(self):
        r = subprocess.run(
            [sys.executable, str(RAIZ / "provas" / "modelo_de_objetos_da_intelligence.py")],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("MODELO_DE_OBJETOS=OK", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
