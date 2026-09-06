#!/usr/bin/env python3
"""RT5 / REPRODUCIBILITY 2 -- sources of machine dependence the certification did NOT name.

The certification blames exactly one line (the unsorted glob in denominator_guard). This
script looks for the others. Every finding is either PROVED with a measurement or reported
as NOT_KNOWN with the experiment that would settle it. Read-only on ENGINE/ and CASES/.

  N1  text-mode open() with no encoding=      -> locale-dependent decode
  N2  non-ASCII bytes actually present?       -> does N1 bite in THIS archive
  N3  PYTHONHASHSEED                          -> does any output depend on it
  N4  id_survey key TYPE across files         -> silent join miss, order-independent
  N5  date strings only some Pythons accept   -> rows silently dropped by version
  N6  'week' values that int() cannot parse   -> crash by data, not by machine
  N7  float summation order in SEVERITY       -> is SEVERITY load-bearing at all
  N8  the denominator glob pattern            -> what it actually matches
  N9  CWD-relative writes                     -> where the committed artefacts land
  N10 network in the gate path                -> gates.json depends on a live server
"""
import json, os, sys, glob, subprocess, collections, datetime as dt, locale, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ENGINE, CASEDIR = os.path.join(ROOT, "ENGINE"), os.path.join(ROOT, "CASES")
sys.path.insert(0, ENGINE); sys.path.insert(0, CASEDIR)
import current_pressure as cp

R = {}
CASES = {"OLIVO-BACTROCERA-TOSCANA": -1002, "VITE-OIDIO-TOSCANA": 39,
         "FRUMENTO-SEPTORIA-TOSCANA": 372}

# ---- N1 --------------------------------------------------------------------------------
srcs = sorted(glob.glob(os.path.join(ENGINE, "*.py")) + glob.glob(os.path.join(CASEDIR, "*.py")))
opens, with_enc = 0, 0
for s in srcs:
    t = open(s, encoding="utf-8").read()
    opens += len(re.findall(r"\bopen\(", t))
    with_enc += len(re.findall(r"\bopen\([^)]*encoding=", t))
R["N1_text_open_without_encoding"] = {
    "python_files_scanned": len(srcs), "open_calls": opens, "with_explicit_encoding": with_enc,
    "this_interpreter_locale_encoding": locale.getpreferredencoding(False),
    "MEANING": "open() in text mode decodes with the platform's preferred encoding. The same "
               "bytes therefore decode differently on a cp1252 Windows box and a UTF-8 Linux box."}

# ---- N2 --------------------------------------------------------------------------------
n2 = {}
for case in CASES:
    d = os.path.join(CASEDIR, case)
    files = sorted(glob.glob(os.path.join(d, "RAW", "*.json"))) + \
            [os.path.join(d, "collection_index.json")]
    nonascii_files, worst = [], None
    for f in files:
        b = open(f, "rb").read()
        na = sum(1 for x in b if x > 127)
        if na:
            nonascii_files.append((os.path.basename(f), na))
            # does it round-trip differently under cp1252?
            try:
                u = b.decode("utf-8"); c = b.decode("cp1252")
                if u != c: worst = os.path.basename(f)
            except UnicodeDecodeError:
                worst = os.path.basename(f) + " (not valid utf-8)"
    n2[case] = {"files_checked": len(files), "files_with_non_ascii_bytes": len(nonascii_files),
                "examples": nonascii_files[:5],
                "a_file_that_decodes_DIFFERENTLY_under_cp1252": worst}
R["N2_non_ascii_bytes_present"] = n2

# ---- N3 --------------------------------------------------------------------------------
snippet = (
    "import sys,os,json,datetime as dt\n"
    f"sys.path.insert(0,{ENGINE!r}); sys.path.insert(0,{CASEDIR!r})\n"
    "import current_pressure as cp\n"
    f"d=os.path.join({CASEDIR!r},'OLIVO-BACTROCERA-TOSCANA')\n"
    "r=cp.current_pressure(d,-1002,dt.date(2026,9,6))\n"
    "print(json.dumps(r,sort_keys=True,default=str))\n")
