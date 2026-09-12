-- ═══════════════════════════════════════════════════════════════════════
-- 028 · A ETAPA RAW APONTA PARA A OBSERVAÇÃO — uma coluna, e nem uma a mais
--
-- A 024 deu à coleta o seu rastro: `etapa_da_corrida`, UMA linha por passagem,
-- com contagens, grão e contabilidade fechada pelo banco. DERIVED, STRUCTURED
-- e ADMISSION falam por lá desde então.
--
-- A etapa RAW estava no vocabulário (`telemetria.ETAPAS_DA_COLETA` já a
-- nomeia, e `diagnostico.da_etapa('RAW', ...)` já lhe dá código), corria, e
-- era MUDA. Medido em `system-map/data/buracos.generated.json`:
--
--     RAW_FORWARD_NAO_EMITE
--     "guarda/preservar_coleta.py escreve `raw_asset` e nao emite rastro"
--
-- E DERIVED declarava `edge_from = 'RAW'` — uma aresta cujo topo de cima não
-- tinha linha nenhuma. A seta estava desenhada dos dois lados e só um lado
-- existia.
--
--     UMA ETAPA QUE PERSISTE MAS NÃO EMITE RASTRO EXISTE NO BANCO
--     E NÃO EXISTE PARA A RECONCILIAÇÃO OPERACIONAL.
--
-- ── POR QUE UMA COLUNA, E NÃO UM SEGUNDO LIVRO ────────────────────────────
--
-- O dono do rastro já existe (`medidas/rastro_da_coleta.py`) e o vocabulário
-- já tem RAW. Não falta owner, não falta estado, não falta etapa. O que falta
-- é UMA correlação: a linha da passagem consegue nomear a corrida e a fonte,
-- e não consegue nomear a OBSERVAÇÃO que ela produziu.
--
--     run_id          nomeia a CORRIDA
--     source_id       nomeia a FONTE
--     last_good_artifact  é um ENDEREÇO, e endereço não é identidade
--
-- Sem esta coluna, «que observação é que esta passagem produziu?» só se
-- responde por `raw_asset.run_id` — correlação ao nível da CORRIDA. Basta
-- para uma corrida de uma observação, e deixa de bastar exatamente quando a
-- coleta cresce, que é quando o rastro passa a ser necessário.
--
-- Criar um `raw-ledger` ao lado responderia a mesma pergunta com um segundo
-- dono. DOIS DONOS DA MESMA PERGUNTA SÃO DUAS RESPOSTAS À ESPERA DE DIVERGIR.
--
-- ── O QUE ESTA COLUNA NÃO É ───────────────────────────────────────────────
--
--     NÃO é a observação      `raw_asset` continua o dono dela
--     NÃO é o sha256          esse identifica BYTES
--     NÃO é o storage_path    esse é endereço físico
--     NÃO é obrigatória       uma passagem que produziu N != 1 observações
--                             deixa-a NULL, e as CONTAGENS dizem a verdade
--
-- Ela é NULLABLE de propósito. Uma passagem RAW que não produziu observação
-- nenhuma (nada a preservar, ou falha antes de persistir) NÃO PODE apontar
-- para uma — e inventar-lhe um alvo seria escrever um sucesso que não houve.
--
--     ON DELETE CASCADE porque a linha do rastro fala DAQUELA observação: se
--     a observação desaparecer, a passagem que a nomeia deixa de ter sujeito.
-- ═══════════════════════════════════════════════════════════════════════

alter table public.etapa_da_corrida
  add column raw_asset_id bigint
    references public.raw_asset(id) on delete cascade;

-- Só a etapa RAW produz observação bruta. Uma linha de DERIVED, STRUCTURED ou
-- ADMISSION que apontasse para `raw_asset` estaria a dizer que ELA a produziu,
-- e não produziu — quem a produziu foi a passagem anterior.
--
--     APONTAR PARA O ARTEFATO DE OUTRA ETAPA É ASSINAR O TRABALHO DELA.
alter table public.etapa_da_corrida
  add constraint so_o_raw_nomeia_a_observacao
    check (raw_asset_id is null or etapa = 'RAW');

create index etapa_raw_observacao_idx
  on public.etapa_da_corrida (raw_asset_id)
  where raw_asset_id is not null;

comment on column public.etapa_da_corrida.raw_asset_id is
  'A OBSERVACAO que esta passagem RAW produziu, quando produziu exatamente '
  'uma. NULL quando nenhuma (nada a preservar, ou falha antes de persistir) '
  'ou quando N > 1 — nesse caso as contagens e `run_id` carregam a verdade. '
  'Nunca e o sha256, nunca e o storage_path: a observacao tem id proprio.';
