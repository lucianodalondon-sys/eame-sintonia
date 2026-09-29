#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O FUNIL DA R9 — onde o caminho automatico perde os itens (D156). So MEDE; nao muda nada.

    py provas/l2/funil_r9.py [--r9=<pasta intelligence-experimental>]  ->  provas/l2/FUNIL-R9.json

Sobre os bytes exatos da Sala da R9 (sha conferido), corre o caminho oficial do gatilho (cortar_vigente ->
motor_das_capacidades.rodar -> montar_o_pote -> validar_pote_v2) e conta, portao a portao, quantos itens passam:
G0 (livro da corrida), triagem estudo/nao-estudo (e_estudo), CAP-WIN (janelas / NOT_POSSIBLE e porque), CAP-SCI,
objetos do motor, NAO_ENVIADOS_AO_POTE e porque, pote (RECUSADOS e porque) e fiscal. E segue item a item os que o
ORACULO (PARA-O-CASCO-R9, so lido) liberou: pela PROVA de cada objeto liberado (ITEM_ID), sem nenhum ID fixo aqui.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve()
RAIZ = AQUI.parents[2]
for p in ("", "admissao", "motor"):
    sys.path.insert(0, str(RAIZ / p))
import _gavetas                            # noqa: E402,F401
import motor_das_capacidades as M          # noqa: E402
import gatilho_da_inteligencia as GI       # noqa: E402
sys.path.insert(0, str(AQUI.parent))
import r9_auto_vs_manual as R9             # noqa: E402

SAIDA = AQUI.parent / "FUNIL-R9.json"


def _curto(v, n=160):
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, default=str)
    return s[:n]


def export_da_r9(base: Path):
    run_dir = next(base.glob("EXPD78-R9-*"))
    copia = run_dir / "copia" / "SALA_ATUAL.json"
    ro = (run_dir / "copia" / "PROVA_RO.txt").read_text(encoding="utf-8").split()
    linhas = json.loads(copia.read_text(encoding="utf-8"))
    return {"EXPORT": M.EXPORT_DA_SALA, "SINTETICO": False, "CORTE": ro[1] + "T" + ro[2],
            "ORIGEM": "copia so-leitura da R9 · sha256 %s" % R9.sha(copia), "READ_ONLY": ro[0], "LINHAS": linhas,
            "POUSOS_DA_COPIA": [{"run_id": l["run_id"], "ordem": l["ordem"], "item_id": l["item_id"],
                                 "pousado_em": l.get("pousado_em")} for l in linhas]}


def itens_do_oraculo(base: Path) -> list:
    pc = json.loads((base / "PARA-O-CASCO-R9" / "POTE-R9-PARA_CLIENTE.json").read_text(encoding="utf-8"))
    return sorted({p["ITEM_ID"] for e in pc["COMPARTIMENTOS"].values() for o in e["OBJETOS"]
                   if o.get("LIBERACAO") == "LIBERADO_PARA_CLIENTE" for p in o["PROVA"]})


def funil(saida: dict, n_corte: int) -> dict:
    livro = saida["CORRIDA"]
    lin = livro["LINEAGE"]
    g0 = Counter(str(l.get("G0") or l.get("G0_RESULT") or l.get("RESULTADO_G0") or "?") for l in lin)
    tri = Counter(v["CAPACIDADE"] for v in saida["TRIAGEM"].values())
    win, sci = saida["CAP_WIN"], saida["CAP_SCI"]
    np_ = Counter(_curto(x.get("REASON") or x.get("PORQUE") or x.get("MOTIVO"), 90) for x in win.get("NOT_POSSIBLE") or [])
    nao = Counter(x.get("MOTIVO") for x in saida.get("NAO_ENVIADOS_AO_POTE") or [])
    return {"ITENS_NO_CORTE": n_corte, "LINEAGE": len(lin), "G0": dict(g0),
            "SINAIS_NO_LIVRO": len(livro.get("SIGNALS") or []),
            "FACTOS_SOBRE_O_FUTURO": len(livro.get("FUTURE_DATED_FACTS") or []),
            "TRIAGEM": dict(tri), "CAP_WIN_JANELAS": len(win.get("CROP_WINDOWS") or []),
            "CAP_WIN_NOT_POSSIBLE": sum(np_.values()), "CAP_WIN_NOT_POSSIBLE_PORQUE": dict(np_.most_common(8)),
            "CAP_SCI_ESTUDOS": len(sci.get("ESTUDOS") or []),
            "OBJETOS": {k: len(v) for k, v in saida["ITENS_POR_FERRAMENTA"].items()},
            "NAO_ENVIADOS_AO_POTE": dict(nao)}


def seguir(saida: dict, iid: str) -> dict:
    livro = saida["CORRIDA"]
    return {
        "LINEAGE": [{k: _curto(v) for k, v in l.items()} for l in livro["LINEAGE"] if str(l.get("ITEM_ID")) == iid],
        "SINAIS": [{k: _curto(v) for k, v in s.items()} for s in livro.get("SIGNALS") or [] if s.get("ITEM_ID") == iid],
        "TRIAGEM": saida["TRIAGEM"].get(iid),
        "D112_LUGAR": saida["D112"]["LUGAR"].get(iid),
        "CAP_WIN_NOT_POSSIBLE": [{k: _curto(v) for k, v in x.items()} for x in saida["CAP_WIN"].get("NOT_POSSIBLE") or []
                                 if x.get("ITEM_ID") == iid],
        "CAP_WIN_JANELAS": [j.get("CROP_WINDOW_ID") for j in saida["CAP_WIN"].get("CROP_WINDOWS") or []
                            if iid in json.dumps(j, ensure_ascii=False)],
        "OBJETOS": [(c, o.get("OBJETO_ID"), o.get("ESPECIE_DO_POTE") or o.get("ESPECIE"))
                    for c, v in saida["ITENS_POR_FERRAMENTA"].items() for o in v
                    if iid in json.dumps(o.get("PROVA") or [], ensure_ascii=False)],
        "NAO_ENVIADOS": [x for x in saida.get("NAO_ENVIADOS_AO_POTE") or [] if iid in json.dumps(x, ensure_ascii=False)]}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    base = Path(next((a.split("=", 1)[1] for a in argv if a.startswith("--r9=")), R9.R9_PADRAO))
    limpo, corte = GI.cortar_vigente(export_da_r9(base))
    saida = M.rodar(M.entrada_do_export(limpo), R9.HOJE, "L2-FUNIL")
    pote, conv = GI.montar_o_pote(saida)
    viol = GI.VP.validar(pote)
    out = {"FUNIL": funil(saida, corte["LINHAS_NO_CORTE"]),
           "POTE": {"OBJETOS": {c: len(e["OBJETOS"]) for c, e in pote["COMPARTIMENTOS"].items() if e["OBJETOS"]},
                    "RECUSADOS": dict(Counter(r.get("MOTIVO") for r in pote.get("RECUSADOS") or [])),
                    "ENTITY_SOURCE_CONVERTIDOS": conv, "VIOLACOES": len(viol),
                    "VIOLACOES_POR_TIPO": dict(Counter(v.split(": ", 2)[-1] for v in viol))},
           "ITENS_DO_ORACULO": {}}
    for iid in itens_do_oraculo(base):
        out["ITENS_DO_ORACULO"][iid] = seguir(saida, iid)
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:9000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
