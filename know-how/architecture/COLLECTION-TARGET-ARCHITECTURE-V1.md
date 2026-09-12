# SINTONIA EAME — COLLECTION TARGET ARCHITECTURE V1

> Registro durável da consolidação transversal pós-censo. Não é a Bíblia e ainda não é implementação. É a arquitetura-alvo derivada do censo completo da Collection.

## FONTES

```text
REPO = lucianodalondon-sys/eame-sintonia
CENSUS_HEAD = 572647dce8a38b8835aafa6f9e3e42d2652fbcd9
KNOW_HOW_SOURCE_COMMIT = 6fca4ad2ebe861ca3df2cb4c582c1704d9766926
CARD_CONTRACT_SOURCE_HEAD = bee7d6af73531b678697dc7f5e9063d597652b47
CENSUS = 64 / 64 nós explicados
```

## ESTADO DA DECISÃO

```text
TARGET_ARCHITECTURE_CLOSED = YES, com correções pré-implementação obrigatórias abaixo
CANONICAL_CONTROL_PLANE_DEFINED = YES
CANONICAL_DATA_PLANE_DEFINED = YES
COLLECTION_BOUNDARY_DEFINED = YES
READY_WAITING_ROOM_DEFINED = YES
CORE_EAME_COUNTRY_SEPARATED = YES
READY_FOR_IMPLEMENTATION_PLAN = YES
```

`READY_FOR_IMPLEMENTATION_PLAN` não autoriza mudança de runtime.

## PRINCÍPIO CENTRAL

A Collection deve ter uma espinha única e encerrar em Waiting Room:

```text
CONTROL
TRIGGER → REQUEST → PLAN/POLICY → ORCHESTRATOR → ROUTE POLICY → EXECUTOR

DATA
SOURCE → EXECUTOR/ADAPTER → CANONICAL INGRESS → RAW → DERIVED
       → STRUCTURED → ADMISSION → READY → WAITING_FOR_INTELLIGENCE
```

Intelligence não é consumidora durante o fechamento da Collection.

## TARGET DE RESPONSABILIDADES

A consolidação propôs:

```text
TARGET_COLLECTION_COMPONENTS = 44
TARGET_GOVERNANCE = 5
TARGET_PROOF_MEASURE = 8
TARGET_REFERENCE_DATA = 3
TARGET_EXTERNAL_REPRESENTATIONS = 5
```

O número não é meta. Ele nasce de `ONE QUESTION → ONE OWNER`.

### Owners críticos do alvo

```text
T-01 COLLECTION-TRIGGER
T-02 COLLECTION-REQUEST
T-03 COLLECTION-PLAN-POLICY
T-04 COLLECTION-ORCHESTRATOR
T-05 ROUTE-POLICY
T-06 EXECUTOR-REGISTRY
T-07 RUN-PROVENANCE

T-20 CANONICAL-INGRESS
T-21 RAW-OWNER
T-30 DERIVED-OWNER
T-32 UNIT-FORWARD-LINEAGE-RUNNER
T-40 DOCUMENT-SEMANTIC-EXTRACTOR
T-41 REGULATORY-REGISTER-OWNER
T-42 CONTENT-FINDINGS-OWNER
T-50 ADMISSION
T-52 READY-OWNER / WAITING ROOM

T-60 DOCUMENT-READER
T-61 TRANSCRIPTION
T-62 CONTENT-TRIAGE-ENGINE
T-63 COLLECTION-LEXICON

T-70 SOURCE-ONBOARDING
T-71 SOURCE-REGISTRY / SOURCE_ID OWNER
T-72 SOURCE-CONTRACTS
T-73 SOURCE-SELECTION-POLICY
T-74 PLATFORM-REGISTRY
T-75 ACCOUNT-IDENTITY
T-76 CHANNEL-IDENTITY
T-77 PERSON-IDENTITY
T-80 SCIENTIFIC-WORK-CORPUS
T-81 COUNTRY-PORTFOLIO-REGISTRY

T-90 TELEMETRY-BOUNDARY
T-91 TRACE-OWNER
T-92 SOURCE-HEALTH
T-95 CANONICAL-SCHEMA
T-96 IMPORT-APPLIER
```

## RAW — LEI DE OWNERSHIP

O meio físico pode ser plural; o livro e a autoridade não.

```text
RAW_OWNER = T-21
RAW_LEDGER = public.raw_asset
RAW_BYTES = storage locator portável (Storage / Git de piloto / disco operacional)
WRITER_TARGET = 1 autoridade, alcançada por T-20
```

### CORREÇÃO PRÉ-IMPLEMENTAÇÃO OBRIGATÓRIA — IDENTIDADE RAW

A consolidação original escreveu `RAW_ID + sha256 + (run_id, storage_path)` perto da identidade. Isso não deve virar contrato literalmente.

Regra correta:

