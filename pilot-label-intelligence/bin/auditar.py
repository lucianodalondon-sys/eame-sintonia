#!/usr/bin/env python3
"""
auditar.py — recontagem independente das afirmacoes do proprio piloto.

Nao confia em nenhum numero publicado pelos outros scripts. Reabre os artefatos
e as fontes e recomputa. Cada linha sai como OK, DIVERGE ou NAO_VERIFICAVEL.

Existe porque um piloto que pede honestidade dos outros tem de se auditar.
"""
import csv, hashlib, json, os, sys

B = "pilot-label-intelligence"
INACT = {"Revocato", "Scaduto"}
r = []


def chk(nome, esperado, obtido, nota=""):
    ok = (esperado == obtido)
    r.append({"CHECK": nome, "PUBLICADO": esperado, "RECOMPUTADO": obtido,
              "STATE": "OK" if ok else "DIVERGE", "NOTE": nota})


def na(nome, nota):
    r.append({"CHECK": nome, "STATE": "NAO_VERIFICAVEL", "NOTE": nota})


def main():
    d = json.load(open(f"{B}/demo/IT-LABEL-INTELLIGENCE.json", encoding="utf-8"))
    rv = json.load(open(f"{B}/labels/IT-ROTULOS-REVERIFICACAO.json", encoding="utf-8"))
    vs = json.load(open(f"{B}/registry/IT-REGISTRO-VERSOES.json", encoding="utf-8"))

    # 1. o universo de 163, recontado do CSV oficial
    csvp = f"{B}/registry/snapshots/PROD_FTS_6_20260831.csv"
    if os.path.exists(csvp):
        rows = list(csv.DictReader(open(csvp, encoding="utf-8", errors="replace"),
                                   delimiter=";"))
        ad = [x for x in rows
              if "ADAMA" in (x["ragione_sociale"] or "").upper()
              and x["stato_amministrativo"] not in INACT]
        chk("universo ADAMA ativo", d["TOTAL_ADAMA_PRODUCTS"], len(ad),
            "recontado direto do CSV oficial")
        chk("registro total", 17695, len(rows), "linhas do CSV oficial")
    else:
        na("universo ADAMA ativo", "CSV oficial ausente do disco")

    # 2. cada PDF no disco confere com o sha256 publicado
    ok = bad = falta = 0
    for it in rv["ITEMS"]:
        p = it.get("PDF_PATH")
        if not p or not os.path.exists(p):
            falta += 1
            continue
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        if h == it.get("CURRENT_SHA256"):
            ok += 1
        else:
            bad += 1
    chk("PDFs cujo sha256 confere com o publicado", rv["LABELS_CHECKED"], ok,
        f"{bad} divergentes, {falta} ausentes do disco")

    # 3. o hash de hoje bate com o da linha de base
    iguais = sum(1 for it in rv["ITEMS"]
                 if it.get("CURRENT_SHA256") == it.get("BASELINE_SHA256"))
    chk("rotulos identicos a linha de base", rv["DOCUMENT_UNCHANGED"], iguais,
        "recontado item a item")

    # 4. versoes distintas do registro sao mesmo distintas
    shas = [v["SHA256"] for v in vs["VERSIONS"]]
    chk("documentos distintos do registro", vs["DISTINCT_DOCUMENTS"], len(set(shas)),
        "sha256 unicos entre as versoes publicadas")
    # e os arquivos no disco batem com o sha publicado
    okv = sum(1 for v in vs["VERSIONS"]
              if os.path.exists(os.path.join(f"{B}/registry/snapshots",
                                             f'PROD_FTS_6_{v["SNAPSHOT_DATE"]}.csv'))
              and hashlib.sha256(open(os.path.join(f"{B}/registry/snapshots",
                                                   f'PROD_FTS_6_{v["SNAPSHOT_DATE"]}.csv'),
                                      "rb").read()).hexdigest() == v["SHA256"])
    chk("instantaneos do registro cujo sha confere", vs["DISTINCT_DOCUMENTS"], okv)

    # 5. eventos regulatorios versus ruido
    reg = [e for e in vs["CHANGE_EVENTS"] if not e.get("UNSTABLE_SOURCE")]
    txt = [e for e in vs["CHANGE_EVENTS"] if e.get("UNSTABLE_SOURCE")]
    chk("eventos regulatorios", vs["CHANGE_EVENTS_REGULATORY"], len(reg))
    chk("eventos rebaixados a texto", vs["CHANGE_EVENTS_TEXT_ONLY"], len(txt))

    # 6. todo evento tem OLD, NEW e fonte
    faltando = [e for e in vs["CHANGE_EVENTS"]
                if not e.get("BEFORE") or not e.get("AFTER") or not e.get("SOURCE")]
    chk("eventos sem OLD/NEW/fonte", 0, len(faltando),
        "um evento sem os tres nao e publicavel")

    # 7. pares cultura x alvo
    chk("pares cultura x alvo", d["TOTAL_USE_ROWS"],
        sum(len(p["USE_ROWS"]) for p in d["PRODUCTS"]))
    chk("produtos com uso lido", d["PRODUCTS_WITH_USE_ROWS"],
        sum(1 for p in d["PRODUCTS"] if p["USE_ROWS"]))

    # 8. a classe de evidencia dos pares fecha e nenhum par se apresenta
    #    como linha de tabela sem ter vindo da tabela
    tab = sum(1 for p in d["PRODUCTS"] for u in p["USE_ROWS"]
              if u["EVIDENCE_CLASS"] == "TABLE_GEOMETRY")
    txt = sum(1 for p in d["PRODUCTS"] for u in p["USE_ROWS"]
              if u["EVIDENCE_CLASS"] == "TEXT_INFERENCE")
    chk("pares de geometria de tabela", d["USE_ROWS_FROM_TABLE_GEOMETRY"], tab)
    chk("pares de inferencia de texto", d["USE_ROWS_FROM_TEXT_INFERENCE"], txt)
    chk("soma das classes bate com o total", d["TOTAL_USE_ROWS"], tab + txt,
        "nenhum par sem classe de evidencia")
    semclasse = sum(1 for p in d["PRODUCTS"] for u in p["USE_ROWS"]
                    if u.get("EVIDENCE_CLASS") not in ("TABLE_GEOMETRY", "TEXT_INFERENCE"))
    chk("pares sem classe de evidencia", 0, semclasse)

    # 9. todo produto da demo tem rotulo com fonte clicavel
    dm = json.load(open(f"{B}/demo/IT-DEMO-PRODUTOS.json", encoding="utf-8"))
    semfonte = [x for x in dm["PRODUCTS"] if not x.get("LABEL_URL")]
    chk("produtos da demo sem URL de rotulo", 0, len(semfonte))

    # 10. alertas: nenhum sem OLD e NEW
    al = json.load(open(f"{B}/demo/IT-ALERTAS.json", encoding="utf-8"))
    ruins = [x for x in al["ALERTS"] if x.get("OLD") in (None, "") or x.get("NEW") in (None, "")]
    chk("alertas sem OLD ou NEW", 0, len(ruins))

    # 11. nenhuma dose inventada: toda linha de dose tem citacao
    semq = 0
    for p in d["PRODUCTS"]:
        for x in p.get("DOSE_ROWS", []):
            if not x.get("SOURCE_QUOTE"):
                semq += 1
    chk("linhas de dose sem citacao", 0, semq,
        "uma dose sem citacao recuperavel nao entra")

    div = [x for x in r if x["STATE"] == "DIVERGE"]
    out = {"DATASET": "IT-AUDITORIA-DO-PILOTO",
           "O_QUE_ISTO_E": "recontagem independente das afirmacoes do proprio piloto",
           "CHECKS": len(r),
           "OK": sum(1 for x in r if x["STATE"] == "OK"),
           "DIVERGE": len(div),
           "NAO_VERIFICAVEL": sum(1 for x in r if x["STATE"] == "NAO_VERIFICAVEL"),
           "RESULTS": r}
    json.dump(out, open(f"{B}/AUDITORIA.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for x in r:
        mark = {"OK": "  ok  ", "DIVERGE": " DIVERGE ", "NAO_VERIFICAVEL": "  n/v "}[x["STATE"]]
        print(f'{mark} {x["CHECK"]:<46} pub={x.get("PUBLICADO")} rec={x.get("RECOMPUTADO")}')
    print(f'\n  {out["OK"]}/{out["CHECKS"]} ok · {out["DIVERGE"]} divergencias · '
          f'{out["NAO_VERIFICAVEL"]} nao verificaveis')
    return 1 if div else 0


if __name__ == "__main__":
    sys.exit(main())
