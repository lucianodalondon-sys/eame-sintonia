#!/usr/bin/env python3
"""RT5 / REPRODUCIBILITY 3 -- two machine dependences the certification never named.

E1  ENCODING. Every open() in ENGINE/ and CASES/ is text mode with no encoding=, so the bytes
    are decoded with locale.getpreferredencoding(). This box: cp1252. A Linux box: utf-8.
    Which FIELDS carry non-ASCII, and does the decode change a LOAD-BEARING field
    (nome_area, date, val, id_survey, id_field)?

E2  KEY TYPE. denominator_guard builds den[r["id_survey"]] and then looks up
    den.get(r.get("id_survey")). If the same survey id arrives as int 42 in one file and
    str "42" in another, those are two different dict keys and the join silently misses.
    This is wrong in EVERY file order, so no amount of sorting fixes it.
"""
import json, os, sys, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
CASEDIR = os.path.join(ROOT, "CASES")
CASES = {"OLIVO-BACTROCERA-TOSCANA": (-1002, 1), "VITE-OIDIO-TOSCANA": (39, None),
         "FRUMENTO-SEPTORIA-TOSCANA": (372, None)}
R = {}

# ============================ E1 : ENCODING ============================================
e1 = {}
for case in CASES:
    d = os.path.join(CASEDIR, case)
    files = sorted(glob.glob(os.path.join(d, "RAW", "*.json")))
    affected, fields, samples, hard_fail = [], collections.Counter(), [], []
    for f in files:
        b = open(f, "rb").read()
        if not any(x > 127 for x in b):
            continue
        try:
            u = json.loads(b.decode("utf-8"))
        except UnicodeDecodeError:
            hard_fail.append((os.path.basename(f), "not valid utf-8")); continue
        try:
            c = json.loads(b.decode("cp1252"))
        except UnicodeDecodeError as ex:
            hard_fail.append((os.path.basename(f), f"cp1252 REFUSES the bytes: {ex}")); continue
        if u == c:
            continue
        affected.append(os.path.basename(f))
        for ru, rc in zip(u, c):
            for k in ru:
                if ru[k] != rc.get(k):
                    fields[k] += 1
                    if len(samples) < 8:
                        samples.append({"file": os.path.basename(f), "field": k,
                                        "utf8": ru[k], "cp1252": rc.get(k)})
    e1[case] = {"files_scanned": len(files),
                "files_that_PARSE_DIFFERENTLY_utf8_vs_cp1252": len(affected),
                "files": affected[:6],
                "cp1252_cannot_decode_at_all": hard_fail,
                "FIELDS_AFFECTED": dict(fields),
                "LOAD_BEARING_FIELD_AFFECTED": sorted(set(fields) &
                        {"nome_area", "date", "val", "id_survey", "id_field", "week"}),
                "samples": samples}
R["E1_ENCODING"] = e1

