#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEDIR CONTAGENS — onde uma rede PUBLICA de monitorizacao pubica o SINAL PRECOCE (capturas em armadilha, voos,
ovos/larvas/adultos, % de infestacao, limiar), em que FORMATO, com que FREQUENCIA, para que cultura/praga.
(LOTE-MONITORIZACAO, 26/09; alinhamento do dono secoes 2-3: o sinal antes do boletim.)

Nao e rota de coleta: nao escreve RAW, nao toca a Sala, nao regista nada. Por alvo, no MAXIMO 5 pedidos ao dominio
(teto D38): robots.txt · a entrada · ate 3 paginas escolhidas pelos links com cara de monitorizacao (ancora ou
endereco: catture, trappole, monitoraggio, voli, cimice, Popillia, mosca, tignoletta...). Robots lido e CUMPRIDO,
portao de egresso IT antes de cada alvo. Os bytes ficam fora do Git com sha256.

    py curadoria/medir_contagens.py --lote=<LOTE.json> --bytes=<pasta fora do Git> --saida=<CONTAGENS.json>

VEREDITO por alvo (medido nos bytes, nunca pelo nome):
  CONTAGEM_PUBLICA  — uma pagina com numeros de captura/individuos/% infestacao (tabela ou texto) e data;
  TABELA_EM_FICHEIRO — so links para CSV/XLS/PDF com nome de monitorizacao (o ficheiro nao foi aberto: diz-se onde);
  SO_BOLETIM         — ha avisos/boletins, mas nenhum numero de contagem nas paginas lidas;
  LOGIN              — a pagina de monitorizacao pede autenticacao (fora: so redes publicas);
  NAO_SEI            — nao abriu, robots, portao — o motivo vai escrito.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import urllib.robotparser
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import colher_prova_territorio as CPT   # noqa: E402  (datas, texto visivel, pagina HTML — o mesmo juizo)

TETO = 5
FORTE = re.compile(r"cattur\w*|trappol\w*|monitoragg\w*|curv[ae][-_ ]di[-_ ]volo|\bvol[oi]\b|ovideposiz\w*|"
                   r"infestaz\w*|soglia|rilevament\w*|campionament\w*|fallenfang|monitoring", re.I)
PRAGAS = re.compile(r"mosca (dell.olivo|olearia)|bactrocera|tignoletta|lobesia|tignola|cimice asiatica|halyomorpha|"
                    r"popillia|drosophila suzukii|suzukii|carpocapsa|cydia|flavescenza|scafoideo|scaphoideus|diabrotica|"
                    r"tuta absoluta|psilla|piralide|ostrinia|peronospora|oidio|ticchiolatura|xylella|cocciniglia|"
                    r"afid\w*|nottu\w*|elaterid\w*|cicalina|margaronia|zeuzera|cossus|anarsia|mosca della frutta|ceratitis", re.I)
CULTURAS = re.compile(r"\b(olivo|vite|melo|pero|pesco|nettarin\w*|albicocc\w*|ciliegi\w*|susin\w*|actinidia|kiwi|"
                      r"mais|frumento|grano|pomodoro|patata|nocciol\w*|castagn\w*|agrumi|arancio|limone|fragola|"
                      r"piccoli frutti|mirtillo|soia|riso|orticole|cucurbit\w*)\b", re.I)
CONTA = re.compile(r"(\d{1,5})\s*(catture|adulti|individui|esemplari|larve|uova|ovideposizioni|femmine|maschi|"
                   r"punture|capture)\b|\b(catture|individui|adulti)\s*(?:[:=]|per trappola|/trappola)?\s*(\d{1,5})", re.I)
PCT = re.compile(r"(\d{1,3}(?:[.,]\d+)?)\s*%\s*(?:di\s+)?(?:infestaz\w*|attacco|frutti colpiti|punture|olive)"
                 r"|(?:infestaz\w*|attacco|frutti colpiti|punture)[^.%]{0,60}?(\d{1,3}(?:[.,]\d+)?)\s*%", re.I)
LOGIN = re.compile(r"type=[\"']password|area riservata|accedi per|effettua(re)? il login|login richiesto|"
                   r"registrati per|previa registrazione", re.I)
EXT_DADOS = re.compile(r"\.(csv|xlsx?|ods|pdf|json)(\?|$)", re.I)


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def links_com_ancora(html: bytes, base: str) -> list[tuple[str, str]]:
    s = html.decode("utf-8", "replace")
    out, vistos = [], set()
    for m in re.finditer(r"<a\b[^>]*href\s*=\s*[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", s, re.I | re.S):
        u = urljoin(base, m.group(1).strip())
        anc = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()[:120]
        if u.startswith(("http://", "https://")) and CPT._mesmo_site(u, base) and u not in vistos:
            vistos.add(u)
            out.append((u, anc))
    return out


def pontuar(u: str, anc: str) -> int:
    s = "%s %s" % (urlparse(u).path, anc)
    return 3 * len(FORTE.findall(s)) + 2 * len(PRAGAS.findall(s)) + bool(re.search(r"bollettin|avvis|difesa", s, re.I))


