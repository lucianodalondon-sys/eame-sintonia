-- ═══════════════════════════════════════════════════════════════════════
-- CAPTURE != REGISTRATION — regressões executáveis
--
-- Exige um banco com 001–013, a fixture ES, o ensaio dos cinco casos e o
-- ensaio de duas capturas. Só lê; os testes negativos desfazem tudo.
--
--   psql "$DB" -f supabase/tests/regressoes_captura.sql
-- ═══════════════════════════════════════════════════════════════════════

\set ON_ERROR_STOP on

create temp table _rc (ordem serial, nome text, ok boolean, detalhe text);

create or replace function pg_temp.afirma(n text, cond boolean, det text default '')
returns void language plpgsql as $f$
begin
  insert into _rc (nome, ok, detalhe) values (n, coalesce(cond, false), det);
end $f$;

create or replace function pg_temp.recusa(n text, comando text)
returns void language plpgsql as $f$
begin
  begin
    execute comando;
    raise exception 'ACEITOU_O_QUE_DEVERIA_RECUSAR';
  exception when others then
    if sqlerrm = 'ACEITOU_O_QUE_DEVERIA_RECUSAR' then
      insert into _rc (nome, ok, detalhe) values (n, false, 'o banco ACEITOU o que a lei proíbe');
    else
      insert into _rc (nome, ok, detalhe) values (n, true, 'recusado: ' || left(sqlerrm, 66));
    end if;
  end;
end $f$;


-- ═══ 1 · O HISTÓRICO NÃO É APAGADO PARA PRODUZIR ESTADO CORRENTE ═════
select pg_temp.afirma('01 HISTORY_ROWS > 1 · as capturas continuam todas lá',
  (select count(*) from public.registro_regulatorio where registration_id='ES-00211') > 1,
  'ES-00211 tem mais de uma captura em registro_regulatorio');

select pg_temp.afirma('01b o log continua devolvendo todas as capturas',
  (select count(*) from public.v_product_registered_windows where nome_comercial='NEPTUNE')
   >= (select count(*) from public.f_product_registered_windows('ES', date '2026-08-30')
        where nome_comercial='NEPTUNE'),
  'v_product_registered_windows é o log e não foi estreitada');


-- ═══ 2 · CURRENT_STATE_ROWS = 1 ══════════════════════════════════════
select pg_temp.afirma('02 CURRENT_STATE_ROWS = 1 por registro',
  not exists (
    select 1 from public.f_registro_corrente('ES', date '2026-08-30')
     group by registration_id having count(*) > 1),
  'nenhum registro devolve duas linhas correntes');

select pg_temp.afirma('02b o NEPTUNE aparece UMA vez no caso',
  (select count(*) from jsonb_array_elements(
      public.f_case_temporal_context('ES','OLIVE','REPILO',null,date '2026-08-30')
      ->'product_window_state') p where p->>'product'='NEPTUNE') = 1,
  'de 3 ocorrências para 1, sem apagar captura');

select pg_temp.afirma('02c e o payload diz quantas capturas existem',
  (select (p->>'captures_up_to_as_of')::int from jsonb_array_elements(
      public.f_case_temporal_context('ES','OLIVE','REPILO',null,date '2026-08-30')
      ->'product_window_state') p where p->>'product'='NEPTUNE') > 1,
  'colapsar não é esconder: o número de capturas viaja no payload');


-- ═══ 3 · FUTURE_CAPTURE_CANNOT_REWRITE_PAST_STATE ════════════════════
-- Duas capturas do mesmo registro, em datas diferentes, dizendo coisas
-- diferentes. A pergunta de abril tem de continuar respondendo abril.
select pg_temp.afirma('03 as_of ANTES da segunda captura devolve a PRIMEIRA',
  (select fecha_caducidad from public.f_registro_corrente('ES', date '2026-04-23')
    where registration_id='ES-ENSAIO-ASOF') = date '2027-06-30',
  'em 2026-04-23 o registro dizia caducidad 2027-06-30');

select pg_temp.afirma('03b as_of DEPOIS devolve a SEGUNDA',
  (select fecha_caducidad from public.f_registro_corrente('ES', date '2026-08-30')
    where registration_id='ES-ENSAIO-ASOF') = date '2026-05-31',
  'em 2026-08-30 o registro já dizia 2026-05-31');

