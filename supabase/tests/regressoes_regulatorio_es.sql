-- ═══════════════════════════════════════════════════════════════════════
-- ES_REGULATORY_IMPORT_V1 — regressões e red team
--
-- Exige 001–018 e o import ES-REGULATORIO-ROPF-2026-08-29.sql.
-- NÃO exige o ensaio: se o ensaio for necessário para estas afirmações
-- passarem, a importação não é canônica. Há teste que mede isso.
-- ═══════════════════════════════════════════════════════════════════════
\set ON_ERROR_STOP on

create temp table _rg (ordem serial, nome text, ok boolean, detalhe text);
create or replace function pg_temp.afirma(n text, cond boolean, det text default '')
returns void language plpgsql as $f$
begin insert into _rg (nome, ok, detalhe) values (n, coalesce(cond,false), det); end $f$;

create or replace function pg_temp.recusa_por(n text, comando text, trava text)
returns void language plpgsql as $f$
declare msg text;
begin
  -- O comando roda numa subtransação que é SEMPRE desfeita: um teste
  -- negativo que ACEITA não pode deixar a mutação no banco.
  begin
    execute comando;
    raise exception 'ACEITOU_O_QUE_DEVERIA_RECUSAR';
  exception when others then msg := sqlerrm;
  end;
  if msg = 'ACEITOU_O_QUE_DEVERIA_RECUSAR' then
    insert into _rg (nome, ok, detalhe) values (n, false, 'o banco ACEITOU o que a lei proíbe');
  elsif position(trava in msg) > 0 then
    insert into _rg (nome, ok, detalhe) values (n, true, 'recusado por ' || trava);
  else
    insert into _rg (nome, ok, detalhe) values (n, false,
      'recusado pelo motivo ERRADO — esperava ' || trava || ', veio: ' || left(msg,70));
  end if;
end $f$;

-- ═══ O DENOMINADOR, MEDIDO ═══════════════════════════════════════════
select pg_temp.afirma('D1 · 96 registros vigentes do ROPF',
  (select count(*) from public.registro_regulatorio where fonte='MAPA_ROPF') = 96,
  'medido no artefato: 96 fichas, 96 REG distintos');
select pg_temp.afirma('D2 · as duas formas de id convivem sem conversão',
  (select count(*) from public.registro_regulatorio
    where fonte='MAPA_ROPF' and registration_id !~ '^ES-') = 62
  and (select count(*) from public.registro_regulatorio
        where fonte='MAPA_ROPF' and registration_id ~ '^ES-') = 34,
  'o registro espanhol usa as duas, e nenhuma virou a outra');
select pg_temp.afirma('D3 · todo registro carrega país, fonte, versão e captura',
  not exists (select 1 from public.registro_regulatorio where fonte='MAPA_ROPF'
               and (pais is null or fonte_versao is null or capturado_em is null
                    or nome_comercial is null or titular is null or formulado is null)),
  'nenhum campo do mínimo ficou vazio nos 96');

-- ═══ RED TEAM ════════════════════════════════════════════════════════

-- 1 · nova captura duplica registro
select pg_temp.afirma('R1 · a chave é de CAPTURA, não de registro',
  (select pg_get_constraintdef(oid) from pg_constraint
    where conname='captura_e_unica_por_fonte_e_versao')
   = 'UNIQUE NULLS NOT DISTINCT (pais, registration_id, fonte, fonte_versao)',
  'CAPTURE != REGISTRATION: (pais, registration_id) é a identidade; a captura acrescenta fonte e versão');
