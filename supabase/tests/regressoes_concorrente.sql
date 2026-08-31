-- ═══════════════════════════════════════════════════════════════════════
-- COMPETITOR_FORESIGHT_IMPORT_V1 — regressões e red team
--
-- Exige 001–020 e o import COMPETITOR-FORESIGHT-2026-08-30.sql.
--
-- O que estas regressões protegem NÃO é o número de linhas: é a disciplina
-- que separa o que foi observado do que foi inferido. Um piloto de
-- concorrência sem estas travas produz, em ordem de gravidade crescente:
--   1. um lead time inventado sobre identidade não provada;
--   2. um zero de camada lido como "o concorrente não anuncia";
--   3. a frase "o concorrente vai lançar o produto X".
-- ═══════════════════════════════════════════════════════════════════════
\set ON_ERROR_STOP on

create temp table _rc (ordem serial, nome text, ok boolean, detalhe text);
create or replace function pg_temp.afirma(n text, cond boolean, det text default '')
returns void language plpgsql as $f$
begin insert into _rc (nome, ok, detalhe) values (n, coalesce(cond,false), det); end $f$;

create or replace function pg_temp.recusa_por(n text, comando text, trava text)
returns void language plpgsql as $f$
declare msg text;
begin
  begin
    execute comando;
    raise exception 'ACEITOU_O_QUE_DEVERIA_RECUSAR';
  exception when others then msg := sqlerrm;
  end;
  if msg = 'ACEITOU_O_QUE_DEVERIA_RECUSAR' then
    insert into _rc (nome, ok, detalhe) values (n, false, 'o banco ACEITOU o que a lei proíbe');
  elsif position(trava in msg) > 0 then
    insert into _rc (nome, ok, detalhe) values (n, true, 'recusado por ' || trava);
  else
    insert into _rc (nome, ok, detalhe) values (n, false,
      'recusado pelo motivo ERRADO — esperava ' || trava || ', veio: ' || left(msg,80));
  end if;
end $f$;


-- ═══ D · O DENOMINADOR, MEDIDO ═══════════════════════════════════════
select pg_temp.afirma('D1 · seis concorrentes, escolhidos pelo registro',
  (select count(*) from public.organizacao
    where nome_canonico in ('BAYER','SYNGENTA','BASF','CORTEVA','NUFARM','UPL')) = 6,
  'a amostra saiu da contagem de titulares vigentes do ROPF, não da lista da missão');

select pg_temp.afirma('D2 · 19.702 eventos importados, nos TRÊS países',
  (select count(*) from public.evento_concorrente) = 19702,
  '9.661 marcas menos 1.633 sem classe agro declarada, mais 11.675 fatos '
  'datados de ES + IT + FR, menos 1 sem data do fato');

select pg_temp.afirma('D2b · os três países estão na base, e a marca da UE também',
  (select count(distinct pais) from public.evento_concorrente) = 4
  and (select count(*) from public.evento_concorrente where pais='IT') > 0
  and (select count(*) from public.evento_concorrente where pais='FR') > 0,
  'ES, IT, FR e EU (a marca da União Europeia). Uma base que dissesse EAME '
  'guardando só Espanha contradiria a própria medição de paridade');

select pg_temp.afirma('D3 · 1.635 links PROVED e 61 recusados, de 2.259 pares',
  (select count(*) from public.evento_concorrente_link where estado='PROVED') = 1635
  and (select count(*) from public.evento_concorrente_link where estado<>'PROVED') = 61,
  'o crosswalk EAME tem 2.259 pares nos três países; 563 não viram link porque '
  'um dos dois eventos foi recusado, e a perda está DECLARADA no cabeçalho do '
  'import em vez de o SQL a engolir em silêncio');

select pg_temp.afirma('D4 · todo evento carrega dono, país, fonte e evidência',
  not exists (select 1 from public.evento_concorrente
               where competidor_id is null or pais is null or fonte is null
                  or evidencia is null or observed_at is null),
  'campo do mínimo vazio é campo que sumiu, e some sem ninguém notar');


