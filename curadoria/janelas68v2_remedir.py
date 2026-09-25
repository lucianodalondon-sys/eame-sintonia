#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JANELAS-68-v2 · A — medir de novo, COM a trava da data, o que o reparo geral ja tinha medido.

SEM REDE (nenhum pedido): repete o reparo + canario sobre os MESMOS bytes guardados nas duas medicoes:
  R182  scripts/receitas_182/CAPTURA-ENTRADAS-V1.json + MEDICAO-COM-REDE-V1.json (14 fontes; entradas,
        robots e itens na pasta da receitas-182, sha256 conferido)
  J68   origin/janelas-68-v1:curadoria/JANELAS-68-MEDICAO-V1.json (32 fontes de janela; entradas e itens
        na pasta j68-bytes, sha256 conferido). O robots dessa medicao foi lido e cumprido na hora mas nao
        foi guardado: aqui so se relem paginas ja abertas com licenca, por isso o robots e permissivo.
O que o reparo quiser e nao estiver guardado responde NAO_MEDIDO (sem rede). Nao escreve em livro nenhum.

    py curadoria/janelas68v2_remedir.py <pasta-receitas-182> <pasta-j68-bytes>
Escreve provas/janelas68v2/REMEDICAO-COM-TRAVA-V1.json.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import urllib.robotparser
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import canario as CAN            # noqa: E402
import gate_de_rota as GATE      # noqa: E402
import reparar_contrato as RC    # noqa: E402

VIVO = Path(r"C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/curadoria")
SAIDA = RAIZ / "provas" / "janelas68v2" / "REMEDICAO-COM-TRAVA-V1.json"
R182 = RAIZ / "scripts" / "receitas_182"


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _carregar(pasta: Path, ficheiros: list, cache: dict):
    for f in ficheiros:
        b = (pasta / f["FICHEIRO"]).read_bytes()
        if _sha(b) != f["SHA256"]:
            raise SystemExit("sha256 mudou: %s" % f["FICHEIRO"])
        cache[f["URL"]] = (f["HTTP"], b, "", f["URL"])


def _git(*a, cwd=RAIZ):
    return subprocess.run(["git", *a], cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
                          check=True).stdout


