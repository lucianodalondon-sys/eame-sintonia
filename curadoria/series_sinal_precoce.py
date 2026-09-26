#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SERIES DO SINAL PRECOCE — tira dos boletins fitossanitarios JA guardados no acervo as series tal como vieram
(data, local/estacao, armadilha, organismo, cultura, valor, limiar, fase), SEM RESUMIR, e marca a natureza de cada
frase (OBSERVACAO / PREVISAO / RECOMENDACAO) so quando o texto o diz. Sem rede; so leitura. (SINAL-PRECOCE-LEITURA 26/09.)

    py curadoria/series_sinal_precoce.py --raiz=<pasta> [--raiz=...] --saida=<JSON>

Um extractor por forma de boletim (medida nos bytes do acervo, nao adivinhada):
  SALERNO (IT-T3-002, Campania): tabela por COLTURA; na coluna «Stato fitosanitario» «n. N catture di <Organismo>» e
    «Media catture N Infestazioni N»;
  APOL (IT-T3-010, Puglia): uma linha por COMPRENSORIO «<FASE>  N  N  N%  <TENDENCIA>  <RISCO>» — o cabecalho e imagem:
    as colunas ficam COLUNA_1..3 (o que medem = NAO SEI);
  TERRE DELL'ETRURIA (IT-T3-005, Toscana, HTML): por ponto «<Local> Torna alla mappa Latitudine … Data di campionamento:
    D Infestazione attiva: V%, <estado> Catture adulti: <…>»;
  ARIF (IT-T3-008, Puglia) e ARPAV (IT-T2-002, Veneto — seccao «Dai Servizi Fitosanitari»): frases com organismo;
    sem numeros de captura — ficam como FRASE com a natureza.
Cada linha leva TRECHO (o texto de onde saiu) e o sha256 do documento.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import colher_prova_territorio as CPT   # noqa: E402  (datas, texto visivel)
import ler_pdf_monitorizacao as L        # noqa: E402  (pdftotext -layout)
import medir_contagens as MC            # noqa: E402  (pragas)

RE_SID = re.compile(r"(IT-T\d+-\d{3})")

# A natureza so quando o texto a diz (verbo/expressao), nunca por adivinha. Uma frase pode ter mais de uma.
OBS = re.compile(r"\b(si riscontran\w*|si osserv\w*|si registr\w*|rilevat\w*|evidenzi\w*|presenza di|presente in|"
                 r"catture\b|campionament\w*|monitoraggi\w* (della settimana|territoriali)|"
                 r"non (si )?sono state rilevate|aumento del numero|cascola|si segnala|osservat\w*)", re.I)
PREV = re.compile(r"\b(si prevede|previst\w*|previsione|nei prossimi giorni|da met[aà] della prossima settimana|"
                  r"favorir\w*|possono favorire|rischio|si verificher\w*|porter\w*)", re.I)
RECO = re.compile(r"\b(si consiglia|si raccomanda|consigliabil\w*|intervenire|occorre|programmare|effettuare un|"
                  r"applicare|utilizzare|trattament\w* (preventiv\w*|insetticid\w*)|non si ritiene giustificat\w*)", re.I)


FORTE_OBS = re.compile(r"\b(si riscontran\w*|riscontrat\w*|si osserv\w*|si registr\w*|rilevat\w*|evidenzi\w*|"
                       r"non si segnalano|aumento del numero|catture di\b)", re.I)
RECO2 = re.compile(r"\b(prestare attenzione|monitorare|proseguire|eseguire|collocare|attuare)\b", re.I)
PREV2 = re.compile(r"\b(potrebbe|possono)\b", re.I)


def natureza(frase: str) -> list[str]:
    """So o que o texto diz. Uma frase de LIMIAR («al superamento della soglia…») nao e observacao, a nao ser que
    tambem diga que viu («si riscontrano», «rilevate»…)."""
    n = []
    obs = OBS.search(frase) and (FORTE_OBS.search(frase) or not re.search(r"soglia", frase, re.I))
    if obs and not (RECO2.search(frase) and not FORTE_OBS.search(frase)):
        n.append("OBSERVACAO")
    if PREV.search(frase) or PREV2.search(frase):
        n.append("PREVISAO")
    if RECO.search(frase) or RECO2.search(frase):
        n.append("RECOMENDACAO")
    return n


