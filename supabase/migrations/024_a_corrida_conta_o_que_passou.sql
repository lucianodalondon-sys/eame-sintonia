-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 024
-- A CORRIDA PASSA A CONTAR O QUE PASSOU POR ELA
--
-- Tres missoes seguidas acharam o mesmo tipo de defeito, e sempre tarde: um
-- estado publicado sem a medicao que o sustentaria. O mapa dizia «2 estradas
-- fechadas» e a medicao disse zero. O instrumento dizia «sem conexao» onde
-- havia caminho transitivo. O piloto dizia «houve RAW» quando o RAW era do
-- checkout.
--
--     UM SISTEMA QUE NAO SABE CONTAR O PROPRIO FLUXO
--     PRECISA DE ALGUEM QUE ESCREVA O NUMERO A MAO.
--     E O NUMERO ESCRITO A MAO E SEMPRE O OTIMISTA.
--
-- DUAS TABELAS, E NAO UMA POR CONCEITO
-- ------------------------------------
-- O prompt desta missao lista muitos nomes — RUN TRACE, STAGE TRACE, EDGE
-- PASSAGE, FAILURE EVENT, FAILURE SNAPSHOT, COUNTS BY GRAIN, ACCOUNTED INPUT.
-- Criar uma tabela para cada seria transcrever o prompt, nao modelar o sistema.
--
-- Medido: uma PASSAGEM DE ETAPA ja e uma passagem de ARESTA (de onde veio, para
-- onde foi) com contagens; e uma FALHA ja e uma passagem com estado FAIL e os
-- campos de diagnostico preenchidos. Sao a mesma linha vista de tres angulos.
-- Separa-las obrigaria a fazer join para responder «o que aconteceu nesta
-- etapa», e a manter tres verdades sobre o mesmo instante.
--
--     FAILURE SNAPSHOT NAO E OUTRA TABELA.
--     E A MESMA PASSAGEM, COM O ESTADO ERRADO.
--
-- O QUE NAO NASCE AQUI, PORQUE JA TEM DONO
-- ----------------------------------------
--   RUN          `collection_run` (001) — actor, custo, metodo do custo, status
--   RAW          `raw_asset` (001)
--   DERIVED      `derived_artifact` (022)
--   CHECKPOINT   `checkpoint_coleta` (016)
--   ACESSO       `fonte_externa` + `fonte_acesso_teste` (020)
--   FALHA        `leis/falhas.py` — 23 estados canonicos em tres camadas
--
-- Nao ha `flow_run` aqui: seria uma segunda corrida paralela a `collection_run`,
-- e duas corridas divergem na primeira pressa.
--
-- NÃO EXECUTADA EM PRODUÇÃO. Aplicada e conferida num PostgreSQL 16 local e
-- descartavel. Aplicar em producao continua sendo trabalho de outra missao,
-- com autorizacao propria.
-- ═══════════════════════════════════════════════════════════════════════

begin;

-- ── O VOCABULARIO ────────────────────────────────────────────────────────
-- Os nomes vem do que a casa ja usa. `ERROR` e `REJECTED` sao separados de
-- proposito: um item recusado por regra e um FATO sobre o item; um item que
-- explodiu e um fato sobre NOS. Junta-los apagaria a diferenca entre «a fonte
-- disse nao» e «o nosso codigo quebrou» — que e a lei de `falhas.py`.
-- ⚠️ CORRIGIDO EM O8C, ANTES DE QUALQUER APLICACAO.
-- A versao anterior deste enum era uma MISTURA de duas perguntas:
--
--     PASS, REJECTED, UNKNOWN, ERROR, NOT_RUN, SKIPPED, NOT_APPLICABLE
--
-- `REJECTED` e `UNKNOWN` NAO sao estados de uma ETAPA — sao portas por onde um
-- ITEM sai. Uma etapa nao e «recusada»; um item e. Com as duas especies no
-- mesmo enum, `estado='REJECTED'` podia significar duas coisas e o banco
-- aceitava as duas.
--
--     STAGE STATE != ITEM DESTINATION.
--
-- O dono do vocabulario e `leis/telemetria.py`, que ja as tinha separadas em
-- duas tuplas. Este enum passa a ser EXATAMENTE `ESTADOS_DE_ETAPA`, e os
-- destinos do item vivem onde sempre deviam ter vivido: nos baldes da
-- contabilidade, mais abaixo. `provas/paridade_da_lingua.py` reprova se algum
-- dia divergirem.
--
-- `FAIL` e nao `ERROR`: a ETAPA falha, o ITEM erra. Duas palavras porque sao
-- duas coisas — e era a confusao entre elas que fazia um defeito parecer cinco.
create type etapa_estado as enum (
  'NOT_RUN', 'RUNNING', 'PASS', 'PARTIAL', 'FAIL', 'SKIPPED', 'NOT_APPLICABLE');

