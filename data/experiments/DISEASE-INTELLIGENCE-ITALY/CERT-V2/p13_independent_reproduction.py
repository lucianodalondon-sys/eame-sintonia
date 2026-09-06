#!/usr/bin/env python3
"""
CERT-V2 / STEP 13 — THE SAME NUMBER BY A SECOND ROAD.

Two scripts that both call current_pressure() are not two measurements. This file does not
import the engine at all. It re-implements CURRENT_PRESSURE from the CONTRACT WRITTEN IN THE
DOCSTRING of current_pressure.py — window, unit, baseline, unknown rule, thresholds, floor —
reading the raw JSON directly, and then compares province by province.

Where the two roads disagree, the disagreement is the finding, not the average.

A SECOND, DELIBERATE DIFFERENCE: the denominator join. The shipped guard joins the
denominator variable to the numerator by `id_survey` alone. Step 1 showed `id_survey` is not
unique across season files. This road computes the cell THREE ways:

   A_NO_GUARD          no denominator guard at all
   B_GUARD_AS_SHIPPED  join by id_survey alone (what the engine does)
   C_GUARD_BY_KEY      join by (id_survey, year) — the same idea with a key that identifies

If B and C disagree, the shipped guard is joining rows that are not the same visit.

Out: p13_independent_reproduction.json
"""
import json, os, sys, glob, collections, datetime as dt, unicodedata, re

HERE = os.path.dirname(os.path.abspath(__file__))
CASEDIR = os.path.join(HERE, "..", "CASES")
AS_OF = dt.date(2026, 9, 6)
WINDOW, MIN_SITES, MIN_BASE, HIGH_P, LOW_P, FLOOR = 28, 8, 5, 0.80, 0.20, 5


def fold(s):
    s = unicodedata.normalize("NFD", str(s))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower().strip()


LADDER = {"nessuna": 0, "nessuno": 0, "assente": 0, "no": 0,
          "bassa": 1, "lieve": 1, "scarsa": 1, "media": 2, "moderata": 2,
          "alta": 3, "grave": 3, "elevata": 3, "si": 3}


def rank_label(lab):
    """Independent re-derivation of the ordinal from the label text."""
    f = fold(lab)
    if f in LADDER:
        return LADDER[f]
    for w in sorted(LADDER, key=len, reverse=True):
        if re.search(r"\b" + w + r"\b", f):
            return LADDER[w]
    m = re.match(r"^[<>]?\s*(\d+)\s*[-–]\s*(\d+)\s*%$", f)
    if m:
        return float(m.group(1))
    m = re.match(r"^>\s*(\d+)\s*%$", f)
    if m:
        return float(m.group(1)) + 0.5
    m = re.match(r"^<\s*(\d+)\s*%$", f)
    if m:
        return 0.5
    return None


def read_case(case, var):
    idx = json.load(open(os.path.join(case, "collection_index.json")))
    codes = [c for c in (idx.get("codes") or []) if c["id_survey_var"] == var]
    scale = {}
    if codes:
        tmp = {}
        for c in codes:
            r = rank_label(c["name"])
            if r is not None:
                tmp[str(c["id_survey_code"])] = r
        order = sorted(set(tmp.values()))
        scale = {k: order.index(v) for k, v in tmp.items()}
    rows = []
    for fn in sorted(glob.glob(os.path.join(case, "RAW", f"*_v{var}_*.json"))):
        y = int(os.path.basename(fn)[:-5].split("_")[-1])
        for r in json.load(open(fn)):
            d = r.get("date")
            if not d:
                continue
            try:
                r["_d"] = dt.date.fromisoformat(d)
            except ValueError:
                continue
            r["_file_year"] = y
            rows.append(r)
    return rows, scale, idx


def value_of(r, scale):
    v = r.get("val")
    if v is None or v == "":
        return None
    if scale:
        return None if str(v) not in scale else float(scale[str(v)])
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


