#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UM PEDIDO T6 ATRAVESSA? — o botao canonico, com as rodadas ja guardadas, SEM rede.

    py provas/o_pedido_t6_atravessa.py --universo=T5|T6 --sala=<pasta vazia> [--banco=<URL>]

Aperta `orquestrador.correr()` com `Pedido(alvo="T6", filtros={universo})`, como a
prova do T4 (`provas/o_pedido_t4_atravessa.py`), e conta o que saiu em cada etapa:
EXECUTOR (colheita declarada) -> INGRESSO/RAW -> DERIVACAO -> ADMISSAO -> SALA.

    --banco ausente  : o bruto fica so em disco; a Sala e a de FICHEIRO em --sala
    --banco=<URL>    : RAW/RUN no Postgres descartavel (nunca a Sala real)

NAO chama a porta a mao: so o botao. O que a Admissao decide e lido do recibo.
O universo e declarado NO PEDIDO (ALVO != UNIVERSO): T5 usa a regua de ciencia que ja
existe; T6 mede o que acontece a um universo sem regua.
"""
import json
import os
import pathlib
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import admissao                                     # noqa: E402
import sala_de_espera as espera                     # noqa: E402
from pedido import Pedido                           # noqa: E402


def _memoria(url):
    import importlib.util as u
    sp_ = u.spec_from_file_location("prova_pg", os.path.join(RAIZ, "provas", "preservar_coleta_no_postgres.py"))
    m = u.module_from_spec(sp_)
    sp_.loader.exec_module(m)
    return m.MemoriaPostgres(url)


def main(argv):
    opt = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    universo = opt.get("universo", "T5")
    sala = opt.get("sala") or tempfile.mkdtemp(prefix="sala-t6-")
    os.makedirs(sala, exist_ok=True)
    if os.listdir(sala):
        print("a sala do ensaio tem de comecar vazia: %s" % sala)
        return 2
    espera.MORADA = sala
    admissao.LIVRO = pathlib.Path(tempfile.mkdtemp(prefix="livro-t6-")) / "LIVRO-DE-DECISOES.json"
    import orquestrador as orq
    p = Pedido(alvo="T6", filtros={"pais": "IT", "universo": universo})
    kw = {}
    if opt.get("banco"):
        import coleta_checkpoint as cc
        kw = {"memoria": _memoria(opt["banco"]), "banco_do_rastro": cc.Banco(opt["banco"])}
    recibo = orq.correr(p, **kw)
    recibo.pop("_plano", None)
    livro = json.loads(admissao.LIVRO.read_text(encoding="utf-8")) if admissao.LIVRO.exists() else {}
    decisoes = livro.get("DECISOES", []) if isinstance(livro, dict) else []
    conta = {}
    for d in decisoes:
        conta[d.get("resultado")] = conta.get(d.get("resultado"), 0) + 1
    motivos = {}
    for d in decisoes:
        if d.get("resultado") != "SIM":
            k = (d.get("regra") or "") + " :: " + (d.get("motivo") or "")[:90]
            motivos[k] = motivos.get(k, 0) + 1
    na_sala = sum(1 for _ in pathlib.Path(sala).rglob("*") if _.is_file())
    ing = recibo.get("INGRESSO") or {}
    der = recibo.get("DERIVACAO") or {}
    out = {
        "UNIVERSO_DO_PEDIDO": universo, "RUN_ID": recibo.get("RUN_ID"), "STATUS": recibo.get("STATUS"),
        "ACTOR": recibo.get("ACTOR"), "COMANDO": recibo.get("COMANDO"),
        "COLHEITA_ENCONTRADA": recibo.get("COLHEITA_ENCONTRADA"),
        "RETORNO": recibo.get("RETORNO"),
        "INGRESSO": {k: (v if not isinstance(v, list) else len(v)) for k, v in ing.items()
                     if not isinstance(v, dict)},
        "DERIVACAO": {k: (v if not isinstance(v, list) else len(v)) for k, v in der.items()
                      if not isinstance(v, dict)},
        "ADMISSAO": conta, "NAO_SIM_POR_MOTIVO": dict(sorted(motivos.items(), key=lambda kv: -kv[1])[:8]),
        "PORTA": recibo.get("PORTA") or recibo.get("ADMISSAO"),
        "SALA_FICHEIROS": na_sala, "SALA": sala, "ERRO": (recibo.get("ERROR") or "")[:400],
    }
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:12000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
