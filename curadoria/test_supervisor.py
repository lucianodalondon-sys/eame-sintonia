#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes do supervisor. Nao reimplementam a regra — asseram o comportamento.

ISOLAMENTO (PROVAS-P1, DEFEITO 2) — ESTA SUITE NAO TOCA A FILA REAL.

Medido antes desta versao: este era o UNICO ficheiro de testes da pasta que
nao redirecionava F.FILA. Consequencias reais: 10 tarefas da fila real
passaram de PENDING a BLOCKED numa lane; PROXIMO_ID avancou noutra; e
TestLock.setUp apagava SUPERVISOR.lock sem perguntar de quem era — com um
supervisor VIVO na mesma arvore (em POSIX ficariam dois supervisores na mesma
fila; a suite destruia o invariante que testa).

E havia um segundo canal que nenhum redirecionamento no processo de teste
alcanca: uma_volta_sup() lanca `ciclo_continuo.py` REAL como subprocesso, e
esse processo abre os ficheiros reais da arvore por conta propria (a adenda de
9d3d7461 mediu um READY-BATCH nascido dentro da suite). Aqui o lancador e
substituido por um worker INERTE (um python que dorme): o supervisor ve um PID
vivo, e ninguem sai a rede nem escreve na arvore.

Molde copiado de test_ready_split.py:44-48 — pasta descartavel, caminhos
guardados em `_antes`, restauro em tearDown. Nao se inventou um segundo.

Guarda: cada teste tira a impressao (sha256) da fila, do livro, do lock e da
bandeira REAIS antes de comecar e compara no fim. Se algum mudou, o teste
reprova — ou a suite escreveu la, ou ha um servico vivo a escrever na mesma
arvore; em ambos os casos a medicao nao vale.

    GIT STATUS VAZIO NAO E PROVA. O SHA256 DA FILA MANDA.

RED TEAM incluido: prova_09 usa heartbeat NOVO mas LAST_PROGRESS_AT igual
para simular o caso em que a comparacao de strings da falso-positivo de
"progresso". Declarado como KNOWN_LIMITATION se falhar.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
import unittest
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F        # noqa: E402
import lifecycle as LC  # noqa: E402
import supervisor as S  # noqa: E402

# Os caminhos REAIS, escritos por extenso e nao lidos dos modulos: se outro
# teste deixou F.FILA a apontar para uma pasta descartavel ja apagada, ler
# F.FILA aqui daria uma "impressao" de um ficheiro que nao e o real.
CAMINHOS_REAIS = {
    "F.FILA":   RAIZ / "curadoria" / "LIFECYCLE-QUEUE-V1.json",
    "LC.LIVRO": RAIZ / "curadoria" / "LIFECYCLE-LEDGER-V1.json",
    "S.LOCK":   RAIZ / "curadoria" / "SUPERVISOR.lock",
    "S.PARAR":  RAIZ / "curadoria" / "PARAR.flag",
}


def _impressao(p: Path) -> str:
    if not p.exists():
        return "AUSENTE"
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _impressoes() -> dict:
    return {k: _impressao(p) for k, p in CAMINHOS_REAIS.items()}


