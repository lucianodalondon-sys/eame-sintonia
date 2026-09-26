#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXTRATOR-EVENTO-V2 · D84 — cultura, praga/doenca e fase dos boletins (T3/T2), o periodo do cabecalho,
e o ano de comparacao. Trechos REAIS dos boletins da Sala (IT-T3-002 Salerno, IT-T3-008 ARIF Puglia,
IT-T3-010). Sem rede, sem banco."""
from __future__ import annotations

import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ("", "leis", "admissao"):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)
import _gavetas  # noqa: E402,F401
import boletim_do_campo as BC  # noqa: E402
import fato_do_texto as FT  # noqa: E402

SALERNO = """BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI SALERNO
N° 27 del 16/09/2026
Stato fitosanitario delle colture
COLTURA N° Comune 1 Eboli
ACTINIDIA UTM
Varietà Stadio fenologico Stato Fitosanitario
Hayward
Ingrossamento frutto
Nulla
CIMICE ASIATICA (Halyomorpha halys); Non Presente
Monitoraggio: nelle fasi inziali porre attenzione ai punti di ingresso (vicinanza ad edifici, siepi, ecc.).
AGRUMI
Stadio fenologico: ripresa vegetativa
MOSCA DELLA FRUTTA (Ceratitis capitata): si segnalano catture in aumento nelle trappole di Battipaglia.
"""

ARIF = """Settimanale N. 37 Anno XL

09 - 15 settembre 2026

Agenzia regionale per le attività irrigue e forestali