# ============================ E2 : id_survey KEY TYPE ==================================
e2 = {}
for case, (outv, denv) in CASES.items():
    d = os.path.join(CASEDIR, case)

    def ids(var):
        seen = collections.defaultdict(set)          # str(id) -> {python types}
        for f in sorted(glob.glob(os.path.join(d, "RAW", f"*_v{var}_*.json"))):
            for r in json.load(open(f)):
                v = r.get("id_survey")
                seen[str(v)].add(type(v).__name__)
        return seen

    out_ids = ids(outv)
    mixed_out = {k: sorted(v) for k, v in out_ids.items() if len(v) > 1}
    row = {"outcome_var": outv, "distinct_id_survey_as_text": len(out_ids),
           "ids_that_appear_as_BOTH_int_and_str_within_the_outcome_files": len(mixed_out),
           "examples": dict(list(mixed_out.items())[:5])}

    if denv is not None:
        den_ids = ids(denv)
        # replay the real guard's dict, keys as-is
        den = {}
        for f in sorted(glob.glob(os.path.join(d, "RAW", f"*_v{denv}_*.json"))):
            for r in json.load(open(f)):
                v = r.get("val")
                try: den[r["id_survey"]] = float(v) if v not in (None, "") else None
                except ValueError: den[r["id_survey"]] = None
        ktypes = collections.Counter(type(k).__name__ for k in den)
        # how many OUTCOME rows fail to find their denominator ONLY because of key type?
        miss_type, miss_real, hit = 0, 0, 0
        for f in sorted(glob.glob(os.path.join(d, "RAW", f"*_v{outv}_*.json"))):
            for r in json.load(open(f)):
                k = r.get("id_survey")
                if k in den:
                    hit += 1
                    continue
                alt = str(k) if isinstance(k, int) else (int(k) if str(k).lstrip("-").isdigit() else None)
                if alt is not None and alt in den:
                    miss_type += 1                   # present, but under the OTHER type
                else:
                    miss_real += 1                   # genuinely absent
        row.update({"denominator_var": denv,
                    "den_key_types": dict(ktypes),
                    "outcome_rows_that_find_their_key": hit,
                    "outcome_rows_MISSING_ONLY_BECAUSE_OF_KEY_TYPE": miss_type,
                    "outcome_rows_genuinely_absent_from_the_denominator": miss_real,
                    "denominator_ids_appearing_as_BOTH_types":
                        len({k for k, v in den_ids.items() if len(v) > 1})})
        # and the collision the certification measured, recomputed independently
        per_key_files = collections.defaultdict(set)
        per_key_vals = collections.defaultdict(set)
        for f in sorted(glob.glob(os.path.join(d, "RAW", f"*_v{denv}_*.json"))):
            b = os.path.basename(f)
            for r in json.load(open(f)):
                per_key_files[r["id_survey"]].add(b)
                per_key_vals[r["id_survey"]].add(str(r.get("val")))
        multi = [k for k, v in per_key_files.items() if len(v) > 1]
        conflict = [k for k in multi if len(per_key_vals[k]) > 1]
        def keeps(vals):
            out = set()
            for s in vals:
                try: out.add(bool(float(s)) if s not in ("None", "") else False)
                except ValueError: out.add(False)
            return out
        flip = [k for k in conflict if len(keeps(per_key_vals[k])) > 1]
        row.update({"RT5_keys_total": len(per_key_files),
                    "RT5_keys_in_more_than_one_file": len(multi),
                    "RT5_keys_with_conflicting_values": len(conflict),
                    "RT5_keys_where_the_conflict_flips_DROP_vs_KEEP": len(flip)})
    e2[case] = row
R["E2_KEY_TYPE"] = e2

json.dump(R, open(os.path.join(HERE, "rt5_p6_encoding_and_keytype.json"), "w"), indent=1, default=str)

print("=== E1 ENCODING")
for c, v in e1.items():
    print(f"  {c:28s} files parsing DIFFERENTLY utf8 vs cp1252: "
          f"{v['files_that_PARSE_DIFFERENTLY_utf8_vs_cp1252']}/{v['files_scanned']}")
    print(f"      fields affected: {v['FIELDS_AFFECTED']}")
    print(f"      LOAD-BEARING affected: {v['LOAD_BEARING_FIELD_AFFECTED']}")
    print(f"      cp1252 hard failures: {v['cp1252_cannot_decode_at_all']}")
    for s in v["samples"][:2]:
        print(f"      e.g. {s['field']}: utf8={s['utf8']!r}  cp1252={s['cp1252']!r}")
print("=== E2 KEY TYPE")
for c, v in e2.items():
    print(f"  {c:28s} ids appearing as BOTH int and str (outcome): "
          f"{v['ids_that_appear_as_BOTH_int_and_str_within_the_outcome_files']} of "
          f"{v['distinct_id_survey_as_text']}")
    if "den_key_types" in v:
        print(f"      den key types {v['den_key_types']}")
        print(f"      outcome rows: hit={v['outcome_rows_that_find_their_key']} "
              f"miss_by_TYPE={v['outcome_rows_MISSING_ONLY_BECAUSE_OF_KEY_TYPE']} "
              f"miss_real={v['outcome_rows_genuinely_absent_from_the_denominator']}")
        print(f"      RT5 recount: keys={v['RT5_keys_total']} multi_file={v['RT5_keys_in_more_than_one_file']} "
              f"conflicting={v['RT5_keys_with_conflicting_values']} flip={v['RT5_keys_where_the_conflict_flips_DROP_vs_KEEP']}")
print("\nwrote rt5_p6_encoding_and_keytype.json")
