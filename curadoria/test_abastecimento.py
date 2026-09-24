#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ABASTECIMENTO DO BOT — tres defeitos medidos em 22/09, tres provas.

    A. FEEDER sem condicao nova = NO-OP silencioso, contado.
    B. FAILED por transporte revive devagar, com teto; policy nunca.
    C. Sementes de 2.a geracao: so o que a regra ATUAL chama TEMATICA.

Tudo em TemporaryDirectory: nenhum teste toca a fila, o livro ou as
candidatas reais.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import descobrir as D            # noqa: E402
import fila as F                 # noqa: E402
import gatilho_discovery as GD   # noqa: E402
import lifecycle as LC            # noqa: E402

T0 = datetime(2026, 9, 22, 12, 0, tzinfo=timezone.utc)


def _tarefa(i, status, erro=None, updated=T0, attempts=0):
    return {"TASK_ID": "T%05d" % i, "SOURCE_ID": "IT-X-%03d" % i,
            "TASK_TYPE": F.VALIDATE_ROUTE, "PRIORITY": 50, "STATUS": status,
            "ATTEMPTS": attempts, "NEXT_ATTEMPT_AT": None, "LAST_ERROR": erro,
            "MOTIVO": "", "CREATED_AT": "2026-09-21T00:00:00+00:00",
            "UPDATED_AT": updated.isoformat()}


class _Isolado(unittest.TestCase):
    def setUp(self):
        # CUR-PRONTA: o gatilho passou a chamar o AVANCAR antes do discovery, e
        # o AVANCAR le o livro VERDADEIRO do repositorio. Esta classe mede a
        # procura de fontes novas: o avanco fica a zero aqui (tem testes
        # proprios em test_avancar_fontes.py).
        import avancar_fontes as _AV
        self.addCleanup(setattr, _AV, "avancar", _AV.avancar)
        _AV.avancar = lambda agora=None, **_k: {"CANDIDATAS": 0, "POR_REGRA": {},
                                                "ENFILEIRADAS": []}
        self._td = tempfile.TemporaryDirectory(prefix="abastecimento-")
        self.tmp = Path(self._td.name)
        self._orig = (F.FILA, GD.CANDIDATAS, LC.LIVRO, GD.CONTRATOS)
        F.FILA = self.tmp / "fila.json"
        GD.CANDIDATAS = self.tmp / "cand.json"
        # R1: o gatilho le o livro e os contratos (reparo antes de discovery);
        # vazios aqui, senao o livro REAL da arvore decidia por estes testes.
        LC.LIVRO = self.tmp / "livro.json"
        GD.CONTRATOS = self.tmp / "contratos.json"
        GD.CONTRATOS.write_text('{"FONTES": []}', encoding="utf-8")

    def tearDown(self):
        F.FILA, GD.CANDIDATAS, LC.LIVRO, GD.CONTRATOS = self._orig
        self._td.cleanup()

    def _gravar_fila(self, tarefas):
        F.FILA.write_text(json.dumps({"PROXIMO_ID": len(tarefas) + 1,
                                      "TAREFAS": tarefas}), encoding="utf-8")

    def _gravar_cand(self, cands):
        GD.CANDIDATAS.write_text(json.dumps({"CANDIDATAS": cands}),
                                 encoding="utf-8")


