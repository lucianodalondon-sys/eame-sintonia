#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A TRAVA DO BANCO DESCARTÁVEL — um dono, e ele vive no runtime.

POR QUE ISTO EXISTE
-------------------
Até 2026-09-17 a única trava que sabia dizer «este endereço é um banco que
nasce e morre com a prova» vivia em `provas/preservar_coleta_no_postgres.py`.
Uma segunda, mais fraca, vivia em `provas/a_sala_sobrevive_ao_processo.py` e
procurava pedaços de texto. E o runtime — a porta de linha de comando do
orquestrador — não tinha trava nenhuma, porque não ligava banco nenhum.

O replay canário pelo workflow real (run 35215565657, know-how §132) provou o
preço: o workflow criava e migrava um PostgreSQL descartável, e a corrida
nunca lhe escrevia uma linha. Para o runtime passar a ligar o banco, ele
precisa de uma trava — e a trava não pode vir de `provas/`:

    PROVA NÃO É RUNTIME. RUNTIME NÃO IMPORTA PROVA.

Por isso a trava mudou de casa. `provas/` importa daqui; nunca o contrário.

O QUE ELA EXIGE, E COMO
-----------------------
Ela **decompõe** a URL. Não procura `localhost` no meio do texto — um host
`localhost.atacante.example` contém `localhost`, e um servidor `db.exemplo.com`
contém `db.`. Comparar pedaços de texto onde se devia comparar estrutura é
conferir um passaporte pelas letras que aparecem nele.

    scheme      postgres | postgresql
    hostname    EXATAMENTE um dos locais (lista de PERMISSÃO)
    database    EXATAMENTE um dos nomes descartáveis (lista de PERMISSÃO)
    query       não pode apontar a ligação para outro sítio

A última linha é a que faltava. A revisão independente da primeira coleta
(§6a) provou, com `psql` 16.4 real, que

    postgresql://p:x@localhost:54329/descartavel?host=db.X.supabase.co

passa uma trava que só olha para `hostname` — e a libpq liga ao `?host=`.
`host`, `hostaddr`, `service` e `dbname` na query são portas laterais para
outro sítio, e aqui fecham-se: `host`/`hostaddr` só podem repetir um local;
`service` (um ficheiro de serviço que pode dizer qualquer coisa) e `dbname`
(um segundo nome de banco, que a libpq prefere ao da morada) são recusados.
E as variáveis `PG*` que a libpq lê por baixo da URL saem do ambiente de
quem compõe — ver `AMBIENTE_QUE_MUDA_O_DESTINO` e `ambiente_sem_desvio()`.

É lista de PERMISSÃO, não de bloqueio. Bloqueio falha por omissão — basta
esquecer um nome. Permissão falha fechado, que é o lado certo para falhar.

    FALHA FECHADA POR OMISSÃO. PRODUÇÃO NÃO É LABORATÓRIO.
