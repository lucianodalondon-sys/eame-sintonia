#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D90 — ensaio da escrita das linhas de monitorizacao numa COPIA da Sala. Nunca a Sala.

Recebe um dump da Sala real feito SO EM LEITURA (`pg_dump -Fc`, o formato de `backup_sala.cmd`) e, num Postgres
DESCARTAVEL novo (o mesmo molde de provas/migracao_033_ensaio_copia.py):

    1  restaura o dump                                  contagens de raw_asset / derived_artifact / sala_de_espera
    2  d90_preservar_pacotes.py --aplicar               um TABLE_EXTRACTION por RAW presente, pelo dono do derivado
    3  outra vez                                        tudo REUSED, 0 linhas novas (idempotente)
    4  SELECTs                                          os filhos novos, e a sala_de_espera IGUAL byte a byte

    py curadoria/d90_ensaio_copia.py --dump <sala.dump> --pacotes <pasta do d90_payload_series> --saida <out.json>

So com LOCK-PESADO livre, sem LOCK-PRIORIDADE ativo e >= 5 GB livres. Sem rede (proxy fechado no ambiente do filho).
"""
import argparse
import hashlib
import importlib.util
import json
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

FILHOS = ("select id, raw_asset_id, producer_version, sha256, storage_path from public.derived_artifact "
          "where kind = 'TABLE_EXTRACTION' and producer = 'linhas-de-monitorizacao' order by raw_asset_id")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True)
    ap.add_argument("--pacotes", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    fora = {"DUMP": a.dump, "DUMP_SHA256": hashlib.sha256(open(a.dump, "rb").read()).hexdigest(),
            "MANIFESTO_SHA256": hashlib.sha256((Path(a.pacotes) / "MANIFESTO.json").read_bytes()).hexdigest(),
            "PASSOS": {}}
    pasta = Path(tempfile.mkdtemp(prefix="ensaio-d90-"))
    base = E.Base(pasta / "pg")
    assert ":54330/" not in base.url, "isto e a Sala real"
    env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", ""),
           "BANCO_DESCARTAVEL_URL": base.url, "SINTONIA_PSQL_EXE": base.exe("psql"), "PYTHONUTF8": "1",
           "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9"}
    for v in ("SINTONIA_COLLECTION_DSN", "SUPABASE_DB_URL", "SINTONIA_SALA_DSN"):
        env.pop(v, None)

    def psql(sql):
        r = subprocess.run([base.exe("psql"), "-X", "-q", "-A", "-t", "-F", "|", "-v", "ON_ERROR_STOP=1",
                            "-c", sql, base.url], capture_output=True, text=True, encoding="utf-8", env=env)
        if r.returncode:
            raise SystemExit("psql: %s" % r.stderr)
        return r.stdout.replace("\r", "").strip()

    def contagens():
        return {t: psql("select count(*) from public.%s" % t)
                for t in ("raw_asset", "derived_artifact", "sala_de_espera")}

    def escrever(nome):
        recibo = pasta / ("recibo-%s.json" % nome)
        r = subprocess.run([sys.executable, "-B", "curadoria/d90_preservar_pacotes.py", "--pacotes=%s" % a.pacotes,
                            "--armazem=%s" % (pasta / "armazem"), "--recibo=%s" % recibo, "--aplicar"],
                           cwd=str(RAIZ), env=env, capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        if r.returncode:
            raise SystemExit("escritor: %s" % r.stderr[-800:])
        shutil.copy(recibo, Path(a.saida).with_name(Path(a.saida).stem + "-recibo-%s.json" % nome))
        d = json.load(open(recibo, encoding="utf-8"))
        return {"SAIDA": r.stdout.strip(), "ESTADOS": [(x["RAW_ASSET_ID"], x["ESTADO"]) for x in d["RESULTADOS"]]}

    try:
        subprocess.run([base.exe("initdb"), "-D", str(base.pasta), "-U", "postgres", "--auth=trust", "-E", "UTF8",
                        "--no-sync"], check=True, capture_output=True)
        subprocess.run([base.exe("pg_ctl"), "-D", str(base.pasta), "-o", f"-p {base.porto} -h 127.0.0.1", "-l",
                        str(base.pasta / "servidor.log"), "-w", "start"], check=True, stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([base.exe("psql"), "-X", "-q", "-c", "create database sala_italia;",
                        f"postgresql://postgres@127.0.0.1:{base.porto}/postgres"], check=True, capture_output=True)
        r = subprocess.run([base.exe("pg_restore"), "--no-owner", "--no-privileges", "-d", base.url, a.dump],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        sala_antes = psql("select md5(string_agg(t::text, '' order by run_id, ordem)) from sala_de_espera t")
        fora["PASSOS"]["1_RESTAURO"] = {"CODIGO": r.returncode, "ERRO": r.stderr[-300:], **contagens()}
        man = json.loads((Path(a.pacotes) / "MANIFESTO.json").read_text(encoding="utf-8"))
        pais = {}
        for d in man["DOCUMENTOS"]:
            if d["RAW"] == "PRESENTE" and d["LINHAS"]:
                no_banco = psql("select sha256 from public.raw_asset where id = %d" % int(d["RAW_ID_PAI_PROPOSTO"]))
                pais[str(d["RAW_ID_PAI_PROPOSTO"])] = no_banco == d["PARENT_SHA256"]
        fora["PASSOS"]["1_RESTAURO"]["PAIS_CONFEREM"] = pais
        if not pais or not all(pais.values()):
            raise SystemExit("o pai na copia nao e o do pacote: %s" % pais)
        fora["PASSOS"]["2_ESCRITA"] = escrever("1")
        fora["PASSOS"]["3_OUTRA_VEZ"] = escrever("2")
        fora["PASSOS"]["4_SELECTS"] = {
            **contagens(), "FILHOS": psql(FILHOS).splitlines(),
            "SALA_DE_ESPERA_IGUAL": sala_antes == psql(
                "select md5(string_agg(t::text, '' order by run_id, ordem)) from sala_de_espera t")}
    finally:
        base.descer()
        shutil.rmtree(pasta, ignore_errors=True)
    Path(a.saida).write_text(json.dumps(fora, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    p = fora["PASSOS"]
    ok = (all(p["1_RESTAURO"]["PAIS_CONFEREM"].values()) and all(e in ("INSERTED", "REUSED") for _, e in p["2_ESCRITA"]["ESTADOS"])
          and all(e == "REUSED" for _, e in p["3_OUTRA_VEZ"]["ESTADOS"]) and p["4_SELECTS"]["SALA_DE_ESPERA_IGUAL"])
    print(json.dumps({"ENSAIO_D90": "PASS" if ok else "FAIL", "ANTES": p["1_RESTAURO"], "DEPOIS": {
        k: p["4_SELECTS"][k] for k in ("raw_asset", "derived_artifact", "sala_de_espera")}}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
