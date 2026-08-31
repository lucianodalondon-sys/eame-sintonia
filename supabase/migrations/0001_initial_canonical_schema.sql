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

BEGIN;

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

-- Uma captura datada de uma fonte, com hash.
-- POR QUE: Sem snapshot, 'a fonte diz X' nao e reproduzivel. E e ele que permite medir latencia com DUAS capturas — com uma so, latencia e NOT_MEASURED.
CREATE TABLE source_snapshot (
  snapshot_id text NOT NULL,
  source_id text NOT NULL,
  captured_at timestamptz NOT NULL,
  source_published_at date,
  content_hash text,
  artifact_ref text,
  artifact_language language_code NOT NULL DEFAULT 'UNKNOWN',
  CONSTRAINT source_snapshot_pk PRIMARY KEY (snapshot_id),
  CONSTRAINT source_snapshot_uq1 UNIQUE (source_id, captured_at, content_hash)
);

-- Os cinco relogios da fonte, cada um separado.
-- POR QUE: Idade da observacao NAO e latencia de pipeline. Fundir os dois num numero foi um erro que ja apareceu no produto.
CREATE TABLE source_clock (
  source_id text NOT NULL,
  source_status text NOT NULL,
  latest_source_publication date,
  latest_capture timestamptz,
  observation_age_days integer,  -- idade do FATO
  pipeline_latency_state field_state NOT NULL DEFAULT 'NOT_MEASURED',
  pipeline_latency_seconds integer,
  CONSTRAINT source_clock_pk PRIMARY KEY (source_id),
  CONSTRAINT source_clock_latencia_sem_medicao_e_nula CHECK ((pipeline_latency_state = 'PROVED') OR (pipeline_latency_seconds IS NULL))
);

-- De onde a EVIDENCIA veio no mundo — a origem externa real.
-- POR QUE: Separada de storage_provenance de proposito. Quando um dado ja estiver no Supabase, SOURCE_BACKEND = SUPABASE descreveria a ENTREGA e apagaria a origem externa. As duas nunca se substituem.
CREATE TABLE source_provenance (
  source_provenance_id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  evidence_id text NOT NULL,
  source_id text NOT NULL,
  snapshot_id text,
  original_ref text,  -- URL ou identificador na origem
  as_of_date date,
  CONSTRAINT source_provenance_pk PRIMARY KEY (source_provenance_id),
  CONSTRAINT source_provenance_uq1 UNIQUE (evidence_id, source_id, snapshot_id)
);

-- De onde a linha foi LIDA ou ENTREGUE — GitHub ou Supabase.
-- POR QUE: Envelope de transporte. O V8 renderiza os dois com o mesmo componente; o discriminador e SOURCE_BACKEND e nenhuma coluna do outro backend e preenchida junto.
CREATE TABLE storage_provenance (
  storage_provenance_id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  subject_kind text NOT NULL,  -- attention_object | evidence | observation | series | ...
  subject_id text NOT NULL,
  source_backend source_backend NOT NULL,
  repository text,
  path text,
  commit_sha char(40),
  content_hash text,
  db_schema text,
  table_or_view text,
  primary_key text,
  snapshot_id text,
  captured_at timestamptz,
  source_id text,
  as_of_date date,
  publish_run_id text,
  CONSTRAINT storage_provenance_pk PRIMARY KEY (storage_provenance_id),
  CONSTRAINT storage_provenance_github_exige_commit_e_caminho CHECK ((source_backend <> 'GITHUB') OR (repository IS NOT NULL AND path IS NOT NULL AND commit_sha IS NOT NULL)),
  CONSTRAINT storage_provenance_supabase_exige_tabela_e_chave CHECK ((source_backend <> 'SUPABASE') OR (db_schema IS NOT NULL AND table_or_view IS NOT NULL AND primary_key IS NOT NULL)),
  CONSTRAINT storage_provenance_backends_nao_se_misturam CHECK (NOT (repository IS NOT NULL AND table_or_view IS NOT NULL))
);

-- Uma evidencia, reutilizavel por muitos consumidores.
-- POR QUE: Uma evidencia sustenta objeto, perna de convergencia, base de acao, evento de timeline e relacao. Duplicar fisicamente por uso criaria cinco verdades que divergem.
CREATE TABLE evidence (
  evidence_id text NOT NULL,
  source_id text NOT NULL,
  snapshot_id text,
  source_location_country char(2),  -- pais da PUBLICACAO
  fact_location_geo_id text,  -- pais e regiao do FATO — nunca o mesmo campo
  source_published_at date,
  captured_at timestamptz,
  evidence_level evidence_level NOT NULL DEFAULT 'NOT_KNOWN',
  original_text text,  -- na lingua da fonte, sem edicao
  source_language language_code NOT NULL DEFAULT 'UNKNOWN',
  document_excerpt text,  -- H1 preserva 3.000 caracteres, nao o corpo inteiro
  passage_start integer,
  passage_end integer,
  source_url text,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT evidence_pk PRIMARY KEY (evidence_id),
  CONSTRAINT evidence_offsets_andam_em_par CHECK ((passage_start IS NULL) = (passage_end IS NULL))
);

-- Entidade textual canonica: o texto existe uma vez, com sua lingua de origem.
-- POR QUE: H9. A verdade textual e o ORIGINAL. Traducao e representacao, e vive em outra tabela.
-- HOSE_ID: H9 · CANONICAL_PAYLOAD_TYPE: CONTENT_ENTITY
CREATE TABLE content_entity (
  canonical_entity_id text NOT NULL,
  entity_kind text NOT NULL,  -- EVIDENCE_QUOTE | OBJECT_TITLE | ACTION_TEXT | ...
  source_language language_code NOT NULL DEFAULT 'UNKNOWN',
  original_text text NOT NULL,
  evidence_id text,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT content_entity_pk PRIMARY KEY (canonical_entity_id)
);

-- Traducao de um content_entity, com proveniencia propria.
-- POR QUE: Traducao NUNCA substitui o original. Ter tabela separada torna impossivel sobrescrever o original por acidente de UPDATE.
-- HOSE_ID: H9 · CANONICAL_PAYLOAD_TYPE: CONTENT_TRANSLATION
CREATE TABLE content_translation (
  canonical_entity_id text NOT NULL,
  translation_language language_code NOT NULL,
  translated_text text NOT NULL,
  translation_provenance text NOT NULL,  -- quem traduziu
  translation_quality translation_quality NOT NULL DEFAULT 'NOT_KNOWN',
  translated_at timestamptz,
  source_text_hash text,  -- hash do original no momento da traducao — muda o original, a traducao fica obsoleta
  CONSTRAINT content_translation_pk PRIMARY KEY (canonical_entity_id, translation_language),
  CONSTRAINT content_translation_traducao_nao_e_na_lingua_de_origem CHECK (translation_language NOT IN ('MULTILINGUAL','UNKNOWN'))
);

-- A unidade superior do produto. Identidade neutra de idioma.
-- POR QUE: UM objeto, varias representacoes. Nunca AO-001-PT e AO-001-EN. Campos especificos de cada tipo ficam em tabelas filhas — quatro tipos numa mega-tabela produziriam colunas nulas que parecem lacunas.
CREATE TABLE attention_object (
  attention_object_id text NOT NULL,  -- NEUTRO DE IDIOMA
  object_type object_type NOT NULL,
  country char(2) NOT NULL,
  attention_state attention_state NOT NULL,
  decision_question text,
  decision_owner department,
  adama_line adama_line NOT NULL DEFAULT 'NOT_APPLICABLE',
  blocker_text text,
  as_of_date date,
  last_evidence_at date,
  publish_run_id text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT attention_object_pk PRIMARY KEY (attention_object_id)
);

-- O texto do objeto num idioma. Nunca a verdade estruturada.
-- POR QUE: Separa FATO ESTRUTURADO de REPRESENTACAO LINGUISTICA. Datas, estados, ids e relacoes existem uma vez; o texto existe por idioma.
CREATE TABLE attention_object_representation (
  attention_object_id text NOT NULL,
  language language_code NOT NULL,
  title text NOT NULL,
  summary text,
  interpretation text,
  attention_reason text,
  what_we_know text,
  what_we_dont_know text,  -- secao obrigatoria no dossie; nunca suprimida na exportacao
  is_translation boolean NOT NULL DEFAULT false,
  translation_provenance text,
  translation_quality translation_quality,
  CONSTRAINT attention_object_representation_pk PRIMARY KEY (attention_object_id, language),
  CONSTRAINT attention_object_representation_traducao_declara_proveniencia CHECK ((is_translation = false) OR (translation_provenance IS NOT NULL))
);

-- Os cinco requisitos do portao, um por linha, reproduziveis.
-- POR QUE: ATTENTION_READY nao pode ser um booleano escrito a mao. Guardando os cinco componentes, o estado e recalculavel e auditavel — e a fila vazia consegue dizer QUAL portao segurou cada objeto.
CREATE TABLE attention_readiness (
  attention_object_id text NOT NULL,
  requirement text NOT NULL,  -- VALID_EVIDENCE | OBJECT_SPECIFIC_TRIGGER | TIME_RELEVANCE | DECISION_QUESTION | DECISION_OWNER
  state field_state NOT NULL,
  reason text,
  evaluated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT attention_readiness_pk PRIMARY KEY (attention_object_id, requirement),
  CONSTRAINT attention_readiness_requisito_do_vocabulario CHECK (requirement IN ('VALID_EVIDENCE','OBJECT_SPECIFIC_TRIGGER','TIME_RELEVANCE','DECISION_QUESTION','DECISION_OWNER'))
);

