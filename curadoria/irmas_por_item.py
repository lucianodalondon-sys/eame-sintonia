#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D32 (1): DUPLICADOS ENTRE IRMAS PELA IDENTIDADE DO ITEM.

Medido em 24/09 (provas/ia_cur/IRMAS-FEDERUNACOMA.json): Assomao, Agridigital e Assotrattori
mostram a MESMA base de noticias da FederUnacoma — 44 de 44 EW_ID iguais nas tres listagens. A
pagina de cada item difere no rodape («Assomao e l'associazione...»), por isso o sha256 da pagina
ou do texto visivel NAO apanha a repeticao; e o `_dono` do reparo so compara moradas do MESMO
anfitriao, e as irmas vivem em anfitrioes diferentes.

    O QUE E IGUAL ENTRE IRMAS E O CORPO DA NOTICIA, NAO A PAGINA.

A identidade do item e o sha256 do MAIOR paragrafo, normalizado (entidades desfeitas, espacos
colapsados). Medido: o maior paragrafo tem o mesmo sha256 nas tres irmas para o mesmo EW_ID.
Paragrafo curto demais (< MINIMO) nao identifica nada — devolve None, e None nunca casa.
"""
from __future__ import annotations

import hashlib
import html
import re

MINIMO = 200          # abaixo disto um paragrafo e frase de rodape, nao corpo
VERSAO = "ITEM_IDENTITY/v1 (sha256 do maior paragrafo, >= %d caracteres)" % MINIMO


def corpo_do_item(b: bytes) -> str | None:
    """O maior paragrafo <p> do item, normalizado; None se nenhum chega a MINIMO."""
    t = b.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", t)
    maior = ""
    for p in re.findall(r"(?is)<p\b[^>]*>(.*?)</p>", t):
        p = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", p))).strip()
        if len(p) > len(maior):
            maior = p
    return maior if len(maior) >= MINIMO else None


def identidade_do_item(b: bytes) -> str | None:
    corpo = corpo_do_item(b)
    return hashlib.sha256(corpo.encode("utf-8")).hexdigest() if corpo else None


def irma_que_ja_colhe(identidade: str | None, eu: str, provas: list[dict],
                      ready: set[str]) -> str | None:
    """A fonte READY (que nao eu) cuja prova de canario abriu um item com esta identidade.

    `provas` = PROVAS do LIFECYCLE-EVIDENCE; so contam as de fontes que estao READY agora.
    As READY promovidas antes desta versao nao tem ITEM_IDENTITY na prova: para essas a trava
    e cega ate o canario delas voltar a correr (dito, nao escondido)."""
    if not identidade:
        return None
    for p in provas:
        sid = p.get("SOURCE_ID")
        if sid == eu or sid not in ready:
            continue
        item = ((p.get("DADOS") or {}).get("ITEM_ABERTO") or {})
        if item.get("ITEM_IDENTITY") == identidade:
            return sid
    return None
