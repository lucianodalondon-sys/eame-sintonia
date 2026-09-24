# -*- coding: utf-8 -*-
"""REND · prova (a): conferencia INDEPENDENTE da 1.a onda (BC5) na Sala real, SO LEITURA.

Nao le o relatorio da BC5 para decidir nada: le so a lista de RUN_ID dele e
pergunta ao banco e ao disco.
  1. sala_de_espera com run_id da onda           (esperado 3: 66 -> 69)
  2. raw_asset com run_id da onda                (esperado 9 documentos + 1 registo de falha)
  3. derived_artifact desses raw_asset           (esperado 9)
  4. cada raw/derived tem storage_object, o ficheiro existe no armazem e o sha256
     do FICHEIRO e o sha256 registado
  5. o pais de cada corrida: collection_run.source_country, o RUN_ID, e o
     VPN_COUNTRY que o coletor gravou no runs.ndjson do bot

Uso: py ferramentas/rendimento/conferir_1a_onda.py --bot <arvore do bot> --saida X.json
"""
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sala_por_fonte import psql  # noqa: E402

AQUI = Path(__file__).resolve().parent
ARMAZEM = Path(os.environ.get("SINTONIA_ARMAZEM_RAIZ") or Path.home() / "sintonia-sala-italia" / "armazem")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def conferir_objeto(caminho, sha_reg):
    p = ARMAZEM / caminho
    if not p.exists():
        return {"EXISTE": False, "IGUAL": False}
    s = sha(p)
    return {"EXISTE": True, "IGUAL": s == sha_reg, "SHA256_FICHEIRO": s}


def main(argv):
    bot = Path(argv[argv.index("--bot") + 1])
    bc5 = json.loads((AQUI.parent / "big_collection" / "BC5-BIG-COLLECTION-1A-ONDA.json").read_text(encoding="utf-8"))
    runs = [f["RUN_ID"] for f in bc5["FONTES"] if f.get("RUN_ID")]
    lista = ",".join("'%s'" % r.replace("'", "") for r in runs)

    sala = psql("select run_id, source_id, universo, item_id, pousado_em::text from sala_de_espera where run_id in (%s) order by pousado_em" % lista)
    raws = psql("select r.id, r.run_id, r.source_id, r.source_url, r.media_type, r.sha256, s.storage_path, s.sha256 "
                "from raw_asset r left join storage_object s on s.id = r.storage_object_id where r.run_id in (%s) order by r.id" % lista)
    ders = psql("select d.id, d.raw_asset_id, d.kind, d.sha256, d.storage_path from derived_artifact d "
                "join raw_asset r on r.id = d.raw_asset_id where r.run_id in (%s) order by d.id" % lista)
    cr = psql("select run_id, coalesce(source_country::text,'(nulo)'), status from collection_run where run_id in (%s) order by run_id" % lista)
    total = psql("select (select count(*) from sala_de_espera), (select count(*) from raw_asset), (select count(*) from derived_artifact)")[0]

    raw_out = []
    for i, run, src, url, mt, sha_raw, sp, sha_so in raws:
        o = {"RAW_ID": int(i), "RUN_ID": run, "SOURCE_ID": src, "SOURCE_URL": url, "MEDIA_TYPE": mt,
             "STORAGE_PATH": sp or None, "SHA256_RAW_IGUAL_STORAGE": bool(sp) and sha_raw == sha_so}
        o.update(conferir_objeto(sp, sha_so) if sp else {"EXISTE": False, "IGUAL": False})
        o["REGISTO_DE_FALHA"] = "/OBSERVATION/" in (sp or "") and mt == "application/json"
        raw_out.append(o)
    der_out = []
    for i, rid, kind, s, sp in ders:
        o = {"DERIVED_ID": int(i), "RAW_ID": int(rid), "KIND": kind, "STORAGE_PATH": sp or None}
        o.update(conferir_objeto(sp, s) if sp else {"EXISTE": False, "IGUAL": False})
        der_out.append(o)

    vpn = {}
    for l in (bot / "data" / "collection-ledger" / "italy" / "runs.ndjson").read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(l)
        except ValueError:
            continue
        if d.get("RUN_ID") in runs:
            vpn[d["RUN_ID"]] = d.get("VPN_COUNTRY")

    docs = [r for r in raw_out if not r["REGISTO_DE_FALHA"]]
    d = {"DATASET": "REND-CONFERENCIA-1A-ONDA-V1", "MODO": "so leitura (banco read-only; armazem so lido)",
         "ARMAZEM": str(ARMAZEM), "RUNS_DA_ONDA": len(runs),
         "SALA_TOTAL_AGORA": {"sala_de_espera": int(total[0]), "raw_asset": int(total[1]), "derived_artifact": int(total[2])},
         "RESPOSTAS": {
             "SALA_LINHAS_DA_ONDA": len(sala),
             "RAW_DOCUMENTOS": len(docs), "RAW_REGISTOS_DE_FALHA": len(raw_out) - len(docs),
             "DERIVED": len(der_out),
             "RAW_COM_FICHEIRO_E_SHA_IGUAL": sum(r["EXISTE"] and r["IGUAL"] and r["SHA256_RAW_IGUAL_STORAGE"] for r in raw_out),
             "DERIVED_COM_FICHEIRO_E_SHA_IGUAL": sum(x["EXISTE"] and x["IGUAL"] for x in der_out),
             "COLLECTION_RUN_SOURCE_COUNTRY": sorted({c[1] for c in cr}),
             "RUN_ID_COM_PREFIXO_IT": sum(r.startswith("IT-") for r in runs),
             "VPN_COUNTRY_NO_LIVRO": {k: sum(1 for v in vpn.values() if v == k) for k in set(vpn.values())},
             "RUNS_SEM_LINHA_NO_LIVRO": [r for r in runs if r not in vpn]},
         "SALA": [dict(zip(("RUN_ID", "SOURCE_ID", "UNIVERSO", "ITEM_ID", "POUSADO_EM"), x)) for x in sala],
         "RAW": raw_out, "DERIVED": der_out,
         "COLLECTION_RUN": [dict(zip(("RUN_ID", "SOURCE_COUNTRY", "STATUS"), c)) for c in cr]}
    Path(argv[argv.index("--saida") + 1]).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(d["RESPOSTAS"], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
