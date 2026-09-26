#!/usr/bin/env python3
"""ACERVO-PARA-SALA · o LOTE pelo reprocesso canonico — para o COORDENADOR correr no VIVO (D82).

    REPROCESSAR NAO E COLHER. Sem internet. Nenhum gate e relaxado: e a MESMA porta de sempre.

Corre, na arvore do vivo, as corridas da lista (`LOTE-260-CORRIDAS.json`, medidas no ensaio), uma a uma:

    italy_executor.colher(RUN_ID)                                  refaz o balcao a partir do LIVRO do vivo
    orquestrador <apelido> --so-a-porta --colheita-da-corrida=RUN_ID --filtro fonte= --filtro universo=

Quem escreve na Sala e `admissao/sala_de_espera.py`, SO depois de um SIM da Admissao.

    py reprocessar_lote.py --arvore <vivo> --lista LOTE-260-CORRIDAS.json            (so confere e mostra)
    py reprocessar_lote.py --arvore <vivo> --lista LOTE-260-CORRIDAS.json --aplicar  (corre)

Recusa-se a correr (--aplicar) se: a Sala nao for POSTGRES canonica; faltar a DSN; faltar o armazem; o robo
nao estiver parado (PARAR.flag ausente); ou a arvore nao for a do vivo (sem o livro). A rede fica fechada no
processo filho (proxy para uma porta morta).
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = None   # a arvore do VIVO, dada por --arvore (nunca a pasta onde este ficheiro esta)
APELIDO = {"T1": "cultura", "T2": "clima", "T3": "praga", "T4": "regulatorio", "T5": "ciencia",
           "T6": "pesquisador", "T7": "cooperativa", "T8": "agricultor", "T9": "concorrente",
           "T10": "mercado", "T11": "evento", "T12": "politica", "T13": "distribuicao"}
UMA = r'''
import os, sys, json
sys.path.insert(0, os.getcwd())
import _gavetas
from coleta import italy_executor as ix
b = ix.colher(sys.argv[1])
print("BALCAO", json.dumps({"OBS": b["OBSERVACOES_DESTA_CORRIDA"], "COM_BYTES": b["COM_BYTES_NO_ARMAZEM"]}))
import orquestrador as orq
sys.argv = ["orquestrador/orquestrador.py", sys.argv[2], "--so-a-porta", "--colheita-da-corrida=%s" % sys.argv[1],
            "--filtro", "fonte=%s" % sys.argv[3], "--filtro", "universo=%s" % sys.argv[4]]
try:
    rc = orq.main()
except SystemExit as e:
    rc = int(e.code or 0)
print("RC", rc)
'''


def dsn():
    d = os.environ.get("SINTONIA_SALA_DSN")
    if d:
        return d
    f = Path.home() / "sintonia-sala-italia" / "SALA_DSN.txt"
    return f.read_text(encoding="utf-8").strip() if f.exists() else ""


def contar(env):
    psql = env.get("SINTONIA_PSQL_EXE") or str(Path.home() / "orca" / "pgtmp" / "pgsql" / "bin" / "psql.exe")
    r = subprocess.run([psql, "-X", "-A", "-t", "-c", "select count(*) from sala_de_espera", env["SINTONIA_SALA_DSN"]],
                       capture_output=True, text=True, encoding="utf-8",
                       env={**env, "PGOPTIONS": "-c default_transaction_read_only=on"})
    return r.stdout.strip() if r.returncode == 0 else "ERRO: " + r.stderr.strip()[-120:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arvore", required=True, help="a arvore do VIVO (source-curator-service-v1)")
    ap.add_argument("--lista", required=True)
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--saida", default="RECIBO-LOTE-ACERVO.json")
    a = ap.parse_args()
    global RAIZ
    RAIZ = Path(a.arvore).resolve()
    lista = json.load(open(a.lista, encoding="utf-8"))["CORRIDAS"]
    env = {**os.environ, "SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_SALA_DSN": dsn(),
           "SINTONIA_COLLECTION_DSN": os.environ.get("SINTONIA_COLLECTION_DSN") or dsn(),
           "SINTONIA_ARMAZEM_RAIZ": os.environ.get("SINTONIA_ARMAZEM_RAIZ")
           or str(Path.home() / "sintonia-sala-italia" / "armazem"),
           "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1",
           "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9", "ALL_PROXY": "http://127.0.0.1:9"}
    env.pop("PGOPTIONS", None)
    falta = []
    if not env["SINTONIA_SALA_DSN"]:
        falta.append("SINTONIA_SALA_DSN (nem no ambiente nem em ~/sintonia-sala-italia/SALA_DSN.txt)")
    if not Path(env["SINTONIA_ARMAZEM_RAIZ"]).is_dir():
        falta.append("SINTONIA_ARMAZEM_RAIZ nao e uma pasta: %s" % env["SINTONIA_ARMAZEM_RAIZ"])
    if not (RAIZ / "data" / "collection-ledger" / "italy" / "observations.ndjson").exists():
        falta.append("esta arvore nao tem o livro do coletor (corra na arvore do VIVO)")
    if not (RAIZ / "PARAR.flag").exists():
        falta.append("PARAR.flag ausente na raiz do vivo: pare o robo antes (o reprocesso nao corre com o coletor vivo)")
    print("CORRIDAS NA LISTA: %d · SIM ESPERADOS NO ENSAIO: %s · SALA AGORA: %s"
          % (len(lista), json.load(open(a.lista, encoding="utf-8")).get("PREVISTO"), contar(env) if not falta[:1] else "?"))
    if falta:
        print("\nNAO PRONTO:\n  - " + "\n  - ".join(falta))
        if a.aplicar:
            return 2
    if not a.aplicar:
        print("\n(sem --aplicar: nada foi corrido)")
        return 0
    antes = contar(env)
    recibo = {"SALA_ANTES": antes, "CORRIDAS": []}
    for c in lista:
        t0 = time.time()
        x = subprocess.run([sys.executable, "-B", "-c", UMA, c["RUN_ID"], APELIDO[c["UNIVERSO"]], c["FONTE"], c["UNIVERSO"]],
                           cwd=str(RAIZ), env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=900)
        rc = next((l[3:] for l in x.stdout.splitlines() if l.startswith("RC ")), None)
        recibo["CORRIDAS"].append({**c, "RC": rc, "EXIT": x.returncode, "SEG": round(time.time() - t0, 1),
                                   "FIM": [l[:200] for l in x.stdout.strip().splitlines()[-6:]],
                                   "ERRO": (x.stderr.strip().splitlines() or [""])[-1][:240]})
        print("%-45s %s rc=%s exit=%s" % (c["RUN_ID"], c["UNIVERSO"], rc, x.returncode))
    recibo["SALA_DEPOIS"] = contar(env)
    with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(recibo, fh, ensure_ascii=False, indent=1)
    print("SALA %s -> %s · recibo %s" % (antes, recibo["SALA_DEPOIS"], a.saida))
    return 0


if __name__ == "__main__":
    sys.exit(main())
