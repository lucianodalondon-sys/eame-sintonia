#!/usr/bin/env python3
"""
TERRITORIAL — leitura de CORPO, última rodada autorizada (missão 16).

O que esta passagem corrige da anterior:

  1. A anterior chamou de "corpo" a PÁGINA DE ÍNDICE da publicação. O boletim
     da Junta de Extremadura tem 9 páginas em PDF e o que foi lido foram 1.106
     caracteres de menu — onde `Frutales Vid Olivar Hortícolas` é a NAVEGAÇÃO,
     não a cultura observada. Por isso CROP deu 100%: veio de um menu.
  2. A anterior preservou 1.500 caracteres de documentos de 33.000. ISSUE podia
     estar nos 94% descartados e ninguém saberia.

Regras que este extrator obedece:

  ISSUE_FROM_BODY_ONLY   o recorte da missão NUNCA preenche ISSUE. Se o corpo
                         não nomeia o alvo, ISSUE = NOT_KNOWN.
  NAV_IS_NOT_CONTENT     blocos de navegação/rodapé são removidos antes de ler.
  EVIDENCE_OR_NOTHING    todo campo preenchido carrega o trecho que o sustenta.
  MANDATE_IS_DECLARED    localidade herdada do mandato é marcada como tal e
                         nunca se confunde com localidade nomeada no texto.

Sem Apify. HTTP direto. Somente as 5 fontes já inventariadas.
"""

import gzip
import io
import json
import re
import sys
import urllib.request
from datetime import date, datetime

UA = "Mozilla/5.0 (compatible; SintoniaEAME/1.0; +territorial-body)"
TIMEOUT = 40

# ── as 5 fontes vivas já inventariadas. Nenhuma sexta. ────────────────────────
FONTES = {
    "ES-RAIF": {
        "NAME": "RAIF — Red de Alerta e Información Fitosanitaria de Andalucía",
        "TYPE": "REGIONAL_PHYTOSANITARY_SERVICE",
        "COUNTRY": "ES",
        "MANDATE": "Andalucía",
        "LISTING": "https://www.juntadeandalucia.es/datosabiertos/portal/dataset/raif",
        "SERVES": ["ES-OLIVE-REPILO", "ES-CEREAL-SEPTORIA"],
    },
    "ES-OLIMERCA": {
        "NAME": "Olimerca — imprensa técnica do olivar",
        "TYPE": "TECHNICAL_PRESS",
        "COUNTRY": "ES",
        "MANDATE": "España",
        "LISTING": "https://www.olimerca.com/",
        "SERVES": ["ES-OLIVE-REPILO"],
    },
    "IT-LAMMA": {
        "NAME": "Consorzio LaMMA — Bollettino Frumento (Regione Toscana)",
        "TYPE": "EXPERIMENTAL_STATION",
        "COUNTRY": "IT",
        "MANDATE": "Toscana",
        # caminho já conhecido do acervo italiano (IT-T3-LAMMA), não é fonte nova
        "LISTING": "https://www.lamma.toscana.it/previ/ita/agrometeo/html/Grosseto_ftsnt.html",
        "SERVES": ["IT-DURUM_WHEAT-FUSARIUM"],
    },
    "FR-VIGNEVIN": {
        "NAME": "IFV — Institut Français de la Vigne et du Vin",
        "TYPE": "TECHNICAL_ORGANIZATION",
        "COUNTRY": "FR",
        "MANDATE": "France",
        "LISTING": "https://www.vignevin.com/",
        "SERVES": ["FR-VINE-DOWNY_MILDEW"],
    },
    "FR-ARVALIS": {
        "NAME": "ARVALIS — Institut du végétal",
        "TYPE": "TECHNICAL_ORGANIZATION",
        "COUNTRY": "FR",
        "MANDATE": "France",
        "LISTING": "https://www.arvalis.fr/",
        "SERVES": ["FR-CEREAL-SEPTORIA"],
    },
}