def ler_pagina(b: bytes, url: str) -> dict:
    """O que uma pagina tem de SINAL PRECOCE. So bytes."""
    if b.lstrip()[:5] == b"%PDF-":
        return {"FORMATO": "PDF", "NOTA": "PDF nao lido aqui (formato registado; o conteudo mede-se na coleta)"}
    if b[:2] == b"PK":
        return {"FORMATO": "XLSX/ZIP", "NOTA": "folha/arquivo nao lido aqui"}
    if not CPT._e_pagina_html(b):
        s = b[:4000].decode("utf-8", "replace")
        if s.count("\n") >= 3 and s.count(";") + s.count(",") >= 6:
            return {"FORMATO": "CSV"}
        return {"FORMATO": "BINARIO_OU_TEXTO"}
    s = b.decode("utf-8", "replace")
    texto = CPT._texto_visivel(s)
    tabelas = re.findall(r"(?is)<table\b.*?</table>", s)
    numericas = [t for t in tabelas if len(re.findall(r"<t[dh][^>]*>\s*\d{1,5}(?:[.,]\d+)?\s*</t[dh]>", t, re.I)) >= 3]
    contas = [m.group(0) for m in CONTA.finditer(texto)][:5]
    pcts = [m.group(0) for m in PCT.finditer(texto)][:5]
    em_tabela = [t for t in numericas if FORTE.search(t) or PRAGAS.search(t)]
    return {"FORMATO": "HTML", "LETRAS": len(texto),
            # o formulario de entrada no menu de TODAS as paginas nao fecha a pagina (Terre dell'Etruria): so e
            # porta fechada quando pede senha E quase nao tem texto
            "LOGIN": bool(LOGIN.search(s)) and len(texto) < CPT.LETRAS_CONTEUDO,
            "TABELAS_NUMERICAS": len(numericas), "TABELAS_DE_MONITORIZACAO": len(em_tabela),
            "CONTAGENS": contas, "PCT_INFESTACAO": pcts, "SOGLIA": bool(re.search(r"soglia", texto, re.I)),
            "PRAGAS": sorted({m.group(0).lower() for m in PRAGAS.finditer(texto)})[:8],
            "CULTURAS": sorted({m.group(0).lower() for m in CULTURAS.finditer(texto)})[:8],
            "DATAS": sorted({"%04d-%02d-%02d" % d for d in CPT._datas(texto) if 1990 <= d[0] and 1 <= d[1] <= 12
                             and 1 <= d[2] <= 31})[-12:]}


def frequencia(datas: list[str]) -> str:
    ds = sorted({date.fromisoformat(d) for d in datas})
    if len(ds) < 3:
        return "NAO SEI (menos de 3 datas lidas)"
    gaps = sorted((b - a).days for a, b in zip(ds, ds[1:]) if (b - a).days > 0)
    if not gaps:
        return "NAO SEI"
    med = gaps[len(gaps) // 2]
    return "~%d dias entre publicacoes (mediana de %d intervalos lidos)" % (med, len(gaps))


def medir(alvo: dict, buscar, portao, pasta: Path, dormir=time.sleep, pausa: float = 3.0) -> dict:
    """Um alvo. `buscar(url)->(status, bytes, erro)` e `portao()->dict` injectados (testavel sem rede)."""
    url = alvo["URL"]
    out = {**{k: alvo.get(k) for k in ("ID", "SOURCE_ID", "NOME", "URL", "REGIAO", "TIPO")},
           "PEDIDOS": 0, "PAGINAS": [], "LINKS_DE_DADOS": []}
    g = portao()
    out["EGRESS_GATE"] = g.get("EGRESS_GATE")
    if g.get("EGRESS_GATE") != "PASS":
        return {**out, "VEREDITO": "NAO_SEI", "PORQUE": "portao de egresso sem PASS IT — 0 pedidos"}

    def pedir(u):
        if out["PEDIDOS"] >= TETO:
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
    elif st == 404:
        rp.parse([])
    else:
        return {**out, "VEREDITO": "NAO_SEI", "PORQUE": "robots.txt ilegivel (%s): UNKNOWN nao e licenca" % (err or st)}
    if not rp.can_fetch("*", url):
        return {**out, "VEREDITO": "NAO_SEI", "PORQUE": "robots.txt proibe a entrada"}

    def guardar(u, st, b):
        n = len(out["PAGINAS"])
        dest = pasta / (alvo.get("ID") or "X") / ("%d.bin" % n)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b)
        pg = {"URL": u, "HTTP": st, "SHA256": hashlib.sha256(b).hexdigest(), "BYTES": len(b),
              "BYTES_EM": str(dest), "LIDO_EM": _agora(), **ler_pagina(b, u)}
        out["PAGINAS"].append(pg)
        return pg

    st, entrada, err = pedir(url)
    if st != 200 or not entrada:
        return {**out, "VEREDITO": "NAO_SEI", "PORQUE": "entrada nao abriu: %s" % (err or st)}
    guardar(url, st, entrada)
    # lm-1310: a FEM linkava a propria entrada (com/sem barra final) e a sonda gastou um pedido a le-la outra vez
    igual = lambda x: x.split("#")[0].rstrip("/").lower()   # noqa: E731
    links = [(u, a) for u, a in links_com_ancora(entrada, url) if rp.can_fetch("*", u) and igual(u) != igual(url)]
    for u, a in links:
        if EXT_DADOS.search(u) and (FORTE.search(u + " " + a) or PRAGAS.search(u + " " + a)):
            out["LINKS_DE_DADOS"].append({"URL": u, "ANCORA": a, "EXT": EXT_DADOS.search(u).group(1).lower()})
    seguir = sorted(((pontuar(u, a), i, u) for i, (u, a) in enumerate(links)
                     if not EXT_DADOS.search(u) and pontuar(u, a) >= 3), key=lambda x: (-x[0], x[1]))
    for _, _, u in seguir:
        if out["PEDIDOS"] >= TETO:
            break
        st2, b2, err2 = pedir(u)
        if st2 == 200 and b2:
            guardar(u, st2, b2)
    return {**out, **veredito(out)}


