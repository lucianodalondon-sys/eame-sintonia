-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 018
-- O LUGAR DO FATO GANHA DONO — e o dono antigo é APOSENTADO, não duplicado
--
-- A 017 mediu cinco lacunas e não consertou quatro delas, porque reabrir a
-- modelagem de localização na véspera do portão de importação teria sido
-- trabalho fora de hora. A hora chegou. Esta migration fecha:
--
--   BR-26  BASE != OPERATING != INFLUENCE != FACT
--   BR-30  um conteúdo tem 0..N lugares de fato, não 0..1
--   BR-31  a escada de precisão parava em PROVINCIA
--   BR-32  TERRITORIAL_LIST != FACT_LIST no eixo da geografia
--   BR-34  PUBLISHED_AT != FACT_TIME  (falta o TEMPO DO FATO como campo)
--
-- E incorpora duas leis que a Itália provou em texto real depois da 017:
--
--   SOURCE_GEOGRAPHY != ADMIN_GEOGRAPHY   "l'Ovest" é um lugar e não é
--                                         uma unidade administrativa
--   NOT_IN_GAZETTEER != NOT_A_PLACE != REJECTED_BY_LAW
--
-- ⚠️ ESTA MIGRATION APOSENTA `conteudo.fact_geografia_id`.
--
-- Não é escolha estética. `fact_geografia_id` é UMA coluna: ela expressa
-- 0..1, e o contrato pede 0..N. Deixá-la viva ao lado da tabela nova
-- criaria DOIS DONOS DA MESMA LEI — o defeito que a 016 já cometeu uma vez,
-- criando um índice único que duplicava a chave natural da 003. Naquela vez
-- o banco recusou. Aqui ninguém recusaria: as duas estruturas conviveriam
-- em silêncio, e um dia responderiam coisas diferentes.
--
-- Por isso a coluna é MIGRADA e removida, junto com as duas travas da 015
-- que a guardavam. As travas não morrem: renascem sobre a tabela nova, onde
-- agora valem para CADA lugar, e não só para o único que cabia.
--
-- NÃO EXECUTADA em Supabase. PostgreSQL 16 local e descartável.
-- ═══════════════════════════════════════════════════════════════════════


-- ═══════════════════════════════════════════════════════════════════════
-- 1 · A ESCADA DE PRECISÃO, E O LUGAR QUE NÃO É ADMINISTRATIVO
--
-- BR-31: a escada parava em PROVINCIA. Para calendário agronômico bastava;
-- para ocorrência de campo não basta — "campioni positivi da Grosseto" e
-- "focolaio nel comune di X" não têm a mesma precisão, e somá-las no mesmo
-- mapa produz um número que não existe.
--
-- E a lei que a Itália trouxe: uma fonte diz "l'Ovest", "areale nord",
-- "zona cerealicola". São LUGARES, e não são unidades administrativas.
-- Forçá-los para REGIAO/PROVINCIA seria geocodificar por conveniência até
-- a zona vaga virar província — que é inventar precisão que ninguém mediu.
-- ═══════════════════════════════════════════════════════════════════════

alter table public.geografia
  add column if not exists municipio   text,
  add column if not exists localidade  text,
  add column if not exists lat         numeric,
  add column if not exists lon         numeric,
  -- O nome exato que a FONTE usou, quando ele não é administrativo.
  add column if not exists nome_da_fonte text,
  add column if not exists especie     text not null default 'ADMIN'
    check (especie in ('ADMIN', 'DEFINIDA_PELA_FONTE', 'ZONA_AGRONOMICA', 'OUTRA'));

comment on column public.geografia.especie is
  'SOURCE_GEOGRAPHY != ADMIN_GEOGRAPHY. ADMIN é divisão oficial. '
  'DEFINIDA_PELA_FONTE é o recorte que a fonte usou e que não corresponde a nenhuma '
  'divisão — "l''Ovest", "areale nord". ZONA_AGRONOMICA é recorte produtivo. Nenhuma '
  'das três é convertida para a escada administrativa: converter seria inventar.';

comment on column public.geografia.nome_da_fonte is
  'o recorte COMO A FONTE ESCREVEU. Existe para que uma zona vaga possa ser guardada '
  'inteira em vez de ser aproximada para a província mais parecida.';

