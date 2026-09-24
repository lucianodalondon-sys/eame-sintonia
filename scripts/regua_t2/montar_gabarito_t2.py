#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T2-REGUA · MONTA O GABARITO T2 A PARTIR DO INVENTARIO E DOS ROTULOS — SEM REDE.

    py scripts/regua_t2/montar_gabarito_t2.py [--dir=DIR]

Entrada (fora do Git, em DIR = %USERPROFILE%\\sintonia-gabarito\\REGUA-T2-V1):
    INVENTARIO.json   o que `inventariar_t2.py` juntou
    A-ROTULAR.json    a ordem dos textos lidos a mao
    rotulos.tsv       N \\t UNIVERSE_MATCH \\t SINTONIA_RELEVANT \\t CONTEUDO \\t PORQUE \\t TRECHO
                      (uma linha repetida mais abaixo substitui a de cima)
    rotulos-janela.tsv TEXTO_ID 	 JANELA 	 ACTION 	 PORQUE  (ADENDA 1, D29)
Saida (no Git): scripts/regua_t2/GABARITO-T2-V1.json (eixo UNIVERSE_MATCH, clima)
                scripts/regua_t2/GABARITO-T2-V2.json (eixo JANELA, o que a regua mede)

JANELA (ADENDA 1): o que foi re-lido esta em rotulos-janela.tsv; o resto herda do
eixo antigo so quando a resposta nao pode mudar — um NO de menu, administracao ou
ambiente continua NO (nao sustenta janela nenhuma), e um NAO_SEI continua NAO_SEI.
Todo o YES antigo e todo o texto com conteudo T3 foi re-lido, sem heranca.

Os rotulos antigos (GABARITO-T2-T12-V2/V3) nao sao refeitos: YES se o conteudo
foi julgado T2 (inclui os REROUTE:T2), NO se foi julgado de outro universo ou de
nenhum. Os NAO_SEI ficam fora da conta, contados a parte.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CASA = Path(os.environ.get("USERPROFILE", str(Path.home())))


def _arg(nome, omissao):
    return next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--%s=" % nome)), omissao)


def serie(it: dict) -> str | None:
    c = (it.get("CAMINHO") or "").replace("\\", "/").lower()
    if re.search(r"(^|[-/])agro_\d", c.rsplit("/", 1)[-1]):
        return "ARPAV-AGROMETEO-INFORMA"
    if "nheowl0530" in c:
        return "SIAS-PRECIPITAZIONI-GIORNALIERE"
    return None


