-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — REGRESSÕES DO CALENDÁRIO AGRONÔMICO
--
-- Cada teste impede UMA confusão nomeada pelo contrato. Não é um teste de
-- schema: é um teste de SIGNIFICADO. Um schema pode estar sintaticamente
-- perfeito e ainda assim responder "CLOSED" para algo que só é desconhecido.
--
-- Roda contra um Postgres com 001–012 aplicadas e a fixture ES carregada:
--   psql "$DB_URL" -v ON_ERROR_STOP=1 -f supabase/tests/regressoes_calendario.sql
--
-- Só lê. Os testes negativos escrevem dentro de uma subtransação que é
-- SEMPRE desfeita — nenhuma linha sobrevive a este arquivo.
-- ═══════════════════════════════════════════════════════════════════════

\set ON_ERROR_STOP on
\set AS_OF '2026-08-30'

create temp table _r (ordem serial, nome text, ok boolean, detalhe text);

create or replace function pg_temp.afirma(n text, cond boolean, det text default '')
returns void language plpgsql as $f$
begin
  insert into _r (nome, ok, detalhe) values (n, coalesce(cond, false), det);
end $f$;

-- Testa que o banco RECUSA o que a lei proíbe. O que for escrito aqui é
-- desfeito pela exceção que a própria função levanta.
create or replace function pg_temp.recusa(n text, comando text)
returns void language plpgsql as $f$
begin
  begin
    execute comando;
    raise exception 'ACEITOU_O_QUE_DEVERIA_RECUSAR';
  exception when others then
    if sqlerrm = 'ACEITOU_O_QUE_DEVERIA_RECUSAR' then
      insert into _r (nome, ok, detalhe) values (n, false, 'o banco ACEITOU o que a lei proíbe');
    else
      insert into _r (nome, ok, detalhe) values (n, true, 'recusado: ' || left(sqlerrm, 70));
    end if;
  end;
end $f$;

create or replace function pg_temp.caso(p_crop text, p_issue text)
returns jsonb language sql stable as $f$
  select public.f_case_temporal_context('ES', p_crop, p_issue, null, date '2026-08-30');
$f$;

create or replace function pg_temp.tem_coluna(t text, c text)
returns boolean language sql stable as $f$
  select exists (select 1 from information_schema.columns
                  where table_schema='public' and table_name=t and column_name=c);
$f$;


-- ═══ 1 · CROP_CALENDAR != PRODUCT_WINDOW ═════════════════════════════
-- Onde a cultura está e até quando o rótulo autoriza são dois donos.
select pg_temp.afirma('01 CROP_CALENDAR != PRODUCT_WINDOW · donos separados',
  not pg_temp.tem_coluna('crop_calendar','registro_uso_id')
  and not pg_temp.tem_coluna('registro_uso_janela','fase')
  and not pg_temp.tem_coluna('registro_uso_janela','crop_id'),
  'crop_calendar não referencia uso; registro_uso_janela não tem fase nem cultura própria');

select pg_temp.afirma('01b CROP_CALENDAR != PRODUCT_WINDOW · chaves distintas no payload',
  (pg_temp.caso('OLIVE','REPILO')->'current_crop_phase') is not null
  and (pg_temp.caso('OLIVE','REPILO')->'product_window_state') is not null
  and pg_temp.caso('OLIVE','REPILO')->'current_crop_phase'->>'phase' = 'MATURATION'
  and pg_temp.caso('OLIVE','REPILO')->'product_window_state'->0->>'state' = 'ACTIVE',
  'fase MATURATION e janela ACTIVE convivem sem uma virar a outra');


-- ═══ 2 · PRODUCT_WINDOW_OPEN != APPLY_NOW ════════════════════════════
select pg_temp.afirma('02 PRODUCT_WINDOW_OPEN != APPLY_NOW',
  exists (select 1 from jsonb_array_elements(pg_temp.caso('OLIVE','REPILO')->'product_window_state') p
           where p->>'state' = 'ACTIVE')
  and pg_temp.caso('OLIVE','REPILO')->'law'->>'current_field_need' = 'NOT_KNOWN',
  'há janela ACTIVE e mesmo assim current_field_need = NOT_KNOWN');

