#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXTRATOR-LUGAR-V2 — mais lugar do facto, com a MESMA lei (lugar preso a acontecimento).

    1. comune pela lista oficial do ISTAT (ficheiro declarado; sem ele, nada muda);
    2. «provincia di X» / «in provincia di X» / «nel X-ese» -> PROVINCE;
    3. o titulo curto entra na leitura (sem o nome do site);
    4. nunca: a sede de quem publica, o nome de um orgao, o homonimo sem sigla.

Os comuni vem de uma AMOSTRA COM O FORMATO do CSV do ISTAT (tests/dados/lugar_v2/AMOSTRA-FORMATO-ISTAT.csv,
4 linhas) — NAO e a lista oficial. As frases reais sao da RENDIMENTO-POR-FONTE (IT-T12-024, IT-T12-008, IT-T2-051).
"""
from __future__ import annotations

import os
import sys
import unittest
from unittest import mock

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "leis"))
import fato_local as FL  # noqa: E402
import fato_do_texto as T  # noqa: E402

AMOSTRA = os.path.join(RAIZ, "tests", "dados", "lugar_v2", "AMOSTRA-FORMATO-ISTAT.csv")


def _mencoes(frase):
    return [(m["PLACE"], m["PRECISION"], m.get("VIA")) for m in FL.mencoes(frase)]


def _aceitas(texto):
    return [(a["FACT_LOCATION"], a["FACT_LOCATION_PRECISION"], a.get("FACT_LOCATION_PROVINCE"))
            for a in FL.localizacoes_do_fato(texto)[0]]


class ProvinciaDi(unittest.TestCase):
    def test_frase_real_it_t12_024_e_provincia_mas_sem_acontecimento_agro_nao_e_facto(self):
        f = "Venti forti dell'11 maggio 2026 in provincia di Verona"
        self.assertEqual([("Verona", "PROVINCE", "provincia di")], _mencoes(f))
        self.assertEqual([], _aceitas(f))                                   # a lei de sempre: sem ancora, nao

    def test_com_acontecimento_a_provincia_e_o_lugar_do_facto(self):
        self.assertEqual([("Verona", "PROVINCE", None)],
                         _aceitas("Constatata la presenza di Popillia japonica in provincia di Verona"))

    def test_adjectivo_em_ese_derivado_da_lista(self):
        self.assertEqual([("Verona", "PROVINCE", "aggettivo -ese")], _mencoes("focolai di peronospora nel veronese"))
        self.assertEqual([("Modena", "PROVINCE", None)], _aceitas("rilevati focolai di peronospora nel modenese"))

    def test_adjectivo_que_nao_vem_da_lista_nao_e_lugar(self):
        self.assertEqual([], _mencoes("rilevati focolai nel francese e nel paese"))

    def test_o_orgao_provincia_sem_acontecimento_nao_e_facto(self):
        self.assertEqual([], _aceitas("La Provincia di Verona ha approvato il bando per le imprese"))


class ComuneIstat(unittest.TestCase):
    def setUp(self):
        self.p = mock.patch.object(FL, "COMUNI_ISTAT", AMOSTRA)
        self.p.start()

    def tearDown(self):
        self.p.stop()

    def test_comune_com_sigla_sai_com_a_provincia_e_precisao_municipality(self):
        self.assertEqual([("Pontenure", "MUNICIPALITY", "Piacenza")],
                         _aceitas("Constatato un focolaio di peronospora a Pontenure (PC)"))

    def test_comune_de_duas_palavras(self):
        self.assertEqual([("Finale Emilia", "MUNICIPALITY", "Modena")],
                         _aceitas("Rilevata la presenza di cimice asiatica a Finale Emilia"))

    def test_homonimo_sem_sigla_fica_de_fora_e_com_sigla_resolve(self):
        self.assertEqual([], _aceitas("Rilevata la presenza di cimice asiatica a Castro"))
        self.assertEqual([("Castro", "MUNICIPALITY", "Lecce")],
                         _aceitas("Rilevata la presenza di cimice asiatica a Castro (LE)"))

    def test_minusculas_nao_sao_comune(self):
        self.assertEqual([], [m for m in _mencoes("il castro del campo e pontenure") if m[2] == "comune ISTAT"])

    def test_a_cobertura_diz_a_fonte(self):
        FL._COMUNI.pop(AMOSTRA, None)
        c = FL.cobertura()
        self.assertEqual(4, c["MUNICIPALITIES"])
        self.assertEqual(AMOSTRA, c["MUNICIPALITIES_SOURCE"]["FICHEIRO"])


class SemListaNadaMuda(unittest.TestCase):
    def test_sem_o_ficheiro_o_comune_e_invisivel_e_a_cobertura_diz_ausente(self):
        with mock.patch.object(FL, "COMUNI_ISTAT", os.path.join(RAIZ, "nao-existe.csv")):
            self.assertEqual([], _aceitas("Constatato un focolaio di peronospora a Pontenure (PC)"))
            self.assertIn("AUSENTE", FL.cobertura()["MUNICIPALITIES_SOURCE"])


class TituloCurto(unittest.TestCase):
    def test_titulo_real_it_t12_008_entra_sem_o_nome_do_site(self):
        texto = ("Potatura dell'olivo: a Macerata la 9a selezione studenti - YouTube\n"
                 "Informazioni Stampa Copyright Contattaci Creator Pubblicità\n© 2026 Google LLC")
        self.assertEqual("Potatura dell'olivo: a Macerata la 9a selezione studenti", T.titulo(texto))
        self.assertTrue(T.corpo(texto).startswith("Potatura dell'olivo"))
        self.assertNotIn("YouTube", T.corpo(texto))

    def test_titulo_curto_com_acontecimento_da_lugar_pela_mesma_regra(self):
        r = T.campos_do_fato("Grandinata, danni constatati a Verona - YouTube\nx")
        self.assertEqual("Verona", r["fact_location"])

    def test_o_nome_do_site_nunca_entra_mesmo_com_regiao(self):
        c = T.corpo("Opportunità di lavoro in Arpae — Arpae Emilia-Romagna\nVai al Contenuto")
        self.assertEqual("Opportunità di lavoro in Arpae", c)
        self.assertNotIn("Emilia-Romagna", c)

    def test_titulo_generico_de_duas_palavras_nao_entra(self):
        self.assertEqual("", T.titulo("Dettaglio news - Regione del Veneto\nSalta al contenuto"))

    def test_a_morada_do_rodape_nunca_e_lugar(self):
        r = T.campos_do_fato("Notizia - Sito\nDIREZIONE GENERALE Via Po, 5 – 40139 Bologna tel 051 1234567 constatati danni")
        self.assertEqual("NAO SEI", r["fact_location"])


class CasosLidosAMaoNaSala(unittest.TestCase):
    """As frases reais das 4 trocas de lugar na Sala (medida antes x depois), lidas a mao."""

    def _lugares(self, texto):
        ev = T.campos_do_fato(texto).get("EVIDENCIA") or {}
        return {(l["LUGAR"], l["KIND"]) for l in ev.get("LUGARES") or []}

    def test_it_t3_008_chuva_registada_in_provincia_di_lecce_e_campo(self):
        t = ("Titolo lungo del bollettino agrometeorologico settimanale della regione Puglia\n"
             "Gli accumuli settimanali più importanti si sono registrati in provincia di Lecce a Nociglia e Otranto, "
             "rispettivamente con 46 e 40 millimetri di pioggia")
        self.assertIn(("Lecce", "CAMPO"), self._lugares(t))

    def test_it_t10_018_mercato_in_provincia_di_ragusa_e_mercado(self):
        t = ("Dai mercati: pomodori sempre alle stelle - Myfruit\n"
             "Al mercato ortofrutticolo di Vittoria, in provincia di Ragusa, i prezzi del pomodoro continuano a rimanere molto alti")
        self.assertIn(("Ragusa", "MERCADO"), self._lugares(t))

    def test_it_t5_010_a_ancora_dentro_do_nome_de_um_orgao_nao_conta(self):
        t = ("Rivista quadrimestrale di economia e cultura della Camera di Commercio\n"
             "Nel 1895 viene fondato a Scafati, in provincia di Salerno, l'Istituto Sperimentale e di Tirocinio "
             "per la Coltivazione dei Tabacchi, con il compito di sperimentare nuove varietà")
        self.assertNotIn(("Salerno", "CAMPO"), self._lugares(t))

    def test_o_titulo_nao_perde_a_data_que_vem_depois_do_traco(self):
        self.assertEqual("Evento RetePAC Valutazioni ex post - 26 Maggio 2026",
                         T.titulo("Evento RetePAC Valutazioni ex post - 26 Maggio 2026\nx"))


if __name__ == "__main__":
    unittest.main()
