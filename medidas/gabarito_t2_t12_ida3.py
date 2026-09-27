#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GABARITO T2/T12 — 3.a IDA: entrar pela SECCAO, nao pela homepage.

    UM SITE PUBLICO FALA PRIMEIRO DE SI, E SO DEPOIS DO ASSUNTO. (§168-17)

A REGRA, ESCRITA E COMMITADA ANTES DE QUALQUER PEDIDO — sem olhar o texto:

  1. ENTRADA. Um anfitriao, uma entrada:
     a. se a fonte tem ROUTE_PROVEN em curadoria/ROTAS-ELEGIVEIS-V1.json, a
        entrada e o INDEX_URL da rota e os itens saem pelo MOTOR do coletor
        (ligacoesDoIndice com o LINK_PATTERN do contrato);
     b. senao, a entrada e uma SECCAO achada nos HTML ja guardados (V1+V2)
        desse anfitriao — nunca adivinhada. Seccao = caminho que acaba em
        bollettini/bollettino > archivio-news > notizie > news >
        comunicati(-stampa) > primo-piano > avvisi (por esta prioridade);
        empate: URL mais curto, depois ordem alfabetica.
     Sem (a) nem (b): o site fica de fora, e fica dito.
  2. ITENS (so em b). Os primeiros 3 links do mesmo anfitriao que estao
     DEBAIXO do caminho da seccao (fora de navegacao e estaticos); se nao ha
     nenhum debaixo, os primeiros 3 pelo seletor generico da 2.a ida.
  3. PEDIDOS. robots + seccao + ate 3 itens = 5 por site. Egresso medido
     antes de cada site; se nao for IT, PARA tudo.
  4. DEDUPLICACAO contra V1+V2 por URL e por sha256 do texto extraido, ANTES
     de contar.

Bytes fora do Git (~/sintonia-gabarito/GABARITO-T2-T12-V3); registo em
curadoria/GABARITO-T2-T12-V3.json. Nada toca a Sala, o livro nem a porta.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "medidas"))
import gabarito_t2_t12 as G2                 # noqa: E402  (egresso, seletor, texto)
import canario_rotas_elegiveis as ROTAS      # noqa: E402  (motor do coletor)

CAN, GATE = G2.CAN, G2.GATE
PASTA = Path.home() / "sintonia-gabarito" / "GABARITO-T2-T12-V3"
SAIDA = RAIZ / "curadoria" / "GABARITO-T2-T12-V3.json"
V1 = RAIZ / "curadoria" / "GABARITO-T2-T12-V1.json"
V2 = RAIZ / "curadoria" / "GABARITO-T2-T12-V2.json"
PROVAS = RAIZ / "curadoria" / "ROTAS-ELEGIVEIS-V1.json"
MAX_ITENS = 3
PAUSA_S = 1.0

PRIORIDADE = ["bollettini", "bollettino", "archivio-news", "notizie", "news",
              "comunicati-stampa", "comunicati", "primo-piano", "avvisi"]
_SEC = re.compile(r"/(%s)/?$" % "|".join(PRIORIDADE), re.I)


def _host(u: str) -> str:
    return (urlparse(u).hostname or "").replace("www.", "")


def seccoes_guardadas(v2: dict) -> dict:
    """{SOURCE_ID: [urls de seccao]} lidos SO dos bytes ja guardados."""
    por = {}
    for i in v2["ITENS"]:
        f = Path(i["FICHEIRO_FORA_DO_GIT"])
        b = f.read_bytes() if f.exists() else b""
        if not b or b[:5] == b"%PDF-":
            continue
        h = _host(i["ENTRADA"])
        for m in re.finditer(rb"<a\s[^>]*?href\s*=\s*[\"']([^\"'#]+)[\"']", b, re.I):
            u = urljoin(i["URL"], m.group(1).decode("utf-8", "replace").strip()).split("?")[0]
            if _host(u) == h and _SEC.search(urlparse(u).path):
                por.setdefault(i["SOURCE_ID"], set()).add(u)
    return por


