-- ═══════════════════════════════════════════════════════════════════════
-- DESFAZER da 035 · o_acervo_guarda_tempo_e_lugar_como_derivado
--
-- FORA de `supabase/migrations/` de propósito (a cadeia aplica todo `*.sql` de lá).
--
-- ⚠️ NÃO APAGA DERIVADOS. Se já existir algum derivado TEMPO_LUGAR, o
-- vocabulário antigo não o aceita, e este desfazer RECUSA-SE a correr: apagar
-- filhos do acervo não é «desfazer um esquema», é perder evidência. O caminho
-- nesse caso é o restauro do backup (`backup_sala.cmd` antes de aplicar).
--
--     psql -X -v ON_ERROR_STOP=1 --single-transaction -f supabase/desfazer/035_desfazer.sql <DSN>
-- ═══════════════════════════════════════════════════════════════════════

do $$
declare n bigint;
begin
  select count(*) into n from public.derived_artifact where kind = 'TEMPO_LUGAR';
  if n > 0 then
    raise exception 'DESFAZER_035_RECUSADO: % derivado(s) TEMPO_LUGAR existem; '
                    'desfazer apagaria evidencia. Restaure o backup.', n;
  end if;
end $$;

alter table public.derived_artifact drop constraint derived_artifact_kind_check;
alter table public.derived_artifact add constraint derived_artifact_kind_check
  check (kind = any (array['TEXT_EXTRACTION', 'OCR', 'TRANSCRIPTION', 'TRANSLATION',
                           'THUMBNAIL', 'FRAME', 'TABLE_EXTRACTION']));

-- o livro-razão da cadeia: sem isto, a cadeia daria SKIP a uma 035 que já não existe
delete from public.schema_migracao where versao = '035';
