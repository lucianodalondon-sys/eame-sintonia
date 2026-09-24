"""D29: quantas fontes de JANELA DE CULTURA ha no livro, e em que estado (so leitura)."""
import json, re, sys, collections
RAIZ = sys.argv[1]
sys.path.insert(0, RAIZ + "/curadoria")
J = lambda p, k: json.load(open(RAIZ + "/" + p, encoding="utf-8"))[k]
lv = J("curadoria/LIFECYCLE-LEDGER-V1.json", "TRANSICOES")
est = {}
for t in lv:
    est[t["SOURCE_ID"]] = t["NEW_STATE"]
con = {c["SOURCE_ID"]: c for c in J("curadoria/italy_contracts_curator.json", "FONTES")}
tab = {c["SOURCE_ID"]: c for c in J("regras/italy_contracts_onboarded.json", "FONTES")}
alo = {c["SOURCE_ID"]: c for c in J("curadoria/SOURCE-ID-ALLOCATION-V1.json", "NOVAS")}
PAL = re.compile(r"agrometeo|agro-meteo|agrometeorolog|fitosanitar|fitopatolog|condifesa|"
                 r"consorzi[oi] di difesa|difesa integrata|difesa fitosanitaria|lotta (integrata|guidata)|"
                 r"produzione integrata|bollettin[oi][ _/-]*(agro|fito|olivicol|viticol|frutticol|colture|"
                 r"difesa|di difesa|fitosanitar)|avvisi?[ _/-]*(fitosanitar|di difesa|colturali)|"
                 r"allerta fitosanitaria", re.I)
def texto(s):
    c = con.get(s) or tab.get(s) or alo.get(s) or {}
    aq = c.get("ACQUISITION") or {}
    return " ".join(str(x) for x in (c.get("NAME"), c.get("NOME"), c.get("OWNER"), aq.get("INDEX_URL"),
                                     c.get("CANONICAL_ENTRY_URL"), c.get("URL")))
def janela(s):
    m = re.match(r"IT-T(\d+)-", s)
    t = int(m.group(1)) if m else None
    return t == 3 or bool(PAL.search(texto(s)))
js = sorted(s for s in est if janela(s))
print("JANELA no livro:", len(js), "de", len(est))
print("  por territorio:", collections.Counter(s.split("-")[1] for s in js).most_common())
print("  por estado:", collections.Counter(est[s] for s in js).most_common())
if len(sys.argv) > 2:
    import collection_gate as CG
    import os; os.chdir(RAIZ)
    inv = {l["SOURCE_ID"]: l for l in CG.inventario()}
    print("  READY_CURRENT:", sum(1 for s in js if inv.get(s, {}).get("STATE") == "READY_FOR_COLLECTION"
                                  and inv[s]["READY_RULE"] != "LEGACY"),
          "| elegiveis no portao:", sum(1 for s in js if inv.get(s, {}).get("COLLECTION_ELIGIBLE")))
json.dump(js, open("C:/cur/JANELA-%s.json" % RAIZ.replace(":", "").replace("/", "_"), "w"), indent=0)
