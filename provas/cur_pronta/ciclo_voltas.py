"""Voltas do ciclo (gatilho + worker) com rede pela VPN IT, ate o AVANCO acabar ou K voltas."""
import os, sys, json, subprocess, time, collections
RAIZ = "C:/cur/ciclo"; os.chdir(RAIZ); sys.path.insert(0, RAIZ + "/curadoria")
import funil_do_curador as FU, gatilho_discovery as GD, worker as W
def egresso():
    r = subprocess.run([sys.executable, "superficie/rede.py", "--portao-de-egresso", "IT"], capture_output=True, text=True)
    return '"EGRESS_GATE": "PASS"' in r.stdout
K = int(sys.argv[1]); todas = []
for v in range(K):
    if not egresso():
        print("volta", v, "PARADA: sem egresso IT"); break
    m = GD.talvez_alimentar({}, descobrir_fn=lambda: {"SEM_REDE": True})
    res = W.correr(max_tarefas=120, pausa=0.8, verboso=False); todas += res
    print("volta", v, "avanco_elegivel", m.get("AVANCO_ELEGIVEL"), "enfileiradas",
          len((m.get("AVANCAR") or {}).get("ENFILEIRADAS", [])), "tarefas", len(res),
          dict(collections.Counter((r.get("TASK_TYPE"), r["RESULTADO"]) for r in res)), flush=True)
    if not m.get("AVANCO_ELEGIVEL") and not res:
        break
print("EGRESSO no fim:", "PASS" if egresso() else "FALHOU")
d = FU.medir()
print("FUNIL WEB", d["FUNIL"]["WEB"]); print("FUNIL SOCIAL", d["FUNIL"]["SOCIAL"])
print("MAQUINA", {x["ESTADO"]: x["N"] for x in d["MAQUINA"]}); print("AVANCO", d["AVANCO_ELEGIVEL"])
json.dump({"DEPOIS": d, "WORKER": todas}, open("C:/cur/ciclo-voltas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
