-- ═══════════════════════════════════════════════════════════════════════
-- ENSAIO — NÃO É IMPORTAÇÃO.
--
-- Cinco casos tirados do handoff `claude/adama-es-local-browser` @ 0a799f5,
-- carregados num banco DESCARTÁVEL para responder uma pergunta só:
--
--     o motor dos quatro relógios consegue representar o que a ADAMA
--     España entrega, sem perder nada e sem inferir nada?
--
-- Nada aqui entra no banco canônico. Nenhuma linha é dado de produção.
-- Rodar assim, e só assim:
--
--   createdb eame_ensaio
--   psql eame_ensaio -f supabase/migrations/00{1..7}_*.sql   (e 009–012, depois 008)
--   psql eame_ensaio -f supabase/ensaios/ADAMA-ES-ENSAIO-CINCO-CASOS.sql
--
-- Os cinco casos:
--   A · produto com cultura + alvo + janela explícita   POSTSCRIPT 80 · arroz
--   B · produto de nível cultura, sem alvo              ORDAGO CAPS · almendro
--   C · produto com validade vencida                    NEPTUNE · olivo
--   D · temporalidade APROXIMADA                        TRINITY · cevada
--   E · dado ausente que precisa continuar NOT_KNOWN    TRINITY · centeio
-- ═══════════════════════════════════════════════════════════════════════

begin;

-- ── vocabulário, com o id do MAPA como identificador local ────────────
-- ARROZ é cultivo 2040 e MALAS HIERBAS é plaga 2040. O mesmo número em dois
-- vocabulários diferentes. Por isso os ids locais moram em crop_local e
-- issue_local, e não numa coluna só.
insert into public.crop (codigo, eppo_code) values
 ('RICE',null),('ALMOND',null),('OLIVE',null),('BARLEY',null),('RYE',null)
on conflict (codigo) do nothing;

insert into public.issue (codigo, classe) values
 ('BROADLEAF_WEEDS','WEED'),('WEEDS_GENERIC','WEED'),('REPILO','DISEASE')
on conflict (codigo) do nothing;

insert into public.crop_local (crop_id, pais, source_system, external_id, nome_local)
select c.id,'ES','MAPA_ROPF',v.eid,v.nome from (values
 ('RICE','2040','ARROZ'),('ALMOND','2006','ALMENDRO'),('OLIVE','1972','OLIVO'),
 ('BARLEY','2035','CEBADA'),('RYE','2037','CENTENO')) as v(cod,eid,nome)
 join public.crop c on c.codigo=v.cod
on conflict do nothing;

insert into public.issue_local (issue_id, pais, source_system, external_id, nome_local)
select i.id,'ES','MAPA_ROPF',v.eid,v.nome from (values
 ('BROADLEAF_WEEDS','2023','Dicotiledóneas, malas hierbas de hoja ancha'),
 ('WEEDS_GENERIC','2040','MALAS HIERBAS'),
 ('REPILO','2016','Repilo del olivo, Venturia oleaginea')) as v(cod,eid,nome)
 join public.issue i on i.codigo=v.cod
on conflict do nothing;

insert into public.crop_issue (crop_id, issue_id)
select c.id,i.id from (values ('RICE','BROADLEAF_WEEDS'),('BARLEY','WEEDS_GENERIC'),
 ('RYE','WEEDS_GENERIC'),('OLIVE','REPILO')) as v(c,i)
 join public.crop c on c.codigo=v.c join public.issue i on i.codigo=v.i
on conflict do nothing;

