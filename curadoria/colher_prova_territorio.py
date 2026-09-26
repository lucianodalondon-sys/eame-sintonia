#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""COLHER PROVA DE TERRITÓRIO — as 3 páginas que o canal DECISOES-SEMANTICAS exige, e mais nada. (MICRO-PROVA, 26/09)

Não é rota de coleta: não escreve RAW, não toca a Sala, não enfileira. Lê, por candidata, no MÁXIMO 5 pedidos ao seu
domínio (teto D38): robots.txt · a entrada da ficha · (a página «chi siamo/about», se a entrada não disser quem é) ·
2 páginas do que o site publica. Tudo pelo leitor da casa (`canario.buscar`: UA, TLS, timeout, teto de 4 MB), com o
robots.txt lido e CUMPRIDO (`urllib.robotparser`), e o portão de egresso IT por consenso antes de cada candidata.

Escreve PROPOSTAS no formato do canal (`curadoria/decisao_semantica.py`): PROVAS com PAPEL/URL/SHA256/BYTES/LIDO_EM/
EGRESSO/BYTES_EM, e `TERRITORIO = "A_DECIDIR"` — o canal IGNORA uma entrada assim (não é T1..T12). A decisão é de
Opus/humano: preenche TERRITORIO, PAIS (da prova), DECIDIDO_POR, PORQUE. Só depois:

    py curadoria/colher_prova_territorio.py --lote=LOTE.json --bytes=<pasta fora do Git> --saida=PROPOSTAS.json
    py curadoria/colher_prova_territorio.py --aplicar=DECIDIDAS.json        # escreve no canal SÓ as que valem

`--aplicar` passa cada decisão pelo validador do próprio canal (`porque_invalida` contra a ficha) e, se a candidata
já tinha um «NAO SEI» (PROVA_INSUFICIENTE…), SUBSTITUI-O guardando-o em `ANTERIOR` — duas entradas para a mesma
candidata são um conflito que o QUALIFY recusa. Nunca escreve TERRITORIO sem DECIDIDO_POR.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "superficie"))

CANDIDATAS = RAIZ / "candidatas" / "FONTES-CANDIDATAS.json"
DECISOES = RAIZ / "curadoria" / "DECISOES-SEMANTICAS-V1.json"
TETO_D38 = 5
A_DECIDIR = "A_DECIDIR"

_INSTITUCIONAL = re.compile(r"chi[-_ ]?siamo|about|presentazion|il[-_]dipartimento|l[-_]ente|istituzional|"
                            r"mission|statuto|organizzazione|who[-_]we[-_]are|contatti-e-sede", re.I)
_NAO_CONTEUDO = re.compile(r"(privacy|cookie|login|contatt|accessibil|note-legali|mappa|search|cerca|feed|"
                           r"wp-(admin|json|content)|\.(pdf|jpg|png|zip|css|js)(\?|$))", re.I)
_TITULO = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mesmo_site(u: str, base: str) -> bool:
    a, b = urlparse(u).netloc.lower().removeprefix("www."), urlparse(base).netloc.lower().removeprefix("www.")
    return a == b


def _links(html: bytes, base: str) -> list[str]:
    s = html.decode("utf-8", "replace")
    vistos, out = set(), []
    for h in re.findall(r'href\s*=\s*["\']([^"\'#]+)', s, re.I):
        u = urljoin(base, h.strip())
        if u.startswith(("http://", "https://")) and _mesmo_site(u, base) and u not in vistos:
            vistos.add(u)
            out.append(u)
    return out


def _parece_conteudo(u: str, base: str) -> bool:
    p = urlparse(u).path
    if _NAO_CONTEUDO.search(u) or p.rstrip("/") in ("", urlparse(base).path.rstrip("/")):
        return False
    ultimo = [x for x in p.split("/") if x][-1:] or [""]
    return bool(re.search(r"(19|20)\d\d", p) or ultimo[0].count("-") >= 3)


