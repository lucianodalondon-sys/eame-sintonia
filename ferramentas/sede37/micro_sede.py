#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEDE-37-PREP · 2) MICRO-SEDE: 1 pedido por página de sede, teto D38 (5 por domínio por corrida), VPN IT.

    --so-plano (por omissão)  SEM REDE: quem ainda precisa, que página, pedidos previstos por domínio, rondas.
    --correr                  COM REDE e só com --autorizado=<quem> e o portão de egresso IT = PASS:
                              robots da casa (gate_de_rota) + 1 GET por página (canario.buscar), bytes guardados
                              em --saida com sha256, e a sede lida pela MESMA regra (curadoria/sede_da_fonte).
                              NAO escreve contrato, tabela, livro, Sala nem RAW: só PROPÕE.

Porque não o orquestrador: ele colhe ITENS pelo contrato de cada fonte e produz RAW de coleta; a página de
contactos não é matéria e não deve virar RAW. As peças são as mesmas do canário das rotas elegíveis
(`medidas/canario_rotas_elegiveis.py`): `gate_de_rota.robots_de/permitido` + `canario.buscar`.

Pedidos por domínio registável (o do teto D38): 1 robots por anfitrião + 1 por página distinta. Uma página
partilhada por várias fontes (ex.: crea.gov.it/contatti) pede-se UMA vez. Acima de 5 num domínio, reparte-se
em rondas (uma corrida por ronda, portão antes de cada uma).

    py ferramentas/sede37/micro_sede.py --paginas ferramentas/sede37/PAGINAS-DE-SEDE.json --saida-plano <plano.json>
    py ferramentas/sede37/micro_sede.py --paginas ... --correr --ronda=1 --autorizado=<coordenador> --saida <pasta>
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import subprocess
import sys
import time
from urllib.parse import urlparse

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in (os.path.join(RAIZ, "curadoria"), os.path.join(RAIZ, "provas")):
    if p not in sys.path:
        sys.path.insert(0, p)
import prova_teto_dominio as T  # noqa: E402
import sede_da_fonte as S  # noqa: E402

TETO = 5
PAUSA_S = 2.0


def precisa(l: dict) -> bool:
    """Ainda sem sede provada na própria página, nem pelas páginas já guardadas."""
    return l["SEDE_HOJE"] != "PAGINA_PROPRIA" and l["SEDE_SEM_REDE"]["SOURCE_LOCATION"] == S.NAO_SEI


def plano(paginas: dict) -> dict:
    alvo = [l for l in paginas["FONTES"] if precisa(l)]
    com_url = [l for l in alvo if l.get("CLASSE")]
    sem_url = [l for l in alvo if not l.get("CLASSE")]
    por_dom = collections.defaultdict(lambda: {"FONTES": [], "URLS": collections.OrderedDict(), "HOSTS": set()})
    for l in com_url:
        u = l["PAGINA_DE_SEDE_PROVAVEL"]
        d = por_dom[l["DOMINIO"]]
        # a mesma pagina com e sem «www.» pede-se UMA vez (medido: cia.it/chi-siamo/contatti nas duas formas)
        chave = lambda x: (urlparse(x).hostname or "").removeprefix("www.") + urlparse(x).path.rstrip("/")
        u = next((x for x in d["URLS"] if chave(x) == chave(u)), u)
        d["FONTES"].append(l["SOURCE_ID"])
        d["URLS"].setdefault(u, []).append(l["SOURCE_ID"])
        d["HOSTS"].add(urlparse(u).hostname)
    dominios, rondas = {}, collections.defaultdict(list)
    for dom, d in sorted(por_dom.items()):
        urls = list(d["URLS"])
        hosts = sorted(d["HOSTS"])
        # por ronda: 1 robots por anfitriao + as paginas, nunca acima do teto
        cabe = max(1, TETO - len(hosts))
        partes = [urls[i:i + cabe] for i in range(0, len(urls), cabe)]
        for i, parte in enumerate(partes, 1):
            rondas[i].append({"DOMINIO": dom, "URLS": parte, "PEDIDOS": len({urlparse(u).hostname for u in parte}) + len(parte)})
        dominios[dom] = {"FONTES": d["FONTES"], "PAGINAS_DISTINTAS": len(urls), "ANFITRIOES": hosts,
                         "PEDIDOS_PREVISTOS": len(hosts) * len(partes) + len(urls), "RONDAS": len(partes),
                         "URLS": {u: f for u, f in d["URLS"].items()}}
    return {"DATASET": "MICRO-SEDE-PLANO-V1", "TETO_POR_DOMINIO_POR_CORRIDA": TETO,
            "FONTES_QUE_PRECISAM": len(alvo), "COM_PAGINA_DE_SEDE": len(com_url),
            "SEM_PAGINA_DE_SEDE_NAO_SEI": [l["SOURCE_ID"] for l in sem_url],
            "DOMINIOS": len(dominios), "PAGINAS_DISTINTAS": sum(v["PAGINAS_DISTINTAS"] for v in dominios.values()),
            "PEDIDOS_PREVISTOS_TOTAL": sum(v["PEDIDOS_PREVISTOS"] for v in dominios.values()),
            "MAXIMO_POR_DOMINIO_POR_CORRIDA": max((r["PEDIDOS"] for rr in rondas.values() for r in rr), default=0),
            "RONDAS": {str(k): v for k, v in sorted(rondas.items())},
            "POR_DOMINIO": dominios}


