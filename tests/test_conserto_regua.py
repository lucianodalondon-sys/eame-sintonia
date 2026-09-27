# -*- coding: utf-8 -*-
"""CONSERTO-REGUA — os quatro erros que a SALA-VERIFICA achou, cada um preso por um exemplo REAL.

Os textos sao trechos curtos das paginas que estao na Sala (fontes publicas; nomes de pessoas
tirados — nao fazem falta para a regra). Cada teste diz de que item veio.

    1  «2,80 euro/kg del 2025» — o ano de COMPARACAO de um preco nao e tempo do facto (IT-T10-018)
    2  o trecho da prova e cortado ANTES do lugar («… colpito la Sicilia», IT-T10-018)
    3  numa LISTA de eventos, os lugares de eventos diferentes juntavam-se (IT-T5-090, Popdays)
       — e um evento de 3 dias com sessoes diarias continua a ser UM evento (IT-T9-021, Didacta)
    4  um no JSON-LD WebPage com datePublished 2009 virava publicacao (IT-T7-013, CONAF)
    +  a data de evento: trecho cortado («ottob…») ou tirado do texto ja tapado (sem «oggi»)

    py -m unittest tests.test_conserto_regua
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ("", "leis", "coleta"):
    sys.path.insert(0, os.path.join(RAIZ, p))
import _gavetas  # noqa: E402,F401
import fato_do_texto as FT  # noqa: E402
import executor_texto_de_html as EX  # noqa: E402

CABECA = "Aggiornamento settimanale dei prezzi e dei mercati ortofrutticoli italiani.\n"

# ── 1 · IT-T10-018 (uva da tavola, 22/09/2026) ─────────────────────────────
UVA = CABECA + (
    "Dopo il calo della settimana 38, il prezzo medio del 2026 scende ulteriormente nella settimana "
    "39 a circa 2,40 euro/kg.\n"
    "Il valore resta sotto i circa 2,80 euro/kg del 2025 e sui livelli minimi della serie osservata.\n")

# ── 2 · IT-T10-018 (nettarine, mercato di Vittoria) ────────────────────────
NETTARINE = CABECA + (
    "Secondo il rappresentante dei grossisti del mercato ortofrutticolo di Vittoria, la causa non è il "
    "caro energia, come spesso si pensa, ma la drastica riduzione della produzione dovuta alle ondate di "
    "calore che hanno colpito la Sicilia negli ultimi mesi e settimane.\n")

# ── 3 · IT-T5-090 (pagina «Eventi segnalati dalle società scientifiche») ───
POPDAYS = (
    "Eventi segnalati dalle società scientifiche per la comunità degli studiosi di popolazione.\n"
    "Convegno Giornate di Studio Sulla Popolazione – Popdays 2023 – Roma, 1-4 febbraio 2023 – "
    "Università Roma Tre – Call for paper entro il 30 settembre 2022.\n"
    "III Conferenza italiana SIS sulle Metodologie per le Indagini Campionarie – Università degli "
    "Studi di Milano-Bicocca, Milano, 26-28 giugno 2013.\n"
    "Convegno ASA, ASSIRM e SIS – Università Cattolica del Sacro Cuore di Milano, Dipartimento di "
    "Scienze Statistiche, Milano 14-15 febbraio 2013.\n")

# ── 3b · IT-T9-021 (Didacta, 21-23 ottobre, sessioni nei tre giorni) ────────
DIDACTA = (
    # como na pagina real: o LUGAR esta no titulo, SEM data; as datas estao noutras frases
    "DIDACTA ITALIA – Edizione Abruzzo: ultime settimane per iscriversi ai 90 eventi formativi del "
    "Programma Scientifico.\n"
    "Ultime settimane per iscriversi e partecipare agli eventi formativi del Programma Scientifico, "
    "spin-off dell'edizione nazionale, in calendario dal 21 al 23 ottobre alla fiera.\n"
    "Il convegno sulla pluriclasse, fissato per il 23 ottobre alle ore 9.30, affronterà il ruolo della "
    "pluriclasse nella scuola della transizione demografica.\n"
    "I workshop sulle piccole scuole ed aree interne, previsto il 21 ottobre alle ore 14.30, propongono "
    "due prospettive complementari.\n")

# ── + · IT-T10-018 (Macfrut) — «oggi» na frase da data de evento ────────────
MACFRUT = CABECA + (
    "E' quanto emerso oggi durante la presentazione della 44esima edizione del Salone, in programma a "
    "Rimini dal 20 al 22 aprile 2027.\n")

# ── 4 · IT-T7-013 (CONAF) — o grafo JSON-LD da pagina, reduzido ao que importa ──
CONAF = (b'<html><head><script type="application/ld+json">{"@context":"https://schema.org","@graph":'
         b'[{"@type":"WebPage","@id":"https://www.conaf.it/consiglio-dellordine-nazionale/",'
         b'"name":"Consiglio dell\'Ordine Nazionale","datePublished":"2009-12-18T13:43:01+00:00",'
         b'"dateModified":"2026-01-23T09:45:42+00:00"},{"@type":"WebSite","@id":"https://www.conaf.it/#website"}]}'
         b'</script></head><body><p>Il Consiglio</p></body></html>')
NOTICIA_YOAST = (b'<html><head><script type="application/ld+json">{"@context":"https://schema.org","@graph":'
                 b'[{"@type":"NewsArticle","datePublished":"2026-09-22T10:00:21+00:00"},'
                 b'{"@type":"WebPage","datePublished":"2026-09-22T10:00:21+00:00"}]}</script></head>'
                 b'<body><p>x</p></body></html>')


class UmAnoDeComparacaoNaoETempoDoFacto(unittest.TestCase):

    def test_o_2025_do_preco_de_referencia_nao_e_o_tempo_do_facto(self):
        r = FT.campos_do_fato(UVA)
        self.assertNotEqual(r["fact_time"], "2025")
        self.assertIn("TERMO_DE_COMPARACAO", r["fact_time_basis"] + str(r["EVIDENCIA"]))

    def test_um_ano_sem_quantidade_antes_continua_a_valer(self):
        t = CABECA + ("Nel 2025 il gruppo dei retailer tedeschi ha raggiunto l'obiettivo condiviso di "
                      "acquistare metà dei propri volumi di banane certificate, con la raccolta dei dati.\n")
        r = FT.campos_do_fato(t)
        self.assertNotIn("TERMO_DE_COMPARACAO", r["fact_time_basis"])


class OTrechoContemOLugar(unittest.TestCase):

    def test_a_prova_de_sicilia_tem_a_palavra_sicilia(self):
        frase = NETTARINE.split("\n")[1]
        self.assertGreater(frase.find("Sicilia"), 200, "o exemplo tem de ter o lugar depois das 200 letras")
        r = FT.campos_do_fato(NETTARINE)
        self.assertIn("Sicilia", r["fact_location"])
        for bloco in r["fact_location_basis"].split(" ; "):
            lugar = [l for l in r["fact_location"].split(" ; ") if "«%s" % l in bloco or l in bloco]
            self.assertTrue(lugar, bloco)
        self.assertIn("Sicilia", r["fact_location_basis"])

    def test_a_base_do_lugar_nao_se_corta(self):
        linhas = ["La fiera di %s si terrà presso il quartiere fieristico cittadino con espositori e buyer "
                  "da tutta Europa, tra il 3 e il 5 marzo, con un programma ricco di incontri tecnici." % c
                  for c in ("Verona", "Bologna", "Rimini", "Cesena", "Parma", "Padova")]
        r = FT.campos_do_fato(CABECA + "\n".join(linhas) + "\n")
        for c in r["fact_location"].split(" ; "):
            if c != FT.NAO_SEI:
                self.assertIn("«", r["fact_location_basis"])
                self.assertIn(c, r["fact_location_basis"])


class UmaListaDeEventosNaoJuntaLugares(unittest.TestCase):

    def test_popdays_fica_so_em_roma(self):
        r = FT.campos_do_fato(POPDAYS)
        self.assertEqual(r["fact_time"], "1-4 febbraio 2023")
        self.assertEqual(r["fact_location"], "Roma")
        self.assertIn("SEM a data deste evento", r["fact_location_basis"])
        self.assertIn("Milano", r["fact_location_basis"])

    def test_um_evento_de_tres_dias_com_sessoes_diarias_e_um_evento_so(self):
        r = FT.campos_do_fato(DIDACTA)
        self.assertEqual(r["fact_time"], "21-23 ottobre")
        self.assertIn("Abruzzo", r["fact_location"])
        self.assertNotIn("SEM a data deste evento", r["fact_location_basis"])


class OTrechoDaDataDeEvento(unittest.TestCase):

    def test_o_trecho_contem_a_data_inteira(self):
        r = FT.campos_do_fato(DIDACTA)
        self.assertIn("23 ottobre", r["fact_time_basis"])

    def test_o_trecho_e_o_texto_original_e_nao_o_tapado(self):
        r = FT.campos_do_fato(MACFRUT)
        self.assertEqual(r["fact_time"], "20-22 aprile 2027")
        self.assertIn("emerso oggi durante", r["fact_time_basis"])


class UmaPaginaNaoEUmArtigo(unittest.TestCase):

    def test_webpage_de_2009_nao_e_publicacao(self):
        r = EX.tempo_de_publicacao(CONAF)
        self.assertEqual(r["VALOR"], "NAO SEI")
        self.assertIn("WebPage", r["PORQUE"])
        self.assertIn("2009-12-18", r["PORQUE"])

    def test_noticia_com_no_de_artigo_continua_a_valer(self):
        r = EX.tempo_de_publicacao(NOTICIA_YOAST)
        self.assertEqual(r["VALOR"], "2026-09-22T10:00:21+00:00")
        self.assertEqual(r["BASE"], EX.BASE_JSON_LD)


if __name__ == "__main__":
    unittest.main()
