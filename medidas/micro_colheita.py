#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MICRO-COLHEITA — a primeira ida a rede desta linha, medida pedido a pedido.

    PERIMETRO: so as fontes que `curadoria/collection_gate.py` declarar
    COLLECTION_ELIGIBLE NO INSTANTE DO PEDIDO. Nao ha lista de IDs aqui.

O QUE ESTE FICHEIRO E, E O QUE ELE NAO E
----------------------------------------
E um INSTRUMENTO DE MEDICAO: vai a fonte, conta o que veio e escreve um
recibo. NAO e um segundo coletor — nao escreve no livro de observacoes, nao
cunha RUN, nao cria `raw_asset`, nao admite nada e nao toca na Sala.

    MEDIR NAO E COLHER. Quem colhe para o acervo e a cadeia
    `coleta/italy_executor.py` -> `admissao/admissao.py` -> Sala.

⚠️ E PORQUE ELE NASCEU — O DESENCONTRO MEDIDO EM 2026-09-21
------------------------------------------------------------
O portao declarou 8 fontes COLLECTION_ELIGIBLE. Perguntado ao coletor de Node
na mesma arvore:

    CONTRACT_IDS = 14        PILOT_SOURCES = 7
    das 8 elegiveis, com contrato executavel: 0

A traducao dos contratos do curador (`curadoria/italy_contracts_curator.json`,
81 fontes, vocabulario MATCH/INDEX_URL/LINK_PATTERN) para a tabela do motor
vive NOUTRA BRANCH (`aquisicao-detalhe-v1`, `regras/italy_contracts_onboarded.json`).
Nesta, o coletor nao conhece nenhuma das 8.

    O PORTAO APROVA QUEM O COLETOR NAO SABE ABRIR.
    Isso e uma medicao, nao uma opiniao — e esta escrita no relatorio.

Enquanto essa traducao nao existir aqui, a unica coisa honesta e ir a fonte
pelo caminho que JA fala a lingua destes contratos, e dizer com todas as
letras ate onde se chegou.

DE QUEM E CADA REGRA QUE ESTE FICHEIRO USA
-------------------------------------------
Nenhuma e reescrita aqui. Todas sao perguntadas ao dono:

    quem pode ser colhido   curadoria/collection_gate.py   avaliar()
    o robots vivo           curadoria/gate_de_rota.py      robots_de()
    o leitor de rede        curadoria/canario.py           buscar()
    os links da entrada     curadoria/provar_listagem.py   _links_internos()
    capa ou materia         curadoria/retrato_html.py      retrato_do_html()
                                                           gate_capa_nao_e_materia()

Uso:
    py medidas/micro_colheita.py --run-id=<ID> --saida=<ficheiro.json>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import canario as CAN            # noqa: E402  o leitor de rede, com o UA medido
import capturador as CAP         # noqa: E402  o UA (dono unico)
import collection_gate as CG     # noqa: E402  QUEM PODE SER COLHIDO
import gate_de_rota as GR        # noqa: E402  o robots vivo
import provar_listagem as PL     # noqa: E402  os links internos da entrada
import retrato_html as RH        # noqa: E402  CAPA != MATERIA

CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"

# ── CADENCIA E TECTO ───────────────────────────────────────────────────────
# Nao sao numeros bonitos: sao o compromisso desta missao. MAX 8 fontes ja vem
# do portao; aqui limita-se o que se pede A CADA UMA.
PAUSA_POR_PEDIDO_S = 1.5
MAX_ITENS_POR_FONTE = 3
TIMEOUT_HERDADO = CAN.TIMEOUT


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def dominio(url: str) -> str:
    return urlparse(url).netloc.lower()


