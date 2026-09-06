"""Stdlib-only PDF text extractor using each font's /ToUnicode CMap.

Written because no PDF library is installed and none may be installed.
Handles classic PDFs (indirect objects, FlateDecode content streams, subset
fonts with ToUnicode CMaps). It does NOT handle object streams (PDF 1.5+
/ObjStm) or encrypted PDFs. A short or empty result is therefore NOT proof
that the document has no text.
"""

import re
import sys
import zlib

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

path = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "sample"
raw = open(path, "rb").read()

objs = {}
for m in re.finditer(rb"(?<![0-9])(\d+)\s+(\d+)\s+obj\b(.*?)\bendobj\b", raw, re.S):
    objs[int(m.group(1))] = m.group(3)


def stream_bytes(body):
    m = re.search(rb"stream\r?\n(.*?)\r?\nendstream", body, re.S)
    if not m:
        m = re.search(rb"stream\r?\n(.*?)endstream", body, re.S)
    if not m:
        return None
    data = m.group(1)
    if b"/FlateDecode" in body:
        try:
            return zlib.decompress(data)
        except Exception:
            try:
                return zlib.decompressobj().decompress(data)
            except Exception:
                return None
    return data


def parse_cmap(data):
    cmap = {}
    two_byte = False
    cs = re.search(rb"begincodespacerange(.*?)endcodespacerange", data, re.S)
    if cs and re.search(rb"<[0-9A-Fa-f]{4}>", cs.group(1)):
        two_byte = True
    for blk in re.findall(rb"beginbfchar(.*?)endbfchar", data, re.S):
        for src, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
            code = int(src, 16)
            try:
                u = bytes.fromhex(dst.decode()).decode("utf-16-be", "replace")
            except Exception:
                continue
            cmap[code] = u
            if len(src) > 2:
                two_byte = True
    for blk in re.findall(rb"beginbfrange(.*?)endbfrange", data, re.S):
        for lo, hi, dst in re.findall(
            rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk
        ):
            a, b = int(lo, 16), int(hi, 16)
            if len(lo) > 2:
                two_byte = True
            try:
                base = int(dst, 16)
            except Exception:
                continue
            width = len(dst) // 4
            for i in range(a, min(b, a + 65535) + 1):
                v = base + (i - a)
                try:
                    if width <= 1:
                        cmap[i] = chr(v)
                    else:
                        cmap[i] = v.to_bytes(width * 2, "big").decode(
                            "utf-16-be", "replace"
                        )
                except Exception:
                    pass
    return cmap, two_byte


AGL = {
    "space": " ",
    "exclam": "!",
    "quotedbl": '"',
    "numbersign": "#",
    "dollar": "$",
    "percent": "%",
    "ampersand": "&",
    "quotesingle": "'",
    "quoteright": "’",
    "quoteleft": "‘",
    "quotedblleft": "“",
    "quotedblright": "”",
    "parenleft": "(",
    "parenright": ")",
    "asterisk": "*",
    "plus": "+",
    "comma": ",",
    "hyphen": "-",
    "period": ".",
    "slash": "/",
    "colon": ":",
    "semicolon": ";",
    "less": "<",
    "equal": "=",
    "greater": ">",
    "question": "?",
    "at": "@",
    "bracketleft": "[",
    "backslash": "\\",
    "bracketright": "]",
    "asciicircum": "^",
    "underscore": "_",
    "grave": "`",
    "braceleft": "{",
    "bar": "|",
    "braceright": "}",
    "asciitilde": "~",
    "endash": "-",
    "emdash": "-",
    "bullet": "*",
    "degree": "°",
    "percentage": "%",
    "germandbls": "ß",
    "ccedilla": "ç",
    "Ccedilla": "Ç",
    "ordmasculine": "º",
    "ordfeminine": "ª",
    "fi": "fi",
    "fl": "fl",
    "Euro": "€",
}
for _i, _n in enumerate(
    "zero one two three four five six seven eight nine".split()
):
    AGL[_n] = str(_i)
for _c in "abcdefghijklmnopqrstuvwxyz":
    AGL[_c] = _c
    AGL[_c.upper()] = _c.upper()
