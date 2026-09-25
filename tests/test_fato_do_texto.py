# -*- coding: utf-8 -*-
"""LUGAR-FATO · o extrator de fact_location / fact_time do texto (leis/fato_do_texto.py). D61 + D62 + D63.

    py -m unittest tests.test_fato_do_texto

Sem rede, sem Sala: textos escritos aqui, com a forma dos 78 da Sala (pagina inteira: menu + corpo + rodape).
"""
import inspect
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "leis"))
import fato_do_texto as FT   # noqa: E402

MENU = "Home\nNotizie\nEmilia-Romagna\nTemi ambientali\n"
RODAPE = ("Dati rilevati dalla stazione di Bologna, Via Po 5, 40139 Bologna tel 051 6223811\n"
          "Iscrizione sul registro stampa del tribunale di Bologna n. 8586")
CORPO_FOCO = "La fusariosi e stata constatata a Grosseto dai tecnici del servizio fitosanitario durante i controlli.\n"
PUB = ("2026-09-23", "meta article:published_time")          # quarta-feira


class TestLugar(unittest.TestCase):
    def test_so_o_lugar_do_corpo_ligado_ao_acontecimento(self):
        r = FT.campos_do_fato(MENU + CORPO_FOCO + RODAPE)
        self.assertEqual("Grosseto", r["fact_location"])
        self.assertEqual("CAMPO", r["fact_location_kind"])
        self.assertEqual("PROVINCE", r["fact_location_precision"])
        self.assertIn("constatata", r["fact_location_basis"])
        self.assertIn("Grosseto", r["fact_location_basis"], "a base traz o trecho")

    def test_lugar_do_menu_e_do_rodape_nao_conta(self):
        r = FT.campos_do_fato(MENU + "Il servizio pubblica ogni settimana le analisi delle acque di balneazione.\n" + RODAPE)
        self.assertEqual(FT.NAO_SEI, r["fact_location"], r["fact_location_basis"])
        self.assertNotIn("Bologna", r["fact_location"])

    def test_o_lugar_da_fonte_e_a_data_de_coleta_nao_tem_por_onde_entrar(self):
        params = set(inspect.signature(FT.campos_do_fato).parameters)
        self.assertEqual({"texto", "publication_time", "publication_time_basis"}, params)

    def test_mencao_sem_acontecimento_fica_nao_sei(self):
        r = FT.campos_do_fato("La nostra associazione rappresenta i produttori di Firenze da oltre trenta anni.\n")
        self.assertEqual(FT.NAO_SEI, r["fact_location"])
        self.assertEqual(FT.NAO_SEI, r["fact_location_kind"])
        self.assertIn("NAO SEI", r["fact_location_basis"])

    def test_varios_lugares_ficam_todos_cada_um_com_o_trecho(self):
        r = FT.campos_do_fato("Sono stati confermati campioni positivi provenienti da Grosseto, Siena e Arezzo nelle ultime analisi.\n")
        self.assertEqual({"Grosseto", "Siena", "Arezzo"}, set(r["fact_location"].split(FT.SEP)))
        self.assertEqual(3, len(r["EVIDENCIA"]["LUGARES"]))

    def test_texto_so_de_menu(self):
        r = FT.campos_do_fato(MENU)
        self.assertEqual(FT.NAO_SEI, r["fact_location"])
        self.assertIn("não tem corpo", r["fact_location_basis"])


