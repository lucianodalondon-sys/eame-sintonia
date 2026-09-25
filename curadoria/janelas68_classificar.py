#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JANELAS-68 · passo 1: classificar pela FORMA real as fontes de janela D29 que chumbaram no canario.

SO LEITURA do vivo (source-curator-service-v1) e das medidas P1g; SEM rede.
Fontes: FILA-UNICA-CORRESPONDENCIA-V1 (quais sao de janela), SOURCE-ID-ALLOCATION (CAND -> SOURCE_ID),
LIFECYCLE-LEDGER (estado), italy_contracts_curator (contrato), LIFECYCLE-EVIDENCE (canario e reparo:
retrato da pagina) e JANELAS-REGIOES-V1 (formato e boletim de exemplo medidos na P1g).

Formas: PDF · PAGINA_BOLETIM · LISTA_NOTICIA · JS_API · MENU · MORTA · LOGIN · NAO_SEI
"""
from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
VIVO = Path(r"C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/curadoria")
SAIDA = RAIZ / "curadoria" / "JANELAS-68-FORMAS-V1.json"
JANELA = ("JANELA_", "BOLLETTINI_DIFESA", "BOLLETTINI_AGROMETEO", "CONSORZI_DIFESA", "SERVIZI_TECNICI")


def _j(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _git_json(ref, caminho):
    out = subprocess.run(["git", "show", "%s:%s" % (ref, caminho)], cwd=str(RAIZ), capture_output=True,
                         text=True, encoding="utf-8", check=True).stdout
    return json.loads(out)


def forma(c: dict) -> tuple[str, str]:
    """Decide a forma pela prova, na ordem do mais forte para o mais fraco. Devolve (forma, porque)."""
    can, rep, p1g = c.get("CANARY") or {}, c.get("REPARO") or {}, c.get("P1G") or {}
    ret = rep.get("ENTRADA_RETRATO") or {}
    http = can.get("HTTP")
    motivo = (rep.get("MOTIVO") or "") + " " + (c.get("RAZAO_DO_ESTADO") or "")
    url = c["URL"].lower()
    ex = ((p1g.get("EXEMPLO") or {}).get("URL") or "").lower()
    if http in (401, 403) or "LOGIN" in motivo or p1g.get("ESTADO_MEDIDO") == "LOGIN_OU_BLOQUEIO":
        return "LOGIN", "canario HTTP %s / %s" % (http, motivo.strip()[:60])
    if http in (0, None) and not ret and "SEM_LIGACAO" in (p1g.get("ESTADO_MEDIDO") or "SEM_LIGACAO"):
        return "MORTA", "canario sem ligacao (HTTP %s) e sem retrato de pagina" % http
    if isinstance(http, int) and http >= 404:
        return "MORTA", "canario HTTP %s" % http
    lidas = " ".join(x.get("URL", "") for x in (rep.get("PAGINAS_LIDAS") or [])).lower()
    anexo = re.compile(r"allegato\.aspx|serveattachment|/documents/|\.pdf|pdf\?|/e/pdf|drive\.google")
    if "drive.google" in ex or "drive.google" in lidas:
        return "PDF", "os boletins estao em ficheiros externos (Google Drive): %s" % (ex or lidas)[-50:]
    if ("ENTRADA_NAO_E_HTML" in motivo or url.endswith(".pdf") or p1g.get("FORMATO") == "PDF"
            or anexo.search(ex) or anexo.search(lidas)):
        return "PDF", "entrada nao e HTML ou os boletins sao PDF (P1g formato %s, exemplo %s)" % (
            p1g.get("FORMATO"), ex[-40:] or "-")
    if (rep.get("PORQUE") or "").startswith("contrato reparado"):
        return "REPARADO_A_REVER", "o reparo ja achou itens (%s); falta a revisao humana do item" % (rep.get("PORQUE") or "")[19:80]
    if "ENTRADA_E_MATERIA" in motivo or ret.get("CAPA_OU_MATERIA") == "MATERIA_PROVAVEL":
        return "PAGINA_BOLETIM", "a entrada ja e o conteudo (%s)" % (rep.get("MOTIVO") or ret.get("CAPA_OU_MATERIA"))
    if (ret.get("PARAGRAPH_CHARACTERS", 1) == 0 and (ret.get("LINKS") or 0) < 20
            and (ret.get("BYTES") or _bytes(rep) or 99999) < 6000):
        return "JS_API", "pagina quase vazia no HTML (%s bytes, %s links, 0 texto): conteudo vem por JS/API" % (
            ret.get("BYTES") or _bytes(rep), ret.get("LINKS"))
    if "FAMILIA_E_MENU" in motivo or ret.get("HTML_KIND") == "NAVIGATION":
        return "MENU", "a entrada e navegacao/menu (%s)" % (rep.get("MOTIVO") or ret.get("HTML_KIND"))
    if rep.get("FAMILIAS_VISTAS") or ret.get("HTML_KIND") in ("LISTING", "ARTICLE_LIST"):
        return "LISTA_NOTICIA", "lista de itens (%s familias vistas, HTML_KIND %s)" % (
            len(rep.get("FAMILIAS_VISTAS") or []), ret.get("HTML_KIND"))
    if "SEM_FAMILIA_DE_ITENS" in motivo:
        return "MENU", "sem familia de itens repetidos na entrada"
    return "NAO_SEI", "prova insuficiente: %s" % motivo.strip()[:80]


def _bytes(rep):
    return sum(p.get("BYTES") or 0 for p in (rep.get("PAGINAS_LIDAS") or [])[:1]) or None


def levantar() -> dict:
    corr = _j(RAIZ.parent / "fila-unica-v1" / "curadoria" / "FILA-UNICA-CORRESPONDENCIA-V1.json")
    jan = {x["CAND_NOVO"]: x for x in corr["CORRESPONDENCIA"]
           if x["RESULTADO"].startswith("NOVA") and x["FAMILIA"].startswith(JANELA)}
    aloc = {x["CANDIDATE_ID"]: x["SOURCE_ID"] for x in _j(VIVO / "SOURCE-ID-ALLOCATION-V1.json")["NOVAS"]
            if x.get("SOURCE_ID")}
    ult = {}
    for t in _j(VIVO / "LIFECYCLE-LEDGER-V1.json")["TRANSICOES"]:
        ult[t["SOURCE_ID"]] = t
    contratos = {c["SOURCE_ID"]: c for c in _j(VIVO / "italy_contracts_curator.json")["FONTES"]}
    provas: dict = {}
    for p in _j(VIVO / "LIFECYCLE-EVIDENCE-V1.json")["PROVAS"]:
        provas.setdefault(p.get("SOURCE_ID"), {})[p["ETAPA"]] = p.get("DADOS") or {}  # a ultima de cada etapa
    p1g = {}
    try:
        for x in _git_json("origin/janelas-regioes-v1", "curadoria/JANELAS-REGIOES-V1.json")["CELULAS"]:
            p1g[x["URL"].rstrip("/").lower()] = x
    except Exception:
        pass
    linhas = []
    for cand, x in jan.items():
        sid = aloc.get(cand)
        if not sid or ult.get(sid, {}).get("NEW_STATE") != "CONTRACTED_CANARY_FAILED":
            continue
        ct = contratos.get(sid, {})
        acq = ct.get("ACQUISITION") or {}
        pv = provas.get(sid, {})
        c = {"SOURCE_ID": sid, "CAND": cand, "NOME": ct.get("NAME"), "URL": x["URL"], "FAMILIA": x["FAMILIA"],
             "BATCH": ct.get("BATCH_ID"), "STRATEGY": acq.get("STRATEGY"), "LINK_PATTERN": acq.get("LINK_PATTERN"),
             "RAZAO_DO_ESTADO": ult[sid].get("REASON"), "CANARY": pv.get("CANARY"), "REPARO": pv.get("REPAIR_CONTRACT"),
             "P1G": p1g.get(x["URL"].rstrip("/").lower())}
        c["FORMA"], c["PORQUE_DA_FORMA"] = forma(c)
        linhas.append(c)
    out = {"DATASET": "JANELAS-68-FORMAS-V1", "N": len(linhas),
           "POR_FORMA": dict(Counter(l["FORMA"] for l in linhas).most_common()), "FONTES": linhas}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    r = levantar()
    print("N", r["N"], "POR_FORMA", r["POR_FORMA"])
    for l in sorted(r["FONTES"], key=lambda l: l["FORMA"]):
        print("%-14s %-11s %-45s %s" % (l["FORMA"], l["SOURCE_ID"], (l["NOME"] or "")[:45], l["PORQUE_DA_FORMA"][:90]))
