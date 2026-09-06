#!/usr/bin/env python3
"""RT3-E5. collect_generic.py line 67-68:

    open(os.path.join(raw, fn), "w").write(blob)                  # locale encoding
    rec["sha256"] = hashlib.sha256(blob.encode()).hexdigest()     # UTF-8, always

open(...,"w") with no encoding= uses locale.getpreferredencoding(False). On this machine that
is cp1252, not UTF-8. If `blob` contains any non-ASCII character the BYTES ON DISK differ from
the BYTES THAT WERE HASHED, and load_rows() raises 'REFUSED: ... does not match its collected
sha256' on the very next read -- the whole case becomes unreadable after a refresh.

This script (1) measures the machine, (2) counts non-ASCII in the real archives,
(3) reproduces the write/hash disagreement end to end on a COPY, and (4) checks whether the
CURRENTLY SHIPPED archives still verify.
"""
import sys, os, json, glob, locale, hashlib, shutil, tempfile, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, "..", "..", "ENGINE"))
CAS = os.path.abspath(os.path.join(HERE, "..", "..", "CASES"))
sys.path.insert(0, ENG)
import current_pressure as cp

OUT = {"MACHINE": {"sys.getdefaultencoding": sys.getdefaultencoding(),
                   "locale.getpreferredencoding(False)": locale.getpreferredencoding(False),
                   "sys.platform": sys.platform,
                   "PYTHONUTF8": os.environ.get("PYTHONUTF8"),
                   "PYTHONIOENCODING": os.environ.get("PYTHONIOENCODING")}}

# ------------------------------------------------- 1. non-ASCII census of the real archives
census = {}
for cname in ("OLIVO-BACTROCERA-TOSCANA", "VITE-OIDIO-TOSCANA", "FRUMENTO-SEPTORIA-TOSCANA"):
    d = os.path.join(CAS, cname)
    files = sorted(glob.glob(os.path.join(d, "RAW", "*.json")))
    n_rows_tot = n_rows_nonascii = 0
    n_files_nonascii = 0
    chars = collections.Counter()
    for fn in files:
        raw = open(fn, "rb").read()
        txt = raw.decode("utf-8")
        rows = json.loads(txt)
        n_rows_tot += len(rows)
        f_has = False
        for r in rows:
            s = json.dumps(r, ensure_ascii=False)
            bad = [c for c in s if ord(c) > 127]
            if bad:
                n_rows_nonascii += 1
                f_has = True
                chars.update(bad)
        if f_has:
            n_files_nonascii += 1
    # the index itself
    idx_txt = open(os.path.join(d, "collection_index.json"), "rb").read().decode("utf-8")
    idx_bad = [c for c in idx_txt if ord(c) > 127]
    census[cname] = {
        "N_RAW_FILES": len(files),
        "N_FILES_CONTAINING_NON_ASCII": n_files_nonascii,
        "N_ROWS_TOTAL": n_rows_tot,
        "N_ROWS_CONTAINING_NON_ASCII": n_rows_nonascii,
        "PCT_ROWS_NON_ASCII": round(100.0 * n_rows_nonascii / n_rows_tot, 4) if n_rows_tot else None,
        "NON_ASCII_CHARS_SEEN": {c: n for c, n in chars.most_common()},
        "COLLECTION_INDEX_NON_ASCII_CHARS": len(idx_bad),
    }
OUT["NON_ASCII_CENSUS"] = census

# ------------------------------------------------- 2. do the shipped archives still verify?
verify = {}
for cname, var in (("OLIVO-BACTROCERA-TOSCANA", -1002), ("VITE-OIDIO-TOSCANA", 39),
                   ("FRUMENTO-SEPTORIA-TOSCANA", 372)):
    d = os.path.join(CAS, cname)
    idx = json.load(open(os.path.join(d, "collection_index.json")))
    by_file = {r["file"]: r.get("sha256") for r in idx["requests"] if r.get("file")}
    mism, ok, unindexed = [], 0, []
    for fn in sorted(glob.glob(os.path.join(d, "RAW", "*.json"))):
        b = os.path.basename(fn)
        h = hashlib.sha256(open(fn, "rb").read()).hexdigest()
        if b not in by_file or not by_file[b]:
            unindexed.append(b)
        elif by_file[b] != h:
            mism.append(b)
        else:
            ok += 1
    verify[cname] = {"N_FILES_ON_DISK": len(glob.glob(os.path.join(d, "RAW", "*.json"))),
                     "N_FILES_IN_INDEX_WITH_SHA": len(by_file),
                     "N_VERIFIED_OK": ok, "N_MISMATCH": len(mism), "MISMATCHED": mism,
                     "N_ON_DISK_BUT_NOT_IN_INDEX (hash check SKIPPED for these)": len(unindexed),
                     "UNINDEXED": unindexed}
