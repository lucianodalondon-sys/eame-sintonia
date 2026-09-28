#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEDICAO da LIGACAO_ADAMA sobre os dados reais que existem offline (D123, 27/09/2026).

    python3 provas/ligacao_adama/medir.py            # escreve MEDICAO.json e a FILA
    python3 provas/ligacao_adama/medir.py --conferir # sai 1 se os ficheiros commitados divergirem

Sem rede, sem LLM, deterministico: HOJE declarado (2026-09-27), a referencia pela porta.

    1. os 86 cruzamentos da R7 e os pares por seccao — pelo proprio cruzamentos_max (o consumidor
       real, que chama a porta), sobre docs/intelligence/r7/ANALISE-R7.json
    2. os sinais da R7 que o insumo offline traz (9 dos 19: os 9 novos; os 10 da R6 nao estao
       em nenhum ficheiro deste repo) — sem chave de cultura/problema/substancia no insumo
    3. o acervo (ENTRADA-INTELLIGENCE-ACERVO.json, 2080 itens) com CROP_IDS/ISSUE_IDS da
       Collection — lido do objeto git de origin/claude/organize-collection-system-japwor
       (nao e trazido para esta arvore); sem o objeto: NAO SEI, dito

Saidas: provas/ligacao_adama/MEDICAO.json · docs/intelligence/ligacao-adama/FILA-BULAS-A-LER.json
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for g in ("motor",):
    sys.path.insert(0, str(RAIZ / g))
import porta_da_referencia as PORTA  # noqa: E402
import cruzamentos_max as XM  # noqa: E402
import fila_bulas_a_ler as FILA  # noqa: E402

HOJE = date(2026, 9, 27)
ACERVO_REF = "origin/claude/organize-collection-system-japwor"
ACERVO_CAMINHO = "docs/intelligence/acervo/ENTRADA-INTELLIGENCE-ACERVO.json"
SAIDA = RAIZ / "provas" / "ligacao_adama" / "MEDICAO.json"
SAIDA_FILA = RAIZ / "docs" / "intelligence" / "ligacao-adama" / "FILA-BULAS-A-LER.json"


def _git_show(ref, caminho):
    try:
        p = subprocess.run(["git", "-C", str(RAIZ), "show", "%s:%s" % (ref, caminho)], capture_output=True,
                           check=True)
        return p.stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def tabela(ligs) -> dict:
    estados = Counter(l["ESTADO"] for l in ligs)
    falta = Counter(l["FALTA"][0] for l in ligs if l["ESTADO"] == PORTA.NAO_SEI_LIGACAO and l["FALTA"])
    falta_todas = Counter(f for l in ligs if l["ESTADO"] == PORTA.NAO_SEI_LIGACAO for f in l["FALTA"])
    return {"FATOS": len(ligs), "POR_ESTADO": {e: estados.get(e, 0) for e in PORTA.ESTADOS_DA_LIGACAO},
            "NAO_SEI_MOTIVO_PRINCIPAL": dict(falta.most_common()),
            "NAO_SEI_TODAS_AS_FALTAS": dict(falta_todas.most_common()),
            "MOTIVO_DOMINANTE_DE_NAO_SEI": (falta.most_common(1)[0][0] if falta else None),
            "COM_PRODUTO_ADAMA_LISTADO": sum(1 for l in ligs if l["PRODUTOS_ADAMA"]),
            "PEDEM_BULAS": sum(1 for l in ligs if l["BULAS_A_LER"])}