-- Quais evidencias sustentam o objeto.
-- POR QUE: N:N. A mesma evidencia serve a mais de um objeto sem ser copiada.
CREATE TABLE attention_object_evidence (
  attention_object_id text NOT NULL,
  evidence_id text NOT NULL,
  role text,
  CONSTRAINT attention_object_evidence_pk PRIMARY KEY (attention_object_id, evidence_id)
);

-- O que ainda nao sabemos, por objeto.
-- POR QUE: Estado transversal, nunca superficie. Guardado como lista para o bloco obrigatorio do dossie.
CREATE TABLE attention_object_unknown (
  attention_object_id text NOT NULL,
  unknown_key text NOT NULL,
  state field_state NOT NULL,
  note text,
  CONSTRAINT attention_object_unknown_pk PRIMARY KEY (attention_object_id, unknown_key)
);

-- Os sete relogios do objeto, cada um com sua resolucao.
-- POR QUE: Os sete NUNCA se fundem, e a interface nao desenha precisao que o dado nao tem. Guardar cada um com time_resolution propria e o que impede a fabricacao de calendario.
CREATE TABLE object_clock (
  attention_object_id text NOT NULL,
  clock_kind clock_kind NOT NULL,
  resolution time_resolution NOT NULL DEFAULT 'NOT_KNOWN',
  value_date date,
  value_text text,  -- BBCH, estacao, faixa
  state field_state NOT NULL DEFAULT 'NOT_MEASURED',
  source_id text,
  CONSTRAINT object_clock_pk PRIMARY KEY (attention_object_id, clock_kind),
  CONSTRAINT object_clock_sem_resolucao_sem_data CHECK ((resolution <> 'NOT_KNOWN') OR (value_date IS NULL))
);

-- Tabela filha do tipo PHENOMENON_CASE.
-- POR QUE: REQUIRED = COUNTRY, REGION, CROP, ISSUE, OBSERVATION_TIME. Sao NOT NULL aqui e nao existem nos outros tipos.
CREATE TABLE phenomenon_case (
  attention_object_id text NOT NULL,
  geo_id text NOT NULL,
  crop_term_id text NOT NULL,
  issue_term_id text NOT NULL,
  crop_issue_pairing_state field_state NOT NULL DEFAULT 'NOT_PROVED',
  pairing_evidence_id text,  -- a passagem onde cultura e problema coocorrem
  CONSTRAINT phenomenon_case_pk PRIMARY KEY (attention_object_id),
  CONSTRAINT phenomenon_case_par_provado_exige_a_passagem CHECK ((crop_issue_pairing_state <> 'PROVED') OR (pairing_evidence_id IS NOT NULL))
);

-- Tabela filha do tipo REGULATORY_DEADLINE.
-- POR QUE: REQUIRED = COUNTRY, REGISTRATION_ID, PRODUCT, DEADLINE, STATUS_AS_DECLARED_BY_SOURCE. CROP, ISSUE e REGION sao NOT_APPLICABLE e por isso nao existem como coluna — ausencia de coluna e mais forte que coluna nula.
CREATE TABLE regulatory_deadline_object (
  attention_object_id text NOT NULL,
  registration_id text NOT NULL,
  deadline_date date NOT NULL,
  deadline_kind text NOT NULL,
  status_as_declared_by_source text NOT NULL,  -- COMO A FONTE DECLARA — nunca reinterpretado
  label_effect_state field_state NOT NULL DEFAULT 'NOT_PROVED',  -- expiracao NAO e retirada
  max_authorized_action action_type NOT NULL DEFAULT 'INVESTIGATION',
  CONSTRAINT regulatory_deadline_object_pk PRIMARY KEY (attention_object_id),
  CONSTRAINT regulatory_deadline_object_prazo_nao_autoriza_decisao_de_negocio CHECK (max_authorized_action <> 'BUSINESS_DECISION')
);

-- Tabela filha do tipo COMPETITOR_IDENTITY_CHAIN.
-- POR QUE: REQUIRED = COMPETITOR, COUNTRY, PRODUCT_NORMALIZED, HOLDER_AGREEMENT. CROP e ISSUE sao NOT_APPLICABLE.
CREATE TABLE competitor_identity_chain_object (
  attention_object_id text NOT NULL,
  competitor_product_identity_id text NOT NULL,
  CONSTRAINT competitor_identity_chain_object_pk PRIMARY KEY (attention_object_id)
);

-- Tabela filha do tipo LONGITUDINAL_FIELD_PRESSURE.
-- POR QUE: REQUIRED inclui SERIES, BASELINE e COHORT_CONTROL — todos vivem na serie, referenciada aqui.
CREATE TABLE longitudinal_field_pressure_object (
  attention_object_id text NOT NULL,
  series_id text NOT NULL,
  CONSTRAINT longitudinal_field_pressure_object_pk PRIMARY KEY (attention_object_id)
);

-- Supertipo de tudo que foi OBSERVADO, com data e ancora.
-- POR QUE: Territorial, voz de campo, atividade paga e leitura de serie sao todas observacoes. Ter o supertipo permite que evento de timeline e perna de convergencia apontem para 'uma observacao' sem saber o subtipo.
CREATE TABLE observation (
  observation_id text NOT NULL,
  observation_kind observation_kind NOT NULL,
  observed_at date,
  observed_at_resolution time_resolution NOT NULL DEFAULT 'NOT_KNOWN',
  geo_id text,
  source_id text NOT NULL,
  evidence_id text,
  signal_family signal_family NOT NULL,
  CONSTRAINT observation_pk PRIMARY KEY (observation_id)
);

-- H1 · payload canonico TERRITORIAL_OBSERVATION.
-- POR QUE: Nome canonico do FINAL-HOSE-MAP. O casco chama de TERRITORIAL_ATTENTION_OBJECT; esse alias fica em UI_ALIAS_MAP e nao entra aqui.
-- HOSE_ID: H1 · CANONICAL_PAYLOAD_TYPE: TERRITORIAL_OBSERVATION
CREATE TABLE territorial_observation (
  observation_id text NOT NULL,
  country_of_fact char(2) NOT NULL,
  region_of_fact text,
  crop_term_id text,
  issue_term_id text,
  issue_evidence_passage text,
  published_at date,
  phenology_at_observation text,
  document_excerpt_evidence_id text,
  multi_bulletin_document boolean NOT NULL DEFAULT false,
  CONSTRAINT territorial_observation_pk PRIMARY KEY (observation_id)
);

-- Registro nacional de produto, de qualquer titular.
-- POR QUE: H2 carrega o prazo de UM registro, de QUALQUER titular — inclusive de concorrente. Manter registro separado de portfolio ADAMA e o que impede o produto de dizer que a ADAMA tem resposta porque um registro qualquer tem prazo.
CREATE TABLE registration (
  registration_id text NOT NULL,
  country char(2) NOT NULL,
  registration_number text NOT NULL,
  holder_organization_id text,
  product_id text,
  status_as_declared_by_source text,
  source_id text NOT NULL,
  CONSTRAINT registration_pk PRIMARY KEY (registration_id),
  CONSTRAINT registration_uq1 UNIQUE (country, registration_number)
);

-- H2 · payload canonico REGISTRATION_DEADLINE.
-- POR QUE: Nome canonico. O casco usa REGULATORY_DEADLINE, que e o OBJECT_TYPE — sao coisas diferentes e nao podem colidir no banco.
-- HOSE_ID: H2 · CANONICAL_PAYLOAD_TYPE: REGISTRATION_DEADLINE
CREATE TABLE registration_deadline (
  deadline_id text NOT NULL,
  registration_id text NOT NULL,
  deadline_date date NOT NULL,
  deadline_kind text NOT NULL,
  status_as_declared_by_source text NOT NULL,
  expiry_is_withdrawal boolean NOT NULL DEFAULT false,  -- guard: expiracao NAO e retirada. Sempre false ate prova em contrario da fonte.
  evidence_id text NOT NULL,
  source_id text NOT NULL,
  as_of_date date,
  CONSTRAINT registration_deadline_pk PRIMARY KEY (deadline_id),
  CONSTRAINT registration_deadline_expiry_nao_e_withdrawal CHECK (expiry_is_withdrawal = false)
);

-- Produto comercial normalizado.
-- POR QUE: Nome comercial != titular != fabricante. Normalizar aqui e o que permite comparar mercados.
CREATE TABLE product (
  product_id text NOT NULL,
  normalized_name text NOT NULL,
  active_ingredient_term_id text,
  is_adama boolean NOT NULL DEFAULT false,
  CONSTRAINT product_pk PRIMARY KEY (product_id)
);

-- Empresa, titular ou grupo.
-- POR QUE: Titular != grupo != fabricante. O portao URBOLE compara nome + grupo + pais, e precisa dos tres separados.
CREATE TABLE organization (
  organization_id text NOT NULL,
  name text NOT NULL,
  group_name text,
  country char(2),
  CONSTRAINT organization_pk PRIMARY KEY (organization_id)
);

-- Registro de marca.
-- POR QUE: Primeiro elo da cadeia competitiva, com escritorio e data de deposito proprios.
CREATE TABLE trademark_record (
  trademark_id text NOT NULL,
  trademark_name text NOT NULL,
  office text,
  filed_at date,
  status text,
  holder_organization_id text,
  evidence_id text,
  CONSTRAINT trademark_record_pk PRIMARY KEY (trademark_id)
);

