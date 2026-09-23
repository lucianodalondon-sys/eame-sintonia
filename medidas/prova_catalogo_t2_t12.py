#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA DO CATALOGO T2/T12 — a pagina de ENTRADA de cada fonte, guardada com sha256.

    NUNCA PROPOR SEM PROVA. DUVIDA = UNKNOWN.

O catalogo (curadoria/italy_contracts_curator.json @ origin/lote-76-v1) guarda
de cada fonte so o NOME e o ENDERECO de entrada — nenhuma pagina. Para propor
MANTER / MUDAR / RETIRAR e preciso ter lido a pagina. Este instrumento busca a
pagina de ENTRADA das fontes que ainda nao tem prova guardada (gabarito
V2/V3 ou canario da 3b), e mais nada.

A REGRA, fixada antes de qualquer pedido:
  * fora: youtube.com (429 medido; canais ficam UNKNOWN pela prova);
  * por anfitriao: robots (1) + ate 2 paginas de entrada = 3 pedidos;
  * quais 2: primeiro as que tem sinal de assunto no nome/endereco
    (agric, rural, psr, pac, agro, masaf, arsac, assam, ersa, confagri, cia,
    aiab, biolog, acqu, suol, meteo, clima, irrig), depois por numero de
    SOURCE_ID crescente — nunca pelo texto da pagina;
  * egresso medido antes de cada anfitriao; se nao for IT, PARA.

Bytes fora do Git (~/sintonia-gabarito/CATALOGO-PROVA-V1); registo em
curadoria/CATALOGO-PROVA-V1.json. Nada toca o catalogo, a porta ou a Sala.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "medidas"))
import gabarito_t2_t12 as G2   # noqa: E402  (egresso, texto_de, CAN, GATE)

CAN, GATE = G2.CAN, G2.GATE
LIVRO_REF = "origin/lote-76-v1"
PASTA = Path.home() / "sintonia-gabarito" / "CATALOGO-PROVA-V1"
SAIDA = RAIZ / "curadoria" / "CATALOGO-PROVA-V1.json"
PAUSA_S = 1.0
POR_ANFITRIAO = 2
SINAL = re.compile(r"agric|rural|psr|\bpac\b|agro|masaf|politicheagricole|arsac|assam|ersa|"
                   r"confagri|\bcia\b|aiab|biolog|acqu|suol|meteo|clima|irrig", re.I)


def _host(u: str) -> str:
    return (urlparse(u).hostname or "").replace("www.", "")


def fontes() -> list[dict]:
    r = subprocess.run(["git", "show", "%s:curadoria/italy_contracts_curator.json" % LIVRO_REF],
                       capture_output=True, cwd=RAIZ)
    return [x for x in json.loads(r.stdout)["FONTES"]
            if x["SOURCE_ID"].startswith(("IT-T2-", "IT-T12-"))]


def com_prova() -> set:
    ev = set()
    for v in ("V2", "V3"):
        for i in json.loads((RAIZ / "curadoria" / ("GABARITO-T2-T12-%s.json" % v))
                            .read_text(encoding="utf-8"))["ITENS"]:
            ev.add(i["SOURCE_ID"])
    for l in json.loads((RAIZ / "curadoria" / "RELEVANCIA-ELEGIVEIS-V1.json")
                        .read_text(encoding="utf-8"))["FONTES"]:
        ev.add(l["SOURCE_ID"])
    return ev


def plano() -> dict:
    ev = com_prova()
    por = defaultdict(list)
    for x in fontes():
        h = _host(x["CANONICAL_ENTRY_URL"])
        if x["SOURCE_ID"] in ev or "youtube" in h:
            continue
        por[h].append(x)
    for h in por:
        por[h].sort(key=lambda x: (0 if SINAL.search(x["NAME"] + " " + x["CANONICAL_ENTRY_URL"]) else 1,
                                   int(x["SOURCE_ID"].split("-")[2])))
        por[h] = por[h][:POR_ANFITRIAO]
    return por


def main() -> int:
    PASTA.mkdir(parents=True, exist_ok=True)
    sites, paginas = [], []
    for h, lista in plano().items():
        eg = G2.egresso()
        reg = {"ANFITRIAO": h, "EGRESSO": eg, "PEDIDOS": 0}
        sites.append(reg)
        if eg.get("COUNTRY") != "IT":
            reg["PARADO"] = "EGRESSO_NAO_IT"
            print("PARAGEM: egresso %s" % eg, flush=True)
            break
        rp, txt = GATE.robots_de(urlparse(lista[0]["CANONICAL_ENTRY_URL"]).hostname)
        reg["PEDIDOS"] += 1
        if "inacessivel" in txt:
            reg["PARADO"] = "robots: " + txt[:100]
            continue
        for x in lista:
            u = x["CANONICAL_ENTRY_URL"]
            p = {"SOURCE_ID": x["SOURCE_ID"], "NAME": x["NAME"], "URL": u, "ANFITRIAO": h,
                 "EGRESSO": eg}
            paginas.append(p)
            if not GATE.permitido(u, rp):
                p["PARADO"] = "robots proibe"
                continue
            time.sleep(PAUSA_S)
            st, b, err = CAN.buscar(u)
            reg["PEDIDOS"] += 1
            p.update(HTTP=st, BYTES=len(b))
            if st != 200 or not b:
                p["PARADO"] = "HTTP %s %s" % (st, err)
                continue
            sha = hashlib.sha256(b).hexdigest()
            ext = ".pdf" if b[:5] == b"%PDF-" else ".html"
            (PASTA / (sha[:16] + ext)).write_bytes(b)
            texto, estado = G2.texto_de(b, u)
            t = re.search(rb"(?is)<title>(.*?)</title>", b)
            p.update(SHA256=sha, FICHEIRO_FORA_DO_GIT=str(PASTA / (sha[:16] + ext)),
                     EXTRACAO=estado, TITLE=(t.group(1).decode("utf-8", "replace").strip()[:200] if t else ""),
                     NON_WHITESPACE_CHARACTERS=len("".join(texto.split())),
                     OBTIDO_EM=datetime.now(timezone.utc).isoformat())
            print("%-11s %s %s" % (x["SOURCE_ID"], st, u[:90]), flush=True)
        time.sleep(PAUSA_S)
    d = {"DATASET": "CATALOGO-PROVA-V1", "LIVRO": LIVRO_REF + ":curadoria/italy_contracts_curator.json",
         "REGRA": "docstring de medidas/prova_catalogo_t2_t12.py, commitada antes da corrida",
         "BYTES_EM": str(PASTA), "SITES": sites, "PAGINAS": paginas}
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
