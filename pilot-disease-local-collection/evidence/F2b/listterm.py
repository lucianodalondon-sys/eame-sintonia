import json, sys, time
from probe import adv, get, BASE


def fetch_all(field, rend, term, cap=400):
    out = {}
    page = 1
    total = None
    while True:
        st, n, d = adv({field: {"type": rend, "value": term}}, page=page, size=50)
        ents = d["page"]["entities"]
        if total is None:
            total = d["page"].get("entitiesCount")
        if not ents:
            break
        for e in ents:
            a = e.get("attributes", {})
            out[e["id"]] = {
                "id": e["id"],
                "name": e.get("name"),
                "title": a.get("sys_title"),
                "slug": e.get("slug"),
                "canonical": a.get("sys_canonical_url"),
                "type": e.get("type"),
                "sys_type": a.get("sys_type"),
                "ipa": a.get("sys_ipa"),
                "path": a.get("sys_full_path"),
                "firstPublishedAt": e.get("firstPublishedAt"),
                "createdAt": e.get("createdAt"),
                "modifiedAt": e.get("modifiedAt"),
                "start_pub": a.get("sys_start_pub_date"),
                "allegati": a.get("mul_association_allegati"),
                "file": e.get("file"),
                "matched_field": field,
            }
        page += 1
        if len(out) >= min(total, cap):
            break
        time.sleep(0.2)
    return out, total


if __name__ == "__main__":
    term = sys.argv[1]
    fields = [("sys_title", "TEXT"), ("sys_name", "TEXT"), ("sys_description", "HTMLAREA")]
    if len(sys.argv) > 2:
        fields = [f for f in fields if f[0] == sys.argv[2]]
    union = {}
    for f, r in fields:
        got, total = fetch_all(f, r, term)
        print("#", term, f, "total=", total, "fetched=", len(got), flush=True)
        for k, v in got.items():
            union.setdefault(k, v)
    print("UNION", term, len(union))
    json.dump(union, open("term_%s.json" % term, "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    for v in sorted(union.values(), key=lambda x: (x["firstPublishedAt"] or "")):
        print("  |", (v["firstPublishedAt"] or "")[:10], "|", v["type"], "|",
              (v["title"] or v["name"] or "")[:95], "|", v["canonical"])
