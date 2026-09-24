#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes de regressao para o impasse B4 (bot parado com trabalho por fazer).

Tres defeitos provados e corrigidos:

    D1  ponte_candidatas: NEEDS_MORE_SAMPLING era ignorada como «ja no curator»
        -> ponte nunca criava tarefas para elas -> 11 fontes presas para sempre.

    D2  nivel_da_fila: HTML com QUALIFY ja tentado (e bloqueado) contava como
        backlog accionavel -> sinal dizia DISCOVERY_NOT_NEEDED com 175 fontes
        que nao podiam avancar -> discovery nao disparava.

    D3  gatilho_discovery: com fila=0 e acervo=0, esperava o intervalo de 3600 s
        em vez de disparar imediatamente -> bot ocioso durante quase uma hora.

Cada classe tem um teste RED TEAM (mutacao Mx) que prova que a guarda e real:
mutar a linha-chave faz o teste reprovar.
"""
from __future__ import annotations

import importlib
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))

import fila as F              # noqa: E402
import fonte_nova as FN       # noqa: E402
import lifecycle as LC        # noqa: E402
import ponte_candidatas as P  # noqa: E402
import nivel_da_fila as N     # noqa: E402
import gatilho_discovery as GD  # noqa: E402


# ---------------------------------------------------------------------------
# Auxiliares
# ---------------------------------------------------------------------------

def _porta(cands: list) -> dict:
    return {"CANDIDATAS": cands, "TOTAL": len(cands)}


def _make_cand(cid: str, tipo: str = "ORGANIZACAO") -> dict:
    return {"CANDIDATA_ID": cid, "TIPO": tipo, "NOME": cid,
            "URL": "https://exemplo.it/", "PAIS": "IT", "ESTADO": "CANDIDATA"}


def _baldes_html(html_ids: list, mais_amostra: int = 0) -> dict:
    """Baldes minimos para testar nivel_da_fila sem tocar em disco real."""
    return {
        "UNIVERSO_DESTA_ARVORE": 100,
        "TOTAIS": {"JA_COM_CONTRATO": 0, "COM_SOURCE_ID_SEM_CONTRATO": 0,
                   "SEM_TERRITORIO": 0, "CARACTERIZADAS_NAO_READY": mais_amostra,
                   "NUNCA_CARACTERIZADAS": len(html_ids)},
        "CARACTERIZADAS_NAO_READY_PORQUE": {"NEEDS_MORE_SAMPLING": mais_amostra},
        "NUNCA_CARACTERIZADAS": {
            "HTML_NOVAS": len(html_ids),
            "HTML_NOVAS_IDS": html_ids,
            "SOCIAL": 0,
            "HTML": len(html_ids),
        },
    }


def _fila_com_qualify(tmp: Path, tarefas_spec: list[tuple[str, str]]) -> None:
    """Cria ficheiro de fila com QUALIFY tasks. tarefas_spec = [(cid, status), ...]."""
    tarefas = [
        {"TASK_ID": "T%05d" % i, "SOURCE_ID": cid,
         "TASK_TYPE": F.QUALIFY, "PRIORITY": 30, "STATUS": status,
         "ATTEMPTS": 0, "NEXT_ATTEMPT_AT": None, "LAST_ERROR": "NAO SEI",
         "MOTIVO": "", "CREATED_AT": "2026-09-21T00:00:00+00:00",
         "UPDATED_AT": "2026-09-23T00:00:00+00:00"}
        for i, (cid, status) in enumerate(tarefas_spec)
    ]
    (tmp / "fila.json").write_text(
        json.dumps({"PROXIMO_ID": len(tarefas) + 1, "TAREFAS": tarefas}),
        encoding="utf-8")


# ===========================================================================
# D1 — ponte_candidatas: NEEDS_MORE_SAMPLING nao e «ja no curator»
# ===========================================================================

class TestD1NeedsMoreSampling(unittest.TestCase):
    """NEEDS_MORE_SAMPLING deve ser processada pela ponte, nao ignorada."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="b4-d1-")
        self.addCleanup(self._td.cleanup)
        self.tmp = Path(self._td.name)
        importlib.reload(LC)
        importlib.reload(F)
        importlib.reload(FN)
        importlib.reload(P)
        LC.LIVRO = self.tmp / "livro.json"
        F.FILA = self.tmp / "fila.json"
        FN.FILA = self.tmp / "candidatas.json"
        P.CARACT = self.tmp / "caract.json"
        P.LEDGER = self.tmp / "ledger.json"
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}),
                          encoding="utf-8")

    def tearDown(self):
        importlib.reload(LC)
        importlib.reload(F)
        importlib.reload(FN)
        importlib.reload(P)

    def _porta(self, cands):
        FN.FILA.write_text(json.dumps(_porta(cands)), encoding="utf-8")

    def _caract(self, fontes):
        P.CARACT.write_text(json.dumps({"FONTES": fontes}), encoding="utf-8")

    def test_needs_more_sampling_e_enfileirada(self):
        """Fonte com FINAL_STATE=NEEDS_MORE_SAMPLING vai para QUALIFY — nao ignorada."""
        self._porta([_make_cand("CAND-0001")])
        self._caract([{"CANDIDATE_ID": "CAND-0001", "FINAL_STATE": "NEEDS_MORE_SAMPLING"}])

        m = P.processar()

        self.assertEqual(0, m["JA_PROCESSADAS_IGNORADAS"])
        self.assertEqual(1, m["ENFILEIRADAS"])

    def test_outro_final_state_continua_ignorado(self):
        """Fonte com FINAL_STATE=PROMOTE (decisao final tomada) e ignorada pela ponte."""
        self._porta([_make_cand("CAND-0002")])
        self._caract([{"CANDIDATE_ID": "CAND-0002", "FINAL_STATE": "PROMOTE"}])

        m = P.processar()

        self.assertEqual(1, m["JA_PROCESSADAS_IGNORADAS"])
        self.assertEqual(0, m["ENFILEIRADAS"])

    def test_mistura_um_ignorado_um_processado(self):
        """NEEDS_MORE_SAMPLING e PROMOTE na mesma corrida: so NEEDS enfileirado."""
        self._porta([_make_cand("CAND-0010"), _make_cand("CAND-0011")])
        self._caract([
            {"CANDIDATE_ID": "CAND-0010", "FINAL_STATE": "NEEDS_MORE_SAMPLING"},
            {"CANDIDATE_ID": "CAND-0011", "FINAL_STATE": "PROMOTE"},
        ])

        m = P.processar()

        self.assertEqual(1, m["JA_PROCESSADAS_IGNORADAS"])
        self.assertEqual(1, m["ENFILEIRADAS"])

    def test_segunda_corrida_idempotente(self):
        """Depois da 1.a corrida, a 2.a nao cria duplicados (ledger guarda)."""
        self._porta([_make_cand("CAND-0001")])
        self._caract([{"CANDIDATE_ID": "CAND-0001", "FINAL_STATE": "NEEDS_MORE_SAMPLING"}])

        m1 = P.processar()
        m2 = P.processar()

        self.assertEqual(1, m1["ENFILEIRADAS"])
        self.assertEqual(0, m2["ENFILEIRADAS"])
        self.assertEqual(1, m2["JA_PROCESSADAS_IGNORADAS"])

    def test_mutacao_m1_sem_exclusao_nao_enfileira(self):
        """RED TEAM D1: incluir NEEDS_MORE_SAMPLING em ja_curator bloqueia a corrida."""
        self._porta([_make_cand("CAND-0001")])
        self._caract([{"CANDIDATE_ID": "CAND-0001", "FINAL_STATE": "NEEDS_MORE_SAMPLING"}])

        orig = P._ja_no_curator
        P._ja_no_curator = lambda: {"CAND-0001"}  # mutacao: inclui NEEDS_MORE_SAMPLING
        try:
            m = P.processar()
            self.assertEqual(0, m["ENFILEIRADAS"],
                             "M1: com NEEDS_MORE_SAMPLING em ja_curator -> nao enfileira (defeito)")
        finally:
            P._ja_no_curator = orig


