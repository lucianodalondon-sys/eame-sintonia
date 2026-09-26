# -*- coding: utf-8 -*-
"""SEGUIR-PESQUISADORES · 2) por PESSOA, os canais PUBLICOS onde ela publica (D85). Rodadas com teto.

    py ferramentas/seguir_pesquisadores/seguir.py --plano --pessoas=PESSOAS-ORDENADAS.json [--so-prioridade]
    py ferramentas/seguir_pesquisadores/seguir.py --rodada=N --pessoas=... --saida=<pasta fora do Git> --autorizado
    py ferramentas/seguir_pesquisadores/seguir.py --seco --fixtures=<pasta> --pessoas=... --saida=<pasta>
    py ferramentas/seguir_pesquisadores/seguir.py --candidatar --saida=<pasta> --fila=<FONTES-CANDIDATAS.json de uma COPIA>

O QUE SE PEDE (so isto, e so publico):
  1. ORCID `researcher-urls` da pessoa (pub.orcid.org, a secao MINIMA: so os links que a PROPRIA pessoa
     declara; nunca /person nem /email).
  2. A pagina institucional/pessoal/de laboratorio que a pessoa declarou no ORCID: dela tiram-se os links
     para canais publicos (YouTube, X, Bluesky, Mastodon, podcast, blog/newsletter, LinkedIn POST).
Os perfis sociais NAO se abrem: o endereco basta para a candidata; quem os abre e o robo de fontes
(QUALIFY -> contrato -> rota -> canario). LinkedIn de PESSOA (/in/) = muro de login: regista-se que
existe e NAO vira candidata; so POST publico (/posts/, /feed/update/) entra (D24/D80/D85).
Nunca: contactos, e-mails, seguidores, comentarios, mensagens (minimizacao, D85).

OS LIMITES (no codigo, nao no papel):
  * teto 5 pedidos por DOMINIO REGISTAVEL por rodada, contando o robots.txt;
  * robots.txt lido e respeitado antes do 1.o pedido a cada host (Disallow = nao se pede);
  * 3 s entre pedidos; timeout 30 s; sem cookies, sem login, User-Agent declarado;
  * portao de egresso IT (superficie/rede.py) ANTES e DEPOIS da rodada; fora de IT -> PARA;
  * saida FORA do Git (pasta dada); os bytes de cada pagina guardados com sha256.
"""
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TETO, PAUSA_S, TIMEOUT_S = 5, 3.0, 30
UA = "SintoniaEAME-SeguirPesquisadores/1 (+publico, sem login; D85)"
ORCID_URLS = "https://pub.orcid.org/v3.0/%s/researcher-urls"
PESSOAS_POR_RODADA = 4          # orcid.org: robots + 4 = 5 (o teto)

