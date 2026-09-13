#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RECUPERAÇÃO PROVADA — um backup que VOLTA, num Postgres que morre no fim.

O QUE ISTO PROVA
----------------
Que a casa sabe **restaurar**, e não apenas que existe um ficheiro chamado
backup. São duas frases diferentes, e a distância entre elas é o gate:

    BACKUP EXISTE  !=  RESTORE PROVADO

A prova corre inteira num PostgreSQL 16 **descartável e local**. Ela constrói
uma bancada pela cadeia canónica, escreve sentinelas **sintéticas**, tira a
impressão do que lá está, faz o backup, **destrói o banco de propósito**,
restaura num banco **vazio**, e volta a tirar a impressão. As duas impressões
têm de bater — sem um único conserto à mão.

    RESTAURAR POR CIMA DO QUE AINDA EXISTE NÃO PROVA NADA.
    Se o original continuar de pé, uma tabela que o restore não trouxe
    continua lá, e o verde é do banco antigo, não do backup.

O QUE ISTO **NÃO** PROVA
------------------------
Que o LIVE é recuperável. O mecanismo aqui é `pg_dump`/`pg_restore` — backup
**lógico**. O mecanismo de backup do LIVE não está medido (não há credencial
de gestão nesta casa: nenhum workflow pede `SUPABASE_ACCESS_TOKEN`, e o único
segredo de banco que existe, `SUPABASE_DB_URL`, fala com o banco e não com a
API que sabe de backups).

    MECANISMO DIFERENTE CHAMADO DE EQUIVALENTE É UM VERDE FALSO.

Por isso o veredito publica `SAME_CLASS_AS_LIVE_BACKUP` **separado** de
`DISPOSABLE_RESTORE`, e a função do portão recusa-se a devolver `PASS`
enquanto o primeiro não for `YES`. O ataque 15 do red team é exactamente
esse, e ele corre.

NENHUMA LIGAÇÃO A PRODUÇÃO
--------------------------
A trava é a mesma da casa (`provas/preservar_coleta_no_postgres.py`): a URL é
**decomposta**, e exige-se `hostname` exactamente local **e** nome de banco
numa lista curta de permissão. A lista é própria desta prova — alargar a de
lá para caber aqui seria afrouxar uma trava alheia por conveniência.

    LIVE_WRITES_PERFORMED = 0, por construção: não há URL de produção neste
    ficheiro, e a que vier de fora é recusada antes de qualquer ligação.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlparse, urlunparse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# OS DOIS ARTEFATOS CANONICOS DE QUE ESTA PROVA DEPENDE, e o caminho vai
# inteiro num literal so de proposito: e dessa linha que o System Map tira
# a prova da ligacao. Partido em `("motor", "cadeia_canonica.sh")` o
# scanner ainda acha o ficheiro pelo nome, mas ja nao consegue dizer que
# esta prova o CORRE — e uma aresta que ninguem consegue provar vira NAO SEI.
CADEIA_CANONICA = os.path.join(RAIZ, "motor/cadeia_canonica.sh")
VERIFICACAO_008 = os.path.join(
    RAIZ, "supabase/migrations/008_verificacao_pos_aplicacao.sql")

# ─────────────────────────────────────────────────────────────────────────
# A · A TRAVA — e ela decompõe a URL, não procura pedaços de texto
# ─────────────────────────────────────────────────────────────────────────
HOSTS_LOCAIS = ("localhost", "127.0.0.1", "::1", "[::1]")

# Os únicos nomes de banco que ESTA prova aceita. Lista de PERMISSÃO: bloqueio
# falha por omissão (basta esquecer um nome), permissão falha fechado.
#
#   recuperacao           a bancada que se constrói e se destrói
#   recuperacao_vazia     o destino vazio do restore
#   recuperacao_ataque    a arena do red team, criada e deitada fora a cada ataque
#   postgres              só para `create database` / `drop database`
BANCOS_PERMITIDOS = ("recuperacao", "recuperacao_vazia", "recuperacao_ataque",
                     "postgres")


def e_descartavel(url):
    """`hostname` exactamente local **e** banco na lista curta.

    Procurar a palavra `localhost` dentro da URL não é uma trava: um servidor
    chamado `localhost.atacante.example` contém-na. Comparar pedaços de texto
    onde se devia comparar estrutura é conferir um passaporte pelas letras.
    """
    try:
        u = urlparse(url or "")
    except ValueError:
        return False
    if u.scheme not in ("postgres", "postgresql"):
        return False
    if (u.hostname or "").lower() not in HOSTS_LOCAIS:
        return False
    return (u.path or "").lstrip("/") in BANCOS_PERMITIDOS


def exigir_descartavel(url, para_que):
    if not e_descartavel(url):
        raise SystemExit(
            "RECUSADO (%s): o endereço não é um banco descartável local. "
            "Esta prova nunca corre contra produção." % para_que)
    return url


def com_banco(url, nome):
    """A mesma URL, outro banco. Sem reconstruir texto à mão."""
    u = urlparse(url)
    return urlunparse(u._replace(path="/" + nome))


# ─────────────────────────────────────────────────────────────────────────
# B · FALAR COM O BANCO
# ─────────────────────────────────────────────────────────────────────────
def psql(url, sql, ro=False):
    """Devolve (ok, texto, erro). `ro=True` fecha a sessão em `begin read only`.

    A sessão só-leitura não é cerimónia: é o que prova que a conferência do
    banco restaurado **não pode** ter consertado nada pelo caminho.
    """
    exigir_descartavel(url, "ligação")
    # O `;` e obrigatorio: sem ele o `commit` cola-se ao fim da consulta
    # e o servidor le `order by 1 commit`, que nao e SQL nenhum.
    corpo = ("begin read only;\n%s;\ncommit;\n" % sql.strip().rstrip(";")) \
        if ro else sql
    p = subprocess.run(["psql", url, "-v", "ON_ERROR_STOP=1", "-tAq", "-f", "-"],
                       input=corpo, capture_output=True, text=True)
    return p.returncode == 0, p.stdout, p.stderr


def linhas(url, sql, ro=False):
    ok, saida, err = psql(url, sql, ro)
    if not ok:
        raise SystemExit("consulta falhou: %s\n%s" % (sql[:80], err[:400]))
    return [l for l in saida.splitlines() if l != ""]


def um(url, sql, ro=False):
    r = linhas(url, sql, ro)
    return r[0] if r else None


def admin_de(url):
    return com_banco(url, "postgres")


def cria_banco(url, nome):
    a = admin_de(url)
    psql(a, "drop database if exists %s;" % nome)
    ok, _, err = psql(a, "create database %s;" % nome)
    if not ok:
        raise SystemExit("não consegui criar %s: %s" % (nome, err[:200]))


