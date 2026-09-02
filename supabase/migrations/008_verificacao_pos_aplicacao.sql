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
-- RODAR DEPOIS de aplicar 001–007 e 009–018. Ela é a última, não a oitava.
--
-- NÃO EXECUTADA em Supabase. Executada e conferida num PostgreSQL 16
-- local e descartável: 001–012 montadas do zero, fixture ES carregada e
-- supabase/tests/regressoes_calendario.sql verde (45/45). Aplicar em
-- produção continua sendo trabalho do workflow supabase-migrate.
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
    'resposta_registrada','lacuna_candidata','registro_regulatorio','registro_uso',
    -- 009
    'disponibilidade_comercial','crop_local','issue_local',
    -- 010 — os quatro relogios
    'crop_calendar','issue_window','registro_uso_janela','freshness_regra'];
begin
  -- 1 · as tabelas existem?
  foreach t in array esperadas loop
    if not exists (select 1 from information_schema.tables
                    where table_schema='public' and table_name=t) then
      faltando := faltando || ('tabela ' || t)::text;
    end if;
  end loop;

  -- 2 · as travas que carregam LEI existem? (não basta a tabela existir)
  if not exists (select 1 from pg_constraint
                  where conname='bruto_ausente_precisa_de_motivo') then
    faltando := faltando || 'CHECK bruto_ausente_precisa_de_motivo'::text;
  end if;
  if not exists (select 1 from pg_constraint
                  where conname='origem_e_pessoa_ou_organizacao') then
    faltando := faltando || 'CHECK origem_e_pessoa_ou_organizacao'::text;
  end if;
  if not exists (select 1 from pg_constraint
                  where conname='zero_precisa_de_diagnostico_antes_de_virar_lacuna') then
    faltando := faltando || 'CHECK zero_precisa_de_diagnostico_antes_de_virar_lacuna'::text;
  end if;

  -- 3 · SEMANTICA DE PAIS (009). Cada uma destas responde "esta afirmacao
  --     sabe de que pais ela fala?". Sem elas, ES/FR/IT se misturam calados.
  if not exists (select 1 from pg_constraint where conname='resposta_registrada_por_pais') then
    faltando := faltando || 'UNIQUE resposta_registrada_por_pais'::text;
  end if;
  if not exists (select 1 from pg_constraint where conname='lacuna_por_pais') then
    faltando := faltando || 'UNIQUE lacuna_por_pais'::text;
  end if;
  if not exists (select 1 from pg_constraint where conname='derivacao_declara_de_onde_fala') then
    faltando := faltando || 'CHECK derivacao_declara_de_onde_fala'::text;
  end if;
  if not exists (select 1 from pg_constraint where conname='afirmacao_comercial_exige_fonte') then
    faltando := faltando || 'CHECK afirmacao_comercial_exige_fonte'::text;
  end if;
  -- crop e issue precisam estar LIMPAS de vocabulario espanhol
  if exists (select 1 from information_schema.columns
              where table_schema='public' and table_name in ('crop','issue')
                and column_name in ('nome_es','mapa_id_cultivo','mapa_id_plaga')) then
    faltando := faltando || 'crop/issue ainda carregam vocabulario espanhol (009 nao aplicada)'::text;
  end if;
  -- as views nacionais precisam agrupar por pais do FATO
  if not exists (select 1 from information_schema.columns
                  where table_schema='public' and table_name='v_independencia_por_par'
                    and column_name='fact_country') then
    faltando := faltando || 'v_independencia_por_par sem fact_country'::text;
  end if;
  if not exists (select 1 from information_schema.views
                  where table_schema='public' and table_name='v_cross_market_por_par') then
    faltando := faltando || 'view v_cross_market_por_par'::text;
  end if;

  -- 4 · a chave natural da origem — o defeito-raiz do Brasil
  if not exists (select 1 from pg_indexes
                  where schemaname='public' and indexname='origem_por_pessoa_idx') then
    faltando := faltando || 'indice origem_por_pessoa_idx'::text;
  end if;

  -- 5 · RLS ligada em todas. `rowsecurity=true` e "existe política" são
  --     perguntas DIFERENTES: tabela trancada com zero políticas está SOLDADA,
  --     e isso não é segurança, é indisponibilidade. O Brasil separa as duas
  --     em conferir-trancas.sql; aqui só a primeira cabe, a segunda depende
  --     de eh_admin() e fica para o schema de acesso.
  foreach t in array esperadas loop
    if exists (select 1 from pg_tables
                where schemaname='public' and tablename=t and not rowsecurity) then
      faltando := faltando || ('RLS desligada em ' || t)::text;
    end if;
  end loop;

  -- 6 · CALENDARIO AGRONOMICO (010-012). Sem estas travas o portal pode
  --     responder uma data que ninguem mediu, ou fechar uma janela que so
  --     e desconhecida. Tabela existir nao basta: a lei mora na constraint.
  foreach t in array array[
      'calendario_resolucao_bate_com_o_preenchido',
      'campanha_observada_nao_recorre',
      'campanha_observada_declara_o_ano',
      'calendario_geografia_e_do_pais',
      'janela_issue_resolucao_bate_com_o_preenchido',
      'atividade_observada_nao_recorre',
      'janela_issue_geografia_e_do_pais',
      'janela_produto_resolucao_bate_com_o_preenchido'] loop
    if not exists (select 1 from pg_constraint where conname=t) then
      faltando := faltando || ('CHECK ' || t)::text;
    end if;
  end loop;

  -- ISSUE_WINDOW != FIELD_PRESSURE. Uma coluna de magnitude aqui seria a
  -- pressao do campo morando na janela do issue, e as duas nao sao a mesma.
  if exists (select 1 from information_schema.columns
              where table_schema='public' and table_name='issue_window'
                and column_name ~ '(pressao|incidencia|severidade|intensidade|valor)') then
    faltando := faltando || 'issue_window ganhou coluna de pressao (relogio B contaminado)'::text;
  end if;

  -- AS_OF_DATE nunca vira coluna. Estado corrente e derivado na pergunta.
  if exists (select 1 from information_schema.columns
              where table_schema='public'
                and table_name in ('crop_calendar','issue_window','registro_uso_janela')
                and column_name ~ '^(hoje|today|as_of|estado_atual|status_atual)$') then
    faltando := faltando || 'alguma tabela do calendario guarda "hoje" como coluna'::text;
  end if;

  -- as funcoes que o portal chama existem, e todas exigem pais
  foreach t in array array['estado_janela_por_data','estado_janela_por_bbch','estado_frescor',
                           'f_bbch_observado','f_crop_calendar','f_next_relevant_window',
                           'f_latest_observations','f_case_temporal_context',
                           'f_paises_no_resultado_do_calendario','geografia_do_pais'] loop
    if not exists (select 1 from pg_proc p join pg_namespace n on n.oid=p.pronamespace
                    where n.nspname='public' and p.proname=t) then
      faltando := faltando || ('funcao ' || t)::text;
    end if;
  end loop;
  foreach t in array array['f_crop_calendar','f_next_relevant_window','f_latest_observations',
                           'f_bbch_observado','f_case_temporal_context'] loop
    if not exists (select 1 from pg_proc p join pg_namespace n on n.oid=p.pronamespace
                    where n.nspname='public' and p.proname=t
                      and 'p_pais' = any(p.proargnames)) then
      faltando := faltando || (t || ' pode ser chamada sem pais')::text;
    end if;
  end loop;

  foreach t in array array['v_crop_calendar','v_crop_calendar_por_regiao','v_issue_windows',
                           'v_product_registered_windows','v_product_line_semantics'] loop
    if not exists (select 1 from information_schema.views
                    where table_schema='public' and table_name=t) then
      faltando := faltando || ('view ' || t)::text;
    end if;
  end loop;

  -- 7 · CAPTURE != REGISTRATION (013). Sem estas, a segunda captura do mesmo
  --     registro volta a duplicar o produto no caso — ou, pior, a faze-lo sumir.
  if not exists (select 1 from pg_constraint
                  where conname='captura_e_unica_por_fonte_e_versao') then
    faltando := faltando || 'UNIQUE captura_e_unica_por_fonte_e_versao'::text;
  end if;
  foreach t in array array['instante_da_fonte','f_registro_corrente',
                           'f_product_registered_windows'] loop
    if not exists (select 1 from pg_proc p join pg_namespace n on n.oid=p.pronamespace
                    where n.nspname='public' and p.proname=t) then
      faltando := faltando || ('funcao ' || t)::text;
    end if;
  end loop;
  -- a chave antiga NAO pode ter sobrevivido: ela omitia `fonte`
  if exists (select 1 from pg_constraint
              where conname='registro_regulatorio_pais_registration_id_fonte_versao_key') then
    faltando := faltando || 'a chave de captura antiga ainda existe (013 nao aplicada)'::text;
  end if;

  -- 8 · AS CICATRIZES DO BRASIL (015). A lição que governa esta seção é que
  --     no Brasil a regra existia na PROSA e não no CAMPO — e foi o campo que
  --     decidiu a saída publicada.
  -- As duas travas de localização da 015 foram APOSENTADAS pela 018 junto
  -- com a coluna que elas guardavam. Elas renasceram sobre conteudo_lugar,
  -- onde valem para CADA lugar do fato, e são conferidas na seção 11.
  foreach t in array array['tentativa_sem_evidencia_nao_e_ausencia'] loop
    if not exists (select 1 from pg_constraint where conname=t) then
      faltando := faltando || ('CHECK ' || t)::text;
    end if;
  end loop;
  foreach t in array array['precisao_da_geografia','f_relevancia_ao_caso',
                           'f_runs_pagos_sem_bruto'] loop
    if not exists (select 1 from pg_proc p join pg_namespace n on n.oid=p.pronamespace
                    where n.nspname='public' and p.proname=t) then
      faltando := faltando || ('funcao ' || t)::text;
    end if;
  end loop;
  if not exists (select 1 from information_schema.tables
                  where table_schema='public' and table_name='tentativa_de_coleta') then
    faltando := faltando || 'tabela tentativa_de_coleta'::text;
  end if;
  if not exists (select 1 from information_schema.views
                  where table_schema='public' and table_name='v_conteudo_localizacao') then
    faltando := faltando || 'view v_conteudo_localizacao'::text;
  end if;
  -- relevancia e estado com motivo, nunca numero
  if exists (select 1 from information_schema.columns
              where table_schema='public' and table_name='conteudo_crop_issue'
                and column_name ~ '(score|peso|nota|rank|pontua)') then
    faltando := faltando || 'conteudo_crop_issue ganhou coluna de score'::text;
  end if;

  -- 9 · O PORTÃO DE ENTRADA DA COLETA (016). Sem estes objetos a guarda do
  --     gasto não existe no banco, e SEM_CHECKPOINT_NAO_GASTEI vira prosa
  --     outra vez — que é exatamente a forma como o Brasil perdeu a coleta.
  if not exists (select 1 from information_schema.tables
                  where table_schema='public' and table_name='checkpoint_coleta') then
    faltando := faltando || 'tabela checkpoint_coleta (016)'::text;
  end if;
  if not exists (select 1 from information_schema.tables
                  where table_schema='public' and table_name='conteudo_visto_em') then
    faltando := faltando || 'tabela conteudo_visto_em (016)'::text;
  end if;
  foreach t in array array['collection_target','input_hash','actor','started_at',
                           'estado','pool_position','run_id','dataset_id',
                           'ultima_unidade','unidades_feitas','itens_persistidos'] loop
    if not exists (select 1 from information_schema.columns
                    where table_schema='public' and table_name='checkpoint_coleta'
                      and column_name=t) then
      faltando := faltando || ('checkpoint_coleta.' || t)::text;
    end if;
  end loop;
  if not exists (select 1 from pg_proc p join pg_namespace n on n.oid=p.pronamespace
                  where n.nspname='public' and p.proname='pode_gastar') then
    faltando := faltando || 'funcao pode_gastar (016)'::text;
  end if;
  -- A identidade do conteúdo NÃO pode carregar a rodada dentro dela: se
  -- carregasse, retomar por outra chave duplicaria tudo.
  if (select pg_get_constraintdef(oid) from pg_constraint
       where conname='conteudo_canal_id_content_id_key')
     is distinct from 'UNIQUE (canal_id, content_id)' then
    faltando := faltando || 'a identidade natural de conteudo mudou de forma'::text;
  end if;
  if not exists (select 1 from pg_constraint
                  where conname='tipo_de_perfil_declarado_exige_evidencia') then
    faltando := faltando || 'CHECK tipo_de_perfil_declarado_exige_evidencia (016)'::text;
  end if;
  if not exists (select 1 from information_schema.views
                  where table_schema='public' and table_name='v_human_sensor_admissivel') then
    faltando := faltando || 'view v_human_sensor_admissivel (016)'::text;
  end if;

  -- 10 · O QUE A CONFERÊNCIA DE LOCALIZAÇÃO ACHOU (017). `fact_forca_da_
  --      sustentacao` era coluna desta view e saiu na 018: com 0..N lugares,
  --      a força passou a ser de CADA lugar, e mora em conteudo_lugar.
  foreach t in array array['fact_sustentado_apenas_por_mencao'] loop
    if not exists (select 1 from information_schema.columns
                    where table_schema='public' and table_name='v_conteudo_localizacao'
                      and column_name=t) then
      faltando := faltando || ('v_conteudo_localizacao.' || t || ' (017)')::text;
    end if;
  end loop;

  -- 11 · O LUGAR DO FATO GANHA DONO (018). Sem estes objetos, o lugar do
  --      fato volta a ser uma coluna 0..1 e as quatro espécies de lugar
  --      voltam a colapsar na praça da fonte.
  foreach t in array array['origem_lugar','conteudo_lugar'] loop
    if not exists (select 1 from information_schema.tables
                    where table_schema='public' and table_name=t) then
      faltando := faltando || ('tabela ' || t || ' (018)')::text;
    end if;
  end loop;
  -- O dono antigo NÃO pode ter voltado: dois donos da mesma lei responderiam
  -- coisas diferentes um dia, e ninguém saberia qual.
  if exists (select 1 from information_schema.columns
              where table_schema='public' and table_name='conteudo'
                and column_name='fact_geografia_id') then
    faltando := faltando || 'conteudo.fact_geografia_id voltou (018 desfeita)'::text;
  end if;
  foreach t in array array['so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato',
                           'lugar_do_fato_diz_como_se_soube',
                           'lugar_do_fato_declara_a_especie_da_evidencia',
                           'lugar_do_fato_carrega_a_ancora',
                           'resolvido_aponta_geografia',
                           'zona_da_fonte_nao_e_divisao_administrativa',
                           'tempo_do_fato_diz_como_se_soube'] loop
    if not exists (select 1 from pg_constraint where conname=t) then
      faltando := faltando || ('CHECK ' || t || ' (018)')::text;
    end if;
  end loop;
  foreach t in array array['escada_de_precisao','f_ocorrencia_nao_e_incidencia'] loop
    if not exists (select 1 from pg_proc p join pg_namespace n on n.oid=p.pronamespace
                    where n.nspname='public' and p.proname=t) then
      faltando := faltando || ('funcao ' || t || ' (018)')::text;
    end if;
  end loop;
  foreach t in array array['fact_tempo_texto','fact_tempo_resolucao',
                           'fact_tempo_evidencia','fact_tempo_origem'] loop
    if not exists (select 1 from information_schema.columns
                    where table_schema='public' and table_name='conteudo'
                      and column_name=t) then
      faltando := faltando || ('conteudo.' || t || ' (018)')::text;
    end if;
  end loop;
  -- PUBLISHED_AT != FACT_TIME: a ausência de 'PUBLICACAO' no vocabulário é
  -- a trava. Se ela aparecer, a lei morreu sem que nada mais reprove.
  if (select pg_get_constraintdef(oid) from pg_constraint
       where conname like '%fact_tempo_origem%') like '%PUBLICACAO%' then
    faltando := faltando || 'PUBLICACAO entrou no vocabulario do tempo do fato'::text;
  end if;
  if not exists (select 1 from information_schema.views
                  where table_schema='public' and table_name='v_lugar_do_fato') then
    faltando := faltando || 'view v_lugar_do_fato (018)'::text;
  end if;

  if array_length(faltando,1) is not null then
    raise exception E'O BANCO NAO BATE COM AS MIGRATIONS.\nFaltando:\n  %',
      array_to_string(faltando, E'\n  ');
  end if;

  raise notice 'migrations 001-018 conferidas: % tabelas, travas, funcoes e RLS no lugar',
    array_length(esperadas,1);
end $$;
