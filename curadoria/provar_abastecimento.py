#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA DO ABASTECIMENTO DO BOT — sobre uma COPIA da worktree viva.

    uso: py provar_abastecimento.py <pasta-da-copia>

A pasta tem copias (feitas antes, com `cp`) de: LIFECYCLE-QUEUE-V1.json,
SOURCE-CURATOR-RUN-LOG.ndjson, FONTES-CANDIDATAS.json, DISCOVERY-VISITED.json,
italy_contracts_curator.json. NADA aqui escreve na worktree do servico: a fila
e as candidatas sao apontadas para um TemporaryDirectory.

Tres partes, e cada numero diz se e REAL ou SIMULADO:

  A  FEEDER   ANTES = contado no run-log vivo (REAL).
              DEPOIS = 240 voltas de 15 s do gatilho novo sobre a copia da
              fila e das candidatas, com o feeder contado e nao executado
              (SIMULADO: o relogio e injectado; os ficheiros sao os reais).
  B  FAILED   o robots.txt de cada host das FAILED por robots lido AGORA, uma
              vez, pela MESMA funcao do worker (gate_de_rota.robots_de) — REAL.
              A revivencia sobre a copia da fila — SIMULADO (relogio injectado).
  C  SEMENTES as candidatas que a regra ATUAL chama TEMATICA; robots de cada
              host lido pela funcao do crawl (descobrir._permitido) — REAL.