def derruba_banco(url, nome):
    a = admin_de(url)
    # Sessões abertas impedem o DROP, e um DROP que não acontece deixaria o
    # original de pé — que é exactamente o que esta prova não pode permitir.
    psql(a, "select pg_terminate_backend(pid) from pg_stat_activity "
            "where datname='%s' and pid <> pg_backend_pid();" % nome)
    ok, _, err = psql(a, "drop database if exists %s;" % nome)
    if not ok:
        raise SystemExit("não consegui destruir %s: %s" % (nome, err[:200]))


def banco_existe(url, nome):
    return um(admin_de(url),
              "select count(*) from pg_database where datname='%s'" % nome) == "1"


# ─────────────────────────────────────────────────────────────────────────
# C · A BANCADA — cadeia canónica, e nenhum segundo aplicador
# ─────────────────────────────────────────────────────────────────────────
# Bytes SINTÉTICOS. Nenhum corpus real é copiado para esta bancada: copiar
# produção para fora também é uma operação de dados, e esta missão não tem
# autorização para a fazer.
BYTES_SINTETICOS = b"SINTONIA RECOVERY TEST :: bytes sinteticos, nenhum corpus real\n"
BYTES_DERIVADOS = b"SINTONIA RECOVERY TEST :: texto derivado sintetico\n"
SHA_RAW = hashlib.sha256(BYTES_SINTETICOS).hexdigest()
SHA_DERIVADO = hashlib.sha256(BYTES_DERIVADOS).hexdigest()
SHA_PARAMETROS = hashlib.sha256(b"{}").hexdigest()
TEXTO_SINTETICO = "RECOVERY_TEST_TEXTO sintetico para a prova de restauro."
HASH_TEXTO = hashlib.sha256(TEXTO_SINTETICO.encode()).hexdigest()

RUN_CAPTURA = "RECOVERY_TEST_RUN"
RUN_DERIVACAO = "RECOVERY_TEST_RUN_DERIV"
CAMINHO_OBJETO = "RECOVERY_TEST_STORAGE/%s.bin" % SHA_RAW[:16]
CAMINHO_DERIVADO = "RECOVERY_TEST_DERIVED/%s.txt" % SHA_DERIVADO[:16]

TABELAS_DA_COLLECTION = (
    "collection_run", "storage_object", "raw_asset", "derived_artifact",
    "etapa_da_corrida", "participacao_na_derivacao", "documento_estruturado",
    "schema_migracao",
)


def aplica_cadeia(url):
    """O aplicador canónico, e mais nenhum. Um segundo aplicador seria um
    segundo dono da mesma lei, e a partir daí nenhuma das duas vale."""
    exigir_descartavel(url, "cadeia de migrations")
    p = subprocess.run(["bash", CADEIA_CANONICA, "migrations", url],
                       capture_output=True, text=True)
    return p.returncode, p.stdout


def confere_008(url):
    """A 008 confere, não cria. Falha dela é falha de conferência."""
    exigir_descartavel(url, "conferência 008")
    p = subprocess.run(["psql", url, "-v", "ON_ERROR_STOP=1", "-q", "-f",
                        VERIFICACAO_008], capture_output=True, text=True)
    return p.returncode == 0


def escreve_sentinelas(url):
    """Dados sintéticos identificáveis, com relações suficientes para que
    PK · FK · UNIQUE · CHECK tenham o que provar depois do restauro.

    A corrida que CAPTURA não é a que DERIVA — e isso é de propósito: é a
    distinção que a `029` mede, e uma restauração que as confundisse passaria
    despercebida se a bancada só tivesse uma corrida.
    """
    sql = """
    insert into public.collection_run (run_id, platform, started_at,
      rule_version, status, source_country)
      values ('{rc}','recovery-test',now(),'v1','concluida','IT'),
             ('{rd}','recovery-test',now(),'v1','concluida','IT');

    insert into public.storage_object (storage_path, media_type, bytes, sha256)
      values ('{cam}','application/octet-stream',{n},'{sha}');

    insert into public.raw_asset (run_id, storage_path, media_type, bytes,
      sha256, captured_at, storage_object_id, source_id, document_key,
      document_key_basis, identity_state)
      select '{rc}','{cam}','application/octet-stream',{n},'{sha}',now(),
             o.id,'RECOVERY_TEST_SOURCE','RECOVERY-TEST-DOC-1',
             'SOURCE_DOCUMENT_ID','FORWARD_IDENTIFIED'
        from public.storage_object o where o.storage_path='{cam}';

    insert into public.derived_artifact (raw_asset_id, parent_sha256, kind,
      producer, producer_version, parameters_hash, sha256, bytes, media_type,
      storage_path, derived_at)
      select r.id,'{sha}','TEXT_EXTRACTION','recovery-test','1',
             '{shap}','{shad}',{nd},'text/plain','{camd}',now()
        from public.raw_asset r where r.storage_path='{cam}';

    insert into public.participacao_na_derivacao (raw_asset_id,
      derived_artifact_id, first_seen_derivation_run_id)
      select r.id, d.id, '{rd}'
        from public.raw_asset r, public.derived_artifact d
       where r.storage_path='{cam}' and d.storage_path='{camd}';

    insert into public.documento_estruturado (derived_artifact_id, run_id,
      source_id, texto, hash_texto, document_id)
      select d.id,'{rd}','RECOVERY_TEST_SOURCE','{txt}','{ht}',
             'RECOVERY-TEST-DOC-1'
        from public.derived_artifact d where d.storage_path='{camd}';

    insert into public.etapa_da_corrida (run_id, etapa, tentativa, estado,
      input_grain, input_count, output_grain, output_count, passed,
      raw_asset_id)
      select '{rc}','RAW',0,'PASS','OBSERVACAO',1,'OBSERVACAO',1,1, r.id
        from public.raw_asset r where r.storage_path='{cam}';
    """.format(rc=RUN_CAPTURA, rd=RUN_DERIVACAO, cam=CAMINHO_OBJETO,
               camd=CAMINHO_DERIVADO, sha=SHA_RAW, shad=SHA_DERIVADO,
               shap=SHA_PARAMETROS, n=len(BYTES_SINTETICOS),
               nd=len(BYTES_DERIVADOS), txt=TEXTO_SINTETICO, ht=HASH_TEXTO)
    ok, _, err = psql(url, sql)
    if not ok:
        raise SystemExit("sentinelas não entraram: %s" % err[:600])


# ─────────────────────────────────────────────────────────────────────────
# D · A IMPRESSÃO — o que tem de voltar igual
# ─────────────────────────────────────────────────────────────────────────
# Sete perguntas, e não uma. Um restauro pode acertar numa e falhar noutra,
# e um número só não distingue «o schema voltou» de «os dados voltaram».
LISTA = "','".join(TABELAS_DA_COLLECTION)

