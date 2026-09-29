#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G0 POR AFIRMACAO sobre a MESMA Sala da R9 — o criterio de aceitacao da DIRETIVA-G0-POR-AFIRMACAO (§3).

    py provas/l2/g0_afirmacao_r9.py --afirmacoes=<AFIRMACOES.json do produtor> [--r9=<intelligence-experimental>]
                                                                   ->  provas/l2/G0-AFIRMACAO-R9.json

O caminho oficial do gatilho (cortar_vigente -> motor_das_capacidades.rodar(afirmacoes=...) -> montar_o_pote ->
validar_pote_v2), sobre os bytes exatos da Sala da R9 (sha conferido) e o artefato AFIRMACOES_DA_SALA/v1 que o
produtor (ramo produtor-afirmacoes-v1, NAO alterado) escreveu a partir dela. O oraculo PARA-O-CASCO-R9 so e lido
para saber que ITENS sao «a R9» (os da PROVA dos objetos liberados a mao): nenhum id, trecho ou data dele entra.

    AFIRMACOES_COM_TEMPO_E_LUGAR   no artefato (FACT_TIME com valor + FACT_LOCATION com valor)
    PASSAM_G0_DA_AFIRMACAO         dessas, quantas passam o G0 DELAS (cada recusa com o motivo, por CLAIM_ID)
    CHEGAM_AO_POTE                 dessas, quantas estao no pote (archive) depois do fiscal
    FORA_DA_R9_CHEGAM_AO_POTE      o mesmo, so nos itens que NAO sao os do oraculo  ← o numero que conta
    SEM_AFIRMACOES_POTE_IGUAL      o pote sem artefato tem o SHA do que a L2 ja publicou
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from collections import Counter
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
import funil_r9 as F                       # noqa: E402

SAIDA = AQUI.parent / "G0-AFIRMACAO-R9.json"
#: o POTE.json que a L2 publicou da R9 SEM afirmacoes (ENTREGA-L2-GERADOR, PARA-O-CASCO-L2-GERADOR)
POTE_PUBLICADO_SEM_AFIRMACOES = "db7e69048d60a087ba79ed511f16a60bd6a976ac1437b8fb1d83a285d3c4e9a8"


def _v(b):
    return b.get("VALOR") if isinstance(b, dict) else b


