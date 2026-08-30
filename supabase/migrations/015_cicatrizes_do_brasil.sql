-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 015
-- AS CICATRIZES DO BRASIL VIRAM CAMPO E TRAVA
--
-- Não copia a arquitetura brasileira. Reusa as LEIS que lá já foram pagas,
-- e as põe onde o Brasil descobriu que elas precisam estar: no CAMPO que
-- decide a saída, não na prosa.
--
-- A cicatriz que governa esta migration, textual:
--
--     « A regra existe. Ela não foi aplicada ao campo `praca` do
--       documento — e é esse campo que decide a praça dos padrões
--       publicados. »
--
-- Lá, `praca` era argumento de linha de comando por FONTE, e carimbava a
-- região do canal em comentário de espectador de qualquer lugar. Quarenta
-- e quatro pessoas "discutindo nematoide de café" numa praça com 7.868 ha
-- de café — contra 1,1 milhão de hectares na região que o sistema chamava
-- de outra coisa.
--
-- ⚠️ O NÚMERO 014 ESTÁ RESERVADO e fica vago de propósito: é o
-- `010_catalogo_publico_fabricante.sql` da branch paralela, que só ganha
-- número quando entrar. Preencher o vão com outra coisa quebraria a ordem
-- que a rodada anterior provou. A ordem canônica é:
--   001–007 · 009 · 010–012 · 013 · 014 catálogo · 015 · 008 por último.
--
-- NÃO EXECUTADA em Supabase. Executada e conferida num PostgreSQL 16
-- local e descartável, com as regressões verdes.
-- ═══════════════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════════════
-- 1 · LOCALIZAÇÃO — como se soube, não só onde
--
-- As duas colunas já existiam desde a 003. O que faltava era a terceira
-- pergunta, e é ela que o Brasil pagou para aprender: COMO se soube?
--
--   ESCRITO   o texto afirma o lugar do fato
--   CITADO    o nome do lugar aparece no meio — o balde mais fraco, e lá
--             ele é filtro de leitura, nunca fonte nova
--   DA_FONTE  veio do cadastro da fonte  ⛔ PROIBIDO sustentar fact
--   DEDUZIDO  a inteligência inferiu     ⛔ PROIBIDO sustentar fact
--
-- No Brasil `deduzido` era permitido com aviso escrito. Aqui não é: a 001
-- já diz que geografia é "lugar declarado, NUNCA inferido". A trava abaixo
-- torna a lei da 001 impossível de violar por este caminho.
-- ═══════════════════════════════════════════════════════════════════════
alter table public.conteudo
  add column if not exists fact_geografia_origem text
    check (fact_geografia_origem in ('ESCRITO','CITADO','DA_FONTE','DEDUZIDO','NAO_SEI')),
  add column if not exists fact_geografia_evidencia text;

-- Um lugar do fato sem dizer como se soube é o defeito do Brasil de volta.
alter table public.conteudo
  add constraint local_do_fato_diz_como_se_soube
  check (fact_geografia_id is null
         or (fact_geografia_origem is not null and fact_geografia_evidencia is not null));

-- A trava que torna a `praca` impossível: a localização da FONTE não pode
-- sustentar a localização do FATO. Nem por dedução.
alter table public.conteudo
  add constraint local_da_fonte_nao_sustenta_local_do_fato
  check (fact_geografia_id is null
         or fact_geografia_origem in ('ESCRITO','CITADO'));

comment on column public.conteudo.fact_geografia_origem is
  'COMO se soube o lugar do fato. DA_FONTE e DEDUZIDO existem no vocabulário para '
  'poderem ser DITOS, e são recusados como sustentação — LOCAL_DA_FONTE != LOCAL_DO_FATO.';
comment on column public.conteudo.fact_geografia_evidencia is
  'O trecho literal que sustenta o lugar. Sem ele o lugar do fato não entra.';


-- ── PRECISÃO DA LOCALIZAÇÃO — derivada, nunca gravada ─────────────────
-- Mesma lei do frescor: o que dá para calcular não vira coluna.
create or replace function public.precisao_da_geografia(g bigint)
returns text language sql stable as $$
  select case
    when g is null then 'NOT_KNOWN'
    else coalesce(
      (select case when x.provincia is not null then 'PROVINCIA'
                   when x.regiao    is not null then 'REGIAO'
                   else 'PAIS' end
         from public.geografia x where x.id = g), 'NOT_KNOWN')
  end;
$$;

comment on function public.precisao_da_geografia is
  'PAIS / REGIAO / PROVINCIA / NOT_KNOWN. País conhecido e região desconhecida é PAIS — '
  'nunca o país inteiro fazendo as vezes de uma região.';


