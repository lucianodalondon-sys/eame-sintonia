-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 022
-- A PRATELEIRA DE UMA REGIÃO — venda declarada, força de marca, oportunidade
-- e o comprador candidato
--
-- Até aqui o banco sabia o que está REGISTRADO (migration 006) e o que a
-- ciência e o campo OBSERVARAM (005, 021). Não tinha lugar para a terceira
-- pergunta, que é a primeira que o Field Sales faz:
--
--     «onde este produto efetivamente se move, e onde não se move?»
--
-- A resposta existe em fonte pública e obrigatória: o D.Lgs 150/2012 art. 16
-- obriga cada titular de autorização de venda a declarar, uma vez por ano, o
-- que vendeu. O Vêneto publica isso como open data (IT-T10-001).
--
-- AS QUATRO LEIS QUE VIRAM COLUNA E TRAVA AQUI
--
--   1. VOLUME NÃO É VALOR. A unidade é kg/litro e está em coluna própria,
--      obrigatória. Enxofre e cobre dominam o volume e custam pouco por
--      quilo: quota em volume NÃO é quota de mercado. Por isso a coluna
--      chama-se `quota_volume_pct` e não `market_share`.
--
--   2. AUSÊNCIA NA DECLARAÇÃO NÃO É AUSÊNCIA DE VENDA. A tabela de
--      oportunidade guarda `classe`, com dois valores possíveis, e nenhum
--      deles diz «não vendido»: produto comprado fora da região e aplicado
--      dentro não aparece na declaração.
--
--   3. O COMPRADOR NÃO ESTÁ NA FONTE. A declaração é publicada agregada por
--      província; o nome de quem vendeu é o campo que ela omite. Por isso
--      `comprador_candidato` é tabela SEPARADA, alimentada por outra porta,
--      e cada linha dela carrega `estado_evidencia` e `fonte`.
--
--   4. EXTERNAL-ONLY (P-003). Nada aqui é dado interno da ADAMA. São
--      declarações públicas de terceiros sobre produtos cujo titular é a
--      ADAMA — a distinção está escrita em D-027 do diário de decisões.
--
-- NÃO EXECUTADA AQUI. Aplicador: `scripts/cadeia_canonica.sh`.
-- ═══════════════════════════════════════════════════════════════════════
begin;

-- 1 · A VENDA DECLARADA, como a fonte a publica: província × produto × ano
create table if not exists public.canal_venda_declarada (
    id                  bigserial primary key,
    fonte_source_id     text        not null,          -- IT-T10-001
    run_id              text        not null,          -- resolve no RUN-MANIFEST
    ano                 int         not null,
    pais                text        not null default 'IT',
    regiao              text        not null,
    provincia           text        not null,
    num_registrazione   int         not null,          -- a chave do cruzamento
    produto_na_fonte    text,                          -- a fonte às vezes omite o nome
    quantidade          numeric     not null check (quantidade >= 0),
    unidade             text        not null default 'kg_ou_litro',
    inserido_em         timestamptz not null default now(),
    unique (ano, provincia, num_registrazione, produto_na_fonte)
);
comment on table public.canal_venda_declarada is
    'Declaração anual de venda de fitossanitários (D.Lgs 150/2012 art. 16). Volume físico, nunca valor. Não diz quem comprou nem qual revenda vendeu.';
comment on column public.canal_venda_declarada.quantidade is
    'kg ou litros. Somar entre tipos de produto é legítimo para dimensionar o território e ILEGÍTIMO para afirmar share.';

-- 2 · A FORÇA DE MARCA: província × titular × tipo, com posição medida
create table if not exists public.canal_forca_de_marca (
    id                  bigserial primary key,
    ano                 int         not null,
    regiao              text        not null,
    provincia           text        not null,
    titolare            text        not null,          -- o titular do registro, não a marca comercial
    tipo                text        not null,          -- FUNGICIDA, DISERBANTE, INSETTICIDA...
    quantidade          numeric     not null,
    quota_volume_pct    numeric     not null,          -- dentro do tipo E da província
    posicao             int         not null,
    concorrentes        int         not null,
    e_adama             boolean     not null default false,
    unique (ano, provincia, titolare, tipo)
);
comment on column public.canal_forca_de_marca.titolare is
    'Titular do registro. Não é a marca percebida no balcão, e não diz de quem a revenda compra.';

-- 3 · A OPORTUNIDADE: portfólio ativo SEM venda declarada naquela província
create table if not exists public.canal_oportunidade (
    id                          bigserial primary key,
    ano                         int     not null,
    regiao                      text    not null,
    provincia                   text    not null,
    num_registrazione           int     not null,
    produto                     text    not null,
    titolare                    text    not null,
    tipo                        text,
    validade                    text,
    classe                      text    not null
        check (classe in ('VENDE_NA_REGIAO_MAS_NAO_AQUI',
                          'SEM_VENDA_DECLARADA_EM_TODA_A_REGIAO')),
    kg_no_resto_da_regiao       numeric not null default 0,
    unique (ano, provincia, num_registrazione)
);
comment on table public.canal_oportunidade is
    'Sem venda DECLARADA. Nunca «não vendido»: produto comprado fora e aplicado dentro não aparece, e omissão de declarante é possível.';

-- 4 · O COMPRADOR CANDIDATO — outra porta, outro estado de evidência
create table if not exists public.comprador_candidato (
    id                      bigserial primary key,
    nome                    text        not null,
    partita_iva             text,                      -- a chave nacional estável
    tipo_canal              text        not null
        check (tipo_canal in ('CONSORZIO_AGRARIO', 'RIVENDITA_PRIVADA', 'COOPERATIVA',
                              'OP_AOP', 'GRUPPO_ACQUISTO', 'NAO_SEI')),
    rede                    text,                      -- CAI, Compag, independente
    pais                    text        not null default 'IT',
    regiao                  text        not null,
    provincia               text,
    comune                  text,
    lat                     numeric,
    lon                     numeric,
    faturamento_eur         numeric,
    faturamento_ano         int,
    compra_agrofarmaco_eur  numeric,                   -- quando é público. Quase nunca é.
    socios_ou_clientes      int,
    pontos_de_venda         int,
    hectares_servidos       numeric,
    marcas_conhecidas       jsonb       not null default '[]'::jsonb,
    tier                    text check (tier in ('A', 'B', 'C', 'NAO_SEI')),
    estado_evidencia        text        not null
        check (estado_evidencia in ('COMPROVADO', 'COMPROVADO_VIA_IMPRENSA', 'INFERENCIA',
                                    'HIPOTESE', 'NAO_SEI')),
    fonte                   text        not null,
    fonte_data              date,
    adama_presente          text        not null default 'NAO_SEI'
        check (adama_presente in ('SIM', 'NAO', 'NAO_SEI')),
    observacao              text,
    inserido_em             timestamptz not null default now(),
    unique (nome, regiao)
);
comment on table public.comprador_candidato is
    'Candidato a cliente do canal. Nenhuma linha afirma relação comercial com a ADAMA: isso é dado interno e está fechado por P-003.';
comment on column public.comprador_candidato.marcas_conhecidas is
    'Marcas que o comprador PUBLICA trabalhar. Lista vazia significa «não publica», nunca «não trabalha nenhuma».';

-- 5 · A leitura que o portal vai pedir primeiro: quem está forte em cada província
create or replace view public.canal_forca_por_provincia as
select ano, regiao, provincia, tipo, titolare, quantidade, quota_volume_pct, posicao, e_adama
from public.canal_forca_de_marca
where posicao <= 10
order by ano desc, provincia, tipo, posicao;

commit;
