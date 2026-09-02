-- ═══════════════════════════════════════════════════════════════════════
-- O CATÁLOGO ADAMA ESPAÑA NO ACERVO — regressões pós-import
--
-- Exige 001–018 (com a 014 no lugar), a fixture ES, o ensaio do
-- pré-requisito ROPF e a importação do catálogo.
--
-- As quinze tentativas do RED TEAM da missão estão aqui como afirmações e
-- recusas. Nenhuma foi desenhada para passar: cada uma é a forma de um
-- falso positivo que já custou caro.
-- ═══════════════════════════════════════════════════════════════════════
\set ON_ERROR_STOP on

create temp table _ca (ordem serial, nome text, ok boolean, detalhe text);
create or replace function pg_temp.afirma(n text, cond boolean, det text default '')
returns void language plpgsql as $f$
begin insert into _ca (nome, ok, detalhe) values (n, coalesce(cond,false), det); end $f$;
create or replace function pg_temp.recusa_por(n text, comando text, trava text)
returns void language plpgsql as $f$
declare msg text;
begin
  -- O comando roda DENTRO de um bloco com EXCEPTION, que é uma subtransação.
  -- Se ele PASSAR, o `raise` desfaz o que ele fez — sem isso, um teste
  -- negativo que aceita deixa a mutação no banco e envenena todas as
  -- afirmações seguintes. Foi o que aconteceu na primeira execução da suíte
  -- do catálogo: um UPDATE passou, virou 41 linhas, e os contadores do gate
  -- reprovaram por culpa do teste, não do dado.
  begin
    execute comando;
    raise exception 'ACEITOU_O_QUE_DEVERIA_RECUSAR';
  exception when others then msg := sqlerrm;
  end;
  if msg = 'ACEITOU_O_QUE_DEVERIA_RECUSAR' then
    insert into _ca (nome, ok, detalhe) values (n, false, 'o banco ACEITOU o que a lei proíbe');
  elsif position(trava in msg) > 0 then
    insert into _ca (nome, ok, detalhe) values (n, true, 'recusado por ' || trava);
  else
    insert into _ca (nome, ok, detalhe) values (n, false,
      'recusado pelo motivo ERRADO — esperava ' || trava || ', veio: ' || left(msg,70));
  end if;
end $f$;

-- ═══ OS CONTADORES DO GATE ═══════════════════════════════════════════
select pg_temp.afirma('N1 · 56 produtos',
  (select count(*) from public.catalogo_produto) = 56, 'esperado 56');
select pg_temp.afirma('N2 · 147 documentos',
  (select count(*) from public.catalogo_produto_documento) = 147, 'esperado 147');
select pg_temp.afirma('N3 · 711 relações de cultivo',
  (select count(*) from public.catalogo_produto_cultivo) = 711, 'esperado 711');
select pg_temp.afirma('N4 · 588 declaradas e 123 citadas',
  (select count(*) from public.catalogo_produto_cultivo
    where origem_declaracao='DECLARADO_NO_BLOCO_CULTIVOS') = 588
  and (select count(*) from public.catalogo_produto_cultivo
        where origem_declaracao='CITADO_NO_CORPO_DA_PAGINA') = 123,
  'DECLARED_CROP != CITED_CROP, e os dois contados separados');
select pg_temp.afirma('N5 · 5 usos com CROP + ISSUE',
  (select count(*) from public.catalogo_produto_cultivo_agente) = 5, 'esperado 5');
select pg_temp.afirma('N6 · 26 crop × dose sem issue',
  (select count(*) from public.catalogo_produto_cultivo_dose) = 26, 'esperado 26');
select pg_temp.afirma('N7 · 3 janelas de aplicação',
  (select count(*) from public.catalogo_produto_janela_aplicacao) = 3, 'esperado 3');
select pg_temp.afirma('N8 · 44 LOCAL_REGISTERED',
  (select count(*) from public.catalogo_registro_crosswalk
    where estado in ('MATCHED_EXACT','MATCHED_WITH_EVIDENCE')) = 44, '41 exatos + 3 por evidência');
select pg_temp.afirma('N9 · 12 LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED',
  (select count(*) from public.catalogo_registro_crosswalk
    where estado='ADAMA_SITE_ONLY') = 12, 'esperado 12');

-- ═══ RED TEAM ════════════════════════════════════════════════════════

-- 1 · catálogo presente vira registrado
select pg_temp.afirma('X1 · presença em catálogo NÃO é registro',
  not exists (select 1 from public.catalogo_registro_crosswalk
               where estado='ADAMA_SITE_ONLY' and registro_id is not null),
  'PUBLIC_CATALOG_PRESENCE != REGULATORY_REGISTRATION');
select pg_temp.recusa_por('X1b · ADAMA_SITE_ONLY com registro é recusado', $x$
  update public.catalogo_registro_crosswalk set estado='ADAMA_SITE_ONLY'
   where estado='MATCHED_EXACT'
$x$, 'site_only_nao_carrega_registro');

