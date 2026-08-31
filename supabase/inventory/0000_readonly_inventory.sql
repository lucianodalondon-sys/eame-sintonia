-- INVENTARIO SOMENTE-LEITURA DO PROJETO CANDIDATO A DEV
--
-- GERADO por scripts/supabase_dev_target.py. Nao editar a mao.
--
-- Projeto: eame-sintonia-dev (xhqebdweltytnghiavew · eu-west-1)
--
-- Este bloco entrega a EVIDENCIA bruta. O veredito separado (DATA_EMPTY e
-- SCHEMA_CLEAN) sai do segundo bloco, no fim do arquivo.
--
-- Este script NAO escreve nada. Nenhum CREATE, ALTER, INSERT, UPDATE ou DROP.
-- Rode no editor SQL do projeto e devolva o JSON para
-- scripts/supabase_dev_target.py classificar.

select jsonb_pretty(jsonb_build_object(
  'DATABASE_VERSION', (select version()),
  'EXISTING_SCHEMAS', (select coalesce(jsonb_agg(nspname), '[]'::jsonb) from (select nspname from pg_namespace where nspname not like 'pg_%' and nspname <> 'information_schema' order by 1) t),
  'EXISTING_TABLES', (select coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb) from (select table_schema, table_name from information_schema.tables where table_type = 'BASE TABLE' and table_schema not in ('pg_catalog','information_schema') order by 1,2) t),
  'EXISTING_VIEWS', (select coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb) from (select table_schema, table_name from information_schema.views where table_schema not in ('pg_catalog','information_schema') order by 1,2) t),
  'EXISTING_FUNCTIONS', (select coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb) from (select n.nspname, p.proname from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname not in ('pg_catalog','information_schema') order by 1,2) t),
  'EXISTING_RLS_POLICIES', (select coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb) from (select schemaname, tablename, policyname from pg_policies order by 1,2,3) t),
  'EXISTING_USER_DATA', (select coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb) from (select schemaname, relname, n_live_tup from pg_stat_user_tables where n_live_tup > 0 order by n_live_tup desc) t),
  'EXISTING_MIGRATION_HISTORY', (select case when to_regclass('supabase_migrations.schema_migrations') is null then null else (select coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb) from (select version, name from supabase_migrations.schema_migrations order by version) t) end),
  'AUTH_USERS', (select case when to_regclass('auth.users') is null then null else (select count(*) from auth.users) end),
  'STORAGE_OBJECTS', (select case when to_regclass('storage.objects') is null then null else (select count(*) from storage.objects) end)
)) as inventario;


-- ── VEREDITO: DATA_EMPTY e SCHEMA_CLEAN, respondidos SEPARADO ──────────
--
-- Tambem somente leitura. Rode depois do bloco de cima, no mesmo projeto.
--
-- Um Supabase novo ja nasce com auth, storage, extensions, realtime, vault e
-- supabase_migrations. Isso e o banco, nao e sujeira. So conta estrutura de
-- APLICACAO: schema fora dessa lista, ou objeto criado dentro de public.
--
-- A contagem de linhas e count(*) real, nao n_live_tup: a estimativa pode dizer
-- zero numa tabela cheia enquanto o autovacuum nao passa, e um zero falso aqui
-- autorizaria a migration em cima do dado de alguem.

