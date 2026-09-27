# C-PLAN-A3 — STRUCTURED POR ESPÉCIE

> Registro durável do fechamento pré-implementação do dispatch de STRUCTURED e do contrato de `NOT_APPLICABLE`. Não é implementação e não substitui a Bíblia.

## CHECKPOINT

```text
REPO = lucianodalondon-sys/eame-sintonia
WORK_BRANCH = claude/raw-observation-identity-3jbwco
INITIAL_HEAD = 1d707d31ea3142c51fcb7a073ccb291c0933ac27
FINAL_HEAD = 2498b7e89d1d1170761bd99a27f0c354dd73117d
RUNTIME_FILES_CHANGED = 0
MIGRATIONS_CHANGED = 0
DATABASE_MUTATIONS = 0
BIBLE_CHANGED = 0
SYSTEM_MAP_CHANGED = 0
SUBAGENTS = 0
```

Documento de origem no ramo de trabalho:

```text
docs/operacao/STRUCTURED-POR-ESPECIE-E-NOT-APPLICABLE.md
```

## O ACHADO CENTRAL

STRUCTURED não é uma unidade universal. O censo limitado encontrou várias espécies com writers e identidades diferentes. O T-32 estava ligado somente a `SOCIAL_CONTENT`, justamente a espécie que exige `canal_id`, e por isso o teste de PDF precisou fabricar uma organização/canal para encaixar um boletim num modelo social.

```text
SOCIAL_CONTENT           public.conteudo                 writer existente
SOCIAL_COMMENT           public.comentario               writer existente
SOCIAL_TRANSCRIPT        public.transcricao              conceito existe; writer não provado nesta casa
REGULATORY_REGISTRATION  public.registro_regulatorio     writer existente
CATALOG_PRODUCT_DOCUMENT public.catalogo_produto_documento writer existente
OFFICIAL_BULLETIN        sem owner/store atual
TABULAR_MEASUREMENT      sem owner/store atual
```

Regra de Know How:

> `STRUCTURED` é uma etapa, não uma tabela universal. A espécie estruturada deve ser declarada antes da execução e cada conceito estruturado deve ter um owner próprio.

## QUEM ESCOLHE A ESPÉCIE

A decisão fechada foi:

```text
STRUCTURED_TARGET_SELECTION_OWNER = CONTRATO DE FONTE
T32_SELECTS_STRUCTURED_CONCEPT = NO
T32_GUESSES_STRUCTURED_FROM_FIELDS = NO
T32_GUESSES_SOCIAL_FROM_CHANNEL = NO
```

Motivo: o contrato de fonte é a autoridade pré-execução por fonte. Pedido conhece universo; Plano conhece executor; Orquestrador coordena; executor já está tarde demais; writer é destino e não se elege a si próprio.

`EVIDENCE_CLASS` foi medido e rejeitado como chave de dispatch: possui texto livre, valores compostos e descreve peso probatório, não a espécie de registro.

O contrato alvo precisa declarar um campo fechado equivalente a:

```text
STRUCTURED_TARGET
```

que então resolve por um registry:

```text
STRUCTURED_TARGET -> owner/writer
```

Sem alvo declarado: falha nomeada, sem fallback. Alvo declarado sem writer conectado: `OWNER_NOT_CONNECTED` ou equivalente canônico.

## QUATRO CLASSES DE TRAVESSIA

```text
A PDF/documento
RAW bytes
→ DERIVED TEXT_EXTRACTION
→ STRUCTURED OFFICIAL_BULLETIN
→ Admission
CURRENT OWNER/STORE = AUSENTE

B social com texto nativo
RAW payload
→ DERIVED NOT_APPLICABLE
→ STRUCTURED SOCIAL_CONTENT
→ Admission
CURRENT OWNER = social_persistencia.py

C legenda buscada da plataforma
RAW caption/fetch
→ DERIVED NOT_APPLICABLE
→ STRUCTURED SOCIAL_TRANSCRIPT
→ Admission
CURRENT CONCEPT EXISTS; WRITER = AUSENTE

D tabular normalizado
RAW bytes
→ DERIVED NOT_APPLICABLE
→ STRUCTURED TABULAR_MEASUREMENT
→ Admission
CURRENT OWNER/STORE = AUSENTE
```

