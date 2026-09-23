"""L1 — a regua multilingue re-medida OFFLINE: antes (regua do commit base) x depois (arvore).

    py tests/medir_multilingue.py <juncao.tsv> <raiz dos derivados> [--base=<ref>]

Nao e uma prova do unittest (nao comeca por test_): e o instrumento que produz a
tabela de mudancas do relatorio. Sem rede, sem Sala, sem banco, sem escrever.
A regua ANTES e a de `<ref>:admissao/admissao.py` (git show), executada em memoria;
a DEPOIS e a da arvore. Para cada documento: a lingua, e o veredito das duas reguas
para T10 (a pergunta com que o lote-76 foi escrito) e para o universo da fonte.
"""
import json
import subprocess
import sys
import types
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
import admissao as DEPOIS  # noqa: E402


def regua_antes(ref: str):
    src = subprocess.run(["git", "show", f"{ref}:admissao/admissao.py"], cwd=RAIZ,
                         capture_output=True).stdout.decode("utf-8")
    m = types.ModuleType("admissao_antes")
    m.__file__ = str(RAIZ / "admissao" / "admissao.py")
    sys.modules["admissao_antes"] = m
    exec(compile(src, m.__file__, "exec"), m.__dict__)
    return m


def julgar(A, texto, u):
    r, motivo, ev = A._do_universo({"texto": texto}, u, A.PERGUNTAS_DO_UNIVERSO.get(u, []))
    return r, motivo


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    tsv, raiz = Path(argv[0]), Path(argv[1])
    ref = next((a.split("=", 1)[1] for a in argv if a.startswith("--base=")), "HEAD")
    ANTES = regua_antes(ref)
    linhas = []
    for l in tsv.read_text(encoding="utf-8").splitlines():
        did, rid, sid, sha, dp, url, rp = l.split("\t")
        texto = (raiz / dp).read_text(encoding="utf-8")
        lg = DEPOIS._lingua_do_item({"texto": texto})
        for u in sorted({"T10", sid.split("-")[1]}):
            a, _ = julgar(ANTES, texto, u)
            d, motivo = julgar(DEPOIS, texto, u)
            linhas.append({"DERIVED": int(did), "SOURCE_ID": sid, "LINGUA": lg, "UNIVERSO": u,
                           "ANTES": a, "DEPOIS": d, "MUDOU": a != d, "MOTIVO_DEPOIS": motivo[:160]})
    print(json.dumps(linhas, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