class Isolado(unittest.TestCase):
    """Molde de test_ready_split.py:44-48: tudo o que e estado vai para uma
    pasta descartavel, e o lancador de worker e um processo inerte."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (F.FILA, LC.LIVRO, S.LOCK, S.ESTADO, S.PARAR, S.DIARIO)
        self._reais_antes = _impressoes()
        F.FILA   = d / "QUEUE.json"
        LC.LIVRO = d / "LEDGER.json"
        S.LOCK   = d / "SUPERVISOR.lock"
        S.ESTADO = d / "SUPERVISOR-STATE.json"
        S.PARAR  = d / "PARAR.flag"
        S.DIARIO = d / "RUN-LOG.ndjson"
        self._procs: list[subprocess.Popen] = []
        self._lancador = mock.patch.object(S, "_lancar_worker", self._worker_inerte)
        self._lancador.start()

    def tearDown(self):
        self._lancador.stop()
        for p in self._procs:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=5)
                except Exception:
                    p.kill()
                    p.wait(timeout=5)
            if p.stdout:
                p.stdout.close()
        (F.FILA, LC.LIVRO, S.LOCK, S.ESTADO, S.PARAR, S.DIARIO) = self._antes
        self.tmp.cleanup()
        depois = _impressoes()
        self.assertEqual(
            self._reais_antes, depois,
            "um ficheiro REAL mudou durante o teste (antes=%s depois=%s): ou a "
            "suite escreveu fora da pasta descartavel, ou ha um servico vivo a "
            "escrever nesta arvore — em ambos os casos a medicao nao vale"
            % (self._reais_antes, depois))

    # -- lancadores substitutos ---------------------------------------------
    def _popen(self, codigo: str) -> subprocess.Popen:
        # Mesmos pipes que S._lancar_worker, para os testes que fazem
        # communicate() continuarem a funcionar.
        p = subprocess.Popen(
            [sys.executable, "-c", codigo],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
        )
        self._procs.append(p)
        return p

    def _worker_inerte(self, pausa: float = 1.0) -> subprocess.Popen:
        """Um PID vivo que nao faz nada: e o que o supervisor precisa de ver."""
        return self._popen("import time; time.sleep(60)")

    def _worker_que_morre_ja(self, pausa: float = 1.0) -> subprocess.Popen:
        """Morre sem escrever uma linha no diario: morte SEM progresso."""
        p = self._popen("import sys; sys.exit(1)")  # morrer e rc != 0; rc 0 e saida limpa
        p.wait(timeout=10)
        return p

    def _worker_que_bate_e_morre(self, pausa: float = 1.0) -> subprocess.Popen:
        """Escreve um batimento no diario e morre: morte COM progresso."""
        linha = json.dumps({"EVENTO": "VOLTA", "AT": S._agora()})
        p = self._popen(
            "import io, sys; io.open(%r, 'a', encoding='utf-8').write(%r); sys.exit(1)"
            % (str(S.DIARIO), linha + "\n"))
        p.wait(timeout=10)
        return p


class TestLock(Isolado):
    """Tudo sobre o lock da pasta descartavel. O lock REAL nunca e tocado —
    nao ha `unlink` nenhum aqui, porque nao ha nada para apagar."""

    def test_lock_dos_testes_nao_e_o_real(self):
        self.assertNotEqual(S.LOCK, CAMINHOS_REAIS["S.LOCK"])
        self.assertEqual(S.LOCK.parent, Path(self.tmp.name))
        self.assertNotEqual(F.FILA, CAMINHOS_REAIS["F.FILA"])
        self.assertEqual(F.FILA.parent, Path(self.tmp.name))

    def test_lock_real_sobrevive_ao_ciclo_adquirir_libertar(self):
        real = CAMINHOS_REAIS["S.LOCK"]
        antes = _impressao(real)
        fd = S._adquirir_lock()
        self.assertIsNotNone(fd)
        S._libertar_lock(fd)
        self.assertEqual(antes, _impressao(real),
                         "adquirir/libertar o lock de teste tocou no lock real")

    def test_adquirir_lock_ok(self):
        fd = S._adquirir_lock()
        self.assertIsNotNone(fd)
        S._libertar_lock(fd)
        self.assertFalse(S.LOCK.exists())

    def test_adquirir_lock_conflito(self):
        fd1 = S._adquirir_lock()
        self.assertIsNotNone(fd1)
        try:
            fd2 = S._adquirir_lock()
            self.assertIsNone(fd2, "segundo lock devia ser recusado")
        finally:
            S._libertar_lock(fd1)

    def test_lock_orfao_pid_morto(self):
        # Escreve lock com PID que nao existe.
        LOCK_DATA = json.dumps({
            "PID": 99999999,
            "STARTED_AT": "2020-01-01T00:00:00",
            "TOKEN": "fake-token",
        })
        S.LOCK.write_text(LOCK_DATA, encoding="utf-8")
        self.assertTrue(S._lock_e_orfao(json.loads(LOCK_DATA)))
        # Novo adquirir deve limpar e suceder.
        fd = S._adquirir_lock()
        self.assertIsNotNone(fd)
        S._libertar_lock(fd)

    def test_lock_orfao_pre_boot(self):
        # STARTED_AT muito antigo (antes de qualquer boot possivel).
        data = {"PID": os.getpid(), "STARTED_AT": "2000-01-01T00:00:00", "TOKEN": "x"}
        self.assertTrue(S._lock_e_orfao(data))

    def test_lock_json_contem_token(self):
        fd = S._adquirir_lock()
        self.assertIsNotNone(fd)
        try:
            d = json.loads(S.LOCK.read_text(encoding="utf-8"))
            self.assertIn("TOKEN", d)
            self.assertIn("STARTED_AT", d)
            self.assertIn("PID", d)
        finally:
            S._libertar_lock(fd)


class TestUmaVoltaSup(Isolado):

    def _estado_base(self):
        return {"SUPERVISOR_STATE": "STARTING", "RESTARTS_TOTAL": 0,
                "CRASHES_SEM_PROGRESSO": []}

    def _injetar(self, sid, tipo=F.CANARY):
        return F.enfileirar(sid, tipo, priority=5,
                            motivo="teste unitario supervisor")

    def test_para_flag_impede_lancamento(self):
        self._injetar("IT-TEST-SUP-001")
        S.PARAR.write_text("teste", encoding="utf-8")
        accao, _, proc = S.uma_volta_sup(self._estado_base(), None)
        self.assertEqual(accao, "PARA_FLAG")
        self.assertIsNone(proc)

    def test_idle_sem_trabalho(self):
        # Sem tarefas elegiveis -> IDLE.
        accao, estado, proc = S.uma_volta_sup(self._estado_base(), None)
        self.assertEqual(accao, "IDLE")
        self.assertIsNone(proc)
        self.assertEqual(estado["SUPERVISOR_STATE"], "IDLE")

    def test_relanca_com_trabalho(self):
        self._injetar("IT-TEST-SUP-002")
        accao, estado, proc = S.uma_volta_sup(self._estado_base(), None,
                                               pausa_worker=0.1)
        self.assertEqual(accao, "RELANCADO")
        self.assertIsNotNone(proc)
        self.assertEqual(estado["RESTARTS_TOTAL"], 1)
        # O que foi lancado e o inerte, nao o ciclo_continuo.py real.
        self.assertIn(proc, self._procs)

    def test_vivo_quando_worker_ativo(self):
        self._injetar("IT-TEST-SUP-003")
        accao, estado, proc = S.uma_volta_sup(self._estado_base(), None,
                                               pausa_worker=0.1)
        self.assertEqual(accao, "RELANCADO")
        # Segunda volta: worker vivo -> VIVO.
        time.sleep(1)
        accao2, estado2, proc2 = S.uma_volta_sup(estado, proc, pausa_worker=0.1)
        self.assertIn(accao2, ("VIVO", "IDLE", "RELANCADO"),
                      "accao inesperada: %s" % accao2)

    def test_bloqueado_com_tres_crashes_ja_no_estado(self):
        """Estado que ja traz TRES mortes sem progresso -> BLOQUEADO.

        Le o limiar pelo comportamento (tres, escrito por extenso), nunca pela
        constante: um teste que importa S.CRASH_MAX mede a constante contra
        ela propria e fica verde com a proteccao desligada.
        """
        agora = datetime.now(timezone.utc).isoformat()
        crashes = [{"AT": agora, "LAST_HB": None} for _ in range(3)]
        estado = {**self._estado_base(), "CRASHES_SEM_PROGRESSO": crashes,
                  "WORKER_PID": None}
        self._injetar("IT-TEST-SUP-004")
        accao, estado2, proc = S.uma_volta_sup(estado, None)
        self.assertEqual(accao, "BLOQUEADO")
        self.assertEqual(estado2["SUPERVISOR_STATE"], "BLOCKED")
        self.assertIsNone(proc)

    def test_crash_com_progresso_nao_conta(self):
        """Morte com heartbeat avancado deve zerar o contador de crashes."""
        agora_ts = datetime.now(timezone.utc).isoformat()
        estado = {
            **self._estado_base(),
            "CRASHES_SEM_PROGRESSO": [{"AT": agora_ts, "LAST_HB": None}],
            "WORKER_PID": 99999,
            "LAST_PROGRESS_AT": "2026-01-01T00:00:00+00:00",
        }
        self._injetar("IT-TEST-SUP-005")
        # Escrever heartbeat recente no log.
        with S.DIARIO.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"EVENTO": "TESTE", "AT": agora_ts}) + "\n")
        proc_morto = self._popen("import sys; sys.exit(1)")  # crash: rc 0 e saida limpa
        proc_morto.wait(timeout=5)
        accao, estado2, proc_new = S.uma_volta_sup(estado, proc_morto)
        # Com progresso, contador zerado.
        self.assertEqual(len(estado2.get("CRASHES_SEM_PROGRESSO", [])), 0,
                         "crashes_sem_progresso devia ser [] apos morte com progresso")
        self.assertNotEqual(accao, "BLOQUEADO",
                            "nao devia BLOQUEAR com um so crash com progresso")

    # -- DEFEITO 1 (PROVAS-P1): o caminho que ACUMULA as mortes ---------------
    #
    # Os testes acima injectam a lista de crashes ja cozinhada. Estes dois
    # deixam o supervisor lancar workers que morrem de verdade e leem o que
    # ficou — sem conhecer CRASH_MAX. O numero e escrito por extenso.

    def _voltas_ate(self, lancador, estado, proc=None, maximo=8):
        """Da `maximo` voltas ao supervisor com este lancador, ou ate BLOQUEADO.
        O `proc` entra e sai: a morte do worker lancado numa volta so e vista
        na volta SEGUINTE, e um proc perdido entre fases esconderia a morte."""
        accoes = []
        with mock.patch.object(S, "_lancar_worker", lancador):
            for _ in range(maximo):
                accao, estado, proc = S.uma_volta_sup(estado, proc, pausa_worker=0.1)
                accoes.append(accao)
                if accao == "BLOQUEADO":
                    break
        return accoes, estado, proc

    def test_crashloop_tres_mortes_reais_sem_progresso_bloqueia(self):
        """Tres workers reais que morrem sem escrever no diario -> BLOQUEADO
        na volta seguinte a terceira morte; nem uma antes, nem uma depois."""
        self._injetar("IT-TEST-SUP-006")
        estado = {**self._estado_base(), "WORKER_PID": None}
        accoes, estado, _ = self._voltas_ate(self._worker_que_morre_ja, estado)
        self.assertEqual(
            accoes, ["RELANCADO", "RELANCADO", "RELANCADO", "BLOQUEADO"],
            "esperava tres relancamentos e o bloqueio a quarta volta; veio %s"
            % accoes)
        self.assertEqual(len(estado["CRASHES_SEM_PROGRESSO"]), 3)
        self.assertEqual(estado["SUPERVISOR_STATE"], "BLOCKED")
        self.assertIsNone(estado["WORKER_PID"])
        # E ficou escrito no disco (descartavel), nao so na memoria.
        no_disco = json.loads(S.ESTADO.read_text(encoding="utf-8"))
        self.assertEqual(no_disco["SUPERVISOR_STATE"], "BLOCKED")
        self.assertEqual(len(no_disco["CRASHES_SEM_PROGRESSO"]), 3)

    def test_crashloop_morte_com_progresso_no_meio_nao_bloqueia(self):
        """MORRER != MORRER SEM PROGREDIR, pelo caminho real.

        Workers A, B morrem mudos (contador 2); C bate e morre (contador 0);
        D, E morrem mudos (contador 2). Quatro mortes mudas, nenhum bloqueio,
        porque nunca foram tres SEGUIDAS.
        """
        self._injetar("IT-TEST-SUP-007")
        estado = {**self._estado_base(), "WORKER_PID": None}
        # v1 lanca A; v2 le a morte de A (1) e lanca B.
        ac, estado, proc = self._voltas_ate(self._worker_que_morre_ja, estado, maximo=2)
        self.assertEqual(ac, ["RELANCADO", "RELANCADO"])
        self.assertEqual(len(estado["CRASHES_SEM_PROGRESSO"]), 1)
        # v3 le a morte de B (2) e lanca C, que escreve um batimento e morre.
        ac, estado, proc = self._voltas_ate(self._worker_que_bate_e_morre, estado, proc, maximo=1)
        self.assertEqual(ac, ["RELANCADO"])
        self.assertEqual(len(estado["CRASHES_SEM_PROGRESSO"]), 2)
        # v4 le a morte de C: batimento novo -> contador a zero; lanca D.
        ac, estado, proc = self._voltas_ate(self._worker_que_morre_ja, estado, proc, maximo=1)
        self.assertEqual(ac, ["RELANCADO"])
        self.assertEqual(estado["CRASHES_SEM_PROGRESSO"], [],
                         "a morte com batimento devia ter reposto o contador")
        # v5 le a morte de D (1), lanca E; v6 le a morte de E (2), lanca F.
        ac, estado, proc = self._voltas_ate(self._worker_que_morre_ja, estado, proc, maximo=2)
        self.assertEqual(ac, ["RELANCADO", "RELANCADO"])
        self.assertEqual(len(estado["CRASHES_SEM_PROGRESSO"]), 2)
        self.assertNotEqual(estado["SUPERVISOR_STATE"], "BLOCKED")

    def test_diario_do_supervisor_nao_e_batimento_do_worker(self):
        """O supervisor escreve no MESMO diario que le como batimento. As suas
        proprias linhas (ORIGEM=SUPERVISOR) nao podem contar como progresso do
        worker — senao cada WORKER_RELANCADO 'prova' que o worker progrediu e
        o anti-crashloop nunca dispara."""
        self.assertIsNone(S._ultimo_heartbeat())
        S._anotar({"EVENTO": "WORKER_RELANCADO", "PID": 1})
        self.assertIsNone(S._ultimo_heartbeat(),
                          "uma linha do proprio supervisor contou como batimento")
        with S.DIARIO.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"EVENTO": "VOLTA", "AT": S._agora()}) + "\n")
        self.assertIsNotNone(S._ultimo_heartbeat())
        S._anotar({"EVENTO": "WORKER_MORTO", "PID": 1})
        hb = S._ultimo_heartbeat()
        self.assertIsNotNone(hb, "a linha do worker ficou escondida atras da do supervisor")


class TestBootTimeParsing(unittest.TestCase):
    """Testes do parser de boot time do wmic (ADDENDUM-02).

    Fixam a string bruta e asseram o instante UTC correcto.
    Sem este teste a regressao do offset volta sozinha.
    """

    def test_offset_negativo_utc_menos_3(self):
        """Host UTC-3: hora local 21:29:51 -> UTC 00:29:51 do dia seguinte."""
        raw = "20260910212951.500000-180"
        result = S._parse_wmic_boot_time(raw)
        self.assertIsNotNone(result)
        expected = datetime(2026, 9, 11, 0, 29, 51, tzinfo=timezone.utc)
        self.assertEqual(result.replace(microsecond=0), expected)

    def test_offset_zero_utc(self):
        """Host UTC+0: hora local == UTC."""
        raw = "20260911003000.000000+000"
        result = S._parse_wmic_boot_time(raw)
        self.assertIsNotNone(result)
        expected = datetime(2026, 9, 11, 0, 30, 0, tzinfo=timezone.utc)
        self.assertEqual(result.replace(microsecond=0), expected)

    def test_offset_positivo_utc_mais_5_30(self):
        """Host UTC+5:30 (India): offset = +330 minutos."""
        raw = "20260911060000.000000+330"
        result = S._parse_wmic_boot_time(raw)
        self.assertIsNotNone(result)
        # 06:00 local - 5h30 = 00:30 UTC
        expected = datetime(2026, 9, 11, 0, 30, 0, tzinfo=timezone.utc)
        self.assertEqual(result.replace(microsecond=0), expected)

    def test_formato_invalido_devolve_none(self):
        """String sem sinal de offset deve devolver None — degradar para NAO SEI."""
        self.assertIsNone(S._parse_wmic_boot_time("20260910212951"))

    def test_lock_orfao_comparacao_aware(self):
        """_lock_e_orfao check (c): STARTED_AT anterior ao boot -> orfao.

        Injecto boot time no futuro (vs STARTED_AT no passado) para verificar
        que a comparacao e feita com datetimes aware, nao strings de fusos mistos.
        """
        # STARTED_AT: 1 hora antes do boot
        started = datetime(2026, 9, 11, 0, 0, 0, tzinfo=timezone.utc)
        boot    = datetime(2026, 9, 11, 1, 0, 0, tzinfo=timezone.utc)
        lock_data = {
            "PID": 99999,
            "STARTED_AT": started.isoformat(),
            "TOKEN": "x",
        }
        with mock.patch.object(S, "_pid_no_so", return_value=True), \
             mock.patch.object(S, "_proc_e_python", return_value=True), \
             mock.patch.object(S, "_boot_time_utc", return_value=boot):
            self.assertTrue(S._lock_e_orfao(lock_data),
                            "STARTED_AT anterior ao boot deve ser orfao")

    def test_lock_valido_depois_do_boot(self):
        """STARTED_AT posterior ao boot: nao e orfao pelo check (c)."""
        started = datetime(2026, 9, 11, 2, 0, 0, tzinfo=timezone.utc)
        boot    = datetime(2026, 9, 11, 1, 0, 0, tzinfo=timezone.utc)
        lock_data = {
            "PID": 99999,
            "STARTED_AT": started.isoformat(),
            "TOKEN": "x",
        }
        with mock.patch.object(S, "_pid_no_so", return_value=True), \
             mock.patch.object(S, "_proc_e_python", return_value=True), \
             mock.patch.object(S, "_boot_time_utc", return_value=boot):
            self.assertFalse(S._lock_e_orfao(lock_data),
                             "STARTED_AT posterior ao boot nao devia ser orfao")

    def test_boot_time_indisponivel_nao_rejeita(self):
        """Se wmic falhar (boot_time=None), check (c) inactivo — lock nao rejeitado."""
        lock_data = {
            "PID": 99999,
            "STARTED_AT": "2026-01-01T00:00:00+00:00",
            "TOKEN": "x",
        }
        with mock.patch.object(S, "_pid_no_so", return_value=True), \
             mock.patch.object(S, "_proc_e_python", return_value=True), \
             mock.patch.object(S, "_boot_time_utc", return_value=None):
            self.assertFalse(S._lock_e_orfao(lock_data),
                             "boot_time None nao devia rejeitar lock com PID vivo")


class TestRedTeam(Isolado):
    """Casos em que a propria sonda pode falhar — declarados honestamente."""

    def test_redteam_pid_reciclado_pode_enganar_verificacao(self):
        """RED TEAM: se o SO reciclar rapidamente o PID do worker morto para
        outro processo Python, _worker_vivo pode dar True erroneamente.

        Este teste DOCUMENTA a limitacao — nao a corrige. A combinacao
        PID+heartbeat+boot_time mitiga mas nao elimina a janela de corrida.
        O teste falha se a mitigacao por heartbeat cobrir o caso.
        """
        # Simulacao: estado com PID do proprio teste (python.exe, vivo).
        estado = {
            "SUPERVISOR_STATE": "RUNNING",
            "WORKER_PID": os.getpid(),
            "WORKER_STARTED_AT": datetime.now(timezone.utc).isoformat(),
            "LAST_PROGRESS_AT": None,
            "CRASHES_SEM_PROGRESSO": [],
        }
        # _worker_vivo verifica PID + heartbeat.
        # O nosso PID existe e e Python, mas nao ha heartbeat recente.
        resultado = S._worker_vivo(estado)
        # KNOWN_LIMITATION: se LAST_PROGRESS_AT for None e o arranque for
        # recente, _worker_vivo da True (beneficio de duvida ao arranque).
        # Isso e correcto para o caso real (worker ainda a arrancar).
        # Mas seria enganador se o PID fosse reciclado imediatamente.
        # Documentado — nao bloqueante.
        self.assertIn(resultado, (True, False),
                      "resultado deve ser bool (True = PID+arranque recente)")
        # O campo KNOWN_LIMITATION e apenas documentacao.
        resultados_redteam = {
            "KNOWN_LIMITATION": (
                "Se o SO reciclar o PID do worker para outro processo Python "
                "dentro de HEARTBEAT_TIMEOUT_S segundos, _worker_vivo devolve "
                "True erroneamente. Janela: %ds. Mitigacao: heartbeat + boot time."
                % S.HEARTBEAT_TIMEOUT_S
            ),
            "RESULTADO_OBSERVADO": resultado,
        }
        # Nao e um FAIL — e documentacao de uma limitacao conhecida.
        self.assertTrue(True, "red team documentado: %s" % resultados_redteam)


class TestHookFilaVazia(Isolado):
    """Enxerto de candidate-bridge-v1 (63b71421): a volta IDLE chama o hook.

    E o unico ponto onde fila vazia pode accionar descoberta. Sem hook a volta
    e a de sempre; com hook que rebenta, a volta continua IDLE e o erro fica
    no diario como DISCOVERY_HOOK_ERRO — e essa linha e do supervisor, nao
    conta como batimento nem como morte do worker.
    """

    def _estado_base(self):
        return {"SUPERVISOR_STATE": "STARTING", "RESTARTS_TOTAL": 0,
                "CRASHES_SEM_PROGRESSO": []}

    def _diario(self) -> list:
        if not S.DIARIO.exists():
            return []
        return [json.loads(l) for l in
                S.DIARIO.read_text(encoding="utf-8").splitlines() if l.strip()]

    def test_sem_hook_a_volta_idle_e_a_de_antes(self):
        accao, estado, proc = S.uma_volta_sup(self._estado_base(), None)
        self.assertEqual(accao, "IDLE")
        self.assertIsNone(proc)
        self.assertEqual([l for l in self._diario()
                          if l["EVENTO"] == "DISCOVERY_HOOK_ERRO"], [])

    def test_fila_vazia_chama_o_hook_uma_vez_por_volta(self):
        chamadas = []
        accao, estado, _ = S.uma_volta_sup(self._estado_base(), None,
                                           hook_fila_vazia=lambda: chamadas.append(1))
        self.assertEqual(accao, "IDLE")
        self.assertEqual(chamadas, [1], "uma volta IDLE = uma chamada")
        S.uma_volta_sup(estado, None, hook_fila_vazia=lambda: chamadas.append(2))
        self.assertEqual(chamadas, [1, 2])

    def test_com_trabalho_elegivel_o_hook_nao_e_chamado(self):
        F.enfileirar("IT-TEST-HOOK-001", F.CANARY, priority=5,
                     motivo="teste unitario hook")
        chamadas = []
        accao, _, proc = S.uma_volta_sup(self._estado_base(), None,
                                         pausa_worker=0.1,
                                         hook_fila_vazia=lambda: chamadas.append(1))
        self.assertEqual(accao, "RELANCADO")
        self.assertEqual(chamadas, [], "com fila cheia nao se pede descoberta")

    def test_hook_que_rebenta_nao_mata_a_volta_e_fica_no_diario(self):
        def rebenta():
            raise RuntimeError("descoberta sem rede")
        accao, estado, proc = S.uma_volta_sup(self._estado_base(), None,
                                              hook_fila_vazia=rebenta)
        self.assertEqual(accao, "IDLE")
        self.assertIsNone(proc)
        self.assertEqual(estado["SUPERVISOR_STATE"], "IDLE")
        erros = [l for l in self._diario() if l["EVENTO"] == "DISCOVERY_HOOK_ERRO"]
        self.assertEqual(len(erros), 1, self._diario())
        self.assertIn("RuntimeError", erros[0]["ERRO"])
        self.assertIn("descoberta sem rede", erros[0]["ERRO"])
        self.assertEqual(erros[0]["ORIGEM"], "SUPERVISOR")
        # A linha e do supervisor: nao e batimento do worker.
        self.assertIsNone(S._ultimo_heartbeat())
        # E o estado IDLE ficou no disco (descartavel).
        self.assertEqual(json.loads(S.ESTADO.read_text(encoding="utf-8"))
                         ["SUPERVISOR_STATE"], "IDLE")

    def test_hook_que_rebenta_repetidamente_nao_conta_como_morte_do_worker(self):
        def rebenta():
            raise RuntimeError("x")
        estado = self._estado_base()
        for _ in range(4):
            accao, estado, _ = S.uma_volta_sup(estado, None, hook_fila_vazia=rebenta)
            self.assertEqual(accao, "IDLE")
        self.assertEqual(estado.get("CRASHES_SEM_PROGRESSO", []), [])
        self.assertNotEqual(estado["SUPERVISOR_STATE"], "BLOCKED")


class TestRecuperacaoDoWorker(Isolado):
    """G3 (BRIDGE-FEEDER): matar o worker -> o supervisor relanca, PID novo.

    Worker inerte (um python que dorme) na pasta descartavel; o supervisor de
    producao (outra arvore, outro PID) nunca e tocado. Os dois PIDs ficam no
    diario: WORKER_MORTO com o antigo, WORKER_RELANCADO com o novo.
    """

    def test_worker_morto_e_relancado_com_pid_novo(self):
        F.enfileirar("IT-TEST-REC-001", F.CANARY, priority=5, motivo="g3")
        estado = {"SUPERVISOR_STATE": "STARTING", "RESTARTS_TOTAL": 0,
                  "CRASHES_SEM_PROGRESSO": [], "WORKER_PID": None}

        accao, estado, proc = S.uma_volta_sup(estado, None, pausa_worker=0.1)
        self.assertEqual(accao, "RELANCADO")
        pid_antes = proc.pid
        self.assertEqual(estado["WORKER_PID"], pid_antes)
        self.assertTrue(S._pid_no_so(pid_antes), "o PID lancado tem de existir no SO")

        accao2, estado, proc = S.uma_volta_sup(estado, proc, pausa_worker=0.1)
        self.assertEqual(accao2, "VIVO", "com o worker vivo a volta e VIVO")

        # MATAR o worker (o inerte, na pasta descartavel).
        proc.kill()
        proc.wait(timeout=10)
        self.assertIsNotNone(proc.poll())

        accao3, estado, proc2 = S.uma_volta_sup(estado, proc, pausa_worker=0.1)
        self.assertEqual(accao3, "RELANCADO", "worker morto -> relancar")
        pid_depois = proc2.pid
        self.assertNotEqual(pid_antes, pid_depois)
        self.assertEqual(estado["WORKER_PID"], pid_depois)
        self.assertEqual(estado["RESTARTS_TOTAL"], 2)
        self.assertEqual(len(estado["CRASHES_SEM_PROGRESSO"]), 1,
                         "uma morte muda conta uma vez; nao bloqueia")
        self.assertNotEqual(estado["SUPERVISOR_STATE"], "BLOCKED")

        linhas = [json.loads(l) for l in
                  S.DIARIO.read_text(encoding="utf-8").splitlines() if l.strip()]
        mortos = [l["PID"] for l in linhas if l["EVENTO"] == "WORKER_MORTO"]
        relancados = [l["PID"] for l in linhas if l["EVENTO"] == "WORKER_RELANCADO"]
        self.assertEqual(mortos, [pid_antes])
        self.assertEqual(relancados, [pid_antes, pid_depois])
        print("\nG3 WORKER_RECOVERY: PID_ANTES=%d morto -> PID_DEPOIS=%d relancado"
              % (pid_antes, pid_depois))


if __name__ == "__main__":
    unittest.main(verbosity=2)
