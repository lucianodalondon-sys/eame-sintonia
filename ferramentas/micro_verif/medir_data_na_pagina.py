#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MICRO-VERIFICACAO · categoria D: que fontes da coorte publicam a data NA PAGINA (sem rede).

    py ferramentas/micro_verif/medir_data_na_pagina.py <collection-store/italy do vivo> <coorte.json> <saida.json>

So leitura do armazem. Por fonte da coorte, conta as materias guardadas (HTML, a versao mais recente de
cada item) que trazem uma destas marcas: JSON-LD "datePublished", <meta property="article:published_time">,
<time datetime="...">. PDF e outros formatos contam como «sem marca HTML» (a data deles vem de outro leitor).
"""
import json
import re
import sys
from pathlib import Path

MARCAS = {
    "JSONLD_DATEPUBLISHED": re.compile(rb'"datePublished"\s*:\s*"\d{4}-\d{2}-\d{2}'),
    "META_ARTICLE_PUBLISHED_TIME": re.compile(rb'article:published_time["\']\s+content=["\']\d{4}-\d{2}-\d{2}|'
                                              rb'content=["\']\d{4}-\d{2}-\d{2}[^"\']*["\']\s+property=["\']article:published_time'),
    "TIME_DATETIME": re.compile(rb'<time[^>]+datetime=["\']\d{4}-\d{2}-\d{2}'),
}


def main():
    loja, coorte_f, saida = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    coorte = json.loads(coorte_f.read_text(encoding="utf-8"))["COORTE"]
    out = []
    for f in coorte:
        sid = f["SOURCE_ID"]
        pasta = loja / sid
        itens = [d for d in pasta.iterdir() if d.is_dir()] if pasta.is_dir() else []
        conta = {k: 0 for k in MARCAS}
        html, alguma = 0, 0
        for it in itens:
            versoes = sorted(v for v in it.iterdir() if v.is_dir())
            if not versoes:
                continue
            fich = [p for p in versoes[-1].iterdir() if p.is_file()]
            b = fich[0].read_bytes() if fich else b""
            if b.lstrip()[:1] != b"<":
                continue
            html += 1
            achou = False
            for k, rx in MARCAS.items():
                if rx.search(b):
                    conta[k] += 1
                    achou = True
            alguma += achou
        out.append({"SOURCE_ID": sid, "UNIVERSO": f.get("UNIVERSO"), "INDEX_URL": f.get("INDEX_URL"),
                    "ITENS_GUARDADOS": len(itens), "HTML": html, "COM_ALGUMA_MARCA": alguma,
                    "FRACAO": round(alguma / html, 2) if html else None, "POR_MARCA": conta})
    saida.write_text(json.dumps({"DATASET": "DATA-NA-PAGINA-COORTE-V1", "LOJA": str(loja), "FONTES": out},
                                ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for x in out:
        print(x["SOURCE_ID"], x["ITENS_GUARDADOS"], x["HTML"], x["COM_ALGUMA_MARCA"], x["FRACAO"], x["POR_MARCA"])


if __name__ == "__main__":
    main()
