-- 038 · A SALA GUARDA O PRECO DECLARADO (myfruit, 28/09). APROVADA PELO DONO (28/09) e PROMOVIDA A
-- MIGRATION: aplicada pela cadeia canonica e anotada no livro-razao `schema_migracao` com o sha256
-- deste ficheiro. A trava dos oito campos de `sala_de_espera` nao foi tocada.
--
-- PORQUE: o item do myfruit precisa de um LUGAR para o preco. A cadeia do canario e: criar o lugar ->
-- reprocessar o mesmo item -> nova leitura com prova -> a Inteligencia consome -> novo pacote -> o portal
-- mostra o preco.
--
-- PORQUE NAO NO CADERNO DE REVISOES DA 033 (medido, e a MESMA resposta que a 036 e a 037 ja deram):
-- o caderno aceita uma lista FECHADA de campos (`revisao_so_de_campo_revisivel`: tempo, lugar,
-- completude, chaves) e o preco nao e nenhum deles. Alargar a lista seria TROCAR UMA TRAVA, e obrigaria a
-- um `drop constraint` + `add constraint` numa migracao nova — o contrario do que a 033 e a 036 fazem
-- (so CREATE). E ha uma segunda razao, de sentido: a revisao de um campo e uma CORRECCAO do valor que
-- ja pousou (o caderno compara com o valor atual e guarda `base`); o preco nao corrige nada — e uma
-- LEITURA NOVA do mesmo item, com prova propria. Usar o caderno de correcoes como canal de entrada era
-- misturar duas coisas com nomes parecidos.
--
-- PORQUE NAO DENTRO DOS JSON QUE JA EXISTEM NA SALA: `fato`, `source_declared_evidence_class` (a
-- especie), `janela_declarada` e `tempo_lugar_evidencia` dizem OUTRA coisa. Por o preco la dentro era
-- misturar.
--
-- PORQUE NAO EM `mercado_observacao` (021): essa e a tabua da SERIE (cultura x praca x periodo, com
-- classe temporal e `o_que_nao_prova`), escrita pelo lastmile (`pacote/lastmile_para_supabase.py`) e
-- SEM ligacao ao item da Sala nem ao ficheiro original. O preco que aqui entra e o do ITEM: o que o
-- documento que pousou diz, com o RAW e o trecho de onde saiu.
--
--     UMA E A SERIE. A OUTRA E A PROVA. NAO SAO O MESMO LUGAR, E NENHUMA DAS DUAS E COPIA DA OUTRA.
--
-- O QUE FAZ: uma tabela AO LADO (como a gaveta da 033 e a proposta 037) — NENHUMA coluna nova em
-- `sala_de_espera`, nenhuma linha existente tocada, nenhuma trava existente mudada. So acrescenta.
--
--   · uma linha por PRECO LIDO de um item da Sala. AUSENCIA NAO GERA LINHA: o que nao foi lido nao vira
--     preco, e a regra do formato recusa «NAO SEI» como valor (como a 037 recusa identidade UNKNOWN).
--   · `valor_texto` LITERAL, tal e qual como a fonte publica («€237,00»): converter cedo perde a virgula
--     decimal italiana e inventa zero (lei medida na 021, no EC Agri-food Data Portal). `valor_numerico`
--     e o NOSSO parse e pode ser NULL — o literal nao depende dele.
--   · `classe` CURRENT / OUTLOOK / HISTORICAL obrigatoria (lei n.o 1 da 021: o demo mostrou azeite de
--     Salerno a «€630» como preco corrente, e a cotacao era de 2015).
--   · `nivel` DECLARADO, e `praca` obrigatoria quando o nivel e PIAZZA (lei n.o 2: praça nao e regiao;
--     cinco documentos provinciais nao sao «a Campania»).
--   · `prova` traz o `RAW_SHA256` (obrigatorio: os bytes existem sempre) e o `DOCUMENT_ID` QUANDO a
--     fonte o consegue provar. Sem prova de identidade, `DOCUMENT_ID` escreve-se «NAO SEI» — a lei de
--     identidade proibe fabrica-lo com URL, slug, sha ou nome de ficheiro.
--   · `citacao_literal` e `o_que_nao_prova` obrigatorios: o trecho de onde o preco saiu, e o que ele NAO
--     prova. A 021 chama a isto «a unica tabela onde a tentacao e automatica» — aqui a tentacao e a mesma.
--   · so acrescenta: UPDATE / DELETE / TRUNCATE recusados (como as revisoes da 033 e a 037).
--   · `sala_de_espera_precos` (VISTA): o que a Inteligencia le — `(run_id, ordem)`, `RAW_SHA256`,
--     `DOCUMENT_ID`, o valor LITERAL e a unidade. Sem a vista, o preco grava e ninguem o ve: e
--     exatamente o que aconteceria se so a trava e o codigo fossem mudados.
--
-- ONDE ESTA: supabase/migrations/038_a_sala_guarda_o_preco.sql — aplicada pela cadeia canonica
-- (`motor/cadeia_canonica.sh migrations <DSN>`), que a anota no livro-razao `schema_migracao` com o
-- sha256 do ficheiro. DESFAZER: supabase/desfazer/038_desfazer.sql.
-- ENSAIO: provas/migracao_038_ensaio_descartavel.py. NUMERO: 038 porque a 037 esta RESERVADA
-- (proposta do video, MAESTRO-SOCIAL, 26/09).

