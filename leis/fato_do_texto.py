#!/usr/bin/env python3
"""O LUGAR E O TEMPO DO FACTO, TIRADOS DO TEXTO — os quatro campos da Sala, com a prova.

    campos_do_fato(texto, publication_time=None, publication_time_basis=None) -> dict

Funcao PURA (sem rede, sem banco, sem ficheiros): recebe o texto de UM documento e devolve

    fact_location        "NAO SEI" ou os lugares do facto, todos, separados por " ; "
    fact_location_basis  como se soube, com o trecho do texto; ou porque NAO SEI
    fact_time            "NAO SEI" ou a data/periodo do facto como o texto a escreve
    fact_time_basis      como se soube (ancora, resolucao, trecho); ou porque NAO SEI
    EVIDENCIA            as mesmas coisas, estruturadas, para o envelope do facto

Os nomes sao os das colunas da Sala (`sala_de_espera`) e do tradutor da porta — combinados com a
TEMPO-E-LUGAR (encanamento) e com as bancadas de PUBLICATION_TIME/SOURCE_LOCATION e das 4 chaves.

QUEM LE O TEXTO E O LEITOR ITALIANO, `leis/fato_local.py` — nao ha um segundo leitor aqui. Ele ja
exerce as leis de `leis/lugar_do_fato.py` (MENCAO != FACTO, LISTA TERRITORIAL != FACTO, PUBLICACAO !=
TEMPO DO FACTO, varios lugares = varios, cada um com o seu trecho). Este ficheiro so poe tres coisas a
volta dele:

  1. O CORPO, NAO A PAGINA. O texto que chega a Sala e a pagina inteira: menu, cabecalho, rodape com a
     morada da fonte ("DIREZIONE GENERALE Via Po, 5 - 40139 Bologna"). Linha curta (menu, titulo de
     seccao) e linha de rodape/institucional nao sao corpo, e nao alimentam nem lugar nem tempo.
  2. TEMPO RELATIVO SO ANCORADO. «oggi», «ieri», «la settimana scorsa» dizem uma data SO em relacao a
     publicacao. Sem PUBLICATION_TIME provada (data ISO e base que nao seja NAO SEI) sao descartados e
     procura-se a proxima expressao; com ela, resolvem-se e a base diz RELATIVA_A_PUBLICACAO.
     Medido no leitor sozinho (25/09, 78 textos da Sala): «oggi» saia como tempo do facto sem data de
     publicacao nenhuma.
  3. NUNCA O LUGAR DA FONTE. A funcao nao recebe SOURCE_LOCATION — nao ha caminho para o copiar.

⚠️ `RELATIVA_A_PUBLICACAO` nao esta em `lugar_do_fato.ORIGENS_DO_TEMPO` (a lei nao tem forma de dizer
que o tempo veio da publicacao, de proposito). Aqui a data e a do TEXTO, contada a partir da publicacao
provada — mas a palavra nova e decisao do dono da lei; fica declarada no relatorio da missao.
"""
from __future__ import annotations

import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fato_local as FL          # noqa: E402  (o leitor italiano: nao se reescreve aqui)

NAO_SEI = "NAO SEI"
RELATIVA = "RELATIVA_A_PUBLICACAO"
SEP = " ; "

# ── 1 · o corpo ─────────────────────────────────────────────────────────────
# Uma linha e corpo se tem frase (>= PALAVRAS_MINIMAS palavras) e nao e rodape/institucional.
# WHY 8: nos 78 textos da Sala, menu e titulos de seccao tem 1-5 palavras ("Home", "Notizie",
# "Temi ambientali"); frases de noticia tem 10+. Heuristica declarada, medida no relatorio.
PALAVRAS_MINIMAS = 8
RODAPE = re.compile(
    r"(cookie|privacy|p\.?\s?iva|partita\s+iva|codice\s+fiscale|c\.f\.|\btel\b|\bfax\b|e-?mail|pec\b|"
    r"copyright|©|tutti\s+i\s+diritti|registro\s+stampa|iscrizione\s+(?:sul|al)\s+registro|direttore\s+responsabile|"
    r"seguici|newsletter|iscriviti|\bvia\s+[a-z']+(?:\s+[a-z']+)?,?\s*\d+|\b\d{5}\s*[-–]?\s*[A-Z][a-z]+|"
    r"sede\s+legale|centralino|orari\s+di\s+apertura|mappa\s+del\s+sito|note\s+legali|accessibilit)",
    re.I)


