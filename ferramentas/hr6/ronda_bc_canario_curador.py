# HR-6 · RONDA B — o canario CANONICO do curador (canario.canario_html), so leitura.
# Mesma funcao que o worker usa na etapa CANARY; nada e gravado no livro.
import json, sys, re
sys.path.insert(0, "curadoria")
import canario as CAN, collection_gate as G, ready_split as RS, gate_de_rota as GR
from urllib.parse import urlparse

ids = sys.argv[1].split(",")
saida = sys.argv[2]
C = RS._contratos()
out = []
for sid in ids:
    c = C[sid]
    idx = c["ACQUISITION"]["INDEX_URL"]
    rp, origem = GR.robots_de(urlparse(idx).hostname)
    if not GR.permitido(idx, rp):
        r = {"PASS": False, "CLASSE": "ROBOTS", "PORQUE": "robots proibe a entrada (%s)" % str(origem)[:80]}
    else:
        r = CAN.canario_html(c)
    r["_ROBOTS"] = str(origem)[:120]
    item = (r.get("ITEM_ABERTO") or {}).get("URL") or r.get("ALVO")
    # quais alvos o padrao casa hoje (sem novo pedido: reconta sobre a entrada ja lida? nao ha
    # cache — o canario so devolve o numero). Registamos o que ele devolve.
    r["_SOURCE_ID"] = sid
    r["_HR_SOBRE_O_ITEM"] = G.revisao_humana_do_url(item or "") if item else "SEM_ITEM"
    out.append(r)
    ia = r.get("ITEM_ABERTO") or {}
    print(sid, "PASS" if r.get("PASS") else "FAIL", r.get("CLASSE"), "| alvos", r.get("ALVOS_DESCOBERTOS"),
          "| item", item, ia.get("HTML_KIND"), ia.get("CAPA_OU_MATERIA"), ia.get("PARAGRAPH_CHARACTERS"))
    print("    HR:", r["_HR_SOBRE_O_ITEM"], "| porque:", str(r.get("PORQUE", ""))[:200])
json.dump(out, open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
