-- ═══════════════════════════════════════════════════════════════════════
-- 033 · A SALA GUARDA A BASE, AS QUATRO CHAVES E AS REVISÕES — UMA migração só
--
-- D68 (dono, 25/09): «UMA migração aditiva — a 033 B do TEMPO-E-LUGAR + as
-- colunas das 4 chaves + a 033 do REROUTE — um só número, uma só migração; e a
-- tabela sala_de_espera_revisao que só acrescenta.» Três propostas de três
-- bancadas, que tinham todas o número 033, juntas aqui:
--
--   A · TEMPO-E-LUGAR   published_at_basis · source_location_basis ·
--                       completude_tempo_lugar · tempo_lugar_evidencia
--                       (TEMPO-E-LUGAR.md §7 B; DA-7 da LUGAR-FATO)
--   B · QUATRO-CHAVES   janela_declarada + a trava da forma, TAL E QUAL da
--                       referência provada da nuvem (nuvem-quatro-chaves-sala-v1,
--                       docs/operacao/QUATRO-CHAVES-DESENHO-DAS-COLUNAS.md)
--   C · REROUTE         sala_de_espera_gaveta          (RELATORIO-REROUTE.md §2)
--   D · REVISÕES        sala_de_espera_revisao (só acrescenta) + a vista
--                       sala_de_espera_atual           (TEMPO-E-LUGAR.md §7 C)
--
-- ── A · O VALOR CHEGAVA, A BASE PARAVA NA PORTA ───────────────────────────
--
-- Medido no TEMPO-E-LUGAR (25/09): a `032` deu casa a `fact_time_basis` e
-- `fact_location_basis`, e não às outras duas. Depois do encanamento, o VALOR
-- de `published_at` e de `source_location` chega à Sala e a BASE fica na
-- porta. Para a data de publicação de uma página (JSON-LD? meta tag?) a base
-- não se reconstrói depois — e um valor sem base é o que a lei proíbe.
--
--     CADA VALOR COM A SUA BASE (D61).
--
-- `completude_tempo_lugar` (D62): de quatro perguntas — publicação, lugar da
-- fonte, data do facto, lugar do facto — quais estão PROVADAS, quais foram
-- CALCULADAS (data relativa contada a partir da publicação provada, D63) e
-- quais são NAO SEI. Nada disto barra: é o grau de precisão, para a
-- Intelligence. O dono é `admissao.completude_tempo_lugar()`; o default é
-- `admissao.COMPLETUDE_NAO_MEDIDA`, byte a byte (há teste que o confere).
--
-- ── B · AS QUATRO CHAVES — COPIADO, NÃO REDESENHADO ──────────────────────
--
-- O DDL e o default vêm da referência provada da nuvem (Postgres 16
-- descartável 40/40; CI 2b8 29/29), sem uma letra mudada. O dono do registo
-- é `admissao.janela_declarada()`, que vive na linha dela e ainda não está
-- nesta árvore: até lá, toda linha lê o default, que diz «não medido».
-- Quando a linha dela juntar, o `033_a_sala_guarda_as_quatro_chaves.sql` dela
-- DEIXA DE EXISTIR como ficheiro próprio, e o teste do default passa a ler
-- este ficheiro.
--
-- ── C · A GAVETA EXTRA DO REROUTE — A TABELA, E NINGUÉM A ESCREVE AINDA ──
--
-- D66 (dono): o REROUTE só anota (`REROUTE_ENTRA_NA_SALA = False`). A tabela
-- nasce vazia para que a decisão de a encher não precise de outra migração.
-- Nenhum código desta árvore escreve nela.
--
-- ── D · CORRIGIR SEM APAGAR: AS REVISÕES ─────────────────────────────────
--
-- Medido: a Sala sabia `pousar`, `ler`, `listar_pendentes` e `retirar`, e
-- não sabia CORRIGIR. Reprocessar o acervo pela estrada reaproveita o texto
-- derivado, o item volta com o mesmo nome, e `pousar` responde
-- `JA_NA_SALA_POR_OUTRA_CORRIDA` — os campos antigos ficavam para sempre.
--
-- A resposta NÃO é um UPDATE: `corrida_sha256` assina o corpo tal como
-- pousou, e reescrever a linha partia a assinatura e apagava o que se sabia
-- antes. A resposta é uma TABELA QUE SÓ ACRESCENTA — cada revisão diz o
-- campo, o valor, a base, que extractor, que versão, quando e porquê — e uma
-- VISTA que lê «a última revisão, senão o valor original».
--
--     O RAW NÃO MUDA. A LINHA NÃO MUDA. NUNCA HÁ UPDATE CALADO.
--
-- A trava é do BANCO, e não de disciplina: UPDATE, DELETE e TRUNCATE na
-- tabela de revisões levantam `SALA_REVISAO_SO_ACRESCENTA`.
--
-- Quem escreve e lê: `admissao/sala_de_espera.py` (`rever`, `ler_atual`) —
-- o dono único do SQL da Sala. A Intelligence lê pela vista.
--
-- ── O QUE ESTA MIGRAÇÃO NÃO FAZ ──────────────────────────────────────────
--
-- Não apaga, não renomeia, não muda tipo. Não reescreve nenhuma linha: as que
-- já estão na Sala leem os defaults, que dizem «não medido». Não cria
-- revisão nenhuma — quem as cria é o reprocessamento, pela porta.
--
-- ⚠️ `json`, E NÃO `jsonb`, nas colunas novas: `impressao_da_corrida()`
-- assina os BYTES do corpo, e `jsonb` reordena chaves (mesma razão da `032`).
--
-- ── O DESFAZER ────────────────────────────────────────────────────────────
--
-- `supabase/desfazer/033_desfazer.sql`, FORA desta pasta de propósito: a
-- cadeia aplica todo `*.sql` daqui, e um desfazer aqui dentro seria aplicado
-- logo a seguir ao fazer.
--
-- ═══════════════════════════════════════════════════════════════════════
--
--     DESIGNED  = YES
--     DB_TESTED = YES   ·  PostgreSQL 16 DESCARTÁVEL (initdb próprio):
--                          tests/test_migracao_033_sala.py, e o ensaio na
--                          CÓPIA da Sala real (MIGRACAO-SALA.md)
--     LIVE      = NO    ·  NÃO EXECUTADA na Sala real. Quem aplica é o
--                          coordenador, pelo roteiro de MIGRACAO-SALA.md.
--
-- ⚠️ A PARTIR DO DIA EM QUE ISTO FOR A PRODUÇÃO, ESTE FICHEIRO NÃO SE EDITA.
-- O livro-razão da cadeia guarda o sha256 do que foi aplicado.
--
--     DESIGNED != DB_TESTED != LIVE.
-- ═══════════════════════════════════════════════════════════════════════

