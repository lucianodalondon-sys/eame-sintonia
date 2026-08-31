-- ═══════════════════════════════════════════════════════════════════════
-- COMPETITOR FORESIGHT — mutações
--
-- Cada mutação quebra UMA lei do piloto e exige que a regressão
-- correspondente reprove. Suíte verde em cima de esquema quebrado não é
-- prova — é a mesma sensação de segurança que o piloto existe para negar.
--
-- Tudo roda dentro de begin/rollback: nenhuma mutação sobrevive ao arquivo.
-- ═══════════════════════════════════════════════════════════════════════
\set QUIET on

begin;
-- MUT 1 · a antecedência deixa de exigir identidade provada
--   É a mutação mais perigosa da suíte: com ela, um par ligado só por nome
--   parecido passa a carregar um número de dias. E o número sobrevive à
--   ressalva — foi assim que uma medida virou verdade uma vez nesta casa.
alter table public.evento_concorrente_link
  drop constraint lead_days_exige_identidade_provada;
insert into public.evento_concorrente_link
  (evento_a_id, evento_b_id, estado, evidencia, lead_days)
select min(id), max(id), 'PARTIAL', 'MUTACAO', 999
  from public.evento_concorrente where event_type = 'EXPIRY';
select 'MUT1 A1  ' || case when exists (
  select 1 from public.evento_concorrente_link
   where lead_days is not null and estado <> 'PROVED')
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- MUT 2 · a view de cobertura para de mostrar camada vazia
--   O `left join` vira `join`: as camadas com zero eventos simplesmente
--   somem da listagem. Ninguém vê erro nenhum — vê seis concorrentes com
--   duas camadas cada e conclui que a cadeia tem duas camadas.
create or replace view public.v_competidor_cobertura_camada as
select o.nome_canonico as competidor, e.camada, count(e.id) as eventos,
       'COLETADO' as estado_da_camada
  from public.evento_concorrente e
  join public.organizacao o on o.id = e.competidor_id
 group by o.nome_canonico, e.camada;
select 'MUT2 C2  ' || case when (
  select count(*) from public.v_competidor_cobertura_camada
   where eventos = 0 and estado_da_camada like 'NOT_AVAILABLE%') <> 18
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- MUT 3 · a view de antecedência esconde os pares que REFUTAM
--   Filtrar `lead_days > 0` transforma 1.053 defensáveis em 1.053 de
--   100% de confirmação, obtido apagando a contraprova.
create or replace view public.v_competidor_antecedencia as
select o.nome_canonico as competidor, a.brand, a.effective_date as data_da_marca,
       b.effective_date as data_do_registro, b.registration_id_texto as registro,
       l.lead_days, l.lead_days_defensavel,
       'MARCA_ANTES' as leitura, l.evidencia
  from public.evento_concorrente_link l
  join public.evento_concorrente a on a.id = l.evento_a_id
  join public.evento_concorrente b on b.id = l.evento_b_id
  join public.organizacao o on o.id = a.competidor_id
 where l.estado = 'PROVED' and l.lead_days > 0;
select 'MUT3 A3  ' || case when not exists (
  select 1 from public.v_competidor_antecedencia where lead_days < 0)
  and (select count(*) from public.evento_concorrente_link
        where estado='PROVED' and lead_days < 0) = 557
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- MUT 4 · a tabela vira depósito comum
--   Sem o dono único, qualquer missão despeja linha aqui, e em seis meses
--   a contagem do piloto responde por dado que ele nunca coletou.
alter table public.evento_concorrente drop constraint evento_tem_um_dono_so;
insert into public.evento_concorrente
  (event_key, competidor_id, pais, camada, event_type, observed_at,
   effective_date, fonte, evidencia, brand, confidence_state, dataset_owner)
select 'MUT-DONO', min(id), 'ES', 'IP', 'TRADEMARK_APPLICATION', current_date,
       current_date, 'MUTACAO', 'MUTACAO', 'X', 'NOT_KNOWN', 'OUTRA_MISSAO'
  from public.organizacao;
select 'MUT4 P1  ' || case when (
  select count(distinct dataset_owner) from public.evento_concorrente) > 1
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- MUT 5 · o evento perde a chave natural
--   Rodar a coleta duas vezes passaria a dobrar as linhas. O piloto
--   publicaria o dobro dos eventos sem ter observado nada a mais.
alter table public.evento_concorrente drop constraint evento_concorrente_event_key_key;
insert into public.evento_concorrente
  (event_key, competidor_id, pais, camada, event_type, observed_at,
   effective_date, fonte, evidencia, brand, confidence_state)
select event_key, competidor_id, pais, camada, event_type, observed_at,
       effective_date, fonte, evidencia, brand, confidence_state
  from public.evento_concorrente limit 5;
select 'MUT5 D2  ' || case when (
  select count(*) from public.evento_concorrente) <> 19702
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- MUT 6 · a data do fato passa a ser preenchida com a data da observação
--   É o erro que apaga a distinção inteira: tudo passa a ter "acontecido
--   hoje", e 15 meses de mudanças se empilham num dia só.
update public.evento_concorrente set effective_date = observed_at
 where camada = 'REGULATORY';
select 'MUT6 T3  ' || case when exists (
  select 1 from public.evento_concorrente
   where camada = 'REGULATORY' and effective_date = observed_at)
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;

begin;
-- MUT 7 · a classe 5 volta a valer como sinal agro
--   Foi o erro real desta rodada, corrigido depois de medir: 4.496 marcas
--   ambíguas viraram "sinal agro", e GINECANES da Bayer entrou como
--   defensivo. A mutação o recoloca para provar que a regressão o pega.
update public.evento_concorrente set confidence_state = 'OBSERVED_STRONG_AGRO_SIGNAL'
 where camada = 'IP' and confidence_state = 'OBSERVED_AMBIGUOUS_CLASS';
select 'MUT7 I1  ' || case when not exists (
  select 1 from public.evento_concorrente
   where camada='IP' and confidence_state='OBSERVED_AMBIGUOUS_CLASS')
  then 'PEGOU' else 'NAO PEGOU (teste inutil)' end as resultado;
rollback;
