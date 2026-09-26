# -*- coding: utf-8 -*-
"""PERIODO-E-CHAVES (26/09) — o periodo, a regiao sem nomes, a cultura fora de T1.

A QUATRO-CHAVES-MEDIR mediu 0 cruzamentos possiveis: o PERIODO estava sempre NAO SEI, 3 de 12
regioes eram erradas, e 4 de 20 textos nomeavam a cultura que ficava de fora. Cada teste traz um
EXEMPLO REAL (trecho curto de pagina publica guardada no armazem ou na Sala), salvo onde diz
«sintetico». Sem banco e sem rede.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(RAIZ, "admissao"), RAIZ]

import admissao as A  # noqa: E402
from leis import fato_do_texto as F  # noqa: E402

NAO_SEI = A.AUSENCIA


def _periodo(fact_time, base="EVENTO · ESCRITO_NO_TEXTO", **extra):
    return A.periodo_do_fato(dict({"fact_time": fact_time, "fact_time_basis": base}, **extra))


class OPeriodoVemSoDoFactTime(unittest.TestCase):

    def test_formas_reais_da_sala(self):
        # os FACT_TIME que a Sala guarda hoje (sala_de_espera_atual, 26/09)
        casos = {
            "12-13 novembre 2026": ("2026-11-12/2026-11-13", "INTERVALO"),
            "1-4 febbraio 2023": ("2023-02-01/2023-02-04", "INTERVALO"),
            "29 settembre 2026": ("2026-09-29", "DIA"),
            "2025": ("2025", "ANO"),
            "campagna 2010": ("2010", "ANO"),
            "raccolta 2026": ("2026", "ANO"),
        }
        for ft, (valor, precisao) in casos.items():
            p = _periodo(ft)
            self.assertEqual((p["VALOR"], p["PRECISAO"]), (valor, precisao), ft)
            self.assertEqual(p["EXPRESSAO"], ft)

    def test_mes_com_ano_e_intervalo_entre_meses(self):  # sintetico
        self.assertEqual(_periodo("maggio 2026")["VALOR"], "2026-05")
        self.assertEqual(_periodo("30 settembre - 2 ottobre 2026")["VALOR"], "2026-09-30/2026-10-02")

    def test_sem_ano_escrito_fica_nao_sei_mesmo_com_publicacao(self):
        # reais: «28 settembre» (IT-T5-186), «21-23 ottobre» (IT-T9-021), «maggio» (Sala)
        for ft in ("28 settembre", "21-23 ottobre", "maggio"):
            p = _periodo(ft, published_at="2026-09-01", captured_at="2026-09-20T10:00:00Z")
            self.assertEqual(p["VALOR"], NAO_SEI, ft)
            self.assertIn("publicacao", p["PORQUE"])

    def test_so_publicacao_nao_da_periodo(self):
        p = A.periodo_do_fato({"published_at": "2026-05-10", "captured_at": "2026-09-20T12:00:00Z"})
        self.assertEqual(p["VALOR"], NAO_SEI)
        p = A.periodo_do_fato({"fact_time": "NAO SEI", "published_at": "2026-05-10"})
        self.assertEqual(p["VALOR"], NAO_SEI)

    def test_data_que_nao_existe_nao_e_periodo(self):  # sintetico
        self.assertEqual(_periodo("31 febbraio 2026")["VALOR"], NAO_SEI)
        self.assertEqual(_periodo("2026-09-13/2026-09-07")["VALOR"], NAO_SEI)

    def test_a_calculada_da_publicacao_passa_marcada(self):
        # real: «2026-09-07/2026-09-13 · RELATIVA_A_PUBLICACAO» (Sala)
        p = _periodo("2026-09-07/2026-09-13", base="RELATIVA_A_PUBLICACAO")
        self.assertEqual(p["VALOR"], "2026-09-07/2026-09-13")
        self.assertEqual(p["PRECISAO"], "INTERVALO+CALCULADA")

    def test_a_janela_leva_o_periodo_com_base(self):
        item = {"texto": "Il workshop si terrà il 12 e 13 novembre 2026 a Napoli.", "source_id": "IT-T5-900",
                "fact_time": "12-13 novembre 2026", "fact_time_basis": "EVENTO · ESCRITO_NO_TEXTO"}
        d = A.decidir(item, "T5", corrida="RUN-TESTE")
        j = A.janela_para_o_ready(item, d)
        self.assertEqual(j["JANELA"]["VALOR"], "2026-11-12/2026-11-13")
        self.assertEqual(j["JANELA"]["BASE"], "EVENTO · ESCRITO_NO_TEXTO")
        self.assertIn("item.fact_time", j["JANELA"]["VEIO_DE"])
        self.assertEqual(j["PRECISAO"]["CHAVES_COM_VALOR"], 1)


class ARegiaoNaoEPedacoDeNome(unittest.TestCase):

    def test_bologna_fiere_e_empresa(self):
        # real: IT-T7-031 (FederBio), bruto 394a362f
        t = ("Partecipano alle attività del progetto anche alcune aziende italiane: Vallefiorita, "
             "Solleone, Bio Organica Italia, oltre che Bologna Fiere, socio di FederBio.")
        self.assertNotEqual(F.campos_do_fato(t)["fact_location"], "Bologna")

    def test_arpa_lazio_e_quem_publica(self):
        # real: IT-T2-025, bruto 19971f5d (titulo de video)
        t = "ARPA Lazio – Seminario su applicativo web ORSo del 9/7/20 – Parte 2/3: Esercitazione 1 - YouTube"
        self.assertNotEqual(F.campos_do_fato(t)["fact_location"], "Lazio")

    def test_a_fiera_bolzano_continua_a_ser_o_local(self):
        # real: IT-T10-018, bruto 9e3e9d34 — a preposicao «a» diz que e o SITIO
        t = ("Dalla teoria alla pratica: a Interpoma 2026 , fiera internazionale della mela in programma "
             "dal 25 al 27 novembre a Fiera Bolzano , le tecnologie destinate a trasformare la gestione "
             "del meleto potranno essere viste e approfondite direttamente.")
        self.assertEqual(F.campos_do_fato(t)["fact_location"], "Bolzano")

    def test_presso_o_orgao_e_o_local(self):  # sintetico
        t = "Il seminario tecnico si terrà presso ARPA Lazio il 5 ottobre 2026 con i tecnici regionali."
        self.assertEqual(F.campos_do_fato(t)["fact_location"], "Lazio")

    def test_so_le_a_frase(self):
        self.assertEqual(F._e_pedaco_de_nome("oltre che Bologna Fiere, socio", 10, "Bologna"), "Bologna Fiere")
        self.assertEqual(F._e_pedaco_de_nome("ARPA Lazio – Seminario", 5, "Lazio"), "ARPA Lazio")
        self.assertIsNone(F._e_pedaco_de_nome("si terrà a Bologna il 5", 12, "Bologna"))


class ACulturaForaDeT1(unittest.TestCase):

    def _janela(self, texto, universo, **extra):
        item = dict({"texto": texto, "source_id": "IT-%s-900" % universo}, **extra)
        d = A.decidir(item, universo, corrida="RUN-TESTE")
        return A.janela_declarada(item, d)

    def test_o_titulo_nomeia_a_cultura(self):
        # reais: IT-T10-017 (4510c175), IT-T9-017 (d7284a8f), IT-T10-018 (bdcc232c)
        casos = (("Le fragole al Mercato Ortofrutticolo di Milano - YouTube", "T10", ["fragole"]),
                 ("Strategie di biocontrollo Koppert su mora - YouTube", "T9", ["mora"]),
                 ("Piccoli frutti, a Firenze prezzo mirtilli sempre più su", "T10", ["mirtilli"]))
        for titulo, uni, esperado in casos:
            j = self._janela(titulo + "\nHome News Contatti", uni)
            self.assertEqual(j["CULTURA"]["VALOR"], esperado, titulo)
            self.assertIn("titulo", j["CULTURA"]["VEIO_DE"])
            self.assertIn("nao decisao da porta", j["CULTURA"]["BASE"])
            self.assertEqual(j["FASE"]["VALOR"], NAO_SEI)

    def test_a_frase_que_prova_o_lugar_nomeia_a_cultura(self):
        # real: IT-T10-018 (9e3e9d34) — o titulo nao diz, a prova do lugar diz «mela», «meleto»
        base = ("EVENTO · EVENTO · CITADO · PROVINCE · âncora «Fiera» · OTHER · «a Interpoma 2026 , fiera "
                "internazionale della mela in programma dal 25 al 27 novembre a Fiera Bolzano , le "
                "tecnologie destinate a trasformare la gestione del meleto»")
        j = self._janela("The Orchard of the Future, a Interpoma 2026\nmenu", "T10",
                         fact_location="Bolzano", fact_location_basis=base)
        self.assertEqual(sorted(j["CULTURA"]["VALOR"]), ["mela", "meleto"])
        self.assertIn("frase que prova o lugar", j["CULTURA"]["VEIO_DE"])

    def test_a_barra_lateral_nao_conta(self):
        # a myfruit repete titulos de outras noticias no corpo; so titulo e prova contam
        j = self._janela("Logistica e Gdo, l'IA riempie i camion vuoti\n"
                         "Piccoli frutti, a Firenze prezzo mirtilli sempre più su", "T10")
        self.assertEqual(j["CULTURA"]["VALOR"], NAO_SEI)

    def test_mora_de_pagamento_nao_e_fruta(self):  # sintetico
        j = self._janela("Pagamenti PAC: interessi di mora per i ritardi della Regione", "T7")
        self.assertEqual(j["CULTURA"]["VALOR"], NAO_SEI)

    def test_a_evidencia_de_outra_regua_nao_e_cultura(self):
        """Uma decisao T2 com `cultura: True` na evidencia NAO da cultura: so o texto do item conta."""
        item = {"texto": "Bollettino agrometeo: pioggia e temperatura della settimana", "source_id": "IT-T2-900"}
        d = A.Decisao(item="x", universo="T2", resultado=A.SIM, regra="pertence ao universo",
                      motivo="x", evidencia={"palavras": ["pioggia"], "cultura": True})
        j = A.janela_declarada(item, d)
        self.assertEqual(j["CULTURA"]["VALOR"], NAO_SEI)
        self.assertEqual(j["FASE"]["VALOR"], NAO_SEI)

    def test_t1_continua_pela_regua(self):
        item = {"texto": "Bollettino tecnico vite. Fase di fioritura in corso nei vigneti di collina. "
                         "Superata la soglia di intervento per infestazione di tignoletta: si consiglia "
                         "il trattamento fitosanitario entro la settimana.",
                "source_id": "IT-T1-900", "id": "derived:1", "artifact_type": "DERIVED",
                "parent_sha256": "a" * 64}
        j = A.janela_declarada(item, A.decidir(item, "T1", corrida="RUN-TESTE"))
        self.assertIn("decisao.evidencia.cultura", j["CULTURA"]["VEIO_DE"])


class OCadernoEscreveAsChaves(unittest.TestCase):
    """As 2 mudancas na ferramenta do caderno de revisoes (`admissao/reprocessar_tempo_lugar.py`)."""

    BOLETIM = ("Bollettino tecnico vite. Fase di fioritura in corso nei vigneti di collina.\n"
               "Superata la soglia di intervento per infestazione di tignoletta: si consiglia "
               "il trattamento fitosanitario entro la settimana.")

    def _linha(self, texto, universo="T1", sid="IT-T1-900"):
        return {"RUN_ID": "RUN-T", "ORDEM": 0, "ITEM_ID": "derived:9", "RAW_OBSERVATION_ID": 9,
                "UNIVERSO": universo, "SOURCE_ID": sid, "CAPTURED_AT": "2026-09-20T10:00:00Z",
                "SHA256": "c" * 64, "TEXTO": texto}

    def test_a_janela_entra_no_caderno_com_json_ordenado(self):
        import json
        import reprocessar_tempo_lugar as RP
        ready = RP.ready_de(self._linha(self.BOLETIM), None)
        revs = RP.revisoes_de(ready)
        jan = [r for r in revs if r["CAMPO"] == "janela_declarada"]
        self.assertEqual(len(jan), 1)
        self.assertEqual(json.loads(jan[0]["VALOR"]), ready["JANELA_DECLARADA"])
        self.assertEqual(jan[0]["VALOR"], json.dumps(ready["JANELA_DECLARADA"], ensure_ascii=False,
                                                     sort_keys=True))
        # o mesmo codigo duas vezes da o mesmo texto: `rever` nao escreve de novo
        self.assertEqual(RP.revisoes_de(RP.ready_de(self._linha(self.BOLETIM), None)), revs)

    def test_cultura_e_fase_leem_a_evidencia_de_hoje(self):
        import reprocessar_tempo_lugar as RP
        j = RP.ready_de(self._linha(self.BOLETIM), None)["JANELA_DECLARADA"]
        self.assertIn("vite", j["CULTURA"]["VALOR"])
        self.assertIn("decisao.evidencia.cultura", j["CULTURA"]["VEIO_DE"])
        self.assertNotEqual(j["FASE"]["VALOR"], NAO_SEI)

    def test_a_admissao_da_linha_nao_muda(self):
        import reprocessar_tempo_lugar as RP
        texto = "Riunione del consiglio direttivo e approvazione del bilancio annuale dell'associazione."
        ready = RP.ready_de(self._linha(texto), None)
        self.assertEqual(ready["JANELA_DECLARADA"]["ORIGEM"]["RESULTADO"], A.SIM)
        base = [r for r in RP.revisoes_de(ready) if r["CAMPO"] == "janela_declarada"][0]["BASE"]
        self.assertIn("resultado de hoje: %s" % ready["_RESULTADO_DA_REGUA_HOJE"], base)
        self.assertNotEqual(ready["_RESULTADO_DA_REGUA_HOJE"], A.SIM)
        self.assertIn("a admissao da linha nao muda", base)

    def test_janela_e_campo_revisivel_na_033(self):
        import sala_de_espera as S
        self.assertIn("janela_declarada", S.CAMPOS_REVISIVEIS)


if __name__ == "__main__":
    unittest.main()
