#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O LEITOR UNICO DE robots.txt DA CASA — pela RFC 9309 (D34, 24/09/2026).

    UM SO LEITOR. QUEM PRECISA DE SABER SE PODE, PERGUNTA AQUI.

PORQUE EXISTE. A casa tinha TRES leitores em Python (`coleta/scrap_http.py`,
`curadoria/gate_de_rota.py`, `curadoria/descobrir.py`), todos com
`urllib.robotparser` — que usa a PRIMEIRA regra que casa e nao conhece `*` nem
`$` no meio do caminho. O coletor (`coleta/italy_pilot_collect.mjs`) ja lia pela
norma. Medido (IA-CUR, 24/09): o SFR Lombardia publica

    User-agent: *
    Disallow: /wps/
    Allow: /wps/portal/site/sfr

Pela norma, `/wps/portal/site/sfr` e PERMITIDO (a regra mais especifica vence);
pelo `urllib.robotparser`, PROIBIDO (a primeira que casa). O Curator fechava a
fonte por um defeito de leitura, e o coletor ter-lha-ia aberto.

A LEITURA (RFC 9309 §2.2):
  · grupos por `User-agent`; o grupo que vale e o do nosso TOKEN de produto (o
    que vem antes da primeira `/` do User-Agent, sem maiusculas); nao havendo, o
    `*`; nao havendo nenhum, tudo permitido. Varios grupos do mesmo agente juntam-se.
  · `Allow`/`Disallow` casam o caminho + query, com `*` (qualquer sequencia) e
    `$` (fim). Vence a regra de caminho MAIS LONGO; no empate vence `Allow`.
    `Disallow:` vazio nao proibe nada. `/robots.txt` e sempre permitido.

A RESPOSTA DO SERVIDOR (RFC 9309 §2.3.1, com duas escolhas da casa — D39):
  · 2xx com texto             -> LIDO
  · 401 / 403                 -> ROBOTS_ACCESS_DENIED: RECUSA por prudencia. ⚠️ MAIS
                                 CONSERVADOR QUE A RFC, e declarado: a norma (§2.3.1.3) diria
                                 «indisponivel, pode»; a casa le um 401/403 ao proprio robots
                                 como «nao nos querem aqui» (muitas vezes um muro anti-robo).
  · outros 4xx (404, 410…)    -> AUSENTE: «indisponivel», pode aceder a tudo (§2.3.1.3)
  · 5xx ou rede em baixo      -> INACESSIVEL: proibido tudo (§2.3.1.4) — NAO SEI, recusa
  · 2xx com HTML no lugar     -> ROBOTS_INVALID_CONTENT: RECUSA — nao afirmamos permissao
                                 que nao lemos. ⚠️ Tambem mais conservador que a RFC (que leria
                                 o HTML como robots sem regras, logo «pode»).
  Nenhuma destas recusas e um Disallow: a regra que decide diz o NOME do estado.

O GEMEO. `coleta/italy_pilot_collect.mjs` (lerRobots/grupoQueVale/robotsPermite)
le igual; `tests/test_robots_rfc9309.py` compara os dois caso a caso.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlsplit

LIDO, AUSENTE, INACESSIVEL, ILEGIVEL = "LIDO", "AUSENTE", "INACESSIVEL", "ILEGIVEL"
# D39 (25/09): duas RECUSAS com nome proprio — nenhuma delas e um Disallow lido.
INVALID_CONTENT = "ROBOTS_INVALID_CONTENT"   # veio HTML (ou outra coisa) no lugar do robots.txt
ACCESS_DENIED = "ROBOTS_ACCESS_DENIED"       # 401/403 ao pedido do robots.txt
RECUSAS = frozenset({INACESSIVEL, ILEGIVEL, INVALID_CONTENT, ACCESS_DENIED})
VERSAO = "ROBOTS/RFC9309-v2 (D39)"

# decodeURI do JavaScript nao desfaz estes (o gemeo Node usa decodeURI)
_RESERVADOS = set(";/?:@&=+$,#")


def _sem_escape(s: str) -> str:
    """Desfaz %XX como o `decodeURI` do gemeo: menos os reservados; UTF-8 invalido fica como esta."""
    def troca(m):
        bruto = m.group(0)
        try:
            txt = bytes.fromhex(bruto.replace("%", "")).decode("utf-8")
        except (UnicodeDecodeError, ValueError):
            raise ValueError
        return "".join(("%%%02X" % ord(ch)) if ch in _RESERVADOS else ch for ch in txt)
    try:
        return re.sub(r"(?:%[0-9A-Fa-f]{2})+", troca, s)
    except ValueError:
        return s


def _casa(padrao: str, caminho: str) -> bool:
    ancorado = padrao.endswith("$")
    corpo = padrao[:-1] if ancorado else padrao
    rx = ".*".join(re.escape(p) for p in corpo.split("*"))
    return re.match("^" + rx + ("$" if ancorado else ""), caminho, re.S) is not None


def token_de(agente: str) -> str:
    return (agente or "").split("/")[0].strip().lower()


@dataclass
class Grupo:
    agentes: list = field(default_factory=list)
    regras: list = field(default_factory=list)      # [(permite: bool, caminho: str)]
    crawl_delay: float | None = None


