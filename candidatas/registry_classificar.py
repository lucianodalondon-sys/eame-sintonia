#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLASSIFICAR CADA SOURCE_ID — e a soma tem de fechar.

OS SETE ESTADOS, E O QUE CADA UM OBRIGA
---------------------------------------
    SAME_ID_SAME_SOURCE        aparece em mais de um registo, mesma fonte.
                               Funde-se. E' o caso facil e o mais comum.
    SAME_ID_DIFFERENT_SOURCE   o mesmo numero foi dado a duas fontes.
                               IDENTITY_COLLISION — nao se escolhe sozinho.
    SAME_SOURCE_MULTIPLE_IDS   a mesma fonte levou dois numeros.
                               DUPLICATE_IDENTITY_ASSIGNMENT — nao se apaga
                               nenhum.
    ONLY_IN_ONE_BRANCH         existe num sitio so'. Entra, com a proveniencia.
    MISSING_FROM_CURRENT_ATLAS emitido, e ausente do atlas da linha corrente.
                               E' a conta que mede o prejuizo de nao reconciliar.
    HISTORICAL_RED             ficha com veredito negativo. O ID continua gasto.
    UNKNOWN                    nao sei, e digo que nao sei.

COMO SE DECIDE SE DUAS FICHAS SAO «A MESMA FONTE»
-------------------------------------------------
Nao por dominio e nao por dono — o §13 proibe as duas coisas, porque uma
organizacao tem varias fontes e um dominio serve varias rotas. Compara-se:

    1 · rota canonica igual (host + caminho)      -> mesma fonte
    2 · nome normalizado igual                    -> mesma fonte
    3 · so' o host igual                          -> NAO decide. Fica para
                                                     leitura, marcado.

