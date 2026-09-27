#!/usr/bin/env python3
"""INTELLIGENCE R3 · RT-INT-02 (menu/sidebar como corpo) · MEDIR antes de consertar o extrator de texto HTML.

O extrator de texto HTML (`coleta/texto_fonte.py::limpar`) tira <script>/<style> e as marcas, mas deixa o texto
da MOLDURA do site (<nav>, <header>, <footer>, <aside>) no texto guardado. Pergunta: se a moldura saisse, o
fact_location / fact_time de `leis/fato_do_texto.py` mudaria? E o texto guardado mudaria em quantas paginas?

So leitura, sem rede: os HTML guardados em data/collection-store (os bytes do coletor).

    py scripts/lugar_fato/medir_moldura_html.py      -> escreve MEDIDA-MOLDURA-HTML-V1.json ao lado
"""
import glob
import hashlib
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "leis"))
import _gavetas  # noqa: E402,F401
from coleta.texto_fonte import limpar  # noqa: E402
import fato_do_texto as FT  # noqa: E402

MOLDURA = re.compile(r"<(nav|header|footer|aside)\b[^>]*>.*?</\1\s*>", re.I | re.S)


def main():
    paginas = sorted(glob.glob(str(RAIZ / "data" / "collection-store" / "**" / "*.html"), recursive=True))
    res = {"DATASET": "MEDIDA-MOLDURA-HTML-V1", "PROPOSTA": "tirar <nav>/<header>/<footer>/<aside> antes de limpar()",
           "APLICADA": False, "PAGINAS": len(paginas), "COM_MOLDURA": 0, "TEXTO_GUARDADO_MUDA": 0,
           "FACT_LOCATION_MUDA": [], "FACT_TIME_MUDA": []}
    for p in paginas:
        b = Path(p).read_bytes()
        fonte = b.decode("utf-8", "replace")
        sem = MOLDURA.sub(" ", fonte).encode("utf-8")
        res["COM_MOLDURA"] += bool(MOLDURA.search(fonte))
        ta, td = limpar(b, "text/html"), limpar(sem, "text/html")
        res["TEXTO_GUARDADO_MUDA"] += ta != td
        a, d = FT.campos_do_fato(ta), FT.campos_do_fato(td)
        rel = str(Path(p).relative_to(RAIZ)).replace("\\", "/")
        for k, chave in (("fact_location", "FACT_LOCATION_MUDA"), ("fact_time", "FACT_TIME_MUDA")):
            if a[k] != d[k]:
                res[chave].append({"PAGINA": rel, "SHA256": hashlib.sha256(b).hexdigest(),
                                   "ANTES": a[k], "SEM_MOLDURA": d[k],
                                   "BASE_ANTES": a[k + "_basis"][:400]})
    out = Path(__file__).with_name("MEDIDA-MOLDURA-HTML-V1.json")
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("paginas %d · com moldura %d · texto guardado muda %d · fact_location muda %d · fact_time muda %d"
          % (res["PAGINAS"], res["COM_MOLDURA"], res["TEXTO_GUARDADO_MUDA"],
             len(res["FACT_LOCATION_MUDA"]), len(res["FACT_TIME_MUDA"])))


if __name__ == "__main__":
    main()
