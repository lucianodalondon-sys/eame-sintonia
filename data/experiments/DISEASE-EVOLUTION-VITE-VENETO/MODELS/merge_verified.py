#!/usr/bin/env python3
"""
Assemble OBSERVATIONS/verified_evidence.json from the two adversarial extraction runs.

Takes only VERIFIER output (the corrected, re-checked set), never the raw extractor
output, so a quote that failed the verbatim or host check cannot reach the dataset.
Then re-proves verbatim membership itself, in this process, against the NORMALIZED text.
Trusting the verifier's word that it checked would defeat the point of having one.
"""
import json, glob, os, sys, re

# RISK_FORECAST != DISEASE_PRESENCE, enforced mechanically.
# A quote whose disease claim is carried by risk language is a forecast, not an outcome.
# Found the hard way: the 2017 report's only vine peronospora sentence is
# "...con un rischio basso di infezione di Peronospora...", which one pipeline coded as a
# severity signal. It is a model's risk category on one date, not a record of what happened.
RISK_LEXICON = [
    "rischio", "rischi ", "pericolo", "condizioni favorevoli", "condizioni predisponenti",
    "possibili infezioni", "possibile infezione", "previsione", "previsto", "atteso",
    "si prevede", "potenziale rischio", "allerta", "soglia di rischio",
]
OUTCOME_LEXICON = [
    "sono risultate", "e' risultata", "è risultata", "si sono manifestate", "sono state osservate",
    "sono comparse", "compaiono", "si sono verificate", "hanno colpito", "sono state segnalate",
    "riscontrate", "riscontrato", "presenza", "danni", "attacchi", "e' stata", "è stata",
    "sono state", "ha causato", "si e' manifestata", "si è manifestata", "virulenza",
]