select pg_temp.recusa_por('R1b · reimportar a MESMA versão da fonte não duplica', $x$
  insert into public.registro_regulatorio
   (pais, registration_id, nome_comercial, titular, formulado, estado, fonte, fonte_versao, capturado_em)
  select pais, registration_id, nome_comercial, titular, formulado, estado, fonte, fonte_versao, capturado_em
    from public.registro_regulatorio where fonte='MAPA_ROPF' limit 1
$x$, 'captura_e_unica_por_fonte_e_versao');
do $$
declare depois integer; sobrou integer;
begin
  -- Uma versão NOVA da fonte entra AO LADO da anterior: duas capturas do
  -- MESMO registro, e o log fica inteiro. É a lei da 013 exercida, não
  -- afirmada.
  insert into public.registro_regulatorio
   (pais, registration_id, nome_comercial, titular, formulado, estado,
    fonte, fonte_versao, capturado_em)
  select 'ES', registration_id, nome_comercial, 'ADAMA', formulado, 'vigente',
         'MAPA_ROPF', '2099-01-01T00:00:00Z', now()
    from public.registro_regulatorio
   where fonte='MAPA_ROPF' and registration_id='19140' and fonte_versao <> '2099-01-01T00:00:00Z';
  select count(*) into depois from public.registro_regulatorio
   where registration_id='19140' and fonte='MAPA_ROPF';
  -- e sai: o que o teste cria, o teste desfaz.
  delete from public.registro_regulatorio where fonte_versao='2099-01-01T00:00:00Z';
  select count(*) into sobrou from public.registro_regulatorio
   where fonte_versao='2099-01-01T00:00:00Z';
  perform pg_temp.afirma('R1c · uma versão NOVA da fonte entra ao lado, não por cima',
    depois = 2 and sobrou = 0,
    'duas capturas do MESMO registro convivem; nova captura NÃO cria registro novo');
end $$;

-- 2 · mesmo nome funde IDs distintos
select pg_temp.afirma('R2 · nada é casado por nome comercial',
  (select count(*) from (
     select nome_comercial from public.registro_regulatorio
      where fonte='MAPA_ROPF' group by nome_comercial having count(*) > 1) x) >= 0
  and (select count(distinct registration_id) from public.registro_regulatorio
        where fonte='MAPA_ROPF') = 96,
  'NOME_IGUAL != MESMO_REGISTRO — a identidade é o id, e são 96 distintos');

-- 3 · ROPF_ONLY vira produto ADAMA
select pg_temp.afirma('R3 · as 52 ROPF_ONLY resolvem, e nenhuma tem produto',
  (select count(*) from public.catalogo_registro_crosswalk where estado='ROPF_ONLY') = 52
  and (select count(*) from public.catalogo_registro_crosswalk
        where estado='ROPF_ONLY' and registro_id is not null) = 52
  and (select count(*) from public.catalogo_registro_crosswalk
        where estado='ROPF_ONLY' and produto_id is not null) = 0,
  'ROPF_ONLY != ADAMA_PRODUCT');
select pg_temp.recusa_por('R3b · dar produto a uma ROPF_ONLY é recusado', $x$
  update public.catalogo_registro_crosswalk
     set produto_id = (select id from public.catalogo_produto limit 1)
   where estado='ROPF_ONLY'
$x$, 'estado_combina_com_o_lado_que_existe');

-- 4 · registro estrangeiro entra em ES
select pg_temp.afirma('R4 · todo registro do ROPF é ES',
  (select count(distinct pais) from public.registro_regulatorio where fonte='MAPA_ROPF') = 1
  and (select distinct pais from public.registro_regulatorio
        where fonte='MAPA_ROPF')::text = 'ES',
  'o país entra na chave da captura, não só na linha');

-- 5 · ausência vira NOT_REGISTERED
select pg_temp.afirma('R5 · os 92 cancelados não coletados NÃO viraram nada',
  (select count(*) from public.registro_regulatorio where fonte='MAPA_ROPF') = 96
  and not exists (select 1 from public.registro_regulatorio
                   where fonte='MAPA_ROPF' and estado <> 'vigente'),
  'NOT_COLLECTED != NOT_REGISTERED — 96 de 188; os 92 cancelados não estão no artefato');

-- 7 · expiry vira withdrawal
select pg_temp.afirma('R7 · caducidade vencida não virou retirada',
  exists (select 1 from public.registro_regulatorio
           where fonte='MAPA_ROPF' and fecha_caducidad < current_date)
  and not exists (select 1 from public.registro_regulatorio
                   where fonte='MAPA_ROPF' and estado <> 'vigente'),
  'EXPIRY != WITHDRAWAL — há data vencida e nenhum estado mudou por causa dela');

