#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O PORTAO DO CONTROL PLANE — os dentes do registo das autoridades.

    py controle/portao_do_controle.py           mede e compara com o chao
    py controle/portao_do_controle.py --fixar   grava o estado de hoje como chao

POR QUE ESTE FICHEIRO EXISTE
-----------------------------
`controle/AUTORIDADES-CANONICAS.json` diz quem manda. Sem este portao, essa frase
seria um pedido por favor: qualquer missao podia apagar uma autoridade, pôr uma
segunda Biblia canonica, duplicar o know-how, trocar o dono de um conceito sem
avisar ninguem — e nada reprovava.

    TEXTO NAO REPROVA NADA. PORTAO REPROVA.

DUAS FAMILIAS DE PROVA, E A DIFERENCA IMPORTA
----------------------------------------------
**INTEGRIDADE** — defeitos que nunca podem existir, nem hoje nem amanha. Dois
cartoes com o mesmo id. Dois donos para o mesmo conceito. Um handoff a governar.
O System Map a aparecer como dono da arquitetura. Uma aresta declarada pintada de
observada. Estes reprovam sempre, e nao ha chao que os desculpe.

**DIVIDA** — defeitos que a casa TEM hoje, medidos e contados: autoridades que
vivem fora desta arvore, copias divergentes, documentos que se dizem lei e nao
estao no registo. Exigir zero hoje reprovaria o repositorio inteiro na primeira
corrida, e a primeira coisa que alguem faria era desligar o portao.

    «ESTA TUDO CERTO» NAO E EXECUTAVEL HOJE. «NAO PIOROU» E.

O estado de hoje fica gravado em `controle/CHAO-DO-CONTROLE.json`. A partir daqui,
uma autoridade nova que desaparece faz o numero subir, e o portao reprova. Quando
alguem pagar a divida, `--fixar` desce o teto — e ele nunca mais sobe.

    A DIVIDA FICA A VISTA, COM NOME E NUMERO, EM VEZ DE VIRAR SILENCIO.

O QUE ESTE PORTAO NAO FAZ
--------------------------
Nao decide o que e lei. Isso esta no registo, escrito por gente. Ele so recusa
que o registo minta sobre si mesmo, e conta o que dói.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


# Substituiveis pela mesma razao que no censo: o red team ataca o codigo real
# sobre ficheiros temporarios, e nunca sobre o registo do repositorio.
def _caminho(env: str, omissao: Path) -> Path:
    v = os.environ.get(env)
    return Path(v) if v else omissao


REGISTO = _caminho("SINTONIA_CONTROLE_REGISTO",
                   RAIZ / "controle" / "AUTORIDADES-CANONICAS.json")
CENSO = _caminho("SINTONIA_CONTROLE_CENSO",
                 RAIZ / "system-map" / "data" / "controle.generated.json")
CHAO = _caminho("SINTONIA_CONTROLE_CHAO", RAIZ / "controle" / "CHAO-DO-CONTROLE.json")

# Palavras com que um documento se declara autoridade. Quem escreve uma destas
# esta a dizer «eu mando» — e quem manda tem de estar no registo.
SE_DIZ_LEI = ("dono canónico", "dono canonico", "CANONICAL_OWNER",
              "SOURCE_OF_TRUTH", "DESIGN_SOURCE_OF_TRUTH")

# O mapa e um CONSUMIDOR da arquitetura, nunca o dono dela.
#
# A regra NAO e sobre a palavra «arquitetura» aparecer no nome do conceito: o
# gerador possui legitimamente a PROJECAO da arquitetura, e proibir-lhe a palavra
# so o ensinaria a chamar-lhe outra coisa. Um portao que se contorna mudando um
# nome nao mede nada.
#
# A regra e sobre o VERBO. Uma peca do mapa pode MEDIR (OBSERVES) e pode REPROVAR
# (VALIDATES) — sao os dois trabalhos dela. O que ela nunca pode e GOVERNAR:
#
#     agente -> implementacao -> testes -> commit -> CI -> mapa regenerado
#
# no dia em que o mapa governasse uma peca, a seta passava a correr ao contrario,
# e o mapa virava a segunda verdade arquitetural que AGENTS.md proibe.
PASTAS_DO_MAPA = ("system-map/",)
VERBOS_DE_GOVERNO = ("GOVERNS", "CONSTRAINS")

falhas: list[tuple[str, str, list]] = []
oks: list[str] = []


def prova(nome: str, descricao: str, passou: bool, detalhe: list | None = None) -> None:
    if passou:
        oks.append(f"  PASS  {nome:<34} {descricao}")
    else:
        falhas.append((nome, descricao, detalhe or []))


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(RAIZ), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout.strip()