-- H3 · payload canonico COMPETITOR_PRODUCT_IDENTITY. Liga marca, registro local e atividade observada.
-- POR QUE: Nome canonico. O casco usa COMPETITOR_IDENTITY_CHAIN, que e o OBJECT_TYPE. Os tres elos existirem nao valida a cadeia: quem valida e AGREEMENT_STATE.
-- HOSE_ID: H3 · CANONICAL_PAYLOAD_TYPE: COMPETITOR_PRODUCT_IDENTITY
CREATE TABLE competitor_product_identity (
  identity_id text NOT NULL,
  country char(2) NOT NULL,
  competitor_organization_id text NOT NULL,
  normalized_product_id text,
  trademark_id text,
  local_registration_id text,
  observed_paid_activity_id text,
  agreement_state field_state NOT NULL DEFAULT 'NOT_PROVED',  -- produto x titular x pais
  urbole_guard_result text NOT NULL DEFAULT 'NOT_RUN',  -- portao sem resultado registrado e portao sem dentes
  urbole_guard_ran_at timestamptz,
  CONSTRAINT competitor_product_identity_pk PRIMARY KEY (identity_id),
  CONSTRAINT competitor_product_identity_concordancia_exige_portao_exercido CHECK ((agreement_state <> 'PROVED') OR (urbole_guard_result <> 'NOT_RUN'))
);

-- H4 · payload canonico OBSERVED_PAID_ACTIVITY. Evidencia, nunca objeto proprio.
-- POR QUE: Nome canonico. E o terceiro elo da cadeia e nada mais: DO_NOT_BUILD = META_DASHBOARD. Os sete 'nao pode afirmar' viajam com a linha.
-- HOSE_ID: H4 · CANONICAL_PAYLOAD_TYPE: OBSERVED_PAID_ACTIVITY
CREATE TABLE observed_paid_activity (
  paid_activity_id text NOT NULL,
  observation_id text NOT NULL,
  platform text NOT NULL,
  page_id text NOT NULL,
  page_name text,
  page_country_scope char(2),  -- NAO e o pais de entrega do anuncio
  ad_delivery_country_state field_state NOT NULL DEFAULT 'NOT_MEASURED',
  observed_at timestamptz NOT NULL,
  observation_window_seconds integer,
  ad_card_count integer,  -- AD_CARD != AD
  cannot_claim_list text[] NOT NULL,
  operational_temporal_signal_state field_state NOT NULL DEFAULT 'NOT_PROVED',
  CONSTRAINT observed_paid_activity_pk PRIMARY KEY (paid_activity_id),
  CONSTRAINT observed_paid_activity_sempre_carrega_os_nao_pode_afirmar CHECK (array_length(cannot_claim_list, 1) >= 6)
);

-- H8 · payload canonico COMPANY_LOCAL_ACCOUNT. Existe antes da coleta.
-- POR QUE: Nome canonico (o casco usa COMPANY_PUBLIC_ACCOUNT). A conta identificada precisa existir com CONTENT_COLLECTION_STAGE = NOT_STARTED, para que zero conteudo nunca seja lido como silencio da empresa.
-- HOSE_ID: H8 · CANONICAL_PAYLOAD_TYPE: COMPANY_LOCAL_ACCOUNT
CREATE TABLE company_local_account (
  account_id text NOT NULL,
  organization_id text NOT NULL,
  platform text NOT NULL,
  country_scope char(2),
  page_role text,  -- COUNTRY_SCOPE != PAGE_ROLE
  account_url text,
  content_collection_stage content_collection_stage NOT NULL DEFAULT 'NOT_STARTED',
  route_state text NOT NULL DEFAULT 'DECLARED',
  identity_resolved_at timestamptz,
  last_identity_check_at timestamptz,
  CONSTRAINT company_local_account_pk PRIMARY KEY (account_id)
);

-- Conteudo publico da conta — tabela prevista, vazia hoje.
-- POR QUE: Prever a entidade sem exigir coleta agora. Existir vazia com a conta em NOT_STARTED e o que permite dizer 'a rota existe e nao correu' em vez de 'nao ha comunicacao'.
-- HOSE_ID: H8 · CANONICAL_PAYLOAD_TYPE: —
CREATE TABLE company_public_content (
  content_id text NOT NULL,
  account_id text NOT NULL,
  published_at timestamptz,
  original_text text,
  source_language language_code NOT NULL DEFAULT 'UNKNOWN',
  evidence_id text,
  CONSTRAINT company_public_content_pk PRIMARY KEY (content_id)
);

-- H5 · payload canonico FIELD_PRESSURE_SERIES.
-- POR QUE: Nome canonico (o casco usa LONGITUDINAL_FIELD_SERIES). Serie separada das leituras: sem isso, baseline e coorte virariam colunas repetidas em cada ponto.
-- HOSE_ID: H5 · CANONICAL_PAYLOAD_TYPE: FIELD_PRESSURE_SERIES
CREATE TABLE field_pressure_series (
  series_id text NOT NULL,
  country char(2) NOT NULL,
  region text,
  crop_term_id text,
  issue_term_id text,
  season_range text,
  baseline_kind text,
  baseline_state field_state NOT NULL DEFAULT 'NOT_MEASURED',
  cohort_state field_state NOT NULL DEFAULT 'NOT_PROVED',
  backtest_state field_state NOT NULL DEFAULT 'NOT_READY',
  false_positive_rate numeric,
  lead_time_days integer,
  independence_from_territorial_state field_state NOT NULL DEFAULT 'NOT_PROVED',  -- SAME_PUBLISHER != INDEPENDENT_OBSERVATION
  source_id text NOT NULL,
  CONSTRAINT field_pressure_series_pk PRIMARY KEY (series_id)
);

-- Uma leitura da serie. Nunca media sem N.
-- POR QUE: O n viaja com o valor, no mesmo registro. Guardar media agregada sem n foi o erro que o repositorio ja documentou.
-- HOSE_ID: H5 · CANONICAL_PAYLOAD_TYPE: —
CREATE TABLE field_pressure_reading (
  reading_id text NOT NULL,
  series_id text NOT NULL,
  observed_at date,
  season text,
  value numeric NOT NULL,
  n integer NOT NULL,  -- obrigatorio: media nunca viaja sem o n
  unit text NOT NULL,
  province text,
  source_id text NOT NULL,
  observation_id text,
  CONSTRAINT field_pressure_reading_pk PRIMARY KEY (reading_id),
  CONSTRAINT field_pressure_reading_n_positivo CHECK (n > 0)
);

-- Pessoa fisica identificada, com estado GDPR.
-- POR QUE: Supertipo de SCIENTIFIC_PERSON e PERSON_CREATOR. Uma pessoa pode ser as duas coisas, e o tratamento GDPR e da PESSOA, nao do papel.
CREATE TABLE person (
  person_id text NOT NULL,
  display_name text,
  country char(2),
  identity_proved boolean NOT NULL DEFAULT false,
  gdpr_treatment_state gdpr_state NOT NULL DEFAULT 'NOT_STARTED',
  orcid text,
  CONSTRAINT person_pk PRIMARY KEY (person_id)
);

-- H7 · payload canonico SCIENTIFIC_PERSON.
-- POR QUE: Nome canonico (o casco usa ISSUE_EXPERT). Pessoa NAO e publicacao — e ISSUE_EXPERT sugere que a expertise e atributo da pessoa, quando e relacao.
-- HOSE_ID: H7 · CANONICAL_PAYLOAD_TYPE: SCIENTIFIC_PERSON
CREATE TABLE scientific_person (
  person_id text NOT NULL,
  organization_id text,
  relation_to_issue_as_declared text,
  source_id text NOT NULL,
  CONSTRAINT scientific_person_pk PRIMARY KEY (person_id)
);

-- Subreceptor · a PUBLICACAO, nao o autor.
-- POR QUE: SCIENTIFIC_PERSON != SCIENTIFIC_PUBLICATION. Sem esta tabela, a camada Ciencia de um caso seria preenchida com pessoas, e o produto passaria a dizer que ha ciencia porque encontrou um pesquisador.
-- PARENT_HOSE_ID: H7 · CANONICAL_PAYLOAD_TYPE: SCIENTIFIC_PUBLICATION
CREATE TABLE scientific_publication (
  publication_id text NOT NULL,
  title text NOT NULL,
  published_at date,
  venue text,
  peer_reviewed_state field_state NOT NULL DEFAULT 'NOT_MEASURED',
  source_language language_code NOT NULL DEFAULT 'UNKNOWN',
  doi text,
  openalex_id text,
  abstract_excerpt text,
  source_id text NOT NULL,
  evidence_id text,
  CONSTRAINT scientific_publication_pk PRIMARY KEY (publication_id)
);

-- N:N entre publicacao e pessoa.
-- POR QUE: Uma pessoa tem muitas publicacoes; uma publicacao tem muitos autores. Nenhum dos dois lados e atributo do outro.
CREATE TABLE publication_author (
  publication_id text NOT NULL,
  person_id text NOT NULL,
  author_position integer,
  CONSTRAINT publication_author_pk PRIMARY KEY (publication_id, person_id)
);

-- Expertise como RELACAO: pessoa x cultura x problema x evidencia x estado.
-- POR QUE: ISSUE_EXPERTISE_PROVED nao e atributo universal da pessoa. Alguem pode ser autoridade em repilo na oliveira e nao ser em mildio na vinha. Modelar como relacao e o que faz o portao ter dentes — e o que impede contagem de artigos virar autoridade.
-- PARENT_HOSE_ID: H7 · CANONICAL_PAYLOAD_TYPE: —
CREATE TABLE issue_expertise (
  person_id text NOT NULL,
  crop_term_id text NOT NULL,
  issue_term_id text NOT NULL,
  issue_expertise_state field_state NOT NULL DEFAULT 'NOT_PROVED',
  evidence_id text,
  evaluated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT issue_expertise_pk PRIMARY KEY (person_id, crop_term_id, issue_term_id),
  CONSTRAINT issue_expertise_expertise_provada_exige_evidencia CHECK ((issue_expertise_state <> 'PROVED') OR (evidence_id IS NOT NULL))
);

