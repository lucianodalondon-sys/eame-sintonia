"""O pacote de desbloqueio G1 com dados sinteticos — sem rede, sem git, sem livro real.

Cada caso diz o que a regra manda: prova que bate aplica; prova que ja nao bate
SALTA; correr duas vezes = zero na segunda; o grupo T nunca muda.
"""
import copy
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("aplicar_desbloqueio",
                                            RAIZ / "scripts" / "desbloqueio" / "aplicar_desbloqueio.py")
PK = importlib.util.module_from_spec(_s)
_s.loader.exec_module(PK)

VELHO = r"^https?://(www\.)?ex\.it/(?!(?:category|tag))[a-z0-9-]+/?$"
NOVO = r"^https?://(www\.)?ex\.it/news/[a-z0-9]+(?:-[a-z0-9]+)+/?$"
MAT = "https://www.ex.it/news/um-titulo-de-noticia"
CAPA = "https://www.ex.it/news/"


def contrato(sid="IT-T10-900", lp=VELHO, t="T10"):
    return {"SOURCE_ID": sid, "TERRITORY": t, "OWNER": "Ex", "NAME": "Ex", "BATCH_ID": "LOTE-HTML-ARTIGO",
            "OUTPUT_TYPE": "HTML", "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY",
                                                   "INDEX_URL": CAPA, "LINK_PATTERN": lp}}


def proposta(sid="IT-T10-900", antes=VELHO, depois=NOVO):
    return [("PROPOSTA-RECEITAS-V1.json", {"SOURCE_ID": sid, "CAMPO": "ACQUISITION.LINK_PATTERN",
                                           "ANTES": antes, "DEPOIS": depois,
                                           "PROVA": {"MATERIAS_CONFIRMADAS": [MAT]}})]


class Peca:
    @staticmethod
    def linha_da_tabela(c, p, quando):
        return {"SOURCE_ID": c["SOURCE_ID"], "TERRITORY": c["TERRITORY"], "ACQUISITION": c["ACQUISITION"],
                "SONDAGEM": {}, "EVIDENCE": "", "ONBOARDED_BY": "teste"}


def canario(sid="IT-T10-900", lp=NOVO):
    return {"GERADO_EM": "2026-09-23T00:00:00Z", "LINHAS": [
        {"SOURCE_ID": sid, "VEREDITO": "ROUTE_PROVEN", "CANARIO": {"URL": MAT},
         "ACQUISITION_PROVADA": {"INDEX_URL": CAPA, "LINK_PATTERN": lp}}]}


