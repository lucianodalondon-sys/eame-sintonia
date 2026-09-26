#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXTRATOR-EVENTO-V2 — o tempo e o fogo como acontecimento, o titulo e a descricao do video na leitura,
e as tres leis que nao mudam: a publicacao nunca vira data do facto, «ieri» so com publicacao provada
(D63/D64), e o que ainda nao aconteceu nao e facto ocorrido. Casos reais da RENDIMENTO-POR-FONTE
(`origin/rendimento-fonte-v1`, AMOSTRA-30) marcados com o SOURCE_ID. Sem rede, sem banco."""
from __future__ import annotations

import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ("", "leis", "coleta", "orquestrador", "admissao"):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)
import _gavetas  # noqa: E402,F401
import fato_do_texto as FT  # noqa: E402
import youtube_janela as YJ  # noqa: E402

PUB = ("2026-09-26", "meta article:published_time")


def tempo(texto, pub=None, base=None, **kw):
    r = FT.campos_do_fato(texto, pub, base, **kw)
    return r["fact_time"], r["fact_time_kind"]


class OsAcontecimentosDoTempoEDoFogo(unittest.TestCase):

    def test_real_verona_declaracao_de_calamidade(self):
        """IT-T12-024: o decreto, a Gazzetta e o vento na mesma frase — vale a data do VENTO."""
        t = ("Con decreto del 30 luglio 2026 , pubblicato nella Gazzetta ufficiale del 10 agosto 2026 n. 184 il MASAF "
             "ha riconosciuto il carattere di eccezionalità dell’evento atmosferico Venti forti dell' 11 maggio 2026 "
             "in provincia di Verona, nei territori comunali di Bussolengo e Pastrengo.")
        self.assertEqual(("11 maggio 2026", "CAMPO"), tempo(t))

    def test_a_data_do_ato_nao_e_a_do_facto_mesmo_sem_ponto_no_meio(self):
        t = ("Con decreto del 30 luglio 2026 il MASAF ha riconosciuto l'evento atmosferico Venti forti dell'11 "
             "maggio 2026 in provincia di Verona.")
        self.assertEqual(("11 maggio 2026", "CAMPO"), tempo(t))
        t = ("Con delibera del 2 agosto 2026 la Regione ha dichiarato lo stato di calamità per la grandinata del "
             "14 giugno 2026 nei vigneti della provincia.")
        self.assertEqual(("14 giugno 2026", "CAMPO"), tempo(t))

    def test_so_o_ato_sem_acontecimento_datado_fica_nao_sei(self):
        t = ("Con decreto del 30 luglio 2026 il MASAF ha riconosciuto il carattere di eccezionalità dell'evento "
             "atmosferico in provincia di Verona e nei territori comunali vicini.")
        self.assertEqual(FT.NAO_SEI, tempo(t)[0])

    def test_real_pontenure_incendio(self):
        """IT-T2-051: «a seguito dell'incendio che, nella prima mattinata del 7 settembre 2026, …»."""
        t = ("Sono stati condotti da Arpae a seguito dell’incendio che, nella prima mattinata del 7 settembre 2026, "
             "ha interessato la ditta Nl Recycling a Pontenure i monitoraggi della qualita dell'aria.")
        self.assertEqual(("7 settembre 2026", "CAMPO"), tempo(t, *PUB))

    def test_os_outros_acontecimentos(self):
        casos = {
            "La grandinata del 3 luglio 2026 ha danneggiato i vigneti della Franciacorta e le serre vicine.": "3 luglio 2026",
            "L'alluvione del 16 maggio 2026 ha sommerso i frutteti e i campi di grano della bassa Romagna.": "16 maggio 2026",
            "Una tromba d'aria il 21 agosto 2026 ha scoperchiato le serre della piana del Sele e i capannoni.": "21 agosto 2026",
            "Le raffiche del 4 marzo 2026 hanno abbattuto i tunnel delle fragole nella zona di Verona.": "4 marzo 2026",
            "La gelata del 9 aprile 2026 ha bruciato i germogli dei meli in Val di Non e in Trentino.": "9 aprile 2026",
            "Il nubifragio del 5 luglio 2026 ha allagato i campi di mais della bassa pianura lombarda.": "5 luglio 2026",
            "La siccità del 2025/26 ha dimezzato le rese del grano duro in tutta la Puglia e in Basilicata.": "2025/26",
        }
        for t, esperado in casos.items():
            with self.subTest(t=t[:30]):
                self.assertEqual((esperado, "CAMPO"), tempo(t))

    def test_evento_atmosferico_sozinho_e_acontecimento(self):
        t = "L'evento atmosferico del 2 giugno 2026 ha danneggiato le coltivazioni di ortaggi della piana di Fondi."
        self.assertEqual(("2 giugno 2026", "CAMPO"), tempo(t))

    def test_real_a_data_da_atualizacao_nao_e_a_do_temporal(self):
        """IT-T2-051 (medido nos 1.252): a data esta a 60+ letras de «eventi meteorologici»."""
        t = ("Il 18 settembre effettuato un nuovo intervento sui dati, a seguito degli eventi meteorologici "
             "registrati nella regione.")
        self.assertEqual(FT.NAO_SEI, tempo(t, "2026-09-20", "meta")[0])
        self.assertIn("DATA_LONGE_DO_ACONTECIMENTO", FT.campos_do_fato(t, "2026-09-20", "meta")["fact_time_basis"])

    def test_falsos_amigos_nao_sao_acontecimento(self):
        # «gelato» (sorvete) nao e «gelata»; «vento» sozinho nao e acontecimento
        self.assertNotEqual("CAMPO", tempo("Il gelato artigianale del 4 agosto 2026 e stato venduto in tutte le "
                                           "gelaterie della citta di Bologna e dintorni.")[1])
        self.assertEqual(FT.NAO_SEI, tempo("Il vento del 3 maggio 2026 era leggero e soffiava da nord sopra le "
                                           "colline della provincia di Siena.")[0])