# endereco -> (plataforma, TIPO da porta candidatas/fonte_nova.py, entra como candidata?)
PLATAFORMAS = [
    (r"linkedin\.com/(posts|feed/update)/", "LINKEDIN_POST", "LINKEDIN", True),
    (r"linkedin\.com/(in|pub)/", "LINKEDIN_PERFIL", None, False),       # muro de login (D24/D85)
    (r"linkedin\.com/company/", "LINKEDIN_PAGINA", "LINKEDIN", True),
    (r"(youtube\.com/(@|channel/|c/|user/)|youtu\.be/)", "YOUTUBE", "YOUTUBE", True),
    (r"(^|//)(www\.)?(x|twitter)\.com/", "X", "OUTRO", True),
    (r"bsky\.app/profile/", "BLUESKY", "OUTRO", True),
    (r"/@[A-Za-z0-9_]+$|mastodon|fediscience|scholar\.social", "MASTODON", "OUTRO", True),
    (r"(podcast|spreaker\.com|anchor\.fm|open\.spotify\.com/show)", "PODCAST", "OUTRO", True),
    (r"(substack\.com|newsletter|/blog\b|wordpress\.com|blogspot\.)", "BLOG_NEWSLETTER", "IMPRENSA", True),
    (r"researchgate\.net", "RESEARCHGATE", None, False),                   # abre com login/muro: fora
    (r"scholar\.google", "GOOGLE_SCHOLAR", None, False),                   # indice, nao canal do dia a dia
    (r"orcid\.org", "ORCID", None, False),
    (r"(facebook\.com)", "FACEBOOK", "FACEBOOK", True),
    (r"(instagram\.com)", "INSTAGRAM", "INSTAGRAM", True),
]
SUFIXOS_DOIS_NIVEIS = {"co.uk", "ac.uk", "com.br", "gov.it", "edu.it"}
# o que o robo de fontes do vivo (278cd489) sabe fazer com cada tipo — escrito na NOTA da candidata
ROTA_HOJE = {
    "YOUTUBE": "rota do Scrap (canal-youtube, SOC2): flui ate ao canario do Scrap",
    "LINKEDIN_POST": "SEM ROTA: o QUALIFY so aceita /company/; espera a fase video-post-linkedin (D80)",
    "LINKEDIN_PAGINA": "rota do Scrap (video-linkedin, D23)",
    "PAGINA_INSTITUCIONAL_OU_PESSOAL": "pagina HTML: contrato de site e canario HTML",
    "BLOG_NEWSLETTER": "pagina HTML: contrato de site e canario HTML",
    "X": "SEM ROTA PROPRIA: o QUALIFY trata-a como site; o canario deve reprovar (pede login)",
    "BLUESKY": "SEM ROTA PROPRIA para a conta: vai como site; o canario deve reprovar",
    "MASTODON": "SEM ROTA PROPRIA para a conta: vai como site; o canario deve reprovar",
    "PODCAST": "SEM ROTA: o audio de podcast nao se baixa; vai como site",
    "FACEBOOK": "rota da familia FACEBOOK (NAO SEI se aceita pessoa)",
    "INSTAGRAM": "rota da familia INSTAGRAM (NAO SEI se aceita pessoa)",
}


def dominio(url: str) -> str:
    h = (urllib.parse.urlparse(url).hostname or "").lower()
    p = h.split(".")
    if len(p) >= 3 and ".".join(p[-2:]) in SUFIXOS_DOIS_NIVEIS:
        return ".".join(p[-3:])
    return ".".join(p[-2:]) if len(p) >= 2 else h


def classificar(url: str) -> tuple:
    u = url.strip()
    for rx, plat, tipo, entra in PLATAFORMAS:
        if re.search(rx, u, re.I):
            return plat, tipo, entra
    return "PAGINA_INSTITUCIONAL_OU_PESSOAL", "CIENCIA", True


class _Links(HTMLParser):
    def __init__(self, base):
        super().__init__()
        self.base, self.links = base, []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href and not href.startswith(("mailto:", "tel:", "javascript:", "#")):
                self.links.append(urllib.parse.urljoin(self.base, href))


def links_da_pagina(html: str, base: str) -> list:
    p = _Links(base)
    try:
        p.feed(html)
    except Exception:                                                 # noqa: BLE001
        pass
    return list(dict.fromkeys(p.links))


