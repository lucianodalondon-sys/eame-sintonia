#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D79 — a 034 (LÁPIDE da retenção do YouTube) e a 035 (TEMPO_LUGAR) ensaiadas JUNTAS numa CÓPIA da Sala real.

Recebe um dump da Sala real feito SÓ EM LEITURA (`pg_dump -Fc`, o formato de `backup_sala.cmd`) e, num Postgres
DESCARTÁVEL novo (o método de `provas/migracao_033_ensaio_copia.py`):

    1  restaura o dump                          a cópia: esquema + dados + livro-razão (última = 033)
    2  cadeia `migrations`                      001..033 = SKIP HASH=MATCH; 034 = PASS; 035 = PASS
    3  validação                                a tabela da lápide e as suas travas; o vocabulário com TEMPO_LUGAR;
                                                os derivados e os RAW que existiam iguais (md5)
    4  LÁPIDE                                   uma lápide válida entra; regra/motivo inventados, rota que não é
                                                da API e o mesmo storage_path duas vezes são recusados
    5  TEMPO_LUGAR                              um derivado entra; a mesma régua outra vez e uma espécie
                                                inventada são recusadas
    6  DESFAZER pela ordem inversa              035 recusa com um TEMPO_LUGAR; 034 recusa com uma lápide;
                                                sem eles, os dois desfazem e o esquema volta ao da cópia
    7  cadeia outra vez                         034 = PASS, 035 = PASS

    py provas/migracoes_034_035_ensaio_copia.py --dump <sala.dump> --saida <out.json>
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

MD5 = {"DERIVADOS": ("select md5(coalesce(string_agg(t::text, '' order by id), '')) from "
                     "(select id, raw_asset_id, parent_sha256, kind, producer, producer_version, "
                     "parameters_hash, sha256, storage_path from derived_artifact) t"),
       "RAW": ("select md5(coalesce(string_agg(t::text, '' order by id), '')) from "
               "(select id, run_id, sha256, storage_path, preserved, not_preserved_reason from raw_asset) t")}


