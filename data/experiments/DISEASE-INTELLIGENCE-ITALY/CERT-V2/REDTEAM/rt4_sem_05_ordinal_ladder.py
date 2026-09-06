#!/usr/bin/env python3
"""RT4 / SEMANTICS probe 5 — attack CASES/run_case.py derive_rank / WORD_RANK.

Three separate attacks:
  A. every label present in the three real code tables, with the rank it receives, and a
     hand-stated TRUE order per variable. Report WRONG, not merely UNRESOLVED.
  B. Italian ordinal vocabulary the ladder does not know, and compounds.
  C. does build_scale depend on the ORDER of the code-table entries? (shuffle test)
"""
import json, os, sys, random, itertools, collections

HERE = os.path.dirname(os.path.abspath(__file__))
CASESD = os.path.abspath(os.path.join(HERE, "..", "..", "CASES"))
sys.path.insert(0, CASESD)
from run_case import derive_rank, build_scale, fold, WORD_RANK

CASES = ["OLIVO-BACTROCERA-TOSCANA", "VITE-OIDIO-TOSCANA", "FRUMENTO-SEPTORIA-TOSCANA"]

# The TRUE agronomic order of each coded variable, stated by hand from the source's own
# order_n / icon colour ramp (no.gif -> green -> yellow -> orange -> red -> triangle red),
# which is the source's own declaration of severity. Index = true severity rank.
TRUE_ORDER = {
    372: ["Nessuna", "5 - lieve", "10 - media", "25 - grave", "50 - gravissina", "75 - completa"],
    382: ["Nessuna", "5 - lieve", "10 - media", "25 - grave", "50 - gravissima", "75 - completa"],
    383: ["Nessuna", "5 - lieve", "10 - media", "25 - grave", "50 - gravissima", "90 - completa"],
    384: ["Nessuna", "Bassa <10%", "Media 10-25%", "Alta >25%"],
    385: ["Nessuna", "Bassa <5%", "Media 5-25%", "Alta >25%"],
    386: ["Nessuna", "Bassa <5%", "Media 5-25%", "Alta >25%"],
    # 371 / 381 are LOCALIZZAZIONE - where on the plant. Ordered by agronomic gravity: the
    # higher up the canopy the infection sits, the worse (flag leaf and ear are yield-bearing).
    371: ["No", "Parte bassa", "Parte alta", "Penultima foglia", "Ultima foglia", "Spiga"],
    381: ["No", "Terzultima foglia", "Penultima foglia", "Ultima foglia", "Spiga"],
    39: ["nessuna", "bassa", "media", "alta"],
    40: ["nessuna", "1-5%", "5-10%", ">10%"],
    # 42 is PRODOTTO - the active substance applied. NOT ORDINAL AT ALL.
    42: None,
}
VAR_NAME = {372: "Intensita Oidio", 382: "Intensita Septoria", 383: "Intensita Fusariosi",
            384: "Frequenza Oidio", 385: "Frequenza Septoria", 386: "Frequenza Fusariosi",
            371: "Localizzazione Oidio (WHERE on the plant)",
            381: "Localizzazione Septoria (WHERE on the plant)",
            39: "Presenza su foglie", 40: "presenza su grappoli",
            42: "prodotto (ACTIVE SUBSTANCE APPLIED)"}


