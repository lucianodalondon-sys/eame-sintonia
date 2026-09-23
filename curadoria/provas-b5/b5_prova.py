# -*- coding: utf-8 -*-
import json, os, re, subprocess, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
D = Path(r"C:\Users\London1\AppData\Local\Temp\b5-copia-1810"); DP = Path(r"C:\Users\London1\AppData\Local\Temp\b5-copia-1810-ponte")
os.chdir(D); sys.path.insert(0, str(D/"curadoria")); sys.path.insert(0, str(D/"candidatas"))
import fila as F, lifecycle as LC, collection_gate as CG, gatilho_discovery as GD, worker as W, ponte_candidatas as P
for nome, p in [("F.FILA", F.FILA), ("LC.LIVRO", LC.LIVRO), ("P.LEDGER", P.LEDGER), ("W.EVIDENCIA", W.EVIDENCIA), ("W.CONTRATOS", W.CONTRATOS)]:
    assert str(Path(p).resolve()).lower().startswith(str(D).lower()), (nome, p)
SAIDA = D/"B5-PROVA-COPIA.json"; LOG = D/"B5-PROVA-COPIA.ndjson"
def anota(e):
    e["AT"] = datetime.now(timezone.utc).isoformat()
    with LOG.open("a", encoding="utf-8") as fh: fh.write(json.dumps(e, ensure_ascii=False) + "\n")
def pais():
    r = subprocess.run(["py", "superficie/rede.py", "--portao-de-egresso", "IT"], cwd=D, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
    m = re.search(r'"EGRESS_COUNTRY_CODE": "([^"]+)"', r.stdout); return m.group(1) if m else "NAO SEI"
def guarda(onde):
    p = pais()
    if p != "IT":
        anota({"EVENTO": "PARADO_POR_EGRESSO", "PAIS": p, "ONDE": onde}); print("PARADO: egresso", p, onde, flush=True); sys.exit(3)
    return p
T0 = datetime.now(timezone.utc); AGORA_SIMULADO = T0 + timedelta(days=8)
n_livro0 = len(LC._ler_bruto()["TRANSICOES"])
el0 = set(CG.elegiveis()); anota({"EVENTO": "INICIO", "ELIGIBLE": len(el0), "AGORA_SIMULADO": AGORA_SIMULADO.isoformat(), "PAIS": guarda("inicio")})
estado = json.loads((D/"curadoria"/"SUPERVISOR-STATE.json").read_text(encoding="utf-8"))
pedidas, execs, voltas = set(), [], 0
while voltas < 25 and len(execs) < 200:
    voltas += 1; guarda("volta %d" % voltas)
    m = GD.talvez_alimentar(estado, descobrir_fn=lambda: {"BLOQUEADO_NA_PROVA_B5": True}, agora=AGORA_SIMULADO)
    novas = [x["SOURCE_ID"] for x in (m.get("REVALIDAR") or {}).get("ENFILEIRADAS", [])]
    pedidas.update(novas); anota({"EVENTO": "GATILHO", "VOLTA": voltas, "DECISAO": m.get("DECISAO"), "ACCOES": m.get("ACCOES"), "REVALIDAR": novas})
    while F.elegiveis() and len(execs) < 200:
        guarda("tarefa %d" % (len(execs) + 1))
        for r in W.correr(max_tarefas=1, pausa=1.0, verboso=False):
            execs.append(r); anota({"EVENTO": "TAREFA", **{k: r.get(k) for k in ("TASK_ID", "SOURCE_ID", "TASK_TYPE", "RESULTADO", "PORQUE")}})
    if el0 <= pedidas: break
guarda("fim")
el1 = set(CG.elegiveis()); tr = LC._ler_bruto()["TRANSICOES"][n_livro0:]
sairam = sorted(el0 - el1); entraram = sorted(el1 - el0)
porque = {s: [(t["OBSERVED_AT"][11:19], t.get("PREVIOUS_STATE"), t["NEW_STATE"], (t.get("REASON") or "")[:160]) for t in tr if t["SOURCE_ID"] == s] for s in sairam}
saiu_e_voltou = sorted(s for s in el0 & el1 if any(t["SOURCE_ID"] == s and t.get("PREVIOUS_STATE") == LC.READY_FOR_COLLECTION for t in tr))
from collections import Counter
r = {"DATASET": "B5-PROVA-COPIA", "INICIO": T0.isoformat(), "FIM": datetime.now(timezone.utc).isoformat(),
     "SIMULADO": "so o relogio do gatilho: +8 dias (REVALIDAR_ELEGIVEIS_DIAS=7); discovery desligado; tudo o resto e o codigo e os livros do vivo",
     "ELIGIBLE_ANTES": len(el0), "ELIGIBLE_DEPOIS": len(el1), "SAIRAM": sairam, "ENTRARAM": entraram,
     "SAIU_E_VOLTOU": saiu_e_voltou, "PEDIDAS_REVALIDAR": len(pedidas), "NAO_PEDIDAS": sorted(el0 - pedidas),
     "TAREFAS": len(execs), "RESULTADOS": dict(Counter(x["RESULTADO"] for x in execs)),
     "TRANSICOES_NOVAS_NO_LIVRO": len(tr), "PORQUE_SAIRAM": porque, "VOLTAS": voltas}
SAIDA.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
anota({"EVENTO": "FIM", "SAIRAM": sairam, "ELIGIBLE": [len(el0), len(el1)]})
print(json.dumps({k: r[k] for k in ("ELIGIBLE_ANTES", "ELIGIBLE_DEPOIS", "SAIRAM", "SAIU_E_VOLTOU", "TAREFAS", "RESULTADOS", "NAO_PEDIDAS")}, ensure_ascii=False), flush=True)
