#!/usr/bin/env python3
"""
DISEASE INTELLIGENCE · OBSERVATIONAL · STEP 1 — WHAT IS THE VISIT KEY, AND WHAT DOES EACH
COLUMN ACTUALLY MEASURE?

Nothing enters the engine because its name looks right. The previous pilot lost a whole case
that way: a directory called FRUMENTO-SEPTORIA collects id_survey_var 372, which the source's
own metadata calls "Intensita' Oidio". So this file establishes two things by measurement
before any analysis exists:

PART A — THE VISIT KEY.
  The previous engine joined its denominator on `id_survey` alone and the certification found
  that key is not unique: the last file the filesystem handed over won. Before anything else,
  find a key that IS unique, or prove that none of the candidates is, and say so.

PART B — THE SEMANTIC FINGERPRINT.
  For each collected variable, measure: type, range, integrality, nulls, and the arithmetic
  relations between variables. The olive schema names its columns
      Tot, u, l1v, l1m, l2v, l2m, l3v, l3m, pv, pm, fu, ps
  plus three the server computes: Attiva, Dannosa, Totale.
  Those are abbreviations in Italian, and a translation is not evidence. What IS evidence:
      does Totale == Attiva + Dannosa, row by row?
      are Attiva/Dannosa/Totale bounded by Tot?
      is Tot a fixed sample size?
      are the values counts or percentages?
  Whatever the arithmetic says is what goes in the semantic sheet. Whatever it cannot settle
  is written UNKNOWN.

Nothing under CASES/ or ENGINE/ is read for logic — only the raw JSON and the collection
index. This file does not import the old engine at all.

Out: s1_key_and_fingerprint.json
"""
import json, os, glob, collections, statistics, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY", "CASES"))
OLIVE = os.path.join(CASES, "OLIVO-BACTROCERA-TOSCANA")

# candidate keys, most specific first
CANDIDATES = [
    ("uid",), ("id_survey",), ("id_survey", "_year"), ("id_survey", "_file"),
    ("id_field", "date"), ("id_field", "date", "_file"),
    ("id_field", "date", "id_org"),
]


def clean(s):
    return re.sub(r"<[^>]+>", " ", html.unescape(str(s))).strip()


def load_var(case, var):
    """Every raw row of one variable, tagged with the file it came from."""
    rows = []
    for fn in sorted(glob.glob(os.path.join(case, "RAW", f"*_v{var}_*.json"))):
        base = os.path.basename(fn)
        year = int(base[:-5].split("_")[-1])
        for r in json.load(open(fn, encoding="utf-8")):
            r["_file"] = base
            r["_year"] = year
            rows.append(r)
    return rows


def num(v):
    if v is None or v == "":
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


def key_report(rows, name):
    out = {}
    for cand in CANDIDATES:
        seen = collections.Counter(tuple(r.get(c) for c in cand) for r in rows)
        dupes = {k: n for k, n in seen.items() if n > 1}
        # a key is only useful if, where it repeats, the VALUE agrees
        conflicting = 0
        if dupes:
            vals = collections.defaultdict(set)
            for r in rows:
                k = tuple(r.get(c) for c in cand)
                if k in dupes:
                    vals[k].add(None if r.get("val") in (None, "") else str(r["val"]))
            conflicting = sum(1 for v in vals.values() if len(v) > 1)
        out["+".join(cand)] = {
            "distinct_keys": len(seen), "rows": len(rows),
            "keys_appearing_more_than_once": len(dupes),
            "of_those_with_CONFLICTING_values": conflicting,
            "UNIQUE": len(dupes) == 0,
            "SAFE_TO_JOIN_ON": len(dupes) == 0 or conflicting == 0}
    return out


def fingerprint(rows, var, declared_name, widget):
    vals = [num(r.get("val")) for r in rows]
    ok = [v for v in vals if v is not None]
    ints = sum(1 for v in ok if float(v).is_integer())
    neg = sum(1 for v in ok if v < 0)
    return {
        "source_var_id": var,
        "source_label": declared_name,
        "source_widget": widget,
        "n_rows": len(rows),
        "n_null_or_empty": len(vals) - len(ok),
        "n_readable": len(ok),
        "distinct_values": len(set(ok)),
        "min": min(ok) if ok else None,
        "max": max(ok) if ok else None,
        "median": statistics.median(ok) if ok else None,
        "share_integer": round(ints / len(ok), 4) if ok else None,
        "n_negative": neg,
        "share_zero": round(sum(1 for v in ok if v == 0) / len(ok), 4) if ok else None,
        "share_le_1": round(sum(1 for v in ok if v <= 1) / len(ok), 4) if ok else None,
        "share_le_100": round(sum(1 for v in ok if v <= 100) / len(ok), 4) if ok else None,
        "top_values": collections.Counter(ok).most_common(8),
        "date_range": (min((r.get("date") for r in rows if r.get("date")), default=None),
                       max((r.get("date") for r in rows if r.get("date")), default=None)),
    }