-- H6 · payload canonico PERSON_CREATOR.
-- POR QUE: Nome canonico. PESSOA que cria conteudo publico. Tabela separada de farm_business_entity porque somar as duas num numero chamado CREATORS_READY e proibido — e a inflacao medida foi de 2,6x.
-- HOSE_ID: H6 · CANONICAL_PAYLOAD_TYPE: PERSON_CREATOR
CREATE TABLE person_creator (
  person_id text NOT NULL,
  relation_to_crop_region field_state NOT NULL DEFAULT 'NOT_PROVED',
  source_id text NOT NULL,
  CONSTRAINT person_creator_pk PRIMARY KEY (person_id)
);

-- H6 · payload canonico FARM_BUSINESS_ENTITY.
-- POR QUE: Nome canonico (o casco abrevia para FARM_BUSINESS). NEGOCIO agricola ou parceiro — nao e pessoa e nao entra em tratamento GDPR de pessoa fisica.
-- HOSE_ID: H6 · CANONICAL_PAYLOAD_TYPE: FARM_BUSINESS_ENTITY
CREATE TABLE farm_business_entity (
  business_id text NOT NULL,
  organization_id text,
  display_name text,
  country char(2),
  relation_to_crop_region field_state NOT NULL DEFAULT 'NOT_PROVED',
  source_id text NOT NULL,
  CONSTRAINT farm_business_entity_pk PRIMARY KEY (business_id)
);

-- H6 · payload canonico CREATOR_CONTENT_PROFILE.
-- POR QUE: Nome canonico — nao aparece em lugar nenhum do casco index (11). Perfil de canal de uma entidade: uma entidade pode ter varios canais, e canal nao e pessoa.
-- HOSE_ID: H6 · CANONICAL_PAYLOAD_TYPE: CREATOR_CONTENT_PROFILE
CREATE TABLE creator_content_profile (
  profile_id text NOT NULL,
  entity_kind creator_entity_kind NOT NULL,
  person_id text,
  business_id text,
  platform text NOT NULL,
  channel_ref text,
  last_observed_at timestamptz,
  source_id text NOT NULL,
  CONSTRAINT creator_content_profile_pk PRIMARY KEY (profile_id),
  CONSTRAINT creator_content_profile_perfil_pertence_a_exatamente_uma_entidade CHECK ((person_id IS NOT NULL)::int + (business_id IS NOT NULL)::int = 1),
  CONSTRAINT creator_content_profile_kind_bate_com_a_entidade CHECK ((entity_kind = 'PERSON_CREATOR' AND person_id IS NOT NULL) OR (entity_kind = 'FARM_BUSINESS_ENTITY' AND business_id IS NOT NULL))
);

-- Subreceptor · o que a voz de campo DISSE.
-- POR QUE: Entidade != observacao. Sem esta tabela, voz de campo e uma lista de nomes — e nome nao e sinal.
-- PARENT_HOSE_ID: H6 · CANONICAL_PAYLOAD_TYPE: FIELD_VOICE_OBSERVATION
CREATE TABLE field_voice_observation (
  observation_id text NOT NULL,
  profile_id text,
  entity_kind creator_entity_kind NOT NULL,
  platform text NOT NULL,
  country char(2),
  crop_mentioned_term_id text,
  issue_mentioned_term_id text,
  region_mentioned text,
  content_entity_id text,  -- o texto original vive em content_entity
  relation_to_issue_state field_state NOT NULL DEFAULT 'NOT_PROVED',
  gdpr_treatment_state gdpr_state NOT NULL DEFAULT 'NOT_STARTED',
  CONSTRAINT field_voice_observation_pk PRIMARY KEY (observation_id),
  CONSTRAINT field_voice_observation_pessoa_identificada_exige_gdpr_tratado CHECK ((entity_kind <> 'PERSON_CREATOR') OR (gdpr_treatment_state <> 'NOT_STARTED'))
);

-- Subreceptor · a ADAMA tem resposta registrada para este alvo neste pais?
-- POR QUE: REGISTRATION_DEADLINE != LOCAL_ADAMA_PORTFOLIO_CONTEXT. Sem esta tabela, alguem liga H2 aqui e o portal passa a dizer que a ADAMA tem produto porque um registro de qualquer titular tem prazo. Portfolio e CONTEXTO, nunca evidencia do fenomeno.
-- PARENT_HOSE_ID: H2 · CANONICAL_PAYLOAD_TYPE: LOCAL_ADAMA_PORTFOLIO_CONTEXT
CREATE TABLE local_adama_portfolio_context (
  context_id text NOT NULL,
  country char(2) NOT NULL,
  crop_term_id text,
  issue_term_id text,
  registered_response_state field_state NOT NULL DEFAULT 'NOT_PROVED',
  label_authorizes_target_state field_state NOT NULL DEFAULT 'NOT_PROVED',
  source_id text NOT NULL,
  is_context_not_evidence boolean NOT NULL DEFAULT true,
  CONSTRAINT local_adama_portfolio_context_pk PRIMARY KEY (context_id),
  CONSTRAINT local_adama_portfolio_context_portfolio_e_sempre_contexto CHECK (is_context_not_evidence = true)
);

-- Produtos ADAMA e registros que sustentam o contexto de portfolio.
-- POR QUE: N:N. Um contexto pode ser sustentado por varios produtos e registros; nenhum deles vira coluna repetida.
-- PARENT_HOSE_ID: H2 · CANONICAL_PAYLOAD_TYPE: —
CREATE TABLE portfolio_product_ref (
  context_id text NOT NULL,
  product_id text,
  registration_id text,
  CONSTRAINT portfolio_product_ref_pk PRIMARY KEY (context_id, product_id, registration_id)
);

-- A proposicao unica que as pernas sustentam.
-- POR QUE: CONVERGENCE_REQUIRES = SAME_PROPOSITION + INDEPENDENT_EVIDENCE. Sem a proposicao como entidade, duas evidencias sobre assuntos parecidos viram convergencia.
-- INDEPENDENT_FAMILY_COUNT nao existe como coluna. E derivado na view v_convergence_state. Um contador manual pode divergir das pernas — e foi assim que cinco das seis convergencias da V1 viraram uma so.
CREATE TABLE convergence_proposition (
  proposition_id text NOT NULL,
  attention_object_id text NOT NULL,
  proposition_text text NOT NULL,
  convergence_kind convergence_kind NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT convergence_proposition_pk PRIMARY KEY (proposition_id)
);

-- Uma perna da convergencia, com sua independencia tipada.
-- POR QUE: DEPENDENCY_RELATION e o campo que impede dupla contagem. Sem ele, a perna Meta da cadeia e o anuncio da Meta contariam como duas familias.
CREATE TABLE convergence_leg (
  leg_id text NOT NULL,
  proposition_id text NOT NULL,
  signal_family signal_family NOT NULL,
  evidence_id text NOT NULL,
  source_id text NOT NULL,
  observed_at date,
  independence_state independence_state NOT NULL DEFAULT 'NOT_PROVED',
  dependency_type dependency_type NOT NULL DEFAULT 'INDEPENDENT_SOURCE',
  depends_on_leg_id text,
  dependency_note text,
  CONSTRAINT convergence_leg_pk PRIMARY KEY (leg_id),
  CONSTRAINT convergence_leg_dependente_declara_o_tipo_e_o_alvo CHECK ((independence_state <> 'DEPENDENT') OR (dependency_type <> 'INDEPENDENT_SOURCE' AND depends_on_leg_id IS NOT NULL)),
  CONSTRAINT convergence_leg_independente_nao_tem_alvo CHECK ((independence_state <> 'INDEPENDENT') OR (depends_on_leg_id IS NULL))
);

-- O grafo de dependencia tipado, entre quaisquer dois sinais.
-- POR QUE: As 17 relacoes medidas do refresh precisam existir fora da convergencia de um objeto: H3 depende de H4 por DERIVATION_DEPENDENCY e H5 depende de H1 por SOURCE_DEPENDENCY sao propriedades do SISTEMA, nao de um caso.
CREATE TABLE dependency_edge (
  edge_id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  from_kind text NOT NULL,  -- SIGNAL_FAMILY | HOSE | EVIDENCE | OBSERVATION | ENTITY
  from_id text NOT NULL,
  to_kind text NOT NULL,
  to_id text NOT NULL,
  dependency_type dependency_type NOT NULL,
  why text NOT NULL,
  evidence_id text,
  CONSTRAINT dependency_edge_pk PRIMARY KEY (edge_id),
  CONSTRAINT dependency_edge_uq1 UNIQUE (from_kind, from_id, to_kind, to_id, dependency_type)
);

-- Cruzamentos entre objetos de atencao.
-- POR QUE: O bloco 'o que liga a outros objetos' precisa de aresta propria, com tipo — nunca inferida por semelhanca de texto.
CREATE TABLE object_relation (
  relation_id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  from_object_id text NOT NULL,
  to_object_id text NOT NULL,
  relation_kind text NOT NULL,
  dependency_type dependency_type,
  evidence_id text,
  CONSTRAINT object_relation_pk PRIMARY KEY (relation_id),
  CONSTRAINT object_relation_uq1 UNIQUE (from_object_id, to_object_id, relation_kind),
  CONSTRAINT object_relation_objeto_nao_se_relaciona_consigo CHECK (from_object_id <> to_object_id)
);

