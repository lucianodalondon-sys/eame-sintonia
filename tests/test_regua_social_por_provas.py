# -*- coding: utf-8 -*-
"""SOCIAL-ATE-A-SALA · B — a regua social julga PROVAS, nunca o nome da fase.

Um envelope de `audio-youtube`, `captura-reel` ou `video-linkedin` satisfaz um contrato
de outra fase SO quando cada item prova quatro coisas: a conta de origem, a data de
publicacao (com precisao), OWNER_AUTHORIZED=SIM, e a ligacao conta->publicacao->midia.
Falta uma: FALHA, e o motivo nomeia-a.

Os tres casos do YouTube sao os REAIS de docs/sintonia-scrap/YT-METADADOS-PROVA-3CANAIS.md,
com cada valor rastreado em tests/dados/social-sala/YT-METADADOS-3CANAIS.json. O Reel e o
LinkedIn sao montados com os NOMES DE CAMPO que os adaptadores escrevem (lidos no codigo:
`ferramentas/reel_transcricao.py`, `coleta/adaptador_linkedin.py::_adquirir_um`) — nao ha
envelope real destes dois no repositorio, e isso fica dito.

`julgar()` e pura: sem rede, sem disco, sem banco.
"""
import copy
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
sys.path.insert(0, str(RAIZ / "curadoria"))
import regua_social as R  # noqa: E402

CASOS = json.loads((RAIZ / "tests" / "dados" / "social-sala" / "YT-METADADOS-3CANAIS.json")
                   .read_text(encoding="utf-8"))["CASOS"]


def contrato_yt(caso):
    return {"SOURCE_ID": caso["SOURCE_ID"], "NAME": caso["NAME"],
            "ACQUISITION": {"STRATEGY": "SCRAP_FASE", "FASE": "canal-youtube", "PLATFORM": "YOUTUBE",
                            "CAPACIDADE": "youtube.channel.discovery", "CHANNEL_ID": caso["CHANNEL_ID"]}}


def envelope(sid, itens, fase):
    return {"SOURCE_ID_DO_PEDIDO": sid, "FASE": fase, "COLHEITA": itens,
            "SUPORTE": [{"ESPECIE": "RUN_RECEIPT", "RESUMO": {"RESULT": "OK"}}]}


def julgar_caso(caso, fase=None, obs=None):
    c = contrato_yt(caso)
    env = envelope(caso["SOURCE_ID"], [{"OBSERVACAO": obs or caso["OBSERVACAO"]}], fase or caso["FASE_DA_CORRIDA"])
    return R.julgar(env, caso["SOURCE_ID"], c["ACQUISITION"]["FASE"], caso["RAW_NO_BANCO"],
                    nome_da_fonte=c["NAME"], contrato=c)


class OsTresCasosReaisDoYtMetadados(unittest.TestCase):
    """Antes: FALHA x3 'o envelope e da fase audio-youtube, e o contrato pede canal-youtube'."""

    def test_1_IT_T9_029_com_as_quatro_provas_fica_READY(self):
        v, porque = julgar_caso(CASOS[0])
        self.assertEqual(v, R.READY, porque)

    def test_2_T5_e_T3_reprovam_so_pela_midia_que_o_repositorio_nao_guarda(self):
        for caso in CASOS[1:]:
            v, porque = julgar_caso(caso)
            self.assertEqual(v, R.FALHA, caso["SOURCE_ID"])
            self.assertIn("sem a midia adquirida", porque, caso["SOURCE_ID"])
            for prova in ("CANAL_DE_ORIGEM", "DATA_DE_PUBLICACAO", "AUTORIZACAO_DO_DONO"):
                self.assertNotIn(prova, porque, caso["SOURCE_ID"])

    def test_3_com_o_sha_do_audio_escrito_T5_e_T3_passam(self):
        """SINTETICO: o sha abaixo nao e medido — prova so que a midia e a UNICA prova em falta."""
        for caso in CASOS[1:]:
            ob = dict(caso["OBSERVACAO"], AUDIO_SHA256="0" * 64)
            v, porque = julgar_caso(caso, obs=ob)
            self.assertEqual(v, R.READY, "%s: %s" % (caso["SOURCE_ID"], porque))

    def test_4_o_veredito_antigo_pelo_nome_nao_existe_mais(self):
        for caso in CASOS:
            _, porque = julgar_caso(caso)
            self.assertNotIn("A_EQUIVALENCIA_NAO_ESTA_DECLARADA", porque)


