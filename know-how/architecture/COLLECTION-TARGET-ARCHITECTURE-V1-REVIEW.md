# SINTONIA EAME — REVIEW DA COLLECTION TARGET ARCHITECTURE V1

> Revisão pré-implementação da consolidação transversal. Preserva a arquitetura V1 como evidência de decisão e registra pontos que precisam fechar antes de escrever o plano executável de reforma.

## FONTES

```text
CENSUS_HEAD = 572647dce8a38b8835aafa6f9e3e42d2652fbcd9
KNOW_HOW_SOURCE_COMMIT = 6fca4ad2ebe861ca3df2cb4c582c1704d9766926
CARD_CONTRACT_SOURCE_HEAD = bee7d6af73531b678697dc7f5e9063d597652b47
TARGET_ARCHITECTURE_FILE = know-how/architecture/COLLECTION-TARGET-ARCHITECTURE-V1.md
```

## VEREDITO

A arquitetura V1 é forte o bastante para uma missão curta de fechamento pré-implementação, mas NÃO deve virar plano de mutation ainda sem resolver os pontos abaixo.

```text
CENSUS = CLOSED 64/64
TARGET_DIRECTION = ACCEPTED
READY_FOR_PRE_IMPLEMENTATION_CLOSURE = YES
READY_FOR_RUNTIME_IMPLEMENTATION = NO
```

## B-01 — NÃO PODE HAVER DOIS ORQUESTRADORES

A V1 define:

```text
T-04 COLLECTION-ORCHESTRATOR = ORCHESTRATOR
T-32 UNIT-FORWARD-LINEAGE-RUNNER = ORCHESTRATOR
```

Isso conflita com a lei já amadurecida de um único owner de orquestração.

T-32 pode possuir a pergunta `esta unidade atravessou as etapas preservando linhagem?`, mas não deve virar um segundo cérebro de coordenação.

Fechamento exigido antes de implementar:

```text
CANONICAL_ORCHESTRATION_OWNER = T-04
T-32_TYPE = EXECUTOR / WORKFLOW / FORWARDER, ou sua coordenação fica subordinada a T-04
T-32_MUST_NOT_DECIDE = rota, retry global, custo, seleção de executor, política de Admission
ORCHESTRATOR_OWNER_COUNT = 1
```

## B-02 — IDENTIDADE RAW TEM TRÊS EIXOS, NÃO UM

Nunca usar `storage_path` como identidade e nunca confundir conteúdo com ocorrência.

```text
RAW_OBSERVATION_ID = identidade da captura/observação
CONTENT_SHA256 = fingerprint do conteúdo para integridade/dedupe
STORAGE_LOCATOR = endereço físico, nunca identidade
SOURCE_ID + RUN_ID + CAPTURED_AT = proveniência
```

O mesmo byte pode ser coletado em duas corridas e continuar sendo duas observações com o mesmo conteúdo.

## B-03 — FACT_TIME / FACT_LOCATION PRECISAM DE AUTORIDADE EXPLÍCITA

A V1 preserva os gates `FACT_TIME_FABRICATED = 0` e `FACT_LOCATION_FABRICATED = 0`, mas não deixa suficientemente explícito quem possui a promoção/validação desses campos.

Além disso, a descrição de T-62 CONTENT-TRIAGE dizia que ele pode decidir `país do fato`. Isso é perigoso e não deve virar contrato.

Regra:

```text
SOURCE_LOCATION != FACT_LOCATION
SOURCE_COUNTRY != FACT_COUNTRY
COLLECTION_TIME != PUBLICATION_TIME != FACT_TIME
```

T-62 pode extrair:

```text
FACT_LOCATION_CANDIDATE + EVIDENCE
FACT_TIME_CANDIDATE + EVIDENCE
```

mas não pode fabricar/promover FACT_LOCATION ou FACT_TIME por escopo, plataforma, conta, idioma ou país da coleta.

A missão de fechamento deve decidir se a autoridade canônica cabe em regra/contrato já existente portado do Brasil ou se precisa de owner explícito no target manifest.

## B-04 — CT-08 É DIVERGÊNCIA TEMPORAL A RECONCILIAR, NÃO PARA IGNORAR

O censo fotografa a Bíblia V1.3. A branch de Card Contract nasce de outra fotografia de trabalho e leva a Bíblia a V1.4 com COL-LAW-601..617.

Antes da Phase 0:

```text
MEASURE merge-base / ancestry
PROVE qual commit descende de qual base
PRESERVE V1.3 como AS-IS do censo
PROMOTE V1.4 somente como target law após integração explícita
```

Não reescrever a história dizendo que o censo já era V1.4.

## B-05 — T-80 OPENALEX / ORCID AINDA NÃO TEM FRONTEIRA DECIDIDA

Antes de implementar T-80, decidir por evidência:

```text
A) acquisition normal:
EXTERNAL → EXECUTOR → T-20 → T-21 → ...

ou

B) EXTERNAL_REFERENCE declarada:
leitura de referência com contrato e proveniência próprios
```

Não deixar OpenAlex/ORCID como exceção silenciosa fora da espinha.

## B-06 — SYSTEM MAP DURANTE A MIGRAÇÃO

O mapa deve ser consequência do runtime, mas o repositório já possui seal/gates que podem reprovar qualquer mudança tracked com mapa stale.

Portanto:

```text
NUNCA editar o mapa manualmente para parecer pronto.
SE o CI exigir, regenerar mecanicamente no checkpoint de cada phase.
PHASE G continua sendo a regeneração/validação final completa.
```

Assim não se escolhe entre `mapa mentiroso` e `branch eternamente vermelha`.

## B-07 — CONTAGEM DE MERGE PRECISA SER NOMINAL

A V1 traz duas leituras que podem parecer contraditórias:

```text
C-SINTONIA-SCRAP → T-01 = MERGE
C-DERIVACAO-FORWARD + C-ROTA-M2 → T-32 = MERGE
C-ESTRADA-PDF contribui com segmento para T-32, mas sua ação primária continua SPLIT
```

A futura migration matrix deve ser `CURRENT_ID → TARGET_ID(s)` nominal. Não usar apenas `MERGE = 3` como prova de fechamento.

## B-08 — T-32 NÃO PODE VIRAR BYPASS DA ADMISSION

A V1 quer `WHO_IS_ALLOWED_TO_CALL_ADMISSION = T-32`.

Isso só é aceitável se T-32 for o forwarder executor subordinado ao T-04 e carregar exclusivamente a unidade já preservada/derivada/estruturada.

Ele não pode:

```text
re-selecionar itens
ignorar accepted list do Ingress
criar RAW implicitamente
chamar Admission com item sem RAW_ID
mudar regra de Admission
```

## PRÓXIMO PASSO CORRETO

Fazer UMA missão read-only curta de `TARGET ARCHITECTURE V1.1 — PRE-IMPLEMENTATION CLOSURE`.

Ela deve fechar B-01, B-02, B-03, B-04, B-05, B-06 e B-07/B-08, produzir os contratos mínimos de identidade/autoridade e só então declarar:

```text
TARGET_ARCHITECTURE_V1_1_CLOSED = YES
READY_FOR_IMPLEMENTATION_PLAN = YES
```

Depois disso vem o plano de implementação por phases/checkpoints. Só depois do plano aprovado começam mutations.
