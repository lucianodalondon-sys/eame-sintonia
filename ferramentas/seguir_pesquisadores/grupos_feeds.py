# -*- coding: utf-8 -*-
"""PESQUISADORES-CONTEUDO (D92) · 2) paginas PUBLICAS de grupos de pesquisa e laboratorios, com feed.

    py ferramentas/seguir_pesquisadores/grupos_feeds.py --plano  --fila=<FONTES-CANDIDATAS.json> --pessoas=PESSOAS-ORDENADAS.json --fora=FORA-DO-MUR.json --saida=<pasta>
    py ferramentas/seguir_pesquisadores/grupos_feeds.py --rodada --autorizado --saida=<pasta> [--cnr-liberado]
    py ferramentas/seguir_pesquisadores/grupos_feeds.py --candidatar --saida=<pasta> --fila=<COPIA da fila>
    (--seco --fixtures=<pasta> faz a rodada com paginas inventadas, sem rede)

As SEMENTES sao as paginas de departamento/instituto que JA estao na fila de candidatas (o endereco le-se
la, pelo CANDIDATA_ID; nada se inventa), por ordem de quantos pesquisadores nossos estao em cada casa.
Da semente segue-se so a ligacao cujo TEXTO ou caminho diz grupo/laboratorio (ate 2 niveis). De cada pagina
tira-se:
  * o FEED DECLARADO: <link rel="alternate" type="application/rss+xml|atom+xml"> ou uma ligacao que se
    diz RSS/feed. Nunca se adivinha «/feed»: feed que a pagina nao declara nao existe aqui;
  * os canais publicos (a classificacao da seguir.py: LinkedIn /in/ fora, e-mail/telefone nunca);
  * os sobrenomes dos nossos pesquisadores DAQUELA casa que a pagina escreve (liga grupo a pessoa, nao funde).

Paginas comuns: robots RESPEITADO (D91), 5 pedidos por dominio por rodada e por 24 h (contador.py), 3 s,
portao IT antes e depois, bytes com sha256 fora do Git. CNR: so com --cnr-liberado (coordenacao 26/09 10:13).
"""
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import seguir as S          # noqa: E402
import pessoas as PE        # noqa: E402
import contador as CT       # noqa: E402

# CANDIDATA_ID -> a casa (a chave do MUR, ou FEM/CREA/CNR/LAIMBURG). O endereco vem da fila.
SEMENTES = {
    "CAND-0263": "TORINO", "CAND-0261": "MILANO", "CAND-0262": "PADOVA", "CAND-1031": "PISA",
    "CAND-1018": "Politecnica delle MARCHE", "CAND-0020": "Napoli Federico II", "CAND-0024": "CATANIA",
    "CAND-1019": "FIRENZE", "CAND-1021": "BOLOGNA", "CAND-1023": "PERUGIA", "CAND-1032": "FOGGIA",
    "CAND-1025": "SASSARI", "CAND-1030": "TUSCIA", "CAND-1046": "PALERMO",
    "CAND-0019": "Mediterranea di REGGIO CALABRIA", "CAND-0027": "Libera Università di BOLZANO",
    "CAND-1029": "VERONA", "CAND-1037": "FEM", "CAND-0258": "CREA", "CAND-0026": "LAIMBURG",
    "CAND-0996": "CNR", "CAND-1000": "CNR", "CAND-1001": "CNR", "CAND-0995": "CNR",
}
SEM_SEMENTE = ["BARI (DiSSPA)", "Cattolica del Sacro Cuore (DIPROVES)", "CNR IPSP"]   # nenhum livro nosso tem o endereco
GRUPO_RX = re.compile(r"\b(laborator\w*|gruppi? di ricerca|research groups?|linee di ricerca|unit[aà] di ricerca|"
                      r"team di ricerca|lab)\b", re.I)
FEED_TIPOS = ("application/rss+xml", "application/atom+xml")
FEED_A_RX = re.compile(r"(\.rss$|/rss/?$|/feed/?$|atom\.xml$|rss\.xml$)", re.I)
PROFUNDIDADE = 2


