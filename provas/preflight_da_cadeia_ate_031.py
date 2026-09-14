#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════
# A CADEIA ATÉ À 031 — medida, e não deduzida do número do ficheiro
#
# ── A PERGUNTA ────────────────────────────────────────────────────────
#
# O retrato do LIVE diz que lá o livro-razão vai até à `027`. A Sala é a
# `031`. Entre uma e outra há três migrations, e a pergunta que ninguém
# tinha medido é se elas são uma DEPENDÊNCIA ou apenas uma ORDEM.
#
#     NUMERO MAIOR NAO E DEPENDENCIA.
#     «FALTAM TRES MIGRATIONS» NAO E O MESMO QUE «A 031 PRECISA DELAS».
#
# Esta prova responde a isso a EXECUTAR, e não a ler nomes de ficheiro:
# constrói o estado `027` num PostgreSQL descartável e depois tenta cada
# migration futura lá dentro, numa transacção que é SEMPRE desfeita.
#
# ── PORQUE É QUE ISTO NÃO TOCA NO LIVE ────────────────────────────────
#
# Não tem como tocar: não há credencial nenhuma nesta sessão, e a trava de
# morada recusa qualquer endereço que não seja local antes de abrir
# ligação. O que se mede aqui é o estado DECLARADO em `supabase/migrations`
# na versão `027` — que é o que o retrato do LIVE diz que lá está.
#
#     ESTADO DECLARADO EM 027 != ESTADO MEDIDO DO LIVE.
#
# O segundo continua `NOT_MEASURED`, e esta prova não o promove.
# ═══════════════════════════════════════════════════════════════════════
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

RAIZ = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("PG_BIN", "/usr/lib/postgresql/17/bin"))
BANCADA = Path(os.environ.get("BANCADA", "/var/lib/postgresql/preflight031"))
DONO = os.environ.get("PG_DONO", "postgres")
PORTA = int(os.environ.get("PORTA", "5436"))
BANCO = "sintonia"

REF_031 = os.environ.get("REF_031", "origin/claude/sala-persistente-preflight-real-v1")
FICHEIRO_031 = "supabase/migrations/031_a_sala_de_espera_ganha_dono_duravel.sql"

# O estado que o retrato do LIVE declara: 001-007 e 009-027. A 008 confere
# e não cria, e por isso nunca entra na cadeia nem no livro.
ATE = "027"

HOSPEDEIROS_PERMITIDOS = {"localhost", "127.0.0.1", "::1", ""}


class MoradaProibida(RuntimeError):
    pass


def exige_morada_descartavel(url: str) -> str:
    partes = urlsplit(url)
    if (partes.hostname or "").lower() not in HOSPEDEIROS_PERMITIDOS:
        raise MoradaProibida(f"hospedeiro nao e local: {partes.hostname!r}")
    if (partes.path or "").lstrip("/") not in {BANCO, "postgres", ""}:
        raise MoradaProibida("nome de banco fora da lista")
    return url


def sh(cmd: str, *, como_dono: bool = False, check: bool = True,
       entrada: str | None = None, tempo: int = 600):
    if como_dono:
        cmd = f"su {DONO} -c {json.dumps(cmd)}"
    p = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True,
                       input=entrada, timeout=tempo, check=False)
    if check and p.returncode != 0:
        raise RuntimeError(f"falhou: {cmd}\n{p.stdout[-1500:]}\n{p.stderr[-1500:]}")
    return p


def url(banco: str = BANCO) -> str:
    return exige_morada_descartavel(f"postgresql://postgres@localhost:{PORTA}/{banco}")


def q(sql: str, *, banco: str = BANCO, so_leitura: bool = False, check: bool = True) -> str:
    corpo = f"begin read only;\n{sql}\ncommit;" if so_leitura else sql
    p = sh(f"{BIN}/psql {json.dumps(url(banco))} -v ON_ERROR_STOP=1 -tA -q -f -",
           como_dono=True, check=False, entrada=corpo)
    if check and p.returncode != 0:
        raise RuntimeError(f"SQL falhou:\n{sql[:300]}\n{p.stderr[-1200:]}")
    return p.stdout.strip() if p.returncode == 0 else f"__ERRO__{p.stderr.strip()}"


def nasce() -> None:
    sh(f"pkill -9 -u {DONO} postgres", check=False)
    time.sleep(1.5)
    if BANCADA.exists():
        shutil.rmtree(BANCADA)
    BANCADA.mkdir(parents=True)
    sh(f"chown -R {DONO}:{DONO} {BANCADA}")
    sh(f"{BIN}/initdb -D {BANCADA}/pg -U postgres --auth=trust -E UTF8", como_dono=True)
    (BANCADA / "pg" / "postgresql.conf").open("a").write(
        f"\nport = {PORTA}\nlisten_addresses = 'localhost'\n")
    sh(f"{BIN}/pg_ctl -D {BANCADA}/pg -l {BANCADA}/pg.log start -w", como_dono=True)
    q(f"create database {BANCO};", banco="postgres")


