-- SINTONIA EAME · EXECUCAO EM PARTES · BLOCO A DE 5 (JA APLICADO PELO CHATGPT — nao rodar de novo)
--
-- GERADO por scripts/supabase_execution_split.py. Nao editar a mao.
--
-- ORIGEM: supabase/migrations/0001_initial_canonical_schema.sql
-- SHA256 DA ORIGEM: 41ffeb52941718a34a01135e2f76bc4611a2978e049175f90cf4014117e335ec
-- ALVO: xhqebdweltytnghiavew (eame-sintonia-dev)
--
-- PARA QUE: schema sintonia, os 27 vocabularios fechados e as quatro primeiras tabelas. Fica separado para poder ser CONFERIDO em vez de reexecutado.
--
-- ORDEM: rode a, b, c, d, e nesta ordem. Cada um abre e fecha a propria
-- transacao: se um falhar, ele volta inteiro e os anteriores ficam de pe.
--
-- O QUE E ANDAIME AQUI: este cabecalho, o BEGIN/COMMIT abaixo e o
-- SET search_path. Foram acrescentados porque cada arquivo roda numa
-- sessao propria. Tudo o que esta entre as duas marcas e fatia LITERAL
-- do arquivo canonico, byte a byte, e a prova de reconstrucao confere.
--
-- ATENCAO: este bloco JA FOI APLICADO. Ele esta aqui para ser
-- CONFERIDO, nao reexecutado. Rodar de novo levanta "already exists"
-- no CREATE SCHEMA e nos 27 CREATE TYPE — o Postgres recusa e a
-- transacao volta inteira, entao nao estraga nada.
-- Ainda assim: nao rode. A conferencia certa e o inventario 0000.

BEGIN;
SET search_path TO sintonia, public;

-- >>> CORPO CANONICO — FATIA LITERAL DE 0001, NAO EDITAR >>>
-- SINTONIA EAME · SCHEMA CANONICO · RASCUNHO
--
-- GERADO por scripts/supabase_schema.py a partir de
-- data/supabase/SUPABASE-CANONICAL-SCHEMA.json.
-- NAO EDITAR A MAO: a proxima geracao apaga a edicao.
--
-- MIGRATION_APPLIED = NO. Este arquivo NAO foi aplicado em producao e exige
-- revisao humana antes de qualquer `supabase db push`.
--
-- Regra que atravessa tudo: os tipos persistidos sao os CANONICOS do
-- FINAL-HOSE-MAP. Os aliases do casco index (11) vivem em sintonia.ui_alias e
-- nunca substituem o tipo.


CREATE SCHEMA IF NOT EXISTS sintonia;
SET search_path TO sintonia, public;


