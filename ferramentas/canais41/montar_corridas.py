# -*- coding: utf-8 -*-
"""CANAIS-41 · monta o `--corridas` da regua social a partir das corridas feitas.

    py ferramentas/canais41/montar_corridas.py --rodada R.tsv --envelopes DIR
        [--dsn-ficheiro C:/Users/London1/sintonia-sala-italia/SALA_DSN.txt] --saida CORRIDAS.json

`R.tsv`: uma linha por corrida, `SOURCE_ID<TAB>RUN_ID` (o RUN_ID e o que o orquestrador
imprimiu no log do job). Para cada corrida:
  * confere que `DIR/<RUN_ID>/ENVELOPE.json` existe e e da fonte e da fase `canal-youtube`;
  * conta as linhas RAW dessa corrida no banco (`public.raw_asset where run_id = ...`),
    SO LEITURA (`default_transaction_read_only=on`), com o DSN lido de um ficheiro e
    nunca impresso. Sem `--dsn-ficheiro`, RAW fica NAO_SEI (a regua reprova: visto != guardado).

Nao escreve em livro nenhum. A regua e quem julga (`curadoria/regua_social.py`).
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PSQL = Path.home() / "orca" / "pgtmp" / "pgsql" / "bin" / "psql.exe"
RE_RUN = re.compile(r"^[A-Za-z0-9._-]{6,120}$")


def raw_da_corrida(dsn: str, run_id: str) -> list:
    if not RE_RUN.match(run_id):
        raise ValueError("RUN_ID com forma estranha: %r" % run_id)
    env = dict(os.environ, PGOPTIONS="-c default_transaction_read_only=on")
    # opcoes ANTES do DSN (psql no Windows nao permuta opcoes)
    r = subprocess.run([str(PSQL), "-X", "-A", "-t", "-F", "|", "-v", "ON_ERROR_STOP=1", "-f", "-", dsn],
                       input="select id, media_type, bytes from public.raw_asset where run_id = '%s' order by id;"
                             % run_id, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=env, timeout=120)
    if r.returncode:
        raise RuntimeError("psql falhou (rc %d): %s" % (r.returncode, r.stderr.replace(dsn, "<DSN>")[-200:]))
    return [l.split("|") for l in r.stdout.replace("\r", "").splitlines() if l.strip()]


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    dsn = Path(arg["dsn-ficheiro"]).read_text(encoding="utf-8").strip() if "dsn-ficheiro" in arg else None
    env_dir = Path(arg["envelopes"])
    out, problemas = {}, []
    for n, linha in enumerate(Path(arg["rodada"]).read_text(encoding="utf-8").splitlines(), 1):
        if not linha.strip() or linha.startswith("#"):
            continue
        sid, run_id = [x.strip() for x in linha.split("\t")[:2]]
        p = env_dir / run_id / "ENVELOPE.json"
        if not p.exists():
            problemas.append("%s: sem envelope em %s" % (sid, p))
            continue
        e = json.loads(p.read_text(encoding="utf-8"))
        if e.get("SOURCE_ID_DO_PEDIDO") != sid or e.get("FASE") != "canal-youtube":
            problemas.append("%s: o envelope %s e de %s/%s" % (sid, run_id, e.get("SOURCE_ID_DO_PEDIDO"), e.get("FASE")))
            continue
        x = {"SOURCE_ID": sid, "FASE": e.get("FASE"), "RUN_ID": run_id}
        if dsn:
            x["MEDIDA"] = {"RAW": raw_da_corrida(dsn, run_id)}
        else:
            x["MEDIDA"] = "NAO_SEI: sem --dsn-ficheiro, RAW nao foi contado"
        out["%s|%s" % (sid, run_id)] = x
    Path(arg["saida"]).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("CORRIDAS=%d PROBLEMAS=%d -> %s" % (len(out), len(problemas), arg["saida"]))
    for pr in problemas:
        print("PROBLEMA", pr)
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
