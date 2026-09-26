#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS CONSERTOS DA INTELLIGENCE — D1-D4, D6, D7, D8 (missao INT-CONSERTOS-EXP).

    python -m unittest tests.test_os_consertos_da_intelligence -v

Cada defeito tem:
    NEGATIVO    o ataque que a versao antiga deixava passar, e que agora morre
                com o motivo NOMEADO (nao so «bloqueou»);
    POSITIVO    a contraprova: o caso legitimo continua a passar. Um portao que
                recusa tudo passa em qualquer teste negativo e nao vale nada.

Os casos negativos vem de valores MEDIDOS na Sala real em 25/09 (so contagens
agregadas, antes da ordem de paragem): «UNKNOWN» na base, «2025» solto,
«21-23 ottobre» sem ano, «20-22 aprile 2027» futuro. Nenhum teste abre a Sala,
o banco ou a rede.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for g in ("", "motor", "provas"):
    if str(RAIZ / g) not in sys.path:
        sys.path.insert(0, str(RAIZ / g))

import corrida_da_inteligencia as CI          # noqa: E402
import espinha_da_intelligence as ESP          # noqa: E402

BASE_PROVADA = "EVENTO · ESCRITO_NO_TEXTO · DATE_EXACT · ancora «il 23 settembre»"
CAPTURA = "2026-09-25T22:58:29+00:00"


def item(**kw):
    """Um item com tudo ancorado; cada teste estraga UMA coisa."""
    base = {"ITEM_ID": "IT-X-1", "SOURCE_ID": "IT-T9-021", "RAW_OBSERVATION_ID": 1062,
            "CORRIDA": "RUN-TESTE", "FACT_TIME": "2026-09-23",
            "FACT_TIME_BASIS": BASE_PROVADA, "CAPTURED_AT": CAPTURA,
            "FACT_LOCATION": "Abruzzo",
            "FACT_LOCATION_BASIS": "EVENTO · EVENTO · CITADO · REGION · ancora «in Abruzzo»",
            "SOURCE_LOCATION": "Bari"}
    base.update(kw)
    return base


def g0(**kw):
    return CI.portao_g0(item(**kw))


class Positivo_OItemAncoradoPassa(unittest.TestCase):
    """A contraprova de todos: sem ela, os negativos nao provam nada."""

    def test_item_com_tempo_provado_passa_e_vira_sinal(self):
        self.assertEqual(g0(), (True, []))
        livro = CI.correr("pergunta de teste", [item()])
        self.assertEqual(len(livro["SIGNALS"]), 1)
        self.assertEqual(livro["ANALYTIC_OUTPUT"], CI.INTAKE_OK)

    def test_dia_da_propria_captura_ainda_e_passado(self):
        self.assertEqual(g0(FACT_TIME="2026-09-25"), (True, []))

    def test_mes_e_ano_e_ano_solto_com_base_provada_passam(self):
        for v in ("settembre 2026", "2025", "stagione 2025/26", "21-23 settembre 2026"):
            with self.subTest(valor=v):
                self.assertEqual(g0(FACT_TIME=v), (True, []))


class D1_UnknownNaoEValor(unittest.TestCase):
    def test_negativo_unknown_em_qualquer_lingua_bloqueia(self):
        for v in ("UNKNOWN", "unknown — sem data", "NOT_KNOWN", "NAO_SEI", "?", "null"):
            with self.subTest(valor=v):
                passou, falta = g0(FACT_TIME=v)
                self.assertFalse(passou)
                self.assertIn("FACT_TIME", falta)

    def test_negativo_unknown_na_identidade_tambem_bloqueia(self):
        passou, falta = g0(SOURCE_ID="UNKNOWN")
        self.assertIn("SOURCE_ID", falta)

    def test_positivo_valor_real_com_a_palavra_no_meio_nao_e_ignorancia(self):
        # a regra e «COMECA por uma palavra de ignorancia», nao «contem as letras»
        self.assertFalse(CI.e_ignorancia("2026-09-23 (agenzia: UNKNOWN press)"))
        self.assertFalse(CI.e_ignorancia("Abruzzo"))


