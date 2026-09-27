#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOLETIM-POR-SECAO · D18/D19 (Intelligence R6) + D112 do dono.

D18: cultura/praga/lugar saiam POR DOCUMENTO e nao pela SECAO do boletim. D19: cultura/regiao saiam da
manchete VIZINHA (barra lateral). Estes testes rodam o extrator canonico (`leis/boletim_do_campo.py`) sobre:
  · os 10 casos do GOLD-FIXTURE-PUGLIA-V1 (trechos curtos de boletins oficiais PUBLICOS + ESPERADO do dono);
  · o boletim A.P.OL. real que ja esta no repo (data/derivados/texto/RAW-59da05274359eff6.txt, n.9);
  · textos SINTETICOS (marcados SINTETICA) para as regras que o gold nao cobre sozinho.
Sem rede, sem banco."""
from __future__ import annotations

import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ("", "leis", "admissao", os.path.join("scripts", "lugar_fato")):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)
import _gavetas  # noqa: E402,F401
import boletim_do_campo as BC  # noqa: E402
import fato_do_texto as FT  # noqa: E402
import gold_puglia as G  # noqa: E402

APOL_N9 = os.path.join(RAIZ, "data", "derivados", "texto", "RAW-59da05274359eff6.txt")


def _gold():
    return json.loads(G.GOLD.read_text(encoding="utf-8"))


def _ler_ficha(caso, sid):
    c = next(x for x in _gold()["CASOS"] if x["CASO"] == caso)
    f = next(x for x in c["FICHAS"] if x["ASSERTION_ID"] == sid)
    d = G.montar(f, BC)
    return BC.ler_afirmacao(d["TEXTO"], d["INICIO"], d["FIM"], titulo=d["TITULO"], cabecalhos_visuais=d["VISUAIS"])


class OGoldDaPuglia(unittest.TestCase):
    """O ESPERADO do dono nao se edita: onde falhar, conserta-se o codigo."""

    @classmethod
    def setUpClass(cls):
        cls.r = G.correr(BC)

    def test_gold_nenhuma_chave_do_extrator_falha(self):
        falhas = {c["CASO"]: {k: v for k, v in c["CHAVES"].items() if v["VEREDITO"] == "FAIL"}
                  for c in self.r["CASOS"] if c["VEREDITO"] == "FAIL"}
        self.assertEqual({}, falhas)

    def test_gold_o_placar_nao_encolhe(self):
        # o numero de chaves MEDIDAS e fixo: um harness que medisse menos passaria com menos prova
        p = self.r["PLACAR"]
        self.assertEqual((9, 0, 1), (p["CASOS_PASS"], p["CASOS_FAIL"], p["CASOS_NAO_MEDIDOS"]))
        self.assertEqual((34, 0, 2, 20), (p["CHAVES_PASS"], p["CHAVES_FAIL"], p["CHAVES_NAO_MEDIDAS"],
                                          p["CHAVES_FORA_DESTE_EXTRATOR"]))

    def test_gold_o_esperado_e_o_do_dono(self):
        g = _gold()
        self.assertEqual(("PUGLIA-HUMANA-V1", "0aee57f6fe33c2da", 10), (g["GOLD_SET"], g["VERSAO"], len(g["CASOS"])))

    def test_gold_c01_cabecalho_so_na_imagem_nunca_vira_fact_location(self):
        a = _ler_ficha("C01", "SA-01")
        self.assertEqual("UNRESOLVED", a["FACT_LOCATION"]["VALOR"])
        self.assertEqual("VISUAL_HEADER_CANDIDATE", a["FACT_LOCATION"]["LOCATION_SOURCE"])
        self.assertEqual("FITOPATOLOGIA BARI E BAT", a["FACT_LOCATION"]["CANDIDATO_VISUAL"]["ROTULO_NA_IMAGEM"])
        self.assertFalse(a["FACT_LOCATION"]["PONTO_NO_MAPA"])
        self.assertEqual(("SPAN", ["olivo"]), (a["CULTURA"]["ENTITY_SOURCE"], a["CULTURA"]["VALOR"]))

    def test_gold_c02_cabecalho_da_secao_no_texto_e_praga_do_titulo(self):
        a = _ler_ficha("C02", "SA-18")
        self.assertEqual(("Collina Litoranea (BR)", "SECTION_HEADER"),
                         (a["FACT_LOCATION"]["VALOR"], a["FACT_LOCATION"]["LOCATION_SOURCE"]))
        self.assertEqual(("DOCUMENT_TITLE", ["mosca dell'olivo"]), (a["PRAGAS"]["ENTITY_SOURCE"], a["PRAGAS"]["VALOR"]))

    def test_gold_c04_troca_de_secao_entre_o_nome_e_o_trecho_e_unknown(self):
        a = _ler_ficha("C04", "SA-06")
        self.assertEqual("UNKNOWN", a["PRAGAS"]["VALOR"])
        self.assertIn("troca de secao", a["PRAGAS"]["MOTIVO"])
        self.assertEqual(("zona costiera del Gargano", "TEXT"),
                         (a["FACT_LOCATION"]["VALOR"], a["FACT_LOCATION"]["LOCATION_SOURCE"]))

    def test_gold_c05_as_duas_pragas_do_trecho_nenhuma_a_menos(self):
        a = _ler_ficha("C05", "SA-12")
        self.assertEqual(["mosca dell'olivo", "margaronia"], a["PRAGAS"]["VALOR"])
        self.assertEqual("SPAN", a["PRAGAS"]["ENTITY_SOURCE"])
        # «TERRITORIO ESCLUSO GARGANO» esta no texto e NAO nomeia a provincia
        self.assertEqual(("UNRESOLVED", "VISUAL_HEADER_CANDIDATE"),
                         (a["FACT_LOCATION"]["VALOR"], a["FACT_LOCATION"]["LOCATION_SOURCE"]))

    def test_gold_c08_expressao_de_lugar_sem_nome_nao_vira_ponto(self):
        a = _ler_ficha("C08", "SA-24")
        self.assertEqual("zone irrigue costiere di tutti comprensori", a["FACT_LOCATION"]["LOCATION_EXPRESSION_RAW"])
        self.assertEqual(("UNRESOLVED", "TEXT", False), (a["FACT_LOCATION"]["VALOR"],
                                                        a["FACT_LOCATION"]["LOCATION_SOURCE"],
                                                        a["FACT_LOCATION"]["PONTO_NO_MAPA"]))

    def test_gold_c09_paragrafo_e_titulo_da_secao(self):
        self.assertEqual("PARAGRAPH_CONTEXT", _ler_ficha("C09", "SA-03")["PRAGAS"]["ENTITY_SOURCE"])
        self.assertEqual("SECTION_TITLE", _ler_ficha("C09", "SA-32")["PRAGAS"]["ENTITY_SOURCE"])


class OBoletimRealDaAPOL(unittest.TestCase):
    """O A.P.OL. n.9 real (07-13/09): tres comprensori, o mesmo paragrafo em cada um."""

    @classmethod
    def setUpClass(cls):
        with open(APOL_N9, encoding="utf-8") as f:
            cls.t = f.read()

    def test_real_mesma_frase_em_tres_secoes_e_tres_aplicacoes_uma_instituicao(self):
        ap = BC.aplicacoes_territoriais(self.t, "non si sono rilevate raggiungimenti o superamenti della soglia di "
                                                "intervento con pochissime punture fertili", publicador="A.P.OL.")
        self.assertEqual(3, ap["APLICACOES_TERRITORIAIS"])
        self.assertEqual(1, ap["INSTITUICOES_INDEPENDENTES"])
        self.assertEqual(["Collina Litoranea (BR)", "Pianura Salentina Nord (LE)", "Pianura Salentina Sud (LE)"],
                         ap["TERRITORIOS"])

    def test_real_cabecalho_partido_em_duas_linhas(self):
        self.assertIn("Pianura Salentina Sud (LE)", [s["VALOR"] for s in BC.secoes_territoriais(self.t)])

    def test_real_o_rodape_fecha_a_secao_o_anexo_nao_herda_comprensorio(self):
        i = self.t.find("CRITERI D")
        self.assertGreater(i, 0)
        self.assertIsNone(BC.ler_afirmacao(self.t, i, i + 10)["SECAO"])

    def test_real_ler_boletim_diz_os_territorios(self):
        self.assertEqual(3, len(BC.ler_boletim(self.t)["TERRITORIOS"]))


# SINTETICA — dois territorios, duas pragas, no MESMO documento
SINTETICA_DUAS_SECOES = """BOLLETTINO SINTETICO DI PROVA
COMPRENSORIO - AA - ZONA NORD
Catture di mosca dell'olivo in aumento nelle trappole.
Si consiglia di intervenire al superamento della soglia.

