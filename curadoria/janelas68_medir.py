#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JANELAS-68 · passo 2b: o reparo GERAL do ramo receitas-182-v1 resolveria as que nenhum ramo tocou?

    py curadoria/janelas68_medir.py <pasta-do-codigo-receitas-182> <pasta-dos-bytes-fora-do-git>

NAO e o robo (D41.3): so as fontes desta lista (fila filtrada), 1 por dominio registavel.
Codigo do ramo receitas-182-v1 (reparar_contrato, canario, gate_de_rota), carregado da pasta dada.
Rede so depois do portao de egresso por consenso dar PASS IT, e de novo a cada 10 fontes.
Por dominio: robots (1) + entrada (1) + itens (ate 3) = ate 5 pedidos (teto D38).
Nao escreve em livro nenhum. Escreve curadoria/JANELAS-68-MEDICAO-V1.json; bytes na pasta dada, com sha256.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
CODIGO = Path(sys.argv[1])
BYTES = Path(sys.argv[2])
sys.path.insert(0, str(CODIGO / "curadoria"))
sys.path.insert(0, str(RAIZ / "superficie"))
import canario as CAN            # noqa: E402
import gate_de_rota as GATE      # noqa: E402
import reparar_contrato as RC    # noqa: E402
import rede                      # noqa: E402

VIVO = Path(r"C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/curadoria")
CRUZ = RAIZ / "curadoria" / "JANELAS-68-CRUZAMENTO-V1.json"
SAIDA = RAIZ / "curadoria" / "JANELAS-68-MEDICAO-V1.json"
TETO_ITENS = 3
PAUSA = 2.0
SUFIXOS_REGIONAIS = {"campania", "marche", "veneto", "toscana", "sardegna", "fvg", "vda", "sicilia", "umbria",
                     "puglia", "lombardia", "molise", "calabria", "basilicata", "liguria", "lazio", "piemonte",
                     "abruzzo", "trentino", "bz", "gov"}


def dominio(host: str) -> str:
    p = host.lower().removeprefix("www.").split(".")
    return ".".join(p[-3:]) if len(p) >= 3 and p[-2] in SUFIXOS_REGIONAIS else ".".join(p[-2:])


def vigia():
    e = rede.portao_de_egresso("IT")
    if e["EGRESS_GATE"] != "PASS":
        raise SystemExit("PORTAO FECHADO: %s" % e.get("PORQUE_BLOQUEADO"))
    return "PASS"


