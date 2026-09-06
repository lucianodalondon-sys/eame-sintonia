#!/usr/bin/env python3
"""
CERT-V2 / STEP 3 — MUTATION TESTING OF GATES A..J.

A gate is not proved by passing. It is proved by FAILING when the property it claims to
protect is destroyed. This file destroys each property in turn and records what the SHIPPED
gate suite says.

METHOD
  Nothing in ENGINE/ or CASES/ is edited. Each mutation monkeypatches the shipped modules for
  the lifetime of one process, then the shipped gates.evaluate() is called unchanged and its
  ten verdicts are recorded. One process per mutation, so no mutation can leak into another.

READING THE RESULT
  KILLED    the target gate went to FAIL (or NOT_TESTABLE) under the mutation  -> gate works
  SURVIVED  the target gate still says PASS with its property destroyed        -> gate is blind
  For mutations whose target is ANY, the question is whether the SUITE notices at all.

Usage:  py p3_mutation.py <MUTATION_ID>      writes MUTANTS/<ID>.json
        py p3_mutation.py --list
"""
import json, os, sys, glob as globmod, random, shutil, datetime as dt, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "ENGINE")
CASEDIR = os.path.join(HERE, "..", "CASES")
OUT = os.path.join(HERE, "MUTANTS")
sys.path.insert(0, ENGINE)
sys.path.insert(0, CASEDIR)

AS_OF = dt.date(2026, 9, 6)


# ───────────────────────────────────────────────────────────── mutation recipes
# Each returns (as_of, cleanup) after patching. Imports happen inside so that the patch is
# applied to the same module objects gates.py will use.

def _mods():
    import current_pressure as cp
    import contracts, run_case, automation_probe as ap, answer_sheet
    return cp, contracts, run_case, ap, answer_sheet


def m01_role_check_removed():
    """A: the module stops refusing inadmissible evidence roles."""
    cp, C, _, _, _ = _mods()
    cp.assert_outcome_admissible = lambda case, var, role: role
    return AS_OF, None


def m02_role_laundered():
    """A: an inadmissible role is ACCEPTED and relabelled OFFICIAL_OBSERVATION on the way out."""
    cp, C, _, _, _ = _mods()
    cp.assert_outcome_admissible = \
        lambda case, var, role: C.EvidenceRole.OFFICIAL_OBSERVATION
    return AS_OF, None


def m03_cutoff_removed():
    """B: the time cutoff stops being applied, so future-dated rows reach published cells."""
    cp, _, _, _, _ = _mods()
    real = cp._window_value
    cp._window_value = lambda rows, scale, lo, hi, mode="ORDINAL": \
        real(rows, scale, lo, dt.date(2100, 1, 1), mode)
    return AS_OF, None


def m04_geography_collapsed_to_national():
    """C: every observation is relabelled with one national key."""
    cp, _, _, _, _ = _mods()
    real = cp.load_rows

    def patched(case_dir, var_id):
        rows, scale, meta = real(case_dir, var_id)
        for r in rows:
            r["nome_area"] = "ITALY"
        return rows, scale, meta
    cp.load_rows = patched
    return AS_OF, None


def m05_geography_inherited_from_one_province():
    """C: the fact inherits ONE location (as if the source institution's address were the
    location of the phenomenon). No 'ITALY' key appears, so the old any('ITALY') test could
    not have seen this."""
    cp, _, _, _, _ = _mods()
    real = cp.load_rows

    def patched(case_dir, var_id):
        rows, scale, meta = real(case_dir, var_id)
        for r in rows:
            r["nome_area"] = "FIRENZE"
        return rows, scale, meta
    cp.load_rows = patched
    return AS_OF, None


def m06_unknown_hidden():
    """D: UNKNOWN cells are dropped from the output instead of published."""
    cp, _, _, _, _ = _mods()
    real = cp.current_pressure

    def patched(*a, **k):
        r = real(*a, **k)
        r["PROVINCES"] = {p: v for p, v in r["PROVINCES"].items()
                          if v.get("STATE") not in (cp.UNKNOWN_NO_DATA, cp.UNKNOWN_NO_BASELINE)}
        return r
    cp.current_pressure = patched
    return AS_OF, None