class TestPacote(unittest.TestCase):

    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        self.f = self.t / "materia.html"
        self.f.write_bytes(b"<html><p>noticia</p></html>")
        self.guardadas = {MAT: (self.f, hashlib.sha256(self.f.read_bytes()).hexdigest())}

    def plano(self, livro, tabela, props=None, can=None, guardadas=None, capas=None, catalogo=None):
        with mock.patch.object(PK, "propostas", lambda: props if props is not None else proposta()):
            return PK.planear(livro, tabela, guardadas=guardadas or self.guardadas,
                              capas=capas if capas is not None else [CAPA],
                              e_generico=lambda *a: None, m3={"LINHAS": []},
                              canario=can or canario(), peca=Peca,
                              catalogo=catalogo if catalogo is not None else {"LINHAS": []})

    def base(self):
        return {"FONTES": [contrato()]}, {"FONTES": []}

    def test_prova_que_bate_aplica_nos_dois_livros(self):
        p = self.plano(*self.base())
        self.assertEqual(p["LIVRO"]["FONTES"][0]["ACQUISITION"]["LINK_PATTERN"], NOVO)
        self.assertEqual([f["SOURCE_ID"] for f in p["TABELA"]["FONTES"]], ["IT-T10-900"])
        self.assertEqual(sorted(a["ACAO"] for a in p["ACOES"]), ["APLICA", "APLICA"])

    def test_pagina_alterada_salta(self):
        g = {MAT: (self.f, "0" * 64)}
        p = self.plano(*self.base(), guardadas=g)
        a = [x for x in p["ACOES"] if x["LIVRO"] == "livro"][0]
        self.assertEqual(a["ACAO"], "SALTA")
        self.assertIn("sha256", a["PORQUE"])
        self.assertEqual(p["LIVRO"]["FONTES"][0]["ACQUISITION"]["LINK_PATTERN"], VELHO)

    def test_pagina_em_falta_salta(self):
        self.f.unlink()
        a = [x for x in self.plano(*self.base())["ACOES"] if x["LIVRO"] == "livro"][0]
        self.assertEqual(a["ACAO"], "SALTA")

    def test_padrao_que_casa_capa_do_gabarito_salta(self):
        p = self.plano(*self.base(), capas=["https://www.ex.it/news/categoria-de-noticias"])
        a = [x for x in p["ACOES"] if x["LIVRO"] == "livro"][0]
        self.assertEqual(a["ACAO"], "SALTA")
        self.assertIn("capa", a["PORQUE"])

    def test_livro_mudado_depois_da_prova_salta(self):
        livro = {"FONTES": [contrato(lp=r"^https?://ex\.it/outra/.*$")]}
        a = [x for x in self.plano(livro, {"FONTES": []})["ACOES"] if x["LIVRO"] == "livro"][0]
        self.assertEqual(a["ACAO"], "SALTA")
        self.assertIn("mudou", a["PORQUE"])

    def test_canario_de_outra_aquisicao_nao_entra_na_tabela(self):
        p = self.plano(*self.base(), can=canario(lp=VELHO))
        self.assertEqual(p["TABELA"]["FONTES"], [])

    def test_duas_fontes_mesmo_documento_so_a_primeira_entra(self):
        livro = {"FONTES": [contrato("IT-T10-900"), contrato("IT-T10-901")]}
        can = canario()
        can["LINHAS"].append(dict(can["LINHAS"][0], SOURCE_ID="IT-T10-901"))
        props = proposta("IT-T10-900") + proposta("IT-T10-901")
        p = self.plano(livro, {"FONTES": []}, props=props, can=can)
        self.assertEqual([f["SOURCE_ID"] for f in p["TABELA"]["FONTES"]], ["IT-T10-900"])

    def test_idempotente(self):
        l, t = self.base()
        p1 = self.plano(l, t)
        p2 = self.plano(copy.deepcopy(p1["LIVRO"]), copy.deepcopy(p1["TABELA"]))
        self.assertEqual([a for a in p2["ACOES"] if a["ACAO"] == "APLICA"], [])
        # a segunda passagem tem de SABER que ja aplicou — nao confundir com «o livro mudou»
        self.assertEqual({a["ACAO"] for a in p2["ACOES"]}, {"JA_APLICADA"})
        self.assertEqual(p2["LIVRO"], p1["LIVRO"])
        self.assertEqual(p2["TABELA"], p1["TABELA"])

    def test_nunca_muda_grupo_T(self):
        l, t = self.base()
        antes = {"FONTES": [contrato()]}
        depois = copy.deepcopy(antes)
        depois["FONTES"][0]["TERRITORY"] = "T7"
        with self.assertRaisesRegex(PK.InvarianteQuebrado, "grupo T"):
            PK.invariantes(antes, depois, t, t)

    def test_nunca_retira_fonte_nem_muda_outro_campo(self):
        l = {"FONTES": [contrato()]}
        with self.assertRaises(PK.InvarianteQuebrado):
            PK.invariantes(l, {"FONTES": []}, {"FONTES": []}, {"FONTES": []})
        d = copy.deepcopy(l)
        d["FONTES"][0]["OWNER"] = "outro"
        with self.assertRaises(PK.InvarianteQuebrado):
            PK.invariantes(l, d, {"FONTES": []}, {"FONTES": []})
        tab = {"FONTES": [contrato()]}
        with self.assertRaises(PK.InvarianteQuebrado):
            PK.invariantes(l, l, tab, {"FONTES": []})

    def test_linha_nova_na_tabela_com_T_diferente_do_livro_e_recusada(self):
        l = {"FONTES": [contrato()]}
        with self.assertRaises(PK.InvarianteQuebrado):
            PK.invariantes(l, l, {"FONTES": []}, {"FONTES": [contrato(t="T3")]})



