#!/usr/bin/env python3
"""MEDIÇÃO D0.3 — os 43 casos canónicos contra os eixos semânticos.

READ-ONLY. Não escreve em produção, não chama rede, não altera dado canónico.
Lê dois artefactos do BASELINE declarado e devolve uma linha por CASE_ID.

    BASELINE = a4fb6d81681094925ccfd1638bc7386cbec6f4d4
               (claude/visible-intelligence-v1, medido em D0.2)

    FONTE 1  italia-portale/client/meeting-intelligence-snapshot.json   Linha A
    FONTE 2  italia-portale/client/adama-relevance.js                   Linha B

O script FALHA (exit 1) se o universo deixar de fechar: 43 ids únicos dos dois
lados, mesmos ids, e cada agregado a recompor o total declarado na fonte.

    UM SCRIPT DE PESQUISA NÃO É DONO DE REGRA.
    Este ficheiro não decide nada: conta, e reprova quando a conta não fecha.

Uso:
    python3 docs/biblia/medicoes/medir_43_quatro_eixos.py [--ref a4fb6d8] [--json OUT]

Sem --json escreve só o relatório em stdout. Determinístico: toda ordenação é
por chave, nunca por iteração de dict.
"""
import argparse
import collections
import hashlib
import json
import subprocess
import sys

BASELINE_DEFAULT = "a4fb6d81681094925ccfd1638bc7386cbec6f4d4"
SNAPSHOT = "italia-portale/client/meeting-intelligence-snapshot.json"
RELEVANCE = "italia-portale/client/adama-relevance.js"
EXPECTED_TOTAL = 43

# Os eixos medidos. O quinto NÃO estava no pedido da missão: foi encontrado no
# código (v21_comercial.py, EXTERNAL_LAW) e é medido porque existe.
AXES = [
    ("ELIGIBILITY_SURFACE", "linha B · adama_relevance.py"),
    ("ELIGIBILITY_CLASS", "linha B · adama_relevance.py"),
    ("ACTION_STATUS", "linha A · v21_oportunidades.py"),
    ("COMMERCIAL_PRIORITY", "linha A · v21_comercial.py"),
    ("PUBLICATION_STATE", "linha A · v21_*.py"),
    ("EXTERNAL_MATERIAL_READY", "linha A · v21_comercial.py"),
]


def git_show(ref, path):
    out = subprocess.run(["git", "show", f"{ref}:{path}"],
                         capture_output=True, check=True)
    return out.stdout


def load_sources(ref):
    raw_snap = git_show(ref, SNAPSHOT)
    raw_rel = git_show(ref, RELEVANCE)
    snap = json.loads(raw_snap)
    text = raw_rel.decode("utf-8")
    start = text.index("{", text.index("window.ADAMA_RELEVANCE"))
    rel = json.loads(text[start:text.rindex(";")].strip())
    meta = {
        "SNAPSHOT_SHA256": hashlib.sha256(raw_snap).hexdigest(),
        "RELEVANCE_SHA256": hashlib.sha256(raw_rel).hexdigest(),
    }
    return snap, rel, meta


def fail(msg):
    print(f"FAIL · {msg}", file=sys.stderr)
    sys.exit(1)


