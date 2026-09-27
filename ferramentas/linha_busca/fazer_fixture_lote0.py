# -*- coding: utf-8 -*-
"""LINHA-BUSCA · a fixture do ensaio a partir do BUSCA-LOTE-0 (3 buscas do coordenador, 27/09 08:20). SEM REDE.

    py ferramentas/linha_busca/fazer_fixture_lote0.py --lote=<auditoria-madrugada/BUSCA-LOTE-0.md>

⚠️ O que ha e o que NAO ha:
  · ha: as 13 URLs e o resumo de cada uma, escrito pelo coordenador a partir do resumo da busca;
  · NAO ha: os bytes das paginas (nenhuma das 13 esta no armazem: conferido na Sala, 27/09), nem a posicao real
    de cada resultado, nem a consulta exata de cada URL.
Por isso as paginas desta fixture sao SINTETICAS: um HTML minimo cujo texto e o RESUMO (nao a pagina). A
consulta de cada URL e atribuida pelo assunto (vite / cimice / mosca) e a POSICAO e a ordem na tabela. O que
o ensaio mede com isto: o portao D93, a candidata pela porta e as perguntas da Admission que o resumo permite
responder. A pergunta «materia ou capa» precisa da pagina real: no ensaio ela julga o HTML sintetico.
"""
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent / "fixtures" / "busca-lote-0"
CONSULTAS = {"vite": "bollettino fitosanitario settembre 2026 vite peronospora",
             "cimice": "cimice asiatica catture trappole settembre 2026",
             "mosca": "mosca dell'olivo infestazione settembre 2026 bollettino"}


def assunto(url: str, resumo: str) -> str:
    t = (url + " " + resumo).lower()
    if "cimice" in t:
        return "cimice"
    if "mosca" in t and "vite" not in url.lower():
        return "mosca"
    return "vite"


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    md = Path(arg["lote"]).read_text(encoding="utf-8")
    linhas = re.findall(r"^\| (https?://\S+) \| (.+?) \|$", md, re.M)
    AQUI.mkdir(parents=True, exist_ok=True)
    resultados, paginas, pos = [], {}, {}
    for i, (url, resumo) in enumerate(linhas, 1):
        a = assunto(url, resumo)
        pos[a] = pos.get(a, 0) + 1
        resultados.append({"CONSULTA_ID": "LOTE0-%s" % a, "CONSULTA": CONSULTAS[a], "UNIVERSO": "T3",
                           "FERRAMENTA": "Finestre Colturali", "MOTOR": "IMPORTADO:HERMES_WEB_SEARCH",
                           "ROTA_DO_MOTOR": "motor de busca web do Hermes (coordenador), resultados importados",
                           "POSICAO": pos[a], "POSICAO_BASE": "ordem na tabela do BUSCA-LOTE-0 (a real nao foi guardada)",
                           "INSTANTE": "2026-09-27T08:20:00+00:00", "URL": url})
        nome = "p%02d.html" % i
        html = ("<!doctype html><html lang=\"it\"><head><meta charset=\"utf-8\"><title>%s</title></head><body>"
                "<!-- SINTETICA: o texto e o RESUMO do BUSCA-LOTE-0, nao a pagina -->"
                "<article><h1>%s</h1><p>%s</p></article></body></html>" % (url, url, resumo))
        (AQUI / nome).write_text(html, encoding="utf-8", newline="\n")
        paginas[url] = {"FICHEIRO": nome, "CONTENT_TYPE": "text/html", "SINTETICA": True}
    (AQUI / "RESULTADOS.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (AQUI / "PAGINAS.json").write_text(json.dumps(paginas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(len(resultados), "resultados;", {a: n for a, n in pos.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
