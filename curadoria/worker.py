#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O WORKER DO SOURCE CURATOR — pega trabalho, faz UMA etapa, persiste, segue.

    NUNCA DEPENDER DE UM HUMANO PARA CADA SOURCE_ID.

O ciclo e deliberadamente burro e por isso e que sobrevive:

    1. buscar proximo trabalho elegivel
    2. executar UMA etapa
    3. persistir o resultado
    4. actualizar o estado da fonte
    5. pegar o proximo

Uma etapa por volta, nunca duas. Se o processo morre entre a 2 e a 3, quem
reabrir o disco ve uma tarefa IN_PROGRESS e sabe que alguem comecou e nao
fechou — que e a verdade. Um worker que fizesse o ciclo inteiro por fonte
perderia tudo a meio e nao saberia dizer onde parou.

---------------------------------------------------------------------------
O QUE ESTE WORKER NAO FAZ

    NAO COLETA. NAO CUNHA RUN_ID. NAO ESCREVE RAW.
    NAO TOCA ADMISSION, SALA, INTELLIGENCE NEM BIG COLLECTION.

O canario abre UM documento para provar que a rota resolve. Isso e prova
sobre a FONTE, nao aquisicao de conteudo: nada e preservado como acervo.

    VALIDAR != COLETAR.

---------------------------------------------------------------------------
AS PRIMITIVAS DE REDE SAO AS DA CASA — E SAO INJETAVEIS

Na integracao (SOURCE-CURATOR-INTEGRATION, 2026-09-20) este worker deixou de
trazer o seu proprio leitor de robots.txt. A casa tem UM: `coleta/scrap_http.py
::permitido`, e uma guarda (`test_so_um_ficheiro_le_o_robots`) que reprova o
segundo. O canario tambem e o da casa: o motor de rota (`regras/motor_de_rota
.mjs::alvosDoContrato`) pela porta de `curadoria/canario_do_motor.mjs` — a
mesma porta que a Collection usa para descobrir alvos.

    PORTAO  = quem le o robots vivo         (default: scrap_http.permitido)
    SONDA   = quem corre o canario canonico (default: canario_do_motor.mjs)

Sao variaveis de modulo de proposito: uma prova substitui a primitiva mais
funda — a que toca a rede — e deixa TODO o resto do motor a correr de verdade.
Substituir uma camada acima mediria a camada de cima, nao o motor.

Os contratos vem de `ESTADO-ACTUAL-DAS-FONTES-V1.json`, materializado do
registo que a Collection executa — nunca da fotografia do curator.

---------------------------------------------------------------------------
HUMAN REVIEW — quando o worker para e chama alguem

Custo, credencial, policy, conflito semantico, decisao irreversivel, e o
UNKNOWN que nao se resolve sozinho. Tudo o resto ele decide, porque tudo o
resto tem evidencia deterministica.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "curadoria"))
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import evidencia as EV             # noqa: E402
import fila as F                   # noqa: E402
import lifecycle as LC             # noqa: E402

CONTRATO = "SOURCE_CURATOR_WORKER/v2"
ESTADO_ACTUAL = RAIZ / "curadoria" / "ESTADO-ACTUAL-DAS-FONTES-V1.json"
CANARIO_DO_MOTOR = RAIZ / "curadoria" / "canario_do_motor.mjs"

# Classes de falha que NUNCA se tentam outra vez automaticamente.
# Tentar de novo o que esta barrado por politica nao e persistencia: e contorno.
NAO_INSISTIR = {"POLICY", "AUTH", "ROBOTS"}


def agora() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# AS PRIMITIVAS DE REDE — as da casa, injetaveis
# ---------------------------------------------------------------------------
def portao_da_casa(url: str) -> tuple[bool, str]:
    """`coleta/scrap_http.permitido`: (bool, motivo). Levanta
    `PortaoIndisponivel` quando o robots nao pode ser LIDO — e isso nao e
    uma recusa do host."""
    import scrap_http as http  # noqa: WPS433 — o unico leitor de robots da casa
    return http.permitido(url)


