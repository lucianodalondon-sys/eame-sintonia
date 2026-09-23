"""Recolhe paginas JA ESCOLHIDAS (missao LD2) — as mesmas regras do colher_gabarito.

NAO e coleta: nada vai a Sala, ao armazem oficial, ao banco, aos livros. Os bytes
ficam numa pasta fora do Git, com um MANIFESTO no formato que o pacote G1 le
(URL, SHA256, FICHEIRO relativo a pasta).

    py scripts/detector_capa/colher_urls.py --pedido=<pedido.json> --saida=<pasta>

pedido.json = [{"SOURCE_ID": ..., "URLS": [[url, papel, porque], ...]}, ...]
  no maximo 2 URLs por entrada, TODAS do mesmo host.

Regras da ida, no codigo (as do colher_gabarito):
  · egresso medido ANTES de cada site; se nao for IT, PARA TUDO;
  · no maximo 3 pedidos por site (robots + 2 paginas), 1 s de pausa;
  · robots lido pelo leitor da casa (gate_de_rota.robots_de), UA da casa; o que o
    robots nega nao se pede; 403 nao se contorna;
  · um site ja presente no manifesto nao se visita outra vez (o teto e por site).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import colher_gabarito as CG  # noqa: E402  egresso(), guardar(), CAN, GR

MAX_PAGINAS_POR_SITE = 2


def _host(u: str) -> str:
    return urlparse(u).netloc.lower().removeprefix("www.")


def recolher(pedido: list[dict], pasta: Path) -> dict:
    pasta.mkdir(parents=True, exist_ok=True)
    mf = pasta / "MANIFESTO.json"
    d = json.loads(mf.read_text(encoding="utf-8")) if mf.exists() else {"PAGINAS": [], "REGISTO": []}
    vistos = {r["HOST"] for r in d["REGISTO"]}
    for e in pedido:
        sid, urls = e["SOURCE_ID"], e["URLS"][:MAX_PAGINAS_POR_SITE]
        hosts = {_host(u) for u, *_ in urls}
        if len(hosts) != 1:
            raise ValueError(f"{sid}: URLs de hosts diferentes {hosts}")
        host = hosts.pop()
        if host in vistos:
            d["REGISTO"].append({"SOURCE_ID": sid, "HOST": host, "PAROU": "SITE_JA_VISITADO"})
            continue
        eg = CG.egresso()
        if eg.get("PAIS") != "IT":
            d["REGISTO"].append({"SOURCE_ID": sid, "HOST": host, "PAROU": "EGRESSO_NAO_IT", "EGRESSO": eg})
            print(f"PARADO: egresso {eg} antes de {sid}", file=sys.stderr)
            break
        vistos.add(host)
        rp, porque_robots = CG.GR.robots_de(urlparse(urls[0][0]).netloc)
        linha = {"SOURCE_ID": sid, "HOST": host, "ROBOTS": porque_robots[:120], "EGRESSO": eg,
                 "PEDIDOS": 1, "PAGINAS": []}
        for u, papel, porque in urls:
            if not rp.can_fetch(CG.GR.CAP.UA, u):
                linha["PAGINAS"].append({"URL": u, "PAROU": "ROBOTS_NEGA"})
                continue
            time.sleep(1)
            st, b, err = CG.CAN.buscar(u)
            linha["PEDIDOS"] += 1
            if st != 200 or not b:
                linha["PAGINAS"].append({"URL": u, "PAROU": err or f"HTTP {st}"})
                continue
            d["PAGINAS"].append(CG.guardar(pasta, sid, papel, u, st, b, eg, porque))
            linha["PAGINAS"].append({"URL": u, "HTTP": st, "BYTES": len(b)})
        d["REGISTO"].append(linha)
        mf.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    mf.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return d


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    pedido = json.loads(Path(arg["pedido"]).read_text(encoding="utf-8"))
    d = recolher(pedido, Path(arg["saida"]))
    for r in d["REGISTO"][-len(pedido):]:
        print(json.dumps(r, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