-- Uma geografia não-administrativa não pode fingir divisão administrativa.
alter table public.geografia
  drop constraint if exists zona_da_fonte_nao_e_divisao_administrativa;
alter table public.geografia
  add constraint zona_da_fonte_nao_e_divisao_administrativa
  check (especie = 'ADMIN'
         or (regiao is null and provincia is null and municipio is null
             and localidade is null and nome_da_fonte is not null));

-- Uma coordenada precisa das duas metades. Meia coordenada é um número solto.
alter table public.geografia
  drop constraint if exists coordenada_vem_inteira;
alter table public.geografia
  add constraint coordenada_vem_inteira
  check (num_nonnulls(lat, lon) <> 1);

-- A chave natural tem de crescer junto com a escada. Sem isto, Toscana e
-- Toscana/Grosseto colidiriam na antiga (pais, regiao, provincia).
alter table public.geografia
  drop constraint if exists geografia_pais_regiao_provincia_key;
alter table public.geografia
  drop constraint if exists geografia_e_unica_por_recorte;
alter table public.geografia
  add constraint geografia_e_unica_por_recorte
  unique nulls not distinct
  (pais, especie, regiao, provincia, municipio, localidade, nome_da_fonte, lat, lon);

-- A escada completa. Cada degrau nasce da LINHA, nunca de suposição — e o
-- degrau não-administrativo não entra na escada, ele tem nome próprio.
create or replace function public.precisao_da_geografia(g bigint)
returns text language sql stable as $$
  select case
    when g is null then 'NOT_KNOWN'
    else coalesce(
      (select case
         when x.especie = 'DEFINIDA_PELA_FONTE' then 'ZONA_DEFINIDA_PELA_FONTE'
         when x.especie = 'ZONA_AGRONOMICA'     then 'ZONA_AGRONOMICA'
         when x.especie = 'OUTRA'               then 'OUTRA_GEOGRAFIA'
         when x.lat is not null                 then 'COORDENADA'
         when x.localidade is not null          then 'LOCALIDADE'
         when x.municipio  is not null          then 'MUNICIPIO'
         when x.provincia  is not null          then 'PROVINCIA'
         when x.regiao     is not null          then 'REGIAO'
         else 'PAIS' end
         from public.geografia x where x.id = g), 'NOT_KNOWN')
  end;
$$;

comment on function public.precisao_da_geografia is
  'A escada: PAIS < REGIAO < PROVINCIA < MUNICIPIO < LOCALIDADE < COORDENADA. Fora dela, '
  'e de propósito: ZONA_DEFINIDA_PELA_FONTE, ZONA_AGRONOMICA e OUTRA_GEOGRAFIA. '
  'SOURCE SAYS REGION != INVENT MUNICIPALITY — mais específico só nasce de evidência '
  'mais específica, e a função deriva da linha, nunca do texto.';

-- Cada país usa a hierarquia que tem. `provincia` na Itália, `provincia` na
-- Espanha, `département` na França — o nome do degrau é do país, o DEGRAU é
-- do contrato. COUNTRY_ISOLATION continua intacta: nada aqui atravessa país.
create or replace function public.escada_de_precisao()
returns table (degrau text, ordem smallint, administrativo boolean) language sql immutable as $$
  values ('PAIS',1::smallint,true), ('REGIAO',2,true), ('PROVINCIA',3,true),
         ('MUNICIPIO',4,true), ('LOCALIDADE',5,true), ('COORDENADA',6,true),
         ('ZONA_DEFINIDA_PELA_FONTE',0,false), ('ZONA_AGRONOMICA',0,false),
         ('OUTRA_GEOGRAFIA',0,false), ('NOT_KNOWN',0,false);
$$;

comment on function public.escada_de_precisao is
  'Os degraus, com ordem. Os não-administrativos têm ordem 0 de propósito: eles não '
  'são "menos precisos que província", são OUTRA COISA, e comparar os dois na mesma '
  'régua é o erro que a função existe para impedir.';


