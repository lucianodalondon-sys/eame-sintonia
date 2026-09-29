#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R9 AUTOMATICO x MANUAL (D151/D152) — MEDIR, SEM CONSTRUIR.

    py provas/l2/r9_auto_vs_manual.py [--r9=<pasta intelligence-experimental>]  ->  provas/l2/R9-AUTO-VS-MANUAL.json

Corre o caminho OFICIAL automatico — o mesmo que o gatilho chama (admissao/gatilho_da_inteligencia.py):
cortar_vigente -> motor_das_capacidades.rodar -> montar_o_pote (gerador do dono + ENTITY_SOURCE da lei) ->
validar_pote_v2 — sobre EXATAMENTE os bytes da Sala que a R9 usou (EXPD78-R9-*/copia/SALA_ATUAL.json, conferido
pelo sha256 que a propria R9 registou no SHA256SUMS). Nao abre banco: a copia so-leitura JA E o export da R9
(PROVA_RO.txt = on no inicio e no fim). O envelope SALA_ATUAL_READ_ONLY/v1 que o motor pede e posto por
programa, com CORTE e READ_ONLY lidos do PROVA_RO.txt; nenhum dado e escrito a mao.

Compara com o ORACULO (PARA-O-CASCO-R9: POTE-R9-PARA_CLIENTE.json, MANIFESTO-R9.json, montar_r9.py). O oraculo
nao e etapa: so se le. Nada e escrito fora de provas/l2/.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve()
RAIZ = AQUI.parents[2]
for p in ("", "admissao", "motor"):
    sys.path.insert(0, str(RAIZ / p))
import _gavetas                            # noqa: E402,F401
import motor_das_capacidades as M          # noqa: E402
import gatilho_da_inteligencia as GI       # noqa: E402

