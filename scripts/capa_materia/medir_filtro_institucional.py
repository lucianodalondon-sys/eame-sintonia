#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CAPA-MATERIA · quantos enderecos JA coletados a regra nova (pagina institucional no ULTIMO
troco) teria recusado. Sem rede; so le o livro de coletas da producao (nao escreve).

    py scripts/capa_materia/medir_filtro_institucional.py [--livro=CAMINHO]

A expressao e a MESMA de regras/motor_de_rota.mjs (PAGINA_INSTITUCIONAL), lida de la.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
LIVRO = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--livro=")),
             "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/data/collection-ledger/italy/observations.ndjson")


def main():
    src = (RAIZ / "regras" / "motor_de_rota.mjs").read_text(encoding="utf-8")
    m = re.search(r"const PAGINA_INSTITUCIONAL = /(.+)/i;", src)
    nav = re.compile(m.group(1), re.I)
    urls = {}
    for linha in open(LIVRO, encoding="utf-8"):
        try:
            o = json.loads(linha)
        except ValueError:
            continue
        u = o.get("SOURCE_URL") or o.get("URL") or o.get("source_url")
        if u and u.startswith("http"):
            urls[u] = o.get("SOURCE_ID")
    recusados = []
    for u, s in urls.items():
        seg = [x for x in re.sub(r"[?#].*", "", u).rstrip("/").split("/")[3:] if x]
        if seg and nav.search(seg[-1]):
            recusados.append({"SOURCE_ID": s, "URL": u})
    out = {"DATASET": "MEDICAO-FILTRO-INSTITUCIONAL-V1", "LIVRO": LIVRO, "ENDERECOS_NO_LIVRO": len(urls),
           "RECUSADOS": recusados, "N_RECUSADOS": len(recusados)}
    (Path(__file__).parent / "MEDICAO-FILTRO-INSTITUCIONAL-V1.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8", newline=chr(10))
    print(out["ENDERECOS_NO_LIVRO"], out["N_RECUSADOS"], recusados)


if __name__ == "__main__":
    main()
