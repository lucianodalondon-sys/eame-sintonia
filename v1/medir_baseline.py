#!/usr/bin/env python3
"""
medir_baseline.py — reconta o piloto A PARTIR DA FONTE, nao dos relatorios.

A missao V1 exige que nenhum numero seja herdado por estar escrito. Entao este
script abre os arquivos brutos e reconta: o CSV oficial do registro, os PDFs no
disco, a geometria versionada, e roda de novo o extrator e o validador. Onde a
fonte nao sustenta, escreve NOT_PROVED / NOT_KNOWN em vez de um numero.

Nao le ENTREGA-FINAL.md, nao le AUDITORIA.json, nao le IT-LABEL-INTELLIGENCE.json.
Le so o que e fonte ou artefato de reuso apontado por commit.
"""
import hashlib, json, os, subprocess, sys, csv
from collections import Counter

P = "pilot-label-intelligence"
CANON = "/tmp/claude-0/-home-user-eame-sintonia/113d92e8-e962-52b2-b6d1-c8c3e286096e/scratchpad/canonical"
INACT = {"Revocato", "Scaduto"}
R = {}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


# ---------------------------------------------------- 1. universo, do CSV oficial
csvp = f"{P}/registry/snapshots/PROD_FTS_6_20260831.csv"
if os.path.exists(csvp):
    rows = list(csv.DictReader(open(csvp, encoding="utf-8", errors="replace"), delimiter=";"))
    ad = [x for x in rows if "ADAMA" in (x["ragione_sociale"] or "").upper()
          and x["stato_amministrativo"] not in INACT]
    R["REGISTRY_ROWS_TOTAL"] = len(rows)
    R["PRODUCT_UNIVERSE"] = len(ad)
    R["PRODUCT_UNIVERSE_SOURCE"] = f"{csvp} sha256={sha(csvp)[:16]}"
    R["PRODUCT_UNIVERSE_BY_HOLDER"] = dict(Counter(x["ragione_sociale"] for x in ad))
    universo = {x["num_registrazione"].strip() for x in ad}
else:
    R["PRODUCT_UNIVERSE"] = "NOT_KNOWN — CSV oficial ausente do disco"
    universo = set()

# ---------------------------------------------------- 2. rotulos no disco
pdfdir = f"{P}/labels/pdf"
pdfs = sorted(f for f in os.listdir(pdfdir) if f.endswith(".pdf")) if os.path.isdir(pdfdir) else []
regs_pdf = {f[:-4] for f in pdfs}
R["LABEL_DOWNLOADED"] = len(pdfs)
R["LABEL_DOWNLOADED_IN_UNIVERSE"] = len(regs_pdf & universo) if universo else "NOT_KNOWN"
# integridade: todo arquivo comeca com %PDF-
ruins = [f for f in pdfs if open(os.path.join(pdfdir, f), "rb").read(5) != b"%PDF-"]
R["LABEL_DOWNLOADED_NOT_A_PDF"] = len(ruins)

# ---------------------------------------------------- 3. descoberta: URL oficial por produto
man = f"{CANON}/data/samples/IT-ROTULOS-V1/IT-ROTULOS-LEITURA-RUN.json"
if os.path.exists(man):
    m = json.load(open(man, encoding="utf-8"))
    itens = m["ITEMS"]
    R["LABEL_DISCOVERED"] = sum(1 for i in itens if i.get("LABEL_URL"))
    R["LABEL_DISCOVERED_SOURCE"] = ("sintonia/canonical @ bdb57cf "
                                    "data/samples/IT-ROTULOS-V1/IT-ROTULOS-LEITURA-RUN.json")
else:
    R["LABEL_DISCOVERED"] = "NOT_KNOWN — manifesto de canonical nao extraido neste checkout"

# ---------------------------------------------------- 4. texto: re-extraido AGORA
extraiu = vazio = falhou = 0
chars = 0
for f in pdfs:
    p = os.path.join(pdfdir, f)
    try:
        t = subprocess.run(["pdftotext", "-q", p, "-"], capture_output=True,
                           text=True, timeout=60).stdout
    except Exception:
        falhou += 1
        continue
    n = len(t.strip())
    chars += n
    if n > 200:
        extraiu += 1
    else:
        vazio += 1
R["TEXT_EXTRACTED"] = extraiu
R["TEXT_EXTRACTED_EMPTY_OR_TINY"] = vazio
R["TEXT_EXTRACTION_FAILED"] = falhou
R["TEXT_TOTAL_CHARS"] = chars
R["TEXT_EXTRACTED_METHOD"] = "pdftotext rodado agora sobre cada PDF do disco"

# ---------------------------------------------------- 5. cultura x alvo: reuso, recontado
# A lista de canonical continua sendo a preferida; a reconstruida
# (v1/fonte/pares_reconstruir.py) entra quando canonical nao esta no checkout, e
# a medicao diz qual das duas foi contada.
pares = f"{CANON}/data/samples/IT-ROTULOS-V1/IT-ROTULOS-PARES-V3.json"
if not os.path.exists(pares):
    pares = "v1/dados/IT-ROTULOS-PARES-RECONSTRUIDO.json"
