#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CANARIO-1149 (D129) — o primeiro vermelho de derived:1149 (CREA, T5), com o texto REAL da Sala.

    python3 -m unittest tests.test_canario_1149 -v

Tres NAO SEI com o texto a dize-los, e a causa de cada um (CANARIO-1149.md):
  C · CORPO       a pagina chegou ACHATADA numa linha so; o rodape casava RODAPE e a linha INTEIRA saia
  P · PUBLICACAO  a data so se lia em metadado HTML; «COMUNICATO STAMPA remove 22 giu 2026» era texto
  L · LUGAR       «Salento» nao estava em vocabulario nenhum, «nelle aree colpite del» nao era preposicao de
                  lugar, e «selezionato» nao era verbo de estudo
  N · PROBLEMA    «nematodi parassiti della sputacchina» (agente de controlo) contava como segunda praga
e os casos que TEM de continuar a reprovar: data de menu/rodape, duas datas, nematoide-praga de verdade,
lugar sem verbo de estudo, e o Salento que nao vira Puglia.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import admissao as adm  # noqa: E402
import afirmacao_da_fonte as AF  # noqa: E402
import boletim_do_campo as BC  # noqa: E402
import estudo_chaves as EC  # noqa: E402
import executor_texto_de_html as H  # noqa: E402
import fato_do_texto as FT  # noqa: E402

INSUMOS = os.path.join(RAIZ, "docs", "lab-insumos", "canario-1149")
with open(os.path.join(INSUMOS, "LINHA-DA-SALA.json"), encoding="utf-8") as _fh:
    LINHA = json.load(_fh)
TEXTO = LINHA["texto"]


class C_CorpoDaPaginaAchatada(unittest.TestCase):
    def test_C1_o_texto_real_e_uma_linha_so_e_tem_corpo(self):
        self.assertEqual(len(TEXTO.splitlines()), 1)
        c = FT.corpo(TEXTO)
        self.assertIn("nelle aree colpite del Salento", c)
        self.assertIn("ospitato dal CIHEAM Bari", c)

    def test_C2_o_rodape_continua_fora(self):
        c = FT.corpo(TEXTO)
        self.assertNotIn("Partita IVA", c)
        self.assertNotIn("Via della Navicella", c)

    def test_C3_linha_curta_com_rodape_continua_a_sair_inteira(self):
        linha = ("La peronospora e stata osservata nei vigneti della zona questa settimana "
                 "e per informazioni tel 06 1234567 scrivere alla redazione.")
        self.assertLess(FT._palavras(linha), FT.LINHA_ACHATADA)
        self.assertEqual(FT.corpo("Titolo della pagina qui\n" + linha).count("peronospora"), 0)

    def test_C4_o_porque_do_lugar_deixa_de_dizer_sem_corpo(self):
        r = FT.campos_do_fato(TEXTO)
        self.assertNotIn("não tem corpo", r["fact_location_basis"])


class P_PublicacaoNoTexto(unittest.TestCase):
    def test_P1_texto_real_da_2026_06_22_com_o_trecho(self):
        r = H.publicacao_no_texto(TEXTO)
        self.assertEqual(r["VALOR"], "2026-06-22")
        self.assertEqual(r["PRECISAO"], "DIA")
        self.assertIn("COMUNICATO STAMPA remove 22 giu 2026", r["BASE"])

    def test_P2_menu_e_rodape_nao_contam(self):
        t = ("Notizie Comunicati Stampa Rassegna Stampa Eventi Save the date 12 marzo 2026 "
             "Risorse correlate 3 aprile 2026 © 2026 CREA")
        self.assertEqual(H.publicacao_no_texto(t)["VALOR"], "NAO SEI")
        # a SECCAO no plural, numa listagem, seguida da data de OUTRO comunicado
        self.assertEqual(H.publicacao_no_texto("Comunicati Stampa 5 maggio 2026 Altro titolo")["VALOR"], "NAO SEI")

    def test_P3_duas_datas_diferentes_sao_ambiguas(self):
        t = "COMUNICATO STAMPA 22 giu 2026 bla bla NEWS 3 luglio 2026"
        r = H.publicacao_no_texto(t)
        self.assertEqual(r["VALOR"], "NAO SEI")
        self.assertIn("AMBIGUO", r["PORQUE"])

    def test_P4_data_impossivel_nao_conta(self):
        self.assertEqual(H.publicacao_no_texto("COMUNICATO STAMPA 31 feb 2026")["VALOR"], "NAO SEI")

    def test_P5_pubblicato_il_numerico(self):
        self.assertEqual(H.publicacao_no_texto("Pubblicato il 03/07/2026 Notizia")["VALOR"], "2026-07-03")

    def test_P6_o_metadado_da_pagina_continua_a_ganhar(self):
        html = ('<html><head><script type="application/ld+json">{"@type":"NewsArticle",'
                '"datePublished":"2026-06-20"}</script></head><body>COMUNICATO STAMPA 22 giu 2026</body></html>')
        r = H.tempo_de_publicacao_com_texto(html.encode("utf-8"))
        self.assertEqual(r["VALOR"], "2026-06-20")
        self.assertEqual(r["BASE"], H.BASE_JSON_LD)

    def test_P7_sem_metadado_o_texto_da_pagina_responde(self):
        html = "<html><body><p>COMUNICATO STAMPA</p><p>22 giu 2026</p><p>Testo.</p></body></html>"
        r = H.tempo_de_publicacao_com_texto(html.encode("utf-8"))
        self.assertEqual(r["VALOR"], "2026-06-22")

    def test_P8_publicacao_nunca_vira_fact_time(self):
        r = FT.campos_do_fato(TEXTO, "2026-06-22", H.BASE_TEXTO)
        self.assertEqual(r["fact_time"], "NAO SEI")


