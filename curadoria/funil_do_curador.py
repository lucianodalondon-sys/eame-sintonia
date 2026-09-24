#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O FUNIL DO CURADOR — o dono ve que a fonte anda (CUR-PRONTA, D28, 24/09/2026).

    CANDIDATA -> QUALIFICADA -> CONTRATO -> ROTA -> CANARIO -> READY -> ELEGIVEL

So LE (livro de estados, fila, candidatas, contratos, alocacao, tabela do
coletor, portao). Nao escreve nada, nao vai a rede. Serve duas perguntas:

  1. QUANTAS fontes estao em cada degrau, web e social separadas, e ha QUANTO
     TEMPO estao paradas (dias desde a ultima transicao no livro).
  2. PARA CADA ESTADO QUE NAO E FIM: que tarefa o avanca, quem a enfileira, se
     esse alguem corre SOZINHO no ciclo vivo — ou se e um BURACO com nome.

A tabela `MAQUINA` e declarada, e os testes conferem-na contra o codigo: todo
o estado de `lifecycle.ESTADOS` tem linha; todo o enfileirador declarado existe;
e o que se diz AUTOMATICO e chamado a partir de `gatilho_discovery.talvez_alimentar`
ou do `worker`. Um estado novo sem linha reprova — um estado sem dono e o
«procurando procurando e depois ela para» do dono.

    python curadoria/funil_do_curador.py            # tabela para gente
    python curadoria/funil_do_curador.py --json     # o mesmo, para maquina
