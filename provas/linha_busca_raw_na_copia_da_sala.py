#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ENSAIO · o repouso da LINHA-BUSCA numa COPIA da Sala (Postgres descartavel), sem tocar a Sala real.

    py provas/linha_busca_raw_na_copia_da_sala.py --saidas=<LOTE0-REAL;LOTE1-REAL> --trabalho=<pasta temp>

1. copia: `pg_dump` da Sala real (leitura; DSN do ficheiro, nunca impresso) -> cluster NOVO e temporario
   (initdb na pasta de trabalho, porto 54339, banco `descartavel`) -> restore;
2. corre `coleta/linha_busca_raw.repousar(..., pousar=True)` com BANCO_DESCARTAVEL_URL + SINTONIA_SALA_DSN a
   apontar para a COPIA;
3. le da copia: a corrida em collection_run, as observacoes em raw_asset, as linhas da Sala com
   raw_observation_id; e le da Sala REAL as mesmas contagens antes e depois (tem de ficar igual);
4. para o cluster temporario (desliga o que ligou). So com LOCK-PESADO livre e >= 5 GB (regra da casa).
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BIN = Path(os.path.expanduser("~/orca/pgtmp/pgsql/bin"))
DSN_REAL = open(os.path.expanduser("~/sintonia-sala-italia/SALA_DSN.txt"), encoding="utf-8").read().strip()
PORTO = 54339
URL = "postgresql://postgres@localhost:%d/descartavel" % PORTO


def psql(url, sql, ro=False):
    env = dict(os.environ, PGCLIENTENCODING="UTF8")
    if ro:
        env["PGOPTIONS"] = "-c default_transaction_read_only=on"
    r = subprocess.run([str(BIN / "psql.exe"), "-X", "-q", "-A", "-t", "-F", "|", "-v", "ON_ERROR_STOP=1",
                        "-d", url, "-c", sql], env=env, capture_output=True)
    if r.returncode:
        raise SystemExit("psql: " + r.stderr.decode("utf-8", "replace").replace(DSN_REAL, "<DSN>")[:400])
    return r.stdout.decode("utf-8").strip().replace("\r", "")


def contagens(url, ro):
    return {t: psql(url, "select count(*) from public.%s" % t, ro)
            for t in ("collection_run", "raw_asset", "storage_object", "sala_de_espera")}


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    trab = Path(arg["trabalho"])
    trab.mkdir(parents=True, exist_ok=True)
    dados, log, dump = trab / "cluster", trab / "postgres.log", trab / "sala.dump"
    real_antes = contagens(DSN_REAL, True)
    subprocess.run([str(BIN / "initdb.exe"), "-D", str(dados), "-U", "postgres", "-A", "trust", "-E", "UTF8"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    # pg_ctl com a saida para ficheiro (memoria: capture_output pendura, o postmaster herda os pipes)
    subprocess.run([str(BIN / "pg_ctl.exe"), "-D", str(dados), "-l", str(log), "-o", "-p %d" % PORTO, "-w", "start"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    out = {}
    try:
        subprocess.run([str(BIN / "createdb.exe"), "-h", "localhost", "-p", str(PORTO), "-U", "postgres", "descartavel"],
                       check=True)
        env = dict(os.environ, PGOPTIONS="-c default_transaction_read_only=on")
        subprocess.run([str(BIN / "pg_dump.exe"), "-Fc", "-f", str(dump), "-d", DSN_REAL], env=env, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        r = subprocess.run([str(BIN / "pg_restore.exe"), "--no-owner", "--no-privileges", "-d", URL, str(dump)],
                           capture_output=True)
        out["RESTORE_AVISOS"] = r.stderr.decode("utf-8", "replace")[-600:]
        copia_antes = contagens(URL, False)
        env = dict(os.environ, BANCO_DESCARTAVEL_URL=URL, SINTONIA_SALA_BACKEND="POSTGRES", SINTONIA_SALA_DSN=URL,
                   SINTONIA_PSQL_EXE=str(BIN / "psql.exe"), PYTHONUTF8="1")
        env.pop("SINTONIA_COLLECTION_DSN", None)
        env.pop("SUPABASE_DB_URL", None)
        corrida = "LINHA-BUSCA-RAW-ENSAIO-%s" % time.strftime("%Y%m%dT%H%M%S")
        r = subprocess.run([sys.executable, str(RAIZ / "coleta" / "linha_busca_raw.py"), "--repousar",
                            "--saidas=%s" % arg["saidas"], "--corrida=%s" % corrida, "--pousar"],
                           env=env, capture_output=True, text=True, cwd=str(RAIZ))
        out["REPOUSO_STDOUT"] = r.stdout[-3000:]
        out["REPOUSO_STDERR"] = r.stderr[-3000:]
        out["REPOUSO_RC"] = r.returncode
        copia_depois = contagens(URL, False)
        out["CORRIDA"] = corrida
        out["COLLECTION_RUN"] = psql(URL, "select run_id, platform, actor, status, item_count_raw from "
                                          "public.collection_run where run_id = '%s'" % corrida)
        out["RAW_DA_CORRIDA"] = psql(URL, "select count(*), count(distinct sha256), min(identity_state), "
                                          "max(identity_state) from public.raw_asset where run_id = '%s'" % corrida)
        out["SALA_DA_CORRIDA"] = psql(URL, "select count(*), count(raw_observation_id), count(distinct item_id) "
                                           "from public.sala_de_espera where run_id = '%s'" % corrida)
        out["SALA_LIGA_AO_RAW"] = psql(URL, "select count(*) from public.sala_de_espera s join public.raw_asset r "
                                            "on r.id = s.raw_observation_id and r.run_id = s.run_id "
                                            "where s.run_id = '%s'" % corrida)
        out["COPIA_ANTES"], out["COPIA_DEPOIS"] = copia_antes, copia_depois
    finally:
        subprocess.run([str(BIN / "pg_ctl.exe"), "-D", str(dados), "-m", "fast", "-w", "stop"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out["SALA_REAL_ANTES"], out["SALA_REAL_DEPOIS"] = real_antes, contagens(DSN_REAL, True)
    out["SALA_REAL_IGUAL"] = out["SALA_REAL_ANTES"] == out["SALA_REAL_DEPOIS"]
    (trab / "ENSAIO-LINHA-BUSCA-RAW.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                                     encoding="utf-8")
    print(json.dumps({k: out.get(k) for k in ("CORRIDA", "REPOUSO_RC", "COLLECTION_RUN", "RAW_DA_CORRIDA",
                                              "SALA_DA_CORRIDA", "SALA_LIGA_AO_RAW", "COPIA_ANTES", "COPIA_DEPOIS",
                                              "SALA_REAL_IGUAL")}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
