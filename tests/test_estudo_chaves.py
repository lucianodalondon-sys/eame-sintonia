#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESTUDOS-CHAVES (27/09) — CULTURA, PROBLEMA e o LUGAR DO ESTUDO no titulo+resumo dos estudos T5.

Fixtures SINTETICAS (`tests/fixtures/estudos_chaves/ESTUDOS-SINTETICOS.json`): titulos e resumos
INVENTADOS e marcados; nenhum artigo real, nenhum dado pessoal. Sem rede, sem banco."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ("", "leis", "admissao", "coleta"):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
import afirmacao_da_fonte as AF  # noqa: E402
import boletim_do_campo as BC  # noqa: E402
import afirmacao_da_fonte as AF  # noqa: E402
import estudo_chaves as EC  # noqa: E402
import pesquisadores_t6 as T6  # noqa: E402
import reprocessar_estudos_chaves as RE  # noqa: E402

FIXTURE = os.path.join(RAIZ, "tests", "fixtures", "estudos_chaves", "ESTUDOS-SINTETICOS.json")
with open(FIXTURE, encoding="utf-8") as _h:
    ITENS = json.load(_h)["ITENS"]
POR_ID = {i["item_id"]: i for i in ITENS}
CHAVES = ("CULTURA", "PROBLEMA", "REGIAO_DO_FATO")


def _decisao(universo="T5"):
    return adm.Decisao(item="x", universo=universo, resultado=adm.SIM, regra="teste", motivo="teste",
                       evidencia={}, versao=adm.VERSAO_DA_REGRA)


def _janela(texto, universo="T5", **extra):
    return adm.janela_declarada(dict({"texto": texto, "published_at": "2024-01-01"}, **extra),
                                _decisao(universo))


class AsFixturesSaoSinteticas(unittest.TestCase):

    def test_toda_fixture_esta_marcada_sintetica(self):
        for i in ITENS:
            self.assertIs(True, i["SINTETICA"], i["item_id"])
            self.assertTrue(i["texto"].startswith("[SINTETICA]"), i["item_id"])
            self.assertNotIn("doi", i, i["item_id"])


class OExtratorLeOQueOTextoDiz(unittest.TestCase):

    def test_cada_fixture_da_o_esperado(self):
        for i in ITENS:
            r = EC.chaves_do_estudo(i["texto"])
            self.assertEqual(i["ESPERADO"], {k: r[k]["VALOR"] for k in CHAVES}, i["item_id"])

    def test_nomes_cientificos_comuns_ingles_e_italiano(self):
        casos = {"Vitis vinifera": "vite", "grapevine": "vite", "Olea europaea": "olivo", "olive": "olivo",
                 "olivo": "olivo"}
        for forma, nome in casos.items():
            self.assertEqual([nome], EC.chaves_do_estudo("[SINTETICA] %s." % forma)["CULTURA"]["VALOR"], forma)
        pragas = {"Plasmopara viticola": "peronospora", "downy mildew": "peronospora",
                  "peronospora": "peronospora", "Botrytis cinerea": "botrite", "Lobesia botrana": "tignoletta",
                  "Bactrocera oleae": "mosca dell'olivo", "Xylella fastidiosa": "xylella",
                  "Erysiphe necator": "oidio", "mosca dell’olivo": "mosca dell'olivo"}
        for forma, nome in pragas.items():
            self.assertEqual([nome], EC.chaves_do_estudo("[SINTETICA] %s." % forma)["PROBLEMA"]["VALOR"], forma)


