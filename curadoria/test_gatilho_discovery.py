#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes do gatilho do modo continuo (low watermark -> feeder/discovery).

Prova as quatro decisoes, com feeder e discovery INJECTADOS (nunca toca a rede)
e fila/candidatas em ficheiros temporarios (nunca toca a lane).
"""
import inspect
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F
import gatilho_discovery as GD


class TestGatilho(unittest.TestCase):
    def setUp(self):
        # CUR-PRONTA: o gatilho passou a chamar o AVANCAR antes do discovery, e
        # o AVANCAR le o livro VERDADEIRO do repositorio. Esta classe mede a
        # procura de fontes novas: o avanco fica a zero aqui (tem testes
        # proprios em test_avancar_fontes.py).
        import avancar_fontes as _AV
        self.addCleanup(setattr, _AV, "avancar", _AV.avancar)
        _AV.avancar = lambda agora=None, **_k: {"CANDIDATAS": 0, "POR_REGRA": {},
                                                "ENFILEIRADAS": []}
        self.tmp = Path(tempfile.mkdtemp(prefix="gatilho-test-"))
        self._orig = {"F.FILA": F.FILA, "GD.CANDIDATAS": GD.CANDIDATAS}
        F.FILA = self.tmp / "fila.json"
        GD.CANDIDATAS = self.tmp / "cand.json"
        self.feeder_calls = 0
        self.disc_calls = 0

    def tearDown(self):
        F.FILA = self._orig["F.FILA"]
        GD.CANDIDATAS = self._orig["GD.CANDIDATAS"]

    def _fila(self, n_pending):
        tarefas = [{"TASK_ID": "T%05d" % i, "SOURCE_ID": "CAND-%04d" % i,
                    "TASK_TYPE": F.QUALIFY, "PRIORITY": 30, "STATUS": F.PENDING,
                    "ATTEMPTS": 0, "NEXT_ATTEMPT_AT": None, "LAST_ERROR": None,
                    "MOTIVO": "", "CREATED_AT": "2026-09-21T00:00:00+00:00",
                    "UPDATED_AT": "2026-09-21T00:00:00+00:00"}
                   for i in range(n_pending)]
        F.FILA.write_text(json.dumps({"PROXIMO_ID": n_pending + 1,
                                      "TAREFAS": tarefas}), encoding="utf-8")

    def _candidatas(self, n_candidata):
        cs = [{"CANDIDATA_ID": "CAND-%04d" % i, "ESTADO": "CANDIDATA"}
              for i in range(n_candidata)]
        GD.CANDIDATAS.write_text(json.dumps({"CANDIDATAS": cs}), encoding="utf-8")

    def _feeder(self):
        self.feeder_calls += 1
        return {"TAREFAS_CRIADAS": 0}

    def _descobrir(self):
        self.disc_calls += 1
        return {"CANDIDATAS_NOVAS": 3}

    def test_queue_ok_nao_faz_nada(self):
        self._fila(50)
        self._candidatas(0)
        m = GD.talvez_alimentar({}, feeder_fn=self._feeder, descobrir_fn=self._descobrir)
        self.assertEqual(m["DECISAO"], "QUEUE_OK")
        self.assertEqual(self.feeder_calls, 0)
        self.assertEqual(self.disc_calls, 0)

    def test_fila_baixa_acervo_cheio_so_feeder(self):
        self._fila(2)
        self._candidatas(100)     # acervo cheio -> nao aciona discovery
        m = GD.talvez_alimentar({}, feeder_fn=self._feeder, descobrir_fn=self._descobrir)
        self.assertIn("FEEDER", m["ACCOES"])
        self.assertEqual(self.disc_calls, 0)
        self.assertTrue(m["DECISAO"].startswith("FEEDER_SO"))

    def test_fila_e_acervo_baixos_aciona_discovery(self):
        self._fila(2)
        self._candidatas(5)       # acervo baixo -> discovery
        estado = {}
        m = GD.talvez_alimentar(estado, feeder_fn=self._feeder, descobrir_fn=self._descobrir)
        self.assertEqual(m["DECISAO"], "DISCOVERY_ACCIONADA")
        self.assertEqual(self.disc_calls, 1)
        self.assertIn("LAST_DISCOVERY_AT", estado)

    def test_discovery_respeita_intervalo(self):
        self._fila(2)
        self._candidatas(5)
        agora = datetime.now(timezone.utc)
        estado = {"LAST_DISCOVERY_AT": (agora - timedelta(seconds=60)).isoformat()}
        m = GD.talvez_alimentar(estado, feeder_fn=self._feeder,
                                descobrir_fn=self._descobrir, agora=agora)
        self.assertEqual(m["DECISAO"], "DISCOVERY_EM_INTERVALO")
        self.assertEqual(self.disc_calls, 0, "nao pode crawlar dentro do intervalo")


class TestLigacaoRealDoDiscovery(unittest.TestCase):
    """⚠️ OS QUATRO TESTES ACIMA INJECTAM `descobrir_fn`.

    Por isso nunca tocaram em `_discovery_real` — e o caminho de PRODUCAO
    esteve partido 2298 voltas seguidas com a suite verde: `_discovery_real`
    chamava `crawl_sementes(max_sementes=...)` quando a assinatura real exige
    quatro posicionais. O TypeError caia no `except` do supervisor, virava uma
    linha `DISCOVERY_HOOK_ERRO` no log, e o servico ficava IDLE a dizer-se sao.

        CHAMAR O GATILHO TEM DE PRODUZIR TAREFAS OU ERRO VISIVEL.
        NUNCA SILENCIO.

    Estes testes exercitam o caminho por omissao (sem `descobrir_fn`), com a
    rede substituida por um espiao que VALIDA A LIGACAO contra a assinatura
    verdadeira de `crawl_sementes`. Se alguem mudar a assinatura outra vez,
    falha aqui — nao em producao, calado.
    """

    def setUp(self):
        # CUR-PRONTA: o gatilho passou a chamar o AVANCAR antes do discovery, e
        # o AVANCAR le o livro VERDADEIRO do repositorio. Esta classe mede a
        # procura de fontes novas: o avanco fica a zero aqui (tem testes
        # proprios em test_avancar_fontes.py).
        import avancar_fontes as _AV
        self.addCleanup(setattr, _AV, "avancar", _AV.avancar)
        _AV.avancar = lambda agora=None, **_k: {"CANDIDATAS": 0, "POR_REGRA": {},
                                                "ENFILEIRADAS": []}
        import descobrir as D
        self.D = D
        self.tmp = Path(tempfile.mkdtemp(prefix="gatilho-real-"))
        self._orig = {"F.FILA": F.FILA, "GD.CANDIDATAS": GD.CANDIDATAS,
                      "crawl": D.crawl_sementes}
        F.FILA = self.tmp / "fila.json"
        GD.CANDIDATAS = self.tmp / "cand.json"
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}),
                          encoding="utf-8")
        GD.CANDIDATAS.write_text(json.dumps({"CANDIDATAS": []}), encoding="utf-8")

        # A assinatura VERDADEIRA, capturada antes de substituir a funcao.
        self.sig = inspect.signature(D.crawl_sementes)
        self.chamadas = []

        def _espiao(*a, **k):
            # Levanta TypeError se a chamada do gatilho nao casar. E este o
            # defeito que se esta a prender.
            self.sig.bind(*a, **k)
            self.chamadas.append(k or a)
            return ([{"id": "CAND-9001", "url": "https://exemplo.it/a"}],
                    {"SEMENTES_USADAS": 1, "PAGINAS_BUSCADAS": 1,
                     "ROBOTS_BLOCKS": 0})

        D.crawl_sementes = _espiao

    def tearDown(self):
        F.FILA = self._orig["F.FILA"]
        GD.CANDIDATAS = self._orig["GD.CANDIDATAS"]
        self.D.crawl_sementes = self._orig["crawl"]

    def test_discovery_real_casa_com_a_assinatura_de_crawl_sementes(self):
        m = GD._discovery_real()
        self.assertEqual(len(self.chamadas), 1, "crawl_sementes nao foi chamado")
        self.assertEqual(m["CANDIDATAS_NOVAS"], 1)
        self.assertEqual(m["CRAWL"], 1)

    def test_o_hook_do_supervisor_produz_accoes_e_nao_silencio(self):
        """Reproduz o `_hook_fila_vazia` do supervisor, sem injeccoes."""
        estado = {}
        m = GD.talvez_alimentar(estado, feeder_fn=lambda: {"TAREFAS_CRIADAS": 0})
        self.assertIn("DISCOVERY", m["ACCOES"],
                      "fila vazia + acervo vazio tem de accionar DISCOVERY")
        self.assertTrue(m["ACCOES"], "ACCOES vazio = o supervisor nao anota nada")
        self.assertIn("LAST_DISCOVERY_AT", estado)

    def test_assinatura_errada_estoura_a_vista_e_nao_em_silencio(self):
        """A contraprova: com a assinatura antiga, isto TEM de falhar."""
        def _antigo():
            import descobrir as D
            return D.crawl_sementes(max_sementes=D.MAX_SEMENTES_ESTA_CORRIDA)
        with self.assertRaises(TypeError):
            _antigo()


if __name__ == "__main__":
    unittest.main(verbosity=2)
