-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 019
-- O EVENTO DO CONCORRENTE — uma camada DERIVADA, que não vira dona de nada
--
-- O COMPETITOR FORESIGHT PILOT precisa guardar fatos públicos datados sobre
-- concorrentes: marca depositada, registro local, caducidade, escoamento.
-- E precisa guardar a LIGAÇÃO entre eles, com estado.
--
-- ⚠️ ESTA MIGRATION NÃO CRIA DONO NENHUM.
--
-- O defeito que ela existe para evitar tem nome e já aconteceu duas vezes
-- nesta casa: a 016 criou um índice único que duplicava a chave natural da
-- 003, e a 018 aposentou `conteudo.fact_geografia_id` porque duas estruturas
-- respondiam à mesma pergunta. Aqui o risco é maior, porque a tentação é
-- confortável: seria fácil escrever `competidor text`, `registro text`,
-- `anuncio text` e ter tudo num lugar só. Isso criaria uma SEGUNDA verdade
-- sobre empresa, sobre registro e sobre anúncio, ao lado das que já existem.
--
-- Então cada entidade continua com seu dono, e esta tabela só APONTA:
--
--   empresa            -> public.organizacao          (002)
--   registro espanhol  -> public.registro_regulatorio (006)
--   produto de catálogo-> public.catalogo_produto     (014)
--   canal / página     -> public.canal                (002)
--   cultura / problema -> public.crop, public.issue   (004)
--   bruto preservado   -> public.raw_asset            (001)
--
-- MARCA é a única coisa que nasce aqui, e nasce como TEXTO num evento —
-- não como tabela. Não há dono de marca neste banco, e inventar um agora,
-- na véspera do piloto, seria a modelagem fora de hora que a 018 recusou.
--
-- NÃO EXECUTADA em Supabase. PostgreSQL 16 local e descartável.
-- ═══════════════════════════════════════════════════════════════════════


-- ═══════════════════════════════════════════════════════════════════════
-- 1 · O EVENTO
--
-- OBSERVED_AT != EFFECTIVE_DATE. As duas datas convivem, sempre, e é a
-- separação que impede a frase mais cara possível: "o concorrente fez isso
-- hoje", quando o que aconteceu hoje foi NÓS OLHARMOS.
--
--   observed_at     quando este projeto viu           — sempre existe
--   effective_date  quando a fonte diz que ocorreu    — pode faltar
--
-- A régua de change event já mediu por que isso importa: entre as duas
-- versões do ROPF há 15 meses e UMA observação. Datar o fato pela
-- observação teria empilhado 15 meses de mudanças num dia só.
-- ═══════════════════════════════════════════════════════════════════════

create table public.evento_concorrente (
  id              bigserial primary key,

  -- chave natural determinística, vinda do pipeline (IP:ST13, REG:id:tipo…).
  -- É ela que impede a mesma coleta rodada duas vezes de dobrar as linhas.
  event_key       text not null unique,

  competidor_id   bigint not null references public.organizacao(id) on delete restrict,
  pais            pais   not null,
  camada          text   not null check (camada in
                    ('IP','REGULATORY','PRODUCT_CATALOG','META','CREATOR')),
  event_type      text   not null,

  observed_at     date not null,
  effective_date  date,

  fonte           text not null,
  source_url      text,
  evidencia       text not null,

  -- ── os ponteiros para os donos. Nenhum é obrigatório; nenhum é cópia ──
  registro_id     bigint references public.registro_regulatorio(id) on delete restrict,
  registration_id_texto text,          -- quando o registro ainda não foi importado
  produto_id      bigint references public.catalogo_produto(id) on delete set null,
  canal_id        bigint references public.canal(id)             on delete set null,
  crop_id         bigint references public.crop(id)              on delete restrict,
  issue_id        bigint references public.issue(id)             on delete restrict,
  raw_asset_id    bigint references public.raw_asset(id)         on delete set null,

  -- marca é texto de evento. Não há tabela de marca, e não se cria uma aqui.
  brand           text,

  confidence_state text not null check (confidence_state in (
                     'OBSERVED_STRONG_AGRO_SIGNAL',
                     'OBSERVED_AMBIGUOUS_CLASS',
                     'OBSERVED_DATED_BY_SOURCE',
                     'OBSERVED_BETWEEN_TWO_ARCHIVED_VERSIONS',
                     'NOT_KNOWN')),

  dataset_owner   text not null default 'COMPETITOR_FORESIGHT_EAME',
  created_at      timestamptz not null default now(),

  -- ── as travas ────────────────────────────────────────────────────────

  -- Esta tabela é de UMA missão. Sem isto ela vira depósito comum, e em seis
  -- meses ninguém sabe qual linha responde a quem.
  constraint evento_tem_um_dono_so
    check (dataset_owner = 'COMPETITOR_FORESIGHT_EAME'),

  -- Ver o futuro não é possível. `observed_at` no futuro é erro de carga.
  -- `effective_date` no futuro é NORMAL e legítimo: caducidade e limite de
  -- venda são datas futuras declaradas hoje pela fonte.
  constraint observacao_nao_e_no_futuro
    check (observed_at <= current_date),

  -- Um fato DATADO sem a data não é fato datado: é um tipo sem conteúdo.
  constraint fato_datado_exige_a_data
    check (event_type not in ('EXPIRY','SELLING_OFF_DEADLINE','LOCAL_REGISTRATION',
                              'REGISTRATION_MODIFIED','TRADEMARK_APPLICATION',
                              'TRADEMARK_REGISTRATION')
           or effective_date is not null),

  -- Evento de registro sem registro é evento sobre nada.
  constraint evento_regulatorio_aponta_para_registro
    check (camada <> 'REGULATORY'
           or registro_id is not null or registration_id_texto is not null),

  -- Evento de marca sem a marca idem.
  constraint evento_de_ip_tem_marca
    check (camada <> 'IP' or brand is not null),

  -- META e CREATOR têm donos em OUTRAS missões. Esta camada só pode
  -- registrar evento deles apontando para o canal que já existe. Sem canal,
  -- a linha seria uma segunda verdade sobre anúncio — exatamente o que a
  -- missão proíbe no §6.
  constraint meta_e_creator_apontam_para_o_dono
    check (camada not in ('META','CREATOR') or canal_id is not null)
);

