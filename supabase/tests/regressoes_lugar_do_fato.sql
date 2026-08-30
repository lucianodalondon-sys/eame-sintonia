-- ═══════════════════════════════════════════════════════════════════════
-- O LUGAR DO FATO — as cinco cicatrizes que faltavam
--
-- Exige 001–018 e o ensaio CICATRIZES-LOCALIZACAO-E-RELEVANCIA.
-- Só lê; os testes negativos desfazem tudo.
--
--   BR-26  BASE != OPERATING != INFLUENCE != FACT
--   BR-30  0..N lugares do fato por conteúdo
--   BR-31  a escada de precisão
--   BR-32  TERRITORIAL_LIST != FACT_LIST
--   BR-34  PUBLISHED_AT != FACT_TIME
--
-- Mais as duas leis que a Itália provou em texto real:
--   SOURCE_GEOGRAPHY != ADMIN_GEOGRAPHY
--   NOT_IN_GAZETTEER != NOT_A_PLACE != REJECTED_BY_LAW
--
-- Os casos NÃO foram desenhados para passar. Cada um é a forma de um falso
-- positivo já medido — no Brasil ou na Itália — e o teste é a tentativa de
-- reproduzi-lo aqui.
-- ═══════════════════════════════════════════════════════════════════════

\set ON_ERROR_STOP on

create temp table _lf (ordem serial, nome text, ok boolean, detalhe text);

create or replace function pg_temp.afirma(n text, cond boolean, det text default '')
returns void language plpgsql as $f$
begin insert into _lf (nome, ok, detalhe) values (n, coalesce(cond,false), det); end $f$;

-- Recusar pelo motivo errado é um teste verde que não prova nada. A trava
-- esperada tem de aparecer na mensagem.
create or replace function pg_temp.recusa_por(n text, comando text, trava text)
returns void language plpgsql as $f$
declare msg text;
begin
  begin
    execute comando;
    insert into _lf (nome, ok, detalhe) values (n, false, 'o banco ACEITOU o que a lei proíbe');
    return;
  exception when others then msg := sqlerrm;
  end;
  if position(trava in msg) > 0 then
    insert into _lf (nome, ok, detalhe) values (n, true, 'recusado por ' || trava);
  else
    insert into _lf (nome, ok, detalhe) values (n, false,
      'recusado pelo motivo ERRADO — esperava ' || trava || ', veio: ' || left(msg, 70));
  end if;
end $f$;

create or replace function pg_temp.fatos(cid text)
returns setof public.conteudo_lugar language sql stable as $f$
  select cl.* from public.conteudo_lugar cl
    join public.conteudo c on c.id = cl.conteudo_id
   where c.content_id = cid and cl.papel = 'FACT';
$f$;

create or replace function pg_temp.cid(c text) returns bigint language sql stable as $f$
  select id from public.conteudo where content_id = c;
$f$;

create or replace function pg_temp.loc(cid text)
returns public.v_conteudo_localizacao language sql stable as $f$
  select l.* from public.v_conteudo_localizacao l
    join public.conteudo c on c.id = l.conteudo_id where c.content_id = cid;
$f$;


-- ═══ BR-26 · BASE != OPERATING != INFLUENCE != FACT ══════════════════
-- O caso obrigatório da missão: pesquisador baseado em Foggia, instituição
-- atuando nacionalmente, audiência italiana, fato em Grosseto. Quatro
-- lugares verdadeiros ao mesmo tempo, e nenhum sobrescreve outro.

select pg_temp.afirma('L1 · as três espécies do sujeito coexistem',
  (select count(distinct papel) from public.origem_lugar ol
     join public.origem o on o.id = ol.origem_id
    where o.rotulo='ORIGEM ENSAIO PESQUISADOR') = 3,
  'BASE, OPERATING e INFLUENCE na mesma ficha, sem uma apagar a outra');

select pg_temp.afirma('L2 · a BASE do sujeito é Foggia e continua sendo',
  (select g.provincia from public.origem_lugar ol
     join public.origem o on o.id = ol.origem_id
     join public.geografia g on g.id = ol.geografia_id
    where o.rotulo='ORIGEM ENSAIO PESQUISADOR' and ol.papel='BASE') = 'Foggia',
  'o perfil declara Foggia, e isso é BASE — no máximo');

select pg_temp.afirma('L3 · e o FATO do documento é Grosseto, não Foggia',
  (select lugar_texto from pg_temp.fatos('ENSAIO-G')) = 'Grosseto',
  'os quatro lugares coexistem: três do sujeito, um do que ele escreveu');

