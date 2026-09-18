#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A BANCADA OPERACIONAL DA COLLECTION — persistente, e por isso NAO descartavel.

    ALLOWLIST EXPLICITA > HEURISTICA DE BLOQUEIO.

POR QUE ESTE FICHEIRO NASCEU
----------------------------
O primeiro canario operacional real (IT-T3-010, run
`XX-T3-2026-09-18-130704-dfbbd422a1b06e7c`) adquiriu o PDF, preservou os bytes
— e parou. Medido:

    RAW BYTES        YES
    RAW_OBSERVATION  NO      <- nenhum `raw_asset`
    DERIVED          NO      <- sem observacao nao ha sujeito
    ADMISSION        NAO_SEI <- «o item veio sem texto nenhum»
    READY            0

A causa nao era defeito: `orquestrador/persistencia.py` so liga a memoria da
Collection quando existe `BANCO_DESCARTAVEL_URL`, e `guarda/banco_descartavel.py`
recusou `sala_italia` — **correctamente**, porque `sala_italia` NAO e um banco
descartavel.

    A CASA TINHA BANCADA DESCARTAVEL E TINHA SALA.
    NAO TINHA BANCADA OPERACIONAL DA COLLECTION.

⚠️ O QUE NAO SE FEZ, E PORQUE
-----------------------------
NAO se acrescentou `sala_italia` a `BANCOS_PERMITIDOS`. Essa lista chama-se
«descartaveis» e e lida por provas que existem para **nunca** correr contra
nada que sobreviva. Por um nome nela, um banco operacional passaria a ser
elegivel para bancadas que apagam o que tocam.

    UM BANCO QUE SOBREVIVE NUMA LISTA CHAMADA «DESCARTAVEL»
    E UMA MENTIRA QUE SO SE DESCOBRE QUANDO ALGUEM APAGA O QUE NAO DEVIA.

E NAO se reinterpretou `SINTONIA_SALA_DSN`. Ela e a configuracao da SALA — outro
dono, outra pergunta. Que a Sala e a Collection possam viver no MESMO Postgres
nao as torna o mesmo conceito:

    MESMO BANCO FISICO != MESMO OWNER CONCEITUAL.

POR QUE O MESMO BANCO FISICO E OBRIGATORIO, E NAO UMA PREFERENCIA
-----------------------------------------------------------------
Medido no schema real, e nao escolhido:

    sala_de_espera.run_id            -> collection_run.run_id
    sala_de_espera.raw_observation_id-> raw_asset.id
    raw_asset.run_id                 -> collection_run.run_id
    raw_asset.storage_object_id      -> storage_object.id
    derived_artifact.raw_asset_id    -> raw_asset.id

Uma chave estrangeira NAO atravessa bancos em PostgreSQL. Separar a Collection
da Sala em dois `database` partiria cinco FKs que a migration `031` escreveu de
proposito. Por isso a topologia e `SAME_DB`, e as duas variaveis podem — e neste
ambiente devem — apontar para la.

    A TOPOLOGIA FOI DECIDIDA PELO SCHEMA. DUAS CONFIGURACOES, UM BANCO.
"""
from urllib.parse import parse_qs, urlparse

#: Os mesmos hosts locais do guarda descartavel. A lista repete-se aqui de
#: proposito: importa-la criaria uma dependencia entre dois guardas que devem
#: poder divergir no dia em que a bancada operacional deixar de ser local.
HOSTS_LOCAIS = ("localhost", "127.0.0.1", "::1", "[::1]")

#: Os UNICOS nomes de banco que esta casa aceita como bancada OPERACIONAL da
#: Collection. A lista e curta para que crescer doa — e cada nome aqui e uma
#: decisao consciente, tal como do lado descartavel.
#:   `sala_italia` entrou em 2026-09-18 (C-SALA-OPERACIONAL-PERSISTENTE-V1):
#:   e o banco onde a Sala italiana vive, e as FKs obrigam a Collection a
#:   viver no mesmo sitio.
BANCOS_OPERACIONAIS = ("sala_italia",)

#: As variaveis de ambiente que a libpq le POR BAIXO da URL e que conseguem
#: mandar a ligacao para outra maquina sem a URL mudar uma letra.
AMBIENTE_QUE_MUDA_O_DESTINO = ("PGHOST", "PGHOSTADDR", "PGPORT", "PGDATABASE",
                               "PGSERVICE", "PGSERVICEFILE", "PGOPTIONS")


class BancoNaoOperacional(Exception):
    """A URL declarada NAO prova ser uma bancada operacional autorizada."""


def porque_nao_e_operacional(url) -> str:
    """O MOTIVO da recusa, ou `""` quando a URL e aceitavel.

    Devolve TEXTO e nao booleano porque quem recusa tem de dizer porque — e o
    motivo nunca repete a URL inteira, que pode trazer senha.

    ⚠️ ISTO NAO E «NAO PARECE PRODUCAO». E «ESTA NA LISTA DOS AUTORIZADOS».
    Uma heuristica de bloqueio erra para o lado de deixar passar o que ninguem
    previu; uma allowlist erra para o lado de recusar o que ninguem declarou.
    So um desses erros e seguro.
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
        return "hostname nao esta na lista operacional autorizada"
    try:
        u.port  # um porto que nao e numero levanta aqui, e nao no psql
    except ValueError:
        return "porto malformado"
    banco = (u.path or "").lstrip("/")
    if banco not in BANCOS_OPERACIONAIS:
        return "banco fora da lista operacional autorizada"
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


def e_operacional(url) -> bool:
    """`True` so quando a URL prova, por estrutura, ser bancada operacional."""
    return porque_nao_e_operacional(url) == ""


def exigir_operacional(url) -> str:
    """Devolve a URL quando ela prova; levanta quando nao. Falha FECHADO."""
    motivo = porque_nao_e_operacional(url)
    if motivo:
        raise BancoNaoOperacional(
            "BANCO_NAO_OPERACIONAL: a URL declarada nao prova ser uma bancada "
            "operacional autorizada (%s). Nada foi escrito. "
            "ALLOWLIST EXPLICITA > HEURISTICA." % motivo)
    return url


def morada_sem_segredo(url) -> str:
    """`host:porto/banco`, sem utilizador e sem senha. Para recibos e logs."""
    try:
        u = urlparse((url or "").strip())
        host = (u.hostname or "?")
        porto = (":%s" % u.port) if u.port else ""
        banco = (u.path or "").lstrip("/") or "?"
        return "%s%s/%s" % (host, porto, banco)
    except ValueError:
        return "?"