def m07_missing_read_as_zero():
    """D: FAILURE == ZERO. An unreadable value becomes a confirmed absence of the issue."""
    cp, _, _, _, _ = _mods()
    real = cp.read_value
    cp.read_value = lambda r, scale, mode: (0.0 if real(r, scale, mode) is None
                                            else real(r, scale, mode))
    return AS_OF, None


def m08_nondeterministic_output():
    """E: the module stops being replayable."""
    cp, _, _, _, _ = _mods()
    real = cp.current_pressure

    def patched(*a, **k):
        r = real(*a, **k)
        r["_NONCE"] = random.random()
        return r
    cp.current_pressure = patched
    return AS_OF, None


def m09_file_order_shuffled():
    """E: the DEFECT FOUND IN STEP 1, applied deliberately. The published numbers become a
    property of the directory listing order. Does the gate that certifies REPRODUCIBLE see it?"""
    cp, _, _, _, _ = _mods()
    real = globmod.glob
    rnd = random.Random(4242)
    cp.glob.glob = lambda p, **k: (lambda L: (rnd.shuffle(L), L)[1])(list(real(p, **k)))
    return AS_OF, None


def m10_label_becomes_parameter_artefact():
    """F: the published class starts depending on the window parameter."""
    cp, _, _, _, _ = _mods()
    real = cp._window_value

    def patched(rows, scale, lo, hi, mode="ORDINAL"):
        v = real(rows, scale, lo, hi, mode)
        if v is None:
            return v
        span = (hi - lo).days
        v["INCIDENCE"] = round(min(1.0, max(0.0, v["INCIDENCE"] + ((span % 7) - 3) * 0.12)), 4)
        return v
    cp._window_value = patched
    return AS_OF, None


def m11_one_class_for_every_season():
    """G: the statement stops discriminating — every season-cell gets the same class."""
    cp, _, _, _, _ = _mods()
    real = cp.hindcast
    cp.hindcast = lambda *a, **k: {y: {p: cp.TYPICAL for p in row}
                                   for y, row in real(*a, **k).items()}
    return AS_OF, None


def m12_classes_balanced_positive_control():
    """G POSITIVE CONTROL: classes spread evenly. A gate that cannot PASS is as broken as one
    that cannot FAIL, and G currently fails on the shipped data."""
    cp, _, _, _, _ = _mods()
    real = cp.hindcast

    def patched(*a, **k):
        h = real(*a, **k)
        cyc = [cp.HIGHER, cp.TYPICAL, cp.LOWER]
        out, i = {}, 0
        for y, row in h.items():
            out[y] = {}
            for p, s in row.items():
                out[y][p] = cyc[i % 3] if s in (cp.HIGHER, cp.TYPICAL, cp.LOWER) else s
                i += 1
        return out
    cp.hindcast = patched
    return AS_OF, None


def m13_refresh_returns_all_nulls():
    """H: the silent failure this project was built to catch — HTTP 200, full row count,
    every value null."""
    _, _, _, ap, _ = _mods()
    real = ap.fetch

    def patched(crop, schema, var, year, timeout=90):
        r = real(crop, schema, var, year, timeout)
        for row in r.get("rows") or []:
            if isinstance(row, dict):
                row["val"] = None
        r["non_null_values"] = 0
        r["SILENT_FAILURE"] = "FULL_ROWCOUNT_BUT_EVERY_VALUE_NULL"
        r["ok"] = False
        return r
    ap.fetch = patched
    return AS_OF, None


def m14_source_unreachable():
    """H: the endpoint dies."""
    _, _, _, ap, _ = _mods()
    ap.fetch = lambda crop, schema, var, year, timeout=90: \
        {"HTTP": None, "ok": False, "error": "URLError: simulated dead endpoint",
         "seconds": 0.0, "rows": []}
    return AS_OF, None


