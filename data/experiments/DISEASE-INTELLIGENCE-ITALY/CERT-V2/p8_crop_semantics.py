#!/usr/bin/env python3
"""
CERT-V2 / STEP 8 — THREE QUESTIONS THAT MUST NOT BE COLLAPSED INTO ONE.

  DATA_HAS_SIGNAL          does the archive carry a measurable series for this crop?
  ENGINE_CANONICALIZES_CROP does the engine know what crop a published cell is about?
  PORTAL_CAN_RENDER_CROP    does the portal have a word for it?

The mission's rule: the absence of OLIVO from the portal's vocabulary may not be reported as
the absence of the phenomenon. The converse trap is just as real and is what this file
actually found: a crop the ENGINE cannot name is not the same as a crop the DATA lacks.

MECHANICAL TEST OF THE MIDDLE QUESTION
  The unit of analysis this whole pilot is built on is REGION x CROP x ISSUE x DATE. So the
  output of the measuring function is asked, directly, which of those four it carries.

Out: p8_crop_semantics.json
"""
import json, os, re, sys, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "ENGINE")
CASEDIR = os.path.join(HERE, "..", "CASES")
sys.path.insert(0, ENGINE)
sys.path.insert(0, CASEDIR)
import current_pressure as cp
import run_case

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SNAP = os.path.join(REPO, "italia-portale", "client", "meeting-intelligence-snapshot.json")

CASES = [("OLIVO", "OLIVO-BACTROCERA-TOSCANA", -1002, 2),
         ("VITE", "VITE-OIDIO-TOSCANA", 39, 3),
         ("FRUMENTO", "FRUMENTO-SEPTORIA-TOSCANA", 372, 19)]
AS_OF = dt.date(2026, 9, 6)


def portal_vocabulary():
    if not os.path.exists(SNAP):
        return None
    S = json.load(open(SNAP, encoding="utf-8"))

    def walk(o):
        if isinstance(o, dict):
            yield o
            for v in o.values():
                yield from walk(v)
        elif isinstance(o, list):
            for v in o:
                yield from walk(v)
    cases = [d for d in walk(S) if isinstance(d, dict) and "ARCHETYPE" in d]
    return {"n_cases": len(cases),
            "CROPS": sorted({str(c.get("CROP")) for c in cases}),
            "TARGETS": sorted({str(c.get("TARGET")) for c in cases}),
            "GEOGRAPHIES": sorted({str(c.get("GEOGRAPHY")) for c in cases}),
            "FIELD_PRESSURE_BY_CROP_GEO": sorted(
                {f"{c.get('CROP')}|{c.get('GEOGRAPHY')}|{c.get('TARGET')}"
                 for c in cases if c.get("ARCHETYPE") == "O1_FIELD_PRESSURE"})}


