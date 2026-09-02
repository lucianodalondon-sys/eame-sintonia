-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 003
-- CONTEÚDO: o que foi publicado, e como se sabe que é um só.
--
-- Herda do Brasil o acerto central de `documentos`: unique(fonte, hash) e
-- autor pseudonimizado. Corrige duas coisas:
--   1. o Brasil guardava `cultura` singular no documento — o par CROP x ISSUE
--      não cabia, e por isso vivia só na camada analítica;
--   2. o Brasil tinha UM campo de lugar; aqui são dois (ver migration 001).
--
-- NÃO EXECUTADA.
-- ═══════════════════════════════════════════════════════════════════════

create type tipo_conteudo as enum
  ('video','post','comentario','transcricao','artigo','nota_tecnica','bula','anuncio','pagina');

create table public.conteudo (
  id                bigserial primary key,
  canal_id          bigint not null references public.canal(id) on delete restrict,
  run_id            text   not null references public.collection_run(run_id) on delete restrict,
  raw_asset_id      bigint references public.raw_asset(id) on delete set null,

  tipo              tipo_conteudo not null,
  content_id        text not null,          -- id da plataforma (video_id, post_id)
  url               text,
  titulo            text,
  descricao         text,
  publicado_em      timestamptz,
  duracao_seg       integer,
  hash_conteudo     char(64) not null,      -- sha256 do corpo, para dedupe real

  -- PESSOA DECLARADA no conteúdo != pessoa dona do canal. Um vídeo
  -- institucional pode declarar um pesquisador que não controla o canal.
  pessoa_declarada  text,
  papel_declarado   text,
  organizacao_declarada text,

  -- As duas geografias, sempre separadas.
  source_geografia_id bigint references public.geografia(id),
  fact_geografia_id   bigint references public.geografia(id),

  -- Independência: uma palestra republicada em 5 canais tem 5 linhas aqui,
  -- mas todas apontam para o MESMO obra_id. Contar evidência independente
  -- é contar obra_id distinto, nunca conteudo.id.
  obra_id           bigint references public.conteudo(id),
  originalidade     text not null default 'UNKNOWN' check (originalidade in
                    ('ORIGINAL','RESHARE','SYNDICATED','UNKNOWN')),

  coletado_em       timestamptz not null default now(),
  rule_version      text not null,

  -- MARCAR, NUNCA APAGAR. No Brasil a lei "um vídeo, uma transcrição" foi RECUSADA pelo
  -- banco: o acervo já a violava, e o índice único não pôde ser criado. O conserto foi
  -- uma coluna `duplicata_de` — a cópia mais completa fica, a outra aponta para ela, e
  -- a lei passa a valer daqui para frente sem destruir o que veio antes.
  duplicata_de      bigint references public.conteudo(id),
  UNIQUE (canal_id, content_id)
);
create index conteudo_hash_idx    on public.conteudo (hash_conteudo);
create index conteudo_obra_idx    on public.conteudo (obra_id);
create index conteudo_pub_idx     on public.conteudo (tipo, publicado_em desc);
create index conteudo_run_idx     on public.conteudo (run_id);

comment on column public.conteudo.obra_id is
  'A mesma obra em N canais NÃO são N evidências independentes. '
  'ORIGIN_ID != CHANNEL_ID != CONTENT_ID, e a independência conta obra.';
comment on column public.conteudo.hash_conteudo is
  'Dedupe por hash do corpo. Título igual NÃO colapsa: o Brasil mediu que '
  'título repetido é comum e id repetido é que é duplicata.';

-- TRANSCRIÇÃO é conteúdo derivado de conteúdo, com língua e fonte da legenda.
-- Fica em tabela própria porque o texto é pesado e nem todo vídeo tem.
create table public.transcricao (
  id             bigserial primary key,
  conteudo_id    bigint not null references public.conteudo(id) on delete cascade,
  run_id         text   not null references public.collection_run(run_id) on delete restrict,
  raw_asset_id   bigint references public.raw_asset(id) on delete set null,
  idioma         text,
  caption_source text check (caption_source in ('AUTO','MANUAL','MIXED','NAO_SEI')),
  texto          text not null,
  hash_texto     char(64) not null,
  rule_version   text not null,
  criado_em      timestamptz not null default now(),
  -- NULLS NOT DISTINCT é obrigatório aqui: `idioma` e `caption_source` são nuláveis, e
  -- no Postgres dois nulos são DIFERENTES. Sem isto a trava destranca sozinha justamente
  -- para as linhas que deixaram o campo em branco — que são as piores de duplicar.
  UNIQUE NULLS NOT DISTINCT (conteudo_id, idioma, caption_source)
);
comment on column public.transcricao.caption_source is
  'Legenda automática e legenda humana não têm o mesmo valor probatório. '
  'NAO_SEI é resposta legítima; NULL seria omissão.';

-- AUTOR pseudonimizado, exatamente como o Brasil resolveu.
-- Permite contar pessoas distintas sem identificar ninguém.
create table public.comentario (
  id             bigserial primary key,
  conteudo_id    bigint not null references public.conteudo(id) on delete cascade,
  run_id         text   not null references public.collection_run(run_id) on delete restrict,
  externo_id     text,
  autor_hash     char(64),                  -- NUNCA nome, NUNCA @
  texto          text not null,
  hash_conteudo  char(64) not null,
  publicado_em   timestamptz,
  UNIQUE (conteudo_id, hash_conteudo)
);
comment on column public.comentario.autor_hash is
  'Pseudonimizado na entrada. O limite de dado pessoal é constraint, não '
  'lembrete: docs/regras/LIMITES-DE-DADO-PESSOAL-EAME.md, pendência P-008.';
create index comentario_autor_idx on public.comentario (autor_hash);
