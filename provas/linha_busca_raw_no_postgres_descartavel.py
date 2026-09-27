#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LOTE5-INTEGRA · a linha-busca num Postgres DESCARTAVEL criado do zero (sem copia de Sala real).

    python3 provas/linha_busca_raw_no_postgres_descartavel.py <pasta de trabalho> [saida.json]

Diferente de `provas/linha_busca_raw_na_copia_da_sala.py` (que copia a Sala real por pg_dump), esta prova
nao le banco nenhum de fora:
1. `initdb` NOVO na pasta de trabalho, porto livre, socket ao lado dos dados, banco `descartavel`
   (initdb recusa root: como root, o cluster corre como o utilizador `postgres` via `runuser`);
2. schema pelas migrations DO REPO, pela cadeia canonica (`motor/cadeia_canonica.sh migrations`);
3. dados SINTETICOS: a fixture `ferramentas/linha_busca/fixtures/teste` (paginas marcadas sinteticas)
   colhida por `linha_busca.colher` com transporte FALSO (nenhum pedido a rede);
4. `coleta/linha_busca_raw.py --repousar --pousar` DUAS vezes na mesma corrida, com
   BANCO_DESCARTAVEL_URL + SINTONIA_SALA_BACKEND=POSTGRES + SINTONIA_SALA_DSN a apontar para o descartavel;
5. le: collection_run da corrida, raw_asset da corrida, sala_de_espera ligada ao raw (join por
   raw_observation_id + run_id), e as contagens antes/depois da 2.a passada (tem de inserir 0);
6. para o cluster e apaga a pasta dos dados.