class TestEventoEMercado(unittest.TestCase):
    """D62: evento tecnico e facto de OUTRO tipo; feira/mercado nunca vira lugar de doenca."""

    def test_lugar_de_evento_sai_com_kind_evento(self):
        r = FT.campos_do_fato("Il convegno sulla difesa del grano si terrà a Bologna con i tecnici delle regioni del nord.\n")
        self.assertEqual("Bologna", r["fact_location"])
        self.assertEqual("EVENTO", r["fact_location_kind"])
        l = r["EVIDENCIA"]["LUGARES"][0]
        self.assertEqual(("EVENTO", "EVENT", "OTHER"), (l["KIND"], l["PAPEL_NA_LEI"], l["TIPO_DE_EVIDENCIA"]))

    def test_evento_nunca_vira_lugar_de_campo(self):
        r = FT.campos_do_fato("Convegno a Bologna sulla peronospora e fusariosi constatata a Grosseto nei campi di grano duro.\n")
        self.assertEqual("Grosseto", r["fact_location"])
        self.assertEqual("CAMPO", r["fact_location_kind"])
        kinds = {l["LUGAR"]: l["KIND"] for l in r["EVIDENCIA"]["LUGARES"]}
        self.assertEqual({"Grosseto": "CAMPO", "Bologna": "EVENTO"}, kinds)
        self.assertIn("Bologna (EVENTO)", r["fact_location_basis"])

    def test_lugar_de_mercado_sai_com_kind_mercado(self):
        r = FT.campos_do_fato("I prezzi dell'uva da tavola al mercato di Verona sono in forte aumento rispetto alla settimana.\n")
        self.assertEqual("Verona", r["fact_location"])
        self.assertEqual("MERCADO", r["fact_location_kind"])

    def test_palavra_comum_nao_vira_lugar(self):
        # medido nas 78: «fermo» (parado) casava com a provincia de Fermo
        r = FT.campos_do_fato("Il mercato dei beni di largo consumo resta sostanzialmente fermo nei volumi di questo anno.\n")
        self.assertEqual(FT.NAO_SEI, r["fact_location"], r["fact_location_basis"])

    def test_eventi_estremi_nao_e_evento_tecnico(self):
        r = FT.campos_do_fato("I soci in Veneto sono stati alle prese con eventi estremi che hanno provocato danni mai visti alle colture.\n")
        self.assertNotEqual("EVENTO", r["fact_location_kind"], r["fact_location_basis"])

    def test_data_de_evento_sai_com_kind_evento(self):
        r = FT.campos_do_fato("Il workshop si terrà il 12 e 13 novembre 2026 nella sala seminari della città della ricerca.\n")
        self.assertEqual("12-13 novembre 2026", r["fact_time"])
        self.assertEqual("EVENTO", r["fact_time_kind"])
        self.assertIn("workshop", r["fact_time_basis"])
        r = FT.campos_do_fato("La fiera è in programma a Madrid dal 6 all'8 ottobre 2026 con molti espositori del settore.\n")
        self.assertEqual("6-8 ottobre 2026", r["fact_time"])

    def test_data_de_campo_vence_data_de_evento(self):
        r = FT.campos_do_fato("Il monitoraggio ha rilevato le prime catture il 12 settembre nei vigneti della zona collinare.\n"
                              "Il convegno regionale si terrà il 20 ottobre 2026 nella sala del consorzio di tutela.\n")
        self.assertEqual(("12 settembre", "CAMPO"), (r["fact_time"], r["fact_time_kind"]))
        self.assertEqual(1, len(r["EVIDENCIA"]["TEMPOS_DE_EVENTO"]))


