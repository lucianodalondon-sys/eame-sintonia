#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GABARITO T2/T12 — recolha de EXEMPLOS, nao coleta (D4, 2026-09-23).

    SEM GABARITO NAO HA REGUA. E O GABARITO VEM ANTES DA REGUA.

Por site: robots (1) + pagina de entrada (1) + UMA materia (1) = 3 pedidos,
todos contados, 1 s de pausa. Egresso medido (ipinfo.io) antes de CADA site:
se nao for IT, PARA a recolha inteira.

A materia e escolhida por REGRA FIXA, nunca pelo conteudo: o primeiro link do
mesmo anfitriao cujo ultimo troco tem 3+ palavras com hifen, ou um ano, ou um
numero de 3+ algarismos, fora da navegacao (privacy, contatti, login...).
Escolher pelo texto seria escolher o gabarito a favor da regua.

Os bytes vao para `data/samples/GABARITO-T2-T12/` com sha256; a proveniencia
para `GABARITO-T2-T12-V1.json`. Nada toca a Sala, o livro nem a porta.
O julgamento a mao e feito DEPOIS, noutro passo, sobre o texto extraido.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "curadoria"))
import _gavetas  # noqa: E402,F401
import canario as CAN                       # noqa: E402
import gate_de_rota as GATE                 # noqa: E402
from coleta import executor_texto_de_html as HTMLX  # noqa: E402
from coleta import executor_texto_de_pdf as PDFX    # noqa: E402

PASTA = RAIZ / "data" / "samples" / "GABARITO-T2-T12"
SAIDA = PASTA / "GABARITO-T2-T12-V1.json"
PAUSA_S = 1.0