def m15_archive_frozen_400_days_ago():
    """H: the archive stops being current while everything else keeps working."""
    cp, _, _, _, _ = _mods()
    real = cp.load_rows
    cut = AS_OF - dt.timedelta(days=400)

    def patched(case_dir, var_id):
        rows, scale, meta = real(case_dir, var_id)
        return [r for r in rows if r["_d"] <= cut], scale, meta
    cp.load_rows = patched
    return AS_OF, None


def m16_clock_moves_one_year_archive_does_not():
    """H: NOT a patch. The shipped as_of is a HARDCODED CONSTANT (gates.evaluate default
    2026-09-06). This asks the shipped suite the same question one year later with the same
    archive. A capability called CURRENT_PRESSURE must go red."""
    return dt.date(2027, 9, 6), None


def m17_unseen_case_raw_file_corrupted():
    """I: a raw file of the generalisation case no longer matches its recorded sha256.

    Applied IN PROCESS (builtins.open returns altered bytes for that one path) rather than by
    editing the file, so this mutation is safe to run in parallel with the others and cannot
    leave the repository dirty if the process dies."""
    import builtins, io
    b = builtins.open
    targ = os.path.normcase(os.path.abspath(
        os.path.join(CASEDIR, "FRUMENTO-SEPTORIA-TOSCANA", "RAW", "c19_s74_v372_2020.json")))

    def patched(p, *a, **k):
        try:
            same = os.path.normcase(os.path.abspath(str(p))) == targ
        except Exception:
            same = False
        if same:
            raw = b(p, "rb").read()
            return io.BytesIO(raw + b" ") if (a and "b" in str(a[0])) else \
                io.StringIO(raw.decode("utf-8"))
        return b(p, *a, **k)
    builtins.open = patched

    def cleanup():
        builtins.open = b
    return AS_OF, cleanup


def m18_unseen_case_series_degenerate():
    """I: the unseen case decodes to a constant — the shape of a decoding failure."""
    _, _, rc, _, _ = _mods()
    real = rc.season_outcomes

    def patched(d, var_id, min_sites=10):
        out, meta = real(d, var_id, min_sites)
        for y in out:
            out[y]["SITE_INCIDENCE"] = 1.0
        return out, meta
    rc.season_outcomes = patched
    sys.modules["run_case"].season_outcomes = patched
    return AS_OF, None


def m19_gate_j_pointed_at_the_in_repo_copy():
    """J: NOT a destructive mutation — a repair probe. The gate reads a HARDCODED ABSOLUTE
    PATH under /home/user while a byte-identical copy is versioned in this repository. This
    run points it at the repo copy and records the answer the gate would have given."""
    import gates as G
    real = os.path.exists
    repo = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..",
                                        "italia-portale", "client",
                                        "meeting-intelligence-snapshot.json"))
    hard = "/home/user/eame-sintonia/italia-portale/client/meeting-intelligence-snapshot.json"
    G.os.path.exists = lambda p: (real(repo) if p == hard else real(p))
    realopen = G.open if hasattr(G, "open") else open
    import builtins
    b = builtins.open
    builtins.open = lambda p, *a, **k: (b(repo, *a, **k) if p == hard else b(p, *a, **k))

    def cleanup():
        builtins.open = b
        G.os.path.exists = real
    return AS_OF, cleanup


# ── cross-cutting: properties NO single gate claims, which the SUITE should still catch ──

def m20_values_replaced_by_code_ids():
    """CODE IS NOT VALUE. Every observed value is replaced by an identifier from the source's
    own code table. The wheat case proved this can produce a confident, wrong agronomic
    sentence."""
    cp, _, _, _, _ = _mods()
    real = cp.load_rows

    def patched(case_dir, var_id):
        rows, scale, meta = real(case_dir, var_id)
        idx = json.load(open(os.path.join(case_dir, "collection_index.json")))
        ids = [str(c.get("id_survey_code")) for c in (idx.get("codes") or [])]
        if ids:
            for i, r in enumerate(rows):
                r["val"] = ids[i % len(ids)]
        return rows, scale, meta
    cp.load_rows = patched
    return AS_OF, None