def escolher_seccao(urls) -> str | None:
    def chave(u):
        nome = _SEC.search(urlparse(u).path).group(1).lower()
        return (PRIORIDADE.index(nome), len(u), u)
    return min(urls, key=chave) if urls else None


def itens_da_seccao(html: bytes, seccao: str, n: int = MAX_ITENS) -> tuple[list, str]:
    raiz = urlparse(seccao).path.rstrip("/") + "/"
    todos = G2.itens_da_entrada(html, seccao, 200)
    debaixo = [u for u in todos if urlparse(u).path.startswith(raiz)]
    if debaixo:
        return debaixo[:n], "DEBAIXO_DA_SECCAO"
    return todos[:n], "SELETOR_GENERICO"


def plano() -> list[dict]:
    v2 = json.loads(V2.read_text(encoding="utf-8"))
    rotas = {l["SOURCE_ID"]: l for l in json.loads(PROVAS.read_text(encoding="utf-8"))["LINHAS"]
             if l.get("VEREDITO") == "ROUTE_PROVEN"}
    secs = seccoes_guardadas(v2)
    fora, vistos = [], set()
    for sid, uni, papel, entrada in G2.SITES:
        host = _host(entrada)
        if sid in rotas:
            p = {"SOURCE_ID": sid, "UNI": uni, "PAPEL": papel, "MODO": "ROTA_PROVADA",
                 "ENTRADA": rotas[sid]["INDEX_URL"], "CONTRATO_DE": rotas[sid]["CONTRATO_LIDO_DE"]}
        elif secs.get(sid):
            p = {"SOURCE_ID": sid, "UNI": uni, "PAPEL": papel, "MODO": "SECCAO_GUARDADA",
                 "ENTRADA": escolher_seccao(secs[sid])}
        else:
            p = {"SOURCE_ID": sid, "UNI": uni, "PAPEL": papel, "MODO": "FORA",
                 "ENTRADA": None, "PORQUE": "sem rota provada e sem seccao nos bytes guardados"}
        if p["ENTRADA"] and host in vistos:
            p.update(MODO="FORA", PORQUE="anfitriao ja coberto por outra linha", ENTRADA=None)
        if p["ENTRADA"]:
            vistos.add(host)
        fora.append(p)
    # as fontes com rota provada que nao estao na lista de sites da 2.a ida
    for sid, l in rotas.items():
        if sid.startswith(("IT-T2-", "IT-T12-")) and sid not in {p["SOURCE_ID"] for p in fora}:
            h = _host(l["INDEX_URL"])
            if any(p["MODO"] == "ROTA_PROVADA" and _host(p["ENTRADA"]) == h for p in fora):
                fora.append({"SOURCE_ID": sid, "UNI": sid.split("-")[1], "PAPEL": "CANDIDATO",
                             "MODO": "FORA", "ENTRADA": None,
                             "PORQUE": "anfitriao ja coberto por outra rota provada"})
                continue
            if h in vistos:
                for p in fora:          # a rota provada vence a seccao no mesmo anfitriao
                    if p["ENTRADA"] and _host(p["ENTRADA"]) == h:
                        p.update(MODO="FORA", PORQUE="anfitriao coberto pela rota provada de %s" % sid,
                                 ENTRADA=None)
            vistos.add(h)
            fora.append({"SOURCE_ID": sid, "UNI": sid.split("-")[1], "PAPEL": "CANDIDATO",
                         "MODO": "ROTA_PROVADA", "ENTRADA": l["INDEX_URL"],
                         "CONTRATO_DE": l["CONTRATO_LIDO_DE"]})
    return fora


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    pl = plano()
    if "--plano" in argv:
        for p in pl:
            print("%-11s %-15s %s" % (p["SOURCE_ID"], p["MODO"], p.get("ENTRADA") or p.get("PORQUE")))
        return 0
    PASTA.mkdir(parents=True, exist_ok=True)
    ja_url, ja_txt = set(), set()
    for f in (V1, V2):
        for i in json.loads(f.read_text(encoding="utf-8"))["ITENS"]:
            ja_url.add(i["URL"])
            if i.get("TEXTO_SHA256"):
                ja_txt.add(i["TEXTO_SHA256"])
    contratos = {}
    sites, itens = [], []
    for p in pl:
        if not p["ENTRADA"]:
            sites.append(dict(p, PEDIDOS=0))
            continue
        eg = G2.egresso()
        reg = dict(p, EGRESSO=eg, PEDIDOS=0)
        sites.append(reg)
        if eg.get("COUNTRY") != "IT":
            reg["PARADO"] = "EGRESSO_NAO_IT — recolha interrompida"
            print("PARAGEM: egresso %s" % eg, flush=True)
            break
        rp, txt = GATE.robots_de(urlparse(p["ENTRADA"]).hostname)
        reg["PEDIDOS"] += 1
        if "inacessivel" in txt or not GATE.permitido(p["ENTRADA"], rp):
            reg["PARADO"] = "robots: " + txt[:100]
            continue
        time.sleep(PAUSA_S)
        st, corpo, err = CAN.buscar(p["ENTRADA"])
        reg["PEDIDOS"] += 1
        if st != 200:
            reg["PARADO"] = "entrada HTTP %s %s" % (st, err)
            continue
        if p["MODO"] == "ROTA_PROVADA":
            ref = p["CONTRATO_DE"].split(":")[0]
            if ref not in contratos:
                contratos[ref] = ROTAS._contratos_de(ref)
            aq = contratos[ref][p["SOURCE_ID"]]["ACQUISITION"]
            alvos, como = ROTAS.ligacoes_pelo_motor(corpo, aq)[:MAX_ITENS], "MOTOR_DO_COLETOR"
        else:
            alvos, como = itens_da_seccao(corpo, p["ENTRADA"])
        reg["ESCOLHA"] = como
        for alvo in alvos:
            if alvo in ja_url:
                reg.setdefault("RECUSAS", []).append("ja visto em V1/V2 (URL): " + alvo)
                continue
            if not GATE.permitido(alvo, rp):
                reg.setdefault("RECUSAS", []).append("robots proibe " + alvo)
                continue
            time.sleep(PAUSA_S)
            st, b, err = CAN.buscar(alvo)
            reg["PEDIDOS"] += 1
            if st != 200 or not (b[:5] == b"%PDF-" or b.lstrip()[:1] == b"<"):
                reg.setdefault("RECUSAS", []).append("HTTP %s / nao HTML-PDF: %s" % (st, alvo))
                continue
            sha = hashlib.sha256(b).hexdigest()
            ext = ".pdf" if b[:5] == b"%PDF-" else ".html"
            (PASTA / (sha[:16] + ext)).write_bytes(b)
            texto, estado = G2.texto_de(b, alvo)
            tsha = hashlib.sha256(" ".join(texto.split()).encode()).hexdigest()
            itens.append({"ITEM_ID": "G3-%s" % sha[:12], "SOURCE_ID": p["SOURCE_ID"],
                          "UNIVERSO_DECLARADO": p["UNI"], "PAPEL": p["PAPEL"], "MODO": p["MODO"],
                          "URL": alvo, "ENTRADA": p["ENTRADA"], "HTTP": st, "BYTES": len(b),
                          "SHA256": sha, "FICHEIRO_FORA_DO_GIT": str(PASTA / (sha[:16] + ext)),
                          "EXTRACAO": estado, "EGRESSO": eg, "TEXTO_SHA256": tsha,
                          "DUPLICADO_DE_V1_V2": tsha in ja_txt,
                          "NON_WHITESPACE_CHARACTERS": len("".join(texto.split())),
                          "OBTIDO_EM": datetime.now(timezone.utc).isoformat()})
            print("%-11s %s" % (p["SOURCE_ID"], alvo[:100]), flush=True)
        time.sleep(PAUSA_S)
    d = {"DATASET": "GABARITO-T2-T12-V3", "ESTADO": "RECOLHIDO — por julgar",
         "AUTORIZACAO": "coordenacao, mandato continuo do dono (3.a ida)",
         "REGRA": "ver docstring de medidas/gabarito_t2_t12_ida3.py (commitada antes da corrida)",
         "BYTES_EM": str(PASTA), "SITES": sites, "ITENS": itens}
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
