"""AS RECEITAS DAS FONTES — censo do defeito e proposta com prova (missao 6-PREP-d).

PROPOSTA, NAO APLICACAO. Nao escreve em italy_contracts_curator.json, admissao/,
retrato_html.py, limiares, fila ou livros. Escreve so curadoria/PROPOSTA-RECEITAS-V1.json.

    py scripts/receitas/censo_e_proposta.py --contratos=<copia do livro vivo> --coorte=<coorte.json>

Entradas (so leitura):
  · contratos: COPIA de source-curator-service-v1/curadoria/italy_contracts_curator.json
    (o bot escreve o vivo; nunca se le o vivo directamente)
  · paginas com veredito humano-proposto:
      scripts/detector_capa/GABARITO-CAPA-V1.json  (bytes em ~/detector-capa-gabarito/)
      scripts/receitas/ROTULOS-PAGINAS-RECEITAS-V1.json  (bytes em ~/receitas-paginas/)

DEFEITOS (medidos, varios por fonte):
  SEM_CONTRATO              a fonte nao tem contrato no livro vivo
  INDEX_APONTA_MATERIA      a pagina do INDEX_URL foi lida e e uma materia
  PADRAO_NAO_CASA_MATERIA   ha materia confirmada da fonte e o LINK_PATTERN nao a casa
  PADRAO_NAO_CASA_NADA      o LINK_PATTERN nao casa nenhum link da pagina de entrada (o EMPTY_LIST)
  PADRAO_GENERICO           o LINK_PATTERN casa capa: o indice, navegacao sintetica ou capa conhecida
  NAO_SEI_SEM_PAGINA        sem pagina lida desta fonte: nao se classifica

REGRA DA PROPOSTA DE LINK_PATTERN (so com prova):
  1. precisa de >= 1 MATERIA confirmada da fonte e da pagina de entrada (bytes);
  2. esqueleto da morada da materia: segmento numerico -> NUM, segmento com >= 2
     hifens ou > 25 caracteres -> SLUG, o resto literal; chaves da query mantidas;
  3. familia = links da pagina de entrada com o mesmo esqueleto; tem de ter >= 2;
  4. o padrao construido tem de passar o GUARDA (e_generico) — senao, NAO SEI.
Nenhum padrao nasce sem uma materia lida. Trava 3 do dono: nao inventar rotas.
"""
from __future__ import annotations

import html as H
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urljoin, urlparse

RAIZ = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).resolve().parent
HOME = Path.home()
SAIDA = RAIZ / "curadoria" / "PROPOSTA-RECEITAS-V1.json"

NAV_SINTETICA = ["/", "/contatti", "/contatti/", "/chi-siamo", "/chi-siamo/", "/privacy",
                 "/privacy-policy/", "/category/notizie", "/tag/agricoltura", "/page/2",
                 "/news/", "/notizie/", "/eventi/", "/search?q=x", "/it/", "/home"]
NAVEGACAO = re.compile(r"(contatt|contact|chi-?siamo|about|archivi|categor|/page/\d|pagina|"
                       r"calendari|/tag/|privacy|cookie|login|/search|/cerca|/feed)", re.I)
TETO_FRACCAO = 0.80


# ── O GUARDA ────────────────────────────────────────────────────────────────
def e_generico(padrao: str, index_url: str, links: list[str], capas: list[str]) -> str | None:
    """Devolve o motivo por que o padrao e GENERICO (defeito), ou None.

    Um padrao que casa a capa nao separa nada: e o mesmo defeito do molde
    WordPress medido na 6-PREP-c, e «.*» e a forma extrema dele."""
    try:
        rx = re.compile(padrao)
    except re.error as ex:
        return f"nao compila: {ex}"
    base = f"{urlparse(index_url).scheme}://{urlparse(index_url).netloc}"
    if rx.match(index_url):
        return "casa o INDEX_URL"
    for s in NAV_SINTETICA:
        if rx.match(base + s):
            return f"casa navegacao sintetica {s}"
    for c in capas:
        if rx.match(c):
            return f"casa uma capa conhecida: {c}"
    for l in links:
        if NAVEGACAO.search(l) and rx.match(l):
            return f"casa um link de navegacao da entrada: {l}"
    if links:
        f = sum(1 for l in links if rx.match(l)) / len(links)
        if f > TETO_FRACCAO:
            return f"casa {f:.0%} dos links da entrada (teto {TETO_FRACCAO:.0%})"
    return None