-- ═══════════════════════════════════════════════════════════════════════
-- 2 · AS QUATRO ESPÉCIES DE LUGAR DO SUJEITO — BR-26
--
-- BASE       onde a pessoa ou entidade está estabelecida
-- OPERATING  onde ela atua
-- INFLUENCE  até onde a fala dela alcança
--
-- E FACT, que NÃO mora aqui: o lugar do fato é do CONTEÚDO, não do sujeito.
-- Essa é a razão de serem duas tabelas e não uma. Um pesquisador baseado em
-- Foggia, de instituição que atua nacionalmente, com audiência italiana,
-- relatando um foco em Grosseto, tem quatro lugares verdadeiros ao mesmo
-- tempo — e três deles são dele, e um é do que ele escreveu.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.origem_lugar (
  id            bigserial primary key,
  origem_id     bigint not null references public.origem(id) on delete cascade,
  geografia_id  bigint not null references public.geografia(id),
  papel         text   not null check (papel in ('BASE','OPERATING','INFLUENCE')),
  -- VALUE_PROVENANCE, não ROW_PROVENANCE: cada lugar diz como ELE se soube.
  origem_do_dado text  not null check (origem_do_dado in
                    ('DECLARADO_NO_PERFIL','ESCRITO_NO_TEXTO','FONTE_OFICIAL',
                     'CADASTRO_INTERNO','NAO_SEI')),
  evidencia     text   not null,
  desde         date,
  ate           date,
  rule_version  text   not null,
  UNIQUE (origem_id, geografia_id, papel)
);

comment on table public.origem_lugar is
  'BASE != OPERATING != INFLUENCE. Três perguntas diferentes sobre o mesmo sujeito, '
  'cada uma com sua evidência. FACT não está no vocabulário desta tabela de propósito: '
  'o lugar do fato é do conteúdo, e promover a sede do autor a lugar de ocorrência foi '
  'a cicatriz que abriu esta família inteira.';

comment on column public.origem_lugar.evidencia is
  'obrigatória. Um papel declarado sem o trecho que o sustenta não é auditável por '
  'outra pessoa — e "auditável só por quem escreveu" é o mesmo que não auditável.';


-- ═══════════════════════════════════════════════════════════════════════
-- 3 · OS 0..N LUGARES DE UM CONTEÚDO — BR-30, BR-32
--
-- "campioni positivi provenienti da Grosseto, Siena e Arezzo" são TRÊS
-- localizações do fato, cada uma com sua evidência. Ficar com a primeira
-- inventaria um recorte que a fonte não fez; concatenar as três numa string
-- destruiria a possibilidade de cruzar qualquer uma.
--
-- E a mesma tabela guarda os lugares que NÃO são fato, porque é preciso
-- poder DIZER que eles não são: "atuamos em A, B e C" é uma lista, ela
-- existe no texto, e a única forma de provar que ela não virou ocorrência é
-- tê-la guardada com o papel certo ao lado das que viraram.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.conteudo_lugar (
  id            bigserial primary key,
  conteudo_id   bigint not null references public.conteudo(id) on delete cascade,

  -- NOT_IN_GAZETTEER != NOT_A_PLACE != REJECTED_BY_LAW.
  -- O nome COMO A FONTE ESCREVEU é obrigatório e vem sempre. A resolução
  -- para uma linha de geografia é opcional: um lugar que a nossa lista
  -- auxiliar não conhece continua existindo no texto, e apagá-lo seria
  -- deixar a nossa lacuna virar lacuna do mundo.
  lugar_texto   text   not null,
  geografia_id  bigint references public.geografia(id),
  estado_do_lugar text not null check (estado_do_lugar in
                    ('RESOLVIDO','NAO_ESTA_NO_GAZETTEER','NAO_E_LUGAR','RECUSADO_POR_LEI')),

  papel         text   not null check (papel in
                    -- o fato
                    ('FACT',
                    -- os que NÃO são o fato, e precisam poder ser ditos
                     'EVENT','OPERATING_MENCIONADO','AREA_COMERCIAL',
                     'LISTA_TERRITORIAL','MENCAO_APENAS','NAO_SEI')),

  -- OCCURRENCE != INCIDENCE. As espécies não se somam entre si.
  tipo_de_evidencia text check (tipo_de_evidencia in
                    ('FIELD_OBSERVATION','DIAGNOSTIC_SAMPLE','OFFICIAL_OCCURRENCE',
                     'CONFIRMED_FOCUS','REGIONAL_STATEMENT','INCIDENCE_MEASUREMENT',
                     'OTHER')),

  -- VALUE_PROVENANCE: de onde veio ESTE lugar, e não de onde veio a linha.
  origem_do_dado text  not null check (origem_do_dado in
                    ('ESCRITO','CITADO','DA_FONTE','DEDUZIDO','LISTA_TERRITORIAL','NAO_SEI')),
  evidencia     text,
  ancora        text,
  rule_version  text   not null,

  UNIQUE (conteudo_id, lugar_texto, papel)
);

