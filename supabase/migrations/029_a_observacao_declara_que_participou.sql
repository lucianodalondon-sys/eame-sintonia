-- ═══════════════════════════════════════════════════════════════════════
-- 029 · A OBSERVAÇÃO DECLARA QUE PARTICIPOU — uma relação, e nem uma a mais
--
-- A `022` decidiu o grão do derivado, e a decisão está certa e fica:
--
--     DERIVED_ARTIFACT grain = CONTEÚDO POR RECEITA
--     duas capturas dos mesmos bytes + mesma receita = UMA linha
--
-- O que não se sustentava era a frase que ela deixou ao lado — que nenhuma
-- procedência se perde, porque as irmãs se encontram com
-- `where sha256 = parent_sha256`. Essa consulta responde «que observações TÊM
-- os mesmos bytes». Não responde «que observações PASSARAM por esta derivação».
--
--     CAN INFER != OBSERVED EDGE.
--     TER OS MESMOS BYTES NÃO É TER PARTICIPADO DA MESMA EXECUÇÃO.
--
-- Medido em `provas/a_linhagem_do_reaproveitamento.py`, contra a rota real:
-- para um derivado, a consulta por sha devolve DUAS observações, e as duas
-- chegam iguais. Uma foi lida e derivada; a outra pode ter sido reaproveitada
-- ou pode nunca ter sido processada. Nada no estado persistido as separa.
--
-- E o runtime SABIA. `guarda/preservar_derivado.py` devolve, no reencontro,
-- `TESTEMUNHA_NO_BANCO` e `TESTEMUNHA_DESTA_CHAMADA` — os dois lados da
-- aresta. Calculava-os, nomeava-os, e deitava-os fora.
--
--     RUNTIME SABE != O SISTEMA GUARDA.
--     O QUE MORRE COM O PROCESSO NÃO É LINHAGEM.
--
-- ── POR QUE UMA TABELA, E NÃO UMA COLUNA ──────────────────────────────────
--
-- `derived_artifact.raw_asset_id` já existe e é TESTEMUNHA: diz de qual cópia
-- se leu. Ela é UMA, e a participação é N — o mesmo derivado é usado por
-- todas as observações dos mesmos bytes. Alargar a testemunha a N valores
-- faria o derivado voltar a crescer por captura, que é exactamente o grão que
-- a `022` tirou.
--
-- E não cabe em `etapa_da_corrida`: o grão de lá é a PASSAGEM, uma linha por
-- `(run_id, etapa, tentativa)`, e ela não tem onde pôr N pares. A `028` até
-- fecha essa porta por `check`: `raw_asset_id` só é preenchível na etapa RAW.
--
--     TELEMETRIA NÃO É MATERIAL DE LINHAGEM.
--
-- ── O GRÃO, EM UMA FRASE ──────────────────────────────────────────────────
-- Uma linha aqui diz: ESTA observação participou da produção ou da
-- reutilização DESTE derivado. Uma vez. Para sempre.
--
-- A frase foi medida contra os quatro casos que a quebrariam
-- (`provas/a_linhagem_do_reaproveitamento.py`):
--
--   1ª derivação de uma observação          linha NOVA
--   retry da MESMA observação, mesma corrida  NENHUMA linha nova
--   outra observação, MESMOS bytes            linha NOVA, para o mesmo derivado
--   rederivar a mesma observação noutra corrida  NENHUMA linha nova
--
--     ARESTAS DISTINTAS NOS QUATRO CASOS   2
--     PASSAGENS SOBRE A ARESTA `1->3`      3
--
-- Os dois números medem conjuntos diferentes, e é por isso que são dois
-- conceitos. A passagem tem dono há muito: `etapa_da_corrida`.
--
-- ── O QUE NÃO ENTRA, E POR QUÊ ────────────────────────────────────────────
--
--   run_id NA CHAVE      medido: a mesma aresta é tocada por passagens de
--                        corridas DIFERENTES. Com a corrida na chave, o mesmo
--                        facto material teria duas linhas — e a chave nem
--                        conseguiria formular QUAL corrida: a que capturou a
--                        observação, ou a da passagem que derivou?
--
--                        UMA CHAVE QUE NÃO SABE RESPONDER «QUAL DOS DOIS?»
--                        NÃO É UMA IDENTIDADE: É UMA AMBIGUIDADE COM ÍNDICE.
--
--   tentativa            é chave da PASSAGEM, em `(run_id, etapa, tentativa)`.
--                        Um retry não cria linhagem nova. E a casa já decidiu
--                        isto um andar abaixo: `raw_asset.attempts` é
--                        «TELEMETRIA, e fora da chave de idempotência».
--
--   INSERTED / REUSED    medido: a MESMA aresta teve `PASSED` na primeira
--                        passagem e `REUSED` nas seguintes. O facto material
--                        não mudou; o resultado mudou três vezes.
--
--                        UMA RELAÇÃO QUE SE REESCREVE A CADA PASSAGEM
--                        NÃO É UMA RELAÇÃO.
--
--                        `STAGE STATE != ITEM DESTINATION` (024). E o destino
--                        POR ITEM não está guardado em lado nenhum hoje — o
--                        balde da passagem guarda QUANTOS, nunca QUAIS. Isso
--                        fica declarado como limite conhecido, e não se
--                        conserta aqui por antecipação.
--
--   surrogate id         não há segunda chave a proteger, e um `bigserial` por
--                        hábito seria um identificador que ninguém cita.
--
-- ── BACKFILL: NENHUM ──────────────────────────────────────────────────────
-- A aresta nunca foi escrita, e a inferência por `sha256` não distingue quem
-- participou de quem apenas tem os mesmos bytes. Uma migration que populasse
-- esta tabela por sha escreveria como FACTO exactamente aquilo que a medição
-- prova não ser sabido.
--
--     PREENCHER O PASSADO POR INFERÊNCIA
--     É FABRICAR A EVIDÊNCIA QUE FALTAVA.
--
-- A relação vale a partir daqui. O que é anterior fica UNKNOWN, que é a
-- verdade — e a tabela nasce VAZIA de propósito.
--
-- A decisão inteira, com as opções medidas e o red team, está em
-- `docs/decisoes/ADR-LINHAGEM-DO-REAPROVEITAMENTO-V1.md`.
--
-- NAO EXECUTADA EM PRODUCAO. Aplicada e conferida num PostgreSQL 16 local e
-- descartavel, sobre a cadeia canonica inteira lida do disco. Aplicar em
-- producao continua sendo trabalho de outra missao, com autorizacao propria.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.participacao_na_derivacao (
  -- ── OS DOIS LADOS DA ARESTA ─────────────────────────────────────────
  -- A OBSERVAÇÃO que participou. `raw_asset.id`, e não o sha256 (que é a
  -- identidade dos BYTES) nem o storage_path (que é um ENDEREÇO).
  raw_asset_id        bigint not null
                      references public.raw_asset(id) on delete restrict,

  -- O DERIVADO de que ela participou — produzindo-o ou reencontrando-o.
  derived_artifact_id bigint not null
                      references public.derived_artifact(id) on delete restrict,

  -- ── A PROVENIÊNCIA, E ELA NÃO É IDENTIDADE ──────────────────────────
  -- A corrida da PASSAGEM em que esta aresta foi vista pela primeira vez.
  --
  -- ⚠️ NÃO É `raw_asset.run_id`, E A DIFERENÇA FOI MEDIDA. A corrida que
  -- CAPTUROU a observação não é necessariamente a que a DERIVOU: o banco
  -- aceita uma passagem de derivação que nomeia outra corrida, e a prova
  -- exercita exactamente esse caso. Copiar uma para a outra por conveniência
  -- escreveria como facto uma coisa falsa.
  --
  --     A CORRIDA QUE CAPTUROU NÃO É NECESSARIAMENTE A QUE DERIVOU.
  --
  -- `not null` é a forma de a recusa ser executada pelo banco em vez de
  -- depender de quem escreve: toda passagem de derivação nomeia uma corrida
  -- (`derivacao_forward.correr()` exige `run_id`, sem valor por omissão), e
  -- quem não a souber não escreve a linha.
  first_seen_derivation_run_id text not null
                      references public.collection_run(run_id) on delete restrict,

  -- O instante da PRIMEIRA PERSISTÊNCIA desta linha.
  --
  -- ⚠️ AQUI O `default now()` É LEGÍTIMO, ao contrário do que a `022` avisa
  -- sobre `derived_at`. Lá o `not null` provava que havia uma data e NÃO
  -- provava que ela tinha sido medida em vez de copiada do pai. Aqui a data É
  -- o momento da escrita — o relógio do banco no `insert` é exactamente a
  -- coisa que se quer registar, e não uma aproximação dela.
  --
  --     UM `default now()` MENTE QUANDO A COLUNA FALA DE OUTRO MOMENTO.
  --     AQUI ELA FALA DESTE.
  first_seen_at       timestamptz not null default now(),

  -- ── A IDENTIDADE ────────────────────────────────────────────────────
  -- Chave natural, sem surrogate. Duas linhas iguais significariam que a
  -- mesma observação participou duas vezes da mesma derivação — e participar
  -- outra vez não é participar duas vezes.
  constraint participacao_e_unica_por_par
    primary key (raw_asset_id, derived_artifact_id)
);

