# -*- coding: utf-8 -*-
"""O CONTADOR MULTICANAL ATOMICO — RESERVAR antes do pedido, para TODAS as linhas (D90, 26/09/2026),
AGORA ADAPTATIVO (D124, 27/09/2026).

    from coleta import reserva_24h as R
    r = R.reservar("www.cia.it", 1, run_id="IT-T7-...", linha="SITES")
    r["ESTADO"]  ->  "RESERVADO" | "ADIADO_ATE" | "FAIL" | "UNKNOWN"
    r["ATE"]     ->  (so em ADIADO_ATE) o instante UTC em que cabe; r["MOTIVO"] diz porque

Porque existe (D90, §2.2): NAO havia reserva atomica partilhada; dois processos no mesmo dominio liam
ambos 4 e ambos pediam. A pergunta e a escrita sao UM passo, sob o mesmo trinco.

D124 (dono, 27/09): o teto fixo 5/dominio/24h deixou de ser a regra. Este ficheiro ficou FACHADA do dono
unico da politica, `coleta/cortesia_adaptativa.py`: o MESMO livro (SINTONIA_CORTESIA_LIVRO; o nome antigo
SINTONIA_TETO_24H aponta para o mesmo), agora append-only (ndjson), o MESMO trinco `<livro>.trinco`, o
orcamento VIGENTE de cada dominio (sobe sem sinal, recua no sinal) e 1 pedido de cada vez por dominio.
Por isso `qtd` so pode ser 1, e `teto=` ja nao se aceita: o teto nao e de quem pede, e da politica.

    UMA RESERVA QUE NAO FOI ESCRITA NAO EXISTE. UM LIVRO ILEGIVEL NAO E UM LIVRO VAZIO (UNKNOWN).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(_AQUI))
import cortesia_adaptativa as _CA                                  # noqa: E402 — o dono unico da politica (D124)

JANELA_S = 24 * 3600
TRINCO_ESPERA_S = _CA.TRINCO_ESPERA_S


def dominio(host: str) -> str:
    return _CA.dominio(host)


def livro() -> Path | None:
    return _CA.livro()


def reservar(host: str, qtd: int = 1, *, run_id: str, linha: str, agora: float | None = None,
             teto: int | None = None, crawl_delay_s: float | None = None) -> dict:
    """Pergunta e escreve num so passo, sob o trinco. Nunca levanta: devolve o estado."""
    if teto is not None:
        return {"DOMINIO": None, "QTD": qtd, "RUN_ID": run_id, "LINHA": linha, "ESTADO": "FAIL",
                "PORQUE": "D124: o teto e da politica adaptativa (coleta/cortesia_adaptativa.py), nao de quem pede"}
    if qtd != 1:
        return {"DOMINIO": None, "QTD": qtd, "RUN_ID": run_id, "LINHA": linha, "ESTADO": "FAIL",
                "PORQUE": "D124: um pedido de cada vez por dominio (qtd=1)"}
    _CA.TRINCO_ESPERA_S = TRINCO_ESPERA_S
    return dict(_CA.reservar(host, run_id=run_id, linha=linha, crawl_delay_s=crawl_delay_s, agora=agora), QTD=1)


# ── LINHAS-NO-CONTADOR (28/09): a PORTA de UM pedido de uma linha Python ──────────────────────────────
# As linhas BUSCA/CIENCIA/SOCIAL nunca corriam na coleta continua: o transporte delas pedia sem passar por
# aqui. Esta e a porta unica (o MESMO livro, o MESMO trinco, a MESMA politica): reserva ANTES, pede so com
# RESERVADO, e a resposta vai ao livro DEPOIS (o sinal de resistencia mede-se ali; o recuo e da politica).
# O `scrap_http` (pedidos por urllib com o abridor instalado) chega ao mesmo livro por `teto_da_onda`.
import threading as _threading                                     # noqa: E402
_PORTA = _threading.local()


def dentro_da_porta(host: str, url: str | None = None) -> bool:
    """True quando ESTE fio esta dentro de `pedir` para o MESMO orcamento: o pedido ja foi reservado pela porta
    e a resposta vai ser registada por ela. O abridor do `scrap_http` (via `teto_da_onda`) usa-o para nao
    reservar duas vezes o mesmo pedido. Um salto para OUTRO orcamento nao esta coberto: reserva-se a parte."""
    k = getattr(_PORTA, "orcamento", None)
    try:
        return k is not None and _CA.dominio_do_pedido(host, url) == k
    except Exception:                                              # noqa: BLE001
        return False


def _marcas_da_falha(ex: BaseException) -> list:
    import socket
    txt = ("%s %s" % (type(ex).__name__, ex)).lower()
    return ["TIMEOUT"] if isinstance(ex, (socket.timeout, TimeoutError)) or "timed out" in txt or "timeout" in txt else []


def pedir(url: str, fazer, *, run_id: str, linha: str, crawl_delay_s: float | None = None,
          espera_max_s: float = 180.0) -> tuple:
    """(reserva, resultado). `fazer()` -> (status, cabecalhos, corpo[, marcas]) faz O pedido; so e chamado com
    a reserva RESERVADO. resultado None = NAO se pediu (reserva["ESTADO"]/["MOTIVO"] dizem porque: ADIADO_ATE,
    FAIL sem livro, UNKNOWN livro ilegivel). Se `fazer` levanta, a falha vai ao livro (o codigo HTTP do erro,
    ou 0 com a marca TIMEOUT) e a excecao sobe. A espera CURTA (um de cada vez, pausa minima) espera-se;
    orcamento esgotado, Retry-After e pausa de 24 h nunca."""
    import urllib.parse
    host = urllib.parse.urlsplit(url).hostname or ""
    r = _CA.reservar_ou_esperar(host, run_id=run_id, linha=linha, crawl_delay_s=crawl_delay_s,
                                espera_max_s=espera_max_s, url=url)
    if r["ESTADO"] != "RESERVADO":
        return r, None
    _PORTA.orcamento = r["DOMINIO"]
    try:
        res = tuple(fazer())
    except Exception as ex:                                        # noqa: BLE001 — regista e deixa subir
        _PORTA.orcamento = None
        cab = getattr(ex, "headers", None)
        _CA.registrar_resposta(host, int(getattr(ex, "code", 0) or 0), dict(cab.items()) if cab else None,
                               marcas=_marcas_da_falha(ex), url=url, run_id=run_id, linha=linha)
        raise
    _PORTA.orcamento = None
    st, cab, corpo = res[:3]
    marcas = list(res[3]) if len(res) > 3 else []
    _CA.registrar_resposta(host, int(st or 0), dict(cab or {}), marcas=marcas, url=url, corpo=corpo,
                           n_bytes=len(corpo) if corpo is not None else None, run_id=run_id, linha=linha)
    return r, res


def gasto_24h(host: str, agora: float | None = None) -> int | None:
    """So leitura (planeamento). None = livro ilegivel ou ausente."""
    if _CA.livro() is None:
        return None
    e = _CA.estado_do_dominio(host, agora)
    return None if e.get("ESTADO") == "UNKNOWN" else e["GASTO_24H"]


if __name__ == "__main__":
    # py coleta/reserva_24h.py <host> [run_id] [linha]  -> imprime o estado (para a coordenacao e os testes)
    a = sys.argv[1:]
    print(json.dumps(reservar(a[0], 1, run_id=a[1] if len(a) > 1 else "CLI",
                              linha=a[2] if len(a) > 2 else "CLI"), ensure_ascii=False))
