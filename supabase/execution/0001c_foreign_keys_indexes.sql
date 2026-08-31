-- SINTONIA EAME · EXECUCAO EM PARTES · BLOCO C DE 5 (CHAVES ESTRANGEIRAS E INDICES)
--
-- GERADO por scripts/supabase_execution_split.py. Nao editar a mao.
--
-- ORIGEM: supabase/migrations/0001_initial_canonical_schema.sql
-- SHA256 DA ORIGEM: 41ffeb52941718a34a01135e2f76bc4611a2978e049175f90cf4014117e335ec
-- ALVO: xhqebdweltytnghiavew (eame-sintonia-dev)
--
-- PARA QUE: as FKs com ON DELETE explicito e os indices. Exige todas as tabelas de pe — por isso vem depois de b.
--
-- ORDEM: rode a, b, c, d, e nesta ordem. Cada um abre e fecha a propria
-- transacao: se um falhar, ele volta inteiro e os anteriores ficam de pe.
--
-- O QUE E ANDAIME AQUI: este cabecalho, o BEGIN/COMMIT abaixo e o
-- SET search_path. Foram acrescentados porque cada arquivo roda numa
-- sessao propria. Tudo o que esta entre as duas marcas e fatia LITERAL
-- do arquivo canonico, byte a byte, e a prova de reconstrucao confere.

BEGIN;
SET search_path TO sintonia, public;

-- >>> CORPO CANONICO — FATIA LITERAL DE 0001, NAO EDITAR >>>