COMPRENSORIO - BB - ZONA SUD
Presenza di margaronia sui germogli.
Si consiglia di intervenire al superamento della soglia.
"""


class ASecaoDaAfirmacao(unittest.TestCase):
    """SINTETICA: cada afirmacao herda da SUA secao; nunca do documento."""

    def _ler(self, texto, trecho, n=0, **kw):
        return BC.afirmacoes_do_trecho(texto, trecho, **kw)[n]

    def test_sintetica_cada_secao_da_a_sua_praga_e_o_seu_lugar(self):
        a = self._ler(SINTETICA_DUAS_SECOES, "Si consiglia di intervenire al superamento della soglia.", 0)
        b = self._ler(SINTETICA_DUAS_SECOES, "Si consiglia di intervenire al superamento della soglia.", 1)
        self.assertEqual((["mosca dell'olivo"], "PARAGRAPH_CONTEXT"), (a["PRAGAS"]["VALOR"], a["PRAGAS"]["ENTITY_SOURCE"]))
        self.assertEqual((["margaronia"], "PARAGRAPH_CONTEXT"), (b["PRAGAS"]["VALOR"], b["PRAGAS"]["ENTITY_SOURCE"]))
        self.assertEqual(("Zona Nord (AA)", "SECTION_HEADER"), (a["FACT_LOCATION"]["VALOR"], a["FACT_LOCATION"]["LOCATION_SOURCE"]))
        self.assertEqual(("Zona Sud (BB)", "SECTION_HEADER"), (b["FACT_LOCATION"]["VALOR"], b["FACT_LOCATION"]["LOCATION_SOURCE"]))

    def test_sintetica_nome_do_outro_lado_do_cabecalho_nao_passa(self):
        t = "COMPRENSORIO - AA - ZONA NORD\nCatture di margaronia.\nCOMPRENSORIO - BB - ZONA SUD\nSoglia superata."
        a = self._ler(t, "Soglia superata.")
        self.assertEqual("UNKNOWN", a["PRAGAS"]["VALOR"])
        self.assertEqual("Zona Sud (BB)", a["FACT_LOCATION"]["VALOR"])

    def test_sintetica_rotulo_corta_o_paragrafo(self):
        t = "Situazione Fitosanitaria: presenza di rogna. Programma di Difesa: intervenire alla soglia."
        a = self._ler(t, "intervenire alla soglia.")
        self.assertEqual("UNKNOWN", a["PRAGAS"]["ENTITY_SOURCE"])
        self.assertIn("troca de secao", a["PRAGAS"]["MOTIVO"])

    def test_sintetica_duas_pragas_no_paragrafo_e_unknown(self):
        t = "Catture di mosca dell'olivo e di margaronia nelle trappole. Intervenire alla soglia."
        a = self._ler(t, "Intervenire alla soglia.")
        self.assertEqual(("UNKNOWN", "UNKNOWN"), (a["PRAGAS"]["VALOR"], a["PRAGAS"]["ENTITY_SOURCE"]))

    def test_sintetica_titulo_diz_uma_praga_paragrafo_outra_e_concorrente(self):
        t = "Presenza di margaronia sui germogli. Intervenire alla soglia."
        a = self._ler(t, "Intervenire alla soglia.", titulo="MOSCA DELLE OLIVE")
        self.assertEqual("UNKNOWN", a["PRAGAS"]["VALOR"])
        self.assertIn("concorrente", a["PRAGAS"]["MOTIVO"])

    def test_sintetica_frase_de_duas_frases_atras_nao_e_paragrafo(self):
        t = "Presenza di margaronia. Tempo stabile e caldo. Intervenire alla soglia."
        self.assertEqual("UNKNOWN", self._ler(t, "Intervenire alla soglia.")["PRAGAS"]["VALOR"])

    def test_sintetica_titulo_repetido_no_topo_de_cada_pagina_e_do_documento(self):
        t = "MOSCA DELLE OLIVE\nCOMPRENSORIO - AA - ZONA NORD\nSoglia non superata.\n\fMOSCA DELLE OLIVE\n"
        a = self._ler(t, "Soglia non superata.")
        self.assertEqual(("DOCUMENT_TITLE", ["mosca dell'olivo"]), (a["PRAGAS"]["ENTITY_SOURCE"], a["PRAGAS"]["VALOR"]))

    def test_sintetica_cabecalho_visual_nunca_e_fact_location_mesmo_com_entidade(self):
        v = [{"ROTULO": "FITOPATOLOGIA LECCE", "PAGINA": 3, "ENTIDADE": "PLACE:PROV-LE"}]
        a = self._ler("Presenza di rogna diffusa.", "Presenza di rogna diffusa.", cabecalhos_visuais=v)
        self.assertEqual(("UNRESOLVED", "VISUAL_HEADER_CANDIDATE", False),
                         (a["FACT_LOCATION"]["VALOR"], a["FACT_LOCATION"]["LOCATION_SOURCE"],
                          a["FACT_LOCATION"]["PONTO_NO_MAPA"]))

    def test_sintetica_cabecalho_de_exclusao_no_texto_nao_resolve(self):
        a = self._ler("TERRITORIO ESCLUSO COSTA\nPresenza di rogna.", "Presenza di rogna.")
        self.assertEqual(("UNRESOLVED", "UNRESOLVED"), (a["FACT_LOCATION"]["VALOR"], a["FACT_LOCATION"]["LOCATION_SOURCE"]))

    def test_sintetica_lugar_escrito_no_trecho_vence_o_cabecalho(self):
        t = "COMPRENSORIO - AA - ZONA NORD\nCatture elevate in provincia di Lecce."
        a = self._ler(t, "Catture elevate in provincia di Lecce.")
        self.assertEqual(("Lecce", "TEXT"), (a["FACT_LOCATION"]["VALOR"], a["FACT_LOCATION"]["LOCATION_SOURCE"]))

    def test_sintetica_titulo_da_secao_vence_o_titulo_do_documento(self):
        t = "CONSIGLI DI DIFESA\n• Margaronia (Palpita unionalis) Monitorare i germogli. Soglia: 10% di germogli colpiti."
        a = self._ler(t, "Soglia: 10% di germogli colpiti.", titulo="MOSCA DELLE OLIVE")
        self.assertEqual(("SECTION_TITLE", ["margaronia"]), (a["PRAGAS"]["ENTITY_SOURCE"], a["PRAGAS"]["VALOR"]))

    def test_sintetica_praga_no_trecho_vence_o_titulo(self):
        a = self._ler("Presenza di margaronia sui germogli.", "Presenza di margaronia sui germogli.",
                      titulo="MOSCA DELLE OLIVE")
        self.assertEqual(("SPAN", ["margaronia"]), (a["PRAGAS"]["ENTITY_SOURCE"], a["PRAGAS"]["VALOR"]))

    def test_sintetica_manchete_vizinha_nao_e_contexto_da_afirmacao(self):
        t = "Ultime notizie\nNocciolo, Xylella in Basilicata\nSegnalare i sintomi ai tecnici."
        a = self._ler(t, "Segnalare i sintomi ai tecnici.")
        self.assertEqual("UNKNOWN", a["CULTURA"]["VALOR"])
        self.assertEqual("UNKNOWN", a["PRAGAS"]["VALOR"])

    def test_as_fontes_sao_do_vocabulario_declarado(self):
        a = self._ler(SINTETICA_DUAS_SECOES, "Presenza di margaronia sui germogli.")
        self.assertIn(a["PRAGAS"]["ENTITY_SOURCE"], BC.ENTITY_SOURCES)
        self.assertIn(a["CULTURA"]["ENTITY_SOURCE"], BC.ENTITY_SOURCES)
        self.assertIn(a["FACT_LOCATION"]["LOCATION_SOURCE"], BC.LOCATION_SOURCES)


# SINTETICA — D19: a noticia fala de AMENDOEIRA em MATERA; a barra lateral fala de NOCCIOLO na BASILICATA
SINTETICA_XYLELLA = """Home | Notizie | Agricoltura | Meteo | Contatti
Xylella, nuovi focolai su mandorlo nel Materano
Il Servizio fitosanitario regionale ha confermato la presenza di Xylella fastidiosa su piante di mandorlo in agro di Matera, dopo le analisi sui campioni prelevati dagli ispettori.
Gli agricoltori della zona sono invitati a segnalare disseccamenti sospetti ai tecnici del servizio regionale.
Ultime notizie
Xylella, primi sintomi sul nocciolo in Basilicata: scatta il monitoraggio straordinario
Prezzi del grano duro in calo sulla piazza di Foggia questa settimana
Redazione - Via Roma 10, 75100 Matera - Tel 0835 000000
"""
FRASE_DA_NOTICIA = ("Il Servizio fitosanitario regionale ha confermato la presenza di Xylella fastidiosa su piante di "
                    "mandorlo in agro di Matera")


class ABarraLateralSaiAntes(unittest.TestCase):
    """D19 (SINTETICA): manchete vizinha nao da cultura nem regiao a noticia."""

    def test_sintetica_xylella_lugar_do_fato_nao_vem_da_manchete_vizinha(self):
        r = FT.campos_do_fato(SINTETICA_XYLELLA)
        self.assertNotIn("Basilicata", r["fact_location"])
        self.assertIn("Matera", r["fact_location"])

    def test_sintetica_xylella_cultura_da_chave_nao_e_nocciolo(self):
        import admissao as A
        r = FT.campos_do_fato(SINTETICA_XYLELLA)
        culturas, _ = A._cultura_fora_da_regua({"texto": SINTETICA_XYLELLA,
                                                "fact_location_basis": r["fact_location_basis"]})
        self.assertNotIn("nocciolo", culturas)

    def test_sintetica_xylella_a_afirmacao_da_noticia(self):
        a = BC.afirmacoes_do_trecho(SINTETICA_XYLELLA, FRASE_DA_NOTICIA)[0]
        self.assertEqual((["xylella"], "SPAN"), (a["PRAGAS"]["VALOR"], a["PRAGAS"]["ENTITY_SOURCE"]))
        self.assertEqual((["mandorlo"], "SPAN"), (a["CULTURA"]["VALOR"], a["CULTURA"]["ENTITY_SOURCE"]))
        self.assertEqual(("Matera", "TEXT"), (a["FACT_LOCATION"]["VALOR"], a["FACT_LOCATION"]["LOCATION_SOURCE"]))

    def test_sintetica_xylella_ler_boletim_nao_ve_o_nocciolo(self):
        self.assertNotIn("nocciolo", BC.ler_boletim(SINTETICA_XYLELLA)["CULTURAS"])
        # manchete vizinha CURTA: sem a barra lateral fora, «Nocciolo in Basilicata» abria uma secao de cultura
        t = "Ultime notizie\nNocciolo in Basilicata\nCimice asiatica, catture in aumento\n\nTesto della notizia."
        self.assertNotIn("nocciolo", BC.ler_boletim(t)["CULTURAS"])

    def test_sintetica_xylella_titulo_da_chave_nao_e_a_manchete_vizinha(self):
        import admissao as A
        t = "Leggi anche: Xylella sul nocciolo in Basilicata\n" + SINTETICA_XYLELLA
        culturas, de_onde = A._cultura_fora_da_regua({"texto": t, "fact_location_basis": ""})
        self.assertNotIn("nocciolo", culturas)

    def test_sintetica_sem_vizinhos_guarda_o_comprimento_e_a_noticia(self):
        s = FT.sem_vizinhos(SINTETICA_XYLELLA)
        self.assertEqual(len(SINTETICA_XYLELLA), len(s))
        self.assertNotIn("nocciolo", s)
        self.assertNotIn("Home | Notizie", s)
        self.assertIn(FRASE_DA_NOTICIA, s)
        self.assertIn("Xylella, nuovi focolai su mandorlo nel Materano", s)

    def test_sintetica_barra_lateral_antes_do_titulo_nao_vira_titulo(self):
        t = ("Leggi anche\nXylella, primi sintomi sul nocciolo in Basilicata\n\n"
             "La presenza di Xylella su mandorlo in agro di Matera e stata confermata dal servizio regionale oggi.\n")
        self.assertNotIn("nocciolo", FT.titulo(t))
        self.assertNotIn("nocciolo", FT.corpo(t))

    def test_sintetica_rotulo_em_linha_sai(self):
        t = "Leggi anche: Xylella sul nocciolo in Basilicata, primi casi\nTesto della notizia su mandorlo a Matera oggi."
        self.assertNotIn("nocciolo", FT.sem_vizinhos(t))

    def test_texto_sem_barra_lateral_nao_muda(self):
        t = "Titolo della notizia di prova\nPresenza di mosca dell'olivo nelle trappole della zona costiera."
        self.assertEqual(t, FT.sem_vizinhos(t))


if __name__ == "__main__":
    unittest.main(verbosity=2)