-- ── A · a base da publicação e da sede, e a completude ──────────────────
alter table public.sala_de_espera
  add column if not exists published_at_basis text not null default 'NAO SEI';
alter table public.sala_de_espera
  add column if not exists source_location_basis text not null default 'NAO SEI';
alter table public.sala_de_espera
  add column if not exists completude_tempo_lugar json not null
  default '{"DATA_DO_FATO": "NAO SEI", "LOCAL_DA_FONTE": "NAO SEI", "LOCAL_DO_FATO": "NAO SEI", "ORIGEM": "pousado antes da migration 033: a completude nao foi medida", "PROVADAS": "NAO SEI", "PUBLICACAO": "NAO SEI"}'::json;

-- DA-7 (LUGAR-FATO): o que o leitor do texto MEDIU e nao cabe no valor nem na
-- base — a especie (CAMPO/EVENTO/MERCADO), a precisao, se a data do facto foi
-- CALCULADA a partir da publicacao (D63) e a expressao com a conta. UMA coluna
-- JSON, e nao seis de texto, pela razao da `janela_declarada`: cada leitura e
-- um registo, e seis colunas soltas deitavam fora de onde veio cada uma.
-- Default = `admissao.TEMPO_LUGAR_EVIDENCIA_NAO_MEDIDA`, byte a byte.
alter table public.sala_de_espera
  add column if not exists tempo_lugar_evidencia json not null
  default '{"FACT_LOCATION_KIND": "NAO SEI", "FACT_LOCATION_PRECISION": "NAO SEI", "FACT_LOCATION_VEIO_DE": "NAO SEI", "FACT_TIME_CALCULO": "NAO SEI", "FACT_TIME_EVIDENCIA": "NAO SEI", "FACT_TIME_KIND": "NAO SEI", "FACT_TIME_PRECISION": "NAO SEI", "FACT_TIME_VEIO_DE": "NAO SEI", "LEITOR": "NAO SEI", "ORIGEM": "pousado antes da migration 033: a evidencia do tempo e do lugar nao foi medida"}'::json;