CONSULTAS = {
    "TABELAS": """
      select c.relname from pg_class c join pg_namespace n on n.oid=c.relnamespace
       where n.nspname='public' and c.relkind='r' order by c.relname""",
    "LEDGER": """
      select versao || '|' || resultado || '|' || sha256
        from public.schema_migracao order by versao""",
    "TRAVAS": """
      select rel.relname || '|' || con.conname || '|' || con.contype::text || '|' ||
             pg_get_constraintdef(con.oid)
        from pg_constraint con join pg_class rel on rel.oid=con.conrelid
        join pg_namespace n on n.oid=rel.relnamespace
       where n.nspname='public' and rel.relname in ('%s')
       order by 1""" % LISTA,
    "INDICES": """
      select tablename || '|' || indexname || '|' || indexdef
        from pg_indexes where schemaname='public' and tablename in ('%s')
       order by 1""" % LISTA,
    "SEQUENCIAS": """
      select c.relname || '|' || coalesce(s.last_value::text,'NULL')
        from pg_class c join pg_namespace n on n.oid=c.relnamespace
        left join pg_sequences s on s.schemaname=n.nspname and s.sequencename=c.relname
       where n.nspname='public' and c.relkind='S' order by 1""",
    "SENTINELAS": """
      select 'RUN|' || run_id || '|' || status::text || '|' || source_country::text
        from public.collection_run where run_id like 'RECOVERY_TEST%'
      union all
      select 'OBJ|' || id::text || '|' || storage_path || '|' || sha256 || '|' || bytes::text
        from public.storage_object where storage_path like 'RECOVERY_TEST%'
      union all
      select 'RAW|' || id::text || '|' || run_id || '|' || sha256 || '|' ||
             coalesce(document_key,'-') || '|' || identity_state || '|' ||
             coalesce(storage_object_id::text,'-')
        from public.raw_asset where storage_path like 'RECOVERY_TEST%'
      union all
      select 'DER|' || id::text || '|' || raw_asset_id::text || '|' ||
             parent_sha256 || '|' || sha256 || '|' || kind
        from public.derived_artifact where storage_path like 'RECOVERY_TEST%'
      union all
      select 'PAR|' || raw_asset_id::text || '|' || derived_artifact_id::text ||
             '|' || first_seen_derivation_run_id
        from public.participacao_na_derivacao
      union all
      select 'DOC|' || derived_artifact_id::text || '|' || run_id || '|' ||
             source_id || '|' || hash_texto || '|' || coalesce(document_id,'-')
        from public.documento_estruturado
      union all
      select 'ETP|' || id::text || '|' || run_id || '|' || etapa::text || '|' ||
             estado::text || '|' || coalesce(raw_asset_id::text,'-')
        from public.etapa_da_corrida where run_id like 'RECOVERY_TEST%'
      order by 1""",
}

# `LINHAS` acima ficou torta com o `values` de sobra; escrita direta é mais
# honesta do que um truque de SQL que ninguém consegue reler.
CONSULTAS["LINHAS"] = "\nunion all\n".join(
    "select '%s=' || (select count(*) from public.%s)::text" % (t, t)
    for t in TABELAS_DA_COLLECTION) + "\norder by 1"


def impressao(url, ro=False):
    """As sete secções, cada uma com o seu sha. Um total só esconderia QUAL
    delas mudou — e saber qual é metade do diagnóstico."""
    secoes = {}
    for nome, sql in CONSULTAS.items():
        corpo = "\n".join(linhas(url, sql, ro))
        secoes[nome] = (hashlib.sha256(corpo.encode()).hexdigest(), corpo)
    total = hashlib.sha256(
        "".join("%s:%s\n" % (n, secoes[n][0]) for n in sorted(secoes)).encode()
    ).hexdigest()
    return total, secoes


def compara(antes, depois):
    """Devolve a lista de secções diferentes. Vazia é a única resposta que
    autoriza dizer que o banco voltou."""
    return [n for n in sorted(antes[1]) if antes[1][n][0] != depois[1][n][0]]


# ─────────────────────────────────────────────────────────────────────────
# E · O BACKUP E O RESTORE
# ─────────────────────────────────────────────────────────────────────────
def faz_backup(url, destino):
    exigir_descartavel(url, "backup")
    p = subprocess.run(["pg_dump", "--format=custom", "--file=" + destino, url],
                       capture_output=True, text=True)
    return p.returncode, p.stderr


def integridade_do_backup(caminho):
    """`pg_restore --list` lê o índice do arquivo. Um ficheiro que não é um
    arquivo, ou está truncado no cabeçalho, morre aqui — antes de tocar num
    banco."""
    if not os.path.exists(caminho) or os.path.getsize(caminho) == 0:
        return False, 0
    p = subprocess.run(["pg_restore", "--list", caminho],
                       capture_output=True, text=True)
    entradas = len([l for l in p.stdout.splitlines()
                    if l and not l.startswith(";")])
    return p.returncode == 0 and entradas > 0, entradas


def restaura(url, caminho, lista_toc=None):
    exigir_descartavel(url, "restauro")
    cmd = ["pg_restore", "--dbname=" + url, "--exit-on-error"]
    if lista_toc:
        cmd += ["--use-list=" + lista_toc]
    cmd.append(caminho)
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stderr


def esta_vazio(url):
    """Zero tabelas em `public`. Restaurar por cima de um banco que ainda tem
    coisas é medir o banco antigo e chamar-lhe backup."""
    return um(url, "select count(*) from pg_class c join pg_namespace n "
                   "on n.oid=c.relnamespace where n.nspname='public' "
                   "and c.relkind='r'") == "0"


def sessao_so_leitura_morde(url):
    """`begin read only` é PEDIDO; a recusa do servidor é OBTIDO. Sem esta
    prova, a impressão do restaurado podia ter vindo de uma sessão que
    escrevia — e aí «não houve conserto» seria uma promessa, não uma medição."""
    ok, _, err = psql(url, "begin read only;\ncreate table proibido_(x int);\n")
    return (not ok) and "read-only" in err.lower()


# ─────────────────────────────────────────────────────────────────────────
# F · O PORTÃO — a função que decide, e que o red team ataca
# ─────────────────────────────────────────────────────────────────────────
def portao(backup_source_for_live, restore_mechanism, same_class_restore,
           disposable_restore, live_writes):
    """Devolve (RECOVERY_GATE, LIVE_READY_FOR_APPLY).

    `PASS` é o ÚLTIMO recurso, nunca o estado por omissão. `BLOCKED` é um
    resultado válido: quer dizer «medi, e falta prova» — que é diferente de
    «medi, e está partido» (`FAIL`).

        UM BLOQUEIO MEDIDO HONESTAMENTE NÃO É UMA FALHA DA MISSÃO.
        UM VERDE SEM AS CINCO PROVAS É UMA MENTIRA DA MISSÃO.
    """
    if disposable_restore != "PASS":
        return "FAIL", "NO"
    if live_writes != 0:
        return "FAIL", "NO"
    cinco = (backup_source_for_live == "PROVEN"
             and restore_mechanism == "PROVEN"
             and same_class_restore == "YES"
             and disposable_restore == "PASS"
             and live_writes == 0)
    if cinco:
        return "PASS", "YES"
    return "BLOCKED", "NO"