def sha_de(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    mig = {n: next((RAIZ / "supabase" / "migrations").glob(n + "_*.sql")) for n in ("034", "035")}
    fora = {"DUMP_SHA256": sha_de(a.dump),
            "MIGRACOES": {n: {"FICHEIRO": p.name, "SHA256": sha_de(p),
                              "DESFAZER_SHA256": sha_de(RAIZ / "supabase" / "desfazer" / (n + "_desfazer.sql"))}
                          for n, p in mig.items()},
            "PASSOS": {}}
    pasta = Path(tempfile.mkdtemp(prefix="ensaio-034-035-"))
    base = E.Base(pasta / "pg")
    assert ":54330/" not in base.url, "isto e a Sala real"
    env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", ""),
           "PYTHONUTF8": "1", "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9"}
    for v in ("SINTONIA_COLLECTION_DSN", "SUPABASE_DB_URL", "BANCO_DESCARTAVEL_URL", "SINTONIA_SALA_DSN"):
        env.pop(v, None)

    def psql(sql, ok=True):
        r = subprocess.run([base.exe("psql"), "-X", "-q", "-A", "-t", "-F", "|", "-v", "ON_ERROR_STOP=1",
                            "-c", sql, base.url], capture_output=True, text=True, encoding="utf-8", env=env)
        if ok and r.returncode:
            raise SystemExit("psql: %s" % r.stderr)
        return r.stdout.strip() if ok else (r.returncode, r.stderr.strip()[-260:])

    def esquema():
        r = subprocess.run([base.exe("pg_dump"), "-s", "--no-owner", "--no-privileges", base.url],
                           capture_output=True, text=True, encoding="utf-8", env=env, check=True)
        return hashlib.sha256(r.stdout.encode()).hexdigest()

    def cadeia():
        r = subprocess.run([shutil.which("bash") or "bash", "motor/cadeia_canonica.sh", "migrations", base.url],
                           cwd=str(RAIZ), env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        linhas = [l for l in r.stdout.splitlines() if l.startswith("MIGRATION")]
        return {"CODIGO": r.returncode, "MATCH": sum("HASH=MATCH" in l for l in linhas),
                "034_035": [l for l in linhas if l.startswith(("MIGRATION_034", "MIGRATION_035"))],
                "OUTRAS_QUE_NAO_SKIP": [l for l in linhas if "SKIP" not in l
                                        and not l.startswith(("MIGRATION_034", "MIGRATION_035"))],
                "ERRO": r.stderr[-300:]}

    def desfazer(n):
        r = subprocess.run([base.exe("psql"), "-X", "-q", "-v", "ON_ERROR_STOP=1", "--single-transaction", "-f",
                            str(RAIZ / "supabase" / "desfazer" / (n + "_desfazer.sql")), base.url],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        return {"CODIGO": r.returncode, "ERRO": r.stderr.strip()[-260:]}

    def lapide(sufixo, regra="YOUTUBE_API_III_E_4_30D", motivo="PRAZO_VENCIDO", rota="youtube-data-api-v3:videos"):
        return psql("insert into lapide_de_retencao (raw_asset_id, storage_path, sha256, bytes, regra, motivo, rota, "
                    "captured_at, prova) select id, 'ENSAIO/034/%s', sha256, 1, '%s', '%s', '%s', now(), 'ensaio' "
                    "from raw_asset order by id limit 1" % (sufixo, regra, motivo, rota), ok=False)

    def derivado(kind, sufixo):
        s = hashlib.sha256(("ensaio-035-" + sufixo).encode()).hexdigest()
        return psql("insert into derived_artifact (raw_asset_id, parent_sha256, kind, producer, producer_version, "
                    "pipeline_version, parameters, parameters_hash, sha256, bytes, media_type, storage_path, derived_at) "
                    "select id, sha256, '%s', 'ensaio-035', 'v0', 'ensaio', '{}'::jsonb, '%s', '%s', 2, "
                    "'application/json', 'ENSAIO/035/%s.json', now() from raw_asset order by id limit 1"
                    % (kind, "0" * 64, s, sufixo), ok=False)

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
                                        "SALA": psql("select count(*) from sala_de_espera"),
                                        "ULTIMA_MIGRACAO": psql("select max(versao) from schema_migracao")}
        esquema_antes = esquema()
        md5_antes = {k: psql(q) for k, q in MD5.items()}
        fora["PASSOS"]["2_UP"] = cadeia()
        fora["PASSOS"]["3_VALIDACAO"] = {
            "LAPIDE_EXISTE": psql("select to_regclass('public.lapide_de_retencao') is not null"),
            "LAPIDE_TRAVAS": psql("select string_agg(conname, ',' order by conname) from pg_constraint "
                                  "where conrelid='public.lapide_de_retencao'::regclass"),
            "VOCABULARIO": psql("select pg_get_constraintdef(oid) from pg_constraint "
                                "where conname='derived_artifact_kind_check'"),
            "LIVRO": psql("select string_agg(versao || ' ' || resultado, ' | ' order by versao) from schema_migracao "
                          "where versao in ('034', '035')"),
            "RAW_E_DERIVADOS_IGUAIS": {k: psql(q) == md5_antes[k] for k, q in MD5.items()}}
        fora["PASSOS"]["4_LAPIDE"] = {
            "VALIDA_ENTRA": lapide("a"),
            "MESMO_STORAGE_PATH_RECUSADO": lapide("a"),
            "REGRA_INVENTADA_RECUSADA": lapide("b", regra="OUTRA_REGRA"),
            "MOTIVO_INVENTADO_RECUSADO": lapide("c", motivo="PORQUE_SIM"),
            "ROTA_QUE_NAO_E_DA_API_RECUSADA": lapide("d", rota="yt-dlp:public_audio")}
        fora["PASSOS"]["5_TEMPO_LUGAR"] = {
            "ENTRA": derivado("TEMPO_LUGAR", "a"),
            "MESMA_REGUA_RECUSADA": derivado("TEMPO_LUGAR", "c"),
            "ESPECIE_INVENTADA_RECUSADA": derivado("INVENTADA", "b")}
        p6 = {"035_COM_TEMPO_LUGAR_RECUSA": desfazer("035")}
        psql("delete from derived_artifact where producer = 'ensaio-035'")
        p6["035_SEM_TEMPO_LUGAR"] = desfazer("035")
        p6["034_COM_LAPIDE_RECUSA"] = desfazer("034")
        psql("delete from lapide_de_retencao where prova = 'ensaio'")
        p6["034_SEM_LAPIDE"] = desfazer("034")
        p6["ESQUEMA_IGUAL_AO_DA_COPIA"] = esquema() == esquema_antes
        p6["RAW_E_DERIVADOS_IGUAIS"] = {k: psql(q) == md5_antes[k] for k, q in MD5.items()}
        fora["PASSOS"]["6_DESFAZER"] = p6
        fora["PASSOS"]["7_UP_DE_NOVO"] = cadeia()
    finally:
        base.descer()
        shutil.rmtree(pasta, ignore_errors=True)
    with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fora, fh, ensure_ascii=False, indent=1)
    print(json.dumps(fora, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
