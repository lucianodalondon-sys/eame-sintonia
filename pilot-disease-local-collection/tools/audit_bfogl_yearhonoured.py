import json, glob, os, re
D = r"C:\disease-local-collection-italy\pilot-disease-local-collection\raw\F3b\bfogl_by_year"
sets = {}
for f in sorted(glob.glob(os.path.join(D, "*.json"))):
    y = re.search(r"_(\d{4})\.json$", f).group(1)
    j = json.load(open(f, encoding="utf-8"))
    sets[y] = {r["codice_stazione"] for r in j["data"]}

ys = sorted(sets)
print("year -> n_stations")
for y in ys:
    print(" ", y, len(sets[y]))

print("\nreal roster change between adjacent distinct groups:")
reps = ["2010", "2013", "2016", "2017", "2018", "2019", "2020"]
for a, b in zip(reps, reps[1:]):
    added = sets[b] - sets[a]
    removed = sets[a] - sets[b]
    print(f"  {a} -> {b}: +{sorted(added)} -{sorted(removed)}")

# is 2019 really identical to 2024/2025/2026 in station membership?
print("\n2019 == 2024 == 2025 == 2026 station sets:",
      sets["2019"] == sets["2024"] == sets["2025"] == sets["2026"])
print("2010 == 2026 station sets:", sets["2010"] == sets["2026"])
print("symmetric difference 2010 vs 2026:", sorted(sets["2010"] ^ sets["2026"]))