class Registo:
    """O livro de pedidos. Tudo o que sai para a rede passa por aqui.

    ⚠️ ISTO E A PROVA DO G-ELIG, e por isso nao se conta pela intencao: conta-se
    o que foi REALMENTE pedido, com o dominio ao lado. Uma fonte fora das
    elegiveis aparece aqui ou nao aconteceu.
    """

    def __init__(self) -> None:
        self.pedidos: list[dict] = []
        self._ultimo_por_dominio: dict[str, float] = {}
        self._robots: dict[str, tuple] = {}

    def _esperar(self, dom: str) -> None:
        anterior = self._ultimo_por_dominio.get(dom)
        if anterior is not None:
            falta = PAUSA_POR_PEDIDO_S - (time.monotonic() - anterior)
            if falta > 0:
                time.sleep(falta)
        self._ultimo_por_dominio[dom] = time.monotonic()

    def robots(self, host: str) -> tuple:
        """Um robots.txt por host, lido VIVO e uma vez por corrida."""
        if host not in self._robots:
            self._esperar(host)
            t0 = time.monotonic()
            rp, txt = GR.robots_de(host)
            self.pedidos.append({
                "QUANDO": agora(), "URL": "https://%s/robots.txt" % host,
                "DOMINIO": host, "TIPO": "ROBOTS", "HTTP": "NAO SEI",
                "BYTES": len(txt or ""), "MS": int((time.monotonic() - t0) * 1000),
                "SOURCE_ID": "-"})
            self._robots[host] = (rp, txt)
        return self._robots[host]

    def permitido(self, url: str) -> tuple[bool, str]:
        rp, txt = self.robots(dominio(url))
        return bool(rp.can_fetch(CAP.UA, url)), (txt or "")[:200]

    def buscar(self, url: str, source_id: str, tipo: str) -> tuple[int, bytes, str]:
        dom = dominio(url)
        self._esperar(dom)
        t0 = time.monotonic()
        st, b, err = CAN.buscar(url)
        self.pedidos.append({
            "QUANDO": agora(), "URL": url, "DOMINIO": dom, "TIPO": tipo,
            "HTTP": st, "BYTES": len(b), "MS": int((time.monotonic() - t0) * 1000),
            "SOURCE_ID": source_id, "ERRO": err or ""})
        return st, b, err


def contratos() -> dict:
    d = json.loads(CONTRATOS.read_text(encoding="utf-8"))
    return {c["SOURCE_ID"]: c for c in d["FONTES"]}


def enumerar(html: str, contrato: dict) -> list[str]:
    """Os itens que a ENTRADA anuncia — pelo padrao do contrato, nada mais.

    A resolucao de `href` para endereco absoluto e de `provar_listagem`, e o
    padrao vem do contrato com `MATCH: URL` — o padrao julga o ENDERECO INTEIRO,
    nao o pedaco de `href`. Sao duas convencoes diferentes na casa e confundi-las
    devolve zero itens com cara de «a fonte nao publicou nada».
    """
    aq = contrato["ACQUISITION"]
    rx = re.compile(aq["LINK_PATTERN"])
    entrada = aq["INDEX_URL"].rstrip("/")
    achados = []
    for u in PL._links_internos(html, aq["INDEX_URL"]):
        if not rx.match(u):
            continue
        if u.rstrip("/") == entrada:
            # ⚠️ O ALVO NAO PODE SER A PROPRIA ENTRADA — a mesma lei do canario.
            continue
        if u not in achados:
            achados.append(u)
    return achados


