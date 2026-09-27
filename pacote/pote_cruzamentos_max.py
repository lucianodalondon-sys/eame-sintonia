#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O POTE DOS CRUZAMENTOS-MAX — o script que o coordenador roda LOCALMENTE.

    MISSAO   CRUZAMENTOS-MAX (D114). ESPECIE: ADAPTADOR DE ENTREGA (Z-PACOTE). NAO E MOTOR. NAO E TELA.

    python3 pacote/pote_cruzamentos_max.py --entrada ENTRADA-DO-POTE-R7.json --saida POTE-XMAX.json
    python3 pacote/pote_cruzamentos_max.py --entrada ENTRADA-DO-POTE-R7.json \\
            --saida italia-portale/client/sintonia-pote.js [--livro LIVRO-R7.json] [--so-cruzamentos]

POR QUE PRECISA DO COORDENADOR
------------------------------
A LINEAGE da R7 (a entrada do pote, com G0 por item) e o livro com as secoes dos boletins vivem fora do
repo (PARA-O-CASCO-R7/, saida/). Sem a LINEAGE nenhum objeto atravessa o pote — e assim deve ser: prova
que nao chega ao item que passou G0 nao e prova. Este script:

    1. corre motor/cruzamentos_max.py (com o livro, se vier: os 1076 pares por secao da R7);
    2. monta UMA corrida nova: a LINEAGE da R7 VERBATIM, os objetos da R7 (salvo --so-cruzamentos) e os
       objetos CRUZAMENTOS-MAX em portfolio e competitors;
    3. entrega essa corrida ao gerador do dono, pacote/pote_intelligence_casco.py (contrato v2), que confere
       e recusa a vista. Este script nao confere prova nenhuma: quem confere e o pote.

A PROVA E LIGADA A LINEAGE SO POR IDENTIDADE EXATA
--------------------------------------------------
O objeto sai do motor com ITEM_ID = a chave da Sala e DOCUMENT_ID/CORRIDA_UPSTREAM = NAO SEI. Se UMA E SO
UMA entrada da LINEAGE tiver o mesmo SOURCE_ID e o mesmo RAW_OBSERVATION_ID (ou o mesmo ITEM_ID), os tres
campos de identidade dela sao transcritos. Duas ou zero: fica como veio, e o pote recusa. DOCUMENT_ID que a
LINEAGE nao tem continua NAO SEI (defeito C1 da R7) — nunca e fabricado.

UMA CORRIDA NOVA, NAO A R7 DISFARCADA
-------------------------------------
INTELLIGENCE_RUN_ID novo (IR-XMAX-...), CORRIDA_BASE = a da R7. Os objetos da R7 viajam como a R7 os
escreveu; os do CRUZAMENTOS-MAX dizem CRUZAMENTO = ROTULO_X_SUBSTANCIA_CITADA_NO_BOLETIM / PORTFOLIO_MATCH /
COMPETITIVE_SET. Um pote e de UMA corrida; esta e ela.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import cruzamentos_max as XM                       # noqa: E402  (motor/)
import pote_intelligence_casco as POTE             # noqa: E402
from ponte_intelligence_casco import NAO_SEI, LeiViolada, e_ignorancia   # noqa: E402

LACUNA_CS = {"FERRAMENTA": "competitors",
             "GAP": "COMPETITIVE_SET com grao = SUBSTANCIA: o cadastro FTS6 nao tem cultura nem alvo e os "
                    "rotulos dos concorrentes nao foram lidos; cultura x alvo do concorrente = NAO SEI"}


def _chave_lineage(linhagem, p):
    """A UNICA entrada da LINEAGE com a mesma identidade da prova; senao None."""
    def bate(e, campos):
        return all(not e_ignorancia(p.get(c)) and str(e.get(c)) == str(p.get(c)) for c in campos)
    for campos in (("SOURCE_ID", "RAW_OBSERVATION_ID"), ("ITEM_ID",)):
        achadas = [e for e in linhagem if isinstance(e, dict) and bate(e, campos)]
        if achadas:
            ids = {(str(e.get("CORRIDA_UPSTREAM")), str(e.get("ITEM_ID"))) for e in achadas}
            return (achadas[0], "+".join(campos)) if len(ids) == 1 else (None, "AMBIGUA:" + "+".join(campos))
    return None, "SEM_ENTRADA"


def ligar_prova(p: dict, linhagem: list) -> dict:
    e, como = _chave_lineage(linhagem, p)
    out = dict(p, PROVA_LIGADA_A_LINEAGE=como if e else ("NAO:" + como))
    if e is None:
        return out
    for c in ("ITEM_ID", "CORRIDA_UPSTREAM", "RAW_OBSERVATION_ID", "SOURCE_ID"):
        if not e_ignorancia(e.get(c)):
            out[c] = e[c]
    doc = e.get("DOCUMENT_ID")
    doc = doc if not e_ignorancia(doc) else e.get("document_key")
    if e_ignorancia(p.get("DOCUMENT_ID")) and not e_ignorancia(doc):
        out["DOCUMENT_ID"] = doc
    return out