class OFuturoNaoEFactoOcorrido(unittest.TestCase):

    def test_alerta_com_previsao_nao_e_facto(self):
        t = ("Allerta meteo: previste per il 28 settembre 2026 raffiche di vento e grandinate su tutta la regione "
             "e nelle campagne della provincia.")
        self.assertEqual(FT.NAO_SEI, tempo(t, *PUB)[0])
        self.assertIn("PREVISAO_NAO_E_FATO", FT.campos_do_fato(t, *PUB)["fact_time_basis"])

    def test_alerta_sem_publicacao_tambem_nao_e_facto(self):
        # sem publicacao provada nao ha conta de datas: e a MARCA de previsao na frase que decide
        t = ("Allerta meteo: previste per il 28 settembre 2026 raffiche di vento e grandinate su tutta la regione "
             "e nelle campagne della provincia.")
        self.assertEqual(FT.NAO_SEI, tempo(t)[0])

    def test_real_a_marca_de_futuro_tem_de_estar_perto_da_data(self):
        """IT-T10-018 (medido nos 1.252): a raccolta 2026 JA comecou; o raccolto 2027 e futuro."""
        t = ("La raccolta 2026 negli Stati Uniti è appena iniziata e, le previsioni Usda sono di una produzione a "
             "2,4 milioni di tonnellate. Dall'Argentina i problemi produttivi di quest'anno potrebbero mantenere "
             "l'offerta ridotta fino all'arrivo del raccolto 2027.")
        self.assertEqual(("raccolta 2026", "CAMPO"), tempo(t))

    def test_real_possibilidade_nao_e_facto(self):
        """IT-T10-021 (medido nos 1.252): «ancora possibili gelate tardive, soprattutto ad aprile»."""
        t = ("Gemme e fiori sono in una fase delicata proprio quando sono ancora possibili gelate tardive, "
             "soprattutto ad aprile nelle zone di pianura.")
        self.assertEqual(FT.NAO_SEI, tempo(t)[0])

    def test_data_depois_da_publicacao_provada_nao_e_facto(self):
        t = "Le raffiche di vento del 30 settembre 2026 hanno abbattuto le serre di tutta la zona agricola della provincia."
        self.assertEqual(FT.NAO_SEI, tempo(t, *PUB)[0])
        # sem publicacao provada nao ha conta: a data escrita fica
        self.assertEqual("30 settembre 2026", tempo(t)[0])

    def test_domani_e_prossima_settimana_de_campo_nao_sao_facto(self):
        for t in ("Domani la grandinata colpira i vigneti della zona collinare secondo il servizio agrometeorologico.",
                  "La prossima settimana la siccità colpira i campi di mais di tutta la pianura padana e lombarda."):
            with self.subTest(t=t[:20]):
                self.assertEqual(FT.NAO_SEI, tempo(t, *PUB)[0])

    def test_o_evento_tecnico_anunciado_continua_evento_D62(self):
        r = FT.campos_do_fato("Il convegno tecnico sulla grandine si terrà domani presso la sede del consorzio "
                              "agrario provinciale.\n", *PUB)
        self.assertEqual(("2026-09-27", "EVENTO"), (r["fact_time"], r["fact_time_kind"]))


