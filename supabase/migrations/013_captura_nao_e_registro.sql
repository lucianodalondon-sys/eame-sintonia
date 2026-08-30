-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 013
-- CAPTURE != REGISTRATION
--
-- registro_regulatorio é um LOG versionado por captura, e continua sendo.
-- O defeito nunca esteve no dado: estava na leitura. A janela do produto
-- lia o log como se cada linha fosse um registro independente, e com a
-- SEGUNDA captura do mesmo registro o NEPTUNE apareceu 3 vezes no mesmo
-- caso.
--
--   REGISTRATION   a autorização. Uma por (pais, registration_id).
--   CAPTURE        uma observação dela, numa fonte, num instante.
--
-- Nada aqui apaga captura. Apagar histórico para resolver duplicação
-- trocaria um defeito por um pior: o portal pararia de poder responder
-- "o que o registro dizia em abril".
--
-- Contrato completo, escrito ANTES desta migration:
--   data/samples/CAPTURE-VS-REGISTRATION-CONTRACT-V1.json
--
-- NÃO EXECUTADA em Supabase. Executada e conferida num PostgreSQL 16
-- local e descartável: 001–013 montadas do zero, fixtures carregadas e as
-- regressões verdes. Aplicar em produção continua sendo trabalho do
-- workflow supabase-migrate.
-- ═══════════════════════════════════════════════════════════════════════

-- ── A CHAVE DE CAPTURA ────────────────────────────────────────────────
-- A chave de 006 era (pais, registration_id, fonte_versao) e omitia `fonte`.
-- Duas fontes diferentes que escrevessem a mesma string de versão colidiriam
-- e uma sobrescreveria a outra em silêncio. Nenhuma captura de hoje cai
-- nesse caso — todas vêm do MAPA ROPF — mas a trava é sobre o que pode
-- entrar amanhã.
alter table public.registro_regulatorio
  drop constraint if exists registro_regulatorio_pais_registration_id_fonte_versao_key;
alter table public.registro_regulatorio
  add constraint captura_e_unica_por_fonte_e_versao
  UNIQUE NULLS NOT DISTINCT (pais, registration_id, fonte, fonte_versao);

comment on table public.registro_regulatorio is
  'LOG de capturas do registro nacional, não tabela de estado corrente. Uma linha por '
  'OBSERVAÇÃO. A entidade regulatória é (pais, registration_id) e pode ter várias '
  'linhas aqui. Para o estado corrente numa data, usar f_registro_corrente.';


-- ── O INSTANTE DA FONTE ───────────────────────────────────────────────
-- fonte_versao é text de propósito: nem toda fonte versiona com timestamp, e
-- converter à força inventaria precisão. Esta função lê quando dá, devolve
-- NULL quando não dá, e nunca levanta erro no meio de uma consulta.
create or replace function public.instante_da_fonte(p_fonte_versao text)
returns timestamptz language plpgsql immutable as $$
begin
  return p_fonte_versao::timestamptz;
exception when others then
  return null;
end $$;

comment on function public.instante_da_fonte is
  'SOURCE_DATE, quando a fonte a escreve como timestamp. NULL quando ela não escreve — '
  'e NULL aqui significa "não ordena por isto", nunca "é antiga".';


