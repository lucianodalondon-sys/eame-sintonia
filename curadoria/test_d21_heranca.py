#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D21 — o canal YouTube herda o território do site da MESMA organização.

Condições da D21 (DECISOES-DONO-2026-09-23, linha 199), cada uma com teste:
  · ligação oficial canal<->site escrita na ficha  -> herda;
  · sem ligação                                   -> NAO SEI;
  · nome ou logotipo iguais, sem ligação           -> NAO SEI;
  · o site sem SOURCE_ID na casa                   -> NAO SEI;
  · o site em dois territórios (conflito)          -> NAO SEI.
Tudo com livros em memória ou em pasta temporária: não toca a lane real.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))

import fila as F                      # noqa: E402
import fonte_nova as FN               # noqa: E402
import lifecycle as LC                # noqa: E402
import rota_do_scrap_youtube as RSY   # noqa: E402
import worker as W                    # noqa: E402

CANAL = "UCXUG407gp3CnWnfS3ycijhA"


def _livro(*linhas):
    return {"FONTES": [{"SOURCE_ID": sid, "TERRITORY": t, "CANONICAL_ENTRY_URL": url,
                        "ACQUISITION": {"INDEX_URL": url}} for sid, t, url in linhas]}


VAZIO = {"FONTES": []}
ATLAS = "#### IT-T3-020 · Societa\n```\nTERRITORY:                    T3\nURL:  https://www.sei.it/\n```\n"


def _ficha(onde="", nota="", nome="Org — Youtube ufficiale"):
    return {"TIPO": "YOUTUBE", "NOME": nome, "PAIS": "IT",
            "URL": "https://www.youtube.com/channel/%s" % CANAL, "ONDE_VIU": onde, "NOTA": nota}


class AHeranca(unittest.TestCase):
    def _h(self, ficha, livro=VAZIO, atlas=""):
        return RSY.heranca_do_site(ficha, tabela=VAZIO, livro=livro, atlas_texto=atlas)

    def test_declarado_no_site_oficial_herda(self):
        t, p = self._h(_ficha(onde="declarado no site oficial do dono: https://www.org.it/"),
                       livro=_livro(("IT-T5-046", "T5", "https://www.org.it/news")))
        self.assertEqual(t, "T5")
        self.assertEqual(p["SOURCE_IDS_DO_SITE"], ["IT-T5-046"])

    def test_link_tirado_pelo_crawler_do_site_herda(self):
        t, _ = self._h(_ficha(onde="https://www.org.it/",
                              nota="DISCOVERED_FROM=https://www.org.it/ | DISCOVERY_METHOD=CRAWL_LINK | X"),
                       livro=_livro(("IT-T2-001", "T2", "https://org.it/")))
        self.assertEqual(t, "T2")

    def test_o_atlas_tambem_prova_o_territorio_do_site(self):
        t, _ = self._h(_ficha(onde="declarado no site oficial do dono: https://www.sei.it/"), atlas=ATLAS)
        self.assertEqual(t, "T3")

    def test_sem_ligacao_e_nao_sei(self):
        t, p = self._h(_ficha(onde="https://www.org.it/"),
                       livro=_livro(("IT-T5-046", "T5", "https://www.org.it/")))
        self.assertIsNone(t)
        self.assertIn("sem ligacao oficial", p["PORQUE"], "o motivo diz QUAL condicao faltou")

    def test_nome_igual_nao_basta(self):
        t, _ = self._h(_ficha(nome="Olio Officina — Youtube ufficiale"),
                       livro=_livro(("IT-T5-046", "T5", "https://www.olioofficina.it/")))
        self.assertIsNone(t)

    def test_crawl_que_nao_e_crawl_link_nao_conta(self):
        t, _ = self._h(_ficha(nota="DISCOVERED_FROM=https://www.org.it/ | DISCOVERY_METHOD=SEARCH"),
                       livro=_livro(("IT-T5-046", "T5", "https://www.org.it/")))
        self.assertIsNone(t)

    def test_site_sem_source_id_e_nao_sei(self):
        t, p = self._h(_ficha(onde="declarado no site oficial do dono: https://www.granarolo.it/"))
        self.assertIsNone(t)
        self.assertIn("nao tem SOURCE_ID", p["PORQUE"])

    def test_conflito_de_territorio_e_nao_sei(self):
        t, p = self._h(_ficha(onde="declarado no site oficial do dono: https://www.org.it/"),
                       livro=_livro(("IT-T5-046", "T5", "https://www.org.it/a"),
                                    ("IT-T7-001", "T7", "https://www.org.it/b")))
        self.assertIsNone(t)
        self.assertIn("conflito", p["PORQUE"])

    def test_conflito_entre_livro_e_atlas_tambem(self):
        atlas = ATLAS.replace("www.sei.it", "www.org.it")
        t, _ = self._h(_ficha(onde="declarado no site oficial do dono: https://www.org.it/"),
                       livro=_livro(("IT-T5-046", "T5", "https://www.org.it/")), atlas=atlas)
        self.assertIsNone(t)

    def test_subdominio_nao_e_o_site(self):
        t, _ = self._h(_ficha(onde="declarado no site oficial do dono: https://canale.org.it/"),
                       livro=_livro(("IT-T5-046", "T5", "https://www.org.it/")))
        self.assertIsNone(t)