class Transporte:
    """O unico sitio que sai a rede. Conta por dominio, le o robots, pausa, guarda os bytes."""

    def __init__(self, pasta: Path, buscar=None, pausa=PAUSA_S):
        self.pasta, self.pausa = pasta, pausa
        self.conta = Counter()
        self.robots = {}
        self.registo = []
        self._buscar = buscar or self._urllib

    @staticmethod
    def _urllib(url):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, text/html"})
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
            return r.status, r.read()

    def _pedir(self, url, porque):
        d = dominio(url)
        if self.conta[d] >= TETO:
            self.registo.append({"URL": url, "RESULTADO": "TETO_DO_DOMINIO", "DOMINIO": d, "PORQUE": porque})
            return None, None
        self.conta[d] += 1
        if self.registo:
            time.sleep(self.pausa)
        try:
            st, b = self._buscar(url)
        except Exception as e:                                        # noqa: BLE001
            st, b = getattr(e, "code", None), None
            self.registo.append({"URL": url, "RESULTADO": "FALHA", "HTTP": st, "ERRO": type(e).__name__, "PORQUE": porque})
            return st, None
        sha = hashlib.sha256(b or b"").hexdigest()
        if b:
            (self.pasta / "bytes").mkdir(parents=True, exist_ok=True)
            (self.pasta / "bytes" / sha).write_bytes(b)
        self.registo.append({"URL": url, "RESULTADO": "OK", "HTTP": st, "SHA256": sha, "BYTES": len(b or b""),
                             "DOMINIO": d, "PORQUE": porque, "EM": datetime.now(timezone.utc).isoformat()})
        return st, b

    def pode(self, url) -> bool:
        p = urllib.parse.urlparse(url)
        host = "%s://%s" % (p.scheme, p.netloc)
        if host not in self.robots:
            st, b = self._pedir(host + "/robots.txt", "robots")
            rp = urllib.robotparser.RobotFileParser()
            if st == 200 and b is not None:
                rp.parse(b.decode("utf-8", "replace").splitlines())
                self.robots[host] = rp
            elif st in (404, 410):
                rp.parse([])            # sem robots = sem regra
                self.robots[host] = rp
            else:
                self.robots[host] = None    # nao se leu: NAO SEI -> nao se pede (prudencia, D39)
        rp = self.robots[host]
        return bool(rp and rp.can_fetch(UA, url))

    def get(self, url, porque):
        if not self.pode(url):
            self.registo.append({"URL": url, "RESULTADO": "ROBOTS_OU_NAO_LIDO", "PORQUE": porque})
            return None, None
        return self._pedir(url, porque)


def seguir_pessoa(p: dict, t: Transporte) -> dict:
    out = {"NOME": p["NOME"], "UNIVERSIDADE": p.get("UNIVERSIDADE"), "SSD": p.get("SSD"),
           "ORCID": p.get("ORCID") or [], "CANAIS": [], "NAO_ENTRAM": [], "PASSOS": []}
    if len(out["ORCID"]) != 1:
        out["PASSOS"].append("ORCID %s: %s" % ("ausente" if not out["ORCID"] else "AMBIGUO (%d)" % len(out["ORCID"]),
                                                "nao se segue sem uma identidade unica"))
        return out
    oid = out["ORCID"][0]
    st, b = t.get(ORCID_URLS % oid, "orcid researcher-urls de %s" % p["NOME"])
    if not b:
        if t.registo and t.registo[-1].get("RESULTADO") == "TETO_DO_DOMINIO":
            out["PENDENTE"] = "TETO_DO_DOMINIO"
            out["PASSOS"].append("ORCID %s: PENDENTE — o teto de %d pedidos a orcid.org nesta rodada acabou; "
                                 "fica para a proxima" % (oid, TETO))
        else:
            out["PASSOS"].append("ORCID %s: sem resposta (HTTP %s)" % (oid, st))
        return out
    try:
        urls = [((u.get("url") or {}).get("value") or "").strip()
                for u in (json.loads(b).get("researcher-url") or [])]
    except ValueError:
        urls = []
    out["PASSOS"].append("ORCID %s: %d link(s) declarados pela pessoa" % (oid, len([u for u in urls if u])))
    vistos = set()

    def anotar(url, prova, origem):
        plat, tipo, entra = classificar(url)
        k = url.rstrip("/").lower()
        if k in vistos:
            return plat
        vistos.add(k)
        linha = {"URL": url, "PLATAFORMA": plat, "TIPO": tipo, "PROVA": prova, "VISTO_EM": origem}
        (out["CANAIS"] if entra else out["NAO_ENTRAM"]).append(linha)
        return plat

    paginas = []
    for u in urls:
        if not u:
            continue
        if anotar(u, "ORCID_RESEARCHER_URLS (declarado pela propria pessoa)", ORCID_URLS % oid) == "PAGINA_INSTITUCIONAL_OU_PESSOAL":
            paginas.append(u)
    for pg in paginas[:2]:          # no maximo 2 paginas por pessoa por rodada
        st, b = t.get(pg, "pagina declarada por %s" % p["NOME"])
        if not b:
            out["PASSOS"].append("pagina %s: nao aberta (%s)" % (pg, st))
            continue
        ls = links_da_pagina(b.decode("utf-8", "replace"), pg)
        n = 0
        for l in ls:
            plat, _, _ = classificar(l)
            if plat not in ("PAGINA_INSTITUCIONAL_OU_PESSOAL", "ORCID", "GOOGLE_SCHOLAR"):
                anotar(l, "LIGADO NA PAGINA que a pessoa declarou no ORCID", pg)
                n += 1
        out["PASSOS"].append("pagina %s: %d link(s) para canais publicos" % (pg, n))
    return out