with sistema(nspname) as (values ('auth'), ('storage'), ('extensions'), ('graphql'), ('graphql_public'), ('realtime'), ('supabase_functions'), ('supabase_migrations'), ('vault'), ('pgsodium'), ('pgsodium_masks'), ('net'), ('cron'), ('public')),
app_ns as (
  select n.oid, n.nspname
    from pg_namespace n
   where n.nspname not like 'pg\_%'
     and n.nspname <> 'information_schema'
     and n.nspname not in (select nspname from sistema)
),
app_rel as (
  select n.nspname as schema_name, c.relname, c.relkind
    from pg_class c
    join pg_namespace n on n.oid = c.relnamespace
   where c.relkind in ('r','p','v','m')
     and (n.nspname = 'public' or n.oid in (select oid from app_ns))
     and not exists (select 1 from pg_depend d
                      where d.objid = c.oid and d.deptype = 'e')
),
app_proc as (
  select n.nspname as schema_name, p.proname
    from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
   where (n.nspname = 'public' or n.oid in (select oid from app_ns))
     and not exists (select 1 from pg_depend d
                      where d.objid = p.oid and d.deptype = 'e')
),
app_linhas as (
  select r.schema_name, r.relname,
         (xpath('/row/c/text()',
                query_to_xml(format('select count(*) as c from %I.%I',
                                    r.schema_name, r.relname),
                             false, true, '')))[1]::text::bigint as linhas_reais
    from app_rel r
   where r.relkind in ('r','p')
),
migracoes as (
  select case when to_regclass('supabase_migrations.schema_migrations') is null
              then 0
              else (select count(*) from supabase_migrations.schema_migrations)
         end as n
),
usuarios as (
  select case when to_regclass('auth.users') is null then 0
              else (select count(*) from auth.users) end as n
),
arquivos as (
  select case when to_regclass('storage.objects') is null then 0
              else (select count(*) from storage.objects) end as n
),
medido as (
  select
    (select n from usuarios)                                        as auth_users,
    (select n from arquivos)                                        as storage_objects,
    (select coalesce(sum(linhas_reais), 0) from app_linhas)          as linhas_app,
    (select coalesce(jsonb_agg(to_jsonb(t) order by t.linhas_reais desc), '[]'::jsonb)
       from (select * from app_linhas where linhas_reais > 0) t)     as tabelas_com_linha,
    (select coalesce(jsonb_agg(nspname order by nspname), '[]'::jsonb)
       from app_ns)                                                  as schemas_de_aplicacao,
    (select coalesce(jsonb_agg(to_jsonb(t) order by t.schema_name, t.relname), '[]'::jsonb)
       from app_rel t)                                               as objetos_de_aplicacao,
    (select coalesce(jsonb_agg(to_jsonb(t) order by t.schema_name, t.proname), '[]'::jsonb)
       from app_proc t)                                              as funcoes_de_aplicacao,
    (select n from migracoes)                                        as migrations_registradas,
    (select count(*) from app_ns where nspname = 'sintonia')          as schema_sintonia
),
julgado as (
  select m.*,
    (m.auth_users = 0 and m.storage_objects = 0 and m.linhas_app = 0)      as dado_vazio,
    (jsonb_array_length(m.schemas_de_aplicacao) = 0
     and jsonb_array_length(m.objetos_de_aplicacao) = 0
     and jsonb_array_length(m.funcoes_de_aplicacao) = 0
     and m.migrations_registradas = 0)                                     as schema_limpo
    from medido m
)
select jsonb_pretty(jsonb_build_object(
  'DEV_PROJECT_REF_ESPERADO', 'xhqebdweltytnghiavew',
  'CONFERIR_O_REF_ANTES_DE_ACREDITAR', 'este SQL nao sabe em que projeto esta rodando: quem cola confere',
  'EVIDENCIA_DE_DADO', jsonb_build_object(
    'AUTH_USERS', j.auth_users,
    'STORAGE_OBJECTS', j.storage_objects,
    'LINHAS_EM_TABELAS_DE_APLICACAO', j.linhas_app,
    'TABELAS_COM_LINHA', j.tabelas_com_linha,
    'COMO_FOI_CONTADO', 'count(*) real por tabela, nao n_live_tup estimado'),
  'EVIDENCIA_DE_SCHEMA', jsonb_build_object(
    'SCHEMAS_DE_APLICACAO', j.schemas_de_aplicacao,
    'OBJETOS_DE_APLICACAO', j.objetos_de_aplicacao,
    'FUNCOES_DE_APLICACAO', j.funcoes_de_aplicacao,
    'MIGRATIONS_REGISTRADAS', j.migrations_registradas,
    'SCHEMA_SINTONIA_JA_EXISTE', j.schema_sintonia > 0,
    'O_QUE_NAO_FOI_CONTADO', 'auth, storage, extensions, realtime, vault, supabase_migrations e objetos de extensao: isso e o Supabase, nao e sujeira'),
  'DATA_EMPTY', case when j.dado_vazio then 'YES' else 'NO' end,
  'SCHEMA_CLEAN', case when j.schema_limpo then 'YES' else 'NO' end,
  'SAFE_FOR_CANONICAL_MIGRATION',
     case when j.dado_vazio and j.schema_limpo then 'YES' else 'NO' end,
  'REGRA', 'as duas perguntas sao independentes, e a migration exige as duas com YES. Vazio de dado nao e limpo de schema — foi assim que a branch hvtycqsrdtmxxodwcwph passou errado uma vez'
)) as veredito
  from julgado j;