def corpo(texto: str) -> str:
    """As linhas do texto que sao frase de conteudo — menu, cabecalho e rodape ficam de fora."""
    fica = []
    for linha in str(texto or "").splitlines():
        l = linha.strip()
        if len(re.findall(r"[A-Za-zÀ-ÿ']+", l)) < PALAVRAS_MINIMAS:
            continue
        if RODAPE.search(l):
            continue
        fica.append(l)
    return "\n".join(fica)


# ── 2 · o tempo relativo ────────────────────────────────────────────────────
RELATIVOS = {"oggi": 0, "stamattina": 0, "ieri": -1, "questa settimana": "SEMANA_0",
             "la settimana scorsa": "SEMANA_-1", "nei giorni scorsi": "APROXIMADO"}
_RE_RELATIVOS = re.compile(r"\b(" + "|".join(re.escape(k) for k in sorted(RELATIVOS, key=len, reverse=True)) + r")\b", re.I)


def publicacao_provada(publication_time, publication_time_basis) -> date | None:
    """A data de publicacao so ancora se for uma data ISO E tiver base que nao seja NAO SEI."""
    if not publication_time or not publication_time_basis:
        return None
    if str(publication_time_basis).strip().upper().startswith(("NAO SEI", "NÃO SEI", "UNKNOWN")):
        return None
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", str(publication_time))
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def _resolve_relativo(valor: str, pub: date) -> tuple[str, str]:
    r = RELATIVOS[valor.lower()]
    if isinstance(r, int):
        return (pub + timedelta(days=r)).isoformat(), "DATE_EXACT"
    if r == "SEMANA_0":
        a, s, _ = pub.isocalendar()
        return "%d-W%02d" % (a, s), "WEEK"
    if r == "SEMANA_-1":
        a, s, _ = (pub - timedelta(days=7)).isocalendar()
        return "%d-W%02d" % (a, s), "WEEK"
    return "antes de %s" % pub.isoformat(), "APPROXIMATE"


# a precisao do leitor, dita no vocabulario da lei (`lugar_do_fato.RESOLUCAO_TEMPORAL`)
RESOLUCAO = {"DAY": "DATE_EXACT", "WEEK": "WEEK", "MONTH": "MONTH", "SEASON": "SEASON", "YEAR": "APPROXIMATE"}


# ── o que NAO e tempo do facto, tapado antes de perguntar ao leitor ───────────
# Medido a mao nos 78 da Sala (25/09): das 15 datas que o leitor dava, 4 erradas; 3 destas eram estas
# formas — a lei ja as nomeia (SERIES_RANGE_NOT_FACT_TIME, PUBLICATION_STAMP_NOT_FACT_TIME) ou sao prazo:
#   · SERIE DE ANOS    «le settimane 35-39 del 2024, 2025 e 2026» -> nao e o ano do facto
#   · CARIMBO DE LISTA «1 Settembre 2026 Risultati ...» no inicio da linha -> data do item da lista
#   · FIM DE PRAZO     «fino a novembre», «entro il 30 settembre» -> limite, nao a data do facto
_MES = "|".join(FL.MESES)
NAO_E_TEMPO_DO_FACTO = (
    ("SERIE_DE_ANOS", re.compile(r"\b(?:19|20)\d{2}(?:\s*(?:,|\be\b|\bed\b)\s*(?:19|20)\d{2})+\b", re.I)),
    ("CARIMBO_DE_LISTA", re.compile(r"^\s*\d{1,2}\s+(?:%s)\s+\d{4}\b" % _MES, re.I | re.M)),
    ("FIM_DE_PRAZO", re.compile(r"\b(?:fino\s+a(?:l(?:la)?)?|entro(?:\s+il)?)\s+(?:\d{1,2}\s+)?(?:%s)(?:\s+\d{4})?\b" % _MES, re.I)),
)


def _tapar(t: str) -> tuple[str, list]:
    tapados = []
    for nome, rx in NAO_E_TEMPO_DO_FACTO:
        def _sub(m, nome=nome):
            tapados.append("%s «%s»" % (nome, m.group(0).strip()))
            return " " * len(m.group(0))
        t = rx.sub(_sub, t)
    return t, tapados


def _tempo(texto_corpo: str, pub: date | None) -> dict:
    """Pergunta ao leitor; se ele escolher uma expressao relativa sem publicacao provada, tapa-a e pergunta de novo."""
    t, tapados = _tapar(texto_corpo)
    for _ in range(12):                      # no maximo tantas voltas quantas expressoes relativas distintas
        r = FL.tempo_do_fato(t, pub.isoformat() if pub else None)
        v = r.get("FACT_TIME")
        if v in (None, "NOT_KNOWN"):
            r["_TAPADOS"] = tapados
            return r
        if v.lower() in RELATIVOS:
            if pub:
                valor, resol = _resolve_relativo(v, pub)
                r.update({"FACT_TIME": valor, "_RESOLUCAO": resol, "_ORIGEM": RELATIVA, "_EXPRESSAO": v})
                r["_TAPADOS"] = tapados
                return r
            tapados.append(v)
            t = re.sub(r"\b%s\b" % re.escape(v), " " * len(v), t, flags=re.I)
            continue
        r["_TAPADOS"] = tapados
        return r
    return {"FACT_TIME": "NOT_KNOWN", "_TAPADOS": tapados}


