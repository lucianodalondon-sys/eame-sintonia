#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D80 (26/09, dono via bot Luciano) — as tres partes, cada condicao com teste.

  (i)   recusa pela porta, reversivel, com a canonica escrita na duplicada;
        a RECUSADA nao se qualifica.
  (ii)  fora de IT com territorio e identidade provados: prefixo canonico
        (EU-/INT-/FR-...), max+1 sobre o que a casa ja escreveu, nunca recicla,
        e PARA (sem contrato, nunca READY automatico).
  (iii) a pagina herda a classe SO do mesmo site: host exacto, classe unica,
        nunca a raiz; site misto nao herda.

Tudo numa pasta temporaria, pela porta publica do worker: nao toca a lane real.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))

import decisao_semantica as DS        # noqa: E402
import fila as F                      # noqa: E402
import fonte_nova as FN               # noqa: E402
import lifecycle as LC                # noqa: E402
import rota_do_scrap_youtube as RSY   # noqa: E402
import worker as W                    # noqa: E402

CAND = "CAND-9960"
NOME = "Portale Qzxv"                 # nenhuma regra de nome o reconhece


def _decisao(url, pais="EU", territorio="T12", cand=CAND):
    return {"CANDIDATA_ID": cand, "URL": url, "TERRITORIO": territorio, "PAIS": pais,
            "DECIDIDO_POR": "OPUS", "PORQUE": "associacao europeia do sector",
            "PROVAS": [{"PAPEL": "INSTITUCIONAL", "URL": url + "about", "SHA256": "a1" * 32},
                       {"PAPEL": "CONTEUDO", "URL": url + "news/1", "SHA256": "b2" * 32},
                       {"PAPEL": "CONTEUDO", "URL": url + "news/2", "SHA256": "c3" * 32}]}


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="d80-")))
        for mod, attr in ((F, "FILA"), (LC, "LIVRO"), (W, "ALLOCATION"), (W, "EVIDENCIA"),
                          (W, "PULSO"), (W, "CONTRATOS"), (W, "FONTES_DE_NUMEROS"),
                          (FN, "FILA"), (DS, "DECISOES"), (RSY, "TABELA"), (RSY, "LIVRO"),
                          (RSY, "ATLAS")):
            self.addCleanup(setattr, mod, attr, getattr(mod, attr))
        F.FILA = self.tmp / "fila.json"
        LC.LIVRO = self.tmp / "livro.json"
        W.ALLOCATION = self.tmp / "alloc.json"
        W.EVIDENCIA = self.tmp / "evid.json"
        W.PULSO = self.tmp / "WORKER-HEARTBEAT.json"
        FN.FILA = self.tmp / "candidatas.json"
        DS.DECISOES = self.tmp / "decisoes.json"
        W.CONTRATOS = RSY.LIVRO = self.tmp / "contratos.json"
        RSY.TABELA = self.tmp / "tabela.json"
        RSY.ATLAS = self.tmp / "atlas.md"
        W.FONTES_DE_NUMEROS = [RSY.ATLAS, self.tmp / "outro_livro.json"]
        W.ALLOCATION.write_text(json.dumps({
            "DATASET": "SOURCE-ID-ALLOCATION-V1",
            "MAIOR_POR_TERRITORIO_ANTES": {"T12": 7, "T5": 40, "T7": 40},
            "ATRIBUIDOS": 0, "NOVAS": []}), encoding="utf-8")
        self.livro([])
        RSY.TABELA.write_text(json.dumps({"FONTES": []}), encoding="utf-8")
        RSY.ATLAS.write_text("", encoding="utf-8")
        self.decisoes([])

    def livro(self, linhas):
        W.CONTRATOS.write_text(json.dumps({"FONTES": [
            {"SOURCE_ID": sid, "TERRITORY": t, "CANONICAL_ENTRY_URL": url,
             "ACQUISITION": {"INDEX_URL": url}} for sid, t, url in linhas]}), encoding="utf-8")

    def decisoes(self, ds):
        DS.DECISOES.write_text(json.dumps({"DATASET": "SEMANTIC-DECISIONS-V1", "DECISOES": ds}),
                               encoding="utf-8")

    def ficha(self, url, cand=CAND, tipo="BASE_OFICIAL", estado="EM_ANALISE"):
        doc = FN.carregar()
        doc["CANDIDATAS"].append({"CANDIDATA_ID": cand, "TIPO": tipo, "NOME": NOME, "URL": url,
                                  "PAIS": "NAO SEI", "ESTADO": estado, "SOURCE_ID": None,
                                  "MOTIVO_DA_RECUSA": None})
        FN.gravar(doc)

    def qualify(self, cand=CAND):
        F.enfileirar(cand, F.QUALIFY, priority=30, motivo="teste")
        return W.correr(max_tarefas=1, pausa=0, verboso=False)[0]

    def alloc(self):
        return json.loads(W.ALLOCATION.read_text(encoding="utf-8"))

    def evidencia(self):
        """O motivo inteiro (o PORQUE do resultado e cortado a 160 letras)."""
        return W.EVIDENCIA.read_text(encoding="utf-8")

    def build_contract_na_fila(self):
        return [t for t in json.loads(F.FILA.read_text(encoding="utf-8"))["TAREFAS"]
                if t["TASK_TYPE"] == F.BUILD_CONTRACT]