def main():
    idx = json.load(open(os.path.join(OLIVE, "collection_index.json"), encoding="utf-8"))
    declared = {v["id_survey_var"]: (clean(v.get("name")), v.get("widget"))
                for v in (idx.get("vars") or [])}
    collected = sorted({r["var"] for r in idx["requests"]})

    out = {"CASE": "OLIVO-BACTROCERA-TOSCANA",
           "SOURCE_API": idx["api"], "crop_id": idx.get("crop"), "schema_id": idx.get("schema"),
           "SOURCE_DECLARES_THESE_VARIABLES": {
               str(k): {"label": v[0], "widget": v[1]} for k, v in sorted(declared.items())},
           "COLLECTED": collected,
           "NOT_COLLECTED": sorted(set(declared) - set(collected)),
           "CODE_TABLE_ENTRIES": len(idx.get("codes") or [])}

    data = {v: load_var(OLIVE, v) for v in collected}

    # ── PART A — the visit key ────────────────────────────────────────────────────
    out["A_VISIT_KEY"] = {str(v): key_report(rows, str(v)) for v, rows in data.items()}
    safe = {}
    for v, rep in out["A_VISIT_KEY"].items():
        safe[v] = [k for k, r in rep.items() if r["SAFE_TO_JOIN_ON"]]
    out["A_KEYS_SAFE_IN_EVERY_COLLECTED_VARIABLE"] = sorted(
        set.intersection(*[set(x) for x in safe.values()]) if safe else set())

    # ── PART B — the fingerprint ─────────────────────────────────────────────────
    out["B_FINGERPRINT"] = {
        str(v): fingerprint(rows, v, declared.get(v, ("?", "?"))[0],
                            declared.get(v, ("?", "?"))[1])
        for v, rows in data.items()}

    # ── PART C — the arithmetic that pins the meaning ────────────────────────────
    # join on the safest key available, and test the identities
    joinkey = (out["A_KEYS_SAFE_IN_EVERY_COLLECTED_VARIABLE"] or ["id_survey+_year"])[0]
    kf = joinkey.split("+")

    def index(rows):
        m = {}
        for r in rows:
            m[tuple(r.get(c) for c in kf)] = num(r.get("val"))
        return m
    A, D, T, TOT = (index(data.get(-1001, [])), index(data.get(-1002, [])),
                    index(data.get(-1003, [])), index(data.get(1, [])))
    common = set(A) & set(D) & set(T) & set(TOT)
    both = [(A[k], D[k], T[k], TOT[k]) for k in common
            if None not in (A[k], D[k], T[k], TOT[k])]

    def frac(f):
        return round(sum(1 for x in both if f(*x)) / len(both), 6) if both else None

    out["C_ARITHMETIC"] = {
        "JOIN_KEY_USED": joinkey,
        "rows_where_all_four_variables_are_readable": len(both),
        "TOTALE_equals_ATTIVA_plus_DANNOSA": frac(lambda a, d, t, x: abs(t - (a + d)) < 1e-6),
        "TOTALE_ge_ATTIVA": frac(lambda a, d, t, x: t >= a - 1e-9),
        "TOTALE_ge_DANNOSA": frac(lambda a, d, t, x: t >= d - 1e-9),
        "ATTIVA_le_TOT": frac(lambda a, d, t, x: a <= x + 1e-9),
        "DANNOSA_le_TOT": frac(lambda a, d, t, x: d <= x + 1e-9),
        "TOTALE_le_TOT": frac(lambda a, d, t, x: t <= x + 1e-9),
        "TOT_equals_100": frac(lambda a, d, t, x: abs(x - 100) < 1e-9),
        "TOT_distribution": collections.Counter(
            x for _, _, _, x in both).most_common(10),
        "ATTIVA_and_DANNOSA_both_zero": frac(lambda a, d, t, x: a == 0 and d == 0),
        "ATTIVA_gt_0_while_DANNOSA_eq_0": frac(lambda a, d, t, x: a > 0 and d == 0),
        "DANNOSA_gt_0_while_ATTIVA_eq_0": frac(lambda a, d, t, x: d > 0 and a == 0)}

    json.dump(out, open(os.path.join(HERE, "s1_key_and_fingerprint.json"), "w",
                        encoding="utf-8"), indent=1, default=str)

    print("SOURCE DECLARES:")
    for k, v in sorted(out["SOURCE_DECLARES_THESE_VARIABLES"].items(), key=lambda x: int(x[0])):
        mark = "COLLECTED" if int(k) in collected else ""
        print(f"  var {k:>6}  {v['widget']:8s}  '{v['label']}'   {mark}")
    print("\nA — VISIT KEY (is it unique, and do repeats agree?)")
    for v, rep in out["A_VISIT_KEY"].items():
        print(f"  var {v}:")
        for k, r in rep.items():
            print(f"     {k:28s} distinct={r['distinct_keys']:>6} of {r['rows']:>6} rows"
                  f"  repeats={r['keys_appearing_more_than_once']:>6}"
                  f"  conflicting={r['of_those_with_CONFLICTING_values']:>6}"
                  f"  UNIQUE={r['UNIQUE']}  SAFE={r['SAFE_TO_JOIN_ON']}")
    print("\n  keys safe in EVERY collected variable:",
          out["A_KEYS_SAFE_IN_EVERY_COLLECTED_VARIABLE"])
    print("\nB — FINGERPRINT")
    for v, f in out["B_FINGERPRINT"].items():
        print(f"  var {v:>6} '{f['source_label']}'  n={f['n_rows']} null={f['n_null_or_empty']}"
              f" min={f['min']} max={f['max']} median={f['median']}"
              f" int={f['share_integer']} zero={f['share_zero']} le1={f['share_le_1']}"
              f" le100={f['share_le_100']}")
        print(f"          top: {f['top_values'][:5]}  dates {f['date_range']}")
    print("\nC — ARITHMETIC")
    for k, v in out["C_ARITHMETIC"].items():
        print(f"  {k} = {v}")


if __name__ == "__main__":
    main()
