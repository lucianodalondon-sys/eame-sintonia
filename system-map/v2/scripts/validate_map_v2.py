#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O DENTE DA LEI DO MAPA V2 — prova que ele corresponde ao repositório de hoje.

    python3 system-map/v2/scripts/validate_map_v2.py

FALHA FECHADO. Erro inesperado também é FAIL: um portão que deixa passar
quando se engana não é um portão, é uma decoração que custa tempo de CI.

O QUE ELE ESTÁ REALMENTE A DEFENDER
------------------------------------
Um mapa mente de quatro maneiras, e todas são silenciosas:

    1. o repositório mudou e o mapa não   → V1
    2. uma afirmação perdeu a autoridade  → V2
    3. uma prova fraca virou prova forte  → V3
    4. um estado foi escrito à mão        → V6

A quarta é a mais perigosa, porque não envelhece: nasce errada. Por isso o
validador recusa que o MODELO contenha a palavra «status» — quem declara diz o
que a peça É e onde se confere; quem calcula o estado é o gerador, sempre.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
V2 = RAIZ / "system-map" / "v2"
MODELO = V2 / "model" / "machine.model.json"
MEDIDO = V2 / "data" / "machine.measured.json"
ESTADO = V2 / "data" / "state.v2.generated.json"

GAVETAS = ("admissao/", "candidatas/", "coleta/", "ferramentas/", "fontes/", "guarda/",
           "leis/", "medidas/", "motor/", "pacote/", "pedido/", "portoes/", "provas/",
           "regras/", "superficie/")
DIRS_DE_CODIGO = GAVETAS + (".github/workflows/", "italia-portale/audit/", "tests/",
                            "system-map/", "italia-portale/client/", "supabase/")
EXT = (".py", ".mjs", ".js", ".sh", ".yml", ".sql", ".cmd")

# Tetos de complexidade. Não são gosto: um nível com dezenas de cartões irmãos
# deixou de agrupar, e a tela volta a ser um inventário. O número é generoso de
# propósito — ele existe para apanhar a regressão, não para desenhar o mapa.
TETO_NIVEL0 = 8
TETO_NIVEL1 = 12

falhas: list[tuple[str, str, list[str]]] = []
passes: list[tuple[str, str]] = []


def prova(chave: str, frase: str, ok: bool, detalhe: list[str] | None = None) -> None:
    (passes.append((chave, frase)) if ok
     else falhas.append((chave, frase, detalhe or [])))


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(RAIZ), *a], capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