# ── (i) ───────────────────────────────────────────────────────────────────────
class RecusaReversivel(_Base):
    URL = "https://www.qzxv.example/contatti"

    def test_recusa_guarda_o_antes_e_a_canonica(self):
        self.ficha(self.URL)
        c = FN.recusar(self.URL, "pagina de contactos da IT-T7-001", duplicada_de="IT-T7-001",
                       decisao="D80(i)")
        self.assertEqual(c["ESTADO"], "RECUSADA")
        self.assertEqual(c["DUPLICADA_DE"], "IT-T7-001")
        self.assertEqual(c["RECUSA_ANTERIOR"], {"ESTADO": "EM_ANALISE", "MOTIVO_DA_RECUSA": None})

    def test_reverter_repoe_o_estado_e_deixa_rasto(self):
        self.ficha(self.URL)
        FN.recusar(self.URL, "nao e fonte", decisao="D80(i)")
        c = FN.reverter_recusa(self.URL, "D80(i)")
        self.assertEqual(c["ESTADO"], "EM_ANALISE")
        self.assertIsNone(c["MOTIVO_DA_RECUSA"])
        self.assertNotIn("RECUSA_ANTERIOR", c)
        self.assertEqual(c["RECUSAS_REVERTIDAS"][0]["MOTIVO_DA_RECUSA"], "nao e fonte")

    def test_nao_reverte_recusa_de_outra_decisao(self):
        self.ficha(self.URL)
        FN.recusar(self.URL, "regra antiga")               # sem decisao: sem «antes» guardado
        self.assertIsNone(FN.reverter_recusa(self.URL, "D80(i)"))
        self.assertEqual(FN.carregar()["CANDIDATAS"][0]["ESTADO"], "RECUSADA")

    def test_so_a_mesma_decisao_desfaz(self):
        self.ficha(self.URL)
        FN.recusar(self.URL, "outra lane", decisao="D99")
        self.assertIsNone(FN.reverter_recusa(self.URL, "D80(i)"))
        self.assertEqual(FN.carregar()["CANDIDATAS"][0]["ESTADO"], "RECUSADA")

    def test_chamada_antiga_grava_o_mesmo_que_gravava(self):
        self.ficha(self.URL)
        c = FN.recusar(self.URL, "regra antiga")
        for k in ("RECUSA_ANTERIOR", "RECUSADA_POR", "RECUSADA_EM", "DUPLICADA_DE"):
            self.assertNotIn(k, c)

    def test_recusada_nao_se_qualifica(self):
        self.livro([("IT-T7-001", "T7", "https://www.qzxv.example/news")])
        self.ficha(self.URL, estado="RECUSADA")
        r = self.qualify()
        self.assertEqual(r["RESULTADO"], "BLOCK", r)
        self.assertIn("RECUSADA", r["PORQUE"])
        self.assertEqual(self.alloc()["NOVAS"], [])
        self.assertEqual(LC.estado_de(CAND), LC.POLICY_BLOCK)