def ficheiro(num: str) -> Path:
    if num == "031":
        destino = BANCADA / "031.sql"
        p = sh(f"cd {RAIZ} && git show {REF_031}:{FICHEIRO_031}")
        destino.write_text(p.stdout)
        sh(f"chown {DONO}:{DONO} {destino}")
        return destino
    # As posteriores a 027 estao ESCONDIDAS enquanto a cadeia constroi o
    # estado 027 — senao o aplicador canonico aplicava-as tambem, e nao
    # haveria estado 027 nenhum para medir. Procura-se nos dois sitios.
    achados = sorted((RAIZ / "supabase" / "migrations").glob(f"{num}_*.sql"))
    if not achados:
        achados = sorted((BANCADA / "escondidas").glob(f"{num}_*.sql"))
    if len(achados) != 1:
        raise RuntimeError(f"{num}: esperava 1 ficheiro, achei {len(achados)}")
    return achados[0]


def aplica(num: str, *, registar: bool = True) -> str:
    """Aplica uma migration inteira, ou não aplica nenhuma parte dela."""
    f = ficheiro(num)
    corpo = f.read_text()
    sha = hashlib.sha256(corpo.encode()).hexdigest()
    if registar:
        corpo += ("\ninsert into public.schema_migracao (versao,resultado,sha256) "
                  f"values ('{num}','APLICADA','{sha}') on conflict (versao) do nothing;\n")
    p = sh(f"{BIN}/psql {json.dumps(url())} -v ON_ERROR_STOP=1 --single-transaction -q -f -",
           como_dono=True, check=False, entrada=corpo)
    return "PASS" if p.returncode == 0 else f"FAIL:{p.stderr.strip()[-300:]}"


def ensaia(num: str) -> dict:
    """Tenta a migration e DESFAZ. Mede a pré-condição sem deixar rasto.

    O DDL do PostgreSQL é transaccional: o `rollback` apaga a tabela, a
    trava e o índice que a migration criou. O que fica é só a resposta.
    """
    f = ficheiro(num)
    corpo = "begin;\n" + f.read_text() + "\nrollback;\n"
    p = sh(f"{BIN}/psql {json.dumps(url())} -v ON_ERROR_STOP=1 -q -f -",
           como_dono=True, check=False, entrada=corpo)
    return {"PRECONDITION": "PASS" if p.returncode == 0 else "FAIL",
            "PORQUE": "" if p.returncode == 0 else p.stderr.strip()[-300:]}


def objectos() -> set:
    return set(filter(None, q(
        "select string_agg(tablename, e'\\n') from pg_tables where schemaname='public';",
        so_leitura=True).split("\n")))


