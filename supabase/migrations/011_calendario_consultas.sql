-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 011
-- CAMADA DE CONSULTA DO CALENDÁRIO.
--
-- Regra que governa este arquivo: o DADO é persistido; o ESTADO é derivado
-- na pergunta. "Hoje" nunca vira coluna — entra como AS_OF_DATE, e o freeze
-- pode passar uma data congelada e obter a mesma resposta de sempre.
--
-- E uma segunda regra, que é a que mais protege: uma janela em BBCH não
-- pode ser comparada com uma data. Se não houver fenologia observada para
-- o mesmo país, cultura e geografia, o estado é NOT_KNOWN — não CLOSED.
--
-- NÃO EXECUTADA em Supabase. Executada e conferida num PostgreSQL 16
-- local e descartável: 001–012 montadas do zero, fixture ES carregada e
-- supabase/tests/regressoes_calendario.sql verde (45/45). Aplicar em
-- produção continua sendo trabalho do workflow supabase-migrate.
-- ═══════════════════════════════════════════════════════════════════════

-- ── Estado de uma janela por DATA ─────────────────────────────────────
-- Sem CLOSING: "faltam N dias" exige um N acordado, e ele não existe.
-- Inventar 7, 15 ou 30 seria fabricar régua.
create or replace function public.estado_janela_por_data(
  p_resolucao   resolucao_temporal,
  p_data_inicio date,
  p_data_fim    date,
  p_mes_inicio  smallint,
  p_mes_fim     smallint,
  p_as_of       date
) returns text language sql immutable as $$
  select case
    when p_resolucao in ('DATE_EXACT','WEEK') and p_data_inicio is not null then
      case when p_as_of < p_data_inicio then 'UPCOMING'
           when p_as_of > p_data_fim    then 'CLOSED'
           else 'ACTIVE' end
    when p_resolucao = 'MONTH' and p_mes_inicio is not null then
      case
        -- janela que cruza o ano (out→fev) é contínua, não vazia
        when p_mes_inicio <= p_mes_fim then
          case when extract(month from p_as_of) between p_mes_inicio and p_mes_fim
               then 'ACTIVE' else 'OUTSIDE_MONTH_RANGE' end
        else
          case when extract(month from p_as_of) >= p_mes_inicio
                 or extract(month from p_as_of) <= p_mes_fim
               then 'ACTIVE' else 'OUTSIDE_MONTH_RANGE' end
      end
    -- BBCH, estação e aproximado NÃO viram data. Quem pergunta por data
    -- sobre eles recebe NOT_KNOWN, e é a resposta certa.
    else 'NOT_KNOWN'
  end;
$$;

comment on function public.estado_janela_por_data is
  'ACTIVE / UPCOMING / CLOSED / OUTSIDE_MONTH_RANGE / NOT_KNOWN. Não existe CLOSING: '
  'ele exigiria um limiar de dias que ninguém acordou. UNKNOWN nunca é CLOSED.';

-- ── Estado de uma janela por FENOLOGIA ────────────────────────────────
create or replace function public.estado_janela_por_bbch(
  p_bbch_inicio smallint,
  p_bbch_fim    smallint,
  p_bbch_obs    smallint
) returns text language sql immutable as $$
  select case
    when p_bbch_inicio is null or p_bbch_obs is null then 'NOT_KNOWN'
    when p_bbch_obs <  p_bbch_inicio then 'UPCOMING'
    when p_bbch_obs >  p_bbch_fim    then 'CLOSED'
    else 'ACTIVE'
  end;
$$;

-- ── Frescor da evidência ──────────────────────────────────────────────
create or replace function public.estado_frescor(
  p_observado_em date,
  p_as_of        date,
  p_proposito    text,
  p_rule_version text
) returns text language sql stable as $$
  select coalesce(
    (select r.estado
       from public.freshness_regra r
      where r.proposito = p_proposito
        and r.rule_version = p_rule_version
        and p_observado_em is not null
        and r.idade_max_dias is not null
        and (p_as_of - p_observado_em) <= r.idade_max_dias
      order by r.idade_max_dias
      limit 1),
    -- Três ignorâncias diferentes, e nenhuma vira a outra:
    --   sem data         → AGE_NOT_KNOWN        (não sei quando foi observado)
    --   sem régua        → NO_RULE_FOR_PURPOSE  (ninguém decidiu o limiar deste propósito)
    --   com data e régua → STALE_FOR_PURPOSE    (medi a idade e ela passou de todos os limiares)
    case when p_observado_em is null then 'AGE_NOT_KNOWN'
         when not exists (select 1 from public.freshness_regra r
                           where r.proposito = p_proposito
                             and r.rule_version = p_rule_version)
              then 'NO_RULE_FOR_PURPOSE'
         else 'STALE_FOR_PURPOSE' end
  );
$$;