class D112OTrechoELiteral(unittest.TestCase):

    def test_todo_valor_tem_span_literal_do_texto(self):
        n = 0
        for i in ITENS:
            r = EC.chaves_do_estudo(i["texto"])
            for k in CHAVES:
                if r[k]["VALOR"] == EC.AUSENCIA:
                    # LOTE6-INTEGRA (ajuste DECLARADO): sem trecho a procedencia e «UNKNOWN», a palavra da
                    # COL-LAW-221 (D112, leis/afirmacao_da_fonte.ENTITY_SOURCES); o VALOR continua «NAO SEI».
                    self.assertEqual("UNKNOWN", r[k]["ENTITY_SOURCE"], (i["item_id"], k))
                    self.assertIn(r[k]["ENTITY_SOURCE"], AF.ENTITY_SOURCES)
                    self.assertEqual([], r[k]["SPANS"], (i["item_id"], k))
                    continue
                self.assertEqual("SPAN", r[k]["ENTITY_SOURCE"])
                self.assertTrue(r[k]["SPANS"])
                for s in r[k]["SPANS"]:
                    self.assertEqual(s["TRECHO"], i["texto"][s["INICIO"]:s["FIM"]], (i["item_id"], k, s))
                    self.assertIn(s["VALOR"], r[k]["VALOR"])
                    n += 1
                    self.assertIn(s["TRECHO"], r[k]["BASE"], (i["item_id"], k))   # BASE = o trecho literal
        self.assertGreater(n, 20)

    def test_o_trecho_guarda_maiusculas_e_acentos_da_fonte(self):
        r = EC.chaves_do_estudo("[SINTETICA] Infezioni di Plasmopara viticola su vite nei vigneti; Mosca dell’Olivo.")
        self.assertIn("Plasmopara viticola", [s["TRECHO"] for s in r["PROBLEMA"]["SPANS"]])
        self.assertIn("Mosca dell’Olivo", [s["TRECHO"] for s in r["PROBLEMA"]["SPANS"]])

    def test_um_trecho_uma_entidade(self):
        r = EC.chaves_do_estudo("[SINTETICA] Lobesia botrana in vineyards.")
        self.assertEqual(["tignoletta"], r["PROBLEMA"]["VALOR"])
        self.assertEqual(1, len(r["PROBLEMA"]["SPANS"]))


class AmbiguoENaoSei(unittest.TestCase):

    def test_forma_ambigua_sozinha_nao_da_cultura(self):
        r = EC.chaves_do_estudo(POR_ID["SINT-05"]["texto"])
        self.assertEqual(EC.AUSENCIA, r["CULTURA"]["VALOR"])
        self.assertEqual(["vite"], [a["VALOR"] for a in r["CULTURA"]["AMBIGUAS"]])
        self.assertIn("AMBIGUO", r["CULTURA"]["PORQUE"])

    def test_forma_ambigua_conta_quando_ha_outra_sem_ambiguidade(self):
        r = EC.chaves_do_estudo(POR_ID["SINT-14"]["texto"])
        self.assertEqual(["vite"], r["CULTURA"]["VALOR"])
        self.assertIn("vite", [s["TRECHO"].lower() for s in r["CULTURA"]["SPANS"]])
        self.assertEqual([], r["CULTURA"]["AMBIGUAS"])

    def test_lugar_homonimo_so_depois_de_provincia_di(self):
        self.assertEqual(EC.AUSENCIA, EC.chaves_do_estudo(POR_ID["SINT-09"]["texto"])["REGIAO_DO_FATO"]["VALOR"])
        self.assertEqual(["Potenza"], EC.chaves_do_estudo(POR_ID["SINT-10"]["texto"])["REGIAO_DO_FATO"]["VALOR"])


class OLugarDoEstudoNuncaEAfiliacao(unittest.TestCase):

    def test_afiliacao_nunca_vira_regiao_mesmo_com_verbo_de_experimento(self):
        for sid, nome, prov in (("SINT-02", "Florence", "Firenze"), ("SINT-03", "Pisa", "Pisa"),
                                ("SINT-13", "Naples", "Napoli")):
            r = EC.chaves_do_estudo(POR_ID[sid]["texto"])["REGIAO_DO_FATO"]
            self.assertNotIn(prov, r["VALOR"] if r["VALOR"] != EC.AUSENCIA else [], sid)
            self.assertIn(nome, [x["TRECHO"] for x in r["RECUSADOS"] if "AFILIACAO" in x["PORQUE"]], sid)

    def test_nomear_um_lugar_nao_e_dizer_onde_o_estudo_foi_feito(self):
        r = EC.chaves_do_estudo(POR_ID["SINT-03"]["texto"])["REGIAO_DO_FATO"]
        self.assertEqual(EC.AUSENCIA, r["VALOR"])
        self.assertIn("Apulia", [x["TRECHO"] for x in r["RECUSADOS"]])

    def test_linguagem_de_incidencia_nao_e_lugar_do_estudo(self):
        # CAP-SCI: «established in Apulia» e a praga instalada, nao o ensaio; «raccolta» e a colheita
        for sid in ("SINT-15", "SINT-16"):
            r = EC.chaves_do_estudo(POR_ID[sid]["texto"])["REGIAO_DO_FATO"]
            self.assertEqual(EC.AUSENCIA, r["VALOR"], sid)
            self.assertIn("Puglia", [x["VALOR"] for x in r["RECUSADOS"]], sid)

    def test_lugares_coordenados_na_mesma_frase(self):
        r = EC.chaves_do_estudo(POR_ID["SINT-01"]["texto"])["REGIAO_DO_FATO"]
        self.assertEqual(["Puglia", "Sicilia"], r["VALOR"])
        self.assertEqual(["REGIAO"], r["PRECISAO"])


