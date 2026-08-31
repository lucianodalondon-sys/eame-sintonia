# DICIONÁRIO DE DADOS — SUPABASE SINTONIA EAME

> **GERADO** por `scripts/supabase_schema.py` a partir de
> `data/supabase/SUPABASE-CANONICAL-SCHEMA.json`. Não editar à mão.

```
SCHEMA_VERSION = 0.1.0-draft        MIGRATION_APPLIED = NO
TABELAS = 57   VIEWS = 13   RPCs = 4    ENUMS = 27 
COLUNAS = 417  CHECKS = 31   CHAVES ESTRANGEIRAS = 112
```

**Toda tabela tem um POR QUE.** Uma tabela sem justificativa é uma tabela que
ninguém sabe defender quando alguém propuser fundi-la com outra.

---

## VOCABULÁRIOS FECHADOS

**`object_type`** — PHENOMENON_CASE · REGULATORY_DEADLINE · COMPETITOR_IDENTITY_CHAIN · LONGITUDINAL_FIELD_PRESSURE

**`attention_state`** — ATTENTION_READY · ATTENTION_CANDIDATE_TEST · VALID_EVIDENCE_NOT_ATTENTION_READY · NEEDS_EVIDENCE · FORMING · WATCH · FUTURE · ARCHIVED

**`field_state`** — PROVED · NOT_PROVED · NOT_MEASURED · NOT_READY · NOT_APPLICABLE

**`language_code`** — pt · en · es · fr · it · MULTILINGUAL · UNKNOWN

**`geo_resolution`** — COUNTRY · NUTS2 · PROVINCE · MUNICIPALITY · LOCALITY_TEXT · POINT · NOT_KNOWN

**`action_type`** — BUSINESS_DECISION · SYSTEM_DECISION · INVESTIGATION

**`convergence_kind`** — PHENOMENON_CONVERGENCE · IDENTITY_CONVERGENCE · CONTEXTUAL_ALIGNMENT

**`dependency_type`** — SOURCE_DEPENDENCY · OBSERVATION_DEPENDENCY · ENTITY_DEPENDENCY · DERIVATION_DEPENDENCY · SEMANTIC_DEPENDENCY · INDEPENDENT_SOURCE

**`signal_family`** — TERRITORIAL · SCIENCE_RESEARCHER · NATIONAL_REGISTRY · TRADEMARK · META_PAID_ADS · CREATOR · FIELD_HISTORICAL · COMPETITOR_PUBLIC_COMM

**`independence_state`** — INDEPENDENT · DEPENDENT · NOT_PROVED

**`evidence_level`** — PROVED · MEASURED · PARTIAL · NOT_PROVED · NOT_MEASURED · NOT_KNOWN

**`source_backend`** — GITHUB · SUPABASE

**`data_state`** — READY · EMPTY_VALID · NOT_STARTED · NOT_AVAILABLE · BLOCKED

**`pipeline_state`** — NOT_STARTED · RUNNING · PARTIAL · COMPLETE · BLOCKED · FAILED_CLOSED

**`content_collection_stage`** — NOT_STARTED · RUNNING · PARTIAL · COMPLETE

**`entry_path`** — FROM_ATTENTION_OBJECT · FROM_CROP_REGION_SEARCH

**`event_type`** — FIRST_OBSERVED · SOURCE_PUBLICATION · FIRST_CAPTURE · NEW_EVIDENCE · SIGNAL_FAMILY_ADDED · STATE_CHANGE · TRIGGER · ATTENTION_CANDIDATE · ATTENTION_READY · ACTION_REVIEW · ARCHIVED · GAP

**`time_resolution`** — EXACT_DATE · WEEK · MONTH · PHENOLOGICAL_STAGE · SEASON · NOT_KNOWN

**`clock_kind`** — OBSERVATION_TIME · STAGE_AT_OBSERVATION · CURRENT_CROP_STAGE · LABEL_USE_STAGE · APPLICATION_WINDOW · REGULATORY_DEADLINE · FUTURE_SEASON_WINDOW

**`ontology_term_kind`** — CROP · ISSUE · ACTIVE_INGREDIENT · PRODUCT_CATEGORY

**`creator_entity_kind`** — PERSON_CREATOR · FARM_BUSINESS_ENTITY

**`department`** — MARKET_DEVELOPMENT · REGULATORY · PORTFOLIO · TECHNICAL_SCIENCE · MARKETING · COMMERCIAL · SUPPLY

**`adama_line`** — DISEASE_CONTROL · WEED_CONTROL · PEST_CONTROL · CROP_ENHANCEMENT · NOT_APPLICABLE

**`gdpr_state`** — NOT_STARTED · IN_REVIEW · CLEARED · RESTRICTED

**`publish_status`** — PENDING · VALIDATING · SHADOW_OK · PUBLISHED · FAILED_CLOSED

**`observation_kind`** — TERRITORIAL_OBSERVATION · FIELD_VOICE_OBSERVATION · OBSERVED_PAID_ACTIVITY · FIELD_PRESSURE_READING

**`translation_quality`** — MACHINE_UNREVIEWED · MACHINE_REVIEWED · HUMAN · NOT_KNOWN

### O que NÃO vira enum

**`request_state`** — UNWIRED · LOADING · ERROR_FAIL_CLOSED

> Sao estados da CAMADA DE APLICACAO, nao verdades do negocio. Guardar LOADING numa tabela transformaria uma requisicao em andamento em fato sobre o mundo. UNWIRED e propriedade da ligacao, nao do dado: uma linha existir ja prova que a rota foi ligada.

**Onde vivem:** no receptor do V8, em memoria, derivados do resultado da chamada

**O que fica no banco:** data_state (READY, EMPTY_VALID, NOT_STARTED, NOT_AVAILABLE, BLOCKED) e pipeline_state — os dois descrevem o MUNDO e a COLETA, nao a requisicao

---

## TABELAS

### `ontology_term`

Termo canonico neutro de idioma: cultura, problema, ingrediente ativo.

> **Por quê:** O contrato multilingue exige ID neutro separado do rotulo. Codigo EPPO e o identificador; o nome em cada lingua vive em ontology_term_label. Sem esta tabela, 'mildiu' e 'downy mildew' viram dois problemas diferentes.

`HOSE_ID = H9` · `CANONICAL_PAYLOAD_TYPE = ONTOLOGY_TERM`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `term_id` 🔑 | text | não |  |
| `term_kind` | ontology_term_kind | não |  |
| `eppo_code` | text | sim | identificador neutro quando existe |
| `created_at` | timestamptz | não |  |

### `ontology_term_label`

Rotulo do termo em cada idioma.

> **Por quê:** Separa ID de rotulo. Cinco idiomas nao criam cinco termos.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `term_id` 🔑 | text | não | → `ontology_term.term_id` |
| `language` 🔑 | language_code | não |  |
| `label` | text | não |  |

### `geo_anchor`

Ancoragem geografica com resolucao declarada.

> **Por quê:** LOCALITY_TEXT nunca vira POINT. A geometria so existe quando a fonte a deu; a resolucao viaja junto e o consumidor decide se pode desenhar.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `geo_id` 🔑 | text | não |  |
| `country` | char(2) | não |  |
| `region` | text | sim |  |
| `locality_text` | text | sim | como a fonte escreveu; nunca geocodificado |
| `geometry` | jsonb | sim | GeoJSON; NULL quando nao ha |
| `geo_resolution` | geo_resolution | não |  |
| `geometry_source_id` | text | sim | → `source.source_id` · geometria exige origem explicita |

