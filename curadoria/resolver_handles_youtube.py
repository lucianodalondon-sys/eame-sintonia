#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOC4 · OS 35 @HANDLE DO YOUTUBE PASSAM A TER channel_id — PELA ROTA DO SCRAP.

    py curadoria/resolver_handles_youtube.py                      # plano: quais e quantos (sem rede)
    py curadoria/resolver_handles_youtube.py --resolver --run-id=X # resolve (precisa da chave NO AMBIENTE)

O QUE ISTO RESOLVE
------------------
Das 71 candidatas YouTube da porta, 35 vêm como `@handle`, `/user/`, `/c/` ou
playlist: o endereço não traz o channel_id, e o QUALIFY para em NAO SEI (sem
fabricar). Resolver é uma capacidade QUE O SCRAP JÁ TEM — `youtube.channel.resolve`
(`channels.list forHandle` / `forUsername`, API oficial, 1 unidade cada). Este
ficheiro não a imita: pede-a ao Scrap pela fronteira canónica
(`scrap_executor.COLLECT`), candidata a candidata, e guarda o resultado num
registo que o QUALIFY lê.

A CHAVE
-------
Vive como secret do repositório no GitHub Actions (`YOUTUBE_DATA_API_KEY`). Este
ficheiro NUNCA a lê para texto: quem responde se ela está no ambiente é o
`scrap_executor.CHECK` (sem gastar); sem ela, a saída é `CREDENTIAL_MISSING` e
nada corre. Nesta máquina ela não está — por desenho.

O QUE SE GUARDA (D20)
---------------------
Só o que prova a identidade: o handle pedido, o `CHANNEL_ID` devolvido, como
(`RESOLVED_BY`), a corrida e a hora. O título do canal é dado da API e NÃO se
guarda aqui — a regra dos 30 dias não tem nada a apagar neste ficheiro.

    `/c/<nome>` NÃO TEM ROTA OFICIAL: fica NAO_RESOLVIDO com o porquê, e não
    se tenta outra rota (nem página, nem yt-dlp). Playlist não é canal.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for _p in ("curadoria", "candidatas", "coleta", "leis", "admissao", "regras", "ferramentas",
           "medidas", "guarda", "pedido", "orquestrador", ""):
    q = str(RAIZ / _p) if _p else str(RAIZ)
    if q not in sys.path:
        sys.path.append(q)

import fonte_nova as FN              # noqa: E402
import rota_do_scrap_youtube as RSY  # noqa: E402

REGISTO = RAIZ / "curadoria" / "RESOLUCAO-HANDLES-YOUTUBE-V1.json"
CAPACIDADE = "youtube.channel.resolve"


#: As formas que a capacidade do Scrap resolve pela API. As outras NÃO vão à API:
#:   /c/<nome>   não tem rota oficial (a própria capacidade o diz);
#:   playlist    NÃO é canal — e o resolvedor leria `playlist` como um handle nu,
#:               devolvendo o canal de outra pessoa qualquer. Identidade fabricada.
RESOLVIVEIS = ("HANDLE", "USER", "NOME_NU")


def forma(url: str) -> str:
    u = (url or "").lower()
    if "list=" in u or "/playlist" in u:
        return "PLAYLIST"
    if "/@" in u:
        return "HANDLE"
    if "/user/" in u:
        return "USER"
    if "/c/" in u:
        return "C"
    m = re.search(r"youtube\.com/([^/?#]+)/?(?:[?#].*)?$", u)
    if m and m.group(1) not in ("watch", "channel", "results", "feed", "shorts", "embed"):
        return "NOME_NU"
    return "OUTRO"


def pendentes(candidatas: dict | None = None) -> list[dict]:
    """As candidatas YouTube cujo endereço NÃO traz o channel_id."""
    cand = FN.carregar() if candidatas is None else candidatas
    return [{"CANDIDATA_ID": c["CANDIDATA_ID"], "URL": c.get("URL", ""), "FORMA": forma(c.get("URL", ""))}
            for c in cand.get("CANDIDATAS", [])
            if c.get("TIPO") == "YOUTUBE" and not RSY.channel_id_da_url(c.get("URL", ""))]