class CapSciEstudoNuncaViraIncidencia(unittest.TestCase):

    def test_problema_e_nomeado_nunca_presente(self):
        for i in ITENS:
            p = EC.chaves_do_estudo(i["texto"])["PROBLEMA"]
            if p["VALOR"] != EC.AUSENCIA:
                self.assertEqual("NOMEADO_NO_ESTUDO", p["ESTADO"], i["item_id"])
            self.assertNotEqual("PRESENTE", p.get("ESTADO"))
            self.assertIn("CAP-SCI", p["LEI"])

    def test_a_janela_t5_carrega_cap_sci_e_nao_toca_no_facto(self):
        j = _janela(POR_ID["SINT-01"]["texto"])
        self.assertEqual("NAO", j["ORIGEM"]["CAP_SCI"]["E_INCIDENCIA_DE_CAMPO"])
        self.assertEqual("LOCAL_DO_ESTUDO", j["REGIAO_DO_FATO"]["KIND"])
        self.assertEqual("NOMEADO_NO_ESTUDO", j["PROBLEMA"]["ESTADO"])
        self.assertEqual(adm.AUSENCIA, j["TEMPOS"]["FACT_TIME"])
        # PUBLICACAO != PERIODO: com published_at declarado, a JANELA continua NAO SEI
        self.assertEqual(adm.AUSENCIA, j["JANELA"]["VALOR"])
        self.assertEqual(adm.AUSENCIA, j["FASE"]["VALOR"])

    def test_fact_location_declarado_continua_a_mandar(self):
        j = _janela(POR_ID["SINT-01"]["texto"], fact_location="Veneto", fact_location_basis="SINTETICA")
        self.assertEqual("Veneto", j["REGIAO_DO_FATO"]["VALOR"])
        self.assertEqual("item.fact_location", j["REGIAO_DO_FATO"]["VEIO_DE"])


class SoOUniversoDeEstudo(unittest.TestCase):

    def test_fora_de_t5_a_janela_nao_usa_o_extrator_de_estudo(self):
        for u in ("T10", "T3", "T2", "T7"):
            j = _janela(POR_ID["SINT-01"]["texto"], universo=u)
            self.assertNotIn("CAP_SCI", j["ORIGEM"], u)
            self.assertNotEqual("NOMEADO_NO_ESTUDO", j["PROBLEMA"].get("ESTADO"), u)
            self.assertEqual(adm.AUSENCIA, j["REGIAO_DO_FATO"]["VALOR"], u)

    def test_t5_passa_de_nao_sei_a_valor(self):
        j = adm.janela_para_o_ready({"texto": POR_ID["SINT-02"]["texto"], "published_at": "2023-11-15"},
                                    _decisao("T5"))
        self.assertEqual(["olivo"], j["CULTURA"]["VALOR"])
        # CHAVE-PROBLEMA — AJUSTE DECLARADO: contrato PROBLEMA/v1, UM nome (antes, a lista com um nome)
        self.assertEqual("mosca dell'olivo", j["PROBLEMA"]["VALOR"])
        self.assertEqual((True, "conforme PROBLEMA/v1"),
                         AF.problema_conforme(j["PROBLEMA"], POR_ID["SINT-02"]["texto"]))
        self.assertEqual(["Lecce"], j["REGIAO_DO_FATO"]["VALOR"])
        self.assertEqual(2, j["PRECISAO"]["CHAVES_COM_VALOR"])
        for c in adm.QUATRO_CHAVES:        # a forma que a trava da 033 exige
            self.assertTrue({"VALOR", "VEIO_DE", "BASE"} <= set(j[c]), c)
            self.assertNotIn(j[c]["VALOR"], (None, "", []), c)