# ── ESQUELETO E PADRAO ──────────────────────────────────────────────────────
_SLUG = r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)+"


def _tipo(seg: str) -> str:
    base = re.sub(r"\.(html?|php|aspx?)$", "", seg, flags=re.I)
    if re.fullmatch(r"\d+", base):
        return "NUM"
    if base.count("-") + base.count("_") >= 2 or len(base) > 25:
        return "SLUG"
    return "LIT:" + seg


def esqueleto(url: str) -> tuple:
    u = urlparse(url)
    segs = tuple(_tipo(s) for s in u.path.strip("/").split("/") if s)
    q = tuple(sorted((k, "NUM" if re.fullmatch(r"\d+", v) else "V") for k, v in parse_qsl(u.query)))
    return (u.netloc.lower().removeprefix("www."), segs, q)


def padrao_de(esq: tuple, url_exemplo: str, familia: list[str] | None = None) -> str:
    """Posicao com o MESMO valor em toda a familia fica literal: «news-e-eventi»
    tem dois hifens mas e o nome da seccao, nao o titulo. So varia o que varia."""
    host, segs, q = esq
    fam = [url_exemplo] + list(familia or [])
    paths = [[x for x in urlparse(u).path.strip("/").split("/") if x] for u in fam]
    segs = tuple("LIT:" + paths[0][i] if s == "SLUG" and len(fam) > 1 and len({pp[i] for pp in paths}) == 1
                 else s for i, s in enumerate(segs))
    ext = re.search(r"\.(html?|php|aspx?)$", urlparse(url_exemplo).path.rstrip("/"), re.I)
    partes = []
    for i, s in enumerate(segs):
        ultimo = i == len(segs) - 1
        if s == "NUM":
            p = r"\d+"
        elif s == "SLUG":
            p = _SLUG
        else:
            p = re.escape(s[4:])
            ultimo = False
        if ultimo and s != "NUM" and ext:
            p += re.escape(ext.group(0))
        partes.append(p)
    rx = r"^https?://(www\.)?" + re.escape(host) + "/" + "/".join(partes) + "/?"
    if q:
        rx += r"\?" + "&".join(re.escape(k) + "=" + (r"\d+" if t == "NUM" else r"[^&]+") for k, t in q)
    return rx + "$"


def links_de(base: str, b: bytes) -> list[str]:
    txt = b.decode("utf-8", "replace")
    host = urlparse(base).netloc.lower().removeprefix("www.")
    out = set()
    for m in re.finditer(r'<a\b[^>]*href=["\']([^"\'#]+)["\']', txt, re.I):
        try:
            u = urljoin(base, H.unescape(m.group(1)).strip())
            if urlparse(u).netloc.lower().removeprefix("www.") == host:
                out.add(u)
        except ValueError:
            continue
    return sorted(out)


