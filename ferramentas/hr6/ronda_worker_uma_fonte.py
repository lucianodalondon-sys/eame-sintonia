# HR-6 · corre o worker SO nas tarefas de UMA fonte (fila filtrada, D41.3).
import json, sys
sys.path.insert(0, "curadoria")
import worker as W, fila as F, lifecycle as LC

sid = sys.argv[1]
for volta in range(4):
    abertas = [t for t in F._ler()["TAREFAS"] if t["SOURCE_ID"] == sid
               and t["STATUS"] in (F.PENDING, F.WAITING_RETRY)]
    if not abertas:
        break
    t = abertas[0]
    r = W.executar_uma(t, W._contratos())
    print(sid, t["TASK_ID"], t["TASK_TYPE"], "->", r.get("RESULTADO"), "|", str(r.get("PORQUE", ""))[:160],
          "| estado:", LC.estado_de(sid))
print("FINAL", sid, LC.estado_de(sid))
