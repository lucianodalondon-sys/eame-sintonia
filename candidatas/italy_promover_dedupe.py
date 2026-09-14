#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEDUPE ANTES DE ID — e a medicao que decide se esta missao pode atribuir numero.

A LEI QUE MANDA AQUI E' DO KNOW-HOW, §119
-----------------------------------------
    ALOCA-SE CONTRA A POPULACAO INTEIRA,
    NUNCA CONTRA O DONO DECLARADO.

O §119 («UM NUMERO QUE JA E' DE ALGUEM») mediu que o registo de identidade
estava PARTIDO EM DOIS: 3 IDs italianos na ficha do atlas — o dono declarado —
e 53 cunhados por `candidatas/ITALY-SOURCE-MASTER-V1.json`, presos a contratos
e a pastas de evidencia. Quem alocasse «o proximo numero» lendo so' o atlas
escolheria um numero ocupado la' fora, e colidiria logo no primeiro.

E o detetor nao existe: `scan_sources.py` indexa por `fora[SOURCE_ID] = ...`,
logo um ID repetido SOBRESCREVE EM SILENCIO. A colisao nao aparece como erro —
aparece como uma fonte que desapareceu.

O QUE ESTA MEDICAO ACRESCENTA
-----------------------------
O registo nao esta partido em dois. Esta partido em TRES, e em TRES BRANCHES
que nao sao antepassadas umas das outras. Por isso este ficheiro conta a
populacao antes de qualquer coisa, e o resultado decide se a missao atribui
numero ou declara BLOCKED_SOURCE_ID_ASSIGNMENT.
"""

import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
TRAB = Path("C:/Users/London1/AppData/Local/Temp/sintonia-promover")
TRAB.mkdir(parents=True, exist_ok=True)

ID = re.compile(r"\b(?:IT|ES|FR|EU|XX|PT|DE)-T\d{1,2}-\d{3}\b")
ATLAS_QUAL = TRAB / "ATLAS-QUALIFICATION.md"


def git(*a):
    return subprocess.run(["git"] + list(a), capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


def chave(url):
    """Chave de comparacao de rota: host + caminho, sem esquema nem www."""
    if not url:
        return ""
    p = urlparse(url if "//" in url else "https://" + url)
    h = (p.netloc or "").lower().removeprefix("www.")
    return (h + p.path.rstrip("/")).lower()


def host(url):
    if not url:
        return ""
    p = urlparse(url if "//" in url else "https://" + url)
    return (p.netloc or "").lower().removeprefix("www.")


# ─────────────────────────────────────────────────────────────────────────────
# 1 · A POPULACAO INTEIRA DE SOURCE_ID
# ─────────────────────────────────────────────────────────────────────────────
def populacao():
    fontes = {}

    meu = (RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md").read_text(
        encoding="utf-8")
    fontes["atlas-desta-branch"] = set(ID.findall(meu))

    mj = RAIZ / "candidatas" / "ITALY-SOURCE-MASTER-V1.json"
    if mj.exists():
        fontes["ITALY-SOURCE-MASTER-V1.json (desta branch)"] = set(
            ID.findall(mj.read_text(encoding="utf-8")))

    if ATLAS_QUAL.exists():
        fontes["atlas de italy-source-qualification-v1"] = set(
            ID.findall(ATLAS_QUAL.read_text(encoding="utf-8")))

    # e o atlas de qualquer outra branch remota, por blob distinto
    refs = [l.strip() for l in git("for-each-ref", "--format=%(refname:short)",
                                   "refs/remotes/origin").splitlines() if l.strip()]
    vistos = set()
    for r in refs:
        s = git("rev-parse", f"{r}:docs/fontes/ATLAS-DE-FONTES-EAME.md").strip()
        if len(s) != 40 or s in vistos:
            continue
        vistos.add(s)
        ids = set(ID.findall(git("cat-file", "-p", s)))
        if len(ids) > 45 and "qualification" not in r:
            fontes[f"atlas de {r.replace('origin/', '')}"] = ids
    return fontes


# ─────────────────────────────────────────────────────────────────────────────
# 2 · AS FICHAS DO ATLAS MAIS AVANCADO, para cruzar com as minhas 23
# ─────────────────────────────────────────────────────────────────────────────
def fichas_do_atlas(texto):
    """Devolve [{SOURCE_ID, SOURCE_NAME, OWNER, URL, TERRITORY, bruto}]."""
    out = []
    partes = re.split(r"\n(?=#### )", texto)
    for p in partes:
        if not p.startswith("#### "):
            continue
        ids = ID.findall(p)
        urls = re.findall(r"https?://[^\s)\]`<>\"']+", p)
        def campo(n):
            m = re.search(rf"^{n}:\s*(.+)$", p, re.M)
            return m.group(1).strip() if m else ""
        out.append({
            "SOURCE_IDS": ids,
            "TITULO": p.splitlines()[0].removeprefix("#### ").strip(),
            "SOURCE_NAME": campo("SOURCE_NAME"),
            "OWNER": campo("SOURCE_OWNER") or campo("OWNER"),
            "URLS": urls,
            "HOSTS": {host(u) for u in urls if host(u)},
            "CHAVES": {chave(u) for u in urls if chave(u)},
            "TERRITORY": campo("TERRITORY"),
        })
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    pop = populacao()

    print("A POPULACAO INTEIRA DE SOURCE_ID — e ela esta partida")
    print("=" * 96)
    todos = set()
    for k, v in sorted(pop.items(), key=lambda x: -len(x[1])):
        it = [x for x in v if x.startswith("IT-")]
        print(f"  {len(v):4d} IDs ({len(it):3d} IT)   {k}")
        todos |= v
    print("-" * 96)
    print(f"  {len(todos):4d} IDs DISTINTOS na uniao "
          f"({len([x for x in todos if x.startswith('IT-')])} italianos)")
    so_no_meu = pop["atlas-desta-branch"]
    print(f"  {len(so_no_meu):4d} deles o atlas DESTA branch conhece "
          f"({100 * len(so_no_meu) // max(len(todos), 1)}%)")
    print(f"  ⚠️ {len(todos - so_no_meu)} IDs estao EM USO e sao INVISIVEIS daqui")

    # ── o proximo livre por territorio, contra a POPULACAO INTEIRA ──
    print()
    print("PROXIMO NUMERO LIVRE POR TERRITORIO — contado contra a uniao")
    print("-" * 96)
    usados = defaultdict(set)
    for x in todos:
        pais, terr, num = x.split("-")
        usados[(pais, terr)].add(int(num))
    prox_meu, prox_uniao = {}, {}
    for t in range(1, 13):
        k = ("IT", f"T{t}")
        u = usados.get(k, set())
        m = {int(x.split("-")[2]) for x in so_no_meu
             if x.startswith(f"IT-T{t}-")}
        n_uniao = max(u) + 1 if u else 1
        n_meu = max(m) + 1 if m else 1
        prox_uniao[k[1]], prox_meu[k[1]] = n_uniao, n_meu
        risco = "⚠️ COLIDIRIA" if n_meu < n_uniao else "ok"
        print(f"  IT-T{t:<2} usados na uniao: {len(u):3d} · "
             f"proximo pela uniao = {n_uniao:3d} · "
             f"proximo pelo meu atlas = {n_meu:3d}   {risco}")

    colidiriam = sum(1 for t in range(1, 13)
                     if prox_meu[f"T{t}"] < prox_uniao[f"T{t}"])
    print("-" * 96)
    print(f"  em {colidiriam} de 12 territorios, alocar pelo MEU atlas daria "
          "um numero JA EM USO")

    # ── cruzar as minhas 23 contra o atlas mais avancado ──
    from openpyxl import load_workbook
    wb = load_workbook(RAIZ / "candidatas" /
                       "ITALY-SOURCE-GAP-CLOSURE-2026-09-14.xlsx",
                       read_only=True, data_only=True)
    r = list(wb["READY_TO_REGISTER"].iter_rows(values_only=True))
    cab = [str(c) for c in r[1]]
    prontas = [dict(zip(cab, x)) for x in r[2:] if any(x)]

    fichas = fichas_do_atlas(ATLAS_QUAL.read_text(encoding="utf-8")) \
        if ATLAS_QUAL.exists() else []
    minhas = fichas_do_atlas((RAIZ / "docs" / "fontes" /
                              "ATLAS-DE-FONTES-EAME.md").read_text(encoding="utf-8"))

    print()
    print(f"AS {len(prontas)} PRONTAS, CRUZADAS CONTRA {len(fichas)} FICHAS DA "
          "BRANCH DE QUALIFICACAO")
    print("=" * 96)
    linhas = []
    for p in prontas:
        u = p["URL_CANONICAL"]
        ck, hk = chave(u), host(u)
        bate_rota = [f for f in fichas if ck and ck in f["CHAVES"]]
        bate_host = [f for f in fichas if hk and hk in f["HOSTS"]]
        bate_meu_rota = [f for f in minhas if ck and ck in f["CHAVES"]]
        bate_meu_host = [f for f in minhas if hk and hk in f["HOSTS"]]

        if bate_rota:
            res, quem = "ALREADY_REGISTERED", bate_rota[0]
        elif bate_meu_rota:
            res, quem = "ALREADY_REGISTERED", bate_meu_rota[0]
        elif bate_host:
            res, quem = "SAME_OWNER_DIFFERENT_SOURCE", bate_host[0]
        elif bate_meu_host:
            res, quem = "SAME_OWNER_DIFFERENT_SOURCE", bate_meu_host[0]
        else:
            res, quem = "NEW_SOURCE", None
        linhas.append({
            "INPUT_SOURCE": p["SOURCE_NAME"], "OWNER": p["OWNER"],
            "URL_CANONICAL": u, "HOST": hk,
            "DEDUPE_RESULT": res,
            "BATE_COM": (", ".join(quem["SOURCE_IDS"]) or quem["TITULO"][:56])
                        if quem else "",
            "BATE_ONDE": ("rota exata" if (bate_rota or bate_meu_rota)
                          else "mesmo host" if quem else ""),
            "GAP_CLOSURE_VALUE": p["GAP_CLOSURE_VALUE"],
            "TOOLS_SUPPORTED": p["TOOLS_SUPPORTED"],
            "RAW_NEEDS_SUPPORTED": p["RAW_NEEDS_SUPPORTED"],
            "TERRITORIES": p["TERRITORIES"],
            "EXAMPLE_REAL": p["EXAMPLE_REAL"],
            "RECORRENCIA_ESTADO": p.get("RECORRENCIA_ESTADO", ""),
            "PRIMARY_OR_SECONDARY": p["PRIMARY_OR_SECONDARY"]})

    for l in sorted(linhas, key=lambda x: x["DEDUPE_RESULT"]):
        print(f"  {l['DEDUPE_RESULT']:28s} {l['INPUT_SOURCE'][:44]:44s} "
              f"{l['BATE_ONDE']:12s} {l['BATE_COM'][:26]}")
    print("-" * 96)
    print("  ", dict(Counter(l["DEDUPE_RESULT"] for l in linhas)))

    json.dump({"POPULACAO": {k: sorted(v) for k, v in pop.items()},
               "UNIAO": sorted(todos),
               "PROXIMO_PELA_UNIAO": prox_uniao,
               "PROXIMO_PELO_MEU_ATLAS": prox_meu,
               "TERRITORIOS_QUE_COLIDIRIAM": colidiriam,
               "DEDUPE": linhas},
              open(TRAB / "DEDUPE.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\ngravado: {TRAB / 'DEDUPE.json'}")


if __name__ == "__main__":
    main()