class TestBlocoCatalogoD9(unittest.TestCase):
    """D9: MUDAR/RETIRAR so com prova integra; RETIRAR marca, nunca apaga;
    retirada relevante = REROUTE (salta); fora da D9 o grupo T continua fechado."""

    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        self.f = self.t / "prova.html"
        self.f.write_bytes(b"<html>prova</html>")
        self.sha = hashlib.sha256(self.f.read_bytes()).hexdigest()

    def linha(self, sid, accao, rotulo="NENHUM/NO/NO", sha=None, actual="T12"):
        return {"SOURCE_ID": sid, "UNIVERSO_ACTUAL": actual, "ACCAO": accao, "PORQUE": "x",
                "PROVA": [{"FICHEIRO": str(self.f), "SHA256": sha or self.sha, "ROTULO": rotulo}]}

    def plano(self, livro, tabela, linhas):
        with mock.patch.object(PK, "propostas", lambda: []):
            return PK.planear(livro, tabela, guardadas={}, capas=[], e_generico=lambda *a: None,
                              m3={"LINHAS": []}, canario={"LINHAS": []}, peca=Peca,
                              catalogo={"LINHAS": linhas})

    def base(self):
        return {"FONTES": [contrato("IT-T12-901", t="T12"), contrato("IT-T12-902", t="T12")]}

    def test_mudar_muda_o_grupo_e_guarda_o_anterior_no_livro_e_na_tabela(self):
        tab = {"FONTES": [contrato("IT-T12-901", t="T12")]}
        p = self.plano(self.base(), tab, [self.linha("IT-T12-901", "MUDAR_PARA_T7")])
        c = p["LIVRO"]["FONTES"][0]
        self.assertEqual(c["TERRITORY"], "T7")
        self.assertEqual(c["SOURCE_ID"], "IT-T12-901")                  # a identidade nao muda
        self.assertEqual(c["CATALOGO_D9"]["UNIVERSO_ANTERIOR"], "T12")
        self.assertEqual(p["TABELA"]["FONTES"][0]["TERRITORY"], "T7")

    def test_retirar_marca_e_nao_apaga(self):
        p = self.plano(self.base(), {"FONTES": []}, [self.linha("IT-T12-902", "RETIRAR_DO_UNIVERSO")])
        self.assertEqual(len(p["LIVRO"]["FONTES"]), 2)
        c = [x for x in p["LIVRO"]["FONTES"] if x["SOURCE_ID"] == "IT-T12-902"][0]
        self.assertEqual(c["ESTADO_CATALOGO"], "RETIRADA_POR_DECISAO")
        self.assertTrue(c["CATALOGO_D9"]["REVERSIVEL"])

    def test_retirada_com_noticia_relevante_salta_pela_d2(self):
        p = self.plano(self.base(), {"FONTES": []},
                       [self.linha("IT-T12-902", "RETIRAR_DO_UNIVERSO", rotulo="T2/NO/YES")])
        a = p["ACOES"][0]
        self.assertEqual(a["ACAO"], "SALTA")
        self.assertIn("D2", a["PORQUE"])

    def test_prova_adulterada_ou_em_falta_salta(self):
        for l in (self.linha("IT-T12-901", "MUDAR_PARA_T7", sha="0" * 64),):
            self.assertEqual(self.plano(self.base(), {"FONTES": []}, [l])["ACOES"][0]["ACAO"], "SALTA")
        self.f.unlink()
        l = self.linha("IT-T12-901", "MUDAR_PARA_T7")
        self.assertEqual(self.plano(self.base(), {"FONTES": []}, [l])["ACOES"][0]["ACAO"], "SALTA")

    def test_unknown_e_manter_intocados(self):
        p = self.plano(self.base(), {"FONTES": []},
                       [self.linha("IT-T12-901", "UNKNOWN"), self.linha("IT-T12-902", "MANTER")])
        self.assertEqual(p["ACOES"], [])
        self.assertEqual(p["LIVRO"]["FONTES"], self.base()["FONTES"])

    def test_universo_actual_diferente_do_da_proposta_salta(self):
        l = self.linha("IT-T12-901", "MUDAR_PARA_T7", actual="T2")
        self.assertIn("mudou", self.plano(self.base(), {"FONTES": []}, [l])["ACOES"][0]["PORQUE"])

    def test_idempotente_no_bloco_d9(self):
        ls = [self.linha("IT-T12-901", "MUDAR_PARA_T7"), self.linha("IT-T12-902", "RETIRAR_DO_UNIVERSO")]
        p1 = self.plano(self.base(), {"FONTES": []}, ls)
        p2 = self.plano(copy.deepcopy(p1["LIVRO"]), copy.deepcopy(p1["TABELA"]), ls)
        self.assertEqual({a["ACAO"] for a in p2["ACOES"]}, {"JA_APLICADA"})
        self.assertEqual(p2["LIVRO"], p1["LIVRO"])

    def test_retirada_no_mesmo_pacote_nao_entra_na_tabela(self):
        sid = "IT-T12-902"
        can = {"GERADO_EM": "2026-09-23", "LINHAS": [
            {"SOURCE_ID": sid, "VEREDITO": "ROUTE_PROVEN", "CANARIO": {"URL": MAT},
             "ACQUISITION_PROVADA": {"INDEX_URL": CAPA, "LINK_PATTERN": VELHO}}]}
        with mock.patch.object(PK, "propostas", lambda: []):
            p = PK.planear(self.base(), {"FONTES": []}, guardadas={}, capas=[], e_generico=lambda *a: None,
                           m3={"LINHAS": []}, canario=can, peca=Peca,
                           catalogo={"LINHAS": [self.linha(sid, "RETIRAR_DO_UNIVERSO")]})
        self.assertEqual(p["TABELA"]["FONTES"], [])
        t = [a for a in p["ACOES"] if a["LIVRO"] == "tabela"]
        self.assertEqual([a["ACAO"] for a in t], ["SALTA"])
        self.assertIn("D9", t[0]["PORQUE"])
        # e a 2.a passagem, com o livro ja retirado, tambem nao a poe na tabela
        with mock.patch.object(PK, "propostas", lambda: []):
            p2 = PK.planear(copy.deepcopy(p["LIVRO"]), copy.deepcopy(p["TABELA"]), guardadas={}, capas=[],
                            e_generico=lambda *a: None, m3={"LINHAS": []}, canario=can, peca=Peca,
                            catalogo={"LINHAS": [self.linha(sid, "RETIRAR_DO_UNIVERSO")]})
        self.assertEqual(p2["TABELA"]["FONTES"], [])
        self.assertEqual([a for a in p2["ACOES"] if a["ACAO"] == "APLICA"], [])

    def test_fora_da_d9_o_grupo_T_continua_fechado(self):
        antes = self.base()
        depois = copy.deepcopy(antes)
        depois["FONTES"][0]["TERRITORY"] = "T7"
        with self.assertRaisesRegex(PK.InvarianteQuebrado, "grupo T"):
            PK.invariantes(antes, depois, {"FONTES": []}, {"FONTES": []}, {"IT-T12-902"})
        PK.invariantes(antes, depois, {"FONTES": []}, {"FONTES": []}, {"IT-T12-901"})   # autorizada: passa


if __name__ == "__main__":
    unittest.main()
