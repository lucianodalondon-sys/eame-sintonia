-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 020
-- OS READ MODELS DO CONCORRENTE — e o que cada um SE RECUSA a responder
--
-- Uma view é onde o rigor costuma vazar: a tabela guarda o estado, e a view
-- soma tudo e devolve um número limpo que não carrega mais a ressalva. Aqui
-- cada view devolve o estado JUNTO com o número, na mesma linha, para que
-- ninguém precise ir buscar a nota de rodapé.
--
-- NÃO EXECUTADA em Supabase. PostgreSQL 16 local e descartável.
-- ═══════════════════════════════════════════════════════════════════════


-- ─────────────────────────────────────────────────────────────────────
-- 1 · A TIMELINE — eventos de um concorrente em ordem de data DO FATO
--
-- Ordenada por effective_date, e não por observed_at: o que interessa é
-- quando a fonte diz que ocorreu. Quem não tem data do fato aparece com
-- effective_date nulo e NÃO é empurrado para a data da observação.
-- ─────────────────────────────────────────────────────────────────────
create or replace view public.v_competidor_timeline as
select
  o.nome_canonico            as competidor,
  e.pais,
  e.camada,
  e.event_type,
  e.effective_date,
  e.observed_at,
  e.brand,
  e.registration_id_texto,
  e.confidence_state,
  e.fonte,
  e.source_url,
  e.evidencia,
  case when e.effective_date is null
       then 'DATA_DO_FATO_DESCONHECIDA'
       else 'DATADO_PELA_FONTE' end as estado_da_data
from public.evento_concorrente e
join public.organizacao o on o.id = e.competidor_id
order by o.nome_canonico, e.effective_date nulls last, e.event_type;

comment on view public.v_competidor_timeline is
  'Eventos públicos datados, em ordem. NÃO é uma narrativa: dois eventos '
  'seguidos não afirmam que o primeiro causou o segundo.';


-- ─────────────────────────────────────────────────────────────────────
-- 2 · A COBERTURA POR CAMADA — a view que mostra o BURACO
--
-- Esta é a view mais importante do conjunto, e é a única que existe para
-- expor uma ausência. As cinco camadas da cadeia aparecem SEMPRE, mesmo
-- as que têm zero linhas, porque uma camada que some da listagem é
-- indistinguível de uma camada que nunca foi tentada.
-- ─────────────────────────────────────────────────────────────────────
create or replace view public.v_competidor_cobertura_camada as
with camadas(camada) as (
  values ('IP'),('REGULATORY'),('PRODUCT_CATALOG'),('META'),('CREATOR')
), comp as (
  select distinct o.id, o.nome_canonico
  from public.evento_concorrente e join public.organizacao o on o.id = e.competidor_id
)
select
  comp.nome_canonico as competidor,
  camadas.camada,
  count(e.id) as eventos,
  case when count(e.id) = 0
       then 'NOT_AVAILABLE — não coletado nesta rodada. NÃO significa que o '
            'concorrente não tenha atividade nesta camada.'
       else 'COLETADO' end as estado_da_camada
from comp
cross join camadas
left join public.evento_concorrente e
       on e.competidor_id = comp.id and e.camada = camadas.camada
group by comp.nome_canonico, camadas.camada
order by comp.nome_canonico, camadas.camada;

comment on view public.v_competidor_cobertura_camada is
  'ZERO AQUI É NOT_COLLECTED, NUNCA NOT_HAPPENING. As cinco camadas sempre '
  'aparecem, inclusive as vazias — camada que some da lista é indistinguível '
  'de camada que nunca foi tentada.';


-- ─────────────────────────────────────────────────────────────────────
-- 3 · A ANTECEDÊNCIA — só o que a trava do banco deixou passar
--
-- `lead_days` só existe sobre link PROVED (constraint da 019). Esta view
-- não relaxa nada: separa defensável de não defensável e publica os dois.
-- ─────────────────────────────────────────────────────────────────────
create or replace view public.v_competidor_antecedencia as
select
  o.nome_canonico as competidor,
  a.brand,
  a.effective_date  as data_da_marca,
  b.effective_date  as data_do_registro,
  b.registration_id_texto as registro,
  l.lead_days,
  l.lead_days_defensavel,
  case
    when l.lead_days is null then 'SEM_MEDIDA'
    when l.lead_days > 0 and l.lead_days_defensavel then 'MARCA_ANTES — DEFENSAVEL'
    when l.lead_days > 0 then 'MARCA_ANTES — NAO_DEFENSAVEL (provável redepósito)'
    when l.lead_days < 0 then 'REGISTRO_ANTES — hipótese REFUTADA neste par'
    else 'MESMO_DIA'
  end as leitura,
  l.evidencia
from public.evento_concorrente_link l
join public.evento_concorrente a on a.id = l.evento_a_id
join public.evento_concorrente b on b.id = l.evento_b_id
join public.organizacao o on o.id = a.competidor_id
where l.estado = 'PROVED'
order by l.lead_days_defensavel desc, l.lead_days;

comment on view public.v_competidor_antecedencia is
  'Antecedência entre marca e registro. Pares com lead negativo REFUTAM a '
  'hipótese e aparecem assim, escrito — não são omitidos do resultado.';


-- ─────────────────────────────────────────────────────────────────────
-- 4 · O QUE NÃO LIGOU — a view da recusa
--
-- Um piloto que só publica o que casou esconde sua própria taxa de acerto.
-- Esta view existe para que a recusa seja tão visível quanto o link.
-- ─────────────────────────────────────────────────────────────────────
create or replace view public.v_competidor_links_recusados as
select
  o.nome_canonico as competidor_da_marca,
  a.brand,
  b.registration_id_texto as registro_candidato,
  l.estado,
  l.evidencia
from public.evento_concorrente_link l
join public.evento_concorrente a on a.id = l.evento_a_id
join public.evento_concorrente b on b.id = l.evento_b_id
join public.organizacao o on o.id = a.competidor_id
where l.estado <> 'PROVED'
order by l.estado, o.nome_canonico;

comment on view public.v_competidor_links_recusados is
  'Os pares que o crosswalk RECUSOU. Publicar a recusa é o que impede a taxa '
  'de acerto de ser lida como 100%.';


-- ─────────────────────────────────────────────────────────────────────
-- 5 · O SINAL DE MARCA, separado por força
--
-- A classe 5 de Nice cobre farmacêutico e veterinário junto com pesticida.
-- Somar as duas forças numa contagem só foi o erro que esta rodada cometeu
-- e corrigiu; a view não deixa ele voltar.
-- ─────────────────────────────────────────────────────────────────────
create or replace view public.v_competidor_marcas_recentes as
select
  o.nome_canonico as competidor,
  e.pais as escritorio,
  e.brand,
  e.event_type,
  e.effective_date as data_do_deposito,
  e.confidence_state,
  case e.confidence_state
    when 'OBSERVED_STRONG_AGRO_SIGNAL' then 'classe 1 declarada — sinal agro'
    when 'OBSERVED_AMBIGUOUS_CLASS'    then 'só classe 5 — AMBÍGUO, a classe 5 '
                                            'também é a do remédio'
    else 'sem classe declarada' end as leitura_da_classe,
  e.source_url
from public.evento_concorrente e
join public.organizacao o on o.id = e.competidor_id
where e.camada = 'IP'
order by e.effective_date desc nulls last;

comment on view public.v_competidor_marcas_recentes is
  'Depósitos de marca, do mais recente ao mais antigo. Um depósito recente é '
  'ATTENTION ITEM, nunca "o concorrente vai lançar o produto X".';