class NuncaPeloNomeDaFase(unittest.TestCase):
    def test_5_o_mesmo_item_tem_o_mesmo_veredito_com_qualquer_nome_de_fase(self):
        """O nome nao passa nem reprova: so muda a frase do contexto."""
        for caso in CASOS:
            base = julgar_caso(caso)[0]
            for nome in ("audio-youtube", "captura-reel", "video-linkedin", "fase-inventada", ""):
                self.assertEqual(julgar_caso(caso, fase=nome)[0], base, (caso["SOURCE_ID"], nome))

    def test_6_cada_prova_que_falta_reprova_com_o_nome_dela(self):
        caso = CASOS[0]
        estragos = {
            "CANAL_DE_ORIGEM": {"CHANNEL_ID": None, "CHANNEL_URL": None},
            "DATA_DE_PUBLICACAO": {"PUBLISHED_AT": "NAO SEI"},
            "AUTORIZACAO_DO_DONO": {"OWNER_AUTHORIZED": "NAO"},
            "LIGACAO_CANAL_VIDEO_AUDIO": {"AUDIO_REFERENCE": "audio-cache/outro.wav"},
        }
        for prova, estraga in estragos.items():
            ob = {k: v for k, v in dict(caso["OBSERVACAO"], **estraga).items() if v is not None}
            v, porque = julgar_caso(caso, obs=ob)
            self.assertEqual(v, R.FALHA, prova)
            self.assertIn(prova, porque, prova)

    def test_6b_midia_com_zero_bytes_nao_e_midia(self):
        ob = dict(CASOS[0]["OBSERVACAO"], AUDIO_BYTES=0)
        v, porque = julgar_caso(CASOS[0], obs=ob)
        self.assertEqual(v, R.FALHA)
        self.assertIn("sem a midia adquirida", porque)

    def test_7_as_provas_nao_recebem_a_fase(self):
        """A funcao das provas nem tem onde receber a fase: e o desenho que o garante."""
        import inspect
        self.assertEqual(list(inspect.signature(R.provas_sociais).parameters), ["ob", "contrato"])


# ── O REEL (captura-reel) — com os campos de `reel_transcricao.transcrever_reel` ──────────
IG_SID, IG_HANDLE, POST = "IT-T5-900", "oliveti_sezze", "DAbCdEfGhIj"
CONTRATO_IG = {"SOURCE_ID": IG_SID, "NAME": "Oliveti Sezze",
               "ACQUISITION": {"STRATEGY": "SCRAP_FASE", "FASE": "audio-reel", "PLATFORM": "INSTAGRAM",
                               "INSTAGRAM_HANDLE": IG_HANDLE}}


def reel(**mudar):
    r = {"REEL": {"PLATFORM": "INSTAGRAM", "POST_ID": POST,
                  "SOURCE_URL": "https://www.instagram.com/reel/%s/" % POST,
                  "ACCOUNT_ID": "NOT_KNOWN", "ACCOUNT_URL": "https://www.instagram.com/%s/" % IG_HANDLE,
                  "ACCOUNT_HANDLE_FROM_URL": IG_HANDLE, "PUBLISHED_AT": "2026-09-01T10:00:00Z",
                  "PUBLISHED_AT_PRECISION": "SECOND"},
         "RAW": {"SHA256": "a" * 64, "BYTES": 812345, "STORAGE_LOCATION": "data/samples/REELS/%s.mp4" % POST},
         "OWNER_AUTHORIZED": "SIM", "PLATFORM_POLICY_STATUS": "DISALLOWED", "TRANSCRIPT_STATE": "OK"}
    for k, v in mudar.items():
        alvo, _, campo = k.partition("__")
        if campo:
            r[alvo] = dict(r[alvo], **{campo: v})
        else:
            r[alvo] = v
    return {"OBSERVACAO": r}


def julgar_reel(it, fase="captura-reel", contrato=CONTRATO_IG, raw=1):
    return R.julgar(envelope(IG_SID, [it], fase), IG_SID, contrato["ACQUISITION"]["FASE"], raw,
                    contrato=contrato)


