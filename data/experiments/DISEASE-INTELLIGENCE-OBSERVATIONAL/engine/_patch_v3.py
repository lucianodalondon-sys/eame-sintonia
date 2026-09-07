#!/usr/bin/env python3
"""Corrections forced by the determinism lens (RT4) and the statistics lens (RT5)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))

# ── 1. di_core: hash the CODE and the SHEET, not only the data ────────────────────────
p = os.path.join(HERE, "di_core.py")
s = open(p, encoding="utf-8").read()
s = s.replace('''def load_sheet(path=SHEET_PATH):
    s = json.load(open(path, encoding="utf-8"))''',
'''def code_fingerprint():
    """Every input the answer depends on, not only the data files.

    The determinism lens found 8 such inputs carrying no hash at all, the semantic sheet among
    them: moving one band edge in it repaints a province green to yellow, and nothing recorded
    that the sheet had moved. A receipt that names the data but not the code or the definitions
    is not a receipt."""
    import sys as _s
    out = {"python": _s.version.split()[0]}
    for f in ("di_core.py", "di_observe.py", "di_adama.py", "di_render.py", "di_refresh.py"):
        fp = os.path.join(HERE, f)
        if os.path.exists(fp):
            out[f] = hashlib.sha256(open(fp, "rb").read()).hexdigest()[:16]
    sp = os.path.abspath(SHEET_PATH)
    if os.path.exists(sp):
        out["SOURCE-SEMANTIC-SHEET.json"] = hashlib.sha256(
            open(sp, "rb").read()).hexdigest()[:16]
        out["sheet_version"] = json.load(open(sp, encoding="utf-8")).get("SHEET_VERSION")
    return out


def load_sheet(path=SHEET_PATH):
    s = json.load(open(path, encoding="utf-8"))''')

# the reader must actually CHECK a hash, not merely record one
s = s.replace('''    return {"AS_OF": as_of.isoformat(),''',
'''    return {"AS_OF": as_of.isoformat(),
            "CODE_AND_DEFINITIONS": code_fingerprint(),''')
open(p, "w", encoding="utf-8").write(s)
print("di_core: code + sheet fingerprint")

# ── 2. di_observe: stop truncating the numerator with int() ───────────────────────────
p2 = os.path.join(HERE, "di_observe.py")
o = open(p2, encoding="utf-8").read()
o = o.replace('''    return {"rate_pct": round(100.0 * num / den, 4) if den else None,
            "infested_drupes": int(num), "drupes_sampled": int(den),''',
'''    # int() on a float sum truncates: the determinism lens found a window that publishes 690
    # or 689 depending on summation order, and four current cells printing a whole number while
    # the rate underneath was built on a fraction. The rate never moved; the printed count did.
    return {"rate_pct": round(100.0 * num / den, 4) if den else None,
            "infested_drupes": round(num, 2), "drupes_sampled": round(den, 2),''')
open(p2, "w", encoding="utf-8").write(o)
print("di_observe: no int() truncation of the numerator")