# ─────────────────────────────────────────────────────────────────────────
# G · O RED TEAM — vinte ataques, e cada um tem de ser apanhado
# ─────────────────────────────────────────────────────────────────────────
URLS_HOSTIS = (
    "postgresql://postgres:x@db.abcdefghijklmnop.supabase.co:5432/postgres",
    "postgresql://postgres.abcd:x@aws-0-eu-central-1.pooler.supabase.com:6543/postgres",
    "postgresql://alguem@localhost.atacante.example:5432/recuperacao",
    "postgresql://alguem@db:5432/recuperacao",
    "postgresql://alguem@127.0.0.1:5432/producao",
    "postgresql://alguem@127.0.0.1:5432/postgres_producao",
    "postgres://alguem@[::2]:5432/recuperacao",
    "",
)


def _arena(url, dump, toc=None):
    """Um banco novo, restaurado do mesmo backup, para sabotar à vontade.
    Sabotar o banco restaurado de verdade contaminaria o veredito."""
    cria_banco(url, "recuperacao_ataque")
    a = com_banco(url, "recuperacao_ataque")
    saida, _ = restaura(a, dump, toc)
    return a, saida


def red_team(url, dump, dump_so_schema, impressao_boa, tmp):
    """Cada ataque devolve (id, nome, APANHADO|SOBREVIVEU, como foi apanhado)."""
    r = []

    def anota(ident, nome, apanhado, como):
        r.append((ident, nome, "APANHADO" if apanhado else "SOBREVIVEU", como))

    # ── 01 · backup inexistente ────────────────────────────────────────
    falso = os.path.join(tmp, "nao-existe.dump")
    ok_int, _ = integridade_do_backup(falso)
    anota("A01", "backup inexistente", not ok_int,
          "integridade recusa ficheiro que não existe")

    # ── 02 · backup vazio ─────────────────────────────────────────────
    vazio = os.path.join(tmp, "vazio.dump")
    open(vazio, "wb").close()
    ok_int, _ = integridade_do_backup(vazio)
    anota("A02", "backup vazio", not ok_int, "integridade recusa 0 bytes")

    # ── 03 · backup truncado ──────────────────────────────────────────
    trunc = os.path.join(tmp, "truncado.dump")
    bruto = open(dump, "rb").read()
    open(trunc, "wb").write(bruto[:int(len(bruto) * 0.6)])
    ok_int, _ = integridade_do_backup(trunc)
    saida_t = 0
    if ok_int:
        a, saida_t = _arena(url, trunc)
        derruba_banco(url, "recuperacao_ataque")
    anota("A03", "backup truncado", (not ok_int) or saida_t != 0,
          "integridade recusa" if not ok_int else "pg_restore sai %d" % saida_t)

    # ── 04 · backup de versão PostgreSQL incompatível ─────────────────
    # Não se finge com um comentário: mexe-se no cabeçalho do arquivo, que é
    # onde a versão vive de verdade (`PGDMP` + vmaj/vmin/vrev).
    outra = os.path.join(tmp, "outra-versao.dump")
    b = bytearray(bruto)
    b[5] = 99
    open(outra, "wb").write(bytes(b))
    ok_int, _ = integridade_do_backup(outra)
    anota("A04", "backup de versao PostgreSQL incompativel", not ok_int,
          "pg_restore recusa o cabecalho 99.x")

    # ── 05 · schema restaura mas dados nao ────────────────────────────
    a, saida = _arena(url, dump_so_schema)
    dif = compara(impressao_boa, impressao(a, ro=True))
    derruba_banco(url, "recuperacao_ataque")
    anota("A05", "schema restaura mas dados nao",
          saida == 0 and ("LINHAS" in dif or "SENTINELAS" in dif),
          "restore sai 0 e a impressao difere em %s" % ",".join(dif))

    # ── 06 · dados restauram mas o ledger nao ─────────────────────────
    # O TOC do arquivo é filtrado: tudo entra menos as LINHAS do livro-razão.
    toc_bruto = subprocess.run(["pg_restore", "--list", dump],
                               capture_output=True, text=True).stdout
    toc = os.path.join(tmp, "sem-ledger.toc")
    with open(toc, "w") as f:
        for l in toc_bruto.splitlines():
            if "TABLE DATA" in l and "schema_migracao" in l:
                f.write(";" + l + "\n")
            else:
                f.write(l + "\n")
    a, saida_06 = _arena(url, dump, toc)
    dif_06 = compara(impressao_boa, impressao(a, ro=True))
    ledger_06 = um(a, "select count(*) from public.schema_migracao", ro=True)
    derruba_banco(url, "recuperacao_ataque")
    anota("A06", "dados restauram mas o ledger nao", "LEDGER" in dif_06,
          "livro-razao volta com %s linhas e a impressao difere em %s"
          % (ledger_06, ",".join(dif_06)))

    # ── 14 · restore parcial devolve exit 0 ───────────────────────────
    # É o MESMO restauro do 06, e a pergunta é outra: o código de saída.
    anota("A14", "restore parcial devolve exit 0",
          saida_06 == 0 and dif_06 != [],
          "exit=%d com impressao diferente — exit 0 nao e prova" % saida_06)

    # ── 07 · ledger restaura com SHA divergente ───────────────────────
    a, _ = _arena(url, dump)
    psql(a, "update public.schema_migracao set sha256 = repeat('0',64) "
            "where versao='030'")
    dif = compara(impressao_boa, impressao(a, ro=True))
    bate, fora = ledger_bate_com_o_repo(a)
    derruba_banco(url, "recuperacao_ataque")
    anota("A07", "ledger restaura com SHA divergente",
          "LEDGER" in dif and not bate,
          "impressao difere em LEDGER e %d versao(oes) nao batem com o repo"
          % len(fora))

    # ── 08 · 09 · 10 · uma trava perdida ──────────────────────────────
    for ident, nome, ddl in (
        ("A08", "FK perdida",
         "alter table public.participacao_na_derivacao drop constraint "
         "participacao_na_derivacao_raw_asset_id_fkey"),
        ("A09", "UNIQUE perdida",
         "alter table public.derived_artifact drop constraint "
         "derivacao_e_unica_por_regua"),
        ("A10", "CHECK perdida",
         "alter table public.raw_asset drop constraint "
         "forward_identificado_exige_identidade"),
    ):
        a, _ = _arena(url, dump)
        psql(a, ddl + ";")
        dif = compara(impressao_boa, impressao(a, ro=True))
        derruba_banco(url, "recuperacao_ataque")
        anota(ident, nome, "TRAVAS" in dif,
              "a impressao difere em %s" % ",".join(dif))

    # ── 11 · uma sentinela sumiu ──────────────────────────────────────
    a, _ = _arena(url, dump)
    psql(a, "delete from public.participacao_na_derivacao;")
    dif = compara(impressao_boa, impressao(a, ro=True))
    derruba_banco(url, "recuperacao_ataque")
    anota("A11", "uma sentinela sumiu",
          "SENTINELAS" in dif and "LINHAS" in dif,
          "a impressao difere em %s" % ",".join(dif))

    # ── 12 · um ID mudou ──────────────────────────────────────────────
    a, _ = _arena(url, dump)
    psql(a, "update public.etapa_da_corrida set id = id + 1000 "
            "where run_id like 'RECOVERY_TEST%';")
    dif = compara(impressao_boa, impressao(a, ro=True))
    derruba_banco(url, "recuperacao_ataque")
    anota("A12", "um ID mudou", "SENTINELAS" in dif,
          "a impressao difere em %s (LINHAS continua igual, e e esse o ponto)"
          % ",".join(dif))

    # ── 13 · row count divergiu ───────────────────────────────────────
    a, _ = _arena(url, dump)
    psql(a, "insert into public.collection_run (run_id, platform, started_at,"
            " rule_version, status) values ('RECOVERY_TEST_A_MAIS',"
            "'recovery-test',now(),'v1','concluida');")
    dif = compara(impressao_boa, impressao(a, ro=True))
    derruba_banco(url, "recuperacao_ataque")
    anota("A13", "row count divergiu", "LINHAS" in dif,
          "a impressao difere em %s" % ",".join(dif))

    # ── 15 · mecanismo descartavel diferente chamado de equivalente ───
    g_unknown = portao("PROVEN", "PROVEN", "UNKNOWN", "PASS", 0)
    g_no = portao("PROVEN", "PROVEN", "NO", "PASS", 0)
    anota("A15", "mecanismo diferente do LIVE chamado de equivalente",
          g_unknown[1] == "NO" and g_no[1] == "NO",
          "o portao devolve %s/%s com SAME_CLASS UNKNOWN e NO"
          % (g_unknown[0], g_no[0]))

    # ── 16 · backup existe mas o restore nunca foi exercido ───────────
    g = portao("PROVEN", "NOT_PROVEN", "YES", "PASS", 0)
    anota("A16", "backup existe mas restore nunca foi exercido",
          g[1] == "NO", "o portao devolve %s" % g[0])

    # ── 17 · restore exercido sobre banco nao vazio ───────────────────
    a, _ = _arena(url, dump)
    cheio = esta_vazio(a)
    cria_banco(url, "recuperacao_ataque")
    a2 = com_banco(url, "recuperacao_ataque")
    limpo = esta_vazio(a2)
    derruba_banco(url, "recuperacao_ataque")
    anota("A17", "restore exercido sobre banco nao vazio",
          (not cheio) and limpo,
          "a medicao de vazio distingue os dois casos, e o restauro so corre "
          "depois dela dar SIM")

    # ── 18 · 19 · a producao como origem ou como destino ──────────────
    passaram = [u for u in URLS_HOSTIS if e_descartavel(u)]
    anota("A18", "corpus LIVE copiado sem autorizacao", passaram == [],
          "%d URLs hostis testadas, 0 aceites como origem de backup"
          % len(URLS_HOSTIS))
    recusou = True
    for u in URLS_HOSTIS:
        try:
            exigir_descartavel(u, "teste")
            recusou = False
        except SystemExit:
            pass
    anota("A19", "restore tenta apontar para o LIVE", recusou and passaram == [],
          "exigir_descartavel levanta em todas as %d" % len(URLS_HOSTIS))

    # ── 20 · a prova depende de conserto manual pos-restore ───────────
    restaurado = com_banco(url, "recuperacao_vazia")
    morde = sessao_so_leitura_morde(restaurado)
    anota("A20", "prova depende de conserto manual pos-restore", morde,
          "a conferencia corre em `begin read only` e o servidor RECUSA "
          "escrita — conserto era impossivel, e nao apenas nao-feito")

    return r


