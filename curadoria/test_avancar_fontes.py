#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CUR-PRONTA (D28): o robo leva a fonte ja achada ate PRONTA.

Prova, sem rede e em pastas temporarias:
  1. as regras do AVANCAR (quem entra, quem fica de fora e porque);
  2. o gatilho poe o AVANCO antes da procura de fontes novas;
  3. o BUILD_CONTRACT importa a linha da tabela do coletor sem a mudar;
  4. a tabela da maquina de estados do FUNIL cobre todo o estado e aponta para
     codigo que existe.
"""
import inspect
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import avancar_fontes as AV       # noqa: E402
import fila as F                  # noqa: E402
import funil_do_curador as FU     # noqa: E402
import gatilho_discovery as GD    # noqa: E402
import lifecycle as LC            # noqa: E402

AGORA = datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc)
HTML = {"ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": "https://ex.it/news/"}}


def _t(sid, tipo, status, quando=AGORA - timedelta(days=3)):
    return {"SOURCE_ID": sid, "TASK_TYPE": tipo, "STATUS": status,
            "UPDATED_AT": quando.isoformat()}


class AsRegras(unittest.TestCase):

    def _cands(self, **kw):
        base = dict(estados={}, tarefas=[], contratos={}, reguas={}, tabela={},
                    candidatas=[], caract=[], ponte={})
        base.update(kw)
        return AV.candidatas_a_avancar(AGORA, **base)

    def _regras(self, **kw):
        return {c["SOURCE_ID"]: c["REGRA"] for c in self._cands(**kw)}

    def test_cada_regra_dispara_no_seu_estado(self):
        r = self._regras(
            estados={"A": LC.DEGRADED, "B": LC.DEGRADED, "C": LC.READY_FOR_COLLECTION,
                     "D": LC.READY_FOR_COLLECTION, "E": LC.CONTRACT_PENDING,
                     "G": LC.RETRY_AFTER},
            contratos={"A": HTML, "C": HTML, "G": HTML},
            tabela={"B": HTML, "D": HTML},
            reguas={"C": "LEGACY", "D": "LEGACY"})
        self.assertEqual(r, {"A": "DEGRADADA", "B": "DEGRADADA_COLETOR", "C": "READY_LEGACY",
                             "D": "LEGACY_COLETOR", "E": "SEM_CONTRATO", "G": "ADIADA"})

    def test_ready_da_regua_de_hoje_nao_entra(self):
        self.assertEqual(self._regras(estados={"C": LC.READY_FOR_COLLECTION},
                                      contratos={"C": HTML}, reguas={"C": "DETAIL/v1"}), {})

    def test_os_estados_da_r1_nao_sao_deste_modulo(self):
        """CONTRACTED_CANARY_FAILED e CANARY_PENDING: dono R1. Dois donos a
        enfileirar a mesma fonte com tarefas diferentes e o defeito que se evita."""
        r = self._regras(estados={"X": LC.CONTRACTED_CANARY_FAILED, "Y": LC.CANARY_PENDING},
                         contratos={"X": HTML, "Y": HTML})
        self.assertEqual(r, {})

    def test_parados_e_semantica_nao_entram(self):
        estados = {s: s for s in LC.PARADOS}
        self.assertEqual(self._regras(estados=estados,
                                      contratos={s: HTML for s in estados}), {})

    def test_youtube_pelo_feed_nao_e_re_medido_pelo_feed(self):
        yt = {"ACQUISITION": {"STRATEGY": "YOUTUBE_CHANNEL_FEED"}}
        self.assertEqual(self._regras(estados={"Y": LC.READY_FOR_COLLECTION},
                                      contratos={"Y": yt}, reguas={"Y": "LEGACY"}), {})

    def test_retirada_por_decisao_nao_volta_por_maquina(self):
        c = dict(HTML, ESTADO_CATALOGO="RETIRADA_POR_DECISAO")
        self.assertEqual(self._regras(estados={"C": LC.READY_FOR_COLLECTION},
                                      contratos={"C": c}, reguas={"C": "LEGACY"}), {})

    def test_tarefa_aberta_ou_recente_nao_repete(self):
        est = {"A": LC.DEGRADED}
        con = {"A": HTML}
        self.assertEqual(self._regras(estados=est, contratos=con,
                                      tarefas=[_t("A", F.CANARY, F.PENDING)]), {})
        self.assertEqual(self._regras(estados=est, contratos=con,
                                      tarefas=[_t("A", F.REPAIR, F.DONE, AGORA - timedelta(hours=2))]), {})
        self.assertEqual(self._regras(estados=est, contratos=con,
                                      tarefas=[_t("A", F.REPAIR, F.DONE, AGORA - timedelta(days=2))]),
                         {"A": "DEGRADADA"})

    def test_canal_youtube_caracterizado_sem_numero(self):
        cand = [{"CANDIDATA_ID": "CAND-1", "TIPO": "YOUTUBE", "ESTADO": "EM_ANALISE",
                 "SOURCE_ID": None},
                {"CANDIDATA_ID": "CAND-2", "TIPO": "YOUTUBE", "ESTADO": "EM_ANALISE",
                 "SOURCE_ID": None},
                {"CANDIDATA_ID": "CAND-3", "TIPO": "YOUTUBE", "ESTADO": "EM_ANALISE",
                 "SOURCE_ID": None}]
        car = [{"CANDIDATE_ID": c, "FINAL_STATE": "ONBOARDING_READY"}
               for c in ("CAND-1", "CAND-2", "CAND-3")]
        r = self._regras(candidatas=cand, caract=car,
                         ponte={"CAND-2": {"DESTINO": "QUALIFY"}},
                         tarefas=[_t("CAND-3", F.QUALIFY, F.BLOCKED)])
        # CAND-2 e da ponte; CAND-3 ja teve QUALIFY (a de texto antigo e da R1)
        self.assertEqual(r, {"CAND-1": "SOCIAL_QUALIFY"})

    def test_a_ordem_da_volta_e_reparo_antes_de_identidade(self):
        cs = self._cands(estados={"Z": LC.DEGRADED, "A": LC.CONTRACT_PENDING},
                         contratos={"Z": HTML})
        self.assertEqual([c["SOURCE_ID"] for c in cs], ["Z", "A"])


class AJanelaDeCultura(unittest.TestCase):
    """D29: a fonte de janela sobe na fila; a classificacao nao aceita palavra solta."""

    def test_o_que_e_e_o_que_nao_e_janela(self):
        import janela_de_cultura as JC
        ficha = lambda nome, url: {"NAME": nome, "ACQUISITION": {"INDEX_URL": url}}
        self.assertTrue(JC.e_janela("IT-T3-001"))
        self.assertTrue(JC.e_janela("IT-T1-006", ficha("ARSAC", "https://arsac.calabria.it/bollettino-agrometeorologico-e-fitosanitario/")))
        self.assertTrue(JC.e_janela("IT-T2-015", ficha("AIAM — Associazione Italiana di Agrometeorologia", "https://www.agrometeorologia.it/")))
        # os falsos positivos medidos na copia (24/09) com a regra de palavras soltas
        self.assertFalse(JC.e_janela("IT-T12-040", ficha("Bandi e avvisi pubblici", "https://www.regione.sicilia.it/x")))
        self.assertFalse(JC.e_janela("IT-T12-042", ficha("Bollettino ufficiale", "http://www.bollettino.regione.lombardia.it/")))
        self.assertFalse(JC.e_janela("IT-T5-113", ficha("Notizie", "https://www.crea.gov.it/web/difesa-e-certificazione/notizie")))
        self.assertFalse(JC.e_janela("IT-T5-093", ficha("Non solo meteo: Arpal alla notte europea della ricerca", "https://www.arpal.liguria.it/n")))

    def test_janela_passa_a_frente_e_sobe_a_prioridade(self):
        cs = AV.candidatas_a_avancar(
            AGORA, estados={"IT-T1-001": LC.DEGRADED, "IT-T3-009": LC.CONTRACT_PENDING},
            contratos={"IT-T1-001": HTML}, tarefas=[], reguas={}, tabela={},
            candidatas=[], caract=[], ponte={})
        self.assertEqual([c["SOURCE_ID"] for c in cs], ["IT-T3-009", "IT-T1-001"])
        self.assertTrue(cs[0]["JANELA"])
        self.assertEqual(cs[0]["PRIORITY"], 45 + AV.JANELA_BONUS)
        self.assertIn("D29", cs[0]["MOTIVO"])
        self.assertEqual(cs[1]["PRIORITY"], 80)


class NaFila(unittest.TestCase):

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.addCleanup(setattr, F, "FILA", F.FILA)
        F.FILA = Path(self._td.name) / "fila.json"

    def test_avancar_respeita_o_teto_e_e_idempotente(self):
        kw = dict(estados={"S%03d" % i: LC.CONTRACT_PENDING for i in range(30)},
                  tarefas=None, contratos={}, reguas={}, tabela={},
                  candidatas=[], caract=[], ponte={})
        kw["tarefas"] = []
        r = AV.avancar(AGORA, limite=20, **kw)
        self.assertEqual(r["CANDIDATAS"], 30)
        self.assertEqual(len(r["ENFILEIRADAS"]), 20)
        self.assertEqual(len(F._ler()["TAREFAS"]), 20)
        AV.avancar(AGORA, limite=20, **kw)      # mesma lista de novo: fila nao duplica
        self.assertEqual(len(F._ler()["TAREFAS"]), 20)


class OGatilhoAvancaAntesDeProcurar(unittest.TestCase):

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        d = Path(self._td.name)
        self.addCleanup(setattr, F, "FILA", F.FILA)
        self.addCleanup(setattr, GD, "CANDIDATAS", GD.CANDIDATAS)
        F.FILA = d / "fila.json"
        GD.CANDIDATAS = d / "cand.json"
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}), encoding="utf-8")
        GD.CANDIDATAS.write_text(json.dumps({"CANDIDATAS": []}), encoding="utf-8")
        self.addCleanup(setattr, GD, "revalidar_elegiveis", GD.revalidar_elegiveis)
        GD.revalidar_elegiveis = lambda agora, **k: {"CANDIDATAS": 0, "ENFILEIRADAS": []}
        self.descobertas = 0

    def _descobrir(self):
        self.descobertas += 1
        return {}

    def _correr(self, n):
        return GD.talvez_alimentar(
            {}, feeder_fn=lambda: {}, descobrir_fn=self._descobrir,
            avancar_fn=lambda agora: {"CANDIDATAS": n, "POR_REGRA": {}, "ENFILEIRADAS": []})

    def test_com_avanco_elegivel_nao_se_procura(self):
        m = self._correr(3)
        self.assertEqual(m["DECISAO"], "AVANCO_ANTES_DE_DISCOVERY")
        self.assertEqual(self.descobertas, 0)

    def test_so_o_avanco_a_zero_abre_a_procura(self):
        m = self._correr(0)
        self.assertEqual(m["DECISAO"], "DISCOVERY_ACCIONADA")
        self.assertEqual(self.descobertas, 1)


class OContratoImportadoDoColetor(unittest.TestCase):

    LINHA = {"SOURCE_ID": "IT-T9-950", "OWNER": "Ente X", "NAME": "Ente X — notizie",
             "TERRITORY": "T9", "BATCH_ID": "LOTE-HTML-ARTIGO", "OUTPUT_TYPE": "HTML",
             "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL",
                             "INDEX_URL": "https://ente-x.it/notizie/",
                             "LINK_PATTERN": "^https?://ente-x\\.it/notizie/[a-z0-9-]+/?$",
                             "MAX_TARGETS": 1}}

    def setUp(self):
        import worker as W
        self.W = W
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        d = Path(self._td.name)
        for nome, v in (("CONTRATOS", d / "contracts.json"),
                        ("TABELA_DO_COLETOR", d / "onboarded.json"),
                        ("ALLOCATION", d / "alloc.json")):
            self.addCleanup(setattr, W, nome, getattr(W, nome))
            setattr(W, nome, v)
        W.CONTRATOS.write_text(json.dumps({"FONTES": []}), encoding="utf-8")
        W.TABELA_DO_COLETOR.write_text(json.dumps({"FONTES": [self.LINHA]}), encoding="utf-8")
        self.d = d

    def test_importa_com_a_aquisicao_igual_a_da_coleta(self):
        r, det = self.W.etapa_build_contract("IT-T9-950", None)
        self.assertEqual(r, "OK", det)
        c = json.loads(self.W.CONTRATOS.read_text(encoding="utf-8"))["FONTES"][0]
        self.assertEqual(c["ACQUISITION"], self.LINHA["ACQUISITION"])
        self.assertEqual(c["ROUTE_PROVENANCE"]["ORIGEM"], "TABELA_DO_COLETOR")
        self.assertTrue(c["ROUTE_PROVENANCE"]["INTEGRADO_EM"])
        import validar_contratos as VC
        self.assertEqual(VC.validar([c])[1], [])
        # a tabela do coletor e LIDA, nunca escrita
        self.assertEqual(json.loads(self.W.TABELA_DO_COLETOR.read_text(encoding="utf-8")),
                         {"FONTES": [self.LINHA]})
        # escrita atomica: nenhum temporario fica para tras
        self.assertEqual(sorted(os.listdir(self.d)), ["contracts.json", "onboarded.json"])

    def test_sem_linha_nem_identidade_continua_a_falhar(self):
        r, det = self.W.etapa_build_contract("IT-T9-951", None)
        self.assertEqual(r, "FAIL")

    def test_a_promocao_antiga_continua_legacy(self):
        """INTEGRADO_EM = agora: uma promocao anterior a importacao nao passa a
        CURRENT so por o contrato ter chegado."""
        import ready_split as RS
        self.W.etapa_build_contract("IT-T9-950", None)
        c = json.loads(self.W.CONTRATOS.read_text(encoding="utf-8"))["FONTES"][0]
        antiga = {"OBSERVED_AT": "2026-09-20T00:00:00+00:00", "EVIDENCE_REF": "x"}
        ev = {"DADOS": {"DETAIL_ENUMERATED": 9, "DETAIL_GATE_PASSED": True,
                        "ITEM_ABERTO": {"URL": "https://ente-x.it/notizie/a-b-c/", "HTTP": 200,
                                        "HTML_KIND": "CONTENT", "CAPA_OU_MATERIA": RS.MATERIA,
                                        "PARAGRAPH_CHARACTERS": 1800}}}
        self.assertEqual(RS.passos_da_promocao(antiga, ev, c)["REGUA"], RS.REGUA_LEGACY)
        nova = {"OBSERVED_AT": (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat(),
                "EVIDENCE_REF": "y"}
        self.assertEqual(RS.passos_da_promocao(nova, ev, c)["REGUA"], RS.REGUA_CURRENT)


class AMaquinaDoFunil(unittest.TestCase):

    def test_todo_estado_tem_linha(self):
        self.assertEqual(sorted(LC.ESTADOS - set(FU.MAQUINA)), [])

    def test_quem_enfileira_existe(self):
        import importlib
        for estado, (_t_, quem, _a, _n) in FU.MAQUINA.items():
            if ":" not in quem:
                continue
            mod, fn = quem.split(":")
            if mod == "gatilho_discovery" and fn == "candidatas_a_reparar":
                continue          # R1: existe no ramo dela; nesta arvore e buraco declarado
            with self.subTest(estado=estado):
                self.assertTrue(hasattr(importlib.import_module(mod), fn), quem)

    def test_automatico_e_mesmo_chamado_pelo_ciclo(self):
        ciclo = inspect.getsource(GD.talvez_alimentar)
        for estado, (_t_, quem, auto, _n) in FU.MAQUINA.items():
            if not auto:
                continue
            mod, fn = quem.split(":")
            with self.subTest(estado=estado):
                self.assertTrue(fn in ciclo or (mod == "ponte_candidatas" and "feeder" in ciclo),
                                "%s diz-se AUTOMATICO mas o ciclo nao o chama" % quem)


if __name__ == "__main__":
    unittest.main()
