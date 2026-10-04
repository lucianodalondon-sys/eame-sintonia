"""GABARITO DO DETECTOR DE CAPA — recolha de paginas reais (missao 6-PREP-c).

NAO e coleta: nada vai a Sala, ao armazem oficial, ao banco, aos livros.
Os bytes ficam numa pasta de gabarito (por omissao ~/detector-capa-gabarito/),
com um MANIFESTO por pagina: URL, sha256, egresso, hora, HTTP, e porque foi
escolhida.

Regras da ida, todas no codigo:
  · egresso medido ANTES de cada site; se nao for IT, PARA TUDO;
  · no maximo 3 pedidos por site (robots + 2 paginas), 1 s de pausa;
  · robots lido pelo leitor da casa (curadoria/gate_de_rota.robots_de), com o
    UA da casa; o que o robots nega nao se pede; 403 nao se contorna.

A escolha das paginas NAO usa o LINK_PATTERN do contrato — de proposito. Se as
materias fossem escolhidas pelo padrao e as capas fossem o INDEX_URL, a
proposta «morada antes da estrutura» acertava tudo por construcao:
  · CAPA_INDICE   o INDEX_URL do contrato (circular para a proposta: declarado)
  · MATERIA       o link interno com o texto de ancora mais longo (titulo)
  · CAPA_OUTRA    um link interno de navegacao (contatti, chi siamo, archivio,
                  categoria, pagina N...) — capa que NAO e o INDEX_URL
O veredito humano vem depois, pagina a pagina; a escolha e so uma candidatura.

    py scripts/detector_capa/colher_gabarito.py [--n=50] [--saida=<pasta>]
"""
from __future__ import annotations

import hashlib
import html as H
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
import canario as CAN          # noqa: E402  buscar() com o UA e o TLS da casa
import gate_de_rota as GR      # noqa: E402  robots_de(): o leitor da casa

NAVEGACAO = re.compile(r"(contatt|contact|chi-?siamo|about|archivi|categor|/page/\d|pagina|"
                       r"calendari|/tag/|comunicati|/news/?$|/notizie/?$|/eventi/?$)", re.I)
LIXO = re.compile(r"(privacy|cookie|login|accedi|registr|mailto:|javascript:|\.pdf$|\.jpe?g$|"
                  r"\.png$|facebook|instagram|linkedin|twitter|youtube|whatsapp)", re.I)
SOCIAL = ("facebook", "instagram", "youtube", "linkedin", "twitter", "x.com", "tiktok")


def agora():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def egresso() -> dict:
    """EGR (24/09): o pais pelo DONO — superficie/rede.py, consenso de 3 verificadores
    com cache de 3 min. Nenhum consumidor pergunta a um servico diretamente (o
    ipinfo.io em 429 parou tudo das 13:05 as 15:05). O IP nao sai do dono."""
    import importlib.util as _u, os as _os
    _s = _u.spec_from_file_location("rede_egresso", _os.path.join(str(RAIZ), "superficie", "rede.py"))
    _r = _u.module_from_spec(_s)
    _s.loader.exec_module(_r)
    e = _r.egresso()
    pais = e["EGRESS_COUNTRY_CODE"] if e["EGRESS_COUNTRY_CODE"] != "UNKNOWN" else None
    return {"PAIS": pais or "NAO SEI", "VOTOS": e["VOTOS"]}


CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"


def hosts(n: int, ids: list[str] | None = None) -> list[dict]:
    """n fontes HTML do Curator, uma por dominio, espalhadas por universo e
    escolhidas de forma deterministica (ordenadas por SOURCE_ID, round-robin).
    Com `ids`, so essas (a ordem dada), uma por dominio na mesma."""
    c = json.loads(Path(CONTRATOS).read_text(encoding="utf-8"))
    if ids is not None:
        por_id = {f["SOURCE_ID"]: f for f in c["FONTES"]}
        out, vistos = [], set()
        for s in ids:
            f = por_id.get(s)
            aq = (f or {}).get("ACQUISITION") or {}
            if aq.get("STRATEGY") != "HTML_LINK_DISCOVERY":
                continue
            h = urlparse(aq["INDEX_URL"]).netloc.lower().removeprefix("www.")
            if h not in vistos:
                vistos.add(h)
                out.append(f)
        return out
    por_u, vistos = {}, set()
    for f in sorted(c["FONTES"], key=lambda f: f["SOURCE_ID"]):
        aq = f.get("ACQUISITION") or {}
        if aq.get("STRATEGY") != "HTML_LINK_DISCOVERY" or str(f.get("OUTPUT_TYPE")).upper() != "HTML":
            continue
        h = urlparse(aq["INDEX_URL"]).netloc.lower().removeprefix("www.")
        if h in vistos or any(s in h for s in SOCIAL):
            continue
        vistos.add(h)
        por_u.setdefault(f["SOURCE_ID"].split("-")[1], []).append(f)
    out = []
    while len(out) < n and any(por_u.values()):
        for u in sorted(por_u):
            if por_u[u] and len(out) < n:
                out.append(por_u[u].pop(0))
    return out


