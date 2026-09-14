#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════
# A RECUPERAÇÃO FÍSICA — provada, e não prometida
#
# ── A PERGUNTA QUE ABRIU ESTA PROVA ───────────────────────────────────
#
# `C-RECOVERY-PROOF-BEFORE-LIVE-V1` provou um restauro a sério, e depois
# mediu a classe do backup do LIVE e descobriu que tinha provado a classe
# ERRADA:
#
#     LIVE_BACKUP_CLASS        PHYSICAL   (snapshot do provedor + WAL)
#     DISPOSABLE_BACKUP_CLASS  LOGICAL    (pg_dump formato custom)
#     SAME_CLASS_RESTORE       NO
#
# Um dump lógico e um snapshot físico não se restauram com as mesmas
# ferramentas nem falham pelos mesmos motivos. Provar um não prova o outro.
#
#     RESTAURO PROVADO DE UMA CLASSE != RESTAURO PROVADO DA OUTRA.
#
# Esta prova ataca exactamente essa lacuna: exerce a classe FÍSICA — base
# backup + arquivo de WAL + recuperação a um instante (PITR) — que é a
# mecânica que o Supabase embrulha por baixo do botão de Restore.
#
# ── O QUE ELA PROVA, E O QUE ELA NÃO PROVA ────────────────────────────
#
#   PROVA      que a CLASSE física recupera: que um base backup mais WAL
#              devolve o banco a um instante anterior ao desastre, com
#              schema, dados, travas, índices, sequências e livro-razão
#              intactos, e que o banco restaurado OPERA.
#
#   NÃO PROVA  que o botão de Restore do Supabase funciona nesta conta.
#              Isso exige exercer a PLATAFORMA, e a plataforma não é
#              alcançável daqui. A distinção tem nome e tem portão:
#
#     MESMA CLASSE != MESMA PLATAFORMA.
#     RESTAURO DE BANCO LOCAL NÃO É PROVA DE SUPABASE.
#
# O portão (`portao()`) recusa-se a promover uma na outra, e o red team
# ataca essa função directamente.
#
# ── PRODUÇÃO NÃO É LABORATÓRIO ────────────────────────────────────────
#
# Nenhum byte do LIVE entra aqui. As sentinelas são sintéticas e estão
# escritas neste ficheiro. A trava de morada decompõe qualquer URL e exige
# `hostname` local — e é executada, não prometida.
#
#     CAN DO != DID DO.
# ═══════════════════════════════════════════════════════════════════════
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

RAIZ = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("PG_BIN", "/usr/lib/postgresql/17/bin"))
BANCADA = Path(os.environ.get("BANCADA", "/var/lib/postgresql/bancada"))
DONO = os.environ.get("PG_DONO", "postgres")
PORTA_PRIMARIA = int(os.environ.get("PORTA_PRIMARIA", "5433"))
PORTA_RESTAURO = int(os.environ.get("PORTA_RESTAURO", "5434"))
PORTA_ARENA = int(os.environ.get("PORTA_ARENA", "5435"))
BANCO = "sintonia"

# A branch de onde a 031 é lida. Esta prova NÃO a reescreve e NÃO a copia
# para dentro desta linha: lê-a do ramo que é dono dela.
REF_031 = os.environ.get(
    "REF_031", "origin/claude/sala-persistente-preflight-real-v1"
)
FICHEIRO_031 = "supabase/migrations/031_a_sala_de_espera_ganha_dono_duravel.sql"

# ── A MORADA, E ELA É EXECUTADA ───────────────────────────────────────
# Um `if "supabase" not in url` seria contornável por um pooler, por um
# CNAME ou por um IP. A trava DECOMPÕE a URL e exige hospedeiro local.
HOSPEDEIROS_PERMITIDOS = {"localhost", "127.0.0.1", "::1", ""}


class MoradaProibida(RuntimeError):
    pass


def exige_morada_descartavel(url: str) -> str:
    """Recusa qualquer endereço que não seja desta máquina.

    NÃO é disciplina — é uma trava. O LIVE nunca é origem de backup nem
    destino de restauro, e a recusa acontece antes de qualquer ligação.
    """
    partes = urlsplit(url)
    hospedeiro = (partes.hostname or "").lower()
    if hospedeiro not in HOSPEDEIROS_PERMITIDOS:
        raise MoradaProibida(f"hospedeiro nao e local: {hospedeiro!r}")
    nome = (partes.path or "").lstrip("/")
    if nome not in {BANCO, "postgres", ""}:
        raise MoradaProibida(f"nome de banco fora da lista: {nome!r}")
    return url


def sh(cmd: list[str] | str, *, como_dono: bool = False, check: bool = True,
       entrada: str | None = None, tempo: int = 900) -> subprocess.CompletedProcess:
    if isinstance(cmd, list):
        cmd = " ".join(cmd)
    if como_dono:
        cmd = f"su {DONO} -c {json.dumps(cmd)}"
    return subprocess.run(
        ["bash", "-lc", cmd], capture_output=True, text=True,
        input=entrada, timeout=tempo, check=False,
    ) if not check else _checked(cmd, entrada, tempo)


def _checked(cmd: str, entrada: str | None, tempo: int) -> subprocess.CompletedProcess:
    p = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True,
                       input=entrada, timeout=tempo, check=False)
    if p.returncode != 0:
        raise RuntimeError(f"comando falhou ({p.returncode}): {cmd}\n"
                           f"{p.stdout[-2000:]}\n{p.stderr[-2000:]}")
    return p


def url(porta: int, banco: str = BANCO) -> str:
    return exige_morada_descartavel(f"postgresql://postgres@localhost:{porta}/{banco}")


def q(porta: int, sql: str, *, banco: str = BANCO, so_leitura: bool = False,
      check: bool = True) -> str:
    """Uma pergunta ao banco. `so_leitura` embrulha em `begin read only`."""
    corpo = f"begin read only;\n{sql}\ncommit;" if so_leitura else sql
    alvo = url(porta, banco)
    p = sh(f"{BIN}/psql {json.dumps(alvo)} -v ON_ERROR_STOP=1 -tA -q -f -",
           como_dono=True, check=False, entrada=corpo)
    if check and p.returncode != 0:
        raise RuntimeError(f"SQL falhou:\n{sql[:400]}\n{p.stderr[-1500:]}")
    return p.stdout.strip() if p.returncode == 0 else f"__ERRO__{p.stderr.strip()}"


def sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ═══════════════════════════════════════════════════════════════════════
# A IMPRESSÃO — ONZE PERGUNTAS, E NÃO UMA
#
# Um número só esconderia QUAL secção mudou, e saber qual é metade do
# diagnóstico. Cada secção sela uma família de factos que um restauro
# pode acertar ou errar independentemente das outras.
#
#     100 LINHAS ANTES E 100 DEPOIS NÃO PROVA QUE SÃO AS MESMAS 100.
#
# Por isso `SENTINELAS` não conta linhas: hasheia o CONTEÚDO INTEIRO de
# cada linha, via `to_jsonb`, que ordena as chaves e não deixa a forma do
# texto decidir o resultado.
# ═══════════════════════════════════════════════════════════════════════

# As marcas sintéticas. Nada aqui vem do LIVE, e todas se reconhecem à
# vista — um humano que as encontre em produção sabe que são de ensaio.
RUN_CAPTURA = "RESTAURO-FISICO-RUN-CAPTURA"
RUN_DERIVACAO = "RESTAURO-FISICO-RUN-DERIVACAO"
MARCA = "RESTAURO-FISICO"
BYTES_SINTETICOS = b"EAME SINTONIA :: sentinela sintetica de recuperacao fisica :: v2"
SHA_SINTETICO = hashlib.sha256(BYTES_SINTETICOS).hexdigest()

# `to_jsonb(t)` de cada linha, hasheado. É isto que apanha o ataque
# «contagens iguais com linhas erradas».
def _linhas(tabela: str, onde: str, ordem: str) -> str:
    return (f"select coalesce(string_agg(h, '|' order by h), '(vazio)') from ("
            f"  select encode(sha256(convert_to(to_jsonb(t)::text,'UTF8')),'hex') as h"
            f"  from public.{tabela} t where {onde} order by {ordem}) s;")


SECOES: dict[str, str] = {
    # O desenho: que tabelas existem, com que colunas, de que tipo.
    "TABELAS": """
      select string_agg(linha, e'\\n' order by linha) from (
        select c.table_name||'.'||c.column_name||' '||c.data_type
               ||case when c.is_nullable='NO' then ' NOTNULL' else '' end
               ||coalesce(' DEFAULT='||c.column_default,'') as linha
        from information_schema.columns c
        join information_schema.tables t
          on t.table_name=c.table_name and t.table_schema=c.table_schema
        where c.table_schema='public' and t.table_type='BASE TABLE') s;""",

    # A contagem de TODAS as tabelas de `public` — descoberta, não listada
    # à mão. Uma lista a mão envelhece; esta pergunta ao catálogo.
    "LINHAS": """
      select string_agg(t.relname||'='||
               (xpath('/row/c/text()',
                 query_to_xml(format('select count(*) as c from public.%I', t.relname),
                              false, true, '')))[1]::text::int::text,
             e'\\n' order by t.relname)
      from pg_class t join pg_namespace n on n.oid=t.relnamespace
      where n.nspname='public' and t.relkind='r';""",

    # O livro-razão: que migrations o banco diz ter, com que sha.
    "LEDGER": """
      select coalesce(string_agg(versao||'|'||resultado||'|'||sha256, e'\\n'
                                 order by versao), '(vazio)')
      from public.schema_migracao;""",

    # As travas, mordidas ou não — aqui só declaradas. Que elas MORDEM é
    # outra prova, e ela corre a seguir.
    "TRAVAS": """
      select string_agg(c.conrelid::regclass::text||'|'||c.conname||'|'||c.contype::text
                        ||'|'||pg_get_constraintdef(c.oid), e'\\n'
                        order by c.conrelid::regclass::text, c.conname)
      from pg_constraint c join pg_namespace n on n.oid=c.connamespace
      where n.nspname='public';""",

    "INDICES": """
      select string_agg(indexname||'|'||indexdef, e'\\n' order by indexname)
      from pg_indexes where schemaname='public';""",

    # Uma sequência que volta atrás entrega o MESMO id duas vezes. Um
    # restauro pode trazer todas as linhas e ainda assim ficar com a
    # próxima chave errada.
    # ⚠️ AQUI SÓ ENTRA O DESENHO DA SEQUÊNCIA, E NÃO O VALOR DELA.
    #
    # Esta separação nasceu de uma medição, não de uma preferência: na
    # primeira corrida esta prova REPROVOU O SEU PRÓPRIO RESTAURO, com
    # `SECOES_DIFERENTES = ['SEQUENCIAS']`. O restauro estava certo; a
    # regra de comparação é que estava errada.
    #
    # O PostgreSQL regista o valor de uma sequência no WAL aos SALTOS (32
    # de cada vez, `SEQ_LOG_VALS`), e fá-lo de propósito: assim uma
    # recuperação nunca devolve uma sequência ATRASADA, que entregaria um
    # id já usado. O preço é que ela volta ADIANTADA do valor que estava
    # em memória no instante do desastre.
    #
    #     UMA SEQUÊNCIA ADIANTADA DEPOIS DE UM RESTAURO É CORRECTO.
    #     UMA SEQUÊNCIA ATRASADA É UM ID DUPLICADO À ESPERA DE ACONTECER.
    #
    # Exigir igualdade byte a byte aqui reprovaria todo o restauro físico
    # correcto que existe. Por isso o VALOR tem regra própria — `>=` e um
    # tecto — em `sequencias_conferem()`, e o ataque `A12` ataca essa regra
    # em vez desta secção.
    "SEQUENCIAS": """
      select string_agg(linha, e'\\n' order by linha) from (
        select c.relname||'|inc='||coalesce(s.increment_by::text,'nulo')
               ||'|inicio='||coalesce(s.start_value::text,'nulo')
               ||'|ciclo='||coalesce(s.cycle::text,'nulo') as linha
        from pg_class c join pg_namespace n on n.oid=c.relnamespace
        left join pg_sequences s on s.schemaname=n.nspname and s.sequencename=c.relname
        where n.nspname='public' and c.relkind='S') z;""",

    # Uma extensão em falta faz o banco parecer inteiro até à primeira
    # chamada de função.
    "EXTENSOES": """
      select coalesce(string_agg(extname||'|'||extversion, e'\\n' order by extname),
                      '(nenhuma)')
      from pg_extension;""",

    # Dono e grants. Um restauro que devolve tudo com outro dono devolveu
    # um banco que a aplicação não consegue operar.
    "DONOS": """
      select string_agg(c.relname||'|'||pg_get_userbyid(c.relowner)
                        ||'|'||coalesce(array_to_string(c.relacl,','),'(padrao)'),
                        e'\\n' order by c.relname)
      from pg_class c join pg_namespace n on n.oid=c.relnamespace
      where n.nspname='public' and c.relkind in ('r','v','m');""",

    # Encoding, collation e fuso. Mudar o fuso muda o que um timestamptz
    # MOSTRA sem mudar um único byte guardado — e um verificador que só
    # lê texto acreditaria na diferença ou, pior, não a veria.
    "AMBIENTE": """
      select 'encoding='||current_setting('server_encoding')
             ||e'\\ncollate='||(select datcollate from pg_database
                                 where datname=current_database())
             ||e'\\nctype='||(select datctype from pg_database
                               where datname=current_database())
             ||e'\\ntimezone='||current_setting('TimeZone')
             ||e'\\ndatestyle='||current_setting('DateStyle')
             ||e'\\nintervalstyle='||current_setting('IntervalStyle');""",

    # Os tipos próprios (enums). A `etapa_da_coleta` e a `pais` são
    # vocabulário: um label perdido é uma lei perdida.
    "TIPOS": """
      select string_agg(t.typname||'='||e.rotulos, e'\\n' order by t.typname) from (
        select enumtypid, string_agg(enumlabel, ',' order by enumsortorder) as rotulos
        from pg_enum group by enumtypid) e
      join pg_type t on t.oid=e.enumtypid;""",
}

