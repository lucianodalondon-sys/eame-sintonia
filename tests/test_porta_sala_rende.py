"""PORTA-DA-SALA-RENDE (28/09) — a proposta da regua, DESLIGADA por omissao.

E1-E4 sao os casos do LAB (ESTEIRA-CONTRAPROVA, MISSAO-06):
  E1  R03 reproduzida: sem a regua nova, 0 entram (2 NAO em T7 pelo menu, 3 NSA em T8)
  E2  corpo T7 + o mesmo menu da CIA NAO pode dar NAO
  E3  T8 (e T12) sem regua = NAO_SE_APLICA com o motivo literal de hoje
  E4  pagina de seccao/listagem nao vira SIM

⚠️ Os bytes da R03 nao estao nesta arvore (vivem no banco). As paginas daqui sao
MODELADAS no que o coordenador mediu: o menu «Turismo Verde la Spesa in Campagna» da
CIA, e a morada `terraevita…/attualita/chi-e-dove/`. O texto do corpo e escrito aqui.
"""
import contextlib
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import admissao as adm  # noqa: E402

RETRATO_MATERIA = {"CAPA_OU_MATERIA": "MATERIA_PROVAVEL", "HTML_KIND": "CONTENT", "LINKS": 40,
                   "READ_MORE_LINKS": 0, "NON_WHITESPACE_CHARACTERS": 3000,
                   "PARAGRAPH_CHARACTERS": 2000}

# O menu da CIA como `limpar()` o deixa: um item de menu por linha.
MENU_CIA = "\n".join(["Chi siamo", "Servizi", "Turismo Verde la Spesa in Campagna",
                      "Donne in Campo", "Agia", "Contatti"])
# Corpo de rede tecnica sem NENHUMA palavra do lexico T7 (e o caso R03: o NAO veio do menu).
CORPO_T7 = ("I tecnici della confederazione hanno incontrato gli imprenditori della provincia "
            "per illustrare le nuove modalita di consulenza sulla gestione del suolo.\n"
            "Nel corso della giornata sono state presentate le schede di orientamento per le "
            "scelte colturali della prossima stagione nelle aree collinari interne.\n"
            "Gli sportelli territoriali restano a disposizione degli iscritti per ogni "
            "chiarimento sulle schede e sul calendario degli incontri successivi.")
CORPO_T7_POSITIVO = CORPO_T7 + (
    "\nLa confederazione ha rafforzato il servizio di assistenza tecnica con nuovi "
    "agronomi presenti ogni settimana negli sportelli di tutta la regione.")
CORPO_T8 = ("I viticoltori della collina hanno cominciato la potatura verde nei vigneti piu "
            "esposti dopo le piogge di fine agosto, con squadre al lavoro ogni mattina.\n"
            "Molti agricoltori raccontano che il raccolto sara inferiore alla media ma con uve "
            "sane, e che la concimazione di primavera ha retto al caldo di luglio.\n"
            "Nelle aziende agricole visitate il lavoro in campo si concentra ora sulla "
            "gestione del verde e sulla preparazione delle cantine per la vendemmia.")


def _pagina(texto, url, sid="TESTE-PSR", pid="teste:1"):
    return {"id": pid, "texto": texto, "source_id": sid, "artifact_type": "DERIVED",
            "parent_sha256": "ab" * 32, "retrato_do_detector": dict(RETRATO_MATERIA),
            "url_da_pagina": url}


@contextlib.contextmanager
def ligada(pecas=("MOLDURA", "NAO_COM_DOIS_SINAIS", "T8", "T12", "SECAO")):
    antes = (adm.PORTA_SALA_RENDE_LIGADA, adm.PORTA_SALA_RENDE_PECAS)
    adm.PORTA_SALA_RENDE_LIGADA, adm.PORTA_SALA_RENDE_PECAS = True, frozenset(pecas)
    try:
        yield
    finally:
        adm.PORTA_SALA_RENDE_LIGADA, adm.PORTA_SALA_RENDE_PECAS = antes


