-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 023
-- O COMENTARIO TEM ID PROPRIO, E A THREAD TEM PAI
--
-- Dois defeitos da 003, medidos num PostgreSQL 16 descartavel antes de
-- qualquer linha ser escrita aqui.
--
-- DEFEITO 1 — DUAS PESSOAS PODEM ESCREVER A MESMA FRASE
-- ----------------------------------------------------
-- A 003 travou a identidade do comentario em `UNIQUE (conteudo_id,
-- hash_conteudo)`. Reproduzido: no mesmo video `ezRyN8vLVvc`, COMMENT-A e
-- COMMENT-B, autores diferentes, ambos «Grazie!». O banco aceitou o primeiro e
-- recusou o segundo.
--
--     comentarios reais: 2 · no banco: 1
--
--     COMMENT_ID NAO E COMMENT_TEXT.
--     HASH DO TEXTO NAO E IDENTIDADE DA OCORRENCIA.
--
-- «Grazie!», «Bravo», «👏», «Grazie mille» sao as frases mais comuns que
-- existem debaixo de um video. A trava do texto apagava exatamente a evidencia
-- mais frequente, e apagava em silencio: um writer com ON CONFLICT DO NOTHING
-- nunca teria contado quantas vozes perdeu.
--
-- A CASA JA SABIA, E SO O BANCO DISCORDAVA
-- ----------------------------------------
-- `social_envelope.envelope()` exige `native_id` de TODA rota, e
-- `social_envelope.dedupe()` ja funde por `PLATFORM + NATIVE_ID`. Mastodon
-- (`uri`), Bluesky (`uri`/`did`), Telegram (`post_id`) e YouTube (`COMMENT_ID`)
-- todos entregam ID nativo. A lei da identidade ja era da casa; a 003 e que
-- nao a tinha recebido. Por isso a identidade nova NAO e YouTube-only.
--
-- NAO SE MENTIU NO HASH
-- ---------------------
-- Meter o COMMENT_ID dentro de `hash_conteudo` fecharia a constraint sem tocar
-- no schema — e mudaria o significado da coluna pela porta dos fundos. Uma
-- coluna chamada «hash do conteudo» que carrega identidade mente para todo
-- leitor futuro, e o proximo a comparar dois textos por hash acharia diferentes
-- dois «Grazie!» iguais. `hash_conteudo` continua sendo o hash do TEXTO, e
-- serve para detectar EDICAO, nunca para dizer QUEM e a ocorrencia.
--
-- DEFEITO 2 — O BANCO NAO SABIA QUEM RESPONDE A QUEM
-- --------------------------------------------------
-- O executor preserva COMMENT_ID, PARENT_ID e IS_REPLY. `public.comentario`
-- nao tinha onde por o pai, entao a estrutura
--
--     comentario
--     └── resposta
--
-- morria na entrada do banco.
--
--     RAW PRESERVAR A THREAD NAO BASTA
--     se a camada estruturada afirma representar comentario
--     e apaga quem responde a quem.
--
-- ESCOLHA: `parent_externo_id`, NAO `parent_comentario_id`
-- -------------------------------------------------------
-- A plataforma ja entrega o ID do pai junto com a resposta. Guardar esse ID
-- direto tem tres consequencias que uma FK para `comentario.id` nao teria:
--
--   1. sem corrida de ordem — a resposta pode ser escrita antes do pai, e a
--      relacao observada continua correta;
--   2. uma resposta cujo pai ainda nao foi persistido continua sendo uma
--      RESPOSTA. Com FK obrigatoria ela seria recusada, e a tentacao seguinte
--      seria grava-la com pai nulo — isto e, PROMOVE-LA A TOP-LEVEL. Isso seria
--      inventar uma conversa que nao aconteceu;
--   3. e o que sabemos e o que fica escrito: o ID que a fonte declarou.
--
--     REPLY NAO E TOP-LEVEL.
--
-- `parent_externo_id IS NULL` significa TOP-LEVEL, e so isso. «Tem pai e o pai
-- ainda nao esta no banco» e outro estado, e o writer o reporta como
-- PARENT_NOT_PERSISTED — nao o converte em nada.
--
-- EXTERNO_ID PASSA A SER OBRIGATORIO
-- ----------------------------------
-- Medido: NENHUM produtor no repositorio escreve hoje em `public.comentario` —
-- zero writers. E todo produtor futuro passa pelo envelope, que exige
-- `native_id`. Entao o NOT NULL nao quebra ninguem, e sem ele UNKNOWN viraria
-- duplicata automatica: duas linhas sem ID nativo colidiriam entre si.
--
-- A alteracao falha ALTO se alguma linha existente violar. Isso e o
-- comportamento desejado: recusar e melhor do que decidir por conta propria o
-- que fazer com um comentario sem identidade.
--
-- NÃO EXECUTADA EM PRODUÇÃO. Aplicada e conferida num PostgreSQL 16 local e
-- descartavel. Aplicar em producao continua sendo trabalho de outra missao,
-- com autorizacao propria.
-- ═══════════════════════════════════════════════════════════════════════