class TestTempo(unittest.TestCase):
    def test_data_escrita_e_ligada_ao_acontecimento(self):
        r = FT.campos_do_fato("Il monitoraggio ha rilevato le prime catture il 12 settembre nei vigneti della zona collinare.\n")
        self.assertEqual("12 settembre", r["fact_time"])
        self.assertEqual("DATE_EXACT", r["fact_time_precision"])
        self.assertIn("prime catture", r["fact_time_basis"], "a base traz o trecho")

    def test_a_publicacao_nunca_vira_tempo_do_facto(self):
        t = "Articolo pubblicato sul portale regionale con tutti gli aggiornamenti delle attività in corso.\n"
        r = FT.campos_do_fato(t, *PUB)
        self.assertEqual(FT.NAO_SEI, r["fact_time"])
        self.assertEqual("NOT_KNOWN", r["fact_time_precision"])
        self.assertIn("nunca preenche", r["fact_time_basis"])
        self.assertEqual("2026-09-23", r["EVIDENCIA"]["PUBLICACAO_PROVADA"], "a publicacao fica a parte")
        r2 = FT.campos_do_fato("Il monitoraggio del 23 settembre 2026 conferma il quadro gia descritto nei giorni precedenti.\n", *PUB)
        self.assertEqual(FT.NAO_SEI, r2["fact_time"], "a data igual a publicacao e carimbo, nao facto")

    def test_serie_de_anos_carimbo_de_lista_e_prazo_nao_sao_tempo_do_facto(self):
        for t in ("Il raccolto registra volumi stabili con il confronto tra le settimane 35-39 del 2024, 2025 e 2026 nei mercati.\n",
                  "1 settembre 2026 Risultati del monitoraggio delle radiazioni ultraviolette in tutta Europa pubblicati.\n",
                  "Il raccolto bio, iniziato da poche settimane e in proseguimento fino a novembre, registra volumi stabili.\n"):
            r = FT.campos_do_fato(t)
            self.assertEqual(FT.NAO_SEI, r["fact_time"], (t, r["fact_time"]))
            self.assertIn("descartadas", r["fact_time_basis"])

    def test_os_campos_com_os_nomes_combinados(self):
        r = FT.campos_do_fato(CORPO_FOCO)
        for k in ("fact_location", "fact_location_basis", "fact_location_kind", "fact_location_precision",
                  "fact_time", "fact_time_basis", "fact_time_kind", "fact_time_precision"):
            self.assertTrue(isinstance(r[k], str) and r[k], k)


