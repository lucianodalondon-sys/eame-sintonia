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
--
--   DUAS CAPTURAS do mesmo conteudo    UMA linha. E a decisao abaixo.
--     derivadas com a mesma receita
--
-- ── CONTEUDO OU CAPTURA? A DECISAO, E O PORQUE ────────────────────────
-- Duas corridas trouxeram os mesmos bytes: sao DUAS capturas legitimas, com
-- duas linhas em `raw_asset`. Se as duas forem derivadas com a mesma receita,
-- ha UMA linha aqui ou DUAS?
--
--     RESPOSTA: UMA. O grao e CONTEUDO POR RECEITA.
--
-- E a assimetria e deliberada. Em `raw_asset` o grao e a OCORRENCIA, porque
-- duas capturas sao DOIS FACTOS SOBRE O MUNDO: a fonte publicou nos dois
-- sitios, e apagar uma perderia a prova de que o documento nao mudou entre
-- elas. Aqui nao ha dois factos: ha UM — a nossa ferramenta, sobre estes
-- bytes, com esta regua, da este resultado. Correr duas vezes e trabalho
-- repetido, nao informacao nova, e os bytes de saida sao identicos ao byte.
--
--     MESMOS BYTES NAO APAGAM A DIFERENCA ENTRE DUAS CAPTURAS.
--     Mas nao criam duas derivacoes onde so houve uma receita.
--
-- E A PROCEDENCIA DA CAPTURA NAO SE PERDE, porque ela nunca morou aqui: mora
-- em `raw_asset`, uma linha por captura, com a sua corrida, o seu
-- `captured_at` e a sua URL. Todas as irmas encontram-se com
--
--     select * from raw_asset where sha256 = <parent_sha256>
--
-- O `raw_asset_id` desta tabela diz apenas DE QUAL COPIA SE LEU. E testemunha,
-- e esta escrito assim na coluna — nao se finge que e a identidade do pai.

-- ── A TRAVA QUE TORNA A COERENCIA POSSIVEL ────────────────────────────
-- Para que uma chave estrangeira COMPOSTA possa apontar para (id, sha256) do
-- bruto, o Postgres exige que esse par seja unico la. Como `id` ja e a chave
-- primaria, o par (id, sha256) e unico por construcao — esta trava nao pode
-- reprovar sobre dado nenhum, presente ou futuro. Ela existe apenas para dar
-- ao banco o alvo declarativo de que ele precisa.
--
-- ADITIVA E NAO DESTRUTIVA: nao altera coluna, nao move dado, nao apaga nada.
-- E a unica coisa que esta migration toca fora da sua propria tabela.
alter table public.raw_asset
  add constraint raw_asset_id_e_sha_juntos unique (id, sha256);

comment on constraint raw_asset_id_e_sha_juntos on public.raw_asset is
  'Nao e uma regra nova: (id, sha256) ja era unico porque id e chave primaria. '
  'Existe para que derived_artifact possa exigir, por chave estrangeira '
  'composta, que o pai por ID e o pai por SHA sejam o MESMO pai.';