-- A mutação central desta cicatriz: promover BASE a FACT.
select pg_temp.afirma('L4 · FACT não está no vocabulário dos lugares do sujeito',
  not exists (select 1 from pg_constraint
               where conrelid='public.origem_lugar'::regclass and contype='c'
                 and pg_get_constraintdef(oid) like '%papel%'
                 and pg_get_constraintdef(oid) like '%FACT%'),
  'não há como declarar que a sede de alguém é o lugar de um fato');

select pg_temp.recusa_por('L5 · promover BASE a FACT é recusado pelo vocabulário', $x$
  insert into public.origem_lugar
    (origem_id, geografia_id, papel, origem_do_dado, evidencia, rule_version)
  select o.id, g.id, 'FACT', 'DECLARADO_NO_PERFIL', 'o perfil diz Foggia', 'ensaio'
    from public.origem o, public.geografia g
   where o.rotulo='ORIGEM ENSAIO PESQUISADOR' and g.provincia='Foggia'
$x$, 'origem_lugar_papel_check');

-- E o caminho de volta: a SEDE mencionada num conteúdo não vira fato.
select pg_temp.afirma('L6 · a sede citada no documento fica como MENCAO_APENAS',
  (select papel from public.conteudo_lugar
    where conteudo_id = pg_temp.cid('ENSAIO-G') and lugar_texto='Bergamo')
   = 'MENCAO_APENAS',
  'Bergamo aparecia num artigo italiano real e não era recusada por lei nenhuma: '
  'era invisível. Aqui ela existe, com o papel certo');

select pg_temp.recusa_por('L7 · a sede promovida a FACT é recusada', $x$
  insert into public.conteudo_lugar
    (conteudo_id, lugar_texto, geografia_id, estado_do_lugar, papel,
     tipo_de_evidencia, origem_do_dado, evidencia, ancora, rule_version)
  select pg_temp.cid('ENSAIO-G'), 'Bergamo', g.id, 'RESOLVIDO', 'FACT',
         'CONFIRMED_FOCUS', 'DA_FONTE', 'sede da empresa', 'sede', 'ensaio'
    from public.geografia g where g.provincia='Bergamo'
$x$, 'so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato');


-- ═══ BR-30 · 0..N LUGARES DO FATO ════════════════════════════════════
-- "campioni positivi provenienti da Grosseto, Siena e Arezzo" são TRÊS.

select pg_temp.afirma('N1 · um documento sustenta três lugares do fato',
  (select count(*) from pg_temp.fatos('ENSAIO-F')) = 3,
  'ficar com a primeira cidade inventaria um recorte que a fonte não fez');

select pg_temp.afirma('N2 · os três vêm como lista, não como string colada',
  (pg_temp.loc('ENSAIO-F')).fact_places = array['Arezzo','Grosseto','Siena'],
  'concatenar destruiria a possibilidade de cruzar qualquer um deles');

select pg_temp.afirma('N3 · cada um dos três carrega a SUA evidência',
  (select count(*) from pg_temp.fatos('ENSAIO-F')
    where evidencia is not null and ancora is not null) = 3,
  'VALUE_PROVENANCE: a evidência é do lugar, não da linha');

select pg_temp.afirma('N4 · zero lugares do fato é uma resposta, não um vazio',
  (pg_temp.loc('ENSAIO-B')).fact_locations = 0
  and (pg_temp.loc('ENSAIO-B')).fact_location_desconhecido,
  '0..N inclui o zero, e ele é dizível');

select pg_temp.afirma('N5 · o dono antigo, de 0..1, não existe mais',
  not exists (select 1 from information_schema.columns
               where table_schema='public' and table_name='conteudo'
                 and column_name in ('fact_geografia_id','fact_geografia_origem',
                                     'fact_geografia_evidencia')),
  'DOIS DONOS DA MESMA LEI é o defeito que a 016 já cometeu uma vez');


-- ═══ BR-31 · A ESCADA DE PRECISÃO ════════════════════════════════════

select pg_temp.afirma('P1 · a escada chega a MUNICIPIO',
  (pg_temp.loc('ENSAIO-L')).fact_precisions = array['MUNICIPIO'],
  '"nel comune di Manciano" é mais específico que a província, e agora cabe');