def main() -> int:
    r: dict = {"PROVA": "PREFLIGHT-DA-CADEIA-ATE-031", "MEDIDO_EM":
               datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "AVISO": "mede o estado DECLARADO em supabase/migrations na versao "
                        "027. NAO mede o LIVE, que continua NOT_MEASURED."}
    nasce()
    r["POSTGRES"] = q("show server_version;")

    # ── o estado 027, construido pelo aplicador canonico ───────────────
    # A cadeia aplica TUDO o que esta em supabase/migrations. Para parar na
    # 027 as posteriores sao escondidas — e repostas no fim.
    guardadas = BANCADA / "escondidas"
    guardadas.mkdir(exist_ok=True)
    movidas = []
    for f in sorted((RAIZ / "supabase" / "migrations").glob("*.sql")):
        if f.name[:3].isdigit() and f.name[:3] > ATE:
            shutil.move(str(f), guardadas / f.name)
            movidas.append(f)
    try:
        p = sh(f"cd {RAIZ} && PATH={BIN}:$PATH bash motor/cadeia_canonica.sh "
               f"migrations {json.dumps(url())}", check=False)
        r["CADEIA_ATE_027"] = {
            "EXIT": p.returncode,
            "APLICADAS": p.stdout.count("=PASS"),
            "LEDGER": q("select count(*) from public.schema_migracao;"),
            "ULTIMA": q("select max(versao) from public.schema_migracao;"),
        }
        conf = sh(f"{BIN}/psql {json.dumps(url())} -v ON_ERROR_STOP=1 -q -f "
                  f"{RAIZ}/supabase/migrations/008_verificacao_pos_aplicacao.sql",
                  check=False)
        r["CADEIA_ATE_027"]["CONFERENCIA_008"] = "PASS" if conf.returncode == 0 else "FAIL"
        antes = objectos()

        # ── A PERGUNTA CENTRAL ─────────────────────────────────────────
        # A 031 aplica-se DIRECTAMENTE sobre a 027, sem a 028, a 029 nem a
        # 030? Se sim, elas sao ORDEM e nao DEPENDENCIA — e dizer «a 031
        # precisa delas» seria falso.
        r["A_031_SOBRE_A_027_SEM_AS_TRES"] = ensaia("031")

        # E cada uma das futuras, sobre o estado 027.
        r["PRECONDICOES_SOBRE_027"] = {n: ensaia(n) for n in ("028", "029", "030")}

        # ── E o rollback deixou mesmo o banco como estava? ─────────────
        # Um ensaio que sujasse o banco mediria o ensaio anterior.
        r["ENSAIOS_NAO_DEIXARAM_RASTO"] = "SIM" if objectos() == antes else "NAO"
        r["LEDGER_DEPOIS_DOS_ENSAIOS"] = q("select count(*) from public.schema_migracao;")

        # ── A cadeia inteira, agora a serio, na ordem canonica ─────────
        r["CADEIA_COMPLETA"] = {}
        for n in ("028", "029", "030", "031"):
            r["CADEIA_COMPLETA"][n] = aplica(n)
        r["CADEIA_COMPLETA"]["LEDGER_FINAL"] = q(
            "select count(*) from public.schema_migracao;")
        r["CADEIA_COMPLETA"]["ULTIMA"] = q("select max(versao) from public.schema_migracao;")
        r["CADEIA_COMPLETA"]["SALA_EXISTE"] = q(
            "select count(*) from pg_tables where tablename='sala_de_espera';")

        # ── A 031, revalidada sem ser alterada ─────────────────────────
        r["MIGRATION_031"] = {
            "SHA": hashlib.sha256(ficheiro("031").read_bytes()).hexdigest(),
            "REF": REF_031,
            "REFERENCIA": sorted(set(q(
                "select string_agg(distinct confrelid::regclass::text, e'\\n') "
                "from pg_constraint where conrelid='public.sala_de_espera'::regclass "
                "and contype='f';", so_leitura=True).split("\n"))),
            "TRAVAS": q("select count(*) from pg_constraint "
                        "where conrelid='public.sala_de_espera'::regclass;", so_leitura=True),
            "INDICES": q("select count(*) from pg_indexes "
                         "where tablename='sala_de_espera';", so_leitura=True),
            "SO_CRIA": "SIM" if "alter table" not in ficheiro("031").read_text().lower()
                       .split("create table")[0] else "NAO",
        }
        # O caminho para a frente, exercido de verdade: a 031 desfaz-se sem
        # tocar em nada que ja existisse antes dela?
        depois_da_031 = objectos()
        r["FORWARD_RECOVERY_031"] = {
            "COMANDO": "drop table public.sala_de_espera; "
                       "delete from public.schema_migracao where versao='031';",
            "EXECUTADO": q("drop table public.sala_de_espera; "
                           "delete from public.schema_migracao where versao='031';",
                           check=False),
        }
        voltou = objectos()
        r["FORWARD_RECOVERY_031"]["DEVOLVEU_O_ESTADO_030"] = (
            "SIM" if voltou == depois_da_031 - {"sala_de_espera"} else "NAO")
        r["FORWARD_RECOVERY_031"]["LEDGER"] = q("select max(versao) from public.schema_migracao;")
    finally:
        for f in movidas:
            shutil.move(str(guardadas / f.name), f)
        r["MIGRATIONS_REPOSTAS"] = len(movidas)

    # ── o veredito ─────────────────────────────────────────────────────
    sem_as_tres = r["A_031_SOBRE_A_027_SEM_AS_TRES"]["PRECONDITION"]
    todas = all(v["PRECONDITION"] == "PASS" for v in r["PRECONDICOES_SOBRE_027"].values())
    cadeia = all(r["CADEIA_COMPLETA"][n] == "PASS" for n in ("028", "029", "030", "031"))
    r["VEREDITO"] = {
        "PRECONDITION_028": r["PRECONDICOES_SOBRE_027"]["028"]["PRECONDITION"],
        "PRECONDITION_029": r["PRECONDICOES_SOBRE_027"]["029"]["PRECONDITION"],
        "PRECONDITION_030": r["PRECONDICOES_SOBRE_027"]["030"]["PRECONDITION"],
        "PRECONDITION_031": sem_as_tres,
        "A_031_DEPENDE_DE_028_029_030": "NAO" if sem_as_tres == "PASS" else "SIM",
        "MIGRATION_CHAIN_028_031": "PASS" if (todas and cadeia) else "FAIL",
        "MIGRATION_031_DEFECT": "NO" if cadeia else "YES",
        "MEDIDO_CONTRA": "estado DECLARADO 027 (git), NAO o LIVE",
        "LIVE_READS": 0, "LIVE_WRITES": 0, "LIVE_DDL": 0,
    }
    saida = RAIZ / "provas" / "PREFLIGHT-CADEIA-031-MEDIDO.json"
    saida.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(r["VEREDITO"], indent=2, ensure_ascii=False))
    print(f"\nrelatorio -> {saida.relative_to(RAIZ)}")
    sh(f"{BIN}/pg_ctl -D {BANCADA}/pg stop -m immediate", como_dono=True, check=False)
    shutil.rmtree(BANCADA, ignore_errors=True)
    return 0 if r["VEREDITO"]["MIGRATION_CHAIN_028_031"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