-- ── AS TRAVAS DA 015, RENASCIDAS ONDE AGORA VALEM PARA CADA LUGAR ─────

-- Um lugar do fato sem dizer COMO se soube é o defeito do Brasil de volta.
alter table public.conteudo_lugar
  drop constraint if exists lugar_do_fato_diz_como_se_soube;
alter table public.conteudo_lugar
  add constraint lugar_do_fato_diz_como_se_soube
  check (papel <> 'FACT' or (evidencia is not null and evidencia <> ''));

-- A LISTA BRANCA das origens que sustentam o lugar do fato. Ela é UMA, e
-- de propósito: três leis diferentes desembocam na mesma pergunta, e cada
-- uma delas ganhar a própria trava criaria donos concorrentes da mesma
-- regra — o defeito que a 016 já cometeu com um índice duplicado.
--
--   LOCAL_DA_FONTE   != LOCAL_DO_FATO     (DA_FONTE fora)
--   INFERIDO         != DECLARADO         (DEDUZIDO fora)
--   TERRITORIAL_LIST != FACT_LIST         (LISTA_TERRITORIAL fora)
--
-- Os quatro valores fora da lista existem no vocabulário para poderem ser
-- DITOS. Dizer é permitido; sustentar o fato, não.
--
-- A primeira versão desta migration tinha DUAS travas aqui: esta e uma só
-- para a lista territorial. A mutação do red team mostrou que a segunda
-- nunca disparava — a lista já caía nesta. Uma trava que nunca dispara é
-- pior que nenhuma: ela dá a impressão de que a lei tem guarda própria.
alter table public.conteudo_lugar
  drop constraint if exists local_da_fonte_nao_sustenta_lugar_do_fato;
alter table public.conteudo_lugar
  drop constraint if exists lista_territorial_nao_e_lugar_do_fato;
alter table public.conteudo_lugar
  drop constraint if exists so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato;
alter table public.conteudo_lugar
  add constraint so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato
  check (papel <> 'FACT' or origem_do_dado in ('ESCRITO','CITADO'));

-- OCCURRENCE != INCIDENCE: um lugar de fato tem de dizer QUE espécie de
-- evidência o sustenta, porque cinco amostras e um comunicado regional não
-- fazem "seis ocorrências", e nenhum dos dois faz incidência.
alter table public.conteudo_lugar
  drop constraint if exists lugar_do_fato_declara_a_especie_da_evidencia;
alter table public.conteudo_lugar
  add constraint lugar_do_fato_declara_a_especie_da_evidencia
  check (papel <> 'FACT' or tipo_de_evidencia is not null);

-- Uma âncora é obrigatória no fato: é o trecho que liga ACONTECIMENTO a
-- LUGAR. Preposição e proximidade não bastam — "convegno a Bologna" tem as
-- duas e não diz nada sobre onde a doença está.
alter table public.conteudo_lugar
  drop constraint if exists lugar_do_fato_carrega_a_ancora;
alter table public.conteudo_lugar
  add constraint lugar_do_fato_carrega_a_ancora
  check (papel <> 'FACT' or (ancora is not null and ancora <> ''));

-- Um lugar resolvido aponta geografia; um não-resolvido não pode apontar.
alter table public.conteudo_lugar
  drop constraint if exists resolvido_aponta_geografia;
alter table public.conteudo_lugar
  add constraint resolvido_aponta_geografia
  check ((estado_do_lugar = 'RESOLVIDO') = (geografia_id is not null));

comment on table public.conteudo_lugar is
  'Um conteúdo tem 0..N lugares, e só alguns deles são o LUGAR DO FATO. Guardar os '
  'outros com o papel certo é o que permite PROVAR que não viraram ocorrência.';

comment on column public.conteudo_lugar.estado_do_lugar is
  'NOT_IN_GAZETTEER != NOT_A_PLACE != REJECTED_BY_LAW. Três respostas diferentes que '
  'no Brasil saíam idênticas do outro lado — e a primeira esconde falta de cobertura '
  'atrás de um resultado que parece correto.';


