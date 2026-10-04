#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOC-ONDA2 — o QUALIFY leva LinkedIn (D23) ao Scrap, e diz o buraco do Instagram.

O que estes testes guardam:

  1. uma pagina LinkedIn de ORGANIZACAO declarada no site oficial ganha SOURCE_ID
     (FAMILY LINKEDIN, slug como identidade da plataforma), e o contrato NOMEIA a
     fase `video-linkedin` do Scrap, passa a validacao e para em CANARY_PENDING;
  2. `/showcase/` e perfil de pessoa nao ganham numero (o adaptador recusa-os);
  3. sem a ligacao oficial (o site que aponta para a conta) nao ha numero — nem
     no LinkedIn nem no YouTube: um id de plataforma diz QUAL conta, nao DE QUEM;
  4. uma pagina ja ligada a uma fonte nao ganha segundo numero;
  5. o Instagram fica bloqueado pelo que a matriz diz de listar a conta — nao por
     uma lista escrita a mao — e sem numero;
  6. o conferidor do Scrap despacha pela fase e recusa pagina trocada.

Tudo em ficheiros temporarios: nao toca a lane real.
"""
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))

import fila as F                      # noqa: E402
import fonte_nova as FN               # noqa: E402
import lifecycle as LC                # noqa: E402
import rota_do_scrap_social as RSS    # noqa: E402
import rota_do_scrap_youtube as RSY   # noqa: E402
import validar_contratos as VC        # noqa: E402
import worker as W                    # noqa: E402
from test_soc2_curator_youtube import CANAL_NOVO, _Lane  # noqa: E402

SITE = "declarado no site oficial do dono: https://www.vini.example.it/"


class _LaneSocial(_Lane):
    def _cand(self, cand, tipo, nome, url, onde_viu=SITE):
        doc = FN.carregar()
        f = {"CANDIDATA_ID": cand, "TIPO": tipo, "NOME": nome, "URL": url, "PAIS": "IT",
             "ESTADO": "EM_ANALISE", "SOURCE_ID": None}
        if onde_viu:
            f["ONDE_VIU"] = onde_viu
        doc["CANDIDATAS"].append(f)
        FN.gravar(doc)
        F.enfileirar(cand, F.QUALIFY, priority=30, motivo="teste")
        return W.correr(max_tarefas=1, pausa=0, verboso=False)[0]


class OLinkedinDeOrganizacao(_LaneSocial):
    def test_pagina_de_organizacao_ganha_numero_e_contrato_do_scrap(self):
        r = self._cand("CAND-L001", "LINKEDIN", "Consorzio Tutela Vini — Linkedin ufficiale",
                       "https://www.linkedin.com/company/consorzio-vini")
        self.assertEqual(r["RESULTADO"], "OK", r.get("PORQUE"))
        novas = self._alloc()
        self.assertEqual(len(novas), 1)
        n = novas[0]
        self.assertEqual((n["FAMILY"], n["SOURCE_NATIVE_ID"], n["SOURCE_NATIVE_ID_KIND"]),
                         ("LINKEDIN", "consorzio-vini", RSS.LI_KIND))
        self.assertEqual(n["SOURCE_ID"], "IT-T7-015")
        sid = n["SOURCE_ID"]
        self.assertEqual(LC.estado_de(sid), LC.CONTRACT_PENDING)

        r = W.correr(max_tarefas=1, pausa=0, verboso=False)[0]          # BUILD_CONTRACT
        self.assertEqual((r["TASK_TYPE"], r["RESULTADO"]), (F.BUILD_CONTRACT, "OK"), r.get("PORQUE"))
        c = {x["SOURCE_ID"]: x for x in json.loads(W.CONTRATOS.read_text(encoding="utf-8"))["FONTES"]}[sid]
        aq = c["ACQUISITION"]
        self.assertEqual((aq["STRATEGY"], aq["EXECUTOR"], aq["FASE"]),
                         ("SCRAP_FASE", "scrap-colheita", "video-linkedin"))
        self.assertEqual(aq["FILTROS"], {"pagina": "https://www.linkedin.com/company/consorzio-vini/",
                                         "teto": RSS.LI_TETO})
        self.assertTrue(c["IDENTITY"]["DOCUMENT_ID"].startswith(sid + ":LI:"))
        self.assertNotIn("feeds/videos.xml", json.dumps(c))
        self.assertEqual(VC.validar([c])[1], [])

        r = W.correr(max_tarefas=1, pausa=0, verboso=False)[0]          # VALIDATE_ROUTE
        self.assertEqual((r["TASK_TYPE"], r["RESULTADO"]), (F.VALIDATE_ROUTE, "OK"))
        self.assertEqual([t for t in F._ler()["TAREFAS"] if t["STATUS"] == F.PENDING], [],
                         "o canario da rota do Scrap e do orquestrador, nao do worker")
        self.assertEqual(LC.estado_de(sid), LC.CANARY_PENDING)
        self.assertNotIn(LC.READY_FOR_COLLECTION, LC.snapshot().values())

    def test_showcase_e_pessoa_nao_ganham_numero(self):
        r = self._cand("CAND-L002", "LINKEDIN", "Rete Rurale — Linkedin ufficiale",
                       "https://www.linkedin.com/showcase/retenazionale")
        self.assertEqual(r["RESULTADO"], "BLOCK")
        self.assertIn("SHOWCASE", r["PORQUE"])
        self.assertEqual(LC.estado_de("CAND-L002"), LC.CAPABILITY_BLOCK)
        r = self._cand("CAND-L003", "LINKEDIN", "Mario Rossi agronomo",
                       "https://www.linkedin.com/in/mario-rossi")
        self.assertEqual(r["RESULTADO"], "BLOCK")
        self.assertIn("PESSOA", r["PORQUE"])
        self.assertEqual(self._alloc(), [])

    def test_sem_ligacao_oficial_nao_ha_numero(self):
        r = self._cand("CAND-L004", "LINKEDIN", "Consorzio Tutela Vini — Linkedin",
                       "https://www.linkedin.com/company/consorzio-vini", onde_viu="uma pesquisa")
        self.assertEqual(r["RESULTADO"], "BLOCK")
        self.assertIn("ligacao oficial", r["PORQUE"])
        self.assertEqual(LC.estado_de("CAND-L004"), LC.SEMANTIC_REVIEW)
        self.assertEqual(self._alloc(), [])

    def test_pagina_ja_ligada_nao_ganha_segundo_numero(self):
        W.CONTRATOS.write_text(json.dumps({"FONTES": [{
            "SOURCE_ID": "IT-T7-003", "SOURCE_NATIVE_ID": "consorzio-vini",
            "SOURCE_NATIVE_ID_KIND": RSS.LI_KIND,
            "ACQUISITION": RSS.acquisition_linkedin("consorzio-vini", {"ROTA": "x"})}]}),
            encoding="utf-8")
        r = self._cand("CAND-L005", "LINKEDIN", "Consorzio Tutela Vini — Linkedin ufficiale",
                       "https://www.linkedin.com/company/Consorzio-Vini/")
        self.assertEqual(r["RESULTADO"], "OK")
        ev = json.loads(W.EVIDENCIA.read_text(encoding="utf-8"))["PROVAS"][-1]["DADOS"]
        self.assertEqual(ev["SOURCE_ID_REAL"], "IT-T7-003")
        self.assertTrue(ev["JA_TINHA_IDENTIDADE"])
        self.assertEqual(self._alloc(), [])


class OContratoGuardaOLugarDeQuemPublica(_LaneSocial):
    """D61 (SOC-TEMPO): o contrato social leva o SOURCE_LOCATION tirado do site oficial."""

    def _contrato(self, onde_viu):
        self._cand("CAND-L090", "LINKEDIN", "Consorzio Tutela Vini — Linkedin ufficiale",
                   "https://www.linkedin.com/company/consorzio-vini", onde_viu=onde_viu)
        W.correr(max_tarefas=1, pausa=0, verboso=False)                 # BUILD_CONTRACT
        sid = self._alloc()[0]["SOURCE_ID"]
        return {x["SOURCE_ID"]: x for x in json.loads(W.CONTRATOS.read_text(encoding="utf-8"))["FONTES"]}[sid]

    def test_site_com_sede_no_cadastro_da_a_provincia(self):
        c = self._contrato("declarado no site oficial do dono: https://www.arpae.it/")
        self.assertEqual((c["SOURCE_LOCATION"], c["SOURCE_LOCATION_PRECISION"]), ("Bologna", "PROVINCE"))
        self.assertEqual(VC.validar([c])[1], [])

    def test_site_sem_prova_fica_NAO_SEI_com_o_porque(self):
        c = self._contrato(SITE)
        self.assertEqual(c["SOURCE_LOCATION"], "NAO SEI")
        self.assertTrue(c["SOURCE_LOCATION_BASIS"].startswith("NAO SEI:"))


class OYoutubePedeALigacaoOficial(_LaneSocial):
    def test_canal_com_nome_bom_sem_site_nao_ganha_numero(self):
        r = self._cand("CAND-Y101", "YOUTUBE", "Consorzio Tutela Vini — Youtube ufficiale",
                       "https://www.youtube.com/channel/%s" % CANAL_NOVO, onde_viu=None)
        self.assertEqual(r["RESULTADO"], "BLOCK")
        self.assertIn("ligacao oficial", r["PORQUE"])
        self.assertEqual(self._alloc(), [])

    def test_crawl_link_do_site_conta_como_ligacao(self):
        doc_nota = ("DISCOVERED_FROM=https://www.vini.example.it/video | "
                    "DISCOVERY_METHOD=CRAWL_LINK | ANCHOR_TEXT=youtube")
        doc = FN.carregar()
        doc["CANDIDATAS"].append({"CANDIDATA_ID": "CAND-Y102", "TIPO": "YOUTUBE",
                                  "NOME": "Consorzio Tutela Vini — Youtube ufficiale",
                                  "URL": "https://www.youtube.com/channel/%s" % CANAL_NOVO,
                                  "PAIS": "IT", "ESTADO": "EM_ANALISE", "SOURCE_ID": None,
                                  "NOTA": doc_nota})
        FN.gravar(doc)
        F.enfileirar("CAND-Y102", F.QUALIFY, priority=30, motivo="teste")
        r = W.correr(max_tarefas=1, pausa=0, verboso=False)[0]
        self.assertEqual(r["RESULTADO"], "OK", r.get("PORQUE"))


class OInstagramDizOBuraco(_LaneSocial):
    def test_conta_instagram_bloqueia_pela_matriz_sem_numero(self):
        r = self._cand("CAND-I001", "INSTAGRAM", "Consorzio Tutela Vini — Instagram ufficiale",
                       "https://www.instagram.com/consorziovini")
        self.assertEqual(r["RESULTADO"], "BLOCK")
        self.assertIn("ROUTE_NOT_ALLOWED", r["PORQUE"])
        self.assertIn("D22", r["PORQUE"])
        self.assertEqual(LC.estado_de("CAND-I001"), LC.POLICY_BLOCK)
        self.assertEqual(self._alloc(), [])

    def test_o_bloqueio_segue_a_matriz(self):
        orig = RSS.instagram_listar_permitido
        self.addCleanup(setattr, RSS, "instagram_listar_permitido", orig)
        RSS.instagram_listar_permitido = lambda: (True, "INSTAGRAM/instagram.profile.discovery: ALLOWED")
        r = self._cand("CAND-I002", "INSTAGRAM", "Consorzio — Instagram ufficiale",
                       "https://www.instagram.com/consorzio")
        self.assertEqual(r["RESULTADO"], "BLOCK")
        self.assertIn("molde", r["PORQUE"])
        self.assertEqual(LC.estado_de("CAND-I002"), LC.CAPABILITY_BLOCK)


class OConferidorDespachaPelaFase(unittest.TestCase):
    def test_linkedin_confere_e_recusa_pagina_trocada(self):
        d = RSS.o_que_o_scrap_declara_linkedin()
        aq = RSS.acquisition_linkedin("consorzio-vini", d)
        self.assertEqual(RSS.conferir(aq)[0], True, RSS.conferir(aq)[1])
        mau = dict(aq, FILTROS={"pagina": "https://www.linkedin.com/company/outra/", "teto": 2})
        self.assertFalse(RSS.conferir(mau)[0])
        mau = dict(aq, FASE="janela")
        self.assertFalse(RSS.conferir(mau)[0])
        self.assertFalse(RSS.conferir(dict(aq, ROTA_DECLARADA_PELO_SCRAP="velha"))[0])

    def test_youtube_continua_pelo_conferidor_dele(self):
        aq = RSY.acquisition(CANAL_NOVO)
        self.assertEqual(RSS.conferir(aq), RSY.conferir(aq))

    def test_slugs(self):
        self.assertEqual(RSS.slug_linkedin("https://it.linkedin.com/company/Arpa-Lazio/"),
                         ("arpa-lazio", ""))
        self.assertEqual(RSS.slug_linkedin("https://www.linkedin.com/showcase/x")[0], None)
        self.assertEqual(RSS.slug_linkedin("https://www.linkedin.com/in/x")[1], "PERFIL_DE_PESSOA")
        # a organizacao publicou o link do painel dela: a pagina e a mesma
        self.assertEqual(RSS.slug_linkedin("https://www.linkedin.com/company/15179878/admin/dashboard")[0],
                         "15179878")
        self.assertIsNone(RSS.slug_linkedin("https://www.linkedin.com/company/x/qualquer/coisa")[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
