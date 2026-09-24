#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM da porta operacional — 16 ataques, e nenhum pode passar.

    py provas/red_team_persistencia_operacional.py

Nao mede o caminho feliz: tenta parti-lo. Cada ataque procura uma maneira de
escrever no banco errado, ou de fazer a casa ligar-se a producao sem ninguem
ter pedido.
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

from orquestrador import persistencia as P  # noqa: E402
from guarda import preservar_coleta as PC  # noqa: E402
import tempfile  # noqa: E402

#: BC4 (24/09/2026): a memoria operacional exige a raiz dos bytes fora da arvore.
ARMAZEM = tempfile.mkdtemp(prefix="armazem-red-team-")

SENHA = "SENHA-SECRETA-DO-RED-TEAM"
OP_OK = "postgresql://postgres:%s@127.0.0.1:54330/sala_italia" % SENHA
DESC_OK = "postgresql://postgres:%s@localhost:54329/descartavel" % SENHA

falhas = []


def recusa(nome, env, esperado=Exception):
    """O ataque TEM de ser recusado. Ligar e a falha."""
    try:
        r = P.dependencias_do_runtime(env)
    except esperado as ex:
        if SENHA in str(ex):
            falhas.append("%s · SENHA VAZOU na mensagem de recusa" % nome)
            print("  FALHA %-52s senha na mensagem" % nome)
            return
        print("  ok    %-52s recusou: %s" % (nome, type(ex).__name__))
        return
    except Exception as ex:                                   # noqa: BLE001
        print("  ok    %-52s recusou: %s" % (nome, type(ex).__name__))
        return
    if r.memoria is None:
        print("  ok    %-52s nao ligou (AUSENTE)" % nome)
        return
    falhas.append("%s · LIGOU quando devia recusar" % nome)
    print("  FALHA %-52s LIGOU em %s" % (nome, r.MORADA))


def ausente(nome, env):
    """O ataque NAO pode ligar memoria nenhuma."""
    try:
        r = P.dependencias_do_runtime(env)
    except Exception as ex:                                   # noqa: BLE001
        print("  ok    %-52s recusou: %s" % (nome, type(ex).__name__))
        return
    if r.memoria is None and r.ESTADO == P.AUSENTE:
        print("  ok    %-52s AUSENTE, como devia" % nome)
        return
    falhas.append("%s · LIGOU por inferencia" % nome)
    print("  FALHA %-52s LIGOU: %s" % (nome, r.MORADA))


print("=" * 74)
print("RED TEAM — A PORTA OPERACIONAL DA COLLECTION")
print("=" * 74)

print("\n-- producao e hosts remotos")
recusa("supabase na variavel operacional",
       {P.VARIAVEL_OPERACIONAL:
        "postgresql://u:%s@db.abc.supabase.co:5432/postgres" % SENHA})
recusa("host remoto com banco autorizado",
       {P.VARIAVEL_OPERACIONAL:
        "postgresql://u:%s@10.1.2.3:54330/sala_italia" % SENHA})
recusa("dbname errado no host certo",
       {P.VARIAVEL_OPERACIONAL:
        "postgresql://u:%s@127.0.0.1:54330/postgres" % SENHA})

print("\n-- a query que redireciona a ligacao por baixo da URL")
recusa("query host= aponta para fora",
       {P.VARIAVEL_OPERACIONAL: OP_OK + "?host=evil.example.com"})
recusa("query hostaddr= aponta para fora",
       {P.VARIAVEL_OPERACIONAL: OP_OK + "?hostaddr=10.9.9.9"})
recusa("query dbname= troca o banco",
       {P.VARIAVEL_OPERACIONAL: OP_OK + "?dbname=postgres"})
recusa("query service= usa ficheiro de servico",
       {P.VARIAVEL_OPERACIONAL: OP_OK + "?service=producao"})

print("\n-- inferencia: nenhuma variavel alheia liga a Collection")
ausente("SUPABASE_DB_URL sozinha",
        {"SUPABASE_DB_URL": "postgresql://u:%s@db.abc.supabase.co/postgres" % SENHA})
ausente("SINTONIA_SALA_DSN sozinha", {"SINTONIA_SALA_DSN": OP_OK})
ausente("SALA_DSN + SALA_BACKEND", {"SINTONIA_SALA_DSN": OP_OK,
                                    "SINTONIA_SALA_BACKEND": "POSTGRES"})
ausente("PGHOST/PGDATABASE soltos", {"PGHOST": "127.0.0.1",
                                     "PGDATABASE": "sala_italia"})

print("\n-- conflito e ambiguidade")
recusa("operacional + descartavel ao mesmo tempo",
       {P.VARIAVEL: DESC_OK, P.VARIAVEL_OPERACIONAL: OP_OK},
       P.ModosEmConflito)
recusa("operacional vazia mas presente",
       {P.VARIAVEL_OPERACIONAL: "   "})

print("\n-- malformados")
recusa("scheme errado",
       {P.VARIAVEL_OPERACIONAL: "mysql://u:%s@127.0.0.1:54330/sala_italia" % SENHA})
recusa("porto nao numerico",
       {P.VARIAVEL_OPERACIONAL: "postgresql://u:x@127.0.0.1:porta/sala_italia"})
recusa("url que nao e url", {P.VARIAVEL_OPERACIONAL: "sala_italia"})

print("\n-- os bytes da memoria operacional nao caem no residuo (BC4)")
recusa("operacional sem raiz dos bytes",
       {P.VARIAVEL_OPERACIONAL: OP_OK}, PC.ArmazemOperacionalSemRaiz)
recusa("operacional com raiz dentro da arvore",
       {P.VARIAVEL_OPERACIONAL: OP_OK, PC.VARIAVEL_DA_RAIZ: os.path.join(RAIZ, "XX")},
       PC.ArmazemOperacionalSemRaiz)

print("\n-- o caminho bom continua bom (controlo)")
r = P.dependencias_do_runtime({P.VARIAVEL_OPERACIONAL: OP_OK, PC.VARIAVEL_DA_RAIZ: ARMAZEM})
if r.ESTADO == P.OPERACIONAL and r.memoria is not None:
    print("  ok    %-52s ligou em %s" % ("bancada operacional autorizada",
                                         r.MORADA))
else:
    falhas.append("o caminho bom nao liga")
    print("  FALHA o caminho bom nao liga")
r = P.dependencias_do_runtime({P.VARIAVEL: DESC_OK})
if r.ESTADO == P.DESCARTAVEL and r.memoria is not None:
    print("  ok    %-52s ligou em %s" % ("bancada descartavel (regressao)",
                                         r.MORADA))
else:
    falhas.append("a bancada descartavel regrediu")
    print("  FALHA a bancada descartavel regrediu")

print("\n" + "=" * 74)
print("RED_TEAM_BLOCKERS = %d" % len(falhas))
for f in falhas:
    print("  · %s" % f)
print("=" * 74)
raise SystemExit(1 if falhas else 0)