select pg_temp.afirma('02b nenhuma chave do payload recomenda aplicar',
  not exists (select 1 from jsonb_object_keys(pg_temp.caso('OLIVE','REPILO')) k
               where k ~* '(apply|aplicar|recommend|recomend|should)'),
  'o payload não tem campo de recomendação');


-- ═══ 3 · ISSUE_WINDOW != FIELD_PRESSURE ══════════════════════════════
-- A pressão atual mora em observacao. Nem como coluna ela entra na janela.
select pg_temp.afirma('03 ISSUE_WINDOW != FIELD_PRESSURE · sem coluna de pressão',
  not exists (select 1 from information_schema.columns
               where table_schema='public' and table_name='issue_window'
                 and column_name ~ '(pressao|pressão|incidencia|severidade|intensidade|valor|nivel_ataque)'),
  'issue_window não tem nenhuma coluna de magnitude');

select pg_temp.afirma('03b a pressão tem dono, e é observacao',
  pg_temp.tem_coluna('observacao','valor') and pg_temp.tem_coluna('observacao','base_denominador'),
  'observacao guarda valor com denominador');


-- ═══ 4 · OBSERVATION_DATE != PUBLICATION_DATE ════════════════════════
-- O risco real: calcular idade a partir da data de captura em vez da data
-- do que foi observado. 77 dias, não 0.
select pg_temp.afirma('04 OBSERVATION_DATE != PUBLICATION_DATE · idade vem do observado',
  (pg_temp.caso('OLIVE','REPILO')->'last_field_observation'->>'age_days')::int
    = (date '2026-08-30' - (select periodo_fim from public.observacao
                             where camada='FIELD' order by periodo_fim desc limit 1)),
  'idade = as_of − periodo_fim');

select pg_temp.afirma('04b a idade NÃO foi calculada da data de medição',
  (pg_temp.caso('OLIVE','REPILO')->'last_field_observation'->>'age_days')::int
    <> (date '2026-08-30' - (select medido_em::date from public.observacao
                              where camada='FIELD' order by periodo_fim desc limit 1)),
  'medido_em daria 0 dias; a resposta é 77');


-- ═══ 5 · PUBLICATION_DATE != CAPTURE_DATE ════════════════════════════
select pg_temp.afirma('05 PUBLICATION_DATE != CAPTURE_DATE · colunas separadas',
  pg_temp.tem_coluna('conteudo','publicado_em') and pg_temp.tem_coluna('conteudo','coletado_em'),
  'conteudo guarda publicação e coleta em colunas diferentes');

select pg_temp.afirma('05b o calendário guarda a versão da fonte sem virar captura',
  exists (select 1 from public.crop_calendar
           where fonte_versao is not null and capturado_em::date <> date '2026-08-26'
             and capturado_em::date = date '2026-08-30'),
  'RAIF: publicado 2026-08-26, capturado 2026-08-30, e os dois estão escritos');


-- ═══ 6 · SOURCE_COUNTRY != FACT_COUNTRY ══════════════════════════════
select pg_temp.afirma('06 SOURCE_COUNTRY != FACT_COUNTRY · conteudo separa os dois',
  pg_temp.tem_coluna('conteudo','source_geografia_id')
  and pg_temp.tem_coluna('conteudo','fact_geografia_id'),
  'a origem do documento e o lugar do fato são colunas distintas');

select pg_temp.recusa('06b um calendário ES não aceita geografia FR', $x$
  with g as (
    insert into public.geografia (pais, regiao) values ('FR','Occitanie') returning id
  )
  insert into public.crop_calendar
    (pais, crop_id, geografia_id, tipo, fase, resolucao, mes_inicio, mes_fim,
     texto_original, recorrente, fonte, nivel_evidencia, capturado_em, rule_version)
  select 'ES', c.id, g.id, 'TYPICAL_CALENDAR', 'SOWING', 'MONTH', 3, 4,
         'teste de regressão', true, 'TESTE', 'DERIVED', now(), 'test'
    from public.crop c, g where c.codigo = 'MAIZE'
$x$);