def _r03():
    """Os 5 da R03, modelados: 2 paginas CIA pedidas a T7, 3 paginas pedidas a T8."""
    return [
        (_pagina(MENU_CIA + "\n" + CORPO_T7, "https://www.cia.it/news/confederazione-incontra-"
                 "imprenditori-consulenza-suolo-collina", pid="r03:1"), "T7"),
        (_pagina(MENU_CIA + "\n" + CORPO_T7.replace("suolo", "terreno"), "https://www.cia.it/"
                 "news/schede-orientamento-scelte-colturali-aree-interne", pid="r03:2"), "T7"),
        (_pagina(CORPO_T8, "https://terraevita.edagricole.it/viticoltura/potatura-verde-"
                 "vigneti-collina-dopo-le-piogge", pid="r03:3"), "T8"),
        (_pagina(CORPO_T8.replace("collina", "pianura"), "https://terraevita.edagricole.it/"
                 "viticoltura/raccolto-uve-sane-caldo-luglio-concimazione", pid="r03:4"), "T8"),
        (_pagina(CORPO_T8, "https://terraevita.edagricole.it/attualita/chi-e-dove/",
                 pid="r03:5"), "T8"),
    ]


class A_ChaveDesligada(unittest.TestCase):
    def test_a_proposta_nasce_desligada_e_a_versao_nao_sobe(self):
        self.assertIs(adm.PORTA_SALA_RENDE_LIGADA, False)
        self.assertEqual("10", adm.VERSAO_DA_REGRA)

    def test_desligada_o_universo_e_a_regua_de_hoje(self):
        for item, u in _r03():
            for uu in (u, "T10", "T3", "T5"):
                self.assertEqual(adm._do_universo(item, uu, adm.PERGUNTAS_DO_UNIVERSO.get(uu, [])),
                                 adm._do_universo_regua(item, uu,
                                                        adm.PERGUNTAS_DO_UNIVERSO.get(uu, [])))

    def test_desligada_T8_e_T12_nao_existem_nas_reguas(self):
        self.assertNotIn("T8", adm.PERGUNTAS_DO_UNIVERSO)
        self.assertNotIn("T12", adm.PERGUNTAS_DO_UNIVERSO)
        self.assertEqual([], adm._palavras_do_universo("T8"))


class E1_R03Reproduzida(unittest.TestCase):
    def test_E1_sem_a_regua_nova_nenhum_entra(self):
        rs = [adm.decidir(i, u).resultado for i, u in _r03()]
        self.assertEqual(["NAO", "NAO", "NAO_SE_APLICA", "NAO_SE_APLICA", "NAO_SE_APLICA"], rs)
        self.assertNotIn("SIM", rs)

    def test_E1_o_NAO_de_hoje_e_a_palavra_do_menu(self):
        d = adm.decidir(_r03()[0][0], "T7")
        self.assertEqual({"T9": ["campagna"]}, d.evidencia["achado_noutro"])

    def test_E1_com_a_proposta_os_dois_T7_saem_do_NAO_e_os_T8_de_materia_entram(self):
        with ligada():
            rs = [adm.decidir(i, u).resultado for i, u in _r03()]
        self.assertEqual(["NAO_SEI", "NAO_SEI", "SIM", "SIM", "NAO_SEI"], rs)


class E2_MenuNaoCausaNao(unittest.TestCase):
    def test_E2_corpo_T7_mais_menu_CIA_nao_da_NAO(self):
        with ligada():
            d = adm.decidir(_pagina(MENU_CIA + "\n" + CORPO_T7, "https://www.cia.it/news/"
                                    "incontro-consulenza-gestione-suolo-provincia"), "T7")
        self.assertNotEqual("NAO", d.resultado)
        self.assertTrue(d.evidencia["moldura"]["aplicada"])

    def test_E2_corpo_T7_positivo_mais_menu_entra_com_trecho_do_corpo(self):
        with ligada():
            d = adm.decidir(_pagina(MENU_CIA + "\n" + CORPO_T7_POSITIVO, "https://www.cia.it/"
                                    "news/assistenza-tecnica-nuovi-agronomi-sportelli"), "T7")
        self.assertEqual("SIM", d.resultado)
        trechos = " ".join(t["trecho"] for t in d.evidencia["trechos"])
        self.assertIn("assistenza tecnica", trechos)
        self.assertNotIn("turismo verde", trechos)

    def test_E2_so_a_moldura_ja_tira_o_NAO(self):
        with ligada(("MOLDURA",)):
            d = adm.decidir(_r03()[0][0], "T7")
        self.assertEqual("NAO_SEI", d.resultado)

    def test_menu_de_uma_linha_nao_e_julgado_vazio(self):
        # pagina minificada: tudo numa linha, com «newsletter» -> corpo() da vazio.
        uma = " ".join(CORPO_T7_POSITIVO.split("\n")) + " Iscriviti alla newsletter"
        with ligada(("MOLDURA",)):
            d = adm.decidir(_pagina(uma, "https://www.cia.it/news/assistenza-tecnica-agronomi"),
                            "T7")
        self.assertFalse(d.evidencia["moldura"]["aplicada"])
        self.assertIn("MOLDURA_NAO_SEPARAVEL", d.evidencia["moldura"]["porque"])
        self.assertEqual("SIM", d.resultado)

    def test_a_lingua_mede_se_na_pagina_inteira_nao_no_corpo(self):
        vistos = []
        original = adm._lingua_do_item
        adm._lingua_do_item = lambda it: vistos.append(len(str(it.get("texto")))) or "it"
        try:
            item = _pagina(MENU_CIA + "\n" + CORPO_T7, "https://www.cia.it/news/a-b-c-d-e")
            with ligada(("MOLDURA",)):
                adm.decidir(item, "T7")
        finally:
            adm._lingua_do_item = original
        self.assertEqual({len(item["texto"])}, set(vistos))

    def test_PDF_nao_tem_moldura(self):
        item = _pagina(MENU_CIA + "\n" + CORPO_T7, "https://x.it/a.pdf")
        del item["retrato_do_detector"]
        with ligada(("MOLDURA",)):
            d = adm.decidir(item, "T7")
        self.assertFalse(d.evidencia["moldura"]["aplicada"])
        self.assertEqual("NAO", d.resultado)