class TestRelativasD63(unittest.TestCase):
    """D63: relativa vale SO com publicacao provada e a conta feita; intervalo nunca vira um dia."""

    def _r(self, expr, pub=PUB):
        return FT.campos_do_fato("I sintomi di peronospora sono stati osservati %s nei vigneti della provincia dai tecnici.\n" % expr, *pub)

    def test_cada_expressao_e_a_conta(self):
        casos = {
            "ieri": ("2026-09-22", "DATE_EXACT+CALCULADA"),
            "oggi, mercoledì,": ("2026-09-23", "DATE_EXACT+CALCULADA"),
            "stamattina": ("2026-09-23", "DATE_EXACT+CALCULADA"),
            "l'altro ieri": ("2026-09-21", "DATE_EXACT+CALCULADA"),
            "la settimana scorsa": ("2026-09-14/2026-09-20", "WEEK+CALCULADA"),
            "la scorsa settimana": ("2026-09-14/2026-09-20", "WEEK+CALCULADA"),
            "questa settimana": ("2026-09-21/2026-09-27", "WEEK+CALCULADA"),
            "lunedì scorso": ("2026-09-21", "DATE_EXACT+CALCULADA"),
            "mercoledì scorso": ("2026-09-16", "DATE_EXACT+CALCULADA"),
            "il mese scorso": ("2026-08-01/2026-08-31", "MONTH+CALCULADA"),
            "l'anno scorso": ("2025-01-01/2025-12-31", "APPROXIMATE+CALCULADA"),
        }
        for expr, (valor, prec) in casos.items():
            r = self._r(expr)
            self.assertEqual((valor, prec), (r["fact_time"], r["fact_time_precision"]), expr)
            # D69/D70: a base e SEMPRE «RELATIVA_A_PUBLICACAO» (nunca PUBLISHED_AT_COM_PROVA); a expressao
            # e o trecho vao para fact_time_expressao / fact_time_evidencia
            self.assertEqual("RELATIVA_A_PUBLICACAO", r["fact_time_basis"], expr)
            self.assertEqual("RELATIVA_A_PUBLICACAO", r["fact_time_calculo"], expr)
            self.assertEqual(expr.split(",")[0].lower(), r["fact_time_expressao"].lower(), "a expressao original")
            self.assertIn(r["fact_time_expressao"], r["fact_time_evidencia"], "o trecho traz a expressao")
            self.assertEqual("2026-09-23", r["EVIDENCIA"]["PUBLICACAO_PROVADA"])

    def test_intervalo_nunca_vira_um_dia(self):
        r = self._r("la settimana scorsa")
        self.assertIn("/", r["fact_time"])
        self.assertNotEqual("2026-09-16", r["fact_time"])

    def test_sem_publicacao_provada_e_nao_sei(self):
        for pub in ((None, None), ("2026-09-23", None), ("2026-09-23", "NAO SEI"), ("23/09/2026", "meta")):
            for expr in ("ieri", "la settimana scorsa", "lunedì scorso"):
                r = self._r(expr, pub)
                self.assertEqual(FT.NAO_SEI, r["fact_time"], (expr, pub))
                self.assertIn("publicação não provada", r["fact_time_basis"])
                self.assertIn("«%s»" % expr, r["fact_time_basis"])
                self.assertEqual(expr, r["EVIDENCIA"]["EXPRESSOES_RELATIVAS"][0]["EXPRESSAO"])

    def test_sem_medida_nao_vira_data(self):
        r = self._r("nei giorni scorsi")
        self.assertEqual(FT.NAO_SEI, r["fact_time"])

    def test_relativa_de_evento(self):
        r = FT.campos_do_fato("Il convegno tecnico sul mais si terrà domani presso la sede del consorzio agrario provinciale.\n", *PUB)
        self.assertEqual(("2026-09-24", "EVENTO", "DATE_EXACT+CALCULADA"),
                         (r["fact_time"], r["fact_time_kind"], r["fact_time_precision"]))

    def test_duas_contas_diferentes_e_nao_sei(self):
        r = FT.campos_do_fato("I sintomi sono stati osservati ieri nei vigneti; altri sintomi rilevati la settimana scorsa "
                              "nei frutteti della provincia.\n", *PUB)
        self.assertEqual(FT.NAO_SEI, r["fact_time"])
        self.assertIn("AMBIGUO", r["fact_time_basis"])

    def test_termo_de_comparacao_nao_e_tempo_do_facto(self):
        # medido nas 78 (IT-T3-008)
        for t in ("Si registrano infezioni di peronospora in minor misura rispetto allo stesso periodo dello scorso anno nei vigneti.\n",
                  "Le catture rilevate nei frutteti sono in aumento rispetto alla settimana scorsa in tutta la provincia.\n"):
            r = FT.campos_do_fato(t, *PUB)
            self.assertEqual(FT.NAO_SEI, r["fact_time"], t)
            self.assertIn("comparação", r["fact_time_basis"], t)

    def test_a_conta_nao_depende_do_dia_de_hoje(self):
        r = self._r("ieri", ("2020-02-29", "meta"))
        self.assertEqual("2020-02-28", r["fact_time"])