def colher(ficha: dict, buscar, portao, pasta: Path, dormir=time.sleep, pausa: float = 3.0) -> dict:
    """Uma candidata. `buscar(url)->(status, bytes, erro)` e `portao()->dict` injectados (testável sem rede)."""
    cid, url = ficha["CANDIDATA_ID"], ficha["URL"]
    out = {"CANDIDATA_ID": cid, "NOME": ficha.get("NOME"), "URL": url, "TERRITORIO": A_DECIDIR,
           "PROVAS": [], "PEDIDOS": 0, "TITULOS": []}
    g = portao()
    out["EGRESS_GATE"] = g.get("EGRESS_GATE")
    if g.get("EGRESS_GATE") != "PASS":
        out["PORQUE_PAROU"] = "portao de egresso sem PASS IT — 0 pedidos"
        return out

    def pedir(u):
        if out["PEDIDOS"] >= TETO_D38:
            return 0, b"", "teto D38"
        if out["PEDIDOS"]:
            dormir(pausa)
        out["PEDIDOS"] += 1
        return buscar(u)

    p = urlparse(url)
    st, txt, err = pedir("%s://%s/robots.txt" % (p.scheme or "https", p.netloc))
    rp = urllib.robotparser.RobotFileParser()
    if st == 200:
        rp.parse(txt.decode("utf-8", "replace").splitlines())
        out["ROBOTS"] = "LIDO"
    elif st == 404:
        rp.parse([])
        out["ROBOTS"] = "404 (nao publica: tudo permitido)"
    else:
        out["ROBOTS"] = "ILEGIVEL (%s) — nao se pede mais nada" % (err or st)
        out["PORQUE_PAROU"] = "robots.txt ilegivel: UNKNOWN nao e licenca"
        return out

    def guardar(papel, u, st, b):
        sha = hashlib.sha256(b).hexdigest()
        n = len(out["PROVAS"])
        dest = pasta / cid / ("%d_%s.bin" % (n, papel))
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b)
        t = _TITULO.search(b.decode("utf-8", "replace"))
        out["TITULOS"].append((t.group(1).strip()[:120] if t else ""))
        out["PROVAS"].append({"PAPEL": papel, "URL": u, "SHA256": sha, "BYTES": len(b), "HTTP": st,
                              "LIDO_EM": _agora(), "EGRESSO": "IT", "BYTES_EM": str(dest)})

    if not rp.can_fetch("*", url):
        out["PORQUE_PAROU"] = "robots.txt proibe a entrada da ficha"
        return out
    st, entrada, err = pedir(url)
    if st != 200 or not entrada:
        out["PORQUE_PAROU"] = "entrada nao abriu: %s" % (err or st)
        return out
    links = [u for u in _links(entrada, url) if rp.can_fetch("*", u)]
    inst = next((u for u in links if _INSTITUCIONAL.search(urlparse(u).path)), None)
    if inst:
        st2, b2, err2 = pedir(inst)                           # a pagina que diz quem a organizacao E
        if st2 == 200 and b2:
            guardar("INSTITUCIONAL", inst, st2, b2)
    else:
        guardar("INSTITUCIONAL", url, st, entrada)             # a propria entrada diz quem e (casa do site)
    conteudos = [u for u in links if _parece_conteudo(u, url)]
    shas_vistas = {x["SHA256"] for x in out["PROVAS"]}
    for u in conteudos:
        if sum(1 for x in out["PROVAS"] if x["PAPEL"] == "CONTEUDO") >= 2 or out["PEDIDOS"] >= TETO_D38:
            break
        st3, b3, err3 = pedir(u)
        if st3 == 200 and b3 and hashlib.sha256(b3).hexdigest() not in shas_vistas:
            guardar("CONTEUDO", u, st3, b3)
            shas_vistas.add(out["PROVAS"][-1]["SHA256"])
    n_cont = sum(1 for x in out["PROVAS"] if x["PAPEL"] == "CONTEUDO")
    out["PROVA_COMPLETA"] = bool(any(x["PAPEL"] == "INSTITUCIONAL" for x in out["PROVAS"]) and n_cont >= 2)
    if not out["PROVA_COMPLETA"]:
        out["PORQUE_PAROU"] = "prova incompleta: %d institucional, %d conteudo (faltam paginas distintas)" % (
            sum(1 for x in out["PROVAS"] if x["PAPEL"] == "INSTITUCIONAL"), n_cont)
    try:
        import atribuir_source_id as ASI                        # a regra da casa, so como SUGESTAO
        t, porque = ASI.territorio_de({"NOME": "%s %s" % (ficha.get("NOME") or "", " ".join(out["TITULOS"][:1])),
                                       "URL": url})
        out["SUGESTAO_DA_REGRA"] = {"TERRITORIO": t, "PORQUE": porque}
    except Exception as ex:  # noqa: BLE001
        out["SUGESTAO_DA_REGRA"] = {"TERRITORIO": "NAO SEI", "PORQUE": "regra indisponivel: %s" % ex}
    return out