```text
RAW_OBSERVATION_ID = identidade da captura/observação preservada
CONTENT_SHA256 = fingerprint/identidade do conteúdo para dedupe e integridade
STORAGE_LOCATOR = endereço físico; NUNCA identidade
SOURCE_ID / RUN_ID / CAPTURED_AT = proveniência da observação
```

O mesmo byte pode ser observado em corridas diferentes. Portanto `sha256` sozinho não identifica a ocorrência, e `storage_path` nunca deve entrar na identidade semântica.

## DERIVED — UM LIVRO

Hoje existem dois livros:

```text
data/derivados/REGISTO-DE-ARTEFATOS.json
public.derived_artifact
```

Alvo:

```text
CANONICAL_DERIVED_LEDGER = public.derived_artifact
OWNER = T-30
```

O registro Git pode permanecer durante migração como cache/proof artifact, mas perde autoridade.

Campos obrigatórios:

```text
DERIVED_ID
PARENT_ID
PARENT_SHA
CHILD_SHA
RUN_ID
EXECUTOR_ID
EXECUTOR_VERSION
PARAMETERS_HASH
SPECIES
```

`TEXT_EXTRACTION`, `MANUAL_TEXT`, `SEARCHABLE_TEXT`, `TRANSLATION` e `TRANSCRIPT` são espécies diferentes.

## STRUCTURED

Não precisa de um owner global.

Regra:

> ONE STRUCTURED CONCEPT → ONE OWNER.

Casos centrais:

```text
T-40 documento/campos semânticos
T-41 registro_regulatorio
T-42 content findings
T-80 scientific work
T-81 portfolio local
T-75/T-76/T-77 identidades
```

`SQL_GENERATOR != SQL_APPLIER != DB_WRITER` permanece regra obrigatória.

## ADMISSION

```text
OWNER = T-50
CALLER ALVO = T-32, e mais ninguém
DECISION_IDENTITY = determinística por item + universo + versão da regra
LEDGER = public.admission_decision
```

A lista aceita pelo Ingresso é a única que pode seguir. Item sem RAW preservado não deve ser julgado como se tivesse entrado normalmente.

Estados permanecem distintos:

```text
SIM
NAO
NAO_SEI
NAO_SE_APLICA
ERRO
```

## READY / WAITING ROOM

```text
OWNER = T-52
READY_ID = 1:1 com decisão SIM de Admission
TARGET STORE = public.ready_item
STATE = WAITING_FOR_INTELLIGENCE
READY_CONSUMER_COUNT = 0 enquanto a Collection fecha
```

READY deixa de ser função em um lugar + writer em outro. O owner constrói e persiste.

## BYPASSES

A consolidação mediu oito leituras diretas Collection → `motor/`.

Alvo:

```text
COLLECTION_TO_INTELLIGENCE_DATA_BYPASSES = 0
```

Leitura legítima de lexicon/reference data precisa ser declarada como referência, não disfarçada de dado colhido.

## SOCIAL / PLATAFORMA

Há três autoridades atuais:

```text
social_matriz = 11 plataformas
social_persistencia = 9
System Map CANAIS = 4 sociais + HTTP
```

Alvo:

```text
T-74 = autoridade canônica de PLATFORM
ACCOUNT = T-75
CHANNEL = T-76
SOURCE_ID = T-71
TRANSPORT = eixo ortogonal; HTTP não é plataforma
TOOL = T-15
ROUTE POLICY = T-05
ADAPTER = T-13
```

`V-YOUTUBE` etc. podem continuar sintéticos. `V-HTTP` é protocolo/transporte.

## CONTENT TRIAGE

```text
ACQUISITION → MEDIA/CAPTION/TRANSCRIPT → TRANSCRIPTION → CONTENT TRIAGE
            → STRUCTURED FINDINGS → ADMISSION
```

Alvo:

```text
TRANSCRIPTION = T-61
CONTENT TRIAGE ENGINE = T-62 CORE
LEXICON = T-63 COUNTRY/EAME overlay
```

Não duplicar cérebro semântico por plataforma ou país.

## DOCUMENTOS

```text
T-60 DOCUMENT-READER = obter conteúdo
T-40 DOCUMENT-SEMANTIC-EXTRACTOR = atribuir campos/significado
T-30 TRANSLATION/DERIVATION = nova representação com pai
```

Leitura, extração semântica e tradução não são a mesma responsabilidade.

## PORTABILIDADE

Novo país não recria o SINTONIA.

Reutiliza o CORE e fornece principalmente:

```text
sources
accounts/canais
endpoints
contratos locais
portfólio/rótulos locais
léxico/recortes
adapter regulatório local
conformidade do país
```

Motores, Ingress, RAW/DERIVED, Admission, READY, telemetry, reader, transcription, triage e proof framework tendem a CORE.

## GOVERNANCE / PROOF / REFERENCE DATA

Alvo fora da esteira operacional:

