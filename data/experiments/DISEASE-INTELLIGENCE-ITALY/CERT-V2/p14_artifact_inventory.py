#!/usr/bin/env python3
"""
CERT-V2 / STEP 14 — EVERY PATH THE PILOT READS, AND WHETHER IT IS IN GIT.

A result that depends on a path outside the repository is not reproducible, however true it
happens to be on the machine that produced it. This scans the pilot's own source for every
string that looks like a filesystem path or a URL, resolves it, and records four states:

  IN_GIT              tracked at this commit; the result can be replayed by anyone
  ON_DISK_NOT_IN_GIT  present here, absent from a fresh clone
  ABSENT              not present at all from this checkout
  NETWORK             a live endpoint; reproducibility depends on a third party staying up

Out: p14_artifact_inventory.json
"""
import json, os, re, subprocess, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.abspath(os.path.join(HERE, ".."))
REPO = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=EXP,
                      capture_output=True, text=True).stdout.strip()

SCAN_DIRS = [os.path.join(EXP, "ENGINE"), os.path.join(EXP, "CASES"),
             os.path.join(EXP, "TOSCANA"), os.path.join(EXP, "ABRUZZO")]

ABS_PATH = re.compile(r"""["']((?:/(?:home|tmp|var|Users|mnt)|[A-Za-z]:[\\/])[^"']{3,})["']""")
URL = re.compile(r"""["'](https?://[^"']+)["']""")
TMPISH = re.compile(r"""["'](/tmp/[^"']*|\.?/?tmp[_/][^"']*)["']""")


def tracked(path):
    if not REPO:
        return False
    r = subprocess.run(["git", "ls-files", "--error-unmatch", "--", path],
                       cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def rel(p):
    try:
        return os.path.relpath(p, REPO).replace("\\", "/")
    except Exception:
        return p


def main():
    findings, files_scanned = [], 0
    for d in SCAN_DIRS:
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            if "__pycache__" in root or os.sep + "RAW" in root:
                continue
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                p = os.path.join(root, fn)
                files_scanned += 1
                src = open(p, encoding="utf-8", errors="replace").read()
                for m in ABS_PATH.finditer(src):
                    hit = m.group(1)
                    exists = os.path.exists(hit)
                    findings.append({
                        "SOURCE_FILE": rel(p), "KIND": "ABSOLUTE_PATH", "VALUE": hit,
                        "STATE": ("IN_GIT" if exists and tracked(hit)
                                  else "ON_DISK_NOT_IN_GIT" if exists else "ABSENT"),
                        "LINE": src[:m.start()].count("\n") + 1})
                for m in TMPISH.finditer(src):
                    findings.append({
                        "SOURCE_FILE": rel(p), "KIND": "TMP_PATH", "VALUE": m.group(1),
                        "STATE": "ON_DISK_NOT_IN_GIT" if os.path.exists(m.group(1)) else "ABSENT",
                        "LINE": src[:m.start()].count("\n") + 1})
                for m in URL.finditer(src):
                    findings.append({
                        "SOURCE_FILE": rel(p), "KIND": "NETWORK", "VALUE": m.group(1),
                        "STATE": "NETWORK",
                        "LINE": src[:m.start()].count("\n") + 1})

    # the evidence artefacts the delivery itself points at
    named = ["data/experiments/DISEASE-INTELLIGENCE-ITALY/ENGINE/gates.json",
             "data/experiments/DISEASE-INTELLIGENCE-ITALY/ENGINE/answer_sheet.json",
             "data/experiments/DISEASE-INTELLIGENCE-ITALY/ENGINE/capability_matrix.json",
             "data/experiments/DISEASE-INTELLIGENCE-ITALY/ENGINE/automation_probe.json",
             "data/experiments/DISEASE-INTELLIGENCE-ITALY/ENGINE/regional_coverage.json",
             "data/experiments/DISEASE-INTELLIGENCE-ITALY/CASES/OLIVO-BACTROCERA-TOSCANA/collection_index.json",
             "data/experiments/DISEASE-INTELLIGENCE-ITALY/CASES/VITE-OIDIO-TOSCANA/collection_index.json",
             "data/experiments/DISEASE-INTELLIGENCE-ITALY/CASES/FRUMENTO-SEPTORIA-TOSCANA/collection_index.json",
             "italia-portale/client/meeting-intelligence-snapshot.json",
             "italia-portale/client/italy-label-verdicts.js"]
    named_state = {}
    for n in named:
        full = os.path.join(REPO, n)
        named_state[n] = {"IN_GIT": tracked(full), "ON_DISK": os.path.exists(full),
                          "sha256": (hashlib.sha256(open(full, "rb").read()).hexdigest()[:16]
                                     if os.path.exists(full) else None)}

    # do the collection indexes carry a collection timestamp at all?
    clocks = {}
    for c in ("OLIVO-BACTROCERA-TOSCANA", "VITE-OIDIO-TOSCANA", "FRUMENTO-SEPTORIA-TOSCANA"):
        p = os.path.join(EXP, "CASES", c, "collection_index.json")
        idx = json.load(open(p))
        keys = sorted(idx.keys())
        reqkeys = sorted({k for r in idx.get("requests", []) for k in r})
        clocks[c] = {
            "INDEX_KEYS": keys, "REQUEST_KEYS": reqkeys,
            "HAS_REFRESH_ATTEMPT_AT": any("attempt" in k.lower() for k in keys + reqkeys),
            "HAS_COLLECTED_AT": any(("collected" in k.lower() or "fetched" in k.lower()
                                     or "timestamp" in k.lower() or k.lower().endswith("_at"))
                                    for k in keys + reqkeys),
            "HAS_REFRESH_STATUS": any("status" in k.lower() for k in keys + reqkeys),
            "HAS_SOURCE_PUBLISHED_AT": any("publish" in k.lower() for k in keys + reqkeys)}

    bad = [f for f in findings if f["STATE"] in ("ON_DISK_NOT_IN_GIT", "ABSENT")]
    out = {"REPO": REPO, "PY_FILES_SCANNED": files_scanned,
           "FINDINGS": findings,
           "NOT_REPRODUCIBLE_REFERENCES": bad,
           "NAMED_EVIDENCE_ARTEFACTS": named_state,
           "COLLECTION_INDEX_CLOCK_FIELDS": clocks,
           "REPRODUCIBILITY": "FAIL" if bad else "PASS"}
    json.dump(out, open(os.path.join(HERE, "p14_artifact_inventory.json"), "w"),
              indent=1, default=str)

    print(f"python files scanned: {files_scanned}")
    print(f"references that a fresh clone cannot resolve: {len(bad)}")
    for f in bad:
        print(f"  {f['STATE']:20s} {f['SOURCE_FILE']}:{f['LINE']}  {f['VALUE'][:110]}")
    print("\nnamed evidence artefacts:")
    for k, v in named_state.items():
        print(f"  IN_GIT={str(v['IN_GIT']):5s} ON_DISK={str(v['ON_DISK']):5s} {k}")
    print("\ncollection index clock fields:")
    for k, v in clocks.items():
        print(f"  {k}: collected_at={v['HAS_COLLECTED_AT']} attempt_at={v['HAS_REFRESH_ATTEMPT_AT']} "
              f"status={v['HAS_REFRESH_STATUS']} published_at={v['HAS_SOURCE_PUBLISHED_AT']}")
        print(f"      index keys   : {v['INDEX_KEYS']}")
        print(f"      request keys : {v['REQUEST_KEYS']}")
    print(f"\nREPRODUCIBILITY = {out['REPRODUCIBILITY']}")


if __name__ == "__main__":
    main()
