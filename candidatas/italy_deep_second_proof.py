#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEGUNDA PROVA — o mesmo facto, por outro caminho.

A primeira medicao olhou UMA pagina (a que o grafo mais viu, ou a raiz). Se a
fonte for boa, uma pagina diferente tem de contar a mesma historia: tem de
haver material datado, recente, que ela mesma produziu.

Por isso a segunda prova NAO repete a primeira. Ela vai a uma ROTA PROFUNDA
— o arquivo de boletins, a lista de publicacoes, o feed — e pergunta uma coisa
so, verificavel:

    ha aqui um item com data completa de 2025 ou 2026?

    CONFIRMED  sim, e a data vem de uma data completa (nao de um ano solto)
    DIVERGED   a rota abre, mas o material mais novo e velho — ou nao ha
               material proprio nenhum, ao contrario do que a homepage sugeria
    UNKNOWN    a rota nao abriu, foi bloqueada, ou exige registo

DIVERGED nao vira REJECT: vira "nao fica A/B ate alguem resolver". A regra e
do pedido, e e a regra certa — um endereco que hoje nao mostra data pode ser um
endereco errado, nao uma fonte morta.
"""

import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TRABALHO = Path(sys.argv[1] if len(sys.argv) > 1
                else "C:/Users/London1/AppData/Local/Temp/sintonia-italy-deep")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

RE_TAG = re.compile(r"<[^>]+>")
RE_ISO = re.compile(r"\b(20[12][0-9])-(0[1-9]|1[0-2])-([0-3][0-9])\b")
RE_IT = re.compile(r"\b([0-3]?[0-9])[/.\-](0?[1-9]|1[0-2])[/.\-](20[12][0-9])\b")
RE_MES = re.compile(r"\b([0-3]?[0-9])\s+(gennaio|febbraio|marzo|aprile|maggio|"
                    r"giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)"
                    r"\s+(20[12][0-9])\b", re.I)
MESES = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5,
         "giugno": 6, "luglio": 7, "agosto": 8, "settembre": 9,
         "ottobre": 10, "novembre": 11, "dicembre": 12}

# ── a amostra vive ao lado, em DADO ──────────────────────────────────────
# Escolhida para NAO ser so a nata: entram A e B, fontes novas e fontes ja
# conhecidas, regioes grandes e pequenas, e dois controles negativos declarados
# ANTES de medir (classe CONTROLE_NEGATIVO na propria lista).
#
# Esta fora do codigo pela mesma razao que as sementes: 18 dos 79 enderecos do
# System Map vinham daqui, e empurravam para fora da vista os enderecos que a
# maquina chama de verdade em producao.
AMOSTRA_JSON = Path(__file__).resolve().parent / "italy_deep_second_proof_amostra.json"


def amostra():
    d = json.loads(AMOSTRA_JSON.read_text(encoding="utf-8"))
    return [(h, c, rotas) for h, c, rotas in d["AMOSTRA"]]


def buscar(url, timeout=22):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "text/html,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.9,de;q=0.7,en;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            raw = r.read(500_000)
            enc = "utf-8"
            m = re.search(r"charset=([\w\-]+)", r.headers.get("Content-Type", ""), re.I)
            if m:
                enc = m.group(1)
            try:
                return r.status, raw.decode(enc, errors="replace"), r.geturl()
            except LookupError:
                return r.status, raw.decode("utf-8", errors="replace"), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, "", url
    except Exception as e:
        return None, f"__ERRO__{type(e).__name__}: {str(e)[:90]}", url


def datas_completas(html):
    out = []
    for a, m, d in RE_ISO.findall(html):
        out.append((int(a), int(m), int(d)))
    for d, m, a in RE_IT.findall(html):
        out.append((int(a), int(m), int(d)))
    for d, mes, a in RE_MES.findall(html):
        out.append((int(a), MESES[mes.lower()], int(d)))
    return sorted({x for x in out if 2010 <= x[0] <= 2026}, reverse=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    resultado = {}
    AMOSTRA = amostra()

    def trabalha(item):
        host, classe, rotas = item
        tentadas = []
        for u in rotas:
            st, html, final = buscar(u)
            tentadas.append({"url": u, "status": st,
                             "erro": html[9:] if html.startswith("__ERRO__") else ""})
            if st == 200 and html and not html.startswith("__ERRO__"):
                ds = datas_completas(html)
                texto = re.sub(r"\s+", " ", RE_TAG.sub(" ", html))
                if not ds:
                    continue
                mais_nova = ds[0]
                if mais_nova[0] >= 2025:
                    return host, {
                        "resultado": "CONFIRMED",
                        "classe_declarada": classe,
                        "rota_independente": final,
                        "prova": (f"data completa mais recente na rota profunda: "
                                  f"{mais_nova[0]:04d}-{mais_nova[1]:02d}-{mais_nova[2]:02d}"
                                  f" · {len(ds)} datas completas distintas na pagina"
                                  f" · {len(texto)} caracteres de texto"),
                        "tentadas": tentadas,
                    }
                return host, {
                    "resultado": "DIVERGED",
                    "classe_declarada": classe,
                    "rota_independente": final,
                    "prova": (f"a rota abre, mas a data completa mais recente e "
                              f"{mais_nova[0]:04d}-{mais_nova[1]:02d}-{mais_nova[2]:02d}"
                              f" — anterior a 2025. Nao fica A/B ate alguem resolver."),
                    "tentadas": tentadas,
                }
        return host, {
            "resultado": "UNKNOWN",
            "classe_declarada": classe,
            "rota_independente": rotas[0],
            "prova": ("nenhuma rota profunda devolveu pagina com data completa "
                      "legivel. UNKNOWN nao e REJECT."),
            "tentadas": tentadas,
        }

    with ThreadPoolExecutor(max_workers=8) as ex:
        for host, r in ex.map(trabalha, AMOSTRA):
            resultado[host] = r

    (TRABALHO / "SECOND-PROOF.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    from collections import Counter
    c = Counter(v["resultado"] for v in resultado.values())
    print(f"SEGUNDA PROVA: {len(resultado)} fontes por caminho independente")
    print("  " + " · ".join(f"{k}={v}" for k, v in c.items()))
    print()
    for h, v in sorted(resultado.items(), key=lambda kv: kv[1]["resultado"]):
        print(f"  {v['resultado']:10s} {v['classe_declarada']:18s} {h[:44]}")
        print(f"             {v['prova'][:140]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