def colher_fonte(sid: str, contrato: dict, reg: Registo, max_itens: int) -> dict:
    aq = contrato.get("ACQUISITION") or {}
    linha = {
        "SOURCE_ID": sid, "INDEX_URL": aq.get("INDEX_URL", "NAO SEI"),
        "DOMINIO": dominio(aq.get("INDEX_URL", "")),
        "HTTP": None, "BYTES": 0, "ITENS_ENUMERADOS": 0, "ITENS_COLHIDOS": 0,
        "MAX_TARGETS_DO_CONTRATO": aq.get("MAX_TARGETS"),
        "ROBOTS_PERMITE_ENTRADA": None, "ROBOTS_BLOCKS": 0,
        "ITENS": [], "PORQUE": "",
    }
    if aq.get("STRATEGY") != "HTML_LINK_DISCOVERY":
        linha["PORQUE"] = ("ESTRATEGIA_NAO_COBERTA: %s — este instrumento so mede "
                           "HTML_LINK_DISCOVERY" % aq.get("STRATEGY"))
        return linha

    ok, _ = reg.permitido(aq["INDEX_URL"])
    linha["ROBOTS_PERMITE_ENTRADA"] = ok
    if not ok:
        linha["ROBOTS_BLOCKS"] += 1
        linha["PORQUE"] = "ROBOTS_BLOCKED: o robots.txt vivo nao permite a entrada"
        return linha

    st, b, err = reg.buscar(aq["INDEX_URL"], sid, "INDEX")
    linha["HTTP"], linha["BYTES"] = st, len(b)
    if st != 200 or not b:
        linha["PORQUE"] = "ENTRADA_INACESSIVEL: %s" % (err or "HTTP %s" % st)
        return linha

    alvos = enumerar(b.decode("utf-8", "replace"), contrato)
    linha["ITENS_ENUMERADOS"] = len(alvos)
    if not alvos:
        linha["PORQUE"] = ("EMPTY_LIST: a entrada abriu e nenhum endereco casa com o "
                           "padrao do contrato — nao e falha de rede")
        return linha

    tecto = min(max_itens, aq.get("MAX_TARGETS") or max_itens)
    for url in alvos[:tecto]:
        item = {"URL": url, "HTTP": None, "BYTES": 0, "MATERIA_REAL": False,
                "PORQUE": ""}
        ok_i, _ = reg.permitido(url)
        if not ok_i:
            linha["ROBOTS_BLOCKS"] += 1
            item["PORQUE"] = "ROBOTS_BLOCKED"
            linha["ITENS"].append(item)
            continue
        st2, b2, err2 = reg.buscar(url, sid, "ITEM")
        item["HTTP"], item["BYTES"] = st2, len(b2)
        if st2 != 200 or not b2:
            item["PORQUE"] = "ITEM_INACESSIVEL: %s" % (err2 or "HTTP %s" % st2)
            linha["ITENS"].append(item)
            continue
        # ⚠️ UM BOM UTF-8 A FRENTE DO «<» NAO E «NAO E HTML» — lei ja medida
        # no provador de listagens (CAND-0060).
        if b2.lstrip().removeprefix(b"\xef\xbb\xbf")[:1] != b"<":
            item["PORQUE"] = "BYTE_VALIDATION_FAILED: os bytes nao sao HTML"
            linha["ITENS"].append(item)
            continue
        linha["ITENS_COLHIDOS"] += 1
        ret = RH.retrato_do_html(b2)
        item.update({
            "HTML_KIND": ret["HTML_KIND"], "CAPA_OU_MATERIA": ret["CAPA_OU_MATERIA"],
            "LINKS": ret["LINKS"],
            "NON_WHITESPACE_CHARACTERS": ret["NON_WHITESPACE_CHARACTERS"],
            "PARAGRAPH_CHARACTERS": ret["PARAGRAPH_CHARACTERS"],
            "TEXT_SHA256": ret["TEXT_SHA256"],
            "URL_DIFERE_DO_INDICE": url.rstrip("/") != aq["INDEX_URL"].rstrip("/"),
            "DETAIL_GATE": RH.GATE_VERSAO,
        })
        if ret["HTML_KIND"] == "EMPTY":
            item["PORQUE"] = "ITEM_SEM_TEXTO: abriu e nao tem texto visivel"
        else:
            gate = RH.gate_capa_nao_e_materia(contrato, ret)
            if gate:
                item["PORQUE"] = gate
            else:
                item["MATERIA_REAL"] = True
                item["PORQUE"] = "MATERIA: item aberto, com corpo util, gate passou"
        linha["ITENS"].append(item)

    linha["PORQUE"] = "ENTRADA_ABERTA_E_ITENS_LIDOS"
    return linha


