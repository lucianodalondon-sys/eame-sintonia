#!/usr/bin/env python3
"""
RT6 — INDEPENDENT RED-TEAM MUTATIONS, aimed at the five gates the certification reports as
healthy (A, C, F, H, I). Written by someone who did not write gates.py and did not write
p3_mutation.py.

Same discipline as p3_mutation.py: nothing in ENGINE/ or CASES/ is edited, one process per
mutation, the SHIPPED gates.evaluate() is called unchanged.

Usage:  py rt6_mutate.py R01        -> REDTEAM/R01.json
        py rt6_mutate.py --list
"""
import json, os, sys, math, random, collections, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.dirname(HERE)
ENGINE = os.path.join(CERT, "..", "ENGINE")
CASEDIR = os.path.join(CERT, "..", "CASES")
sys.path.insert(0, ENGINE)
sys.path.insert(0, CASEDIR)

AS_OF = dt.date(2026, 9, 6)


def _mods():
    import current_pressure as cp
    import contracts, run_case, automation_probe as ap, answer_sheet
    return cp, contracts, run_case, ap, answer_sheet


# ─────────────────────────────────────────────────────────────────── recipes

def r01_published_cells_harmonised():
    """C. The PUBLISHED product stops distinguishing provinces: on the certified date every
    classified province of a case carries the modal class, so a single national sentence would
    be equivalent. History is left completely untouched, because gate C's predicate reads
    hindcast(), not the published cells. If gate C is about the published unit it must fail."""
    cp, _, _, _, _ = _mods()
    real = cp.current_pressure

    def patched(case_dir, var_id, as_of, *a, **k):
        r = real(case_dir, var_id, as_of, *a, **k)
        if as_of != AS_OF:                       # history untouched: only today is harmonised
            return r
        cls = [v.get("STATE") for v in r["PROVINCES"].values()
               if v.get("STATE") in (cp.HIGHER, cp.TYPICAL, cp.LOWER)]
        if cls:
            modal = collections.Counter(cls).most_common(1)[0][0]
            for v in r["PROVINCES"].values():
                if v.get("STATE") in (cp.HIGHER, cp.TYPICAL, cp.LOWER):
                    v["STATE"] = modal
        return r
    cp.current_pressure = patched
    return AS_OF, None


def r02_one_case_label_is_pure_parameter_artefact():
    """F. The vine case's ten labels become a 100% parameter artefact — agreement 0.000 across
    the whole 135-point grid — while the olive case is left alone. Gate F's predicate is
    `any(v >= STAB_MIN ...)`, so it should not notice. Gate H's own docstring records that a
    list-truthiness/all() confusion was fixed there; the same confusion is still in F."""
    cp, _, _, _, _ = _mods()
    real = cp.sensitivity

    def patched(case_dir, var_id, as_of, metric="INCIDENCE"):
        s = real(case_dir, var_id, as_of, metric)
        if "VITE" in str(case_dir).upper():
            for p in s["PER_PROVINCE"]:
                s["PER_PROVINCE"][p]["AGREEMENT"] = 0.0
            s["MEAN_AGREEMENT"] = 0.0
        return s
    cp.sensitivity = patched
    return AS_OF, None


def r03_generalisation_result_fabricated():
    """I. The unseen 4th case is never actually run: season_outcomes returns a stub that ignores
    the case directory entirely and hands back 14 seasons of pseudo-random SITE_INCIDENCE. The
    sha256 chain gate I checks still passes, because the FILES are untouched — only the claim
    that the pipeline processed them is destroyed."""
    _, _, rc, _, _ = _mods()

    def patched(d, var_id, min_sites=10):
        rnd = random.Random(20260906)
        out = {y: {"n_visits": 400, "n_sites": 25,
                   "SITE_INCIDENCE": round(rnd.random(), 4),
                   "SITE_MAX_MEAN": 1.0, "n_provinces": 6, "n_comuni": 30,
                   "n_orgs": 3, "pct_georef": 50.0}
               for y in range(2010, 2024)}
        return out, {"derivation_methods": ["STUB_NEVER_READ_THE_CASE"],
                     "unresolved_labels": [], "numeric_fallback": False}
    rc.season_outcomes = patched
    sys.modules["run_case"].season_outcomes = patched
    return AS_OF, None


def r04_refresh_answers_with_the_wrong_series():
    """H. Every live refresh of a real case is answered with the OLIVE series, whatever was
    asked for. HTTP 200, ok:true, 2,870 non-null values, and for the vine case the row count
    GROWS by 413 — which gate H reads as the success case. The negative control is left alone so
    the detector still trips. If gate H certifies 'this case can be refreshed' it must fail; if
    it only certifies 'an endpoint answered', it passes."""
    _, _, _, ap, _ = _mods()
    real = ap.fetch

    def patched(crop, schema, var, year, timeout=90):
        if var == 50:                       # the negative control must still trip
            return real(crop, schema, var, year, timeout)
        return real(2, 1, -1002, year, timeout)
    ap.fetch = patched
    return AS_OF, None