def sonda_da_casa(fonte: dict) -> dict:
    """O canario canonico: o motor de rota resolve o contrato e diz se sai
    pelo menos um alvo com identidade. Devolve o JSON da ultima linha.

    Nao se corre aqui nenhuma rede por conta propria: quem vai a rede e o
    script Node, pela mesma porta da Collection, com o mesmo portao de robots.
    """
    r = subprocess.run(["node", str(CANARIO_DO_MOTOR), fonte["SOURCE_ID"]],
                       cwd=str(RAIZ), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=180)
    linhas = [l for l in r.stdout.splitlines() if l.strip().startswith("{")]
    if not linhas:
        return {"PASS": False, "CLASSE": "UNKNOWN",
                "PORQUE": "o canario nao devolveu JSON (exit %d): %s"
                          % (r.returncode, (r.stderr or r.stdout)[-160:])}
    return json.loads(linhas[-1])


PORTAO = portao_da_casa
SONDA = sonda_da_casa


def _contratos() -> dict:
    if not ESTADO_ACTUAL.exists():
        raise FileNotFoundError(
            "%s nao existe. Materialize o estado actual primeiro: "
            "node curadoria/estado_actual_das_fontes.mjs" % ESTADO_ACTUAL)
    d = json.loads(ESTADO_ACTUAL.read_text(encoding="utf-8"))
    return {f["SOURCE_ID"]: f for f in d["FONTES"]}


# ---------------------------------------------------------------------------
# AS ETAPAS — cada uma devolve (RESULTADO, detalhe)
#
# RESULTADO ∈ {OK, RETRY, BLOCK, FAIL}
#   OK     avanca o estado
#   RETRY  transporte/429 — adia ESTA tarefa, nao a fila
#   BLOCK  policy/robots/auth — para, e diz de quem e o servico que falta
#   FAIL   a fonte respondeu e o que devolveu nao serve
# ---------------------------------------------------------------------------
def etapa_validate_route(source_id: str, fonte: dict) -> tuple[str, dict]:
    """O portao do anfitriao, lido AO VIVO pelo leitor da casa.

        ROTA QUE RESPONDE != ROTA PERMITIDA.

    Um 200 nao torna uma rota legal. Esta etapa corre ANTES do canario de
    proposito: nao se bate a uma porta que ja se sabe estar proibida.

    ⚠️ NAO SEI != PROIBIDO. O leitor da casa separa os dois: robots que nao
    pode ser LIDO levanta `PortaoIndisponivel` (rede) ou devolve «ilegivel»
    (o host respondeu outra coisa). Nenhum dos dois e um Disallow, e gravar
    CONTRACT_READY_ROUTE_BLOCKED por um timeout condenaria uma fonte boa por
    defeito do nosso lado.

        rede em baixo / ilegivel -> RETRY (volta depois, por conta propria)
        Disallow lido            -> BLOCK (para, e chama o dono da politica)
    """
    url = fonte.get("ROUTE")
    if not url or url == "NAO SEI":
        return "FAIL", {"PORQUE": "contrato sem endereco de aquisicao"}
    try:
        ok, motivo = PORTAO(url)
    except Exception as e:  # PortaoIndisponivel, e qualquer avaria de transporte
        return "RETRY", {"ROTA": url, "PORQUE": "robots nao pode ser lido — UNKNOWN, "
                                                 "nao proibicao: %s" % type(e).__name__}
    if ok:
        return "OK", {"ROTA": url, "ROBOTS": motivo[:160], "PERMITIDO": True}
    if "ileg" in motivo.lower():
        return "RETRY", {"ROTA": url, "ROBOTS": motivo[:160],
                         "PORQUE": "robots ilegivel — UNKNOWN, nao proibicao"}
    return "BLOCK", {"CLASSE": "ROBOTS", "ROTA": url, "ROBOTS": motivo[:160],
                     "PORQUE": "o endereco do contrato casa com Disallow no robots vivo"}


