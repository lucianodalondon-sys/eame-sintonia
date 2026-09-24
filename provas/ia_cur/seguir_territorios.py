"""IA-CUR: as decisoes de territorio do agente seguem pelo ciclo deterministico COM REDE
(QUALIFY -> BUILD_CONTRACT -> VALIDATE_ROUTE -> CANARY -> regua), tarefa a tarefa pelo worker.
uso: py seguir_territorios.py <raiz da copia>"""
import json, os, sys
RAIZ = sys.argv[1]
os.chdir(RAIZ); sys.path.insert(0, RAIZ + "/curadoria")
import worker as W, fila as F, lifecycle as LC   # noqa: E402

ALVO = ["CAND-0503", "CAND-0575", "CAND-0577", "CAND-0579", "CAND-0580", "CAND-0515", "CAND-0527", "CAND-0582"]
for c in ALVO:
    F.enfileirar(c, F.QUALIFY, priority=90, motivo="IA-CUR: decisao do agente pela porta semantica")
for rodada in range(6):
    alo = {n.get("CANDIDATE_ID"): n["SOURCE_ID"] for n in json.load(open(W.ALLOCATION, encoding="utf-8"))["NOVAS"]}
    ids = set(ALVO) | {alo[c] for c in ALVO if c in alo}
    ab = [t for t in F._ler()["TAREFAS"] if t["SOURCE_ID"] in ids and t["STATUS"] == F.PENDING]
    if not ab:
        break
    for t in ab:
        r = W.executar_uma(t, W._contratos())
        print(rodada, t["SOURCE_ID"], t["TASK_TYPE"], r["RESULTADO"], (r.get("PORQUE") or "")[:110], flush=True)
alo = {n.get("CANDIDATE_ID"): n["SOURCE_ID"] for n in json.load(open(W.ALLOCATION, encoding="utf-8"))["NOVAS"]}
print("---")
for c in ALVO:
    s = alo.get(c)
    print(c, "->", s, "|", LC.estado_de(s) if s else LC.estado_de(c))
