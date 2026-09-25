#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REGUAS-T4-T5-T9 · o que se mede quando o gabarito diz NAO PRONTO (protocolo, regra 2).

    py scripts/regua_t4t5t9/medir.py

Sem rede, sem tocar no vivo nem na Sala. Duas medicoes:
  A · a regua ANTIGA de T4/T5/T9 (admissao/admissao.py, sem mudanca) contra os 167 rotulos do gabarito;
      so os textos rotulados sao abertos (a prova cega fica selada).
  B · o REROUTE com cada conjunto de destinos, contra os rotulos humanos SINTONIA_RELEVANT
      (scripts/regua_t2/GABARITO-T2-V1.json), a partir de ferramentas/reroute/MEDICAO-REROUTE-V1.json.
      Recalcular desse ficheiro e valido porque nenhuma regua mudou: os destinos de cada texto sao os mesmos,
      e desligar um universo como destino so tira esse universo da lista.
"""
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).parent
sys.path[:0] = [str(RAIZ / "admissao"), str(RAIZ)]
import admissao as A  # noqa: E402

TEXTOS = Path.home() / "sintonia-gabarito" / "REGUA-T4T5T9-V1" / "textos"
UNIVERSOS = ("T4", "T5", "T9")


def _pr(tp, fp, fn):
    return {"TP": tp, "FP": fp, "FN": fn,
            "PRECISAO": round(tp / (tp + fp), 3) if tp + fp else None,
            "RECALL": round(tp / (tp + fn), 3) if tp + fn else None}


def regua_antiga():
    rot = json.loads((AQUI / "rotulos" / "rotulos-gabarito.json").read_text(encoding="utf-8"))
    out = {}
    for u in UNIVERSOS:
        m = Counter()
        for x in rot:
            t = (TEXTOS / (x["ID"] + ".txt")).read_text(encoding="utf-8")
            r, _mot, _ev = A._do_universo({"texto": t}, u, A.PERGUNTAS_DO_UNIVERSO.get(u, []))
            m["%s->%s" % (x[u], r)] += 1
        tp, fp, fn = m["YES->SIM"], m["NO->SIM"], sum(v for k, v in m.items() if k.startswith("YES->") and k != "YES->SIM")
        out[u] = dict(_pr(tp, fp, fn), MATRIZ=dict(sorted(m.items())))
    return len(rot), out


def reroute():
    med = json.loads((RAIZ / "ferramentas" / "reroute" / "MEDICAO-REROUTE-V1.json").read_text(encoding="utf-8"))
    total = med["CONTRA_O_HUMANO_V1"]
    todos = sorted({d[0] for r in med["REROUTES"] for d in r["DESTINOS"]})
    variantes = {"TODOS (hoje)": set(todos), "SEM T4/T5/T9": set(todos) - set(UNIVERSOS)}
    for u in UNIVERSOS:
        variantes["SEM %s" % u] = set(todos) - {u}
    variantes["SO T1/T2 (reguas medidas)"] = {"T1", "T2"}
    out = {}
    for nome, dest in variantes.items():
        acesos = Counter()
        for r in med["REROUTES"]:
            h = (r.get("HUMANO") or {}).get("SINTONIA_RELEVANT")
            if h and any(d[0] in dest for d in r["DESTINOS"]):
                acesos[h] += 1
        yes_total = total.get("humano YES · reroute SIM", 0) + total.get("humano YES · reroute NAO", 0)
        tp, fp = acesos["YES"], acesos["NO"]
        out[nome] = dict(_pr(tp, fp, yes_total - tp), DESTINOS=sorted(dest), ACESOS_NAO_SEI=acesos["NAO_SEI"],
                         ACESOS_TOTAL_NO_CORPUS=sum(1 for r in med["REROUTES"]
                                                    if any(d[0] in dest for d in r["DESTINOS"])))
    return out


def main():
    n, antiga = regua_antiga()
    out = {"DATASET": "MEDICAO-REGUAS-T4T5T9-V1", "MEDIDO_DENTRO_DA_AMOSTRA": True,
           "A_REGUA_ANTIGA_NO_GABARITO": {"ROTULOS": n, "POR_UNIVERSO": antiga},
           "B_REROUTE_POR_DESTINOS": reroute(),
           "ALVO": {"T1": 0.981, "T2": 0.953, "FONTE": "scripts/regua_t1/MEDICAO-REGUA-T1-V1.json, "
                                                     "scripts/regua_t2/MEDICAO-REGUA-T2-V3.json"}}
    (AQUI / "MEDICAO-REGUAS-T4T5T9-V1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                                       encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