def main() -> int:
    d = Path(_arg("dir", str(CASA / "sintonia-gabarito" / "REGUA-T2-V1")))
    inv = {i["TEXTO_ID"]: i for i in json.load(open(d / "INVENTARIO.json", encoding="utf-8"))["ITENS"]}
    ordem = json.load(open(d / "A-ROTULAR.json", encoding="utf-8"))
    novos = {}
    for linha in open(d / "rotulos.tsv", encoding="utf-8"):
        if not linha.strip():
            continue
        n, um, sr, cont, porque, trecho = (linha.rstrip("\n").split("\t") + [""] * 6)[:6]
        novos[ordem[int(n)]] = {"UNIVERSE_MATCH": um, "SINTONIA_RELEVANT": sr, "CONTEUDO": cont,
                                "PORQUE": porque, "TRECHO": trecho, "ROTULO_DE": "T2-REGUA-V1 (Claude)"}
    itens = []
    for tid, it in inv.items():
        r = novos.get(tid)
        if r is None and it.get("ROTULO_ANTIGO"):
            a = it["ROTULO_ANTIGO"]
            cont = a.get("UNIVERSO_DO_CONTEUDO")
            um = "YES" if cont == "T2" or a.get("ACTION") == "REROUTE:T2" else "NO"
            r = {"UNIVERSE_MATCH": um, "SINTONIA_RELEVANT": a.get("SINTONIA_RELEVANT"),
                 "CONTEUDO": cont, "PORQUE": a.get("PORQUE"), "TRECHO": None,
                 "ROTULO_DE": a.get("DE")}
        if r is None:
            continue                       # no corpus dos vizinhos, fora do gabarito
        itens.append({"TEXTO_ID": tid, "TEXTO_SHA256": it["TEXTO_SHA256"], "SOURCE_ID": it["SOURCE_ID"],
                      "ORIGEM": it["ORIGEM"], "URL": it.get("URL"),
                      "CAMINHO_FORA_DO_GIT": it["CAMINHO"], "BYTES_SHA256": it["BYTES_SHA256"],
                      "SERIE": serie(it), **r})
    c = Counter(i["UNIVERSE_MATCH"] for i in itens)
    pos = [i for i in itens if i["UNIVERSE_MATCH"] == "YES"]
    out = {"DATASET": "GABARITO-T2-V1", "PROTOCOLO": "scripts/regua_t2/PROTOCOLO-GABARITO-T2.md",
           "VALIDADO_POR_HUMANO": "NAO",
           "CONTAGEM": {"ITENS": len(itens), "YES": c["YES"], "NO": c["NO"], "NAO_SEI": c["NAO_SEI"],
                        "MINIMO": 20, "PRONTO": c["YES"] >= 20 and c["NO"] >= 20,
                        "YES_POR_SERIE": dict(Counter(i["SERIE"] or "(avulso)" for i in pos)),
                        "YES_POR_FONTE": dict(Counter(i["SOURCE_ID"] for i in pos)),
                        "YES_DE_ROTULO_ANTIGO": sum(1 for i in pos if not i["ROTULO_DE"].startswith("T2-REGUA")),
                        "SINTONIA_RELEVANT_NOS_YES": dict(Counter(i["SINTONIA_RELEVANT"] for i in pos))},
           "ITENS": sorted(itens, key=lambda i: (i["UNIVERSE_MATCH"], i["SOURCE_ID"], i["TEXTO_ID"]))}
    if (d / "rotulos-janela.tsv").is_file():
        jan = {}
        for linha in open(d / "rotulos-janela.tsv", encoding="utf-8"):
            if linha.strip():
                tid, j, acc, porque = (linha.rstrip(chr(10)).split(chr(9)) + [""] * 4)[:4]
                jan[tid] = (j, acc or None, porque)
        v2 = []
        for tid, it in inv.items():
            base = next((i for i in itens if i["TEXTO_ID"] == tid), None)
            if tid in jan:
                j, acc, porque = jan[tid]
                de = "T2-REGUA-V1 ADENDA-1 (Claude, re-lido)"
            elif base is not None and base["UNIVERSE_MATCH"] in ("NO", "NAO_SEI"):
                j, acc, porque = base["UNIVERSE_MATCH"], None, base.get("PORQUE")
                de = "herdado de %s" % base["ROTULO_DE"]
            else:
                continue
            v2.append({"TEXTO_ID": tid, "TEXTO_SHA256": it["TEXTO_SHA256"], "SOURCE_ID": it["SOURCE_ID"],
                       "ORIGEM": it["ORIGEM"], "URL": it.get("URL"), "CAMINHO_FORA_DO_GIT": it["CAMINHO"],
                       "BYTES_SHA256": it["BYTES_SHA256"], "SERIE": serie(it), "JANELA": j, "ACTION": acc,
                       "PORQUE": porque, "ROTULO_DE": de,
                       "UNIVERSE_MATCH_V1": base["UNIVERSE_MATCH"] if base else None})
        cj = Counter(i["JANELA"] for i in v2)
        pj = [i for i in v2 if i["JANELA"] == "YES"]
        o2 = {"DATASET": "GABARITO-T2-V2", "EIXO": "JANELA (ADENDA 1, D29)",
              "PROTOCOLO": "scripts/regua_t2/PROTOCOLO-GABARITO-T2.md#adenda-1", "VALIDADO_POR_HUMANO": "NAO",
              "CONTAGEM": {"ITENS": len(v2), "YES": cj["YES"], "NO": cj["NO"], "NAO_SEI": cj["NAO_SEI"],
                           "MINIMO": 20, "PRONTO": cj["YES"] >= 20 and cj["NO"] >= 20,
                           "RE_LIDOS": len(jan), "HERDADOS": len(v2) - len(jan),
                           "REROUTE": sum(1 for i in v2 if i["ACTION"] == "REROUTE"),
                           "YES_POR_SERIE": dict(Counter(i["SERIE"] or "(avulso)" for i in pj)),
                           "YES_POR_FONTE": dict(Counter(i["SOURCE_ID"] for i in pj)),
                           "YES_V1_QUE_SAO_NO_OU_NAO_SEI_EM_V2": sum(1 for i in v2 if i["UNIVERSE_MATCH_V1"] == "YES" and i["JANELA"] != "YES"),
                           "NO_V1_QUE_SAO_YES_EM_V2": sum(1 for i in v2 if i["UNIVERSE_MATCH_V1"] == "NO" and i["JANELA"] == "YES")},
              "ITENS": sorted(v2, key=lambda i: (i["JANELA"], i["SOURCE_ID"], i["TEXTO_ID"]))}
        (AQUI / "GABARITO-T2-V2.json").write_text(json.dumps(o2, ensure_ascii=False, indent=1) + chr(10),
                                                  encoding="utf-8", newline=chr(10))
        print(json.dumps(o2["CONTAGEM"], ensure_ascii=False, indent=1))
    (AQUI / "GABARITO-T2-V1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                              encoding="utf-8", newline="\n")
    print(json.dumps(out["CONTAGEM"], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__" and "--v3" not in sys.argv:
    raise SystemExit(main())


def montar_v3(d=None):
    """ADENDA 2: T2-V2 + os textos da RECOLHA pela rede (1.a/2.a/3.a ida), rotulados no
    eixo JANELA em rotulos-recolha.tsv (TEXTO_SHA256 \t JANELA \t ACTION \t PORQUE).
    Os textos normalizados vao para textos/<sha16>.txt (fora do Git), como os outros."""
    d = Path(d or (CASA / "sintonia-gabarito" / "REGUA-T2-V1"))
    spec = importlib.util.spec_from_file_location("inv", AQUI / "inventariar_t2.py")
    inv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inv)
    v2 = json.load(open(AQUI / "GABARITO-T2-V2.json", encoding="utf-8"))
    rot = {}
    for linha in open(d / "rotulos-recolha.tsv", encoding="utf-8"):
        if linha.strip():
            h, j, acc, porque = (linha.rstrip(chr(10)).split(chr(9)) + [""] * 4)[:4]
            rot[h] = (j, acc or None, porque)
    novos, vistos = [], {i["TEXTO_SHA256"] for i in v2["ITENS"]}
    for ida in ("V1", "V2", "V3"):
        for i in json.load(open(AQUI / ("RECOLHA-BOLETINS-%s.json" % ida), encoding="utf-8"))["ITENS"]:
            h = i["TEXTO_SHA256"]
            if h in vistos or h not in rot:
                continue
            vistos.add(h)
            corpo = Path(i["FICHEIRO_FORA_DO_GIT"]).read_bytes()
            norm = inv.normalizar(inv.extrair(corpo)[0])
            assert hashlib.sha256(norm.encode("utf-8")).hexdigest() == h, i["URL"]
            (d / "textos" / (h[:16] + ".txt")).write_bytes(norm.encode("utf-8"))
            j, acc, porque = rot[h]
            novos.append({"TEXTO_ID": h[:16], "TEXTO_SHA256": h, "SOURCE_ID": i["SOURCE_ID"],
                          "SERVICO": i["SERVICO"], "ORIGEM": "RECOLHA-REDE-" + ida, "URL": i["URL"],
                          "CAMINHO_FORA_DO_GIT": i["FICHEIRO_FORA_DO_GIT"], "BYTES_SHA256": i["SHA256"],
                          "SERIE": "ARPAV-AGROMETEO-INFORMA" if "/agro_" in i["URL"] else None,
                          "JANELA": j, "ACTION": acc, "PORQUE": porque,
                          "ROTULO_DE": "T2-REGUA ADENDA-2 (Claude)", "FORA_DA_AMOSTRA": True})
    itens = v2["ITENS"] + novos
    c = Counter(i["JANELA"] for i in itens)
    cn = Counter(i["JANELA"] for i in novos)
    out = {"DATASET": "GABARITO-T2-V3", "EIXO": "JANELA (ADENDA 1, D29)",
           "PROTOCOLO": "scripts/regua_t2/PROTOCOLO-GABARITO-T2.md#adenda-2", "VALIDADO_POR_HUMANO": "NAO",
           "CONTAGEM": {"ITENS": len(itens), "YES": c["YES"], "NO": c["NO"], "NAO_SEI": c["NAO_SEI"],
                        "NOVOS_DA_REDE": {"ITENS": len(novos), "YES": cn["YES"], "NO": cn["NO"],
                                          "NAO_SEI": cn["NAO_SEI"],
                                          "YES_POR_SERVICO": dict(Counter(i["SERVICO"] for i in novos
                                                                          if i["JANELA"] == "YES"))},
                        "MINIMO": 20, "PRONTO": c["YES"] >= 20 and c["NO"] >= 20},
           "ITENS": itens}
    (AQUI / "GABARITO-T2-V3.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + chr(10),
                                              encoding="utf-8", newline=chr(10))
    print(json.dumps(out["CONTAGEM"], ensure_ascii=False, indent=1))


if __name__ == "__main__" and "--v3" in sys.argv:
    montar_v3()
