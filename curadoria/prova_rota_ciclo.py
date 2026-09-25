# -*- coding: utf-8 -*-
"""A PROVA DE ROTA NO CICLO DO ROBO — o canario de rotas corre sozinho, pelo supervisor.

    UMA PROVA QUE SO EXISTE QUANDO ALGUEM SE LEMBRA DE A CORRER
    E UMA PORTA QUE SO ABRE QUANDO HA PORTEIRO.

MEDIDO (PONTE-ONBOARD, 25/09/2026): o onboarding passou a ser chamado pelo
supervisor, mas so onboarda o que tem prova de rota recente do contrato de agora
(`onboardar_rotas_provadas`, PROVA_MAX_IDADE). A prova (`medidas/canario_rotas_elegiveis.py`)
so corria a mao — e as provas antigas do vivo nem tinham impressao do contrato.

O QUE ESTE MODULO FAZ, uma rodada de cada vez:

  1. QUEM PRECISA: as fontes ELIGIBLE no portao, sem contrato no coletor, cuja
     ultima prova NAO e do contrato de agora (impressao `sha_do_contrato`
     diferente ou ausente) OU tem mais de PROVA_MAX_IDADE. Uma prova recente que
     falhou (CAPABILITY_BLOCK, UNKNOWN) tambem conta como recente: repete-se ao
     fim de 7 dias ou quando o contrato mudar — nao a cada rodada.
  2. QUEM VAI NESTA RODADA: no maximo RONDA_MAX_FONTES, e no maximo UMA fonte
     por dominio registavel (D38: 5 pedidos por dominio por corrida; o canario
     faz ate 4 por fonte). O contador da ONDA2-G3 vive no coletor (Node), noutro
     processo — por isso aqui vale a regra de uma fonte por dominio por rodada.
  3. O PORTAO DE EGRESSO POR CONSENSO (`superficie/rede.py --portao-de-egresso IT`)
     ANTES de cada rodada. Sem PASS a rodada nao sai, e fica escrito porque.
  4. O canario corre num PROCESSO PROPRIO (`--juntar`): o supervisor nao espera
     pela rede. A rodada seguinte so sai quando esta acabar e passar RONDA_INTERVALO.
     Robots, pausa e o gate CAPA != MATERIA sao os do canario (leitor da casa).

Nao promove, nao escreve no livro nem na fila. Quem transforma a prova em linha
do coletor continua a ser `onboardar_rotas_provadas.onboardar_se_mudou`.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import collection_gate as G              # noqa: E402
import onboardar_rotas_provadas as ONB   # noqa: E402
import sha_do_contrato as SHA            # noqa: E402

CANARIO_PY = RAIZ / "medidas" / "canario_rotas_elegiveis.py"
REDE_PY = RAIZ / "superficie" / "rede.py"
DIARIO_DA_RONDA = RAIZ / "curadoria" / "PROVA-ROTA-CICLO.log"

RONDA_INTERVALO = timedelta(minutes=30)   # entre o FIM de uma rodada e o inicio da seguinte
RONDA_MAX_FONTES = 8                       # <= 8 x 4 pedidos, espalhados por 8 dominios
RONDA_TEMPO_MAXIMO = timedelta(minutes=30) # uma rodada presa mais do que isto e terminada
PORTAO_TIMEOUT_S = 180

# ── O DOMINIO REGISTAVEL — a MESMA regra do coletor (ONDA2-G3) ──────────────
# Copiada de `coleta/italy_pilot_collect.mjs::dominioRegistavel` (ramo onda2-g3-v1,
# 25/09): as duas ultimas etiquetas, salvo sufixo publico de dois niveis declarado.
# Um sufixo desconhecido junta MAIS do que devia: fica mais apertado, nunca mais
# largo. `tests/test_prova_rota_ciclo.py` compara as duas quando o .mjs a exporta.
SUFIXOS_DE_DOIS_NIVEIS = frozenset({
    "gov.it", "edu.it",
    "abruzzo.it", "abr.it", "basilicata.it", "bas.it", "calabria.it", "cal.it", "campania.it", "cam.it",
    "emilia-romagna.it", "emiliaromagna.it", "emr.it", "friuli-venezia-giulia.it", "friuli-vgiulia.it",
    "friulivenezia-giulia.it", "friulivgiulia.it", "fvg.it", "lazio.it", "laz.it", "liguria.it", "lig.it",
    "lombardia.it", "lom.it", "marche.it", "mar.it", "molise.it", "mol.it", "piemonte.it", "pmn.it",
    "puglia.it", "pug.it", "sardegna.it", "sar.it", "sicilia.it", "sic.it", "toscana.it", "tos.it",
    "trentino.it", "trentino-alto-adige.it", "trentinoaltoadige.it", "taa.it", "umbria.it", "umb.it",
    "valledaosta.it", "valle-daosta.it", "vda.it", "vao.it", "veneto.it", "ven.it",
    "co.uk", "org.uk", "ac.uk", "gov.uk", "com.br", "org.br", "gov.br", "com.au", "org.au",
    "co.jp", "com.es", "com.pt", "co.nz", "com.ar", "com.mx"})


def dominio_registavel(host: str) -> str:
    h = str(host or "").lower()
    h = h[4:] if h.startswith("www.") else h
    h = h.rstrip(".")
    partes = [p for p in h.split(".") if p]
    if len(partes) == 4 and all(p.isdigit() for p in partes) or ":" in h:
        return h
    if len(partes) <= 2:
        return ".".join(partes)
    dois = ".".join(partes[-2:])
    return ".".join(partes[-3:]) if dois in SUFIXOS_DE_DOIS_NIVEIS else dois


def _dominio_da_fonte(c: dict) -> str:
    aq = (c or {}).get("ACQUISITION") or {}
    return dominio_registavel(urlparse(aq.get("INDEX_URL") or c.get("CANONICAL_ENTRY_URL") or "").hostname or "")


# ── 1 · QUEM PRECISA DE PROVA ────────────────────────────────────────────────
def precisam_de_prova(*, agora: datetime, ctx: dict | None = None, curator: dict | None = None,
                      prova: dict | None = None, com_contrato: set[str] | None = None) -> list[str]:
    """ELIGIBLE, sem contrato no coletor, sem prova recente do contrato de agora.
    Por ordem: nunca provadas primeiro, depois a prova mais velha."""
    ctx = ctx if ctx is not None else G._contexto()
    curator = curator if curator is not None else {
        c["SOURCE_ID"]: c for c in json.loads(ONB.CURATOR.read_text(encoding="utf-8"))["FONTES"]}
    if prova is None:
        prova = json.loads(ONB.CANARIO.read_text(encoding="utf-8")) if ONB.CANARIO.exists() else {"LINHAS": []}
    com_contrato = com_contrato if com_contrato is not None else ONB.ids_com_contrato_no_coletor()
    linhas = {l["SOURCE_ID"]: l for l in prova.get("LINHAS", [])}
    fila = []
    for sid in G.elegiveis(ctx=ctx):
        c = curator.get(sid)
        if sid in com_contrato or not c or not (c.get("ACQUISITION") or {}).get("INDEX_URL"):
            continue
        l = linhas.get(sid) or {}
        quando = ONB._quando(l.get("PROVADO_EM"))
        recente = (quando is not None and agora - quando <= ONB.PROVA_MAX_IDADE
                   and l.get("CONTRATO_SHA256") == SHA.do_contrato(c))
        if not recente:
            fila.append((quando or datetime.min.replace(tzinfo=timezone.utc), sid))
    return [sid for _, sid in sorted(fila)]


# ── 2 · QUEM VAI NESTA RODADA: uma fonte por dominio ─────────────────────────
def escolher_ronda(ids: list[str], curator: dict, maximo: int = RONDA_MAX_FONTES) -> list[str]:
    vistos, ronda = set(), []
    for sid in ids:
        d = _dominio_da_fonte(curator.get(sid) or {})
        if not d or d in vistos:
            continue            # dominio repetido espera pela rodada seguinte
        vistos.add(d)
        ronda.append(sid)
        if len(ronda) >= maximo:
            break
    return ronda


# ── 3 · O PORTAO DE EGRESSO, pelo dono dele ──────────────────────────────────
def portao_de_egresso() -> tuple[bool, str]:
    try:
        r = subprocess.run([sys.executable, str(REDE_PY), "--portao-de-egresso", "IT"], cwd=RAIZ,
                           capture_output=True, text=True, timeout=PORTAO_TIMEOUT_S)
        d = json.loads(r.stdout[r.stdout.index("{"):])
    except Exception as e:  # noqa: BLE001 — sem veredito legivel nao ha PASS
        return False, "portao sem resposta legivel: %r" % e
    v = d.get("EGRESS_GATE")
    return v == "PASS", "EGRESS_GATE=%s" % v


# ── 4 · LANCAR A RODADA num processo proprio ─────────────────────────────────
_EM_CURSO: dict = {}     # o Popen da rodada deste processo (nao sobrevive a um reinicio)


def lancar(ronda: list[str]) -> subprocess.Popen:
    log = open(DIARIO_DA_RONDA, "a", encoding="utf-8")
    return subprocess.Popen([sys.executable, str(CANARIO_PY), "--fontes=" + ",".join(ronda), "--juntar"],
                            cwd=RAIZ, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)


def _quando(t):
    return ONB._quando(t)


def provar_se_devido(estado: dict, *, agora: datetime | None = None, planear_fn=None,
                     portao_fn=None, lancar_fn=None) -> dict:
    """Uma volta do supervisor. Devolve o que fez; guarda em `estado` a rodada em curso."""
    agora = agora or datetime.now(timezone.utc)
    proc = _EM_CURSO.get("proc")
    desde = _quando(estado.get("PROVA_ROTA_DESDE"))
    if estado.get("PROVA_ROTA_PID"):
        if proc is not None and proc.poll() is None:
            if desde and agora - desde > RONDA_TEMPO_MAXIMO:
                proc.kill()
                _EM_CURSO.clear()
                estado["PROVA_ROTA_PID"] = None
                estado["PROVA_ROTA_FIM"] = agora.isoformat()
                return {"ACCAO": "RONDA_TERMINADA_POR_TEMPO", "PID": proc.pid}
            return {"ACCAO": "RONDA_EM_CURSO"}
        if proc is None and desde and agora - desde <= RONDA_TEMPO_MAXIMO:
            # reinicio do supervisor com uma rodada lancada pelo anterior: nao se sabe
            # se acabou — espera-se o tempo maximo antes de lancar outra.
            return {"ACCAO": "RONDA_DE_OUTRO_PROCESSO_A_ESPERA"}
        rc = proc.returncode if proc is not None else None
        _EM_CURSO.clear()
        estado["PROVA_ROTA_PID"] = None
        estado["PROVA_ROTA_FIM"] = agora.isoformat()
        return {"ACCAO": "RONDA_ACABOU", "RC": rc}
    fim = _quando(estado.get("PROVA_ROTA_FIM"))
    if fim and agora - fim < RONDA_INTERVALO:
        return {"ACCAO": "NADA"}
    ronda = (planear_fn or _planear)(agora)
    estado["PROVA_ROTA_FIM"] = agora.isoformat()      # conta como tentativa: nao insiste a cada volta
    if not ronda:
        return {"ACCAO": "SEM_FONTES_A_PROVAR"}
    ok, porque = (portao_fn or portao_de_egresso)()
    if not ok:
        return {"ACCAO": "RONDA_NAO_SAIU", "PORQUE": porque, "FONTES": ronda}
    p = (lancar_fn or lancar)(ronda)
    _EM_CURSO["proc"] = p
    estado["PROVA_ROTA_PID"], estado["PROVA_ROTA_DESDE"] = p.pid, agora.isoformat()
    return {"ACCAO": "RONDA_LANCADA", "FONTES": ronda, "PID": p.pid, "PORTAO": porque}


def _planear(agora: datetime) -> list[str]:
    curator = {c["SOURCE_ID"]: c for c in json.loads(ONB.CURATOR.read_text(encoding="utf-8"))["FONTES"]}
    return escolher_ronda(precisam_de_prova(agora=agora, curator=curator), curator)


def main(argv=None) -> int:
    """Sem --lancar so mostra a rodada que sairia (sem rede)."""
    argv = sys.argv[1:] if argv is None else argv
    agora = datetime.now(timezone.utc)
    curator = {c["SOURCE_ID"]: c for c in json.loads(ONB.CURATOR.read_text(encoding="utf-8"))["FONTES"]}
    precisa = precisam_de_prova(agora=agora, curator=curator)
    ronda = escolher_ronda(precisa, curator)
    print("PRECISAM_DE_PROVA=%d  RONDA=%d  %s" % (len(precisa), len(ronda), ",".join(ronda)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
