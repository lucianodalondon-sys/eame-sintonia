-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 020
-- A FONTE EXTERNA GANHA TABELA — e o estado dela passa a ser MEDIDO
--
-- Até aqui o banco sabia quem FALA (`origem` é pessoa ou organização) e sabia
-- o que foi COLHIDO (`collection_run`, `raw_asset`, `conteudo`). Não sabia
-- DE ONDE — o sítio, a API, o boletim regional, o portal estatístico. Isso
-- vivia em JSON e em prosa, e por isso a mesma pergunta era refeita a cada
-- missão: «essa fonte abre?».
--
-- A missão LAST-MILE de 02/09/2026 mediu 146 fontes e a resposta não é
-- binária. Ela tem CAUSA, e a causa muda o que fazer:
--
--   ABERTA                   nada a fazer
--   BLOQUEIO_GEOGRAFICO      abre de outro país — é ROTA, não ausência
--   TLS_DO_SERVIDOR          chave fraca ou cadeia incompleta — nem VPN resolve
--   DETECCAO_DE_ROBO         lê o navegador, não o IP — ⛔ e não se contorna
--   EXIGE_AUTENTICACAO       precisa de conta
--   FORA_DO_AR               não respondeu
--
-- ⚠️ A LEI QUE ESTA TABELA EXISTE PARA IMPEDIR
--
--     FONTE BLOQUEADA NÃO É FONTE INEXISTENTE.
--
-- O projeto já escreveu «a ISMEA não tem dado» quando a ISMEA tinha — ela
-- recusava o nosso IP. Sem estado medido, a próxima pessoa repete o erro, e
-- pior: com o tempo o erro vira premissa herdada, e ninguém mais testa.
--
-- ⚠️ E A ARMADILHA QUE ELA EXISTE PARA IMPEDIR DE NOVO
--
--     UM 200 NÃO DIZ NADA SOBRE A ROTA SE VOCÊ NÃO SABE POR ONDE SAIU.
--
-- Em 02/09 um coletor concluiu que «a ISMEA nunca esteve bloqueada», porque
-- recebeu HTTP 200. Havia uma VPN italiana ligada e ele não sabia. Por isso
-- `estado_de_acesso` é sempre acompanhado de `rota_de_saida` — sem saber por
-- onde a medição saiu, ela não mede nada.
--
-- NÃO EXECUTADA AQUI. O aplicador é `scripts/cadeia_canonica.sh`, e as
-- credenciais do Supabase só existem como segredo do GitHub Actions.
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- O QUE A FONTE PUBLICA. Não é o assunto do dado — é a NATUREZA dela.
-- Uma fonte pode publicar mais de uma coisa; por isso é array, e não enum
-- de coluna única. O Brasil tinha `tipo` texto livre e acabou com sete
-- grafias de «boletim».
-- ─────────────────────────────────────────────────────────────────────
create type fonte_natureza as enum (
  'ESTATISTICA_OFICIAL',      -- ISTAT, Eurostat
  'MERCADO',                  -- ISMEA, BMTI, EC Agri-food
  'BOLETIM_FITOSSANITARIO',   -- serviços fitossanitários regionais
  'AGROMETEOROLOGIA',         -- ARPA, Copernicus, JRC MARS
  'REGULATORIO',              -- Ministero, EU Pesticides Database, EUR-Lex
  'CIENCIA',                  -- OpenAlex, revistas, GIRE
  'CATALOGO_FABRICANTE',      -- adama.com e concorrentes
  'IMPRENSA_TECNICA',         -- Agronotizie, Informatore Agrario
  'EVENTO',                   -- feiras, congressos
  'REDE_SOCIAL',
  'OUTRA'
);

create type estado_de_acesso as enum (
  'ABERTA',
  'BLOQUEIO_GEOGRAFICO',
  'TLS_DO_SERVIDOR',
  'DETECCAO_DE_ROBO',
  'EXIGE_AUTENTICACAO',
  'FORA_DO_AR',
  'NAO_TESTADA'
);

-- De onde a medição saiu. Sem isto, `estado_de_acesso` é uma opinião.
create type rota_de_saida as enum ('BR_DIRETO', 'IT_VPN', 'OUTRA', 'NAO_SEI');

create table if not exists public.fonte_externa (
  id                 bigserial primary key,
  nome               text not null,
  url_base           text not null,
  natureza           fonte_natureza[] not null,
  pais               pais not null default 'IT',
  organismo          text,                    -- quem publica, quando declarado
  periodicidade      text,                    -- «semanal», «anual», NULL = não sei
  formato            text,                    -- HTML, PDF, SDMX, JSON, CSV
  observacao         text,
  criada_em          timestamptz not null default now(),
  UNIQUE (url_base)
);
comment on table public.fonte_externa is
  'De ONDE o dado veio: sítio, API, portal. Não confundir com `origem`, que é '
  'quem FALA (pessoa ou organização). Uma revista é fonte_externa; o autor '
  'assinado dela é origem.';