class E3_SemReguaENSALiteral(unittest.TestCase):
    MOTIVO = "nao ha regra escrita do que conta como «%s». Sem regra, esta porta nao inventa uma."

    def test_E3_T8_e_T12_sem_regua_sao_NSA_literal(self):
        for u in ("T8", "T12"):
            d = adm.decidir(_pagina(CORPO_T8, "https://terraevita.edagricole.it/a/b-c-d-e-f"), u)
            self.assertEqual("NAO_SE_APLICA", d.resultado)
            self.assertEqual(self.MOTIVO % u, d.motivo)

    def test_E3_ligada_sem_a_peca_T8_continua_NSA(self):
        with ligada(("MOLDURA", "NAO_COM_DOIS_SINAIS", "T12", "SECAO")):
            d = adm.decidir(_pagina(CORPO_T8, "https://terraevita.edagricole.it/a/b-c-d-e-f"), "T8")
        self.assertEqual(("NAO_SE_APLICA", self.MOTIVO % "T8"), (d.resultado, d.motivo))


class E4_SecaoNaoViraSim(unittest.TestCase):
    def test_E4_secao_chi_e_dove_nao_vira_SIM(self):
        with ligada():
            d = adm.decidir(_r03()[4][0], "T8")
        self.assertEqual("NAO_SEI", d.resultado)
        self.assertIn("SECAO_OU_LISTAGEM", d.motivo)

    def test_E4_o_mesmo_texto_numa_morada_de_materia_entra(self):
        with ligada():
            d = adm.decidir(_r03()[2][0], "T8")
        self.assertEqual("SIM", d.resultado)
        self.assertTrue(d.evidencia["trechos"])

    def test_morada_com_algarismos_e_de_item(self):
        with ligada():
            d = adm.decidir(_pagina(CORPO_T8, "https://agronotizie.imagelinenetwork.com/"
                                    "vitivinicoltura/2026/09/10/63565"), "T8")
        self.assertEqual("SIM", d.resultado)


