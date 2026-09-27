#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRUZAMENTOS-MAX — o motor (motor/cruzamentos_max.py) e o pote do coordenador (pacote/pote_cruzamentos_max.py).

    python3 -m unittest tests.test_cruzamentos_max -v

Os casos sao SINTETICOS (ids SINT-, empresas SINT-): nenhum valor daqui e real. So os casos X* leem os
insumos reais do repo, para provar que o JSON commitado e o que o codigo produz.
"""
import copy
import json
import os
import sys
import unittest
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import cruzamentos_max as XM                 # noqa: E402
import pote_cruzamentos_max as PX            # noqa: E402
import pote_intelligence_casco as POTE       # noqa: E402
from ponte_intelligence_casco import NAO_SEI  # noqa: E402


def par(reg, prod, cult, alvo, linha, nivel="BLOCO_DA_CULTURA", culturas=""):
    return {"REGISTRATION_ID": reg, "PRODUCT": prod, "PRODUCT_ID": "SINT-" + reg, "CULTURA_CANONICA": cult,
            "ALVO_CANONICO": alvo, "CITACAO_DA_LINHA": linha, "CITACAO_DAS_CULTURAS": culturas,
            "LIGACAO_NIVEL": nivel}


def linha_cad(reg, prod, empresa, subs, reg_em="01/01/2010", fim="31/12/2030", stato="Autorizzato",
              revoca="-"):
    return {"num_registrazione": reg, "denominazione_prodotto": prod, "ragione_sociale": empresa,
            "data_registrazione": reg_em, "data_scadenza_autorizzazione": fim, "stato_amministrativo": stato,
            "sostanze_attive": subs, "importazione_parallela": "NO", "data_decorrenza_revoca": revoca}


PARES = [
    # SINT-1 (ADAMA, tau-fluvalinate): declara Pomacee e Cavoli; vite em bloco
    par("S001", "SINT-TAU", "MELO", "AFIDI", "Pomacee (melo, pero, melo cotogno e nespolo) Contro afidi ( Aphis pomi ) impiegare a 2 l/ha"),
    par("S001", "SINT-TAU", "BRASSICACEE", "AFIDI", "Cavoli (cavolfiore, cavolo cappuccio) Contro afidi ( Brevicoryne brassicae )"),
    par("S001", "SINT-TAU", "VITE", "SCAFOIDEO", "Vite (da vino e da tavola) Contro cicaline ( Scaphoideus titanus ) impiegare a 30-300 ml/hl"),
    par("S001", "SINT-TAU", "CUCURBITACEE", "AFIDI", "Zucchino Contro afidi ( Aphis gossypii ) impiegare a 0,5 l/ha"),
    # SINT-2 (ADAMA): cita «Pomacee» sem declarar os membros
    par("S002", "SINT-POM", "MELO", "AFIDI", "Pomacee Contro afidi ( Aphis pomi )"),
    # SINT-3 (ADAMA, herbicida): rotacao na zona da cultura
    par("S003", "SINT-ROT", "LEGUMINOSE", "DIGITARIA", "Digitaria sanguinalis", nivel="DECLARACAO_DE_PRODUTO",
        culturas="possono essere seminate fava, cece, trifoglio"),
    # SINT-4 (ADAMA): cultura escrita DEPOIS do alvo (fora da zona)
    par("S004", "SINT-ZONA", "CUCURBITACEE", "AFIDI", "Zucchino Contro afidi; non trattare melone in fioritura"),
    # SINT-5 (ADAMA, folpet): peronospora na vite, so por declaracao de produto
    par("S005", "SINT-FOL", "VITE", "PERONOSPORA", "Plasmopara viticola", nivel="DECLARACAO_DE_PRODUTO",
        culturas="Fungicida per vite"),
    # SINT-7 (ADAMA): o leitor pos «Cereali (orzo, frumento)» num par de COLZA
    par("S007", "SINT-CER", "COLZA", "AFIDI", "Cereali (orzo, frumento) Contro afidi ( Sitobion avenae )"),
]
POR_PRODUTO = [{"REGISTRATION_ID": r, "PRODUCT": p, "ESTADO_DA_LEITURA": e} for r, p, e in (
    ("S001", "SINT-TAU", "LIDO_POR_BLOCO"), ("S002", "SINT-POM", "LIDO"), ("S003", "SINT-ROT", "LIDO_COMO_HERBICIDA"),
    ("S004", "SINT-ZONA", "LIDO"), ("S005", "SINT-FOL", "LIDO"), ("S006", "SINT-NAOLIDO", "TABELA_NAO_LOCALIZADA"),
    ("S007", "SINT-CER", "LIDO_POR_BLOCO"))]
CADASTRO = [
    linha_cad("S001", "SINT-TAU", "ADAMA SINT S.R.L.", "TAU-FLUVALINATE"),
    linha_cad("S002", "SINT-POM", "ADAMA SINT S.R.L.", "TAU-FLUVALINATE"),
    linha_cad("S003", "SINT-ROT", "ADAMA SINT S.R.L.", "IMAZAMOX"),
    linha_cad("S004", "SINT-ZONA", "ADAMA SINT S.R.L.", "PIRIMICARB"),
    linha_cad("S005", "SINT-FOL", "ADAMA SINT S.R.L.", "FOLPET"),
    linha_cad("S006", "SINT-NAOLIDO", "ADAMA SINT S.R.L.", "FLUDIOXONIL"),
    linha_cad("C100", "SINT-CONC-A", "SINT CONCORRENTE SPA", "TAU-FLUVALINATE"),
    linha_cad("C101", "SINT-CONC-REV", "SINT CONCORRENTE SPA", "TAU-FLUVALINATE", stato="Revocato",
              revoca="01/01/2020"),
    linha_cad("C102", "SINT-CONC-VENC", "SINT OUTRA SRL", "TAU-FLUVALINATE", fim="01/01/2025", stato="Scaduto"),
    linha_cad("C103", "SINT-CONC-M", "SINT OUTRA SRL", "METALAXYL"),
    linha_cad("C104", "SINT-CONC-MM", "SINT OUTRA SRL", "FOLPET|METALAXYL-M"),
]


def referencia(pares=None, cadastro=None):
    return XM.Referencia({"PARES": pares or PARES, "POR_PRODUTO": POR_PRODUTO, "COBERTURA": "SINT 5/6"},
                         cadastro or CADASTRO, {"ITENS": [{"REGISTRATION_ID": "S001", "PRODUCT_ID": "SINT-PRD-1"}]},
                         date(2026, 9, 7))


def cruzamento(sub, produtos, culturas, troco, estado=XM.PARTIAL, x3h=None, publicado="2026-06-30",
               oid="SINT-X1", raw=77):
    return {"OBJETO_ID": oid, "VIA": "SINT", "SOURCE_ID": "SINT-SRC", "SALA_CHAVE": "SINT-RUN#0",
            "RAW_OBSERVATION_ID": raw, "URL": "https://sint.example/b", "PUBLISHED_AT": publicado,
            "SUBSTANCIA": sub, "PRODUTOS_ADAMA": produtos, "ESTADO_R7": estado,
            "FONTE": {"CULTURA_NO_READY": culturas, "TROCO_COM_A_SUBSTANCIA": [troco]},
            "INTERPRETACAO": {"ESTADO": estado, "X2_CULTURAS_QUE_CASAM": [], "X3H_CABECALHO": x3h or []}}


class A_Grao(unittest.TestCase):
    def setUp(self):
        self.ref = referencia()

    def test_A1_membro_declarado_pelo_mesmo_rotulo(self):
        como, ev = XM.cultura_no_par("pero", self.ref.pares_do_reg["S001"][0], self.ref)
        self.assertEqual(como, "MEMBRO_DECLARADO_NO_ROTULO")
        self.assertEqual(ev["GRUPO"], "pomacee")

    def test_A2_declaracao_de_outro_rotulo_nao_serve(self):
        como, motivo = XM.cultura_no_par("pero", self.ref.pares_do_reg["S002"][0], self.ref)
        self.assertIsNone(como)
        self.assertEqual(motivo, "OUTRA_CULTURA")

    def test_A3_chave_do_grupo_sem_nome_nao_prova(self):
        como, motivo = XM.cultura_no_par("melone", self.ref.pares_do_reg["S001"][3], self.ref)
        self.assertIsNone(como)
        self.assertEqual(motivo, "GRAO_NAO_PROVADO")

    def test_A4_cultura_fora_da_zona_nao_prova(self):
        como, motivo = XM.cultura_no_par("melone", self.ref.pares_do_reg["S004"][0], self.ref)
        self.assertIsNone(como)

    def test_A5_rotacao_nao_e_uso(self):
        como, motivo = XM.cultura_no_par("cece", self.ref.pares_do_reg["S003"][0], self.ref)
        self.assertEqual((como, motivo), (None, "PAR_COM_CULTURA_DE_ROTACAO"))

    def test_A6_subtipo_nao_cobre_o_generico(self):
        como, _ = XM.cultura_no_par("cavolo", self.ref.pares_do_reg["S001"][1], self.ref)
        self.assertIsNone(como)
        como, _ = XM.cultura_no_par("cavolfiore", self.ref.pares_do_reg["S001"][1], self.ref)
        self.assertIsNotNone(como)

    def test_A7_melo_cotogno_nao_e_melo_mas_melo_e(self):
        self.assertIn("melocotogno", self.ref.grao[0]["MEMBROS"])
        como, _ = XM.cultura_no_par("melo", self.ref.pares_do_reg["S001"][0], self.ref)
        self.assertIsNotNone(como)

    def test_A8_mesma_cultura_nao_e_grupo(self):
        como, _ = XM.cultura_no_par("vigneto", self.ref.pares_do_reg["S001"][2], self.ref)
        self.assertEqual(como, "MESMA_CULTURA")

    def test_A10_grupo_declarado_nao_prova_num_par_de_outra_cultura(self):
        como, motivo = XM.cultura_no_par("orzo", self.ref.pares_do_reg["S007"][0], self.ref)
        self.assertEqual((como, motivo), (None, "OUTRA_CULTURA"))

    def test_A9_tabela_de_grao_so_com_culturas(self):
        g = XM.tabela_de_grao([par("S9", "P", "FRAGOLA", "X", "piccoli frutti ( Drosophila suzukii ) Contro")])
        self.assertEqual(g, [])


class B_Refazer(unittest.TestCase):
    def setUp(self):
        self.ref = referencia()

    def test_B1_partial_continua_partial_sem_ligacao_no_texto(self):
        c = cruzamento("TAUFLUVALINATE", ["SINT-TAU"], ["vite", "olivo"], "Situazione fenologica: nulla")
        r = XM.refazer(c, self.ref)
        self.assertEqual(r["DEPOIS"], XM.PARTIAL)
        self.assertIn("vite", r["COBERTAS_COM_GRAO"])

    def test_B2_ligacao_no_troco_vira_yes_a_confirmar(self):
        c = cruzamento("TAUFLUVALINATE", ["SINT-TAU"], ["vite", "olivo"], "Vite: intervenire con tau-fluvalinate")
        self.assertEqual(XM.refazer(c, self.ref)["DEPOIS"], XM.YES_A_CONFIRMAR)

    def test_B3_ligacao_a_cultura_ausente_do_rotulo_lido_vira_no(self):
        c = cruzamento("TAUFLUVALINATE", ["SINT-TAU"], ["vite", "patata"], "Patata: tau-fluvalinate")
        self.assertEqual(XM.refazer(c, self.ref)["DEPOIS"], XM.NO)

    def test_B4_rotulo_nao_lido_nunca_e_no(self):
        c = cruzamento("FLUDIOXONIL", ["SINT-NAOLIDO"], ["vite"], "x", estado=XM.NO)
        self.assertEqual(XM.refazer(c, self.ref)["DEPOIS"], XM.UNRESOLVED)

    def test_B5_cultura_fora_do_vocabulario_nunca_e_no(self):
        c = cruzamento("TAUFLUVALINATE", ["SINT-TAU"], ["mirtillo", "patata"], "x", estado=XM.NO)
        self.assertEqual(XM.refazer(c, self.ref)["DEPOIS"], XM.UNRESOLVED)

    def test_B6_no_so_com_todas_lidas_e_ausentes(self):
        c = cruzamento("TAUFLUVALINATE", ["SINT-TAU"], ["patata"], "x", estado=XM.NO)
        self.assertEqual(XM.refazer(c, self.ref)["DEPOIS"], XM.NO)

    def test_B7_ganho_de_grao_e_contado(self):
        c = cruzamento("TAUFLUVALINATE", ["SINT-TAU"], ["pero"], "x")
        r = XM.refazer(c, self.ref)
        self.assertEqual(r["GANHAS_PELO_GRAO"], ["pero"])

    def test_B9_substancia_longe_da_cultura_nao_liga(self):
        c = cruzamento("TAUFLUVALINATE", ["SINT-TAU"], ["vite", "olivo"], "Vite " + "x" * 500 + " tau-fluvalinate")
        r = XM.refazer(c, self.ref)
        self.assertEqual((r["DEPOIS"], r["CULTURAS_LIGADAS_NO_TROCO"]), (XM.PARTIAL, []))

    def test_B8_not_possible_nao_muda(self):
        c = cruzamento("TAUFLUVALINATE", ["SINT-TAU"], [], "x", estado=XM.NOT_POSSIBLE)
        self.assertEqual(XM.refazer(c, self.ref)["DEPOIS"], XM.NOT_POSSIBLE)


class C_Confirmar(unittest.TestCase):
    def conf(self, publicado="2026-06-30", troco="BOLLETTINO FITOSANITARIO VITE: tau-fluvalinate", cadastro=None,
             produtos=("SINT-TAU",)):
        ref = referencia(cadastro=cadastro)
        c = cruzamento("TAUFLUVALINATE", list(produtos), ["vite"], troco, estado=XM.YES_A_CONFIRMAR,
                       x3h=["vite"], publicado=publicado)
        return XM.confirmar(XM.refazer(c, ref), c, ref)

    def test_C1_confirmado_com_os_quatro_cheques(self):
        r = self.conf()
        self.assertEqual(r["ESTADO"], XM.CONFIRMED_YES)
        p = r["PRODUTOS"][0]
        self.assertEqual(p["VALIDADE"]["VALIDO"], "SIM")
        self.assertEqual(p["CHEQUES"]["CULTURA_NO_ROTULO"], "SIM")
        self.assertIn("30-300 ml/hl", p["DOSE_E_VOLUME_LITERAIS"])

    def test_C2_data_do_boletim_nao_sei_nao_confirma(self):
        r = self.conf(publicado="NAO SEI")
        self.assertEqual(r["ESTADO"], XM.UNRESOLVED)
        self.assertIn("data do boletim NAO SEI", r["MOTIVO"])

    def test_C3_cabecalho_fora_do_troco_nao_confirma(self):
        self.assertEqual(self.conf(troco="appezzamenti vigorosi tau-fluvalinate " * 20)["ESTADO"], XM.UNRESOLVED)

    def test_C4_registo_depois_do_boletim(self):
        cad = [dict(l, data_registrazione="01/07/2026") if l["num_registrazione"] == "S001" else l for l in CADASTRO]
        self.assertNotEqual(self.conf(cadastro=cad)["ESTADO"], XM.CONFIRMED_YES)

    def test_C5_empresa_que_nao_e_adama(self):
        cad = [dict(l, ragione_sociale="SINT OUTRA") if l["num_registrazione"] == "S001" else l for l in CADASTRO]
        self.assertNotEqual(self.conf(cadastro=cad)["ESTADO"], XM.CONFIRMED_YES)

    def test_C6_substancia_fora_da_composicao(self):
        cad = [dict(l, sostanze_attive="FOLPET") if l["num_registrazione"] == "S001" else l for l in CADASTRO]
        self.assertNotEqual(self.conf(cadastro=cad)["ESTADO"], XM.CONFIRMED_YES)

    def test_C7_revogado_antes_do_boletim(self):
        cad = [dict(l, stato_amministrativo="Revocato", data_decorrenza_revoca="01/06/2026")
               if l["num_registrazione"] == "S001" else l for l in CADASTRO]
        self.assertNotEqual(self.conf(cadastro=cad)["ESTADO"], XM.CONFIRMED_YES)

    def test_C8_validade_terminada_antes(self):
        cad = [dict(l, data_scadenza_autorizzazione="01/06/2026") if l["num_registrazione"] == "S001" else l
               for l in CADASTRO]
        self.assertNotEqual(self.conf(cadastro=cad)["ESTADO"], XM.CONFIRMED_YES)

    def test_C9_rotulo_lido_sem_a_cultura_e_no(self):
        r = self.conf(produtos=("SINT-POM",))
        self.assertEqual(r["ESTADO"], XM.NO)


class D_Validade(unittest.TestCase):
    def test_D1_sem_data(self):
        self.assertEqual(XM.validade(CADASTRO[0], None)["VALIDO"], NAO_SEI)

    def test_D2_sem_registo(self):
        self.assertEqual(XM.validade(None, date(2026, 1, 1))["VALIDO"], NAO_SEI)

    def test_D3_revogado_depois_valia_antes(self):
        self.assertEqual(XM.validade(CADASTRO[7], date(2019, 1, 1))["VALIDO"], "SIM")
        self.assertEqual(XM.validade(CADASTRO[7], date(2021, 1, 1))["VALIDO"], "NAO")

    def test_D4_data_depois_do_cadastro_vem_com_nota(self):
        v = XM.validade(CADASTRO[0], date(2026, 9, 20), date(2026, 9, 7))
        self.assertEqual(v["VALIDO"], "SIM")
        self.assertTrue(v["NOTA"])


class E_Portfolio(unittest.TestCase):
    def setUp(self):
        self.ref = referencia()
        self.regs = ["S001", "S002", "S003", "S004", "S005"]

    def pm(self, cultura, praga, publicado="2026-06-01"):
        return XM.portfolio_match({"SALA_CHAVE": "SINT#1", "SOURCE_ID": "SINT", "URL": "u", "PUBLISHED_AT": publicado,
                                   "CULTURA": cultura, "PRAGA": praga}, self.ref, self.regs)

    def test_E1_match_forte_com_registo(self):
        r = self.pm("vite", "Scaphoideus titanus")
        self.assertEqual(r["ESTADO"], XM.PM_MATCH)
        self.assertEqual([p["REGISTRATION_ID"] for p in r["PRODUTOS"]], ["S001"])

    def test_E2_so_espectro_de_produto_nao_soma(self):
        r = self.pm("vite", "peronospora")
        self.assertEqual(r["ESTADO"], XM.PM_ESPECTRO)
        self.assertEqual(r["PRODUTOS"], [])

    def test_E3_sem_par_lido_e_leitura_nao_mundo(self):
        r = self.pm("olivo", "mosca delle olive")
        self.assertEqual(r["ESTADO"], XM.PM_SEM_PAR)
        self.assertIn("NA NOSSA LEITURA", r["MOTIVO"])
        self.assertNotIn("nao tem produto", r["MOTIVO"].replace("«a ADAMA nao tem»", ""))

    def test_E4_praga_sem_alvo_no_vocabulario_e_nao_sei(self):
        r = self.pm("vite", "flavescenza dorata")
        self.assertEqual((r["ESTADO"], r["TARGET_ID"]), (XM.PM_NAO_SEI, NAO_SEI))

    def test_E5_membro_de_grupo_declarado(self):
        self.assertEqual(self.pm("pero", "afidi")["ESTADO"], XM.PM_MATCH)

    def test_E6_registo_invalido_na_data_nao_e_match(self):
        self.assertEqual(self.pm("vite", "Scaphoideus titanus", publicado="2009-01-01")["ESTADO"], XM.PM_NAO_SEI)


class F_Competitive(unittest.TestCase):
    def test_F1_so_outras_empresas_validas(self):
        cs = XM.competitive_set(["TAU-FLUVALINATE"], date(2026, 6, 1), referencia())
        self.assertEqual([p["NUM_REGISTRAZIONE"] for p in cs["PRODUTOS"]], ["C100"])
        self.assertEqual(cs["CULTURA_X_ALVO_DO_CONCORRENTE"], NAO_SEI)
        self.assertTrue(cs["GRAO"].startswith("SUBSTANCIA"))

    def test_F2_metalaxyl_nao_e_metalaxyl_m(self):
        cs = XM.competitive_set(["METALAXYLM"], date(2026, 6, 1), referencia())
        self.assertEqual([p["NUM_REGISTRAZIONE"] for p in cs["PRODUTOS"]], ["C104"])


class G_ParesDoBoletim(unittest.TestCase):
    def test_G1_so_pares_da_mesma_secao(self):
        livro = [{"SALA_CHAVE": "SINT#2", "SOURCE_ID": "S", "PROBLEMA": {"SECOES": [
            {"CULTURA": None, "PROBLEMAS": [{"NOME": "oidio", "ESTADO": "CITADA"}]},
            {"CULTURA": "vite", "PROBLEMAS": [{"NOME": "peronospora", "ESTADO": "PRESENTE"}]},
            {"CULTURA": "melo", "PROBLEMAS": [{"NOME": "ticchiolatura", "ESTADO": "CITADA"}]}]}}]
        pares = {(p["CULTURA"], p["PRAGA"]) for p in XM.pares_do_boletim({}, livro)}
        self.assertEqual(pares, {("vite", "peronospora"), ("melo", "ticchiolatura")})

    def test_G2_praga_com_a_cultura_no_nome_do_cabecalho(self):
        analise = {"CROSSINGS": [cruzamento("X", [], ["vite"], "Lotta alla Flavescenza dorata della vite – 2026",
                                            x3h=["vite"])]}
        pares = XM.pares_do_boletim(analise)
        self.assertEqual([(p["CULTURA"], p["PRAGA"]) for p in pares], [("vite", "flavescenza dorata della vite")])


class H_Pote(unittest.TestCase):
    """Os objetos atravessam o gerador do dono SO com a prova ligada a um item que passou G0."""

    def setUp(self):
        self.ref = referencia()
        c = cruzamento("TAUFLUVALINATE", ["SINT-TAU"], ["vite"], "BOLLETTINO FITOSANITARIO VITE: tau-fluvalinate",
                       estado=XM.YES_A_CONFIRMAR, x3h=["vite"])
        self.res = XM.analisar({"CROSSINGS": [c], "CORTE_VERTICAL": {"ITENS": []}}, self.ref)
        self.itens = XM.itens_do_pote(self.res, self.ref)

    def entrada(self, g0="PASSOU", doc="SINT-DOC-1", duplicar=False):
        lin = [{"ITEM_ID": "SINT-RUN#0", "CORRIDA_UPSTREAM": "SINT-UP", "RAW_OBSERVATION_ID": 77,
                "SOURCE_ID": "SINT-SRC", "G0": g0, "G0_FALTA": [], "DOCUMENT_ID": doc}]
        if duplicar:
            lin.append(dict(lin[0], CORRIDA_UPSTREAM="SINT-UP-2"))
        return {"SCHEMA": "SINT", "SINTETICA": True, "INTELLIGENCE_RUN_ID": "SINT-IR-R7", "SOURCE_HEAD": "SINT-H",
                "CORTE": "2026-09-27", "RESULT_STATE": "DONE", "LINEAGE": lin, "ITENS_POR_FERRAMENTA": {}}

    def pote(self, **kw):
        return POTE.adaptar(PX.montar_corrida(self.entrada(**kw), self.itens, "SINT-HEAD"))

    def test_H1_confirmado_atravessa_com_estado_visivel(self):
        p = self.pote()
        objs = p["COMPARTIMENTOS"]["portfolio"]["OBJETOS"]
        self.assertTrue(objs)
        o = objs[0]
        self.assertEqual(o["ESPECIE"], "CROSSING")
        self.assertEqual(o["FORA_DO_CONTRATO"]["CROSSING_STATE"], XM.CONFIRMED_YES)
        self.assertEqual(o["CHAVES"]["PRODUCT_ID"], "SINT-PRD-1")
        self.assertEqual(o["PROVA"][0]["DOCUMENT_ID"], "SINT-DOC-1")
        self.assertEqual(POTE.conferir_pote(p), [])

    def test_H2_competitors_com_grao_substancia(self):
        objs = self.pote()["COMPARTIMENTOS"]["competitors"]["OBJETOS"]
        self.assertEqual([o["CHAVES"]["COMPANY_ID"] for o in objs], ["SINT CONCORRENTE SPA"])
        self.assertEqual(objs[0]["CHAVES"]["CROP_ID"], NAO_SEI)
        self.assertEqual(objs[0]["FORA_DO_CONTRATO"]["GRAO"], "SUBSTANCIA")

    def test_H3_sem_document_id_e_recusado_a_vista(self):
        p = self.pote(doc=None)
        self.assertEqual(p["COMPARTIMENTOS"]["portfolio"]["OBJETOS"], [])
        self.assertTrue(any(r["MOTIVO"] == "PROVA_INCOMPLETA" for r in p["RECUSADOS"]))

    def test_H4_g0_bloqueado_nao_atravessa(self):
        p = self.pote(g0="BLOQUEADO_EM_G0")
        self.assertEqual(p["COMPARTIMENTOS"]["portfolio"]["OBJETOS"], [])

    def test_H5_lineage_ambigua_nao_e_ligada(self):
        corrida = PX.montar_corrida(self.entrada(duplicar=True), self.itens, "SINT-HEAD")
        prova = corrida["ITENS_POR_FERRAMENTA"]["portfolio"][0]["PROVA"][0]
        self.assertEqual(prova["DOCUMENT_ID"], NAO_SEI)
        self.assertTrue(prova["PROVA_LIGADA_A_LINEAGE"].startswith("NAO:AMBIGUA"))

    def test_H6_corrida_nova_nao_e_a_r7(self):
        corrida = PX.montar_corrida(self.entrada(), self.itens, "SINT-HEAD")
        self.assertNotEqual(corrida["INTELLIGENCE_RUN_ID"], "SINT-IR-R7")
        self.assertEqual(corrida["CORRIDA_BASE"], "SINT-IR-R7")
        self.assertTrue(corrida["INTELLIGENCE_RUN_ID"].startswith("IR-XMAX-"))

    def test_H7_objetos_da_r7_mantidos_salvo_so_cruzamentos(self):
        e = self.entrada()
        e["ITENS_POR_FERRAMENTA"] = {"market": [{"OBJETO_ID": "SINT-M"}]}
        self.assertIn("market", PX.montar_corrida(e, self.itens, "H")["ITENS_POR_FERRAMENTA"])
        self.assertNotIn("market", PX.montar_corrida(e, self.itens, "H", so_cruzamentos=True)["ITENS_POR_FERRAMENTA"])

    def test_H8_nada_de_oportunidade_nem_sinal(self):
        for objs in self.itens.values():
            self.assertEqual({o["ESPECIE"] for o in objs}, {"CROSSING"})


class Z_Vocabulario(unittest.TestCase):
    def test_Z1_vocabulario_igual_ao_do_leitor(self):
        import rotulos_ler
        import adama_it_intelligence
        self.assertEqual(list(XM.CULTURAS_ROTULO), list(rotulos_ler.CULTURAS_ROTULO))
        self.assertEqual(list(XM.ALVOS_CANON), list(rotulos_ler.ALVOS_CANON))
        self.assertEqual(tuple(XM.ADMIN_ATIVO), tuple(adama_it_intelligence.ADMIN_ATIVO))


class X_Real(unittest.TestCase):
    """Os insumos reais do repo: o JSON commitado tem de ser o que o codigo produz agora."""

    @classmethod
    def setUpClass(cls):
        cls.out = XM.correr()
        with open(XM.SAIDA, encoding="utf-8") as f:
            cls.commitado = json.load(f)

    def test_X1_contagens_commitadas_batem(self):
        self.assertEqual(self.out["CONTAGENS"], self.commitado["CONTAGENS"])

    def test_X2_nenhum_yes_sem_prova_de_cultura_e_registo(self):
        for r in self.out["REFEITOS"]:
            if r["FINAL"] == XM.CONFIRMED_YES:
                c = r["CONFIRMACAO"]
                self.assertTrue(c["CABECALHO_NO_TROCO_GUARDADO"])
                self.assertNotEqual(c["DATA_DO_BOLETIM"], NAO_SEI)
                self.assertTrue(all(p["CHEQUES"]["CULTURA_NO_ROTULO"] == "SIM"
                                    and p["VALIDADE"]["VALIDO"] == "SIM" for p in c["PRODUTOS"] if p["CONFIRMA"]))

    def test_X3_os_48_so_mudam_com_ligacao_no_texto(self):
        for r in self.out["REFEITOS"]:
            if r["ANTES"] == XM.PARTIAL and r["FINAL"] in (XM.CONFIRMED_YES, XM.YES_A_CONFIRMAR):
                self.assertTrue(r["CULTURAS_LIGADAS_NO_TROCO"])

    def test_X4_itens_commitados_batem(self):
        with open(XM.SAIDA_ITENS, encoding="utf-8") as f:
            itens = json.load(f)["ITENS_POR_FERRAMENTA"]
        self.assertEqual(itens, json.loads(json.dumps(self.out["_ITENS"], ensure_ascii=False)))


if __name__ == "__main__":
    unittest.main()