select pg_temp.afirma('03c a captura futura NÃO reescreve o passado',
  (select fecha_caducidad from public.f_registro_corrente('ES', date '2026-04-23')
    where registration_id='ES-ENSAIO-ASOF')
  <> (select fecha_caducidad from public.f_registro_corrente('ES', date '2026-08-30')
       where registration_id='ES-ENSAIO-ASOF'),
  'a segunda captura existe na tabela e a resposta de abril não mudou');

select pg_temp.afirma('03d o dia exato da segunda captura já a usa',
  (select fonte_versao from public.f_registro_corrente('ES', date '2026-06-20')
    where registration_id='ES-ENSAIO-ASOF') like '2026-06-20%',
  'a fronteira é <= as_of, e o próprio dia conta');

select pg_temp.afirma('03e antes da PRIMEIRA captura não há linha nenhuma',
  not exists (select 1 from public.f_registro_corrente('ES', date '2026-02-01')
               where registration_id='ES-ENSAIO-ASOF'),
  'ausência de evidência é ausência de linha, nunca uma linha inventada');

select pg_temp.afirma('03f o número de capturas cresce com o as_of',
  (select capturas_ate_as_of from public.f_registro_corrente('ES', date '2026-04-23')
    where registration_id='ES-ENSAIO-ASOF') = 1
  and (select capturas_ate_as_of from public.f_registro_corrente('ES', date '2026-08-30')
        where registration_id='ES-ENSAIO-ASOF') = 2,
  '1 em abril, 2 em agosto');


-- ═══ 4 · A RESPOSTA É DETERMINÍSTICA ═════════════════════════════════
select pg_temp.afirma('04 a mesma pergunta devolve a mesma linha',
  (select registro_id from public.f_registro_corrente('ES', date '2026-08-30')
    where registration_id='ES-00211')
  = (select registro_id from public.f_registro_corrente('ES', date '2026-08-30')
      where registration_id='ES-00211'),
  'o desempate por id torna o empate impossível');

select pg_temp.afirma('04b fonte_versao inválida não derruba nem vira palpite',
  public.instante_da_fonte('isto não é um timestamp') is null
  and public.instante_da_fonte('2026-08-30T05:01:51+02:00') is not null,
  'NULL significa "não ordena por isto", nunca "é antiga"');


-- ═══ 5 · A CHAVE DE CAPTURA INCLUI A FONTE ═══════════════════════════
select pg_temp.afirma('05 a chave natural é (pais, registration_id, fonte, fonte_versao)',
  exists (select 1 from pg_constraint
           where conname='captura_e_unica_por_fonte_e_versao'
             and pg_get_constraintdef(oid) like '%fonte, fonte_versao%'),
  'duas fontes com a mesma string de versão não se sobrescrevem mais');

select pg_temp.recusa('05b a mesma fonte e versão não entra duas vezes', $x$
  insert into public.registro_regulatorio
    (pais, registration_id, nome_comercial, titular, estado, fonte, fonte_versao, capturado_em)
  select 'ES','ES-00211','NEPTUNE','ADAMA Agriculture España S.A.','Vigente',
         r.fonte, r.fonte_versao, now()
    from public.registro_regulatorio r
   where r.registration_id='ES-00211' limit 1
$x$);


-- ═══ 6 · A SEGUNDA CAPTURA NÃO DUPLICA O PRODUTO ═════════════════════
-- O teste que importa: inserir uma captura NOVA e conferir que o caso
-- continua com uma linha por produto. Desfeito no fim.
do $$
declare antes integer; depois integer;
begin
  select count(*) into antes from jsonb_array_elements(
    public.f_case_temporal_context('ES','OLIVE','REPILO',null,date '2026-08-30')
    ->'product_window_state');
  begin
    insert into public.registro_regulatorio
      (pais, registration_id, nome_comercial, titular, formulado, estado,
       fecha_caducidad, fonte, fonte_versao, capturado_em)
    select pais, registration_id, nome_comercial, titular, formulado, estado,
           fecha_caducidad, fonte, '2026-08-30T23:59:59+02:00', capturado_em
      from public.registro_regulatorio where registration_id='ES-00211' limit 1;
    select count(*) into depois from jsonb_array_elements(
      public.f_case_temporal_context('ES','OLIVE','REPILO',null,date '2026-08-30')
      ->'product_window_state');
    -- A escrita foi só para medir. Ela sai do banco aqui, e as variáveis
    -- sobrevivem porque são memória do plpgsql, não estado de tabela.
    raise exception 'DESFAZER';
  exception when others then
    if sqlerrm <> 'DESFAZER' then
      depois := -1;
    end if;
  end;
  insert into _rc (nome, ok, detalhe) values (
    '06 uma captura NOVA não acrescenta produto ao caso', antes = depois,
    format('antes %s produto(s); com a captura nova, %s', antes, depois));
