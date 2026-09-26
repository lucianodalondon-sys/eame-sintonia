-- ═══════════════════════════════════════════════════════════════════════
-- 035 · O ACERVO GUARDA O TEMPO E O LUGAR COMO DERIVADO — PROPOSTA
--
-- D79 (coordenador, 26/09 03:45): nasceu 034; passa a 035 porque a 034 é a LÁPIDE da retenção do
-- YouTube (`034_a_lapide_da_retencao.sql`). Ensaiadas as duas juntas, numa cópia da Sala.
--
-- ACERVO-TEMPO-LUGAR (26/09/2026). ⚠️ PROPOSTA: a decisão de aplicar é do
-- coordenador/dono. Testada só em Postgres DESCARTÁVEL (ver o relatório).
--
-- O PROBLEMA. A 033 deu casa ao tempo e ao lugar das linhas da SALA (revisões).
-- Mas o armazém tem muito mais do que a Sala: medido em 26/09, 1.562 linhas de
-- raw_asset, e só 94 linhas na Sala. O que o extractor instalado diz sobre o
-- RESTO — data de publicação, lugar da fonte, data e lugar do facto — não tem
-- onde ficar: não há linha de Sala para rever, e o RAW NÃO SE ALTERA.
--
-- A CASA QUE JÁ EXISTE. `derived_artifact` é exatamente a coisa que nasce de um
-- RAW, com pai declarado (raw_asset_id + parent_sha256, conferidos pela chave
-- estrangeira), produtor, versão do produtor, parâmetros e o sha256 dos bytes.
-- E já é idempotente: `derivacao_e_unica_por_regua` não deixa a mesma régua
-- produzir duas vezes o mesmo filho.
--
-- O QUE FALTA É UMA PALAVRA. `derived_artifact_kind_check` é um vocabulário
-- FECHADO (7 espécies) e nenhuma é «tempo e lugar». Usar TABLE_EXTRACTION ou
-- TEXT_EXTRACTION para isto seria mentir sobre a espécie do filho.
--
--     TEMPO_LUGAR = um JSON com os quatro campos do contrato comum, cada um com
--     a sua BASE (PUBLISHED_AT, SOURCE_LOCATION, FACT_TIME, FACT_LOCATION), a
--     evidência do extractor e a proveniência (livro do coletor, texto usado).
--     O filho de um RAW. Nunca o substitui; nunca o altera.
--
-- ADITIVA NO SIGNIFICADO: o vocabulário só GANHA uma palavra; nenhuma linha
-- existente muda, nenhuma deixa de passar. Tecnicamente é DROP + ADD da mesma
-- restrição (Postgres não alarga um CHECK no lugar), dentro de UMA transação.
-- ═══════════════════════════════════════════════════════════════════════

alter table public.derived_artifact drop constraint derived_artifact_kind_check;
alter table public.derived_artifact add constraint derived_artifact_kind_check
  check (kind = any (array['TEXT_EXTRACTION', 'OCR', 'TRANSCRIPTION', 'TRANSLATION',
                           'THUMBNAIL', 'FRAME', 'TABLE_EXTRACTION', 'TEMPO_LUGAR']));

comment on constraint derived_artifact_kind_check on public.derived_artifact is
  'Vocabulario fechado das especies de derivado. TEMPO_LUGAR (035): JSON com os quatro '
  'campos de tempo/lugar do contrato comum, cada um com a base, filho de um RAW; nunca '
  'o altera. UNKNOWN nao funde nem vira facto: NAO SEI fica NAO SEI com o porque.';