comment on column public.fonte_externa.natureza is
  'Array de propósito: uma fonte pode publicar estatística E mercado. Texto '
  'livre aqui produziria sete grafias de «boletim», como no Brasil.';

-- ─────────────────────────────────────────────────────────────────────
-- A MEDIÇÃO DO ACESSO. Uma linha por TESTE, não por fonte — porque o
-- estado muda com a rota e com o tempo, e o histórico é que prova a lei.
--
-- Guardar só o último estado apagaria justamente a evidência do bloqueio
-- geográfico: é a comparação entre duas rotas que prova que a fonte existe.
-- ─────────────────────────────────────────────────────────────────────
create table if not exists public.fonte_acesso_teste (
  id                 bigserial primary key,
  fonte_id           bigint not null references public.fonte_externa(id) on delete cascade,
  testada_em         timestamptz not null default now(),
  rota               rota_de_saida not null,
  estado             estado_de_acesso not null,
  http_status        int,
  bytes              int,
  segundos           numeric(6,2),
  erro_literal       text,          -- a mensagem do cliente, copiada
  evidencia          text not null, -- por que este estado, em uma frase
  causa_nao_e_geografia text,       -- quando o estado NÃO é geográfico, o porquê
  UNIQUE (fonte_id, testada_em, rota)
);
comment on table public.fonte_acesso_teste is
  'Uma linha por TESTE. O histórico é a prova: só a comparação entre rotas '
  'mostra que uma fonte existe e recusa o nosso IP. Guardar apenas o último '
  'estado apagaria a evidência.';
comment on column public.fonte_acesso_teste.rota is
  'OBRIGATÓRIO. UM 200 NÃO DIZ NADA SOBRE A ROTA SE VOCÊ NÃO SABE POR ONDE '
  'SAIU. Em 02/09/2026 um coletor concluiu que a ISMEA nunca esteve '
  'bloqueada, porque recebeu 200 — com uma VPN italiana ligada que ele '
  'desconhecia.';
comment on column public.fonte_acesso_teste.causa_nao_e_geografia is
  'Preenchido quando o obstáculo NÃO é o IP: DH_KEY_TOO_SMALL do enterisi.it, '
  'cadeia de certificado incompleta do regione.veneto.it, Akamai do adama.com. '
  'Sem esta coluna, alguém liga uma VPN esperando resolver e perde a tarde.';

-- ⚠️ A trava que impede a mentira mais cara desta tabela.
-- Declarar BLOQUEIO_GEOGRAFICO exige evidência de que a fonte responde por
-- OUTRA rota — senão «não abriu daqui» vira «bloqueio geográfico» por
-- preguiça, e a fonte é abandonada.
alter table public.fonte_acesso_teste drop constraint if exists
  bloqueio_geografico_precisa_de_prova;
alter table public.fonte_acesso_teste add constraint
  bloqueio_geografico_precisa_de_prova check (
    estado <> 'BLOQUEIO_GEOGRAFICO' or evidencia is not null and length(evidencia) > 20
  );

-- Uma fonte que exige rota italiana precisa dizer isso em algum lugar
-- consultável, senão a próxima coleta falha e ninguém sabe por quê.
create or replace view public.v_fonte_exige_rota_italiana as
select f.id, f.nome, f.url_base, f.natureza,
       max(t.testada_em) filter (where t.rota = 'IT_VPN'  and t.estado = 'ABERTA') as ok_por_italia,
       max(t.testada_em) filter (where t.rota = 'BR_DIRETO' and t.estado <> 'ABERTA') as falhou_direto
from public.fonte_externa f
join public.fonte_acesso_teste t on t.fonte_id = f.id
group by f.id, f.nome, f.url_base, f.natureza
having max(t.testada_em) filter (where t.rota = 'IT_VPN' and t.estado = 'ABERTA') is not null
   and max(t.testada_em) filter (where t.rota = 'BR_DIRETO' and t.estado <> 'ABERTA') is not null;
comment on view public.v_fonte_exige_rota_italiana is
  'As fontes que SÓ abrem por saída italiana, provadas pelas duas medições. '
  'Em 02/09/2026 eram ISMEA Mercati, ISTAT esploradati e ARPAV. Quem for '
  'coletar delas sem a rota vai receber timeout e concluir que sumiram.';