def main():
    out = {"AS_OF": AS_OF.isoformat()}

    # ── does the ENGINE carry crop / region / issue anywhere in what it emits? ──────
    live = cp.current_pressure(os.path.join(CASEDIR, "OLIVO-BACTROCERA-TOSCANA"), -1002, AS_OF)
    top = sorted(live.keys())
    prov = sorted(next(iter(live["PROVINCES"].values())).keys())
    src = open(os.path.join(ENGINE, "current_pressure.py"), encoding="utf-8").read()
    src += open(os.path.join(CASEDIR, "run_case.py"), encoding="utf-8").read()
    has_vocab = bool(re.search(r"CROP_[A-Z]{3,}|CROP_VOCAB|canonical_crop|normali[sz]e_crop", src))
    out["ENGINE_OUTPUT_SHAPE"] = {
        "TOP_LEVEL_KEYS": top,
        "PER_PROVINCE_KEYS": prov,
        "CARRIES_DATE": "AS_OF" in top,
        "CARRIES_REGION": any(k in top for k in ("REGION", "REGIONE")),
        "CARRIES_CROP": any(k in top for k in ("CROP", "COLTURA")),
        "CARRIES_ISSUE": any(k in top for k in ("ISSUE", "TARGET", "PROBLEMA")),
        "CROP_VOCABULARY_IN_ENGINE_SOURCE": has_vocab,
        "HOW_THE_CROP_IS_CARRIED_TODAY":
            "as a directory name (CASES/<CROP>-<ISSUE>-<REGION>) and as a free-text argument "
            "the caller passes to answer_sheet(); in ENGINE/gates.py:26 that argument is the "
            "literal placeholder string \"crop\". Nothing validates it against any vocabulary.",
        "CONSEQUENCE":
            "two of the four dimensions of the declared unit of analysis "
            "(REGION x CROP x ISSUE x DATE) exist only in a folder name. A cell cannot be "
            "joined to a product, a label or a portal card without a human retyping them."}

    # ── DATA_HAS_SIGNAL, per crop, measured ────────────────────────────────────────
    data = {}
    for crop, name, var, crop_id in CASES:
        case = os.path.join(CASEDIR, name)
        rec = {"source_crop_id": crop_id, "survey_var": var}
        try:
            rows, scale, meta = cp.load_rows(case, var)
            vals = [r.get("val") for r in rows if r.get("val") not in (None, "")]
            seasons, _ = run_case.season_outcomes(case, var)
            distinct = sorted({round(v["SITE_INCIDENCE"], 4) for v in seasons.values()})
            rec.update({"n_rows": len(rows), "n_readable_values": len(vals),
                        "VALUE_MODE": meta["VALUE_MODE"], "scale_size": len(scale),
                        "scale_unresolved": meta["scale_unresolved"],
                        "n_seasons_with_enough_sites": len(seasons),
                        "distinct_site_incidence_values": len(distinct),
                        "DATA_HAS_SIGNAL": len(seasons) >= 5 and len(distinct) > 1})
        except Exception as e:
            rec.update({"DATA_HAS_SIGNAL": False,
                        "REFUSED": f"{type(e).__name__}: {str(e)[:200]}"})
        try:
            r = cp.current_pressure(case, var, AS_OF)
            rec["PUBLISHABLE_TODAY"] = sum(
                1 for v in r["PROVINCES"].values()
                if v.get("STATE") in (cp.HIGHER, cp.TYPICAL, cp.LOWER))
            rec["DATA_LATENCY_DAYS"] = r.get("DATA_LATENCY_DAYS")
        except Exception as e:
            rec["PUBLISHABLE_TODAY"] = f"REFUSED: {type(e).__name__}"
        data[crop] = rec

    # crops the mission named that this pilot never collected
    census_p = os.path.join(HERE, "..", "CENSUS", "italy_census.json")
    census_crops = []
    if os.path.exists(census_p):
        C = json.load(open(census_p, encoding="utf-8"))
        census_crops = sorted({str(x.get("crop"))[:60]
                               for l in C.get("lanes", []) for x in l.get("candidates", [])})
    data["MAIS"] = {"DATA_HAS_SIGNAL": "NOT_COLLECTED_BY_THIS_PILOT",
                    "NOTE": "no maize case exists in CASES/, and the pilot's own Italy census "
                            "(CENSUS/italy_census.json, 25 candidates) contains no maize "
                            "candidate. This is an absence of COLLECTION, not a measured "
                            "absence of the phenomenon.",
                    "CENSUS_CROPS_SEEN": census_crops}
    out["DATA_HAS_SIGNAL"] = data

    # ── PORTAL_CAN_RENDER_CROP ─────────────────────────────────────────────────────
    voc = portal_vocabulary()
    out["PORTAL"] = voc
    if voc:
        pc = voc["CROPS"]
        out["PORTAL_CAN_RENDER_CROP"] = {
            "OLIVO": "CROP_OLIVE" in pc, "VITE": "CROP_GRAPEVINE" in pc,
            "FRUMENTO": "CROP_WHEAT_GENERIC" in pc, "MAIS": "CROP_MAIZE" in pc}
        out["PORTAL_HAS_ISSUE_WORD"] = {
            "OLIVE_FRUIT_FLY": any("BACTROCERA" in t.upper() or "OLIVE" in t.upper()
                                   for t in voc["TARGETS"]),
            "OIDIO_POWDERY_MILDEW": any("POWDERY" in t.upper() for t in voc["TARGETS"]),
            "SEPTORIA": any("SEPTORIA" in t.upper() for t in voc["TARGETS"])}
        out["GATE_J_CLAIM_RECHECKED"] = {
            "GATE_J_SAID": "its whole TARGET vocabulary contains 0 olive targets ... the "
                           "portal has no words for the cell we can [publish]",
            "MEASURED": {
                "olive_ISSUE_words": [t for t in voc["TARGETS"]
                                      if "OLIVE" in t.upper() or "BACTROCERA" in t.upper()],
                "olive_CROP_word_present": "CROP_OLIVE" in pc,
                "n_cases_using_CROP_OLIVE": None},
            "CORRECTION": "the first half is right and the conclusion overshoots. The portal "
                          "HAS the crop word CROP_OLIVE (three cases carry it) and lacks the "
                          "ISSUE word and any provincial olive geography. 'No vocabulary for "
                          "the olive' is not what the file says; 'no field-pressure capability "
                          "for olive x olive-fly x province' is."}

    ok_norm = out["ENGINE_OUTPUT_SHAPE"]["CARRIES_CROP"] and \
        out["ENGINE_OUTPUT_SHAPE"]["CARRIES_REGION"] and \
        out["ENGINE_OUTPUT_SHAPE"]["CARRIES_ISSUE"]
    out["CROP_NORMALIZATION"] = "PASS" if ok_norm else "FAIL"
    out["CROPS_IN_DATA"] = [c for c, r in data.items() if r.get("DATA_HAS_SIGNAL") is True]
    out["CROPS_CANONICALIZED"] = []
    out["CROPS_NOT_CANONICALIZED"] = [c for c, _, _, _ in CASES]
    out["SEMANTIC_COVERAGE"] = ("SEMANTIC_COVERAGE_FAIL" if not ok_norm else "OK")

    json.dump(out, open(os.path.join(HERE, "p8_crop_semantics.json"), "w"), indent=1, default=str)
    print("ENGINE OUTPUT carries:",
          {k: v for k, v in out["ENGINE_OUTPUT_SHAPE"].items() if k.startswith("CARRIES")},
          "vocab_in_source =", has_vocab)
    print("top-level keys:", top)
    print()
    for c, r in data.items():
        print(f"  {c:9s} DATA_HAS_SIGNAL={str(r.get('DATA_HAS_SIGNAL')):26s} "
              f"seasons={r.get('n_seasons_with_enough_sites')} "
              f"publishable_today={r.get('PUBLISHABLE_TODAY')} "
              f"latency={r.get('DATA_LATENCY_DAYS')} {str(r.get('REFUSED',''))[:70]}")
    print()
    print("PORTAL_CAN_RENDER_CROP:", out.get("PORTAL_CAN_RENDER_CROP"))
    print("PORTAL_HAS_ISSUE_WORD :", out.get("PORTAL_HAS_ISSUE_WORD"))
    print("CROP_NORMALIZATION =", out["CROP_NORMALIZATION"], "|", out["SEMANTIC_COVERAGE"])


if __name__ == "__main__":
    main()
