#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O ESQUELETO DE INTELLIGENCE SCIENTIFICA, ATACADO.

    python3 -m unittest tests.test_esqueleto_scientifica -v

⚠️ DADO SINTETICO DECLARADO: a lista MUR e as obras abaixo sao inventadas para o
teste (nomes SINT-, DOI 10.0000/sint-*), e vivem so neste ficheiro. O dado real
(MUR, foto-final T6) fica fora do Git e foi corrido a mao — ver o relatorio.
"""
import copy
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in (RAIZ, RAIZ / "pacote", RAIZ / "motor", RAIZ / "provas"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import esqueleto_scientifica as S                               # noqa: E402

NAO_SEI = S.NAO_SEI


def mur(apelido, estado, ids, ateneo="SINT-ATENEO"):
    return {"MUR_NOME": f"{apelido} Sint", "APELIDO": apelido, "NOME": "Sint", "ATENEO": ateneo,
            "SSD_2024": "AGRI-05/A", "SSD_2015": "AGR/11", "FASCIA": "Associato",
            "STRUTTURA": "SINT-DIP", "IRIS": "NAO SEI", "IRIS_ESTADO": "A_CONFIRMAR",
            "ESTADO": estado, "OPENALEX_IDS": ids, "ORCID": ["0000-0000-0000-000X"] if ids else "NAO SEI",
            "OBRAS_NAS_589": 0, "PARES_DO_CASCO": [], "PROVA": ["SO_INDICE"], "SO_NOME_COM": []}


def obra(doi, autores, pares, cultura=None, local="NAO SEI", periodo="NAO SEI"):
    return {"UNIDADE": "TRABALHO_DE_PESQUISADOR", "DOI": doi, "OPENALEX_WORK_ID": "SINT-W-" + doi,
            "TITULO": "SINT titulo " + doi, "TIPO": "PEER_REVIEWED_PAPER", "PUBLICADO_EM": "2025-01-01",
            "TRIAL_ID": "NAO SEI", "AUTORES": [{"OPENALEX_ID": a, "NOME": "SINT " + a,
                                                  "PROVA_DA_PESSOA": "SO_INDICE"} for a in autores],
            "CULTURA": cultura or "NAO SEI", "PROBLEMA": "NAO SEI", "MOLECULA": "NAO SEI",
            "LOCAL_DO_ESTUDO_ESCRITO": local, "PERIODO_DO_ESTUDO": periodo,
            "NA_CONSULTA_E_NO_TEXTO": pares}


def dados():
    cruz = {"ESTADOS": {}, "LISTA": [
        mur("ALFA", "MUR_E_OBRAS", ["A1"]),
        mur("BETA", "VARIOS_IDS", ["B1", "B2"]),
        mur("GAMA", "SO_NOME", []),           # nome bate, universidade nao: fica fora
        mur("DELTA", "NAO_ENCONTRADO", []),
    ]}
    cruz["LISTA"][2]["OPENALEX_IDS"] = ["G1"]   # mesmo tendo um id, SO_NOME nao se liga
    unid = {"UNIDADES": [
        obra("10.0000/sint-1", ["A1", "X9"], ["vite x peronospora"],
             local=[{"VALOR": "Veneto", "ORIGEM": "ESCRITO"}]),
        obra("10.0000/sint-2", ["B2", "G1"], ["vite x peronospora", "vite x oidio"]),
        obra("10.0000/sint-3", ["A1"], [], cultura=[{"VALOR": "vite"}]),   # cultura sem par no texto
        obra("10.0000/sint-4", ["G1"], ["vite x oidio"]),
    ], "GRUPOS": [{"ESTADO": "PROVAVEL_MESMA_OBRA", "DOIS": ["10.0000/sint-1", "10.0000/sint-9"]}]}
    pm = {"REPLICACAO_POR_CULTURA_X_PROBLEMA": {"vite x peronospora": {
        "OBRAS": 1, "GRUPOS_DE_AUTORIA_LIMITE_SUPERIOR_DE_INDEPENDENCIA": 1}},
        "DATA_DEMAND": {"DATA_SUPPORTS_ANALYSIS": "NAO"}}
    return cruz, unid, pm


class A_OEsqueleto(unittest.TestCase):

    def setUp(self):
        c, u, pm = dados()
        self.e = S.montar(c, u, pm, {"PRE_MEDICAO_BASE": "SINT base"})

    def test_A1_marca_e_natureza_pre_sala(self):
        self.assertEqual(self.e["MARCA"], S.MARCA)
        self.assertIn("PRE_SALA", self.e["NATUREZA"])
        for t in self.e["TEMAS"].values():
            self.assertEqual(t["MARCA"], S.MARCA)
            self.assertIs(t["NAO_PARA_CLIENTE"], True)

    def test_A2_tema_so_pelo_par_no_texto_e_nunca_pela_cultura(self):
        self.assertEqual(set(self.e["TEMAS"]), {"vite x peronospora", "vite x oidio"})
        dois = [s["DOI"] for t in self.e["TEMAS"].values() for s in t["ESTUDOS"]]
        self.assertNotIn("10.0000/sint-3", dois)
        self.assertEqual(self.e["OBRAS_SEM_TEMA_DO_CASCO_NO_TEXTO"], 1)

    def test_A3_pessoa_so_pelo_id_provado_e_so_se_ligada(self):
        per = {q["MUR_NOME"]: q for q in self.e["TEMAS"]["vite x peronospora"]["PESQUISADORES_MUR"]}
        self.assertEqual(set(per), {"ALFA Sint", "BETA Sint"})
        self.assertEqual(per["BETA Sint"]["OPENALEX_IDS"], ["B1", "B2"])      # VARIOS_IDS: nao se funde
        oidio = {q["MUR_NOME"] for q in self.e["TEMAS"]["vite x oidio"]["PESQUISADORES_MUR"]}
        self.assertEqual(oidio, {"BETA Sint"})                                # GAMA (SO_NOME) fora
        self.assertEqual([f["MUR_NOME"] for f in self.e["FORA_POR_SO_NOME"]], ["GAMA Sint"])

    def test_A4_nao_sei_por_extenso_e_publicacao_nao_e_periodo(self):
        s = [x for x in self.e["TEMAS"]["vite x peronospora"]["ESTUDOS"] if x["DOI"] == "10.0000/sint-2"][0]
        self.assertEqual(s["PERIODO_DO_ESTUDO"], NAO_SEI)
        self.assertEqual(s["LOCAL_DO_ESTUDO_ESCRITO"], NAO_SEI)
        self.assertEqual(s["PUBLICADO_EM"], "2025-01-01")
        s1 = [x for x in self.e["TEMAS"]["vite x peronospora"]["ESTUDOS"] if x["DOI"] == "10.0000/sint-1"][0]
        self.assertEqual(s1["LOCAL_DO_ESTUDO_ESCRITO"], ["Veneto"])
        self.assertEqual(s1["PROVAVEL_MESMA_OBRA_QUE"], ["10.0000/sint-9"])

    def test_A4b_nao_sei_por_extenso_nos_campos_simples(self):
        """Mutante E4 sobrevivia: IRIS e TRIAL_ID passam por _v e ninguem os olhava."""
        q = self.e["TEMAS"]["vite x peronospora"]["PESQUISADORES_MUR"][0]
        self.assertEqual(q["IRIS"], NAO_SEI)
        s = self.e["TEMAS"]["vite x peronospora"]["ESTUDOS"][0]
        self.assertEqual(s["TRIAL_ID"], NAO_SEI)

    def test_A5_independencia_nao_se_calcula_vem_com_a_base(self):
        ind = self.e["TEMAS"]["vite x peronospora"]["INDEPENDENCIA_DA_PRE_MEDICAO"]
        self.assertEqual(ind["BASE"], "SINT base")
        self.assertEqual(self.e["TEMAS"]["vite x oidio"]["INDEPENDENCIA_DA_PRE_MEDICAO"], NAO_SEI)

    def test_A6_autor_mostra_o_mur_so_quando_ligado(self):
        s = [x for x in self.e["TEMAS"]["vite x peronospora"]["ESTUDOS"] if x["DOI"] == "10.0000/sint-2"][0]
        mur_por_id = {a["OPENALEX_ID"]: a["MUR"] for a in s["AUTORES"]}
        self.assertEqual(mur_por_id, {"B2": "BETA Sint", "G1": NAO_SEI})


class B_AConferencia(unittest.TestCase):

    def setUp(self):
        c, u, pm = dados()
        self.e = S.montar(c, u, pm)
        self.assertEqual(S.conferir_esqueleto(self.e), [])

    def test_B1_marca_removida_reprova(self):
        e = copy.deepcopy(self.e)
        del e["TEMAS"]["vite x oidio"]["MARCA"]
        self.assertTrue(S.conferir_esqueleto(e))
        e = copy.deepcopy(self.e)
        e["NATUREZA"] = "INTELLIGENCE"
        self.assertTrue(S.conferir_esqueleto(e))

    def test_B2_nao_sei_escondido_ou_pessoa_nao_ligada_reprova(self):
        e = copy.deepcopy(self.e)
        e["TEMAS"]["vite x oidio"]["ESTUDOS"][0]["PERIODO_DO_ESTUDO"] = ""
        self.assertTrue(S.conferir_esqueleto(e))
        e = copy.deepcopy(self.e)
        e["TEMAS"]["vite x oidio"]["PESQUISADORES_MUR"][0]["ESTADO_NA_LISTA_MESTRA"] = "SO_NOME"
        self.assertTrue(S.conferir_esqueleto(e))


class C_APagina(unittest.TestCase):

    def test_C1_faixa_pre_sala_e_escape(self):
        c, u, pm = dados()
        u["UNIDADES"][0]["TITULO"] = "<script>x</script>"
        h = S.como_html(S.montar(c, u, pm), css_href="styles.css")
        self.assertTrue(h.split("<body>", 1)[1].startswith(f'<div class="faixa" data-marca="1">{S.MARCA}'))
        self.assertIn("PRE_SALA", h)
        self.assertNotIn("<script>x</script>", h)
        self.assertIn(f'<span class="naosei">{NAO_SEI}</span>', h)

    def test_C2_nao_escreve_dentro_do_portal(self):
        self.assertEqual(S.main(["a", "b", str(RAIZ / "italia-portale" / "client" / "sci.html")]), 3)


if __name__ == "__main__":
    unittest.main()
