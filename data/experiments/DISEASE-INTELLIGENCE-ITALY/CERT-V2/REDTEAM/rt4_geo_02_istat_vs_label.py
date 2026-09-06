#!/usr/bin/env python3
"""RT4 / GEOGRAPHY probe 2 — the province string vs the province implied by the ISTAT code.

Every disagreement is classified as either
  ADMIN_REFORM_PRATO  (comune belongs to the 1992 province of Prato but the source still serves
                       the legacy 48xxx Firenze-era ISTAT code) — a source-side legacy code, the
                       LABEL is the modern truth, or
  MISLABEL            (no reform explains it)

ISTAT province codes for Toscana (codice provincia, official):
  045 Massa-Carrara  046 Lucca  047 Pistoia  048 Firenze  049 Livorno
  050 Pisa           051 Arezzo 052 Siena    053 Grosseto 100 Prato
Prato (100) was constituted 1992-04-16 (L. 187/1992, operative 1995) from seven Firenze comuni:
  Prato, Cantagallo, Carmignano, Montemurlo, Poggio a Caiano, Vaiano, Vernio.
"""
import json, glob, os, collections

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "CASES")
HERE = os.path.dirname(os.path.abspath(__file__))
CASES = {"OLIVO-BACTROCERA-TOSCANA": "c2_s1_v-1002_*.json",
         "VITE-OIDIO-TOSCANA": "c3_s8_v39_*.json",
         "FRUMENTO-SEPTORIA-TOSCANA": "c19_s74_v372_*.json"}

ISTAT_PROV = {"45": "Massa-Carrara", "46": "Lucca", "47": "Pistoia", "48": "Firenze",
              "49": "Livorno", "50": "Pisa", "51": "Arezzo", "52": "Siena",
              "53": "Grosseto", "100": "Prato"}
PRATO_COMUNI = {"PRATO", "CANTAGALLO", "CARMIGNANO", "MONTEMURLO",
                "POGGIO A CAIANO", "VAIANO", "VERNIO"}


def prov_from_code(ac):
    s = str(ac)
    if s.startswith("100") and len(s) == 6:
        return "100"
    return s[:2] if len(s) == 5 else ("0" + s)[:2]


def load_all():
    rows = []
    for case, pat in CASES.items():
        for fn in sorted(glob.glob(os.path.join(ROOT, case, "RAW", pat))):
            for r in json.load(open(fn)):
                r["_case"], r["_file"] = case, os.path.basename(fn)
                rows.append(r)
    return rows