def risk_flag(quote):
    q = quote.lower()
    risk = sorted({w.strip() for w in RISK_LEXICON if w in q})
    outc = sorted({w.strip() for w in OUTCOME_LEXICON if w in q})
    return risk, outc

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
    if m:
        # NOT an agrarian year. Checked against the documents themselves:
        # annata-agraria-2004-05.pdf is internally titled "PERIODO GENNAIO-NOVEMBRE 2005",
        # and 2000-01 is "GENNAIO-NOVEMBRE 2001". The YYYY-YY filename denotes the report
        # for the SECOND year. The per-document verifier resolves this from the printed
        # header and takes precedence; this is only the fallback.
        return int(m.group(1)) + 1, "filename_second_year_fallback"
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
                risk, outc = risk_flag(s)
                q["_risk_language"] = risk
                q["_outcome_language"] = outc
                # risk words present and no outcome verb -> this is a forecast, not a record
                q["_is_risk_not_outcome"] = bool(risk) and not outc
                kept.append(q)
            else:
                dropped.append({"quote": s[:160], "reason": "NOT VERBATIM in NORMALIZED text (re-proved here, independently of the verifier)"})
        if dropped:
            problems.append({"doc": key, "dropped": dropped})
        n_risk_only = sum(1 for q in kept if q["_is_risk_not_outcome"])
        outcome_quotes = [q for q in kept if not q["_is_risk_not_outcome"]]
        out[key] = {
            "doc_key": key,
            "vine_season_year": sy,
            "season_year_resolved_by": how,
            "verifier_verdict": v.get("verdict"),
            "has_explicit_severity_as_reported": bool(v.get("year_has_usable_severity_signal")),
            "n_quotes_that_are_risk_not_outcome": n_risk_only,
            "n_outcome_quotes": len(outcome_quotes),
            "has_explicit_severity": bool(v.get("year_has_usable_severity_signal")) and len(outcome_quotes) > 0,
            "severity_downgraded_by_risk_rule": bool(v.get("year_has_usable_severity_signal")) and len(outcome_quotes) == 0,
            "mention_only": bool(v.get("year_has_mention_only")),
            "n_quotes": len(kept),
            "quotes": kept,
            "quotes_dropped_on_reproof": dropped,
            "host_misattributions_caught": v.get("host_misattributions", []),
            "missed_quotes_recovered": len(v.get("missed_vine_peronospora_quotes", [])),
            "verifier_notes": v.get("verifier_notes", ""),
        }
    # collisions: two documents describing the SAME vine season.
    # ARPAV published two reports for 2005 (a Jan-Nov edition filed as "2004-05" and a
    # full-year edition filed as "2005"). Counting both would put one season into the
    # backtest twice and inflate every count downstream. Seasons are therefore collapsed:
    # one row per vine season, quotes unioned, sources listed.
    seen = {}
    for k, r in out.items():
        seen.setdefault(r["vine_season_year"], []).append(k)
    collisions = {sy: ks for sy, ks in seen.items() if len(ks) > 1}

    seasons = {}
    for sy, keys in sorted(seen.items()):
        rs = [out[k] for k in keys]
        qs, seenq = [], set()
        for r in rs:
            for q in r["quotes"]:
                if q["quote_it"] not in seenq:
                    seenq.add(q["quote_it"]); qs.append(dict(q, _from_doc=r["doc_key"]))
        outcome_qs = [q for q in qs if not q["_is_risk_not_outcome"]]
        seasons[sy] = {
            "vine_season_year": sy,
            "source_documents": keys,
            "n_source_documents": len(keys),
            "n_quotes": len(qs),
            "n_outcome_quotes": len(outcome_qs),
            "has_explicit_severity": any(r["has_explicit_severity"] for r in rs),
            "mention_only": (not any(r["has_explicit_severity"] for r in rs)
                             and any(r["mention_only"] for r in rs)),
            "no_statement": len(qs) == 0,
            "severity_downgraded_by_risk_rule": any(r["severity_downgraded_by_risk_rule"] for r in rs),
            "quotes": qs,
        }

    doc = {
        "note": ("Verifier-approved quotes only, re-proved verbatim in THIS process against "
                 "NORMALIZED/. A quote the verifier passed but that does not occur in the text "
                 "is dropped here and listed in quotes_dropped_on_reproof."),
        "n_documents": len(out),
        "n_with_explicit_severity": sum(1 for r in out.values() if r["has_explicit_severity"]),
        "n_downgraded_by_risk_rule": sum(1 for r in out.values() if r["severity_downgraded_by_risk_rule"]),
        "downgraded_docs": [k for k, r in out.items() if r["severity_downgraded_by_risk_rule"]],
        "risk_rule": ("RISK_FORECAST != DISEASE_PRESENCE, applied mechanically: a quote carrying risk "
                      "language and no outcome verb is a forecast, not a record, and does not count "
                      "toward a season's severity signal."),
        "n_mention_only": sum(1 for r in out.values() if r["mention_only"]),
        "n_no_statement": sum(1 for r in out.values() if not r["has_explicit_severity"] and not r["mention_only"] and r["n_quotes"] == 0),
        "n_distinct_vine_seasons": len(seasons),
        "season_year_collisions": collisions,
        "collision_rule": ("Two documents describing the same vine season are collapsed into one "
                           "season row with their quotes unioned. ARPAV published two reports for "
                           "2005; counting both would put one season into the backtest twice."),
        "seasons_with_explicit_severity": sorted(sy for sy, r in seasons.items() if r["has_explicit_severity"]),
        "seasons_mention_only": sorted(sy for sy, r in seasons.items() if r["mention_only"]),
        "seasons_no_statement": sorted(sy for sy, r in seasons.items() if r["no_statement"]),
        "per_season": seasons,
        "reproof_problems": problems,
        "per_document": out,
    }
    dest = os.path.join(ROOT, "OBSERVATIONS", "verified_evidence.json")
    json.dump(doc, open(dest, "w"), indent=1, ensure_ascii=False)

    print(f"{'DOC':9s} {'season':6s} {'by':18s} {'verdict':10s} {'sev':5s} {'ment':5s} {'nq':3s} {'risk':4s} {'drop':4s}")
    for k in sorted(out, key=lambda x: out[x]["vine_season_year"] or 0):
        r = out[k]
        print(f"{k:9s} {str(r['vine_season_year']):6s} {r['season_year_resolved_by']:18s} "
              f"{str(r['verifier_verdict']):10s} {str(r['has_explicit_severity'])[:5]:5s} "
              f"{str(r['mention_only'])[:5]:5s} {r['n_quotes']:3d} {len(r['quotes_dropped_on_reproof']):4d}")
    print(f"\ndocuments={doc['n_documents']}  explicit severity={doc['n_with_explicit_severity']}  "
          f"mention only={doc['n_mention_only']}  no statement={doc['n_no_statement']}")
    print(f"downgraded by the risk-not-outcome rule: {doc['n_downgraded_by_risk_rule']} {doc['downgraded_docs']}")
    print(f"distinct vine seasons after collapsing duplicates: {doc['n_distinct_vine_seasons']}")
    print(f"  explicit severity: {len(doc['seasons_with_explicit_severity'])} {doc['seasons_with_explicit_severity']}")
    print(f"  mention only:      {len(doc['seasons_mention_only'])} {doc['seasons_mention_only']}")
    print(f"  no statement:      {len(doc['seasons_no_statement'])} {doc['seasons_no_statement']}")
    if collisions: print("SEASON COLLISIONS COLLAPSED:", collisions)
    if problems:   print("REPROOF PROBLEMS:", json.dumps(problems, ensure_ascii=False)[:600])
    print(f"wrote {dest}")