def main():
    p182, pj68 = Path(sys.argv[1]), Path(sys.argv[2])
    livro = json.loads((VIVO / "italy_contracts_curator.json").read_text(encoding="utf-8"))
    contratos = {c["SOURCE_ID"]: c for c in livro["FONTES"]}
    estado = {}
    for t in json.loads((VIVO / "LIFECYCLE-LEDGER-V1.json").read_text(encoding="utf-8"))["TRANSICOES"]:
        estado[t["SOURCE_ID"]] = t["NEW_STATE"]

    cache, robots = {}, {}
    cap = json.loads((R182 / "CAPTURA-ENTRADAS-V1.json").read_text(encoding="utf-8"))
    m182 = json.loads((R182 / "MEDICAO-COM-REDE-V1.json").read_text(encoding="utf-8"))
    for f in cap["FONTES"]:
        b = (p182 / (f["SOURCE_ID"] + ".html")).read_bytes()
        if _sha(b) != f["SHA256"]:
            raise SystemExit("%s: sha256 da entrada mudou" % f["SOURCE_ID"])
        cache[f["ENTRADA"]] = (f["HTTP"], b, "", f.get("DESTINO") or f["ENTRADA"])
        robots[urlparse(f["ENTRADA"]).netloc] = (p182 / (f["SOURCE_ID"] + ".robots.txt")).read_text(encoding="utf-8")
    _carregar(p182, m182["BYTES_NOVOS"], cache)
    j68 = json.loads(_git("show", "origin/janelas-68-v1:curadoria/JANELAS-68-MEDICAO-V1.json"))
    _carregar(pj68, j68["BYTES_FORA_DO_GIT"]["FICHEIROS"], cache)

    def buscar(url):
        return cache.get(url) or (0, b"", "NAO_MEDIDO: pagina nao guardada (sem rede)", url)

    def robots_de(host):
        rp = urllib.robotparser.RobotFileParser()
        txt = robots.get(host, "User-agent: *\nAllow: /\n")
        rp.parse(txt.splitlines())
        return rp, txt

    antes = {("R182", f["SOURCE_ID"]): f for f in m182["FONTES"]}
    antes.update({("J68", f["SOURCE_ID"]): f for f in j68["FONTES"] if f.get("DESFECHO")})
    linhas = []
    for (conj, sid), a in antes.items():
        if sid not in contratos:
            linhas.append({"CONJUNTO": conj, "SOURCE_ID": sid, "AGORA": "SEM_CONTRATO_NO_LIVRO_VIVO"})
            continue
        base = contratos[sid]
        outros = {c["SOURCE_ID"]: c for c in livro["FONTES"] if c["SOURCE_ID"] != sid
                  and (estado.get(c["SOURCE_ID"]) == "READY_FOR_COLLECTION" or c.get("REPARO_DE_CONTRATO"))}
        RC._ROBOTS.clear()
        p = RC.inferir(base, outros=outros, buscar=buscar, robots_de=robots_de, permitido=GATE.permitido, pausa=0)
        can = None
        if p["DESFECHO"] == "PADRAO_NOVO":
            novo = RC.aplicar(base, p)
            velho = CAN.buscar
            CAN.buscar = lambda u: (lambda r: (r[0], r[1], r[2]))(buscar(u))
            try:
                r = CAN.canario_html(novo)
            finally:
                CAN.buscar = velho
            can = {k: r.get(k) for k in ("PASS", "CLASSE", "PORQUE", "ALVO")}
        passa_antes = a.get("DESFECHO") == "PADRAO_NOVO" and bool((a.get("CANARIO") or {}).get("PASS"))
        passa_agora = bool(can and can.get("PASS"))
        item = p.get("ITEM_LIDO") or {}
        linhas.append({"CONJUNTO": conj, "SOURCE_ID": sid, "PASSAVA_ANTES": passa_antes,
                       "PASSA_COM_TRAVA": passa_agora,
                       "ANTES": [a.get("DESFECHO"), a.get("MOTIVO")], "AGORA": [p["DESFECHO"], p.get("MOTIVO")],
                       "ITEM": item.get("URL"), "DATA_DE_PUBLICACAO": item.get("DATA_DE_PUBLICACAO"),
                       "DATA_PROVADA_POR": item.get("DATA_PROVADA_POR"), "CANARIO": can,
                       "PORQUE": (p.get("PORQUE") or "")[:300]})
        print(conj, sid, "antes", passa_antes, "-> agora", passa_agora, p["DESFECHO"], p.get("MOTIVO") or "",
              item.get("DATA_DE_PUBLICACAO") or "", flush=True)
    medidas = [l for l in linhas if "PASSA_COM_TRAVA" in l]
    out = {"DATASET": "JANELAS-68-V2-REMEDICAO-COM-TRAVA", "SEM_REDE": True, "PEDIDOS": 0,
           "CODIGO": "janelas-68-v2 @ " + _git("rev-parse", "--short", "HEAD").strip(),
           "LIVRO_VIVO_LIDO": _git("rev-parse", "--short", "HEAD", cwd=VIVO).strip(),
           "BYTES": {"R182": str(p182), "J68": str(pj68), "SHA256": "conferido ficheiro a ficheiro"},
           "MEDIDAS": len(medidas),
           "PASSAVAM_ANTES": sum(1 for l in medidas if l["PASSAVA_ANTES"]),
           "PASSAM_COM_TRAVA": sum(1 for l in medidas if l["PASSA_COM_TRAVA"]),
           "DEIXARAM_DE_PASSAR": [l["SOURCE_ID"] for l in medidas if l["PASSAVA_ANTES"] and not l["PASSA_COM_TRAVA"]],
           "PASSAM_AGORA_E_NAO_ANTES": [l["SOURCE_ID"] for l in medidas
                                        if l["PASSA_COM_TRAVA"] and not l["PASSAVA_ANTES"]],
           "SEM_CONTRATO_NO_LIVRO_VIVO": [l["SOURCE_ID"] for l in linhas if "PASSA_COM_TRAVA" not in l],
           "FONTES": linhas}
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for k in ("MEDIDAS", "PASSAVAM_ANTES", "PASSAM_COM_TRAVA", "DEIXARAM_DE_PASSAR", "PASSAM_AGORA_E_NAO_ANTES"):
        print(k, out[k])


if __name__ == "__main__":
    main()
