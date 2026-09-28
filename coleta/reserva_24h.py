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
