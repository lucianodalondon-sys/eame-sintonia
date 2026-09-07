#!/usr/bin/env python3
"""RT3 shared loader: every raw row of every collected variable, with its file."""
import os, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
RAW = os.path.join(CASE, "RAW")

VARS = ["1", "-1001", "-1002", "-1003"]

# ISTAT province code -> province name, for Toscana + the neighbours that matter.
ISTAT_PROV = {
    "045": "Massa-Carrara", "046": "Lucca", "047": "Pistoia", "048": "Firenze",
    "049": "Livorno", "050": "Pisa", "051": "Arezzo", "052": "Siena",
    "053": "Grosseto", "100": "Prato",
}

# The 7 comuni transferred from Firenze (048) to the new province of Prato (100) in 1992.
# Legacy 048xxx code (as this source still serves it) -> current 100xxx code, comune name.
# The legacy codes below are the ones ACTUALLY present in this RAW dump, verified by name_4.
PRATO_REFORM = {
    "048007": ("100001", "CANTAGALLO"),
    "048009": ("100002", "CARMIGNANO"),
    "048029": ("100003", "MONTEMURLO"),
    "048051": ("100004", "POGGIO A CAIANO"),
    "048034": ("100005", "PRATO"),
    "048047": ("100006", "VAIANO"),
    "048048": ("100007", "VERNIO"),
}
PRATO_COMUNI = {v[1] for v in PRATO_REFORM.values()}


def admin6(code):
    """admin_code as the 6-digit ISTAT comune code string."""
    if code is None:
        return None
    s = str(code).strip()
    if s == "":
        return None
    if s.endswith(".0"):
        s = s[:-2]
    return s.zfill(6)


def prov_of_admin(code):
    a = admin6(code)
    return None if a is None else a[:3]


def rows(var=None):
    """Yield (filename, row) for one variable, or for all four."""
    vs = VARS if var is None else [var]
    for v in vs:
        for fn in sorted(glob.glob(os.path.join(RAW, f"*_v{v}_*.json"))):
            for r in json.load(open(fn, encoding="utf-8")):
                yield os.path.basename(fn), r


def visit_rows():
    """One row per (id_field, date) taken from the denominator variable v1 - the same
    population di_core turns into visits. Geography is identical across the 4 variables;
    that is verified separately by rt3_01."""
    out = {}
    for fn, r in rows("1"):
        k = (r.get("id_field"), r.get("date"))
        if None in k:
            continue
        out[k] = r
    return out


def fnum(x):
    try:
        return float(str(x).replace(",", "."))
    except (TypeError, ValueError):
        return None
