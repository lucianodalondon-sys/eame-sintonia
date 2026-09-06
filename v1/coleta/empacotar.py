#!/usr/bin/env python3
"""
empacotar.py — DEPARTAMENTO DE COLETA. Emite o COLLECTION_PACKAGE.

A coleta nao decide valor estrategico. Ela responde uma pergunta so: o que foi
captado, de onde, quando, e em que estado de leitura ficou. Quem interpreta e a
INTELIGENCIA; quem mostra e o CASCO.

    OFFICIAL_REGISTRY -> REGISTRY_SNAPSHOT -> PRODUCT_IDENTITY -> LABEL_DISCOVERY
    -> PDF_CAPTURE -> RAW_PRESERVATION -> HASH -> TEXT_EXTRACTION
    -> STRUCTURE_CANDIDATES -> COLLECTION_PACKAGE

Nunca escreve "COMPLETE" sozinho. Cada cobertura diz completa DE QUE.
"""
import csv, hashlib, json, os, re, subprocess, sys, datetime
from collections import Counter

P = "pilot-label-intelligence"
CANON_REF = "sintonia/canonical @ bdb57cf7379a4b8b94b3ef117fb3da469fca0764"
CANON = "/tmp/claude-0/-home-user-eame-sintonia/113d92e8-e962-52b2-b6d1-c8c3e286096e/scratchpad/canonical"
INACT = {"Revocato", "Scaduto"}

# Estados de leitura. Sao ESCADA: cada um pressupoe o anterior, e nenhum
# significa o seguinte.
ESTADOS = ["LABEL_DISCOVERED", "LABEL_DOWNLOADED", "TEXT_EXTRACTED", "LABEL_READ",
           "USE_ROWS_STRUCTURED", "DOSE_STRUCTURED", "PHI_STRUCTURED", "NEEDS_REVIEW"]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def dt(s):
    s = (s or "").strip()
    if not s or s == "-":
        return None
    try:
        return datetime.datetime.strptime(s, "%d/%m/%Y").date().isoformat()
    except ValueError:
        return None


MESES_IT = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6,
            "luglio": 7, "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11,
            "dicembre": 12}
RX_VIGENCIA = re.compile(
    r"valida\s+dal\s+(\d{1,2})\s+([a-z]+)\s+(\d{4})\s+al\s+(\d{1,2})\s+([a-z]+)\s+(\d{4})", re.I)


