-- ═══════════════════════════════════════════════════════════════════════
-- DESFAZER da 036 · a_sala_guarda_as_versoes_do_documento
--
-- FORA de `supabase/migrations/` de propósito: a cadeia aplica todo `*.sql`
-- de lá, e um desfazer ali dentro correria logo a seguir ao fazer.
--
-- ⚠️ ISTO APAGA AS VERSÕES. Antes de o correr na Sala real: backup
-- (`backup_sala.cmd`). As linhas de `sala_de_espera` não são tocadas.
--
--     psql -X -v ON_ERROR_STOP=1 --single-transaction -f supabase/desfazer/036_desfazer.sql <DSN>
-- ═══════════════════════════════════════════════════════════════════════

drop trigger if exists sala_de_espera_versao_nao_muda on public.sala_de_espera_versao;
drop trigger if exists sala_de_espera_versao_nao_esvazia on public.sala_de_espera_versao;
drop table if exists public.sala_de_espera_versao;
drop function if exists public.sala_de_espera_versao_so_acrescenta();

delete from public.schema_migracao where versao = '036';
