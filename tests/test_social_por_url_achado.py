# -*- coding: utf-8 -*-
"""SOCIAL-ATE-A-SALA · D — reel e post LinkedIn ACHADOS -> pedido do Scrap, com a proveniencia.

O formato de entrada e o de `POSTS-PARA-O-SCRAP.jsonl` da linha da busca (`coleta/linha_busca.py`,
ramo `linha-busca-v1`): URL + PROVENIENCIA{ESPECIE, CONSULTA, MOTOR, POSICAO, INSTANTE}.
Os livros sao pequenos e montados aqui (o repositorio nao tem contrato social). Sem rede.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
import social_por_url_achado as D  # noqa: E402

BUSCA = {"ESPECIE": "ACHADO_POR_BUSCA", "CONSULTA": "peronospora vite reel", "CONSULTA_ID": "Q7",
         "MOTOR": "duckduckgo-html", "ROTA_DO_MOTOR": "HTTP", "POSICAO": 3, "INSTANTE": "2026-09-27T20:10:00+00:00"}
PESSOA = {"ESPECIE": "ACHADO_POR_PESSOA", "QUEM": "luciano", "ONDE": "grupo WhatsApp dos agronomos",
          "INSTANTE": "2026-09-27T21:00:00+00:00"}
REEL = "https://www.instagram.com/reel/DAbCdEfGhIj/"
REEL_COM_CONTA = "https://www.instagram.com/oliveti_sezze/reel/DAbCdEfGhIj/"
POST_ORG = ("https://www.linkedin.com/posts/gruppocaviro_vendemmia-2026-activity-7490681050906439680-AbCd")
POST_PESSOA = ("https://www.linkedin.com/posts/alex-beneventi-0680b635_perizia-activity-7390681050906439681-XyZw")


def livros(**mais):
    lv = {"CONTRATOS": {"FONTES": [
              {"SOURCE_ID": "IT-T9-024", "ACQUISITION": {"FASE": "video-linkedin", "LINKEDIN_SLUG": "gruppocaviro"}},
              {"SOURCE_ID": "IT-T5-900", "ACQUISITION": {"FASE": "audio-reel", "INSTAGRAM_HANDLE": "oliveti_sezze"}}]},
          "ALLOC": {"NOVAS": []},
          "FILA": {"CANDIDATAS": [
              {"CANDIDATA_ID": "CAND-0087", "TIPO": "INSTAGRAM", "URL": "https://www.instagram.com/provinciatrento",
               "ESTADO": "POLICY_BLOCK", "SOURCE_ID": None},
              {"CANDIDATA_ID": "CAND-1175", "TIPO": "LINKEDIN", "ESTADO": "CANDIDATA", "SOURCE_ID": None,
               "URL": "https://www.linkedin.com/in/alex-beneventi-0680b635"}]}}
    lv.update(mais)
    return lv


def um(url, prov=BUSCA, lv=None, **achado):
    return D.planear([dict({"URL": url, "PROVENIENCIA": dict(prov)}, **achado)], lv or livros())["LINHAS"][0]


class OEndereco(unittest.TestCase):
    def test_1_reel_post_e_perfil_sao_tres_coisas(self):
        self.assertEqual(D.especie_do_endereco(REEL)["ESPECIE"], "REEL")
        self.assertEqual(D.especie_do_endereco(REEL_COM_CONTA)["CONTA_NO_ENDERECO"], "oliveti_sezze")
        self.assertIsNone(D.especie_do_endereco(REEL)["CONTA_NO_ENDERECO"])
        p = D.especie_do_endereco(POST_ORG)
        self.assertEqual((p["ESPECIE"], p["ACTIVITY_ID"], p["VANITY"]),
                         ("POST_LINKEDIN", "7490681050906439680", "gruppocaviro"))
        u = D.especie_do_endereco("https://www.linkedin.com/feed/update/urn:li:activity:7490681050906439680/")
        self.assertEqual((u["ESPECIE"], u["VANITY"]), ("POST_LINKEDIN", None))
        for perfil in ("https://www.instagram.com/oliveti_sezze/", "https://www.linkedin.com/in/alex",
                       "https://www.linkedin.com/company/gruppocaviro/", "https://www.youtube.com/watch?v=abc"):
            self.assertEqual(D.especie_do_endereco(perfil)["ESPECIE"], "NAO_E_PUBLICACAO", perfil)

    def test_2_perfil_achado_nao_vira_item(self):
        l = um("https://www.instagram.com/oliveti_sezze/")
        self.assertEqual(l["ESTADO"], "NAO_E_ITEM")
        self.assertNotIn("PEDIDO", l)


class AProveniencia(unittest.TestCase):
    def test_3_busca_sem_consulta_motor_posicao_ou_instante_e_rejeitada(self):
        for k in ("CONSULTA", "MOTOR", "POSICAO", "INSTANTE"):
            p = dict(BUSCA)
            del p[k]
            l = um(REEL_COM_CONTA, prov=p)
            self.assertEqual(l["ESTADO"], "REJEITADO", k)
            self.assertIn(k, l["PORQUE"], k)

    def test_4_posicao_e_instante_com_forma(self):
        for k, v in (("POSICAO", 0), ("POSICAO", "terceira"), ("INSTANTE", "ontem")):
            l = um(REEL_COM_CONTA, prov=dict(BUSCA, **{k: v}))
            self.assertEqual(l["ESTADO"], "REJEITADO", (k, v))

    def test_5_pessoa_exige_quem_onde_e_quando(self):
        self.assertEqual(um(REEL_COM_CONTA, prov=PESSOA)["ESTADO"], "PEDIDO")
        p = dict(PESSOA)
        del p["ONDE"]
        self.assertEqual(um(REEL_COM_CONTA, prov=p)["ESTADO"], "REJEITADO")

    def test_6_especie_desconhecida_e_rejeitada(self):
        self.assertEqual(um(REEL_COM_CONTA, prov=dict(BUSCA, ESPECIE="ACHADO_POR_ACASO"))["ESTADO"], "REJEITADO")


class OPedido(unittest.TestCase):
    def test_7_reel_de_conta_com_SOURCE_ID_vira_captura_reel_com_a_proveniencia(self):
        l = um(REEL_COM_CONTA)
        self.assertEqual(l["ESTADO"], "PEDIDO")
        self.assertEqual(l["SOURCE_ID"], "IT-T5-900")
        self.assertEqual(l["PEDIDO"], {"alvo": "T5", "filtros": {"fase": "captura-reel", "url": REEL_COM_CONTA,
                                                               "fonte": "IT-T5-900", "pais": "IT", "universo": "T5"}})
        self.assertEqual(l["PROVENIENCIA"], BUSCA)

    def test_8_reel_sem_conta_no_endereco_usa_a_CONTA_do_achado_ou_fica_NAO_SEI(self):
        self.assertEqual(um(REEL)["ESTADO"], "CONTA_NAO_SEI")
        self.assertEqual(um(REEL, CONTA="https://www.instagram.com/oliveti_sezze/")["SOURCE_ID"], "IT-T5-900")

    def test_9_conta_do_achado_contra_a_do_endereco_e_conflito(self):
        self.assertEqual(um(REEL_COM_CONTA, CONTA="outra")["ESTADO"], "CONTA_EM_CONFLITO")

    def test_10_post_de_organizacao_vira_video_linkedin_da_pagina_dela(self):
        l = um(POST_ORG)
        self.assertEqual((l["ESTADO"], l["SOURCE_ID"], l["FASE"]), ("PEDIDO", "IT-T9-024", "video-linkedin"))
        self.assertEqual(l["PEDIDO"]["filtros"]["pagina"], "https://www.linkedin.com/company/gruppocaviro/")
        self.assertEqual(l["ALVO_ACHADO"]["ACTIVITY_ID"], "7490681050906439680")

    def test_11_post_de_pessoa_fica_bloqueado_por_decisao(self):
        l = um(POST_PESSOA)
        self.assertEqual(l["ESTADO"], "BLOQUEADO_POR_DECISAO")
        self.assertIn("D37", l["PORQUE"])
        self.assertNotIn("PEDIDO", l)

    def test_12_autor_desconhecido_no_post_nao_se_adivinha(self):
        l = um("https://www.linkedin.com/posts/desconhecido_x-activity-7490681050906439682-Qq")
        self.assertEqual(l["ESTADO"], "CONTA_NAO_SEI")
        self.assertIsNone(l.get("A_REGISTAR"))

    def test_13_conta_sem_SOURCE_ID_espera_e_nao_inventa(self):
        l = um("https://www.instagram.com/novaconta/reel/ZZZZZZZZZZZ/")
        self.assertEqual(l["ESTADO"], "ESPERA_SOURCE_ID")
        self.assertNotIn("SOURCE_ID", l)
        f = l["A_REGISTAR"]
        self.assertEqual((f["tipo"], f["pais"], f["url"]), ("INSTAGRAM", "NAO SEI", "https://www.instagram.com/novaconta/"))
        self.assertIn("consulta «peronospora vite reel»", f["nota"])

    def test_14_conta_que_ja_e_candidata_espera_o_QUALIFY_sem_segunda_candidata(self):
        l = um("https://www.instagram.com/provinciatrento/reel/YYYYYYYYYYY/")
        self.assertEqual((l["ESTADO"], l["CANDIDATA_ID"], l["A_REGISTAR"]), ("ESPERA_SOURCE_ID", "CAND-0087", None))

    def test_15_o_mesmo_reel_achado_duas_vezes_e_um_pedido_so(self):
        p = D.planear([{"URL": REEL_COM_CONTA, "PROVENIENCIA": BUSCA},
                       {"URL": REEL_COM_CONTA + "?utm=x", "PROVENIENCIA": dict(BUSCA, POSICAO=7)}], livros())
        self.assertEqual([l["ESTADO"] for l in p["LINHAS"]], ["PEDIDO", "DUPLICADO"])

    def test_16_conta_ligada_a_duas_fontes_e_colisao(self):
        lv = livros()
        lv["CONTRATOS"]["FONTES"].append({"SOURCE_ID": "IT-T5-901",
                                          "ACQUISITION": {"INSTAGRAM_HANDLE": "oliveti_sezze"}})
        self.assertEqual(um(REEL_COM_CONTA, lv=lv)["ESTADO"], "IDENTIDADE_EM_COLISAO")


class APortaEOAnexo(unittest.TestCase):
    def test_17_a_candidata_entra_pela_porta_canonica_numa_copia(self):
        import fonte_nova as FN
        antes = FN.FILA
        with tempfile.TemporaryDirectory() as t:
            FN.FILA = Path(t) / "FONTES-CANDIDATAS.json"
            try:
                p = D.planear([{"URL": "https://www.instagram.com/novaconta/reel/ZZZZZZZZZZZ/", "PROVENIENCIA": BUSCA}],
                              livros())
                feitas = D.registar_candidatas(p)
                self.assertEqual(len(feitas), 1)
                c = FN.carregar()["CANDIDATAS"][0]
                self.assertEqual((c["TIPO"], c["ESTADO"], c["SOURCE_ID"]), ("INSTAGRAM", "CANDIDATA", None))
                self.assertEqual(D.registar_candidatas(p)[0]["CANDIDATA_ID"], c["CANDIDATA_ID"])  # idempotente
                self.assertEqual(len(FN.carregar()["CANDIDATAS"]), 1)
            finally:
                FN.FILA = antes

    def test_18_anexar_poe_a_proveniencia_ao_lado_do_envelope_e_mede_o_alvo(self):
        l = um(POST_ORG)
        with tempfile.TemporaryDirectory() as t:
            run = Path(t) / "RUN-1"
            run.mkdir()
            (run / "ENVELOPE.json").write_text(json.dumps({"COLHEITA": [
                {"OBSERVACAO": {"NATIVE_ID": "7490681050906439680"}}]}), encoding="utf-8")
            s = D.anexar(l, "RUN-1", balcao=t)
            self.assertEqual(s["ALVO_NA_COLHEITA"], "SIM")
            self.assertEqual(json.loads((run / "PROVENIENCIA-DO-ACHADO.json").read_text(encoding="utf-8"))
                             ["PROVENIENCIA"]["CONSULTA"], "peronospora vite reel")
            self.assertEqual(D.anexar(l, "RUN-2", balcao=t)["ALVO_NA_COLHEITA"], "NAO SEI (sem envelope desta corrida)")

    def test_19_a_fase_e_os_filtros_existem_no_Scrap(self):
        """O pedido so usa fases e filtros que `scrap_colheita` declara (senao a corrida recusa)."""
        import scrap_colheita as SC
        for url in (REEL_COM_CONTA, POST_ORG):
            f = dict(um(url)["PEDIDO"]["filtros"])
            fase = f.pop("fase")
            for k in ("fonte", "pais", "universo"):
                f.pop(k)
            self.assertIn(fase, SC.FASES)
            self.assertTrue(set(f) <= set(SC.NOMEADOS[fase]), (fase, f))

    def test_20_registar_fora_da_copia_e_recusado(self):
        with tempfile.TemporaryDirectory() as t:
            a = Path(t) / "a.jsonl"
            a.write_text(json.dumps({"URL": REEL_COM_CONTA, "PROVENIENCIA": BUSCA}) + "\n", encoding="utf-8")
            self.assertEqual(D.main(["--plano", "--achados", str(a), "--registar"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
