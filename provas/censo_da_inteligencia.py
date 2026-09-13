#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CENSO DA INTELLIGENCE — a populacao vem do mapa, a prova vem da arvore.

    ARVORE=/tmp/wtf python3 provas/censo_da_inteligencia.py

O QUE ESTE INSTRUMENTO FAZ
--------------------------
1. Descobre COMO o System Map classifica a familia INTELIGENCIA
   (componente -> territorio -> familia) e extrai a populacao EXATA.
2. Mede cada peca contra a arvore: ficheiros, simbolos, quem lhe toca.
3. Separa, e nunca mistura:

       DECLARED            o mapa diz
       STATIC_OBSERVED     ha uma linha de codigo que refere
       RUNTIME_OBSERVED    correu, e ha saida

O QUE ELE NAO FAZ
-----------------
Nao transforma import em fluxo. Nao transforma mencao em chamada. Nao
transforma documentacao em aresta. Nao conta o proprio System Map como
prova da maquina que ele descreve.

    O MAPA E OBSERVADOR DA MAQUINA. ELE NAO E A MAQUINA.
"""
import ast
import io
import json
import os
import re
import subprocess
import sys

ARVORE = os.environ.get("ARVORE") or os.getcwd()
SAIDA = os.environ.get("SAIDA") or "/tmp/censo-int"

IGNORAR_DIR = (".git", "node_modules", "BASELINE", "__pycache__", ".venv",
               "dist", "build")


def caminho(*p):
    return os.path.join(ARVORE, *p)


def ler(rel):
    try:
        return io.open(caminho(rel), encoding="utf-8", errors="ignore").read()
    except Exception:
        return ""


def ficheiros_da_arvore():
    """Todo ficheiro de texto da arvore, uma vez so. O censo le muito."""
    out = {}
    for base, dirs, fs in os.walk(ARVORE):
        dirs[:] = [d for d in dirs if d not in IGNORAR_DIR]
        for f in fs:
            cam = os.path.join(base, f)
            rel = os.path.relpath(cam, ARVORE)
            if os.path.getsize(cam) > 4_000_000:
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext in (".png", ".jpg", ".jpeg", ".pdf", ".woff", ".woff2",
                       ".ttf", ".ico", ".gz", ".zip", ".webp", ".mp4"):
                continue
            try:
                out[rel] = io.open(cam, encoding="utf-8",
                                   errors="ignore").read()
            except Exception:
                pass
    return out


def classe_do_referente(rel):
    """QUEM refere importa tanto como QUE refere.

    Um teste a nomear uma peca nao prova que a maquina a usa: prova que
    alguem a mede. Um documento a nomea-la prova menos ainda.
    """
    if rel.startswith("tests/"):
        return "TEST"
    if rel.startswith("provas/"):
        return "PROVA"
    # ⚠️ `italia-portale/client/system-map/` E COPIA DO MAPA, e nao Portal.
    # O build copia-a para a Vercel poder servir. Conta-la como uso do Portal
    # faria o mapa provar a maquina que ele apenas descreve — o ATAQUE 4 do
    # red team desta missao, cometido pelo proprio medidor.
    #
    #     O MAPA A FALAR DE UMA PECA NAO E A MAQUINA A USA-LA.
    if rel.startswith("system-map/") or "client/system-map/" in rel:
        return "SYSTEM_MAP"
    if rel.startswith(".github/"):
        return "WORKFLOW"
    if rel.startswith("docs/") or rel.endswith(".md"):
        return "DOC"
    if rel.startswith("italia-portale/"):
        return "PORTAL"
    return "RUNTIME"


def simbolos(rel):
    """Os nomes de topo que um ficheiro Python define. Vazio nao e erro."""
    if not rel.endswith(".py"):
        return []
    try:
        arv = ast.parse(ler(rel))
    except Exception:
        return []
    return sorted({n.name for n in arv.body
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef,
                                     ast.ClassDef))})


def main():
    S = json.load(io.open(caminho("system-map/data/state.generated.json"),
                          encoding="utf-8"))
    D = json.load(io.open(caminho("system-map/data/architecture.declared.json"),
                          encoding="utf-8"))

    # ── 1 · COMO O MAPA CLASSIFICA ───────────────────────────────────────
    fam_do_terr = {t["id"]: t.get("family") for t in D["TERRITORIES"]}
    terr_int = sorted(t for t, f in fam_do_terr.items()
                      if f == "F-INTELIGENCIA")
    universo = [n for n in S["NODES"] if n.get("family") == "F-INTELIGENCIA"]
    universo.sort(key=lambda n: n["id"])

    print("=" * 78)
    print("CENSO DA INTELLIGENCE · arvore %s" % ARVORE)
    print("=" * 78)
    print("  MECANISMO       componente.territory -> territory.family")
    print("  TERRITORIOS     %s" % ", ".join(terr_int))
    print("  PECAS NO MAPA   %d de %d" % (len(universo), len(S["NODES"])))
    print()

    arquivos = ficheiros_da_arvore()
    print("  ficheiros lidos da arvore: %d" % len(arquivos))

    # arestas por peca
    ent, sai = {}, {}
    for e in S["EDGES"]:
        sai.setdefault(e["from"], []).append(e)
        ent.setdefault(e["to"], []).append(e)

    nome_do_no = {n["id"]: n["name"] for n in S["NODES"]}
    decl = {c["id"]: c for c in D["COMPONENTS"]}

    censo = []
    for n in universo:
        pid = n["id"]
        fs = n.get("files") or []

        # ── EXISTENCIA ───────────────────────────────────────────────────
        existe = {f: os.path.exists(caminho(f)) for f in fs}
        syms = {f: simbolos(f) for f in fs if f.endswith(".py")}

        # ── QUEM REFERE (STATIC_OBSERVED) ────────────────────────────────
        refs = {}
        for f in fs:
            base = os.path.basename(f)
            modulo = os.path.splitext(base)[0]
            padrao_imp = re.compile(
                r"^\s*(?:from\s+%s\s+import|import\s+%s)\b" % (
                    re.escape(modulo), re.escape(modulo)), re.M)
            for rel, texto in arquivos.items():
                if rel in fs:
                    continue                      # a peca nao se refere a si
                como = None
                if f in texto:
                    como = "PATH"
                if f.endswith(".py") and padrao_imp.search(texto):
                    como = "IMPORT"
                if como:
                    refs.setdefault(classe_do_referente(rel), []).append(
                        "%s(%s)" % (rel, como))

        runtime_refs = refs.get("RUNTIME", []) + refs.get("WORKFLOW", [])
        so_teste = (not runtime_refs) and bool(
            refs.get("TEST") or refs.get("PROVA"))
        so_doc = (not runtime_refs) and (not refs.get("TEST")) and \
                 (not refs.get("PROVA")) and bool(refs.get("DOC"))
        so_mapa = list(refs.keys()) in ([], ["SYSTEM_MAP"])

        # ── ARESTAS: DECLARADA vs OBSERVADA ──────────────────────────────
        def resume(es):
            o = []
            for e in es:
                outro = e["to"] if e in sai.get(pid, []) else e["from"]
                o.append({
                    "outro": outro,
                    "nome": nome_do_no.get(outro, "?"),
                    "kind": e.get("kind"),
                    "status": e.get("status"),
                    "evidence": e.get("evidence"),
                })
            return o

        a_ent, a_sai = resume(ent.get(pid, [])), resume(sai.get(pid, []))
        obs_in = [x for x in a_ent if x["kind"] != "expected"]
        obs_out = [x for x in a_sai if x["kind"] != "expected"]

        # ── ESTADO ───────────────────────────────────────────────────────
        # ⚠️ NENHUM ESTADO AQUI DIZ «RUNTIME PROVADO». Este instrumento e
        # estatico, e um instrumento estatico que afirmasse runtime estaria
        # a inventar. RUNTIME so entra por execucao medida, noutra seccao.
        if not fs:
            estado = "SEM_FICHEIRO_DECLARADO"
        elif not all(existe.values()):
            estado = "BROKEN_FICHEIRO_AUSENTE"
        elif so_mapa:
            estado = "ORPHAN_SO_O_MAPA_A_CONHECE"
        elif so_doc:
            estado = "ORPHAN_SO_DOCUMENTO_REFERE"
        elif so_teste:
            estado = "ONLY_TEST_CALLER"
        elif runtime_refs:
            estado = "CONNECTED_STATIC_NOT_RUNTIME_PROVEN"
        else:
            estado = "UNKNOWN"

        censo.append({
            "MAP_NODE_ID": pid,
            "NOME": n["name"],
            "KIND": n.get("kind"),
            "TERRITORY": n.get("territory"),
            "FAMILY": n.get("family"),
            "LANE": n.get("lane"),
            "LEGACY": n.get("legacy"),
            "VIEWS": n.get("views"),
            "MAP_STATUS": n.get("status"),
            "MAP_STATUS_REASON": (n.get("status_reason") or "")[:200],
            "WHAT": (n.get("what") or "")[:300],
            "WHY_HERE": (n.get("why_here") or "")[:300],
            "FILES": fs,
            "FILE_EXISTS": existe,
            "SYMBOLS": syms,
            "DECLARED_INBOUND": [x["outro"] for x in a_ent],
            "DECLARED_OUTBOUND": [x["outro"] for x in a_sai],
            "OBSERVED_INBOUND": [x["outro"] for x in obs_in],
            "OBSERVED_OUTBOUND": [x["outro"] for x in obs_out],
            "EDGES_IN": a_ent,
            "EDGES_OUT": a_sai,
            "REFS_POR_CLASSE": {k: sorted(v)[:14] for k, v in refs.items()},
            "REFS_CONTAGEM": {k: len(v) for k, v in refs.items()},
            "RUNTIME_REFS": sorted(runtime_refs)[:14],
            "TEM_TESTE": bool(refs.get("TEST")),
            "TEM_PROVA": bool(refs.get("PROVA")),
            "ESTADO_ESTATICO": estado,
            "RUNTIME_OBSERVED": "NAO_MEDIDO_POR_ESTE_INSTRUMENTO",
            "DECLARACAO_ORIGEM": "architecture.declared.json"
                                 if pid in decl else "GERADA_PELO_SCANNER",
        })

    os.makedirs(SAIDA, exist_ok=True)
    uni = {
        "MEDIDO_EM": subprocess.run(
            ["git", "-C", ARVORE, "rev-parse", "HEAD"],
            capture_output=True, text=True).stdout.strip(),
        "MECANISMO": "componente.territory -> territory.family",
        "TERRITORIOS_DA_FAMILIA": terr_int,
        "TOTAL_DE_PECAS_NO_MAPA": len(S["NODES"]),
        "INTELLIGENCE_MAP_COUNT": len(universo),
        "PECAS": censo,
    }
    with io.open(os.path.join(SAIDA, "INTELLIGENCE-MAP-UNIVERSE.json"),
                 "w", encoding="utf-8") as f:
        json.dump(uni, f, ensure_ascii=False, indent=2)

    # ── RELATORIO DE ECRA ────────────────────────────────────────────────
    print()
    print("  %-22s %-11s %-30s %s" % ("PECA", "KIND", "ESTADO ESTATICO",
                                      "REFS RUNTIME"))
    print("  " + "-" * 74)
    for c in censo:
        print("  %-22s %-11s %-30s %d" % (
            c["MAP_NODE_ID"][:22], (c["KIND"] or "-")[:11],
            c["ESTADO_ESTATICO"][:30], len(c["RUNTIME_REFS"])))
    print()
    from collections import Counter
    for k, v in sorted(Counter(c["ESTADO_ESTATICO"] for c in censo).items()):
        print("  %-34s %d" % (k, v))
    print()
    print("  escrito: %s/INTELLIGENCE-MAP-UNIVERSE.json" % SAIDA)
    print("  INTELLIGENCE_MAP_COUNT = %d" % len(universo))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
