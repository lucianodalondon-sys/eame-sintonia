#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEDE-37-PREP · 3) a porta que ESCREVE a sede provada. Por omissão SÓ MOSTRA; --aplicar escreve.

    UNKNOWN NÃO SE ESCREVE.   SÓ OS CAMPOS DA SEDE MUDAM.   OS DOIS FICHEIROS SÃO LIVROS VIVOS.

Entrada: PAGINAS-DE-SEDE.json (achar_paginas_de_sede.py), onde `SEDE_SEM_REDE` é a sede lida pela regra única
(curadoria/sede_da_fonte) nas páginas JÁ guardadas da própria fonte. Escreve:
  · no contrato do Curator (curadoria/italy_contracts_curator.json): SOURCE_LOCATION, SOURCE_LOCATION_BASIS,
    SOURCE_LOCATION_PRECISION, SOURCE_LOCATION_RULE — o dono da sede, como já é da aquisição;
  · na tabela do coletor (regras/italy_contracts_onboarded.json), SÓ nas linhas que JÁ lá estão:
    SOURCE_LOCATION_RULE (as novas recebem-na pela ponte, `onboardar_rotas_provadas.linha_da_tabela`).
Nunca mexe na ACQUISITION (o CONTRATO_SHA256 das provas de rota fica igual). Uma fonte que JÁ tem sede não é
tocada (JA_TEM). `--excluir` guarda as decisões do dono por tomar (por omissão a IT-T10-021: sede legal x operacional).

    py ferramentas/sede37/escrever_sede.py --paginas <PAGINAS-DE-SEDE.json> --contratos <...curator.json> --tabela <...onboarded.json> [--aplicar]
