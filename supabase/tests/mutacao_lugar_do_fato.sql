-- O RED TEAM DO LUGAR DO FATO.
--
-- Doze tentativas de derrubar a lei, uma por ataque da missão. Cada bloco
-- quebra UMA trava e exige que a regressão correspondente reprove. Tudo
-- dentro de begin/rollback: nenhuma mutação sobrevive ao arquivo.
--
-- "NAO PEGOU" significa que a regressão daquele número está verde em cima de
-- código quebrado — ou seja, que ela não prova nada.
\set QUIET on

begin;
-- ATAQUE 1 · source/base vira fact
alter table public.conteudo_lugar drop constraint so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato;
do $$
declare aceitou boolean := false;
begin
  begin
    insert into public.conteudo_lugar
      (conteudo_id, lugar_texto, geografia_id, estado_do_lugar, papel,
       tipo_de_evidencia, origem_do_dado, evidencia, ancora, rule_version)
    select ct.id, 'Foggia', g.id, 'RESOLVIDO', 'FACT', 'FIELD_OBSERVATION',
           'DA_FONTE', 'a ficha do canal diz Foggia', 'sede', 'ensaio'
      from public.conteudo ct, public.geografia g
     where ct.content_id='ENSAIO-B' and g.provincia='Foggia';
    aceitou := true;
  exception when others then aceitou := false;
  end;
  raise notice 'MUT01 E2  %', case when aceitou then 'PEGOU' else 'NAO PEGOU (teste inutil)' end;
end $$;
rollback;

begin;
-- ATAQUE 2 e 3 · operating e influence viram fact
alter table public.origem_lugar drop constraint origem_lugar_papel_check;
do $$
declare aceitou boolean := false;
begin
  begin
    insert into public.origem_lugar
      (origem_id, geografia_id, papel, origem_do_dado, evidencia, rule_version)
    select o.id, g.id, 'FACT', 'DECLARADO_NO_PERFIL', 'o perfil diz Foggia', 'ensaio'
      from public.origem o, public.geografia g
     where o.rotulo='ORIGEM ENSAIO PESQUISADOR' and g.provincia='Foggia';
    aceitou := true;
  exception when others then aceitou := false;
  end;
  raise notice 'MUT02 L5  %', case when aceitou then 'PEGOU' else 'NAO PEGOU (teste inutil)' end;
end $$;
rollback;

begin;
-- ATAQUE 4 · o primeiro lugar da lista vira o único FACT
-- A view passa a devolver UM lugar onde há três.
create or replace view public.v_conteudo_localizacao with (security_invoker = on) as
select c.id as conteudo_id, gs.pais as source_country,
       coalesce(gs.municipio, gs.provincia, gs.regiao, gs.nome_da_fonte, 'PAÍS') as source_place,
       null::pais as fact_country,
       least((select count(*) from public.conteudo_lugar cl
               where cl.conteudo_id = c.id and cl.papel='FACT'), 1) as fact_locations,
       (select array[min(cl.lugar_texto)] from public.conteudo_lugar cl
         where cl.conteudo_id = c.id and cl.papel='FACT') as fact_places,
       null::text[] as fact_precisions,
       false as fact_location_desconhecido,
       false as fact_sustentado_apenas_por_mencao,
       0::bigint as lugares_nao_fato, 0::bigint as lugares_fora_do_gazetteer
  from public.conteudo c
  left join public.geografia gs on gs.id = c.source_geografia_id;
select 'MUT04 N1 ' || case when (
  select l.fact_locations from public.v_conteudo_localizacao l
    join public.conteudo c on c.id=l.conteudo_id where c.content_id='ENSAIO-F') <> 3
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- ATAQUE 5 · região vira município
create or replace function public.precisao_da_geografia(g bigint)
returns text language sql stable as $x$ select 'MUNICIPIO' $x$;
select 'MUT05 P3 ' || case when public.precisao_da_geografia(
    (select id from public.geografia where pais='IT' and regiao='Toscana'
       and provincia is null and municipio is null and especie='ADMIN')) <> 'REGIAO'
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- ATAQUE 6 · zona textual vira divisão administrativa
create or replace function public.precisao_da_geografia(g bigint)
returns text language sql stable as $x$
  select case when g is null then 'NOT_KNOWN' else 'REGIAO' end $x$;