def main():
    BYTES.mkdir(parents=True, exist_ok=True)
    cruz = json.loads(CRUZ.read_text(encoding="utf-8"))["FONTES"]
    livro = json.loads((VIVO / "italy_contracts_curator.json").read_text(encoding="utf-8"))
    contratos = {c["SOURCE_ID"]: c for c in livro["FONTES"]}
    estado = {}
    for t in json.loads((VIVO / "LIFECYCLE-LEDGER-V1.json").read_text(encoding="utf-8"))["TRANSICOES"]:
        estado[t["SOURCE_ID"]] = t["NEW_STATE"]
    # 1 por dominio registavel, entre as que nenhum ramo tocou
    escolhidas, fora, vistos = [], [], set()
    for l in cruz:
        if l["VEREDITOS"]:
            continue
        c = contratos[l["SOURCE_ID"]]
        entrada = (c.get("ACQUISITION") or {}).get("INDEX_URL") or c.get("CANONICAL_ENTRY_URL")
        d = dominio(urlparse(entrada).netloc)
        (fora if d in vistos else escolhidas).append((l["SOURCE_ID"], entrada, d))
        vistos.add(d)
    vigias = [vigia()]
    pedidos: dict = {}
    cache, bytes_ = {}, []

    def guardar(url, r):
        if r[1]:
            nome = hashlib.sha256(url.encode()).hexdigest()[:16] + ".html"
            (BYTES / nome).write_bytes(r[1])
            bytes_.append({"URL": url, "HTTP": r[0], "FICHEIRO": nome, "SHA256": hashlib.sha256(r[1]).hexdigest()})

    linhas = []
    for n, (sid, entrada, d) in enumerate(escolhidas, 1):
        if n % 10 == 0:
            vigias.append(vigia())
        host = urlparse(entrada).netloc
        l = {"SOURCE_ID": sid, "ENTRADA": entrada, "DOMINIO": d}
        try:
            _, txt = GATE.robots_de(host)
            pedidos[d] = pedidos.get(d, 0) + 1
            rp = GATE.urllib.robotparser.RobotFileParser()
            rp.parse((txt or "").splitlines())
            if not GATE.permitido(entrada, rp):
                l["DESFECHO"] = "ROBOTS_PROIBE_A_ENTRADA"
                linhas.append(l)
                continue
        except Exception as e:  # noqa: BLE001
            l.update({"DESFECHO": "ROBOTS_ILEGIVEL", "ERRO": repr(e)[:160]})
            linhas.append(l)
            continue
        time.sleep(PAUSA)
        r = RC.buscar_com_destino(entrada)
        pedidos[d] += 1
        cache[entrada] = r
        guardar(entrada, r)
        l.update({"HTTP": r[0], "BYTES": len(r[1] or b"")})
        if not r[1]:
            l["DESFECHO"] = "ENTRADA_NAO_ABRIU"
            linhas.append(l)
            continue

        def buscar(url, d=d):
            if url in cache:
                return cache[url]
            if pedidos.get(dominio(urlparse(url).netloc), 0) >= 2 + TETO_ITENS:
                return 0, b"", "NAO_MEDIDO: teto D38 do dominio", url
            pedidos[dominio(urlparse(url).netloc)] = pedidos.get(dominio(urlparse(url).netloc), 0) + 1
            rr = RC.buscar_com_destino(url)
            cache[url] = rr
            guardar(url, rr)
            return rr

        def robots_de(h, rp=rp, txt=txt):
            return rp, txt

        outros = {c["SOURCE_ID"]: c for c in livro["FONTES"] if c["SOURCE_ID"] != sid
                  and (estado.get(c["SOURCE_ID"]) == "READY_FOR_COLLECTION" or c.get("REPARO_DE_CONTRATO"))}
        p = RC.inferir(contratos[sid], outros=outros, buscar=buscar, robots_de=robots_de,
                       permitido=GATE.permitido, pausa=PAUSA)
        l.update({"DESFECHO": p["DESFECHO"], "MOTIVO": p.get("MOTIVO"), "PORQUE": (p.get("PORQUE") or "")[:240],
                  "LINK_PATTERN": p.get("LINK_PATTERN"), "ITEM_LIDO": p.get("ITEM_LIDO")})
        if p["DESFECHO"] == "PADRAO_NOVO":
            novo = RC.aplicar(contratos[sid], p)
            antes = CAN.buscar
            CAN.buscar = lambda u: (lambda x: (x[0], x[1], x[2]))(cache[u]) if u in cache else (
                0, b"", "NAO_MEDIDO: pagina nao lida pelo reparo")
            try:
                rc = CAN.canario_html(novo)
            finally:
                CAN.buscar = antes
            l["CANARIO"] = {k: rc.get(k) for k in ("PASS", "CLASSE", "PORQUE", "ALVO", "DETAIL_GATE_PASSED")}
        linhas.append(l)
        print(sid, d, l.get("HTTP"), l["DESFECHO"], l.get("MOTIVO") or "", "| canario:",
              (l.get("CANARIO") or {}).get("PASS"), flush=True)
        time.sleep(PAUSA)
    vigias.append(vigia())
    out = {"DATASET": "JANELAS-68-MEDICAO-V1", "EM": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "CODIGO": "receitas-182-v1 @ " + (CODIGO / ".git").read_text(encoding="utf-8").strip()[:80],
           "VIGIAS": vigias, "PEDIDOS_POR_DOMINIO": pedidos, "PEDIDOS_TOTAL": sum(pedidos.values()),
           "MAX_POR_DOMINIO": max(pedidos.values()) if pedidos else 0,
           "MEDIDAS": len(linhas), "NAO_MEDIDAS_OUTRA_DO_MESMO_DOMINIO": [s for s, _, _ in fora],
           "PADRAO_NOVO": sum(1 for x in linhas if x.get("DESFECHO") == "PADRAO_NOVO"),
           "CANARIO_PASS": sum(1 for x in linhas if (x.get("CANARIO") or {}).get("PASS")),
           "BYTES_FORA_DO_GIT": {"PASTA": str(BYTES), "FICHEIROS": bytes_}, "FONTES": linhas}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("MEDIDAS", out["MEDIDAS"], "PADRAO_NOVO", out["PADRAO_NOVO"], "CANARIO_PASS", out["CANARIO_PASS"],
          "PEDIDOS", out["PEDIDOS_TOTAL"], "MAX/DOMINIO", out["MAX_POR_DOMINIO"],
          "NAO_MEDIDAS(mesmo dominio)", len(fora))


if __name__ == "__main__":
    main()
