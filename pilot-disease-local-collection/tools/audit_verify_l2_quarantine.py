#!/usr/bin/env py
"""Independent re-verification of the L2 quarantine-labelling finding.
Read-only. Does not touch raw/ or manifests/."""
import json, os, sys, glob, hashlib, collections

ROOT = r"C:\disease-local-collection-italy\pilot-disease-local-collection"
os.chdir(ROOT)

def rows(p):
    out = []
    with open(p, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                out.append(json.loads(ln))
    return out

print("=" * 72)
print("A. THE TWO FAILED-*.jsonl FILES, ROW BY ROW")
print("=" * 72)
failed_files = sorted(glob.glob("manifests/FAILED-*.jsonl"))
failed_rows_all = []
for p in failed_files:
    rs = rows(p)
    failed_rows_all.extend(rs)
    dangling = [r for r in rs if not os.path.exists(r.get("raw_path", ""))]
    exists = len(rs) - len(dangling)
    # does raw_path point INTO the quarantine folder?
    into_quar = [r for r in rs if "_failed-captures" in r.get("raw_path", "")]
    into_good = [r for r in rs if r.get("raw_path", "").startswith(("raw/F7-arpav-bollettino-mese", "raw/F8-arpav-agrometeo-docs"))]
    keyset = set()
    for r in rs:
        keyset |= set(r.keys())
    # any key OR value anywhere mentioning failure
    bad_words = ("fail", "quarant", "invalid", "shell", "reject", "discard", "bad")
    flag_keys = sorted(k for k in keyset if any(w in k.lower() for w in bad_words))
    flag_vals = collections.Counter()
    for r in rs:
        for k, v in r.items():
            if isinstance(v, str) and any(w in v.lower() for w in bad_words):
                flag_vals[f"{k}={v[:70]}"] += 1
    print(f"\n{p}")
    print(f"   rows: {len(rs)}")
    print(f"   preservation values : {sorted(set(r.get('preservation','<MISSING>') for r in rs))}")
    print(f"   media_type values   : {sorted(set(r.get('media_type','<MISSING>') for r in rs))}")
    print(f"   http_status values  : {sorted(set(r.get('http_status','<MISSING>') for r in rs))}")
    print(f"   dedup values        : {sorted(set(r.get('dedup','<MISSING>') for r in rs))}")
    print(f"   raw_path EXISTS on disk : {exists}")
    print(f"   raw_path DANGLING       : {len(dangling)}")
    print(f"   raw_path -> quarantine folder : {len(into_quar)}")
    print(f"   raw_path -> GOOD folders      : {len(into_good)}")
    print(f"   keys containing fail/quarant/invalid/shell : {flag_keys}")
    print(f"   VALUES containing those words             : {dict(flag_vals) if flag_vals else '{}'}")
    print(f"   all keys present: {sorted(keyset)}")

print()
print("=" * 72)
print("B. IS ANY FAILED sha256 ACTUALLY ON DISK ANYWHERE (incl. quarantine)?")
print("=" * 72)
# hash every quarantined file
quar_sha = {}
for dirpath, _, fns in os.walk("raw/_failed-captures"):
    for fn in fns:
        fp = os.path.join(dirpath, fn)
        h = hashlib.sha256(open(fp, "rb").read()).hexdigest()
        quar_sha.setdefault(h, []).append(fp.replace("\\", "/"))
print(f"quarantined files on disk : {sum(len(v) for v in quar_sha.values())}")
print(f"distinct sha256 in quarantine : {len(quar_sha)}")

failed_sha = [r["sha256"] for r in failed_rows_all]
print(f"FAILED-manifest rows          : {len(failed_sha)}")
print(f"distinct sha in FAILED rows   : {len(set(failed_sha))}")
matched = [s for s in failed_sha if s in quar_sha]
print(f"FAILED rows whose sha IS a quarantined file : {len(matched)}")
print(f"   -> so the bytes ARE preserved, only the PATH is wrong: {len(matched)==len(failed_sha)}")

print()
print("=" * 72)
print("C. MAGIC BYTES OF THE QUARANTINED FILES (are they really HTML shells?)")
print("=" * 72)
magic = collections.Counter()
for dirpath, _, fns in os.walk("raw/_failed-captures"):
    for fn in fns:
        with open(os.path.join(dirpath, fn), "rb") as fh:
            head = fh.read(16)
        if head.startswith(b"%PDF"):
            magic["PDF"] += 1
        elif head[:1] in (b"<", b"\n", b"\r", b" ") or b"<!DOC" in head or b"<html" in head.lower():
            magic["HTML/text"] += 1
        else:
            magic[repr(head[:8])] += 1
print(dict(magic))

print()
print("=" * 72)
print("D. THE GOOD DOWNLOADS: are they real PDFs, and do they collide with FAILED?")
print("=" * 72)
for folder, fm in (("raw/F8-arpav-agrometeo-docs", "manifests/FAILED-arpav-docs-manifest-htmlshells.jsonl"),
                   ("raw/F7-arpav-bollettino-mese", "manifests/FAILED-arpav-monthly-manifest-htmlshells.jsonl")):
    good_sha = set()
    gmagic = collections.Counter()
    n = 0
    for dirpath, _, fns in os.walk(folder):
        for fn in fns:
            fp = os.path.join(dirpath, fn)
            b = open(fp, "rb").read()
            n += 1
            good_sha.add(hashlib.sha256(b).hexdigest())
            gmagic["PDF" if b[:4] == b"%PDF" else "NOT-PDF:" + repr(b[:8])] += 1
    fsha = set(r["sha256"] for r in rows(fm))
    print(f"\n{folder}")
    print(f"   files on disk: {n}  distinct sha: {len(good_sha)}  magic: {dict(gmagic)}")
    print(f"   sha OVERLAP with its FAILED manifest: {len(good_sha & fsha)}")

print()
print("=" * 72)
print("E. NAIVE 'COUNT PRESERVED ACROSS manifests/' -- what does it return TODAY?")
print("=" * 72)
tot = 0
per = []
for p in sorted(glob.glob("manifests/*.jsonl")):
    c = 0
    with open(p, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("preservation") == "PRESERVED":
                c += 1
    if c:
        per.append((c, p))
        tot += c
for c, p in per:
    print(f"   {c:5d}  {p}")
print(f"   {tot:5d}  TOTAL naive PRESERVED across manifests/")

print()
print("=" * 72)
print("F. DE-DUPLICATE: real distinct preserved artifacts")
print("=" * 72)
# duplicate-manifest pairs
pairs = [("manifests/arpav-docs-manifest.jsonl", "manifests/arpav-docs-manifest.verified.jsonl"),
         ("manifests/arpav-monthly-manifest.jsonl", "manifests/arpav-monthly-manifest.verified.jsonl")]
for a, b in pairs:
    if os.path.exists(a) and os.path.exists(b):
        sa = set(r["sha256"] for r in rows(a))
        sb = set(r["sha256"] for r in rows(b))
        pa = set(r["raw_path"] for r in rows(a))
        pb = set(r["raw_path"] for r in rows(b))
        print(f"   {os.path.basename(a)} ({len(sa)} sha) vs {os.path.basename(b)} ({len(sb)} sha)")
        print(f"      sha identical set? {sa == sb}   raw_path identical set? {pa == pb}")

# global: union of raw_path over the NON-failed manifests, where file exists
real = set()
for p in sorted(glob.glob("manifests/*.jsonl")):
    if os.path.basename(p).startswith("FAILED-"):
        continue
    if "inventory" in os.path.basename(p) and "raw-file" not in os.path.basename(p):
        continue
    if os.path.basename(p) == "raw-file-inventory.jsonl":
        continue
    if os.path.basename(p) == "daily-series-provenance.jsonl":
        continue
    for r in rows(p):
        if r.get("preservation") == "PRESERVED" and r.get("raw_path"):
            real.add(r["raw_path"].replace("\\", "/"))
print(f"\n   distinct raw_path with PRESERVED in non-FAILED manifests: {len(real)}")
onDisk = sum(1 for p in real if os.path.exists(p))
print(f"   of those, files that EXIST on disk: {onDisk}   dangling: {len(real)-onDisk}")

print()
print("=" * 72)
print("G. DOES ANY DOC OUTSIDE THE FAILED FILES CALL THEM FAILED?")
print("=" * 72)
for p in ["manifests/collection-manifest.json", "manifests/arpav-docs-preserve.log",
          "manifests/arpav-monthly-preserve.log", "LOCAL-DISEASE-COLLECTION-HANDOFF.md"]:
    if not os.path.exists(p):
        continue
    txt = open(p, encoding="utf-8", errors="replace").read()
    hits = [l.strip() for l in txt.splitlines()
            if any(w in l.lower() for w in ("failed-capture", "quarant", "html shell", "htmlshell", "html-shell"))]
    print(f"\n   {p}: {len(hits)} mentions")
    for h in hits[:8]:
        print(f"      {h[:160]}")
