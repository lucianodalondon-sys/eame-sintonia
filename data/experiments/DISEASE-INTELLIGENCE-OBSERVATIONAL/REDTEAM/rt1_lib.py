#!/usr/bin/env python3
"""RT1 shared loader. Reads the archive AND the RT1 stage fetch into one visit table.
Read-only on everything outside REDTEAM/."""
import os, json, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
FETCH = os.path.join(HERE, "FETCH")

ARCHIVE_VARS = {1: "tot", -1001: "attiva", -1002: "dannosa", -1003: "totale"}
STAGE_VARS = {2: "u", 3: "l1v", 4: "l1m", 5: "l2v", 6: "l2m", 7: "l3v", 8: "l3m",
              9: "pv", 10: "pm", 11: "fu", 21: "ps"}


def _num(v):
    if v is None or v == "":
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


def read_var(var_id, years=None, root=None):
    """{(id_field,date): {'value':..,'row':..}} for one variable."""
    root = root or CASE
    if root == CASE:
        pattern = os.path.join(root, "RAW", f"*_v{var_id}_*.json")
    else:
        pattern = os.path.join(root, f"*_v{var_id}_*.json")
    out = {}
    for fn in sorted(glob.glob(pattern)):
        yr = os.path.basename(fn).rsplit("_", 1)[1][:4]
        if years and int(yr) not in years:
            continue
        for r in json.load(open(fn, encoding="utf-8")):
            k = (r.get("id_field"), r.get("date"))
            if None in k:
                continue
            out[k] = {"value": _num(r.get("val")), "row": r, "year": int(yr)}
    return out


def visit_table(years=None, with_stages=False):
    """One row per visit key, every variable as a column."""
    cols = {}
    for vid, name in ARCHIVE_VARS.items():
        cols[name] = read_var(vid, years)
    if with_stages:
        for vid, name in STAGE_VARS.items():
            cols[name] = read_var(vid, years, root=FETCH)
    keys = set()
    for c in cols.values():
        keys |= set(c)
    rows = []
    for k in sorted(keys, key=lambda t: (str(t[1]), str(t[0]))):
        any_row = next((cols[c][k]["row"] for c in cols if k in cols[c]), None)
        rec = {"id_field": k[0], "date": k[1],
               "province": any_row.get("nome_area"), "comune": any_row.get("name_4"),
               "org": any_row.get("org_name"), "id_org": any_row.get("id_org"),
               "week": any_row.get("week"), "cultivar": any_row.get("cultivar"),
               "name": any_row.get("name"),
               "lat": any_row.get("lat"), "lon": any_row.get("lon"),
               "id_survey": any_row.get("id_survey"), "uid": any_row.get("uid"),
               "year": int(str(k[1])[:4]) if k[1] else None}
        for c in cols:
            rec[c] = cols[c][k]["value"] if k in cols[c] else None
        rows.append(rec)
    return rows


def pct(n, d, nd=2):
    return "n/a" if not d else f"{100.0*n/d:.{nd}f}%"
