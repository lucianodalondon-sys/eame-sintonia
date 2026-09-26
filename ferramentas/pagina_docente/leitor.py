# -*- coding: utf-8 -*-
"""PAGINA-DO-DOCENTE · o leitor: acha a pessoa na lista e le a pagina dela. SEM REDE (so recebe bytes).

Tres passos, os tres puros (texto entra, dicionario sai):
  descobrir_lista(html_da_casa)       -> links do MESMO dominio que levam a lista de pessoas
  achar_pessoa(html_da_lista, pessoa) -> o endereco da pagina da pessoa (so com SOBRENOME + 1.o NOME;
                                         dois enderecos diferentes = AMBIGUO, nao se escolhe)
  ler_pagina(html_da_pessoa)          -> os canais publicos que estao DENTRO do bloco da pessoa

O que NUNCA sai daqui: e-mail, telefone, seguidores (minimizacao, D85). As contas sociais DA UNIVERSIDADE
(cabecalho/rodape) nao sao da pessoa: cortam-se pelo BLOCO medido, pelo gabarito (link repetido em varias
paginas da mesma universidade) e, em ultimo caso, pelo nome da universidade no endereco da conta.
"""
import re
import sys
import unicodedata
import urllib.parse
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "seguir_pesquisadores"))
import seguir as S                                                    # noqa: E402  (classificar, dominio)
import universidades as U                                             # noqa: E402

# servicos que aparecem em paginas de docente e nao sao canal de ninguem
UTILIDADES = re.compile(r"(readspeaker\.com|google\.[a-z.]+/maps|goo\.gl/maps|maps\.app\.goo\.gl|cookiebot|iubenda|"
                        r"addtoany|creativecommons\.org|w3\.org|doi\.org|europa\.eu/cookies|bunny\.net|"
                        r"apple\.com/app|play\.google\.com)", re.I)
# a conta e da INSTITUICAO quando o endereco traz o nome dela (so para contas sociais, fora do bloco medido)
INSTITUCIONAL = re.compile(r"(universit|ateneo|dipartiment|department|/school/|unipi|unimi|unito|unipd|univpm|uniba|"
                           r"unicatt|unitn|unimol|unina|federico|unibo|univr|unipa|unite|uniroma1|sapienza|unict|uniud|"
                           r"unisa|unimore|statale|cattolica|polimi)", re.I)
# link do mesmo dominio que NAO e pagina da pessoa, mesmo com «laboratorio» no texto (curso, projeto, publicacao)
NAO_E_PAGINA_PROPRIA = re.compile(r"(/corsi/|insegnament|ent=progetto|ent=cs|ent=insegnamento|/handle/|/didattica/|"
                                  r"/tesi|pubblicazion|/news/|/notizie/|/eventi/|/avvisi/|\.pdf$|/category/ruoli/|"
                                  r"ent=struttura|ent=organo|ent=oi&|main\?ent=)", re.I)
SOCIAIS = {"YOUTUBE", "X", "BLUESKY", "MASTODON", "FACEBOOK", "INSTAGRAM", "LINKEDIN_PAGINA", "LINKEDIN_POST",
           "LINKEDIN_PERFIL", "PODCAST"}


REDE_SOCIAL = re.compile(r"(linkedin\.com|facebook\.com|instagram\.com|youtube\.com|twitter\.com|//(www\.)?x\.com|"
                         r"tiktok\.com|bsky\.app|threads\.net)", re.I)


def e_conta_social(href: str, plat: str) -> bool:
    """Qualquer endereco de rede social (tambem os que o classificar do seguir.py nao conhece, ex. linkedin /school/)."""
    return plat in SOCIAIS or bool(REDE_SOCIAL.search(href))


def normal(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in s if not unicodedata.combining(c)).lower()).strip()


def partes_do_nome(nome: str) -> tuple:
    """MUR escreve «SOBRENOME Nome»: as palavras TODAS EM MAIUSCULA sao o sobrenome. Consulta2 escreve
    «Nome Sobrenome»: a ultima palavra e o sobrenome."""
    ps = nome.split()
    sob = [p for p in ps if p.isupper() and len(p) > 1]
    if sob:
        dados = [p for p in ps if p not in sob]
    else:
        sob, dados = ps[-1:], ps[:-1]
    return [normal(x) for x in sob], [normal(x) for x in dados]


class _Ancoras(HTMLParser):
    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base, self.ancoras, self._a = base, [], None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            a = dict(attrs)
            self._a = [a.get("href") or "", [a.get("aria-label") or "", a.get("title") or ""]]

    def handle_data(self, data):
        if self._a is not None:
            self._a[1].append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._a is not None:
            href, txt = self._a
            self._a = None
            if href and not href.lower().startswith(("mailto:", "tel:", "javascript:", "#")):
                self.ancoras.append((urllib.parse.urljoin(self.base, href.strip()),
                                     texto_limpo(re.sub(r"\s+", " ", " ".join(txt)).strip())))