class TestLeiDoArtefatoD70(unittest.TestCase):
    """D70: a data calculada diz RELATIVA_A_PUBLICACAO, escreve-se como o DIA, e `leis.artefato.conferir`
    refaz a conta a partir das NOTES (os testes da lei em si estao em test_artefato_tempo_do_fato)."""

    OGGI = "I tecnici hanno osservato oggi, lunedì, sintomi di peronospora nei vigneti di Verona.\n"
    BASE = "meta article:published_time"

    def _conferir(self, r, published_at):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from leis import artefato as A
        a = A.Artefato(ARTIFACT_ID="t", ARTIFACT_TYPE="DERIVED", STORAGE_LOCATION="t", SHA256="0" * 64,
                       FACT_TIME=r["fact_time"], PUBLISHED_AT=published_at,
                       NOTES=FT.notas_para_o_artefato(r, self.BASE))
        return A.conferir(a)

    def test_oggi_marcado_com_publicacao_so_dia_passa_na_lei(self):
        r = FT.campos_do_fato(self.OGGI, "2026-09-21", self.BASE)
        self.assertEqual("2026-09-21", r["fact_time"], "D70: o dia calculado e o dia, nao um intervalo de fuga")
        self.assertEqual("RELATIVA_A_PUBLICACAO", r["fact_time_basis"])
        self.assertEqual("DATE_EXACT+CALCULADA", r["fact_time_precision"])
        self.assertEqual(("RELATIVA_A_PUBLICACAO", "oggi"), (r["fact_time_calculo"], r["fact_time_expressao"]))
        self.assertIn("oggi, lunedì", r["fact_time_evidencia"])
        self.assertEqual([], self._conferir(r, "2026-09-21"))
        self.assertEqual([], self._conferir(r, "2026-09-21T09:00:00+02:00"))

    def test_nunca_published_at_com_prova(self):
        for pub in ("2026-09-21", "2026-09-23"):
            for t in (self.OGGI, "I tecnici hanno osservato ieri sintomi di peronospora nei vigneti di Verona.\n"):
                r = FT.campos_do_fato(t, pub, self.BASE)
                self.assertNotIn("PUBLISHED_AT_COM_PROVA", r["fact_time_basis"] + r["fact_time_evidencia"])

    def test_conta_diferente_da_publicacao_diz_relativa(self):
        r = FT.campos_do_fato("I tecnici hanno osservato ieri sintomi di peronospora nei vigneti della provincia di Verona.\n",
                              "2026-09-21", self.BASE)
        self.assertEqual(("2026-09-20", "RELATIVA_A_PUBLICACAO"), (r["fact_time"], r["fact_time_basis"]))
        self.assertEqual([], self._conferir(r, "2026-09-21"))

    def test_a_expressao_esta_sempre_no_trecho(self):
        # «ieri» depois da letra 250 da frase: um trecho que so guardasse o comeco da frase perdia-o
        longa = ("Nel corso della lunga riunione tecnica del consorzio di tutela, che ha visto la partecipazione "
                 "di molti produttori della zona collinare e pedecollinare, dei tecnici regionali incaricati del "
                 "controllo e dei rappresentanti delle cantine sociali della valle, è stato riferito con chiarezza che "
                 "ieri sono stati osservati sintomi di peronospora in diversi vigneti della parte collinare "
                 "della provincia, con una diffusione ancora limitata ma da seguire con attenzione.\n")
        self.assertGreater(longa.index("ieri"), 250)
        r = FT.campos_do_fato(longa, "2026-09-21", self.BASE)
        self.assertEqual("2026-09-20", r["fact_time"])
        self.assertIn("ieri", r["fact_time_evidencia"])
        self.assertEqual([], self._conferir(r, "2026-09-21"))

    def test_data_nao_calculada_nao_ganha_campos_de_calculo(self):
        r = FT.campos_do_fato("Il monitoraggio ha rilevato le prime catture il 12 settembre nei vigneti della zona collinare.\n")
        self.assertEqual(("NAO_SE_APLICA",) * 3,
                         (r["fact_time_calculo"], r["fact_time_expressao"], r["fact_time_evidencia"]))