def aplicar(decididas: list[dict], caminho: Path = DECISOES, fichas: dict | None = None) -> dict:
    import decisao_semantica as DS
    fichas = fichas if fichas is not None else {c["CANDIDATA_ID"]: c for c in
                                                json.loads(CANDIDATAS.read_text(encoding="utf-8"))["CANDIDATAS"]}
    doc = json.loads(caminho.read_text(encoding="utf-8"))
    por_cand = {}
    for i, d in enumerate(doc["DECISOES"]):
        por_cand.setdefault(d.get("CANDIDATA_ID"), []).append(i)
    entram, ficam = [], []
    for d in decididas:
        cid = d.get("CANDIDATA_ID")
        motivo = None
        if d.get("TERRITORIO") in (A_DECIDIR, None, ""):
            motivo = "ainda A_DECIDIR"
        elif cid not in fichas:
            motivo = "candidata desconhecida na porta"
        else:
            motivo = DS.porque_invalida(d, fichas[cid])
        if motivo:
            ficam.append({"CANDIDATA_ID": cid, "PORQUE": motivo})
            continue
        velhas = [doc["DECISOES"][i] for i in por_cand.get(cid, [])]
        if any(v.get("TERRITORIO") not in ("NAO SEI", None) for v in velhas):
            ficam.append({"CANDIDATA_ID": cid, "PORQUE": "ja tem territorio decidido — nao se sobrescreve"})
            continue
        nova = {k: v for k, v in d.items() if k not in ("TITULOS", "PEDIDOS", "EGRESS_GATE", "ROBOTS",
                                                        "PROVA_COMPLETA", "PORQUE_PAROU")}
        if not nova.get("DECIDIDO_EM"):
            nova["DECIDIDO_EM"] = _agora()
        if velhas:
            nova["ANTERIOR"] = velhas
        entram.append(nova)
    if entram:
        sai = {e["CANDIDATA_ID"] for e in entram}
        doc["DECISOES"] = [d for d in doc["DECISOES"] if d.get("CANDIDATA_ID") not in sai] + entram
        doc["TOTAL"] = len(doc["DECISOES"])
        doc["DECIDIDAS"] = sum(1 for d in doc["DECISOES"] if d.get("TERRITORIO") != "NAO SEI")
        doc["NAO_SEI"] = doc["TOTAL"] - doc["DECIDIDAS"]
        tmp = caminho.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        tmp.replace(caminho)
    return {"ENTRAM": [e["CANDIDATA_ID"] for e in entram], "FICAM": ficam}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    if a.get("aplicar"):
        r = aplicar(json.loads(Path(a["aplicar"]).read_text(encoding="utf-8"))["PROPOSTAS"])
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0
    if not a.get("lote") or not a.get("bytes"):
        print(__doc__)
        return 2
    import canario as CAN      # noqa: E402
    import rede                # noqa: E402
    lote = json.loads(Path(a["lote"]).read_text(encoding="utf-8"))
    fichas = {c["CANDIDATA_ID"]: c for c in json.loads(CANDIDATAS.read_text(encoding="utf-8"))["CANDIDATAS"]}
    props = [colher(fichas[cid], CAN.buscar, lambda: rede.portao_de_egresso("IT"), Path(a["bytes"]))
             for cid in lote["CANDIDATAS"]]
    out = {"DATASET": "PROPOSTAS-DE-TERRITORIO", "GERADO_EM": _agora(), "PEDIDOS": sum(p["PEDIDOS"] for p in props),
           "PROVA_COMPLETA": sum(1 for p in props if p.get("PROVA_COMPLETA")), "PROPOSTAS": props}
    Path(a.get("saida", "PROPOSTAS-DE-TERRITORIO.json")).write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("PEDIDOS", "PROVA_COMPLETA")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