class OReel(unittest.TestCase):
    def test_8_reel_com_as_quatro_provas_fica_READY(self):
        v, porque = julgar_reel(reel())
        self.assertEqual(v, R.READY, porque)

    def test_9_reel_de_outra_conta_reprova_na_ligacao(self):
        v, porque = julgar_reel(reel(REEL__ACCOUNT_URL="https://www.instagram.com/outra/",
                                     REEL__ACCOUNT_HANDLE_FROM_URL="outra"))
        self.assertEqual(v, R.FALHA)
        self.assertIn("LIGACAO_CONTA_PUBLICACAO_MIDIA", porque)

    def test_10_reel_com_duas_contas_diferentes_reprova(self):
        """Uma conta que concorda e outra que discorda nao e prova: e conflito."""
        v, porque = julgar_reel(reel(REEL__ACCOUNT_ID="outra"))
        self.assertEqual(v, R.FALHA)
        self.assertIn("LIGACAO_CONTA_PUBLICACAO_MIDIA", porque)

    def test_11_reel_sem_os_bytes_reprova(self):
        v, porque = julgar_reel(reel(RAW=None))
        self.assertEqual(v, R.FALHA)
        self.assertIn("sem a midia adquirida", porque)

    def test_12_reel_cuja_midia_nao_nomeia_a_publicacao_reprova(self):
        v, porque = julgar_reel(reel(RAW__STORAGE_LOCATION="data/samples/REELS/outro.mp4"))
        self.assertEqual(v, R.FALHA)
        self.assertIn("a midia guardada nao nomeia a publicacao", porque)

    def test_12b_reel_cuja_pagina_e_de_outra_publicacao_reprova(self):
        v, porque = julgar_reel(reel(REEL__SOURCE_URL="https://www.instagram.com/reel/OUTROCODIGO/"))
        self.assertEqual(v, R.FALHA)
        self.assertIn("a pagina da publicacao nao nomeia", porque)

    def test_13_reel_sem_data_ou_sem_precisao_reprova(self):
        for estraga in ({"REEL__PUBLISHED_AT": "NOT_KNOWN"}, {"REEL__PUBLISHED_AT_PRECISION": None}):
            v, porque = julgar_reel(reel(**estraga))
            self.assertEqual(v, R.FALHA, estraga)
            self.assertIn("DATA_DE_PUBLICACAO", porque, estraga)

    def test_14_reel_sem_autorizacao_reprova(self):
        v, porque = julgar_reel(reel(OWNER_AUTHORIZED="NAO"))
        self.assertEqual(v, R.FALHA)
        self.assertIn("AUTORIZACAO_DO_DONO", porque)

    def test_15_contrato_sem_conta_nao_prova_a_ligacao(self):
        c = copy.deepcopy(CONTRATO_IG)
        del c["ACQUISITION"]["INSTAGRAM_HANDLE"]
        v, porque = julgar_reel(reel(), contrato=c)
        self.assertEqual(v, R.FALHA)
        self.assertIn("o contrato nao declara", porque)

    def test_16_visto_nao_e_guardado_sem_linha_RAW_no_banco(self):
        v, porque = julgar_reel(reel(), raw=0)
        self.assertEqual(v, R.FALHA)
        self.assertIn("0 linhas RAW", porque)


# ── O VIDEO DO LINKEDIN — com os campos de `adaptador_linkedin._adquirir_um` ─────────────
LI_SID, SLUG, ACT = "IT-T9-024", "gruppocaviro", "7490681050906439680"
CONTRATO_LI = {"SOURCE_ID": LI_SID, "NAME": "Gruppo Caviro",
               "ACQUISITION": {"STRATEGY": "SCRAP_FASE", "FASE": "posts-linkedin", "PLATFORM": "LINKEDIN",
                               "LINKEDIN_SLUG": SLUG}}


def post_li(**raw):
    ob = {"NATIVE_ID": ACT, "URL": "https://www.linkedin.com/feed/update/urn:li:activity:%s/" % ACT,
          "SOURCE_ACCOUNT": "https://www.linkedin.com/company/%s/" % SLUG,
          "PUBLISHED_AT": "2026-08-05T08:12:12Z", "PUBLISHED_AT_PRECISION": "SECOND",
          "OWNER_AUTHORIZED": "SIM", "PLATFORM_POLICY_STATUS": "DISALLOWED",
          "RAW": dict({"CREATOR_NAME": "Gruppo Caviro", "CREATOR_URL": "https://it.linkedin.com/company/%s" % SLUG,
                       "ACTIVITY_ID": ACT, "VIDEO_SHA256": "b" * 64, "VIDEO_BYTES": 7464653,
                       "VIDEO_STORAGE_LOCATION": "data/samples/LINKEDIN/video/%s__bbbbbbbbbbbbbbbb.mp4" % ACT},
                      **raw)}
    return {"OBSERVACAO": ob}


def julgar_li(it, contrato=CONTRATO_LI):
    return R.julgar(envelope(LI_SID, [it], "video-linkedin"), LI_SID, contrato["ACQUISITION"]["FASE"], 1,
                    slug=SLUG, nome_da_fonte=contrato["NAME"], contrato=contrato)


class OVideoDoLinkedIn(unittest.TestCase):
    def test_17_video_da_propria_organizacao_fica_READY(self):
        v, porque = julgar_li(post_li())
        self.assertEqual(v, R.READY, porque)

    def test_18_republicacao_de_outra_organizacao_reprova_na_ligacao(self):
        v, porque = julgar_li(post_li(CREATOR_URL="https://it.linkedin.com/company/abc-interreg"))
        self.assertEqual(v, R.FALHA)
        self.assertIn("LIGACAO_CONTA_PUBLICACAO_MIDIA", porque)

    def test_18b_sem_o_autor_declarado_o_endereco_nao_serve_de_conta(self):
        """No LinkedIn o SOURCE_ACCOUNT e o endereco do POST (medido no adaptador), nao a conta."""
        it = post_li()
        del it["OBSERVACAO"]["RAW"]["CREATOR_URL"]
        v, porque = julgar_li(it)
        self.assertEqual(v, R.FALHA)
        self.assertIn("CONTA_DE_ORIGEM", porque)

    def test_19_post_sem_os_bytes_do_video_reprova(self):
        v, porque = julgar_li(post_li(VIDEO_SHA256=None, VIDEO_BYTES=None, VIDEO_BYTES_ACQUIRED=False))
        self.assertEqual(v, R.FALHA)
        self.assertIn("sem a midia adquirida", porque)


if __name__ == "__main__":
    unittest.main(verbosity=2)
