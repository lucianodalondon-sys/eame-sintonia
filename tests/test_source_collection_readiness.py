#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOURCE-COLLECTION-READINESS-V1 — as guardas do censo e do coletor generico.

O que estas provas impedem de voltar:

  1. o censo gravado divergir do que o codigo/runtime produz hoje (drift);
  2. o indice gerado («a maquina busca?») ser lido como readiness — medido:
     1 «sim» em 6 fontes que o runtime provou;
  3. uma fonte ficar READY sem canario nem fluxo observado;
  4. um SOURCE_ID nascer na tabela declarativa em vez de no Atlas;
  5. um contrato generico entrar sem as regras que a guarda dos contratos exige;
  6. a descoberta generica devolver a propria entrada, uma pagina 2 de listagem
     ou um .css como se fosse documento (landing page nao e documento);
  7. os quatro contadores serem fundidos ou «acertados» para bater;
  8. um blocker fora do vocabulario fechado;
  9. observacoes sem identidade colapsarem num «documento mudou no lugar».
"""
import io
import json
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "provas"))
import _gavetas  # noqa: E402,F401

import medir_source_collection_readiness as msc  # noqa: E402

JSON = os.path.join(RAIZ, "data", "derivados", "SOURCE-COLLECTION-READINESS-V1.json")
TABELA = os.path.join(RAIZ, "regras", "italy_contracts_onboarded.json")
COLETOR = os.path.join(RAIZ, "coleta", "italy_pilot_collect.mjs")
LEDGER = os.path.join(RAIZ, "data", "collection-ledger", "italy", "observations.ndjson")


def _json(p):
    with io.open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _node(guiao: str) -> dict:
    r = subprocess.run(["node", "--input-type=module", "-e", guiao], capture_output=True,
                       text=True, encoding="utf-8", cwd=RAIZ, timeout=120)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-800:])
    return json.loads(r.stdout)


class OCensoNaoMente(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gravado = _json(JSON)
        cls.vivo = msc.medir()

    def test_1_o_censo_gravado_e_o_que_o_codigo_produz_hoje(self):
        self.assertEqual(self.gravado["RESUMO"], self.vivo["RESUMO"],
                         "o JSON gravado ficou para tras: corra py provas/medir_source_collection_readiness.py")
        chave = lambda d: [(l["SOURCE_ID"], l["TECHNICALLY_COLLECTION_READY"], l["BLOCKER"]) for l in d["FONTES"]]
        self.assertEqual(chave(self.gravado), chave(self.vivo))

    def test_2_o_indice_nao_e_owner_do_readiness(self):
        seis = self.vivo["CONTRAPROVA_AS_SEIS"]
        self.assertEqual(sorted(seis), sorted(msc.AS_SEIS_DA_BIG_COLLECTION))
        for sid, v in seis.items():
            self.assertTrue(v["FLOW_OBSERVED"], "%s: a Big Collection deixou observacao HEALTHY com bytes" % sid)
        diz_sim = sum(1 for v in seis.values() if v["INDICE_A_MAQUINA_BUSCA"] == "sim")
        self.assertEqual(diz_sim, 1, "o indice marca «sim» em 1 das 6 (IT-T4-001) — medido no ADDENDUM-01")
        self.assertEqual(self.vivo["RESUMO"]["INDEX_COLLECTION_READINESS_STALE"], "YES")
        por_id = {l["SOURCE_ID"]: l for l in self.vivo["FONTES"]}
        for sid in seis:
            self.assertEqual(por_id[sid]["TECHNICALLY_COLLECTION_READY"], "YES", sid)

    def test_3_nenhuma_fonte_e_ready_sem_prova_de_execucao(self):
        for l in self.vivo["FONTES"]:
            if l["TECHNICALLY_COLLECTION_READY"] != "YES":
                continue
            self.assertTrue(l["CANARY_STATE"] == "PASS" or (l["FLOW_OBSERVED"] == "YES" and l["SOURCE_ID"] in msc.CAPACIDADE_ANTES),
                            "%s READY sem canario nem fluxo observado" % l["SOURCE_ID"])
            self.assertTrue(all(l["CRITERIOS_16"].values()), l["SOURCE_ID"])
            self.assertEqual(l["BLOCKER"], "", l["SOURCE_ID"])

    def test_3b_ready_e_executavel_sao_perguntas_diferentes(self):
        R = self.vivo["RESUMO"]
        self.assertLessEqual(R["BIG_COLLECTION_EXECUTABLE_AFTER"], R["RELEVANCE_SIM"])
        self.assertLessEqual(R["BIG_COLLECTION_EXECUTABLE_AFTER"], R["SOURCE_COLLECTION_READY_AFTER"])
        for l in self.vivo["FONTES"]:
            if l["BIG_COLLECTION_EXECUTABLE"] == "YES":
                self.assertEqual(l["RELEVANCE_STATE"], "SIM", l["SOURCE_ID"])
                self.assertEqual(l["TECHNICALLY_COLLECTION_READY"], "YES", l["SOURCE_ID"])

    def test_7_os_quatro_contadores_ficam_separados(self):
        C = self.vivo["OS_QUATRO_CONTADORES"]
        self.assertEqual(list(C), ["ATLAS_FICHAS", "ATLAS_HEADER_STAMP", "ESCADA_REGISTADA", "CONTRATOS_DECLARADOS"])
        self.assertEqual(len({v["OWNER"] for v in C.values()}), 4, "quatro contadores, quatro owners")
        for k, v in C.items():
            self.assertIsNotNone(v["VALOR"], k)
            self.assertIn("STALE", v)
        # o indice diz 5 e o runtime diz mais: o contador NAO foi acertado para bater
        self.assertGreaterEqual(C["CONTRATOS_DECLARADOS"]["VALOR"], self.vivo["RESUMO"]["DECLARED_CONTRACT"],
                                "o contador conta o atlas inteiro; o resumo so IT+EU")
        self.assertNotEqual(C["CONTRATOS_DECLARADOS"]["VALOR"], self.vivo["RESUMO"]["SOURCE_COLLECTION_READY_AFTER"])
        self.assertNotEqual(C["ATLAS_FICHAS"]["VALOR"], C["ATLAS_HEADER_STAMP"]["VALOR"],
                            "a divergencia 210/190 e decisao humana; nao se acerta aqui")

    def test_8_todo_blocker_esta_no_vocabulario(self):
        for l in self.vivo["FONTES"]:
            if l["BLOCKER"]:
                self.assertIn(l["BLOCKER"], msc.BLOCKERS, l["SOURCE_ID"])
            self.assertIn(l["ACCESS_SHAPE"], msc.SHAPES, l["SOURCE_ID"])


class ATabelaNaoInventaFonte(unittest.TestCase):
    def test_4_todo_source_id_da_tabela_vem_do_atlas(self):
        fichas = msc.fichas_do_atlas()
        linhas = _json(TABELA)["FONTES"]
        ids = [l["SOURCE_ID"] for l in linhas]
        self.assertEqual(len(ids), len(set(ids)), "SOURCE_ID repetido na tabela")
        for sid in ids:
            self.assertIn(sid, fichas, "%s nao tem ficha no Atlas — a tabela nao cunha identidade" % sid)
        for sid in ("IT-T3-005", "IT-T2-002", "IT-T2-004", "IT-T3-002", "IT-T3-010", "IT-T3-008", "IT-T4-001"):
            self.assertNotIn(sid, ids, "os sete do piloto tem codigo proprio; nao entram na tabela")

    def test_5_todo_contrato_generico_cumpre_as_guardas_dos_contratos(self):
        K = msc.contratos_e_capacidade()
        genericos = [(i, c) for i, c in K["CONTRACTS"].items() if c["ACQUISITION"] and not c["A_MAO"]]
        self.assertGreater(len(genericos), 50)
        for sid, c in genericos:
            self.assertTrue(c["DOCUMENT_ID_RULE"], sid)
            self.assertNotIn("SHA", c["DOCUMENT_ID_RULE"].upper(), sid)
            self.assertTrue(c["FAIL_CLOSED_RULE"], sid)
            self.assertTrue(c["NEGATIVE_CONTROL"], sid)
            self.assertIn(c["ROUTE_TYPE"], ("STATIC_ROUTE", "PREDICTABLE_ROUTE", "DISCOVERED_ROUTE", "APPLICATION_ROUTE", "BROWSER_DISCOVERED_ROUTE"), sid)
            self.assertIn(c["ACQUISITION"]["SHAPE"], ("PDF_DISCOVERY_PAGE", "HTML_ARTICLE_DISCOVERY", "PDF_DIRECT"), sid)
            self.assertTrue(str(c["ACQUISITION"]["ENTRY_URL"]).startswith("http"), sid)
        # e a capacidade do coletor e exactamente os sete mais a tabela
        self.assertEqual(sorted(K["FONTES_PERCORRIVEIS"]), sorted(set(K["PILOT_SOURCES"]) | {i for i, c in K["CONTRACTS"].items() if c["ACQUISITION"]}))


class ADescobertaNaoRegistaLandingPage(unittest.TestCase):
    def test_6_a_entrada_a_paginacao_e_os_ativos_nunca_sao_documento(self):
        guiao = (
            "const m = await import(%s);\n"
            "const html = `<a href='/'>home</a><a href='/news/'>lista</a><a href='/news/page/2/'>pag2</a>"
            "<a href='/news/artigo-longo-2026'>art</a><a href='/static/app.css'>css</a><a href='/news/feed.xml'>xml</a>"
            "<a href='https://outro.example/news/artigo-x-y'>fora</a><a href='/docs/boletim.pdf/view'>plone</a>`;\n"
            "const aq = {ENTRY_URL: 'https://x.example/news/', LINK_PATTERN: null, SAME_HOST: true, STRIP_SUFFIX: '/view'};\n"
            "process.stdout.write(JSON.stringify(m.linksDaEntrada(html, aq.ENTRY_URL, aq)));\n"
            % json.dumps("file:///" + COLETOR.replace("\\", "/")))
        links = _node(guiao)
        self.assertNotIn("https://x.example/news/", links, "a propria entrada nunca e documento")
        self.assertFalse(any("/page/2" in u for u in links), "pagina 2 de uma listagem e listagem")
        self.assertFalse(any(u.endswith(".css") or u.endswith(".xml") for u in links))
        self.assertFalse(any("outro.example" in u for u in links), "SAME_HOST")
        self.assertIn("https://x.example/news/artigo-longo-2026", links)
        self.assertIn("https://x.example/docs/boletim.pdf", links, "o sufixo /view do Plone e removido")
        self.assertNotIn("https://x.example/docs/boletim.pdf/view", links)

    def test_9_sem_identidade_nao_ha_mudou_no_lugar_nem_alvo_resolvido(self):
        if not os.path.isfile(LEDGER):
            self.skipTest("sem ledger")
        vistas = 0
        with io.open(LEDGER, encoding="utf-8") as fh:
            for linha in fh:
                linha = linha.strip()
                if not linha:
                    continue
                o = json.loads(linha)
                if o.get("DOCUMENT_ID") != "NAO SEI":
                    continue
                vistas += 1
                self.assertNotIn(o.get("OBSERVATION_RESULT"), ("DOCUMENT_CHANGED_IN_PLACE", "SEMANTIC_ID_CHANGED_SAME_BYTES"), o.get("RUN_ID"))
                self.assertNotIn("RESOLVED_STRUCTURED_TARGET", o, o.get("RUN_ID"))
                self.assertIn("DOCUMENT_ID_BASE", o, o.get("RUN_ID"))
        self.assertGreater(vistas, 0, "os canarios genericos deixaram observacoes sem identidade no ledger")


if __name__ == "__main__":
    unittest.main()