- **check `point_exige_geometria`** — `(geo_resolution <> 'POINT') OR (geometry IS NOT NULL)`
- **check `geometria_exige_origem`** — `(geometry IS NULL) OR (geometry_source_id IS NOT NULL)`
- **check `locality_text_nao_e_point`** — `(geo_resolution <> 'LOCALITY_TEXT') OR (geometry IS NULL)`

### `source`

Fonte externa, com papel e escopo declarados.

> **Por quê:** SOURCE_ID e a ancora de toda proveniencia de evidencia. Uma fonte existe antes de qualquer captura.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `source_id` 🔑 | text | não |  |
| `source_name` | text | não |  |
| `source_role` | text | não |  |
| `entity_kind` | text | sim |  |
| `country` | char(2) | sim | pais da PUBLICACAO, nunca do fato |
| `access_state` | text | não |  |
| `cadence` | text | sim |  |
| `geographic_scope` | text | sim |  |
| `crop_scope` | text | sim |  |
| `is_prospective` | boolean | sim |  |
| `collection_state` | pipeline_state | não |  |
| `created_at` | timestamptz | não |  |

### `source_snapshot`

Uma captura datada de uma fonte, com hash.

> **Por quê:** Sem snapshot, 'a fonte diz X' nao e reproduzivel. E e ele que permite medir latencia com DUAS capturas — com uma so, latencia e NOT_MEASURED.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `snapshot_id` 🔑 | text | não |  |
| `source_id` | text | não | → `source.source_id` |
| `captured_at` | timestamptz | não |  |
| `source_published_at` | date | sim |  |
| `content_hash` | text | sim |  |
| `artifact_ref` | text | sim |  |
| `artifact_language` | language_code | não |  |

### `source_clock`

Os cinco relogios da fonte, cada um separado.

> **Por quê:** Idade da observacao NAO e latencia de pipeline. Fundir os dois num numero foi um erro que ja apareceu no produto.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `source_id` 🔑 | text | não | → `source.source_id` |
| `source_status` | text | não |  |
| `latest_source_publication` | date | sim |  |
| `latest_capture` | timestamptz | sim |  |
| `observation_age_days` | integer | sim | idade do FATO |
| `pipeline_latency_state` | field_state | não |  |
| `pipeline_latency_seconds` | integer | sim |  |

- **check `latencia_sem_medicao_e_nula`** — `(pipeline_latency_state = 'PROVED') OR (pipeline_latency_seconds IS NULL)`

### `source_provenance`

De onde a EVIDENCIA veio no mundo — a origem externa real.

> **Por quê:** Separada de storage_provenance de proposito. Quando um dado ja estiver no Supabase, SOURCE_BACKEND = SUPABASE descreveria a ENTREGA e apagaria a origem externa. As duas nunca se substituem.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `source_provenance_id` 🔑 | bigint | não |  |
| `evidence_id` | text | não | → `evidence.evidence_id` |
| `source_id` | text | não | → `source.source_id` |
| `snapshot_id` | text | sim | → `source_snapshot.snapshot_id` |
| `original_ref` | text | sim | URL ou identificador na origem |
| `as_of_date` | date | sim |  |

### `storage_provenance`

De onde a linha foi LIDA ou ENTREGUE — GitHub ou Supabase.

> **Por quê:** Envelope de transporte. O V8 renderiza os dois com o mesmo componente; o discriminador e SOURCE_BACKEND e nenhuma coluna do outro backend e preenchida junto.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `storage_provenance_id` 🔑 | bigint | não |  |
| `subject_kind` | text | não | attention_object | evidence | observation | series | ... |
| `subject_id` | text | não |  |
| `source_backend` | source_backend | não |  |
| `repository` | text | sim |  |
| `path` | text | sim |  |
| `commit_sha` | char(40) | sim |  |
| `content_hash` | text | sim |  |
| `db_schema` | text | sim |  |
| `table_or_view` | text | sim |  |
| `primary_key` | text | sim |  |
| `snapshot_id` | text | sim |  |
| `captured_at` | timestamptz | sim |  |
| `source_id` | text | sim | → `source.source_id` |
| `as_of_date` | date | sim |  |
| `publish_run_id` | text | sim | → `publish_run.publish_run_id` |

- **check `github_exige_commit_e_caminho`** — `(source_backend <> 'GITHUB') OR (repository IS NOT NULL AND path IS NOT NULL AND commit_sha IS NOT NULL)`
- **check `supabase_exige_tabela_e_chave`** — `(source_backend <> 'SUPABASE') OR (db_schema IS NOT NULL AND table_or_view IS NOT NULL AND primary_key IS NOT NULL)`
- **check `backends_nao_se_misturam`** — `NOT (repository IS NOT NULL AND table_or_view IS NOT NULL)`

### `evidence`

Uma evidencia, reutilizavel por muitos consumidores.

> **Por quê:** Uma evidencia sustenta objeto, perna de convergencia, base de acao, evento de timeline e relacao. Duplicar fisicamente por uso criaria cinco verdades que divergem.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `evidence_id` 🔑 | text | não |  |
| `source_id` | text | não | → `source.source_id` |
| `snapshot_id` | text | sim | → `source_snapshot.snapshot_id` |
| `source_location_country` | char(2) | sim | pais da PUBLICACAO |
| `fact_location_geo_id` | text | sim | → `geo_anchor.geo_id` · pais e regiao do FATO — nunca o mesmo campo |
| `source_published_at` | date | sim |  |
| `captured_at` | timestamptz | sim |  |
| `evidence_level` | evidence_level | não |  |
| `original_text` | text | sim | na lingua da fonte, sem edicao |
| `source_language` | language_code | não |  |
| `document_excerpt` | text | sim | H1 preserva 3.000 caracteres, nao o corpo inteiro |
| `passage_start` | integer | sim |  |
| `passage_end` | integer | sim |  |
| `source_url` | text | sim |  |
| `created_at` | timestamptz | não |  |

- **check `offsets_andam_em_par`** — `(passage_start IS NULL) = (passage_end IS NULL)`

### `content_entity`

Entidade textual canonica: o texto existe uma vez, com sua lingua de origem.

> **Por quê:** H9. A verdade textual e o ORIGINAL. Traducao e representacao, e vive em outra tabela.

`HOSE_ID = H9` · `CANONICAL_PAYLOAD_TYPE = CONTENT_ENTITY`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `canonical_entity_id` 🔑 | text | não |  |
| `entity_kind` | text | não | EVIDENCE_QUOTE | OBJECT_TITLE | ACTION_TEXT | ... |
| `source_language` | language_code | não |  |
| `original_text` | text | não |  |
| `evidence_id` | text | sim | → `evidence.evidence_id` |
| `created_at` | timestamptz | não |  |

### `content_translation`

Traducao de um content_entity, com proveniencia propria.

> **Por quê:** Traducao NUNCA substitui o original. Ter tabela separada torna impossivel sobrescrever o original por acidente de UPDATE.

