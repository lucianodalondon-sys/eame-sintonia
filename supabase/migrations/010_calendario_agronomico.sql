-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 010
-- QUATRO RELÓGIOS. NENHUM EMPRESTA A SEMÂNTICA DO OUTRO.
--
--   CROP_STAGE  !=  ISSUE_RELEVANCE  !=  REGISTERED_WINDOW  !=  EVIDENCE_AGE
--
-- O calendário não é decoração: é camada de inteligência temporal. E ele
-- não pode inventar o tempo que a fonte não mediu — por isso a resolução
-- temporal é coluna, com trava, e não uma conveniência de interface.
--
-- DONOS QUE JÁ EXISTEM E NÃO SÃO DUPLICADOS AQUI:
--   crop, issue, crop_issue, geografia   → 001 e 004
--   registro_regulatorio, registro_uso   → 006
--   observacao (camada FIELD)            → 005
--   raw_asset, collection_run            → 001
--
-- O QUE NASCE AQUI:
--   crop_calendar          — relógio A, sem dono anterior
--   issue_window           — relógio B, sem dono anterior
--   registro_uso_janela    — relógio C, FILHO de registro_uso (não segundo dono)
--   relógio D              — NÃO tem tabela. É função sobre observacao.
--
-- NÃO EXECUTADA em Supabase. Executada e conferida num PostgreSQL 16
-- local e descartável: 001–012 montadas do zero, fixture ES carregada e
-- supabase/tests/regressoes_calendario.sql verde (45/45). Aplicar em
-- produção continua sendo trabalho do workflow supabase-migrate.
-- ═══════════════════════════════════════════════════════════════════════

-- ── RESOLUÇÃO TEMPORAL ────────────────────────────────────────────────
-- Se a fonte só sustenta "primavera", guardamos SEASON. Converter para
-- 2027-03-21 seria inventar precisão que ninguém mediu.
create type resolucao_temporal as enum (
  'DATE_EXACT', 'WEEK', 'MONTH', 'PHENOLOGY_STAGE', 'SEASON', 'APPROXIMATE', 'NOT_KNOWN'
);

-- ── TIPO DE CALENDÁRIO ────────────────────────────────────────────────
-- Não chamar tudo de calendário. Um calendário típico pode se repetir;
-- uma campanha observada NÃO pode ser projetada para o ano seguinte.
create type tipo_calendario as enum (
  'TYPICAL_CALENDAR',
  'OFFICIAL_RECOMMENDED_CALENDAR',
  'OBSERVED_CAMPAIGN',
  'DERIVED_FROM_MULTIYEAR_DATA'
);

-- ── FASE DA CULTURA ───────────────────────────────────────────────────
-- Vocabulário controlado. Nem toda cultura usa todas as fases, e o schema
-- não obriga nenhuma a usar.
create type fase_cultura as enum (
  'PREPARATION', 'SOWING', 'EMERGENCE', 'VEGETATIVE_DEVELOPMENT',
  'REPRODUCTIVE_DEVELOPMENT', 'MATURATION', 'HARVEST', 'DORMANCY',
  'OFF_SEASON', 'OTHER'
);

-- ── TIPO DE JANELA DO ISSUE ───────────────────────────────────────────
-- EXPECTED_RELEVANCE != CURRENT_FIELD_PRESSURE. A pressão atual mora em
-- observacao e não entra aqui — nem como coluna.
create type tipo_janela_issue as enum (
  'EXPECTED_RELEVANCE', 'OBSERVED_ACTIVITY', 'MONITORING_WINDOW',
  'RISK_WINDOW', 'CONTROL_DECISION_WINDOW', 'OTHER'
);

create type nivel_evidencia as enum (
  'REGULATORY_FACT', 'OFFICIAL_SOURCE', 'MEASURED_SERIES',
  'SCIENTIFIC_DOCUMENT', 'MANUFACTURER_STATEMENT', 'DERIVED'
);


