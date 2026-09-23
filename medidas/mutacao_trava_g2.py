#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G2 — os sobreviventes da auditoria 08 (08-RED-TEAM-DAS-PROVAS.md, 21/09) atacados de novo.

    4b  CRASH_MAX = 99999                          (o travao de crashloop nunca dispara)
    4c  a morte sem progresso nao e registada       (o travao nao conta nada)
    5c  _proc_e_python desligado                    (PID reciclado por nao-Python = lock valido)
    5d  _pid_no_so desligado                        (PID morto = lock valido)

Cada mutante e aplicado sozinho em curadoria/supervisor.py, corre a suite do dono
(curadoria/test_supervisor.py + test_fila_windows.py) sem bytecode, e o ficheiro e
RESTAURADO byte a byte no `finally`. MORTO = a suite reprova. Sem rede.
"""
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ALVO = RAIZ / "curadoria" / "supervisor.py"
MUTANTES = [
    ("4b CRASH_MAX=99999", "CRASH_MAX      = 3", "CRASH_MAX      = 99999"),
    ("4c morte sem progresso nao registada",
     'estado.setdefault("CRASHES_SEM_PROGRESSO", []).append({', '(lambda _x: None)({'),
    ("5c _proc_e_python desligado", "python = _proc_e_python(pid)", "python = True"),
    ("5d _pid_no_so desligado", "existe = _pid_no_so(pid)", "existe = True"),
]


def correr() -> tuple[bool, str]:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_supervisor", "test_fila_windows"],
                       cwd=RAIZ / "curadoria", env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=900)
    fim = [l for l in r.stderr.splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]
    return r.returncode == 0, " ".join(fim)


def main() -> int:
    ok, resumo = correr()
    print("BASE", "VERDE" if ok else "VERMELHA", resumo, flush=True)
    if not ok:
        return 2
    mortos = 0
    for nome, de, para in MUTANTES:
        orig = ALVO.read_bytes()
        t = orig.decode("utf-8")
        if t.count(de) != 1:
            print("ANCORA NAO CASA (%d): %s" % (t.count(de), nome))
            continue
        try:
            ALVO.write_bytes(t.replace(de, para).encode("utf-8"))
            verde, resumo = correr()
        finally:
            ALVO.write_bytes(orig)
        mortos += not verde
        print("%-9s %s | %s" % ("MORTO" if not verde else "SOBREVIVE", nome, resumo), flush=True)
    print("MUTATION %d/%d" % (mortos, len(MUTANTES)))
    return 0 if mortos == len(MUTANTES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
