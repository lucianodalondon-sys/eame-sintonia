-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 019
-- A CAMADA EUROPEIA DA SUBSTÂNCIA, E A RESISTÊNCIA CONFIRMADA.
--
-- Duas camadas que o esquema NÃO tinha, e que a rodada italiana de
-- 02/09/2026 mediu pela primeira vez.
--
-- ⚠️ POR QUE A PRIMEIRA PRECISOU NASCER, e é o achado que a motivou
-- ────────────────────────────────────────────────────────────────────────
-- A `registro_regulatorio` (006) é NACIONAL. Ela guarda que o KLARTAN vence
-- em 2027-01-31 na Itália, com o comentário — correto — de que
-- `EXPIRY != WITHDRAWAL`, porque re-registro nacional é rotina.
--
-- Só que a rotina pressupõe uma coisa que a tabela não sabe dizer: que a
-- APROVAÇÃO EUROPEIA da substância esteja de pé. E ela pode não estar.
--
--     A aprovação UE do tau-fluvalinate expira em 2027-01-31 — a MESMA
--     data dos 7 produtos ADAMA italianos que o contêm. A data nacional
--     não é um prazo administrativo italiano: é a fronteira europeia.
--
--     REGISTRO NACIONAL NÃO SOBREVIVE A APROVAÇÃO UE VENCIDA.
--
-- Sem esta tabela, o sistema lê 2027-01-31 como rotina renovável. Com ela,
-- lê como o que é. A diferença entre as duas leituras é a missão inteira.
--
-- ⚠️ POR QUE A SEGUNDA PRECISOU NASCER
-- ────────────────────────────────────────────────────────────────────────
-- `crop_issue` (004) diz que um par cultura×problema existe. Não diz que o
-- problema DEIXOU DE RESPONDER a um mecanismo — que é uma afirmação de
-- outra natureza, com outro dono e outra fonte. Na Itália o dono é o GIRE
-- (CNR-IPSP); no Brasil seria outro. A tabela guarda a DECLARAÇÃO DA
-- AUTORIDADE, nunca uma medição nossa.
--
-- ⛔ E ela NÃO é ponte para produto. Cruzar resistência com portfólio é
-- derivação, mora na `derivacao`, e carrega as proibições de sempre.
--
-- NÃO EXECUTADA.
-- ⚠️ ESTA MIGRATION NASCEU COM O NUMERO 017 E FOI RENUMERADA PARA 019.
--
-- O aplicador (`scripts/cadeia_canonica.sh`) usa os TRES PRIMEIROS
-- CARACTERES do nome do arquivo como chave do livro-razao:
--
--     num=$(basename "$f" | cut -c1-3)
--
-- Ja existia uma `017_o_que_a_conferencia_de_localizacao_achou.sql`, de
-- 30/08. Em ordem alfabetica «017_c» vem antes de «017_o», entao esta aqui
-- rodaria primeiro, gravaria versao='017' no livro, e a ORIGINAL seria
-- pulada para sempre -- em silencio, com o log dizendo SKIP como se fosse
-- normal. E a 018 declara, no proprio cabecalho, depender do que a 017 mediu.
--
--     DUAS MIGRATIONS COM O MESMO NUMERO NAO SAO DUAS. SAO UMA, E A OUTRA
--     NUNCA EXISTIU PARA O APLICADOR.
--
-- Renumerar e seguro aqui porque toda criacao desta migration e
-- `if not exists`: se ela ja tiver rodado como 017 em algum banco, rodar
-- como 019 devolve «already exists» e o livro anota JA_EXISTIA.
--

-- ═══════════════════════════════════════════════════════════════════════

-- ── 1 · SUBSTÂNCIA ATIVA, a entidade que faltava ───────────────────────
-- O `registro_regulatorio` guarda o PRODUTO. O ativo vivia solto dentro de
-- `catalogo_produto_substancia` como texto. Aqui ele vira entidade, porque
-- é dele que a aprovação europeia é.
create table if not exists public.substancia_ativa (
  id             bigserial primary key,
  nome_canonico  text not null,          -- TAU-FLUVALINATE
  nome_ue        text,                   -- como o ato europeu escreve
  cas            text,
  UNIQUE (nome_canonico)
);
comment on column public.substancia_ativa.nome_ue is
  'O ato europeu e o rótulo nacional escrevem o mesmo ativo de formas diferentes '
  '(CLODINAFOP x clodinafop-propargyl). Guardar as duas evita o casamento por '
  'palpite, que é o que fez `2,4-D` e `cloquintocet mexyl` não casarem na primeira '
  'passagem e a ausência parecer "sem ato".';

-- ── 2 · A APROVAÇÃO EUROPEIA, com a história inteira ───────────────────
create table if not exists public.substancia_aprovacao_ue (
  id                bigserial primary key,
  substancia_id     bigint not null references public.substancia_ativa(id) on delete cascade,
  celex             text not null,        -- 32024R1206
  ato_data          date not null,
  ato_tipo          text not null,        -- EXTENSION_OF_APPROVAL_PERIOD | RENEWAL | NON_RENEWAL | ...
  expiry_anterior   date,
  expiry_novo       date,
  anexo_parte       text,                 -- A, B, D, E do Anexo do Reg. 540/2011
  anexo_linha       text,
  risk_assessment   text,                 -- NOT_FINALISED | FINALISED | EFSA_NEEDS_MORE_TIME | NAO_SEI
  candidate_for_substitution boolean,
  citacao_literal   text not null,
  ato_lido          boolean not null default false,
  fonte             text not null default 'EU Publications Office / CELLAR',
  capturado_em      timestamptz not null,
  UNIQUE (substancia_id, celex)
);
comment on table public.substancia_aprovacao_ue is
  'Uma linha por ATO, não por substância. A aprovação do tau-fluvalinate já foi '
  'estendida em 2020 e de novo em 2024: são duas linhas, e a segunda não apaga a '
  'primeira. Prorrogação repetida É a informação — ela diz que a decisão está '
  'aberta há anos.';
