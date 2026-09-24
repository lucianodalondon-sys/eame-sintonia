#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JANELA DE CULTURA — as fontes que dizem QUANDO agir sobem na fila (D29, 24/09/2026).

    «as fontes que publicam informacao de janela (servizi fitosanitari
     regionali, bollettini agrometeorologici, ARPA agrometeo, consorzi di
     difesa, avisos de praga) sobem na fila de reparo/validacao» — D29.

O Curator ACONSELHA e AVANCA fontes; a agenda da Collection nao e tocada aqui.
Isto so muda a ORDEM em que o robo repara e valida.

A regra nao inventa categoria: parte do Atlas. T3 e PEST / DISEASE / WEEDS
(`docs/fontes/ATLAS-DE-FONTES-EAME.md`), e todo o T3 e janela. Fora do T3, so
entra quem se declara janela no nome ou no endereco com uma FRASE de janela.

⚠️ PALAVRAS SOLTAS MENTEM (medido na copia, 24/09). A primeira regra, com
«avvis», «bollettin», «difesa» e «meteo» soltos, deu 59 fontes — e trouxe
«Bandi e avvisi pubblici», o «Bollettino Ufficiale» da regiao (a gazeta), as
paginas institucionais do CREA Difesa e uma noticia da Arpal sobre a noite da
ciencia. Com frases, 21: o T3 inteiro, dois boletins agrometeorologico/olivicola
e dois de agrometeorologia.
"""
from __future__ import annotations

import re

JANELA = re.compile(
    r"agrometeo|agro-meteo|agrometeorolog|fitosanitar|fitopatolog|condifesa|"
    r"consorzi[oi] di difesa|difesa integrata|difesa fitosanitaria|lotta (integrata|guidata)|"
    r"produzione integrata|bollettin[oi][ _/-]*(agro|fito|olivicol|viticol|frutticol|colture|"
    r"difesa|di difesa|fitosanitar)|avvisi?[ _/-]*(fitosanitar|di difesa|colturali)|"
    r"allerta fitosanitaria", re.I)

_T = re.compile(r"^[A-Z]{2}-T(\d+)-")


def texto_de(c: dict | None) -> str:
    c = c or {}
    aq = c.get("ACQUISITION") or {}
    return " ".join(str(x) for x in (c.get("NAME"), c.get("NOME"), c.get("OWNER"),
                                     aq.get("INDEX_URL"), c.get("CANONICAL_ENTRY_URL"),
                                     c.get("URL")) if x)


def e_janela(source_id: str, *fichas: dict | None) -> bool:
    """True se a fonte e T3, ou se alguma das fichas (contrato do robo, linha do
    coletor, alocacao) se declara janela com uma frase de janela."""
    m = _T.match(source_id or "")
    if m and m.group(1) == "3":
        return True
    return any(JANELA.search(texto_de(f)) for f in fichas if f)