comment on table public.evento_concorrente is
  'Camada de inteligência DERIVADA. Não é dona de empresa, registro, anúncio '
  'nem creator: aponta para os donos que já existem. Uma linha aqui é um FATO '
  'PÚBLICO DATADO, nunca uma intenção do concorrente.';
comment on column public.evento_concorrente.observed_at is
  'Quando NÓS vimos. Nunca confundir com effective_date: entre duas versões '
  'do ROPF houve 15 meses e uma observação.';
comment on column public.evento_concorrente.effective_date is
  'Quando a FONTE diz que ocorreu. Pode ser futura — caducidade e limite de '
  'venda são datas futuras declaradas hoje, e isso não é erro.';
comment on column public.evento_concorrente.brand is
  'Texto. NÃO existe tabela de marca neste banco, e esta migration não cria '
  'uma: seria modelagem fora de hora na véspera do piloto.';
comment on column public.evento_concorrente.confidence_state is
  'OBSERVED_AMBIGUOUS_CLASS existe porque a classe 5 de Nice cobre '
  'farmacêutico junto com pesticida: 4.496 das 9.661 marcas coletadas caem '
  'nela, e 2.551 são da Bayer, que tem divisão farmacêutica.';

create index evento_conc_competidor_idx on public.evento_concorrente
  (competidor_id, pais, effective_date);
create index evento_conc_tipo_idx  on public.evento_concorrente (camada, event_type);
create index evento_conc_brand_idx on public.evento_concorrente (upper(brand));
create index evento_conc_reg_idx   on public.evento_concorrente (registration_id_texto);


-- ═══════════════════════════════════════════════════════════════════════
-- 2 · O LINK — e a trava que impede a antecedência inventada
--
-- A missão manda medir LEAD_DAYS "somente quando a relação entre eventos
-- for defensável". Isso não pode ficar só no script: um dia alguém carrega
-- a tabela por outro caminho. Então a regra desce para o banco.
--
-- Medido nos 209 pares provados desta rodada: a amplitude bruta de lead
-- days vai de -15.700 a +11.033 dias. Redepósito de marca, reuso de nome
-- comercial e colisão de nome genérico produzem esses extremos. Publicar a
-- média disso seria um número bonito medindo três coisas diferentes.
-- ═══════════════════════════════════════════════════════════════════════

create table public.evento_concorrente_link (
  id              bigserial primary key,

  evento_a_id     bigint not null references public.evento_concorrente(id) on delete cascade,
  evento_b_id     bigint not null references public.evento_concorrente(id) on delete cascade,

  estado          text not null check (estado in
                    ('PROVED','PARTIAL','REJECTED_HOLDER_MISMATCH','NOT_KNOWN')),
  evidencia       text not null,

  lead_days       integer,
  lead_days_defensavel boolean not null default false,

  dataset_owner   text not null default 'COMPETITOR_FORESIGHT_EAME',
  created_at      timestamptz not null default now(),

  -- ── as travas ────────────────────────────────────────────────────────

  -- Um evento não se liga a si mesmo, e o par não se repete invertido.
  constraint link_nao_e_reflexivo check (evento_a_id <> evento_b_id),
  constraint link_e_unico unique (evento_a_id, evento_b_id),

  -- ⚠️ A TRAVA CENTRAL. Antecedência só existe sobre identidade provada.
  -- Sem ela, um link PARTIAL carregaria um número de dias, e o número
  -- sobreviveria à ressalva — que é como uma medida virou verdade uma vez.
  constraint lead_days_exige_identidade_provada
    check (lead_days is null or estado = 'PROVED'),

  -- Defensável exige a ordem certa: marca ANTES do registro. Um lead
  -- negativo REFUTA a hipótese do piloto naquele par; chamá-lo de
  -- defensável seria publicar a refutação como confirmação.
  constraint defensavel_exige_ordem_e_valor
    check (lead_days_defensavel = false
           or (lead_days is not null and lead_days > 0 and estado = 'PROVED'))
);

comment on table public.evento_concorrente_link is
  'A relação temporal entre dois eventos públicos. NÃO é causalidade: o '
  'registro não diz que veio da marca, e a marca não diz que virou produto.';
comment on column public.evento_concorrente_link.lead_days is
  'Só existe quando estado = PROVED, por trava de banco. Nome parecido nunca '
  'gera link: URBOLE é marca da SYNGENTA e registro 24157 da ADAMA, e o par '
  'sai REJECTED_HOLDER_MISMATCH.';


-- ═══════════════════════════════════════════════════════════════════════
-- 3 · RLS — mesma regra de todas as tabelas desta casa
-- (as policies concretas dependem de public.eh_admin(), do schema de acesso)
-- ═══════════════════════════════════════════════════════════════════════
alter table public.evento_concorrente      enable row level security;
alter table public.evento_concorrente_link enable row level security;
