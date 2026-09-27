# -*- coding: utf-8 -*-
"""POLSO DI MERCATO · o extrator de preco observado (leis/preco_de_mercado.py). D84 + Biblia CAP-MKT.

    py -m unittest tests.test_preco_de_mercado

Sem rede, sem Sala. Dois tipos de texto, e cada teste diz qual usa:
  REAL      bytes/rotulos ja guardados no repo: BMTI 46622 e 46647 (IT-T10-002, HTML inteiro),
            Assosementi (IT-T1-013, titulo real), ISMEA (citacao literal em data/samples/IT-V2),
            Cantine Riunite (IT-T7-017, texto em data/samples/RUN-MANIFEST.json).
  SINTETICO escrito aqui, com a forma de myfruit / listini / borsa merci, marcado «SINTETICO».
"""
import inspect
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "leis"))
import preco_de_mercado as PM   # noqa: E402

AMOSTRAS = RAIZ / "data" / "samples"


def _html(nome):
    return PM.texto_de_html((AMOSTRAS / "IT-SOURCE-SAMPLES" / "IT-T10-002" / nome).read_text(encoding="utf-8"))


def _obs(r, papel=PM.OBSERVACAO):
    return [o for o in r["OBSERVACOES"] if o["PAPEL"] == papel]


class TestCasoReal280(unittest.TestCase):
    """O caso que motivou a missao: 2,80 €/kg de erba medica com «2025» ao lado, e o 2025 virou data do facto."""

    def test_real_titulo_assosementi_periodo_e_a_campanha(self):
        # REAL: IT-T1-013, REAL_EXAMPLE.TITULO
        m = json.loads((AMOSTRAS / "IT-SOURCE-SAMPLES" / "IT-T1-013" / "MANIFEST.json").read_text(encoding="utf-8"))
        r = PM.precos_do_texto(m["REAL_EXAMPLE"]["TITULO"])
        o, = _obs(r)
        self.assertEqual(2.8, o["PRECO"])
        self.assertEqual("EUR/kg", o["UNIDADE"])
        self.assertEqual("ERBA_MEDICA", o["CULTURA"])
        self.assertEqual("campagna 2026", o["PERIODO"])
        self.assertEqual("CAMPANHA", o["PERIODO_TIPO"])
        self.assertEqual("ORIENTATIVO", o["NATUREZA"])
        self.assertEqual(PM.NAO_SEI, o["ESTAGIO"], "o titulo nao escreve o estagio")

    def test_sintetico_come_nel_2025_nao_e_periodo(self):
        # SINTETICO com a forma do caso real: o unico ano da frase e o da comparacao
        r = PM.precos_do_texto("Erba medica: il prezzo orientativo resta di 2,80 €/kg come nel 2025, stabile per "
                               "gli agricoltori italiani.")
        o, = _obs(r)
        self.assertEqual(2.8, o["PRECO"])
        self.assertEqual(PM.NAO_SEI, o["PERIODO"], o["PERIODO_BASIS"])
        self.assertNotIn("2025", o["PERIODO"])
        self.assertIn("come nel 2025", [c["TRECHO"] for c in r["COMPARACOES"]])

    def test_sintetico_rispetto_al_2025_nao_e_periodo(self):
        for frase in ("Il seme di erba medica e quotato 2,80 €/kg rispetto al 2025.",
                      "Il seme di erba medica e quotato 2,80 €/kg, in linea sul 2025.",
                      "Il seme di erba medica e quotato 2,80 €/kg contro il 2025.",
                      "Il seme di erba medica e quotato 2,80 €/kg, in calo rispetto allo scorso anno 2025."):
            with self.subTest(frase=frase):
                o, = _obs(PM.precos_do_texto(frase))
                self.assertEqual(PM.NAO_SEI, o["PERIODO"], o["PERIODO_BASIS"])

    def test_sintetico_preco_do_2025_dentro_da_comparacao_e_referencia(self):
        # SINTETICO: «2,80 €/kg del 2025» e o preco da REGUA — observacao propria, periodo proprio
        r = PM.precos_do_texto("Nella campagna 2026 il seme di erba medica e pagato 3,10 €/kg, rispetto ai "
                               "2,80 €/kg del 2025.")
        o, = _obs(r)
        ref, = _obs(r, PM.REFERENCIA)
        self.assertEqual((3.1, "campagna 2026"), (o["PRECO"], o["PERIODO"]))
        self.assertEqual((2.8, "2025"), (ref["PRECO"], ref["PERIODO"]))
        self.assertNotEqual("2025", o["PERIODO"], "o ano da regua nao passa para a observacao principal")

    def test_ano_solto_antes_da_virgula_e_lido_quando_nao_e_comparacao(self):
        o, = _obs(PM.precos_do_texto("Il grano duro alla CUN e rimasto a 265 €/t nel 2026, senza scosse."))
        self.assertEqual(("2026", "ANO"), (o["PERIODO"], o["PERIODO_TIPO"]))

    def test_campanha_da_frase_vence_mesmo_com_comparacao(self):
        o, = _obs(PM.precos_do_texto("Per la campagna 2026 confermato a 2,80 €/kg il prezzo, come nel 2025."))
        self.assertEqual("campagna 2026", o["PERIODO"])


