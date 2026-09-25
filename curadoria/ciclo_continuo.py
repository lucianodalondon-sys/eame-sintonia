#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CICLO CONTINUO — o Bot de Fontes que nao para.

    NAO HARD STOP PORQUE UMA FONTE FALHOU.
    CLASSIFICAR E SEGUIR.

Uma volta faz:

    1. recupera tarefas orfas de um processo que morreu
    2. esgota o trabalho ELEGIVEL (uma etapa por tarefa)
    3. fecha lote se houver READY novas
    4. escreve o status live
    5. dorme ate haver trabalho outra vez

⚠️ O UNICO SITIO ONDE E LEGITIMO DORMIR e entre voltas, com a fila SEM
NADA elegivel. Dormir com trabalho elegivel por fazer seria o bloqueio
que este projeto existe para acabar. E a espera e limitada pelo relogio da
proxima tarefa adiada — nao por um numero fixo inventado.

    ESPERAR PELA FILA VAZIA != ESPERAR POR UMA FONTE.

Parar so por bloqueio real: escrita fora de escopo, gasto, credencial,
policy nao decidida, corrupcao de estado, owner conflitante.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F              # noqa: E402
import lotes as LOTES         # noqa: E402
import status_live as SL      # noqa: E402
import worker as W            # noqa: E402

DIARIO = RAIZ / "curadoria" / "SOURCE-CURATOR-RUN-LOG.ndjson"

# ⚠️ PARAGEM LIMPA. Matar o processo perde a volta em curso e deixa uma
# tarefa IN_PROGRESS que so a recuperacao de orfas resolve. Um ficheiro-
# -bandeira lido ENTRE voltas para no unico instante em que nao ha trabalho
# a meio — o estado fica coerente sem precisar de recuperacao.
#
#     PEDIR PARA PARAR != MATAR.
PARAR = RAIZ / "curadoria" / "PARAR.flag"

# Espera entre voltas quando nao ha NADA elegivel. Teto, nao valor fixo:
# se houver tarefa adiada para daqui a 40 s, acorda-se aos 40 s.
ESPERA_MAX = 120


def _proximo_relogio() -> float | None:
    """Quantos segundos faltam ate a tarefa adiada mais proxima."""
    agora = F.agora_utc()
    esperas = []
    for t in F._ler()["TAREFAS"]:
        if t["STATUS"] == F.WAITING_RETRY and t["NEXT_ATTEMPT_AT"]:
            d = (F._parse(t["NEXT_ATTEMPT_AT"]) - agora).total_seconds()
            if d > 0:
                esperas.append(d)
    return min(esperas) if esperas else None


def _anotar(evento: dict) -> None:
    evento["AT"] = datetime.now(timezone.utc).isoformat()
    with DIARIO.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(evento, ensure_ascii=False) + "\n")