-- As etapas canonicas da aquisicao. A fronteira desta missao termina em READY:
-- INTELLIGENCE, PACKAGE, PORTAL e DELIVERY NAO entram, e nao entram de
-- proposito — o mesmo protocolo podera segui-los depois, mas exigi-los agora
-- faria a fundacao da coleta depender de coisas que nao sao coleta.
create type etapa_da_coleta as enum (
  'DECIDE', 'CHECK', 'DISCOVER', 'FETCH', 'RAW', 'DERIVED',
  'STRUCTURED', 'ADMISSION', 'READY');

-- ── A DECISAO, QUE VEM ANTES DO GASTO ────────────────────────────────────
-- Sem este recibo, mais tarde sabemos o RESULTADO e nao sabemos POR QUE o
-- sistema decidiu gastar. E uma decisao que ninguem consegue explicar tambem
-- nao consegue ser comparada com outra — o que mataria a evolucao antes dela
-- comecar.
create table public.decisao_de_coleta (
  id                    bigserial primary key,
  decision_id           text not null unique,
  requirement_id        text,
  source_id             text not null,
  route_class_id        text,
  acao                  text not null check (acao in ('CHECK','FETCH','SKIP','TRIAL','RETRY')),
  decidida_em           timestamptz not null default now(),
  prioridade            text not null check (prioridade in ('P0','P1','P2','P3','P4')),
  -- As tres perguntas que tornam a decisao auditavel. NOT NULL de proposito:
  -- uma decisao sem POR QUE AGORA nao e auditavel, e o red team desta missao
  -- exige que ela seja recusada na entrada, nao descoberta depois.
  why_now               text not null,
  why_this_source       text not null,
  why_this_route        text,
  satisfaction_before   text not null check (satisfaction_before in
                          ('YES_FRESH','YES_BUT_STALE','PARTIAL','NO','UNKNOWN')),
  staleness_horas       numeric(10,2),
  -- VETOR, e nao nota. Colapsar em `SOURCE_SCORE = 87` perderia exatamente a
  -- informacao que permite dizer POR QUE uma fonte vale — e uma nota que
  -- ninguem sabe desmontar nao se audita nem se melhora.
  expected_value        jsonb,
  expected_cost_usd     numeric(12,6),
  is_exploration        boolean not null default false,
  -- Sem versao de politica a decisao nao pode ser comparada com outra: nao se
  -- sabe qual regra a produziu. O red team recusa decisao sem versao.
  policy_version        text not null,
  -- Corrida legada ou manual e legitima. O que nao e legitimo e inventar um
  -- recibo que nao existiu.
  decision_provenance   text not null default 'POLICY'
                        check (decision_provenance in ('POLICY','MANUAL','LEGACY')),
  criada_em             timestamptz not null default now()
);
create index decisao_fonte_idx on public.decisao_de_coleta (source_id, decidida_em desc);

comment on table public.decisao_de_coleta is
  'O recibo que vem ANTES do gasto. Sem ele saberiamos o resultado e nao o '
  'motivo. UMA DECISAO SEM WHY_NOW NAO E AUDITAVEL.';
comment on column public.decisao_de_coleta.expected_value is
  'VETOR de dimensoes, nunca uma nota. SOURCE_SCORE = 87 perde a razao de ser '
  'do numero, e nota que ninguem desmonta nao se melhora.';

