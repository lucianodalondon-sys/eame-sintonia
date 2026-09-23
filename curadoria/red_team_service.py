#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM da missao SOURCE-CURATOR-SERVICE-V1 — SURVIVORS = 0.

Para cada mutante: aplica a mutacao, corre o teste-assassino, confirma que ele
REPROVA (a mutacao morre), reverte, e limpa __pycache__ entre mutacoes.

    UM MUTANTE QUE SOBREVIVE E UM DEFEITO QUE NENHUM TESTE VE.

Corre numa copia descartavel da arvore. Nao toca rede (os testes-assassino sao
todos isolados/injectados).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CUR = RAIZ / "curadoria"

# (id, descricao, ficheiro, velho, novo, teste_assassino)
MUTANTES = [
    ("M1_QUALIFY_PROMOVE_READY",
     "QUALIFY passa a cair no ramo de promocao READY",
     "worker.py", "elif tipo == F.QUALIFY:", "elif tipo == F.QUALIFY and False:",
     "test_worker_qualify.py TestQualify.test_qualify_nunca_promove_ready"),
    ("M2_GUARD_REBLOQUEIA_QUALIFY",
     "o guard 'sem contrato' volta a barrar QUALIFY",
     "worker.py", "SEM_CONTRATO_POR_DESENHO = frozenset({F.BUILD_CONTRACT, F.QUALIFY, F.REPAIR_CONTRACT})",
     "SEM_CONTRATO_POR_DESENHO = frozenset({F.BUILD_CONTRACT, F.REPAIR_CONTRACT})",
     "test_worker_qualify.py TestQualify.test_html_aloca_e_enfileira_build_contract"),
    ("M3_FABRICA_SOURCE_ID",
     "QUALIFY fabrica SOURCE_ID mesmo com territorio NAO SEI",
     "worker.py", 'if territorio == "NAO SEI":', "if False:",
     "test_worker_qualify.py TestQualify.test_territorio_naosei_vira_semantic_sem_fabricar"),
    ("M4_PAINEL_CONFIA_NO_JSON",
     "liveness do supervisor confia no ficheiro em vez do SO",
     "supervisor.py", "sup_vivo = bool(sup_pid and _pid_no_so(sup_pid))",
     "sup_vivo = bool(sup_pid)",
     "test_status_liveness.py TestLiveness.test_pid_morto_com_json_running_nao_e_running"),
    ("M5_IGNORA_HEARTBEAT_STALE",
     "worker com PID vivo mas heartbeat velho conta como vivo",
     "supervisor.py", "worker_alive = worker_pid_no_so and not hb_stale",
     "worker_alive = worker_pid_no_so",
     "test_status_liveness.py TestLiveness.test_heartbeat_velho_e_stale_com_delta_a_vista"),
    ("M6_HOOK_LOW_WATERMARK_MORTO",
     "o gatilho nunca realimenta (fila vazia = paragem de facto)",
     "gatilho_discovery.py", 'if m["QUEUE_ELIGIBLE"] > QUEUE_LOW_WATERMARK:',
     "if True:",
     "test_gatilho_discovery.py TestGatilho.test_fila_e_acervo_baixos_aciona_discovery"),
    ("M7_DISCOVERY_SEM_INTERVALO",
     "discovery crawla em rajada, ignorando o intervalo",
     "gatilho_discovery.py", "if faltam > 0:", "if False:",
     "test_gatilho_discovery.py TestGatilho.test_discovery_respeita_intervalo"),
    ("M8_DESBLOQUEIA_TUDO",
     "o desbloqueio deixa de filtrar por assinatura (apanha policy)",
     "fila.py", "if any(a in err for a in assinaturas):", "if True:",
     "test_worker_qualify.py TestDesbloqueio.test_desbloqueia_qualify_mas_nao_canary_nem_policy"),
    ("M9_NAO_RELANCA_WORKER",
     "o supervisor fica IDLE mesmo havendo trabalho (nao recupera worker)",
     "supervisor.py", "if n_elegiveis == 0:", "if True:",
     "test_supervisor.py TestUmaVoltaSup.test_relanca_com_trabalho"),
    ("M10_IDLE_VIRA_STOPPED",
     "servico com worker ocioso passa a reportar-se parado",
     "supervisor.py", 'supervisor_state = "STOPPING" if parar else "RUNNING"',
     'supervisor_state = "STOPPED"',
     "test_status_liveness.py TestLiveness.test_idle_nao_se_chama_stopped"),
]


def _limpar_pycache():
    pc = CUR / "__pycache__"
    if pc.exists():
        shutil.rmtree(pc, ignore_errors=True)


def _correr(teste: str) -> int:
    partes = teste.split()
    ficheiro, alvo = partes[0], (partes[1] if len(partes) > 1 else "")
    cmd = [sys.executable, str(CUR / ficheiro)]
    if alvo:
        cmd.append(alvo)
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(RAIZ))
    return r.returncode


def main() -> int:
    resultados = []
    _limpar_pycache()
    for mid, desc, ficheiro, velho, novo, teste in MUTANTES:
        alvo = CUR / ficheiro
        original = alvo.read_text(encoding="utf-8")
        aplicado = velho in original
        killed = None
        if aplicado:
            alvo.write_text(original.replace(velho, novo, 1), encoding="utf-8")
            _limpar_pycache()
            rc = _correr(teste)
            killed = rc != 0            # teste reprovou => mutante morto
            alvo.write_text(original, encoding="utf-8")   # reverter
            _limpar_pycache()
        resultados.append({
            "MUTANTE": mid, "DESCRICAO": desc,
            "MUTANT_APPLIED": "YES" if aplicado else "NO",
            "MUTANT_KILLED": ("YES" if killed else "NO") if aplicado else "N/A",
            "TESTE_ASSASSINO": teste,
        })
        print("%-28s applied=%-3s killed=%s"
              % (mid, "YES" if aplicado else "NO",
                 ("YES" if killed else "NO") if aplicado else "N/A"), flush=True)

    survivors = [r for r in resultados
                 if r["MUTANT_APPLIED"] == "YES" and r["MUTANT_KILLED"] == "NO"]
    nao_aplicados = [r for r in resultados if r["MUTANT_APPLIED"] == "NO"]
    saida = {
        "GERADO_EM": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(),
        "TOTAL": len(resultados),
        "SURVIVORS": len(survivors),
        "NAO_APLICADOS": [r["MUTANTE"] for r in nao_aplicados],
        "RESULTADOS": resultados,
    }
    (CUR / "RED-TEAM-SERVICE-V1.json").write_text(
        json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nSURVIVORS = %d / %d aplicados"
          % (len(survivors), sum(1 for r in resultados if r["MUTANT_APPLIED"] == "YES")))
    if nao_aplicados:
        print("NAO_APLICADOS (assinatura nao encontrada):",
              [r["MUTANTE"] for r in nao_aplicados])
    return 0 if not survivors and not nao_aplicados else 1


if __name__ == "__main__":
    raise SystemExit(main())
