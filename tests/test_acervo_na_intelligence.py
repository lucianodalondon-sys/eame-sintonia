#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACERVO-NA-INTELLIGENCE — o acervo antigo pelas capacidades da casa, ate ao pote v2.

    python3 -m unittest tests.test_acervo_na_intelligence -v

A · a corrida inteira sobre a ENTRADA real (2.080 itens): contagens, pote valido,
    o pote commitado e o que a arvore regera.
B · as leis desta missao, lidas no pote: anuncio nao e oportunidade nem demanda;
    preco isolado nao e mudanca; lugar da fonte nao e lugar do facto; publicacao
    nao e tempo do facto; prova ate ao registo; USO_EXIGE_TEMPO; ID PROVISORIO.
C · as regras, uma a uma, sobre registos pequenos (sem a corrida inteira).
"""
import copy
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

import acervo_na_intelligence as A     # noqa: E402  (pacote/)
import pote_intelligence_casco as PIC  # noqa: E402
import validar_pote_v2 as VALIDAR      # noqa: E402

NAO_SEI = A.NAO_SEI
_CACHE = {}


def corrida():
    if "livro" not in _CACHE:
        livro = A._sem_relogio(A.correr(source_head="TESTE"))
        pote, viol, res = A.gerar(livro)
        _CACHE.update(livro=livro, pote=pote, viol=viol, res=res,
                      entrada=json.loads(A.ENTRADA.read_text(encoding="utf-8")))
    return _CACHE


def objetos(pote, comp):
    return pote["COMPARTIMENTOS"][comp]["OBJETOS"]


class A_CorridaInteira(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        c = corrida()
        cls.livro, cls.pote, cls.viol, cls.res, cls.entrada = (c["livro"], c["pote"], c["viol"],
                                                               c["res"], c["entrada"])

    def test_A1_o_pote_passa_no_validador_do_contrato_unico(self):
        self.assertEqual(self.viol, [])
        self.assertEqual(VALIDAR.validar(self.pote), [])
        self.assertEqual(self.pote["SCHEMA"], "POTE_INTELLIGENCE_CASCO/v2")

    def test_A2_uma_corrida_so(self):
        run = self.pote["INTELLIGENCE_RUN_ID"]
        self.assertEqual(run, self.livro["INTELLIGENCE_RUN_ID"])
        for comp, e in self.pote["COMPARTIMENTOS"].items():
            for o in e["OBJETOS"]:
                for p in o["PROVA"]:
                    self.assertEqual(p["INTELLIGENCE_RUN_ID"], run)

    def test_A3_todo_item_da_entrada_e_contado_uma_vez(self):
        self.assertEqual(len(self.entrada["LISTA"]), 2080)
        por = self.res["POR_TIPO"]
        self.assertEqual({t: v["ENTRARAM"] for t, v in por.items()}, self.entrada["POR_TIPO"])
        for t, v in por.items():
            self.assertEqual(v["ENTRARAM"], v["VIRARAM_OBJETO"] + v["RECUSADOS"], t)
            self.assertEqual(sum(v["PORQUE"].values()), v["RECUSADOS"], t)

    def test_A4_quem_fica_fora_da_corrida_e_contado_com_o_motivo(self):
        fora = self.livro["ACERVO"]["FORA_DA_CORRIDA"]
        ids = {x["ITEM_ID"] for x in fora}
        linhas = {l["ITEM_ID"] for l in self.livro["LINEAGE"]}
        self.assertEqual(len(fora), 7)
        self.assertFalse(ids & linhas)
        self.assertEqual(len(linhas) + len(fora), 2080)
        for x in fora:
            self.assertIn("API", x["DETALHE"])

    def test_A5_o_pote_commitado_e_o_que_a_arvore_regera(self):
        commitado = json.loads(A.POTE_SAIDA.read_text(encoding="utf-8"))
        for k in self.pote:
            if k == "SOURCE_HEAD":
                continue
            self.assertEqual(commitado.get(k), self.pote[k], k)
        resumo = json.loads(A.RESUMO_SAIDA.read_text(encoding="utf-8"))
        self.assertEqual(resumo["POR_TIPO"], self.res["POR_TIPO"])
        self.assertEqual(resumo["POTE_POR_COMPARTIMENTO"], self.res["POTE_POR_COMPARTIMENTO"])

    def test_A6_a_origem_e_a_que_a_entrada_declara(self):
        self.assertEqual(A._sha256(A.ORIGEM), self.entrada["ORIGEM"]["SHA256"])

    def test_A7_o_limite_superior_da_captura_vem_do_git(self):
        r = subprocess.run(["git", "show", A.COMMIT_DA_ORIGEM + ":italia-portale/client/italy-handoff-v21.js"],
                           cwd=RAIZ, capture_output=True)
        if r.returncode != 0:
            self.skipTest("NAO SEI: o commit da origem nao esta neste clone")
        import hashlib
        self.assertEqual(hashlib.sha256(r.stdout).hexdigest(), self.entrada["ORIGEM"]["SHA256"])
        d = subprocess.run(["git", "show", "-s", "--format=%cd", "--date=short", A.COMMIT_DA_ORIGEM],
                           cwd=RAIZ, capture_output=True, text=True).stdout.strip()
        self.assertEqual(d, A.LIMITE_SUPERIOR_DA_CAPTURA)
        # a data do pacote NAO e limite: ha OBSERVED_AT depois dela
        self.assertNotEqual(A.LIMITE_SUPERIOR_DA_CAPTURA, self.entrada["LISTA"][0]["DATA_DO_PACOTE"])

    def test_A8_as_capacidades_que_correram(self):
        caps = self.livro["CAPACIDADES_EXECUTADAS"]
        for c in ("CAP-WIN", "CAP-SCI", "CAP-COMP", "CAP-MKT", "CAP-FIELD"):
            self.assertIn(c, caps)
        self.assertEqual(caps["CAP-FIELD"]["MEDIDA"]["VOZES_EXTRAIDAS"],
                         caps["CAP-FIELD"]["MEDIDA"]["VOZES_SEM_PROVA_ADMITIDA"] + len(objetos(self.pote, "voices")))
        self.assertEqual(self.livro["CAP_SCI"]["UNIVERSO"]["JULGADOS"] > 0, True)
        self.assertEqual(self.res["REFERENCIA_ADAMA"]["EDICAO_REGISTRO"], "PROD_FTS_6_20260831")

    def test_A9_o_archivio_so_guarda_o_que_atravessou(self):
        # F2 (§5-E): o CONHECIMENTO sem tempo atravessa (science) mas nao se arquiva — o Archivio e memoria datada
        conhecimento = {("science", o["OBJETO_ID"]) for o in objetos(self.pote, "science")
                        if o.get("RESULTADO") == "NO_DEFENSIBLE_ACTION_YET" and not o["USO_EXIGE_TEMPO"]}
        atravessou = {(c, o["OBJETO_ID"]) for c in ("competitors", "market", "voices", "science",
                                                     "windows", "future") for o in objetos(self.pote, c)} - conhecimento
        for o in objetos(self.pote, "archive"):
            self.assertIn((o["FORA_DO_CONTRATO"]["ARQUIVADO_DE"], o["OBJETO_ID"]), atravessou)
        self.assertEqual(self.pote["COMPARTIMENTOS"]["archive"]["RECUSADOS_AQUI"], 0)
        self.assertEqual(len(objetos(self.pote, "archive")), len(atravessou))


class B_AsLeisNoPote(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        c = corrida()
        cls.livro, cls.pote = c["livro"], c["pote"]
        cls.lugar = cls.livro["ACERVO"]["LUGAR_POR_ITEM"]
        cls.lin = {l["ITEM_ID"]: l for l in cls.livro["LINEAGE"]}

    def test_B1_anuncio_nao_e_oportunidade_nem_demanda(self):
        self.assertEqual(objetos(self.pote, "meeting"), [])
        comp = objetos(self.pote, "competitors")
        self.assertTrue(comp)
        for o in comp:
            self.assertEqual(o["ESPECIE"], "SINAL")
            self.assertIn("OPORTUNIDADE", o["FORA_DO_CONTRATO"]["INTERPRETACAO_DO_SISTEMA"]["NAO_E"])
            self.assertIn("DEMANDA", o["FORA_DO_CONTRATO"]["INTERPRETACAO_DO_SISTEMA"]["NAO_E"])
        for e in self.pote["COMPARTIMENTOS"].values():
            for o in e["OBJETOS"]:
                self.assertNotEqual(o["ESPECIE"], "OPORTUNIDADE")

    def test_B2_concorrente_so_por_substancia_e_so_pela_porta(self):
        for o in objetos(self.pote, "competitors"):
            self.assertEqual(o["CHAVES"]["CROP_ID"], NAO_SEI)
            i = o["FORA_DO_CONTRATO"]["INTERPRETACAO_DO_SISTEMA"]
            regs = sorted({g["REGISTRATION_NUMBER"] for s in i["SUBSTANCIAS_NO_CRIATIVO"]
                           for g in s["ADAMA"]["REGISTOS"]})
            self.assertEqual(i["ADAMA_COM_A_MESMA_SUBSTANCIA"], regs or NAO_SEI)
            self.assertEqual(i["REFERENCIA_ADAMA"], "PROD_FTS_6_20260831")
        com = [o for o in objetos(self.pote, "competitors")
               if o["FORA_DO_CONTRATO"]["INTERPRETACAO_DO_SISTEMA"]["ADAMA_COM_A_MESMA_SUBSTANCIA"] != NAO_SEI]
        self.assertTrue(com, "nenhum anuncio ligado por substancia: a porta nao foi perguntada")

    def test_B3_preco_isolado_nao_e_mudanca_de_mercado(self):
        for o in self.livro["ITENS_POR_FERRAMENTA"]["market"]:
            self.assertNotIn("MUDANCA_DE_MERCADO", o)
            self.assertNotIn("MUDANCA_DE_MERCADO", o["CHAVES"])
            self.assertEqual(PIC.ler_serie(o)[0], PIC.SINAL_SOLTO)
            v = o["CHAVES"]["DA_FONTE"]["VARIACAO_ESCRITA_PELA_FONTE"]
            self.assertEqual(v["PERIODO_DO_PONTO_ANTERIOR"], NAO_SEI)
            for p in o.get("SERIE") or []:
                self.assertNotEqual(p["PRICE"], v["PREV_PRICE_NUM"])
        for o in objetos(self.pote, "market"):
            self.assertEqual(o["MERCADO"]["LEITURA"], PIC.SINAL_SOLTO)

    def test_B4_o_lugar_da_fonte_nao_e_o_lugar_do_facto(self):
        for iid, r in self.lugar.items():
            self.assertEqual(r["FACT_LOCATION"], NAO_SEI, iid)
        for e in self.pote["COMPARTIMENTOS"].values():
            for o in e["OBJETOS"]:
                self.assertNotIn(PIC.normal(o.get("LOCATION_SOURCE", "")), PIC.LOCATION_SOURCE_PROIBIDA)
                self.assertEqual(o["CHAVES"].get("FACT_LOCATION", NAO_SEI), NAO_SEI, o["OBJETO_ID"])

    def test_B5_a_fonte_tem_lugar_e_ele_fica_no_campo_dela(self):
        com_lugar = [r for i, r in self.lugar.items() if "::transcripts::" in i]
        self.assertGreater(len(com_lugar), 100)
        for r in com_lugar:
            self.assertNotEqual(r["SOURCE_LOCATION"], NAO_SEI)
            self.assertIn("SOURCE_COUNTRY", r["SOURCE_LOCATION_BASIS"])
            self.assertEqual(r["FACT_LOCATION"], NAO_SEI)

    def test_B6_publicacao_nao_e_tempo_do_facto_fora_da_atividade_do_concorrente(self):
        n = 0
        for iid, l in self.lin.items():
            col = iid.split("::")[1]
            if col in ("scienceCorpus", "scienceRecords", "transcripts", "news", "publicVoices",
                       "fieldBulletins", "agrometConditions", "currentFieldSignals"):
                n += 1
                self.assertEqual(l["FACT_TIME"], NAO_SEI, iid)
                self.assertNotEqual(l["G0"], "PASSOU", iid)
        self.assertEqual(n, 1300)   # 851 + 184 + 8 + 79 + 133 + 38 + 7 (6 agromet ficaram FORA_DA_CORRIDA)

    def test_B7_prova_ate_ao_registo_de_origem(self):
        sha = self.livro["ACERVO"]["ORIGEM"]["SHA256"][:12]
        for comp, e in self.pote["COMPARTIMENTOS"].items():
            for o in e["OBJETOS"]:
                for p in o["PROVA"]:
                    if comp != "sources":
                        self.assertTrue(p["RAW_OBSERVATION_ID"].startswith("italy-handoff-v21.js@" + sha), p)
                    for k in ("URL", "PUBLISHED_AT", "COLHIDO_EM", "FACT_TIME", "URL_BASE", "PUBLISHED_AT_BASE"):
                        self.assertIn(k, p)
                    self.assertNotEqual(p["DOCUMENT_ID"], NAO_SEI)

    def test_B8_colhido_em_diz_o_que_e(self):
        for o in objetos(self.pote, "competitors") + objetos(self.pote, "future"):
            for p in o["PROVA"]:
                c = p["COLHIDO_EM"]
                self.assertTrue(c == NAO_SEI or "PROVADO" in c.upper() or len(c) == 10, c)
                if "LIMITE" in c:
                    self.assertIn("NAO SEI", c)

    def test_B9_uso_exige_tempo(self):
        # F2 (§5-E): a UNICA excecao e o CONHECIMENTO de estudo em science — uso sem tempo, RESULTADO honesto,
        # FACT_TIME NAO SEI. Tudo o resto continua a exigir tempo.
        for comp in ("competitors", "future", "market", "voices", "science", "windows"):
            for o in objetos(self.pote, comp):
                if comp == "science" and o.get("RESULTADO") == "NO_DEFENSIBLE_ACTION_YET" and not o["USO_EXIGE_TEMPO"]:
                    for p in o["PROVA"]:
                        self.assertEqual(p["ADMITIDA_POR"], "USO_SEM_TEMPO", o["OBJETO_ID"])
                        self.assertEqual(p["FACT_TIME"], "NAO SEI", o["OBJETO_ID"])
                    self.assertEqual(o["CHAVES"]["STUDY_PERIOD"], "NAO SEI", o["OBJETO_ID"])
                    continue
                self.assertTrue(o["USO_EXIGE_TEMPO"], o["OBJETO_ID"])
                for p in o["PROVA"]:
                    self.assertIn(p["ADMITIDA_POR"], ("G0_PASSOU", "FUTURO_POR_DESENHO"))

    def test_B9b_conhecimento_nunca_vai_ao_archivio(self):
        for o in objetos(self.pote, "archive"):
            self.assertNotEqual(o["FORA_DO_CONTRATO"].get("ARQUIVADO_DE") == "science"
                                and o["CHAVES"].get("FACT_TIME") == "NAO SEI", True, o["OBJETO_ID"])

    def test_B10_todo_id_e_provisorio_e_sem_composto_de(self):
        for comp, e in self.pote["COMPARTIMENTOS"].items():
            for o in e["OBJETOS"]:
                self.assertEqual(o["FORA_DO_CONTRATO"].get("ID_ESTADO"), "PROVISORIO", (comp, o["OBJETO_ID"]))
                self.assertNotIn("COMPOSTO_DE", json.dumps(o))
                self.assertTrue(o["OBJETO_ID"].startswith("R7-"), o["OBJETO_ID"])

    def test_B11_entity_source_por_chave_viaja_inteiro(self):
        for comp in ("competitors", "future", "sources"):
            for o in objetos(self.pote, comp):
                # D-GER-1-MIG: no objeto, o valor da COL-LAW-221; o mapa inteiro ao lado, e EXIGIDO
                self.assertEqual(o["ENTITY_SOURCE"], "UNKNOWN")
                porch = o["FORA_DO_CONTRATO"]["ENTITY_SOURCE_POR_CHAVE"]
                self.assertIsInstance(porch, dict)
                self.assertTrue(porch, (o["OBJETO_ID"], "sem o mapa de procedencia"))
                for k, v in o["CHAVES"].items():
                    self.assertEqual(porch[k]["VALOR"], v, (o["OBJETO_ID"], k))

    def test_B12_o_futuro_so_por_desenho_e_so_depois_do_limite_do_git(self):
        for o in objetos(self.pote, "future"):
            for p in o["PROVA"]:
                self.assertEqual(p["ADMITIDA_POR"], "FUTURO_POR_DESENHO")
                self.assertGreater(p["FACT_TIME"][:10], A.LIMITE_SUPERIOR_DA_CAPTURA)

    def test_B13_o_conferir_deste_adaptador_esta_limpo(self):
        self.assertEqual(A.conferir(self.livro), [])


# ── C · as regras, sem a corrida inteira ─────────────────────────────────────
def _x(col, rid="X-1", tipo="anuncio", url="https://exemplo/1"):
    return {"ACERVO_ID": f"italy-handoff-v21.js::{col}::{rid}", "TIPO": tipo, "SOURCE_IDS": ["SRC_A"],
            "URL": url}


class C_AsRegras(unittest.TestCase):
    def test_C1_anuncio_no_ar_e_o_facto(self):
        ft, base = A.tempo_do_facto(_x("competitorActivities"), {"START_DATE": "2026-01-30", "END_DATE": "2026-02-09"})
        self.assertEqual(ft, "2026-01-30..2026-02-09")
        self.assertIn("START_DATE", base)

    def test_C2_ciencia_noticia_transcricao_nao_tem_tempo_de_facto(self):
        for col, r in (("scienceCorpus", {"PUBLISHED_AT": "2019-01-03"}),
                       ("news", {"DATE": "2026-02-13"}),
                       ("transcripts", {"PUBLICATION_DATE": "2026-02-09", "OBSERVED_AT": "2026-09-03"})):
            self.assertEqual(A.tempo_do_facto(_x(col), r), (NAO_SEI, NAO_SEI), col)
            self.assertNotEqual(A.publicacao(_x(col), r)[0], NAO_SEI, col)

    def test_C3_publicacao_do_concorrente_so_quando_a_atividade_e_publicar(self):
        x = _x("competitorActivities")
        self.assertEqual(A.tempo_do_facto(x, {"PUBLISHED_AT": "2020-02-19", "ACTIVITY_TYPE": "ORGANIC_VIDEO"})[0],
                         "2020-02-19")
        self.assertEqual(A.tempo_do_facto(x, {"PUBLISHED_AT": "2020-02-19", "ACTIVITY_TYPE": "PAID"})[0], NAO_SEI)

    def test_C4_periodo_do_preco_so_reescrito(self):
        ft, _ = A.tempo_do_facto(_x("marketObservations"), {"REFERENCE_PERIOD": "08/06/2026..14/06/2026"})
        self.assertEqual(ft, "2026-06-08..2026-06-14")

    def test_C5_captura_limites_provados(self):
        x = _x("events")
        cap, _ = A.captura(x, {}, "2026-11-10", NAO_SEI)
        self.assertTrue(cap.startswith(A.LIMITE_SUPERIOR_DA_CAPTURA))
        cap, como = A.captura(x, {}, "2026-09-10", NAO_SEI)
        self.assertEqual(cap, NAO_SEI, "um evento entre os limites nao e passado nem futuro provado")
        cap, _ = A.captura(x, {}, "2026-09-02", NAO_SEI)
        self.assertEqual(cap, NAO_SEI, "a data do pacote nao e limite de nada")
        cap, _ = A.captura(_x("competitorActivities"), {}, "2026-01-30", NAO_SEI)
        self.assertTrue(cap.startswith("2026-01-30 (LIMITE_INFERIOR"))
        cap, _ = A.captura(_x("transcripts"), {"OBSERVED_AT": "2026-09-03"}, NAO_SEI, "2026-02-09")
        self.assertEqual(cap, "2026-09-03")

    def test_C6_o_ready_nao_tem_lugar_do_facto(self):
        r = {"SOURCE_COUNTRY": "IT", "SOURCE_COUNTRY_ORIGIN": "DA_FONTE", "REGION_IDS": ["GEO_ITALY"],
             "PUBLICATION_DATE": "2026-02-09", "OBSERVED_AT": "2026-09-03"}
        it, raw, _ = A.ready(_x("transcripts", tipo="transcricao"), r, "0" * 64)
        self.assertEqual(it["FACT_LOCATION"], NAO_SEI)
        self.assertEqual(it["SOURCE_LOCATION"], "IT")
        self.assertEqual(it["TEMPO_LUGAR_EVIDENCIA"]["FACT_LOCATION_VEIO_DE"], NAO_SEI)
        self.assertEqual(raw["DOCUMENT_ID"], "https://exemplo/1")

    def test_C7_url_ambigua_nao_se_escolhe(self):
        self.assertEqual(A._url({"URL": ["https://a", "https://b"]}), NAO_SEI)
        self.assertEqual(A._fonte({"SOURCE_IDS": ["SRC_NAO_DECLARADA"]}), NAO_SEI)

    def test_C8_a_serie_so_com_pontos_admitidos_da_mesma_chave(self):
        regs, itens, linhas = {}, [], {}
        for i, (per, preco, un) in enumerate((("2026-06-01..2026-06-07", 10.0, "€/t"),
                                             ("2026-06-08..2026-06-14", 11.0, "€/t"),
                                             ("2026-06-15..2026-06-21", 12.0, "€/100kg"))):
            x = _x("marketObservations", f"M{i}", "preco")
            itens.append(x)
            regs[x["ACERVO_ID"]] = {"MARKET": "Bologna", "PRODUCT": "grano", "STAGE": "farm gate", "UNIT": un,
                                    "PRICE_NUM": preco, "CHANGE_VS_PREV_PCT": 5.0, "PREV_PRICE_NUM": 9.0}
            linhas[x["ACERVO_ID"]] = {"ITEM_ID": x["ACERVO_ID"], "G0": "PASSOU", "FACT_TIME": per}
        # AJUSTE DECLARADO (LOTE8-INTEGRA, D123/LIGACAO-ADAMA): todo objeto leva a ligacao feita pela
        # porta, e o ctx passou a trazer a porta aberta. REF=None: a porta diz NAO_SEI/FALTA=REFERENCIA.
        # Nenhuma assercao mudou.
        ctx = {"RUN_ID": "IR-T", "LINHA": linhas, "RAW": {}, "REF": None,
               "READY": {k: {"ITEM_ID": k, "RAW_OBSERVATION_ID": "r", "SOURCE_ID": "S",
                             "PUBLISHED_AT": NAO_SEI, "CAPTURED_AT": NAO_SEI} for k in linhas}}
        objs, nao = A.mercado(itens, regs, ctx)
        self.assertEqual(nao, [])
        a, b, c = objs
        self.assertEqual(PIC.ler_serie(a)[0], PIC.SERIE_MEDIDA)
        self.assertEqual(len(a["SERIE"]), 2)
        self.assertEqual(PIC.ler_serie(c)[0], PIC.SINAL_SOLTO, "outra unidade nao entra na serie")
        for o in objs:
            self.assertNotIn(9.0, [p["PRICE"] for p in o.get("SERIE", [])], "o preco anterior nao e ponto")
        # um so ponto admitido: sinal solto
        linhas[itens[1]["ACERVO_ID"]]["G0"] = "BLOQUEADO_EM_G0"
        objs, nao = A.mercado(itens, regs, ctx)
        self.assertEqual(len(nao), 1)
        self.assertEqual(PIC.ler_serie(objs[0])[0], PIC.SINAL_SOLTO)

    def test_C9_o_conferir_apanha_as_tres_mentiras(self):
        livro = copy.deepcopy(corrida()["livro"])
        o = livro["ITENS_POR_FERRAMENTA"]["competitors"][0]
        o["ESPECIE"] = "OPORTUNIDADE"
        self.assertTrue(any("OPORTUNIDADE" in v for v in A.conferir(livro)))
        livro = copy.deepcopy(corrida()["livro"])
        livro["ITENS_POR_FERRAMENTA"]["market"][0]["MUDANCA_DE_MERCADO"] = True
        self.assertTrue(any("mudanca" in v for v in A.conferir(livro)))
        livro = copy.deepcopy(corrida()["livro"])
        livro["ITENS_POR_FERRAMENTA"]["competitors"][0]["LOCATION_SOURCE"] = "SOURCE_LOCATION"
        self.assertTrue(any("lugar da fonte" in v for v in A.conferir(livro)))

    def test_C10_nomear_palavra_da_collection(self):
        self.assertEqual(A.nomeia_palavra_da_collection({"ITEM_ID": "x", "SOURCE_ID": "SRC_API_ARPA_VENETO_IT",
                                                          "UNIVERSO": "ACERVO/agromet"}), ["API"])
        self.assertEqual(A.nomeia_palavra_da_collection({"ITEM_ID": "x", "SOURCE_ID": "SRC_EIMA_IT",
                                                          "UNIVERSO": "ACERVO/evento"}), [])


if __name__ == "__main__":
    unittest.main()