def links(base: str, b: bytes) -> list[tuple[str, str]]:
    txt = b.decode("utf-8", "replace")
    host = urlparse(base).netloc.lower().removeprefix("www.")
    out = []
    for m in re.finditer(r'<a\b[^>]*href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a\s*>', txt, re.I | re.S):
        try:
            u = urljoin(base, H.unescape(m.group(1)).strip())
            fora = urlparse(u).netloc.lower().removeprefix("www.") != host
        except ValueError:             # href mal formado (medido: «Invalid IPv6 URL»)
            continue
        if fora or LIXO.search(u):
            continue
        ancora = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))).strip()
        out.append((u, ancora))
    return out


def escolher(base: str, b: bytes, modo: str) -> tuple[str, str] | None:
    ls = [(u, a) for u, a in links(base, b) if u.rstrip("/") != base.rstrip("/")]
    if modo == "MATERIA":
        cand = [(u, a) for u, a in ls if not NAVEGACAO.search(u) and len(a.split()) >= 5]
        return max(cand, key=lambda x: len(x[1])) if cand else None
    cand = [(u, a) for u, a in ls if NAVEGACAO.search(u)]
    return cand[0] if cand else None


def guardar(pasta: Path, sid: str, papel: str, url: str, st: int, b: bytes, eg: dict, porque: str) -> dict:
    sha = hashlib.sha256(b).hexdigest()
    f = pasta / "bytes" / f"{sid}-{papel}-{sha[:12]}.html"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(b)
    return {"SOURCE_ID": sid, "PAPEL_CANDIDATO": papel, "URL": url, "HTTP": st,
            "SHA256": sha, "BYTES": len(b), "FICHEIRO": str(f.relative_to(pasta)),
            "EGRESSO": eg, "QUANDO": agora(), "PORQUE_ESCOLHIDA": porque}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    n = int(next((a.split("=", 1)[1] for a in argv if a.startswith("--n=")), 50))
    pasta = Path(next((a.split("=", 1)[1] for a in argv if a.startswith("--saida=")),
                      Path.home() / "detector-capa-gabarito"))
    global CONTRATOS
    CONTRATOS = Path(next((a.split("=", 1)[1] for a in argv if a.startswith("--contratos=")), CONTRATOS))
    ids = next((a.split("=", 1)[1].split(",") for a in argv if a.startswith("--ids=")), None)
    so_materia = "--so-materia" in argv
    pasta.mkdir(parents=True, exist_ok=True)
    manifesto, registo = [], []
    # RETOMA: um site ja visitado nao se visita outra vez — o teto e 3 pedidos
    # POR SITE, nao por corrida.
    mf = pasta / "MANIFESTO.json"
    if mf.exists():
        velho = json.loads(mf.read_text(encoding="utf-8"))
        manifesto, registo = velho["PAGINAS"], velho["REGISTO"]
    feitos = {r["SOURCE_ID"] for r in registo}
    for i, f in enumerate(hosts(n, ids)):
        sid, aq = f["SOURCE_ID"], f["ACQUISITION"]
        if sid in feitos:
            continue
        modo = "MATERIA" if so_materia else ("CAPA_OUTRA" if i % 4 == 3 else "MATERIA")
        eg = egresso()
        if eg.get("PAIS") != "IT":
            registo.append({"SOURCE_ID": sid, "PAROU": "EGRESSO_NAO_IT", "EGRESSO": eg})
            print(f"PARADO: egresso {eg} antes de {sid}", file=sys.stderr)
            break
        host = urlparse(aq["INDEX_URL"]).netloc
        pedidos = 1
        rp, porque_robots = GR.robots_de(host)
        linha = {"SOURCE_ID": sid, "HOST": host, "MODO": modo, "ROBOTS": porque_robots[:120],
                 "EGRESSO": eg}
        if not rp.can_fetch(GR.CAP.UA, aq["INDEX_URL"]):
            registo.append({**linha, "PAROU": "ROBOTS_NEGA_O_INDICE"})
            continue
        time.sleep(1)
        st, b, err = CAN.buscar(aq["INDEX_URL"])
        pedidos += 1
        if st != 200 or not b:
            registo.append({**linha, "PAROU": f"INDICE {err or st}"})
            continue
        manifesto.append(guardar(pasta, sid, "CAPA_INDICE", aq["INDEX_URL"], st, b, eg,
                                 "INDEX_URL do contrato"))
        alvo = escolher(aq["INDEX_URL"], b, modo)
        if not alvo:
            registo.append({**linha, "PEDIDOS": pedidos, "PAROU": f"SEM_LINK_PARA_{modo}"})
            continue
        u, ancora = alvo
        if not rp.can_fetch(GR.CAP.UA, u):
            registo.append({**linha, "PEDIDOS": pedidos, "PAROU": "ROBOTS_NEGA_O_ALVO", "ALVO": u})
            continue
        time.sleep(1)
        st, b2, err = CAN.buscar(u)
        pedidos += 1
        if st == 200 and b2:
            manifesto.append(guardar(pasta, sid, modo, u, st, b2, eg,
                                     f"ancora: {ancora[:120]}"))
        registo.append({**linha, "PEDIDOS": pedidos, "ALVO": u,
                        "RESULTADO": st if st == 200 else (err or st)})
        (pasta / "MANIFESTO.json").write_text(json.dumps(
            {"GERADO_EM": agora(), "PAGINAS": manifesto, "REGISTO": registo},
            ensure_ascii=False, indent=1), encoding="utf-8")
    (pasta / "MANIFESTO.json").write_text(json.dumps(
        {"GERADO_EM": agora(), "PAGINAS": manifesto, "REGISTO": registo},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"paginas {len(manifesto)} · sites {len(registo)} · em {pasta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