def texto_limpo(txt: str) -> str:
    """O texto do link vai para a saida: sem e-mail e sem numero com cara de telefone (minimizacao, D85)."""
    txt = re.sub(r"[\w.+-]+(@|\(at\)|\[at\])[\w-]+\.[\w.]+", "[e-mail omitido]", txt)
    return re.sub(r"(?<![\w/=.-])\+?\d[\d ./-]{7,}\d", "[numero omitido]", txt)


def ancoras(html: str, base: str) -> list:
    p = _Ancoras(base)
    try:
        p.feed(html)
    except Exception:                                                 # noqa: BLE001
        pass
    return p.ancoras


def mesmo_dominio(url: str, dominio: str) -> bool:
    h = (urllib.parse.urlparse(url).hostname or "").lower()
    return h == dominio or h.endswith("." + dominio)


def descobrir_lista(html: str, base: str, universidade: str) -> list:
    """Na CASA do site: os links do mesmo dominio com cara de lista de pessoas (melhor primeiro)."""
    dom = U.UNIVERSIDADES[universidade]["DOMINIO"]
    vistos, fora = set(), []
    for href, txt in ancoras(html, base):
        if not mesmo_dominio(href, dom) or href in vistos:
            continue
        m = U.PISTA_DA_LISTA.search(href) or U.PISTA_DA_LISTA.search(txt)
        if m:
            vistos.add(href)
            # «docenti»/«persone» no texto do link vale mais do que so no endereco
            fora.append((0 if U.PISTA_DA_LISTA.search(txt) else 1, len(href), href, txt[:80]))
    return [{"URL": h, "TEXTO": t} for _, _, h, t in sorted(fora)]


def cartoes(html: str, base: str, padrao: str) -> list:
    """Listas em que o link diz so «Profilo completo» (Udine): o nome esta no CARTAO, que comeca no 1.o link
    da pessoa (a foto) e acaba no 1.o link da pessoa seguinte. Devolve (href, texto do cartao)."""
    inicios = []
    for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>', html):
        href = urllib.parse.urljoin(base, m.group(1).replace("&amp;", "&"))
        if re.match(padrao, href) and (not inicios or inicios[-1][0] != href):
            inicios.append((href, m.start()))
    out = []
    for i, (href, ini) in enumerate(inicios):
        fim = inicios[i + 1][1] if i + 1 < len(inicios) else ini + 3000
        out.append((href, re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html[ini:fim]))[:600]))
    return out


def achar_pessoa(html: str, base: str, pessoa: dict, universidade: str) -> dict:
    u = U.UNIVERSIDADES[universidade]
    sob, dados = partes_do_nome(pessoa["NOME"])
    if not sob or not dados:
        return {"ESTADO": "NOME_INCOMPLETO", "URLS": []}
    primeiro = dados[0]
    achados = []
    for href, txt in (cartoes(html, base, u["PADRAO_PESSOA"]) if u.get("NOME_NO_CARTAO") else ancoras(html, base)):
        if not mesmo_dominio(href, u["DOMINIO"]):
            continue
        if u["PADRAO_PESSOA"] and not re.match(u["PADRAO_PESSOA"], href.replace("&amp;", "&")):
            continue
        alvo = " %s %s " % (normal(txt), normal(urllib.parse.unquote(href)))
        if all(" %s " % s in alvo for s in sob) and " %s " % primeiro in alvo:
            achados.append(href.replace("&amp;", "&"))
    achados = list(dict.fromkeys(achados))
    # a mesma pagina em ITA/ENG ou com / no fim e uma so
    chave = {re.sub(r"/(it|en)/|/$|/index\.html$", "/", a.lower()) for a in achados}
    if not achados:
        return {"ESTADO": "NAO_ACHEI", "URLS": []}
    if len(chave) > 1:
        return {"ESTADO": "AMBIGUO", "URLS": achados}
    return {"ESTADO": "ACHEI", "URL": achados[0], "URLS": achados}


def cortar_bloco(html: str, universidade: str) -> tuple:
    b = U.UNIVERSIDADES[universidade]["BLOCO"]
    if not b:
        return html, "SEM_BLOCO_MEDIDO"
    i = re.search(b[0], html)
    if not i:
        return html, "BLOCO_NAO_ENCONTRADO (a forma da pagina mudou?)"
    f = re.search(b[1], html[i.start():])
    return html[i.start(): i.start() + f.start() if f else None], "BLOCO_MEDIDO"


