-- ═══════════════════════════════════════════════════════════════════════
-- AS CICATRIZES DO BRASIL, EXERCIDAS NO EAME
--
-- Exige 001–015 e o ensaio CICATRIZES-LOCALIZACAO-E-RELEVANCIA.
-- Só lê; os testes negativos desfazem tudo.
-- ═══════════════════════════════════════════════════════════════════════

\set ON_ERROR_STOP on

create temp table _ci (ordem serial, nome text, ok boolean, detalhe text);

create or replace function pg_temp.afirma(n text, cond boolean, det text default '')
returns void language plpgsql as $f$
begin insert into _ci (nome, ok, detalhe) values (n, coalesce(cond,false), det); end $f$;

create or replace function pg_temp.recusa(n text, comando text)
returns void language plpgsql as $f$
begin
  begin
    execute comando;
    raise exception 'ACEITOU_O_QUE_DEVERIA_RECUSAR';
  exception when others then
    if sqlerrm = 'ACEITOU_O_QUE_DEVERIA_RECUSAR' then
      insert into _ci (nome, ok, detalhe) values (n, false, 'o banco ACEITOU o que a lei proíbe');
    else
      insert into _ci (nome, ok, detalhe) values (n, true, 'recusado: ' || left(sqlerrm, 62));
    end if;
  end;
end $f$;

-- Recusar não basta: uma linha pode ser recusada pelo motivo ERRADO e o
-- teste ficar verde sem provar nada. Esta variante exige que a recusa
-- NOMEIE a trava que deveria disparar.
create or replace function pg_temp.recusa_por(n text, comando text, trava text)
returns void language plpgsql as $f$
declare msg text;
begin
  -- O comando roda DENTRO de um bloco com EXCEPTION, que é uma
  -- subtransação. Se ele passar, `raise` desfaz o que ele fez — sem isso,
  -- um teste negativo que ACEITA deixa a mutação no banco e envenena todas
  -- as afirmações seguintes. Foi exatamente o que aconteceu na primeira
  -- execução da suíte do catálogo: um UPDATE passou, virou 41 linhas, e os
  -- contadores do gate reprovaram por culpa do teste, não do dado.
  begin
    execute comando;
    raise exception 'ACEITOU_O_QUE_DEVERIA_RECUSAR';
  exception when others then msg := sqlerrm;
  end;
  if msg = 'ACEITOU_O_QUE_DEVERIA_RECUSAR' then
    insert into _ci (nome, ok, detalhe) values (n, false, 'o banco ACEITOU o que a lei proíbe');
    return;
  end if;
  if position(trava in msg) > 0 then
    insert into _ci (nome, ok, detalhe) values (n, true, 'recusado por ' || trava);
  else
    insert into _ci (nome, ok, detalhe) values (n, false,
      'recusado pelo motivo ERRADO — esperava ' || trava || ', veio: ' || left(msg, 70));
  end if;
end $f$;

create or replace function pg_temp.loc(cid text)
returns public.v_conteudo_localizacao language sql stable as $f$
  select l.* from public.v_conteudo_localizacao l
    join public.conteudo c on c.id = l.conteudo_id where c.content_id = cid;
$f$;


-- ═══ LOCALIZAÇÃO · os casos ══════════════════════════════════════════
-- A cicatriz: no Brasil a praça do CANAL carimbava a praça do documento, e
-- 44 pessoas "discutiam nematoide de café" numa praça com 7.868 ha de café.
--
-- Reescrito na 018: o lugar do fato deixou de ser uma coluna e passou a ser
-- `conteudo_lugar`, porque a coluna expressava 0..1 e o mundo é 0..N.

create or replace function pg_temp.lugares(cid text)
returns setof public.conteudo_lugar language sql stable as $f$
  select cl.* from public.conteudo_lugar cl
    join public.conteudo c on c.id = cl.conteudo_id
   where c.content_id = cid and cl.papel = 'FACT';
$f$;

select pg_temp.afirma('A · fonte na região A relata fato na região B',
  (pg_temp.loc('ENSAIO-A')).source_place = 'Foggia'
  and (pg_temp.loc('ENSAIO-A')).fact_places = array['Toscana'],
  'a fonte é de Foggia e o fato é da Toscana; nenhuma virou a outra');

