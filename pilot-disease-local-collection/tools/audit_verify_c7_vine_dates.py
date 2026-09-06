# Independent re-derivation of the vine-bulletin PDF metadata.
# Does not import any collector code and does not read the other auditor's script.
# Parses the PDF bytes directly: the /Info dictionary in plain object form, and
# every FlateDecode stream, looking for an XMP packet.
import json
import re
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "raw" / "F8-arpav-agrometeo-docs"

TARGETS = {
    "vitimeteo.pdf": "5d0669adb9c4_file",
    "vitimeteo2.pdf": "e0e176fb1a87_file",
}


def info_dict_fields(blob: bytes):
    """Pull /Key (value) pairs out of every uncompressed object that looks like
    a document information dictionary."""
    out = {}
    for key in (b"CreationDate", b"ModDate", b"Title", b"Author", b"Producer",
                b"Creator", b"Subject", b"Keywords"):
        for m in re.finditer(rb"/" + key + rb"\s*\((.*?)(?<!\\)\)", blob, re.S):
            out.setdefault(key.decode(), []).append(
                m.group(1).decode("latin-1", "replace"))
        for m in re.finditer(rb"/" + key + rb"\s*<([0-9A-Fa-f\s]+)>", blob):
            hexs = re.sub(rb"\s", b"", m.group(1))
            try:
                dec = bytes.fromhex(hexs.decode())
                if dec.startswith(b"\xfe\xff"):
                    dec = dec[2:].decode("utf-16-be", "replace")
                else:
                    dec = dec.decode("latin-1", "replace")
            except Exception:
                dec = "<unhexable>"
            out.setdefault(key.decode(), []).append(dec)
    return out


def xmp_packets(blob: bytes):
    """XMP can sit in a plain <?xpacket...?> region or inside a Flate stream."""
    found = []
    for m in re.finditer(rb"<\?xpacket begin.*?<\?xpacket end.*?\?>", blob, re.S):
        found.append(("plaintext", m.group(0)))
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", blob, re.S):
        raw = m.group(1)
        for candidate in (raw, raw.strip(b"\r\n")):
            try:
                dec = zlib.decompress(candidate)
            except Exception:
                continue
            if b"<x:xmpmeta" in dec or b"<?xpacket" in dec:
                found.append(("flate_stream", dec))
            break
    return found


def xmp_titles(packet: bytes):
    """Every dc:title / rdf:li under it, plus any other title-ish tag."""
    titles = []
    for m in re.finditer(rb"<dc:title>(.*?)</dc:title>", packet, re.S):
        block = m.group(1)
        lis = re.findall(rb"<rdf:li[^>]*>(.*?)</rdf:li>", block, re.S)
        if lis:
            titles += [x.decode("utf-8", "replace").strip() for x in lis]
        else:
            titles.append(re.sub(rb"<[^>]+>", b"", block)
                          .decode("utf-8", "replace").strip())
    for m in re.finditer(rb'(?:xmp|pdf|dc):[Tt]itle\s*=\s*"([^"]*)"', packet):
        titles.append(m.group(1).decode("utf-8", "replace").strip())
    return titles


def xmp_dates(packet: bytes):
    d = {}
    for tag in (b"CreateDate", b"ModifyDate", b"MetadataDate"):
        for m in re.finditer(rb"<xmp:" + tag + rb">(.*?)</xmp:" + tag + rb">",
                             packet, re.S):
            d.setdefault(tag.decode(), []).append(
                m.group(1).decode("utf-8", "replace").strip())
        for m in re.finditer(rb"xmp:" + tag + rb'\s*=\s*"([^"]*)"', packet):
            d.setdefault(tag.decode(), []).append(
                m.group(1).decode("utf-8", "replace").strip())
    return d


def manifest_rows(name):
    rows = []
    for mf in ("arpav-docs-manifest.jsonl", "arpav-docs-manifest.verified.jsonl",
               "arpav-docs-inventory.jsonl",
               "FAILED-arpav-docs-manifest-htmlshells.jsonl"):
        p = ROOT / "manifests" / mf
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if name in json.dumps(r):
                rows.append((mf, r))
    return rows


for pretty, fname in TARGETS.items():
    path = DOCS / fname
    blob = path.read_bytes()
    print("=" * 72)
    print(f"{pretty}  ->  {path}")
    print(f"  bytes on disk        : {len(blob)}")
    print(f"  first 8 bytes        : {blob[:8]!r}")
    print(f"  '/Type /Page' count  : {blob.count(b'/Type /Page') + blob.count(b'/Type/Page')}")
    print("  -- /Info dictionary (raw PDF trailer metadata) --")
    for k, v in info_dict_fields(blob).items():
        print(f"     {k:14s}: {v}")
    print("  -- XMP packets --")
    pk = xmp_packets(blob)
    if not pk:
        print("     NONE FOUND")
    for kind, packet in pk:
        print(f"     source={kind} len={len(packet)}")
        print(f"     dc/xmp titles : {xmp_titles(packet)}")
        print(f"     xmp dates     : {xmp_dates(packet)}")
    print("  -- what the manifests say about this same file --")
    for mf, r in manifest_rows(pretty):
        print(f"     [{mf}]")
        for k in ("document_title", "published_at", "modified_at", "bytes",
                  "sha256", "preservation", "media_type", "http_status",
                  "verification", "magic_ok", "verified_media_type"):
            if k in r:
                val = r[k]
                if k == "sha256":
                    val = str(val)[:16] + "..."
                print(f"        {k:20s}= {val}")