class _Pagina(HTMLParser):
    def __init__(self, base):
        super().__init__()
        self.base, self.ancoras, self.feeds, self.titulo, self.texto = base, [], [], "", []
        self._a, self._t, self._no_titulo = None, [], False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "link" and "alternate" in (a.get("rel") or "").lower() and (a.get("type") or "").lower() in FEED_TIPOS \
                and a.get("href"):
            self.feeds.append(S.urllib.parse.urljoin(self.base, a["href"]))
        elif tag == "a" and a.get("href") and not a["href"].startswith(("mailto:", "tel:", "javascript:", "#")):
            self._a, self._t = S.urllib.parse.urljoin(self.base, a["href"]), []
        elif tag == "title":
            self._no_titulo = True

    def handle_data(self, data):
        if self._no_titulo:
            self.titulo += data
        if self._a is not None:
            self._t.append(data)
        self.texto.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._a is not None:
            txt = " ".join("".join(self._t).split())
            self.ancoras.append((self._a, txt))
            if FEED_A_RX.search(self._a.split("?")[0]) or txt.strip().upper() in ("RSS", "FEED RSS", "ATOM"):
                self.feeds.append(self._a)
            self._a = None
        elif tag == "title":
            self._no_titulo = False


def ler_pagina(html: str, base: str) -> _Pagina:
    p = _Pagina(base)
    try:
        p.feed(html)
    except Exception:                                                     # noqa: BLE001
        pass
    p.feeds = list(dict.fromkeys(p.feeds))
    return p


# ═══════════════════════════════════ sementes e alvos (sem rede)
def alvos_por_casa(pessoas: list, fora: list) -> dict:
    out = {}
    for p in pessoas:
        if p.get("PRIORIDADE") and p.get("UNIVERSIDADE"):
            out.setdefault(p["UNIVERSIDADE"], set()).add(PE.partir_nome_mur(p["NOME"])[0])
    for p in fora:
        for c in {c.split("/")[0] for c in p.get("CASAS") or []}:
            if p.get("PAR_DO_CASCO_RECENTE") or p.get("PEDIDA_PELO_NOME"):
                out.setdefault(c, set()).add(PE.chave(p["NOME"]).split()[-1])
    return {k: sorted(v) for k, v in out.items()}


def estado_novo(fila_cand: list, alvos: dict) -> dict:
    por_id = {c["CANDIDATA_ID"]: c for c in fila_cand}
    sementes = [{"CANDIDATA_ID": k, "CASA": v, "URL": por_id[k]["URL"], "NOME": por_id[k]["NOME"],
                 "ALVOS": len(alvos.get(v, []))} for k, v in SEMENTES.items() if k in por_id]
    sementes.sort(key=lambda s: -s["ALVOS"])
    return {"DATASET": "PESQUISADORES-CONTEUDO-GRUPOS", "ALVOS": alvos, "SEMENTES": sementes,
            "SEMENTES_EM_FALTA": [k for k in SEMENTES if k not in por_id] + SEM_SEMENTE,
            "FILA": [{"URL": s["URL"], "PAPEL": "SEMENTE", "PROF": 0, "CASA": s["CASA"], "SEMENTE": s["CANDIDATA_ID"]}
                     for s in sementes],
            "FEITOS": [], "GRUPOS": [], "FEEDS_DAS_SEMENTES": {}, "RODADAS": 0}


