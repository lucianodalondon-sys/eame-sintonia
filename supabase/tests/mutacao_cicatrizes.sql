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

-- MUT 2 e MUT 3 MUDARAM DE ARQUIVO na 018, junto com o dono da lei.
--
-- A precisão da geografia e a trava do lugar do fato deixaram de morar em
-- `conteudo` e passaram a morar em `conteudo_lugar`. As mutações que as
-- atacam foram para supabase/tests/mutacao_lugar_do_fato.sql — MUT05 e
-- MUT06 para a precisão, MUT01 para a trava.
--
-- Elas não ficam nos dois lugares: duas mutações para a mesma lei em dois
-- arquivos é a mesma doença que duas travas para a mesma regra, e a segunda
-- envelhece sem que ninguém perceba. Esta nota fica no lugar delas para que
-- a ausência seja lida como mudança de dono, e não como cobertura perdida.

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
-- Refeita na 018: a view passou a ler `conteudo_lugar`, e a coluna de força
-- da sustentação saiu (com 0..N, a força é de CADA lugar, não do conteúdo).
create or replace view public.v_conteudo_localizacao with (security_invoker = on) as
select c.id as conteudo_id, gs.pais as source_country,
       coalesce(gs.municipio, gs.provincia, gs.regiao, gs.nome_da_fonte, 'PAÍS') as source_place,
       null::pais as fact_country,
       (select count(*) from public.conteudo_lugar cl
         where cl.conteudo_id = c.id and cl.papel='FACT') as fact_locations,
       (select array_agg(cl.lugar_texto order by cl.lugar_texto)
          from public.conteudo_lugar cl
         where cl.conteudo_id = c.id and cl.papel='FACT') as fact_places,
       null::text[] as fact_precisions,
       false as fact_location_desconhecido,
       -- a mutação: a menção deixa de ser sinalizada
       false as fact_sustentado_apenas_por_mencao,
       0::bigint as lugares_nao_fato, 0::bigint as lugares_fora_do_gazetteer
  from public.conteudo c
  left join public.geografia gs on gs.id = c.source_geografia_id;
select 'MUT6 C5  ' || case when not (
  select l.fact_sustentado_apenas_por_mencao from public.v_conteudo_localizacao l
    join public.conteudo c on c.id=l.conteudo_id where c.content_id='ENSAIO-E')
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;