-- ── A PASSAGEM: ETAPA, ARESTA, CONTAGEM E FALHA, NA MESMA LINHA ──────────
create table public.etapa_da_corrida (
  id                    bigserial primary key,
  run_id                text not null references public.collection_run(run_id) on delete cascade,
  decision_id           text references public.decisao_de_coleta(decision_id) on delete set null,
  source_id             text,
  route_class_id        text,
  etapa                 etapa_da_coleta not null,
  -- A ARESTA. `edge_from` NULL = etapa de entrada do fluxo.
  edge_from             etapa_da_coleta,
  tentativa             integer not null default 0,

  comecou_em            timestamptz not null default now(),
  terminou_em           timestamptz,
  duracao_ms            integer,

  -- ── O GRAO ──────────────────────────────────────────────────────────
  -- OBRIGATORIO nos dois lados. Sem ele, 100 documentos que viram 250 alegacoes
  -- viram «250% de rendimento» — um numero que nao existe. O grao muda, e a
  -- razao entre contagens de especies diferentes nao e rendimento.
  input_grain           text,
  input_count           integer,
  output_grain          text,
  output_count          integer,
  cardinalidade         text check (cardinalidade in ('1:1','1:N','N:1','N:M','NAO_SE_APLICA')),

  -- ── A CONTABILIDADE ─────────────────────────────────────────────────
  -- NAO E OBRIGATORIO QUE 100% CHEGUE AO FIM.
  -- E OBRIGATORIO QUE 100% TENHA EXPLICACAO.
  -- ⚠️ UM BALDE POR DESTINO DE ITEM, E EXATAMENTE OS DE `telemetria.py`.
  -- Ate O8C faltavam dois e sobrava um:
  --
  --   FALTAVA `reused`   — a casa ja escrevia REUSED em `preservar_coleta.py`
  --                        e `preservar_derivado.py`, ANTES desta missao. Sem
  --                        o balde, 100 entradas com 60 novas e 40 reencontros
  --                        davam UNACCOUNTED=40: um defeito inventado por
  --                        falta de coluna, num fluxo que estava correto.
  --   FALTAVA `not_run`  — item que nunca chegou a ser processado.
  --   SOBRAVA `skipped`  — SKIPPED e estado de ETAPA, nao destino de ITEM.
  --                        Estava aqui por copia do enum misturado acima.
  passed                integer not null default 0,
  rejected              integer not null default 0,
  error_count           integer not null default 0,
  not_run_count         integer not null default 0,
  unknown_count         integer not null default 0,
  reused                integer not null default 0,
  -- Colunas GERADAS: ninguem escreve `accounted` a mao, e por isso ninguem
  -- pode escrever um numero que fecha sem fechar.
  accounted_input       integer generated always as
                          (passed + rejected + error_count
                           + not_run_count + unknown_count + reused) stored,
  unaccounted_input     integer generated always as
                          (coalesce(input_count, 0)
                           - (passed + rejected + error_count
                              + not_run_count + unknown_count + reused)) stored,

  estado                etapa_estado not null,
  custo_usd             numeric(12,6),
  actor                 text,
  actor_version         text,
  policy_version        text,

  -- ── O DIAGNOSTICO ───────────────────────────────────────────────────
  -- A MENSAGEM PODE MUDAR. O CODIGO E ESTAVEL. Quem alerta olha o codigo;
  -- quem depura le a mensagem. Guardar so a mensagem faz o alerta quebrar na
  -- primeira vez que alguem melhora o texto do erro.
  diagnostic_code       text,
  error_class           text,
  error_message_redacted text,
  canonical_state       text,          -- de `leis/falhas.py`, quando aplicavel
  http_status           integer,

  -- ── A RETOMADA ──────────────────────────────────────────────────────
  last_good_artifact    text,
  checkpoint_before     text,
  checkpoint_after      text,

  criada_em             timestamptz not null default now(),

  -- Uma passagem por (corrida, etapa, tentativa). Retentar cria linha nova, e
  -- a anterior FICA: apagar a tentativa que falhou apagaria a evidencia do que
  -- se esta a tentar consertar.
  UNIQUE (run_id, etapa, tentativa),

  -- FALHA PRECISA DE CODIGO. Sem isto, um FAIL sem diagnostico e um alerta que
  -- ninguem sabe encaminhar — e o proximo a olhar vai ter de reproduzir tudo.
  CONSTRAINT falha_tem_codigo CHECK (estado <> 'FAIL' OR diagnostic_code IS NOT NULL),

  -- ETAPA QUE CONSOME PRECISA DECLARAR O GRAO. Sem grao, contagem nao se
  -- compara com contagem — e foi assim que 100 -> 250 virou percentagem.
  CONSTRAINT contagem_tem_grao CHECK (input_count IS NULL OR input_grain IS NOT NULL),
  CONSTRAINT saida_tem_grao CHECK (output_count IS NULL OR output_grain IS NOT NULL)
);
create index etapa_run_idx    on public.etapa_da_corrida (run_id, etapa);
create index etapa_fonte_idx  on public.etapa_da_corrida (source_id, comecou_em desc);
create index etapa_estado_idx on public.etapa_da_corrida (estado) where estado = 'FAIL';
-- Indice pelo proprio instante, e nao por `date_trunc('hour', ...)`: com
-- `timestamptz` aquela funcao depende do fuso da sessao e o Postgres a recusa
-- num indice, com razao — o mesmo instante cairia em horas diferentes para
-- sessoes diferentes. A busca por janela usa BETWEEN sobre este indice.
create index etapa_hora_idx   on public.etapa_da_corrida (comecou_em);

