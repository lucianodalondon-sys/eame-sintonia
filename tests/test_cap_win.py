#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CAP-WIN, ATACADA — a janela de cultura minima (motor/cap_win.py).

    python3 -m unittest tests.test_cap_win -v

Todo item daqui e SINTETICO e vai marcado. O corte ARIF x APOL da mosca-da-
oliveira (desenho R5 §3) esta em `tests/dados/cap-win/arif-apol-mosca-sintetico.json`:
e reconstrucao das citacoes do desenho, NAO o RAW. Nenhum dado real no repo.

O resultado esperado do corte foi fixado no desenho ANTES de o motor existir
(§5): WINDOW_DEFINED = THRESHOLD_WINDOW, WINDOW_OPEN_NOW = NO,
regra = 1 apoio, observacao = 2 provaveis / NAO SEI provados,
RESULTADO = NO_DEFENSIBLE_ACTION_YET.
"""
import copy
import json
import sys
import unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in (RAIZ, RAIZ / "motor", RAIZ / "provas", RAIZ / "leis"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import afirmacao_da_fonte as AF                        # noqa: E402
import cap_win as W                                    # noqa: E402
import corrida_da_inteligencia as CI                   # noqa: E402

HOJE = date(2026, 9, 27)
CORTE = RAIZ / "tests" / "dados" / "cap-win" / "arif-apol-mosca-sintetico.json"
S = "SINTETICO"


def _campo(valor, base="SINTETICO · declarado em campo pela Collection"):
    return {"VALOR": valor, "BASE": base, "VEIO_DE": "SINTETICO"}


def _problema(valor, forma=None):
    """CHAVE-PROBLEMA (27/09) — AJUSTE DECLARADO: o PROBLEMA declarado pela Collection sai no
    contrato PROBLEMA/v1 (`leis/afirmacao_da_fonte.py`): UM nome, o trecho LITERAL que o contem e
    onde esta escrito. Antes daqui a fixture dizia VEIO_DE = SINTETICO e o nome nao estava no texto;
    o contrato recusa isso (seria praga inferida), por isso `_amarrar_problema` escreve o nome no item."""
    if valor == "NAO SEI":
        return {"CONTRATO": AF.CONTRATO_PROBLEMA, "VALOR": "NAO SEI", "VEIO_DE": "NAO SEI",
                "BASE": "NAO SEI", "PORQUE": "SINTETICO: a Collection nao declarou o problema"}
    forma = forma or valor
    return {"CONTRATO": AF.CONTRATO_PROBLEMA, "VALOR": valor, "VEIO_DE": "TEXT", "BASE": forma,
            "FORMA": forma, "CODIGO": {"SISTEMA": "NOME_CANONICO", "VALOR": valor,
                                       "TABELA": "SINTETICO"}}


def _amarrar_problema(it):
    """Se o nome declarado nao esta escrito no texto, ele vai como 1.a linha (o titulo): DOCUMENT_TITLE."""
    p = it["JANELA_DECLARADA"]["PROBLEMA"]
    if p["VALOR"] != "NAO SEI" and p["BASE"] not in str(it.get("TEXTO") or ""):
        it["TEXTO"] = p["BASE"] + "\n" + str(it.get("TEXTO") or "")
        p["VEIO_DE"] = "DOCUMENT_TITLE"
    return it


def jd(cultura="CROP_OLIVE", problema="ISSUE_OLIVE_FLY", regiao="IT-PUG",
       fase=None, subarea=None, rede=None, origem=None, forma_do_problema=None):
    d = {"CULTURA": _campo(cultura), "PROBLEMA": _problema(problema, forma_do_problema),
         "REGIAO_DO_FATO": _campo(regiao),
         "FASE": _campo(fase) if fase else _campo("NAO SEI", "NAO SEI"),
         "JANELA": _campo("NAO SEI", "NAO SEI")}
    if subarea:
        d["SUBAREA"] = _campo(subarea)
    if rede:
        d["REDE_DE_MONITORIZACAO"] = _campo(rede)
    if origem:
        d["ORIGEM_DA_REGRA"] = _campo(origem)
    return d


def item(iid, texto, url, fact="2026-09-20/2026-09-24", captura="2026-09-25T10:00:00Z",
         sid=None, **kw_jd):
    return _amarrar_problema({"MARCA": S, "ITEM_ID": iid, "RAW_OBSERVATION_ID": "RAW-" + iid,
                              "SOURCE_ID": sid or ("SRC-" + url.split("/")[2]), "URL": url,
                              "CAPTURED_AT": captura, "PUBLISHED_AT": "2026-09-25",
                              "FACT_TIME": fact,
                              "FACT_TIME_BASIS": "SINTETICO" if fact != "NAO SEI" else "NAO SEI",
                              "TEXTO": texto, "JANELA_DECLARADA": jd(**kw_jd)})


def rodar(itens, hoje=HOJE):
    livro = CI.correr("CAP-WIN teste", itens, universo={"ITENS_NO_CORTE": len(itens)})
    return livro, W.julgar(livro, itens, hoje)


def corte(cenario):
    """COMO_MEDIDO · PAR_EM_CAMPO (tempo como medido) · DEPOIS_DOS_REQUISITOS."""
    bruto = json.loads(CORTE.read_text(encoding="utf-8"))
    itens = []
    for it in bruto["ITENS"]:
        assert it["MARCA"] == S
        x = copy.deepcopy(it)
        x["TEXTO"] = x["TEXTO"].replace("{DISCIPLINARE}", bruto["DISCIPLINARE_SINTETICO"])
        extra = x.pop("PREENCHIDO_SE_A_COLLECTION_ENTREGAR")
        if cenario == "COMO_MEDIDO":
            x["JANELA_DECLARADA"] = jd(cultura="NAO SEI", problema="NAO SEI",
                                       regiao="NAO SEI")
        else:
            # o nome ja esta escrito em todo item do corte («Mosca delle olive, ...»)
            x["JANELA_DECLARADA"] = jd(subarea=extra.get("SUBAREA"),
                                       forma_do_problema="Mosca delle olive")
            _amarrar_problema(x)
            if cenario == "DEPOIS_DOS_REQUISITOS" and "FACT_TIME" in extra:
                x["FACT_TIME"] = extra["FACT_TIME"]
                x["FACT_TIME_BASIS"] = extra["FACT_TIME_BASIS"]
        itens.append(x)
    return itens


APOL = "XX-T3-2026-09-18-134205-772b57c43c0130fe#0"
ARIF37 = "XX-T3-2026-09-18-171937-6f76511ca75100a5#0"
ARIF38 = "IT-T3-2026-09-20-110656-6e4ffc27a86c5269#0"
GARGANO = "IT-T3-2026-09-20-110656-6e4ffc27a86c5269#1"


# ══════════════════════════════════════════════════════════════════════════
class A_ARegraPortadaDoV21(unittest.TestCase):
    """Os casos que o V21 ja tinha, contra a regra portada (nao o ficheiro)."""

    def test_T39_ato_administrativo_nunca_e_janela_agronomica(self):
        tipos = [t for t, _p in W.tipos_da_oracao(
            "Vite/flavescenza dorata: inspecionar os vinhedos e arrancar as plantas "
            "sintomaticas, conforme a Determinazione n. 9818 de 20/05/2026.")]
        self.assertIn(W.ADMINISTRATIVE_WINDOW, tipos)
        self.assertNotIn(W.ADMINISTRATIVE_WINDOW, W.AGRONOMICOS)
        self.assertEqual((W.NO, "ATO_ADMINISTRATIVO_NAO_E_JANELA_AGRONOMICA"),
                         W.aberta_agora(W.ADMINISTRATIVE_WINDOW, "x", "Vite: «maturazione»."))

    def test_T40_o_estadio_sozinho_nao_e_janela(self):
        solto = W.tipos_da_oracao("as espigas em maturacao avancada nao correm risco de dano")
        self.assertNotIn(W.PHENOLOGY_WINDOW, [t for t, _p in solto])
        amarrado = W.tipos_da_oracao("botrite a partir da invaiatura, intervir com antibotriticos")
        self.assertIn(W.PHENOLOGY_WINDOW, [t for t, _p in amarrado])

    def test_T40b_aberta_agora_exige_o_estadio_no_mesmo_documento(self):
        for estagio, esperado in ((None, W.UNKNOWN), ("Vite: «maturazione».", W.YES),
                                  ("Vite: «germogliamento».", W.NO)):
            got, _m = W.aberta_agora(W.PREHARVEST_WINDOW, "intervir em pre-colheita", estagio)
            self.assertEqual(esperado, got, str(estagio))

    def test_T40c_condicao_medida_sem_medicao_fica_UNKNOWN_com_a_razao_certa(self):
        for tipo in (W.THRESHOLD_WINDOW, W.WEATHER_TRIGGERED_WINDOW):
            got, por = W.aberta_agora(tipo, "x", "Vite: «maturazione».")
            self.assertEqual(W.UNKNOWN, got)
            self.assertEqual("FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE", por)

    def test_red_team_voo_terminado_e_fase_da_praga_encerrada(self):
        voo = ("reporta terceiro voo de Cydia pomonella terminado; tratar a geracao "
               "seguinte com danos em aumento")
        self.assertIn(W.PEST_STAGE_WINDOW, [t for t, _p in W.tipos_da_oracao(voo)])
        self.assertEqual((W.NO, "FONTE_DECLARA_A_FASE_DA_PRAGA_COMO_ENCERRADA"),
                         W.aberta_agora(W.PEST_STAGE_WINDOW, voo, None))

    def test_red_team_fase_conclusa_e_presente_e_fim(self):
        self.assertEqual((W.NO, "FONTE_DECLARA_A_FASE_COMO_ENCERRADA"),
                         W.aberta_agora(W.PHENOLOGY_WINDOW,
                                        "siamo nella fase conclusa della difesa", None))

    def test_red_team_frase_qualitativa_nao_responde_limiar(self):
        q = "o quadro a nivel territorial permanece tendencialmente bom"
        self.assertEqual((W.UNKNOWN, "FRASE_QUALITATIVA_NAO_RESPONDE_CONDICAO_QUANTITATIVA"),
                         W.aberta_agora(W.THRESHOLD_WINDOW, q, None))

    def test_regra_delegada_ao_pomar_e_definida_e_nunca_aberta(self):
        o = ("per cui le decisioni devono essere necessariamente basate sulle "
             "osservazioni aziendali")
        self.assertIn(W.RULE_DELEGATED_TO_FARM, [t for t, _p in W.tipos_da_oracao(o)])
        self.assertEqual(W.UNKNOWN, W.aberta_agora(W.RULE_DELEGATED_TO_FARM, o, None)[0])

    def test_os_oito_tipos_estao_todos(self):
        self.assertEqual(8, len(W.TIPOS))
        self.assertEqual(set(W.TIPOS), {t for t, _ in W._P})


class B_SogliaNaoAtingida(unittest.TestCase):
    """O defeito que o desenho achou no legado ANTES de portar (§3)."""

    APOL = ("Nei comprensori di Brindisi e Lecce non si sono rilevate raggiungimenti "
            "o superamenti della soglia di intervento")

    def test_a_APOL_por_extenso_e_NO_com_a_razao_certa(self):
        self.assertIn(W.THRESHOLD_WINDOW, [t for t, _p in W.tipos_da_oracao(self.APOL)])
        self.assertEqual((W.NO, "FONTE_DECLARA_SOGLIA_NAO_ATINGIDA"),
                         W.aberta_agora(W.THRESHOLD_WINDOW, self.APOL, None))

    def test_o_ARIF_al_disotto_delle_soglie_e_NO(self):
        self.assertEqual(W.NO, W.aberta_agora(
            W.THRESHOLD_WINDOW, "poche catture, al disotto delle soglie di intervento", None)[0])

    def test_poche_catture_sozinho_nao_e_soglia_nao_atingida(self):
        self.assertEqual(W.UNKNOWN, W.aberta_agora(
            W.THRESHOLD_WINDOW, "poche catture; controllare la soglia", None)[0])

    def test_pochissime_aree_sopra_soglia_diz_as_duas_coisas(self):
        self.assertEqual((W.UNKNOWN, "FONTE_DECLARA_SOGLIA_ATINGIDA_SO_EM_PARTE_DA_AREA"),
                         W.aberta_agora(W.THRESHOLD_WINDOW,
                                        "pochissime aree sopra soglia", None))

    def test_soglia_superata_e_YES(self):
        self.assertEqual((W.YES, "FONTE_DECLARA_SOGLIA_ATINGIDA"),
                         W.aberta_agora(W.THRESHOLD_WINDOW,
                                        "e stata superata la soglia di intervento", None))

    def test_verificare_il_superamento_nao_e_declaracao(self):
        self.assertEqual(W.UNKNOWN, W.aberta_agora(
            W.THRESHOLD_WINDOW, "verificare in campo il superamento della soglia", None)[0])

    def test_non_si_ritiene_giustificata_manda_parar(self):
        self.assertTrue(W.restritiva("Pertanto non si ritiene giustificata "
                                     "l'esecuzione di un trattamento."))
        self.assertIsNone(W.restritiva("si consiglia di intervenire subito"))


class C_OCorteComoMedidoNaR5(unittest.TestCase):
    """W0 · sem par em campo nao ha janela: NOT_POSSIBLE + o requisito."""

    def setUp(self):
        self.itens = corte("COMO_MEDIDO")
        self.livro, self.cw = rodar(self.itens)

    def test_todo_ready_atravessou_o_intake(self):
        self.assertEqual(4, len(self.livro["LINEAGE"]))
        estados = {l["ITEM_ID"]: l["TEMPORAL_STATE"] for l in self.livro["LINEAGE"]}
        self.assertEqual("UNKNOWN_WINDOW", estados[APOL])
        self.assertEqual("UNKNOWN_WINDOW", estados[ARIF37])
        self.assertEqual("ANCORADO", estados[ARIF38])

    def test_nenhuma_janela_e_tudo_NOT_POSSIBLE(self):
        self.assertEqual([], self.cw["CROP_WINDOWS"])
        self.assertEqual(W.NOT_POSSIBLE, self.cw["ANALYTIC_OUTPUT"])
        self.assertEqual(4, len(self.cw["NOT_POSSIBLE"]))
        self.assertTrue(all("INT-LAW-091" in n["PORQUE"] for n in self.cw["NOT_POSSIBLE"]))

    def test_o_requisito_nomeia_o_par_e_a_regiao_e_a_sonda_nao_vira_par(self):
        self.assertEqual(4, len(self.cw["REQUIREMENTS"]))
        for r in self.cw["REQUIREMENTS"]:
            self.assertEqual(["CROP_ISSUE_EM_CAMPO", "REGION_EM_CAMPO"], r["REQUIREMENT"])
            self.assertIn(W.THRESHOLD_WINDOW, r["SONDA_DO_TEXTO"])
        # o texto diz «olive» e «mosca», e nenhum CROP_ID saiu dele
        self.assertNotIn("CROP_OLIVE", json.dumps(self.cw))

    def test_nenhuma_oportunidade(self):
        self.assertEqual([], self.cw["OPPORTUNITIES"])


class D_ParEmCampoComOTempoComoMedido(unittest.TestCase):
    """O tempo so bloqueia os usos que exigem tempo: a regra entra, o «agora» nao."""

    def setUp(self):
        self.livro, self.cw = rodar(corte("PAR_EM_CAMPO"))
        self.j = self.cw["CROP_WINDOWS"][0]
        self.ev = {e["ITEM_ID"]: e for e in self.j["EVIDENCE"]}

    def test_um_par_e_a_regra_definida_pelas_tres_fontes(self):
        self.assertEqual(1, len(self.cw["CROP_WINDOWS"]))
        self.assertEqual(("CROP_OLIVE", "ISSUE_OLIVE_FLY", "IT-PUG"),
                         (self.j["CROP_ID"], self.j["ISSUE_ID"], self.j["REGION_ID"]))
        self.assertEqual("YES", self.j["WINDOW_DEFINED"])
        self.assertEqual([W.THRESHOLD_WINDOW], self.j["WINDOW_TYPES"])
        self.assertTrue(self.ev[APOL]["REGRA_UTILIZAVEL"])

    def test_a_APOL_sem_tempo_declara_NO_mas_nao_responde_agora(self):
        e = self.ev[APOL]
        self.assertEqual(W.NO, e["DECLARADO_PELA_FONTE"])
        self.assertEqual("FONTE_DECLARA_SOGLIA_NAO_ATINGIDA", e["METODO_DECLARADO"])
        self.assertEqual(W.UNKNOWN, e["WINDOW_OPEN_NOW"])
        self.assertTrue(e["OPEN_NOW_METHOD"].startswith("OBSERVACAO_SEM_TEMPO"))
        self.assertTrue(any(APOL in l for l in self.j["LIMITATIONS"]))

    def test_FACT_TIME_NAO_SEI_continua_NAO_SEI_no_livro(self):
        l = next(x for x in self.livro["LINEAGE"] if x["ITEM_ID"] == APOL)
        self.assertEqual(CI.NAO_SEI, l["FACT_TIME"])

    def test_so_o_ARIF_38_responde_e_e_uma_fonte_so(self):
        self.assertEqual(W.NO, self.j["WINDOW_OPEN_NOW"])
        self.assertEqual(W.CURRENT, self.j["TEMPORAL_STATE"])
        self.assertEqual(1, self.j["SUPPORTS"]["OBSERVACAO"]["ORIGINADORES_DISTINTOS"])
        self.assertEqual(W.NO_DEFENSIBLE_ACTION_YET, self.j["RESULT"])


class E_OCorteDepoisDosRequisitos(unittest.TestCase):
    """§5 do desenho, fixado antes: e isto que o corte deve responder."""

    def setUp(self):
        self.livro, self.cw = rodar(corte("DEPOIS_DOS_REQUISITOS"))
        self.j = self.cw["CROP_WINDOWS"][0]

    def test_definida_THRESHOLD_e_aberta_NO(self):
        self.assertEqual([W.THRESHOLD_WINDOW], self.j["WINDOW_TYPES"])
        self.assertEqual(W.NO, self.j["WINDOW_OPEN_NOW"])
        self.assertIn("FONTE_DECLARA_SOGLIA_NAO_ATINGIDA", self.j["METHOD"])
        self.assertEqual(W.CURRENT, self.j["TEMPORAL_STATE"])

    def test_duas_semanas_do_ARIF_sao_um_apoio(self):
        obs = self.j["SUPPORTS"]["OBSERVACAO"]
        self.assertEqual(3, obs["SINAIS"])
        self.assertEqual(2, obs["ORIGINADORES_DISTINTOS"])
        self.assertEqual(["agrometeopuglia.it", "apol.it"], sorted(obs["ORIGINADORES"]))

    def test_redes_nao_declaradas_independencia_NAO_SEI_provavel_2(self):
        obs = self.j["SUPPORTS"]["OBSERVACAO"]
        self.assertEqual(CI.NAO_SEI, obs["INDEPENDENTES_PROVADOS"])
        self.assertEqual(2, obs["INDEPENDENTES_PROVAVEIS"])

    def test_a_regra_do_disciplinare_conta_uma_vez(self):
        regra = self.j["SUPPORTS"]["REGRA"]
        self.assertEqual(1, regra["CONTA"])
        self.assertGreater(regra["SEQUENCIAS_PARTILHADAS"], 0)
        self.assertEqual(2, regra["ORIGINADORES_QUE_A_CITAM"])

    def test_origens_da_regra_declaradas_distintas_contam_duas(self):
        its = corte("DEPOIS_DOS_REQUISITOS")
        for it, o in zip(its, ("DISCIPLINARE-A", "DISCIPLINARE-B", "DISCIPLINARE-B",
                               "DISCIPLINARE-B")):
            it["JANELA_DECLARADA"]["ORIGEM_DA_REGRA"] = _campo(o)
        _l, cw = rodar(its)
        regra = cw["CROP_WINDOWS"][0]["SUPPORTS"]["REGRA"]
        self.assertEqual(2, regra["CONTA"])
        self.assertIn("declarada", regra["BASE"])

    def test_gargano_e_subarea_UNKNOWN_e_nao_contradicao(self):
        self.assertEqual([], self.j["CONTRADICTIONS"])
        self.assertTrue(any("GARGANO_COSTIERO" in l and "UNKNOWN" in l
                            for l in self.j["LIMITATIONS"]))

    def test_as_arestas_sao_de_apoio(self):
        tipos = {(a["DE"], a["PARA"]): a["TIPO"] for a in self.j["EDGES"]}
        self.assertTrue(tipos)
        self.assertEqual({W.SUPPORT}, set(tipos.values()))
        # APOL (14-20) e ARIF 38 (07-13) nao se tocam no tempo: nao ha aresta
        self.assertNotIn((APOL, ARIF38), tipos)
        self.assertNotIn((ARIF38, APOL), tipos)

    def test_resultado_NO_DEFENSIBLE_ACTION_YET_com_o_porque(self):
        self.assertEqual(W.NO_DEFENSIBLE_ACTION_YET, self.j["RESULT"])
        self.assertEqual(W.NO_DEFENSIBLE_ACTION_YET, self.cw["ANALYTIC_OUTPUT"])
        self.assertTrue(any("WINDOW_OPEN_NOW = NO" in w for w in self.j["WHY"]))
        self.assertTrue(self.j["SOURCE_SAYS_DO_NOT_TREAT"])
        self.assertIn("monitorizar", self.j["READING"])
        self.assertIn("nao se justifica", self.j["READING"])

    def test_o_objeto_tem_os_campos_do_W7_e_linhagem_ate_ao_RAW(self):
        for k in ("CROP_ID", "ISSUE_ID", "REGION_ID", "TIME_WINDOW", "WINDOW_DEFINED",
                  "WINDOW_OPEN_NOW", "METHOD", "TEMPORAL_STATE", "SUPPORTS",
                  "CONTRADICTIONS", "LIMITATIONS", "LINEAGE", "PHENOLOGY_STAGE"):
            self.assertIn(k, self.j)
        self.assertEqual("ANALYTIC_JUDGMENT", self.j["OBJECT"])
        self.assertEqual("CROP_WINDOW", self.j["SPECIES"])
        raws = {r for _i, _s, r in self.j["LINEAGE"]}
        self.assertIn("RAW-SINTETICO-APOL-38", raws)
        self.assertEqual({"CAP-WIN": {"VERSION": W.VERSAO,
                                      "RUN": self.livro["INTELLIGENCE_RUN_ID"]}},
                         self.cw["CAPACIDADES_EXECUTADAS"])


class F_ActNowSoComAsQuatro(unittest.TestCase):
    """W8 · ACT_NOW exige YES ∧ CURRENT ∧ >= 2 independentes provados ∧ 0 contradicoes."""

    SIM = "Mosca delle olive: e stata superata la soglia di intervento."

    def dois(self, rede_b="RETE-B", url_b="https://b.example.org/SINTETICO/1", **kw):
        return [item("S-A", self.SIM, "https://a.example.org/SINTETICO/1", rede="RETE-A", **kw),
                item("S-B", self.SIM, url_b, rede=rede_b, **kw)]

    def test_as_quatro_dao_ACT_NOW(self):
        _l, cw = rodar(self.dois())
        j = cw["CROP_WINDOWS"][0]
        self.assertEqual(W.YES, j["WINDOW_OPEN_NOW"])
        self.assertEqual(2, j["SUPPORTS"]["OBSERVACAO"]["INDEPENDENTES_PROVADOS"])
        self.assertEqual(W.ACT_NOW, j["RESULT"])
        self.assertEqual(W.ACT_NOW, cw["ANALYTIC_OUTPUT"])
        self.assertEqual([], cw["OPPORTUNITIES"], "janela nao e oportunidade")

    def test_a_mesma_rede_declarada_e_um_apoio(self):
        _l, cw = rodar(self.dois(rede_b="RETE-A"))
        self.assertEqual(1, cw["CROP_WINDOWS"][0]["SUPPORTS"]["OBSERVACAO"]["INDEPENDENTES_PROVADOS"])
        self.assertEqual(W.NO_DEFENSIBLE_ACTION_YET, cw["CROP_WINDOWS"][0]["RESULT"])

    def test_sem_rede_declarada_nao_ha_ACT_NOW(self):
        its = self.dois()
        del its[1]["JANELA_DECLARADA"]["REDE_DE_MONITORIZACAO"]
        _l, cw = rodar(its)
        j = cw["CROP_WINDOWS"][0]
        self.assertEqual(CI.NAO_SEI, j["SUPPORTS"]["OBSERVACAO"]["INDEPENDENTES_PROVADOS"])
        self.assertEqual(W.NO_DEFENSIBLE_ACTION_YET, j["RESULT"])

    def test_duas_semanas_da_mesma_fonte_sao_um_originador(self):
        its = [item("S-A1", self.SIM, "https://a.example.org/SINTETICO/37",
                    fact="2026-09-14/2026-09-20", rede="RETE-A"),
               item("S-A2", self.SIM, "https://a.example.org/SINTETICO/38", rede="RETE-A")]
        _l, cw = rodar(its)
        obs = cw["CROP_WINDOWS"][0]["SUPPORTS"]["OBSERVACAO"]
        self.assertEqual(2, obs["SINAIS"])
        self.assertEqual(1, obs["ORIGINADORES_DISTINTOS"])
        self.assertEqual(W.NO_DEFENSIBLE_ACTION_YET, cw["CROP_WINDOWS"][0]["RESULT"])

    def test_janela_de_outro_ano_e_STALE_e_nao_e_agora(self):
        _l, cw = rodar(self.dois(fact="2025-09-20/2025-09-24"))
        j = cw["CROP_WINDOWS"][0]
        self.assertEqual(W.STALE, j["TEMPORAL_STATE"])
        self.assertEqual(W.UNKNOWN, j["WINDOW_OPEN_NOW"])
        self.assertEqual(W.NO_DEFENSIBLE_ACTION_YET, j["RESULT"])

    def test_PUBLISHED_AT_nao_vira_tempo_do_facto(self):
        _l, cw = rodar(self.dois(fact="NAO SEI"))
        j = cw["CROP_WINDOWS"][0]
        self.assertEqual(W.UNKNOWN, j["WINDOW_OPEN_NOW"])
        self.assertEqual(W.UNKNOWN, j["TEMPORAL_STATE"])
        self.assertEqual("YES", j["WINDOW_DEFINED"], "a regra continua lida")


class G_Contradicao(unittest.TestCase):
    """W6 · dois «agora» opostos no mesmo par, regiao e semana: as duas visiveis."""

    SIM = "Mosca delle olive: e stata superata la soglia di intervento."
    NAO = "Mosca delle olive: non e stata superata la soglia di intervento."

    def test_YES_contra_NO_na_mesma_semana_e_CONFLICTING(self):
        _l, cw = rodar([item("C-A", self.SIM, "https://a.example.org/SINTETICO/1", rede="R1"),
                        item("C-B", self.NAO, "https://b.example.org/SINTETICO/1", rede="R2")])
        j = cw["CROP_WINDOWS"][0]
        self.assertEqual(1, len(j["CONTRADICTIONS"]))
        self.assertEqual(W.CONTRADICTS, j["CONTRADICTIONS"][0]["TIPO"])
        self.assertEqual(W.CONFLICTING_EVIDENCE, j["METHOD"])
        self.assertEqual(W.UNKNOWN, j["WINDOW_OPEN_NOW"])
        self.assertEqual(W.NO_DEFENSIBLE_ACTION_YET, j["RESULT"])
        self.assertEqual({"C-A", "C-B"}, {e["ITEM_ID"] for e in j["EVIDENCE"]})

    def test_o_porque_nomeia_a_contradicao(self):
        """Nasceu do mutante M8: sem isto, ACT_NOW podia esquecer as contradicoes."""
        _l, cw = rodar([item("C-A", self.SIM, "https://a.example.org/SINTETICO/1", rede="R1"),
                        item("C-B", self.NAO, "https://b.example.org/SINTETICO/1", rede="R2")])
        self.assertTrue(any("contradicao" in w for w in cw["CROP_WINDOWS"][0]["WHY"]))

    def test_subareas_diferentes_nao_se_contradizem(self):
        _l, cw = rodar([item("C-A", self.SIM, "https://a.example.org/SINTETICO/1", subarea="X"),
                        item("C-B", self.NAO, "https://b.example.org/SINTETICO/1", subarea="Y")])
        j = cw["CROP_WINDOWS"][0]
        self.assertEqual([], j["CONTRADICTIONS"])
        self.assertEqual("SUBAREAS_OU_PERIODOS_DIVERGEM", j["METHOD"])
        self.assertEqual(W.UNKNOWN, j["WINDOW_OPEN_NOW"])

    def test_semanas_que_nao_se_tocam_nao_se_contradizem(self):
        _l, cw = rodar([item("C-A", self.SIM, "https://a.example.org/SINTETICO/1",
                             fact="2026-09-01/2026-09-05"),
                        item("C-B", self.NAO, "https://b.example.org/SINTETICO/1")])
        self.assertEqual([], cw["CROP_WINDOWS"][0]["CONTRADICTIONS"])

    def test_UNKNOWN_nao_contradiz_nem_apoia(self):
        _l, cw = rodar([item("C-A", self.SIM, "https://a.example.org/SINTETICO/1"),
                        item("C-B", "verificare il superamento della soglia",
                             "https://b.example.org/SINTETICO/1")])
        self.assertEqual([], cw["CROP_WINDOWS"][0]["EDGES"])

    def test_pares_diferentes_nao_se_misturam(self):
        _l, cw = rodar([item("C-A", self.SIM, "https://a.example.org/SINTETICO/1"),
                        item("C-B", self.NAO, "https://b.example.org/SINTETICO/1",
                             problema="ISSUE_OLIVE_MOTH")])
        self.assertEqual(2, len(cw["CROP_WINDOWS"]))
        self.assertTrue(all(not j["CONTRADICTIONS"] for j in cw["CROP_WINDOWS"]))


class H_OsPortoes(unittest.TestCase):

    def test_a_capacidade_obedece_aos_usos_do_livro(self):
        """Nasceu do mutante M5. Quem decide que usos um item serve e a corrida;
        a CAP-WIN nao os recalcula. Livro que tira o uso CAP-WIN -> sem «agora»."""
        its = [item("H-0", "e stata superata la soglia di intervento",
                    "https://a.example.org/SINTETICO/1")]
        livro = CI.correr("CAP-WIN teste", its)
        livro["LINEAGE"][0]["USOS_DISPONIVEIS"].remove("CAP-WIN")
        j = W.julgar(livro, its, HOJE)["CROP_WINDOWS"][0]
        self.assertEqual(W.YES, j["EVIDENCE"][0]["DECLARADO_PELA_FONTE"])
        self.assertEqual(W.UNKNOWN, j["WINDOW_OPEN_NOW"])
        self.assertTrue(j["EVIDENCE"][0]["OPEN_NOW_METHOD"].startswith("OBSERVACAO_SEM_TEMPO"))

    def test_a_oracao_que_manda_parar_fecha_a_janela(self):
        """Nasceu do mutante M18 (regra do V21: quem manda parar manda parar)."""
        _l, cw = rodar([item("H-9", "superata la soglia di intervento, ma i trattamenti "
                             "sono sospesi", "https://a.example.org/SINTETICO/1")])
        e = cw["CROP_WINDOWS"][0]["EVIDENCE"][0]
        self.assertEqual((W.NO, "A_ORACAO_MANDA_PARAR"),
                         (e["DECLARADO_PELA_FONTE"], e["METODO_DECLARADO"]))

    def test_so_ato_administrativo_nao_define_janela(self):
        _l, cw = rodar([item("H-1", "Trattamenti obbligatori conforme a determina n. 12.",
                             "https://a.example.org/SINTETICO/1")])
        j = cw["CROP_WINDOWS"][0]
        self.assertEqual("NO", j["WINDOW_DEFINED"])
        self.assertTrue(j["ADMINISTRATIVE_CONSTRAINTS"])
        self.assertEqual(W.NO_DEFENSIBLE_ACTION_YET, j["RESULT"])

    def test_valor_sem_base_nao_e_par(self):
        it = item("H-2", "non superata la soglia", "https://a.example.org/SINTETICO/1")
        it["JANELA_DECLARADA"]["PROBLEMA"]["BASE"] = "NAO SEI"
        _l, cw = rodar([it])
        self.assertEqual(W.NOT_POSSIBLE, cw["ANALYTIC_OUTPUT"])
        self.assertIn("sem BASE", cw["NOT_POSSIBLE"][0]["PORQUE"])

    def test_sem_proveniencia_nao_ha_uso(self):
        it = item("H-3", "non superata la soglia", "https://a.example.org/SINTETICO/1")
        it["RAW_OBSERVATION_ID"] = "NAO SEI"
        _l, cw = rodar([it])
        self.assertIn("SEM_PROVENIENCIA", cw["NOT_POSSIBLE"][0]["PORQUE"])
        self.assertEqual([], cw["REQUIREMENTS"])

    def test_sem_hoje_nao_ha_agora(self):
        its = [item("H-4", "x", "https://a.example.org/SINTETICO/1")]
        livro = CI.correr("CAP-WIN teste", its)
        with self.assertRaises(W.LeiViolada):
            W.julgar(livro, its, None)

    def test_pre_filtro_recusado(self):
        its = [item("H-5", "x", "https://a.example.org/SINTETICO/1"),
               item("H-6", "x", "https://b.example.org/SINTETICO/1")]
        livro = CI.correr("CAP-WIN teste", its)
        with self.assertRaises(W.LeiViolada):
            W.julgar(livro, its[:1], HOJE)

    def test_so_le_livro_G0_v4_fechado(self):
        its = [item("H-7", "x", "https://a.example.org/SINTETICO/1")]
        livro = CI.correr("CAP-WIN teste", its)
        livro["RULESET_VERSION"] = "G0/v3"
        with self.assertRaises(W.LeiViolada):
            W.julgar(livro, its, HOJE)

    def test_o_requisito_nao_nomeia_palavra_da_collection(self):
        _l, cw = rodar(corte("COMO_MEDIDO"))
        txt = json.dumps(cw["REQUIREMENTS"], ensure_ascii=False).upper()
        for p in W.PALAVRAS_QUE_O_REQUISITO_RECUSA:
            self.assertNotIn(p, txt)

    def test_N_de_CURRENT_esta_declarado(self):
        self.assertEqual(30, W.N_DIAS_CURRENT)
        _l, cw = rodar(corte("DEPOIS_DOS_REQUISITOS"))
        self.assertEqual(30, cw["N_DIAS_CURRENT"])
        self.assertIn("HERDADO", cw["N_DIAS_CURRENT_ESTADO"])

    def test_fixture_e_toda_sintetica(self):
        bruto = json.loads(CORTE.read_text(encoding="utf-8"))
        self.assertEqual(S, bruto["MARCA"])
        for it in bruto["ITENS"]:
            self.assertEqual(S, it["MARCA"])
            self.assertIn("/SINTETICO/", it["URL"])
            self.assertTrue(it["RAW_OBSERVATION_ID"].startswith("RAW-SINTETICO-"))


if __name__ == "__main__":
    unittest.main()