class L_LugarDoEstudo(unittest.TestCase):
    def test_L1_texto_real_da_salento_zona_local_do_estudo(self):
        r = EC.chaves_do_estudo(TEXTO)["REGIAO_DO_FATO"]
        self.assertEqual(r["VALOR"], ["Salento"])
        self.assertEqual(r["PRECISAO"], ["ZONA"])
        self.assertEqual(r["KIND"], "LOCAL_DO_ESTUDO")
        self.assertIn("nelle aree colpite del Salento", r["BASE"])

    def test_L2_salento_nao_vira_puglia(self):
        r = EC.chaves_do_estudo(TEXTO)["REGIAO_DO_FATO"]
        self.assertNotIn("Puglia", r["VALOR"])

    def test_L3_sem_verbo_de_estudo_nao_conta(self):
        r = EC.chaves_do_estudo("La Xylella e diffusa nelle aree colpite del Salento. Fine.")["REGIAO_DO_FATO"]
        self.assertEqual(r["VALOR"], "NAO SEI")

    def test_L4_bari_do_nome_da_instituicao_continua_recusado(self):
        r = EC.chaves_do_estudo(TEXTO)["REGIAO_DO_FATO"]
        self.assertIn("Bari", [x["VALOR"] for x in r["RECUSADOS"]])


class N_ProblemaEAgenteDeControle(unittest.TestCase):
    def test_N1_texto_real_da_xylella_e_o_nematoide_como_agente(self):
        p = adm.problema_da_chave({"texto": TEXTO}, "T5")
        self.assertEqual(p["VALOR"], "xylella")
        self.assertEqual([a["NOME"] for a in p["AGENTES_DE_CONTROLE"]], ["nematode"])
        self.assertIn("nematodi parassiti della sputacchina", p["AGENTES_DE_CONTROLE"][0]["BASE"])
        self.assertEqual(AF.problema_conforme(p, TEXTO), (True, "conforme PROBLEMA/v1"))

    def test_N2_pagina_achatada_nao_e_titulo_nem_base_inteira(self):
        p = adm.problema_da_chave({"texto": TEXTO}, "T5")
        self.assertEqual(p["VEIO_DE"], "TEXT")
        self.assertLess(len(p["BASE"]), 300)

    def _problema(self, t):
        return adm.problema_da_chave({"texto": t}, "T5")

    def test_N3_nematoide_praga_de_verdade_continua_problema(self):
        p = self._problema("Attacchi di nematodi galligeni su pomodoro in serra: prove condotte in Sicilia.")
        self.assertEqual(p["VALOR"], "nematode")
        self.assertEqual(p["AGENTES_DE_CONTROLE"], [])

    def test_N4_parassiti_delle_piante_continua_problema(self):
        for t in ("I nematodi parassiti delle piante causano perdite nel pomodoro.",
                  "I nematodi parassiti dell'olivo sono stati campionati in Puglia."):
            self.assertEqual(self._problema(t)["VALOR"], "nematode", t)

    def test_N5_agente_contra_uma_praga_do_vocabulario(self):
        p = self._problema("Un virus per il controllo degli afidi e stato provato su melo.")
        self.assertEqual(p["VALOR"], "afide")
        self.assertEqual([a["NOME"] for a in p["AGENTES_DE_CONTROLE"]], ["virus"])

    def test_N6_titulo_com_dois_pontos_nao_vira_agente(self):
        p = self._problema("Peronospora: strategie per il controllo della peronospora nella vite.")
        self.assertEqual(p["VALOR"], "peronospora")
        self.assertEqual(p["AGENTES_DE_CONTROLE"], [])

    def test_N7_regra_geral_no_boletim(self):
        t = "OLIVO\nPresenza di nematodi parassiti della sputacchina e di mosca dell'olivo nelle trappole."
        p = BC.problema_do_boletim(t)
        self.assertEqual(p["VALOR"], "mosca dell'olivo")


