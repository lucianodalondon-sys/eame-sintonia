-- ═══════════════════════════════════════════════════════════════════════
-- O PORTÃO DE ENTRADA DA COLETA — regressões
--
-- Exige 001–016 e o ensaio SENSOR-HUMANO-CINCO-PERFIS.
-- Só lê; os testes negativos desfazem tudo.
--
-- Aqui moram as leis que a coleta paga tem de obedecer ANTES de gastar:
--   BR-16  AGGREGATOR ≠ HUMAN_VOICE  ·  SEARCH_HIT ≠ PERSON
--   BR-19  SEM_CHECKPOINT_NAO_GASTEI
--   BR-20  PROCESS_CRASH ≠ LOST_COLLECTION
--   BR-14  a identidade do conteúdo não depende da rodada
-- O ciclo completo (token acaba → retomada → zero duplicata) é provado em
-- tests/test_coleta_resiliente.py, que exerce o MESMO caminho produtivo.
-- ═══════════════════════════════════════════════════════════════════════

\set ON_ERROR_STOP on

create temp table _co (ordem serial, nome text, ok boolean, detalhe text);

create or replace function pg_temp.afirma(n text, cond boolean, det text default '')
returns void language plpgsql as $f$
begin insert into _co (nome, ok, detalhe) values (n, coalesce(cond,false), det); end $f$;

create or replace function pg_temp.recusa(n text, comando text)
returns void language plpgsql as $f$
begin
  begin
    execute comando;
    raise exception 'ACEITOU_O_QUE_DEVERIA_RECUSAR';
  exception when others then
    if sqlerrm = 'ACEITOU_O_QUE_DEVERIA_RECUSAR' then
      insert into _co (nome, ok, detalhe) values (n, false, 'o banco ACEITOU o que a lei proíbe');
    else
      insert into _co (nome, ok, detalhe) values (n, true, 'recusado: ' || left(sqlerrm, 62));
    end if;
  end;
end $f$;

-- Recusar não basta: uma linha pode ser recusada pelo motivo ERRADO e o
-- teste ficar verde sem provar nada. A primeira versão do K4 esquecia
-- `platform` e passava por NOT NULL, não pelo vocabulário de estados.
-- Por isso a recusa esperada tem de NOMEAR a trava que deveria disparar.
create or replace function pg_temp.recusa_por(n text, comando text, trava text)
returns void language plpgsql as $f$
declare msg text;
begin
  begin
    execute comando;
    insert into _co (nome, ok, detalhe) values (n, false, 'o banco ACEITOU o que a lei proíbe');
    return;
  exception when others then
    msg := sqlerrm;
  end;
  if position(trava in msg) > 0 then
    insert into _co (nome, ok, detalhe) values (n, true, 'recusado por ' || trava);
  else
    insert into _co (nome, ok, detalhe) values (n, false,
      'recusado pelo motivo ERRADO — esperava ' || trava || ', veio: ' || left(msg, 80));
  end if;
end $f$;

create or replace function pg_temp.sensor(cid text)
returns public.v_human_sensor_admissivel language sql stable as $f$
  select s.* from public.v_human_sensor_admissivel s where s.channel_id = cid;
$f$;


-- ═══ BR-16 · AGGREGATOR ≠ HUMAN_VOICE ════════════════════════════════
-- A cicatriz: um canal que republica o que outros escreveram foi contado
-- como voz humana, e o número de "pessoas falando" subiu sem que uma só
-- voz humana nova existisse.

select pg_temp.afirma('S1 · pessoa legítima é admissível',
  (pg_temp.sensor('ENSAIO-PERFIL-PESSOA')).admissivel
  and (pg_temp.sensor('ENSAIO-PERFIL-PESSOA')).porque = 'ADMISSIVEL',
  'perfil de pessoa COM ficha de pessoa: o único caso que passa');

select pg_temp.afirma('S2 · página institucional NÃO é voz humana',
  not (pg_temp.sensor('ENSAIO-PERFIL-ORG')).admissivel
  and (pg_temp.sensor('ENSAIO-PERFIL-ORG')).porque = 'ORGANIZACAO_NAO_E_VOZ_HUMANA',
  'a entidade fala; isso não faz dela uma pessoa');

select pg_temp.afirma('S3 · agregador NÃO é sensor humano',
  not (pg_temp.sensor('ENSAIO-PERFIL-AGREGADOR')).admissivel
  and (pg_temp.sensor('ENSAIO-PERFIL-AGREGADOR')).porque = 'AGGREGATOR_NAO_E_HUMAN_SENSOR',
  'republicar texto de terceiro não é ter voz');

select pg_temp.afirma('S4 · resultado de busca NÃO é pessoa',
  not (pg_temp.sensor('ENSAIO-PERFIL-BUSCA')).admissivel
  and (pg_temp.sensor('ENSAIO-PERFIL-BUSCA')).porque = 'SEARCH_HIT_NAO_E_PESSOA',
  'o envelope da resposta não é quem respondeu');