def uma_volta(pausa: float) -> dict:
    orfas = F.recuperar_orfas()
    feitos = W.correr(max_tarefas=0, pausa=pausa, verboso=True)
    lote = LOTES.fechar_lote()
    s = SL.status()
    SL.SAIDA.write_text(json.dumps(s, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    v = {"EVENTO": "VOLTA", "ORFAS_RECUPERADAS": len(orfas),
         "TAREFAS_EXECUTADAS": len(feitos),
         "RESULTADOS": {r: sum(1 for x in feitos if x["RESULTADO"] == r)
                        for r in ("OK", "PASS_PARCIAL", "DUPLICADA_DE_IRMA", "RETRY", "BLOCK", "FAIL")},
         # FONTE FALHOU != SERVICO MORREU: etapas que levantaram excecao e
         # foram adiadas pelo worker. A volta sobreviveu — esta linha e a prova.
         "FONTES_REBENTARAM": sum(1 for x in feitos if x.get("FONTE_FALHOU")),
         "LOTE": lote.get("READY_BATCH_ID") if lote.get("CRIADO") else None,
         "READY_TOTAL": s["READY_TOTAL"],
         "QUEUE_ELIGIBLE_NOW": s["QUEUE_ELIGIBLE_NOW"],
         "QUEUE_WAITING_RETRY": s["QUEUE_WAITING_RETRY"]}
    # D32 (7) · FILA-PRECISA-DE-IA CONTINUA: o robo refaz a fila a cada volta (escritor unico: o
    # robo; derivada, sem rede). Uma falha aqui NAO mata a volta — fica escrita no diario.
    try:
        import bancada_ia as BIA   # noqa: PLC0415
        fia = BIA.construir_do_disco(escrever=True)
        v["FILA_IA"] = {"TOTAL": fia["TOTAL"], "POR_PERGUNTA": fia["POR_PERGUNTA"],
                        "JANELA_D29": sum(1 for c in fia["CASOS"] if c["JANELA_D29"])}
    except Exception as e:  # noqa: BLE001
        v["FILA_IA"] = {"ERRO": "%s: %s" % (type(e).__name__, str(e)[:120])}
    _anotar(v)
    return v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--voltas", type=int, default=0, help="0 = sem fim")
    ap.add_argument("--pausa", type=float, default=1.0)
    ap.add_argument("--sair-quando-ocioso", action="store_true",
                    help="sair (rc 0) sem elegiveis e sem relogio dentro de ESPERA_MAX")
    a = ap.parse_args()

    print("CICLO CONTINUO DO SOURCE CURATOR — arranque %s" % SL.LC.agora(),
          flush=True)
    _anotar({"EVENTO": "ARRANQUE", "VOLTAS_PEDIDAS": a.voltas})

    n = 0
    while True:
        n += 1
        print("\n--- VOLTA %d ---" % n, flush=True)
        v = uma_volta(a.pausa)
        print("  executadas=%d  %s  ready=%d  elegiveis=%d  a_espera=%d"
              % (v["TAREFAS_EXECUTADAS"], v["RESULTADOS"], v["READY_TOTAL"],
                 v["QUEUE_ELIGIBLE_NOW"], v["QUEUE_WAITING_RETRY"]), flush=True)

        if a.voltas and n >= a.voltas:
            break

        if PARAR.exists():
            print("  pedido de paragem lido entre voltas — a sair limpo",
                  flush=True)
            _anotar({"EVENTO": "PARAGEM_PEDIDA", "VOLTA": n,
                     "MOTIVO": PARAR.read_text(encoding="utf-8").strip()[:120]})
            break

        # Dormir SO com a fila sem nada elegivel, e so ate o proximo relogio.
        prox = _proximo_relogio()

        # ⚠️ OCIOSO SAI. Medido em 23/09 (M2b): o worker 91744 deu 12 voltas
        # com 0 tarefas e nunca saiu; o supervisor so chama o gatilho
        # (reviver -> feeder -> discovery) com o worker MORTO, logo o gatilho
        # ficou desligado — sem discovery, sem revivencias. Sair aqui devolve
        # a vez ao supervisor. Continua-se a dormir so quando o proximo
        # relogio cabe numa espera (<= ESPERA_MAX): esse trabalho e nosso.
        #
        #     SEM TRABALHO A VISTA, O WORKER DEVOLVE A CADEIRA.
        #
        # Saida limpa = rc 0 e evento proprio; o supervisor nao a conta como
        # crash (supervisor._saida_limpa).
        if (a.sair_quando_ocioso and v["QUEUE_ELIGIBLE_NOW"] == 0
                and (prox is None or prox > ESPERA_MAX)):
            print("  ocioso: nada elegivel e nenhum relogio dentro de %ds — "
                  "a devolver a vez ao supervisor" % ESPERA_MAX, flush=True)
            _anotar({"EVENTO": "WORKER_OCIOSO_SAIU", "VOLTA": n,
                     "PROXIMO_RELOGIO_S": round(prox, 0) if prox else None,
                     "ESPERA_MAX": ESPERA_MAX})
            return 0

        if v["QUEUE_ELIGIBLE_NOW"] == 0:
            if prox is None:
                print("  fila sem trabalho e sem adiadas — a aguardar %ds"
                      % ESPERA_MAX, flush=True)
                espera = ESPERA_MAX
            else:
                espera = min(prox + 1, ESPERA_MAX)
                print("  proxima adiada em %.0fs — a aguardar %.0fs"
                      % (prox, espera), flush=True)
            time.sleep(espera)

    _anotar({"EVENTO": "PARAGEM", "VOLTAS": n})
    print("\nPARADO apos %d volta(s). Estado persistido no disco." % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