def m21_crop_swapped():
    """The olive case is served the VINE archive. Region, issue name and every label stay
    put; only the biology underneath changes."""
    cp, _, _, _, _ = _mods()
    real = cp.load_rows
    vine = os.path.join(CASEDIR, "VITE-OIDIO-TOSCANA")

    def patched(case_dir, var_id):
        if "OLIVO" in case_dir:
            return real(vine, 39)
        return real(case_dir, var_id)
    cp.load_rows = patched
    return AS_OF, None


def m22_dates_shifted_one_year():
    """TIME. Every observation is moved forward 365 days: a 2025 season is served as 2026."""
    cp, _, _, _, _ = _mods()
    real = cp.load_rows

    def patched(case_dir, var_id):
        rows, scale, meta = real(case_dir, var_id)
        for r in rows:
            r["_d"] = r["_d"] + dt.timedelta(days=365)
        return rows, scale, meta
    cp.load_rows = patched
    return AS_OF, None


def m23_source_url_removed():
    """PROVENANCE. The evidence chain loses the source it points at."""
    cp, _, _, _, _ = _mods()
    real = cp.load_rows

    def patched(case_dir, var_id):
        rows, scale, meta = real(case_dir, var_id)
        meta["api"] = None
        meta["hashes"] = {}
        return rows, scale, meta
    cp.load_rows = patched
    return AS_OF, None


def m24_signal_inverted():
    """The measurement is inverted: presence becomes absence and absence becomes presence."""
    cp, _, _, _, _ = _mods()
    real = cp.read_value

    def patched(r, scale, mode):
        v = real(r, scale, mode)
        return None if v is None else (100.0 - v if v > 1 else 1.0 - v)
    cp.read_value = patched
    return AS_OF, None


def m25_universe_zeroed():
    """The archive is emptied. Nothing may be published, and nothing may be published as
    'no disease'."""
    cp, _, _, _, _ = _mods()
    real = cp.load_rows

    def patched(case_dir, var_id):
        rows, scale, meta = real(case_dir, var_id)
        return [], scale, meta
    cp.load_rows = patched
    return AS_OF, None


def m26_evidence_link_broken():
    """Every cell keeps its number and loses the raw file it was computed from."""
    cp, _, _, _, _ = _mods()
    real = cp.current_pressure

    def patched(*a, **k):
        r = real(*a, **k)
        for p, v in r["PROVINCES"].items():
            if isinstance(v, dict) and "EVIDENCE" in v:
                v["EVIDENCE"] = {}
        return r
    cp.current_pressure = patched
    return AS_OF, None


MUTATIONS = {
    "M01": ("A", "the module stops refusing inadmissible evidence roles", m01_role_check_removed),
    "M02": ("A", "an inadmissible role is accepted and relabelled on the way out", m02_role_laundered),
    "M03": ("B", "the time cutoff is removed", m03_cutoff_removed),
    "M04": ("C", "geography collapsed to one national key", m04_geography_collapsed_to_national),
    "M05": ("C", "every fact inherits one province", m05_geography_inherited_from_one_province),
    "M06": ("D", "UNKNOWN cells hidden from the output", m06_unknown_hidden),
    "M07": ("D", "missing read as zero (FAILURE == ZERO)", m07_missing_read_as_zero),
    "M08": ("E", "output made non-deterministic", m08_nondeterministic_output),
    "M09": ("E", "file order shuffled (the real Step-1 defect)", m09_file_order_shuffled),
    "M10": ("F", "the label becomes a parameter artefact", m10_label_becomes_parameter_artefact),
    "M11": ("G", "one class for every season-cell", m11_one_class_for_every_season),
    "M12": ("G", "POSITIVE CONTROL: classes balanced", m12_classes_balanced_positive_control),
    "M13": ("H", "refresh returns full rowcount, all values null", m13_refresh_returns_all_nulls),
    "M14": ("H", "source unreachable", m14_source_unreachable),
    "M15": ("H", "archive frozen 400 days ago", m15_archive_frozen_400_days_ago),
    "M16": ("H", "clock moves one year, archive does not", m16_clock_moves_one_year_archive_does_not),
    "M17": ("I", "unseen case raw file no longer matches its sha256", m17_unseen_case_raw_file_corrupted),
    "M18": ("I", "unseen case decodes to a constant", m18_unseen_case_series_degenerate),
    "M19": ("J", "REPAIR PROBE: gate J pointed at the in-repo copy", m19_gate_j_pointed_at_the_in_repo_copy),
    "M20": ("ANY", "observed values replaced by code ids", m20_values_replaced_by_code_ids),
    "M21": ("ANY", "crop swapped: olive case served the vine archive", m21_crop_swapped),
    "M22": ("ANY", "every observation date shifted one year forward", m22_dates_shifted_one_year),
    "M23": ("ANY", "source url and file hashes removed", m23_source_url_removed),
    "M24": ("ANY", "signal inverted", m24_signal_inverted),
    "M25": ("ANY", "universe zeroed", m25_universe_zeroed),
    "M26": ("ANY", "evidence link broken on every cell", m26_evidence_link_broken),
}