def build_rows(snap, rel):
    cases = {c["ID"]: c for c in snap["CASES"]}
    verd = rel["VERDETTI"]

    if len(cases) != EXPECTED_TOTAL:
        fail(f"snapshot tem {len(cases)} ids únicos, esperado {EXPECTED_TOTAL}")
    if len(snap["CASES"]) != EXPECTED_TOTAL:
        fail("há CASE_IDs duplicados no snapshot")
    if len(verd) != EXPECTED_TOTAL:
        fail(f"adama-relevance tem {len(verd)} vereditos, esperado {EXPECTED_TOTAL}")
    if set(cases) != set(verd):
        fail("os conjuntos de CASE_ID das duas fontes não coincidem: "
             f"só-A={sorted(set(cases)-set(verd))} só-B={sorted(set(verd)-set(cases))}")

    rows = []
    for cid in sorted(cases):
        c, v = cases[cid], verd[cid]
        pm = c.get("PORTFOLIO_MATCHES") or []
        rows.append({
            "CASE_ID": cid,
            "ARCHETYPE": c.get("ARCHETYPE"),
            # eixo 1 — elegibilidade (linha B)
            "ELIGIBILITY_CLASS": v.get("CLASSE"),
            "ELIGIBILITY_SURFACE": v.get("SUPERFICIE"),
            "ELIGIBILITY_REASON": v.get("PERCHE"),
            "ELIGIBILITY_PROOF": v.get("PROVA"),
            "ELIGIBILITY_OWNER": rel.get("DONO_DA_LEI"),
            "ELIGIBILITY_RULE_VERSION": rel.get("BUILD_ID"),
            # eixo 2 — estado de ação (linha A)
            "ACTION_STATUS": c.get("STATUS"),
            "ACTION_STATUS_OWNER": "scripts/v21_oportunidades.py",
            "ACTION_STATUS_RULE_VERSION": snap.get("RULE_VERSION"),
            # eixo 3 — prioridade comercial (linha A)
            "COMMERCIAL_PRIORITY": c.get("COMMERCIAL_PRIORITY"),
            "COMMERCIAL_PRIORITY_REASON": c.get("WHY_COMMERCIAL_CODES"),
            "COMMERCIAL_PRIORITY_OWNER": "scripts/v21_comercial.py",
            "COMMERCIAL_PRIORITY_RULE_VERSION": snap.get("RULE_VERSION"),
            # eixo 4 — publicação (linha A)
            "PUBLICATION_STATE": c.get("PUBLICATION_STATE"),
            "PUBLICATION_STATE_OWNER": "UNKNOWN",
            "PUBLICATION_STATE_RULE_VERSION": snap.get("RULE_VERSION"),
            # eixo 5 — saída externa (encontrado no código, não pedido)
            "EXTERNAL_MATERIAL_READY": c.get("EXTERNAL_MATERIAL_READY"),
            "EXTERNAL_BLOCKER_CODES": c.get("EXTERNAL_BLOCKER_CODES") or [],
            "EXTERNAL_OWNER": "scripts/v21_comercial.py",
            # tempo
            "WINDOW_DEFINED": c.get("WINDOW_DEFINED"),
            "WINDOW_OPEN_NOW": c.get("WINDOW_OPEN_NOW"),
            "WINDOW_TYPE": c.get("WINDOW_TYPE"),
            "WINDOW_RULE_STATE": c.get("WINDOW_RULE_STATE"),
            "WINDOW_STATE": c.get("WINDOW_STATE"),
            "DAYS_REMAINING": c.get("DAYS_REMAINING"),
            "COMMERCIAL_TIMING_BASIS": c.get("COMMERCIAL_TIMING_BASIS"),
            # why now
            "WHY_NOW_PRESENT": bool(c.get("WHY_NOW_CODES")),
            "WHY_NOW_CODES": c.get("WHY_NOW_CODES") or [],
            "WHY_NOW_OWNER": "scripts/v21_oportunidades.py",
            # produto
            "PORTFOLIO_MATCH_COUNT": len(pm),
            "COMMERCIAL_PRODUCT_COUNT": c.get("COMMERCIAL_PRODUCT_COUNT"),
            "PRIMARY_PRODUCT_OR_PROOF": c.get("PRIMARY_MATCH")
                                        or c.get("PRIMARY_MATCH_REASON"),
            "PRODUCT_LINK_STATE": c.get("PRODUCT_LINK_STATE"),
            "PRODUCT_LINK_PROVEN": c.get("PRODUCT_LINK_STATE") == "VERIFIED_LABEL_MATCH",
            "TARGET": c.get("TARGET"),
            "NEED_DIRECTION": c.get("NEED_DIRECTION"),
            "CLAIM_GEOGRAPHY_HOLDS": c.get("CLAIM_GEOGRAPHY_HOLDS"),
            # evidência
            "EVIDENCE_IDS": c.get("EVIDENCE_IDS") or [],
            "EVIDENCE_COUNT": c.get("EVIDENCE_COUNT"),
            "OPPORTUNITY_SCORE": c.get("OPPORTUNITY_SCORE"),
            "OPPORTUNITY_STATE": c.get("OPPORTUNITY_STATE"),
        })
    return rows


