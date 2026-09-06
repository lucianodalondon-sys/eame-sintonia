"""L4 AUDIT — independent PDF metadata + text extraction, no third-party libs.

Read-only. Prints /Info dict dates, XMP dates, and decompressed text streams.
"""
import re, sys, zlib, os

def raw_meta(path):
    b = open(path, 'rb').read()
    out = {'path': path, 'bytes': len(b), 'magic': b[:8].decode('latin-1')}
    # PDF version
    m = re.match(rb'%PDF-(\d\.\d)', b)
    out['pdf_version'] = m.group(1).decode() if m else 'NONE'
    # all date strings anywhere in the file (uncompressed Info dicts)
    out['D_dates'] = sorted(set(x.decode('latin-1') for x in re.findall(rb'D:\d{8,14}[^\s/>\)\]]*', b)))
    # Info dict keys
    info = {}
    for key in [b'Title', b'Author', b'Subject', b'Creator', b'Producer',
                b'CreationDate', b'ModDate', b'Keywords']:
        for m in re.finditer(rb'/' + key + rb'\s*(\(((?:[^()\\]|\\.)*)\)|<([0-9A-Fa-f\s]+)>)', b):
            if m.group(2) is not None:
                v = m.group(2)
            else:
                h = re.sub(rb'\s', b'', m.group(3))
                v = bytes.fromhex(h.decode())
            info.setdefault(key.decode(), []).append(v.decode('latin-1', 'replace')[:200])
    out['info'] = info
    # XMP
    xmp = {}
    for tag in ['xmp:CreateDate', 'xmp:ModifyDate', 'xmp:MetadataDate',
                'dc:title', 'pdf:Producer', 'xmp:CreatorTool']:
        for m in re.finditer(('<' + tag + r'[^>]*>(.*?)</' + tag + '>').encode(), b, re.S):
            xmp.setdefault(tag, []).append(
                re.sub(rb'<[^>]+>', b' ', m.group(1)).decode('utf-8', 'replace').strip()[:200])
    out['xmp'] = xmp
    return out, b


def streams_text(b):
    """Decompress every FlateDecode stream, return concatenated raw content."""
    chunks = []
    for m in re.finditer(rb'stream\r?\n', b):
        start = m.end()
        e = b.find(b'endstream', start)
        if e < 0:
            continue
        data = b[start:e]
        try:
            d = zlib.decompress(data)
        except Exception:
            try:
                d = zlib.decompressobj().decompress(data)
            except Exception:
                continue
        chunks.append(d)
    return chunks


def content_text(chunks):
    """Pull literal strings out of PDF content-stream text operators."""
    words = []
    for d in chunks:
        if b'Tj' not in d and b'TJ' not in d:
            continue
        for m in re.finditer(rb'\(((?:[^()\\]|\\.)*)\)', d):
            s = m.group(1)
            s = s.replace(b'\\(', b'(').replace(b'\\)', b')').replace(b'\\\\', b'\\')
            words.append(s.decode('latin-1', 'replace'))
    return words


if __name__ == '__main__':
    for p in sys.argv[1:]:
        meta, b = raw_meta(p)
        print('=' * 78)
        print('FILE       :', p)
        print('bytes      :', meta['bytes'], ' magic:', repr(meta['magic']),
              ' pdfver:', meta['pdf_version'])
        print('D: dates   :', meta['D_dates'])
        print('Info dict  :', meta['info'])
        print('XMP        :', meta['xmp'])
        ch = streams_text(b)
        print('streams decompressed:', len(ch))
        # dates hidden inside compressed object streams
        allc = b''.join(ch)
        cd = sorted(set(x.decode('latin-1') for x in re.findall(rb'D:\d{8,14}[^\s/>\)\]]*', allc)))
        print('D: dates in compressed streams:', cd)
        xd = sorted(set(x.decode('latin-1') for x in re.findall(
            rb'(?:CreateDate|ModifyDate|MetadataDate)>[^<]{4,40}<', allc)))
        print('XMP dates in compressed streams:', xd)
        words = content_text(ch)
        txt = ' '.join(words)
        txt = re.sub(r'\s+', ' ', txt)
        print('--- extracted text (%d chars) ---' % len(txt))
        print(txt[:6000])
        print()