-- ── CHAVES ESTRANGEIRAS ───────────────────────────────────────────────
-- Declaradas depois das tabelas: o grafo tem ciclos legitimos
-- (evidence -> source -> ... -> evidence) e ordenar por dependencia
-- exigiria quebrar uma relacao real.
ALTER TABLE ontology_term_label ADD CONSTRAINT ontology_term_label_term_id_fk
  FOREIGN KEY (term_id) REFERENCES ontology_term (term_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE geo_anchor ADD CONSTRAINT geo_anchor_geometry_source_id_fk
  FOREIGN KEY (geometry_source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE source_snapshot ADD CONSTRAINT source_snapshot_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE source_clock ADD CONSTRAINT source_clock_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE source_provenance ADD CONSTRAINT source_provenance_evidence_id_fk
  FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE source_provenance ADD CONSTRAINT source_provenance_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE source_provenance ADD CONSTRAINT source_provenance_snapshot_id_fk
  FOREIGN KEY (snapshot_id) REFERENCES source_snapshot (snapshot_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE storage_provenance ADD CONSTRAINT storage_provenance_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE storage_provenance ADD CONSTRAINT storage_provenance_publish_run_id_fk
  FOREIGN KEY (publish_run_id) REFERENCES publish_run (publish_run_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE evidence ADD CONSTRAINT evidence_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE evidence ADD CONSTRAINT evidence_snapshot_id_fk
  FOREIGN KEY (snapshot_id) REFERENCES source_snapshot (snapshot_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE evidence ADD CONSTRAINT evidence_fact_location_geo_id_fk
  FOREIGN KEY (fact_location_geo_id) REFERENCES geo_anchor (geo_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE content_entity ADD CONSTRAINT content_entity_evidence_id_fk
  FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE content_translation ADD CONSTRAINT content_translation_canonical_entity_id_fk
  FOREIGN KEY (canonical_entity_id) REFERENCES content_entity (canonical_entity_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE attention_object ADD CONSTRAINT attention_object_publish_run_id_fk
  FOREIGN KEY (publish_run_id) REFERENCES publish_run (publish_run_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE attention_object_representation ADD CONSTRAINT attention_object_representation_attention_object_id_fk
  FOREIGN KEY (attention_object_id) REFERENCES attention_object (attention_object_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE attention_readiness ADD CONSTRAINT attention_readiness_attention_object_id_fk
  FOREIGN KEY (attention_object_id) REFERENCES attention_object (attention_object_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE attention_object_evidence ADD CONSTRAINT attention_object_evidence_attention_object_id_fk
  FOREIGN KEY (attention_object_id) REFERENCES attention_object (attention_object_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE attention_object_evidence ADD CONSTRAINT attention_object_evidence_evidence_id_fk
  FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE attention_object_unknown ADD CONSTRAINT attention_object_unknown_attention_object_id_fk
  FOREIGN KEY (attention_object_id) REFERENCES attention_object (attention_object_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE object_clock ADD CONSTRAINT object_clock_attention_object_id_fk
  FOREIGN KEY (attention_object_id) REFERENCES attention_object (attention_object_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE object_clock ADD CONSTRAINT object_clock_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE phenomenon_case ADD CONSTRAINT phenomenon_case_attention_object_id_fk
  FOREIGN KEY (attention_object_id) REFERENCES attention_object (attention_object_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE phenomenon_case ADD CONSTRAINT phenomenon_case_geo_id_fk
  FOREIGN KEY (geo_id) REFERENCES geo_anchor (geo_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_3_OBRIGATORIA
ALTER TABLE phenomenon_case ADD CONSTRAINT phenomenon_case_crop_term_id_fk
  FOREIGN KEY (crop_term_id) REFERENCES ontology_term (term_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE phenomenon_case ADD CONSTRAINT phenomenon_case_issue_term_id_fk
  FOREIGN KEY (issue_term_id) REFERENCES ontology_term (term_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE phenomenon_case ADD CONSTRAINT phenomenon_case_pairing_evidence_id_fk
  FOREIGN KEY (pairing_evidence_id) REFERENCES evidence (evidence_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE regulatory_deadline_object ADD CONSTRAINT regulatory_deadline_object_attention_object_id_fk
  FOREIGN KEY (attention_object_id) REFERENCES attention_object (attention_object_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE regulatory_deadline_object ADD CONSTRAINT regulatory_deadline_object_registration_id_fk
  FOREIGN KEY (registration_id) REFERENCES registration (registration_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_3_OBRIGATORIA
ALTER TABLE competitor_identity_chain_object ADD CONSTRAINT competitor_identity_chain_object_attention_object_id_fk
  FOREIGN KEY (attention_object_id) REFERENCES attention_object (attention_object_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE competitor_identity_chain_object ADD CONSTRAINT competitor_identity_chain_object_competitor_product_identity_id_fk
  FOREIGN KEY (competitor_product_identity_id) REFERENCES competitor_product_identity (identity_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_3_OBRIGATORIA
ALTER TABLE longitudinal_field_pressure_object ADD CONSTRAINT longitudinal_field_pressure_object_attention_object_id_fk
  FOREIGN KEY (attention_object_id) REFERENCES attention_object (attention_object_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE longitudinal_field_pressure_object ADD CONSTRAINT longitudinal_field_pressure_object_series_id_fk
  FOREIGN KEY (series_id) REFERENCES field_pressure_series (series_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_3_OBRIGATORIA
ALTER TABLE observation ADD CONSTRAINT observation_geo_id_fk
  FOREIGN KEY (geo_id) REFERENCES geo_anchor (geo_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE observation ADD CONSTRAINT observation_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE observation ADD CONSTRAINT observation_evidence_id_fk
  FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE territorial_observation ADD CONSTRAINT territorial_observation_observation_id_fk
  FOREIGN KEY (observation_id) REFERENCES observation (observation_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE territorial_observation ADD CONSTRAINT territorial_observation_crop_term_id_fk
  FOREIGN KEY (crop_term_id) REFERENCES ontology_term (term_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE territorial_observation ADD CONSTRAINT territorial_observation_issue_term_id_fk
  FOREIGN KEY (issue_term_id) REFERENCES ontology_term (term_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE territorial_observation ADD CONSTRAINT territorial_observation_document_excerpt_evidence_id_fk
  FOREIGN KEY (document_excerpt_evidence_id) REFERENCES evidence (evidence_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE registration ADD CONSTRAINT registration_holder_organization_id_fk
  FOREIGN KEY (holder_organization_id) REFERENCES organization (organization_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE registration ADD CONSTRAINT registration_product_id_fk
  FOREIGN KEY (product_id) REFERENCES product (product_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE registration ADD CONSTRAINT registration_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE registration_deadline ADD CONSTRAINT registration_deadline_registration_id_fk
  FOREIGN KEY (registration_id) REFERENCES registration (registration_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_3_OBRIGATORIA
ALTER TABLE registration_deadline ADD CONSTRAINT registration_deadline_evidence_id_fk
  FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE registration_deadline ADD CONSTRAINT registration_deadline_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE product ADD CONSTRAINT product_active_ingredient_term_id_fk
  FOREIGN KEY (active_ingredient_term_id) REFERENCES ontology_term (term_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE trademark_record ADD CONSTRAINT trademark_record_holder_organization_id_fk
  FOREIGN KEY (holder_organization_id) REFERENCES organization (organization_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE trademark_record ADD CONSTRAINT trademark_record_evidence_id_fk
  FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE competitor_product_identity ADD CONSTRAINT competitor_product_identity_competitor_organization_id_fk
  FOREIGN KEY (competitor_organization_id) REFERENCES organization (organization_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_3_OBRIGATORIA
ALTER TABLE competitor_product_identity ADD CONSTRAINT competitor_product_identity_normalized_product_id_fk
  FOREIGN KEY (normalized_product_id) REFERENCES product (product_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE competitor_product_identity ADD CONSTRAINT competitor_product_identity_trademark_id_fk
  FOREIGN KEY (trademark_id) REFERENCES trademark_record (trademark_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE competitor_product_identity ADD CONSTRAINT competitor_product_identity_local_registration_id_fk
  FOREIGN KEY (local_registration_id) REFERENCES registration (registration_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE competitor_product_identity ADD CONSTRAINT competitor_product_identity_observed_paid_activity_id_fk
  FOREIGN KEY (observed_paid_activity_id) REFERENCES observed_paid_activity (paid_activity_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE observed_paid_activity ADD CONSTRAINT observed_paid_activity_observation_id_fk
  FOREIGN KEY (observation_id) REFERENCES observation (observation_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE company_local_account ADD CONSTRAINT company_local_account_organization_id_fk
  FOREIGN KEY (organization_id) REFERENCES organization (organization_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_3_OBRIGATORIA
ALTER TABLE company_public_content ADD CONSTRAINT company_public_content_account_id_fk
  FOREIGN KEY (account_id) REFERENCES company_local_account (account_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_3_OBRIGATORIA
ALTER TABLE company_public_content ADD CONSTRAINT company_public_content_evidence_id_fk
  FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE field_pressure_series ADD CONSTRAINT field_pressure_series_crop_term_id_fk
  FOREIGN KEY (crop_term_id) REFERENCES ontology_term (term_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE field_pressure_series ADD CONSTRAINT field_pressure_series_issue_term_id_fk
  FOREIGN KEY (issue_term_id) REFERENCES ontology_term (term_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE field_pressure_series ADD CONSTRAINT field_pressure_series_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE field_pressure_reading ADD CONSTRAINT field_pressure_reading_series_id_fk
  FOREIGN KEY (series_id) REFERENCES field_pressure_series (series_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_3_OBRIGATORIA
ALTER TABLE field_pressure_reading ADD CONSTRAINT field_pressure_reading_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE field_pressure_reading ADD CONSTRAINT field_pressure_reading_observation_id_fk
  FOREIGN KEY (observation_id) REFERENCES observation (observation_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE scientific_person ADD CONSTRAINT scientific_person_person_id_fk
  FOREIGN KEY (person_id) REFERENCES person (person_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE scientific_person ADD CONSTRAINT scientific_person_organization_id_fk
  FOREIGN KEY (organization_id) REFERENCES organization (organization_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE scientific_person ADD CONSTRAINT scientific_person_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE scientific_publication ADD CONSTRAINT scientific_publication_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE scientific_publication ADD CONSTRAINT scientific_publication_evidence_id_fk
  FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE publication_author ADD CONSTRAINT publication_author_publication_id_fk
  FOREIGN KEY (publication_id) REFERENCES scientific_publication (publication_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE publication_author ADD CONSTRAINT publication_author_person_id_fk
  FOREIGN KEY (person_id) REFERENCES person (person_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE issue_expertise ADD CONSTRAINT issue_expertise_person_id_fk
  FOREIGN KEY (person_id) REFERENCES person (person_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE issue_expertise ADD CONSTRAINT issue_expertise_crop_term_id_fk
  FOREIGN KEY (crop_term_id) REFERENCES ontology_term (term_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE issue_expertise ADD CONSTRAINT issue_expertise_issue_term_id_fk
  FOREIGN KEY (issue_term_id) REFERENCES ontology_term (term_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE issue_expertise ADD CONSTRAINT issue_expertise_evidence_id_fk
  FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE person_creator ADD CONSTRAINT person_creator_person_id_fk
  FOREIGN KEY (person_id) REFERENCES person (person_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE person_creator ADD CONSTRAINT person_creator_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE farm_business_entity ADD CONSTRAINT farm_business_entity_organization_id_fk
  FOREIGN KEY (organization_id) REFERENCES organization (organization_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE farm_business_entity ADD CONSTRAINT farm_business_entity_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE creator_content_profile ADD CONSTRAINT creator_content_profile_person_id_fk
  FOREIGN KEY (person_id) REFERENCES person (person_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE creator_content_profile ADD CONSTRAINT creator_content_profile_business_id_fk
  FOREIGN KEY (business_id) REFERENCES farm_business_entity (business_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE creator_content_profile ADD CONSTRAINT creator_content_profile_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE field_voice_observation ADD CONSTRAINT field_voice_observation_observation_id_fk
  FOREIGN KEY (observation_id) REFERENCES observation (observation_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE field_voice_observation ADD CONSTRAINT field_voice_observation_profile_id_fk
  FOREIGN KEY (profile_id) REFERENCES creator_content_profile (profile_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE field_voice_observation ADD CONSTRAINT field_voice_observation_crop_mentioned_term_id_fk
  FOREIGN KEY (crop_mentioned_term_id) REFERENCES ontology_term (term_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE field_voice_observation ADD CONSTRAINT field_voice_observation_issue_mentioned_term_id_fk
  FOREIGN KEY (issue_mentioned_term_id) REFERENCES ontology_term (term_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE field_voice_observation ADD CONSTRAINT field_voice_observation_content_entity_id_fk
  FOREIGN KEY (content_entity_id) REFERENCES content_entity (canonical_entity_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE local_adama_portfolio_context ADD CONSTRAINT local_adama_portfolio_context_crop_term_id_fk
  FOREIGN KEY (crop_term_id) REFERENCES ontology_term (term_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE local_adama_portfolio_context ADD CONSTRAINT local_adama_portfolio_context_issue_term_id_fk
  FOREIGN KEY (issue_term_id) REFERENCES ontology_term (term_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE local_adama_portfolio_context ADD CONSTRAINT local_adama_portfolio_context_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE portfolio_product_ref ADD CONSTRAINT portfolio_product_ref_context_id_fk
  FOREIGN KEY (context_id) REFERENCES local_adama_portfolio_context (context_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE portfolio_product_ref ADD CONSTRAINT portfolio_product_ref_product_id_fk
  FOREIGN KEY (product_id) REFERENCES product (product_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE portfolio_product_ref ADD CONSTRAINT portfolio_product_ref_registration_id_fk
  FOREIGN KEY (registration_id) REFERENCES registration (registration_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE convergence_proposition ADD CONSTRAINT convergence_proposition_attention_object_id_fk
  FOREIGN KEY (attention_object_id) REFERENCES attention_object (attention_object_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_3_OBRIGATORIA
ALTER TABLE convergence_leg ADD CONSTRAINT convergence_leg_proposition_id_fk
  FOREIGN KEY (proposition_id) REFERENCES convergence_proposition (proposition_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_3_OBRIGATORIA
ALTER TABLE convergence_leg ADD CONSTRAINT convergence_leg_evidence_id_fk
  FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE convergence_leg ADD CONSTRAINT convergence_leg_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE convergence_leg ADD CONSTRAINT convergence_leg_depends_on_leg_id_fk
  FOREIGN KEY (depends_on_leg_id) REFERENCES convergence_leg (leg_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE dependency_edge ADD CONSTRAINT dependency_edge_evidence_id_fk
  FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE object_relation ADD CONSTRAINT object_relation_from_object_id_fk
  FOREIGN KEY (from_object_id) REFERENCES attention_object (attention_object_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_3_OBRIGATORIA
ALTER TABLE object_relation ADD CONSTRAINT object_relation_to_object_id_fk
  FOREIGN KEY (to_object_id) REFERENCES attention_object (attention_object_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_3_OBRIGATORIA
ALTER TABLE object_relation ADD CONSTRAINT object_relation_evidence_id_fk
  FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE object_event ADD CONSTRAINT object_event_attention_object_id_fk
  FOREIGN KEY (attention_object_id) REFERENCES attention_object (attention_object_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_3_OBRIGATORIA
ALTER TABLE object_event ADD CONSTRAINT object_event_source_id_fk
  FOREIGN KEY (source_id) REFERENCES source (source_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE object_event ADD CONSTRAINT object_event_observation_id_fk
  FOREIGN KEY (observation_id) REFERENCES observation (observation_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE action ADD CONSTRAINT action_attention_object_id_fk
  FOREIGN KEY (attention_object_id) REFERENCES attention_object (attention_object_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_3_OBRIGATORIA
ALTER TABLE action_evidence ADD CONSTRAINT action_evidence_action_id_fk
  FOREIGN KEY (action_id) REFERENCES action (action_id)
  ON DELETE CASCADE ON UPDATE CASCADE;  -- REGRA_2_FILHA_CAI_COM_A_RAIZ
ALTER TABLE action_evidence ADD CONSTRAINT action_evidence_evidence_id_fk
  FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE entry_path_event ADD CONSTRAINT entry_path_event_attention_object_id_fk
  FOREIGN KEY (attention_object_id) REFERENCES attention_object (attention_object_id)
  ON DELETE SET NULL ON UPDATE CASCADE;  -- REGRA_4_OPCIONAL
ALTER TABLE entry_path_event ADD CONSTRAINT entry_path_event_crop_term_id_fk
  FOREIGN KEY (crop_term_id) REFERENCES ontology_term (term_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE publish_run_freeze ADD CONSTRAINT publish_run_freeze_publish_run_id_fk
  FOREIGN KEY (publish_run_id) REFERENCES publish_run (publish_run_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS
ALTER TABLE shadow_validation ADD CONSTRAINT shadow_validation_publish_run_id_fk
  FOREIGN KEY (publish_run_id) REFERENCES publish_run (publish_run_id)
  ON DELETE RESTRICT ON UPDATE CASCADE;  -- REGRA_1_IMUTAVEIS

-- ── INDICES ───────────────────────────────────────────────────────────
-- O Postgres indexa PK e UNIQUE, e NAO a coluna que aponta para fora. Sem estes indices todo join do produto varre a tabela inteira, e o produto e feito de joins. Nao ha indice em coluna que ja e a primeira da PK ou de um UNIQUE: seria duplicado.
CREATE INDEX geo_anchor_geometry_source_id_idx ON geo_anchor (geometry_source_id);
CREATE INDEX source_provenance_source_id_idx ON source_provenance (source_id);
CREATE INDEX source_provenance_snapshot_id_idx ON source_provenance (snapshot_id);
CREATE INDEX storage_provenance_source_id_idx ON storage_provenance (source_id);
CREATE INDEX storage_provenance_publish_run_id_idx ON storage_provenance (publish_run_id);
CREATE INDEX evidence_source_id_idx ON evidence (source_id);
CREATE INDEX evidence_snapshot_id_idx ON evidence (snapshot_id);
CREATE INDEX evidence_fact_location_geo_id_idx ON evidence (fact_location_geo_id);
CREATE INDEX content_entity_evidence_id_idx ON content_entity (evidence_id);
CREATE INDEX attention_object_publish_run_id_idx ON attention_object (publish_run_id);
CREATE INDEX attention_object_evidence_evidence_id_idx ON attention_object_evidence (evidence_id);
CREATE INDEX object_clock_source_id_idx ON object_clock (source_id);
CREATE INDEX phenomenon_case_geo_id_idx ON phenomenon_case (geo_id);
CREATE INDEX phenomenon_case_crop_term_id_idx ON phenomenon_case (crop_term_id);
CREATE INDEX phenomenon_case_issue_term_id_idx ON phenomenon_case (issue_term_id);
CREATE INDEX phenomenon_case_pairing_evidence_id_idx ON phenomenon_case (pairing_evidence_id);
CREATE INDEX regulatory_deadline_object_registration_id_idx ON regulatory_deadline_object (registration_id);
CREATE INDEX competitor_identity_chain_object_competitor_product_identity_id_idx ON competitor_identity_chain_object (competitor_product_identity_id);
CREATE INDEX longitudinal_field_pressure_object_series_id_idx ON longitudinal_field_pressure_object (series_id);
CREATE INDEX observation_geo_id_idx ON observation (geo_id);
CREATE INDEX observation_source_id_idx ON observation (source_id);
CREATE INDEX observation_evidence_id_idx ON observation (evidence_id);
CREATE INDEX territorial_observation_crop_term_id_idx ON territorial_observation (crop_term_id);
CREATE INDEX territorial_observation_issue_term_id_idx ON territorial_observation (issue_term_id);
CREATE INDEX territorial_observation_document_excerpt_evidence_id_idx ON territorial_observation (document_excerpt_evidence_id);
CREATE INDEX registration_holder_organization_id_idx ON registration (holder_organization_id);
CREATE INDEX registration_product_id_idx ON registration (product_id);
CREATE INDEX registration_source_id_idx ON registration (source_id);
CREATE INDEX registration_deadline_registration_id_idx ON registration_deadline (registration_id);
CREATE INDEX registration_deadline_evidence_id_idx ON registration_deadline (evidence_id);
CREATE INDEX registration_deadline_source_id_idx ON registration_deadline (source_id);
CREATE INDEX product_active_ingredient_term_id_idx ON product (active_ingredient_term_id);
CREATE INDEX trademark_record_holder_organization_id_idx ON trademark_record (holder_organization_id);
CREATE INDEX trademark_record_evidence_id_idx ON trademark_record (evidence_id);
CREATE INDEX competitor_product_identity_competitor_organization_id_idx ON competitor_product_identity (competitor_organization_id);
CREATE INDEX competitor_product_identity_normalized_product_id_idx ON competitor_product_identity (normalized_product_id);
CREATE INDEX competitor_product_identity_trademark_id_idx ON competitor_product_identity (trademark_id);
CREATE INDEX competitor_product_identity_local_registration_id_idx ON competitor_product_identity (local_registration_id);
CREATE INDEX competitor_product_identity_observed_paid_activity_id_idx ON competitor_product_identity (observed_paid_activity_id);
CREATE INDEX observed_paid_activity_observation_id_idx ON observed_paid_activity (observation_id);
CREATE INDEX company_local_account_organization_id_idx ON company_local_account (organization_id);
CREATE INDEX company_public_content_account_id_idx ON company_public_content (account_id);
CREATE INDEX company_public_content_evidence_id_idx ON company_public_content (evidence_id);
CREATE INDEX field_pressure_series_crop_term_id_idx ON field_pressure_series (crop_term_id);
CREATE INDEX field_pressure_series_issue_term_id_idx ON field_pressure_series (issue_term_id);
CREATE INDEX field_pressure_series_source_id_idx ON field_pressure_series (source_id);
CREATE INDEX field_pressure_reading_series_id_idx ON field_pressure_reading (series_id);
CREATE INDEX field_pressure_reading_source_id_idx ON field_pressure_reading (source_id);
CREATE INDEX field_pressure_reading_observation_id_idx ON field_pressure_reading (observation_id);
CREATE INDEX scientific_person_organization_id_idx ON scientific_person (organization_id);
CREATE INDEX scientific_person_source_id_idx ON scientific_person (source_id);
CREATE INDEX scientific_publication_source_id_idx ON scientific_publication (source_id);
CREATE INDEX scientific_publication_evidence_id_idx ON scientific_publication (evidence_id);
CREATE INDEX publication_author_person_id_idx ON publication_author (person_id);
CREATE INDEX issue_expertise_crop_term_id_idx ON issue_expertise (crop_term_id);
CREATE INDEX issue_expertise_issue_term_id_idx ON issue_expertise (issue_term_id);
CREATE INDEX issue_expertise_evidence_id_idx ON issue_expertise (evidence_id);
CREATE INDEX person_creator_source_id_idx ON person_creator (source_id);
CREATE INDEX farm_business_entity_organization_id_idx ON farm_business_entity (organization_id);
CREATE INDEX farm_business_entity_source_id_idx ON farm_business_entity (source_id);
CREATE INDEX creator_content_profile_person_id_idx ON creator_content_profile (person_id);
CREATE INDEX creator_content_profile_business_id_idx ON creator_content_profile (business_id);
CREATE INDEX creator_content_profile_source_id_idx ON creator_content_profile (source_id);
CREATE INDEX field_voice_observation_profile_id_idx ON field_voice_observation (profile_id);
CREATE INDEX field_voice_observation_crop_mentioned_term_id_idx ON field_voice_observation (crop_mentioned_term_id);
CREATE INDEX field_voice_observation_issue_mentioned_term_id_idx ON field_voice_observation (issue_mentioned_term_id);
CREATE INDEX field_voice_observation_content_entity_id_idx ON field_voice_observation (content_entity_id);
CREATE INDEX local_adama_portfolio_context_crop_term_id_idx ON local_adama_portfolio_context (crop_term_id);
CREATE INDEX local_adama_portfolio_context_issue_term_id_idx ON local_adama_portfolio_context (issue_term_id);
CREATE INDEX local_adama_portfolio_context_source_id_idx ON local_adama_portfolio_context (source_id);
CREATE INDEX portfolio_product_ref_product_id_idx ON portfolio_product_ref (product_id);
CREATE INDEX portfolio_product_ref_registration_id_idx ON portfolio_product_ref (registration_id);
CREATE INDEX convergence_proposition_attention_object_id_idx ON convergence_proposition (attention_object_id);
CREATE INDEX convergence_leg_proposition_id_idx ON convergence_leg (proposition_id);
CREATE INDEX convergence_leg_evidence_id_idx ON convergence_leg (evidence_id);
CREATE INDEX convergence_leg_source_id_idx ON convergence_leg (source_id);
CREATE INDEX convergence_leg_depends_on_leg_id_idx ON convergence_leg (depends_on_leg_id);
CREATE INDEX dependency_edge_evidence_id_idx ON dependency_edge (evidence_id);
CREATE INDEX object_relation_to_object_id_idx ON object_relation (to_object_id);
CREATE INDEX object_relation_evidence_id_idx ON object_relation (evidence_id);
CREATE INDEX object_event_attention_object_id_idx ON object_event (attention_object_id);
CREATE INDEX object_event_source_id_idx ON object_event (source_id);
CREATE INDEX object_event_observation_id_idx ON object_event (observation_id);
CREATE INDEX action_evidence_evidence_id_idx ON action_evidence (evidence_id);
CREATE INDEX entry_path_event_attention_object_id_idx ON entry_path_event (attention_object_id);
CREATE INDEX entry_path_event_crop_term_id_idx ON entry_path_event (crop_term_id);
-- <<< FIM DO CORPO CANONICO <<<

COMMIT;