def correr(run_id: str, max_itens: int = MAX_ITENS_POR_FONTE) -> dict:
    # ⚠️ O PORTAO E PERGUNTADO AGORA, NAO LIDO DE UM JSON VELHO.
    ctx = CG._contexto()
    elegiveis = CG.elegiveis(ctx=ctx)
    contr = contratos()
    reg = Registo()
    linhas = []
    for sid in elegiveis:
        v = CG.avaliar(sid, **ctx)
        if not v["COLLECTION_ELIGIBLE"]:
            # cinto e suspensorios: a lista veio do portao e cada fonte e
            # reconfirmada ANTES do primeiro pedido dela.
            linhas.append({"SOURCE_ID": sid, "PORQUE": "BLOQUEADA_PELO_PORTAO",
                           "ITENS": []})
            continue
        c = contr.get(sid)
        if not c:
            linhas.append({"SOURCE_ID": sid, "ITENS": [], "ITENS_ENUMERADOS": 0,
                           "ITENS_COLHIDOS": 0,
                           "PORQUE": "SEM_CONTRATO_NO_CURADOR"})
            continue
        linhas.append(colher_fonte(sid, c, reg, max_itens))
    por_dominio: dict[str, int] = {}
    for p in reg.pedidos:
        por_dominio[p["DOMINIO"]] = por_dominio.get(p["DOMINIO"], 0) + 1
    return {
        "DATASET": "MICRO-COLLECTION-MEDIDA-V1",
        "RUN_ID": run_id,
        "QUANDO": agora(),
        "O_QUE_ISTO_E": ("medicao de ida a rede. NAO escreve no livro, NAO cunha "
                         "RUN, NAO cria raw_asset e NAO toca na Sala."),
        "COLLECTION_ELIGIBLE_MEDIDO": elegiveis,
        "FONTES_TENTADAS": [l["SOURCE_ID"] for l in linhas],
        "TOTAIS": {
            "FONTES": len(linhas),
            "ITENS_ENUMERADOS": sum(l.get("ITENS_ENUMERADOS", 0) for l in linhas),
            "ITENS_COLHIDOS": sum(l.get("ITENS_COLHIDOS", 0) for l in linhas),
            "MATERIA_REAL": sum(1 for l in linhas for i in l.get("ITENS", [])
                                if i.get("MATERIA_REAL")),
            "CAPAS": sum(1 for l in linhas for i in l.get("ITENS", [])
                         if str(i.get("PORQUE", "")).startswith("CAPA_NAO_E_MATERIA")),
            "PEDIDOS_TOTAL": len(reg.pedidos),
            "ROBOTS_BLOCKS": sum(l.get("ROBOTS_BLOCKS", 0) for l in linhas),
            "HTTP_429": sum(1 for p in reg.pedidos if p.get("HTTP") == 429),
            "HTTP_403": sum(1 for p in reg.pedidos if p.get("HTTP") == 403),
            "PAID_USD": 0.0,
        },
        "PEDIDOS_POR_DOMINIO": dict(sorted(por_dominio.items())),
        "PEDIDOS": reg.pedidos,
        "FONTES": linhas,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--max-itens", type=int, default=MAX_ITENS_POR_FONTE)
    a = ap.parse_args(argv)
    d = correr(a.run_id, a.max_itens)
    Path(a.saida).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                             encoding="utf-8")
    t = d["TOTAIS"]
    print("RUN_ID                 %s" % d["RUN_ID"])
    for k in ("FONTES", "ITENS_ENUMERADOS", "ITENS_COLHIDOS", "MATERIA_REAL",
              "CAPAS", "PEDIDOS_TOTAL", "ROBOTS_BLOCKS", "HTTP_429", "HTTP_403"):
        print("%-22s %s" % (k, t[k]))
    for l in d["FONTES"]:
        print("  %-12s HTTP=%-5s enum=%-3s colhidos=%-3s materia=%-3s %s"
              % (l["SOURCE_ID"], l.get("HTTP"), l.get("ITENS_ENUMERADOS", 0),
                 l.get("ITENS_COLHIDOS", 0),
                 sum(1 for i in l.get("ITENS", []) if i.get("MATERIA_REAL")),
                 l.get("PORQUE", "")[:60]))
    print("escrito: %s" % a.saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
