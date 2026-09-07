#!/usr/bin/env python3
"""RT6-J. What the tool COMPUTES and then does not show. The pooled provincial rate is
the only number in the card. The per-visit maximum is computed in pooled() and dropped."""
import os, sys, json, datetime as dt, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_report, di_render

sheet, loaded, cells, adama = di_report.run(dt.date(2026, 9, 6))
print(f"{'PROV':14s} {'pooled%':>8s} {'per-visit med%':>15s} {'per-visit MAX%':>15s} "
      f"{'source band of the MAX':>24s} {'ATTN':>14s}")
import di_core
for c in sorted(cells, key=lambda x: -x['observation']['per_visit_rate_pct_max']):
    o = c["observation"]
    b = di_core.band_for(sheet, o["per_visit_rate_pct_max"])
    print(f"{c['province']:14s} {o['value_pct']:8.4f} {o['per_visit_rate_pct_median']:15.4f} "
          f"{o['per_visit_rate_pct_max']:15.4f} "
          f"{(b['label']+' ('+str(b['meaning'])+')'):>24s} "
          f"{c['attention']['attention_class']:>14s}")

txt = di_render.render_province(cells[0], adama, cells[0]["attention"])
reg = di_render.render_region(cells, adama)
print("\nIS THE MAX EVER PRINTED?")
for f in ("per_visit_rate_pct_max", "per_visit_rate_pct_median"):
    print(f"  {f:28s} in cell.observation: True   in the province card: "
          f"{f in txt}   in the region card: {f in reg}")
print("  the token 'yellow' or 'red' anywhere in the region card:",
      "yellow" in reg or "red" in reg)
print("  region card says:", [l for l in reg.splitlines() if "bandas" in l][0].strip())

print("\nMODEL FIELDS THAT EXIST AND ARE NEVER RENDERED (the guards live here):")
never = []
def leaves(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{p}.{k}" if p else k)
    elif isinstance(o, list):
        yield p
    else:
        yield p
allf = sorted(set(leaves(cells[0])))
for f in allf:
    last = f.split(".")[-1]
    if last not in txt and last.upper() not in txt.upper():
        never.append(f)
for f in never:
    if any(t in f for t in ("FORBIDDEN", "NOT_A_COMMERCIAL", "per_visit", "percentile",
                            "baseline_rate", "panel_overlap", "matched_seasons",
                            "semantic_validity", "denominator_validity",
                            "temporal_validity", "historical_state_matched",
                            "absence_rule", "scope_note", "default_for_anything")):
        print(f"  {f}")
print(f"\n  total cell leaf paths: {len(allf)};  never appearing in a province card: "
      f"{len(never)}")

print("\nTHE ATTENTION LINE'S NEIGHBOURHOOD IN THE CARD (Lucca):")
lucca = next(c for c in cells if c["province"] == "Lucca")
lt = di_render.render_province(lucca, adama, lucca["attention"]).splitlines()
i = [n for n, l in enumerate(lt) if "RELEV" in l][0]
for l in lt[i:i+5]:
    print("   |", l[:150])
print("  the flag attention['NOT_A_COMMERCIAL_INSTRUCTION'] =",
      lucca["attention"]["NOT_A_COMMERCIAL_INSTRUCTION"], "-> printed in the card:",
      "NOT_A_COMMERCIAL_INSTRUCTION" in "\n".join(lt))
print("  the list adama['FORBIDDEN_OUTPUTS_NOT_EMITTED'] -> printed in the card:",
      "FORBIDDEN" in "\n".join(lt))

print("\nWHICH PROVINCES GET A CARD AT ALL?")
rep = open(os.path.join(HERE, "..", "engine", "di_report.py"), encoding="utf-8").read()
line = [l for l in rep.splitlines() if 'for p in (' in l][0]
print("  di_report.py:", line.strip())
print(f"  provinces with a rendered card: 3 of {len(cells)}")
shown = ("Firenze", "Siena", "Lucca")
missing = [(c['province'], c['observation']['value_pct'])
           for c in sorted(cells, key=lambda x: -x['observation']['value_pct'])
           if c['province'] not in shown]
print(f"  never rendered, by reading, highest first: {missing}")
