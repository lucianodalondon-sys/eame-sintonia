"""Ajuda de leitura do agente: resume cada caso do lote (paginas, titulo, retrato, familias de links).
uso: py provas/ia_cur/bancada_continua/ler_lote.py <LOTE.json> [CASO ...]"""
import json, re, html, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "curadoria"))
import canario as C, reparar_contrato as RC, retrato_html as RH   # noqa: E402

lote = json.load(open(sys.argv[1], encoding="utf-8"))
so = set(sys.argv[2:])
for c in lote["CASOS"]:
    if so and c["CASO"] not in so:
        continue
    print("\n#### %s | %s" % (c["CASO"], c["GATILHO"][:150]))
    for p in c["PAGINAS"]:
        if not p.get("SHA256"):
            print("   [%s] %s %s" % (p.get("PAPEL"), p.get("ESTADO"), p["URL"][:90])); continue
        b = open(p["BYTES_EM"], "rb").read()
        t = b.decode("utf-8", "replace")
        ti = re.search(r"(?is)<title[^>]*>(.*?)</title>", t)
        r = RH.retrato_do_html(b) if b[:1] in (b"<", b" ", b"\n", b"\r", b"\t", b"\xef") else {}
        print("   [%s] HTTP %s %dB %s | %s | %s %s par=%s" % (
            p.get("PAPEL"), p.get("HTTP"), p.get("BYTES", 0), p["URL"][:80],
            re.sub(r"\s+", " ", html.unescape(ti.group(1))).strip()[:60] if ti else "-",
            r.get("HTML_KIND"), r.get("CAPA_OU_MATERIA"), r.get("PARAGRAPH_CHARACTERS")))
        if p.get("PAPEL") in ("ENTRADA", "EXTRA") and b[:5] != b"%PDF-":
            hs = C.hrefs_da_entrada(b, p["URL"])
            pdfs = sorted(h for h in hs if h.lower().split("?")[0].endswith(".pdf"))
            print("        hrefs=%d pdfs=%d %s" % (len(hs), len(pdfs), pdfs[:3]))
            for f in RC.familias(hs, p["URL"])[:4]:
                print("        fam %d %s" % (f["MEMBROS"], f["PADRAO"][:120]))