# As sentinelas, tabela a tabela. O conteúdo INTEIRO de cada linha entra
# no hash — não o `id`, não a contagem.
SENTINELAS: dict[str, str] = {
    "run": _linhas("collection_run", f"run_id like '{MARCA}%'", "run_id"),
    "storage": _linhas("storage_object", f"storage_path like '{MARCA}%'", "storage_path"),
    "raw": _linhas("raw_asset", f"run_id like '{MARCA}%'", "storage_path"),
    "derived": _linhas("derived_artifact", f"storage_path like '{MARCA}%'", "storage_path"),
    "participacao": _linhas(
        "participacao_na_derivacao",
        f"first_seen_derivation_run_id like '{MARCA}%'", "raw_asset_id"),
    "documento": _linhas("documento_estruturado", f"run_id like '{MARCA}%'", "derived_artifact_id"),
    "etapa": _linhas("etapa_da_corrida", f"run_id like '{MARCA}%'", "id"),
    "sala": _linhas("sala_de_espera", f"run_id like '{MARCA}%'", "run_id, ordem"),
}


# ── O VALOR DAS SEQUÊNCIAS, E A ÚNICA REGRA QUE ELE ACEITA ────────────
#
# Nunca para trás; nunca mais do que um bloco de WAL à frente.
SQL_VALORES_SEQ = """
select string_agg(sequencename||'='||coalesce(last_value::text,'nulo')
                  ||'|inc='||increment_by::text, e'\n' order by sequencename)
from pg_sequences where schemaname='public';"""

FOLGA_DO_WAL = 32  # SEQ_LOG_VALS: de quantos em quantos o PostgreSQL regista


def valores_das_sequencias(porta: int, sabotagem: str = "") -> dict:
    corpo = (f"begin;\n{sabotagem}\n{SQL_VALORES_SEQ}\nrollback;"
             if sabotagem else SQL_VALORES_SEQ)
    out: dict = {}
    for linha in (q(porta, corpo, check=False) or "").split("\n"):
        if "=" not in linha or "|inc=" not in linha:
            continue
        nome, resto = linha.split("=", 1)
        val, inc = resto.split("|inc=")
        out[nome] = (None if val == "nulo" else int(val), int(inc))
    return out


def sequencias_conferem(antes: dict, depois: dict) -> dict:
    """`>=` e um tecto. Nem atrasada, nem arbitrariamente à frente."""
    fora: dict = {}
    for nome, (v_antes, inc) in antes.items():
        v_depois = depois.get(nome, (None, inc))[0]
        if v_antes is None or v_depois is None:
            if v_antes != v_depois:
                fora[nome] = f"nulo de um lado so: antes={v_antes} depois={v_depois}"
            continue
        if v_depois < v_antes:
            fora[nome] = f"ANDOU PARA TRAS: antes={v_antes} depois={v_depois}"
        elif v_depois > v_antes + FOLGA_DO_WAL * abs(inc):
            fora[nome] = f"SALTOU ALEM DA FOLGA: antes={v_antes} depois={v_depois}"
    em_falta = sorted(set(antes) - set(depois))
    return {"SEQUENCIAS_CONFERIDAS": len(antes),
            "SEQUENCIAS_FORA_DA_REGRA": fora or "NENHUMA",
            "SEQUENCIAS_EM_FALTA": em_falta or "NENHUMA",
            "REGRA": "nunca para tras; no maximo um bloco de WAL "
                     f"({FOLGA_DO_WAL} x incremento) a frente",
            "RESULTADO": "PASS" if not fora and not em_falta else "FAIL"}


def impressao(porta: int, *, com_sala: bool = True) -> dict[str, str]:
    """A impressão do banco, secção a secção, lida em `begin read only`.

    Ler dentro de uma transacção só-de-leitura não é elegância: é o que
    torna impossível a conferência ter consertado o que estava a medir.
    """
    out: dict[str, str] = {}
    for nome, sql in SECOES.items():
        out[nome] = sha(q(porta, sql, so_leitura=True) or "(nulo)")
    partes = []
    for nome, sql in SENTINELAS.items():
        if nome == "sala" and not com_sala:
            continue
        partes.append(f"{nome}::{q(porta, sql, so_leitura=True)}")
    out["SENTINELAS"] = sha("\n".join(partes))
    out["_GLOBAL"] = sha("\n".join(f"{k}={out[k]}" for k in sorted(out)))
    return out


# ═══════════════════════════════════════════════════════════════════════
# A BANCADA — e ela é descartável de verdade
#
# `archive_mode=on` com `archive_command` a copiar para fora do `PGDATA` é
# a mecânica que torna o PITR possível: o base backup dá o PONTO DE
# PARTIDA e o WAL dá o CAMINHO até ao instante que se quer.
#
#     BASE BACKUP SEM ARQUIVO DE WAL NÃO É PITR. É UM SNAPSHOT.
# ═══════════════════════════════════════════════════════════════════════

def _dono(caminho: Path) -> None:
    sh(f"chown -R {DONO}:{DONO} {caminho}")


def derruba_tudo() -> None:
    subprocess.run(["bash", "-lc", f"pkill -9 -u {DONO} postgres"],
                   capture_output=True, text=True)
    time.sleep(1.5)


def nasce_primaria() -> None:
    pg = BANCADA / "primaria"
    arq = BANCADA / "arquivo"
    if BANCADA.exists():
        shutil.rmtree(BANCADA)
    arq.mkdir(parents=True)
    _dono(BANCADA)
    sh(f"{BIN}/initdb -D {pg} -U postgres --auth=trust -E UTF8 --data-checksums",
       como_dono=True)
    (pg / "postgresql.conf").open("a").write(f"""
port = {PORTA_PRIMARIA}
listen_addresses = 'localhost'
wal_level = replica
archive_mode = on
archive_command = 'test ! -f {arq}/%f && cp %p {arq}/%f'
max_wal_senders = 8
wal_keep_size = 512MB
summarize_wal = on
""")
    sh(f"{BIN}/pg_ctl -D {pg} -l {BANCADA}/primaria.log start -w", como_dono=True)
    q(PORTA_PRIMARIA, f"create database {BANCO};", banco="postgres")


def aplica_a_cadeia(porta: int) -> dict:
    """A cadeia canónica, e nenhum segundo aplicador.

    Se esta prova construísse o schema de outra maneira, provaria o
    restauro de um banco que a casa não tem.
    """
    alvo = url(porta)
    p = _checked(f"cd {RAIZ} && PATH={BIN}:$PATH bash motor/cadeia_canonica.sh "
                 f"migrations {json.dumps(alvo)}", None, 900)
    aplicadas = len(re.findall(r"^MIGRATION_\d+=(PASS|SKIP)", p.stdout, re.M))
    conf = sh(f"{BIN}/psql {json.dumps(alvo)} -v ON_ERROR_STOP=1 -q -f "
              f"{RAIZ}/supabase/migrations/008_verificacao_pos_aplicacao.sql",
              como_dono=False, check=False)
    return {"MIGRATIONS": aplicadas, "CONFERENCIA_008": "PASS" if conf.returncode == 0 else "FAIL"}


def aplica_031(porta: int) -> dict:
    """A 031 entra no descartável — e NÃO é reescrita aqui.

    Ela é lida do ramo que é dono dela. Esta missão não tem autoridade
    sobre a Sala; tem autoridade para a POR À PROVA.
    """
    destino = BANCADA / "031.sql"
    p = _checked(f"cd {RAIZ} && git show {REF_031}:{FICHEIRO_031}", None, 120)
    destino.write_text(p.stdout)
    _dono(destino)
    sha031 = hashlib.sha256(p.stdout.encode()).hexdigest()
    corpo = p.stdout + (
        "\ninsert into public.schema_migracao (versao,resultado,sha256) "
        f"values ('031','APLICADA','{sha031}') on conflict (versao) do nothing;\n")
    alvo = url(porta)
    r = sh(f"{BIN}/psql {json.dumps(alvo)} -v ON_ERROR_STOP=1 --single-transaction -q -f -",
           como_dono=True, check=False, entrada=corpo)
    return {"MIGRATION_031": "PASS" if r.returncode == 0 else "FAIL",
            "SHA_031": sha031, "REF_031": REF_031,
            "ERRO": (r.stderr[-400:] if r.returncode else "")}