-- Quem pergunta «que observações passaram por este derivado?» entra pelo lado
-- do derivado, e a chave primária começa pela observação.
create index participacao_por_derivado_idx
  on public.participacao_na_derivacao (derived_artifact_id);

-- Quem pergunta «que arestas esta corrida estabeleceu?».
create index participacao_por_corrida_idx
  on public.participacao_na_derivacao (first_seen_derivation_run_id);

alter table public.participacao_na_derivacao enable row level security;

comment on table public.participacao_na_derivacao is
  'ESTA observacao participou da producao ou da reutilizacao DESTE derivado. '
  'Uma linha por par, e nao por passagem: retry e reprocessamento nao criam '
  'linha nova. O grao do derivado continua CONTEUDO POR RECEITA (022); esta '
  'tabela e o que faltava para as capturas irmas nao se distinguirem apenas '
  'por inferencia de sha256. Nasce VAZIA: nao ha backfill honesto.';

comment on column public.participacao_na_derivacao.raw_asset_id is
  'A OBSERVACAO. raw_asset.id, e nunca o sha256 (identidade dos BYTES) nem o '
  'storage_path (ENDERECO). ON DELETE RESTRICT: apagar uma observacao que '
  'participou de uma derivacao tem de doer.';

comment on column public.participacao_na_derivacao.derived_artifact_id is
  'O DERIVADO de que ela participou. Um derivado tem N participantes quando N '
  'capturas trouxeram os mesmos bytes — e e por isso que isto e uma tabela e '
  'nao uma coluna: derived_artifact.raw_asset_id e TESTEMUNHA, e testemunha e '
  'uma so.';

comment on column public.participacao_na_derivacao.first_seen_derivation_run_id is
  'A corrida da PASSAGEM em que esta aresta foi vista pela primeira vez. NAO e '
  'raw_asset.run_id: a corrida que capturou nao e necessariamente a que '
  'derivou, e isso esta medido. Nao se reescreve nas passagens seguintes — e '
  'proveniencia da primeira vez, e nao identidade da aresta.';

comment on column public.participacao_na_derivacao.first_seen_at is
  'Quando esta linha foi escrita pela primeira vez. NAO e derived_at (do '
  'artefato) nem comecou_em (da passagem). O default now() e legitimo porque a '
  'coluna fala do proprio instante da escrita.';

comment on constraint participacao_e_unica_por_par on public.participacao_na_derivacao is
  'Participar outra vez nao e participar duas vezes. Retry, reprocessamento e '
  'derivacao noutra corrida reencontram a linha; nao criam uma segunda. E a '
  'chave natural e quem resolve a concorrencia, com on conflict do nothing.';
