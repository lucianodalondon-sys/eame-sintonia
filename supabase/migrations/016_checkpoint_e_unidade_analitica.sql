-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 016
-- SEM CHECKPOINT, NÃO GASTA · E UM AGREGADOR NÃO É UMA PESSOA
--
-- Fecha os dois contratos que o portão de entrada ainda deixava abertos:
-- RESILIENCE e ANALYTICAL_UNIT.
--
-- A rotação de chave e a classificação de falha JÁ EXISTEM e vêm do piloto
-- italiano (scripts/apify_pool.py), portadas sem alteração. O que faltava
-- não era a rotação: era a DURABILIDADE. O pool italiano guarda progresso
-- em memória, e um processo que morre no meio perde tudo o que já foi pago.
--
--     PROCESS_CRASH != LOST_COLLECTION
--
-- NÃO EXECUTADA em Supabase. Executada e conferida num PostgreSQL 16 local
-- e descartável, com as regressões verdes.
-- ═══════════════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════════════
-- 1 · CHECKPOINT — o objeto que precisa existir ANTES de gastar
--
-- Não é o mesmo grão que collection_run. Uma rodada é UMA execução do
-- ator; o checkpoint é a UNIDADE DE TRABALHO, e ela pode atravessar várias
-- execuções quando a chave roda. Por isso collection_run aponta para cá, e
-- não o contrário.
-- ═══════════════════════════════════════════════════════════════════════
create table public.checkpoint_coleta (
  id                bigserial primary key,
  collection_target text not null,           -- o que se quer coletar
  input_hash        char(64) not null,       -- sha256 da entrada REAL
  actor             text not null,
  platform          text not null,
  pais              pais not null default 'NAO_SEI',
  started_at        timestamptz not null,
  updated_at        timestamptz not null,
  finished_at       timestamptz,
  estado            text not null check (estado in
                    ('ABERTO','EM_CURSO','CONCLUIDO','PARCIAL','FALHOU','ABANDONADO')),
  pool_position     smallint check (pool_position >= 1),
  run_id            text references public.collection_run(run_id) on delete set null,
  dataset_id        text,
  -- LAST_PERSISTED_PROGRESS: o que JÁ foi persistido, não o que foi lido.
  -- A diferença é a coleta inteira: contar o que voltou faz a retomada
  -- pular item que ninguém salvou.
  unidades_totais   integer not null default 0,
  unidades_feitas   integer not null default 0,
  itens_persistidos integer not null default 0,
  ultima_unidade    text,
  motivo            text,
  rule_version      text not null,
  UNIQUE (collection_target, input_hash)
);

comment on table public.checkpoint_coleta is
  'A trava do SEM_CHECKPOINT_NAO_GASTEI. Nenhuma chamada paga pode começar sem uma '
  'linha aqui. Grão diferente de collection_run: um checkpoint atravessa várias '
  'execuções quando a chave roda.';
comment on column public.checkpoint_coleta.itens_persistidos is
  'O que já foi SALVO, nunca o que voltou do ator. Contar o que voltou faria a '
  'retomada pular item que ninguém guardou.';

alter table public.checkpoint_coleta enable row level security;
create index on public.checkpoint_coleta (estado, pais);

-- Uma rodada paga tem de saber de qual checkpoint ela nasceu.
alter table public.collection_run
  add column if not exists checkpoint_id bigint
    references public.checkpoint_coleta(id) on delete set null;

comment on column public.collection_run.checkpoint_id is
  'De qual unidade de trabalho esta execução nasceu. NULL só é aceitável para rodadas '
  'anteriores à 016 — a guarda do chamador exige checkpoint desde então.';


-- ── A PERGUNTA QUE O CHAMADOR TEM DE FAZER ANTES DE GASTAR ────────────
create or replace function public.pode_gastar(p_target text, p_input_hash text)
returns table (pode boolean, porque text, checkpoint_id bigint, retomar_de text)
language sql stable as $$
  select
    c.id is not null and c.estado in ('ABERTO','EM_CURSO','PARCIAL'),
    case
      when c.id is null then 'SEM_CHECKPOINT_NAO_GASTEI'
      when c.estado in ('CONCLUIDO') then 'JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES'
      when c.estado in ('FALHOU','ABANDONADO') then 'CHECKPOINT_ENCERRADO_ABRIR_OUTRO'
      else 'CHECKPOINT_ABERTO'
    end,
    c.id,
    c.ultima_unidade
  from (select 1) z
  left join public.checkpoint_coleta c
    on c.collection_target = p_target and c.input_hash = p_input_hash;
$$;

comment on function public.pode_gastar is
  'SEM_CHECKPOINT_NAO_GASTEI e JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES na mesma resposta. '
  'Os dois são recusas, e a segunda é a lei brasileira de não pagar duas vezes.';


-- ═══════════════════════════════════════════════════════════════════════
-- 2 · UNIDADE ANALÍTICA — um agregador não é uma pessoa
--
-- O Brasil mediu 4.548 fichas tratadas como fonte individual e conseguiu
-- PROVAR que 4 delas eram unidade analítica válida. O resto ficou NÃO SEI.
-- Aqui a classificação não é heurística nem volume: é um campo declarado,
-- com evidência, e NOT_KNOWN é o padrão.
-- ═══════════════════════════════════════════════════════════════════════
alter table public.canal
  add column if not exists tipo_de_perfil text not null default 'NOT_KNOWN'
    check (tipo_de_perfil in ('PERSON_PROFILE','ORGANIZATION_PROFILE',
                              'AGGREGATOR','SEARCH_RESULT_ENVELOPE',
                              'OTHER','NOT_KNOWN')),
  add column if not exists tipo_de_perfil_evidencia text;