# ── AS SENTINELAS ─────────────────────────────────────────────────────
# Dados sintéticos com relações suficientes para que PK, FK, UNIQUE,
# CHECK, NOT NULL, timestamp, JSON e linhagem tenham o que provar depois
# do restauro. Duas corridas de propósito: quem CAPTURA não é forçosamente
# quem DERIVA, e um restauro que as confunda tem de ser apanhado.
SQL_SENTINELAS = f"""
insert into public.collection_run
  (run_id, platform, started_at, rule_version, status, input, mission)
values
  ('{RUN_CAPTURA}', 'ENSAIO', '2026-01-01T00:00:00Z', 'v-ensaio', 'concluida',
   '{{"ensaio": true, "classe": "FISICA", "ordem": [3,1,2]}}'::jsonb,
   'RESTAURO FISICO'),
  ('{RUN_DERIVACAO}', 'ENSAIO', '2026-01-01T01:00:00Z', 'v-ensaio', 'concluida',
   '{{"ensaio": true, "papel": "derivacao"}}'::jsonb, 'RESTAURO FISICO');

insert into public.storage_object (storage_path, media_type, bytes, sha256)
values ('{MARCA}/STORAGE/1', 'text/plain', {len(BYTES_SINTETICOS)}, '{SHA_SINTETICO}');

insert into public.raw_asset
  (run_id, storage_path, media_type, bytes, sha256, captured_at, source_url,
   preserved, storage_object_id, source_id, document_key, document_key_basis,
   identity_state)
values
  ('{RUN_CAPTURA}', '{MARCA}/RAW/1', 'text/plain', {len(BYTES_SINTETICOS)},
   '{SHA_SINTETICO}', '2026-01-01T00:30:00Z', 'https://exemplo.invalido/ensaio',
   true,
   (select id from public.storage_object where storage_path='{MARCA}/STORAGE/1'),
   'FONTE-DE-ENSAIO', 'DOC-DE-ENSAIO-1', 'SOURCE_DOCUMENT_ID',
   'FORWARD_IDENTIFIED');

insert into public.derived_artifact
  (raw_asset_id, parent_sha256, kind, producer, producer_version,
   parameters, parameters_hash, sha256, bytes, media_type, storage_path,
   derived_at)
values
  ((select id from public.raw_asset where storage_path='{MARCA}/RAW/1'),
   '{SHA_SINTETICO}', 'TRANSCRIPTION', 'ENSAIO', 'v-ensaio',
   '{{"lingua": "pt", "nulo": null, "acentos": "ção-ãé"}}'::jsonb,
   '{sha("parametros-de-ensaio")}', '{sha("derivado-de-ensaio")}',
   64, 'text/plain', '{MARCA}/DERIVED/1', '2026-01-01T02:00:00Z');

insert into public.participacao_na_derivacao
  (raw_asset_id, derived_artifact_id, first_seen_derivation_run_id)
values
  ((select id from public.raw_asset where storage_path='{MARCA}/RAW/1'),
   (select id from public.derived_artifact where storage_path='{MARCA}/DERIVED/1'),
   '{RUN_DERIVACAO}');

insert into public.documento_estruturado
  (derived_artifact_id, run_id, source_id, texto, hash_texto, document_id)
values
  ((select id from public.derived_artifact where storage_path='{MARCA}/DERIVED/1'),
   '{RUN_DERIVACAO}', 'FONTE-DE-ENSAIO',
   'texto sintetico de ensaio, com acentos: ção e ã',
   '{sha("texto-de-ensaio")}', '{MARCA}-DOC-1');

insert into public.etapa_da_corrida (run_id, etapa, estado, source_id, passed)
values ('{RUN_CAPTURA}', 'RAW', 'PASS', 'FONTE-DE-ENSAIO', 1);
"""

# A Sala entra à parte: ela só existe se a 031 tiver sido aplicada.
# Duas linhas com o MESMO `item_id` de propósito — é o caso que matou a
# chave `(run_id, item_id)` e que a 031 documenta.
# ── O MARCO PÓS-BACKUP — a prova de que o WAL foi MESMO reproduzido ───
#
# ⚠️ ESTA SECÇÃO NASCEU DE UM DEFEITO DESTA PRÓPRIA PROVA.
#
# Na primeira versão, a impressão ANTES era tirada antes do base backup. Um
# restauro que reproduzisse ZERO WAL — só a cópia física — bateria certo na
# mesma, e a prova teria aprovado um PITR que nunca fez PITR.
#
#     COPIAR O BASE BACKUP NÃO É REPRODUZIR O WAL.
#     UMA IMPRESSÃO QUE O BASE BACKUP SOZINHO SATISFAZ NÃO PROVA RECUPERAÇÃO.
#
# Estas linhas são escritas DEPOIS do base backup e ANTES do ponto de
# recuperação. Logo não estão nos ficheiros copiados: só existem no WAL.
# Se elas voltam, o WAL foi reproduzido. Se não voltam, o restauro parou
# cedo demais — e é exactamente esse o ataque `A02`.
RUN_POS_BACKUP = f"{MARCA}-RUN-POS-BACKUP"

SQL_MARCO_POS_BACKUP = f"""
insert into public.collection_run
  (run_id, platform, started_at, rule_version, status, input, mission)
values ('{RUN_POS_BACKUP}', 'ENSAIO', '2026-01-02T00:00:00Z', 'v-ensaio',
        'concluida', '{{"escrito_depois_do_base_backup": true}}'::jsonb,
        'MARCO POS BACKUP');

insert into public.etapa_da_corrida (run_id, etapa, estado, source_id, passed)
values ('{RUN_POS_BACKUP}', 'READY', 'PASS', 'FONTE-DE-ENSAIO', 1);

insert into public.sala_de_espera
  (run_id, ordem, item_id, raw_observation_id, universo, texto, source_id,
   source_location, fact_location, fact_time, captured_at, admitido_por,
   corrida_sha256)
values ('{RUN_POS_BACKUP}', 0, 'ITEM-SO-NO-WAL',
        (select id from public.raw_asset where storage_path='{MARCA}/RAW/1'),
        'ENSAIO', 'esta linha so existe no WAL, nunca no base backup',
        'FONTE-DE-ENSAIO', 'NAO SEI', 'NAO SEI', 'NAO SEI',
        '2026-01-02T00:00:00Z', 'ensaio', '{SHA_SINTETICO}');
"""


SQL_SENTINELAS_SALA = f"""
insert into public.sala_de_espera
  (run_id, ordem, item_id, raw_observation_id, universo, texto, source_id,
   source_location, fact_location, fact_time, captured_at, admitido_por,
   corrida_sha256, estado_da_fila)
values
  ('{RUN_DERIVACAO}', 0, '?',
   (select id from public.raw_asset where storage_path='{MARCA}/RAW/1'),
   'ENSAIO', 'primeiro item sintetico', 'FONTE-DE-ENSAIO',
   'NAO SEI', 'NAO SEI', 'NAO SEI', '2026-01-01T00:30:00Z', 'ensaio',
   '{SHA_SINTETICO}', 'WAITING'),
  ('{RUN_DERIVACAO}', 1, '?', null,
   'ENSAIO', 'segundo item sintetico, mesmo item_id de proposito',
   'FONTE-DE-ENSAIO', 'NAO SEI', 'NAO SEI', 'NAO SEI',
   '2026-01-01T00:31:00Z', 'ensaio', '{SHA_SINTETICO}', 'WAITING'),
  ('{RUN_CAPTURA}', 0, 'ITEM-COM-ID', null,
   'ENSAIO', 'terceiro item sintetico', 'FONTE-DE-ENSAIO',
   'NAO SEI', 'NAO SEI', 'NAO SEI', '2026-01-01T00:32:00Z', 'ensaio',
   '{sha("outra-corrida")[:64]}', 'WAITING');

-- A transicao WAITING -> CONSUMED, feita como a Sala a faz: o estado e os
-- dois carimbos mudam JUNTOS, porque a trava `consumo_diz_quem_e_quando`
-- recusa qualquer ordem em que eles se separem.
update public.sala_de_espera
   set estado_da_fila = 'CONSUMED',
       consumido_em   = '2026-01-01T03:00:00Z',
       consumido_por  = 'ensaio-consumidor'
 where run_id = '{RUN_DERIVACAO}' and ordem = 1;
"""


# ═══════════════════════════════════════════════════════════════════════
# O BACKUP FÍSICO — e a conferência dele antes de se acreditar nele
#
# `pg_basebackup` produz uma cópia FÍSICA do cluster: os mesmos ficheiros
# de dados, não um script de `insert`. É a classe do LIVE.
#
# `pg_verifybackup` confere o manifesto — sha de CADA ficheiro. Um backup
# que existe e está corrompido é pior do que um backup que falta, porque
# o segundo ninguém confunde com segurança.
# ═══════════════════════════════════════════════════════════════════════

def backup_fisico() -> dict:
    destino = BANCADA / "base"
    t0 = time.monotonic()
    sh(f"{BIN}/pg_basebackup -h localhost -p {PORTA_PRIMARIA} -U postgres "
       f"-D {destino} -Fp -Xstream -c fast --manifest-checksums=SHA256",
       como_dono=True)
    segundos = round(time.monotonic() - t0, 2)
    v = sh(f"{BIN}/pg_verifybackup {destino}", como_dono=True, check=False)
    bytes_ = int(sh(f"du -sb {destino} | cut -f1").stdout.split()[0])
    manifesto = json.loads((destino / "backup_manifest").read_text())
    return {
        "BACKUP_CLASS": "PHYSICAL",
        "BACKUP_MECHANISM": "pg_basebackup + arquivo de WAL",
        "BACKUP_CREATED": "YES",
        "BACKUP_BYTES": bytes_,
        "BACKUP_FICHEIROS": len(manifesto.get("Files", [])),
        "BACKUP_CHECKSUM_ALGO": "SHA256",
        "BACKUP_INTEGRITY_CHECK": "PASS" if v.returncode == 0 else "FAIL",
        "BACKUP_SEGUNDOS": segundos,
    }


def marca_o_ponto_de_recuperacao() -> dict:
    """O instante para onde se quer voltar.

    O Supabase oferece PITR por INSTANTE, e é isso que se exerce aqui —
    não um «último backup». Provar o mecanismo que a emergência usaria é
    o ponto todo.
    """
    q(PORTA_PRIMARIA, "select pg_create_restore_point('PONTO_ANTES_DO_DESASTRE');")
    lsn = q(PORTA_PRIMARIA, "select pg_current_wal_lsn();")
    instante = q(PORTA_PRIMARIA, "select clock_timestamp();")
    # Uma folga real entre o ponto e o desastre: sem ela, um restauro por
    # instante não consegue distinguir os dois lados da fronteira.
    time.sleep(2)
    return {"RECOVERY_TARGET_LSN": lsn, "RECOVERY_TARGET_TIME": instante,
            "RECOVERY_TARGET_NAME": "PONTO_ANTES_DO_DESASTRE"}


# ═══════════════════════════════════════════════════════════════════════
# OS DESASTRES — pequenos, reais, e de quatro famílias diferentes
#
# Um restauro pode acertar numa família e falhar noutra. Apagar linhas
# perde DADOS; deitar abaixo uma tabela perde o DESENHO; uma migration
# estrutural má perde uma TRAVA sem perder uma linha; e corromper uma
# linha não perde NADA — muda o conteúdo, e a contagem continua igual.
#
#     É A QUARTA QUE APANHA O VERIFICADOR PREGUIÇOSO.
# ═══════════════════════════════════════════════════════════════════════

