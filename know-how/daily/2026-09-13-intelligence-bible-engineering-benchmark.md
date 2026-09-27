# DAILY KNOW-HOW — 2026-09-13 — INTELLIGENCE BIBLE / BENCHMARK DE ENGENHARIA

Este arquivo pertence à trilha canônica `know-how/daily/`. Registra somente o delta durável da missão de benchmark e criação da Bíblia de Engenharia da Intelligence. **Não cria um segundo KNOW-HOW** e não substitui Bíblias, contratos, System Map, Git, código, runtime ou provas.

## CONTEXTO MEDIDO

A auditoria de governança C-GOV-01 encontrou:

```text
INTELLIGENCE_BIBLE = FOUND_FRAGMENTS_ONLY
CONTROL_PLANE_ATOMICITY = FAIL
```

O documento histórico de 621 linhas encontrado no Git declara-se `INPUT_TO_INTELLIGENCE_BIBLE` e diz explicitamente que ainda **não é** a Bíblia de Engenharia da Intelligence.

Portanto, a Bíblia de Engenharia ainda precisava ser escrita. A missão atual fez isso em branch isolada, sem iniciar implementação.

## ARTEFATOS PRODUZIDOS

Branch de pesquisa:

```text
research/intelligence-bible-engineering-v1
```

Artefatos:

```text
research/intelligence/BENCHMARK-DE-ENGENHARIA-DA-INTELLIGENCE-2026-09-13.md
BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md
research/intelligence/RED-TEAM-BIBLIA-INTELLIGENCE-V0.2.md
```

Estado da Bíblia:

```text
BIBLE_ID = SINTONIA-INTELLIGENCE-BIBLE
VERSION = V0.2
STATUS = CANDIDATE_FOR_CANONICAL_REVIEW
IMPLEMENTATION_AUTHORIZED = NO
```

Ela **não é canônica ainda**.

---

# DELTA DURÁVEL

## 1 · COLLECTION JÁ POSSUI O FACT/CLAIM EXTRAÍDO

A primeira versão candidata da Bíblia da Intelligence tratou `FACT / CLAIM` como identidade interna da Intelligence.

O red team contra `BIBLIA-CANONICA-DA-COLETA.md` V1.4 encontrou conflito real de owner: a Bíblia da Collection já reserva `CLAIM / FACT` como contrato próprio para separar artefato do fato extraído, com a relação conceitual:

```text
ARTIFACT -> CLAIM
```

A V0.1 portanto violava:

```text
ONE CONCEPT -> ONE OWNER
```

A V0.2 corrigiu a fronteira:

```text
COLLECTION OWNS
- source factual CLAIM / FACT extraído
- identidade/proveniência desse factual unit

INTELLIGENCE CONSUMES
- claims/fatos admitidos

INTELLIGENCE OWNS ANALYTIC DERIVATIVES
- INTELLIGENCE_REQUEST
- INTELLIGENCE_RUN
- SUPPORT / CONTRADICTION RELATIONS
- DEPENDENCY / INDEPENDENCE GRAPH
- CROSSING
- ANALYTIC_SIGNAL
- ANALYTIC_ASSUMPTION
- ANALYTIC_HYPOTHESIS
- ANALYTIC_JUDGMENT / FINDING
- OPPORTUNITY / ATTENTION ITEM / FUTURE SIGNAL
- ANALYTIC_RECOMMENDATION
```

Consequência:

> Intelligence não fabrica uma segunda identidade de fato para destravar análise. Se o factual upstream não tiver identidade/proveniência suficiente, isso vira contract/collection gap.

---

## 2 · GRAFO DE DEPENDÊNCIAS VEM ANTES DE CONVERGÊNCIA

O refresh histórico de Intelligence EAME provou que contagem sem dependência fabrica valor:

```text
5 de 6 alegações anteriores de convergência não sobreviveram
após o SIGNAL-DEPENDENCY-GRAPH.
```

Exemplos históricos:

- anúncio Meta contido em outra cadeia derivada não cria segunda família;
- registro nacional lido por duas rotas não cria duas fontes;
- listing e corpo do mesmo documento não criam independência;
- Creator Map e Deep Corpus sobre a mesma entidade não viram duas famílias automaticamente.

Lei durável:

```text
DEPENDENCY GRAPH
BEFORE
CONVERGENCE COUNT / SCORE
```

---

## 3 · CONTEXTO DO CONTEÚDO É PARTE DA PROVA

O refresh histórico também removeu falso sinal francês porque o termo de doença vinha de sidebar/menu, não do corpo do boletim.

Lei durável:

```text
PAGE CHROME != FACTUAL BODY
SNIPPET != FULL UNIT WHEN CONTEXT IS REQUIRED
```

Intelligence não pode promover evidência só porque a string apareceu no documento renderizado.

---

## 4 · INTELLIGENCE É PRODUÇÃO ANALÍTICA AUDITÁVEL

O benchmark externo e a experiência interna convergiram em uma arquitetura:

```text
ADMITTED FACTUAL CLAIMS / EVIDENCE
→ SUPPORT / CONTRADICTION
→ DEPENDENCY / INDEPENDENCE
→ CROSSINGS
→ SIGNALS
→ HYPOTHESES / ALTERNATIVES
→ JUDGMENTS / FINDINGS
→ OPPORTUNITY / ATTENTION / FUTURE SIGNAL
```

Sempre acompanhado por:

```text
PROVENANCE
UNCERTAINTY
CONTRARY EVIDENCE
TIME / GEOGRAPHY
UNIVERSE / COMPLETENESS
RUN / VERSION / PARAMETERS
QUALITY / OBSERVABILITY
SECURITY
```

O benchmark não se torna autoridade. Ele informa as leis que a Bíblia candidata consolidou.

