#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JANELAS-68-v2 · C — ARSAC (IT-T2-148) mudou de arsacweb.it para arsac.calabria.it: achar a LISTA de
edicoes no site novo e deixar o reparo da casa (com a trava da data) propor o contrato.

Canario autorizado pela missao: portao de egresso IT por consenso antes e depois; 1 dominio;
robots.txt lido e cumprido; teto D38 = 5 pedidos NO TOTAL ao arsac.calabria.it (robots incluido).
NAO escreve em livro nenhum; o contrato proposto vai para ARSAC-PROPOSTA-V1.json.

    py provas/janelas68v2/arsac_sonda.py <pasta-dos-bytes-fora-do-git>
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import urllib.robotparser
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "superficie"))
import canario as CAN            # noqa: E402
import gate_de_rota as GATE      # noqa: E402
import reparar_contrato as RC    # noqa: E402
import rede                      # noqa: E402

VIVO = Path(r"C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/curadoria")
SID = "IT-T2-148"
NOVO = "https://arsac.calabria.it"
TETO = 5
PAUSA = 3.0
EDICAO = re.compile(r"bollettino-agrometeorologico-e-fitosanitario", re.I)
SAIDA = Path(__file__).resolve().parent / "ARSAC-PROPOSTA-V1.json"


def main():
    pasta = Path(sys.argv[1])
    pasta.mkdir(parents=True, exist_ok=True)
    vigias = []

    def vigia():
        e = rede.portao_de_egresso("IT")
        vigias.append({"EGRESS_GATE": e["EGRESS_GATE"], "VOTOS": [v.get("PAIS") for v in e.get("VOTOS") or []]})
        if e["EGRESS_GATE"] != "PASS":
            raise SystemExit("PORTAO FECHADO: %s" % e.get("PORQUE_BLOQUEADO"))

    vigia()
    pedidos, lidas, cache = [], [], {}
    # rodada 2: o que a rodada 1 ja leu vem da pasta (sha256 conferido) e CONTA para o teto de 5
    anterior = Path(__file__).resolve().parent / "ARSAC-SONDA-RODADA1-ENTRADA-ERRADA.json"
    if anterior.exists():
        r1 = json.loads(anterior.read_text(encoding="utf-8"))
        pedidos.extend(r1["PEDIDOS"])
        for f in r1["BYTES_FORA_DO_GIT"]["FICHEIROS"]:
            b = (pasta / f["FICHEIRO"]).read_bytes()
            if hashlib.sha256(b).hexdigest() != f["SHA256"]:
                raise SystemExit("sha256 mudou: %s" % f["FICHEIRO"])
            cache[f["URL"]] = (f["HTTP"], b, "", f["URL"])
            lidas.append(f)

    def buscar(url):
        if url in cache:
            return cache[url]
        if not url.startswith(NOVO + "/") and url != NOVO:
            return 0, b"", "NAO_MEDIDO: fora do dominio da sonda", url
        if len(pedidos) >= TETO:
            return 0, b"", "NAO_MEDIDO: teto D38 (5 pedidos)", url
        time.sleep(PAUSA)
        pedidos.append(url)
        r = RC.buscar_com_destino(url)
        cache[url] = r
        if r[1]:
            nome = hashlib.sha256(url.encode()).hexdigest()[:16] + ".html"
            (pasta / nome).write_bytes(r[1])
            lidas.append({"URL": url, "HTTP": r[0], "FICHEIRO": nome, "SHA256": hashlib.sha256(r[1]).hexdigest(),
                          "BYTES": len(r[1])})
        return r

    # 1. robots (pedido 1)
    st, txt, _, _ = buscar(NOVO + "/robots.txt")
    rp = urllib.robotparser.RobotFileParser()
    rp.parse((txt.decode("utf-8", "replace") if st == 200 else "").splitlines())
    robots = {"HTTP": st, "TEXTO": (txt or b"").decode("utf-8", "replace")[:2000]}

    def robots_de(host):
        return rp, robots["TEXTO"]

    # 2. a casa (pedido 2): onde estao as edicoes?
    if not GATE.permitido(NOVO + "/", rp):
        raise SystemExit("robots proibe a casa")
    st, casa, _, _ = buscar(NOVO + "/")
    html = (casa or b"").decode("utf-8", "replace")
    links = sorted(set(re.findall(r'href="(%s/[^"#]*)"' % re.escape(NOVO), html)))
    edicoes = [u for u in links if EDICAO.search(u)]
    categorias = [u for u in links if "/category/" in u]
    # rodada 1 escolheu /category/bandi-e-avvisi-di-gara-arssa/ porque «avvis» casava: sao concursos, nao boletins.
    # So conta categoria com a palavra do boletim; senao, a casa, se ela propria listar 2+ edicoes.
    candidatas = [u for u in categorias if re.search(r"bollettin|agrometeo|fitosanit", u, re.I)]
    entrada = candidatas[0] if candidatas else (NOVO + "/" if len(edicoes) >= 2 else None)
    out = {"DATASET": "ARSAC-PROPOSTA-V1", "SOURCE_ID": SID, "EM": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "ROBOTS": robots, "EDICOES_NA_CASA": edicoes, "CATEGORIAS_NA_CASA": categorias,
           "ENTRADA_ESCOLHIDA": entrada}
    if entrada:
        contratos = {c["SOURCE_ID"]: c for c in
                     json.loads((VIVO / "italy_contracts_curator.json").read_text(encoding="utf-8"))["FONTES"]}
        base = json.loads(json.dumps(contratos[SID]))
        base["ACQUISITION"]["INDEX_URL"] = entrada            # o reparo le a entrada nova; o livro nao muda aqui
        RC._ROBOTS.clear()
        p = RC.inferir(base, outros={}, buscar=buscar, robots_de=robots_de, permitido=GATE.permitido, pausa=PAUSA)
        out["REPARO"] = {k: p.get(k) for k in ("DESFECHO", "MOTIVO", "PORQUE", "INDEX_URL", "LINK_PATTERN",
                                                "COMO", "ITEM_LIDO")}
        if p["DESFECHO"] == "PADRAO_NOVO":
            p["ACQUISITION_ANTERIOR"] = contratos[SID]["ACQUISITION"]
            novo = RC.aplicar(contratos[SID], p)
            velho = CAN.buscar
            CAN.buscar = lambda u: (lambda r: (r[0], r[1], r[2]))(buscar(u))
            try:
                r = CAN.canario_html(novo)
            finally:
                CAN.buscar = velho
            out["CANARIO"] = {k: r.get(k) for k in ("PASS", "CLASSE", "PORQUE", "ALVO", "DETAIL_GATE_PASSED")}
            out["CONTRATO_PROPOSTO"] = novo
    vigia()
    out.update({"VIGIAS": vigias, "PEDIDOS": pedidos, "N_PEDIDOS": len(pedidos),
                "BYTES_FORA_DO_GIT": {"PASTA": str(pasta), "FICHEIROS": lidas}})
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out.get(k) for k in ("ENTRADA_ESCOLHIDA", "N_PEDIDOS", "VIGIAS")}, ensure_ascii=False))
    print("EDICOES", edicoes[:5], "CATEGORIAS", categorias[:10])
    print("REPARO", json.dumps(out.get("REPARO"), ensure_ascii=False)[:600])
    print("CANARIO", out.get("CANARIO"))


if __name__ == "__main__":
    main()