-- ── A VISTA QUE O RESTO DO SISTEMA DEVE LER ───────────────────────────
create or replace view public.v_conteudo_localizacao with (security_invoker = on) as
select c.id as conteudo_id,
       gs.pais as source_country,
       coalesce(gs.provincia, gs.regiao, 'PAÍS') as source_place,
       gf.pais as fact_country,
       coalesce(gf.provincia, gf.regiao, 'PAÍS') as fact_place,
       c.fact_geografia_origem,
       c.fact_geografia_evidencia,
       public.precisao_da_geografia(c.fact_geografia_id) as fact_precision,
       (c.fact_geografia_id is null) as fact_location_desconhecido,
       (gs.pais is distinct from gf.pais) as fonte_e_fato_em_paises_diferentes
  from public.conteudo c
  left join public.geografia gs on gs.id = c.source_geografia_id
  left join public.geografia gf on gf.id = c.fact_geografia_id;

comment on view public.v_conteudo_localizacao is
  'As duas geografias lado a lado, com a precisão derivada e a marca de quando elas '
  'discordam de país. Um pesquisador de Foggia pode falar de ocorrência na Toscana: '
  'as duas linhas são verdadeiras e nenhuma vira a outra.';


-- ═══════════════════════════════════════════════════════════════════════
-- 2 · RELEVÂNCIA — ela mora no CONTEÚDO, não na fonte
--
-- `conteudo_crop_issue.relacao` já separava cinco forças de evidência
-- desde a 004, com COOCORRENCIA_TEXTUAL como a mais fraca e `evidencia`
-- NOT NULL. O que faltava é o outro eixo: que TIPO de sinal é este para
-- um caso.
--
-- As cicatrizes italianas que este eixo preserva:
--   RIGHT_CLASS + WRONG_CROP   != CASE_SIGNAL
--   RIGHT_TIME  + WRONG_ISSUE  != CASE_SIGNAL
--   RIGHT_TOPIC + WRONG_YEAR   != CASE_SIGNAL
--
-- E a brasileira, que é a mais barata de esquecer: contagem alta com régua
-- limpa continua NÃO distinguindo sentido. `Leiteiro` é gado, `Cupim` é o
-- meme, `Murcha` é seca, `Tiririca` é grama de jardim, `Caruru` é comida.
-- ═══════════════════════════════════════════════════════════════════════
alter table public.conteudo_crop_issue
  add column if not exists sinal text
    check (sinal in ('EXACT_SIGNAL','NEIGHBOURING_SIGNAL','CONTEXT_ONLY',
                     'RETROSPECTIVE','UNRELATED','NAO_SEI'));

comment on column public.conteudo_crop_issue.sinal is
  'Que TIPO de sinal isto é. Eixo independente de `relacao`: uma OCORRENCIA_DECLARADA '
  'da cultura errada continua sendo ocorrência declarada, e não é sinal do caso.';

-- Sem score. A relevância ao caso é DERIVADA na pergunta, com o motivo escrito.
create or replace function public.f_relevancia_ao_caso(
  p_conteudo_crop_issue bigint,
  p_crop text, p_issue text, p_pais pais,
  p_janela_inicio date default null, p_janela_fim date default null
) returns table (relevancia text, porque text) language sql stable as $$
  select case
    when cc.relacao = 'COOCORRENCIA_TEXTUAL' then 'CONTEXT_ONLY'
    when c.codigo is distinct from p_crop     then 'UNRELATED'
    when i.codigo is distinct from p_issue    then 'UNRELATED'
    when gf.pais is not null and gf.pais <> p_pais then 'UNRELATED'
    when gf.pais is null                      then 'CONTEXT_ONLY'
    when p_janela_inicio is not null and ct.publicado_em is not null
         and ct.publicado_em::date < p_janela_inicio then 'RETROSPECTIVE'
    when p_janela_fim is not null and ct.publicado_em is not null
         and ct.publicado_em::date > p_janela_fim then 'UNRELATED'
    when cc.relacao in ('ESPECTRO_DE_PRODUTO') then 'CONTEXT_ONLY'
    else 'EXACT_SIGNAL'
  end,
  case
    when cc.relacao = 'COOCORRENCIA_TEXTUAL'
      then 'só apareceram juntos no texto — coocorrência não é ocorrência'
    when c.codigo is distinct from p_crop
      then 'cultura errada: ' || coalesce(c.codigo,'NAO_SEI') || ' != ' || p_crop
    when i.codigo is distinct from p_issue
      then 'problema errado: ' || coalesce(i.codigo,'NAO_SEI') || ' != ' || p_issue
    when gf.pais is not null and gf.pais <> p_pais
      then 'o fato é de outro país: ' || gf.pais::text || ' != ' || p_pais::text
    when gf.pais is null
      then 'sem lugar do fato sustentado — serve de contexto, não de sinal do caso'
    when p_janela_inicio is not null and ct.publicado_em is not null
         and ct.publicado_em::date < p_janela_inicio
      then 'publicado antes da janela do caso: ' || ct.publicado_em::date::text
    when p_janela_fim is not null and ct.publicado_em is not null
         and ct.publicado_em::date > p_janela_fim
      then 'publicado depois da janela do caso: ' || ct.publicado_em::date::text
    when cc.relacao = 'ESPECTRO_DE_PRODUTO'
      then 'lista de rótulo é espectro de produto, não ocorrência observada'
    else 'cultura, problema, país e janela conferem, com evidência escrita'
  end
  from public.conteudo_crop_issue cc
  join public.conteudo ct  on ct.id = cc.conteudo_id
  join public.crop_issue ci on ci.id = cc.crop_issue_id
  join public.crop  c on c.id = ci.crop_id
  join public.issue i on i.id = ci.issue_id
  left join public.geografia gf on gf.id = ct.fact_geografia_id
 where cc.id = p_conteudo_crop_issue;
