#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A SEDE DE QUEM PUBLICA, lida em PÁGINAS JÁ GUARDADAS da própria fonte. Sem rede. Nunca inventa.

    SOURCE_LOCATION != FACT_LOCATION.   UNKNOWN FICA UNKNOWN.

Dono desta regra (SEDE-37-PREP, 26/09/2026). A regra é a da SEDE-DAS-FONTES (`sede-fontes-v1`,
`ferramentas/sede_fontes/medir_sede.py`), escrita antes de ler os trechos e lida à mão em 14 fontes:

  · conta uma MORADA italiana na página: CAP de 5 dígitos + comune + (SIGLA);
  · o comune vale com a SIGLA entre parêntesis, ou se estiver no gazetteer de `leis/fato_local.py`;
  · a candidata é a morada que aparece em MAIS páginas (o rodapé repete-se; um evento aparece numa);
  · só vale com >= 2 páginas OU com «sede / indirizzo / contatti / dove siamo» ao lado; empate = NAO SEI;
  · NUNCA o `REGION` do Atlas, nunca o nome da instituição.

O que sai tem a forma que o contrato do Curator já tem para as contas sociais
(`leis/lugar_da_organizacao.do_contrato`): SOURCE_LOCATION (nome do gazetteer), SOURCE_LOCATION_BASIS
(a prova: página, sha256, trecho), SOURCE_LOCATION_PRECISION — e o texto da regra que a tabela do coletor
lê (`regras/italy_contracts.mjs`: SOURCE_LOCATION_RULE = «<nome> (<aparte>) — fixo»), conferido pelo MESMO
leitor do contrato (`regras/contratos_de_fonte`). Sem prova: SOURCE_LOCATION = NAO SEI e o porquê.