# ─────────────────────────────────────────────────────────────────────────
# H · O LIVRO-RAZÃO CONTRA O REPOSITÓRIO
# ─────────────────────────────────────────────────────────────────────────
def migrations_do_repo():
    """Versão → sha256 do ficheiro. A `008` confere e não cria: nunca entra
    na cadeia nem no livro."""
    d = os.path.join(RAIZ, "supabase", "migrations")
    saida = {}
    for nome in sorted(os.listdir(d)):
        if not nome.endswith(".sql") or nome.startswith("008_"):
            continue
        with open(os.path.join(d, nome), "rb") as f:
            saida[nome[:3]] = hashlib.sha256(f.read()).hexdigest()
    return saida


def ledger_bate_com_o_repo(url):
    """Devolve (bate, divergências). Depois do restauro, o livro tem de
    continuar a apontar para os ficheiros que correram de facto."""
    esperado = migrations_do_repo()
    vivo = {}
    for l in linhas(url, "select versao || '|' || sha256 from "
                         "public.schema_migracao order by versao", ro=True):
        v, s = l.split("|", 1)
        vivo[v] = s
    fora = []
    for v in sorted(set(esperado) | set(vivo)):
        if esperado.get(v) != vivo.get(v):
            fora.append(v)
    return fora == [], fora


# ─────────────────────────────────────────────────────────────────────────
# I · O QUE O LIVE TEM — medido, e nunca suposto
# ─────────────────────────────────────────────────────────────────────────
# ⚠️ ESTES VALORES NÃO SE PASSAM POR VARIÁVEL DE AMBIENTE, E É DE PROPÓSITO.
# Se o veredito do LIVE pudesse ser afirmado de fora, o portão passaria a
# obedecer a quem o corre em vez de obedecer ao que existe. A função mede o
# repositório e o ambiente, e a resposta dela muda sozinha no dia em que os
# factos mudarem — que é o único jeito honesto de ela um dia dizer `PROVEN`.
CREDENCIAIS_DE_GESTAO = ("SUPABASE_ACCESS_TOKEN", "SUPABASE_MANAGEMENT_TOKEN")
PISTAS_DE_BACKUP = re.compile(
    r"pg_dump|pg_basebackup|supabase\s+db\s+dump|wal-g|barman|pgbackrest", re.I)


