#!/usr/bin/env python3
"""
test_portoes.py — checa mecanicamente os portoes que a missao exige.

Nao substitui o red team humano/agente: cobre so o que da para verificar por
programa, que e justamente onde um humano cansa e deixa passar.
"""
import json, os, re, subprocess, sys
from collections import Counter

R = []
def ok(g, d=""):  R.append({"GATE": g, "STATE": "PASS", "DETALHE": d}); print(f"  PASS  {g}  {d}")
def fail(g, d):   R.append({"GATE": g, "STATE": "FAIL", "DETALHE": d}); print(f"  FAIL  {g}  {d}")

PAY = json.load(open("v1/dados/CASCO-PAYLOAD.json", encoding="utf-8"))
OBJ = PAY["objects"]
HTML = open("v1/casco/label-intelligence.html", encoding="utf-8").read()
REGRAS = open("v1/inteligencia/REGRAS.md", encoding="utf-8").read()

UNK = {"NOT_KNOWN","NOT_PROVED","NOT_PRESERVED","NOT_PRESENT","UNKNOWN","NOT_APPLICABLE",
       "NOT_ATTEMPTED","NOT_EMITTED_BY_THIS_TOOL","NOT_CHECKED"}

# --- 1. nenhuma ACTION emitida
acoes = {o["ACTION"] for o in OBJ}
if acoes == {"NOT_EMITTED_BY_THIS_TOOL"}:
    ok("UNPROVED_ACTION_ROUTING", f"nenhum objeto emite ACTION ({len(OBJ)} objetos)")
else:
    fail("UNPROVED_ACTION_ROUTING", f"ACTION com valores {acoes}")

# --- 2. todo roteamento aponta uma regra que EXISTE em REGRAS.md
ids = set(re.findall(r"`(C-\d\d|R-\d\d|N-\d\d|T-\d\d|G-\d\d)`", REGRAS))
faltando, semrule = set(), 0
for o in OBJ:
    for r in o["CAPABILITY_ROUTING"]:
        if not r.get("RULE_ID"):
            semrule += 1
        elif r["RULE_ID"] not in ids:
            faltando.add(r["RULE_ID"])
if semrule == 0 and not faltando:
    ok("ROUTING_RULE_EXISTS", f"todo roteamento aponta uma das {len(ids)} regras declaradas")
else:
    fail("ROUTING_RULE_EXISTS", f"{semrule} sem regra; ids inexistentes: {faltando}")

# --- 3. implicacao de negocio nunca afirmada
bi = {o["POTENTIAL_BUSINESS_IMPLICATION"] for o in OBJ}
ok("BUSINESS_IMPLICATION_GATED", f"todos NOT_PROVED") if bi == {"NOT_PROVED"} \
    else fail("BUSINESS_IMPLICATION_GATED", f"valores {bi}")

# --- 4. PHI nunca emitido
if not any(o["OBJECT_TYPE"] == "PHI_CHANGE" for o in OBJ):
    ok("PHI_GATE_G02", "nenhum PHI_CHANGE emitido, coerente com PHI_PROVED = 0")
else:
    fail("PHI_GATE_G02", "PHI_CHANGE emitido sem PHI provado")

# --- 5. RTV nunca RELEVANT
rtv = Counter(r["ROUTING_STATE"] for o in OBJ for r in o["CAPABILITY_ROUTING"]
              if r["CAPABILITY_ID"] == "COMMERCIAL_RTV")
ok("COMMERCIAL_GATE_G01", f"RTV sempre {dict(rtv)}") if set(rtv) == {"NOT_RELEVANT"} \
    else fail("COMMERCIAL_GATE_G01", f"RTV com estados {dict(rtv)}")

# --- 6. toda afirmacao material tem rota para fonte
sem = []
for o in OBJ:
    tem_doc = any(str(o.get(k, "")) not in UNK and o.get(k) for k in
                  ("SOURCE_DOCUMENT_AFTER", "SOURCE_DOCUMENT_BEFORE"))
    tem_loc = str(o.get("EVIDENCE_LOCATION", "")) not in UNK
    tem_url = bool(o.get("SOURCE_URL"))
    if not (tem_doc and tem_loc and tem_url):
        sem.append({"id": o["INTELLIGENCE_OBJECT_ID"], "tipo": o["OBJECT_TYPE"],
                    "doc": tem_doc, "loc": tem_loc, "url": tem_url})