class Pecas(unittest.TestCase):
    def test_NAO_com_um_so_sinal_de_outro_universo_fica_NAO_SEI(self):
        with ligada(("NAO_COM_DOIS_SINAIS",)):
            d = adm.decidir(_r03()[0][0], "T7")
        self.assertEqual("NAO_SEI", d.resultado)
        self.assertIn("UM_SO_SINAL_DE_OUTRO_UNIVERSO", d.motivo)

    def test_cada_peca_e_independente_so_T8_nao_mexe_no_NAO(self):
        for so in (("T8",), ("T12",), ("SECAO",)):
            with ligada(so):
                d = adm.decidir(_r03()[0][0], "T7")
            self.assertEqual("NAO", d.resultado, so)

    def test_NAO_com_dois_sinais_de_outro_universo_continua_NAO(self):
        # EXACTAMENTE dois sinais de T9 (campagna, prodotto): a barra e SINAIS_MINIMOS, nao mais
        texto = CORPO_T7 + ("\nLa campagna promozionale presenta il nuovo prodotto e sara "
                            "illustrata ai visitatori nelle giornate di settembre in citta.")
        with ligada():
            d = adm.decidir(_pagina(texto, "https://www.cia.it/news/campagna-promozionale-"
                                    "nuovo-prodotto-fiera"), "T7")
        self.assertEqual("NAO", d.resultado)
        self.assertEqual({"T9": ["campagna", "prodotto"]}, d.evidencia["achado_noutro"])

    def test_T8_e_T12_sao_transversais_nunca_provam_NAO(self):
        texto = ("Il documento parla della politica agricola comune e dell'emendamento al "
                 "disegno di legge sulla riforma degli ecoschemi per il prossimo biennio.\n"
                 "Gli agricoltori e i viticoltori hanno seguito il dibattito nelle aziende "
                 "agricole della regione con grande attenzione alle scadenze.")
        with ligada():
            d = adm.decidir(_pagina(texto, "https://x.it/news/politica-agricola-comune-emendamento"),
                            "T10")
        self.assertNotEqual("NAO", d.resultado)
        self.assertNotIn("T8", (d.evidencia.get("achado_noutro") or {}))
        self.assertNotIn("T12", (d.evidencia.get("achado_noutro") or {}))

    def test_T12_entra_com_dois_conceitos_e_trecho(self):
        texto = ("Le organizzazioni chiedono di sostenere l'innovazione dentro la politica "
                 "agricola comune con misure dedicate agli investimenti delle imprese.\n"
                 "Il Parlamento discute un emendamento che semplifica le regole e riduce "
                 "gli oneri amministrativi per chi coltiva in pianura e in collina.")
        with ligada():
            d = adm.decidir(_pagina(texto, "https://x.it/news/innovazione-politica-agricola-"
                                    "comune-emendamento"), "T12")
        self.assertEqual("SIM", d.resultado)
        sinais = [t["sinal"] for t in d.evidencia["trechos"]]
        self.assertIn("politica agricola comune", sinais)
        self.assertIn("emendamento", sinais)

    def test_T12_palavra_inteira_pac_nao_casa_em_capacita(self):
        texto = ("La capacita produttiva dell'impianto e cresciuta e l'impaccatura dei "
                 "prodotti procede, mentre si discute un emendamento sui trasporti locali.\n"
                 "Nessuna novita sulla programmazione delle consegne per le prossime "
                 "settimane secondo quanto riferito dalla direzione dello stabilimento.")
        with ligada():
            d = adm.decidir(_pagina(texto, "https://x.it/news/capacita-produttiva-impianto-"
                                    "emendamento-trasporti"), "T12")
        self.assertNotEqual("SIM", d.resultado)

    def test_nome_de_ministerio_nao_e_politica(self):
        texto = ("Direzione generale politiche agricole alimentari e forestali, servizio "
                 "fitosanitario regionale, bollettino settimanale della difesa integrata.\n"
                 "Finanziata dal MASAF con decreto ministeriale, la campagna di monitoraggio "
                 "prosegue nelle stazioni della rete regionale di rilevamento.\n"
                 "In settimana e atteso anche un emendamento sulle scadenze dei rilievi "
                 "presso le aziende della rete di monitoraggio regionale.")
        # um so conceito de T12 (emendamento): o nome do ministerio NAO pode ser o segundo
        with ligada():
            d = adm.decidir(_pagina(texto, "https://x.it/news/bollettino-difesa-integrata-"
                                    "settimanale-regione"), "T12")
        self.assertNotEqual("SIM", d.resultado)

    def test_nenhum_SIM_sem_trecho(self):
        original = adm._trechos
        adm._trechos = lambda *a, **k: []
        try:
            with ligada():
                d = adm.decidir(_r03()[2][0], "T8")
        finally:
            adm._trechos = original
        self.assertEqual("NAO_SEI", d.resultado)
        self.assertIn("SEM_TRECHO", d.motivo)

    def test_T8_e_a_regua_YT2_sem_uma_palavra_mudada(self):
        # 14 conceitos da YT2 (4f39e8c0), pela ordem; o 1.o e o ultimo conferidos por inteiro
        t8 = adm.REGUAS_PSR["T8"]
        self.assertEqual(14, len(t8))
        self.assertEqual("agricoltore|agricoltori|agricultor|agricultores", t8[0])
        self.assertEqual("redditivita|costi di produzione|rentabilidade|custos de producao", t8[-1])
        self.assertEqual(14, len(adm.REGUAS_PSR_EN["T8"]))


if __name__ == "__main__":
    unittest.main()
