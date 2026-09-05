-- Cada mutação quebra UMA lei do portão de coleta e exige que a regressão
-- correspondente reprove. Suíte verde em cima de código quebrado não é prova.
-- Tudo roda dentro de begin/rollback: nenhuma mutação sobrevive ao arquivo.
\set QUIET on

begin;
-- MUT 1 · o sensor humano passa a aceitar qualquer canal
-- (a cicatriz literal: o agregador contado como voz humana)
create or replace view public.v_human_sensor_admissivel with (security_invoker = on) as
select c.id as canal_id, c.plataforma, c.channel_id, c.handle,
       c.tipo_de_perfil, c.tipo_de_perfil_evidencia,
       o.pessoa_id, o.organizacao_id,
       true as admissivel, 'ADMISSIVEL' as porque
  from public.canal c join public.origem o on o.id = c.origem_id;
select 'MUT1 S3  ' || case when (
  select s.admissivel from public.v_human_sensor_admissivel s
   where s.channel_id='ENSAIO-PERFIL-AGREGADOR')
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- MUT 2 · classificar por volume: quem tem muito conteúdo vira pessoa
-- Esta é a heurística fraca que a lei proíbe, escrita como código.
create or replace view public.v_human_sensor_admissivel with (security_invoker = on) as
select c.id as canal_id, c.plataforma, c.channel_id, c.handle,
       c.tipo_de_perfil, c.tipo_de_perfil_evidencia,
       o.pessoa_id, o.organizacao_id,
       (select count(*) from public.conteudo ct where ct.canal_id = c.id) >= 0
         as admissivel,
       'ADMISSIVEL' as porque
  from public.canal c join public.origem o on o.id = c.origem_id;
select 'MUT2 S8  ' || case when exists (
  select 1 from public.v_human_sensor_admissivel
   where admissivel and (tipo_de_perfil <> 'PERSON_PROFILE' or pessoa_id is null))
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- MUT 3 · declarar tipo de perfil deixa de exigir evidência
alter table public.canal drop constraint tipo_de_perfil_declarado_exige_evidencia;
do $$
declare aceitou boolean := false;
begin
  begin
    insert into public.canal (origem_id, plataforma, channel_id, tipo_de_perfil)
    select o.id, 'web', 'MUT3-SEM-EVIDENCIA', 'PERSON_PROFILE'
      from public.origem o where o.rotulo='ORIGEM ENSAIO PESSOA';
    aceitou := true;
  exception when others then aceitou := false;
  end;
  raise notice 'MUT3 S9   %',
    case when aceitou then 'PEGOU' else 'NAO PEGOU (teste inutil)' end;
end $$;
rollback;

begin;
-- MUT 4 · a guarda do gasto passa a dizer SIM sem checkpoint
-- (BR-19: SEM_CHECKPOINT_NAO_GASTEI vira "pode gastar")
create or replace function public.pode_gastar(p_target text, p_input_hash text)
returns table (pode boolean, porque text, checkpoint_id bigint, retomar_de text)
language sql stable as $x$ select true, 'CHECKPOINT_ABERTO', null::bigint, null::text $x$;
select 'MUT4 K1  ' || case when (
  select pode from public.pode_gastar('ALVO-QUE-NUNCA-EXISTIU','hash-inexistente'))
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- MUT 5 · a rodada entra na identidade do conteúdo
-- É exatamente o defeito que duplicava tudo quando a retomada trocava de
-- chave: o mesmo item, colhido por dois RUN_ID, virava dois conteúdos.
alter table public.conteudo drop constraint conteudo_canal_id_content_id_key;
alter table public.conteudo add constraint conteudo_canal_id_content_id_key
  unique (canal_id, content_id, run_id);
select 'MUT5 D2  ' || case when exists (
  select 1 from unnest(array['run_id','token','dataset','capturado_em']) t(proibido)
   where (select pg_get_constraintdef(oid) from pg_constraint
           where conname='conteudo_canal_id_content_id_key') like '%' || t.proibido || '%')
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- MUT 6 · o checkpoint perde o progresso persistido
-- (BR-20: sem estes campos, o que foi feito só existia na memória do
-- processo, e um processo que morre levava a coleta junto)
alter table public.checkpoint_coleta drop column itens_persistidos;
select 'MUT6 K5  ' || case when (
  select count(*) from information_schema.columns
   where table_schema='public' and table_name='checkpoint_coleta'
     and column_name in ('unidades_totais','unidades_feitas','itens_persistidos')) <> 3
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;