-- ═══════════════════════════════════════════════════════════════════════
-- 4 · A MUDANÇA DE DONO — o que estava na coluna passa para a tabela
--
-- Nada se perde e nada fica em dois lugares. Depois deste bloco,
-- `conteudo.fact_geografia_id` não existe mais.
-- ═══════════════════════════════════════════════════════════════════════

insert into public.conteudo_lugar
  (conteudo_id, lugar_texto, geografia_id, estado_do_lugar, papel,
   tipo_de_evidencia, origem_do_dado, evidencia, ancora, rule_version)
select c.id,
       coalesce(g.municipio, g.provincia, g.regiao, g.pais::text),
       c.fact_geografia_id, 'RESOLVIDO', 'FACT',
       -- A coluna antiga não guardava a espécie da evidência. Dizer qual era
       -- seria inventar; OTHER é a resposta honesta para o que não foi medido.
       'OTHER',
       c.fact_geografia_origem,
       c.fact_geografia_evidencia,
       -- Nem âncora. O texto da evidência é o que existe, e ele vai como
       -- âncora declarada para que a trava valha sem fabricar dado.
       'migrado da 015: a evidência escrita era a única âncora guardada',
       coalesce(c.rule_version, 'migrado-018')
  from public.conteudo c
  left join public.geografia g on g.id = c.fact_geografia_id
 where c.fact_geografia_id is not null
on conflict do nothing;

alter table public.conteudo drop constraint if exists local_do_fato_diz_como_se_soube;
alter table public.conteudo drop constraint if exists local_da_fonte_nao_sustenta_local_do_fato;

-- Três views da 009 liam a coluna. Elas caem aqui e renascem na seção 6,
-- sobre o dono novo. A 009 continua sendo quem as CRIOU; a partir daqui é
-- esta migration quem as define, e há um aviso no topo da 009 dizendo isso.
drop view if exists public.v_independencia_por_par;
drop view if exists public.v_par_por_porta;
drop view if exists public.v_cross_market_por_par;
-- E a própria visão de localização, da 015/017: ela lia a coluna, e volta
-- na seção 6 lendo a tabela — com fact_places no plural, que é o ponto.
drop view if exists public.v_conteudo_localizacao;

-- Estas três colunas eram o dono antigo. A partir daqui o dono é a tabela.
alter table public.conteudo drop column if exists fact_geografia_id;
alter table public.conteudo drop column if exists fact_geografia_origem;
alter table public.conteudo drop column if exists fact_geografia_evidencia;


-- ═══════════════════════════════════════════════════════════════════════
-- 5 · O TEMPO DO FATO — BR-34
--
-- A 017 consertou a metade que dava resposta errada: publicado depois da
-- janela deixou de virar UNRELATED. A metade que faltava é esta — o EAME
-- não tinha ONDE guardar "o fato aconteceu na safra 2025" separado de "o
-- texto saiu em 13/02/2026".
--
-- Reusa `resolucao_temporal`, que a 009 já tem. Criar um segundo vocabulário
-- de precisão temporal seria um segundo dono da mesma lei.
-- ═══════════════════════════════════════════════════════════════════════

alter table public.conteudo
  add column if not exists fact_tempo_texto      text,
  add column if not exists fact_tempo_resolucao  resolucao_temporal,
  add column if not exists fact_tempo_inicio     date,
  add column if not exists fact_tempo_fim        date,
  add column if not exists fact_tempo_evidencia  text,
  add column if not exists fact_tempo_origem     text
    check (fact_tempo_origem in ('ESCRITO_NO_TEXTO','AMARRADO_AO_ACONTECIMENTO',
                                 'FONTE_OFICIAL','NAO_SEI'));

-- PUBLISHED_AT != FACT_TIME, escrito como trava e não como comentário.
-- `PUBLICACAO` não está no vocabulário acima: não há como declarar que o
-- tempo do fato veio do carimbo da publicação, porque isso não é permitido.
alter table public.conteudo
  drop constraint if exists tempo_do_fato_diz_como_se_soube;
alter table public.conteudo
  add constraint tempo_do_fato_diz_como_se_soube
  check (fact_tempo_texto is null
         or (fact_tempo_origem is not null and fact_tempo_evidencia is not null
             and fact_tempo_resolucao is not null));

