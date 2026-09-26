"""Monta, numa COPIA da producao, o envelope de uma corrida social a partir de um envelope REAL de 24/09.

O que e real: a observacao da plataforma (post, video, legenda, JSON-LD) e os bytes em data/raw/LINKEDIN.
O que se refaz com o CODIGO DE PRODUCAO: os campos que o adaptador de hoje acrescenta ao objeto
(PUBLISHED_AT_SOURCE/PRECISION, os tres campos de politica D37) e a unidade inteira (scrap_colheita.unidade),
com o SOURCE_ID que o robo de fontes cunhou nesta copia. Nada vai a rede.
"""
import json
import os
import secrets
import sys
from datetime import datetime, timezone

E = os.environ.get("ENS", r"C:\ens-sr")
os.chdir(E)
for p in ("coleta", "leis", "regras", "curadoria", ""):
    sys.path.insert(0, os.path.join(E, p) if p else E)
import adaptador_linkedin as LI      # noqa: E402
import scrap_colheita as SC          # noqa: E402

VELHO = os.environ.get("VELHO", r"C:\soc2\copia\data\colheita\scrap\IT-T2-2026-09-24-135639-e71207d057344cdc\ENVELOPE.json")
SID, TERR = sys.argv[1], sys.argv[2]
env = json.load(open(VELHO, encoding="utf-8"))
run_id = "IT-%s-%s-%s" % (TERR, datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S"), secrets.token_hex(8))
itens = []
for it in env["COLHEITA"]:
    ob = dict(it["OBSERVACAO"])
    raw = ob.get("RAW") or {}
    # o que o adaptador de HOJE escreve no objeto (coleta/adaptador_linkedin.py, _adquirir_um)
    ob.update(LI.politica_do_objeto(ob.get("DECISAO_DO_DONO") or LI.DECISAO_DO_DONO))
    if ob.get("PUBLISHED_AT"):
        ob["PUBLISHED_AT_SOURCE"] = "PLATAFORMA — LinkedIn, pagina publica do post, %s" % raw.get("PUBLISHED_AT_SOURCE")
    ob["PUBLISHED_AT_PRECISION"] = LI.precisao_da_publicacao(ob.get("PUBLISHED_AT"))
    ob["RUN_ID"] = run_id
    itens.append(SC.unidade(ob, run_id=run_id, fonte=SID))
novo = dict(env, RUN_ID=run_id, SOURCE_ID_DO_PEDIDO=SID, COLHEITA=itens)
pasta = os.path.join(E, "data", "colheita", "scrap", run_id)
os.makedirs(pasta, exist_ok=True)
json.dump(novo, open(os.path.join(pasta, "ENVELOPE.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(run_id)
u = itens[0]
print(json.dumps({k: u.get(k) for k in ("SOURCE_ID", "PUBLISHED_AT", "PUBLISHED_AT_BASIS", "PUBLISHED_AT_PRECISION",
                                        "SOURCE_LOCATION", "SOURCE_LOCATION_PRECISION", "SOURCE_LOCATION_BASIS",
                                        "DOCUMENT_ID")}, ensure_ascii=False, indent=1))