def denominators(case, denom_var, by_year):
    """by_year=False reproduces the shipped join (id_survey alone).
       by_year=True joins on (id_survey, file year), a key that identifies the visit."""
    den = {}
    for fn in sorted(glob.glob(os.path.join(case, "RAW", f"*_v{denom_var}_*.json"))):
        y = int(os.path.basename(fn)[:-5].split("_")[-1])
        for r in json.load(open(fn)):
            v = r.get("val")
            try:
                val = float(v) if v not in (None, "") else None
            except ValueError:
                val = None
            den[(r["id_survey"], y) if by_year else r["id_survey"]] = val
    return den


def window_incidence(rows, scale, lo, hi):
    sites = collections.defaultdict(list)
    for r in rows:
        if not (lo <= r["_d"] <= hi):
            continue
        v = value_of(r, scale)
        if v is None:
            continue
        sites[r["id_field"]].append(v)
    if not sites:
        return None
    m = [max(v) for v in sites.values()]
    return {"n_sites": len(m), "INCIDENCE": sum(1 for v in m if v > 0) / len(m)}


def shift(d, y):
    try:
        return d.replace(year=y)
    except ValueError:
        return d.replace(year=y, day=28)


def pressure(rows, scale, as_of):
    hi, lo = as_of, as_of - dt.timedelta(days=WINDOW - 1)
    byp = collections.defaultdict(list)
    for r in rows:
        if r.get("nome_area"):
            byp[r["nome_area"]].append(r)
    out = {}
    for p, pr in sorted(byp.items()):
        cur = window_incidence(pr, scale, lo, hi)
        if cur is None or cur["n_sites"] < MIN_SITES:
            out[p] = {"STATE": "UNKNOWN_NO_DATA", "VALUE": None,
                      "n_sites": (cur or {}).get("n_sites", 0)}
            continue
        base = []
        for y in sorted({r["_d"].year for r in pr}):
            if y >= as_of.year:
                continue
            b = window_incidence(pr, scale, shift(lo, y), shift(hi, y))
            if b and b["n_sites"] >= MIN_SITES:
                base.append(b["INCIDENCE"])
        rec = {"VALUE": round(cur["INCIDENCE"], 4), "n_sites": cur["n_sites"],
               "BASELINE_N": len(base)}
        if len(base) < MIN_BASE:
            rec["STATE"] = "UNKNOWN_NO_BASELINE"
        else:
            v = cur["INCIDENCE"]
            below = sum(1 for b in base if b < v) + 0.5 * sum(1 for b in base if b == v)
            pc = below / len(base)
            rec["PERCENTILE"] = round(pc, 4)
            st = "HIGHER_THAN_USUAL" if pc >= HIGH_P else (
                "LOWER_THAN_USUAL" if pc <= LOW_P else "TYPICAL_FOR_THE_DATE")
            if st == "HIGHER_THAN_USUAL" and cur["n_sites"] * v < FLOOR:
                st = "TYPICAL_FOR_THE_DATE"
                rec["HIGHER_WITHHELD_BY_FLOOR"] = True
            rec["STATE"] = st
        out[p] = rec
    return out


