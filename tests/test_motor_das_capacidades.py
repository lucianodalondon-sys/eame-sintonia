#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O MOTOR DAS CAPACIDADES (INT-R7-CAPS), atacado.

    python3 -m unittest tests.test_motor_das_capacidades -v

⚠️ DADO SINTETICO DECLARADO: tests/dados/int-r7/SINTETICO-R7-SALA-EXPORT.json
(`SINTETICO: true`, enderecos com /SINTETICO/). Os boletins APOL/ARIF sao frases
curtas ja publicadas no desenho CAP-WIN R5, alteradas de proposito; o limite 10%
do ARIF, a mudanca de recomendacao e o Gargano DEDUZIDO sao INVENTADOS para
provar as regras D112. Estudos e DOI 10.0000/* sao ficticios.
"""
import copy
import json
import sys
import unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in (RAIZ / "motor", RAIZ / "leis", RAIZ / "provas" / "int_r7"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import motor_das_capacidades as M            # noqa: E402
import cap_win as WIN                         # noqa: E402

NAO_SEI = M.NAO_SEI
EXPORT = RAIZ / "tests" / "dados" / "int-r7" / "SINTETICO-R7-SALA-EXPORT.json"
HOJE = date(2026, 9, 27)

APOL_BRLE, APOL_TA = "SINT-R7-APOL-38-BRLE#0", "SINT-R7-APOL-38-TA#0"
ARIF37, ARIF38, GARGANO = "SINT-R7-ARIF-37#0", "SINT-R7-ARIF-38#0", "SINT-R7-ARIF-38#1"
EVT = "SINT-R7-ARIF-EVT#0"
EST1, EST2, EST3 = "SINT-R7-EST-01", "SINT-R7-EST-02", "SINT-R7-EST-03"
ESTUDOS = {EST1, EST2, EST3}


def export():
    return json.loads(EXPORT.read_text(encoding="utf-8"))


def entrada(mexer=None):
    e = export()
    if mexer:
        mexer(e)
    return M.entrada_do_export(e)


_CACHE = {}


def saida():
    if "s" not in _CACHE:
        _CACHE["s"] = M.rodar(entrada(), HOJE, "SINT-HEAD")
    return copy.deepcopy(_CACHE["s"])


def linha(e, item_id):
    return next(l for l in e["LINHAS"] if l["item_id"] == item_id)


def janela(s):
    (j,) = s["CAP_WIN"]["CROP_WINDOWS"]
    return j


def objs(s, comp):
    return s["ITENS_POR_FERRAMENTA"][comp]


def rels(s, tipo):
    return [r for r in s["D112"]["RELACOES"] if r["TIPO"] == tipo]


class A_AEntradaDaSala(unittest.TestCase):
    """O export read-only -> READY | JANELA | RAW, sem nada completado."""

    def test_A1_o_ready_tem_so_os_campos_do_dono(self):
        for r in entrada()["ITENS"]:
            self.assertEqual(tuple(r["READY"]), M.CI.CAMPOS_DO_READY)
            self.assertEqual(r["READY"]["ESTADO"], "PRONTO_PARA_INTELIGENCIA")

    def test_A2_url_e_document_id_vem_do_raw_e_nao_entram_no_ready(self):
        e = entrada()
        for r in e["ITENS"]:
            self.assertNotIn("URL", r["READY"])
            self.assertNotIn("DOCUMENT_ID", r["READY"])
        self.assertEqual(e["RAW"]["9001"]["URL"], "https://www.apol.it/SINTETICO/bollettino-mosca-38-brle")
        self.assertEqual(e["RAW"]["9102"]["DOCUMENT_ID"], NAO_SEI)

    def test_A3_janela_viaja_dentro_do_ready(self):
        # LOTE6-INTEGRA (ajuste DECLARADO): o dono do READY (sala_de_espera.CAMPOS_DO_READY, D58
        # QUATRO-CHAVES-NA-SALA, ja na base 18461b92) leva JANELA_DECLARADA DENTRO do READY. Este teste
        # nasceu num ramo anterior a D58 e pedia-a ao lado; agora pede-a onde o dono a pos, e so la.
        r = entrada()["ITENS"][0]
        self.assertEqual(set(r), {"READY"})
        self.assertEqual(r["READY"]["JANELA_DECLARADA"]["CULTURA"]["VALOR"], "olivo")

    def test_A4_campo_de_fora_do_ready_e_recusado(self):
        e = entrada()
        e["ITENS"][0]["ADAMA_PRODUCT_ID"] = "X"
        with self.assertRaisesRegex(M.LeiViolada, "IDENTIDADE_DE_FORA_DO_READY"):
            M.rodar(e, HOJE)
        e = entrada()
        e["ITENS"][0]["READY"]["DOI"] = "10.0000/x"
        with self.assertRaisesRegex(Exception, "IDENTIDADE_DE_FORA_DO_READY"):
            M.rodar(e, HOJE)

    def test_A5_export_de_outro_contrato_e_recusado(self):
        with self.assertRaises(M.LeiViolada):
            M.entrada_do_export({"EXPORT": "OUTRA_COISA", "LINHAS": []})

    def test_A6_sem_hoje_nao_ha_agora(self):
        with self.assertRaises(M.LeiViolada):
            M.rodar(entrada(), "2026-09-27")

    def test_A7_item_id_repetido_e_recusado(self):
        def dup(e):
            e["LINHAS"][1]["item_id"] = e["LINHAS"][0]["item_id"]
        with self.assertRaisesRegex(M.LeiViolada, "repetido"):
            M.rodar(entrada(dup), HOJE)


class B_UmaCorridaSo(unittest.TestCase):
    """As duas capacidades leem o MESMO livro: um RUN_ID, nenhum recontar."""

    def test_B1_um_run_id_para_tudo(self):
        s = saida()
        rid = s["INTELLIGENCE_RUN_ID"]
        self.assertEqual(s["CORRIDA"]["INTELLIGENCE_RUN_ID"], rid)
        self.assertEqual(s["CAP_WIN"]["INTELLIGENCE_RUN_ID"], rid)
        self.assertEqual(s["CAP_SCI"]["INTELLIGENCE_RUN_ID"], rid)
        self.assertEqual({v["RUN"] for v in s["CAPACIDADES_EXECUTADAS"].values()}, {rid})
        self.assertEqual(set(s["CAPACIDADES_EXECUTADAS"]), {"CAP-WIN", "CAP-SCI"})

    def test_B2_todo_ready_atravessa_e_ninguem_some(self):
        s = saida()
        n = len(export()["LINHAS"])
        self.assertEqual(len(s["LINEAGE"]), n)
        self.assertEqual(s["CAP_SCI"]["UNIVERSO"]["ITENS"], n)
        win = s["CAP_WIN"]
        vistos = ({e["ITEM_ID"] for j in win["CROP_WINDOWS"] for e in j["EVIDENCE"]}
                  | {x["ITEM_ID"] for x in win["NOT_POSSIBLE"]} | {x["ITEM_ID"] for x in win["FORA"]})
        self.assertLessEqual(vistos, {l["item_id"] for l in export()["LINHAS"]})
        self.assertEqual(s["CAP_SCI"]["UNIVERSO"]["JULGADOS"] + s["CAP_SCI"]["UNIVERSO"]["FORA"], n)

    def test_B3_a_mesma_entrada_da_a_mesma_corrida(self):
        self.assertEqual(M.rodar(entrada(), HOJE)["INTELLIGENCE_RUN_ID"], saida()["INTELLIGENCE_RUN_ID"])


class C_Triagem(unittest.TestCase):
    """Estudo vai a CAP-SCI; ESTUDO NUNCA VIRA INCIDENCIA DE CAMPO."""

    def test_C1_estudos_vao_a_cap_sci_e_o_resto_a_cap_win(self):
        t = saida()["TRIAGEM"]
        self.assertEqual({i for i, v in t.items() if v["CAPACIDADE"] == "CAP-SCI"}, ESTUDOS)

    def test_C2_nenhum_estudo_numa_janela(self):
        s = saida()
        for j in s["CAP_WIN"]["CROP_WINDOWS"]:
            self.assertFalse({e["ITEM_ID"] for e in j["EVIDENCE"]} & ESTUDOS)
        for o in objs(s, "windows"):
            self.assertFalse({p["ITEM_ID"] for p in o["PROVA"]} & ESTUDOS)

    def test_C3_estudo_fora_da_cap_win_nao_pede_par_em_campo(self):
        s = saida()
        self.assertEqual({x["ITEM_ID"] for x in s["CAP_WIN"]["FORA"]}, ESTUDOS)
        pedidos = {q["REQUIRED_SCOPE"]["ITEM_ID"] for q in s["CAP_WIN"]["REQUIREMENTS"]}
        self.assertFalse(pedidos & ESTUDOS)

    def test_C4_boletim_nao_e_julgado_como_estudo(self):
        s = saida()
        self.assertEqual({e["ITEM_ID"] for e in s["CAP_SCI"]["ESTUDOS"]}, ESTUDOS)
        self.assertIn(APOL_BRLE, {x["ITEM_ID"] for x in s["CAP_SCI"]["FORA"]})

    def test_C5_a_classe_declarada_pela_fonte_nao_decide(self):
        def cls(e):
            linha(e, APOL_BRLE)["source_declared_evidence_class"] = "SCIENTIFIC_RESULT"
        s = M.rodar(entrada(cls), HOJE)
        self.assertEqual(s["TRIAGEM"][APOL_BRLE]["CAPACIDADE"], "CAP-WIN")

    def test_C6_os_estudos_dizem_o_que_nao_sao(self):
        for o in objs(saida(), "science"):
            self.assertIn("INCIDENCIA_DE_CAMPO", o["CHAVES"]["INTERPRETACAO_DO_SISTEMA"]["NAO_E"])


class D_LugarSoComSustentacaoExplicita(unittest.TestCase):
    """D112(a) — pela lei que ja existe (leis/lugar_do_fato.sustenta_fato)."""

    def test_D1_escrito_e_citado_sustentam(self):
        for o in ("ESCRITO", "CITADO"):
            self.assertTrue(M.lugar_sustentado("Puglia", "SINTETICO · base", o)["SUSTENTADO"])

    def test_D2_da_fonte_deduzido_lista_e_nao_sei_nao_sustentam(self):
        for o in ("DA_FONTE", "DEDUZIDO", "LISTA_TERRITORIAL", "NAO SEI", None, "INVENTADO"):
            r = M.lugar_sustentado("Puglia", "SINTETICO · base", o)
            self.assertFalse(r["SUSTENTADO"], o)
            self.assertEqual(r["VALOR"], NAO_SEI)
            self.assertEqual(r["VALOR_RECUSADO"], "Puglia")

    def test_D3_sem_base_nao_sustenta_mesmo_escrito(self):
        self.assertFalse(M.lugar_sustentado("Puglia", "NAO SEI", "ESCRITO")["SUSTENTADO"])

    def test_D4_regiao_da_fonte_vira_not_possible_e_pede_a_regiao(self):
        s = saida()
        np = {x["ITEM_ID"]: x for x in s["CAP_WIN"]["NOT_POSSIBLE"]}
        self.assertIn(GARGANO, np)
        self.assertIn("REGIAO_DO_FATO", np[GARGANO]["PORQUE"])
        req = next(q for q in s["CAP_WIN"]["REQUIREMENTS"] if q["REQUIREMENT_ID"] == np[GARGANO]["REQUIREMENT_ID"])
        self.assertIn("REGION_EM_CAMPO", req["REQUIREMENT"])
        lug = s["D112"]["LUGAR"][GARGANO]
        self.assertEqual(lug["JANELA_DECLARADA.REGIAO_DO_FATO"]["VEIO_DE"], "DA_FONTE")
        self.assertEqual(lug["JANELA_DECLARADA.SUBAREA"]["VALOR_RECUSADO"], "GARGANO_COSTIERO")

    def test_D5_afiliacao_nao_vira_local_do_estudo(self):
        e2 = next(e for e in saida()["CAP_SCI"]["ESTUDOS"] if e["ITEM_ID"] == EST2)
        self.assertEqual(e2["LOCAL_DO_ESTUDO"]["VALOR"], NAO_SEI)
        self.assertIn("LOCAL", e2["APLICABILIDADE"]["FALTA"])

    def test_D6_o_original_nao_muda_no_livro(self):
        s = saida()
        self.assertEqual(s["CORRIDA"]["LINEAGE"][[l["ITEM_ID"] for l in s["LINEAGE"]].index(EST2)]["ITEM_ID"], EST2)
        # a corrida le o READY como veio; so a copia das capacidades perde o lugar
        r = next(x for x in entrada()["ITENS"] if x["READY"]["ITEM_ID"] == EST2)
        self.assertEqual(r["READY"]["FACT_LOCATION"], "Italia")
        rc, _jd, rel = M.aplicar_d112_lugar(r)
        self.assertEqual(r["READY"]["FACT_LOCATION_BASIS"], "AFILIACAO · pais da instituicao dos autores")
        self.assertTrue(rc["FACT_LOCATION_BASIS"].startswith(NAO_SEI))
        self.assertEqual(rel["FACT_LOCATION"]["VALOR_RECUSADO"], "Italia")

    def test_D7_regiao_sustentada_passa(self):
        s = saida()
        self.assertEqual(janela(s)["REGION_ID"], "Puglia")
        self.assertTrue(s["D112"]["LUGAR"][APOL_BRLE]["JANELA_DECLARADA.REGIAO_DO_FATO"]["SUSTENTADO"])


class E_EntitySource(unittest.TestCase):
    """D112(b,c) — toda entidade com a procedencia; sem evidencia, NAO SEI."""

    def test_E1_toda_chave_do_contrato_tem_procedencia(self):
        s = saida()
        for comp, lista in s["ITENS_POR_FERRAMENTA"].items():
            for o in lista:
                ent = o["CHAVES"]["ENTITY_SOURCE"]
                for k in M.CHAVES_DO_POTE[comp]:
                    self.assertEqual(ent[k]["VALOR"], o["CHAVES"][k], (comp, k))
                    if o["CHAVES"][k] != NAO_SEI:
                        self.assertNotEqual(ent[k]["ENTITY_SOURCE"], NAO_SEI, (comp, k))
                    else:
                        self.assertIn("PORQUE", ent[k])

    def test_E2_a_procedencia_da_janela_e_por_item(self):
        es = objs(saida(), "windows")[0]["CHAVES"]["ENTITY_SOURCE"]
        self.assertEqual(es["CROP_ID"]["ENTITY_SOURCE"], "JANELA_DECLARADA.CULTURA")
        self.assertEqual({x["ITEM_ID"] for x in es["REGION_ID"]["POR_ITEM"]},
                         {APOL_BRLE, APOL_TA, ARIF37, ARIF38})
        self.assertTrue(all(x["VEIO_DE"] == "ESCRITO" for x in es["REGION_ID"]["POR_ITEM"]))
        self.assertEqual(es["DATE_OR_STAGE"]["VALOR"], NAO_SEI)

    def test_E3_a_procedencia_do_estudo_e_o_campo_do_fato(self):
        o = next(o for o in objs(saida(), "science") if o["CHAVES"]["DOI"] == "10.0000/sint.r7.01")
        es = o["CHAVES"]["ENTITY_SOURCE"]
        self.assertEqual(es["MOLECULE"]["ENTITY_SOURCE"], "FATO.molecule")
        self.assertEqual(es["STUDY_LOCATION"]["ENTITY_SOURCE"], "READY.FACT_LOCATION")
        self.assertEqual(es["STUDY_PERIOD"]["VALOR"], "campagna 2023")

    def test_E4_rede_nao_declarada_da_independencia_nao_sei(self):
        def sem_rede(e):
            for l in e["LINHAS"]:
                if isinstance(l["janela_declarada"], dict):
                    l["janela_declarada"].pop("REDE_DE_MONITORIZACAO", None)
        j = janela(M.rodar(entrada(sem_rede), HOJE))
        self.assertEqual(j["SUPPORTS"]["OBSERVACAO"]["INDEPENDENTES_PROVADOS"], NAO_SEI)


class F_FonteSeparadaDaInterpretacao(unittest.TestCase):
    """D112(d) — o que a fonte disse nunca se mistura com o que o sistema concluiu."""

    def test_F1_cada_objeto_traz_os_dois_blocos(self):
        for lista in saida()["ITENS_POR_FERRAMENTA"].values():
            for o in lista:
                self.assertIn("DA_FONTE", o["CHAVES"])
                self.assertIn("INTERPRETACAO_DO_SISTEMA", o["CHAVES"])

    def test_F2_o_juizo_nao_esta_no_bloco_da_fonte(self):
        o = objs(saida(), "windows")[0]["CHAVES"]
        fonte = json.dumps(o["DA_FONTE"])
        for juizo in ("NO_DEFENSIBLE_ACTION_YET", "WINDOW_OPEN_NOW", "CURRENT", "monitorizar"):
            self.assertNotIn(juizo, fonte)
        self.assertEqual(o["INTERPRETACAO_DO_SISTEMA"]["RESULT"], "NO_DEFENSIBLE_ACTION_YET")

    def test_F3_o_estudo_separa_o_fato_da_forca(self):
        o = next(o for o in objs(saida(), "science") if o["CHAVES"]["DOI"] == "10.0000/sint.r7.01")["CHAVES"]
        self.assertEqual(o["DA_FONTE"]["FATO"]["result"], "EFICAZ")
        self.assertNotIn("FORCA", o["DA_FONTE"])
        self.assertEqual(o["INTERPRETACAO_DO_SISTEMA"]["FORCA"]["NIVEL"], "FORTE")

    def test_F4_as_relacoes_separam_fonte_e_interpretacao(self):
        for r in saida()["D112"]["RELACOES"]:
            self.assertIn("DA_FONTE", r)
            self.assertIn("INTERPRETACAO_DO_SISTEMA", r)


class G_Relacoes(unittest.TestCase):
    """D112(e,f,g)."""

    def test_G1_mesma_redacao_em_tres_territorios_e_uma_instituicao(self):
        (r,) = [r for r in rels(saida(), M.MESMA_REDACAO) if r["INSTITUICOES"] == 1
                and r["POR_INSTITUICAO"][0]["INSTITUICAO"] == "IT-T3-010"]
        p = r["POR_INSTITUICAO"][0]
        self.assertEqual(p["TERRITORIOS"], ["BR", "LE", "TA"])
        self.assertEqual(p["APLICACOES"], 3)
        self.assertEqual(p["INSTITUICOES"], 1)
        self.assertIn("nunca como N fontes", r["INTERPRETACAO_DO_SISTEMA"])

    def test_G2_a_mesma_redacao_nao_soma_originador(self):
        j = janela(saida())
        self.assertEqual(j["SUPPORTS"]["OBSERVACAO"]["ORIGINADORES_DISTINTOS"], 2)

    def test_G3_territorio_nao_sustentado_da_aplicacoes_nao_sei(self):
        def sem_sub(e):
            linha(e, APOL_TA)["janela_declarada"]["SUBAREA"]["VEIO_DE"] = "DEDUZIDO"
        (r,) = [r for r in rels(M.rodar(entrada(sem_sub), HOJE), M.MESMA_REDACAO)
                if r["POR_INSTITUICAO"][0]["INSTITUICAO"] == "IT-T3-010"]
        self.assertEqual(r["POR_INSTITUICAO"][0]["APLICACOES"], NAO_SEI)
        self.assertEqual(r["POR_INSTITUICAO"][0]["TERRITORIOS"], ["BR", "LE"])

    def test_G4_limites_diferentes_sao_divergent_unresolved(self):
        (r,) = rels(saida(), M.DIVERGENT)
        self.assertEqual(r["CONTRADICAO"], "UNRESOLVED")
        self.assertEqual({tuple(g["LIMITE"]) for g in r["DA_FONTE"]}, {("4-5%",), ("10%",)})
        self.assertIn("NAO escolhe", r["INTERPRETACAO_DO_SISTEMA"])
        o = objs(saida(), "windows")[0]
        self.assertIn("DIVERGENT/UNRESOLVED", o["CONTRADIZ"])

    def test_G5_limites_iguais_nao_divergem(self):
        def igual(e):
            for i in (ARIF37, ARIF38):
                linha(e, i)["texto"] = linha(e, i)["texto"].replace("10%", "4-5%")
        self.assertEqual(rels(M.rodar(entrada(igual), HOJE), M.DIVERGENT), [])

    def test_G6_sem_numero_nao_ha_divergencia_inventada(self):
        def sem(e):
            for i in (ARIF37, ARIF38):
                linha(e, i)["texto"] = linha(e, i)["texto"].replace(
                    " (10% di infestazione attiva per le olive da olio)", "")
        self.assertEqual(rels(M.rodar(entrada(sem), HOJE), M.DIVERGENT), [])

    def test_G7_divergent_nunca_deixa_agir_agora(self):
        j = copy.deepcopy(janela(saida()))
        j["RESULT"] = WIN.ACT_NOW
        j["WHY"] = ["as quatro condicoes do W8 estao satisfeitas"]
        ctx = {"RUN_ID": "X", "RAW": entrada()["RAW"], "D112": {},
               "JANELA": {r["READY"]["ITEM_ID"]: r["READY"]["JANELA_DECLARADA"] for r in entrada()["ITENS"]},
               "READY": {r["READY"]["ITEM_ID"]: r["READY"] for r in entrada()["ITENS"]},
               "LINHA": {l["ITEM_ID"]: l for l in saida()["LINEAGE"]}}
        o, _ = M._objeto_da_janela(j, ctx, M.relacoes(j))
        self.assertEqual(o["CHAVES"]["INTERPRETACAO_DO_SISTEMA"]["RESULT"], WIN.NO_DEFENSIBLE_ACTION_YET)
        self.assertEqual(o["CHAVES"]["INTERPRETACAO_DO_SISTEMA"]["RESULT_DA_CAP_WIN"], WIN.ACT_NOW)
        o, _ = M._objeto_da_janela(j, ctx, [])
        self.assertEqual(o["CHAVES"]["INTERPRETACAO_DO_SISTEMA"]["RESULT"], WIN.ACT_NOW)

    def test_G8_mudanca_de_recomendacao_e_temporal_change_e_nao_prova_o_campo(self):
        (r,) = rels(saida(), M.TEMPORAL_CHANGE)
        self.assertEqual((r["DE"], r["PARA"]), (ARIF37, ARIF38))
        self.assertTrue(r["DA_FONTE"]["ANTES"]["MANDA_NAO_TRATAR"])
        self.assertFalse(r["DA_FONTE"]["DEPOIS"]["MANDA_NAO_TRATAR"])
        self.assertTrue(r["NAO_PROVA"].startswith("MUDANCA_NO_CAMPO"))
        # e nao vira contradicao entre as observacoes
        self.assertEqual(janela(saida())["CONTRADICTIONS"], [])

    def test_G9_tempos_que_se_tocam_nao_sao_antes_e_depois(self):
        def junto(e):
            linha(e, ARIF37)["fact_time"] = "2026-09-14/2026-09-20"
            linha(e, ARIF37)["captured_at"] = "2026-09-21T08:00:00+00:00"
        self.assertEqual(rels(M.rodar(entrada(junto), HOJE), M.TEMPORAL_CHANGE), [])

    def test_G10_territorios_diferentes_nao_sao_mudanca_no_tempo(self):
        def outro(e):
            linha(e, ARIF38)["janela_declarada"]["SUBAREA"]["VALOR"] = "SALENTO"
        self.assertEqual(rels(M.rodar(entrada(outro), HOJE), M.TEMPORAL_CHANGE), [])

    def test_G11_mesma_recomendacao_nao_e_mudanca(self):
        def igual(e):
            linha(e, ARIF38)["texto"] = linha(e, ARIF38)["texto"].replace(
                "Si consiglia di intensificare il monitoraggio settimanale.",
                "Non si ritiene giustificato alcun trattamento.")
        self.assertEqual(rels(M.rodar(entrada(igual), HOJE), M.TEMPORAL_CHANGE), [])


class P_OPoteV2(unittest.TestCase):
    """A saida no contrato de entrada do gerador ce775ff5."""

    def test_P1_intelligence_run_id_no_topo(self):
        s = saida()
        self.assertEqual(next(iter(s)), "INTELLIGENCE_RUN_ID")
        self.assertEqual(s["SOURCE_HEAD"], "SINT-HEAD")
        self.assertEqual(s["CORTE"], "2026-09-27T12:00:00+00:00")
        self.assertIn("ce775ff5ad2287d8f6fc19bee5feebd02843b8de", s["CONTRATO_DE_SAIDA_PARA"])

    def test_P2_prova_com_url_e_published_at_e_fact_time_da_corrida(self):
        s = saida()
        ft = {l["ITEM_ID"]: l["FACT_TIME"] for l in s["LINEAGE"]}
        for lista in s["ITENS_POR_FERRAMENTA"].values():
            for o in lista:
                for p in o["PROVA"]:
                    self.assertTrue(p["URL"].startswith("https://") and "/SINTETICO/" in p["URL"])
                    self.assertEqual(p["PUBLISHED_AT"], p["PUBLICADO_EM"])
                    self.assertEqual(p["FACT_TIME"], ft[p["ITEM_ID"]])
        p = objs(s, "science")[0]["PROVA"][0]
        self.assertNotEqual(p["FACT_TIME"], p["PUBLISHED_AT"])

    def test_P3_so_especies_que_nao_prometem_mais(self):
        s = saida()
        self.assertEqual({o["ESPECIE"] for l in s["ITENS_POR_FERRAMENTA"].values() for o in l},
                         {"SINAL", "FATO_PRESENTE_SOBRE_O_FUTURO", "RENDIMENTO_DE_FONTE"})
        self.assertNotIn("meeting", s["ITENS_POR_FERRAMENTA"])

    def test_P4_o_futuro_vai_para_o_radar_futuro(self):
        (o,) = objs(saida(), "future")
        self.assertEqual(o["PROVA"][0]["ITEM_ID"], EVT)
        self.assertEqual(o["ESPECIE"], "FATO_PRESENTE_SOBRE_O_FUTURO")

    def test_P5_o_rendimento_vem_da_lineage(self):
        s = saida()
        r = {o["CHAVES"]["SOURCE_ID"]: o["CHAVES"] for o in objs(s, "sources")}
        self.assertEqual(r["IT-T3-008"]["ITENS_LIDOS"], 4)
        self.assertEqual(r["SINT-T6"]["ITENS_QUE_PASSARAM_G0"], 3)
        self.assertEqual(r["SINT-T6"]["PASSARAM_G0_SEM_DOCUMENT_ID_FORA_DA_PROVA"], [EST2])

    def test_P5b_o_motor_nao_cunha_document_id(self):
        """Nasceu do mutante M19: sem document_key no RAW, a prova diz NAO SEI."""
        (o,) = [o for o in objs(saida(), "science") if o["PROVA"][0]["ITEM_ID"] == EST2]
        self.assertEqual(o["PROVA"][0]["DOCUMENT_ID"], NAO_SEI)
        self.assertEqual(saida()["ITENS_POR_FERRAMENTA"]["windows"][0]["PROVA"][0]["DOCUMENT_ID"],
                         "SINT-DOC-APOL-38-BRLE")

    def test_P5c_evidencia_sem_g0_fica_fora_da_prova_e_a_vista(self):
        """Nasceu do mutante M20: a regra de um item sem tempo continua lida, mas
        ele nao prova nada no pote (so G0 = PASSOU prova)."""
        def sem_tempo(e):
            linha(e, ARIF37)["fact_time"] = "NAO SEI"
            linha(e, ARIF37)["fact_time_basis"] = "NAO SEI"
        s = M.rodar(entrada(sem_tempo), HOJE)
        o = objs(s, "windows")[0]
        self.assertNotIn(ARIF37, {p["ITEM_ID"] for p in o["PROVA"]})
        self.assertEqual(o["CHAVES"]["EVIDENCIA_SEM_G0_FORA_DA_PROVA"], [ARIF37])
        self.assertIn(ARIF37, {e["ITEM_ID"] for e in janela(s)["EVIDENCE"]})

    def test_P5d_futuro_com_outra_falta_nao_vai_ao_radar_futuro(self):
        """Nasceu do mutante M30: so o item que G0 bloqueou SO por ser futuro
        prova um facto presente sobre o futuro."""
        def sem_base(e):
            linha(e, EVT)["fact_time_basis"] = "NAO SEI"
        s = M.rodar(entrada(sem_base), HOJE)
        self.assertEqual(objs(s, "future"), [])
        (n,) = [x for x in s["NAO_ENVIADOS_AO_POTE"] if x["COMPARTIMENTO"] == "future"]
        self.assertEqual(n["MOTIVO"], "FUTURO_COM_OUTRA_FALTA")
        self.assertIn("FACT_TIME:SEM_BASE", n["DETALHE"])

    def test_P6_o_gerador_de_verdade_aceita(self):
        import tempfile
        import aceite_pelo_gerador as G
        if not G.blob_existe():
            self.skipTest("NAO SEI: o commit do gerador ce775ff5 nao esta neste clone")
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump(saida(), fh, ensure_ascii=False)
        pote = G.correr_gerador(fh.name)
        Path(fh.name).unlink()
        self.assertEqual(pote["SCHEMA"], "POTE_INTELLIGENCE_CASCO/v2")
        self.assertEqual(pote["INTELLIGENCE_RUN_ID"], saida()["INTELLIGENCE_RUN_ID"])
        c = pote["COMPARTIMENTOS"]
        self.assertEqual(len(c["windows"]["OBJETOS"]), 1)
        self.assertEqual(len(c["science"]["OBJETOS"]), 2)
        self.assertEqual(len(c["future"]["OBJETOS"]), 1)
        self.assertEqual(len(c["sources"]["OBJETOS"]), 3)
        # o unico recusado e o estudo sem DOCUMENT_ID no RAW — a vista, com o motivo
        self.assertEqual([(r["COMPARTIMENTO"], r["MOTIVO"], r["DETALHE"]) for r in pote["RECUSADOS"]],
                         [("science", "PROVA_INCOMPLETA", "falta DOCUMENT_ID")])
        w = c["windows"]["OBJETOS"][0]
        self.assertEqual(w["ESPECIE_DITA_POR"], "INTELLIGENCE")
        self.assertIn("ENTITY_SOURCE", w["FORA_DO_CONTRATO"])
        self.assertTrue(all(p["URL"].startswith("https://") for p in w["PROVA"]))


class Q_OPortaoDaSaida(unittest.TestCase):
    """`conferir_saida` apanha o que o motor nunca pode deixar sair."""

    def _viola(self, mexer, trecho):
        s = saida()
        mexer(s)
        v = M.conferir_saida(s)
        self.assertTrue(any(trecho in x for x in v), v)

    def test_Q0_a_saida_verdadeira_passa(self):
        self.assertEqual(M.conferir_saida(saida()), [])

    def test_Q1_estudo_numa_janela(self):
        def m(s):
            est = next(o for o in objs(s, "science"))["PROVA"][0]
            objs(s, "windows")[0]["PROVA"].append(est)
        self._viola(m, "estudo nunca vira incidencia de campo")

    def test_Q2_chave_sem_entity_source(self):
        self._viola(lambda s: objs(s, "windows")[0]["CHAVES"]["ENTITY_SOURCE"].pop("REGION_ID"),
                    "REGION_ID sem ENTITY_SOURCE")
        def valor_sem_fonte(s):
            objs(s, "science")[0]["CHAVES"]["ENTITY_SOURCE"]["DOI"]["ENTITY_SOURCE"] = NAO_SEI
        self._viola(valor_sem_fonte, "sem procedencia (D112b)")

    def test_Q3_published_at_nao_e_fact_time(self):
        def m(s):
            p = objs(s, "science")[0]["PROVA"][0]
            p["FACT_TIME"] = p["PUBLISHED_AT"]
        self._viola(m, "publicacao nao e facto")
        def m2(s):
            objs(s, "windows")[0]["PROVA"][0]["PUBLISHED_AT"] = "2020-01-01"
        self._viola(m2, "PUBLISHED_AT e PUBLICADO_EM divergem")

    def test_Q4_oportunidade_nunca(self):
        self._viola(lambda s: objs(s, "windows")[0].update(ESPECIE="OPORTUNIDADE"), "nao e emitida")

    def test_Q5_leitura_proibida(self):
        def m(s):
            objs(s, "science")[0]["PORQUE"] = "O_PRODUTO_NAO_FUNCIONA"
        self._viola(m, "leitura proibida")

    def test_Q6_run_id_fora_do_topo(self):
        def m(s):
            rid = s.pop("INTELLIGENCE_RUN_ID")
            s["INTELLIGENCE_RUN_ID"] = rid
        self._viola(m, "primeira chave")

    def test_Q7_prova_fora_da_lineage_ou_bloqueada(self):
        self._viola(lambda s: objs(s, "windows")[0]["PROVA"][0].update(ITEM_ID="SINT-NAO-EXISTE"),
                    "fora da LINEAGE")
        def bloq(s):
            p = objs(s, "windows")[0]["PROVA"][0]
            l = next(l for l in s["LINEAGE"] if l["ITEM_ID"] == p["ITEM_ID"])
            l["G0"] = "BLOQUEADO_EM_G0"
        self._viola(bloq, "nao admitida em G0")

    def test_Q8_ignorancia_escondida(self):
        self._viola(lambda s: objs(s, "windows")[0]["PROVA"][0].update(URL=""), "prova esconde URL")


class R_ORunbook(unittest.TestCase):
    """O que o RUNBOOK-R7 promete no caso ARIF/APOL e nos estudos e o que sai."""

    def test_R1_janela_arif_apol(self):
        j = janela(saida())
        self.assertEqual((j["CROP_ID"], j["ISSUE_ID"], j["REGION_ID"]), ("olivo", "Bactrocera oleae", "Puglia"))
        self.assertEqual(j["WINDOW_TYPES"], ["THRESHOLD_WINDOW"])
        self.assertEqual(j["WINDOW_OPEN_NOW"], "NO")
        self.assertEqual(j["METHOD"], ["FONTE_DECLARA_SOGLIA_NAO_ATINGIDA"])
        self.assertEqual(j["TEMPORAL_STATE"], "CURRENT")
        self.assertEqual(j["RESULT"], "NO_DEFENSIBLE_ACTION_YET")
        self.assertEqual(j["SUPPORTS"]["OBSERVACAO"]["INDEPENDENTES_PROVADOS"], 2)
        self.assertEqual(j["SUPPORTS"]["REGRA"]["CONTA"], 1)
        self.assertTrue(j["READING"].startswith("monitorizar"))
        self.assertEqual(j["CONTRADICTIONS"], [])
        self.assertEqual(saida()["CAP_WIN"]["OPPORTUNITIES"], [])

    def test_R2_estudos(self):
        e = {x["ITEM_ID"]: x for x in saida()["CAP_SCI"]["ESTUDOS"]}
        tabela = {i: (x["ESPECIE"], x["FORCA"]["NIVEL"], x["APLICABILIDADE"]["ESTADO"], x["LEITURA"])
                  for i, x in e.items()}
        self.assertEqual(tabela, {
            EST1: ("SCIENTIFIC_RESULT", "FORTE", "COMPLETA", "SUSTENTA_EFEITO_NESTAS_CONDICOES"),
            EST2: ("SCIENTIFIC_RESULT", "INDICATIVA", "PARCIAL", "INDICIO_A_CONFIRMAR"),
            EST3: ("RESISTANCE", "FRACA", "PARCIAL", "RESISTENCIA_OBSERVADA_LOCAL_OU_PERIODO_NAO_PROVADO"),
        })
        g = saida()["CAP_SCI"]["INDEPENDENCIA"]["OLIVO x BACTROCERA OLEAE"]
        self.assertEqual(g["GRUPOS_TETO"], 2)   # EST-01 e EST-02 sao o mesmo ensaio

    def test_R3_o_runbook_le_a_copia_em_transacao_read_only(self):
        rb = (RAIZ / "RUNBOOK-R7.md").read_text(encoding="utf-8")
        self.assertIn("begin transaction read only", rb)
        self.assertIn("default_transaction_read_only=on", rb)
        self.assertIn("motor_das_capacidades.py", rb)
        self.assertIn("aceite_pelo_gerador.py", rb)
        self.assertIn("r7_export_da_copia.sql", rb)
        self.assertNotIn("SUPABASE_DB_URL", rb.split("## 2")[1].split("## 3")[0])


class S_NaCopiaDescartavel(unittest.TestCase):
    """O export read-only sobre o esquema REAL (migrations 001..033), ponta a ponta.

    Sem Postgres (PG_BIN do ensaio da 033 ou SINTONIA_PG_BIN), ou como root:
    SALTA com NAO SEI — nunca passa sem ter corrido. A ultima corrida medida
    esta em provas/int_r7/E2E-COPIA-DESCARTAVEL.json.
    """

    def test_S1_export_read_only_e_a_mesma_resposta(self):
        import os
        import tempfile
        import export_numa_copia_descartavel as X
        initdb = X.E.PG_BIN / ("initdb.exe" if os.name == "nt" else "initdb")
        if not initdb.exists() or (hasattr(os, "geteuid") and os.geteuid() == 0):
            self.skipTest("NAO SEI: sem Postgres portatil em %s, ou a correr como root" % X.E.PG_BIN)
        with tempfile.TemporaryDirectory() as d:
            r = X.correr(Path(d) / "e2e.json")
        self.assertEqual(r["ESTADO"], "PASS", r)
        self.assertEqual(r["PASSOS"]["3_EXPORT"]["READ_ONLY"], "on")
        self.assertIn("read-only", r["PASSOS"]["4_ESCRITA_RECUSADA"]["ERRO"])
        self.assertTrue(r["PASSOS"]["6_IGUAL_A_FIXTURE"])


if __name__ == "__main__":
    unittest.main()
