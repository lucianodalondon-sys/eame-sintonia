-- ═══════════════════════════════════════════════════════════════════════
-- FIXTURE — MVP TEMPORAL DA ESPANHA
--
-- Só entra o que uma fonte já sustenta e que já está num artefato canônico
-- do repositório. Onde um relógio não existe, NÃO há linha — e a consulta
-- devolve NO_DATA. Essa ausência é o comportamento correto, não um buraco.
--
-- O que deliberadamente NÃO está aqui:
--   · janela agronômica do repilo no outono — a frase existe nos cartões
--     mas sem fonte citada. Seria calendário inventado.
--   · qualquer data de 2027 — o caso do milho diz NEXT_CYCLE e é só isso
--     que a fonte sustenta.
--   · pressão de campo dentro de issue_window — pressão mora em observacao.
-- ═══════════════════════════════════════════════════════════════════════

begin;

insert into public.collection_run (run_id, platform, source_country, started_at, status, rule_version)
values ('fixture-es-calendario-v1','FIXTURE','ES','2026-08-30T00:00:00Z','concluida','v1')
on conflict (run_id) do nothing;

-- ── Geografia ─────────────────────────────────────────────────────────
insert into public.geografia (pais, regiao, provincia, codigo_nuts) values
  ('ES','Andalucía',null,'ES61'),
  ('ES','Andalucía','Huelva','ES615'),
  ('ES','Andalucía','Cádiz','ES612'),
  ('ES','Aragón','Huesca','ES241'),
  ('ES','Castilla y León',null,'ES41')
on conflict do nothing;

-- ── Vocabulário ───────────────────────────────────────────────────────
insert into public.crop (codigo, eppo_code) values
  ('OLIVE','OLVEU'), ('MAIZE','ZEAMX'), ('WHEAT','TRZAX')
on conflict (codigo) do nothing;

insert into public.issue (codigo, classe) values
  ('REPILO','DISEASE'), ('AMARANTHUS_PALMERI','WEED'), ('LOLIUM_RIGIDUM','WEED')
on conflict (codigo) do nothing;

insert into public.crop_local (crop_id, pais, source_system, external_id, nome_local)
select id,'ES','MAPA_ROPF', v.ext, v.nome from public.crop c
  join (values ('OLIVE','1972','OLIVO'),('MAIZE','2024','MAÍZ'),('WHEAT','2034','TRIGO')) as v(cod,ext,nome)
    on v.cod = c.codigo
on conflict do nothing;

insert into public.issue_local (issue_id, pais, source_system, external_id, nome_local)
select id,'ES','MAPA_ROPF', v.ext, v.nome from public.issue i
  join (values ('REPILO','6200','REPILO DEL OLIVO, VENTURIA OLEAGINEA'),
               ('AMARANTHUS_PALMERI','2067','BLEDOS, AMARANTHUS SPP.'),
               ('LOLIUM_RIGIDUM','2062','VALLICO, LOLIUM RIGIDUM')) as v(cod,ext,nome)
    on v.cod = i.codigo
on conflict do nothing;

insert into public.crop_issue (crop_id, issue_id)
select c.id, i.id from public.crop c join public.issue i on true
 where (c.codigo,i.codigo) in (('OLIVE','REPILO'),('MAIZE','AMARANTHUS_PALMERI'),('WHEAT','LOLIUM_RIGIDUM'))
on conflict do nothing;

-- ═══ RELÓGIO A · CROP CALENDAR ═══════════════════════════════════════
-- Olivar: fenologia OBSERVADA. Campanha observada não se repete.
insert into public.crop_calendar
 (pais, crop_id, geografia_id, campanha, tipo, fase, resolucao,
  data_inicio, data_fim, bbch_inicio, bbch_fim, texto_original, recorrente,
  fonte, fonte_versao, fonte_url, nivel_evidencia, capturado_em, rule_version)
select 'ES', c.id, g.id, '2026', 'OBSERVED_CAMPAIGN', 'MATURATION', 'PHENOLOGY_STAGE',
       '2026-08-01','2026-08-19', 75, 81,
       '1.726 registros em "H endurecimiento hueso" (~BBCH 75-79) e 57 em "I1 envero" (~BBCH 81) nos muestreos de agosto/2026',
       false, 'RAIF Andalucía — 2026_RAIF_Olivar_Muestreos.xml',
       'gerado 2026-08-24, publicado 2026-08-26',
       'https://www.juntadeandalucia.es/datosabiertos/portal/dataset/raif',
       'MEASURED_SERIES','2026-08-30T00:00:00Z','v1'
  from public.crop c, public.geografia g
 where c.codigo='OLIVE' and g.pais='ES' and g.regiao='Andalucía' and g.provincia is null;

-- Milho em Huesca: calendário TÍPICO, e o cartão diz que é típico.
-- Por ser típico, pode recorrer — e é só isso que autoriza falar de 2027.
insert into public.crop_calendar
 (pais, crop_id, geografia_id, campanha, tipo, fase, resolucao,
  texto_original, recorrente, fonte, nivel_evidencia, capturado_em, rule_version)
