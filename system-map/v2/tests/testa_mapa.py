#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVAS DAS REGRAS DO MAPA V2 — e o teste do leigo.

    python3 system-map/v2/tests/testa_mapa.py

TESTE QUE NUNCA VIU VERMELHO NÃO É TESTE. Metade destes constrói de propósito o
caso mau — a evidência que não prova, o estado escrito à mão, o conceito que
some por estar parcial — e exige que o sistema o RECUSE.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
V2 = RAIZ / "system-map" / "v2"
falhou = 0


def carrega(nome):
    spec = importlib.util.spec_from_file_location(nome, V2 / "scripts" / f"{nome}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def teste(frase, ok, det=""):
    global falhou
    print(("  PASS  " if ok else "  FAIL  ") + frase + (("  ·  " + det) if not ok and det else ""))
    if not ok:
        falhou += 1


G = carrega("gerar_mapa")
M = carrega("medir_maquina")
S = json.loads((V2 / "data" / "estado.gerado.json").read_text(encoding="utf-8"))
MOD = json.loads((V2 / "model" / "maquina.model.json").read_text(encoding="utf-8"))
C, L = S["CONCEITOS"], S["LIGACOES"]

print("=" * 78); print("PROVAS DO MAPA V2"); print("=" * 78)

# ── 1 · a evidência tem de PROVAR, não só existir ───────────────────────────
teste("artefato que existe mas sem o caminho pedido NÃO confirma",
      M.caminho_em({"A": 1}, "B")[0] is False)
teste("o valor tem de bater com o esperado", M.bate(False, True) is False)
teste("«>0» recusa zero", M.bate(0, ">0") is False)
teste("«>0» aceita um número maior", M.bate(6, ">0") is True)
teste("«nao-vazio» recusa lista vazia", M.bate([], "nao-vazio") is False)
teste("«contem:A>B» exige aquele par exato",
      M.bate([["X", "Y"]], "contem:A>B") is False and
      M.bate([["A", "B"]], "contem:A>B") is True)

# ── 2 · nenhuma prova fraca vira forte ──────────────────────────────────────
so_codigo = {"declarada": {"estado": "CONFIRMADA", "file": "x"},
             "codigo": {"estado": "ENCONTRADA", "file": "x", "line": 1},
             "observada": {"estado": "NAO_CONFIRMA", "artefato": "a", "caminho": "c",
                           "valor": False, "espera": True}}
teste("medição que não confirma deixa a aresta em IMPLEMENTED, nunca OBSERVED",
      G.estado_ligacao(so_codigo)[0] == "IMPLEMENTED")
so_escrito = {"declarada": {"estado": "CONFIRMADA", "file": "x"},
              "codigo": {"estado": "NAO_DECLARADA", "file": None},
              "observada": {"estado": "SEM_OBSERVACAO"}}
teste("contrato sem código fica em DECLARED", G.estado_ligacao(so_escrito)[0] == "DECLARED")
nada = {"declarada": {"estado": "FRASE_NAO_ENCONTRADA", "file": "x"},
        "codigo": {"estado": "NAO_ENCONTRADA", "file": "x"},
        "observada": {"estado": "SEM_OBSERVACAO"}}
teste("sem prova nenhuma a aresta fica em UNKNOWN — e não desaparece",
      G.estado_ligacao(nada)[0] == "UNKNOWN")

# ── 3 · as quatro verdades não se fundem ────────────────────────────────────
teste("canónico e não implementado continua VISÍVEL, como NÃO IMPLEMENTADO",
      G.saude({}, "SIM", "SIM", "NAO", "NAO_SEI")[0] == "NAO_IMPLEMENTADO")
teste("implementado e nunca observado é NÃO SEI, nunca OK",
      G.saude({}, "SIM", "SIM", "SIM", "NAO_SEI")[0] == "UNKNOWN")
teste("medição que diz que não aconteceu é BLOQUEADO",
      G.saude({}, "SIM", "SIM", "SIM", "NAO")[0] == "BLOQUEADO")
teste("legado é sempre LEGADO, mesmo com tudo verde",
      G.saude({"legacy": True}, "SIM", "SIM", "SIM", "SIM")[0] == "LEGADO")
teste("tudo provado é OK", G.saude({}, "SIM", "SIM", "SIM", "SIM")[0] == "OK")
teste("código fora do desenho canónico é representável (BIBLE=NÃO SEI, CODE=SIM)",
      G.saude({}, "NAO_SEI", "SIM", "SIM", "NAO_SEI")[0] in ("UNKNOWN", "ATENCAO"))

# ── 4 · o modelo não carrega estado ─────────────────────────────────────────
cru = (V2 / "model" / "maquina.model.json").read_text(encoding="utf-8")
teste("o modelo declarado não contém nenhum campo de estado",
      not any(p in cru for p in ('"status"', '"saude"', '"OBSERVED"', '"biblia":')))

# ── 5 · a tela não guarda factos ────────────────────────────────────────────
app = (V2 / "app" / "map.js").read_text(encoding="utf-8")
nomes = [c["nome"] for c in C.values()] + [d["nome"] for d in S["DEPARTAMENTOS"]]
vaz = [n for n in nomes if len(n) > 6 and n in app]
teste("nenhum nome de peça está escrito dentro da tela", not vaz, str(vaz[:3]))
tam = [float(x) for x in re.findall(r"font-size:\s*([\d.]+)px",
                                    (V2 / "app" / "map.css").read_text(encoding="utf-8"))]
teste("nenhuma letra desce abaixo de 11px", tam and min(tam) >= 11.0,
      f"menor={min(tam) if tam else '?'}")

# ── 6 · determinismo ────────────────────────────────────────────────────────
def _sc(p):
    d = json.loads(p.read_text(encoding="utf-8")); d.pop("PROVENANCE", None)
    return json.dumps(d, ensure_ascii=False, sort_keys=True)
alvo = V2 / "data" / "estado.gerado.json"
a = _sc(alvo)
for passo in ("medir_maquina.py", "gerar_mapa.py"):
    subprocess.run([sys.executable, str(V2 / "scripts" / passo)], capture_output=True, check=True)
teste("regerar duas vezes devolve exatamente o mesmo mapa", _sc(alvo) == a)

# ── 7 · as metas ────────────────────────────────────────────────────────────
c = S["CONTAS"]
teste("órfãos inexplicados = 0", c["ORFAOS"] == 0, str(S["ORFAOS_INEXPLICADOS"]))
teste("conflitos de dono = 0", c["CONFLITOS_DE_DONO"] == 0)
teste("o nível 0 cabe numa tela (≤ 8)", c["NIVEL_0"] <= 8, str(c["NIVEL_0"]))
teste("nenhum departamento passa de 14 no nível 1",
      all(n <= 14 for n in c["NIVEL_1_POR_DEPARTAMENTO"].values()),
      str(c["NIVEL_1_POR_DEPARTAMENTO"]))
teste("há legado classificado, e ele não é apagado", c["LEGADO"] >= 1)

# ── 8 · a máquina inteira está representada ─────────────────────────────────
papeis = {x.get("papel_canonico") for x in C.values()}
for p in ("SOURCE", "REQUEST", "ORCHESTRATOR", "EXECUTOR", "RUN", "RAW_OBSERVATION",
          "STORAGE_OBJECT", "DERIVED", "STRUCTURED", "ADMISSION", "READY",
          "WAITING_ROOM", "COLLECTION_GAP", "PACKAGE", "SURFACE"):
    teste(f"o papel canónico {p} tem cartão", p in papeis)

print()
print("-" * 78); print("O TESTE DO LEIGO — 20 perguntas respondidas só com o mapa"); print("-" * 78)

D = {d["id"]: d for d in S["DEPARTAMENTOS"]}
por_papel = {}
for x in C.values():
    por_papel.setdefault(x.get("papel_canonico"), []).append(x)
lig = lambda a, b: next((x for x in L if x["de"] == a and x["para"] == b), None)
um = lambda p: por_papel[p][0]

PERG = [
 ("A", "De onde entra informação?", lambda: um("SOURCE")["nome"] + " — " + um("SOURCE")["frase"]),
 ("B", "Quem recebe o pedido?", lambda: um("ORCHESTRATOR")["nome"] + " — " + um("ORCHESTRATOR")["frase"]),
 ("C", "Quem decide como coletar?", lambda: um("ORCHESTRATOR")["porque"]),
 ("D", "Quem sai buscar?", lambda: um("EXECUTOR")["nome"] + " — " + um("EXECUTOR")["frase"]),
 ("E", "O que é uma RUN?", lambda: um("RUN")["frase"]),
 ("F", "Onde fica o original?", lambda: um("RAW_OBSERVATION")["nome"] + " — " + um("RAW_OBSERVATION")["frase"]),
 ("G", "Onde ele é armazenado?", lambda: um("STORAGE_OBJECT")["nome"] + " — " + um("STORAGE_OBJECT")["frase"]),
 ("H", "Onde é transformado?", lambda: um("DERIVED")["nome"] + " — " + um("DERIVED")["frase"]),
 ("I", "Onde é estruturado?", lambda: um("STRUCTURED")["nome"] + " — " + um("STRUCTURED")["frase"]),
 ("J", "Quem decide se entra?", lambda: um("ADMISSION")["nome"] + " — " + um("ADMISSION")["frase"]),
 ("K", "Onde espera?", lambda: um("WAITING_ROOM")["nome"] + " · estado: " + um("WAITING_ROOM")["status"]),
 ("L", "Onde começa a Inteligência?",
  lambda: D["D-ESPERA"]["nome"] + " → " + D["D-INTELIGENCIA"]["nome"] +
          " (" + lig("D-ESPERA", "D-INTELIGENCIA")["status"] + ")"),
 ("M", "O que a Inteligência cruza?", lambda: [x for x in C.values()
        if x["papel_canonico"] == "CROSSING"][0]["frase"]),
 ("N", "Onde nasce um sinal?", lambda: [x for x in C.values()
        if x["papel_canonico"] == "SIGNAL_FINDING"][0]["nome"]),
 ("O", "Onde nasce um achado?", lambda: [x for x in C.values()
        if x["papel_canonico"] == "SIGNAL_FINDING"][0]["frase"]),
 ("P", "O que as ferramentas fazem?", lambda: [x for x in C.values()
        if x["papel_canonico"] == "VALIDATION"][0]["frase"]),
 ("Q", "Como pede nova coleta?", lambda: um("COLLECTION_GAP")["frase"] +
        " — hoje " + um("COLLECTION_GAP")["status"]),
 ("R", "O que chega ao Portal?", lambda: um("SURFACE")["entra"]),
 ("S", "Onde há bloqueio?", lambda: ", ".join(x["nome"] for x in C.values()
        if x["status"] == "BLOQUEADO")),
 ("T", "O que ainda não existe?", lambda: ", ".join(x["nome"] for x in C.values()
        if x["codigo"] == "NAO") or "nada"),
]
for letra, q, f in PERG:
    try:
        r = f()
    except Exception as e:                       # noqa: BLE001
        r = ""; print(f"  {letra}. {q}\n     ERRO: {e!r}")
    ok = bool(r and str(r).strip())
    if ok:
        print(f"  {letra}. {q}"); print(f"     → {r}")
    teste(f"o mapa responde a pergunta {letra} sem abrir código", ok)

print("=" * 78)
print(("TESTES_MAPA_V2=FAIL · %d reprovado(s)" % falhou) if falhou else "TESTES_MAPA_V2=PASS")
raise SystemExit(1 if falhou else 0)