-- ── VOCABULARIOS FECHADOS ─────────────────────────────────────────────
CREATE TYPE object_type AS ENUM ('PHENOMENON_CASE', 'REGULATORY_DEADLINE', 'COMPETITOR_IDENTITY_CHAIN', 'LONGITUDINAL_FIELD_PRESSURE');
CREATE TYPE attention_state AS ENUM ('ATTENTION_READY', 'ATTENTION_CANDIDATE_TEST', 'VALID_EVIDENCE_NOT_ATTENTION_READY', 'NEEDS_EVIDENCE', 'FORMING', 'WATCH', 'FUTURE', 'ARCHIVED');
CREATE TYPE field_state AS ENUM ('PROVED', 'NOT_PROVED', 'NOT_MEASURED', 'NOT_READY', 'NOT_APPLICABLE');
CREATE TYPE language_code AS ENUM ('pt', 'en', 'es', 'fr', 'it', 'MULTILINGUAL', 'UNKNOWN');
CREATE TYPE geo_resolution AS ENUM ('COUNTRY', 'NUTS2', 'PROVINCE', 'MUNICIPALITY', 'LOCALITY_TEXT', 'POINT', 'NOT_KNOWN');
CREATE TYPE action_type AS ENUM ('BUSINESS_DECISION', 'SYSTEM_DECISION', 'INVESTIGATION');
CREATE TYPE convergence_kind AS ENUM ('PHENOMENON_CONVERGENCE', 'IDENTITY_CONVERGENCE', 'CONTEXTUAL_ALIGNMENT');
CREATE TYPE dependency_type AS ENUM ('SOURCE_DEPENDENCY', 'OBSERVATION_DEPENDENCY', 'ENTITY_DEPENDENCY', 'DERIVATION_DEPENDENCY', 'SEMANTIC_DEPENDENCY', 'INDEPENDENT_SOURCE');
CREATE TYPE signal_family AS ENUM ('TERRITORIAL', 'SCIENCE_RESEARCHER', 'NATIONAL_REGISTRY', 'TRADEMARK', 'META_PAID_ADS', 'CREATOR', 'FIELD_HISTORICAL', 'COMPETITOR_PUBLIC_COMM');
CREATE TYPE independence_state AS ENUM ('INDEPENDENT', 'DEPENDENT', 'NOT_PROVED');
CREATE TYPE evidence_level AS ENUM ('PROVED', 'MEASURED', 'PARTIAL', 'NOT_PROVED', 'NOT_MEASURED', 'NOT_KNOWN');
CREATE TYPE source_backend AS ENUM ('GITHUB', 'SUPABASE');
CREATE TYPE data_state AS ENUM ('READY', 'EMPTY_VALID', 'NOT_STARTED', 'NOT_AVAILABLE', 'BLOCKED');
CREATE TYPE pipeline_state AS ENUM ('NOT_STARTED', 'RUNNING', 'PARTIAL', 'COMPLETE', 'BLOCKED', 'FAILED_CLOSED');
CREATE TYPE content_collection_stage AS ENUM ('NOT_STARTED', 'RUNNING', 'PARTIAL', 'COMPLETE');
CREATE TYPE entry_path AS ENUM ('FROM_ATTENTION_OBJECT', 'FROM_CROP_REGION_SEARCH');
CREATE TYPE event_type AS ENUM ('FIRST_OBSERVED', 'SOURCE_PUBLICATION', 'FIRST_CAPTURE', 'NEW_EVIDENCE', 'SIGNAL_FAMILY_ADDED', 'STATE_CHANGE', 'TRIGGER', 'ATTENTION_CANDIDATE', 'ATTENTION_READY', 'ACTION_REVIEW', 'ARCHIVED', 'GAP');
CREATE TYPE time_resolution AS ENUM ('EXACT_DATE', 'WEEK', 'MONTH', 'PHENOLOGICAL_STAGE', 'SEASON', 'NOT_KNOWN');
CREATE TYPE clock_kind AS ENUM ('OBSERVATION_TIME', 'STAGE_AT_OBSERVATION', 'CURRENT_CROP_STAGE', 'LABEL_USE_STAGE', 'APPLICATION_WINDOW', 'REGULATORY_DEADLINE', 'FUTURE_SEASON_WINDOW');
CREATE TYPE ontology_term_kind AS ENUM ('CROP', 'ISSUE', 'ACTIVE_INGREDIENT', 'PRODUCT_CATEGORY');
CREATE TYPE creator_entity_kind AS ENUM ('PERSON_CREATOR', 'FARM_BUSINESS_ENTITY');
CREATE TYPE department AS ENUM ('MARKET_DEVELOPMENT', 'REGULATORY', 'PORTFOLIO', 'TECHNICAL_SCIENCE', 'MARKETING', 'COMMERCIAL', 'SUPPLY');
CREATE TYPE adama_line AS ENUM ('DISEASE_CONTROL', 'WEED_CONTROL', 'PEST_CONTROL', 'CROP_ENHANCEMENT', 'NOT_APPLICABLE');
CREATE TYPE gdpr_state AS ENUM ('NOT_STARTED', 'IN_REVIEW', 'CLEARED', 'RESTRICTED');
CREATE TYPE publish_status AS ENUM ('PENDING', 'VALIDATING', 'SHADOW_OK', 'PUBLISHED', 'FAILED_CLOSED');
CREATE TYPE observation_kind AS ENUM ('TERRITORIAL_OBSERVATION', 'FIELD_VOICE_OBSERVATION', 'OBSERVED_PAID_ACTIVITY', 'FIELD_PRESSURE_READING');
CREATE TYPE translation_quality AS ENUM ('MACHINE_UNREVIEWED', 'MACHINE_REVIEWED', 'HUMAN', 'NOT_KNOWN');

