# -*- coding: utf-8 -*-
"""A REGUA T1 (CROP & PRODUCTION) PARA JANELAS DE CULTURA (D29) — T1-JANELA, 24/09.

Medida em `scripts/regua_t1/` (gabarito T1-V1: 55 YES / 80 NO / 46 NAO_SEI). Estes
testes guardam o mecanismo — cada um cai se uma decisao medida for desfeita:

    SIM pede CULTURA NOMEADA e DOIS momentos distintos (SINAIS_MINIMOS)
    metade fica NAO_SEI (nunca NAO), com o motivo
    `raccolta` solto nao e momento; palavra inteira; conceito conta uma vez
    T1 e transversal: nunca prova que um texto NAO e de outro universo
    a porta nao decide a janela
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

AQUI = os.path.join(RAIZ, "scripts", "regua_t1")


def t1(texto):
    return adm._do_universo({"texto": texto}, "T1", adm.PERGUNTAS_DO_UNIVERSO["T1"])


class CulturaEDoisMomentos(unittest.TestCase):

    def test_boletim_por_cultura_entra(self):
        r, _m, ev = t1("OLIVO · Fase fenologica: invaiatura. Soglia di intervento: 5% di drupe infestate.")
        self.assertEqual(r, adm.SIM)
        self.assertTrue(ev["cultura"])

    def test_sem_cultura_fica_nao_sei(self):
        r, m, _ev = t1("Fase fenologica: invaiatura. Soglia di intervento superata.")
        self.assertEqual(r, adm.NAO_SEI)
        self.assertIn("SEM_CULTURA_NOMEADA", m)

    def test_um_so_momento_fica_nao_sei(self):
        """A campanha de uma marca de macas que fala da «fioritura primaverile» nao e janela."""
        r, m, _ev = t1("Le mele Marlene: dalla fioritura primaverile alla tavola.")
        self.assertEqual(r, adm.NAO_SEI)
        self.assertIn("UM_SO_MOMENTO", m)

    def test_cultura_sem_momento_fica_nao_sei(self):
        r, m, _ev = t1("Il pomodoro italiano conquista i mercati esteri.")
        self.assertEqual(r, adm.NAO_SEI)
        self.assertIn("SEM_MOMENTO", m)

    def test_a_metade_nunca_vira_nao(self):
        for t in ("fase fenologica e catture", "vite e olivo", "vite, fioritura"):
            with self.subTest(t=t):
                self.assertNotEqual(t1(t)[0], adm.NAO)

    def test_dois_momentos_do_mesmo_conceito_contam_um(self):
        """«fenologia» e «fase fenologica» sao o mesmo indicio."""
        self.assertEqual(t1("vite: fenologia, fase fenologica, fenologico")[0], adm.NAO_SEI)


class ORuidoQueFicouDeFora(unittest.TestCase):

    def test_raccolta_solta_nao_e_momento(self):
        """«raccolta dati», «raccolta differenziata» — e a colheita do mercado."""
        r, _m, ev = t1("Olive e vite: raccolta dei dati personali e raccolta differenziata; fioritura")
        self.assertEqual(r, adm.NAO_SEI)
        self.assertEqual(ev["palavras"], ["fioritura"])

    def test_raccolta_em_frase_e_momento(self):
        self.assertEqual(t1("Mele: inizio della raccolta e fioritura tardiva nel meleto")[0], adm.SIM)

    def test_pero_mas_nao_e_pera(self):
        """«però» (= mas) dobra para «pero»; `pero` nao esta na lista, `pere` esta."""
        self.assertEqual(t1("però il clima: fioritura, soglia di intervento")[0], adm.NAO_SEI)
        self.assertEqual(t1("pere: fioritura, soglia di intervento")[0], adm.SIM)

    def test_palavra_inteira_na_cultura(self):
        """`uva` nao casa dentro de «ruvida»; `vite` nao dentro de «invitee»."""
        self.assertEqual(t1("superficie ruvida: fioritura, soglia di intervento")[0], adm.NAO_SEI)


class T1ETransversal(unittest.TestCase):

    def test_palavras_de_t1_nao_provam_nao_noutro_universo(self):
        texto = "vite olivo: fioritura, invaiatura, catture, soglia di intervento"
        for u in ("T2", "T3", "T4", "T5", "T7", "T9", "T10"):
            with self.subTest(universo=u):
                _r, _m, ev = adm._do_universo({"texto": texto}, u, adm.PERGUNTAS_DO_UNIVERSO[u])
                self.assertNotIn("T1", (ev.get("achado_noutro") or {}))

    def test_sem_a_transversal_t1_seria_prova_contra_outro(self):
        """O contraponto: sem T1 em TRANSVERSAIS, as palavras de T1 viravam prova de NAO."""
        velho = adm.TRANSVERSAIS
        try:
            adm.TRANSVERSAIS = frozenset({"T2"})
            r, _m, ev = adm._do_universo({"texto": "fioritura e invaiatura"}, "T10",
                                         adm.PERGUNTAS_DO_UNIVERSO["T10"])
        finally:
            adm.TRANSVERSAIS = velho
        self.assertEqual(r, adm.NAO)
        self.assertIn("T1", ev["achado_noutro"])


class APortaNaoDecideAJanela(unittest.TestCase):

    def test_a_evidencia_so_traz_palavras(self):
        _r, _m, ev = t1("OLIVO bollettino del 14/09/2026, Brindisi: fase fenologica, catture")
        self.assertLessEqual(set(ev), {"palavras", "cultura", "sinais", "falta"})

    def test_decidir_nao_mexe_no_item(self):
        item = {"id": "x", "texto": "OLIVO fase fenologica invaiatura, catture in trappola",
                "source_id": "IT-T3-010", "url": "https://e.it/a", "artifact_type": "RAW",
                "captured_at": "2026-09-03T00:00:00Z"}
        antes = dict(item)
        adm.decidir(item, "T1", corrida="x")
        self.assertEqual(item, antes)


class OGabaritoEAMedicao(unittest.TestCase):

    def setUp(self):
        self.g = json.load(open(os.path.join(AQUI, "GABARITO-T1-V1.json"), encoding="utf-8"))
        self.m = json.load(open(os.path.join(AQUI, "MEDICAO-REGUA-T1-V1.json"), encoding="utf-8"))

    def test_gabarito_20_de_cada_lado_e_nao_validado(self):
        c = self.g["CONTAGEM"]
        self.assertGreaterEqual(c["YES"], 20)
        self.assertGreaterEqual(c["NO"], 20)
        self.assertEqual(self.g["VALIDADO_POR_HUMANO"], "NAO")

    def test_a_medicao_e_da_regua_escrita(self):
        self.assertEqual(self.m["REGUA"]["MOMENTOS"], adm.PERGUNTAS_DO_UNIVERSO["T1"])
        self.assertEqual(self.m["REGUA"]["CULTURA"], adm.CULTURA_OBRIGATORIA["T1"])
        self.assertEqual(self.m["VERSAO_DA_REGRA"], adm.VERSAO_DA_REGRA)

    def test_vizinhos_intactos_e_sha_a_bater(self):
        self.assertEqual(self.m["VIZINHOS"]["VEREDITOS_VIZINHOS_MUDADOS"], 0)
        self.assertGreater(self.m["VIZINHOS"]["JULGAMENTOS"], 9000)
        self.assertEqual(self.m["SHA_NAO_CONFERE"], [])

    def test_precisao_e_recall_minimos_dentro_da_amostra(self):
        t = self.m["T1_TOTAL"]
        self.assertIs(self.m["MEDIDO_DENTRO_DA_AMOSTRA"], True)
        self.assertGreaterEqual(t["PRECISAO"], 0.9)
        self.assertGreaterEqual(t["RECALL"], 0.9)
        self.assertEqual(t["YES_QUE_SAIRAM_NAO"], 0)


if __name__ == "__main__":
    unittest.main()