-- ═══════════════════════════════════════════════════════════════════════
-- O REGISTRO CORRENTE NUMA DATA
--
-- A pergunta não é "qual a última captura". É:
--     qual evidência estava disponível até AS_OF_DATE, e qual delas é a
--     declaração mais recente do registro?
--
-- 1 ELEGIBILIDADE  capturado_em <= as_of
--                  não se responde uma pergunta de abril com evidência de agosto
-- 2 ORDEM          maior SOURCE_INSTANT — o que o registro disse por último
-- 3 DESEMPATE      maior capturado_em
-- 4 DESEMPATE      maior id — para que a resposta seja SEMPRE a mesma
-- ═══════════════════════════════════════════════════════════════════════
create or replace function public.f_registro_corrente(
  p_pais pais, p_as_of date default current_date
) returns table (
  registro_id        bigint,
  pais               pais,
  registration_id    text,
  nome_comercial     text,
  titular            text,
  formulado          text,
  estado             text,
  fecha_caducidad    date,
  fecha_limite_venta date,
  fecha_inscricao    date,
  fonte              text,
  fonte_versao       text,
  capturado_em       timestamptz,
  capturas_ate_as_of integer,
  fontes_ate_as_of   text[],
  conflito_de_fonte  boolean
) language sql stable as $$
  select r.id, r.pais, r.registration_id, r.nome_comercial, r.titular, r.formulado,
         r.estado, r.fecha_caducidad, r.fecha_limite_venta, r.fecha_inscripcion,
         r.fonte, r.fonte_versao, r.capturado_em,
         c.n::integer, c.fontes,
         -- Não há prioridade entre fontes, e inventar uma seria decidir no
         -- escuro. Quando duas fontes convivem, a escolha continua
         -- determinística E o conflito fica visível.
         (array_length(c.fontes, 1) > 1)
    from (
      select rr.pais, rr.registration_id,
             count(*) as n,
             array_agg(distinct rr.fonte order by rr.fonte) as fontes,
             (array_agg(rr.id order by
                public.instante_da_fonte(rr.fonte_versao) desc nulls last,
                rr.capturado_em desc,
                rr.id desc))[1] as escolhida
        from public.registro_regulatorio rr
       where rr.pais = p_pais
         and rr.capturado_em::date <= p_as_of
       group by rr.pais, rr.registration_id
    ) c
    join public.registro_regulatorio r on r.id = c.escolhida;
$$;

comment on function public.f_registro_corrente is
  'UMA linha por (pais, registration_id), escolhida entre as capturas disponíveis até '
  'as_of. Não apaga nada: registro_regulatorio continua com todas as capturas. '
  'FUTURE_CAPTURE_CANNOT_REWRITE_PAST_STATE.';