class D2_ValorSemBaseNaoAncora(unittest.TestCase):
    def test_negativo_base_nao_sei(self):
        passou, falta = g0(FACT_TIME="2025", FACT_TIME_BASIS="NAO SEI")
        self.assertFalse(passou)
        self.assertIn("FACT_TIME:SEM_BASE", falta)

    def test_negativo_base_ausente(self):
        it = item(FACT_TIME="2025")
        del it["FACT_TIME_BASIS"]
        self.assertIn("FACT_TIME:SEM_BASE", CI.portao_g0(it)[1])

    def test_negativo_base_que_confessa_unknown_no_meio(self):
        # medido na Sala: 12 linhas com esta forma
        passou, falta = g0(FACT_TIME="2025", FACT_TIME_BASIS=(
            "o coletor declarou: «UNKNOWN — identidade pelo endereco, sem data»"))
        self.assertIn("FACT_TIME:SEM_BASE", falta)


class D3_DataSemAnoNaoAncora(unittest.TestCase):
    def test_negativo_sem_ano(self):
        for v in ("21-23 ottobre", "28 settembre", "ottobre", "5 ottobre"):
            with self.subTest(valor=v):
                passou, falta = g0(FACT_TIME=v)
                self.assertFalse(passou)
                self.assertIn("FACT_TIME:SEM_ANO", falta)

    def test_negativo_data_impossivel_nao_vira_data(self):
        self.assertIn("FACT_TIME:NAO_ANALISAVEL", g0(FACT_TIME="31 febbraio 2026")[1])
        self.assertIn("FACT_TIME:NAO_ANALISAVEL", g0(FACT_TIME="em breve")[1])

    def test_positivo_o_intervalo_e_o_que_o_texto_diz(self):
        t = CI.intervalo_do_tempo("12-13 novembre 2026")
        self.assertEqual((t["INICIO"], t["FIM"]), ("2026-11-12", "2026-11-13"))
        t = CI.intervalo_do_tempo("2025/26")
        self.assertEqual((t["INICIO"], t["FIM"]), ("2025-01-01", "2026-12-31"))
        t = CI.intervalo_do_tempo("febbraio 2024")
        self.assertEqual(t["FIM"], "2024-02-29")


class D4_EventoFuturoNaoEFacto(unittest.TestCase):
    def test_negativo_evento_depois_da_captura(self):
        for v in ("20-22 aprile 2027", "21-23 ottobre 2026", "29 settembre 2026",
                  "2026-09-26"):
            with self.subTest(valor=v):
                passou, falta = g0(FACT_TIME=v)
                self.assertFalse(passou)
                self.assertIn("FACT_TIME:FUTURO_EM_RELACAO_A_CAPTURA", falta)

    def test_negativo_sem_captura_o_futuro_nao_esta_excluido(self):
        for c in ("NAO SEI", None, "", "UNKNOWN"):
            with self.subTest(captura=c):
                passou, falta = g0(CAPTURED_AT=c)
                self.assertFalse(passou)
                self.assertIn("FACT_TIME:CAPTURA_DESCONHECIDA_FUTURO_NAO_EXCLUIDO", falta)

    def test_negativo_publicacao_nao_substitui_captura_nem_fact_time(self):
        it = item(CAPTURED_AT="NAO SEI", PUBLISHED_AT="2026-09-24")
        self.assertFalse(CI.portao_g0(it)[0])
        it = item(FACT_TIME="NAO SEI", PUBLISHED_AT="2026-09-24")
        self.assertIn("FACT_TIME", CI.portao_g0(it)[1])

    def test_o_evento_futuro_nao_vira_sinal(self):
        # (G0/v3: o destino do evento futuro e D14 — ver D14_OFuturoNaoELacuna)
        livro = CI.correr("pergunta de teste", [item(FACT_TIME="20-22 aprile 2027")])
        self.assertEqual(livro["SIGNALS"], [])
        self.assertEqual(len(livro["FUTURE_DATED_FACTS"]), 1)


