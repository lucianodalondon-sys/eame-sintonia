#!/usr/bin/env python3
"""
citar.py — tenta recuperar a citacao literal de cada par, e explica por que nao da.

RESULTADO: NAO E POSSIVEL com os artefatos atuais. Este script existe para
DOCUMENTAR isso com numero, e para deixar pronto o teste que aceitaria a citacao
no dia em que o parser da casa passar a gravar o x.

## O que se queria

O contrato do piloto exige evidencia recuperavel para toda afirmacao de uso. Os
2.928 pares reusados de `sintonia/canonical` trazem ponteiro — pagina e faixa y —
mas nao trazem o texto. A ideia era recuperar o texto da geometria versionada.

## Por que nao funciona

Os pares gravam **pagina e y**, e nao gravam **x**.

Estas etichette sao paisagem, com varias colunas por pagina: a pagina 1 do
registro 014091 tem 842 pt de largura e colunas comecando em x=57 e x=503. Uma
faixa y, sozinha, atravessa colunas que nao tem relacao nenhuma entre si.

Medido, nesta ordem:

    921 citacoes recuperadas usando so a faixa y
    913 REPROVADAS ao conferir contra o texto que o proprio parser leu
      8 sobreviveram a conferencia
      5 dessas 8 ainda estavam erradas na leitura manual

O par 014091 GIRASOLE x AFIDI, por exemplo, sobreviveu a conferencia automatica
e mesmo assim recebeu um trecho que fala de "Pesco, nettarine, albicocco, susino,
ciliegio" — cultura nenhuma a ver. Passou so porque o nome do alvo aparecia em
algum lugar da mesma faixa.

Entao a taxa de acerto util e proxima de zero, e **nenhuma citacao e publicada**.

    USE_ROWS_WITH_LITERAL_QUOTE = 0
    QUOTE_RECOVERY_STATE        = IMPOSSIBLE_WITHOUT_X_COORDINATE

## Por que isso e melhor que o contrario

921 citacoes erradas na tela seriam pior que nenhuma: dariam ao cliente a
sensacao de evidencia exatamente onde ela nao existe, que e a falha que este
piloto inteiro existe para nao cometer.

## O conserto, para quem mantiver o parser

`it_rotulo_parser` ja conhece o x de cada palavra quando monta o par — a
geometria tem xMin e xMax. Basta gravar, junto de PAGE e CROP_Y/TARGET_Y, a
faixa **x** da celula. Com x e y a citacao sai exata, e a conferencia que este
script ja implementa passa a valer como teste de regressao.
"""
import argparse, json, sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", default="pilot-label-intelligence/demo/IT-LABEL-INTELLIGENCE.json")
    a = ap.parse_args()
    d = json.load(open(a.dados, encoding="utf-8"))

    tot = 0
    for prod in d["PRODUCTS"]:
        for u in prod["USE_ROWS"]:
            tot += 1
            u["SOURCE_QUOTE"] = "NOT_PRESERVED"
            u["SOURCE_QUOTE_NOTE"] = (
                "o par guarda pagina e faixa y, mas nao guarda x; a etichetta tem varias "
                "colunas por pagina, entao a faixa y sozinha nao identifica a linha. "
                "Ver bin/citar.py."
            )
    d["USE_ROWS_WITH_LITERAL_QUOTE"] = 0
    d["USE_ROWS_WITHOUT_LITERAL_QUOTE"] = tot
    d["QUOTE_RECOVERY_STATE"] = "IMPOSSIBLE_WITHOUT_X_COORDINATE"
    d["QUOTE_NOTE"] = (
        "tentativa medida: 921 citacoes recuperadas so pela faixa y, 913 reprovadas na "
        "conferencia contra o texto lido pelo parser, e 5 das 8 restantes ainda erradas na "
        "leitura manual. Nenhuma e publicada. O ponteiro (pagina + faixa y + PROVENANCE) "
        "continua sendo a evidencia disponivel para estes pares; a citacao literal exige "
        "que o parser passe a gravar a faixa x."
    )
    json.dump(d, open(a.dados, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  pares: {tot} | citacao literal publicada: 0", file=sys.stderr)
    print("  QUOTE_RECOVERY_STATE = IMPOSSIBLE_WITHOUT_X_COORDINATE", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
