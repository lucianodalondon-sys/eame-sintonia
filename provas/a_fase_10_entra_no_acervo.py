#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A MIGRATION 027 APLICADA A UM ACERVO QUE JÁ EXISTE — e não a um banco novo.

O QUE ISTO PROVA, E O QUE `a_lei_da_fase_10.py` NÃO PROVA
---------------------------------------------------------
Aquela prova mede a LEI: o que passa a ser possível depois da fase 10. Esta
mede a **passagem**. São perguntas diferentes, e uma migration pode responder
bem à primeira e mal à segunda.

    LEI        o que o esquema novo permite
    PASSAGEM   o que acontece ao acervo QUE JÁ LA ESTAVA quando ele chega

Correr a `027` sobre uma tabela vazia provaria o SQL e nada mais.

    MIGRATION QUE SO FOI PROVADA EM BANCO NOVO E UMA MIGRATION POR PROVAR.

A FIXTURE TEM A FORMA DO VIVO, E ISSO É O PONTO
-----------------------------------------------
252 observações legadas, `id` esparsos até 890, o corte da fase 8 instalado
sobre eles, 252 cópias ligadas uma a uma, e um derivado. O livro-razão já
regista `001`–`026`, como o do banco canónico. O aplicador vê exactamente o
que veria em produção: **uma** migration pendente.

⚠️ Nenhum byte vem do banco vivo. A fixture é gerada, e a semelhança é
ESTRUTURAL — contagens, dispersão dos ids, ligações, corte. É a forma que
importa; os dados reais não acrescentariam prova nenhuma e acrescentariam
risco.

O APLICADOR É O DA CASA
-----------------------
`motor/cadeia_canonica.sh migrations`. Não há aqui um segundo migrador, nem um
`psql -f` a fingir de aplicação: se a cadeia não encontrar a `027`, não a puser
na ordem certa, não registar o `sha256` ou não a correr numa transacção só,
esta prova reprova.

E A FALHA A MEIO É ENCENADA, E NÃO IMAGINADA
--------------------------------------------
Uma cópia da `027` com um erro deliberado no fim corre pela MESMA cadeia, numa
raiz temporária. O que se mede a seguir é o que ficou instalado.

    PARTIAL_PHASE10_AFTER_FAILED_MIGRATION = 0   ou esta prova reprova.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import importlib.util as _u  # noqa: E402

_spec = _u.spec_from_file_location(
    "prova_pg", os.path.join(RAIZ, "provas", "preservar_coleta_no_postgres.py"))
_pg = _u.module_from_spec(_spec)
_spec.loader.exec_module(_pg)

M027 = "027_a_observacao_deixa_de_ser_o_endereco.sql"
MIGRACOES = os.path.join(RAIZ, "supabase", "migrations")
CADEIA = os.path.join(RAIZ, "motor", "cadeia_canonica.sh")
SEP = "\x1f"

# A forma do vivo, medida na auditoria de leitura do banco canónico.
LINHAS_LEGADAS = 252
CORTE_ESPERADO = 757          # 252 * 3 + 1, a dispersão que a fixture gera

FORA = []


# ─────────────────────────────────────────────────────────────────────────
def psql(url, sql):
    p = subprocess.run(["psql", url, "-X", "-q", "-v", "ON_ERROR_STOP=1",
                        "-t", "-A", "-F", SEP, "-c", sql],
                       capture_output=True, text=True)
    linhas = [l.split(SEP) for l in p.stdout.strip().splitlines() if l]
    return (p.returncode == 0), linhas, p.stderr.strip()


def um(url, sql):
    ok, r, _ = psql(url, sql)
    return r[0][0] if (ok and r) else ""


def ficheiro(url, caminho, transacao=True):
    cmd = ["psql", url, "-X", "-q", "-v", "ON_ERROR_STOP=1"]
    if transacao:
        cmd.append("--single-transaction")
    cmd += ["-f", caminho]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode == 0, p.stderr.strip()


