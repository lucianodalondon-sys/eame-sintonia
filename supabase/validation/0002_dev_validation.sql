-- VALIDACAO DO DEV — SINTONIA EAME
--
-- GERADO por scripts/supabase_dev_validation.py. Nao editar a mao.
--
-- ALVO: um DEV_PROJECT_REF LIMPO, que ainda nao existe.
--
-- REFS RECUSADOS, ambos medidos:
--   hvtycqsrdtmxxodwcwph — branch develop: 51 tabelas herdadas e public.schema_migracao
--   odhdwvugikjdvkapbowe — parent: 732 objetos em storage, 19 tabelas com dado
--
-- Rodar DEPOIS de aplicar supabase/migrations/0001_initial_canonical_schema.sql
-- em um banco limpo de dado E de schema. As duas coisas.
--
-- Tudo acontece dentro de UMA transacao que termina em ROLLBACK: o banco sai
-- como entrou. As verificacoes NEGATIVAS sao as que valem — contar tabela prova
-- que o CREATE correu; so a linha RECUSADA prova que a lei pega.

BEGIN;
SET search_path TO sintonia, public;

CREATE TEMP TABLE _resultado (ordem serial, nome text, tipo text,
                             esperado text, encontrado text, veredito text) ON COMMIT DROP;

-- fixture minima
SAVEPOINT antes_da_fixture;
DO $fx$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $fx$;

-- representacoes em cinco idiomas: UM objeto, cinco linhas
INSERT INTO attention_object_representation (attention_object_id, language, title)
SELECT 'AO-ES-V', l, 'titulo em ' || l
  FROM unnest(ARRAY['pt','en','es','fr','it']::language_code[]) AS l;

-- ── NEGATIVAS: cada uma DEVE ser recusada ──────────────────────────

