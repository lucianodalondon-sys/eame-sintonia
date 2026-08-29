-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 008 (VERIFICAÇÃO, não criação)
--
-- Esta migration não cria nada. Ela CONFERE que as sete anteriores foram
-- de fato aplicadas, e falha alto se não foram.
--
-- Por que existe — a lição de método mais cara do Sintonia Brasil:
--
--     "ler o .sql do repositório NÃO prova que a trava está no banco.
--      Migração versionada prova que alguém ESCREVEU a tranca,
--      não que ela FOI APLICADA."
--
-- Lá, o arquivo que descreve o banco deixou de descrever o banco. Quatro
-- colunas de `fontes` — cadencia_dias, canal_youtube, falhas, ultima_coleta —
-- usadas por 6 coletores e pela fila inteira, foram criadas à mão no painel do
-- Supabase e nunca entraram em .sql nenhum. A função `eh_admin()` é chamada 10
-- vezes e não é definida em lugar nenhum. A view `v_agenda_coleta`, que é a
-- fila da coleta inteira, também não. O próprio repo registra o veredito:
-- «quem for montar este banco do zero amanhã monta um banco que não funciona».
--
-- E a `fontes` real tem 63 colunas contra as 14 declaradas no arquivo.
--
-- O teste em tests/test_migrations.py cobre o outro lado — que os arquivos são
-- coerentes entre si. Os dois juntos fecham a pergunta; nenhum sozinho fecha.
--
-- RODAR DEPOIS de aplicar 001–007. NÃO EXECUTADA ainda.
-- ═══════════════════════════════════════════════════════════════════════

do $$
declare
  faltando text[] := '{}';
  t text;
  esperadas text[] := array[
    'geografia','collection_run','raw_asset','organizacao','pessoa',
    'pessoa_identificador','afiliacao','origem','canal','conteudo',
    'transcricao','comentario','crop','issue','crop_issue',
    'conteudo_crop_issue','observacao','derivacao','derivacao_observacao',
    'resposta_registrada','lacuna_candidata','registro_regulatorio','registro_uso'];
begin
  -- 1 · as tabelas existem?
  foreach t in array esperadas loop
    if not exists (select 1 from information_schema.tables
                    where table_schema='public' and table_name=t) then
      faltando := faltando || ('tabela ' || t);
    end if;
  end loop;

  -- 2 · as travas que carregam LEI existem? (não basta a tabela existir)
  if not exists (select 1 from pg_constraint
                  where conname='bruto_ausente_precisa_de_motivo') then
    faltando := faltando || 'CHECK bruto_ausente_precisa_de_motivo';
  end if;
  if not exists (select 1 from pg_constraint
                  where conname='origem_e_pessoa_ou_organizacao') then
    faltando := faltando || 'CHECK origem_e_pessoa_ou_organizacao';
  end if;
  if not exists (select 1 from pg_constraint
                  where conname='zero_precisa_de_diagnostico_antes_de_virar_lacuna') then
    faltando := faltando || 'CHECK zero_precisa_de_diagnostico_antes_de_virar_lacuna';
  end if;

  -- 3 · a chave natural da origem — o defeito-raiz do Brasil
  if not exists (select 1 from pg_indexes
                  where schemaname='public' and indexname='origem_por_pessoa_idx') then
    faltando := faltando || 'indice origem_por_pessoa_idx';
  end if;

  -- 4 · RLS ligada em todas. `rowsecurity=true` e "existe política" são
  --     perguntas DIFERENTES: tabela trancada com zero políticas está SOLDADA,
  --     e isso não é segurança, é indisponibilidade. O Brasil separa as duas
  --     em conferir-trancas.sql; aqui só a primeira cabe, a segunda depende
  --     de eh_admin() e fica para o schema de acesso.
  foreach t in array esperadas loop
    if exists (select 1 from pg_tables
                where schemaname='public' and tablename=t and not rowsecurity) then
      faltando := faltando || ('RLS desligada em ' || t);
    end if;
  end loop;

  if array_length(faltando,1) is not null then
    raise exception E'O BANCO NAO BATE COM AS MIGRATIONS.\nFaltando:\n  %',
      array_to_string(faltando, E'\n  ');
  end if;

  raise notice 'migrations 001-007 conferidas: % tabelas, travas e RLS no lugar',
    array_length(esperadas,1);
end $$;