if os.path.exists(pares):
    pp = json.load(open(pares, encoding="utf-8"))
    PA = pp["PAIRS"]
    R["AUTHORIZED_USE_PAIRS"] = len(PA)
    R["PRODUCTS_WITH_USE_ROWS"] = len({x["REGISTRATION_ID"] for x in PA})
    TAB = {"GEOMETRIC_TABLE", "MERGED_COLUMN_TABLE"}
    R["USE_PAIRS_FROM_TABLE_GEOMETRY"] = sum(1 for x in PA if x.get("ROUTE") in TAB)
    R["USE_PAIRS_FROM_TEXT_INFERENCE"] = sum(1 for x in PA if x.get("ROUTE") not in TAB)
    R["USE_PAIRS_WITHOUT_PAGE"] = sum(1 for x in PA if not x.get("PAGE"))
    R["USE_PAIRS_BY_ROUTE"] = dict(Counter(x.get("ROUTE") for x in PA))
    R["USE_PAIRS_WITH_LITERAL_QUOTE"] = 0
    R["USE_PAIRS_QUOTE_NOTE"] = ("os pares nao gravam SOURCE_QUOTE nem coordenada x; "
                                 "citacao literal e NOT_PRESERVED — medido no piloto")
    R["AUTHORIZED_USE_PAIRS_SOURCE"] = pares
else:
    R["AUTHORIZED_USE_PAIRS"] = "NOT_KNOWN"
    R["PRODUCTS_WITH_USE_ROWS"] = "NOT_KNOWN"

# ---------------------------------------------------- 6. historico do registro, dos arquivos
snapdir = f"{P}/registry/snapshots"
snaps = sorted(f for f in os.listdir(snapdir) if f.endswith(".csv")) if os.path.isdir(snapdir) else []
hashes = {}
for f in snaps:
    hashes.setdefault(sha(os.path.join(snapdir, f)), []).append(f)
R["HISTORICAL_SNAPSHOTS"] = len(snaps)
R["DISTINCT_HISTORICAL_DOCS"] = len(hashes)
R["REPUBLISHED_IDENTICAL"] = len(snaps) - len(hashes)
import re as _re
_d = sorted(_re.search(r"(\d{8})", f).group(1) for f in snaps) if snaps else []
R["HISTORY_WINDOW"] = f"{_d[0]}..{_d[-1]}" if _d else "NOT_KNOWN"

# ---------------------------------------------------- 7. mudancas: differ rodado de novo
sys.path.insert(0, f"{P}/bin")
import registro_it as RI

def _idx(path):
    return RI.adama_rows(RI.read_rows(path))

versoes, vistos = [], set()
for f in snaps:
    h = sha(os.path.join(snapdir, f))
    if h in vistos:
        continue
    vistos.add(h)
    versoes.append(os.path.join(snapdir, f))
bruto = normal = 0
eventos = []
prev = prevmeta = None
for path in versoes:
    idx = _idx(path)
    if prev is not None:
        bruto += RI.contar_diffs_de_campo(prev, idx, normalizar=False)
        normal += RI.contar_diffs_de_campo(prev, idx, normalizar=True)
        meta_a = {"sha256": sha(prevmeta), "date": os.path.basename(prevmeta)[12:20],
                  "url": "recontado localmente"}
        meta_b = {"sha256": sha(path), "date": os.path.basename(path)[12:20],
                  "url": "recontado localmente"}
        eventos += RI.diff(prev, idx, meta_a, meta_b)
    prev, prevmeta = idx, path
eventos = RI.mark_oscillations(eventos)
R["RAW_CHANGES"] = bruto
R["FIELD_DIFFS_AFTER_NORMALISATION"] = normal
R["FALSE_CHANGE_NOISE"] = bruto - normal
R["FALSE_CHANGE_NOISE_SHARE_PCT"] = round(100.0 * (bruto - normal) / bruto, 1) if bruto else "NOT_KNOWN"
R["TRUE_CHANGES"] = sum(1 for e in eventos if not e.get("UNSTABLE_SOURCE"))
R["TEXT_ONLY_CHANGES"] = sum(1 for e in eventos if e.get("UNSTABLE_SOURCE"))
R["TRUE_CHANGES_BY_TYPE"] = dict(Counter(e["CHANGE_TYPE"] for e in eventos
                                          if not e.get("UNSTABLE_SOURCE")))
R["CHANGE_METHOD"] = "differ do piloto reexecutado sobre os 54 documentos distintos"

