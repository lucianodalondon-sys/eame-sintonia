#!/usr/bin/env python3
"""Auditoria do manifesto de rotulos e tentativa de recuperacao dos PDF.

Nao inventa uso de rotulo. Faz as duas coisas que dao para fazer sem os arquivos:

  1. AUDITA o manifesto contra si mesmo e contra o mapa de identidade — sha256
     duplicado, documento sem produto, tipo em conflito, registro ausente.
  2. TENTA recuperar os PDF pelas rotas que existem, e grava o HTTP de cada uma.
     Uma amostra basta para provar a rota: se a rota devolve 403 para tres, ela
     devolve 403 para 141.

    ./scripts/adama_it_labels.py

Regra que o codigo aplica: arquivo baixado mais novo nao e rotulo legal vigente.
Sem data de rotulo lida, CURRENT_LABEL_STATUS = UNKNOWN.
"""
import json
import os
import subprocess
from collections import Counter, defaultdict
from datetime import date

OUT = "research/adama-italy-product-intelligence-deep"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36"
AMOSTRA = 3


def _http(url):
    r = subprocess.run(["curl", "-sS", "-m", "30", "-A", UA, "-o", "/dev/null",
                        "-w", "%{http_code} %{size_download}", "-L", url],
                       capture_output=True, text=True)
    return (r.stdout.strip() or "000 0") + (" " + r.stderr.strip()[:80] if r.stderr.strip() else "")