create table if not exists public.sala_de_espera_preco (
  id                 bigserial   primary key,
  run_id             text        not null,
  ordem              integer     not null,
  indicador          text        not null,
  cultura_literal    text        not null,
  nivel              text        not null,
  praca              text,
  valor_texto        text        not null,
  valor_numerico     numeric,
  unidade            text        not null,
  periodo_inicio     date        not null,
  periodo_fim        date        not null,
  classe             text        not null,
  citacao_literal    text        not null,
  o_que_nao_prova    text        not null,
  prova              jsonb       not null,
  registado_em       timestamptz not null default now(),
  foreign key (run_id, ordem) references public.sala_de_espera (run_id, ordem)
    on delete restrict,
  -- O indicador diz o que a linha e. «Outlook» nao e preco corrente: e o que a fonte espera, e a classe
  -- temporal e que o separa.
  constraint preco_e_de_um_indicador check (indicador in ('PRECO', 'CUSTO', 'OUTLOOK')),
  constraint preco_e_das_tres_classes check (classe in ('CURRENT', 'OUTLOOK', 'HISTORICAL')),
  constraint preco_declara_o_nivel check (nivel in ('PIAZZA', 'NACIONAL', 'REGIAO')),
  -- Ausencia escreve-se AUSENCIA DE LINHA, nunca «NAO SEI» com valor.
  constraint preco_nao_se_inventa_o_que_nao_se_leu check (
    length(btrim(valor_texto)) > 0 and valor_texto <> 'NAO SEI'),
  constraint preco_diz_a_unidade check (length(btrim(unidade)) > 0),
  constraint preco_traz_o_trecho check (length(btrim(citacao_literal)) > 0),
  constraint preco_diz_o_que_nao_prova check (length(btrim(o_que_nao_prova)) > 0),
  constraint preco_nao_vem_do_vazio check (periodo_fim >= periodo_inicio),
  constraint praca_obrigatoria_no_nivel_piazza check (
    nivel <> 'PIAZZA' or (praca is not null and length(btrim(praca)) > 0)),
  -- A PROVA: os bytes. O DOCUMENT_ID nao se exige aqui (a lei de identidade so o admite quando a fonte
  -- o prova); o que se exige e que a prova seja um objeto e traga o sha dos bytes de origem.
  constraint prova_traz_o_raw_sha256 check (
    jsonb_typeof(prova) = 'object' and prova ? 'RAW_SHA256'
    and prova ->> 'RAW_SHA256' ~ '^[0-9a-f]{64}$'),
  constraint prova_diz_onde_esta check (
    prova ? 'ONDE' and length(btrim(prova ->> 'ONDE')) > 0),
  -- Um preco, uma vez: reprocessar o mesmo item com o mesmo codigo nao escreve segunda linha.
  -- O nome e EXPLICITO porque o escritor o cita no `on conflict` — uma chave sem nome obrigaria o
  -- banco a adivinhar por que colunas se resolve.
  constraint preco_do_item_uma_vez unique nulls not distinct (
    run_id, ordem, indicador, cultura_literal, praca, periodo_inicio, periodo_fim)
);

