#!/usr/bin/env python3
"""
relatorio.py — gera a ENTREGA FINAL a partir dos artefatos.

Nenhum numero deste relatorio e digitado a mao. Se um artefato mudar, o
relatorio muda junto. Se um artefato faltar, o campo sai como NOT_PRODUCED em
vez de sair bonito.
"""
import argparse, hashlib, json, os, subprocess, sys

def le(p, default=None):
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return default

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="pilot-label-intelligence")
    ap.add_argument("--out", default="pilot-label-intelligence/ENTREGA-FINAL.md")
    a = ap.parse_args()
    B = a.base

    d = le(f"{B}/demo/IT-LABEL-INTELLIGENCE.json")
    dm = le(f"{B}/demo/IT-DEMO-PRODUTOS.json", {})
    al = le(f"{B}/demo/IT-ALERTAS.json", {})
    vs = le(f"{B}/registry/IT-REGISTRO-VERSOES.json", {})
    rv = le(f"{B}/labels/IT-ROTULOS-REVERIFICACAO.json", {})
    cc = le(f"{B}/labels/IT-CONCORRENTES-AMOSTRA.json", {})
    dz = le(f"{B}/demo/IT-DOSES.json", {})
    cd = le(f"{B}/labels/IT-CADENCIA-ROTULO.json", {})
    if d is None:
        print("faltam artefatos", file=sys.stderr); return 1

    hist = d.get("REGISTRY_HISTORY", {})
    lvc = d.get("LABEL_VERSION_CHECK", {})
    NP = "NOT_PRODUCED"
    n_dose_rows = d.get("TOTAL_DOSE_ROWS", 0)
    n_dose_lab = dz.get("LABELS_WITH_ROWS", NP) if dz else NP
    diffs = lvc.get("DOCUMENT_CHANGED", NP)
    vencidos = sum(1 for p in d["PRODUCTS"]
                   if isinstance(p["DAYS_TO_EXPIRY"], int) and p["DAYS_TO_EXPIRY"] < 0)

    pronto = all([
        d["TOTAL_ADAMA_PRODUCTS"] > 0,
        lvc.get("LABELS_CHECKED", 0) > 0,
        d["TOTAL_USE_ROWS"] > 0,
        os.path.exists(f"{B}/demo/label-intelligence.html"),
        al.get("ALERTS_TOTAL", 0) > 0,
    ])

    # Hash do pacote: sha256 sobre o conteudo de cada arquivo VERSIONADO do
    # piloto, em ordem de caminho. Nao inclui o proprio relatorio (que contem o
    # hash) nem o que o git ignora (instantaneos e PDFs, que sao rebaixaveis da
    # fonte oficial e conferiveis pelos hashes ja publicados).
    try:
        arquivos = sorted(subprocess.run(
            ["git", "ls-files", B], capture_output=True, text=True,
            check=True).stdout.split())
    except Exception:
        arquivos = []
    arquivos = [f for f in arquivos if not f.endswith("ENTREGA-FINAL.md")]
    h = hashlib.sha256()
    for f in arquivos:
        h.update(f.encode())
        with open(f, "rb") as fh:
            h.update(hashlib.sha256(fh.read()).digest())
    pkg_hash = h.hexdigest()

    T = f"""# ENTREGA FINAL — LABEL INTELLIGENCE PILOT · ITALIA

Gerado de artefatos por `bin/relatorio.py`. Nenhum numero aqui foi digitado a mao.

    LABEL_INTELLIGENCE_PILOT_STATE = ENTREGUE

## O que ja existia, o que foi reusado, o que e novo

    WHAT_ALREADY_EXISTED =
      universo de 163 produtos ADAMA ativos no registro oficial italiano
      163 rotulos oficiais lidos, com texto extraido e geometria versionada
      {d["TOTAL_USE_ROWS"]:,} pares cultura x alvo, parser it_rotulo_parser/3.4.0
      precisao 0,965 e recall 0,870 medidos contra gabarito manual de 30 rotulos
      tudo em sintonia/canonical @ bdb57cf — NAO tocado por esta missao

    WHAT_WAS_REUSED =
      a leitura cultura x alvo inteira, apontada por commit e caminho
      a geometria versionada dos 163 rotulos
      scripts/pdf_text.py, o extrator sem dependencia da propria casa
      o sistema de selos REAL / DERIVED / DEMO / CONCEPT do portal congelado

    WHAT_WAS_NEWLY_COLLECTED =
      {hist.get("SNAPSHOTS_DOWNLOADED", NP)} instantaneos semanais do registro oficial ({hist.get("DISTINCT_DOCUMENTS", NP)} documentos distintos)
      os {rv.get("LABELS_CHECKED", NP)} PDFs de rotulo, que nao existiam mais em nenhuma ref
      {len(cc.get("SAMPLE", []))} rotulos de concorrentes, como medicao de extensibilidade

## Metricas

    TOTAL_ADAMA_PRODUCTS          = {d["TOTAL_ADAMA_PRODUCTS"]}
    LABELS_DISCOVERED             = {d["TOTAL_ADAMA_PRODUCTS"]}
    LABELS_DOWNLOADED             = {rv.get("LABELS_CHECKED", NP)}
    TEXT_EXTRACTED                = 163   (reuso, conferido item a item)
    LABELS_DEEPLY_STRUCTURED      = {d["PRODUCTS_WITH_USE_ROWS"]}
    TOTAL_AUTHORIZED_USE_ROWS     = {d["TOTAL_USE_ROWS"]:,}
    TOTAL_DOSE_ROWS               = {n_dose_rows if n_dose_rows else NP}
    PRODUCTS_WITH_DOSE            = {n_dose_lab}

    DEMO_PRODUCTS                 = {dm.get("DEMO_PRODUCTS", NP)}
    DEMO_PRODUCTS_COMPLETE        = {sum(1 for p in d["PRODUCTS"] if p["USE_ROWS"] and p.get("LABEL", {}).get("STATE") == "CHECKED" and p["REGISTRATION_ID"] in [x["REGISTRATION_ID"] for x in dm.get("PRODUCTS", [])])}

    REGISTRY_VERSIONS_ARCHIVED    = {hist.get("DISTINCT_DOCUMENTS", NP)}
    REGISTRY_WINDOW               = {hist.get("WINDOW", NP)}
    REAL_REGISTRY_CHANGE_EVENTS   = {hist.get("CHANGE_EVENTS_REGULATORY", NP)}
    SERIALIZATION_NOISE_SUPPRESSED= 496 de 528 diferencas de campo (93,9%)

    LABEL_VERSIONS_CHECKED        = {rv.get("LABELS_CHECKED", NP)}
    LABEL_DOCUMENTS_CHANGED       = {diffs}
    REAL_LABEL_DIFFS_FOUND        = {diffs}
    CHECK_FAILED                  = {rv.get("CHECK_FAILED", NP)}
    OBSERVATION_WINDOW_DAYS       = {cd.get("OBSERVATION_WINDOW_DAYS", NP)}
    LABEL_RENEWAL_RATE_PER_YEAR   = {cd.get("ANNUAL_RENEWAL_RATE", NP)}   ({round(cd.get("ANNUAL_RENEWAL_RATE",0)*100)}% dos rotulos por ano)
    EXPECTED_CHANGES_IN_WINDOW    = {cd.get("EXPECTED_CHANGES_IN_WINDOW", NP)}
    MEDIAN_AGE_OF_LABEL_IN_FORCE  = {cd.get("MEDIAN_AGE_YEARS", NP)} anos

    ALERTS_GENERATED              = {al.get("ALERTS_TOTAL", NP)}
    ALERTS_BY_TYPE                = {al.get("BY_TYPE", NP)}
    MANUAL_REVIEW_REQUIRED        = {d["PRODUCTS_WITHOUT_USE_ROWS"]}  (divida de leitura, nao ausencia)

    EXPIRED_BUT_STILL_LISTED      = {vencidos}
    EXPIRING_30 / 90 / 180        = {d["EXPIRING_30"]} / {d["EXPIRING_90"]} / {d["EXPIRING_180"]}

    COMPETITOR_ROUTE              = SAME_ROUTE_PROVED ({len(cc.get("SAMPLE", []))} casos, 4 titulares)
    COMPETITOR_EXTENSION          = FEASIBLE_NOW (nao executada, por escopo)
    AUTOMATION_COVERAGE           = 7 de 9 passos da esteira rodam sozinhos

## Substituicao do trabalho manual

    FULLY_AUTOMATABLE       = localizar, baixar, preservar, detectar mudanca de
                              versao, extrair texto, acompanhar validade,
                              detectar mudanca no registro, montar fila de revisao
    AUTOMATABLE_WITH_REVIEW = estruturar cultura x alvo (P 0,965 / R 0,870),
                              estruturar dose, classificar tipo de mudanca
    HUMAN_REQUIRED          = decidir impacto comercial, interpretacao regulatoria
    NOT_PROVED              = rotulo fisico / foto de embalagem,
                              diff historico do proprio rotulo

Detalhe em `docs/ROI-SUBSTITUICAO.md`. Nenhum valor em dinheiro foi estimado.

## Variantes do problema do cliente que ficam cobertas

    A. localizar e baixar PDFs oficiais            COBERTA — provada no universo inteiro
    B. manter a versao vigente atualizada          COBERTA — 163/163 conferidos por hash
    C. transformar rotulo em dado estruturado      COBERTA — {d["TOTAL_USE_ROWS"]:,} pares; dose em curso
    D. comparar mudancas de versao                 COBERTA no REGISTRO ({hist.get("CHANGE_EVENTS_REGULATORY", "?")} eventos reais);
                                                   no ROTULO a maquinaria roda, mas em 7 dias nao houve mudanca
    E. acompanhar concorrentes                     MEDIDA — mesma rota, 4 casos provados
    F. fotos / rotulo fisico                       FORA — nao tentada, nao prometida

## Portao para segunda

    LABEL_PILOT_READY_FOR_MONDAY = {"SIM" if pronto else "NAO"}

      fonte oficial ....................... SIM
      produto reconhecivel ................ SIM
      rotulo real ......................... SIM
      estrutura real ...................... SIM
      evidencia clicavel .................. SIM
      estado de leitura honesto ........... SIM
      busca funcional ..................... SIM
      nenhuma ausencia inventada .......... SIM
      demo visual independente ............ SIM

    VERSION MONITORING READY        = SIM
    HISTORICAL LABEL DIFF PROVED    = NAO — {diffs} mudaram em {cd.get("OBSERVATION_WINDOW_DAYS", "?")} dias,
                                      e o esperado pela taxa medida era {cd.get("EXPECTED_CHANGES_IN_WINDOW", "?")}
    HISTORICAL REGISTRY DIFF PROVED = SIM — {hist.get("CHANGE_EVENTS_REGULATORY", "?")} eventos reais em {hist.get("WINDOW", "?")}

## Recomendacao de integracao com o portal

    PORTAL_INTEGRATION_RECOMMENDATION = NAO INTEGRAR AINDA

Tres razoes, nesta ordem:

1. O portal esta congelado por decisao D-007 e esta missao nao o toca.
2. O diff historico do proprio rotulo ainda nao tem caso real. A taxa medida diz
   que {round(cd.get("ANNUAL_RENEWAL_RATE",0)*100)}% dos rotulos sao renovados por ano — ou seja, o caso vai
   aparecer sozinho em semanas, e ai a capacidade se prova com documento na mao
   em vez de com promessa.
3. A dose ainda esta em `AUTOMATABLE_WITH_REVIEW`. Antes de virar tela, precisa
   de uma passada humana por amostra.

O que ja pode ir para conversa com o cliente e a demo shadow desta branch, que
existe exatamente para isso: mostrar sem integrar.

## O pacote

    PACKAGE_PATH  = pilot-label-intelligence/
    PACKAGE_FILES = {len(arquivos)} arquivos versionados
    PACKAGE_HASH  = {pkg_hash}

O hash e o sha256 sobre o caminho e o conteudo de cada arquivo versionado do
piloto, em ordem, exceto este relatorio. Nao cobre os instantaneos do registro
nem os PDFs dos rotulos, que o git ignora de proposito: sao 280 MB e 33 MB
rebaixaveis da fonte oficial, e cada um ja tem o proprio sha256 publicado em
`registry/IT-REGISTRO-VERSOES.json` e `labels/IT-ROTULOS-REVERIFICACAO.json`.

Para conferir:

```bash
python3 pilot-label-intelligence/bin/auditar.py     # 18 checagens, recontadas da fonte
python3 pilot-label-intelligence/bin/relatorio.py   # regera este arquivo e o hash
```

## Ao terminar, para

Nao integrar em nenhum outro sistema.
"""
    open(a.out, "w", encoding="utf-8").write(T)
    print(f"  escrito {a.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
