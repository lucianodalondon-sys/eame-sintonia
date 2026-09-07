#!/usr/bin/env python3
"""
DISEASE INTELLIGENCE · OBSERVATIONAL · THE REFRESH CYCLE

  DISCOVER -> FETCH -> VALIDATE -> NORMALIZE -> HASH -> STORE -> (analysis reads it)

Three properties, enforced here rather than promised:

  NON-DESTRUCTIVE. A fetch writes to STAGING. Nothing reaches CANONICAL until it has passed
  validation. A failed or empty refresh cannot overwrite a good archive, because it never
  gets near it.

  IDEMPOTENT. The same source bytes produce the same snapshot and leave CANONICAL untouched.
  Re-running is free and safe.

  AUDITABLE, AND IT DISTINGUISHES ITS FAILURES. The previous collector rebuilt its index from
  scratch on every run, so a partial refresh silently dropped the hash chain of every file it
  did not re-request, and a network error wiped the code table and took the whole case down.
  Here the index is MERGED, every entry keeps its own clock, and the six outcomes are named:

    NO_UPDATE          the source returned the same bytes
    NEW_OBSERVATIONS   new readable rows arrived
    SOURCE_UNAVAILABLE the endpoint did not answer
    SOURCE_EMPTY       it answered with a full row skeleton and no readable value
    SCHEMA_CHANGED     the variables or the code table moved
    INVALID_DATA       it answered, but the payload fails validation

Clocks are kept apart and never collapsed into one `date`:
    OBSERVATION_TIME        the date on the row - the only one that means anything agronomic
    COLLECTION_TIME         when we fetched
    SOURCE_PUBLICATION_TIME UNKNOWN - this API does not expose one
    SOURCE_UPDATE_TIME      UNKNOWN - same
    PROCESSING_TIME         when this snapshot was written
"""
import os, sys, json, time, hashlib, urllib.parse, urllib.request, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://agroambiente.info.regione.toscana.it/agro18/api/dati/get_aedita_data"

NO_UPDATE, NEW_OBSERVATIONS = "NO_UPDATE", "NEW_OBSERVATIONS"
SOURCE_INCOMPLETE = "SOURCE_INCOMPLETE"
SOURCE_UNAVAILABLE, SOURCE_EMPTY = "SOURCE_UNAVAILABLE", "SOURCE_EMPTY"
SCHEMA_CHANGED, INVALID_DATA = "SCHEMA_CHANGED", "INVALID_DATA"


def fetch(crop, schema, var, year, timeout=90, _transport=None):
    """One request. Returns the raw body and a transport verdict, and never raises."""
    q = urllib.parse.urlencode({"tipo_elab": "elab_pivot", "year": year, "crop": crop,
                                "survey_schema": schema, "survey_var": var, "difesa": "all",
                                "week": "all", "cultivar": "all", "area": "all",
                                "accesso": "all", "user_access": "all"})
    url = f"{API}?{q}"
    t0 = time.time()
    try:
        body = _transport(url) if _transport else \
            urllib.request.urlopen(url, timeout=timeout).read()
        return {"ok": True, "body": body, "seconds": round(time.time() - t0, 2), "url": url}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {str(e)[:160]}",
                "seconds": round(time.time() - t0, 2), "url": url}


def validate(body):
    """What came back, and whether it is usable. Every rejection is named."""
    try:
        js = json.loads(body.decode("utf-8"))
    except Exception as e:
        return INVALID_DATA, {"reason": f"not JSON: {type(e).__name__}"}, None, None
    d = js.get("data") if isinstance(js, dict) else js
    rows = (d.get("data") or []) if isinstance(d, dict) else (d if isinstance(d, list) else [])
    ok = d.get("ok") if isinstance(d, dict) else True
    msg = (d.get("message") if isinstance(d, dict) else None) or (
        js.get("message") if isinstance(js, dict) else None)
    filt = js.get("filter") if isinstance(js, dict) else None
    if ok is False:
        return SOURCE_EMPTY, {"reason": f"the source said not ok: {msg!r}"}, rows, filt
    if not rows:
        return SOURCE_EMPTY, {"reason": "zero rows with a successful response"}, rows, filt
    readable = sum(1 for r in rows if isinstance(r, dict) and r.get("val") not in (None, ""))
    if readable == 0:
        return SOURCE_EMPTY, {"reason": "a full row skeleton with no readable value - the "
                                        "shape this source returns for a variable that is "
                                        "not in the requested schema",
                              "n_rows": len(rows)}, rows, filt
    dated = [r for r in rows if r.get("date")]
    if not dated:
        return INVALID_DATA, {"reason": "no row carries a date"}, rows, filt
    return "OK", {"n_rows": len(rows), "n_readable": readable,
                  "latest_observation": max(r["date"] for r in dated)}, rows, filt


