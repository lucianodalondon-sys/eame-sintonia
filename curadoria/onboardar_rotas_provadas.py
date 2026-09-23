#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ONBOARDAR ROTAS PROVADAS — a capacidade que faltava entre o Curator e o coletor.

    ELEGIVEL SEM CONTRATO NAO E UMA DECISAO QUE FALTA. E UMA PONTE QUE FALTA.

MEDIDO (ROTAS-ELEGIVEIS-V1, 2026-09-22). O coletor so colhe quem tem contrato
em `regras/italy_contracts.mjs`, e as fontes do Curator so la entram por uma
linha em `regras/italy_contracts_onboarded.json`. Essa tabela foi escrita UMA
vez (INTEGRACAO-04A, 18 linhas, 2026-09-20). Toda a fonte que o portao aprovou
DEPOIS — com rota declarada pelo Curator e tudo — ficou em
`ELIGIBLE_WITHOUT_CONTRACT`. Nao por decisao: por nao haver caminho.

Este ficheiro e esse caminho, e so esse. Uma linha entra na tabela quando as
TRES coisas sao verdade ao mesmo tempo, no instante da corrida:

    1. o portao (`collection_gate.avaliar`) diz ELIGIBLE, no livro desta arvore
    2. a fonte nao tem contrato no coletor (o dono e `italy_contracts.mjs`)
    3. o canario real (`medidas/canario_rotas_elegiveis.py`) deu ROUTE_PROVEN
       com a MESMA aquisicao que vai ser escrita, e nenhuma outra fonte provou
       a rota pelo mesmo documento (duas fichas, uma fonte: nao se contrata a
       segunda — e decisao de identidade, nao de rota)

A aquisicao escrita e a do Curator, byte a byte. Nada se inventa aqui.

    POR OMISSAO SO MOSTRA. `--aplicar` escreve a tabela.

O que NAO faz: nao promove, nao mexe no livro, na fila, no portao nem na
rede, e nao declara RECOLLECTION (quem nao mediu nao declara).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import collection_gate as G      # noqa: E402

TABELA = RAIZ / "regras" / "italy_contracts_onboarded.json"
CANARIO = RAIZ / "curadoria" / "ROTAS-ELEGIVEIS-V1.json"
CURATOR = RAIZ / "curadoria" / "italy_contracts_curator.json"


def ids_com_contrato_no_coletor() -> set[str]:
    r = subprocess.run(
        ["node", "-e", 'import("./regras/italy_contracts.mjs").then(m=>'
         'console.log(JSON.stringify(Object.keys(m.CONTRACTS))))'],
        cwd=RAIZ, capture_output=True, text=True, timeout=120)
    if r.returncode:
        raise RuntimeError("o dono dos contratos nao carregou: " + r.stderr[-300:])
    return set(json.loads(r.stdout))


def _json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _site(url) -> str:
    h = urlparse(url or "").hostname or ""
    return h[4:] if h.startswith("www.") else h


