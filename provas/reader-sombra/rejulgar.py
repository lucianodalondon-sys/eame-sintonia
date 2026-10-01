#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-julga uma rodada JA FEITA com o juiz atual, sem chamar o modelo de novo: a resposta crua do modelo
(VALOR_DO_MODELO, DATA_LITERAL, TRECHO, PAPEL_DA_DATA, PORQUE_DO_MODELO) fica igual; so o codigo do juiz muda.
    python provas/reader-sombra/rejulgar.py <SALA_ATUAL.json> <RODADA.json> <saida.json>"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "leis"))
import leitor_semantico as L  # noqa: E402


def main(a):
    S = json.load(open(a[0], encoding="utf-8"))
    r = json.load(open(a[1], encoding="utf-8"))
    for x in r["LEITURAS"]:
        f = x["FACT_TIME"]
        if str(f.get("JUIZ", "")).startswith("ERRO_DO_MECANISMO"):
            continue
        resp = {"VALOR": f.get("VALOR_DO_MODELO"), "DATA_LITERAL": f.get("DATA_LITERAL"), "TRECHO": f.get("TRECHO"),
                "PAPEL_DA_DATA": f.get("PAPEL_DA_DATA"), "PORQUE": f.get("PORQUE_DO_MODELO")}
        s = S[x["N"]]
        x["FACT_TIME"] = L.julgar(s["texto"] or "", resp, s.get("captured_at"))
        x["FACT_TIME"]["JUIZ_ANTERIOR"] = f.get("JUIZ")
    r["JUIZ_VERSAO"] = L.JUIZ_VERSAO
    r["REJULGADO_DE"] = a[1]
    Path(a[2]).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ACEITES", sum(1 for x in r["LEITURAS"] if x["FACT_TIME"].get("JUIZ") == "ACEITE"))


if __name__ == "__main__":
    main(sys.argv[1:])
