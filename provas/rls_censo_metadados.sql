-- CENSO DE METADADOS DAS 12 CANDIDATAS · S0-P0M1
--
-- SO LE CATALOGO. Nenhuma linha de negocio e tocada: nem um select numa tabela
-- candidata, nem uma coluna de conteudo. Zero mutacao, zero DDL.
--
--     A PORTA ESTA ABERTA OU FECHADA?
--     SE O CATALOGO RESPONDE, NAO SE TOCA NA MACANETA.
--
-- has_table_privilege e has_schema_privilege devolvem o privilegio EFECTIVO:
-- ja contam heranca de role, GRANT a PUBLIC e default privileges. Ler
-- information_schema.table_privileges sozinho veria so o GRANT textual na
-- tabela, e perderia exactamente os caminhos que interessam.
--
--     EXISTE UM GRANT NA TABELA? != O ROLE CONSEGUE?

\pset tuples_only on
\pset format unaligned
\pset fieldsep '|'

-- ── contexto: quem somos, e que schemas o PostgREST expoe ──────────────────
select 'CTX|db=' || current_database()
    || '|user=' || current_user
    || '|pgrst_db_schemas=' || coalesce(current_setting('pgrst.db_schemas', true), 'NAO_DEFINIDO_AO_NIVEL_DA_BD');

select 'ROLE|' || rolname || '|exists=true' from pg_roles
 where rolname in ('anon','authenticated','service_role','authenticator') order by rolname;

select 'SCHEMA|public|anon_usage='          || has_schema_privilege('anon','public','USAGE')::text
    || '|anon_create='                      || has_schema_privilege('anon','public','CREATE')::text
    || '|authenticated_usage='              || has_schema_privilege('authenticated','public','USAGE')::text
    || '|authenticated_create='             || has_schema_privilege('authenticated','public','CREATE')::text;

-- ── as 12 candidatas ───────────────────────────────────────────────────────
with candidatas(nome) as (values
  ('boletim_fitossanitario'), ('clima_observacao'), ('conteudo_lugar'),
  ('decisao_de_coleta'), ('estatistica_agricola'), ('etapa_da_corrida'),
  ('evento_setorial'), ('fonte_acesso_teste'), ('fonte_externa'),
  ('mercado_observacao'), ('origem_lugar'), ('sinal_regulatorio_futuro')
)
select
  'T|' || k.nome
  || '|presente='  || (c.oid is not null)::text
  || '|rls='       || coalesce(c.relrowsecurity::text, '-')
  || '|force='     || coalesce(c.relforcerowsecurity::text, '-')
  || '|policies='  || coalesce((select count(*) from pg_policy p where p.polrelid = c.oid)::text, '-')
  || '|colunas='   || coalesce((select count(*) from pg_attribute a
                                where a.attrelid = c.oid and a.attnum > 0 and not a.attisdropped)::text, '-')
  || '|anon_s='    || coalesce(has_table_privilege('anon', c.oid, 'SELECT')::text, '-')
  || '|anon_i='    || coalesce(has_table_privilege('anon', c.oid, 'INSERT')::text, '-')
  || '|anon_u='    || coalesce(has_table_privilege('anon', c.oid, 'UPDATE')::text, '-')
  || '|anon_d='    || coalesce(has_table_privilege('anon', c.oid, 'DELETE')::text, '-')
  || '|auth_s='    || coalesce(has_table_privilege('authenticated', c.oid, 'SELECT')::text, '-')
  || '|auth_i='    || coalesce(has_table_privilege('authenticated', c.oid, 'INSERT')::text, '-')
  || '|auth_u='    || coalesce(has_table_privilege('authenticated', c.oid, 'UPDATE')::text, '-')
  || '|auth_d='    || coalesce(has_table_privilege('authenticated', c.oid, 'DELETE')::text, '-')
from candidatas k
left join pg_class c
  on c.relname = k.nome
 and c.relnamespace = 'public'::regnamespace
 and c.relkind = 'r'
order by k.nome;

-- ── contexto de fundo: o mesmo para TODA a schema public, so agregado ──────
-- Serve para saber se as 12 sao uma excepcao ou a regra da base viva.
select 'AGG|tabelas_public=' || count(*)::text
    || '|rls_on='            || count(*) filter (where c.relrowsecurity)::text
    || '|com_policy='        || count(*) filter (where exists (select 1 from pg_policy p where p.polrelid = c.oid))::text
    || '|anon_select='       || count(*) filter (where has_table_privilege('anon', c.oid, 'SELECT'))::text
    || '|anon_write='        || count(*) filter (where has_table_privilege('anon', c.oid, 'INSERT')
                                                    or has_table_privilege('anon', c.oid, 'UPDATE')
                                                    or has_table_privilege('anon', c.oid, 'DELETE'))::text
from pg_class c
where c.relnamespace = 'public'::regnamespace and c.relkind = 'r';
