#!/usr/bin/env python3
"""Baixa e parseia HRAC e IRAC — a camada de modo de acao, com origem rastreavel.

    ./scripts/adama_it_moa.py

Grava MOA-SOURCE-HRAC.json e MOA-SOURCE-IRAC.json no pacote. Sao a evidencia:
sem eles, a classificacao publicada nao teria de onde ser refeita.

FRAC nao entra. O PDF oficial (frac-code-list-2026.pdf) baixa, mas o texto sai com
subconjunto de fonte e perde glifos — 'M 04' vira 'M 0', 'quinone' vira 'uinone'.
Um codigo FRAC extraido assim seria o defeito do extrator publicado como fonte.
"""
import json
import os
import re
import subprocess

OUT = "research/adama-italy-product-intelligence-deep"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
HRAC_URL = "https://www.hracglobal.com/tools/classification-lookup"
IRAC_URL = "https://irac-online.org/mode-of-action/classification-online/"


def _get(url):
    return subprocess.run(["curl", "-sSL", "-m", "120", "-A", UA, "--retry", "4",
                           "--retry-delay", "2", url],
                          check=True, capture_output=True, text=True,
                          errors="replace").stdout


def hrac():
    h = _get(HRAC_URL)
    out = {}
    for b in re.findall(r'<div class="ingredientBlock">.*?(?=<div class="ingredientBlock">|$)', h, re.S):
        ai = re.search(r'<span class="activeIngredient">(.*?)</span>', b, re.S)
        if not ai:
            continue
        hr = re.search(r'class="hrac">\s*<span[^>]*>(.*?)</span>', b, re.S)
        ws = re.search(r'class="wssa"><span[^>]*>(.*?)</span>', b, re.S)
        cf = re.search(r'class="chemicalFamily">\(Chemical Family:\s*(.*?)\)</div>', b, re.S)
        nome = re.sub(r"<[^>]+>", "", ai.group(1)).strip()
        out[nome.upper()] = {
            "HRAC": re.sub(r"\s+", "", hr.group(1)) if hr else None,
            "WSSA": re.sub(r"\s+", "", ws.group(1)) if ws else None,
            "CHEMICAL_FAMILY": re.sub(r"\s+", " ", cf.group(1)).strip() if cf else None,
        }
    return out


def _slug(n):
    s = n.lower()
    for c in "/()[],.":
        s = s.replace(c, " ")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def irac():
    """Cada grupo traz em data-search a lista 'Nome slug Nome slug'. O par so conta
    quando o slug bate com o nome — assim o texto solto do cabecalho nao vira
    ingrediente."""
    h = _get(IRAC_URL)
    out = {}
    for m in re.finditer(r'data-moa-group="([^"]+)"\s+data-search="([^"]*)"', h):
        grp = m.group(1)
        toks = re.sub(r"\s+", " ", m.group(2)).split(" ")
        sub, i = None, 0
        while i < len(toks):
            if re.fullmatch(r"[A-Z]", toks[i]):
                sub = toks[i]
            for n in (4, 3, 2, 1):
                if i + n < len(toks):
                    nome, cand = " ".join(toks[i:i + n]), toks[i + n]
                    if _slug(nome) == cand and len(cand) > 3 and re.match(r"^[A-Za-z]", nome):
                        out.setdefault(nome.upper(), {"IRAC_GROUP": grp, "IRAC_SUBGROUP": sub})
                        i += n
                        break
            i += 1
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for nome, url, dados in (("HRAC", HRAC_URL, hrac()), ("IRAC", IRAC_URL, irac())):
        caminho = os.path.join(OUT, "MOA-SOURCE-%s.json" % nome)
        with open(caminho, "w", encoding="utf-8") as fh:
            json.dump({"SOURCE": nome, "SOURCE_URL": url, "READ_AT": "2026-09-02",
                       "COUNT": len(dados), "INGREDIENTS": dados}, fh,
                      ensure_ascii=False, indent=2)
        print("%s: %d ingredientes -> %s" % (nome, len(dados), caminho))
