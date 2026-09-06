#!/usr/bin/env python3
"""
CERT-V2 / STEP 4 (DATE AS A FIRST-CLASS DIMENSION) and STEP 5 (THE EFFECT FLOOR), measured
together because they are the same sweep.

STEP 4 — the unit of analysis is REGION x CROP x ISSUE x DATE, never REGION x CROP x ISSUE.
  The same cell is evaluated at many real dates in the series. A cell that qualifies on one
  date and not on another is NOT an inconsistency if the evidence moved. What is forbidden is
  publishing a state without the date attached.

STEP 5 — MIN_POSITIVE_SITES = 5 was added AFTER a red team found HIGHER_THAN_USUAL firing off
  4 groves out of 119. A floor introduced to remove known false positives cannot be certified
  by the false positives it was built to remove. It is therefore re-measured here BLIND:
  every date, every province, every case, including dates and cells that were never part of
  the sample that motivated it, with the class computed BOTH with and without the floor.

  The question is NOT "does it save the olive". It is:
     of the HIGHER calls the floor withheld, how many rested on a handful of positive sites?
     of the HIGHER calls it kept, how many rested on a broad base?
     does it ever withhold a call that a large positive base supports?

Nothing in ENGINE/ is modified: the floor is switched off by passing min_positive_sites=0 to
the shipped function, which is a declared parameter of it.

Out: p4_cell_state_by_date.json, p5_effect_floor.json
"""
import json, os, sys, datetime as dt, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ENGINE"))
sys.path.insert(0, os.path.join(HERE, "..", "CASES"))
import current_pressure as cp

CASES = [("TOSCANA", "OLIVE", "BACTROCERA_OLEAE_DAMAGING",
          os.path.join(HERE, "..", "CASES", "OLIVO-BACTROCERA-TOSCANA"), -1002),
         ("TOSCANA", "VINE", "OIDIO_LEAF",
          os.path.join(HERE, "..", "CASES", "VITE-OIDIO-TOSCANA"), 39),
         ("TOSCANA", "WHEAT", "SEPTORIA",
          os.path.join(HERE, "..", "CASES", "FRUMENTO-SEPTORIA-TOSCANA"), 372)]

# Real dates spanning the 2026 season, including the two the pilot itself named.
DATES_2026 = [dt.date(2026, m, d) for m, d in
              [(3, 15), (4, 15), (5, 15), (6, 1), (6, 15), (7, 1), (7, 15),
               (8, 1), (8, 15), (9, 1), (9, 6)]]
# the SAME calendar date in every prior season present in the archive
SAME_DAY_PRIOR = [dt.date(y, 9, 6) for y in range(2007, 2026)]

CLASSED = (cp.HIGHER, cp.TYPICAL, cp.LOWER)


def memoize_denominator_guard():
    """DECLARED PERFORMANCE PATCH, verified before it is used.

    current_pressure.denominator_guard re-reads and re-parses all 21 denominator files on
    EVERY call, and this sweep calls the definition ~180 times. The guard is a pure function
    of (rows, case_dir, denom_var), so it is memoised here. Before the cache is trusted, the
    real function is called twice on the same inputs and the two results are compared: if the
    guard were not pure, this would catch it and the sweep would refuse to run.

    (It is pure GIVEN a file order. Step 1 showed the file order itself varies between
    machines; memoising freezes one order for the whole sweep, which makes this sweep MORE
    deterministic than the shipped code, not less.)"""
    real = cp.denominator_guard
    cache = {}

    def patched(rows, case_dir, denom_var):
        k = (os.path.abspath(case_dir), denom_var, len(rows), id(rows))
        if k not in cache:
            cache[k] = real(rows, case_dir, denom_var)
        return cache[k]
    cp.denominator_guard = patched
    return real


def verify_guard_is_pure(real):
    case = os.path.join(HERE, "..", "CASES", "OLIVO-BACTROCERA-TOSCANA")
    rows, _, _ = cp.load_rows(case, -1002)
    a, ia = real(rows, case, 1)
    b, ib = real(rows, case, 1)
    same = len(a) == len(b) and ia == ib and \
        all(x is y for x, y in zip(a[:5000], b[:5000]))
    return {"CALLS_COMPARED": 2, "ROWS_KEPT": f"{len(a)}/{len(rows)}",
            "IDENTICAL": bool(same), "INFO": ia}


