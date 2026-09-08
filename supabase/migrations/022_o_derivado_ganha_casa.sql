-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 022
-- O DERIVADO GANHA CASA
--
-- RAW e o que foi COLHIDO. DERIVED e o que NOS PRODUZIMOS a partir do RAW.
-- Sao duas especies, e por isso sao duas tabelas. Acrescentar um
-- `parent_sha256` ao `raw_asset` seria mais curto e apagaria a COL-LAW-007
-- dentro da tabela chamada «bruto» — uma tabela que se chama bruto com filhos
-- la dentro mente para todo leitor futuro.
--
-- NAO EXECUTADA EM PRODUCAO. Aplicada e conferida num PostgreSQL 16 local e
-- descartavel, no workflow `banco-descartavel`, que morre no fim do job.
-- Aplicar em producao continua sendo trabalho de outra missao, com autorizacao
-- propria.
--
-- O QUE A MEDICAO DECIDIU, E ONDE ELA ESTA
-- ----------------------------------------
-- `system-map/data/derivacoes.generated.json`, produzido por
-- `system-map/scripts/censo_das_derivacoes.py`:
--
--   7 produtores medidos, e so 3 sao de DERIVED_ARTIFACT.
--   A legenda que o YouTube entrega com o video NAO e derivado — nos nao a
--   produzimos, e mete-la aqui declararia uma linhagem que nao existe.
--   Um campo extraido tambem nao e: e registo estruturado, com outra casa.
--   Um juizo de admissao muito menos: COL-LAW-502, documento pronto nao e
--   fato pronto.
--
--   43 derivacoes reais, todas TEXT_EXTRACTION por `texto-de-pdf`.
--   2 ferramentas de derivacao existem: `texto-de-pdf` e `whisper`.
-- ═══════════════════════════════════════════════════════════════════════

-- ── O GRAO, EM UMA FRASE ──────────────────────────────────────────────
-- Uma linha aqui representa UM artefato que NOS produzimos, a partir de UM
-- conteudo bruto, por UMA ferramenta numa VERSAO, com UM conjunto de
-- parametros, e numa POSICAO da serie quando a derivacao produz varios.
--
-- A frase foi testada contra os oito casos que a quebrariam:
--
--   PDF -> TXT                        1 linha
--   o mesmo PDF -> OCR                outro `kind`, outra linha
--   o mesmo PDF -> thumbnail          outro `kind`, outra linha
--   o mesmo PDF -> 10 frames          MESMO kind, mesma ferramenta, mesma
--                                     versao, mesmos parametros — e DEZ
--                                     artefatos. E o caso que quebra qualquer
--                                     chave sem `serie_posicao`.
--   audio -> transcricao              1 linha
--   o mesmo RAW por DUAS versoes       duas linhas, e as duas sao legitimas
--   retry identico                     mesma chave, mesmos bytes -> REUSED
--   os mesmos bytes por rotas          `producer` diferente -> duas linhas com
--     diferentes                       o mesmo sha256

create table if not exists public.derived_artifact (
  id              bigserial primary key,

  -- ── DE QUEM ISTO NASCEU ─────────────────────────────────────────────
  -- O pai e uma linha de `raw_asset`: UM OBJETO PRESERVADO, com a corrida que
  -- o trouxe. NOT NULL de proposito — derivado sem bruto canonico e a coisa
  -- que esta missao recusou fabricar. Os 43 derivados italianos de hoje NAO
  -- cabem aqui, e isso e o desenho a funcionar, nao um defeito: eles sao
  -- LEGACY_DERIVATION_WITHOUT_CANONICAL_RAW_PARENT, e a migration e FORWARD.
  raw_asset_id    bigint not null references public.raw_asset(id) on delete restrict,

  -- O sha256 do PAI, repetido aqui de proposito. A linhagem verdadeira sao os
  -- BYTES: uma copia pode mudar de caminho ou ser apagada do armazem sem que o
  -- filho deixe de saber de que conteudo veio.
  parent_sha256   char(64) not null,

  -- ── O QUE ISTO E ────────────────────────────────────────────────────
  -- Uma lista fechada, e curta. Ela cresce por migration, com um caso real a
  -- justificar — nao por antecipacao.
  kind            text not null check (kind in (
                    'TEXT_EXTRACTION',   -- pdftotext, html->texto
                    'OCR',               -- quando nao ha camada de texto
                    'TRANSCRIPTION',     -- whisper sobre audio
                    'TRANSLATION',
                    'THUMBNAIL',
                    'FRAME',
                    'TABLE_EXTRACTION')),

  -- ── QUEM PRODUZIU, E COM QUE REGUA ──────────────────────────────────
  producer        text not null,          -- texto-de-pdf, whisper
  -- «whisper» NAO BASTA. O modelo `base` e o `small` sobre o mesmo audio dao
  -- textos diferentes, e os dois sao legitimos — esta escrito em
  -- ferramentas/youtube_transcrever.py, nao e hipotese. Sem a versao na
  -- identidade, a segunda passagem apagaria a primeira em silencio.
  producer_version text not null,
  pipeline_version text,

  -- Os parametros que mudam a saida (idioma forcado, DPI do OCR, intervalo dos
  -- frames). Guarda-se o HASH deles para a chave, e o corpo para o humano.
  -- Sem parametros: a string vazia tem hash proprio e estavel, e nao e NULL —
  -- NULL em chave e a porta pela qual entram duas linhas iguais.
  parameters      jsonb,
  parameters_hash char(64) not null,

  -- A POSICAO NA SERIE. NULL quando a derivacao produz UM artefato; 0..N
  -- quando produz varios do mesmo tipo — os 10 frames do mesmo video. E o
  -- unico campo que existe so por causa de um caso que ainda nao temos, e
  -- existe porque sem ele a chave e falsa no dia em que ele aparecer.
  serie_posicao   integer check (serie_posicao is null or serie_posicao >= 0),

  -- ── O ARTEFATO ──────────────────────────────────────────────────────
  -- So entra aqui o que EXISTE. Uma derivacao que falhou nao tem bytes, e
  -- portanto nao tem linha: ela vive no manifesto da corrida, com o erro.
  -- Guardar linhas de erro aqui faria a tabela dos artefatos contar coisas que
  -- nao sao artefatos, e toda contagem em cima dela passaria a mentir.
  sha256          char(64) not null,
  bytes           bigint not null check (bytes >= 0),
  media_type      text not null,
  -- Os BYTES vivem no Storage; aqui vive a MEMORIA deles. UNIQUE porque o grao
  -- e o objeto guardado, tal como em `raw_asset`.
  storage_path    text not null unique,

  derived_at      timestamptz not null,
  created_at      timestamptz not null default now(),

  -- Um rotulo para agrupar a leva que produziu isto. NAO e chave estrangeira e
  -- NAO cria entidade: nao houve prova de que a derivacao precise de uma RUN
  -- propria, e esticar `collection_run` para significar algo que nao e coleta
  -- seria pior do que nao ter nada.
  derivation_batch text,

  -- ── AS TRAVAS ───────────────────────────────────────────────────────
  -- A IDENTIDADE DA DERIVACAO. Repetir a mesma derivacao com a mesma regua nao
  -- cria linha nova: e reencontro. Mudar de ferramenta, de versao, de
  -- parametros ou de tipo cria — porque e outra derivacao.
  --
  -- E o `sha256` do FILHO NAO entra aqui, de proposito. Se entrasse, a mesma
  -- identidade com bytes diferentes viraria duas linhas caladas — e e
  -- exatamente esse caso que tem de dar CONFLITO, nao silencio.
  constraint derivacao_e_unica_por_regua
    unique nulls not distinct (parent_sha256, kind, producer, producer_version,
                               parameters_hash, serie_posicao),

  constraint sha256_do_filho_tem_formato
    check (sha256 ~ '^[0-9a-f]{64}$'),
  constraint sha256_do_pai_tem_formato
    check (parent_sha256 ~ '^[0-9a-f]{64}$'),

  -- DERIVADO NASCE DEPOIS DO BRUTO. Nao se conferem aqui as duas datas — o
  -- `captured_at` mora noutra tabela — mas garante-se que a data existe e nao
  -- foi herdada: quem escreve tem de a declarar.
  constraint derivado_declara_quando_nasceu
    check (derived_at is not null)
);