select 'ES', c.id, g.id, null, 'TYPICAL_CALENDAR', 'SOWING', 'APPROXIMATE',
       'em Aragón o milho é semeado a partir de abril',
       true, 'MAPA — descrição textual, não tabela lida',
       'OFFICIAL_SOURCE','2026-08-30T00:00:00Z','v1'
  from public.crop c, public.geografia g
 where c.codigo='MAIZE' and g.provincia='Huesca';

-- Cereal de inverno: sementeira outubro/novembro, típico.
insert into public.crop_calendar
 (pais, crop_id, geografia_id, campanha, tipo, fase, resolucao,
  mes_inicio, mes_fim, texto_original, recorrente,
  fonte, nivel_evidencia, capturado_em, rule_version)
select 'ES', c.id, g.id, null, 'TYPICAL_CALENDAR', 'SOWING', 'MONTH',
       10, 11, 'sementeira do cereal de inverno em outubro/novembro',
       true, 'ES-CASE-003 — calendário declarado TYPICAL, sem tabela lida',
       'OFFICIAL_SOURCE','2026-08-30T00:00:00Z','v1'
  from public.crop c, public.geografia g
 where c.codigo='WHEAT' and g.regiao='Castilla y León' and g.provincia is null;

-- ═══ RELÓGIO B · ISSUE WINDOW ════════════════════════════════════════
-- Milho × palmeri: atividade OBSERVADA, com as datas dos três avisos.
-- Não recorre: é o que foi visto, não o que costuma acontecer.
insert into public.issue_window
 (pais, crop_issue_id, geografia_id, campanha, tipo, resolucao,
  data_inicio, data_fim, texto_original, recorrente,
  fonte, fonte_url, nivel_evidencia, capturado_em, rule_version)
select 'ES', ci.id, g.id, '2026', 'OBSERVED_ACTIVITY', 'DATE_EXACT',
       '2025-10-22','2026-07-15',
       'três avisos oficiais sobre Amaranthus palmeri: 22/10/2025 (aviso 17), 08/06/2026 (aviso 8) e 15/07/2026 (aviso 9)',
       false, 'Gobierno de Aragón — Boletín Fitosanitario de Avisos e Informaciones',
       'https://www.aragon.es/-/boletin-fitosanitario-de-avisos-e-informaciones',
       'OFFICIAL_SOURCE','2026-08-30T00:00:00Z','v1'
  from public.crop_issue ci
  join public.crop c on c.id=ci.crop_id join public.issue i on i.id=ci.issue_id,
       public.geografia g
 where c.codigo='MAIZE' and i.codigo='AMARANTHUS_PALMERI' and g.provincia='Huesca';

-- NÃO há linha de issue_window para OLIVE × REPILO nem para WHEAT × LOLIUM.
-- Para o repilo, a frase "o controle se concentra no outono" não tem fonte
-- citada nos cartões. Para o vallico, nenhuma fonte de campo consultada mede
-- daninha. As duas consultas devolvem NO_DATA, e é a resposta certa.

-- ═══ RELÓGIO C · PRODUCT REGISTERED WINDOW ═══════════════════════════
insert into public.registro_regulatorio
 (pais, registration_id, nome_comercial, titular, formulado, estado,
  fecha_caducidad, fonte, fonte_versao, capturado_em)
values
 ('ES','ES-00979','CUPROXI FLO','ADAMA Agriculture España S.A.',
  'OXICLORURO DE COBRE 52% (EXPR. EN CU) [SC] P/V','Vigente','2029-06-30',
  'MAPA ROPF','2026-08-30T05:01:51+02:00','2026-08-30T00:00:00Z'),
 ('ES','ES-00211','NEPTUNE','ADAMA Agriculture España S.A.',
  'TEBUCONAZOL 3,6% + OXICLORURO DE COBRE (exp. como cobre) 36% [SC] P/V','Vigente','2026-08-15',
  'MAPA ROPF','2026-08-30T05:01:51+02:00','2026-08-30T00:00:00Z'),
 ('ES','ES-01677','DIODE 100','ADAMA Agriculture España S.A.',
  'MESOTRIONA 10% [SC] P/V','Vigente',null,
  'MAPA ROPF','2026-08-30T05:01:51+02:00','2026-08-30T00:00:00Z'),
 ('ES','19549','ACCRESTO','ADAMA Agriculture España S.A.',
  'CLODINAFOP-PROPARGIL 24% [EC] P/V','Vigente','2027-07-31',
  'MAPA ROPF','2026-08-30T05:01:51+02:00','2026-08-30T00:00:00Z')
on conflict do nothing;