# (SOURCE_ID, universo declarado, papel, entrada). Uma linha por ANFITRIAO:
# o teto de 3 pedidos e por site, e dois SOURCE_ID no mesmo site partilhariam-no.
SITES = [
    # T2 · clima / agua / solo
    ("IT-T2-051", "T2", "CANDIDATO", "https://www.arpae.it/it"),
    ("IT-T2-002", "T2", "CANDIDATO", "https://www.arpa.veneto.it/"),
    ("IT-T2-004", "T2", "CANDIDATO", "http://www.sias.regione.sicilia.it"),
    ("IT-T2-006", "T2", "CANDIDATO", "https://www.arpacampania.it/"),
    ("IT-T2-007", "T2", "CANDIDATO", "https://www.arpa.sicilia.it/"),
    ("IT-T2-008", "T2", "CANDIDATO", "https://www.arpat.toscana.it/"),
    ("IT-T2-009", "T2", "CANDIDATO", "https://www.isprambiente.gov.it/it"),
    ("IT-T2-010", "T2", "CANDIDATO", "https://appa.provincia.tn.it/"),
    ("IT-T2-011", "T2", "CANDIDATO", "https://www.arpalombardia.it/"),
    ("IT-T2-012", "T2", "CANDIDATO", "https://www.arpa.fvg.it/"),
    ("IT-T2-013", "T2", "CANDIDATO", "https://www.arpalazio.it/"),
    ("IT-T2-014", "T2", "CANDIDATO", "https://www.arpamolise.it/"),
    ("IT-T2-015", "T2", "CANDIDATO", "https://www.agrometeorologia.it/"),
    ("IT-T2-016", "T2", "CANDIDATO", "https://www.arpa.marche.it/"),
    ("IT-T2-017", "T2", "CANDIDATO", "https://www.iret.cnr.it/"),
    ("IT-T2-018", "T2", "CANDIDATO", "https://www.isafom.cnr.it/"),
    ("IT-T2-019", "T2", "CANDIDATO", "https://www.arpa.piemonte.it/home"),
    ("IT-T2-020", "T2", "CANDIDATO", "https://www.artaabruzzo.it/"),
    ("IT-T2-021", "T2", "CANDIDATO", "https://www.arpal.liguria.it/"),
    ("IT-T2-022", "T2", "CANDIDATO", "https://www.arpa.vda.it/"),
    ("IT-T2-023", "T2", "CANDIDATO", "https://www.arpab.it/"),
    ("IT-T2-024", "T2", "CANDIDATO", "https://www.anbi.it/"),
    ("IT-T2-029", "T2", "CANDIDATO", "https://www.arpa.puglia.it/"),
    ("IT-T2-035", "T2", "CANDIDATO", "https://www.arpa.sardegna.it/"),
    ("IT-T2-036", "T2", "CANDIDATO", "https://www.arpacal.it/"),
    ("IT-T2-038", "T2", "CANDIDATO", "https://www.meteotrentino.it/"),
    ("IT-T2-030", "T2", "UNIVERSO_ERRADO_PROPOSTO", "https://www.nomisma.it/"),
    # T12 · politica agricola
    ("IT-T12-013", "T12", "CANDIDATO", "https://www.regione.piemonte.it/web/temi/agricoltura"),
    ("IT-T12-023", "T12", "CANDIDATO", "https://www.regione.puglia.it/web/agricoltura"),
    ("IT-T12-024", "T12", "CANDIDATO", "https://www.regione.veneto.it/web/agricoltura-e-foreste"),
    ("IT-T12-025", "T12", "CANDIDATO", "https://www.regione.vda.it/"),
    ("IT-T12-021", "T12", "CANDIDATO", "https://www.provincia.bz.it/agricoltura-foreste/"),
    ("IT-T12-022", "T12", "CANDIDATO", "https://www.regione.molise.it/"),
    ("IT-T12-028", "T12", "CANDIDATO", "https://agricoltura.regione.campania.it/"),
    ("IT-T12-020", "T12", "CANDIDATO", "https://www.politicheagricole.it/"),
    ("IT-T12-026", "T12", "CANDIDATO", "https://www.pianetapsr.it/"),
    ("IT-T12-019", "T12", "CANDIDATO", "https://www.ersaf.lombardia.it/"),
    ("IT-T12-018", "T12", "CANDIDATO", "https://www.arsacweb.it/"),
    ("IT-T12-009", "T12", "CANDIDATO", "https://www.assam.marche.it/"),
    ("IT-T12-017", "T12", "CANDIDATO", "https://www.ersa.fvg.it/"),
    ("IT-T12-003", "T12", "CANDIDATO", "https://www.cia.it/"),
    ("IT-T12-004", "T12", "CANDIDATO", "https://www.confagricoltura.it/ita/"),
    ("IT-T12-005", "T12", "CANDIDATO", "https://aiab.it/"),
    ("IT-T12-006", "T12", "CANDIDATO", "https://www.ciatoscana.eu/home/"),
    ("IT-T12-041", "T12", "CANDIDATO", "https://bura.regione.abruzzo.it/"),
    ("IT-T12-042", "T12", "CANDIDATO", "http://www.bollettino.regione.lombardia.it/"),
    ("IT-T12-039", "T12", "CANDIDATO", "https://www.bandi.regione.lombardia.it/servizi/home"),
    ("IT-T12-105", "T12", "CANDIDATO", "https://www.regione.emilia-romagna.it/"),
    ("IT-T12-064", "T12", "CANDIDATO", "https://calabriaeuropa.regione.calabria.it/"),
    ("IT-T12-081", "T12", "CANDIDATO", "https://ue.regione.lombardia.it"),
    ("IT-T12-076", "T12", "CANDIDATO", "https://pnrr.regione.campania.it/"),
    ("IT-T12-054", "T12", "CANDIDATO", "https://europa.regione.campania.it/"),
    # NEGATIVOS · fontes FORA_DO_ESCOPO (proposta de catalogo) e irmas
    ("IT-T12-057", "T12", "NEGATIVO_FORA_DO_ESCOPO", "https://www.giovani.regione.lombardia.it/"),
    ("IT-T12-074", "T12", "NEGATIVO_FORA_DO_ESCOPO", "https://www.openinnovation.regione.lombardia.it/"),
    ("IT-T12-049", "T12", "NEGATIVO_FORA_DO_ESCOPO", "https://cultura.regione.campania.it/home"),
    ("IT-T12-069", "T12", "NEGATIVO_FORA_DO_ESCOPO", "https://experience.regione.lombardia.it/it/"),
    ("IT-T12-045", "T12", "NEGATIVO_FORA_DO_ESCOPO", "https://istruzione.regione.calabria.it/"),
    ("IT-T12-071", "T12", "NEGATIVO_FORA_DO_ESCOPO", "https://www.nonseidasola.regione.lombardia.it/"),
    ("IT-T12-073", "T12", "NEGATIVO_FORA_DO_ESCOPO", "https://www.oltreigiochi2026.regione.lombardia.it/"),
    ("IT-T12-052", "T12", "NEGATIVO_FORA_DO_ESCOPO", "https://ecosanita.regione.calabria.it/"),
]

_NAV = re.compile(r"privacy|cookie|contatt|accessibil|note-legali|mappa-del-sito|login|"
                  r"area-riservata|newsletter|credits|dichiarazione|feed|rss|/tag/|/category/|"
                  r"wp-content/themes|javascript:|mailto:", re.I)
_ESTATICO = re.compile(r"\.(?:css|js|png|jpe?g|gif|svg|ico|webp|woff2?|ttf|eot|xml|json|zip)$", re.I)
_ITEM = re.compile(r"(?:[a-z0-9]+-){2,}[a-z0-9]+|(?:19|20)\d{2}|\d{3,}", re.I)


def egresso() -> dict:
    try:
        with urllib.request.urlopen("https://ipinfo.io/json", timeout=15) as r:
            d = json.loads(r.read())
        return {"IP": d.get("ip"), "CITY": d.get("city"), "COUNTRY": d.get("country")}
    except Exception as e:                                      # noqa: BLE001
        return {"IP": None, "COUNTRY": "NAO SEI", "ERRO": type(e).__name__}


