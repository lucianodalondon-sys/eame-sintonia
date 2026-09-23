#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G2 — gate PROVENANCE_COMPLETE medido nos documentos da micro (A2 e A4). So leitura.

Os 11 campos pedidos, cada um PRESENTE ou UNKNOWN explicito («NAO SEI»), nunca inferido:
SOURCE, RUN, OBSERVATION, CONTENT, STORAGE OBJECT, FACT_TIME, SOURCE_LOCATION,
FACT_LOCATION, PUBLICATION_TIME, OBSERVATION_TIME, COLLECTION_TIME.

Duas camadas, porque sao dois registos diferentes:
  SALA      as linhas de `sala_de_espera` (o que a Inteligencia le). A Sala da A2 so
            existe dentro do Postgres parado da corrida: COPIA-se a pasta `pg` para
            outro sitio, liga-se a copia numa porta livre, le-se, desliga-se. A prova
            original nao e tocada.
  COLETOR   `observations.ndjson` do coletor (A2 e A4): o registo por documento antes
            da porta. Aqui «ausente» (chave que nao existe) NAO e UNKNOWN explicito.

INFERIDO = um tempo igual a outro que ele nao e (fact_time == captured_at,
published_at == captured_at, observed_at == captured_at).

    py medidas/medir_proveniencia_g2.py --a2=<micro-ensaio-...> --a4=<micro-rede-real-...>
        --pgbin=<.../pgsql/bin> [--porta=54391] [--saida=curadoria/G2-PROVENIENCIA-V1.json]
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

NS = "NAO SEI"
SQL = """select s.item_id, s.source_id,
 (s.run_id is not null and exists(select 1 from collection_run r where r.run_id=s.run_id))::text,
 coalesce(s.raw_observation_id::text,''),
 (exists(select 1 from storage_object o join raw_asset a on a.storage_object_id=o.id
         where a.id=s.raw_observation_id))::text,
 coalesce(length(s.texto),0)::text, coalesce(s.fact_time,''), coalesce(s.source_location,''),
 coalesce(s.fact_location,''), coalesce(s.published_at,''), coalesce(s.observed_at,''),
 coalesce(s.captured_at,'')
from sala_de_espera s order by s.pousado_em, s.item_id"""
COLS = ["ITEM_ID", "SOURCE", "RUN", "OBSERVATION", "STORAGE_OBJECT", "CONTENT", "FACT_TIME",
        "SOURCE_LOCATION", "FACT_LOCATION", "PUBLICATION_TIME", "OBSERVATION_TIME", "COLLECTION_TIME"]
TEMPOS = ("FACT_TIME", "PUBLICATION_TIME", "OBSERVATION_TIME")


def classe(campo: str, v: str, linha: dict) -> str:
    if campo == "RUN" or campo == "STORAGE_OBJECT":
        return "PRESENTE" if v == "true" else "AUSENTE"
    if campo == "CONTENT":
        return "PRESENTE" if int(v or 0) > 0 else "AUSENTE"
    if v in ("", None):
        return "AUSENTE"
    if v.strip().upper() in (NS, "UNKNOWN", "NAO_SEI"):
        return "UNKNOWN_EXPLICITO"
    if campo in TEMPOS and v == linha["COLLECTION_TIME"]:
        return "INFERIDO"
    return "PRESENTE"


def ler_sala(pasta_pg: Path, pgbin: Path, porta: int) -> list[dict]:
    copia = Path(tempfile.mkdtemp(prefix="g2-pg-")) / "pg"
    shutil.copytree(pasta_pg, copia)
    (copia / "postmaster.pid").unlink(missing_ok=True)
    log = copia.parent / "pg.log"
    # sem capture_output: o postmaster herda os pipes e o start pendura
    subprocess.run([str(pgbin / "pg_ctl.exe"), "-D", str(copia), "-l", str(log), "-w", "-o",
                    "-p %d -c listen_addresses=localhost" % porta, "start"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    try:
        r = subprocess.run([str(pgbin / "psql.exe"), "-h", "localhost", "-p", str(porta), "-U", "postgres",
                            "-d", "sala_italia", "-At", "-F", "\t", "-c", SQL],
                           capture_output=True, text=True, encoding="utf-8")
        if r.returncode:
            raise SystemExit("psql: " + r.stderr)
        return [dict(zip(COLS, l.rstrip("\r").split("\t"))) for l in r.stdout.splitlines() if l.strip()]
    finally:
        subprocess.run([str(pgbin / "pg_ctl.exe"), "-D", str(copia), "stop", "-m", "fast"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        time.sleep(1)
        shutil.rmtree(copia.parent, ignore_errors=True)


def medir_sala(linhas: list[dict]) -> dict:
    por_campo = {c: Counter() for c in COLS[1:]}
    completas = 0
    for l in linhas:
        cls = {c: classe(c, l[c], l) for c in COLS[1:]}
        for c, k in cls.items():
            por_campo[c][k] += 1
        completas += all(k in ("PRESENTE", "UNKNOWN_EXPLICITO") for k in cls.values())
    return {"LINHAS": len(linhas), "FONTES": sorted({l["SOURCE"] for l in linhas}),
            "LINHAS_COMPLETAS": completas, "POR_CAMPO": {c: dict(v) for c, v in por_campo.items()}}


def medir_coletor(ndjson: Path) -> dict:
    L = [json.loads(x) for x in ndjson.read_text(encoding="utf-8").splitlines() if x.strip()]
    mapa = {"SOURCE": "SOURCE_ID", "RUN": "RUN_ID", "OBSERVATION": "DOCUMENT_VERSION_ID",
            "CONTENT": "RAW_SHA256", "STORAGE_OBJECT": "RAW_PATH", "FACT_TIME": "FACT_TIME",
            "SOURCE_LOCATION": "SOURCE_LOCATION", "FACT_LOCATION": "FACT_LOCATION",
            "PUBLICATION_TIME": "PUBLISHED_AT", "OBSERVATION_TIME": "OBSERVED_AT",
            "COLLECTION_TIME": "CAPTURED_AT"}
    out = {}
    for c, k in mapa.items():
        v = [l.get(k) for l in L]
        out[c] = {"CHAVE": k, "PRESENTE": sum(1 for x in v if x not in (None, "")),
                  "AUSENTE": sum(1 for x in v if x in (None, ""))}
    return {"REGISTOS": len(L), "POR_CAMPO": out,
            "CAMPOS_AUSENTES_EM_TODOS": sorted(c for c, x in out.items() if x["PRESENTE"] == 0)}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    a2, a4 = Path(arg["a2"]), Path(arg["a4"])
    obs = Path("ops/data/collection-ledger/italy/observations.ndjson")
    sala = medir_sala(ler_sala(a2 / "pg", Path(arg["pgbin"]), int(arg.get("porta", 54391))))
    r = {"DATASET": "G2-PROVENIENCIA-V1", "GATE": "PROVENANCE_COMPLETE",
         "A2": {"CORRIDA": a2.name, "SALA": sala, "COLETOR": medir_coletor(a2 / obs)},
         "A4": {"CORRIDA": a4.name, "SALA": "0 linhas (A4: SIM 0 -> Sala +0; know-how §198 em origin/micro-rede-real-v1)",
                "COLETOR": medir_coletor(a4 / obs)}}
    s = r["A2"]["SALA"]
    r["PROVENANCE_COMPLETE"] = ("YES" if s["LINHAS"] and s["LINHAS_COMPLETAS"] == s["LINHAS"] else "NO")
    print(json.dumps(r, ensure_ascii=False, indent=1))
    if "saida" in arg:
        Path(arg["saida"]).write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