```text
G-01 BIBLE
G-02 LAW-MACHINE-INTERFACE
G-03 CONFORMITY-<COUNTRY>
G-04 LESSON-REGISTRY
G-05 COLLECTION-POLICY

P-01..P-08 PROOF / MEASURE / TEST INFRA

R-01 EU-REGULATORY-APPROVAL
R-02 MOA-RESISTANCE
R-03 EU-OPEN-DATA
```

Bíblia, test double, censos e relatório não são passos da Collection.

## ORDEM DE MIGRAÇÃO

```text
PHASE 0   contratos/arquitetura e resolução de blockers
PHASE A   control plane
PHASE B   canonical ingress + RAW
PHASE B'  SOURCE_ID / identity antes do processo
PHASE C   DERIVED → STRUCTURED → ADMISSION → READY → Waiting Room
PHASE D   readers / transcription / content triage / adapters
PHASE E   observability / proof / runtime gates
PHASE F   E2E real até Waiting Room
PHASE G   System Map final, derivado da realidade
```

### System Map durante a implementação

O mapa não deve ser editado manualmente para fazer a arquitetura parecer pronta. Porém o repositório já possui seals/gates que podem exigir regeneração quando arquivos tracked mudam.

Regra operacional para o plano de implementação:

> Se CI exigir map regeneration durante uma fase, regenerar mecanicamente como consequência do runtime daquele checkpoint. Não redesenhar o mapa à mão. A regeneração final completa continua na Phase G.

Isso evita tanto mapa mentiroso quanto branches permanentemente vermelhas por seal stale.

## PORTÕES FINAIS

```text
CANONICAL_COLLECTION_STARTS = 1
CANONICAL_ORCHESTRATION_OWNER = 1
CANONICAL_ROUTE_AUTHORITY = 1
CANONICAL_INGRESS = 1
RAW_OWNER = 1
DERIVED_OWNER = 1
STRUCTURED_OWNER_PER_CONCEPT = YES
ADMISSION_OWNER = 1
READY_OWNER = 1
UNAUTHORIZED_DATA_BYPASSES = 0
COLLECTION_TO_INTELLIGENCE_DATA_BYPASSES = 0
DUPLICATE_AUTHORITY_UNRESOLVED = 0
UNOWNED_CRITICAL_STATE = 0
LINEAGE_LOST = 0
FACT_TIME_FABRICATED = 0
FACT_LOCATION_FABRICATED = 0
REAL_END_TO_END_ITEM >= 1
RAW = PROVED
DERIVED = PROVED
STRUCTURED = PROVED
ADMISSION = PROVED
READY = PROVED
READY_CONSUMER_COUNT = 0
FINAL_STATE = WAITING_FOR_INTELLIGENCE
```

Portões adicionais aprendidos no censo:

```text
MODULE_LOADS_AT_HEAD = 100%
PROOF_SEES_ALL_WRITE_MECHANISMS = YES
ABSOLUTE_LOCAL_PATH_AS_ONLY_LOCATOR = 0
SOURCE_ID_WITHOUT_OWNER = 0
OUTPUT_WITHOUT_CONSUMER = 0 OR DECLARED_DEAD_END
GENERATED_ARTIFACT_WITHOUT_PROVENANCE = 0
```

## QUESTÕES QUE NÃO DEVEM SER VARrIDAS PARA BAIXO DO TAPETE

### A-01 · versão da Bíblia / CT-08

Censo lê V1.3/104 leis; Card Contract branch leva Bíblia a V1.4 com COL-LAW-601..617. Antes de integrar Phase 0, reconciliar qual snapshot vira autoridade. Não escolher silenciosamente.

### A-02 · T-80 OpenAlex/ORCID

Ainda precisa decidir se OpenAlex/ORCID entram na espinha como acquisition `EXTERNAL → T-20 → T-21` ou se são reference data declarada. Não implementar T-80 antes dessa classificação.

### A-03 · contabilização de MERGE

A consolidação mapeia `C-SINTONIA-SCRAP → T-01` como MERGE, além de `C-DERIVACAO-FORWARD` e `C-ROTA-M2` convergirem em T-32; `C-ESTRADA-PDF` contribui apenas com um segmento e continua SPLIT como ação primária.

Portanto o plano deve ter uma tabela nominal current→target e não depender só do contador agregado `MERGE = 3`, que pode ser lido de forma ambígua.

### A-04 · escolha do PDF reader

Não escolher ainda. Medir taxa de sucesso, fidelidade de layout e custo antes de eleger implementação canônica de T-60.

## REGRA PARA A PRÓXIMA MISSÃO

A próxima missão é PLANO DE IMPLEMENTAÇÃO, não implementação.

Ela deve converter cada phase em commits/checkpoints/gates pequenos, declarar branch/base e ordem de dependência, resolver A-01/A-03 e contratos fundamentais de identidade antes do primeiro mutation de runtime, e manter `NÃO SEI` para medições que não bloqueiam a fase atual.

> PROMPT CURTO → EXECUÇÃO LONGA → VERIFICAÇÃO FORTE.
