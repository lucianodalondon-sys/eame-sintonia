-- ═══════════════════════════════════════════════════════════════════════
-- 030 · O DOCUMENTO GANHA REGISTO — e não ganha um canal que não tem
--
-- A estrada canónica parava em `DERIVED -> STRUCTURED`, e parava por uma
-- razão medida: `public.conteudo.canal_id` é `not null`, e não há canal para
-- um boletim em PDF publicado no sítio de uma agência regional.
--
-- ── POR QUE `conteudo` NÃO SERVE, E NÃO É DEFEITO DELE ────────────────────
--
-- `conteudo` é a casa do que uma PLATAFORMA publica. Está escrito nas próprias
-- colunas dela:
--
--     canal.channel_id     «o id da plataforma, NUNCA o nome»
--     conteudo.content_id  «id da plataforma (video_id, post_id)»
--
-- Um boletim agrometeorológico da ARPAV não tem nenhum dos dois. O sítio de
-- uma agência não emite identificadores de canal, e o PDF não tem um id que a
-- plataforma lhe tenha dado — porque não há plataforma.
--
--     A TABELA PRESSUPÕE UMA PLATAFORMA QUE EMITA IDENTIFICADORES.
--     UMA FONTE DOCUMENTAL NÃO É UMA.
--
-- Havia três saídas, e duas fabricavam identidade:
--
--   1. inventar um `channel_id` a partir da URL, do domínio, do `SOURCE_ID`
--      ou do nome da agência          → IDENTIDADE FABRICADA. Recusada.
--   2. afrouxar `conteudo.canal_id`   → mudar o contrato de uma tabela que
--                                       está certa para o que ela é.
--   3. dar ao documento a casa dele   → esta migration.
--
--     SOURCE != ENDPOINT != ARTIFACT.
--     Provar a fonte e provar o endpoint não cria um canal.
--
-- ── E POR QUE NÃO UMA DAS TABELAS DA 021 ──────────────────────────────────
--
-- A `021` criou seis famílias para o FACTO PUBLICADO POR TERCEIRO —
-- `clima_observacao`, `boletim_fitossanitario` e as outras. Elas são
-- documentais e são chaveadas pela FONTE, o que parece encaixar.
--
-- Não encaixa, e o catálogo diz porquê: **nenhuma delas liga a `raw_asset` ou
-- a `derived_artifact`**. Elas guardam o FACTO já extraído — «choveu 12 mm
-- entre estas duas datas» — e não o DOCUMENTO de que ele foi lido. São o
-- degrau seguinte, e não este.
--
--     O FACTO LIDO DE UM DOCUMENTO NÃO É O DOCUMENTO.
--     Usar uma para a outra perderia a linhagem que a estrada acabou de ganhar.
--
-- ── O GRÃO, EM UMA FRASE ──────────────────────────────────────────────────
-- Uma linha aqui é UM texto derivado, estruturado como registo de documento.
--
-- A chave é o `derived_artifact_id`, e a razão é a mesma da `022`: o registo é
-- do CONTEÚDO que nós produzimos, e não da ocorrência que o trouxe. Duas
-- capturas dos mesmos bytes partilham um derivado — e partilham este registo.
-- Quem participou está em `participacao_na_derivacao` (029), que é o dono
-- dessa pergunta.
--
--     ONE CONCEPT → ONE OWNER.
--     O REGISTO NÃO REPETE A LINHAGEM: ELE APOIA-SE NELA.
--
-- ── A IDENTIDADE DO DOCUMENTO, E O QUE NÃO SE INVENTA ─────────────────────
--
-- `document_id` é ANULÁVEL de propósito. Ele só se preenche quando a própria
-- fonte o prova — um número de boletim, um identificador de registo, um DOI.
--
--     DOCUMENT_ID SÓ EXISTE QUANDO A FONTE CONSEGUE PROVÁ-LO.
--     Nunca se deriva de sha256, URL, filename, timestamp, slug ou caminho.
--
-- Sem prova: NULL, que quer dizer NÃO SEI. E o registo continua a ter
-- identidade — a dele, `derived_artifact_id`, tal como a observação tem
-- `raw_asset.id`. Uma coisa é a identidade do nosso registo; outra é a
-- identidade que o mundo deu ao documento. Confundi-las é que seria fabricar.
--
-- ── O TEMPO E O LUGAR NÃO ENTRAM ──────────────────────────────────────────
-- Não há aqui `fact_time`, `fact_location` nem `publicado_em`. Não por
-- esquecimento: porque nada nesta passagem os prova, e uma coluna que nasce
-- para ficar sempre nula é especulação com cara de contrato.
--
--     FACT_TIME != PUBLICATION_TIME != OBSERVED_TIME != COLLECTED_TIME.
--     Quem os vier a provar traz a coluna, e traz a prova com ela.
--
-- NAO EXECUTADA EM PRODUCAO. Aplicada e conferida num PostgreSQL 16 local e
-- descartavel, sobre a cadeia canonica inteira lida do disco. Aplicar em
-- producao continua sendo trabalho de outra missao, com autorizacao propria.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.documento_estruturado (
  -- ── A IDENTIDADE, E ELA É O TEXTO DERIVADO ──────────────────────────
  -- Um derivado, um registo. Reprocessar reencontra; não cria segundo.
  derived_artifact_id bigint primary key
                      references public.derived_artifact(id) on delete restrict,

  -- ── A PROCEDÊNCIA ───────────────────────────────────────────────────
  -- A corrida da PASSAGEM que estruturou. Não é a corrida que capturou a
  -- observação, pela mesma razão que a `029` já mediu.
  run_id              text not null
                      references public.collection_run(run_id) on delete restrict,

  -- A FONTE, declarada pelo coletor. Nunca inferida de URL, caminho ou slug.
  source_id           text not null,

  -- ── O CORPO ─────────────────────────────────────────────────────────
  texto               text not null,
  -- O sha256 do corpo, para dedupe real e para conferir sem reler os bytes.
  hash_texto          char(64) not null
                      constraint hash_texto_tem_formato
                      check (hash_texto ~ '^[0-9a-f]{64}$'),

  -- ── O QUE SÓ ENTRA COM PROVA ────────────────────────────────────────
  -- NULL = NAO SEI. Nenhum destes se deriva do caminho nem do hash.
  document_id         text,
  source_url          text,
  titulo              text,

  estruturado_em      timestamptz not null default now(),

  -- Um documento estruturado sem fonte seria um texto órfão com cara de
  -- registo. `source_id` vazio ou com espaço a fingir conteúdo não passa.
  constraint documento_declara_a_fonte
    check (length(btrim(source_id)) > 0),

  -- ⚠️ E `document_id`, QUANDO EXISTE, NÃO PODE SER O HASH NEM O CAMINHO.
  -- Não é uma trava de omnisciência: é a recusa dos dois atalhos concretos
  -- que esta casa já viu tentarem passar por identidade.
  constraint document_id_nao_e_o_hash
    check (document_id is null or document_id <> hash_texto)
);