# ── (ii) ──────────────────────────────────────────────────────────────────────
class ForaDeIT(_Base):
    URL = "https://www.qzxv-europe.example/"

    def test_prefixo_continua_do_maior_escrito_na_casa(self):
        RSY.ATLAS.write_text("#### EU-T12-001 · Outra\n", encoding="utf-8")
        (self.tmp / "outro_livro.json").write_text('{"x": "EU-T12-004", "y": "SEU-T12-009"}',
                                                   encoding="utf-8")
        self.ficha(self.URL)
        self.decisoes([_decisao(self.URL)])
        r = self.qualify()
        self.assertEqual(r["RESULTADO"], "BLOCK", r)
        fora = self.alloc()["NOVAS_FORA_DE_IT"]
        self.assertEqual([n["SOURCE_ID"] for n in fora], ["EU-T12-005"])
        self.assertEqual(self.alloc()["NOVAS"], [], "nunca na lista italiana")
        self.assertEqual(LC.estado_de(CAND), LC.CAPABILITY_BLOCK)
        self.assertEqual(self.build_contract_na_fila(), [], "sem contrato: para no QUALIFY")
        self.assertNotIn(LC.READY_FOR_COLLECTION, LC.snapshot().values())

    def test_territorio_e_prefixo_contam_a_parte(self):
        RSY.ATLAS.write_text("#### EU-T1-009 · X\n#### INT-T12-003 · Y\n", encoding="utf-8")
        self.ficha(self.URL)
        self.decisoes([_decisao(self.URL)])
        self.qualify()
        self.assertEqual(self.alloc()["NOVAS_FORA_DE_IT"][0]["SOURCE_ID"], "EU-T12-001")

    def test_pais_da_prova_da_o_prefixo(self):
        self.ficha(self.URL)
        self.decisoes([_decisao(self.URL, pais="FR", territorio="T5")])
        self.qualify()
        self.assertEqual(self.alloc()["NOVAS_FORA_DE_IT"][0]["SOURCE_ID"], "FR-T5-001")

    def test_segundo_site_continua_a_contagem(self):
        """O que ja se cunhou aqui conta — mesmo que ainda nao esteja em nenhum livro."""
        outro = "https://www.qzxv-intl.example/"
        self.ficha(self.URL)
        self.ficha(outro, cand="CAND-9962")
        self.decisoes([_decisao(self.URL), _decisao(outro, cand="CAND-9962")])
        self.qualify()
        self.qualify("CAND-9962")
        self.assertEqual([n["SOURCE_ID"] for n in self.alloc()["NOVAS_FORA_DE_IT"]],
                         ["EU-T12-001", "EU-T12-002"])

    def test_idempotente_nunca_cunha_segundo(self):
        self.ficha(self.URL)
        self.decisoes([_decisao(self.URL)])
        self.qualify()
        F.recuperar_bloqueadas_por_defeito(["D80(ii)"], {F.QUALIFY})
        W.correr(max_tarefas=1, pausa=0, verboso=False)
        self.assertEqual([n["SOURCE_ID"] for n in self.alloc()["NOVAS_FORA_DE_IT"]], ["EU-T12-001"])

    def test_site_que_ja_tem_numero_nao_recebe_outro(self):
        RSY.ATLAS.write_text("#### EU-T12-001 · Ja\n```\nTERRITORY: T12\nURL: https://qzxv-europe.example/x\n```\n",
                             encoding="utf-8")
        self.ficha(self.URL)
        self.decisoes([_decisao(self.URL)])
        r = self.qualify()
        self.assertIn("ja tem numero", r["PORQUE"])
        self.assertEqual(self.alloc().get("NOVAS_FORA_DE_IT", []), [])
        self.assertEqual(LC.estado_de(CAND), LC.SEMANTIC_REVIEW)

    def test_canal_de_fora_de_it_fica_nao_sei(self):
        url = "https://www.youtube.com/channel/UCXUG407gp3CnWnfS3ycijhA"
        self.ficha(url, tipo="YOUTUBE")
        doc = FN.carregar()
        doc["CANDIDATAS"][0]["ONDE_VIU"] = "declarado no site oficial do dono: https://www.qzxv-europe.example/"
        FN.gravar(doc)
        self.decisoes([_decisao(url)])
        r = self.qualify()
        self.assertEqual(r["RESULTADO"], "BLOCK", r)
        self.assertEqual(self.alloc().get("NOVAS_FORA_DE_IT", []), [])