-- ═══ 7 · TYPICAL_CALENDAR != OBSERVED_CAMPAIGN ═══════════════════════
select pg_temp.recusa('07 TYPICAL_CALENDAR != OBSERVED_CAMPAIGN · campanha observada não recorre', $x$
  insert into public.crop_calendar
    (pais, crop_id, campanha, tipo, fase, resolucao, bbch_inicio, bbch_fim,
     recorrente, fonte, nivel_evidencia, capturado_em, rule_version)
  select 'ES', c.id, '2026', 'OBSERVED_CAMPAIGN', 'MATURATION', 'PHENOLOGY_STAGE', 70, 80,
         true, 'TESTE', 'DERIVED', now(), 'test'
    from public.crop c where c.codigo = 'OLIVE'
$x$);

select pg_temp.recusa('07b campanha observada tem de dizer qual campanha', $x$
  insert into public.crop_calendar
    (pais, crop_id, campanha, tipo, fase, resolucao, bbch_inicio, bbch_fim,
     recorrente, fonte, nivel_evidencia, capturado_em, rule_version)
  select 'ES', c.id, null, 'OBSERVED_CAMPAIGN', 'MATURATION', 'PHENOLOGY_STAGE', 70, 80,
         false, 'TESTE', 'DERIVED', now(), 'test'
    from public.crop c where c.codigo = 'OLIVE'
$x$);


-- ═══ 8 · FIRST_YEAR != RECURRING_CALENDAR ════════════════════════════
-- A campanha 2026 do olival e os avisos 2025/26 do palmeri são o que foi
-- visto uma vez. Não podem aparecer como "a próxima janela".
select pg_temp.afirma('08 FIRST_YEAR != RECURRING_CALENDAR · o visto uma vez não projeta',
  not exists (
    select 1 from public.f_next_relevant_window('ES','OLIVE',date '2026-08-30')
     where recorrente = false)
  and not exists (
    select 1 from public.f_next_relevant_window('ES','MAIZE',date '2026-08-30')
     where recorrente = false),
  'f_next_relevant_window só devolve recorrente = true');

select pg_temp.afirma('08b a campanha observada de 2026 existe, e mesmo assim não é próxima janela',
  exists (select 1 from public.crop_calendar
           where tipo='OBSERVED_CAMPAIGN' and campanha='2026' and pais='ES')
  and not exists (select 1 from public.f_next_relevant_window('ES','OLIVE',date '2026-08-30')),
  'o olival tem campanha 2026 e nenhuma próxima janela — a ausência é resposta');


-- ═══ 9 · MONTH_RESOLUTION != EXACT_DATE ══════════════════════════════
select pg_temp.recusa('09 MONTH_RESOLUTION != EXACT_DATE · MONTH não aceita data', $x$
  insert into public.crop_calendar
    (pais, crop_id, tipo, fase, resolucao, mes_inicio, mes_fim, data_inicio, data_fim,
     recorrente, fonte, nivel_evidencia, capturado_em, rule_version)
  select 'ES', c.id, 'TYPICAL_CALENDAR', 'SOWING', 'MONTH', 10, 11,
         '2026-10-01', '2026-11-30', true, 'TESTE', 'DERIVED', now(), 'test'
    from public.crop c where c.codigo = 'WHEAT'
$x$);

select pg_temp.afirma('09b a linha MONTH do trigo não expõe data nenhuma',
  exists (select 1 from public.crop_calendar cc join public.crop c on c.id=cc.crop_id
           where c.codigo='WHEAT' and cc.resolucao='MONTH'
             and cc.data_inicio is null and cc.data_fim is null),
  'outubro/novembro continua sendo mês, não 2026-10-01');


-- ═══ 10 · BBCH_RANGE != CALENDAR_DATE ════════════════════════════════
select pg_temp.afirma('10 BBCH_RANGE != CALENDAR_DATE · fenologia não vira data',
  public.estado_janela_por_data('PHENOLOGY_STAGE', null, null, null, null, date '2026-08-30')
    = 'NOT_KNOWN',
  'uma janela em BBCH avaliada por data devolve NOT_KNOWN');