def mede_backup_do_live():
    """Devolve (mecanismo, estado, evidências).

    Três sítios, e nenhum deles é uma opinião:
      1. o ambiente tem credencial capaz de falar com a API de gestão?
      2. alguma automação deste repositório PRODUZ um backup do LIVE?
      3. existe registo datado de um restauro do LIVE?

    «O Supabase tem backup» não entra em nenhum dos três. Não é uma medição.
    """
    ev = []
    tem_credencial = [v for v in CREDENCIAIS_DE_GESTAO if os.environ.get(v)]
    ev.append("CREDENCIAL_DE_GESTAO=%s"
              % (",".join(tem_credencial) if tem_credencial else "AUSENTE"))

    wf = os.path.join(RAIZ, ".github", "workflows")
    produtores = []
    if os.path.isdir(wf):
        for nome in sorted(os.listdir(wf)):
            caminho = os.path.join(wf, nome)
            if not os.path.isfile(caminho):
                continue
            with open(caminho, encoding="utf-8", errors="replace") as f:
                texto = f.read()
            if PISTAS_DE_BACKUP.search(texto) and "SUPABASE_DB_URL" in texto:
                produtores.append(nome)
    ev.append("WORKFLOW_QUE_PRODUZ_BACKUP_DO_LIVE=%s"
              % (",".join(produtores) if produtores else "NENHUM"))

    if tem_credencial:
        # Haver credencial não é haver medição: ela abre a porta, e quem mede
        # é a chamada à API — que esta prova não faz, porque fazê-la daqui
        # seria alargar o escopo sem autorização.
        return "UNKNOWN", "NOT_MEASURED", ev
    if produtores:
        return "PG_DUMP", "NOT_PROVEN", ev
    return "UNKNOWN", "NOT_MEASURED", ev


def mesma_classe(mecanismo_live, mecanismo_descartavel):
    if mecanismo_live == "UNKNOWN":
        return "UNKNOWN"
    return "YES" if mecanismo_live == mecanismo_descartavel else "NO"


# ─────────────────────────────────────────────────────────────────────────
# J · A PROVA FUNCIONAL — não basta as tabelas existirem
# ─────────────────────────────────────────────────────────────────────────
def prova_funcional(url):
    """Corre DEPOIS da conferência, porque escreve. Devolve (ok, medições).

    Quatro perguntas diferentes, e um restauro pode acertar nas primeiras e
    falhar na última:

        SCHEMA_RESTORED     as tabelas existem
        DATA_RESTORED       as linhas voltaram
        RELATIONS_RESTORED  as arestas continuam a ligar as mesmas pontas
        COLLECTION_CAN_OPERATE_AFTER_RESTORE  o aplicador canónico e as
                                              travas trabalham sobre ele
    """
    m = []

    # 1 · a cadeia canónica corre outra vez sobre o banco restaurado. Tudo
    #     tem de dar SKIP com HASH=MATCH: é a prova de que o livro-razão
    #     voltou coerente com os ficheiros, e de que o aplicador consegue
    #     operar o banco restaurado sem reaplicar nada.
    codigo, saida = aplica_cadeia(url)
    skips = len(re.findall(r"=SKIP \(ja no livro-razao\) HASH=MATCH", saida))
    aplicadas = len(re.findall(r"=PASS", saida))
    m.append(("SEGUNDA_PASSAGEM_EXIT", codigo))
    m.append(("SEGUNDA_PASSAGEM_SKIP_HASH_MATCH", skips))
    m.append(("SEGUNDA_PASSAGEM_REAPLICOU", aplicadas))

    # 2 · a conferência da 008 sobre o banco restaurado
    m.append(("CONFERENCIA_008", "PASS" if confere_008(url) else "FAIL"))

    # 3 · a linhagem sintética lê-se pelas duas pontas
    lado_do_derivado = um(url, """
      select r.document_key from public.participacao_na_derivacao p
        join public.raw_asset r on r.id = p.raw_asset_id
        join public.derived_artifact d on d.id = p.derived_artifact_id
       where d.storage_path = '%s'""" % CAMINHO_DERIVADO)
    m.append(("LINHAGEM_DO_DERIVADO_PARA_A_OBSERVACAO",
              lado_do_derivado or "NADA"))
    corrida_da_aresta = um(url, "select first_seen_derivation_run_id from "
                                "public.participacao_na_derivacao")
    m.append(("CORRIDA_DA_ARESTA", corrida_da_aresta or "NADA"))

    # 4 · as travas MORDEM no banco restaurado. Uma trava que veio no dump
    #     mas não recusa nada é um desenho, não uma trava.
    mordidas = []
    for nome, sql in (
        ("CHECK_forward_exige_identidade",
         "insert into public.raw_asset (run_id, storage_path, media_type, "
         "bytes, sha256, captured_at, source_id, identity_state, preserved, "
         "not_preserved_reason) values ('%s','RECOVERY_TEST_ATAQUE/x.bin',"
         "'application/octet-stream',1,'%s',now(),'RECOVERY_TEST_SOURCE',"
         "'FORWARD_IDENTIFIED',false,'ataque')" % (RUN_CAPTURA, SHA_RAW)),
        ("PK_participacao_e_unica_por_par",
         "insert into public.participacao_na_derivacao (raw_asset_id, "
         "derived_artifact_id, first_seen_derivation_run_id) "
         "select raw_asset_id, derived_artifact_id, '%s' from "
         "public.participacao_na_derivacao" % RUN_DERIVACAO),
        ("FK_o_pai_por_id_e_o_pai_por_sha",
         "insert into public.derived_artifact (raw_asset_id, parent_sha256, "
         "kind, producer, producer_version, parameters_hash, sha256, bytes, "
         "media_type, storage_path, derived_at) select r.id, repeat('a',64),"
         "'OCR','recovery-test','1','%s','%s',1,'text/plain',"
         "'RECOVERY_TEST_ATAQUE/y.txt',now() from public.raw_asset r "
         "where r.storage_path='%s'"
         % (SHA_PARAMETROS, SHA_DERIVADO, CAMINHO_OBJETO)),
        ("UNIQUE_derivacao_e_unica_por_regua",
         "insert into public.derived_artifact (raw_asset_id, parent_sha256, "
         "kind, producer, producer_version, parameters_hash, sha256, bytes, "
         "media_type, storage_path, derived_at) select raw_asset_id, "
         "parent_sha256, kind, producer, producer_version, parameters_hash, "
         "sha256, bytes, media_type, storage_path || '.copia', derived_at "
         "from public.derived_artifact where storage_path='%s'"
         % CAMINHO_DERIVADO),
        # A etapa, e nao o documento: em `documento_estruturado` a chave
        # primaria dispararia ANTES da FK, e o teste passaria pela razao
        # errada. Uma trava que morde por outro motivo nao e a trava medida.
        ("FK_etapa_nomeia_corrida_existente",
         "insert into public.etapa_da_corrida (run_id, etapa, tentativa, "
         "estado) values ('CORRIDA_QUE_NAO_EXISTE','DERIVED',0,'PASS')"),
    ):
        ok, _, _ = psql(url, sql + ";")
        mordidas.append((nome, "RECUSOU" if not ok else "ACEITOU"))
    for nome, r in mordidas:
        m.append((nome, r))

    tudo = (codigo == 0 and aplicadas == 0 and skips > 0
            and dict(m)["CONFERENCIA_008"] == "PASS"
            and lado_do_derivado == "RECOVERY-TEST-DOC-1"
            and corrida_da_aresta == RUN_DERIVACAO
            and all(r == "RECUSOU" for _, r in mordidas))
    return tudo, m


