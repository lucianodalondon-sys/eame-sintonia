-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 009
-- PAÍS NÃO É FILTRO. PAÍS MUDA A VERDADE DA AFIRMAÇÃO.
--
-- Cada país é um portal Sintonia completo; a camada EAME compara produtos
-- nacionais. O mesmo banco serve os três, mas nenhuma linha pode emprestar
-- portfólio, regulação ou disponibilidade comercial de um país para outro.
--
-- Feita agora, com o banco em ROWS_TOTAL = 0: todo ADD COLUMN NOT NULL aqui
-- é barato porque não há linha para preencher. Com dado dentro, deixa de ser.
--
-- NÃO EXECUTADA.
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- 1 · PORTFÓLIO É NACIONAL — e o país entra na CHAVE, não só na linha.
--
-- Sem isto, "a ADAMA tem resposta registrada para OLIVE × REPILO" é uma
-- frase sem país — e a chave (crop_issue, titular, fonte_versao) deixaria
-- ES e FR colidirem sempre que a versão da fonte coincidisse.
-- ─────────────────────────────────────────────────────────────────────
alter table public.resposta_registrada
  add column pais pais not null;
alter table public.resposta_registrada
  drop constraint resposta_registrada_crop_issue_id_titular_fonte_versao_key;
alter table public.resposta_registrada
  add constraint resposta_registrada_por_pais
  unique (pais, crop_issue_id, titular, fonte_versao);
comment on column public.resposta_registrada.pais is
  'DONO ÚNICO da nacionalidade desta afirmação. Não existe segunda coluna de '
  'país nesta tabela: portfolio_country e market_country seriam o mesmo fato '
  'com dois nomes, e duas colunas iguais divergem.';

-- Disponibilidade comercial SAI daqui. Ver bloco 2.
alter table public.resposta_registrada
  drop column current_commercial_availability;

-- ─────────────────────────────────────────────────────────────────────
-- 2 · DISPONIBILIDADE COMERCIAL É OUTRA AFIRMAÇÃO, COM OUTRA PROVENIÊNCIA
--
-- REGISTERED_RESPONSE_EXISTS != CURRENT_COMMERCIAL_AVAILABILITY. A segunda
-- tem outra fonte, outra data, outro método e outra validade — e dentro de
-- `resposta_registrada` ela herdava a proveniência do REGISTRO, que não a
-- sustenta. Separar não é estética: é a única forma de ela carregar o
-- próprio SOURCE, SOURCE_VERSION e MEASURED_AT.
--
-- Ausência de evidência comercial é NAO_SEI, nunca NAO — e por isso o
-- default é NAO_SEI e um estado 'NAO' exige fonte declarada.
-- ─────────────────────────────────────────────────────────────────────
create table public.disponibilidade_comercial (
  id             bigserial primary key,
  pais           pais   not null,
  crop_issue_id  bigint not null references public.crop_issue(id) on delete restrict,
  titular        text   not null,
  estado         text   not null default 'NAO_SEI'
                 check (estado in ('SIM','NAO','NAO_SEI')),
  fonte          text,
  fonte_versao   text,
  medido_em      timestamptz,
  rule_version   text   not null,
  CONSTRAINT afirmacao_comercial_exige_fonte
    CHECK (estado = 'NAO_SEI' OR (fonte IS NOT NULL AND medido_em IS NOT NULL)),
  -- fonte_versao e nulavel; sem NULLS NOT DISTINCT duas medicoes sem versao
  -- declarada entrariam as duas, e a segunda destrancaria a trava.
  UNIQUE NULLS NOT DISTINCT (pais, crop_issue_id, titular, fonte_versao)
);
comment on constraint afirmacao_comercial_exige_fonte on public.disponibilidade_comercial is
  'Dizer SIM ou NAO sobre o mercado exige fonte e data. NAO_SEI não exige — '
  'é o estado honesto de quem não mediu, e o default.';

-- ─────────────────────────────────────────────────────────────────────
-- 3 · LACUNA É NACIONAL. "Falta resposta para OLIVE × REPILO" é falso ou
--     verdadeiro conforme o país.
-- ─────────────────────────────────────────────────────────────────────
alter table public.lacuna_candidata add column pais pais not null;
alter table public.lacuna_candidata
  add constraint lacuna_por_pais unique (pais, crop_issue_id, rule_version);

