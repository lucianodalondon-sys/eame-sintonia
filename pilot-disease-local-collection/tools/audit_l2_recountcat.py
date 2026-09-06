import json, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)

R = json.load(open(P('manifests/daily-series-recount.json'), encoding='utf-8'))
LW = R['leaf_wetness']
print("leaf_wetness entries:", len(LW))
print()
print("%-42s %-6s %-6s %-8s %-9s %s" % ("station", "cat_y", "pres_y", "days", "pct", "catalog-years NOT preserved"))
diff_any = 0
for e in sorted(LW, key=lambda e: -e['window_coverage_pct']):
    cy = set(e['catalog_years']); py = set(e['years_preserved'])
    d = sorted(cy - py)
    if d: diff_any += 1
    print("%-42s %-6d %-6d %-8d %-9s %s" % (e['stazione'][:42], len(cy), len(py),
          e['days_in_window_2014_2025'], e['window_coverage_pct'], d or '-'))
print()
print("entries where catalog_years != years_preserved:", diff_any)
print("sum of preserved leaf-wetness (station,year):", sum(len(e['years_preserved']) for e in LW))
print("sum of catalogue-declared leaf-wetness (station,year):", sum(len(e['catalog_years']) for e in LW))
print()
print(">= 99.4 strict from the recount's own pct field:",
      sum(1 for e in LW if e['window_coverage_pct'] >= 99.4), "of", len(LW))
print("values between 99.35 and 99.4:", [(e['stazione'], e['window_coverage_pct']) for e in LW
                                          if 99.0 <= e['window_coverage_pct'] < 99.4])

st = R['sensor_types']
print()
print("=== sensor_types: stations x years implied grid vs actual files ===")
for k, v in st.items():
    print("  %-8s stations=%2d years=%2d -> implied grid=%3d ; files=%3d ; shortfall=%d" %
          (k, v['stations'], len(v['years']), v['stations'] * len(v['years']), v['files'],
           v['stations'] * len(v['years']) - v['files']))
