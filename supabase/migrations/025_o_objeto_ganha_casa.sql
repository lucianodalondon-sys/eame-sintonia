-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 025
-- O OBJETO GANHA CASA
--
-- `raw_asset` guardava duas especies na mesma linha, e a tabela dizia as duas
-- coisas ao mesmo tempo. A migration 022 escreveu, por gente desta casa:
--
--     «Em `raw_asset` o grao e a OCORRENCIA, porque duas capturas sao DOIS
--      FACTOS SOBRE O MUNDO.»
--
-- E a migration 001, na MESMA tabela, escreveu isto:
--
--     storage_path text not null unique
--
-- Um endereco unico por linha e a definicao de OBJETO DE STORAGE. A prosa diz
-- ocorrencia, a trava diz objeto, e a trava ganha sempre — porque e ela que
-- recusa a escrita.
--
--     ESTA MIGRATION NAO TRAZ IDEIA NOVA.
--     FAZ A TRAVA CONCORDAR COM A FRASE QUE A CASA JA TINHA ASSINADO.
--
-- ESCOPO: FASES 1-6 DO PLANO, E NEM UMA A MAIS
-- --------------------------------------------
-- O plano inteiro esta em `docs/operacao/CIRURGIA-OBJETO-E-OBSERVACAO.md`, e
-- tem onze fases. Esta migration faz seis, e todas sao ADITIVAS:
--
--   1 criar `storage_object` + RLS
--   2 povoar, um objeto por endereco existente
--   3 acrescentar `raw_asset.storage_object_id`, anulavel, com chave estrangeira
--   4 ligar cada observacao ao objeto dela
--   5 check condicional `preservado => objeto`, primeiro NOT VALID
--   6 VALIDATE CONSTRAINT
--
-- O QUE ELA NAO FAZ, E FICA DITO PARA NAO SE ACREDITAR NO CONTRARIO:
--
--   NAO retira `unique (raw_asset.storage_path)`   -> fase 10
--   NAO retira `raw_asset.storage_path`            -> fase 11
--   NAO acrescenta `source_id`, `document_key`,
--       `document_key_basis`, estado de legado,
--       `attempts`, `last_attempt_at`              -> fases 7-9
--   NAO instala chave de idempotencia              -> fase 9
--
-- ⚠️ E POR ISSO, DEPOIS DESTA MIGRATION, A SEGUNDA CORRIDA DO MESMO CONTEUDO
-- AINDA CONFLITA. O conflito nasce de `unique (storage_path)` sobre a
-- observacao, e essa trava so cai na fase 10. Separar as especies e a
-- CONDICAO da cura; nao e a cura.
--
--     NEW_RUN_SAME_CONTENT_RESOLVED = NO
--
-- NENHUM `raw_asset.id` MUDA
-- -------------------------
-- `raw_asset` continua a ser a OBSERVACAO, no lugar, com os mesmos `id`. Isso
-- nao e conveniencia: NOVE chaves estrangeiras de cinco migrations apontam
-- para `raw_asset.id` (003, 006, 010, 014 e a composta da 022), e os `id`
-- vivos sao esparsos — o canario forward recebeu 890 num banco de 252 linhas.
-- Copiar as observacoes para uma tabela nova e renumerar obrigaria a reescrever
-- as nove a mao, e nao ha mapa de 1..N para reconstruir.
--
--     RAW_OBSERVATION_ID_PRESERVED_IN_PLACE = YES
--
-- NAO EXECUTADA EM PRODUCAO. Aplicada e conferida num PostgreSQL 16
-- descartavel, por `provas/objeto_e_observacao_no_postgres.py`. Aplicar em
-- producao continua a ser trabalho de outra missao, com autorizacao propria.
-- ═══════════════════════════════════════════════════════════════════════

-- ── FASE 1 · A CASA DO OBJETO ──────────────────────────────────────────
-- O GRAO, EM UMA FRASE: uma linha aqui e UMA copia de bytes gravada UMA vez
-- num endereco do armazem.
--
-- Nao e o conteudo — esse e o `sha256`, e o mesmo conteudo pode estar em duas
-- copias. Nao e a ida a fonte — essa e a observacao, e a mesma copia pode ser
-- observada em dez corridas. E a COPIA: aquilo que ocupa espaco e que se pode
-- ler de volta.
create table if not exists public.storage_object (
  id             bigserial primary key,

  -- A IDENTIDADE DA COPIA E O ENDERECO DELA, e nao o hash do que ela contem.
  -- `guarda/preservar_coleta.py::caminho_do_objeto()` ja compoe este endereco
  -- com um discriminante de publicacao la dentro, e o comentario dele cita o
  -- caso que obrigou a isso.
  storage_path   text not null unique,

  media_type     text not null,
  bytes          bigint not null,

  -- ⚠️ SEM `unique`, E ISTO E MEDIDO, NAO PRECAUCAO.
  -- No armazem a serio, duas chaves carregam o mesmo etag e os mesmos 138.284
  -- bytes:
  --
  --   IT/adama-website/DOCUMENT/227779fdd6be9975-6321-Postscript-80-XL-….pdf
  --   IT/adama-website/DOCUMENT/227779fdd6be9975-731-Scheda-di-sicurezza-….pdf
  --
  -- A ADAMA publicou a mesma ficha de seguranca como ficha de DOIS produtos.
  -- Sao dois factos sobre o mundo, e um `unique (sha256)` aqui apagaria um
  -- deles em silencio.
  --
  --     UM CONTEUDO  ->  DUAS PUBLICACOES  ->  DOIS OBJETOS
  sha256         char(64) not null,

  created_at     timestamptz not null default now(),

  -- O formato do hash, e SO o formato — mesmo check que a 022 ja usa no
  -- derivado. `raw_asset.sha256` nunca teve este check, e por isso ele e
  -- tambem a rede que apanha um hash estragado a atravessar a fase 2. Se
  -- existir um, esta migration REPROVA — que e melhor do que copia-lo em
  -- silencio e terminar verde.
  constraint sha256_do_objeto_tem_formato
    check (sha256 ~ '^[0-9a-f]{64}$'),

  -- UM ENDERECO EM BRANCO NAO E UM ENDERECO. `not null` sozinho aceita uma
  -- string de espacos, e uma copia que se diz guardada sem dizer onde e
  -- exatamente o caso que a fase 5 existe para recusar.
  constraint objeto_tem_endereco
    check (btrim(storage_path) <> '')
);