OUT["SHIPPED_ARCHIVE_VERIFICATION"] = verify

# ------------------------------------------------- 3. reproduce the write/hash disagreement
tmp = os.path.join(HERE, "_enc_tmp")
shutil.rmtree(tmp, ignore_errors=True)
os.makedirs(tmp)
repro = {}
# take a REAL row set containing non-ASCII if one exists, else synthesise the source's own text
sample = None
for cname in census:
    if census[cname]["N_ROWS_CONTAINING_NON_ASCII"]:
        d = os.path.join(CAS, cname)
        for fn in sorted(glob.glob(os.path.join(d, "RAW", "*.json"))):
            rows = json.loads(open(fn, "rb").read().decode("utf-8"))
            hit = [r for r in rows if any(ord(c) > 127 for c in json.dumps(r, ensure_ascii=False))]
            if hit:
                sample = hit[:3]
                repro["SAMPLE_SOURCE"] = os.path.join(cname, "RAW", os.path.basename(fn))
                break
    if sample:
        break
if sample is None:
    sample = [{"nome_area": "Forlì-Cesena", "val": "1", "date": "2026-01-01"}]
    repro["SAMPLE_SOURCE"] = "SYNTHETIC (no non-ASCII row found in the shipped archives)"

blob = json.dumps(sample, ensure_ascii=False)
p = os.path.join(tmp, "probe.json")
# EXACTLY what collect_generic.py does
open(p, "w").write(blob)
recorded = hashlib.sha256(blob.encode()).hexdigest()
on_disk = hashlib.sha256(open(p, "rb").read()).hexdigest()
repro.update({
    "SAMPLE_HAS_NON_ASCII": any(ord(c) > 127 for c in blob),
    "NON_ASCII_IN_SAMPLE": sorted({c for c in blob if ord(c) > 127}),
    "BYTES_WRITTEN_TO_DISK": os.path.getsize(p),
    "BYTES_OF_blob.encode()": len(blob.encode()),
    "SHA256_RECORDED_IN_INDEX": recorded,
    "SHA256_OF_FILE_ON_DISK": on_disk,
    "HASHES_AGREE": recorded == on_disk,
})
# and what load_rows would then do
try:
    json.loads(open(p, "rb").read().decode("utf-8"))
    repro["FILE_STILL_PARSES_AS_UTF8"] = True
except Exception as e:
    repro["FILE_STILL_PARSES_AS_UTF8"] = f"NO -- {type(e).__name__}: {e}"
OUT["WRITE_VS_HASH_REPRO"] = repro

# ------------------------------------------------- 4. which characters actually break cp1252
brk = {}
for ch in ["ì", "à", "è", "ò", "ù", "’", "–", "č", "€"]:
    try:
        enc = ch.encode(locale.getpreferredencoding(False))
        brk[ch] = {"cp1252_ok": True, "cp1252_bytes": enc.hex(), "utf8_bytes": ch.encode().hex(),
                   "BYTES_DIFFER": enc != ch.encode()}
    except Exception as e:
        brk[ch] = {"cp1252_ok": False, "ERROR": f"{type(e).__name__}: {e}",
                   "utf8_bytes": ch.encode().hex(), "BYTES_DIFFER": True}
OUT["CHAR_BEHAVIOUR_UNDER_LOCALE_ENCODING"] = brk

shutil.rmtree(tmp, ignore_errors=True)
json.dump(OUT, open(os.path.join(HERE, "rt3_e5_encoding.json"), "w"), indent=1)
print(json.dumps(OUT, indent=1, ensure_ascii=False))
