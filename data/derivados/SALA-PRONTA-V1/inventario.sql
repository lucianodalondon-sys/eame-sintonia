-- SALA-PRONTA-V1 · inventario da Sala real, SO metadados. Nunca le a coluna texto.
-- Corre com PGOPTIONS="-c default_transaction_read_only=on".
\echo '== 0 sessao so-leitura'
show default_transaction_read_only;
\echo '== 1 total'
select count(*) from public.sala_de_espera;
\echo '== 2 por universo'
select universo, count(*) from public.sala_de_espera group by 1 order by 1;
\echo '== 3 por fonte'
select source_id, universo, count(*) from public.sala_de_espera group by 1,2 order by 3 desc, 1;
\echo '== 4 por estagio e estado da fila'
select estagio, estado_da_fila, count(*) from public.sala_de_espera group by 1,2 order by 3 desc;
\echo '== 5 pousado_em (quando entrou na Sala): min, max, por dia'
select min(pousado_em), max(pousado_em) from public.sala_de_espera;
select to_char(pousado_em,'YYYY-MM-DD') dia, count(*) from public.sala_de_espera group by 1 order by 1;
\echo '== 6 os quatro tempos: conhecido vs NAO SEI'
select 'fact_time' campo, sum(case when coalesce(fact_time,'') ~* '^\s*(n[aã]o\s*sei|)$' or fact_time ilike 'NAO SEI%' or fact_time ilike 'NÃO SEI%' then 1 else 0 end) nao_sei, count(*) total from public.sala_de_espera
union all select 'published_at', sum(case when coalesce(published_at,'')='' or published_at ilike 'NAO SEI%' or published_at ilike 'NÃO SEI%' then 1 else 0 end), count(*) from public.sala_de_espera
union all select 'observed_at', sum(case when coalesce(observed_at,'')='' or observed_at ilike 'NAO SEI%' or observed_at ilike 'NÃO SEI%' then 1 else 0 end), count(*) from public.sala_de_espera
union all select 'captured_at', sum(case when coalesce(captured_at,'')='' or captured_at ilike 'NAO SEI%' or captured_at ilike 'NÃO SEI%' then 1 else 0 end), count(*) from public.sala_de_espera;
\echo '== 7 base do fact_time e do fact_location'
select 'fact_time_basis' campo, left(coalesce(fact_time_basis,'<nulo>'),60) valor, count(*) from public.sala_de_espera group by 1,2
union all select 'fact_location_basis', left(coalesce(fact_location_basis,'<nulo>'),60), count(*) from public.sala_de_espera group by 1,2 order by 1,3 desc;
\echo '== 8 fact_location conhecido vs NAO SEI, e igual ao source_location?'
select sum(case when fact_location ilike 'NAO SEI%' or fact_location ilike 'NÃO SEI%' or coalesce(fact_location,'')='' then 1 else 0 end) nao_sei,
       sum(case when not (fact_location ilike 'NAO SEI%' or fact_location ilike 'NÃO SEI%' or coalesce(fact_location,'')='') then 1 else 0 end) conhecido,
       sum(case when fact_location = source_location then 1 else 0 end) igual_ao_da_fonte, count(*) from public.sala_de_espera;
\echo '== 9 published_at igual a captured_at (carimbo da nossa visita?)'
select sum(case when published_at = captured_at then 1 else 0 end) iguais, count(*) from public.sala_de_espera;
\echo '== 10 tipo do envelope FATO'
select json_typeof(fato) tipo, count(*) from public.sala_de_espera group by 1;
\echo '== 11 chaves do envelope FATO (quando e objeto)'
select k, count(*) from public.sala_de_espera, json_object_keys(case when json_typeof(fato)='object' then fato else '{}'::json end) k group by 1 order by 2 desc, 1;
\echo '== 12 evidencia declarada pela fonte'
select left(coalesce(source_declared_evidence_class,'<nulo>'),60), count(*) from public.sala_de_espera group by 1 order by 2 desc;
\echo '== 13 source_location (o lugar da FONTE, nunca o do fato)'
select left(coalesce(source_location,'<nulo>'),40), count(*) from public.sala_de_espera group by 1 order by 2 desc;
\echo '== 14 valor do envelope FATO (string)'
select left(fato::text,40), count(*) from public.sala_de_espera group by 1 order by 2 desc;
\echo '== 15 admitido_por'
select left(coalesce(admitido_por,'<nulo>'),50), count(*) from public.sala_de_espera group by 1 order by 2 desc;
\echo '== 16 consumido (a Intelligence ja leu algum?)'
select count(consumido_em) consumidos, count(*) from public.sala_de_espera;