-- ═══ T · AS DUAS DATAS NÃO SE MISTURAM ═══════════════════════════════
select pg_temp.afirma('T1 · observed_at é o mesmo dia para todas as linhas',
  (select count(distinct observed_at) from public.evento_concorrente) = 1,
  'foi uma captura só. Espalhar observed_at simularia vigilância contínua');

select pg_temp.afirma('T2 · existe effective_date no FUTURO, e isso é legítimo',
  exists (select 1 from public.evento_concorrente
           where effective_date > current_date and event_type in
                 ('EXPIRY','SELLING_OFF_DEADLINE')),
  'caducidade e limite de venda são datas futuras declaradas HOJE pela fonte. '
  'Um banco que proibisse futuro em effective_date perderia o fato');

select pg_temp.afirma('T3 · effective_date nunca foi preenchido com a observação',
  not exists (select 1 from public.evento_concorrente
               where camada = 'REGULATORY' and effective_date = observed_at),
  'a tentação é preencher a data do fato com a data em que olhamos');


-- ═══ A · A ANTECEDÊNCIA NÃO PODE SER INVENTADA ═══════════════════════
select pg_temp.afirma('A1 · nenhum lead_days sobre link não provado',
  not exists (select 1 from public.evento_concorrente_link
               where lead_days is not null and estado <> 'PROVED'),
  'a missão manda medir antecedência só quando a relação for defensável');

select pg_temp.afirma('A2 · 1.053 defensáveis de 1.635 medidos',
  (select count(*) from public.evento_concorrente_link
    where lead_days_defensavel) = 1053,
  '582 pares ficam de fora: 557 têm o registro ANTES da marca — refutação — e '
  'os demais usam depósito que não é o mais antigo da marca (redepósito)');

select pg_temp.afirma('A2b · precedência histórica NÃO é antecendência operacional',
  (select count(*) from public.evento_concorrente_link
    where lead_days_defensavel and lead_days > 365) > 0,
  'a mediana defensável passa de mil dias. Um sinal que chega anos antes pode '
  'estar cedo DEMAIS para decisão: OPERATIONAL_EARLY_WARNING_VALUE = NOT_PROVED');

select pg_temp.afirma('A3 · a refutação está gravada, não descartada',
  (select count(*) from public.evento_concorrente_link
    where estado='PROVED' and lead_days < 0) = 557,
  'os 557 pares em que o registro precede a marca REFUTAM a hipótese do piloto '
  'e continuam na base — apagá-los produziria 100% de confirmação');

select pg_temp.afirma('A4 · nenhum defensável tem lead negativo ou zero',
  not exists (select 1 from public.evento_concorrente_link
               where lead_days_defensavel and coalesce(lead_days,0) <= 0),
  'chamar de defensável um par que refuta a hipótese seria publicar a '
  'refutação como confirmação');


-- ═══ C · AS CAMADAS VAZIAS PRECISAM APARECER ═════════════════════════
select pg_temp.afirma('C1 · três camadas estão em zero',
  (select count(*) from public.evento_concorrente
    where camada in ('PRODUCT_CATALOG','META','CREATOR')) = 0,
  'catálogo, Meta e creator não existem no acervo desta rodada');

select pg_temp.afirma('C2 · a view de cobertura MOSTRA as três camadas vazias',
  (select count(*) from public.v_competidor_cobertura_camada
    where eventos = 0 and estado_da_camada like 'NOT_AVAILABLE%') = 18,
  '6 concorrentes × 3 camadas vazias. Camada que some da listagem é '
  'indistinguível de camada que nunca foi tentada');

select pg_temp.afirma('C3 · nenhuma cadeia fim-a-fim foi fechada',
  not exists (
    select 1 from public.evento_concorrente
     where camada in ('META','CREATOR','PRODUCT_CATALOG')),
  'a resposta é: nenhuma. 2 de 5 camadas em todas as 1.683 cadeias. E o zero '
  'aqui é NOT_JOINED_IN_THIS_MISSION — o Creator Map está congelado em branch '
  'própria e a missão Meta tem 1.111 anúncios; esta branch não os juntou');


