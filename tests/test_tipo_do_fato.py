#!/usr/bin/env python3
"""REGUA-DO-TIPO-DE-FATO · as regras de `leis/tipo_do_fato.py`, uma por teste.

    py -m unittest tests.test_tipo_do_fato

Frases inventadas no italiano dos boletins e das noticias do acervo; nenhuma vem da prova cega.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "leis"))
import tipo_do_fato as TF  # noqa: E402

PREZZI = ("Le quotazioni dell'uva da tavola restano sotto i livelli della scorsa campagna nelle rilevazioni di settimana.\n"
          "Il prezzo medio della varieta bianca si attesta intorno a 3 euro/kg nei mercati all'ingrosso del nord.\n")
PRAGA = ("Nelle trappole a feromoni sono state registrate catture di mosca dell'olivo in aumento nella zona costiera.\n"
         "Si consiglia di verificare la soglia di intervento prima di ogni trattamento sugli oliveti della provincia.\n"
         "Presenza localizzata di peronospora e oidio nei vigneti non ancora vendemmiati della pianura interna.\n")


def tipo(t):
    return TF.tipo_do_fato(t)["fact_kind"]


class OCorpo(unittest.TestCase):
    def test_menu_curto_nao_conta(self):
        menu = "Difesa\nTrappole e catture\nPeronospora oidio\nMosca dell'olivo\n"
        self.assertEqual(tipo(menu + PREZZI), TF.MERCADO)

    def test_linha_em_maiusculas_e_menu(self):
        grito = "EVENTI FIERE CONVEGNI WORKSHOP DEL DIPARTIMENTO DI AGRARIA E DELLE COLTURE ARBOREE\n"
        r = TF.tipo_do_fato(grito + PREZZI)
        self.assertEqual(r["fact_kind"], TF.MERCADO)
        self.assertIsNone(r["EVIDENCIA"]["EVENTO_NA_ABERTURA"])

    def test_sem_corpo_e_nao_sei(self):
        self.assertEqual(tipo("Home\nNotizie\nContatti\n"), TF.NAO_SEI)
        self.assertEqual(tipo(""), TF.NAO_SEI)
        self.assertEqual(tipo(None), TF.NAO_SEI)


class PalavraInteira(unittest.TestCase):
    def test_gelateria_nao_e_gelata(self):
        t = ("La nuova gelateria del centro apre le porte ai clienti con una festa per tutta la famiglia.\n"
             "Una gelateria artigianale con prodotti tipici e una grande attenzione alla temperatura di servizio.\n")
        clima = TF.tipo_do_fato(t)["EVIDENCIA"]["CONCEITOS"].get(TF.CLIMA, [])
        self.assertFalse([c for c in clima if c.lower().startswith("gelat")])

    def test_resa_participio_e_raccolta_de_dados_nao_contam(self):
        t = ("La raccolta dei dati e stata resa possibile dal lavoro dei ricercatori del laboratorio centrale.\n"
             "Il gruppo ha curato la raccolta delle firme e la maturazione del progetto con tutti i partner.\n")
        self.assertEqual(TF.tipo_do_fato(t)["EVIDENCIA"]["CONCEITOS"].get(TF.PRODUCAO, []), [])

    def test_conceito_conta_uma_vez(self):
        t = ("Il prezzo sale ancora, il prezzo delle pere e il prezzo delle mele salgono in tutti i mercati.\n"
             "Il prezzo resta alto anche per le altre referenze vendute nei punti vendita della regione.\n")
        self.assertEqual(TF.tipo_do_fato(t)["EVIDENCIA"]["CONCEITOS"][TF.MERCADO].count("prezzo"), 1)


class OsTipos(unittest.TestCase):
    def test_praga(self):
        self.assertEqual(tipo(PRAGA), TF.FITO)

    def test_clima(self):
        t = ("La situazione sinottica vede un promontorio anticiclonico in espansione sul Mediterraneo centrale.\n"
             "Temperature in aumento e precipitazioni assenti su tutta la regione nei prossimi giorni di settimana.\n")
        self.assertEqual(tipo(t), TF.CLIMA)

    def test_evento_na_abertura_com_agro_e_evento_mesmo_com_praga(self):
        t = ("Il convegno sulla difesa integrata dell'olivo si terra a Bari il 12 novembre 2026 presso la fiera.\n"
             + PRAGA)
        self.assertEqual(tipo(t), TF.EVENTO)

    def test_evento_sem_agro_nao_e_evento_tecnico(self):
        t = ("Il convegno sulla popolazione italiana si terra a Roma il 12 novembre 2026 presso l'universita.\n"
             "Relazioni di demografi e statistici sulle tendenze della natalita e delle migrazioni interne.\n"
             "La partecipazione e libera previa registrazione sul sito della societa scientifica organizzatrice.\n")
        self.assertNotEqual(tipo(t), TF.EVENTO)

    def test_aviso_academico_nao_e_evento(self):
        t = ("Si comunica agli studenti che l'esame di Arboricoltura si svolgera il 23 settembre in aula G alle nove.\n"
             "Gli studenti del corso di viticoltura sono pregati di prenotarsi entro il giorno precedente l'appello.\n"
             "Per informazioni rivolgersi alla segreteria didattica del dipartimento di agraria in orario di ufficio.\n")
        self.assertNotEqual(tipo(t), TF.EVENTO)

    def test_empate_e_nao_sei(self):
        t = ("Il prezzo delle olive cala mentre le catture nelle trappole della costa aumentano ovunque in zona.\n"
             "Le quotazioni restano basse in molti oliveti della costa secondo i tecnici delle associazioni locali.\n")
        r = TF.tipo_do_fato(t)
        self.assertEqual(len(r["EVIDENCIA"]["CONCEITOS"][TF.FITO]), len(r["EVIDENCIA"]["CONCEITOS"][TF.MERCADO]))
        self.assertEqual(r["fact_kind"], TF.NAO_SEI)
        self.assertIn("empate", r["fact_kind_basis"])


class NegocioENaoFacto(unittest.TestCase):
    NEG = ("L'azienda ha annunciato il lancio di una nuova gamma e un investimento nel nuovo stabilimento del gruppo.\n"
           "La societa punta a crescere con il fatturato in aumento grazie al marchio e alle startup partner.\n")

    def test_negocio_sem_agro_nao_e_negocio_agro(self):
        self.assertNotEqual(tipo(self.NEG + "Il gruppo vende elettrodomestici e mobili in tutta Europa con successo.\n"),
                            TF.NEGOCIO)

    def test_negocio_com_agro(self):
        self.assertEqual(tipo(self.NEG + "La nuova gamma di sementi orticole e pensata per la filiera ortofrutticola.\n"),
                         TF.NEGOCIO)

    def test_poucas_palavras_de_negocio_nao_chegam(self):
        t = ("Le aziende agricole e la societa cooperativa della filiera ortofrutticola si sono incontrate in sede.\n"
             "Si e parlato di colture e di agricoltori in generale, senza altri dettagli sul tema della riunione.\n")
        self.assertNotEqual(tipo(t), TF.NEGOCIO)

    def test_institucional(self):
        t = ("Il regolamento definisce le modalita di deposito delle pubblicazioni nell'archivio istituzionale.\n"
             "Ogni autore deve completare la scheda del prodotto con i metadati obbligatori richiesti dal sistema.\n"
             "Le informazioni vengono trasferite automaticamente al sito docente dopo la validazione finale.\n")
        self.assertEqual(tipo(t), TF.NAO_FATO)

    def test_um_titulo_solto_nao_e_nao_facto(self):
        self.assertEqual(tipo("Nature Restoration Law e Piano nazionale di ripristino della natura - YouTube video"),
                         TF.NAO_SEI)

    def test_nunca_descarta(self):
        for t in (PRAGA, PREZZI, "", "x", self.NEG):
            r = TF.tipo_do_fato(t)
            self.assertIn(r["fact_kind"], TF.TIPOS)
            self.assertTrue(r["fact_kind_basis"])


class LigacaoAoLugarEAoTempo(unittest.TestCase):
    def test_evento_usa_o_lugar_e_o_tempo_do_evento(self):
        t = ("Il convegno sulla difesa del grano si terrà a Bologna il 12 e 13 novembre 2026 con i tecnici regionali.\n"
             "Fusariosi constatata a Grosseto la settimana scorsa, con sintomi osservati in campo.\n")
        base = TF.FT.campos_do_fato(t)
        self.assertEqual(base["fact_location_kind"], "CAMPO")          # a LUGAR-FATO, sozinha, poe o campo
        r = TF.fato_com_tipo(t)
        self.assertEqual(r["fact_kind"], TF.EVENTO)
        self.assertEqual(r["fact_location_kind"], "EVENTO")
        self.assertIn("Bologna", r["fact_location"])
        self.assertNotIn("Grosseto", r["fact_location"])
        self.assertEqual(r["fact_time_kind"], "EVENTO")
        self.assertIn("não é lugar deste facto", r["fact_location_basis"])

    def test_lugar_de_evento_nunca_vira_lugar_de_praga(self):
        t = (PRAGA + "Di questi temi si parlera anche al convegno tecnico che si terrà a Bologna il 12 novembre 2026.\n")
        base = TF.FT.campos_do_fato(t)
        self.assertEqual(base["fact_location_kind"], "EVENTO")         # sozinha, a LUGAR-FATO daria Bologna (EVENTO)
        r = TF.fato_com_tipo(t)
        self.assertEqual(r["fact_kind"], TF.FITO)
        self.assertEqual(r["fact_location"], "NAO SEI")
        self.assertNotEqual(r["fact_time_kind"], "EVENTO")
        self.assertIn("Bologna (EVENTO)", r["fact_location_basis"])

    def test_outros_tipos_nao_mexem_no_lugar(self):
        base = TF.FT.campos_do_fato(PREZZI)
        r = TF.fato_com_tipo(PREZZI)
        for k in ("fact_location", "fact_location_kind", "fact_time", "fact_time_kind"):
            self.assertEqual(r[k], base[k])


if __name__ == "__main__":
    unittest.main()