def pronto() -> dict:
    """O CHECK do Scrap para a capacidade — sem gastar, sem ler a chave."""
    import scrap_executor as sx
    v = sx.CHECK("YOUTUBE", CAPACIDADE)
    return {"CAN": v.get("CAN"), "STATE": v.get("STATE")}


def resolver(lista: list[dict], run_id: str, collect=None) -> list[dict]:
    if collect is None:
        import scrap_executor as sx
        collect = sx.COLLECT
    quando = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    fora = []
    for c in lista:
        if c.get("FORMA", forma(c["URL"])) not in RESOLVIVEIS:
            fora.append({"CANDIDATA_ID": c["CANDIDATA_ID"], "URL": c["URL"], "ESTADO": "NAO_SUPORTADO",
                         "CHANNEL_ID": None, "RESOLVED_BY": None, "RUN_ID": run_id, "RESOLVIDO_EM": quando,
                         "PORQUE": ("playlist nao e canal (o dono dela sai por playlists.list, rota que o "
                                    "Scrap nao declara)" if c.get("FORMA") == "PLAYLIST" else
                                    "/c/ nao tem rota oficial" if c.get("FORMA") == "C" else
                                    "forma de endereco desconhecida")})
            continue
        objetos, trace = collect(platform="YOUTUBE", capability=CAPACIDADE, run_id=run_id,
                                 account_url=c["URL"])
        o = (objetos or [{}])[0]
        canal = o.get("CHANNEL_ID")
        fora.append({"CANDIDATA_ID": c["CANDIDATA_ID"], "URL": c["URL"],
                     "ESTADO": "RESOLVIDO" if canal and RSY.RE_CANAL.match(canal) else "NAO_RESOLVIDO",
                     "CHANNEL_ID": canal if canal and RSY.RE_CANAL.match(canal) else None,
                     "RESOLVED_BY": o.get("RESOLVED_BY"),
                     "PORQUE": (trace or {}).get("WHY") or (trace or {}).get("RESULT"),
                     "RUN_ID": run_id, "RESOLVIDO_EM": quando})
    return fora


def gravar(linhas: list[dict], destino: Path = REGISTO) -> None:
    anterior = {}
    if destino.exists():
        anterior = {l["CANDIDATA_ID"]: l for l in json.loads(destino.read_text(encoding="utf-8"))["LINHAS"]}
    for l in linhas:
        # Uma resolução nova só substitui a antiga se RESOLVEU: um erro de hoje
        # não apaga a prova de ontem.
        if l["ESTADO"] == "RESOLVIDO" or l["CANDIDATA_ID"] not in anterior:
            anterior[l["CANDIDATA_ID"]] = l
    d = {"DATASET": "RESOLUCAO-HANDLES-YOUTUBE-V1",
         "LEI": ("channel_id de candidatas YouTube cujo endereco nao o traz, resolvido pela "
                 "capacidade youtube.channel.resolve do Scrap (API oficial). So identidade: sem "
                 "titulo nem outro dado da API. Lido pelo QUALIFY (rota_do_scrap_youtube.canal_resolvido)."),
         "RESUMO": dict(Counter(l["ESTADO"] for l in anterior.values())),
         "LINHAS": sorted(anterior.values(), key=lambda l: l["CANDIDATA_ID"])}
    destino.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    lista = pendentes()
    print("PENDENTES %d · %s · vao a API: %d" % (len(lista), dict(Counter(c["FORMA"] for c in lista)),
                                                 sum(c["FORMA"] in RESOLVIVEIS for c in lista)))
    if "--resolver" not in argv:
        return 0
    p = pronto()
    print("CHECK %s" % p["STATE"])
    if not p["CAN"]:
        print("NAO_CORREU: a chave nao esta NESTE ambiente (%s). Corre no GitHub Actions: "
              "workflow curator-youtube-handles." % p["STATE"])
        return 3
    run_id = arg.get("run-id") or os.environ.get("GITHUB_RUN_ID")
    if not run_id:
        print("SEM_RUN_ID")
        return 2
    linhas = resolver(lista, "SOC4-HANDLES-%s" % run_id)
    gravar(linhas)
    print("RESOLVIDOS %d de %d" % (sum(l["ESTADO"] == "RESOLVIDO" for l in linhas), len(linhas)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