-- EXPIRY_NE_WITHDRAWAL · prazo com expiry_is_withdrawal = true
DO $n$ BEGIN
  BEGIN
    insert into organization (organization_id, name) values ('ORG-V', 'x');
    insert into product (product_id, normalized_name) values ('PRD-V', 'x');
    insert into registration (registration_id, country, registration_number,
    holder_organization_id, product_id, source_id)
    values ('REG-V', 'IT', '0001', 'ORG-V', 'PRD-V', 'SRC-V');
    insert into registration_deadline (deadline_id, registration_id, deadline_date,
    deadline_kind, status_as_declared_by_source, expiry_is_withdrawal,
    evidence_id, source_id)
    values ('DL-V', 'REG-V', '2027-03-31', 'EXPIRY', 'IN FORCE', true,
    'EV-V', 'SRC-V');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('EXPIRY_NE_WITHDRAWAL', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('EXPIRY_NE_WITHDRAWAL', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- PRAZO_NAO_AUTORIZA_BUSINESS_DECISION · objeto de prazo com max_authorized_action = BUSINESS_DECISION
DO $n$ BEGIN
  BEGIN
    insert into organization (organization_id, name) values ('ORG-W', 'x');
    insert into product (product_id, normalized_name) values ('PRD-W', 'x');
    insert into registration (registration_id, country, registration_number,
    holder_organization_id, product_id, source_id)
    values ('REG-W', 'IT', '0002', 'ORG-W', 'PRD-W', 'SRC-V');
    insert into regulatory_deadline_object (attention_object_id, registration_id,
    deadline_date, deadline_kind, status_as_declared_by_source,
    max_authorized_action)
    values ('AO-IT-V', 'REG-W', '2027-03-31', 'EXPIRY', 'IN FORCE',
    'BUSINESS_DECISION');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('PRAZO_NAO_AUTORIZA_BUSINESS_DECISION', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('PRAZO_NAO_AUTORIZA_BUSINESS_DECISION', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- MEDIA_EXIGE_N · leitura de serie com n = 0
DO $n$ BEGIN
  BEGIN
    insert into field_pressure_reading (reading_id, series_id, value, n, unit, source_id)
    values ('RD-V', 'SER-V', 12.5, 0, 'pct', 'SRC-V');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('MEDIA_EXIGE_N', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('MEDIA_EXIGE_N', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- MEDIA_EXIGE_N_NAO_NULO · leitura de serie com n nulo
DO $n$ BEGIN
  BEGIN
    insert into field_pressure_reading (reading_id, series_id, value, n, unit, source_id)
    values ('RD-W', 'SER-V', 12.5, null, 'pct', 'SRC-V');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('MEDIA_EXIGE_N_NAO_NULO', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('MEDIA_EXIGE_N_NAO_NULO', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- LOCALITY_TEXT_NAO_E_POINT · localidade em texto carregando geometria
DO $n$ BEGIN
  BEGIN
    insert into geo_anchor (geo_id, country, locality_text, geometry, geo_resolution,
    geometry_source_id)
    values ('GEO-X', 'ES', 'cerca de Jaen', '{"type":"Point"}'::jsonb,
    'LOCALITY_TEXT', 'SRC-V');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('LOCALITY_TEXT_NAO_E_POINT', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('LOCALITY_TEXT_NAO_E_POINT', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- POINT_EXIGE_GEOMETRIA · resolucao POINT sem geometria
DO $n$ BEGIN
  BEGIN
    insert into geo_anchor (geo_id, country, geo_resolution)
    values ('GEO-Y', 'ES', 'POINT');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('POINT_EXIGE_GEOMETRIA', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('POINT_EXIGE_GEOMETRIA', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- GEOMETRIA_EXIGE_ORIGEM · geometria sem fonte declarada
DO $n$ BEGIN
  BEGIN
    insert into geo_anchor (geo_id, country, geometry, geo_resolution)
    values ('GEO-Z', 'ES', '{"type":"Point"}'::jsonb, 'POINT');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('GEOMETRIA_EXIGE_ORIGEM', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('GEOMETRIA_EXIGE_ORIGEM', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- DEPENDENTE_DECLARA_ALVO · perna DEPENDENT sem tipo de dependencia e sem alvo
DO $n$ BEGIN
  BEGIN
    insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
    source_id, independence_state)
    values ('LEG-W', 'PROP-V', 'FIELD_HISTORICAL', 'EV-V', 'SRC-V', 'DEPENDENT');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('DEPENDENTE_DECLARA_ALVO', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('DEPENDENTE_DECLARA_ALVO', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- INDEPENDENTE_NAO_TEM_ALVO · perna INDEPENDENT apontando para outra perna
DO $n$ BEGIN
  BEGIN
    insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
    source_id, independence_state, depends_on_leg_id)
    values ('LEG-X', 'PROP-V', 'CREATOR', 'EV-V', 'SRC-V', 'INDEPENDENT', 'LEG-V');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('INDEPENDENTE_NAO_TEM_ALVO', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('INDEPENDENTE_NAO_TEM_ALVO', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- SOURCE_LANGUAGE_VOCABULARIO_FECHADO · lingua fora do vocabulario
DO $n$ BEGIN
  BEGIN
    insert into evidence (evidence_id, source_id, source_language)
    values ('EV-X', 'SRC-V', 'de');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('SOURCE_LANGUAGE_VOCABULARIO_FECHADO', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('SOURCE_LANGUAGE_VOCABULARIO_FECHADO', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- SOURCE_LANGUAGE_NAO_ACEITA_TRACO · lingua igual a travessao
DO $n$ BEGIN
  BEGIN
    insert into evidence (evidence_id, source_id, source_language)
    values ('EV-Y', 'SRC-V', '—');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('SOURCE_LANGUAGE_NAO_ACEITA_TRACO', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('SOURCE_LANGUAGE_NAO_ACEITA_TRACO', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- EXPERTISE_PROVADA_EXIGE_EVIDENCIA · expertise PROVED sem evidencia
DO $n$ BEGIN
  BEGIN
    insert into person (person_id) values ('PER-V');
    insert into issue_expertise (person_id, crop_term_id, issue_term_id,
    issue_expertise_state)
    values ('PER-V', 'CROP-V', 'ISSUE-V', 'PROVED');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('EXPERTISE_PROVADA_EXIGE_EVIDENCIA', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('EXPERTISE_PROVADA_EXIGE_EVIDENCIA', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- GDPR_ANTES_DA_IDENTIDADE · observacao de pessoa identificada com GDPR nao iniciado
DO $n$ BEGIN
  BEGIN
    insert into observation (observation_id, observation_kind, source_id, signal_family)
    values ('OBS-V', 'FIELD_VOICE_OBSERVATION', 'SRC-V', 'CREATOR');
    insert into field_voice_observation (observation_id, entity_kind, platform,
    gdpr_treatment_state)
    values ('OBS-V', 'PERSON_CREATOR', 'youtube', 'NOT_STARTED');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('GDPR_ANTES_DA_IDENTIDADE', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('GDPR_ANTES_DA_IDENTIDADE', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- LATENCIA_SEM_MEDICAO_E_NULA · latencia com valor sem estado PROVED
DO $n$ BEGIN
  BEGIN
    insert into source_clock (source_id, source_status, pipeline_latency_state,
    pipeline_latency_seconds)
    values ('SRC-V', 'ABERTA', 'NOT_MEASURED', 0);
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('LATENCIA_SEM_MEDICAO_E_NULA', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('LATENCIA_SEM_MEDICAO_E_NULA', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- PUBLICADO_EXIGE_SOMBRA · publish_run PUBLISHED sem sombra aprovada
DO $n$ BEGIN
  BEGIN
    insert into publish_run (publish_run_id, pipeline_version, schema_version,
    status, shadow_validation_passed)
    values ('RUN-X', 'v', '0.1.0-draft', 'PUBLISHED', false);
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('PUBLICADO_EXIGE_SOMBRA', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('PUBLICADO_EXIGE_SOMBRA', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- BACKENDS_NAO_SE_MISTURAM · proveniencia com repositorio E tabela ao mesmo tempo
DO $n$ BEGIN
  BEGIN
    insert into storage_provenance (subject_kind, subject_id, source_backend,
    repository, path, commit_sha, db_schema, table_or_view, primary_key)
    values ('evidence', 'EV-V', 'GITHUB', 'r', 'p',
    'd7b289425c5e436f3ce68e367b8706e11910f43b',
    'sintonia', 'evidence', 'evidence_id');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('BACKENDS_NAO_SE_MISTURAM', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('BACKENDS_NAO_SE_MISTURAM', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- GITHUB_EXIGE_COMMIT · proveniencia GITHUB sem commit_sha
DO $n$ BEGIN
  BEGIN
    insert into storage_provenance (subject_kind, subject_id, source_backend,
    repository, path)
    values ('evidence', 'EV-V', 'GITHUB', 'r', 'p');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('GITHUB_EXIGE_COMMIT', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('GITHUB_EXIGE_COMMIT', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- PORTFOLIO_E_SEMPRE_CONTEXTO · portfolio local marcado como evidencia
DO $n$ BEGIN
  BEGIN
    insert into local_adama_portfolio_context (context_id, country, source_id,
    is_context_not_evidence)
    values ('CTX-V', 'ES', 'SRC-V', false);
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('PORTFOLIO_E_SEMPRE_CONTEXTO', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('PORTFOLIO_E_SEMPRE_CONTEXTO', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- OBJETO_NAO_SE_RELACIONA_CONSIGO · objeto relacionado a si mesmo
DO $n$ BEGIN
  BEGIN
    insert into object_relation (from_object_id, to_object_id, relation_kind)
    values ('AO-ES-V', 'AO-ES-V', 'MESMO');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('OBJETO_NAO_SE_RELACIONA_CONSIGO', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('OBJETO_NAO_SE_RELACIONA_CONSIGO', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- MUDANCA_DE_ESTADO_EXIGE_ESTADO · evento STATE_CHANGE sem estado depois
DO $n$ BEGIN
  BEGIN
    insert into object_event (event_id, attention_object_id, event_type, what_changed)
    values ('EVT-V', 'AO-ES-V', 'STATE_CHANGE', 'mudou');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('MUDANCA_DE_ESTADO_EXIGE_ESTADO', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('MUDANCA_DE_ESTADO_EXIGE_ESTADO', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- VAZIO_TEMPORAL_DECLARA_MOTIVO · evento GAP sem motivo
DO $n$ BEGIN
  BEGIN
    insert into object_event (event_id, attention_object_id, event_type, what_changed)
    values ('EVT-W', 'AO-ES-V', 'GAP', 'nada');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('VAZIO_TEMPORAL_DECLARA_MOTIVO', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('VAZIO_TEMPORAL_DECLARA_MOTIVO', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- SEM_DATA_SEM_PRECISAO · evento sem data com resolucao exata
DO $n$ BEGIN
  BEGIN
    insert into object_event (event_id, attention_object_id, event_type,
    event_at_resolution, what_changed)
    values ('EVT-X', 'AO-ES-V', 'NEW_EVIDENCE', 'EXACT_DATE', 'x');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('SEM_DATA_SEM_PRECISAO', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('SEM_DATA_SEM_PRECISAO', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- PERFIL_PERTENCE_A_UMA_ENTIDADE · perfil de creator sem pessoa e sem negocio
DO $n$ BEGIN
  BEGIN
    insert into creator_content_profile (profile_id, entity_kind, platform, source_id)
    values ('PRF-V', 'PERSON_CREATOR', 'youtube', 'SRC-V');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('PERFIL_PERTENCE_A_UMA_ENTIDADE', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('PERFIL_PERTENCE_A_UMA_ENTIDADE', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- CONCORDANCIA_EXIGE_PORTAO · cadeia com concordancia PROVED e portao NOT_RUN
DO $n$ BEGIN
  BEGIN
    insert into organization (organization_id, name) values ('ORG-Z', 'x');
    insert into competitor_product_identity (identity_id, country,
    competitor_organization_id, agreement_state, urbole_guard_result)
    values ('CPI-V', 'ES', 'ORG-Z', 'PROVED', 'NOT_RUN');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('CONCORDANCIA_EXIGE_PORTAO', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('CONCORDANCIA_EXIGE_PORTAO', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- PAR_PROVADO_EXIGE_PASSAGEM · pareamento cultura x problema PROVED sem a passagem
DO $n$ BEGIN
  BEGIN
    insert into phenomenon_case (attention_object_id, geo_id, crop_term_id,
    issue_term_id, crop_issue_pairing_state)
    values ('AO-ES-V', 'GEO-ES', 'CROP-V', 'ISSUE-V', 'PROVED');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('PAR_PROVADO_EXIGE_PASSAGEM', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('PAR_PROVADO_EXIGE_PASSAGEM', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- OFFSETS_ANDAM_EM_PAR · offset de passagem pela metade
DO $n$ BEGIN
  BEGIN
    insert into evidence (evidence_id, source_id, passage_start)
    values ('EV-Z', 'SRC-V', 10);
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('OFFSETS_ANDAM_EM_PAR', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('OFFSETS_ANDAM_EM_PAR', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- TRADUCAO_NAO_E_NA_LINGUA_DE_ORIGEM · traducao com lingua UNKNOWN
DO $n$ BEGIN
  BEGIN
    insert into content_translation (canonical_entity_id, translation_language,
    translated_text, translation_provenance)
    values ('AO-ES-V', 'UNKNOWN', 'x', 'y');
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('TRADUCAO_NAO_E_NA_LINGUA_DE_ORIGEM', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');
  EXCEPTION WHEN others THEN
    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
    VALUES ('TRADUCAO_NAO_E_NA_LINGUA_DE_ORIGEM', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');
  END;
  ROLLBACK TO SAVEPOINT antes_da_fixture;
  -- refazer a fixture: o rollback do teste desfez tudo
END $n$;
DO $rf$ BEGIN

  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');

END $rf$;

-- ── POSITIVAS: contagem e derivacao ────────────────────────────────
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'TABLES_ACTUAL', 'POSITIVA', '57', v::text,
       CASE WHEN v::text = '57' THEN 'PASS' ELSE 'FAIL' END
  FROM (select count(*) from information_schema.tables where table_schema = 'sintonia' and table_type = 'BASE TABLE') s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'VIEWS_ACTUAL', 'POSITIVA', '13', v::text,
       CASE WHEN v::text = '13' THEN 'PASS' ELSE 'FAIL' END
  FROM (select count(*) from information_schema.views where table_schema = 'sintonia') s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'RPCS_ACTUAL', 'POSITIVA', '5', v::text,
       CASE WHEN v::text = '5' THEN 'PASS' ELSE 'FAIL' END
  FROM (select count(*) from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'sintonia') s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'ENUMS_ACTUAL', 'POSITIVA', '27', v::text,
       CASE WHEN v::text = '27' THEN 'PASS' ELSE 'FAIL' END
  FROM (select count(distinct t.typname) from pg_type t join pg_namespace n on n.oid = t.typnamespace where n.nspname = 'sintonia' and t.typtype = 'e') s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'RLS_ENABLED_ALL', 'POSITIVA', '57', v::text,
       CASE WHEN v::text = '57' THEN 'PASS' ELSE 'FAIL' END
  FROM (select count(*) from pg_class c join pg_namespace n on n.oid = c.relnamespace where n.nspname = 'sintonia' and c.relkind = 'r' and c.relrowsecurity) s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'PUBLISHER_POLICIES', 'POSITIVA', '57', v::text,
       CASE WHEN v::text = '57' THEN 'PASS' ELSE 'FAIL' END
  FROM (select count(*) from pg_policies where schemaname = 'sintonia' and policyname = 'publisher_all') s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'INDEXES_ON_FK', 'POSITIVA', '86', v::text,
       CASE WHEN v::text = '86' THEN 'PASS' ELSE 'FAIL' END
  FROM (select count(*) from pg_indexes where schemaname = 'sintonia' and indexname like '%\_idx') s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'CONVERGENCE_SINGLE_SIGNAL', 'POSITIVA', 'SINGLE_SIGNAL', v::text,
       CASE WHEN v::text = 'SINGLE_SIGNAL' THEN 'PASS' ELSE 'FAIL' END
  FROM (select convergence_state from v_convergence_state where proposition_id = 'PROP-V') s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'READINESS_NOT_READY', 'POSITIVA', 'false', v::text,
       CASE WHEN v::text = 'false' THEN 'PASS' ELSE 'FAIL' END
  FROM (select coalesce(computed_is_ready, false)::text from v_attention_readiness where attention_object_id = 'AO-ES-V') s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'COUNTRY_ISOLATION_ES', 'POSITIVA', '1', v::text,
       CASE WHEN v::text = '1' THEN 'PASS' ELSE 'FAIL' END
  FROM (select count(*) from attention_object where country = 'ES') s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'COUNTRY_ISOLATION_IT', 'POSITIVA', '1', v::text,
       CASE WHEN v::text = '1' THEN 'PASS' ELSE 'FAIL' END
  FROM (select count(*) from attention_object where country = 'IT') s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'COUNTRY_ISOLATION_FR', 'POSITIVA', '1', v::text,
       CASE WHEN v::text = '1' THEN 'PASS' ELSE 'FAIL' END
  FROM (select count(*) from attention_object where country = 'FR') s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'MULTILINGUAL_ONE_OBJECT', 'POSITIVA', '1', v::text,
       CASE WHEN v::text = '1' THEN 'PASS' ELSE 'FAIL' END
  FROM (select count(distinct attention_object_id) from attention_object_representation where attention_object_id = 'AO-ES-V') s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'MULTILINGUAL_FIVE_LANGUAGES', 'POSITIVA', '5', v::text,
       CASE WHEN v::text = '5' THEN 'PASS' ELSE 'FAIL' END
  FROM (select count(*) from attention_object_representation where attention_object_id = 'AO-ES-V') s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'ORIGINAL_PRESERVED', 'POSITIVA', 'texto original em espanhol', v::text,
       CASE WHEN v::text = 'texto original em espanhol' THEN 'PASS' ELSE 'FAIL' END
  FROM (select original_text from content_entity where canonical_entity_id = 'AO-ES-V') s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'PROVENANCE_REACHES_COMMIT', 'POSITIVA', 'd7b289425c5e436f3ce68e367b8706e11910f43b', v::text,
       CASE WHEN v::text = 'd7b289425c5e436f3ce68e367b8706e11910f43b' THEN 'PASS' ELSE 'FAIL' END
  FROM (select commit_sha from v_publish_provenance where attention_object_id = 'AO-ES-V' limit 1) s(v);
INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
SELECT 'ALLOWED_COUNTRIES_DENIES_BY_DEFAULT', 'POSITIVA', '0', v::text,
       CASE WHEN v::text = '0' THEN 'PASS' ELSE 'FAIL' END
  FROM (select coalesce(array_length(allowed_countries(), 1), 0)) s(v);

-- ── RESULTADO ──────────────────────────────────────────────────────
SELECT jsonb_pretty(jsonb_build_object(
  'DEV_PROJECT_REF', current_setting('sintonia.dev_ref', true),
  'TOTAL', (select count(*) from _resultado),
  'PASS', (select count(*) from _resultado where veredito = 'PASS'),
  'FAIL', (select count(*) from _resultado where veredito = 'FAIL'),
  'FALHAS', (select coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb)
             from (select nome, tipo, esperado, encontrado from _resultado
                   where veredito = 'FAIL' order by ordem) t),
  'TUDO', (select jsonb_agg(to_jsonb(t) order by t.ordem)
           from (select * from _resultado) t)
)) AS validacao;

-- O banco sai como entrou.
ROLLBACK;