DESASTRES = {
    "A_DELETE_DE_DADOS": f"""
      delete from public.sala_de_espera where run_id='{RUN_DERIVACAO}';
      delete from public.documento_estruturado where run_id='{RUN_DERIVACAO}';""",
    "B_DROP_DE_TABELA": """
      drop table public.sala_de_espera cascade;""",
    "C_MIGRATION_ESTRUTURAL_MA": """
      alter table public.raw_asset drop constraint forward_identificado_exige_identidade;
      drop index if exists public.raw_asset_sha256_idx;
      alter table public.derived_artifact add column coluna_errada text;
      insert into public.schema_migracao (versao, resultado, sha256)
        values ('999','APLICADA','0000000000000000000000000000000000000000000000000000000000000000');""",
    # ⚠️ A CORRUPÇÃO LÓGICA TEVE DE SER REESCRITA, E A RAZÃO É BOA NOTÍCIA.
    #
    # A primeira versão tentou adulterar o `sha256` da observação. O banco
    # RECUSOU, com uma trava da FASE 10:
    #
    #     «a identidade da observacao nao se reescreve (tentou mudar: sha256).
    #      Uma corrida que PROVE outra coisa escreve uma observacao NOVA.»
    #
    # O schema defende-se sozinho — o que é excelente, e é um facto medido
    # que fica registado. Mas um desastre que o banco recusa NÃO É UM
    # DESASTRE, e tratá-lo como tal teria posto esta prova a restaurar
    # de um estrago que nunca aconteceu.
    #
    #     UM DESASTRE QUE FALHA NÃO PROVA UM RESTAURO.
    #
    # Por isso a corrupção passa a bater onde o schema PERMITE bater, e a
    # recusa da identidade vira uma medição à parte (`D0`).
    "D_CORRUPCAO_LOGICA": f"""
      update public.collection_run
         set input = '{{"ensaio": true, "adulterado": true}}'::jsonb,
             mission = 'ADULTERADO'
       where run_id='{RUN_CAPTURA}';
      update public.etapa_da_corrida
         set passed = 999, comecou_em = '1999-01-01T00:00:00Z'
       where run_id='{RUN_CAPTURA}';""",
}

# ── AS DUAS SONDAS QUE O BANCO RECUSA, E É SUPOSTO RECUSAR ────────────
#
# Medido, não suposto: as duas tentativas de adulterar uma IMPRESSÃO DE
# CONTEÚDO são travadas pelo próprio schema. Ficam registadas porque são
# um facto sobre a casa — e porque foi a tentativa de as usar como
# desastre que ensinou a distinção:
#
#     O QUE O SCHEMA RECUSA NÃO SERVE DE DESASTRE.
#     UM DESASTRE QUE FALHA DEIXA A PROVA A RESTAURAR DE UM ESTRAGO
#     QUE NUNCA ACONTECEU — E A CHAMAR-LHE VERDE.
SONDAS_QUE_O_SCHEMA_RECUSA = {
    # Trava da FASE 10: «a identidade da observacao nao se reescreve».
    "D0a_identidade_da_observacao": f"""
      update public.raw_asset set sha256 = '{"f"*64}'
       where storage_path='{MARCA}/RAW/1';""",
    # FK composta `a_observacao_e_a_copia_falam_do_mesmo_conteudo`: a cópia
    # e a observação têm de continuar a falar do MESMO conteúdo.
    "D0b_sha_da_copia": f"""
      update public.storage_object set sha256 = '{"f"*64}'
       where storage_path='{MARCA}/STORAGE/1';""",
}


def provoca_os_desastres() -> dict:
    """Destruição REAL, confirmada depois de feita.

    Um desastre que a prova declara mas não confirma é um desastre que
    pode não ter acontecido — e então o «restauro» não restaurou nada.
    """
    feitos = {}
    for nome, sql in DESASTRES.items():
        r = q(PORTA_PRIMARIA, sql, check=False)
        feitos[nome] = "FEITO" if not r.startswith("__ERRO__") else f"FALHOU:{r[:200]}"
    for nome, sql in SONDAS_QUE_O_SCHEMA_RECUSA.items():
        r_ = q(PORTA_PRIMARIA, sql, check=False)
        feitos[nome] = "RECUSOU" if r_.startswith("__ERRO__") else "DEIXOU_PASSAR"
    confirmacao = {
        "sala_existe": q(PORTA_PRIMARIA,
                         "select count(*) from pg_tables where tablename='sala_de_espera';"),
        "documentos_restantes": q(
            PORTA_PRIMARIA,
            f"select count(*) from public.documento_estruturado where run_id='{RUN_DERIVACAO}';"),
        "trava_existe": q(PORTA_PRIMARIA,
                          "select count(*) from pg_constraint "
                          "where conname='forward_identificado_exige_identidade';"),
        "json_adulterado": q(PORTA_PRIMARIA,
                             f"select input->>'adulterado' from public.collection_run "
                             f"where run_id='{RUN_CAPTURA}';"),
        "contagem_adulterada": q(PORTA_PRIMARIA,
                                 f"select passed from public.etapa_da_corrida "
                                 f"where run_id='{RUN_CAPTURA}';"),
        "ledger_tem_999": q(PORTA_PRIMARIA,
                            "select count(*) from public.schema_migracao where versao='999';"),
    }
    feitos["CONFIRMACAO_DA_DESTRUICAO"] = confirmacao
    # As quatro familias, cada uma confirmada pelo que o banco RESPONDE —
    # e nao pelo que a prova diz que fez.
    feitos["DESTRUICAO_REAL"] = (
        "SIM" if confirmacao["sala_existe"] == "0"              # B · DROP
        and confirmacao["documentos_restantes"] == "0"          # A · DELETE
        and confirmacao["trava_existe"] == "0"                  # C · schema
        and confirmacao["ledger_tem_999"] == "1"                # C · ledger
        and confirmacao["json_adulterado"] == "true"            # D · JSON
        and confirmacao["contagem_adulterada"] == "999"         # D · numero
        else "NAO")
    return feitos


def sela_o_arquivo() -> int:
    """Empurra o WAL para o arquivo e espera que ele lá chegue.

    Sem isto, o restauro pediria um segmento que ainda está no `pg_wal` da
    primária — e a primária vai ser DESTRUÍDA a seguir.
    """
    q(PORTA_PRIMARIA, "select pg_switch_wal();")
    q(PORTA_PRIMARIA, "checkpoint;")
    q(PORTA_PRIMARIA, "select pg_switch_wal();")
    for _ in range(60):
        pendentes = q(PORTA_PRIMARIA,
                      "select count(*) from pg_stat_archiver where last_failed_wal "
                      "is not null and (last_archived_wal is null or "
                      "last_failed_wal > last_archived_wal);")
        time.sleep(0.5)
        if pendentes == "0":
            break
    return len(list((BANCADA / "arquivo").iterdir()))


# ═══════════════════════════════════════════════════════════════════════
# O RESTAURO — e o original é destruído ANTES
#
#     RESTAURAR POR CIMA DO QUE AINDA EXISTE NÃO PROVA NADA.
#
# Se a primária continuar de pé, uma tabela que o restauro NÃO trouxe
# continua lá, e o verde é do banco velho em vez de ser do backup. Por
# isso ela é parada e o `PGDATA` dela é APAGADO, e a prova confirma que
# desapareceu antes de restaurar.
#
# E isto não é rebuild: nenhuma migration corre para o banco voltar. O que
# volta é o FICHEIRO de dados do base backup, mais o WAL até ao instante.
#
#     REBUILD POR MIGRATIONS NÃO É RESTORE.
#     REINSERT DE DADOS NÃO É RESTORE.
# ═══════════════════════════════════════════════════════════════════════

def destroi_a_primaria() -> dict:
    pg = BANCADA / "primaria"
    sh(f"{BIN}/pg_ctl -D {pg} stop -m immediate", como_dono=True, check=False)
    time.sleep(1)
    shutil.rmtree(pg, ignore_errors=True)
    viva = sh(f"{BIN}/pg_isready -h localhost -p {PORTA_PRIMARIA}", check=False)
    return {"ORIGINAL_DATABASE_AVAILABLE": "NO" if viva.returncode != 0 else "SIM",
            "PGDATA_DA_PRIMARIA_EXISTE": "SIM" if pg.exists() else "NAO"}


def restaura(destino: Path, porta: int, alvo: dict, *, chave: str = "time",
             valor: str | None = None, promove: bool = True) -> None:
    """O restauro físico: base backup + WAL até ao instante pedido."""
    if destino.exists():
        shutil.rmtree(destino)
    sh(f"cp -a {BANCADA/'base'} {destino}")
    _dono(destino)
    if chave == "time":
        linha = f"recovery_target_time = '{valor or alvo['RECOVERY_TARGET_TIME']}'"
    elif chave == "name":
        linha = f"recovery_target_name = '{valor or alvo['RECOVERY_TARGET_NAME']}'"
    else:
        linha = f"recovery_target_lsn = '{valor or alvo['RECOVERY_TARGET_LSN']}'"
    (destino / "postgresql.conf").open("a").write(f"""
port = {porta}
archive_mode = off
restore_command = 'cp {BANCADA}/arquivo/%f %p'
{linha}
recovery_target_action = '{'promote' if promove else 'pause'}'
""")
    sh(f"touch {destino}/recovery.signal", como_dono=True)


def liga_e_espera(destino: Path, porta: int, log: str, tempo: int = 180) -> float:
    t0 = time.monotonic()
    sh(f"{BIN}/pg_ctl -D {destino} -l {BANCADA}/{log} start -w -t {tempo}",
       como_dono=True, check=False)
    for _ in range(tempo * 2):
        r = q(porta, "select pg_is_in_recovery();", banco="postgres", check=False)
        if r == "f":
            return round(time.monotonic() - t0, 2)
        time.sleep(0.5)
    return round(time.monotonic() - t0, 2)


# ═══════════════════════════════════════════════════════════════════════
# O BANCO RESTAURADO TEM DE OPERAR — e as travas têm de MORDER
#
# Uma trava que veio no restauro mas não recusa nada é um desenho, não uma
# trava. Contá-las não chega: cada uma é MORDIDA, e a recusa do servidor é
# a prova.
# ═══════════════════════════════════════════════════════════════════════

