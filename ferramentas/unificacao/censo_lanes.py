"""Censo SO LEITURA das lanes candidatas a unificacao (missao 5-prep).

Nao escreve no repositorio: so `git rev-parse`, `merge-base`, `rev-list`,
`diff --name-only`, `ls-tree`, `cat-file` e `merge-file -p` sobre ficheiros
temporarios fora do repo. Nao escreve objectos, refs nem indice.

Uso:  PYTHONUTF8=1 py ferramentas/unificacao/censo_lanes.py > saida.json
"""
import itertools
import json
import os
import re
import subprocess
import sys
import tempfile

LANES = {
    # nome curto -> ref
    "ponte": "ponte-curador-v1",
    "servico": "source-curator-service-v1",   # == abastecimento-bot-v1 (779ac8f6)
    "rotas": "rotas-elegiveis-v1",
    "diagnostico": "diagnostico-sala-v1",
    "lote76": "lote-76-v1",
    "producao": "origin/ops/italy-forward-only-live",
}
# ordem de integracao proposta (a base e a primeira)
ORDEM = ["ponte", "servico", "diagnostico", "rotas", "lote76"]


def git(*a, ok=(0,)):
    p = subprocess.run(["git", *a], capture_output=True)
    if p.returncode not in ok:
        raise SystemExit(f"git {a} -> {p.returncode}: {p.stderr.decode(errors='replace')}")
    return p.stdout


def s(*a):
    return git(*a).decode("utf-8", errors="replace").strip()


def blob(ref, path):
    out = git("ls-tree", ref, "--", path).decode("utf-8", errors="replace").strip()
    return out.split()[2] if out else None


def tipo(path):
    p = path.replace("\\", "/")
    if ".generated." in p or p.startswith("system-map/") and p.endswith((".json", ".md", ".html", ".mmd")):
        return "gerado"
    if p.endswith((".py", ".mjs", ".js", ".ts", ".sql", ".yml", ".yaml", ".ps1", ".sh")):
        return "codigo"
    if "KNOW-HOW" in p or p.startswith("know-how/"):
        return "know-how"
    if re.search(r"(LEDGER|QUEUE|EVIDENCE|TELEMETRIA|LIVRO|contracts?_?.*\.json$|\.jsonl$)", p, re.I):
        return "livro"
    if p.endswith(".json"):
        return "livro"
    return "doc"


def conflitos_tres_vias(base, a, b, path):
    """merge-file -p em temporarios; devolve lista de (linha, tamanho) dos conflitos."""
    tmp = tempfile.mkdtemp(prefix="censo-")
    fs = []
    for nome, ref in (("a", a), ("o", base), ("b", b)):
        f = os.path.join(tmp, nome)
        bl = blob(ref, path)
        with open(f, "wb") as h:
            h.write(git("cat-file", "blob", bl) if bl else b"")
        fs.append(f)
    p = subprocess.run(["git", "merge-file", "-p", *fs], capture_output=True)
    linhas = p.stdout.decode("utf-8", errors="replace").splitlines()
    res = [i + 1 for i, l in enumerate(linhas) if l.startswith("<<<<<<<")]
    return res


