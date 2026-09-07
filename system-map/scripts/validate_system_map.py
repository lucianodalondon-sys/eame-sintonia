#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SINTONIA SYSTEM MAP · VALIDADOR

    UMA LEI SEM DENTES E UM PEDIDO POR FAVOR.

`AGENTS.md` manda manter o mapa sincronizado com o repositorio. Este ficheiro e
o que torna essa frase verificavel: ele roda no CI, em cada mudanca, e REPROVA.

Falha fechado. Erro inesperado tambem e FAIL, pela mesma razao que o portao da
build falha fechado: dar a sensacao de guarda com a garantia de nenhuma e pior
do que nao ter guarda.

O QUE ELE PROVA
---------------
  P1  o mapa commitado e o mesmo que o repositorio de hoje produz  ← anti-drift
  P2  nenhum ID repetido
  P3  nenhuma ligacao apontando para peca que nao existe
  P4  todo ficheiro declarado existe mesmo
  P5  nenhuma ligacao tecnica sem linha de codigo que a prove
  P6  nenhum verde sem a prova propria do tipo
  P7  o NAO SEI sobreviveu (nao foi convertido em verde nem escondido)
  P8  nenhum ficheiro com dois donos
  P9  todo ficheiro de codigo tem dono declarado                    ← anti-drift
  P10 status so pode ser um dos quatro valores conhecidos