comment on table public.etapa_da_corrida is
  'UMA linha por passagem. Ela e ao mesmo tempo o STAGE TRACE, o EDGE PASSAGE '
  '(edge_from -> etapa) e o FAILURE SNAPSHOT (estado=FAIL com diagnostico). '
  'Sao a mesma linha vista de tres angulos; separa-las manteria tres verdades '
  'sobre o mesmo instante.';
comment on column public.etapa_da_corrida.unaccounted_input is
  'GERADA. O alvo de integridade e ZERO. Nao exige que tudo chegue ao fim: '
  'exige que tudo tenha explicacao. 100 entram, 80 passam, 10 recusados, 5 '
  'unknown, 4 erro -> 1 sem explicacao -> FLOW_UNACCOUNTED_INPUT.';
comment on column public.etapa_da_corrida.input_grain is
  'OBRIGATORIO quando ha contagem. 100 DOCUMENTOS que viram 250 ALEGACOES nao '
  'sao 250% de rendimento: o grao mudou, e a razao nao e rendimento.';

-- ── A VISTA POR JANELA ───────────────────────────────────────────────────
-- View e nao tabela: agregacao guardada seria uma segunda verdade que envelhece
-- sozinha, e a primeira pergunta seria «este numero e de quando?».
create view public.v_coleta_por_hora as
select
  date_trunc('hour', e.comecou_em)              as hora,
  e.source_id,
  e.route_class_id,
  e.etapa,
  e.input_grain,
  e.output_grain,
  count(*)                                       as passagens,
  sum(coalesce(e.input_count, 0))                as entraram,
  sum(coalesce(e.output_count, 0))               as sairam,
  sum(e.passed)                                  as passaram,
  sum(e.rejected)                                as recusados,
  sum(e.unknown_count)                           as unknown,
  sum(e.error_count)                             as com_erro,
  sum(e.not_run_count)                           as nao_correram,
  sum(e.reused)                                  as reencontrados,
  sum(e.unaccounted_input)                       as sem_explicacao,
  sum(coalesce(e.custo_usd, 0))                  as custo_usd,
  sum(coalesce(e.duracao_ms, 0))                 as duracao_ms
from public.etapa_da_corrida e
group by 1,2,3,4,5,6;

comment on view public.v_coleta_por_hora is
  'Por hora, fonte, rota e etapa. `entraram` e `sairam` NAO se dividem quando '
  'os graos diferem — por isso os dois graos aparecem na propria linha.';

-- ── A SAUDE, DERIVADA ────────────────────────────────────────────────────
-- SOURCE + ROUTE, e nao SOURCE: uma fonte pode ter uma rota morta e outra viva.
--
--     ROUTE FAILURE NAO E SOURCE BAD.
create view public.v_saude_da_rota as
select
  e.source_id,
  e.route_class_id,
  count(*) filter (where e.estado = 'PASS')      as passagens_ok,
  count(*) filter (where e.estado = 'FAIL')      as passagens_falha,
  max(e.comecou_em) filter (where e.estado = 'PASS')  as ultimo_sucesso,
  max(e.comecou_em) filter (where e.estado = 'FAIL') as ultima_falha,
  sum(coalesce(e.custo_usd, 0))                  as custo_total,
  avg(e.duracao_ms)                              as duracao_media_ms
from public.etapa_da_corrida e
where e.source_id is not null
group by 1,2;

comment on view public.v_saude_da_rota is
  'A saude e do par (fonte, rota). ROUTE FAILURE NAO E SOURCE BAD: uma fonte '
  'pode ter uma estrada morta e outra viva, e condenar a fonte apagaria a viva.';

commit;
