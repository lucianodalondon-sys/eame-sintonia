-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 005
-- OBSERVADO != DERIVADO, e DETECÇÃO != PORTFÓLIO.
--
-- Duas leis brasileiras que não podem virar a mesma tabela:
--   · DETECÇÃO responde "o que o mundo externo está mostrando?"
--   · PORTFÓLIO responde "temos resposta registrada para este par?"
-- Nascer da mesma régua foi o defeito que o Brasil separou em
-- separar-portfolio.py. Aqui elas nem compartilham tabela.
--
-- E toda linha derivada carrega `rule_version`: derivado sem a versão da
-- regra que o produziu não é reproduzível, e o Brasil mediu que regra
-- copiada em dois lugares diverge.
--
-- NÃO EXECUTADA.
-- ═══════════════════════════════════════════════════════════════════════

-- OBSERVAÇÃO: um fato medido numa fonte externa, com denominador.
-- `base_*` são NOT NULL pela mesma razão do Brasil (termos_medicoes):
-- razão publicada sem denominador declarado é como o número mente.
create table public.observacao (
  id               bigserial primary key,
  crop_issue_id    bigint references public.crop_issue(id) on delete restrict,
  geografia_id     bigint references public.geografia(id),
  camada           text not null check (camada in
                   ('FIELD','SCIENCE','VOICE','MEDIA','COMPETITOR','REGULATORY')),
  periodo_inicio   date not null,
  periodo_fim      date not null,
  valor            numeric,
  unidade          text,
  base_denominador numeric not null,
  base_descricao   text not null,
  fonte_conteudo_id bigint references public.conteudo(id) on delete set null,
  run_id           text references public.collection_run(run_id) on delete set null,
  rule_version     text not null,
  medido_em        timestamptz not null default now(),
  -- nulls not distinct: crop_issue_id, geografia_id e unidade são nuláveis.
  UNIQUE NULLS NOT DISTINCT (crop_issue_id, geografia_id, camada, periodo_inicio, periodo_fim, unidade)
);
comment on column public.observacao.base_denominador is
  'Obrigatório. O Brasil já travava isso em termos_medicoes.base_comentarios/base_pessoas.';

-- DERIVAÇÃO: conclusão calculada A PARTIR de observações. Nunca se mistura
-- com observação, e aponta para as observações que a sustentam.
create table public.derivacao (
  id             bigserial primary key,
  pergunta       text not null,
  resposta       text not null,
  estado         text not null check (estado in
                 ('PROVED','PARTIAL','NOT_REACHED','CONFOUNDER_OPEN','REFUTED')),
  limitacao      text not null,             -- o que esta conclusão NÃO prova
  rule_version   text not null,
  derivado_em    timestamptz not null default now()
);
comment on column public.derivacao.limitacao is
  'NOT NULL de propósito: uma conclusão sem limite declarado é a que vira '
  'slide. CONFOUNDER_OPEN é estado de primeira classe — Córdoba vive aqui.';

create table public.derivacao_observacao (
  derivacao_id  bigint not null references public.derivacao(id)  on delete cascade,
  observacao_id bigint not null references public.observacao(id) on delete restrict,
  primary key (derivacao_id, observacao_id)
);

-- PORTFÓLIO — tabela separada, alimentada SÓ por registro oficial.
-- Nunca por menção, nunca por volume de conteúdo.
create table public.resposta_registrada (
  id                    bigserial primary key,
  crop_issue_id         bigint not null references public.crop_issue(id) on delete restrict,
  titular               text not null,
  registered_response_exists boolean not null,
  registro_count        integer not null,
  substancias           text[] not null default '{}',
  fonte                 text not null,       -- MAPA ROPF + timestamp do servidor
  fonte_versao          text not null,
  -- Deliberadamente sem default: disponibilidade comercial NÃO se deduz de registro.
  current_commercial_availability text not null default 'NAO_SEI'
    check (current_commercial_availability in ('SIM','NAO','NAO_SEI')),
  medido_em             timestamptz not null default now(),
  UNIQUE (crop_issue_id, titular, fonte_versao)
);
comment on column public.resposta_registrada.current_commercial_availability is
  'REGISTERED_RESPONSE_EXISTS != CURRENT_COMMERCIAL_AVAILABILITY. '
  'Default NAO_SEI porque o registro público não responde essa pergunta. '
  'Ver Neptune ES-00211.';

-- LACUNA é ferramenta separada de "temos para?". Zero ADAMA encontrado NÃO
-- é lacuna enquanto a chave não foi diagnosticada: o Brasil teve 0 -> N
-- correspondências só consertando a normalização do nome do produto.
create table public.lacuna_candidata (
  id                bigserial primary key,
  crop_issue_id     bigint not null references public.crop_issue(id) on delete restrict,
  zero_diagnosticado boolean not null default false,
  diagnostico_da_chave text,
  necessidade_evidenciada boolean not null default false,
  concorrente_presente boolean,
  cobertura_da_fonte text not null,
  estado            text not null default 'NAO_DIAGNOSTICADA' check (estado in
                    ('NAO_DIAGNOSTICADA','CHAVE_QUEBRADA','LACUNA_CANDIDATA','SEM_LACUNA')),
  rule_version      text not null,
  CONSTRAINT zero_precisa_de_diagnostico_antes_de_virar_lacuna
    CHECK (estado <> 'LACUNA_CANDIDATA' OR zero_diagnosticado)
);
comment on constraint zero_precisa_de_diagnostico_antes_de_virar_lacuna
  on public.lacuna_candidata is
  'Zero inesperado é chave quebrada até prova em contrário. O schema não '
  'deixa um zero virar lacuna sem alguém ter olhado a chave primeiro.';
