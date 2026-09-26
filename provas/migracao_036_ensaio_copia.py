#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEDUP-PARA-INSTALAR — o ensaio GERAL da 036 numa CÓPIA da Sala real. Nunca a Sala.

Recebe um dump da Sala real feito SÓ EM LEITURA (`pg_dump -Fc`, o formato de
`backup_sala.cmd`) e, num Postgres DESCARTÁVEL novo:

    1  restaura o dump                    a cópia; conta as linhas; impressão do conteúdo
    2  cadeia `migrations`                036 = PASS; diz QUALQUER outra que não seja SKIP
    3  validação                          tabela, 2 gatilhos, livro-razão 036
    4  cadeia outra vez                    036 = SKIP HASH=MATCH (idempotente)
    5  conteúdo igual                      sala_de_espera e sala_de_espera_revisao, byte a byte
    6  o caderno só acrescenta            UPDATE/DELETE/TRUNCATE recusados (numa versão de ensaio)
    7  DESFAZER                           esquema de volta ao da cópia; conteúdo igual
    8  cadeia outra vez                    036 = PASS de novo

    py provas/migracao_036_ensaio_copia.py --dump <sala.dump> --saida <out.json>
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

#: A impressão do CONTEÚDO: cada linha inteira, pela ordem da chave.
IMPRESSAO = {
    "SALA": "select count(*) || ' ' || coalesce(md5(string_agg(t::text, '' order by run_id, ordem)), '-') "
            "from public.sala_de_espera t",
    "REVISOES": "select count(*) || ' ' || coalesce(md5(string_agg(t::text, '' "
                "order by run_id, ordem, campo, revisao)), '-') from public.sala_de_espera_revisao t",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    mig = next((RAIZ / "supabase" / "migrations").glob("036_*.sql"))
    fora = {"DUMP": a.dump,
            "DUMP_SHA256": hashlib.sha256(open(a.dump, "rb").read()).hexdigest(),
            "MIGRATION_036": mig.name,
            "MIGRATION_036_SHA256": hashlib.sha256(mig.read_bytes()).hexdigest(),
            "PASSOS": {}}
    pasta = Path(tempfile.mkdtemp(prefix="ensaio-036-"))
    base = E.Base(pasta / "pg")
    assert ":54330/" not in base.url, "isto e a Sala real"
    env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", ""),
           "PYTHONUTF8": "1", "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9"}
    for v in ("SINTONIA_COLLECTION_DSN", "SUPABASE_DB_URL", "BANCO_DESCARTAVEL_URL",
              "SINTONIA_SALA_DSN", "PGOPTIONS"):
        env.pop(v, None)

    def psql(sql, falhar=True):
        r = subprocess.run([base.exe("psql"), "-X", "-q", "-A", "-t", "-F", "|",
                            "-v", "ON_ERROR_STOP=1", "-c", sql, base.url],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        if r.returncode and falhar:
            raise SystemExit("psql: %s" % r.stderr)
        return r.stdout.strip() if not r.returncode else ("RECUSADO: " + r.stderr.strip()[:160])

    def esquema(sem_036=False):
        """sha256 do esquema. `sem_036`: sem os blocos que falam da tabela de versões.

        ⚠️ A Sala real está na 033 e o vivo já traz a 034: a cadeia aplica AS DUAS.
        O desfazer da 036 não desfaz a 034 (nem deve), por isso o esquema depois do
        desfazer compara-se com o de DEPOIS DO UP menos os objetos da 036.
        """
        r = subprocess.run([base.exe("pg_dump"), "-s", "--no-owner", "--no-privileges",
                            base.url], capture_output=True, text=True, encoding="utf-8",
                           env=env, check=True)
        texto = r.stdout
        if sem_036:
            texto = "

".join(b for b in texto.split("

")
                                if "sala_de_espera_versao" not in b)
        return hashlib.sha256(texto.encode()).hexdigest()

    def conteudo():
        return {k: psql(v) for k, v in IMPRESSAO.items()}

    def cadeia():
        r = subprocess.run([shutil.which("bash") or "bash", "motor/cadeia_canonica.sh",
                            "migrations", base.url], cwd=str(RAIZ), env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        linhas = [l for l in r.stdout.splitlines() if l.startswith("MIGRATION")]
        return {"CODIGO": r.returncode,
                "MATCH": sum("HASH=MATCH" in l for l in linhas),
                "036": [l for l in linhas if l.startswith("MIGRATION_036")],
                "OUTRAS_QUE_NAO_SKIP": [l for l in linhas if "SKIP" not in l
                                        and not l.startswith("MIGRATION_036")],
                "ERRO": r.stderr[-400:]}

    try:
        # 1 · a cópia
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
        antes = conteudo()
        fora["PASSOS"]["1_RESTAURO"] = {
            "CODIGO": r.returncode, "ERRO": r.stderr[-300:], "CONTEUDO": antes,
            "MIGRACOES_NO_LIVRO": psql("select string_agg(versao, ',' order by versao) "
                                       "from schema_migracao where versao >= '030'")}
        esquema_antes = esquema()
        # 2 · UP
        fora["PASSOS"]["2_UP"] = cadeia()
        esquema_depois_do_up_sem_036 = esquema(sem_036=True)
        # 3 · validação
        fora["PASSOS"]["3_VALIDACAO"] = {
            "TABELA": psql("select to_regclass('public.sala_de_espera_versao') is not null"),
            "GATILHOS": psql("select count(*) from pg_trigger where tgname like 'sala_de_espera_versao_%'"),
            "LIVRO_036": psql("select resultado || ' ' || sha256 from schema_migracao where versao='036'"),
            "VERSOES": psql("select count(*) from sala_de_espera_versao")}
        # 4 · idempotente
        fora["PASSOS"]["4_UP_OUTRA_VEZ"] = cadeia()
        # 5 · conteúdo igual
        depois = conteudo()
        fora["PASSOS"]["5_CONTEUDO"] = {"DEPOIS": depois, "IGUAL": depois == antes}
        # 6 · o caderno só acrescenta (uma versão de ensaio, SÓ na cópia)
        um = psql("select run_id || '|' || ordem from sala_de_espera order by run_id, ordem limit 1")
        run, ordem = um.split("|")
        psql("insert into sala_de_espera_versao (run_id, ordem, versao, veio_da_corrida, item_id, "
             "texto, derivado_anterior, como_se_comparou) values ('%s', %s, 2, 'ENSAIO', "
             "'derived:0', 'ensaio', 'derived:0', 'MESMO_EXTRATOR')" % (run, ordem))
        fora["PASSOS"]["6_SO_ACRESCENTA"] = {
            c: psql(c, falhar=False) for c in (
                "update sala_de_espera_versao set texto = 'x'",
                "delete from sala_de_espera_versao",
                "truncate sala_de_espera_versao")}
        # 7 · DESFAZER
        r = subprocess.run([base.exe("psql"), "-X", "-q", "-v", "ON_ERROR_STOP=1",
                            "--single-transaction", "-f",
                            str(RAIZ / "supabase" / "desfazer" / "036_desfazer.sql"), base.url],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        fora["PASSOS"]["7_DESFAZER"] = {
            "CODIGO": r.returncode, "ERRO": r.stderr[-300:],
            "ESQUEMA_IGUAL_AO_DA_COPIA": esquema() == esquema_antes,
            "PORQUE_PODE_DIFERIR_DA_COPIA": "a cadeia aplicou tambem: %s" % (
                fora["PASSOS"]["2_UP"]["OUTRAS_QUE_NAO_SKIP"] or "nada"),
            "ESQUEMA_IGUAL_AO_DEPOIS_DO_UP_SEM_036": esquema(sem_036=True) == esquema_depois_do_up_sem_036,
            "OBJETOS_036_QUE_SOBRARAM": psql(
                "select count(*) from pg_class where relname = 'sala_de_espera_versao'") + "/" + psql(
                "select count(*) from pg_proc where proname = 'sala_de_espera_versao_so_acrescenta'"),
            "CONTEUDO_IGUAL": conteudo() == antes}
        # 8 · UP outra vez
        fora["PASSOS"]["8_UP_DE_NOVO"] = cadeia()
    finally:
        base.descer()
        shutil.rmtree(pasta, ignore_errors=True)
    with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fora, fh, ensure_ascii=False, indent=1)
    print(json.dumps(fora, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