def refresh_one(canonical_dir, staging_dir, crop, schema, var, year, _transport=None):
    """One variable, one season. Never touches canonical unless the payload is good."""
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    fn = f"c{crop}_s{schema}_v{var}_{year}.json"
    canon_path = os.path.join(canonical_dir, "RAW", fn)
    prev_hash = (hashlib.sha256(open(canon_path, "rb").read()).hexdigest()
                 if os.path.exists(canon_path) else None)

    rec = {"file": fn, "var": var, "year": year,
           "REFRESH_ATTEMPT_AT": now, "COLLECTION_TIME": now,
           "SOURCE_PUBLICATION_TIME": "UNKNOWN", "SOURCE_UPDATE_TIME": "UNKNOWN",
           "previous_sha256": prev_hash}

    r = fetch(crop, schema, var, year, _transport=_transport)
    if not r["ok"]:
        rec.update({"REFRESH_STATUS": SOURCE_UNAVAILABLE, "detail": r.get("error"),
                    "canonical_touched": False,
                    "note": "the canonical archive is untouched and remains the last good copy"})
        return rec

    status, detail, rows, filt = validate(r["body"])
    rec["detail"] = detail

    # A payload can be 200 OK, ok:true, well formed AND INCOMPLETE. An independent time lens
    # fed back 2,245 of 2,928 real rows - a truncated but perfectly valid response - and it was
    # promoted: Siena went from 0.6909% on 18,383 drupes to 0.0% on 13,200, band green to
    # "Nessuna Infestazione", and it stayed publishable. Nothing refused it, because validate()
    # only ever looked at the payload and never at what canonical already held.
    if status == "OK" and os.path.exists(canon_path):
        try:
            prev_rows = json.loads(open(canon_path, "rb").read().decode("utf-8"))
        except Exception:
            prev_rows = []
        prev_n = len(prev_rows)
        prev_dates = [x.get("date") for x in prev_rows if isinstance(x, dict) and x.get("date")]
        prev_max = max(prev_dates) if prev_dates else None
        new_max = detail.get("latest_observation")
        lost = prev_n - detail["n_rows"]
        if lost > 0 or (prev_max and new_max and new_max < prev_max):
            status = SOURCE_INCOMPLETE
            detail = {"reason": "the response holds fewer rows, or an older newest "
                                "observation, than the copy already on disk",
                      "rows_now": detail["n_rows"], "rows_in_canonical": prev_n,
                      "rows_lost": lost,
                      "newest_now": new_max, "newest_in_canonical": prev_max}
            rec["detail"] = detail
    if status != "OK":
        rec.update({"REFRESH_STATUS": status, "canonical_touched": False,
                    "note": "refused: a bad payload never reaches canonical"})
        return rec

    blob = json.dumps(rows, ensure_ascii=False).encode("utf-8")   # utf-8 in, utf-8 hashed
    new_hash = hashlib.sha256(blob).hexdigest()
    os.makedirs(os.path.join(staging_dir, "RAW"), exist_ok=True)
    open(os.path.join(staging_dir, "RAW", fn), "wb").write(blob)
    rec.update({"sha256": new_hash, "bytes": len(blob),
                "LAST_GOOD_OBSERVATION_AT": detail["latest_observation"],
                "staged_at": os.path.join(staging_dir, "RAW", fn)})

    if new_hash == prev_hash:
        rec.update({"REFRESH_STATUS": NO_UPDATE, "canonical_touched": False,
                    "note": "byte-identical to canonical; nothing to promote"})
    else:
        rec["REFRESH_STATUS"] = NEW_OBSERVATIONS
        rec["canonical_touched"] = False
        rec["note"] = ("staged and validated; promote() will move it into canonical and MERGE "
                       "the index entry, leaving every other entry's hash chain intact")
    return rec


def promote(canonical_dir, staging_dir, records):
    """Move validated files into canonical and MERGE the index. Never rebuilds it."""
    idx_path = os.path.join(canonical_dir, "collection_index.json")
    idx = json.load(open(idx_path, encoding="utf-8")) if os.path.exists(idx_path) else \
        {"api": API, "requests": []}
    by_file = {r.get("file"): r for r in idx.get("requests", []) if r.get("file")}
    promoted = []
    for rec in records:
        if rec["REFRESH_STATUS"] != NEW_OBSERVATIONS:
            continue
        src = rec["staged_at"]
        dst = os.path.join(canonical_dir, "RAW", rec["file"])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, "wb").write(open(src, "rb").read())
        by_file[rec["file"]] = {k: v for k, v in rec.items()
                                if k not in ("staged_at", "previous_sha256", "note")}
        promoted.append(rec["file"])
    idx["requests"] = [by_file[f] for f in sorted(by_file)]     # merged, not rebuilt
    json.dump(idx, open(idx_path, "w", encoding="utf-8"), indent=1)
    return {"promoted": promoted, "index_entries_after": len(idx["requests"])}