class TestEnsaioDoPacote(unittest.TestCase):
    """Os casos do ensaio do PACOTE-TEMPO-LUGAR (25/09): incoerencia lugar/data, conselho, lugares perdidos."""

    def test_mesma_frase_da_lugar_e_data(self):
        # IT-T3-008: «registrato» e ancora de LUGAR do leitor, nao de TEMPO; a relativa tem de contar na mesma
        t = ("Importante è sottolineare lo scarto climatico registrato nella settimana scorsa: + 6 gradi le massime "
             "su gran parte della Puglia e fino a quattro gradi sull'area adriatica.\n")
        r = FT.campos_do_fato(t, "2026-09-16", "meta article:published_time")
        self.assertEqual("Puglia", r["fact_location"])
        self.assertEqual(("2026-09-07/2026-09-13", "RELATIVA_A_PUBLICACAO"), (r["fact_time"], r["fact_time_basis"]))
        self.assertEqual(FT.NAO_SEI, FT.campos_do_fato(t)["fact_time"], "sem publicacao continua NAO SEI")

    def test_proximo_boletim_nao_e_facto(self):
        t = "Il prossimo bollettino fitosanitario sarà pubblicato la prossima settimana sul sito del servizio regionale.\n"
        r = FT.campos_do_fato(t, "2026-09-16", "meta article:published_time")
        self.assertEqual(FT.NAO_SEI, r["fact_time"], r["fact_time_basis"])

    def test_conselho_nao_e_facto(self):
        t = ('Per la mosca delle olive i tecnici hanno rilevato catture basse in tutta la zona collinare.\n'
             '- eseguire la "diagnosi precoce" in luglio e agosto per verificare la presenza di nuove infezioni non ancora evidenti\n'
             'Si ricorda che la "diagnosi\nprecoce" in luglio e agosto per verificare la presenza di nuove infezioni non ancora evidenti\n')
        r = FT.campos_do_fato(t)
        self.assertEqual(FT.NAO_SEI, r["fact_time"], r["fact_time_basis"])
        self.assertIn("RECOMENDACAO_NAO_FATO", r["fact_time_basis"])
        self.assertEqual(["luglio"], [j["VALOR"] for j in r["EVIDENCIA"]["JANELA_RECOMENDADA"]])
        r = FT.campos_do_fato("Si consiglia di intervenire la prossima settimana nei vigneti colpiti da peronospora in collina.\n",
                              "2026-09-16", "meta article:published_time")
        self.assertEqual(FT.NAO_SEI, r["fact_time"])
        self.assertIn("conselho", r["fact_time_basis"])

    def test_evento_com_a_palavra_depois_das_300_letras(self):
        t = ("Giovedì 8 ottobre 2026 la Scuola di Legalità dell'Università di Teramo ospita il direttore del servizio "
             "regionale, responsabile del centro nazionale per la protezione delle infrastrutture critiche del paese, "
             "che interverrà sul tema della sicurezza delle aziende agricole e della filiera alimentare italiana nel "
             "corso del seminario aperto agli studenti e ai tecnici delle organizzazioni professionali agricole.\n")
        self.assertGreater(t.index("seminario"), 300)
        r = FT.campos_do_fato(t)
        self.assertEqual(("Teramo", "EVENTO"), (r["fact_location"], r["fact_location_kind"]))

    def test_punti_vendita_e_mercado(self):
        r = FT.campos_do_fato("L'Osservatorio Piccoli Frutti a Firenze ha visitato 14 punti vendita della grande "
                              "distribuzione per rilevare i prezzi dei mirtilli.\n")
        self.assertEqual(("Firenze", "MERCADO"), (r["fact_location"], r["fact_location_kind"]))

    def test_pais_e_nome_maior_nao_sao_promovidos(self):
        r = FT.campos_do_fato("Il convegno internazionale presenterà i nuovi risultati sullo spreco alimentare con focus "
                              "sull'Italia e sul confronto tra paesi.\n")
        self.assertEqual(FT.NAO_SEI, r["fact_location"], r["fact_location_basis"])
        r = FT.campos_do_fato("La fiera punta a diversificare verso nuovi contesti internazionali, a partire dall'America "
                              "Latina con il Cile paese partner.\n")
        self.assertNotIn("Latina", r["fact_location"])