def cell_rows(region, crop, issue, case, var, as_of, pre):
    """One run of the shipped definition, with and without the effect floor."""
    try:
        on = cp.current_pressure(case, var, as_of, _pre=pre)
    except ValueError as e:
        return {"REFUSED": str(e)[:160]}, None
    try:
        off = cp.current_pressure(case, var, as_of, _pre=pre, min_positive_sites=0)
    except ValueError as e:
        off = None
    rows = []
    for p, v in sorted(on["PROVINCES"].items()):
        w = (off or {}).get("PROVINCES", {}).get(p, {})
        n_sites = v.get("n_sites") or 0
        val = v.get("VALUE")
        rows.append({
            "REGION": region, "CROP": crop, "ISSUE": issue, "DATE": as_of.isoformat(),
            "PROVINCE": p,
            "STATE": v.get("STATE"), "STATE_WITHOUT_FLOOR": w.get("STATE"),
            "VALUE": val, "PERCENTILE": v.get("PERCENTILE"),
            "BASELINE_N": v.get("BASELINE_N"), "BASELINE_MEDIAN": v.get("BASELINE_MEDIAN"),
            "n_sites": n_sites, "n_visits": v.get("n_visits"),
            "n_positive_sites": (round(val * n_sites, 1) if val is not None else None),
            "HIGHER_WITHHELD": v.get("HIGHER_WITHHELD")})
    meta = {"DATA_LATENCY_DAYS": on.get("DATA_LATENCY_DAYS"),
            "CUTOFF_LABEL": on.get("CUTOFF_LABEL"), "VALUE_MODE": on.get("VALUE_MODE"),
            "WINDOW": on.get("WINDOW"),
            "PUBLISHABLE_CLASSED": sum(1 for r in rows if r["STATE"] in CLASSED),
            "PROVINCES": len(rows)}
    return rows, meta