def r05_every_value_replaced_by_a_calendar_model():
    """A. The numbers become a MODEL and the label stays OFFICIAL_OBSERVATION.

    current_pressure's own docstring says: 'Fed a rainfall series it would have stamped a
    weather model's number as an official field observation and passed its own gate A.' The fix
    checks (1) the role string and (2) that the variable id is declared in the survey schema.
    Neither looks at the numbers. Here every observed code is overwritten by a deterministic
    sinusoid of the day-of-year — a pure calendar model, no observation left in the file — while
    the variable id, the role, the case directory and every refusal stay exactly as shipped."""
    cp, _, _, _, _ = _mods()
    real = cp.load_rows

    def patched(case_dir, var_id):
        rows, scale, meta = real(case_dir, var_id)
        codes = sorted(scale, key=lambda k: scale[k]["ordinal"])
        if codes:
            n = len(codes) - 1
            for r in rows:
                doy = r["_d"].timetuple().tm_yday
                frac = math.sin(2 * math.pi * doy / 365.0) * 0.5 + 0.5
                r["val"] = codes[int(round(frac * n))]
        return rows, scale, meta
    cp.load_rows = patched
    return AS_OF, None


MUTATIONS = {
    "R01": ("C", "published cells harmonised to one class per case; history untouched",
            r01_published_cells_harmonised),
    "R02": ("F", "one of the two cases' labels made a 100% parameter artefact",
            r02_one_case_label_is_pure_parameter_artefact),
    "R03": ("I", "the unseen case is never run; season_outcomes is a stub",
            r03_generalisation_result_fabricated),
    "R04": ("H", "every refresh answers with the wrong series (olive for both)",
            r04_refresh_answers_with_the_wrong_series),
    "R05": ("A", "every value replaced by a calendar model; role and schema untouched",
            r05_every_value_replaced_by_a_calendar_model),
}

BASELINE = {"A_OUTCOME_IS_OBSERVED": "PASS", "B_NOT_SOLD_AS_FORECAST": "PASS",
            "C_REGIONAL_NOT_NATIONAL": "PASS", "D_UNKNOWN_IS_VISIBLE": "PASS",
            "E_REPRODUCIBLE": "PASS", "F_LABEL_NOT_PARAMETER_ARTEFACT": "PASS",
            "G_DISCRIMINATES_BETWEEN_SEASONS": "FAIL", "H_REFRESHABLE_WITHOUT_RESEARCH": "PASS",
            "I_GENERALIZES": "PASS", "J_NOT_DUPLICATE": "FAIL"}
LETTER = {k[0]: k for k in BASELINE}


def run_one(mid):
    target, desc, recipe = MUTATIONS[mid]
    # gates.py resolves its two cases as the RELATIVE path "../CASES/...", so evaluate() only
    # works from a directory that is a sibling of CASES. p3_mutation.py happens to satisfy that
    # because it lives in CERT-V2; from REDTEAM/ it does not. Recorded, then worked around.
    os.chdir(CERT)
    rec = {"ID": mid, "TARGET_GATE": target, "PROPERTY_DESTROYED": desc,
           "BASELINE_VERDICTS": BASELINE, "CWD_FOR_RUN": os.getcwd()}
    cleanup = None
    try:
        as_of, cleanup = recipe()
        import gates as G
        r = G.evaluate(as_of=as_of)
        v = {k: x["VERDICT"] for k, x in r["GATES"].items()}
        rec["AS_OF"] = as_of.isoformat()
        rec["VERDICTS"] = v
        rec["EVIDENCE_OF_TARGET"] = (r["GATES"].get(LETTER[target], {}) or {}).get("EVIDENCE")
        rec["CHANGED_GATES"] = sorted(k for k in v if v[k] != BASELINE[k])
        g = LETTER[target]
        rec["OUTCOME"] = ("KILLED" if v[g] != "PASS" and BASELINE[g] == "PASS" else
                          "ALREADY_FAILING" if BASELINE[g] != "PASS" else "SURVIVED")
        rec["SUITE_TOTALS"] = {"PASS": r["PASS"], "FAIL": r["FAIL"],
                               "NOT_TESTABLE": r["NOT_TESTABLE"],
                               "DESERVES_FUTURE_INTEGRATION": r["DESERVES_FUTURE_INTEGRATION"]}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        rec["OUTCOME"] = ("SUITE_CRASHED_NO_VERDICT"
                          if ("gates.py" in tb or "current_pressure.py" in tb)
                          else "MUTATION_RAISED")
        rec["ERROR"] = f"{type(e).__name__}: {e}"
        rec["TRACEBACK_TAIL"] = tb.strip().splitlines()[-8:]
    finally:
        if cleanup:
            cleanup()
    json.dump(rec, open(os.path.join(HERE, f"{mid}.json"), "w"), indent=1, default=str)
    print(json.dumps({k: rec[k] for k in ("ID", "TARGET_GATE", "OUTCOME") if k in rec}))
    return rec


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        for k, (t, d, _) in MUTATIONS.items():
            print(f"{k}  gate {t}  {d}")
    else:
        run_one(sys.argv[1])