class TestRealBMTI(unittest.TestCase):
    """REAL: BMTI 46622 (cereali, HTML inteiro, capturado em 2026-09-07 do IP italiano)."""

    @classmethod
    def setUpClass(cls):
        cls.r = PM.precos_do_texto(_html("46622"))

    def test_uma_so_observacao_o_grano_duro_da_cun(self):
        o, = _obs(self.r)
        self.assertEqual(265.0, o["PRECO"])
        self.assertEqual("EUR/t", o["UNIDADE"])
        self.assertEqual("FRUMENTO", o["CULTURA"])
        self.assertEqual("grano duro fino", o["COMMODITY"])
        self.assertEqual("CUN", o["PRACA"])
        self.assertEqual(PM.INGROSSO, o["ESTAGIO"])
        self.assertEqual("FRUMENTO|CUN|INGROSSO|EUR/t|EUR", o["SERIE"])

    def test_mes_sem_ano_nao_ganha_ano(self):
        o, = _obs(self.r)
        self.assertEqual("luglio", o["PERIODO"])
        self.assertEqual("MES", o["PERIODO_TIPO"])
        self.assertIn("MES SEM ANO", o["PERIODO_BASIS"])

    def test_variacao_percentual_e_comentario_nao_preco(self):
        variacoes = [c["TRECHO"] for c in self.r["COMENTARIOS"] if c["PORQUE"] == "VARIACAO_SEM_NIVEL_DE_PRECO"]
        self.assertTrue(any("1,7%" in t for t in variacoes), variacoes)
        self.assertTrue(any("12%" in t for t in variacoes), variacoes)
        self.assertFalse(any("%" in o["PRECO_TEXTO"] for o in self.r["OBSERVACOES"]))

    def test_producao_em_toneladas_nao_vira_preco(self):
        self.assertFalse(any("tonnellate" in o["PRECO_TEXTO"] or o["PRECO"] == 5 for o in self.r["OBSERVACOES"]))

    def test_capital_social_do_rodape_e_recusado(self):
        rec = {x["VALOR_TEXTO"]: x["PORQUE"] for x in self.r["RECUSADOS"]}
        self.assertEqual("VALOR_DE_FATURAMENTO_OU_CAPITAL_NAO_E_PRECO", rec.get("€ 2.387.372,16"), rec)

    def test_su_base_mensile_nao_come_a_praca(self):
        self.assertIn("su base mensile", [c["TRECHO"] for c in self.r["COMPARACOES"]])
        self.assertNotIn("su base mensile nei listini delle principali Borse Merci nazionali",
                         [c["TRECHO"] for c in self.r["COMPARACOES"]])

    def test_menu_nao_e_comentario(self):
        self.assertNotIn("Prezzi e tariffe", [c["TRECHO"] for c in self.r["COMENTARIOS"]])
        self.assertNotIn("Listini CUN", [c["TRECHO"] for c in self.r["COMENTARIOS"]])


