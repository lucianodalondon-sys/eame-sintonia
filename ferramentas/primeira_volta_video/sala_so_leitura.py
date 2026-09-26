# -*- coding: utf-8 -*-
"""PRIMEIRA-VOLTA-VIDEO · consulta a Sala real SO LEITURA (default_transaction_read_only=on).

O DSN le-se de um ficheiro e nunca se imprime (nem em erro). Opcoes do psql ANTES do DSN
(o psql do Windows nao permuta opcoes).
"""
import os
import subprocess
from pathlib import Path

PSQL = Path.home() / "orca" / "pgtmp" / "pgsql" / "bin" / "psql.exe"
DSN_FICHEIRO = Path.home() / "sintonia-sala-italia" / "SALA_DSN.txt"


def consultar(sql: str, dsn_ficheiro: Path = DSN_FICHEIRO) -> list[list[str]]:
    dsn = dsn_ficheiro.read_text(encoding="utf-8").strip()
    env = dict(os.environ, PGOPTIONS="-c default_transaction_read_only=on")
    r = subprocess.run([str(PSQL), "-X", "-A", "-t", "-F", "\x1f", "-v", "ON_ERROR_STOP=1", "-f", "-", dsn],
                       input=sql, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=env, timeout=300)
    if r.returncode:
        raise RuntimeError("psql rc %d: %s" % (r.returncode, r.stderr.replace(dsn, "<DSN>")[-300:]))
    # \x1f separa campos; o \r do psql no Windows sai aqui (psql traz \r)
    return [l.split("\x1f") for l in r.stdout.replace("\r", "").split("\n") if l != ""]