-- ═══ I · O SINAL DE MARCA NÃO PODE SER SUPERESTIMADO ═════════════════
select pg_temp.afirma('I1 · a classe 5 sozinha fica marcada como AMBÍGUA',
  (select count(*) from public.evento_concorrente
    where camada='IP' and confidence_state='OBSERVED_AMBIGUOUS_CLASS') > 0,
  'a classe 5 de Nice cobre farmacêutico e veterinário junto com pesticida');

select pg_temp.afirma('I2 · a Bayer concentra a ambiguidade',
  (select count(*) from public.evento_concorrente e
     join public.organizacao o on o.id=e.competidor_id
    where e.confidence_state='OBSERVED_AMBIGUOUS_CLASS' and o.nome_canonico='BAYER')
  > (select count(*) from public.evento_concorrente e
       join public.organizacao o on o.id=e.competidor_id
      where e.confidence_state='OBSERVED_AMBIGUOUS_CLASS' and o.nome_canonico='UPL'),
  'a Bayer tem divisão farmacêutica; GINECANES e BEPANTHEN entraram por '
  'classe 5 e não são defensivo');

select pg_temp.afirma('I3 · nenhum evento de IP entrou sem marca',
  not exists (select 1 from public.evento_concorrente
               where camada='IP' and brand is null),
  'evento de marca sem a marca é evento sobre nada');


-- ═══ P · A PROPRIEDADE DO DADO ═══════════════════════════════════════
select pg_temp.afirma('P1 · esta tabela tem um dono só',
  (select count(distinct dataset_owner) from public.evento_concorrente) = 1
  and (select distinct dataset_owner from public.evento_concorrente)
      = 'COMPETITOR_FORESIGHT_EAME',
  'sem isto a tabela vira depósito comum e em seis meses ninguém sabe qual '
  'linha responde a quem');

select pg_temp.afirma('P2 · o registro espanhol NÃO foi duplicado aqui',
  not exists (select 1 from public.evento_concorrente where registro_id is not null),
  'os registros dos concorrentes não estão na fundação; apontar por texto '
  'espera o dono em vez de criar um segundo');

-- ═══ N · A CLASSE DE NICE NÃO É IDENTIDADE DE PRODUTO ════════════
select pg_temp.afirma('N1 · a mesma marca aparece com classes diferentes por país',
  exists (
    select 1 from public.evento_concorrente a
      join public.evento_concorrente b
        on upper(a.brand) = upper(b.brand) and a.competidor_id = b.competidor_id
     where a.camada='IP' and b.camada='IP' and a.pais <> b.pais
       and a.confidence_state <> b.confidence_state),
  'VERDALIS da Corteva: classe 1 na Itália e na França, classe 5 na Espanha. '
  'A classe é escolha de quem deposita, escritório por escritório — logo a '
  'classe de Nice NÃO pode ser identidade universal de produto');

select pg_temp.afirma('N2 · nenhum evento de IP foi promovido só pela classe 5',
  not exists (
    select 1 from public.evento_concorrente
     where camada='IP' and confidence_state='OBSERVED_STRONG_AGRO_SIGNAL'
       and evidencia like '%SO_CLASSE_5%'),
  'a classe 5 cobre farmacêutico e veterinário. Promover por ela sozinha foi o '
  'erro que carimbou GINECANES da Bayer como defensivo');

select pg_temp.afirma('P3 · a fundação ADAMA continua intocada',
  (select count(*) from public.registro_regulatorio where fonte='MAPA_ROPF') = 96,
  'esta missão acrescenta uma camada derivada; não mexe em fundação alheia');


-- ═══ R · RED TEAM — as travas precisam ter dentes ════════════════════
-- R1 e R2 usam dois eventos de EXPIRY: os links reais ligam MARCA a
-- LOCAL_REGISTRATION, então este par nunca existe. Sem isso, a mutação
-- poderia esbarrar na unicidade do link e ser "recusada pelo motivo errado".
select pg_temp.recusa_por('R1 · lead_days sobre link PARTIAL',
  $$insert into public.evento_concorrente_link
      (evento_a_id, evento_b_id, estado, evidencia, lead_days)
    select min(id), max(id), 'PARTIAL', 'mutação', 400
      from public.evento_concorrente where event_type = 'EXPIRY'$$,
  'lead_days_exige_identidade_provada');

