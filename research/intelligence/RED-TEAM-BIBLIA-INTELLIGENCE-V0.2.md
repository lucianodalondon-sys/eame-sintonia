# RED TEAM — BÍBLIA DE ENGENHARIA DA INTELLIGENCE V0.2

**Data:** 2026-09-13  
**Status:** `NON_CANONICAL_REVIEW_EVIDENCE`  
**Alvo:** `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md` V0.2  
**Objetivo:** tentar derrubar a candidata antes de qualquer promoção.

---

# 1. VEREDITO CURTO

```text
BIBLE_EXISTS                         YES
STATUS                               CANDIDATE_FOR_CANONICAL_REVIEW
COLLECTION_BOUNDARY                  PASS AFTER FIX
ONE_CONCEPT_ONE_OWNER                PARTIAL — MOTOR V2 OWNER RECONCILIATION PENDING
DIRECT_COLLECTION_PATH               NOT AUTHORIZED
PORTAL_AS_TRUTH                      PROHIBITED
UNKNOWN_PRESERVATION                 REQUIRED
DEPENDENCY_BEFORE_CONVERGENCE        REQUIRED
SECURITY_BY_DESIGN                   REQUIRED
IMPLEMENTATION_AUTHORIZED            NO
CANONICAL_PROMOTION_READY            NO
```

A candidata está suficientemente coerente para servir de base de arbitragem, mas **não está pronta para promoção** porque ainda há convergência de governança a resolver.

---

# 2. ATAQUE RT-BIBLE-01 — FACT/CLAIM COM DOIS DONOS

## Tentativa

Tratar `FACT` e `CLAIM` como identidades nascidas dentro da Intelligence.

## Evidência contrária

`BIBLIA-CANONICA-DA-COLETA.md` V1.4 já declara `CLAIM / FACT` como contrato próprio para separar artefato do fato extraído, incluindo a relação `ARTIFACT → CLAIM`.

## Resultado

```text
V0.1 = FAIL
V0.2 = FIXED
```

A V0.2 agora declara:

```text
COLLECTION OWNS SOURCE FACTUAL CLAIM / FACT
INTELLIGENCE CONSUMES IT
INTELLIGENCE OWNS ANALYTIC DERIVATIVES
```

## Consequência

Esta foi uma colisão arquitetural real descoberta pelo red team, não uma melhoria editorial.

---

# 3. ATAQUE RT-BIBLE-02 — MOTOR V2 VIRA SEGUNDA BÍBLIA

## Tentativa

Deixar `MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md` e a nova Bíblia ambos como fonte de verdade para os mesmos gates/estados.

## Resultado

```text
PROMOTION_BLOCKER = YES
```

O Motor V2 tem requisitos maduros que devem sobreviver, mas o ownership final precisa ser:

```text
INTELLIGENCE BIBLE = CONSTITUTION / PRINCIPLES / BOUNDARIES
MOTOR V2 REQUIREMENTS = SUBORDINATE IMPLEMENTATION CONTRACT
```

Essa reconciliação não foi executada nesta missão.

---

# 4. ATAQUE RT-BIBLE-03 — INTELLIGENCE PUXA COLETA DIRETA

## Tentativa

Usar `COLLECTION_GAP` para chamar scraper/collector diretamente.

## Resultado

```text
DEFENDED
```

A Bíblia exige retorno via Orchestrator/Collection canônica e preserva RUN, RAW, storage, retry, custo, procedência e Admission.

---

# 5. ATAQUE RT-BIBLE-04 — CONVERGÊNCIA POR CONTAGEM

## Tentativa

Apresentar várias validações dependentes como confirmação independente.

## Resultado

```text
DEFENDED
```

Grafo de dependências precede convergência; contagens ficam separadas entre signal/source/structural validation/family.

Evidência interna: o refresh final EAME derrubou 5 de 6 alegações de convergência após medir dependência.

---

# 6. ATAQUE RT-BIBLE-05 — LLM COMO FONTE

## Tentativa

Permitir que uma afirmação gerada pelo modelo seja promovida a fato porque o modelo “sabe”.

## Resultado

```text
DEFENDED
```

LLM é mecanismo. Output deve ligar a claim/fato upstream ou permanecer synthesis/hypothesis/judgment com estado apropriado.

---

# 7. ATAQUE RT-BIBLE-06 — PROMPT INJECTION VIA FONTE

## Tentativa

Documento coletado contém texto que tenta instruir agente a mudar ferramenta, política, acesso ou segredo.

## Resultado

```text
DEFENDED AT LAW LEVEL
IMPLEMENTATION = NOT_YET
```

Conteúdo coletado é data não confiável, não instrução de controle.

---

# 8. ATAQUE RT-BIBLE-07 — VERDADE ANTIGA VIRA ACT_NOW

## Tentativa

Um fato verdadeiro de 130 dias atrás é promovido a ação atual.

## Resultado

```text
DEFENDED
```

Actionability tem gate temporal separado de factualidade.

---

# 9. ATAQUE RT-BIBLE-08 — AUSÊNCIA SEM UNIVERSO

## Tentativa

Converter `NOT_FOUND` em `ZERO_PROVED` sem declarar universo esperado.

## Resultado

```text
DEFENDED
```

Zero exige universe contract.

---

# 10. ATAQUE RT-BIBLE-09 — PORTAL COMPLETA A VERDADE

## Tentativa

Delivery cruza dados ou resolve UNKNOWN para montar um card mais útil.

## Resultado

```text
DEFENDED
```

Portal consome, não reconstrói Intelligence.

---

