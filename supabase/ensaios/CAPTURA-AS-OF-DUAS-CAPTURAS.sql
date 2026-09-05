-- ═══════════════════════════════════════════════════════════════════════
-- ENSAIO — NÃO É IMPORTAÇÃO. Banco DESCARTÁVEL.
--
-- Prova de mecanismo para FUTURE_CAPTURE_CANNOT_REWRITE_PAST_STATE.
--
-- Duas capturas do MESMO registro, em datas diferentes, com o registro
-- dizendo coisas diferentes em cada uma:
--
--   CAPTURA A   observada em 2026-03-10   caducidad 2027-06-30
--   CAPTURA B   observada em 2026-06-20   caducidad 2026-05-31
--
-- A data do caso é 2026-04-23 — entre as duas. Perguntar por ela DEPOIS de
-- B existir tem de continuar devolvendo A.
--
-- ⚠️ O registro `ES-ENSAIO-ASOF` é FICTÍCIO e existe só para exercer o
-- mecanismo. Não é uma autorização real, não descreve nenhum produto real
-- e NUNCA pode entrar no banco canônico. Usar um número de registro real
-- aqui seria pior: afirmaria datas falsas sobre uma autorização de verdade.
-- Há regressão que reprova se ele aparecer fora de supabase/ensaios/.
-- ═══════════════════════════════════════════════════════════════════════

begin;

insert into public.crop (codigo) values ('ENSAIO_CROP') on conflict do nothing;

insert into public.registro_regulatorio
 (pais, registration_id, nome_comercial, titular, formulado, estado,
  fecha_caducidad, fonte, fonte_versao, capturado_em) values
 -- CAPTURA A · o que o registro dizia em março
 ('ES','ES-ENSAIO-ASOF','PRODUTO DE ENSAIO','TITULAR DE ENSAIO',
  'SUBSTANCIA DE ENSAIO','Vigente','2027-06-30',
  'FONTE DE ENSAIO','2026-03-10T09:00:00+01:00','2026-03-10T09:30:00+01:00'),
 -- CAPTURA B · o que ele passou a dizer em junho
 ('ES','ES-ENSAIO-ASOF','PRODUTO DE ENSAIO','TITULAR DE ENSAIO',
  'SUBSTANCIA DE ENSAIO','Vigente','2026-05-31',
  'FONTE DE ENSAIO','2026-06-20T09:00:00+02:00','2026-06-20T09:30:00+02:00');

-- Um uso e uma janela por captura — é assim que o dado nasce hoje, e é
-- justamente isso que a regra de seleção precisa colapsar sem apagar.
insert into public.registro_uso (registro_id, crop_id, substancia)
select r.id, c.id, 'SUBSTANCIA DE ENSAIO'
  from public.registro_regulatorio r, public.crop c
 where r.registration_id='ES-ENSAIO-ASOF' and c.codigo='ENSAIO_CROP';

insert into public.registro_uso_janela
 (registro_uso_id, resolucao, bbch_inicio, bbch_fim, timing_texto_original,
  nivel_evidencia, fonte, fonte_versao, capturado_em, rule_version)
select ru.id,'PHENOLOGY_STAGE',10,50,'janela de ensaio, capturada em '||r.fonte_versao,
       'DERIVED','FONTE DE ENSAIO', r.fonte_versao, r.capturado_em,'ensaio-asof-v1'
  from public.registro_uso ru
  join public.registro_regulatorio r on r.id=ru.registro_id
 where r.registration_id='ES-ENSAIO-ASOF';

commit;
