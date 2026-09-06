#!/usr/bin/env python3
"""
test_ruido.py — tenta FABRICAR mudanca falsa. Se conseguir, a ferramenta reprova.

O piloto mediu 528 diferencas brutas contra 34 mudancas reais. Isso significa que
o modo de falha dominante desta ferramenta nao e deixar de ver mudanca: e ver
mudanca onde nao houve. Estes testes existem para atacar exatamente isso.

Cada teste pega dados REAIS do acervo, aplica uma perturbacao que NAO muda
regulacao nenhuma, e exige que o motor emita ZERO evento.

    DOCUMENT_CHANGED  != REGULATORY_MEANING_CHANGED
    SOURCE_REORDER    != LABEL_CHANGE_EVENT
"""
import csv, hashlib, io, json, os, random, sys, tempfile

sys.path.insert(0, "pilot-label-intelligence/bin")
import registro_it as RI

SNAP = "pilot-label-intelligence/registry/snapshots"
BASE = os.path.join(SNAP, "PROD_FTS_6_20260831.csv")
FALHAS = []
PASSOU = []


def carrega(path):
    return RI.adama_rows(RI.read_rows(path))


def eventos(a, b):
    meta = {"sha256": "x" * 16, "date": "TESTE", "url": "teste"}
    ev = RI.diff(a, b, dict(meta), dict(meta))
    return RI.mark_oscillations(ev)


def reais(ev):
    return [e for e in ev if not e.get("UNSTABLE_SOURCE")]


def checa(nome, ev, lei):
    r = reais(ev)
    if r:
        FALHAS.append({"TESTE": nome, "LEI": lei, "EVENTOS_FABRICADOS": len(r),
                       "AMOSTRA": [{k: e[k] for k in ("REGISTRATION_ID", "CHANGE_TYPE",
                                                      "BEFORE", "AFTER")} for e in r[:3]]})
        print(f"  FAIL  {nome}: {len(r)} eventos fabricados")
    else:
        PASSOU.append({"TESTE": nome, "LEI": lei})
        print(f"  ok    {nome}")


def perturba(idx, fn):
    """Copia o indice aplicando fn a cada linha."""
    out = {}
    for k, r in idx.items():
        rr = dict(r)
        fn(rr)
        out[k] = rr
    return out


A = carrega(BASE)
print(f"base: {len(A)} registros ADAMA ativos\n")

# --- N-01 reorder de campo multivalorado
def reorder(r):
    for campo in ("indicazioni_di_pericolo", "sostanze_attive"):
        v = (r.get(campo) or "")
        if "|" in v:
            p = v.split("|")
            r[campo] = "|".join(p[1:] + p[:1])
checa("reorder de lista multivalorada", eventos(A, perturba(A, reorder)), "N-01")

# --- N-01 reorder invertido total
def reorder_rev(r):
    for campo in ("indicazioni_di_pericolo", "sostanze_attive"):
        v = (r.get(campo) or "")
        if "|" in v:
            r[campo] = "|".join(reversed(v.split("|")))
checa("reorder invertido da lista de perigo", eventos(A, perturba(A, reorder_rev)), "N-01")

# --- N-02 whitespace
def espaco(r):
    for campo in list(r):
        if isinstance(r[campo], str) and r[campo]:
            r[campo] = "  " + r[campo].replace(" ", "  ") + "\t"
checa("whitespace em todos os campos", eventos(A, perturba(A, espaco)), "N-02")

# --- N-02 whitespace dentro de campo multivalorado
def espaco_multi(r):
    v = (r.get("indicazioni_di_pericolo") or "")
    if "|" in v:
        r["indicazioni_di_pericolo"] = " | ".join(x.strip() for x in v.split("|"))
checa("espaco em volta do separador |", eventos(A, perturba(A, espaco_multi)), "N-02")

# --- N-04 mesma captura duas vezes
checa("mesmo instantaneo comparado consigo", eventos(A, carrega(BASE)), "N-04")

# --- N-04 arquivo recapturado com outro nome, conteudo identico
tmp = os.path.join(tempfile.gettempdir(), "PROD_FTS_6_99999999.csv")
with open(BASE, "rb") as s, open(tmp, "wb") as d:
    d.write(s.read())
