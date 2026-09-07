#!/usr/bin/env python3
"""RT1 - ACCUSATION 8: make the engine accept something it should refuse.

Nothing outside REDTEAM/ is written. The fake case directory is built under
REDTEAM/FAKECASE/ from copies.
"""
import os, sys, json, shutil, glob, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
sys.path.insert(0, HERE)
import di_core, di_observe, di_render
import rt1_lib as L

FAKE = os.path.join(HERE, "FAKECASE")


def hr(t):
    print("\n" + "=" * 74 + f"\n{t}\n" + "=" * 74)


def n_usable(loaded):
    """the engine renamed this key mid-audit; accept either."""
    for k in ("n_visits_usable_for_rates",
              "n_visits_usable_for_at_least_one_measurement"):
        if k in loaded:
            return loaded[k]
    return "n/a"


def main():
    sheet = di_core.load_sheet()

    hr("A. the refusals that DO work")
    for canon in ("EGG_COUNT", "Infestazione Attiva", "attiva", -1001):
        try:
            di_core.var_for(sheet, canon)
            print(f"  ACCEPTED {canon!r}  <-- hole")
        except di_core.SemanticRefusal as e:
            print(f"  REFUSED  {canon!r}: {str(e)[:80]}...")
    try:
        di_core._read_variable(L.CASE, 2, sheet)
        print("  ACCEPTED raw var 2  <-- hole")
    except di_core.SemanticRefusal as e:
        print(f"  REFUSED  raw var 2: {str(e)[:80]}...")

    hr("B. HOLE 1 - the sheet forbids it, the code does not read the prohibition")
    print("  the sheet says var 1 CANNOT_USE_FOR 'any measure of disease'.")
    print("  di_report.py takes the metric from argv[2] and passes it straight through.")
    as_of = dt.date(2026, 9, 6)
    loaded = di_core.load_visits(L.CASE, sheet, as_of)
    c = di_observe.cell(loaded["visits"], sheet, "Firenze",
                        "SAMPLE_SIZE / DENOMINATOR", as_of)
    o = c["observation"]
    print(f"  ACCEPTED. Firenze 'observation' with the DENOMINATOR as the metric:")
    print(f"    value_pct = {o['value_pct']}   band = {o['source_band']}")
    print(f"    rendered sentence: "
          f"{[l for l in di_render.render_province(c, {'relevance':'NO','reason':''}, c and {'attention_class':'X','rule_applied':['x']}).splitlines() if '%' in l][:2]}")
    print("  -> the engine publishes '100.0% of sampled drupes with live infestation'.")
    print("     No CANNOT_USE_FOR check exists anywhere in di_core / di_observe:")
    src = open(os.path.join(HERE, "..", "engine", "di_core.py"), encoding="utf-8").read() + \
        open(os.path.join(HERE, "..", "engine", "di_observe.py"), encoding="utf-8").read()
    print(f"     occurrences of 'CANNOT_USE_FOR' in di_core.py + di_observe.py: "
          f"{src.count('CANNOT_USE_FOR')}")
    print(f"     occurrences of 'CAN_USE_FOR'    : {src.count('CAN_USE_FOR')}")
    print(f"     occurrences of 'crop_id'/'survey_schema_id': "
          f"{src.count('crop_id') + src.count('survey_schema_id')}")

    hr("C. HOLE 2 - the filename glob ignores crop and schema")
    print("  di_core._read_variable globs RAW/*_v{var}_*.json .")
    print("  Nothing checks the c{crop}_s{schema} prefix that di_refresh itself writes.")
    if os.path.exists(FAKE):
        shutil.rmtree(FAKE)
    os.makedirs(os.path.join(FAKE, "RAW"))
    for fn in glob.glob(os.path.join(L.CASE, "RAW", "*_2026.json")):
        shutil.copy(fn, os.path.join(FAKE, "RAW", os.path.basename(fn)))
    base = di_core.load_visits(FAKE, sheet, as_of)
    print(f"  clean fake case (2026 only): {base['n_visits']} visits, "
          f"{n_usable(base)} usable")
    # a file from a DIFFERENT crop and a DIFFERENT schema, same var number
    rows = json.load(open(os.path.join(FAKE, "RAW", "c2_s1_v-1001_2026.json"),
                          encoding="utf-8"))
    alien = []
    for r in rows[:400]:
        q = dict(r)
        q["id_field"] = 999000 + (q["id_field"] or 0)
        q["val"] = "77"
        q["nome_area"] = "Firenze"
        alien.append(q)
    json.dump(alien, open(os.path.join(FAKE, "RAW", "c7_s99_v-1001_2026.json"),
                          "w", encoding="utf-8"))
    den = [dict(r, id_field=999000 + (r["id_field"] or 0), val="100",
                nome_area="Firenze")
           for r in json.load(open(os.path.join(FAKE, "RAW", "c2_s1_v1_2026.json"),
                                   encoding="utf-8"))[:400]]
    json.dump(den, open(os.path.join(FAKE, "RAW", "c7_s99_v1_2026.json"),
                        "w", encoding="utf-8"))
    after = di_core.load_visits(FAKE, sheet, as_of)
    print(f"  after dropping c7_s99_v-1001_2026.json (crop 7, schema 99) into the same "
          f"RAW dir:")
    print(f"    {after['n_visits']} visits, {n_usable(after)} usable "
          f"(+{after['n_visits'] - base['n_visits']})")
    cb = di_observe.cell(base["visits"], sheet, "Firenze", "ACTIVE_INFESTATION_COUNT", as_of)
    ca = di_observe.cell(after["visits"], sheet, "Firenze", "ACTIVE_INFESTATION_COUNT",
                         as_of)
    print(f"    Firenze rate before {cb['observation']['value_pct']}%  ->  after "
          f"{ca['observation']['value_pct']}%")
    print(f"    band before {cb['observation']['source_band']['label']} -> after "
          f"{ca['observation']['source_band']['label']}")
    print("  ACCEPTED without a word. The provenance block still names the API and the "
          "sheet, and prints the alien file among 'source_files'.")
    print(f"    source_files now: "
          f"{sorted(f['file'] for f in after['provenance']['ACTIVE_INFESTATION_COUNT']['files'])}")

    hr("D. HOLE 3 - band_for has a hole between 0 and 0.01, and the renderer crashes in it")
    for p in (0, 0.004, 0.0099, 0.01, 5.9, 6.0, 6.5, 9.9, 10.0, 25.0):
        b = di_core.band_for(sheet, p)
        print(f"  rate {p:>7}%  ->  {b['label'] if b else 'None'}"
              f"{'   <-- NO BAND' if b is None else ''}"
              f"{'   <-- label contradicts the number' if b and p >= 6 and p < 7 else ''}")
    fake_cell = dict(cb)
    fake_cell["observation"] = dict(cb["observation"])
    fake_cell["observation"]["value_pct"] = 0.004
    fake_cell["observation"]["source_band"] = di_core.band_for(sheet, 0.004)
    try:
        di_render.render_province(fake_cell, {"relevance": "NO", "reason": "x"},
                                  {"attention_class": "X", "rule_applied": ["x"]})
        print("  renderer survived a rate of 0.004%")
    except Exception as e:
        print(f"  RENDERER CRASHES on a rate of 0.004%: {type(e).__name__}: {e}")

    hr("E. HOLE 4 - a NaN in the source poisons a whole province and passes every gate")
    print(f"  di_core._num('nan') = {di_core._num('nan')}")
    print(f"  di_core._num('NaN') = {di_core._num('NaN')}")
    print(f"  di_core._num('Infinity') = {di_core._num('Infinity')}")
    n = di_core._num("nan")
    print(f"  sanity checks: (nan < 0) = {n < 0}; (nan > 100) = {n > 100} "
          f"-> both False, so the visit is marked usable_for_rates")
    poisoned = json.load(open(os.path.join(FAKE, "RAW", "c2_s1_v-1001_2026.json"),
                              encoding="utf-8"))
    hits = 0
    for r in poisoned:
        if r.get("nome_area") == "Prato" and not hits:
            r["val"] = "nan"
            hits = 1
    json.dump(poisoned, open(os.path.join(FAKE, "RAW", "c2_s1_v-1001_2026.json"),
                             "w", encoding="utf-8"))
    os.remove(os.path.join(FAKE, "RAW", "c7_s99_v-1001_2026.json"))
    os.remove(os.path.join(FAKE, "RAW", "c7_s99_v1_2026.json"))
    pois = di_core.load_visits(FAKE, sheet, as_of)
    cp = di_observe.cell(pois["visits"], sheet, "Prato", "ACTIVE_INFESTATION_COUNT", as_of)
    print(f"  one row of Prato set to 'nan': value_pct = "
          f"{cp['observation']['value_pct']}, band = {cp['observation']['source_band']}, "
          f"publishable = {cp['quality']['observation_publishable']}")
    print(f"  exclusions reported: {pois['exclusions']}")
    shutil.rmtree(FAKE)


if __name__ == "__main__":
    main()