# ── AS PAGINAS COM VEREDITO ────────────────────────────────────────────────
def paginas() -> list[dict]:
    out = []
    g = json.loads((RAIZ / "scripts/detector_capa/GABARITO-CAPA-V1.json").read_text(encoding="utf-8"))
    pg = HOME / "detector-capa-gabarito"
    for p in g["PAGINAS"]:
        out.append({"SOURCE_ID": p["SOURCE_ID"], "URL": p["URL"], "VEREDITO": p["VEREDITO"],
                    "PAPEL": p["GRUPO"], "BYTES": pg / p["FICHEIRO"], "ORIGEM": f"gabarito#{p['ID']}"})
    # as paginas VAZIAS/DUPLICADAS do gabarito nao contam como veredito, mas a
    # pagina de entrada delas ainda da os links
    for p in g["FORA_DA_CONTAGEM"]:
        if p["GRUPO"] == "CAPA_INDICE":
            out.append({"SOURCE_ID": p["SOURCE_ID"], "URL": p["URL"], "VEREDITO": p["VEREDITO"],
                        "PAPEL": "CAPA_INDICE", "BYTES": pg / p["FICHEIRO"], "ORIGEM": f"gabarito#{p['ID']}"})
    pr = HOME / "receitas-paginas"
    mf = pr / "MANIFESTO.json"
    if mf.exists():
        m = json.loads(mf.read_text(encoding="utf-8"))["PAGINAS"]
        rot = json.loads((AQUI / "ROTULOS-PAGINAS-RECEITAS-V1.json").read_text(encoding="utf-8"))["ROTULOS"]
        for i, p in enumerate(m):
            v, _ = rot[str(i)]
            out.append({"SOURCE_ID": p["SOURCE_ID"], "URL": p["URL"], "VEREDITO": v,
                        "PAPEL": p["PAPEL_CANDIDATO"], "BYTES": pr / p["FICHEIRO"], "ORIGEM": f"receitas#{i}"})
    return out