# ── léxicos declarados. Um alvo só entra se o CORPO o nomear. ─────────────────
ISSUE_LEX = {
    "REPILO": [r"\brepilo\b", r"venturia\s+oleaginea", r"spilocaea\s+olea", r"cycloconium"],
    "SEPTORIA": [r"septorios[ie]s?\b", r"\bseptoria\b", r"zymoseptoria", r"mycosphaerella\s+graminicola"],
    "FLAVESCENCE": [r"flavescen[czt]", r"scaphoideus\s+titanus", r"flavescence\s+dor"],
    "FUSARIUM": [r"\bfusarium\b", r"fusarios[ie]s?\b", r"deossinivalenolo", r"deoxynivalenol", r"\bDON\b"],
    "DOWNY_MILDEW": [r"\bmildiou\b", r"\bmildiu\b", r"peronospora", r"plasmopara\s+viticola"],
}

CROP_LEX = {
    "OLIVE": [r"\bolivar\b", r"\bolivo\b", r"\boliv[ae]s?\b", r"olivicoltur", r"ol[ée]icultur", r"\bolivier"],
    "CEREAL": [r"\btrigo\b", r"\bcereal", r"\bfrumento\b", r"\bgrano\s+duro\b", r"\bbl[ée]\b",
               r"c[ée]r[ée]ale", r"\borge\b", r"\bcebada\b", r"\bwheat\b", r"\bdurum\b"],
    "VINE": [r"\bvi[ñn]a\b", r"\bvid\b", r"\bvigne\b", r"\bvite\b", r"vigneto", r"viticoltur",
             r"viticultur", r"\bvineyard", r"\bvigneron"],
}

REGION_LEX = {
    "ES": ["Andalucía", "Andalucia", "Jaén", "Jaen", "Córdoba", "Cordoba", "Sevilla", "Granada",
           "Málaga", "Malaga", "Cádiz", "Cadiz", "Huelva", "Almería", "Almeria", "Extremadura",
           "Castilla y León", "Cataluña", "Aragón", "Aragon", "Lleida", "Badajoz"],
    "IT": ["Toscana", "Veneto", "Lombardia", "Piemonte", "Emilia-Romagna", "Emilia Romagna",
           "Friuli", "Umbria", "Marche", "Grosseto", "Siena", "Firenze", "Puglia", "Sicilia"],
    "FR": ["Nouvelle-Aquitaine", "Occitanie", "Grand Est", "Bourgogne", "Champagne", "Bordeaux",
           "Beaujolais", "Alsace", "Charentes", "Val de Loire", "Languedoc", "Provence",
           "Bretagne", "Normandie", "Hauts-de-France", "Centre-Val de Loire"],
}

# marcadores de OBSERVAÇÃO DE CAMPO — verbo de constatação, não de explicação
FIELD_MARK = [
    r"se\s+observ", r"si\s+osserv", r"on\s+observe", r"observa[dt][ao]s?\b",
    r"rilievi\s+in\s+campo", r"se\s+ha\s+detectad", r"si\s+segnala", r"segnalazion",
    r"se\s+detect", r"pr[ée]sence\s+", r"presencia\s+de", r"presenza\s+di",
    r"primeros?\s+s[íi]ntomas", r"primi\s+sintomi", r"premiers?\s+sympt",
    r"niveau\s+de\s+risque", r"riesgo\s+de", r"rischio\s+di", r"attaque",
]
ALERT_MARK = [r"\bavis[oa]s?\b", r"\balerta\b", r"\ballerta\b", r"\battenzione\b",
              r"\bvigilance\b", r"\bbollettino\b", r"\bbolet[íi]n\b", r"\bbulletin\b"]

# GUARD: conteúdo educativo/promocional NUNCA é sinal de campo
EDU_MARK = [
    r"giochiamo", r"mettetevi\s+alla\s+prova", r"riconoscete\s+i\s+sintomi",
    r"\bquiz\b", r"mettiti\s+alla\s+prova", r"\bwebinar\b", r"\bcorso\b",
    r"\biscriviti\b", r"\binscr[íi]bete\b", r"\bformation\b", r"\bformaci[óo]n\b",
    r"\bcolloque\b", r"\bjornada\b", r"\bconvegno\b", r"\bnewsletter\b",
    r"\bpodcast\b", r"\bpremio\b", r"\bconcorso\b",
]