# ---------------------------------------------------- 8. dose: extrator + validador de novo
import dose_extrair as DE, dose_validar as DV
prov = rev = tentados = comlinha = 0
vals = {"CHECKED": 0, "OK": 0, "CONTRADICTED": 0, "UNVERIFIABLE_NO_RULES": 0, "NOT_LOCATED": 0}
distintas = 0
for f in pdfs:
    rid = f[:-4]
    tentados += 1
    try:
        r = DE.extrair(os.path.join(pdfdir, f), rid, None)
    except Exception:
        continue
    rows = r.get("ROWS") or []
    if not rows:
        continue
    comlinha += 1
    s2 = DV.valida(os.path.join(pdfdir, f), rows, cache_fios="/tmp/fioscache")
    for k in vals:
        vals[k] += s2[k]
    seen = set()
    for x in rows:
        k = (x.get("CROP"), x.get("TARGET"), x.get("DOSE_CONCENTRATION"), x.get("DOSE_PER_HECTARE"))
        if k in seen:
            continue
        seen.add(k)
        distintas += 1
        if x.get("NEEDS_REVIEW"):
            rev += 1
        elif x.get("DOSE_PER_HECTARE") != "NOT_PRESENT" or x.get("DOSE_CONCENTRATION") != "NOT_PRESENT":
            prov += 1
R["DOSE_LABELS_ATTEMPTED"] = tentados
R["DOSE_LABELS_WITH_ROWS"] = comlinha
R["DOSE_ROWS_DISTINCT"] = distintas
R["DOSE_ROWS_PROVED"] = prov
R["DOSE_NEEDS_REVIEW"] = rev
R["DOSE_RULE_VALIDATION"] = vals
R["DOSE_METHOD"] = "dose_extrair + dose_validar reexecutados sobre os 163 PDFs"

# ---------------------------------------------------- 9. PHI
R["PHI_PROVED"] = 0
R["PHI_NOT_PROVED"] = len(pdfs)
R["PHI_NOTE"] = ("o extrator de carencia do piloto esta marcado PROTOTYPE_NOT_SHIPPED: "
                 "2 de 15 rotulos, com a primeira linha de cada bloco contaminada. "
                 "Nenhum PHI e publicado, entao PHI_PROVED = 0 por decisao, nao por ausencia "
                 "de carencia nas etichette")

# RECONCILIACAO. Esta medicao le a FONTE e reexecuta os extratores; a ferramenta
# publica o que sobra depois da camada de inteligencia. Os dois numeros nao tem
# de ser iguais — tem de ser explicados. Antes eles apareciam em telas
# diferentes sem que nada dissesse por que diferiam, e isso e a mesma doenca de
# publicar cobertura como numero unico.
try:
    _pay = json.load(open("v1/dados/CASCO-PAYLOAD.json", encoding="utf-8"))
    _pub_rows = sum(len(x["doses"]) for x in _pay["products"])
    _pub_labs = sum(1 for x in _pay["products"] if x["doses"])
    R["RECONCILIATION_WITH_PUBLISHED"] = {
        "O_QUE_ISTO_E": ("diferenca entre a RELEITURA CRUA da fonte (este arquivo) e o que a "
                         "ferramenta publica, com o mecanismo que explica cada delta"),
        "TRUE_CHANGES_MEASURED": R["TRUE_CHANGES"],
        "TRUE_CHANGES_PUBLISHED": _pay["history"]["true_changes"],
        "TRUE_CHANGES_DELTA": R["TRUE_CHANGES"] - _pay["history"]["true_changes"],
        "DOSE_ROWS_MEASURED_DISTINCT": R["DOSE_ROWS_DISTINCT"],
        "DOSE_ROWS_PUBLISHED_DISTINCT": _pub_rows,
        "DOSE_ROWS_DELTA": R["DOSE_ROWS_DISTINCT"] - _pub_rows,
        "DOSE_LABELS_MEASURED": R["DOSE_LABELS_WITH_ROWS"],
        "DOSE_LABELS_PUBLISHED": _pub_labs,
        "DOSE_LABELS_DELTA": R["DOSE_LABELS_WITH_ROWS"] - _pub_labs,
        "POR_QUE_O_DELTA_DE_DOSE": ("a releitura crua nao aplica o filtro de plausibilidade "
                                    "v1/inteligencia/dose_plausibilidade.py (regras P-01 a P-05), "
                                    "que descarta tabela que o extrator achou onde nao havia. "
                                    "O delta E o filtro; se ele fosse zero, o filtro nao estaria "
                                    "rodando"),
        "POR_QUE_O_DELTA_DE_MUDANCA": ("ambos os lados rodam o mesmo differ com a mesma "
                                       "normalizacao; delta diferente de zero aqui e defeito, "
                                       "nao decisao"),
    }
except Exception as _e:                       # payload ainda nao construido
    R["RECONCILIATION_WITH_PUBLISHED"] = {"STATE": "NOT_CHECKED", "WHY": str(_e)}

json.dump(R, open("v1/BASELINE-RAW.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in R.items():
    if isinstance(v, dict):
        print(f"  {k}: {json.dumps(v, ensure_ascii=False)[:130]}")
    else:
        print(f"  {k}: {v}")