select pg_temp.afirma('B · fonte tem lugar, fato não tem',
  (pg_temp.loc('ENSAIO-B')).source_place = 'Foggia'
  and (pg_temp.loc('ENSAIO-B')).fact_location_desconhecido
  and (pg_temp.loc('ENSAIO-B')).fact_locations = 0,
  'o lugar da fonte NÃO preencheu o lugar do fato');

select pg_temp.afirma('C · o fato nomeia a província',
  (pg_temp.loc('ENSAIO-C')).fact_places = array['Jaén']
  and (pg_temp.loc('ENSAIO-C')).fact_precisions = array['PROVINCIA']
  and (select origem_do_dado from pg_temp.lugares('ENSAIO-C')) = 'ESCRITO',
  'província nomeada e escrita, com evidência');

select pg_temp.afirma('D · país conhecido, região desconhecida',
  (pg_temp.loc('ENSAIO-D')).fact_country::text = 'IT'
  and (pg_temp.loc('ENSAIO-D')).fact_precisions = array['PAIS'],
  'o país não faz as vezes de uma região');

select pg_temp.afirma('E · todo lugar do fato carrega COMO se soube',
  not exists (select 1 from public.conteudo_lugar
               where papel = 'FACT'
                 and (origem_do_dado is null or evidencia is null
                      or ancora is null or tipo_de_evidencia is null)),
  'sem origem, trecho, âncora e espécie de evidência, o lugar do fato não entra');

select pg_temp.recusa_por('E2 · o lugar da FONTE não sustenta o lugar do FATO', $x$
  insert into public.conteudo_lugar
    (conteudo_id, lugar_texto, geografia_id, estado_do_lugar, papel,
     tipo_de_evidencia, origem_do_dado, evidencia, ancora, rule_version)
  select ct.id, 'Foggia', g.id, 'RESOLVIDO', 'FACT', 'FIELD_OBSERVATION',
         'DA_FONTE', 'a ficha do canal diz Foggia', 'sede', 'ensaio'
    from public.conteudo ct, public.geografia g
   where ct.content_id='ENSAIO-B' and g.provincia='Foggia'
$x$, 'so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato');

select pg_temp.recusa_por('E3 · localização inferida nunca vira declarada', $x$
  insert into public.conteudo_lugar
    (conteudo_id, lugar_texto, geografia_id, estado_do_lugar, papel,
     tipo_de_evidencia, origem_do_dado, evidencia, ancora, rule_version)
  select ct.id, 'Toscana', g.id, 'RESOLVIDO', 'FACT', 'FIELD_OBSERVATION',
         'DEDUZIDO', 'a inteligência inferiu pela audiência', 'inferido', 'ensaio'
    from public.conteudo ct, public.geografia g
   where ct.content_id='ENSAIO-B' and g.regiao='Toscana' and g.provincia is null
     and g.municipio is null
$x$, 'so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato');

select pg_temp.recusa_por('E4 · lugar do fato sem o trecho que o sustenta', $x$
  insert into public.conteudo_lugar
    (conteudo_id, lugar_texto, geografia_id, estado_do_lugar, papel,
     tipo_de_evidencia, origem_do_dado, ancora, rule_version)
  select ct.id, 'Toscana', g.id, 'RESOLVIDO', 'FACT', 'FIELD_OBSERVATION',
         'ESCRITO', 'osservata', 'ensaio'
    from public.conteudo ct, public.geografia g
   where ct.content_id='ENSAIO-B' and g.regiao='Toscana' and g.provincia is null
     and g.municipio is null
$x$, 'lugar_do_fato_diz_como_se_soube');


-- ═══ RELEVÂNCIA · ela mora no conteúdo ═══════════════════════════════
select pg_temp.afirma('R1 · sinal exato quando cultura, problema e país conferem',
  (select r.relevancia from public.conteudo_crop_issue cc
     join public.conteudo ct on ct.id=cc.conteudo_id
     join public.crop_issue ci on ci.id=cc.crop_issue_id
     join public.crop c on c.id=ci.crop_id join public.issue i on i.id=ci.issue_id,
     lateral public.f_relevancia_ao_caso(cc.id,'ENSAIO_CROP_A','ENSAIO_ISSUE_A','IT') r
    where ct.content_id='ENSAIO-A' and c.codigo='ENSAIO_CROP_A'
      and i.codigo='ENSAIO_ISSUE_A' and cc.relacao='OCORRENCIA_DECLARADA') = 'EXACT_SIGNAL',
  'cultura, problema, país e janela conferem');