Situazione Attuale
Olivo
La mosca dell'olivo (Bactrocera oleae) e presente con catture in aumento negli oliveti della provincia di Lecce, in fase di accrescimento frutti.
"""


class OBoletimPorSecaoDeCultura(unittest.TestCase):

    def test_real_salerno_cada_praga_e_fase_na_sua_cultura(self):
        r = BC.ler_boletim(SALERNO)
        self.assertEqual(["actinidia", "agrumi"], r["CULTURAS"])
        act, agr = [s for s in r["SECOES"] if s["CULTURA"]]
        self.assertEqual(["ingrossamento frutto"], [f["NOME"] for f in act["FASES"]])
        self.assertEqual(["ripresa vegetativa"], [f["NOME"] for f in agr["FASES"]])
        self.assertIn(("mosca della frutta", "PRESENTE"), [(p["NOME"], p["ESTADO"]) for p in agr["PROBLEMAS"]])

    def test_real_praga_non_presente_e_ausente_nunca_ocorrencia(self):
        r = BC.ler_boletim(SALERNO)
        act = [s for s in r["SECOES"] if s["CULTURA"] == "actinidia"][0]
        self.assertIn(("cimice asiatica", "AUSENTE"), [(p["NOME"], p["ESTADO"]) for p in act["PROBLEMAS"]])
        self.assertNotIn("cimice asiatica", r["PROBLEMAS_NAO_AUSENTES"])
        self.assertIn("mosca della frutta", r["PROBLEMAS_NAO_AUSENTES"])

    def test_praga_citada_sem_marca_nao_e_presente(self):
        r = BC.ler_boletim("VITE\nPeronospora: si ricorda di proteggere la vegetazione nelle fasi piu sensibili.")
        self.assertEqual([("peronospora", "CITADA")], [(p["NOME"], p["ESTADO"]) for p in r["SECOES"][0]["PROBLEMAS"]])

    def test_texto_antes_da_primeira_cultura_nao_herda_cultura(self):
        r = BC.ler_boletim("Andamento generale con catture di cimice asiatica in aumento su tutta la regione.\nOLIVO\nMosca dell'olivo presente.")
        self.assertIsNone(r["SECOES"][0]["CULTURA"])
        self.assertIn("cimice asiatica", [p["NOME"] for p in r["SECOES"][0]["PROBLEMAS"]])

    def test_a_mesma_cultura_repetida_e_uma_secao(self):
        r = BC.ler_boletim("OLIVO\nMosca dell'olivo presente.\nOLIVO\nOcchio di pavone presente.\nOLIVO\n")
        self.assertEqual(1, len([s for s in r["SECOES"] if s["CULTURA"] == "olivo"]))

    def test_frase_longa_com_cultura_nao_abre_secao(self):
        r = BC.ler_boletim("Nei vigneti della provincia si osservano sintomi di peronospora sulle foglie basali della vite.")
        self.assertEqual([], r["CULTURAS"])

    def test_real_arif_a_praga_com_a_cultura_no_nome_vai_para_essa_cultura(self):
        """IT-T3-008 (lido a mao): sem linha curta da vite, a Lobesia ia para o olivo; e «non si riscontrano
        catture» e AUSENTE."""
        t = ("OLIVO\n"
             "Mosca dell'olivo (Bactrocera oleae) : non riscontrate catture nelle trappole a feromoni.\n"
             "Tignoletta della vite (Lobesia botrana): non si riscontrano catture, si e in attesa della quarta generazione.\n")
        r = BC.ler_boletim(t)
        sec = {s["CULTURA"]: [(p["NOME"], p["ESTADO"]) for p in s["PROBLEMAS"]] for s in r["SECOES"]}
        # EXTRATORES-V2-JUNTOS: o nome cientifico entre parenteses e a mesma praga — conta uma vez
        self.assertEqual([("tignoletta della vite", "AUSENTE")], sec["vite"])
        self.assertNotIn("lobesia botrana", [n for n, _ in sec["olivo"]])
        self.assertEqual([], r["PROBLEMAS_NAO_AUSENTES"])

    def test_marciume_leva_o_nome_e_nao_a_preposicao(self):
        r = BC.ler_boletim("OLIVO\nMarciume del frutto e marciume radicale presenti.")
        self.assertEqual(["marciume radicale"], [p["NOME"] for p in r["SECOES"][0]["PROBLEMAS"]])


class OPeriodoDoCabecalho(unittest.TestCase):

    def test_real_arif_semana_do_cabecalho(self):
        r = FT.campos_do_fato(ARIF, "2026-09-09", "meta article:published_time")
        self.assertEqual(("09 - 15 settembre 2026", "CAMPO", "WEEK"),
                         (r["fact_time"], r["fact_time_kind"], r["fact_time_precision"]))
        self.assertIn("CABECALHO_DO_BOLETIM", r["fact_time_basis"])

    def test_real_salerno_numero_e_data_e_publicacao_nao_periodo(self):
        r = FT.campos_do_fato(SALERNO, "2026-09-16", "meta article:published_time")
        self.assertNotIn("CABECALHO_DO_BOLETIM", r["fact_time_basis"])

    def test_periodo_depois_da_publicacao_e_futuro(self):
        t = "Bollettino n. 5\ndal 22 al 28 settembre 2026\nLe previsioni indicano tempo stabile su tutta la regione."
        self.assertEqual(FT.NAO_SEI, FT.campos_do_fato(t, "2026-09-16", "meta")["fact_time"])

    def test_dal_al_normaliza_para_o_leitor_do_periodo(self):
        t = "Bollettino agrometeorologico n. 12\ndal 9 al 15 settembre 2026\nSituazione generale della regione."
        r = FT.campos_do_fato(t)
        self.assertEqual("09 - 15 settembre 2026", r["fact_time"])
        self.assertIn("dal 9 al 15 settembre 2026", r["fact_time_basis"])

    def test_sem_marca_de_boletim_o_periodo_solto_nao_entra(self):
        t = "Notizie dal mondo agricolo\n09 - 15 settembre 2026\nLa settimana della frutta a Milano con degustazioni."
        self.assertNotIn("CABECALHO_DO_BOLETIM", FT.campos_do_fato(t)["fact_time_basis"])

    def test_data_de_campo_presa_ao_acontecimento_vence_o_cabecalho(self):
        t = ARIF + "Le catture del 12 settembre 2026 hanno colpito gli oliveti della zona di Otranto.\n"
        # publicado a 16: o dia 12 ja passou (com publicacao a 9, o dia 12 seria futuro e nao entraria)
        self.assertEqual("12 settembre 2026", FT.campos_do_fato(t, "2026-09-16", "meta")["fact_time"])


class OAnoDeComparacao(unittest.TestCase):

    def test_ano_de_comparacao_nao_e_data_do_facto(self):
        for t in ("I prezzi delle mele sono in calo rispetto al 2025 secondo la campagna di rilevazione nella Val di Non.",
                  "Il raccolto delle pere e in calo rispetto allo stesso periodo del 2025 secondo la campagna nazionale."):
            with self.subTest(t=t[:30]):
                self.assertNotEqual("2025", FT.campos_do_fato(t)["fact_time"])
        t = "La campagna 2026 registra prezzi in calo del 12% rispetto al 2025 per le mele della Val di Non."
        self.assertEqual("campagna 2026", FT.campos_do_fato(t)["fact_time"])

    def test_a_campanha_de_comparacao_que_vem_primeiro_nao_vence(self):
        # sem a guarda sairia «campagna 2025»; «quest'anno» nao diz o ano: NAO SEI e a resposta certa
        t = "Rispetto alla campagna 2025, la raccolta di quest'anno e stata colpita dalla grandine nei frutteti."
        r = FT.campos_do_fato(t)
        self.assertEqual(FT.NAO_SEI, r["fact_time"])
        self.assertIn("COMPARACAO_NAO_E_FATO", r["fact_time_basis"])


class OMesmoProblemaContaUmaVez(unittest.TestCase):
    """EXTRATORES-V2-JUNTOS: medido na D84 — no boletim de Salerno (IT-T3-002, Sala) a chave PROBLEMA tinha
    «afide» e «afidi», «cimice» e «cimici», «tripidi», «nottue», «bactrocera oleae» e «ceratitis capitata»
    ao lado do nome comum: 25 nomes para menos problemas."""

    def test_afide_e_afidi_sao_um(self):
        b = BC.ler_boletim("PESCO\nAfidi: presenti colonie sui germogli.\nAfide verde: nessuna segnalazione.")
        self.assertEqual(["afide"], b["PROBLEMAS"])
        formas = [p["FORMA"] for s in b["SECOES"] for p in s["PROBLEMAS"]]
        self.assertEqual(["afidi", "afide"], formas)            # a forma do texto fica guardada

    def test_real_salerno_nome_cientifico_entre_parenteses_e_o_mesmo(self):
        b = BC.ler_boletim(SALERNO)
        self.assertIn("cimice asiatica", b["PROBLEMAS"])
        self.assertNotIn("halyomorpha halys", b["PROBLEMAS"])
        self.assertIn("mosca della frutta", b["PROBLEMAS"])
        self.assertNotIn("ceratitis capitata", b["PROBLEMAS"])
        self.assertEqual(["mosca della frutta"], b["PROBLEMAS_NAO_AUSENTES"])

    def test_real_arif_mosca_e_bactrocera_sao_uma(self):
        b = BC.ler_boletim(ARIF)
        self.assertEqual(["mosca dell'olivo"], b["PROBLEMAS"])

    def test_real_it_t3_010_mosca_delle_olive_e_praga_nao_cabecalho(self):
        b = BC.ler_boletim("MOSCA DELLE OLIVE\nSi registrano catture in aumento nelle trappole.")
        self.assertEqual(["mosca dell'olivo"], b["PROBLEMAS"])
        self.assertEqual(["olivo"], b["CULTURAS"])              # a cultura vem do nome da praga

    def test_a_linha_toda_segue_a_cultura_do_nome_tambem_sem_sinonimo(self):
        # a cocciniglia nao tem a cultura no nome: vai para a vite porque esta na linha da tignoletta
        b = BC.ler_boletim("OLIVO\nTignoletta della vite: presenti anche cocciniglie sui grappoli.")
        sec = {s["CULTURA"]: [p["NOME"] for p in s["PROBLEMAS"]] for s in b["SECOES"]}
        self.assertIn("cocciniglia", sec["vite"])
        self.assertNotIn("cocciniglia", sec.get("olivo", []))

    def test_o_que_nao_esta_na_lista_fica_como_o_texto_escreve(self):
        self.assertEqual("cocciniglia", BC.nome_do_problema("cocciniglia"))
        self.assertEqual("cimice", BC.nome_do_problema("cimici"))
        self.assertEqual("cimice asiatica", BC.nome_do_problema("cimice asiatica"))   # nao vira «cimice»
        self.assertEqual("tignola", BC.nome_do_problema("tignole"))
        self.assertEqual("tignoletta della vite", BC.nome_do_problema("lobesia botrana"))


class APortaLevaAsChavesDoBoletim(unittest.TestCase):

    def _janela(self, texto, universo):
        import admissao as A
        item = {"id": "derived:1", "texto": texto, "source_id": "IT-T3-002", "fact_location": "NAO SEI",
                "fact_time": "NAO SEI"}
        d = A.decidir(item, universo, corrida="RUN-TESTE")
        return A.janela_para_o_ready(item, d)

    def test_t3_cultura_fase_e_problema(self):
        j = self._janela(SALERNO, "T3")
        self.assertEqual(["actinidia", "agrumi"], j["CULTURA"]["VALOR"])
        self.assertIn("boletim", j["CULTURA"]["BASE"])
        self.assertEqual(["ingrossamento frutto", "ripresa vegetativa"], j["FASE"]["VALOR"])
        self.assertEqual(["mosca della frutta"], [p for p in j["PROBLEMA"]["VALOR"] if p.startswith("mosca")])
        self.assertIn("cimice asiatica", j["PROBLEMA"]["AUSENTES"])
        self.assertNotIn("cimice asiatica", j["PROBLEMA"]["VALOR"])     # ausente nunca e valor
        pares = {s["CULTURA"]: [p["NOME"] for p in s["PROBLEMAS"]] for s in j["PROBLEMA"]["SECOES"]}
        self.assertIn("mosca della frutta", pares["agrumi"])
        # a porta leva tambem a FORMA como o boletim a escreve (o NOME e o da lista MESMO_PROBLEMA)
        formas = {p["NOME"]: p.get("FORMA") for s in j["PROBLEMA"]["SECOES"] for p in s["PROBLEMAS"]}
        self.assertEqual("mosca della frutta", formas["mosca della frutta"])
        self.assertEqual("cimice asiatica", formas["cimice asiatica"])

    def test_fora_de_t2_t3_nao_le_o_boletim(self):
        j = self._janela(SALERNO, "T10")
        self.assertEqual("NAO SEI", j["PROBLEMA"]["VALOR"])
        self.assertNotIn("boletim", str(j["CULTURA"]["BASE"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
