#!/usr/bin/env python3
"""
vigencia_etichetta.py — R-19. `NOT_PRESENT` na vigencia declarada pela etichetta
estava dizendo "o documento nao declara" onde o documento declara.

## O defeito, medido

A ficha do produto tem uma linha chamada "Vigencia declarada NA PROPRIA
etichetta". Ela so aparece quando o leitor acha a frase

    "valida dal 22 luglio 2024 al 18 novembre 2024"

que existe em **1** dos 163 rotulos. Nos outros 162 o campo sai `NOT_PRESENT`,
e `NOT_PRESENT` le-se **"nao esta no rotulo"**.

Medido no acervo, a forma que a etichetta italiana usa de verdade e outra:

    150 rotulos  "Etichetta autorizzata con ..."
    145 rotulos  "...decreto dirigenziale del <data>"
    112 rotulos  "...con validita dal <data>"          <- a data de vigencia
    112 rotulos  "...modificata ai sensi dell'art. 7, comma 1, D.P.R. n. 55/2012"
      1 rotulo   "valida dal <data> al <data>"          <- a unica que era lida

Ou seja: **112 rotulos declaram desde quando a etichetta vale, e a ferramenta
dizia que nao declaravam.** Isso e `PARSER_FAILURE` sendo publicado como
`REGULATORY_ABSENCE`, que e a lei que este produto mais repete.

## O que esta regra faz — e o que ela recusa fazer

Ela **nao parseia a data**. Poderia: "con validita dal 28.12.2022" e um padrao
limpo. Mas o campo se chama "vigencia declarada" e teria de significar a mesma
coisa que significa hoje na unica ficha que o exibe, e nao ha nada no acervo que
prove que a data do "modificata ai sensi ... con validita dal" e o mesmo fato que
a data do "valida dal ... al ...". Inventar essa equivalencia para preencher um
campo vazio e exatamente o movimento que a LEI ZERO proibe.

Entao ela faz o que da para provar: acha a frase, guarda a **citacao literal**
(cortada no salto de coluna, para nao virar remontagem) e devolve o estado com
nome proprio:

    VALIDITY_WINDOW_READ                a forma "valida dal X al Y" foi lida
    VALIDITY_PHRASE_PRESENT_FORM_NOT_READ
                                        o rotulo declara vigencia numa forma que
                                        este leitor nao estrutura — e aqui esta
                                        a frase, para a pessoa ler
    VALIDITY_PHRASE_NOT_FOUND           nenhuma das formas conhecidas aparece
    VALIDITY_NOT_CHECKED                nao ha texto

A tela passa a mostrar a frase. Quem precisa da data le a frase; o que a
ferramenta nao faz e afirmar que a data nao existe.
"""
import argparse, json, os, re, subprocess, sys, unicodedata
from collections import Counter

# Formas medidas no acervo, com o numero de rotulos em que cada uma ocorre.
FORMAS = [
    (r"valid[ao]\s+dal\s+\d{1,2}\s+\w+\s+\d{4}\s+al\s+\d{1,2}\s+\w+\s+\d{4}",
     "valida dal X al Y", 1, True),
    (r"con\s+validit[aà]\s+dal\s+[\d./-]+", "con validita dal X", 112, False),
    (r"decreto\s+dirigenziale\s+del\s+[\d\w./ ]{4,24}", "decreto dirigenziale del X", 145, False),
    (r"etichetta\s+autorizzata\s+con\s+[^\"”]{0,60}", "etichetta autorizzata con X", 150, False),
]
RX_SALTO = re.compile(r"\n|   +")
JANELA = 120


def sa(s):
    s = unicodedata.normalize("NFD", str(s or ""))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def texto(reg, pdfs, cache, modo=("-layout",), suf="layout"):
    os.makedirs(cache, exist_ok=True)
    alvo = os.path.join(cache, f"{reg}.{suf}.txt")
    if not os.path.exists(alvo) or os.path.getsize(alvo) == 0:
        pdf = os.path.join(pdfs, f"{reg}.pdf")
        if not os.path.exists(pdf):
            return None
        try:
            subprocess.run(["pdftotext"] + list(modo) + [pdf, alvo], check=True,
                           capture_output=True, timeout=180)
        except Exception:
            return None
    try:
        return open(alvo, encoding="utf-8", errors="replace").read()
    except OSError:
        return None


def citacao(t, m):
    """O trecho em volta do achado, cortado no salto de coluna dos dois lados."""
    ini, fim = m.start(), m.end()
    s_ = RX_SALTO.search(t[max(0, ini - JANELA):ini][::-1])
    a = ini - (s_.start() if s_ else min(ini, JANELA))
    s_ = RX_SALTO.search(t[fim:fim + JANELA])
    b = fim + (s_.start() if s_ else min(len(t) - fim, JANELA))
    return re.sub(r"\s+", " ", t[a:b]).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pacote", default="v1/dados/COLLECTION-PACKAGE.json")
    ap.add_argument("--pdfs", default="pilot-label-intelligence/labels/pdf")
    ap.add_argument("--cache", default="/tmp/nomecache")
    ap.add_argument("--out", default="v1/dados/VIGENCIA-ETICHETTA.json")
    a = ap.parse_args()

    regs = [i["REGISTRATION_ID"] for i in
            json.load(open(a.pacote, encoding="utf-8"))["ITEMS"]]
    ver = {}
    cont = Counter()
    for reg in regs:
        bruto = texto(reg, a.pdfs, a.cache)
        if bruto is None:
            ver[reg] = {"STATE": "VALIDITY_NOT_CHECKED", "QUOTE": None, "FORM": None}
            cont["VALIDITY_NOT_CHECKED"] += 1
            continue
        t = sa(bruto)
        achado = None
        for pat, nome, _n, estruturada in FORMAS:
            m = re.search(pat, t, re.I)
            if m:
                achado = (nome, estruturada, citacao(bruto, m))
                break
        if achado is None:
            est = "VALIDITY_PHRASE_NOT_FOUND"
            ver[reg] = {"STATE": est, "QUOTE": None, "FORM": None}
        else:
            nome, estruturada, cit = achado
            est = ("VALIDITY_WINDOW_READ" if estruturada
                   else "VALIDITY_PHRASE_PRESENT_FORM_NOT_READ")
            ver[reg] = {"STATE": est, "QUOTE": cit, "FORM": nome}
        cont[est] += 1

    saida = {
        "DATASET": "V1-VIGENCIA-ETICHETTA",
        "RULE_ID": "R-19",
        "O_QUE_ISTO_E": ("a etichetta declara desde quando ela vale? em que forma, e com que "
                         "frase literal"),
        "O_QUE_ISTO_NAO_E": ("nao parseia a data das formas nao estruturadas: nada no acervo prova "
                             "que a data do 'modificata ai sensi ... con validita dal' e o mesmo "
                             "fato que a do 'valida dal X al Y'"),
        "FORMS_MEASURED": {n: c for _p, n, c, _e in FORMAS},
        "COUNTS": dict(cont.most_common()),
        "VERDICT": ver,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(saida, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in cont.most_common():
        print(f"  {v:5}  {k}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
