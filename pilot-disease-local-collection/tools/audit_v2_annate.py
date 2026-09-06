"""INDEPENDENT re-audit of C5 (26 Annate agrarie). Written from scratch.
Read-only. Does not touch raw/ or manifests/.
Checks:
  A. physical preservation: file exists, sha256 recomputed, %PDF magic, distinctness
  B. where the season label comes from (slug / document_title / published_at)
  C. the PDF's OWN internal Info dict (Title, CreationDate) -- my own parser
  D. the PDF's OWN TEXT LAYER via poppler pdftotext (the prior auditor could not read this)
"""
import json, re, os, sys, hashlib, zlib, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(ROOT, "manifests", "arpav-docs-manifest.verified.jsonl")

rows = [json.loads(l) for l in open(MAN, encoding="utf-8")]
annate = [r for r in rows if "/annate-agrarie/" in r["source_url"]]


def slug(r):
    return r["source_url"].split("/annate-agrarie/")[-1].split("/@@")[0]


annate.sort(key=lambda r: slug(r))

# ---------- A. physical preservation ----------
print("=" * 78)
print("A. PHYSICAL PRESERVATION (recomputed by me, not read from manifest)")
print("=" * 78)
shas, sizes, bad = set(), set(), []
for r in annate:
    p = os.path.join(ROOT, r["raw_path"].replace("/", os.sep))
    if not os.path.exists(p):
        bad.append((slug(r), "MISSING_FILE"))
        continue
    b = open(p, "rb").read()
    h = hashlib.sha256(b).hexdigest()
    if h != r["sha256"]:
        bad.append((slug(r), "SHA_MISMATCH"))
    if len(b) != r["bytes"]:
        bad.append((slug(r), "BYTES_MISMATCH"))
    if b[:5] != b"%PDF-":
        bad.append((slug(r), "NOT_PDF_MAGIC:" + repr(b[:16])))
    # does the on-disk filename encode anything but the hash?
    base = os.path.basename(p)
    if not h.startswith(base.split("_")[0]):
        bad.append((slug(r), "FILENAME_NOT_HASH_PREFIX:" + base))
    shas.add(h)
    sizes.add(len(b))
print(f"annate rows: {len(annate)}")
print(f"distinct slugs: {len({slug(r) for r in annate})}")
print(f"distinct sha256 (recomputed): {len(shas)}")
print(f"distinct byte sizes (recomputed): {len(sizes)}")
print(f"problems: {bad if bad else 'NONE'}")

# ---------- C. internal Info dict, my own parser ----------
TITLE_RE = re.compile(rb"/Title\s*\(((?:\\.|[^\\()])*)\)", re.S)
TITLE_HEX = re.compile(rb"/Title\s*<([0-9A-Fa-f\s]+)>")
CDATE_RE = re.compile(rb"/CreationDate\s*\(([^)]*)\)")
XMPT = re.compile(rb"<dc:title>.*?<rdf:li[^>]*>(.*?)</rdf:li>", re.S)


def depdf(s):
    s = re.sub(rb"\\([()\\])", rb"\1", s)
    if s[:2] in (b"\xfe\xff",):
        try:
            return s.decode("utf-16-be", "replace").lstrip("﻿")
        except Exception:
            pass
    return s.decode("latin-1", "replace")


def inflated_blob(b):
    out = [b]
    for m in re.finditer(rb"stream\r?\n", b):
        st = m.end()
        en = b.find(b"endstream", st)
        if en < 0:
            continue
        chunk = b[st:en]
        if len(chunk) > 4_000_000:
            continue
        try:
            out.append(zlib.decompress(chunk))
        except Exception:
            try:
                out.append(zlib.decompressobj().decompress(chunk))
            except Exception:
                pass
    return b"\n".join(out)


def meta(path):
    b = open(path, "rb").read()
    blob = b
    t = TITLE_RE.findall(blob) or TITLE_HEX.findall(blob)
    c = CDATE_RE.findall(blob)
    if not t or not c:
        blob = inflated_blob(b)
        t = t or TITLE_RE.findall(blob) or XMPT.findall(blob)
        c = c or CDATE_RE.findall(blob)
    tt = [depdf(x) for x in t]
    # hex-decode if it came from TITLE_HEX
    tt2 = []
    for x in tt:
        if re.fullmatch(r"[0-9A-Fa-f\s]+", x) and len(x) > 8:
            try:
                x = bytes.fromhex(re.sub(r"\s", "", x)).decode("utf-16-be", "replace")
            except Exception:
                pass
        tt2.append(x.strip())
    return sorted(set(tt2)), sorted({depdf(x).strip() for x in c})


# ---------- D. text layer via poppler ----------
YEAR = re.compile(r"(?<!\d)(19[89]\d|20[0-2]\d)(?!\d)")
PERIOD = re.compile(
    r"(GENNAIO|FEBBRAIO|MARZO|APRILE|MAGGIO|GIUGNO|LUGLIO|AGOSTO|SETTEMBRE|OTTOBRE|NOVEMBRE|DICEMBRE|ANNATA|ANNO)[^\n]{0,120}",
    re.I)


def text_head(path, pages=2):
    try:
        r = subprocess.run(["pdftotext", "-f", "1", "-l", str(pages), path, "-"],
                           capture_output=True, timeout=120)
        return r.stdout.decode("latin-1", "replace")
    except Exception as e:
        return "PDFTOTEXT_FAILED:" + type(e).__name__


print()
print("=" * 78)
print("C+D. THREE INDEPENDENT SOURCES OF THE SEASON LABEL")
print("=" * 78)
recs = []
for r in annate:
    p = os.path.join(ROOT, r["raw_path"].replace("/", os.sep))
    t, c = meta(p)
    txt = text_head(p)
    head = " ".join(txt.split())[:260]
    yrs = sorted(set(int(y) for y in YEAR.findall(txt[:4000])))
    recs.append(dict(slug=slug(r), doc_title=r["document_title"],
                     published=r["published_at"], title=t, cdate=c,
                     head=head, yrs=yrs, textlen=len(txt.strip()),
                     raw=os.path.basename(p)))

print(f"{'slug':<34}| {'internal /Title':<46}| CreationDate")
print("-" * 78)
for x in recs:
    print(f"{x['slug']:<34}| {(x['title'][0] if x['title'] else 'NO_TITLE_IN_PDF')[:45]:<46}| "
          f"{(x['cdate'][0] if x['cdate'] else 'NO_CDATE')[:26]}")

print()
print("=" * 78)
print("D. TEXT-LAYER EXTRACTION SUCCESS RATE (poppler pdftotext)")
print("=" * 78)
ok = [x for x in recs if x["textlen"] > 200 and not x["head"].startswith("PDFTOTEXT_FAILED")]
print(f"text extracted (>200 chars) on {len(ok)} / {len(recs)} annate PDFs")
print(f"empty/failed: {[x['slug'] for x in recs if x not in ok]}")

print()
print("=" * 78)
print("D2. WHAT THE DOCUMENT ITSELF SAYS (first ~260 chars of page 1-2 text)")
print("=" * 78)
for x in recs:
    print(f"\n### {x['slug']}   [file {x['raw']}]")
    print(f"    manifest document_title : {x['doc_title']}")
    print(f"    manifest published_at   : {x['published']}")
    print(f"    internal /Title         : {x['title']}")
    print(f"    years seen in first 4k  : {x['yrs']}")
    print(f"    TEXT: {x['head']}")

json.dump(recs, open(os.path.join(ROOT, "tools", "_v2_annate.json"), "w",
                     encoding="utf-8"), ensure_ascii=False, indent=1)
