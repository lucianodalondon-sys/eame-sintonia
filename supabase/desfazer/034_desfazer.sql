-- ═══════════════════════════════════════════════════════════════════════
-- DESFAZER da 034 · a_lapide_da_retencao
--
-- FORA de `supabase/migrations/` de propósito (a cadeia aplica todo `*.sql` de lá).
--
-- ⚠️ NÃO APAGA LÁPIDES. Uma lápide é a ÚNICA prova escrita de que um ficheiro da YouTube Data API foi
-- apagado pela regra dos 30 dias (D20 · III.E.4): o byte já saiu. Se existir alguma, este desfazer
-- RECUSA-SE — apagá-la seria perder a prova do que se apagou. O caminho, nesse caso, é o backup.
--
-- Se a 035 estiver aplicada, desfaz-se ela primeiro (a ordem inversa da aplicação).
--
--     psql -X -v ON_ERROR_STOP=1 --single-transaction -f supabase/desfazer/034_desfazer.sql <DSN>
-- ═══════════════════════════════════════════════════════════════════════

do $$
declare n bigint;
begin
  if to_regclass('public.lapide_de_retencao') is not null then
    execute 'select count(*) from public.lapide_de_retencao' into n;
    if n > 0 then
      raise exception 'DESFAZER_034_RECUSADO: % lapide(s) de retencao existem; '
                      'desfazer apagaria a prova do que foi apagado. Restaure o backup.', n;
    end if;
  end if;
end $$;

drop index if exists public.lapide_raw_idx;
drop table if exists public.lapide_de_retencao;

-- o livro-razão da cadeia: sem isto, a cadeia daria SKIP a uma 034 que já não existe
delete from public.schema_migracao where versao = '034';