MORDIDAS = {
    "CHECK forward_identificado_exige_identidade": f"""
      insert into public.raw_asset
        (run_id, storage_path, media_type, bytes, sha256, captured_at, preserved,
         storage_object_id, source_id, identity_state)
      values ('{RUN_CAPTURA}', '{MARCA}/MORDIDA/1', 'text/plain', 1, '{SHA_SINTETICO}',
        now(), true,
        (select id from public.storage_object where storage_path='{MARCA}/STORAGE/1'),
        'FONTE-DE-ENSAIO', 'FORWARD_IDENTIFIED');""",
    "PK sala_de_espera (run_id, ordem)": f"""
      insert into public.sala_de_espera
        (run_id, ordem, item_id, universo, texto, source_id, source_location,
         fact_location, fact_time, captured_at, admitido_por, corrida_sha256)
      values ('{RUN_DERIVACAO}', 0, 'colisao', 'ENSAIO', 'x', 'F', 'NAO SEI',
              'NAO SEI', 'NAO SEI', 'x', 'ensaio', '{SHA_SINTETICO}');""",
    "FK sala_de_espera -> collection_run": f"""
      insert into public.sala_de_espera
        (run_id, ordem, item_id, universo, texto, source_id, source_location,
         fact_location, fact_time, captured_at, admitido_por, corrida_sha256)
      values ('CORRIDA-QUE-NAO-EXISTE', 0, 'x', 'ENSAIO', 'x', 'F', 'NAO SEI',
              'NAO SEI', 'NAO SEI', 'x', 'ensaio', '{SHA_SINTETICO}');""",
    "FK sala_de_espera -> raw_asset": f"""
      insert into public.sala_de_espera
        (run_id, ordem, item_id, raw_observation_id, universo, texto, source_id,
         source_location, fact_location, fact_time, captured_at, admitido_por,
         corrida_sha256)
      values ('{RUN_CAPTURA}', 77, 'x', 999999999, 'ENSAIO', 'x', 'F', 'NAO SEI',
              'NAO SEI', 'NAO SEI', 'x', 'ensaio', '{SHA_SINTETICO}');""",
    "CHECK consumo_diz_quem_e_quando": f"""
      update public.sala_de_espera set estado_da_fila='CONSUMED'
       where run_id='{RUN_CAPTURA}' and ordem=0;""",
    "CHECK corrida_sha_tem_formato": f"""
      insert into public.sala_de_espera
        (run_id, ordem, item_id, universo, texto, source_id, source_location,
         fact_location, fact_time, captured_at, admitido_por, corrida_sha256)
      values ('{RUN_CAPTURA}', 88, 'x', 'ENSAIO', 'x', 'F', 'NAO SEI',
              'NAO SEI', 'NAO SEI', 'x', 'ensaio', 'nao-e-um-sha');""",
    "PK participacao_na_derivacao": f"""
      insert into public.participacao_na_derivacao
        (raw_asset_id, derived_artifact_id, first_seen_derivation_run_id)
      values ((select id from public.raw_asset where storage_path='{MARCA}/RAW/1'),
              (select id from public.derived_artifact where storage_path='{MARCA}/DERIVED/1'),
              '{RUN_DERIVACAO}');""",
    "FK etapa_da_corrida -> collection_run": """
      insert into public.etapa_da_corrida (run_id, etapa, estado)
      values ('CORRIDA-QUE-NAO-EXISTE', 'RAW', 'PASS');""",
}


def as_travas_mordem(porta: int) -> dict:
    """Cada trava é provocada. `RECUSOU` é a resposta do servidor."""
    out = {}
    for nome, sql in MORDIDAS.items():
        r = q(porta, f"begin;\n{sql}\nrollback;", check=False)
        out[nome] = "RECUSOU" if r.startswith("__ERRO__") else "DEIXOU_PASSAR"
    return out


def opera_depois_do_restauro(porta: int) -> dict:
    """Quatro perguntas diferentes — e um restauro pode acertar em três."""
    alvo = url(porta)
    cadeia = sh(f"cd {RAIZ} && PATH={BIN}:$PATH bash motor/cadeia_canonica.sh "
                f"migrations {json.dumps(alvo)}", check=False)
    skips = len(re.findall(r"=SKIP \(ja no livro-razao\) HASH=MATCH", cadeia.stdout))
    reaplicadas = len(re.findall(r"^MIGRATION_\d+=PASS", cadeia.stdout, re.M))
    conf008 = sh(f"{BIN}/psql {json.dumps(alvo)} -v ON_ERROR_STOP=1 -q -f "
                 f"{RAIZ}/supabase/migrations/008_verificacao_pos_aplicacao.sql",
                 check=False)
    linhagem = q(porta, f"""
      select d.document_id
        from public.documento_estruturado d
        join public.derived_artifact da on da.id = d.derived_artifact_id
        join public.participacao_na_derivacao p on p.derived_artifact_id = da.id
        join public.raw_asset r on r.id = p.raw_asset_id
       where r.storage_path = '{MARCA}/RAW/1';""", so_leitura=True)
    corrida_da_aresta = q(porta, f"""
      select first_seen_derivation_run_id from public.participacao_na_derivacao p
        join public.raw_asset r on r.id = p.raw_asset_id
       where r.storage_path='{MARCA}/RAW/1';""", so_leitura=True)
    return {
        "CADEIA_CANONICA_EXIT": cadeia.returncode,
        "CADEIA_SKIP_HASH_MATCH": skips,
        "CADEIA_REAPLICADAS": reaplicadas,
        "CONFERENCIA_008": "PASS" if conf008.returncode == 0 else "FAIL",
        "LINHAGEM_LIDA_ATE_A_OBSERVACAO": linhagem,
        "CORRIDA_DA_ARESTA_E_A_DA_DERIVACAO":
            "SIM" if corrida_da_aresta == RUN_DERIVACAO else f"NAO({corrida_da_aresta})",
        "TRAVAS_MORDEM": as_travas_mordem(porta),
    }


def a_sessao_recusa_escrita(porta: int) -> str:
    """«Não houve conserto» é uma promessa. Isto é uma medição.

        PEDIR NÃO É OBTER.
    """
    r = q(porta, "begin read only;\ncreate table prova_de_escrita(x int);\ncommit;",
          check=False)
    return "SIM" if r.startswith("__ERRO__") else "NAO"


# ═══════════════════════════════════════════════════════════════════════
# A CONTRAPROVA — o verificador tem de ACUSAR
#
# Se o verificador aprovar um banco sabotado, ele não é um verificador: é
# um carimbo. Por isso cada sabotagem corre DENTRO de uma transacção que
# é desfeita a seguir — o DDL do PostgreSQL é transaccional, e assim a
# arena mede-se sem nunca ficar contaminada.
#
#     UM VERIFICADOR QUE NUNCA DIZ NÃO NÃO ESTÁ A VERIFICAR.
# ═══════════════════════════════════════════════════════════════════════

def secao_sob_sabotagem(porta: int, sabotagem: str, secao: str) -> str:
    """O valor de uma secção com a sabotagem aplicada — e desfeita a seguir."""
    sql = SECOES[secao] if secao in SECOES else None
    if sql is None:
        partes = []
        corpo = "begin;\n" + sabotagem + "\n"
        for nome, s in SENTINELAS.items():
            corpo += s + "\n"
        corpo += "rollback;"
        return sha("\n".join(
            f"{n}::{v}" for n, v in zip(
                SENTINELAS, q(porta, corpo, check=False).split("\n"))))
    return sha(q(porta, f"begin;\n{sabotagem}\n{sql}\nrollback;", check=False) or "(nulo)")


SABOTAGENS = {
    # nome do ataque            : (sql, seccao que TEM de mudar)
    "A07_schema_volta_dados_nao": (
        f"delete from public.sala_de_espera where run_id='{RUN_DERIVACAO}';", "LINHAS"),
    "A08_dados_voltam_travas_nao": (
        "alter table public.sala_de_espera drop constraint consumo_diz_quem_e_quando;",
        "TRAVAS"),
    "A09_contagens_iguais_linhas_erradas": (
        f"update public.sala_de_espera set texto='TEXTO TROCADO' "
        f"where run_id='{RUN_DERIVACAO}' and ordem=0;", "SENTINELAS"),
    "A10_restore_sem_migration_history": (
        "delete from public.schema_migracao where versao='031';", "LEDGER"),
    "A11_indice_ausente": (
        "drop index public.sala_pendentes_idx;", "INDICES"),

    "A13_fk_quebrada": (
        "alter table public.sala_de_espera drop constraint sala_de_espera_run_id_fkey;",
        "TRAVAS"),
    "A14_timezone_alterado": (
        "set local timezone = 'America/Sao_Paulo';", "AMBIENTE"),
    "A15_json_alterado": (
        f"update public.collection_run set input='{{\"outro\": 1}}'::jsonb "
        f"where run_id='{RUN_CAPTURA}';", "SENTINELAS"),
    "A16_owner_grant_diferente": (
        "revoke all on public.sala_de_espera from postgres;", "DONOS"),
    "A17_extensao_ausente": (
        "drop extension if exists plpgsql cascade;", "EXTENSOES"),
    "A18_restore_parcial_como_pass": (
        "drop table public.documento_estruturado cascade;", "TABELAS"),
    "A28_impressao_fraca": (
        f"update public.raw_asset set sha256='{'a'*64}' "
        f"where storage_path='{MARCA}/RAW/1';", "SENTINELAS"),
}


def contraprova(porta: int, referencia: dict[str, str]) -> dict:
    """Treze bancos errados. O verificador tem de recusar os treze."""
    out = {}
    for nome, (sql, secao) in SABOTAGENS.items():
        obtido = secao_sob_sabotagem(porta, sql, secao)
        acusou = obtido != referencia[secao]
        out[nome] = {"SECAO": secao, "VERIFICADOR": "ACUSOU" if acusou else "APROVOU_O_ERRADO"}
    # E a prova de que a arena NÃO ficou suja: a impressão dela tem de
    # continuar igual à do banco restaurado.
    out["ARENA_INTACTA_DEPOIS_DAS_SABOTAGENS"] = (
        "SIM" if impressao(porta)["_GLOBAL"] == referencia["_GLOBAL"] else "NAO")
    return out


# ═══════════════════════════════════════════════════════════════════════
# O RED TEAM — vinte e oito ataques
#
# Os que se executam, executam-se. Os que são de PORTÃO atacam a função
# `portao()` directamente, com entradas que a tentam fazer dizer PASS.
# ═══════════════════════════════════════════════════════════════════════

# URLs hostis: nenhuma pode servir de origem de backup nem de destino de
# restauro. Duas têm a forma real de uma DSN do Supabase, directa e por
# pooler — porque é essa a que um erro de copiar-colar produziria.
URLS_HOSTIS = [
    "postgresql://postgres:x@db.odhdwvugikjdvkapbowe.supabase.co:5432/postgres",
    "postgresql://postgres.odhdwvugikjdvkapbowe:x@aws-0-eu-west-1.pooler.supabase.com:6543/postgres",
    "postgresql://postgres:x@127.0.0.1.evil.example:5432/sintonia",
    "postgresql://postgres:x@localhost:5432/postgres_producao",
    "postgres://u:p@10.0.0.5:5432/sintonia",
    "postgresql://u:p@[::ffff:1.2.3.4]:5432/sintonia",
    "postgresql://u:p@LOCALHOST.supabase.co:5432/sintonia",
    "postgresql://u:p@supabase.co:5432/sintonia",
]


def portao(f: dict) -> str:
    """O portão é uma FUNÇÃO, e não uma frase.

    `PASS` exige todas as condições juntas. Nenhuma delas se compra com
    documentação, com nome de plano, nem com uma prova de outra classe ou
    de outra plataforma.
    """
    if f.get("RESTORE_EXECUTED") != "YES":
        return "BLOCKED"
    if f.get("RESTORE_VERIFIED") != "YES":
        return "BLOCKED"
    if f.get("DISPOSABLE_ONLY") != "YES":
        return "BLOCKED"
    if f.get("SAME_CLASS_RESTORE") != "YES":
        return "BLOCKED"
    # A linha que esta missão NÃO atravessa. Provar a classe não é provar
    # a plataforma, e nenhum documento oficial a atravessa por ela.
    if f.get("SAME_PLATFORM_RESTORE") != "YES":
        return "BLOCKED"
    if f.get("COUNTERPROOF_WORKS") != "YES":
        return "BLOCKED"
    if f.get("RED_TEAM_SURVIVORS") != 0:
        return "BLOCKED"
    return "PASS"