class TestRealOutros(unittest.TestCase):
    def test_real_bmti_46647_so_rodape_nenhum_preco(self):
        # REAL: a pagina do olio capturada so tem o rodape com €
        r = PM.precos_do_texto(_html("46647"))
        self.assertEqual([], r["OBSERVACOES"])
        self.assertTrue(r["RECUSADOS"])

    def test_real_ismea_linha_de_tabela(self):
        # REAL: citacao_literal em data/samples/IT-V2/IT-V2-CANONICO.json
        lit = "Olio extravergine di oliva | 2026-7 | 5,12 €/Kg | -15,2% | -46,7%"
        self.assertIn(lit, (AMOSTRAS / "IT-V2" / "IT-V2-CANONICO.json").read_text(encoding="utf-8"))
        o, = _obs(PM.precos_do_texto(lit))
        self.assertEqual((5.12, "EUR/kg", "OLIVO", "2026-7", "MES"),
                         (o["PRECO"], o["UNIDADE"], o["CULTURA"], o["PERIODO"], o["PERIODO_TIPO"]))

    def test_real_cooperativa_preco_de_riparto_e_fatturato(self):
        # REAL: IT-T7-017 (Cantine Riunite & Civ), texto preservado em RUN-MANIFEST.json
        raw = (AMOSTRAS / "RUN-MANIFEST.json").read_text(encoding="utf-8")
        i = raw.find("Nello splendido contesto")
        texto = json.loads('"%s"' % raw[i:raw.find('"', i)])
        texto = "16/12/2025\n" + texto          # a data da noticia, como esta na pagina
        r = PM.precos_do_texto(texto)
        o, = _obs(r)
        self.assertEqual((47.2, "EUR/q", PM.PRODUTOR), (o["PRECO"], o["UNIDADE"], o["ESTAGIO"]))
        self.assertEqual("MEDIO", o["NATUREZA"])
        self.assertEqual(PM.NAO_SEI, o["CULTURA"], "a frase do preco nao diz a cultura")
        self.assertEqual(PM.NAO_SEI, o["PERIODO"], "a data da noticia nao e o periodo do preco")
        self.assertIn("soddisfazione", " ".join(c["TRECHO"] for c in r["COMENTARIOS"] if c["PORQUE"] == "OPINIAO"))
        valores = [x["VALOR_TEXTO"] for x in r["RECUSADOS"]]
        self.assertTrue(any("266" in v for v in valores), valores)
        self.assertTrue(all(x["PORQUE"] == "VALOR_DE_FATURAMENTO_OU_CAPITAL_NAO_E_PRECO" for x in r["RECUSADOS"]))


class TestSinteticoMercado(unittest.TestCase):
    """SINTETICO: a forma de myfruit, listini e borsa merci."""

    def test_myfruit_intervalo_praca_estagio_semana(self):
        r = PM.precos_do_texto("Al mercato ortofrutticolo di Verona, nella settimana dal 7 al 13 settembre 2026, "
                               "le mele Golden sono state quotate tra 0,90 e 1,10 €/kg all'ingrosso.")
        o, = _obs(r)
        self.assertEqual((None, 0.9, 1.1), (o["PRECO"], o["PRECO_MIN"], o["PRECO_MAX"]))
        self.assertEqual(("MELO", "Verona", PM.INGROSSO), (o["CULTURA"], o["PRACA"], o["ESTAGIO"]))
        self.assertEqual("settimana dal 7 al 13 settembre 2026", o["PERIODO"])
        self.assertEqual("MELO|Verona|INGROSSO|EUR/kg|EUR", o["SERIE"])

    def test_listino_borsa_merci_forma_euro_barra_unidade_antes(self):
        o, = _obs(PM.precos_do_texto("Borsa Merci di Bologna, listino del 10/09/2026: mais nazionale franco "
                                     "partenza €/t 228,00-232,00."))
        self.assertEqual((228.0, 232.0, "EUR/t"), (o["PRECO_MIN"], o["PRECO_MAX"], o["UNIDADE"]))
        self.assertEqual(("Bologna", PM.INGROSSO, "MAIS"), (o["PRACA"], o["ESTAGIO"], o["CULTURA"]))
        self.assertEqual("10/09/2026", o["PERIODO"])

    def test_quintale_e_euro_antes_do_numero(self):
        a, b = _obs(PM.precos_do_texto("Il grano tenero alla produzione vale € 24,50/q e il risone 38 euro al quintale "
                                       "nella campagna 2025/26."))
        self.assertEqual(("EUR/q", 24.5), (a["UNIDADE"], a["PRECO"]))
        self.assertEqual(("EUR/q", 38.0, "RISO"), (b["UNIDADE"], b["PRECO"], b["CULTURA"]))
        self.assertEqual("campagna 2025/26", a["PERIODO"])

    def test_numero_com_milhar_italiano(self):
        o, = _obs(PM.precos_do_texto("L'olio extravergine di oliva e quotato 1.050,00 euro al quintale all'origine."))
        self.assertEqual(1050.0, o["PRECO"])
        self.assertEqual(PM.PRODUTOR, o["ESTAGIO"])

    def test_dettaglio(self):
        o, = _obs(PM.precos_do_texto("Nei supermercati le pere Abate sono vendute a 2,99 €/kg al dettaglio."))
        self.assertEqual((PM.DETTAGLIO, "PERO"), (o["ESTAGIO"], o["CULTURA"]))

    def test_estagios_em_conflito_ficam_nao_sei(self):
        o, = _obs(PM.precos_do_texto("Le pesche pagate 0,40 €/kg ai produttori arrivano al dettaglio con forti "
                                     "rincari nella settimana 36."))
        self.assertEqual(PM.NAO_SEI, o["ESTAGIO"])
        self.assertIn("CONFLITO", o["ESTAGIO_BASIS"])

    def test_publicacao_escrita_no_texto_nao_e_periodo(self):
        o, = _obs(PM.precos_do_texto("Pubblicato il 15/09/2026. Il pomodoro da industria e pagato ai produttori "
                                     "150 euro/t."))
        self.assertEqual(PM.NAO_SEI, o["PERIODO"])
        o, = _obs(PM.precos_do_texto("Articolo pubblicato il 15/09/2026 - pomodoro da industria pagato ai "
                                     "produttori 150 euro/t."))
        self.assertEqual(PM.NAO_SEI, o["PERIODO"], o["PERIODO_BASIS"])

    def test_projecao_nao_e_observacao(self):
        r = PM.precos_do_texto("Secondo gli operatori il prezzo del grano duro potrebbe salire a 300 €/t in autunno.")
        self.assertEqual([], r["OBSERVACOES"])
        self.assertEqual("PROJECAO_NAO_E_OBSERVACAO", r["COMENTARIOS"][0]["PORQUE"])

    def test_preco_sem_unidade_recusado(self):
        r = PM.precos_do_texto("Il prezzo delle arance di Sicilia e salito a 1,50 euro nella settimana 12 del 2026.")
        self.assertEqual([], r["OBSERVACOES"])
        self.assertEqual("PRECO_SEM_UNIDADE_NAO_E_COMPARAVEL", r["RECUSADOS"][0]["PORQUE"])

    def test_commodity_fora_da_tabela_e_cultura_nao_sei(self):
        o, = _obs(PM.precos_do_texto("I mirtilli al mercato di Milano quotati 6,50 €/kg all'ingrosso."))
        self.assertEqual(PM.NAO_SEI, o["CULTURA"])
        self.assertTrue(o["SERIE"].startswith(PM.NAO_SEI))
        self.assertIn("CULTURA", o["SERIE"])


