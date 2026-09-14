#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A CORRIDA EXISTE EM CADA ROTA? — medido rota a rota, e nao aceite de lista.

    python3 provas/a_corrida_existe_em_cada_rota.py

A LEI
-----
    COLETA REAL  ->  RUN.

Uma aquisicao sem corrida e material sem procedencia: nao ha a quem perguntar
quando foi colhido, com que codigo, por que executor, nem contra que ledger
reconciliar. E `raw_asset.run_id` tem chave estrangeira para `collection_run` —
sem corrida, a observacao nao entra no banco de todo.

O QUE ESTA PROVA RECUSA FAZER
------------------------------
⚠️ NAO CUNHA CORRIDA PARA O TESTE PASSAR. Se uma rota nao tem RUN, a resposta e
dizer QUAL rota e porque — nunca acrescentar um `novo_run_id()` dentro de um
modulo que nao e dono de aquisicao. Um RUN cunhado no sitio errado e pior do
que nenhum: parece procedencia e nao tem dono.

    UM RUN CUNHADO PARA SATISFAZER UM TESTE
    NAO PROVA A ESTRADA: PROVA O TESTE.

⚠️ E NAO ACEITA A LISTA DE NINGUEM. O relatorio da prova de fogo nomeava tres
rotas sem RUN. Aqui cada rota e medida contra ESTA arvore, porque uma lista
escrita noutra arvore descreve outra arvore.

AS TRES RESPOSTAS, E ELAS SAO DIFERENTES
-----------------------------------------
    CUNHA       o proprio executor abre a corrida no dono do RUN
    RECEBE      o orquestrador cunha e passa (`recebe_run_id: True`). E a forma
                canonica: quem controla cunha, quem executa transporta.
    SEM_RUN     nao cunha nem recebe. A coleta dele nao tem corrida.

