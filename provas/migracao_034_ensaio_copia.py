#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACERVO-TEMPO-LUGAR — o ensaio da 034 numa CÓPIA da Sala real. Nunca a Sala.

Recebe um dump da Sala real feito SÓ EM LEITURA (`pg_dump -Fc`, o formato de `backup_sala.cmd`) e,
num Postgres DESCARTÁVEL novo (o mesmo método de `provas/migracao_033_ensaio_copia.py`):

    1  restaura o dump                       a cópia: esquema + dados + livro-razão
    2  cadeia `migrations`                   001..033 = SKIP HASH=MATCH, 034 = PASS
    3  validação                             o vocabulário ganhou TEMPO_LUGAR; os derivados que
                                             existiam não mudaram (md5 da tabela igual)
    4  um derivado TEMPO_LUGAR entra         filho de um RAW real, com pai conferido pela FK
       e a mesma régua não entra duas vezes  (`derivacao_e_unica_por_regua`)
       e uma espécie inventada é recusada
    5  DESFAZER com um TEMPO_LUGAR presente  RECUSA (não apaga evidência)
    6  tira o derivado de ensaio (só aqui, na cópia) e DESFAZ   o esquema volta ao da cópia
    7  cadeia outra vez                      034 = PASS de novo

    py provas/migracao_034_ensaio_copia.py --dump <sala.dump> --saida <out.json>
