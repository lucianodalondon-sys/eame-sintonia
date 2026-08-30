-- Cada mutação quebra UMA lei e exige que a regressão correspondente reprove.
\set QUIET on
begin;
-- MUT 1 · a relevância passa a ignorar cultura e problema
create or replace function public.f_relevancia_ao_caso(
  p_conteudo_crop_issue bigint, p_crop text, p_issue text, p_pais pais,
  p_janela_inicio date default null, p_janela_fim date default null)
returns table (relevancia text, porque text) language sql stable as $x$
  select 'EXACT_SIGNAL', 'tudo é sinal' $x$;
select 'MUT1 R2  ' || case when (
  select r.relevancia from public.conteudo_crop_issue cc
    join public.conteudo ct on ct.id=cc.conteudo_id
    join public.crop_issue ci on ci.id=cc.crop_issue_id
    join public.crop c on c.id=ci.crop_id,
    lateral public.f_relevancia_ao_caso(cc.id,'ENSAIO_CROP_A','ENSAIO_ISSUE_A','IT') r
   where ct.content_id='ENSAIO-A' and c.codigo='ENSAIO_CROP_B') = 'UNRELATED'
  then 'NAO PEGOU (teste inutil)' else 'PEGOU' end as resultado;
rollback;

begin;
-- MUT 2 · a precisão passa a devolver o país como se fosse região
create or replace function public.precisao_da_geografia(g bigint)
returns text language sql stable as $x$ select 'REGIAO' $x$;
select 'MUT2 D   ' || case when (
  select l.fact_precision from public.v_conteudo_localizacao l
    join public.conteudo c on c.id=l.conteudo_id where c.content_id='ENSAIO-D') = 'PAIS'
  then 'NAO PEGOU (teste inutil)' else 'PEGOU' end as resultado;
rollback;

begin;
-- MUT 3 · a trava do lugar do fato cai
alter table public.conteudo drop constraint local_da_fonte_nao_sustenta_local_do_fato;
do $$
declare aceitou boolean := false;
begin
  begin
    insert into public.conteudo
      (canal_id, run_id, tipo, content_id, hash_conteudo, source_geografia_id,
       fact_geografia_id, fact_geografia_origem, fact_geografia_evidencia, rule_version)
    select c.id, 'ENSAIO-RUN-CICATRIZ', 'artigo', 'MUT3', repeat('m',64),
           g.id, g.id, 'DA_FONTE', 'a ficha do canal diz Foggia', 'ensaio'
      from public.canal c, public.geografia g
     where c.channel_id='ENSAIO-CANAL-01' and g.provincia='Foggia';
    aceitou := true;
  exception when others then aceitou := false;
  end;
  raise notice 'MUT3 E2   %', case when aceitou then 'PEGOU' else 'NAO PEGOU (teste inutil)' end;
end $$;
rollback;

begin;
-- MUT 4 · o veredito de preservação passa a chamar tudo de preservado
create or replace function public.f_runs_pagos_sem_bruto(p_pais pais default null)
returns table (run_id text, platform text, actor text, source_country pais,
  status run_status, item_count_raw integer, cost_usd numeric, cost_method text,
  raw_assets integer, veredito text) language sql stable as $x$
  select r.run_id, r.platform, r.actor, r.source_country, r.status, r.item_count_raw,
         r.cost_usd, r.cost_method, 0, 'PRESERVADO' from public.collection_run r $x$;
select 'MUT4 P1  ' || case when (
  select veredito from public.f_runs_pagos_sem_bruto()
   where run_id='ENSAIO-RUN-PAGO-SEM-BRUTO') = 'PAGO_E_NAO_PRESERVADO'
  then 'NAO PEGOU (teste inutil)' else 'PEGOU' end as resultado;
rollback;

begin;
-- MUT 5 · a data de PUBLICAÇÃO volta a decidir como se fosse a do FATO
-- (a 015 devolvia UNRELATED para quem publicou depois da janela)
create or replace function public.f_relevancia_ao_caso(
  p_conteudo_crop_issue bigint, p_crop text, p_issue text, p_pais pais,
  p_janela_inicio date default null, p_janela_fim date default null)
returns table (relevancia text, porque text) language sql stable as $x$
  select 'UNRELATED', 'publicado fora da janela' $x$;
select 'MUT5 C1  ' || case when (
  select r.relevancia from public.conteudo_crop_issue cc
    join public.conteudo ct on ct.id=cc.conteudo_id
    join public.crop_issue ci on ci.id=cc.crop_issue_id
    join public.crop c on c.id=ci.crop_id and c.codigo='ENSAIO_CROP_A'
    join public.issue i on i.id=ci.issue_id and i.codigo='ENSAIO_ISSUE_A',
    lateral public.f_relevancia_ao_caso(cc.id,'ENSAIO_CROP_A','ENSAIO_ISSUE_A','IT',
                                        date '2026-01-01', date '2026-03-01') r
   where ct.content_id='ENSAIO-A') <> 'CONTEXT_ONLY'
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- MUT 6 · a menção volta a chegar ao consumidor disfarçada de afirmação
create or replace view public.v_conteudo_localizacao with (security_invoker = on) as
select c.id as conteudo_id, gs.pais as source_country,
       coalesce(gs.provincia, gs.regiao, 'PAÍS') as source_place,
       gf.pais as fact_country,
       coalesce(gf.provincia, gf.regiao, 'PAÍS') as fact_place,
       c.fact_geografia_origem, c.fact_geografia_evidencia,
       public.precisao_da_geografia(c.fact_geografia_id) as fact_precision,
       c.fact_geografia_id is null as fact_location_desconhecido,
       gs.pais is distinct from gf.pais as fonte_e_fato_em_paises_diferentes,
       false as fact_sustentado_apenas_por_mencao,
       'AFIRMADO_NO_TEXTO' as fact_forca_da_sustentacao
  from public.conteudo c
  left join public.geografia gs on gs.id = c.source_geografia_id
  left join public.geografia gf on gf.id = c.fact_geografia_id;
select 'MUT6 C5  ' || case when not (
  select l.fact_sustentado_apenas_por_mencao from public.v_conteudo_localizacao l
    join public.conteudo c on c.id=l.conteudo_id where c.content_id='ENSAIO-E')
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;
