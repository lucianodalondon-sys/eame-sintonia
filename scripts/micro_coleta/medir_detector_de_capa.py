"""O detector CAPA != MATERIA, medido nos dois sentidos — SEM o alterar.

SO LE: SELECT (pela trava do micro_coleta.sql), bytes do armazem, o contrato
do Curator, e o NEGATIVE_CONTROL da M3 por `git show`. Nao chama rede.

    py scripts/micro_coleta/medir_detector_de_capa.py [--armazem=<raiz>]

Dois conjuntos com veredito humano conhecido:
  MATERIAS  os 76 do lote-76 (corrida 0a8a01...): noticias individuais, lidas
            (RELATORIO-DIAGNOSTICO-SALA + RELATORIO-MICRO-PREP). Bytes brutos.
  CAPAS     as paginas de indice (INDEX_URL) que a M3 retratou como controlo
            negativo. SO O RETRATO: os bytes nao estao guardados.

E a PROPOSTA (nao aplicada): a MORADA antes da estrutura —
  morada que nao casa o LINK_PATTERN do contrato, ou e o INDEX_URL -> CAPA;
  morada de detalhe -> a estrutura so pode dizer MATERIA ou NAO_SEI
  (NAVIGATION numa morada de detalhe vira NAO_SEI: uma pessoa le).
"""
import ast
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import micro_coleta as MC  # noqa: E402

CORRIDA = "XX-T10-2026-09-22-193411-0a8a01dbc999da85"
KIND = {"NAVIGATION": "CAPA_PROVAVEL", "CONTENT": "MATERIA_PROVAVEL"}


def proposta(url: str, hoje: str, aq: dict) -> str:
    detalhe = bool(re.match(aq["LINK_PATTERN"], url))
    indice = url.rstrip("/") == str(aq.get("INDEX_URL", "")).rstrip("/")
    if not detalhe or indice:
        return "CAPA_PROVAVEL"
    return "NAO_SEI" if hoje == "CAPA_PROVAVEL" else hoje


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    armazem = next((Path(a.split("=", 1)[1]) for a in argv if a.startswith("--armazem=")),
                   MC._armazem())
    contratos = {f["SOURCE_ID"]: f["ACQUISITION"] for f in json.loads(
        (MC.RAIZ / "curadoria" / "italy_contracts_curator.json").read_text(encoding="utf-8"))["FONTES"]}

    mat = {"HOJE": Counter(), "PROPOSTA": Counter(), "N": 0, "SEM_BYTES": 0,
           "CASA_LINK_PATTERN": 0, "CAPA_HOJE": []}
    for rid, sid, url, sp in MC.sql(
            "select r.id, r.source_id, r.source_url, r.storage_path from raw_asset r"
            f" where r.run_id = '{CORRIDA}' order by r.id"):
        f = armazem / sp
        if not f.exists():
            mat["SEM_BYTES"] += 1
            continue
        mat["N"] += 1
        hoje = MC.RETRATO.retrato_do_html(f.read_bytes())["CAPA_OU_MATERIA"]
        aq = contratos[sid]
        mat["CASA_LINK_PATTERN"] += bool(re.match(aq["LINK_PATTERN"], url))
        mat["HOJE"][hoje] += 1
        mat["PROPOSTA"][proposta(url, hoje, aq)] += 1
        if hoje == "CAPA_PROVAVEL":
            mat["CAPA_HOJE"].append(rid)

    txt, h = MC.git_show(MC.FILTROS[0]["REF"], MC.FILTROS[0]["DADOS"])
    cap = {"HOJE": Counter(), "PROPOSTA": Counter(), "N": 0, "M3_HASH": h, "LINHAS": []}
    for l in json.loads(txt)["LINHAS"]:
        nc = l.get("NEGATIVE_CONTROL")
        if isinstance(nc, str):
            nc = ast.literal_eval(nc)
        if not nc:
            continue
        cap["N"] += 1
        hoje = KIND.get(nc["HTML_KIND"], "NAO_SEI")
        novo = proposta(nc["URL"], hoje, contratos[l["SOURCE_ID"]])
        cap["HOJE"][hoje] += 1
        cap["PROPOSTA"][novo] += 1
        cap["LINHAS"].append((l["SOURCE_ID"], nc["URL"], nc["HTML_KIND"], hoje, novo))

    out = {
        "MATERIAS": {**mat, "HOJE": dict(mat["HOJE"]), "PROPOSTA": dict(mat["PROPOSTA"])},
        "CAPAS": {**cap, "HOJE": dict(cap["HOJE"]), "PROPOSTA": dict(cap["PROPOSTA"])},
        "FALSE_CAPA_HOJE": f"{mat['HOJE'].get('CAPA_PROVAVEL', 0)}/{mat['N']}",
        "FALSE_MATERIA_HOJE": f"{cap['HOJE'].get('MATERIA_PROVAVEL', 0)}/{cap['N']}",
        "CAPA_QUE_ATRAVESSA_O_PORTAO_HOJE":
            f"{cap['N'] - cap['HOJE'].get('CAPA_PROVAVEL', 0)}/{cap['N']}",
        "FALSE_CAPA_PROPOSTA": f"{mat['PROPOSTA'].get('CAPA_PROVAVEL', 0)}/{mat['N']}",
        "CAPA_APANHADA_PROPOSTA": f"{cap['PROPOSTA'].get('CAPA_PROVAVEL', 0)}/{cap['N']}",
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
