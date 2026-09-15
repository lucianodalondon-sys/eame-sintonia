#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O RAW LOCAL NAO E DURAVEL — e o livro deixa de o fazer parecer.

    python3 provas/o_raw_local_nao_e_duravel.py

O QUE SE MEDIU
--------------
`data/collection-ledger/italy/observations.ndjson` tem 144 observacoes. De 35
com `RAW_PATH` declarado:

    10  o ficheiro ESTA nesta arvore, no armazem versionado
    25  o caminho e `C:/eame-sintonia-ops/...` — absoluto, de Windows, da
        maquina do operador

As 25 declaram `RAW_OBJECT_CREATED: true`, e por isso aparecem a quem le o
livro exactamente como as 10 — indistinguiveis. Mas os bytes delas nunca
entraram no repositorio nem em armazem nenhum alcancavel daqui.

    LOCAL PATH != REMOTE DURABILITY.
    E `RAW_OBJECT_CREATED = true` NAO DIZ ONDE, NEM POR QUANTO TEMPO.

O proprio `coleta/italy_recurrent_collect.mjs` declara a lei
`LOCAL_COMMIT != REMOTE_DURABILITY` no cabecalho. Estava violada na pratica.

O QUE ESTA PROVA FAZ, E O QUE ELA RECUSA FAZER
-----------------------------------------------
⚠️ NAO CONSERTA CAMINHO. Reescrever `C:/...` para um caminho desta arvore
diria que os bytes estao aqui, e nao estao.

⚠️ NAO COPIA NADA, e nao fabrica `storage_object`. Um objeto de armazem
inventado para uma observacao cujos bytes ninguem tem e a mentira mais cara
desta casa: a partir dela, toda a cadeia que confia no armazem esta errada.

⚠️ NAO ALTERA `RAW_OBSERVATION_ID`. A identidade da observacao nao muda porque
descobrimos onde os bytes dela estao — nem porque descobrimos que nao estao.

⚠️ E NAO BLOQUEIA O CANARIO. Estas 25 sao LEGADO: nenhuma delas participa da
corrida que esta missao leva a Sala. O que elas nao podem continuar e a
PARECER duraveis.

A CLASSIFICACAO
---------------
    LOCAL_ONLY    o caminho e de uma maquina, e nao deste repositorio. Os bytes
                  podem existir LA. Daqui, nao se alcancam e nao se conferem.
    MISSING       declara caminho desta arvore, e o ficheiro nao esta la.
    RECOVERABLE   nao ha caminho, mas ha SHA e o conteudo existe no armazem
                  desta arvore — da para religar sem inventar nada.
    UNKNOWN       o livro nao diz o suficiente para dizer qualquer uma das
                  outras tres. Ausencia de resposta e uma resposta.