# ── CENSO + PROPOSTA ───────────────────────────────────────────────────────
def por_fonte(sid: str, c: dict | None, pags: list[dict], capas_do_host: list[str]) -> dict:
    linha = {"SOURCE_ID": sid, "DEFEITOS": [], "PROPOSTAS": []}
    if not c:
        linha["DEFEITOS"].append("SEM_CONTRATO")
        return linha
    aq = c.get("ACQUISITION") or {}
    idx, lp = aq.get("INDEX_URL", ""), aq.get("LINK_PATTERN")
    linha.update(INDEX_URL=idx, LINK_PATTERN=lp)
    if not pags:
        linha["DEFEITOS"].append("NAO_SEI_SEM_PAGINA")
        return linha
    entrada = next((p for p in pags if p["PAPEL"] == "CAPA_INDICE" and p["BYTES"].exists()), None)
    mats = [p for p in pags if p["VEREDITO"] == "MATERIA"]
    links = links_de(idx, entrada["BYTES"].read_bytes()) if entrada else []
    capas = sorted({p["URL"] for p in pags if p["VEREDITO"] == "CAPA"} | set(capas_do_host))
    if entrada and entrada["VEREDITO"] == "MATERIA":
        linha["DEFEITOS"].append("INDEX_APONTA_MATERIA")
    if not lp:
        linha["DEFEITOS"].append("PADRAO_AUSENTE")
    else:
        rx = re.compile(lp)
        if any(not rx.match(m["URL"]) for m in mats):
            linha["DEFEITOS"].append("PADRAO_NAO_CASA_MATERIA")
        if entrada and links and not any(rx.match(l) for l in links):
            linha["DEFEITOS"].append("PADRAO_NAO_CASA_NADA")
        g = e_generico(lp, idx, links, capas)
        if g:
            linha["DEFEITOS"].append("PADRAO_GENERICO")
            linha["GENERICO_PORQUE"] = g
    if not linha["DEFEITOS"]:
        linha["DEFEITOS"].append("SEM_DEFEITO_MEDIDO")

    # a proposta: so com materia lida E entrada com links
    if not set(linha["DEFEITOS"]) & {"PADRAO_NAO_CASA_MATERIA", "PADRAO_NAO_CASA_NADA",
                                      "PADRAO_GENERICO", "PADRAO_AUSENTE"}:
        linha["SEM_PROPOSTA"] = "o padrao actual nao mostrou defeito medido: nao se mexe no que funciona"
        return linha
    if not mats:
        linha["SEM_PROPOSTA"] = "NAO SEI: nenhuma materia confirmada desta fonte"
        return linha
    if not links:
        linha["SEM_PROPOSTA"] = "NAO SEI: sem pagina de entrada legivel para medir a familia"
        return linha
    candidatos = []
    for m in mats:
        esq = esqueleto(m["URL"])
        fam = [l for l in links if esqueleto(l) == esq]
        novo = padrao_de(esq, m["URL"], fam)
        if len(set(fam) | {m["URL"]} & set(links)) < 2 and len(fam) < 2:
            candidatos.append((None, f"familia com {len(fam)} link(s) na entrada para {m['URL']}: < 2"))
            continue
        g = e_generico(novo, idx, links, capas)
        if g:
            candidatos.append((None, f"padrao derivado recusado pelo guarda: {g}"))
            continue
        candidatos.append((novo, None))
    # a proposta tem de casar TODAS as materias confirmadas da fonte, senao NAO SEI
    bons_todos = [n for n, _ in candidatos if n]
    if bons_todos:
        alt = "|".join(f"(?:{b})" for b in sorted(set(bons_todos)))
        falham = [m["URL"] for m in mats if not re.match(alt, m["URL"])]
        if falham:
            linha["SEM_PROPOSTA"] = ("NAO SEI: o padrao derivado nao casa a propria materia "
                                     f"confirmada {falham[0]} (esqueleto nao reproduzivel)")
            return linha
    bons = sorted({n for n, _ in candidatos if n})
    if not bons:
        linha["SEM_PROPOSTA"] = "NAO SEI: " + "; ".join(p for _, p in candidatos if p)
        return linha
    novo = "|".join(f"(?:{b})" for b in bons) if len(bons) > 1 else bons[0]
    rx_a = re.compile(lp) if lp else None
    rx_n = re.compile(novo)

    def conta(rx, urls):
        return sum(1 for u in urls if rx and rx.match(u))
    linha["PROPOSTAS"].append({
        "CAMPO": "ACQUISITION.LINK_PATTERN", "ANTES": lp, "DEPOIS": novo,
        "PROVA": {
            "MATERIAS_CONFIRMADAS": [m["URL"] for m in mats],
            "MATERIAS_CASADAS_ANTES": f"{conta(rx_a, [m['URL'] for m in mats])}/{len(mats)}",
            "MATERIAS_CASADAS_DEPOIS": f"{conta(rx_n, [m['URL'] for m in mats])}/{len(mats)}",
            "CAPAS_CASADAS_ANTES": f"{conta(rx_a, capas)}/{len(capas)}",
            "CAPAS_CASADAS_DEPOIS": f"{conta(rx_n, capas)}/{len(capas)}",
            "LINKS_DA_ENTRADA_CASADOS_ANTES": f"{conta(rx_a, links)}/{len(links)}",
            "LINKS_DA_ENTRADA_CASADOS_DEPOIS": f"{conta(rx_n, links)}/{len(links)}",
            "EXEMPLOS_DEPOIS": [l for l in links if rx_n.match(l)][:5],
            "PAGINA_DE_ENTRADA": entrada["ORIGEM"]}})
    return linha


FAMILIA_MINIMA_DO_INDICE = 10