Precisão: o gazetteer tem regiões e 85 províncias, nenhum comune. Um comune fora dele vira a PROVÍNCIA da
SIGLA — só para as siglas DECLARADAS abaixo (cobertura declarada, não presumida: a mesma lei do gazetteer).
Sigla fora da tabela = NAO SEI (NOT_IN_GAZETTEER), nunca um palpite.
"""
from __future__ import annotations

import os
import re
import sys
from collections import Counter, defaultdict
from html import unescape

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, "regras")):
    if p not in sys.path:
        sys.path.insert(0, p)
from leis import fato_local as FL  # noqa: E402
import contratos_de_fonte as CDF  # noqa: E402

NAO_SEI = "NAO SEI"
GAZ = {n: p for n, p in FL.GAZETTEER}
#: o rodape escreve «20149 - MILANO»: o nome confere-se sem maiusculas e sai o nome do gazetteer (medido: IT-T7-043)
GAZ_MIN = {n.lower(): n for n in GAZ}
#: sigla -> província do gazetteer. DECLARADA: as que a SEDE-DAS-FONTES precisou (propor_regra.py). Crescer
#: esta tabela é decisão escrita, não conveniência.
PROVINCIA_DA_SIGLA = {"MO": "Modena", "RE": "Reggio nell'Emilia", "RM": "Roma", "MI": "Milano", "FI": "Firenze",
                      "BO": "Bologna", "GE": "Genova", "RA": "Ravenna"}

RE_TAG = re.compile(r"<script\b.*?</script>|<style\b.*?</style>|<[^>]+>", re.I | re.S)
RE_MORADA = re.compile(
    r"(?<!\d)(\d{5})\s*[-–,]?\s*((?:[A-ZÀ-Ý][A-Za-zÀ-ÿ'’]+)(?:[\s-]+(?:[A-ZÀ-Ý][A-Za-zÀ-ÿ'’]+|d[ie]l?|di|sul|in|a)){0,4})"
    r"\s*(?:\(\s*([A-Z]{2})\s*\))?")
RE_SEDE = re.compile(r"\bsede(?:\s+legale|\s+operativa|\s+centrale|\s+amministrativa)?\b|\bindirizzo\b|\bdove siamo\b|"
                     r"\bcontatti\b|\bheadquarters?\b|\bp\.?\s?iva\b", re.I)
PARAGEM = {"sede", "tel", "tel.", "telefono", "fax", "email", "e-mail", "mail", "pec", "codice", "partita", "p.iva",
           "piva", "c.f.", "cf", "centralino", "italia", "italy", "iscrizione", "registro", "cap", "numero",
           "orari", "contatti", "privacy", "copyright", "tutti", "via", "viale", "piazza", "questo", "in"}


def texto(b: bytes) -> str:
    t = b.decode("utf-8", "replace") if isinstance(b, bytes) else str(b)
    return re.sub(r"\s+", " ", unescape(RE_TAG.sub(" ", t)))


def moradas(t: str):
    """[(cap, comune, sigla, janela, perto_de_sede)] de UM texto."""
    fora = []
    for m in RE_MORADA.finditer(t):
        palavras = []
        for w in m.group(2).split():
            if w.lower().strip(".,:;") in PARAGEM:
                break
            palavras.append(w)
        comune = " ".join(palavras).strip(" -")
        if not comune or not (m.group(3) or comune.lower() in GAZ_MIN):
            continue
        janela = t[max(0, m.start() - 160): m.end() + 40].strip()
        fora.append((m.group(1), comune, m.group(3) or "", janela, bool(RE_SEDE.search(janela))))
    return fora


def _nome_do_gazetteer(comune: str, sigla: str):
    if comune.lower() in GAZ_MIN:
        n = GAZ_MIN[comune.lower()]
        return n, GAZ[n], "o comune esta no gazetteer"
    if sigla in PROVINCIA_DA_SIGLA:
        p = PROVINCIA_DA_SIGLA[sigla]
        return p, GAZ.get(p, NAO_SEI), "comune fora do gazetteer: a PROVINCIA da sigla %s" % sigla
    return None, None, "NOT_IN_GAZETTEER: comune %r fora do gazetteer e sigla %r fora da tabela declarada" % (comune, sigla)


def sede_das_paginas(paginas) -> dict:
    """`paginas` = [(url, sha256, bytes)] da MESMA fonte. -> os 4 campos do contrato + o recibo."""
    vistas, com_sede, trechos, onde = defaultdict(set), Counter(), {}, defaultdict(list)
    n = 0
    for url, sha, b in paginas:
        n += 1
        for cap, comune, sigla, janela, perto in moradas(texto(b)):
            k = (cap, comune, sigla)
            if sha not in vistas[k]:
                onde[k].append((url, sha))
            vistas[k].add(sha)
            trechos.setdefault(k, janela)
            com_sede[k] += perto
    if not n:
        return _nao_sei("nenhuma pagina guardada desta fonte")
    cands = sorted(vistas, key=lambda k: (-len(vistas[k]), -com_sede[k], k))
    if not cands:
        return _nao_sei("%d pagina(s) guardada(s) lida(s), nenhuma morada com CAP e SIGLA/gazetteer" % n)
    k = cands[0]
    forte = len(vistas[k]) >= 2 or com_sede[k] > 0
    empate = len(cands) > 1 and len(vistas[cands[1]]) == len(vistas[k]) and cands[1][1] != k[1] and len(vistas[k]) < 2
    if not forte or empate:
        return _nao_sei("a morada %s %s %s aparece em %d pagina(s) sem «sede/contatti» ao lado%s"
                        % (k[0], k[1], k[2], len(vistas[k]), " e empata com outra" if empate else ""),
                        candidata={"CAP": k[0], "COMUNE": k[1], "SIGLA": k[2] or None, "TRECHO": trechos[k]})
    nome, precisao, como = _nome_do_gazetteer(k[1], k[2])
    if not nome:
        return _nao_sei(como, candidata={"CAP": k[0], "COMUNE": k[1], "SIGLA": k[2] or None, "TRECHO": trechos[k]})
    url, sha = onde[k][0]
    base = ("PAGINA_GUARDADA_DA_PROPRIA_FONTE · %s · sha256 %s · morada «%s %s%s» em %d pagina(s)%s · %s"
            % (url, sha[:16], k[0], k[1], " (%s)" % k[2] if k[2] else "", len(vistas[k]),
               ", com «sede/contatti» ao lado" if com_sede[k] else "", como))
    # sem parêntesis dentro do aparte: o leitor do contrato corta no primeiro «)» (medido pela SEDE-DAS-FONTES)
    regra = "%s (sede: %s%s, CAP %s; prova: PAGINA_GUARDADA) — fixo" % (nome, k[1], " %s" % k[2] if k[2] else "", k[0])
    valor, prec = confere(regra)
    if (valor, prec) != (nome, precisao):
        return _nao_sei("a regra %r nao passa no leitor do contrato (%s, %s)" % (regra, valor, prec))
    return {"SOURCE_LOCATION": nome, "SOURCE_LOCATION_BASIS": base, "SOURCE_LOCATION_PRECISION": precisao,
            "SOURCE_LOCATION_RULE": regra,
            "RECIBO": {"CAP": k[0], "COMUNE": k[1], "SIGLA": k[2] or None, "PAGINAS": len(vistas[k]),
                       "PERTO_DE_SEDE": com_sede[k], "TRECHO": trechos[k], "PAGINAS_LIDAS": n}}


def confere(regra: str):
    """O que o leitor do contrato devolveria para esta regra: (VALOR, PRECISAO)."""
    for nome in CDF._candidatos_do_texto(regra):
        if nome in GAZ:
            return nome, GAZ[nome]
    return NAO_SEI, "NOT_IN_GAZETTEER"


def _nao_sei(porque, candidata=None) -> dict:
    r = {"SOURCE_LOCATION": NAO_SEI, "SOURCE_LOCATION_BASIS": "NAO SEI — " + porque,
         "SOURCE_LOCATION_PRECISION": NAO_SEI, "SOURCE_LOCATION_RULE": None}
    if candidata:
        r["CANDIDATA_NAO_PROVADA"] = candidata
    return r


def campos_para_o_contrato(r: dict) -> dict:
    """O que se ESCREVE no contrato do Curator: os 4 campos, SÓ quando há prova. UNKNOWN não se escreve —
    a ausência continua a dizer NAO SEI no coletor (`linha.SOURCE_LOCATION_RULE || "NAO SEI"`)."""
    if r.get("SOURCE_LOCATION") in (None, "", NAO_SEI) or not r.get("SOURCE_LOCATION_RULE"):
        return {}
    return {k: r[k] for k in ("SOURCE_LOCATION", "SOURCE_LOCATION_BASIS", "SOURCE_LOCATION_PRECISION",
                              "SOURCE_LOCATION_RULE")}
