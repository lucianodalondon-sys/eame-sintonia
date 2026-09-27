#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LOTE6-INTEGRA — os PONTOS DE JUNCAO das quatro entregas de 27/09, atacados.

    python3 -m unittest tests.test_lote6_integra -v

Cada entrega passava sozinha. O que so existe depois do merge e o sitio onde
elas se tocam, e e isso que este ficheiro prende:

  J1  o gold da Puglia tem UMA copia (a selada), e o harness do extrator le-a;
  J2  o extrator por secao (boletim-por-secao) fala o vocabulario da lei D112
      (metodo-puglia) — lido do dono, nao copiado;
  J3  as travas da lei (COL-LAW-221 / COL-LAW-032) decidem a saida do extrator;
  J4  o extrator dos estudos (estudos-chaves) so grava ENTITY_SOURCE da lei;
  J5  o motor das capacidades (int-r7-caps) segue o dono do READY (D58: a
      JANELA_DECLARADA vai DENTRO do READY), e a copia das capacidades leva a
      janela ja passada pela D112a;
  J6  as relacoes do motor dizem a palavra da INT-LAW-078/079 — e a MESMA que a
      funcao da lei (`afirmacao_da_fonte.relacao`) da para o mesmo par.

⚠️ Dado SINTETICO onde nao e o gold: tests/dados/int-r7/SINTETICO-R7-SALA-EXPORT.json
(`SINTETICO: true`) e frases «[SINTETICA]». Sem rede. Sem banco.
"""
import copy
import json
import os
import sys
import unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in (RAIZ, RAIZ / "motor", RAIZ / "leis", RAIZ / "scripts" / "lugar_fato"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import _gavetas  # noqa: E402,F401
import afirmacao_da_fonte as AF                # noqa: E402
import lugar_do_fato as LF                     # noqa: E402
import boletim_do_campo as BC                  # noqa: E402
import estudo_chaves as EC                     # noqa: E402
import gold_puglia as G                        # noqa: E402
import corrida_da_inteligencia as CI           # noqa: E402
import motor_das_capacidades as M              # noqa: E402
import cap_win as WIN                          # noqa: E402

EXPORT = RAIZ / "tests" / "dados" / "int-r7" / "SINTETICO-R7-SALA-EXPORT.json"
HOJE = date(2026, 9, 27)
GARGANO = "SINT-R7-ARIF-38#1"
APOL_TA = "SINT-R7-APOL-38-TA#0"


def export():
    return json.loads(EXPORT.read_text(encoding="utf-8"))


def rodar(mexer=None):
    e = export()
    if mexer:
        mexer(e)
    return M.rodar(M.entrada_do_export(e), HOJE, "SINT-HEAD")


def rels(s, tipo):
    return [r for r in s["D112"]["RELACOES"] if r["TIPO"] == tipo]


class J1_UmGoldSo(unittest.TestCase):

    def test_a_copia_gemea_saiu_e_o_harness_le_a_selada(self):
        self.assertFalse((RAIZ / "docs" / "iab" / "puglia" / "GOLD-FIXTURE-PUGLIA-V1.json").exists())
        self.assertEqual(RAIZ / "tests" / "fixtures" / "puglia" / "GOLD-FIXTURE-PUGLIA-V1.json", G.GOLD)


class J2_OExtratorFalaALei(unittest.TestCase):

    def test_o_vocabulario_e_o_do_dono(self):
        self.assertIs(AF.ENTITY_SOURCES, BC.ENTITY_SOURCES)
        self.assertIs(LF.LOCATION_SOURCES, BC.LOCATION_SOURCES)
        self.assertEqual(LF.UNRESOLVED, BC.UNRESOLVED)


class J3_AsTravasDaLeiDecidem(unittest.TestCase):

    def test_cabecalho_so_na_imagem_nunca_vira_lugar_mesmo_que_o_extrator_o_proponha(self):
        r = BC._trava_do_lugar({"VALOR": "Bari", "LOCATION_SOURCE": BC.VISUAL_HEADER_CANDIDATE})
        self.assertEqual(LF.UNRESOLVED, r["VALOR"])
        self.assertIn("COL-LAW-032", r["PORQUE"])

    def test_fonte_fora_do_vocabulario_nao_sustenta(self):
        r = BC._trava_do_lugar({"VALOR": "Bari", "LOCATION_SOURCE": "DEDUZIDO_DO_LAYOUT"})
        self.assertEqual(LF.UNRESOLVED, r["VALOR"])

    def test_cabecalho_escrito_e_texto_sustentam(self):
        for fonte in (BC.SECTION_HEADER, BC.TEXT):
            self.assertEqual("Bari", BC._trava_do_lugar({"VALOR": "Bari", "LOCATION_SOURCE": fonte})["VALOR"])

    def test_span_sem_nome_no_trecho_vira_unknown(self):
        r = BC._trava_da_entidade({"VALOR": ["xylella"], "ENTITY_SOURCE": BC.SPAN}, False)
        self.assertEqual((BC.UNKNOWN, BC.UNKNOWN), (r["VALOR"], r["ENTITY_SOURCE"]))
        self.assertIn("COL-LAW-221", r["MOTIVO"])

    def test_herdada_com_o_nome_no_trecho_vira_unknown(self):
        r = BC._trava_da_entidade({"VALOR": ["xylella"], "ENTITY_SOURCE": BC.SECTION_TITLE}, True)
        self.assertEqual(BC.UNKNOWN, r["ENTITY_SOURCE"])

    def test_a_trava_nao_promove(self):
        ok = {"VALOR": ["xylella"], "ENTITY_SOURCE": BC.SPAN, "PROVA": "no trecho"}
        self.assertEqual(ok, BC._trava_da_entidade(dict(ok), True))


class J4_OEstudoGravaSoPalavrasDaLei(unittest.TestCase):

    def test_sem_trecho_e_unknown_e_com_trecho_e_span(self):
        vazio = EC.chaves_do_estudo("[SINTETICA] Un testo senza nomi.")
        cheio = EC.chaves_do_estudo("[SINTETICA] Field trials in Apulia on olive against Bactrocera oleae.")
        for k in ("CULTURA", "PROBLEMA", "REGIAO_DO_FATO"):
            self.assertEqual(EC.AUSENCIA, vazio[k]["VALOR"], k)
            self.assertEqual("UNKNOWN", vazio[k]["ENTITY_SOURCE"], k)
            self.assertIn(vazio[k]["ENTITY_SOURCE"], AF.ENTITY_SOURCES)
            self.assertIn(cheio[k]["ENTITY_SOURCE"], AF.ENTITY_SOURCES)
        self.assertEqual("SPAN", cheio["CULTURA"]["ENTITY_SOURCE"])


class J5_OMotorSegueODonoDoREADY(unittest.TestCase):

    def test_o_ready_e_exactamente_o_do_dono_e_leva_a_janela_dentro(self):
        e = M.entrada_do_export(export())
        for r in e["ITENS"]:
            self.assertEqual({"READY"}, set(r))
            self.assertEqual(set(CI.CAMPOS_DO_READY), set(r["READY"]))
            self.assertIn("JANELA_DECLARADA", CI.CAMPOS_DO_READY)

    def test_a_copia_das_capacidades_leva_a_janela_ja_passada_pela_d112a(self):
        e = M.entrada_do_export(export())
        (r,) = [x for x in e["ITENS"] if x["READY"]["ITEM_ID"] == GARGANO]
        original = copy.deepcopy(r)
        rc, jd, rel = M.aplicar_d112_lugar(r)
        self.assertFalse(rel["JANELA_DECLARADA." + WIN.CHAVE_DA_SUBAREA]["SUSTENTADO"])
        self.assertEqual(M.NAO_SEI, rc["JANELA_DECLARADA"][WIN.CHAVE_DA_SUBAREA]["VALOR"])
        self.assertEqual(jd, rc["JANELA_DECLARADA"])
        self.assertEqual(original, r, "o READY original nao muda")


class J6_AsRelacoesFalamALei(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.s = rodar()

    def test_toda_relacao_diz_a_palavra_da_lei(self):
        rs = self.s["D112"]["RELACOES"]
        self.assertEqual({M.MESMA_REDACAO, M.DIVERGENT, M.TEMPORAL_CHANGE}, {r["TIPO"] for r in rs})
        for r in rs:
            self.assertIn(r["RELATION"], AF.RELACOES, r["TIPO"])
            self.assertIn(r["CONTRADICTION_STATUS"], AF.CONTRADICTION_STATUS, r["TIPO"])

    def test_mesma_redacao_numa_casa_e_a_078_como_a_lei_a_calcula(self):
        (r,) = rels(self.s, M.MESMA_REDACAO)
        (casa,) = r["POR_INSTITUICAO"]
        t1, t2 = casa["TERRITORIOS"][:2]
        a = {"PUBLISHER": casa["INSTITUICAO"], "SPAN_SHA256": r["DA_FONTE"]["REDACAO"], "TERRITORIO": t1,
             "VALOR": r["DA_FONTE"]["REDACAO"]}
        lei = AF.relacao(a, dict(a, TERRITORIO=t2))
        self.assertEqual(lei["RELATION"], r["RELATION"])
        self.assertEqual(lei["CONTRADICTION_STATUS"], r["CONTRADICTION_STATUS"])

    def test_limites_de_casas_diferentes_sao_a_079_como_a_lei_a_calcula(self):
        (r,) = rels(self.s, M.DIVERGENT)
        g1, g2 = r["DA_FONTE"]
        a = {"PUBLISHER": g1["INSTITUICOES"][0], "SPAN_SHA256": "a", "VALOR": g1["LIMITE"]}
        b = {"PUBLISHER": g2["INSTITUICOES"][0], "SPAN_SHA256": "b", "VALOR": g2["LIMITE"]}
        lei = AF.relacao(a, b)
        self.assertEqual(lei["RELATION"], r["RELATION"])
        self.assertEqual(lei["CONTRADICTION_STATUS"], r["CONTRADICTION_STATUS"])

    def test_mudanca_no_tempo_e_a_079_e_nao_prova_o_campo(self):
        (r,) = rels(self.s, M.TEMPORAL_CHANGE)

        def afirmacao(lado, sha):
            d = r["DA_FONTE"][lado]
            return {"PUBLISHER": r["INSTITUICAO"], "SPAN_SHA256": sha,
                    "VALIDADE": json.dumps(d["TIME_WINDOW"], sort_keys=True),
                    "VALOR": json.dumps({k: v for k, v in d.items() if k != "TIME_WINDOW"}, sort_keys=True)}
        a, b = afirmacao("ANTES", "a"), afirmacao("DEPOIS", "b")
        lei = AF.relacao(a, b)
        self.assertEqual(lei["RELATION"], r["RELATION"])
        self.assertEqual(lei["CONTRADICTION_STATUS"], r["CONTRADICTION_STATUS"])
        self.assertIs(False, r["CONCLUIR_MUDANCA_DO_CAMPO"])

    def test_mesma_redacao_em_casas_diferentes_a_lei_nao_qualifica(self):
        def outra_casa(e):
            for l in e["LINHAS"]:
                if l["item_id"] == APOL_TA:
                    l["source_id"] = "SINT-OUTRA-CASA"
        (r,) = rels(rodar(outra_casa), M.MESMA_REDACAO)
        self.assertEqual(2, r["INSTITUICOES"])
        self.assertEqual(("NAO_SEI", "UNRESOLVED"), (r["RELATION"], r["CONTRADICTION_STATUS"]))

    def test_limites_diferentes_na_mesma_casa_nao_sao_divergent_recommendations(self):
        (r,) = rels(self.s, M.DIVERGENT)
        casa = r["DA_FONTE"][0]["INSTITUICOES"][0]

        def mesma_casa(e):
            outras = {g["INSTITUICOES"][0] for g in r["DA_FONTE"]} - {casa}
            for l in e["LINHAS"]:
                if l["source_id"] in outras:
                    l["source_id"] = casa
        (r2,) = rels(rodar(mesma_casa), M.DIVERGENT)
        self.assertEqual(("NAO_SEI", "UNRESOLVED"), (r2["RELATION"], r2["CONTRADICTION_STATUS"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