class D6_OSinalLevaABase(unittest.TestCase):
    def sinal(self, **kw):
        return CI.correr("pergunta de teste", [item(**kw)])["SIGNALS"][0]

    def test_o_sinal_carrega_a_base_do_tempo_e_do_lugar(self):
        s = self.sinal()
        self.assertEqual(s["FACT_TIME_BASIS"], BASE_PROVADA)
        self.assertTrue(s["FACT_LOCATION_BASIS"].startswith("EVENTO"))
        self.assertEqual(s["FACT_LOCATION_ESTADO"], "COM_BASE")
        self.assertEqual(s["FACT_TIME_INTERVALO"]["INICIO"], "2026-09-23")

    def test_negativo_lugar_sem_base_fica_marcado_e_nao_e_apagado(self):
        s = self.sinal(FACT_LOCATION_BASIS="NAO SEI")
        self.assertEqual(s["FACT_LOCATION"], "Abruzzo")
        self.assertEqual(s["FACT_LOCATION_ESTADO"], "SEM_BASE_NAO_ANCORA")

    def test_negativo_source_location_nunca_entra_no_sinal(self):
        s = self.sinal(FACT_LOCATION="NAO SEI", FACT_LOCATION_BASIS="NAO SEI")
        self.assertEqual(s["FACT_LOCATION_ESTADO"], "NAO SEI")
        self.assertNotIn("Bari", json.dumps(s, ensure_ascii=False))


class D7_ABibliaEfetiva(unittest.TestCase):
    def test_o_livro_carimba_a_biblia_do_cabecalho_e_do_registo(self):
        livro = CI.correr("pergunta de teste", [item()])
        cab = (RAIZ / "BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md").read_text(
            encoding="utf-8")[:600]
        import re
        ver = re.search(r"^VERSION = (\S+)", cab, re.M).group(1)
        self.assertIn(ver, livro["BIBLE_VERSION"])
        self.assertNotIn("NAO SEI", livro["BIBLE_VERSION"])
        self.assertEqual(len(livro["BIBLE_FILE_SHA256"]), 64)

    def test_nenhuma_versao_da_biblia_escrita_a_mao_no_motor(self):
        fonte = (RAIZ / "motor" / "corrida_da_inteligencia.py").read_text(encoding="utf-8")
        import re
        self.assertIsNone(re.search(r"BIBLE\s+V\d+\.\d+", fonte),
                          "versao da Biblia digitada no motor")

    def _biblia(self, d, versao, status="CANONICAL"):
        b = Path(d) / "b.md"
        b.write_text(f"# X\n\nBIBLE_ID = SINTONIA-INTELLIGENCE-BIBLE\nVERSION = {versao}\n"
                     f"STATUS = {status}\n", encoding="utf-8")
        return b

    def _registo(self, d, versao, status="CANONICAL"):
        r = Path(d) / "r.json"
        r.write_text(json.dumps({"AUTHORITIES": [{"CARD_ID": CI.CARTAO_DA_BIBLIA,
                                                  "VERSION": versao,
                                                  "LIFECYCLE": status}]}), encoding="utf-8")
        return r

    def test_negativo_cabecalho_e_registo_em_desacordo_dao_nao_sei(self):
        with tempfile.TemporaryDirectory() as d:
            c = CI.carimbo_da_biblia(self._biblia(d, "V0.4"), self._registo(d, "V0.3"))
            self.assertTrue(c["BIBLE_VERSION"].startswith("NAO SEI"))

    def test_negativo_registo_ausente_da_nao_sei(self):
        with tempfile.TemporaryDirectory() as d:
            c = CI.carimbo_da_biblia(self._biblia(d, "V0.3"), Path(d) / "nao-existe.json")
            self.assertTrue(c["BIBLE_VERSION"].startswith("NAO SEI"))

    def test_positivo_os_dois_de_acordo(self):
        with tempfile.TemporaryDirectory() as d:
            c = CI.carimbo_da_biblia(self._biblia(d, "V9.9"), self._registo(d, "V9.9"))
            self.assertEqual(c["BIBLE_VERSION"],
                             "SINTONIA-INTELLIGENCE-BIBLE V9.9 CANONICAL")

    def test_mudar_a_biblia_muda_a_identidade_da_corrida(self):
        a = CI.identidade_da_corrida("IQ-1", [item()])
        orig = CI.carimbo_da_biblia
        try:
            CI.carimbo_da_biblia = lambda *x, **k: {"BIBLE_VERSION": "outra",
                                                    "BIBLE_FILE_SHA256": "0" * 64}
            b = CI.identidade_da_corrida("IQ-1", [item()])
        finally:
            CI.carimbo_da_biblia = orig
        self.assertNotEqual(a, b, "reuso depois de mudar a lei seria reuso falso")