select pg_temp.afirma('P2 · a escada tem os seis degraus administrativos',
  (select count(*) from public.escada_de_precisao() where administrativo) = 6,
  'PAIS < REGIAO < PROVINCIA < MUNICIPIO < LOCALIDADE < COORDENADA');

select pg_temp.afirma('P3 · a precisão nasce da LINHA, nunca do texto',
  public.precisao_da_geografia(
    (select id from public.geografia
      where pais='IT' and regiao='Toscana' and provincia is null
        and municipio is null and especie='ADMIN')) = 'REGIAO',
  'SOURCE SAYS REGION != INVENT MUNICIPALITY');

select pg_temp.afirma('P4 · província não vira município por conveniência',
  public.precisao_da_geografia(
    (select id from public.geografia
      where pais='IT' and provincia='Grosseto' and municipio is null)) = 'PROVINCIA',
  'mais específico só nasce de evidência mais específica');

select pg_temp.recusa_por('P5 · meia coordenada é recusada', $x$
  insert into public.geografia (pais, regiao, provincia, lat)
  values ('IT','Toscana','Livorno', 43.5)
$x$, 'coordenada_vem_inteira');


-- ═══ SOURCE_GEOGRAPHY != ADMIN_GEOGRAPHY ═════════════════════════════
-- A cicatriz que a Itália achou em texto real: "l'Ovest", "areale nord".

select pg_temp.afirma('S1 · a zona da fonte NÃO entra na escada administrativa',
  (pg_temp.loc('ENSAIO-I')).fact_precisions = array['ZONA_DEFINIDA_PELA_FONTE'],
  'forçá-la para REGIAO seria geocodificar por conveniência');

select pg_temp.afirma('S2 · a zona da fonte tem ordem 0, não "menos que província"',
  (select ordem from public.escada_de_precisao()
    where degrau='ZONA_DEFINIDA_PELA_FONTE') = 0
  and not (select administrativo from public.escada_de_precisao()
            where degrau='ZONA_DEFINIDA_PELA_FONTE'),
  'ela não é menos precisa que província: é incomparável, e a régua diz isso');

select pg_temp.afirma('S3 · o nome que a fonte usou é guardado inteiro',
  (select nome_da_fonte from public.geografia where especie='DEFINIDA_PELA_FONTE'
     and nome_da_fonte like '%Ovest%') is not null,
  'guardar o recorte inteiro é o oposto de aproximá-lo');

select pg_temp.recusa_por('S4 · zona da fonte fingindo divisão administrativa é recusada', $x$
  insert into public.geografia (pais, especie, regiao, nome_da_fonte)
  values ('IT','DEFINIDA_PELA_FONTE','Toscana','areale sud')
$x$, 'zona_da_fonte_nao_e_divisao_administrativa');


-- ═══ BR-32 · TERRITORIAL_LIST != FACT_LIST ═══════════════════════════
-- "atuamos em A, B e C" — a maior fábrica de falso positivo do Brasil.

select pg_temp.afirma('T1 · a lista econômica existe no banco, com o papel certo',
  (select count(*) from public.conteudo_lugar
    where conteudo_id = pg_temp.cid('ENSAIO-H') and papel='LISTA_TERRITORIAL') = 3,
  'guardá-la é o que permite PROVAR que ela não virou ocorrência');

select pg_temp.afirma('T2 · e nenhum dos três é lugar do fato',
  (pg_temp.loc('ENSAIO-H')).fact_locations = 0,
  'três lugares no documento, zero ocorrências');

select pg_temp.recusa_por('T3 · lista nua promovida a FACT é recusada', $x$
  insert into public.conteudo_lugar
    (conteudo_id, lugar_texto, geografia_id, estado_do_lugar, papel,
     tipo_de_evidencia, origem_do_dado, evidencia, ancora, rule_version)
  select pg_temp.cid('ENSAIO-H'), 'Torino', g.id, 'RESOLVIDO', 'FACT',
         'FIELD_OBSERVATION', 'LISTA_TERRITORIAL', 'operiamo in Torino',
         'operiamo', 'ensaio'
    from public.geografia g where g.provincia='Torino'
$x$, 'so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato');