checa("mesmo conteudo sob outro nome de arquivo", eventos(A, carrega(tmp)), "N-04")

# --- ordem das LINHAS do CSV (layout do arquivo, nao do dado)
linhas = RI.read_rows(BASE)
emb = linhas[:]
random.Random(7).shuffle(emb)
tmp2 = os.path.join(tempfile.gettempdir(), "embaralhado.csv")
with open(tmp2, "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=linhas[0].keys(), delimiter=";")
    w.writeheader()
    w.writerows(emb)
checa("linhas do CSV embaralhadas", eventos(A, carrega(tmp2)), "N-02/layout")

# --- N-03 oscilacao A -> B -> A
def troca_perigo(r):
    v = (r.get("indicazioni_di_pericolo") or "")
    if "|" in v:
        p = v.split("|")
        r["indicazioni_di_pericolo"] = "|".join(p[1:] + p[:1])
B = perturba(A, troca_perigo)
ida = eventos(A, B)
volta = eventos(B, A)
todos = RI.mark_oscillations(ida + volta)
checa("oscilacao ida e volta no mesmo campo", todos, "N-03")

# --- N-05 parser diferente: mesmo documento lido com outro dialeto de CSV
def via_stringio(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    rd = csv.DictReader(io.StringIO(txt), delimiter=";")
    return RI.adama_rows(list(rd))
checa("mesmo documento lido por outro leitor de CSV", eventos(A, via_stringio(BASE)), "N-05")

# --- CONTROLE POSITIVO: uma mudanca REAL tem de passar
def muda_validade(r):
    if r.get("num_registrazione", "").strip() == "015275":
        r["data_scadenza_autorizzazione"] = "31/12/2099"
C = perturba(A, muda_validade)
ev = reais(eventos(A, C))
if len(ev) == 1 and ev[0]["CHANGE_TYPE"] == "EXPIRY_CHANGED":
    PASSOU.append({"TESTE": "controle positivo: mudanca real e detectada", "LEI": "R-01"})
    print("  ok    controle positivo: mudanca real de validade E detectada")
else:
    FALHAS.append({"TESTE": "controle positivo", "LEI": "R-01",
                   "PROBLEMA": f"esperado 1 EXPIRY_CHANGED, obtido {len(ev)}"})
    print(f"  FAIL  controle positivo: esperado 1 evento, obtido {len(ev)}")

# --- CONTROLE POSITIVO 2: status real muda
def muda_status(r):
    if r.get("num_registrazione", "").strip() == "015275":
        r["stato_amministrativo"] = "Revocato"
D = perturba(A, muda_status)
ev2 = reais(eventos(A, D))
tipos = {e["CHANGE_TYPE"] for e in ev2}
if "PRODUCT_REMOVED" in tipos or "STATUS_CHANGED" in tipos:
    PASSOU.append({"TESTE": "controle positivo: revoga e detectada", "LEI": "R-02"})
    print("  ok    controle positivo: revoga E detectada")
else:
    FALHAS.append({"TESTE": "controle positivo revoga", "LEI": "R-02",
                   "PROBLEMA": f"tipos obtidos: {tipos}"})
    print(f"  FAIL  controle positivo revoga: {tipos}")

res = {"SUITE": "FALSE-CHANGE-NOISE-TEST",
       "O_QUE_ISTO_TESTA": ("se o motor fabrica mudanca a partir de perturbacao que nao muda "
                            "regulacao nenhuma, e se ainda assim enxerga mudanca real"),
       "PASSOU": len(PASSOU), "FALHOU": len(FALHAS),
       "FALSE_CHANGE_NOISE_TEST": "PASS" if not FALHAS else "FAIL",
       "TESTES_OK": PASSOU, "FALHAS": FALHAS}
json.dump(res, open("v1/testes/RESULTADO-RUIDO.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f'\n  {len(PASSOU)} passaram, {len(FALHAS)} falharam '
      f'-> FALSE_CHANGE_NOISE_TEST = {res["FALSE_CHANGE_NOISE_TEST"]}')
sys.exit(1 if FALHAS else 0)