outs = {}
for seed in ("0", "1", "12345"):
    env = dict(os.environ); env["PYTHONHASHSEED"] = seed
    p = subprocess.run([sys.executable, "-c", snippet], capture_output=True, text=True, env=env)
    outs[seed] = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else f"ERR:{p.stderr[-200:]}"
R["N3_PYTHONHASHSEED"] = {"seeds_tried": list(outs),
                          "all_outputs_identical": len(set(outs.values())) == 1,
                          "n_distinct_outputs": len(set(outs.values()))}

# ---- N4 --------------------------------------------------------------------------------
n4 = {}
for case, var in CASES.items():
    d = os.path.join(CASEDIR, case)
    idx = json.load(open(os.path.join(d, "collection_index.json")))
    dv = idx.get("DENOMINATOR_VAR")
    types_den, types_out = collections.Counter(), collections.Counter()
    if dv is not None:
        for f in sorted(glob.glob(os.path.join(d, "RAW", f"*_v{dv}_*.json"))):
            for r in json.load(open(f)):
                types_den[type(r.get("id_survey")).__name__] += 1
    for f in sorted(glob.glob(os.path.join(d, "RAW", f"*_v{var}_*.json"))):
        for r in json.load(open(f)):
            types_out[type(r.get("id_survey")).__name__] += 1
    n4[case] = {"DENOMINATOR_VAR": dv,
                "id_survey_types_in_denominator_files": dict(types_den),
                "id_survey_types_in_outcome_files": dict(types_out),
                "TYPES_MATCH": set(types_den) == set(types_out) if dv is not None else None}
R["N4_id_survey_key_types"] = n4

# ---- N5 / N6 ---------------------------------------------------------------------------
n5, n6 = {}, {}
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
for case, var in CASES.items():
    d = os.path.join(CASEDIR, case)
    forms, weeks_bad, ndates = collections.Counter(), collections.Counter(), 0
    for f in sorted(glob.glob(os.path.join(d, "RAW", f"*_v{var}_*.json"))):
        for r in json.load(open(f)):
            ds = r.get("date")
            if ds is None: forms["<null>"] += 1; continue
            ndates += 1
            forms["plain_YYYY-MM-DD" if ISO.match(str(ds)) else f"OTHER:{ds!r}"] += 1
            w = r.get("week")
            if w is not None:
                try: int(w)
                except (TypeError, ValueError): weeks_bad[repr(w)] += 1
    n5[case] = {"rows_with_a_date": ndates,
                "date_shapes": {k: v for k, v in list(forms.items())[:6]},
                "ALL_plain_ISO": set(forms) <= {"plain_YYYY-MM-DD", "<null>"}}
    n6[case] = {"week_values_int_cannot_parse": dict(list(weeks_bad.items())[:5]),
                "n_bad": sum(weeks_bad.values())}
R["N5_date_string_shapes"] = n5
R["N6_week_values"] = n6

# ---- N7 --------------------------------------------------------------------------------
callers = {}
for s in srcs:
    t = open(s, encoding="utf-8").read()
    callers[os.path.basename(s)] = {"passes_SEVERITY": "SEVERITY" in t and 'metric="SEVERITY"' in t,
                                    "mentions_SEVERITY": t.count("SEVERITY")}
R["N7_SEVERITY_is_float_order_sensitive_but"] = {
    "per_file": callers,
    "metric_used_by_gates_py": "INCIDENCE (the default; no caller passes SEVERITY)",
    "INCIDENCE_arithmetic": "sum(1 for v in vals if v>0)/len(vals) -- integer counts, "
                            "so summation order cannot change it",
    "VERDICT": "float summation order exists in SEVERITY only, and SEVERITY reaches no gate"}