-- ─────────────────────────────────────────────────────────────────────
-- 4 · DERIVAÇÃO DECLARA SEU ESCOPO
--
-- "CONFOUNDER_OPEN em Córdoba" é uma conclusão espanhola. Uma comparação
-- ES × FR é outra coisa, e precisa ser PEDIDA — não pode ser o default de
-- uma linha que esqueceu de dizer de onde fala.
-- ─────────────────────────────────────────────────────────────────────
alter table public.derivacao add column escopo_pais pais;
alter table public.derivacao add column cross_market boolean not null default false;
alter table public.derivacao
  add constraint derivacao_declara_de_onde_fala
  CHECK ( (cross_market and escopo_pais is null)
       or ((not cross_market) and escopo_pais is not null) );
comment on constraint derivacao_declara_de_onde_fala on public.derivacao is
  'Ou a conclusão é de UM país nomeado, ou é explicitamente cross-market. '
  'Não existe conclusão sem origem declarada.';

-- ─────────────────────────────────────────────────────────────────────
-- 5 · CROP e ISSUE VOLTAM A SER CANÔNICOS
--
-- `nome_es` e `mapa_id_cultivo` eram seed espanhol dentro da entidade
-- canônica. OLIVE é OLIVE nos três países; OLIVO, OLIVIER e OLIVO são
-- nomes locais, e o id do MAPA é um identificador de UM sistema nacional.
-- Vão para uma camada de vocabulário local, sem inventar id francês ou
-- italiano: a tabela nasce só com o que a Espanha realmente tem.
-- ─────────────────────────────────────────────────────────────────────
create table public.crop_local (
  id             bigserial primary key,
  crop_id        bigint not null references public.crop(id) on delete cascade,
  pais           pais   not null,
  source_system  text   not null,          -- MAPA_ROPF, EPHY, ...
  external_id    text,                     -- id no sistema nacional
  nome_local     text   not null,
  -- external_id fica NULL onde o pais ainda nao tem sistema mapeado — e por
  -- isso a trava precisa tratar dois NULLs como iguais, senao o pais sem id
  -- aceita linhas repetidas justamente por nao ter identificador.
  UNIQUE NULLS NOT DISTINCT (pais, source_system, external_id),
  UNIQUE (crop_id, pais, source_system, nome_local)
);
create table public.issue_local (
  id             bigserial primary key,
  issue_id       bigint not null references public.issue(id) on delete cascade,
  pais           pais   not null,
  source_system  text   not null,
  external_id    text,
  nome_local     text   not null,
  -- external_id fica NULL onde o pais ainda nao tem sistema mapeado — e por
  -- isso a trava precisa tratar dois NULLs como iguais, senao o pais sem id
  -- aceita linhas repetidas justamente por nao ter identificador.
  UNIQUE NULLS NOT DISTINCT (pais, source_system, external_id),
  UNIQUE (issue_id, pais, source_system, nome_local)
);
comment on table public.crop_local is
  'Um CROP canônico, N vocabulários nacionais. O id do MAPA é um external_id '
  'espanhol, não um atributo do OLIVE.';

alter table public.crop  drop column nome_es;
alter table public.crop  drop column mapa_id_cultivo;
alter table public.issue drop column nome_es;
alter table public.issue drop column mapa_id_plaga;

alter table public.crop_local  enable row level security;
alter table public.issue_local enable row level security;
alter table public.disponibilidade_comercial enable row level security;

-- ─────────────────────────────────────────────────────────────────────
-- 6 · VIEWS NACIONAIS DEIXAM DE SOMAR PAÍSES EM SILÊNCIO
--
-- As duas views de evidência agrupavam CROP × ISSUE sobre TODO o conteúdo.
-- Com ES + FR + IT no mesmo banco, elas somariam três mercados e chamariam
-- o resultado de "a evidência do par". Agora o país é coluna de agrupamento,
-- e quem quiser comparar mercados pede a view cross-market pelo nome.
--
-- FACT_COUNTRY é o país do FATO. Quando ele é desconhecido, a linha cai em
-- 'NAO_SEI' — nunca herda o país da fonte.
-- ─────────────────────────────────────────────────────────────────────
-- ⚠️ ATENÇÃO: as três views desta seção são SUBSTITUÍDAS pela 018. Elas leem
-- `conteudo.fact_geografia_id`, coluna que a 018 aposenta ao dar à lei do
-- lugar do fato um dono que expressa 0..N. Editar aqui não muda o banco
-- depois da 018.
-- CREATE OR REPLACE nao troca o nome/ordem das colunas de uma view existente.
-- Como `fact_country` entra na frente, a view precisa ser derrubada e refeita.
drop view if exists public.v_independencia_por_par;
create view public.v_independencia_por_par with (security_invoker = on) as
select coalesce(gf.pais, 'NAO_SEI'::pais)       as fact_country,
       ci.id as crop_issue_id, c.codigo as crop, i.codigo as issue,
       count(*)                                    as conteudos,
       count(distinct coalesce(ct.obra_id, ct.id)) as obras_independentes,
       count(distinct cn.origem_id)                as origens_distintas