def ler(texto: str) -> list[Grupo]:
    grupos, atual, a_ler_agentes = [], None, False
    for bruta in re.split(r"\r\n|\r|\n", texto or ""):
        linha = re.sub(r"#.*$", "", bruta).strip()
        m = re.match(r"^([A-Za-z-]+)\s*:\s*(.*)$", linha)
        if not m:
            continue
        campo, valor = m.group(1).lower(), m.group(2).strip()
        if campo == "user-agent":
            if atual is None or not a_ler_agentes:
                atual = Grupo()
                grupos.append(atual)
            atual.agentes.append(valor.lower())
            a_ler_agentes = True
        elif campo in ("allow", "disallow", "crawl-delay"):
            if atual is None:
                continue                  # regra antes de qualquer User-agent: de ninguem
            a_ler_agentes = False
            if campo == "crawl-delay":
                try:
                    n = float(valor)
                    if n >= 0:
                        atual.crawl_delay = n
                except ValueError:
                    pass
            elif valor:
                atual.regras.append((campo == "allow", valor))
    return grupos


@dataclass
class Decisao:
    permite: bool
    regra: str            # a linha que decidiu, ou o porque sem linha
    estado: str

    def __bool__(self):
        return self.permite


class Robots:
    """O robots de UM anfitriao, ja classificado. `can_fetch(agente, url)` mantem a assinatura
    que os chamadores ja usavam com `urllib.robotparser`."""

    def __init__(self, estado: str, texto: str = "", porque: str = ""):
        self.estado, self.texto, self.porque = estado, texto or "", porque
        self.grupos = ler(self.texto) if estado == LIDO else []

    def grupo(self, agente: str) -> Grupo | None:
        tok = token_de(agente)
        nossos = [g for g in self.grupos if tok in g.agentes]
        escolhidos = nossos or [g for g in self.grupos if "*" in g.agentes]
        if not escolhidos:
            return None
        atrasos = [g.crawl_delay for g in escolhidos if g.crawl_delay is not None]
        return Grupo(agentes=[a for g in escolhidos for a in g.agentes],
                     regras=[r for g in escolhidos for r in g.regras],
                     crawl_delay=max(atrasos) if atrasos else None)

    def decidir(self, agente: str, url: str) -> Decisao:
        if self.estado == AUSENTE:
            return Decisao(True, "sem robots.txt (%s) — RFC 9309 §2.3.1.3" % self.porque, self.estado)
        if self.estado == INACESSIVEL:
            return Decisao(False, "robots inacessivel (%s) — RFC 9309 §2.3.1.4: tudo proibido" % self.porque,
                           self.estado)
        if self.estado == ILEGIVEL:
            return Decisao(False, "robots ilegivel (%s) — nao afirmamos permissao que nao lemos" % self.porque,
                           self.estado)
        if self.estado == INVALID_CONTENT:
            return Decisao(False, "%s (%s) — recusa, nao e Disallow (D39)" % (INVALID_CONTENT, self.porque),
                           self.estado)
        if self.estado == ACCESS_DENIED:
            return Decisao(False, "%s (%s) — recusa por prudencia, mais conservador que a RFC; nao e "
                                  "Disallow (D39)" % (ACCESS_DENIED, self.porque), self.estado)
        p = urlsplit(url)
        caminho = (p.path or "/") + ("?" + p.query if p.query else "")
        if caminho == "/robots.txt":
            return Decisao(True, "/robots.txt e sempre permitido", self.estado)
        g = self.grupo(agente)
        if g is None:
            return Decisao(True, "nenhum grupo para %s nem para *" % token_de(agente), self.estado)
        alvo = _sem_escape(caminho)
        melhor = None
        for permite, regra in g.regras:
            padrao = _sem_escape(regra)
            if not _casa(padrao, alvo):
                continue
            if melhor is None or len(padrao) > melhor[0] or (len(padrao) == melhor[0] and permite):
                melhor = (len(padrao), permite, regra)
        if melhor is None:
            return Decisao(True, "nenhuma regra casa", self.estado)
        return Decisao(melhor[1], "%s: %s" % ("Allow" if melhor[1] else "Disallow", melhor[2]), self.estado)

    def can_fetch(self, agente: str, url: str) -> bool:
        return self.decidir(agente, url).permite

    def crawl_delay(self, agente: str) -> float | None:
        g = self.grupo(agente)
        return g.crawl_delay if g else None


def de_resposta(status: int | None, corpo: bytes | str | None = b"", *, erro: str | None = None) -> Robots:
    """Classifica UMA resposta ao pedido de /robots.txt (a busca e de quem chama)."""
    if status is None:
        return Robots(INACESSIVEL, porque="rede: %s" % (erro or "sem resposta"))
    if status in (401, 403):
        return Robots(ACCESS_DENIED, porque="HTTP %d" % status)
    if 400 <= status < 500:
        return Robots(AUSENTE, porque="HTTP %d" % status)
    if status >= 500 or status < 200 or status >= 300:
        return Robots(INACESSIVEL, porque="HTTP %d" % status)
    txt = corpo.decode("utf-8", "replace") if isinstance(corpo, bytes) else (corpo or "")
    cabeca = txt.lstrip()[:9].lower()
    if cabeca.startswith("<!doctype") or cabeca.startswith("<html"):
        return Robots(INVALID_CONTENT, porque="HTML no lugar do robots.txt")
    return Robots(LIDO, txt, porque="HTTP %d" % status)