select pg_temp.afirma('10b sem fenologia observada, a janela BBCH é NOT_KNOWN — nunca CLOSED',
  public.estado_janela_por_bbch(10::smallint, 85::smallint, null) = 'NOT_KNOWN',
  'BBCH sem observação não fecha janela');


-- ═══ 11 · NEXT_CYCLE != EXACT_NEXT_DATE ══════════════════════════════
select pg_temp.afirma('11 NEXT_CYCLE != EXACT_NEXT_DATE · nenhuma data inventada',
  not exists (select 1 from public.f_next_relevant_window('ES','MAIZE',date '2026-08-30')
               where quando ~ '\d{4}-\d{2}-\d{2}' or quando ~ '202[7-9]'),
  '"a partir de abril" não virou 2027-04-01');

select pg_temp.afirma('11b o texto original da fonte é o que sai',
  (select quando from public.f_next_relevant_window('ES','MAIZE',date '2026-08-30') limit 1)
    = 'em Aragón o milho é semeado a partir de abril',
  'a frase da fonte chega inteira ao portal');


-- ═══ 12 · UNKNOWN != CLOSED ══════════════════════════════════════════
select pg_temp.afirma('12 UNKNOWN != CLOSED · NEPTUNE é NOT_KNOWN, não CLOSED',
  (select p->>'state' from jsonb_array_elements(
      pg_temp.caso('OLIVE','REPILO')->'product_window_state') p
    where p->>'product' = 'NEPTUNE') = 'NOT_KNOWN',
  '"antes de la floración" não sustenta nem ACTIVE nem CLOSED');

select pg_temp.afirma('12b nenhuma resolução imprecisa produz CLOSED',
  not exists (
    select 1 from jsonb_array_elements(pg_temp.caso('OLIVE','REPILO')->'product_window_state') p
     where p->>'temporal_resolution' in ('APPROXIMATE','SEASON','NOT_KNOWN')
       and p->>'state' = 'CLOSED'),
  'APPROXIMATE, SEASON e NOT_KNOWN nunca fecham');


-- ═══ 13 · NO_DATA != NO_WINDOW ═══════════════════════════════════════
-- O olival não tem janela de issue registrada. Isso é ausência de linha,
-- não ausência de janela no campo.
select pg_temp.afirma('13 NO_DATA != NO_WINDOW · o repilo responde NO_DATA',
  pg_temp.caso('OLIVE','REPILO')->'current_issue_window_state'->>'state' = 'NO_DATA'
  and pg_temp.caso('OLIVE','REPILO')->'current_issue_window_state'->>'type' = 'NOT_KNOWN',
  'sem linha de issue_window a resposta é NO_DATA');

select pg_temp.afirma('13b o payload nunca afirma que a janela não existe',
  pg_temp.caso('OLIVE','REPILO')::text !~ 'NO_WINDOW|SEM_JANELA|NAO_HA_JANELA',
  'não existe estado que diga "não há janela"');

select pg_temp.afirma('13c o desconhecido é contado, não escondido',
  (pg_temp.caso('OLIVE','REPILO')->>'temporal_unknown_count')::int >= 1,
  'temporal_unknown_count declara quantos relógios ficaram sem resposta');


-- ═══ 14 · CLOSED != NO_ACTION ════════════════════════════════════════
-- O milho tem janela de issue CLOSED em 2026-08-30 e continua tendo o que
-- preparar. Fechar a janela não apaga o caso.
select pg_temp.afirma('14 CLOSED != NO_ACTION · janela fechada, preparação viva',
  pg_temp.caso('MAIZE','AMARANTHUS_PALMERI')->'current_issue_window_state'->>'state' = 'CLOSED'
  and jsonb_array_length(pg_temp.caso('MAIZE','AMARANTHUS_PALMERI')->'next_relevant_window') > 0,
  'CLOSED e next_relevant_window não-vazia no mesmo payload');

select pg_temp.afirma('14b janela fechada não apaga o registro do produto',
  jsonb_array_length(pg_temp.caso('MAIZE','AMARANTHUS_PALMERI')->'product_window_state') > 0,
  'DIODE 100 continua no payload com a janela do issue fechada');


