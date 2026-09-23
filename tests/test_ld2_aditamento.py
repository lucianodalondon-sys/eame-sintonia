"""LD2 — o aditamento V3 entra pelo MESMO pacote G1, com a MESMA prova.

As provas usam bytes fora do Git (~/detector-capa-gabarito); sem eles, os testes
que precisam de prova saltam (declarado), os de estrutura correm sempre.
"""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location(
    "aplicar_desbloqueio", RAIZ / "scripts" / "desbloqueio" / "aplicar_desbloqueio.py")
PK = importlib.util.module_from_spec(_s)
_s.loader.exec_module(PK)
V3 = RAIZ / "curadoria" / "PROPOSTA-RECEITAS-V3.json"
TEM_BYTES = (Path.home() / "detector-capa-gabarito" / "MANIFESTO.json").exists()


class TestAditamentoV3(unittest.TestCase):
    def test_o_pacote_le_a_v3(self):
        vindas = {(p["SOURCE_ID"], p["CAMPO"]) for o, p in PK.propostas()
                  if o == "PROPOSTA-RECEITAS-V3.json"}
        self.assertIn(("IT-T2-039", "ACQUISITION.LINK_PATTERN"), vindas)
        self.assertIn(("IT-T5-049", "ACQUISITION.LINK_PATTERN"), vindas)

    def test_v3_nao_propoe_nada_sem_prova(self):
        d = json.loads(V3.read_text(encoding="utf-8"))
        for l in d["FONTES"]:
            for p in l["PROPOSTAS"]:
                self.assertTrue(p["PROVA"].get("MATERIAS_CONFIRMADAS"), l["SOURCE_ID"])
            if not l["PROPOSTAS"]:
                self.assertTrue((l.get("SEM_PROPOSTA") or "").startswith("NAO SEI")
                                or l.get("SEM_PROPOSTA_INDEX"), l["SOURCE_ID"])

    def test_it_t11_010_fica_nao_sei_com_o_que_falta(self):
        d = {l["SOURCE_ID"]: l for l in json.loads(V3.read_text(encoding="utf-8"))["FONTES"]}
        l = d["IT-T11-010"]
        self.assertEqual(l["PROPOSTAS"], [])
        self.assertIn("minimo do G1 = 10", l["SEM_PROPOSTA_INDEX"])

    @unittest.skipUnless(TEM_BYTES, "bytes do gabarito fora desta maquina")
    def test_cada_receita_v3_passa_a_prova_do_g1(self):
        guardadas, capas, gen = PK.paginas_guardadas(), PK.capas_do_gabarito(), PK.guarda()
        d = json.loads(V3.read_text(encoding="utf-8"))
        for l in d["FONTES"]:
            for p in l["PROPOSTAS"]:
                livro_c = {"ACQUISITION": {"INDEX_URL": l.get("INDEX_URL", "")}}
                self.assertIsNone(PK.provar_padrao(p, livro_c, guardadas, capas, gen), l["SOURCE_ID"])

    @unittest.skipUnless(TEM_BYTES, "bytes do gabarito fora desta maquina")
    def test_padrao_generico_na_v3_seria_recusado(self):
        guardadas, capas, gen = PK.paginas_guardadas(), PK.capas_do_gabarito(), PK.guarda()
        p = {"DEPOIS": r"^https?://(www\.)?arpae\.it/.*$",
             "PROVA": {"MATERIAS_CONFIRMADAS": [
                 "https://www.arpae.it/it/notizie/copy_of_monitoraggio-pollini-e-spore-alternaria-ovunque"]}}
        e = PK.provar_padrao(p, {"ACQUISITION": {"INDEX_URL": "https://www.arpae.it/it/notizie"}},
                             guardadas, capas, gen)
        self.assertIsNotNone(e)



_s2 = importlib.util.spec_from_file_location(
    "propor_receitas_v3", RAIZ / "scripts" / "receitas" / "propor_receitas_v3.py")
PV3 = importlib.util.module_from_spec(_s2)
_s2.loader.exec_module(PV3)


class TestEntradaDaV3(unittest.TestCase):
    def _p(self, url, papel, veredito):
        return {"URL": url, "PAPEL": papel, "VEREDITO": veredito}

    def test_a_pagina_do_indice_de_hoje_e_a_entrada(self):
        ps = [self._p("https://a.it/velho", "CAPA_INDICE", "MATERIA"),
              self._p("https://a.it/news", "CAPA_INDICE", "CAPA")]
        out = PV3._entrada_primeiro(ps, "https://a.it/news/")
        self.assertEqual(out[0]["URL"], "https://a.it/news")
        self.assertEqual([p["PAPEL"] for p in out[1:]], ["CAPA_ANTIGO_INDICE"])

    def test_sem_pagina_de_hoje_uma_listagem_antiga_serve(self):
        ps = [self._p("https://a.it/notizie", "CAPA_INDICE", "CAPA"),
              self._p("https://a.it/notizie/x", "MATERIA", "MATERIA")]
        out = PV3._entrada_primeiro(ps, "https://a.it/")
        self.assertEqual(out[0]["PAPEL"], "CAPA_INDICE")

    def test_uma_materia_nunca_e_entrada(self):
        ps = [self._p("https://a.it/fiera-2026", "CAPA_INDICE", "MATERIA")]
        out = PV3._entrada_primeiro(ps, "https://a.it/")
        self.assertFalse([p for p in out if p["PAPEL"] == "CAPA_INDICE"])


if __name__ == "__main__":
    unittest.main()
