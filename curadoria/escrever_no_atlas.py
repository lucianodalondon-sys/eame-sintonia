#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Escreve as fichas novas no ATLAS-DE-FONTES-EAME.md — o registry-mae.

    O ATLAS REGISTA FONTES, NAO DESEJOS.
    «Uma linha so existe aqui depois que alguem abriu a fonte, olhou o que
     ela entrega e guardou evidencia disso.»  (o proprio Atlas, no cabecalho)

Estas fichas cumprem isso: cada uma tem exemplo real capturado, amostra
representativa e sha256 em manifesto.

⚠️ O QUE NAO SE MEDIU FICA `NAO SEI`, E ISSO NAO E UMA FICHA INCOMPLETA.
O Atlas tem um VERDICT proprio para isto e uma regra explicita:

    «NÃO SEI — nao foi possivel verificar.
     NUNCA converter "nao consegui verificar" em RED.»

Preencher CROPS com «transversal» porque fica bonito, ou GEOGRAPHIC_GRANULARITY
com «nazionale» por defeito, seria inventar — e o Atlas passaria a mentir com
ar de completo. Um `NAO SEI` honesto e uma instrucao para quem vier medir.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import emparelhar_com_atlas as EM  # noqa: E402

ATLAS = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"

TIPO_POR_FAMILIA = {
    "YOUTUBE": "VIDEO_CHANNEL - canal oficial no YouTube",
    "HTML_SITE": "WEB_PORTAL - portal institucional",
}

# como a caracterizacao fala -> como o Atlas fala
FREQ = {
    "ACTIVE_HIGH_FREQUENCY": "ATIVO - publicacao semanal ou mais frequente",
    "ACTIVE_MEDIUM_FREQUENCY": "ATIVO - publicacao mensal",
    "ACTIVE_LOW_FREQUENCY": "ATIVO - publicacao esparsa",
    "DORMANT": "DORMENTE - sem publicacao ha mais de um ano na amostra",
    "UNKNOWN": "NAO SEI - a amostra nao permitiu medir o ritmo",
}


def ficha(n: dict, f: dict, c: dict | None) -> str:
    """Um bloco ``` com CHAVE: valor, como o scanner do System Map espera."""
    fam = f["FAMILY"]
    car = (c or {}).get("CARACTERIZACAO", {})
    nat = (c or {}).get("SOURCE_NATIVE_ID", "")
    amostra = f["REPRESENTATIVE_SAMPLE_COUNT"]
    periodo = "%s .. %s" % (f["SAMPLE_PERIOD_START"], f["SAMPLE_PERIOD_END"])
    topicos = ", ".join(f["TOPICS_OBSERVED"][:6]) or "NAO SEI"
    geos = ", ".join(f["GEOGRAPHIES_OBSERVED"][:4])

    # ⚠️ GEOGRAFIA DA FONTE != GEOGRAFIA DO FACTO. O Atlas pergunta a
    # granularidade do que ela PUBLICA, e so se responde o que a amostra viu.
    gran = ("regiao (%s) - observado na amostra" % geos) if geos else \
           "NAO SEI - a amostra nao trouxe recorte geografico declarado"

    verd = ("GREEN - fonte aberta, exemplo real capturado e padrao observado "
            "em %d itens" % amostra) if f["SOURCE_PATTERN_STABLE"] == "SIM" else \
           ("YELLOW - fonte aberta e exemplo real capturado, mas o padrao ainda "
            "nao estabilizou em %d itens" % amostra)

    linhas = [
        ("SOURCE_ID", n["SOURCE_ID"]),
        ("SOURCE_NAME", f["NOME"]),
        ("SOURCE_OWNER", (c or {}).get("OWNER") or "NAO SEI - nao medido nesta missao"),
        ("COUNTRY", "ITALY"),
        ("REGION", geos.upper() if geos else "NAO SEI"),
        ("LANGUAGE", "it"),
        ("TERRITORY", n["TERRITORY"]),
        ("SOURCE_TYPE", TIPO_POR_FAMILIA.get(fam, "NAO SEI")),
        ("URL", f["URL"]),
    ]
    if nat and nat != "NAO SEI":
        linhas.append(("PLATFORM_NATIVE_ID", nat))
    linhas += [
        ("ACCESS_METHOD", ("RSS publico do canal (feeds/videos.xml) - sem chave, "
                           "sem sessao") if fam == "YOUTUBE" else
                          "HTTP publico - descoberta por padrao de link na entrada"),
        ("CROPS", ", ".join(f.get("CROPS_OBSERVED", [])[:6]) or
                  "NAO SEI - a amostra nao nomeou culturas"),
        ("TOPICS", topicos),
        ("GEOGRAPHIC_GRANULARITY", gran),
        ("UPDATE_FREQUENCY", FREQ.get(f["ACTIVITY"], "NAO SEI")),
        ("HISTORICAL_DEPTH", f["HISTORICAL_DEPTH_OBSERVED"]),
        ("SOURCE_IDENTITY_PRESERVABLE",
         ("SIM - channel_id nativo (%s), estavel e verificado" % nat) if nat
         else "SIM - endereco canonico estavel"),
        ("DOCUMENT_ID_AVAILABLE",
         "SIM - videoId nativo por item" if fam == "YOUTUBE"
         else "NAO SEI - identidade pelo ENDERECO; a fonte nao expoe id proprio"),
        ("PUBLICATION_DATE_AVAILABLE",
         "SIM - <published> por entrada no feed" if fam == "YOUTUBE"
         else ("SIM - data visivel em %d de %d itens da amostra"
               % (f["DATE_PRESENT_COUNT"], amostra) if f.get("DATE_PRESENT_COUNT")
               else "NAO SEI - a amostra nao trouxe data declarada")),
        ("RAW_EVIDENCE_PRESERVABLE", "SIM - bytes capturados e sha256 em manifesto"),
        ("AUTOMATION_FEASIBILITY",
         "HIGH - rota publica sobre capacidade ja provada" if fam == "YOUTUBE"
         else "MEDIUM - rota generica por descoberta de link"),
        ("COLLECTION_FEASIBILITY",
         "CONTRATO ESCRITO E CANARIO CORRIDO - ver curadoria/italy_contracts_curator.json"),
        ("LEGAL_OR_ACCESS_RISK",
         "canal publico; sem login, sem sessao, sem contorno de muro"),
        ("REAL_EXAMPLE", (f["SAMPLE_ITEMS"][0]["TITLE"][:90] + " (" +
                          f["SAMPLE_ITEMS"][0]["PUBLISHED_AT"] + ")")
         if f["SAMPLE_ITEMS"] else "NAO SEI"),
        ("REPRESENTATIVE_SAMPLE", "%d itens reais, periodo %s" % (amostra, periodo)),
        ("EXPECTED_YIELD", ("%s itens/semana (observado)" % f["EXPECTED_ITEMS_PER_WEEK"])
         if f["EXPECTED_ITEMS_PER_WEEK"] != "NAO SEI"
         else "NAO SEI - amostra insuficiente para estimar ritmo"),
        ("INITIAL_COLLECTION_CADENCE", "%s - %s"
         % (f["INITIAL_COLLECTION_CADENCE"], f["CADENCE_REASON"][:110])),
        ("ADAMA_USE_CASE", "NAO SEI - relevancia tematica medida (%s), uso por definir"
         % (f["RELEVANT_TO_SINTONIA"])),
        ("EVIDENCE", "%s (sha256 em curadoria/REAL-EXAMPLE-MANIFEST-V1.json)"
         % f["CANONICAL_EXAMPLE"]),
        ("VERDICT", verd),
    ]
    if n.get("MESMA_ORGANIZACAO"):
        linhas.insert(9, ("MESMA_ORGANIZACAO",
                          "%s - canal e site sao fontes distintas (COL-LAW-034)"
                          % ", ".join(n["MESMA_ORGANIZACAO"])))

    corpo = "\n".join("%-30s%s" % (k + ":", v) for k, v in linhas)
    return "#### %s · %s\n\n```\n%s\n```\n" % (n["SOURCE_ID"], f["NOME"], corpo)


