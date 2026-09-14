#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CENSO GLOBAL DE SOURCE_ID — quem EMITE identidade, e quem apenas a CITA.

A DISTINCAO QUE TEM DE VIR PRIMEIRO
-----------------------------------
Um `SOURCE_ID` aparece em centenas de ficheiros: runs, amostras, ledgers,
relatorios, artefactos de build. Quase todos sao CONSUMIDORES — citam uma
identidade que alguem ja' emitiu. Tratar um nome de ficheiro de run como
«atribuicao de identidade» inventaria emissores que nunca existiram.

    EMISSOR      declara «este ID denota esta fonte»: ID junto de nome/dono
    CONSUMIDOR   usa o ID para se referir a uma fonte ja' existente

Medido em 14/09/2026: um grep por campo `SOURCE_ID:` devolve 192 ficheiros so'
na main. Emissores de verdade sao poucos, e estao nomeados em EMISSORES.

E O QUE ISTO NAO FAZ
--------------------
Nao escreve o Atlas. Nao atribui ID. Nao decide colisao. So' mede, e escreve
a prova em `build/source-registry-reconciliation/`.
"""

import collections
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "build" / "source-registry-reconciliation"
ID = re.compile(r"\b(?:IT|ES|FR|EU|XX|PT|DE)-T\d{1,2}-\d{3}\b")

# ── OS EMISSORES CANDIDATOS. Cada um e' um sitio que DEFINE fontes. ────────
# `build/...` entra porque um deles se chama literalmente MASTER-SOURCE-REGISTRY
# e seria desonesto ignora-lo por viver numa pasta de build.
EMISSORES = [
    "docs/fontes/ATLAS-DE-FONTES-EAME.md",
    "candidatas/ITALY-SOURCE-MASTER-V1.json",
    "candidatas/FONTES-CANDIDATAS.json",
    "build/ITALY-REALITY-HANDOFF-V2/PREVIOUS-HANDOFF/03-SOURCE-REGISTRY/"
    "MASTER-SOURCE-REGISTRY.json",
    "build/ITALY-REALITY-HANDOFF-V2/SOURCES.json",
    "build/ITALY-REALITY-HANDOFF-V2/PREVIOUS-HANDOFF/01-DESIGN-READY/SOURCES/"
    "sources.json",
    "docs/operacao/CONTRATOS-DAS-FONTES-EAME.md",
]


def g(*a):
    return subprocess.run(["git"] + list(a), capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


def refs_remotas():
    return [l.strip() for l in
            g("for-each-ref", "--format=%(refname:short)",
              "refs/remotes/origin").splitlines() if l.strip()]


def blob(ref, caminho):
    s = g("rev-parse", f"{ref}:{caminho}").strip()
    return s if len(s) == 40 else None


# ─────────────────────────────────────────────────────────────────────────────
# LEITORES POR FORMATO — cada emissor tem a sua forma
# ─────────────────────────────────────────────────────────────────────────────
FAIXA = re.compile(
    r"\b((?:IT|ES|FR|EU|XX|PT|DE)-T\d{1,2})-(\d{3})\s*\.\.\s*(\d{3})\b")


def expandir_faixas(texto):
    """`ES-T7-001..027` sao 27 identidades emitidas, nao duas.

    ⚠️ ISTO QUASE CUSTOU 17 IDENTIDADES. O atlas declara uma ficha com
    `SOURCE_ID: ES-T7-001..027` — midia tecnica e rede de assessores. O leitor
    original apanhava `ES-T7-001` e `ES-T7-027` como literais e perdia 002 a
    026. Resultado: 17 IDs apareciam como «citados e nunca emitidos», e um
    atlas reconciliado sem eles teria PERDIDO 17 fontes sem acusar nada.
    """
    fora = []
    for m in FAIXA.finditer(texto):
        base, a, b = m.group(1), int(m.group(2)), int(m.group(3))
        if 0 < b - a <= 200:
            fora += [f"{base}-{n:03d}" for n in range(a, b + 1)]
    return fora


def ler_tabelas(texto):
    """IDs declarados em TABELA de estado — emissao com menos detalhe.

    O atlas tem, alem das fichas, tabelas como
        | SOURCE_ID | camada | origens | estado |
        | `ES-T8-001` | YouTube | 157 canais · 252 videos | ... |
    Isto E' registo de identidade emitida: diz a que camada a fonte pertence e
    em que estado esta. Nao e' ficha completa, e por isso entra com a marca
    `TABELA_DE_ESTADO` — a confianca de campo trata-a como mais fraca.

    ⚠️ Ignorar as tabelas fazia `ES-T8-001` — com 7.634 citacoes no repo —
    aparecer como «citado e nunca emitido». Uma fonte com milhares de
    referencias nao e' um fantasma; era o meu leitor que nao a via.
    """
    fora = []
    for l in texto.splitlines():
        if not l.lstrip().startswith("|"):
            continue
        cels = [c.strip().strip("`").strip() for c in l.strip().strip("|").split("|")]
        if not cels:
            continue
        ids = [c for c in cels[:1] if ID.fullmatch(c)]
        if not ids:
            continue
        fora.append({
            "SOURCE_ID": ids[0],
            "SOURCE_NAME": " · ".join(x for x in cels[1:3] if x)[:160],
            "SOURCE_OWNER": "", "COUNTRY": "", "TERRITORY": ids[0].split("-")[1],
            "URL": "", "URLS_TODAS": "", "URLS_NA_PROSA": "", "DERIVA_DE": "",
            "VERDICT": (cels[-1] if len(cels) > 2 else "")[:90],
            "EVIDENCE_PATH": "", "IDS_NO_MESMO_BLOCO": ids[0],
            "TEM_CERCA_DECLARADA": "TABELA_DE_ESTADO",
            "TITULO_DO_BLOCO": "(tabela de estado)",
        })
    return fora


# ── O QUE NAO E' EMISSAO, por muito que pareca ────────────────────────────
# O preambulo do atlas ENSINA o formato do ID:
#     «Exemplos: `EU-T4-001`, `FR-T3-002`, `ES-T1-001`, `IT-T12-001`.»
# Isso e' documentacao da convencao, nao atribuicao de identidade. O leitor
# original contava-os como fontes e inventava quatro identidades que nunca
# existiram — incluindo `IT-T12-001`, que nao tem ficha nenhuma.
PREAMBULO_EXEMPLO = re.compile(r"^Exemplos?:.*", re.M)


def ler_atlas(texto):
    """Uma ficha por bloco `#### `, e os CAMPOS saem so' da cerca declarada.

    ⚠️ O LEITOR ORIGINAL SANGRAVA ENTRE BLOCOS e produziu 36 «colisoes de
    identidade» que nao existiam: `recherche-entreprises.api.gouv.fr` — uma API
    francesa de empresas — aparecia como rota de fichas espanholas e europeias,
    porque as URLs eram varridas de TODA a prosa do bloco, e a prosa fala de
    outras fontes. Publicar aquele numero teria alarmado a casa por nada.

    Agora: os campos vem da PRIMEIRA cerca ``` depois do titulo, que e' onde o
    atlas os declara (26 dos 29 blocos tem-na). Rota que nao esteja na cerca
    NAO conta para identidade — fica em URLS_NA_PROSA, para leitura.
    """
    fora = []
    for p in re.split(r"\n(?=#### )", texto):
        if not p.startswith("#### "):
            continue
        titulo = p.splitlines()[0].removeprefix("#### ").strip()
        cerca = re.search(r"^#### .*?\n+```\n(.*?)\n```", p, re.S)
        decl = cerca.group(1) if cerca else ""
        # os IDs da ficha vem do titulo e da cerca — nunca da prosa
        cabeca = titulo + "\n" + decl
        ids = list(dict.fromkeys(ID.findall(cabeca) + expandir_faixas(cabeca)))
        if not ids:
            continue

        def campo(*nomes):
            for n in nomes:
                m = re.search(rf"^{n}:\s*(.+?)\s*$", decl, re.M)
                if m and m.group(1).strip():
                    return m.group(1).strip()
            return ""
        urls_decl = re.findall(r"https?://[^\s)\]`<>\"']+", decl)
        urls_prosa = re.findall(r"https?://[^\s)\]`<>\"']+",
                                p[len(titulo):] if not cerca else
                                p.replace(decl, ""))
        # `DERIVA_DE` e' o mecanismo que o atlas JA TEM para «mesma fonte,
        # recorte proprio». O §8 manda nao inventar alias — nao e' preciso.
        deriva = campo("DERIVA_DE", "DERIVES_FROM")
        for i in ids:
            fora.append({
                "SOURCE_ID": i,
                "SOURCE_NAME": campo("SOURCE_NAME", "NOME") or titulo,
                "SOURCE_OWNER": campo("SOURCE_OWNER", "OWNER", "DONO"),
                "COUNTRY": campo("COUNTRY", "PAIS"),
                "TERRITORY": campo("TERRITORY", "TERRITORIO") or i.split("-")[1],
                "URL": (urls_decl[0] if urls_decl else ""),
                "URLS_TODAS": " | ".join(dict.fromkeys(urls_decl))[:400],
                "URLS_NA_PROSA": " | ".join(dict.fromkeys(urls_prosa))[:300],
                "DERIVA_DE": deriva,
                "VERDICT": campo("VERDICT", "VEREDITO"),
                "EVIDENCE_PATH": campo("EVIDENCE_PATH", "REAL_EXAMPLE",
                                       "EXEMPLO_REAL"),
                "IDS_NO_MESMO_BLOCO": " ".join(ids),
                "TEM_CERCA_DECLARADA": "SIM" if cerca else "NAO",
                "TITULO_DO_BLOCO": titulo[:120],
            })
    return fora