comment on table public.storage_object is
  'A COPIA FISICA. Uma linha e UM byte-string gravado UMA vez num endereco. '
  'Nao e o conteudo (isso e o sha256) nem a ida a fonte (isso e raw_asset).';
comment on column public.storage_object.storage_path is
  'A IDENTIDADE desta especie. O endereco carrega o discriminante da '
  'publicacao, e e por isso que duas publicacoes dos mesmos bytes sao duas '
  'linhas — medido nos objetos italianos.';
comment on column public.storage_object.sha256 is
  'A identidade dos BYTES, e NAO desta linha. Sem `unique`, de proposito.';

create index if not exists storage_object_hash_idx
  on public.storage_object (sha256);

-- Mesma regra do resto da casa: a 006 ligou RLS em todas as tabelas, e a 022
-- fez o mesmo para o derivado. Sem policy nova — nao ha acesso publico a
-- inventar aqui.
alter table public.storage_object enable row level security;

-- ── FASE 2 · POVOAR, PELO DADO E NAO POR UM NUMERO ─────────────────────
-- Um objeto por endereco que ja existe em `raw_asset`. A correspondencia e
-- total e injetora POR CONSTRUCAO: `raw_asset.storage_path` e `not null` e
-- `unique` desde a 001, portanto cada linha tem exatamente um endereco e
-- nenhum endereco se repete.
--
-- SEM FILTRO, DE PROPOSITO. Um `where` que saltasse linha estranha faria a
-- fase 5 reprovar mais tarde sobre uma observacao que esta fase escolheu
-- ignorar — e o diagnostico apareceria longe da causa. Aqui entram todas, e
-- os checks da fase 1 recusam em voz alta o que nao puder entrar.
--
-- E o numero nao esta escrito em lado nenhum: a migration corre pelo dado.
insert into public.storage_object (storage_path, media_type, bytes, sha256)
select a.storage_path, a.media_type, a.bytes, a.sha256
  from public.raw_asset a
on conflict (storage_path) do nothing;

-- ── FASE 3 · A LIGACAO ─────────────────────────────────────────────────
-- ANULAVEL, e nao por preguica. A 001 ja aceita observacao com
-- `preserved = false` — uma tentativa que nao trouxe bytes e uma observacao
-- legitima, e obriga-la a apontar para um objeto seria inventar uma copia que
-- nao existe.
--
--     OBSERVACAO DE TENTATIVA  !=  OBSERVACAO PRESERVADA COM BYTES
--
-- ON DELETE RESTRICT: apagar um objeto que ainda tem observacoes levaria a
-- memoria delas junto, em silencio. Mesma escolha da 022 para o derivado.
alter table public.raw_asset
  add column if not exists storage_object_id bigint
    references public.storage_object(id) on delete restrict;

comment on column public.raw_asset.storage_object_id is
  'QUAL COPIA esta observacao preservou. N observacoes podem apontar para o '
  'mesmo objeto — e esse e o ponto da separacao. Anulavel porque uma '
  'observacao NAO PRESERVADA nao tem copia para apontar.';

create index if not exists raw_storage_object_idx
  on public.raw_asset (storage_object_id);

-- ── FASE 4 · LIGAR CADA OBSERVACAO AO OBJETO DELA ──────────────────────
-- PELO ENDERECO, E NUNCA PELO SHA. Dois objetos podem carregar os mesmos
-- bytes — e o caso medido acima e exatamente esse. Um join por `sha256`
-- ligaria a observacao a copia errada, e as duas pareceriam certas.
update public.raw_asset a
   set storage_object_id = o.id
  from public.storage_object o
 where o.storage_path = a.storage_path
   and a.storage_object_id is null;

-- ── FASE 5 · A TRAVA CONDICIONAL, PRIMEIRO SEM VALIDAR ─────────────────
-- `NOT VALID` primeiro: a trava passa a valer para o que vier a seguir sem
-- varrer a tabela inteira no mesmo folego. E entao valida-se, explicitamente,
-- para que a promessa cubra tambem o que ja la estava.
--
-- SO UMA DIRECAO. `preservado => tem objeto` e o que o plano autorizou. A
-- direcao inversa — `nao preservado => nao tem objeto` — NAO entra aqui:
-- alargar uma fase em silencio e como assinar uma linha que ninguem leu.
alter table public.raw_asset
  add constraint preservado_aponta_para_a_copia
  check (not preserved or storage_object_id is not null) not valid;

comment on constraint preservado_aponta_para_a_copia on public.raw_asset is
  'PRESERVADO E UMA AFIRMACAO, e uma afirmacao tem de poder ser conferida. '
  'Uma linha que se diz preservada e nao diz onde estao os bytes nao e '
  'conferivel — e nao entra. NOT_PRESERVED continua a poder existir sem copia.';

-- ── FASE 6 · VALIDAR ───────────────────────────────────────────────────
alter table public.raw_asset
  validate constraint preservado_aponta_para_a_copia;