-- ═══════════════════════════════════════════════════════════════════════
-- A · CROP CALENDAR — onde a cultura está
-- ═══════════════════════════════════════════════════════════════════════
create table public.crop_calendar (
  id                bigserial primary key,
  pais              pais not null,
  crop_id           bigint not null references public.crop(id) on delete restrict,
  geografia_id      bigint references public.geografia(id) on delete restrict,
  campanha          text,                    -- '2026', '2026/27'. NULL = calendário sem ano.
  tipo              tipo_calendario not null,
  fase              fase_cultura not null,
  resolucao         resolucao_temporal not null,

  -- só um par preenchido, conforme a resolução. A trava está abaixo.
  data_inicio       date,
  data_fim          date,
  mes_inicio        smallint check (mes_inicio between 1 and 12),
  mes_fim           smallint check (mes_fim between 1 and 12),
  bbch_inicio       smallint check (bbch_inicio between 0 and 99),
  bbch_fim          smallint check (bbch_fim between 0 and 99),
  texto_original    text,                    -- o que a fonte disse, literal

  recorrente        boolean not null default false,
  qualificadores    jsonb not null default '{}'::jsonb,  -- irrigado/sequeiro, variedade...

  fonte             text not null,
  fonte_versao      text,
  fonte_url         text,
  nivel_evidencia   nivel_evidencia not null,
  raw_asset_id      bigint references public.raw_asset(id) on delete set null,
  capturado_em      timestamptz not null,
  valido_de         date,
  valido_ate        date,
  rule_version      text not null,

  -- A trava da precisão: a resolução declarada tem de bater com o que
  -- foi preenchido. Sem isso, MONTH vira data exata na primeira consulta.
  CONSTRAINT calendario_resolucao_bate_com_o_preenchido CHECK (
    (resolucao = 'DATE_EXACT'      and data_inicio is not null and data_fim is not null)
 or (resolucao = 'WEEK'            and data_inicio is not null and data_fim is not null)
 or (resolucao = 'MONTH'           and mes_inicio  is not null and mes_fim  is not null
                                   and data_inicio is null     and data_fim is null)
 or (resolucao = 'PHENOLOGY_STAGE' and bbch_inicio is not null and bbch_fim is not null)
 or (resolucao in ('SEASON','APPROXIMATE') and texto_original is not null)
 or (resolucao = 'NOT_KNOWN'       and data_inicio is null and mes_inicio is null
                                   and bbch_inicio is null)
  ),
  -- Campanha observada não se repete. Projetar 2026 em 2027 seria inventar.
  CONSTRAINT campanha_observada_nao_recorre CHECK (
    tipo <> 'OBSERVED_CAMPAIGN' or recorrente = false
  ),
  -- Campanha observada precisa dizer qual campanha foi.
  CONSTRAINT campanha_observada_declara_o_ano CHECK (
    tipo <> 'OBSERVED_CAMPAIGN' or campanha is not null
  ),
  UNIQUE NULLS NOT DISTINCT (pais, crop_id, geografia_id, campanha, tipo, fase, fonte)
);

-- A geografia da linha tem de ser do país da linha. SOURCE_LOCATION continua
-- podendo ser outro; FACT_LOCATION não.
create or replace function public.geografia_do_pais(g bigint, p pais)
returns boolean language sql stable as $$
  select g is null or exists (select 1 from public.geografia x where x.id = g and x.pais = p);
$$;
alter table public.crop_calendar
  add constraint calendario_geografia_e_do_pais
  check (public.geografia_do_pais(geografia_id, pais)) not valid;


-- ═══════════════════════════════════════════════════════════════════════
-- B · ISSUE WINDOW — quando o problema importa
-- Não guarda pressão atual. Pressão atual é observacao.
-- ═══════════════════════════════════════════════════════════════════════
create table public.issue_window (
  id                bigserial primary key,
  pais              pais not null,
  crop_issue_id     bigint not null references public.crop_issue(id) on delete restrict,
  geografia_id      bigint references public.geografia(id) on delete restrict,
  campanha          text,
  tipo              tipo_janela_issue not null,
  resolucao         resolucao_temporal not null,

  data_inicio       date,
  data_fim          date,
  mes_inicio        smallint check (mes_inicio between 1 and 12),
  mes_fim           smallint check (mes_fim between 1 and 12),
  bbch_inicio       smallint check (bbch_inicio between 0 and 99),
  bbch_fim          smallint check (bbch_fim between 0 and 99),
  texto_original    text,

  condicao_fenologica text,   -- "antes da floração", quando a fonte diz assim
  condicao_ambiental  text,   -- "queda térmica + umidade", quando a fonte diz
  recorrente        boolean not null default false,
  qualificadores    jsonb not null default '{}'::jsonb,

  fonte             text not null,
  fonte_versao      text,
  fonte_url         text,
  nivel_evidencia   nivel_evidencia not null,
  raw_asset_id      bigint references public.raw_asset(id) on delete set null,
  capturado_em      timestamptz not null,
  rule_version      text not null,

  CONSTRAINT janela_issue_resolucao_bate_com_o_preenchido CHECK (
    (resolucao = 'DATE_EXACT'      and data_inicio is not null and data_fim is not null)
 or (resolucao = 'WEEK'            and data_inicio is not null and data_fim is not null)
 or (resolucao = 'MONTH'           and mes_inicio  is not null and mes_fim  is not null
                                   and data_inicio is null     and data_fim is null)
 or (resolucao = 'PHENOLOGY_STAGE' and bbch_inicio is not null and bbch_fim is not null)
 or (resolucao in ('SEASON','APPROXIMATE') and texto_original is not null)
 or (resolucao = 'NOT_KNOWN'       and data_inicio is null and mes_inicio is null
                                   and bbch_inicio is null)
  ),
  -- OBSERVED_ACTIVITY é o único tipo que fala de um ano concreto, e por isso
  -- é o único que não pode ser projetado adiante.
  CONSTRAINT atividade_observada_nao_recorre CHECK (
    tipo <> 'OBSERVED_ACTIVITY' or recorrente = false
  ),
  UNIQUE NULLS NOT DISTINCT (pais, crop_issue_id, geografia_id, campanha, tipo, fonte)
);
alter table public.issue_window
  add constraint janela_issue_geografia_e_do_pais
  check (public.geografia_do_pais(geografia_id, pais)) not valid;