-- A timeline do objeto. STATE_BEFORE e STATE_AFTER separados.
-- POR QUE: Guardar 'FORMING -> ATTENTION_CANDIDATE_TEST' como string impede filtrar, agregar e reconstruir. A seta e apresentacao e vive numa view.
CREATE TABLE object_event (
  event_id text NOT NULL,
  attention_object_id text NOT NULL,
  event_type event_type NOT NULL,
  event_at timestamptz,  -- NULL quando o evento e um vazio temporal
  event_at_resolution time_resolution NOT NULL DEFAULT 'NOT_KNOWN',
  source_id text,
  observation_id text,
  state_before attention_state,
  state_after attention_state,
  what_changed text NOT NULL,
  signal_family_added signal_family,
  gap_reason text,
  trigger_id text,
  CONSTRAINT object_event_pk PRIMARY KEY (event_id),
  CONSTRAINT object_event_mudanca_de_estado_exige_os_dois_estados CHECK ((event_type <> 'STATE_CHANGE') OR (state_after IS NOT NULL)),
  CONSTRAINT object_event_vazio_temporal_declara_o_motivo CHECK ((event_type <> 'GAP') OR (gap_reason IS NOT NULL)),
  CONSTRAINT object_event_sem_data_sem_precisao CHECK ((event_at IS NOT NULL) OR (event_at_resolution = 'NOT_KNOWN'))
);

-- Uma acao por area, com tipo canonico.
-- POR QUE: ACTION_TYPE persistido e BUSINESS_DECISION / SYSTEM_DECISION / INVESTIGATION. BUSINESS e SYSTEM sao rotulos de tela e ficam em ui_alias.
CREATE TABLE action (
  action_id text NOT NULL,
  attention_object_id text NOT NULL,
  department department NOT NULL,
  action_type action_type NOT NULL,
  action_state field_state NOT NULL DEFAULT 'NOT_READY',
  action_text text NOT NULL,
  why_text text,
  time_horizon text,
  is_central_area boolean NOT NULL DEFAULT false,
  regional_owner text,
  is_publishable boolean NOT NULL DEFAULT false,  -- derivado pelo publisher: BUSINESS_DECISION sem base de evidencia nao publica
  CONSTRAINT action_pk PRIMARY KEY (action_id),
  CONSTRAINT action_uq1 UNIQUE (attention_object_id, department, action_type)
);

-- EVIDENCE_BASIS como relacao N:N.
-- POR QUE: Uma acao pode se apoiar em varias evidencias e uma evidencia sustenta varias acoes. A regra 'BUSINESS_DECISION sem base nao publica' se verifica contando linhas aqui — nao confiando num campo.
CREATE TABLE action_evidence (
  action_id text NOT NULL,
  evidence_id text NOT NULL,
  CONSTRAINT action_evidence_pk PRIMARY KEY (action_id, evidence_id)
);

-- Telemetria minima de como o usuario chegou a capability Creator.
-- POR QUE: A arbitragem decidiu que Creator vira ferramenta com DADO DE USO, nao com estetica. Sem esta tabela a decisao nunca pode ser tomada. Guarda so a rota e o recorte — sem PII, sem identificador de usuario.
-- PARENT_HOSE_ID: H6 · CANONICAL_PAYLOAD_TYPE: —
-- PRIVACIDADE: sem user_id, sem sessao, sem IP. So a rota, o recorte e a hora.
CREATE TABLE entry_path_event (
  event_id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  entry_path entry_path NOT NULL,
  attention_object_id text,
  crop_term_id text,
  region text,
  country char(2),
  occurred_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT entry_path_event_pk PRIMARY KEY (event_id),
  CONSTRAINT entry_path_event_rota_do_objeto_exige_objeto CHECK ((entry_path <> 'FROM_ATTENTION_OBJECT') OR (attention_object_id IS NOT NULL))
);

-- Uma execucao do publisher, com versao e freezes.
-- POR QUE: Responde 'qual versao do pipeline colocou este objeto aqui, e com quais freezes'. Sem isso, o Supabase vira um estado sem historia.
CREATE TABLE publish_run (
  publish_run_id text NOT NULL,
  pipeline_version text NOT NULL,
  schema_version text NOT NULL,
  published_at timestamptz NOT NULL DEFAULT now(),
  status publish_status NOT NULL DEFAULT 'PENDING',
  shadow_validation_passed boolean NOT NULL DEFAULT false,
  failed_reason text,
  CONSTRAINT publish_run_pk PRIMARY KEY (publish_run_id),
  CONSTRAINT publish_run_publicado_exige_sombra_aprovada CHECK ((status <> 'PUBLISHED') OR (shadow_validation_passed = true))
);

-- Os commits congelados que alimentaram a execucao.
-- POR QUE: Uma execucao pode ler varios freezes. Guardar N:N torna a pergunta 'de que commit veio esta linha' respondivel.
CREATE TABLE publish_run_freeze (
  publish_run_id text NOT NULL,
  repository text NOT NULL,
  path text NOT NULL,
  commit_sha char(40) NOT NULL,
  hose_id text,
  CONSTRAINT publish_run_freeze_pk PRIMARY KEY (publish_run_id, repository, path, commit_sha)
);

-- O resultado da comparacao freeze x Supabase, familia por familia.
-- POR QUE: Contagem igual nao prova semantica igual. Cada verificacao fica registrada com o que se esperava e o que se achou.
CREATE TABLE shadow_validation (
  validation_id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  publish_run_id text NOT NULL,
  family text NOT NULL,
  check_name text NOT NULL,
  expected text,
  found text,
  passed boolean NOT NULL,
  checked_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT shadow_validation_pk PRIMARY KEY (validation_id),
  CONSTRAINT shadow_validation_uq1 UNIQUE (publish_run_id, family, check_name)
);

-- Os aliases de apresentacao, declarados e separados do tipo canonico.
-- POR QUE: O index (11) usa oito nomes divergentes. Guardar o mapa aqui e o que permite o adapter traduzir SEM que o alias vire tipo persistido — e o que torna a divergencia visivel em vez de silenciosa.
CREATE TABLE ui_alias (
  canonical_type text NOT NULL,
  hose_id text,
  ui_alias text,
  alias_source text NOT NULL DEFAULT 'INDEX11',
  note text,
  CONSTRAINT ui_alias_pk PRIMARY KEY (canonical_type)
);

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

-- ── ROW LEVEL SECURITY ────────────────────────────────────────────────
-- Ligado em TODAS as tabelas. Uma tabela sem RLS num projeto Supabase fica
-- legivel pela chave anonima: o padrao seguro e negar e abrir depois.
--
-- Papeis:
--   publisher_role  escreve inteligencia canonica (service role, so no backend)
--   portal_reader   le o que o pais dele autoriza
--   anon            nao le nada de inteligencia
--
-- SERVICE_ROLE_KEY NUNCA vai para o frontend. O portal fala com um servidor,
-- e o servidor fala com o Supabase.

-- Papeis. Criados se nao existirem; NOLOGIN porque quem loga e a aplicacao.
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'publisher_role')
  THEN CREATE ROLE publisher_role NOLOGIN; END IF;
END $$;  -- escreve inteligencia canonica; so no backend, nunca no browser
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'portal_reader')
  THEN CREATE ROLE portal_reader NOLOGIN; END IF;
END $$;  -- le o que o pais dele autoriza; escreve APENAS entry_path_event
--   anon: nao le nada de inteligencia (nenhuma policy = nao le nada)

-- Uma politica que lesse um claim de JWT com formato ainda nao decidido seria invencao. Esta funcao e exercitavel hoje via SET, nega por padrao, e troca de implementacao sem mexer nas politicas.
CREATE OR REPLACE FUNCTION allowed_countries() RETURNS char(2)[]
LANGUAGE sql STABLE AS $$
  -- Deny by default. Enquanto o modelo de identidade nao for decidido, a funcao
  -- devolve o que estiver na configuracao de sessao; sem configuracao, vazio.
  -- NAO inventa papel de usuario e NAO le claim de JWT que ainda nao existe.
  SELECT coalesce(
    string_to_array(nullif(current_setting('sintonia.countries', true), ''), ',')::char(2)[],
    ARRAY[]::char(2)[]
  );
$$;

