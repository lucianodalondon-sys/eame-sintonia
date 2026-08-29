-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 001
-- FUNDAÇÃO: geografia, execução de coleta e evidência bruta.
--
-- Por que esta vem primeiro: no Brasil, `coletas` e `documentos` nasceram
-- juntas e a proveniência ficou boa. O que faltou lá foi um lugar para o
-- BRUTO PESADO — ele ficou em arquivo e em Git. Aqui o bruto tem tabela
-- desde o começo, apontando para o Storage.
--
-- NÃO EXECUTADA. Proposta da MISSÃO 11A-BRIDGE-ES.
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- O EAME é UM projeto, não um por país. Toda linha de fato carrega
-- geografia suficiente para separar de onde veio de sobre onde fala.
-- Esta é a lei SOURCE_LOCATION != FACT_LOCATION virando coluna.
-- O Brasil tinha UM campo (`praca`) para as duas coisas — e por isso a
-- pergunta "o conteúdo é de Córdoba ou fala de Córdoba?" não tinha como
-- ser feita no banco. É o confundidor de Córdoba, no nível do schema.
-- ─────────────────────────────────────────────────────────────────────
create type pais as enum ('ES','FR','IT','PT','EU','BR','OTHER','NAO_SEI');

create table public.geografia (
  id           bigserial primary key,
  pais         pais   not null,
  regiao       text,                      -- Andalucía, Occitanie...
  provincia    text,                      -- Córdoba, Jaén...
  codigo_nuts  text,                      -- ES61, ES613... quando existir
  -- nulls not distinct: regiao e provincia são nuláveis, e uma linha de país
  -- inteiro (ambas NULL) entraria N vezes sem que a trava reclamasse.
  UNIQUE NULLS NOT DISTINCT (pais, regiao, provincia)
);
comment on table public.geografia is
  'Lugar declarado. NUNCA inferido: geografia ausente fica NULL, jamais chutada.';

-- ─────────────────────────────────────────────────────────────────────
-- EXECUÇÃO DE COLETA — o RUN_MANIFEST.json do EAME dentro do Postgres.
-- Campo a campo igual ao contrato que scripts/proveniencia.py já trava,
-- para que a migração seja transporte e não redesenho.
-- `status` separa 'vazia' de 'concluida' pela mesma razão do Brasil e do
-- coletor espanhol: SUCCEEDED com zero itens é degradação, não sucesso.
-- ─────────────────────────────────────────────────────────────────────
create type run_status as enum ('rodando','concluida','vazia','parcial','falhou');

create table public.collection_run (
  id                     bigserial primary key,
  run_id                 text not null unique,      -- ES-T8-001-2026-08-29-a
  platform               text not null,
  actor                  text,                      -- apidojo/youtube-scraper
  actor_version          text,
  input                  jsonb,                     -- a entrada real, não a pretendida
  query                  text,
  mission                text,
  source_country         pais not null default 'NAO_SEI',
  started_at             timestamptz not null,
  finished_at            timestamptz,
  dataset_id             text,
  item_count_raw         integer,
  item_count_normalized  integer,
  cost_usd               numeric(12,6),
  -- COMO o custo foi obtido faz parte do custo. No Brasil TRES metodos diferentes
  -- escreviam na mesma coluna `custo_usd` sem registrar qual — e o proprio leitor do
  -- acervo chamou isso de "o defeito de schema mais importante" da proveniencia.
  -- Custo lido da plataforma e custo estimado por diferenca de saldo nao sao o mesmo
  -- numero, e somar os dois produz um total que nao existe.
  cost_method            text check (cost_method in
                         ('PLATAFORMA_USAGE_TOTAL',   -- usageTotalUsd da propria execucao
                          'DIFERENCA_DE_SALDO',       -- saldo antes menos saldo depois
                          'TABELA_DE_PRECO',          -- eventos x preco publicado
                          'NAO_SEI')),
  CONSTRAINT custo_declarado_diz_como_foi_medido
    CHECK (cost_usd IS NULL OR cost_method IS NOT NULL),
  source_version         text,
  status                 run_status not null default 'rodando',
  error                  text,
  capture_method         text,
  rule_version           text not null,             -- a versão da regra que normalizou
  created_at             timestamptz not null default now()
);
create index run_status_idx  on public.collection_run (status, started_at desc);
create index run_actor_idx   on public.collection_run (actor, started_at desc);
comment on column public.collection_run.item_count_normalized is
  'NULL = ainda não normalizado. 0 = normalizou e deu zero. Não são a mesma coisa.';
comment on column public.collection_run.cost_usd is
  'NULL != 0. NULL é "não medido"; 0 é "medido e deu zero". O Brasil enforça essa '
  'distinção em código; aqui ela é o par (cost_usd, cost_method).';
comment on table public.collection_run is
  'UMA linha = UMA execução de ator. Nunca duas semânticas na mesma tabela: no Brasil '
  '`coletas` mistura RODADA (fonte_id nulo) com VISITA A UMA FONTE (fonte_id preenchido), '
  'e os dois denominadores nunca podem ser somados. '
  'PROVENIÊNCIA É PROSPECTIVA: não se preenche elo de execução passada. Inventar o elo '
  'depois seria fabricar proveniência. '
  'PRECEDÊNCIA DE STATUS: falhou > vazia > parcial > concluida — regra, não estilo.';

-- ─────────────────────────────────────────────────────────────────────
-- EVIDÊNCIA BRUTA — o que o Brasil não teve e pagou caro: JSONs de 6,6 MB
-- versionados em Git (coletas-do-navegador/). Aqui o bruto vive no
-- Storage e o Postgres guarda só o ponteiro, o hash e a proveniência.
--
-- `sha256` é o que permite dizer "este bruto é o mesmo" sem abrir o arquivo,
-- e é o que sobrevive a qualquer mudança futura de normalização.
-- ─────────────────────────────────────────────────────────────────────
create table public.raw_asset (
  id             bigserial primary key,
  run_id         text not null references public.collection_run(run_id) on delete restrict,
  storage_path   text not null unique,     -- bucket/caminho no Supabase Storage
  media_type     text not null,            -- application/json+gzip, application/pdf...
  bytes          bigint not null,
  sha256         char(64) not null,
  captured_at    timestamptz not null,
  source_url     text,
  preserved      boolean not null default true,
  not_preserved_reason text,
  created_at     timestamptz not null default now(),
  CONSTRAINT bruto_ausente_precisa_de_motivo
    CHECK (preserved OR not_preserved_reason IS NOT NULL)
);
create index raw_run_idx  on public.raw_asset (run_id);
create index raw_hash_idx on public.raw_asset (sha256);
comment on constraint bruto_ausente_precisa_de_motivo on public.raw_asset is
  'NOT_PRESERVED é um estado declarado, nunca um silêncio. Mesma lei de proveniencia.py.';