`HOSE_ID = H9` · `CANONICAL_PAYLOAD_TYPE = CONTENT_TRANSLATION`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `canonical_entity_id` 🔑 | text | não | → `content_entity.canonical_entity_id` |
| `translation_language` 🔑 | language_code | não |  |
| `translated_text` | text | não |  |
| `translation_provenance` | text | não | quem traduziu |
| `translation_quality` | translation_quality | não |  |
| `translated_at` | timestamptz | sim |  |
| `source_text_hash` | text | sim | hash do original no momento da traducao — muda o original, a traducao fica obsoleta |

- **check `traducao_nao_e_na_lingua_de_origem`** — `translation_language NOT IN ('MULTILINGUAL','UNKNOWN')`

### `attention_object`

A unidade superior do produto. Identidade neutra de idioma.

> **Por quê:** UM objeto, varias representacoes. Nunca AO-001-PT e AO-001-EN. Campos especificos de cada tipo ficam em tabelas filhas — quatro tipos numa mega-tabela produziriam colunas nulas que parecem lacunas.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `attention_object_id` 🔑 | text | não | NEUTRO DE IDIOMA |
| `object_type` | object_type | não |  |
| `country` | char(2) | não |  |
| `attention_state` | attention_state | não |  |
| `decision_question` | text | sim |  |
| `decision_owner` | department | sim |  |
| `adama_line` | adama_line | não |  |
| `blocker_text` | text | sim |  |
| `as_of_date` | date | sim |  |
| `last_evidence_at` | date | sim |  |
| `publish_run_id` | text | sim | → `publish_run.publish_run_id` |
| `created_at` | timestamptz | não |  |
| `updated_at` | timestamptz | não |  |

### `attention_object_representation`

O texto do objeto num idioma. Nunca a verdade estruturada.

> **Por quê:** Separa FATO ESTRUTURADO de REPRESENTACAO LINGUISTICA. Datas, estados, ids e relacoes existem uma vez; o texto existe por idioma.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `attention_object_id` 🔑 | text | não | → `attention_object.attention_object_id` |
| `language` 🔑 | language_code | não |  |
| `title` | text | não |  |
| `summary` | text | sim |  |
| `interpretation` | text | sim |  |
| `attention_reason` | text | sim |  |
| `what_we_know` | text | sim |  |
| `what_we_dont_know` | text | sim | secao obrigatoria no dossie; nunca suprimida na exportacao |
| `is_translation` | boolean | não |  |
| `translation_provenance` | text | sim |  |
| `translation_quality` | translation_quality | sim |  |

- **check `traducao_declara_proveniencia`** — `(is_translation = false) OR (translation_provenance IS NOT NULL)`

### `attention_readiness`

Os cinco requisitos do portao, um por linha, reproduziveis.

> **Por quê:** ATTENTION_READY nao pode ser um booleano escrito a mao. Guardando os cinco componentes, o estado e recalculavel e auditavel — e a fila vazia consegue dizer QUAL portao segurou cada objeto.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `attention_object_id` 🔑 | text | não | → `attention_object.attention_object_id` |
| `requirement` 🔑 | text | não | VALID_EVIDENCE | OBJECT_SPECIFIC_TRIGGER | TIME_RELEVANCE | DECISION_QUESTION | DECISION_OWNER |
| `state` | field_state | não |  |
| `reason` | text | sim |  |
| `evaluated_at` | timestamptz | não |  |

- **check `requisito_do_vocabulario`** — `requirement IN ('VALID_EVIDENCE','OBJECT_SPECIFIC_TRIGGER','TIME_RELEVANCE','DECISION_QUESTION','DECISION_OWNER')`

### `attention_object_evidence`

Quais evidencias sustentam o objeto.

> **Por quê:** N:N. A mesma evidencia serve a mais de um objeto sem ser copiada.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `attention_object_id` 🔑 | text | não | → `attention_object.attention_object_id` |
| `evidence_id` 🔑 | text | não | → `evidence.evidence_id` |
| `role` | text | sim |  |

### `attention_object_unknown`

O que ainda nao sabemos, por objeto.

> **Por quê:** Estado transversal, nunca superficie. Guardado como lista para o bloco obrigatorio do dossie.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `attention_object_id` 🔑 | text | não | → `attention_object.attention_object_id` |
| `unknown_key` 🔑 | text | não |  |
| `state` | field_state | não |  |
| `note` | text | sim |  |

### `object_clock`

Os sete relogios do objeto, cada um com sua resolucao.

> **Por quê:** Os sete NUNCA se fundem, e a interface nao desenha precisao que o dado nao tem. Guardar cada um com time_resolution propria e o que impede a fabricacao de calendario.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `attention_object_id` 🔑 | text | não | → `attention_object.attention_object_id` |
| `clock_kind` 🔑 | clock_kind | não |  |
| `resolution` | time_resolution | não |  |
| `value_date` | date | sim |  |
| `value_text` | text | sim | BBCH, estacao, faixa |
| `state` | field_state | não |  |
| `source_id` | text | sim | → `source.source_id` |

- **check `sem_resolucao_sem_data`** — `(resolution <> 'NOT_KNOWN') OR (value_date IS NULL)`

### `phenomenon_case`

Tabela filha do tipo PHENOMENON_CASE.

> **Por quê:** REQUIRED = COUNTRY, REGION, CROP, ISSUE, OBSERVATION_TIME. Sao NOT NULL aqui e nao existem nos outros tipos.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `attention_object_id` 🔑 | text | não | → `attention_object.attention_object_id` |
| `geo_id` | text | não | → `geo_anchor.geo_id` |
| `crop_term_id` | text | não | → `ontology_term.term_id` |
| `issue_term_id` | text | não | → `ontology_term.term_id` |
| `crop_issue_pairing_state` | field_state | não |  |
| `pairing_evidence_id` | text | sim | → `evidence.evidence_id` · a passagem onde cultura e problema coocorrem |

- **check `par_provado_exige_a_passagem`** — `(crop_issue_pairing_state <> 'PROVED') OR (pairing_evidence_id IS NOT NULL)`

### `regulatory_deadline_object`

Tabela filha do tipo REGULATORY_DEADLINE.

> **Por quê:** REQUIRED = COUNTRY, REGISTRATION_ID, PRODUCT, DEADLINE, STATUS_AS_DECLARED_BY_SOURCE. CROP, ISSUE e REGION sao NOT_APPLICABLE e por isso nao existem como coluna — ausencia de coluna e mais forte que coluna nula.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `attention_object_id` 🔑 | text | não | → `attention_object.attention_object_id` |
| `registration_id` | text | não | → `registration.registration_id` |
| `deadline_date` | date | não |  |
| `deadline_kind` | text | não |  |
| `status_as_declared_by_source` | text | não | COMO A FONTE DECLARA — nunca reinterpretado |
| `label_effect_state` | field_state | não | expiracao NAO e retirada |
| `max_authorized_action` | action_type | não |  |

- **check `prazo_nao_autoriza_decisao_de_negocio`** — `max_authorized_action <> 'BUSINESS_DECISION'`

### `competitor_identity_chain_object`

Tabela filha do tipo COMPETITOR_IDENTITY_CHAIN.