def _com_tempo_e_lugar(af) -> bool:
    ft, lugar = _v(af.get("FACT_TIME")), af.get("FACT_LOCATION") or {}
    return (ft not in (None, "NAO SEI", "NAO_EXISTE")
            and lugar.get("VALOR") not in (None, "NAO SEI") and lugar.get("LOCATION_SOURCE") != "UNRESOLVED")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    base = Path(next((a.split("=", 1)[1] for a in argv if a.startswith("--r9=")), R9.R9_PADRAO))
    arq = Path(next(a.split("=", 1)[1] for a in argv if a.startswith("--afirmacoes=")))
    artefato = json.loads(arq.read_text(encoding="utf-8"))
    oraculo_itens = set(F.itens_do_oraculo(base))
    export = F.export_da_r9(base)
    limpo, corte = GI.cortar_vigente(export)
    out = {"SALA_SHA256": R9.sha(next(base.glob("EXPD78-R9-*")) / "copia" / "SALA_ATUAL.json"),
           "AFIRMACOES": {"FICHEIRO": str(arq), "SHA256": R9.sha(arq), "CONTRATO": artefato.get("CONTRATO"),
                          "FUNIL_DO_PRODUTOR": artefato.get("FUNIL")},
           "ITENS_DO_ORACULO": sorted(oraculo_itens)}

    # 1 · sem afirmacoes: o pote tem de ser o publicado (o mesmo caminho do funil, a mesma entrega)
    s0 = M.rodar(M.entrada_do_export(limpo), R9.HOJE, "L2-FUNIL")
    with tempfile.TemporaryDirectory(prefix="l2-g0-") as t:
        GI.subir_o_pote(s0, Path(t) / "c", Path(t) / "PARAR.flag", entrega=Path(t) / "PARA-O-CASCO", corte=corte)
        sha0 = R9.sha(Path(t) / "PARA-O-CASCO" / "POTE.json")
    out["SEM_AFIRMACOES_POTE_SHA256"] = sha0
    out["SEM_AFIRMACOES_POTE_IGUAL"] = sha0 == POTE_PUBLICADO_SEM_AFIRMACOES

    # 2 · com afirmacoes
    s = M.rodar(M.entrada_do_export(limpo), R9.HOJE, "L2-FUNIL", afirmacoes=artefato)
    pote, conv = GI.montar_o_pote(s)
    viol = GI.VP.validar(pote)
    livro = s["CORRIDA"]
    entradas = {e["CLAIM_ID"]: e for e in s["LINEAGE"] if "CLAIM_ID" in e}
    recusadas = {r["CLAIM_ID"]: r for r in livro.get("AFIRMACOES_RECUSADAS") or []}
    no_pote = {p["CLAIM_ID"] for c in pote["COMPARTIMENTOS"].values() for o in c["OBJETOS"]
               for p in o["PROVA"] if "CLAIM_ID" in p}
    recusados_no_pote = {p.get("CLAIM_ID"): r.get("MOTIVO") for r in pote.get("RECUSADOS") or []
                         for p in ((r.get("OBJETO") or {}).get("PROVA") or []) if isinstance(p, dict)}
    alvo = [af for it in artefato["ITENS"] for af in it["AFIRMACOES"] if _com_tempo_e_lugar(af)]
    linhas = []
    for af in alvo:
        cid = af["CLAIM_ID"]
        e = entradas.get(cid)
        linhas.append({
            "CLAIM_ID": cid, "ITEM_ID": af.get("ITEM_ID"), "SOURCE_ID": af.get("SOURCE_ID"),
            "R9": af.get("ITEM_ID") in oraculo_itens,
            "FACT_TIME": _v(af.get("FACT_TIME")), "ORIGEM": (af.get("FACT_TIME_ROLE") or {}).get("ORIGEM"),
            "CLAIM_KIND": _v(af.get("CLAIM_KIND")), "FACT_LOCATION": (af.get("FACT_LOCATION") or {}).get("VALOR"),
            "G0_DO_ITEM": e.get("G0_DO_ITEM") if e else None,
            "G0_DA_AFIRMACAO": (e or {}).get("G0_DA_AFIRMACAO", "RECUSADA" if cid in recusadas else "FORA_DO_CORTE"),
            "PORQUE": ((e or {}).get("G0_FALTA") or (recusadas.get(cid) or {}).get("MOTIVOS") or
                       ([] if e else ["o item desta afirmacao nao esta no corte vigente"])),
            "DUPLICATA_DE": (e or {}).get("DUPLICATA_DE"),
            "NO_POTE": cid in no_pote,
            "RECUSA_NO_POTE": recusados_no_pote.get(cid)})
    fora = [l for l in linhas if not l["R9"]]
    r9 = [l for l in linhas if l["R9"]]
    out["CRITERIO"] = {
        "AFIRMACOES_COM_TEMPO_E_LUGAR": len(linhas),
        "PASSAM_G0_DA_AFIRMACAO": sum(1 for l in linhas if l["G0_DA_AFIRMACAO"] == "PASSOU"),
        "CHEGAM_AO_POTE": sum(1 for l in linhas if l["NO_POTE"]),
        "ANTES": "14 (medido pelo produtor com o G0 do ITEM: provas/d158/R9-PELO-CAMINHO-CANONICO.json)",
        "FORA_DA_R9_CHEGAM_AO_POTE": "%d / %d" % (sum(1 for l in fora if l["NO_POTE"]), len(fora)),
        "FORA_DA_R9_NUMERADOR": sum(1 for l in fora if l["NO_POTE"]),
        "FORA_DA_R9_DENOMINADOR": len(fora),
        "R9_CANARIO_NO_POTE": "%d / %d afirmacoes dos itens do oraculo" % (sum(1 for l in r9 if l["NO_POTE"]), len(r9)),
        # o sinal de DOCUMENTO INTEIRO do item do oraculo: um SINAL no pote provado pelo ITEM (sem CLAIM_ID)
        "SINAL_DE_DOCUMENTO_INTEIRO_NO_POTE": sum(1 for c in pote["COMPARTIMENTOS"].values() for o in c["OBJETOS"]
                                                  if o.get("ESPECIE") == "SINAL"
                                                  and any(p.get("ITEM_ID") in oraculo_itens and "CLAIM_ID" not in p
                                                          for p in o["PROVA"])),
        "SEM_AFIRMACOES_POTE_IGUAL": out["SEM_AFIRMACOES_POTE_IGUAL"],
        "VALIDAR_POTE_V2": "PASS" if not viol else "FAIL (%d)" % len(viol),
        "LIBERADOS": 0,
    }
    out["POR_QUE_NAO_PASSAM"] = dict(Counter(m for l in linhas if l["G0_DA_AFIRMACAO"] != "PASSOU"
                                             for m in l["PORQUE"]))
    out["INTAKE_DAS_AFIRMACOES"] = livro.get("INTAKE_DAS_AFIRMACOES")
    out["POTE"] = {"OBJETOS": {c: len(e["OBJETOS"]) for c, e in pote["COMPARTIMENTOS"].items() if e["OBJETOS"]},
                   "VIOLACOES": viol[:10], "RECUSADOS": dict(Counter(r.get("MOTIVO") for r in pote.get("RECUSADOS") or [])),
                   "ENTITY_SOURCE_CONVERTIDOS": conv, "INTELLIGENCE_RUN_ID": pote.get("INTELLIGENCE_RUN_ID")}
    out["AFIRMACOES_COM_TEMPO_E_LUGAR"] = linhas
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: out[k] for k in ("CRITERIO", "POR_QUE_NAO_PASSAM", "INTAKE_DAS_AFIRMACOES", "POTE")},
                     ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