create table if not exists public.derived_artifact (
  id              bigserial primary key,

  -- ── DE QUEM ISTO NASCEU ─────────────────────────────────────────────
  -- DOIS CAMPOS DECLARAM O MESMO PARENTESCO, E POR ISSO NAO PODEM DISCORDAR.
  --
  -- Um red team encontrou a brecha e ela foi REPRODUZIDA no Postgres antes de
  -- ser fechada: com chaves estrangeiras separadas, dava para escrever
  -- `raw_asset_id` = A e `parent_sha256` = os bytes de B. As duas travas
  -- passavam — porque A existe, e porque o sha tinha o formato certo — e a
  -- linha ficava a dizer duas coisas ao mesmo tempo.
  --
  --     FK EXISTIR NAO BASTA.
  --     O PAI POR ID E O PAI POR SHA TEM DE SER O MESMO PAI.
  --
  -- A trava esta la em baixo, em `o_pai_por_id_e_o_pai_por_sha_sao_o_mesmo`, e
  -- e DECLARATIVA: uma chave estrangeira composta, nao um gatilho. O banco
  -- garante sozinho, sem depender de quem escreve.

  -- QUAL COPIA FOI LIDA. E uma TESTEMUNHA, nao a identidade do pai: quando o
  -- mesmo conteudo foi capturado duas vezes, ha duas linhas de `raw_asset`
  -- com o mesmo sha256, e esta aponta para aquela de que se leu. As outras
  -- capturas nao se perdem — continuam inteiras em `raw_asset`, cada uma com a
  -- sua corrida e o seu `captured_at`, e encontram-se todas com
  -- `where sha256 = parent_sha256`.
  raw_asset_id    bigint not null,

  -- O PAI DE VERDADE SAO OS BYTES. Uma copia pode mudar de caminho ou sair do
  -- armazem sem que o filho deixe de saber de que conteudo nasceu. E e este
  -- campo — nao o `raw_asset_id` — que entra na identidade da derivacao,
  -- porque o grao e CONTEUDO POR RECEITA. Ver a nota do grao, mais abaixo.
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
  -- ⚠️ O BANCO CONFERE O FORMATO, NAO A CORRESPONDENCIA. Ele nao sabe se este
  -- hash e o do JSON ao lado: para isso teria de conhecer a serializacao
  -- canonica de quem escreveu (ordem das chaves, espacos, numeros). Um gatilho
  -- que tentasse adivinha-la seria uma segunda implementacao da regra, livre
  -- para divergir da primeira — e duas verdades sao piores do que uma so.
  --
  -- A AUTORIDADE E O WRITER. Ele serializa e ele resume, com uma funcao so, e
  -- e la que o teste tem de morar. Aqui fica dito de quem e a
  -- responsabilidade, para nao se acreditar que o banco a assumiu.
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

  -- ⚠️ NOT NULL PROVA QUE HA UMA DATA. NAO PROVA QUE ELA FOI MEDIDA.
  -- O comentario anterior dizia que esta trava garantia que a data «nao foi
  -- herdada» do `captured_at`. Nao garante, e nunca podia: o banco ve um
  -- timestamptz, nao ve de onde ele veio. Quem copiasse o `captured_at` para
  -- aqui passaria por esta trava sem um arranhao.
  --
  --     DB_PROVES_PRESENT  !=  DB_PROVES_NOT_COPIED.
  --
  -- A lei continua a valer — quem escreve tem de MEDIR o momento da derivacao,
  -- e nao herda-lo. Mas ela e do WRITER, e e la que se prova, com teste.
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

  -- ── A COERENCIA DO PARENTESCO, DECLARATIVA ──────────────────────────
  -- As duas colunas de pai viajam JUNTAS para `raw_asset(id, sha256)`. Se o
  -- `raw_asset_id` for de A e o `parent_sha256` for de B, nao existe par (A,
  -- bytes-de-B) do outro lado, e o banco recusa. Sem gatilho, e sem confiar em
  -- quem escreve.
  --
  -- ON DELETE RESTRICT continua a valer: apagar um bruto que tem filhos levaria
  -- a linhagem junto, em silencio.
  constraint o_pai_por_id_e_o_pai_por_sha_sao_o_mesmo
    foreign key (raw_asset_id, parent_sha256)
    references public.raw_asset (id, sha256) on delete restrict,

  constraint sha256_do_filho_tem_formato
    check (sha256 ~ '^[0-9a-f]{64}$'),
  constraint sha256_do_pai_tem_formato
    check (parent_sha256 ~ '^[0-9a-f]{64}$'),
  -- O FORMATO do hash dos parametros, e SO o formato. O banco nao sabe — nem
  -- pode saber — se este hash corresponde ao JSON da coluna `parameters`: para
  -- isso teria de conhecer a serializacao canonica de quem escreveu. Ver o
  -- comentario da coluna: a autoridade e o writer, e e la que isso se prova.
  constraint parameters_hash_tem_formato
    check (parameters_hash ~ '^[0-9a-f]{64}$'),

  -- A data tem de EXISTIR. Nada mais do que isso — ver o comentario da coluna.
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
  'A linhagem verdadeira sao os BYTES do pai, e e este campo que entra na '
  'identidade da derivacao — o grao e CONTEUDO POR RECEITA. Sobrevive a copia '
  'mudar de caminho ou sair do armazem.';

comment on column public.derived_artifact.raw_asset_id is
  'DE QUAL COPIA SE LEU. E testemunha, nao identidade: quando o mesmo conteudo '
  'foi capturado duas vezes, ha duas linhas de raw_asset com o mesmo sha256 e '
  'esta aponta para aquela que se abriu. As outras capturas continuam inteiras '
  'em raw_asset, com a sua corrida e o seu captured_at, e acham-se com '
  'where sha256 = parent_sha256. Nenhuma procedencia se perde aqui.';

comment on column public.derived_artifact.derived_at is
  'Quando a derivacao aconteceu. O NOT NULL prova que ha uma data — NAO prova '
  'que ela foi medida em vez de copiada do captured_at do pai. Essa lei e do '
  'writer, e e la que se prova.';

comment on column public.derived_artifact.parameters_hash is
  'O banco confere o FORMATO, nao a correspondencia com o JSON ao lado: para '
  'isso teria de conhecer a serializacao canonica de quem escreveu. A '
  'autoridade e o writer.';

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

comment on constraint o_pai_por_id_e_o_pai_por_sha_sao_o_mesmo
  on public.derived_artifact is
  'As duas colunas de pai viajam JUNTAS para raw_asset(id, sha256). Com chaves '
  'separadas dava para escrever raw_asset_id de A e parent_sha256 de B, e as '
  'duas travas passavam — foi REPRODUZIDO no Postgres antes de ser fechado. FK '
  'EXISTIR NAO BASTA: o pai por id e o pai por sha tem de ser o mesmo pai. '
  'E ON DELETE RESTRICT, nao CASCADE: apagar um bruto com filhos levaria a '
  'linhagem junto, em silencio.';