-- ═══ 15 · APPLICATION_WINDOW != COMMERCIAL_AVAILABILITY ══════════════
select pg_temp.afirma('15 APPLICATION_WINDOW != COMMERCIAL_AVAILABILITY',
  pg_temp.caso('OLIVE','REPILO')->'law'->>'commercial_availability' = 'NOT_KNOWN'
  and not exists (select 1 from information_schema.columns
                   where table_schema='public' and table_name='registro_uso_janela'
                     and column_name ~ '(estoque|disponivel|preco|venda|comercial)'),
  'nem coluna nem afirmação de disponibilidade comercial');


-- ═══ 16 · EXPIRY != WITHDRAWAL ═══════════════════════════════════════
-- NEPTUNE caducou em 2026-08-15, quinze dias antes do as_of. O payload diz
-- que a data passou. Não diz que o produto foi retirado.
select pg_temp.afirma('16 EXPIRY != WITHDRAWAL · a data vencida é dita, a retirada não',
  (select p->>'registration_expiry_state' from jsonb_array_elements(
      pg_temp.caso('OLIVE','REPILO')->'product_window_state') p
    where p->>'product'='NEPTUNE') = 'EXPIRY_DATE_PASSED'
  and pg_temp.caso('OLIVE','REPILO')::text !~ 'WITHDRAWN|RETIRADO|CANCELADO',
  'EXPIRY_DATE_PASSED sem nenhuma palavra de retirada');

select pg_temp.afirma('16b o produto com data vencida continua no payload',
  exists (select 1 from jsonb_array_elements(
            pg_temp.caso('OLIVE','REPILO')->'product_window_state') p
           where p->>'product'='NEPTUNE'),
  'sumir com ele seria afirmar retirada por omissão');


-- ═══ 17 · AS_OF_DATE != STORED_TODAY ═════════════════════════════════
-- "Hoje" nunca é gravado. Duas perguntas com o mesmo as_of dão a mesma
-- resposta; com as_of diferente, a resposta muda.
select pg_temp.afirma('17 AS_OF_DATE != STORED_TODAY · mesma data, mesma resposta',
  public.f_case_temporal_context('ES','MAIZE','AMARANTHUS_PALMERI',null,date '2026-08-30')
    = public.f_case_temporal_context('ES','MAIZE','AMARANTHUS_PALMERI',null,date '2026-08-30'),
  'o payload é reproduzível');

select pg_temp.afirma('17b as_of anterior devolve a mesma janela ainda ACTIVE',
  public.f_case_temporal_context('ES','MAIZE','AMARANTHUS_PALMERI',null,date '2026-06-20')
    ->'current_issue_window_state'->>'estado' is null
  and public.f_case_temporal_context('ES','MAIZE','AMARANTHUS_PALMERI',null,date '2026-06-20')
    ->'current_issue_window_state'->>'state' = 'ACTIVE',
  'em 2026-06-20 a mesma linha estava ACTIVE — o estado é derivado, não gravado');

select pg_temp.afirma('17c nenhuma tabela do calendário guarda um campo "hoje"',
  not exists (select 1 from information_schema.columns
               where table_schema='public'
                 and table_name in ('crop_calendar','issue_window','registro_uso_janela')
                 and column_name ~ '^(hoje|today|as_of|estado_atual|status_atual)$'),
  'o estado corrente não tem coluna');


-- ═══ 18 · ISOLAMENTO DE PAÍS ═════════════════════════════════════════
-- A consulta ES não pode devolver fase da França nem janela da Itália.
select pg_temp.afirma('18 COUNTRY_ISOLATION · a consulta ES só devolve ES',
  not exists (select 1 from public.f_paises_no_resultado_do_calendario('ES')
               where paises is not null and paises <> array['ES']),
  'crop_calendar, issue_window e product_window: todos só ES');

select pg_temp.afirma('18b a consulta FR num acervo só-ES devolve vazio, não ES',
  not exists (select 1 from public.f_crop_calendar('FR'))
  and not exists (select 1 from public.f_next_relevant_window('FR','MAIZE',date '2026-08-30')),
  'perguntar pela França devolve nada — nunca a resposta da Espanha');