from public.crop_issue ci
join public.crop  c on c.id = ci.crop_id
join public.issue i on i.id = ci.issue_id
join public.conteudo_crop_issue cci on cci.crop_issue_id = ci.id
join public.conteudo ct on ct.id = cci.conteudo_id
join public.canal    cn on cn.id = ct.canal_id
left join public.geografia gf on gf.id = ct.fact_geografia_id
where cci.relacao in ('OCORRENCIA_DECLARADA','ENSAIO_OU_ESTUDO','RECOMENDACAO_TECNICA')
group by 1, ci.id, c.codigo, i.codigo;

drop view if exists public.v_par_por_porta;
create view public.v_par_por_porta with (security_invoker = on) as
select coalesce(gf.pais, 'NAO_SEI'::pais) as fact_country,
       c.codigo as crop, i.codigo as issue, ct.tipo as porta,
       count(distinct coalesce(ct.obra_id, ct.id)) as obras
from public.conteudo_crop_issue cci
join public.crop_issue ci on ci.id = cci.crop_issue_id
join public.crop  c on c.id = ci.crop_id
join public.issue i on i.id = ci.issue_id
join public.conteudo ct on ct.id = cci.conteudo_id
left join public.geografia gf on gf.id = ct.fact_geografia_id
group by 1, c.codigo, i.codigo, ct.tipo;

-- A comparação entre mercados existe, mas tem NOME. Ninguém cai nela sem pedir.
-- REPLAY-SAFE: esta view é redefinida por uma migration posterior, e
-- `create or replace` recusa reescrever view cuja forma mudou. O drop
-- faz cada migration ser dona inteira do objeto no ponto dela da cadeia.
drop view if exists public.v_cross_market_por_par;
create view public.v_cross_market_por_par with (security_invoker = on) as
select c.codigo as crop, i.codigo as issue,
       coalesce(gf.pais, 'NAO_SEI'::pais) as fact_country,
       count(distinct coalesce(ct.obra_id, ct.id)) as obras,
       min(ct.publicado_em) as primeiro_registro,
       max(ct.publicado_em) as ultimo_registro
from public.conteudo_crop_issue cci
join public.crop_issue ci on ci.id = cci.crop_issue_id
join public.crop  c on c.id = ci.crop_id
join public.issue i on i.id = ci.issue_id
join public.conteudo ct on ct.id = cci.conteudo_id
left join public.geografia gf on gf.id = ct.fact_geografia_id
where cci.relacao in ('OCORRENCIA_DECLARADA','ENSAIO_OU_ESTUDO','RECOMENDACAO_TECNICA')
group by c.codigo, i.codigo, 3;
comment on view public.v_cross_market_por_par is
  'A ÚNICA view que compara países, e ela precisa ser chamada pelo nome. '
  '`primeiro_registro` por país é o que sustenta a pergunta EAME "apareceu '
  'primeiro onde?" — sem afirmar difusão, que exige mais que ordem de data.';

-- Portfólio lado a lado entre mercados, também explícita.
create or replace view public.v_cross_market_portfolio with (security_invoker = on) as
select c.codigo as crop, i.codigo as issue, rr.pais, rr.titular,
       rr.registered_response_exists, rr.registro_count,
       dc.estado as disponibilidade_comercial
from public.resposta_registrada rr
join public.crop_issue ci on ci.id = rr.crop_issue_id
join public.crop  c on c.id = ci.crop_id
join public.issue i on i.id = ci.issue_id
left join public.disponibilidade_comercial dc
       on dc.crop_issue_id = rr.crop_issue_id
      and dc.pais = rr.pais
      and dc.titular = rr.titular;