-- A trava é UMA lista branca, e três leis dependem do que está nela. Fixar
-- o conteúdo é o que impede que alargá-la mate as três de uma vez, em
-- silêncio e sem que nenhuma outra afirmação reprove.
select pg_temp.afirma('T3b · a lista branca tem exatamente ESCRITO e CITADO',
  (select pg_get_constraintdef(oid) from pg_constraint
    where conname='so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato')
   like '%''ESCRITO''%''CITADO''%'
  and not exists (
    select 1 from unnest(array['DA_FONTE','DEDUZIDO','LISTA_TERRITORIAL','NAO_SEI']) t(fora)
     where (select pg_get_constraintdef(oid) from pg_constraint
             where conname='so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato')
           like '%' || t.fora || '%'),
  'LOCAL_DA_FONTE, DEDUZIDO e TERRITORIAL_LIST ficam de fora — os três pela mesma trava');

select pg_temp.afirma('T4 · a guarda do eixo do PRODUTO continua onde estava',
  exists (select 1 from public.conteudo_crop_issue
           where relacao='ESPECTRO_DE_PRODUTO'),
  'a lista de rótulo já era CONTEXT_ONLY; agora o eixo da geografia tem a dele');


-- ═══ OCCURRENCE != INCIDENCE ═════════════════════════════════════════

select pg_temp.afirma('O1 · a contagem sai POR espécie de evidência',
  (select count(*) from public.f_ocorrencia_nao_e_incidencia(pg_temp.cid('ENSAIO-F'))) = 1
  and (select quantos from public.f_ocorrencia_nao_e_incidencia(pg_temp.cid('ENSAIO-F'))
        where tipo_de_evidencia='DIAGNOSTIC_SAMPLE') = 3,
  'três amostras de diagnóstico, e a função não as chama de incidência');

select pg_temp.afirma('O2 · amostra positiva NÃO autoriza dizer incidência',
  (select tipo_de_evidencia from pg_temp.fatos('ENSAIO-M')) = 'DIAGNOSTIC_SAMPLE'
  and not exists (select 1 from public.f_ocorrencia_nao_e_incidencia(pg_temp.cid('ENSAIO-M'))
                   where tipo_de_evidencia='INCIDENCE_MEASUREMENT'),
  'POSITIVE_SAMPLE != REGIONAL_INCIDENCE');

select pg_temp.recusa_por('O3 · lugar do fato sem espécie de evidência é recusado', $x$
  insert into public.conteudo_lugar
    (conteudo_id, lugar_texto, geografia_id, estado_do_lugar, papel,
     origem_do_dado, evidencia, ancora, rule_version)
  select pg_temp.cid('ENSAIO-B'), 'Siena', g.id, 'RESOLVIDO', 'FACT',
         'ESCRITO', 'campioni positivi', 'campioni', 'ensaio'
    from public.geografia g where g.provincia='Siena'
$x$, 'lugar_do_fato_declara_a_especie_da_evidencia');

select pg_temp.afirma('O4 · não nasceu coluna de score em lugar nenhum',
  not exists (select 1 from information_schema.columns
               where table_schema='public'
                 and table_name in ('conteudo_lugar','origem_lugar')
                 and column_name ~ '(score|peso|nota|rank|pontua|forca)'),
  'a força da evidência é a ESPÉCIE dela, e espécies não viram número');


-- ═══ BR-34 · PUBLISHED_AT != FACT_TIME ═══════════════════════════════

select pg_temp.afirma('F1 · o tempo do fato tem campo próprio',
  (select fact_tempo_texto from public.conteudo where content_id='ENSAIO-J')
   = 'stagione 2025',
  'publicado em 13/02/2026 e o fato é da safra 2025');

select pg_temp.afirma('F2 · e a data de publicação continua sendo outra coisa',
  (select publicado_em::date from public.conteudo where content_id='ENSAIO-J')
   = date '2026-02-13'
  and (select fact_tempo_resolucao from public.conteudo where content_id='ENSAIO-J')::text
   = 'SEASON',
  'os dois lado a lado, e a precisão do fato é SEASON, não DATE_EXACT');

select pg_temp.afirma('F3 · PUBLICACAO não existe no vocabulário de origem do tempo',
  (select pg_get_constraintdef(oid) from pg_constraint
    where conname like '%fact_tempo_origem%') not like '%PUBLICACAO%',
  'a ausência é a trava: não há como declarar que o tempo veio do carimbo');

select pg_temp.recusa_por('F4 · tempo do fato sem evidência é recusado', $x$
  update public.conteudo set fact_tempo_texto='stagione 2024'
   where content_id='ENSAIO-A'
$x$, 'tempo_do_fato_diz_como_se_soube');