"""
from __future__ import annotations

import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F          # noqa: E402
import lifecycle as LC    # noqa: E402

CONTRATO = "FUNIL_DO_CURADOR/v1"

# ESTADO -> (tarefa que o avanca, quem a enfileira [modulo:funcao], AUTOMATICO?, nota)
# AUTOMATICO = o enfileirador corre sozinho no ciclo vivo (gatilho ou worker).
# «—» na tarefa = estado de fim ou parado por desenho (sai por decisao/capacidade).
MAQUINA = {
    LC.DISCOVERED: ("QUALIFY", "ponte_candidatas:processar", True,
                    "candidata nova: a ponte leva-a a QUALIFY (so uma vez por candidata)"),
    LC.QUALIFYING: ("QUALIFY", "ponte_candidatas:processar", True,
                    "estado de passagem: a QUALIFY aloca SOURCE_ID ou bloqueia com motivo"),
    LC.CONTRACT_PENDING: ("BUILD_CONTRACT", "avancar_fontes:avancar", True,
                          "o worker enfileira-a apos a QUALIFY; sem tarefa, o AVANCAR repoe"),
    LC.CANARY_PENDING: ("VALIDATE_ROUTE/CANARY", "gatilho_discovery:reparar_encalhadas", True,
                        "a cadeia do worker enfileira; ORFAS sem tarefa: REPARAR da R1 (nivel 0c)"),
    LC.RETRY_AFTER: ("VALIDATE_ROUTE", "avancar_fontes:avancar", True,
                     "a tarefa volta pelo relogio da fila; sem tarefa ha > 24 h, o AVANCAR repoe"),
    LC.READY_FOR_COLLECTION: ("VALIDATE_ROUTE", "avancar_fontes:avancar", True,
                              "LEGACY: AVANCAR re-mede (HTML) ou importa o contrato do coletor; "
                              "CURRENT elegivel: REVALIDAR (B3) com prova > 7 dias; "
                              "YouTube pelo feed: rota do Scrap (buraco social)"),
    LC.DEGRADED: ("REPAIR/BUILD_CONTRACT", "avancar_fontes:avancar", True,
                  "com contrato do robo: REPAIR; so na tabela do coletor: importar e re-medir"),
    LC.REPAIRING: ("REPAIR", "avancar_fontes:avancar", True, "como DEGRADED"),
    LC.CONTRACTED_CANARY_FAILED: ("REPAIR_CONTRACT", "gatilho_discovery:reparar_encalhadas", True,
                                  "dono R1 (reparo-fontes-v2, junta neste ramo): reparo "
                                  "deterministico do padrao, UM por fonte; o que ele recusa fica aqui"),
    LC.SEMANTIC_REVIEW: ("—", "canal_da_decisao_semantica (humano/Opus)", False,
                         "decisao com prova no DECISOES-SEMANTICAS; a QUALIFY le-a; nao e maquina"),
    LC.UNKNOWN: ("—", "NINGUEM", False, "BURACO: estado sem tarefa que o avance"),
    LC.RECONCILIATION_REQUIRED: ("—", "NINGUEM", False,
                                 "BURACO por desenho do alimentar_fila (adaptador noutra arvore)"),
    LC.POLICY_BLOCK: ("—", "decisao do dono (D15/D22/D23/D24)", False, "PARADO por desenho"),
    LC.AUTH_BLOCK: ("—", "decisao do dono", False, "PARADO por desenho"),
    LC.CAPABILITY_BLOCK: ("—", "capacidade nova (SCRAP ENGINEER)", False, "PARADO por desenho"),
    LC.CONTRACT_READY_ROUTE_BLOCKED: ("—", "rota nova (robots)", False, "PARADO por desenho"),
}

SOCIAL_TIPOS = frozenset({"YOUTUBE", "LINKEDIN", "INSTAGRAM", "FACEBOOK", "TIKTOK",
                          "TELEGRAM", "X", "TWITTER"})
SOCIAL_ESTRATEGIAS = frozenset({"YOUTUBE_CHANNEL_FEED", "SCRAP_FASE"})

_ABERTAS = frozenset({F.PENDING, F.IN_PROGRESS, F.WAITING_RETRY})


def _json(p: Path, chave: str, padrao):
    if not p.exists():
        return padrao
    return json.loads(p.read_text(encoding="utf-8")).get(chave, padrao)


def _dias(agora: datetime, s: str | None) -> float | None:
    if not s:
        return None
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    d = d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    return round((agora - d).total_seconds() / 86400, 2)


def medir(agora: datetime | None = None, *, com_portao: bool = True) -> dict:
    agora = agora or datetime.now(timezone.utc)
    livro = LC._ler_bruto()
    ultima = {}
    for t in livro["TRANSICOES"]:
        ultima[t["SOURCE_ID"]] = t
    estados = {s: t["NEW_STATE"] for s, t in ultima.items()}
    tarefas = F._ler()["TAREFAS"]
    abertas = {}
    for t in tarefas:
        if t["STATUS"] in _ABERTAS:
            abertas.setdefault(t["SOURCE_ID"], []).append(t["TASK_TYPE"])
    contratos = {c["SOURCE_ID"]: c for c in
                 _json(RAIZ / "curadoria" / "italy_contracts_curator.json", "FONTES", [])}
    alloc = {n["SOURCE_ID"]: n for n in
             _json(RAIZ / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json", "NOVAS", [])}
    tabela = {x["SOURCE_ID"] for x in
              _json(RAIZ / "regras" / "italy_contracts_onboarded.json", "FONTES", [])}
    candidatas = _json(RAIZ / "candidatas" / "FONTES-CANDIDATAS.json", "CANDIDATAS", [])

    def social(sid: str) -> bool:
        estr = ((contratos.get(sid) or {}).get("ACQUISITION") or {}).get("STRATEGY")
        if estr in SOCIAL_ESTRATEGIAS:
            return True
        return (alloc.get(sid) or {}).get("FAMILY") == "YOUTUBE"

    # ── os estados, com o tempo parado e quem os move ─────────────────────
    por_estado = {}
    for sid, e in estados.items():
        lado = "SOCIAL" if social(sid) else "WEB"
        p = por_estado.setdefault(e, {"N": 0, "WEB": 0, "SOCIAL": 0,
                                      "COM_TAREFA_ABERTA": 0, "_dias": []})
        p["N"] += 1
        p[lado] += 1
        if sid in abertas:
            p["COM_TAREFA_ABERTA"] += 1
        d = _dias(agora, ultima[sid].get("OBSERVED_AT"))
        if d is not None:
            p["_dias"].append(d)
    maquina = []
    for e in sorted(por_estado, key=lambda x: -por_estado[x]["N"]):
        p = por_estado[e]
        ds = sorted(p.pop("_dias"))
        tarefa, quem, auto, nota = MAQUINA.get(e, ("?", "NINGUEM", False, "ESTADO SEM LINHA"))
        maquina.append({"ESTADO": e, **p,
                        "SEM_TAREFA": p["N"] - p["COM_TAREFA_ABERTA"],
                        "DIAS_PARADO_MEDIANA": statistics.median(ds) if ds else None,
                        "DIAS_PARADO_MAX": ds[-1] if ds else None,
                        "TAREFA_QUE_AVANCA": tarefa, "QUEM_ENFILEIRA": quem,
                        "AUTOMATICO_NO_CICLO": auto, "NOTA": nota})

    # ── o funil ────────────────────────────────────────────────────────────
    # ⚠️ A QUALIFY aloca o SOURCE_ID no registo de alocacao (CANDIDATE_ID ->
    # SOURCE_ID) e NAO o escreve de volta na ficha da porta das candidatas
    # (medido na copia, 24/09: 30 QUALIFY OK, 0 fichas com SOURCE_ID). Contar so
    # pela ficha diria «sem numero» a quem ja tem. Conta-se pelos dois.
    com_numero = {n.get("CANDIDATE_ID") for n in alloc.values() if n.get("CANDIDATE_ID")}
    sem_sid = [c for c in candidatas if not c.get("SOURCE_ID")
               and c["CANDIDATA_ID"] not in com_numero
               and c.get("ESTADO") not in ("RECUSADA", "PROMOVIDA")]
    funil = {"WEB": {}, "SOCIAL": {}}
    for lado in funil:
        funil[lado]["CANDIDATAS_SEM_SOURCE_ID"] = sum(
            1 for c in sem_sid if (c.get("TIPO") in SOCIAL_TIPOS) == (lado == "SOCIAL"))
    for sid, e in estados.items():
        f = funil["SOCIAL" if social(sid) else "WEB"]
        f["QUALIFICADAS"] = f.get("QUALIFICADAS", 0) + 1
        tem_contrato = sid in contratos or sid in tabela
        if tem_contrato:
            f["COM_CONTRATO"] = f.get("COM_CONTRATO", 0) + 1
        if e in (LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, LC.CONTRACTED_CANARY_FAILED,
                 LC.RETRY_AFTER, LC.DEGRADED, LC.REPAIRING):
            f["ROTA_EM_PROVA_OU_PROVADA"] = f.get("ROTA_EM_PROVA_OU_PROVADA", 0) + 1
        if e == LC.READY_FOR_COLLECTION:
            f["READY"] = f.get("READY", 0) + 1

    out = {"DATASET": "FUNIL-DO-CURADOR", "CONTRATO": CONTRATO,
           "MEDIDO_EM": agora.isoformat(), "FONTES_NO_LIVRO": len(estados),
           "COM_TAREFA_ABERTA": sum(1 for s in estados if s in abertas),
           "TAREFAS_ABERTAS": sum(len(v) for v in abertas.values()),
           "FUNIL": funil, "MAQUINA": maquina}

    if com_portao:
        import collection_gate as CG   # noqa: E402
        ctx = CG._contexto()
        inv = CG.inventario(ctx=ctx)
        ready = [l for l in inv if l["STATE"] == LC.READY_FOR_COLLECTION]
        for lado in funil:
            rs = [l for l in ready if social(l["SOURCE_ID"]) == (lado == "SOCIAL")]
            funil[lado]["READY_CURRENT"] = sum(1 for l in rs if l["READY_RULE"] != "LEGACY")
            funil[lado]["READY_LEGACY"] = sum(1 for l in rs if l["READY_RULE"] == "LEGACY")
            funil[lado]["ELEGIVEIS_NO_PORTAO"] = sum(1 for l in rs if l["COLLECTION_ELIGIBLE"])
        import avancar_fontes as AV   # noqa: E402
        cands = AV.candidatas_a_avancar(agora)
        por = {}
        for c in cands:
            por[c["REGRA"]] = por.get(c["REGRA"], 0) + 1
        out["AVANCO_ELEGIVEL"] = {"TOTAL": len(cands), "POR_REGRA": por}
    return out


def _tabela(m: dict) -> str:
    L = ["FUNIL DO CURADOR · %s · %d fontes no livro · %d com tarefa aberta"
         % (m["MEDIDO_EM"][:16], m["FONTES_NO_LIVRO"], m["COM_TAREFA_ABERTA"]), ""]
    for lado, f in m["FUNIL"].items():
        L.append("%-6s " % lado + " -> ".join("%s %s" % (k, v) for k, v in f.items()))
    L.append("")
    L.append("%-28s %5s %4s %4s %6s %6s %-22s %-5s %s" % (
        "ESTADO", "N", "WEB", "SOC", "S/TAR", "DIAS", "TAREFA", "AUTO", "QUEM"))
    for x in m["MAQUINA"]:
        L.append("%-28s %5d %4d %4d %6d %6s %-22s %-5s %s" % (
            x["ESTADO"], x["N"], x["WEB"], x["SOCIAL"], x["SEM_TAREFA"],
            x["DIAS_PARADO_MEDIANA"], x["TAREFA_QUE_AVANCA"][:22],
            "SIM" if x["AUTOMATICO_NO_CICLO"] else "NAO", x["QUEM_ENFILEIRA"]))
    if "AVANCO_ELEGIVEL" in m:
        L.append("")
        L.append("AVANCO ELEGIVEL = %d %s" % (m["AVANCO_ELEGIVEL"]["TOTAL"],
                                              json.dumps(m["AVANCO_ELEGIVEL"]["POR_REGRA"])))
    return "\n".join(L)


if __name__ == "__main__":
    m = medir()
    if "--json" in sys.argv:
        print(json.dumps(m, ensure_ascii=False, indent=1))
    else:
        print(_tabela(m))