def main() -> int:
    fixar = "--fixar" in sys.argv

    if not CENSO.exists():
        print("PORTAO_DO_CONTROLE=FAIL · o censo nao existe.\n"
              "  Corra primeiro: python3 controle/censo_do_controle.py")
        return 1

    R = json.loads(REGISTO.read_text(encoding="utf-8"))
    C = json.loads(CENSO.read_text(encoding="utf-8"))
    cartoes = C["CARDS"]
    arestas = C["GOVERNANCE_EDGES"]
    por_id = {c["CARD_ID"]: c for c in cartoes}
    rastreados = set(git("ls-files").split("\n"))

    # ══ INTEGRIDADE — nunca pode existir ═══════════════════════════════════

    # ── 1 · dois cartoes com o mesmo id ──────────────────────────────────────
    ids = [a["CARD_ID"] for a in R["AUTHORITIES"]]
    repetidos = sorted({i for i in ids if ids.count(i) > 1})
    prova("DUPLICATE_AUTHORITY_ID", "nenhum cartao com id repetido",
          not repetidos, repetidos)

    # ── 2 · UM CONCEITO, UM DONO ─────────────────────────────────────────────
    # A lei inteira desta missao numa linha. Dois documentos canonicos a
    # reivindicar o mesmo conceito e o estado em que nenhum dos dois vale.
    donos: dict[str, list] = {}
    for a in R["AUTHORITIES"]:
        co = a.get("CONCEPT_OWNER", "")
        if co and a["LIFECYCLE"] == "CANONICAL" and not a.get("IS_POINTER"):
            donos.setdefault(co, []).append(a["CARD_ID"])
    colisao = [f"{co}: {' e '.join(v)}" for co, v in sorted(donos.items()) if len(v) > 1]
    prova("DUPLICATE_CONCEPT_OWNER", "nenhum conceito com dois donos canonicos",
          not colisao, colisao)

    # ── 3 · UM SO KNOW-HOW ───────────────────────────────────────────────────
    kh = [a["CARD_ID"] for a in R["AUTHORITIES"]
          if a["KIND"] == "KNOW_HOW" and a["LIFECYCLE"] == "CANONICAL"]
    prova("KNOW_HOW_DUPLICATED", "existe exatamente um know-how canonico",
          len(kh) == 1, kh if len(kh) != 1 else [])

    # ── 4 · superseded nao volta a ser lei ───────────────────────────────────
    zumbis = [a["CARD_ID"] for a in R["AUTHORITIES"]
              if a["LIFECYCLE"] == "CANONICAL" and a.get("SUPERSEDED_BY")]
    prova("SUPERSEDED_MARKED_CANONICAL", "nada substituido continua carimbado de canonico",
          not zumbis, zumbis)

    # ── 5 · HANDOFF NAO E AUTORIDADE ─────────────────────────────────────────
    # Um handoff conta o que aconteceu. No dia em que ele governar alguem, a
    # memoria de uma sessao passa a mandar no repositorio inteiro.
    mandoes = [f"{a['CARD_ID']} governa {len(a.get('GOVERNS', []) + a.get('CONSTRAINS', []))}"
               for a in R["AUTHORITIES"]
               if a["KIND"] == "HANDOFF" and (a.get("GOVERNS") or a.get("CONSTRAINS"))]
    prova("HANDOFF_AS_AUTHORITY", "nenhum handoff governa nada", not mandoes, mandoes)

    # ── 6 · O MAPA NAO E DONO DA ARQUITETURA ─────────────────────────────────
    usurpa = [f"{a['CARD_ID']} governa {len(a.get(v, []))} ({v})"
              for a in R["AUTHORITIES"]
              if a["CANONICAL_PATH"].startswith(PASTAS_DO_MAPA)
              for v in VERBOS_DE_GOVERNO if a.get(v)]
    prova("SYSTEM_MAP_IS_AUTHORITY", "nenhuma peca do mapa governa — mede e reprova, so",
          not usurpa, usurpa)

    # ── 7 · DECLARADA NAO SE PINTA DE OBSERVADA ──────────────────────────────
    # A prova tem de ser do TIPO que aquele tipo de aresta exige. Uma GOVERNS
    # observada com prova `PATH_EXISTS` seria «o ficheiro existe, logo a lei
    # manda nele» — que e exatamente o que esta lei recusa.
    mentiras = [f"{e['FROM']}->{e['TO_PATH']} ({e['EDGE_TYPE']} observada com "
                f"prova {e['PROOF_KIND']})"
                for e in arestas
                if e["EDGE_STATE"] == "OBSERVED"
                and e["PROOF_KIND"] != R["EDGE_TYPES"][e["EDGE_TYPE"]]["observed_needs"]]
    prova("DECLARED_EDGE_RENDERED_AS_OBSERVED",
          "nenhuma aresta declarada aparece como observada", not mentiras, mentiras)

    # ── 8 · toda aresta observada aponta para uma linha que existe ───────────
    sem_linha = [f"{e['FROM']}->{e['TO_PATH']}" for e in arestas
                 if e["EDGE_STATE"] == "OBSERVED" and not e["PROOF_LOCATION"]]
    prova("OBSERVED_EDGE_HAS_LOCATION", "toda aresta observada diz ficheiro e linha",
          not sem_linha, sem_linha)

    # ── 9 · PONTEIRO QUEBRADO ────────────────────────────────────────────────
    # So conta para autoridade que ESTA nesta arvore: cobrar o alvo de uma lei
    # que nem ca esta seria cobrar duas vezes o mesmo defeito.
    quebrados = [f"{e['FROM']} -> {e['TO_PATH']}" for e in arestas
                 if e["PROOF_KIND"] == "ABSENT" and por_id[e["FROM"]]["IN_TREE"]]
    prova("BROKEN_POINTER", "nenhuma autoridade presente aponta para caminho inexistente",
          not quebrados, quebrados)

    # ── 10 · o censo esta atual ──────────────────────────────────────────────
    drift = [a["CARD_ID"] for a in R["AUTHORITIES"] if a["CARD_ID"] not in por_id]
    drift += [c["CARD_ID"] for c in cartoes if c["CARD_ID"] not in set(ids)]
    prova("CONTROL_PLANE_REGISTRY_DRIFT", "o censo corresponde ao registo de hoje",
          not drift, sorted(set(drift)))

    # ── 11 · UM SO PONTO DE ENTRADA DO CONTROL PLANE ─────────────────────────
    entradas = [a["CARD_ID"] for a in R["AUTHORITIES"]
                if a["KIND"] == "REGISTRY" and a["CANONICAL_PATH"].endswith(".md")]
    prova("CANONICAL_CONTROL_ENTRYPOINTS", "existe exatamente uma sala de controle",
          len(entradas) == 1, entradas if len(entradas) != 1 else [])

    # ── 12 · A PORTA COMMITADA E A QUE O CENSO DE HOJE PRODUZ ────────────────
    # `SALA-DE-CONTROLE-SINTONIA.md` e gerada, e o validador do mapa nao a
    # confere — ele confere o indice de fontes e a porta da coleta, que ja
    # existiam quando foi escrito. Sem esta prova, alguem podia mudar o registo,
    # regerar tudo menos ela, e commitar uma porta que descreve um Control Plane
    # que ja nao existe.
    #
    #     UMA PORTA DE ENTRADA DESATUALIZADA E PIOR QUE NENHUMA:
    #     QUEM A LE ACREDITA NELA.
    sala = RAIZ / "SALA-DE-CONTROLE-SINTONIA.md"
    with tempfile.TemporaryDirectory() as td:
        nova = Path(td) / "sala.md"
        r = subprocess.run(
            [sys.executable, str(RAIZ / "controle" / "censo_do_controle.py")],
            capture_output=True, text=True,
            env={**os.environ, "SINTONIA_CONTROLE_SALA": str(nova),
                 "SINTONIA_CONTROLE_CENSO": str(Path(td) / "censo.json")})
        igual = (r.returncode == 0 and nova.exists() and sala.exists()
                 and nova.read_text(encoding="utf-8") == sala.read_text(encoding="utf-8"))
    prova("SALA_DE_CONTROLE_ATUAL",
          "a sala de controle commitada e a que o censo de hoje produz", igual,
          ["regenere: python3 controle/censo_do_controle.py"] if not igual else [])

    # ══ DIVIDA — medida, contada, e com teto que nao sobe ══════════════════

    ausentes = sorted(c["CARD_ID"] for c in cartoes
                      if c["LIFECYCLE"] == "CANONICAL"
                      and c["OBSERVED_STATE"] in ("ABSENT_FROM_SNAPSHOT", "ABSENT"))
    # Uma autoridade canonica que nao existe em lado nenhum e outra coisa, e
    # muito pior: nem branch lateral a guarda.
    perdidas = sorted(c["CARD_ID"] for c in cartoes
                      if c["LIFECYCLE"] == "CANONICAL" and c["OBSERVED_STATE"] == "ABSENT")
    divergentes = sorted(f"{c['CARD_ID']} ({len(c['DIVERGENT_COPIES'])})"
                         for c in cartoes if c["DIVERGENT_COPIES"])
    orfas = sorted(c["CARD_ID"] for c in cartoes
                   if c["OBSERVED_STATE"] == "ORPHAN_IN_TREE")

    # STALE — por regra objetiva, nunca por idade. Uma autoridade e velha nesta
    # foto quando a versao canonica dela vive numa ref que NAO e antepassada do
    # HEAD: o que esta arvore carrega nao e o que o registo diz ser canonico.
    stale = []
    for c in cartoes:
        ref = c.get("CANONICAL_REF", "IN_TREE")
        if ref in ("", "IN_TREE"):
            continue
        alvo = git("rev-parse", "--verify", f"{ref}^{{commit}}")
        if not alvo:
            continue
        antepassado = subprocess.run(
            ["git", "-C", str(RAIZ), "merge-base", "--is-ancestor", alvo, "HEAD"],
            capture_output=True).returncode == 0
        if not antepassado:
            stale.append(f"{c['CARD_ID']} (canonica em {ref}, fora deste HEAD)")

    # Documento que se diz lei e nao esta no registo.
    registados = {a["CANONICAL_PATH"] for a in R["AUTHORITIES"]}
    nao_registados = []
    for p in sorted(rastreados):
        if not p.endswith(".md") or p in registados:
            continue
        if p.startswith(("build/", "research/", "data/", "italia-portale/BASELINE/")):
            continue
        try:
            txt = (RAIZ / p).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(w in txt for w in SE_DIZ_LEI):
            nao_registados.append(p)

    medido = {
        "CANONICAL_AUTHORITY_MISSING": len(ausentes),
        "CANONICAL_AUTHORITY_LOST": len(perdidas),
        "DIVERGENT_CANONICAL_COPY": len(divergentes),
        "STALE_AUTHORITY": len(stale),
        "UNREGISTERED_CANONICAL_DOCUMENT": len(nao_registados),
        "ORPHAN_AUTHORITY": len(orfas),
    }
    detalhes = {
        "CANONICAL_AUTHORITY_MISSING": ausentes,
        "CANONICAL_AUTHORITY_LOST": perdidas,
        "DIVERGENT_CANONICAL_COPY": divergentes,
        "STALE_AUTHORITY": stale,
        "UNREGISTERED_CANONICAL_DOCUMENT": nao_registados,
        "ORPHAN_AUTHORITY": orfas,
    }

    if fixar or not CHAO.exists():
        CHAO.write_text(json.dumps({
            "NOTA": ["O TETO DA DIVIDA DO CONTROL PLANE. Nao e meta: e teto.",
                     "Um numero que sobe reprova. Quando alguem pagar a divida,",
                     "`--fixar` desce o teto — e ele nunca mais sobe."],
            "HEAD": git("rev-parse", "HEAD")[:10],
            "TETO": medido,
            "QUEM": detalhes,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"CHAO_FIXADO=OK · controle/CHAO-DO-CONTROLE.json")
        for k, v in medido.items():
            print(f"    {k:<34} {v}")
        return 0

    teto = json.loads(CHAO.read_text(encoding="utf-8"))["TETO"]
    for k, v in medido.items():
        limite = teto.get(k, 0)
        prova(k, f"nao piorou desde o chao (teto {limite}, hoje {v})",
              v <= limite, detalhes[k] if v > limite else [])

    # ── impressao ────────────────────────────────────────────────────────────
    print("=" * 70)
    print("PORTAO DO CONTROL PLANE")
    print("=" * 70)
    for linha in oks:
        print(linha)
    for nome, desc, det in falhas:
        print(f"  FAIL  {nome:<34} {desc}")
        for d in det[:8]:
            print(f"        {d}")

    print()
    print("A DIVIDA DE HOJE, com nome e numero:")
    for k, v in medido.items():
        print(f"    {k:<34} {v:>3}   (teto {teto.get(k, 0)})")
        for d in detalhes[k][:4]:
            print(f"        · {d}")

    print()
    print("=" * 70)
    if falhas:
        print(f"PORTAO_DO_CONTROLE=FAIL · {len(falhas)} prova(s) reprovada(s)")
        print("=" * 70)
        print("Um conceito, um dono. Um dono, muitos ponteiros.")
        print("Leia SALA-DE-CONTROLE-SINTONIA.md antes de mexer.")
        return 1
    print(f"PORTAO_DO_CONTROLE=PASS · {len(oks)} prova(s)")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