def mede_o_live() -> dict:
    """O LIVE, medido — e quando não dá para medir, declarado NOT_MEASURED.

    Nada aqui liga a lado nenhum. Mede-se o que esta sessão TEM: se existe
    credencial de gestão, se existe workflow que produza backup, se existe
    registo datado de um restauro. A resposta muda sozinha no dia em que
    algum destes aparecer — um veredito que obedecesse a quem o corre não
    seria um veredito.
    """
    credenciais = {
        nome: ("PRESENTE" if os.environ.get(nome) else "AUSENTE")
        for nome in ("SUPABASE_ACCESS_TOKEN", "SUPABASE_MANAGEMENT_TOKEN",
                     "SUPABASE_DB_URL", "SUPABASE_SERVICE_ROLE_KEY")
    }
    wf = sh(f"grep -rlE 'pg_basebackup|wal-g|pgbackrest|barman|supabase db dump' "
            f"{RAIZ}/.github/workflows/ 2>/dev/null || true", check=False)
    produz_backup = [Path(x).name for x in wf.stdout.split() if x]
    pode_gerir = any(v == "PRESENTE" for k, v in credenciais.items()
                     if k in ("SUPABASE_ACCESS_TOKEN", "SUPABASE_MANAGEMENT_TOKEN"))
    return {
        "CREDENCIAIS": credenciais,
        "WORKFLOW_QUE_PRODUZ_BACKUP": produz_backup or "NENHUM",
        "MANAGEMENT_API_ALCANCAVEL": "SIM" if pode_gerir else "NAO",
        "LIVE_READS": 0,
        "LIVE_WRITES": 0,
        "LIVE_DDL": 0,
        # Capacidade e prova são coisas diferentes, e ficam em grupos
        # diferentes de propósito.
        "LIVE_BACKUP_CAPABILITY": "PROVIDER_PHYSICAL (politica do plano Pro, lida em documentacao)",
        "LIVE_BACKUP_ENABLED": "NOT_MEASURED" if not pode_gerir else "MEDIR",
        "LIVE_BACKUP_EXISTS": "NOT_MEASURED" if not pode_gerir else "MEDIR",
        "PITR_STATUS": "NOT_MEASURED",
        "LATEST_BACKUP_AVAILABLE": "NOT_MEASURED",
        "RETENTION_WINDOW": "NOT_MEASURED",
        "RESTORE_MECHANISM_AVAILABLE": "NOT_MEASURED",
        "RESTORE_EXECUTED_NO_LIVE": "NO",
        "RESTORE_VERIFIED_NO_LIVE": "NO",
    }


def red_team(porta_arena_viva: int, referencia: dict, contra: dict,
             factos: dict) -> dict:
    """Vinte e oito ataques. Zero sobreviventes, ou o veredito não vale."""
    a: dict[str, dict] = {}

    def reg(n, desc, apanhado, como):
        a[n] = {"ATAQUE": desc, "RESULTADO": "APANHADO" if apanhado else "SOBREVIVEU",
                "COMO": como}

    # ── 1 · backup declarado mas inexistente ───────────────────────────
    v = sh(f"{BIN}/pg_verifybackup {BANCADA}/nao-existe", como_dono=True, check=False)
    reg("A01", "backup declarado mas inexistente", v.returncode != 0,
        "pg_verifybackup recusa um caminho que nao existe")

    # ── 2 · backup antigo demais / alvo fora da janela ─────────────────
    #
    # ⚠️ ESTE ATAQUE SOBREVIVEU À PRIMEIRA VERSÃO DESTA PROVA, e o que ele
    # ensinou vale mais do que o ataque:
    #
    #     O POSTGRESQL NÃO RECUSA UM ALVO ANTERIOR AO BACKUP.
    #
    # Pedir `recovery_target_time = 2020` não dá erro. O servidor atinge o
    # estado consistente, PROMOVE, escreve «database system is ready to
    # accept connections» e aceita ligações — entregando o banco no estado
    # do INÍCIO do backup, sem nunca dizer que não chegou onde lhe pediram.
    #
    #     EXIT 0 E «READY TO ACCEPT CONNECTIONS» NÃO SÃO PROVA DE QUE O
    #     RESTAURO CHEGOU AO INSTANTE PEDIDO.
    #
    # Quem confiasse no arranque do servidor levava um banco silenciosamente
    # atrasado para produção. Quem defende é a IMPRESSÃO: o marco pós-backup
    # só existe no WAL, e um restauro que parou cedo não o traz.
    destino = BANCADA / "arena-antiga"
    porta_a = PORTA_ARENA + 10
    restaura(destino, porta_a, factos["ALVO"], chave="time",
             valor="2020-01-01 00:00:00+00")
    sh(f"{BIN}/pg_ctl -D {destino} -l {BANCADA}/arena-antiga.log start -w -t 30",
       como_dono=True, check=False)
    promoveu = q(porta_a, "select 1;", banco="postgres", check=False) == "1"
    marco = q(porta_a, f"select count(*) from public.collection_run "
                       f"where run_id='{RUN_POS_BACKUP}';", check=False)
    impr = impressao(porta_a) if promoveu else {"_GLOBAL": "(nao arrancou)"}
    sh(f"{BIN}/pg_ctl -D {destino} stop -m immediate", como_dono=True, check=False)
    nota_a02 = {
        "SERVIDOR_PROMOVEU_COM_ALVO_IMPOSSIVEL": "SIM" if promoveu else "NAO",
        "MARCO_POS_BACKUP_PRESENTE": marco,
        "LICAO": "o arranque do servidor NAO e prova de que o alvo foi atingido",
    }
    reg("A02", "backup antigo demais / alvo fora da janela",
        marco == "0" and impr["_GLOBAL"] != referencia["_GLOBAL"],
        "o servidor PROMOVE na mesma; quem acusa e a impressao — o marco "
        "pos-backup, que so existe no WAL, nao volta")

    # ── 3 · PITR desabilitado (sem arquivo de WAL) ─────────────────────
    destino = BANCADA / "arena-sem-wal"
    (BANCADA / "arquivo-vazio").mkdir(exist_ok=True)
    _dono(BANCADA / "arquivo-vazio")
    restaura(destino, PORTA_ARENA + 11, factos["ALVO"])
    conf = (destino / "postgresql.conf")
    conf.write_text(conf.read_text().replace(
        f"cp {BANCADA}/arquivo/%f %p", f"cp {BANCADA}/arquivo-vazio/%f %p"))
    sh(f"{BIN}/pg_ctl -D {destino} -l {BANCADA}/arena-sem-wal.log start -w -t 30",
       como_dono=True, check=False)
    porta_b = PORTA_ARENA + 11
    promoveu_b = q(porta_b, "select 1;", banco="postgres", check=False) == "1"
    marco_b = q(porta_b, f"select count(*) from public.collection_run "
                         f"where run_id='{RUN_POS_BACKUP}';", check=False)
    impr_b = impressao(porta_b) if promoveu_b else {"_GLOBAL": "(nao arrancou)"}
    sh(f"{BIN}/pg_ctl -D {destino} stop -m immediate", como_dono=True, check=False)
    # `pg_basebackup -Xstream` mete o WAL MINIMO dentro do proprio backup. Um
    # arquivo vazio nao impede o arranque: impede CHEGAR AO ALVO. Sem PITR
    # ha snapshot, e um snapshot nao e o instante que se pediu.
    # E a resposta do servidor aqui e DIFERENTE da do A02 — medido, e a
    # diferenca importa mais do que o veredito:
    #
    #     ALVO À FRENTE DO WAL DISPONÍVEL  ->  FATAL, e NÃO promove.
    #     ALVO ATRÁS DO INÍCIO DO BACKUP   ->  PROMOVE, calado.
    #
    # O primeiro caso o servidor defende. O SEGUNDO NÃO — e é o segundo
    # que entrega um banco atrasado com cara de restauro bem-sucedido.
    reg("A03", "PITR desabilitado / arquivo de WAL vazio",
        (not promoveu_b) or (marco_b == "0"
                             and impr_b["_GLOBAL"] != referencia["_GLOBAL"]),
        "o servidor recusa promover — «recovery ended before configured "
        "recovery target was reached» — e, se promovesse, o marco pos-backup "
        "em falta fazia a impressao acusar")

    # ── 4 · credencial sem permissao ───────────────────────────────────
    reg("A04", "credencial sem permissao tratada como medicao",
        factos["LIVE"]["MANAGEMENT_API_ALCANCAVEL"] == "NAO"
        and factos["LIVE"]["PITR_STATUS"] == "NOT_MEASURED",
        "sem credencial de gestao a medicao devolve NOT_MEASURED, nao um palpite")

    # ── 5 · restore documentado mas nao executavel ─────────────────────
    reg("A05", "restore documentado tratado como restore executado",
        portao({**factos["PORTAO"], "RESTORE_EXECUTED": "NO"}) == "BLOCKED",
        "o portao exige RESTORE_EXECUTED=YES; documentacao nao o compra")

    # ── 6 · backup de versao PostgreSQL incompativel ───────────────────
    destino = BANCADA / "arena-versao"
    restaura(destino, PORTA_ARENA + 12, factos["ALVO"])
    (destino / "PG_VERSION").write_text("14\n")
    sh(f"{BIN}/pg_ctl -D {destino} -l {BANCADA}/arena-versao.log start -w -t 20",
       como_dono=True, check=False)
    vivo = q(PORTA_ARENA + 12, "select 1;", banco="postgres", check=False)
    sh(f"{BIN}/pg_ctl -D {destino} stop -m immediate", como_dono=True, check=False)
    reg("A06", "backup de versao PostgreSQL incompativel", vivo != "1",
        "PG_VERSION alterado para 14: o servidor 17 recusa arrancar")

    # ── 7 a 18, e 28 · as sabotagens, medidas pela contraprova ─────────
    mapa = {
        "A07": ("A07_schema_volta_dados_nao", "schema volta mas dados nao"),
        "A08": ("A08_dados_voltam_travas_nao", "dados voltam mas travas nao"),
        "A09": ("A09_contagens_iguais_linhas_erradas", "contagens iguais com linhas erradas"),
        "A10": ("A10_restore_sem_migration_history", "restore sem migration history"),
        "A11": ("A11_indice_ausente", "indice ausente"),
        "A13": ("A13_fk_quebrada", "FK quebrada"),
        "A14": ("A14_timezone_alterado", "timezone alterado"),
        "A15": ("A15_json_alterado", "JSON alterado"),
        "A16": ("A16_owner_grant_diferente", "owner/grant diferente"),
        "A17": ("A17_extensao_ausente", "extensao necessaria ausente"),
        "A18": ("A18_restore_parcial_como_pass", "restore parcial tratado como PASS"),
        "A28": ("A28_impressao_fraca", "impressao calculada de forma fraca"),
    }
    for cod, (chave, desc) in mapa.items():
        reg(cod, desc, contra[chave]["VERIFICADOR"] == "ACUSOU",
            f"seccao {contra[chave]['SECAO']} da impressao acusa a sabotagem")

    # ── 12 · sequence/identity errada ──────────────────────────────────
    #
    # Ataca a REGRA, e não a secção: `SEQUENCIAS` já não carrega o valor,
    # porque exigir igualdade nele reprovaria qualquer restauro físico
    # correcto (ver o comentário da secção). A regra é `>=` com tecto, e
    # tem de acusar nos DOIS sentidos — uma regra só com `>=` deixaria
    # passar a sequência disparada para a frente.
    #
    # ⚠️ E O ATAQUE É FEITO À FUNÇÃO, COM ENTRADAS SINTÉTICAS, DE PROPÓSITO.
    # `setval` NÃO é transaccional: um `begin … rollback` à volta dele não
    # o desfaz. Sabotar a sequência do banco restaurado para testar a regra
    # deixaria o banco sabotado depois do teste — e o veredito passaria a
    # ser sobre um banco que a própria prova estragou.
    #
    #     UM TESTE QUE CONTAMINA O QUE MEDE NÃO É UM TESTE.
    #
    # A primeira versão tentou o contrário e apanhou uma segunda lição de
    # borco: `raw_asset_id_seq` valia 1, e «pô-la em 1» não é pô-la para
    # trás. Uma sabotagem que não sabota mede o nada e diz PASS.
    base = dict(factos["SEQUENCIAS"]["VALORES_DEPOIS"])
    # A sequencia atacada tem de ter VALOR. A maioria das 64 nunca foi
    # chamada e vale `nulo` — atacar uma dessas media a ausencia, nao a
    # regra. (Foi o que a primeira tentativa fez, e o `ADIANTADA_DENTRO_DA
    # _FOLGA_APROVADA` veio `false` por comparar nulo com numero.)
    com_valor = sorted(k for k, (v, _) in base.items() if v is not None)
    if not com_valor:
        base = {"seq_de_ensaio": (100, 1)}
        com_valor = ["seq_de_ensaio"]
    nome0 = com_valor[0]
    v0, inc0 = base[nome0]
    atrasada = {**base, nome0: (v0 - 1 if v0 > 1 else 0, inc0)}
    adiantada = {**base, nome0: (v0 + FOLGA_DO_WAL * abs(inc0) + 1, inc0)}
    na_folga = {**base, nome0: (v0 + 1, inc0)}
    em_falta = {k: v for k, v in base.items() if k != nome0}
    detalhe12 = {
        "SEQUENCIA_ATACADA": nome0,
        "VALOR_DE_PARTIDA": v0,
        "ATRASADA_ACUSADA": sequencias_conferem(base, atrasada)["RESULTADO"] == "FAIL",
        "ADIANTADA_ALEM_DA_FOLGA_ACUSADA":
            sequencias_conferem(base, adiantada)["RESULTADO"] == "FAIL",
        "EM_FALTA_ACUSADA": sequencias_conferem(base, em_falta)["RESULTADO"] == "FAIL",
        # E a contraprova da contraprova: a regra tem de APROVAR o caso
        # legitimo. Uma regra que reprova tudo tambem nao verifica nada.
        "ADIANTADA_DENTRO_DA_FOLGA_APROVADA":
            sequencias_conferem(base, na_folga)["RESULTADO"] == "PASS",
        "IGUAL_APROVADA": sequencias_conferem(base, base)["RESULTADO"] == "PASS",
    }
    reg("A12", "sequence/identity errada", all(detalhe12[k] for k in (
            "ATRASADA_ACUSADA", "ADIANTADA_ALEM_DA_FOLGA_ACUSADA",
            "EM_FALTA_ACUSADA", "ADIANTADA_DENTRO_DA_FOLGA_APROVADA",
            "IGUAL_APROVADA")),
        "a regra acusa a sequencia atrasada (id duplicado a espera), a "
        "disparada alem de um bloco de WAL e a que desapareceu — e aprova "
        "o adiantamento legitimo, que e o que a torna uma regra e nao um nao")

    # ── 19 · rebuild por migrations chamado de restore ─────────────────
    reg("A19", "rebuild por migrations chamado de restore",
        factos["RESTAURO"]["CADEIA_REAPLICADAS"] == 0
        and factos["RESTAURO"]["CADEIA_SKIP_HASH_MATCH"] >= 29,
        "nenhuma migration correu para o banco voltar: 0 reaplicadas, "
        f"{factos['RESTAURO']['CADEIA_SKIP_HASH_MATCH']} SKIP HASH=MATCH")

    # ── 20 · pg_dump chamado de restore fisico ─────────────────────────
    reg("A20", "pg_dump chamado de restore fisico sem contrato",
        factos["BACKUP"]["BACKUP_CLASS"] == "PHYSICAL"
        and "basebackup" in factos["BACKUP"]["BACKUP_MECHANISM"].replace("_", "")
        and portao({**factos["PORTAO"], "SAME_CLASS_RESTORE": "NO"}) == "BLOCKED",
        "a classe e declarada e comparada; LOGICAL nao passa por PHYSICAL")

    # ── 21 · backup local tratado como backup gerenciado ───────────────
    reg("A21", "backup local tratado como backup gerenciado",
        factos["LIVE"]["LIVE_BACKUP_EXISTS"] == "NOT_MEASURED",
        "o backup desta bancada nao promove LIVE_BACKUP_EXISTS")

    # ── 22 · documento oficial tratado como prova de execucao ──────────
    reg("A22", "documentacao oficial tratada como prova de execucao",
        factos["LIVE"]["LIVE_BACKUP_CAPABILITY"].startswith("PROVIDER_PHYSICAL")
        and factos["LIVE"]["RESTORE_EXECUTED_NO_LIVE"] == "NO",
        "capacidade e prova vivem em campos diferentes, e so o segundo conta")

    # ── 23 · restore de banco local tratado como prova de Supabase ─────
    reg("A23", "restore de banco local tratado como prova de Supabase",
        portao({**factos["PORTAO"], "SAME_PLATFORM_RESTORE": "NO"}) == "BLOCKED"
        and factos["PORTAO"]["SAME_PLATFORM_RESTORE"] != "YES",
        "o portao exige SAME_PLATFORM_RESTORE=YES, e esta missao NAO o tem")

    # ── 24 · teste contra producao ─────────────────────────────────────
    recusadas = 0
    for u in URLS_HOSTIS:
        try:
            exige_morada_descartavel(u)
        except MoradaProibida:
            recusadas += 1
    reg("A24", "teste contra producao", recusadas == len(URLS_HOSTIS),
        f"{recusadas}/{len(URLS_HOSTIS)} URLs hostis recusadas antes de qualquer ligacao")

    # ── 25 · segredo a vazar para o log ────────────────────────────────
    texto = json.dumps(factos, default=str, ensure_ascii=False)
    padroes = [r"sbp_[A-Za-z0-9]{20,}", r"eyJ[A-Za-z0-9_\-]{20,}",
               r"postgres(ql)?://[^@\s\"]*:[^@\s\"]+@", r"service_role"]
    vazou = [p for p in padroes if re.search(p, texto)]
    reg("A25", "segredo a vazar para o log", not vazou,
        "nenhum padrao de segredo no relatorio; a DSN local nao leva senha")

    # ── 26 · recurso pago criado sem autorizacao ───────────────────────
    reg("A26", "recurso pago criado sem autorizacao",
        factos["CUSTO"]["RECURSO_PAGO_CRIADO"] == "NAO",
        "nenhum projeto, plano ou add-on foi criado; a bancada e local e gratuita")

    # ── 27 · restore termina mas a aplicacao liga ao banco errado ──────
    reg("A27", "restore termina mas a aplicacao liga ao banco errado",
        factos["IDENTIDADE"]["PRIMARIA_VIVA"] == "NAO"
        and factos["IDENTIDADE"]["PORTA_VERIFICADA"] == PORTA_RESTAURO
        and factos["IDENTIDADE"]["SYSTEM_IDENTIFIER_CONFERE"] == "SIM",
        "a primaria esta morta, a porta verificada e a do restauro, e o "
        "system_identifier do cluster lido bate com o do base backup")

    sobreviventes = [k for k, v in a.items() if v["RESULTADO"] != "APANHADO"]
    return {"ATAQUES": a, "RED_TEAM_ATTACKS": len(a),
            "RED_TEAM_SURVIVORS": len(sobreviventes), "SOBREVIVENTES": sobreviventes,
            "NOTA_APRENDIDA_NO_A02_E_A03": nota_a02,
            "DETALHE_DO_A12": detalhe12}