end $$;


-- ═══ 7 · UMA CAPTURA NOVA COM USOS SUPERSEDE, NÃO SOMA ═══════════════
do $$
declare antes integer; depois integer; nova bigint;
begin
  select count(*) into antes from public.f_product_registered_windows('ES', date '2026-08-30')
   where nome_comercial='NEPTUNE';
  begin
    insert into public.registro_regulatorio
      (pais, registration_id, nome_comercial, titular, formulado, estado,
       fecha_caducidad, fonte, fonte_versao, capturado_em)
    select pais, registration_id, nome_comercial, titular, formulado, estado,
           fecha_caducidad, fonte, '2026-08-30T23:59:59+02:00', capturado_em
      from public.registro_regulatorio where registration_id='ES-00211' limit 1
    returning id into nova;
    -- a captura nova traz o MESMO uso e a MESMA janela
    insert into public.registro_uso (registro_id, crop_id, issue_id, substancia)
    select nova, ru.crop_id, ru.issue_id, ru.substancia
      from public.registro_uso ru join public.registro_regulatorio r on r.id=ru.registro_id
     where r.registration_id='ES-00211' limit 1;
    insert into public.registro_uso_janela
      (registro_uso_id, resolucao, prazo_seguranca_dias, timing_texto_original,
       nivel_evidencia, fonte, capturado_em, rule_version)
    select ru.id, 'APPROXIMATE', 120, 'Se dará la primera aplicación antes de la floración',
           'REGULATORY_FACT', 'ENSAIO', now(), 'ensaio'
      from public.registro_uso ru where ru.registro_id = nova;
    select count(*) into depois from public.f_product_registered_windows('ES', date '2026-08-30')
     where nome_comercial='NEPTUNE';
    raise exception 'DESFAZER';
  exception when others then
    if sqlerrm <> 'DESFAZER' then depois := -1; end if;
  end;
  insert into _rc (nome, ok, detalhe) values (
    '07 captura nova COM usos supersede, não soma', antes = depois,
    format('antes %s janela(s); com a captura nova, %s', antes, depois));
end $$;


-- ═══ 8 · QUANDO O ESTADO E OS USOS VÊM DE CAPTURAS DIFERENTES, DIZ ═══
do $$
declare marcado boolean;
begin
  begin
    insert into public.registro_regulatorio
      (pais, registration_id, nome_comercial, titular, formulado, estado,
       fecha_caducidad, fonte, fonte_versao, capturado_em)
    select pais, registration_id, nome_comercial, titular, formulado, estado,
           fecha_caducidad, fonte, '2026-08-30T23:59:59+02:00', capturado_em
      from public.registro_regulatorio where registration_id='ES-00211' limit 1;
    select bool_or(usos_de_outra_captura) into marcado
      from public.f_product_registered_windows('ES', date '2026-08-30')
     where nome_comercial='NEPTUNE';
    raise exception 'DESFAZER';
  exception when others then
    if sqlerrm <> 'DESFAZER' then marcado := null; end if;
  end;
  insert into _rc (nome, ok, detalhe) values (
    '08 estado e usos de capturas diferentes fica DECLARADO', marcado is true,
    'usos_de_outra_captura = true quando a captura corrente não observou usos');
end $$;