select pg_temp.afirma('S5 · desconhecido fica desconhecido',
  not (pg_temp.sensor('ENSAIO-PERFIL-DESCONHECIDO')).admissivel
  and (pg_temp.sensor('ENSAIO-PERFIL-DESCONHECIDO')).porque = 'TIPO_DE_PERFIL_NAO_MEDIDO',
  'NOT_KNOWN é "não medimos", e não "não é pessoa"');

-- As duas condições são independentes, e a prova é o caso que tem uma só.
select pg_temp.afirma('S6 · perfil de pessoa SEM ficha de pessoa não passa',
  not (pg_temp.sensor('ENSAIO-PERFIL-PESSOA-SEM-FICHA')).admissivel
  and (pg_temp.sensor('ENSAIO-PERFIL-PESSOA-SEM-FICHA')).porque
      = 'PERFIL_DE_PESSOA_SEM_FICHA_DE_PESSOA',
  'ler a página e cadastrar a origem são dois atos; um só não basta');

select pg_temp.afirma('S7 · toda recusa vem com motivo escrito',
  not exists (select 1 from public.v_human_sensor_admissivel
               where porque is null or porque = ''),
  'REFUSED_WITH_REASON, nunca um falso silencioso');

select pg_temp.afirma('S8 · só PERSON_PROFILE com ficha de pessoa é admissível',
  not exists (select 1 from public.v_human_sensor_admissivel
               where admissivel
                 and (tipo_de_perfil <> 'PERSON_PROFILE' or pessoa_id is null)),
  'nenhum outro caminho leva a admissivel = true');

-- Declarar exige evidência. NOT_KNOWN é o único que não exige nada — e é
-- por isso que ele é o padrão, e não uma classificação automática.
select pg_temp.recusa_por('S9 · declarar tipo de perfil sem evidência é recusado', $x$
  insert into public.canal (origem_id, plataforma, channel_id, tipo_de_perfil)
  select o.id, 'web', 'ENSAIO-PERFIL-SEM-EVIDENCIA', 'PERSON_PROFILE'
    from public.origem o where o.rotulo='ORIGEM ENSAIO PESSOA'
$x$, 'tipo_de_perfil_declarado_exige_evidencia');

-- 'INFLUENCER' é justamente o rótulo que sai de heurística fraca: contar
-- seguidores. O banco não conhece essa palavra, e é assim que ele impede
-- a classificação por volume.
select pg_temp.recusa_por('S10 · um tipo de perfil fora do vocabulário é recusado', $x$
  insert into public.canal (origem_id, plataforma, channel_id, tipo_de_perfil,
                            tipo_de_perfil_evidencia)
  select o.id, 'web', 'ENSAIO-PERFIL-INVENTADO', 'INFLUENCER', 'muitos seguidores'
    from public.origem o where o.rotulo='ORIGEM ENSAIO PESSOA'
$x$, 'canal_tipo_de_perfil_check');

select pg_temp.afirma('S11 · o padrão de um canal novo é NOT_KNOWN',
  (select column_default from information_schema.columns
    where table_schema='public' and table_name='canal'
      and column_name='tipo_de_perfil') like '%NOT_KNOWN%',
  'um canal recém-cadastrado nasce não-medido, nunca "pessoa"');


-- ═══ BR-19 · SEM CHECKPOINT NÃO GASTEI ═══════════════════════════════
-- A cicatriz: a coleta paga começava sem registro, o processo morria, e
-- não havia como saber o que já tinha sido pago.

select pg_temp.afirma('K1 · sem linha aberta, pode_gastar diz não',
  not (select pode from public.pode_gastar('ALVO-QUE-NUNCA-EXISTIU','hash-inexistente'))
  and (select porque from public.pode_gastar('ALVO-QUE-NUNCA-EXISTIU','hash-inexistente'))
      = 'SEM_CHECKPOINT_NAO_GASTEI',
  'a resposta padrão é NÃO, e ela vem com o motivo');

select pg_temp.afirma('K2 · o checkpoint mínimo tem os nove campos',
  (select count(*) from information_schema.columns
    where table_schema='public' and table_name='checkpoint_coleta'
      and column_name in ('collection_target','input_hash','actor','started_at',
                          'estado','pool_position','run_id','dataset_id',
                          'ultima_unidade')) = 9,
  'COLLECTION_TARGET, INPUT_HASH, ACTOR, STARTED_AT, STATE, POOL_POSITION, '
  'RUN_ID, DATASET_ID, LAST_PERSISTED_PROGRESS');

select pg_temp.afirma('K3 · o mesmo alvo com a mesma entrada é uma linha só',
  exists (select 1 from pg_constraint
           where conrelid='public.checkpoint_coleta'::regclass and contype='u'
             and pg_get_constraintdef(oid) like '%collection_target%input_hash%'),
  'sem isso, duas rodadas do mesmo alvo pagariam duas vezes');