"""
from urllib.parse import parse_qs, urlparse

#: Os únicos hosts que uma bancada descartável pode ter. Sem `*.local`, sem
#: nomes de máquina: descartável é o que corre AQUI, ao lado de quem prova.
HOSTS_LOCAIS = ("localhost", "127.0.0.1", "::1", "[::1]")

#: Os ÚNICOS nomes de banco que esta casa aceita como descartáveis. São os que
#: os workflows criam e deitam fora; qualquer outro — sobretudo um chamado como
#: a produção — não passa. Acrescentar um nome aqui é uma decisão consciente, e
#: é esse o ponto: a lista é curta para que crescer doa.
#:   `social` entrou em 2026-09-08 (contrato de persistência social);
#:   `objeto` entrou em 2026-09-10 (migration 025, cópia ≠ observação).
#:   `sala` entrou em 2026-09-25 (SALA-AGUENTA): o passo 2b5 do
#:   `banco-descartavel.yml` cria o banco PROPRIO `sala` desde 2026-09-14 para a
#:   prova `a_sala_sobrevive_ao_processo.py`, e a lista de 2026-09-17 (497093a7)
#:   nao o trouxe — a prova recusava-se a correr (SystemExit 2) e o job ficou
#:   vermelho sem medir a Sala. Mesmo padrao de `derivado`/`social`/`objeto`:
#:   um nome por prova que assere contagens exactas. `sala_italia` (a Sala
#:   OPERACIONAL) continua FORA — o nome compara-se inteiro, nunca por pedaco.
BANCOS_PERMITIDOS = ("descartavel", "derivado", "social", "objeto", "sala")

#: Parâmetros de query que mudam PARA ONDE a libpq liga. `host` e `hostaddr`
#: só passam se repetirem um local; `service` e `dbname` nunca passam.
#: `dbname` entrou em 2026-09-17 pelo red team de arquitetura: a libpq deixa
#: escrever um SEGUNDO nome de banco na query e usa esse — a trava conferia o
#: nome escrito na morada, e `.../descartavel?dbname=postgres` ligava ao
#: `postgres`. Fica local, mas «local» não é «descartável».
QUERY_QUE_MUDA_O_DESTINO = ("host", "hostaddr", "service", "dbname")

#: As variáveis de ambiente que a libpq lê POR BAIXO da URL e que mudam o
#: destino: `PGHOSTADDR` vence o `host` da URL; `PGSERVICE`/`PGSERVICEFILE`
#: enchem o que a URL não fixou. A trava olha para a URL; o carteiro também lê
#: os bilhetes colados na parede. Quem compõe um runtime descartável tira-os
#: da parede ANTES de chamar o `psql` — ver `ambiente_sem_desvio()`.
#: `PGPASSWORD`/`PGPASSFILE` ficam: são credencial, não destino.
AMBIENTE_QUE_MUDA_O_DESTINO = ("PGHOST", "PGHOSTADDR", "PGPORT", "PGDATABASE",
                               "PGSERVICE", "PGSERVICEFILE", "PGOPTIONS")


class BancoNaoDescartavel(ValueError):
    """A URL não prova ser um banco descartável local. Fail closed."""


def porque_nao_e_descartavel(url) -> str:
    """O MOTIVO da recusa, ou `""` quando a URL é aceitável.

    Devolve texto e não booleano porque quem recusa tem de dizer porquê — e
    o motivo nunca repete a URL inteira, que pode trazer senha.
    """
    if not isinstance(url, str) or not url.strip():
        return "URL vazia"
    try:
        u = urlparse(url.strip())
    except ValueError:
        return "URL malformada"
    if u.scheme not in ("postgres", "postgresql"):
        return "scheme nao e postgres/postgresql"
    try:
        host = (u.hostname or "").lower()
    except ValueError:
        return "host malformado"
    if host not in HOSTS_LOCAIS:
        return "hostname nao e local"
    try:
        u.port  # um porto que nao e numero levanta aqui, e nao no psql
    except ValueError:
        return "porto malformado"
    banco = (u.path or "").lstrip("/")
    if banco not in BANCOS_PERMITIDOS:
        return "banco fora da lista descartavel"
    try:
        query = parse_qs(u.query or "", keep_blank_values=True,
                         strict_parsing=bool(u.query))
    except ValueError:
        return "query malformada"
    for chave, valores in query.items():
        c = chave.lower()
        if c in ("service", "dbname"):
            return "query '%s' aponta a ligacao para fora" % c
        if c in ("host", "hostaddr"):
            for v in valores:
                if v.strip().lower() not in HOSTS_LOCAIS:
                    return "query '%s' aponta a ligacao para fora" % c
    return ""


def e_descartavel(url) -> bool:
    """`True` só quando a URL prova, por estrutura, ser descartável e local."""
    return porque_nao_e_descartavel(url) == ""


def exigir_descartavel(url) -> str:
    """A URL, se for descartável. Senão levanta `BancoNaoDescartavel`."""
    motivo = porque_nao_e_descartavel(url)
    if motivo:
        raise BancoNaoDescartavel(
            "RECUSADO: a URL nao prova ser um banco descartavel local (%s). "
            "PRODUCAO NAO E LABORATORIO." % motivo)
    return url.strip()


def ambiente_sem_desvio(env=None) -> tuple:
    """`(ambiente_limpo, nomes_retirados)`: o ambiente sem as variáveis que
    desviam a ligação da libpq. Não altera o que recebe; devolve uma cópia."""
    e = dict(__import__("os").environ if env is None else env)
    retiradas = tuple(n for n in AMBIENTE_QUE_MUDA_O_DESTINO if n in e)
    for n in retiradas:
        e.pop(n, None)
    return e, retiradas


def morada_sem_segredo(url) -> str:
    """`host:porto/banco`, sem utilizador nem senha — para o recibo e o log."""
    try:
        u = urlparse(url or "")
        porto = ":%s" % u.port if u.port else ""
        return "%s%s/%s" % (u.hostname or "?", porto, (u.path or "").lstrip("/"))
    except ValueError:
        return "?"