select pg_temp.afirma('18c toda função temporal exige o país',
  not exists (
    select 1 from pg_proc p join pg_namespace n on n.oid = p.pronamespace
     where n.nspname='public'
       and p.proname in ('f_crop_calendar','f_next_relevant_window','f_latest_observations',
                         'f_bbch_observado','f_case_temporal_context')
       and not exists (select 1 from unnest(p.proargnames) a where a = 'p_pais')),
  'nenhuma delas pode ser chamada sem país');


-- ═══ 19 · O QUE NÃO PODE VAZAR PARA O CLIENTE ════════════════════════
select pg_temp.afirma('19 o payload não carrega caminho de RAW nem custo',
  pg_temp.caso('OLIVE','REPILO')::text !~* '(raw_asset|storage|bucket|s3://|custo|cost|api_key|token)',
  'nenhuma chave de infraestrutura no que o portal recebe');

select pg_temp.afirma('19b a semântica de linha de produto não guarda cor',
  not exists (select 1 from public.v_product_line_semantics
               where product_line ~ '^#' or issue_class ~ '^#')
  and not exists (select 1 from information_schema.columns
                   where table_schema='public' and table_name='v_product_line_semantics'
                     and column_name ~ '(cor|color|hex)'),
  'cor é do Design System, não deste banco');



-- ═══ 20 · AS TRÊS IGNORÂNCIAS DO FRESCOR NÃO SE MISTURAM ═════════════
-- NO_RULE != STALE != AGE_NOT_KNOWN. Dizer "velha" sem ter limiar seria
-- inventar a régua para poder condenar a evidência.
select pg_temp.afirma('20 NO_RULE_FOR_PURPOSE != STALE_FOR_PURPOSE',
  public.estado_frescor(date '2026-06-14', date '2026-08-30', 'MARKETING', 'v1')
    = 'NO_RULE_FOR_PURPOSE'
  and public.estado_frescor(date '2024-03-14', date '2026-08-30', 'FIELD_DECISION', 'v1')
    = 'STALE_FOR_PURPOSE',
  'propósito sem régua não é evidência velha');

select pg_temp.afirma('20b AGE_NOT_KNOWN != STALE_FOR_PURPOSE',
  public.estado_frescor(null, date '2026-08-30', 'FIELD_DECISION', 'v1') = 'AGE_NOT_KNOWN',
  'sem data de observação não há idade a julgar');

select pg_temp.afirma('20c os limiares são dado, não constante de código',
  (select count(*) from public.freshness_regra where justificativa <> '') >= 4
  and not exists (select 1 from public.freshness_regra where justificativa is null),
  'toda linha da régua diz de onde veio o limite');

select pg_temp.afirma('20d o mesmo dado tem frescor diferente por propósito',
  public.estado_frescor(date '2022-06-14', date '2026-08-30', 'SCIENCE_CONTEXT', 'v1') = 'CURRENT'
  and public.estado_frescor(date '2022-06-14', date '2026-08-30', 'FIELD_DECISION', 'v1')
      = 'STALE_FOR_PURPOSE',
  'um levantamento de 2022 (1.538 dias) é ciência corrente e leitura de campo vencida');

select pg_temp.afirma('20e a régua não estende o propósito além do que ela diz',
  public.estado_frescor(date '2021-06-14', date '2026-08-30', 'SCIENCE_CONTEXT', 'v1')
    = 'STALE_FOR_PURPOSE',
  '1.903 dias passam dos 1.825 cadastrados — a régua vale, inclusive contra nós');

-- ═══════════════════════════════════════════════════════════════════════
\echo ''
\echo '── REGRESSÕES DO CALENDÁRIO AGRONÔMICO ──────────────────────────'
select case when ok then 'PASS' else 'FAIL' end as r, nome, detalhe
  from _r order by ordem;

select 'TOTAL=' || count(*) || '  PASS=' || count(*) filter (where ok)
     || '  FAIL=' || count(*) filter (where not ok) as placar from _r;

do $$
declare n integer;
begin
  select count(*) into n from _r where not ok;
  if n > 0 then
    raise exception 'REGRESSOES_FALHARAM=%', n;
  end if;
  raise notice 'REGRESSOES_CALENDARIO=PASS';
end $$;