-- ═══════════════════════════════════════════════════════════════════════
-- A JANELA DO PRODUTO, PELO REGISTRO CORRENTE
-- v_product_registered_windows continua existindo e continua devolvendo
-- TODAS as capturas: ela é o log, e o log não mente. Quem quer o estado de
-- uma data usa a função.
-- ═══════════════════════════════════════════════════════════════════════
create or replace function public.f_product_registered_windows(
  p_pais pais, p_as_of date default current_date
) returns table (
  id bigint, pais pais, registration_id text, nome_comercial text, titular text,
  estado_registro text, fecha_caducidad date,
  crop text, issue text, issue_classe text, substancia text,
  resolucao resolucao_temporal, bbch_inicio smallint, bbch_fim smallint,
  aplicacoes_min smallint, aplicacoes_max smallint,
  intervalo_min_dias smallint, intervalo_max_dias smallint,
  prazo_seguranca_dias smallint,
  dose_min numeric, dose_max numeric, dose_unidade text,
  timing_texto_original text, timing_normalizado text,
  nivel_evidencia nivel_evidencia, fonte text, fonte_versao text,
  capturado_em timestamptz, alvo_explicito boolean,
  capturas_ate_as_of integer, conflito_de_fonte boolean,
  usos_de_outra_captura boolean
) language sql stable as $$
  -- O uso e a janela são FILHOS DE UMA CAPTURA, não da autorização. Uma
  -- captura que observou só o cabeçalho do registro não tem uso nenhum
  -- pendurado — e ler os usos direto da captura corrente faria o produto
  -- DESAPARECER do caso. Sumir é pior que duplicar: duplicar se vê.
  --
  -- Regra: o ESTADO vem da captura corrente; os USOS vêm da captura mais
  -- recente que de fato observou usos. Quando as duas não são a mesma, a
  -- linha diz isso em usos_de_outra_captura, em vez de resolver calado.
  with corrente as (
    select * from public.f_registro_corrente(p_pais, p_as_of)
  ), captura_com_uso as (
    select rr.pais, rr.registration_id,
           (array_agg(rr.id order by
              public.instante_da_fonte(rr.fonte_versao) desc nulls last,
              rr.capturado_em desc, rr.id desc))[1] as captura
      from public.registro_regulatorio rr
     where rr.pais = p_pais
       and rr.capturado_em::date <= p_as_of
       and exists (select 1 from public.registro_uso u where u.registro_id = rr.id)
     group by rr.pais, rr.registration_id
  )
  select ruj.id, rc.pais, rc.registration_id, rc.nome_comercial, rc.titular,
         rc.estado, rc.fecha_caducidad,
         c.codigo, i.codigo, i.classe, ru.substancia,
         ruj.resolucao, ruj.bbch_inicio, ruj.bbch_fim,
         ruj.aplicacoes_min, ruj.aplicacoes_max,
         ruj.intervalo_min_dias, ruj.intervalo_max_dias, ruj.prazo_seguranca_dias,
         ruj.dose_min, ruj.dose_max, ruj.dose_unidade,
         ruj.timing_texto_original, ruj.timing_normalizado,
         ruj.nivel_evidencia, ruj.fonte, ruj.fonte_versao, ruj.capturado_em,
         (i.codigo is not null),
         rc.capturas_ate_as_of, rc.conflito_de_fonte,
         (cu.captura <> rc.registro_id)
    from corrente rc
    join captura_com_uso cu
      on cu.pais = rc.pais and cu.registration_id = rc.registration_id
    join public.registro_uso ru         on ru.registro_id = cu.captura
    join public.registro_uso_janela ruj on ruj.registro_uso_id = ru.id
    left join public.crop  c on c.id = ru.crop_id
    left join public.issue i on i.id = ru.issue_id;
$$;

comment on function public.f_product_registered_windows is
  'Janela AUTORIZADA no rótulo, lida pelo registro corrente em as_of. Não diz que há '
  'necessidade de aplicar e não diz que o produto está disponível para compra.';

comment on view public.v_product_registered_windows is
  'LOG: uma linha por captura. Devolve o mesmo registro tantas vezes quantas ele foi '
  'observado, e isso é correto — é o histórico. Para o estado numa data, usar '
  'f_product_registered_windows. CAPTURE != REGISTRATION.';


-- ═══════════════════════════════════════════════════════════════════════
-- O CASO, LIDO PELO REGISTRO CORRENTE
--
-- Mesma função da 012, com UMA diferença: a carga do relógio C passa por
-- f_product_registered_windows em vez do log. Duas chaves novas viajam no
-- payload — captures_up_to_as_of e source_conflict — para que o número de
-- capturas e um eventual conflito de fonte nunca fiquem invisíveis.
-- ═══════════════════════════════════════════════════════════════════════
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
         w.capturas_ate_as_of, w.conflito_de_fonte, w.usos_de_outra_captura,
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
    -- Pelo registro CORRENTE em as_of, nunca pelo log. Ler o log aqui fazia o
    -- mesmo produto aparecer uma vez por captura. CAPTURE != REGISTRATION.
    from public.f_product_registered_windows(p_pais, p_as_of) w
   where w.crop = p_crop
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
        'registration_expiry_state', caducidade,
        'captures_up_to_as_of', capturas_ate_as_of,
        'source_conflict', conflito_de_fonte,
        'uses_from_a_different_capture', usos_de_outra_captura)
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
  'Carga compacta do caso, pelo registro CORRENTE em as_of. Devolve os quatro relógios '
  'separados e conta os desconhecidos. Nunca devolve necessidade de aplicação nem '
  'disponibilidade comercial: as duas são NOT_KNOWN por contrato, não por falta de dado.';
