#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A ORDEM DOS ARGUMENTOS DO PSQL — a DSN vem POR ÚLTIMO, em toda a casa.

    py -m unittest tests.test_psql_argv

POR QUE ISTO É UMA LEI E NÃO UM ESTILO
--------------------------------------
O `getopt` da glibc PERMUTA: acha as opções onde quer que estejam, e por isso
`psql <dsn> -c <sql>` sempre funcionou no Linux e no CI. O `getopt` do Windows
NÃO permuta: parado o primeiro argumento posicional, tudo o que vem depois
deixa de ser opção.

Provado em PostgreSQL 16.4 real nesta máquina (2026-09-16):

    psql -X -q -A -t -c 'select 1;' <DSN>   ->  "1"                      rc=0
    psql <DSN> -X -q -A -t -c 'select 1;'   ->  6x "extra ... ignored"   rc=0
    psql <DSN> -X ... -f ficheiro.sql       ->  idem                     rc=0

    ELE NÃO FALHA. SAI COM ZERO SEM TER FEITO NADA — LEITURA E ESCRITA.

E sem o stdin fechado fica PRESO à espera de senha, porque com a DSN à frente
até o `-w` deixa de ser opção.

O QUE ESTE TESTE MEDE, E COMO
-----------------------------
Não é grep de uma linha — essa medição já produziu a resposta invertida duas
vezes, porque as opções do início cabem no corte e a DSN fica três linhas
abaixo. Aqui a chamada é decomposta por AST:

    para toda lista literal que começa por "psql":
        um elemento NÃO-LITERAL (variável, atributo, chamada, f-string)
        só pode aparecer NA ÚLTIMA POSIÇÃO,
        ou imediatamente depois de uma opção que recebe valor.

Uma variável no meio da lista sem opção-mãe é a DSN adiantada — o defeito.
O SQL passado como variável (`-c`, sql) tem opção-mãe e passa.

E para shell (`.sh`, `.yml`): `psql "$VAR"` — o psql imediatamente seguido de
variável entre aspas — é a DSN à frente, e reprova.

    LER METADE DA CHAMADA E DIZER QUE SE MEDIU A CHAMADA
    É ADIVINHAR COM AR DE MEDIR.