> **Por quê:** REQUIRED = COMPETITOR, COUNTRY, PRODUCT_NORMALIZED, HOLDER_AGREEMENT. CROP e ISSUE sao NOT_APPLICABLE.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `attention_object_id` 🔑 | text | não | → `attention_object.attention_object_id` |
| `competitor_product_identity_id` | text | não | → `competitor_product_identity.identity_id` |

### `longitudinal_field_pressure_object`

Tabela filha do tipo LONGITUDINAL_FIELD_PRESSURE.

> **Por quê:** REQUIRED inclui SERIES, BASELINE e COHORT_CONTROL — todos vivem na serie, referenciada aqui.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `attention_object_id` 🔑 | text | não | → `attention_object.attention_object_id` |
| `series_id` | text | não | → `field_pressure_series.series_id` |

### `observation`

Supertipo de tudo que foi OBSERVADO, com data e ancora.

> **Por quê:** Territorial, voz de campo, atividade paga e leitura de serie sao todas observacoes. Ter o supertipo permite que evento de timeline e perna de convergencia apontem para 'uma observacao' sem saber o subtipo.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `observation_id` 🔑 | text | não |  |
| `observation_kind` | observation_kind | não |  |
| `observed_at` | date | sim |  |
| `observed_at_resolution` | time_resolution | não |  |
| `geo_id` | text | sim | → `geo_anchor.geo_id` |
| `source_id` | text | não | → `source.source_id` |
| `evidence_id` | text | sim | → `evidence.evidence_id` |
| `signal_family` | signal_family | não |  |

### `territorial_observation`

H1 · payload canonico TERRITORIAL_OBSERVATION.

> **Por quê:** Nome canonico do FINAL-HOSE-MAP. O casco chama de TERRITORIAL_ATTENTION_OBJECT; esse alias fica em UI_ALIAS_MAP e nao entra aqui.

`HOSE_ID = H1` · `CANONICAL_PAYLOAD_TYPE = TERRITORIAL_OBSERVATION`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `observation_id` 🔑 | text | não | → `observation.observation_id` |
| `country_of_fact` | char(2) | não |  |
| `region_of_fact` | text | sim |  |
| `crop_term_id` | text | sim | → `ontology_term.term_id` |
| `issue_term_id` | text | sim | → `ontology_term.term_id` |
| `issue_evidence_passage` | text | sim |  |
| `published_at` | date | sim |  |
| `phenology_at_observation` | text | sim |  |
| `document_excerpt_evidence_id` | text | sim | → `evidence.evidence_id` |
| `multi_bulletin_document` | boolean | não |  |

### `registration`

Registro nacional de produto, de qualquer titular.

> **Por quê:** H2 carrega o prazo de UM registro, de QUALQUER titular — inclusive de concorrente. Manter registro separado de portfolio ADAMA e o que impede o produto de dizer que a ADAMA tem resposta porque um registro qualquer tem prazo.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `registration_id` 🔑 | text | não |  |
| `country` | char(2) | não |  |
| `registration_number` | text | não |  |
| `holder_organization_id` | text | sim | → `organization.organization_id` |
| `product_id` | text | sim | → `product.product_id` |
| `status_as_declared_by_source` | text | sim |  |
| `source_id` | text | não | → `source.source_id` |

### `registration_deadline`

H2 · payload canonico REGISTRATION_DEADLINE.

> **Por quê:** Nome canonico. O casco usa REGULATORY_DEADLINE, que e o OBJECT_TYPE — sao coisas diferentes e nao podem colidir no banco.

`HOSE_ID = H2` · `CANONICAL_PAYLOAD_TYPE = REGISTRATION_DEADLINE`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `deadline_id` 🔑 | text | não |  |
| `registration_id` | text | não | → `registration.registration_id` |
| `deadline_date` | date | não |  |
| `deadline_kind` | text | não |  |
| `status_as_declared_by_source` | text | não |  |
| `expiry_is_withdrawal` | boolean | não | guard: expiracao NAO e retirada. Sempre false ate prova em contrario da fonte. |
| `evidence_id` | text | não | → `evidence.evidence_id` |
| `source_id` | text | não | → `source.source_id` |
| `as_of_date` | date | sim |  |

- **check `expiry_nao_e_withdrawal`** — `expiry_is_withdrawal = false`

### `product`

Produto comercial normalizado.

> **Por quê:** Nome comercial != titular != fabricante. Normalizar aqui e o que permite comparar mercados.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `product_id` 🔑 | text | não |  |
| `normalized_name` | text | não |  |
| `active_ingredient_term_id` | text | sim | → `ontology_term.term_id` |
| `is_adama` | boolean | não |  |

### `organization`

Empresa, titular ou grupo.

> **Por quê:** Titular != grupo != fabricante. O portao URBOLE compara nome + grupo + pais, e precisa dos tres separados.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `organization_id` 🔑 | text | não |  |
| `name` | text | não |  |
| `group_name` | text | sim |  |
| `country` | char(2) | sim |  |

### `trademark_record`

Registro de marca.

> **Por quê:** Primeiro elo da cadeia competitiva, com escritorio e data de deposito proprios.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `trademark_id` 🔑 | text | não |  |
| `trademark_name` | text | não |  |
| `office` | text | sim |  |
| `filed_at` | date | sim |  |
| `status` | text | sim |  |
| `holder_organization_id` | text | sim | → `organization.organization_id` |
| `evidence_id` | text | sim | → `evidence.evidence_id` |

### `competitor_product_identity`

H3 · payload canonico COMPETITOR_PRODUCT_IDENTITY. Liga marca, registro local e atividade observada.

> **Por quê:** Nome canonico. O casco usa COMPETITOR_IDENTITY_CHAIN, que e o OBJECT_TYPE. Os tres elos existirem nao valida a cadeia: quem valida e AGREEMENT_STATE.

`HOSE_ID = H3` · `CANONICAL_PAYLOAD_TYPE = COMPETITOR_PRODUCT_IDENTITY`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `identity_id` 🔑 | text | não |  |
| `country` | char(2) | não |  |
| `competitor_organization_id` | text | não | → `organization.organization_id` |
| `normalized_product_id` | text | sim | → `product.product_id` |
| `trademark_id` | text | sim | → `trademark_record.trademark_id` |
| `local_registration_id` | text | sim | → `registration.registration_id` |
| `observed_paid_activity_id` | text | sim | → `observed_paid_activity.paid_activity_id` |
| `agreement_state` | field_state | não | produto x titular x pais |
| `urbole_guard_result` | text | não | portao sem resultado registrado e portao sem dentes |
| `urbole_guard_ran_at` | timestamptz | sim |  |

- **check `concordancia_exige_portao_exercido`** — `(agreement_state <> 'PROVED') OR (urbole_guard_result <> 'NOT_RUN')`

### `observed_paid_activity`

H4 · payload canonico OBSERVED_PAID_ACTIVITY. Evidencia, nunca objeto proprio.

> **Por quê:** Nome canonico. E o terceiro elo da cadeia e nada mais: DO_NOT_BUILD = META_DASHBOARD. Os sete 'nao pode afirmar' viajam com a linha.