create index if not exists sala_de_espera_preco_por_item_idx
  on public.sala_de_espera_preco (run_id, ordem);

comment on table public.sala_de_espera_preco is
  'O preco que o documento de cada item da Sala DECLARA, com a prova (RAW_SHA256, DOCUMENT_ID quando '
  'provado) e o trecho literal. Ausencia nao tem linha. So acrescenta. Escritor: '
  'admissao/preco_na_sala.py. Leitura: sala_de_espera_precos. Migration 038.';
comment on column public.sala_de_espera_preco.valor_texto is
  'O que a fonte publica, LITERAL («€237,00»). Converter cedo perde a virgula decimal italiana e '
  'inventa zero — o parse e o valor_numerico, e nao substitui este campo.';
comment on column public.sala_de_espera_preco.o_que_nao_prova is
  'O que este preco NAO prova (preco de piazza nao e preco nacional; preco nao e lucro). Obrigatorio, '
  'como na 021.';

-- ── SO ACRESCENTA: o que foi lido nao se edita nem se apaga ─────────────────
create or replace function public.sala_de_espera_preco_so_acrescenta()
returns trigger language plpgsql as $$
begin
  raise exception 'SALA_PRECO_SO_ACRESCENTA: % recusado em sala_de_espera_preco. '
    'O preco e o que o documento diz naquele item: nao se edita nem se apaga.', tg_op;
end $$;

do $$
begin
  if not exists (select 1 from pg_trigger
                 where tgname = 'sala_de_espera_preco_nao_muda') then
    create trigger sala_de_espera_preco_nao_muda
      before update or delete on public.sala_de_espera_preco
      for each row execute function public.sala_de_espera_preco_so_acrescenta();
  end if;
  if not exists (select 1 from pg_trigger
                 where tgname = 'sala_de_espera_preco_nao_esvazia') then
    create trigger sala_de_espera_preco_nao_esvazia
      before truncate on public.sala_de_espera_preco
      for each statement execute function public.sala_de_espera_preco_so_acrescenta();
  end if;
end $$;

-- ── A VISTA: o que a Inteligencia le (o elo sem isto nao existe) ────────────
create or replace view public.sala_de_espera_precos as
select p.run_id, p.ordem, p.indicador, p.cultura_literal, p.nivel, p.praca,
       p.valor_texto, p.valor_numerico, p.unidade,
       p.periodo_inicio, p.periodo_fim, p.classe,
       p.citacao_literal, p.o_que_nao_prova,
       p.prova ->> 'RAW_SHA256'                             as raw_sha256,
       coalesce(p.prova ->> 'DOCUMENT_ID', 'NAO SEI')       as document_id,
       p.prova ->> 'ONDE'                                   as prova_onde,
       s.item_id, s.universo, s.source_id, s.estado_da_fila,
       p.registado_em
  from public.sala_de_espera_preco p
  join public.sala_de_espera s
    on s.run_id = p.run_id and s.ordem = p.ordem;

comment on view public.sala_de_espera_precos is
  'O preco de cada item da Sala com a prova: (run_id, ordem), RAW_SHA256, DOCUMENT_ID, o valor LITERAL '
  'e a unidade. E por aqui que a Inteligencia o consome e o mapeia para PRICE/UNIT. A linha original '
  'de sala_de_espera NUNCA muda.';