def main():
    real_guard = memoize_denominator_guard()
    purity = verify_guard_is_pure(real_guard)
    if not purity["IDENTICAL"]:
        raise SystemExit(f"REFUSED to run: denominator_guard is not pure -> {purity}")
    all_rows, by_date_meta, refusals = [], {}, {}
    for region, crop, issue, case, var in CASES:
        try:
            pre = cp.load_rows(case, var)
        except Exception as e:
            refusals[f"{crop}"] = f"LOAD_FAILED: {type(e).__name__}: {e}"
            continue
        for as_of in DATES_2026 + SAME_DAY_PRIOR:
            rows, meta = cell_rows(region, crop, issue, case, var, as_of, pre)
            k = f"{region}|{crop}|{issue}|{as_of.isoformat()}"
            if isinstance(rows, dict):
                refusals[k] = rows["REFUSED"]
                continue
            all_rows += rows
            by_date_meta[k] = meta

    # ── STEP 4 output ────────────────────────────────────────────────────────────────
    per_cell = collections.defaultdict(dict)
    for r in all_rows:
        per_cell[f"{r['REGION']}|{r['CROP']}|{r['ISSUE']}|{r['PROVINCE']}"][r["DATE"]] = r["STATE"]
    changing = {k: v for k, v in per_cell.items() if len({s for s in v.values()}) > 1}
    changing_2026 = {k: {d: s for d, s in v.items() if d.startswith("2026")}
                     for k, v in per_cell.items()}
    changing_2026 = {k: v for k, v in changing_2026.items() if len(set(v.values())) > 1}

    headline = {}
    for k, m in sorted(by_date_meta.items()):
        reg, crop, issue, d = k.split("|")
        if d.startswith("2026"):
            headline.setdefault(d, {})[crop] = {
                "PUBLISHABLE_CLASSED": f"{m['PUBLISHABLE_CLASSED']}/{m['PROVINCES']}",
                "DATA_LATENCY_DAYS": m["DATA_LATENCY_DAYS"]}

    step4 = {
        "GUARD_PURITY_CHECK": purity,
        "UNIT_OF_ANALYSIS": "REGION x CROP x ISSUE x DATE x PROVINCE",
        "DATES_EVALUATED_2026": [d.isoformat() for d in DATES_2026],
        "SAME_CALENDAR_DAY_PRIOR_SEASONS": [d.isoformat() for d in SAME_DAY_PRIOR],
        "REFUSALS": refusals,
        "HEADLINE_BY_DATE_2026": headline,
        "N_CELLS": len(per_cell),
        "CELLS_CHANGING_STATE_ACROSS_ALL_DATES": len(changing),
        "CELLS_CHANGING_STATE_WITHIN_2026": len(changing_2026),
        "CHANGING_WITHIN_2026": changing_2026,
        "ROWS": all_rows}
    json.dump(step4, open(os.path.join(HERE, "p4_cell_state_by_date.json"), "w"),
              indent=1, default=str)

    # ── STEP 5 output ────────────────────────────────────────────────────────────────
    withheld = [r for r in all_rows
                if r["STATE_WITHOUT_FLOOR"] == cp.HIGHER and r["STATE"] != cp.HIGHER]
    kept = [r for r in all_rows if r["STATE"] == cp.HIGHER]
    unaffected_high = [r for r in all_rows
                       if r["STATE"] == cp.HIGHER and r["STATE_WITHOUT_FLOOR"] == cp.HIGHER]

    def dist(rows, f):
        v = sorted(x for x in (f(r) for r in rows) if x is not None)
        if not v:
            return None
        return {"n": len(v), "min": v[0], "median": v[len(v) // 2], "max": v[-1]}

    # blind check: is the floor ever the ONLY thing standing between a broad base and HIGHER?
    withheld_with_broad_base = [r for r in withheld if (r["n_positive_sites"] or 0) >= 5]
    kept_with_thin_base = [r for r in kept if (r["n_positive_sites"] or 0) < 5]

    by_crop = collections.Counter((r["CROP"], "WITHHELD") for r in withheld)
    by_crop.update((r["CROP"], "KEPT_HIGHER") for r in kept)

    step5 = {
        "FLOOR": {"PARAMETER": "MIN_POSITIVE_SITES", "VALUE": cp.MIN_POSITIVE_SITES,
                  "RULE": "a HIGHER_THAN_USUAL rank is downgraded to TYPICAL unless "
                          "n_sites * INCIDENCE >= MIN_POSITIVE_SITES"},
        "SAMPLE": {"ROWS_EVALUATED": len(all_rows),
                   "CASES": sorted({r["CROP"] for r in all_rows}),
                   "DATES": len({r["DATE"] for r in all_rows}),
                   "NOTE": "includes dates, provinces and a crop (WHEAT) that were NOT part of "
                           "the sample that motivated the floor"},
        "HIGHER_WITHHELD_BY_FLOOR": len(withheld),
        "HIGHER_KEPT": len(kept),
        "POSITIVE_SITES_OF_WITHHELD": dist(withheld, lambda r: r["n_positive_sites"]),
        "POSITIVE_SITES_OF_KEPT": dist(unaffected_high, lambda r: r["n_positive_sites"]),
        "MONITORED_SITES_OF_WITHHELD": dist(withheld, lambda r: r["n_sites"]),
        "MONITORED_SITES_OF_KEPT": dist(unaffected_high, lambda r: r["n_sites"]),
        "FALSE_POSITIVE_TEST": {
            "DEFINITION": "a HIGHER call the floor KEPT although fewer than 5 sites are "
                          "positive — the floor failing open",
            "COUNT": len(kept_with_thin_base),
            "ROWS": kept_with_thin_base[:20]},
        "FALSE_NEGATIVE_TEST": {
            "DEFINITION": "a HIGHER call the floor WITHHELD although 5 or more sites are "
                          "positive — the floor failing closed on a broad base",
            "COUNT": len(withheld_with_broad_base),
            "ROWS": withheld_with_broad_base[:20]},
        "BY_CROP": {f"{k[0]}|{k[1]}": v for k, v in sorted(by_crop.items())},
        "WITHHELD_ROWS": withheld}
    json.dump(step5, open(os.path.join(HERE, "p5_effect_floor.json"), "w"),
              indent=1, default=str)

    print("=== STEP 4 ===")
    for d in sorted(headline):
        print(" ", d, json.dumps(headline[d]))
    print(f"  cells={step4['N_CELLS']}  changing_all_dates={len(changing)}  "
          f"changing_within_2026={len(changing_2026)}")
    print("  refusals:", json.dumps(refusals)[:400])
    print("\n=== STEP 5 ===")
    for k in ("HIGHER_WITHHELD_BY_FLOOR", "HIGHER_KEPT", "POSITIVE_SITES_OF_WITHHELD",
              "POSITIVE_SITES_OF_KEPT"):
        print(f"  {k} = {json.dumps(step5[k])}")
    print(f"  floor fails OPEN (kept, thin base) = {step5['FALSE_POSITIVE_TEST']['COUNT']}")
    print(f"  floor fails CLOSED (withheld, broad base) = {step5['FALSE_NEGATIVE_TEST']['COUNT']}")
    print("  by crop:", json.dumps(step5["BY_CROP"]))


if __name__ == "__main__":
    main()