`HOSE_ID = H4` · `CANONICAL_PAYLOAD_TYPE = OBSERVED_PAID_ACTIVITY`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `paid_activity_id` 🔑 | text | não |  |
| `observation_id` | text | não | → `observation.observation_id` |
| `platform` | text | não |  |
| `page_id` | text | não |  |
| `page_name` | text | sim |  |
| `page_country_scope` | char(2) | sim | NAO e o pais de entrega do anuncio |
| `ad_delivery_country_state` | field_state | não |  |
| `observed_at` | timestamptz | não |  |
| `observation_window_seconds` | integer | sim |  |
| `ad_card_count` | integer | sim | AD_CARD != AD |
| `cannot_claim_list` | text[] | não |  |
| `operational_temporal_signal_state` | field_state | não |  |

- **check `sempre_carrega_os_nao_pode_afirmar`** — `array_length(cannot_claim_list, 1) >= 6`

### `company_local_account`

H8 · payload canonico COMPANY_LOCAL_ACCOUNT. Existe antes da coleta.

> **Por quê:** Nome canonico (o casco usa COMPANY_PUBLIC_ACCOUNT). A conta identificada precisa existir com CONTENT_COLLECTION_STAGE = NOT_STARTED, para que zero conteudo nunca seja lido como silencio da empresa.

`HOSE_ID = H8` · `CANONICAL_PAYLOAD_TYPE = COMPANY_LOCAL_ACCOUNT`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `account_id` 🔑 | text | não |  |
| `organization_id` | text | não | → `organization.organization_id` |
| `platform` | text | não |  |
| `country_scope` | char(2) | sim |  |
| `page_role` | text | sim | COUNTRY_SCOPE != PAGE_ROLE |
| `account_url` | text | sim |  |
| `content_collection_stage` | content_collection_stage | não |  |
| `route_state` | text | não |  |
| `identity_resolved_at` | timestamptz | sim |  |
| `last_identity_check_at` | timestamptz | sim |  |

### `company_public_content`

Conteudo publico da conta — tabela prevista, vazia hoje.

> **Por quê:** Prever a entidade sem exigir coleta agora. Existir vazia com a conta em NOT_STARTED e o que permite dizer 'a rota existe e nao correu' em vez de 'nao ha comunicacao'.

`HOSE_ID = H8` · `CANONICAL_PAYLOAD_TYPE = —`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `content_id` 🔑 | text | não |  |
| `account_id` | text | não | → `company_local_account.account_id` |
| `published_at` | timestamptz | sim |  |
| `original_text` | text | sim |  |
| `source_language` | language_code | não |  |
| `evidence_id` | text | sim | → `evidence.evidence_id` |

### `field_pressure_series`

H5 · payload canonico FIELD_PRESSURE_SERIES.

> **Por quê:** Nome canonico (o casco usa LONGITUDINAL_FIELD_SERIES). Serie separada das leituras: sem isso, baseline e coorte virariam colunas repetidas em cada ponto.

`HOSE_ID = H5` · `CANONICAL_PAYLOAD_TYPE = FIELD_PRESSURE_SERIES`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `series_id` 🔑 | text | não |  |
| `country` | char(2) | não |  |
| `region` | text | sim |  |
| `crop_term_id` | text | sim | → `ontology_term.term_id` |
| `issue_term_id` | text | sim | → `ontology_term.term_id` |
| `season_range` | text | sim |  |
| `baseline_kind` | text | sim |  |
| `baseline_state` | field_state | não |  |
| `cohort_state` | field_state | não |  |
| `backtest_state` | field_state | não |  |
| `false_positive_rate` | numeric | sim |  |
| `lead_time_days` | integer | sim |  |
| `independence_from_territorial_state` | field_state | não | SAME_PUBLISHER != INDEPENDENT_OBSERVATION |
| `source_id` | text | não | → `source.source_id` |

### `field_pressure_reading`

Uma leitura da serie. Nunca media sem N.

> **Por quê:** O n viaja com o valor, no mesmo registro. Guardar media agregada sem n foi o erro que o repositorio ja documentou.

`HOSE_ID = H5` · `CANONICAL_PAYLOAD_TYPE = —`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `reading_id` 🔑 | text | não |  |
| `series_id` | text | não | → `field_pressure_series.series_id` |
| `observed_at` | date | sim |  |
| `season` | text | sim |  |
| `value` | numeric | não |  |
| `n` | integer | não | obrigatorio: media nunca viaja sem o n |
| `unit` | text | não |  |
| `province` | text | sim |  |
| `source_id` | text | não | → `source.source_id` |
| `observation_id` | text | sim | → `observation.observation_id` |

- **check `n_positivo`** — `n > 0`

### `person`

Pessoa fisica identificada, com estado GDPR.

> **Por quê:** Supertipo de SCIENTIFIC_PERSON e PERSON_CREATOR. Uma pessoa pode ser as duas coisas, e o tratamento GDPR e da PESSOA, nao do papel.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `person_id` 🔑 | text | não |  |
| `display_name` | text | sim |  |
| `country` | char(2) | sim |  |
| `identity_proved` | boolean | não |  |
| `gdpr_treatment_state` | gdpr_state | não |  |
| `orcid` | text | sim |  |

### `scientific_person`

H7 · payload canonico SCIENTIFIC_PERSON.

> **Por quê:** Nome canonico (o casco usa ISSUE_EXPERT). Pessoa NAO e publicacao — e ISSUE_EXPERT sugere que a expertise e atributo da pessoa, quando e relacao.

`HOSE_ID = H7` · `CANONICAL_PAYLOAD_TYPE = SCIENTIFIC_PERSON`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `person_id` 🔑 | text | não | → `person.person_id` |
| `organization_id` | text | sim | → `organization.organization_id` |
| `relation_to_issue_as_declared` | text | sim |  |
| `source_id` | text | não | → `source.source_id` |

### `scientific_publication`

Subreceptor · a PUBLICACAO, nao o autor.

> **Por quê:** SCIENTIFIC_PERSON != SCIENTIFIC_PUBLICATION. Sem esta tabela, a camada Ciencia de um caso seria preenchida com pessoas, e o produto passaria a dizer que ha ciencia porque encontrou um pesquisador.

`PARENT_HOSE_ID = H7` · `CANONICAL_PAYLOAD_TYPE = SCIENTIFIC_PUBLICATION`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `publication_id` 🔑 | text | não |  |
| `title` | text | não |  |
| `published_at` | date | sim |  |
| `venue` | text | sim |  |
| `peer_reviewed_state` | field_state | não |  |
| `source_language` | language_code | não |  |
| `doi` | text | sim |  |
| `openalex_id` | text | sim |  |
| `abstract_excerpt` | text | sim |  |
| `source_id` | text | não | → `source.source_id` |
| `evidence_id` | text | sim | → `evidence.evidence_id` |

### `publication_author`

N:N entre publicacao e pessoa.

> **Por quê:** Uma pessoa tem muitas publicacoes; uma publicacao tem muitos autores. Nenhum dos dois lados e atributo do outro.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `publication_id` 🔑 | text | não | → `scientific_publication.publication_id` |
| `person_id` 🔑 | text | não | → `person.person_id` |
| `author_position` | integer | sim |  |

### `issue_expertise`

Expertise como RELACAO: pessoa x cultura x problema x evidencia x estado.

> **Por quê:** ISSUE_EXPERTISE_PROVED nao e atributo universal da pessoa. Alguem pode ser autoridade em repilo na oliveira e nao ser em mildio na vinha. Modelar como relacao e o que faz o portao ter dentes — e o que impede contagem de artigos virar autoridade.