class D8_UmaListaSo(unittest.TestCase):
    def test_a_espinha_le_a_lista_do_dono_sem_copia(self):
        import ast
        arvore = ast.parse((RAIZ / "provas" / "espinha_da_intelligence.py")
                           .read_text(encoding="utf-8"))
        for no in arvore.body:
            if (isinstance(no, ast.Assign) and isinstance(no.targets[0], ast.Name)
                    and no.targets[0].id == "CAMPOS_DO_READY"):
                self.assertNotIsInstance(no.value, ast.Tuple,
                                         "CAMPOS_DO_READY voltou a ser uma copia literal")

    def test_o_itempronto_cobre_todos_os_campos_do_dono(self):
        p = ESP.ItemPronto(ITEM_ID="a", UNIVERSO="T5", TEXTO="t", SOURCE_ID="s")
        self.assertEqual(set(p.dentro_do_contrato_de_hoje()), set(ESP.CAMPOS_DO_READY))


if __name__ == "__main__":
    unittest.main()


# ════════════════════════════════════════════════════════════════════════════
# D11 · D14 · D15 — achados na 1.a rodada REAL (EXPD78, IR-e73156836958445fe86a)
# Os valores vem da copia da Sala de 26/09 (IT-T5-090, IT-T5-010, 10 eventos
# futuros). Nenhum teste abre a Sala.
# ════════════════════════════════════════════════════════════════════════════
EVID_EVENTO = {"FACT_TIME_KIND": "EVENTO", "FACT_TIME_PRECISION": "APPROXIMATE",
               "FACT_LOCATION_KIND": "EVENTO"}
EVID_CAMPO = {"FACT_TIME_KIND": "CAMPO", "FACT_TIME_PRECISION": "WEEK+CALCULADA",
              "FACT_LOCATION_KIND": "CAMPO"}


class D11_OSinalDizAEspecieDaData(unittest.TestCase):
    def sinal(self, **kw):
        return CI.correr("pergunta de teste", [item(**kw)])["SIGNALS"][0]

    def test_negativo_congresso_e_campo_nao_saem_iguais(self):
        congresso = self.sinal(FACT_TIME="1-4 febbraio 2023", TEMPO_LUGAR_EVIDENCIA=EVID_EVENTO)
        campo = self.sinal(FACT_TIME="2026-09-07/2026-09-13", TEMPO_LUGAR_EVIDENCIA=EVID_CAMPO)
        self.assertEqual(congresso["FACT_TIME_KIND"], "EVENTO")
        self.assertEqual(campo["FACT_TIME_KIND"], "CAMPO")
        self.assertEqual(campo["FACT_TIME_PRECISION"], "WEEK+CALCULADA")

    def test_negativo_especie_ausente_e_nao_sei_nunca_inventada(self):
        s = self.sinal()                                   # sem TEMPO_LUGAR_EVIDENCIA
        self.assertEqual(s["FACT_TIME_KIND"], CI.NAO_SEI)
        s = self.sinal(TEMPO_LUGAR_EVIDENCIA={"FACT_TIME_KIND": "UNKNOWN"})
        self.assertEqual(s["FACT_TIME_KIND"], CI.NAO_SEI)
        s = self.sinal(TEMPO_LUGAR_EVIDENCIA="lixo")       # forma errada nao rebenta
        self.assertEqual(s["FACT_LOCATION_KIND"], CI.NAO_SEI)

    def test_negativo_a_especie_nao_vem_do_texto(self):
        s = self.sinal(TEXTO="convegno congresso seminario", FACT_TIME="2026-09-23")
        self.assertEqual(s["FACT_TIME_KIND"], CI.NAO_SEI)