select pg_temp.afirma('F5 · sem tempo do fato, o campo fica vazio e isso é dizível',
  (select tempo_do_fato_desconhecido from public.v_lugar_do_fato
    where content_id='ENSAIO-A' limit 1),
  'a maioria dos conteúdos não diz quando o fato foi, e fingir seria pior');


-- ═══ NOT_IN_GAZETTEER != NOT_A_PLACE != REJECTED_BY_LAW ══════════════

select pg_temp.afirma('G1 · um lugar fora da lista não desaparece',
  (select lugar_texto from pg_temp.fatos('ENSAIO-K')) = 'Roccalbegna',
  'a nossa lacuna não pode virar lacuna do mundo');

select pg_temp.afirma('G2 · e ele diz que está fora, em vez de fingir resolução',
  (select estado_do_lugar from pg_temp.fatos('ENSAIO-K')) = 'NAO_ESTA_NO_GAZETTEER'
  and (select geografia_id from pg_temp.fatos('ENSAIO-K')) is null,
  'três respostas diferentes que no Brasil saíam idênticas do outro lado');

select pg_temp.afirma('G3 · a precisão dele é NOT_KNOWN, não uma província chutada',
  (pg_temp.loc('ENSAIO-K')).fact_precisions = array['NOT_KNOWN']
  and (pg_temp.loc('ENSAIO-K')).lugares_fora_do_gazetteer = 1,
  'não resolver é diferente de resolver errado');

select pg_temp.recusa_por('G4 · dizer RESOLVIDO sem apontar geografia é recusado', $x$
  insert into public.conteudo_lugar
    (conteudo_id, lugar_texto, geografia_id, estado_do_lugar, papel,
     tipo_de_evidencia, origem_do_dado, evidencia, ancora, rule_version)
  values (pg_temp.cid('ENSAIO-B'), 'Roccalbegna', null, 'RESOLVIDO', 'FACT',
          'CONFIRMED_FOCUS', 'ESCRITO', 'constatato a Roccalbegna', 'constatato', 'ensaio')
$x$, 'resolvido_aponta_geografia');


-- ═══ A RELEVÂNCIA, COM 0..N ══════════════════════════════════════════

select pg_temp.afirma('R1 · um lugar do fato no país do caso basta',
  (select r.relevancia from public.conteudo_crop_issue cc
     join public.conteudo ct on ct.id=cc.conteudo_id
     join public.crop_issue ci on ci.id=cc.crop_issue_id
     join public.crop c on c.id=ci.crop_id and c.codigo='ENSAIO_CROP_A'
     join public.issue i on i.id=ci.issue_id and i.codigo='ENSAIO_ISSUE_A',
     lateral public.f_relevancia_ao_caso(cc.id,'ENSAIO_CROP_A','ENSAIO_ISSUE_A','IT') r
    where ct.content_id='ENSAIO-F') = 'EXACT_SIGNAL',
  'exigir que TODOS fossem descartaria o documento que relata dois países');

select pg_temp.afirma('R2 · sem nenhum lugar do fato, é contexto',
  (select r.relevancia from public.conteudo_crop_issue cc
     join public.conteudo ct on ct.id=cc.conteudo_id
     join public.crop_issue ci on ci.id=cc.crop_issue_id
     join public.crop c on c.id=ci.crop_id and c.codigo='ENSAIO_CROP_A'
     join public.issue i on i.id=ci.issue_id and i.codigo='ENSAIO_ISSUE_A',
     lateral public.f_relevancia_ao_caso(cc.id,'ENSAIO_CROP_A','ENSAIO_ISSUE_A','IT') r
    where ct.content_id='ENSAIO-H') = 'CONTEXT_ONLY',
  'a lista de atuação não sustenta sinal do caso');


-- ═══════════════════════════════════════════════════════════════════════
\echo ''
\echo '── O LUGAR DO FATO ───────────────────────────────────────────────'
select case when ok then 'PASS' else 'FAIL' end as r, nome, detalhe
  from _lf order by ordem;
select 'TOTAL=' || count(*) || '  PASS=' || count(*) filter (where ok)
     || '  FAIL=' || count(*) filter (where not ok) as placar from _lf;
do $$
declare n integer;
begin
  select count(*) into n from _lf where not ok;
  if n > 0 then raise exception 'REGRESSOES_LUGAR_DO_FATO_FALHARAM=%', n; end if;
  raise notice 'REGRESSOES_LUGAR_DO_FATO=PASS';
end $$;