def portao(saida: Path, quando: str) -> bool:
    vivo = Path("C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1")
    r = subprocess.run([sys.executable, str(vivo / "superficie" / "rede.py"), "--portao-de-egresso", "IT"],
                       capture_output=True, text=True, timeout=300)
    (saida / ("PORTAO-%s.txt" % quando)).write_text(r.stdout[-4000:] + r.stderr[-2000:], encoding="utf-8")
    return r.returncode == 0


def rodadas(pessoas: list, so_prioridade: bool) -> list:
    alvo = [p for p in pessoas if (p.get("PRIORIDADE") or not so_prioridade)
            and p.get("LIGACAO_T6") in ("NOME+UNIVERSIDADE", "RESOLVIDO")]
    return [alvo[i:i + PESSOAS_POR_RODADA] for i in range(0, len(alvo), PESSOAS_POR_RODADA)]


def correr(grupo: list, saida: Path, transporte: Transporte) -> dict:
    res = [seguir_pessoa(p, transporte) for p in grupo]
    doc = {"DATASET": "SEGUIR-PESQUISADORES-RODADA", "PESSOAS": res, "PEDIDOS": transporte.registo,
           "PEDIDOS_POR_DOMINIO": dict(transporte.conta), "TETO": TETO,
           "TETO_RESPEITADO": all(v <= TETO for v in transporte.conta.values())}
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "RESULTADO.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return doc


