# -*- coding: utf-8 -*-
"""MATERIA-PRIMA-POR-DIA — o painel da metrica do dono (D124, item 4). SO LEITURA, SEM REDE.

    py medidas/materia_prima_por_dia.py [--corridas=<runs.ndjson>] [--estados=<pasta das ondas>]
                                        [--cortesia=<LIVRO-CORTESIA.ndjson>] [--saida=<MATERIA-PRIMA-POR-DIA.json>]

D124: «precisamos de muita materia prima». A pergunta deixa de ser «quantos pedidos gastamos» e passa a
ser «quanta materia-prima nova entrou por dia, por linha». Tres fontes, cada uma com a sua pergunta, e
NENHUMA inventa a outra:

  DOCUMENTOS NOVOS   o livro de corridas (`data/collection-ledger/italy/runs.ndjson`): `contadores.NEW_DOCUMENTS`
                     de cada corrida, pelo dia UTC de FINISHED_AT; a linha e `LINHA` (senao `FASE` do Scrap,
                     senao SITES — o coletor web).
  ITENS NA SALA      os estados das ondas (`**/ONDA-WEB-ESTADO.json` = SITES, `**/MAESTRO-SOCIAL-ESTADO.json`
                     = SOCIAL): SALA_DEPOIS - SALA_ANTES de cada fonte, por tabela, pelo dia do RUN_ID.
                     Sem estados: NAO SEI (nunca zero).
  PEDIDOS            o livro da cortesia adaptativa (RESERVA por dia e linha). Sem livro: os pedidos do
                     proprio livro de corridas (INDEX_REQUESTS + DETAIL_REQUESTS), dito como tal.

    MEDIR NAO E FILTRAR: este painel nao barra nada, conta. AUSENCIA DE MEDIDA = NAO SEI.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
NAO_SEI = "NAO SEI"
RE_RUN_QUANDO = re.compile(r"-(\d{4})-(\d{2})-(\d{2})-\d{6}-[0-9a-f]{16}")


def _dia_iso(texto):
    try:
        return datetime.fromisoformat(str(texto).replace("Z", "+00:00")).astimezone(timezone.utc).date().isoformat()
    except ValueError:
        return None


def _linha_da_corrida(d: dict) -> str:
    return d.get("LINHA") or ("SCRAP:%s" % d["FASE"] if d.get("FASE") else "SITES")


def documentos_por_dia(linhas) -> tuple:
    """({(dia, linha): {DOCUMENTOS_NOVOS, CORRIDAS, PEDIDOS_DO_LIVRO_DE_CORRIDAS}}, corridas ilegiveis)."""
    out, ilegiveis = {}, 0
    for l in linhas:
        if not l.strip():
            continue
        try:
            d = json.loads(l)
        except ValueError:
            ilegiveis += 1
            continue
        c = d.get("contadores") or {}
        dia = _dia_iso(d.get("FINISHED_AT") or d.get("STARTED_AT") or "")
        if not dia or "NEW_DOCUMENTS" not in c:
            ilegiveis += 1
            continue
        k = out.setdefault((dia, _linha_da_corrida(d)), {"DOCUMENTOS_NOVOS": 0, "CORRIDAS": 0,
                                                         "PEDIDOS_DO_LIVRO_DE_CORRIDAS": 0})
        k["DOCUMENTOS_NOVOS"] += int(c.get("NEW_DOCUMENTS") or 0)
        k["CORRIDAS"] += 1
        if "INDEX_REQUESTS" in c or "DETAIL_REQUESTS" in c:
            k["PEDIDOS_DO_LIVRO_DE_CORRIDAS"] += int(c.get("INDEX_REQUESTS") or 0) + int(c.get("DETAIL_REQUESTS") or 0)
        else:
            k["CORRIDAS_SEM_CONTAGEM_DE_PEDIDOS"] = k.get("CORRIDAS_SEM_CONTAGEM_DE_PEDIDOS", 0) + 1
    return out, ilegiveis


def sala_por_dia(pasta: Path) -> dict:
    """{(dia, linha): {tabela: itens novos}} a partir dos estados das ondas."""
    out = {}
    for nome, linha in (("ONDA-WEB-ESTADO.json", "SITES"), ("MAESTRO-SOCIAL-ESTADO.json", "SOCIAL")):
        for f in sorted(Path(pasta).glob("**/" + nome)):
            try:
                est = json.loads(f.read_text(encoding="utf-8"))
            except ValueError:
                continue
            for fo in est.get("FONTES", []):
                m = RE_RUN_QUANDO.search(fo.get("RUN_ID") or "")
                a, b = fo.get("SALA_ANTES"), fo.get("SALA_DEPOIS")
                if not m or not isinstance(a, dict) or not isinstance(b, dict):
                    continue
                dia = "%s-%s-%s" % m.groups()
                k = out.setdefault((dia, linha), {})
                for t in set(a) | set(b):
                    if isinstance(a.get(t), int) and isinstance(b.get(t), int):
                        k[t] = k.get(t, 0) + max(0, b[t] - a[t])
    return out


def pedidos_por_dia(eventos: list) -> dict:
    out = {}
    for e in eventos:
        if e.get("TIPO") != "RESERVA":
            continue
        dia = datetime.fromtimestamp(float(e["EM"]), tz=timezone.utc).date().isoformat()
        k = (dia, e.get("LINHA") or NAO_SEI)
        out[k] = out.get(k, 0) + 1
    return out


def painel(corridas: Path | None, estados: Path | None, cortesia: Path | None) -> dict:
    docs, ilegiveis = ({}, 0)
    if corridas and corridas.exists():
        docs, ilegiveis = documentos_por_dia(corridas.read_text(encoding="utf-8").splitlines())
    sala = sala_por_dia(estados) if estados else None
    ped, ped_vem = None, "livro de corridas (INDEX_REQUESTS + DETAIL_REQUESTS)"
    if cortesia and cortesia.exists():
        sys.path.insert(0, str(RAIZ / "coleta"))
        import cortesia_adaptativa as CA                           # noqa: PLC0415 — so para LER o livro
        ped, ped_vem = pedidos_por_dia(CA.ler_eventos(cortesia)), "livro da cortesia adaptativa (RESERVA)"
    chaves = sorted(set(docs) | set(sala or {}) | set(ped or {}))
    dias = []
    for dia, linha in chaves:
        d = docs.get((dia, linha))
        p = (ped or {}).get((dia, linha)) if ped is not None else (
            None if not d or d.get("CORRIDAS_SEM_CONTAGEM_DE_PEDIDOS") else d["PEDIDOS_DO_LIVRO_DE_CORRIDAS"])
        s = None if sala is None else sala.get((dia, linha))
        n = d["DOCUMENTOS_NOVOS"] if d else NAO_SEI
        dias.append({"DIA": dia, "LINHA": linha, "DOCUMENTOS_NOVOS": n, "CORRIDAS": d["CORRIDAS"] if d else 0,
                     "PEDIDOS": p if p is not None else NAO_SEI,
                     "DOC_POR_PEDIDO": round(n / p, 3) if isinstance(n, int) and isinstance(p, int) and p else NAO_SEI,
                     "ITENS_NOVOS_NA_SALA": NAO_SEI if s is None else sum(s.values()),
                     "ITENS_NOVOS_NA_SALA_POR_TABELA": s if s is not None else NAO_SEI})
    return {"DATASET": "MATERIA-PRIMA-POR-DIA", "DECISAO": "D124 item 4",
            "GERADO_EM": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "FONTES": {"DOCUMENTOS": str(corridas) if corridas else NAO_SEI,
                       "SALA": str(estados) if estados else NAO_SEI + " (sem --estados)",
                       "PEDIDOS": ped_vem}, "CORRIDAS_ILEGIVEIS": ilegiveis, "DIAS": dias}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    ops = Path(os.environ.get("ITALY_OPS_ROOT") or RAIZ)
    corridas = Path(a.get("corridas") or ops / "data" / "collection-ledger" / "italy" / "runs.ndjson")
    cort = a.get("cortesia") or os.environ.get("SINTONIA_CORTESIA_LIVRO")
    r = painel(corridas, Path(a["estados"]) if a.get("estados") else None, Path(cort) if cort else None)
    if a.get("saida"):
        Path(a["saida"]).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print("MATERIA-PRIMA-POR-DIA  (documentos: %s · sala: %s · pedidos: %s)"
          % (r["FONTES"]["DOCUMENTOS"], r["FONTES"]["SALA"], r["FONTES"]["PEDIDOS"]))
    print("%-10s  %-16s %10s %8s %8s %9s %10s" % ("DIA", "LINHA", "DOC NOVOS", "CORRIDAS", "PEDIDOS", "DOC/PED", "SALA NOVOS"))
    for d in r["DIAS"]:
        print("%-10s  %-16s %10s %8s %8s %9s %10s" % (d["DIA"], d["LINHA"][:16], d["DOCUMENTOS_NOVOS"], d["CORRIDAS"],
                                                      d["PEDIDOS"], d["DOC_POR_PEDIDO"], d["ITENS_NOVOS_NA_SALA"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