select pg_temp.afirma('R2 · RIGHT_CLASS + WRONG_CROP != CASE_SIGNAL',
  (select r.relevancia from public.conteudo_crop_issue cc
     join public.conteudo ct on ct.id=cc.conteudo_id
     join public.crop_issue ci on ci.id=cc.crop_issue_id
     join public.crop c on c.id=ci.crop_id join public.issue i on i.id=ci.issue_id,
     lateral public.f_relevancia_ao_caso(cc.id,'ENSAIO_CROP_A','ENSAIO_ISSUE_A','IT') r
    where ct.content_id='ENSAIO-A' and c.codigo='ENSAIO_CROP_B') = 'UNRELATED',
  'ocorrência declarada de outra cultura não é sinal do caso');

select pg_temp.afirma('R3 · RIGHT_CROP + WRONG_ISSUE != CASE_SIGNAL',
  (select r.relevancia from public.conteudo_crop_issue cc
     join public.conteudo ct on ct.id=cc.conteudo_id
     join public.crop_issue ci on ci.id=cc.crop_issue_id
     join public.crop c on c.id=ci.crop_id join public.issue i on i.id=ci.issue_id,
     lateral public.f_relevancia_ao_caso(cc.id,'ENSAIO_CROP_A','ENSAIO_ISSUE_A','IT') r
    where ct.content_id='ENSAIO-A' and i.codigo='ENSAIO_ISSUE_B') = 'UNRELATED',
  'ocorrência declarada de outro problema não é sinal do caso');

select pg_temp.afirma('R4 · KEYWORD_MATCH != RELEVANT_EVIDENCE',
  (select r.relevancia from public.conteudo_crop_issue cc
     join public.conteudo ct on ct.id=cc.conteudo_id,
     lateral public.f_relevancia_ao_caso(cc.id,'ENSAIO_CROP_A','ENSAIO_ISSUE_A','ES') r
    where ct.content_id='ENSAIO-C' and cc.relacao='COOCORRENCIA_TEXTUAL') = 'CONTEXT_ONLY',
  'coocorrência textual nunca passa de contexto');

select pg_temp.afirma('R5 · sem lugar do fato, é contexto e não sinal',
  (select r.relevancia from public.conteudo_crop_issue cc
     join public.conteudo ct on ct.id=cc.conteudo_id,
     lateral public.f_relevancia_ao_caso(cc.id,'ENSAIO_CROP_A','ENSAIO_ISSUE_A','IT') r
    where ct.content_id='ENSAIO-B' and cc.relacao='OCORRENCIA_DECLARADA') = 'CONTEXT_ONLY',
  'ocorrência sem lugar sustentado serve de contexto');

select pg_temp.afirma('R6 · país A não fecha pergunta do país B',
  (select r.relevancia from public.conteudo_crop_issue cc
     join public.conteudo ct on ct.id=cc.conteudo_id,
     lateral public.f_relevancia_ao_caso(cc.id,'ENSAIO_CROP_A','ENSAIO_ISSUE_A','IT') r
    where ct.content_id='ENSAIO-C' and cc.relacao='COOCORRENCIA_TEXTUAL') <> 'EXACT_SIGNAL',
  'o fato é da Espanha e a pergunta é da Itália');

select pg_temp.afirma('R7 · espectro de rótulo não é ocorrência',
  (select r.relevancia from public.conteudo_crop_issue cc
     join public.conteudo ct on ct.id=cc.conteudo_id,
     lateral public.f_relevancia_ao_caso(cc.id,'ENSAIO_CROP_A','ENSAIO_ISSUE_A','IT') r
    where ct.content_id='ENSAIO-D' and cc.relacao='ESPECTRO_DE_PRODUTO') = 'CONTEXT_ONLY',
  'lista de rótulo é espectro, não ocorrência observada');