pct = round(100.0 * (len(OBJ) - len(sem)) / len(OBJ), 1)
ok("MATERIAL_CLAIMS_WITH_EVIDENCE", f"{pct}% ({len(OBJ)-len(sem)}/{len(OBJ)})") if not sem \
    else fail("MATERIAL_CLAIMS_WITH_EVIDENCE", f"{pct}% — {len(sem)} sem rota completa: {sem[:3]}")

# --- 7. nenhum "-" / "N/A" significando desconhecido no HTML renderizado
suspeitos = re.findall(r"<td[^>]*>\s*(?:-|N/A|n/a|none|null|undefined)\s*</td>", HTML)
ok("UNKNOWN_HIDDEN_OR_FILLED", "nenhuma celula com traco/N-A no template") if not suspeitos \
    else fail("UNKNOWN_HIDDEN_OR_FILLED", f"{len(suspeitos)} celulas suspeitas")

# --- 8. o token de ignorancia e renderizado com o proprio nome
if 'class="unknown"' in HTML and "NOT_KNOWN" in HTML:
    ok("UNKNOWN_VISIBLE", "tokens de ignorancia renderizados com nome proprio")
else:
    fail("UNKNOWN_VISIBLE", "nao encontrei o estilo/token de desconhecido")

# --- 9. expiry nunca vira withdrawal
proibido = ["stop selling", "pare de vender", "retirar do mercado", "withdrawn",
            "queda de demanda", "demand drop", "stock risk", "risco de estoque",
            "reduza estoque", "fora do mercado"]
achou = [p for p in proibido if p in HTML.lower()]
ok("EXPIRY_AS_WITHDRAWAL", "nenhuma frase de retirada/demanda/estoque na interface") if not achou \
    else fail("EXPIRY_AS_WITHDRAWAL", f"frases encontradas: {achou}")

# --- 10. parser failure nunca apresentado como ausencia regulatoria
if "PARSER_FAILURE != REGULATORY_ABSENCE" in HTML:
    ok("PARSER_FAILURE_AS_ABSENCE", "a lei aparece na interface onde o estado de leitura e mostrado")
else:
    fail("PARSER_FAILURE_AS_ABSENCE", "a lei nao esta visivel na interface")

# --- 11. isolamento: nada fora de v1/ e pilot-label-intelligence/
dif = subprocess.run(["git", "diff", "--name-only", "df3a4fd..HEAD"],
                     capture_output=True, text=True).stdout.split()
fora = [f for f in dif if not (f.startswith("v1/") or f.startswith("pilot-label-intelligence/"))]
ok("ISOLATION", f"{len(dif)} arquivos, todos dentro de v1/ e pilot/") if not fora \
    else fail("ISOLATION", f"arquivos fora do escopo: {fora}")

# --- 12. canonical intocada
ls = subprocess.run(["git", "ls-remote", "origin", "refs/heads/sintonia/canonical"],
                    capture_output=True, text=True).stdout.split()
ok("CANONICAL_TOUCHED", "canonical segue em bdb57cf") \
    if ls and ls[0] == "bdb57cf7379a4b8b94b3ef117fb3da469fca0764" \
    else fail("CANONICAL_TOUCHED", f"canonical em {ls[:1]}")

# --- 13. cobertura nunca publicada como numero unico
cov = PAY["coverage"]
ok("COVERAGE_NOT_SINGLE_NUMBER", f"{len(cov)} coberturas separadas") if len(cov) >= 6 \
    else fail("COVERAGE_NOT_SINGLE_NUMBER", f"so {len(cov)} coberturas")

# --- 14. o filtro de ruido passa
r = subprocess.run(["python3", "v1/testes/test_ruido.py"], capture_output=True, text=True)
ok("FALSE_CHANGE_NOISE_TEST", "11 testes adversariais passam") if r.returncode == 0 \
    else fail("FALSE_CHANGE_NOISE_TEST", "a suite de ruido falhou")

falhas = [x for x in R if x["STATE"] == "FAIL"]
json.dump({"SUITE": "PORTOES-V1", "PASS": len(R) - len(falhas), "FAIL": len(falhas),
           "RESULTS": R}, open("v1/testes/RESULTADO-PORTOES.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\n  {len(R)-len(falhas)}/{len(R)} portoes passam")
sys.exit(1 if falhas else 0)