create index derived_parent_idx   on public.derived_artifact (parent_sha256);
create index derived_raw_idx      on public.derived_artifact (raw_asset_id);
create index derived_kind_idx     on public.derived_artifact (kind, producer);
create index derived_sha_idx      on public.derived_artifact (sha256);

alter table public.derived_artifact enable row level security;

comment on table public.derived_artifact is
  'O que NOS produzimos a partir de um conteudo bruto. RAW nao e DERIVED: por '
  'isso esta tabela existe em vez de uma coluna em raw_asset. Uma linha e UM '
  'artefato, de UM bruto, por UMA ferramenta numa VERSAO, com UNS parametros, '
  'numa POSICAO da serie.';

comment on column public.derived_artifact.parent_sha256 is
  'A linhagem verdadeira sao os BYTES do pai. O raw_asset_id diz de QUAL copia '
  'se leu; o sha256 diz de que CONTEUDO se trata, e sobrevive a copia mudar de '
  'caminho ou sair do armazem.';

comment on column public.derived_artifact.producer_version is
  'NUNCA opcional. `whisper` nao basta: `base` e `small` sobre o mesmo audio '
  'dao textos diferentes, e os dois sao legitimos. Sem versao na identidade, a '
  'segunda passagem apagaria a primeira em silencio. Versao historica que nao '
  'se consegue provar entra como UNKNOWN, nunca adivinhada.';

comment on column public.derived_artifact.serie_posicao is
  'NULL quando a derivacao produz um artefato so. 0..N quando produz varios do '
  'mesmo tipo — os frames de um video. Sem isto, dez frames colidiriam na '
  'mesma chave.';

comment on column public.derived_artifact.sha256 is
  'Os bytes do FILHO. NAO entra na chave de identidade: se entrasse, a mesma '
  'derivacao com resultado diferente viraria duas linhas caladas em vez de dar '
  'conflito. E sha256 igual em dois derivados NAO prova mesma linhagem — duas '
  'rotas podem chegar aos mesmos bytes.';

comment on column public.derived_artifact.derivation_batch is
  'Rotulo da leva, para agrupar. NAO e chave estrangeira e NAO cria entidade: '
  'nao houve prova de que a derivacao precise de uma RUN propria, e esticar '
  'collection_run para algo que nao e coleta seria pior do que nao ter nada.';

comment on constraint derivacao_e_unica_por_regua on public.derived_artifact is
  'Retry identico e REENCONTRO, nao linha nova. Trocar de ferramenta, de versao '
  'ou de parametros e OUTRA derivacao, e as duas coexistem — a antiga nao se '
  'apaga porque a nova chegou.';

comment on constraint derived_artifact_raw_asset_id_fkey on public.derived_artifact is
  'ON DELETE RESTRICT, e nao CASCADE. Apagar um bruto que tem filhos levaria a '
  'linhagem junto, em silencio. Aqui o banco recusa — a evidencia de que o '
  'derivado existiu vale mais do que a comodidade de apagar.';