select pg_temp.afirma('R8 · RIGHT_TOPIC + WRONG_YEAR != CASE_SIGNAL',
  (select r.relevancia from public.conteudo_crop_issue cc
     join public.conteudo ct on ct.id=cc.conteudo_id
     join public.crop_issue ci on ci.id=cc.crop_issue_id
     join public.crop c on c.id=ci.crop_id join public.issue i on i.id=ci.issue_id,
     lateral public.f_relevancia_ao_caso(cc.id,'ENSAIO_CROP_A','ENSAIO_ISSUE_A','IT',
                                         date '2026-07-01', date '2026-12-31') r
    where ct.content_id='ENSAIO-A' and c.codigo='ENSAIO_CROP_A'
      and i.codigo='ENSAIO_ISSUE_A' and cc.relacao='OCORRENCIA_DECLARADA') = 'RETROSPECTIVE',
  'publicado antes da janela do caso: retrospectivo, não sinal corrente');

select pg_temp.afirma('R9 · toda relevância vem com o MOTIVO escrito',
  not exists (
    select 1 from public.conteudo_crop_issue cc,
      lateral public.f_relevancia_ao_caso(cc.id,'ENSAIO_CROP_A','ENSAIO_ISSUE_A','IT') r
     where r.porque is null or r.porque = ''),
  'a pergunta "por que este conteúdo entrou?" tem sempre resposta');

select pg_temp.afirma('R10 · não existe score de relevância',
  not exists (select 1 from information_schema.columns
               where table_schema='public' and table_name='conteudo_crop_issue'
                 and column_name ~ '(score|peso|nota|rank|pontua)'),
  'relevância é estado com motivo, nunca número');


-- ═══ PROVENIÊNCIA · PAID_RESULT != PRESERVED_RESULT ══════════════════
select pg_temp.afirma('P1 · ator executou, item voltou, RAW sumiu = NÃO preservado',
  (select veredito from public.f_runs_pagos_sem_bruto()
    where run_id='ENSAIO-RUN-PAGO-SEM-BRUTO') = 'PAGO_E_NAO_PRESERVADO',
  'o defeito italiano tem nome e sai na consulta');

select pg_temp.afirma('P2 · rodada sem item não é rodada não preservada',
  (select veredito from public.f_runs_pagos_sem_bruto()
    where run_id='ENSAIO-RUN-VAZIA') = 'SEM_ITEM_NADA_A_PRESERVAR',
  'vazia é um estado, não um defeito');

select pg_temp.afirma('P3 · bruto ausente exige motivo escrito',
  exists (select 1 from pg_constraint where conname='bruto_ausente_precisa_de_motivo'),
  'NOT_PRESERVED é declarado, nunca silêncio');

select pg_temp.afirma('P4 · custo declarado diz COMO foi medido',
  exists (select 1 from pg_constraint where conname='custo_declarado_diz_como_foi_medido'),
  'três métodos na mesma coluna foi o pior defeito de proveniência do Brasil');


-- ═══ AUSÊNCIA · NOT_MEASURED != ABSENT ═══════════════════════════════
select pg_temp.afirma('N1 · o mundo, a instalação e nós são estados diferentes',
  (select count(distinct estado) from public.tentativa_de_coleta
    where estado in ('RESPONDEU_SEM_O_CAMPO','LOGIN_WALL','NAO_TESTADO',
                     'SEM_CHECKPOINT_NAO_GASTEI')) = 4,
  'no Brasil os três viraram um só e 299 fichas foram contadas como ausência');

select pg_temp.recusa('N2 · um estado de tentativa fora do vocabulário é recusado', $x$
  insert into public.tentativa_de_coleta (alvo, estado, motivo, observado_em, rule_version)
  values ('x','SEM_CIDADE','o perfil não declara lugar', now(), 'ensaio')
$x$);

select pg_temp.afirma('N3 · toda tentativa carrega o motivo',
  not exists (select 1 from public.tentativa_de_coleta where motivo is null or motivo=''),
  'FAILED_WITH_REASON, nunca FAILED');


-- ═══ A CONFERÊNCIA DE LOCALIZAÇÃO (017) ══════════════════════════════
-- A rodada anterior marcou o contrato de localização como completo. A
-- conferência contra dez cicatrizes mais novas achou seis lacunas; duas
-- produziam RESPOSTA ERRADA e foram consertadas. Estas são as testemunhas.

create or replace function pg_temp.rel(cid text, ini date, fim date)
returns text language sql stable as $f$
  select r.relevancia
    from public.conteudo_crop_issue cc
    join public.conteudo ct on ct.id = cc.conteudo_id
    join public.crop_issue ci on ci.id = cc.crop_issue_id
    join public.crop  c on c.id = ci.crop_id  and c.codigo = 'ENSAIO_CROP_A'
    join public.issue i on i.id = ci.issue_id and i.codigo = 'ENSAIO_ISSUE_A',
    lateral public.f_relevancia_ao_caso(cc.id,'ENSAIO_CROP_A','ENSAIO_ISSUE_A','IT',
                                        ini, fim) r
   where ct.content_id = cid;