-- ═══ 9 · O DEFEITO ORIGINAL, RECONSTRUÍDO E MEDIDO NA MESMA EXECUÇÃO ═
-- A rodada anterior mediu "NEPTUNE 3 vezes" com uma fixture que mudou desde
-- então. Um número de antes/depois que só existe em dois relatórios não é
-- prova. Aqui a condição original é remontada dentro de uma transação
-- desfeita, e as duas leituras são feitas lado a lado.
do $$
declare no_log integer; corrente integer; captura_velha bigint;
begin
  begin
    select id into captura_velha from public.registro_regulatorio
     where registration_id='ES-00211'
     order by public.instante_da_fonte(fonte_versao) asc limit 1;
    -- a captura antiga volta a carregar uma janela própria, como carregava
    insert into public.registro_uso_janela
      (registro_uso_id, resolucao, timing_texto_original, nivel_evidencia,
       fonte, capturado_em, rule_version)
    select ru.id, 'NOT_KNOWN', 'janela da captura antiga, remontada para medir',
           'MANUFACTURER_STATEMENT', 'ENSAIO', now(), 'ensaio'
      from public.registro_uso ru where ru.registro_id = captura_velha;
    insert into public.registro_uso_janela
      (registro_uso_id, resolucao, timing_texto_original, nivel_evidencia,
       fonte, capturado_em, rule_version)
    select ru.id, 'NOT_KNOWN', 'segunda janela da captura corrente, remontada',
           'MANUFACTURER_STATEMENT', 'ENSAIO', now(), 'ensaio'
      from public.registro_uso ru
      join public.registro_regulatorio r on r.id = ru.registro_id
     where r.registration_id='ES-00211' and r.id <> captura_velha;

    select count(*) into no_log from public.v_product_registered_windows
     where nome_comercial='NEPTUNE';
    select count(*) into corrente from public.f_product_registered_windows(
      'ES', date '2026-08-30') where nome_comercial='NEPTUNE';
    raise exception 'DESFAZER';
  exception when others then
    if sqlerrm <> 'DESFAZER' then no_log := -1; corrente := -1; end if;
  end;
  -- A decomposição honesta: das 3 janelas do log, UMA vinha da captura
  -- antiga e some com a 013. As outras duas eram duas linhas de janela da
  -- MESMA captura corrente — e a segunda só existia porque a ficha pública
  -- não publica timing nenhum. Essa sai pela regra de importação (só nasce
  -- janela quando a fonte publica algo), não pela 013.
  --
  -- ATUALIZADO na integração do catálogo: o número absoluto do LOG saiu da
  -- afirmação. Ele era 3 quando as únicas capturas do NEPTUNE eram as do
  -- ensaio; a importação regulatória canônica trouxe uma captura REAL do
  -- ROPF e o log foi para 4 — que é o log fazendo exatamente o trabalho
  -- dele. Fixar o número faria a próxima captura legítima reprovar um teste
  -- que existe para provar que capturas se ACUMULAM.
  --
  -- O que é durável, e o que o teste passa a afirmar:
  --   · o estado CORRENTE continua 2, mexa quem mexer no log;
  --   · o log é MAIOR que o corrente — se fossem iguais, ou a 013 parou de
  --     filtrar a captura antiga, ou alguém apagou histórico para "limpar".
  insert into _rc (nome, ok, detalhe) values (
    '09 a condição original remontada: o log cresce, o corrente não — a 013 filtra a captura antiga',
    corrente = 2 and no_log > corrente,
    format('log %s janela(s) do NEPTUNE, estado corrente %s. O log acumula capturas; '
           'o corrente é derivado as-of e não se move com elas.', no_log, corrente));
end $$;


-- ═══════════════════════════════════════════════════════════════════════
\echo ''
\echo '── CAPTURE != REGISTRATION ───────────────────────────────────────'
select case when ok then 'PASS' else 'FAIL' end as r, nome, detalhe
  from _rc order by ordem;
select 'TOTAL=' || count(*) || '  PASS=' || count(*) filter (where ok)
     || '  FAIL=' || count(*) filter (where not ok) as placar from _rc;
do $$
declare n integer;
begin
  select count(*) into n from _rc where not ok;
  if n > 0 then raise exception 'REGRESSOES_CAPTURA_FALHARAM=%', n; end if;
  raise notice 'REGRESSOES_CAPTURA=PASS';
end $$;
