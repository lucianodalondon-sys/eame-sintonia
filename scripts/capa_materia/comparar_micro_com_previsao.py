# -*- coding: utf-8 -*-
"""APOIO AO MICRO · o que veio contra o que se previu — SO LEITURA.

    py scripts/capa_materia/comparar_micro_com_previsao.py --estado <BIG-COLLECTION-ESTADO.json> --saida <pasta>
    py scripts/capa_materia/comparar_micro_com_previsao.py --runs RUN1,RUN2,... --saida <pasta>
       [--arvore <arvore do bot>]  [--previsao <MEDICAO-...json>]  [--sem-banco]

Depois de o MICRO correr, responde a duas perguntas:

  1. POR FONTE: quantos documentos novos a corrida trouxe, contra a previsao (27 no total,
     MEDICAO-CONTRATOS-AJUSTE-HOJE-V1.json), e quantos a Admission disse SIM / NAO / NAO_SEI.
  2. POR DOCUMENTO: cada documento, com o endereco, o resultado da observacao, o veredicto da
     Admission (e a regra e o motivo), se esta na Sala, e se era um dos alvos previstos.

DE ONDE LE (os mesmos sitios que o condutor da 1.a onda e o `micro_coleta.relatorio`):
  · <arvore>/data/collection-ledger/italy/observations.ndjson   o que o coletor viu, por RUN_ID
  · <arvore>/data/samples/LIVRO-DE-DECISOES.json                 o veredicto, por corrida e item
  · o banco da Sala, pela `micro_coleta.sql` (SELECT e nada mais; o banco em read-only) — para
    ligar cada documento (raw_asset) ao seu derivado e a decisao `derived:<id>`, e ver a Sala.
    Sem banco (ou com --sem-banco): as contagens por fonte fazem-se na mesma (a corrida e de UMA
    fonte); o veredicto documento a documento fica NAO SEI, e diz-se.

NAO escreve em livro nenhum, nem na Sala. So escreve os dois ficheiros de resultado em --saida.

⚠️ A previsao foi medida nos indices de 25/09 07:33. O indice muda todos os dias: diferenca entre
previsto e real NAO e erro por si — o que interessa e a forma (quem rende, quem volta vazio).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
ARVORE = Path.home() / "orca" / "workspaces" / "eame-sintonia" / "source-curator-service-v1"
PREVISAO = AQUI / "MEDICAO-CONTRATOS-AJUSTE-HOJE-V1.json"
# documento que a corrida trouxe e que o livro ainda nao tinha (o que a previsao conta)
NOVO = ("NEW_DOCUMENT",)
# o documento ja existia e voltou mudado (revisita) — conta-se a parte
VERSAO_NOVA = ("DOCUMENT_CHANGED_IN_PLACE", "SEMANTIC_ID_CHANGED_SAME_BYTES")
NAO_SEI = "NAO SEI"


def ler_ndjson(p: Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def corridas_do_estado(estado: dict) -> list[tuple[str, str]]:
    return [(f["SOURCE_ID"], f["RUN_ID"]) for f in estado.get("FONTES", []) if f.get("RUN_ID")]


def consultar_banco(run_ids: list[str], consulta) -> tuple[list[dict], set[str]]:
    """(uma linha por raw_asset das corridas, itens na Sala). `consulta` = micro_coleta.sql."""
    em = ",".join("'%s'" % r.replace("'", "") for r in run_ids)
    raws = consulta(
        "select r.id, r.source_id, r.run_id, coalesce(r.source_url,''), coalesce(d.id::text,'')"
        " from raw_asset r left join derived_artifact d on d.raw_asset_id = r.id"
        f" where r.run_id in ({em}) order by r.id")
    sala = consulta(f"select s.item_id from sala_de_espera s where s.run_id in ({em})")
    return ([{"RAW_ID": x[0], "SOURCE_ID": x[1], "RUN_ID": x[2], "SOURCE_URL": x[3], "DERIVED_ID": x[4]}
             for x in raws], {x[0] for x in sala})


def comparar(corridas: list[tuple[str, str]], observacoes: list[dict], decisoes: list[dict],
             previsao: dict, banco: tuple[list[dict], set[str]] | None) -> dict:
    run_ids = [r for _, r in corridas]
    fonte_de = {r: s for s, r in corridas}
    prev = {f["SOURCE_ID"]: f for f in previsao.get("FONTES", [])}
    obs = [o for o in observacoes if o.get("RUN_ID") in fonte_de]
    dec = [d for d in decisoes if d.get("corrida") in fonte_de]
    por_item = {d["item"]: d for d in dec if d.get("item") and d["item"] != NAO_SEI}

    documentos = []
    for o in obs:
        res = o.get("OBSERVATION_RESULT")
        if res not in NOVO + VERSAO_NOVA:
            continue
        sid = fonte_de[o["RUN_ID"]]
        documentos.append({"SOURCE_ID": sid, "RUN_ID": o["RUN_ID"], "SOURCE_URL": o.get("SOURCE_URL"),
                           "OBSERVATION_RESULT": res, "TIPO": "NOVO" if res in NOVO else "VERSAO_NOVA",
                           "ESTAVA_NA_PREVISAO": o.get("SOURCE_URL") in (prev.get(sid, {}).get("ALVOS_D40") or []),
                           "RAW_ID": NAO_SEI, "DERIVED_ID": NAO_SEI, "ADMISSION": NAO_SEI,
                           "REGRA": None, "MOTIVO": None, "NA_SALA": NAO_SEI})
    if banco is not None:
        raws, sala = banco
        por_url = {}
        for r in raws:
            por_url.setdefault((r["RUN_ID"], r["SOURCE_URL"]), []).append(r)
        for d in documentos:
            achados = por_url.get((d["RUN_ID"], d["SOURCE_URL"])) or []
            if len(achados) != 1:
                d["LIGACAO"] = "%d raw_asset para este endereco nesta corrida" % len(achados)
                continue
            r = achados[0]
            d["RAW_ID"], d["DERIVED_ID"] = r["RAW_ID"], r["DERIVED_ID"] or "SEM_DERIVADO"
            if not r["DERIVED_ID"]:
                d["ADMISSION"] = "SEM_DERIVADO"
                continue
            k = "derived:%s" % r["DERIVED_ID"]
            x = por_item.get(k)
            d["ADMISSION"] = x["resultado"] if x else "SEM_DECISAO"
            if x:
                d["REGRA"], d["MOTIVO"] = x.get("regra"), (x.get("motivo") or "")[:200]
            d["NA_SALA"] = k in sala

    fontes = []
    for sid, run in corridas:
        p = prev.get(sid, {})
        meus = [d for d in documentos if d["SOURCE_ID"] == sid]
        novos = [d for d in meus if d["TIPO"] == "NOVO"]
        previsto = p.get("DOCUMENTOS_NOVOS_NA_CORRIDA", NAO_SEI)
        adm_por_corrida = Counter(d.get("resultado") for d in dec if d.get("corrida") == run)
        fontes.append({
            "SOURCE_ID": sid, "RUN_ID": run, "PREVISTO_NOVOS": previsto, "REAL_NOVOS": len(novos),
            "DIFERENCA": (len(novos) - previsto) if isinstance(previsto, int) else NAO_SEI,
            "REAL_VERSOES_NOVAS": len(meus) - len(novos),
            "NOVOS_QUE_ERAM_PREVISTOS": sum(1 for d in novos if d["ESTAVA_NA_PREVISAO"]),
            # da corrida inteira (sem banco e o que ha); com banco, por documento em ADMISSION_DOS_DOCUMENTOS
            "ADMISSION_DA_CORRIDA": dict(adm_por_corrida),
            "ADMISSION_DOS_DOCUMENTOS": dict(Counter(d["ADMISSION"] for d in meus)),
        })
    soma = lambda k: sum(f[k] for f in fontes if isinstance(f[k], int))   # noqa: E731
    return {
        "DATASET": "COMPARACAO-MICRO-COM-PREVISAO-V1",
        "PREVISAO": {"DATASET": previsao.get("DATASET"), "MEDIDO_EM": previsao.get("MEDIDO_EM"),
                     "TOTAL_PREVISTO": (previsao.get("TOTAL") or {}).get("DOCUMENTOS_NOVOS_POR_CORRIDA_D40_D38")},
        "BANCO": "LIDO" if banco is not None else "NAO_LIDO — veredicto por documento NAO SEI",
        "CORRIDAS": len(corridas),
        "TOTAL": {
            "PREVISTO_NOVOS": soma("PREVISTO_NOVOS"), "REAL_NOVOS": soma("REAL_NOVOS"),
            "REAL_VERSOES_NOVAS": soma("REAL_VERSOES_NOVAS"),
            "FONTES_COM_NOVO": sum(1 for f in fontes if f["REAL_NOVOS"] > 0),
            "ADMISSION_DAS_CORRIDAS": dict(sum((Counter(f["ADMISSION_DA_CORRIDA"]) for f in fontes), Counter())),
            "ADMISSION_DOS_DOCUMENTOS": dict(Counter(d["ADMISSION"] for d in documentos)),
            "SIM_SOBRE_FONTES": "%d/%d" % (sum(1 for d in documentos if d["ADMISSION"] == "SIM"), len(corridas)),
        },
        "FONTES": fontes,
        "DOCUMENTOS": documentos,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--estado", help="o estado do condutor (FONTES[].SOURCE_ID/RUN_ID)")
    g.add_argument("--runs", help="RUN_IDs separados por virgula (a fonte le-se no livro de observacoes)")
    ap.add_argument("--saida", required=True)
    ap.add_argument("--arvore", default=str(ARVORE))
    ap.add_argument("--previsao", default=str(PREVISAO))
    ap.add_argument("--sem-banco", action="store_true")
    a = ap.parse_args(argv)
    arvore = Path(a.arvore)
    observacoes = ler_ndjson(arvore / "data" / "collection-ledger" / "italy" / "observations.ndjson")
    if a.estado:
        corridas = corridas_do_estado(json.loads(Path(a.estado).read_text(encoding="utf-8")))
    else:
        runs = [r.strip() for r in a.runs.split(",") if r.strip()]
        fonte = {o["RUN_ID"]: o["SOURCE_ID"] for o in observacoes if o.get("RUN_ID") in runs}
        corridas = [(fonte.get(r, NAO_SEI), r) for r in runs]
    livro = arvore / "data" / "samples" / "LIVRO-DE-DECISOES.json"
    decisoes = json.loads(livro.read_text(encoding="utf-8"))["DECISOES"] if livro.exists() else []
    previsao = json.loads(Path(a.previsao).read_text(encoding="utf-8"))
    banco = None
    if not a.sem_banco:
        try:
            sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
            import micro_coleta as M   # noqa: PLC0415
            banco = consultar_banco([r for _, r in corridas], M.sql)
        except Exception as e:   # noqa: BLE001
            print("banco nao lido (%s) — sigo sem ele" % str(e)[:160])
    out = comparar(corridas, observacoes, decisoes, previsao, banco)
    out["LIDO_DE"] = {"ARVORE": str(arvore), "PREVISAO": str(a.previsao)}
    s = Path(a.saida)
    s.mkdir(parents=True, exist_ok=True)
    (s / "COMPARACAO-MICRO-COM-PREVISAO-V1.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    with open(s / "DOCUMENTOS-DO-MICRO.tsv", "w", encoding="utf-8", newline="\n") as f:
        cols = ["SOURCE_ID", "TIPO", "ADMISSION", "NA_SALA", "ESTAVA_NA_PREVISAO", "SOURCE_URL", "REGRA", "MOTIVO"]
        f.write("\t".join(cols) + "\n")
        for d in out["DOCUMENTOS"]:
            f.write("\t".join(str(d.get(c) if d.get(c) is not None else "") for c in cols) + "\n")
    print("%-11s %8s %5s %5s  %s" % ("FONTE", "PREVISTO", "REAL", "DIF", "ADMISSION (documentos)"))
    for x in out["FONTES"]:
        print("%-11s %8s %5s %5s  %s" % (x["SOURCE_ID"], x["PREVISTO_NOVOS"], x["REAL_NOVOS"], x["DIFERENCA"],
                                         x["ADMISSION_DOS_DOCUMENTOS"] or x["ADMISSION_DA_CORRIDA"]))
    print(json.dumps(out["TOTAL"], ensure_ascii=False))
    print("banco:", out["BANCO"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