def main():
    rows = load_all()
    N = len(rows)
    res = {"N_ROWS_ALL_CASES": N, "PER_CASE": {}, "DISAGREEMENTS": {}}

    agree = disagree = 0
    dis_detail = collections.Counter()
    dis_rows = collections.defaultdict(list)
    per_case = collections.defaultdict(lambda: collections.Counter())

    for r in rows:
        code_prov = ISTAT_PROV.get(prov_from_code(r.get("admin_code")))
        label = r.get("nome_area")
        if code_prov == label:
            agree += 1
            per_case[r["_case"]]["AGREE"] += 1
            continue
        disagree += 1
        comune = (r.get("name_4") or "").strip().upper()
        if code_prov == "Firenze" and label == "Prato" and comune in PRATO_COMUNI:
            kind = "ADMIN_REFORM_PRATO"
        elif code_prov == "Firenze" and label == "Prato":
            kind = "PRATO_LABEL_BUT_COMUNE_NOT_IN_PRATO_PROVINCE"
        else:
            kind = "MISLABEL"
        key = (kind, code_prov, label, comune)
        dis_detail[key] += 1
        dis_rows[kind].append(r)
        per_case[r["_case"]][kind] += 1

    res["AGREE"] = agree
    res["DISAGREE"] = disagree
    res["PER_CASE"] = {k: dict(v) for k, v in per_case.items()}
    res["DISAGREEMENT_BREAKDOWN"] = [
        {"KIND": k[0], "PROV_FROM_ISTAT_CODE": k[1], "PROV_FROM_LABEL": k[2],
         "COMUNE": k[3], "N_ROWS": n} for k, n in sorted(dis_detail.items(), key=lambda kv: -kv[1])]

    # the mislabels, fully described
    mis = dis_rows["MISLABEL"]
    res["MISLABEL_ROWS"] = {
        "N": len(mis), "OF": N,
        "DISTINCT_FIELDS": sorted({r.get("id_field") for r in mis}),
        "DISTINCT_ADMIN_CODES": sorted({r.get("admin_code") for r in mis}),
        "DISTINCT_COMUNI": sorted({r.get("name_4") for r in mis}),
        "DISTINCT_NAME_5": sorted({r.get("name_5") for r in mis}),
        "NOME_AREA": sorted({r.get("nome_area") for r in mis}),
        "NAME_3": sorted({r.get("name_3") for r in mis}),
        "ID_AREA": sorted({r.get("id_area") for r in mis}),
        "ADMIN_CODE_3": sorted({r.get("admin_code_3") for r in mis}),
        "ORG_NAME": sorted({str(r.get("org_name")) for r in mis}),
        "YEARS": sorted({r.get("date", "")[:4] for r in mis}),
        "DATE_RANGE": [min(r.get("date") for r in mis), max(r.get("date") for r in mis)],
        "LATLON": sorted(f"{a},{b}" for a, b in {(r.get("lat"), r.get("lon")) for r in mis}),
        "CASES": dict(collections.Counter(r["_case"] for r in mis)),
        "SAMPLE": [{k: r.get(k) for k in ("id_field", "id_survey", "date", "nome_area", "name_3",
                                          "admin_code", "name_4", "name_5", "lat", "lon", "val")}
                   for r in mis[:5]],
    }

    # Prato: which comuni, and is any Prato-labelled row served with a 100xxx code?
    prato_rows = [r for r in rows if r.get("nome_area") == "Prato"]
    res["PRATO"] = {
        "N_ROWS_LABELLED_PRATO": len(prato_rows), "OF": N,
        "CODE_PREFIXES_SEEN": dict(collections.Counter(
            prov_from_code(r.get("admin_code")) for r in prato_rows)),
        "COMUNI": dict(collections.Counter((r.get("name_4") or "").strip().upper()
                                           for r in prato_rows)),
        "ANY_MODERN_100_CODE": any(prov_from_code(r.get("admin_code")) == "100" for r in rows),
        "COMUNI_NOT_IN_PRATO_PROVINCE": sorted(
            {(r.get("name_4") or "").strip().upper() for r in prato_rows}
            - PRATO_COMUNI),
        "PRATO_COMUNI_LABELLED_FIRENZE": dict(collections.Counter(
            (r.get("name_4") or "").strip().upper() for r in rows
            if (r.get("name_4") or "").strip().upper() in PRATO_COMUNI
            and r.get("nome_area") != "Prato")),
    }

    # does nome_area ever disagree with name_3 (the source's OTHER province field)?
    d3 = [r for r in rows if r.get("nome_area") != r.get("name_3")]
    res["NOME_AREA_VS_NAME_3"] = {
        "N": len(d3), "OF": N,
        "PAIRS": {f"nome_area={a} | name_3={b}": n for (a, b), n in
                  collections.Counter((r.get("nome_area"), r.get("name_3")) for r in d3).items()},
    }
    # and admin_code_3 vs id_area
    da = [r for r in rows if r.get("admin_code_3") != r.get("id_area")]
    res["ADMIN_CODE_3_VS_ID_AREA"] = {"N": len(da), "OF": N}

    json.dump(res, open(os.path.join(HERE, "rt4_geo_02_istat_vs_label.json"), "w"),
              indent=1, ensure_ascii=False, default=str)

    print(f"ROWS (3 cases) = {N}")
    print(f"  province label AGREES with ISTAT comune code : {agree}/{N} = {100*agree/N:.4f}%")
    print(f"  province label DISAGREES                     : {disagree}/{N} = {100*disagree/N:.4f}%")
    print("\n  breakdown:")
    for d in res["DISAGREEMENT_BREAKDOWN"]:
        print(f"    {d['N_ROWS']:6d}  {d['KIND']:38s} code={d['PROV_FROM_ISTAT_CODE']:13s} "
              f"label={d['PROV_FROM_LABEL']:13s} comune={d['COMUNE']}")
    print("\n  PRATO:", json.dumps(res["PRATO"], ensure_ascii=False, indent=2))
    print("\n  MISLABEL:", json.dumps(res["MISLABEL_ROWS"], ensure_ascii=False, indent=2))
    print("\n  nome_area vs name_3:", res["NOME_AREA_VS_NAME_3"])
    print("  admin_code_3 vs id_area disagreements:", res["ADMIN_CODE_3_VS_ID_AREA"])


if __name__ == "__main__":
    main()
