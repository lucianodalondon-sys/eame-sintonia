#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPROC-SALA-PLANO — o ensaio do roteiro numa CÓPIA da Sala. Nunca a Sala.

Restaura um backup da Sala real (`pg_dump -Fc`, o de `backup_sala.cmd`) num Postgres DESCARTÁVEL
novo e corre contra ele, sem mudar uma linha, o MESMO roteiro que o coordenador corre na Sala:
`scripts/reproc_sala/reprocessar_sala.sh`. Desliga o Postgres e apaga a pasta no fim.

    py provas/reproc_sala_ensaio.py --dump <sala.dump> --saida <pasta>
"""
import argparse
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "ensaio_offline", RAIZ / "scripts" / "micro_coleta" / "ensaio_offline.py")
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    pasta = Path(tempfile.mkdtemp(prefix="reproc-sala-"))
    base = E.Base(pasta / "pg")
    assert ":54330/" not in base.url, "isto e a Sala real"
    env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", ""),
           "SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_SALA_DSN": base.url,
           "SINTONIA_PSQL_EXE": base.exe("psql"), "PYTHONUTF8": "1", "PY": sys.executable}
    for v in ("SINTONIA_COLLECTION_DSN", "SUPABASE_DB_URL", "BANCO_DESCARTAVEL_URL", "PGOPTIONS"):
        env.pop(v, None)
    print("DUMP %s sha256 %s" % (a.dump, hashlib.sha256(open(a.dump, "rb").read()).hexdigest()), flush=True)
    codigo = 1
    try:
        subprocess.run([base.exe("initdb"), "-D", str(base.pasta), "-U", "postgres",
                        "--auth=trust", "-E", "UTF8", "--no-sync"], check=True, capture_output=True)
        # sem capture_output: o postmaster herda os pipes e o run() pendura
        subprocess.run([base.exe("pg_ctl"), "-D", str(base.pasta), "-o",
                        f"-p {base.porto} -h 127.0.0.1", "-l", str(base.pasta / "servidor.log"),
                        "-w", "start"], check=True, stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([base.exe("psql"), "-X", "-q", "-c", "create database sala_italia;",
                        f"postgresql://postgres@127.0.0.1:{base.porto}/postgres"],
                       check=True, capture_output=True)
        r = subprocess.run([base.exe("pg_restore"), "--no-owner", "--no-privileges",
                            "-d", base.url, a.dump], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        print("RESTAURO codigo=%d %s" % (r.returncode, r.stderr[-300:].strip()), flush=True)
        r = subprocess.run([shutil.which("bash") or "bash", "scripts/reproc_sala/reprocessar_sala.sh",
                            str(saida)], cwd=str(RAIZ), env=env, text=True, encoding="utf-8",
                           errors="replace")
        codigo = r.returncode
    finally:
        base.descer()
        shutil.rmtree(pasta, ignore_errors=True)
        print("POSTGRES_DESCARTAVEL=DESLIGADO", flush=True)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