def planear(*, ctx: dict | None = None, canario: dict | None = None,
            curator: dict | None = None, com_contrato: set[str] | None = None) -> dict:
    ctx = ctx if ctx is not None else G._contexto()
    canario = canario if canario is not None else _json(CANARIO)
    curator = curator if curator is not None else {
        c["SOURCE_ID"]: c for c in _json(CURATOR)["FONTES"]}
    com_contrato = com_contrato if com_contrato is not None else ids_com_contrato_no_coletor()
    provas = {l["SOURCE_ID"]: l for l in canario["LINHAS"]}
    # o documento que provou a rota — dois IDs pelo mesmo documento sao uma fonte
    dono_do_doc = {}
    for l in canario["LINHAS"]:
        if l.get("VEREDITO") == "ROUTE_PROVEN":
            dono_do_doc.setdefault(l["CANARIO"]["URL"], l["SOURCE_ID"])
    # ...e contra quem JA tem contrato no coletor: o mesmo site com o mesmo padrao de
    # materias colhe os mesmos documentos (BC2, 23/09: duas paginas de «seleccao de
    # idioma» da ARPAE, com OWNER «Italiano», iam duplicar a fonte ja contratada).
    ja_contratada = {}
    for s in sorted(com_contrato):
        a = (curator.get(s) or {}).get("ACQUISITION") or {}
        if a.get("LINK_PATTERN"):
            ja_contratada.setdefault((_site(a.get("INDEX_URL")), a["LINK_PATTERN"]), s)
    entra, fica = [], []
    for sid in G.elegiveis(ctx=ctx):
        if sid in com_contrato:
            continue
        p, c = provas.get(sid), curator.get(sid)
        porque = None
        if not c:
            porque = "sem contrato do Curator nesta arvore"
        elif not p or p.get("VEREDITO") != "ROUTE_PROVEN":
            porque = "canario nao provou a rota: %s — %s" % (
                (p or {}).get("VEREDITO", "SEM_CANARIO"), (p or {}).get("CAUSA", ""))
        elif (p.get("INDEX_URL"), p.get("LINK_PATTERN")) != (
                c["ACQUISITION"].get("INDEX_URL"), c["ACQUISITION"].get("LINK_PATTERN")):
            porque = "o canario provou OUTRA aquisicao que nao a do contrato actual"
        elif dono_do_doc.get(p["CANARIO"]["URL"]) != sid:
            porque = ("DUPLICADA: a rota chega ao mesmo documento que %s — duas fichas, "
                      "uma fonte; decisao de identidade, nao de rota"
                      % dono_do_doc[p["CANARIO"]["URL"]])
        elif (_site(c["ACQUISITION"].get("INDEX_URL")),
              c["ACQUISITION"].get("LINK_PATTERN")) in ja_contratada:
            porque = ("DUPLICADA de fonte ja contratada: %s — mesmo site e mesmo padrao de "
                      "materias; decisao de identidade, nao de rota"
                      % ja_contratada[(_site(c["ACQUISITION"].get("INDEX_URL")),
                                       c["ACQUISITION"].get("LINK_PATTERN"))])
        if porque:
            fica.append({"SOURCE_ID": sid, "PORQUE": porque})
            continue
        entra.append(linha_da_tabela(c, p, canario.get("GERADO_EM", "NAO SEI")))
    return {"ENTRA": entra, "FICA": fica}


def linha_da_tabela(c: dict, p: dict, quando: str) -> dict:
    k = p["CANARIO"]
    return {
        "SOURCE_ID": c["SOURCE_ID"], "OWNER": c.get("OWNER"), "NAME": c.get("NAME"),
        "TERRITORY": c.get("TERRITORY"), "BATCH_ID": c.get("BATCH_ID"),
        "OUTPUT_TYPE": c.get("OUTPUT_TYPE"), "ACQUISITION": c["ACQUISITION"],
        "EVIDENCE": "curadoria/ROTAS-ELEGIVEIS-V1.json",
        "SONDAGEM": {
            "SONDADO_EM": quando[:10],
            "REGRA": "medidas/canario_rotas_elegiveis.py: robots pela casa, INDEX_URL, "
                     "links pelo motor do coletor, alvo aberto e retratado, gate CAPA != MATERIA",
            "ENTRADA_STATUS": p.get("INDEX_HTTP"), "DOCUMENTO": k["URL"],
            "DOCUMENTO_ASSINATURA": "HTML", "DOCUMENTO_BYTES": k["BYTES"],
            "ALVOS_DESCOBERTOS": p.get("LINKS_DE_DETALHE"),
            "HTML_KIND": k["HTML_KIND"], "PARAGRAPH_CHARACTERS": k["PARAGRAPH_CHARACTERS"],
        },
        "ONBOARDED_BY": "ROTAS-ELEGIVEIS-V1 (canario de rota %s) — curadoria/onboardar_rotas_provadas.py"
                        % quando[:10],
    }


def aplicar(entra: list[dict]) -> int:
    t = _json(TABELA)
    ja = {f["SOURCE_ID"] for f in t["FONTES"]}
    novas = [l for l in entra if l["SOURCE_ID"] not in ja]
    t["FONTES"].extend(novas)
    TABELA.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return len(novas)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    plano = planear()
    for l in plano["ENTRA"]:
        print("ENTRA  %s  %s" % (l["SOURCE_ID"], l["ACQUISITION"]["INDEX_URL"]))
    for l in plano["FICA"]:
        print("FICA   %s  %s" % (l["SOURCE_ID"], l["PORQUE"][:140]))
    print("ENTRA=%d FICA=%d" % (len(plano["ENTRA"]), len(plano["FICA"])))
    if "--aplicar" in argv:
        print("escritas na tabela: %d" % aplicar(plano["ENTRA"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
