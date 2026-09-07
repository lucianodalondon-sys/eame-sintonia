#!/usr/bin/env python3
"""RT6-H. Try to make the tool emit banned vocabulary through a LEGITIMATE path:
a province name, an org name, a comune, a source band label, an audit date.
Two parts: (1) what the REAL data already contains, (2) what the renderer does with a
source string it is handed."""
import os, sys, re, json, collections, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_core, di_observe, di_adama, di_render

BANNED = ("ACT_NOW", "SALES_READY", "BUY", "SELL", "OPPORTUNITY",
          "CONTACT_NOW", "COMMERCIAL_OPPORTUNITY")
CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)
sheet = di_core.load_sheet()
loaded = di_core.load_visits(CASE, sheet, AS_OF)
V = loaded["visits"]

print("=== 1. WHAT THE REAL SOURCE STRINGS ALREADY CONTAIN ===")
for f in ("province", "comune", "org"):
    vals = sorted({str(v.get(f)) for v in V if v.get(f)})
    hits = [x for x in vals if any(b in x.upper() for b in BANNED)]
    print(f"  distinct {f:9s}: {len(vals):5d}   banned-substring hits: {len(hits)} {hits[:6]}")
print("  source band labels in the semantic sheet:",
      [(b['label'], b.get('meaning')) for b in sheet['SOURCE_ACTION_BANDS']['BANDS']])
print("  AUDIT_DATE read from the verdict file:",
      di_adama.read_label_verdicts()["audit_date"])

print("\n=== 2. DOES ANYTHING SANITISE A SOURCE STRING BEFORE IT IS PRINTED? ===")
src = open(os.path.join(HERE, "..", "engine", "di_core.py"), encoding="utf-8").read()
for line in src.splitlines():
    if "nome_area" in line or "org_name" in line or "name_4" in line:
        print("  di_core.py:", line.strip())
rsrc = open(os.path.join(HERE, "..", "engine", "di_render.py"), encoding="utf-8").read()
print("  di_render.py mentions of any allow-list / sanitiser / escape:",
      [w for w in ("sanit", "allow", "escape", "whitelist", "VOCAB", "assert", "banned")
       if w in rsrc.lower()] or "NONE")

print("\n=== 3. FEED THE RENDERER A POISONED SOURCE STRING (the legitimate path) ===")
poisoned = [dict(v) for v in V]
n = 0
for v in poisoned:
    if v["province"] == "Lucca":
        v["province"] = "Lucca ACT_NOW"          # as if nome_area read this in the source
        n += 1
print(f"  rewrote nome_area on {n} Lucca visits to 'Lucca ACT_NOW'")
adama = di_adama.relevance("Olive", "Olive Fruit Fly")
c = di_observe.cell(poisoned, sheet, "Lucca ACT_NOW", "ACTIVE_INFESTATION_COUNT", AS_OF)
at = di_adama.attention_class(c, adama)
txt = di_render.render_province(c, adama, at)
print("  first line of the rendered card:")
print("   ", txt.splitlines()[0])
hits = {w: txt.upper().count(w) for w in BANNED if w in txt.upper()}
print(f"  G10's own check on that rendered card: "
      f"{'FAIL' if hits else 'PASS'}  {hits}")

print("\n=== 4. POISON THE SOURCE'S OWN COLOUR BAND (the sheet is an input too) ===")
s2 = json.loads(json.dumps({k: v for k, v in sheet.items() if not k.startswith("_")}))
s2["SOURCE_ACTION_BANDS"]["BANDS"][0]["meaning"] = "no commercial opportunity yet"
s2["_by_canonical"] = sheet["_by_canonical"]; s2["_by_id"] = sheet["_by_id"]
c2 = di_observe.cell(V, s2, "Firenze", "ACTIVE_INFESTATION_COUNT", AS_OF)
t2 = di_render.render_province(c2, adama, di_adama.attention_class(c2, adama))
band_line = [l for l in t2.splitlines() if "banda" in l][0]
print("  ", band_line.strip())
h2 = {w: t2.upper().count(w) for w in BANNED if w in t2.upper()}
print(f"  G10's own check: {'FAIL' if h2 else 'PASS'}  {h2}")
reg = di_render.render_region([c2], adama)
print("  region card band line:", [l for l in reg.splitlines() if "bandas" in l][0].strip())

print("\n=== 5. IS THERE ANY OUTPUT-SIDE VOCABULARY CHECK AT ALL? ===")
for f in ("di_render.py", "di_report.py", "di_adama.py", "di_observe.py", "di_core.py"):
    t = open(os.path.join(HERE, "..", "engine", f), encoding="utf-8").read()
    guard = any(b in t and ("raise" in t.split(b)[0][-300:] or "assert" in t.split(b)[0][-300:])
                for b in BANNED)
    print(f"  {f:14s} contains banned tokens: "
          f"{[b for b in BANNED if b in t]}   raises/asserts on them: {guard}")
