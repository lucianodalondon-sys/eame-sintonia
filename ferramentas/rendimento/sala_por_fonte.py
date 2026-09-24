# -*- coding: utf-8 -*-
"""REND · o historico de cada fonte na Sala, SO LEITURA.

Tres contagens por SOURCE_ID, todas da memoria canonica (Postgres da Sala):
  RAW       raw_asset            documentos que alguma vez se guardaram
  DERIVED   documento_estruturado textos tirados desses documentos
  SIM       sala_de_espera       o que a Admissao deixou entrar
e a lista de SOURCE_URL ja guardados (para separar «novo para o coletor» de
«novo para o acervo»).

A transaccao e read-only por PGOPTIONS; opcoes do psql ANTES da DSN (no
Windows o psql deixa de ler opcoes depois do primeiro posicional).

Uso: py ferramentas/rendimento/sala_por_fonte.py --saida C:/rend/sala.json
Variaveis: SINTONIA_SALA_DSN (ou ~/sintonia-sala-italia/SALA_DSN.txt),
           SINTONIA_PSQL_EXE.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def dsn():
    v = os.environ.get("SINTONIA_SALA_DSN")
    if v:
        return v
    return (Path.home() / "sintonia-sala-italia" / "SALA_DSN.txt").read_text(encoding="utf-8").strip()


def psql(sql):
    exe = os.environ.get("SINTONIA_PSQL_EXE", r"C:\Users\London1\orca\pgtmp\pgsql\bin\psql.exe")
    env = dict(os.environ, PGOPTIONS="-c default_transaction_read_only=on")
    r = subprocess.run([exe, "-X", "-q", "-A", "-t", "-F", "\x1e", "-c", sql, dsn()],
                       capture_output=True, env=env, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise SystemExit("psql falhou: %s" % r.stderr.decode("utf-8", "replace")[:300])
    # \r do psql no Windows: tirar antes de partir (ver know-how do censo)
    linhas = r.stdout.decode("utf-8").replace("\r", "").split("\n")
    return [l.split("\x1e") for l in linhas if l]


def main(argv):
    saida = Path(argv[argv.index("--saida") + 1])
    por = {}

    def f(s):
        return por.setdefault(s, {"RAW": 0, "DERIVED": 0, "SIM": 0, "SIM_ULTIMO": None, "URLS": []})

    for s, n in psql("select source_id, count(*) from raw_asset where source_id is not null group by 1"):
        f(s)["RAW"] = int(n)
    for s, n in psql("select source_id, count(*) from documento_estruturado where source_id is not null group by 1"):
        f(s)["DERIVED"] = int(n)
    for s, n, u in psql("select source_id, count(*), max(pousado_em)::date::text from sala_de_espera group by 1"):
        f(s)["SIM"] = int(n)
        f(s)["SIM_ULTIMO"] = u
    for s, u in psql("select distinct source_id, source_url from raw_asset where source_id is not null and source_url is not null"):
        f(s)["URLS"].append(u)
    tot = psql("select (select count(*) from raw_asset), (select count(*) from documento_estruturado), (select count(*) from sala_de_espera)")[0]
    d = {"DATASET": "REND-SALA-POR-FONTE-V1",
         "MEDIDO_EM": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "MODO": "so leitura (default_transaction_read_only=on)",
         "TOTAIS": {"RAW": int(tot[0]), "DERIVED": int(tot[1]), "SIM": int(tot[2])},
         "POR_FONTE": por}
    saida.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("SALA", d["TOTAIS"], "fontes:", len(por))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