`PARENT_HOSE_ID = H7` · `CANONICAL_PAYLOAD_TYPE = —`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `person_id` 🔑 | text | não | → `person.person_id` |
| `crop_term_id` 🔑 | text | não | → `ontology_term.term_id` |
| `issue_term_id` 🔑 | text | não | → `ontology_term.term_id` |
| `issue_expertise_state` | field_state | não |  |
| `evidence_id` | text | sim | → `evidence.evidence_id` |
| `evaluated_at` | timestamptz | não |  |

- **check `expertise_provada_exige_evidencia`** — `(issue_expertise_state <> 'PROVED') OR (evidence_id IS NOT NULL)`

### `person_creator`

H6 · payload canonico PERSON_CREATOR.

> **Por quê:** Nome canonico. PESSOA que cria conteudo publico. Tabela separada de farm_business_entity porque somar as duas num numero chamado CREATORS_READY e proibido — e a inflacao medida foi de 2,6x.

`HOSE_ID = H6` · `CANONICAL_PAYLOAD_TYPE = PERSON_CREATOR`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `person_id` 🔑 | text | não | → `person.person_id` |
| `relation_to_crop_region` | field_state | não |  |
| `source_id` | text | não | → `source.source_id` |

### `farm_business_entity`

H6 · payload canonico FARM_BUSINESS_ENTITY.

> **Por quê:** Nome canonico (o casco abrevia para FARM_BUSINESS). NEGOCIO agricola ou parceiro — nao e pessoa e nao entra em tratamento GDPR de pessoa fisica.

`HOSE_ID = H6` · `CANONICAL_PAYLOAD_TYPE = FARM_BUSINESS_ENTITY`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `business_id` 🔑 | text | não |  |
| `organization_id` | text | sim | → `organization.organization_id` |
| `display_name` | text | sim |  |
| `country` | char(2) | sim |  |
| `relation_to_crop_region` | field_state | não |  |
| `source_id` | text | não | → `source.source_id` |

### `creator_content_profile`

H6 · payload canonico CREATOR_CONTENT_PROFILE.

> **Por quê:** Nome canonico — nao aparece em lugar nenhum do casco index (11). Perfil de canal de uma entidade: uma entidade pode ter varios canais, e canal nao e pessoa.

`HOSE_ID = H6` · `CANONICAL_PAYLOAD_TYPE = CREATOR_CONTENT_PROFILE`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `profile_id` 🔑 | text | não |  |
| `entity_kind` | creator_entity_kind | não |  |
| `person_id` | text | sim | → `person.person_id` |
| `business_id` | text | sim | → `farm_business_entity.business_id` |
| `platform` | text | não |  |
| `channel_ref` | text | sim |  |
| `last_observed_at` | timestamptz | sim |  |
| `source_id` | text | não | → `source.source_id` |

- **check `perfil_pertence_a_exatamente_uma_entidade`** — `(person_id IS NOT NULL)::int + (business_id IS NOT NULL)::int = 1`
- **check `kind_bate_com_a_entidade`** — `(entity_kind = 'PERSON_CREATOR' AND person_id IS NOT NULL) OR (entity_kind = 'FARM_BUSINESS_ENTITY' AND business_id IS NOT NULL)`

### `field_voice_observation`

Subreceptor · o que a voz de campo DISSE.

> **Por quê:** Entidade != observacao. Sem esta tabela, voz de campo e uma lista de nomes — e nome nao e sinal.

`PARENT_HOSE_ID = H6` · `CANONICAL_PAYLOAD_TYPE = FIELD_VOICE_OBSERVATION`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `observation_id` 🔑 | text | não | → `observation.observation_id` |
| `profile_id` | text | sim | → `creator_content_profile.profile_id` |
| `entity_kind` | creator_entity_kind | não |  |
| `platform` | text | não |  |
| `country` | char(2) | sim |  |
| `crop_mentioned_term_id` | text | sim | → `ontology_term.term_id` |
| `issue_mentioned_term_id` | text | sim | → `ontology_term.term_id` |
| `region_mentioned` | text | sim |  |
| `content_entity_id` | text | sim | → `content_entity.canonical_entity_id` · o texto original vive em content_entity |
| `relation_to_issue_state` | field_state | não |  |
| `gdpr_treatment_state` | gdpr_state | não |  |

- **check `pessoa_identificada_exige_gdpr_tratado`** — `(entity_kind <> 'PERSON_CREATOR') OR (gdpr_treatment_state <> 'NOT_STARTED')`

### `local_adama_portfolio_context`

Subreceptor · a ADAMA tem resposta registrada para este alvo neste pais?

> **Por quê:** REGISTRATION_DEADLINE != LOCAL_ADAMA_PORTFOLIO_CONTEXT. Sem esta tabela, alguem liga H2 aqui e o portal passa a dizer que a ADAMA tem produto porque um registro de qualquer titular tem prazo. Portfolio e CONTEXTO, nunca evidencia do fenomeno.

`PARENT_HOSE_ID = H2` · `CANONICAL_PAYLOAD_TYPE = LOCAL_ADAMA_PORTFOLIO_CONTEXT`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `context_id` 🔑 | text | não |  |
| `country` | char(2) | não |  |
| `crop_term_id` | text | sim | → `ontology_term.term_id` |
| `issue_term_id` | text | sim | → `ontology_term.term_id` |
| `registered_response_state` | field_state | não |  |
| `label_authorizes_target_state` | field_state | não |  |
| `source_id` | text | não | → `source.source_id` |
| `is_context_not_evidence` | boolean | não |  |

- **check `portfolio_e_sempre_contexto`** — `is_context_not_evidence = true`

### `portfolio_product_ref`

Produtos ADAMA e registros que sustentam o contexto de portfolio.

> **Por quê:** N:N. Um contexto pode ser sustentado por varios produtos e registros; nenhum deles vira coluna repetida.

`PARENT_HOSE_ID = H2` · `CANONICAL_PAYLOAD_TYPE = —`

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `context_id` 🔑 | text | não | → `local_adama_portfolio_context.context_id` |
| `product_id` 🔑 | text | sim | → `product.product_id` |
| `registration_id` 🔑 | text | sim | → `registration.registration_id` |

### `convergence_proposition`

A proposicao unica que as pernas sustentam.

> **Por quê:** CONVERGENCE_REQUIRES = SAME_PROPOSITION + INDEPENDENT_EVIDENCE. Sem a proposicao como entidade, duas evidencias sobre assuntos parecidos viram convergencia.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `proposition_id` 🔑 | text | não |  |
| `attention_object_id` | text | não | → `attention_object.attention_object_id` |
| `proposition_text` | text | não |  |
| `convergence_kind` | convergence_kind | não |  |
| `created_at` | timestamptz | não |  |

> ⚠️ INDEPENDENT_FAMILY_COUNT nao existe como coluna. E derivado na view v_convergence_state. Um contador manual pode divergir das pernas — e foi assim que cinco das seis convergencias da V1 viraram uma so.

### `convergence_leg`

Uma perna da convergencia, com sua independencia tipada.