class D14_OFuturoNaoELacunaDaColeta(unittest.TestCase):
    def test_negativo_evento_futuro_nao_vira_pedido(self):
        livro = CI.correr("pergunta de teste", [item(FACT_TIME="20-22 aprile 2027")])
        self.assertEqual(livro["REQUIREMENTS"], [])
        f = livro["FUTURE_DATED_FACTS"][0]
        self.assertEqual(f["ESPECIE"], "FACTO_PRESENTE_SOBRE_O_FUTURO")
        self.assertIn("SINAL_FRACO", f["NAO_E"])          # §28: data futura != forecast
        self.assertIn("LACUNA_DA_COLETA", f["NAO_E"])
        self.assertEqual(f["RAW_OBSERVATION_ID"], 1062)   # lineage nao se perde

    def test_positivo_futuro_com_outra_falta_ainda_pede_a_outra(self):
        livro = CI.correr("pergunta de teste", [item(FACT_TIME="20-22 aprile 2027",
                                                     RAW_OBSERVATION_ID="NAO SEI")])
        falta = livro["REQUIREMENTS"][0]["MISSING_FACT_OR_KEY"]
        self.assertIn("RAW_OBSERVATION_ID", falta)
        self.assertNotIn("FACT_TIME:FUTURO_EM_RELACAO_A_CAPTURA", falta)
        self.assertEqual(len(livro["FUTURE_DATED_FACTS"]), 1)

    def test_positivo_falta_real_continua_pedido(self):
        livro = CI.correr("pergunta de teste", [item(FACT_TIME="NAO SEI")])
        self.assertEqual(len(livro["REQUIREMENTS"]), 1)
        self.assertEqual(livro["FUTURE_DATED_FACTS"], [])

    def test_negativo_futuro_nao_vira_sinal_nem_saida(self):
        livro = CI.correr("pergunta de teste", [item(FACT_TIME="2027-04-20")])
        self.assertEqual(livro["SIGNALS"], [])
        self.assertEqual(livro["ANALYTIC_OUTPUT"], CI.SEM_SAIDA_ANALITICA)


class D15_OSinalDizAIdade(unittest.TestCase):
    def idade(self, **kw):
        return CI.correr("pergunta de teste", [item(**kw)])["SIGNALS"][0]["IDADE_NA_CAPTURA"]

    def test_negativo_2010_e_2026_nao_saem_iguais(self):
        velho = self.idade(FACT_TIME="campagna 2010")
        novo = self.idade(FACT_TIME="2026-09-23")
        self.assertGreater(velho["MIN_DIAS"], 5000)
        self.assertEqual(novo["MIN_DIAS"], 2)
        self.assertEqual(novo["MAX_DIAS"], 2)

    def test_o_intervalo_da_min_e_max(self):
        i = self.idade(FACT_TIME="2025")
        self.assertEqual(i["MIN_DIAS"], (CI.date(2026, 9, 25) - CI.date(2025, 12, 31)).days)
        self.assertEqual(i["MAX_DIAS"], (CI.date(2026, 9, 25) - CI.date(2025, 1, 1)).days)

    def test_negativo_idade_nao_e_veredito_de_acao(self):
        i = self.idade(FACT_TIME="campagna 2010")
        self.assertIn("NAO_AVALIADA", i["ATUALIDADE_PARA_AGIR"])
        self.assertNotIn("ACT_NOW", json.dumps(i))

    def test_negativo_sem_captura_idade_nao_sei_nunca_zero(self):
        self.assertEqual(CI.idade_na_captura({"CAPTURED_AT": "NAO SEI"},
                                             CI.intervalo_do_tempo("2026-09-23"))["MIN_DIAS"],
                         CI.NAO_SEI)


class RegraSobe(unittest.TestCase):
    def test_a_regra_subiu_para_v3(self):
        self.assertEqual(CI.RULESET_VERSION, "G0/v3")
