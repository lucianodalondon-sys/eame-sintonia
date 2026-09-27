#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O GRAFO DE DEPENDENCIA, ATACADO — as classes PURAS de
`tests/test_independencia_de_fontes.py` @ eb3a7b1d (ramo nuvem-independencia-v1).

    python3 -m unittest tests.test_grafo_de_dependencia -v

MISSAO CAP-WIN. O grafo veio para este ramo TAL E QUAL (`motor/grafo_de_dependencia.py`
e o blob de eb3a7b1d, byte a byte) porque a janela precisa de contar originadores.
A integracao do grafo na corrida G0 e no motor V2.1 NAO veio: aquele ramo parte de
60faa7cb e perderia D11/D14/D15. Por isso as classes `NaCorridaDaInteligencia` e
`NoMotorV21` ficam la; aqui ficam, sem uma linha mudada, as tres que so tocam o grafo.

Os casos SINTETICOS vao marcados `SINTETICO` no proprio item.
"""
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in (RAIZ, RAIZ / "motor"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import grafo_de_dependencia as GD                           # noqa: E402

S = "SINTETICO"


def sin(ref, url=None, sha=None, sid=None, **kw):
    e = {"ID": ref, "MARCA": S}
    if url:
        e["URL"] = url
    if sha:
        e["SHA256"] = sha
    if sid:
        e["SOURCE_ID"] = sid
    e.update(kw)
    return e


def nove_da_primeira_rodada():
    """A forma do D16: 9 sinais, 6 de myfruit.it (paginas e seccoes diferentes,
    dois SOURCE_ID diferentes — o registo tambem pode partir o mesmo site)."""
    mf = [sin(f"MF{i}", f"https://www.myfruit.it/notizie/{i}", sha=f"mf{i}",
              sid="IT-T6-MF" if i < 4 else "IT-T6-MF-B") for i in range(5)]
    mf.append(sin("MF5", "https://news.myfruit.it/mercati/5", sha="mf5"))
    outros = [sin("A", "https://www.ansa.it/x", sha="a", sid="IT-T6-ANSA"),
              sin("B", "https://agricoltura.regione.emilia-romagna.it/b", sha="b"),
              sin("C", "https://www.freshplaza.it/c", sha="c")]
    return mf + outros


# ══════════════════════════════════════════════════════════════════════════════
class D12_MesmoDocumentoEUmaEvidencia(unittest.TestCase):

    def test_o_mesmo_sha_lido_duas_vezes_e_uma_evidencia(self):
        g = GD.grafo([sin("R1", sha="abc", sid="IT-T3-1", RAW_OBSERVATION_ID="O1"),
                      sin("R2", sha="ABC", sid="IT-T3-1", RAW_OBSERVATION_ID="O2")])
        self.assertEqual(2, g["EXTERNAL_SIGNAL_COUNT"])
        self.assertEqual(1, g["EVIDENCE_BASE_COUNT"])
        self.assertEqual(1, g["INDEPENDENT_SOURCE_COUNT"])
        self.assertEqual(GD.NAO_CONVERGE, g["CONVERGENCE"])
        self.assertEqual(["R2"], g["DOCUMENT_DUPLICATES"][0]["COLAPSADAS"])
        self.assertIn("SHA", g["DOCUMENT_DUPLICATES"][0]["PORQUE"])

    def test_o_mesmo_document_id_sem_sha_e_uma_evidencia(self):
        g = GD.grafo([sin("R1", SOURCE_DOCUMENT_ID="DOC-9"),
                      sin("R2", SOURCE_DOCUMENT_ID="DOC-9")])
        self.assertEqual(1, g["EVIDENCE_BASE_COUNT"])

    def test_duas_capturas_do_mesmo_endereco_sao_um_documento_marcado(self):
        """INT-LAW-074: bytes diferentes no mesmo endereco classificam-se,
        nao se somam."""
        g = GD.grafo([sin("R1", "https://www.x.it/bollettino/", sha="v1"),
                      sin("R2", "http://x.it/bollettino#topo", sha="v2")])
        self.assertEqual(1, g["EVIDENCE_BASE_COUNT"])
        self.assertTrue(g["DOCUMENT_DUPLICATES"][0]["VERSOES_DIFERENTES"])

    def test_query_diferente_e_documento_diferente(self):
        g = GD.grafo([sin("R1", "https://x.it/b?id=7"), sin("R2", "https://x.it/b?id=8")])
        self.assertEqual(2, g["EVIDENCE_BASE_COUNT"])
        self.assertEqual(1, g["INDEPENDENT_SOURCE_COUNT"])

    def test_a_coorte_real_sao_seis_documentos_de_tres_originadores(self):
        """Os 6 itens reais da Sala (14/09): 6 boletins/ficheiros diferentes, mas
        so 3 publicadores (Campania, Puglia, Ministero). Sem o grafo, 6 sinais
        pareciam 6 fontes."""
        itens = json.loads((RAIZ / "research" / "intelligence"
                            / "COORTE-DA-SALA-2026-09-14.json").read_text(encoding="utf-8"))["ITENS"]
        g = GD.grafo(itens)
        self.assertEqual(6, g["EXTERNAL_SIGNAL_COUNT"])
        self.assertEqual(6, g["EVIDENCE_BASE_COUNT"])
        self.assertEqual(3, g["INDEPENDENT_SOURCE_COUNT"])
        self.assertEqual(33.3, g["DOMINANT_SOURCE_SHARE_PCT"])
        self.assertEqual(["agrometeopuglia.it", "campania.it", "salute.gov.it"],
                         sorted(f["ORIGINADOR"] for f in g["SOURCE_FAMILIES"]))
        # e nenhum deles declara o FATO: tres fontes sobre fatos desconhecidos
        # nao sao concordancia
        pf = GD.por_fato(itens, lambda e: e.get("FATO"))
        self.assertEqual([GD.NAO_SEI], list(pf))
        self.assertEqual(GD.NAO_SEI, pf[GD.NAO_SEI]["CONVERGENCE"])


# ══════════════════════════════════════════════════════════════════════════════
class D16_MesmoOriginadorEUmaFonte(unittest.TestCase):

    def test_seis_de_nove_de_myfruit_da_quatro_fontes_e_66_7_por_cento(self):
        g = GD.grafo(nove_da_primeira_rodada())
        self.assertEqual(9, g["EXTERNAL_SIGNAL_COUNT"])
        self.assertEqual(9, g["EVIDENCE_BASE_COUNT"])
        self.assertEqual(4, g["INDEPENDENT_SOURCE_COUNT"])
        self.assertEqual("myfruit.it", g["DOMINANT_SOURCE"])
        self.assertEqual(6, g["DOMINANT_SOURCE_SIGNALS"])
        self.assertEqual(66.7, g["DOMINANT_SOURCE_SHARE_PCT"])
        # os dois SOURCE_ID do mesmo site ficam na MESMA familia
        self.assertEqual(["IT-T6-MF", "IT-T6-MF-B"], g["SOURCE_FAMILIES"][0]["SOURCE_IDS"])

    def test_seis_paginas_do_mesmo_site_nao_convergem(self):
        g = GD.grafo(nove_da_primeira_rodada()[:6])
        self.assertEqual(1, g["INDEPENDENT_SOURCE_COUNT"])
        self.assertEqual(100.0, g["DOMINANT_SOURCE_SHARE_PCT"])
        self.assertEqual(GD.NAO_CONVERGE, g["CONVERGENCE"])

    def test_republicacao_declarada_e_do_originador(self):
        g = GD.grafo([sin("A", "https://www.ansa.it/nota", sha="1"),
                      sin("B", "https://www.myfruit.it/copia", sha="2",
                          REPUBLISHED_FROM="https://www.ansa.it/nota")])
        self.assertEqual(1, g["INDEPENDENT_SOURCE_COUNT"])
        self.assertEqual(GD.NAO_CONVERGE, g["CONVERGENCE"])

    def test_os_mesmos_bytes_em_dois_dominios_sao_uma_fonte(self):
        g = GD.grafo([sin("A", "https://a.it/n", sha="igual"),
                      sin("B", "https://b.it/n", sha="igual")])
        self.assertEqual(1, g["EVIDENCE_BASE_COUNT"])
        self.assertEqual(1, g["INDEPENDENT_SOURCE_COUNT"])

    def test_o_mesmo_source_id_une_dominios(self):
        g = GD.grafo([sin("A", "https://a.it/n", sid="IT-T1-1"),
                      sin("B", "https://b.it/n", sid="IT-T1-1")])
        self.assertEqual(1, g["INDEPENDENT_SOURCE_COUNT"])

    def test_dois_canais_do_youtube_sao_duas_fontes_e_watch_nao_diz_quem(self):
        g = GD.grafo([sin("A", "https://www.youtube.com/@canale1/videos"),
                      sin("B", "https://www.youtube.com/@canale2")])
        self.assertEqual(2, g["INDEPENDENT_SOURCE_COUNT"])
        g = GD.grafo([sin("A", "https://www.youtube.com/watch?v=1"),
                      sin("B", "https://www.youtube.com/watch?v=2")])
        self.assertEqual(GD.NAO_SEI, g["INDEPENDENT_SOURCE_COUNT"])
        self.assertEqual(GD.NAO_SEI, g["CONVERGENCE"])

    def test_anuncios_de_paginas_diferentes_sao_anunciantes_diferentes(self):
        """Forma real do pacote V2.1: 351 anuncios com SOURCE_ID SRC_FACEBOOK_COM.
        A plataforma nao e quem fala; a pagina do anunciante e."""
        ads = "https://www.facebook.com/ads/library/?id="
        g = GD.grafo([sin("A1", ads + "1", SOURCE_IDS=["SRC_FACEBOOK_COM"], PAGE_ID="100452355885332"),
                      sin("A2", ads + "2", SOURCE_IDS=["SRC_FACEBOOK_COM"], PAGE_ID="100452355885332"),
                      sin("B1", ads + "3", SOURCE_IDS=["SRC_FACEBOOK_COM"], PAGE_ID="1741459832625091")])
        self.assertEqual(2, g["INDEPENDENT_SOURCE_COUNT"])
        self.assertEqual(GD.CONVERGE, g["CONVERGENCE"])

    def test_a_biblioteca_de_anuncios_sem_pagina_nao_e_um_anunciante(self):
        ads = "https://www.facebook.com/ads/library/?id="
        g = GD.grafo([sin("A1", ads + "1"), sin("A2", ads + "2")])
        self.assertNotIn("facebook.com/ads", [f["ORIGINADOR"] for f in g["SOURCE_FAMILIES"]])
        self.assertEqual(GD.NAO_SEI, g["CONVERGENCE"])

    def test_doi_org_nao_e_quem_escreve(self):
        """Forma real do pacote V2.1: 86 de 88 registos cientificos em doi.org com
        SOURCE_ID SRC_DOI_ORG. Quem fala e a instituicao; sem ela, NAO SEI."""
        g = GD.grafo([sin("S1", "https://doi.org/10.3390/a", SOURCE_IDS=["SRC_DOI_ORG"],
                          INSTITUTION="University of Milan"),
                      sin("S2", "https://doi.org/10.3390/b", SOURCE_IDS=["SRC_DOI_ORG"],
                          INSTITUTION="University of Milan"),
                      sin("S3", "https://doi.org/10.1094/c", SOURCE_IDS=["SRC_DOI_ORG"],
                          INSTITUTION="Instituto de Agricultura Sostenible")])
        self.assertEqual(2, g["INDEPENDENT_SOURCE_COUNT"])
        self.assertNotIn("doi.org", [f["ORIGINADOR"] for f in g["SOURCE_FAMILIES"]])
        g = GD.grafo([sin("S1", "https://doi.org/10.3390/a", SOURCE_IDS=["SRC_DOI_ORG"]),
                      sin("S2", "https://doi.org/10.3390/b", SOURCE_IDS=["SRC_DOI_ORG"])])
        self.assertEqual(GD.NAO_SEI, g["INDEPENDENT_SOURCE_COUNT"])
        self.assertEqual(GD.NAO_SEI, g["CONVERGENCE"])

    def test_sufixo_gov_it_nao_funde_ministerios(self):
        g = GD.grafo([sin("A", "https://www.salute.gov.it/a"),
                      sin("B", "https://www.politicheagricole.gov.it/b")])
        self.assertEqual(2, g["INDEPENDENT_SOURCE_COUNT"])


# ══════════════════════════════════════════════════════════════════════════════
class ConvergenciaSoComIndependencia(unittest.TestCase):

    def test_controle_positivo_duas_fontes_distintas_convergem(self):
        g = GD.grafo([sin("A", "https://a.it/1"), sin("B", "https://b.it/1")])
        self.assertEqual(GD.CONVERGE, g["CONVERGENCE"])
        self.assertEqual(50.0, g["DOMINANT_SOURCE_SHARE_PCT"])

    def test_sem_originador_e_nao_sei_com_minimo_e_maximo(self):
        g = GD.grafo([sin("A", "https://a.it/1"), {"ID": "X", "MARCA": S}])
        self.assertEqual(GD.NAO_SEI, g["INDEPENDENT_SOURCE_COUNT"])
        self.assertEqual((1, 2), (g["INDEPENDENT_SOURCE_COUNT_MIN"],
                                  g["INDEPENDENT_SOURCE_COUNT_MAX"]))
        self.assertEqual(GD.NAO_SEI, g["CONVERGENCE"])
        self.assertEqual(["X"], g["SEM_ORIGINADOR"])

    def test_nao_sei_escrito_por_extenso_nao_e_originador(self):
        g = GD.grafo([sin("A", "https://a.it/1"),
                      {"ID": "X", "SOURCE_ID": "NAO SEI — nao veio", "URL": "NAO SEI"}])
        self.assertEqual(GD.NAO_SEI, g["INDEPENDENT_SOURCE_COUNT"])

    def test_validacao_estrutural_nao_e_fonte(self):
        rot = lambda e: e.get("ENTITY_TYPE") in ("LABEL", "REGISTRY")      # noqa: E731
        g = GD.grafo([sin("S", "https://a.it/1"),
                      sin("L", "https://b.it/r", ENTITY_TYPE="LABEL"),
                      sin("R", "https://c.it/r", ENTITY_TYPE="REGISTRY")], rot)
        self.assertEqual(2, g["STRUCTURAL_VALIDATION_COUNT"])
        self.assertEqual(1, g["INDEPENDENT_SOURCE_COUNT"])
        self.assertEqual(GD.NAO_CONVERGE, g["CONVERGENCE"])

    def test_vazio_nao_converge(self):
        g = GD.grafo([])
        self.assertEqual((0, GD.NAO_CONVERGE), (g["EXTERNAL_SIGNAL_COUNT"], g["CONVERGENCE"]))

    def test_por_fato_fontes_distintas_em_fatos_distintos_nao_convergem(self):
        ev = [sin("A", "https://a.it/1", F="peronospora|vite"),
              sin("B", "https://b.it/1", F="oidio|vite"),
              sin("C", "https://c.it/1"), sin("D", "https://d.it/1")]
        pf = GD.por_fato(ev, lambda e: e.get("F"))
        self.assertEqual(GD.NAO_CONVERGE, pf["peronospora|vite"]["CONVERGENCE"])
        self.assertEqual(GD.NAO_CONVERGE, pf["oidio|vite"]["CONVERGENCE"])
        self.assertEqual(GD.NAO_SEI, pf[GD.NAO_SEI]["CONVERGENCE"],
                         "duas fontes sobre um fato desconhecido nao concordam")


# ══════════════════════════════════════════════════════════════════════════════
def item(ref, url, sha, sid, fato=None):
    """Item SINTETICO no formato do READY, a passar em G0/v2 (INT-CONSERTOS-EXP,
    vivo 278cd489): data com ANO, com BASE e nao posterior a captura."""
    return {"MARCA": S, "ITEM_ID": url, "RAW_OBSERVATION_ID": ref, "SOURCE_ID": sid,
            "FACT_TIME": "2026-09-20", "TEXTO_SHA256": sha,
            "FACT_TIME_BASIS": "SINTETICO · ESCRITO_NO_TEXTO · DATE_EXACT",
            "CAPTURED_AT": "2026-09-25T10:00:00Z",
            "FATO": fato if fato is not None else "NAO_SE_APLICA"}


if __name__ == "__main__":
    unittest.main()