def main():
    res = {"AS_OF": AS_OF.isoformat(), "METHOD": "independent re-implementation from the "
           "written contract; the engine is never imported", "CASES": {}}
    for crop, name, var, denom in [("OLIVE", "OLIVO-BACTROCERA-TOSCANA", -1002, 1),
                                   ("VINE", "VITE-OIDIO-TOSCANA", 39, None),
                                   ("WHEAT", "FRUMENTO-SEPTORIA-TOSCANA", 372, None)]:
        case = os.path.join(CASEDIR, name)
        rows, scale, idx = read_case(case, var)
        variants = {"A_NO_GUARD": pressure(rows, scale, AS_OF)}
        if denom is not None:
            for label, by_year in (("B_GUARD_AS_SHIPPED", False), ("C_GUARD_BY_KEY", True)):
                den = denominators(case, denom, by_year)
                kept = [r for r in rows
                        if den.get((r["id_survey"], r["_file_year"]) if by_year
                                   else r["id_survey"])]
                variants[label] = pressure(kept, scale, AS_OF)
                variants[label + "_rows_kept"] = f"{len(kept)}/{len(rows)}"
        res["CASES"][crop] = {"VALUE_MODE": "ORDINAL" if scale else "NUMERIC",
                              "scale_size": len(scale), "n_rows": len(rows),
                              "VARIANTS": variants}

    # compare against the shipped engine, loaded only now and only to read its answer
    sys.path.insert(0, os.path.join(HERE, "..", "ENGINE"))
    sys.path.insert(0, CASEDIR)
    import current_pressure as cp
    agree, disagree, detail = 0, 0, {}
    for crop, name, var in [("OLIVE", "OLIVO-BACTROCERA-TOSCANA", -1002),
                            ("VINE", "VITE-OIDIO-TOSCANA", 39),
                            ("WHEAT", "FRUMENTO-SEPTORIA-TOSCANA", 372)]:
        case = os.path.join(CASEDIR, name)
        try:
            shipped = cp.current_pressure(case, var, AS_OF)["PROVINCES"]
        except Exception as e:
            detail[crop] = {"SHIPPED_REFUSED": f"{type(e).__name__}: {str(e)[:200]}"}
            continue
        mine = res["CASES"][crop]["VARIANTS"].get(
            "B_GUARD_AS_SHIPPED", res["CASES"][crop]["VARIANTS"]["A_NO_GUARD"])
        d = {}
        for p in sorted(set(shipped) | set(mine)):
            a = shipped.get(p, {}).get("STATE")
            b = mine.get(p, {}).get("STATE")
            va = shipped.get(p, {}).get("VALUE")
            vb = mine.get(p, {}).get("VALUE")
            same = (a == b) and (va is None and vb is None or
                                 (va is not None and vb is not None and abs(va - vb) < 1e-4))
            agree += same
            disagree += (not same)
            if not same:
                d[p] = {"SHIPPED": {"STATE": a, "VALUE": va},
                        "INDEPENDENT": {"STATE": b, "VALUE": vb}}
        detail[crop] = {"disagreeing_provinces": d, "n_provinces": len(set(shipped) | set(mine))}

    # does the shipped join differ from a join on a key that identifies?
    join_effect = {}
    for crop, v in res["CASES"].items():
        V = v["VARIANTS"]
        if "C_GUARD_BY_KEY" in V:
            diff = {p: {"B_as_shipped": V["B_GUARD_AS_SHIPPED"].get(p),
                        "C_by_identifying_key": V["C_GUARD_BY_KEY"].get(p)}
                    for p in V["B_GUARD_AS_SHIPPED"]
                    if V["B_GUARD_AS_SHIPPED"].get(p) != V["C_GUARD_BY_KEY"].get(p)}
            join_effect[crop] = {"rows_kept_B": V["B_GUARD_AS_SHIPPED_rows_kept"],
                                 "rows_kept_C": V["C_GUARD_BY_KEY_rows_kept"],
                                 "cells_that_differ": len(diff), "detail": diff}

    res["COMPARISON_WITH_SHIPPED"] = {"CELLS_AGREE": agree, "CELLS_DISAGREE": disagree,
                                      "DETAIL": detail}
    res["DENOMINATOR_JOIN_EFFECT"] = join_effect
    res["INDEPENDENT_REPRODUCTIONS"] = len(res["CASES"])
    json.dump(res, open(os.path.join(HERE, "p13_independent_reproduction.json"), "w"),
              indent=1, default=str)

    print(f"cells agree={agree}  disagree={disagree}")
    for c, d in detail.items():
        print(f"  {c}: {json.dumps(d)[:600]}")
    print("\ndenominator join effect (shipped id_survey vs identifying key):")
    for c, d in join_effect.items():
        print(f"  {c}: kept_B={d['rows_kept_B']} kept_C={d['rows_kept_C']} "
              f"cells_that_differ={d['cells_that_differ']}")
        for p, x in list(d["detail"].items())[:6]:
            print(f"     {p}: {json.dumps(x)[:220]}")


if __name__ == "__main__":
    main()