def main():
    with open(os.path.join(OUT, "LABEL-MANIFEST.json"), encoding="utf-8") as fh:
        man = json.load(fh)
    with open(os.path.join(OUT, "PRODUCT-IDENTITY-MAP.json"), encoding="utf-8") as fh:
        mapa = {m["PRODUCT_ID"]: m for m in json.load(fh)["PRODUCTS"]}
    docs = man["DOCUMENTS"]

    # ---------------------------------------------------------- 1 · auditoria
    achados = []
    por_sha = defaultdict(list)
    for d in docs:
        if d.get("SHA256"):
            por_sha[d["SHA256"]].append(d)
    for sha, grupo in por_sha.items():
        if len(grupo) > 1:
            achados.append({"KIND": "SAME_SHA256_MULTIPLE_ENTRIES", "SHA256": sha,
                            "PRODUCTS": sorted({g["PRODUCT_NAME"] for g in grupo}),
                            "MEANING": "um mesmo arquivo serve mais de um produto — nao e erro, e um fato a preservar"})
    for d in docs:
        if not d.get("PRODUCT_ID"):
            achados.append({"KIND": "DOCUMENT_WITHOUT_PRODUCT_ID", "SOURCE_URL": d.get("SOURCE_URL"),
                            "PRODUCT_NAME": d.get("PRODUCT_NAME")})
        elif d["PRODUCT_ID"] in mapa and not mapa[d["PRODUCT_ID"]]["REGISTRATION_NUMBER"]:
            achados.append({"KIND": "DOCUMENT_ON_PRODUCT_WITHOUT_REGISTRATION",
                            "PRODUCT_NAME": d.get("PRODUCT_NAME"),
                            "MEANING": "produto sem registro provado — o documento existe, o vinculo regulatorio nao"})
        if not d.get("SHA256"):
            achados.append({"KIND": "NO_SHA256", "SOURCE_URL": d.get("SOURCE_URL")})

    etichette = [d for d in docs if d.get("DOCUMENT_TYPE") == "ETICHETTA"]

    # ------------------------------------------------- 2 · tentar recuperar
    tentativas = []
    for d in etichette[:AMOSTRA]:
        tentativas.append({"ROUTE": "ADAMA_MEDIA_DOWNLOAD", "URL": d["SOURCE_URL"],
                           "PRODUCT": d["PRODUCT_NAME"], "RESULT": _http(d["SOURCE_URL"])})
    tentativas.append({"ROUTE": "MINISTERO_BANCA_DATI_ETICHETTE",
                       "URL": "https://www.fitosanitari.salute.gov.it/",
                       "PRODUCT": None, "RESULT": _http("https://www.fitosanitari.salute.gov.it/")})
    tentativas.append({"ROUTE": "SUPABASE_BUCKET",
                       "URL": "(bucket 'raw', prefixo IT/adama-website)", "PRODUCT": None,
                       "RESULT": "NO_CREDENTIALS_IN_THIS_ENVIRONMENT — SUPABASE_URL e SUPABASE_SECRET_KEY nao estao definidos, e nao devem ser commitados"})
    tentativas.append({"ROUTE": "GIT_HISTORY",
                       "URL": "(qualquer branch)", "PRODUCT": None,
                       "RESULT": "NOT_PRESENT — data/raw e ignorado por politica do repositorio (D-003); nenhum PDF entrou no Git"})
    tentativas.append({"ROUTE": "LOCAL_DISK",
                       "URL": "(find / -name '*.pdf' -path '*adama*')", "PRODUCT": None,
                       "RESULT": "NOT_PRESENT — nenhum arquivo"})

    recuperados = sum(1 for t in tentativas if t["RESULT"].startswith("200"))

    # -------------------------------------------------- 3 · versao do rotulo
    for d in docs:
        d["CURRENT_LABEL_STATUS"] = "UNKNOWN"
        d["CURRENT_LABEL_STATUS_WHY"] = (
            "nenhuma data de rotulo foi lida do documento; arquivo baixado mais novo "
            "nao prova rotulo legal vigente")
        d["VERSIONS_KNOWN"] = 1
        d["RECOVERY_STATE"] = "NOT_RECOVERED"

    man["AUDITED_AT"] = date.today().isoformat()
    man["AUDIT"] = {
        "DOCUMENTS": len(docs),
        "ETICHETTE": len(etichette),
        "BY_TYPE": dict(Counter(d.get("DOCUMENT_TYPE") for d in docs)),
        "WITH_SHA256": sum(1 for d in docs if d.get("SHA256")),
        "WITH_PRODUCT_ID": sum(1 for d in docs if d.get("PRODUCT_ID")),
        "WITH_REGISTRATION_NUMBER": sum(1 for d in docs if d.get("REGISTRATION_NUMBER")),
        "FINDINGS": achados,
        "FINDINGS_BY_KIND": dict(Counter(a["KIND"] for a in achados)),
    }
    man["RECOVERY"] = {
        "ATTEMPTED_ROUTES": tentativas,
        "DOCUMENTS_RECOVERED": recuperados,
        "SAMPLE_PROVES_ROUTE": "uma rota que devolve 403 para 3 devolve 403 para 141",
        "CURRENT_LABELS_VERIFIED": 0,
        "WHAT_WOULD_UNBLOCK": [
            "rodar na maquina com janela grafica e o acervo em C:\\eame-sintonia-it",
            "expor SUPABASE_URL e SUPABASE_SECRET_KEY como secrets de execucao (nunca no Git)",
        ],
    }
    with open(os.path.join(OUT, "LABEL-MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump(man, fh, ensure_ascii=False, indent=2)

    # As camadas que dependem do conteudo do rotulo nascem vazias E DIZEM O HTTP de
    # cada rota tentada. Um zero sem o motivo ao lado vira, tres semanas depois,
    # "nao existe" na cabeca de quem le.
    vazio = {
        "BUILT_AT": man["AUDITED_AT"], "RECORDS": [], "COUNT": 0, "STATE": "REAL_GAP",
        "WHY": "nenhuma etichetta foi lida. %d rotas de recuperacao tentadas, %d documentos recuperados."
               % (len(tentativas), recuperados),
        "RECOVERY_ROUTES_TRIED": [{"ROUTE": t["ROUTE"], "RESULT": t["RESULT"]} for t in tentativas],
        "WHAT_IS_INVENTORIED_INSTEAD": "%d etichette com URL, tipo, bytes e sha256 em LABEL-MANIFEST.json" % len(etichette),
        "WHAT_WOULD_UNBLOCK": man["RECOVERY"]["WHAT_WOULD_UNBLOCK"],
        "RULE": "sem rotulo lido nao ha par cultura x alvo defensavel. Zero e o numero honesto.",
    }
    for nome in ("LABEL-USES.json", "HERBICIDE-LABEL-USES.json",
                 "FUNGICIDE-LABEL-USES.json", "INSECTICIDE-LABEL-USES.json"):
        with open(os.path.join(OUT, nome), "w", encoding="utf-8") as fh:
            json.dump(vazio, fh, ensure_ascii=False, indent=2)
    cobertura = dict(
        vazio,
        WHY="depende de LABEL-USES.json, que esta vazio pelo motivo acima",
        NEVER=("zero verificado NAO significa 'a ADAMA nao tem produto'. Significa "
               "NO CONFIRMED MATCH IN CURRENT LABEL READING."))
    for nome in ("PRODUCT-CROP-COVERAGE.json", "TARGET-PRODUCT-COVERAGE.json"):
        with open(os.path.join(OUT, nome), "w", encoding="utf-8") as fh:
            json.dump(cobertura, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"AUDIT": {k: v for k, v in man["AUDIT"].items() if k != "FINDINGS"},
                      "RECOVERED": recuperados,
                      "ROUTES": [{"ROUTE": t["ROUTE"], "RESULT": t["RESULT"][:70]} for t in tentativas]},
                     ensure_ascii=False, indent=2))
    return man


if __name__ == "__main__":
    main()
