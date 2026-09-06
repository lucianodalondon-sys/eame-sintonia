#!/usr/bin/env python3
"""
dose_rodar.py — roda o extrator de dose sobre um conjunto de rotulos.

Emite IT-DOSES.json com uma entrada por rotulo, incluindo os que FALHARAM. Um
rotulo sem tabela lida aparece com PARSE_STATE, nunca desaparece da lista: sumir
da lista e a forma silenciosa de transformar falha de leitura em ausencia.
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dose_extrair


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdfdir", default="pilot-label-intelligence/labels/pdf")
    ap.add_argument("--dados", default="pilot-label-intelligence/demo/IT-LABEL-INTELLIGENCE.json")
    ap.add_argument("--demo", default="pilot-label-intelligence/demo/IT-DEMO-PRODUTOS.json",
                    help="se dado, roda so nos produtos da demo")
    ap.add_argument("--todos", action="store_true", help="roda no universo inteiro")
    ap.add_argument("--cachedir", default=None)
    ap.add_argument("--out", default="pilot-label-intelligence/demo/IT-DOSES.json")
    a = ap.parse_args()

    d = json.load(open(a.dados, encoding="utf-8"))
    nomes = {p["REGISTRATION_ID"]: p["PRODUCT"] for p in d["PRODUCTS"]}
    if a.todos:
        alvos = sorted(nomes)
    else:
        dm = json.load(open(a.demo, encoding="utf-8"))
        alvos = [x["REGISTRATION_ID"] for x in dm["PRODUCTS"]]

    labels, com, linhas, falhas = [], 0, 0, 0
    for reg in alvos:
        pdf = os.path.join(a.pdfdir, f"{reg}.pdf")
        if not os.path.exists(pdf):
            labels.append({"REGISTRATION_ID": reg, "PRODUCT": nomes.get(reg),
                           "PARSE_STATE": "PDF_NOT_ON_DISK", "ROWS": []})
            falhas += 1
            continue
        try:
            r = dose_extrair.extrair(pdf, reg, nomes.get(reg),
                                     cache=(os.path.join(a.cachedir, f"{reg}.xml")
                                            if a.cachedir else None))
        except Exception as e:
            r = {"REGISTRATION_ID": reg, "PRODUCT": nomes.get(reg),
                 "PARSE_STATE": "PARSER_ERROR", "ERROR": type(e).__name__,
                 "NOTE": str(e)[:200], "ROWS": []}
        labels.append(r)
        n = len(r.get("ROWS") or [])
        linhas += n
        com += bool(n)
        falhas += (not n)
        print(f'  {reg} {str(nomes.get(reg))[:24]:<24} {r["PARSE_STATE"]:<22} '
              f'linhas={n}', file=sys.stderr)

    out = {
        "DATASET": "IT-DOSES",
        "O_QUE_ISTO_E": "dose, unidade, intervalo e n max de aplicacoes lidos da etichetta oficial",
        "O_QUE_ISTO_NAO_E": ("nao substitui os pares cultura x alvo de canonical, que continuam "
                             "sendo a leitura de referencia. Dose e camada NOVA."),
        "SOURCE": "Ministero della Salute — etichetta oficial em PDF",
        "METHOD": "geometria (pdftotext -bbox-layout), colunas por x e linhas por y",
        "LABELS_ATTEMPTED": len(labels),
        "LABELS_WITH_ROWS": com,
        "LABELS_WITHOUT_ROWS": falhas,
        "TOTAL_DOSE_ROWS": linhas,
        "REGRA": ("rotulo sem linha lida continua na lista com PARSE_STATE. "
                  "PARSER_FAILURE != REGULATORY_ABSENCE."),
        "LABELS": labels,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f'\n  {com}/{len(labels)} rotulos com linha de dose | {linhas} linhas', file=sys.stderr)
    print(f'  escrito {a.out}', file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