def medir(ref=None) -> tuple:
    ref = ref if ref is not None else PORTA.abrir(hoje=HOJE)
    r7 = XM.correr(hoje=HOJE, referencia=ref)
    cruz = [(r["OBJETO_ID"], r["LIGACAO_ADAMA"]) for r in r7["REFEITOS"]]
    pares = [("PAR:" + p["PAR_DO_BOLETIM"]["SALA_CHAVE"], p["LIGACAO_ADAMA"]) for p in r7["PORTFOLIO"]]
    analise = json.loads(Path(XM.R7).read_text(encoding="utf-8"))
    sinais = [("SINAL:%s:%s" % (s.get("SOURCE_ID"), s.get("FACT_TIME")), PORTA.ligacao_adama(ref, {"VEM_DE": {}}))
              for s in (analise.get("O_QUE_AS_38_ACRESCENTARAM") or {}).get("SINAIS") or []]

    bruto = _git_show(ACERVO_REF, ACERVO_CAMINHO)
    acervo, acervo_info = [], {"ESTADO": PORTA.NAO_SEI, "PORQUE": "objeto git %s:%s ausente neste clone"
                               % (ACERVO_REF, ACERVO_CAMINHO)}
    if bruto is not None:
        lista = json.loads(bruto)["LISTA"]
        memo = {}
        for it in lista:
            k = (tuple(sorted(it.get("CROP_IDS") or [])), tuple(sorted(it.get("ISSUE_IDS") or [])))
            if k not in memo:
                memo[k] = PORTA.ligacao_adama(ref, {
                    "CULTURA": list(k[0]), "PROBLEMA": list(k[1]),
                    "VEM_DE": {"CULTURA": "ACERVO.CROP_IDS (Collection)", "PROBLEMA": "ACERVO.ISSUE_IDS (Collection)"}})
            acervo.append((it["ACERVO_ID"], memo[k]))
        acervo_info = {"ESTADO": "LIDO", "GIT": "%s:%s" % (ACERVO_REF, ACERVO_CAMINHO),
                       "SHA256": hashlib.sha256(bruto).hexdigest(), "ITENS": len(lista),
                       "COMBINACOES_DE_CHAVES": len(memo)}
    todos = cruz + pares + sinais + acervo
    medicao = {
        "SCHEMA": "MEDICAO_LIGACAO_ADAMA/v1", "MARCA": "EXPERIMENTAL · NAO_PARA_CLIENTE",
        "HOJE": HOJE.isoformat(), "CARIMBO": {k: v for k, v in PORTA.carimbo(ref).items() if k != "SHA256"},
        "INSUMOS": {
            "ANALISE_R7": {"CAMINHO": "docs/intelligence/r7/ANALISE-R7.json",
                           "SHA256": hashlib.sha256(Path(XM.R7).read_bytes()).hexdigest()},
            "ACERVO": acervo_info},
        "CHAVES_USADAS": {
            "CRUZAMENTOS_R7": "SUBSTANCIA (a citada no troco). A cultura do boletim e lista do DOCUMENTO "
                              "(ENTITY_SOURCE = DOCUMENT, D112) e nao entra como chave",
            "PARES_POR_SECAO": "CULTURA x PRAGA da mesma seccao (Collection)",
            "SINAIS_R7": "nenhuma: o insumo offline so traz SOURCE_ID, FACT_TIME, KIND, LOCAL, URL",
            "ACERVO": "CROP_IDS x ISSUE_IDS (Collection)"},
        "TABELAS": {"CRUZAMENTOS_R7": tabela([l for _, l in cruz]),
                    "PARES_POR_SECAO_R7": tabela([l for _, l in pares]),
                    "SINAIS_R7_OFFLINE": dict(tabela([l for _, l in sinais]),
                                              NOTA="9 de 19: os 10 sinais da R6 nao estao em ficheiro deste repo "
                                                   "(NAO MEDIDOS)"),
                    "ACERVO": tabela([l for _, l in acervo]) if acervo else acervo_info,
                    "TUDO": tabela([l for _, l in todos])},
        "NAO_PROVA": "a ligacao nao prova pressao de campo nem demanda (INT-LAW-145) e nao e fonte (INT-LAW-076)",
    }
    return medicao, FILA.fila(todos)


def _texto(d):
    return json.dumps(d, ensure_ascii=False, indent=1) + "\n"


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    medicao, fila = medir()
    if "--conferir" in argv:
        ok = SAIDA.read_text(encoding="utf-8") == _texto(medicao) and \
            SAIDA_FILA.read_text(encoding="utf-8") == _texto(fila)
        print("IGUAL" if ok else "DIFERENTE")
        return 0 if ok else 1
    SAIDA_FILA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(_texto(medicao), encoding="utf-8")
    SAIDA_FILA.write_text(_texto(fila), encoding="utf-8")
    for k, t in medicao["TABELAS"].items():
        print(k, t.get("FATOS"), t.get("POR_ESTADO"), t.get("NAO_SEI_MOTIVO_PRINCIPAL"))
    print("fila:", len(fila["ADAMA"]), "bulas ADAMA ·", len(fila["CONCORRENTES"]), "substancias (concorrentes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
