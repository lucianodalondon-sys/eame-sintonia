#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PORTAS LIGADAS À PRODUÇÃO — adaptadores, não donos.

O QUE ISTO É
------------
Os donos da escrita (`preservar_coleta.py`, `preservar_derivado.py`) nunca
falaram com banco nem com armazém: falam com duas **portas**, `Armazem` e
`Memoria`. Até hoje só existiam implementações descartáveis — um dicionário e
um SQLite. Este ficheiro é a primeira implementação **real**.

    ISTO NÃO É UM DONO. É UMA PORTA.

Não decide nada, não tem regra de negócio, não sabe o que é uma derivação.
Traduz chamadas para HTTP e para `psql`, e mais nada. Toda a lei continua nos
donos — que é o que permite prová-los sem tocar em produção.

POR QUE MORA EM `guarda/`
-------------------------
Na gaveta do dono, ao lado das portas que implementa. Pô-lo no executor faria
o executor conhecer o banco, e a doutrina desta casa é a oposta: o executor
produz o artefato, o dono persiste.

CREDENCIAIS
-----------
Vêm do ambiente e **nunca são impressas**. Um erro do `psql` pode trazer a URL
dentro da mensagem, e por isso ela é limpa antes de sair.
"""
import json
import os
import re
import urllib.error
import urllib.request

from guarda.preservar_coleta import Armazem
from guarda.memoria_postgres import MemoriaPostgres, lit as _lit  # noqa: F401

SEGREDO = re.compile(r"postgres(ql)?://[^\s]*")


def _sem_segredo(texto: str) -> str:
    return SEGREDO.sub("<URL_OMITIDA>", texto or "")


class ArmazemSupabase(Armazem):
    """O bucket `raw`, por HTTP. Três perguntas, e nenhuma delas é «apague».

    A porta não tem `remover` — e esta implementação também não o inventa. Se a
    memória falhar depois do envio, apagar o byte para fingir atomicidade
    destruiria a única evidência que sobrou.
    """

    def __init__(self, url=None, chave=None, bucket="raw"):
        self.base = (url or os.environ["SUPABASE_URL"]).rstrip("/")
        self.chave = chave or os.environ["SUPABASE_SECRET_KEY"]
        self.bucket = bucket

    def _pedir(self, metodo, caminho, dados=None, tipo=None):
        req = urllib.request.Request(
            "%s/storage/v1/object/%s/%s" % (self.base, self.bucket, caminho),
            data=dados, method=metodo)
        req.add_header("Authorization", "Bearer %s" % self.chave)
        req.add_header("apikey", self.chave)
        if tipo:
            req.add_header("Content-Type", tipo)
        return urllib.request.urlopen(req, timeout=120)

    def existe(self, caminho):
        try:
            self._pedir("GET", caminho).read(1)
            return True
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                return False
            raise

    def enviar(self, caminho, dados, media_type):
        self._pedir("POST", caminho, dados, media_type).read()

    def ler(self, caminho):
        return self._pedir("GET", caminho).read()


class MemoriaSupabase(MemoriaPostgres):
    """O Postgres de produção, falado por `psql`.

    ⚠️ ISTO ERA UMA SEGUNDA IMPLEMENTAÇÃO DO MESMO DIALETO. Tinha o `-c` em
    argv (o defeito do Windows do §130), não tinha `documento_do_derivado`, e
    divergia da porta da prova em pormenores que ninguém media. Duas portas
    da mesma coisa que não falam a mesma língua não são duas portas: são dois
    contratos. Desde 2026-09-17 há UM adaptador — `guarda/memoria_postgres.py`
    — e esta classe só sabe de onde vem a URL.

    Sem driver instalado: `psql` já existe no runner, e instalar um pacote
    global só para isto continua proibido nesta casa.
    """

    def __init__(self, url=None):
        super().__init__(url or os.environ["SUPABASE_DB_URL"])


def buscar(url: str) -> dict:
    """UM GET real, e o recibo dele.

    Nada de confiar no `sha256` histórico: o que conta é o que voltou HOJE, e
    é medido dos bytes que chegaram.
    """
    from datetime import datetime, timezone
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (compatible; SINTONIA/1.0)")
    quando = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with urllib.request.urlopen(req, timeout=120) as r:
        dados = r.read()
        return {"URL_PEDIDA": url, "URL_EFETIVA": r.geturl(),
                "HTTP_STATUS": r.status,
                "CONTENT_TYPE": r.headers.get("Content-Type"),
                "CONTENT_LENGTH_DECLARADO": r.headers.get("Content-Length"),
                "COLLECTED_AT": quando, "BYTES": dados, "TAMANHO": len(dados)}


def e_pdf(dados: bytes) -> bool:
    """A assinatura real dos bytes, não o que o servidor disse que eram.

    Um desafio de bot devolve `200` com HTML por dentro. `content-type` é
    declaração; `%PDF-` é facto.
    """
    return dados[:5] == b"%PDF-"


if __name__ == "__main__":
    print(json.dumps({"O_QUE_ISTO_E": "adaptadores, nao donos",
                      "PORTAS": ["ArmazemSupabase", "MemoriaSupabase"]},
                     ensure_ascii=False))