insert into public.registro_uso (registro_id, crop_id, issue_id, substancia)
select r.id, c.id, i.id, v.subst
  from (values ('ES-00979','OLIVE','REPILO','OXICLORURO DE COBRE'),
               ('ES-00211','OLIVE','REPILO','TEBUCONAZOL + OXICLORURO DE COBRE'),
               ('ES-01677','MAIZE',null,'MESOTRIONA'),
               ('19549','WHEAT','LOLIUM_RIGIDUM','CLODINAFOP-PROPARGIL')) as v(reg,cropc,issuec,subst)
  join public.registro_regulatorio r on r.registration_id=v.reg and r.pais='ES'
  join public.crop c on c.codigo=v.cropc
  left join public.issue i on i.codigo=v.issuec;

insert into public.registro_uso_janela
 (registro_uso_id, resolucao, bbch_inicio, bbch_fim,
  aplicacoes_min, aplicacoes_max, prazo_seguranca_dias,
  dose_min, dose_max, dose_unidade, timing_texto_original, timing_normalizado,
  nivel_evidencia, fonte, fonte_versao, capturado_em, rule_version)
select ru.id, v.res::resolucao_temporal, v.b0, v.b1, v.a0, v.a1, v.phi,
       v.d0, v.d1, v.du, v.txt, v.norm,
       'REGULATORY_FACT','ficha oficial do MAPA (PDF preservado)','ROPF 2026-08-30',
       '2026-08-30T00:00:00Z','v1'
  from (values
    ('ES-00979','PHENOLOGY_STAGE',10::smallint,85::smallint,1::smallint,4::smallint,7::smallint,
     0.15,0.30,'% p/v','BBCH 10-85','aplicação autorizada de BBCH 10 a 85'),
    -- NEPTUNE: a etiqueta fala de fenologia em palavras, não em BBCH.
    -- Guardar APPROXIMATE preserva a imprecisão da fonte.
    ('ES-00211','APPROXIMATE',null,null,null,2::smallint,120::smallint,
     0.15,0.25,'% p/v','Se dará la primera aplicación antes de la floración',null),
    ('ES-01677','PHENOLOGY_STAGE',0::smallint,19::smallint,1::smallint,2::smallint,7::smallint,
     0.75,1.5,'l/ha','BBCH 00-19','aplicação autorizada de BBCH 00 a 19'),
    ('19549','APPROXIMATE',null,null,null,null,null,
     0.225,0.300,'l/ha',
     'Aplicar en postemergencia del cultivo, desde el estado de 3 hojas hasta el final del ahijamiento de las malas hierbas',
     null)
  ) as v(reg,res,b0,b1,a0,a1,phi,d0,d1,du,txt,norm)
  join public.registro_regulatorio r on r.registration_id=v.reg and r.pais='ES'
  join public.registro_uso ru on ru.registro_id=r.id;

-- ═══ RELÓGIO D · OBSERVAÇÃO DE CAMPO ═════════════════════════════════
-- Magnitude e denominador na mesma linha, como o esquema já exigia.
insert into public.observacao
 (crop_issue_id, geografia_id, camada, periodo_inicio, periodo_fim,
  valor, unidade, base_denominador, base_descricao, run_id, rule_version, medido_em)
select ci.id, g.id, 'FIELD', v.ini::date, v.fim::date, v.val, '% de folhas',
       v.den, v.desc_, 'fixture-es-calendario-v1','v1','2026-08-30T00:00:00Z'
  from (values ('Huelva','2026-03-03','2026-06-14',8.83,18,'18 leituras de repilo visível em 7 parcelas — o menor n das 21 campanhas'),
               ('Cádiz', '2026-02-10','2026-05-27',8.01,141,'141 leituras de repilo visível em 39 parcelas — rede estável nas 21 campanhas'))
       as v(prov,ini,fim,val,den,desc_)
  join public.geografia g on g.provincia=v.prov and g.pais='ES'
  join public.crop_issue ci on true
  join public.crop c on c.id=ci.crop_id and c.codigo='OLIVE'
  join public.issue i on i.id=ci.issue_id and i.codigo='REPILO';

-- ═══ RÉGUA DE FRESCOR ════════════════════════════════════════════════
-- Limiares são DADO, com justificativa. Não há constante universal em código.
insert into public.freshness_regra (proposito, estado, idade_max_dias, rule_version, justificativa) values
 ('FIELD_DECISION','CURRENT',14,'v1',
  'duas semanas é o intervalo típico entre boletins fitossanitários regionais; além disso a leitura deixa de descrever a semana corrente'),
 ('FIELD_DECISION','RECENT',45,'v1',
  'até cerca de um mês e meio a leitura ainda descreve a mesma fase da campanha'),
 ('FIELD_DECISION','SEASONAL',180,'v1',
  'dentro da mesma campanha agrícola, mas já não descreve o estado corrente do campo'),
 ('SCIENCE_CONTEXT','CURRENT',1825,'v1',
  'cinco anos: um levantamento de resistência publicado segue sendo contexto científico válido muito depois de perder valor como leitura de campo')
on conflict do nothing;

commit;
