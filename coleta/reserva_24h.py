# -*- coding: utf-8 -*-
"""O CONTADOR MULTICANAL ATOMICO — RESERVAR antes do pedido, para TODAS as linhas (D90, 26/09/2026).

    from coleta import reserva_24h as R
    r = R.reservar("www.cia.it", 1, run_id="IT-T7-...", linha="SITES")
    r["ESTADO"]  ->  "RESERVADO" | "ADIADO_ATE" | "FAIL" | "UNKNOWN"
    r["ATE"]     ->  (so em ADIADO_ATE) o instante UTC em que cabe

Porque existe: o estudo de orquestracao (D90, §2.2) mediu que NAO havia reserva atomica partilhada.
O transporte web perguntava `tetoAtingido()` (leitura) e so DEPOIS gastava (`gastarNaOnda`, escrita):
dois processos no mesmo dominio liam ambos 4 e ambos pediam. Aqui a pergunta e a escrita sao UM passo,
sob o mesmo trinco.

O LIVRO: `SINTONIA_TETO_24H` (um ficheiro JSON) = {"RESERVAS": [{"DOMINIO", "QTD", "EM", "RUN_ID", "LINHA"}]}
  · EM = segundos UTC (epoch). A janela e MOVEL: contam as reservas com EM > agora - 24 h.
  · O dominio e o registavel (a mesma regra do transporte: `coleta/dominio_registavel.dominio_registavel`, a mesma que a prova-teto importa),
    com os orcamentos partilhados declarados (D41: googlevideo.com gasta de youtube.com).
  · Sem livro (variavel vazia): FAIL — nao ha contador, nao se pede. Uma linha de rede sem contador
    partilhado e o que o estudo proibe.

O TRINCO e o do transporte Node (`coleta/italy_pilot_collect.mjs::gastarNaOnda`): um DIRECTORIO
`<livro>.trinco`, que o sistema cria ou recusa de uma vez (mkdir e atomico em Windows e POSIX).
Python e Node excluem-se um ao outro pelo mesmo nome. Escrita por `<livro>.tmp` + rename.

    UMA RESERVA QUE NAO FOI ESCRITA NAO EXISTE. UM LIVRO ILEGIVEL NAO E UM LIVRO VAZIO (UNKNOWN).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

_AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(_AQUI))
import dominio_registavel as _PT                                   # noqa: E402 — um so dono da regra (DA-21: runtime, nao provas/)

TETO = int(os.environ.get("SINTONIA_TETO_POR_HOST") or _PT.TETO_D38)
JANELA_S = 24 * 3600
# Orcamentos partilhados (D41): o video do YouTube vem de googlevideo.com e gasta de youtube.com.
MESMO_ORCAMENTO = {"googlevideo.com": "youtube.com", "ytimg.com": "youtube.com"}
TRINCO_ESPERA_S = 10.0


def dominio(host: str) -> str:
    d = _PT.dominio_registavel(host)
    return MESMO_ORCAMENTO.get(d, d)


def livro() -> Path | None:
    f = os.environ.get("SINTONIA_TETO_24H")
    return Path(f) if f else None


def _ler(f: Path) -> list:
    if not f.exists():
        return []
    d = json.loads(f.read_text(encoding="utf-8"))                  # ilegivel -> ValueError -> UNKNOWN
    if not isinstance(d, dict) or not isinstance(d.get("RESERVAS"), list):
        raise ValueError("TETO_24H sem RESERVAS[]")
    return d["RESERVAS"]


class _Trinco:
    def __init__(self, f: Path):
        self.d = Path(str(f) + ".trinco")

    def __enter__(self):
        fim = time.monotonic() + TRINCO_ESPERA_S
        while True:
            try:
                os.mkdir(self.d)
                return self
            except FileExistsError:
                if time.monotonic() > fim:
                    raise TimeoutError("TETO_24H_TRINCO: %s ocupado ha mais de %.0f s" % (self.d, TRINCO_ESPERA_S))
                time.sleep(0.025)

    def __exit__(self, *a):
        os.rmdir(self.d)


def gasto(reservas: list, dom: str, agora: float) -> int:
    return sum(int(r["QTD"]) for r in reservas if r["DOMINIO"] == dom and float(r["EM"]) > agora - JANELA_S)


def ate_quando(reservas: list, dom: str, qtd: int, agora: float, teto: int = TETO) -> float:
    """O primeiro instante em que `qtd` cabe: vao saindo as reservas mais antigas da janela."""
    vivas = sorted((float(r["EM"]), int(r["QTD"])) for r in reservas
                   if r["DOMINIO"] == dom and float(r["EM"]) > agora - JANELA_S)
    usado = sum(q for _, q in vivas)
    for em, q in vivas:
        usado -= q
        if usado + qtd <= teto:
            return em + JANELA_S
    return agora


def reservar(host: str, qtd: int = 1, *, run_id: str, linha: str, agora: float | None = None,
             teto: int | None = None) -> dict:
    """Pergunta e escreve num so passo, sob o trinco. Nunca levanta: devolve o estado."""
    teto = TETO if teto is None else teto
    f = livro()
    base = {"DOMINIO": None, "QTD": qtd, "RUN_ID": run_id, "LINHA": linha}
    if f is None:
        return dict(base, ESTADO="FAIL", PORQUE="SINTONIA_TETO_24H vazio: sem contador partilhado nao se pede")
    try:
        dom = dominio(host)
    except Exception as ex:                                        # noqa: BLE001
        return dict(base, ESTADO="FAIL", PORQUE="host invalido: %s" % ex)
    base["DOMINIO"] = dom
    if not run_id or not linha or not isinstance(qtd, int) or qtd < 1 or qtd > teto:
        return dict(base, ESTADO="FAIL", PORQUE="pedido invalido (run_id, linha, 1 <= qtd <= teto)")
    try:
        with _Trinco(f):
            reservas = _ler(f)
            t = time.time() if agora is None else agora
            g = gasto(reservas, dom, t)
            if g + qtd > teto:
                return dict(base, ESTADO="ADIADO_ATE", ATE=ate_quando(reservas, dom, qtd, t, teto), GASTO_24H=g)
            reservas.append({"DOMINIO": dom, "QTD": qtd, "EM": t, "RUN_ID": run_id, "LINHA": linha})
            # higiene: o que saiu da janela ha mais de 48 h ja nao decide nada
            reservas = [r for r in reservas if float(r["EM"]) > t - 2 * JANELA_S]
            tmp = Path(str(f) + ".tmp")
            tmp.write_text(json.dumps({"RESERVAS": reservas}, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp, f)
            return dict(base, ESTADO="RESERVADO", GASTO_24H=g + qtd, EM=t)
    except TimeoutError as ex:
        return dict(base, ESTADO="UNKNOWN", PORQUE=str(ex))
    except (ValueError, KeyError, TypeError) as ex:
        return dict(base, ESTADO="UNKNOWN", PORQUE="TETO_24H ilegivel: %s" % ex)


def gasto_24h(host: str, agora: float | None = None) -> int | None:
    """So leitura (planeamento). None = livro ilegivel ou ausente."""
    f = livro()
    if f is None:
        return None
    try:
        return gasto(_ler(f), dominio(host), time.time() if agora is None else agora)
    except (ValueError, KeyError, TypeError):
        return None


if __name__ == "__main__":
    # py coleta/reserva_24h.py <host> [qtd] [run_id] [linha]  -> imprime o estado (para a coordenacao e os testes)
    a = sys.argv[1:]
    print(json.dumps(reservar(a[0], int(a[1]) if len(a) > 1 else 1, run_id=a[2] if len(a) > 2 else "CLI",
                              linha=a[3] if len(a) > 3 else "CLI"), ensure_ascii=False))