def veredito(out: dict) -> dict:
    html = [p for p in out["PAGINAS"] if p.get("FORMATO") == "HTML"]
    com_conta = [p for p in html if (p.get("CONTAGENS") or p.get("PCT_INFESTACAO") or p.get("TABELAS_DE_MONITORIZACAO"))
                 and p.get("DATAS") and not p.get("LOGIN")]
    datas = sorted({d for p in html for d in p.get("DATAS", [])})
    base = {"PRAGAS": sorted({x for p in html for x in p.get("PRAGAS", [])}),
            "CULTURAS": sorted({x for p in html for x in p.get("CULTURAS", [])}),
            "FREQUENCIA": frequencia(datas)}
    if com_conta:
        melhor = max(com_conta, key=lambda p: (p.get("TABELAS_DE_MONITORIZACAO", 0), len(p.get("CONTAGENS", []))))
        return {**base, "VEREDITO": "CONTAGEM_PUBLICA", "TABELA_EM": melhor["URL"],
                "FORMATO_DA_TABELA": "HTML (tabela)" if melhor.get("TABELAS_DE_MONITORIZACAO") else "HTML (texto)",
                "PORQUE": "numeros de monitorizacao lidos: %s" % "; ".join(
                    (melhor.get("CONTAGENS") or []) + (melhor.get("PCT_INFESTACAO") or []))[:200]}
    if out["LINKS_DE_DADOS"]:
        exts = sorted({x["EXT"].upper() for x in out["LINKS_DE_DADOS"]})
        return {**base, "VEREDITO": "TABELA_EM_FICHEIRO", "TABELA_EM": out["LINKS_DE_DADOS"][0]["URL"],
                "FORMATO_DA_TABELA": "/".join(exts),
                "PORQUE": "links para %s com nome de monitorizacao (nao abertos aqui): %s" % (
                    "/".join(exts), out["LINKS_DE_DADOS"][0]["ANCORA"][:80])}
    if any(p.get("LOGIN") for p in html[1:]) or (html and html[0].get("LOGIN") and len(html) == 1):
        return {**base, "VEREDITO": "LOGIN", "TABELA_EM": None, "FORMATO_DA_TABELA": None,
                "PORQUE": "a pagina de monitorizacao pede autenticacao"}
    if html:
        return {**base, "VEREDITO": "SO_BOLETIM", "TABELA_EM": None, "FORMATO_DA_TABELA": None,
                "PORQUE": "%d paginas lidas, nenhum numero de contagem com data" % len(html)}
    return {**base, "VEREDITO": "NAO_SEI", "TABELA_EM": None, "FORMATO_DA_TABELA": None,
            "PORQUE": "nenhuma pagina HTML lida"}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    if not a.get("lote") or not a.get("bytes"):
        print(__doc__)
        return 2
    import canario as CAN      # noqa: E402
    import rede                # noqa: E402
    lote = json.loads(Path(a["lote"]).read_text(encoding="utf-8"))
    sem = set(filter(None, a.get("sem", "").split(",")))      # --sem=LM-03,LM-04: dominios ja visitados hoje
    res = [medir(x, CAN.buscar, lambda: rede.portao_de_egresso("IT"), Path(a["bytes"]))
           for x in lote["ALVOS"] if x["ID"] not in sem]
    out = {"DATASET": "CONTAGENS-MEDIDAS", "GERADO_EM": _agora(), "PEDIDOS": sum(r["PEDIDOS"] for r in res),
           "POR_VEREDITO": {v: sum(1 for r in res if r["VEREDITO"] == v) for v in sorted({r["VEREDITO"] for r in res})},
           "ALVOS": res}
    Path(a.get("saida", "CONTAGENS-MEDIDAS.json")).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                                               encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("PEDIDOS", "POR_VEREDITO")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