`RECEBE` e `CUNHA` sao ambos aceitaveis. `SEM_RUN` nao e, para uma rota de
aquisicao — e para o canario desta missao e bloqueante.
"""
import io
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                    # noqa: E402,F401
from receitas import EXECUTORES                    # noqa: E402

SAIDA = os.path.join(RAIZ, "system-map", "data", "corrida-por-rota.generated.json")

#: Quem SABE abrir uma corrida nesta arvore. Medido, e nao suposto: sao os
#: ficheiros que escrevem em `public.collection_run`.
DONOS_DO_RUN = (
    "guarda/preservar_coleta.py",
    "coleta/coleta_checkpoint.py",
    "coleta/regulatorio_importar.py",
    "coleta/ropf_pre_requisito.py",
    "guarda/catalogo_importar.py",
)

CUNHA, RECEBE, SEM_RUN = "CUNHA", "RECEBE", "SEM_RUN"

FALHAS, PASSOU = [], []


def T(nome, condicao, detalhe=""):
    (PASSOU if condicao else FALHAS).append(nome)
    print("  %s  %s%s" % ("ok  " if condicao else "FALHA", nome,
                          ("" if condicao else "\n        " + detalhe)))


def _fonte(rel):
    p = os.path.join(RAIZ, rel)
    if not os.path.isfile(p):
        return None
    with io.open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


def _donos_do_run_medidos():
    """Confere que os donos declarados ESCREVEM mesmo em `collection_run`.

    Uma lista de donos que ninguem verifica envelhece como qualquer outra.
    """
    fora = []
    for d in DONOS_DO_RUN:
        t = _fonte(d) or ""
        if re.search(r"insert\s+into\s+(public\.)?collection_run", t, re.I):
            fora.append(d)
    return fora


def _classificar(exe):
    """A rota deste executor tem corrida? → (estado, porque)."""
    if exe.get("recebe_run_id"):
        return RECEBE, ("declara `recebe_run_id`: o orquestrador cunha a corrida "
                        "e o executor transporta-a. Quem controla cunha, quem "
                        "executa nao inventa.")
    script = (exe.get("roda") or [None])[0]
    t = _fonte(script) if script else None
    if t is None:
        return SEM_RUN, "o ficheiro declarado nao existe nesta arvore: %s" % script
    # Cunha? Ou fala com quem cunha?
    for dono in DONOS_DO_RUN:
        modulo = os.path.splitext(os.path.basename(dono))[0]
        if re.search(r"\bimport\s+%s\b" % re.escape(modulo), t):
            return CUNHA, "importa `%s`, que e dono do RUN" % modulo
    if re.search(r"--run-id|run_id\s*=", t):
        return SEM_RUN, ("fala de `run_id` mas nao o recebe pelo contrato da "
                         "receita nem chama dono nenhum do RUN: o valor entra "
                         "por fora e nao aterra em `collection_run`")
    return SEM_RUN, "nao cunha, nao recebe e nao chama dono do RUN"


print("A CORRIDA EXISTE EM CADA ROTA?")
print()

donos = _donos_do_run_medidos()
T("os donos do RUN declarados escrevem mesmo em `collection_run`",
  len(donos) == len(DONOS_DO_RUN),
  "estes nao escrevem: %s" % sorted(set(DONOS_DO_RUN) - set(donos)))

com_run, sem_run = [], []
detalhe = {}
for alvo, lista in sorted(EXECUTORES.items(), key=lambda x: int(x[0][1:])):
    for exe in lista:
        estado, porque = _classificar(exe)
        linha = {"ALVO": alvo, "EXECUTOR": exe["id"],
                 "RODA": " ".join(exe.get("roda") or []),
                 "ESTADO": estado, "PORQUE": porque}
        detalhe["%s/%s" % (alvo, exe["id"])] = linha
        (com_run if estado in (CUNHA, RECEBE) else sem_run).append(linha)

print()
print("  WHICH_ACQUISITION_PATHS_HAVE_RUN")
for x in com_run:
    print("    %-4s %-22s %-7s %s" % (x["ALVO"], x["EXECUTOR"], x["ESTADO"],
                                      x["PORQUE"][:72]))
print()
print("  WHICH_ACQUISITION_PATHS_LACK_RUN")
if not sem_run:
    print("    (nenhuma)")
for x in sem_run:
    print("    %-4s %-22s %s" % (x["ALVO"], x["EXECUTOR"], x["PORQUE"][:78]))

# ── AS ROTAS DO CANARIO DESTA MISSAO ──────────────────────────────────────
# ⚠️ ESTAS SAO BLOQUEANTES. As outras ficam MEDIDAS; estas tem de ter corrida,
# porque e por elas que o material real vai atravessar ate a Sala.
CANARIO = {"T2": "italia-recorrente",       # PDF e WEB italianos
           "T4": "regulatorio-eu",          # PDF oficial da UE
           "T9": "scrap-colheita"}          # social, se houver rota livre
print()
print("  AS ROTAS DO CANARIO")
for alvo, ident in sorted(CANARIO.items()):
    linha = detalhe.get("%s/%s" % (alvo, ident))
    T("canario %s/%s tem corrida" % (alvo, ident),
      bool(linha) and linha["ESTADO"] in (CUNHA, RECEBE),
      "estado=%s · %s" % ((linha or {}).get("ESTADO"), (linha or {}).get("PORQUE")))

estado_final = {
    "O_QUE_ISTO_E": ("Que rotas de aquisicao tem corrida, medido rota a rota "
                     "nesta arvore — e nao aceite de uma lista escrita noutra."),
    "COMO_REFAZER": "python3 provas/a_corrida_existe_em_cada_rota.py",
    "A_LEI": "COLETA REAL -> RUN",
    "DONOS_DO_RUN": list(donos),
    "WHICH_ACQUISITION_PATHS_HAVE_RUN": [x["ALVO"] + "/" + x["EXECUTOR"]
                                         for x in com_run],
    "WHICH_ACQUISITION_PATHS_LACK_RUN": [x["ALVO"] + "/" + x["EXECUTOR"]
                                         for x in sem_run],
    "DETALHE": detalhe,
    "CANARIO_RUN_REQUIRED": "YES",
    "O_QUE_ISTO_NAO_FAZ": ("nao cunha corrida nenhuma. Uma rota sem RUN sai "
                           "nomeada, e o conserto e do dono dela."),
}
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with io.open(SAIDA, "w", encoding="utf-8") as f:
    json.dump(estado_final, f, ensure_ascii=False, indent=1)
    f.write("\n")

print()
print("  gravado: %s" % os.path.relpath(SAIDA, RAIZ))
print()
print("CANARY_ACQUISITION_HAS_RUN = %s · %d passaram · %d falharam"
      % ("YES" if not FALHAS else "NO", len(PASSOU), len(FALHAS)))
raise SystemExit(1 if FALHAS else 0)