def sha_do(caminho):
    with open(caminho, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _e(nome, obtido, esperado):
    bate = str(obtido) == str(esperado)
    print("  %-52s %-34s %s" % (nome, obtido,
                                "OK" if bate else "!! esperado=%s" % esperado))
    if not bate:
        FORA.append(nome)
    return bate


def diz(nome, v):
    print("  %-52s %s" % (nome, v))


# ─────────────────────────────────────────────────────────────────────────
# 1 · A FIXTURE, COM A FORMA DO VIVO
# ─────────────────────────────────────────────────────────────────────────
def fixture_pos_026(url):
    """Um banco no estado EXACTO em que o canónico está hoje: `001`–`026`
    aplicadas, acervo legado dentro, livro-razão a saber disso.

    As `001`–`025` entram por `psql` porque a cadeia aplicaria TODAS — e o que
    esta prova precisa é do momento ANTES da `027`. A `026` entra a seguir ao
    acervo, e não antes: é ela que classifica o legado e instala o corte, e
    corrê-la sobre uma tabela vazia daria um corte de zero.

        A ORDEM E A DA VIDA REAL, E NAO A CONVENIENTE.
    """
    psql(url, "drop schema public cascade; create schema public;")
    for nome in sorted(os.listdir(MIGRACOES)):
        if not nome.endswith(".sql") or nome[:3] in ("008", "026", "027"):
            continue
        ok, e = ficheiro(url, os.path.join(MIGRACOES, nome))
        if not ok:
            print("FALHOU a aplicar %s: %s" % (nome, e.splitlines()[0][:120]))
            return False

    # O ACERVO LEGADO. `id` esparsos de propósito: no vivo o canário forward
    # recebeu 890 num acervo de 252 linhas, e um corte medido sobre ids densos
    # não seria o mesmo corte.
    ok, _, e = psql(url, """
      insert into public.collection_run (run_id, platform, started_at,
                                         rule_version, status)
        values ('LEGADO','historico','2026-08-30T00:00:00Z','1','concluida');
      insert into public.storage_object (storage_path, media_type, bytes, sha256)
        select 'IT/legado/DOCUMENT/'||g||'-ficha.pdf', 'application/pdf',
               1000 + g, md5(g::text)||md5((g+1)::text)
          from generate_series(1, %d) g;
      insert into public.raw_asset (id, run_id, storage_path, media_type, bytes,
                                    sha256, captured_at, storage_object_id,
                                    source_url)
        select o.id * 3 + 1, 'LEGADO', o.storage_path, o.media_type, o.bytes,
               o.sha256, '2026-08-30T03:19:24Z', o.id,
               'https://exemplo.it/legado/'||o.id
          from public.storage_object o;
      select setval('raw_asset_id_seq', (select max(id) from public.raw_asset));
    """ % LINHAS_LEGADAS)
    if not ok:
        print("FALHOU a semear o acervo: %s" % e.splitlines()[0][:140])
        return False

    # UM DERIVADO, porque `derived_artifact` tem chave estrangeira COMPOSTA
    # para `(raw_asset.id, sha256)`. Uma migration que mexesse nos ids partia-a,
    # e sem um filho no acervo essa trava não teria por onde morder.
    pai = um(url, "select id from public.raw_asset order by id limit 1")
    sha_pai = um(url, "select sha256 from public.raw_asset where id=%s" % pai)
    ok, _, e = psql(url,
                    "insert into public.derived_artifact (raw_asset_id, "
                    "parent_sha256, kind, producer, producer_version, "
                    "parameters_hash, sha256, bytes, media_type, storage_path, "
                    "derived_at) values (%s,'%s','TEXT_EXTRACTION','texto-de-pdf',"
                    "'1','%s','%s',4968,'text/plain','IT/legado/TEXT/1.txt',"
                    "'2026-08-30T04:00:00Z')"
                    % (pai, sha_pai, "e" * 64, "d" * 64))
    if not ok:
        print("FALHOU a semear o derivado: %s" % e.splitlines()[0][:140])
        return False

    ok, e = ficheiro(url, os.path.join(MIGRACOES, "026_a_observacao_ganha_identidade.sql"))
    if not ok:
        print("FALHOU a aplicar a 026: %s" % e.splitlines()[0][:140])
        return False

    # O LIVRO-RAZÃO FICA COERENTE COM O QUE JÁ ENTROU. Sem isto o aplicador
    # veria `001`–`026` como pendentes e reaplicá-las-ia — e esta prova
    # mediria a cadeia inteira em vez de medir a passagem da `027`.
    psql(url, "create table if not exists public.schema_migracao ("
              " versao text primary key,"
              " aplicada_em timestamptz not null default now(),"
              " resultado text not null,"
              " sha256 text not null)")
    for nome in sorted(os.listdir(MIGRACOES)):
        if not nome.endswith(".sql") or nome[:3] in ("008", "027"):
            continue
        psql(url, "insert into public.schema_migracao (versao, resultado, "
                  "sha256) values ('%s','APLICADA','%s') on conflict (versao) "
                  "do nothing" % (nome[:3], sha_do(os.path.join(MIGRACOES, nome))))
    return True


def censo(url):
    """As mesmas perguntas, feitas ANTES e DEPOIS. Uma lista, e não uma
    consulta repetida: repetir a consulta mediria o depois duas vezes e
    chamaria a isso um antes."""
    return {
        "RAW_ASSET_COUNT": um(url, "select count(*) from public.raw_asset"),
        "RAW_ASSET_MIN_ID": um(url, "select min(id) from public.raw_asset"),
        "RAW_ASSET_MAX_ID": um(url, "select max(id) from public.raw_asset"),
        "RAW_ASSET_ID_SET_MD5": um(
            url, "select md5(string_agg(id::text, ',' order by id)) "
                 "from public.raw_asset"),
        "RAW_ASSET_SHA_SET_MD5": um(
            url, "select md5(string_agg(sha256, ',' order by id)) "
                 "from public.raw_asset"),
        "RAW_ASSET_PATH_SET_MD5": um(
            url, "select md5(string_agg(storage_path, ',' order by id)) "
                 "from public.raw_asset"),
        "STORAGE_OBJECT_COUNT": um(
            url, "select count(*) from public.storage_object"),
        "LINKS_MD5": um(
            url, "select md5(string_agg(id::text||'>'||"
                 "coalesce(storage_object_id::text,'-'), ',' order by id)) "
                 "from public.raw_asset"),
        "LEGACY_ROWS": um(url, "select count(*) from public.raw_asset where "
                               "identity_state='LEGACY_PRE_IDEMPOTENCY'"),
        "FORWARD_ROWS": um(url, "select count(*) from public.raw_asset where "
                                "identity_state like 'FORWARD%'"),
        "DERIVED_COUNT": um(url, "select count(*) from public.derived_artifact"),
        "DERIVED_LINKS_MD5": um(
            url, "select md5(string_agg(raw_asset_id::text||'>'||parent_sha256,"
                 " ',' order by id)) from public.derived_artifact"),
        "ORFAOS": um(url, "select count(*) from public.raw_asset r where "
                          "r.preserved and r.storage_object_id is null"),
        "DIVERGENTES": um(
            url, "select count(*) from public.raw_asset r join "
                 "public.storage_object o on o.id = r.storage_object_id "
                 "where o.sha256 <> r.sha256 or o.storage_path <> r.storage_path"),
    }


# ─────────────────────────────────────────────────────────────────────────
# 2 · O APLICADOR CANÓNICO
# ─────────────────────────────────────────────────────────────────────────
def aplicar_pela_cadeia(url, raiz=None):
    p = subprocess.run(["bash", os.path.join(raiz or RAIZ, "motor",
                                             "cadeia_canonica.sh"),
                        "migrations", url],
                       capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def parte_upgrade(url):
    print("\n== A · A PASSAGEM, MEDIDA DOS DOIS LADOS ==")
    antes = censo(url)
    for k in ("RAW_ASSET_COUNT", "STORAGE_OBJECT_COUNT", "LEGACY_ROWS",
              "FORWARD_ROWS", "RAW_ASSET_MIN_ID", "RAW_ASSET_MAX_ID"):
        diz("ANTES_" + k, antes[k])
    diz("ANTES_RAW_ASSET_ID_SET_MD5", antes["RAW_ASSET_ID_SET_MD5"])
    _e("ANTES_A_FIXTURE_TEM_A_FORMA_DO_VIVO",
       antes["RAW_ASSET_COUNT"], LINHAS_LEGADAS)
    _e("ANTES_O_CORTE_DO_LEGADO_ESTA_INSTALADO",
       um(url, "select count(*) from pg_constraint where "
               "conname='legado_e_anterior_ao_corte'"), 1)
    _e("ANTES_O_UNIQUE_DO_ENDERECO_ESTA_DE_PE",
       um(url, "select count(*) from pg_constraint where "
               "conname='raw_asset_storage_path_key'"), 1)
    _e("ANTES_A_CHAVE_DA_TENTATIVA_NAO_EXISTE",
       um(url, "select count(*) from pg_class where "
               "relname='raw_tentativa_sem_prova_idx'"), 0)
    _e("ANTES_O_LIVRO_RAZAO_NAO_TEM_A_027",
       um(url, "select count(*) from public.schema_migracao where "
               "versao='027'"), 0)

    print("\n  -- e agora a cadeia canonica, com a 027 como unica pendente")
    codigo, saida, erro = aplicar_pela_cadeia(url)
    linhas = saida.splitlines()
    _e("A_CADEIA_TERMINOU_BEM", codigo, 0)
    if codigo:
        print("    " + (erro or saida)[-400:])
    saltadas = [l for l in linhas if "SKIP (ja no livro-razao) HASH=MATCH" in l]
    _e("AS_ANTERIORES_FORAM_SALTADAS_COM_HASH_A_BATER", len(saltadas), 25)
    _e("A_027_FOI_APLICADA",
       "MIGRATION_027=PASS" if "MIGRATION_027=PASS" in linhas else
       [l for l in linhas if "027" in l] or "NADA SOBRE A 027",
       "MIGRATION_027=PASS")
    _e("NENHUMA_OUTRA_FOI_APLICADA",
       len([l for l in linhas if l.endswith("=PASS")]), 1)
    _e("NENHUMA_FOI_PULADA",
       len([l for l in linhas if l.startswith("MIGRATION_")]), 26)

    print("\n  -- o livro-razao")
    _e("LEDGER_TEM_A_027",
       um(url, "select resultado from public.schema_migracao where "
               "versao='027'"), "APLICADA")
    _e("LEDGER_GUARDOU_O_SHA_DO_FICHEIRO",
       um(url, "select sha256 from public.schema_migracao where versao='027'"),
       sha_do(os.path.join(MIGRACOES, M027)))

    print("\n  -- o acervo, relido")
    depois = censo(url)
    for k in sorted(antes):
        _e("PRESERVADO_" + k, depois[k], antes[k])
    return antes, depois


def parte_contrato(url):
    print("\n== B · O CONTRATO DA 027, COBRADO NO BANCO ==")
    _e("DROP_RAW_STORAGE_PATH_UNIQUE",
       um(url, "select count(*) from pg_constraint where "
               "conname='raw_asset_storage_path_key'"), 0)
    # E o índice implícito dele também tem de ter saído: uma constraint largada
    # que deixasse o índice para trás continuaria a travar, sem nome.
    _e("E_O_INDICE_DELE_TAMBEM_SAIU",
       um(url, "select count(*) from pg_class where "
               "relname='raw_asset_storage_path_key'"), 0)
    _e("FORWARD_IDENTIFIED_INDEX_PRESENTE",
       um(url, "select count(*) from pg_index i join pg_class c on "
               "c.oid=i.indexrelid where c.relname="
               "'raw_identidade_forward_idx' and i.indisvalid and i.indisunique"), 1)
    _e("UNPROVEN_INDEX_PRESENTE",
       um(url, "select count(*) from pg_index i join pg_class c on "
               "c.oid=i.indexrelid where c.relname="
               "'raw_tentativa_sem_prova_idx' and i.indisvalid and i.indisunique"), 1)
    d = um(url, "select indexdef from pg_indexes where "
                "indexname='raw_tentativa_sem_prova_idx'")
    _e("UNPROVEN_NULLS_NOT_DISTINCT",
       "SIM" if "NULLS NOT DISTINCT" in d.upper() else "NAO", "SIM")
    _e("UNPROVEN_E_SOBRE_O_OBJETO_E_NAO_SOBRE_O_ENDERECO",
       "SIM" if "storage_object_id" in d and "storage_path" not in d else "NAO",
       "SIM")
    diz("UNPROVEN_INDEXDEF", d)
    _e("IDENTITY_IMMUTABILITY_INSTALLED",
       um(url, "select count(*) from pg_trigger where "
               "tgname='a_identidade_da_observacao_nao_se_reescreve' "
               "and not tgisinternal"), 1)
    # O QUE A 027 NAO PODE TER MEXIDO
    _e("O_CORTE_DO_LEGADO_CONTINUA",
       um(url, "select count(*) from pg_constraint where "
               "conname='legado_e_anterior_ao_corte'"), 1)
    _e("AS_SETE_TRAVAS_DA_026_CONTINUAM_VALIDADAS",
       um(url, "select count(*) from pg_constraint where conrelid="
               "'public.raw_asset'::regclass and convalidated and conname in "
               "('base_da_chave_tem_vocabulario','estado_de_identidade_tem_"
               "vocabulario','fonte_real_em_qualquer_estado_forward',"
               "'forward_identificado_exige_identidade','forward_sem_prova_nao"
               "_finge_chave','legado_e_anterior_ao_corte',"
               "'a_observacao_e_a_copia_falam_do_mesmo_conteudo')"), 7)
    _e("A_COPIA_CONTINUA_DONA_DO_ENDERECO",
       um(url, "select count(*) from pg_constraint where "
               "conname='storage_object_storage_path_key'"), 1)
    _e("A_COLUNA_DO_ENDERECO_FICA",      # a fase 11 e que a retira
       um(url, "select count(*) from information_schema.columns where "
               "table_name='raw_asset' and column_name='storage_path'"), 1)


# ─────────────────────────────────────────────────────────────────────────
# 3 · A FALHA A MEIO
# ─────────────────────────────────────────────────────────────────────────
def parte_rollback(url):
    """A `027` com um erro deliberado no fim, pela MESMA cadeia.

    A raiz é temporária porque a cadeia varre `$RAIZ/supabase/migrations/*.sql`
    — e pôr um ficheiro estragado na pasta a sério seria encenar a falha no
    sítio onde ela não pode acontecer.
    """
    print("\n== C · A MIGRATION QUE FALHA A MEIO NAO DEIXA METADE ==")
    tmp = tempfile.mkdtemp(prefix="fase10-rollback-")
    try:
        os.makedirs(os.path.join(tmp, "supabase"))
        shutil.copytree(MIGRACOES, os.path.join(tmp, "supabase", "migrations"))
        shutil.copytree(os.path.join(RAIZ, "motor"), os.path.join(tmp, "motor"))
        alvo = os.path.join(tmp, "supabase", "migrations", M027)
        with open(alvo, "a", encoding="utf-8") as f:
            f.write("\n-- O ERRO DELIBERADO: a ultima instrucao do ficheiro\n"
                    "-- rebenta, e as tres fases ja correram acima dela.\n"
                    "select 1 from tabela_que_nao_existe_de_proposito;\n")
        _e("A_027_ESTRAGADA_TEM_OUTRO_SHA",
           "SIM" if sha_do(alvo) != sha_do(os.path.join(MIGRACOES, M027))
           else "NAO", "SIM")
        codigo, saida, _ = aplicar_pela_cadeia(url, raiz=tmp)
        _e("A_CADEIA_REPROVOU", "SIM" if codigo else "NAO", "SIM")
        _e("E_DISSE_QUAL", "MIGRATION_027=FAIL"
           if "MIGRATION_027=FAIL" in saida else saida.splitlines()[-1][:60],
           "MIGRATION_027=FAIL")
        # E AGORA O QUE INTERESSA: o que ficou no banco.
        instalado = 0
        instalado += 1 if um(url, "select count(*) from pg_class where "
                                  "relname='raw_tentativa_sem_prova_idx'") != "0" else 0
        instalado += 1 if um(url, "select count(*) from pg_trigger where "
                                  "tgname='a_identidade_da_observacao_nao_se_"
                                  "reescreve' and not tgisinternal") != "0" else 0
        instalado += 1 if um(url, "select count(*) from pg_constraint where "
                                  "conname='raw_asset_storage_path_key'") == "0" else 0
        _e("PARTIAL_PHASE10_AFTER_FAILED_MIGRATION", instalado, 0)
        _e("O_UNIQUE_DO_ENDERECO_CONTINUA_LA",
           um(url, "select count(*) from pg_constraint where "
                   "conname='raw_asset_storage_path_key'"), 1)
        _e("O_LIVRO_RAZAO_NAO_REGISTOU_A_027",
           um(url, "select count(*) from public.schema_migracao where "
                   "versao='027'"), 0)
        # E a recuperacao: a 027 BOA entra a seguir, sem nada por limpar.
        codigo, saida, _ = aplicar_pela_cadeia(url)
        _e("A_027_BOA_ENTRA_A_SEGUIR_SEM_LIMPEZA",
           "MIGRATION_027=PASS" if "MIGRATION_027=PASS" in saida else "NAO",
           "MIGRATION_027=PASS")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ─────────────────────────────────────────────────────────────────────────
# 4 · A IMUTABILIDADE, NO BANCO MIGRADO
# ─────────────────────────────────────────────────────────────────────────
def parte_imutabilidade(url):
    print("\n== D · A IDENTIDADE NAO SE REESCREVE, E O RESTO SIM ==")
    psql(url, "delete from public.derived_artifact")
    psql(url, "delete from public.raw_asset")
    psql(url, "delete from public.storage_object")
    sha = hashlib.sha256(b"D").hexdigest()
    caminho = "IT/f/DOCUMENT/%s-731-a.pdf" % sha[:16]
    for r in ("RA", "RB"):
        psql(url, "insert into public.collection_run (run_id, platform, "
                  "started_at, rule_version, status) values ('%s','p',now(),"
                  "'1','concluida') on conflict (run_id) do nothing" % r)
    psql(url, "insert into public.storage_object (storage_path, media_type, "
              "bytes, sha256) values ('%s','application/pdf',10,'%s')"
              % (caminho, sha))
    oid = um(url, "select id from public.storage_object")

    def semear(estado, doc):
        psql(url, "delete from public.raw_asset")
        dk = "null" if doc is None else "'%s'" % doc
        ba = "null" if doc is None else "'SOURCE_DOCUMENT_ID'"
        psql(url, "insert into public.raw_asset (run_id, storage_path, "
                  "media_type, bytes, sha256, captured_at, storage_object_id, "
                  "source_id, document_key, document_key_basis, identity_state,"
                  " attempts) values ('RA','%s','application/pdf',10,'%s',"
                  "now(),%s,'ARPAV',%s,%s,'%s',1)"
                  % (caminho, sha, oid, dk, ba, estado))

    U, I = "FORWARD_IDENTITY_UNPROVEN", "FORWARD_IDENTIFIED"
    recusadas = [
        ("UNPROVEN->IDENTIFIED", U, None,
         "identity_state='%s', document_key='D', "
         "document_key_basis='SOURCE_DOCUMENT_ID'" % I),
        ("IDENTIFIED->UNPROVEN", I, "D-1",
         "identity_state='%s', document_key=null, document_key_basis=null" % U),
        ("IDENTIFIED->LEGACY", I, "D-1",
         "identity_state='LEGACY_PRE_IDEMPOTENCY', source_id=null, "
         "document_key=null, document_key_basis=null"),
        ("trocar source_id (IDENTIFIED)", I, "D-1", "source_id='OUTRA'"),
        ("trocar source_id (UNPROVEN)", U, None, "source_id='OUTRA'"),
        ("trocar document_key", I, "D-1", "document_key='D-2'"),
        ("trocar document_key_basis", I, "D-1", "document_key_basis=null"),
        ("trocar run_id", I, "D-1", "run_id='RB'"),
        ("trocar sha256", I, "D-1",
         "sha256='%s'" % hashlib.sha256(b"outro").hexdigest()),
        ("desligar storage_object_id", I, "D-1", "storage_object_id=null"),
    ]
    nega = 0
    for nome, estado, doc, sets in recusadas:
        semear(estado, doc)
        ok, _, _ = psql(url, "update public.raw_asset set %s" % sets)
        if not ok:
            nega += 1
        else:
            print("  !! ACEITE (devia recusar): %s" % nome)
    _e("IDENTITY_MUTATIONS_REJECTED", "%d/%d" % (nega, len(recusadas)),
       "%d/%d" % (len(recusadas), len(recusadas)))

    permitidas = [
        ("attempts / last_attempt_at",
         "attempts=coalesce(attempts,0)+1, last_attempt_at=now()"),
        ("preserved / not_preserved_reason",
         "preserved=false, not_preserved_reason='BYTE_NAO_VOLTOU'"),
        ("source_url", "source_url='https://exemplo.it/outra'"),
        ("captured_at", "captured_at=now()"),
        ("media_type", "media_type='application/octet-stream'"),
        ("storage_path (e ENDERECO — a fase 11 tira-o)",
         "storage_path='IT/f/DOCUMENT/outro.pdf'"),
    ]
    sim = 0
    for nome, sets in permitidas:
        semear(I, "D-1")
        ok, _, e = psql(url, "update public.raw_asset set %s" % sets)
        if ok:
            sim += 1
        else:
            print("  !! RECUSADO (devia permitir): %s · %s"
                  % (nome, e.splitlines()[-1][:80]))
    _e("OPERATIONAL_MUTATIONS_ALLOWED", "%d/%d" % (sim, len(permitidas)),
       "%d/%d" % (len(permitidas), len(permitidas)))


# ─────────────────────────────────────────────────────────────────────────
# 5 · RED TEAM — A JANELA DA TRANSIÇÃO
# ─────────────────────────────────────────────────────────────────────────
def parte_red_team(url):
    """O ponto crítico: não pode existir momento em que o escritor novo e um
    esquema — velho ou novo — produzam SILÊNCIO INCORRECTO.

    Silêncio incorrecto é o único resultado inaceitável: uma escrita que não
    acontece e ninguém sabe, ou uma que acontece errada e a corrida fecha.
    """
    from guarda.preservar_coleta import ArmazemDeMentira, preservar, sha256
    print("\n== E · A JANELA DA TRANSICAO ==")
    banco = _pg.MemoriaPostgres(url)
    A = b"conteudo-transicao"

    def art(nativo, doc="D-T"):
        return {"COUNTRY": "IT", "SOURCE_SLUG": "fonte-de-teste",
                "SOURCE_ID": "IT-T2-002", "DOCUMENT_ID": doc,
                "ARTIFACT_KIND": "DOCUMENT", "NAME": "a.pdf",
                "SOURCE_NATIVE_ID": nativo, "SHA256": sha256(A),
                "BYTES": len(A), "MEDIA_TYPE": "application/pdf",
                "CAPTURED_AT": "2026-09-10T00:00:00Z",
                "SOURCE_URL": "https://exemplo.it/%s" % nativo}

    def corrida(r):
        return {"RUN_ID": r, "PLATFORM": "local", "ACTOR": "prova",
                "ACTOR_VERSION": "1", "SOURCE_COUNTRY": "IT",
                "MISSION": "fase10", "STARTED_AT": "2026-09-10T00:00:00Z",
                "RULE_VERSION": "1", "CAPTURE_METHOD": "HTTP_GET"}

    def correr(run):
        return preservar(corrida(run), [art("731")], ArmazemDeMentira(),
                         lambda o: A, memoria=banco,
                         terminou_em="2026-09-10T01:00:00Z")

    def limpar():
        psql(url, "delete from public.derived_artifact")
        psql(url, "delete from public.raw_asset")
        psql(url, "delete from public.storage_object")

    # ── E1 · escritor NOVO contra esquema VELHO ─────────────────────────
    # Repõe-se o `unique` do endereço: é o estado em que a produção está
    # NESTE momento, com o runtime já trocado e a migration ainda por aplicar.
    limpar()
    psql(url, "drop index if exists raw_tentativa_sem_prova_idx")
    psql(url, "alter table public.raw_asset add constraint "
              "raw_asset_storage_path_key unique (storage_path)")
    r1 = correr("T-A")
    _e("E1_PRIMEIRA_CORRIDA_FECHA", r1["RUN_STATE"], "COMPLETE")
    r2 = correr("T-B")
    _e("E1_A_SEGUNDA_NAO_ENTRA",
       um(url, "select count(*) from public.raw_asset"), 1)
    _e("E1_E_A_CORRIDA_NAO_MENTE", r2["RUN_STATE"], "PARTIAL")
    _e("E1_COM_O_NOME_DA_TRAVA", r2["PENDENCIA"], "NEW_RUN_SAME_STORAGE_PATH")
    _e("E1_SEM_SILENCIO", "SIM" if r2["MEMORIA"]["ERRO"] else "NAO", "SIM")

    # ── E2 · escritor VELHO contra esquema NOVO ─────────────────────────
    # Não sobrou nenhum, mas o que ele fazia — `on conflict (storage_path)` —
    # tem de falhar ALTO, e não silenciosamente.
    psql(url, "alter table public.raw_asset drop constraint "
              "raw_asset_storage_path_key")
    psql(url, "create unique index raw_tentativa_sem_prova_idx on "
              "public.raw_asset (run_id, source_id, storage_object_id, sha256) "
              "nulls not distinct where identity_state = "
              "'FORWARD_IDENTITY_UNPROVEN'")
    ok, _, e = psql(url,
                    "insert into public.raw_asset (run_id, storage_path, "
                    "media_type, bytes, sha256, captured_at) values "
                    "('T-A','x','application/pdf',1,'%s',now()) on conflict "
                    "(storage_path) do nothing" % sha256(A))
    _e("E2_O_ESCRITOR_ANTIGO_FALHA_ALTO", "SIM" if not ok else "NAO", "SIM")
    _e("E2_E_A_PLANEAR_E_NAO_A_CORRER",
       "SIM" if "no unique or exclusion constraint" in e else e[:60], "SIM")

    # ── E3 · escritor NOVO contra esquema NOVO ──────────────────────────
    # A mesma corrida `T-B` que ficou de fora em E1 entra agora, e o objeto
    # que já lá estava é REUTILIZADO.
    r3 = correr("T-B")
    _e("E3_A_CORRIDA_NOVA_ENTRA",
       um(url, "select count(*) from public.raw_asset"), 2)
    _e("E3_UM_SO_OBJETO",
       um(url, "select count(*) from public.storage_object"), 1)
    _e("E3_IDS_DIFERENTES",
       um(url, "select count(distinct id) from public.raw_asset"), 2)
    _e("E3_E_A_CORRIDA_FECHA", r3["RUN_STATE"], "COMPLETE")

    # ── E4 · o retry, depois da migration ───────────────────────────────
    antes_id = um(url, "select id from public.raw_asset where run_id='T-B'")
    r4 = correr("T-B")
    _e("E4_RETRY_NAO_DUPLICA",
       um(url, "select count(*) from public.raw_asset"), 2)
    _e("E4_MESMO_RAW_ASSET_ID",
       um(url, "select id from public.raw_asset where run_id='T-B'"), antes_id)
    _e("E4_ATTEMPTS_SUBIU",
       um(url, "select attempts from public.raw_asset where run_id='T-B'"), 2)
    _e("E4_A_CORRIDA_FECHA", r4["RUN_STATE"], "COMPLETE")

    # ── E5 · UNPROVEN com `storage_object_id` nulo ──────────────────────
    limpar()
    psql(url, "insert into public.raw_asset (run_id, storage_path, media_type, "
              "bytes, sha256, captured_at, storage_object_id, source_id, "
              "identity_state, preserved, not_preserved_reason) values "
              "('T-A','IT/sem/1.pdf','application/pdf',1,'%s',now(),null,"
              "'ARPAV','FORWARD_IDENTITY_UNPROVEN',false,'BYTE_NAO_VOLTOU')"
              % sha256(A))
    ok, _, _ = psql(url, "insert into public.raw_asset (run_id, storage_path, "
                         "media_type, bytes, sha256, captured_at, "
                         "storage_object_id, source_id, identity_state, "
                         "preserved, not_preserved_reason) values "
                         "('T-A','IT/sem/2.pdf','application/pdf',1,'%s',now(),"
                         "null,'ARPAV','FORWARD_IDENTITY_UNPROVEN',false,"
                         "'BYTE_NAO_VOLTOU')" % sha256(A))
    _e("E5_SEM_COPIA_A_CHAVE_AINDA_TRAVA", "SIM" if not ok else "NAO", "SIM")
    _e("E5_UMA_LINHA_SO", um(url, "select count(*) from public.raw_asset"), 1)

    # ── E6 · dois documentos com o MESMO sha256 ─────────────────────────
    limpar()
    for i, disc in enumerate(("731", "6321")):
        p = "IT/f/DOCUMENT/%s-%s-a.pdf" % (sha256(A)[:16], disc)
        psql(url, "insert into public.storage_object (storage_path, media_type,"
                  " bytes, sha256) values ('%s','application/pdf',10,'%s')"
                  % (p, sha256(A)))
        psql(url, "insert into public.raw_asset (run_id, storage_path, "
                  "media_type, bytes, sha256, captured_at, storage_object_id, "
                  "source_id, document_key, document_key_basis, identity_state,"
                  " attempts) select 'T-A','%s','application/pdf',10,'%s',now(),"
                  "o.id,'ARPAV','D-%s','SOURCE_DOCUMENT_ID',"
                  "'FORWARD_IDENTIFIED',1 from public.storage_object o where "
                  "o.storage_path='%s'" % (p, sha256(A), disc, p))
    _e("E6_DOIS_DOCUMENTOS_MESMO_SHA_CONTINUAM_DOIS",
       um(url, "select count(*) from public.raw_asset"), 2)

    # ── E7 · concorrência sobre a MESMA observação, nas duas famílias ───
    for nome, estado, doc in (("E7_IDENTIFIED", "FORWARD_IDENTIFIED", "D-C"),
                              ("E8_UNPROVEN", "FORWARD_IDENTITY_UNPROVEN",
                               None)):
        limpar()
        p = "IT/f/DOCUMENT/%s-c-a.pdf" % sha256(A)[:16]
        psql(url, "insert into public.storage_object (storage_path, media_type,"
                  " bytes, sha256) values ('%s','application/pdf',10,'%s')"
                  % (p, sha256(A)))
        oid = um(url, "select id from public.storage_object")
        dk = "null" if doc is None else "'%s'" % doc
        ba = "null" if doc is None else "'SOURCE_DOCUMENT_ID'"
        ins = ("insert into public.raw_asset (run_id, storage_path, media_type,"
               " bytes, sha256, captured_at, storage_object_id, source_id, "
               "document_key, document_key_basis, identity_state, attempts) "
               "values ('T-A','%s','application/pdf',10,'%s',now(),%s,'ARPAV',"
               "%s,%s,'%s',1);" % (p, sha256(A), oid, dk, ba, estado))
        a = subprocess.Popen(["psql", url, "-X", "-q", "-A", "-t"],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, bufsize=1)
        b = subprocess.Popen(["psql", url, "-X", "-q", "-A", "-t"],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, bufsize=1)
        for s in (a, b):
            s.stdin.write("begin;\n")
            s.stdin.flush()
        a.stdin.write(ins)
        a.stdin.flush()
        time.sleep(1)
        b.stdin.write(ins)
        b.stdin.flush()
        time.sleep(1)
        a.stdin.write("commit;\n")
        a.stdin.close()
        a.stdout.read()
        a.wait()
        time.sleep(1)
        b.stdin.write("commit;\n")
        b.stdin.close()
        sb = b.stdout.read()
        b.wait()
        _e(nome + "_UMA_LINHA_SO",
           um(url, "select count(*) from public.raw_asset"), 1)
        _e(nome + "_A_SEGUNDA_FOI_RECUSADA",
           "SIM" if "duplicate key" in sb else "NAO", "SIM")
    limpar()


# ─────────────────────────────────────────────────────────────────────────
def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL", "")
    if not _pg._e_descartavel(url):
        print("NOT_RUN — sem BANCO_DESCARTAVEL_URL apontado a um banco "
              "descartavel local. Esta prova nunca corre contra producao.")
        return 2
    print("=== A FASE 10 ENTRA NUM ACERVO QUE JA EXISTE ===")
    print("motor: %s" % um(url, "select version()").split(",")[0])
    print("migration: %s" % M027)
    print("sha256: %s\n" % sha_do(os.path.join(MIGRACOES, M027)))

    print("-- a fixture, com a forma do vivo")
    if not fixture_pos_026(url):
        return 1
    parte_upgrade(url)
    parte_contrato(url)
    parte_imutabilidade(url)
    parte_red_team(url)

    print("\n-- e a falha a meio, num banco proprio")
    url_r = url.rsplit("/", 1)[0] + "/objeto"
    if _pg._e_descartavel(url_r):
        if fixture_pos_026(url_r):
            parte_rollback(url_r)
    else:
        print("  NAO CORRIDA — falta o banco `objeto` para a encenacao")
        FORA.append("ROLLBACK_NAO_CORRIDO")

    print()
    for nome in FORA:
        print("  FAIL %s" % nome)
    print("\nA_FASE_10_ENTRA_NO_ACERVO=%s%s" % (
        "PASS" if not FORA else "FAIL",
        "" if not FORA else " · reprovou: " + ", ".join(FORA)))
    print("PHASE_10_LIVE=NO — esta prova nunca fala com o banco canonico.")
    return 0 if not FORA else 1


if __name__ == "__main__":
    sys.exit(main())