class TestPrecoNaoViraDemanda(unittest.TestCase):
    CAMPOS_PROIBIDOS = ("DOMANDA", "DEMAND", "VENDA", "VENDAS", "SALES", "VOLUME", "QUOTA", "SHARE", "FATTURATO",
                        "RECEITA", "PROCURA")

    def test_nenhum_campo_de_demanda_ou_venda(self):
        r = PM.precos_do_texto("Al mercato di Verona le mele quotate 1,10 €/kg all'ingrosso nella settimana 37; "
                               "la domanda e in forte crescita e le vendite salgono del 12%.")
        o, = _obs(r)
        for k in o:
            for p in self.CAMPOS_PROIBIDOS:
                self.assertNotIn(p, k.upper())
        self.assertEqual(["COMENTARIOS", "COMPARACOES", "OBSERVACOES", "RECUSADOS"], sorted(r))
        self.assertIn("VOLUME_DEMANDA_OU_VENDA_NAO_E_PRECO", [c["PORQUE"] for c in r["COMENTARIOS"]])

    def test_fatturato_nunca_e_preco(self):
        r = PM.precos_do_texto("La cooperativa ha registrato un fatturato di 266 milioni di euro con vendite di "
                               "mele in aumento.")
        self.assertEqual([], r["OBSERVACOES"])
        self.assertEqual("VALOR_DE_FATURAMENTO_OU_CAPITAL_NAO_E_PRECO", r["RECUSADOS"][0]["PORQUE"])


class TestPorta(unittest.TestCase):
    def test_publicacao_e_coleta_nao_tem_por_onde_entrar(self):
        self.assertEqual({"texto"}, set(inspect.signature(PM.precos_do_texto).parameters))

    def test_cultura_vem_do_dono(self):
        import regua_italia as RI
        chaves = {k for k, _r, _a in RI.CULTURAS}
        self.assertTrue({k for _r, k in PM.COMMODITIES} <= chaves)

    def test_numero_italiano(self):
        self.assertEqual([2.8, 1234.56, 265.0, 1050.0, 0.9],
                         [PM.numero(x) for x in ("2,80", "1.234,56", "265", "1.050", "0,90")])

    def test_texto_vazio_nao_inventa(self):
        self.assertEqual({"OBSERVACOES": [], "COMENTARIOS": [], "RECUSADOS": [], "COMPARACOES": []},
                         PM.precos_do_texto(""))


if __name__ == "__main__":
    unittest.main()
