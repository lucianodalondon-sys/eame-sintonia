#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MIGRACOES-EM-SERIE (DA-19) — 034 -> 035 -> 036, UMA POR VEZ, numa CÓPIA da Sala real.

Recebe um dump da Sala real feito SÓ EM LEITURA e, num Postgres DESCARTÁVEL novo,
para CADA migração, na ordem:

    a  backup da cópia (pg_dump -Fc) + sha256     como o runbook manda fazer na real
    b  impressão ANTES                            sala_de_espera, revisões, derived_artifact
    c  ferramentas/cadeia_ate.sh NNN              NNN = PASS; todas as outras = SKIP
    d  validação própria da NNN
    e  cadeia_ate NNN outra vez                   NNN = SKIP HASH=MATCH (idempotente)
    f  impressão DEPOIS                           igual à de ANTES, byte a byte
    g  DESFAZER da NNN                            esquema IGUAL ao de antes da NNN; conteúdo igual
    h  cadeia_ate NNN de novo                     NNN = PASS (para seguir para a próxima)

No fim: a cadeia INTEIRA (motor/cadeia_canonica.sh) sobre o resultado = tudo SKIP.

    py provas/migracoes_em_serie_ensaio.py --dump <sala.dump> --saida <out.json>
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

SERIE = ("034", "035", "036")

IMPRESSAO = {
    "SALA": "select count(*) || ' ' || coalesce(md5(string_agg(t::text, '' order by run_id, ordem)), '-') "
            "from public.sala_de_espera t",
    "REVISOES": "select count(*) || ' ' || coalesce(md5(string_agg(t::text, '' "
                "order by run_id, ordem, campo, revisao)), '-') from public.sala_de_espera_revisao t",
    "DERIVADOS": "select count(*) || ' ' || coalesce(md5(string_agg(t::text, '' order by id)), '-') "
                 "from public.derived_artifact t",
    "RAW": "select count(*) || ' ' || coalesce(md5(string_agg(t::text, '' order by id)), '-') "
           "from public.raw_asset t",
}

