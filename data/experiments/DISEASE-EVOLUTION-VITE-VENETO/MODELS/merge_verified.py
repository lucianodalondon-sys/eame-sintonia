#!/usr/bin/env python3
"""
Assemble OBSERVATIONS/verified_evidence.json from the two adversarial extraction runs.

Takes only VERIFIER output (the corrected, re-checked set), never the raw extractor
output, so a quote that failed the verbatim or host check cannot reach the dataset.
Then re-proves verbatim membership itself, in this process, against the NORMALIZED text.
Trusting the verifier's word that it checked would defeat the point of having one.
"""
import json, glob, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NORM = os.path.join(ROOT, "NORMALIZED")
WF = "/root/.claude/projects/-home-user-eame-sintonia/225e1b33-2ad9-51d4-af35-56626f84e287/subagents/workflows/wf_*/journal.jsonl"

def collect():
    rows = {}
    for p in glob.glob(WF):
        for line in open(p):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("type") != "result":
                continue
            v = r.get("result")
            if isinstance(v, dict) and "corrected_vine_peronospora_quotes" in v:
                rows[str(v.get("year"))] = v
    return rows

def norm_text(key):
    p = os.path.join(NORM, f"annata-agraria-{key}.txt")
    return open(p, encoding="utf-8").read() if os.path.exists(p) else None

def season_year(key, v):
    """Calendar year of the spring-summer vine season this document describes."""
    y = v.get("vine_season_calendar_year_confirmed")
    if isinstance(y, int) and 1990 <= y <= 2026:
        return y, "verifier"
    m = re.fullmatch(r"(\d{4})-(\d{2})", key)
    if m:                       # agrarian year 1 Nov Y -> 31 Oct Y+1; vine season = Y+1
        return int(m.group(1)) + 1, "agrarian_year_rule"
    if re.fullmatch(r"\d{4}", key):
        return int(key), "calendar_key"
    return None, "UNRESOLVED"

if __name__ == "__main__":
    rows = collect()
    out, problems = {}, []
    for key, v in sorted(rows.items()):
        t = norm_text(key)
        if t is None:
            problems.append({"doc": key, "problem": "no NORMALIZED text found"})
            continue
        sy, how = season_year(key, v)
        kept, dropped = [], []
        for q in v.get("corrected_vine_peronospora_quotes", []):
            s = q.get("quote_it", "")
            n = t.count(s)
            if n >= 1:
                q = dict(q); q["_verbatim_occurrences"] = n
                kept.append(q)
            else:
                dropped.append({"quote": s[:160], "reason": "NOT VERBATIM in NORMALIZED text (re-proved here, independently of the verifier)"})
        if dropped:
            problems.append({"doc": key, "dropped": dropped})
        out[key] = {
            "doc_key": key,
            "vine_season_year": sy,
            "season_year_resolved_by": how,
            "verifier_verdict": v.get("verdict"),
            "has_explicit_severity": bool(v.get("year_has_usable_severity_signal")),
            "mention_only": bool(v.get("year_has_mention_only")),
            "n_quotes": len(kept),
            "quotes": kept,
            "quotes_dropped_on_reproof": dropped,
            "host_misattributions_caught": v.get("host_misattributions", []),
            "missed_quotes_recovered": len(v.get("missed_vine_peronospora_quotes", [])),
            "verifier_notes": v.get("verifier_notes", ""),
        }
    # collisions: two documents claiming the same vine season
    seen = {}
    for k, r in out.items():
        sy = r["vine_season_year"]
        seen.setdefault(sy, []).append(k)
    collisions = {sy: ks for sy, ks in seen.items() if len(ks) > 1}

    doc = {
        "note": ("Verifier-approved quotes only, re-proved verbatim in THIS process against "
                 "NORMALIZED/. A quote the verifier passed but that does not occur in the text "
                 "is dropped here and listed in quotes_dropped_on_reproof."),
        "n_documents": len(out),
        "n_with_explicit_severity": sum(1 for r in out.values() if r["has_explicit_severity"]),
        "n_mention_only": sum(1 for r in out.values() if r["mention_only"]),
        "n_no_statement": sum(1 for r in out.values() if not r["has_explicit_severity"] and not r["mention_only"] and r["n_quotes"] == 0),
        "season_year_collisions": collisions,
        "reproof_problems": problems,
        "per_document": out,
    }
    dest = os.path.join(ROOT, "OBSERVATIONS", "verified_evidence.json")
    json.dump(doc, open(dest, "w"), indent=1, ensure_ascii=False)

    print(f"{'DOC':9s} {'season':6s} {'by':18s} {'verdict':10s} {'sev':5s} {'ment':5s} {'nq':3s} {'drop':4s}")
    for k in sorted(out, key=lambda x: out[x]["vine_season_year"] or 0):
        r = out[k]
        print(f"{k:9s} {str(r['vine_season_year']):6s} {r['season_year_resolved_by']:18s} "
              f"{str(r['verifier_verdict']):10s} {str(r['has_explicit_severity'])[:5]:5s} "
              f"{str(r['mention_only'])[:5]:5s} {r['n_quotes']:3d} {len(r['quotes_dropped_on_reproof']):4d}")
    print(f"\ndocuments={doc['n_documents']}  explicit severity={doc['n_with_explicit_severity']}  "
          f"mention only={doc['n_mention_only']}  no statement={doc['n_no_statement']}")
    if collisions: print("SEASON COLLISIONS:", collisions)
    if problems:   print("REPROOF PROBLEMS:", json.dumps(problems, ensure_ascii=False)[:600])
    print(f"wrote {dest}")