> **Por quê:** DEPENDENCY_RELATION e o campo que impede dupla contagem. Sem ele, a perna Meta da cadeia e o anuncio da Meta contariam como duas familias.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `leg_id` 🔑 | text | não |  |
| `proposition_id` | text | não | → `convergence_proposition.proposition_id` |
| `signal_family` | signal_family | não |  |
| `evidence_id` | text | não | → `evidence.evidence_id` |
| `source_id` | text | não | → `source.source_id` |
| `observed_at` | date | sim |  |
| `independence_state` | independence_state | não |  |
| `dependency_type` | dependency_type | não |  |
| `depends_on_leg_id` | text | sim | → `convergence_leg.leg_id` |
| `dependency_note` | text | sim |  |

- **check `dependente_declara_o_tipo_e_o_alvo`** — `(independence_state <> 'DEPENDENT') OR (dependency_type <> 'INDEPENDENT_SOURCE' AND depends_on_leg_id IS NOT NULL)`
- **check `independente_nao_tem_alvo`** — `(independence_state <> 'INDEPENDENT') OR (depends_on_leg_id IS NULL)`

### `dependency_edge`

O grafo de dependencia tipado, entre quaisquer dois sinais.

> **Por quê:** As 17 relacoes medidas do refresh precisam existir fora da convergencia de um objeto: H3 depende de H4 por DERIVATION_DEPENDENCY e H5 depende de H1 por SOURCE_DEPENDENCY sao propriedades do SISTEMA, nao de um caso.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `edge_id` 🔑 | bigint | não |  |
| `from_kind` | text | não | SIGNAL_FAMILY | HOSE | EVIDENCE | OBSERVATION | ENTITY |
| `from_id` | text | não |  |
| `to_kind` | text | não |  |
| `to_id` | text | não |  |
| `dependency_type` | dependency_type | não |  |
| `why` | text | não |  |
| `evidence_id` | text | sim | → `evidence.evidence_id` |

### `object_relation`

Cruzamentos entre objetos de atencao.

> **Por quê:** O bloco 'o que liga a outros objetos' precisa de aresta propria, com tipo — nunca inferida por semelhanca de texto.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `relation_id` 🔑 | bigint | não |  |
| `from_object_id` | text | não | → `attention_object.attention_object_id` |
| `to_object_id` | text | não | → `attention_object.attention_object_id` |
| `relation_kind` | text | não |  |
| `dependency_type` | dependency_type | sim |  |
| `evidence_id` | text | sim | → `evidence.evidence_id` |

- **check `objeto_nao_se_relaciona_consigo`** — `from_object_id <> to_object_id`

### `object_event`

A timeline do objeto. STATE_BEFORE e STATE_AFTER separados.

> **Por quê:** Guardar 'FORMING -> ATTENTION_CANDIDATE_TEST' como string impede filtrar, agregar e reconstruir. A seta e apresentacao e vive numa view.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `event_id` 🔑 | text | não |  |
| `attention_object_id` | text | não | → `attention_object.attention_object_id` |
| `event_type` | event_type | não |  |
| `event_at` | timestamptz | sim | NULL quando o evento e um vazio temporal |
| `event_at_resolution` | time_resolution | não |  |
| `source_id` | text | sim | → `source.source_id` |
| `observation_id` | text | sim | → `observation.observation_id` |
| `state_before` | attention_state | sim |  |
| `state_after` | attention_state | sim |  |
| `what_changed` | text | não |  |
| `signal_family_added` | signal_family | sim |  |
| `gap_reason` | text | sim |  |
| `trigger_id` | text | sim |  |

- **check `mudanca_de_estado_exige_os_dois_estados`** — `(event_type <> 'STATE_CHANGE') OR (state_after IS NOT NULL)`
- **check `vazio_temporal_declara_o_motivo`** — `(event_type <> 'GAP') OR (gap_reason IS NOT NULL)`
- **check `sem_data_sem_precisao`** — `(event_at IS NOT NULL) OR (event_at_resolution = 'NOT_KNOWN')`

### `action`

Uma acao por area, com tipo canonico.

> **Por quê:** ACTION_TYPE persistido e BUSINESS_DECISION / SYSTEM_DECISION / INVESTIGATION. BUSINESS e SYSTEM sao rotulos de tela e ficam em ui_alias.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `action_id` 🔑 | text | não |  |
| `attention_object_id` | text | não | → `attention_object.attention_object_id` |
| `department` | department | não |  |
| `action_type` | action_type | não |  |
| `action_state` | field_state | não |  |
| `action_text` | text | não |  |
| `why_text` | text | sim |  |
| `time_horizon` | text | sim |  |
| `is_central_area` | boolean | não |  |
| `regional_owner` | text | sim |  |
| `is_publishable` | boolean | não | derivado pelo publisher: BUSINESS_DECISION sem base de evidencia nao publica |

### `action_evidence`

EVIDENCE_BASIS como relacao N:N.

> **Por quê:** Uma acao pode se apoiar em varias evidencias e uma evidencia sustenta varias acoes. A regra 'BUSINESS_DECISION sem base nao publica' se verifica contando linhas aqui — nao confiando num campo.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `action_id` 🔑 | text | não | → `action.action_id` |
| `evidence_id` 🔑 | text | não | → `evidence.evidence_id` |

### `entry_path_event`

Telemetria minima de como o usuario chegou a capability Creator.

> **Por quê:** A arbitragem decidiu que Creator vira ferramenta com DADO DE USO, nao com estetica. Sem esta tabela a decisao nunca pode ser tomada. Guarda so a rota e o recorte — sem PII, sem identificador de usuario.

`PARENT_HOSE_ID = H6` · `CANONICAL_PAYLOAD_TYPE = —`

**Privacidade:** sem user_id, sem sessao, sem IP. So a rota, o recorte e a hora.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `event_id` 🔑 | bigint | não |  |
| `entry_path` | entry_path | não |  |
| `attention_object_id` | text | sim | → `attention_object.attention_object_id` |
| `crop_term_id` | text | sim | → `ontology_term.term_id` |
| `region` | text | sim |  |
| `country` | char(2) | sim |  |
| `occurred_at` | timestamptz | não |  |

- **check `rota_do_objeto_exige_objeto`** — `(entry_path <> 'FROM_ATTENTION_OBJECT') OR (attention_object_id IS NOT NULL)`

### `publish_run`

Uma execucao do publisher, com versao e freezes.

> **Por quê:** Responde 'qual versao do pipeline colocou este objeto aqui, e com quais freezes'. Sem isso, o Supabase vira um estado sem historia.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `publish_run_id` 🔑 | text | não |  |
| `pipeline_version` | text | não |  |
| `schema_version` | text | não |  |
| `published_at` | timestamptz | não |  |
| `status` | publish_status | não |  |
| `shadow_validation_passed` | boolean | não |  |
| `failed_reason` | text | sim |  |

- **check `publicado_exige_sombra_aprovada`** — `(status <> 'PUBLISHED') OR (shadow_validation_passed = true)`

### `publish_run_freeze`

Os commits congelados que alimentaram a execucao.

> **Por quê:** Uma execucao pode ler varios freezes. Guardar N:N torna a pergunta 'de que commit veio esta linha' respondivel.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `publish_run_id` 🔑 | text | não | → `publish_run.publish_run_id` |
| `repository` 🔑 | text | não |  |
| `path` 🔑 | text | não |  |
| `commit_sha` 🔑 | char(40) | não |  |
| `hose_id` | text | sim |  |

