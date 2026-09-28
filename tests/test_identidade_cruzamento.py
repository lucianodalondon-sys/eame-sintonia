#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IDENTIDADE DO CRUZAMENTO (IDENT-v1) — o red team do LAB promovido a teste do motor (D125, §11.3 passo 6).

    python3 -m unittest tests.test_identidade_cruzamento -v
    python3 provas/_mutantes_identidade.py          # os 9 mutantes do LAB + os da D125, contra ESTES testes

De onde vem: docs/lab/identidade-cruzamento/redteam_identidade.py (origin/claude/stable-crossing-identity-onfwdu
@dccb0ec). La os 17 casos corriam contra uma COPIA da regra com o vocabulario v0 de ~12 entradas; aqui correm
contra o CODIGO do motor (motor/identidade_do_cruzamento.py) e o vocabulario unico v1 (motor/vocabulario_unico.py).
Os mutantes deixam de ser «bandeiras» dentro da regra: sao defeitos plantados no codigo real (provas/).

⚠️ Os dados sao SINTETICOS (SINT-) salvo a classe R7_Real, que le os insumos commitados do repo.
"""
import json
import os
import sys
import unittest
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import identidade_do_cruzamento as IDENT   # noqa: E402
import vocabulario_unico as VOCAB          # noqa: E402
import cruzamentos_max as XM               # noqa: E402
import corrida_da_inteligencia as CI       # noqa: E402
from tests.test_cruzamentos_max import referencia, cruzamento   # noqa: E402

F1, F2, F4, F5 = IDENT.F1, IDENT.F2, IDENT.F4, IDENT.F5
NAO_SEI = IDENT.NAO_SEI


def xid(familia, slots, doc):
    return IDENT.crossing_id(IDENT.crossing_key(familia, slots, doc))


def janela(txt_lugar, ft, doc, alvo="mosca dell'olivo"):
    return xid(F4, {"CROP": VOCAB.cultura("olivo"), "TARGET": VOCAB.praga(alvo), "LUGAR": VOCAB.lugar(txt_lugar),
                    "CAMPANHA": IDENT.campanha(ft)}, doc)


FOLPET_VITE = {"JURISDICAO": "IT", "AI": IDENT.slot_ai("folpet"), "CROP": VOCAB.cultura("vite")}


class RT_RedTeam(unittest.TestCase):
    """Os 17 casos do red team (IDENTIDADE-CRUZAMENTO §9), contra o codigo real."""

    def test_RT01_lugares_diferentes_nao_juntam(self):
        self.assertNotEqual(janela("Puglia ; Lecce", "2026-09-07/2026-09-13", "d1"),
                            janela("Puglia ; Brindisi", "2026-09-07/2026-09-13", "d2"))

    def test_RT02_niveis_diferentes_nao_juntam(self):
        self.assertNotEqual(janela("Puglia ; Lecce", "2026-09-10", "d1"), janela("Puglia", "2026-09-10", "d2"))

    def test_RT03_lugar_nao_resolvido_nao_junta(self):
        self.assertIsNone(VOCAB.lugar("zona costiera"))
        self.assertNotEqual(janela("zona costiera", "2026-09-10", "d1"), janela("zona costiera", "2026-09-10", "d2"))

    def test_RT04_nao_sei_nao_e_igual_a_nao_sei(self):
        a = xid(F1, {"JURISDICAO": "IT", "AI": "AI:TAUFLUVALINATE", "CROP": None}, "ARIF:SETTIMANALE:2026:N37")
        b = xid(F1, {"JURISDICAO": "IT", "AI": "AI:TAUFLUVALINATE", "CROP": None}, "ARIF:SETTIMANALE:2026:N38")
        self.assertNotEqual(a, b)

    def test_RT05_cultura_generica_nao_vira_especifica(self):
        self.assertEqual(VOCAB.cultura("drupacee"), "CROP_GRUPO:DRUPACEE")
        self.assertNotEqual(xid(F2, {"JURISDICAO": "IT", "CROP": VOCAB.cultura("drupacee"),
                                     "TARGET": VOCAB.praga("ceratitis capitata")}, "d1"),
                            xid(F2, {"JURISDICAO": "IT", "CROP": VOCAB.cultura("pesco"),
                                     "TARGET": VOCAB.praga("ceratitis capitata")}, "d2"))
        # e a chave do leitor que junta varias culturas nao junta na identidade
        self.assertNotEqual(VOCAB.cultura("melone"), VOCAB.cultura("zucchina"))
        self.assertNotEqual(VOCAB.cultura("pomacee"), VOCAB.cultura("melo"))

    def test_RT06_praga_de_nome_parecido_nao_junta(self):
        self.assertNotEqual(VOCAB.praga("mosca dell'olivo"), VOCAB.praga("mosca della frutta"))
        self.assertIsNone(VOCAB.praga("mosca"))

    def test_RT07_sinonimos_juntam(self):
        self.assertEqual(len({janela("Puglia ; Lecce", "2026-09-10", "d%d" % i, alvo=a) for i, a in
                              enumerate(["bactrocera oleae", "mosca delle olive", "Mosca dell’olivo"])}), 1)

    def test_RT08_grafias_da_mesma_substancia_juntam(self):
        self.assertEqual(IDENT.slot_ai("TAU-FLUVALINATE"), IDENT.slot_ai("tau fluvalinate"))

    def test_RT09_substancias_parecidas_nao_juntam(self):
        self.assertNotEqual(IDENT.slot_ai("metalaxyl"), IDENT.slot_ai("metalaxyl-m"))

    def test_RT10_edicao_nova_da_bula_nao_cria_pergunta(self):
        self.assertEqual(xid(F1, dict(FOLPET_VITE, _EDICAO="MINSALUTE_20260907"), "d1"),
                         xid(F1, dict(FOLPET_VITE, _EDICAO="MINSALUTE_20261007"), "d1"))
        self.assertNotIn("EDICAO", IDENT.crossing_key(F1, dict(FOLPET_VITE, _EDICAO="X"), "d1"))

    def test_RT11_setembro_e_outubro_na_F1_sao_a_mesma_pergunta(self):
        self.assertEqual(xid(F1, FOLPET_VITE, "boletim-set"), xid(F1, FOLPET_VITE, "boletim-out"))

    def test_RT12_campanhas_diferentes_sao_episodios_diferentes(self):
        self.assertNotEqual(janela("Lecce", "2026-09-10", "d1"), janela("Lecce", "2027-09-10", "d2"))

    def test_RT13_publicacao_nao_e_fact_time(self):
        self.assertIsNone(IDENT.campanha(None))
        self.assertIsNone(IDENT.campanha(NAO_SEI))
        self.assertNotEqual(janela("Lecce", None, "d1"), janela("Lecce", "2026-09-10", "d2"))

    def test_RT14_previsao_e_facto_nunca_juntam(self):
        self.assertNotEqual(xid(F5, {"TARGET": VOCAB.praga("mosca dell'olivo"), "LUGAR": VOCAB.lugar("Lecce"),
                                     "HORIZONTE": "2026"}, "d1"), janela("Lecce", "2026-09-10", "d1"))

    def test_RT15_o_mesmo_boletim_2x_e_1_evidencia(self):
        dois = [{"ITEM_ID": "a", "raw_sha256": "f" * 64, "ORIGINADOR": "REG-CAMPANIA", "SOURCE_ID": "IT-T3-002"},
                {"ITEM_ID": "b", "raw_sha256": "f" * 64, "ORIGINADOR": "REG-CAMPANIA", "SOURCE_ID": "IT-T3-002"}]
        self.assertEqual(len({IDENT.evidencia(p) for p in dois}), 1)
        c = IDENT.contar_provas(dois)
        self.assertEqual((c["N_LINKS"], c["N_EVIDENCIAS_DOCUMENTO"], c["N_ORIGINADORES"]), (2, 1, 1))

    def test_RT16_tres_distritos_da_mesma_instituicao_sao_1_fonte(self):
        tres = [{"ITEM_ID": str(i), "raw_sha256": str(i) * 64, "ORIGINADOR": "REG-TOSCANA",
                 "SOURCE_ID": "IT-T3-0%d" % i} for i in (1, 2, 3)]
        c = IDENT.contar_provas(tres)
        self.assertEqual((c["N_EVIDENCIAS_DOCUMENTO"], c["N_ORIGINADORES"]), (3, 1))

    def test_RT17_tratar_nao_tratar_da_mesma_origem_e_temporal_change(self):
        a = {"estado": "NO", "originador": "ARIF", "periodo": "n.38"}
        self.assertEqual(IDENT.relacao(a, {"estado": "YES", "originador": "ARIF", "periodo": "n.39"}),
                         IDENT.TEMPORAL_CHANGE)
        self.assertEqual(IDENT.relacao(a, {"estado": "YES", "originador": "APOL", "periodo": "n.38"}),
                         IDENT.DIVERGENT)


class P_DefeitosDaPOC(unittest.TestCase):
    """Os 2 defeitos que a nuvem achou na POC do LAB (IDENTIDADE-CRUZAMENTO §3) — corrigidos e presos."""

    def test_P1_temporal_change_nao_e_conflitante(self):
        e = IDENT.estado_vigente([{"estado": "NO", "originador": "ARIF", "periodo": "2026-W38"},
                                  {"estado": "YES", "originador": "ARIF", "periodo": "2026-W39"}])
        self.assertEqual(e["ESTADO"], "YES")                    # o vigente e o da prova mais recente
        self.assertEqual(e["RELACAO"], IDENT.TEMPORAL_CHANGE)
        self.assertEqual(e["CONTRADICAO"], "NENHUMA")
        self.assertEqual(e["HISTORICO"][0]["DE"], "NO")         # o anterior fica no historico
        self.assertNotIn("CONFLITANTE", json.dumps(e))

    def test_P1b_origens_diferentes_ficam_abertas_e_nao_se_escolhe(self):
        e = IDENT.estado_vigente([{"estado": "NO", "originador": "ARIF", "periodo": "2026-W38"},
                                  {"estado": "YES", "originador": "APOL", "periodo": "2026-W38"}])
        self.assertEqual((e["ESTADO"], e["RELACAO"], e["CONTRADICAO"]), (NAO_SEI, IDENT.DIVERGENT, "UNRESOLVED"))

    def test_P2_F1_resposta_e_do_rotulo_nao_do_melhor_link(self):
        ref = referencia()
        a = cruzamento("TAUFLUVALINATE", ["SINT-TAU"], ["vite"], "BOLLETTINO FITOSANITARIO VITE: tau-fluvalinate",
                       estado=XM.YES_A_CONFIRMAR, x3h=["vite"], oid="SINT-A")
        b = dict(cruzamento("TAUFLUVALINATE", ["SINT-TAU"], ["vite"], "nada de cabecalho aqui: tau-fluvalinate",
                            estado=XM.YES_A_CONFIRMAR, x3h=["vite"], oid="SINT-B", raw=78),
                 URL="https://sint.example/outro", SALA_CHAVE="SINT-RUN#1")
        itens = XM.itens_do_pote(XM.analisar({"CROSSINGS": [a, b], "CORTE_VERTICAL": {"ITENS": []}}, ref), ref)
        f1 = [c for c in itens["portfolio"] if c.get("FAMILIA") == F1]
        self.assertEqual(len(f1), 1, "dois boletins da mesma pergunta = UM cartao")
        c = f1[0]
        self.assertEqual(c["RESPOSTA_DITA_POR"], "ROTULO")
        self.assertEqual(c["RESPOSTA"], XM.avaliar_rotulo("TAUFLUVALINATE", "vite", ref)["RESPOSTA"])
        self.assertEqual(len(c["LINKS"]), 2)
        self.assertEqual(len(c["ALIAS"]), 2, "os dois XMAX- antigos viram ALIAS, nenhum apagado")
        estados = {l["ESTADO_DO_LINK"] for l in c["LINKS"]}
        self.assertEqual(len(estados), 2, "a qualidade de cada link fica NO link, os dois a vista")

    def test_P2b_rotulo_que_nao_foi_lido_nao_vira_nao(self):
        ref = referencia()
        self.assertEqual(XM.avaliar_rotulo("TAUFLUVALINATE", None, ref)["RESPOSTA"], NAO_SEI)
        self.assertEqual(XM.avaliar_rotulo("SUBSTANCIA-QUE-NAO-EXISTE", "vite", ref)["RESPOSTA"], NAO_SEI)


class S_SinalEFuturoSemRun(unittest.TestCase):
    """§11.3 passo 2: SG2/FUT2 nao dependem da corrida; o ID antigo vai para ALIAS."""

    P = "o sinal sobrevive a corrida seguinte?"

    @staticmethod
    def item(ref, url, sha, sid):
        return {"MARCA": "SINTETICO", "ITEM_ID": url, "RAW_OBSERVATION_ID": ref, "SOURCE_ID": sid,
                "FACT_TIME": "2026-09-20", "TEXTO_SHA256": sha, "DOCUMENT_ID": "SINT-DOC-" + ref,
                "FACT_TIME_BASIS": "SINTETICO · ESCRITO_NO_TEXTO · DATE_EXACT",
                "CAPTURED_AT": "2026-09-25T10:00:00Z", "FATO": "NAO_SE_APLICA"}

    def test_S1_o_mesmo_item_tem_o_mesmo_SG2_em_duas_corridas(self):
        a, b, c = (self.item("O%d" % i, "https://x.it/%d" % i, "s%d" % i, "IT-T3-%d" % i) for i in (1, 2, 3))
        l1 = CI.correr(self.P, [a, b])
        l2 = CI.correr(self.P, [c, a, b])          # outra corrida (outro RUN_ID), outra posicao
        self.assertNotEqual(l1["INTELLIGENCE_RUN_ID"], l2["INTELLIGENCE_RUN_ID"])
        s1 = {s["RAW_OBSERVATION_ID"]: s for s in l1["SIGNALS"]}
        s2 = {s["RAW_OBSERVATION_ID"]: s for s in l2["SIGNALS"]}
        for r in ("O1", "O2"):
            self.assertEqual(s1[r]["SIGNAL_ID"], s2[r]["SIGNAL_ID"])
            self.assertTrue(s1[r]["SIGNAL_ID"].startswith("SG2-"))
            self.assertTrue(s1[r]["ALIAS"][0].startswith("SG-"))       # o antigo nao some
            self.assertNotEqual(s1[r]["ALIAS"], s2[r]["ALIAS"])         # e era ele que rodava

    def test_S2_a_mesma_observacao_lida_2x_continua_com_nome_proprio(self):
        a = self.item("O1", "https://x.it/1", "s", "IT-T3-1")
        b = dict(a, ITEM_ID="https://x.it/1-bis")
        l = CI.correr(self.P, [a, b])
        ids = [s["SIGNAL_ID"] for s in l["SIGNALS"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_S3_FUT2_sem_run(self):
        self.assertEqual(IDENT.fut2_id("ISSUE:X", "Napoli", "2026-11", "DOC:a", 1),
                         IDENT.fut2_id("ISSUE:X", "Napoli", "2026-11", "DOC:b", 2))
        self.assertNotEqual(IDENT.fut2_id(None, "Napoli", "2026-11", "DOC:a", 1),
                            IDENT.fut2_id(None, "Napoli", "2026-11", "DOC:b", 1))


class V_Vocabulario(unittest.TestCase):
    def test_V1_versao_e_impressao(self):
        self.assertTrue(VOCAB.carimbo().startswith("VOCAB-v1@"))
        t = VOCAB.termos()
        self.assertIn("PEST:MOSCA_OLIVO", t)
        self.assertIn("bactrocera\\s+oleae", " ".join(t["PEST:MOSCA_OLIVO"]["ALIASES"]))
        self.assertIn("PLACE:IT-PROV:LECCE", t)

    def test_V2_nenhum_termo_inventado(self):
        """Todo codigo nasce de uma lista do repo (a ORIGEM diz qual)."""
        for cod, e in VOCAB.termos().items():
            self.assertTrue(e["ORIGEM"].startswith(("leis/", "motor/")), cod)
            self.assertTrue(e["ALIASES"], cod)


class R7_Real(unittest.TestCase):
    """Os insumos commitados: docs/intelligence/r7/CRUZAMENTOS-MAX-ITENS-DO-POTE.json (regerado nesta missao)."""

    @classmethod
    def setUpClass(cls):
        with open(XM.SAIDA_ITENS, encoding="utf-8") as f:
            cls.itens = json.load(f)["ITENS_POR_FERRAMENTA"]["portfolio"]

    def test_R1_um_cartao_por_pergunta_e_nenhum_id_repetido(self):
        ids = [c["OBJETO_ID"] for c in self.itens]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(i.startswith("XQ-") for i in ids))
        self.assertEqual(len(self.itens), 83)                       # eram 96 objetos por link

    def test_R2_olivo_x_mosca_13_para_1(self):
        k = "F2_PORTFOLIO_MATCH/v1|JURISDICAO=IT|CROP=CROP:OLIVO|TARGET=PEST:MOSCA_OLIVO"
        c = [x for x in self.itens if x["CROSSING_KEY"] == k]
        self.assertEqual(len(c), 1)
        self.assertEqual(len(c[0]["LINKS"]), 13)
        self.assertEqual(c[0]["CONTAGENS"]["N_EVIDENCIAS_DOCUMENTO"], 13)

    def test_R3_os_ids_antigos_sao_alias_e_nenhum_se_perde(self):
        with open(os.path.join(RAIZ, "provas", "potes_um_cartao", "ITENS-XMAX-ANTES-b273660.json"), encoding="utf-8") as f:
            antes = {o["OBJETO_ID"] for o in json.load(f)["ITENS_POR_FERRAMENTA"]["portfolio"]}
        alias = [a for c in self.itens for a in c["ALIAS"]]
        self.assertEqual(len(alias), len(set(alias)))
        self.assertEqual(set(alias), antes)                        # 96 XMAX- -> ALIAS, nenhum apagado

    def test_R4_folpet_vite_2_para_1_com_os_dois_estados_no_link(self):
        c = [x for x in self.itens if x["CROSSING_KEY"].endswith("AI=AI:FOLPET|CROP=CROP:VITE")]
        self.assertEqual(len(c), 1)
        self.assertEqual(sorted(l["ESTADO_DO_LINK"] for l in c[0]["LINKS"]),
                         ["POSSIBLE_ANSWER_YES_A_CONFIRMAR", "UNRESOLVED"])
        self.assertEqual(c[0]["RESPOSTA_DITA_POR"], "ROTULO")


if __name__ == "__main__":
    unittest.main()
