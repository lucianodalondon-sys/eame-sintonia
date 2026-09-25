# -*- coding: utf-8 -*-
"""LEGACY-99 B · o canal YouTube vai para a rota do Scrap — UM SO DONO da rota.

O Curator nao escreve a rota com a mao dele: `importar_do_coletor.pelo_scrap` chama o
bloco 4 do desbloqueio (o dono da troca feed -> fase `canal-youtube`), so para as
fontes pedidas, e manda-as ao remedir. O canario e uma colheita do Scrap, julgada pela
regua social: nada aqui promove, nem o Curator vai ao YouTube.

Sem rede e sem livros reais: livro, tabela e ledger sao temporarios; o que o Scrap
declara e um literal; o `remedir` e um dublo.
"""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import importar_do_coletor as I   # noqa: E402
import collection_gate as CG      # noqa: E402
import ready_split as RS          # noqa: E402
import rota_do_scrap_youtube as RSY  # noqa: E402
import worker as W                # noqa: E402
import lifecycle as LC            # noqa: E402

# canais inventados (24 caracteres, forma de channel_id) — nao colidem com o .mjs real
C1, C2 = "UCtestelegacy99v4aaaaaaa", "UCtestelegacy99v4bbbbbbb"
DECLARADO = {"FASE_EXISTE": True, "PLATAFORMA": RSY.PLATAFORMA, "CAPACIDADE": RSY.CAPACIDADE,
             "FILTROS": {RSY.FILTRO: "channel_id"}, "DECISAO": "ALLOWED",
             "ROTA": "youtube-data-api-v3:playlistItems.list"}


def feed(sid, canal):
    return {"SOURCE_ID": sid, "NAME": "Canale " + sid, "OWNER": "Canale", "TERRITORY": "T10",
            "BATCH_ID": "LOTE-YOUTUBE-FEED", "OUTPUT_TYPE": "VIDEO_METADATA",
            "CANONICAL_ENTRY_URL": "https://www.youtube.com/channel/" + canal,
            "SOURCE_NATIVE_ID": canal, "SOURCE_NATIVE_ID_KIND": "YOUTUBE_CHANNEL_ID",
            "IDENTITY": {"DOCUMENT_ID": sid + ":YT:{video.videoId}"},
            "ACQUISITION": {"STRATEGY": "YOUTUBE_CHANNEL_FEED", "CHANNEL_ID": canal,
                            "FEED_URL": "https://www.youtube.com/feeds/videos.xml?channel_id=" + canal,
                            "MAX_TARGETS": 15}}


def linha(sid, canal, match="YES"):
    return {"SOURCE_ID": sid, "TERRITORY": "T10", "OUTPUT_TYPE": "HTML", "SOURCE_NATIVE_ID": canal,
            "ACQUISITION": {"STRATEGY": "CUSTOM_ADAPTER", "ADAPTER_ID": "CANAL_PUBLICO_YOUTUBE_V1",
                            "CHANNEL_ID": canal, "MAX_TARGETS": 15},
            "SONDAGEM": {"IDENTITY_MATCH": match, "SONDADO_EM": "2026-09-20"}}


HTML = {"SOURCE_ID": "IT-T5-006", "TERRITORY": "T5", "OUTPUT_TYPE": "HTML",
        "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": "https://www.cnr.it/it/news"}}