comment on column public.conteudo.fact_tempo_texto is
  'QUANDO o fato aconteceu, como a fonte disse — "stagione 2025", "la settimana '
  'scorsa". PUBLISHED_AT != FACT_TIME: publicado_em nunca preenche este campo, e não '
  'existe valor no vocabulário de origem que permita dizer que preencheu.';

comment on column public.conteudo.fact_tempo_resolucao is
  'A precisão do tempo do fato, no MESMO vocabulário da 009. Uma série histórica '
  '"2011-2025" não é SEASON: é o alcance da medição, não a data do que foi medido.';


-- ═══════════════════════════════════════════════════════════════════════
-- 6 · AS CONSULTAS, REFEITAS SOBRE O DONO NOVO
-- ═══════════════════════════════════════════════════════════════════════

create view public.v_conteudo_localizacao with (security_invoker = on) as
select c.id as conteudo_id,
       gs.pais as source_country,
       coalesce(gs.municipio, gs.provincia, gs.regiao, gs.nome_da_fonte, 'PAÍS')
         as source_place,
       -- 0..N: o país do fato só é afirmável quando TODOS os lugares do fato
       -- concordam. Dois países entre os lugares é informação, não um deles.
       (select case when count(distinct g.pais) = 1 then min(g.pais::text) end
          from public.conteudo_lugar cl
          join public.geografia g on g.id = cl.geografia_id
         where cl.conteudo_id = c.id and cl.papel = 'FACT')::pais as fact_country,
       (select count(*) from public.conteudo_lugar cl
         where cl.conteudo_id = c.id and cl.papel = 'FACT') as fact_locations,
       (select array_agg(cl.lugar_texto order by cl.lugar_texto)
          from public.conteudo_lugar cl
         where cl.conteudo_id = c.id and cl.papel = 'FACT') as fact_places,
       (select array_agg(distinct public.precisao_da_geografia(cl.geografia_id))
          from public.conteudo_lugar cl
         where cl.conteudo_id = c.id and cl.papel = 'FACT') as fact_precisions,
       not exists (select 1 from public.conteudo_lugar cl
                    where cl.conteudo_id = c.id and cl.papel = 'FACT')
         as fact_location_desconhecido,
       -- PLACE_MENTION != FACT_LOCATION, dito em voz alta, por conteúdo.
       exists (select 1 from public.conteudo_lugar cl
                where cl.conteudo_id = c.id and cl.papel = 'FACT'
                  and cl.origem_do_dado = 'CITADO')
         as fact_sustentado_apenas_por_mencao,
       (select count(*) from public.conteudo_lugar cl
         where cl.conteudo_id = c.id and cl.papel <> 'FACT') as lugares_nao_fato,
       (select count(*) from public.conteudo_lugar cl
         where cl.conteudo_id = c.id
           and cl.estado_do_lugar = 'NAO_ESTA_NO_GAZETTEER') as lugares_fora_do_gazetteer
  from public.conteudo c
  left join public.geografia gs on gs.id = c.source_geografia_id;

comment on view public.v_conteudo_localizacao is
  'SOURCE_LOCATION != FACT_LOCATION, e um conteúdo tem 0..N lugares do fato. '
  '`fact_places` é ARRAY porque a fonte pode ter nomeado três, e escolher um deles '
  'seria inventar um recorte que ela não fez.';

-- Um lugar do fato, uma linha, com tudo o que o sustenta ao lado.
create or replace view public.v_lugar_do_fato with (security_invoker = on) as
select cl.id, cl.conteudo_id, ct.content_id, cl.lugar_texto,
       cl.geografia_id, cl.estado_do_lugar,
       public.precisao_da_geografia(cl.geografia_id) as precisao,
       g.especie as especie_da_geografia,
       cl.tipo_de_evidencia, cl.origem_do_dado, cl.evidencia, cl.ancora,
       ct.publicado_em, ct.fact_tempo_texto, ct.fact_tempo_resolucao,
       -- PUBLISHED_AT != FACT_TIME, lado a lado para que a diferença seja vista.
       (ct.fact_tempo_texto is null) as tempo_do_fato_desconhecido
  from public.conteudo_lugar cl
  join public.conteudo ct on ct.id = cl.conteudo_id
  left join public.geografia g on g.id = cl.geografia_id
 where cl.papel = 'FACT';