# ── 3 · os quatro campos ────────────────────────────────────────────────────
def _trecho(s: str, n: int = 200) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()[:n]


def campos_do_fato(texto: str, publication_time: str | None = None,
                   publication_time_basis: str | None = None) -> dict:
    c = corpo(texto)
    pub = publicacao_provada(publication_time, publication_time_basis)

    aceitas, recusadas = FL.localizacoes_do_fato(c, origem="TEXTO_DO_CORPO")
    lugares = []
    for a in aceitas:
        lugares.append({"LUGAR": a["FACT_LOCATION"], "PRECISAO": a["FACT_LOCATION_PRECISION"],
                        "ORIGEM": "CITADO", "ANCORA": a["FACT_LOCATION_ANCHOR"],
                        "TIPO_DE_EVIDENCIA": a["TYPE_OF_EVIDENCE"], "TRECHO": _trecho(a["FACT_LOCATION_EVIDENCE"])})
    if lugares:
        fact_location = SEP.join(l["LUGAR"] for l in lugares)
        fact_location_basis = SEP.join("CITADO · %s · âncora «%s» · %s · «%s»"
                                       % (l["PRECISAO"], l["ANCORA"], l["TIPO_DE_EVIDENCIA"], l["TRECHO"]) for l in lugares)
    else:
        mencionados = sorted({r["PLACE"] for r in recusadas})
        fact_location = NAO_SEI
        fact_location_basis = ("NAO SEI · nenhum lugar ligado a um acontecimento no corpo do texto"
                               + (" (só mencionados: %s)" % ", ".join(mencionados[:8]) if mencionados else "")
                               + ("" if c else " · o texto não tem corpo (só menu/rodapé)"))

    r = _tempo(c, pub)
    if r.get("FACT_TIME") not in (None, "NOT_KNOWN"):
        origem = r.get("_ORIGEM") or "AMARRADO_AO_ACONTECIMENTO"
        resol = r.get("_RESOLUCAO") or RESOLUCAO.get(r.get("FACT_TIME_PRECISION"), "APPROXIMATE")
        trecho = _trecho(r.get("FACT_TIME_EVIDENCE"))
        fact_time = r["FACT_TIME"]
        if origem == RELATIVA:
            fact_time_basis = ("%s · %s · «%s» contado a partir da publicação %s (%s) · «%s»"
                               % (RELATIVA, resol, r["_EXPRESSAO"], pub.isoformat(), _trecho(publication_time_basis, 60), trecho))
        else:
            fact_time_basis = "%s · %s · «%s»" % (origem, resol, trecho)
        tempo = {"VALOR": fact_time, "RESOLUCAO": resol, "ORIGEM": origem, "TRECHO": trecho}
    else:
        fact_time = NAO_SEI
        why = "nenhuma data do texto ligada ao acontecimento"
        if r.get("_TAPADOS"):
            why += "; descartadas (não são tempo do facto, ou relativas sem publicação provada): %s" % ", ".join(r["_TAPADOS"])
        fact_time_basis = "NAO SEI · " + why + " · a data de publicação nunca preenche este campo"
        tempo = None

    return {"fact_location": fact_location, "fact_location_basis": fact_location_basis[:1000],
            "fact_time": fact_time, "fact_time_basis": fact_time_basis[:600],
            "EVIDENCIA": {"LUGARES": lugares, "TEMPO": tempo,
                          "LINHAS_DE_CORPO": len(c.splitlines()) if c else 0,
                          "PUBLICACAO_USADA": pub.isoformat() if pub else None}}


if __name__ == "__main__":
    ex = ("Home\nNotizie\nFusariosi constatata a Grosseto la settimana scorsa, con sintomi osservati in campo.\n"
          "DIREZIONE GENERALE Via Po, 5 - 40139 Bologna centralino 051 6223811")
    import json
    print(json.dumps(campos_do_fato(ex), ensure_ascii=False, indent=1))
    print(json.dumps(campos_do_fato(ex, "2026-09-23", "meta article:published_time"), ensure_ascii=False, indent=1))
