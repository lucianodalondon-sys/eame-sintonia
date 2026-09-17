#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QUAL `psql` ESTE PROCESSO USA — um dono, uma variável, falha fechada.

O DEFEITO QUE ISTO FECHA
------------------------
O replay canário 3 pelo workflow real (run GitHub 35232024024, 2026-09-17,
know-how §135) atravessou os três portões — bancada descartável, Sala,
egresso IT — adquiriu IT-T3-002 da rede e caiu na PRIMEIRA chamada do runtime
ao banco:

    guarda/memoria_postgres.py:117   subprocess.run(["psql", …])
    → FileNotFoundError: [WinError 2]

Três donos do runtime (`MemoriaPostgres`, `coleta_checkpoint.Banco`, a Sala
`_Postgres`) lançavam `"psql"` pelo nome e confiavam no PATH do processo. O
workflow escrevia a pasta do psql no `GITHUB_PATH`; o Python do passo 6 não a
viu. O mecanismo exato dessa diferença NÃO ficou provado (know-how §135, ponto
5) — e não precisa de ficar para a lição valer:

    DESCOBERTA IMPLÍCITA POR PATH NÃO É UM CONTRATO.
    QUEM CRIA A BANCADA SABE ONDE ESTÁ O psql. QUE O DIGA.

O CONTRATO
----------
    SINTONIA_PSQL_EXE   caminho NATIVO do executável, tal como o processo
                        Python o consegue abrir (Windows: `C:/…/psql.exe` ou com barras invertidas;
                        `/c/…` NÃO é nativo para o CreateProcess e recusa-se).

Resolução, por esta ordem e sem terceira via:

    1  a variável existe → o ficheiro tem de existir E chamar-se `psql`
       (`psql.exe`); usa-se EXATAMENTE ele. Inválida = recusa. NUNCA se cai
       para o PATH por cima de uma declaração explícita errada: isso
       mascararia um erro de configuração com um acerto por acaso.
    2  a variável não existe → `shutil.which("psql")`, para o ambiente que já
       tem o cliente no PATH (a máquina de quem desenvolve, o CI Linux).
    3  nada → `ClientePostgresAusente`, com a frase que diz o que declarar.

Nunca: inventar caminho, instalar software, descarregar PostgreSQL, cair para
produção. Este dono não sabe o que é uma DSN e não decide para onde se liga —
isso é de `guarda/banco_descartavel.py` e de quem compõe o runtime.

SEM EFEITO NO IMPORT
--------------------
Importar não lê ambiente nem toca no disco. Tudo acontece em `resolver_psql()`,
com o ambiente que lhe derem — e é isso que a torna testável sem banco.
"""
import os
import shutil

#: A ÚNICA variável que declara o cliente. Ver o cabeçalho.
VARIAVEL = "SINTONIA_PSQL_EXE"

#: Os nomes que um executável tem de ter para ser aceite como o psql.
NOMES_ACEITES = ("psql", "psql.exe")


class ClientePostgresAusente(RuntimeError):
    """Não há `psql` utilizável por este processo. Fail closed."""


def porque_nao_serve(caminho) -> str:
    """O MOTIVO de um caminho declarado não servir, ou `""` quando serve.

    Devolve texto e não booleano porque quem recusa tem de dizer porquê.
    """
    c = (caminho or "").strip()
    if not c:
        return "caminho vazio"
    if len(c) > 2 and c[0] == "/" and c[1].isalpha() and c[2] == "/":
        # `/c/Users/...` é a forma POSIX do MSYS para uma unidade Windows; o
        # CreateProcess não a lê. `/usr/bin/psql` (Linux) não cai aqui.
        return "caminho em forma POSIX (/c/...), nao nativo"
    if not os.path.isabs(c):
        # relativo resolve-se contra o cwd de CADA subprocesso: dois processos,
        # dois psql. Nativo e completo, ou nada.
        return "caminho relativo, nao absoluto"
    if not os.path.isfile(c):
        return "ficheiro nao existe"
    if os.path.basename(c).lower() not in NOMES_ACEITES:
        return "o ficheiro nao se chama psql"
    return ""


def resolver_psql(env=None) -> str:
    """O caminho do `psql` que este processo deve usar. Ver o cabeçalho.

    → o caminho declarado em `SINTONIA_PSQL_EXE`, se serve;
    → levanta `ClientePostgresAusente` se está declarado e não serve;
    → `shutil.which("psql")` se nada está declarado e o PATH o tem;
    → levanta `ClientePostgresAusente` se não há nenhum.
    """
    e = os.environ if env is None else env
    declarado = (e.get(VARIAVEL) or "").strip()
    if declarado:
        motivo = porque_nao_serve(declarado)
        if motivo:
            raise ClientePostgresAusente(
                "%s esta declarada e nao serve (%s): %r. Nao se cai para o PATH "
                "por cima de uma declaracao explicita. Corrija a declaracao."
                % (VARIAVEL, motivo, declarado))
        return declarado
    achado = shutil.which("psql", path=e.get("PATH") if env is not None else None)
    if achado:
        return achado
    raise ClientePostgresAusente(
        "nenhum psql: %s nao esta declarada e o PATH deste processo nao tem "
        "`psql`. Declare %s com o caminho NATIVO do executavel (Windows: "
        "C:\\...\\psql.exe). Nada e inventado, nada e instalado." % (VARIAVEL, VARIAVEL))


def comando_psql(*argumentos, env=None) -> list:
    """`[<psql resolvido>, *argumentos]` — a cabeça da lista vem daqui, e a
    ordem dos argumentos continua a ser lei de `tests/test_psql_argv.py`
    (opções primeiro, DSN por último)."""
    return [resolver_psql(env), *argumentos]


def como_foi_resolvido(env=None) -> dict:
    """Para recibos e portões: de onde veio o psql, sem levantar."""
    e = os.environ if env is None else env
    declarado = (e.get(VARIAVEL) or "").strip()
    try:
        caminho = resolver_psql(env)
    except ClientePostgresAusente as ex:
        return {"PSQL": None, "ORIGEM": "AUSENTE", "PORQUE": str(ex),
                "DECLARADO": declarado or None}
    return {"PSQL": caminho, "ORIGEM": "DECLARADO" if declarado else "PATH",
            "PORQUE": "", "DECLARADO": declarado or None}