-- OCCURRENCE != INCIDENCE: conta POR espécie e nunca soma entre espécies.
create or replace function public.f_ocorrencia_nao_e_incidencia(p_conteudo_id bigint)
returns table (tipo_de_evidencia text, quantos bigint) language sql stable as $$
  select cl.tipo_de_evidencia, count(*)
    from public.conteudo_lugar cl
   where cl.conteudo_id = p_conteudo_id and cl.papel = 'FACT'
   group by cl.tipo_de_evidencia
   order by cl.tipo_de_evidencia;
$$;

comment on function public.f_ocorrencia_nao_e_incidencia is
  'POSITIVE_SAMPLE != REGIONAL_INCIDENCE. Devolve a contagem POR espécie de evidência '
  'e nunca um total: cinco amostras de diagnóstico e um comunicado regional não fazem '
  '"seis ocorrências", e nenhum dos dois autoriza dizer incidência. Sem score.';

-- A relevância volta a ler o lugar do fato — agora da tabela, e com 0..N.
create or replace function public.f_relevancia_ao_caso(
  p_conteudo_crop_issue bigint, p_crop text, p_issue text, p_pais pais,
  p_janela_inicio date default null, p_janela_fim date default null)
returns table (relevancia text, porque text) language sql stable as $$
  with lugares as (
    select cl.conteudo_id,
           count(*) as n,
           count(*) filter (where g.pais = p_pais) as no_pais,
           bool_or(cl.origem_do_dado = 'CITADO') as so_mencao
      from public.conteudo_lugar cl
      left join public.geografia g on g.id = cl.geografia_id
     where cl.papel = 'FACT'
     group by cl.conteudo_id
  )
  select case
    when cc.relacao = 'COOCORRENCIA_TEXTUAL' then 'CONTEXT_ONLY'
    when c.codigo is distinct from p_crop     then 'UNRELATED'
    when i.codigo is distinct from p_issue    then 'UNRELATED'
    when coalesce(l.n,0) = 0                  then 'CONTEXT_ONLY'
    -- 0..N: basta UM lugar do fato no país do caso. Exigir que todos fossem
    -- descartaria um documento que relata Toscana e Provence ao mesmo tempo.
    when l.no_pais = 0                        then 'UNRELATED'
    when p_janela_inicio is not null and ct.publicado_em is not null
         and ct.publicado_em::date < p_janela_inicio then 'RETROSPECTIVE'
    when p_janela_fim is not null and ct.publicado_em is not null
         and ct.publicado_em::date > p_janela_fim then 'CONTEXT_ONLY'
    when l.so_mencao                          then 'CONTEXT_ONLY'
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
    when coalesce(l.n,0) = 0
      then 'sem lugar do fato sustentado — serve de contexto, não de sinal do caso'
    when l.no_pais = 0
      then 'nenhum dos ' || l.n || ' lugares do fato é do país do caso'
    when p_janela_inicio is not null and ct.publicado_em is not null
         and ct.publicado_em::date < p_janela_inicio
      then 'publicado antes da janela do caso (' || ct.publicado_em::date::text
           || '): um documento não relata o futuro'
    when p_janela_fim is not null and ct.publicado_em is not null
         and ct.publicado_em::date > p_janela_fim
      then 'publicado depois da janela (' || ct.publicado_em::date::text
           || '), e o TEMPO DO FATO não é conhecido — a data de publicação não '
              'desqualifica o conteúdo, apenas não o sustenta'
    when l.so_mencao
      then 'o lugar do fato está sustentado por MENÇÃO — o nome do lugar aparece '
           'no texto, e mencionar não é afirmar que o fato foi ali'
    when cc.relacao = 'ESPECTRO_DE_PRODUTO'
      then 'lista de rótulo é espectro de produto, não ocorrência observada'
    else 'cultura, problema, país e janela conferem, com evidência escrita'
  end
  from public.conteudo_crop_issue cc
  join public.conteudo ct  on ct.id = cc.conteudo_id
  join public.crop_issue ci on ci.id = cc.crop_issue_id
  join public.crop  c on c.id = ci.crop_id
  join public.issue i on i.id = ci.issue_id
  left join lugares l on l.conteudo_id = ct.id
 where cc.id = p_conteudo_crop_issue;
$$;

comment on function public.f_relevancia_ao_caso is
  'PUBLISHED_AT != FACT_TIME e 0..N lugares do fato. A data de publicação decide numa '
  'direção só. Um lugar do fato no país do caso basta — exigir todos descartaria o '
  'documento que relata dois países ao mesmo tempo, que é justamente o mais valioso.';


