#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM da telemetria (missao TELEMETRIA-V1) — SURVIVORS = 0.

Protocolo CACHE-SAFE (obrigatorio nesta lane):
  - PYTHONDONTWRITEBYTECODE=1 e apagar __pycache__/.pyc ANTES e DEPOIS;
  - processo novo por mutante;
  - BASELINE: o teste-assassino PASSA no codigo limpo (prova que ele exercita o alvo);
  - provar que a mutacao ficou no FONTE (a string trocada);
  - o teste-assassino REPROVA com a mutacao (o codigo mutado executou e mudou o
    resultado — mutante que «morre» sem executar o codigo mutado NAO conta);
  - restaurar e limpar cache outra vez.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CUR = RAIZ / "curadoria"

# (id, descricao, ficheiro, velho, novo, teste_assassino)
MUTANTES = [
    ("M1_READY_IGUAL_DISCOVERED",
     "READY_CURRENT passa a contar tambem CONTRACT_PENDING (conflacao)",
     "telemetria_do_curador.py", "if ns == READY:", "if ns == READY or ns == LC.CONTRACT_PENDING:",
     "test_telemetria.py TestTelemetria.test_ready_e_subconjunto_das_concluidas"),
    ("M2_PAINEL_CONFIA_NO_JSON",
     "liveness do supervisor confia no ficheiro, nao no SO",
     "supervisor.py", "sup_vivo = bool(sup_pid and _pid_no_so(sup_pid))",
     "sup_vivo = bool(sup_pid)",
     "test_telemetria.py TestTelemetria.test_json_stale_nao_diz_running_se_processo_morreu"),
    ("M3_READY_INCREMENTA_2X",
     "contador de READY incrementa 2x na mesma transicao",
     "telemetria_do_curador.py", 'm["READY_CURRENT"] += 1', 'm["READY_CURRENT"] += 2',
     "test_telemetria.py TestTelemetria.test_janela_24h_inclui_evento_correto"),
    ("M4_EVENTO_ANTIGO_NA_JANELA_1H",
     "a janela deixa de filtrar por tempo (evento antigo entra)",
     "telemetria_do_curador.py", "if at is None or not (desde <= at < ate):", "if at is None:",
     "test_telemetria.py TestTelemetria.test_janela_1h_nao_inclui_evento_antigo"),
    ("M5_RESTART_ZERA_24H",
     "a janela 24h passa a comecar na sessao (restart apaga producao)",
     "telemetria_do_curador.py", "j24 = _janela(tr, n - timedelta(hours=24), n)",
     "j24 = _janela(tr, sess_ini, n)",
     "test_telemetria.py TestTelemetria.test_reiniciar_supervisor_nao_zera_producao_24h"),
    ("M6_BLOQUEIO_CONTA_COMO_READY",
     "CAPABILITY_BLOCK passa a incrementar READY_CURRENT",
     "telemetria_do_curador.py", 'm["CAPABILITY_BLOCK"] += 1', 'm["READY_CURRENT"] += 1',
     "test_telemetria.py TestTelemetria.test_bloqueio_nao_conta_como_ready"),
    ("M7_SEM_PROGRESSO_PARECE_NORMAL",
     "fila com trabalho e zero progresso reporta ACTIVE_PRODUCTIVE",
     "telemetria_do_curador.py", 'return "ACTIVE_NO_OUTPUT"', 'return "ACTIVE_PRODUCTIVE"',
     "test_telemetria.py TestTelemetria.test_fila_com_trabalho_sem_progresso_nao_e_produtivo"),
    ("M8_CHECKPOINT_SPAM_DIVERGENTE",
     "checkpoint escreve sempre (fonte divergente/spam, ignora a assinatura)",
     "telemetria_do_curador.py",
     "if not forcar and ultimo is not None and ultimo.get(\"ASSINATURA\") == assin:",
     "if False:",
     "test_telemetria.py TestTelemetria.test_checkpoint_sem_mudanca_nao_faz_spam"),
]


def _limpar_cache():
    for pc in RAIZ.rglob("__pycache__"):
        shutil.rmtree(pc, ignore_errors=True)


def _correr(teste: str) -> int:
    fich, alvo = teste.split()[0], teste.split()[1]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
    r = subprocess.run([sys.executable, str(CUR / fich), alvo],
                       capture_output=True, text=True, cwd=str(RAIZ), env=env)
    return r.returncode


def main() -> int:
    resultados = []
    _limpar_cache()
    for mid, desc, fich, velho, novo, teste in MUTANTES:
        alvo = CUR / fich
        original = alvo.read_text(encoding="utf-8")
        no_fonte = velho in original

        # BASELINE: o assassino tem de PASSAR no codigo limpo.
        _limpar_cache()
        baseline_ok = _correr(teste) == 0

        killed = None
        mutou = False
        if no_fonte:
            alvo.write_text(original.replace(velho, novo), encoding="utf-8")
            mutou = velho not in alvo.read_text(encoding="utf-8") or novo in alvo.read_text(encoding="utf-8")
            _limpar_cache()
            killed = _correr(teste) != 0     # reprovou => mutante morto
            alvo.write_text(original, encoding="utf-8")   # restaurar
            _limpar_cache()

        resultados.append({
            "MUTANTE": mid, "DESCRICAO": desc, "TESTE_ASSASSINO": teste,
            "MUTANT_IN_SOURCE": "YES" if no_fonte else "NO",
            "MUTATION_APPLIED": "YES" if mutou else "NO",
            "BASELINE_PASSED": "YES" if baseline_ok else "NO",
            "MUTANT_KILLED": ("YES" if killed else "NO") if no_fonte else "N/A",
        })
        print("%-32s baseline=%-3s applied=%-3s killed=%s"
              % (mid, "YES" if baseline_ok else "NO", "YES" if mutou else "NO",
                 ("YES" if killed else "NO") if no_fonte else "N/A"), flush=True)

    survivors = [r for r in resultados if r["MUTANT_KILLED"] == "NO"
                 or r["MUTANT_IN_SOURCE"] == "NO" or r["BASELINE_PASSED"] == "NO"]
    saida = {"GERADO_EM": __import__("datetime").datetime.now(
                 __import__("datetime").timezone.utc).isoformat(),
             "TOTAL": len(resultados), "SURVIVORS": len(survivors),
             "RESULTADOS": resultados}
    (CUR / "RED-TEAM-TELEMETRIA-V1.json").write_text(
        json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nSURVIVORS = %d / %d" % (len(survivors), len(resultados)))
    return 0 if not survivors else 1


if __name__ == "__main__":
    raise SystemExit(main())
