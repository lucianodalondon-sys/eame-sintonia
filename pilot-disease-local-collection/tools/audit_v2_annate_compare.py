"""Three-way comparison of the season label for the 26 Annate agrarie.
  SRC1 = CMS URL slug            (catalogue claim)
  SRC2 = PDF Info /Title         (authoring artefact)
  SRC3 = the PDF's own TEXT      (the document speaking about itself)
Decides, per file, whether SRC1 is corroborated or contradicted.
"""
import json, re, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
recs = json.load(open(os.path.join(ROOT, "tools", "_v2_annate.json"), encoding="utf-8"))

# SRC3: the document's own declared coverage. Two header dialects exist:
#   new: "ANNATA <YYYY> (da dicembre <YYYY-1> a novembre <YYYY>)"
#   old: "RELATIVO AL PERIODO GENNAIO-NOVEMBRE <YYYY>"
DECL = [
    re.compile(r"ANNATA\s+(\d{4})", re.I),
    re.compile(r"PERIODO\s+GENNAIO[-\s]*NOVEMBRE\s+(\d{4})", re.I),
]


def slug_year(s):
    s = s.replace("annata20agraria2020", "annata-agraria-20")  # %20-encoded slug
    m = re.search(r"(\d{4})-(\d{2})", s)
    if m:                      # "2000-01" -> span 2000..2001, end year 2001
        return int(m.group(1)) + 1, f"{m.group(1)}-{m.group(2)} (span, end={int(m.group(1))+1})"
    m = re.search(r"(\d{4})", s)
    return (int(m.group(1)), m.group(1)) if m else (None, "NO_YEAR_IN_SLUG")


def title_year(t):
    if not t:
        return None, "NO_TITLE"
    t0 = t[0]
    if t0.startswith("\\376\\377"):                      # UTF-16BE octal escapes
        t0 = re.sub(r"\\000", "", t0).replace("\\376\\377", "")
    m = re.findall(r"(\d{4})-(\d{2})\b", t0)
    if m:
        return int(m[0][0]) + 1, t0
    m = re.findall(r"(19\d\d|20\d\d)", t0)
    return (int(m[-1]), t0) if m else (None, t0)


def text_year(head):
    for rx in DECL:
        m = rx.search(head)
        if m:
            return int(m.group(1)), m.group(0)
    return None, "NO_DECLARED_PERIOD"


print("=" * 116)
print(f"{'CMS slug':<30}|{'slug yr':>8} |{'Title yr':>9} |{'TEXT yr':>8} | verdict")
print("=" * 116)
rowsout, contra_title, contra_text, notitle = [], [], [], []
for x in recs:
    sy, sd = slug_year(x["slug"])
    ty, td = title_year(x["title"])
    xy, xd = text_year(x["head"])
    v = []
    if ty is None:
        v.append("TITLE_HAS_NO_YEAR"); notitle.append(x["slug"])
    elif ty != sy:
        v.append("TITLE_vs_SLUG_MISMATCH"); contra_title.append((x["slug"], sy, ty, td))
    if xy is None:
        v.append("TEXT_UNDECLARED")
    elif xy != sy:
        v.append("TEXT_vs_SLUG_MISMATCH"); contra_text.append((x["slug"], sy, xy))
    if not v:
        v = ["ALL_THREE_AGREE"]
    print(f"{x['slug']:<30}|{sy!s:>8} |{ty!s:>9} |{xy!s:>8} | {','.join(v)}")
    rowsout.append((x["slug"], sy, ty, xy, x["head"][:120], x["raw"]))

print()
print("Title-vs-slug mismatches:", len(contra_title))
for s, a, b, d in contra_title:
    print(f"   {s:<30} slug={a}  title={b}   [{d[:60]}]")
print("Titles with NO year at all:", len(notitle), notitle)
print()
print("TEXT-vs-slug mismatches (the document's own declared coverage):", len(contra_text))
for s, a, b in contra_text:
    print(f"   {s:<30} slug->{a}   document says {b}")

print()
print("=" * 116)
print("COVERAGE SET IMPLIED BY THE DOCUMENTS THEMSELVES (SRC3), not by the slugs")
print("=" * 116)
yrs = [r[3] for r in rowsout if r[3]]
print("files with a self-declared coverage year :", len(yrs), "/", len(rowsout))
print("distinct self-declared years             :", len(set(yrs)))
print("range                                    :", min(yrs), "..", max(yrs))
print("missing years inside the range           :",
      sorted(set(range(min(yrs), max(yrs) + 1)) - set(yrs)) or "none")
from collections import Counter
dup = {y: c for y, c in Counter(yrs).items() if c > 1}
print("years covered by MORE THAN ONE file      :", dup)
for y in dup:
    print(f"   annata {y} is claimed by:")
    for r in rowsout:
        if r[3] == y:
            print(f"      {r[0]:<30} [{r[5]}] :: {r[4][:100]}")
