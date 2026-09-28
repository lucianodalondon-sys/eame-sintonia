-- ═══════════════════════════════════════════════════════════════════════
-- DESFAZER da 038 · a_sala_mostra_cada_item_em_cada_gaveta
--
-- FORA de `supabase/migrations/` de propósito: a cadeia aplica todo `*.sql`
-- de lá, e um desfazer ali dentro correria logo a seguir ao fazer.
--
-- Só tira a VISTA. As gavetas (`sala_de_espera_gaveta`, 033) e as linhas de
-- `sala_de_espera` não são tocadas.
--
--     psql -X -v ON_ERROR_STOP=1 --single-transaction -f supabase/desfazer/038_desfazer.sql <DSN>
-- ═══════════════════════════════════════════════════════════════════════

drop view if exists public.sala_de_espera_por_gaveta;

delete from public.schema_migracao where versao = '038';