def primeiro_item(html: bytes, base: str) -> str | None:
    host = urlparse(base).hostname.replace("www.", "")
    vistos = set()
    # ⚠️ SO `<a href>`. A primeira corrida (2026-09-23) lia QUALQUER href — e
    # `<link rel=stylesheet href=...css?ver=1789...>` tem um numero de 3+
    # algarismos: 36 de 47 «materias» foram CSS, JS e icones, e o teto de 3
    # pedidos desses sites ficou gasto. Um seletor que nao olha para a TAG
    # escolhe a folha de estilo antes do artigo.
    for m in re.finditer(rb"<a\s[^>]*?href\s*=\s*[\"']([^\"'#]+)[\"']", html, re.I):
        try:
            u = urljoin(base, m.group(1).decode("utf-8", "replace").strip())
        except ValueError:
            continue
        p = urlparse(u)
        if p.scheme not in ("http", "https") or (p.hostname or "").replace("www.", "") != host:
            continue
        if (u in vistos or u.rstrip("/") == base.rstrip("/") or _NAV.search(u)
                or _ESTATICO.search(p.path)):
            continue
        vistos.add(u)
        ultimo = [s for s in p.path.split("/") if s]
        if ultimo and _ITEM.search(ultimo[-1]):
            return u
    return None


def texto_de(corpo: bytes, url: str) -> tuple[str, str]:
    if corpo[:5] == b"%PDF-":
        with tempfile.TemporaryDirectory() as d:
            f = Path(d, "x.pdf")
            f.write_bytes(corpo)
            t, estado, _e, _m = PDFX.extrair(f)
        return t, "PDF:" + str(estado)
    t, estado, _e, _m = HTMLX.extrair(corpo, "text/html")
    return t, "HTML:" + str(estado)


def main(argv=None) -> int:
    PASTA.mkdir(parents=True, exist_ok=True)
    itens, sites = [], []
    for sid, uni, papel, entrada in SITES:
        eg = egresso()
        reg = {"SOURCE_ID": sid, "UNIVERSO_DECLARADO": uni, "PAPEL": papel,
               "ENTRADA": entrada, "EGRESSO": eg, "PEDIDOS": 0}
        sites.append(reg)
        if eg.get("COUNTRY") != "IT":
            reg["PARADO"] = "EGRESSO_NAO_IT — recolha interrompida"
            print("PARAGEM: egresso %s" % eg, flush=True)
            break
        rp, txt = GATE.robots_de(urlparse(entrada).hostname)
        reg["PEDIDOS"] += 1
        if "inacessivel" in txt or not GATE.permitido(entrada, rp):
            reg["PARADO"] = "robots: " + txt[:100]
            print("%-11s robots %s" % (sid, txt[:60]), flush=True)
            continue
        time.sleep(PAUSA_S)
        st, corpo, err = CAN.buscar(entrada)
        reg["PEDIDOS"] += 1
        if st != 200:
            reg["PARADO"] = "entrada HTTP %s %s" % (st, err)
            print("%-11s entrada %s" % (sid, st), flush=True)
            continue
        alvo = primeiro_item(corpo, entrada)
        if not alvo:
            reg["PARADO"] = "nenhum link com cara de item na entrada"
            print("%-11s sem item" % sid, flush=True)
            continue
        if not GATE.permitido(alvo, rp):
            reg["PARADO"] = "robots proibe " + alvo
            continue
        time.sleep(PAUSA_S)
        st, corpo, err = CAN.buscar(alvo)
        reg["PEDIDOS"] += 1
        if st != 200:
            reg["PARADO"] = "item HTTP %s %s" % (st, err)
            print("%-11s item %s" % (sid, st), flush=True)
            continue
        if not (corpo[:5] == b"%PDF-" or corpo.lstrip()[:1] == b"<"):
            reg["PARADO"] = "item nao e HTML nem PDF: " + alvo
            continue
        sha = hashlib.sha256(corpo).hexdigest()
        ext = ".pdf" if corpo[:5] == b"%PDF-" else ".html"
        (PASTA / (sha[:16] + ext)).write_bytes(corpo)
        texto, estado = texto_de(corpo, alvo)
        itens.append({"ITEM_ID": "G-%s" % sha[:12], "SOURCE_ID": sid,
                      "UNIVERSO_DECLARADO": uni, "PAPEL": papel, "URL": alvo,
                      "ENTRADA": entrada, "HTTP": st, "BYTES": len(corpo),
                      "SHA256": sha, "FICHEIRO": "data/samples/GABARITO-T2-T12/%s%s" % (sha[:16], ext),
                      "EXTRACAO": estado, "EGRESSO": eg,
                      "OBTIDO_EM": datetime.now(timezone.utc).isoformat()})
        print("%-11s %-4s %s %d B" % (sid, uni, alvo[:90], len(corpo)), flush=True)
        time.sleep(PAUSA_S)
    d = {"DATASET": "GABARITO-T2-T12-V1", "ESTADO": "RECOLHIDO — por julgar",
         "AUTORIZACAO": "DECISOES-DONO-2026-09-23 D4",
         "REGRA_DE_PEDIDOS": "robots + entrada + 1 materia = 3 por site, todos contados",
         "SITES": sites, "ITENS": itens}
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
