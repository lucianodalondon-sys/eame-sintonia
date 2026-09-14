#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A PENEIRA — abre cada pista, olha o que ela entrega, e diz porque.

O grafo de descoberta devolve milhares de hosts. A maioria nao e fonte: e o
banner de cookies, o provedor de e-mail da universidade, o botao de partilhar
no Twitter. Isso nao e falha do grafo — e o preco de andar pelos links de
verdade em vez de aceitar o que uma busca por palavra devolve.

Este script separa. E separa com sonda: cada linha que sai daqui tem um HTTP
real por tras, com titulo de pagina guardado. Nenhuma classificacao nasce de
"parece relevante".

AS SEIS MEDIDAS, MEDIDAS EM SEPARADO
------------------------------------
Nao existe nota unica. Somar autoridade com alcance faz um perfil de
entretenimento com um milhao de seguidores empatar com um servico
fitossanitario — e foi exatamente esse erro que esta missao procura.

    ITALIA          o conteudo e italiano, ou so o dominio e?
    SINAL_AGRI      quantas palavras do oficio aparecem na pagina
    INFO_PROPRIA    ela PRODUZ (boletim, dado, aviso) ou so fala de si?
    RECORRENCIA     ha data recente e palavra de periodicidade?
    PROXIMIDADE     e dona do fato, ou conta o fato de outro?
    IDENTIDADE      da-se a conhecer? titulo, nome, dono legivel?

CLASSES
-------
    A  informacao propria + recorrente + proxima do fato + identidade clara
    B  util, menos central
    C  complementar
    HOLD    ha indicio bom e falta prova
    REJECT  razao concreta escrita ao lado
    UNKNOWN nao foi possivel medir — e diferente de REJECT

