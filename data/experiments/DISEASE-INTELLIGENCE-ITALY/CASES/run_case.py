#!/usr/bin/env python3
"""
GENERIC CASE RUNNER — one code path for every REGION x CROP x ISSUE.

The honest reuse test: the engine must DERIVE the ordinal scale from whatever code table the
source returns, without a per-case hardcoded dict. Every place it cannot is recorded as a
CASE_SPECIFIC_RULE, which counts AGAINST the reuse rate.

Known ordering traps this must survive without help, all met already in this project:
  - order_n is unreliable (peronospora leaf: media=3 ranks below bassa=5)
  - the code NUMBER is unreliable (50=media, 51=bassa)
  - band vocabularies differ between issues (peronospora bunch tops at >15%, oidio at >10%)
So the ordinal is derived from the LABEL TEXT and nothing else.
"""
import json, os, sys, re, glob, collections, unicodedata
from statistics import mean

def fold(s):
    s = unicodedata.normalize("NFD", str(s))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower().strip()

# a WORD ladder, not a per-case dict. Applies to any Italian ordinal presence scale.
WORD_RANK = {"nessuna": 0, "nessuno": 0, "assente": 0, "no": 0,
             "bassa": 1, "lieve": 1, "scarsa": 1,
             "media": 2, "moderata": 2,
             "alta": 3, "grave": 3, "elevata": 3, "si": 3}

def derive_rank(label):
    """Return (rank, how) from the label text alone. None if not ordinal.

    EXTENDED 2026-09-06. The first case this pipeline was not built for (frumento x septoria)
    labels its scale "Nessuna / Bassa <5% / Media 5-25% / Alta >25%" — a ladder word AND a band
    in the same string. The original parser matched only a bare word or a bare band, resolved
    1 of those 4 codes, and the case fell through to the numeric fallback which read the CODE
    IDS 1634-1637 as magnitudes and published SITE_INCIDENCE 1.000 for every season.
    The extension is generic (word anywhere, then band anywhere), not a rule about wheat.
    """
    f = fold(label)
    if f in WORD_RANK:
        return WORD_RANK[f], "WORD_LADDER"
    for w, r in sorted(WORD_RANK.items(), key=lambda kv: -len(kv[0])):
        if re.search(r"\b" + w + r"\b", f):
            m = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*%|[<>]\s*(\d+)\s*%", f)
            return (r, "WORD_LADDER_IN_COMPOUND_LABEL" if not m
                    else "WORD_LADDER_IN_COMPOUND_LABEL_WITH_BAND")
    # percentage bands: rank by the LOWER bound, so >10% and >15% both sort last correctly
    m = re.match(r"^[<>]?\s*(\d+)\s*[-–]\s*(\d+)\s*%$", f)
    if m: return float(m.group(1)), "BAND_LOWER_BOUND"
    m = re.match(r"^>\s*(\d+)\s*%$", f)
    if m: return float(m.group(1)) + 0.5, "BAND_OPEN_UPPER"
    m = re.match(r"^<\s*(\d+)\s*%$", f)
    if m: return 0.5, "BAND_OPEN_LOWER"
    return None, "NOT_ORDINAL"

def build_scale(codes, var_id):
    """Derive the ordinal map for one variable from the API's own code table."""
    entries = [c for c in codes if c["id_survey_var"] == var_id]
    scale, unresolved, hows = {}, [], set()
    for c in entries:
        r, how = derive_rank(c["name"])
        hows.add(how)
        if r is None: unresolved.append(c["name"])
        else: scale[str(c["id_survey_code"])] = {"label": c["name"], "rank": r}
    ranks = sorted({v["rank"] for v in scale.values()})
    for v in scale.values(): v["ordinal"] = ranks.index(v["rank"])
    return scale, unresolved, sorted(hows)

def load_case(d):
    idx = json.load(open(os.path.join(d, "collection_index.json")))
    return idx

def season_outcomes(d, var_id, min_sites=10):
    idx = load_case(d)
    scale, unresolved, hows = build_scale(idx["codes"] or [], var_id)
    out, numeric_fallback = {}, False
    for fn in sorted(glob.glob(os.path.join(d, "RAW", f"*_v{var_id}_*.json"))):
        y = int(os.path.basename(fn)[:-5].split("_")[-1])
        rows = json.load(open(fn))
        sites = collections.defaultdict(list); nnum = 0
        for r in rows:
            v = r.get("val")
            if v is None: continue
            s = scale.get(str(v))
            if s is not None:
                sites[r["id_field"]].append(s["ordinal"])
            else:
                try:                                  # continuous variable, not ordinal
                    sites[r["id_field"]].append(float(str(v).replace(",", ".")))
                    nnum += 1; numeric_fallback = True
                except Exception:
                    pass
        if len(sites) < min_sites: continue
        pos = sum(1 for v in sites.values() if max(v) > 0)
        out[y] = {"n_visits": len(rows), "n_sites": len(sites),
                  "SITE_INCIDENCE": round(pos / len(sites), 4),
                  "SITE_MAX_MEAN": round(mean(max(v) for v in sites.values()), 4),
                  "n_provinces": len({r.get("nome_area") for r in rows if r.get("nome_area")}),
                  "n_comuni": len({r.get("admin_code") for r in rows if r.get("admin_code")}),
                  "n_orgs": len({r.get("org_name") for r in rows if r.get("org_name")}),
                  "pct_georef": round(100 * sum(1 for r in rows if _ll(r)) / len(rows), 1)}
    return out, {"scale": scale, "unresolved_labels": unresolved,
                 "derivation_methods": hows, "numeric_fallback_used": numeric_fallback}

def _ll(r):
    try: la, lo = float(r.get("lat") or 0), float(r.get("lon") or 0)
    except Exception: return False
    return abs(la) > 0.001 and abs(lo) > 0.001

if __name__ == "__main__":
    d, var = sys.argv[1], int(sys.argv[2])
    out, meta = season_outcomes(d, var)
    print(f"=== {os.path.basename(d)}  var {var}")
    print(f"    scale derived by {meta['derivation_methods']}  "
          f"unresolved={meta['unresolved_labels']}  numeric_fallback={meta['numeric_fallback_used']}")
    for cid, s in sorted(meta["scale"].items(), key=lambda x: x[1]["ordinal"]):
        print(f"      code {cid:>5s} -> ordinal {s['ordinal']}  '{s['label']}'")
    if not out: print("    NO SEASONS with enough sites"); raise SystemExit
    print(f"\n{'year':5s} {'visits':>7s} {'sites':>6s} {'prov':>5s} {'comuni':>7s} {'orgs':>5s} "
          f"{'%geo':>6s} {'siteInc':>8s} {'maxMean':>8s}")
    for y, v in sorted(out.items()):
        print(f"{y:5d} {v['n_visits']:7d} {v['n_sites']:6d} {v['n_provinces']:5d} {v['n_comuni']:7d} "
              f"{v['n_orgs']:5d} {v['pct_georef']:6.1f} {v['SITE_INCIDENCE']:8.3f} {v['SITE_MAX_MEAN']:8.3f}")
    print(f"\nSEASONS={len(out)}  TOTAL_VISITS={sum(v['n_visits'] for v in out.values())}")
    json.dump({"outcomes": out, "scale_meta": meta},
              open(os.path.join(d, f"outcomes_v{var}.json"), "w"), indent=1, default=str)