# ═══════════════════════════════════ a rodada
def rodada(e: dict, t: "S.Transporte", cnr: bool) -> dict:
    fila, resto, lidos = list(e["FILA"]), [], {f["URL"] for f in e["FEITOS"]}
    n = {"PAGINAS": 0, "GRUPOS_NOVOS": 0, "FEEDS": 0}
    while fila:
        item = fila.pop(0)
        url = item["URL"]
        if url in lidos:
            continue
        if item["CASA"] == "CNR" and not cnr:
            resto.append(item)                   # fechado pela coordenacao: fica na fila, nao se pede
            continue
        d = S.dominio(url)
        if t.conta[d] >= S.TETO or (t.contador is not None and not t.contador.livres(d)):
            resto.append(item)
            continue
        st, b = t.get(url, "%s %s" % (item["PAPEL"], item["CASA"]))
        if b is None:
            if t.registo and t.registo[-1]["RESULTADO"] in S.TETOS:
                resto.append(item)
            else:
                e["FEITOS"].append(dict(item, RESULTADO="NAO_ABERTA", HTTP=st, MOTIVO=(t.registo[-1]["RESULTADO"] if t.registo else None)))
                lidos.add(url)
            continue
        lidos.add(url)
        n["PAGINAS"] += 1
        pg = ler_pagina(b.decode("utf-8", "replace"), url)
        e["FEITOS"].append(dict(item, RESULTADO="LIDA", HTTP=st))
        if item["PAPEL"] == "SEMENTE" and pg.feeds:
            e["FEEDS_DAS_SEMENTES"][url] = pg.feeds
        if item["PAPEL"] == "GRUPO":
            texto = PE.chave(" ".join(pg.texto))
            citados = [s for s in e["ALVOS"].get(item["CASA"], []) if len(s) >= 4 and re.search(r"\b%s\b" % re.escape(s), texto)]
            canais, fora = [], []
            for href, _txt in pg.ancoras:
                plat, tipo, entra = S.classificar(href)
                if plat in ("PAGINA_INSTITUCIONAL_OU_PESSOAL", "ORCID", "GOOGLE_SCHOLAR"):
                    continue
                (canais if entra else fora).append({"URL": href, "PLATAFORMA": plat, "TIPO": tipo})
            e["GRUPOS"].append({"URL": url, "TITULO": " ".join(pg.titulo.split())[:120], "TEXTO_DA_LIGACAO": item.get("TEXTO"),
                                "CASA": item["CASA"], "SEMENTE": item["SEMENTE"], "LIGADO_EM": item.get("DE"),
                                "FEEDS": pg.feeds, "CANAIS": canais, "NAO_ENTRAM": fora, "PESQUISADORES_CITADOS": citados})
            n["GRUPOS_NOVOS"] += 1
            n["FEEDS"] += len(pg.feeds)
        if item["PROF"] < PROFUNDIDADE:
            for href, txt in pg.ancoras:
                if S.dominio(href) != d or href in lidos:
                    continue                     # so dentro da mesma casa
                if GRUPO_RX.search(txt) or GRUPO_RX.search(S.urllib.parse.urlparse(href).path.replace("-", " ").replace("_", " ")):
                    fila.append({"URL": href, "PAPEL": "GRUPO", "PROF": item["PROF"] + 1, "CASA": item["CASA"],
                                 "SEMENTE": item["SEMENTE"], "DE": url, "TEXTO": txt[:80]})
    vistos, prox = {f["URL"] for f in e["FEITOS"]}, []
    for x in resto:
        if x["URL"] not in vistos and x["URL"] not in {y["URL"] for y in prox}:
            prox.append(x)
    e["FILA"] = prox
    e["RODADAS"] += 1
    n["NA_FILA"] = len(prox)
    return n


# ═══════════════════════════════════ candidatas (numa COPIA da fila)
def candidatar(e: dict, fila: Path) -> dict:
    sys.path.insert(0, str(S.RAIZ / "candidatas"))
    import fonte_nova as FN
    FN.FILA = fila
    feitas = []
    for g in e["GRUPOS"]:
        base = "grupo/laboratorio publico %s (%s), ligado da pagina oficial da casa" % (g["URL"], g["CASA"])
        if g["FEEDS"]:
            linha = FN.registar("CIENCIA", "IT", "%s — grupo de pesquisa" % (g["TITULO"] or g["URL"])[:90], g["URL"],
                                "D92: materiais de pesquisadores (%s) para a Sala: o grupo publica por feed" % g["CASA"],
                                "PESQUISADORES-CONTEUDO (ferramentas/seguir_pesquisadores/grupos_feeds.py)", g["LIGADO_EM"] or g["URL"],
                                "FEED_DECLARADO=%s; PESQUISADORES_CITADOS=%s; PAIS_PROVA=casa italiana; ROBOTS=respeitado; %s"
                                % (" ".join(g["FEEDS"]), ",".join(g["PESQUISADORES_CITADOS"]) or "nenhum", base))
            feitas.append({"CANDIDATA_ID": linha["CANDIDATA_ID"], "TIPO": "CIENCIA", "URL": g["URL"], "FEED": g["FEEDS"]})
        for c in g["CANAIS"]:
            linha = FN.registar(c["TIPO"], "IT", "%s — %s" % ((g["TITULO"] or g["URL"])[:80], c["PLATAFORMA"]), c["URL"],
                                "D92: canal publico de um grupo de pesquisa (%s)" % g["CASA"],
                                "PESQUISADORES-CONTEUDO (ferramentas/seguir_pesquisadores/grupos_feeds.py)", g["URL"],
                                "LIGADO NA PAGINA DO GRUPO; ROTA_HOJE=%s; %s" % (S.ROTA_HOJE.get(c["PLATAFORMA"], "NAO SEI"), base))
            feitas.append({"CANDIDATA_ID": linha["CANDIDATA_ID"], "TIPO": linha["TIPO"], "URL": c["URL"]})
    return {"CANDIDATAS": feitas}