E QUANDO OS CAMPOS DIFEREM
--------------------------
Ordem de confianca do §11, aplicada campo a campo: evidencia real preservada >
fonte aberta > contrato canonico > dado observado > documentacao historica >
descricao sem prova. Nunca «a branch mais nova vence». Ausencia fica UNKNOWN.
"""

import collections
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "build" / "source-registry-reconciliation"
CENSO = json.loads((SAIDA / "censo.json").read_text(encoding="utf-8"))
ID = re.compile(r"\b(?:IT|ES|FR|EU|XX|PT|DE)-T\d{1,2}-\d{3}\b")

# A linha corrente — cujo atlas vai receber a reconciliacao
ATLAS_CORRENTE = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"

VERMELHO = re.compile(r"\bRED\b|BLOQUEAD|NAO SEI|NÃO SEI|REJECT|MORTA|"
                      r"FORA DO AR|INACESS", re.I)


def norm_nome(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\b(o|a|os|as|de|da|do|das|dos|e|the|of|del|della|dei|il|la|"
               r"le|i|gli|un|una)\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())[:90]


def rota(u):
    if not u:
        return ""
    p = urlparse(u if "//" in u else "https://" + u)
    h = (p.netloc or "").lower().removeprefix("www.")
    return (h + p.path.rstrip("/")).lower()


def host(u):
    if not u:
        return ""
    p = urlparse(u if "//" in u else "https://" + u)
    return (p.netloc or "").lower().removeprefix("www.")


# ── CONFIANCA DO CAMPO (§11) — quem ganha quando dois registos discordam ──
def confianca(rec):
    """Quanto vale este registo como fonte de verdade de campo."""
    p = 0
    if rec.get("EVIDENCE_PATH"):
        p += 50                    # 1 · evidencia preservada
    if rec.get("URL"):
        p += 20                    # 2 · rota declarada
    if rec["FILE"].endswith("ATLAS-DE-FONTES-EAME.md"):
        p += 15                    # 3 · o dono declarado do conceito
    if rec.get("VERDICT"):
        p += 10                    # 4 · veredito observado
    if rec.get("SOURCE_OWNER"):
        p += 5                     # 5 · dono nomeado
    # ⚠️ NAO ha ponto por «branch mais nova». O §11 proibe-o por escrito.
    return p


def reconciliar_campos(recs):
    """Campo a campo, o valor com melhor prova. Divergencia fica escrita."""
    fora, divergencias = {}, []
    for c in ("SOURCE_NAME", "SOURCE_OWNER", "COUNTRY", "TERRITORY", "URL",
              "VERDICT", "EVIDENCE_PATH"):
        vistos = {}
        for r in sorted(recs, key=confianca, reverse=True):
            v = (r.get(c) or "").strip()
            if v:
                vistos.setdefault(v, r)
        if not vistos:
            fora[c] = "UNKNOWN"
            continue
        fora[c] = next(iter(vistos))
        if len(vistos) > 1:
            divergencias.append(
                f"{c}: escolhido «{fora[c][:44]}» (prova "
                f"{confianca(vistos[fora[c]])}) sobre "
                + " / ".join(f"«{k[:34]}» ({confianca(v)})"
                             for k, v in list(vistos.items())[1:3]))
    fora["DIVERGENCIAS"] = " || ".join(divergencias)
    return fora


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    regs = CENSO["REGISTOS"]
    uniao = set(CENSO["UNIAO"])
    por_id = collections.defaultdict(list)
    for r in regs:
        por_id[r["SOURCE_ID"]].append(r)

    atlas_hoje = set(ID.findall(ATLAS_CORRENTE.read_text(encoding="utf-8")))
    print(f"atlas da linha corrente: {len(atlas_hoje)} IDs")
    print(f"populacao emitida: {len(uniao)} IDs")

    # ── mapa fonte -> IDs, para achar a mesma fonte com dois numeros ──────
    por_rota, por_nome = collections.defaultdict(set), collections.defaultdict(set)
    for r in regs:
        if r.get("URL"):
            por_rota[rota(r["URL"])].add(r["SOURCE_ID"])
        n = norm_nome(r.get("SOURCE_NAME"))
        if len(n) > 12:
            por_nome[n].add(r["SOURCE_ID"])

    linhas, colisoes, duplicadas = [], [], []
    for i in sorted(uniao):
        recs = por_id[i]
        campos = reconciliar_campos(recs)

        # mesma fonte, dois numeros?
        irmaos = set()
        for r in recs:
            if r.get("URL"):
                irmaos |= por_rota.get(rota(r["URL"]), set())
            n = norm_nome(r.get("SOURCE_NAME"))
            if len(n) > 12:
                irmaos |= por_nome.get(n, set())
        irmaos.discard(i)
        # so' conta irmao do MESMO pais e territorio: FR-T3-001 e IT-T3-001
        # sao a mesma NATUREZA declarada em paises diferentes, nao duplicata
        irmaos = {x for x in irmaos
                  if x.split("-")[0] == i.split("-")[0]
                  and x.split("-")[1] == i.split("-")[1]}

        # ⚠️ TRES COISAS DIFERENTES ESTAVAM A ENTRAR COMO «MESMA FONTE», e
        # nenhuma das tres era. Medido em 14/09/2026 nos «33 pares»:
        #
        #   1 · MEMBROS DA MESMA FAIXA. `ES-T7-001..027` e' UMA ficha que
        #       declara 27 fontes da mesma natureza — 27 orgaos de imprensa
        #       tecnica, nao 27 copias de um. Ligar-los com DERIVA_DE seria
        #       exatamente o que o §8 proibe.
        #   2 · MESMO DONO, FONTES DIFERENTES. `IT-T10-004` e' o registo do
        #       VINHO (Cantina Italia) e `IT-T10-005` o do AZEITE (Frantoio
        #       Italia): mesmo ICQRF, mesmo portal, produtos diferentes.
        #   3 · NOME TIRADO DA PROSA. `IT-T3-003` (SIMFITO Campania) e
        #       `IT-T3-010` (APOL Lecce) casaram porque o meu leitor apanhou
        #       uma referencia de ficheiro como nome.
        #
        # Regra nova: irmao exige ROTA igual E dono compativel, e nunca vale
        # entre membros de uma faixa.
        mesma_faixa = {x for x in irmaos
                       if any(i in (r.get("IDS_NO_MESMO_BLOCO") or "").split()
                              and x in (r.get("IDS_NO_MESMO_BLOCO") or "").split()
                              for r in regs)}
        irmaos -= mesma_faixa
        donos_meus = {(r.get("SOURCE_OWNER") or "").strip().lower()
                      for r in recs if r.get("SOURCE_OWNER")}
        confirmados = set()
        for x in irmaos:
            rx = por_id[x]
            rotas_x = {rota(r["URL"]) for r in rx if r.get("URL")}
            rotas_i = {rota(r["URL"]) for r in recs if r.get("URL")}
            if not (rotas_x and rotas_i and rotas_x & rotas_i):
                continue                      # sem rota comum, nao decide
            nomes_x = {norm_nome(r.get("SOURCE_NAME")) for r in rx}
            nomes_i = {norm_nome(r.get("SOURCE_NAME")) for r in recs}
            if not (nomes_x & nomes_i):
                continue                      # rota igual e nome diferente ->
                                              # mesmo dono, outra fonte
            donos_x = {(r.get("SOURCE_OWNER") or "").strip().lower()
                       for r in rx if r.get("SOURCE_OWNER")}
            if donos_meus and donos_x and not (donos_meus & donos_x):
                continue
            confirmados.add(x)
        irmaos = confirmados

        # o mesmo numero em fontes diferentes?
        rotas = {rota(r["URL"]) for r in recs if r.get("URL")}
        nomes = {norm_nome(r.get("SOURCE_NAME")) for r in recs
                 if len(norm_nome(r.get("SOURCE_NAME"))) > 12}
        conflito = len(rotas) > 1 and len(nomes) > 1

        vermelho = any(VERMELHO.search(r.get("VERDICT") or "") for r in recs)
        onde = {r["FILE"] for r in recs}
        n_versoes = len({r["BLOB"] for r in recs})

        if conflito:
            estado = "SAME_ID_DIFFERENT_SOURCE"
            colisoes.append((i, recs, rotas, nomes))
        elif irmaos:
            estado = "SAME_SOURCE_MULTIPLE_IDS"
            duplicadas.append((i, sorted(irmaos)))
        elif i not in atlas_hoje:
            estado = "MISSING_FROM_CURRENT_ATLAS"
        elif vermelho:
            estado = "HISTORICAL_RED"
        elif n_versoes > 1 or len(onde) > 1:
            estado = "SAME_ID_SAME_SOURCE"
        else:
            estado = "ONLY_IN_ONE_BRANCH"

        pa = recs[0]
        linhas.append({
            "SOURCE_ID": i, "ESTADO": estado,
            **{k: campos[k] for k in ("SOURCE_NAME", "SOURCE_OWNER", "COUNTRY",
                                      "TERRITORY", "URL", "VERDICT",
                                      "EVIDENCE_PATH")},
            "NO_ATLAS_CORRENTE": "SIM" if i in atlas_hoje else "NAO",
            "IRMAOS_MESMA_FONTE": " ".join(sorted(irmaos)),
            "N_REGISTOS": len(recs), "N_VERSOES": n_versoes,
            "ONDE": " | ".join(sorted(x.split("/")[-1] for x in onde)),
            "N_CITACOES": max(r.get("N_CITACOES", 0) for r in recs),
            "FIRST_ASSIGNMENT_COMMIT": pa["FIRST_ASSIGNMENT_COMMIT"],
            "FIRST_ASSIGNMENT_DATE": pa["FIRST_ASSIGNMENT_DATE"],
            "FIRST_ASSIGNMENT_BRANCH": pa["FIRST_ASSIGNMENT_BRANCH"],
            "FIRST_ASSIGNMENT_FILE": pa["FIRST_ASSIGNMENT_FILE"].split("/")[-1],
            "FIRST_ASSIGNMENT_SOURCE": pa["FIRST_ASSIGNMENT_SOURCE"],
            "DIVERGENCIAS": campos["DIVERGENCIAS"],
        })

    c = collections.Counter(l["ESTADO"] for l in linhas)
    print("\n=== CLASSIFICACAO ===")
    for k, v in sorted(c.items(), key=lambda x: -x[1]):
        print(f"  {k:28s} {v}")
    print(f"  {'SOMA':28s} {sum(c.values())}  "
          f"{'✓ fecha em ' + str(len(uniao)) if sum(c.values()) == len(uniao) else '✗ NAO FECHA'}")

    # ── IDs CITADOS E NUNCA EMITIDOS ──────────────────────────────────────
    citados = set(CENSO["CONSUMO"])
    fantasmas = sorted(citados - uniao)
    print(f"\n=== IDs CITADOS E NUNCA EMITIDOS: {len(fantasmas)} ===")
    for f in fantasmas:
        print(f"  {f}  ·  {CENSO['CONSUMO'][f]} citacoes")
    print("  ⚠️ estes nao sao perda de reconciliacao: nenhum registo os emitiu.")

    # ── escrever prova ────────────────────────────────────────────────────
    cab = list(linhas[0])
    for nome, dados in (("BRANCH-COVERAGE.csv", linhas),):
        with open(SAIDA / nome, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cab, delimiter=";",
                               extrasaction="ignore")
            w.writeheader()
            w.writerows(dados)

    with open(SAIDA / "COLLISIONS.csv", "w", encoding="utf-8-sig",
              newline="") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["SOURCE_ID", "N_FONTES_DIFERENTES", "ROTAS", "NOMES",
                    "N_CITACOES", "FIRST_ASSIGNMENT", "RESOLUCAO_PROPOSTA"])
        for i, recs, rotas, nomes in colisoes:
            w.writerow([i, len(rotas), " | ".join(sorted(rotas))[:300],
                        " | ".join(sorted(nomes))[:300],
                        max(r.get("N_CITACOES", 0) for r in recs),
                        recs[0]["FIRST_ASSIGNMENT_COMMIT"] + " " +
                        recs[0]["FIRST_ASSIGNMENT_DATE"],
                        "IDENTITY_COLLISION — nao resolver sozinho"])

    with open(SAIDA / "DUPLICATE-SOURCES.csv", "w", encoding="utf-8-sig",
              newline="") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["SOURCE_ID", "IRMAOS", "NOME", "URL", "FIRST_ASSIGNMENT",
                    "CLASSIFICACAO"])
        for i, irm in duplicadas:
            l = next(x for x in linhas if x["SOURCE_ID"] == i)
            w.writerow([i, " ".join(irm), l["SOURCE_NAME"][:80], l["URL"][:120],
                        f'{l["FIRST_ASSIGNMENT_COMMIT"]} {l["FIRST_ASSIGNMENT_DATE"]}',
                        "DUPLICATE_IDENTITY_ASSIGNMENT"])

    json.dump({"LINHAS": linhas, "COLISOES": [x[0] for x in colisoes],
               "DUPLICADAS": {i: irm for i, irm in duplicadas},
               "FANTASMAS": fantasmas,
               "ATLAS_CORRENTE": sorted(atlas_hoje)},
              open(SAIDA / "classificacao.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\ngravado: BRANCH-COVERAGE.csv ({len(linhas)}) · "
          f"COLLISIONS.csv ({len(colisoes)}) · "
          f"DUPLICATE-SOURCES.csv ({len(duplicadas)})")
    if sum(c.values()) != len(uniao):
        sys.exit(1)


if __name__ == "__main__":
    main()