R9_PADRAO = Path(r"C:/Users/London1/sintonia-sala-italia/intelligence-experimental")
HOJE = date(2026, 9, 28)                   # o dia da R9 (LIVRO START 2026-09-28T15:59:39+00:00)
SAIDA = AQUI.parent / "R9-AUTO-VS-MANUAL.json"
N38 = ("derived:11", "IT-T3-2026-09-20-110656-6e4ffc27a86c5269")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    base = Path(next((a.split("=", 1)[1] for a in argv if a.startswith("--r9=")), R9_PADRAO))
    run_dir = next(base.glob("EXPD78-R9-*"))
    oraculo = base / "PARA-O-CASCO-R9"
    copia = run_dir / "copia" / "SALA_ATUAL.json"
    somas = (oraculo / "SHA256SUMS.txt").read_text(encoding="utf-8")
    esperado = next(l.split(" *")[0] for l in somas.splitlines() if l.endswith("copia/SALA_ATUAL.json"))
    out = {"SALA_ATUAL": str(copia), "SALA_ATUAL_SHA256": sha(copia), "SHA256_QUE_A_R9_REGISTOU": esperado}
    assert out["SALA_ATUAL_SHA256"] == esperado, "nao e a mesma Sala da R9"
    ro = (run_dir / "copia" / "PROVA_RO.txt").read_text(encoding="utf-8").split()
    ro_fim = (run_dir / "copia" / "PROVA_RO_FIM.txt").read_text(encoding="utf-8").split()
    linhas = json.loads(copia.read_text(encoding="utf-8"))

    # 1 · o export, com o envelope do motor (por programa) e os pousos da propria copia
    export = {"EXPORT": M.EXPORT_DA_SALA, "SINTETICO": False, "CORTE": ro[1] + "T" + ro[2],
              "ORIGEM": "copia so-leitura da R9 · %s · sha256 %s" % (copia.name, out["SALA_ATUAL_SHA256"]),
              "READ_ONLY": ro[0] if ro_fim[0] == "on" else "off", "LINHAS": linhas,
              "POUSOS_DA_COPIA": [{"run_id": l["run_id"], "ordem": l["ordem"], "item_id": l["item_id"],
                                   "pousado_em": l.get("pousado_em")} for l in linhas]}
    limpo, corte = GI.cortar_vigente(export)
    out["CORTE"] = {k: corte[k] for k in ("LINHAS_NO_EXPORT", "LINHAS_NO_CORTE", "DEFEITO_NA_SALA",
                                          "ITEM_ID_REPETIDO", "REPETIDO_SEM_HORA_LEGIVEL")}
    out["CORTE"]["ITEM_ID_SEM_IDENTIDADE"] = len(corte["ITEM_ID_SEM_IDENTIDADE"])
    out["N38_NO_CORTE"] = any(l["item_id"] == N38[0] and l["run_id"] == N38[1] for l in limpo["LINHAS"])

    # 2 · o motor oficial (o mesmo do gatilho)
    try:
        saida = M.rodar(M.entrada_do_export(limpo), HOJE, "fd8c94698+L2")
    except Exception as e:  # noqa: BLE001
        out["MOTOR"] = {"ERRO": repr(e)[:500]}
        saida = None
    if saida is not None:
        objs = saida["ITENS_POR_FERRAMENTA"]
        out["MOTOR"] = {"CORRIDA": saida["INTELLIGENCE_RUN_ID"], "RESULT_STATE": saida["RESULT_STATE"],
                        "OBJETOS": {k: len(v) for k, v in objs.items()},
                        "NAO_ENVIADOS_AO_POTE": len(saida.get("NAO_ENVIADOS_AO_POTE") or []),
                        "RELACOES_D112": len(saida["D112"]["RELACOES"]),
                        "SINAIS_NO_LIVRO": len(saida["CORRIDA"].get("SIGNALS") or [])}
        # o que o motor oficial fez com o item do N38 (derived:11)
        def toca_n38(o):
            return N38[0] in json.dumps(o.get("PROVA") or o, ensure_ascii=False)
        out["MOTOR_SOBRE_O_N38"] = {
            "OBJETOS": [{"COMP": c, "ID": o.get("OBJETO_ID") or o.get("ID"), "ESPECIE": o.get("ESPECIE"),
                         "FACT_TIME": (o.get("CHAVES") or {}).get("FACT_TIME", o.get("FACT_TIME")),
                         "FACT_LOCATION": (o.get("CHAVES") or {}).get("FACT_LOCATION", o.get("FACT_LOCATION"))}
                        for c, v in objs.items() for o in v if toca_n38(o)],
            "SINAIS_DO_LIVRO": [{k: s.get(k) for k in ("SIGNAL_ID", "FACT_TIME", "FACT_TIME_BASIS", "FACT_LOCATION")}
                                for s in saida["CORRIDA"].get("SIGNALS") or [] if s.get("ITEM_ID") == N38[0]],
            "NAO_ENVIADOS": [x for x in saida.get("NAO_ENVIADOS_AO_POTE") or [] if N38[0] in json.dumps(x)][:5]}
        pote, conv = GI.montar_o_pote(saida)
        viol = GI.VP.validar(pote)
        prova = [p for e in pote["COMPARTIMENTOS"].values() for o in e["OBJETOS"] for p in o.get("PROVA") or []]
        out["POTE_OFICIAL"] = {"OBJETOS": {c: len(e["OBJETOS"]) for c, e in pote["COMPARTIMENTOS"].items() if e["OBJETOS"]},
                               "ENTITY_SOURCE_CONVERTIDOS": conv, "VIOLACOES": len(viol), "PRIMEIRAS": viol[:5],
                               "CAMPOS_DE_LIBERACAO": sorted({k for e in pote["COMPARTIMENTOS"].values()
                                                             for o in e["OBJETOS"] for k in o
                                                             if k in ("LIBERACAO", "CONFERENCIA_DE_LIBERACAO")}),
                               "PROVAS_COM_RAW_SHA256": sum(1 for p in prova if p.get("RAW_SHA256")),
                               "PROVAS": len(prova),
                               "PROVAS_COM_TRECHO": sum(1 for p in prova if p.get("TRECHO_DA_AFIRMACAO"))}

    # 3 · o oraculo (so leitura)
    man = json.loads((oraculo / "MANIFESTO-R9.json").read_text(encoding="utf-8"))
    pc = json.loads((oraculo / "POTE-R9-PARA_CLIENTE.json").read_text(encoding="utf-8"))
    lib = [o for e in pc["COMPARTIMENTOS"].values() for o in e["OBJETOS"] if o.get("LIBERACAO") == "LIBERADO_PARA_CLIENTE"]
    out["ORACULO"] = {"OBJETOS_LIBERADOS": len(lib),
                      "OBJETOS": [{"ID": o["OBJETO_ID"], "COMP": o["COMPARTIMENTO"], "ESPECIE": o["ESPECIE"],
                                   "FACT_TIME": (o.get("FORA_DO_CONTRATO") or {}).get("FACT_TIME"),
                                   "FACT_LOCATION": (o.get("FORA_DO_CONTRATO") or {}).get("FACT_LOCATION"),
                                   "TRECHO": (o["PROVA"][0].get("TRECHO_DA_AFIRMACAO") or "")[:90],
                                   "RAW_SHA256": o["PROVA"][0].get("RAW_SHA256")} for o in lib]}
    src = (oraculo / "montar_r9.py").read_text(encoding="utf-8").splitlines()
    out["ORACULO_ESCRITO_A_MAO"] = {
        "AFIRMACOES_LINHAS": [i + 1 for i, l in enumerate(src) if l.startswith("AFIRMACOES = [")],
        "TRECHOS_LITERAIS_NO_SCRIPT": sum(1 for l in src if re.search(r'"(AFIRMACAO|DATA|LUGAR|FACT_TIME|FACT_LOCATION)":\s*"', l)),
        "C8_ESCRITO": [i + 1 for i, l in enumerate(src) if l.startswith(("C8_N38", "C8_MYFRUIT"))]}

    # 4 · a tabela
    auto = 0 if saida is None else sum(1 for e in pote["COMPARTIMENTOS"].values() for o in e["OBJETOS"]
                                       if o.get("LIBERACAO") == "LIBERADO_PARA_CLIENTE")
    ids_auto = set() if saida is None else {o.get("OBJETO_ID") for e in pote["COMPARTIMENTOS"].values()
                                              for o in e["OBJETOS"]}
    out["TABELA"] = {
        "OBJETOS_LIBERADOS_MANUAL": len(lib),
        "OBJETOS_LIBERADOS_AUTO": auto,
        "MESMOS_OBJETOS": "SIM" if {o["OBJETO_ID"] for o in lib} <= ids_auto and auto == len(lib) else "NAO",
        "HOUVE_INTERVENCAO_HUMANA_NA_GERACAO": "NAO",
    }
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:6000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
