-- ═══════════════════════════════════════════════════════════════════════
-- 038 · A SALA MOSTRA CADA ITEM EM CADA GAVETA — SÓ UMA VISTA (REROUTE-D56)
--
-- NÃO EXECUTADA NA SALA REAL. Preparada e ensaiada em Postgres DESCARTÁVEL
-- (tests/test_reroute_d56.py). O número é 038 porque a 037 já está tomada pela
-- proposta do MAESTRO-SOCIAL (`supabase/propostas/037_*`).
--
-- D56 (bot Luciano, 25/09 09:05): «se o item der SIM em vários universos, UM item
-- canónico ligado a TODAS as gavetas aprovadas (sem duplicar bytes nem
-- proveniência), com pontuação e motivo de cada decisão.»
--
-- A CASA JÁ EXISTIA: a 033 criou `sala_de_espera_gaveta` (secção C) e deixou-a
-- vazia (D66). Quem passa a escrever nela é `admissao/sala_de_espera.py::pousar`
-- (escritor único), com as gavetas que `admissao.gavetas_para_a_sala()` monta.
-- O que faltava era o LEITOR poder perguntar «o que há na gaveta T3?» sem saber
-- que há duas tabelas. É só isso que esta vista faz:
--
--     uma linha por (item, gaveta): a gaveta da LINHA (papel LINHA, a coluna
--     `universo` de sempre) e cada gaveta extra (papel REROUTE, da 033 C).
--
-- `sala_de_espera_atual` NÃO MUDA: continua uma linha por item, e quem a lê hoje
-- lê o mesmo amanhã. O texto, a proveniência e os bytes vêm pela (run_id, ordem)
-- da linha — nunca copiados para a gaveta.
--
-- Só CREATE VIEW. Nada existente é alterado, nenhuma linha é escrita.
-- DESFAZER: supabase/desfazer/038_desfazer.sql (fora desta pasta de propósito).
--
--     DESIGNED = YES · DB_TESTED = YES (Postgres 16 descartável) · LIVE = NO
-- ═══════════════════════════════════════════════════════════════════════

create or replace view public.sala_de_espera_por_gaveta as
select a.run_id, a.ordem, a.item_id, a.raw_observation_id,
       a.universo           as gaveta,
       a.universo           as universo_da_linha,
       'LINHA'::text        as papel,
       null::integer        as pontuacao,
       a.admitido_por       as motivo,
       a.source_id, a.estado_da_fila, a.pousado_em
  from public.sala_de_espera_atual a
union all
select a.run_id, a.ordem, a.item_id, a.raw_observation_id,
       g.universo           as gaveta,
       a.universo           as universo_da_linha,
       'REROUTE'::text      as papel,
       g.pontuacao,
       g.motivo,
       a.source_id, a.estado_da_fila, a.pousado_em
  from public.sala_de_espera_gaveta g
  join public.sala_de_espera_atual a
    on a.run_id = g.run_id and a.ordem = g.ordem;

comment on view public.sala_de_espera_por_gaveta is
  'D56: uma linha por (item, gaveta). LINHA = a coluna universo da Sala; REROUTE = '
  'sala_de_espera_gaveta (033 C). O texto e a proveniencia vem de sala_de_espera_atual '
  'pela (run_id, ordem). Escritor das gavetas: admissao/sala_de_espera.py::pousar.';
