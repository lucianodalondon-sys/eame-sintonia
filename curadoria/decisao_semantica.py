#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O canal da decisao semantica: territorio decidido por Opus/humano, com prova.

O QUALIFY bloqueia em SEMANTIC quando nem o nome nem o endereco dizem a que
territorio a fonte pertence, e a mensagem sempre disse «precisa de decisao
semantica (Opus/humano)». Nao havia por onde essa decisao entrar no circuito:
quem decidisse teria de escrever no livro a mao.

Este ficheiro e a porta. O QUALIFY consulta-o ANTES de bloquear, e so ai —
nunca por cima de um territorio que a regra do nome ja decidiu.

    UMA DECISAO SEM PROVA E UMA OPINIAO. O CANAL IGNORA-A.

Medido em 23/09 (S1): uma pagina so decide mal — 6 de 105 fontes ganharam
territorio pelo tema de um item, e pelo menos 4 foram para a gaveta errada.
Por isso a decisao so vale com prova MULTIPLA: pelo menos uma prova do que a
organizacao E (pagina institucional, ou a lei que a cria) e pelo menos duas
do que ela PUBLICA, cada uma com URL e sha256 dos bytes lidos.

Os bytes vivem fora do Git; o sha256 prende a decisao ao que foi lido.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
DECISOES = RAIZ / "curadoria" / "DECISOES-SEMANTICAS-V1.json"

TERRITORIOS = frozenset("T%d" % i for i in range(1, 13))
PAPEIS_DO_QUE_E = frozenset({"INSTITUCIONAL", "LEI"})
PAPEL_DO_QUE_PUBLICA = "CONTEUDO"
MIN_CONTEUDO = 2
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _norm(url: str) -> str:
    p = urlparse((url or "").strip().lower())
    host = re.sub(r"^www\.", "", p.hostname or "")
    return host + (p.path or "").rstrip("/")


def _ler(caminho: Path | None = None) -> list[dict]:
    caminho = caminho or DECISOES
    if not caminho.exists():
        return []
    try:
        return json.loads(caminho.read_text(encoding="utf-8")).get("DECISOES", [])
    except Exception:
        return []


def porque_invalida(dec: dict, ficha: dict) -> str | None:
    """None se a decisao vale para esta ficha; senao, o motivo de a ignorar."""
    if _norm(dec.get("URL", "")) != _norm(ficha.get("URL", "")):
        return "a URL da decisao nao e a da candidata"
    if dec.get("TERRITORIO") not in TERRITORIOS:
        return "territorio fora de T1..T12: %r" % dec.get("TERRITORIO")
    if not (dec.get("DECIDIDO_POR") or "").strip():
        return "sem DECIDIDO_POR"
    provas = dec.get("PROVAS") or []
    boas, urls, shas = [], set(), set()
    for p in provas:
        u = (p.get("URL") or "").strip()
        if not u.startswith(("http://", "https://")):
            continue
        if not _SHA256.match((p.get("SHA256") or "").lower()):
            continue
        if _norm(u) in urls:
            continue                      # a mesma pagina nao conta duas vezes
        # ⚠️ BYTES IGUAIS SAO UMA PROVA SO. Medido em 23/09: em 4 sites
        # (Veneto Agricoltura, Laimburg, Wine Monitor, Agrifood Monitor) tres
        # URLs diferentes devolveram os MESMOS bytes — uma casca de JavaScript
        # sem conteudo. Tres enderecos, zero leitura.
        if p["SHA256"].lower() in shas:
            continue
        urls.add(_norm(u))
        shas.add(p["SHA256"].lower())
        boas.append(p)
    if not any(p.get("PAPEL") in PAPEIS_DO_QUE_E for p in boas):
        return "sem prova do que a organizacao E (INSTITUCIONAL ou LEI com sha256)"
    if sum(1 for p in boas if p.get("PAPEL") == PAPEL_DO_QUE_PUBLICA) < MIN_CONTEUDO:
        return "menos de %d provas do que a fonte PUBLICA (CONTEUDO com sha256)" % MIN_CONTEUDO
    return None


def decisao_para(cand_id: str, ficha: dict,
                 caminho: Path | None = None) -> tuple[dict | None, str]:
    """(decisao valida, porque). Sem decisao valida: (None, motivo)."""
    todas = [d for d in _ler(caminho) if d.get("CANDIDATA_ID") == cand_id]
    if not todas:
        return None, "sem decisao semantica registada"
    if len(todas) > 1:
        # Duas decisoes para a mesma candidata: nao se escolhe uma em silencio.
        return None, "%d decisoes para a mesma candidata — conflito" % len(todas)
    if todas[0].get("TERRITORIO") == "NAO SEI":
        return None, "decisao semantica: NAO SEI — %s" % (todas[0].get("MOTIVO") or "sem motivo")
    motivo = porque_invalida(todas[0], ficha)
    if motivo:
        return None, "decisao ignorada: " + motivo
    return todas[0], "decisao semantica valida"
