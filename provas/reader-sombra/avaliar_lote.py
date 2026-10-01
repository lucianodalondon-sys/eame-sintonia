#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Avalia as DUAS rodadas do leitor contra o CRITERIO do lote fixado (3827c7d7), sem mudar nada no criterio:
    GANHO >= 20 (alvos com FACT_TIME de ANO provado + trecho literal no texto) · REGRESSAO = 0 nos 6 controles ·
    DATAS_FALSAS = 0 nas 4 armadilhas · RODADA_1 = RODADA_2 por item (valor + trecho) · custo medido.
Regras de leitura (deterministicas, sem juizo humano):
  ALVO ganho     = JUIZ ACEITE nas duas rodadas, mesmo VALOR e TRECHO, trecho literal na copia, data nao e uma das
                   DATAS_FALSAS_CONHECIDAS do lote (mesma posicao), FACT_TIME com ano.
  CONTROLE ok    = o leitor NAO contradiz o FACT_TIME atual: ou NAO SEI (nao piora: o atual continua) ou um valor cujo
                   intervalo se sobrepoe ao do FACT_TIME atual. Valor fora do intervalo atual = REGRESSAO.
  ARMADILHA ok   = o leitor nao aceita nenhuma data (FACT_TIME continua NAO SEI). Qualquer ACEITE = DATA_FALSA.
  python provas/reader-sombra/avaliar_lote.py <LOTE.json> <SALA_ATUAL.json> <RODADA-1.json> <RODADA-2.json> <saida.json>"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "motor"))
import corrida_da_inteligencia as CI  # noqa: E402

norm = lambda t: re.sub(r"\s+", " ", t or "").strip()


def iv(v):
    t = CI.intervalo_do_tempo(v)
    return (t["INICIO"], t["FIM"]) if t.get("ESTADO") == "INTERVALO" else None


def main(a):
    lote, S = json.load(open(a[0], encoding="utf-8")), json.load(open(a[1], encoding="utf-8"))
    r1, r2 = (json.load(open(p, encoding="utf-8")) for p in a[2:4])
    R1 = {x["LOTE_ID"]: x for x in r1["LEITURAS"]}
    R2 = {x["LOTE_ID"]: x for x in r2["LEITURAS"]}
    linhas, cont = [], {"GANHO": 0, "REGRESSAO": 0, "DATAS_FALSAS": 0, "DIVERGENCIA_ENTRE_RODADAS": 0,
                        "TRECHO_FORA_DO_TEXTO": 0}
    for it in lote["ITENS"]:
        lid, cl = it["ID"], it["CLASSE"]
        texto = S[it["N"]]["texto"] or ""
        a1, a2 = R1[lid]["FACT_TIME"], R2[lid]["FACT_TIME"]
        k = lambda f: (f.get("VALOR"), norm(f.get("TRECHO")) if f.get("VALOR") != "NAO SEI" else "")
        igual = k(a1) == k(a2)
        if not igual:
            cont["DIVERGENCIA_ENTRE_RODADAS"] += 1
        falsas = {(f.get("POS"), f.get("DATA")) for f in it.get("DATAS_FALSAS_CONHECIDAS") or []}
        def falsa(f):
            p = (f.get("POSICAO_DA_DATA") or {}).get("INICIO")
            return any(p is not None and fp is not None and abs(p - fp) < 40 and norm(fd) in norm(f.get("DATA_LITERAL"))
                       for fp, fd in falsas)
        ac = [f for f in (a1, a2) if f.get("JUIZ") == "ACEITE"]
        for f in ac:
            if norm(f.get("TRECHO")) not in norm(texto):
                cont["TRECHO_FORA_DO_TEXTO"] += 1
        res = None
        if cl == "ALVO_PERDA_FACT_TIME":
            ok = (len(ac) == 2 and igual and not any(falsa(f) for f in ac) and iv(a1["VALOR"]) is not None
                  and norm(a1.get("TRECHO")) in norm(texto))
            res = "GANHO" if ok else "SEM_GANHO"
            cont["GANHO"] += ok
            if any(falsa(f) for f in ac):
                cont["DATAS_FALSAS"] += 1
                res = "DATA_FALSA_CONHECIDA"
        elif cl == "CONTROLE_JA_CORRETO":
            atual = iv(it["FACT_TIME_ATUAL"])
            reg = False
            for f in ac:
                v = iv(f["VALOR"])
                if atual is None or v is None or v[1] < atual[0] or v[0] > atual[1]:
                    reg = True
            res = "REGRESSAO" if reg else ("CONFIRMA" if ac else "NAO_SEI_NAO_PIORA")
            cont["REGRESSAO"] += reg
        else:
            res = "DATA_FALSA" if ac else "NAO_SEI_CORRETO"
            cont["DATAS_FALSAS"] += bool(ac)
        linhas.append({"ID": lid, "CLASSE": cl, "ITEM_ID": S[it["N"]]["item_id"], "RESULTADO": res,
                       "R1": {k_: a1.get(k_) for k_ in ("VALOR", "DATA_LITERAL", "TRECHO", "PAPEL_DA_DATA", "JUIZ")},
                       "R2": {k_: a2.get(k_) for k_ in ("VALOR", "DATA_LITERAL", "TRECHO", "PAPEL_DA_DATA", "JUIZ")},
                       "R1_IGUAL_R2": igual, "FACT_TIME_ATUAL": it["FACT_TIME_ATUAL"]})
    custo = [x["CUSTO"] for x in r1["LEITURAS"] + r2["LEITURAS"]]
    soma = lambda c: sum((x.get(c) or 0) for x in custo)
    n = len(custo)
    crit = {"GANHO>=20": cont["GANHO"] >= 20, "REGRESSAO=0": cont["REGRESSAO"] == 0,
            "DATAS_FALSAS=0": cont["DATAS_FALSAS"] == 0,
            "RODADA_1=RODADA_2": cont["DIVERGENCIA_ENTRE_RODADAS"] == 0,
            "TRECHO_NO_TEXTO": cont["TRECHO_FORA_DO_TEXTO"] == 0}
    out = {"LOTE_SHA256": r1["LOTE_SHA256"], "CONTAGEM": cont, "CRITERIO": crit,
           "VEREDITO": "PASSA" if all(crit.values()) else "FALHA",
           "CUSTO": {"LEITURAS": n, "SEGUNDOS_POR_ITEM": round(soma("SEGUNDOS") / n, 2),
                     "SEGUNDOS_API_POR_ITEM": round(soma("SEGUNDOS_API") / n, 2),
                     "TOKENS_SAIDA_POR_ITEM": round(soma("TOKENS_SAIDA") / n, 1),
                     "TOKENS_ENTRADA_TOTAL_POR_ITEM": round((soma("TOKENS_ENTRADA") + soma("TOKENS_CACHE_LIDOS") +
                                                             soma("TOKENS_CACHE_CRIADOS")) / n, 1),
                     "USD_LISTA_POR_ITEM": round(soma("USD_LISTA") / n, 4),
                     "NOTA": "USD_LISTA e o preco de lista que a CLI reporta; corre pela assinatura da casa"},
           "POR_CLASSE": {}, "LINHAS": linhas}
    for l in linhas:
        out["POR_CLASSE"].setdefault(l["CLASSE"], {}).setdefault(l["RESULTADO"], 0)
        out["POR_CLASSE"][l["CLASSE"]][l["RESULTADO"]] += 1
    Path(a[4]).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("CONTAGEM", "CRITERIO", "VEREDITO", "CUSTO", "POR_CLASSE")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