def check_totals(rows, snap, rel):
    """Cada agregado recompõe o total declarado NA FONTE. Se não, FAIL."""
    checks = [
        ("BY_STATUS", "ACTION_STATUS", snap["BY_STATUS"]),
        ("BY_COMMERCIAL_PRIORITY", "COMMERCIAL_PRIORITY", snap["BY_COMMERCIAL_PRIORITY"]),
        ("BY_PUBLICATION_STATE", "PUBLICATION_STATE", snap["BY_PUBLICATION_STATE"]),
        ("BY_WINDOW_DEFINED", "WINDOW_DEFINED", snap["BY_WINDOW_DEFINED"]),
        ("BY_WINDOW_OPEN_NOW", "WINDOW_OPEN_NOW", snap["BY_WINDOW_OPEN_NOW"]),
        ("BY_WINDOW_RULE_STATE", "WINDOW_RULE_STATE", snap["BY_WINDOW_RULE_STATE"]),
        ("PER_SUPERFICIE", "ELIGIBILITY_SURFACE", rel["PER_SUPERFICIE"]),
        ("PER_CLASSE", "ELIGIBILITY_CLASS", rel["PER_CLASSE"]),
    ]
    report = []
    empty_declared = {}
    for name, field, declared in checks:
        got = dict(collections.Counter(r[field] for r in rows))
        # Uma fonte pode DECLARAR um estado com zero membros. Isso não é
        # divergência: é vocabulário publicado sem população. Fica registado à
        # parte em vez de ser apagado da comparação em silêncio.
        #
        #     ESTADO DECLARADO E VAZIO NÃO É ESTADO AUSENTE.
        zeros = sorted(k for k, v in declared.items() if v == 0)
        if zeros:
            empty_declared[name] = zeros
        nonzero = {k: v for k, v in declared.items() if v != 0}
        if got != nonzero:
            fail(f"{name}: recontagem {got} != declarado (não-zero) {nonzero}")
        if sum(got.values()) != EXPECTED_TOTAL:
            fail(f"{name}: soma {sum(got.values())} != {EXPECTED_TOTAL}")
        report.append((name, field, got))
    return report, empty_declared


def cross(rows, a, b):
    """Matriz cruzada determinística. Fecha em len(rows) ou levanta."""
    t = collections.defaultdict(lambda: collections.defaultdict(int))
    for r in rows:
        t[r[a]][r[b]] += 1
    total = sum(v for row in t.values() for v in row.values())
    if total != len(rows):
        fail(f"matriz {a}×{b} fecha em {total}, esperado {len(rows)}")
    return {ka: dict(sorted(t[ka].items())) for ka in sorted(t)}


def render_matrix(title, a, b, m):
    cols = sorted({c for row in m.values() for c in row})
    w = max([len(a)] + [len(str(k)) for k in m]) + 1
    out = [f"### {title}", "", "```",
           " " * w + "| " + " | ".join(f"{c:>{max(len(c), 4)}}" for c in cols) + " | TOTAL"]
    out.append("-" * (w + sum(max(len(c), 4) + 3 for c in cols) + 8))
    for ka in sorted(m):
        cells = []
        for c in cols:
            v = m[ka].get(c, 0)
            cells.append(f"{(v if v else '·'):>{max(len(c), 4)}}")
        out.append(f"{str(ka):<{w}}| " + " | ".join(cells) + f" | {sum(m[ka].values()):>5}")
    tot = [sum(m[k].get(c, 0) for k in m) for c in cols]
    out.append("-" * (w + sum(max(len(c), 4) + 3 for c in cols) + 8))
    out.append(f"{'TOTAL':<{w}}| " + " | ".join(
        f"{t:>{max(len(c), 4)}}" for t, c in zip(tot, cols)) + f" | {sum(tot):>5}")
    out += ["```", ""]
    return "\n".join(out)


