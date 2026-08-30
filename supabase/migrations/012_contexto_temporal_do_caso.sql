-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 012
-- O QUE O PORTAL RECEBE. Uma consulta, não catorze joins.
--
-- Fluxo: dado canônico → visão de inteligência temporal → display → portal.
-- O casco visual não precisa saber o schema interno.
--
-- NÃO EXECUTADA em Supabase. Executada e conferida num PostgreSQL 16
-- local e descartável: 001–012 montadas do zero, fixture ES carregada e
-- supabase/tests/regressoes_calendario.sql verde (45/45). Aplicar em
-- produção continua sendo trabalho do workflow supabase-migrate.
-- ═══════════════════════════════════════════════════════════════════════

-- ── Semântica de linha de produto ─────────────────────────────────────
-- A classe do issue já existe em public.issue desde 004. Aqui ela vira
-- a semântica que o Design consome. Nenhuma cor: cor é do Design System.
create or replace view public.v_product_line_semantics with (security_invoker = on) as
select codigo as issue, classe as issue_class,
       case classe
         when 'DISEASE'    then 'DISEASE_CONTROL'
         when 'PEST'       then 'PEST_CONTROL'
         when 'WEED'       then 'WEED_CONTROL'
         when 'RESISTANCE' then 'RESISTANCE_MANAGEMENT'
         else 'NOT_MAPPED'
       end as product_line
  from public.issue;

comment on view public.v_product_line_semantics is
  'Semântica, não cor. NOT_MAPPED é resposta válida — APPLICATION_TIMING, ABIOTIC e '
  'OTHER não correspondem a uma linha de produto e não devem receber uma à força.';