class SemSegundoVocabulario(unittest.TestCase):

    def test_toda_forma_de_cultura_vem_de_um_dono(self):
        donos = {EC._dobrar(t) for ts in T6.CULTURAS.values() for t in ts}
        donos |= {EC._dobrar(c) for c in list(BC.CULTURAS) + list(BC.FORMAS)}
        for v in (adm.CULTURA_OBRIGATORIA["T1"], adm.CULTURA_OBRIGATORIA_EN["T1"], adm.CULTURA_SO_DA_CHAVE):
            donos |= {EC._dobrar(f) for f in v.split("|")}
        for forma, _nome, _dono in EC.vocabulario_de_cultura():
            self.assertIn(forma, donos)

    def test_toda_forma_de_praga_e_de_lugar_vem_de_um_dono(self):
        t6 = {t for ts in T6.PROBLEMAS.values() for t in ts}
        for forma, _n, _d, e_regex in EC.vocabulario_de_problema():
            self.assertTrue(forma is BC._RE_PROBLEMA if e_regex else forma in t6)
        import fato_local as FL
        lugares = {EC._dobrar(x) for x in list(FL.REGIOES) + list(FL.PROVINCIAS) + list(T6.PAIS_IT)}
        lugares |= {EC._dobrar(t) for d in (T6.REGIOES_EN, T6.ZONAS_IT) for ts in d.values() for t in ts}
        lugares |= {EC._dobrar(t) for ts in T6.EXONIMOS.values() for t in ts}
        for forma, *_ in EC.vocabulario_de_lugar():
            self.assertIn(forma, lugares)

    def test_o_codigo_do_extrator_nao_escreve_nomes_de_cultura_nem_de_praga(self):
        with open(os.path.join(RAIZ, "leis", "estudo_chaves.py"), encoding="utf-8") as h:
            arvore = ast.parse(h.read())
        docs = {id(n.body[0].value) for n in ast.walk(arvore)
                if isinstance(n, (ast.Module, ast.FunctionDef)) and n.body
                and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
        literais = " ".join(n.value.lower() for n in ast.walk(arvore)
                            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs)
        for nome in ("plasmopara", "grapevine", "botrytis", "bactrocera", "xylella", "olea europaea",
                     "tuscany", "apulia", "lobesia"):
            self.assertNotIn(nome, literais, nome)

    def test_o_olivo_entrou_no_lexico_t6_sem_mudar_as_consultas(self):
        self.assertIn("olivo", T6.CULTURAS)
        self.assertEqual(12, len(T6.PARES))
        self.assertEqual(BC.nome_do_problema("bactrocera oleae"), "mosca dell'olivo")
        self.assertIn("mosca dell'olivo", T6.PROBLEMAS)


class OReprocessoDevolveRevisoesENaoGrava(unittest.TestCase):

    def test_revisoes_no_formato_de_rever(self):
        fora = RE.reprocessar(ITENS)
        self.assertIs(False, fora["GRAVOU_NO_BANCO"])
        self.assertEqual(len(ITENS), fora["CONTA"]["ITENS"])
        self.assertEqual(len(ITENS), fora["CONTA"]["REVISOES"])
        self.assertTrue(fora["VERSAO_DO_EXTRATOR"].startswith("estudos-chaves@"))
        for it in fora["ITENS"]:
            (r,) = it["REVISOES"]
            self.assertEqual({"CAMPO", "VALOR", "BASE"}, set(r))
            self.assertEqual("janela_declarada", r["CAMPO"])
            v = json.loads(r["VALOR"])
            self.assertEqual(r["VALOR"], json.dumps(v, ensure_ascii=False, sort_keys=True))
            # CHAVE-PROBLEMA (27/09) — AJUSTE DECLARADO: o PROBLEMA saiu no contrato PROBLEMA/v1. Os nomes
            # que o estudo cita estao em CANDIDATOS (a mesma lista de antes); o VALOR e UM nome, ou NAO SEI
            # quando ha mais de um (D112). A lista esperada continua a mesma, e o VALOR passa a ser conferido.
            esperado = POR_ID[it["ITEM_ID"]]["ESPERADO"]
            lido = {k: v[k]["VALOR"] for k in CHAVES}
            lido["PROBLEMA"] = [c["NOME"] for c in v["PROBLEMA"]["CANDIDATOS"]] or "NAO SEI"
            self.assertEqual(esperado, lido)
            unico = esperado["PROBLEMA"][0] if len(esperado["PROBLEMA"]) == 1 and esperado["PROBLEMA"] != "NAO SEI" else "NAO SEI"
            self.assertEqual(unico, v["PROBLEMA"]["VALOR"], it["ITEM_ID"])

    def test_mesmo_codigo_duas_vezes_nao_repete(self):
        a = RE.reprocessar(ITENS)
        atuais = [dict(i, janela_declarada=x["REVISOES"][0]["VALOR"]) for i, x in zip(ITENS, a["ITENS"])]
        b = RE.reprocessar(atuais)
        self.assertEqual(a["VERSAO_DO_EXTRATOR"], b["VERSAO_DO_EXTRATOR"])
        self.assertEqual(0, b["CONTA"]["REVISOES"])
        self.assertEqual(len(ITENS), b["CONTA"]["JA_ERAM_ASSIM"])

    def test_a_conta_diz_quantos_saem_de_nao_sei(self):
        c = RE.reprocessar(ITENS)["CONTA"]
        esp = {k: sum(1 for i in ITENS if i["ESPERADO"][k] != "NAO SEI") for k in CHAVES}
        self.assertEqual(esp["CULTURA"], c["COM_CULTURA"])
        # CHAVE-PROBLEMA — AJUSTE DECLARADO: COM_PROBLEMA conta o VALOR do contrato PROBLEMA/v1 (UM nome);
        # o estudo que nomeia dois problemas fica NAO SEI e e contado a parte, em PROBLEMA_SO_CANDIDATOS.
        um = sum(1 for i in ITENS if i["ESPERADO"]["PROBLEMA"] != "NAO SEI" and len(i["ESPERADO"]["PROBLEMA"]) == 1)
        self.assertEqual(um, c["COM_PROBLEMA"])
        self.assertEqual(esp["PROBLEMA"] - um, c["PROBLEMA_SO_CANDIDATOS"])
        self.assertEqual(esp["REGIAO_DO_FATO"], c["COM_REGIAO_DO_ESTUDO"])
        self.assertEqual(1, c["SO_FORMAS_AMBIGUAS"])

    def test_sem_item_id_e_erro_declarado_e_nao_revisao(self):
        fora = RE.reprocessar([{"texto": "[SINTETICA] grapevine", "published_at": "2024"}])
        self.assertEqual(1, fora["CONTA"]["SEM_ITEM_ID"])
        self.assertEqual(0, fora["CONTA"]["REVISOES"])

    def test_o_script_nao_abre_o_banco(self):
        with open(os.path.join(RAIZ, "admissao", "reprocessar_estudos_chaves.py"), encoding="utf-8") as h:
            arvore = ast.parse(h.read())
        importados = {a.name for n in ast.walk(arvore) if isinstance(n, (ast.Import, ast.ImportFrom))
                      for a in n.names}
        self.assertNotIn("sala_de_espera", importados)
        chamadas = {getattr(n.func, "attr", getattr(n.func, "id", "")) for n in ast.walk(arvore)
                    if isinstance(n, ast.Call)}
        self.assertFalse({"rever", "pousar", "exigir_canonica"} & chamadas)

    def test_linha_de_comando(self):
        with tempfile.TemporaryDirectory() as d:
            saida = os.path.join(d, "rev.json")
            r = subprocess.run([sys.executable, os.path.join(RAIZ, "admissao", "reprocessar_estudos_chaves.py"),
                                "--entrada", FIXTURE, "--saida", saida], capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stderr)
            with open(saida, encoding="utf-8") as h:
                self.assertEqual(len(ITENS), len(json.load(h)["ITENS"]))
            self.assertIn('"GRAVOU_NO_BANCO": false', r.stdout)


if __name__ == "__main__":
    unittest.main()
