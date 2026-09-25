# HR-6 · RONDA A — o reparo da R1 so INFERE (nao escreve), 1 fonte por dominio.
import json, sys, time
sys.path.insert(0, "curadoria")
import reparar_contrato as RC, collection_gate as G, lifecycle as LC

ids = sys.argv[1].split(",")
saida = sys.argv[2]
livro = json.load(open("curadoria/italy_contracts_curator.json", encoding="utf-8"))
C = {c["SOURCE_ID"]: c for c in livro["FONTES"]}
est = LC.snapshot()
out = []
for sid in ids:
    outros = {k: v for k, v in C.items() if k != sid and
              (est.get(k) == LC.READY_FOR_COLLECTION or v.get("REPARO_DE_CONTRATO"))}
    t0 = time.time()
    p = RC.inferir(C[sid], outros=outros)
    item = p.get("ITEM_LIDO") or {}
    url = item.get("URL") if isinstance(item, dict) else item
    p["_HR_SOBRE_O_ITEM_LIDO"] = G.revisao_humana_do_url(url or "") if url else "SEM_ITEM"
    p["_SOURCE_ID"] = sid
    p["_SEGUNDOS"] = round(time.time() - t0, 1)
    out.append(p)
    print(sid, p["DESFECHO"], p.get("MOTIVO"), "| pedidos", p.get("PEDIDOS"),
          "| item", url, "| HR:", p["_HR_SOBRE_O_ITEM_LIDO"])
    print("    padrao", p.get("INDEX_URL"), p.get("LINK_PATTERN"))
    print("    porque", str(p.get("PORQUE"))[:300])
json.dump(out, open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