def ler_json(texto):
    """JSON de registo: procura objetos com SOURCE_ID."""
    fora = []
    try:
        d = json.loads(texto)
    except Exception:                                            # noqa: BLE001
        return fora

    def andar(o):
        if isinstance(o, dict):
            sid = o.get("SOURCE_ID") or o.get("source_id")
            if isinstance(sid, str) and ID.fullmatch(sid.strip()):
                fora.append({
                    "SOURCE_ID": sid.strip(),
                    "SOURCE_NAME": str(o.get("SOURCE_NAME") or o.get("NAME")
                                       or o.get("nome") or "")[:200],
                    "SOURCE_OWNER": str(o.get("SOURCE_OWNER") or o.get("OWNER")
                                        or o.get("owner") or "")[:200],
                    "COUNTRY": str(o.get("COUNTRY") or o.get("pais") or ""),
                    "TERRITORY": str(o.get("TERRITORY") or o.get("TERRITORIES")
                                     or sid.split("-")[1]),
                    "URL": str(o.get("URL") or o.get("URL_CANONICAL")
                               or o.get("url") or "")[:300],
                    "URLS_TODAS": "",
                    "VERDICT": str(o.get("VERDICT") or o.get("QUALITY_CLASS")
                                   or o.get("ESTADO") or "")[:80],
                    "EVIDENCE_PATH": str(o.get("EVIDENCE_PATH")
                                         or o.get("REAL_EXAMPLE") or "")[:300],
                    "IDS_NO_MESMO_BLOCO": sid.strip(),
                    "TITULO_DO_BLOCO": "",
                })
            for v in o.values():
                andar(v)
        elif isinstance(o, list):
            for v in o:
                andar(v)
    andar(d)
    return fora