# ── (iii) ─────────────────────────────────────────────────────────────────────
class PaginaHerda(_Base):
    def test_pagina_do_mesmo_site_herda_a_classe_unica(self):
        self.livro([("IT-T5-046", "T5", "https://www.qzxv.example/news")])
        self.ficha("https://www.qzxv.example/pubblicazioni/")
        r = self.qualify()
        self.assertEqual(r["RESULTADO"], "OK", r)
        nova = self.alloc()["NOVAS"][0]
        self.assertEqual((nova["SOURCE_ID"], nova["TERRITORY"]), ("IT-T5-041", "T5"))
        self.assertEqual(nova["MESMA_ORGANIZACAO"]["REGRA"], "D80(iii)")
        self.assertEqual(nova["MESMA_ORGANIZACAO"]["SOURCE_IDS_DO_SITE"], ["IT-T5-046"])

    def test_o_atlas_tambem_prova_a_classe(self):
        RSY.ATLAS.write_text("#### IT-T7-020 · Org\n```\nTERRITORY:   T7\nURL:  https://qzxv.example/\n```\n",
                             encoding="utf-8")
        self.ficha("https://qzxv.example/eventi")
        self.assertEqual(self.qualify()["RESULTADO"], "OK")
        self.assertEqual(self.alloc()["NOVAS"][0]["TERRITORY"], "T7")

    def test_site_misto_nao_herda(self):
        self.livro([("IT-T5-046", "T5", "https://www.qzxv.example/a"),
                    ("IT-T7-001", "T7", "https://www.qzxv.example/b")])
        self.ficha("https://www.qzxv.example/pubblicazioni/")
        r = self.qualify()
        self.assertEqual(r["RESULTADO"], "BLOCK", r)
        self.assertIn("site misto", self.evidencia())
        self.assertEqual(self.alloc()["NOVAS"], [])

    def test_raiz_do_site_nao_e_pagina(self):
        self.livro([("IT-T5-046", "T5", "https://www.qzxv.example/news")])
        for url in ("https://www.qzxv.example/", "https://qzxv.example/it/", "https://qzxv.example/index.php"):
            with self.subTest(url=url):
                self.ficha(url, cand="CAND-9961")
                r = self.qualify("CAND-9961")
                self.assertEqual(r["RESULTADO"], "BLOCK", r)
                self.assertIn("raiz do site", self.evidencia())
                FN.FILA.unlink()
        self.assertEqual(self.alloc()["NOVAS"], [])

    def test_subdominio_e_outro_site(self):
        self.livro([("IT-T5-046", "T5", "https://www.qzxv.example/news")])
        self.ficha("https://eventi.qzxv.example/programma")
        r = self.qualify()
        self.assertEqual(r["RESULTADO"], "BLOCK", r)
        self.assertIn("nao tem SOURCE_ID", self.evidencia())

    def test_decisao_com_prova_vale_antes_da_heranca(self):
        url = "https://www.qzxv.example/pubblicazioni/"
        self.livro([("IT-T5-046", "T5", "https://www.qzxv.example/news")])
        self.ficha(url)
        self.decisoes([_decisao(url, pais="IT", territorio="T12")])
        self.qualify()
        self.assertEqual(self.alloc()["NOVAS"][0]["TERRITORY"], "T12")

    def test_duvida_de_identidade_registada_nao_herda(self):
        url = "https://www.qzxv.example/archivio/16361"
        self.livro([("IT-T1-001", "T1", "https://www.qzxv.example/")])
        self.ficha(url)
        self.decisoes([{"CANDIDATA_ID": CAND, "URL": url, "TERRITORIO": "NAO SEI",
                        "CATEGORIA": "IDENTIDADE_DUPLICADA_POSSIVEL", "MOTIVO": "talvez a mesma que IT-T1-001",
                        "DECIDIDO_POR": "OPUS"}])
        r = self.qualify()
        self.assertEqual(r["RESULTADO"], "BLOCK", r)
        self.assertEqual(self.alloc()["NOVAS"], [])
        self.assertIn("duvida de identidade", self.evidencia())

    def test_falta_de_prova_registada_ainda_herda(self):
        url = "https://www.qzxv.example/pubblicazioni/"
        self.livro([("IT-T5-046", "T5", "https://www.qzxv.example/news")])
        self.ficha(url)
        self.decisoes([{"CANDIDATA_ID": CAND, "URL": url, "TERRITORIO": "NAO SEI",
                        "CATEGORIA": "PROVA_INSUFICIENTE", "MOTIVO": "pagina JS", "DECIDIDO_POR": "OPUS"}])
        self.assertEqual(self.qualify()["RESULTADO"], "OK")
        self.assertEqual(self.alloc()["NOVAS"][0]["TERRITORY"], "T5")

    def test_canal_nao_usa_a_regra_da_pagina(self):
        """Um canal cujo site nao tem numero nao herda de OUTRO canal do youtube.com."""
        self.livro([("IT-T5-046", "T5", "https://www.youtube.com/@outro")])
        self.ficha("https://www.youtube.com/channel/UCXUG407gp3CnWnfS3ycijhA/videos", tipo="YOUTUBE")
        doc = FN.carregar()
        doc["CANDIDATAS"][0]["ONDE_VIU"] = "declarado no site oficial do dono: https://www.semcasa.example/"
        FN.gravar(doc)
        r = self.qualify()
        self.assertEqual(r["RESULTADO"], "BLOCK", r)
        self.assertEqual(self.alloc()["NOVAS"], [])
        self.assertNotIn("D80(iii)", self.evidencia())

if __name__ == "__main__":
    unittest.main(verbosity=2)