def _uma(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip()


# ── SALERNO: transcricao a mao, CONFERIDA pela maquina ───────────────────────
# O -layout destes 2 PDFs mistura as colunas «Azienda/Varieta/Stadio/Stato» (medido: um extractor generico leu
# «Gaetano riccio» — pedaco de um nome de azienda — como organismo). Para 2 documentos, a transcricao a mao e mais
# honesta; a maquina confere que CADA trecho citado existe no texto do PDF (espacos normalizados). Trecho que nao
# bate -> a linha sai com CONFERE=False. Chave = sha256 do PDF.
_S1 = "0c2723e66201"   # N° 25 del 02/09/2026
_S2 = "c5ae3bfe76d9"   # N° 27 del 16/09/2026
_ANGRI = ("AGRUMI", "Angri", "Monte Longobardi", "Taccaro Gennaro", "varie", "Accrescimento frutticini")
_TRAM_V = ("VITE", "Tramonti", "Capitignano", "Apicella P.", "Piedirosso", "Maturazione")
_TRAM_C = ("CASTAGNO", "Tramonti", "Frescale", "Apicella Gaetano", "diverse", "Accrescimento riccio")
_SARNO_N = ("NOCE", "Sarno", "Quattrofuni", "Fasolino", "Sorrento", "Maturazione frutti")
_SARNO_P = ("POMODORO", "Sarno", "San Vito", "Raimo Aniello", "San Marzano", "Prosegue la raccolta")
_CAPACCIO = ("MELANZANA", "Capaccio", "Paestum Scalo", "Mucciolo L.", "Diverse", "Fase di maturazione commerciale")
_OLIVO = ("OLIVO", "Campagna / Agropoli (a linha nao se atribui: colunas misturadas no PDF)", "—", "Reppuccia G. / Cardone F.",
          "Rotondella / Salella-Frantoio-Leccino", "Accrescimento del frutto")
SALERNO_MAO = {
 _S1: [(_ANGRI, "Prays citri", 0, "n. 0 catture di Prays"),
       (_ANGRI, "Ceratitis capitata", 4, "n. 4 catture di Ceratitis Capitata"),
       (_TRAM_V, "Lobesia botrana", 3, "n.3 catture di Lobesia"),
       (_TRAM_V, "Cryptoblabes gnidiella", 0, "n.0 catture di Cryptoblabes Gnidiella"),
       (_TRAM_V, "Scaphoideus (Scafoide)", 3, "n. 3 catture di Scafoide"),
       (_TRAM_C, "Cydia fagiglandana (Cidia)", 2, ". 2 catture di Cidia fagiglandana"),
       (_TRAM_C, "Pammene fasciana (Pamena)", 5, "n. 5 catture di Pamena Fasciana"),
       (_TRAM_C, "Cinipide", "Presenza", "Presenza di Cinipide"),
       (_SARNO_N, "Cydia pomonella", 3, "n. 3 catture di Cydia Pomonella"),
       (_OLIVO, "mosca (linha 1)", "Minime cattura di mosca", "Minime cattura di mosca"),
       (_OLIVO, "mosca (linha 2)", "Nulla", "Nulla"),
       (_SARNO_P, "Tuta absoluta", 5, "Tuta Absoluta: n. 5 catture"),
       (_SARNO_P, "Helicoverpa armigera", 0, "Helicoverpa A. n. 0 catture"),
       (_CAPACCIO, "Tuta absoluta", 6, "-n. 6 catture di Tuta absoluta"),
       (_CAPACCIO, "cicaline", "Presenza", "-Presenza di cicaline")],
 _S2: [(_ANGRI, "Prays citri", 0, "n. 0 catture di Prays Citri"),
       (_ANGRI, "Ceratitis capitata", 40, "40 catture di Ceratitis Capitata"),
       (_TRAM_V, "Lobesia botrana", 5, "n.5 catture di Lobesia Botrana"),
       (_TRAM_V, "Cryptoblabes gnidiella", 0, "catture di Cryptoblabes Gnidiella"),
       (_TRAM_V, "Scaphoideus (Scafoide)", 4, "n. 4 catture di Scafoide"),
       (_TRAM_C, "Cydia fagiglandana (Cidia)", 0, "n. 0 catture di Cidia fagiglandana"),
       (_TRAM_C, "Pammene fasciana (Pamena)", 0, "n. 0 catture di Pamena Fasciana"),
       (_TRAM_C, "Cinipide", "Presenza", "Presenza di Cinipide"),
       (_SARNO_N, "Cydia pomonella", 3, "n. 3 catture di Cydia Pomonella"),
       (_OLIVO, "mosca (linha 1)", "Media catture 3 / Infestazioni 0", "Media catture 3"),
       (_OLIVO, "mosca (linha 2)", "Media catture 7 / Infestazioni 0", "Media catture 7"),
       (_SARNO_P, "Tuta absoluta", 5, "n. 5 catture."),
       (_SARNO_P, "Helicoverpa armigera", 0, "Helicoverpa A. n. 0 catture"),
       (_CAPACCIO, "Tuta absoluta", 9, "-n. 9 catture di Tuta absoluta")],
}


def confere(trecho: str, corrido: str, janela: int = 120) -> str | None:
    """EXATO se o trecho esta no texto; EM_ORDEM se as palavras aparecem por esta ordem em <= `janela` letras (o
    -layout intercala palavras de outras colunas dentro de uma celula); None se nao."""
    t = _uma(trecho)
    if t in corrido:
        return "EXATO"
    ps = t.split()
    for m in re.finditer(re.escape(ps[0]), corrido):
        pos, ok = m.end(), True
        for w in ps[1:]:
            k = corrido.find(w, pos, m.start() + janela)
            if k < 0:
                ok = False
                break
            pos = k + len(w)
        if ok:
            return "EM_ORDEM"
    return None


def salerno(texto: str, sha: str = "") -> list[dict]:
    data = re.search(r"N°\s*(\d+)\s+del\s+(\d\d)/(\d\d)/(\d{4})", texto)
    iso = "%s-%s-%s" % (data.group(4), data.group(3), data.group(2)) if data else None
    corrido = _uma(texto)
    linhas = SALERNO_MAO.get(sha[:12])
    if linhas is None:
        return [{"DATA": iso, "ORGANISMO": None, "METRICA": "NAO LIDO",
                 "NOTA": "PDF de Salerno sem transcricao conferida (novo): ler a mao antes de usar", "NATUREZA": []}]
    out = []
    for (cult, comune, loc, az, var, fase), org, valor, trecho in linhas:
        out.append({"CULTURA": cult, "COMUNE": comune, "LOCALITA": loc, "AZIENDA": az, "VARIETA": var, "FASE": fase,
                    "LOCAL": "%s · %s · %s" % (comune, loc, az), "ORGANISMO": org,
                    "METRICA": "catture" if isinstance(valor, int) else "estado (texto)",
                    "VALOR": valor, "TRECHO": trecho, "CONFERE": confere(trecho, corrido),
                    "DATA": iso, "BOLETIM_N": data.group(1) if data else None,
                    "NATUREZA": ["OBSERVACAO"],            # coluna «Stato fitosanitario» da rete di monitoraggio
                    "ORIGEM": "transcricao a mao conferida pela maquina"})
    return out


# ── APOL ────────────────────────────────────────────────────────────────────
RE_APOL_LINHA = re.compile(r"^\s*([A-Z][A-Z ]+?)\s+(\d+)\s+(\d+)\s+(\d+%)\s+([A-Z]+)\s+([A-Z]+)\s*$", re.M)


def apol(texto: str) -> list[dict]:
    out, comp = [], None
    periodo = None
    linhas = texto.splitlines()
    for i, l in enumerate(linhas):
        m = re.search(r"COMPRENSORIO\s*-\s*(.+)", l)
        if m:
            comp = m.group(1).strip()
            for k in (1, 2, 3):
                nx = linhas[i + k].strip() if i + k < len(linhas) else ""
                if nx and nx.isupper() and not re.search(r"\d", nx) and "  " not in nx:
                    comp += " " + nx
                    break
        p = re.search(r"(\d\d/\d\d/\d{4})\s*-\s*(\d\d/\d\d/\d{4})", l)
        if p:
            periodo = (p.group(1), p.group(2))
        r = RE_APOL_LINHA.match(l)
        if r and comp:
            out.append({"LOCAL": "COMPRENSORIO %s" % comp, "ORGANISMO": "mosca delle olive (Bactrocera oleae)",
                        "CULTURA": "olivo", "FASE": r.group(1).strip(),
                        "COLUNA_1": int(r.group(2)), "COLUNA_2": int(r.group(3)), "COLUNA_3": r.group(4),
                        "TENDENCIA": r.group(5), "RISCO": r.group(6),
                        "METRICA": "NAO SEI (o cabecalho da tabela e imagem)",
                        "PERIODO": periodo, "DATA": "%s-%s-%s" % tuple(reversed(periodo[0].split("/"))) if periodo else None,
                        "NATUREZA": ["OBSERVACAO"], "TRECHO": l.strip()})
    return out


# ── TERRE DELL'ETRURIA (HTML) ──────────────────────────────────────────────
RE_PONTO = re.compile(r"(?:registrati|mappa|dedicato)\s+([^:]{3,80}?)\s+Torna alla mappa\s+Latitudine:\s*([\d.]+),\s*"
                      r"Longitudine:\s*([\d.]+)\s+Data di campionamento:\s*([\d-]+|-)\s+Infestazione attiva:\s*"
                      r"([\d.,]+\s*%|-)(?:,\s*([^C]+?))?\s+Catture adulti:\s*([^A-Z]*?Dato per utenti registrati|[\d.,]+|-)")


def terretruria(texto: str) -> list[dict]:
    out = []
    for m in RE_PONTO.finditer(texto):
        d = m.group(4)
        out.append({"LOCAL": m.group(1).strip(), "LAT": m.group(2), "LON": m.group(3),
                    "DATA": ("%s-%s-%s" % tuple(reversed(d.split("-")))) if d != "-" else None,
                    "ORGANISMO": "mosca delle olive", "CULTURA": "olivo",
                    "METRICA": "Infestazione attiva", "VALOR": m.group(5).replace(" ", ""),
                    "ESTADO": (m.group(6) or "").strip() or None,
                    "CATTURE_ADULTI": m.group(7).strip(), "NATUREZA": ["OBSERVACAO"], "TRECHO": _uma(m.group(0))[:400]})
    return out


# ── ARIF (IT-T3-008): blocos «Situazione Fenologica / Situazione Fitosanitaria / Programma di Difesa» ────────
# Os rotulos sao do proprio boletim: FITOSANITARIA = OBSERVACAO, PROGRAMMA = RECOMENDACAO (+ os LIMIARES escritos).
# Os titulos de cultura/area sao imagem (no texto so sai «TERRITORIO ESCLUSO GARGANO»): CULTURA/AREA = NAO SEI, e o
# par entre numeros faz-se pela POSICAO do bloco (N36 e N38: 31 blocos na mesma ordem) — declarado em cada linha.
RE_ARIF = re.compile(r"Situazione Fenologica:\s*(.*?)\s*Situazione Fitosanitaria:\s*(.*?)\s*Programma di Difesa:\s*(.*?)"
                     r"(?=Situazione Fenologica:|Notiziario Agrometeorologico|\Z)", re.S)


def arif(texto_raw: str) -> list[dict]:
    num = re.search(r"n\.\s*(\d+)\s+del\s+(\d{1,2})\s+(\w+)\s+(\d{4})", texto_raw)
    iso = None
    if num:
        d = CPT._datas("%s %s %s" % (num.group(2), num.group(3), num.group(4)))
        iso = "%04d-%02d-%02d" % d[0] if d else None
    out = []
    for i, (fe, fi, pr) in enumerate(RE_ARIF.findall(texto_raw)):
        fe, fi, pr = _uma(fe), _uma(fi), _uma(pr)
        limiares = [s for s in re.split(r"(?<=[.;])\s+", pr) if re.search(r"soglia|catture per trappola|\d+\s*%", s, re.I)]
        out.append({"BLOCO": i, "DATA": iso, "BOLETIM_N": num.group(1) if num else None,
                    "CULTURA": "NAO SEI (titulo em imagem)", "AREA": "NAO SEI (titulo em imagem)",
                    "FASE": fe, "OBSERVACAO": fi, "RECOMENDACAO": pr, "LIMIARES": limiares,
                    "ORGANISMOS": sorted({m.group(1) for m in re.finditer(r"\(([A-Z][a-z]+ [a-z]+)", fi + " " + pr)}),
                    "NATUREZA": ["OBSERVACAO"] + (["RECOMENDACAO"] if pr and not re.match(r"Nessun consiglio", pr) else []),
                    "ORIGEM": "rotulos do boletim (Situazione Fitosanitaria = observacao; Programma di Difesa = recomendacao)"})
    return out


# ── FRASES (ARIF, ARPAV) ────────────────────────────────────────────────────
def frases_com_organismo(texto: str) -> list[dict]:
    """Frases (do texto corrido) que citam organismo/cultura e dizem observacao/previsao/recomendacao. Tal como estao."""
    corrido = _uma(texto)
    out = []
    for f in re.split(r"(?<=[.;])\s+(?=[A-Z])", corrido):
        org = MC.PRAGAS.search(f) or re.search(r"\(([A-Z][a-z]+ [a-z]+)\)", f)
        if not org:
            continue
        nat = natureza(f)
        if not nat:
            continue
        lim = bool(re.search(r"soglia", f, re.I))
        out.append({"ORGANISMO": org.group(0) if not org.lastindex else org.group(1), "NATUREZA": nat,
                    "LIMIAR": lim, "FRASE": f[:700]})
    return out


def arpav_secao(texto_raw: str) -> str:
    m = re.search(r"Dai Servizi Fitosanitari(.*?)(?:\n(?:Meteo Veneto|RIEPILOGO|C o ne)|\Z)", texto_raw, re.S)
    return m.group(1) if m else ""


def _raw(pdf: Path) -> str:
    r = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"], capture_output=True, timeout=120)
    return r.stdout.decode("utf-8", "replace")


# ── O PASSEIO PELO ACERVO ──────────────────────────────────────────────────
FORMA = {"IT-T3-002": "SALERNO", "IT-T3-010": "APOL", "IT-T3-005": "TERRETRURIA", "IT-T3-008": "ARIF", "IT-T2-002": "ARPAV"}


def documentos(raizes: list[Path]) -> list[dict]:
    por_sha = {}
    for r in raizes:
        for dp, _dn, fns in os.walk(r):
            for fn in fns:
                f = Path(dp) / fn
                m = RE_SID.search(str(f).replace("\\", "/"))
                if not m or m.group(1) not in FORMA:
                    continue
                forma = FORMA[m.group(1)]
                if (forma == "TERRETRURIA") != fn.lower().endswith(".html") or not fn.lower().endswith((".pdf", ".html")):
                    continue
                if forma == "TERRETRURIA" and fn.lower() != "monitoraggio.html":
                    continue
                b = f.read_bytes()
                h = hashlib.sha256(b).hexdigest()
                e = por_sha.setdefault(h, {"SHA256": h, "SOURCE_ID": m.group(1), "FORMA": forma, "CAMINHOS": []})
                e["CAMINHOS"].append(str(f).replace("\\", "/"))
    return sorted(por_sha.values(), key=lambda e: (e["SOURCE_ID"], e["CAMINHOS"][0]))


def ler(doc: dict) -> dict:
    p = Path(doc["CAMINHOS"][0])
    f = doc["FORMA"]
    base = {**{k: doc[k] for k in ("SOURCE_ID", "FORMA", "SHA256")}, "FICHEIRO": p.name, "CAMINHO": doc["CAMINHOS"][0],
            "COPIAS": len(doc["CAMINHOS"])}
    if f == "TERRETRURIA":
        return {**base, "LINHAS": terretruria(CPT._texto_visivel(p.read_bytes().decode("utf-8", "replace")))}
    if f == "ARPAV":
        raw = _raw(p)
        cab = re.search(r"Zona\s+\d+\s+[^\n]*?N°\s*\d+\s+\d\d/\d\d/\d\d", raw)
        return {**base, "CABECALHO": cab.group(0) if cab else None,
                "LINHAS": frases_com_organismo(arpav_secao(raw)), "SECAO_INTEGRAL": _uma(arpav_secao(raw))}
    if f == "ARIF":
        return {**base, "LINHAS": arif(_raw(p))}
    t = L.texto_do_pdf(p)
    if f == "SALERNO":
        return {**base, "LINHAS": salerno(t, doc["SHA256"])}
    if f == "APOL":
        return {**base, "LINHAS": apol(t)}
    return {**base, "LINHAS": frases_com_organismo(t)}


def series(docs: list[dict]) -> list[dict]:
    """Serie = o mesmo (fonte, local, organismo, metrica) em >= 2 datas distintas com valor. Os valores tal como vieram."""
    g: dict = {}
    for d in docs:
        for l in d["LINHAS"]:
            v = l.get("VALOR", "%s | %s | %s" % (l.get("COLUNA_1"), l.get("COLUNA_2"), l.get("COLUNA_3"))
                       if "COLUNA_1" in l else None)
            if v is None or not l.get("DATA"):
                continue
            k = (d["SOURCE_ID"], l.get("LOCAL") or l.get("CULTURA"), l.get("ORGANISMO"), l.get("METRICA"),
                 l.get("LINHA_DA_TABELA"))
            g.setdefault(k, {}).setdefault(l["DATA"], v)
    out = []
    for (sid, loc, org, met, lin), pontos in sorted(g.items(), key=lambda x: [str(y) for y in x[0]]):
        out.append({"SOURCE_ID": sid, "LOCAL_OU_CULTURA": loc, "ORGANISMO": org, "METRICA": met,
                    "LINHA_DA_TABELA": lin, "PONTOS": dict(sorted(pontos.items())), "REAL": len(pontos) >= 2})
    return out


def series_qualitativas(docs: list[dict]) -> list[dict]:
    """Texto de observacao ao longo das datas (sem numero): ARIF por BLOCO (posicao no boletim), ARPAV por organismo.
    Nao conta como serie real — e o que o boletim diz, lado a lado."""
    g: dict = {}
    # ARIF: so se pareia por posicao se TODOS os numeros tem o MESMO numero de blocos (medido: N36 = 32, N38 = 31 —
    # um bloco a mais desloca tudo a partir do 21; parear assim poria culturas diferentes lado a lado)
    n_blocos = {len(d["LINHAS"]) for d in docs if d["FORMA"] == "ARIF"}
    parear = len(n_blocos) == 1
    for d in docs:
        for l in d["LINHAS"]:
            if d["FORMA"] == "ARIF":
                k = (d["SOURCE_ID"], ("BLOCO %02d (cultura/area: titulo em imagem)" % l["BLOCO"]) if parear else
                     ("N.%s BLOCO %02d (SEM PAR: os numeros tem %s blocos)" % (l["BOLETIM_N"], l["BLOCO"],
                                                                              "/".join(map(str, sorted(n_blocos))))))
                g.setdefault(k, {})[l["DATA"]] = {"FASE": l["FASE"], "OBSERVACAO": l["OBSERVACAO"], "LIMIARES": l["LIMIARES"]}
            elif d["FORMA"] == "ARPAV" and "OBSERVACAO" in l["NATUREZA"]:
                # as 4 zonas saem em dias seguidos com o MESMO texto: a unidade e o numero do boletim, nao a data
                num = re.search(r"N°\s*(\d+)", d.get("CABECALHO") or "")
                k = (d["SOURCE_ID"], "Veneto (texto regional, igual nas 4 zonas) · %s" % l["ORGANISMO"])
                g.setdefault(k, {})["N° %s" % (num.group(1) if num else "?")] = l["FRASE"]
    return [{"SOURCE_ID": sid, "CHAVE": ch, "POR_DATA": dict(sorted(v.items()))} for (sid, ch), v in sorted(g.items())]


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    raizes = [Path(x.split("=", 1)[1]) for x in argv if x.startswith("--raiz=")]
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x and not x.startswith("--raiz="))
    if not raizes or not a.get("saida"):
        print(__doc__)
        return 2
    docs = [ler(d) for d in documentos(raizes)]
    s = series(docs)
    q = series_qualitativas(docs)
    out = {"DATASET": "SINAL-PRECOCE-SERIES", "RAIZES": [str(r) for r in raizes], "DOCUMENTOS": docs, "SERIES": s,
           "SERIES_REAIS": sum(1 for x in s if x["REAL"]), "SERIES_QUALITATIVAS": q}
    Path(a["saida"]).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"DOCUMENTOS": len(docs), "LINHAS": sum(len(d["LINHAS"]) for d in docs), "SERIES": len(s),
                      "SERIES_REAIS": out["SERIES_REAIS"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
