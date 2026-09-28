#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O VIGIA DA ESTEIRA — de hora a hora, quando cada etapa andou pela ultima vez, e quem parou.

    MISSAO   ESTEIRA-SOZINHA (28/09/2026)
    QUEM CHAMA  o supervisor (`curadoria/supervisor.py::_hook_esteira`); ou a mao:
    python3 medidas/vigia_da_esteira.py            # mede agora e escreve curadoria/ESTEIRA-SAUDE.json

MEDIR NAO E FILTRAR
-------------------
O vigia nao barra nada e nao conserta nada: le o rasto que cada etapa ja deixa e escreve UM
ficheiro, `curadoria/ESTEIRA-SAUDE.json`, que o coordenador le. Uma linha por hora tambem vai para
`curadoria/ESTEIRA-SAUDE-HISTORICO.ndjson` (runtime, fora do Git).

AS ETAPAS, ONDE SE LE «ANDOU», E O N DE CADA UMA (declarado — mude aqui, e so aqui)
------------------------------------------------------------------------------------
    fonte         robo de fontes: ultimo batimento do WORKER (supervisor._ultimo_heartbeat)   N 24 h
    coleta        maior FINISHED_AT nos livros de corridas (arvore + ITALY_OPS_ROOT)          N 26 h (D86: 24 h + folga)
    agendador     ultima linha de <ITALY_OPS_ROOT>/.../logs/runs.log (a tarefa ForwardOnly)  N  2 h (corre de hora a hora)
    passagem      PAS_VERIFICADO_EM no estado do supervisor (a passagem olhou o livro)       N  1 h
    sala          max(pousado_em) da Sala, so SELECT                                          N 48 h
    intelligence  INT_ULTIMA_CORRIDA_EM no estado do supervisor                               N 24 h
    pote          INT_ULTIMA_SUBIDA_EM (pote que passou no fiscal e subiu)                    N 24 h
    portal        mtime de italia-portale/client/sintonia-pote.js (o que o casco local le)   N 24 h
    portal_publico  o deploy publico (D126): NAO SEI — medir e rede, e o vigia nao sai.

    SEM MARCA NAO E «ESTA TUDO BEM». Uma etapa cuja marca nao se consegue ler fica NAO SEI e
    entra nos ALERTAS. O vigia calado e o unico erro que ele nao pode cometer.

Uma etapa parada com a de cima tambem parada leva `CAUSA_PROVAVEL = A_MONTANTE`: a Sala nao anda
se a coleta nao anda. E ajuda de leitura, nao silencia o alerta.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

CURADORIA = RAIZ / "curadoria"
SAUDE = CURADORIA / "ESTEIRA-SAUDE.json"
HISTORICO = CURADORIA / "ESTEIRA-SAUDE-HISTORICO.ndjson"
ESTADO_DO_SUPERVISOR = CURADORIA / "SUPERVISOR-STATE.json"
POTE_NO_CASCO = RAIZ / "italia-portale" / "client" / "sintonia-pote.js"
INTERVALO = timedelta(hours=1)
NAO_SEI = "NAO SEI"

#: (etapa, N horas, a etapa de cima). A ORDEM e a da esteira.
ETAPAS = (
    ("fonte", 24, None),
    ("coleta", 26, None),
    ("agendador", 2, None),
    ("passagem", 1, "coleta"),
    ("sala", 48, "coleta"),
    ("intelligence", 24, "sala"),
    ("pote", 24, "intelligence"),
    ("portal", 24, "pote"),
)
ANDANDO, PARADA = "ANDANDO", "PARADA"


def _quando(v) -> datetime | None:
    if v in (None, "", NAO_SEI):
        return None
    s = str(v).strip().replace("Z", "+00:00").replace(" ", "T", 1)
    if len(s) >= 3 and s[-3] in "+-" and s[-3:].lstrip("+-").isdigit():
        s += ":00"
    try:
        d = datetime.fromisoformat(s)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