def validade_da_etichetta(reg, pdfs, cache):
    """Janela de vigencia que a PROPRIA etichetta declara, quando ela declara."""
    import subprocess, unicodedata
    os.makedirs(cache, exist_ok=True)
    alvo = os.path.join(cache, f"{reg}.txt")
    if not os.path.exists(alvo) or os.path.getsize(alvo) == 0:
        pdf = os.path.join(pdfs, f"{reg}.pdf")
        if not os.path.exists(pdf):
            return {"LABEL_VALID_FROM": "NOT_CHECKED", "LABEL_VALID_TO": "NOT_CHECKED"}
        try:
            subprocess.run(["pdftotext", "-layout", pdf, alvo], check=True,
                           capture_output=True, timeout=180)
        except Exception:
            return {"LABEL_VALID_FROM": "NOT_CHECKED", "LABEL_VALID_TO": "NOT_CHECKED"}
    t = open(alvo, encoding="utf-8", errors="replace").read()
    t = "".join(c for c in unicodedata.normalize("NFD", t)
                if unicodedata.category(c) != "Mn").lower()
    t = re.sub(r"\s+", " ", t)
    m = RX_VIGENCIA.search(t)
    if not m:
        return {"LABEL_VALID_FROM": "NOT_PRESENT", "LABEL_VALID_TO": "NOT_PRESENT"}
    def iso(d, mes, ano):
        n = MESES_IT.get(mes)
        return f"{ano}-{n:02d}-{int(d):02d}" if n else "NOT_PARSED"
    return {"LABEL_VALID_FROM": iso(m.group(1), m.group(2), m.group(3)),
            "LABEL_VALID_TO": iso(m.group(4), m.group(5), m.group(6)),
            "LABEL_VALIDITY_QUOTE": m.group(0)}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--registro", default=f"{P}/registry/snapshots/PROD_FTS_6_20260831.csv")
    ap.add_argument("--registro-url",
                    default="https://www.dati.salute.gov.it/sites/default/files/opendata/PROD_FTS_6_20260831.csv")
    ap.add_argument("--pdfdir", default=f"{P}/labels/pdf")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--cachetxt", default="/tmp/tetotxt")
    ap.add_argument("--out", default="v1/dados/COLLECTION-PACKAGE.json")
    a = ap.parse_args()

    snap_sha = sha(a.registro)
    snap_id = "PROD_FTS_6_" + re.search(r"(\d{8})", os.path.basename(a.registro)).group(1)

    # ---- reuso apontado: URL/hash/data de vigencia do rotulo, e os pares
    man = json.load(open(f"{CANON}/data/samples/IT-ROTULOS-V1/IT-ROTULOS-LEITURA-RUN.json",
                         encoding="utf-8"))
    manif = {i["REGISTRATION_ID"]: i for i in man["ITEMS"]}
    pares = json.load(open(f"{CANON}/data/samples/IT-ROTULOS-V1/IT-ROTULOS-PARES-V3.json",
                           encoding="utf-8"))["PAIRS"]
    por_reg = {}
    for x in pares:
        por_reg.setdefault(x["REGISTRATION_ID"], []).append(x)

    doses = {}
    dz = f"{P}/demo/IT-DOSES.json"
    if os.path.exists(dz):
        for lab in json.load(open(dz, encoding="utf-8"))["LABELS"]:
            doses[lab["REGISTRATION_ID"]] = lab

    rows = list(csv.DictReader(open(a.registro, encoding="utf-8", errors="replace"),
                               delimiter=";"))
    itens = []
    for r in rows:
        if "ADAMA" not in (r.get("ragione_sociale") or "").upper():
            continue
        if (r.get("stato_amministrativo") or "").strip() in INACT:
            continue
        reg = (r.get("num_registrazione") or "").strip()
        pdf = os.path.join(a.pdfdir, f"{reg}.pdf")
        tem_pdf = os.path.exists(pdf)
        mm = manif.get(reg, {})
        dz_l = doses.get(reg, {})
        dose_rows = dz_l.get("ROWS") or []
        texto = "NOT_KNOWN"
        if tem_pdf:
            try:
                t = subprocess.run(["pdftotext", "-q", pdf, "-"], capture_output=True,
                                   text=True, timeout=60).stdout
                texto = len(t.strip())
            except Exception:
                texto = "EXTRACTION_FAILED"

        estados = {e: False for e in ESTADOS}
        estados["LABEL_DISCOVERED"] = bool(mm.get("LABEL_URL"))
        estados["LABEL_DOWNLOADED"] = tem_pdf
        estados["TEXT_EXTRACTED"] = isinstance(texto, int) and texto > 200
        estados["LABEL_READ"] = estados["TEXT_EXTRACTED"]
        estados["USE_ROWS_STRUCTURED"] = bool(por_reg.get(reg))
        estados["DOSE_STRUCTURED"] = bool(dose_rows)
        estados["PHI_STRUCTURED"] = False          # nada de PHI e publicado, por decisao
        estados["NEEDS_REVIEW"] = any(x.get("NEEDS_REVIEW") for x in dose_rows)

        itens.append({
            "SOURCE_ID": "IT-MINSAL-FITOSANITARI",
            "SOURCE_AUTHORITY": "Ministero della Salute (Italia)",
            "SOURCE_URL": a.registro_url,
            "PRODUCT_NAME_RAW": (r.get("denominazione_prodotto") or "").strip(),
            "REGISTRATION_ID": reg,
            "HOLDER_RAW": (r.get("ragione_sociale") or "").strip(),
            "STATUS_RAW": (r.get("stato_amministrativo") or "").strip(),
            "ACTIVE_INGREDIENTS_RAW": (r.get("sostanze_attive") or "").strip() or "NOT_PRESENT",
            "FORMULATION_RAW": (r.get("descrizione_formulazione") or "").strip() or "NOT_PRESENT",
            "ACTIVITY_RAW": (r.get("attivita") or "").strip() or "NOT_PRESENT",
            "REGISTERED_AT": dt(r.get("data_registrazione")) or "NOT_PRESENT",
            "EXPIRY_RAW": dt(r.get("data_scadenza_autorizzazione")) or "NOT_PRESENT",
            "PDF_URL": mm.get("LABEL_URL", "NOT_KNOWN"),
            "PDF_SHA256": (sha(pdf) if tem_pdf else "NOT_KNOWN"),
            "PDF_BYTES": (os.path.getsize(pdf) if tem_pdf else "NOT_KNOWN"),
            "LABEL_EFFECTIVE_AT": mm.get("MANIFEST_LABEL_DATE", "NOT_KNOWN"),
            # A etichetta as vezes declara a PROPRIA janela de vigencia, e a
            # ferramenta guardava so o inicio. 002732 (GOLTIX) escreve
            # "Etichetta autorizzata con Decreto Dirigenziale del 22 luglio 2024
            # valida dal 22 luglio 2024 al 18 novembre 2024": guardar so o
            # "dal" e ficar com a metade que envelhece bem. E o unico rotulo do
            # corpus que traz a frase — medido nos 163 — e por isso mesmo o
            # unico caso em que a omissao passaria despercebida.
            **validade_da_etichetta(reg, a.pdfdir, a.cachetxt),
            "REGISTRY_SNAPSHOT_ID": snap_id,
            "REGISTRY_SNAPSHOT_SHA256": snap_sha,
            "CAPTURED_AT": mm.get("BASELINE_CAPTURED_AT") or man.get("CAPTURED_AT", "NOT_KNOWN"),
            "DOCUMENT_ID": (mm.get("LABEL_URL", "").split("id=")[-1] or "NOT_KNOWN"),
            "RAW_PATH": (pdf if tem_pdf else "NOT_PRESERVED"),
            "TEXT_PATH": "NOT_PRESERVED",   # texto e reextraido sob demanda, nao arquivado
            "TEXT_CHARS": texto,
            "PARSER_VERSION": {"use_rows": "it_rotulo_parser/3.4.0 (reuso, " + CANON_REF + ")",
                               "dose": "v1/dose_extrair (painel + validacao por fios)"},
            "COLLECTION_RUN_ID": a.run_id,
            "READ_STATES": estados,
            "USE_ROW_COUNT": len(por_reg.get(reg, [])),
            "DOSE_ROW_COUNT": len(dose_rows),
            "DOSE_PARSE_STATE": dz_l.get("PARSE_STATE", "NOT_ATTEMPTED"),
        })

    n = len(itens)
    def cov(k):
        c = sum(1 for i in itens if i["READ_STATES"][k])
        return {"COVERED": c, "OF": n, "PCT": round(100.0 * c / n, 1) if n else "NOT_KNOWN"}

    pkg = {
        "PACKAGE": "IT-COLLECTION-PACKAGE",
        "COUNTRY": "IT",
        "HOLDER_SCOPE": "ADAMA (5 entidades juridicas)",
        "COLLECTION_RUN_ID": a.run_id,
        "REGISTRY_SNAPSHOT_ID": snap_id,
        "REGISTRY_SNAPSHOT_SHA256": snap_sha,
        "SOURCE_AUTHORITY": "Ministero della Salute (Italia)",
        "LICENSE": "Italian Open Data Licence v2.0",
        "O_QUE_ISTO_E": "o que foi captado, de onde, quando, e em que estado de leitura ficou",
        "O_QUE_ISTO_NAO_E": ("nao interpreta, nao prioriza, nao roteia. Coleta nao decide "
                             "valor estrategico"),
        "PRODUCTS": n,
        "COVERAGE": {
            "LABEL_DISCOVERY_COVERAGE": cov("LABEL_DISCOVERED"),
            "LABEL_DOWNLOAD_COVERAGE": cov("LABEL_DOWNLOADED"),
            "TEXT_EXTRACTION_COVERAGE": cov("TEXT_EXTRACTED"),
            "LABEL_READ_COVERAGE": cov("LABEL_READ"),
            "AUTHORIZED_USE_ROW_COVERAGE": cov("USE_ROWS_STRUCTURED"),
            "DOSE_COVERAGE": cov("DOSE_STRUCTURED"),
            "PHI_COVERAGE": cov("PHI_STRUCTURED"),
        },
        "COVERAGE_NOTE": ("cada cobertura conta uma coisa diferente e nenhuma implica a "
                          "seguinte. PHI_COVERAGE = 0 por decisao: o extrator de carencia "
                          "esta marcado PROTOTYPE_NOT_SHIPPED e nada e publicado"),
        "ITEMS": itens,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(pkg, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in pkg["COVERAGE"].items():
        print(f'  {k:<32} {v["COVERED"]:>4}/{v["OF"]}  {v["PCT"]}%', file=sys.stderr)
    print(f'  escrito {a.out}', file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