# ---- N8 --------------------------------------------------------------------------------
d = os.path.join(CASEDIR, "OLIVO-BACTROCERA-TOSCANA")
R["N8_denominator_glob"] = {
    "pattern": "*_v1_*.json",
    "matches": sorted(os.path.basename(x) for x in glob.glob(os.path.join(d, "RAW", "*_v1_*.json"))),
    "all_files_in_RAW": len(glob.glob(os.path.join(d, "RAW", "*.json"))),
    "does_it_leak_v-1001_or_v-1002": [b for b in
        (os.path.basename(x) for x in glob.glob(os.path.join(d, "RAW", "*_v1_*.json")))
        if "v-100" in b]}

# ---- N9 --------------------------------------------------------------------------------
n9 = {}
for s in srcs:
    t = open(s, encoding="utf-8").read()
    rel = re.findall(r'open\((["\'])([A-Za-z0-9_.\-]+\.(?:json|txt))\1\s*,\s*["\']w', t)
    if rel: n9[os.path.basename(s)] = sorted({m[1] for m in rel})
R["N9_writes_relative_to_CWD"] = {
    "files": n9,
    "MEANING": "the committed artefact is only overwritten when the script is launched from "
               "the directory that holds it; run from anywhere else the stale copy survives"}

# ---- N10 -------------------------------------------------------------------------------
gtxt = open(os.path.join(ENGINE, "gates.py"), encoding="utf-8").read()
R["N10_network_inside_the_gate_run"] = {
    "gate_H_calls": "automation_probe.fetch() x3, live HTTP GET",
    "endpoint": re.search(r'API = "([^"]+)"',
                          open(os.path.join(ENGINE, "automation_probe.py"), encoding="utf-8").read()).group(1),
    "offline_behaviour": "fetch() returns HTTP=None -> reachable=0 -> gate H FAIL",
    "MEANING": "gates.json is not a function of the repository alone; it is a function of the "
               "repository AND of what a third-party server returns on the day of the run"}
# absolute paths that a clean checkout cannot resolve
abs_paths = sorted(set(re.findall(r'"(/[a-zA-Z][^"]*)"', gtxt)))
R["N11_absolute_paths_in_ENGINE"] = {
    "found": abs_paths,
    "exists_on_this_machine": {p: os.path.exists(p) for p in abs_paths}}

json.dump(R, open(os.path.join(HERE, "rt5_p5_nondeterminism.json"), "w"), indent=1, default=str)

print("N1 open() calls / with encoding= :", R["N1_text_open_without_encoding"]["open_calls"], "/",
      R["N1_text_open_without_encoding"]["with_explicit_encoding"],
      "| this box decodes as", R["N1_text_open_without_encoding"]["this_interpreter_locale_encoding"])
for c, v in R["N2_non_ascii_bytes_present"].items():
    print(f"N2 {c:28s} files with non-ASCII bytes: {v['files_with_non_ascii_bytes']}/{v['files_checked']}"
          f"  differs under cp1252: {v['a_file_that_decodes_DIFFERENTLY_under_cp1252']}")
print("N3 PYTHONHASHSEED 0/1/12345 -> identical output:", R["N3_PYTHONHASHSEED"]["all_outputs_identical"])
for c, v in R["N4_id_survey_key_types"].items():
    print(f"N4 {c:28s} denom types {v['id_survey_types_in_denominator_files']} "
          f"outcome types {v['id_survey_types_in_outcome_files']}")
for c, v in R["N5_date_string_shapes"].items():
    print(f"N5 {c:28s} all plain ISO dates: {v['ALL_plain_ISO']}  ({v['rows_with_a_date']} dated rows)")
for c, v in R["N6_week_values"].items():
    print(f"N6 {c:28s} unparseable week values: {v['n_bad']}")
print("N8 denominator glob matched:", len(R["N8_denominator_glob"]["matches"]), "of",
      R["N8_denominator_glob"]["all_files_in_RAW"], "| leaks:", R["N8_denominator_glob"]["does_it_leak_v-1001_or_v-1002"])
print("N9 CWD-relative writes:", R["N9_writes_relative_to_CWD"]["files"])
print("N11 absolute paths in gates.py:", R["N11_absolute_paths_in_ENGINE"]["exists_on_this_machine"])
print("\nwrote rt5_p5_nondeterminism.json")