-- RLS ligado em TODAS as tabelas. Sem policy, o acesso e negado:
-- o padrao seguro e negar e abrir depois.
ALTER TABLE ontology_term ENABLE ROW LEVEL SECURITY;
ALTER TABLE ontology_term_label ENABLE ROW LEVEL SECURITY;
ALTER TABLE geo_anchor ENABLE ROW LEVEL SECURITY;
ALTER TABLE source ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_snapshot ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_clock ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_provenance ENABLE ROW LEVEL SECURITY;
ALTER TABLE storage_provenance ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_entity ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_translation ENABLE ROW LEVEL SECURITY;
ALTER TABLE attention_object ENABLE ROW LEVEL SECURITY;
ALTER TABLE attention_object_representation ENABLE ROW LEVEL SECURITY;
ALTER TABLE attention_readiness ENABLE ROW LEVEL SECURITY;
ALTER TABLE attention_object_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE attention_object_unknown ENABLE ROW LEVEL SECURITY;
ALTER TABLE object_clock ENABLE ROW LEVEL SECURITY;
ALTER TABLE phenomenon_case ENABLE ROW LEVEL SECURITY;
ALTER TABLE regulatory_deadline_object ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_identity_chain_object ENABLE ROW LEVEL SECURITY;
ALTER TABLE longitudinal_field_pressure_object ENABLE ROW LEVEL SECURITY;
ALTER TABLE observation ENABLE ROW LEVEL SECURITY;
ALTER TABLE territorial_observation ENABLE ROW LEVEL SECURITY;
ALTER TABLE registration ENABLE ROW LEVEL SECURITY;
ALTER TABLE registration_deadline ENABLE ROW LEVEL SECURITY;
ALTER TABLE product ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization ENABLE ROW LEVEL SECURITY;
ALTER TABLE trademark_record ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_product_identity ENABLE ROW LEVEL SECURITY;
ALTER TABLE observed_paid_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_local_account ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_public_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE field_pressure_series ENABLE ROW LEVEL SECURITY;
ALTER TABLE field_pressure_reading ENABLE ROW LEVEL SECURITY;
ALTER TABLE person ENABLE ROW LEVEL SECURITY;
ALTER TABLE scientific_person ENABLE ROW LEVEL SECURITY;
ALTER TABLE scientific_publication ENABLE ROW LEVEL SECURITY;
ALTER TABLE publication_author ENABLE ROW LEVEL SECURITY;
ALTER TABLE issue_expertise ENABLE ROW LEVEL SECURITY;
ALTER TABLE person_creator ENABLE ROW LEVEL SECURITY;
ALTER TABLE farm_business_entity ENABLE ROW LEVEL SECURITY;
ALTER TABLE creator_content_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE field_voice_observation ENABLE ROW LEVEL SECURITY;
ALTER TABLE local_adama_portfolio_context ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_product_ref ENABLE ROW LEVEL SECURITY;
ALTER TABLE convergence_proposition ENABLE ROW LEVEL SECURITY;
ALTER TABLE convergence_leg ENABLE ROW LEVEL SECURITY;
ALTER TABLE dependency_edge ENABLE ROW LEVEL SECURITY;
ALTER TABLE object_relation ENABLE ROW LEVEL SECURITY;
ALTER TABLE object_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE action ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE entry_path_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE publish_run ENABLE ROW LEVEL SECURITY;
ALTER TABLE publish_run_freeze ENABLE ROW LEVEL SECURITY;
ALTER TABLE shadow_validation ENABLE ROW LEVEL SECURITY;
ALTER TABLE ui_alias ENABLE ROW LEVEL SECURITY;

-- 1 · o publisher escreve; e a unica coisa que escreve inteligencia
CREATE POLICY publisher_all ON ontology_term FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON ontology_term_label FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON geo_anchor FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON source FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON source_snapshot FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON source_clock FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON source_provenance FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON storage_provenance FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON evidence FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON content_entity FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON content_translation FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON attention_object FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON attention_object_representation FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON attention_readiness FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON attention_object_evidence FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON attention_object_unknown FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON object_clock FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON phenomenon_case FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON regulatory_deadline_object FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON competitor_identity_chain_object FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON longitudinal_field_pressure_object FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON observation FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON territorial_observation FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON registration FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON registration_deadline FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON product FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON organization FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON trademark_record FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON competitor_product_identity FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON observed_paid_activity FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON company_local_account FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON company_public_content FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON field_pressure_series FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON field_pressure_reading FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON person FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON scientific_person FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON scientific_publication FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON publication_author FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON issue_expertise FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON person_creator FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON farm_business_entity FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON creator_content_profile FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON field_voice_observation FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON local_adama_portfolio_context FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON portfolio_product_ref FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON convergence_proposition FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON convergence_leg FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON dependency_edge FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON object_relation FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON object_event FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON action FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON action_evidence FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON entry_path_event FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON publish_run FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON publish_run_freeze FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON shadow_validation FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON ui_alias FOR ALL TO publisher_role USING (true) WITH CHECK (true);

-- 2 · o portal le so o pais autorizado. Sem SET, allowed_countries()
--     devolve vazio e nenhuma linha passa.
CREATE POLICY portal_read_country ON geo_anchor FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON source FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON attention_object FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON registration FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON organization FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON competitor_product_identity FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON field_pressure_series FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON person FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON farm_business_entity FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON field_voice_observation FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON local_adama_portfolio_context FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON entry_path_event FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));

-- 3 · a tabela filha herda o pais da raiz, sem repetir a coluna
CREATE POLICY portal_read_child ON attention_object_representation FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = attention_object_representation.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON attention_readiness FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = attention_readiness.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON attention_object_evidence FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = attention_object_evidence.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON attention_object_unknown FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = attention_object_unknown.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON object_clock FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = object_clock.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON phenomenon_case FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = phenomenon_case.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON regulatory_deadline_object FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = regulatory_deadline_object.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON competitor_identity_chain_object FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = competitor_identity_chain_object.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON longitudinal_field_pressure_object FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = longitudinal_field_pressure_object.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON convergence_proposition FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = convergence_proposition.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON object_event FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = object_event.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON action FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = action.attention_object_id AND o.country = ANY (allowed_countries())));

-- 4 · a UNICA escrita do portal, e nao e inteligencia: rota de entrada
CREATE POLICY portal_write_telemetry ON entry_path_event FOR INSERT TO portal_reader WITH CHECK (true);

-- O que NAO entra agora, por depender de decisao de autenticacao:
--   como o pais do usuario chega ate o banco (claim de JWT? tabela de membership?)
--   multi-tenant: a coluna tenant_id nao entra antes de existir cliente multiplo
--   auditoria de acesso: quem leu o que — entra quando houver usuario real
-- SERVICE_ROLE_KEY nunca vai para o frontend. O navegador fala com um servidor; o servidor fala com o Supabase.

-- ── VIEWS DE LEITURA ──────────────────────────────────────────────────
-- Projecoes. A fonte de verdade continua normalizada: nenhuma view
-- redefine regra, e nenhuma duplica logica que ja existe em outra.
-- Onde pode faltar linha o join e LEFT: view nenhuma esconde
-- NOT_PROVED ou UNKNOWN sumindo com a linha.

-- v_convergence_state · Deriva INDEPENDENT_FAMILY_COUNT e CONVERGENCE_STATE das pernas.
-- POR QUE: A contagem NUNCA e coluna. Contar familias distintas entre pernas INDEPENDENT e o que produz SINGLE_SIGNAL com duas pernas quando uma depende da outra.
-- LE: convergence_proposition, convergence_leg
-- DERIVA: independent_family_count, convergence_state
CREATE OR REPLACE VIEW v_convergence_state AS
SELECT p.proposition_id,
       p.attention_object_id,
       p.proposition_text,
       p.convergence_kind,
       count(DISTINCT l.signal_family)
         FILTER (WHERE l.independence_state = 'INDEPENDENT')          AS independent_family_count,
       count(*) FILTER (WHERE l.independence_state = 'DEPENDENT')     AS dependent_leg_count,
       count(*)                                                       AS leg_count,
       CASE WHEN count(DISTINCT l.signal_family)
                   FILTER (WHERE l.independence_state = 'INDEPENDENT') >= 2
            THEN 'MULTI_SIGNAL' ELSE 'SINGLE_SIGNAL' END              AS convergence_state
  FROM convergence_proposition p
  LEFT JOIN convergence_leg l ON l.proposition_id = p.proposition_id
 GROUP BY p.proposition_id, p.attention_object_id, p.proposition_text, p.convergence_kind;

-- v_attention_readiness · Recalcula ATTENTION_READY a partir dos cinco requisitos.
-- POR QUE: O estado publicado tem de ser reproduzivel. Se algum requisito nao estiver PROVED, o objeto nao e READY — e a view diz qual portao segurou.
-- LE: attention_object, attention_readiness
-- DERIVA: computed_is_ready, blocking_requirements
CREATE OR REPLACE VIEW v_attention_readiness AS
WITH gate AS (
  SELECT o.attention_object_id,
         r.requirement,
         coalesce(r.state, 'NOT_MEASURED'::field_state) AS state
    FROM attention_object o
    CROSS JOIN unnest(ARRAY['VALID_EVIDENCE','OBJECT_SPECIFIC_TRIGGER','TIME_RELEVANCE',
                            'DECISION_QUESTION','DECISION_OWNER']) AS req(requirement)
    LEFT JOIN attention_readiness r
           ON r.attention_object_id = o.attention_object_id
          AND r.requirement = req.requirement
)
SELECT attention_object_id,
       count(*) FILTER (WHERE state = 'PROVED')                       AS proved_gates,
       count(*)                                                       AS total_gates,
       bool_and(state = 'PROVED')                                     AS computed_is_ready,
       array_agg(requirement ORDER BY requirement)
         FILTER (WHERE state <> 'PROVED')                             AS blocking_requirements
  FROM gate
 GROUP BY attention_object_id;

-- v_attention_feed · Fila de atencao por pais, com o motivo quando vazia.
-- LE: attention_object, v_attention_readiness, attention_object_representation
CREATE OR REPLACE VIEW v_attention_feed AS
SELECT o.attention_object_id,
       o.object_type,
       o.country,
       o.attention_state,
       o.decision_question,
       o.decision_owner,
       o.adama_line,
       o.blocker_text,
       o.as_of_date,
       o.last_evidence_at,
       rd.computed_is_ready,
       rd.blocking_requirements,
       rp.language,
       rp.title,
       rp.summary,
       rp.attention_reason
  FROM attention_object o
  LEFT JOIN v_attention_readiness rd ON rd.attention_object_id = o.attention_object_id
  LEFT JOIN attention_object_representation rp ON rp.attention_object_id = o.attention_object_id
 WHERE o.attention_state = 'ATTENTION_READY';