A classe que sai daqui e PRE-CLASSE. Ela nao promove ninguem: A e B so valem
depois de um humano abrir a fonte e guardar um exemplo real. Este ficheiro
prepara o trabalho; nao o substitui.
"""

import json
import re
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TRABALHO = Path(sys.argv[1] if len(sys.argv) > 1
                else "C:/Users/London1/AppData/Local/Temp/sintonia-italy-deep")
CACHE = TRABALHO / "cache"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

HOJE = "2026-09-14"
ANO_HOJE = 2026

# ── o que NAO e fonte, e porque ───────────────────────────────────────────
# Isto nao apaga nada: marca REJECT com motivo. Uma lista destas escrita a
# mao e sempre incompleta — por isso a auditoria manual existe.
INFRA = {
    "cookie/consentimento": ["iubenda.com", "cookiedatabase.org", "webtoffee.com",
                             "cookiebot.com", "onetrust.com", "cookieyes.com",
                             "termsfeed.com", "civicuk.com", "usercentrics.com"],
    "plataforma/servico tecnico": ["agid.gov.it", "cineca.it", "office.com", "office365.com",
                                   "microsoftonline.com", "sharepoint.com", "outlook.com",
                                   "amazonaws.com", "cloudflare.com", "gitlab.com",
                                   "github.com", "wordpress.org", "wordpress.com",
                                   "readspeaker.com", "browsehappy.com", "opencontent.it",
                                   "u-gov.it", "emailsp.com", "urbi.it", "adobe.com",
                                   "mozilla.org", "microsoft.com", "google.com",
                                   "google.it", "goo.gl", "gstatic.com", "jquery.com",
                                   "w3.org", "schema.org", "creativecommons.org",
                                   "maps.google.com", "apple.com", "play.google.com",
                                   "bit.ly", "tinyurl.com", "doi.org", "issuu.com",
                                   "calameo.com", "scribd.com", "eventbrite.it",
                                   "zoom.us", "teams.microsoft.com", "webex.com",
                                   "surveymonkey.com", "mailchimp.com", "sendinblue.com",
                                   "addtoany.com", "sharethis.com", "portaleamministrazionetrasparente.it",
                                   "trasparenza-valutazione-merito.it", "albotelematico.provincia.tn.it",
                                   "pagopa.gov.it", "spid.gov.it", "agenziaentrate.gov.it",
                                   "inps.it", "normattiva.it", "gazzettaufficiale.it"],
    "rede social (a conta e que e canal, nao a plataforma)": [
        "twitter.com", "x.com", "facebook.com", "instagram.com", "linkedin.com",
        "youtube.com", "youtu.be", "tiktok.com", "whatsapp.com", "wa.me",
        "t.me", "telegram.me", "threads.net", "pinterest.com", "flickr.com",
        "vimeo.com", "spotify.com", "soundcloud.com", "podcasts.apple.com",
        "open.spotify.com", "linktr.ee", "tumblr.com", "reddit.com",
        "messenger.com", "snapchat.com", "twitch.tv"],
    "enciclopedia/agregador sem informacao propria": [
        "wikipedia.org", "wikimedia.org", "researchgate.net", "academia.edu",
        "scholar.google.com", "semanticscholar.org", "sciencedirect.com",
        "springer.com", "link.springer.com", "mdpi.com", "wiley.com",
        "tandfonline.com", "elsevier.com", "jstor.org", "scopus.com",
        "webofscience.com", "europepmc.org", "pubmed.ncbi.nlm.nih.gov"],
}
MOTIVO_INFRA = {}
for motivo, hosts in INFRA.items():
    for h in hosts:
        MOTIVO_INFRA[h] = motivo

PALAVRA_AGRI = [
    "agricol", "agrari", "agronom", "coltur", "fitosanitar", "fitopatolog",
    "difesa integrata", "parassit", "malatti delle piante", "infestant",
    "diserb", "vigne", "viticol", "olivicol", "oliveto", "cereal", "frumento",
    "grano duro", "mais", "riso", "risicol", "pomodoro", "orticol",
    "frutticol", "melo", "pero", "agrum", "nocciol", "patata", "barbabietol",
    "soia", "girasol", "irrigaz", "agrometeo", "suolo agricolo", "semina",
    "raccolto", "produttor agricol", "azienda agricola", "vivaist", "sementi",
    "fertilizz", "agroaliment", "agrifood", "bollettino", "consorzio agrario",
    "cooperativa agricola", "psr", "pac", "biologico", "zootecn", "apicol",
    "trattamento", "principio attivo", "agrofarmac", "fitofarmac",
    "monitoraggio", "fenologic", "avversita", "resa", "vendemmia",
]
MARCA_INFO_PROPRIA = [
    "bollettino", "bollettini", "notiziario", "newsletter", "avviso",
    "avvisi", "allerta", "comunicato", "rapporto", "report", "open data",
    "dati aperti", "statistic", "pubblicazioni", "annuario", "archivio",
    "risultati", "prove sperimentali", "sperimentazione", "monitoraggio",
    "osservatorio", "rilevazioni", "listino", "quotazioni", "prezzi",
    "rss", "feed", "podcast", "webinar", "banca dati", "database",
    "disciplinari", "linee tecniche", "schede tecniche",
]
MARCA_PERIODICA = [
    "settimanale", "settimanali", "quindicinale", "mensile", "bimestrale",
    "trimestrale", "giornaliero", "quotidiano", "periodic", "aggiornato il",
    "ultimo aggiornamento", "n. ", "numero ",
]
# Marcas de quem e DONO do facto, e nao quem o conta.
MARCA_PRIMARIA = [
    "servizio fitosanitario", "ispettore fitosanitario", "monitoraggio",
    "rete di monitoraggio", "stazione agrometeo", "stazioni meteo",
    "laboratorio", "analisi", "prove sperimentali", "campo sperimentale",
    "azienda sperimentale", "rilevazioni", "nostri tecnici", "i nostri dati",
    "open data", "dati aperti", "listino", "quotazioni ufficiali",
]
MARCA_AGREGADOR = [
    "rassegna stampa", "elenco dei siti", "link utili", "directory",
    "portale di accesso", "aggregatore", "motore di ricerca",
]
MARCA_LOJA = ["carrello", "aggiungi al carrello", "acquista ora", "shop online",
              "e-commerce", "spedizione gratuita", "iva inclusa", "prezzo:",
              "sconto", "offerta speciale"]

REGIOES = {
    "ABRUZZO": ["abruzzo", "l'aquila", "teramo", "pescara", "chieti"],
    "BASILICATA": ["basilicata", "lucan", "potenza", "matera", "metaponto"],
    "CALABRIA": ["calabria", "cosenza", "catanzaro", "reggio calabria", "crotone", "vibo"],
    "CAMPANIA": ["campania", "napoli", "salerno", "avellino", "benevento", "caserta"],
    "EMILIA-ROMAGNA": ["emilia-romagna", "emilia romagna", "bologna", "modena",
                       "parma", "reggio emilia", "ferrara", "ravenna", "forli",
                       "cesena", "rimini", "piacenza", "romagna"],
    "FRIULI-VENEZIA GIULIA": ["friuli", "trieste", "udine", "gorizia", "pordenone"],
    "LAZIO": ["lazio", "roma", "viterbo", "latina", "frosinone", "rieti"],
    "LIGURIA": ["liguria", "genova", "savona", "imperia", "la spezia", "albenga", "sanremo"],
    "LOMBARDIA": ["lombardia", "milano", "brescia", "bergamo", "mantova", "pavia",
                  "cremona", "lodi", "como", "varese", "sondrio", "valtellina", "monza"],
    "MARCHE": ["marche", "ancona", "macerata", "pesaro", "fermo", "ascoli"],
    "MOLISE": ["molise", "campobasso", "isernia", "larino"],
    "PIEMONTE": ["piemonte", "torino", "cuneo", "asti", "alessandria", "novara",
                 "vercelli", "biella", "verbania", "langhe", "monferrato"],
    "PUGLIA": ["puglia", "bari", "foggia", "lecce", "taranto", "brindisi",
               "salento", "barletta", "andria", "trani"],
    "SARDEGNA": ["sardegna", "cagliari", "sassari", "nuoro", "oristano", "olbia", "sardo"],
    "SICILIA": ["sicilia", "palermo", "catania", "messina", "siracusa", "ragusa",
                "trapani", "agrigento", "caltanissetta", "enna", "acireale", "sicilian"],
    "TOSCANA": ["toscana", "firenze", "siena", "pisa", "arezzo", "grosseto",
                "livorno", "lucca", "pistoia", "prato", "chianti", "maremma"],
    "TRENTINO-ALTO ADIGE": ["trentino", "alto adige", "sudtirol", "südtirol", "trento",
                            "bolzano", "bozen", "san michele all'adige", "val di non",
                            "vallagarina", "valsugana"],
    "UMBRIA": ["umbria", "perugia", "terni", "todi", "foligno", "orvieto"],
    "VALLE D'AOSTA": ["valle d'aosta", "vallee d'aoste", "aosta", "valdostan", "aostan"],
    "VENETO": ["veneto", "verona", "padova", "treviso", "vicenza", "venezia",
               "rovigo", "belluno", "valpolicella", "valdobbiadene", "soave"],
}

TIPO_DONO = [
    ("SERVIZIO_FITOSANITARIO", ["servizio fitosanitario", "fitosanitario regionale",
                                "consorzio fitosanitario", "ispettorato fitosanitario",
                                "osservatorio per le malattie delle piante"]),
    ("AGENZIA_REGIONALE", ["agenzia regionale", "arpa", "ersa", "assam", "amap",
                           "arsial", "alsia", "arsac", "arsarp", "laore", "agris",
                           "arif", "avepa", "ersaf", "agrion", "veneto agricoltura",
                           "ipla", "arpae"]),
    ("REGIONE", ["regione ", "provincia autonoma", "assessorato", "giunta regionale"]),
    ("UNIVERSIDADE", ["universit", "dipartimento di scienze agrar", "ateneo",
                      "facolt", "scuola superiore"]),
    ("CENTRO_PESQUISA", ["cnr", "crea", "istituto di ricerca", "centro di ricerca",
                         "fondazione edmund mach", "laimburg", "centro di sperimentazione",
                         "stazione sperimentale", "istituto sperimentale", "agrobios"]),
    ("CONSORZIO_TUTELA", ["consorzio di tutela", "consorzio tutela", "consorzio del",
                          "consorzio vini", "denominazione di origine"]),
    ("CONSORZIO_BONIFICA", ["consorzio di bonifica", "bonifica", "irrigu", "canale emiliano"]),
    ("COOPERATIVA_OP", ["cooperativa", "societa cooperativa", "organizzazione di produttori",
                        "op ", "consorzio agrario", "cantina sociale", "apo ", "asso"]),
    ("ASSOCIACAO_AGRICOLA", ["coldiretti", "confagricoltura", "cia ", "copagri",
                             "confcooperative", "legacoop", "associazione produttori",
                             "unione agricoltori", "federazione provinciale"]),
    ("ORDEM_PROFISSIONAL", ["ordine dei dottori agronomi", "collegio", "federazione dei dottori",
                            "conaf", "ordine provinciale"]),
    ("SOCIEDADE_CIENTIFICA", ["societa italiana", "accademia", "sipav", "sirfi", "aipp",
                              "societa entomologica", "soi "]),
    ("MIDIA_TECNICA", ["rivista", "testata", "giornale", "quotidiano", "magazine",
                       "notizie", "informatore", "edagricole", "image line",
                       "agronotizie", "tecniche nuove", "redazione"]),
    ("EMPRESA_INSUMOS", ["agrofarmac", "fitofarmac", "sementi", "fertilizzanti",
                         "syngenta", "bayer", "basf", "corteva", "adama", "sipcam",
                         "certis", "biogard", "koppert", "bioplanet", "gowan",
                         "nufarm", "upl", "isagro", "diachem", "cifo", "biolchim"]),
    ("CAMARA_COMERCIO", ["camera di commercio", "camcom", "unioncamere", "borsa merci"]),
    ("ESTADO_NACIONAL", ["ministero", "masaf", "agea", "ispra", "istat", "ismea",
                         "salute.gov", "governo"]),
    ("FEIRA_EVENTO", ["fiera", "expo", "salone", "congresso", "convegno", "manifestazione"]),
]

RE_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
RE_TAG = re.compile(r"<[^>]+>")
RE_RSS = re.compile(r'type\s*=\s*["\']application/(rss|atom)\+xml["\']', re.I)
RE_DATA_ISO = re.compile(r"\b(20[12][0-9])-(0[1-9]|1[0-2])-([0-3][0-9])\b")
RE_DATA_IT = re.compile(r"\b([0-3]?[0-9])[/.\-](0?[1-9]|1[0-2])[/.\-](20[12][0-9])\b")
RE_MES_IT = re.compile(
    r"\b([0-3]?[0-9])\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|"
    r"agosto|settembre|ottobre|novembre|dicembre)\s+(20[12][0-9])\b", re.I)
RE_ANO = re.compile(r"\b(20[12][0-9])\b")

_c = {"http": 0, "cache": 0, "erro": 0, "bytes": 0}
_lock = threading.Lock()


def normalizar(url):
    u = (url or "").strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    return u.split("#")[0].rstrip("/")


def host_de(url):
    try:
        h = urllib.parse.urlsplit(url).netloc.lower()
    except Exception:
        return ""
    h = h.split("@")[-1].split(":")[0]
    return h[4:] if h.startswith("www.") else h


def raiz_registavel(h):
    p = h.split(".")
    if len(p) <= 2:
        return h
    comp = {"gov.it", "edu.it", "co.uk", "org.uk", "com.br", "gov.br",
            "camcom.gov.it", "provincia.tn.it", "provincia.bz.it"}
    for n in (3, 2):
        if len(p) > n and ".".join(p[-n:]) in comp:
            return ".".join(p[-(n + 1):])
    return ".".join(p[-2:])


def chave_cache(url):
    import hashlib
    return CACHE / (hashlib.sha1(url.encode("utf-8")).hexdigest() + ".json")


def buscar(url, timeout=18, max_bytes=300_000):
    ck = chave_cache(url)
    if ck.exists():
        with _lock:
            _c["cache"] += 1
        try:
            return json.loads(ck.read_text(encoding="utf-8"))
        except Exception:
            pass
    out = {"url": url, "status": None, "final": url, "ctype": "", "html": "",
           "erro": "", "quando": time.strftime("%Y-%m-%dT%H:%M:%S")}
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.6"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            raw = r.read(max_bytes)
            out["status"] = r.status
            out["final"] = r.geturl()
            out["ctype"] = r.headers.get("Content-Type", "")
            enc = "utf-8"
            m = re.search(r"charset=([\w\-]+)", out["ctype"], re.I)
            if m:
                enc = m.group(1)
            try:
                out["html"] = raw.decode(enc, errors="replace")
            except LookupError:
                out["html"] = raw.decode("utf-8", errors="replace")
        with _lock:
            _c["http"] += 1
            _c["bytes"] += len(raw)
    except urllib.error.HTTPError as e:
        out["status"] = e.code
        out["erro"] = f"HTTP {e.code}"
        with _lock:
            _c["http"] += 1
            _c["erro"] += 1
    except Exception as e:
        out["erro"] = f"{type(e).__name__}: {str(e)[:100]}"
        with _lock:
            _c["http"] += 1
            _c["erro"] += 1
    CACHE.mkdir(parents=True, exist_ok=True)
    ck.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def texto(h):
    h = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", h or "")
    return re.sub(r"\s+", " ", RE_TAG.sub(" ", h)).strip()


def ultima_data(html):
    """A data mais recente visivel na pagina, e ela nao e prova de frescura.

    Um rodape com (c) 2026 mente sobre a idade do conteudo. Por isso guardamos
    tambem de onde a data veio: data completa vale mais do que ano solto.
    """
    cand = []
    for a, m, d in RE_DATA_ISO.findall(html):
        cand.append((int(a), int(m), int(d), "DATA_COMPLETA"))
    for d, m, a in RE_DATA_IT.findall(html):
        cand.append((int(a), int(m), int(d), "DATA_COMPLETA"))
    meses = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5,
             "giugno": 6, "luglio": 7, "agosto": 8, "settembre": 9,
             "ottobre": 10, "novembre": 11, "dicembre": 12}
    for d, mes, a in RE_MES_IT.findall(html):
        cand.append((int(a), meses[mes.lower()], int(d), "DATA_COMPLETA"))
    cand = [c for c in cand if 2010 <= c[0] <= ANO_HOJE]
    if cand:
        cand.sort(reverse=True)
        a, m, d, fonte = cand[0]
        return f"{a:04d}-{m:02d}-{min(d,28):02d}", fonte
    anos = [int(a) for a in RE_ANO.findall(html) if 2010 <= int(a) <= ANO_HOJE]
    if anos:
        return f"{max(anos)}", "SO_O_ANO"
    return "", "NAO_ENCONTRADA"


def medir(url, html, ctype):
    baixo = html.lower()
    txt = texto(html)
    tbaixo = txt.lower()
    tit = ""
    m = RE_TITLE.search(html)
    if m:
        tit = texto(m.group(1))[:220]

    agri = sorted({p for p in PALAVRA_AGRI if p in tbaixo})
    propria = sorted({p for p in MARCA_INFO_PROPRIA if p in tbaixo})
    period = sorted({p for p in MARCA_PERIODICA if p in tbaixo})
    prim = sorted({p for p in MARCA_PRIMARIA if p in tbaixo})
    agreg = sorted({p for p in MARCA_AGREGADOR if p in tbaixo})
    loja = sorted({p for p in MARCA_LOJA if p in tbaixo})

    h = host_de(url)
    it_dominio = h.endswith(".it")
    palavras_it = sum(1 for w in (" di ", " della ", " per ", " sono ", " con ",
                                  " nel ", " alla ", " gli ", " che ", " una ")
                      if w in tbaixo)
    it_conteudo = palavras_it >= 4
    de_dominio = h.endswith(".de") or h.endswith(".at")

    regs = sorted({r for r, palavras in REGIOES.items()
                   if any(p in tbaixo for p in palavras)})
    tipos = [t for t, palavras in TIPO_DONO if any(p in tbaixo for p in palavras)]

    data, fonte_data = ultima_data(html)
    ano_data = int(data[:4]) if data[:4].isdigit() else None

    return {
        "TITULO": tit,
        "HTTP_CTYPE": ctype,
        "TAMANHO_TEXTO": len(txt),
        "AGRI_PALAVRAS": agri,
        "AGRI_N": len(agri),
        "INFO_PROPRIA_MARCAS": propria,
        "INFO_PROPRIA_N": len(propria),
        "PERIODICIDADE_MARCAS": period,
        "PRIMARIA_MARCAS": prim,
        "AGREGADOR_MARCAS": agreg,
        "LOJA_MARCAS": loja,
        "TEM_RSS": bool(RE_RSS.search(html)),
        "ITALIA_DOMINIO": it_dominio,
        "ITALIA_CONTEUDO": it_conteudo,
        "DOMINIO_DE_AT": de_dominio,
        "REGIOES_NO_TEXTO": regs,
        "TIPO_DONO": tipos,
        "ULTIMA_DATA_VISTA": data,
        "ULTIMA_DATA_FONTE": fonte_data,
        "ULTIMA_DATA_ANO": ano_data,
    }


def classificar(reg, med):
    """Diz a classe E a razao. Classe sem razao ao lado nao se pode auditar."""
    razoes = []
    host = reg["HOST_RAIZ"]

    for marca, motivo in MOTIVO_INFRA.items():
        if host == marca or host.endswith("." + marca):
            return "REJECT", [f"nao e fonte: {motivo}"], "AGGREGATOR"

    if med is None:
        return "UNKNOWN", ["nao abriu: " + (reg.get("HTTP_ERRO") or "sem resposta")], "UNKNOWN"

    st = reg.get("HTTP_STATUS")
    if st is None or st >= 400:
        return "UNKNOWN", [f"HTTP {st} — nao foi possivel medir"], "UNKNOWN"

    # ── site morto com HTTP 200: o caso que o red team procura ──
    if med["TAMANHO_TEXTO"] < 400:
        return "REJECT", [f"HTTP {st} mas a pagina tem {med['TAMANHO_TEXTO']} "
                          f"caracteres de texto — casca, nao conteudo"], "UNKNOWN"

    agri = med["AGRI_N"]
    propria = med["INFO_PROPRIA_N"]
    italia = med["ITALIA_DOMINIO"] or med["ITALIA_CONTEUDO"] or med["DOMINIO_DE_AT"]

    if not italia:
        return "REJECT", ["sem ligacao provada a Italia: dominio nao-.it e "
                          "conteudo nao-italiano"], "UNKNOWN"
    if agri == 0:
        return "REJECT", ["zero palavras do oficio agricola na pagina"], "UNKNOWN"
    if agri <= 2 and propria == 0:
        return "REJECT", [f"sinal agricola minimo ({agri} palavra(s)) e nenhuma "
                          f"marca de informacao propria"], "UNKNOWN"
    if len(med["LOJA_MARCAS"]) >= 3 and propria <= 1:
        return "REJECT", [f"loja: {', '.join(med['LOJA_MARCAS'][:3])} — "
                          f"vende, nao informa"], "AGGREGATOR"

    # ── proximidade ──
    tipos = med["TIPO_DONO"]
    if any(t in tipos for t in ("SERVIZIO_FITOSANITARIO", "AGENZIA_REGIONALE",
                                "CENTRO_PESQUISA", "CAMARA_COMERCIO")) or med["PRIMARIA_MARCAS"]:
        prox = "PRIMARY"
    elif any(t in tipos for t in ("UNIVERSIDADE", "REGIONE", "CONSORZIO_TUTELA",
                                  "CONSORZIO_BONIFICA", "COOPERATIVA_OP",
                                  "ASSOCIACAO_AGRICOLA", "ORDEM_PROFISSIONAL",
                                  "SOCIEDADE_CIENTIFICA", "ESTADO_NACIONAL",
                                  "EMPRESA_INSUMOS")):
        prox = "NEAR_PRIMARY"
    elif "MIDIA_TECNICA" in tipos:
        prox = "SECONDARY"
    elif med["AGREGADOR_MARCAS"]:
        prox = "AGGREGATOR"
    else:
        prox = "UNKNOWN"

    # ── recorrencia ──
    ano = med["ULTIMA_DATA_ANO"]
    data_completa = med["ULTIMA_DATA_FONTE"] == "DATA_COMPLETA"
    fresca = bool(ano and ano >= ANO_HOJE - 1)
    if propria >= 3 and med["PERIODICIDADE_MARCAS"] and fresca and data_completa:
        rec = "HIGH"
    elif propria >= 2 and fresca:
        rec = "MEDIUM"
    elif propria >= 1:
        rec = "LOW"
    else:
        rec = "UNKNOWN"
    if med["TEM_RSS"] and rec in ("LOW", "UNKNOWN"):
        rec = "MEDIUM"

    identidade = bool(med["TITULO"]) and med["TAMANHO_TEXTO"] >= 800

    # ── a classe ──
    if (prox in ("PRIMARY", "NEAR_PRIMARY") and rec == "HIGH"
            and agri >= 6 and identidade):
        classe = "A"
        razoes.append(f"dona/vizinha do facto ({prox}) · {propria} marcas de "
                      f"informacao propria · periodicidade declarada · "
                      f"data recente {med['ULTIMA_DATA_VISTA']} · "
                      f"{agri} palavras do oficio")
    elif prox in ("PRIMARY", "NEAR_PRIMARY") and rec in ("HIGH", "MEDIUM") and agri >= 4:
        classe = "B"
        razoes.append(f"{prox} · recorrencia {rec} · {agri} palavras do oficio · "
                      f"ultima data vista {med['ULTIMA_DATA_VISTA'] or 'NAO SEI'}")
    elif agri >= 8 and propria >= 2:
        classe = "B"
        razoes.append(f"sinal agricola denso ({agri}) e {propria} marcas de "
                      f"informacao propria, mas dono nao identificado com "
                      f"seguranca — proximidade {prox}")
    elif agri >= 3 and propria >= 1:
        classe = "C"
        razoes.append(f"sinal agricola presente ({agri}) e alguma informacao "
                      f"propria ({propria}), mas nao central — recorrencia {rec}")
    elif agri >= 3:
        classe = "HOLD"
        razoes.append(f"{agri} palavras do oficio e NENHUMA marca de informacao "
                      f"propria: pode ser fonte sem que a homepage o mostre")
    else:
        classe = "HOLD"
        razoes.append(f"indicios fracos: agri={agri}, propria={propria}")

    if ano and ano <= ANO_HOJE - 4:
        classe = "HOLD" if classe in ("A", "B") else classe
        razoes.append(f"a data mais recente visivel e {med['ULTIMA_DATA_VISTA']} — "
                      f"possivel abandono; nao fica A/B sem prova de frescura")
    if med["ULTIMA_DATA_FONTE"] == "SO_O_ANO":
        razoes.append("a idade vem de um ano solto na pagina (rodape?), "
                      "nao de uma data completa — frescura NAO PROVADA")

    return classe, razoes, prox


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    desc = json.loads((TRABALHO / "CRAWL-DISCOVERIES.json").read_text(encoding="utf-8"))
    por_raiz = {d["HOST_RAIZ"]: d for d in desc}

    # as URLs que vieram da busca por palavra entram no mesmo balcao — de todas
    # as rodadas. urls-from-websearch.txt e a rodada 2; urls-round3.txt e a
    # rodada 3, que voltou de proposito as regioes que ficaram fracas.
    n_extra = 0
    linhas_extra = []
    for extra in sorted((TRABALHO / "search").glob("urls-*.txt")):
        linhas_extra += extra.read_text(encoding="utf-8").splitlines()
    if linhas_extra:
        for linha in linhas_extra:
            u = linha.strip()
            if not u.startswith("http"):
                continue
            r = raiz_registavel(host_de(u))
            if not r:
                continue
            n_extra += 1
            d = por_raiz.setdefault(r, {
                "HOST_RAIZ": r, "HOSTS": [], "N_LINKS_RECEBIDOS": 0,
                "N_DESCOBRIDORES": 0, "URLS_TOP": [], "ANCORAS": [],
                "DISCOVERED_FROM": [], "REGIOES_DO_DESCOBRIDOR": []})
            if u not in d["URLS_TOP"]:
                d["URLS_TOP"] = [u] + d["URLS_TOP"][:5]
            if "WebSearch" not in d["DISCOVERED_FROM"]:
                d["DISCOVERED_FROM"] = ["WebSearch (busca por palavra)"] + d["DISCOVERED_FROM"][:5]
    print(f"HOSTS A MEDIR = {len(por_raiz)}  (do grafo: {len(desc)}, "
          f"da busca: {n_extra} URLs)")

    # ── decidir o que sondar ──
    a_sondar, rejeitados_sem_sonda = [], []
    for r, d in por_raiz.items():
        infra = None
        for marca, motivo in MOTIVO_INFRA.items():
            if r == marca or r.endswith("." + marca):
                infra = motivo
                break
        if infra:
            rejeitados_sem_sonda.append((r, d, infra))
            continue
        a_sondar.append((r, d))
    print(f"  infraestrutura/plataforma, rejeitada sem sonda: {len(rejeitados_sem_sonda)}")
    print(f"  a sondar de verdade: {len(a_sondar)}")

    def trabalha(item):
        r, d = item
        # A melhor URL primeiro: a que o grafo viu mais vezes. A raiz do host
        # e' o plano B — porque muitas fontes vivem num caminho, nao na home.
        tentativas = []
        for u in (d.get("URLS_TOP") or [])[:2]:
            tentativas.append(u)
        tentativas.append(f"https://{r}/")
        tentativas.append(f"http://{r}/")
        melhor = None
        for u in tentativas:
            res = buscar(u)
            if res.get("status") == 200 and res.get("html"):
                melhor = res
                break
            if melhor is None:
                melhor = res
        med = None
        if melhor and melhor.get("html"):
            med = medir(melhor.get("final") or melhor["url"], melhor["html"],
                        melhor.get("ctype", ""))
        reg = {
            "HOST_RAIZ": r,
            "URL_DISCOVERED": (d.get("URLS_TOP") or [f"https://{r}/"])[0],
            "URL_PROBED": melhor["url"] if melhor else f"https://{r}/",
            "URL_FINAL": (melhor.get("final") if melhor else "") or "",
            "HTTP_STATUS": melhor.get("status") if melhor else None,
            "HTTP_ERRO": melhor.get("erro") if melhor else "",
            "N_DESCOBRIDORES": d.get("N_DESCOBRIDORES", 0),
            "N_LINKS_RECEBIDOS": d.get("N_LINKS_RECEBIDOS", 0),
            "ANCORAS": (d.get("ANCORAS") or [])[:8],
            "DISCOVERED_FROM": (d.get("DISCOVERED_FROM") or [])[:4],
            "REGIOES_DO_DESCOBRIDOR": d.get("REGIOES_DO_DESCOBRIDOR") or [],
            "HOSTS": d.get("HOSTS") or [r],
        }
        classe, razoes, prox = classificar(reg, med)
        reg["MEDIDA"] = med
        reg["PRE_CLASSE"] = classe
        reg["PRE_CLASSE_RAZAO"] = razoes
        reg["INFORMATION_PROXIMITY"] = prox
        if med:
            ano = med["ULTIMA_DATA_ANO"]
            propria = med["INFO_PROPRIA_N"]
            fresca = bool(ano and ano >= ANO_HOJE - 1)
            if propria >= 3 and med["PERIODICIDADE_MARCAS"] and fresca \
                    and med["ULTIMA_DATA_FONTE"] == "DATA_COMPLETA":
                reg["RECURRING_INFORMATION_POTENTIAL"] = "HIGH"
            elif propria >= 2 and fresca:
                reg["RECURRING_INFORMATION_POTENTIAL"] = "MEDIUM"
            elif propria >= 1 or med["TEM_RSS"]:
                reg["RECURRING_INFORMATION_POTENTIAL"] = "LOW"
            else:
                reg["RECURRING_INFORMATION_POTENTIAL"] = "UNKNOWN"
            # estado do endereco
            if reg["URL_FINAL"] and normalizar(reg["URL_FINAL"]) != normalizar(reg["URL_PROBED"]):
                reg["URL_STATUS"] = "REDIRECT"
            elif med["TAMANHO_TEXTO"] < 400:
                reg["URL_STATUS"] = "VALID_BUT_GENERIC"
            else:
                reg["URL_STATUS"] = "CANONICAL"
        else:
            reg["RECURRING_INFORMATION_POTENTIAL"] = "UNKNOWN"
            reg["URL_STATUS"] = "BROKEN" if reg["HTTP_STATUS"] else "UNKNOWN"
        return reg

    saida = []
    for r, d, motivo in rejeitados_sem_sonda:
        saida.append({
            "HOST_RAIZ": r, "URL_DISCOVERED": (d.get("URLS_TOP") or [f"https://{r}/"])[0],
            "URL_PROBED": "", "URL_FINAL": "", "HTTP_STATUS": None, "HTTP_ERRO": "",
            "N_DESCOBRIDORES": d.get("N_DESCOBRIDORES", 0),
            "N_LINKS_RECEBIDOS": d.get("N_LINKS_RECEBIDOS", 0),
            "ANCORAS": (d.get("ANCORAS") or [])[:8],
            "DISCOVERED_FROM": (d.get("DISCOVERED_FROM") or [])[:4],
            "REGIOES_DO_DESCOBRIDOR": d.get("REGIOES_DO_DESCOBRIDOR") or [],
            "HOSTS": d.get("HOSTS") or [r], "MEDIDA": None,
            "PRE_CLASSE": "REJECT", "PRE_CLASSE_RAZAO": [f"nao e fonte: {motivo}"],
            "INFORMATION_PROXIMITY": "AGGREGATOR",
            "RECURRING_INFORMATION_POTENTIAL": "UNKNOWN",
            "URL_STATUS": "UNKNOWN", "SONDADO": False,
        })

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=12) as ex:
        for i, reg in enumerate(ex.map(trabalha, a_sondar), 1):
            reg["SONDADO"] = True
            saida.append(reg)
            if i % 250 == 0:
                print(f"    sondados {i}/{len(a_sondar)} "
                      f"({time.time()-t0:.0f}s, http={_c['http']}, cache={_c['cache']})")

    (TRABALHO / "PROBE.json").write_text(
        json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    from collections import Counter
    cc = Counter(x["PRE_CLASSE"] for x in saida)
    print("\nPRE-CLASSE (maquina, antes da leitura humana):")
    for k in ("A", "B", "C", "HOLD", "UNKNOWN", "REJECT"):
        print(f"  {k:8s} {cc.get(k,0)}")
    cp = Counter(x["INFORMATION_PROXIMITY"] for x in saida)
    print("PROXIMIDADE:", dict(cp))
    cr = Counter(x["RECURRING_INFORMATION_POTENTIAL"] for x in saida)
    print("RECORRENCIA:", dict(cr))
    print(f"\nPEDIDOS={_c['http']} CACHE={_c['cache']} ERROS={_c['erro']} "
          f"BYTES={_c['bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