def etapa_canary(source_id: str, fonte: dict) -> tuple[str, dict]:
    """A corrida real: o contrato resolve e sai um ITEM com identidade?

    Distinguir 429 de falha da fonte e o coracao do backoff: um 429 e a
    plataforma a pedir tempo, nao a fonte a dizer que nao presta.
    """
    try:
        r = SONDA(fonte)
    except Exception as e:
        return "RETRY", {"PORQUE": "%s: %s" % (type(e).__name__, str(e)[:120])}

    if r.get("PASS"):
        return "OK", r
    if r.get("HTTP") in (429, 503):
        return "RETRY", r
    if r.get("HTTP") in (401, 403):
        return "BLOCK", dict(r, CLASSE="AUTH")
    if r.get("CLASSE") == "ROBOTS":
        return "BLOCK", r
    if r.get("CLASSE") == "UNKNOWN":
        return "RETRY", r
    return "FAIL", r


ETAPAS = {
    F.VALIDATE_ROUTE: etapa_validate_route,
    F.CANARY: etapa_canary,
    F.REVALIDATE: etapa_canary,
    F.REPAIR: etapa_canary,
}


def executar_uma(tarefa: dict, contratos: dict, agora=None) -> dict:
    """UMA etapa. Devolve o desfecho, ja persistido na fila e no livro.

    `agora` e o relogio injetado (datetime UTC) — o mesmo que a fila usa. Uma
    prova de backoff que exigisse esperar 3600 s reais nao se corria."""
    sid, tipo, tid = tarefa["SOURCE_ID"], tarefa["TASK_TYPE"], tarefa["TASK_ID"]
    fonte = contratos.get(sid)
    if not fonte:
        F.bloquear(tid, "sem contrato no registo actual da Collection")
        return {"TASK_ID": tid, "SOURCE_ID": sid, "TASK_TYPE": tipo,
                "RESULTADO": "BLOCK", "EVIDENCE_REF": None, "PORQUE": "sem contrato"}

    fn = ETAPAS.get(tipo)
    if not fn:
        F.bloquear(tid, "etapa nao implementada neste worker: %s" % tipo)
        return {"TASK_ID": tid, "SOURCE_ID": sid, "TASK_TYPE": tipo,
                "RESULTADO": "BLOCK", "EVIDENCE_REF": None,
                "PORQUE": "etapa %s sem executor" % tipo}

    resultado, detalhe = fn(sid, fonte)
    ref = EV.guardar(sid, tipo, detalhe)
    estado = LC.estado_de(sid)

    if resultado == "OK":
        F.concluir(tid, "%s OK" % tipo)
        if tipo == F.VALIDATE_ROUTE:
            if estado != LC.CANARY_PENDING:
                LC.registar(sid, LC.CANARY_PENDING,
                            "rota permitida pelo portao do anfitriao",
                            evidence_ref=ref)
            F.enfileirar(sid, F.CANARY, priority=60,
                         motivo="rota validada, falta o canario")
        elif tipo == F.REPAIR and estado == LC.DEGRADED:
            # O REPARO e duas transicoes, e a segunda so existe porque houve
            # canario novo: DEGRADED -> REPAIRING -> READY. Saltar a do meio
            # e exactamente o decreto que a lei do lifecycle proibe.
            LC.registar(sid, LC.REPAIRING, "curator assume o reparo apos "
                        "SOURCE_REPAIR_NEEDED", evidence_ref=ref)
            LC.registar(sid, LC.READY_FOR_COLLECTION,
                        "novo canario resolveu apos reparo", evidence_ref=ref)
        elif estado == LC.READY_FOR_COLLECTION:
            # Ja e READY: REVALIDATE confirmou. Nao se repromove — o guarda
            # recusaria, e com razao; regista-se so a prova nova.
            pass
        else:
            if estado == LC.RETRY_AFTER:
                # A espera acabou e o canario correu. RETRY_AFTER nao promove
                # directo: volta a CANARY_PENDING, que e o unico sitio de onde
                # se promove — e a historia fica com a espera escrita.
                LC.registar(sid, LC.CANARY_PENDING,
                            "o relogio passou e o canario voltou a correr",
                            evidence_ref=ref)
            # PROMOCAO. So daqui, e so com a prova do canario em mao.
            LC.registar(sid, LC.READY_FOR_COLLECTION,
                        "canario resolveu e trouxe um item com identidade",
                        evidence_ref=ref)

    elif resultado == "RETRY":
        espera = detalhe.get("RETRY_AFTER_S")
        F.adiar(tid, retry_after_s=espera, erro=detalhe.get("PORQUE", "")[:160], agora=agora)
        if estado not in (LC.RETRY_AFTER, LC.READY_FOR_COLLECTION, LC.DEGRADED):
            LC.registar(sid, LC.RETRY_AFTER,
                        "adiada: %s" % detalhe.get("PORQUE", "")[:120],
                        evidence_ref=ref)

    elif resultado == "BLOCK":
        classe = detalhe.get("CLASSE", "UNKNOWN")
        F.bloquear(tid, detalhe.get("PORQUE", classe)[:160])
        novo = {"ROBOTS": LC.CONTRACT_READY_ROUTE_BLOCKED,
                "AUTH": LC.AUTH_BLOCK,
                "POLICY": LC.POLICY_BLOCK}.get(classe, LC.CAPABILITY_BLOCK)
        if estado != novo:
            LC.registar(sid, novo, detalhe.get("PORQUE", "")[:200], evidence_ref=ref)

    else:  # FAIL
        F.concluir(tid, "canario reprovou")
        if estado != LC.CONTRACTED_CANARY_FAILED:
            LC.registar(sid, LC.CONTRACTED_CANARY_FAILED,
                        detalhe.get("PORQUE", "")[:200], evidence_ref=ref)

    return {"TASK_ID": tid, "SOURCE_ID": sid, "TASK_TYPE": tipo,
            "RESULTADO": resultado, "EVIDENCE_REF": ref,
            "PORQUE": detalhe.get("PORQUE", "")[:160]}


