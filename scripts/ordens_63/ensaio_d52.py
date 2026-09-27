# -*- coding: utf-8 -*-
"""ORDENS-63 v2 · ensaio da D52 numa COPIA do livro vivo, com a rede fechada (proxy para 127.0.0.1:9).

    py scripts/ordens_63/ensaio_d52.py <pasta-da-copia>

Copia do vivo (so leitura) o livro do curador, a fila e o livro de estados; aplica a D52 na copia pela
porta (`retirar_por_decisao.py --escrever`), mede o gatilho antes e depois, repete (idempotente) e
reverte (sha256 igual ao original). Escreve ENSAIO-D52-V1.json ao lado.
"""
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
    os.environ[k] = "http://127.0.0.1:9"
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import retirar_por_decisao as R   # noqa: E402
import gatilho_discovery as G     # noqa: E402

VIVO = Path(r"C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/curadoria")
d = Path(sys.argv[1])
d.mkdir(parents=True, exist_ok=True)
for f in ("italy_contracts_curator.json", "LIFECYCLE-QUEUE-V1.json", "LIFECYCLE-LEDGER-V1.json"):
    shutil.copyfile(VIVO / f, d / f)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()   # noqa: E731
livro = d / "italy_contracts_curator.json"
h0 = sha(livro)
dec = R.ler_decisao("D52")
as62 = {f["SOURCE_ID"] for f in dec["FONTES"]}
agora = datetime.now(timezone.utc)
estados = {}
for t in json.loads((d / "LIFECYCLE-LEDGER-V1.json").read_text(encoding="utf-8"))["TRANSICOES"]:
    estados[t["SOURCE_ID"]] = t["NEW_STATE"]
tarefas = json.loads((d / "LIFECYCLE-QUEUE-V1.json").read_text(encoding="utf-8"))["TAREFAS"]
# o caso que a trava tem de travar: o ultimo reparo FALHOU ha mais de 24 h (hoje estao DONE)
simuladas = [dict(t, STATUS="FAILED", UPDATED_AT=(agora - timedelta(days=2)).isoformat())
             if t["TASK_TYPE"] == "REPAIR_CONTRACT" and t["SOURCE_ID"] in as62 else t for t in tarefas]


def ler():
    return {c["SOURCE_ID"]: c for c in json.loads(livro.read_text(encoding="utf-8"))["FONTES"]}


def gat(contratos, ts):
    return {x["SOURCE_ID"] for x in G.candidatas_a_reparar(agora, estados=estados, contratos=contratos, tarefas=ts)}


antes = ler()
conaf = sorted(s for s, c in antes.items() if "conaf.it" in ((c.get("ACQUISITION") or {}).get("INDEX_URL")
                                                          or c.get("CANONICAL_ENTRY_URL") or ""))
g_hoje, g_sim_antes = gat(antes, tarefas) & as62, gat(antes, simuladas) & as62
r1 = R.main(["--decisao", "D52", "--livro", str(livro), "--escrever"])
depois = ler()
h1 = sha(livro)
mudaram = sorted(s for s in antes if antes[s] != depois[s])
g_sim_depois = gat(depois, simuladas) & as62
r2 = R.main(["--decisao", "D52", "--livro", str(livro), "--escrever"])
h2 = sha(livro)
r3 = R.main(["--decisao", "D52", "--livro", str(livro), "--reverter", "--escrever"])
h3 = sha(livro)
out = {"DATASET": "ENSAIO-D52-V1", "EM": agora.isoformat(), "REDE": "fechada (proxy 127.0.0.1:9)",
       "COPIA": str(d), "LIVRO_SHA256": {"ORIGINAL": h0, "MARCADO": h1, "SEGUNDA_CORRIDA": h2, "REVERTIDO": h3},
       "FONTES_NO_LIVRO": len(antes), "MUDARAM": len(mudaram), "MUDARAM_SAO_AS_62": set(mudaram) == as62,
       "CONAF_NO_LIVRO": len(conaf), "CONAF_FORA_DAS_62": sorted(set(conaf) - as62),
       "CONAF_FORA_DAS_62_MUDOU": [s for s in set(conaf) - as62 if antes[s] != depois[s]],
       "GATILHO_HOJE_PROPOE_DAS_62": len(g_hoje),
       "GATILHO_COM_REPARO_FALHADO_SIMULADO": {"ANTES": len(g_sim_antes), "DEPOIS": len(g_sim_depois)},
       "IDEMPOTENTE": h1 == h2, "REVERTER_DEVOLVE_O_ORIGINAL": h3 == h0, "SAIDAS": [r1, r2, r3]}
(AQUI / "ENSAIO-D52-V1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in out.items() if k not in ("LIVRO_SHA256",)}, ensure_ascii=False, indent=1))