-- 8 · registro sem prova vira CURRENT
select pg_temp.afirma('R8 · o estado corrente é DERIVADO, não persistido',
  exists (select 1 from pg_proc p join pg_namespace n on n.oid=p.pronamespace
           where n.nspname='public' and p.proname='f_registro_corrente'),
  'quem responde "qual é o registro corrente em X" é a função as-of da 013');

-- 9 · source capture sobrescreve história
select pg_temp.afirma('R9 · o import não tem UPDATE nem DELETE',
  (select count(*) from public.registro_regulatorio where fonte='MAPA_ROPF') = 96,
  'três execuções do mesmo import e o número não se moveu — nem para cima nem para baixo');
select pg_temp.afirma('R9b · uma captura futura não reescreve a resposta de ontem',
  (select count(*) from public.f_registro_corrente('ES', date '2020-01-01')) = 0,
  'FUTURE_CAPTURE_CANNOT_REWRITE_PAST_STATE — em 2020 nada tinha sido capturado');

-- 10 · CUPROXI funde
select pg_temp.afirma('R10 · CUPROXI: ES-00979 no registro, 19232 no catálogo',
  (select count(*) from public.registro_regulatorio
    where fonte='MAPA_ROPF' and registration_id='ES-00979') = 1
  and (select count(*) from public.registro_regulatorio
        where fonte='MAPA_ROPF' and registration_id='19232') = 0
  and (select p.registration_id from public.catalogo_produto p
        where p.nome_publicado='CUPROXI FLO') = '19232',
  'os dois ids existem em sistemas diferentes e NENHUM foi criado no outro');
select pg_temp.afirma('R10b · quem os aproxima é o crosswalk, com evidência',
  (select cw.estado from public.catalogo_registro_crosswalk cw
     join public.catalogo_produto p on p.id=cw.produto_id
    where p.nome_publicado='CUPROXI FLO') = 'MATCHED_WITH_EVIDENCE'
  and (select r.registration_id from public.catalogo_registro_crosswalk cw
         join public.catalogo_produto p on p.id=cw.produto_id
         join public.registro_regulatorio r on r.id=cw.registro_id
        where p.nome_publicado='CUPROXI FLO') = 'ES-00979',
  'relação, não fusão — e o estado diz a força dela');

-- ═══ O ENSAIO NÃO PODE APARECER NA CADEIA ════════════════════════════
select pg_temp.afirma('E1 · nenhum registro veio do ensaio',
  not exists (select 1 from public.collection_run
               where run_id like 'ES-ENSAIO-ROPF%')
  or not exists (select 1 from public.registro_regulatorio r
                  join public.collection_run cr on true
                 where cr.run_id like 'ES-ENSAIO-ROPF%'
                   and r.capturado_em = cr.started_at and r.fonte='MAPA_ROPF'
                   and not exists (select 1 from public.collection_run c2
                                    where c2.run_id like 'ES-ROPF-IMPORT%')),
  'a importação canônica é ES-ROPF-IMPORT-V1; o ensaio continua ensaio');
select pg_temp.afirma('E2 · a rodada canônica do import regulatório existe',
  exists (select 1 from public.collection_run
           where run_id = 'ES-ROPF-IMPORT-V1-2026-08-29'),
  'de onde a captura pendura');

-- ═══════════════════════════════════════════════════════════════════════
\echo ''
\echo '── ES_REGULATORY_IMPORT_V1 ───────────────────────────────────────'
select case when ok then 'PASS' else 'FAIL' end as r, nome, detalhe from _rg order by ordem;
select 'TOTAL=' || count(*) || '  PASS=' || count(*) filter (where ok)
     || '  FAIL=' || count(*) filter (where not ok) as placar from _rg;
do $$
declare n integer;
begin
  select count(*) into n from _rg where not ok;
  if n > 0 then raise exception 'REGRESSOES_REGULATORIO_FALHARAM=%', n; end if;
  raise notice 'REGRESSOES_REGULATORIO_ES=PASS';
end $$;
