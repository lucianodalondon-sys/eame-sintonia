#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O POST DE UM PESQUISADOR ENTRA COMO CANDIDATO — e so com a prova de uma pagina OFICIAL (D80).

    julgar(candidata, *, pagina=None, hosts_oficiais=()) -> {ESTADO, PORQUE, ACTIVITY_ID, PROVA}
    autor_confere(creator_url, perfil_url)               -> True / False / None (NAO SEI)

D80 (delegado, 26/09 06:30), (iv): URLs de posts de pesquisadores LinkedIn SO de
  · pagina OFICIAL (universidade/empregador, evento ou projeto oficial) que CITE o pesquisador e
    LIGUE o post, ou
  · lista do DONO.
A busca publica so DESCOBRE candidatas, nao prova identidade. Sem perfil, login, cookie ou contorno.

ESTADOS (a candidata nunca e mais do que a prova dela):
  PROVADA       pagina oficial conhecida, bytes com o sha256 declarado, que contem o link do post
                (o activity id) E o nome da pessoa — ou lista do dono com referencia.
  SO_CANDIDATA  descoberta sem prova bastante (busca publica; pagina que nao e de casa oficial conhecida;
                falta o link ou o nome nos bytes). Fica a espera; NAO entra na colheita.
  RECUSADA      o endereco nao e um post publico (perfil /in/, login, outra coisa) — a trava do D24,
                a MESMA do coletor (`adaptador_linkedin._alvo_e_post_publico`), sem segunda copia.

NA COLHEITA (o segundo cadeado, sem pedido a mais): a pagina do post declara o autor
(`CREATOR_URL`). `autor_confere` compara-o com o perfil da candidata-pessoa (a identidade que a P5
provou pela pagina oficial). Diferente = o post nao e desta pessoa: o video nao se atribui.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from urllib.parse import urlparse

ORIGENS = ("PAGINA_OFICIAL", "LISTA_DO_DONO", "BUSCA_PUBLICA")
CLASSES_OFICIAIS = ("UNIVERSIDADE", "EMPREGADOR", "EVENTO", "PROJETO")


def _host(url) -> str:
    h = (urlparse(url or "").hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s or "") if not unicodedata.combining(c)).lower()


def _nome_na_pagina(nome: str, texto: str) -> bool:
    """Todos os pedacos do nome (>= 2 letras), sem acento, na pagina. Um so pedaco nao basta."""
    pedacos = [p for p in re.split(r"[^a-z]+", _sem_acento(nome)) if len(p) >= 2]
    return len(pedacos) >= 2 and all(re.search(r"\b%s\b" % re.escape(p), texto) for p in pedacos)


def _post_publico(url):
    import adaptador_linkedin as LI                               # noqa: PLC0415 — o dono da trava D24
    return LI._alvo_e_post_publico(url)


def julgar(c: dict, *, pagina: bytes | None = None, hosts_oficiais=()) -> dict:
    fora = {"ESTADO": "SO_CANDIDATA", "PORQUE": None, "ACTIVITY_ID": None, "PROVA": None}
    try:
        _url, act = _post_publico(c.get("URL"))
    except Exception as e:                                         # noqa: BLE001 — a recusa da trava, com o nome
        return dict(fora, ESTADO="RECUSADA", PORQUE="URL_NAO_E_POST_PUBLICO: %s" % str(e)[:160])
    fora["ACTIVITY_ID"] = act
    origem = c.get("ORIGEM")
    if origem not in ORIGENS:
        return dict(fora, PORQUE="ORIGEM desconhecida: %r (uma de %s)" % (origem, ", ".join(ORIGENS)))
    if origem == "BUSCA_PUBLICA":
        return dict(fora, PORQUE="a busca publica descobre, nao prova (D80): falta pagina oficial ou lista do dono")
    if origem == "LISTA_DO_DONO":
        ref = str(c.get("REF_DO_DONO") or "").strip()
        if not ref:
            return dict(fora, PORQUE="LISTA_DO_DONO sem referencia da decisao")
        return dict(fora, ESTADO="PROVADA", PORQUE="lista do dono (%s)" % ref, PROVA={"LISTA_DO_DONO": ref})
    p = c.get("PROVA_PAGINA") or {}
    falta = []
    if p.get("CLASSE") not in CLASSES_OFICIAIS:
        falta.append("CLASSE da pagina (%s)" % "/".join(CLASSES_OFICIAIS))
    h = _host(p.get("URL"))
    if not h or h not in {_host("https://" + x) for x in hosts_oficiais}:
        falta.append("pagina de casa oficial CONHECIDA (host %r fora da lista)" % h)
    if pagina is None:
        falta.append("os bytes da pagina (guardados por nos)")
    else:
        if hashlib.sha256(pagina).hexdigest() != str(p.get("SHA256") or ""):
            falta.append("sha256 dos bytes igual ao declarado")
        texto = _sem_acento(pagina.decode("utf-8", "replace"))
        if not re.search(r"linkedin\.com/[^\s\"'<>]*activity[-:]%s" % re.escape(act), texto):
            falta.append("o LINK do post (activity %s) na pagina" % act)
        if not _nome_na_pagina(c.get("PESSOA_NOME") or "", texto):
            falta.append("o NOME da pessoa na pagina")
    if falta:
        return dict(fora, PORQUE="falta: " + "; ".join(falta))
    return dict(fora, ESTADO="PROVADA", PORQUE="pagina oficial %s cita a pessoa e liga o post" % h,
                PROVA={"PAGINA_OFICIAL": p.get("URL"), "CLASSE": p.get("CLASSE"), "SHA256": p.get("SHA256"),
                       "LIDA_EM": p.get("LIDA_EM")})


def _slug(url) -> str | None:
    m = re.search(r"linkedin\.com/in/([^/?#]+)", url or "", re.I)
    return m.group(1).lower() if m else None


def autor_confere(creator_url, perfil_url):
    """True = o autor que a pagina do post declara e o perfil da pessoa; False = e outro; None = NAO SEI."""
    a, b = _slug(creator_url), _slug(perfil_url)
    if not a or not b:
        return None
    return a == b