-- Quem pergunta «que documentos esta corrida estruturou?».
create index documento_por_corrida_idx
  on public.documento_estruturado (run_id);

-- Quem pergunta «que documentos vieram desta fonte?».
create index documento_por_fonte_idx
  on public.documento_estruturado (source_id);

-- Dedupe real por corpo, quando alguém precisar de o procurar.
create index documento_por_hash_idx
  on public.documento_estruturado (hash_texto);

alter table public.documento_estruturado enable row level security;

comment on table public.documento_estruturado is
  'O REGISTO ESTRUTURADO DE UM DOCUMENTO NAO-PLATAFORMA. `conteudo` e a casa '
  'do que uma PLATAFORMA publica — ela exige canal, e canal exige um id que a '
  'plataforma tenha emitido. Um boletim em PDF no sitio de uma agencia nao tem '
  'nenhum dos dois. SOURCE != ENDPOINT != ARTIFACT: provar a fonte e o '
  'endpoint nao cria um canal. O grao e UM texto derivado, e a linhagem de '
  'quem participou vive em participacao_na_derivacao.';

comment on column public.documento_estruturado.derived_artifact_id is
  'A IDENTIDADE deste registo, e ela e o texto derivado. Duas capturas dos '
  'mesmos bytes partilham o derivado e partilham este registo — quem '
  'participou responde-se em participacao_na_derivacao, que e o dono dessa '
  'pergunta. Reprocessar reencontra esta linha; nao cria uma segunda.';

comment on column public.documento_estruturado.document_id is
  'A identidade que O MUNDO deu ao documento — numero de boletim, registo, '
  'DOI. NULL quer dizer NAO SEI, e e a resposta certa quando a fonte nao a '
  'prova. NUNCA se deriva de sha256, URL, filename, timestamp, slug ou '
  'storage_path. A identidade do NOSSO registo e outra coisa, e e a chave '
  'primaria desta tabela.';

comment on column public.documento_estruturado.source_id is
  'A fonte canonica, declarada pelo coletor. Nunca reconstruida de URL, '
  'caminho, slug ou hash.';

comment on column public.documento_estruturado.run_id is
  'A corrida da PASSAGEM que estruturou. NAO e necessariamente a corrida que '
  'capturou a observacao — a 029 mediu que as duas podem ser diferentes.';

comment on constraint document_id_nao_e_o_hash on public.documento_estruturado is
  'O hash identifica BYTES, e nao documento. Esta trava recusa o atalho mais '
  'provavel; os outros (URL, filename, caminho) sao do writer, e e la que se '
  'provam.';