"""
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "ensaio_offline", RAIZ / "scripts" / "micro_coleta" / "ensaio_offline.py")
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)

DERIVADOS_MD5 = ("select md5(coalesce(string_agg(t::text, '' order by id), '')) from "
                 "(select id, raw_asset_id, parent_sha256, kind, producer, producer_version, "
                 "parameters_hash, sha256, storage_path from derived_artifact) t")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    m034 = next((RAIZ / "supabase" / "migrations").glob("034_*.sql"))
    fora = {"DUMP_SHA256": hashlib.sha256(open(a.dump, "rb").read()).hexdigest(),
            "MIGRATION_034": m034.name,
            "MIGRATION_034_SHA256": hashlib.sha256(m034.read_bytes()).hexdigest(),
            "DESFAZER_034_SHA256": hashlib.sha256(
                (RAIZ / "supabase" / "desfazer" / "034_desfazer.sql").read_bytes()).hexdigest(),
            "PASSOS": {}}
    pasta = Path(tempfile.mkdtemp(prefix="ensaio-034-"))
    base = E.Base(pasta / "pg")
    assert ":54330/" not in base.url, "isto e a Sala real"
    env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", ""),
           "PYTHONUTF8": "1", "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9"}
    for v in ("SINTONIA_COLLECTION_DSN", "SUPABASE_DB_URL", "BANCO_DESCARTAVEL_URL", "SINTONIA_SALA_DSN"):
        env.pop(v, None)

    def psql(sql, ok=True):
        r = subprocess.run([base.exe("psql"), "-X", "-q", "-A", "-t", "-F", "|",
                            "-v", "ON_ERROR_STOP=1", "-c", sql, base.url],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        if ok and r.returncode:
            raise SystemExit("psql: %s" % r.stderr)
        return r.stdout.strip() if ok else (r.returncode, r.stderr.strip()[-300:])

    def esquema():
        r = subprocess.run([base.exe("pg_dump"), "-s", "--no-owner", "--no-privileges", base.url],
                           capture_output=True, text=True, encoding="utf-8", env=env, check=True)
        return hashlib.sha256(r.stdout.encode()).hexdigest()

    def cadeia():
        r = subprocess.run([shutil.which("bash") or "bash", "motor/cadeia_canonica.sh", "migrations", base.url],
                           cwd=str(RAIZ), env=env, capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        linhas = [l for l in r.stdout.splitlines() if l.startswith("MIGRATION")]
        return {"CODIGO": r.returncode, "MATCH": sum("HASH=MATCH" in l for l in linhas),
                "034": [l for l in linhas if l.startswith("MIGRATION_034")],
                "OUTRAS_QUE_NAO_SKIP": [l for l in linhas if "SKIP" not in l and not l.startswith("MIGRATION_034")],
                "ERRO": r.stderr[-400:]}

    def desfazer():
        r = subprocess.run([base.exe("psql"), "-X", "-q", "-v", "ON_ERROR_STOP=1", "--single-transaction", "-f",
                            str(RAIZ / "supabase" / "desfazer" / "034_desfazer.sql"), base.url],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        return {"CODIGO": r.returncode, "ERRO": r.stderr.strip()[-300:]}

    def inserir(kind, sufixo):
        # um filho de ensaio, de um RAW real da copia; bytes/sha de mentira mas com formato valido
        sha = hashlib.sha256(("ensaio-034-" + sufixo).encode()).hexdigest()
        return psql("insert into derived_artifact (raw_asset_id, parent_sha256, kind, producer, producer_version, "
                    "pipeline_version, parameters, parameters_hash, sha256, bytes, media_type, storage_path, derived_at) "
                    "select id, sha256, '%s', 'ensaio-034', 'v0', 'ensaio', '{}'::jsonb, '%s', '%s', 2, "
                    "'application/json', 'ENSAIO/034/%s.json', now() from raw_asset order by id limit 1"
                    % (kind, "0" * 64, sha, sufixo), ok=False)

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
        fora["PASSOS"]["1_RESTAURO"] = {"CODIGO": r.returncode, "ERRO": r.stderr[-300:],
                                        "RAW": psql("select count(*) from raw_asset"),
                                        "DERIVADOS": psql("select count(*) from derived_artifact"),
                                        "ULTIMA_MIGRACAO": psql("select max(versao) from schema_migracao")}
        esquema_antes, md5_antes = esquema(), psql(DERIVADOS_MD5)
        fora["PASSOS"]["2_UP"] = cadeia()
        fora["PASSOS"]["3_VALIDACAO"] = {
            "VOCABULARIO": psql("select pg_get_constraintdef(oid) from pg_constraint "
                                "where conname='derived_artifact_kind_check'"),
            "LIVRO_034": psql("select resultado || ' ' || sha256 from schema_migracao where versao='034'"),
            "DERIVADOS_QUE_EXISTIAM_IGUAIS": psql(DERIVADOS_MD5) == md5_antes}
        fora["PASSOS"]["4_TEMPO_LUGAR_ENTRA"] = inserir("TEMPO_LUGAR", "a")
        # outro caminho e outros bytes, a MESMA regua (pai, especie, produtor, versao, parametros):
        # tem de ser a `derivacao_e_unica_por_regua` a recusar, e nao o caminho unico
        fora["PASSOS"]["4_MESMA_REGUA_DUAS_VEZES_RECUSADA"] = inserir("TEMPO_LUGAR", "c")
        fora["PASSOS"]["4_ESPECIE_INVENTADA_RECUSADA"] = inserir("INVENTADA", "b")
        fora["PASSOS"]["5_DESFAZER_COM_TEMPO_LUGAR_RECUSA"] = desfazer()
        psql("delete from derived_artifact where producer = 'ensaio-034'")
        d = desfazer()
        d.update({"ESQUEMA_IGUAL_AO_DA_COPIA": esquema() == esquema_antes,
                  "DERIVADOS_IGUAIS": psql(DERIVADOS_MD5) == md5_antes})
        fora["PASSOS"]["6_DESFAZER_SEM_TEMPO_LUGAR"] = d
        fora["PASSOS"]["7_UP_DE_NOVO"] = cadeia()
    finally:
        base.descer()
        shutil.rmtree(pasta, ignore_errors=True)
    with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fora, fh, ensure_ascii=False, indent=1)
    print(json.dumps(fora, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