def gabarito(paginas: list) -> set:
    """Links que se repetem em varias paginas da MESMA universidade = moldura do site, nao da pessoa."""
    if len(paginas) < 2:
        return set()
    c = Counter(h for html, base in paginas for h in {a for a, _ in ancoras(html, base)})
    return {h for h, n in c.items() if n >= max(2, 0.3 * len(paginas))}


def ler_pagina(html: str, url: str, universidade: str, moldura: set = frozenset()) -> dict:
    u = U.UNIVERSIDADES[universidade]
    corpo, bloco = cortar_bloco(html, universidade)
    out = {"URL_PAGINA": url, "BLOCO": bloco, "CANAIS": [], "NAO_ENTRAM": [], "PAGINAS_PROPRIAS": [], "EXTERNOS_SEM_ROTULO": [],
           "IGNORADOS": Counter()}
    campos = {}
    for nome, rx in (u.get("CAMPOS") or {}).items():
        for m in re.finditer(r"<a\b[^>]*>", corpo):
            if re.search(rx, m.group(0)) or re.search(rx, corpo[m.end(): m.end() + 120].split("</a>")[0]):
                h = re.search(r'href="([^"]+)"', m.group(0))
                if h:
                    campos[urllib.parse.urljoin(url, h.group(1).replace("&amp;", "&"))] = nome
    vistos = set()
    for href, txt in ancoras(corpo, url):
        k = href.rstrip("/").lower()
        if k in vistos or href == url:
            continue
        vistos.add(k)
        if href in moldura:
            out["IGNORADOS"]["MOLDURA_DO_SITE"] += 1
            continue
        if UTILIDADES.search(href):
            out["IGNORADOS"]["UTILIDADE"] += 1
            continue
        campo = campos.get(href)
        if mesmo_dominio(href, u["DOMINIO"]):
            if campo or (U.PISTA_PAGINA_PROPRIA.search(txt) and not NAO_E_PAGINA_PROPRIA.search(href)):
                out["PAGINAS_PROPRIAS"].append({"URL": href, "TEXTO": txt[:80], "CAMPO": campo})
            else:
                out["IGNORADOS"]["MESMO_DOMINIO"] += 1
            continue
        plat, tipo, entra = S.classificar(href)
        if e_conta_social(href, plat) and bloco != "BLOCO_MEDIDO" and INSTITUCIONAL.search(href):
            out["IGNORADOS"]["CONTA_DA_INSTITUICAO"] += 1
            continue
        if plat == "PAGINA_INSTITUCIONAL_OU_PESSOAL" and not campo and not U.PISTA_PAGINA_PROPRIA.search(txt):
            # link externo sem rotulo (noticia, revista, projeto): nao se afirma que e DA pessoa; fica para
            # leitura humana, nao vira canal
            out["EXTERNOS_SEM_ROTULO"].append({"URL": href, "TEXTO": txt[:80]})
            continue
        linha = {"URL": href, "PLATAFORMA": plat, "TIPO": tipo, "TEXTO": txt[:80],
                 "PROVA": "PAGINA OFICIAL DO DOCENTE (%s)%s" % (universidade, ", campo %s" % campo if campo else ""),
                 "VISTO_EM": url}
        (out["CANAIS"] if entra else out["NAO_ENTRAM"]).append(linha)
    out["IGNORADOS"] = dict(out["IGNORADOS"])
    return out


def nome_confere(html: str, pessoa: dict, universidade: str) -> bool:
    """A pagina e mesmo desta pessoa? SOBRENOME inteiro + 1.o NOME dentro do bloco da pessoa."""
    sob, dados = partes_do_nome(pessoa["NOME"])
    if not sob or not dados:
        return False
    corpo, _ = cortar_bloco(html, universidade)
    t = " %s " % normal(re.sub(r"<[^>]+>", " ", corpo))
    return all(" %s " % x in t for x in sob) and " %s " % dados[0] in t


def construir(pessoa: dict, universidade: str) -> str:
    """O endereco CONSTRUIDO pela regra medida (so onde ha regra); a pagina so vale se nome_confere()."""
    regra = U.UNIVERSIDADES[universidade].get("CONSTRUIR")
    sob, dados = partes_do_nome(pessoa["NOME"])
    if not regra or not sob or not dados:
        return ""
    return regra[0].format(primeiro=dados[0].replace(" ", ""), sobrenome="".join(sob).replace(" ", ""))


def proximas_paginas(html: str, base: str, universidade: str) -> list:
    """Lista de pessoas partida em paginas (ex.: Udine, 10 por pagina): os links para as paginas seguintes."""
    rx = U.UNIVERSIDADES[universidade].get("PAGINACAO")
    if not rx:
        return []
    return list(dict.fromkeys(h.replace("&amp;", "&") for h, _ in ancoras(html, base) if re.search(rx, h)))