Rede: so robots.txt, um pedido logico por host. Zero pagina, zero coleta.
"""
from __future__ import annotations

import collections
import json
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import descobrir as D            # noqa: E402
import fila as F                 # noqa: E402
import gate_de_rota as GATE      # noqa: E402
import gatilho_discovery as GD   # noqa: E402

SAIDA = RAIZ / "curadoria" / "ABASTECIMENTO-PROOF-V1.json"


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def _ler(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- A
def parte_a(copia: Path, tmp: Path) -> dict:
    ev = [json.loads(l) for l in
          (copia / "SOURCE-CURATOR-RUN-LOG.ndjson").read_text(encoding="utf-8").splitlines()
          if l.strip()]
    realim = [e for e in ev if e.get("EVENTO") == "REALIMENTACAO"]
    por_hora = collections.Counter(e["AT"][:13] for e in realim)
    eco = [e for e in realim
           if "FEEDER" in e.get("ACCOES", [])
           and (e.get("FEEDER") or {}).get("TAREFAS_CRIADAS") == 0
           and "DISCOVERY" not in e.get("ACCOES", [])]
    horas_cheias = {h: n for h, n in por_hora.items() if n >= 200}

    shutil.copy(copia / "LIFECYCLE-QUEUE-V1.json", F.FILA)
    shutil.copy(copia / "FONTES-CANDIDATAS.json", GD.CANDIDATAS)
    t0 = _agora()
    estado = {"LAST_DISCOVERY_AT": t0.isoformat()}     # discovery em intervalo
    feeder = {"n": 0}

    def _feeder():
        feeder["n"] += 1
        return {"TAREFAS_CRIADAS": 0, "SIMULADO": True}

    anotados, accoes = 0, collections.Counter()
    for k in range(240):
        m = GD.talvez_alimentar(estado, feeder_fn=_feeder,
                                descobrir_fn=lambda: {"SIMULADO": True},
                                agora=t0 + timedelta(seconds=15 * k))
        if m.get("ACCOES"):
            anotados += 1
            accoes.update(m["ACCOES"])
    # a segunda hora, ja sem revivencias pendentes: o regime estacionario
    anotados2 = 0
    for k in range(240, 480):
        m = GD.talvez_alimentar(estado, feeder_fn=_feeder,
                                descobrir_fn=lambda: {"SIMULADO": True},
                                agora=t0 + timedelta(seconds=15 * k))
        if m.get("ACCOES") and m["ACCOES"] != ["DISCOVERY", "FEEDER_2"]:
            anotados2 += 1
    # A ISOLADA: o mesmo, com o reviver desligado — mede SO a mudanca do
    # feeder. Sem isto, as revividas enchem a fila, o gatilho sai por QUEUE_OK
    # e o caminho do NO-OP nem chega a ser exercido com dados reais.
    shutil.copy(copia / "LIFECYCLE-QUEUE-V1.json", F.FILA)
    orig_rev = F.reviver_intermitentes
    F.reviver_intermitentes = lambda agora=None: []
    est_iso = {"LAST_DISCOVERY_AT": t0.isoformat()}
    feeder_iso = {"n": 0}

    def _feeder_iso():
        feeder_iso["n"] += 1
        return {"TAREFAS_CRIADAS": 0, "SIMULADO": True}
    anot_iso = 0
    try:
        for k in range(240):
            m = GD.talvez_alimentar(est_iso, feeder_fn=_feeder_iso,
                                    descobrir_fn=lambda: {"SIMULADO": True},
                                    agora=t0 + timedelta(seconds=15 * k))
            anot_iso += bool(m.get("ACCOES"))
    finally:
        F.reviver_intermitentes = orig_rev

    ats = sorted(datetime.fromisoformat(e["AT"]) for e in eco)
    gaps = sorted((b - a).total_seconds() for a, b in zip(ats, ats[1:])
                  if (b - a).total_seconds() < 120)
    return {
        "ANTES_REAL": {
            "INTERVALO_MEDIANO_ENTRE_ECOS_S": gaps[len(gaps) // 2] if gaps else None,
            "ECOS_CONSECUTIVOS_A_MENOS_DE_2_MIN": len(gaps),
            "FONTE": "SOURCE-CURATOR-RUN-LOG.ndjson da worktree viva (copia)",
            "REALIMENTACAO_TOTAL": len(realim),
            "REALIMENTACAO_ECO_FEEDER_0_CRIADAS": len(eco),
            "HORAS_COM_200_OU_MAIS": horas_cheias,
            "MAX_POR_HORA": max(por_hora.values()) if por_hora else 0,
            "CADENCIA": "1 evento a cada volta de 15 s com fila elegivel 0 = 240/h",
        },
        "DEPOIS_SIMULADO_SO_FEEDER": {
            "VOLTAS": 240, "EVENTOS_ANOTADOS": anot_iso,
            "FEEDER_CHAMADAS": feeder_iso["n"],
            "FEEDER_NOOP_TOTAL": est_iso.get("FEEDER_NOOP_TOTAL", 0)},
        "DEPOIS_SIMULADO": {
            "VOLTAS": 240,
            "EVENTOS_ANOTADOS_1A_HORA": anotados,
            "ACCOES_1A_HORA": dict(accoes),
            "EVENTOS_ANOTADOS_2A_HORA_SEM_DISCOVERY": anotados2,
            "FEEDER_CHAMADAS": feeder["n"],
            "FEEDER_NOOP_TOTAL": estado.get("FEEDER_NOOP_TOTAL", 0),
            "NOTA": ("com o reviver ligado, a 1a volta revive as FAILED por "
                     "transporte e corre o feeder (1 evento); a fila fica com "
                     "trabalho elegivel e o gatilho sai por QUEUE_OK nas voltas "
                     "seguintes — aqui o worker nao corre, por isso o NO-OP so "
                     "se ve em DEPOIS_SIMULADO_SO_FEEDER. A discovery horaria "
                     "continua a anotar (1/h): relogio proprio, nao eco."),
        },
    }


# --------------------------------------------------------------------------- B
def _host_do_contrato(c: dict) -> str | None:
    aq = c.get("ACQUISITION", {})
    url = aq.get("FEED_URL") or aq.get("INDEX_URL")
    return url.split("/")[2] if url and url.count("/") >= 2 else None


def _classe_robots(origem: str) -> str:
    if "inacessivel" in origem:
        return "AINDA_ILEGIVEL"
    if "tratado como Disallow total" in origem:
        return "MURO_NO_ROBOTS_POLICY"          # 401/403 -> BLOCK, nunca revive
    if "nao publica robots.txt" in origem:
        return "SEM_ROBOTS_404_PERMITE"
    return "LEGIVEL"


def parte_b(copia: Path) -> dict:
    fila = _ler(copia / "LIFECYCLE-QUEUE-V1.json")["TAREFAS"]
    contratos = {c["SOURCE_ID"]: c for c in
                 _ler(copia / "italy_contracts_curator.json")["FONTES"]}
    robots_failed = [t for t in fila if t["STATUS"] == F.FAILED
                     and "robots nao pode ser lido" in (t["LAST_ERROR"] or "")]
    outras_failed = [t for t in fila if t["STATUS"] == F.FAILED
                     and t not in robots_failed]

    # «ja leu alguma vez»: outro VALIDATE_ROUTE do MESMO host acabou DONE
    host_de = {}
    for t in fila:
        c = contratos.get(t["SOURCE_ID"])
        if c:
            host_de[t["TASK_ID"]] = _host_do_contrato(c)
    hosts_que_ja_leram = {host_de.get(t["TASK_ID"]) for t in fila
                          if t["TASK_TYPE"] == F.VALIDATE_ROUTE
                          and t["STATUS"] == F.DONE}

    hosts = sorted({host_de.get(t["TASK_ID"]) for t in robots_failed} - {None})

    def _sonda(h):
        try:
            rp, origem = GATE.robots_de(h)
            return h, _classe_robots(origem), origem[:100]
        except Exception as e:                   # noqa: BLE001
            return h, "ERRO_NA_SONDA", type(e).__name__

    with ThreadPoolExecutor(max_workers=8) as ex:
        sondas = {h: (c, o) for h, c, o in ex.map(_sonda, hosts)}

    fontes = []
    for t in robots_failed:
        h = host_de.get(t["TASK_ID"])
        classe, origem = sondas.get(h, ("SEM_CONTRATO", ""))
        fontes.append({"TASK_ID": t["TASK_ID"], "SOURCE_ID": t["SOURCE_ID"],
                       "HOST": h, "ROBOTS_AGORA": classe, "ORIGEM": origem,
                       "JA_LEU_ANTES_NO_MESMO_HOST": h in hosts_que_ja_leram})

    def _veredicto(f):
        if f["ROBOTS_AGORA"] in ("LEGIVEL", "SEM_ROBOTS_404_PERMITE"):
            return "INTERMITENTE_PROVADO_LE_AGORA"
        if f["ROBOTS_AGORA"] == "MURO_NO_ROBOTS_POLICY":
            return "POLICY_SE_REVIVIDA_VIRA_BLOCK"
        if f["JA_LEU_ANTES_NO_MESMO_HOST"]:
            return "INTERMITENTE_JA_LEU_ANTES"
        return "SEM_PROVA_DE_VIDA_HOJE"
    for f in fontes:
        f["VEREDICTO"] = _veredicto(f)

    return {
        "REAL": {
            "FAILED_TOTAL": len(robots_failed) + len(outras_failed),
            "FAILED_POR_ROBOTS_ILEGIVEL": len(robots_failed),
            "HOSTS_SONDADOS": len(hosts),
            "POR_CLASSE_ROBOTS_AGORA_FONTES": dict(collections.Counter(
                f["ROBOTS_AGORA"] for f in fontes)),
            "POR_VEREDICTO_FONTES": dict(collections.Counter(
                f["VEREDICTO"] for f in fontes)),
            "OUTRAS_FAILED": dict(collections.Counter(
                (t["LAST_ERROR"] or "")[:60] for t in outras_failed)),
            "FONTES": fontes,
        },
    }


def parte_b_simulada(copia: Path) -> dict:
    shutil.copy(copia / "LIFECYCLE-QUEUE-V1.json", F.FILA)
    t0 = _agora()
    r1 = F.reviver_intermitentes(t0)
    tipos = collections.Counter(t["TASK_TYPE"] for t in r1)
    eleg = len(F.elegiveis(t0))
    nao = [t for t in F._ler()["TAREFAS"] if t["STATUS"] == F.FAILED]
    return {
        "SIMULADO": {
            "RELOGIO": "agora real; as FAILED tem UPDATED_AT de 22/09 -> degrau 1 (6 h) ja venceu",
            "REVIVIDAS": len(r1),
            "REVIVIDAS_POR_TIPO": dict(tipos),
            "ELEGIVEIS_DEPOIS": eleg,
            "FICAM_FAILED": [(t["TASK_ID"], (t["LAST_ERROR"] or "")[:60]) for t in nao],
            "SEGUNDA_VOLTA_NO_MESMO_INSTANTE": len(F.reviver_intermitentes(t0)),
        },
    }


# --------------------------------------------------------------------------- C
def parte_c(copia: Path) -> dict:
    vis = _ler(copia / "DISCOVERY-VISITED.json")
    todas = D._extrair_sementes_legitimas()
    estado = collections.Counter()
    livres = []
    for s in todas:
        n = D.normalizar(s)
        if n in vis.get("VISITADOS", {}):
            estado["VISITADA"] += 1
        elif n in vis.get("REJEITADOS", {}):
            estado["REJEITADA"] += 1
        else:
            estado["LIVRE"] += 1
            livres.append({"URL": s, "CLASSIFICACAO": D._classificar_semente(s)})
    novas = [s for s in D._sementes_de_segunda_geracao(copia / "FONTES-CANDIDATAS.json")
             if D.normalizar(s["URL"]) not in vis.get("VISITADOS", {})
             and D.normalizar(s["URL"]) not in vis.get("REJEITADOS", {})]
    with ThreadPoolExecutor(max_workers=6) as ex:
        perm = list(ex.map(D._permitido, [s["URL"] for s in novas]))
    for s, p in zip(novas, perm):
        s["ROBOTS_PERMITE_A_SEMENTE"] = p
    cand = _ler(copia / "FONTES-CANDIDATAS.json")["CANDIDATAS"]
    em = [c for c in cand if c.get("ESTADO") == "EM_ANALISE"]
    return {
        "CATALOGO_REAL": {"SEMENTES": len(todas), **estado, "LIVRES": livres},
        "REGRA": ("TEMATICA = dominio na lista agro/ambiental ou subdominio "
                  "agri./agricoltura./fitosanitario.; GENERICA = regione.*.it; "
                  "UNKNOWN = o resto. So TEMATICA e rastejada."),
        "SEEDS_UNKNOWN_CAUSE": ("as 6 livres sao universidades (cnr, unimi, unipd, "
                                "unibo, unito) e ISTAT: nenhum dominio esta na lista "
                                "TEMATICA nem tem subdominio agri.; a regra decide "
                                "pelo host, nao pelo caminho — a pagina de departamento "
                                "agrario da unimi.it cai em UNKNOWN pelo host unimi.it"),
        "EM_ANALISE_POR_CLASSE": dict(collections.Counter(
            D._classificar_semente(c["URL"])[0] for c in em)),
        "SEGUNDA_GERACAO_REAL": novas,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    copia = Path(sys.argv[1])
    orig = (F.FILA, GD.CANDIDATAS)
    with tempfile.TemporaryDirectory(prefix="prova-abastecimento-") as td:
        tmp = Path(td)
        F.FILA = tmp / "fila.json"
        GD.CANDIDATAS = tmp / "cand.json"
        try:
            a = parte_a(copia, tmp)
            bs = parte_b_simulada(copia)
        finally:
            F.FILA, GD.CANDIDATAS = orig
    b = parte_b(copia)
    c = parte_c(copia)
    doc = {"DATASET": "ABASTECIMENTO-PROOF-V1",
           "GERADO_EM": _agora().isoformat(),
           "LEI": "repetir o que nada mudou nao e persistencia; um teto de "
                  "tentativas nao e uma sentenca; semente nova != regra nova",
           "FONTE_DA_COPIA": "worktree viva source-curator-service-v1, copiada "
                             "com cp para TEMP; nada escrito nela",
           "A_FEEDER": a, "B_FAILED": {**b, **bs}, "C_SEMENTES": c}
    SAIDA.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(json.dumps({"A": {k: v for k, v in a["DEPOIS_SIMULADO"].items() if k != "NOTA"},
                      "A_SO_FEEDER": a["DEPOIS_SIMULADO_SO_FEEDER"],
                      "A_ANTES": {k: v for k, v in a["ANTES_REAL"].items() if k not in ("HORAS_COM_200_OU_MAIS",)},
                      "B": {k: v for k, v in b["REAL"].items() if k != "FONTES"},
                      "B_SIM": bs["SIMULADO"],
                      "C": {"CATALOGO": c["CATALOGO_REAL"],
                            "NOVAS": [(s["URL"], s["ROBOTS_PERMITE_A_SEMENTE"])
                                      for s in c["SEGUNDA_GERACAO_REAL"]]}},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