"""
from __future__ import annotations

import argparse
import copy
import json
import sys

CAMPOS = ("SOURCE_LOCATION", "SOURCE_LOCATION_BASIS", "SOURCE_LOCATION_PRECISION", "SOURCE_LOCATION_RULE")
#: D83.1 (bot Luciano, 26/09): conta a sede LEGAL; a operacional fica registada a parte, na BASE (nao e outro campo).
PENDENTES_DO_DONO = {}
SEDE_OPERACIONAL = {"IT-T10-021": "sede operacional: Faenza (D83.1: conta a sede LEGAL, Roma)"}


class InvarianteQuebrado(Exception):
    pass


def provadas(paginas: dict) -> dict:
    fora = {}
    for l in paginas["FONTES"]:
        s = l.get("SEDE_SEM_REDE") or {}
        if s.get("SOURCE_LOCATION") not in (None, "", "NAO SEI") and s.get("SOURCE_LOCATION_RULE") \
                and str(s.get("SOURCE_LOCATION_BASIS", "")).startswith("PAGINA_GUARDADA_DA_PROPRIA_FONTE"):
            fora[l["SOURCE_ID"]] = {k: s[k] for k in CAMPOS}
            if l["SOURCE_ID"] in SEDE_OPERACIONAL:
                fora[l["SOURCE_ID"]]["SOURCE_LOCATION_BASIS"] += " · " + SEDE_OPERACIONAL[l["SOURCE_ID"]]
    return fora


def planear(paginas, contratos, tabela, excluir=None):
    excluir = PENDENTES_DO_DONO if excluir is None else excluir
    prov = provadas(paginas)
    c2, t2 = copy.deepcopy(contratos), copy.deepcopy(tabela)
    pc = {c["SOURCE_ID"]: c for c in c2["FONTES"]}
    pt = {c["SOURCE_ID"]: c for c in t2["FONTES"]}
    acoes = []
    for sid, campos in sorted(prov.items()):
        a = {"SOURCE_ID": sid, "SOURCE_LOCATION": campos["SOURCE_LOCATION"]}
        if sid in excluir:
            acoes.append(dict(a, ACAO="PENDENTE_DO_DONO", PORQUE=excluir[sid])); continue
        c = pc.get(sid)
        if c is None:
            # LUGAR-DO-PUBLICADOR: fora do Curator mas com linha na tabela do coletor (universidades da Sala) —
            # a linha da tabela E o contrato que a Sala le; escreve-se SO a SOURCE_LOCATION_RULE dela.
            if sid in pt and not pt[sid].get("SOURCE_LOCATION_RULE"):
                pt[sid]["SOURCE_LOCATION_RULE"] = campos["SOURCE_LOCATION_RULE"]
                acoes.append(dict(a, ACAO="APLICA", TABELA="SOURCE_LOCATION_RULE (so a tabela: fora do Curator)")); continue
            if sid in pt:
                igual = pt[sid]["SOURCE_LOCATION_RULE"] == campos["SOURCE_LOCATION_RULE"]
                acoes.append(dict(a, ACAO="JA_APLICADA" if igual else "JA_TEM", PORQUE=pt[sid]["SOURCE_LOCATION_RULE"])); continue
            acoes.append(dict(a, ACAO="SALTA", PORQUE="fora do livro de contratos do Curator e da tabela do coletor")); continue
        if c.get("SOURCE_LOCATION") not in (None, "", "NAO SEI"):
            igual = all(c.get(k) == campos[k] for k in CAMPOS)
            acoes.append(dict(a, ACAO="JA_APLICADA" if igual else "JA_TEM", PORQUE=c.get("SOURCE_LOCATION"))); continue
        c.update(campos)
        na_tabela = sid in pt and not pt[sid].get("SOURCE_LOCATION_RULE")
        if na_tabela:
            pt[sid]["SOURCE_LOCATION_RULE"] = campos["SOURCE_LOCATION_RULE"]
        acoes.append(dict(a, ACAO="APLICA", TABELA="SOURCE_LOCATION_RULE" if na_tabela else "fica para a ponte"))
    invariantes(contratos, c2, {"SOURCE_LOCATION", "SOURCE_LOCATION_BASIS", "SOURCE_LOCATION_PRECISION", "SOURCE_LOCATION_RULE"})
    invariantes(tabela, t2, {"SOURCE_LOCATION_RULE"})
    return c2, t2, acoes


def invariantes(antes, depois, permitidos):
    A, D = antes["FONTES"], depois["FONTES"]
    if [c["SOURCE_ID"] for c in A] != [c["SOURCE_ID"] for c in D]:
        raise InvarianteQuebrado("o livro ganhou, perdeu ou reordenou fontes")
    for a, d in zip(A, D):
        for k in set(a) | set(d):
            if k not in permitidos and a.get(k) != d.get(k):
                raise InvarianteQuebrado("%s: mudou %s, que a porta da sede nao pode mudar" % (a["SOURCE_ID"], k))
            if k in permitidos and a.get(k) not in (None, "", "NAO SEI") and a.get(k) != d.get(k):
                raise InvarianteQuebrado("%s: pisou um %s que ja existia" % (a["SOURCE_ID"], k))


def _ler(caminho):
    b = open(caminho, "rb").read()
    return json.loads(b.decode("utf-8")), ("\r\n" if b"\r\n" in b else "\n"), b.endswith(b"\n")


def _escrever(caminho, d, quebra, fim):
    with open(caminho, "w", encoding="utf-8", newline=quebra) as fh:
        fh.write(json.dumps(d, ensure_ascii=False, indent=1) + ("\n" if fim else ""))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    for x in ("--paginas", "--contratos", "--tabela"):
        ap.add_argument(x, required=True)
    ap.add_argument("--aplicar", action="store_true")
    a = ap.parse_args(argv)
    pag = json.load(open(a.paginas, encoding="utf-8"))
    (c, qc, fc), (t, qt, ft) = _ler(a.contratos), _ler(a.tabela)
    c2, t2, acoes = planear(pag, c, t)
    import collections
    print(json.dumps(dict(collections.Counter(x["ACAO"] for x in acoes)), ensure_ascii=False))
    for x in acoes:
        print("%-16s %-11s %-18s %s" % (x["ACAO"], x["SOURCE_ID"], x["SOURCE_LOCATION"], x.get("TABELA") or x.get("PORQUE") or ""))
    if a.aplicar and any(x["ACAO"] == "APLICA" for x in acoes):
        _escrever(a.contratos, c2, qc, fc)
        _escrever(a.tabela, t2, qt, ft)
        print("escritos: livro de contratos do Curator e tabela do coletor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