VALIDACAO = {
    "034": {"TABELA_LAPIDE": "select to_regclass('public.lapide_de_retencao') is not null",
            "LAPIDES": "select count(*) from public.lapide_de_retencao"},
    "035": {"KIND_ACEITA_TEMPO_LUGAR": "select pg_get_constraintdef(oid) like '%TEMPO_LUGAR%' "
                                       "from pg_constraint where conname = 'derived_artifact_kind_check'",
            "DERIVADOS_TEMPO_LUGAR": "select count(*) from public.derived_artifact where kind = 'TEMPO_LUGAR'"},
    "036": {"TABELA_VERSOES": "select to_regclass('public.sala_de_espera_versao') is not null",
            "GATILHOS": "select count(*) from pg_trigger where tgname like 'sala_de_espera_versao_%'",
            "VERSOES": "select count(*) from public.sala_de_espera_versao"},
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    fora = {"DUMP": a.dump, "DUMP_SHA256": hashlib.sha256(open(a.dump, "rb").read()).hexdigest(),
            "MIGRACOES": {}, "PASSOS": {}}
    for n in SERIE:
        f = next((RAIZ / "supabase" / "migrations").glob(n + "_*.sql"))
        fora["MIGRACOES"][n] = {"FICHEIRO": f.name, "SHA256": hashlib.sha256(f.read_bytes()).hexdigest()}
    pasta = Path(tempfile.mkdtemp(prefix="ensaio-serie-"))
    base = E.Base(pasta / "pg")
    assert ":54330/" not in base.url, "isto e a Sala real"
    env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", ""),
           "PYTHONUTF8": "1", "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9"}
    for v in ("SINTONIA_COLLECTION_DSN", "SUPABASE_DB_URL", "BANCO_DESCARTAVEL_URL",
              "SINTONIA_SALA_DSN", "PGOPTIONS"):
        env.pop(v, None)
    bash = shutil.which("bash") or "bash"

    def psql(sql):
        r = subprocess.run([base.exe("psql"), "-X", "-q", "-A", "-t", "-F", "|",
                            "-v", "ON_ERROR_STOP=1", "-c", sql, base.url],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        if r.returncode:
            raise SystemExit("psql: %s" % r.stderr)
        return r.stdout.strip()

    def esquema():
        r = subprocess.run([base.exe("pg_dump"), "-s", "--no-owner", "--no-privileges", base.url],
                           capture_output=True, text=True, encoding="utf-8", env=env, check=True)
        return hashlib.sha256(r.stdout.encode()).hexdigest()

    def conteudo():
        return {k: psql(v) for k, v in IMPRESSAO.items()}

    def livro():
        return psql("select string_agg(versao, ',' order by versao) from schema_migracao where versao >= '030'")

    def cadeia(ate=None):
        cmd = ([bash, "ferramentas/cadeia_ate.sh", ate, base.url] if ate
               else [bash, "motor/cadeia_canonica.sh", "migrations", base.url])
        r = subprocess.run(cmd, cwd=str(RAIZ), env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        linhas = [l for l in r.stdout.splitlines() if l.startswith("MIGRATION")]
        return {"CODIGO": r.returncode,
                "SKIP_MATCH": sum("HASH=MATCH" in l for l in linhas),
                "NAO_SKIP": [l for l in linhas if "SKIP" not in l],
                "ERRO": r.stderr[-300:] if r.returncode else ""}

    try:
        subprocess.run([base.exe("initdb"), "-D", str(base.pasta), "-U", "postgres",
                        "--auth=trust", "-E", "UTF8", "--no-sync"], check=True, capture_output=True)
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
        inicio = conteudo()
        fora["PASSOS"]["0_RESTAURO"] = {"CODIGO": r.returncode, "ERRO": r.stderr[-300:],
                                        "CONTEUDO": inicio, "LIVRO": livro()}
        for n in SERIE:
            p = {}
            bk = pasta / ("antes-%s.dump" % n)
            subprocess.run([base.exe("pg_dump"), "-Fc", "--no-owner", "--no-privileges",
                            "-f", str(bk), base.url], check=True, capture_output=True, env=env)
            p["a_BACKUP_SHA256"] = hashlib.sha256(bk.read_bytes()).hexdigest()
            antes, esq_antes = conteudo(), esquema()
            p["b_ANTES"] = antes
            p["c_UP"] = cadeia(n)
            p["d_VALIDACAO"] = {k: psql(v) for k, v in VALIDACAO[n].items()}
            p["e_UP_OUTRA_VEZ"] = cadeia(n)
            p["f_CONTEUDO_IGUAL"] = conteudo() == antes
            r = subprocess.run([base.exe("psql"), "-X", "-q", "-v", "ON_ERROR_STOP=1",
                                "--single-transaction", "-f",
                                str(RAIZ / "supabase" / "desfazer" / ("%s_desfazer.sql" % n)), base.url],
                               capture_output=True, text=True, encoding="utf-8", env=env)
            p["g_DESFAZER"] = {"CODIGO": r.returncode, "ERRO": r.stderr[-300:],
                               "ESQUEMA_IGUAL_AO_DE_ANTES": esquema() == esq_antes,
                               "CONTEUDO_IGUAL": conteudo() == antes, "LIVRO": livro()}
            p["h_UP_DE_NOVO"] = cadeia(n)
            p["LIVRO_DEPOIS"] = livro()
            fora["PASSOS"][n] = p
        fora["PASSOS"]["Z_CADEIA_INTEIRA"] = cadeia()
        fora["PASSOS"]["Z_CONTEUDO_IGUAL_AO_INICIO"] = conteudo() == inicio
    finally:
        base.descer()
        shutil.rmtree(pasta, ignore_errors=True)
    with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fora, fh, ensure_ascii=False, indent=1)
    print(json.dumps(fora, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
