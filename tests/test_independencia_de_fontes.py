#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""INDEPENDENCIA DE FONTES, ATACADA — missao INDEPENDENCIA-V1 (D12 e D16).

    python3 -m unittest tests.test_independencia_de_fontes -v

    D12  o mesmo documento lido duas vezes contava como duas evidencias.
    D16  o motor nao contava fontes independentes (6 de 9 sinais de myfruit.it).

Os casos SINTETICOS vao marcados `SINTETICO` no proprio item: a Sala real nao
existe nesta arvore. O unico caso real e a coorte da Sala de 14/09
(`research/intelligence/COORTE-DA-SALA-2026-09-14.json`): 6 itens, 6 documentos,
3 originadores.
"""
import json
import os
import shutil
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in (RAIZ, RAIZ / "motor", RAIZ / "provas"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import grafo_de_dependencia as GD                           # noqa: E402
import corrida_da_inteligencia as CI                        # noqa: E402

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
    """Item SINTETICO no formato do READY, a passar em G0."""
    return {"MARCA": S, "ITEM_ID": url, "RAW_OBSERVATION_ID": ref, "SOURCE_ID": sid,
            "FACT_TIME": "2026-09-20", "TEXTO_SHA256": sha,
            "FATO": fato if fato is not None else "NAO_SE_APLICA"}


class NaCorridaDaInteligencia(unittest.TestCase):
    P = "quantas fontes independentes sustentam este sinal?"

    def test_d12_na_corrida_o_mesmo_documento_e_uma_evidencia(self):
        livro = CI.correr(self.P, [item("O1", "https://x.it/b", "s", "IT-T3-1"),
                                   item("O2", "https://x.it/b", "s", "IT-T3-1")])
        d = livro["DEPENDENCIA"]["GERAL"]
        self.assertEqual(2, len(livro["SIGNALS"]), "a linhagem nao perde leituras")
        self.assertEqual(1, d["EVIDENCE_BASE_COUNT"])
        self.assertEqual(1, d["INDEPENDENT_SOURCE_COUNT"])
        self.assertIsNone(livro["SIGNALS"][0]["DUPLICATA_DE"])
        self.assertEqual(livro["SIGNALS"][0]["SIGNAL_ID"], livro["SIGNALS"][1]["DUPLICATA_DE"])
        self.assertEqual(0, livro["COLLECTOR_CALLS"])

    def test_d16_na_corrida_a_fonte_dominante_aparece(self):
        itens = [item(e["ID"], e["URL"], e["SHA256"], e.get("SOURCE_ID", "IT-X-" + e["ID"]))
                 for e in nove_da_primeira_rodada()]
        livro = CI.correr(self.P, itens)
        d = livro["DEPENDENCIA"]["GERAL"]
        self.assertEqual(9, d["EXTERNAL_SIGNAL_COUNT"])
        self.assertEqual(4, d["INDEPENDENT_SOURCE_COUNT"])
        self.assertEqual("myfruit.it", d["DOMINANT_SOURCE"])
        self.assertEqual(66.7, d["DOMINANT_SOURCE_SHARE_PCT"])

    def test_por_fato_na_corrida(self):
        f = {"subject": "vite", "predicate": "peronospora"}
        livro = CI.correr(self.P, [item("O1", "https://a.it/1", "1", "IT-A", f),
                                   item("O2", "https://b.it/1", "2", "IT-B", dict(f)),
                                   item("O3", "https://c.it/1", "3", "IT-C")])
        pf = livro["DEPENDENCIA"]["POR_FATO"]
        self.assertEqual(GD.CONVERGE, pf["vite|peronospora"]["CONVERGENCE"])
        self.assertEqual(GD.NAO_CONVERGE, pf[GD.NAO_SEI]["CONVERGENCE"])

    def test_o_bloqueado_em_g0_nao_entra_na_conta(self):
        mau = item("O2", "https://b.it/1", "2", "IT-B")
        mau["FACT_TIME"] = "NAO SEI"
        livro = CI.correr(self.P, [item("O1", "https://a.it/1", "1", "IT-A"), mau])
        self.assertEqual(1, livro["DEPENDENCIA"]["GERAL"]["EXTERNAL_SIGNAL_COUNT"])

    def test_sem_sinais_o_grafo_diz_zero_e_nao_converge(self):
        livro = CI.correr(self.P, [])
        self.assertEqual("EMPTY_RESULT", livro["RESULT_STATE"])
        self.assertEqual(0, livro["DEPENDENCIA"]["GERAL"]["EXTERNAL_SIGNAL_COUNT"])

    def test_o_reuso_leva_o_mesmo_grafo(self):
        itens = [item("O1", "https://a.it/1", "1", "IT-A")]
        a = CI.correr(self.P, itens)
        b = CI.correr(self.P, itens, ja_corridas={a["INTELLIGENCE_RUN_ID"]: a})
        self.assertEqual("REUSED", b["RESULT_STATE"])
        self.assertEqual(a["DEPENDENCIA"], b["DEPENDENCIA"])


# ══════════════════════════════════════════════════════════════════════════════
class NoMotorV21(unittest.TestCase):
    """O motor de oportunidades sobre o pacote REAL (ZIP versionado). Sem o ZIP
    e SKIP declarado."""

    @classmethod
    def setUpClass(cls):
        from tests.test_completude_oportunidade import _prepara_ingest, ING
        ok, cls._limpar = _prepara_ingest()
        cls._ing = ING
        if not ok:
            raise unittest.SkipTest("DESIGN-INGEST indisponivel (sem ZIP no disco)")
        import v21_oportunidades as M
        cls.M = M
        cls.brutos = M.main()[0]

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "_limpar", False):
            shutil.rmtree(os.path.dirname(cls._ing), ignore_errors=True)

    def test_multi_source_nunca_passa_das_fontes_independentes(self):
        for o, _ in self.brutos:
            dep = o["DEPENDENCY_GRAPH"]
            teto = min(2, dep["INDEPENDENT_SOURCE_COUNT_MIN"])
            self.assertLessEqual(o["SCORE_DIMENSIONS"]["MULTI_SOURCE"], teto, o["ID"])
            self.assertEqual(self.M.score(o["SCORE_DIMENSIONS"]), o["OPPORTUNITY_SCORE"], o["ID"])

    def test_o_valor_declarado_fica_ao_lado(self):
        """INT-LAW-093: score nao substitui decomposicao."""
        for o, _ in self.brutos:
            self.assertIn("MULTI_SOURCE_DECLARED", o, o["ID"])
            self.assertGreaterEqual(o["MULTI_SOURCE_DECLARED"],
                                    o["SCORE_DIMENSIONS"]["MULTI_SOURCE"], o["ID"])

    def test_rotulo_nao_conta_como_fonte(self):
        for o, apoios in self.brutos:
            n_rot = sum(1 for a in apoios if a.get("ENTITY_TYPE") in self.M.TIPOS_ESTRUTURAIS)
            self.assertEqual(n_rot, o["DEPENDENCY_GRAPH"]["STRUCTURAL_VALIDATION_COUNT"], o["ID"])

    def test_o_registo_gravado_leva_as_quatro_metricas(self):
        regs = self.M.gravar(self.brutos, *self.M.main()[2:4])[0]
        for r in regs:
            for k in ("EXTERNAL_SIGNAL_COUNT", "INDEPENDENT_SOURCE_COUNT",
                      "STRUCTURAL_VALIDATION_COUNT", "EVIDENCE_BASE_COUNT",
                      "DOMINANT_SOURCE_SHARE_PCT", "CONVERGENCE"):
                self.assertIn(k, r["DEPENDENCY_GRAPH"], r["ID"])


if __name__ == "__main__":
    unittest.main()