-- ═══════════════════════════════════════════════════════════════════════
-- C · PRODUCT REGISTERED WINDOW — até quando o produto PODE ser usado
-- Filho de registro_uso. registro_uso continua dono do uso; esta tabela
-- é dona apenas da condição temporal dele.
-- ═══════════════════════════════════════════════════════════════════════
create table public.registro_uso_janela (
  id                 bigserial primary key,
  registro_uso_id    bigint not null references public.registro_uso(id) on delete cascade,
  resolucao          resolucao_temporal not null,

  bbch_inicio        smallint check (bbch_inicio between 0 and 99),
  bbch_fim           smallint check (bbch_fim between 0 and 99),
  data_inicio        date,
  data_fim           date,
  mes_inicio         smallint check (mes_inicio between 1 and 12),
  mes_fim            smallint check (mes_fim between 1 and 12),

  aplicacoes_min     smallint check (aplicacoes_min >= 0),
  aplicacoes_max     smallint check (aplicacoes_max >= 0),
  intervalo_min_dias smallint check (intervalo_min_dias >= 0),
  intervalo_max_dias smallint check (intervalo_max_dias >= 0),
  prazo_seguranca_dias smallint check (prazo_seguranca_dias >= 0),
  dose_min           numeric,
  dose_max           numeric,
  dose_unidade       text,

  -- O texto literal da etiqueta é obrigatório. Toda normalização abaixo
  -- pode ser conferida contra ele.
  timing_texto_original text not null,
  timing_normalizado    text,

  fonte_documento_id bigint references public.conteudo(id) on delete set null,
  raw_asset_id       bigint references public.raw_asset(id) on delete set null,
  nivel_evidencia    nivel_evidencia not null,
  fonte              text not null,
  fonte_versao       text,
  capturado_em       timestamptz not null,
  rule_version       text not null,

  CONSTRAINT janela_produto_resolucao_bate_com_o_preenchido CHECK (
    (resolucao = 'PHENOLOGY_STAGE' and bbch_inicio is not null and bbch_fim is not null)
 or (resolucao = 'DATE_EXACT'      and data_inicio is not null and data_fim is not null)
 or (resolucao = 'MONTH'           and mes_inicio  is not null and mes_fim  is not null)
 or (resolucao in ('SEASON','APPROXIMATE'))
 or (resolucao = 'NOT_KNOWN'       and bbch_inicio is null and data_inicio is null
                                   and mes_inicio is null)
  ),
  CONSTRAINT bbch_em_ordem CHECK (bbch_inicio is null or bbch_fim is null or bbch_inicio <= bbch_fim),
  CONSTRAINT aplicacoes_em_ordem CHECK (
    aplicacoes_min is null or aplicacoes_max is null or aplicacoes_min <= aplicacoes_max
  ),
  UNIQUE NULLS NOT DISTINCT (registro_uso_id, resolucao, bbch_inicio, bbch_fim, timing_texto_original)
);

comment on table public.registro_uso_janela is
  'Janela REGISTRADA do produto. Autorização de rótulo, nunca necessidade de aplicar, '
  'nunca disponibilidade comercial.';


-- ═══════════════════════════════════════════════════════════════════════
-- D · EVIDENCE FRESHNESS — não tem tabela, e isso é decisão
-- A idade da evidência é derivada de observacao no momento da pergunta,
-- porque ela depende de AS_OF_DATE e de PROPÓSITO. Persistir "hoje" seria
-- gravar um fato que muda sozinho.
-- ═══════════════════════════════════════════════════════════════════════
create table public.freshness_regra (
  id            bigserial primary key,
  proposito     text not null,     -- FIELD_DECISION, SCIENCE_CONTEXT...
  estado        text not null check (estado in ('CURRENT','RECENT','SEASONAL','STALE_FOR_PURPOSE')),
  idade_max_dias integer,          -- NULL = sem limite superior neste estado
  rule_version  text not null,
  justificativa text not null,     -- por que este limite, e de onde ele veio
  UNIQUE (proposito, estado, rule_version)
);

comment on table public.freshness_regra is
  'Os limiares de frescor são DADO, não constante de código. Freshness depende do '
  'propósito: um paper de 2021 segue válido como ciência; uma leitura de campo de '
  '95 dias pode ser velha para decisão. Sem linha aqui, o estado é AGE_NOT_KNOWN.';


-- ── RLS, mesmo padrão de 006 ──────────────────────────────────────────
alter table public.crop_calendar        enable row level security;
alter table public.issue_window         enable row level security;
alter table public.registro_uso_janela  enable row level security;
alter table public.freshness_regra      enable row level security;

-- ── Índices das perguntas que o portal faz ────────────────────────────
create index on public.crop_calendar (pais, crop_id, geografia_id);
create index on public.issue_window  (pais, crop_issue_id, geografia_id);
create index on public.registro_uso_janela (registro_uso_id);