class TestFeederNoop(_Isolado):
    def setUp(self):
        super().setUp()
        self.chamadas = 0
        self._gravar_fila([_tarefa(1, F.DONE)])
        self._gravar_cand([{"CANDIDATA_ID": "CAND-0001", "ESTADO": "EM_ANALISE"}])

    def _feeder(self):
        self.chamadas += 1
        return {"TAREFAS_CRIADAS": 0}

    def _volta(self, estado, agora):
        return GD.talvez_alimentar(estado, feeder_fn=self._feeder,
                                   descobrir_fn=lambda: {"CANDIDATAS_NOVAS": 0},
                                   agora=agora)

    def test_uma_hora_parada_da_um_feeder_e_nao_240(self):
        estado = {"LAST_DISCOVERY_AT": T0.isoformat()}   # discovery em intervalo
        anotados = 0
        for k in range(240):                              # 1 h de voltas de 15 s
            m = self._volta(estado, T0 + timedelta(seconds=15 * k))
            if m.get("ACCOES"):                           # o supervisor so anota assim
                anotados += 1
        self.assertEqual(self.chamadas, 1)
        self.assertEqual(anotados, 1)
        self.assertEqual(estado["FEEDER_NOOP_TOTAL"], 239)   # nada engolido

    def test_candidata_nova_reacorda_o_feeder(self):
        estado = {"LAST_DISCOVERY_AT": T0.isoformat()}
        self._volta(estado, T0)
        self._volta(estado, T0 + timedelta(seconds=15))
        self.assertEqual(self.chamadas, 1)
        self._gravar_cand([{"CANDIDATA_ID": "CAND-0001", "ESTADO": "EM_ANALISE"},
                           {"CANDIDATA_ID": "CAND-0002", "ESTADO": "CANDIDATA"}])
        m = self._volta(estado, T0 + timedelta(seconds=30))
        self.assertEqual(self.chamadas, 2)
        self.assertIn("FEEDER", m["ACCOES"])

    def test_fila_que_muda_reacorda_o_feeder(self):
        estado = {"LAST_DISCOVERY_AT": T0.isoformat()}
        self._volta(estado, T0)
        self._gravar_fila([_tarefa(1, F.DONE), _tarefa(2, F.DONE)])
        self._volta(estado, T0 + timedelta(seconds=15))
        self.assertEqual(self.chamadas, 2)

    def test_discovery_continua_no_intervalo_mesmo_em_noop(self):
        estado = {"LAST_DISCOVERY_AT": (T0 - timedelta(hours=2)).isoformat()}
        self._volta(estado, T0)                       # feeder + discovery
        m = self._volta(estado, T0 + timedelta(hours=1, seconds=1))
        self.assertIn("DISCOVERY", m["ACCOES"])
        self.assertNotIn("FEEDER", m["ACCOES"])       # a condicao nao mudou


class TestReviverIntermitentes(_Isolado):
    ROBOTS = "teto de 5 tentativas: robots nao pode ser lido — UNKNOWN, nao proibicao"

    def test_robots_ilegivel_revive_so_depois_do_backoff(self):
        self._gravar_fila([_tarefa(1, F.FAILED, self.ROBOTS, attempts=5)])
        self.assertEqual(F.reviver_intermitentes(T0 + timedelta(hours=5)), [])
        r = F.reviver_intermitentes(T0 + timedelta(hours=6))
        self.assertEqual(len(r), 1)
        t = F._ler()["TAREFAS"][0]
        self.assertEqual(t["STATUS"], F.WAITING_RETRY)
        self.assertEqual(t["ATTEMPTS"], F.MAX_ATTEMPTS - 1)   # UMA tentativa
        self.assertEqual(t["REVIVALS"], 1)
        self.assertEqual(len(F.elegiveis(T0 + timedelta(hours=6))), 1)

    def test_falha_de_novo_volta_a_failed_e_o_degrau_cresce(self):
        self._gravar_fila([_tarefa(1, F.FAILED, self.ROBOTS, attempts=5)])
        t6 = T0 + timedelta(hours=6)
        F.reviver_intermitentes(t6)
        F.adiar("T00001", erro="robots nao pode ser lido — UNKNOWN", agora=t6)
        t = F._ler()["TAREFAS"][0]
        self.assertEqual(t["STATUS"], F.FAILED)
        # 23 h depois ainda nao: o degrau 2 e 24 h
        self.assertEqual(F.reviver_intermitentes(t6 + timedelta(hours=23)), [])
        self.assertEqual(len(F.reviver_intermitentes(t6 + timedelta(hours=24))), 1)

    def test_teto_de_revivencias_declara_morta_e_para(self):
        self._gravar_fila([_tarefa(1, F.FAILED, self.ROBOTS, attempts=5)])
        agora = T0
        for degrau in F.REVIVE_BACKOFF_S:
            agora = agora + timedelta(seconds=degrau)
            self.assertEqual(len(F.reviver_intermitentes(agora)), 1)
            F.adiar("T00001", erro="robots nao pode ser lido", agora=agora)
        agora += timedelta(days=30)
        r = F.reviver_intermitentes(agora)
        self.assertEqual(r[0]["INTERMITENCIA_VEREDICTO"], F.MORTA)
        t = F._ler()["TAREFAS"][0]
        self.assertEqual(t["STATUS"], F.FAILED)
        self.assertIn("morta: 3 revivencias", t["MOTIVO"])
        self.assertEqual(F.reviver_intermitentes(agora + timedelta(days=99)), [])

    def test_policy_e_erro_da_fonte_nunca_revivem(self):
        self._gravar_fila([
            _tarefa(1, F.BLOCKED, "o endereco do contrato casa com Disallow no robots vivo"),
            _tarefa(2, F.FAILED, "teto de 5 tentativas: HTTP 422", attempts=5),
            _tarefa(3, F.BLOCKED, "HTTP 403 no robots.txt — tratado como Disallow total"),
            _tarefa(4, F.DONE),
        ])
        self.assertEqual(F.reviver_intermitentes(T0 + timedelta(days=30)), [])

    def test_timeout_e_reset_contam_como_transporte(self):
        self._gravar_fila([
            _tarefa(1, F.FAILED, "teto de 5 tentativas: TimeoutError: The read "
                    "operation timed out", attempts=5),
            _tarefa(2, F.FAILED, "teto de 5 tentativas: URLError: <urlopen error "
                    "[WinError 10054] Foi forcado o cancelamento", attempts=5),
        ])
        self.assertEqual(len(F.reviver_intermitentes(T0 + timedelta(hours=6))), 2)

    def test_gatilho_anota_a_revivencia(self):
        self._gravar_fila([_tarefa(1, F.FAILED, self.ROBOTS, attempts=5)])
        self._gravar_cand([])
        estado = {"LAST_DISCOVERY_AT": (T0 + timedelta(hours=6)).isoformat()}
        m = GD.talvez_alimentar(estado, feeder_fn=lambda: {},
                                descobrir_fn=lambda: {},
                                agora=T0 + timedelta(hours=6))
        self.assertIn("REVIVER", m["ACCOES"])
        self.assertEqual(m["REVIVER"]["REVIVIDAS"], 1)