class PeloScrap(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.cur = Path(self.d.name, "cur.json")
        self.tab = Path(self.d.name, "tab.json")
        self.led = Path(self.d.name, "ledger.jsonl")
        self.escrever([feed("IT-T10-017", C1), feed("IT-T10-018", C2), HTML],
                      [linha("IT-T10-017", C1), linha("IT-T10-018", C2), HTML])
        self.ps = [mock.patch.object(I, "CURATOR", self.cur), mock.patch.object(I, "TABELA", self.tab),
                   mock.patch.object(I, "LEDGER", self.led),
                   mock.patch.object(I, "planear", return_value={"IMPORTA": [], "FICA": [], "PELO_SCRAP": [
                       {"SOURCE_ID": "IT-T10-017"}, {"SOURCE_ID": "IT-T10-018"}]}),
                   # o registo de alocacao real fica fora (so le, mas a prova nao depende dele)
                   mock.patch.object(RSY, "ALLOCATION", Path(self.d.name, "sem-alloc.json")),
                   mock.patch.object(LC, "registar", side_effect=AssertionError("pelo_scrap nao mexe no livro"))]
        for p in self.ps:
            p.start()

    def tearDown(self):
        for p in self.ps:
            p.stop()
        self.d.cleanup()

    def escrever(self, livro, tabela):
        self.cur.write_text(json.dumps({"FONTES": livro}, ensure_ascii=False, indent=1), encoding="utf-8")
        self.tab.write_text(json.dumps({"FONTES": tabela}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        self.antes = (self.cur.read_bytes(), self.tab.read_bytes())

    def correr(self, ids):
        chamadas = []
        r = I.pelo_scrap(ids, declarado=DECLARADO,
                         remedir_fn=lambda x: (chamadas.append(list(x)), [{"FEITO": True} for _ in x])[1])
        return r, chamadas

    def fontes(self, p):
        return {c["SOURCE_ID"]: c for c in json.loads(p.read_text(encoding="utf-8"))["FONTES"]}

    def test_so_a_pedida_passa_para_a_fase_do_scrap_e_vai_ao_remedir(self):
        r, chamadas = self.correr(["IT-T10-017"])
        self.assertEqual([["IT-T10-017"]], chamadas)
        self.assertEqual(1, r["REMEDIDAS"])
        liv, tab = self.fontes(self.cur), self.fontes(self.tab)
        aq = liv["IT-T10-017"]["ACQUISITION"]
        self.assertEqual(RSY.acquisition(C1, DECLARADO), aq)
        self.assertEqual((True, ), RSY.conferir(aq, DECLARADO)[:1])
        self.assertNotIn("feeds/videos.xml", json.dumps(aq))
        # o que nao foi pedido fica byte a byte
        self.assertEqual(feed("IT-T10-018", C2), liv["IT-T10-018"])
        self.assertEqual(HTML, liv["IT-T5-006"])
        self.assertEqual(linha("IT-T10-018", C2), tab["IT-T10-018"])
        # na tabela do coletor so se ACRESCENTA quem colhe; a aquisicao do motor fica
        self.assertEqual(RSY.EXECUTOR, tab["IT-T10-017"]["COLETADO_POR"]["EXECUTOR"])
        self.assertEqual(linha("IT-T10-017", C1)["ACQUISITION"], tab["IT-T10-017"]["ACQUISITION"])
        ledger = [json.loads(x) for x in self.led.read_text(encoding="utf-8").splitlines()]
        self.assertEqual({("livro", "IT-T10-017"), ("tabela", "IT-T10-017")},
                         {(x["LIVRO"], x["SOURCE_ID"]) for x in ledger})
        self.assertTrue(all(x["MISSAO"] == I.MISSAO_B and x["DECISAO"] == "D17.4" for x in ledger))
        self.assertFalse(Path(self.d.name, "cur.json.tmp").exists())

    def test_se_o_bloco_4_salta_nada_se_escreve(self):
        self.escrever([feed("IT-T10-017", C1), feed("IT-T10-018", C2), HTML],
                      [linha("IT-T10-017", C1, match="NO"), linha("IT-T10-018", C2), HTML])
        for ids in (["IT-T10-017"], ["IT-T10-018", "IT-T10-017"]):
            with self.subTest(ids=ids), self.assertRaises(I.ImportacaoInvalida) as e:
                I.pelo_scrap(ids, declarado=DECLARADO, remedir_fn=lambda x: self.fail("nao devia remedir"))
            self.assertIn("IDENTITY_MATCH", str(e.exception))
            self.assertEqual(self.antes, (self.cur.read_bytes(), self.tab.read_bytes()))
        self.assertFalse(self.led.exists())

    def test_canal_de_duas_fontes_e_colisao_e_para(self):
        self.escrever([feed("IT-T10-017", C1), feed("IT-T10-018", C1), HTML],
                      [linha("IT-T10-017", C1), linha("IT-T10-018", C1), HTML])
        with self.assertRaises(I.ImportacaoInvalida) as e:
            I.pelo_scrap(["IT-T10-017"], declarado=DECLARADO, remedir_fn=lambda x: self.fail("nao"))
        self.assertIn("colisao", str(e.exception))
        self.assertEqual(self.antes, (self.cur.read_bytes(), self.tab.read_bytes()))

    def test_o_scrap_que_nao_declara_a_rota_hoje_para(self):
        with self.assertRaises(I.ImportacaoInvalida):
            I.pelo_scrap(["IT-T10-017"], declarado=dict(DECLARADO, DECISAO="ROUTE_NOT_ALLOWED"),
                         remedir_fn=lambda x: self.fail("nao"))
        self.assertEqual(self.antes, (self.cur.read_bytes(), self.tab.read_bytes()))

    def test_fora_do_plano_recusa(self):
        with self.assertRaises(I.ImportacaoInvalida):
            I.pelo_scrap(["IT-T5-006"], declarado=DECLARADO, remedir_fn=lambda x: self.fail("nao"))
        self.assertEqual(self.antes, (self.cur.read_bytes(), self.tab.read_bytes()))

    def test_o_remedir_por_omissao_e_o_de_ready_split(self):
        with mock.patch.object(RS, "remedir", return_value=[{"FEITO": True}]) as rm:
            I.pelo_scrap(["IT-T10-017"], declarado=DECLARADO)
        self.assertEqual(["IT-T10-017"], rm.call_args.args[0])
        self.assertIn("nunca READY daqui", rm.call_args.kwargs["motivo"])


class UmSoDono(unittest.TestCase):
    """Depois da troca, o circuito do Curator nao vai ao YouTube e nao promove sozinho."""
    NOVO = dict(feed("IT-T10-017", C1), ACQUISITION=RSY.acquisition(C1, DECLARADO))

    def test_o_canario_do_curator_nao_corre_a_rota_do_scrap(self):
        import canario as CAN
        with mock.patch.object(CAN, "buscar", side_effect=AssertionError("o Curator nao vai ao YouTube")):
            r, d = W.etapa_canary("IT-T10-017", copy.deepcopy(self.NOVO))
        self.assertEqual(("BLOCK", "DO_SCRAP"), (r, d["CANARIO"]))

    def test_sem_veredito_da_regua_social_fica_legacy(self):
        promo = {"OBSERVED_AT": "2026-09-25T00:00:00+00:00", "EVIDENCE_REF": "EV-1"}
        self.assertEqual(RS.REGUA_LEGACY, RS.passos_da_promocao(promo, {"DADOS": {}}, self.NOVO)["REGUA"])

    def test_o_plano_manda_o_canal_com_contrato_pelo_scrap_e_sem_contrato_fica(self):
        ctx = {"livro": {"TRANSICOES": [{"SOURCE_ID": s, "NEW_STATE": "READY_FOR_COLLECTION"}
                                        for s in ("IT-T10-017", "IT-T10-018")]},
               "contratos": {"IT-T10-017": feed("IT-T10-017", C1)}}
        with mock.patch.object(CG, "avaliar", return_value={"MOTIVO": CG.READY_LEGACY}), \
             mock.patch.object(RS, "ultima_promocao", return_value=None):
            p = I.planear(ctx=ctx, tabela={"IT-T10-018": linha("IT-T10-018", C2)})
        self.assertEqual(["IT-T10-017"], [x["SOURCE_ID"] for x in p["PELO_SCRAP"]])
        self.assertEqual(["IT-T10-018"], [x["SOURCE_ID"] for x in p["FICA"]])
        self.assertEqual([], p["IMPORTA"])


if __name__ == "__main__":
    unittest.main()
