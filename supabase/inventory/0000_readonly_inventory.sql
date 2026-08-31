-- INVENTARIO SOMENTE-LEITURA DO PROJETO CANDIDATO A DEV
--
-- GERADO por scripts/supabase_dev_target.py. Nao editar a mao.
--
-- Projeto: eame-sintonia (odhdwvugikjdvkapbowe · eu-west-1)
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