begin;

-- ── 1 · O PAI DA RESPOSTA ────────────────────────────────────────────────
alter table public.comentario
  add column if not exists parent_externo_id text;

comment on column public.comentario.parent_externo_id is
  'ID NATIVO do comentario pai, como a plataforma o declarou. NULL = TOP-LEVEL, '
  'e so isso. Nao e FK de proposito: a resposta pode chegar antes do pai, e '
  'recusa-la faria alguem grava-la com pai nulo — promovendo uma RESPOSTA a '
  'TOP-LEVEL. REPLY NAO E TOP-LEVEL.';

-- Uma resposta nao pode ser pai de si mesma. Barato, e fecha um erro de writer
-- que so apareceria depois, como uma thread que se referencia em circulo.
alter table public.comentario
  drop constraint if exists comentario_nao_responde_a_si_mesmo;
alter table public.comentario
  add constraint comentario_nao_responde_a_si_mesmo
  check (parent_externo_id is null or parent_externo_id <> externo_id);

-- Reconstruir a thread por SELECT precisa deste indice; sem ele, montar a
-- conversa obrigaria a varrer a tabela ou a abrir o RAW.
create index if not exists comentario_parent_idx
  on public.comentario (conteudo_id, parent_externo_id);

-- ── 2 · A IDENTIDADE DA OCORRENCIA ───────────────────────────────────────
-- Guarda antes do NOT NULL: uma mensagem que diz o que fazer vale mais do que
-- um erro de constraint sozinho.
do $$
declare n bigint;
begin
  select count(*) into n from public.comentario where externo_id is null;
  if n > 0 then
    raise exception
      'MIGRATION 023 RECUSADA: % comentario(s) sem externo_id. '
      'Um comentario sem ID nativo nao tem identidade de ocorrencia, e '
      'UNKNOWN NAO PODE VIRAR DUPLICATA AUTOMATICA. Decida caso a caso '
      'ANTES de aplicar — esta migration nao inventa identidade.', n;
  end if;
end $$;

alter table public.comentario
  alter column externo_id set not null;

-- A trava velha sai. Ela nao era «uma trava a mais»: era a que colapsava duas
-- pessoas numa so.
alter table public.comentario
  drop constraint if exists comentario_conteudo_id_hash_conteudo_key;

alter table public.comentario
  add constraint comentario_conteudo_id_externo_id_key
  unique (conteudo_id, externo_id);

comment on column public.comentario.externo_id is
  'ID NATIVO da ocorrencia na plataforma (YouTube COMMENT_ID, Mastodon/Bluesky '
  'uri, Telegram post_id). E A IDENTIDADE. `social_envelope.dedupe()` ja funde '
  'por PLATFORM + NATIVE_ID desde antes desta migration.';

comment on column public.comentario.hash_conteudo is
  'Hash do TEXTO do comentario, e nada mais. Serve para detectar EDICAO do '
  'mesmo comentario; NAO e identidade. Meter o ID nativo aqui dentro para '
  'escapar de uma constraint mudaria o significado da coluna pela porta dos '
  'fundos: dois «Grazie!» iguais passariam a ter hashes diferentes. '
  'COMMENT_ID NAO E COMMENT_TEXT.';

commit;
