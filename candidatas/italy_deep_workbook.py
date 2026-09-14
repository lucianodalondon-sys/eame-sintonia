#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A PLANILHA — junta sonda, busca e acervo, e escreve onde cada linha veio.

Tres coisas que este ficheiro se recusa a fazer, porque cada uma delas ja
estragou uma contagem nesta casa:

1 · NAO deduz a regiao pelo nome do dominio. 'agrisicilia.it' pode ser uma
    empresa de Milao. A regiao so e afirmada quando as palavras da regiao
    aparecem no TEXTO da pagina, e a coluna REGION_EVIDENCE diz isso.
    Quando nao aparece: REGION = 'NAO SEI'. Ausencia nao vira negativo.

2 · NAO conta canal novo como organizacao nova. O YouTube do Beratungsring e
    o site do Beratungsring sao DUAS linhas e UM dono. As colunas
    NEW_VS_EXISTING e RELATED_OWNER guardam a diferenca.

3 · NAO chama fonte ao que ainda e candidata. Nenhum SOURCE_ID nasce aqui.
    Nenhum DOCUMENT_ID nasce aqui. A classe A/B e uma PROPOSTA de
    prioridade, e diz em que prova se apoia.

O CSV import-ready sai no formato exato que `candidatas/fonte_nova.py` aceita
(TIPO · PAIS · NOME · URL · PARA_QUE_SERVE · QUEM_VIU · ONDE_VIU · NOTA) — e
nao e executado. Ficheiro pronto nao e ingestao feita.
"""

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

TRABALHO = Path(sys.argv[1] if len(sys.argv) > 1
                else "C:/Users/London1/AppData/Local/Temp/sintonia-italy-deep")
DESTINO = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent
HOJE = "2026-09-14"
QUEM_VIU = "claude-code (missao ITALY-DEEP-SOURCE-RESEARCH, 2026-09-14)"

REGIOES_20 = ["ABRUZZO", "BASILICATA", "CALABRIA", "CAMPANIA", "EMILIA-ROMAGNA",
              "FRIULI-VENEZIA GIULIA", "LAZIO", "LIGURIA", "LOMBARDIA", "MARCHE",
              "MOLISE", "PIEMONTE", "PUGLIA", "SARDEGNA", "SICILIA", "TOSCANA",
              "TRENTINO-ALTO ADIGE", "UMBRIA", "VALLE D'AOSTA", "VENETO"]

# A taxonomia vem do dono, nao de uma copia aqui. Esta lista estava certa —
# batia com o atlas linha por linha — e ainda assim saiu: uma copia certa hoje e
# uma copia errada no dia em que o atlas mudar e ninguem se lembrar deste
# ficheiro. Ver `_territorios.py`.
_RAIZ_REPO = Path(__file__).resolve().parents[1]
if str(_RAIZ_REPO) not in sys.path:
    sys.path.insert(0, str(_RAIZ_REPO))
import _territorios as _T  # noqa: E402

TERRITORIOS = _T.TERRITORIOS

# Territorio deduzido do que a pagina mostra. Uma fonte cobre varios.
SINAL_TERRITORIO = [
    ("T3", ["fitosanitar", "difesa integrata", "parassit", "avversita", "infestant",
            "diserb", "peronospora", "oidio", "mosca dell", "cimice", "brusone",
            "bollettino di difesa", "monitoraggio", "lotta obbligatoria", "trappol"]),
    ("T2", ["agrometeo", "meteo", "pioggia", "temperatur", "irrigaz", "siccita",
            "bilancio idrico", "suolo", "clima", "stazioni meteo", "nitrati"]),
    ("T1", ["coltura", "colture", "resa", "produzione", "semina", "raccolto",
            "varieta", "vendemmia", "superfici", "ettari", "fenologi"]),
    ("T4", ["autorizzazione", "revoca", "disciplinare", "normativa", "decreto",
            "regolamento", "passaporto delle piante", "registro", "deroga", "pan "]),
    ("T5", ["ricerca", "sperimentazione", "prove sperimentali", "pubblicazioni",
            "progetto", "dottorato", "convegno scientifico", "risultati"]),
    ("T6", ["docenti", "ricercator", "professor", "curriculum", "orcid",
            "dipartimento", "staff scientifico"]),
    ("T7", ["assistenza tecnica", "consulenza", "tecnici", "agronomi", "soci",
            "cooperativ", "consorzio", "organizzazione di produttori",
            "servizi alle aziende", "formazione", "corsi", "patentino"]),
    ("T8", ["agricoltor", "azienda agricola", "testimonianza", "storie",
            "canale youtube", "seguici", "instagram", "podcast", "vlog"]),
    ("T9", ["prodotti fitosanitari", "portfolio", "catalogo prodotti", "formulato",
            "sostanza attiva", "fungicida", "erbicida", "insetticida",
            "soluzioni per", "gamma"]),
    ("T10", ["prezzi", "quotazioni", "listino", "mercato", "export", "import",
             "consumi", "borsa merci", "fatturato", "domanda"]),
    ("T11", ["fiera", "convegno", "evento", "giornata tecnica", "webinar",
             "calendario", "iscrizioni", "programma"]),
    ("T12", ["psr", "pac", "politica agricola", "bando", "contributi",
             "sviluppo rurale", "assessorato", "programmazione", "sostenibilita",
             "ecoschemi", "green deal"]),
]

CULTURAS = {
    "vite": ["vite", "vigneto", "viticol", "uva", "vino", "vendemmia"],
    "olivo": ["olivo", "oliveto", "olivicol", "olive", "olio di oliva", "frantoio"],
    "cereali": ["cereal", "cerealicol", "grano", "frumento", "orzo", "spiga"],
    "frumento duro": ["grano duro", "frumento duro", "semola"],
    "mais": ["mais", "maiscol", "granella di mais"],
    "riso": ["riso", "risaia", "risicol", "risone"],
    "pomodoro": ["pomodoro", "pomodori"],
    "ortaggi": ["ortic", "orticol", "ortaggi", "insalata", "lattuga", "peperone",
                "zucchino", "melone", "carciofo", "finocchio"],
    "frutta": ["frutticol", "frutta", "fruttifer", "drupacee", "pomacee"],
    "melo": ["melo", "mele", "melicol", "ticchiolatura"],
    "pero": ["pero", "pere"],
    "agrumi": ["agrum", "arancia", "limone", "mandarino", "clementine"],
    "nocciolo": ["nocciol", "corilicol", "nocciole"],
    "patata": ["patata", "patate"],
    "barbabietola": ["barbabietol", "bietola"],
    "soia": ["soia"],
    "girasole": ["girasol"],
    "piccoli frutti": ["piccoli frutti", "mirtill", "fragol", "lampon"],
    "kiwi": ["kiwi", "actinidia"],
    "pesco": ["pesco", "pesche", "nettarine"],
    "mandorlo": ["mandorl"],
    "castagno": ["castagn"],
    "olivo da mensa": ["olive da mensa", "olive da tavola"],
    "floricoltura": ["floricol", "florovivais", "fiori"],
    "tabacco": ["tabacco"],
    "canapa": ["canapa"],
}

TIPO_PARA_PORTA = {
    "SERVIZIO_FITOSANITARIO": "BASE_OFICIAL", "AGENZIA_REGIONALE": "BASE_OFICIAL",
    "REGIONE": "BASE_OFICIAL", "ESTADO_NACIONAL": "BASE_OFICIAL",
    "CAMARA_COMERCIO": "BASE_OFICIAL",
    "UNIVERSIDADE": "CIENCIA", "CENTRO_PESQUISA": "CIENCIA",
    "SOCIEDADE_CIENTIFICA": "CIENCIA",
    "CONSORZIO_TUTELA": "ORGANIZACAO", "CONSORZIO_BONIFICA": "ORGANIZACAO",
    "COOPERATIVA_OP": "ORGANIZACAO", "ASSOCIACAO_AGRICOLA": "ORGANIZACAO",
    "ORDEM_PROFISSIONAL": "ORGANIZACAO", "EMPRESA_INSUMOS": "ORGANIZACAO",
    "FEIRA_EVENTO": "ORGANIZACAO",
    "MIDIA_TECNICA": "IMPRENSA",
}
PLATAFORMA_PARA_PORTA = {
    "INSTAGRAM": "INSTAGRAM", "YOUTUBE": "YOUTUBE", "LINKEDIN": "LINKEDIN",
    "FACEBOOK": "FACEBOOK", "TIKTOK": "OUTRO", "PODCAST": "OUTRO",
    "TELEGRAM": "OUTRO", "BLOG": "OUTRO",
}


def normalizar(url):
    u = (url or "").strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    return u.split("#")[0].rstrip("/")


def raiz_registavel(h):
    p = (h or "").split(".")
    if len(p) <= 2:
        return h or ""
    comp = {"gov.it", "edu.it", "co.uk", "org.uk", "com.br", "gov.br",
            "camcom.gov.it", "provincia.tn.it", "provincia.bz.it"}
    for n in (3, 2):
        if len(p) > n and ".".join(p[-n:]) in comp:
            return ".".join(p[-(n + 1):])
    return ".".join(p[-2:])


def host_de(url):
    n = normalizar(url)
    return n.split("/")[0].split("?")[0]


def territorios_de(med, ancoras):
    if not med:
        return []
    alvo = " ".join([med.get("TITULO", "")] + med.get("AGRI_PALAVRAS", [])
                    + med.get("INFO_PROPRIA_MARCAS", [])
                    + med.get("PRIMARIA_MARCAS", [])
                    + list(ancoras or [])).lower()
    achados = [t for t, palavras in SINAL_TERRITORIO
               if any(p in alvo for p in palavras)]
    return achados


def culturas_de(med, ancoras):
    if not med:
        return []
    alvo = " ".join([med.get("TITULO", "")] + med.get("AGRI_PALAVRAS", [])
                    + list(ancoras or [])).lower()
    return [c for c, palavras in CULTURAS.items() if any(p in alvo for p in palavras)]


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    probe = json.loads((TRABALHO / "PROBE.json").read_text(encoding="utf-8"))
    base = json.loads((TRABALHO / "KNOWN-BASELINE.json").read_text(encoding="utf-8"))
    crawl_pages = json.loads((TRABALHO / "CRAWL-PAGES.json").read_text(encoding="utf-8"))

    urls_conhecidos = set(base["urls"].keys())
    hosts_conhecidos = set(base["hosts"].keys())
    raizes_conhecidas = {raiz_registavel(h) for h in hosts_conhecidos}
    nomes_conhecidos = {n.strip().lower() for n in base["nomes"] if n}
    owners_conhecidos = {o.strip().lower() for o in base["owners"] if o}
    social_conhecido = {k: set(v) for k, v in base.get("social", {}).items()}

    linhas = []

    # ══ 1 · o que a sonda mediu ══════════════════════════════════════════
    for p in probe:
        r = p["HOST_RAIZ"]
        med = p.get("MEDIDA")
        url_disc = p.get("URL_DISCOVERED") or f"https://{r}/"
        url_fin = p.get("URL_FINAL") or p.get("URL_PROBED") or url_disc

        # ── regiao: SO do texto da pagina ──
        regs = (med or {}).get("REGIOES_NO_TEXTO") or []
        if len(regs) == 1:
            regiao, reg_ev = regs[0], "TEXTO_DA_PAGINA (uma regiao citada)"
            escopo = "REGIONAL"
        elif len(regs) >= 6:
            regiao = "ITALIA"
            reg_ev = f"TEXTO_DA_PAGINA ({len(regs)} regioes citadas — alcance nacional)"
            escopo = "NATIONAL"
        elif len(regs) >= 2:
            regiao = ";".join(regs)
            reg_ev = f"TEXTO_DA_PAGINA ({len(regs)} regioes citadas)"
            escopo = "MULTI_REGIONAL"
        else:
            regiao = "NAO SEI"
            reg_ev = ("NAO PROVADA — nenhuma palavra de regiao no texto. "
                      "O dominio NAO foi usado para deduzir a regiao.")
            escopo = "UNKNOWN"

        # ── dedupe contra o acervo ──
        # A raiz encurtada NAO basta e chegou a mentir: o heuristico corta
        # 'agricoltura.regione.emilia-romagna.it' para 'emilia-romagna.it', e
        # com isso uma fonte que o acervo JA tinha aparecia como nova. Por isso
        # a comparacao usa TRES chaves, da mais forte para a mais fraca:
        #   1 · o URL normalizado  -> a mesma pagina
        #   2 · o host COMPLETO    -> o mesmo sitio
        #   3 · a raiz             -> provavelmente o mesmo dono
        nd = normalizar(url_disc)
        nf = normalizar(url_fin)
        hosts_desta = set(p.get("HOSTS") or [])
        hosts_desta.add(host_de(url_disc))
        hosts_desta.add(host_de(url_fin))
        hosts_desta.discard("")
        url_igual = nd in urls_conhecidos or nf in urls_conhecidos
        host_igual = bool(hosts_desta & hosts_conhecidos)
        raiz_igual = r in raizes_conhecidas

        if url_igual:
            novo = "KNOWN_SOURCE"
        elif host_igual:
            novo = "SAME_OWNER_DIFFERENT_SOURCE"
        elif raiz_igual:
            novo = "SAME_OWNER_DIFFERENT_SOURCE"
        else:
            novo = "NEW_SOURCE"
        # quando a raiz junta donos diferentes (camcom.it, provincia.*.it,
        # regione.*.it), a linha leva aviso: a raiz nao prova dono.
        raiz_ambigua = (len(hosts_desta) > 1 and
                        len({h.split(".")[0] for h in hosts_desta}) > 1)

        terrs = territorios_de(med, p.get("ANCORAS"))
        crops = culturas_de(med, p.get("ANCORAS"))
        tipos = (med or {}).get("TIPO_DONO") or []
        titulo = (med or {}).get("TITULO") or ""

        # ── o que ela pode dizer ao SINTONIA, em palavras de gente ──
        pedacos = []
        if "T3" in terrs:
            pedacos.append("avisa praga e doenca")
        if "T2" in terrs:
            pedacos.append("mede tempo, agua ou solo")
        if "T1" in terrs:
            pedacos.append("diz o que se planta e quanto sai")
        if "T4" in terrs:
            pedacos.append("diz o que esta autorizado")
        if "T5" in terrs or "T6" in terrs:
            pedacos.append("publica ensaio e pesquisa")
        if "T7" in terrs:
            pedacos.append("esta ao lado de quem aplica")
        if "T8" in terrs:
            pedacos.append("mostra a voz do produtor")
        if "T9" in terrs:
            pedacos.append("mostra o que o concorrente comunica")
        if "T10" in terrs:
            pedacos.append("acompanha preco e mercado")
        if "T11" in terrs:
            pedacos.append("anuncia evento tecnico")
        if "T12" in terrs:
            pedacos.append("mostra a politica agricola")
        o_que_diz = " · ".join(pedacos) if pedacos else "NAO SEI — a pagina nao mostrou"
        if crops:
            o_que_diz += f" — em {', '.join(crops[:4])}"
        if regiao not in ("NAO SEI", "ITALIA"):
            o_que_diz += f" (territorio citado: {regiao})"

        ev = []
        if p.get("HTTP_STATUS"):
            ev.append(f"HTTP {p['HTTP_STATUS']}")
        if titulo:
            ev.append(f"titulo: {titulo[:90]}")
        if med:
            if med.get("ULTIMA_DATA_VISTA"):
                ev.append(f"data mais recente vista: {med['ULTIMA_DATA_VISTA']} "
                          f"({med['ULTIMA_DATA_FONTE']})")
            if med.get("INFO_PROPRIA_MARCAS"):
                ev.append("marcas de informacao propria: "
                          + ", ".join(med["INFO_PROPRIA_MARCAS"][:6]))
            if med.get("TEM_RSS"):
                ev.append("tem feed RSS/Atom")
        if p.get("DISCOVERED_FROM"):
            ev.append("descoberta a partir de: " + p["DISCOVERED_FROM"][0][:90])

        limit = []
        if not p.get("SONDADO"):
            limit.append("nao foi sondada (rejeitada como infraestrutura)")
        if (med or {}).get("ULTIMA_DATA_FONTE") == "SO_O_ANO":
            limit.append("frescura NAO PROVADA: a idade vem de um ano solto")
        if regiao == "NAO SEI":
            limit.append("regiao NAO PROVADA")
        if not terrs:
            limit.append("territorio T1-T12 nao identificavel pela homepage")
        if raiz_ambigua:
            limit.append(f"a raiz '{r}' junta mais de um subdominio "
                         f"({', '.join(sorted(hosts_desta)[:3])}) — a raiz NAO "
                         f"prova dono unico")

        # o host completo e mais honesto que a raiz encurtada
        host_cheio = host_de(url_fin) or host_de(url_disc) or r

        linhas.append({
            "RECORD_KIND": "SOURCE",
            "NAME": titulo[:120] or host_cheio,
            "OWNER": (titulo.split("|")[-1].strip()[:90] if "|" in titulo
                      else (titulo[:90] or host_cheio)),
            "PERSON": "",
            "ORGANIZATION": titulo[:90] or host_cheio,
            "COUNTRY": "IT" if r.endswith(".it") else ("EU" if r.endswith(".eu") else "NAO SEI"),
            "REGION": regiao,
            "REGION_EVIDENCE": reg_ev,
            "SCOPE": escopo,
            # Guardo TODOS os tipos detetados, nao so o primeiro: a pagina do
            # MASAF cita universidades, e com 'o primeiro que bater' o
            # ministerio da agricultura ia para a gaveta CIENCIA.
            "SOURCE_TYPE": (tipos[0] if tipos else "NAO SEI"),
            "SOURCE_TYPE_ALL": ";".join(tipos),
            "PLATFORM": "WEB",
            "URL_DISCOVERED": url_disc,
            "URL_FINAL": url_fin,
            "URL_CANONICAL": url_fin if p.get("URL_STATUS") == "CANONICAL" else "",
            "URL_STATUS": p.get("URL_STATUS") or "UNKNOWN",
            "HTTP_STATUS": p.get("HTTP_STATUS") or "",
            "TERRITORIES": ";".join(terrs),
            "CROPS": ";".join(crops),
            "TOPICS": ";".join(((med or {}).get("AGRI_PALAVRAS") or [])[:12]),
            "INFORMATION_PROXIMITY": p.get("INFORMATION_PROXIMITY") or "UNKNOWN",
            "RECURRING_INFORMATION_POTENTIAL": p.get("RECURRING_INFORMATION_POTENTIAL") or "UNKNOWN",
            "WHY_USEFUL": "; ".join(p.get("PRE_CLASSE_RAZAO") or []),
            "WHAT_CAN_THIS_SOURCE_TELL_SINTONIA": o_que_diz,
            "EXAMPLE_REAL": url_fin,
            "EVIDENCE": " · ".join(ev),
            "LAST_ACTIVITY_OBSERVED": (med or {}).get("ULTIMA_DATA_VISTA") or "NAO SEI",
            "OFFICIALITY": ("OFICIAL" if any(t in tipos for t in (
                "SERVIZIO_FITOSANITARIO", "AGENZIA_REGIONALE", "REGIONE",
                "ESTADO_NACIONAL", "CAMARA_COMERCIO")) else "NAO SEI"),
            "OWNER_MATCH": "PROVED_BY_PAGE_TITLE" if titulo else "NOT_PROVED",
            "NEW_VS_EXISTING": novo,
            "RELATED_OWNER": host_cheio,
            "QUALITY_CLASS": p.get("PRE_CLASSE") or "UNKNOWN",
            "QUALITY_REASON": "; ".join(p.get("PRE_CLASSE_RAZAO") or []),
            "LIMITATION": "; ".join(limit) or "—",
            "VALIDATED_AT": HOJE,
            "DISCOVERED_FROM": " | ".join(p.get("DISCOVERED_FROM") or []),
            "N_DESCOBRIDORES": p.get("N_DESCOBRIDORES") or 0,
            "AGRI_N": (med or {}).get("AGRI_N") or 0,
            "INFO_PROPRIA_N": (med or {}).get("INFO_PROPRIA_N") or 0,
            "_raiz": r,
            "_fonte_do_registo": "SONDA_HTTP",
        })

    # ══ 2 · o que a busca por palavra trouxe: pessoas e canais ══════════
    pessoas_desta_rodada = set()
    canais_desta_rodada = set()
    for fich in sorted((TRABALHO / "search").glob("*.jsonl")):
        for ln in fich.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if not ln:
                continue
            d = json.loads(ln)
            kind = d.get("kind", "PERSON")
            url = d.get("url", "")
            r = raiz_registavel(host_de(url))
            plataforma = d.get("platform", "WEB")

            if kind == "CHANNEL":
                handle = "/".join(normalizar(url).split("/")[1:3]).lower()
                conhecidas = social_conhecido.get(plataforma, set())
                chave_canal = f"{plataforma}::{normalizar(url)}"
                if any(handle and handle in c or (c and c in handle) for c in conhecidas):
                    novo = "KNOWN_SOURCE"
                elif chave_canal in canais_desta_rodada:
                    novo = "TRUE_DUPLICATE"
                elif r in raizes_conhecidas and plataforma == "WEB":
                    novo = "SAME_OWNER_DIFFERENT_SOURCE"
                else:
                    novo = "NEW_CHANNEL"
                canais_desta_rodada.add(chave_canal)
            else:
                # Dedupe de pessoa em DOIS sentidos, e o segundo faltava:
                # contra o acervo (ja conhecida) e contra ESTA MESMA rodada.
                # Sem o segundo, a mesma pessoa citada por duas buscas conta
                # duas vezes — e o numero final de 'novos pesquisadores' mente.
                nome = (d.get("name") or "").strip().lower()
                if nome in nomes_conhecidos:
                    novo = "KNOWN_SOURCE"
                elif nome in pessoas_desta_rodada:
                    novo = "TRUE_DUPLICATE"
                else:
                    novo = "NEW_PERSON"
                pessoas_desta_rodada.add(nome)

            terrs = d.get("terr") or []
            crops = d.get("crops") or []
            probs = d.get("problems") or []

            if kind == "PERSON":
                classe = "PEOPLE"
                prox = "PRIMARY" if any(t in terrs for t in ("T3", "T7")) else "NEAR_PRIMARY"
                rec = "MEDIUM"
                nome_lin = d.get("name", "")
                dono = d.get("inst", "")
            else:
                # canal social: a classe depende de autoridade, NAO de alcance
                ta = (d.get("technical_authority") or "").upper()
                fa = (d.get("field_authority") or "").upper()
                if ta.startswith(("ALTA", "MUITO ALTA")) and fa.startswith(("ALTA", "MUITO ALTA")):
                    classe = "A"
                elif ta.startswith(("ALTA", "MEDIA-ALTA", "MUITO ALTA")) or fa.startswith(("ALTA", "MUITO ALTA")):
                    classe = "B"
                elif "NULA" in ta or "BAIXA" in ta and "BAIXA" in fa:
                    classe = "REJECT"
                else:
                    classe = "C"
                if (d.get("region") or "") == "FORA_DE_ITALIA":
                    classe = "REJECT"
                if (d.get("owner") or "NAO IDENTIFICADO") == "NAO IDENTIFICADO":
                    classe = "HOLD"
                prox = "NEAR_PRIMARY" if fa.startswith(("ALTA", "MUITO ALTA")) else "SECONDARY"
                rec = "HIGH" if "ALTA" in (d.get("commercial_influence") or "") or \
                    "video" in (d.get("what") or "") else "MEDIUM"
                nome_lin = d.get("name", "")
                dono = d.get("owner", "")

            linhas.append({
                "RECORD_KIND": kind,
                "NAME": nome_lin,
                "OWNER": dono,
                "PERSON": d.get("name", "") if kind == "PERSON" else "",
                "ORGANIZATION": d.get("inst", "") if kind == "PERSON" else dono,
                "COUNTRY": "IT",
                "REGION": d.get("region") or "NAO SEI",
                "REGION_EVIDENCE": "DECLARADA NA FONTE QUE A CITOU (ver EVIDENCE)",
                "SCOPE": "REGIONAL" if (d.get("region") or "") in REGIOES_20 else
                         ("NATIONAL" if (d.get("region") or "") == "ITALIA" else "UNKNOWN"),
                "SOURCE_TYPE": "PESSOA" if kind == "PERSON" else f"CANAL_{plataforma}",
                "PLATFORM": plataforma,
                "URL_DISCOVERED": url,
                "URL_FINAL": url,
                "URL_CANONICAL": "",
                "URL_STATUS": "NAO_TESTADO_NESTA_LINHA",
                "HTTP_STATUS": "",
                "TERRITORIES": ";".join(terrs),
                "CROPS": ";".join(crops),
                "TOPICS": ";".join(probs) or d.get("spec", ""),
                "INFORMATION_PROXIMITY": prox,
                "RECURRING_INFORMATION_POTENTIAL": rec,
                "WHY_USEFUL": d.get("spec", "") or d.get("field_authority", ""),
                "WHAT_CAN_THIS_SOURCE_TELL_SINTONIA": d.get("what", ""),
                "EXAMPLE_REAL": url,
                "EVIDENCE": d.get("ev", ""),
                "LAST_ACTIVITY_OBSERVED": "NAO SEI",
                "OFFICIALITY": "NAO SEI",
                "OWNER_MATCH": "NOT_PROVED" if kind == "CHANNEL" and not dono else "DECLARED",
                "NEW_VS_EXISTING": novo,
                # Para um CANAL, a raiz do dominio e 'youtube.com' — o que nao
                # identifica dono nenhum e faz a OWNER_MAP dizer que um dono
                # chamado YouTube tem 9 fontes. O dono de um canal e quem o
                # opera; a plataforma e so o lugar.
                "RELATED_OWNER": (d.get("owner") or d.get("inst") or r or "")[:70]
                                 if kind == "CHANNEL" else (r or d.get("inst", "")),
                "QUALITY_CLASS": classe,
                "QUALITY_REASON": ("pessoa: relevancia declarada por cultura/problema, "
                                   "sem ranking universal"
                                   if kind == "PERSON" else
                                   f"autoridade tecnica={d.get('technical_authority','?')} · "
                                   f"autoridade de campo={d.get('field_authority','?')} · "
                                   f"alcance={d.get('reach','?')} — medidos em separado, "
                                   f"nunca somados"),
                "LIMITATION": ("afiliacao atual por confirmar; a fonte que a citou pode "
                               "estar desatualizada" if kind == "PERSON" else
                               "atividade recente do canal NAO medida nesta missao"),
                "VALIDATED_AT": HOJE,
                "DISCOVERED_FROM": d.get("from", ""),
                "N_DESCOBRIDORES": 1,
                "AGRI_N": "",
                "INFO_PROPRIA_N": "",
                "_raiz": r,
                "_fonte_do_registo": "WEBSEARCH",
                "_reach": d.get("reach", ""),
                "_field": d.get("field_authority", ""),
                "_tech": d.get("technical_authority", ""),
                "_comm": d.get("commercial_influence", ""),
                "_orcid": d.get("orcid", ""),
            })

    print(f"LINHAS TOTAIS = {len(linhas)}")
    cc = Counter(l["QUALITY_CLASS"] for l in linhas)
    print("por classe:", dict(cc))
    ck = Counter(l["RECORD_KIND"] for l in linhas)
    print("por tipo de registo:", dict(ck))
    cn = Counter(l["NEW_VS_EXISTING"] for l in linhas)
    print("novo vs existente:", dict(cn))

    (TRABALHO / "LINHAS.json").write_text(
        json.dumps(linhas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"gravado: {TRABALHO / 'LINHAS.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
