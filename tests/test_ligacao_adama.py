#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LIGACAO-ADAMA (D123 do dono, 27/09/2026) — o contrato, em testes.

«todo fato do sintonia tem que estar linkado a bula e ao portfolio senao nada faz sentido»

    python3 -m unittest tests.test_ligacao_adama -v

  A  a ligacao so sai da PORTA: varredura por AST dos consumidores, e o SELO
  B  os estados de D123 sobre a referencia real (edicao PROD_FTS_6_20260831)
  C  catalogo nunca autoriza; DECLARACAO_DE_PRODUTO nunca autoriza; D117 aos 30 dias
  D  ADAMA_SEM_PRODUTO so com a porta a ter lido
  E  travas: nao prova pressao nem demanda (INT-LAW-145), nao e fonte independente (INT-LAW-076)
  F  o pote recusa objeto sem ligacao, com ligacao fora da porta, e edicoes misturadas
  G  cada capacidade anexa a ligacao a todo objeto que emite
  H  as chaves: sem texto, sem procedencia nao contam
"""
import ast
import copy
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for g in ("motor", "leis", "coleta", "pacote", "provas/ligacao_adama"):
    if str(RAIZ / g) not in sys.path:
        sys.path.insert(0, str(RAIZ / g))
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

import porta_da_referencia as PORTA  # noqa: E402
import pote_intelligence_casco as POTE  # noqa: E402
import validar_pote_v2 as VALIDAR  # noqa: E402

HOJE = date(2026, 9, 27)
REF = PORTA.abrir(hoje=HOJE)


def lig(ref=REF, **chaves):
    chaves["VEM_DE"] = {k: "TESTE" for k in chaves}
    return PORTA.ligacao_adama(ref, chaves)


def ref_copiada(mexer):
    """Uma copia da casa numa pasta temporaria, mexida por `mexer(pasta)`, aberta pela porta."""
    d = Path(tempfile.mkdtemp(prefix="lig-adama-"))
    shutil.copytree(PORTA.CASA, d / "adama")
    mexer(d / "adama")
    return PORTA.abrir(d / "adama", hoje=HOJE), d


def reescrever(pasta, nome, f):
    p = pasta / (nome + ".json")
    dado = json.loads(p.read_text(encoding="utf-8"))
    f(dado)
    p.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")


#: Quem emite objetos da Intelligence e tem de chamar a porta (D123, lista da missao).
CONSUMIDORES = ("motor/capacidade_cientifica.py", "motor/cap_win.py", "motor/motor_das_capacidades.py",
                "motor/cruzamentos_max.py", "motor/voce_dal_campo.py", "leis/preco_de_mercado.py",
                "leis/boletim_do_campo.py", "coleta/concorrencia_meta.py", "pacote/pote_intelligence_casco.py")
GAVETAS_VARRIDAS = ("motor", "leis", "coleta", "pacote", "admissao", "regras", "medidas", "guarda",
                    "fontes", "ferramentas", "superficie", "portoes", "candidatas", "pedido")
SO_DA_PORTA = {"ligacao_adama", "conferir_ligacao", "_selar_ligacao", "_selo_da_ligacao"}
PALAVRAS_DA_PORTA = {PORTA.CONTRATO_LIGACAO, PORTA.AUTORIZADO_BULA_LIDA, PORTA.ADAMA_SEM_PRODUTO,
                     PORTA.SO_CULTURA}


def _varrer():
    for g in GAVETAS_VARRIDAS:
        for p in sorted((RAIZ / g).rglob("*.py")):
            rel = p.relative_to(RAIZ).as_posix()
            if rel == PORTA.PORTA:
                continue
            yield rel, ast.parse(p.read_text(encoding="utf-8"))


class A_SoAPortaCalcula(unittest.TestCase):

    def test_A1_nenhum_ficheiro_fora_da_porta_define_ou_sela_a_ligacao(self):
        sujos = []
        for rel, arv in _varrer():
            for n in ast.walk(arv):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in SO_DA_PORTA:
                    sujos.append("%s:%d define %s" % (rel, n.lineno, n.name))
                if isinstance(n, ast.Attribute) and n.attr in ("_selar_ligacao", "_selo_da_ligacao"):
                    sujos.append("%s:%d chama %s" % (rel, n.lineno, n.attr))
                if isinstance(n, ast.Constant) and n.value in PALAVRAS_DA_PORTA:
                    sujos.append("%s:%d escreve %r" % (rel, n.lineno, n.value))
                if isinstance(n, ast.Dict) and any(isinstance(k, ast.Constant) and k.value in ("SELO", "CALCULADA_POR")
                                                   for k in n.keys):
                    sujos.append("%s:%d monta um dict com SELO/CALCULADA_POR" % (rel, n.lineno))
                # x["LIGACAO_ADAMA"] = {...}  ou  {"LIGACAO_ADAMA": {...}}
                if isinstance(n, ast.Assign) and isinstance(n.value, ast.Dict):
                    for t in n.targets:
                        if isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Constant) \
                                and t.slice.value == "LIGACAO_ADAMA":
                            sujos.append("%s:%d monta a LIGACAO_ADAMA a mao" % (rel, n.lineno))
                if isinstance(n, ast.Dict):
                    for k, v in zip(n.keys, n.values):
                        if isinstance(k, ast.Constant) and k.value == "LIGACAO_ADAMA" and isinstance(v, ast.Dict):
                            sujos.append("%s:%d monta a LIGACAO_ADAMA a mao" % (rel, n.lineno))
        self.assertEqual([], sujos)

    def test_A2_cada_consumidor_chama_a_porta(self):
        for rel in CONSUMIDORES:
            arv = ast.parse((RAIZ / rel).read_text(encoding="utf-8"))
            chamadas = [n for n in ast.walk(arv) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                        and n.func.attr == "ligacao_adama"]
            self.assertTrue(chamadas, "%s nao chama PORTA.ligacao_adama" % rel)

    def test_A3_o_selo_apanha_a_ligacao_mexida_fora_da_porta(self):
        x = lig(CULTURA="VITE", PROBLEMA="PERONOSPORA")
        self.assertEqual([], PORTA.conferir_ligacao(x))
        y = copy.deepcopy(x)
        y["ESTADO"] = PORTA.A_CONFIRMAR
        self.assertTrue(any("SELO" in v for v in PORTA.conferir_ligacao(y)))
        z = copy.deepcopy(x)
        z["CALCULADA_POR"] = "motor/cap_win.py"
        self.assertTrue(PORTA.conferir_ligacao(z))

    def test_A4_uma_ligacao_feita_a_mao_com_a_forma_certa_reprova(self):
        falsa = {k: v for k, v in lig(CULTURA="VITE").items() if k != "SELO"}
        falsa["SELO"] = "0" * 64
        self.assertTrue(PORTA.conferir_ligacao(falsa))


class B_OsEstados(unittest.TestCase):

    def test_B1_cultura_e_alvo_na_mesma_linha_de_bula_lida(self):
        x = lig(CULTURA="VITE", PROBLEMA="PERONOSPORA")
        self.assertEqual(x["ESTADO"], PORTA.AUTORIZADO_BULA_LIDA)
        aut = [p for p in x["PRODUTOS_ADAMA"] if p["ESTADO"] == PORTA.AUTORIZADO_BULA_LIDA]
        self.assertTrue(aut)
        for p in aut:
            self.assertTrue(p["BULA_LIDA"])
            self.assertTrue(set(p["LINK_LEVEL"]) & set(PORTA.NIVEIS_QUE_AUTORIZAM))
            self.assertIn("DOCUMENT_ID", p["BULA"])

    def test_B2_o_carimbo_da_edicao_viaja(self):
        c = lig(CULTURA="VITE")["CARIMBO"]
        for k in ("EDICAO_REGISTRO", "DATA_DA_EDICAO_REGISTRO", "ULTIMA_CHECAGEM_OK", "ESTADO_FRESCOR",
                  "IMPRESSAO_DOS_LIVROS"):
            self.assertNotIn(c.get(k), (None, PORTA.NAO_SEI), k)
        self.assertEqual(c["EDICAO_REGISTRO"], REF["REGISTRO"]["EDICAO"])

    def test_B3_so_cultura(self):
        x = lig(CULTURA="CROP_OLIVE")
        self.assertEqual(x["ESTADO"], PORTA.SO_CULTURA)
        self.assertEqual(x["FALTA"], ["PROBLEMA"])
        self.assertTrue(all(p["ESTADO"] == PORTA.SO_CULTURA for p in x["PRODUTOS_ADAMA"]))

    def test_B4_nao_sei_diz_o_que_falta(self):
        self.assertEqual(lig()["FALTA"], ["CULTURA", "PROBLEMA", "SUBSTANCIA"])
        s = lig(SUBSTANCIA="TAU-FLUVALINATE")
        self.assertEqual((s["ESTADO"], s["FALTA"][0]), (PORTA.NAO_SEI_LIGACAO, "CULTURA"))
        self.assertTrue(s["PRODUTOS_ADAMA"])
        self.assertTrue(all(p["ESTADO"] == PORTA.REGISTRADO_COM_A_SUBSTANCIA for p in s["PRODUTOS_ADAMA"]))
        r = PORTA.ligacao_adama(None, {"CULTURA": "VITE", "VEM_DE": {"CULTURA": "T"}})
        self.assertEqual((r["ESTADO"], r["FALTA"]), (PORTA.NAO_SEI_LIGACAO, ["REFERENCIA"]))
        self.assertEqual([], PORTA.conferir_ligacao(r))

    def test_B5_bula_nao_lida_fica_a_confirmar_e_entra_na_fila(self):
        x = lig(CULTURA="CROP_OLIVE", PROBLEMA="ISSUE_OLIVE_FLY")
        self.assertEqual(x["ESTADO"], PORTA.A_CONFIRMAR)
        self.assertTrue(x["BULAS_A_LER"])
        self.assertTrue(all(b["EMPRESA"] == "ADAMA" for b in x["BULAS_A_LER"]))

    def test_B6_concorrentes_so_por_substancia_e_hoje_nao_sei(self):
        x = lig(SUBSTANCIA="FOLPET", CULTURA="VITE")
        self.assertEqual(x["CONCORRENTES_MESMA_SUBSTANCIA"], [])
        self.assertEqual(x["CONCORRENTES_ESTADO"], PORTA.NAO_SEI)
        self.assertIn("lacuna 3", x["CONCORRENTES_PORQUE"])

    def test_B8_varias_culturas_e_um_problema_nao_autoriza(self):
        x = lig(CULTURA=["CROP_APPLE", "CROP_GRAPEVINE"], PROBLEMA="ISSUE_SCAB")
        self.assertEqual(x["ESTADO"], PORTA.A_CONFIRMAR)
        self.assertFalse(any(p["ESTADO"] == PORTA.AUTORIZADO_BULA_LIDA for p in x["PRODUTOS_ADAMA"]))
        self.assertEqual(lig(CULTURA="CROP_APPLE", PROBLEMA="ISSUE_SCAB")["ESTADO"], PORTA.AUTORIZADO_BULA_LIDA)

    def test_B7_deterministica(self):
        self.assertEqual(lig(CULTURA="VITE", PROBLEMA="PERONOSPORA"), lig(CULTURA="VITE", PROBLEMA="PERONOSPORA"))


class C_OQueNuncaAutoriza(unittest.TestCase):

    def test_C1_catalogo_nao_muda_a_autorizacao(self):
        vazio, d = ref_copiada(lambda p: reescrever(p, "PORTFOLIO", lambda x: x.update(RECORDS=[])))
        try:
            for ch in ({"CULTURA": "VITE", "PROBLEMA": "PERONOSPORA"}, {"CULTURA": "CROP_OLIVE"}):
                a, b = lig(REF, **ch), lig(vazio, **ch)
                self.assertEqual((a["ESTADO"], [p["REGISTRO"] for p in a["PRODUTOS_ADAMA"]]),
                                 (b["ESTADO"], [p["REGISTRO"] for p in b["PRODUTOS_ADAMA"]]))
        finally:
            shutil.rmtree(d)

    def test_C2_produto_so_no_catalogo_nao_vira_autorizado(self):
        x = lig(CULTURA="VITE", PROBLEMA="PERONOSPORA")
        falso = copy.deepcopy(x)
        falso["PRODUTOS_ADAMA"].append({"PRODUTO": "VITRINE", "REGISTRO": "000000", "BULA": {}, "BULA_LIDA": True,
                                        "LINK_LEVEL": ["LINHA_DA_TABELA"], "ESTADO": PORTA.AUTORIZADO_BULA_LIDA,
                                        "FONTE_DO_ESTADO": "CATALOGO.PORTFOLIO"})
        falso = PORTA._selar_ligacao(falso)   # mesmo re-selado pela porta, a lei reprova
        self.assertTrue(any("catalogo" in v for v in PORTA.conferir_ligacao(falso)))

    def test_C3_declaracao_de_produto_fica_a_confirmar(self):
        x = lig(CULTURA="BARBABIETOLA", PROBLEMA="CAPSELLA")
        self.assertEqual(x["ESTADO"], PORTA.A_CONFIRMAR)
        self.assertTrue(x["PRODUTOS_ADAMA"])
        self.assertTrue(all(p["ESTADO"] == PORTA.A_CONFIRMAR for p in x["PRODUTOS_ADAMA"]))
        self.assertTrue(any("DECLARACAO_DE_PRODUTO" in b["PORQUE"] for b in x["BULAS_A_LER"]))
        falso = copy.deepcopy(x)
        falso["ESTADO"] = PORTA.AUTORIZADO_BULA_LIDA
        for p in falso["PRODUTOS_ADAMA"]:
            p["ESTADO"] = PORTA.AUTORIZADO_BULA_LIDA
        self.assertTrue(any("DECLARACAO" in v for v in PORTA.conferir_ligacao(PORTA._selar_ligacao(falso))))

    def test_C4_d117_aos_30_dias_nada_sai_autorizado(self):
        velho = PORTA.abrir(hoje=date.fromisoformat(REF["REGISTRO"]["ULTIMA_CHECAGEM_OK"]) + timedelta(days=30))
        x = lig(velho, CULTURA="VITE", PROBLEMA="PERONOSPORA")
        self.assertEqual(x["ESTADO"], PORTA.A_CONFIRMAR)
        self.assertFalse(any(p["ESTADO"] == PORTA.AUTORIZADO_BULA_LIDA for p in x["PRODUTOS_ADAMA"]))


    def test_C5_registo_revogado_nao_volta_pela_vitrine(self):
        x = lig(CULTURA="VITE", PROBLEMA="PERONOSPORA")
        reg = next(p["REGISTRO"] for p in x["PRODUTOS_ADAMA"] if p["ESTADO"] == PORTA.AUTORIZADO_BULA_LIDA)

        def revogar(pasta):
            reescrever(pasta, "REGISTRATIONS", lambda d: [r.update(ADMIN_ACTIVE=False) for r in d["RECORDS"]
                                                          if r["REGISTRATION_NUMBER"] == reg])
            reescrever(pasta, "PORTFOLIO", lambda d: d["RECORDS"].append({"REGISTRATION_NUMBER": reg,
                                                                          "ADAMA_PRODUCT_ID": "SINT"}))
        r, d = ref_copiada(revogar)
        try:
            self.assertNotIn(reg, [p["REGISTRO"] for p in lig(r, CULTURA="VITE", PROBLEMA="PERONOSPORA")["PRODUTOS_ADAMA"]])
        finally:
            shutil.rmtree(d)


class D_AdamaSemProduto(unittest.TestCase):

    def test_D1_com_bulas_por_ler_nunca_se_diz_que_nao_ha(self):
        for ch in ({"CULTURA": "NOCCIOLO", "PROBLEMA": "CIMICE"}, {"CULTURA": "CROP_OLIVE", "PROBLEMA": "ISSUE_OLIVE_FLY"}):
            self.assertNotEqual(lig(**ch)["ESTADO"], PORTA.ADAMA_SEM_PRODUTO)

    def test_D2_substancia_sem_registo_ativo_com_a_composicao_toda_lida(self):
        x = lig(SUBSTANCIA="ALACLOR")
        self.assertEqual((x["ESTADO"], x["GRAO"]), (PORTA.ADAMA_SEM_PRODUTO, "SUBSTANCIA"))
        pl = x["PROVA_DA_LEITURA"]
        self.assertEqual(pl["COM_COMPOSICAO_LIDA"], pl["REGISTOS_ATIVOS"])
        self.assertEqual([], PORTA.conferir_ligacao(x))

    def test_D3_com_todas_as_bulas_lidas_a_porta_pode_dizer(self):
        def ler_tudo(p):
            reescrever(p, "LABEL-READINGS", lambda x: [r.update(LABEL_WAS_READ=True) for r in x["RECORDS"]])
        tudo, d = ref_copiada(ler_tudo)
        try:
            x = lig(tudo, CULTURA="VITE", PROBLEMA="CIMICE_ASIATICA_INVENTADA")
            self.assertEqual(x["ESTADO"], PORTA.ADAMA_SEM_PRODUTO)
            self.assertEqual([], PORTA.conferir_ligacao(x))
        finally:
            shutil.rmtree(d)

    def test_D4_adama_sem_produto_sem_ter_lido_reprova(self):
        x = lig(CULTURA="CROP_OLIVE", PROBLEMA="ISSUE_OLIVE_FLY")
        falso = copy.deepcopy(x)
        falso.update(ESTADO=PORTA.ADAMA_SEM_PRODUTO, GRAO="CULTURA_X_PROBLEMA")
        self.assertTrue(any("nao leu tudo" in v for v in PORTA.conferir_ligacao(PORTA._selar_ligacao(falso))))
        r = PORTA.ligacao_adama(None, {"VEM_DE": {}})
        r.update(ESTADO=PORTA.ADAMA_SEM_PRODUTO, GRAO="SUBSTANCIA", FALTA=[])
        self.assertTrue(any("sem a porta ter lido" in v for v in PORTA.conferir_ligacao(PORTA._selar_ligacao(r))))


    def test_D5_composicao_incompleta_nao_autoriza_dizer_que_nao_ha(self):
        def tirar(pasta):
            def f(d):   # um registo ativo fica sem composicao lida (todas as linhas dele saem)
                reg = d["RECORDS"][0]["REGISTRATION_NUMBER"]
                d["RECORDS"] = [x for x in d["RECORDS"] if x["REGISTRATION_NUMBER"] != reg]
            reescrever(pasta, "PRODUCT-ACTIVE-INGREDIENTS", f)
        r, d = ref_copiada(tirar)
        try:
            x = lig(r, SUBSTANCIA="ALACLOR")
            self.assertEqual(x["ESTADO"], PORTA.A_CONFIRMAR)
        finally:
            shutil.rmtree(d)


class E_Travas(unittest.TestCase):

    def test_E1_nao_prova_pressao_nem_demanda_e_nao_e_fonte(self):
        x = lig(CULTURA="VITE")
        self.assertEqual(x["NAO_PROVA"], ["PRESSAO_DE_CAMPO", "DEMANDA"])
        self.assertIs(x["CONTA_COMO_FONTE_INDEPENDENTE"], False)
        self.assertIs(x["CATALOGO_E_AUTORIZACAO"], False)
        for k, v in (("CONTA_COMO_FONTE_INDEPENDENTE", True), ("NAO_PROVA", [])):
            y = copy.deepcopy(x)
            y[k] = v
            self.assertTrue(any("trava" in m for m in PORTA.conferir_ligacao(PORTA._selar_ligacao(y))))

    def test_E2_prova_da_referencia_nao_atravessa_o_pote(self):
        c = json.loads((RAIZ / "tests/fixtures/pote/CORRIDA-SINTETICA-POTE.json").read_text(encoding="utf-8"))
        comp, objs = next((k, v) for k, v in c["ITENS_POR_FERRAMENTA"].items() if v and k == "windows")
        objs[0]["PROVA"][0]["SOURCE_ID"] = "IT-T4-001"
        for l in c.get("LINEAGE") or []:
            if l.get("ITEM_ID") == objs[0]["PROVA"][0]["ITEM_ID"]:
                l["SOURCE_ID"] = "IT-T4-001"
        pote = POTE.adaptar(c)
        self.assertIn(("windows", objs[0].get("OBJETO_ID") or objs[0].get("SIGNAL_ID"),
                       "REFERENCIA_NAO_E_FONTE_INDEPENDENTE"),
                      {(r["COMPARTIMENTO"], r["OBJETO_ID"], r["MOTIVO"]) for r in pote["RECUSADOS"]})


class F_OPoteRecusa(unittest.TestCase):

    def corrida(self):
        return json.loads((RAIZ / "tests/fixtures/pote/CORRIDA-SINTETICA-POTE.json").read_text(encoding="utf-8"))

    def test_F1_objeto_sem_ligacao_e_recusado(self):
        c = self.corrida()
        o = c["ITENS_POR_FERRAMENTA"]["windows"][0]
        del o["LIGACAO_ADAMA"]
        pote = POTE.adaptar(c)
        self.assertIn(("windows", o.get("OBJETO_ID") or o.get("SIGNAL_ID"), "SEM_LIGACAO_ADAMA"),
                      {(r["COMPARTIMENTO"], r["OBJETO_ID"], r["MOTIVO"]) for r in pote["RECUSADOS"]})

    def test_F2_ligacao_fora_da_porta_e_recusada(self):
        c = self.corrida()
        o = c["ITENS_POR_FERRAMENTA"]["windows"][0]
        o["LIGACAO_ADAMA"]["ESTADO"] = PORTA.AUTORIZADO_BULA_LIDA
        pote = POTE.adaptar(c)
        self.assertIn("LIGACAO_ADAMA_FORA_DA_PORTA",
                      {r["MOTIVO"] for r in pote["RECUSADOS"] if r["OBJETO_ID"] == (o.get("OBJETO_ID") or o.get("SIGNAL_ID"))})

    def test_F3_o_validador_reprova_pote_com_objeto_sem_ligacao(self):
        pote = json.loads((RAIZ / "tests/fixtures/pote/POTE-SINTETICO.json").read_text(encoding="utf-8"))
        self.assertEqual([], VALIDAR.validar(pote))
        o = next(o for e in pote["COMPARTIMENTOS"].values() for o in e["OBJETOS"])
        del o["LIGACAO_ADAMA"]
        v = VALIDAR.validar(pote)
        self.assertTrue(any("LIGACAO_ADAMA" in x for x in v))
        self.assertTrue(any(x.startswith("LEI:") and "D123" in x for x in v))

    def test_F4_edicoes_misturadas_num_pote_reprovam(self):
        pote = json.loads((RAIZ / "tests/fixtures/pote/POTE-SINTETICO.json").read_text(encoding="utf-8"))
        objs = [o for e in pote["COMPARTIMENTOS"].values() for o in e["OBJETOS"]]
        velho = PORTA.abrir(hoje=HOJE + timedelta(days=40))
        objs[0]["LIGACAO_ADAMA"] = lig(REF, CULTURA="VITE")
        objs[1]["LIGACAO_ADAMA"] = lig(velho, CULTURA="VITE")
        self.assertEqual([], POTE.conferir_pote(pote))   # mesma edicao (so o dia mudou)
        outra, d = ref_copiada(lambda p: reescrever(p, "DOSES", lambda x: x["RECORDS"].pop()))
        try:
            objs[1]["LIGACAO_ADAMA"] = lig(outra, CULTURA="VITE")
            self.assertTrue(any("edicoes diferentes" in x for x in POTE.conferir_pote(pote)))
        finally:
            shutil.rmtree(d)

    def test_F5_o_contrato_diz_a_revisao(self):
        self.assertIn(PORTA.CONTRATO_LIGACAO, POTE.REVISAO_DO_CONTRATO)
        schema = json.loads(VALIDAR.SCHEMA.read_text(encoding="utf-8"))
        self.assertIn("LIGACAO_ADAMA", schema["$defs"]["objeto"]["required"])
        self.assertEqual(schema["properties"]["REVISAO_DO_CONTRATO"]["const"], POTE.REVISAO_DO_CONTRATO)
        self.assertEqual(schema["$defs"]["ligacao"]["properties"]["ESTADO"]["enum"], list(PORTA.ESTADOS_DA_LIGACAO))


class G_CadaCapacidadeAnexa(unittest.TestCase):

    def test_G1_cruzamentos_max_itens_commitados(self):
        d = json.loads((RAIZ / "docs/intelligence/r7/CRUZAMENTOS-MAX-ITENS-DO-POTE.json").read_text(encoding="utf-8"))
        objs = [o for v in d["ITENS_POR_FERRAMENTA"].values() for o in v]
        self.assertTrue(objs)
        for o in objs:
            self.assertEqual([], PORTA.conferir_ligacao(o.get("LIGACAO_ADAMA")), o["OBJETO_ID"])

    def test_G2_cap_win_e_cap_sci_e_motor(self):
        import cap_win as WIN
        import capacidade_cientifica as SCI
        self.assertEqual(WIN.ligacao_da_janela(REF, "CROP_OLIVE", "ISSUE_OLIVE_FLY")["CALCULADA_POR"], PORTA.PORTA)
        e = {"CULTURA": "VITE", "PROBLEMA": "PERONOSPORA", "MOLECULA": ["FOLPET"]}
        x = SCI.ligacao_do_estudo(e, SCI.da_porta(REF))
        self.assertEqual([], PORTA.conferir_ligacao(x))
        self.assertEqual(x["PERGUNTA"]["SUBSTANCIA"], ["FOLPET"])
        import motor_das_capacidades as M
        self.assertIn("LIGACAO_ADAMA", Path(M.__file__).read_text(encoding="utf-8"))

    def test_G3_voce_preco_boletim_concorrencia(self):
        import voce_dal_campo as VC
        import preco_de_mercado as PM
        import boletim_do_campo as BC
        import concorrencia_meta as CM
        doc = VC.documento("Sono Mario Rossi, agronomo. Nel vigneto la peronospora e forte quest'anno.",
                           source_id="SINT-1", external_id="SINT-1", published_at="2026-09-01", channel="SINT")
        for v in VC.extrair(doc, REF)["VOZES"]:
            self.assertEqual([], PORTA.conferir_ligacao(v["LIGACAO_ADAMA"]))
        res = PM.com_ligacao_adama(PM.precos_do_texto("Grano duro fino: 300-310 euro/t a Foggia."), REF)
        for o in res["OBSERVACOES"]:
            self.assertEqual([], PORTA.conferir_ligacao(o["LIGACAO_ADAMA"]))
        leitura = {"SECOES": [{"CULTURA": "vite", "PROBLEMAS": [{"NOME": "peronospora", "ESTADO": "PRESENTE"}]}]}
        for p in BC.produtos_adama_do_boletim(leitura, REF)["PARES"]:
            self.assertEqual([], PORTA.conferir_ligacao(p["LIGACAO_ADAMA"]))
        col = [{"OBSERVACAO": {"CREATIVE_TEXT": "Folpet contro la peronospora", "META_AD_LIBRARY_ID": "SINT"}}]
        for a in CM.adama_no_anuncio(col, REF)["ANUNCIOS"]:
            self.assertEqual([], PORTA.conferir_ligacao(a["LIGACAO_ADAMA"]))


class H_AsChaves(unittest.TestCase):

    def test_H1_a_porta_nao_le_texto(self):
        with self.assertRaises(PORTA.ChaveInvalida):
            PORTA.ligacao_adama(REF, {"TEXTO": "peronospora sulla vite", "VEM_DE": {}})

    def test_H2_chave_sem_procedencia_nao_conta(self):
        x = PORTA.ligacao_adama(REF, {"CULTURA": "VITE", "PROBLEMA": "PERONOSPORA", "VEM_DE": {"CULTURA": "T"}})
        self.assertEqual(x["CHAVES_SEM_PROCEDENCIA_IGNORADAS"], ["PROBLEMA"])
        self.assertEqual(x["ESTADO"], PORTA.SO_CULTURA)

    def test_H3_nao_sei_nao_e_chave(self):
        x = lig(CULTURA=PORTA.NAO_SEI, PROBLEMA="UNKNOWN")
        self.assertEqual(x["PERGUNTA"], {"CULTURA": [], "PROBLEMA": [], "SUBSTANCIA": []})


class I_AFilaEAMedicao(unittest.TestCase):

    def test_I1_fila_adama_primeiro_por_numero_de_fatos_e_lotes_de_5_por_host(self):
        import fila_bulas_a_ler as FILA
        a = lig(CULTURA="CROP_OLIVE", PROBLEMA="ISSUE_OLIVE_FLY")
        b = lig(CULTURA="BARBABIETOLA", PROBLEMA="CAPSELLA")
        f = FILA.fila([("F1", a), ("F2", a), ("F3", b)])
        ns = [x["N_FATOS_QUE_PEDEM"] for x in f["ADAMA"]]
        self.assertEqual(ns, sorted(ns, reverse=True))
        self.assertTrue(all(x["EMPRESA"] == "ADAMA" for x in f["ADAMA"]))
        por = {}
        for x in f["ADAMA"]:
            por.setdefault((x["HOST"], x["LOTE_24H"]), []).append(x)
        self.assertTrue(all(len(v) <= FILA.TETO_POR_DOMINIO_24H for v in por.values()))
        self.assertEqual(f["CONCORRENTES"], [])

    def test_I2_ligacao_fora_da_porta_nao_pede_bula(self):
        import fila_bulas_a_ler as FILA
        a = copy.deepcopy(lig(CULTURA="CROP_OLIVE", PROBLEMA="ISSUE_OLIVE_FLY"))
        a["ESTADO"] = PORTA.SO_CULTURA
        f = FILA.fila([("F1", a)])
        self.assertEqual((f["ADAMA"], len(f["LIGACOES_RECUSADAS"])), ([], 1))

    def test_I3_medicao_e_fila_commitadas_sao_as_que_o_codigo_produz(self):
        import medir as MEDIR
        if MEDIR._git_show(MEDIR.ACERVO_REF, MEDIR.ACERVO_CAMINHO) is None:
            self.skipTest("NAO SEI: o objeto git do acervo nao esta neste clone")
        medicao, fila = MEDIR.medir(REF)
        self.assertEqual(json.loads(MEDIR.SAIDA.read_text(encoding="utf-8")), json.loads(MEDIR._texto(medicao)))
        self.assertEqual(json.loads(MEDIR.SAIDA_FILA.read_text(encoding="utf-8")), json.loads(MEDIR._texto(fila)))


if __name__ == "__main__":
    unittest.main()