def main() -> int:
    alloc = json.loads((RAIZ / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json")
                       .read_text(encoding="utf-8"))
    car = json.loads((RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json")
                     .read_text(encoding="utf-8"))
    contr = json.loads((RAIZ / "curadoria" / "italy_contracts_curator.json")
                       .read_text(encoding="utf-8"))
    porid = {c["CANDIDATE_ID"]: c for c in car["FONTES"]}
    porsid = {c["SOURCE_ID"]: c for c in contr["FONTES"]}

    # ⚠️ NUNCA REESCREVER O ATLAS: ACRESCENTAR. O ficheiro tem 7310 linhas de
    # prosa cuidada e um scanner que a le. Uma reescrita perderia tudo o que
    # nao percebi — e o que nao percebi e a maior parte.
    if not ATLAS.exists():
        print("Atlas nao existe nesta worktree: %s" % ATLAS)
        return 1
    txt = ATLAS.read_text(encoding="utf-8")

    ja = set(a["SOURCE_ID"] for a in EM.ler_atlas())
    blocos, escritos = [], []
    for n in alloc["NOVAS"]:
        if n["SOURCE_ID"] in ja:
            continue
        f = porid[n["CANDIDATE_ID"]]
        blocos.append(ficha(n, f, porsid.get(n["SOURCE_ID"])))
        escritos.append(n["SOURCE_ID"])

    if not blocos:
        print("nada a escrever")
        return 0

    cab = (
        "\n---\n\n"
        "## ONDA SOURCE CURATOR — 2026-09-20\n\n"
        "*%d fontes italianas trazidas pela fila de candidatas, todas com exemplo real\n"
        "capturado, amostra representativa (717 itens no total da onda) e contrato\n"
        "executavel escrito em `curadoria/italy_contracts_curator.json`.*\n\n"
        "> **O que estas fichas NAO afirmam.** Nenhuma delas foi coletada ainda. Ter\n"
        "> contrato e canario nao e ter corpus: `FONTE PRONTA != FONTE COLETADA`.\n"
        "> Os campos a `NAO SEI` sao medidas que faltam, nao defeitos da fonte —\n"
        "> e o Atlas proibe converter «nao consegui verificar» em RED.\n\n"
        "> **Canal e site sao duas fontes** (COL-LAW-034). Onde a mesma organizacao\n"
        "> aparece duas vezes, o campo `MESMA_ORGANIZACAO` guarda o parentesco sem\n"
        "> fundir as identidades.\n\n" % len(blocos))

    ATLAS.write_text(txt.rstrip() + "\n" + cab + "\n".join(blocos), encoding="utf-8")

    print("fichas escritas   %d" % len(blocos))
    print("Atlas antes       %d fichas (versao do COORDINATOR)" % len(ja))
    print("Atlas depois      %d fichas (no disco desta worktree)"
          % len(EM.ler_atlas(do_disco=True)))
    (RAIZ / "curadoria" / "ATLAS-WRITE-V1.json").write_text(
        json.dumps({"ESCRITOS": escritos, "TOTAL": len(escritos),
                    "ATLAS_ANTES": len(ja)}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