def setof(rows, field, value):
    return sorted(r["CASE_ID"] for r in rows if r[field] == value)


def relation(a_ids, b_ids, a_name, b_name):
    A, B = set(a_ids), set(b_ids)
    if A == B:
        return f"{a_name} == {b_name}  (conjuntos idênticos, n={len(A)})"
    if A < B:
        return f"{a_name} ⊂ {b_name}  (próprio, {len(A)} de {len(B)})"
    if B < A:
        return f"{b_name} ⊂ {a_name}  (próprio, {len(B)} de {len(A)})"
    if A & B:
        return (f"{a_name} ∩ {b_name} = {len(A & B)}; "
                f"só-{a_name}={len(A - B)}; só-{b_name}={len(B - A)}  (sobreposição parcial)")
    return f"{a_name} ∩ {b_name} = ∅  (disjuntos)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=BASELINE_DEFAULT)
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    snap, rel, meta = load_sources(args.ref)
    rows = build_rows(snap, rel)
    totals, empty_declared = check_totals(rows, snap, rel)

    matrices = {
        "A · ELIGIBILITY_SURFACE × ACTION_STATUS": ("ELIGIBILITY_SURFACE", "ACTION_STATUS"),
        "B · ELIGIBILITY_CLASS × ACTION_STATUS": ("ELIGIBILITY_CLASS", "ACTION_STATUS"),
        "C · ELIGIBILITY_SURFACE × COMMERCIAL_PRIORITY": ("ELIGIBILITY_SURFACE", "COMMERCIAL_PRIORITY"),
        "D · ACTION_STATUS × COMMERCIAL_PRIORITY": ("ACTION_STATUS", "COMMERCIAL_PRIORITY"),
        "E · COMMERCIAL_PRIORITY × PUBLICATION_STATE": ("COMMERCIAL_PRIORITY", "PUBLICATION_STATE"),
        "F · ELIGIBILITY_SURFACE × PUBLICATION_STATE": ("ELIGIBILITY_SURFACE", "PUBLICATION_STATE"),
        "G · ACTION_STATUS × PUBLICATION_STATE": ("ACTION_STATUS", "PUBLICATION_STATE"),
        "H · WINDOW_DEFINED × ACTION_STATUS": ("WINDOW_DEFINED", "ACTION_STATUS"),
        "I · WINDOW_OPEN_NOW × ACTION_STATUS": ("WINDOW_OPEN_NOW", "ACTION_STATUS"),
        "J · WINDOW_OPEN_NOW × COMMERCIAL_PRIORITY": ("WINDOW_OPEN_NOW", "COMMERCIAL_PRIORITY"),
        "K · PUBLICATION_STATE × EXTERNAL_MATERIAL_READY": ("PUBLICATION_STATE", "EXTERNAL_MATERIAL_READY"),
    }
    built = {k: cross(rows, a, b) for k, (a, b) in matrices.items()}

    sets = {
        "SALES_READY": setof(rows, "COMMERCIAL_PRIORITY", "SALES_READY"),
        "PUBLISHABLE": setof(rows, "PUBLICATION_STATE", "PUBLISHABLE"),
        "ACT_NOW": setof(rows, "ACTION_STATUS", "ACT_NOW"),
        "OPPORTUNITA": setof(rows, "ELIGIBILITY_SURFACE", "OPPORTUNITA"),
        "EXTERNAL_YES": setof(rows, "EXTERNAL_MATERIAL_READY", "YES"),
        "WINDOW_OPEN_YES": setof(rows, "WINDOW_OPEN_NOW", "YES"),
        "CLASS_A": setof(rows, "ELIGIBILITY_CLASS", "A"),
    }

    print(f"BASELINE_REF                 {args.ref}")
    print(f"SNAPSHOT_SHA256              {meta['SNAPSHOT_SHA256']}")
    print(f"RELEVANCE_SHA256             {meta['RELEVANCE_SHA256']}")
    print(f"BUILD_ID (A)                 {snap.get('BUILD_ID')}")
    print(f"BUILD_ID (B)                 {rel.get('BUILD_ID')}")
    print(f"BUILD_ID_MATCH               {snap.get('BUILD_ID') == rel.get('BUILD_ID')}")
    print(f"CASE_IDS_UNIQUE              {len(rows)}")
    print(f"UNIVERSE_43_OF_43            {'PASS' if len(rows) == EXPECTED_TOTAL else 'FAIL'}")
    print(f"AGGREGATES_RECOMPOSE         PASS  ({len(totals)} agregados)")
    print()
    for name, zeros in sorted(empty_declared.items()):
        print(f"  DECLARED_EMPTY  {name:<24} {zeros}   estado declarado, populacao 0")
    if empty_declared:
        print()
    for name, field, got in totals:
        print(f"  {name:<24} {json.dumps(got, sort_keys=True)}")
    print()
    for title, (a, b) in matrices.items():
        print(render_matrix(title, a, b, built[title]))
    print("## CONJUNTOS POR CASE_ID\n")
    for k in sorted(sets):
        print(f"{k:<18} n={len(sets[k]):>2}  {sets[k]}")
    print("\n## RELAÇÕES DE CONJUNTO\n")
    pairs = [("SALES_READY", "PUBLISHABLE"), ("SALES_READY", "ACT_NOW"),
             ("SALES_READY", "OPPORTUNITA"), ("SALES_READY", "EXTERNAL_YES"),
             ("PUBLISHABLE", "ACT_NOW"), ("PUBLISHABLE", "OPPORTUNITA"),
             ("ACT_NOW", "OPPORTUNITA"), ("ACT_NOW", "WINDOW_OPEN_YES"),
             ("SALES_READY", "WINDOW_OPEN_YES"), ("CLASS_A", "OPPORTUNITA")]
    for a, b in pairs:
        print("  " + relation(sets[a], sets[b], a, b))

    if args.json:
        payload = {
            "MEASUREMENT": "D0.3 · 43 casos × eixos semânticos",
            "GENERATED_BY": "docs/biblia/medicoes/medir_43_quatro_eixos.py",
            "READ_ONLY": True,
            "BASELINE_REF": args.ref,
            "SOURCES": {SNAPSHOT: meta["SNAPSHOT_SHA256"],
                        RELEVANCE: meta["RELEVANCE_SHA256"]},
            "LINE_A": {"BUILD_ID": snap.get("BUILD_ID"),
                       "RULE_VERSION": snap.get("RULE_VERSION"),
                       "ENGINE_VERSION": snap.get("ENGINE_VERSION"),
                       "GENERATED_AT": snap.get("GENERATED_AT"),
                       "SOURCE_HEAD": snap.get("SOURCE_HEAD"),
                       "LAW": snap.get("LAW")},
            "LINE_B": {"BUILD_ID": rel.get("BUILD_ID"),
                       "OWNER": rel.get("DONO_DA_LEI"),
                       "GENERATED_BY": rel.get("GERADO_POR"),
                       "SOURCE_HEAD": rel.get("SOURCE_HEAD")},
            "TOTAL_CASES": len(rows),
            "AGGREGATES": {n: g for n, _, g in totals},
            "DECLARED_BUT_EMPTY": empty_declared,
            "MATRICES": built,
            "SETS": sets,
            "CASES": rows,
        }
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=False)
        print(f"\nJSON escrito: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
