#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MIGRACAO-SALA (D68) — o ensaio GERAL numa CÓPIA da Sala real. Nunca a Sala.

Recebe um dump da Sala real feito SÓ EM LEITURA (`pg_dump -Fc`, o mesmo
formato de `backup_sala.cmd`) e, num Postgres DESCARTÁVEL novo:

    1  restaura o dump                          (a cópia: esquema + dados + livro-razão)
    2  cadeia `migrations`                      001..032 = SKIP HASH=MATCH, 033 = PASS
    3  SELECTs de validação                     colunas, tabelas, vista, trava
    4  reprocessa as 78 pela porta (--aplicar)  as revisões nascem; as linhas não mudam
    5  reprocessa outra vez                     INSERIDAS = 0 (idempotente)
    6  contagem por campo, pela vista           quantas saem de NAO SEI
    7  DESFAZER                                 o esquema volta a ser o da cópia, byte a byte
    8  cadeia outra vez                         033 = PASS de novo

    py provas/migracao_033_ensaio_copia.py --dump <sala.dump> --livros "<glob;glob>" --saida <out.json>

É o roteiro de MIGRACAO-SALA.md, passo a passo, contra uma cópia.
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

CONTAGEM = """select count(*),
  count(*) filter (where published_at <> 'NAO SEI'),
  count(*) filter (where source_location <> 'NAO SEI'),
  count(*) filter (where fact_time <> 'NAO SEI'),
  count(*) filter (where fact_location <> 'NAO SEI'),
  count(*) filter (where fact_time_basis like 'RELATIVA_A_PUBLICACAO%'
                      or fact_time_basis like 'PUBLISHED_AT_COM_PROVA%'),
  count(*) filter (where revisoes > 0)
from public.sala_de_espera_atual"""
NOMES = ("LINHAS", "PUBLICACAO", "LOCAL_DA_FONTE", "DATA_DO_FATO", "LOCAL_DO_FATO",
         "DATA_DO_FATO_CALCULADA", "LINHAS_COM_REVISAO")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True)
    ap.add_argument("--livros", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    fora = {"DUMP": a.dump,
            "DUMP_SHA256": hashlib.sha256(open(a.dump, "rb").read()).hexdigest(),
            "MIGRATION_033_SHA256": hashlib.sha256(open(next(
                (RAIZ / "supabase" / "migrations").glob("033_*.sql")), "rb").read()).hexdigest(),
            "PASSOS": {}}
    pasta = Path(tempfile.mkdtemp(prefix="ensaio-033-"))
    base = E.Base(pasta / "pg")
    assert ":54330/" not in base.url, "isto e a Sala real"
    env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", ""),
           "SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_SALA_DSN": base.url,
           "SINTONIA_PSQL_EXE": base.exe("psql"), "PYTHONUTF8": "1",
           "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9"}
    for v in ("SINTONIA_COLLECTION_DSN", "SUPABASE_DB_URL", "BANCO_DESCARTAVEL_URL"):
        env.pop(v, None)

    def psql(sql):
        r = subprocess.run([base.exe("psql"), "-X", "-q", "-A", "-t", "-F", "|",
                            "-v", "ON_ERROR_STOP=1", "-c", sql, base.url],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        if r.returncode:
            raise SystemExit("psql: %s" % r.stderr)
        return r.stdout.strip()

    def esquema():
        r = subprocess.run([base.exe("pg_dump"), "-s", "--no-owner", "--no-privileges",
                            base.url], capture_output=True, text=True, encoding="utf-8",
                           env=env, check=True)
        return hashlib.sha256(r.stdout.encode()).hexdigest()

    def cadeia():
        r = subprocess.run([shutil.which("bash") or "bash", "motor/cadeia_canonica.sh",
                            "migrations", base.url], cwd=str(RAIZ), env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        linhas = [l for l in r.stdout.splitlines() if l.startswith("MIGRATION")]
        return {"CODIGO": r.returncode,
                "MATCH": sum("HASH=MATCH" in l for l in linhas),
                "033": [l for l in linhas if l.startswith("MIGRATION_033")],
                "OUTRAS_QUE_NAO_SKIP": [l for l in linhas if "SKIP" not in l
                                        and not l.startswith("MIGRATION_033")],
                "ERRO": r.stderr[-400:]}

    def reprocessar(nome):
        saida = pasta / ("reprocesso-%s.json" % nome)
        r = subprocess.run([sys.executable, "-B", "admissao/reprocessar_tempo_lugar.py",
                            "--livros", a.livros, "--aplicar", "--saida", str(saida)],
                           cwd=str(RAIZ), env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode:
            raise SystemExit("reprocessar: %s" % r.stderr[-800:])
        d = json.load(open(saida, encoding="utf-8"))
        shutil.copy(saida, Path(a.saida).with_name(Path(a.saida).stem + "-reprocesso-%s.json" % nome))
        return {k: d[k] for k in ("VERSAO_DO_EXTRATOR", "CONTA", "SAEM_DE_NAO_SEI")}

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
        fora["PASSOS"]["1_RESTAURO"] = {"CODIGO": r.returncode, "ERRO": r.stderr[-300:],
                                        "SALA_LINHAS": psql("select count(*) from sala_de_espera"),
                                        "ULTIMA_MIGRACAO": psql("select max(versao) from schema_migracao")}
        esquema_antes = esquema()
        linhas_antes = psql("select md5(string_agg(t::text, '' order by run_id, ordem)) "
                            "from sala_de_espera t")
        # 2 · UP
        fora["PASSOS"]["2_UP"] = cadeia()
        # 3 · validação
        fora["PASSOS"]["3_VALIDACAO"] = {
            "COLUNAS_NOVAS": psql("select string_agg(column_name, ',' order by column_name) "
                                  "from information_schema.columns where table_name='sala_de_espera' "
                                  "and column_name in ('published_at_basis','source_location_basis',"
                                  "'completude_tempo_lugar','tempo_lugar_evidencia','janela_declarada')"),
            "OBJETOS": psql("select to_regclass('public.sala_de_espera_revisao') is not null, "
                            "to_regclass('public.sala_de_espera_gaveta') is not null, "
                            "to_regclass('public.sala_de_espera_atual') is not null"),
            "GATILHOS": psql("select count(*) from pg_trigger where tgname like 'sala_de_espera_revisao_%'"),
            "LIVRO_033": psql("select resultado || ' ' || sha256 from schema_migracao where versao='033'"),
            "VISTA_IGUAL_A_TABELA_SEM_REVISOES": psql(
                "select count(*) from sala_de_espera s join sala_de_espera_atual a using (run_id, ordem) "
                "where a.fact_time = s.fact_time and a.published_at = s.published_at")}
        fora["PASSOS"]["6_CONTAGEM_ANTES"] = dict(zip(NOMES, psql(CONTAGEM).split("|")))
        # 4 · reprocessar
        fora["PASSOS"]["4_REPROCESSO_1"] = reprocessar("1")
        # 5 · outra vez
        fora["PASSOS"]["5_REPROCESSO_2"] = reprocessar("2")
        # 6 · contagem
        fora["PASSOS"]["6_CONTAGEM_DEPOIS"] = dict(zip(NOMES, psql(CONTAGEM).split("|")))
        fora["PASSOS"]["6_REVISOES"] = psql(
            "select string_agg(campo || '=' || n, ' ' order by campo) from "
            "(select campo, count(*) n from sala_de_espera_revisao group by campo) x")
        fora["PASSOS"]["6_LINHAS_ORIGINAIS_IGUAIS"] = linhas_antes == psql(
            "select md5(string_agg((run_id, ordem, item_id, raw_observation_id, universo, texto, "
            "source_id, source_location, fact_location, fact_time, captured_at, admitido_por, "
            "corrida_sha256, estado_da_fila, pousado_em, consumido_em, consumido_por, estagio, "
            "published_at, observed_at, fact_time_basis, fact_location_basis, "
            "source_declared_evidence_class, fato)::text, '' order by run_id, ordem)) "
            "from sala_de_espera")
        # 7 · DESFAZER
        r = subprocess.run([base.exe("psql"), "-X", "-q", "-v", "ON_ERROR_STOP=1",
                            "--single-transaction", "-f",
                            str(RAIZ / "supabase" / "desfazer" / "033_desfazer.sql"), base.url],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        fora["PASSOS"]["7_DESFAZER"] = {"CODIGO": r.returncode, "ERRO": r.stderr[-300:],
                                        "ESQUEMA_IGUAL_AO_DA_COPIA": esquema() == esquema_antes,
                                        "SALA_LINHAS": psql("select count(*) from sala_de_espera")}
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