def montar_corrida(entrada: dict, itens: dict, source_head, so_cruzamentos=False) -> dict:
    """A entrada da R7 + os objetos CRUZAMENTOS-MAX -> UMA corrida para o pote v2."""
    if not isinstance(entrada, dict) or e_ignorancia(entrada.get("INTELLIGENCE_RUN_ID")):
        raise LeiViolada("a entrada nao e uma corrida com INTELLIGENCE_RUN_ID")
    linhagem = [e for e in entrada.get("LINEAGE") or [] if isinstance(e, dict)]
    base = entrada["INTELLIGENCE_RUN_ID"]
    novos = {}
    for comp, objs in (itens or {}).items():
        novos[comp] = [dict(o, PROVA=[ligar_prova(p, linhagem) for p in o.get("PROVA") or []]) for o in objs]
    por_ferr = {} if so_cruzamentos else {k: list(v if isinstance(v, list) else [v])
                                          for k, v in (entrada.get("ITENS_POR_FERRAMENTA") or {}).items()}
    for comp, objs in novos.items():
        por_ferr.setdefault(comp, []).extend(objs)
    impressao = hashlib.sha256(json.dumps([base, novos], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return {
        "SCHEMA": f"{XM.SCHEMA}+{entrada.get('SCHEMA', NAO_SEI)}",
        "INTELLIGENCE_RUN_ID": "IR-XMAX-" + impressao[:20],
        "CORRIDA_BASE": base,
        "CORRIDA_BASE_SOURCE_HEAD": entrada.get("SOURCE_HEAD", NAO_SEI),
        "SOURCE_HEAD": source_head,
        "CORTE": entrada.get("CORTE", NAO_SEI),
        "RESULT_STATE": entrada.get("RESULT_STATE", NAO_SEI),
        "SINTETICA": entrada.get("SINTETICA", entrada.get("CORRIDA_SINTETICA", NAO_SEI)),
        "LINEAGE": linhagem,
        "LINEAGE_E": f"a da corrida {base}, verbatim",
        "SIGNALS": [] if so_cruzamentos else list(entrada.get("SIGNALS") or []),
        "REQUIREMENTS": [] if so_cruzamentos else list(entrada.get("REQUIREMENTS") or []),
        "GAPS": ([] if so_cruzamentos else list(entrada.get("GAPS") or [])) + [LACUNA_CS],
        "ITENS_POR_FERRAMENTA": por_ferr,
    }


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    def arg(nome):
        return argv[argv.index(nome) + 1] if nome in argv else None
    entrada, saida = arg("--entrada"), arg("--saida")
    if not entrada or not saida:
        print(__doc__.strip().split("\n\n")[0])
        print("\n  uso: python3 pacote/pote_cruzamentos_max.py --entrada ENTRADA-DO-POTE-R7.json "
              "--saida <POTE.json|italia-portale/client/sintonia-pote.js> [--livro LIVRO.json] [--so-cruzamentos]")
        return 2
    destino = Path(saida)
    if not POTE.destino_permitido(destino):
        print("RECUSADO: dentro de italia-portale/ o pote so pode ir para client/sintonia-pote.js "
              "(fora do Git e do deploy).")
        return 3
    livro = None
    if arg("--livro"):
        livro = json.loads(Path(arg("--livro")).read_text(encoding="utf-8"))
        livro = livro.get("ITENS") if isinstance(livro, dict) else livro
    analise = XM.correr(livro)
    corrida = montar_corrida(json.loads(Path(entrada).read_text(encoding="utf-8")), analise["_ITENS"],
                             analise["LIDO_SOBRE_A_ARVORE"], "--so-cruzamentos" in argv)
    pote = POTE.adaptar(corrida)
    texto = POTE.como_js(pote) if destino.suffix == ".js" else json.dumps(pote, ensure_ascii=False, indent=1) + "\n"
    destino.write_text(texto, encoding="utf-8")
    n = {k: len(e["OBJETOS"]) for k, e in pote["COMPARTIMENTOS"].items() if e["OBJETOS"]}
    rec = Counter(r["MOTIVO"] for r in pote["RECUSADOS"] if r.get("COMPARTIMENTO") in ("portfolio", "competitors"))
    print(f"{POTE.MARCA} · {POTE.CONTRATO} · corrida {pote['INTELLIGENCE_RUN_ID']} (base {corrida['CORRIDA_BASE']})")
    print(f"  objetos por compartimento {n}")
    print(f"  recusados em portfolio/competitors {dict(rec)} · conferir_pote: {len(POTE.conferir_pote(pote))} violacoes")
    print(f"  contagens {analise['CONTAGENS']['DEPOIS']} -> {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
