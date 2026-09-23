"""ENSAIO da unificacao num clone TEMPORARIO (missao 5-PREP-b). Nada se publica.

    git worktree add --detach <TEMP>/ensaio-<x> <base>
    junta pela ordem do plano (diagnostico -> rotas -> servico), resolve,
    corre a suite de curadoria/ com a fila VAZIA (a suite lanca worker real
    que bate a rede se houver tarefas), mede por nome, e remove a worktree.

Resolucao usada no ENSAIO (nao e a da missao 5):
  - codigo: ferramentas/unificacao/resolver_conflitos.py
  - livros, gerados, docs, know-how: fica o lado da base. Os livros reconciliam-se
    na missao 5 por SOURCE_ID (reconciliar_livros.py --livro-servico); os gerados
    regeram-se; aqui so interessa se o CODIGO junto passa nos testes.

Uso:  py ferramentas/unificacao/ensaio_unificacao.py <pasta-de-saida>
Escreve <saida>/testes-base.json e <saida>/testes-unificado.json.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BASE = "2018ed6a"
ORDEM = [("diagnostico", "diagnostico-sala-v1"), ("rotas", "rotas-elegiveis-v1"),
         ("servico", "source-curator-service-v1")]
RE_TESTE = re.compile(r"^(test\w+) \(([\w.]+)\)(?:\s*\n?.*?)? \.\.\. (ok|FAIL|ERROR|skipped.*|expected failure|unexpected success)$",
                      re.M)


def git(cwd, *a, ok=(0,)):
    p = subprocess.run(["git", *a], cwd=str(cwd), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if p.returncode not in ok:
        raise SystemExit("git %s (%s): %s%s" % (a, cwd, p.stdout[-800:], p.stderr[-800:]))
    return p


def juntar(wt: Path, nome: str, ref: str) -> dict:
    head = git(wt, "rev-parse", "--short", ref).stdout.strip()
    p = git(wt, "merge", "--no-ff", "--no-commit", ref, ok=(0, 1))
    conflitos = [l for l in git(wt, "diff", "--name-only", "--diff-filter=U").stdout.splitlines() if l]
    codigo = []
    if nome == "servico":
        sys.path.insert(0, str(AQUI))
        import resolver_conflitos as RC
        rel = RC.resolver(wt)
        codigo = [f for f in rel if f != "REMENDOS"]
    resolvidos = {"codigo_resolver": [], "lado_da_base": []}
    for f in conflitos:
        if f in codigo:
            git(wt, "add", "--", f)
            resolvidos["codigo_resolver"].append(f)
        else:
            if git(wt, "checkout", "--ours", "--", f, ok=(0, 1)).returncode != 0:
                git(wt, "rm", "-q", "--", f)
            else:
                git(wt, "add", "--", f)
            resolvidos["lado_da_base"].append(f)
    for f in codigo:                      # os que o git juntou limpo tambem levam a resolucao
        git(wt, "add", "--", f)
    ext = [f for f in conflitos if f.endswith((".py", ".mjs", ".js")) and f not in codigo]
    git(wt, "-c", "user.name=ensaio", "-c", "user.email=ensaio@local",
        "commit", "-q", "--no-verify", "-m", "ENSAIO: junta %s" % nome)
    return {"lane": nome, "ref": head, "conflitos_git": len(conflitos),
            "codigo_nao_previsto": ext, **{k: len(v) for k, v in resolvidos.items()},
            "remendos": rel["REMENDOS"] if codigo else []}


def suite(wt: Path) -> dict:
    fila = wt / "curadoria" / "LIFECYCLE-QUEUE-V1.json"
    fila.write_text(json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}), encoding="utf-8")
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "curadoria",
                        "-p", "test_*.py", "-v"], cwd=str(wt), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env, timeout=3000)
    res = {}
    for m in RE_TESTE.finditer(p.stderr):
        res["%s.%s" % (m.group(2), m.group(1))] = m.group(3).split()[0]
    fim = p.stderr.strip().splitlines()[-3:]
    i = p.stderr.find("\n======")
    detalhe = p.stderr[i:i + 40000] if i >= 0 else ""
    return {"RESULTADOS": res, "FIM": fim, "DETALHE_DAS_FALHAS": detalhe,
            "OK": sum(1 for v in res.values() if v == "ok"), "TOTAL": len(res)}


def ensaio(saida: Path, nome: str, juntar_lanes: bool) -> dict:
    raiz = Path(git(AQUI, "rev-parse", "--show-toplevel").stdout.strip())
    wt = Path(tempfile.gettempdir()) / ("ensaio-unif-%s" % nome)
    if wt.exists():
        shutil.rmtree(wt)
    git(raiz, "worktree", "add", "-q", "--detach", str(wt), BASE)
    try:
        passos = [juntar(wt, n, r) for n, r in ORDEM] if juntar_lanes else []
        s = suite(wt)
        doc = {"BASE": BASE, "PASSOS": passos, **s}
    finally:
        git(raiz, "worktree", "remove", "--force", str(wt), ok=(0, 128))
        git(raiz, "worktree", "prune")
        doc_rem = not wt.exists()
    doc["TEMP_CLONE_REMOVED"] = doc_rem
    (saida / ("testes-%s.json" % nome)).write_text(json.dumps(doc, indent=1, ensure_ascii=False),
                                                     encoding="utf-8")
    return doc


if __name__ == "__main__":
    saida = Path(sys.argv[1])
    saida.mkdir(parents=True, exist_ok=True)
    qual = sys.argv[2] if len(sys.argv) > 2 else "ambos"
    for nome, j in (("base", False), ("unificado", True)):
        if qual in (nome, "ambos"):
            d = ensaio(saida, nome, j)
            print(nome, d["OK"], "/", d["TOTAL"], "removido=%s" % d["TEMP_CLONE_REMOVED"],
                  json.dumps(d.get("PASSOS"), ensure_ascii=False))
