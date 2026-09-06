# Is the published_at-vs-document-date drift limited to the two vine slots,
# or systemic across all 46 preserved ARPAV docs?
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAN = ROOT / "manifests" / "arpav-docs-manifest.jsonl"

rows = [json.loads(l) for l in MAN.read_text(encoding="utf-8").splitlines() if l.strip()]
print(f"rows in arpav-docs-manifest.jsonl : {len(rows)}")

drift = []
nodate = []
for r in rows:
    p = ROOT / r["raw_path"]
    if not p.exists():
        continue
    blob = p.read_bytes()
    m = re.search(rb"/CreationDate\s*\(D:(\d{4})(\d{2})(\d{2})", blob)
    pub = str(r.get("published_at", ""))[:10]
    if not m:
        nodate.append((r["raw_path"], r["document_title"][:40], pub))
        continue
    cy, cm, cd = m.group(1).decode(), m.group(2).decode(), m.group(3).decode()
    creation = f"{cy}-{cm}-{cd}"
    if pub[:4] != cy:
        drift.append((r["document_title"][:44], pub, creation,
                      int(cy) - int(pub[:4] or 0)))

print(f"\nfiles whose published_at YEAR != PDF CreationDate YEAR : {len(drift)}")
print(f"{'document_title':46s} {'published_at':12s} {'PDF created':12s} {'yrs off':>7s}")
for t, pub, cr, d in sorted(drift, key=lambda x: -abs(x[3])):
    print(f"{t:46s} {pub:12s} {cr:12s} {d:>7d}")

print(f"\nfiles with NO parseable /CreationDate : {len(nodate)}")
for rp, t, pub in nodate:
    print(f"   {rp}  {t}  published_at={pub}")