"""
import ast
import io
import os
import re
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Opções do psql que RECEBEM um valor no argumento seguinte. Um elemento
#: não-literal imediatamente depois de uma destas é o valor dela (o SQL de
#: `-c`, o ficheiro de `-f`), e não a DSN adiantada.
OPCOES_COM_VALOR = {"-c", "-f", "-F", "-R", "-v", "-o", "-U", "-h", "-p",
                    "-d", "-P", "-L", "-T", "--command", "--file"}

#: Letras curtas que recebem valor — para flags COMBINADAS. `-tAc` é `-t -A
#: -c` e o argumento seguinte é o SQL do `-c`; sem isto o detector marcava o
#: SQL como DSN adiantada e um codemod chegou a rodar em círculo por causa
#: disso. A ÚLTIMA letra decide: só ela pode consumir o argumento seguinte.
LETRAS_COM_VALOR = set("cfFRvoUhpdPLT")


def _recebe_valor(flag):
    if flag in OPCOES_COM_VALOR:
        return True
    return (len(flag) > 1 and flag.startswith("-")
            and not flag.startswith("--") and flag[-1] in LETRAS_COM_VALOR)

#: Onde se mede. Código de runtime e provas — tudo o que chama o psql.
PASTAS_PY = ("admissao", "guarda", "coleta", "leis", "regras", "medidas",
             "orquestrador", "pedido", "motor", "provas", "tests",
             "portoes", "superficie", "candidatas", "fontes", "controle")

#: Shell e workflows que correm nesta casa.
SHELL_GLOBS = ("motor", os.path.join(".github", "workflows"))

#: `psql` imediatamente seguido de variável entre aspas = DSN à frente.
PADRAO_SHELL_MAU = re.compile(r'\bpsql(?:\.exe)?\s+"\$')


def _e_literal(no):
    return isinstance(no, ast.Constant) and isinstance(no.value, str)


def violacoes_python(caminho):
    """As chamadas psql deste ficheiro com um não-literal fora do lugar."""
    try:
        arvore = ast.parse(io.open(caminho, encoding="utf-8").read())
    except (SyntaxError, UnicodeDecodeError):
        return []
    fora = []
    for no in ast.walk(arvore):
        if not isinstance(no, ast.List) or not no.elts:
            continue
        primeiro = no.elts[0]
        if not (_e_literal(primeiro) and primeiro.value == "psql"):
            continue
        ultimo = len(no.elts) - 1
        for i, e in enumerate(no.elts[1:], 1):
            if _e_literal(e):
                continue                      # literais nunca são a DSN errada
            if i == ultimo:
                continue                      # última posição é o lugar da DSN
            anterior = no.elts[i - 1]
            if _e_literal(anterior) and _recebe_valor(anterior.value):
                continue                      # é o valor de uma opção
            fora.append((no.lineno, i))
    return fora


def violacoes_shell(caminho):
    """Onde a doença morde: shell que corre (ou pode correr) no Windows.

    Os workflows que declaram `runs-on: ubuntu-*` e nenhum runner Windows
    ficam DE FORA de propósito, e isso não é perdão: a glibc permuta as
    opções e a ordem antiga funciona lá. Um `.yml` que declare um runner
    `Windows`/`self-hosted` entra na guarda — e no dia em que um workflow
    de ubuntu migrar para Windows, ele entra sozinho, porque o critério é
    lido do próprio ficheiro e não de uma lista aqui.

    Os `.sh` de `motor/` entram SEMPRE: são chamados desta máquina Windows.
    """
    texto = io.open(caminho, encoding="utf-8", errors="replace").read()
    if caminho.endswith((".yml", ".yaml")):
        corre_em_windows = ("Windows" in texto and "self-hosted" in texto)
        if not corre_em_windows:
            return []
    linhas = []
    for n, linha in enumerate(texto.split("\n"), 1):
        if PADRAO_SHELL_MAU.search(linha):
            linhas.append(n)
    return linhas


def censo():
    maus = {}
    for pasta in PASTAS_PY:
        base = os.path.join(RAIZ, pasta)
        for raiz, dirs, ficheiros in os.walk(base):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in ficheiros:
                if not f.endswith(".py"):
                    continue
                p = os.path.join(raiz, f)
                v = violacoes_python(p)
                if v:
                    maus[os.path.relpath(p, RAIZ)] = v
    for pasta in SHELL_GLOBS:
        base = os.path.join(RAIZ, pasta)
        if not os.path.isdir(base):
            continue
        for raiz, dirs, ficheiros in os.walk(base):
            for f in ficheiros:
                if not f.endswith((".sh", ".yml", ".yaml")):
                    continue
                p = os.path.join(raiz, f)
                v = violacoes_shell(p)
                if v:
                    maus[os.path.relpath(p, RAIZ)] = v
    return maus


class ADsnVemPorUltimo(unittest.TestCase):

    maxDiff = None

    def test_nenhuma_chamada_psql_com_a_dsn_adiantada(self):
        """Zero tolerância: qualquer DSN antes das opções reprova, com o sítio."""
        maus = censo()
        linhas = ["%s -> %s" % (k, v) for k, v in sorted(maus.items())]
        self.assertEqual(maus, {},
                         "psql com a DSN antes das opcoes — no Windows isto "
                         "sai com rc=0 SEM EXECUTAR NADA:\n  " +
                         "\n  ".join(linhas))

    def test_o_detector_apanha_o_padrao_errado(self):
        """A guarda morde: o padrão historicamente errado é detectado."""
        mau = "x = [\"psql\", url, \"-q\", \"-c\", sql]\n"
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                         encoding="utf-8") as fh:
            fh.write(mau)
            nome = fh.name
        try:
            self.assertTrue(violacoes_python(nome),
                            "o detector deixou passar a DSN adiantada")
        finally:
            os.unlink(nome)

    def test_o_detector_aceita_o_padrao_certo(self):
        bom = ("x = [\"psql\", \"-X\", \"-q\", \"-A\", \"-t\", \"-F\", sep,\n"
               "     \"-v\", \"ON_ERROR_STOP=1\", \"-c\", sql, url]\n")
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                         encoding="utf-8") as fh:
            fh.write(bom)
            nome = fh.name
        try:
            self.assertEqual(violacoes_python(nome), [],
                             "o detector reprovou a ordem correcta")
        finally:
            os.unlink(nome)

    def test_o_detector_de_shell_apanha_e_aceita(self):
        self.assertTrue(PADRAO_SHELL_MAU.search('psql "$URL" -v x -q -c "y"'))
        self.assertTrue(PADRAO_SHELL_MAU.search('out=$(psql "$URL" -tAc "z")'))
        self.assertFalse(PADRAO_SHELL_MAU.search(
            'psql -v ON_ERROR_STOP=1 -q -c "y" "$URL"'))


if __name__ == "__main__":
    unittest.main()