# ═══════════════════════════════════════════════════════════════════════
# A INTERRUPÇÃO — o que acontece se o restauro morrer a meio
#
# «E se falhar?» é a pergunta que nenhum runbook deve responder por
# suposição. Aqui ela é EXECUTADA: o servidor é morto com `-9` durante a
# reprodução do WAL, e a seguir pergunta-se se ele retoma.
# ═══════════════════════════════════════════════════════════════════════

def a_interrupcao(alvo: dict, referencia: dict) -> dict:
    destino = BANCADA / "arena-crash"
    porta = PORTA_ARENA + 20
    restaura(destino, porta, alvo)
    sh(f"{BIN}/pg_ctl -D {destino} -l {BANCADA}/arena-crash.log start",
       como_dono=True, check=False)
    time.sleep(0.4)
    pid_f = destino / "postmaster.pid"
    pid = pid_f.read_text().split("\n")[0] if pid_f.exists() else ""
    morto = False
    if pid:
        sh(f"kill -9 {pid}", check=False)
        morto = True
    time.sleep(1.5)
    # O estado intermedio: utilizavel ou bloqueado?
    intermedio = q(porta, "select 1;", banco="postgres", check=False)
    # E agora retoma-se, sem refazer nada e sem tocar no backup.
    t0 = time.monotonic()
    sh(f"{BIN}/pg_ctl -D {destino} -l {BANCADA}/arena-crash.log start -w -t 120",
       como_dono=True, check=False)
    for _ in range(240):
        if q(porta, "select pg_is_in_recovery();", banco="postgres", check=False) == "f":
            break
        time.sleep(0.5)
    segundos = round(time.monotonic() - t0, 2)
    igual = impressao(porta)["_GLOBAL"] == referencia["_GLOBAL"] if \
        q(porta, "select 1;", banco="postgres", check=False) == "1" else False
    sh(f"{BIN}/pg_ctl -D {destino} stop -m fast", como_dono=True, check=False)
    return {
        "MORTO_DURANTE_A_REPRODUCAO": "SIM" if morto else "NAO",
        "ESTADO_INTERMEDIO_UTILIZAVEL": "NAO" if intermedio != "1" else "SIM",
        "PODE_SER_RETOMADO": "SIM" if igual else "NAO",
        "PRECISA_REINICIAR_DO_ZERO": "NAO" if igual else "SIM",
        "SEGUNDOS_ATE_RETOMAR": segundos,
        "COMO_SABEMOS_QUE_TERMINOU":
            "pg_is_in_recovery() devolve `f` e o log diz «database system is ready "
            "to accept connections». Antes disso o servidor RECUSA ligacoes — o "
            "estado intermedio e bloqueado, nao meio-aberto.",
        "IMPRESSAO_IGUAL_A_DO_RESTAURO_LIMPO": "SIM" if igual else "NAO",
    }


# ═══════════════════════════════════════════════════════════════════════
# A CORRIDA
# ═══════════════════════════════════════════════════════════════════════

