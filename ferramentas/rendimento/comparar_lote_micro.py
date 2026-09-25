# -*- coding: utf-8 -*-
"""Previsao x resultado do MICRO, fonte a fonte, contra o LOTE-MICRO-V3 fixado. So leitura, sem rede.

    py ferramentas/rendimento/comparar_lote_micro.py --lote=ferramentas/rendimento/LOTE-MICRO-V3.json
        --estado=<ONDA-WEB-ESTADO.json ou BIG-COLLECTION-ESTADO.json da corrida>
        --runs=<data/collection-ledger/italy/runs.ndjson do bot>
        --decisoes=<data/samples/LIVRO-DE-DECISOES.json do bot>
        [--saida=...]

Liga tudo pelo RUN_ID de cada fonte:
  documentos novos = contadores.DETAIL_NEW da corrida (runs.ndjson);
  SIM / NAO / NAO_SEI = decisoes da Admissao com `corrida` = RUN_ID (LIVRO-DE-DECISOES).
Criterio D35 (o do lote): SIM / fontes que CORRERAM > 16,7 % E >= 2 SIM.
Fonte que nao correu = NAO_RODOU (com o motivo): nao conta como 0 SIM e sai do denominador.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

LIMIAR = 3 / 18                       # 16,7 % — 3 SIM em 18 fontes na 1.a onda
MINIMO_SIM = 2


def _runs(path: Path) -> dict:
    out = {}
    for l in path.read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(l)
        except ValueError:
            continue
        if d.get("RUN_ID"):
            out[d["RUN_ID"]] = d
    return out


def _decisoes(path: Path) -> list:
    d = json.loads(path.read_text(encoding="utf-8"))
    return d if isinstance(d, list) else next(v for v in d.values() if isinstance(v, list))


def comparar(lote: dict, estado: dict, runs: dict, decisoes: list) -> dict:
    corrida = {f["SOURCE_ID"]: f for f in estado.get("FONTES", [])}
    por_run = {}
    for x in decisoes:
        por_run.setdefault(x.get("corrida"), []).append(x.get("resultado"))
    linhas = []
    for e in lote["ESCOLHA"]:
        s = e["SOURCE_ID"]
        f = corrida.get(s)
        l = {"SOURCE_ID": s, "PREVISTO_DOCUMENTOS": e["PREVISAO_DOCUMENTOS_NOVOS"], "PREVISTO_SIM": e["PREVISAO_SIM"]}
        if not f or not f.get("CORREU") or not f.get("RUN_ID"):
            l.update(ESTADO="NAO_RODOU", PORQUE=(f or {}).get("PORQUE_NAO_CORREU") or "a fonte nao aparece na corrida")
        else:
            r = runs.get(f["RUN_ID"]) or {}
            c = r.get("contadores") or {}
            res = por_run.get(f["RUN_ID"], [])
            l.update(ESTADO="RODOU", RUN_ID=f["RUN_ID"], STATUS=f.get("STATUS"),
                     DOCUMENTOS_NOVOS=c.get("DETAIL_NEW") if r else "RUN_ID_FORA_DO_LIVRO",
                     SIM=res.count("SIM"), NAO=res.count("NAO"), NAO_SEI=res.count("NAO_SEI"),
                     RECUSAS_CORTESIA=c.get("COURTESY_REFUSALS"))
            ps = e["PREVISAO_SIM"]
            l["SIM_VS_PREVISTO"] = ("previsao NAO_SEI" if ps == "NAO_SEI" else
                                    "ACIMA" if l["SIM"] > ps else "ABAIXO" if l["SIM"] < ps else "IGUAL")
        linhas.append(l)
    rodaram = [l for l in linhas if l["ESTADO"] == "RODOU"]
    sim = sum(l["SIM"] for l in rodaram)
    taxa = sim / len(rodaram) if rodaram else None
    return {"LINHAS": linhas, "FONTES_QUE_CORRERAM": len(rodaram),
            "NAO_RODARAM": [l["SOURCE_ID"] for l in linhas if l["ESTADO"] == "NAO_RODOU"],
            "SIM_TOTAL": sim, "SIM_SO_DA_MYFRUIT": sum(l["SIM"] for l in rodaram if l["SOURCE_ID"] == "IT-T10-018"),
            "TAXA_D35": None if taxa is None else round(taxa, 4),
            "PASSA_D35": bool(rodaram) and taxa > LIMIAR and sim >= MINIMO_SIM,
            "LEITURA": "PASS = rendimento do sistema instalado (provavelmente sustentado pela myfruit); clima T2 = NAO PROVADO (D47)"}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    lb = Path(a["lote"]).read_bytes()
    r = comparar(json.loads(lb), json.loads(Path(a["estado"]).read_text(encoding="utf-8")),
                 _runs(Path(a["runs"])), _decisoes(Path(a["decisoes"])))
    r = {"DATASET": "COMPARACAO-LOTE-MICRO-V3", "LOTE_SHA256": hashlib.sha256(lb).hexdigest(), **r}
    s = json.dumps(r, ensure_ascii=False, indent=1) + "\n"
    if a.get("saida"):
        Path(a["saida"]).write_text(s, encoding="utf-8")
    print(s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