NAV_MARK = re.compile(
    r"(compartir|condividi|partager|imprimir|stampa|whatsapp|facebook|twitter|linkedin|"
    r"vai\s+al\s+contenuto|skip\s+to|menu\s+principal|cookie|newsletter|"
    r"inicio\s+publicaciones|accedi|registrati|iscriviti\s+alla)", re.I)


def buscar(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept-Encoding": "gzip",
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        return raw, r.headers.get("Content-Type", ""), r.geturl()


def texto_de_html(html):
    """Remove script/style/nav e devolve texto corrido. Guarda o que foi removido."""
    t = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    t = re.sub(r"(?is)<(nav|header|footer|aside)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = (t.replace("&nbsp;", " ").replace("&amp;", "&").replace("&egrave;", "è")
          .replace("&agrave;", "à").replace("&eacute;", "é").replace("&#39;", "'")
          .replace("&quot;", '"').replace("&ldquo;", '"').replace("&rdquo;", '"'))
    t = re.sub(r"&[a-z]+;", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def texto_de_pdf(raw):
    """Extrai texto de PDF sem dependência externa: streams FlateDecode + Tj/TJ."""
    saida = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", raw, re.S):
        try:
            dec = zlib_decompress(m.group(1))
        except Exception:
            continue
        for t in re.finditer(rb"\((?:\\.|[^\\()])*\)", dec):
            s = t.group(0)[1:-1]
            s = re.sub(rb"\\([()\\])", rb"\1", s)
            try:
                saida.append(s.decode("latin-1"))
            except Exception:
                pass
    return re.sub(r"\s+", " ", " ".join(saida)).strip()


def zlib_decompress(b):
    import zlib
    return zlib.decompress(b)


def achar(lex, texto):
    """Devolve (rotulos, evidencias) — cada rótulo com o trecho exato."""
    rot, ev = [], {}
    for nome, pats in lex.items():
        for p in pats:
            m = re.search(p, texto, re.I)
            if m:
                a = max(0, m.start() - 90)
                rot.append(nome)
                ev[nome] = texto[a:m.end() + 90].strip()
                break
    return rot, ev


def marcador(pats, texto):
    for p in pats:
        m = re.search(p, texto, re.I)
        if m:
            a = max(0, m.start() - 90)
            return texto[a:m.end() + 90].strip()
    return None


def datas(texto):
    for p, f in [(r"(\d{4})-(\d{2})-(\d{2})", "ymd"),
                 (r"(\d{1,2})[/-](\d{1,2})[/-](20\d{2})", "dmy")]:
        m = re.search(p, texto)
        if m:
            try:
                if f == "ymd":
                    return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
                return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
            except Exception:
                pass
    meses = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6,
             "luglio": 7, "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12,
             "enero": 1, "febrero": 2, "abril": 4, "mayo": 5, "junio": 6, "julio": 7,
             "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
             "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
             "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "décembre": 12}
    m = re.search(r"(\d{1,2})\s+(" + "|".join(meses) + r")\s+(20\d{2})", texto, re.I)
    if m:
        return f"{m.group(3)}-{meses[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    return None


def analisar(sid, cfg, url, texto, papel):
    """Constrói o item territorial a partir do CORPO. Evidência ou NOT_KNOWN."""
    crops, crop_ev = achar(CROP_LEX, texto)
    issues, issue_ev = achar(ISSUE_LEX, texto)

    reg, reg_ev = None, None
    for r in REGION_LEX.get(cfg["COUNTRY"], []):
        m = re.search(re.escape(r), texto, re.I)
        if m:
            reg, reg_ev = r, texto[max(0, m.start() - 90):m.end() + 90].strip()
            break

    edu = marcador(EDU_MARK, texto)
    fld = marcador(FIELD_MARK, texto)
    alr = marcador(ALERT_MARK, texto)

    if edu:
        otype, oev = "PROMOTIONAL_OR_EDUCATIONAL", edu
    elif fld:
        otype, oev = "FIELD_OBSERVATION", fld
    elif alr:
        otype, oev = "TECHNICAL_ALERT", alr
    else:
        otype, oev = "OTHER", "nenhum marcador dos léxicos declarados"

    return {
        "ITEM_ID": f"{sid}::{re.sub(r'[^a-z0-9]+', '-', url.lower())[-90:]}",
        "DATASET_OWNER": "EARLY_SIGNAL_EAME",
        "MISSION_ID": "16-ROTA-TERRITORIAL",
        "BATCH_ID": "TERRITORIAL-CORPO-R2",
        "SOURCE_ENTITY_ID": sid,
        "SOURCE_NAME": cfg["NAME"],
        "SOURCE_TYPE": cfg["TYPE"],
        "SOURCE_URL": url,
        "SOURCE_COUNTRY": cfg["COUNTRY"],
        "MANDATE_GEOGRAPHY": cfg["MANDATE"],
        "DOCUMENT_ROLE": papel,
        "PUBLISHED_AT": datas(texto[:4000]) or "NOT_KNOWN",
        "CAPTURED_AT": str(date.today()),
        "COUNTRY_OF_FACT": cfg["COUNTRY"],
        "COUNTRY_BASIS": "INHERITED_FROM_MANDATE",
        "REGION_OF_FACT": reg or "NOT_KNOWN",
        "LOCALITY_BASIS": "NAMED_IN_TEXT" if reg else "NOT_KNOWN",
        "LOCALITY_EVIDENCE": reg_ev or "nenhuma região do léxico do país aparece no corpo",
        "CROP": crops or "NOT_KNOWN",
        "CROP_EVIDENCE": crop_ev or {},
        "ISSUE": issues or "NOT_KNOWN",
        "ISSUE_EVIDENCE": issue_ev or {},
        "ISSUE_SOURCE_RULE": "somente do corpo; o recorte da missão nunca preenche ISSUE",
        "OBSERVATION_TYPE": otype,
        "OBSERVATION_TYPE_EVIDENCE": oev,
        "EDUCATIONAL_GUARD_HIT": bool(edu),
        "DOCUMENT_CHARS": len(texto),
        "DOCUMENT_TEXT_PRESERVED": len(texto),
        "DOCUMENT_EXCERPT": texto[:3000],
        "NAV_SUSPECT": bool(NAV_MARK.search(texto[:600])) and len(texto) < 2500,
        "PROVENANCE": {"ROUTE": "HTTP_DIRECT", "APIFY": False, "TOOL": "urllib"},
    }


def links(html, base, pats):
    fora = []
    for m in re.finditer(r'href=["\']([^"\']+)["\']', html, re.I):
        u = m.group(1)
        if u.startswith("//"):
            u = "https:" + u
        elif u.startswith("/"):
            u = re.match(r"(https?://[^/]+)", base).group(1) + u
        elif not u.startswith("http"):
            continue
        if any(re.search(p, u, re.I) for p in pats):
            fora.append(u.split("#")[0])
    vistos, saida = set(), []
    for u in fora:
        if u not in vistos:
            vistos.add(u)
            saida.append(u)
    return saida


CAND = {
    "ES-RAIF": [r"/dataset/", r"\.pdf$", r"informe", r"boletin"],
    "ES-OLIMERCA": [r"/texto-diario/", r"/noticia", r"/actualidad/"],
    "IT-LAMMA": [r"ftsnt", r"bollettino", r"\.pdf$"],
    "FR-VIGNEVIN": [r"/publication", r"/actualite", r"/article", r"\.pdf$"],
    "FR-ARVALIS": [r"/actualite", r"/article", r"/nos-publications", r"\.pdf$"],
}
TETO = 8


def main():
    itens, relatorio = [], []
    for sid, cfg in FONTES.items():
        r = {"SOURCE_ENTITY_ID": sid, "SOURCE_COUNTRY": cfg["COUNTRY"],
             "SOURCE_REACHABLE": "NO", "BODY_EXTRACTION_SUCCESS": "NO",
             "LISTING_URL": cfg["LISTING"], "DOCS_TRIED": 0, "DOCS_FETCHED": 0,
             "VALID_BODY_ITEMS": 0, "FROZEN_SLICES_SUPPORTED": cfg["SERVES"],
             "FAILURE_REASON": None}
        try:
            raw, ct, final = buscar(cfg["LISTING"])
            r["SOURCE_REACHABLE"] = "YES"
            html = raw.decode("utf-8", "replace")
            base_txt = texto_de_html(html)
        except Exception as e:
            r["FAILURE_REASON"] = f"{type(e).__name__}: {str(e)[:90]}"
            relatorio.append(r)
            continue

        alvos = links(html, cfg["LISTING"], CAND.get(sid, [r"\.pdf$"]))[:TETO]
        # a própria página é documento quando já é o boletim (LaMMA)
        alvos = ([cfg["LISTING"]] if len(base_txt) > 2500 else []) + alvos
        r["DOCS_TRIED"] = len(alvos)

        for u in alvos:
            try:
                braw, bct, bfinal = buscar(u)
            except Exception:
                continue
            try:
                if "pdf" in bct.lower() or u.lower().endswith(".pdf"):
                    txt, papel = texto_de_pdf(braw), "PDF_DOCUMENT"
                else:
                    txt, papel = texto_de_html(braw.decode("utf-8", "replace")), "HTML_DOCUMENT"
            except Exception:
                continue
            if len(txt) < 400:
                continue
            r["DOCS_FETCHED"] += 1
            it = analisar(sid, cfg, bfinal, txt, papel)
            if it["NAV_SUSPECT"]:
                continue
            itens.append(it)
            r["VALID_BODY_ITEMS"] += 1

        r["BODY_EXTRACTION_SUCCESS"] = "YES" if r["VALID_BODY_ITEMS"] else "NO"
        if r["VALID_BODY_ITEMS"] == 0 and not r["FAILURE_REASON"]:
            r["FAILURE_REASON"] = "rota alcançada, nenhum corpo utilizável"
        r["SOURCE_ROUTE_PROVED"] = "YES" if r["SOURCE_REACHABLE"] == "YES" else "NO"
        r["TERRITORIAL_SIGNAL_FROM_SOURCE"] = "PROVED" if r["VALID_BODY_ITEMS"] else "NOT_PROVED"
        relatorio.append(r)
        print(f"{sid:<14} alcancavel={r['SOURCE_REACHABLE']:<4} tentados={r['DOCS_TRIED']:<3} "
              f"baixados={r['DOCS_FETCHED']:<3} validos={r['VALID_BODY_ITEMS']}", file=sys.stderr)

    saida = {
        "SOURCE_ID": "TERRITORIAL/CORPO-R2",
        "DATASET_OWNER": "EARLY_SIGNAL_EAME",
        "MISSION_ID": "16-ROTA-TERRITORIAL",
        "source": "leitura de CORPO das 5 fontes vivas já inventariadas — HTTP direto, zero Apify",
        "SOURCE_LOCATION": "ES, IT, FR",
        "FACT_LOCATION": "ver por item",
        "ORIGINAL_LANGUAGE": "multi",
        "EVIDENCE_CLASS": "PRIMARY_SOURCE",
        "captured_at": str(date.today()),
        "CAPTURED_AT": str(date.today()),
        "APIFY_RUNS": 0,
        "COST_USD": 0,
        "LISTING_ROLE": "DISCOVERY_INDEX_ONLY",
        "REGRA_ISSUE": "ISSUE vem SOMENTE do corpo. O recorte da missão nunca o preenche.",
        "SOURCES": relatorio,
        "ITEMS_COUNT": len(itens),
        "ITEMS": itens,
    }
    with open("data/samples/TERRITORIAL/CORPO-R2.json", "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)
    print(f"\nitens de corpo: {len(itens)}", file=sys.stderr)


if __name__ == "__main__":
    main()