comment on function public.estado_frescor is
  'CURRENT / RECENT / SEASONAL / STALE_FOR_PURPOSE / NO_RULE_FOR_PURPOSE / AGE_NOT_KNOWN. '
  'Sem data é AGE_NOT_KNOWN; sem régua cadastrada é NO_RULE_FOR_PURPOSE — dizer '
  'STALE_FOR_PURPOSE aí seria afirmar que a evidência é velha sem ter limiar para '
  'medi-la. Não há limiar universal embutido em código.';


-- ═══════════════════════════════════════════════════════════════════════
-- VIEWS DE LISTAGEM — sem estado, porque estado depende de AS_OF_DATE
-- ═══════════════════════════════════════════════════════════════════════
create or replace view public.v_crop_calendar with (security_invoker = on) as
select cc.id, cc.pais, c.codigo as crop, cl.nome_local as crop_nome_local,
       g.regiao, g.provincia, g.codigo_nuts,
       cc.campanha, cc.tipo, cc.fase, cc.resolucao,
       cc.data_inicio, cc.data_fim, cc.mes_inicio, cc.mes_fim,
       cc.bbch_inicio, cc.bbch_fim, cc.texto_original,
       cc.recorrente, cc.qualificadores,
       cc.fonte, cc.fonte_versao, cc.fonte_url, cc.nivel_evidencia, cc.capturado_em
  from public.crop_calendar cc
  join public.crop c on c.id = cc.crop_id
  -- o nome local vem de crop_local e é filtrado pelo MESMO país da linha:
  -- 009 tirou nome_es de crop justamente para o nome não atravessar fronteira.
  left join public.crop_local cl on cl.crop_id = cc.crop_id and cl.pais = cc.pais
  left join public.geografia g on g.id = cc.geografia_id;

create or replace view public.v_crop_calendar_por_regiao with (security_invoker = on) as
select pais, crop, coalesce(provincia, regiao, 'PAÍS') as unidade_geografica,
       campanha, fase, resolucao, tipo,
       mes_inicio, mes_fim, data_inicio, data_fim, bbch_inicio, bbch_fim,
       texto_original, fonte
  from public.v_crop_calendar;

create or replace view public.v_issue_windows with (security_invoker = on) as
select iw.id, iw.pais, c.codigo as crop, i.codigo as issue, i.classe as issue_classe,
       il.nome_local as issue_nome_local,
       g.regiao, g.provincia, iw.campanha, iw.tipo, iw.resolucao,
       iw.data_inicio, iw.data_fim, iw.mes_inicio, iw.mes_fim,
       iw.bbch_inicio, iw.bbch_fim, iw.texto_original,
       iw.condicao_fenologica, iw.condicao_ambiental, iw.recorrente,
       iw.fonte, iw.nivel_evidencia, iw.capturado_em
  from public.issue_window iw
  join public.crop_issue ci on ci.id = iw.crop_issue_id
  join public.crop  c on c.id = ci.crop_id
  join public.issue i on i.id = ci.issue_id
  left join public.issue_local il on il.issue_id = i.id and il.pais = iw.pais
  left join public.geografia g on g.id = iw.geografia_id;

create or replace view public.v_product_registered_windows with (security_invoker = on) as
select ruj.id, rr.pais, rr.registration_id, rr.nome_comercial, rr.titular,
       rr.estado as estado_registro, rr.fecha_caducidad,
       c.codigo as crop, i.codigo as issue, i.classe as issue_classe,
       ru.substancia,
       ruj.resolucao, ruj.bbch_inicio, ruj.bbch_fim,
       ruj.aplicacoes_min, ruj.aplicacoes_max,
       ruj.intervalo_min_dias, ruj.intervalo_max_dias, ruj.prazo_seguranca_dias,
       ruj.dose_min, ruj.dose_max, ruj.dose_unidade,
       ruj.timing_texto_original, ruj.timing_normalizado,
       ruj.nivel_evidencia, ruj.fonte, ruj.fonte_versao, ruj.capturado_em,
       (i.codigo is not null) as alvo_explicito
  from public.registro_uso_janela ruj
  join public.registro_uso ru        on ru.id = ruj.registro_uso_id
  join public.registro_regulatorio rr on rr.id = ru.registro_id
  left join public.crop  c on c.id = ru.crop_id
  left join public.issue i on i.id = ru.issue_id;

comment on view public.v_product_registered_windows is
  'Janela AUTORIZADA no rótulo. Não diz que há necessidade de aplicar e não diz que '
  'o produto está disponível para compra.';


-- ═══════════════════════════════════════════════════════════════════════
-- FUNÇÕES COM AS_OF_DATE — o "hoje" entra aqui, nunca no dado
-- ═══════════════════════════════════════════════════════════════════════