def propor_indice(linha: dict, pags: list[dict], todas: list[dict]) -> None:
    """INDEX_URL novo so com prova: a pagina candidata foi BUSCADA
    (scripts/receitas/provar_indices.py) e tem >= 10 links com o esqueleto de
    uma materia CONFIRMADA do mesmo site. Senao, NAO SEI."""
    if "INDEX_APONTA_MATERIA" not in linha["DEFEITOS"]:
        return
    mf = HOME / "receitas-paginas" / "indices" / "MANIFESTO-INDICES.json"
    cand = {l["SOURCE_ID"]: l for l in json.loads(mf.read_text(encoding="utf-8"))} if mf.exists() else {}
    c = cand.get(linha["SOURCE_ID"])
    if not c or not c.get("FICHEIRO"):
        linha["SEM_PROPOSTA_INDEX"] = "NAO SEI: nenhuma pagina candidata buscada"
        return
    host = urlparse(c["URL"]).netloc.lower().removeprefix("www.")
    mats = [p["URL"] for p in todas if p["VEREDITO"] == "MATERIA"
            and urlparse(p["URL"]).netloc.lower().removeprefix("www.") == host]
    links = links_de(c["URL"], Path(c["FICHEIRO"]).read_bytes())
    melhor = max((sum(1 for l in links if esqueleto(l) == esqueleto(m)) for m in mats), default=0)
    prova = {"PAGINA_BUSCADA": c["URL"], "SHA256": c.get("SHA256"), "EGRESSO": c.get("EGRESSO"),
             "HTML_KIND": (c.get("RETRATO") or {}).get("HTML_KIND"), "LINKS": len(links),
             "LINKS_COM_FORMA_DE_MATERIA_CONFIRMADA": melhor, "MINIMO": FAMILIA_MINIMA_DO_INDICE}
    if melhor < FAMILIA_MINIMA_DO_INDICE:
        linha["SEM_PROPOSTA_INDEX"] = f"NAO SEI: a candidata tem {melhor} links com forma de materia (< {FAMILIA_MINIMA_DO_INDICE})"
        linha["PROVA_INDEX_FRACA"] = prova
        return
    linha["PROPOSTAS"].append({"CAMPO": "ACQUISITION.INDEX_URL", "ANTES": linha.get("INDEX_URL"),
                               "DEPOIS": c["URL"], "PROVA": prova})


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    contratos = {f["SOURCE_ID"]: f for f in json.loads(
        Path(arg["contratos"]).read_text(encoding="utf-8"))["FONTES"]}
    coorte = json.loads(Path(arg["coorte"]).read_text(encoding="utf-8"))
    pags = paginas()
    capas_host: dict[str, list[str]] = {}
    for p in pags:
        if p["VEREDITO"] == "CAPA":
            capas_host.setdefault(urlparse(p["URL"]).netloc.lower().removeprefix("www."), []).append(p["URL"])
    linhas = []
    for sid in coorte["TODOS"]:
        c = contratos.get(sid)
        idx = ((c or {}).get("ACQUISITION") or {}).get("INDEX_URL", "")
        host = urlparse(idx).netloc.lower().removeprefix("www.")
        linhas.append(por_fonte(sid, c, [p for p in pags if p["SOURCE_ID"] == sid],
                                capas_host.get(host, [])))
        propor_indice(linhas[-1], [p for p in pags if p["SOURCE_ID"] == sid], pags)
    for l in linhas:
        l["GRUPOS"] = [g for g in ("MICRO", "E45", "GOLD") if l["SOURCE_ID"] in coorte[g]]
    d = {"DATASET": "PROPOSTA-RECEITAS-V1", "MISSAO": "6-PREP-d",
         "ESTADO": "PROPOSTA — NAO APLICADA. Aplicacao depois da unificacao (M5), pelo coordenador, com o dono.",
         "CONTRATOS_LIDOS_DE": arg["contratos"], "COORTE": len(linhas), "FONTES": linhas}
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    from collections import Counter
    print("COORTE", len(linhas))
    print("DEFEITOS", dict(Counter(x for l in linhas for x in l["DEFEITOS"])))
    from collections import Counter as _C
    print("POR_CAMPO", dict(_C(p["CAMPO"] for l in linhas for p in l["PROPOSTAS"])))
    print("PROPOSTAS", sum(1 for l in linhas if l["PROPOSTAS"]),
          "SEM_PROPOSTA", sum(1 for l in linhas if not l["PROPOSTAS"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