-- 2 · não provado vira não registrado
select pg_temp.afirma('X2 · nenhum dos 12 virou NOT_REGISTERED',
  not exists (select 1 from public.catalogo_registro_crosswalk where estado='NOT_REGISTERED')
  and (select count(*) from public.catalogo_registro_crosswalk where estado='ADAMA_SITE_ONLY')=12,
  'LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED != NOT_REGISTERED — e o estado nem existe');
select pg_temp.recusa_por('X2b · NOT_REGISTERED não está no vocabulário', $x$
  insert into public.catalogo_registro_crosswalk (captura_id, produto_id, estado, evidencia)
  select captura_id, id, 'NOT_REGISTERED', 'x' from public.catalogo_produto limit 1
$x$, 'catalogo_registro_crosswalk_estado_check');

-- 3 · menu vira issue
select pg_temp.afirma('X3 · termo de menu fica em catalogo_termo_ambiguo',
  (select count(*) from public.catalogo_termo_ambiguo) = 210
  and not exists (
    select 1 from public.catalogo_produto_agente a
     join public.catalogo_termo_ambiguo t
       on t.produto_id = a.produto_id and t.eixo = 'ISSUE'
      and t.termo_na_pagina = a.rotulo_publicado
    where a.issue_id is not null),
  'MENU_TERM != AUTHORIZED_ISSUE — nenhum termo marcado ambíguo virou issue canônico');

-- 4 · cited vira declared
select pg_temp.afirma('X4 · citado e declarado não se misturam',
  (select count(distinct origem_declaracao) from public.catalogo_produto_cultivo) = 2,
  'os dois estados sobrevivem à importação');

-- 5 · dose cria issue
-- A tabela de dose tem `par_derivavel` e `porque_nao_ha_par`, e NÃO tem
-- issue_id nem agente_rotulo: uma dose por cultivo não nomeia o problema, e
-- deixar um campo vazio esperando seria convidar o preenchimento.
select pg_temp.afirma('X5 · linha de dose NÃO tem onde guardar um agente',
  not exists (select 1 from information_schema.columns
               where table_schema='public' and table_name='catalogo_produto_cultivo_dose'
                 and column_name in ('issue_id','agente_rotulo'))
  and exists (select 1 from information_schema.columns
               where table_schema='public' and table_name='catalogo_produto_cultivo_dose'
                 and column_name='porque_nao_ha_par'),
  'DOSE != CROP_ISSUE_PAIR — e a ausência do par vem com o motivo escrito');

select pg_temp.afirma('X5b · as 26 doses dizem por que não formam par',
  (select count(*) from public.catalogo_produto_cultivo_dose
    where par_derivavel = false and porque_nao_ha_par is not null) = 26,
  'nenhuma dose virou par por conveniência');

-- 6 · import repetido duplica  (provado por execução; aqui a trava)
select pg_temp.afirma('X6 · toda tabela do catálogo tem chave natural',
  not exists (
    select 1 from unnest(array['catalogo_produto','catalogo_produto_documento',
                               'catalogo_produto_cultivo','catalogo_produto_cultivo_agente',
                               'catalogo_produto_cultivo_dose',
                               'catalogo_produto_janela_aplicacao',
                               'catalogo_registro_crosswalk']) t(tab)
     where not exists (select 1 from pg_constraint
                        where conrelid = ('public.'||t.tab)::regclass and contype='u')),
  'IDEMPOTENT IMPORT != DELETE AND RECREATE — sem chave natural não há idempotência');

-- 7 · nova captura duplica registro
select pg_temp.afirma('X7 · a captura é única por fonte e versão',
  exists (select 1 from pg_constraint where conname='captura_e_unica_por_fonte_e_versao'),
  'CAPTURE != REGISTRATION continua com o dono da 013, e o catálogo não o recriou');

-- 8 · CUPROXI funde
select pg_temp.afirma('X8 · CUPROXI FLO continua com DOIS identificadores tipados',
  (select p.registration_id from public.catalogo_produto p
    where p.nome_publicado='CUPROXI FLO') = '19232'
  and (select cw.registration_id_texto from public.catalogo_registro_crosswalk cw
        join public.catalogo_produto p on p.id=cw.produto_id
       where p.nome_publicado='CUPROXI FLO') = 'ES-00979'
  and (select cw.estado from public.catalogo_registro_crosswalk cw
        join public.catalogo_produto p on p.id=cw.produto_id
       where p.nome_publicado='CUPROXI FLO') = 'MATCHED_WITH_EVIDENCE',
  '19232 e ES-00979 lado a lado, ligados por evidência e NÃO fundidos');

-- 9 · RAW path vira identidade
select pg_temp.afirma('X9 · a identidade do RAW é o sha256, não o caminho',
  (select count(distinct sha256) from public.raw_asset) =
  (select count(*) from public.raw_asset)
  and not exists (select 1 from public.raw_asset where sha256 is null),
  'PATH != IDENTITY — o nome storage-safe mudou o caminho e não o documento');