A distinção crítica permanece:

> legenda buscada da plataforma = RAW; machine transcription feita por nós = DERIVED.

Não fabricar pai DERIVED quando a etapa não aconteceu.

## CHANNEL_ID NÃO É IDENTIDADE DE DOCUMENTO

Foi corrigida uma suspeita: `public.conteudo` possui `raw_asset_id`, então a linhagem para RAW existe. O defeito real é `canal_id NOT NULL`.

Regra de Know How:

> Um documento/boletim não deve fabricar organização, canal ou identidade social para entrar numa tabela de conteúdo social. `CHANNEL_ID_REQUIRED_FOR_DOCUMENT` deve ser `NO` no alvo.

## NOT_APPLICABLE

O estado já existe na lei e no enum do banco, mas a razão não tem suporte persistente simétrico ao `FAIL`.

Contrato alvo mínimo:

```text
STATE = NOT_APPLICABLE
REASON_CODE
REASON_TEXT
PREVIOUS_REAL_STAGE = edge_from
PREVIOUS_REAL_ARTIFACT_ID = last_good_artifact
```

Regra:

```text
NOT_APPLICABLE sem razão = INVALID
NOT_APPLICABLE != NOT_RUN
NOT_APPLICABLE != FAIL
NOT_APPLICABLE != UNKNOWN
```

`EVIDENCE` pode caber em `REASON_TEXT`; não criar campo novo sem necessidade.

## LINEAGE QUANDO UMA ETAPA NÃO SE APLICA

A aresta deve nomear a última etapa que realmente aconteceu. Exemplo:

```text
RAW → DERIVED[NOT_APPLICABLE] → STRUCTURED
```

Então:

```text
STRUCTURED_PARENT_STAGE = RAW
STRUCTURED_PARENT_ID = RAW_OBSERVATION_ID
```

Não criar `DERIVED_ID` fictício só para preencher uma coluna.

## BLOQUEIOS APÓS A3

```text
TRAVERSAL_CONTRACT_BLOCKERS = 0
STRUCTURED_CONTRACT_BLOCKERS = 5
SCHEMA_BLOCKERS = 3
RUNTIME_BLOCKERS = 5
```

A primeira implementação possível é a classe A, sem depender de machine transcription real.

Questões estruturais ainda abertas incluem:

- owner/store de `OFFICIAL_BULLETIN`;
- owner/store de `TABULAR_MEASUREMENT`;
- writer de `SOCIAL_TRANSCRIPT`;
- registry canônico `STRUCTURED_TARGET -> owner`;
- persistência de `REASON_CODE/REASON_TEXT` para `NOT_APPLICABLE`;
- writer direto em `guarda/catalogo_importar.py` para `raw_asset` e `collection_run`, fora do owner canônico, registrado como `AUTHORITY_CONFLICT` sem expandir escopo.

## PRINCÍPIO REUTILIZÁVEL PARA NOVOS PAÍSES

Novo país não deve criar um pipeline STRUCTURED paralelo. Ele deve declarar, em seu contrato de fonte, qual conceito canônico produz e usar os mesmos owners/registries CORE quando a espécie é comum.

```text
COUNTRY SOURCE CONTRACT
        ↓
STRUCTURED_TARGET
        ↓
CORE DISPATCH REGISTRY
        ↓
CONCEPT OWNER
```

Se a espécie for realmente nova, cria-se um novo conceito/owner justificado — não um fallback por formato, país, palavra ou plataforma.

## FECHO

```text
STRUCTURED_DISPATCH_CONTRACT_CLOSED = YES
NOT_APPLICABLE_CONTRACT_CLOSED = YES
UNRESOLVED_CRITICAL_A3_QUESTIONS = 0
READY_FOR_C_PLAN_A4 = YES
```

Definido não é implementado.
