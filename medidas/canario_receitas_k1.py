#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""K1 — o canario das fontes com receita nova, numa COPIA dos livros. Nada toca o vivo.

Para cada fonte: egresso (ipinfo) -> PARA se nao for IT; robots pelo leitor da casa
(gate_de_rota) — proibido nao se bate; depois `canario.canario_html` (o canario do
worker, sem alteracao): entrada + 1 item = 3 pedidos por sitio. A prova (DADOS) tem os
campos que `ready_split.passos_da_promocao` le. Grava-se:
  · as provas em <saida>/PROVAS.json (com o sha256 do item aberto no TEXT_SHA256);
  · uma promocao por fonte que PASSOU, no livro da COPIA, pelo `lifecycle.registar`
    apontado a copia — nunca ao livro vivo.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import canario as CAN          # noqa: E402
import gate_de_rota as GATE    # noqa: E402


def egresso() -> dict:
    """EGR (24/09): o pais pelo DONO — superficie/rede.py, consenso de 3 verificadores
    com cache de 3 min. Nenhum consumidor pergunta a um servico diretamente (o
    ipinfo.io em 429 parou tudo das 13:05 as 15:05). O IP nao sai do dono."""
    import importlib.util as _u, os as _os
    _s = _u.spec_from_file_location("rede_egresso", _os.path.join(str(RAIZ), "superficie", "rede.py"))
    _r = _u.module_from_spec(_s)
    _s.loader.exec_module(_r)
    e = _r.egresso()
    pais = e["EGRESS_COUNTRY_CODE"] if e["EGRESS_COUNTRY_CODE"] != "UNKNOWN" else None
    return {"IP": None, "CITY": None, "COUNTRY": pais or "NAO SEI", "VOTOS": e["VOTOS"]}


def correr(contratos: dict, fontes: list[str]) -> list[dict]:
    out = []
    for sid in fontes:
        c = contratos.get(sid)
        eg = egresso()
        linha = {"SOURCE_ID": sid, "EGRESSO": eg, "AT": datetime.now(timezone.utc).isoformat()}
        out.append(linha)
        if eg.get("COUNTRY") != "IT":
            linha["PARADO"] = "EGRESSO_NAO_IT — canario interrompido"
            print("PARAGEM: egresso %s" % eg, flush=True)
            break
        if not c or not (c.get("ACQUISITION") or {}).get("INDEX_URL"):
            linha["PARADO"] = "sem contrato com INDEX_URL"
            continue
        idx = c["ACQUISITION"]["INDEX_URL"]
        rp, txt = GATE.robots_de(urlparse(idx).hostname)
        if "inacessivel" in txt or not GATE.permitido(idx, rp):
            linha["PARADO"] = "robots: " + txt[:100]
            continue
        time.sleep(1)
        r = CAN.canario_html(c)
        linha["CANARIO"] = r
        linha["ACQUISITION_MEDIDA"] = c["ACQUISITION"]
        print("%-11s %s %s" % (sid, r.get("PASS"), (r.get("PORQUE") or r.get("ALVO") or "")[:90]), flush=True)
        time.sleep(1)
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    contratos = {c["SOURCE_ID"]: c for c in json.loads(Path(arg["contratos"]).read_text(encoding="utf-8"))["FONTES"]}
    fontes = json.loads(Path(arg["fontes"]).read_text(encoding="utf-8"))
    res = correr(contratos, fontes)
    Path(arg["saida"]).write_text(json.dumps({"DATASET": "K1-CANARIO-RECEITAS", "LINHAS": res},
                                             ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