class OQualifyAplicaAD21(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="d21-")))
        alvos = {(F, "FILA"): "fila.json", (LC, "LIVRO"): "livro.json",
                 (W, "ALLOCATION"): "alloc.json", (W, "EVIDENCIA"): "evid.json",
                 (W, "PULSO"): "pulso.json", (W, "CONTRATOS"): "contratos.json",
                 (FN, "FILA"): "candidatas.json", (RSY, "TABELA"): "tabela.json",
                 (RSY, "LIVRO"): "contratos.json", (RSY, "ALLOCATION"): "alloc.json",
                 (RSY, "CONTRATOS_MJS"): "contratos.mjs", (RSY, "ATLAS"): "atlas.md"}
        for (mod, attr), nome in alvos.items():
            self.addCleanup(setattr, mod, attr, getattr(mod, attr))
            setattr(mod, attr, self.tmp / nome)
        W.ALLOCATION.write_text(json.dumps({"MAIOR_POR_TERRITORIO_ANTES": {"T5": 84}, "NOVAS": []}),
                                encoding="utf-8")
        RSY.TABELA.write_text(json.dumps(VAZIO), encoding="utf-8")
        W.CONTRATOS.write_text(json.dumps(_livro(("IT-T5-046", "T5", "https://www.olioofficina.it/"))),
                               encoding="utf-8")
        RSY.CONTRATOS_MJS.write_text("", encoding="utf-8")
        RSY.ATLAS.write_text("", encoding="utf-8")

    def _qualify(self, cand, onde, tipo="YOUTUBE", url=None):
        doc = FN.carregar()
        doc["CANDIDATAS"].append({"CANDIDATA_ID": cand, "TIPO": tipo, "NOME": "Olio Officina — Youtube ufficiale",
                                  "URL": url or "https://www.youtube.com/channel/%s" % CANAL,
                                  "PAIS": "IT", "ONDE_VIU": onde, "ESTADO": "EM_ANALISE", "SOURCE_ID": None})
        FN.gravar(doc)
        F.enfileirar(cand, F.QUALIFY, priority=30, motivo="teste")
        return W.correr(max_tarefas=1, pausa=0, verboso=False)[0]

    def _novas(self):
        return json.loads(W.ALLOCATION.read_text(encoding="utf-8"))["NOVAS"]

    def test_com_ligacao_aloca_no_territorio_herdado_e_regista_a_prova(self):
        r = self._qualify("CAND-D1", "declarado no site oficial do dono: https://www.olioofficina.it/")
        self.assertEqual(r["RESULTADO"], "OK")
        n = self._novas()
        self.assertEqual([x["SOURCE_ID"] for x in n], ["IT-T5-085"])
        self.assertEqual(n[0]["MESMA_ORGANIZACAO"]["SOURCE_IDS_DO_SITE"], ["IT-T5-046"])
        self.assertIn("D21", n[0]["TERRITORY_REASON"])

    def test_sem_ligacao_fica_semantic(self):
        r = self._qualify("CAND-D2", "https://www.olioofficina.it/")
        self.assertEqual(r["RESULTADO"], "BLOCK")
        self.assertEqual(self._novas(), [])
        self.assertEqual(LC.estado_de("CAND-D2"), LC.SEMANTIC_REVIEW)

    def test_so_vale_para_youtube(self):
        r = self._qualify("CAND-D3", "declarado no site oficial do dono: https://www.olioofficina.it/",
                          tipo="ORGANIZACAO", url="https://www.olio-exemplo.it/")
        self.assertEqual(r["RESULTADO"], "BLOCK")
        self.assertEqual(self._novas(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
