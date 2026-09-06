import json, os
ROOT = r"C:\disease-local-collection-italy\pilot-disease-local-collection"

def load(p):
    rows = []
    with open(os.path.join(ROOT, "manifests", p), encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    return rows

def norm(u):
    return u.replace("/@@download/file", "").rstrip("/")

def report(label, good_name, failed_name):
    good = load(good_name)
    bad = load(failed_name)
    print("=== " + label)
    print("  good manifest %-42s rows=%d PRESERVED=%d" %
          (good_name, len(good), sum(1 for r in good if r.get("preservation") == "PRESERVED")))
    print("  FAILED manifest %-40s rows=%d PRESERVED=%d" %
          (failed_name, len(bad), sum(1 for r in bad if r.get("preservation") == "PRESERVED")))
    gp = [r for r in good if r.get("preservation") == "PRESERVED"]
    bp = [r for r in bad if r.get("preservation") == "PRESERVED"]
    print("  TOTAL rows asserting PRESERVED across the two:", len(gp) + len(bp))
    gu = set(norm(r["source_url"]) for r in gp)
    bu = set(norm(r["source_url"]) for r in bp)
    print("  distinct normalized source_url  good=%d failed=%d union=%d overlap=%d" %
          (len(gu), len(bu), len(gu | bu), len(gu & bu)))
    gs = set(r["sha256"] for r in gp)
    bs = set(r["sha256"] for r in bp)
    print("  distinct sha256                 good=%d failed=%d union=%d overlap=%d" %
          (len(gs), len(bs), len(gs | bs), len(gs & bs)))
    # api_url is the stable identity field in both
    ga = set(r["api_url"] for r in gp)
    ba = set(r["api_url"] for r in bp)
    print("  distinct api_url                good=%d failed=%d union=%d overlap=%d" %
          (len(ga), len(ba), len(ga | ba), len(ga & ba)))
    print()

report("F8 DOCS", "arpav-docs-manifest.jsonl",
       "FAILED-arpav-docs-manifest-htmlshells.jsonl")
report("F7 MONTHLY", "arpav-monthly-manifest.jsonl",
       "FAILED-arpav-monthly-manifest-htmlshells.jsonl")

# Does the .verified variant add a THIRD assertion of the same 46?
v = load("arpav-docs-manifest.verified.jsonl")
d = load("arpav-docs-manifest.jsonl")
print("=== third-copy check (F8)")
print("  arpav-docs-manifest.jsonl          PRESERVED rows:",
      sum(1 for r in d if r.get("preservation") == "PRESERVED"))
print("  arpav-docs-manifest.verified.jsonl PRESERVED rows:",
      sum(1 for r in v if r.get("preservation") == "PRESERVED"))
print("  sha256 sets identical between them:",
      set(r["sha256"] for r in d) == set(r["sha256"] for r in v))
print("  naive `grep -c PRESERVED manifests/*.jsonl` F8 total:",
      len(d) + len(v) + 46)