comment on column public.sala_de_espera.published_at_basis is
  'Como se sabe o PUBLISHED_AT (JSON-LD, meta tag, edicao impressa...), ou porque '
  'NAO se sabe. PUBLISHED_AT != FACT_TIME.';
comment on column public.sala_de_espera.source_location_basis is
  'Como se sabe onde esta quem publica (o contrato de fonte), ou porque NAO se sabe. '
  'SOURCE_LOCATION != FACT_LOCATION. O REGION do Atlas NAO e sede.';
comment on column public.sala_de_espera.completude_tempo_lugar is
  'D62: PROVADA / CALCULADA / NAO SEI para publicacao, lugar da fonte, data e lugar '
  'do facto. Nao barra nada. Dono: admissao.completude_tempo_lugar().';
comment on column public.sala_de_espera.tempo_lugar_evidencia is
  'DA-7: especie, precisao, CALCULO e evidencia da leitura do tempo e do lugar do '
  'facto (leis/fato_do_texto.py). A base continua na coluna _basis.';

-- ── B · as quatro chaves (referência provada da nuvem, tal e qual) ──────
alter table public.sala_de_espera
  add column if not exists janela_declarada json not null
  default '{"CULTURA": {"BASE": "NAO SEI", "VALOR": "NAO SEI", "VEIO_DE": "NAO SEI"}, "FASE": {"BASE": "NAO SEI", "VALOR": "NAO SEI", "VEIO_DE": "NAO SEI"}, "JANELA": {"BASE": "NAO SEI", "VALOR": "NAO SEI", "VEIO_DE": "NAO SEI"}, "ORIGEM": {"PORQUE": "pousado antes da migration 033: as quatro chaves nao foram medidas"}, "PRECISAO": {"CHAVES_COM_VALOR": "NAO SEI", "FACT_TIME": "NAO SEI", "PUBLISHED_AT": "NAO SEI"}, "REGIAO_DO_FATO": {"BASE": "NAO SEI", "VALOR": "NAO SEI", "VEIO_DE": "NAO SEI"}, "TEMPO_RELATIVO": {"CONTA": "NAO SEI", "EXPRESSOES": "NAO SEI", "VEIO_DE": "NAO SEI"}}'::json;

