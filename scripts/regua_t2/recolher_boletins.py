#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T2-REGUA · ADENDA 2 — RECOLHA DE BOLETINS REAIS PARA O GABARITO (nao e coleta).

    py scripts/regua_t2/recolher_boletins.py

Regra (commitada antes da corrida, PROTOCOLO-GABARITO-T2.md#adenda-2):
  * egresso pelo DONO (superficie/rede.py, consenso) antes de CADA site; nao-PASS PARA tudo;
  * robots.txt pelo leitor da casa; teto de 6 pedidos por anfitriao; 2 s de pausa;
  * alvo escolhido por regra fixa (endereco ou texto do link com bollettin/notiziario/
    agrometeo/fitosanitar/difesa, ou .pdf), pela ordem da pagina, ate 3; um nivel a mais
    se o alvo for um indice;
  * bytes fora do Git, sha256 no manifesto. Nada toca a Sala, o livro nem a porta.
"""
from __future__ import annotations

import hashlib
import html
import importlib.util
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

RAIZ = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RAIZ), str(RAIZ / "curadoria")]
import _gavetas  # noqa: E402,F401
import canario as CAN  # noqa: E402
import gate_de_rota as GATE  # noqa: E402

_sp = importlib.util.spec_from_file_location("rede", RAIZ / "superficie" / "rede.py")
REDE = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(REDE)
_sp = importlib.util.spec_from_file_location("inv", Path(__file__).parent / "inventariar_t2.py")
INV = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(INV)

PASTA = Path.home() / "sintonia-gabarito" / "REGUA-T2-V1" / "recolha"
SAIDA = Path(__file__).parent / "RECOLHA-BOLETINS-V1.json"
TETO = 6
PAUSA_S = 2.0
MAX_ALVOS = 3

# (SOURCE_ID ou NAO_CATALOGADO, servico/regiao, entrada, de onde vem o endereco)
SITES = [
    ("IT-T2-001", "ARPAE Emilia-Romagna · agrometeo",
     "https://www.arpae.it/it/temi-ambientali/meteo/report-meteo/bollettini-e-rapporti-agrometeo/bollettini-agrometeo/bollettini-2026",
     "contrato regras/italy_contracts.mjs"),
    ("IT-T2-002", "ARPAV Veneto · Agrometeo Informa",
     "https://www.arpa.veneto.it/dati-ambientali/bollettini/agrometeo/agrometeoinforma",
     "contrato regras/italy_contracts.mjs"),
    ("IT-T3-002", "Campania · Servizio Fitosanitario Regionale",
     "https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026.html",
     "contrato regras/italy_contracts.mjs"),
    ("IT-T3-008", "Puglia · agrometeo regionale",
     "https://www.agrometeopuglia.it/bollettini", "contrato regras/italy_contracts.mjs"),
    ("IT-T3-010", "Puglia · APOL mosca delle olive", "http://www.apol.it",
     "contrato regras/italy_contracts.mjs"),
    ("IT-T3-022", "Lombardia · Servizio Fitosanitario",
     "https://www.fitosanitario.regione.lombardia.it/", "catalogo curadoria"),
    ("IT-T2-004", "Sicilia · SIAS agrometeo", "http://www.sias.regione.sicilia.it/",
     "pagina inicial do anfitriao do contrato"),
    ("IT-T12-009", "Marche · ASSAM (servizio agrometeo)", "https://www.assam.marche.it/",
     "catalogo curadoria"),
    ("IT-T12-017", "Friuli Venezia Giulia · ERSA", "https://www.ersa.fvg.it/",
     "catalogo curadoria"),
    ("NAO_CATALOGADO", "Toscana · LaMMA", "https://www.lamma.toscana.it/", "pagina inicial"),
    ("NAO_CATALOGADO", "Lazio · ARSIAL", "https://www.arsial.it/", "pagina inicial"),
    ("NAO_CATALOGADO", "Basilicata · ALSIA", "https://www.alsia.it/", "pagina inicial"),
    ("NAO_CATALOGADO", "Liguria · Agriligurianet", "https://www.agriligurianet.it/",
     "pagina inicial"),
    ("NAO_CATALOGADO", "Trentino · Fondazione Edmund Mach", "https://www.fmach.it/",
     "pagina inicial"),
    ("IT-T2-035", "Sardegna · ARPAS", "https://www.arpa.sardegna.it/", "catalogo curadoria"),
]

# 2.a ida (Adenda 2): paginas-indice de boletins ENCONTRADAS na 1.a ida (de onde vieram).
SITES_IDA2 = [
    ("IT-T2-001", "ARPAE · bollettino agrofenologico",
     "https://www.arpae.it/it/temi-ambientali/meteo/report-meteo/bollettini-e-rapporti-agrometeo/bollettino-agrofenologico",
     "link em .../bollettini-e-rapporti-agrometeo (1.a ida)"),
    ("IT-T3-002", "Campania · SFR bollettini 2026",
     "https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026.html",
     "entrada do contrato; na 1.a ida a regra pegou a navegacao antes dos PDF"),
    ("IT-T3-008", "Puglia · agrometeo bollettini", "https://www.agrometeopuglia.it/bollettini",
     "entrada do contrato; idem"),
    ("NAO_CATALOGADO", "Liguria · bollettino di olivicoltura",
     "https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/agrometeo-caar/bollettino-di-olivicoltura.html",
     "link em agrometeo-caar.html (1.a ida)"),
    ("NAO_CATALOGADO", "Liguria · bollettino di viticoltura",
     "https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/agrometeo-caar/bollettino-di-viticoltura.html",
     "link em agrometeo-caar.html (1.a ida)"),
    ("NAO_CATALOGADO", "Trentino · FEM bollettini tecnici", "https://www.fmach.it/Servizi/Bollettini-tecnici",
     "link na pagina inicial da FEM (1.a ida)"),
    ("IT-T3-010", "Puglia · APOL bollettini 2026",
     "http://www.apol.it/press/item/bollettini-fitosanitari-mosca-dell-olivo-2026", "1.a ida"),
]

# 3.a ida (Adenda 2): PDFs pelas ROUTE_TEMPLATE dos contratos; datas pela frequencia declarada.
_CAMP = "https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/pdf/%s.pdf"
_ARIF = ("https://www.agrometeopuglia.it/bollettino-elettronico/settimanale/2026/"
         "Notiziario_Agrometeorologico_N%s_%s.pdf")
_ARPAE = ("https://www.arpae.it/it/temi-ambientali/meteo/report-meteo/bollettini-e-rapporti-agrometeo/"
          "bollettini-agrometeo/bollettini-2026/%s_boll_agro_%s.pdf")
_ARPAV = "https://www.arpa.veneto.it/risorse/data-agrometeo/agrometeo/32zone/agro_%s.pdf"
PDFS_IDA3 = [
    ("IT-T2-001", "ARPAE · bollettino agrometeo", [_ARPAE % ("36", "20260907"), _ARPAE % ("38", "20260921")]),
    ("IT-T3-008", "Puglia · notiziario agrometeorologico e fitosanitario",
     [_ARIF % ("37", "09-09-2026"), _ARIF % ("38", "16-09-2026"), _ARIF % ("39", "23-09-2026")]),
    ("IT-T3-002", "Campania · SFR bollettini per provincia",
     [_CAMP % x for x in ("NA-16-09", "AV-16-09", "CE-23-09", "BN-23-09", "SA-23-09")]),
    ("IT-T2-002", "ARPAV · Agrometeo Informa por zona", [_ARPAV % z for z in ("05", "12", "20", "28")]),
]

REGRA = re.compile(r"bollettin|notiziario|agrometeo|fitosanitar|difesa", re.I)
_NAV = re.compile(r"privacy|cookie|contatt|accessibil|login|facebook|twitter|instagram|"
                  r"youtube|linkedin|mailto:|javascript:|#", re.I)
_A = re.compile(rb"<a\s[^>]*?href\s*=\s*[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", re.I | re.S)


def alvos_da_pagina(corpo: bytes, base: str, n: int) -> list[str]:
    host = (urlparse(base).hostname or "").replace("www.", "")
    fora, vistos = [], set()
    for m in _A.finditer(corpo):
        try:
            u = urljoin(base, html.unescape(m.group(1).decode("utf-8", "replace")).strip())
        except ValueError:
            continue
        txt = re.sub(r"<[^>]+>", " ", m.group(2).decode("utf-8", "replace"))
        p = urlparse(u)
        if p.scheme not in ("http", "https") or (p.hostname or "").replace("www.", "") != host:
            continue
        if u in vistos or u.rstrip("/") == base.rstrip("/") or _NAV.search(u):
            continue
        if REGRA.search(u) or REGRA.search(txt) or p.path.lower().endswith(".pdf"):
            vistos.add(u)
            fora.append(u)
    if PDF_PRIMEIRO:
        fora = [u for u in fora if urlparse(u).path.lower().endswith(".pdf")] +                [u for u in fora if not urlparse(u).path.lower().endswith(".pdf")]
    return fora[:n]


PDF_PRIMEIRO = False


def ida3() -> int:
    """So os PDFs das rotas dos contratos; `%PDF` obrigatorio."""
    saida = Path(__file__).parent / "RECOLHA-BOLETINS-V3.json"
    PASTA.mkdir(parents=True, exist_ok=True)
    sites, itens = [], []
    for sid, nome, urls in PDFS_IDA3:
        eg = REDE.portao_de_egresso("IT")
        reg = {"SOURCE_ID": sid, "SERVICO": nome, "ROTA": "ROUTE_TEMPLATE do contrato",
               "EGRESSO": {"GATE": eg["EGRESS_GATE"], "VOTOS": [(v["VERIFICADOR"], v["PAIS"]) for v in eg["VOTOS"]]},
               "PEDIDOS": 0}
        sites.append(reg)
        if eg["EGRESS_GATE"] != "PASS":
            reg["PARADO"] = "EGRESSO NAO PASS — recolha interrompida"
            break
        rp, txt = GATE.robots_de(urlparse(urls[0]).hostname)
        reg["PEDIDOS"] += 1
        if "inacessivel" in txt:
            reg["PARADO"] = "robots: " + txt[:100]
            continue
        for u in urls:
            if reg["PEDIDOS"] >= TETO:
                break
            if not GATE.permitido(u, rp):
                reg.setdefault("RECUSAS", []).append("robots proibe " + u)
                continue
            time.sleep(PAUSA_S)
            st, c, err = CAN.buscar(u)
            reg["PEDIDOS"] += 1
            if st != 200 or c[:5] != b"%PDF-":
                reg.setdefault("RECUSAS", []).append("HTTP %s %s %s" % (st, "sem %PDF" if st == 200 else err, u))
                print("%-15s %s %s" % (nome[:15], st, u[-60:]), flush=True)
                continue
            sha = hashlib.sha256(c).hexdigest()
            f = PASTA / (sha[:16] + ".pdf")
            f.write_bytes(c)
            texto, estado = INV.extrair(c)
            norm = INV.normalizar(texto)
            itens.append({"SOURCE_ID": sid, "SERVICO": nome, "URL": u, "HTTP": st, "BYTES": len(c),
                          "SHA256": sha, "FICHEIRO_FORA_DO_GIT": str(f), "EXTRACAO": estado,
                          "TEXTO_SHA256": hashlib.sha256(norm.encode("utf-8")).hexdigest(),
                          "NON_WHITESPACE_CHARACTERS": len(norm.replace(" ", "")),
                          "OBTIDO_EM": datetime.now(timezone.utc).isoformat()})
            print("%-15s PDF %d B %s" % (nome[:15], len(c), u[-60:]), flush=True)
    out = {"DATASET": "RECOLHA-BOLETINS-V3", "PROTOCOLO": "PROTOCOLO-GABARITO-T2.md#adenda-2 (3.a ida)",
           "BYTES_EM": str(PASTA), "SITES": sites, "ITENS": itens,
           "CONTAGEM": {"ITENS": len(itens), "TEXTOS_DISTINTOS": len({i["TEXTO_SHA256"] for i in itens}),
                        "PEDIDOS": sum(s["PEDIDOS"] for s in sites)}}
    saida.write_text(json.dumps(out, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8", newline=chr(10))
    print(json.dumps(out["CONTAGEM"]))
    return 0


def main() -> int:
    global PDF_PRIMEIRO, SAIDA
    if "--ida=3" in sys.argv:
        return ida3()
    ida2 = "--ida=2" in sys.argv
    if ida2:
        PDF_PRIMEIRO = True
        SAIDA = Path(__file__).parent / "RECOLHA-BOLETINS-V2.json"
    PASTA.mkdir(parents=True, exist_ok=True)
    sites, itens = [], []
    for sid, nome, entrada, origem in (SITES_IDA2 if ida2 else SITES):
        eg = REDE.portao_de_egresso("IT")
        reg = {"SOURCE_ID": sid, "SERVICO": nome, "ENTRADA": entrada, "ORIGEM_DO_ENDERECO": origem,
               "EGRESSO": {"GATE": eg["EGRESS_GATE"], "VOTOS": [(v["VERIFICADOR"], v["PAIS"]) for v in eg["VOTOS"]],
                           "DA_CACHE": eg.get("DA_CACHE")}, "PEDIDOS": 0}
        sites.append(reg)
        if eg["EGRESS_GATE"] != "PASS":
            reg["PARADO"] = "EGRESSO NAO PASS — recolha interrompida"
            print("PARAGEM egresso", reg["EGRESSO"], flush=True)
            break
        host = urlparse(entrada).hostname
        rp, txt = GATE.robots_de(host)
        reg["PEDIDOS"] += 1
        if "inacessivel" in txt or not GATE.permitido(entrada, rp):
            reg["PARADO"] = "robots: " + txt[:100]
            print("%-15s robots %s" % (nome[:15], txt[:60]), flush=True)
            continue
        time.sleep(PAUSA_S)
        st, corpo, err = CAN.buscar(entrada)
        reg["PEDIDOS"] += 1
        if st != 200:
            reg["PARADO"] = "entrada HTTP %s %s" % (st, err)
            print("%-15s entrada %s %s" % (nome[:15], st, err[:40]), flush=True)
            continue
        fila = alvos_da_pagina(corpo, entrada, MAX_ALVOS)
        seguiu = False
        if not fila:
            reg["PARADO"] = "nenhum link pela regra na entrada"
        while fila and reg["PEDIDOS"] < TETO:
            alvo = fila.pop(0)
            if not GATE.permitido(alvo, rp):
                reg.setdefault("RECUSAS", []).append("robots proibe " + alvo)
                continue
            time.sleep(PAUSA_S)
            st, c, err = CAN.buscar(alvo)
            reg["PEDIDOS"] += 1
            if st != 200 or not c:
                reg.setdefault("RECUSAS", []).append("HTTP %s %s" % (st, alvo))
                continue
            e_pdf = c[:5] == b"%PDF-"
            if not e_pdf and c.lstrip()[:1] != b"<":
                reg.setdefault("RECUSAS", []).append("nao e HTML nem PDF: " + alvo)
                continue
            sha = hashlib.sha256(c).hexdigest()
            f = PASTA / (sha[:16] + (".pdf" if e_pdf else ".html"))
            f.write_bytes(c)
            texto, estado = INV.extrair(c)
            norm = INV.normalizar(texto)
            itens.append({"SOURCE_ID": sid, "SERVICO": nome, "URL": alvo, "ENTRADA": entrada,
                          "HTTP": st, "BYTES": len(c), "SHA256": sha, "FICHEIRO_FORA_DO_GIT": str(f),
                          "EXTRACAO": estado,
                          "TEXTO_SHA256": hashlib.sha256(norm.encode("utf-8")).hexdigest(),
                          "NON_WHITESPACE_CHARACTERS": len(norm.replace(" ", "")),
                          "OBTIDO_EM": datetime.now(timezone.utc).isoformat()})
            print("%-15s %s %d B %s" % (nome[:15], "PDF " if e_pdf else "HTML", len(c), alvo[-70:]), flush=True)
            # um nivel a mais: o alvo era um indice de boletins
            if not e_pdf and not seguiu:
                mais = [u for u in alvos_da_pagina(c, alvo, MAX_ALVOS) if u != entrada]
                if mais:
                    seguiu = True
                    fila = mais[:max(0, TETO - reg["PEDIDOS"])] + fila
        time.sleep(PAUSA_S)
    out = {"DATASET": SAIDA.stem, "PROTOCOLO": "PROTOCOLO-GABARITO-T2.md#adenda-2",
           "REGRA": "egresso por consenso antes de cada site; robots; teto %d/anfitriao; %.0f s; alvos por regra fixa" % (TETO, PAUSA_S),
           "BYTES_EM": str(PASTA), "SITES": sites, "ITENS": itens,
           "CONTAGEM": {"SITES": len(sites), "ITENS": len(itens),
                        "TEXTOS_DISTINTOS": len({i["TEXTO_SHA256"] for i in itens}),
                        "PEDIDOS": sum(s["PEDIDOS"] for s in sites)}}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(out["CONTAGEM"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