P1 e P9 sao os dois que impedem "depois alguem atualiza o mapa": criar um script
novo em `scripts/` sem o declarar reprova; mudar codigo sem regerar reprova.
"""

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "system-map" / "data"
AQUI = Path(__file__).parent

VALIDOS = {"PROVEN", "PENDING", "BROKEN", "UNKNOWN"}
falhas: list[str] = []
provas: list[str] = []


def prova(id_: str, o_que: str, ok: bool, detalhe: str = ""):
    provas.append(f"  {'PASS' if ok else 'FAIL'}  {id_:22s} {o_que}")
    if not ok:
        falhas.append(f"{id_}: {o_que}" + (f"\n        {detalhe}" if detalhe else ""))
        if detalhe:
            provas.append(f"        {detalhe}")


def main() -> int:
    # ── P1 · anti-drift: regerar e comparar com o que esta commitado ─────────
    def arquitetura(nome: str):
        """O conteudo SEM o bloco de proveniencia.

        HEAD e BRANCH mudam a cada commit e a cada ramo. Compara-los faria o
        portao reprovar toda a gente, sempre. O que tem de bater e a
        arquitetura; o carimbo de quem correu e informativo.
        """
        f = DADOS / nome
        if not f.exists():
            return None
        d = json.loads(f.read_text(encoding="utf-8"))
        d.pop("PROVENANCE", None)
        return json.dumps(d, ensure_ascii=False, sort_keys=True)

    SERVIDO = RAIZ / "italia-portale" / "client" / "system-map"

    def sem_proveniencia(f: Path):
        if not f.exists():
            return None
        d = json.loads(f.read_text(encoding="utf-8"))
        d.pop("PROVENANCE", None)
        return json.dumps(d, ensure_ascii=False, sort_keys=True)

    antes = {n: arquitetura(n)
             for n in ("architecture.generated.json", "state.generated.json")}
    # A COPIA SERVIDA entra na mesma comparacao. E ela que o cliente abre: se
    # so o ficheiro de dados fosse conferido, alguem podia regerar, commitar os
    # dados e servir a app antiga — e o URL publico mostrava um mapa que ja nao
    # existe, com o carimbo a dizer que estava em dia.
    def servido(n: str):
        f = SERVIDO / n
        if not f.exists():
            return None
        return sem_proveniencia(f) if n.endswith(".json") else f.read_text(encoding="utf-8")

    servido_antes = {n: servido(n)
                     for n in ("state.generated.json", "index.html", "map.js", "map.css")}

    for script in ("scan_repo.py", "generate_system_map.py"):
        r = subprocess.run([sys.executable, str(AQUI / script)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            prova("P1_REGERA", f"{script} correu sem erro", False, r.stderr.strip()[:400])
            return relatar()

    mudou = [n for n, texto in antes.items() if texto != arquitetura(n)]
    for n, texto in servido_antes.items():
        atual = servido(n)
        fonte = ((RAIZ / "system-map" / "app" / n).read_text(encoding="utf-8")
                 if not n.endswith(".json") and (RAIZ / "system-map" / "app" / n).exists() else None)
        if texto != atual or (fonte is not None and fonte != atual):
            mudou.append(f"servido/{n}")
    prova("P1_SEM_DRIFT", "o mapa commitado corresponde ao repositorio de hoje",
          not mudou,
          ("regerar mudou " + ", ".join(mudou) +
           "\n        ALGUEM MEXEU NA ARQUITETURA E NAO ATUALIZOU O MAPA."
           "\n        Conserto: py system-map/scripts/generate_system_map.py && git add system-map/data")
          if mudou else "")

    S = json.loads((DADOS / "state.generated.json").read_text(encoding="utf-8"))
    G = json.loads((DADOS / "architecture.generated.json").read_text(encoding="utf-8"))
    nos = {n["id"]: n for n in S["NODES"]}
    existentes = {f["path"] for f in G["FILES"]}

    # ── P2 · ids unicos ──────────────────────────────────────────────────────
    ids = [n["id"] for n in S["NODES"]]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    prova("P2_IDS_UNICOS", "nenhuma peca com id repetido", not dup, ", ".join(dup))

    terr = {t["id"] for t in S["TERRITORIES"]}
    sem_terr = sorted({n["id"] for n in S["NODES"] if n["territory"] not in terr})
    prova("P2_TERRITORIO", "toda peca vive num territorio que existe",
          not sem_terr, ", ".join(sem_terr))

    # ── P3 · ligacoes apontam para peca existente ────────────────────────────
    soltas = sorted({f"{e['from']}->{e['to']}" for e in S["EDGES"]
                     if e["from"] not in nos or e["to"] not in nos})
    prova("P3_SEM_PONTA_SOLTA", "nenhuma ligacao aponta para peca inexistente",
          not soltas, ", ".join(soltas[:6]))

    deps = set(S["DEPARTMENTS"])
    b_ruins = sorted({f"{e['from']}->{e['to']}" for e in S["BUSINESS_EDGES"]
                      if e["from"] not in nos
                      or not (e["to"].startswith("DEPT:") and e["to"][5:] in deps)})
    prova("P3_NEGOCIO_VALIDO", "toda ligacao de negocio liga peca real a departamento real",
          not b_ruins, ", ".join(b_ruins))

    # ── P4 · ficheiro declarado existe ───────────────────────────────────────
    fantasmas = sorted({f for n in S["NODES"] for f in n["files"] if f not in existentes})
    prova("P4_FICHEIROS_REAIS", "todo ficheiro citado pelo mapa existe no repositorio",
          not fantasmas, ", ".join(fantasmas[:6]))

    # ── P5 · aresta tecnica sem prova nao existe ─────────────────────────────
    sem_prova = [f"{e['from']}->{e['to']} ({e['type']})" for e in S["EDGES"]
                 if e.get("kind") == "technical" and not e.get("evidence")]
    prova("P5_ARESTA_PROVADA", "nenhuma ligacao tecnica sem linha de codigo que a prove",
          not sem_prova, ", ".join(sem_prova[:6]))

    mal_formada = [f"{e['from']}->{e['to']}" for e in S["EDGES"]
                   for ev in e.get("evidence", [])
                   if not (ev.get("file") in existentes and isinstance(ev.get("line"), int))]
    prova("P5_PROVA_APONTAVEL", "toda prova aponta para ficheiro e linha que existem",
          not mal_formada, ", ".join(sorted(set(mal_formada))[:6]))

    # ── P6 · verde exige prova, nunca "o ficheiro existe" ────────────────────
    verde_frouxo = [n["id"] for n in S["NODES"]
                    if n["status"] == "PROVEN"
                    and not (n["inbound"] or n["outbound"])
                    # A linhagem prova-se por documento nomeado (o contrato
                    # canonico) e pelo proprio git — nao por import. Exigir-lhe
                    # uma aresta seria exigir a prova errada.
                    and not (n["territory"] == "Z-LINEAGE"
                             and (n["files"] or n.get("proof") == "git-measurement"))]
    prova("P6_VERDE_TEM_PROVA", "nenhum verde so por o ficheiro existir",
          not verde_frouxo, ", ".join(verde_frouxo))

    sem_tipo = [n["id"] for n in S["NODES"]
                if n["territory"] == "Z-LINEAGE"
                and n.get("proof") not in ("document", "git-measurement")]
    prova("P6_LINHAGEM_DIZ_A_PROVA",
          "toda peca de linhagem declara se a prova e documento ou medicao do git",
          not sem_tipo, ", ".join(sem_tipo))

    verde_stale = [n["id"] for n in S["NODES"]
                   if n["status"] == "PROVEN" and n.get("changed_since_declared")]
    prova("P6_VERDE_NAO_E_VELHO", "nenhum verde sobre ficheiro que mudou depois de declarado",
          not verde_stale, ", ".join(verde_stale))

    # ── P7 · o NAO SEI sobreviveu ────────────────────────────────────────────
    # Um mapa em que tudo e verde nao esta saudavel: esta a esconder.
    expected_verde = [f"{e['from']}->{e['to']}" for e in S["EDGES"]
                      if e.get("kind") == "expected" and e["status"] != "UNKNOWN"]
    prova("P7_NAO_SEI_VIVE", "ligacao declarada e nao provada continua sendo NAO SEI",
          not expected_verde, ", ".join(expected_verde))

    # ── P8 · um ficheiro, um dono ────────────────────────────────────────────
    conf = [f"{c['file']} ({' e '.join(c['claimed_by'])})" for c in S["OWNERSHIP_CONFLICTS"]]
    prova("P8_UM_DONO", "nenhum ficheiro reivindicado por duas pecas",
          not conf, "; ".join(conf[:6]))

    # ── P9 · anti-drift: codigo novo tem de ser declarado ────────────────────
    orfaos = S["UNCLAIMED_CODE_FILES"]
    prova("P9_CODIGO_DECLARADO", "todo ficheiro de codigo pertence a uma peca do mapa",
          not orfaos,
          (f"{len(orfaos)} ficheiro(s) de codigo que o mapa nao conhece:\n        "
           + "\n        ".join(orfaos[:10]) +
           "\n        CODIGO NOVO SEM PECA NO MAPA E ARQUITETURA INVISIVEL."
           "\n        Conserto: declare-o em system-map/data/architecture.declared.json")
          if orfaos else "")

    # ── P10 · vocabulario de status fechado ──────────────────────────────────
    maus = sorted({n["status"] for n in S["NODES"]} - VALIDOS)
    prova("P10_STATUS_VALIDO", "todo status e um dos quatro valores conhecidos",
          not maus, ", ".join(maus))

    return relatar()


def relatar() -> int:
    print("\n".join(provas))
    if falhas:
        print("\n" + "=" * 70)
        print(f"SYSTEM_MAP_CHECK=FAIL · {len(falhas)} prova(s) reprovada(s)")
        print("=" * 70)
        for f in falhas:
            print(f"  · {f}")
        print("\nO mapa e derivado do repo. O repo nao e derivado do mapa.")
        print("Leia AGENTS.md antes de mexer.")
        return 1
    print("\nSYSTEM_MAP_CHECK=PASS · o mapa corresponde ao repositorio")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:  # falha fechado, sempre
        print(f"SYSTEM_MAP_CHECK=FAIL · erro inesperado no validador: {e}", file=sys.stderr)
        raise SystemExit(1)
