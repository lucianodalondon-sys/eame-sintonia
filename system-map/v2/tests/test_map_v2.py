#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVAS DAS REGRAS DO MAPA V2 — que elas não afrouxem sem alguém reparar.

    python3 system-map/v2/tests/test_map_v2.py

TESTE QUE NUNCA VIU VERMELHO NÃO É TESTE. Por isso metade destes constrói de
propósito o caso mau — a ligação sem artefato, a autoridade que não confirma, o
estado escrito à mão — e exige que o sistema o RECUSE. Um teste que só passa o
caso bom prova que o caso bom funciona, e nada sobre o portão.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
V2 = RAIZ / "system-map" / "v2"

falhou = 0


def carrega(nome: str):
    spec = importlib.util.spec_from_file_location(nome, V2 / "scripts" / f"{nome}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def teste(frase: str, ok: bool, detalhe: str = "") -> None:
    global falhou
    print(("  PASS  " if ok else "  FAIL  ") + frase + (("  ·  " + detalhe) if not ok and detalhe else ""))
    if not ok:
        falhou += 1


G = carrega("generate_map_v2")
S = json.loads((V2 / "data" / "state.v2.generated.json").read_text(encoding="utf-8"))
M = json.loads((V2 / "model" / "machine.model.json").read_text(encoding="utf-8"))

print("=" * 74)
print("PROVAS DO MAPA V2")
print("=" * 74)

# ── 1 · uma prova fraca nunca vira forte ────────────────────────────────────
so_codigo = {"declarada": {"estado": "CONFIRMADA", "file": "x"},
             "implementada": {"estado": "ENCONTRADA", "file": "x", "line": 1},
             "observada": {"existe": False, "path": None}}
teste("código sem artefato fica em IMPLEMENTED, nunca em OBSERVED",
      G.estado_ligacao(so_codigo)[0] == "IMPLEMENTED", G.estado_ligacao(so_codigo)[0])

so_escrito = {"declarada": {"estado": "CONFIRMADA", "file": "x"},
              "implementada": {"estado": "NAO_DECLARADA", "file": None},
              "observada": {"existe": False, "path": None}}
teste("declaração sem código fica em DECLARED, nunca em IMPLEMENTED",
      G.estado_ligacao(so_escrito)[0] == "DECLARED", G.estado_ligacao(so_escrito)[0])

nada = {"declarada": {"estado": "FRASE_NAO_ENCONTRADA", "file": "x"},
        "implementada": {"estado": "NAO_ENCONTRADA", "file": "x"},
        "observada": {"existe": False, "path": None}}
teste("sem prova nenhuma a ligação fica em UNKNOWN — e não desaparece",
      G.estado_ligacao(nada)[0] == "UNKNOWN", G.estado_ligacao(nada)[0])

# ── 2 · autoridade que não confirma não promove ─────────────────────────────
for mau in ("FRASE_NAO_ENCONTRADA", "FICHEIRO_AUSENTE", "SEM_AUTORIDADE"):
    v = G.estado_canonico({"autoridade": {"estado": mau, "file": "x", "anchor": "y"}})[0]
    teste(f"autoridade em {mau} devolve NÃO SEI, nunca SIM", v == "NAO SEI", v)

# ── 3 · observado exige artefato que exista ─────────────────────────────────
v = G.estado_observado({"observacoes": [{"existe": False, "path": "p", "prova": "q"}]})[0]
teste("artefato ausente devolve OBSERVADO=NÃO", v == "NAO", v)
v = G.estado_observado({"observacoes": []})[0]
teste("sem artefato apontado devolve OBSERVADO=NÃO SEI, e não NÃO", v == "NAO SEI", v)

# ── 4 · bloqueado nasce de medição, não de opinião ──────────────────────────
st, _ = G.saude({}, "SIM", "SIM", "SIM", True)
teste("caminho exigido em falta força BLOQUEADO mesmo com tudo o resto verde",
      st == "BLOQUEADO", st)
st, _ = G.saude({}, "SIM", "SIM", "SIM", False)
teste("sem impedimento e sem problema, a saúde é OK", st == "OK", st)
st, _ = G.saude({"legacy": True}, "SIM", "SIM", "SIM", False)
teste("peça de legado é sempre LEGADO, mesmo com tudo verde", st == "LEGADO", st)
st, _ = G.saude({}, "NAO SEI", "SIM", "NAO SEI", False)
teste("peça sem autoridade confirmada cai em UNKNOWN, e não em OK", st == "UNKNOWN", st)

# ── 5 · o modelo não pode carregar estado ───────────────────────────────────
cru = (V2 / "model" / "machine.model.json").read_text(encoding="utf-8")
teste("o modelo declarado não contém nenhum campo de estado",
      not any(p in cru for p in ('"status"', '"ui_status"', '"saude"', '"canonico"')))

# ── 6 · a tela não guarda factos da máquina ─────────────────────────────────
app = (V2 / "app" / "map.js").read_text(encoding="utf-8")
nomes = [c["nome"] for c in S["CONCEITOS"].values()] + [d["nome"] for d in S["DEPARTAMENTOS"]]
vaz = [n for n in nomes if len(n) > 6 and n in app]
teste("nenhum nome de peça da máquina está escrito dentro da tela", not vaz, str(vaz[:3]))

# ── 6b · nenhuma letra obriga a aproximar para ser lida ─────────────────────
# Um mapa que se decifra em vez de se ler falhou. O red team desta entrega
# derrubou uma versão anterior por causa de uma única pastilha a 9,5px — e ela
# estava exatamente onde o estado de cada ligação é dito.
import re as _re
_css = (V2 / "app" / "map.css").read_text(encoding="utf-8")
_tams = [float(x) for x in _re.findall(r"font-size:\s*([\d.]+)px", _css)]
teste("nenhum tamanho de letra desce abaixo de 11px",
      _tams and min(_tams) >= 11.0, f"menor = {min(_tams) if _tams else '?'}px")

# ── 7 · determinismo: mesma árvore, mesmos bytes ────────────────────────────
# Sem o carimbo: `PROVENANCE` carrega HEAD, e commitar muda o HEAD. Comparar
# bytes crus mediria o acto de commitar, não o determinismo do gerador.
def _sem_carimbo(p):
    d = json.loads(p.read_text(encoding="utf-8"))
    d.pop("PROVENANCE", None)
    return json.dumps(d, ensure_ascii=False, sort_keys=True)


alvo = V2 / "data" / "state.v2.generated.json"
a = _sem_carimbo(alvo)
subprocess.run([sys.executable, str(V2 / "scripts" / "scan_machine.py")],
               capture_output=True, check=True)
subprocess.run([sys.executable, str(V2 / "scripts" / "generate_map_v2.py")],
               capture_output=True, check=True)
teste("regerar duas vezes na mesma árvore devolve exatamente o mesmo mapa",
      _sem_carimbo(alvo) == a)

# ── 8 · as metas que a missão exige ─────────────────────────────────────────
c = S["CONTAS"]
teste("UNEXPLAINED_ORPHANS = 0", c["UNEXPLAINED_ORPHANS"] == 0, str(c["UNEXPLAINED_ORPHANS"]))
teste("OWNERSHIP_CONFLICTS = 0", c["OWNERSHIP_CONFLICTS"] == 0, str(c["OWNERSHIP_CONFLICTS"]))
teste("o nível 0 cabe numa tela (≤ 8 cartões)", c["LEVEL_0_CARD_COUNT"] <= 8,
      str(c["LEVEL_0_CARD_COUNT"]))
teste("nenhum departamento passa de 12 cartões no nível 1",
      all(n <= 12 for n in c["LEVEL_1_POR_DEPARTAMENTO"].values()),
      str(c["LEVEL_1_POR_DEPARTAMENTO"]))

# ── 9 · a máquina inteira está representada ─────────────────────────────────
deps = {d["id"] for d in S["DEPARTAMENTOS"]}
for d in ("D-FONTES", "D-COLETA", "D-ESPERA", "D-INTELIGENCIA", "D-VALIDACAO", "D-PORTAL"):
    teste(f"o departamento {d} existe no mapa", d in deps)
teste("cada departamento tem pelo menos um sistema dentro",
      all(x["conta_n1"] >= 1 for x in S["DEPARTAMENTOS"]))

# ── 10 · o legado fica fora do fluxo, e não some ────────────────────────────
leg = {cid for cid, x in S["CONCEITOS"].items() if x["legacy"]}
teste("existe legado classificado, e ele não é apagado", len(leg) >= 1)
teste("nenhuma ligação do fluxo toca uma peça de legado",
      not [l for l in S["LIGACOES"] if l["de"] in leg or l["para"] in leg])

# ── 11 · o mapa V1 não foi tocado ───────────────────────────────────────────
sujo = subprocess.run(["git", "-C", str(RAIZ), "status", "--porcelain",
                       "system-map/app", "system-map/scripts", "system-map/tests"],
                      capture_output=True, text=True).stdout.strip()
teste("o mapa antigo continua intacto", not sujo, sujo[:120])

# ── 12 · O TESTE DO LEIGO ───────────────────────────────────────────────────
# Vinte perguntas que uma pessoa que não programa tem de conseguir responder
# OLHANDO SÓ PARA O MAPA. Cada uma aqui é respondida a partir do estado gerado —
# se a resposta não sair dele, o mapa não a mostra, e o teste reprova.
#
#     SE FOR PRECISO ABRIR CÓDIGO PARA RESPONDER, É FAIL.
print()
print("-" * 74)
print("O TESTE DO LEIGO — 20 perguntas respondidas só com o mapa")
print("-" * 74)

D = {d["id"]: d for d in S["DEPARTAMENTOS"]}
CC = S["CONCEITOS"]
LIG = S["LIGACOES"]


def por_papel(*papeis):
    return [c for c in CC.values() if c["papel"] in papeis and not c["legacy"]]


def no_dep(dep):
    return [c for c in CC.values() if c["departamento"] == dep and not c["legacy"]]


def liga(de, para):
    return next((l for l in LIG if l["de"] == de and l["para"] == para), None)


PERGUNTAS = [
 ("A", "De onde os dados entram?",
  lambda: ", ".join(c["nome"] for c in por_papel("SOURCE_BY_DESIGN"))),
 ("B", "Como a coleta começa?",
  lambda: CC["S-PEDIDO"]["frase"]),
 ("C", "Onde a coleta física acontece?",
  lambda: CC["S-EXECUTORES"]["nome"] + " — " + CC["S-EXECUTORES"]["frase"]),
 ("D", "Onde nasce um RUN (a corrida, com o seu recibo)?",
  lambda: CC["S-ORQUESTRADOR"]["nome"] + " · prova: " + CC["S-ORQUESTRADOR"]["observado_motivo"]),
 ("E", "Onde nasce o material bruto?",
  lambda: CC["S-CANAIS"]["frase"]),
 ("F", "Onde o material é armazenado?",
  lambda: ", ".join(c["nome"] for c in no_dep("D-ESPERA"))),
 ("G", "Onde é derivado e estruturado?",
  lambda: CC["S-MOTOR"]["nome"] + " — " + CC["S-MOTOR"]["frase"]),
 ("H", "Onde acontece a Admissão?",
  lambda: CC["S-ADMISSAO"]["nome"] + " · estado: " + CC["S-ADMISSAO"]["status"]),
 ("I", "Onde a Coleta termina?",
  lambda: "na ligação " + liga("S-ADMISSAO", "S-PRONTOS")["significado"] +
          " (" + liga("S-ADMISSAO", "S-PRONTOS")["status"] + ")"),
 ("J", "Onde a Inteligência começa?",
  lambda: "na ligação " + D["D-ESPERA"]["nome"] + " → " + D["D-INTELIGENCIA"]["nome"] +
          " (" + liga("D-ESPERA", "D-INTELIGENCIA")["status"] + ")"),
 ("K", "O que a Inteligência faz?", lambda: D["D-INTELIGENCIA"]["frase"]),
 ("L", "Onde aparecem Cruzamentos, Sinais e Achados?",
  lambda: CC["M-CRUZAMENTOS"]["nome"] + " e " + CC["M-SINAIS"]["nome"] +
          ", dentro de «" + CC["S-MOTOR"]["nome"] + "»"),
 ("M", "Como a Inteligência pode pedir nova coleta?",
  lambda: liga("D-INTELIGENCIA", "D-FONTES")["significado"] +
          " — hoje " + liga("D-INTELIGENCIA", "D-FONTES")["status"]),
 ("N", "Onde entram as ferramentas que consomem a Inteligência?",
  lambda: CC["S-TOOLS"]["nome"] + " — " + CC["S-TOOLS"]["frase"]),
 ("O", "Onde entra a Validação?", lambda: D["D-VALIDACAO"]["frase"]),
 ("P", "Como a informação chega ao Portal?",
  lambda: " → ".join([liga("S-PACOTE", "S-PORTAO-BUILD")["para"],
                      liga("S-PORTAO-BUILD", "S-INGEST-SITE")["para"],
                      liga("S-INGEST-SITE", "S-MODELO")["para"],
                      liga("S-MODELO", "S-TOOLS")["para"]])),
 ("Q", "Onde existem problemas?",
  lambda: ", ".join(c["nome"] for c in CC.values()
                    if c["status"] in ("BLOQUEADO", "ATENCAO"))),
 ("R", "O que ainda não está implementado?",
  lambda: ", ".join(c["nome"] for c in CC.values()
                    if c["implementado"] == "NAO") or "nada"),
 ("S", "O que está implementado mas nunca foi observado a correr?",
  lambda: ", ".join(c["nome"] for c in CC.values()
                    if c["implementado"] == "SIM" and c["observado"] in ("NAO", "NAO SEI"))),
 ("T", "Onde está o legado?",
  lambda: ", ".join(c["nome"] + " (" + c["departamento"] + ")"
                    for c in CC.values() if c["legacy"])),
]

for letra, q, resp in PERGUNTAS:
    try:
        r = resp()
    except Exception as e:                       # noqa: BLE001
        r = ""
        print(f"  {letra}. {q}\n     ERRO: {e!r}")
    ok = bool(r and str(r).strip())
    if ok:
        print(f"  {letra}. {q}")
        print(f"     → {r}")
    teste(f"o mapa responde a pergunta {letra} sem abrir código", ok)

print("=" * 74)
print(("TESTES_MAPA_V2=FAIL · %d reprovado(s)" % falhou) if falhou else "TESTES_MAPA_V2=PASS")
raise SystemExit(1 if falhou else 0)
