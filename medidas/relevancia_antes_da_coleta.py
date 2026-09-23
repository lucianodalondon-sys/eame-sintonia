#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RELEVANCIA ANTES DA COLETA — a rota existe; o conteudo serve para a Sala?

    ROTA != RELEVANCIA. PREVER O RENDIMENTO ANTES DE COLHER.

Medido pela missao 4 (diagnostico-sala-v1 @ 44c873ff): 55 de 71 itens que nao
chegaram a Sala vieram de tres fontes com rota perfeita e conteudo de marca.
Este instrumento amostra, pela ROTA PROVADA (`curadoria/ROTAS-ELEGIVEIS-V1.json`),
materias individuais de cada fonte e julga-as com a PROPRIA porta:

    bytes  -> coleta/executor_texto_de_html.extrair   (o derivador da casa)
    texto  -> orquestrador.item_documental_para_a_porta (o tradutor da casa)
    item   -> admissao.decidir(item, universo_da_fonte) (a porta, em memoria)

    NUNCA admissao.escrever(). NUNCA a base. Zero alteracao a regua.

Cadencia: robots (1) + INDEX_URL (1) + ate 2 materias = 4 pedidos por fonte,
1 s de pausa. O egresso e lido (ipinfo.io) antes de cada fonte e escrito.

O universo e o do SOURCE_ID (`IT-Tn-...` -> `Tn`) — a mesma leitura da missao 4.
Universo sem regua na porta e dito com esse nome, e nao contado como NAO.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "medidas"))
import _gavetas  # noqa: E402,F401
import admissao as adm                      # noqa: E402
from coleta import executor_texto_de_html as HTMLX  # noqa: E402
import orquestrador as ORQ  # noqa: E402
import canario as CAN                       # noqa: E402
import gate_de_rota as GATE                 # noqa: E402
import canario_rotas_elegiveis as ROTAS     # noqa: E402

PROVAS = RAIZ / "curadoria" / "ROTAS-ELEGIVEIS-V1.json"
SAIDA = RAIZ / "curadoria" / "RELEVANCIA-ELEGIVEIS-V1.json"
PAUSA_S = 1.0
MAX_MATERIAS = 2


def egresso() -> str:
    try:
        with urllib.request.urlopen("https://ipinfo.io/json", timeout=15) as r:
            d = json.loads(r.read())
        return "%s %s %s" % (d.get("ip"), d.get("city"), d.get("country"))
    except Exception as e:                                      # noqa: BLE001
        return "NAO SEI (%s)" % type(e).__name__


def julgar(sid: str, universo: str, url: str, corpo: bytes, n: int) -> dict:
    texto, estado, erro, medidas = HTMLX.extrair(corpo, "text/html")
    item = ORQ.item_documental_para_a_porta(
        {"TEXTO": texto, "SOURCE_ID": sid,
         "PARENT_SHA256": hashlib.sha256(corpo).hexdigest(),
         "DERIVED_ARTIFACT_ID": "amostra:%s:%d" % (sid, n),
         "CAPTURED_AT": datetime.now(timezone.utc).isoformat()},
        source_id=sid)
    d = adm.decidir(item, universo, corrida="RELEVANCIA-ELEGIVEIS-V1")
    # A leitura TEMATICA isolada, pela mesma funcao que `decidir` chama no fim.
    # Existe porque uma amostra sem raw_asset pode parar numa prontidao que a
    # coleta real preencheria — e entao `decidir` nao chegaria ao tema.
    if universo in adm.PERGUNTAS_DO_UNIVERSO:
        r, motivo, ev = adm._do_universo({"texto": texto}, universo,
                                         adm.PERGUNTAS_DO_UNIVERSO[universo])
        tema = {"RESULTADO": r, "MOTIVO": motivo[:200],
                "PALAVRAS": ev.get("palavras", []), "NOUTRO": ev.get("achado_noutro", {})}
    else:
        tema = {"RESULTADO": "SEM_REGUA",
                "MOTIVO": "a porta nao tem PERGUNTAS_DO_UNIVERSO[%r]" % universo}
    return {"URL": url, "BYTES": len(corpo), "EXTRACAO": estado,
            "NON_WHITESPACE_CHARACTERS": medidas.get("NON_WHITESPACE_CHARACTERS"),
            "DECIDIR": {"RESULTADO": d.resultado, "REGRA": d.regra,
                        "MOTIVO": (d.motivo or "")[:200]},
            "TEMA": tema, "TEXTO_INICIO": texto[:300]}


def amostrar(linha: dict, contrato: dict) -> dict:
    sid = linha["SOURCE_ID"]
    universo = sid.split("-")[1]
    out = {"SOURCE_ID": sid, "UNIVERSO": universo, "OWNER": linha.get("OWNER"),
           "EGRESSO": egresso(), "PEDIDOS": 0, "AMOSTRAS": []}
    aq = contrato["ACQUISITION"]
    rp, txt = GATE.robots_de(urlparse(aq["INDEX_URL"]).hostname)
    out["PEDIDOS"] += 1
    if "inacessivel" in txt or not GATE.permitido(aq["INDEX_URL"], rp):
        out["PARADO"] = "robots: " + txt[:120]
        return out
    time.sleep(PAUSA_S)
    st, corpo, err = CAN.buscar(aq["INDEX_URL"])
    out["PEDIDOS"] += 1
    if st != 200:
        out["PARADO"] = "indice HTTP %s %s" % (st, err)
        return out
    links = ROTAS.ligacoes_pelo_motor(corpo, aq)
    out["LINKS_DE_DETALHE"] = len(links)
    for n, u in enumerate(links[:MAX_MATERIAS]):
        if not GATE.permitido(u, rp):
            out["AMOSTRAS"].append({"URL": u, "PARADO": "robots proibe"})
            continue
        time.sleep(PAUSA_S)
        st, corpo, err = CAN.buscar(u)
        out["PEDIDOS"] += 1
        if st != 200:
            out["AMOSTRAS"].append({"URL": u, "PARADO": "HTTP %s %s" % (st, err)})
            continue
        out["AMOSTRAS"].append(julgar(sid, universo, u, corpo, n))
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    provas = json.loads(PROVAS.read_text(encoding="utf-8"))["LINHAS"]
    livros = {}
    fontes = []
    for l in provas:
        if l.get("VEREDITO") != "ROUTE_PROVEN":
            continue
        ref = l["CONTRATO_LIDO_DE"].split(":")[0]
        if ref not in livros:
            livros[ref] = ROTAS._contratos_de(ref)
        f = amostrar(l, livros[ref][l["SOURCE_ID"]])
        fontes.append(f)
        print("%-11s %-4s %s | %s" % (f["SOURCE_ID"], f["UNIVERSO"], f["EGRESSO"],
              " ".join("%s/%s" % (a.get("DECIDIR", {}).get("RESULTADO"),
                                   a.get("TEMA", {}).get("RESULTADO"))
                       for a in f["AMOSTRAS"])), flush=True)
        time.sleep(PAUSA_S)
    d = {"DATASET": "RELEVANCIA-ELEGIVEIS-V1",
         "GERADO_EM": datetime.now(timezone.utc).isoformat(),
         "INSTRUMENTO": "medidas/relevancia_antes_da_coleta.py",
         "LEI": "admissao.decidir em memoria; nunca escrever(); zero base; regua intocada",
         "FONTES": fontes}
    if "--escrever" in argv:
        SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
