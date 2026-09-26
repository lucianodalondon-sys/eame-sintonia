#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D90 · ENSAIO da escrita dos pacotes TABLE_EXTRACTION pelo ESCRITOR UNICO do derivado (`guarda/preservar_derivado.py`),
num banco DESCARTAVEL. So para os documentos cujo RAW ja esta na Sala (os outros precisam de entrar como RAW antes).

    BANCO_DESCARTAVEL_URL=<postgres descartavel>  py curadoria/d90_preservar_pacotes.py --pacotes=<pasta do d90_payload_series>
        --armazem=<pasta vazia fora do Git> [--aplicar] [--recibo=<json>]

Sem --aplicar: diz o que escreveria. Com --aplicar: escreve pelo dono e LE OUTRA VEZ (o recibo e do dono, nao daqui).
RECUSA a Sala real: se o DSN for o de C:/Users/London1/sintonia-sala-italia/SALA_DSN.txt ou usar a porta 54330. Levar isto
a Sala real e decisao + instalacao do coordenador (e ha contrato por fechar: ver CAMINHO-SERIES-SALA-D90.md).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path[:0] = [str(RAIZ), str(AQUI)]

SALA_DSN = Path("C:/Users/London1/sintonia-sala-italia/SALA_DSN.txt")
PORTA_DA_SALA_REAL = "54330"
FICHEIROS_DO_PRODUTOR = ("series_sinal_precoce.py", "d90_payload_series.py")


def versao_do_produtor() -> str:
    h = hashlib.sha256()
    for f in FICHEIROS_DO_PRODUTOR:
        h.update((AQUI / f).read_bytes().replace(b"\r\n", b"\n"))
    return "d90@" + h.hexdigest()[:12]


def e_a_sala_real(dsn: str) -> bool:
    if not dsn:
        return False
    if (":%s" % PORTA_DA_SALA_REAL) in dsn or ("port=%s" % PORTA_DA_SALA_REAL) in dsn:
        return True
    try:
        return SALA_DSN.exists() and SALA_DSN.read_text(encoding="utf-8").strip() == dsn.strip()
    except OSError:
        return False


def pedidos(pasta: Path) -> list[tuple[dict, bytes, dict]]:
    import d90_payload_series as P
    man = json.loads((pasta / "MANIFESTO.json").read_text(encoding="utf-8"))
    out = []
    for d in man["DOCUMENTOS"]:
        if d["RAW"] != "PRESENTE" or not d["LINHAS"]:
            continue   # sem RAW nao ha pai; sem linhas nao ha tabela (ARPAV N.56: a seccao vem cortada no PDF)
        b = (pasta / d["PACOTE"]).read_bytes()
        assert hashlib.sha256(b).hexdigest() == d["PACOTE_SHA256"], d["PACOTE"]
        out.append(({"raw_asset_id": d["RAW_ID_PAI_PROPOSTO"], "kind": "TABLE_EXTRACTION", "producer": P.PRODUTOR,
                     "producer_version": versao_do_produtor(), "pipeline_version": "D90-ensaio",
                     "parameters": {"CONTRATO": P.CONTRATO, "FORMA": d["FORMA"]}, "serie_posicao": None,
                     "media_type": "application/json"}, b, d))
    return out


def correr(pasta: Path, armazem, memoria, aplicar: bool) -> list[dict]:
    from guarda.preservar_derivado import preservar_derivado
    res = []
    for pedido, b, d in pedidos(pasta):
        linha = {"SOURCE_ID": d["SOURCE_ID"], "RAW_ASSET_ID": pedido["raw_asset_id"], "PACOTE": d["PACOTE"],
                 "LINHAS": d["LINHAS"]}
        if not aplicar:
            res.append({**linha, "ESTADO": "A_SECO"})
            continue
        r = preservar_derivado(pedido, b, armazem, memoria)
        res.append({**linha, "ESTADO": r.get("ESTADO"), "PORQUE": r.get("PORQUE"),
                    "DERIVADO": {k: r.get(k) for k in ("ID", "SHA256", "STORAGE_PATH") if k in r} or r.get("DERIVADO")})
    return res


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    aplicar = "--aplicar" in argv
    dsn = os.environ.get(a.get("dsn-env", "BANCO_DESCARTAVEL_URL"), "")
    if e_a_sala_real(dsn):
        print("RECUSADO: o DSN e o da Sala real — isto e ENSAIO (banco descartavel). A Sala real e do coordenador.",
              file=sys.stderr)
        return 2
    if aplicar and not dsn:
        print("RECUSADO: --aplicar sem BANCO_DESCARTAVEL_URL", file=sys.stderr)
        return 2
    from guarda.preservar_coleta import ArmazemLocal
    armazem = ArmazemLocal(a["armazem"]) if a.get("armazem") else None
    memoria = None
    if aplicar:
        from guarda.memoria_postgres import MemoriaPostgres
        memoria = MemoriaPostgres(dsn)
    res = correr(Path(a["pacotes"]), armazem, memoria, aplicar)
    out = {"MODO": "APLICAR" if aplicar else "A_SECO", "PRODUCER_VERSION": versao_do_produtor(), "RESULTADOS": res}
    if a.get("recibo"):
        Path(a["recibo"]).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"MODO": out["MODO"], "PEDIDOS": len(res),
                      "POR_ESTADO": {e: sum(1 for r in res if r["ESTADO"] == e) for e in sorted({r["ESTADO"] for r in res})}},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