# 11. ATAQUE RT-BIBLE-10 — HUMAN APPROVAL LAVA EVIDÊNCIA FRACA

## Tentativa

Reviewer humano aprova finding e o sistema o marca como factual/provado sem suporte.

## Resultado

```text
DEFENDED
```

Approval não apaga provenance, gaps nem base de evidência.

---

# 12. ATAQUE RT-BIBLE-11 — SECURITY POR PERÍMETRO

## Tentativa

Agente ganha write porque já está autenticado “dentro” do SINTONIA.

## Resultado

```text
DEFENDED
```

`AUTHENTICATION != AUTHORIZATION` e `READ != DERIVE != WRITE != ACT`.

---

# 13. ATAQUE RT-BIBLE-12 — HISTÓRICO REESCRITO

## Tentativa

Nova evidência corrige finding antigo sobrescrevendo a versão anterior.

## Resultado

```text
DEFENDED
```

Histórico append-only por default; active state e historical state separados.

---

# 14. ATAQUE RT-BIBLE-13 — SCORE ESCONDE GATE DURO

## Tentativa

Somar muitos sinais fracos e deixar score alto superar missing provenance/universe/time.

## Resultado

```text
DEFENDED
```

Score não substitui decomposição e não derrota gate duro.

---

# 15. ATAQUE RT-BIBLE-14 — FUTURE RADAR COMO CALENDÁRIO

## Tentativa

Data futura + cultura + expiry = opportunity futura.

## Resultado

```text
DEFENDED
```

`FUTURE_DATE != FORECAST != FACT != OPPORTUNITY`.

---

# 16. ATAQUE RT-BIBLE-15 — EVIDENCE FAMILY COLAPSA ORIGEM

## Tentativa

Um `FAMILY_ID` genérico mistura natureza da evidência, dataset e source method e impede medir independência.

## Resultado

```text
DEFENDED
```

V0.2 preserva `EVIDENCE_FAMILY`, `DATASET_FAMILY`, `SOURCE_FAMILY`.

---

# 17. PONTOS AINDA NÃO RESOLVIDOS — NÃO DISFARÇAR DE PASS

## G-INT-01 · Promotion topology

```text
STATUS = OPEN
```

A governança mediu `CONTROL_PLANE_ATOMICITY = FAIL`. A candidata vive em branch lateral. Não pode ser chamada canônica até existir estratégia de integração.

## G-INT-02 · Motor V2 owner reconciliation

```text
STATUS = OPEN
```

Motor V2 continua documento “canônico de requisitos futuros”. Antes da promoção, decidir/subordinar ownership sem apagar histórico.

## G-INT-03 · Contract shape de INTELLIGENCE_RUN

```text
STATUS = NOT_DESIGNED
```

A Bíblia declara semântica mínima, não schema/tabela.

## G-INT-04 · Contract shape de analytic objects

```text
STATUS = NOT_DESIGNED
```

Support edge, contradiction, hypothesis, signal, judgment e opportunity ainda não têm schema canônico. Isso é correto nesta fase: lei antes de implementação.

## G-INT-05 · Confidence vocabulary/calibration

```text
STATUS = NEEDS_CONTRACT
```

A Bíblia distingue confidence de probability, mas não congela escalas sem baseline/eval.

## G-INT-06 · Human review thresholds

```text
STATUS = NEEDS_MEASUREMENT
```

“Alto impacto / baixa confiança” é princípio; threshold operacional exige risco real e casos.

## G-INT-07 · Security runtime

```text
STATUS = NOT_MEASURED
```

A Bíblia declara least privilege e separação de capabilities; não prova IAM/RLS/secrets/runtime atual.

## G-INT-08 · Quality baselines

```text
STATUS = NOT_MEASURED
```

Métricas foram escolhidas; valores baseline ainda não existem.

---

# 18. O QUE O BENCHMARK EXTERNO REALMENTE MUDOU

Sem benchmark, a tendência seria desenhar “motor que cruza tudo e dá score”.

O estudo mudou o alvo para:

```text
AUDITABLE ANALYTIC PRODUCTION
+ DECISION TRACE
+ DEPENDENCY GRAPH
+ PROVENANCE
+ UNCERTAINTY
+ QUALITY OBSERVABILITY
+ SECURITY
+ HUMAN/AI BOUNDARY
```

Referências principais:

- ODNI ICD 203: source quality, uncertainty, assumptions vs judgments, alternatives, relevance, change in judgment;
- CIA Structured Analytic Techniques: mecanismos contra viés/ambiguidade;
- Databricks Unity Catalog: governance/lineage/quality como camada transversal;
- Palantir Ontology: data + logic + action + security e decision lineage;
- OpenLineage: run/job/dataset e lineage explícito;
- OpenMetadata: lineage/quality/incidents;
- NIST AI RMF/SSDF/Zero Trust: risk lifecycle, secure development, no implicit trust;
- UK Futures Toolkit: horizon scanning sem transformar sinal em previsão.

---

# 19. VEREDITO

```text
BIBLE_V0_2 = COHERENT_ENOUGH_FOR_CANONICAL_ARBITRATION
CANONICAL_PROMOTION = BLOCKED
IMPLEMENTATION = NOT_AUTHORIZED
```

A descoberta mais valiosa do red team foi `FACT/CLAIM` já ter owner na Collection. Isso prova que a sequência correta foi respeitada:

```text
AUTHORITY
→ BENCHMARK
→ DRAFT
→ RED TEAM
→ CORRECTION
→ ONLY THEN ARBITRATION
```

---

`KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA`

**HARD STOP.**