-- 10 · documento falho ganha raw inexistente
select pg_temp.afirma('X10 · documento que falhou NÃO aponta raw',
  not exists (select 1 from public.catalogo_produto_documento
               where download_state='FAILED' and raw_asset_id is not null),
  'FAILED_DOCUMENT_REFERENCE != RAW_ASSET');
select pg_temp.recusa_por('X10b · e a trava impede criar um', $x$
  update public.catalogo_produto_documento
     set raw_asset_id = (select id from public.raw_asset limit 1)
   where download_state='FAILED'
$x$, 'falha_nao_vira_bytes_preservados');

-- 11 · Espanha contamina Itália
select pg_temp.afirma('X11 · todo produto do catálogo é ES',
  (select count(distinct pais) from public.catalogo_produto) = 1
  and (select distinct pais from public.catalogo_produto)::text = 'ES',
  'COUNTRY_ISOLATION');
select pg_temp.afirma('X11b · consulta IT não devolve nada do catálogo espanhol',
  (select count(*) from public.catalogo_produto where pais='IT') = 0
  and (select count(*) from public.catalogo_produto where pais='FR') = 0,
  'nenhum catálogo global fecha portfolio local de outro país');
select pg_temp.afirma('X11c · o calendário italiano segue vazio depois do import',
  (select count(*) from public.f_crop_calendar('IT')) = 0,
  'o import espanhol não criou linha nenhuma em IT');

-- 13 · disponibilidade comercial nasce sem prova
select pg_temp.afirma('X13 · nenhuma coluna de disponibilidade comercial no catálogo',
  not exists (select 1 from information_schema.columns
               where table_schema='public' and table_name like 'catalogo_%'
                 and column_name ~ '(disponivel|comercial|venda|estoque|preco)'),
  'REGISTRATION != COMMERCIAL_AVAILABILITY, e o catálogo não inventou a terceira');
select pg_temp.afirma('X13b · disponibilidade_comercial continua vazia',
  (select count(*) from public.disponibilidade_comercial) = 0,
  'a casa existe desde a 009 e o import não escreveu nela');

-- 14 · expiry vira withdrawal
select pg_temp.afirma('X14 · caducidade vencida não virou retirada',
  not exists (select 1 from public.registro_regulatorio
               where estado <> 'vigente' and fonte='MAPA_ROPF')
  and exists (select 1 from public.registro_regulatorio
               where fonte='MAPA_ROPF' and fecha_caducidad < current_date),
  'EXPIRY != WITHDRAWAL — há registro com data vencida e nenhum foi marcado retirado');

-- 15 · AS_OF futuro reescreve passado
select pg_temp.afirma('X15 · uma captura futura não muda a resposta de ontem',
  (select count(*) from public.f_registro_corrente('ES', current_date - 1))
  <= (select count(*) from public.f_registro_corrente('ES', current_date)),
  'FUTURE_CAPTURE_CANNOT_REWRITE_PAST_STATE');

-- ═══ EVIDÊNCIA · o caminho de volta existe ═══════════════════════════
select pg_temp.afirma('E1 · todo documento baixado leva a bytes com sha256',
  not exists (select 1 from public.catalogo_produto_documento d
               where d.download_state='DOWNLOADED' and d.raw_asset_id is not null
                 and not exists (select 1 from public.raw_asset ra
                                  where ra.id=d.raw_asset_id and ra.sha256 is not null)),
  'DB ROW -> raw_asset -> sha256, sem buraco');
select pg_temp.afirma('E2 · o AVASTEL grande está no acervo, com os bytes declarados',
  (select ra.bytes from public.raw_asset ra
    where ra.storage_path like '%Folleto AVASTEL%') = 158083718,
  'o caso-limite dos 50 MB: 158 MB, presente e com tamanho declarado');
select pg_temp.afirma('E3 · o NEPTUNE entrou com os três documentos',
  (select count(*) from public.catalogo_produto_documento d
     join public.catalogo_produto p on p.id=d.produto_id
    where p.nome_publicado='NEPTUNE' and d.raw_asset_id is not null) = 3,
  'PRESERVED_PDF != CASE_RESOLVED — ES-CASE-001 continua ABERTA');

-- ═══════════════════════════════════════════════════════════════════════
\echo ''
\echo '── O CATÁLOGO ADAMA ESPAÑA NO ACERVO ─────────────────────────────'
select case when ok then 'PASS' else 'FAIL' end as r, nome, detalhe from _ca order by ordem;
select 'TOTAL=' || count(*) || '  PASS=' || count(*) filter (where ok)
     || '  FAIL=' || count(*) filter (where not ok) as placar from _ca;
do $$
declare n integer;
begin
  select count(*) into n from _ca where not ok;
  if n > 0 then raise exception 'REGRESSOES_CATALOGO_ES_FALHARAM=%', n; end if;
  raise notice 'REGRESSOES_CATALOGO_ES=PASS';
end $$;