def main() -> int:
    r: dict = {"PROVA": "RECUPERACAO-FISICA-PROVADA-NO-POSTGRES",
               "MEDIDO_EM": agora()}
    derruba_tudo()

    # ── a bancada ──────────────────────────────────────────────────────
    nasce_primaria()
    r["BANCADA"] = {
        "POSTGRES_VERSION": q(PORTA_PRIMARIA, "show server_version;"),
        "DATA_CHECKSUMS": q(PORTA_PRIMARIA, "show data_checksums;"),
        "WAL_LEVEL": q(PORTA_PRIMARIA, "show wal_level;"),
        "ARCHIVE_MODE": q(PORTA_PRIMARIA, "show archive_mode;"),
        "DISPOSABLE_ONLY": "YES",
        "CORPUS_DO_LIVE_IMPORTADO": "NAO",
    }
    r["CADEIA"] = aplica_a_cadeia(PORTA_PRIMARIA)
    r["CADEIA"].update(aplica_031(PORTA_PRIMARIA))
    if r["CADEIA"]["MIGRATION_031"] != "PASS":
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 2

    # ── as sentinelas ──────────────────────────────────────────────────
    q(PORTA_PRIMARIA, SQL_SENTINELAS)
    q(PORTA_PRIMARIA, SQL_SENTINELAS_SALA)

    # ── o backup fisico ────────────────────────────────────────────────
    # Tirado AQUI, e nao depois: o que se escrever a seguir so existe no
    # WAL, e e isso que torna a impressao capaz de distinguir «reproduziu
    # o WAL» de «copiou os ficheiros».
    r["BACKUP"] = backup_fisico()

    # ── o marco que so vive no WAL ─────────────────────────────────────
    q(PORTA_PRIMARIA, SQL_MARCO_POS_BACKUP)
    r["SENTINELAS"] = {
        "SHA_DOS_BYTES_SINTETICOS": SHA_SINTETICO,
        "CORRIDAS": [RUN_CAPTURA, RUN_DERIVACAO, RUN_POS_BACKUP],
        "LINHAS_NA_SALA": q(PORTA_PRIMARIA,
                            f"select count(*) from public.sala_de_espera "
                            f"where run_id like '{MARCA}%';"),
        "MARCO_POS_BACKUP": RUN_POS_BACKUP,
        "PORQUE_O_MARCO_EXISTE":
            "escrito depois do base backup e antes do ponto de recuperacao. "
            "So existe no WAL. Se ele volta, o WAL foi reproduzido.",
    }

    # ── a impressao ANTES ──────────────────────────────────────────────
    antes = impressao(PORTA_PRIMARIA)
    r["IMPRESSAO_ANTES"] = antes
    seq_antes = valores_das_sequencias(PORTA_PRIMARIA)

    # ── o ponto de recuperacao ─────────────────────────────────────────
    alvo = marca_o_ponto_de_recuperacao()
    r["ALVO"] = alvo
    t_ponto = time.monotonic()

    # ── o desastre ─────────────────────────────────────────────────────
    r["DESASTRE"] = provoca_os_desastres()
    r["WAL_ARQUIVADO"] = sela_o_arquivo()
    rpo = round(time.monotonic() - t_ponto, 2)

    # ── o original desaparece ──────────────────────────────────────────
    r["DESTRUICAO_DO_ORIGINAL"] = destroi_a_primaria()

    # ── o restauro ─────────────────────────────────────────────────────
    destino = BANCADA / "restaurado"
    restaura(destino, PORTA_RESTAURO, alvo, chave="time")
    rto = liga_e_espera(destino, PORTA_RESTAURO, "restaurado.log")
    r["RESTORE"] = {
        "RESTORE_MECHANISM": "PITR: base backup fisico + restore_command + recovery_target_time",
        "RESTORE_EXECUTED": "YES",
        "RECOVERY_TARGET_USADO": "recovery_target_time",
        "EM_RECUPERACAO": q(PORTA_RESTAURO, "select pg_is_in_recovery();", banco="postgres"),
        "RESTORE_SEGUNDOS": rto,
    }

    # ── a impressao DEPOIS ─────────────────────────────────────────────
    depois = impressao(PORTA_RESTAURO)
    r["IMPRESSAO_DEPOIS"] = depois
    diferentes = [k for k in antes if k != "_GLOBAL" and antes[k] != depois[k]]
    r["SECOES_DIFERENTES"] = diferentes or "NENHUMA"

    # O valor das sequencias nao se compara por igualdade — compara-se pela
    # regra. Ver o comentario da seccao SEQUENCIAS.
    seq_depois = valores_das_sequencias(PORTA_RESTAURO)
    r["SEQUENCIAS"] = sequencias_conferem(seq_antes, seq_depois)
    r["SEQUENCIAS"]["VALORES_DEPOIS"] = seq_depois

    # E a prova de que o WAL foi MESMO reproduzido: o marco pos-backup, que
    # nao esta nos ficheiros copiados, tem de estar aqui.
    marco = q(PORTA_RESTAURO, f"select count(*) from public.collection_run "
                              f"where run_id='{RUN_POS_BACKUP}';", so_leitura=True)
    r["RESTORE"]["MARCO_POS_BACKUP_VOLTOU"] = "SIM" if marco == "1" else f"NAO({marco})"
    r["RESTORE"]["WAL_FOI_REPRODUZIDO"] = "SIM" if marco == "1" else "NAO"

    r["RESTORE"]["RESTORE_VERIFIED"] = (
        "YES" if not diferentes and r["SEQUENCIAS"]["RESULTADO"] == "PASS"
        and marco == "1" else "NO")

    # ── o banco restaurado OPERA ───────────────────────────────────────
    r["RESTAURO"] = opera_depois_do_restauro(PORTA_RESTAURO)
    r["RESTAURO"]["SESSAO_SO_LEITURA_RECUSA_ESCRITA"] = \
        a_sessao_recusa_escrita(PORTA_RESTAURO)
    r["RESTAURO"]["REPAROS_MANUAIS_ANTES_DA_CONFERENCIA"] = 0

    # ── ligamos ao banco certo? ────────────────────────────────────────
    sid_backup = sh(f"{BIN}/pg_controldata {BANCADA}/base | grep 'system identifier'",
                    como_dono=True, check=False).stdout.split(":")[-1].strip()
    sid_vivo = sh(f"{BIN}/pg_controldata {destino} | grep 'system identifier'",
                  como_dono=True, check=False).stdout.split(":")[-1].strip()
    viva = sh(f"{BIN}/pg_isready -h localhost -p {PORTA_PRIMARIA}", check=False)
    r["IDENTIDADE"] = {
        "PRIMARIA_VIVA": "NAO" if viva.returncode != 0 else "SIM",
        "PORTA_VERIFICADA": PORTA_RESTAURO,
        "SYSTEM_IDENTIFIER_DO_BACKUP": sid_backup,
        "SYSTEM_IDENTIFIER_DO_RESTAURADO": sid_vivo,
        "SYSTEM_IDENTIFIER_CONFERE": "SIM" if sid_backup and sid_backup == sid_vivo else "NAO",
    }

    # ── RTO e RPO, medidos ─────────────────────────────────────────────
    r["TEMPOS"] = {
        "DISPOSABLE_RTO_SEGUNDOS": rto,
        "DISPOSABLE_RPO_SEGUNDOS": rpo,
        "O_QUE_O_RPO_MEDE": "o intervalo entre o ponto de recuperacao e o "
                            "selamento do arquivo apos o desastre, NESTA bancada",
        "NAO_E_O_RTO_DO_LIVE": "o LIVE tem outro tamanho, outra rede e outro "
                               "orquestrador. Este numero e da bancada e so dela.",
    }

    # ── a contraprova ──────────────────────────────────────────────────
    r["CONTRAPROVA"] = contraprova(PORTA_RESTAURO, depois)
    aprovou_errado = [k for k, v in r["CONTRAPROVA"].items()
                      if isinstance(v, dict) and v["VERIFICADOR"] != "ACUSOU"]
    r["COUNTERPROOF_WORKS"] = "YES" if not aprovou_errado else "NO"

    # ── a interrupcao ──────────────────────────────────────────────────
    r["INTERRUPCAO"] = a_interrupcao(alvo, depois)

    # ── o LIVE, e o custo ──────────────────────────────────────────────
    r["LIVE"] = mede_o_live()
    r["CUSTO"] = {
        "RECURSO_PAGO_CRIADO": "NAO",
        "PROJETO_SUPABASE_DESCARTAVEL_CRIADO": "NAO",
        "PORQUE": "criar um projeto Supabase da mesma classe do LIVE exige plano "
                  "Pro, que e pago. Esta prova nao gasta, e por isso nao exerce a "
                  "PLATAFORMA.",
    }

    # ── o portao ───────────────────────────────────────────────────────
    r["PORTAO"] = {
        "RESTORE_EXECUTED": r["RESTORE"]["RESTORE_EXECUTED"],
        "RESTORE_VERIFIED": r["RESTORE"]["RESTORE_VERIFIED"],
        "DISPOSABLE_ONLY": "YES",
        "DISPOSABLE_BACKUP_CLASS": "PHYSICAL",
        "LIVE_BACKUP_CLASS": "PHYSICAL",
        "SAME_CLASS_RESTORE": "YES",
        # A linha que esta missao NAO atravessa, e que o A23 defende.
        "SAME_PLATFORM_RESTORE": "NO",
        "COUNTERPROOF_WORKS": r["COUNTERPROOF_WORKS"],
        "RED_TEAM_SURVIVORS": 0,
    }
    rt = red_team(PORTA_RESTAURO, depois, r["CONTRAPROVA"], r)
    r["RED_TEAM"] = rt
    r["PORTAO"]["RED_TEAM_SURVIVORS"] = rt["RED_TEAM_SURVIVORS"]

    r["VEREDITO"] = {
        "PHYSICAL_CLASS_RESTORE":
            "PASS" if (r["RESTORE"]["RESTORE_VERIFIED"] == "YES"
                       and r["COUNTERPROOF_WORKS"] == "YES") else "FAIL",
        "SAME_CLASS_RESTORE": "YES",
        "SAME_PLATFORM_RESTORE": "NO",
        "PLATFORM_RESTORE_EXERCISED": "NO",
        "RESTORE_PROOF": portao(r["PORTAO"]),
        "BLOCKER": ("PLATFORM_RESTORE_NOT_EXERCISED"
                    if portao(r["PORTAO"]) != "PASS" else "NENHUM"),
        "LIVE_WRITES": 0, "LIVE_DDL": 0, "LIVE_READS": 0,
        "MIGRATION_031_APPLIED_NO_LIVE": "NO",
    }

    saida = RAIZ / "provas" / "RECUPERACAO-FISICA-MEDIDA.json"
    saida.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(r["VEREDITO"], indent=2, ensure_ascii=False))
    print(f"\nrelatorio completo -> {saida.relative_to(RAIZ)}")
    print(f"SECOES_DIFERENTES = {r['SECOES_DIFERENTES']}")
    print(f"RED_TEAM = {rt['RED_TEAM_ATTACKS']} ataques, "
          f"{rt['RED_TEAM_SURVIVORS']} sobreviventes {rt['SOBREVIVENTES']}")
    print(f"SEQUENCIAS = {r['SEQUENCIAS']['RESULTADO']} "
          f"({r['SEQUENCIAS']['SEQUENCIAS_CONFERIDAS']} conferidas)")
    print(f"WAL_FOI_REPRODUZIDO = {r['RESTORE']['WAL_FOI_REPRODUZIDO']}")
    ok = (r["RESTORE"]["RESTORE_VERIFIED"] == "YES"
          and r["COUNTERPROOF_WORKS"] == "YES"
          and rt["RED_TEAM_SURVIVORS"] == 0)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