# ═══════════════════════════════════ linha de comando
def _ler(c):
    d = json.loads(Path(c).read_text(encoding="utf-8"))
    return d.get("PESSOAS") or d.get("CANDIDATAS") or [] if isinstance(d, dict) else d


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    saida = Path(arg["saida"])
    arq = saida / "ESTADO-GRUPOS.json"
    if "--plano" in argv:
        if not arq.exists():
            saida.mkdir(parents=True, exist_ok=True)
            e = estado_novo(_ler(arg["fila"]), alvos_por_casa(_ler(arg["pessoas"]), _ler(arg["fora"]) if "fora" in arg else []))
            arq.write_text(json.dumps(e, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        e = json.loads(arq.read_text(encoding="utf-8"))
        dom = Counter(S.dominio(s["URL"]) for s in e["SEMENTES"])
        print(json.dumps({"SEMENTES": len(e["SEMENTES"]), "DOMINIOS": len(dom), "CNR_FECHADAS": sum(1 for s in e["SEMENTES"] if s["CASA"] == "CNR"),
                          "EM_FALTA": e["SEMENTES_EM_FALTA"],
                          "ORDEM": ["%s (%d alvos) %s" % (s["CASA"], s["ALVOS"], s["URL"]) for s in e["SEMENTES"]]},
                         ensure_ascii=False, indent=1))
        return 0
    e = json.loads(arq.read_text(encoding="utf-8"))
    if "--candidatar" in argv:
        print(json.dumps({"CANDIDATAS": len(candidatar(e, Path(arg["fila"]))["CANDIDATAS"])}, ensure_ascii=False))
        return 0
    if "--rodada" not in argv:
        print(__doc__)
        return 2
    pasta = saida / ("RODADA-%02d" % (e["RODADAS"] + 1))
    if "--seco" in argv:
        resp = json.loads((Path(arg["fixtures"]) / "RESPOSTAS-GRUPOS.json").read_text(encoding="utf-8"))

        def falso(url):
            if url not in resp:
                raise S.urllib.error.HTTPError(url, 404, "sem fixture", {}, None)
            return 200, resp[url].encode("utf-8")
        t = S.Transporte(pasta, buscar=falso, pausa=0, contador=CT.Contador24h(saida / "CONTADOR-24H.json"))
    else:
        if "--autorizado" not in argv:
            print("RECUSADO: sai a rede; so com --autorizado (quem corre e o coordenador)")
            return 2
        pasta.mkdir(parents=True, exist_ok=True)
        if not S.portao(pasta, "ANTES"):
            print("PAROU: portao de egresso nao e IT (antes)")
            return 3
        t = S.Transporte(pasta, contador=CT.Contador24h(Path(arg.get("contador") or CT.CONTADOR_PADRAO)))
    r = rodada(e, t, "--cnr-liberado" in argv)
    arq.write_text(json.dumps(e, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "PEDIDOS.json").write_text(json.dumps({"PEDIDOS": t.registo, "POR_DOMINIO": dict(t.conta)},
                                                   ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if "--seco" not in argv and not S.portao(pasta, "DEPOIS"):
        print("PAROU: portao de egresso nao e IT (depois)")
        return 3
    print(json.dumps(dict(r, PEDIDOS_POR_DOMINIO=dict(t.conta)), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