-- NAO existe enum para request_state (UNWIRED, LOADING, ERROR_FAIL_CLOSED):
-- Sao estados da CAMADA DE APLICACAO, nao verdades do negocio. Guardar LOADING numa tabela transformaria uma requisicao em andamento em fato sobre o mundo. UNWIRED e propriedade da ligacao, nao do dado: uma linha existir ja prova que a rota foi ligada.

-- ── TABELAS ───────────────────────────────────────────────────────────

-- Termo canonico neutro de idioma: cultura, problema, ingrediente ativo.
-- POR QUE: O contrato multilingue exige ID neutro separado do rotulo. Codigo EPPO e o identificador; o nome em cada lingua vive em ontology_term_label. Sem esta tabela, 'mildiu' e 'downy mildew' viram dois problemas diferentes.
-- HOSE_ID: H9 · CANONICAL_PAYLOAD_TYPE: ONTOLOGY_TERM
CREATE TABLE ontology_term (
  term_id text NOT NULL,
  term_kind ontology_term_kind NOT NULL,
  eppo_code text,  -- identificador neutro quando existe
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT ontology_term_pk PRIMARY KEY (term_id),
  CONSTRAINT ontology_term_uq1 UNIQUE (term_kind, eppo_code)
);

-- Rotulo do termo em cada idioma.
-- POR QUE: Separa ID de rotulo. Cinco idiomas nao criam cinco termos.
CREATE TABLE ontology_term_label (
  term_id text NOT NULL,
  language language_code NOT NULL,
  label text NOT NULL,
  CONSTRAINT ontology_term_label_pk PRIMARY KEY (term_id, language)
);

-- Ancoragem geografica com resolucao declarada.
-- POR QUE: LOCALITY_TEXT nunca vira POINT. A geometria so existe quando a fonte a deu; a resolucao viaja junto e o consumidor decide se pode desenhar.
CREATE TABLE geo_anchor (
  geo_id text NOT NULL,
  country char(2) NOT NULL,
  region text,
  locality_text text,  -- como a fonte escreveu; nunca geocodificado
  geometry jsonb,  -- GeoJSON; NULL quando nao ha
  geo_resolution geo_resolution NOT NULL DEFAULT 'NOT_KNOWN',
  geometry_source_id text,  -- geometria exige origem explicita
  CONSTRAINT geo_anchor_pk PRIMARY KEY (geo_id),
  CONSTRAINT geo_anchor_point_exige_geometria CHECK ((geo_resolution <> 'POINT') OR (geometry IS NOT NULL)),
  CONSTRAINT geo_anchor_geometria_exige_origem CHECK ((geometry IS NULL) OR (geometry_source_id IS NOT NULL)),
  CONSTRAINT geo_anchor_locality_text_nao_e_point CHECK ((geo_resolution <> 'LOCALITY_TEXT') OR (geometry IS NULL))
);

-- Fonte externa, com papel e escopo declarados.
-- POR QUE: SOURCE_ID e a ancora de toda proveniencia de evidencia. Uma fonte existe antes de qualquer captura.
CREATE TABLE source (
  source_id text NOT NULL,
  source_name text NOT NULL,
  source_role text NOT NULL,
  entity_kind text,
  country char(2),  -- pais da PUBLICACAO, nunca do fato
  access_state text NOT NULL,
  cadence text,
  geographic_scope text,
  crop_scope text,
  is_prospective boolean,
  collection_state pipeline_state NOT NULL DEFAULT 'NOT_STARTED',
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT source_pk PRIMARY KEY (source_id)
);
-- <<< FIM DO CORPO CANONICO <<<

COMMIT;