-- v_radar · Cards do radar: tipo, pais, estado, bloqueador, ultima evidencia.
-- LE: attention_object, attention_object_representation, attention_readiness
CREATE OR REPLACE VIEW v_radar AS
SELECT o.attention_object_id,
       o.object_type,
       o.country,
       o.attention_state,
       o.adama_line,
       o.blocker_text,
       o.last_evidence_at,
       rd.blocking_requirements,
       rp.language,
       rp.title
  FROM attention_object o
  LEFT JOIN v_attention_readiness rd ON rd.attention_object_id = o.attention_object_id
  LEFT JOIN attention_object_representation rp ON rp.attention_object_id = o.attention_object_id;

-- v_object_detail · Objeto + tabela filha do tipo + relogios + desconhecidos.
-- LE: attention_object, phenomenon_case, regulatory_deadline_object, competitor_identity_chain_object, longitudinal_field_pressure_object, object_clock, attention_object_unknown
CREATE OR REPLACE VIEW v_object_detail AS
SELECT o.attention_object_id,
       o.object_type,
       o.country,
       o.attention_state,
       o.decision_question,
       o.decision_owner,
       o.as_of_date,
       pc.geo_id                          AS case_geo_id,
       pc.crop_term_id                    AS case_crop_term_id,
       pc.issue_term_id                   AS case_issue_term_id,
       pc.crop_issue_pairing_state,
       rdo.registration_id                AS deadline_registration_id,
       rdo.deadline_date,
       rdo.deadline_kind,
       rdo.status_as_declared_by_source,
       rdo.label_effect_state,
       rdo.max_authorized_action,
       cic.competitor_product_identity_id,
       lfp.series_id
  FROM attention_object o
  LEFT JOIN phenomenon_case pc                    ON pc.attention_object_id  = o.attention_object_id
  LEFT JOIN regulatory_deadline_object rdo        ON rdo.attention_object_id = o.attention_object_id
  LEFT JOIN competitor_identity_chain_object cic  ON cic.attention_object_id = o.attention_object_id
  LEFT JOIN longitudinal_field_pressure_object lfp ON lfp.attention_object_id = o.attention_object_id;

-- v_evidence_drawer · Evidencia + proveniencia dos dois backends + original e traducao separados.
-- POR QUE: O mesmo formato para GITHUB e SUPABASE. A UI nao sabe de qual veio.
-- LE: evidence, source, source_provenance, storage_provenance, content_entity, content_translation
CREATE OR REPLACE VIEW v_evidence_drawer AS
SELECT e.evidence_id,
       e.source_id,
       s.source_name,
       s.source_role,
       e.source_location_country,
       g.country                     AS fact_location_country,
       g.region                      AS fact_location_region,
       e.source_published_at,
       e.captured_at,
       e.evidence_level,
       e.original_text,
       e.source_language,
       e.document_excerpt,
       e.passage_start,
       e.passage_end,
       e.source_url,
       sp.snapshot_id                AS source_snapshot_id,
       sp.original_ref,
       stp.source_backend,
       stp.repository, stp.path, stp.commit_sha, stp.content_hash,
       stp.db_schema, stp.table_or_view, stp.primary_key, stp.snapshot_id AS storage_snapshot_id,
       stp.as_of_date,
       ce.canonical_entity_id,
       ce.original_text              AS canonical_original_text,
       ce.source_language            AS canonical_source_language
  FROM evidence e
  LEFT JOIN source s              ON s.source_id = e.source_id
  LEFT JOIN geo_anchor g          ON g.geo_id = e.fact_location_geo_id
  LEFT JOIN source_provenance sp  ON sp.evidence_id = e.evidence_id
  LEFT JOIN storage_provenance stp ON stp.subject_kind = 'evidence'
                                  AND stp.subject_id = e.evidence_id
  LEFT JOIN content_entity ce     ON ce.evidence_id = e.evidence_id;

-- v_crop_map_point · Pontos do mapa, ja filtrados por resolucao desenhavel.
-- POR QUE: A view devolve is_drawable derivado de GEO_RESOLUTION = POINT com geometria. O cliente nao decide isso sozinho.
-- LE: attention_object, geo_anchor, phenomenon_case
-- DERIVA: is_drawable, undrawable_reason
CREATE OR REPLACE VIEW v_crop_map_point AS
SELECT o.attention_object_id           AS object_id,
       o.object_type,
       o.attention_state,
       g.country,
       g.region,
       g.locality_text,
       g.geometry,
       g.geo_resolution,
       pc.crop_term_id                 AS crop,
       (g.geo_resolution = 'POINT' AND g.geometry IS NOT NULL) AS is_drawable,
       CASE WHEN g.geo_resolution = 'POINT' AND g.geometry IS NOT NULL THEN NULL
            WHEN g.geo_resolution = 'NOT_KNOWN' THEN 'GEO_RESOLUTION_NOT_KNOWN'
            WHEN g.geometry IS NULL              THEN 'NO_GEOMETRY'
            ELSE 'RESOLUTION_' || g.geo_resolution::text END      AS undrawable_reason
  FROM attention_object o
  LEFT JOIN phenomenon_case pc ON pc.attention_object_id = o.attention_object_id
  LEFT JOIN geo_anchor g       ON g.geo_id = pc.geo_id;

-- v_object_timeline · Timeline com a seta de apresentacao montada aqui.
-- POR QUE: STATE_BEFORE -> STATE_AFTER e string SO nesta view. No banco os dois sao colunas.
-- LE: object_event
-- DERIVA: state_transition_label
CREATE OR REPLACE VIEW v_object_timeline AS
SELECT ev.event_id,
       ev.attention_object_id,
       ev.event_type,
       ev.event_at,
       ev.event_at_resolution,
       ev.source_id,
       ev.observation_id,
       ev.state_before,
       ev.state_after,
       ev.what_changed,
       ev.signal_family_added,
       ev.gap_reason,
       ev.trigger_id,
       CASE WHEN ev.state_before IS NULL AND ev.state_after IS NULL THEN NULL
            ELSE coalesce(ev.state_before::text, '—') || ' → '
                 || coalesce(ev.state_after::text, '—') END AS state_transition_label
  FROM object_event ev;

-- v_action_map · Acoes com contagem de base de evidencia.
-- POR QUE: Deriva is_defensible: BUSINESS_DECISION com zero linhas em action_evidence nao e defensavel.
-- LE: action, action_evidence
-- DERIVA: evidence_basis_count, is_defensible
CREATE OR REPLACE VIEW v_action_map AS
SELECT a.action_id,
       a.attention_object_id,
       a.department,
       a.action_type,
       a.action_state,
       a.action_text,
       a.why_text,
       a.time_horizon,
       a.is_central_area,
       a.regional_owner,
       count(ae.evidence_id)                                   AS evidence_basis_count,
       array_remove(array_agg(ae.evidence_id), NULL)           AS evidence_basis,
       (a.action_type <> 'BUSINESS_DECISION'
        OR count(ae.evidence_id) > 0)                          AS is_defensible
  FROM action a
  LEFT JOIN action_evidence ae ON ae.action_id = a.action_id
 GROUP BY a.action_id, a.attention_object_id, a.department, a.action_type,
          a.action_state, a.action_text, a.why_text, a.time_horizon,
          a.is_central_area, a.regional_owner;

-- v_eame_cross_market · Camada regional: so as dimensoes declaradas comparaveis.
-- POR QUE: Cruzar so onde ha comparabilidade declarada. Uma view que juntasse tudo fabricaria uniformidade.
-- LE: attention_object, object_relation, field_pressure_series
CREATE OR REPLACE VIEW v_eame_cross_market AS
SELECT r.relation_id,
       r.relation_kind,
       r.dependency_type,
       fo.attention_object_id  AS from_object_id,
       fo.country              AS from_country,
       fo.object_type          AS from_object_type,
       fo.attention_state      AS from_state,
       to_.attention_object_id AS to_object_id,
       to_.country             AS to_country,
       to_.object_type         AS to_object_type,
       to_.attention_state     AS to_state,
       r.evidence_id
  FROM object_relation r
  JOIN attention_object fo  ON fo.attention_object_id = r.from_object_id
  JOIN attention_object to_ ON to_.attention_object_id = r.to_object_id
 WHERE fo.country <> to_.country;

-- v_source_status · Os cinco relogios por fonte, sem agregacao.
-- LE: source, source_clock, source_snapshot
CREATE OR REPLACE VIEW v_source_status AS
SELECT s.source_id,
       s.source_name,
       s.source_role,
       s.country                      AS publication_country,
       s.access_state,
       s.collection_state,
       c.source_status,
       c.latest_source_publication,
       c.latest_capture,
       c.observation_age_days,
       c.pipeline_latency_state,
       c.pipeline_latency_seconds,
       count(sn.snapshot_id)          AS snapshot_count
  FROM source s
  LEFT JOIN source_clock c    ON c.source_id = s.source_id
  LEFT JOIN source_snapshot sn ON sn.source_id = s.source_id
 GROUP BY s.source_id, s.source_name, s.source_role, s.country, s.access_state,
          s.collection_state, c.source_status, c.latest_source_publication,
          c.latest_capture, c.observation_age_days, c.pipeline_latency_state,
          c.pipeline_latency_seconds;

