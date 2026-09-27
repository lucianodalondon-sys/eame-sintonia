#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O MESMO VIDEO EM DUAS CONTAS — a identidade do video, e o registo de quem o viu primeiro.

    identidade(objeto)                 -> (ID, BASE) — ID None quando NAO SEI
    mesmo_video(a, b)                  -> True so se as duas identidades sao CONHECIDAS e iguais
    marcar(unidades, registo=None)     -> as unidades com VIDEO_IDENTITY e, se ja visto, MESMO_VIDEO_QUE

MEDIDO no canario LinkedIn de 24/09 (FREIO-SOCIAL, 26/09): a ARPA Valle d'Aosta
(IT-T2-137, post activity 7507360685509607424) e o ISPRA (IT-T5-160, post activity
7507010113581314048) trouxeram o MESMO video — 679.948 bytes os dois, e o MESMO
`urn:li:digitalmediaAsset:D4D05AQH1yJW2COxvNQ`. Os POSTS sao dois (a ARPA partilhou);
o VIDEO e um.

    O URN DO POST IDENTIFICA A PUBLICACAO. O URN DO ASSET IDENTIFICA O VIDEO.

A identidade, por plataforma, e SO o que a plataforma declara:
  · YOUTUBE  — o id do video (11 caracteres), do objeto (`NATIVE_ID`/`VIDEO_ID`).
  · LINKEDIN — o `ASSET_URN` (`urn:li:digitalmediaAsset:...`) que a pagina do post declara.
Nunca o titulo, a legenda, o tamanho ou o sha dos bytes (dois cortes do mesmo video
teriam sha diferente; dois videos diferentes podem ter o mesmo titulo).

⚠️ UNKNOWN NAO FUNDE. Sem identidade declarada, o video fica `NAO SEI`, com o porque,
e NUNCA e marcado como igual a nada — nem a outro `NAO SEI`.

⚠️ NADA SE APAGA (D62). O segundo post continua a ser um item: a partilha e um facto
(quem partilhou, quando, com que texto). O que muda e que ele diz de quem e o video
(`MESMO_VIDEO_QUE`), para quem conta nao contar duas vezes o mesmo video.
"""
from __future__ import annotations

import json
import os
import re

NAO_SEI = "NAO SEI"
RE_YT = re.compile(r"^[A-Za-z0-9_-]{11}$")
RE_LI_ASSET = re.compile(r"^urn:li:digitalmediaAsset:[A-Za-z0-9_-]+$")
REGISTO = os.path.join("data", "collection-ledger", "italy", "VIDEOS-SOCIAIS.ndjson")


def identidade(objeto: dict) -> tuple[str | None, str]:
    ob = objeto or {}
    raw = ob.get("RAW") or {}
    plat = str(ob.get("PLATFORM") or "").upper()
    if plat == "YOUTUBE":
        vid = str(ob.get("NATIVE_ID") or raw.get("VIDEO_ID") or ob.get("VIDEO_ID") or "")
        if RE_YT.match(vid):
            return "YOUTUBE:" + vid, "id do video declarado pela plataforma (NATIVE_ID)"
        return None, "NAO SEI: o objeto YouTube nao declara um id de video de 11 caracteres"
    if plat == "LINKEDIN":
        urn = str(raw.get("ASSET_URN") or ob.get("ASSET_URN") or "")
        if RE_LI_ASSET.match(urn):
            return "LINKEDIN:" + urn, "ASSET_URN do video, declarado na pagina publica do post"
        return None, "NAO SEI: a pagina do post nao declarou o ASSET_URN do video (o URN do post nao e o do video)"
    return None, "NAO SEI: plataforma %r sem regra de identidade de video" % (plat or None)


def mesmo_video(a: str | None, b: str | None) -> bool:
    return bool(a) and bool(b) and a not in (NAO_SEI,) and a == b


def _ler(registo: str) -> dict:
    vistos = {}
    try:
        with open(registo, encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    r = json.loads(l)
                    vistos.setdefault(r["VIDEO_IDENTITY"], r)       # o PRIMEIRO fica
    except FileNotFoundError:
        pass
    return vistos


def marcar(unidades: list[dict], objetos: list[dict], registo: str | None = None) -> list[dict]:
    """Carimba cada unidade com a identidade do video do seu objeto e, se o video ja
    foi visto noutra publicacao, com `MESMO_VIDEO_QUE` (a primeira). Acrescenta ao registo
    as que sao vistas pela primeira vez. → as unidades (as mesmas, alteradas no sitio)."""
    vistos = _ler(registo) if registo else {}
    novos = []
    for u, ob in zip(unidades, objetos):
        vid, base = identidade(ob)
        u["VIDEO_IDENTITY"] = vid or NAO_SEI
        u["VIDEO_IDENTITY_BASIS"] = base
        if not vid:
            continue
        eu = {"VIDEO_IDENTITY": vid, "SOURCE_ID": u.get("SOURCE_ID"), "RUN_ID": u.get("RUN_ID"),
              "DOCUMENT_ID": u.get("DOCUMENT_ID"), "POST": (ob or {}).get("URL") or (ob or {}).get("NATIVE_ID")}
        primeiro = vistos.get(vid)
        if primeiro and (primeiro.get("POST"), primeiro.get("SOURCE_ID")) != (eu["POST"], eu["SOURCE_ID"]):
            u["MESMO_VIDEO_QUE"] = {k: primeiro.get(k) for k in ("SOURCE_ID", "RUN_ID", "DOCUMENT_ID", "POST")}
        elif not primeiro:
            vistos[vid] = eu
            novos.append(eu)
    if registo and novos:
        os.makedirs(os.path.dirname(registo), exist_ok=True)
        with open(registo, "a", encoding="utf-8") as f:
            for r in novos:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return unidades
