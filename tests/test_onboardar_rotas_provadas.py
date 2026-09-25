# -*- coding: utf-8 -*-
"""Guardas da ponte rota-provada -> tabela do coletor (ROTAS-ELEGIVEIS-V1).

Sem rede, sem escrever na tabela real: o portao e trocado por uma lista, e a
escrita vai para um ficheiro temporario.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import onboardar_rotas_provadas as O  # noqa: E402
import sha_do_contrato as SHA  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402

AGORA = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)

AQ = {"STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL",
      "INDEX_URL": "https://a.it/", "LINK_PATTERN": "^https?://a\\.it/news/.+$", "MAX_TARGETS": 1}


def _cur(sid, aq=AQ):
    return {"SOURCE_ID": sid, "OWNER": "X", "NAME": "X", "TERRITORY": "T2",
            "BATCH_ID": "LOTE-HTML-ARTIGO", "OUTPUT_TYPE": "HTML", "ACQUISITION": dict(aq)}


def _prova(sid, v="ROUTE_PROVEN", doc="https://a.it/news/um-dois-tres", aq=AQ,
           provado_em=AGORA - timedelta(hours=2)):
    # PONTE-ONBOARD: a prova diz QUE contrato provou (impressao) e QUANDO.
    return {"SOURCE_ID": sid, "VEREDITO": v, "CAUSA": "c", "INDEX_URL": aq["INDEX_URL"],
            "CONTRATO_SHA256": SHA.do_contrato(_cur(sid, aq)),
            "PROVADO_EM": provado_em.isoformat() if provado_em else None,
            "LINK_PATTERN": aq["LINK_PATTERN"], "INDEX_HTTP": 200, "LINKS_DE_DETALHE": 3,
            "CANARIO": {"URL": doc, "BYTES": 5000, "HTML_KIND": "CONTENT",
                        "PARAGRAPH_CHARACTERS": 900}}


class Ponte(unittest.TestCase):
    def planear(self, elegiveis, provas, curator, com_contrato=()):
        with mock.patch.object(O.G, "elegiveis", return_value=list(elegiveis)):
            return O.planear(ctx={}, canario={"GERADO_EM": "2026-09-22T00:00", "LINHAS": provas},
                             curator={c["SOURCE_ID"]: c for c in curator},
                             com_contrato=set(com_contrato), agora=AGORA)

    def test_elegivel_provada_sem_contrato_entra_com_a_aquisicao_do_curator(self):
        p = self.planear(["IT-T2-001"], [_prova("IT-T2-001")], [_cur("IT-T2-001")])
        self.assertEqual(["IT-T2-001"], [l["SOURCE_ID"] for l in p["ENTRA"]])
        self.assertEqual(AQ, p["ENTRA"][0]["ACQUISITION"])

    def test_nao_elegivel_nunca_entra_mesmo_provada(self):
        p = self.planear([], [_prova("IT-T2-001")], [_cur("IT-T2-001")])
        self.assertEqual([], p["ENTRA"])

    def test_quem_ja_tem_contrato_nao_e_reescrito(self):
        p = self.planear(["IT-T2-001"], [_prova("IT-T2-001")], [_cur("IT-T2-001")],
                         com_contrato=["IT-T2-001"])
        self.assertEqual(([], []), (p["ENTRA"], p["FICA"]))

    def test_canario_nao_provado_fica_com_o_veredito_escrito(self):
        for v in ("UNKNOWN", "CAPABILITY_BLOCK", "POLICY_BLOCK"):
            p = self.planear(["IT-T2-001"], [_prova("IT-T2-001", v)], [_cur("IT-T2-001")])
            self.assertEqual([], p["ENTRA"])
            self.assertIn(v, p["FICA"][0]["PORQUE"])

    def test_sem_canario_fica(self):
        p = self.planear(["IT-T2-001"], [], [_cur("IT-T2-001")])
        self.assertIn("SEM_CANARIO", p["FICA"][0]["PORQUE"])

    def test_canario_de_outra_aquisicao_nao_vale(self):
        outra = dict(AQ, INDEX_URL="https://a.it/news/")
        p = self.planear(["IT-T2-001"], [_prova("IT-T2-001", aq=outra)], [_cur("IT-T2-001")])
        self.assertEqual([], p["ENTRA"])
        self.assertIn("OUTRA aquisicao", p["FICA"][0]["PORQUE"])

    def test_duas_fichas_pelo_mesmo_documento_so_a_primeira_entra(self):
        p = self.planear(["IT-T2-001", "IT-T2-002"],
                         [_prova("IT-T2-001"), _prova("IT-T2-002")],
                         [_cur("IT-T2-001"), _cur("IT-T2-002")])
        self.assertEqual(["IT-T2-001"], [l["SOURCE_ID"] for l in p["ENTRA"]])
        self.assertIn("DUPLICADA", p["FICA"][0]["PORQUE"])

    def test_mesmo_site_e_padrao_de_fonte_ja_contratada_fica_como_duplicada(self):
        outra_porta = dict(AQ, INDEX_URL="https://www.a.it/@@seletor-de-lingua/it")
        p = self.planear(["IT-T2-002"], [_prova("IT-T2-002", aq=outra_porta)],
                         [_cur("IT-T2-001"), _cur("IT-T2-002", aq=outra_porta)],
                         com_contrato=["IT-T2-001"])
        self.assertEqual([], p["ENTRA"])
        self.assertIn("DUPLICADA de fonte ja contratada: IT-T2-001", p["FICA"][0]["PORQUE"])

    def test_outro_site_com_o_mesmo_padrao_nao_e_duplicada(self):
        outro = dict(AQ, INDEX_URL="https://b.it/")
        p = self.planear(["IT-T2-002"], [_prova("IT-T2-002", aq=outro)],
                         [_cur("IT-T2-001"), _cur("IT-T2-002", aq=outro)],
                         com_contrato=["IT-T2-001"])
        self.assertEqual(["IT-T2-002"], [l["SOURCE_ID"] for l in p["ENTRA"]])

    def test_aplicar_acrescenta_sem_repetir(self):
        with tempfile.TemporaryDirectory() as d:
            t = Path(d, "t.json")
            t.write_text(json.dumps({"FONTES": [{"SOURCE_ID": "IT-T2-001"}]}), encoding="utf-8")
            with mock.patch.object(O, "TABELA", t):
                l = O.linha_da_tabela(_cur("IT-T2-002"), _prova("IT-T2-002"), "2026-09-22")
                self.assertEqual(1, O.aplicar([l, {"SOURCE_ID": "IT-T2-001"}]))
                self.assertEqual(1, O.aplicar([l]) + 1)
            self.assertEqual(2, len(json.loads(t.read_text(encoding="utf-8"))["FONTES"]))

    def test_o_ficheiro_nao_tem_source_id_literal(self):
        texto = (RAIZ / "curadoria" / "onboardar_rotas_provadas.py").read_text(encoding="utf-8")
        import re
        self.assertIsNone(re.search(r"IT-T\d+-\d{3}", texto))

    # -- PONTE-ONBOARD: o contrato provado e o contrato onboardado sao o mesmo --
    def test_prova_sem_impressao_do_contrato_fica(self):
        p0 = _prova("IT-T2-001")
        del p0["CONTRATO_SHA256"]
        p = self.planear(["IT-T2-001"], [p0], [_cur("IT-T2-001")])
        self.assertEqual([], p["ENTRA"])
        self.assertIn("sem CONTRATO_SHA256", p["FICA"][0]["PORQUE"])

    def test_mesma_entrada_e_padrao_mas_outro_contrato_fica(self):
        # INDEX_URL e LINK_PATTERN iguais, MAX_TARGETS diferente: a regra antiga deixava entrar
        outro = dict(AQ, MAX_TARGETS=30)
        p = self.planear(["IT-T2-001"], [_prova("IT-T2-001", aq=outro)], [_cur("IT-T2-001")])
        self.assertEqual([], p["ENTRA"])
        self.assertIn("OUTRA aquisicao", p["FICA"][0]["PORQUE"])

    def test_campo_que_o_coletor_nao_le_nao_obriga_a_reprovar(self):
        c = dict(_cur("IT-T2-001"), NOTAS="caracterizacao nova", EVIDENCE_REF="EV-9")
        p = self.planear(["IT-T2-001"], [_prova("IT-T2-001")], [c])
        self.assertEqual(["IT-T2-001"], [l["SOURCE_ID"] for l in p["ENTRA"]])

    def test_prova_velha_fica(self):
        velha = _prova("IT-T2-001", provado_em=AGORA - O.PROVA_MAX_IDADE - timedelta(minutes=1))
        p = self.planear(["IT-T2-001"], [velha], [_cur("IT-T2-001")])
        self.assertEqual([], p["ENTRA"])
        self.assertIn("VELHA", p["FICA"][0]["PORQUE"])

    def test_prova_no_limite_da_idade_entra(self):
        justa = _prova("IT-T2-001", provado_em=AGORA - O.PROVA_MAX_IDADE + timedelta(minutes=1))
        p = self.planear(["IT-T2-001"], [justa], [_cur("IT-T2-001")])
        self.assertEqual(["IT-T2-001"], [l["SOURCE_ID"] for l in p["ENTRA"]])

    def test_prova_sem_data_usa_a_do_ficheiro_e_sem_nenhuma_fica(self):
        p0 = _prova("IT-T2-001", provado_em=None)
        with mock.patch.object(O.G, "elegiveis", return_value=["IT-T2-001"]):
            sem = O.planear(ctx={}, canario={"LINHAS": [p0]}, curator={"IT-T2-001": _cur("IT-T2-001")},
                            com_contrato=set(), agora=AGORA)
            com = O.planear(ctx={}, canario={"GERADO_EM": (AGORA - timedelta(days=1)).isoformat(),
                                             "LINHAS": [p0]},
                            curator={"IT-T2-001": _cur("IT-T2-001")}, com_contrato=set(), agora=AGORA)
        self.assertEqual([], sem["ENTRA"])
        self.assertIn("sem data", sem["FICA"][0]["PORQUE"])
        self.assertEqual(["IT-T2-001"], [l["SOURCE_ID"] for l in com["ENTRA"]])

    def test_a_linha_da_tabela_leva_a_impressao_e_a_data_da_prova(self):
        p = self.planear(["IT-T2-001"], [_prova("IT-T2-001")], [_cur("IT-T2-001")])
        s = p["ENTRA"][0]["SONDAGEM"]
        self.assertEqual(SHA.do_contrato(_cur("IT-T2-001")), s["CONTRATO_SHA256"])
        self.assertTrue(s["PROVADO_EM"])

    def test_o_caso_medido_14_de_17_trocados_ficam_todos(self):
        # provas feitas com o HEAD velho (o defeito) contra os contratos do disco
        fix = json.loads((RAIZ / "tests" / "fixtures" / "ponte_onboard_17_contratos.json")
                         .read_text(encoding="utf-8"))
        cur = {s: dict(c, OWNER="X", NAME="X", TERRITORY="T", BATCH_ID="B") for s, c in fix["DISCO"].items()}
        provas = []
        for i, (s, c) in enumerate(sorted(fix["HEAD"].items())):
            provas.append({"SOURCE_ID": s, "VEREDITO": "ROUTE_PROVEN", "CAUSA": "c",
                           "CONTRATO_SHA256": SHA.do_contrato(c), "PROVADO_EM": AGORA.isoformat(),
                           "INDEX_HTTP": 200, "LINKS_DE_DETALHE": 3,
                           "CANARIO": {"URL": "https://x.it/doc-%d" % i, "BYTES": 1, "HTML_KIND": "CONTENT",
                                       "PARAGRAPH_CHARACTERS": 9}})
        with mock.patch.object(O.G, "elegiveis", return_value=sorted(fix["DISCO"])):
            p = O.planear(ctx={}, canario={"LINHAS": provas}, curator=cur, com_contrato=set(), agora=AGORA)
        # 9 sem prova (nao estavam no HEAD) + 5 com outro contrato ficam; so as 3 iguais entram
        self.assertEqual(3, len(p["ENTRA"]))
        self.assertEqual(14, len(p["FICA"]))

    def test_aplicar_sem_novas_nao_toca_na_tabela(self):
        with tempfile.TemporaryDirectory() as d:
            t = Path(d, "t.json")
            t.write_text(json.dumps({"FONTES": [{"SOURCE_ID": "IT-T2-001"}]}), encoding="utf-8")
            antes = t.stat().st_mtime_ns
            with mock.patch.object(O, "TABELA", t):
                self.assertEqual(0, O.aplicar([{"SOURCE_ID": "IT-T2-001"}]))
            self.assertEqual(antes, t.stat().st_mtime_ns)
            self.assertFalse(Path(d, "t.json.tmp").exists())


class GanchoDoSupervisor(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.prova = Path(self.d.name, "ROTAS-ELEGIVEIS-V1.json")
        self.prova.write_text('{"LINHAS": []}', encoding="utf-8")
        self.p = mock.patch.object(O, "CANARIO", self.prova)
        self.p.start()
        self.chamadas = []
        self.plano = {"ENTRA": [{"SOURCE_ID": "IT-T2-001"}], "FICA": []}

    def tearDown(self):
        self.p.stop()
        self.d.cleanup()

    def volta(self, estado, agora):
        return O.onboardar_se_mudou(
            estado, agora=agora,
            planear_fn=lambda agora: (self.chamadas.append("planear"), self.plano)[1],
            aplicar_fn=lambda entra: (self.chamadas.append("aplicar"), len(entra))[1])

    def test_primeira_volta_onboarda_e_guarda_a_impressao_da_prova(self):
        e = {}
        r = self.volta(e, AGORA)
        self.assertEqual(("ONBOARDOU", 1), (r["ACCAO"], r["ESCRITAS"]))
        self.assertTrue(e["ONBOARD_PROVA_SHA"])

    def test_sem_prova_nova_e_dentro_do_intervalo_nao_faz_nada(self):
        e = {}
        self.volta(e, AGORA)
        r = self.volta(e, AGORA + O.ONBOARD_INTERVALO - timedelta(seconds=1))
        self.assertEqual("NADA_MUDOU", r["ACCAO"])
        self.assertEqual(["planear", "aplicar"], self.chamadas)

    def test_prova_nova_corre_logo(self):
        e = {}
        self.volta(e, AGORA)
        self.prova.write_text('{"LINHAS": [1]}', encoding="utf-8")
        self.assertNotEqual("NADA_MUDOU", self.volta(e, AGORA + timedelta(seconds=5))["ACCAO"])

    def test_passado_o_intervalo_corre_mesmo_sem_prova_nova(self):
        e = {}
        self.volta(e, AGORA)
        self.assertNotEqual("NADA_MUDOU", self.volta(e, AGORA + O.ONBOARD_INTERVALO)["ACCAO"])

    def test_sem_ficheiro_de_prova_nao_planeia(self):
        self.prova.unlink()
        self.assertEqual("SEM_PROVA", self.volta({}, AGORA)["ACCAO"])
        self.assertEqual([], self.chamadas)

    def test_ninguem_a_entrar_nao_chama_aplicar(self):
        self.plano = {"ENTRA": [], "FICA": [{"SOURCE_ID": "x"}]}
        self.assertEqual("NINGUEM_ENTROU", self.volta({}, AGORA)["ACCAO"])
        self.assertEqual(["planear"], self.chamadas)

    def _loop_do_supervisor(self, onboard):
        """Corre o `_loop` verdadeiro do supervisor com o resto trocado por dublos:
        duas voltas e depois sai. Devolve os eventos anotados."""
        import supervisor as S
        eventos = []
        voltas = [("WORKER_OK", {}, None), ("WORKER_OK", {}, None), KeyboardInterrupt()]
        with mock.patch.object(S, "uma_volta_sup", side_effect=voltas),              mock.patch.object(S.time, "sleep"),              mock.patch.object(S, "_anotar", side_effect=eventos.append),              mock.patch.object(S, "_ler_estado", return_value={}),              mock.patch.object(S, "_gravar_estado"),              mock.patch.object(S.F, "recuperar_orfas", return_value=[]),              mock.patch.object(O, "onboardar_se_mudou", side_effect=onboard),              mock.patch("ready_split.remedir", side_effect=AssertionError("LIVRO REAL NUM TESTE")),              mock.patch("gatilho_discovery.revalidar_legacy_se_devido", side_effect=AssertionError("LIVRO REAL NUM TESTE")):
            with self.assertRaises(KeyboardInterrupt):
                S._loop(1.0, 0)
        return eventos

    def test_o_loop_do_supervisor_chama_o_onboarding_em_cada_volta(self):
        chamadas = []
        ev = self._loop_do_supervisor(lambda e: (chamadas.append(1), {"ACCAO": "ONBOARDOU", "ESCRITAS": 1})[1])
        self.assertEqual(2, len(chamadas))
        self.assertEqual(2, sum(1 for e in ev if e.get("EVENTO") == "ONBOARDING"))

    def test_um_erro_do_onboarding_fica_no_diario_e_o_supervisor_continua(self):
        def rebenta(e):
            raise RuntimeError("tabela ilegivel")
        ev = self._loop_do_supervisor(rebenta)
        erros = [e for e in ev if e.get("EVENTO") == "ONBOARDING_ERRO"]
        self.assertEqual(2, len(erros))            # duas voltas, duas anotacoes: nao morreu na 1.a
        self.assertIn("tabela ilegivel", erros[0]["ERRO"])

    def test_nada_mudou_nao_enche_o_diario(self):
        ev = self._loop_do_supervisor(lambda e: {"ACCAO": "NADA_MUDOU"})
        self.assertEqual([], [e for e in ev if str(e.get("EVENTO", "")).startswith("ONBOARDING")])


if __name__ == "__main__":
    unittest.main()