-- Todos os NOT NULL vêm preenchidos DE PROPÓSITO: a única coisa errada na
-- linha tem de ser o estado, senão o teste passa por outra trava.
select pg_temp.recusa_por('K4 · um estado de checkpoint fora do vocabulário é recusado', $x$
  insert into public.checkpoint_coleta
    (collection_target, input_hash, actor, platform, started_at, updated_at,
     estado, rule_version)
  values ('ENSAIO-K4','h','ator','web', now(), now(), 'QUASE_PRONTO','ensaio')
$x$, 'checkpoint_coleta_estado_check');

-- E a mesma linha, com um estado do vocabulário, ENTRA. Sem isto o K4
-- poderia estar verde só porque a tabela recusa tudo.
do $$
declare entrou boolean; sobrou boolean;
begin
  insert into public.checkpoint_coleta
    (collection_target, input_hash, actor, platform, started_at, updated_at,
     estado, rule_version)
  values ('ENSAIO-K4','h','ator','web', now(), now(), 'ABERTO','ensaio');
  entrou := exists (select 1 from public.checkpoint_coleta
                     where collection_target='ENSAIO-K4');
  -- E sai: esta suíte não deixa rastro no banco.
  delete from public.checkpoint_coleta where collection_target='ENSAIO-K4';
  sobrou := exists (select 1 from public.checkpoint_coleta
                     where collection_target='ENSAIO-K4');
  perform pg_temp.afirma('K4b · a mesma linha com estado válido é aceita, e depois sai',
    entrou and not sobrou,
    'a trava recusa o estado inventado, não a linha — e o teste não deixa rastro');
end $$;


-- ═══ BR-20 · PROCESS_CRASH ≠ LOST_COLLECTION ═════════════════════════
-- O progresso mora no BANCO, não na memória do processo. Um processo que
-- morre não leva a coleta junto — e a prova de que a retomada funciona é
-- o ciclo A–H em tests/test_coleta_resiliente.py.

select pg_temp.afirma('K5 · o progresso persistido é campo de banco',
  (select count(*) from information_schema.columns
    where table_schema='public' and table_name='checkpoint_coleta'
      and column_name in ('unidades_totais','unidades_feitas','itens_persistidos')) = 3,
  'o que foi feito não pode existir só na memória de quem estava fazendo');

select pg_temp.afirma('K6 · a rodada aponta o checkpoint que a gerou',
  exists (select 1 from information_schema.columns
           where table_schema='public' and table_name='collection_run'
             and column_name='checkpoint_id'),
  'do RUN_ID se chega ao alvo, e do alvo se chega ao que falta');


-- ═══ BR-14 · A IDENTIDADE NÃO DEPENDE DA RODADA ══════════════════════
-- A cicatriz: retomar por outra chave duplicava tudo, porque a identidade
-- carregava a rodada dentro dela.

select pg_temp.afirma('D1 · a identidade do conteúdo é (canal, content_id)',
  (select pg_get_constraintdef(oid) from pg_constraint
    where conname='conteudo_canal_id_content_id_key') = 'UNIQUE (canal_id, content_id)',
  'PLATFORM + EXTERNAL_ID via canal, e nada mais');

-- Se a rodada entrasse na identidade, ela apareceria na definição da trava.
-- Este teste lê a definição real e procura os quatro nomes proibidos.
select pg_temp.afirma('D2 · rodada, token, dataset e captura ficam FORA da identidade',
  not exists (
    select 1 from unnest(array['run_id','token','dataset','capturado_em']) t(proibido)
     where (select pg_get_constraintdef(oid) from pg_constraint
             where conname='conteudo_canal_id_content_id_key') like '%' || t.proibido || '%'),
  'com qualquer um deles dentro, a retomada por outra chave duplicaria tudo');

select pg_temp.afirma('D3 · ver o mesmo conteúdo de novo é observação, não conteúdo novo',
  exists (select 1 from pg_constraint
           where conrelid='public.conteudo_visto_em'::regclass and contype='u'
             and pg_get_constraintdef(oid) like '%conteudo_id%run_id%'),
  'duas rodadas, duas observações, UM conteúdo');


-- ═══════════════════════════════════════════════════════════════════════
\echo ''
\echo '── O PORTÃO DE ENTRADA DA COLETA ─────────────────────────────────'
select case when ok then 'PASS' else 'FAIL' end as r, nome, detalhe
  from _co order by ordem;
select 'TOTAL=' || count(*) || '  PASS=' || count(*) filter (where ok)
     || '  FAIL=' || count(*) filter (where not ok) as placar from _co;
do $$
declare n integer;
begin
  select count(*) into n from _co where not ok;
  if n > 0 then raise exception 'REGRESSOES_COLETA_FALHARAM=%', n; end if;
  raise notice 'REGRESSOES_COLETA=PASS';
end $$;