# ===========================================================================
# D2 — nivel_da_fila: HTML com QUALIFY ja tentado nao conta como backlog
# ===========================================================================

class TestD2QualifyTentadas(unittest.TestCase):
    """HTML com QUALIFY BLOCKED nao deve aparecer no CANDIDATE_BACKLOG."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="b4-d2-")
        self.addCleanup(self._td.cleanup)
        self.tmp = Path(self._td.name)
        self._orig_fila = F.FILA
        F.FILA = self.tmp / "fila.json"

    def tearDown(self):
        F.FILA = self._orig_fila

    def test_175_blocked_dao_backlog_zero(self):
        """Caso do impasse real: 175 QUALIFY BLOCKED -> backlog HTML = 0."""
        ids = ["CAND-%04d" % i for i in range(175)]
        _fila_com_qualify(self.tmp, [(cid, F.BLOCKED) for cid in ids])

        r = N.medir(_baldes_html(ids), watermark=20)

        self.assertEqual(0, r["CANDIDATE_BACKLOG_COMPOSICAO"]["HTML_NUNCA_CARACTERIZADAS_NOVAS"])
        self.assertEqual(175, r["FORA_DO_BACKLOG"]["HTML_QUALIFY_BLOQUEADO"])

    def test_sem_qualify_conta_tudo(self):
        """HTML sem QUALIFY algum -> conta como backlog accionavel."""
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}),
                          encoding="utf-8")
        ids = ["CAND-%04d" % i for i in range(10)]

        r = N.medir(_baldes_html(ids), watermark=20)

        self.assertEqual(10, r["CANDIDATE_BACKLOG_COMPOSICAO"]["HTML_NUNCA_CARACTERIZADAS_NOVAS"])
        self.assertEqual(0, r["FORA_DO_BACKLOG"]["HTML_QUALIFY_BLOQUEADO"])

    def test_needs_more_sampling_conta_sempre(self):
        """NEEDS_MORE_SAMPLING e backlog independente do estado dos QUALIFY."""
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}),
                          encoding="utf-8")

        r = N.medir(_baldes_html([], mais_amostra=11), watermark=20)

        self.assertEqual(11, r["CANDIDATE_BACKLOG"])
        self.assertEqual(11, r["CANDIDATE_BACKLOG_COMPOSICAO"]["NEEDS_MORE_SAMPLING"])

    def test_needs_more_sampling_ja_tentada_sai_do_backlog(self):
        """Vivo 23/09 17:44: 11 enfileiradas, 7 ganharam SOURCE_ID, 4 bloquearam -> 0, nao 4."""
        bloq = ["CAND-0003", "CAND-0058", "CAND-0151", "CAND-0156"]
        _fila_com_qualify(self.tmp, [(c, F.BLOCKED) for c in bloq])
        b = _baldes_html([], mais_amostra=5)
        b["NEEDS_MORE_SAMPLING_IDS"] = bloq + ["CAND-0999"]

        r = N.medir(b, watermark=20)

        self.assertEqual(1, r["CANDIDATE_BACKLOG_COMPOSICAO"]["NEEDS_MORE_SAMPLING"])
        self.assertEqual(4, r["FORA_DO_BACKLOG"]["NEEDS_MORE_SAMPLING_JA_TENTADAS"])

    def test_impasse_real_11_needs_175_blocked_discovery_needed(self):
        """175 BLOCKED + 11 NEEDS_MORE_SAMPLING -> backlog=11 -> DISCOVERY_NEEDED."""
        ids = ["CAND-%04d" % i for i in range(175)]
        _fila_com_qualify(self.tmp, [(cid, F.BLOCKED) for cid in ids])

        r = N.medir(_baldes_html(ids, mais_amostra=11), watermark=20)

        self.assertEqual(11, r["CANDIDATE_BACKLOG"])
        self.assertTrue(r["DISCOVERY_NEEDED"])
        self.assertEqual("DISCOVERY_NEEDED", r["DISCOVERY_SIGNAL"])

    def test_qualify_done_tambem_exclui_do_backlog(self):
        """QUALIFY DONE: a fonte ja foi processada (SOURCE_ID alocado) — nao e backlog."""
        ids = ["CAND-%04d" % i for i in range(5)]
        _fila_com_qualify(self.tmp, [(cid, F.DONE) for cid in ids])

        r = N.medir(_baldes_html(ids), watermark=20)

        self.assertEqual(0, r["CANDIDATE_BACKLOG_COMPOSICAO"]["HTML_NUNCA_CARACTERIZADAS_NOVAS"])

    def test_mutacao_m2_sem_subtraccao_camufla_discovery(self):
        """RED TEAM D2: sem subtrair tentadas, 175 BLOCKED parecem backlog real."""
        ids = ["CAND-%04d" % i for i in range(175)]
        _fila_com_qualify(self.tmp, [(cid, F.BLOCKED) for cid in ids])

        orig = N._qualify_ja_tentadas
        N._qualify_ja_tentadas = lambda: set()  # mutacao: ignora tasks existentes
        try:
            r = N.medir(_baldes_html(ids), watermark=20)
            self.assertFalse(r["DISCOVERY_NEEDED"],
                             "M2: sem subtraccao -> 175 parecem backlog -> NOT_NEEDED (defeito)")
        finally:
            N._qualify_ja_tentadas = orig


# ===========================================================================
# D3 — gatilho_discovery: fila+acervo zero dispara sem esperar intervalo
# ===========================================================================

class TestD3DispararImediato(unittest.TestCase):
    """Com fila=0 e acervo=0, discovery dispara imediatamente."""

    def setUp(self):
        # CUR-PRONTA: o gatilho passou a chamar o AVANCAR antes do discovery, e
        # o AVANCAR le o livro VERDADEIRO do repositorio. Esta classe mede a
        # procura de fontes novas: o avanco fica a zero aqui (tem testes
        # proprios em test_avancar_fontes.py).
        import avancar_fontes as _AV
        self.addCleanup(setattr, _AV, "avancar", _AV.avancar)
        _AV.avancar = lambda agora=None, **_k: {"CANDIDATAS": 0, "POR_REGRA": {},
                                                "ENFILEIRADAS": []}
        self._td = tempfile.TemporaryDirectory(prefix="b4-d3-")
        self.addCleanup(self._td.cleanup)
        self.tmp = Path(self._td.name)
        self._orig = {"F.FILA": F.FILA, "GD.CANDIDATAS": GD.CANDIDATAS,
                      "LC.LIVRO": LC.LIVRO, "GD.CONTRATOS": GD.CONTRATOS}
        F.FILA = self.tmp / "fila.json"
        GD.CANDIDATAS = self.tmp / "cand.json"
        # R1: livro e contratos vazios — o gatilho agora os le (reparo antes de discovery)
        LC.LIVRO = self.tmp / "livro.json"
        GD.CONTRATOS = self.tmp / "contratos.json"
        GD.CONTRATOS.write_text('{"FONTES": []}', encoding="utf-8")
        self.disc_calls = 0
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}),
                          encoding="utf-8")

    def tearDown(self):
        F.FILA = self._orig["F.FILA"]
        GD.CANDIDATAS = self._orig["GD.CANDIDATAS"]
        LC.LIVRO = self._orig["LC.LIVRO"]
        GD.CONTRATOS = self._orig["GD.CONTRATOS"]

    def _acervo(self, n_candidata: int) -> None:
        cs = [{"CANDIDATA_ID": "CAND-%04d" % i, "ESTADO": "CANDIDATA"}
              for i in range(n_candidata)]
        GD.CANDIDATAS.write_text(json.dumps({"CANDIDATAS": cs}), encoding="utf-8")

    def _descobrir(self):
        self.disc_calls += 1
        return {"CANDIDATAS_NOVAS": 0}

    def test_fila_zero_acervo_zero_dispara_mesmo_no_intervalo(self):
        """IMPASSE B4: a fila mudou desde o ultimo discovery e chegou a zero -> dispara ja."""
        self._acervo(0)
        agora = datetime.now(timezone.utc)
        estado = {"LAST_DISCOVERY_AT": (agora - timedelta(seconds=60)).isoformat(),
                  "DISCOVERY_ASSINATURA_FILA": "fila-de-antes-do-trabalho"}

        m = GD.talvez_alimentar(estado, feeder_fn=lambda: {"TAREFAS_CRIADAS": 0},
                                descobrir_fn=self._descobrir, agora=agora)

        self.assertEqual(1, self.disc_calls,
                         "discovery tem de disparar mesmo dentro do intervalo")
        self.assertEqual("DISCOVERY_ACCIONADA", m["DECISAO"])
        self.assertIn("DISCOVERY_ANTECIPADO", m)
        self.assertEqual(GD.assinatura_da_fila(), estado["DISCOVERY_ASSINATURA_FILA"])

    def test_fila_igual_ao_ultimo_discovery_respeita_intervalo(self):
        """Anti-rajada: nada mudou desde o ultimo crawl -> 240 voltas dao 0 crawls."""
        self._acervo(0)
        agora = datetime.now(timezone.utc)
        estado = {"LAST_DISCOVERY_AT": (agora - timedelta(seconds=60)).isoformat(),
                  "DISCOVERY_ASSINATURA_FILA": GD.assinatura_da_fila()}
        for k in range(240):
            GD.talvez_alimentar(estado, feeder_fn=lambda: {"TAREFAS_CRIADAS": 0},
                                descobrir_fn=self._descobrir,
                                agora=agora + timedelta(seconds=15 * k) / 100)
        self.assertEqual(0, self.disc_calls)

    def test_um_disparo_antecipado_nao_vira_rajada(self):
        """Dispara uma vez ao chegar a zero; nas voltas seguintes, sem mudanca, espera."""
        self._acervo(0)
        agora = datetime.now(timezone.utc)
        estado = {"LAST_DISCOVERY_AT": (agora - timedelta(seconds=60)).isoformat(),
                  "DISCOVERY_ASSINATURA_FILA": "fila-de-antes-do-trabalho"}
        for k in range(20):
            GD.talvez_alimentar(estado, feeder_fn=lambda: {"TAREFAS_CRIADAS": 0},
                                descobrir_fn=self._descobrir,
                                agora=agora + timedelta(seconds=15 * k))
        self.assertEqual(1, self.disc_calls)

    def test_estado_antigo_sem_assinatura_respeita_intervalo(self):
        """Estado gravado antes desta regra: nao se adivinha — o intervalo manda."""
        self._acervo(0)
        agora = datetime.now(timezone.utc)
        estado = {"LAST_DISCOVERY_AT": (agora - timedelta(seconds=60)).isoformat()}
        m = GD.talvez_alimentar(estado, feeder_fn=lambda: {"TAREFAS_CRIADAS": 0},
                                descobrir_fn=self._descobrir, agora=agora)
        self.assertEqual(0, self.disc_calls)
        self.assertEqual("DISCOVERY_EM_INTERVALO", m["DECISAO"])

    def test_regra_nova_da_ponte_acorda_o_feeder(self):
        """Instalar regra nova muda a assinatura: o FEEDER sai do NO-OP."""
        self._acervo(0)
        antes = GD.assinatura_da_condicao()
        orig = GD.PONTE.REGRA_VERSAO
        GD.PONTE.REGRA_VERSAO = "outra-regra"
        try:
            self.assertNotEqual(antes, GD.assinatura_da_condicao())
        finally:
            GD.PONTE.REGRA_VERSAO = orig

    def test_fila_com_trabalho_respeita_intervalo(self):
        """Com QUALIFY PENDING na fila, o intervalo de discovery e respeitado."""
        tarefas = [{"TASK_ID": "T00001", "SOURCE_ID": "CAND-0001",
                    "TASK_TYPE": F.QUALIFY, "PRIORITY": 30, "STATUS": F.PENDING,
                    "ATTEMPTS": 0, "NEXT_ATTEMPT_AT": None, "LAST_ERROR": None,
                    "MOTIVO": "", "CREATED_AT": "2026-09-21T00:00:00+00:00",
                    "UPDATED_AT": "2026-09-21T00:00:00+00:00"}]
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 2, "TAREFAS": tarefas}),
                          encoding="utf-8")
        self._acervo(0)
        agora = datetime.now(timezone.utc)
        estado = {"LAST_DISCOVERY_AT": (agora - timedelta(seconds=60)).isoformat()}

        m = GD.talvez_alimentar(estado, feeder_fn=lambda: {"TAREFAS_CRIADAS": 0},
                                descobrir_fn=self._descobrir, agora=agora)

        self.assertEqual(0, self.disc_calls,
                         "com trabalho na fila, intervalo deve ser respeitado")

    def test_acervo_com_candidatas_respeita_intervalo(self):
        """Com candidatas por qualificar (ESTADO=CANDIDATA), o intervalo e respeitado."""
        self._acervo(5)
        agora = datetime.now(timezone.utc)
        estado = {"LAST_DISCOVERY_AT": (agora - timedelta(seconds=60)).isoformat()}

        m = GD.talvez_alimentar(estado, feeder_fn=lambda: {"TAREFAS_CRIADAS": 0},
                                descobrir_fn=self._descobrir, agora=agora)

        self.assertEqual(0, self.disc_calls,
                         "com acervo cheio, intervalo deve ser respeitado")

    def test_feeder_cria_tarefas_e_discovery_nao_dispara(self):
        """Se o feeder criou 11 tarefas, eligible_apos_feeder>0 -> sem discovery."""
        self._acervo(0)
        agora = datetime.now(timezone.utc)
        estado = {}

        feeder_calls = []

        def _feeder_que_cria():
            # Simular feeder que cria 11 QUALIFY PENDING
            tarefas = [{"TASK_ID": "T%05d" % i, "SOURCE_ID": "CAND-%04d" % i,
                        "TASK_TYPE": F.QUALIFY, "PRIORITY": 30, "STATUS": F.PENDING,
                        "ATTEMPTS": 0, "NEXT_ATTEMPT_AT": None, "LAST_ERROR": None,
                        "MOTIVO": "", "CREATED_AT": "2026-09-21T00:00:00+00:00",
                        "UPDATED_AT": "2026-09-21T00:00:00+00:00"}
                       for i in range(11)]
            F.FILA.write_text(
                json.dumps({"PROXIMO_ID": 12, "TAREFAS": tarefas}), encoding="utf-8")
            feeder_calls.append(1)
            return {"TAREFAS_CRIADAS": 11}

        m = GD.talvez_alimentar(estado, feeder_fn=_feeder_que_cria,
                                descobrir_fn=self._descobrir, agora=agora)

        self.assertEqual(0, self.disc_calls,
                         "feeder criou 11 tasks -> eligible>10 -> discovery nao dispara")
        self.assertEqual(1, len(feeder_calls))


if __name__ == "__main__":
    unittest.main()
