-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 007
-- VIEWS: as perguntas que hoje exigem carregar JSON inteiro na memória.
-- NÃO EXECUTADA.
-- ═══════════════════════════════════════════════════════════════════════

-- Contador do acervo. Espelha v_acervo do Brasil.
create or replace view public.v_acervo with (security_invoker = on) as
select
  (select count(*) from public.origem)                    as origens,
  (select count(*) from public.canal)                     as canais,
  (select count(*) from public.conteudo)                  as conteudos,
  (select count(distinct obra_id) from public.conteudo
     where obra_id is not null)                           as obras_distintas,
  (select count(*) from public.transcricao)               as transcricoes,
  (select count(distinct autor_hash) from public.comentario
     where autor_hash is not null)                        as pessoas_distintas,
  (select max(coletado_em) from public.conteudo)          as ultima_captura;

-- INDEPENDÊNCIA: quantas evidências REALMENTE independentes existem por par.
-- Conta obra distinta, não linha de conteúdo.
-- ⚠️ REPLAY-SAFE, desde a integração de 2026-08-30.
--
-- Estas duas views são REDEFINIDAS depois: a 009 acrescenta fact_country na
-- frente, e a 018 as refaz sobre conteudo_lugar. `create or replace view`
-- não consegue reescrever uma view cujas colunas mudaram — ele recusa com
-- "cannot drop columns from view".
--
-- Isso não é teórico: a produção parou aqui. O caminho de produção reaplica
-- a cadeia inteira desde a 001, e num banco que já tinha a 009 aplicada a
-- 007 batia na forma NOVA e falhava. O laço tratava "already exists" como
-- SKIP, e este erro não é esse — então a cadeia parava na sétima migration,
-- antes de qualquer coisa nova ser aplicada.
--
-- O `drop` explícito faz cada migration ser dona INTEIRA do objeto no ponto
-- dela da cadeia: a 007 repõe a forma da 007, a 009 repõe a da 009, a 018
-- repõe a da 018, e o estado final é o da última. Sem ele, uma migration
-- antiga só é aplicável uma vez na vida.

drop view if exists public.v_independencia_por_par;
create view public.v_independencia_por_par with (security_invoker = on) as
select ci.id as crop_issue_id, c.codigo as crop, i.codigo as issue,
       count(*)                                   as conteudos,
       count(distinct coalesce(ct.obra_id, ct.id)) as obras_independentes,
       count(distinct cn.origem_id)                as origens_distintas
from public.crop_issue ci
join public.crop  c on c.id = ci.crop_id
join public.issue i on i.id = ci.issue_id
join public.conteudo_crop_issue cci on cci.crop_issue_id = ci.id
join public.conteudo ct on ct.id = cci.conteudo_id
join public.canal    cn on cn.id = ct.canal_id
where cci.relacao in ('OCORRENCIA_DECLARADA','ENSAIO_OU_ESTUDO','RECOMENDACAO_TECNICA')
group by ci.id, c.codigo, i.codigo;
comment on view public.v_independencia_por_par is
  'Exclui COOCORRENCIA_TEXTUAL e ESPECTRO_DE_PRODUTO: eles não sustentam '
  'a afirmação de que o problema ocorre na cultura.';

-- A MESMA PERGUNTA POR PORTA. É o seletor-por-porta do Brasil virando view:
-- se a distribuição muda conforme o tipo de conteúdo, a cultura não pode
-- ser eleita por uma porta só.
drop view if exists public.v_par_por_porta;
create view public.v_par_por_porta with (security_invoker = on) as
select c.codigo as crop, i.codigo as issue, ct.tipo as porta,
       count(distinct coalesce(ct.obra_id, ct.id)) as obras
from public.conteudo_crop_issue cci
join public.crop_issue ci on ci.id = cci.crop_issue_id
join public.crop  c on c.id = ci.crop_id
join public.issue i on i.id = ci.issue_id
join public.conteudo ct on ct.id = cci.conteudo_id
group by c.codigo, i.codigo, ct.tipo;

-- SAÚDE DA COLETA: execução que se apresentou como sucesso e veio vazia.
create or replace view public.v_execucao_degradada with (security_invoker = on) as
select run_id, actor, status, item_count_raw, cost_usd, error, started_at
from public.collection_run
where status in ('vazia','parcial')
   or (status = 'concluida' and coalesce(item_count_raw,0) = 0);
comment on view public.v_execucao_degradada is
  'SUCCEEDED DA PLATAFORMA != EXECUÇÃO BEM-SUCEDIDA.';

-- BRUTO ÓRFÃO e conteúdo sem bruto — os dois lados da cadeia quebrada.
create or replace view public.v_cadeia_quebrada with (security_invoker = on) as
select 'raw_sem_run' as problema, ra.id::text as ref
  from public.raw_asset ra
  left join public.collection_run r on r.run_id = ra.run_id
 where r.run_id is null
union all
select 'conteudo_sem_raw', ct.id::text
  from public.conteudo ct
 where ct.raw_asset_id is null;
