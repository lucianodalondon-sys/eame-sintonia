#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LEITOR-DATA-YOUTUBE · compara antes x depois, campo a campo e item a item. So leitura.
uso: py comparar.py <pasta da medida> [<previsao da ACERVO para conferir o antes>]"""
import collections, json, sys

NS = "NAO SEI"
QUATRO = ("PUBLICACAO", "LOCAL_DA_FONTE", "DATA_DO_FATO", "LOCAL_DO_FATO")
o = sys.argv[1]
A = json.load(open(o + "/antes.json", encoding="utf-8"))
D = json.load(open(o + "/depois.json", encoding="utf-8"))
ia = {x["SHA256"]: x for x in A["ITENS"]}
idd = {x["SHA256"]: x for x in D["ITENS"]}
assert set(ia) == set(idd), "os dois lados nao mediram os mesmos conteudos"
tem = lambda x, c: x["PREVISTO"][c]["VALOR"] not in (NS, "", None) and not str(x["PREVISTO"][c]["VALOR"]).startswith(NS)
out = collections.OrderedDict()
out["CODIGO"] = {"ANTES": A["CODIGO"], "DEPOIS": D["CODIGO"]}
out["ENTRADAS"] = {k: A["ENTRADAS"][k] for k in ("RAW_LINHAS", "CONTEUDOS_DISTINTOS", "SALA_LINHAS", "LIVROS_LIDOS", "OBSERVACOES_COM_SHA")}
for grupo, filtro in (("FORA_DA_SALA", lambda x: not x["NA_SALA"]), ("SALA", lambda x: x["NA_SALA"])):
    shas = [s for s in ia if filtro(ia[s])]
    g = collections.OrderedDict(CONTEUDOS=len(shas))
    for c in QUATRO:
        g[c] = {"ANTES": sum(tem(ia[s], c) for s in shas), "DEPOIS": sum(tem(idd[s], c) for s in shas)}
    mudou = collections.defaultdict(list)
    for s in shas:
        for c in QUATRO:
            va, vd = ia[s]["PREVISTO"][c], idd[s]["PREVISTO"][c]
            if (va["VALOR"], va["BASE"]) != (vd["VALOR"], vd["BASE"]):
                mudou[c].append({"SHA256": s[:16], "SOURCE_ID": ia[s]["SOURCE_ID"], "ANTES": va, "DEPOIS": vd})
    g["MUDARAM_POR_CAMPO"] = {c: len(mudou[c]) for c in QUATRO}
    g["PUBLICACAO_JA_LIDA_QUE_MUDOU"] = sum(1 for m in mudou["PUBLICACAO"] if m["ANTES"]["VALOR"] != NS)
    g["BASES_NOVAS_DA_PUBLICACAO"] = dict(collections.Counter(m["DEPOIS"]["BASE"] for m in mudou["PUBLICACAO"]))
    g["FONTES_QUE_GANHAM_PUBLICACAO"] = dict(collections.Counter(m["SOURCE_ID"] for m in mudou["PUBLICACAO"]).most_common(15))
    g["DATA_DO_FATO_CALCULADA"] = {"ANTES": sum(1 for s in shas if ia[s]["FACT_TIME_CALCULO"] == "RELATIVA_A_PUBLICACAO"),
                                   "DEPOIS": sum(1 for s in shas if idd[s]["FACT_TIME_CALCULO"] == "RELATIVA_A_PUBLICACAO")}
    g["OUTROS_3_CAMPOS_QUE_MUDARAM"] = {c: mudou[c] for c in QUATRO[1:] if mudou[c]}
    out[grupo] = g
if len(sys.argv) > 2:
    P = json.load(open(sys.argv[2], encoding="utf-8"))
    out["CONFERENCIA_COM_A_ACERVO"] = {"ACERVO_FORA": {k: P["ACERVO_FORA_DA_SALA"][k] for k in P["ACERVO_FORA_DA_SALA"] if k.startswith("GANHA_")},
                                      "MEU_ANTES_FORA": {k: A["ACERVO_FORA_DA_SALA"][k] for k in A["ACERVO_FORA_DA_SALA"] if k.startswith("GANHA_")},
                                      "ACERVO_SALA": {k: P["SALA"][k] for k in P["SALA"] if k.startswith("GANHA_")},
                                      "MEU_ANTES_SALA": {k: A["SALA"][k] for k in A["SALA"] if k.startswith("GANHA_")}}
json.dump(out, open(o + "/COMPARACAO.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
resumo = {k: v for k, v in out.items()}
for g in ("FORA_DA_SALA", "SALA"):
    resumo[g] = {k: v for k, v in out[g].items() if k != "OUTROS_3_CAMPOS_QUE_MUDARAM"}
    resumo[g]["OUTROS_3_CAMPOS_QUE_MUDARAM"] = {c: len(v) for c, v in out[g]["OUTROS_3_CAMPOS_QUE_MUDARAM"].items()}
print(json.dumps(resumo, ensure_ascii=False, indent=1))
