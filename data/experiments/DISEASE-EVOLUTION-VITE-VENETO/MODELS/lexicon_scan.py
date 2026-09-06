#!/usr/bin/env python3
"""
MECHANICAL CROSS-CHECK — not the outcome.

A fixed, dumb, reproducible scan of the 26 ARPAV reports. It has no judgement and no
context: it finds sentences containing a peronospora token, decides whether a vine token
is nearby, and counts severity markers from a frozen lexicon.

Its ONLY purpose is to be an independent yardstick for the agent-produced ordinal scale.
If the scale and this scan disagree wildly on a year, that year is not robustly codeable
and must not be treated as a comparable season, whatever either one says.

It is deliberately worse than a careful reader. It cannot resolve "Nei vigneti ... Su
patata è stata rilevata la Peronospora" and it will mis-host some sentences. That is the
point: a mechanical floor, not a ceiling.
"""
import os, re, json, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NORM = os.path.join(ROOT, "NORMALIZED")

def fold(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()

PERO  = re.compile(r"peronospor", re.I)
OIDIO = re.compile(r"\boidi", re.I)
VINE  = re.compile(r"\b(vite|viti|vigne|vigneti|vigneto|vitat|uva|uve|grappol|viticolt|vitigni)", re.I)
OTHER_HOST = re.compile(r"\b(patat|pomodor|cipoll|lattug|tabacc|girasol|barbabietol|melo|meli\b|pero\b|actinidi)", re.I)

SEV = {
  "HIGH":   ["gravissim","grave","gravi","virulenz","virulent","forte","forti","elevat","intens",
             "important","esplosiv","dilagant","ingent","sever","notevol","massicc","epidemi",
             "generalizzat","recrudescenz","aggressiv","danni ingenti","attacchi violenti"],
  "MEDIUM": ["medio-bass","medio-alt","medi a","moderat","discret","sensibil","apprezzabil",
             "media gravita","gravita media"],
  "LOW":    ["legger","lieve","scars","limitat","contenut","modest","rade","rara","raro","sporadic",
             "trascurabil","assent","assenza","minim","ridott","bland","poco attiv","poco present",
             "non ha destato","nessun problema","sotto controllo"],
}
SCOPE = {
  "WIDE":   ["tutto il territorio","tutti gli ambienti","ovunque","generalizzat","in tutta la regione",
             "su tutto il","diffus","in tutti i"],
  "PARTIAL":["in diversi areali","in alcune","in alcuni","in numerosi","in molti","varie zone",
             "in parte","in certe"],
  "NARROW": ["localmente","solo localmente","in alcune aree limitate","circoscritt","puntiform","isolat"],
}
TREATMENT = ["regolarmente difes","ben difes","trattament","difesa fitosanitaria","anticrittogamic",
             "interventi","copertur"]

def sentences(t):
    t = re.sub(r"=== PAGE \d+ ===", " ", t)
    t = re.sub(r"\s+", " ", t)
    return [s.strip() for s in re.split(r"(?<=[.;:!?])\s+", t) if s.strip()]

def scan(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    ss = sentences(t)
    out = {"n_sentences": len(ss), "chars": len(t), "vine_pero": [], "vine_oidio": [],
           "other_host_pero": [], "ambiguous_pero": []}
    for i, s in enumerate(ss):
        f = fold(s)
        ctx = fold(" ".join(ss[max(0, i-1):i+2]))
        for rx, key in ((PERO, "pero"), (OIDIO, "oidio")):
            if not rx.search(s):
                continue
            vine_here = bool(VINE.search(s)); other_here = bool(OTHER_HOST.search(s))
            vine_ctx = bool(VINE.search(ctx)); other_ctx = bool(OTHER_HOST.search(ctx))
            rec = {
                "sentence": s,
                "sev_markers": {lvl: sorted({w for w in ws if w in f}) for lvl, ws in SEV.items()},
                "scope_markers": {lvl: sorted({w for w in ws if w in f}) for lvl, ws in SCOPE.items()},
                "treatment_markers": sorted({w for w in TREATMENT if w in f}),
                "vine_in_sentence": vine_here, "other_host_in_sentence": other_here,
                "vine_in_context": vine_ctx, "other_host_in_context": other_ctx,
            }
            if vine_here and not other_here:
                bucket = "vine_pero" if key == "pero" else "vine_oidio"
            elif other_here and not vine_here:
                bucket = "other_host_pero" if key == "pero" else None
            elif vine_ctx and not other_ctx:
                bucket = "vine_pero" if key == "pero" else "vine_oidio"
            else:
                bucket = "ambiguous_pero" if key == "pero" else None
            if bucket:
                out[bucket].append(rec)
    # mechanical severity tally over vine peronospora sentences only
    tally = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in out["vine_pero"]:
        for lvl in tally:
            tally[lvl] += len(r["sev_markers"][lvl])
    out["mechanical_tally"] = tally
    total = sum(tally.values())
    if total == 0:
        out["mechanical_class"] = "NO_SEVERITY_MARKER"
    else:
        out["mechanical_class"] = max(tally, key=lambda k: (tally[k], -["HIGH","MEDIUM","LOW"].index(k)))
    out["mechanical_confidence"] = ("NONE" if total == 0 else
                                    "LOW" if total == 1 else
                                    "MEDIUM" if total <= 3 else "HIGH")
    out["n_vine_pero_sentences"] = len(out["vine_pero"])
    out["n_other_host_pero_sentences"] = len(out["other_host_pero"])
    out["n_ambiguous"] = len(out["ambiguous_pero"])
    out["any_treatment_conditional"] = any(r["treatment_markers"] for r in out["vine_pero"])
    return out

if __name__ == "__main__":
    res = {}
    for fn in sorted(os.listdir(NORM)):
        if not fn.endswith(".txt"):
            continue
        key = fn.replace("annata-agraria-", "").replace(".txt", "")
        res[key] = scan(os.path.join(NORM, fn))
    dest = os.path.join(ROOT, "OBSERVATIONS", "lexicon_scan.json")
    json.dump({"WARNING": "MECHANICAL CROSS-CHECK ONLY. Not the outcome. Not evidence on its own.",
               "lexicon_frozen": {"SEV": SEV, "SCOPE": SCOPE, "TREATMENT": TREATMENT},
               "per_doc": res}, open(dest, "w"), indent=1, ensure_ascii=False)
    print(f"{'DOC':10s} {'chars':>6s} {'vinePero':>9s} {'other':>6s} {'ambig':>6s} "
          f"{'H':>3s} {'M':>3s} {'L':>3s}  {'mech class':18s} conf   txtCond")
    for k in sorted(res):
        r = res[k]; t = r["mechanical_tally"]
        print(f"{k:10s} {r['chars']:6d} {r['n_vine_pero_sentences']:9d} "
              f"{r['n_other_host_pero_sentences']:6d} {r['n_ambiguous']:6d} "
              f"{t['HIGH']:3d} {t['MEDIUM']:3d} {t['LOW']:3d}  {r['mechanical_class']:18s} "
              f"{r['mechanical_confidence']:6s} {r['any_treatment_conditional']}")
    n_no = sum(1 for r in res.values() if r["mechanical_class"] == "NO_SEVERITY_MARKER")
    print(f"\ndocs={len(res)}  no severity marker={n_no}  "
          f"with >=1 vine-pero sentence={sum(1 for r in res.values() if r['n_vine_pero_sentences'])}")
    print(f"wrote {dest}")