-- v_issue_expert · Pessoas com expertise PROVADA no par cultura x problema.
-- POR QUE: Filtra pelo portao. Quem nao passou nao aparece como especialista do problema — e a view nao ordena por contagem de nada.
-- LE: person, scientific_person, issue_expertise
CREATE OR REPLACE VIEW v_issue_expert AS
SELECT p.person_id,
       p.display_name,
       p.country,
       p.identity_proved,
       p.gdpr_treatment_state,
       o.name                         AS organization,
       sp.relation_to_issue_as_declared,
       ie.crop_term_id,
       ie.issue_term_id,
       ie.issue_expertise_state,
       ie.evidence_id
  FROM issue_expertise ie
  JOIN person p            ON p.person_id = ie.person_id
  JOIN scientific_person sp ON sp.person_id = ie.person_id
  LEFT JOIN organization o ON o.organization_id = sp.organization_id
 WHERE ie.issue_expertise_state = 'PROVED'
   AND p.gdpr_treatment_state IN ('CLEARED','IN_REVIEW');

-- v_publish_provenance · De um objeto ate o commit do freeze que o produziu.
-- POR QUE: PROVENANCE_REACHES_SOURCE_FREEZE, verificavel em uma consulta.
-- LE: attention_object, publish_run, publish_run_freeze, storage_provenance
CREATE OR REPLACE VIEW v_publish_provenance AS
SELECT o.attention_object_id,
       o.country,
       o.object_type,
       pr.publish_run_id,
       pr.pipeline_version,
       pr.schema_version,
       pr.published_at,
       pr.status,
       pr.shadow_validation_passed,
       prf.repository,
       prf.path,
       prf.commit_sha,
       prf.hose_id,
       stp.source_backend,
       stp.as_of_date
  FROM attention_object o
  LEFT JOIN publish_run pr        ON pr.publish_run_id = o.publish_run_id
  LEFT JOIN publish_run_freeze prf ON prf.publish_run_id = pr.publish_run_id
  LEFT JOIN storage_provenance stp ON stp.subject_kind = 'attention_object'
                                  AND stp.subject_id = o.attention_object_id;

-- ── RPCs ──────────────────────────────────────────────────────────────
-- O V8 nao monta a inteligencia com dezessete joins no navegador.
-- SECURITY INVOKER de proposito: a RPC NAO contorna RLS.

-- Objeto + representacao no idioma pedido, com fallback explicito.
--   RETORNA: object, representation, requested_language, display_language, fallback_used
--   POR QUE: O V8 nao monta a inteligencia com dezessete joins no navegador. E o fallback e declarado, nunca fingido.
CREATE OR REPLACE FUNCTION get_attention_object(p_object_id text, p_display_language language_code)
RETURNS TABLE (
  attention_object_id text,
  object_type object_type,
  country char(2),
  attention_state attention_state,
  decision_question text,
  decision_owner department,
  computed_is_ready boolean,
  blocking_requirements text[],
  display_language language_code,
  requested_language language_code,
  fallback_used text,
  title text,
  summary text,
  what_we_dont_know text
)
LANGUAGE plpgsql STABLE SECURITY INVOKER AS $fn$
BEGIN
  RETURN QUERY
    SELECT o.attention_object_id, o.object_type, o.country, o.attention_state,
           o.decision_question, o.decision_owner,
           rd.computed_is_ready, rd.blocking_requirements,
           rr.language, rr.requested_language, rr.fallback_used,
           rr.title, rr.summary, rr.what_we_dont_know
      FROM attention_object o
      LEFT JOIN v_attention_readiness rd ON rd.attention_object_id = o.attention_object_id
      LEFT JOIN LATERAL resolve_representation(o.attention_object_id, p_display_language) rr
             ON TRUE
     WHERE o.attention_object_id = p_object_id;
END;
$fn$;

-- Fila de atencao do pais, com o motivo quando vazia.
--   RETORNA: items, empty_reason, blocking_gate_counts
CREATE OR REPLACE FUNCTION get_attention_feed(p_country char(2), p_display_language language_code)
RETURNS TABLE (
  attention_object_id text,
  object_type object_type,
  attention_state attention_state,
  blocker_text text,
  display_language language_code,
  requested_language language_code,
  fallback_used text,
  title text,
  empty_reason text
)
LANGUAGE plpgsql STABLE SECURITY INVOKER AS $fn$
DECLARE
  v_total int;
BEGIN
  SELECT count(*) INTO v_total
    FROM attention_object o
   WHERE o.country = p_country AND o.attention_state = 'ATTENTION_READY';

  IF v_total = 0 THEN
    -- fila vazia se mostra vazia, COM o motivo. Nunca uma lista muda.
    RETURN QUERY
      SELECT NULL::text, NULL::object_type, NULL::attention_state, NULL::text,
             NULL::language_code, p_display_language, NULL::text, NULL::text,
             coalesce(
               (SELECT 'NO_OBJECT_PASSED_ALL_GATES: ' ||
                       string_agg(DISTINCT req, ', ')
                  FROM attention_object o2
                  JOIN v_attention_readiness rd2
                    ON rd2.attention_object_id = o2.attention_object_id
                  CROSS JOIN LATERAL unnest(rd2.blocking_requirements) AS req
                 WHERE o2.country = p_country),
               'NO_OBJECTS_FOR_COUNTRY');
    RETURN;
  END IF;

  RETURN QUERY
    SELECT o.attention_object_id, o.object_type, o.attention_state, o.blocker_text,
           rr.language, rr.requested_language, rr.fallback_used, rr.title, NULL::text
      FROM attention_object o
      LEFT JOIN LATERAL resolve_representation(o.attention_object_id, p_display_language) rr
             ON TRUE
     WHERE o.country = p_country AND o.attention_state = 'ATTENTION_READY';
END;
$fn$;

-- Gaveta de evidencia completa, com original preservado.
--   RETORNA: evidence, source_provenance, storage_provenance, original_text, source_language, translation, fallback_used
CREATE OR REPLACE FUNCTION get_evidence(p_evidence_id text, p_display_language language_code)
RETURNS TABLE (
  evidence_id text,
  source_id text,
  source_backend source_backend,
  repository text,
  path text,
  commit_sha char(40),
  db_schema text,
  table_or_view text,
  primary_key text,
  source_location_country char(2),
  fact_location_country char(2),
  evidence_level evidence_level,
  original_text text,
  source_language language_code,
  translated_text text,
  translation_language language_code,
  translation_provenance text,
  display_language language_code,
  requested_language language_code,
  fallback_used text
)
LANGUAGE plpgsql STABLE SECURITY INVOKER AS $fn$
BEGIN
  RETURN QUERY
    SELECT d.evidence_id, d.source_id, d.source_backend,
           d.repository, d.path, d.commit_sha,
           d.db_schema, d.table_or_view, d.primary_key,
           d.source_location_country, d.fact_location_country,
           d.evidence_level,
           -- ORIGINAL_TEXT nunca sofre fallback: vai na lingua da fonte, sempre
           d.original_text, d.source_language,
           t.translated_text, t.translation_language, t.translation_provenance,
           coalesce(t.translation_language, d.source_language) AS display_language,
           p_display_language,
           CASE WHEN t.translation_language IS NULL THEN 'NO_TRANSLATION_ORIGINAL_ONLY'
                WHEN t.translation_language = p_display_language THEN 'NO'
                ELSE 'YES' END
      FROM v_evidence_drawer d
      LEFT JOIN content_translation t
             ON t.canonical_entity_id = d.canonical_entity_id
            AND t.translation_language = p_display_language
     WHERE d.evidence_id = p_evidence_id;
END;
$fn$;

-- Politica de fallback de idioma, num lugar so.
--   RETORNA: language, text, requested_language, fallback_used, fallback_chain
--   POR QUE: Uma implementacao, nao uma por view. Se FR nao existe, devolve EN dizendo que devolveu EN.
CREATE OR REPLACE FUNCTION resolve_representation(p_entity_id text, p_requested_language language_code)
RETURNS TABLE (
  language language_code,
  title text,
  summary text,
  interpretation text,
  attention_reason text,
  what_we_know text,
  what_we_dont_know text,
  requested_language language_code,
  fallback_used text
)
LANGUAGE plpgsql STABLE SECURITY INVOKER AS $fn$
DECLARE
  v_chain language_code[] := ARRAY[p_requested_language, 'en', 'pt'];
  v_lang  language_code;
BEGIN
  -- a cadeia e explicita e curta. Nunca fabricar traducao para preencher.
  FOREACH v_lang IN ARRAY v_chain LOOP
    IF EXISTS (SELECT 1 FROM attention_object_representation r
                WHERE r.attention_object_id = p_entity_id AND r.language = v_lang) THEN
      RETURN QUERY
        SELECT r.language, r.title, r.summary, r.interpretation, r.attention_reason,
               r.what_we_know, r.what_we_dont_know,
               p_requested_language,
               CASE WHEN v_lang = p_requested_language THEN 'NO' ELSE 'YES' END
          FROM attention_object_representation r
         WHERE r.attention_object_id = p_entity_id AND r.language = v_lang;
      RETURN;
    END IF;
  END LOOP;
  -- nenhuma lingua da cadeia existe: dizer isso, nao inventar
  RETURN QUERY SELECT NULL::language_code, NULL::text, NULL::text, NULL::text,
                      NULL::text, NULL::text, NULL::text,
                      p_requested_language, 'NO_REPRESENTATION_AVAILABLE'::text;
END;
$fn$;

-- FALLBACK DE IDIOMA: <requested> -> en -> pt
-- Nunca fabricar traducao. Se nenhuma lingua da cadeia existir, devolver NULL com FALLBACK_USED = NO_REPRESENTATION_AVAILABLE.
-- ORIGINAL_TEXT nunca entra na cadeia de fallback: ele e exibido na lingua da fonte, sempre.

COMMIT;