BASELINE = {"A_OUTCOME_IS_OBSERVED": "PASS", "B_NOT_SOLD_AS_FORECAST": "PASS",
            "C_REGIONAL_NOT_NATIONAL": "PASS", "D_UNKNOWN_IS_VISIBLE": "PASS",
            "E_REPRODUCIBLE": "PASS", "F_LABEL_NOT_PARAMETER_ARTEFACT": "PASS",
            "G_DISCRIMINATES_BETWEEN_SEASONS": "FAIL", "H_REFRESHABLE_WITHOUT_RESEARCH": "PASS",
            "I_GENERALIZES": "PASS", "J_NOT_DUPLICATE": "FAIL"}

LETTER = {k[0]: k for k in BASELINE}


def run_one(mid):
    target, desc, recipe = MUTATIONS[mid]
    os.makedirs(OUT, exist_ok=True)
    rec = {"ID": mid, "TARGET_GATE": target, "PROPERTY_DESTROYED": desc,
           "BASELINE_VERDICTS": BASELINE}
    cleanup = None
    try:
        as_of, cleanup = recipe()
        import gates as G
        r = G.evaluate(as_of=as_of)
        v = {k: x["VERDICT"] for k, x in r["GATES"].items()}
        rec["AS_OF"] = as_of.isoformat()
        rec["VERDICTS"] = v
        rec["EVIDENCE_OF_TARGET"] = (r["GATES"].get(LETTER.get(target, ""), {}) or {}).get("EVIDENCE")
        rec["CHANGED_GATES"] = sorted(k for k in v if v[k] != BASELINE[k])
        if target == "ANY":
            broke = [k for k in v if v[k] != BASELINE[k] and v[k] != "PASS"]
            rec["OUTCOME"] = "DETECTED_BY_SUITE" if broke else "UNDETECTED_BY_SUITE"
            rec["DETECTED_BY"] = broke
        elif mid == "M12":
            rec["OUTCOME"] = ("POSITIVE_CONTROL_OK" if v[LETTER[target]] == "PASS"
                              else "POSITIVE_CONTROL_FAILED")
        elif mid == "M19":
            rec["OUTCOME"] = "REPAIR_PROBE"
        else:
            g = LETTER[target]
            rec["OUTCOME"] = ("KILLED" if v[g] != "PASS" and BASELINE[g] == "PASS" else
                              "ALREADY_FAILING" if BASELINE[g] != "PASS" else "SURVIVED")
    except Exception as e:
        rec["OUTCOME"] = "MUTATION_RAISED"
        rec["ERROR"] = f"{type(e).__name__}: {e}"
    finally:
        if cleanup:
            cleanup()
    json.dump(rec, open(os.path.join(OUT, f"{mid}.json"), "w"), indent=1, default=str)
    print(json.dumps({k: rec[k] for k in ("ID", "TARGET_GATE", "OUTCOME") if k in rec}))
    return rec


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        for k, (t, d, _) in MUTATIONS.items():
            print(f"{k}  gate {t:3s}  {d}")
    else:
        run_one(sys.argv[1])