def correr(max_tarefas: int = 0, pausa: float = 0.8, verboso: bool = True,
           contratos: dict | None = None, agora_fn=None) -> list[dict]:
    """O LOOP. Para quando a fila nao tem nada ELEGIVEL — o que nao e o mesmo
    que a fila estar vazia: pode haver tarefas a espera do relogio delas, e
    esperar por elas aqui seria exactamente o bloqueio que a lei proibe.

    `pausa` e a cortesia entre pedidos a fontes DIFERENTES, nunca a espera de
    um Retry-After: essa vive em NEXT_ATTEMPT_AT, no disco, e nao dorme.
    """
    contratos = contratos if contratos is not None else _contratos()
    feitos = []
    F.recuperar_orfas()
    while True:
        if max_tarefas and len(feitos) >= max_tarefas:
            break
        n = agora_fn() if agora_fn else None
        t = F.proxima(n)
        if t is None:
            break
        r = executar_uma(t, contratos, agora=n)
        feitos.append(r)
        if verboso:
            print("  %-12s %-10s %s  %s" % (r["SOURCE_ID"], r["RESULTADO"],
                                            r["TASK_TYPE"], r["PORQUE"][:70]),
                  flush=True)
        if pausa:
            time.sleep(pausa)
    return feitos


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=0, help="0 = ate esgotar elegiveis")
    ap.add_argument("--pausa", type=float, default=0.8)
    a = ap.parse_args()

    print("WORKER DO SOURCE CURATOR — %s" % CONTRATO)
    print("fila antes: %s" % json.dumps(F.metricas(), ensure_ascii=False))
    feitos = correr(a.max, a.pausa)
    print("\nfila depois: %s" % json.dumps(F.metricas(), ensure_ascii=False))
    print("fontes:      %s" % json.dumps(
        {k: v for k, v in LC.metricas().items() if v}, ensure_ascii=False))
    print("executadas:  %d" % len(feitos))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
