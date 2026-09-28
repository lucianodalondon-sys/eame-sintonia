#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""POTE v2.1 — UM CARTAO POR PERGUNTA (D125, aprovada pelo dono 27/09 ~21:40: «potes, aprovo»).

    python3 -m unittest tests.test_pote_v21 -v

Os quatro pontos da D125, cada um com o teste que o segura:
    D125.1  um fato/documento alimenta VARIOS potes ao mesmo tempo           -> T3, T1
    D125.2  atualiza UMA vez e todos os potes mudam juntos (CAUSA=PAI_MUDOU)  -> T3, T5
    D125.3  1 documento novo que toca 3 potes = 0 cartoes repetidos e os 3
            potes com o mesmo carimbo/motivo                                  -> T3 (o teste obrigatorio)
    D125.4  nenhum pote guarda copia do cartao, so o ID; a prova conta 1 vez   -> T1, T2, T7
e o contrato v2.1 (IDENTIDADE-CRUZAMENTO §6.2): ANTERIOR = RUN_ID + SHA256 (T8), SAIU so com causa (T4),
REFERENCIAS {CROSSING_ID, AVALIACAO_ID, PAPEL} para baixo (T6), migracao com ALIAS (T9), R7 publicado (T13).

⚠️ DADO SINTETICO DECLARADO (SINT-), salvo T13, que le o POTE-R7 PUBLICADO commitado em
docs/intelligence/r7/POTE-R7-PUBLICADO.json (origem: origin/claude/casco-r7-publication-yb7nsg @60ee56b2,
docs/casco/r7/POTE-R7.json, sha256 0189967826ea79e0…).
"""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

import pote_intelligence_casco as P      # noqa: E402
import validar_pote_v2 as VV             # noqa: E402
import identidade_do_cruzamento as IDENT  # noqa: E402
from ponte_intelligence_casco import LeiViolada  # noqa: E402

KEY_C = "F2_PORTFOLIO_MATCH/v1|JURISDICAO=IT|CROP=CROP:OLIVO|TARGET=PEST:MOSCA_OLIVO"
C = IDENT.crossing_id(KEY_C)
R7_PUBLICADO = RAIZ / "docs" / "intelligence" / "r7" / "POTE-R7-PUBLICADO.json"


def prova(n, src="SINT-SRC-A", orig=None):
    p = {"ITEM_ID": "SINT-IT-%s" % n, "CORRIDA_UPSTREAM": "SINT-UP", "RAW_OBSERVATION_ID": "SINT-RAW-%s" % n,
         "SOURCE_ID": src, "DOCUMENT_ID": "SINT-DOC-%s" % n, "URL": "https://sint.example/%s" % n,
         "PUBLISHED_AT": "2026-09-18", "FACT_TIME": "2026-09-18"}
    if orig:
        p["ORIGINADOR"] = orig
    return p


def cruz(provas, estado="SEM_PAR_LIDO"):
    return {"OBJETO_ID": C, "CROSSING_KEY": KEY_C, "FAMILIA": IDENT.F2, "ALIAS": [], "ESPECIE": "CROSSING",
            "ESTADO": "EXPERIMENTAL_CANDIDATE", "RESPOSTA": estado,
            "CHAVES": {"CROP_ID": "OLIVO", "TARGET_ID": "MOSCA_OLIVO", "CROSSING_STATE": estado},
            "PROVA": provas, "PORQUE": "SINT: o rotulo lido nao tem o par"}


def dependente(oid, especie, provas, papel="APOIA"):
    return {"OBJETO_ID": oid, "ESPECIE": especie, "ESTADO": "EXPERIMENTAL_CANDIDATE", "CHAVES": {},
            "PROVA": provas, "REFERENCIAS": [{"CROSSING_ID": C, "PAPEL": papel}], "PORQUE": "SINT: depende de C"}


def sinal(n):
    return {"OBJETO_ID": "SG2-SINT%012d" % n, "ESPECIE": "SINAL", "ESTADO": "EXPERIMENTAL_CANDIDATE",
            "CHAVES": {"FACT_TIME": "2026-09-18"}, "PROVA": [prova("S%d" % n)], "PORQUE": "SINT: sinal"}


def corrida(run, provas_c, estado="SEM_PAR_LIDO", sem=()):
    c = cruz(provas_c, estado)
    o = dependente("SINT-OPP-1", "OPORTUNIDADE", [prova("O1")])
    w = dependente("SINT-FIN-AGENDA-1", "FINDING", [prova("W1")])
    s = sinal(1)
    itens = {"portfolio": [c], "meeting": [c, o], "windows": [c, w, s], "archive": [s]}
    for comp, oid in sem:
        itens[comp] = [x for x in itens[comp] if x["OBJETO_ID"] != oid]
    todas = [p for objs in itens.values() for x in objs for p in x["PROVA"]]
    lin, vistos = [], set()
    for p in todas:
        if p["ITEM_ID"] not in vistos:
            vistos.add(p["ITEM_ID"])
            lin.append({"ITEM_ID": p["ITEM_ID"], "CORRIDA_UPSTREAM": "SINT-UP", "RAW_OBSERVATION_ID": p["RAW_OBSERVATION_ID"],
                        "SOURCE_ID": p["SOURCE_ID"], "G0": "PASSOU", "G0_FALTA": []})
    return {"SCHEMA": "SINT", "SINTETICA": True, "INTELLIGENCE_RUN_ID": run, "SOURCE_HEAD": "SINT-HEAD",
            "CORTE": "2026-09-27", "RESULT_STATE": "DONE", "LINEAGE": lin, "ITENS_POR_FERRAMENTA": copy.deepcopy(itens)}


def publicar(pote):
    """O pote como fica publicado: os BYTES e o sha256 deles (opcao A)."""
    b = (json.dumps(pote, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    return json.loads(b), IDENT.impressao_do_pote(b)


class Pote21(unittest.TestCase):
    def setUp(self):
        self.a = P.adaptar_v21(corrida("SINT-IR-A", [prova(1), prova(2)]))
        self.ant, self.sha = publicar(self.a)

    def b(self, causas=None, **kw):
        return P.adaptar_v21(corrida("SINT-IR-B", kw.pop("provas_c", [prova(1), prova(2)]), **kw),
                             self.ant, self.sha, causas)

    # ── D125.4 · nenhum pote guarda copia ────────────────────────────────────
    def test_T1_nenhum_compartimento_guarda_copia_so_o_id(self):
        p = self.a
        self.assertEqual(p["SCHEMA"], P.CONTRATO_V21)
        for comp, e in p["COMPARTIMENTOS"].items():
            self.assertNotIn("OBJETOS", e, comp)
            self.assertTrue(all(isinstance(i, str) for i in e["IDS"]))
        # o sinal esta em windows E no archive: UM cartao, dois lugares
        s = [c for c in p["CARTOES"].values() if c["ESPECIE"] == "SINAL"]
        self.assertEqual(len(s), 1)
        self.assertEqual(s[0]["COMPARTIMENTOS"], ["windows", "archive"])
        self.assertIn(s[0]["OBJETO_ID"], p["COMPARTIMENTOS"]["archive"]["IDS"])
        n = p["CONTAGEM_DE_CARTOES"]
        self.assertEqual((n["LUGARES_NOS_COMPARTIMENTOS"], n["CARTOES_DISTINTOS"]), (7, 4))
        self.assertEqual(P.conferir_pote(p), [])

    def test_T2_copia_no_compartimento_reprova(self):
        p = copy.deepcopy(self.a)
        p["COMPARTIMENTOS"]["archive"]["OBJETOS"] = [p["CARTOES"][p["COMPARTIMENTOS"]["archive"]["IDS"][0]]]
        self.assertTrue(any("COPIA_NO_POTE" in v for v in P.conferir_pote(p)))
        self.assertTrue(VV.validar(p))
        q = copy.deepcopy(self.a)
        q["COMPARTIMENTOS"]["archive"]["IDS"].append(q["COMPARTIMENTOS"]["archive"]["IDS"][0])
        self.assertTrue(any("repetido" in v for v in P.conferir_pote(q)))
        r = copy.deepcopy(self.a)
        r["COMPARTIMENTOS"]["archive"]["IDS"].append("SINT-NAO-EXISTE")
        self.assertTrue(any("sem cartao" in v for v in P.conferir_pote(r)))
        t = copy.deepcopy(self.a)          # a mesma pergunta com dois cartoes (o nome antigo de um e o novo de outro)
        o = t["CARTOES"]["SINT-OPP-1"]
        o["ALIAS"] = [C]
        self.assertTrue(any("dois cartoes" in v for v in P.conferir_pote(t)))

    # ── D125.3 · O TESTE OBRIGATORIO ─────────────────────────────────────────
    def test_T3_um_documento_novo_que_toca_3_potes_zero_repetidos_mesmo_carimbo(self):
        p = self.b(provas_c=[prova(1), prova(2), prova("D")])
        self.assertEqual(P.conferir_pote(p), [])
        # 0 cartoes repetidos: cada ID uma vez em CARTOES e uma vez por compartimento
        ids = [i for e in p["COMPARTIMENTOS"].values() for i in e["IDS"]]
        self.assertEqual(len(set(ids)), len(p["CARTOES"]))
        for e in p["COMPARTIMENTOS"].values():
            self.assertEqual(len(e["IDS"]), len(set(e["IDS"])))
        # o documento novo toca 3 potes: Label (portfolio), Oportunidade (meeting), Agenda (windows)
        potes = ("portfolio", "meeting", "windows")
        self.assertTrue(all(C in p["COMPARTIMENTOS"][k]["IDS"] for k in potes))
        v2 = P.materializar(p)
        vistos = {k: [o for o in v2["COMPARTIMENTOS"][k]["OBJETOS"] if o["OBJETO_ID"] == C][0]["DELTA"] for k in potes}
        self.assertEqual(len({json.dumps(d, sort_keys=True) for d in vistos.values()}), 1, "o mesmo carimbo nos 3")
        d = vistos["portfolio"]
        self.assertEqual((d["MUDANCA"], d["CAUSA"], d["GATILHO"]),
                         (IDENT.FORTALECEU, "NOVA_EVIDENCIA", ["DOC:SINT-DOC-D"]))
        # e os dependentes nos outros potes mudam JUNTO, com o mesmo gatilho (D125.2)
        for dep in ("SINT-OPP-1", "SINT-FIN-AGENDA-1"):
            dd = p["CARTOES"][dep]["DELTA"]
            self.assertEqual((dd["MUDANCA"], dd["CAUSA"], dd["GATILHO"]),
                             (IDENT.FORTALECEU, "PAI_MUDOU(%s)" % C, ["DOC:SINT-DOC-D"]))
        # o sinal que o documento nao tocou nao muda
        s = [c for c in p["CARTOES"].values() if c["ESPECIE"] == "SINAL"][0]
        self.assertEqual(s["DELTA"]["MUDANCA"], IDENT.SEM_REVISAO)
        self.assertEqual(p["DELTA_CONTAGEM"], {"NOVO": 0, "FORTALECEU": 3, "MUDOU_ESTADO": 0, "ENFRAQUECEU": 0,
                                               "SEM_REVISAO": 1, "SAIU": 0})

    # ── SAIU so com causa ───────────────────────────────────────────────────
    def test_T4_ausencia_nao_e_saida_e_saiu_exige_causa(self):
        sem = [("windows", "SINT-FIN-AGENDA-1")]
        p = self.b(sem=sem)
        self.assertEqual(p["SAIRAM"], [])
        self.assertEqual([x["CROSSING_ID"] for x in p["NAO_REVISTOS"]], ["SINT-FIN-AGENDA-1"])
        self.assertEqual(P.conferir_pote(p), [])
        q = self.b(sem=sem, causas={"SINT-FIN-AGENDA-1": "PROVA_REVOGADA_NA_SALA (SINT)"})
        self.assertEqual([x["CROSSING_ID"] for x in q["SAIRAM"]], ["SINT-FIN-AGENDA-1"])
        self.assertEqual(q["DELTA_CONTAGEM"]["SAIU"], 1)
        self.assertEqual(P.conferir_pote(q), [])
        r = copy.deepcopy(q)
        r["SAIRAM"][0]["CAUSA"] = ""
        self.assertTrue(any("SAIU sem causa" in v for v in P.conferir_pote(r)))

    def test_T5_mudou_estado_propaga_aos_dependentes(self):
        p = self.b(estado="PORTFOLIO_MATCH")
        self.assertEqual(p["CARTOES"][C]["DELTA"]["MUDANCA"], IDENT.MUDOU_ESTADO)
        self.assertEqual(p["CARTOES"][C]["DELTA"]["ESTADO_DE"], "SEM_PAR_LIDO")
        self.assertEqual(p["CARTOES"]["SINT-OPP-1"]["DELTA"]["MUDANCA"], IDENT.MUDOU_ESTADO)
        self.assertEqual(p["CARTOES"]["SINT-OPP-1"]["DELTA"]["CAUSA"], "PAI_MUDOU(%s)" % C)

    # ── REFERENCIAS: para baixo, desta corrida ──────────────────────────────
    def test_T6_referencias_para_baixo_e_da_mesma_corrida(self):
        o = self.a["CARTOES"]["SINT-OPP-1"]
        self.assertEqual(o["REFERENCIAS"], [{"CROSSING_ID": C, "PAPEL": "APOIA",
                                             "AVALIACAO_ID": IDENT.avaliacao_id(C, "SINT-IR-A")}])
        p = copy.deepcopy(self.a)
        p["CARTOES"]["SINT-OPP-1"]["REFERENCIAS"][0]["AVALIACAO_ID"] = IDENT.avaliacao_id(C, "OUTRA")
        self.assertTrue(any("outra corrida" in v for v in P.conferir_pote(p)))
        q = copy.deepcopy(self.a)
        q["CARTOES"][C]["REFERENCIAS"] = [{"CROSSING_ID": "SINT-OPP-1", "PAPEL": "APOIA",
                                           "AVALIACAO_ID": q["CARTOES"]["SINT-OPP-1"]["AVALIACAO_ID"]}]
        self.assertTrue(any("DESCE" in v or "CICLO" in v for v in P.conferir_pote(q)))
        r = copy.deepcopy(self.a)
        r["CARTOES"]["SINT-OPP-1"]["REFERENCIAS"][0]["PAPEL"] = "PORQUE_SIM"
        self.assertTrue(any("PAPEL" in v for v in P.conferir_pote(r)))

    # ── a prova conta 1 vez ─────────────────────────────────────────────────
    def test_T7_fecho_conta_cada_documento_e_originador_uma_vez(self):
        corr = corrida("SINT-IR-F", [prova(1, orig="REG-X"), prova(2, orig="REG-X")])
        corr["ITENS_POR_FERRAMENTA"]["meeting"][1]["PROVA"] = [prova(1, orig="REG-X")]   # a MESMA prova do pai
        p = P.adaptar_v21(corr)
        f = p["CARTOES"]["SINT-OPP-1"]["FECHO"]
        self.assertEqual((f["N_EVIDENCIAS_DOCUMENTO"], f["N_ORIGINADORES"]), (2, 1))
        q = copy.deepcopy(p)
        q["CARTOES"]["SINT-OPP-1"]["FECHO"]["N_ORIGINADORES"] = 3
        self.assertTrue(any("FECHO" in v for v in P.conferir_pote(q)))

    # ── ANTERIOR = RUN_ID + SHA256 ──────────────────────────────────────────
    def test_T8_anterior_exige_o_sha_e_a_contagem_bate(self):
        self.assertEqual(self.a["ANTERIOR"], "NENHUM")
        self.assertTrue(all(c["DELTA"]["MUDANCA"] == IDENT.NOVO for c in self.a["CARTOES"].values()))
        with self.assertRaisesRegex(LeiViolada, "SHA256 dos bytes"):      # a guarda de ENTRADA
            P.adaptar_v21(corrida("SINT-IR-B", [prova(1)]), self.ant, None)
        with self.assertRaisesRegex(LeiViolada, "SHA256 dos bytes"):
            P.adaptar_v21(corrida("SINT-IR-B", [prova(1)]), self.ant, "nao-e-sha")
        t = copy.deepcopy(self.b())                                          # e a de SAIDA, sozinha
        t["ANTERIOR"]["POTE_SHA256"] = "NAO SEI"
        self.assertTrue(any("ANTERIOR tem de ser" in v for v in P.conferir_pote(t)))
        p = self.b()
        self.assertEqual(p["ANTERIOR"], {"INTELLIGENCE_RUN_ID": "SINT-IR-A", "POTE_SHA256": self.sha})
        self.assertTrue(all(c["DELTA"]["MUDANCA"] == IDENT.SEM_REVISAO for c in p["CARTOES"].values()),
                        "a mesma materia-prima na corrida seguinte: os mesmos IDs, nada muda")
        q = copy.deepcopy(p)
        q["DELTA_CONTAGEM"]["NOVO"] = 9
        self.assertTrue(any("DELTA_CONTAGEM" in v for v in P.conferir_pote(q)))
        r = copy.deepcopy(self.a)
        r["CARTOES"][C]["DELTA"]["MUDANCA"] = IDENT.FORTALECEU
        self.assertTrue(P.conferir_pote(r))

    # ── migracao: ALIAS, nunca apagar ───────────────────────────────────────
    def test_T9_objetos_do_esquema_anterior_da_mesma_pergunta_viram_um_cartao_com_alias(self):
        legado = []
        for i in range(3):
            legado.append({"OBJETO_ID": "XMAX-SINT%04d" % i, "ESPECIE": "CROSSING", "ESTADO": "EXPERIMENTAL_CANDIDATE",
                           "CHAVES": {"CROSSING_STATE": "SEM_PAR_LIDO", "CRUZAMENTO": "PORTFOLIO_MATCH",
                                      "PAR_DO_BOLETIM": "olivo x mosca dell'olivo"},
                           "PROVA": [prova("L%d" % i, src="SINT-SRC-%d" % i)], "PORQUE": "SINT"})
        corr = corrida("SINT-IR-L", [prova(1)])
        corr["ITENS_POR_FERRAMENTA"] = {"portfolio": legado}
        corr["LINEAGE"] = [{"ITEM_ID": x["PROVA"][0]["ITEM_ID"], "CORRIDA_UPSTREAM": "SINT-UP",
                            "RAW_OBSERVATION_ID": x["PROVA"][0]["RAW_OBSERVATION_ID"],
                            "SOURCE_ID": x["PROVA"][0]["SOURCE_ID"], "G0": "PASSOU", "G0_FALTA": []} for x in legado]
        p = P.adaptar_v21(corr)
        self.assertEqual(list(p["CARTOES"]), [C])
        c = p["CARTOES"][C]
        self.assertEqual(c["ALIAS"], ["XMAX-SINT0000", "XMAX-SINT0001", "XMAX-SINT0002"])
        self.assertEqual(len(c["LINKS"]), 3)
        self.assertEqual(P.conferir_pote(p), [])

    # ── o validador e a linha de comando ────────────────────────────────────
    def test_T10_validador_le_a_v21_e_o_schema_proibe_a_copia(self):
        self.assertEqual(VV.validar(self.a), [])
        s = json.loads(VV.SCHEMA_V21.read_text(encoding="utf-8"))
        self.assertEqual(s["properties"]["COMPARTIMENTOS"]["additionalProperties"]["not"], {"required": ["OBJETOS"]})
        p = copy.deepcopy(self.a)
        del p["CARTOES"][C]["DELTA"]
        self.assertTrue(VV.validar(p))

    def test_T11_linha_de_comando_com_anterior_publicado(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "a.json").write_text(json.dumps(corrida("SINT-IR-A", [prova(1), prova(2)])), encoding="utf-8")
            (d / "b.json").write_text(json.dumps(corrida("SINT-IR-B", [prova(1), prova(2), prova("D")])), encoding="utf-8")
            self.assertEqual(P.main([str(d / "a.json"), str(d / "pa.js"), "--v21"]), 0)
            self.assertEqual(P.main([str(d / "b.json"), str(d / "pb.json"), "--anterior", str(d / "pa.js")]), 0)
            self.assertEqual(VV.main([str(d / "pb.json")]), 0)
            pb = json.loads((d / "pb.json").read_text(encoding="utf-8"))
            self.assertEqual(pb["ANTERIOR"]["POTE_SHA256"], IDENT.impressao_do_pote((d / "pa.js").read_bytes()))
            self.assertEqual(pb["CARTOES"][C]["DELTA"]["MUDANCA"], IDENT.FORTALECEU)

    def test_T12_o_casco_nao_calcula_o_delta_so_o_le(self):
        leitor = (RAIZ / "italia-portale" / "client" / "sintonia-pote-casco.js").read_text(encoding="utf-8")
        for proibido in ("EVIDENCIAS_NOVAS.length >", "ANTERIOR_IDS", "impressao", "sha256(", "fecho("):
            self.assertNotIn(proibido, leitor)
        self.assertIn("CONTRATO_V21", leitor)


class K_Fixture(unittest.TestCase):
    def test_K1_a_fixture_do_casco_e_a_que_o_gerador_produz(self):
        """python3 provas/potes_um_cartao/gerar_fixture_v21.py"""
        sys.path.insert(0, str(RAIZ / "provas" / "potes_um_cartao"))
        import gerar_fixture_v21 as G
        a, b = G.gerar()
        fx = RAIZ / "tests" / "fixtures" / "pote"
        self.assertEqual(json.loads((fx / "POTE-SINTETICO-V21-A.json").read_text(encoding="utf-8")), json.loads(json.dumps(a)))
        self.assertEqual(json.loads((fx / "POTE-SINTETICO-V21.json").read_text(encoding="utf-8")), json.loads(json.dumps(b)))
        self.assertEqual(VV.main([str(fx / "POTE-SINTETICO-V21.json")]), 0)


class L_OCascoLeAv21(unittest.TestCase):
    def test_L1_o_casco_resolve_o_id_e_so_mostra_o_delta(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "FALTA DEPENDENCIA: node (as provas do casco sao em JavaScript)")
        r = subprocess.run([node, str(RAIZ / "tests" / "test_pote_v21_no_casco.mjs")], cwd=RAIZ,
                           capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])


class R7_Publicado(unittest.TestCase):
    """T13 · o POTE-R7 publicado (47 objetos): so MEDICAO de identidade — a lei v2 de hoje ja nao o aprova
    (formato anterior ao contrato unico, 170 violacoes medidas), e isso fica dito em ENTRADA."""

    @classmethod
    def setUpClass(cls):
        b = R7_PUBLICADO.read_bytes()
        cls.sha = IDENT.impressao_do_pote(b)
        cls.p = P.v21_do_v2(json.loads(b), conferir=False)

    def test_T13_47_lugares_25_cartoes_e_o_arquivo_sem_copia(self):
        self.assertEqual(self.sha, "0189967826ea79e05fa93b144144ddcedd151370ba56d11a56d5066946d2b930")
        self.assertEqual(self.p["ENTRADA"], "POTE_V2_SO_MEDICAO")
        n = self.p["CONTAGEM_DE_CARTOES"]
        self.assertEqual((n["LUGARES_NOS_COMPARTIMENTOS"], n["CARTOES_DISTINTOS"]), (47, 25))
        arq = self.p["COMPARTIMENTOS"]["archive"]["IDS"]
        outros = {i for k, e in self.p["COMPARTIMENTOS"].items() if k != "archive" for i in e["IDS"]}
        self.assertEqual((len(arq), len([i for i in arq if i in outros])), (22, 22))

    def test_T14_tau_fluvalinato_continua_2_com_o_mesmo_grupo(self):
        x = [c for c in self.p["CARTOES"].values() if c["ESPECIE"] == "CROSSING"]
        self.assertEqual(len(x), 2)
        self.assertEqual(len({c["GRUPO"] for c in x}), 1)
        self.assertTrue(all(c["ALIAS"][0].startswith("XC-") for c in x))

    def test_T15_a_identidade_e_estavel(self):
        de_novo = P.v21_do_v2(json.loads(R7_PUBLICADO.read_bytes()), conferir=False)
        self.assertEqual(sorted(de_novo["CARTOES"]), sorted(self.p["CARTOES"]))
        self.assertTrue(all(k.startswith(("SG2-", "FUT2-", "XQ-", "REND-")) for k in self.p["CARTOES"]))


if __name__ == "__main__":
    unittest.main()
