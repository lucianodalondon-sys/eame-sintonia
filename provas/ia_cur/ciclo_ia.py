"""Uma volta do ciclo do Curator na copia C:/cur/ciclo, SEM REDE (proxy numa porta fechada)."""
import os, sys, json, collections, time
import subprocess
COM_REDE = os.environ.get("CICLO_COM_REDE") == "1"
if not COM_REDE:
    os.environ["HTTP_PROXY"] = os.environ["HTTPS_PROXY"] = "http://127.0.0.1:9"
    os.environ["http_proxy"] = os.environ["https_proxy"] = "http://127.0.0.1:9"
    os.environ.pop("NO_PROXY", None); os.environ.pop("no_proxy", None)
def egresso():
    r = subprocess.run([sys.executable, "superficie/rede.py", "--portao-de-egresso", "IT"], cwd="C:/cur/ia-copia",
                       capture_output=True, text=True)
    ok = '"EGRESS_GATE": "PASS"' in r.stdout
    print("EGRESSO IT", "PASS" if ok else "FALHOU"); return ok
RAIZ = "C:/cur/ia-copia"
os.chdir(RAIZ)
sys.path.insert(0, RAIZ + "/curadoria")
import funil_do_curador as FU, gatilho_discovery as GD, worker as W, fila as F
N = int(sys.argv[1]) if len(sys.argv) > 1 else 60
if COM_REDE and not egresso():
    sys.exit("sem egresso IT: nao corre")
antes = FU.medir()
t0 = time.time()
m = GD.talvez_alimentar({}, descobrir_fn=lambda: {"SEM_REDE": True})
print("GATILHO", json.dumps({k: m[k] for k in ("ACCOES", "DECISAO", "AVANCO_ELEGIVEL") if k in m}, ensure_ascii=False))
print("  AVANCAR", json.dumps((m.get("AVANCAR") or {}).get("POR_REGRA"), ensure_ascii=False),
      "enfileiradas", len((m.get("AVANCAR") or {}).get("ENFILEIRADAS", [])))
res = W.correr(max_tarefas=N, pausa=(0.8 if COM_REDE else 0), verboso=False)
print("WORKER", len(res), "tarefas em %.0f s" % (time.time() - t0))
print("  ", collections.Counter((r.get("TASK_TYPE"), r["RESULTADO"]) for r in res).most_common())
print("  porques:", collections.Counter((r.get("PORQUE") or "")[:70] for r in res).most_common(6))
if COM_REDE:
    egresso()
depois = FU.medir()
def est(m):
    return {x["ESTADO"]: x["N"] for x in m["MAQUINA"]}
a, d = est(antes), est(depois)
print("ESTADOS antes->depois:", {k: (a.get(k, 0), d.get(k, 0)) for k in sorted(set(a) | set(d)) if a.get(k, 0) != d.get(k, 0)})
print("COM_TAREFA_ABERTA", antes["COM_TAREFA_ABERTA"], "->", depois["COM_TAREFA_ABERTA"])
print("FUNIL WEB   ", antes["FUNIL"]["WEB"], "\n         -> ", depois["FUNIL"]["WEB"])
print("FUNIL SOCIAL", antes["FUNIL"]["SOCIAL"], "\n         -> ", depois["FUNIL"]["SOCIAL"])
print("AVANCO_ELEGIVEL", antes["AVANCO_ELEGIVEL"], "->", depois["AVANCO_ELEGIVEL"])
json.dump({"ANTES": antes, "DEPOIS": depois, "GATILHO": m, "WORKER": res},
          open("C:/cur/ia-ciclo-%s-%d.json" % ("rede" if COM_REDE else "offline", N), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