comment on column public.substancia_aprovacao_ue.ato_lido is
  'TÍTULO CASADO NÃO É ATO LIDO. false significa que só o título nomeou a '
  'substância; nenhuma data desta linha pode ser publicada enquanto for false.';
comment on column public.substancia_aprovacao_ue.ato_tipo is
  'EXTENSION_OF_APPROVAL_PERIOD e RENEWAL são coisas DIFERENTES. A primeira só '
  'empurra a data porque a decisão não saiu; a segunda decide. Confundir as duas '
  'transforma "pendente há 6 anos" em "renovado".';
comment on column public.substancia_aprovacao_ue.risk_assessment is
  'NOT_FINALISED é declaração do PRÓPRIO ato, citada em `citacao_literal`. Não é '
  'inferência nossa e não é previsão de resultado.';

-- ── 3 · A PONTE produto nacional ↔ substância ──────────────────────────
create table if not exists public.registro_substancia (
  registro_id    bigint not null references public.registro_regulatorio(id) on delete cascade,
  substancia_id  bigint not null references public.substancia_ativa(id) on delete restrict,
  primary key (registro_id, substancia_id)
);

-- A pergunta que só existe depois da 017: um produto nacional cuja data
-- nacional COINCIDE com a fronteira europeia da sua substância.
create or replace view public.v_registro_x_fronteira_ue as
select r.pais,
       r.registration_id,
       r.nome_comercial,
       r.fecha_caducidad                          as expiry_nacional,
       s.nome_canonico                            as substancia,
       a.expiry_novo                              as expiry_ue,
       a.risk_assessment,
       a.celex,
       a.ato_lido,
       (r.fecha_caducidad = a.expiry_novo)        as datas_coincidem
from public.registro_regulatorio r
join public.registro_substancia rs on rs.registro_id = r.id
join public.substancia_ativa s     on s.id = rs.substancia_id
join public.substancia_aprovacao_ue a on a.substancia_id = s.id
where a.expiry_novo is not null;
comment on view public.v_registro_x_fronteira_ue is
  '`datas_coincidem` = true é o sinal que a 017 existe para produzir: o vencimento '
  'nacional NÃO é administrativo, é a aprovação europeia. Ler como rotina de '
  're-registro seria errar a natureza do prazo. ⛔ E mesmo true NÃO autoriza dizer '
  'que o produto sai do mercado.';

-- ── 4 · RESISTÊNCIA CONFIRMADA POR AUTORIDADE ──────────────────────────
create table if not exists public.resistencia_confirmada (
  id                bigserial primary key,
  pais              pais not null,
  especie           text not null,          -- Lolium spp.
  especie_comum     text,                   -- loietto
  crop_id           bigint references public.crop(id) on delete restrict,
  cultura_declarada text,                   -- como a autoridade escreve, quando não há crop_id
  mecanismo         text not null,          -- ACCasi | ALS | EPSP | fotossistema II | ...
  hrac              text,
  primeiro_caso_ano smallint,
  regioes           text[],
  resistencia_multipla boolean,
  autoridade        text not null,          -- GIRE (CNR-IPSP)
  fonte_url         text not null,
  citacao_literal   text not null,
  capturado_em      timestamptz not null,
  UNIQUE (pais, especie, mecanismo, cultura_declarada, autoridade)
);
comment on table public.resistencia_confirmada is
  'A DECLARAÇÃO DA AUTORIDADE de que uma espécie deixou de responder a um mecanismo, '
  'naquela cultura. ⛔ NÃO é mapa de incidência: diz ONDE FOI CONFIRMADA, nunca '
  'quanta área tem. ⛔ E não é medição nossa — `citacao_literal` é obrigatória para '
  'que ninguém possa publicar a linha sem a frase que a sustenta.';
comment on column public.resistencia_confirmada.cultura_declarada is
  'A cultura como a autoridade escreve ("dicotiledoni estive"), que às vezes é um '
  'GRUPO e não uma espécie. Forçar isso dentro de `crop` inventaria precisão: quando '
  'não houver crop_id, o texto fica, e a régua sabe que é grupo.';
comment on column public.resistencia_confirmada.regioes is
  'Regiões NOMEADAS pela fonte. Vazio é NÃO SEI, jamais "em todo o país".';

alter table public.substancia_ativa          enable row level security;
alter table public.substancia_aprovacao_ue   enable row level security;
alter table public.registro_substancia       enable row level security;
alter table public.resistencia_confirmada    enable row level security;

-- ⛔ O QUE A 017 DELIBERADAMENTE NÃO CRIA
-- Nenhuma tabela que ligue `resistencia_confirmada` a produto. O cruzamento
-- "a ADAMA tem N registros que declaram o grupo com resistência confirmada"
-- é DERIVAÇÃO, mora na `derivacao` com sua evidência, e continua sujeito à
-- lista de afirmações proibidas. Uma chave estrangeira aqui daria a esse
-- cruzamento a aparência de fato regulatório, que ele não tem.
