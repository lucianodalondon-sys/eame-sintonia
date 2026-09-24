# -*- coding: utf-8 -*-
"""A REGUA T2 (D29 — JANELAS DE CULTURA) E AS LEIS QUE ELA NAO PODE QUEBRAR.

Medida em `scripts/regua_t2/` (gabarito T2-V2, 45 YES / 225 NO). Estes testes
guardam o MECANISMO — cada um cai se uma das decisoes medidas for desfeita:

    SIM pede CONDICAO do campo E LIGACAO AGRICOLA escrita
    metade fica NAO_SEI (nunca NAO), com o motivo e a marca D2
    palavra inteira, conceito conta uma vez
    T2 e transversal: nunca prova que um item NAO e de outro universo
    a porta nao decide a janela nem escreve tempo/lugar do facto
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402

AQUI = os.path.join(RAIZ, "scripts", "regua_t2")


def t2(texto):
    return adm._do_universo({"texto": texto}, "T2", adm.PERGUNTAS_DO_UNIVERSO["T2"])


class OSimPedeAsDuasCoisas(unittest.TestCase):

    def test_condicao_e_fenologia_entram(self):
        r, _m, ev = t2("Bollettino: fase fenologica invaiatura; piogge e temperature in calo.")
        self.assertEqual(r, adm.SIM)
        self.assertTrue(ev["palavras"] and ev["ancoras"])

    def test_tempo_sem_cultura_fica_nao_sei_com_d2(self):
        r, m, ev = t2("Previsioni: piogge diffuse, temperature in calo, anticiclone in ritiro.")
        self.assertEqual(r, adm.NAO_SEI, "tempo sem ligacao agricola nao e janela")
        self.assertIn("SEM_LIGACAO_AGRICOLA", m)
        self.assertEqual(ev.get("d2"), "REROUTE_POSSIVEL")

    def test_fenologia_sem_condicao_fica_nao_sei(self):
        r, m, _ev = t2("Fase fenologica: invaiatura. Soglia di intervento: 2 individui per pianta.")
        self.assertEqual(r, adm.NAO_SEI)
        self.assertIn("SEM_CONDICAO_DO_CAMPO", m)

    def test_agrometeo_so_conta_com_duas_condicoes(self):
        self.assertEqual(t2("Agrometeo · siccita in pianura")[0], adm.NAO_SEI,
                         "o menu «Agrometeo» com uma palavra de tempo entrou")
        self.assertEqual(t2("Bollettino agrometeorologico: siccita e temperature record")[0], adm.SIM)

    def test_a_metade_nunca_vira_nao(self):
        for texto in ("piogge e temperature", "fase fenologica e catture"):
            with self.subTest(texto=texto):
                self.assertNotEqual(t2(texto)[0], adm.NAO)


class PalavraInteiraEConceitoUmaVez(unittest.TestCase):

    def test_serie_temporali_nao_e_trovoada(self):
        r, _m, ev = t2("Le serie temporali di temperatura; fase fenologica.")
        self.assertEqual(r, adm.SIM)
        self.assertNotIn("temporalesco", ev["palavras"])

    def test_privacidade_e_lixo_nao_sao_ancora(self):
        r, m, _ev = t2("Trattamento dei dati personali. Raccolta differenziata. Pioggia.")
        self.assertEqual(r, adm.NAO_SEI)
        self.assertIn("SEM_LIGACAO_AGRICOLA", m)

    def test_seca_dentro_de_secao_nao_casa(self):
        """«seca» vive dentro de «secao» (seccao do site, em portugues)."""
        r, _m, ev = t2("nesta secao do site: fase fenologica")
        self.assertEqual(r, adm.NAO_SEI, "a seca casou dentro de «secao»")
        self.assertNotIn("siccita", ev.get("palavras", []))

    def test_singular_e_plural_sao_um_indicio(self):
        r, _m, ev = t2("pioggia, piogge, precipitazioni — agrometeo")
        self.assertEqual(ev["palavras"], ["pioggia"])
        self.assertEqual(r, adm.NAO_SEI, "tres formas da chuva nao sao duas condicoes")


class T2ETransversal(unittest.TestCase):
    """«As chuvas da semana passada aumentaram os voos» nao tira um boletim de T3."""

    def test_palavras_de_t2_nao_provam_nao_noutro_universo(self):
        for u in ("T3", "T4", "T5", "T7", "T9", "T10"):
            with self.subTest(universo=u):
                r, _m, ev = adm._do_universo({"texto": "piogge e temperature in calo, siccita"},
                                             u, adm.PERGUNTAS_DO_UNIVERSO[u])
                self.assertNotEqual(r, adm.NAO, "T2 serviu de prova contra %s" % u)
                self.assertNotIn("T2", (ev.get("achado_noutro") or {}))

    def test_sem_a_transversal_t2_seria_prova_contra_t3(self):
        """O contraponto: o mecanismo de prova-noutro-universo VE as formas de T2 —
        e so a transversalidade as cala. Sem isto, tirar T2 de TRANSVERSAIS nao
        mudava nada e a guarda acima guardava por acidente."""
        velho = adm.TRANSVERSAIS
        try:
            adm.TRANSVERSAIS = frozenset()
            r, _m, ev = adm._do_universo({"texto": "piogge e temperature in calo"}, "T3",
                                         adm.PERGUNTAS_DO_UNIVERSO["T3"])
        finally:
            adm.TRANSVERSAIS = velho
        self.assertEqual(r, adm.NAO)
        self.assertIn("T2", ev["achado_noutro"])

    def test_t2_e_transversal_e_palavra_inteira(self):
        self.assertIn("T2", adm.TRANSVERSAIS)
        self.assertIn("T2", adm.PALAVRA_INTEIRA)


class APortaNaoDecideAJanela(unittest.TestCase):
    """Data de calendario != janela; FACT_TIME != PUBLICATION_TIME;
    SOURCE_LOCATION != FACT_LOCATION. A regua admite; a Intelligence decide."""

    def test_a_evidencia_nao_traz_tempo_nem_lugar(self):
        _r, _m, ev = t2("Bollettino del 14/09/2026, Veneto: fase fenologica, piogge.")
        self.assertLessEqual(set(ev), {"palavras", "ancoras", "sinais"})

    def test_decidir_nao_escreve_fact_time_nem_fact_location(self):
        item = {"id": "x", "texto": "Bollettino: fase fenologica invaiatura, piogge e temperature",
                "source_id": "IT-T2-002", "url": "https://e.it/a", "artifact_type": "RAW",
                "captured_at": "2026-09-03T00:00:00Z"}
        antes = dict(item)
        adm.decidir(item, "T2", corrida="x")
        self.assertEqual(item, antes, "a porta mexeu no item")


class OIngles(unittest.TestCase):

    def test_boletim_ingles_entra_pela_lista_inglesa(self):
        texto = ("Weekly crop bulletin. The weather this week brought heavy rainfall and "
                 "temperatures well above the seasonal average across the region, and the "
                 "vineyards are now at veraison. Trap catches of the moth increased after the "
                 "rain, and growers should check the action threshold before any treatment. "
                 "This is the advice of the regional service for the growers of the area, and it "
                 "will be updated with the next bulletin of the week when the data are in.")
        r, _m, ev = t2(texto)
        self.assertEqual(r, adm.SIM, ev)


class OGabaritoEAMedicao(unittest.TestCase):

    def setUp(self):
        self.g = json.load(open(os.path.join(AQUI, "GABARITO-T2-V2.json"), encoding="utf-8"))
        self.m = json.load(open(os.path.join(AQUI, "MEDICAO-REGUA-T2-V2.json"), encoding="utf-8"))

    def test_o_gabarito_tem_20_de_cada_lado_e_nao_foi_validado(self):
        c = self.g["CONTAGEM"]
        self.assertGreaterEqual(c["YES"], 20)
        self.assertGreaterEqual(c["NO"], 20)
        self.assertEqual(self.g["VALIDADO_POR_HUMANO"], "NAO")
        self.assertTrue({i["JANELA"] for i in self.g["ITENS"]} <= {"YES", "NO", "NAO_SEI"})

    def test_cada_item_tem_origem_e_sha(self):
        for i in self.g["ITENS"]:
            self.assertEqual(len(i["TEXTO_SHA256"]), 64)
            self.assertTrue(i["CAMINHO_FORA_DO_GIT"])

    def test_a_medicao_e_da_regua_que_esta_escrita(self):
        """Mudar a lista sem voltar a medir deixa esta medicao a descrever outra regua."""
        self.assertEqual(self.m["REGUA"]["IT_PT"], adm.PERGUNTAS_DO_UNIVERSO["T2"])
        self.assertEqual(self.m["REGUA"]["ANCORAS"], adm.ANCORAS["T2"])
        self.assertEqual(self.m["VERSAO_DA_REGRA"], adm.VERSAO_DA_REGRA)

    def test_os_vizinhos_nao_mudaram(self):
        self.assertEqual(self.m["VIZINHOS"]["VEREDITOS_VIZINHOS_MUDADOS"], 0)
        self.assertGreater(self.m["VIZINHOS"]["JULGAMENTOS"], 1000)

    def test_a_medicao_diz_que_e_dentro_da_amostra(self):
        self.assertIs(self.m["T2"]["MEDIDO_DENTRO_DA_AMOSTRA"], True)


if __name__ == "__main__":
    unittest.main()
