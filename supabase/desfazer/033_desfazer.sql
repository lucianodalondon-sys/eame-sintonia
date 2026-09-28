-- ═══════════════════════════════════════════════════════════════════════
-- DESFAZER da 033 · a_sala_guarda_a_base_as_chaves_e_as_revisoes
--
-- FORA de `supabase/migrations/` de propósito: a cadeia aplica todo `*.sql`
-- de lá, e um desfazer ali dentro correria logo a seguir ao fazer.
--
-- ⚠️ ISTO APAGA AS REVISÕES. Antes de o correr na Sala real, o roteiro manda
-- fazer backup (`backup_sala.cmd`); o caminho de volta completo é o restauro
-- desse backup. Este ficheiro repõe o ESQUEMA da 032.
--
-- Corre numa transação só:
--     psql -X -v ON_ERROR_STOP=1 --single-transaction -f supabase/desfazer/033_desfazer.sql <DSN>
-- ═══════════════════════════════════════════════════════════════════════

-- REROUTE-D56 (28/09): a vista da 038 le `sala_de_espera_atual` e `sala_de_espera_gaveta`;
-- desfazer a 033 leva-a primeiro (sem ela o drop da vista abaixo e recusado).
drop view if exists public.sala_de_espera_por_gaveta;
delete from public.schema_migracao where versao = '038';

drop view if exists public.sala_de_espera_atual;

drop trigger if exists sala_de_espera_revisao_nao_muda on public.sala_de_espera_revisao;
drop trigger if exists sala_de_espera_revisao_nao_esvazia on public.sala_de_espera_revisao;
drop table if exists public.sala_de_espera_revisao;
drop function if exists public.sala_de_espera_revisao_so_acrescenta();

drop table if exists public.sala_de_espera_gaveta;

alter table public.sala_de_espera drop constraint if exists janela_declara_as_quatro_chaves;
alter table public.sala_de_espera drop column if exists janela_declarada;
alter table public.sala_de_espera drop column if exists completude_tempo_lugar;
alter table public.sala_de_espera drop column if exists tempo_lugar_evidencia;
alter table public.sala_de_espera drop column if exists source_location_basis;
alter table public.sala_de_espera drop column if exists published_at_basis;

-- o livro-razão da cadeia: sem isto, a cadeia daria SKIP a uma 033 que já não existe
delete from public.schema_migracao where versao = '033';