-- Fenologia observada mais recente, do próprio acervo de observação.
-- É ela que permite avaliar uma janela em BBCH.
create or replace function public.f_bbch_observado(
  p_pais pais, p_crop text, p_geografia_id bigint, p_as_of date
) returns table (bbch smallint, observado_em date, fonte text)
language sql stable as $$
  select cc.bbch_inicio, cc.data_fim, cc.fonte
    from public.crop_calendar cc
    join public.crop c on c.id = cc.crop_id
   where cc.pais = p_pais
     and c.codigo = p_crop
     and cc.tipo = 'OBSERVED_CAMPAIGN'
     and cc.bbch_inicio is not null
     and (p_geografia_id is null or cc.geografia_id is not distinct from p_geografia_id)
     and cc.data_fim <= p_as_of
   order by cc.data_fim desc
   limit 1;
$$;

create or replace function public.f_crop_calendar(
  p_pais pais, p_crop text default null, p_geografia_id bigint default null,
  p_as_of date default current_date
) returns table (
  id bigint, crop text, unidade_geografica text, campanha text,
  tipo tipo_calendario, fase fase_cultura, resolucao resolucao_temporal,
  estado text, texto_original text, fonte text, nivel_evidencia nivel_evidencia
) language sql stable as $$
  select cc.id, c.codigo,
         coalesce(g.provincia, g.regiao, 'PAÍS'),
         cc.campanha, cc.tipo, cc.fase, cc.resolucao,
         public.estado_janela_por_data(cc.resolucao, cc.data_inicio, cc.data_fim,
                                       cc.mes_inicio, cc.mes_fim, p_as_of),
         cc.texto_original, cc.fonte, cc.nivel_evidencia
    from public.crop_calendar cc
    join public.crop c on c.id = cc.crop_id
    left join public.geografia g on g.id = cc.geografia_id
   where cc.pais = p_pais
     and (p_crop is null or c.codigo = p_crop)
     and (p_geografia_id is null or cc.geografia_id is not distinct from p_geografia_id);
$$;

-- Próxima janela relevante. SÓ para o que a fonte declara recorrente.
-- Um calendário típico pode voltar; uma campanha observada, não.
create or replace function public.f_next_relevant_window(
  p_pais pais, p_crop text, p_as_of date default current_date
) returns table (
  origem text, referencia bigint, fase_ou_tipo text, resolucao resolucao_temporal,
  quando text, recorrente boolean, fonte text
) language sql stable as $$
  select 'CROP_CALENDAR', cc.id, cc.fase::text, cc.resolucao,
         coalesce(cc.texto_original,
                  case when cc.mes_inicio is not null
                       then 'meses ' || cc.mes_inicio || '–' || cc.mes_fim end,
                  'NOT_KNOWN'),
         cc.recorrente, cc.fonte
    from public.crop_calendar cc
    join public.crop c on c.id = cc.crop_id
   where cc.pais = p_pais and c.codigo = p_crop and cc.recorrente
  union all
  select 'ISSUE_WINDOW', iw.id, iw.tipo::text, iw.resolucao,
         coalesce(iw.texto_original,
                  case when iw.mes_inicio is not null
                       then 'meses ' || iw.mes_inicio || '–' || iw.mes_fim end,
                  'NOT_KNOWN'),
         iw.recorrente, iw.fonte
    from public.issue_window iw
    join public.crop_issue ci on ci.id = iw.crop_issue_id
    join public.crop c on c.id = ci.crop_id
   where iw.pais = p_pais and c.codigo = p_crop and iw.recorrente;
$$;

comment on function public.f_next_relevant_window is
  'Devolve apenas linhas com recorrente = true. Projetar uma campanha observada '
  'para o ano seguinte seria inventar recorrência que a fonte não declarou.';

-- Última observação de campo do par, com frescor.
create or replace function public.f_latest_observations(
  p_pais pais, p_crop text, p_issue text default null,
  p_as_of date default current_date, p_proposito text default 'FIELD_DECISION',
  p_rule_version text default 'v1'
) returns table (
  crop text, issue text, unidade_geografica text,
  observado_ate date, idade_dias integer, valor numeric, unidade text,
  base_denominador numeric, base_descricao text, frescor text
) language sql stable as $$
  select c.codigo, i.codigo, coalesce(g.provincia, g.regiao, 'PAÍS'),
         o.periodo_fim, (p_as_of - o.periodo_fim)::integer,
         o.valor, o.unidade, o.base_denominador, o.base_descricao,
         public.estado_frescor(o.periodo_fim, p_as_of, p_proposito, p_rule_version)
    from public.observacao o
    join public.crop_issue ci on ci.id = o.crop_issue_id
    join public.crop  c on c.id = ci.crop_id
    join public.issue i on i.id = ci.issue_id
    left join public.geografia g on g.id = o.geografia_id
   where o.camada = 'FIELD'
     and c.codigo = p_crop
     and (p_issue is null or i.codigo = p_issue)
     and (g.pais = p_pais or g.pais is null)
   order by o.periodo_fim desc;
$$;
