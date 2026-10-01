# -*- coding: utf-8 -*-
"""T9 SOCIAL-CATALOGO-AUTORIZADO (01/10) · a porta social aceita SO o item com rastro, dentro do ambito,
e diz o motivo de cada recusa com nome proprio.

Medido antes deste teste (`curadoria/plano_onda_social.py:59-61` @ 6c1374d62): `fontes_sociais()` aceitava
um contrato por UMA palavra (`ACQUISITION.STRATEGY == "SCRAP_FASE"`) e devolvia `[]` sem dizer porque.
Dois defeitos, os dois medidos aqui:
  · um feed de canal YouTube READY_FOR_COLLECTION com rastro completo (AUTORIZACAO + ROUTE_POLICY_STATUS
    ALLOWED) ficava FORA, so por ter outra STRATEGY;
  · um contrato SCRAP_FASE SEM rastro de autorizacao entrava, e um canal-youtube (fora do ambito do T9)
    tambem — a porta nao lia o rastro, lia a palavra.

O ambito (missao T9 + resposta do dono a 01/10):
  · YouTube   so YOUTUBE_CHANNEL_FEED de canal em READY_FOR_COLLECTION (a missao a letra);
  · LinkedIn  video-linkedin de pagina de ORGANIZACAO (D23) — a fase traz MP4 e legenda; o dono aceitou;
  · Instagram so o Reel por URL directa (D22/D157); listagem e perfil NAO.

Os contratos dos testes sao SINTETICOS (nenhum byte de plataforma); o livro do ciclo de vida e um dict.
Sem rede.
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for _p in (RAIZ, RAIZ / "curadoria", RAIZ / "ferramentas" / "big_collection"):
    sys.path.insert(0, str(_p))
import _gavetas  # noqa: E402,F401
import plano_onda_social as P  # noqa: E402
import rota_do_scrap_social as RSS  # noqa: E402
import rota_do_scrap_youtube as RSY  # noqa: E402

CANAL = "UCXUG407gp3CnWnfS3ycijhA"
MOTIVOS = {"STRATEGY_DESCONHECIDA", "LISTAGEM_NAO_AUTORIZADA", "FORA_DO_AMBITO_AUTORIZADO",
           "SEM_RASTRO_DE_AUTORIZACAO", "SEM_RASTRO_DE_POLITICA", "ROTA_NAO_PERMITIDA", "ROTA_NAO_CONFERIDA",
           "ESTADO_NAO_READY"}


def feed(sid, *, autorizacao=RSY.AUTORIZACAO, politica="ALLOWED", canal=CANAL):
    aq = {"STRATEGY": "YOUTUBE_CHANNEL_FEED", "CHANNEL_ID": canal,
          "FEED_URL": "https://www.youtube.com/feeds/videos.xml?channel_id=%s" % canal, "MAX_TARGETS": 15}
    if autorizacao is not None:
        aq["AUTORIZACAO"] = autorizacao
    c = {"SOURCE_ID": sid, "TERRITORY": "T5", "ACQUISITION": aq}
    if politica is not None:
        c["ROUTE_POLICY_STATUS"] = politica
    return c


def linkedin(sid, slug="ispra_2", *, autorizacao=RSS.LI_AUTORIZACAO):
    aq = RSS.acquisition_linkedin(slug)
    if autorizacao is None:
        aq.pop("AUTORIZACAO")
    else:
        aq["AUTORIZACAO"] = autorizacao
    return {"SOURCE_ID": sid, "TERRITORY": "T5", "ACQUISITION": aq}


def canal_youtube(sid):
    return {"SOURCE_ID": sid, "TERRITORY": "T5", "ACQUISITION": RSY.acquisition(CANAL)}


def fase(sid, nome, autorizacao):
    return {"SOURCE_ID": sid, "TERRITORY": "T5",
            "ACQUISITION": {"STRATEGY": "SCRAP_FASE", "EXECUTOR": "scrap-colheita", "FASE": nome,
                            "FILTROS": {}, "AUTORIZACAO": autorizacao}}


def site(sid):
    return {"SOURCE_ID": sid, "TERRITORY": "T5",
            "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": "https://x.test/", "LINK_PATTERN": "x"}}


def cat(*cs):
    return {c["SOURCE_ID"]: c for c in cs}


def estados(**kw):
    return lambda s: kw.get(s.replace("-", "_"))


READY = "READY_FOR_COLLECTION"


class PortaSocialT9(unittest.TestCase):
    # ── o VERMELHO da missao: autorizado com rastro fica fora; recusa sem motivo ──────────────────
    def test_feed_ready_com_rastro_entra_na_porta(self):
        c = cat(feed("IT-T5-901"))
        self.assertEqual(P.fontes_sociais(c, estado_de=estados(IT_T5_901=READY)), ["IT-T5-901"])

    def test_a_porta_diz_o_motivo_de_cada_recusa(self):
        c = cat(feed("IT-T5-902", politica="ROBOTS_DISALLOWED"), site("IT-T5-903"))
        t = P.triagem_social(c, estado_de=estados(IT_T5_902=READY))
        self.assertEqual(t["ACEITES"], [])
        self.assertEqual([r["SOURCE_ID"] for r in t["RECUSADAS"]], ["IT-T5-902"])
        r = t["RECUSADAS"][0]
        self.assertEqual(r["MOTIVO"], "ROTA_NAO_PERMITIDA", r)
        self.assertIn("ROBOTS_DISALLOWED", r["PORQUE"])
        self.assertEqual(t["NAO_SOCIAIS"], 1)              # o site nao e recusa da porta social: nem e social

    # ── cada motivo, com o nome dele ───────────────────────────────────────────────────────────────
    def motivo(self, contrato, **est):
        t = P.triagem_social(cat(contrato), estado_de=estados(**est))
        self.assertEqual(t["ACEITES"], [], t)
        self.assertEqual(len(t["RECUSADAS"]), 1, t)
        r = t["RECUSADAS"][0]
        self.assertIn(r["MOTIVO"], MOTIVOS, r)
        self.assertTrue(r["PORQUE"], r)
        self.assertEqual(r["MOTIVO"], r["MOTIVOS"][0]["MOTIVO"], r)
        return r

    def test_linkedin_de_organizacao_com_d23_entra(self):
        self.assertEqual(P.fontes_sociais(cat(linkedin("IT-T5-910")), estado_de=estados()), ["IT-T5-910"])

    def test_linkedin_sem_autorizacao_fica_fora(self):
        self.assertEqual(self.motivo(linkedin("IT-T5-911", autorizacao=None))["MOTIVO"], "SEM_RASTRO_DE_AUTORIZACAO")

    def test_linkedin_com_decisao_de_outra_plataforma_fica_fora(self):
        r = self.motivo(linkedin("IT-T5-912", autorizacao=RSY.AUTORIZACAO))
        self.assertEqual(r["MOTIVO"], "SEM_RASTRO_DE_AUTORIZACAO")
        self.assertIn("D17.4", r["PORQUE"])

    def test_canal_youtube_pelo_scrap_fica_fora_do_ambito(self):
        r = self.motivo(canal_youtube("IT-T5-913"))
        self.assertEqual(r["MOTIVO"], "FORA_DO_AMBITO_AUTORIZADO")
        self.assertIn("canal-youtube", r["PORQUE"])

    def test_feed_sem_autorizacao_fica_fora(self):
        self.assertEqual(self.motivo(feed("IT-T5-914", autorizacao=None), IT_T5_914=READY)["MOTIVO"],
                         "SEM_RASTRO_DE_AUTORIZACAO")

    def test_feed_sem_politica_da_rota_fica_fora(self):
        self.assertEqual(self.motivo(feed("IT-T5-915", politica=None), IT_T5_915=READY)["MOTIVO"],
                         "SEM_RASTRO_DE_POLITICA")

    def test_feed_fora_de_ready_fica_fora(self):
        r = self.motivo(feed("IT-T5-916"), IT_T5_916="RETRY_AFTER")
        self.assertEqual(r["MOTIVO"], "ESTADO_NAO_READY")
        self.assertIn("RETRY_AFTER", r["PORQUE"])

    def test_feed_sem_estado_no_livro_fica_fora(self):
        self.assertEqual(self.motivo(feed("IT-T5-917"))["MOTIVO"], "ESTADO_NAO_READY")

    def test_feed_com_canal_invalido_nao_passa_a_rota(self):
        self.assertEqual(self.motivo(feed("IT-T5-918", canal="nao-e-canal"), IT_T5_918=READY)["MOTIVO"],
                         "ROTA_NAO_CONFERIDA")

    def test_listagem_do_instagram_fica_fora(self):
        self.assertEqual(self.motivo(fase("IT-T5-919", "janela", "D22 (DECISOES-DONO): reels"))["MOTIVO"],
                         "LISTAGEM_NAO_AUTORIZADA")

    def test_reel_sem_conferidor_no_curator_diz_que_a_rota_nao_se_confere(self):
        # D22/D157 cobrem o Reel por URL directa; o Curator nao tem conferidor para a fase: recusa com nome
        self.assertEqual(self.motivo(fase("IT-T5-920", "captura-reel", "D22 (DECISOES-DONO): reels"))["MOTIVO"],
                         "ROTA_NAO_CONFERIDA")

    def test_plataforma_fora_do_ambito_fica_fora(self):
        self.assertEqual(self.motivo(fase("IT-T5-921", "canario-bluesky", "D99 qualquer"))["MOTIVO"],
                         "FORA_DO_AMBITO_AUTORIZADO")

    def test_strategy_desconhecida_tem_nome(self):
        c = {"SOURCE_ID": "IT-T5-922", "TERRITORY": "T5", "ACQUISITION": {"STRATEGY": "PALAVRA_NOVA"}}
        r = self.motivo(c)
        self.assertEqual(r["MOTIVO"], "STRATEGY_DESCONHECIDA")
        self.assertIn("PALAVRA_NOVA", r["PORQUE"])

    def test_nenhum_social_some_em_silencio(self):
        c = cat(feed("IT-T5-930"), feed("IT-T5-931", politica="ROBOTS_DISALLOWED"), linkedin("IT-T5-932"),
                linkedin("IT-T5-933", "outra", autorizacao=None), canal_youtube("IT-T5-934"), site("IT-T5-935"),
                {"SOURCE_ID": "IT-T5-936", "ACQUISITION": {}})
        t = P.triagem_social(c, estado_de=estados(IT_T5_930=READY, IT_T5_931=READY))
        self.assertEqual(t["ACEITES"], ["IT-T5-930", "IT-T5-932"])
        recusadas = [r["SOURCE_ID"] for r in t["RECUSADAS"]]
        self.assertEqual(sorted(t["ACEITES"] + recusadas + ["IT-T5-935"]), sorted(c))
        self.assertEqual(t["NAO_SOCIAIS"], 1)
        self.assertEqual(sum(t["RECUSADAS_POR_MOTIVO"].values()), len(recusadas))
        self.assertEqual(t["POR_PLATAFORMA"]["YOUTUBE"]["ACEITES"], 1)
        self.assertEqual(t["POR_PLATAFORMA"]["LINKEDIN"]["ACEITES"], 1)

    def test_a_porta_nao_le_o_livro_quando_nao_ha_feed(self):
        def rebenta(_s):
            raise AssertionError("o livro do ciclo de vida nao devia ser lido")
        self.assertEqual(P.fontes_sociais(cat(linkedin("IT-T5-940")), estado_de=rebenta), ["IT-T5-940"])


class LinhaSocialT9(unittest.TestCase):
    """O alimentador da coleta continua (`_catalogo_social`) le a MESMA porta e escreve as recusas."""

    def setUp(self):
        import coleta_continua as C  # noqa: PLC0415
        self.C = C
        self.raiz = Path(tempfile.mkdtemp(prefix="porta-social-t9-"))
        self.addCleanup(shutil.rmtree, self.raiz, True)
        (self.raiz / "curadoria").mkdir()
        (self.raiz / "ferramentas" / "big_collection").mkdir(parents=True)
        (self.raiz / "ferramentas" / "big_collection" / "COORTE-BIG-COLLECTION-V1.json").write_text(
            json.dumps({"PLANO": {"PAINEL_DO_GATE": {"READY_SOCIAL_TOTAL": 0}}}), encoding="utf-8")

    def escrever(self, contratos, transicoes):
        (self.raiz / "curadoria" / "italy_contracts_curator.json").write_text(
            json.dumps({"FONTES": contratos}), encoding="utf-8")
        (self.raiz / "curadoria" / "LIFECYCLE-LEDGER-V1.json").write_text(json.dumps({"TRANSICOES": [
            {"SOURCE_ID": s, "NEW_STATE": e} for s, e in transicoes]}), encoding="utf-8")

    def test_feed_ready_com_rastro_e_unidade_governada_da_linha(self):
        self.escrever([feed("IT-T5-950"), feed("IT-T5-951", politica="ROBOTS_DISALLOWED")],
                      [("IT-T5-950", "CANARY_PENDING"), ("IT-T5-950", READY), ("IT-T5-951", READY)])
        f = self.C._catalogo_social(self.raiz)
        self.assertEqual(f["UNIDADES_GOVERNADAS"], 1, f)
        self.assertEqual(f["PORTA_SOCIAL"]["ACEITES"], ["IT-T5-950"])
        self.assertEqual(f["PORTA_SOCIAL"]["RECUSADAS"], {"ROTA_NAO_PERMITIDA": ["IT-T5-951"]})
        self.assertNotIn("SEM_CATALOGO", [m[0] for m in f["MOTIVOS"]])

    def test_porta_vazia_diz_os_motivos_e_nao_so_a_palavra(self):
        self.escrever([feed("IT-T5-960", autorizacao=None), canal_youtube("IT-T5-961"), site("IT-T5-962")],
                      [("IT-T5-960", READY)])
        f = self.C._catalogo_social(self.raiz)
        self.assertEqual(f["UNIDADES_GOVERNADAS"], 0)
        sem = [p for e, p in f["MOTIVOS"] if e == "SEM_CATALOGO"]
        self.assertEqual(len(sem), 1, f["MOTIVOS"])
        self.assertIn("SEM_RASTRO_DE_AUTORIZACAO", sem[0])
        self.assertIn("FORA_DO_AMBITO_AUTORIZADO", sem[0])
        self.assertEqual(f["PORTA_SOCIAL"]["RECUSADAS"], {"FORA_DO_AMBITO_AUTORIZADO": ["IT-T5-961"],
                                                          "SEM_RASTRO_DE_AUTORIZACAO": ["IT-T5-960"]})

    def test_a_linha_leva_a_porta_para_o_registo_do_ciclo(self):
        self.escrever([linkedin("IT-T5-970")], [])
        a = self.C.alimentar_linhas({"RODADAS": []}, raiz=self.raiz)
        self.assertEqual(a["SOCIAL"]["PORTA_SOCIAL"]["ACEITES"], ["IT-T5-970"], a["SOCIAL"])
        self.assertEqual(a["SOCIAL"]["UNIDADES_GOVERNADAS"], 1)
        self.assertEqual(a["SOCIAL"]["CANDIDATAS"], [])         # sem onda propria a linha nao recebe candidatas
        self.assertEqual(a["SOCIAL"]["ESTADO"], "BLOQUEADA_PERMISSAO_SOCIAL")


if __name__ == "__main__":
    unittest.main()
