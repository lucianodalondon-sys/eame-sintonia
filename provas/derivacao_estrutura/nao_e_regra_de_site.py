#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA «NÃO É REGRA PARA A XYLELLA» — DERIVACAO-ESTRUTURA-V2 (28/09).

Lê o diff de `coleta/` entre o vivo (`e24139702`) e a árvore, fica só com as linhas
ACRESCENTADAS que são CÓDIGO (tokenizador do Python: fora comentários e strings de
várias linhas) e procura nelas nome de site, domínio, URL, CREA, Xylella, balsâmico
ou código de fonte (`IT-T…`). Tem de dar 0.

    py provas/derivacao_estrutura/nao_e_regra_de_site.py

Só leitura (git diff + leitura dos ficheiros). Sai com código ≠ 0 se achar alguma.
"""
import io
import os
import re
import subprocess
import sys
import tokenize

sys.dont_write_bytecode = True

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = "e24139702b8216ad54127cf63a14b550bcd4aeab"
PADRAO = re.compile(r"crea|xylella|balsamic|consorzio|https?:|www\.|\.it\b|IT-T\d|"
                    r"dominio|hostname|netloc|urlparse", re.I)


def linhas_acrescentadas():
    diff = subprocess.run(["git", "diff", "-U0", BASE, "--", "coleta/"], cwd=RAIZ,
                          capture_output=True, text=True, encoding="utf-8").stdout
    novas, f = {}, None
    for l in diff.splitlines():
        if l.startswith("+++ b/"):
            f = l[6:]
            novas[f] = set()
        m = re.match(r"@@ -\S+ \+(\d+)(?:,(\d+))? @@", l)
        if m and f:
            a, n = int(m.group(1)), int(m.group(2) or 1)
            novas[f].update(range(a, a + n))
    return novas


def linhas_de_codigo(src):
    codigo = set()
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                        tokenize.INDENT, tokenize.DEDENT):
            continue
        if tok.type == tokenize.STRING and tok.start[0] != tok.end[0]:
            continue  # docstring / texto de várias linhas
        codigo.update(range(tok.start[0], tok.end[0] + 1))
    return codigo


def main():
    total, achados, em_comentario = 0, [], 0
    for f, ls in sorted(linhas_acrescentadas().items()):
        if not f.endswith(".py"):
            continue
        with open(os.path.join(RAIZ, f), encoding="utf-8") as fh:
            src = fh.read()
        linhas, codigo = src.split("\n"), linhas_de_codigo(src)
        for n in sorted(ls):
            if n not in codigo:
                em_comentario += bool(PADRAO.search(linhas[n - 1]))
                continue
            total += 1
            if PADRAO.search(linhas[n - 1]):
                achados.append("%s:%d: %s" % (f, n, linhas[n - 1].strip()))
    print("BASE %s · coleta/ · padrao %s" % (BASE[:9], PADRAO.pattern))
    print("LINHAS_DE_CODIGO_ACRESCENTADAS %d · CITAM_SITE %d · (em comentario/docstring: %d, "
          "que contam de onde veio a medida)" % (total, len(achados), em_comentario))
    for a in achados:
        print("  " + a)
    return 1 if achados else 0


if __name__ == "__main__":
    raise SystemExit(main())