$f$;

-- I · PUBLISHED_AT != FACT_TIME
select pg_temp.afirma('C1 · publicado DEPOIS da janela não vira UNRELATED',
  pg_temp.rel('ENSAIO-A', date '2026-01-01', date '2026-03-01') = 'CONTEXT_ONLY',
  'um documento de setembro pode relatar um fato de junho — a 015 devolvia UNRELATED');

select pg_temp.afirma('C2 · publicado ANTES da janela continua RETROSPECTIVE',
  pg_temp.rel('ENSAIO-A', date '2026-09-01', date '2026-12-01') = 'RETROSPECTIVE',
  'a data de publicação decide numa direção só: documento não relata o futuro');

select pg_temp.afirma('C3 · dentro da janela, o sinal exato continua exato',
  pg_temp.rel('ENSAIO-A', date '2026-05-01', date '2026-07-01') = 'EXACT_SIGNAL',
  'sem isto, P1 e P2 estariam verdes só porque a função parou de dizer sim');

-- B · PLACE_MENTION != FACT_LOCATION
select pg_temp.afirma('C4 · lugar do fato só MENCIONADO não é sinal exato',
  pg_temp.rel('ENSAIO-E', date '2026-05-01', date '2026-07-01') = 'CONTEXT_ONLY',
  'cultura, problema, país e janela conferem; o lugar veio de menção, e menção não afirma');

select pg_temp.afirma('C5 · a menção aparece na visão, em vez de passar despercebida',
  (pg_temp.loc('ENSAIO-E')).fact_sustentado_apenas_por_mencao
  and (select origem_do_dado from pg_temp.lugares('ENSAIO-E')) = 'CITADO',
  'mencionado e afirmado chegam ao consumidor com nomes diferentes');

select pg_temp.afirma('C6 · afirmado no texto continua sendo afirmado',
  (select origem_do_dado from pg_temp.lugares('ENSAIO-A')) = 'ESCRITO'
  and not (pg_temp.loc('ENSAIO-A')).fact_sustentado_apenas_por_mencao,
  'a distinção sobrevive por LINHA, e não marca tudo como menção');

-- As lacunas A e E, que a conferência deixou abertas, FECHARAM na 018.
-- As duas afirmações abaixo eram "continua aberta e DECLARADA"; agora são
-- a prova de que fecharam. Inverter um teste sem inverter o mecanismo seria
-- mover a régua — o mecanismo está em supabase/tests/regressoes_lugar_do_fato.sql.
select pg_temp.afirma('C7 · lacuna A fechada: as espécies de lugar têm dono',
  exists (select 1 from information_schema.tables
           where table_schema='public' and table_name='origem_lugar')
  and (select count(distinct papel) from public.origem_lugar
        where papel in ('BASE','OPERATING','INFLUENCE')) = 3,
  'BASE, OPERATING e INFLUENCE deixaram de colapsar na praça da fonte');

select pg_temp.afirma('C8 · lacuna E fechada: um conteúdo tem 0..N lugares do fato',
  not exists (select 1 from information_schema.columns
               where table_schema='public' and table_name='conteudo'
                 and column_name='fact_geografia_id')
  and (pg_temp.loc('ENSAIO-F')).fact_locations = 3,
  'a coluna 0..1 foi APOSENTADA, e o documento de três províncias tem três');


-- ═══════════════════════════════════════════════════════════════════════
\echo ''
\echo '── AS CICATRIZES DO BRASIL NO EAME ───────────────────────────────'
select case when ok then 'PASS' else 'FAIL' end as r, nome, detalhe
  from _ci order by ordem;
select 'TOTAL=' || count(*) || '  PASS=' || count(*) filter (where ok)
     || '  FAIL=' || count(*) filter (where not ok) as placar from _ci;
do $$
declare n integer;
begin
  select count(*) into n from _ci where not ok;
  if n > 0 then raise exception 'REGRESSOES_CICATRIZES_FALHARAM=%', n; end if;
  raise notice 'REGRESSOES_CICATRIZES=PASS';
end $$;
