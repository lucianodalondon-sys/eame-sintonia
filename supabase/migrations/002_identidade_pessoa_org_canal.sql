-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 002
-- IDENTIDADE: pessoa, organização, canal — e a distância entre eles.
--
-- Esta é a migration que MAIS se afasta do Brasil, e de propósito.
-- No Brasil, `vozes` guarda os canais como COLUNAS (linkedin_url,
-- instagram, youtube, tiktok, site). Funciona para quatro plataformas
-- conhecidas e quebra na quinta: adicionar canal vira ALTER TABLE, e
-- "quantos canais esta pessoa tem?" não é uma consulta, é uma leitura de
-- colunas nulas.
--
-- O EAME precisa de 1 pessoa -> N canais -> N conteúdos como ESTRUTURA,
-- porque a regra "uma palestra republicada em 5 lugares não são 5
-- evidências" depende de conseguir contar origens distintas.
--
-- NÃO EXECUTADA.
-- ═══════════════════════════════════════════════════════════════════════

-- PERSON != ORGANIZATION. Duas tabelas, nunca uma com campo `tipo`:
-- uma pessoa tem ORCID e afiliação; uma organização tem ROR e sede.
-- Colapsar as duas foi o que produziu "cooperativa contada como voz técnica".
create table public.organizacao (
  id              bigserial primary key,
  nome_canonico   text not null,
  tipo            text check (tipo in
                  ('universidade','instituto_publico','cooperativa','associacao',
                   'empresa','midia','orgao_publico','congresso','outro')),
  ror_id          text unique,                 -- identificador declarado, não inferido
  organizacao_mae bigint references public.organizacao(id),
  geografia_id    bigint references public.geografia(id),
  created_at      timestamptz not null default now()
);

create table public.pessoa (
  id              bigserial primary key,
  nome_exibicao   text not null,
  orcid           text unique,                 -- pub.orcid.org, com dígito verificador
  openalex_id     text,
  identidade_status text not null default 'NAO_RESOLVIDA' check (identidade_status in
                  ('CONFIRMADA','CANDIDATA','NAO_RESOLVIDA','CONFLACAO_SUSPEITA','FRAGMENTACAO_SUSPEITA')),
  identidade_caution text,
  created_at      timestamptz not null default now()
);
comment on column public.pessoa.identidade_status is
  'UM ID != UMA PESSOA, nas DUAS direções. CONFLACAO e FRAGMENTACAO seguem '
  'expressáveis: o schema não pode fingir que a identidade está resolvida.';

-- Uma pessoa pode ter N OpenAlex IDs (fragmentação) e um OpenAlex ID pode
-- cobrir N pessoas (conflação). Por isso o vínculo é tabela, não coluna.
create table public.pessoa_identificador (
  id           bigserial primary key,
  pessoa_id    bigint not null references public.pessoa(id) on delete cascade,
  sistema      text not null check (sistema in ('ORCID','OPENALEX','ROR','SCOPUS','LATTES','OUTRO')),
  valor        text not null,
  evidencia    text not null,               -- COMO se sabe que é a mesma pessoa
  confianca    text not null check (confianca in ('ALTA','MEDIA','BAIXA')),
  UNIQUE (sistema, valor, pessoa_id)
);
comment on table public.pessoa_identificador is
  'Deliberadamente SEM unique(sistema,valor): o mesmo ID apontando para duas '
  'pessoas é conflação — um estado que precisa ser REPRESENTÁVEL para ser medido.';

create table public.afiliacao (
  pessoa_id       bigint not null references public.pessoa(id) on delete cascade,
  organizacao_id  bigint not null references public.organizacao(id) on delete cascade,
  desde           date,
  ate             date,
  fonte           text not null,
  primary key (pessoa_id, organizacao_id, fonte)
);

-- ORIGEM != CANAL != CONTEÚDO. A origem é quem publica; o canal é onde;
-- o conteúdo é o quê. Uma pessoa com LinkedIn e YouTube é UMA origem
-- com DOIS canais — e é isso que impede contar duas vezes.
create table public.origem (
  id              bigserial primary key,
  pessoa_id       bigint references public.pessoa(id) on delete set null,
  organizacao_id  bigint references public.organizacao(id) on delete set null,
  rotulo          text not null,
  created_at      timestamptz not null default now(),
  CONSTRAINT origem_e_pessoa_ou_organizacao
    CHECK (num_nonnulls(pessoa_id, organizacao_id) = 1)
);
comment on constraint origem_e_pessoa_ou_organizacao on public.origem is
  'Uma origem é pessoa OU organização, nunca as duas nem nenhuma. '
  'Foi a mistura das duas que fez cooperativa virar voz técnica.';

-- ⚠️ CHAVE NATURAL DA ORIGEM — o defeito-raiz do Brasil, corrigido antes de nascer.
-- Lá, `fontes` tem só `id bigserial primary key`: nenhuma chave natural. Resultado
-- medido: 102 nomes repetidos em 212 fontes. E como o dedupe de `documentos` é
-- unique(fonte_id, hash_conteudo), uma fonte cadastrada DUAS VEZES faz o mesmo
-- conteúdo entrar duas vezes — e para o índice isso é legítimo.
-- Aqui a origem é única por pessoa e por organização, em índice parcial porque
-- exatamente um dos dois é nulo em cada linha.
create unique index origem_por_pessoa_idx      on public.origem (pessoa_id)      where pessoa_id      is not null;
create unique index origem_por_organizacao_idx on public.origem (organizacao_id) where organizacao_id is not null;

create table public.canal (
  id            bigserial primary key,
  origem_id     bigint not null references public.origem(id) on delete cascade,
  plataforma    text not null check (plataforma in
                ('youtube','linkedin','instagram','web','podcast','x','tiktok','facebook','api')),
  channel_id    text not null,              -- id da plataforma, NUNCA o nome
  handle        text,                       -- pode mudar; não é identidade
  url           text,
  verificado_em date,
  evidencia_de_papel text,                  -- headline/cargo que sustenta o papel
  UNIQUE (plataforma, channel_id)
);
comment on column public.canal.channel_id is
  'NAME != HANDLE != URL != PROFILE != PERSON. A chave é o id da plataforma; '
  'handle é atributo mutável e nunca chave.';
