#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PROVA REVERSA DO POTE, PARA O LAB — D156 (criterio do Casco owner, item F).

    python3 portoes/prova_reversa_do_pote.py --url <preview> [--pasta <PARA-O-CASCO>] [--armazem <raiz>] [--saida <pasta>]

Um comando que o LAB corre sozinho quando chegar o pote LIVE, e que tambem prova o vazio legitimo (Radar LIVE = 0):

    SHA DA PASTA    SHA256SUMS + MANIFESTO conferidos (portoes/publicar_preview_da_pasta.py:conferir_pasta)
      -> SHA NO AR  <url>/sintonia-pote-publicado.js -> POTE_SHA256 = sha canonico do pote da pasta
      -> DOM        <url>/portale#debug-intelligence-pot, num navegador: os [data-pote-objeto] = os objetos do pote,
                    na ordem do pote; nenhum a mais, nenhum a menos
      -> PROVA      cada PROVA de cada objeto: TRECHO_DA_AFIRMACAO, RAW_SHA256, RAW_STORAGE_PATH, URL
      -> BYTE       <armazem>/<RAW_STORAGE_PATH> lido de novo: sha256 = RAW_SHA256
      -> FONTE      a URL da fonte (listada; nao se visita sem --rede)

Nao escreve nada fora de --saida. Nao decide nada: mede e diz PASS / FAIL / NAO SEI por passo. Pote sintetico
(CORRIDA_SINTETICA = true) nao tem RAW no armazem: o passo BYTE diz NAO SEI com esse porque, nunca PASS.
Saida 0 = nenhum FAIL; 1 = algum FAIL; 4 = uso errado.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = Path(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

import publicar_preview_da_pasta as G  # noqa: E402
import publicar_portal_sozinho as P  # noqa: E402

DOZE = ["meeting", "future", "windows", "market", "voices", "competitors", "science", "portfolio", "archive",
        "sources", "field", "casa"]
TELA_DEBUG = "debug-intelligence-pot"


def objetos_do_pote(pote: dict) -> list:
    """Os objetos na ordem em que o debug os desenha: compartimentos na ordem do contrato, objetos na do pote."""
    C = pote.get("COMPARTIMENTOS") or {}
    return [(k, o) for k in DOZE if k in C for o in (C[k].get("OBJETOS") or [])]


def ids_no_dom(url: str, saida: Path) -> tuple:
    """-> (ids, erro). Abre o debug num navegador (o fotografo do publicador) e le os data-pote-objeto."""
    r = subprocess.run(["node", str(RAIZ / "portoes" / "fotografar_portal.mjs"), "--base", url, "--saida", str(saida),
                        "--telas", TELA_DEBUG], cwd=str(RAIZ), capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=600)
    f = saida / "CONTAGENS.json"
    if not f.exists():
        return None, (r.stdout + r.stderr)[-400:]
    t = (json.loads(f.read_text(encoding="utf-8")).get("TELAS") or {}).get(TELA_DEBUG) or {}
    if t.get("HTTP") != 200:
        return None, f"HTTP {t.get('HTTP')} em {TELA_DEBUG}"
    return t.get("POTE_IDS") or [], None


def byte_no_armazem(armazem, caminho, esperado) -> tuple:
    if not armazem:
        return "NAO SEI", "sem --armazem (nem SINTONIA_ARMAZEM_RAIZ)"
    alvo = Path(armazem) / str(caminho or "")
    if not caminho or not alvo.is_file():
        return "FAIL", f"{alvo}: ausente"
    got = hashlib.sha256(alvo.read_bytes()).hexdigest()
    return ("PASS", got) if got == esperado else ("FAIL", f"sha {got} != {esperado}")


def provar(pasta: Path, url: str, armazem, saida: Path, rede: bool = False, dom=ids_no_dom, no_ar=P.sha_no_ar) -> dict:
    passos = []

    def passo(nome, estado, detalhe):
        passos.append({"PASSO": nome, "ESTADO": estado, "DETALHE": detalhe})

    c = G.conferir_pasta(pasta)
    if not c["COMPLETA"]:
        passo("SHA_DA_PASTA", "FAIL", c["MOTIVOS"])
        return {"PASSOS": passos, "VEREDITO": "FAIL"}
    pote = json.loads(Path(c["POTE"]).read_text(encoding="utf-8"))
    sha = P.sha_do_pote(pote)
    passo("SHA_DA_PASTA", "PASS", {"PASTA": str(pasta), "SHA256_FICHEIRO": c["SHA256_POTE"], "SHA256_CANONICO": sha,
                                   "INTELLIGENCE_RUN_ID": c["INTELLIGENCE_RUN_ID"],
                                   "CORRIDA_SINTETICA": pote.get("CORRIDA_SINTETICA")})
    st, s_ar = no_ar(url)
    passo("SHA_NO_AR", "PASS" if s_ar == sha else "FAIL", {"URL": url.rstrip("/") + "/sintonia-pote-publicado.js",
                                                          "HTTP": st, "POTE_SHA256": s_ar})
    objs = objetos_do_pote(pote)
    esperados = [o.get("OBJETO_ID") for _, o in objs]
    ids, erro = dom(url, saida / "DOM")
    passo("DOM", "FAIL" if erro or ids != esperados else "PASS",
          {"ESPERADOS": esperados, "NO_DOM": ids, "ERRO": erro} if (erro or ids != esperados) else
          {"OBJETOS": len(ids), "IDS": ids})
    if not objs:
        vazios = {k: (e.get("ESTADO"), e.get("PORQUE_VAZIO")) for k, e in (pote.get("COMPARTIMENTOS") or {}).items()}
        ok = all(est == "VAZIO" and pq for est, pq in vazios.values())
        passo("VAZIO_LEGITIMO", "PASS" if ok else "FAIL", vazios)
    for comp, o in objs:
        for i, pr in enumerate(o.get("PROVA") or []):
            ident = f"{comp}/{o.get('OBJETO_ID')}#{i}"
            faltam = [k for k in ("TRECHO_DA_AFIRMACAO", "RAW_SHA256", "RAW_STORAGE_PATH", "URL") if not pr.get(k)]
            passo(f"PROVA {ident}", "FAIL" if faltam else "PASS",
                  {"FALTAM": faltam} if faltam else {"TRECHO": pr["TRECHO_DA_AFIRMACAO"][:160], "RAW_SHA256": pr["RAW_SHA256"],
                                                     "RAW_STORAGE_PATH": pr["RAW_STORAGE_PATH"], "ITEM_ID": pr.get("ITEM_ID")})
            if pote.get("CORRIDA_SINTETICA") is True:
                passo(f"BYTE {ident}", "NAO SEI", "pote sintetico (CORRIDA_SINTETICA = true): nao ha RAW no armazem")
            else:
                est, det = byte_no_armazem(armazem, pr.get("RAW_STORAGE_PATH"), pr.get("RAW_SHA256"))
                passo(f"BYTE {ident}", est, det)
            fonte = {"URL": pr.get("URL"), "PUBLISHED_AT": pr.get("PUBLISHED_AT"), "FACT_TIME": pr.get("FACT_TIME")}
            if rede and str(pr.get("URL") or "").startswith("http"):
                try:
                    with urllib.request.urlopen(urllib.request.Request(pr["URL"], method="HEAD"), timeout=30) as r:
                        fonte["HTTP"] = r.status
                except Exception as e:  # noqa: BLE001 — falha de ligacao nao e fonte morta: diz-se
                    fonte["HTTP"] = f"NAO SEI ({type(e).__name__})"
            passo(f"FONTE {ident}", "PASS" if fonte["URL"] else "FAIL", fonte)
    veredito = "FAIL" if any(p["ESTADO"] == "FAIL" for p in passos) else "PASS"
    return {"PASSOS": passos, "VEREDITO": veredito, "URL": url, "OBJETOS": len(objs)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Prova reversa do pote no preview (D156, item F).")
    ap.add_argument("--url", required=True, help="o endereco do preview (deployment)")
    ap.add_argument("--pasta", default=str(G.ENTREGA))
    ap.add_argument("--armazem", default=os.environ.get("SINTONIA_ARMAZEM_RAIZ"))
    ap.add_argument("--saida", default=None)
    ap.add_argument("--rede", action="store_true", help="visita a URL da fonte (HEAD)")
    a = ap.parse_args(argv)
    if not a.url.startswith("http"):
        print("--url tem de ser http(s)")
        return 4
    saida = Path(a.saida or tempfile.mkdtemp(prefix="prova-reversa-"))
    saida.mkdir(parents=True, exist_ok=True)
    r = provar(Path(a.pasta), a.url.rstrip("/"), a.armazem, saida, a.rede)
    (saida / "PROVA-REVERSA.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    for p in r["PASSOS"]:
        print(f"  {p['ESTADO']:7} {p['PASSO']}  {json.dumps(p['DETALHE'], ensure_ascii=False)[:200]}")
    print(f"\n  VEREDITO {r['VEREDITO']} · {saida / 'PROVA-REVERSA.json'}")
    return 0 if r["VEREDITO"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
