-- CENSO DE METADADOS DA BASE VIVA · SEC-020
--
-- SO LE CATALOGO. Nenhuma linha de negocio e tocada: nem uma coluna de
-- conteudo, nem um dado pessoal. Zero mutacao, zero DDL.
--
--     A PORTA ESTA ABERTA OU FECHADA?
--     SE O CATALOGO DA PROPRIA CASA RESPONDE, NAO SE TOCA NA MACANETA.
--
-- Nasceu a olhar 12 tabelas, para fechar o candidato a P0. Olha agora o schema
-- inteiro, porque a pergunta mudou: nao e «aquelas doze estao bem?», e «o que
-- e que mudou desde ontem?». Um censo que so ve as tabelas de que ja
-- desconfiamos nunca ve a tabela que aparecer amanha.
--
--     MEDIR O QUE SE SUSPEITA NAO E MEDIR.
--
-- has_table_privilege e has_schema_privilege devolvem o privilegio EFECTIVO:
-- ja contam heranca de role, GRANT a PUBLIC e default privileges.
--
--     EXISTE UM GRANT NA TABELA? != O ROLE CONSEGUE?

\pset tuples_only on
\pset format unaligned
\pset fieldsep '|'

select 'CTX|db=' || current_database()
    || '|user=' || current_user
    || '|pgrst_db_schemas=' || coalesce(current_setting('pgrst.db_schemas', true), 'NAO_DEFINIDO_AO_NIVEL_DA_BD');

select 'ROLE|' || rolname from pg_roles
 where rolname in ('anon','authenticated','service_role','authenticator') order by rolname;

select 'SCHEMA|public'
    || '|anon_usage='           || has_schema_privilege('anon','public','USAGE')::text
    || '|anon_create='          || has_schema_privilege('anon','public','CREATE')::text
    || '|authenticated_usage='  || has_schema_privilege('authenticated','public','USAGE')::text
    || '|authenticated_create=' || has_schema_privilege('authenticated','public','CREATE')::text;

-- Uma linha por tabela do schema public. O nome, o estado de RLS, quantas
-- politicas, e o privilegio efectivo dos dois roles que a API expoe.
select
  'T|' || c.relname
  || '|rls='      || c.relrowsecurity::text
  || '|force='    || c.relforcerowsecurity::text
  || '|policies=' || (select count(*) from pg_policy p where p.polrelid = c.oid)::text
  || '|anon_s='   || has_table_privilege('anon', c.oid, 'SELECT')::text
  || '|anon_i='   || has_table_privilege('anon', c.oid, 'INSERT')::text
  || '|anon_u='   || has_table_privilege('anon', c.oid, 'UPDATE')::text
  || '|anon_d='   || has_table_privilege('anon', c.oid, 'DELETE')::text
  || '|auth_s='   || has_table_privilege('authenticated', c.oid, 'SELECT')::text
  || '|auth_i='   || has_table_privilege('authenticated', c.oid, 'INSERT')::text
  || '|auth_u='   || has_table_privilege('authenticated', c.oid, 'UPDATE')::text
  || '|auth_d='   || has_table_privilege('authenticated', c.oid, 'DELETE')::text
from pg_class c
where c.relnamespace = 'public'::regnamespace and c.relkind = 'r'
order by c.relname;

-- Vistas tambem sao superficie de API. security_invoker decide se a vista
-- corre com os direitos de quem a chama ou de quem a criou; uma vista sem ele
-- e um caminho a volta da RLS das tabelas que ela le.
--
--     UMA VISTA SEM security_invoker E UMA PORTA LATERAL.
select
  'V|' || c.relname
  || '|invoker=' || coalesce((select option_value from pg_options_to_table(c.reloptions)
                              where option_name = 'security_invoker'), 'nao_definido')
  || '|anon_s='  || has_table_privilege('anon', c.oid, 'SELECT')::text
  || '|auth_s='  || has_table_privilege('authenticated', c.oid, 'SELECT')::text
from pg_class c
where c.relnamespace = 'public'::regnamespace and c.relkind = 'v'
order by c.relname;
