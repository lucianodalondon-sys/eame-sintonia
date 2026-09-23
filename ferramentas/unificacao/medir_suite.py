"""Mede a suite de um commit POR NOME, numa worktree descartavel (missao 5).

    py ferramentas/unificacao/medir_suite.py <ref> <saida.json>

- `git worktree add --detach` em %TEMP%; nunca corre na worktree de trabalho
  (a suite de tests/ apaga XX/, a de curadoria/ lanca worker real que le a fila).
- a fila da curadoria fica VAZIA antes de correr (sem tarefas, sem rede).
- corre as duas suites em sequencia (nunca duas medicoes ao mesmo tempo):
  curadoria/ e tests/ (esta com PYTHONPATH=.sintonia-libs, para o PyYAML).
- grava, por nome completo `modulo.Classe.teste`, ok / FAIL / ERROR / skipped,
  e as linhas `FAIL:` / `ERROR:` inteiras (incluem setUpClass e modulos que
  nao carregam, que nao tem linha `... ok`).
- remove a worktree no fim.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

LIBS = Path.home() / ".sintonia-libs"
RE_TESTE = re.compile(r"^(test\w+) \(([\w.]+)\)(?:\s*\n?.*?)? \.\.\. (ok|FAIL|ERROR|skipped.*|expected failure|unexpected success)$",
                      re.M)
RE_LINHA = re.compile(r"^(FAIL|ERROR): (.+)$", re.M)


def git(cwd, *a, ok=(0,)):
    p = subprocess.run(["git", *a], cwd=str(cwd), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if p.returncode not in ok:
        raise SystemExit("git %s: %s%s" % (a, p.stdout[-800:], p.stderr[-800:]))
    return p


def correr(wt: Path, pasta: str, extra_env: dict) -> dict:
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
               PYTHONDONTWRITEBYTECODE="1", **extra_env)
    t0 = time.time()
    p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", pasta,
                        "-p", "test_*.py", "-v"], cwd=str(wt), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env, timeout=5400)
    res = {}
    for m in RE_TESTE.finditer(p.stderr):
        res["%s.%s" % (m.group(2), m.group(1))] = m.group(3).split()[0]
    vermelhas = sorted(set(m.group(0).strip() for m in RE_LINHA.finditer(p.stderr)))
    return {"RESULTADOS": res, "LINHAS_VERMELHAS": vermelhas,
            "FIM": p.stderr.strip().splitlines()[-3:],
            "OK": sum(1 for v in res.values() if v == "ok"), "TOTAL": len(res),
            "SEGUNDOS": round(time.time() - t0)}


def medir(ref: str) -> dict:
    raiz = Path(git(Path(__file__).parent, "rev-parse", "--show-toplevel").stdout.strip())
    sha = git(raiz, "rev-parse", ref).stdout.strip()
    wt = Path(tempfile.gettempdir()) / ("medir-suite-%s" % sha[:8])
    if wt.exists():
        git(raiz, "worktree", "remove", "--force", str(wt), ok=(0, 128))
        shutil.rmtree(wt, ignore_errors=True)
    git(raiz, "worktree", "add", "-q", "--detach", str(wt), sha)
    try:
        fila = wt / "curadoria" / "LIFECYCLE-QUEUE-V1.json"
        if fila.exists():
            fila.write_text(json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}), encoding="utf-8")
        doc = {"REF": ref, "SHA": sha,
               "curadoria": correr(wt, "curadoria", {}),
               "tests": correr(wt, "tests", {"PYTHONPATH": str(LIBS)})}
    finally:
        git(raiz, "worktree", "remove", "--force", str(wt), ok=(0, 128))
        git(raiz, "worktree", "prune")
    doc["WORKTREE_REMOVIDA"] = not wt.exists()
    return doc


if __name__ == "__main__":
    d = medir(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
    for k in ("curadoria", "tests"):
        print(k, d[k]["OK"], "/", d[k]["TOTAL"], "vermelhas:", len(d[k]["LINHAS_VERMELHAS"]),
              "s:", d[k]["SEGUNDOS"])