---

## 5 · LLM É MECANISMO, NÃO FONTE

Lei durável:

```text
LLM OUTPUT != SOURCE FACT
```

Modelos podem auxiliar extração, normalização, classificação, síntese, geração de hipótese e judgment candidato, mas precisam de lineage, evals, versionamento e estados de recusa/UNKNOWN.

Também:

```text
COLLECTED CONTENT = UNTRUSTED DATA
COLLECTED CONTENT != CONTROL INSTRUCTION
```

Instruções encontradas em web/PDF/comment/transcript não autorizam ferramenta, segredo, escopo ou permissão.

---

## 6 · DECISION TRACE SUBSTITUI DEPENDÊNCIA DE CHAIN-OF-THOUGHT PRIVADO

Auditoria da Intelligence deve depender de artefatos compartilháveis:

```text
INPUTS
EVIDENCE
SUPPORT / CONTRADICTION
ASSUMPTIONS
ALTERNATIVES
RULE / ALGORITHM / PROMPT VERSION
RATIONAL SUMMARY
GATES
OUTPUT STATE
```

Não depender de raciocínio privado de modelo para reconstruir por que uma decisão aconteceu.

---

## 7 · TRUE != RELEVANT != ACTIONABLE

O caso histórico Toscana × trigo duro × fusarium mostrou um fato territorial verdadeiro que já estava fora da janela para `ACT_NOW`.

Lei durável:

```text
FACTUALITY
RELEVANCE
ACTIONABILITY
```

são eixos distintos.

Um fato correto pode terminar em:

```text
PLAN_NEXT_CYCLE
MONITOR
STALE_FOR_ACTION
UNKNOWN_WINDOW
```

conforme contratos futuros.

---

## 8 · NO_DEFENSIBLE_ACTION_YET É RESULTADO VÁLIDO

A Intelligence não é medida por quantidade de cards.

```text
NO_DEFENSIBLE_ACTION_YET
```

é sucesso epistemológico quando a evidência não suporta promoção.

Não relaxar gate para alimentar portal.

---

## 9 · FUTURO NÃO É ADIVINHAÇÃO

Preservar:

```text
WEAK_SIGNAL != FORECAST
FORECAST != FACT
SCENARIO != PREDICTION
FUTURE_DATE != OPPORTUNITY
```

Future Radar precisa declarar evidência, horizonte, impacto potencial, incerteza e indicadores que alterariam o judgment.

---

## 10 · SECURITY-BY-DESIGN NA INTELLIGENCE

A candidata consolida como princípios:

```text
AUTHENTICATION != AUTHORIZATION
READ != DERIVE != WRITE != ACT
```

Baseline da Intelligence V1:

```text
READ / DERIVE FIRST
NO EXTERNAL OPERATIONAL ACTION BY DEFAULT
```

Least privilege, gestão de segredos, minimização de dados, auditoria, risco de dependências/modelos e validação antes de LIVE fazem parte da arquitetura, não fase posterior.

---

## 11 · QUALITY / LINEAGE SÃO CONTÍNUOS

Intelligence precisa poder observar, quando mensurável:

```text
FRESHNESS
COMPLETENESS
LINEAGE GAPS
CONTRACT DRIFT
FAMILY CONSULTATION GAPS
MODEL BEHAVIOR DRIFT
```

E preservar:

```text
SYSTEM HEALTH != ANALYTIC TRUTH
```

Pipeline verde não prova finding correto.

---

## 12 · PROMOÇÃO DA BÍBLIA CONTINUA BLOQUEADA

Dois bloqueadores materiais continuam abertos:

### A. CONTROL PLANE ATOMICITY

A governança já mediu que ainda não existe um único snapshot contendo de forma coerente código + Bíblias + Know-how + registry + testes.

### B. MOTOR INTELLIGENCE V2

`docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md` contém requisitos maduros e hoje se declara documento canônico de requisitos futuros.

Antes de promover a nova Bíblia, é obrigatório eliminar double-owner.

Direção candidata:

```text
INTELLIGENCE BIBLE
= CONSTITUTION / PRINCIPLES / BOUNDARIES

MOTOR V2 REQUIREMENTS
= SUBORDINATE IMPLEMENTATION CONTRACT
```

Essa reconciliação **não foi executada** nesta missão.

---

# PROVA

Branch de pesquisa contém:

```text
BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md V0.2
research/intelligence/BENCHMARK-DE-ENGENHARIA-DA-INTELLIGENCE-2026-09-13.md
research/intelligence/RED-TEAM-BIBLIA-INTELLIGENCE-V0.2.md
```

O red team encontrou e corrigiu a colisão Collection FACT/CLAIM antes da promoção.

Runtime da Intelligence não foi alterado.

---

# CONSEQUÊNCIA PARA OUTRAS ABAS

Até promoção explícita:

```text
INTELLIGENCE_BIBLE_STATUS = CANDIDATE
```

Nenhuma aba deve tratá-la como Constituição vigente ou iniciar implementação “porque a Bíblia existe”.

Ao trabalhar em Intelligence, reler:

1. Bíblia da Collection vigente para fronteira upstream;
2. Bíblia candidata V0.2;
3. Motor Intelligence V2 requirements;
4. este delta de Know-how;
5. estado real Git/runtime antes de qualquer mudança.

---

# O QUE NÃO MUDOU

- nenhuma implementação de Intelligence começou;
- nenhuma Collection foi alterada;
- nenhum Portal/Casco foi alterado;
- nenhum LIVE foi alterado;
- a candidata não foi registrada/promovida como `CANONICAL`;
- Motor V2 não foi rebaixado ou editado silenciosamente.

`KNOW_HOW_DELTA = ATUALIZADO`

**HARD STOP.**