$$;

comment on function public.f_relevancia_ao_caso is
  'EXACT_SIGNAL / NEIGHBOURING_SIGNAL / CONTEXT_ONLY / RETROSPECTIVE / UNRELATED, com o '
  'MOTIVO escrito. Não é score: é a resposta auditável a "por que este conteúdo entrou?".';


-- ═══════════════════════════════════════════════════════════════════════
-- 3 · PAID_RESULT != PRESERVED_RESULT
--
-- O defeito medido na Itália: o ator executou, o item voltou, e o RAW
-- sumiu. Não existe constraint possível — uma rodada legitimamente tem
-- itens antes do upload terminar. O que existe é a PERGUNTA, e ela tem
-- de ser fácil de fazer.
-- ═══════════════════════════════════════════════════════════════════════
create or replace function public.f_runs_pagos_sem_bruto(p_pais pais default null)
returns table (
  run_id text, platform text, actor text, source_country pais,
  status run_status, item_count_raw integer, cost_usd numeric,
  cost_method text, raw_assets integer, veredito text
) language sql stable as $$
  select r.run_id, r.platform, r.actor, r.source_country, r.status,
         r.item_count_raw, r.cost_usd, r.cost_method,
         count(a.id)::integer,
         case
           when count(a.id) > 0 then 'PRESERVADO'
           when coalesce(r.item_count_raw,0) = 0 then 'SEM_ITEM_NADA_A_PRESERVAR'
           when r.status = 'rodando' then 'EM_CURSO'
           else 'PAGO_E_NAO_PRESERVADO'
         end
    from public.collection_run r
    left join public.raw_asset a on a.run_id = r.run_id
   where (p_pais is null or r.source_country = p_pais)
   group by r.run_id, r.platform, r.actor, r.source_country, r.status,
            r.item_count_raw, r.cost_usd, r.cost_method;
$$;

comment on function public.f_runs_pagos_sem_bruto is
  'PAID_RESULT != PRESERVED_RESULT. Ator executou + item voltou + zero raw_asset = '
  'resultado NÃO preservado, e o nome disso é PAGO_E_NAO_PRESERVADO — nunca silêncio.';


-- ═══════════════════════════════════════════════════════════════════════
-- 4 · NOT_MEASURED != ABSENT
--
-- A cicatriz mais cara do vocabulário brasileiro: a primeira versão chamou
-- a recusa do plano de "o perfil não declara lugar", e 299 fichas foram
-- contadas como ausência quando ninguém chegou a perguntar.
-- ═══════════════════════════════════════════════════════════════════════
create table if not exists public.tentativa_de_coleta (
  id            bigserial primary key,
  run_id        text references public.collection_run(run_id) on delete restrict,
  alvo          text not null,              -- o que se tentou obter
  estado        text not null check (estado in (
                  'RESPONDEU_COM_EVIDENCIA',   -- o mundo respondeu, e com evidência
                  'RESPONDEU_SEM_O_CAMPO',     -- o mundo respondeu "não tenho"
                  'NAO_RETORNOU',              -- não voltou item
                  'ACCESS_FAILURE',            -- falha técnica de acesso
                  'LOGIN_WALL',                -- a plataforma exigiu conta
                  'THROTTLED',                 -- limite de taxa
                  'NOT_FOUND',                 -- a fonte respondeu 404
                  'PARSER_FAILURE',            -- chegou e não soubemos ler
                  'SEM_CHECKPOINT_NAO_GASTEI', -- a NOSSA trava barrou, nada gastou
                  'NAO_TESTADO')),             -- ninguém perguntou
  motivo        text not null,
  observado_em  timestamptz not null,
  rule_version  text not null,
  CONSTRAINT tentativa_sem_evidencia_nao_e_ausencia CHECK (
    estado <> 'RESPONDEU_SEM_O_CAMPO' or motivo is not null)
);

comment on table public.tentativa_de_coleta is
  'Separa o mundo, a instalação e nós. RESPONDEU_SEM_O_CAMPO é o mundo dizendo "não '
  'tenho"; LOGIN_WALL e THROTTLED são a instalação recusando; NAO_TESTADO é ninguém ter '
  'perguntado. No Brasil os três viraram um só e 299 fichas foram contadas como ausência.';

alter table public.tentativa_de_coleta enable row level security;
create index if not exists tentativa_por_run on public.tentativa_de_coleta (run_id, estado);
