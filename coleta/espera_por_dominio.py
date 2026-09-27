# -*- coding: utf-8 -*-
"""A ESPERA POR DOMINIO, COM CASTIGO — quando o host nos corta, espera-se MAIS, nunca se pede mais.

    e = EsperaPorDominio(base=1.0)
    e.antes(url)                       # dorme o que falta para este dominio
    d = e.depois(url, http=429, erro="", retry_after="30")
    d["DESISTIR"]                      # True: o host pediu mais do que o maximo — parar este dominio

SCRAP-EVOLUCAO-V1 (26/09, D89, rec. 2.3 do ESTUDO-SCRAPLING-DEEPSEEK.md, a ideia do AutoThrottle, sem a
biblioteca). A casa esperava sempre o mesmo (1 s no portao do Scrap, 3 s na prova de territorio), mesmo
depois de o host a ter cortado. Agora:

  · bloqueio (HTTP 403, 429, 503, ou a ligacao cortada — WinError 10054 / connection reset) DOBRA a
    espera daquele dominio (ate `maximo`);
  · `Retry-After` (segundos ou data HTTP) e CUMPRIDO: a espera passa a ser pelo menos esse tempo;
  · Retry-After MAIOR do que `maximo` = `DESISTIR`: nao se fica horas parado; o dominio fica para outra
    rodada (a janela de 24 h das rodadas, D79, ja o afasta);
  · resposta boa depois de um castigo desce a espera para metade (nunca abaixo da base).

⚠️ ESPERAR NAO E TENTAR DE NOVO. Esta peca nao repete pedido nenhum e nao da vaga nenhuma: o teto por
dominio (D38, 5 por rodada) e de quem conta; aqui so se decide QUANDO sai o proximo pedido que o dono do
teto ja autorizou. Um castigo que virasse retentativa gastaria o teto contra um host que ja disse «pare».
"""
from __future__ import annotations

import os
import re
import sys
import time
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit

CODIGOS_DE_BLOQUEIO = frozenset({403, 429, 503})
RE_CORTE = re.compile(r"10054|connection reset|ConnectionResetError|reset by peer|ECONNRESET", re.I)


def _dominio_da_casa(url_ou_host: str) -> str:
    """A regra do dominio registavel da casa (a da prova-teto, D38/D41); sem ela, o host sem www."""
    h = urlsplit(url_ou_host).hostname if "://" in (url_ou_host or "") else (url_ou_host or "")
    try:
        raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.path.join(raiz, "provas") not in sys.path:
            sys.path.insert(0, os.path.join(raiz, "provas"))
        import prova_teto_dominio as PT                                     # noqa: PLC0415
        return PT.orcamento_de(h)
    except Exception:                                                       # noqa: BLE001
        h = (h or "").lower()
        return h[4:] if h.startswith("www.") else h


def segundos_do_retry_after(valor, agora=None) -> float | None:
    """`Retry-After` em segundos (numero) ou data HTTP. Ilegivel = None (nao se inventa espera)."""
    if valor in (None, ""):
        return None
    v = str(valor).strip()
    if re.fullmatch(r"\d+(\.\d+)?", v):
        return float(v)
    try:
        quando = parsedate_to_datetime(v)
    except (TypeError, ValueError):
        return None
    if quando is None:
        return None
    import datetime as _dt                                                   # noqa: PLC0415
    agora = agora or _dt.datetime.now(_dt.timezone.utc)
    return max(0.0, (quando - agora).total_seconds())


def e_bloqueio(http=None, erro: str = "") -> bool:
    return (http in CODIGOS_DE_BLOQUEIO) or bool(RE_CORTE.search(erro or ""))


class EsperaPorDominio:
    def __init__(self, base: float = 1.0, maximo: float = 120.0, *, dormir=time.sleep,
                 relogio=time.monotonic, dominio_de=_dominio_da_casa):
        if base < 0 or maximo < base:
            raise ValueError("espera invalida: base=%r maximo=%r" % (base, maximo))
        self.base, self.maximo = float(base), float(maximo)
        self._dormir, self._relogio, self._dominio = dormir, relogio, dominio_de
        self.atraso, self.ultimo, self.historico = {}, {}, []

    def atraso_de(self, url) -> float:
        return self.atraso.get(self._dominio(url), self.base)

    def antes(self, url) -> float:
        """Dorme o que falta desde o ultimo pedido a este dominio. → os segundos dormidos."""
        d = self._dominio(url)
        if d not in self.ultimo:
            return 0.0
        falta = self.ultimo[d] + self.atraso.get(d, self.base) - self._relogio()
        if falta > 0:
            self._dormir(falta)
            return falta
        return 0.0

    def depois(self, url, *, http=None, erro: str = "", retry_after=None) -> dict:
        """Regista a resposta e decide a espera do PROXIMO pedido a este dominio."""
        d = self._dominio(url)
        atual = self.atraso.get(d, self.base)
        ra = segundos_do_retry_after(retry_after)
        castigo = e_bloqueio(http, erro)
        desistir = False
        if castigo:
            novo = min(max(atual * 2, self.base * 2, 1.0), self.maximo)
        else:
            novo = max(self.base, atual / 2)
        if ra is not None:
            if ra > self.maximo:
                desistir = True
            novo = min(max(novo, ra), self.maximo)
        self.atraso[d] = novo
        self.ultimo[d] = self._relogio()
        r = {"DOMINIO": d, "HTTP": http, "CASTIGO": castigo, "RETRY_AFTER_S": ra,
             "ESPERA_SEGUINTE_S": novo, "DESISTIR": desistir}
        self.historico.append(r)
        return r