select pg_temp.recusa_por('R2 · defensável com lead negativo',
  $$insert into public.evento_concorrente_link
      (evento_a_id, evento_b_id, estado, evidencia, lead_days, lead_days_defensavel)
    select max(id), min(id), 'PROVED', 'mutação', -30, true
      from public.evento_concorrente where event_type = 'EXPIRY'$$,
  'defensavel_exige_ordem_e_valor');

select pg_temp.recusa_por('R3 · observação datada no futuro',
  $$insert into public.evento_concorrente
      (event_key, competidor_id, pais, camada, event_type, observed_at,
       effective_date, fonte, evidencia, brand, confidence_state)
    select 'MUT-FUTURO', min(id), 'ES', 'IP', 'TRADEMARK_APPLICATION',
           current_date + 30, current_date, 'mutação', 'mutação', 'X', 'NOT_KNOWN'
      from public.organizacao$$,
  'observacao_nao_e_no_futuro');

select pg_temp.recusa_por('R4 · fato datado sem a data',
  $$insert into public.evento_concorrente
      (event_key, competidor_id, pais, camada, event_type, observed_at,
       fonte, evidencia, brand, confidence_state)
    select 'MUT-SEM-DATA', min(id), 'ES', 'IP', 'TRADEMARK_APPLICATION',
           current_date, 'mutação', 'mutação', 'X', 'NOT_KNOWN'
      from public.organizacao$$,
  'fato_datado_exige_a_data');

select pg_temp.recusa_por('R5 · evento de META sem apontar para o canal dono',
  $$insert into public.evento_concorrente
      (event_key, competidor_id, pais, camada, event_type, observed_at,
       fonte, evidencia, confidence_state)
    select 'MUT-META', min(id), 'ES', 'META', 'META_AD_OBSERVED',
           current_date, 'mutação', 'mutação', 'NOT_KNOWN'
      from public.organizacao$$,
  'meta_e_creator_apontam_para_o_dono');

select pg_temp.recusa_por('R6 · outra missão despejando dado aqui',
  $$insert into public.evento_concorrente
      (event_key, competidor_id, pais, camada, event_type, observed_at,
       fonte, evidencia, brand, confidence_state, dataset_owner)
    select 'MUT-DONO', min(id), 'ES', 'IP', 'NEW_BRAND_OBSERVED',
           current_date, 'mutação', 'mutação', 'X', 'NOT_KNOWN', 'OUTRA_MISSAO'
      from public.organizacao$$,
  'evento_tem_um_dono_so');

select pg_temp.recusa_por('R7 · evento regulatório sem registro',
  $$insert into public.evento_concorrente
      (event_key, competidor_id, pais, camada, event_type, observed_at,
       effective_date, fonte, evidencia, confidence_state)
    select 'MUT-REG', min(id), 'ES', 'REGULATORY', 'EXPIRY',
           current_date, current_date, 'mutação', 'mutação', 'NOT_KNOWN'
      from public.organizacao$$,
  'evento_regulatorio_aponta_para_registro');

select pg_temp.recusa_por('R8 · o mesmo evento entrando duas vezes',
  $$insert into public.evento_concorrente
      (event_key, competidor_id, pais, camada, event_type, observed_at,
       effective_date, fonte, evidencia, brand, confidence_state)
    select event_key, competidor_id, pais, camada, event_type, observed_at,
           effective_date, fonte, evidencia, brand, confidence_state
      from public.evento_concorrente limit 1$$,
  'evento_concorrente_event_key_key');


-- ═══════════════════════════════════════════════════════════════════════
\echo ''
\echo '── COMPETITOR_FORESIGHT_IMPORT_V1 ────────────────────────────────'
select case when ok then 'PASS' else 'FAIL' end as r, nome, detalhe from _rc order by ordem;
select 'TOTAL=' || count(*) || '  PASS=' || count(*) filter (where ok)
     || '  FAIL=' || count(*) filter (where not ok) as placar from _rc;
do $$
declare n integer;
begin
  select count(*) into n from _rc where not ok;
  if n > 0 then raise exception 'REGRESSOES_CONCORRENTE_FALHARAM=%', n; end if;
  raise notice 'REGRESSOES_CONCORRENTE=PASS';
end $$;