def main():
    res = {}

    # ---------- A. real labels ----------
    A = {}
    for case in CASES:
        idx = json.load(open(os.path.join(CASESD, case, "collection_index.json")))
        codes = idx.get("codes") or []
        byvar = collections.defaultdict(list)
        for c in codes:
            byvar[c["id_survey_var"]].append(c)
        for var, entries in sorted(byvar.items()):
            scale, unresolved, hows = build_scale(codes, var)
            rows = []
            for c in sorted(entries, key=lambda c: c["order_n"]):
                r, how = derive_rank(c["name"])
                s = scale.get(str(c["id_survey_code"]))
                rows.append({"code": c["id_survey_code"], "label": c["name"],
                             "source_order_n": c["order_n"], "source_icon": c.get("icon"),
                             "RANK": r, "HOW": how,
                             "ORDINAL": (s or {}).get("ordinal"),
                             "IN_SCALE": s is not None})
            truth = TRUE_ORDER.get(var)
            verdict, detail = "NOT_ASSESSED", ""
            if truth is None and var in TRUE_ORDER:
                verdict = "CATEGORY_ERROR"
                detail = ("this variable is not ordinal at all; the engine still builds a scale "
                          f"for it with {len(scale)} of {len(entries)} labels")
            elif truth:
                got = [x for x in rows if x["IN_SCALE"]]
                kept = [x["label"] for x in sorted(got, key=lambda x: x["ORDINAL"])]
                # true order restricted to the labels that survived
                kept_true = [l for l in truth if l in {x["label"] for x in got}]
                dropped = [l for l in truth if l not in {x["label"] for x in got}]
                # is the surviving order right?
                order_ok = kept_true == [l for l in kept_true if l in kept] and \
                    [k for k in kept if k in kept_true] == kept_true
                # do two distinct true levels collapse onto one ordinal?
                byord = collections.defaultdict(list)
                for x in got:
                    byord[x["ORDINAL"]].append(x["label"])
                collapsed = {o: ls for o, ls in byord.items() if len(ls) > 1}
                verdict = ("ORDER_PRESERVED_BUT_TRUNCATED" if order_ok and dropped
                           else "ORDER_PRESERVED" if order_ok and not dropped
                           else "ORDER_WRONG")
                detail = {"SURVIVING_ORDER": kept, "TRUE_ORDER": truth,
                          "DROPPED_FROM_SCALE": dropped,
                          "N_DROPPED_OF_TOTAL": f"{len(dropped)}/{len(truth)}",
                          "COLLAPSED_ONTO_SAME_ORDINAL": collapsed}
            A[f"{case} :: var {var} ({VAR_NAME.get(var,'?')})"] = {
                "N_LABELS": len(entries), "N_IN_SCALE": len(scale),
                "N_UNRESOLVED": len(unresolved), "UNRESOLVED": unresolved,
                "METHODS": hows, "VERDICT": verdict, "DETAIL": detail, "LABELS": rows}
    res["A_REAL_CODE_TABLES"] = A

    # ---------- B. vocabulary the ladder does not know ----------
    probes = ["Nulla", "Assente/Bassa", "Molto alta", "Molto bassa", "Bassissima", "Altissima",
              "Elevatissima", "Trascurabile", "Diffusa", "Forte", "Debole", "Intensa",
              "Assenza", "Presente", "Non rilevata", "Non rilevato", "Non si rileva",
              "Nessun sintomo", "Sintomi assenti", "Medio-alta", "Bassa/Media", "Media-Alta",
              "Nessuna/Alta", "Alta/Nessuna", "Bassa", "Alta", "Media", "Nessuna",
              "0 - nulla", "1 - lieve", "grave", "gravissima", "gravissina", "completa",
              "Sporadica", "Localizzata", "Generalizzata", "Focolai", "Iniziale", "Avanzata",
              "n.d.", "N.D.", "Non applicabile", "Da verificare", "si", "no", "SI", "NO"]
    B = []
    for p in probes:
        r, how = derive_rank(p)
        B.append({"label": p, "folded": fold(p), "RANK": r, "HOW": how})
    res["B_VOCABULARY_PROBE"] = B
    res["B_SUMMARY"] = {
        "N_PROBED": len(probes),
        "N_UNRESOLVED": sum(1 for x in B if x["RANK"] is None),
        "N_RESOLVED": sum(1 for x in B if x["RANK"] is not None),
    }
    # the specific ones asked for
    res["B_ASKED_EXPLICITLY"] = {p: dict(zip(("RANK", "HOW"), derive_rank(p)))
                                 for p in ("Assente/Bassa", "Molto alta", "Nulla")}
    # WORD_RANK tie-break order (source-code order dependence inside derive_rank)
    res["B_WORD_RANK_MATCH_ORDER"] = [w for w, _ in
                                      sorted(WORD_RANK.items(), key=lambda kv: -len(kv[0]))]

    # ---------- C. does build_scale depend on code-table ORDER? ----------
    C = {}
    for case in CASES:
        idx = json.load(open(os.path.join(CASESD, case, "collection_index.json")))
        codes = idx.get("codes") or []
        if not codes:
            C[case] = "NO CODE TABLE (numeric case)"
            continue
        byvar = collections.defaultdict(list)
        for c in codes:
            byvar[c["id_survey_var"]].append(c)
        per = {}
        for var in byvar:
            ref = build_scale(codes, var)[0]
            same = True
            rnd = random.Random(1234)
            for _ in range(200):
                sh = codes[:]
                rnd.shuffle(sh)
                if build_scale(sh, var)[0] != ref:
                    same = False
                    break
            per[var] = {"ORDER_INDEPENDENT_OVER_200_SHUFFLES": same}
        C[case] = per
    # but: is the ORDINAL VALUE stable if a code is REMOVED from the table?
    idx = json.load(open(os.path.join(CASESD, "FRUMENTO-SEPTORIA-TOSCANA",
                                      "collection_index.json")))
    codes = idx["codes"]
    full = build_scale(codes, 384)[0]
    minus = build_scale([c for c in codes if c["id_survey_code"] != 1631], 384)[0]
    C["ORDINAL_IS_A_DENSE_RERANK_NOT_AN_ABSOLUTE_LEVEL"] = {
        "var_384_full_table": {k: (v["label"], v["ordinal"]) for k, v in full.items()},
        "var_384_with_Bassa_removed": {k: (v["label"], v["ordinal"]) for k, v in minus.items()},
        "NOTE": ("ordinal = ranks.index(rank), so deleting ONE code shifts the ordinal of every "
                 "code above it. The ordinal is a position in the SURVIVING set, not a level.")}
    res["C_ORDER_DEPENDENCE"] = C

    json.dump(res, open(os.path.join(HERE, "rt4_sem_05_ordinal_ladder.json"), "w",
                        encoding="utf-8"), indent=1, ensure_ascii=False, default=str)

    print("=" * 78)
    print("A. EVERY LABEL IN THE THREE REAL CODE TABLES")
    for k, v in A.items():
        print(f"\n--- {k}")
        print(f"    in_scale {v['N_IN_SCALE']}/{v['N_LABELS']}  unresolved={v['UNRESOLVED']}")
        print(f"    VERDICT: {v['VERDICT']}")
        for r in v["LABELS"]:
            mark = "  " if r["IN_SCALE"] else "XX"
            print(f"     {mark} code {r['code']:>5} order_n {r['source_order_n']:>3} "
                  f"icon {str(r['source_icon']):9s} {r['label']!r:26s} "
                  f"rank={str(r['RANK']):6s} ordinal={str(r['ORDINAL']):5s} {r['HOW']}")
        if isinstance(v["DETAIL"], dict):
            print(f"     DROPPED {v['DETAIL']['N_DROPPED_OF_TOTAL']}: {v['DETAIL']['DROPPED_FROM_SCALE']}")
            if v["DETAIL"]["COLLAPSED_ONTO_SAME_ORDINAL"]:
                print(f"     COLLAPSED: {v['DETAIL']['COLLAPSED_ONTO_SAME_ORDINAL']}")
        elif v["DETAIL"]:
            print("     ", v["DETAIL"])

    print("\n" + "=" * 78)
    print("B. VOCABULARY PROBE  (resolved %d / unresolved %d of %d)" % (
        res["B_SUMMARY"]["N_RESOLVED"], res["B_SUMMARY"]["N_UNRESOLVED"], len(probes)))
    for x in B:
        print(f"    {x['label']!r:20s} -> rank={str(x['RANK']):6s} {x['HOW']}")
    print("\n    WORD_RANK match order (longest first, ties by dict order):")
    print("     ", res["B_WORD_RANK_MATCH_ORDER"])

    print("\n" + "=" * 78)
    print("C. ORDER DEPENDENCE")
    print(json.dumps(res["C_ORDER_DEPENDENCE"], indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