-- ── CONTEXTO TEMPORAL DO CASO — a carga compacta ──────────────────────
create or replace function public.f_case_temporal_context(
  p_pais pais,
  p_crop text,
  p_issue text default null,
  p_geografia_id bigint default null,
  p_as_of date default current_date,
  p_proposito text default 'FIELD_DECISION',
  p_rule_version text default 'v1'
) returns jsonb language sql stable as $$
with fen as (
  select * from public.f_bbch_observado(p_pais, p_crop, p_geografia_id, p_as_of)
), fase as (
  -- Uma fase pode ser conhecida por DATA ou por FENOLOGIA OBSERVADA. As duas
  -- são respostas válidas e diferentes, e o campo `known_by` diz qual foi usada.
  -- Quando as duas existem, a fenologia medida vem primeiro: ela é medição,
  -- o calendário por data é expectativa. A ordem é explícita para que a mesma
  -- pergunta devolva sempre a mesma resposta.
  select 1 as prioridade, cc.fase::text as f, 'OBSERVED' as estado,
         cc.resolucao::text as r, cc.tipo::text as tipo, cc.fonte as fonte,
         'BY_OBSERVED_PHENOLOGY' as como
    from public.crop_calendar cc
    join public.crop c on c.id = cc.crop_id
   where cc.pais = p_pais and c.codigo = p_crop
     and (p_geografia_id is null or cc.geografia_id is not distinct from p_geografia_id)
     and cc.bbch_inicio is not null
     and (select bbch from fen) between cc.bbch_inicio and cc.bbch_fim
  union all
  select 2, fc.fase::text, 'ACTIVE', fc.resolucao::text, fc.tipo::text, fc.fonte,
         'BY_DATE'
    from public.f_crop_calendar(p_pais, p_crop, p_geografia_id, p_as_of) fc
   where fc.estado = 'ACTIVE'
), jissue as (
  select iw.tipo::text as tipo, iw.resolucao::text as r,
         public.estado_janela_por_data(iw.resolucao, iw.data_inicio, iw.data_fim,
                                       iw.mes_inicio, iw.mes_fim, p_as_of) as estado,
         iw.texto_original, iw.fonte
    from public.issue_window iw
    join public.crop_issue ci on ci.id = iw.crop_issue_id
    join public.crop  c on c.id = ci.crop_id
    join public.issue i on i.id = ci.issue_id
   where iw.pais = p_pais and c.codigo = p_crop
     and (p_issue is null or i.codigo = p_issue)
   limit 1
), jprod as (
  -- Um registro pode ser de nível CULTURA (rótulo sem alvo nomeado) ou de nível
  -- ALVO. Perguntar por um issue não pode fazer o registro de nível cultura
  -- desaparecer: sumiço silencioso vira 'não há janela de produto', que é outra
  -- afirmação. Ele vem, marcado como CROP_LEVEL.
  select w.registration_id, w.nome_comercial, w.resolucao::text as r,
         w.bbch_inicio, w.bbch_fim, w.prazo_seguranca_dias, w.timing_texto_original,
         case when w.alvo_explicito then 'ISSUE_LEVEL' else 'CROP_LEVEL' end as escopo,
         w.estado_registro, w.fecha_caducidad,
         -- EXPIRY != WITHDRAWAL. A data de caducidade ter passado é um fato
         -- datado; dizer que o produto foi retirado do mercado seria outro,
         -- e este banco não o tem.
         case when w.fecha_caducidad is null then 'NOT_KNOWN'
              when w.fecha_caducidad < p_as_of then 'EXPIRY_DATE_PASSED'
              else 'WITHIN_EXPIRY_DATE' end as caducidade,
         case when w.resolucao = 'PHENOLOGY_STAGE'
              then public.estado_janela_por_bbch(w.bbch_inicio, w.bbch_fim,
                                                 (select bbch from fen))
              else public.estado_janela_por_data(w.resolucao, null, null, null, null, p_as_of)
         end as estado
    from public.v_product_registered_windows w
   where w.pais = p_pais and w.crop = p_crop
     and (p_issue is null or w.issue = p_issue or w.issue is null)
), obs as (
  select * from public.f_latest_observations(p_pais, p_crop, p_issue, p_as_of,
                                             p_proposito, p_rule_version) limit 1
)
select jsonb_build_object(
  'as_of_date', p_as_of,
  'country', p_pais,
  'crop', p_crop,
  'issue', coalesce(p_issue, 'NOT_SPECIFIED'),

  'current_crop_phase', coalesce(
     (select jsonb_build_object('phase', f, 'state', estado, 'known_by', como,
                                'temporal_resolution', r, 'calendar_type', tipo,
                                'source', fonte)
        from fase order by prioridade limit 1),
     jsonb_build_object('phase','NOT_KNOWN','state','NO_DATA')),

  'current_issue_window_state', coalesce(
     (select jsonb_build_object('type', tipo, 'state', estado,
                                'temporal_resolution', r,
                                'original_text', texto_original, 'source', fonte) from jissue),
     jsonb_build_object('type','NOT_KNOWN','state','NO_DATA')),

  'product_window_state', coalesce(
     (select jsonb_agg(jsonb_build_object(
        'registration_id', registration_id, 'product', nome_comercial,
        'state', estado, 'temporal_resolution', r,
        'target_scope', escopo,
        'bbch_start', bbch_inicio, 'bbch_end', bbch_fim,
        'phi_days', prazo_seguranca_dias, 'original_text', timing_texto_original,
        'registration_state', estado_registro,
        'registration_expiry_date', fecha_caducidad,
        'registration_expiry_state', caducidade)
        order by nome_comercial)
      from jprod),
     '[]'::jsonb),

  'observed_phenology', coalesce(
     (select jsonb_build_object('bbch', bbch, 'observed_at', observado_em, 'source', fonte)
        from fen),
     jsonb_build_object('bbch', null, 'state', 'NOT_KNOWN')),

  'last_field_observation', coalesce(
     (select jsonb_build_object('observed_until', observado_ate, 'age_days', idade_dias,
                                'value', valor, 'unit', unidade,
                                'denominator', base_denominador,
                                'denominator_description', base_descricao,
                                'geography', unidade_geografica) from obs),
     jsonb_build_object('state','NOT_KNOWN')),

  'observation_freshness', coalesce((select frescor from obs), 'AGE_NOT_KNOWN'),
  'freshness_purpose', p_proposito,
  'freshness_rule_version', p_rule_version,

  'next_relevant_window', coalesce(
     (select jsonb_agg(jsonb_build_object('origin', origem, 'what', fase_ou_tipo,
                                          'when', quando, 'source', fonte))
        from public.f_next_relevant_window(p_pais, p_crop, p_as_of)),
     '[]'::jsonb),

  -- Contar o que NÃO se sabe é parte da resposta, não um detalhe.
  'temporal_unknown_count',
     (case when not exists (select 1 from fase)   then 1 else 0 end) +
     (case when not exists (select 1 from jissue) then 1 else 0 end) +
     (case when not exists (select 1 from jprod)  then 1 else 0 end) +
     (case when not exists (select 1 from obs)    then 1 else 0 end) +
     (case when not exists (select 1 from fen)    then 1 else 0 end),

  -- A lei do produto, carregada no próprio payload para que nenhuma camada
  -- acima precise lembrar dela.
  'law', jsonb_build_object(
     'registered_window_is_not_need',
        'Janela registrada aberta não significa necessidade de aplicar.',
     'current_field_need', 'NOT_KNOWN',
     'commercial_availability', 'NOT_KNOWN',
     'expiry_is_not_withdrawal',
        'Data de caducidade vencida não significa produto retirado do mercado.')
);
$$;

comment on function public.f_case_temporal_context is
  'Carga compacta do caso. Devolve os quatro relógios separados e conta os '
  'desconhecidos. Nunca devolve necessidade de aplicação nem disponibilidade '
  'comercial: as duas são NOT_KNOWN por contrato, não por falta de dado.';


-- ── ISOLAMENTO DE PAÍS ────────────────────────────────────────────────
-- Toda função acima recebe p_pais e filtra por ele. Esta função existe para
-- que o teste consiga PROVAR isso, e não apenas afirmar.
create or replace function public.f_paises_no_resultado_do_calendario(p_pais pais)
returns table (origem text, paises text[]) language sql stable as $$
  select 'crop_calendar', array_agg(distinct cc.pais::text)
    from public.crop_calendar cc
    join public.crop c on c.id = cc.crop_id
   where cc.id in (select id from public.f_crop_calendar(p_pais))
  union all
  select 'issue_window', array_agg(distinct iw.pais::text)
    from public.issue_window iw where iw.pais = p_pais
  union all
  select 'product_window', array_agg(distinct w.pais::text)
    from public.v_product_registered_windows w where w.pais = p_pais;
$$;