-- ── OS PAÍSES DO FATO DE UM CONTEÚDO ──────────────────────────────────
-- Com 0..N lugares, um conteúdo pode sustentar fato em MAIS DE UM país.
-- Esta view é o único dono dessa pergunta, e as três views nacionais a
-- reusam — em vez de cada uma reimplementar o join e divergir com o tempo.
--
-- Um conteúdo sem lugar do fato cai em NAO_SEI. Ele NUNCA herda o país da
-- fonte: essa herança é a cicatriz de origem desta família inteira.
create or replace view public.v_conteudo_fact_country with (security_invoker = on) as
select ct.id as conteudo_id,
       coalesce(g.pais, 'NAO_SEI'::pais) as fact_country,
       (select count(distinct g2.pais) from public.conteudo_lugar cl2
          join public.geografia g2 on g2.id = cl2.geografia_id
         where cl2.conteudo_id = ct.id and cl2.papel = 'FACT') as paises_do_fato
  from public.conteudo ct
  left join public.conteudo_lugar cl
         on cl.conteudo_id = ct.id and cl.papel = 'FACT'
  left join public.geografia g on g.id = cl.geografia_id
 group by ct.id, g.pais;

comment on view public.v_conteudo_fact_country is
  'Um conteúdo, 0..N países do fato. `paises_do_fato` > 1 é informação, não erro: um '
  'documento que relata ocorrência em dois países existe, e escolher um deles seria '
  'inventar um recorte que a fonte não fez.';

-- ── AS TRÊS VIEWS NACIONAIS, REFEITAS ─────────────────────────────────
-- O que muda: `conteudos` passa a ser count(distinct conteúdo). Antes era
-- count(*) sobre um join 1:1 com a coluna única — o mesmo número enquanto
-- cada conteúdo tinha um país só. Com 0..N o join deixaria de ser 1:1, e
-- count(*) passaria a contar PARES conteúdo×país chamando isso de conteúdos.
create view public.v_independencia_por_par with (security_invoker = on) as
select fc.fact_country,
       ci.id as crop_issue_id, c.codigo as crop, i.codigo as issue,
       count(distinct ct.id)                       as conteudos,
       count(distinct coalesce(ct.obra_id, ct.id)) as obras_independentes,
       count(distinct cn.origem_id)                as origens_distintas
from public.crop_issue ci
join public.crop  c on c.id = ci.crop_id
join public.issue i on i.id = ci.issue_id
join public.conteudo_crop_issue cci on cci.crop_issue_id = ci.id
join public.conteudo ct on ct.id = cci.conteudo_id
join public.canal    cn on cn.id = ct.canal_id
join public.v_conteudo_fact_country fc on fc.conteudo_id = ct.id
where cci.relacao in ('OCORRENCIA_DECLARADA','ENSAIO_OU_ESTUDO','RECOMENDACAO_TECNICA')
group by 1, ci.id, c.codigo, i.codigo;

create view public.v_par_por_porta with (security_invoker = on) as
select fc.fact_country,
       c.codigo as crop, i.codigo as issue, ct.tipo as porta,
       count(distinct coalesce(ct.obra_id, ct.id)) as obras
from public.conteudo_crop_issue cci
join public.crop_issue ci on ci.id = cci.crop_issue_id
join public.crop  c on c.id = ci.crop_id
join public.issue i on i.id = ci.issue_id
join public.conteudo ct on ct.id = cci.conteudo_id
join public.v_conteudo_fact_country fc on fc.conteudo_id = ct.id
group by 1, c.codigo, i.codigo, ct.tipo;

create view public.v_cross_market_por_par with (security_invoker = on) as
select c.codigo as crop, i.codigo as issue, fc.fact_country,
       count(distinct coalesce(ct.obra_id, ct.id)) as obras,
       min(ct.publicado_em) as primeiro_registro,
       max(ct.publicado_em) as ultimo_registro
from public.conteudo_crop_issue cci
join public.crop_issue ci on ci.id = cci.crop_issue_id
join public.crop  c on c.id = ci.crop_id
join public.issue i on i.id = ci.issue_id
join public.conteudo ct on ct.id = cci.conteudo_id
join public.v_conteudo_fact_country fc on fc.conteudo_id = ct.id
group by c.codigo, i.codigo, fc.fact_country;
