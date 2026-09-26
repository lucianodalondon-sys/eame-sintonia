# -*- coding: utf-8 -*-
"""PESQ-FORA-DO-MUR · as listas OFICIAIS de pessoal da FEM, do CREA e do CNR, lidas por rodadas.

    py ferramentas/seguir_pesquisadores/listas_oficiais.py --plano --alvos=FORA-DO-MUR.json
    py ferramentas/seguir_pesquisadores/listas_oficiais.py --rodada --casa=FEM|CREA|CNR --alvos=... \
        --saida=<pasta fora do Git> --autorizado            [CNR: so com --cnr-liberado]
    py ferramentas/seguir_pesquisadores/listas_oficiais.py --seco --fixtures=<pasta> --casa=... --alvos=... --saida=...
    py ferramentas/seguir_pesquisadores/listas_oficiais.py --candidatar --saida=<pasta> --fila=<COPIA da fila>

Nao varre o site: parte da(s) pagina(s) de LISTA oficial de cada casa e so abre o PERFIL das pessoas
que ja estao no cruzamento com as obras (FORA-DO-MUR.json: sobrenome + inicial no texto da ligacao).
Do perfil tira: o papel/unidade que a propria pagina escreve e os links publicos (LinkedIn, YouTube,
X, Bluesky, ...; a classificacao e a de `seguir.classificar`: LinkedIn /in/ fica FORA). Nunca e-mail,
telefone, contactos. O que nao se conhece da casa (a pagina de lista da FEM) DESCOBRE-SE a partir da
pagina de entrada oficial, pelo texto das ligacoes — nao se inventa endereco.

Uma FILA por casa (ESTADO-<CASA>.json) guarda o que falta: cada rodada tira dela o que cabe no teto
(5 pedidos por dominio registavel, contando o robots) e grava o resto para a proxima.
⚠️ Todos os institutos do CNR (ipsp.cnr.it, ibbr.cnr.it, ...) sao o MESMO dominio registavel (cnr.it):
dividem os 5 pedidos da rodada. E a coordenacao (26/09 10:13) fechou o CNR na rede: --cnr-liberado.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import seguir as S        # noqa: E402  (o transporte com teto/robots/pausa, o portao, a classificacao)
import pessoas as PE      # noqa: E402  (a normalizacao de nomes)

# O que se sabe de cada casa, e DE ONDE se sabe (medido por quem, ou NAO SEI).
CASAS = {
    "FEM": {
        "ENTRADAS": ["https://www.fmach.it/"],
        "LISTAS": [],                                   # NAO SEI: a descobrir na entrada
        "DESCOBRIR_POR": r"\b(persone|personale|staff|chi siamo|organigramma|ricercator|people|unita|unità)\b",
        "PERFIL": r"fmach\.it/.+",
        "SABIDO": "NAO SEI o formato: a P5 (24/09) pos a FEM na lista de casas a visitar e nao a visitou (VPN fora)",
        "UNIDADES_NO_ESCOPO": "CRI (ricerca) e CTT (trasferimento tecnologico: consulenza tecnica, entomologia, patologia)",
    },
    "CREA": {
        # as paginas dos centros (a prova P4: os perfis so se ligam dali). Todos os enderecos ja estao nos nossos
        # livros: 5 na fila de candidatas, o da viticultura no ramo pessoas-agro-v1 (P4)
        "ENTRADAS": ["https://www.crea.gov.it/web/difesa-e-certificazione",
                     "https://www.crea.gov.it/web/viticoltura-e-enologia",
                     "https://www.crea.gov.it/web/olivicoltura-frutticoltura-e-agrumicoltura",
                     "https://www.crea.gov.it/web/agricoltura-e-ambiente",
                     "https://www.crea.gov.it/cerealicoltura-e-colture-industriali",
                     "https://www.crea.gov.it/orticoltura-e-florovivaismo"],
        "LISTAS": [],
        "DESCOBRIR_POR": r"\b(personale|persone|staff|ricercator|chi siamo|organigramma)\b",
        "PERFIL": r"crea\.gov\.it/web/[^/]+/-/[a-z0-9\-]+$",
        "SABIDO": ("P4 (23/09): perfis em crea.gov.it/web/<centro>/-/<nome>, com campo LinkedIn; NAO estao no sitemap "
                   "(27 mil noticias), so ligados das paginas dos 12 centros (P4 leu 96 perfis em 439 pedidos, antes do "
                   "teto). NAO SEI em que sub-pagina do centro esta a lista: descobre-se pelo texto das ligacoes"),
        "UNIDADES_NO_ESCOPO": "DC (difesa), VE (viticoltura), OFA (olivo/frutta/agrumi), AA, CI (cereali), OF (orticoltura)",
    },
    "CNR": {
        "ENTRADAS": ["https://www.ipsp.cnr.it/", "https://www.ibbr.cnr.it/ibbr/", "https://www.isafom.cnr.it/",
                     "https://www.ispa.cnr.it/"],
        "LISTAS": ["https://ibba.cnr.it/staff-ibba/"],
        "DESCOBRIR_POR": r"\b(people|persone|personale|staff)\b",
        "PERFIL": r"(/info/people/[\w-]+$|/staff/[\w-]+/?$|/people/[\w-]+/?$|/persone/[\w-]+/?$)",
        "SABIDO": ("P5 (24/09): IBBR ~160 pessoas em /ibbr/info/people/<nome>; ISAFOM 91; IBBA 52 fichas /staff/<nome>/ "
                   "(lista em /staff-ibba/) com campo «Linkedin:»; IBE/ISPA 0 perfis sociais; IPSP (o instituto de "
                   "protecao das plantas, o que MAIS importa) respondeu 403 e certificado recusado — sem lista lida"),
        "UNIDADES_NO_ESCOPO": "IPSP (protecao das plantas), IBBR, ISAFOM, ISPA, IBE, IRET, IMAMOTER",
    },
}


def alvos_da_casa(fora: dict, casa: str) -> list:
    return [p for p in fora["PESSOAS"] if any(c.startswith(casa + "/") for c in p.get("CASAS") or [])]


def chaves_de_nome(p: dict) -> list:
    """(sobrenome, inicial) de cada forma do nome da pessoa (OpenAlex)."""
    out = set()
    for n in [p["NOME"]] + list(p.get("OUTROS_NOMES") or []):
        t = PE.chave(n).split()
        if len(t) >= 2:
            out.add((t[-1], t[0][0]))
    return sorted(out)


def casa_o_alvo(texto: str, alvos: list):
    """O alvo cujo sobrenome+inicial aparece no texto da ligacao (e so um). Dois = ambiguo -> None."""
    t = PE.chave(texto).split()
    achados = []
    for a in alvos:
        for sob, ini in chaves_de_nome(a):
            if sob in t and any(w[0] == ini for w in t if w != sob):
                achados.append(a)
                break
    return achados[0] if len(achados) == 1 else None


class _Ancoras(S.HTMLParser):
    def __init__(self, base):
        super().__init__()
        self.base, self.a, self._href, self._txt = base, [], None, []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href, self._txt = dict(attrs).get("href"), []

    def handle_data(self, data):
        if self._href is not None:
            self._txt.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            h = self._href
            if not h.startswith(("mailto:", "tel:", "javascript:", "#")):
                self.a.append((S.urllib.parse.urljoin(self.base, h), " ".join("".join(self._txt).split())))
            self._href = None


def ancoras(html: str, base: str) -> list:
    p = _Ancoras(base)
    try:
        p.feed(html)
    except Exception:                                                  # noqa: BLE001
        pass
    return p.a


def estado_inicial(casa: str) -> dict:
    c = CASAS[casa]
    fila = [{"URL": u, "PAPEL": "ENTRADA"} for u in c["ENTRADAS"]] + [{"URL": u, "PAPEL": "LISTA"} for u in c["LISTAS"]]
    return {"CASA": casa, "FILA": fila, "FEITOS": [], "PERFIS": [], "RODADAS": 0}


def ordem(item: dict):
    """Listas antes de perfis; entre perfis, os pedidos pelo nome e os com mais obra recente do casco primeiro."""
    return (item["PAPEL"] == "PERFIL", [-v for v in item.get("PRIORIDADE") or [0, 0, 0]])


def uma_rodada(casa: str, estado: dict, alvos: list, t: "S.Transporte") -> dict:
    c = CASAS[casa]
    resto, fila = [], list(estado["FILA"])      # o que se descobre na rodada entra na mesma fila (ate ao teto)
    lidos = {f["URL"] for f in estado["FEITOS"]}
    while fila:
        fila.sort(key=ordem)                    # listas antes de perfis; perfis pela prioridade do alvo
        item = fila.pop(0)
        url, papel = item["URL"], item["PAPEL"]
        if url in lidos:
            continue
        lidos.add(url)
        if t.conta[S.dominio(url)] >= S.TETO:
            resto.append(item)
            lidos.discard(url)
            continue
        st, b = t.get(url, "%s %s" % (casa, papel))
        if b is None:
            if t.registo and t.registo[-1].get("RESULTADO") == "TETO_DO_DOMINIO":
                resto.append(item)
                lidos.discard(url)
            else:       # robots proibe/nao se leu, ou a pagina falhou: fica escrito, nao se repete
                estado["FEITOS"].append(dict(item, RESULTADO="NAO_ABERTA", HTTP=st,
                                             MOTIVO=(t.registo[-1].get("RESULTADO") if t.registo else None)))
            continue
        html = b.decode("utf-8", "replace")
        estado["FEITOS"].append(dict(item, RESULTADO="LIDA", HTTP=st))
        if papel in ("ENTRADA", "LISTA"):
            for href, txt in ancoras(html, url):
                if papel == "ENTRADA" and re.search(c["DESCOBRIR_POR"], txt, re.I):
                    fila.append({"URL": href, "PAPEL": "LISTA", "DESCOBERTA_EM": url, "TEXTO": txt[:80]})
                elif re.search(c["PERFIL"], href):
                    a = casa_o_alvo(txt, alvos)
                    if a:
                        fila.append({"URL": href, "PAPEL": "PERFIL", "ALVO": a["NOME"], "OPENALEX_ID": a["OPENALEX_ID"],
                                      "ORCID": a.get("ORCID") or [], "LIGADO_EM": url, "TEXTO": txt[:80],
                                      "PRIORIDADE": [bool(a.get("PEDIDA_PELO_NOME")), a.get("PAR_DO_CASCO_RECENTE") or 0,
                                                     a.get("OBRAS_T6") or 0]})
        else:   # PERFIL: os links publicos da pagina oficial da pessoa
            canais, fora = [], []
            for href, txt in ancoras(html, url):
                plat, tipo, entra = S.classificar(href)
                if plat in ("PAGINA_INSTITUCIONAL_OU_PESSOAL", "ORCID", "GOOGLE_SCHOLAR"):
                    continue
                (canais if entra else fora).append({"URL": href, "PLATAFORMA": plat, "TIPO": tipo})
            estado["PERFIS"].append({"PESSOA": item["ALVO"], "OPENALEX_ID": item["OPENALEX_ID"], "ORCID": item["ORCID"],
                                     "PAGINA_OFICIAL": url, "LIGADA_DA_LISTA": item["LIGADO_EM"],
                                     "CANAIS": canais, "NAO_ENTRAM": fora})
    vistos, prox = {f["URL"] for f in estado["FEITOS"]}, []
    for x in resto:                                 # sem repetir o que ja se leu nem o que ja esta na fila
        if x["URL"] not in vistos and x["URL"] not in {y["URL"] for y in prox}:
            prox.append(x)
    prox.sort(key=ordem)
    estado["FILA"] = prox
    estado["RODADAS"] += 1
    return estado


def candidatar(estados: list, fila: Path) -> dict:
    """Os canais achados nas paginas OFICIAIS, pela porta canonica (`fonte_nova.registar`), numa fila dada (COPIA)."""
    sys.path.insert(0, str(S.RAIZ / "candidatas"))
    import fonte_nova as FN
    FN.FILA = fila
    feitas, fora = [], []
    for arq in estados:
        e = json.loads(Path(arq).read_text(encoding="utf-8"))
        for p in e["PERFIS"]:
            for c in p["CANAIS"]:
                para = ("D85: canal publico onde o pesquisador %s (%s) publica — %s; conhecimento/sinal precoce para "
                        "Intelligence Scientifica e Voci dal Campo" % (p["PESSOA"], e["CASA"], c["PLATAFORMA"]))
                nota = ("PESSOA=%s; IDENTIDADE=OpenAlex %s (obra T6 com a casa %s); ORCID=%s; PROVA=ligado da pagina oficial "
                        "%s; PAIS_PROVA=instituicao italiana da pessoa, nao o lugar do facto; ROTA_HOJE=%s" % (
                            p["PESSOA"], p["OPENALEX_ID"], e["CASA"], ",".join(p["ORCID"]) or "NAO SEI",
                            p["PAGINA_OFICIAL"], S.ROTA_HOJE.get(c["PLATAFORMA"], "NAO SEI")))
                linha = FN.registar(c["TIPO"], "IT", "%s — %s" % (p["PESSOA"], c["PLATAFORMA"]), c["URL"], para,
                                    "PESQ-FORA-DO-MUR (ferramentas/seguir_pesquisadores/listas_oficiais.py)",
                                    p["PAGINA_OFICIAL"], nota)
                feitas.append({"CANDIDATA_ID": linha["CANDIDATA_ID"], "TIPO": linha["TIPO"], "URL": linha["URL"]})
            fora += [dict(x, PESSOA=p["PESSOA"]) for x in p["NAO_ENTRAM"]]
    return {"CANDIDATAS": feitas, "NAO_ENTRAM": fora}


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    if "--candidatar" in argv:
        r = candidatar(sorted(Path(arg["saida"]).glob("ESTADO-*.json")), Path(arg["fila"]))
        print(json.dumps({"CANDIDATAS": len(r["CANDIDATAS"]), "NAO_ENTRAM": len(r["NAO_ENTRAM"])}, ensure_ascii=False))
        return 0
    fora = json.loads(Path(arg["alvos"]).read_text(encoding="utf-8"))
    if "--plano" in argv:
        for casa, c in CASAS.items():
            al = alvos_da_casa(fora, casa)
            print("%s: %d pessoas no cruzamento (%d com obra recente do casco); listas conhecidas %d; entradas %d"
                  % (casa, len(al), sum(1 for p in al if p.get("PAR_DO_CASCO_RECENTE")), len(c["LISTAS"]), len(c["ENTRADAS"])))
            print("   sabido:", c["SABIDO"])
            so = [p for p in al if p.get("PAR_DO_CASCO_RECENTE") or p.get("PEDIDA_PELO_NOME")]
            print("   com --so-casco: %d perfis a abrir no maximo -> ~%d rodadas so de perfis (4 paginas por rodada)"
                  % (len(so), -(-len(so) // 4)))
        return 0
    casa = arg["casa"]
    if casa == "CNR" and "--cnr-liberado" not in argv and "--seco" not in argv:
        print("RECUSADO: a coordenacao fechou o CNR na rede (26/09 10:13); so com --cnr-liberado")
        return 2
    saida = Path(arg["saida"])
    saida.mkdir(parents=True, exist_ok=True)
    arq = saida / ("ESTADO-%s.json" % casa)
    estado = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else estado_inicial(casa)
    alvos = alvos_da_casa(fora, casa)
    if "--so-casco" in argv:        # so quem tem obra RECENTE com par do casco no texto, e os pedidos pelo nome
        alvos = [x for x in alvos if x.get("PAR_DO_CASCO_RECENTE") or x.get("PEDIDA_PELO_NOME")]
    if "--seco" in argv:
        fx = Path(arg["fixtures"])
        resp = json.loads((fx / "RESPOSTAS-LISTAS.json").read_text(encoding="utf-8"))

        def falso(url):
            r = resp.get(url)
            if r is None:
                raise S.urllib.error.HTTPError(url, 404, "sem fixture", {}, None)
            return r.get("HTTP", 200), r["TEXTO"].encode("utf-8")
        if not arq.exists():
            estado = estado_inicial(casa)
            estado["FILA"] = [{"URL": u, "PAPEL": "ENTRADA"} for u in resp.get("_ENTRADAS_%s" % casa, [])] + \
                             [{"URL": u, "PAPEL": "LISTA"} for u in resp.get("_LISTAS_%s" % casa, [])]
        t = S.Transporte(saida / ("RODADA-%s-%02d" % (casa, estado["RODADAS"] + 1)), buscar=falso, pausa=0)
    else:
        if "--rodada" not in argv or "--autorizado" not in argv:
            print("RECUSADO: --rodada sai a rede; so com --autorizado (quem corre e o coordenador)")
            return 2
        pasta = saida / ("RODADA-%s-%02d" % (casa, estado["RODADAS"] + 1))
        pasta.mkdir(parents=True, exist_ok=True)
        if not S.portao(pasta, "ANTES"):
            print("PAROU: portao de egresso nao e IT (antes)")
            return 3
        t = S.Transporte(pasta)
    estado = uma_rodada(casa, estado, alvos, t)
    arq.write_text(json.dumps(estado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    t.pasta.mkdir(parents=True, exist_ok=True)
    (t.pasta / "PEDIDOS.json").write_text(json.dumps({"PEDIDOS": t.registo, "POR_DOMINIO": dict(t.conta), "TETO": S.TETO},
                                                     ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if "--seco" not in argv and not S.portao(t.pasta, "DEPOIS"):
        print("PAROU: portao de egresso nao e IT (depois)")
        return 3
    print(json.dumps({"CASA": casa, "RODADA": estado["RODADAS"], "PEDIDOS_POR_DOMINIO": dict(t.conta),
                      "NA_FILA": len(estado["FILA"]), "PERFIS_LIDOS": len(estado["PERFIS"]),
                      "CANAIS": sum(len(p["CANAIS"]) for p in estado["PERFIS"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