def ler(caminho, texto):
    if not caminho.endswith(".md"):
        return ler_json(texto)
    # o preambulo ensina o formato do ID; nao emite identidade
    limpo = PREAMBULO_EXEMPLO.sub("", texto)
    fichas = ler_atlas(limpo)
    ja = {r["SOURCE_ID"] for r in fichas}
    # tabela so' acrescenta o que nenhuma ficha declarou
    return fichas + [r for r in ler_tabelas(limpo) if r["SOURCE_ID"] not in ja]


# ─────────────────────────────────────────────────────────────────────────────
def main():
    sys.stdout.reconfigure(encoding="utf-8")
    SAIDA.mkdir(parents=True, exist_ok=True)
    refs = refs_remotas()
    print(f"refs remotas: {len(refs)}")

    # ── 1 · POPULACOES: por (caminho, blob distinto) ──────────────────────
    # Contar por REF multiplicaria a mesma versao dezenas de vezes.
    registos = []                 # uma linha por (ID, caminho, blob)
    pop_por_caminho = collections.defaultdict(set)
    blobs_por_caminho = collections.defaultdict(dict)   # blob -> [refs]
    # ⚠️ LER AS PONTAS DAS BRANCHES NAO BASTA, E ISSO CUSTOU IDENTIDADES.
    # `ES-T4-004` — com 206 citacoes e tres ficheiros de amostra proprios —
    # aparecia como «citado e nunca emitido». Ele existe em 2 das 31 versoes
    # HISTORICAS do atlas, e em nenhuma das 10 que estao nas pontas. Uma
    # identidade emitida e depois removida continua GASTA: reatribui-la
    # quebraria as referencias que ficaram. Por isso a populacao le-se na
    # historia inteira, nao no estado atual.
    for cam in EMISSORES:
        for r in refs:                       # 1 · as pontas
            b = blob(r, cam)
            if b:
                blobs_por_caminho[cam].setdefault(b, []).append(r)
        for h in g("log", "--all", "--format=%H", "--", cam).split():
            b = blob(h, cam)                 # 2 · toda a historia
            if b:
                blobs_por_caminho[cam].setdefault(b, []).append("hist:" + h[:8])
    for cam, bl in blobs_por_caminho.items():
        for b, rs in bl.items():
            texto = g("cat-file", "-p", b)
            for rec in ler(cam, texto):
                rec["FILE"] = cam
                rec["BLOB"] = b[:12]
                rec["REFS"] = " ".join(x.replace("origin/", "") for x in rs[:6])
                rec["N_REFS"] = len(rs)
                registos.append(rec)
                pop_por_caminho[cam].add(rec["SOURCE_ID"])

    print("\n=== POPULACOES DE EMISSOR (por blob distinto) ===")
    for cam in EMISSORES:
        n = len(pop_por_caminho.get(cam, ()))
        nb = len(blobs_por_caminho.get(cam, {}))
        it = len([x for x in pop_por_caminho.get(cam, ()) if x.startswith("IT-")])
        marca = "" if n else "   (nenhum ID)"
        print(f"  {n:4d} IDs ({it:3d} IT) · {nb:3d} versoes · {cam}{marca}")

    uniao = {r["SOURCE_ID"] for r in registos}
    print(f"\n  UNIAO DE EMISSORES = {len(uniao)} IDs "
          f"({len([x for x in uniao if x.startswith('IT-')])} italianos)")

    # ── 2 · PRIMEIRA ATRIBUICAO: andar a historia dos emissores ───────────
    print("\n=== PRIMEIRA ATRIBUICAO (a historia decide, nao a branch nova) ===")
    commits = []
    for cam in EMISSORES:
        if not pop_por_caminho.get(cam):
            continue
        saida = g("log", "--all", "--format=%H|%cI|%s", "--", cam)
        for l in saida.splitlines():
            if "|" in l:
                h, iso, assunto = l.split("|", 2)
                commits.append((iso, h, cam, assunto))
    commits.sort()                               # mais antigo primeiro
    print(f"  {len(commits)} commits tocaram os emissores")
    primeira = {}
    for iso, h, cam, assunto in commits:
        b = blob(h, cam)
        if not b:
            continue
        for rec in ler(cam, g("cat-file", "-p", b)):
            i = rec["SOURCE_ID"]
            if i not in primeira:
                ramos = g("branch", "-r", "--contains", h).splitlines()
                primeira[i] = {
                    "FIRST_ASSIGNMENT_COMMIT": h[:12],
                    "FIRST_ASSIGNMENT_DATE": iso[:10],
                    "FIRST_ASSIGNMENT_FILE": cam,
                    "FIRST_ASSIGNMENT_BRANCH":
                        (ramos[0].strip().replace("origin/", "")
                         if ramos else "NAO SEI"),
                    "FIRST_ASSIGNMENT_SOURCE": rec["SOURCE_NAME"][:120],
                    "FIRST_ASSIGNMENT_COMMIT_MSG": assunto[:90],
                }
    print(f"  proveniencia reconstruida para {len(primeira)} de {len(uniao)} IDs")
    sem = sorted(uniao - set(primeira))
    if sem:
        print(f"  ⚠️ {len(sem)} sem primeira atribuicao legivel: "
              f"{', '.join(sem[:8])}")

    for r in registos:
        r.update(primeira.get(r["SOURCE_ID"], {
            "FIRST_ASSIGNMENT_COMMIT": "NAO SEI",
            "FIRST_ASSIGNMENT_DATE": "NAO SEI",
            "FIRST_ASSIGNMENT_FILE": "NAO SEI",
            "FIRST_ASSIGNMENT_BRANCH": "NAO SEI",
            "FIRST_ASSIGNMENT_SOURCE": "NAO SEI",
            "FIRST_ASSIGNMENT_COMMIT_MSG": "NAO SEI"}))

    # ── 3 · CONSUMIDORES: quantas referencias dependem de cada ID ─────────
    # Isto importa para julgar colisao: o §7 pergunta «quais referencias ja'
    # dependem dele». Conta-se por CAMINHO distinto, nao por ref, senao 248
    # branches multiplicam a mesma dependencia.
    print("\n=== CONSUMIDORES (quem depende de cada ID) ===")
    consumo = collections.Counter()
    for ref in ("origin/main", "HEAD",
                "origin/claude/italy-source-qualification-v1",
                "origin/claude/passport-tags-italy-v1"):
        saida = g("grep", "-I", "-o", "-h", "-E",
                  r"\b(IT|ES|FR|EU|XX)-T[0-9]{1,2}-[0-9]{3}\b", ref)
        for l in saida.splitlines():
            m = ID.search(l)
            if m:
                consumo[m.group(0)] += 1
    print(f"  {len(consumo)} IDs citados · "
          f"{sum(consumo.values())} citacoes nas 4 linhas principais")
    for r in registos:
        r["N_CITACOES"] = consumo.get(r["SOURCE_ID"], 0)

    # ── 4 · ESCREVER A PROVA ──────────────────────────────────────────────
    cab = ["SOURCE_ID", "SOURCE_NAME", "SOURCE_OWNER", "COUNTRY", "TERRITORY",
           "URL", "URLS_TODAS", "URLS_NA_PROSA", "DERIVA_DE",
           "TEM_CERCA_DECLARADA", "VERDICT", "EVIDENCE_PATH", "FILE", "BLOB",
           "REFS", "N_REFS", "IDS_NO_MESMO_BLOCO", "TITULO_DO_BLOCO",
           "FIRST_ASSIGNMENT_COMMIT", "FIRST_ASSIGNMENT_DATE",
           "FIRST_ASSIGNMENT_FILE", "FIRST_ASSIGNMENT_BRANCH",
           "FIRST_ASSIGNMENT_SOURCE", "FIRST_ASSIGNMENT_COMMIT_MSG",
           "N_CITACOES"]
    with open(SAIDA / "ALL-SOURCE-IDS.csv", "w", encoding="utf-8-sig",
              newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cab, delimiter=";",
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(registos, key=lambda x: (x["SOURCE_ID"], x["FILE"])))

    json.dump({"REFS": len(refs),
               "EMISSORES": {c: sorted(v) for c, v in pop_por_caminho.items()},
               "UNIAO": sorted(uniao),
               "PRIMEIRA_ATRIBUICAO": primeira,
               "CONSUMO": dict(consumo),
               "REGISTOS": registos},
              open(SAIDA / "censo.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\ngravado: {(SAIDA / 'ALL-SOURCE-IDS.csv').relative_to(RAIZ)} "
          f"({len(registos)} linhas)")
    print(f"gravado: {(SAIDA / 'censo.json').relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