-- ── os registros ──────────────────────────────────────────────────────
-- titular e fecha_caducidad vêm do ROPF (ES-ADAMA-PORTFOLIO-ROPF, export de
-- titular ADAMA), NUNCA do site do fabricante. O site não prova registro.
-- ORDAGO CAPS e POSTSCRIPT 80 não têm caducidad no export: fica NULL, que é
-- ausência de informação e não prazo indeterminado.
insert into public.registro_regulatorio
 (pais, registration_id, nome_comercial, titular, formulado, estado,
  fecha_caducidad, fonte, fonte_versao, capturado_em) values
 ('ES','ES-01516','POSTSCRIPT 80','ADAMA Agriculture España S.A.',
  'IMAZAMOX 8% [SL] P/V','Vigente',null,
  'MAPA ROPF','2026-08-30T01:01:43+02:00','2026-08-30T00:00:00Z'),
 ('ES','ES-00499','ORDAGO CAPS','ADAMA Agriculture España S.A.',
  'PENDIMETALINA 40% [CS] P/V','Vigente',null,
  'MAPA ROPF','2026-08-30T01:01:43+02:00','2026-08-30T00:00:00Z'),
 ('ES','ES-00211','NEPTUNE','ADAMA Agriculture España S.A.',
  'TEBUCONAZOL 3,6% + OXICLORURO DE COBRE (exp. como cobre) 36% [SC] P/V','Vigente',
  '2026-08-15','MAPA ROPF','2026-08-30T01:01:43+02:00','2026-08-30T00:00:00Z'),
 ('ES','25667','TRINITY','ADAMA Agriculture España S.A.',
  'DIFLUFENICAN 4% + CLORTOLURON 25% + PENDIMETALINA 30% [SC] P/V','Vigente',null,
  'MAPA ROPF','2026-08-30T01:01:43+02:00','2026-08-30T00:00:00Z')
on conflict do nothing;

-- ── os usos ───────────────────────────────────────────────────────────
-- ORDAGO CAPS entra com issue_id NULL de propósito: a fonte declara cultivo
-- e dose, e NÃO nomeia agente. Inventar um alvo aqui seria cartesiano.
insert into public.registro_uso (registro_id, crop_id, issue_id, substancia)
select r.id, c.id, i.id, v.subst from (values
 ('ES-01516','RICE','BROADLEAF_WEEDS','IMAZAMOX'),
 ('ES-00499','ALMOND',null,'PENDIMETALINA'),
 ('ES-00211','OLIVE','REPILO','TEBUCONAZOL + OXICLORURO DE COBRE'),
 ('25667','BARLEY','WEEDS_GENERIC','DIFLUFENICAN + CLORTOLURON + PENDIMETALINA'),
 ('25667','RYE','WEEDS_GENERIC','DIFLUFENICAN + CLORTOLURON + PENDIMETALINA')
 ) as v(reg,crop,issue,subst)
 join public.registro_regulatorio r on r.registration_id=v.reg and r.pais='ES'
 join public.crop c on c.codigo=v.crop
 left join public.issue i on i.codigo=v.issue
on conflict do nothing;

-- ── as janelas · relógio C ────────────────────────────────────────────

-- A · POSTSCRIPT 80 — a única com BBCH numérico que a fonte realmente diz.
--     "Aplicar durante BBCH 12-29", lido da linha da tabela, com âncora.
insert into public.registro_uso_janela
 (registro_uso_id, resolucao, bbch_inicio, bbch_fim, aplicacoes_max, dose_max, dose_unidade,
  timing_texto_original, nivel_evidencia, fonte, fonte_versao, capturado_em, rule_version)
select ru.id,'PHENOLOGY_STAGE',12,29,2,0.4375,'l/ha',
 'Aplicar durante BBCH 12-29. Pueden realizarse 2 aplicaciones a 0,4375 l/ha, espaciadas 20 días.',
 'REGULATORY_FACT','ADAMA España — ficha pública postscript-80, confirmada no ROPF par 2040x2023',
 '2026-08-30T03:19:24Z','2026-08-30T00:00:00Z','ensaio-adama-es-v1'
 from public.registro_uso ru
 join public.registro_regulatorio r on r.id=ru.registro_id and r.registration_id='ES-01516';

-- B · ORDAGO CAPS — nível cultura. A fonte publica dose e nenhum tempo.
--     resolucao NOT_KNOWN é a resposta certa, não um buraco a preencher.
insert into public.registro_uso_janela
 (registro_uso_id, resolucao, dose_max, dose_unidade,
  timing_texto_original, nivel_evidencia, fonte, fonte_versao, capturado_em, rule_version)