RESIDUO NA ARVORE: no modo DESCARTAVEL o dono do RAW escreve os bytes SEMPRE na arvore (`XX/`, `IT/`;
`guarda/preservar_coleta.raiz_do_armazem_local`, de proposito). A prova apaga exatamente os ficheiros que o
`storage_object` desta corrida registou, e so esses, e as pastas que ficarem vazias.
"""
import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "coleta"))
FX = RAIZ / "ferramentas" / "linha_busca" / "fixtures" / "teste"
TABELAS = ("collection_run", "raw_asset", "storage_object", "sala_de_espera")


def _bin():
    for c in sorted(Path("/usr/lib/postgresql").glob("*/bin"), reverse=True):
        if all((c / n).exists() for n in ("initdb", "pg_ctl", "psql")):
            return c
    raise SystemExit("FALTA: binarios do PostgreSQL (initdb, pg_ctl, psql) em /usr/lib/postgresql/*/bin")


def _como_dono(cmd):
    return (["runuser", "-u", "postgres", "--"] + cmd) if os.geteuid() == 0 else cmd


def _porto_livre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main(argv) -> int:
    trab = Path(argv[1]).resolve()
    saida = Path(argv[2]) if len(argv) > 2 else trab / "PROVA-LINHA-BUSCA-DESCARTAVEL.json"
    BIN, porto = _bin(), _porto_livre()
    if trab.exists():
        shutil.rmtree(trab)
    dados = trab / "cluster"
    trab.mkdir(parents=True)
    if os.geteuid() == 0:
        shutil.chown(trab, "postgres", "postgres")
    url = "postgresql://postgres@127.0.0.1:%d/descartavel" % porto

    def psql(sql):
        r = subprocess.run([str(BIN / "psql"), "-X", "-q", "-A", "-t", "-F", "|", "-v", "ON_ERROR_STOP=1",
                            "-d", url, "-c", sql], capture_output=True, text=True)
        if r.returncode:
            raise SystemExit("psql: " + r.stderr[:400])
        return r.stdout.strip()

    def contagens():
        return {t: int(psql("select count(*) from public.%s" % t)) for t in TABELAS}

    subprocess.run(_como_dono([str(BIN / "initdb"), "-D", str(dados), "-U", "postgres", "--auth=trust",
                               "-E", "UTF8", "--no-sync"]), check=True, capture_output=True)
    subprocess.run(_como_dono([str(BIN / "pg_ctl"), "-D", str(dados), "-o",
                               "-p %d -h 127.0.0.1 -k %s" % (porto, trab), "-l", str(trab / "servidor.log"),
                               "-w", "start"]), check=True, stdin=subprocess.DEVNULL,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out = {"PG": str(BIN), "PORTO": porto}
    try:
        subprocess.run([str(BIN / "psql"), "-X", "-q", "-v", "ON_ERROR_STOP=1", "-c", "create database descartavel;",
                        "postgresql://postgres@127.0.0.1:%d/postgres" % porto], check=True, capture_output=True)
        r = subprocess.run(["bash", "motor/cadeia_canonica.sh", "migrations", url], cwd=str(RAIZ),
                           capture_output=True, text=True)
        out["MIGRATIONS_RC"] = r.returncode
        out["MIGRATIONS_PASS"] = sum(1 for l in r.stdout.splitlines() if l.startswith("MIGRATION_") and "=PASS" in l)
        if r.returncode:
            out["MIGRATIONS_ERRO"] = (r.stdout[-800:], r.stderr[-800:])
            raise SystemExit("a cadeia de migrations falhou")

        # dados SINTETICOS: a fixture de teste da linha, colhida sem rede
        import linha_busca as LB
        idx = json.loads((FX / "PAGINAS.json").read_text(encoding="utf-8"))

        def falso(u, cab=None):
            p = idx[u]
            if p.get("ERRO"):
                raise type(p["ERRO"], (Exception,), {})(p["PORQUE"])
            return (FX / p["FICHEIRO"]).read_bytes(), {"CONTENT_TYPE": p["CONTENT_TYPE"]}

        def _recusa_rede(*a, **k):
            raise AssertionError("a prova tentou sair a rede")
        LB.portao_it = LB.transporte_real = _recusa_rede
        fila = trab / "fila.json"
        fila.write_text(json.dumps({"DATASET": "SINTETICA", "LEI": "t", "ESTADOS": {}, "CANDIDATAS": []}),
                        encoding="utf-8")
        lote = trab / "LOTE-SINTETICO"
        LB.colher(json.loads((FX / "RESULTADOS.json").read_text(encoding="utf-8")), fila, lote, falso,
                  corrida="SINTETICA-COLHER")

        corrida = "LINHA-BUSCA-RAW-SINTETICA-LOTE5"
        env = dict(os.environ, BANCO_DESCARTAVEL_URL=url, SINTONIA_SALA_BACKEND="POSTGRES", SINTONIA_SALA_DSN=url,
                   SINTONIA_PSQL_EXE=str(BIN / "psql"), PYTHONUTF8="1",
                   HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9",
                   NO_PROXY="127.0.0.1,localhost")
        for n in ("SINTONIA_COLLECTION_DSN", "SUPABASE_DB_URL"):
            env.pop(n, None)
        out["ANTES"] = contagens()
        for i in (1, 2):
            r = subprocess.run([sys.executable, str(RAIZ / "coleta" / "linha_busca_raw.py"), "--repousar",
                                "--saidas=%s" % lote, "--corrida=%s" % corrida, "--pousar"],
                               env=env, capture_output=True, text=True, cwd=str(RAIZ))
            out["PASSADA_%d" % i] = {"RC": r.returncode, "STDOUT": r.stdout.strip()[-1500:],
                                     "STDERR": r.stderr.strip()[-1500:],
                                     "ERROS_DO_BANCO": [l.strip()[:300] for l in r.stderr.splitlines()
                                                        if "ERROR:" in l or "DETAIL:" in l][:4],
                                     "CONTAGENS": contagens()}
        out["CORRIDA"] = corrida
        out["COLLECTION_RUN"] = psql("select run_id, platform, actor, status from public.collection_run "
                                     "where run_id = '%s'" % corrida)
        out["RAW_DA_CORRIDA"] = psql("select count(*), count(distinct sha256) from public.raw_asset "
                                     "where run_id = '%s'" % corrida)
        out["SALA_DA_CORRIDA"] = psql("select count(*), count(raw_observation_id) from public.sala_de_espera "
                                      "where run_id = '%s'" % corrida)
        out["SALA_LIGA_AO_RAW"] = int(psql(
            "select count(*) from public.sala_de_espera s join public.raw_asset r "
            "on r.id = s.raw_observation_id and r.run_id = s.run_id where s.run_id = '%s'" % corrida))
        paths = [l for l in psql("select storage_path from public.storage_object").splitlines() if l.strip()]
        out["STORAGE_PATHS"] = paths
        for sp in paths:
            f = (RAIZ / sp).resolve()
            if RAIZ in f.parents and f.is_file() and not subprocess.run(
                    ["git", "ls-files", "--error-unmatch", sp], cwd=str(RAIZ), capture_output=True).returncode == 0:
                f.unlink()
                d = f.parent
                while d != RAIZ and not any(d.iterdir()):
                    d.rmdir()
                    d = d.parent
        p1, p2 = out["PASSADA_1"]["CONTAGENS"], out["PASSADA_2"]["CONTAGENS"]
        out["VEREDITO"] = {
            "CORRIDA_NASCE": bool(out["COLLECTION_RUN"]),
            "RAW_NASCE": p1["raw_asset"] > out["ANTES"]["raw_asset"],
            "ITEM_POUSA_LIGADO_AO_RAW": out["SALA_LIGA_AO_RAW"] > 0
            and out["SALA_LIGA_AO_RAW"] == p1["sala_de_espera"] - out["ANTES"]["sala_de_espera"],
            "SEGUNDA_PASSADA_INSERE_0": p1 == p2,
            "RC_OK": out["PASSADA_1"]["RC"] == 0 and out["PASSADA_2"]["RC"] == 0,
        }
    finally:
        subprocess.run(_como_dono([str(BIN / "pg_ctl"), "-D", str(dados), "-m", "fast", "-w", "stop"]),
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.rmtree(dados, ignore_errors=True)
    saida.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out.get(k) for k in ("MIGRATIONS_PASS", "CORRIDA", "COLLECTION_RUN", "RAW_DA_CORRIDA",
                                              "SALA_DA_CORRIDA", "SALA_LIGA_AO_RAW", "ANTES", "VEREDITO")},
                     ensure_ascii=False, indent=1))
    return 0 if all(out["VEREDITO"].values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