select 'MUT06 S1 ' || case when public.precisao_da_geografia(
    (select id from public.geografia where especie='DEFINIDA_PELA_FONTE'
       and nome_da_fonte like '%Ovest%')) <> 'ZONA_DEFINIDA_PELA_FONTE'
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- ATAQUE 7 · lista econômica vira lista de ocorrência
alter table public.conteudo_lugar drop constraint so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato;
do $$
declare aceitou boolean := false;
begin
  begin
    insert into public.conteudo_lugar
      (conteudo_id, lugar_texto, geografia_id, estado_do_lugar, papel,
       tipo_de_evidencia, origem_do_dado, evidencia, ancora, rule_version)
    select ct.id, 'Torino', g.id, 'RESOLVIDO', 'FACT', 'FIELD_OBSERVATION',
           'LISTA_TERRITORIAL', 'operiamo in Torino', 'operiamo', 'ensaio'
      from public.conteudo ct, public.geografia g
     where ct.content_id='ENSAIO-B' and g.provincia='Torino';
    aceitou := true;
  exception when others then aceitou := false;
  end;
  raise notice 'MUT07 T3  %', case when aceitou then 'PEGOU' else 'NAO PEGOU (teste inutil)' end;
end $$;
rollback;

begin;
-- ATAQUE 7b · a lista branca é ALARGADA em vez de removida
-- O ataque mais realista dos dois: ninguém apaga a trava, alguém acrescenta
-- um valor "só para este caso" — e as TRÊS leis que dependem dela morrem.
alter table public.conteudo_lugar
  drop constraint so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato;
alter table public.conteudo_lugar
  add constraint so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato
  check (papel <> 'FACT' or origem_do_dado in ('ESCRITO','CITADO','LISTA_TERRITORIAL'));
select 'MUT07b T3b ' || case when (
  select pg_get_constraintdef(oid) from pg_constraint
   where conname='so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato')
  like '%LISTA_TERRITORIAL%'
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- ATAQUE 8 · amostra positiva vira incidência
create or replace function public.f_ocorrencia_nao_e_incidencia(p_conteudo_id bigint)
returns table (tipo_de_evidencia text, quantos bigint) language sql stable as $x$
  select 'INCIDENCE_MEASUREMENT'::text, count(*)
    from public.conteudo_lugar cl
   where cl.conteudo_id = p_conteudo_id and cl.papel='FACT' $x$;
select 'MUT08 O2 ' || case when exists (
  select 1 from public.f_ocorrencia_nao_e_incidencia(
    (select id from public.conteudo where content_id='ENSAIO-M'))
   where tipo_de_evidencia='INCIDENCE_MEASUREMENT')
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- ATAQUE 9 · published_at vira fact_time
update public.conteudo
   set fact_tempo_texto = publicado_em::date::text,
       fact_tempo_resolucao = 'DATE_EXACT',
       fact_tempo_evidencia = 'a data que estava no topo do artigo',
       fact_tempo_origem = 'ESCRITO_NO_TEXTO'
 where content_id = 'ENSAIO-J';
select 'MUT09 F1 ' || case when (
  select fact_tempo_texto from public.conteudo where content_id='ENSAIO-J')
  <> 'stagione 2025'
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- ATAQUE 10 · lugar fora do gazetteer desaparece
delete from public.conteudo_lugar
 where estado_do_lugar = 'NAO_ESTA_NO_GAZETTEER';
select 'MUT10 G1 ' || case when not exists (
  select 1 from public.conteudo_lugar cl
    join public.conteudo c on c.id=cl.conteudo_id
   where c.content_id='ENSAIO-K' and cl.papel='FACT')
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- ATAQUE 11 · documento com três lugares perde dois
delete from public.conteudo_lugar cl
 using public.conteudo c
 where c.id = cl.conteudo_id and c.content_id='ENSAIO-F'
   and cl.lugar_texto in ('Siena','Arezzo');
select 'MUT11 N2 ' || case when (
  select l.fact_places from public.v_conteudo_localizacao l
    join public.conteudo c on c.id=l.conteudo_id where c.content_id='ENSAIO-F')
  <> array['Arezzo','Grosseto','Siena']
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- ATAQUE 12 · a proveniência da LINHA vira a do LOCAL
-- Todos os lugares passam a herdar uma evidência só, a do conteúdo.
update public.conteudo_lugar cl
   set evidencia = 'evidência única, herdada do conteúdo'
  from public.conteudo c
 where c.id = cl.conteudo_id and c.content_id = 'ENSAIO-F';
select 'MUT12 N3 ' || case when (
  select count(distinct evidencia) from public.conteudo_lugar cl
    join public.conteudo c on c.id=cl.conteudo_id
   where c.content_id='ENSAIO-F') = 1
  and (select count(distinct lugar_texto) from public.conteudo_lugar cl
    join public.conteudo c on c.id=cl.conteudo_id
   where c.content_id='ENSAIO-F') = 3
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- ATAQUE 13 · o dono antigo volta, ao lado do novo
-- Dois donos da mesma lei é o defeito que a 016 já cometeu uma vez.
alter table public.conteudo add column fact_geografia_id bigint references public.geografia(id);
select 'MUT13 N5 ' || case when exists (
  select 1 from information_schema.columns
   where table_schema='public' and table_name='conteudo'
     and column_name='fact_geografia_id')
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;