class TestOggiD64(unittest.TestCase):
    """D64: «oggi» so conta quando o texto deixa claro que e o proprio dia."""

    FRASE = "I tecnici hanno osservato %s sintomi di peronospora nei vigneti della provincia di Verona.\n"

    def test_oggi_que_e_o_dia(self):
        for expr in ("oggi, lunedì,", "oggi 23 settembre", "oggi alle 10", "oggi pomeriggio", "nella giornata di oggi"):
            r = FT.campos_do_fato(self.FRASE % expr, *PUB)
            self.assertEqual("2026-09-23", r["fact_time"], expr)
            self.assertEqual("DATE_EXACT+CALCULADA", r["fact_time_precision"], expr)
        r = FT.campos_do_fato("Oggi è stato osservato un forte attacco di peronospora nei vigneti della zona collinare.\n", *PUB)
        self.assertEqual("2026-09-23", r["fact_time"])

    def test_oggi_que_e_hoje_em_dia(self):
        for t in ("Oggi i consumatori chiedono più frutta biologica e i produttori osservano la domanda crescente.\n",
                  "Ad oggi sono stati rilevati pochi casi di flavescenza dorata nei vigneti della provincia.\n",
                  "Fino ad oggi il monitoraggio non ha rilevato superamenti della soglia nei frutteti della zona.\n",
                  "Al giorno d'oggi il monitoraggio delle colture si fa con trappole e sensori nei campi del nord.\n",
                  "I sintomi osservati oggi nei vigneti confermano la pressione della peronospora in tutta la zona.\n"):
            r = FT.campos_do_fato(t, *PUB)
            self.assertEqual(FT.NAO_SEI, r["fact_time"], (t, r["fact_time_basis"]))
            self.assertIn("D64", r["fact_time_basis"], t)

    def test_oggi_sem_publicacao_e_nao_sei(self):
        r = FT.campos_do_fato(self.FRASE % "oggi, lunedì,")
        self.assertEqual(FT.NAO_SEI, r["fact_time"])


class TestCoordenacao2509(unittest.TestCase):
    """(a) onde se planta/colhe e CAMPO mesmo em noticia de mercado; (b) data institucional nao e facto."""

    def test_lugar_de_producao_numa_noticia_de_mercado_e_campo(self):
        r = FT.campos_do_fato("Più shelf-life per allargare i confini del mercato In Sardegna si producono tante fragole, "
                              "ma le distanze impediscono una politica di export.\n")
        self.assertEqual(("Sardegna", "CAMPO"), (r["fact_location"], r["fact_location_kind"]))
        self.assertIn("PRODUCAO", r["fact_location_basis"])
        self.assertEqual("OTHER", r["EVIDENCIA"]["LUGARES"][0]["TIPO_DE_EVIDENCIA"], "producao nao e foco de praga")

    def test_producao_longe_do_lugar_nao_o_faz_campo(self):
        r = FT.campos_do_fato("La Toscana ha presentato ieri il suo nuovo piano regionale per la formazione dei giovani "
                              "tecnici agrari e, in un altro capitolo del documento, si producono stime generali.\n")
        self.assertEqual(FT.NAO_SEI, r["fact_location"], r["fact_location_basis"])

    def test_o_mercado_perto_continua_mercado(self):
        r = FT.campos_do_fato("Al mercato ortofrutticolo di Milano i prezzi dei piccoli frutti sono aumentati in questa fase.\n")
        self.assertEqual(("Milano", "MERCADO"), (r["fact_location"], r["fact_location_kind"]))

    def test_exame_adiado_nao_e_tempo_do_facto(self):
        r = FT.campos_do_fato("L'esame del modulo di arboricoltura già previsto per il 21 settembre è spostato a mercoledì 30.\n")
        self.assertEqual(FT.NAO_SEI, r["fact_time"], r["fact_time_basis"])
        self.assertIn("INSTITUCIONAL_NAO_FATO", r["fact_time_basis"])

    def test_ancora_dentro_de_outra_palavra_nao_amarra(self):
        # «coltura» dentro de «agricoltura» nao liga a data a um acontecimento
        r = FT.campos_do_fato("La Regione ha destinato nel 2022 molti fondi al settore della agricoltura e della pesca.\n")
        self.assertEqual(FT.NAO_SEI, r["fact_time"], r["fact_time_basis"])
        self.assertIn("ANCORA_DENTRO_DE_OUTRA_PALAVRA", r["fact_time_basis"])


if __name__ == "__main__":
    unittest.main()
