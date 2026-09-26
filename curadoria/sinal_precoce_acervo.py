#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SINAL PRECOCE NO ACERVO — le TODOS os PDFs ja colhidos de um territorio (T3 por omissao) com o leitor de
monitorizacao, SEM REDE e SEM RESUMIR. (SINAL-PRECOCE-PDF, 26/09.)

    py curadoria/sinal_precoce_acervo.py --raiz=<pasta> [--raiz=<outra>] --textos=<fora do Git> --saida=<JSON> [--prefixo=IT-T3-]

- procura *.pdf (so ficheiros) nas raizes; o SOURCE_ID sai do caminho (…/IT-T3-002/…); o mesmo PDF guardado em varias
  copias conta UMA vez (por sha256) e diz quantas copias ha;
- texto integral (`pdftotext -layout`) para <textos>/<SOURCE_ID>/<sha256[:12]>-<nome>.txt, com sha256 do texto;
- no JSON: TODAS as linhas com sinal (`LINHA` tal como saiu), por PDF, e as contas por tipo. Nada e cortado.
Lembrete medido: onde o PDF tem duas camadas de texto sobrepostas (anexo do disciplinare da APOL), o `-layout` devolve
letras misturadas — essas linhas vao tal como sairam, e nao se leem como valor.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import ler_pdf_monitorizacao as L   # noqa: E402

RE_SID = re.compile(r"(IT-T\d+-\d{3})")


def inventario(raizes: list[Path], prefixo: str) -> list[dict]:
    por_sha: dict[str, dict] = {}
    for r in raizes:
        for dp, _dn, fns in os.walk(r):
            for fn in fns:
                if not fn.lower().endswith(".pdf"):
                    continue
                f = Path(dp) / fn
                m = RE_SID.search(str(f).replace("\\", "/"))
                if not m or not m.group(1).startswith(prefixo):
                    continue
                h = hashlib.sha256(f.read_bytes()).hexdigest()
                e = por_sha.setdefault(h, {"SHA256": h, "SOURCE_ID": m.group(1), "CAMINHOS": []})
                e["CAMINHOS"].append(str(f).replace("\\", "/"))
    return sorted(por_sha.values(), key=lambda e: (e["SOURCE_ID"], Path(e["CAMINHOS"][0]).name))


def ler_todos(pdfs: list[dict], textos: Path, extrair=L.texto_do_pdf) -> list[dict]:
    out = []
    for e in pdfs:
        p = Path(e["CAMINHOS"][0])
        base = {"SOURCE_ID": e["SOURCE_ID"], "FICHEIRO": p.name, "SHA256": e["SHA256"], "CAMINHO": e["CAMINHOS"][0],
                "COPIAS": len(e["CAMINHOS"])}
        try:
            t = extrair(p)
        except Exception as ex:  # noqa: BLE001
            out.append({**base, "ESTADO": "SEM_TEXTO", "PORQUE": str(ex)[:200]})
            continue
        dest = textos / e["SOURCE_ID"] / ("%s-%s.txt" % (e["SHA256"][:12], p.stem))
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(t, encoding="utf-8")
        ls = L.linhas_com_sinal(t)
        out.append({**base, "ESTADO": "LIDO" if t.strip() else "PDF_SEM_TEXTO",
                    "TEXTO_INTEGRAL_EM": str(dest).replace("\\", "/"),
                    "TEXTO_SHA256": hashlib.sha256(t.encode("utf-8")).hexdigest(),
                    "LINHAS_DO_TEXTO": len(t.splitlines()),
                    "POR_TIPO": {k: sum(1 for x in ls if k in x["TIPOS"]) for k in ("CONTAGEM", "PERCENTAGEM", "LIMIAR", "VOO", "TABELA")},
                    "LINHAS_COM_SINAL": ls})
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    raizes = [Path(x.split("=", 1)[1]) for x in argv if x.startswith("--raiz=")]
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x and not x.startswith("--raiz="))
    if not raizes or not a.get("textos") or not a.get("saida"):
        print(__doc__)
        return 2
    pdfs = inventario(raizes, a.get("prefixo", "IT-T3-"))
    res = ler_todos(pdfs, Path(a["textos"]))
    out = {"DATASET": "SINAL-PRECOCE-PDF-ACERVO", "RAIZES": [str(r) for r in raizes], "PREFIXO": a.get("prefixo", "IT-T3-"),
           "PDFS_DISTINTOS": len(res), "COPIAS": sum(r["COPIAS"] for r in res), "PDFS": res}
    Path(a["saida"]).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"PDFS_DISTINTOS": len(res), "COPIAS": out["COPIAS"],
                      "POR_FONTE": {s: sum(1 for r in res if r["SOURCE_ID"] == s) for s in sorted({r["SOURCE_ID"] for r in res})}},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
