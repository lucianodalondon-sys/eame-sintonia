#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ONDE ESTA QUEM PUBLICA — o SOURCE_LOCATION de uma conta social, pelo site oficial da organizacao.

    lugar_da_organizacao(site_url, owners=None, atlas_texto=None) -> dict
    do_contrato(source_id, raiz=None) -> dict | None

D61 (dono real, 25/09): a data e o local tem de chegar ao item da Sala. Medido (SOC-TEMPO): o coletor
do LinkedIn escrevia `source_location=None`, o do YouTube nem tinha o campo, e nada o completava.

A conta social (pagina LinkedIn, canal YouTube) so tem numero porque o SITE OFICIAL da organizacao
aponta para ela (D21 cond. 2 / D24). E esse site que diz DE QUEM a conta e — e por isso e ele que diz
ONDE esta quem publica. A ordem, da mais precisa para a menos, e sem saltar degraus:

  1. SEDE no cadastro-mestre (`candidatas/ITALY-SOURCE-MASTER-V1.json`, `owners[]`): o dono cujo
     `WEBSITE` e o MESMO host do site oficial → `PROVINCE` (precisao PROVINCE).
  2. PAIS da ficha do site no Atlas (`COUNTRY:` das fichas cujo endereco e o mesmo host), se todas
     concordam → precisao COUNTRY.
  3. NAO SEI, com o porque.

O QUE NUNCA SE USA, e porque:
  · o `REGION:` da ficha do Atlas — descreve a COBERTURA do que a fonte publica («REGIÃO — LAZIO»),
    ou, nas fichas do Curator, a regiao VISTA NA AMOSTRA (lugar dos factos). SOURCE_LOCATION !=
    FACT_LOCATION; cobertura nao e morada.
  · o `COUNTRY_SCOPE` da corrida e o pais do egresso — dizem onde NOS estavamos a pedir
    (VPN_LOCATION != SOURCE_LOCATION).
  · o nome da organizacao («ARPA Lazio» → Lazio) — nome parecido nao prova lugar (D21).
"""
from __future__ import annotations

import json
import os
import re
from urllib.parse import urlparse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join("candidatas", "ITALY-SOURCE-MASTER-V1.json")
ATLAS = os.path.join("docs", "fontes", "ATLAS-DE-FONTES-EAME.md")
LIVRO_CURATOR = os.path.join("curadoria", "italy_contracts_curator.json")
NAO_SEI = "NAO SEI"
RE_URL = re.compile(r"https?://[^\s)>|`\"'<]+")
RE_FICHA = re.compile(r"^#### ([A-Z]{2}-T\d+-\d+)")
RE_PAIS = re.compile(r"^COUNTRY:\s*(.+)$")


def host(url: str) -> str:
    u = (url or "").strip()
    h = urlparse(u if "://" in u else "https://" + u).hostname or ""
    return re.sub(r"^www\.", "", h.lower())


def _vazio(v) -> bool:
    s = str(v or "").strip()
    return not s or s.upper().startswith("NAO SEI") or s.upper().startswith("NÃO SEI")


def _owners(raiz=None) -> list:
    p = os.path.join(raiz or RAIZ, MASTER)
    if not os.path.isfile(p):
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f).get("owners") or []


def _atlas(raiz=None) -> str:
    p = os.path.join(raiz or RAIZ, ATLAS)
    if not os.path.isfile(p):
        return ""
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


def paises_do_host(h: str, atlas_texto: str) -> dict:
    """→ {SOURCE_ID: COUNTRY} das fichas do Atlas cujo endereco e este host."""
    fora, sid, pais, hosts = {}, None, None, set()

    def fechar():
        if sid and h in hosts and not _vazio(pais):
            fora[sid] = pais.strip()
    for linha in atlas_texto.splitlines():
        m = RE_FICHA.match(linha)
        if m:
            fechar()
            sid, pais, hosts = m.group(1), None, set()
            continue
        p = RE_PAIS.match(linha)
        if p:
            pais = p.group(1).split("#")[0].strip()
        for u in RE_URL.findall(linha):
            hosts.add(host(u))
    fechar()
    return fora


def lugar_da_organizacao(site_url: str | None, owners=None, atlas_texto=None) -> dict:
    """→ {SOURCE_LOCATION, SOURCE_LOCATION_BASIS, SOURCE_LOCATION_PRECISION}. Nunca adivinha."""
    if not site_url:
        return {"SOURCE_LOCATION": NAO_SEI, "SOURCE_LOCATION_PRECISION": "NAO DECLARADA",
                "SOURCE_LOCATION_BASIS": "NAO SEI: sem site oficial ligado a conta, nao ha organizacao "
                                         "provada de quem tirar o lugar"}
    h = host(site_url)
    owners = _owners() if owners is None else owners
    donos = [o for o in owners if o.get("WEBSITE") and host(o["WEBSITE"]) == h]
    provincias = sorted({o.get("PROVINCE") for o in donos if not _vazio(o.get("PROVINCE"))})
    if len(provincias) == 1:
        o = next(o for o in donos if o.get("PROVINCE") == provincias[0])
        return {"SOURCE_LOCATION": provincias[0], "SOURCE_LOCATION_PRECISION": "PROVINCE",
                "SOURCE_LOCATION_BASIS": ("SEDE declarada no cadastro-mestre (%s · %s, %s) para o site "
                                          "oficial %s que aponta para a conta"
                                          % (o.get("OWNER_ID"), o.get("OWNER_CANONICAL_NAME", "")[:60],
                                             MASTER.replace(os.sep, "/"), h))}
    if len(provincias) > 1:
        return {"SOURCE_LOCATION": NAO_SEI, "SOURCE_LOCATION_PRECISION": "NAO DECLARADA",
                "SOURCE_LOCATION_BASIS": "NAO SEI: o cadastro-mestre da %s sedes para %s"
                                         % (", ".join(provincias), h)}
    atlas_texto = _atlas() if atlas_texto is None else atlas_texto
    por_sid = paises_do_host(h, atlas_texto)
    paises = sorted(set(por_sid.values()))
    if len(paises) == 1:
        return {"SOURCE_LOCATION": paises[0], "SOURCE_LOCATION_PRECISION": "COUNTRY",
                "SOURCE_LOCATION_BASIS": ("PAIS da ficha do site oficial %s no Atlas (%s), o site que "
                                          "aponta para a conta; a regiao da ficha e cobertura, nao morada"
                                          % (h, ", ".join(sorted(por_sid))))}
    return {"SOURCE_LOCATION": NAO_SEI, "SOURCE_LOCATION_PRECISION": "NAO DECLARADA",
            "SOURCE_LOCATION_BASIS": ("NAO SEI: o site oficial %s %s" % (
                h, "aparece no Atlas com paises diferentes (%s)" % ", ".join(paises) if paises
                else "nao tem sede no cadastro-mestre nem ficha com pais no Atlas"))}


CAMPOS = ("SOURCE_LOCATION", "SOURCE_LOCATION_BASIS", "SOURCE_LOCATION_PRECISION")


def do_contrato(source_id: str, raiz=None) -> dict | None:
    """O lugar que o CONTRATO da fonte (livro do Curator) declara, ou None se ele nao declara.
    O contrato e o dono; quem colhe so o le — como faz com a regra do DOCUMENT_ID."""
    p = os.path.join(raiz or RAIZ, LIVRO_CURATOR)
    if not source_id or not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8") as f:
        for c in json.load(f).get("FONTES") or []:
            if c.get("SOURCE_ID") == source_id and not _vazio(c.get("SOURCE_LOCATION")):
                return {k: c.get(k) for k in CAMPOS}
    return None