for _base, _accents in [
    ("a", {"acute": "á", "grave": "à", "circumflex": "â",
           "dieresis": "ä", "tilde": "ã", "ring": "å"}),
    ("e", {"acute": "é", "grave": "è", "circumflex": "ê",
           "dieresis": "ë"}),
    ("i", {"acute": "í", "grave": "ì", "circumflex": "î",
           "dieresis": "ï"}),
    ("o", {"acute": "ó", "grave": "ò", "circumflex": "ô",
           "dieresis": "ö", "tilde": "õ"}),
    ("u", {"acute": "ú", "grave": "ù", "circumflex": "û",
           "dieresis": "ü"}),
    ("n", {"tilde": "ñ"}),
]:
    for _suf, _ch in _accents.items():
        AGL[_base + _suf] = _ch
        AGL[_base.upper() + _suf] = _ch.upper()


def glyph_to_char(name):
    if name in AGL:
        return AGL[name]
    m = re.fullmatch(r"uni([0-9A-Fa-f]{4})", name)
    if m:
        return chr(int(m.group(1), 16))
    m = re.fullmatch(r"u([0-9A-Fa-f]{4,6})", name)
    if m:
        return chr(int(m.group(1), 16))
    m = re.fullmatch(r"[A-Za-z]\d{1,3}", name)  # g12, c45 - unknowable
    if m:
        return ""
    return ""


def parse_differences(body):
    """/Encoding << /Differences [ 32 /space 33 /exclam ... ] >> -> {code: char}"""
    m = re.search(rb"/Differences\s*\[(.*?)\]", body, re.S)
    if not m:
        return None
    out = {}
    code = 0
    for tok in re.finditer(rb"(\d+)|/([A-Za-z0-9._]+)", m.group(1)):
        if tok.group(1):
            code = int(tok.group(1))
        else:
            ch = glyph_to_char(tok.group(2).decode("latin-1"))
            if ch:
                out[code] = ch
            code += 1
    return out or None


font_cache = {}


def font_cmap(objnum):
    if objnum in font_cache:
        return font_cache[objnum]
    body = objs.get(objnum, b"")
    res = (None, False)
    m = re.search(rb"/ToUnicode\s+(\d+)\s+\d+\s+R", body)
    if m:
        data = stream_bytes(objs.get(int(m.group(1)), b""))
        if data:
            res = parse_cmap(data)
    if res[0] is None:
        em = re.search(rb"/Encoding\s*(\d+)\s+\d+\s+R", body)
        encbody = objs.get(int(em.group(1)), b"") if em else body
        diff = parse_differences(encbody)
        if diff:
            res = (diff, False)
    font_cache[objnum] = res
    return res


def resolve(body):
    """Follow one level of indirection for a dict body."""
    m = re.fullmatch(rb"\s*(\d+)\s+\d+\s+R\s*", body)
    if m:
        return objs.get(int(m.group(1)), b"")
    return body


def decode_string(lit, cmap, two_byte, fallback=False):
    if cmap is None:
        return lit.decode("latin-1")
    out = []
    if two_byte:
        for i in range(0, len(lit) - 1, 2):
            code = (lit[i] << 8) | lit[i + 1]
            out.append(cmap.get(code, ""))
    else:
        for b in lit:
            if b in cmap:
                out.append(cmap[b])
            elif fallback and b >= 32:
                out.append(chr(b))
    return "".join(out)


def unescape(lit):
    out = bytearray()
    i = 0
    while i < len(lit):
        c = lit[i]
        if c == 0x5C and i + 1 < len(lit):
            n = lit[i + 1]
            simple = {
                0x6E: 10,
                0x72: 13,
                0x74: 9,
                0x62: 8,
                0x66: 12,
                0x28: 40,
                0x29: 41,
                0x5C: 92,
            }
            if n in simple:
                out.append(simple[n])
                i += 2
                continue
            if 0x30 <= n <= 0x37:
                j = i + 1
                oct_digits = b""
                while j < len(lit) and len(oct_digits) < 3 and 0x30 <= lit[j] <= 0x37:
                    oct_digits += bytes([lit[j]])
                    j += 1
                out.append(int(oct_digits, 8) & 0xFF)
                i = j
                continue
            i += 2
            continue
        out.append(c)
        i += 1
    return bytes(out)