# ── as marcas, cada uma lida do dono dela ────────────────────────────────────
def _estado_do_supervisor() -> dict:
    try:
        return json.loads(ESTADO_DO_SUPERVISOR.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def marca_fonte():
    sys.path.insert(0, str(CURADORIA))
    import supervisor as S                                       # noqa: PLC0415
    hb = S._ultimo_heartbeat()
    return hb.isoformat() if hb else None, "batimento do worker (run log / WORKER-HEARTBEAT.json)"


def _raizes() -> list[Path]:
    out = [RAIZ]
    ops = os.environ.get("ITALY_OPS_ROOT")
    if ops and Path(ops).resolve() != RAIZ.resolve():
        out.append(Path(ops))
    return out


def marca_coleta():
    melhor = None
    for r in _raizes():
        p = r / "data" / "collection-ledger" / "italy" / "runs.ndjson"
        if not p.exists():
            continue
        for linha in p.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                d = _quando(json.loads(linha).get("FINISHED_AT"))
            except (ValueError, AttributeError):
                continue
            if d and (melhor is None or d > melhor):
                melhor = d
    return melhor.isoformat() if melhor else None, "maior FINISHED_AT nos livros de corridas"


def marca_agendador():
    ops = os.environ.get("ITALY_OPS_ROOT")
    if not ops:
        return None, "ITALY_OPS_ROOT ausente: o log da tarefa ForwardOnly nao se le daqui"
    p = Path(ops) / "data" / "collection-ledger" / "italy" / "logs" / "runs.log"
    try:
        ult = [l for l in p.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()][-1]
    except (OSError, IndexError):
        return None, "%s sem linhas" % p
    trava = Path(ops) / ".italy-forward-only.lock"
    nota = "ultima linha do runs.log da tarefa"
    if trava.exists():
        nota += " · TRAVA PRESENTE %s (sem PID nem idade no codigo: pode ser orfa)" % trava
    for pedaco in ult.replace("\t", " ").split():
        if pedaco.startswith(("STARTED=", "FINISHED=")):
            d = _quando(pedaco.split("=", 1)[1])
            if d:
                return d.isoformat(), nota
    return None, nota + " · hora ilegivel: %r" % ult[:120]


def marca_sala(consulta=None):
    if consulta is None:
        sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
        import micro_coleta as MC                               # noqa: PLC0415
        consulta = MC.sql
    linhas = consulta("select max(pousado_em) from sala_de_espera")
    v = linhas[0][0] if linhas and linhas[0] else None
    d = _quando(v)
    return d.isoformat() if d else None, "max(pousado_em) da Sala (so SELECT)"


def marca_portal():
    try:
        return (datetime.fromtimestamp(POTE_NO_CASCO.stat().st_mtime, timezone.utc).isoformat(),
                "mtime de %s" % POTE_NO_CASCO.relative_to(RAIZ))
    except OSError:
        return None, "%s nao existe" % POTE_NO_CASCO.relative_to(RAIZ)


def marcas_padrao(estado_sup: dict) -> dict:
    return {
        "fonte": marca_fonte,
        "coleta": marca_coleta,
        "agendador": marca_agendador,
        "passagem": lambda: (estado_sup.get("PAS_VERIFICADO_EM"), "PAS_VERIFICADO_EM (estado do supervisor)"),
        "sala": marca_sala,
        "intelligence": lambda: (estado_sup.get("INT_ULTIMA_CORRIDA_EM"),
                                 "INT_ULTIMA_CORRIDA_EM (estado do supervisor)"),
        "pote": lambda: (estado_sup.get("INT_ULTIMA_SUBIDA_EM"),
                         "INT_ULTIMA_SUBIDA_EM · ultimo pote: %s" % (estado_sup.get("INT_ULTIMO_POTE"),)),
        "portal": marca_portal,
    }


# ── o relatorio ──────────────────────────────────────────────────────────────
def medir(agora: datetime | None = None, marcas: dict | None = None, estado_sup: dict | None = None) -> dict:
    agora = agora or datetime.now(timezone.utc)
    estado_sup = _estado_do_supervisor() if estado_sup is None else estado_sup
    marcas = marcas or marcas_padrao(estado_sup)
    etapas, alertas = {}, []
    for nome, n, cima in ETAPAS:
        try:
            quando, de_onde = marcas[nome]()
        except Exception as e:  # noqa: BLE001 — nao conseguir ler e NAO SEI, nunca «tudo bem»
            quando, de_onde = None, "erro a ler: %s" % repr(e)[:200]
        d = _quando(quando)
        linha = {"ULTIMA_VEZ": d.isoformat() if d else NAO_SEI, "N_HORAS": n, "LIDO_DE": de_onde}
        if d is None:
            linha["ESTADO"] = NAO_SEI
        else:
            horas = round((agora - d).total_seconds() / 3600, 2)
            linha["HORAS_PARADA"] = horas
            linha["ESTADO"] = PARADA if horas > n else ANDANDO
        if linha["ESTADO"] != ANDANDO:
            if cima and etapas.get(cima, {}).get("ESTADO") in (PARADA, NAO_SEI):
                linha["CAUSA_PROVAVEL"] = "A_MONTANTE (%s)" % cima
            alertas.append({"ETAPA": nome, "ESTADO": linha["ESTADO"], "N_HORAS": n,
                            "HORAS_PARADA": linha.get("HORAS_PARADA", NAO_SEI),
                            "CAUSA_PROVAVEL": linha.get("CAUSA_PROVAVEL")})
        etapas[nome] = linha
    etapas["portal_publico"] = {"ULTIMA_VEZ": NAO_SEI, "ESTADO": NAO_SEI,
                                "LIDO_DE": "deploy publico (D126): medir e rede, e o vigia nao sai"}
    return {"SCHEMA": "ESTEIRA-SAUDE/v1", "MEDIDO_EM": agora.isoformat(),
            "ALERTA": bool(alertas), "ALERTAS": alertas, "ETAPAS": etapas,
            "PLANO_DA_PASSAGEM": estado_sup.get("PAS_ULTIMO_PLANO"),
            "ULTIMO_DELTA_DA_INTELLIGENCE": estado_sup.get("INT_ULTIMO_DELTA"),
            "COMO_LER": "ALERTA=true quando alguma etapa passou de N horas parada ou nao se sabe "
                        "quando andou. N por etapa em medidas/vigia_da_esteira.py::ETAPAS."}


def escrever(relatorio: dict, saude: Path = SAUDE, historico: Path = HISTORICO) -> None:
    saude.parent.mkdir(parents=True, exist_ok=True)
    tmp = saude.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(relatorio, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, saude)
    with historico.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"MEDIDO_EM": relatorio["MEDIDO_EM"], "ALERTAS": relatorio["ALERTAS"]},
                            ensure_ascii=False) + "\n")


def vigiar_se_devido(estado: dict, *, agora: datetime | None = None, marcas=None,
                     saude: Path = SAUDE, historico: Path = HISTORICO) -> dict:
    """De hora a hora. Guarda VIG_ULTIMO_EM em `estado`."""
    agora = agora or datetime.now(timezone.utc)
    ultimo = _quando(estado.get("VIG_ULTIMO_EM"))
    if ultimo and agora - ultimo < INTERVALO:
        return {"ACCAO": "NADA"}
    r = medir(agora, marcas, estado)
    escrever(r, saude, historico)
    estado["VIG_ULTIMO_EM"] = agora.isoformat()
    return {"ACCAO": "ESCREVEU", "ALERTA": r["ALERTA"],
            "ALERTAS": [(a["ETAPA"], a["ESTADO"]) for a in r["ALERTAS"]]}


def main(argv=None) -> int:
    r = medir()
    escrever(r)
    print(json.dumps({"ALERTA": r["ALERTA"], "ALERTAS": r["ALERTAS"]}, ensure_ascii=False, indent=1))
    print("escrito:", SAUDE)
    return 1 if r["ALERTA"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