class R_OItemInteiroPelaEstradaDoReprocesso(unittest.TestCase):
    """A estrada de `admissao/reprocessar_um_item.py` sobre a linha exportada — sem banco."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(RAIZ, "admissao"))
        import reprocessar_um_item as R1
        cls.R1 = R1
        cls.r = R1.reprocessar([LINHA], "derived:1149")

    def test_R1_resumo_do_item(self):
        s = self.r["RESUMO"]
        self.assertEqual(s["PUBLISHED_AT"], ["NAO SEI", "2026-06-22"])
        self.assertEqual(s["FACT_TIME"], ["NAO SEI", "NAO SEI"])
        self.assertEqual(s["PROBLEMA"], "xylella")
        self.assertEqual(s["REGIAO_DO_FATO"], ["Salento"])

    def test_R2_so_campos_revisiveis_e_nunca_os_do_livro(self):
        campos = [r["CAMPO"] for r in self.r["REVISOES"]]
        self.assertEqual(campos, ["published_at", "fact_location", "completude_tempo_lugar",
                                  "tempo_lugar_evidencia", "janela_declarada"])
        self.assertFalse(self.r["GRAVOU_NO_BANCO"])

    def test_R3_so_um_item(self):
        with self.assertRaises(SystemExit):
            self.R1.reprocessar([LINHA, LINHA], "derived:1149")
        with self.assertRaises(SystemExit):
            self.R1.reprocessar([LINHA], "derived:9999")

    def test_R4_aplicar_recusa_sem_parar_flag_e_sem_prova_vale(self):
        with self.assertRaises(SystemExit):
            self.R1.aplicar(self.r, {"PROVA_VALE": True, "DUMP": __file__}, espera=object(),
                            parar=os.path.join(RAIZ, "nao-existe-PARAR.flag"))
        with self.assertRaises(SystemExit):
            self.R1.aplicar(self.r, {"PROVA_VALE": False, "DUMP": __file__}, espera=object(), parar=__file__)

    def test_R5_aplicar_recusa_texto_diferente(self):
        class Espera:
            def exigir_canonica(self):
                return {}

            def ler_atual(self, run_id):
                return {"ITENS": [{"ORDEM": LINHA["ordem"], "ITEM_ID": "derived:1149", "TEXTO": "outro"}]}

            def rever(self, *a, **k):
                raise AssertionError("nao podia escrever")
        with self.assertRaises(SystemExit):
            self.R1.aplicar(self.r, {"PROVA_VALE": True, "DUMP": __file__}, espera=Espera(), parar=__file__)

    def test_R6_aplicar_escreve_so_pela_porta_rever(self):
        chamadas = []

        class Espera:
            def exigir_canonica(self):
                return {}

            def ler_atual(self, run_id):
                return {"ITENS": [{"ORDEM": LINHA["ordem"], "ITEM_ID": "derived:1149", "TEXTO": TEXTO}]}

            def rever(self, run_id, ordem, revisoes, extrator, versao, motivo):
                chamadas.append((run_id, ordem, [r["CAMPO"] for r in revisoes]))
                return {"INSERIDAS": len(revisoes), "JA_ERAM_ASSIM": 0}
        rec = self.R1.aplicar(self.r, {"PROVA_VALE": True, "DUMP": __file__}, espera=Espera(), parar=__file__)
        self.assertEqual(rec["INSERIDAS"], 5)
        self.assertEqual(chamadas[0][:2], (LINHA["run_id"], LINHA["ordem"]))


if __name__ == "__main__":
    unittest.main()