### `shadow_validation`

O resultado da comparacao freeze x Supabase, familia por familia.

> **Por quê:** Contagem igual nao prova semantica igual. Cada verificacao fica registrada com o que se esperava e o que se achou.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `validation_id` 🔑 | bigint | não |  |
| `publish_run_id` | text | não | → `publish_run.publish_run_id` |
| `family` | text | não |  |
| `check_name` | text | não |  |
| `expected` | text | sim |  |
| `found` | text | sim |  |
| `passed` | boolean | não |  |
| `checked_at` | timestamptz | não |  |

### `ui_alias`

Os aliases de apresentacao, declarados e separados do tipo canonico.

> **Por quê:** O index (11) usa oito nomes divergentes. Guardar o mapa aqui e o que permite o adapter traduzir SEM que o alias vire tipo persistido — e o que torna a divergencia visivel em vez de silenciosa.

| coluna | tipo | nulo | nota |
|---|---|---|---|
| `canonical_type` 🔑 | text | não |  |
| `hose_id` | text | sim |  |
| `ui_alias` | text | sim |  |
| `alias_source` | text | não |  |
| `note` | text | sim |  |

---

## VIEWS

### `v_convergence_state`

Deriva INDEPENDENT_FAMILY_COUNT e CONVERGENCE_STATE das pernas.

> **Por quê:** A contagem NUNCA e coluna. Contar familias distintas entre pernas INDEPENDENT e o que produz SINGLE_SIGNAL com duas pernas quando uma depende da outra.

**Lê:** `convergence_proposition`, `convergence_leg`

**Deriva:** `independent_family_count`, `convergence_state`

### `v_attention_readiness`

Recalcula ATTENTION_READY a partir dos cinco requisitos.

> **Por quê:** O estado publicado tem de ser reproduzivel. Se algum requisito nao estiver PROVED, o objeto nao e READY — e a view diz qual portao segurou.

**Lê:** `attention_object`, `attention_readiness`

**Deriva:** `computed_is_ready`, `blocking_requirements`

### `v_attention_feed`

Fila de atencao por pais, com o motivo quando vazia.

**Lê:** `attention_object`, `v_attention_readiness`, `attention_object_representation`

### `v_radar`

Cards do radar: tipo, pais, estado, bloqueador, ultima evidencia.

**Lê:** `attention_object`, `attention_object_representation`, `attention_readiness`

### `v_object_detail`

Objeto + tabela filha do tipo + relogios + desconhecidos.

**Lê:** `attention_object`, `phenomenon_case`, `regulatory_deadline_object`, `competitor_identity_chain_object`, `longitudinal_field_pressure_object`, `object_clock`, `attention_object_unknown`

### `v_evidence_drawer`

Evidencia + proveniencia dos dois backends + original e traducao separados.

> **Por quê:** O mesmo formato para GITHUB e SUPABASE. A UI nao sabe de qual veio.

**Lê:** `evidence`, `source`, `source_provenance`, `storage_provenance`, `content_entity`, `content_translation`

### `v_crop_map_point`

Pontos do mapa, ja filtrados por resolucao desenhavel.

> **Por quê:** A view devolve is_drawable derivado de GEO_RESOLUTION = POINT com geometria. O cliente nao decide isso sozinho.

**Lê:** `attention_object`, `geo_anchor`, `phenomenon_case`

**Deriva:** `is_drawable`, `undrawable_reason`

### `v_object_timeline`

Timeline com a seta de apresentacao montada aqui.

> **Por quê:** STATE_BEFORE -> STATE_AFTER e string SO nesta view. No banco os dois sao colunas.

**Lê:** `object_event`

**Deriva:** `state_transition_label`

### `v_action_map`

Acoes com contagem de base de evidencia.

> **Por quê:** Deriva is_defensible: BUSINESS_DECISION com zero linhas em action_evidence nao e defensavel.

**Lê:** `action`, `action_evidence`

**Deriva:** `evidence_basis_count`, `is_defensible`

### `v_eame_cross_market`

Camada regional: so as dimensoes declaradas comparaveis.

> **Por quê:** Cruzar so onde ha comparabilidade declarada. Uma view que juntasse tudo fabricaria uniformidade.

**Lê:** `attention_object`, `object_relation`, `field_pressure_series`

### `v_source_status`

Os cinco relogios por fonte, sem agregacao.

**Lê:** `source`, `source_clock`, `source_snapshot`

### `v_issue_expert`

Pessoas com expertise PROVADA no par cultura x problema.

> **Por quê:** Filtra pelo portao. Quem nao passou nao aparece como especialista do problema — e a view nao ordena por contagem de nada.

**Lê:** `person`, `scientific_person`, `issue_expertise`

### `v_publish_provenance`

De um objeto ate o commit do freeze que o produziu.

> **Por quê:** PROVENANCE_REACHES_SOURCE_FREEZE, verificavel em uma consulta.

**Lê:** `attention_object`, `publish_run`, `publish_run_freeze`, `storage_provenance`

---

## RPCs

### `get_attention_object(p_object_id text, p_display_language language_code)`

Objeto + representacao no idioma pedido, com fallback explicito.

**Retorna:** `object`, `representation`, `requested_language`, `display_language`, `fallback_used`

> **Por quê:** O V8 nao monta a inteligencia com dezessete joins no navegador. E o fallback e declarado, nunca fingido.

### `get_attention_feed(p_country char(2), p_display_language language_code)`

Fila de atencao do pais, com o motivo quando vazia.

**Retorna:** `items`, `empty_reason`, `blocking_gate_counts`

### `get_evidence(p_evidence_id text, p_display_language language_code)`

Gaveta de evidencia completa, com original preservado.

**Retorna:** `evidence`, `source_provenance`, `storage_provenance`, `original_text`, `source_language`, `translation`, `fallback_used`

### `resolve_representation(p_entity_id text, p_requested_language language_code)`

Politica de fallback de idioma, num lugar so.

**Retorna:** `language`, `text`, `requested_language`, `fallback_used`, `fallback_chain`

> **Por quê:** Uma implementacao, nao uma por view. Se FR nao existe, devolve EN dizendo que devolveu EN.

---

## POLÍTICA DE FALLBACK DE IDIOMA

```
CADEIA: <requested> → en → pt
```

Nunca fabricar traducao. Se nenhuma lingua da cadeia existir, devolver NULL com FALLBACK_USED = NO_REPRESENTATION_AVAILABLE.

**Sempre declarado:** REQUESTED_LANGUAGE · DISPLAY_LANGUAGE · FALLBACK_USED

**Nunca:** fingir que FR existe porque EN existe

**Evidência:** ORIGINAL_TEXT nunca entra na cadeia de fallback: ele e exibido na lingua da fonte, sempre.

---

## NÚMEROS DE LEDGER

Numero de ledger nao se duplica em tabela. Deriva-se por consulta e compara-se com o dono.

```
RAIF_SEASONS_AVAILABLE   = 23        deriva de: count(distinct season) em field_pressure_reading do series RAIF
RAIF_READINGS_TOTAL      = 148964    deriva de: count(*) em field_pressure_reading do series RAIF
```

**Onde mora a verdade:** scripts/metricas_canonicas.py. O Supabase reproduz; nao redefine.