class TestSementesSegundaGeracao(unittest.TestCase):
    def _cands(self, lista):
        td = tempfile.TemporaryDirectory(prefix="sementes-")
        self.addCleanup(td.cleanup)
        p = Path(td.name) / "c.json"
        p.write_text(json.dumps({"CANDIDATAS": lista}), encoding="utf-8")
        return p

    def test_so_tematica_pela_regra_atual(self):
        p = self._cands([
            {"CANDIDATA_ID": "CAND-1", "URL": "https://www.nomisma.it/", "ESTADO": "EM_ANALISE"},
            {"CANDIDATA_ID": "CAND-2", "URL": "https://www.unipd.it/", "ESTADO": "EM_ANALISE"},
            {"CANDIDATA_ID": "CAND-3", "URL": "https://www.regione.veneto.it/", "ESTADO": "EM_ANALISE"},
            {"CANDIDATA_ID": "CAND-4", "URL": "https://puglia.coldiretti.it/", "ESTADO": "RECUSADA"},
            {"CANDIDATA_ID": "CAND-5", "URL": "https://veneto.coldiretti.it/", "ESTADO": "EM_ANALISE"},
        ])
        urls = [s["URL"] for s in D._sementes_de_segunda_geracao(p)]
        self.assertEqual(urls, ["https://www.nomisma.it/", "https://veneto.coldiretti.it/"])

    def test_a_regra_de_semente_nao_afrouxou(self):
        for u in ("https://www.unipd.it/", "https://www.istat.it/",
                  "https://www.cnr.it/it/istituto?cds=0", "https://www.unito.it/"):
            self.assertEqual(D._classificar_semente(u)[0], "UNKNOWN", u)
        self.assertEqual(D._classificar_semente("https://www.regione.veneto.it/")[0],
                         "GENERICA")

    def test_orcamento_zero_nao_le_robots(self):
        chamadas = []
        orig = D._permitido
        D._permitido = lambda u: chamadas.append(u) or True
        try:
            _, stats = D.crawl_sementes(D.Orcamento(total=0), set(),
                                        {"VISITADOS": {}, "REJEITADOS": {}},
                                        [], max_sementes=50)
        finally:
            D._permitido = orig
        self.assertEqual(chamadas, [])
        self.assertGreater(stats["ORCAMENTO_BLOQUEADAS"], 0)

    def test_proveniencia_viaja_com_a_semente(self):
        p = self._cands([{"CANDIDATA_ID": "CAND-9", "URL": "https://www.uiv.it/",
                          "ESTADO": "EM_ANALISE", "ONDE_VIU": "sonda HTTP"}])
        s = D._sementes_de_segunda_geracao(p)[0]
        self.assertEqual((s["CANDIDATA_ID"], s["ONDE_VIU"]), ("CAND-9", "sonda HTTP"))


if __name__ == "__main__":
    unittest.main()
