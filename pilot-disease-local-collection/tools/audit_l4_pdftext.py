"""L4 AUDIT — decode PDF text using each font's ToUnicode CMap. No third-party libs.

Read-only. Handles the subset-font / custom-encoding case where naive string
extraction returns control characters.
"""
import re, sys, zlib


def objects(b):
    """Return {objnum: (dict_bytes, stream_bytes_or_None)} for classic PDFs."""
    out = {}
    for m in re.finditer(rb'(\d+)\s+(\d+)\s+obj\b', b):
        num = int(m.group(1))
        start = m.end()
        end = b.find(b'endobj', start)
        if end < 0:
            continue
        body = b[start:end]
        sm = re.search(rb'stream\r?\n', body)
        stream = None
        if sm:
            se = body.find(b'endstream', sm.end())
            raw = body[sm.end():se if se > 0 else len(body)]
            try:
                stream = zlib.decompress(raw)
            except Exception:
                try:
                    stream = zlib.decompressobj().decompress(raw)
                except Exception:
                    stream = None
            body = body[:sm.start()]
        out[num] = (body, stream)
    return out


def parse_cmap(data):
    """ToUnicode CMap -> {src_code_int: unicode_str}."""
    m = {}
    for blk in re.findall(rb'beginbfchar(.*?)endbfchar', data, re.S):
        for a, b_ in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            src = int(a, 16)
            h = b_.decode()
            s = ''.join(chr(int(h[i:i + 4], 16)) for i in range(0, len(h) - 3, 4))
            m[src] = s
    for blk in re.findall(rb'beginbfrange(.*?)endbfrange', data, re.S):
        for lo, hi, dst in re.findall(
                rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            l, h = int(lo, 16), int(hi, 16)
            d = int(dst, 16)
            for i in range(l, h + 1):
                m[i] = chr(d + (i - l))
    return m


def extract(path):
    b = open(path, 'rb').read()
    objs = objects(b)
    # font resource name -> ToUnicode map
    fontmaps = {}
    for num, (body, _st) in objs.items():
        if b'/Type' in body and b'/Font' in body:
            tu = re.search(rb'/ToUnicode\s+(\d+)\s+\d+\s+R', body)
            bf = re.search(rb'/BaseFont\s*/([^\s/\]>]+)', body)
            if tu and int(tu.group(1)) in objs:
                cm = objs[int(tu.group(1))][1]
                if cm:
                    fontmaps[num] = (bf.group(1).decode() if bf else '?', parse_cmap(cm))
    # resource name (/F1 etc) -> font obj, per page resources
    name2obj = {}
    for num, (body, _st) in objs.items():
        for nm, on in re.findall(rb'/(F\w+|C2_\d+|TT\d+|R\d+)\s+(\d+)\s+\d+\s+R', body):
            if int(on) in fontmaps:
                name2obj[nm.decode()] = int(on)

    pieces = []
    for num, (_body, st) in objs.items():
        if not st or (b'Tj' not in st and b'TJ' not in st):
            continue
        cur = None
        # walk tokens in order
        for m in re.finditer(
                rb'/([A-Za-z0-9_]+)\s+[\d.]+\s+Tf|<([0-9A-Fa-f\s]*)>\s*Tj|'
                rb'\(((?:[^()\\]|\\.)*)\)\s*Tj|\[(.*?)\]\s*TJ|(T\*|Td|TD|ET)', st, re.S):
            if m.group(1):
                cur = name2obj.get(m.group(1).decode())
                continue
            cmap = fontmaps.get(cur, ('', {}))[1] if cur is not None else {}

            def dec_hex(h):
                h = re.sub(rb'\s', b'', h).decode()
                if len(h) % 2:
                    h += '0'
                # 2-byte codes if cmap keys are >255, else 1-byte
                two = any(k > 255 for k in cmap) or len(h) % 4 == 0
                step = 4 if two else 2
                o = ''
                for i in range(0, len(h), step):
                    c = int(h[i:i + step], 16)
                    o += cmap.get(c, chr(c) if 32 <= c < 127 else '�')
                return o

            def dec_lit(s):
                s = s.replace(b'\\(', b'(').replace(b'\\)', b')').replace(b'\\\\', b'\\')
                return ''.join(cmap.get(c, chr(c) if 32 <= c < 127 else '�') for c in s)

            if m.group(2) is not None:
                pieces.append(dec_hex(m.group(2)))
            elif m.group(3) is not None:
                pieces.append(dec_lit(m.group(3)))
            elif m.group(4) is not None:
                arr = m.group(4)
                for mm in re.finditer(rb'<([0-9A-Fa-f\s]*)>|\(((?:[^()\\]|\\.)*)\)|(-?[\d.]+)', arr):
                    if mm.group(1) is not None:
                        pieces.append(dec_hex(mm.group(1)))
                    elif mm.group(2) is not None:
                        pieces.append(dec_lit(mm.group(2)))
                    elif mm.group(3) and float(mm.group(3)) < -180:
                        pieces.append(' ')
            else:
                pieces.append('\n')
    return ''.join(pieces), fontmaps


if __name__ == '__main__':
    for p in sys.argv[1:]:
        txt, fm = extract(p)
        print('=' * 78)
        print('FILE:', p)
        print('fonts with ToUnicode:', [(v[0], len(v[1])) for v in fm.values()])
        txt = re.sub(r'\n{3,}', '\n\n', txt)
        print('--- TEXT (%d chars) ---' % len(txt))
        print(txt)