def main() -> int:
    for f in (MODELO, MEDIDO, ESTADO):
        if not f.is_file():
            print(f"FALTA {f.relative_to(RAIZ)} — corra o scanner e o gerador.",
                  file=sys.stderr)
            return 1
    modelo = json.loads(MODELO.read_text(encoding="utf-8"))
    S = json.loads(ESTADO.read_text(encoding="utf-8"))
    C = S["CONCEITOS"]

    # ── V1 · o mapa commitado é o que o repositório de hoje produz ──────────
    antes_m, antes_e = MEDIDO.read_bytes(), ESTADO.read_bytes()
    for passo in ("scan_machine.py", "generate_map_v2.py"):
        r = subprocess.run([sys.executable, str(V2 / "scripts" / passo)],
                           capture_output=True, text=True)
        if r.returncode:
            prova("V1_SEM_DRIFT", "o mapa commitado corresponde ao repositório de hoje",
                  False, [f"{passo} falhou: {r.stderr.strip()[:300]}"])
            break
    else:
        mudou = [n for n, a, b in (("machine.measured.json", antes_m, MEDIDO.read_bytes()),
                                   ("state.v2.generated.json", antes_e, ESTADO.read_bytes()))
                 if a != b]
        prova("V1_SEM_DRIFT", "o mapa commitado corresponde ao repositório de hoje",
              not mudou,
              [f"regerar mudou: {', '.join(mudou)}",
               "ALGUÉM MEXEU NA MÁQUINA E NÃO REGEROU O MAPA.",
               "Conserto: python3 system-map/v2/scripts/generate_map_v2.py && git add system-map/v2/data"])
        # relê o estado que acabou de ser regerado
        S = json.loads(ESTADO.read_text(encoding="utf-8"))
        C = S["CONCEITOS"]

    medido = json.loads(MEDIDO.read_text(encoding="utf-8"))

    # ── V2 · toda afirmação aponta para uma autoridade que a confirma ───────
    sem = [x["id"] for x in medido["DEPARTAMENTOS"] + medido["CONCEITOS"]
           if x["autoridade"]["estado"] != "CONFIRMADA"]
    prova("V2_AUTORIDADE_CONFIRMA", "toda peça cita autoridade que existe e diz aquilo",
          not sem, [f"{len(sem)} peça(s) sem autoridade confirmada: {', '.join(sem[:8])}"])

    # ── V3 · nenhuma prova fraca promovida a forte ──────────────────────────
    maus = []
    for l in S["LIGACOES"]:
        if l["status"] == "OBSERVED" and not l["prova_observada"].get("existe"):
            maus.append(f"{l['de']}→{l['para']}: OBSERVED sem artefato")
        if l["status"] == "IMPLEMENTED" and l["prova_implementada"]["estado"] != "ENCONTRADA":
            maus.append(f"{l['de']}→{l['para']}: IMPLEMENTED sem linha de código")
        if l["status"] == "DECLARED" and l["prova_declarada"]["estado"] != "CONFIRMADA":
            maus.append(f"{l['de']}→{l['para']}: DECLARED sem autoridade")
    prova("V3_NAO_PROMOVE", "nenhuma prova fraca aparece como prova forte", not maus, maus)

    # ── V3b · observado exige que o artefato exista, também nas peças ───────
    maus = [cid for cid, c in C.items()
            if c["observado"] == "SIM" and not all(o["existe"] for o in c["observacoes"])]
    prova("V3_OBSERVADO_TEM_ARTEFATO",
          "nenhuma peça diz OBSERVADO sem o artefato que o prova", not maus, maus)

    # ── V4 · nenhum órfão inexplicado ───────────────────────────────────────
    o = S["ORFAOS_INEXPLICADOS"]
    prova("V4_SEM_ORFAO_INEXPLICADO",
          "toda peça de fluxo tem entrada, saída, ou papel declarado que o explique",
          not o, [f"{x['id']} ({x['papel']})" for x in o])

    # ── V5 · um ficheiro, um dono ───────────────────────────────────────────
    cf = S["CONFLITOS_DE_DONO"]
    prova("V5_UM_DONO", "nenhum ficheiro reivindicado por duas peças", not cf,
          [f"{x['ficheiro']} ← {', '.join(x['reivindicado_por'])}" for x in cf])

    # ── V6 · nenhum estado escrito à mão no modelo ──────────────────────────
    cru = MODELO.read_text(encoding="utf-8")
    proibidas = sorted({p for p in ("\"status\"", "\"ui_status\"", "\"observado\":",
                                    "\"implementado\":", "\"canonico\"", "\"saude\"",
                                    "\"bloqueado\"", "\"OBSERVED\"", "\"IMPLEMENTED\"")
                        if p in cru})
    prova("V6_ESTADO_NAO_SE_DECLARA",
          "o modelo diz o que a peça é e onde se confere — nunca o estado dela",
          not proibidas, [f"o modelo contém {p}" for p in proibidas])

    # ── V7 · a hierarquia fecha ─────────────────────────────────────────────
    deps = {d["id"] for d in S["DEPARTAMENTOS"]}
    fams = {f["id"] for f in S["FAMILIAS"]}
    maus = []
    for cid, c in C.items():
        if c["departamento"] not in deps:
            maus.append(f"{cid}: departamento inexistente {c['departamento']}")
        if c["parent"] and c["parent"] not in C:
            maus.append(f"{cid}: parent inexistente {c['parent']}")
        if c["parent"] and C.get(c["parent"], {}).get("departamento") != c["departamento"]:
            maus.append(f"{cid}: está noutro departamento que o seu parent")
        if c["nivel"] == 2 and not c["parent"]:
            maus.append(f"{cid}: nível 2 sem parent")
        if c["nivel"] == 1 and c["parent"]:
            maus.append(f"{cid}: nível 1 com parent")
    for d in S["DEPARTAMENTOS"]:
        if d["familia"] not in fams:
            maus.append(f"{d['id']}: família inexistente {d['familia']}")
    prova("V7_HIERARQUIA_FECHA",
          "todo conceito tem departamento e família reais, e o nível bate com o parent",
          not maus, maus)

    # ── V8 · nenhuma ligação aponta para peça que não existe ────────────────
    reais = set(C) | deps
    pontas = [f"{l['de']}→{l['para']}" for l in S["LIGACOES"]
              if l["de"] not in reais or l["para"] not in reais]
    prova("V8_SEM_PONTA_SOLTA", "nenhuma ligação aponta para peça inexistente",
          not pontas, pontas)

    # ── V9 · o legado está fora do fluxo ────────────────────────────────────
    leg = {cid for cid, c in C.items() if c["legacy"]}
    dentro = [f"{l['de']}→{l['para']}" for l in S["LIGACOES"]
              if l["de"] in leg or l["para"] in leg]
    prova("V9_LEGADO_FORA_DO_FLUXO",
          "peça de legado não participa do fluxo principal", not dentro, dentro)

    # ── V10 · o agrupamento não afrouxou ────────────────────────────────────
    maus = []
    if S["CONTAS"]["LEVEL_0_CARD_COUNT"] > TETO_NIVEL0:
        maus.append(f"nível 0 tem {S['CONTAS']['LEVEL_0_CARD_COUNT']} cartões (teto {TETO_NIVEL0})")
    for d, n in S["CONTAS"]["LEVEL_1_POR_DEPARTAMENTO"].items():
        if n > TETO_NIVEL1:
            maus.append(f"{d} tem {n} cartões no nível 1 (teto {TETO_NIVEL1})")
    prova("V10_AGRUPAMENTO", "nenhum nível virou inventário de irmãos sem agrupar",
          not maus, maus + (["AGRUPE SOB O DONO CERTO."] if maus else []))

    # ── V11 · todo código da máquina pertence a um conceito ─────────────────
    tracked = [f for f in git("ls-files").splitlines() if f]
    codigo = [f for f in tracked
              if f.startswith(DIRS_DE_CODIGO) and f.endswith(EXT)
              and "/vendor/" not in f
              and not f.startswith("italia-portale/client/system-map/")]
    dono = set()
    for c in C.values():
        dono |= set(c["ficheiros_todos"])
    orfaos = sorted(set(codigo) - dono)
    prova("V11_CODIGO_TEM_CONCEITO",
          "todo ficheiro de código da máquina pertence a um conceito do mapa",
          not orfaos,
          [f"{len(orfaos)} sem conceito: " + ", ".join(orfaos[:10]),
           "CÓDIGO QUE NINGUÉM APONTA NO MAPA É ARQUITETURA INVISÍVEL."] if orfaos else [])

    # ── V12 · a tela não guarda factos ──────────────────────────────────────
    app = (V2 / "app" / "map.js").read_text(encoding="utf-8")
    nomes = [c["nome"] for c in C.values()] + [d["nome"] for d in S["DEPARTAMENTOS"]]
    vazados = sorted({n for n in nomes if len(n) > 6 and n in app})
    prova("V12_TELA_SEM_FACTOS",
          "nenhum nome de peça da máquina está escrito dentro da tela",
          not vazados, [f"a tela contém «{n}»" for n in vazados])

    # ── V13 · o mapa V1 continua intacto ────────────────────────────────────
    sujo = [l[3:] for l in git("status", "--porcelain", "system-map/app",
                               "system-map/scripts", "system-map/tests").splitlines()]
    prova("V13_MAPA_ANTIGO_INTACTO",
          "o mapa antigo não foi alterado por esta reconstrução", not sujo, sujo)

    # ── relatório ───────────────────────────────────────────────────────────
    largura = 74
    print("=" * largura)
    print("SYSTEM MAP V2 — o mapa mostra a máquina, e prova cada coisa que diz")
    print("=" * largura)
    for k, f in passes:
        print(f"  PASS  {k:28s} {f}")
    for k, f, det in falhas:
        print(f"  FAIL  {k:28s} {f}")
        for d in det:
            print(f"        {d}")
    print()
    c = S["CONTAS"]
    print(f"  departamentos {c['LEVEL_0_CARD_COUNT']} · "
          f"nível 2 {c['SECOND_LEVEL_CARD_COUNT']} · legado escondido {c['LEGACY_HIDDEN_COUNT']}")
    print(f"  arestas: DECLARED {c['EDGES']['DECLARED_COUNT']} · "
          f"IMPLEMENTED {c['EDGES']['IMPLEMENTED_COUNT']} · "
          f"OBSERVED {c['EDGES']['OBSERVED_COUNT']} · UNKNOWN {c['EDGES']['UNKNOWN_COUNT']}")
    print(f"  UNEXPLAINED_ORPHANS {c['UNEXPLAINED_ORPHANS']} · "
          f"OWNERSHIP_CONFLICTS {c['OWNERSHIP_CONFLICTS']}")
    print("=" * largura)
    if falhas:
        print(f"SYSTEM_MAP_V2_CHECK=FAIL · {len(falhas)} prova(s) reprovada(s)")
        return 1
    print(f"SYSTEM_MAP_V2_CHECK=PASS · {len(passes)} prova(s)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:       # falha fechado: engano também é FAIL
        print(f"SYSTEM_MAP_V2_CHECK=FAIL · erro inesperado: {e!r}", file=sys.stderr)
        raise SystemExit(1)
