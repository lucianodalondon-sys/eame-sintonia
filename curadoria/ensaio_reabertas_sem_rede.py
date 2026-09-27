# MICRO-PROVA LOTE 1: as QUALIFY reabertas fora do lote voltam a bloquear SEM rede (correr numa copia, depois do ensaio).
import json, sys
from pathlib import Path
R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / "curadoria"))
import urllib.request
tentativas = []
def proibido(req, *a, **k):
    tentativas.append(getattr(req, "full_url", req)); raise OSError("rede proibida no ensaio")
urllib.request.urlopen = proibido
import fila as F, worker as W
from collections import Counter
lote = set(json.loads((R / "curadoria" / "MICRO-PROVA-LOTE1.json").read_text(encoding="utf-8"))["CANDIDATAS"])
pend = [t for t in F._ler()["TAREFAS"] if t["STATUS"] == F.PENDING and t["TASK_TYPE"] == F.QUALIFY and t["SOURCE_ID"] not in lote]
res = Counter()
for t in pend:
    r = W.executar_uma(t, W._contratos())
    res[(r.get("RESULTADO"))] += 1
print(json.dumps({"QUALIFY_REABERTAS_FORA_DO_LOTE": len(pend), "RESULTADOS": dict(res), "TENTATIVAS_DE_REDE": len(tentativas),
                  "AINDA_PENDING": sum(1 for t in F._ler()["TAREFAS"] if t["STATUS"] == F.PENDING and t["TASK_TYPE"] == F.QUALIFY)}))