pages = 0
all_text = []
for num, body in objs.items():
    if not re.search(rb"/Type\s*/Page\b", body):
        continue
    pages += 1
    fonts = {}
    rm = re.search(rb"/Resources\s*(\d+\s+\d+\s+R|<<)", body)
    resbody = b""
    if rm:
        if rm.group(1) == b"<<":
            start = rm.end() - 2
            depth = 0
            i = start
            while i < len(body) - 1:
                if body[i : i + 2] == b"<<":
                    depth += 1
                    i += 2
                    continue
                if body[i : i + 2] == b">>":
                    depth -= 1
                    i += 2
                    if depth == 0:
                        break
                    continue
                i += 1
            resbody = body[start:i]
        else:
            resbody = resolve(rm.group(1))
    fm = re.search(rb"/Font\s*(\d+\s+\d+\s+R|<<)", resbody)
    fontbody = b""
    if fm:
        if fm.group(1) == b"<<":
            start = fm.end() - 2
            depth = 0
            i = start
            while i < len(resbody) - 1:
                if resbody[i : i + 2] == b"<<":
                    depth += 1
                    i += 2
                    continue
                if resbody[i : i + 2] == b">>":
                    depth -= 1
                    i += 2
                    if depth == 0:
                        break
                    continue
                i += 1
            fontbody = resbody[start:i]
        else:
            fontbody = resolve(fm.group(1))
    for name, onum in re.findall(rb"/([A-Za-z0-9#._+-]+)\s+(\d+)\s+\d+\s+R", fontbody):
        fonts[name] = int(onum)

    contents = []
    cm = re.search(rb"/Contents\s*(\d+)\s+\d+\s+R", body)
    if cm:
        contents = [int(cm.group(1))]
    else:
        cm = re.search(rb"/Contents\s*\[(.*?)\]", body, re.S)
        if cm:
            contents = [int(x) for x in re.findall(rb"(\d+)\s+\d+\s+R", cm.group(1))]
    data = b""
    for cnum in contents:
        d = stream_bytes(objs.get(cnum, b""))
        if d:
            data += d + b"\n"
    if not data:
        continue
    # Inline images (BI ... ID <binary> EI) hold binary that looks like text
    # operators. Strip them before tokenizing.
    data = re.sub(rb"\bBI\b.*?\bID\b.*?\bEI\b", b" ", data, flags=re.S)

    cur = (None, False)
    buf = []
    for tok in re.finditer(
        rb"/([A-Za-z0-9#._+-]+)\s+[\d.]+\s+Tf|\((?:\\.|[^()\\])*\)|<([0-9A-Fa-f\s]+)>\s*Tj|TJ|Tj|T\*|ET",
        data,
        re.S,
    ):
        s = tok.group(0)
        if s.endswith(b"Tf"):
            name = tok.group(1)
            if name in fonts:
                cur = font_cmap(fonts[name])
            else:
                cur = (None, False)
        elif s.startswith(b"("):
            buf.append(decode_string(unescape(s[1:-1]), cur[0], cur[1]))
        elif s.startswith(b"<") and tok.group(2):
            hx = re.sub(rb"\s", b"", tok.group(2))
            try:
                buf.append(decode_string(bytes.fromhex(hx.decode()), cur[0], cur[1]))
            except Exception:
                pass
        elif s in (b"T*", b"ET"):
            buf.append("\n")
    all_text.append("".join(buf))

txt = "\n".join(all_text)
print("OBJECTS", len(objs), "PAGES", pages, "CHARS", len(txt))
print("HAS_OBJSTM", b"/ObjStm" in raw, "ENCRYPTED", b"/Encrypt" in raw)

if mode == "sample":
    print("---- SAMPLE ----")
    print(txt[:4000])
elif mode == "dump":
    print(txt)
elif mode == "grep":
    pat = sys.argv[3]
    flat = re.sub(r"[ \t]+", " ", txt)
    n = 0
    for m in re.finditer(r".{0,150}" + pat + r".{0,150}", flat, re.I | re.S):
        print("  *", re.sub(r"\s+", " ", m.group(0)))
        n += 1
        if n > 60:
            break
    print("HITS", n)