-- ── A FORMA, E SÓ A FORMA ────────────────────────────────────────────────
-- As quatro chaves estão SEMPRE lá, e cada uma diz o VALOR, de onde VEIO e a
-- BASE. Ausência escreve-se — `"NAO SEI"` —, nunca se omite.
-- ⚠️ A TRAVA NÃO JULGA O CONTEÚDO, e não pode proibir REGIAO_DO_FATO =
-- source_location (o fato de um boletim do Veneto pode mesmo ser no Veneto).
-- A lei «a região da fonte não vira região do fato» vive no dono.
do $$
begin
  if not exists (select 1 from pg_constraint
                 where conname = 'janela_declara_as_quatro_chaves') then
    alter table public.sala_de_espera
      add constraint janela_declara_as_quatro_chaves
      check (
        json_typeof(janela_declarada) = 'object'
        and coalesce((janela_declarada::jsonb #> '{CULTURA,VALOR}')
                     not in ('null'::jsonb, '""'::jsonb, '[]'::jsonb), false)
        and coalesce((janela_declarada::jsonb #> '{REGIAO_DO_FATO,VALOR}')
                     not in ('null'::jsonb, '""'::jsonb, '[]'::jsonb), false)
        and coalesce((janela_declarada::jsonb #> '{FASE,VALOR}')
                     not in ('null'::jsonb, '""'::jsonb, '[]'::jsonb), false)
        and coalesce((janela_declarada::jsonb #> '{JANELA,VALOR}')
                     not in ('null'::jsonb, '""'::jsonb, '[]'::jsonb), false)
        and (janela_declarada::jsonb #> '{CULTURA}')        ?& array['VEIO_DE', 'BASE']
        and (janela_declarada::jsonb #> '{REGIAO_DO_FATO}') ?& array['VEIO_DE', 'BASE']
        and (janela_declarada::jsonb #> '{FASE}')           ?& array['VEIO_DE', 'BASE']
        and (janela_declarada::jsonb #> '{JANELA}')         ?& array['VEIO_DE', 'BASE']
      );
  end if;
end $$;

comment on column public.sala_de_espera.janela_declarada is
  'As quatro chaves (cultura, regiao do FATO, fase, janela), cada uma com VALOR, '
  'VEIO_DE e BASE. Dono: admissao.janela_declarada() (linha quatro-chaves).';

-- ── C · a gaveta extra do REROUTE (vazia; D66: ninguém a escreve ainda) ──
create table if not exists public.sala_de_espera_gaveta (
  run_id      text    not null,
  ordem       integer not null,
  universo    text    not null,
  origem      text    not null,
  pontuacao   integer not null check (pontuacao > 0),
  motivo      text    not null,
  decidido_em timestamptz not null default now(),
  primary key (run_id, ordem, universo),
  foreign key (run_id, ordem) references public.sala_de_espera (run_id, ordem)
    on delete restrict,
  check (universo <> origem)
);

comment on table public.sala_de_espera_gaveta is
  'REROUTE: a gaveta onde o item TAMBEM mora, sem texto e sem bytes. D66: vazia '
  'ate o dono decidir que o REROUTE entra na Sala.';

-- ── D · as revisões — SÓ ACRESCENTA ──────────────────────────────────────
create table if not exists public.sala_de_espera_revisao (
  run_id             text        not null,
  ordem              integer     not null,
  campo              text        not null,
  revisao            integer     not null check (revisao >= 1),
  valor              text        not null,
  base               text        not null,
  extrator           text        not null,
  versao_do_extrator text        not null,
  revisto_em         timestamptz not null default now(),
  motivo             text        not null,
  primary key (run_id, ordem, campo, revisao),
  foreign key (run_id, ordem) references public.sala_de_espera (run_id, ordem)
    on delete restrict,
  -- Só os campos de tempo, lugar, completude e chaves se revêem. O texto, a
  -- fonte, a identidade e a fila NÃO: são o que pousou, e a assinatura é deles.
  constraint revisao_so_de_campo_revisivel check (campo in (
    'published_at', 'source_location', 'fact_time', 'fact_location',
    'observed_at', 'completude_tempo_lugar', 'janela_declarada',
    'tempo_lugar_evidencia')),
  -- Ausência escreve-se «NAO SEI», nunca vazio.
  constraint revisao_valor_e_base_nao_vazios check (
    length(btrim(valor)) > 0 and length(btrim(base)) > 0),
  constraint revisao_diz_quem_e_porque check (
    length(btrim(extrator)) > 0 and length(btrim(versao_do_extrator)) > 0
    and length(btrim(motivo)) > 0)
);

comment on table public.sala_de_espera_revisao is
  'Correcoes de campos da Sala, SO ACRESCENTA (trigger recusa UPDATE/DELETE/TRUNCATE). '
  'Escritor unico: admissao/sala_de_espera.py::rever. Leitura: sala_de_espera_atual.';

create or replace function public.sala_de_espera_revisao_so_acrescenta()
returns trigger language plpgsql as $$
begin
  raise exception 'SALA_REVISAO_SO_ACRESCENTA: % recusado em sala_de_espera_revisao. '
    'Uma revisao nao se edita nem se apaga: escreve-se outra.', tg_op;
end $$;

do $$
begin
  if not exists (select 1 from pg_trigger
                 where tgname = 'sala_de_espera_revisao_nao_muda') then
    create trigger sala_de_espera_revisao_nao_muda
      before update or delete on public.sala_de_espera_revisao
      for each row execute function public.sala_de_espera_revisao_so_acrescenta();
  end if;
  if not exists (select 1 from pg_trigger
                 where tgname = 'sala_de_espera_revisao_nao_esvazia') then
    create trigger sala_de_espera_revisao_nao_esvazia
      before truncate on public.sala_de_espera_revisao
      for each statement execute function public.sala_de_espera_revisao_so_acrescenta();
  end if;
end $$;

-- ── A VISTA: o valor atual = a última revisão, senão o original ─────────
create or replace view public.sala_de_espera_atual as
select s.run_id, s.ordem, s.item_id, s.raw_observation_id, s.universo, s.texto,
       s.source_id,
       coalesce(sl.valor, s.source_location)              as source_location,
       coalesce(sl.base,  s.source_location_basis)        as source_location_basis,
       coalesce(fl.valor, s.fact_location)                as fact_location,
       coalesce(fl.base,  s.fact_location_basis)          as fact_location_basis,
       coalesce(ft.valor, s.fact_time)                    as fact_time,
       coalesce(ft.base,  s.fact_time_basis)              as fact_time_basis,
       coalesce(pa.valor, s.published_at)                 as published_at,
       coalesce(pa.base,  s.published_at_basis)           as published_at_basis,
       coalesce(oa.valor, s.observed_at)                  as observed_at,
       coalesce(co.valor::json, s.completude_tempo_lugar) as completude_tempo_lugar,
       coalesce(jd.valor::json, s.janela_declarada)       as janela_declarada,
       coalesce(te.valor::json, s.tempo_lugar_evidencia)  as tempo_lugar_evidencia,
       s.captured_at, s.admitido_por, s.corrida_sha256, s.estagio,
       s.source_declared_evidence_class, s.fato,
       s.estado_da_fila, s.pousado_em, s.consumido_em, s.consumido_por,
       (select count(*) from public.sala_de_espera_revisao r
         where r.run_id = s.run_id and r.ordem = s.ordem)  as revisoes
  from public.sala_de_espera s
  left join lateral (select valor, base from public.sala_de_espera_revisao r
                      where r.run_id = s.run_id and r.ordem = s.ordem
                        and r.campo = 'source_location'
                      order by r.revisao desc limit 1) sl on true
  left join lateral (select valor, base from public.sala_de_espera_revisao r
                      where r.run_id = s.run_id and r.ordem = s.ordem
                        and r.campo = 'fact_location'
                      order by r.revisao desc limit 1) fl on true
  left join lateral (select valor, base from public.sala_de_espera_revisao r
                      where r.run_id = s.run_id and r.ordem = s.ordem
                        and r.campo = 'fact_time'
                      order by r.revisao desc limit 1) ft on true
  left join lateral (select valor, base from public.sala_de_espera_revisao r
                      where r.run_id = s.run_id and r.ordem = s.ordem
                        and r.campo = 'published_at'
                      order by r.revisao desc limit 1) pa on true
  left join lateral (select valor, base from public.sala_de_espera_revisao r
                      where r.run_id = s.run_id and r.ordem = s.ordem
                        and r.campo = 'observed_at'
                      order by r.revisao desc limit 1) oa on true
  left join lateral (select valor, base from public.sala_de_espera_revisao r
                      where r.run_id = s.run_id and r.ordem = s.ordem
                        and r.campo = 'completude_tempo_lugar'
                      order by r.revisao desc limit 1) co on true
  left join lateral (select valor, base from public.sala_de_espera_revisao r
                      where r.run_id = s.run_id and r.ordem = s.ordem
                        and r.campo = 'janela_declarada'
                      order by r.revisao desc limit 1) jd on true
  left join lateral (select valor, base from public.sala_de_espera_revisao r
                      where r.run_id = s.run_id and r.ordem = s.ordem
                        and r.campo = 'tempo_lugar_evidencia'
                      order by r.revisao desc limit 1) te on true;

comment on view public.sala_de_espera_atual is
  'O que a Intelligence le: cada campo revisivel = a ultima revisao, senao o valor '
  'original. A linha original de sala_de_espera NUNCA muda.';
