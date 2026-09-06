"""Stdlib-only PDF text sniffer.

No third-party library is installed and none may be installed, so this only
inflates FlateDecode content streams and pulls the literal strings out of the
text-showing operators. It CANNOT decode subset fonts with custom encodings,
so a blank result is NOT proof the PDF has no text. Treat output as a sample,
never as a complete extraction.
"""

import re
import sys
import zlib

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

path = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "sample"
raw = open(path, "rb").read()
print("FILE", path)
print("BYTES", len(raw))
print("HEADER", raw[:8])

streams = re.findall(rb"stream\r?\n(.*?)endstream", raw, re.S)
print("STREAMS_FOUND", len(streams))

ok = 0
fail = 0
chunks = []
for s in streams:
    try:
        d = zlib.decompress(s)
        ok += 1
        chunks.append(d)
    except Exception:
        fail += 1
print("STREAMS_INFLATED", ok, "STREAMS_NOT_INFLATED", fail)

text_parts = []
GOOD = set(range(32, 127)) | {9, 10, 13} | set(range(160, 256))
for d in chunks:
    if b"BT" not in d or (b"Tj" not in d and b"TJ" not in d):
        continue
    for m in re.finditer(rb"\((?:\\.|[^()\\])*\)", d):
        lit = m.group(0)[1:-1]
        lit = re.sub(rb"\\([()\\])", rb"\1", lit)
        if not lit:
            continue
        bad = sum(1 for b in lit if b not in GOOD)
        if bad / len(lit) > 0.15:
            continue
        try:
            text_parts.append(lit.decode("latin-1"))
        except Exception:
            pass

txt = " ".join(text_parts)
txt = re.sub(r"\s+", " ", txt)
print("EXTRACTED_CHARS", len(txt))

if mode == "sample":
    print("---- SAMPLE (first 3000 chars) ----")
    print(txt[:3000])
elif mode == "nums":
    print("---- NUMERIC-LOOKING SNIPPETS ----")
    hits = 0
    for m in re.finditer(
        r"[^ ]{0,60}\b\d{1,3}(?:[.,]\d+)?\s?"
        r"(?:%|ha|n\.|focolai|piante|campioni|siti|aziende|trappole|vigneti|parcelle)"
        r"[^ ]{0,60}",
        txt,
        re.I,
    ):
        print("  *", m.group(0)[:160])
        hits += 1
        if hits > 80:
            break
    print("NUMERIC_SNIPPETS", hits)
elif mode == "grep":
    pat = sys.argv[3]
    for m in re.finditer(r".{0,120}" + pat + r".{0,120}", txt, re.I):
        print("  *", m.group(0))
elif mode == "find":
    # PDFs kern glyph-by-glyph, so search a space-stripped copy and map back.
    pat = sys.argv[3]
    idx = []
    flat = []
    for i, ch in enumerate(txt):
        if not ch.isspace():
            flat.append(ch)
            idx.append(i)
    flat = "".join(flat)
    print("FLAT_CHARS", len(flat))
    hits = 0
    for m in re.finditer(pat, flat, re.I):
        a = idx[max(0, m.start() - 90)]
        b = idx[min(len(idx) - 1, m.end() + 90)]
        print("  *", txt[a:b])
        hits += 1
        if hits > 60:
            break
    print("FIND_HITS", hits)