def candidatar(pastas: list, fila: Path) -> dict:
    """As candidatas pela PORTA CANONICA (`candidatas/fonte_nova.registar`), numa fila dada (uma COPIA)."""
    sys.path.insert(0, str(RAIZ / "candidatas"))
    import fonte_nova as FN
    FN.FILA = fila
    feitas, fora = [], []
    for pasta in pastas:
        doc = json.loads((pasta / "RESULTADO.json").read_text(encoding="utf-8"))
        for p in doc["PESSOAS"]:
            for c in p["CANAIS"]:
                para = ("D85: canal publico onde o pesquisador %s (%s, %s) publica — %s; conhecimento/sinal precoce "
                        "para Intelligence Scientifica e Voci dal Campo" % (p["NOME"], p.get("UNIVERSIDADE"), p.get("SSD"),
                                                                          c["PLATAFORMA"]))
                nota = ("PESSOA=%s; IDENTIDADE=MUR; ORCID=%s; PROVA=%s; VISTO_EM=%s; PAIS_PROVA=universidade italiana "
                        "(MUR) da pessoa, nao o lugar do facto; ROTA_HOJE=%s" % (
                            p["NOME"], ",".join(p["ORCID"]), c["PROVA"], c["VISTO_EM"], ROTA_HOJE.get(c["PLATAFORMA"], "NAO SEI")))
                linha = FN.registar(c["TIPO"], "IT", "%s — %s" % (p["NOME"], c["PLATAFORMA"]), c["URL"], para,
                                    "SEGUIR-PESQUISADORES (ferramentas/seguir_pesquisadores/seguir.py)", c["VISTO_EM"], nota)
                feitas.append({"CANDIDATA_ID": linha["CANDIDATA_ID"], "TIPO": linha["TIPO"], "URL": linha["URL"]})
            fora += [dict(x, PESSOA=p["NOME"]) for x in p["NAO_ENTRAM"]]
    return {"CANDIDATAS": feitas, "NAO_ENTRAM": fora}


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    pessoas = json.loads(Path(arg["pessoas"]).read_text(encoding="utf-8")) if "pessoas" in arg else []
    pessoas = pessoas["PESSOAS"] if isinstance(pessoas, dict) else pessoas
    rs = rodadas(pessoas, "--so-prioridade" in argv or "--seco" not in argv)
    if "--plano" in argv:
        print("rodadas", len(rs), "pessoas", sum(len(r) for r in rs),
              "pedidos previstos por rodada: orcid.org <= %d (robots + %d); paginas: <= 2 por pessoa, teto 5 por dominio"
              % (TETO, PESSOAS_POR_RODADA))
        for i, r in enumerate(rs, 1):
            print("RODADA %02d: %s" % (i, "; ".join("%s (%s)" % (p["NOME"], p.get("UNIVERSIDADE")) for p in r)))
        return 0
    if "rodada" in arg:
        if "--autorizado" not in argv:
            print("RECUSADO: --rodada sai a rede; so com --autorizado (quem corre e o coordenador)")
            return 2
        n = int(arg["rodada"])
        saida = Path(arg["saida"]) / ("RODADA-%02d" % n)
        saida.mkdir(parents=True, exist_ok=True)
        if not portao(saida, "ANTES"):
            print("PAROU: portao de egresso nao e IT (antes)")
            return 3
        doc = correr(rs[n - 1], saida, Transporte(saida))
        ok = portao(saida, "DEPOIS")
        print(json.dumps({"PEDIDOS_POR_DOMINIO": doc["PEDIDOS_POR_DOMINIO"], "TETO_RESPEITADO": doc["TETO_RESPEITADO"],
                          "PORTAO_DEPOIS_IT": ok, "CANAIS": sum(len(p["CANAIS"]) for p in doc["PESSOAS"])}, ensure_ascii=False))
        return 0 if ok else 3
    if "--seco" in argv:
        fx = Path(arg["fixtures"])
        respostas = json.loads((fx / "RESPOSTAS.json").read_text(encoding="utf-8"))

        def falso(url):
            r = respostas.get(url)
            if r is None:
                e = urllib.error.HTTPError(url, 404, "nao ha fixture", {}, None)
                raise e
            corpo = (fx / r["FICHEIRO"]).read_bytes() if r.get("FICHEIRO") else r.get("TEXTO", "").encode("utf-8")
            return r.get("HTTP", 200), corpo
        grupo = json.loads((fx / "PESSOAS.json").read_text(encoding="utf-8"))
        saida = Path(arg["saida"])
        doc = correr(grupo, saida, Transporte(saida, buscar=falso, pausa=0))
        print(json.dumps({"PEDIDOS_POR_DOMINIO": doc["PEDIDOS_POR_DOMINIO"], "TETO_RESPEITADO": doc["TETO_RESPEITADO"],
                          "CANAIS": [(p["NOME"], c["PLATAFORMA"]) for p in doc["PESSOAS"] for c in p["CANAIS"]],
                          "NAO_ENTRAM": [(p["NOME"], c["PLATAFORMA"]) for p in doc["PESSOAS"] for c in p["NAO_ENTRAM"]]},
                         ensure_ascii=False, indent=1))
        return 0
    if "--candidatar" in argv:
        pastas = sorted(Path(arg["saida"]).glob("RODADA-*")) or [Path(arg["saida"])]
        r = candidatar(pastas, Path(arg["fila"]))
        print("candidatas", len(r["CANDIDATAS"]), "nao entram", len(r["NAO_ENTRAM"]),
              dict(Counter(x["TIPO"] for x in r["CANDIDATAS"])))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