# ─────────────────────────────────────────────────────────────────────────
# K · A CORRIDA
# ─────────────────────────────────────────────────────────────────────────
def secao(titulo):
    print()
    print("── %s " % titulo + "─" * max(0, 62 - len(titulo)))


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL", "")
    if not url:
        print("RECUPERACAO_PROVADA=NOT_RUN · falta BANCO_DESCARTAVEL_URL.")
        print("  Esta prova exige um Postgres 16 descartavel e local. Ela nao")
        print("  inventa um endereco, e nao corre contra producao.")
        return 2
    exigir_descartavel(url, "bancada")
    if (urlparse(url).path or "").lstrip("/") != "recuperacao":
        print("RECUPERACAO_PROVADA=NOT_RUN · a bancada chama-se `recuperacao`.")
        return 2

    tmp = tempfile.mkdtemp(prefix="recuperacao-")
    falhas = []
    try:
        # ── 1 · A BANCADA ─────────────────────────────────────────────
        secao("1 · A BANCADA, PELA CADEIA CANONICA")
        cria_banco(url, "recuperacao")
        codigo, saida = aplica_cadeia(url)
        aplicadas = len(re.findall(r"=PASS", saida))
        print("CADEIA_EXIT=%d" % codigo)
        print("MIGRATIONS_APLICADAS=%d" % aplicadas)
        if codigo != 0 or aplicadas == 0:
            print(saida[-1500:])
            falhas.append("a cadeia canonica nao construiu a bancada")
            return 1
        print("CONFERENCIA_008=%s" % ("PASS" if confere_008(url) else "FAIL"))
        escreve_sentinelas(url)
        print("SENTINELAS_ESCRITAS=SIM  (dados sinteticos; nenhum corpus real)")
        print("SHA_DOS_BYTES_SINTETICOS=%s" % SHA_RAW)
        versao_pg = um(url, "show server_version")
        print("POSTGRES_VERSION=%s" % versao_pg)
        # CLIENTE MAIS VELHO QUE O SERVIDOR NAO FAZ BACKUP — `pg_dump` recusa-se,
        # e o log diria apenas «falhou». Medir os dois numeros aqui transforma
        # uma falha obscura numa frase.
        cliente = subprocess.run(["pg_dump", "--version"], capture_output=True,
                                 text=True).stdout.strip()
        print("PG_DUMP_VERSION=%s" % cliente)
        maior = lambda t: int(re.search(r"(\d+)", t).group(1))
        if maior(cliente.split()[-1]) < maior(versao_pg):
            falhas.append("pg_dump (%s) e mais velho que o servidor (%s)"
                          % (cliente, versao_pg))
            print("RECUPERACAO_PROVADA=FAIL · cliente mais velho que o servidor")
            return 1

        # ── 2 · A IMPRESSAO DE ANTES ──────────────────────────────────
        secao("2 · A IMPRESSAO DA BANCADA, ANTES DO BACKUP")
        antes = impressao(url)
        for n in sorted(antes[1]):
            print("  %-12s %s  (%d linha(s))"
                  % (n, antes[1][n][0][:16],
                     len(antes[1][n][1].splitlines()) if antes[1][n][1] else 0))
        print("IMPRESSAO_ANTES=%s" % antes[0])

        # ── 3 · O BACKUP ──────────────────────────────────────────────
        secao("3 · O BACKUP DA BANCADA")
        dump = os.path.join(tmp, "bancada.dump")
        codigo, err = faz_backup(url, dump)
        ok_int, entradas = integridade_do_backup(dump)
        print("DISPOSABLE_BACKUP_MECHANISM=PG_DUMP  (formato custom, logico)")
        print("BACKUP_EXIT=%d" % codigo)
        print("BACKUP_CREATED=%s" % ("YES" if os.path.exists(dump) else "NO"))
        print("BACKUP_BYTES=%d" % (os.path.getsize(dump)
                                   if os.path.exists(dump) else 0))
        print("BACKUP_INTEGRITY_CHECK=%s  (%d entradas no indice)"
              % ("PASS" if ok_int else "FAIL", entradas))
        if codigo != 0 or not ok_int:
            print(err[:400])
            falhas.append("o backup da bancada nao se fez")
            return 1
        # o mesmo backup, so o schema — o ataque 05 precisa dele
        dump_schema = os.path.join(tmp, "so-schema.dump")
        subprocess.run(["pg_dump", "--format=custom", "--schema-only",
                        "--file=" + dump_schema, url], check=True)

        # ── 4 · DESTRUIR DE PROPOSITO ─────────────────────────────────
        secao("4 · DESTRUIR A BANCADA, DE PROPOSITO")
        derruba_banco(url, "recuperacao")
        original_existe = banco_existe(url, "recuperacao")
        print("ORIGINAL_DATABASE_AVAILABLE=%s" % ("YES" if original_existe else "NO"))
        if original_existe:
            falhas.append("o original continuou de pe — o restauro mediria ele")
            return 1
        cria_banco(url, "recuperacao_vazia")
        destino = com_banco(url, "recuperacao_vazia")
        vazio = esta_vazio(destino)
        print("RESTORE_TARGET_EMPTY=%s" % ("YES" if vazio else "NO"))
        if not vazio:
            falhas.append("o destino do restauro nao estava vazio")
            return 1

        # ── 5 · O RESTORE ─────────────────────────────────────────────
        secao("5 · O RESTORE")
        saida_r, err_r = restaura(destino, dump)
        print("RESTORE_COMMAND_EXIT=%d" % saida_r)
        if err_r.strip():
            print("  stderr: %s" % err_r.strip().splitlines()[0][:160])

        # ── 6 · A CONFERENCIA, EM SESSAO SO-LEITURA ───────────────────
        secao("6 · A CONFERENCIA — E ELA NAO PODE CONSERTAR NADA")
        morde = sessao_so_leitura_morde(destino)
        print("SESSAO_SO_LEITURA_RECUSA_ESCRITA=%s" % ("SIM" if morde else "NAO"))
        depois = impressao(destino, ro=True)
        dif = compara(antes, depois)
        print("IMPRESSAO_DEPOIS=%s" % depois[0])
        print("SECOES_DIFERENTES=%s" % (",".join(dif) if dif else "NENHUMA"))
        for n in sorted(antes[1]):
            igual = antes[1][n][0] == depois[1][n][0]
            print("  %-12s %s" % (n, "IGUAL" if igual else "DIFERENTE"))

        def sub(imp, tipo):
            return sorted(l for l in imp[1]["TRAVAS"][1].splitlines()
                          if l.split("|")[2] == tipo)

        pk = sub(antes, "p") == sub(depois, "p")
        fk = sub(antes, "f") == sub(depois, "f")
        uq = sub(antes, "u") == sub(depois, "u")
        ck = sub(antes, "c") == sub(depois, "c")
        bate_ledger, fora = ledger_bate_com_o_repo(destino)
        print("RESTORE_SCHEMA_COMPLETE=%s"
              % ("PASS" if antes[1]["TABELAS"][0] == depois[1]["TABELAS"][0]
                 and antes[1]["INDICES"][0] == depois[1]["INDICES"][0] else "FAIL"))
        print("RESTORE_LEDGER_COMPLETE=%s"
              % ("PASS" if antes[1]["LEDGER"][0] == depois[1]["LEDGER"][0]
                 and bate_ledger else "FAIL"))
        print("RESTORE_LEDGER_BATE_COM_O_REPO=%s%s"
              % ("SIM" if bate_ledger else "NAO",
                 "" if bate_ledger else "  divergentes: %s" % ",".join(fora)))
        print("RESTORE_ROW_COUNTS=%s"
              % ("PASS" if antes[1]["LINHAS"][0] == depois[1]["LINHAS"][0] else "FAIL"))
        print("RESTORE_SENTINELS=%s"
              % ("PASS" if antes[1]["SENTINELAS"][0] == depois[1]["SENTINELAS"][0]
                 else "FAIL"))
        print("RESTORE_CONSTRAINTS=%s"
              % ("PASS" if antes[1]["TRAVAS"][0] == depois[1]["TRAVAS"][0] else "FAIL"))
        print("RESTORE_PRIMARY_KEYS=%s" % ("PASS" if pk else "FAIL"))
        print("RESTORE_FOREIGN_KEYS=%s" % ("PASS" if fk else "FAIL"))
        print("RESTORE_UNIQUES=%s" % ("PASS" if uq else "FAIL"))
        print("RESTORE_CHECKS=%s" % ("PASS" if ck else "FAIL"))
        print("RESTORE_SEQUENCIAS=%s"
              % ("PASS" if antes[1]["SEQUENCIAS"][0] == depois[1]["SEQUENCIAS"][0]
                 else "FAIL"))
        print("REPAROS_MANUAIS_ANTES_DA_CONFERENCIA=0  (a sessao recusava escrita)")

        restauro_ok = (saida_r == 0 and dif == [] and morde and bate_ledger)
        if not restauro_ok:
            falhas.append("o restauro nao devolveu a bancada inteira")

        # ── 7 · A PROVA FUNCIONAL ─────────────────────────────────────
        secao("7 · O BANCO RESTAURADO OPERA")
        ok_func, medidas = prova_funcional(destino)
        for k, v in medidas:
            print("%s=%s" % (k, v))
        print("SCHEMA_RESTORED=%s"
              % ("YES" if antes[1]["TABELAS"][0] == depois[1]["TABELAS"][0] else "NO"))
        print("DATA_RESTORED=%s"
              % ("YES" if antes[1]["LINHAS"][0] == depois[1]["LINHAS"][0] else "NO"))
        print("RELATIONS_RESTORED=%s"
              % ("YES" if fk and antes[1]["SENTINELAS"][0] == depois[1]["SENTINELAS"][0]
                 else "NO"))
        print("COLLECTION_CAN_OPERATE_AFTER_RESTORE=%s"
              % ("YES" if ok_func else "NO"))
        if not ok_func:
            falhas.append("o banco restaurado nao opera")

        # ── 8 · O RED TEAM ────────────────────────────────────────────
        secao("8 · RED TEAM — VINTE ATAQUES")
        ataques = red_team(url, dump, dump_schema, antes, tmp)
        sobreviventes = [a for a in ataques if a[2] != "APANHADO"]
        for ident, nome, estado, como in ataques:
            print("  %s  %-9s %-46s %s" % (ident, estado, nome[:46], como[:70]))
        print("ATTACKS=%d" % len(ataques))
        print("SURVIVORS=%d" % len(sobreviventes))
        if sobreviventes:
            falhas.append("%d ataque(s) sobreviveram" % len(sobreviventes))

        # ── 9 · O VEREDITO ────────────────────────────────────────────
        secao("9 · O VEREDITO")
        mec_live, estado_live, ev = mede_backup_do_live()
        for e in ev:
            print("  %s" % e)
        classe = mesma_classe(mec_live, "PG_DUMP")
        # DUAS PALAVRAS, E ELAS NAO SAO SINONIMOS. `LIVE_BACKUP_STATUS` diz o
        # que se conseguiu MEDIR da origem; `BACKUP_SOURCE_FOR_LIVE` diz o que
        # o portao pode CONTAR COM. Tudo o que nao for `PROVEN` conta como
        # `NOT_PROVEN`, porque o portao nao pode distinguir «ainda nao olhei»
        # de «olhei e nao ha» — e as duas dao o mesmo: nao ha prova.
        backup_source = "PROVEN" if estado_live == "PROVEN" else "NOT_PROVEN"
        restore_mec = "PROVEN" if (restauro_ok and ok_func
                                   and not sobreviventes) else "NOT_PROVEN"
        descartavel = "PASS" if (restauro_ok and ok_func) else "FAIL"
        gate, pronto = portao(backup_source, restore_mec, classe, descartavel, 0)
        print("LIVE_BACKUP_MECHANISM=%s" % mec_live)
        print("LIVE_BACKUP_STATUS=%s" % estado_live)
        print("BACKUP_SOURCE_FOR_LIVE=%s" % backup_source)
        print("DISPOSABLE_BACKUP_MECHANISM=PG_DUMP")
        print("SAME_CLASS_AS_LIVE_BACKUP=%s" % classe)
        print("SAME_CLASS_RESTORE=%s" % classe)
        print("RESTORE_MECHANISM=%s" % restore_mec)
        print("DISPOSABLE_RESTORE=%s" % descartavel)
        print("LIVE_WRITES_PERFORMED=0")
        print("RECOVERY_GATE=%s" % gate)
        print("LIVE_READY_FOR_APPLY=%s" % pronto)
        print()
        if falhas:
            print("RECUPERACAO_PROVADA=FAIL")
            for f in falhas:
                print("  · %s" % f)
            return 1
        print("RECUPERACAO_PROVADA=PASS")
        print("  o que isto prova: que um backup DESTA CLASSE, feito com")
        print("  pg_dump, devolve um Postgres 16 inteiro e operavel depois de")
        print("  o original ter sido destruido — schema, dados, livro-razao,")
        print("  travas, sequencias e linhagem — sem um unico conserto a mao.")
        print("  o que NAO prova: que o LIVE seja recuperavel. O mecanismo de")
        print("  backup do LIVE esta %s, e por isso SAME_CLASS_RESTORE=%s e o"
              % (estado_live, classe))
        print("  portao devolve %s. Um mecanismo diferente chamado de" % gate)
        print("  equivalente seria o unico erro que esta prova nao pode cometer.")
        return 0
    finally:
        # A bancada morre. Fica o ficheiro do backup fora do repositorio, e ele
        # nao contem corpus nenhum — so as sentinelas sinteticas.
        for nome in ("recuperacao", "recuperacao_vazia", "recuperacao_ataque"):
            try:
                derruba_banco(url, nome)
            except SystemExit:
                pass
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