"""
import io
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

LIVRO = os.path.join(RAIZ, "data", "collection-ledger", "italy",
                     "observations.ndjson")
ARMAZEM = os.path.join(RAIZ, "data", "collection-store")
SAIDA = os.path.join(RAIZ, "system-map", "data",
                     "durabilidade-do-raw.generated.json")

LOCAL_ONLY, MISSING, RECOVERABLE, UNKNOWN = (
    "LOCAL_ONLY", "MISSING", "RECOVERABLE", "UNKNOWN")

FALHAS, PASSOU = [], []


def T(nome, condicao, detalhe=""):
    (PASSOU if condicao else FALHAS).append(nome)
    print("  %s  %s%s" % ("ok  " if condicao else "FALHA", nome,
                          ("" if condicao else "\n        " + detalhe)))


def _shas_no_armazem():
    """Os sha256 dos bytes que ESTAO nesta arvore. Medido, e nao declarado."""
    import hashlib
    fora = {}
    for base, _p, ficheiros in os.walk(ARMAZEM):
        for f in ficheiros:
            if f.startswith("."):
                continue
            caminho = os.path.join(base, f)
            h = hashlib.sha256()
            with open(caminho, "rb") as fh:
                for pedaco in iter(lambda: fh.read(1 << 20), b""):
                    h.update(pedaco)
            fora[h.hexdigest()] = os.path.relpath(caminho, RAIZ)
    return fora


def _absoluto_de_outra_maquina(caminho):
    """Um caminho que so existe na maquina de alguem. Nao e heuristica frouxa:
    ou tem letra de unidade Windows, ou comeca na raiz do sistema."""
    c = str(caminho or "")
    return bool(c) and (
        (len(c) > 1 and c[1] == ":") or c.startswith("\\\\") or c.startswith("/"))


def classificar(obs, shas):
    caminho = obs.get("RAW_PATH")
    sha = obs.get("RAW_SHA256")
    criado = obs.get("RAW_OBJECT_CREATED")
    if caminho and _absoluto_de_outra_maquina(caminho):
        return LOCAL_ONLY, ("o caminho e absoluto e de outra maquina: os bytes "
                            "podem existir LA, e daqui nao se alcancam nem se "
                            "conferem")
    if caminho:
        if os.path.isfile(os.path.join(RAIZ, caminho)):
            return None, "o ficheiro esta nesta arvore"
        return MISSING, ("declara um caminho DESTA arvore e o ficheiro nao "
                         "esta la")
    if sha and sha in shas:
        return RECOVERABLE, ("nao declara caminho, mas o conteudo com este "
                             "sha256 existe no armazem desta arvore: %s"
                             % shas[sha])
    if not criado:
        return UNKNOWN, ("o livro nao declara objeto criado nem caminho — esta "
                         "observacao nunca disse ter bytes")
    return UNKNOWN, ("declara objeto criado e nao diz onde, e o sha nao "
                     "corresponde a nada nesta arvore")


print("O RAW LOCAL NAO E DURAVEL")
print()

if not os.path.isfile(LIVRO):
    print("o livro italiano nao esta nesta arvore: nada a medir")
    print("RAW_DURABILITY = NOT_MEASURED")
    raise SystemExit(2)

shas = _shas_no_armazem()
print("  bytes no armazem desta arvore: %d ficheiro(s)" % len(shas))

observacoes = []
with io.open(LIVRO, encoding="utf-8") as f:
    for linha in f:
        linha = linha.strip()
        if not linha:
            continue
        try:
            observacoes.append(json.loads(linha))
        except json.JSONDecodeError:
            continue

por_classe = {LOCAL_ONLY: [], MISSING: [], RECOVERABLE: [], UNKNOWN: []}
duraveis = []
for o in observacoes:
    classe, porque = classificar(o, shas)
    ficha = {"RUN_ID": o.get("RUN_ID"), "SOURCE_ID": o.get("SOURCE_ID"),
             "RAW_SHA256": o.get("RAW_SHA256"),
             "RAW_PATH": o.get("RAW_PATH"),
             "RAW_OBJECT_CREATED": o.get("RAW_OBJECT_CREATED"),
             "PORQUE": porque}
    if classe is None:
        duraveis.append(ficha)
    else:
        por_classe[classe].append(ficha)

print("  observacoes no livro ......... %d" % len(observacoes))
print("  DURAVEL NESTA ARVORE ......... %d" % len(duraveis))
for c in (LOCAL_ONLY, MISSING, RECOVERABLE, UNKNOWN):
    print("  %-28s %d" % (c, len(por_classe[c])))

print()
# ── AS TRAVAS ──────────────────────────────────────────────────────────────
T("as 25 observacoes de `C:/` sao encontradas e classificadas LOCAL_ONLY",
  len(por_classe[LOCAL_ONLY]) == 25,
  "achei %d" % len(por_classe[LOCAL_ONLY]))

sem_porque = [x for lista in por_classe.values() for x in lista
              if len(x["PORQUE"]) < 20]
T("toda observacao nao duravel diz PORQUE", not sem_porque,
  "%d sem razao escrita" % len(sem_porque))

# ⚠️ A TRAVA QUE IMPORTA: nenhuma LOCAL_ONLY pode ter sido "consertada" com um
# caminho desta arvore, e nenhuma pode ter ganho objeto de armazem.
inventadas = [x for x in por_classe[LOCAL_ONLY]
              if x["RAW_SHA256"] and x["RAW_SHA256"] in shas]
T("nenhuma LOCAL_ONLY foi silenciosamente religada a bytes desta arvore",
  not inventadas,
  "%d teriam sido religadas sem reconciliacao declarada" % len(inventadas))

T("o material que esta missao levou a Sala NAO vem de nenhuma LOCAL_ONLY",
  all(x["RUN_ID"] != "PILOT_RUN_20260907153737_4c34b3"
      for x in por_classe[LOCAL_ONLY]),
  "a corrida do canario tem observacoes local-only")

T("e as 10 duraveis sao exactamente as da corrida que atravessou",
  len(duraveis) == 10
  and all(x["RUN_ID"] == "PILOT_RUN_20260907153737_4c34b3" for x in duraveis),
  "%d duraveis" % len(duraveis))

estado = {
    "O_QUE_ISTO_E": ("A durabilidade REAL de cada observacao do livro italiano, "
                     "medida contra os bytes que esta arvore tem."),
    "COMO_REFAZER": "python3 provas/o_raw_local_nao_e_duravel.py",
    "A_LEI": "LOCAL PATH != REMOTE DURABILITY",
    "OBSERVACOES_NO_LIVRO": len(observacoes),
    "DURAVEL_NESTA_ARVORE": len(duraveis),
    "LOCAL_ONLY": len(por_classe[LOCAL_ONLY]),
    "MISSING": len(por_classe[MISSING]),
    "RECOVERABLE": len(por_classe[RECOVERABLE]),
    "UNKNOWN": len(por_classe[UNKNOWN]),
    "O_QUE_ISTO_NAO_FAZ": (
        "nao conserta caminho, nao copia bytes, nao fabrica storage_object e "
        "nao altera RAW_OBSERVATION_ID. Uma observacao local-only continua a "
        "ser local-only; o que ela deixa de fazer e parecer duravel."),
    "BLOQUEIA_O_CANARIO": "NAO — as local-only sao legado e nenhuma participa "
                          "da corrida que chegou a Sala",
    "DETALHE": {c: por_classe[c] for c in por_classe},
}
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with io.open(SAIDA, "w", encoding="utf-8") as f:
    json.dump(estado, f, ensure_ascii=False, indent=1)
    f.write("\n")

print()
print("  gravado: %s" % os.path.relpath(SAIDA, RAIZ))
print()
print("RAW_DURABILITY = %s · %d passaram · %d falharam"
      % ("MEDIDO" if not FALHAS else "FALHOU", len(PASSOU), len(FALHAS)))
raise SystemExit(1 if FALHAS else 0)
