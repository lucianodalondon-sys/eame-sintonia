-- MICRO-VERIFICACAO (D74) · as consultas de DEPOIS, so leitura, sobre os itens NOVOS da micro.
--
--   psql -X -v ON_ERROR_STOP=1 -v inicio='<INICIO ISO da micro, ex.: 2026-09-26T09:00:00Z>' -f MICRO-VERIFICACAO-SELECTS.sql "<DSN da Sala>"
--
-- (opcoes ANTES da DSN: o psql do Windows nao as permuta.) A transacao e READ ONLY e acaba em ROLLBACK:
-- qualquer escrita por engano falha. Le a VISTA `sala_de_espera_atual` (033: o valor atual = a ultima
-- revisao, senao o original), filtrada pelas 5 fontes e pelo instante de inicio da micro.
-- Q0 corre ANTES da micro (com inicio = agora) e DEPOIS, para provar que a Sala nao desceu.

begin transaction read only;

-- Q0 · a Sala inteira: quantas linhas e a ultima pousada (antes e depois)
select count(*) as linhas, max(pousado_em) as ultima_pousada,
       (select count(*) from public.sala_de_espera_revisao) as revisoes
  from public.sala_de_espera;

-- Q1 · os itens NOVOS da micro
select source_id, run_id, ordem, item_id, universo, estagio, pousado_em, revisoes
  from public.sala_de_espera_atual
 where pousado_em >= (:'inicio')::timestamptz
   and source_id in ('IT-T10-018','IT-T2-034','IT-T5-160','IT-T7-017','IT-T2-051')
 order by pousado_em, source_id;

-- Q2 · tempo e lugar, cada valor com a base
select source_id, item_id,
       published_at,    published_at_basis,
       source_location, source_location_basis,
       fact_time,       fact_time_basis,
       fact_location,   fact_location_basis
  from public.sala_de_espera_atual
 where pousado_em >= (:'inicio')::timestamptz
   and source_id in ('IT-T10-018','IT-T2-034','IT-T5-160','IT-T7-017','IT-T2-051')
 order by source_id, item_id;

-- Q3 · a completude e a evidencia (inclui PUBLISHED_AT_PRECISION — aviso da SOCIAL-TEMPO)
select source_id, item_id,
       completude_tempo_lugar::text                          as completude,
       tempo_lugar_evidencia->>'PUBLISHED_AT_PRECISION'      as publicacao_precisao,
       tempo_lugar_evidencia->>'PUBLISHED_AT_CONFLITO'       as publicacao_conflito,
       tempo_lugar_evidencia->>'PUBLISHED_AT_OUTRA'          as publicacao_outra,
       tempo_lugar_evidencia->>'SOURCE_LOCATION_PRECISION'   as lugar_fonte_precisao,
       tempo_lugar_evidencia->>'FACT_TIME_KIND'              as data_fato_tipo,
       tempo_lugar_evidencia->>'FACT_TIME_PRECISION'         as data_fato_precisao,
       tempo_lugar_evidencia->>'FACT_TIME_VEIO_DE'           as data_fato_veio_de,
       tempo_lugar_evidencia->>'FACT_LOCATION_KIND'          as lugar_fato_tipo,
       tempo_lugar_evidencia->>'FACT_LOCATION_PRECISION'     as lugar_fato_precisao,
       tempo_lugar_evidencia->>'LEITOR'                      as leitor,
       tempo_lugar_evidencia->>'ORIGEM'                      as origem
  from public.sala_de_espera_atual
 where pousado_em >= (:'inicio')::timestamptz
   and source_id in ('IT-T10-018','IT-T2-034','IT-T5-160','IT-T7-017','IT-T2-051')
 order by source_id, item_id;

-- Q4 · o resumo por fonte: quantos saem de NAO SEI em cada campo (valor E base)
select source_id, count(*) as itens,
       count(*) filter (where published_at    <> 'NAO SEI')                     as publicacao,
       count(*) filter (where published_at_basis <> 'NAO SEI')                  as publicacao_com_base,
       count(*) filter (where source_location <> 'NAO SEI')                     as lugar_fonte,
       count(*) filter (where fact_time       <> 'NAO SEI')                     as data_fato,
       count(*) filter (where fact_time_basis <> 'NAO SEI')                     as data_fato_base,
       count(*) filter (where fact_location   <> 'NAO SEI')                     as lugar_fato,
       count(*) filter (where fact_location_basis <> 'NAO SEI')                 as lugar_fato_base,
       count(*) filter (where tempo_lugar_evidencia->>'PUBLISHED_AT_PRECISION' <> 'NAO SEI') as publicacao_precisao
  from public.sala_de_espera_atual
 where pousado_em >= (:'inicio')::timestamptz
   and source_id in ('IT-T10-018','IT-T2-034','IT-T5-160','IT-T7-017','IT-T2-051')
 group by source_id order by source_id;

-- Q5 · a prova de que foi o CODIGO NOVO que escreveu: nenhum item novo com os defaults da 033
--      (as linhas antigas trazem ORIGEM «pousado antes da migration 033…»). Esperado: 0 e 0.
select count(*) filter (where completude_tempo_lugar->>'ORIGEM' like 'pousado antes da migration 033%') as completude_default,
       count(*) filter (where tempo_lugar_evidencia->>'ORIGEM'  like 'pousado antes da migration 033%') as evidencia_default
  from public.sala_de_espera_atual
 where pousado_em >= (:'inicio')::timestamptz
   and source_id in ('IT-T10-018','IT-T2-034','IT-T5-160','IT-T7-017','IT-T2-051');

rollback;