def main():
    heads = {k: s("rev-parse", "--short", v) for k, v in LANES.items()}
    pares = {}
    for x, y in itertools.combinations(LANES, 2):
        mb = s("merge-base", LANES[x], LANES[y])
        cx = int(s("rev-list", "--count", f"{LANES[y]}..{LANES[x]}"))
        cy = int(s("rev-list", "--count", f"{LANES[x]}..{LANES[y]}"))
        pares[f"{x}|{y}"] = {"merge_base": mb[:8], f"so_{x}": cx, f"so_{y}": cy}

    lanes_u = ORDEM
    base_todas = s("merge-base", "--octopus", *[LANES[k] for k in lanes_u])
    tocados = {}
    for k in lanes_u:
        for f in s("diff", "--name-only", "--no-renames", base_todas, LANES[k]).splitlines():
            if f:
                tocados.setdefault(f, []).append(k)
    multi = {f: ls for f, ls in tocados.items() if len(ls) > 1}
    censo = {}
    for f, ls in sorted(multi.items()):
        bls = {k: blob(LANES[k], f) for k in ls}
        vivos = {k: v for k, v in bls.items() if v}
        if len(vivos) < len(bls) and len(set(vivos.values())) <= 1:
            estado = "ONE_SIDE"
        elif len(set(bls.values())) == 1:
            estado = "IDENTICAL"
        else:
            estado = "DIVERGENT"
        e = {"lanes": ls, "estado": estado, "tipo": tipo(f),
             "blobs": {k: (v[:8] if v else None) for k, v in bls.items()}}
        if estado == "DIVERGENT" and e["tipo"] == "codigo":
            # tres vias par a par contra a primeira lane da ordem que o toca
            reais = {}
            a = ls[0]
            for b in ls[1:]:
                if bls[a] == bls[b]:
                    continue
                mb = s("merge-base", LANES[a], LANES[b])
                c = conflitos_tres_vias(mb, LANES[a], LANES[b], f)
                if c:
                    reais[f"{a}<-{b}"] = c
            e["conflitos_linhas"] = reais
        censo[f] = e

    # contra a BASE proposta (ponte): o que cada lane muda desde o seu merge-base
    # com a ponte, e que a ponte TAMBEM mudou desde esse ponto = conflito possivel
    contra_base = {}
    for k in ORDEM[1:]:
        mb = s("merge-base", LANES["ponte"], LANES[k])
        dx = set(s("diff", "--name-only", "--no-renames", mb, LANES[k]).splitlines())
        dp = set(s("diff", "--name-only", "--no-renames", mb, LANES["ponte"]).splitlines())
        ambos = sorted(f for f in dx & dp if f)
        linhas = {}
        for f in ambos:
            bp, bx = blob(LANES["ponte"], f), blob(LANES[k], f)
            if bp == bx:
                linhas[f] = {"tipo": tipo(f), "estado": "IDENTICAL"}
            elif not bp or not bx:
                linhas[f] = {"tipo": tipo(f), "estado": "ONE_SIDE"}
            else:
                e = {"tipo": tipo(f), "estado": "DIVERGENT"}
                if e["tipo"] == "codigo":
                    e["conflitos_linhas"] = conflitos_tres_vias(mb, LANES["ponte"], LANES[k], f)
                linhas[f] = e
        contra_base[k] = {"merge_base": mb[:8], "so_na_lane": len(dx - dp),
                          "tocados_nos_dois": len(ambos), "ficheiros": linhas}

    # know-how: seccoes '# §N' por lane e numeros com titulos diferentes
    sec = {}
    for k in ORDEM:
        txt = git("show", f"{LANES[k]}:SINTONIA-EAME-KNOW-HOW.md").decode("utf-8", errors="replace")
        for m in re.finditer(r"^# §(\d+)\s*·?\s*(.*)$", txt, re.M):
            sec.setdefault(int(m.group(1)), {}).setdefault(m.group(2).strip()[:70], []).append(k)
    colisoes = {n: v for n, v in sec.items() if len(v) > 1}
    so_numa = {n: next(iter(v.values())) for n, v in sec.items()
               if len(v) == 1 and len(next(iter(v.values()))) < len(ORDEM)}

    resumo = {"FILES_MULTI_LANE": len(censo)}
    for est in ("IDENTICAL", "ONE_SIDE", "DIVERGENT"):
        resumo[est] = sum(1 for e in censo.values() if e["estado"] == est)
    por_tipo = {}
    for e in censo.values():
        if e["estado"] == "DIVERGENT":
            por_tipo[e["tipo"]] = por_tipo.get(e["tipo"], 0) + 1
    resumo["DIVERGENT_POR_TIPO"] = por_tipo
    resumo["REAL_CODE_CONFLICTS"] = sorted(
        f for f, e in censo.items() if e.get("conflitos_linhas"))
    json.dump({"know_how": {"colisoes": colisoes, "seccoes_nao_universais": so_numa},
               "contra_base": contra_base, "heads": heads, "base_todas": base_todas[:8], "pares": pares,
               "resumo": resumo, "censo": censo}, sys.stdout, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