-- Dizer que é pessoa exige evidência escrita. NOT_KNOWN não exige nada —
-- e é por isso que ele é o padrão.
alter table public.canal
  add constraint tipo_de_perfil_declarado_exige_evidencia
  check (tipo_de_perfil = 'NOT_KNOWN' or tipo_de_perfil_evidencia is not null);

comment on column public.canal.tipo_de_perfil is
  'PERSON_PROFILE / ORGANIZATION_PROFILE / AGGREGATOR / SEARCH_RESULT_ENVELOPE / OTHER / '
  'NOT_KNOWN. Nunca classificado por volume nem por heurística fraca. Sem evidência '
  'suficiente, NOT_KNOWN — que é diferente de "não é pessoa".';


-- ── QUEM A CAMADA HUMANA PODE CONSUMIR COMO PESSOA ────────────────────
-- Duas condições, e as duas juntas: o perfil tem de ser declarado
-- PERSON_PROFILE COM evidência, e a origem tem de apontar uma pessoa.
-- Uma só não basta: a ficha de origem é decisão de quem cadastra, e o
-- tipo de perfil é leitura da página.
create or replace view public.v_human_sensor_admissivel with (security_invoker = on) as
select c.id as canal_id, c.plataforma, c.channel_id, c.handle,
       c.tipo_de_perfil, c.tipo_de_perfil_evidencia,
       o.pessoa_id, o.organizacao_id,
       (c.tipo_de_perfil = 'PERSON_PROFILE' and o.pessoa_id is not null) as admissivel,
       case
         when c.tipo_de_perfil = 'NOT_KNOWN' then 'TIPO_DE_PERFIL_NAO_MEDIDO'
         when c.tipo_de_perfil = 'AGGREGATOR' then 'AGGREGATOR_NAO_E_HUMAN_SENSOR'
         when c.tipo_de_perfil = 'SEARCH_RESULT_ENVELOPE' then 'SEARCH_HIT_NAO_E_PESSOA'
         when c.tipo_de_perfil = 'ORGANIZATION_PROFILE' then 'ORGANIZACAO_NAO_E_VOZ_HUMANA'
         when c.tipo_de_perfil = 'OTHER' then 'TIPO_DECLARADO_FORA_DO_VOCABULARIO_HUMANO'
         when o.pessoa_id is null then 'PERFIL_DE_PESSOA_SEM_FICHA_DE_PESSOA'
         else 'ADMISSIVEL'
       end as porque
  from public.canal c
  join public.origem o on o.id = c.origem_id;

comment on view public.v_human_sensor_admissivel is
  'SOURCE/COLLECTOR/AGGREGATOR != HUMAN SENSOR PERSON. A camada humana só consome '
  'linhas com admissivel = true, e toda recusa vem com o motivo escrito.';


-- ═══════════════════════════════════════════════════════════════════════
-- 3 · DEDUPE NO CAMINHO PRODUTIVO
--
-- A identidade do conteúdo é (plataforma, content_id), e ela JÁ ESTAVA
-- travada: `conteudo_canal_id_content_id_key`, UNIQUE (canal_id, content_id),
-- existe desde a 003.
--
-- A primeira versão desta migration criou um índice único novo com o mesmo
-- par de colunas. Seria um SEGUNDO DONO da mesma lei, e o banco recusou a
-- duplicata na primeira execução do teste. O erro estava no diagnóstico da
-- rodada anterior, não no schema: o BR-14 nunca foi "falta a trava de
-- identidade". Era "o caminho produtivo nunca foi provado passando por ela".
--
-- Por isso aqui não nasce índice nenhum. O que nasce é o lugar de guardar a
-- SEGUNDA vez que vimos o mesmo conteúdo — que é a informação que se perdia
-- quando a retomada por outra chave reencontrava o mesmo item.

comment on constraint conteudo_canal_id_content_id_key on public.conteudo is
  'PLATFORM + EXTERNAL_ID, via canal. TOKEN, RUN_ID, DATASET_ID e CAPTURED_AT nunca '
  'entram na identidade — se entrassem, a retomada por outra chave duplicaria tudo. '
  'Existe desde a 003; a 016 apenas provou o caminho produtivo passando por ela.';

-- Uma observação por rodada continua podendo existir: a proveniência da
-- SEGUNDA vez que vimos o mesmo conteúdo é informação, e ela mora aqui, sem
-- duplicar o conteúdo.
create table if not exists public.conteudo_visto_em (
  id            bigserial primary key,
  conteudo_id   bigint not null references public.conteudo(id) on delete cascade,
  run_id        text not null references public.collection_run(run_id) on delete restrict,
  visto_em      timestamptz not null,
  pool_position smallint,
  UNIQUE (conteudo_id, run_id)
);

comment on table public.conteudo_visto_em is
  'O mesmo conteúdo visto em duas rodadas são DUAS observações e UM conteúdo. Guardar '
  'a segunda aqui preserva a proveniência sem duplicar a entidade.';

alter table public.conteudo_visto_em enable row level security;
