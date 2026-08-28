#!/usr/bin/env python3
"""
Extrator de texto de PDF — biblioteca padrão, sem dependências.

Existe porque a evidência primária espanhola chega em PDF e porque uma leitura de
PDF que não é reproduzível não é evidência. O extrator resolve o caso que nos
interessa: fontes com subconjunto (subset) e mapa /ToUnicode, que é o formato do
`dc_web.pdf` do MAPA e da ficha oficial de produto.

Uso:
    python3 scripts/pdf_text.py arquivo.pdf            # texto, uma linha por Tj/TJ
    python3 scripts/pdf_text.py arquivo.pdf --pages    # separa por página

O que ele NÃO faz: layout, colunas, tabelas. Quem precisa de coluna tem de
declarar a regra de corte — ver `scripts/denominaciones.py`.
"""
import re
import sys
import zlib


def _objects(data):
    """Todos os objetos indiretos do arquivo: {num: (dicionário bruto, stream)}."""
    objs = {}
    for m in re.finditer(rb'(\d+)\s+(\d+)\s+obj\b', data):
        num = int(m.group(1))
        start = m.end()
        end = data.find(b'endobj', start)
        if end < 0:
            continue
        body = data[start:end]
        stream = None
        sm = re.search(rb'stream\r?\n', body)
        if sm:
            se = body.find(b'endstream', sm.end())
            stream = body[sm.end():se]
        objs[num] = (body[:sm.start()] if sm else body, stream)
    return objs


def _inflate(header, stream):
    if stream is None:
        return None
    if b'/FlateDecode' in header:
        try:
            return zlib.decompress(stream)
        except zlib.error:
            try:
                return zlib.decompressobj().decompress(stream)
            except zlib.error:
                return None
    return stream


def _cmap(text):
    """Lê um /ToUnicode CMap e devolve {código: string}."""
    table = {}
    for blk in re.findall(rb'beginbfchar(.*?)endbfchar', text, re.S):
        for src, dst in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            table[int(src, 16)] = _utf16(dst)
    for blk in re.findall(rb'beginbfrange(.*?)endbfrange', text, re.S):
        for lo, hi, dst in re.findall(
                rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            a, b, base = int(lo, 16), int(hi, 16), int(dst, 16)
            for i in range(a, b + 1):
                table[i] = chr(base + i - a)
    return table


def _utf16(hexstr):
    raw = bytes.fromhex(hexstr.decode('ascii'))
    if len(raw) % 2:
        raw += b'\x00'
    try:
        return raw.decode('utf-16-be')
    except UnicodeDecodeError:
        return ''


def _fonts(objs):
    """{nome do recurso de fonte: cmap} — o nome é o /Fn usado no operador Tf."""
    tounicode = {}
    for num, (head, stream) in objs.items():
        if b'/ToUnicode' not in head and b'beginbfchar' not in (stream or b''):
            continue
    # mapeia objeto de fonte -> cmap
    font_cmap = {}
    for num, (head, _) in objs.items():
        if b'/Type' not in head or b'/Font' not in head:
            continue
        m = re.search(rb'/ToUnicode\s+(\d+)\s+\d+\s+R', head)
        if not m:
            continue
        tgt = int(m.group(1))
        if tgt not in objs:
            continue
        body = _inflate(*objs[tgt])
        if body:
            font_cmap[num] = _cmap(body)
    # resolve /Font << /F1 12 0 R >> em cada /Resources
    named = {}
    for num, (head, _) in objs.items():
        for fm in re.finditer(rb'/Font\s*<<(.*?)>>', head, re.S):
            for name, ref in re.findall(rb'/([A-Za-z0-9]+)\s+(\d+)\s+\d+\s+R', fm.group(1)):
                ref = int(ref)
                if ref in font_cmap:
                    named.setdefault(name.decode('latin-1'), font_cmap[ref])
    return named, font_cmap


_LIT = re.compile(rb'\\(\d{1,3}|.)', re.S)
_ESC = {b'n': b'\n', b'r': b'\r', b't': b'\t', b'b': b'\b', b'f': b'\f'}


def _unescape(raw):
    def sub(m):
        g = m.group(1)
        if g.isdigit():
            return bytes([int(g, 8) & 0xFF])
        return _ESC.get(g, g)
    return _LIT.sub(sub, raw)


def _decode(raw, cmap):
    if cmap is None:
        return raw.decode('latin-1')
    # fonte com subconjunto: códigos de 1 byte na maioria destes PDFs
    if all(k < 256 for k in cmap):
        return ''.join(cmap.get(b, '') for b in raw)
    out = []
    for i in range(0, len(raw) - 1, 2):
        out.append(cmap.get((raw[i] << 8) | raw[i + 1], ''))
    return ''.join(out)


_TOKEN = re.compile(
    rb'/([A-Za-z0-9]+)\s+[\d.]+\s+Tf'                    # 1 fonte
    rb'|\(((?:\\.|[^\\()])*)\)\s*Tj'                      # 2 literal Tj
    rb'|<([0-9A-Fa-f\s]+)>\s*Tj'                          # 3 hex Tj
    rb'|\[((?:[^\[\]\\]|\\.)*)\]\s*TJ',                   # 4 array TJ
    re.S)

_TJ_PART = re.compile(rb'\(((?:\\.|[^\\()])*)\)|<([0-9A-Fa-f\s]+)>', re.S)


def page_texts(data):
    objs = _objects(data)
    named, _ = _fonts(objs)
    pages = []
    for num in sorted(objs):
        head, stream = objs[num]
        body = _inflate(head, stream)
        if not body or (b'Tj' not in body and b'TJ' not in body):
            continue
        cur = None
        out = []
        for m in _TOKEN.finditer(body):
            if m.group(1):
                cur = named.get(m.group(1).decode('latin-1'))
            elif m.group(2) is not None:
                out.append(_decode(_unescape(m.group(2)), cur))
            elif m.group(3):
                out.append(_decode(bytes.fromhex(re.sub(rb'\s', b'', m.group(3)).decode()), cur))
            elif m.group(4) is not None:
                for p in _TJ_PART.finditer(m.group(4)):
                    if p.group(1) is not None:
                        out.append(_decode(_unescape(p.group(1)), cur))
                    else:
                        out.append(_decode(bytes.fromhex(re.sub(rb'\s', b'', p.group(2)).decode()), cur))
        if any(out):
            pages.append(out)
    return pages


def text(path):
    with open(path, 'rb') as f:
        return page_texts(f.read())


if __name__ == '__main__':
    pgs = text(sys.argv[1])
    for i, pg in enumerate(pgs, 1):
        if '--pages' in sys.argv:
            print(f'--- página {i} ---')
        print(''.join(pg))