select ru.id,'NOT_KNOWN',3.0,'l/ha',
 'linha CULTIVO x DOSIS, cabeçalho "DOSIS (L/Ha)", sem coluna de agente e sem tempo',
 'MANUFACTURER_STATEMENT','ADAMA España — ficha pública ordago-caps',
 '2026-08-30T03:19:24Z','2026-08-30T00:00:00Z','ensaio-adama-es-v1'
 from public.registro_uso ru
 join public.registro_regulatorio r on r.id=ru.registro_id and r.registration_id='ES-00499';

-- C · NEPTUNE — registro caducado em 2026-08-15 e nenhuma janela publicada.
--     A ausência de janela no site é AUSÊNCIA DE PUBLICAÇÃO. Não é janela
--     fechada, e não vira uma.
insert into public.registro_uso_janela
 (registro_uso_id, resolucao, prazo_seguranca_dias,
  timing_texto_original, nivel_evidencia, fonte, fonte_versao, capturado_em, rule_version)
select ru.id,'NOT_KNOWN',null,
 'a ficha pública do NEPTUNE não publica BBCH nem intervalo; o rótulo em PDF não foi lido',
 'MANUFACTURER_STATEMENT','ADAMA España — ficha pública neptune',
 '2026-08-30T03:19:24Z','2026-08-30T00:00:00Z','ensaio-adama-es-v1'
 from public.registro_uso ru
 join public.registro_regulatorio r on r.id=ru.registro_id and r.registration_id='ES-00211';

-- D · TRINITY x cevada — o texto do rótulo oferece DUAS janelas alternativas
--     e o handoff as achatou em BBCH 00-00, que não é o que a fonte diz.
--     Importar como APPROXIMATE preserva a frase inteira; importar 00-00
--     inventaria uma janela de um único estádio. Ver o ensaio D2 abaixo.
insert into public.registro_uso_janela
 (registro_uso_id, resolucao, dose_max, dose_unidade,
  timing_texto_original, nivel_evidencia, fonte, fonte_versao, capturado_em, rule_version)
select ru.id,'APPROXIMATE',2.0,'l/ha',
 'En cebada de invierno se podrá realizar una aplicación en post-emergencia temprada del cultivo, o bien, realizar dicha aplicación en pre-emergencia del cultivo, desde BBCH 00 (semilla seca) hasta BBCH 07 (coleòptilo, emergido de la semilla).',
 'MANUFACTURER_STATEMENT','ADAMA España — ficha pública trinity, coluna Condic. Específico',
 '2026-08-30T03:19:24Z','2026-08-30T00:00:00Z','ensaio-adama-es-v1'
 from public.registro_uso ru
 join public.registro_regulatorio r on r.id=ru.registro_id and r.registration_id='25667'
 join public.crop c on c.id=ru.crop_id and c.codigo='BARLEY';

-- E · TRINITY x centeio — a mesma tabela, coluna "Condic. Específico" VAZIA.
--     Herdar o texto da linha da cevada seria inventar. NOT_KNOWN.
insert into public.registro_uso_janela
 (registro_uso_id, resolucao, dose_max, dose_unidade,
  timing_texto_original, nivel_evidencia, fonte, fonte_versao, capturado_em, rule_version)
select ru.id,'NOT_KNOWN',2.0,'l/ha',
 'linha "Centeno | Malas Hierbas | 2 l/ha |" — a coluna Condic. Específico está vazia na fonte',
 'MANUFACTURER_STATEMENT','ADAMA España — ficha pública trinity, coluna Condic. Específico',
 '2026-08-30T03:19:24Z','2026-08-30T00:00:00Z','ensaio-adama-es-v1'
 from public.registro_uso ru
 join public.registro_regulatorio r on r.id=ru.registro_id and r.registration_id='25667'
 join public.crop c on c.id=ru.crop_id and c.codigo='RYE';

commit;