def portao_it() -> bool:
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "superficie", "rede.py"), "--portao-de-egresso", "IT"],
                       cwd=RAIZ, capture_output=True, text=True)
    return '"EGRESS_GATE": "PASS"' in r.stdout


def correr(pl: dict, ronda: int, saida: str, *, buscar=None, robots_de=None, permitido=None, portao=portao_it,
           pausa=PAUSA_S) -> dict:
    """Uma ronda. Conta pedidos por dominio e PARA antes de passar o teto. Nunca escreve contratos."""
    if not portao():
        return {"CORREU": False, "PORQUE": "portao de egresso IT nao deu PASS"}
    if buscar is None:
        import canario as CAN  # noqa: PLC0415
        import gate_de_rota as G  # noqa: PLC0415
        buscar, robots_de, permitido = CAN.buscar, G.robots_de, G.permitido
    os.makedirs(saida, exist_ok=True)
    pedidos, fora, robots = collections.Counter(), [], {}
    for item in pl["RONDAS"].get(str(ronda), []):
        dom = item["DOMINIO"]
        for u in item["URLS"]:
            host = urlparse(u).hostname
            if host not in robots:
                if pedidos[dom] + 1 > TETO:
                    fora.append({"URL": u, "RESULTADO": "TETO_DOMINIO"}); continue
                robots[host] = robots_de(host); pedidos[dom] += 1
            rp = robots[host][0] if isinstance(robots[host], tuple) else robots[host]
            if not permitido(u, rp):
                fora.append({"URL": u, "RESULTADO": "ROBOTS_PROIBE"}); continue
            if pedidos[dom] + 1 > TETO:
                fora.append({"URL": u, "RESULTADO": "TETO_DOMINIO"}); continue
            time.sleep(pausa)
            st, b, err = buscar(u); pedidos[dom] += 1
            if st != 200 or not b:
                fora.append({"URL": u, "RESULTADO": "HTTP %s %s" % (st, err or "")}); continue
            sha = hashlib.sha256(b).hexdigest()
            with open(os.path.join(saida, sha + ".html"), "wb") as fh:
                fh.write(b)
            r = S.sede_das_paginas([(u, sha, b)])
            fora.append({"URL": u, "RESULTADO": "OK", "SHA256": sha, "BYTES": len(b),
                         "FONTES": pl["POR_DOMINIO"][dom]["URLS"][u],
                         "SEDE_PROPOSTA": {k: r[k] for k in ("SOURCE_LOCATION", "SOURCE_LOCATION_PRECISION",
                                                             "SOURCE_LOCATION_BASIS", "SOURCE_LOCATION_RULE")}})
    rel = {"CORREU": True, "RONDA": ronda, "PEDIDOS_POR_DOMINIO": dict(pedidos),
           "MAXIMO_POR_DOMINIO": max(pedidos.values(), default=0), "PAGINAS": fora,
           "NOTA": "so proposta: nada foi escrito em contratos; a escrita e a porta de sede, com ordem"}
    with open(os.path.join(saida, "MICRO-SEDE-RONDA-%d.json" % ronda), "w", encoding="utf-8") as fh:
        json.dump(rel, fh, ensure_ascii=False, indent=1)
    return rel


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paginas", required=True)
    ap.add_argument("--saida-plano")
    ap.add_argument("--correr", action="store_true")
    ap.add_argument("--ronda", type=int, default=1)
    ap.add_argument("--autorizado")
    ap.add_argument("--saida")
    a = ap.parse_args(argv)
    pl = plano(json.load(open(a.paginas, encoding="utf-8")))
    if a.saida_plano:
        json.dump(pl, open(a.saida_plano, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if not a.correr:
        print(json.dumps({k: pl[k] for k in pl if k not in ("POR_DOMINIO", "RONDAS")}, ensure_ascii=False, indent=1))
        return 0
    if not (a.autorizado and a.saida):
        print("--correr exige --autorizado=<quem autorizou> e --saida=<pasta>", file=sys.stderr)
        return 2
    print(json.dumps(correr(pl, a.ronda, a.saida), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