class APublicacaoNuncaViraData(unittest.TestCase):

    def test_data_igual_a_publicacao_e_carimbo(self):
        t = "Il 26 settembre 2026 una forte grandinata ha colpito i frutteti della bassa pianura e le serre della zona."
        self.assertEqual(FT.NAO_SEI, tempo(t, *PUB)[0])

    def test_ieri_so_com_publicacao_provada_D63(self):
        t = "Ieri la grandinata ha colpito i vigneti della zona collinare della provincia secondo il servizio agrometeorologico."
        self.assertEqual(("2026-09-25", "CAMPO"), tempo(t, *PUB))
        self.assertEqual(FT.NAO_SEI, tempo(t)[0])
        self.assertEqual(FT.NAO_SEI, tempo(t, "2026-09-26", "NAO SEI")[0])

    def test_sem_texto_do_facto_a_publicacao_nao_preenche(self):
        r = FT.campos_do_fato("Grandinata sui vigneti della Franciacorta - YouTube", *PUB)
        self.assertEqual(FT.NAO_SEI, r["fact_time"])


class OTituloEADescricao(unittest.TestCase):

    def test_real_titulo_so_titulo_entra_no_corpo_sem_o_sitio(self):
        """IT-T12-008: o texto guardado de um video e so o titulo."""
        c = FT.corpo("Potatura dell'olivo: a Macerata la 9a selezione studenti - YouTube")
        self.assertEqual("Potatura dell'olivo: a Macerata la 9a selezione studenti", c)
        c = FT.corpo("Incendio Pontenure (PC), esiti dei monitoraggi — Arpae Emilia-Romagna")
        self.assertEqual("Incendio Pontenure (PC), esiti dei monitoraggi", c)

    def test_titulo_com_acontecimento_e_data_da_a_data(self):
        self.assertEqual(("12 giugno 2026", "CAMPO"),
                         tempo("Grandinata del 12 giugno 2026 sui vigneti di Franciacorta - YouTube"))

    def test_titulo_em_duas_linhas_curtas_tambem_e_lido(self):
        t = "Grandinata del 12 giugno 2026 sui vigneti\nFranciacorta, le notizie del consorzio"
        self.assertEqual(("12 giugno 2026", "CAMPO"), tempo(t))

    def test_menu_continua_fora(self):
        self.assertEqual("", FT.corpo("Home\nNotizie\nContatti\nChi siamo"))
        self.assertEqual("", FT.corpo("Home\nNotizie\nPrivacy e cookie policy del sito web"))

    def test_texto_com_frase_longa_nao_leva_as_linhas_curtas(self):
        # EXTRATORES-V2-JUNTOS: a 1.a linha e o <title> e entra sempre (lei da EXTRATOR-LUGAR-V2); as linhas
        # curtas DEPOIS dela continuam fora quando ha frase longa
        c = FT.corpo("Home\nMenu principale del sito\nLa grandinata ha colpito i vigneti della zona collinare della provincia.")
        self.assertEqual("La grandinata ha colpito i vigneti della zona collinare della provincia.", c)

    def test_descricao_do_video_da_a_data(self):
        r = FT.campos_do_fato("x - YouTube", titulo="Maltempo in Lombardia - YouTube",
                              descricao="Il nubifragio del 5 luglio 2026 ha allagato i campi di mais della bassa.\n"
                                        "Iscriviti al canale!")
        self.assertEqual(("5 luglio 2026", "CAMPO"), (r["fact_time"], r["fact_time_kind"]))

    def test_descricao_nao_traz_a_publicacao(self):
        r = FT.campos_do_fato("x", "2026-09-26", "meta", descricao="Pubblicato il 26 settembre 2026. Buona visione.")
        self.assertEqual(FT.NAO_SEI, r["fact_time"])

    def test_pagina_do_video_guardada(self):
        det = {"videoDetails": {"title": "Grandinata del 12 giugno 2026", "shortDescription": "La grandinata del 12 giugno 2026 sui vigneti."}}
        html = "<html><script>var ytInitialPlayerResponse = %s;</script></html>" % json.dumps(det)
        self.assertEqual({"TITULO": "Grandinata del 12 giugno 2026",
                          "DESCRICAO": "La grandinata del 12 giugno 2026 sui vigneti."},
                         YJ.titulo_e_descricao_do_video(html.encode("utf-8")))

    def test_video_sem_descricao_nao_leva_a_frase_do_youtube(self):
        det = {"videoDetails": {"title": "Isitituto Agrario", "shortDescription": ""}}
        html = ('<meta name="description" content="Divertiti con i video e la musica che ami">'
                "<script>var ytInitialPlayerResponse = %s;</script>" % json.dumps(det))
        self.assertEqual({"TITULO": "Isitituto Agrario"}, YJ.titulo_e_descricao_do_video(html))
        self.assertEqual({}, YJ.titulo_e_descricao_do_video("<html>sem player</html>"))

    def test_o_reprocesso_so_pergunta_a_paginas_com_player(self):
        import reprocessar_tempo_lugar as RP
        self.assertEqual({}, RP.titulo_e_descricao(b"<html>uma pagina qualquer</html>"))
        self.assertEqual({}, RP.titulo_e_descricao(None))
        det = {"videoDetails": {"title": "Grandinata", "shortDescription": "La grandinata del 12 giugno 2026."}}
        b = ("<script>var ytInitialPlayerResponse = %s;</script>" % json.dumps(det)).encode("utf-8")
        self.assertEqual("La grandinata del 12 giugno 2026.", RP.titulo_e_descricao(b)["DESCRICAO"])

    def test_o_reprocesso_entrega_a_descricao_a_estrada(self):
        import reprocessar_tempo_lugar as RP
        from unittest import mock
        visto = {}

        class Parou(Exception):
            pass

        def espia(est, source_id):
            visto.update(est)
            raise Parou()
        det = {"videoDetails": {"title": "Grandinata", "shortDescription": "La grandinata del 12 giugno 2026."}}
        b = ("<script>var ytInitialPlayerResponse = %s;</script>" % json.dumps(det)).encode("utf-8")
        linha = {"SOURCE_ID": "IT-T8-006", "TEXTO": "Grandinata - YouTube", "ITEM_ID": "derived:1",
                 "RAW_OBSERVATION_ID": 1, "SHA256": "", "CAPTURED_AT": "2026-09-10T00:00:00Z"}
        with mock.patch.object(RP.ORQ, "item_documental_para_a_porta", espia):
            with self.assertRaises(Parou):
                RP.ready_de(linha, None, b)
        self.assertEqual("La grandinata del 12 giugno 2026.", visto.get("DESCRICAO"))

    def test_a_estrada_leva_o_titulo_e_a_descricao_ate_ao_leitor(self):
        import orquestrador as ORQ
        est = {"SOURCE_ID": "IT-T2-051", "TEXTO": "Incendio Pontenure - Arpae", "DERIVED_ARTIFACT_ID": "1",
               "RAW_ASSET_ID": 1, "PARENT_SHA256": None, "CAPTURED_AT": "2026-09-10T00:00:00Z", "TEMPO_E_LUGAR": {},
               "DESCRICAO": "Nella prima mattinata del 7 settembre 2026 un incendio ha interessato la ditta "
                            "a Pontenure con fumo sulla campagna."}
        self.assertEqual("7 settembre 2026", ORQ.item_documental_para_a_porta(est, source_id="IT-T2-051")["fact_time"])
        est.pop("DESCRICAO")
        self.assertNotEqual("7 settembre 2026",
                            ORQ.item_documental_para_a_porta(est, source_id="IT-T2-051").get("fact_time"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
