# PADRÕES DE CARDS E AÇÃO — SINTONIA EAME V1

**Research only. Não é especificação de UI/CSS.**

## 1. Lei principal

> **O card é uma unidade de decisão, não uma unidade de armazenamento.**

O card não deve demonstrar quanto o SINTONIA sabe. Deve ajudar uma pessoa a entender o que mudou, por que importa, qual o limite da evidência e o que pode fazer agora.

---

## 2. Modelo 3s / 30s / 3min

### 3 segundos — PRIMARY

A pessoa deve conseguir responder sem abrir detalhe:

- **WHAT:** qual é a chamada?
- **WHERE:** qual geografia/cultura/problema?
- **WHEN:** qual janela/horizonte/time-to-act?
- **WHY NOW:** por que precisa olhar agora?
- **ACTION STATE:** agir, preparar, próxima janela ou monitorar/validar?

A ação primária deve estar visível.

### 30 segundos — SECONDARY

- what is happening;
- why it matters to ADAMA;
- ADAMA implication/response;
- what to do;
- principal limitation/unknown;
- freshness/evidence maturity;
- related objects.

### 3 minutos — ON DEMAND

- claim-linked evidence;
- source originals;
- versions/timestamps;
- contrary evidence;
- source diversity;
- chronology;
- coverage gaps;
- linked science, competitor, label, portfolio, windows;
- investigation history.

---

## 3. Gramática visual comum

Uma família de Intelligence Cards pode compartilhar:

1. `BIG CALL`
2. `WHY NOW`
3. `WHERE`
4. `WINDOW / HORIZON`
5. `WHY IT MATTERS`
6. `ADAMA IMPLICATION / RESPONSE`
7. `WHAT TO DO`
8. `EVIDENCE STATE`
9. `UNKNOWN / LIMITATION`
10. `EVIDENCE`

Mas cada família precisa preservar campos próprios.

### Opportunity Card

**Obrigatórios**
- CALL
- WHAT IS HAPPENING
- WHY NOW
- WHERE
- AGRONOMIC WINDOW
- TIME TO PREPARE / TIME TO ACT quando conhecido
- WHY IT MATTERS
- ADAMA RESPONSE
- WHAT TO DO
- LIMITATION / UNKNOWN
- EVIDENCE STATE

**Campo epistemológico central:** `IS THIS ACTIONABLE NOW?`

### Future Card

**Obrigatórios**
- CALL
- HORIZON
- WHY WE ARE WATCHING
- WHAT MAY CHANGE
- EVIDENCE MATURITY
- ADAMA IMPLICATION
- WHO SHOULD PREPARE
- WHAT WOULD STRENGTHEN IT
- WHAT WOULD WEAKEN IT
- CONTRARY EVIDENCE
- UNKNOWN

**Campo epistemológico central:** `WHAT WOULD HAVE TO BECOME TRUE?`

### Scientific Card

**Obrigatórios**
- BIG CALL
- WHAT SCIENCE SAYS
- WHY IT MATTERS TO ADAMA
- MATURITY
- HORIZON
- WHERE / applicability boundary
- WHO IS WORKING ON IT
- INDEPENDENT GROUPS / replication when measurable
- EVIDENCE
- CONTRARY EVIDENCE
- IMPLICATION
- WHO SHOULD ACT
- NEXT ACTION
- UNKNOWN

**Campo epistemológico central:** `HOW MATURE AND TRANSFERABLE IS THIS KNOWLEDGE?`

### Market Card

Não deve herdar toda a família acima automaticamente.

- CHANGE
- AS OF
- SCOPE / geography / crop
- WHY IT MATTERS
- WHICH DECISION MAY CHANGE
- WHO NEEDS TO LOOK
- EVIDENCE / source
- LIMITATION

**Campo central:** `SO WHAT FOR AN ADAMA DECISION?`

### Field Voices Card

- HEADLINE
- SMART SUMMARY
- WHY IT MATTERS
- WHERE
- CROP / PROBLEM
- FIRST/LAST OBSERVED
- SOURCE DIVERSITY
- SOURCE ROLE
- SIGNAL STATE
- CONFIDENCE IN THE SIGNAL, not incidence
- OPEN ORIGINAL VOICES

**Campo central:** `WHAT IS THE FIELD TALKING ABOUT, NOT WHAT IS PROVEN TO BE HAPPENING?`

---

## 4. Time UX

Time é um objeto de primeira classe.

### Não colapsar

- `FACT_TIME`
- `PUBLISHED_AT`
- `FIRST_OBSERVED`
- `LAST_OBSERVED`
- `AS_OF`
- `WINDOW_START / WINDOW_END`
- `TIME_TO_PREPARE`
- `TIME_TO_ACT`
- `DEADLINE`
- `EXPIRY`
- `HORIZON`

### Leis

- calendar date ≠ observed phenology;
- approximate window ≠ exact date;
- time-to-prepare ≠ time-to-apply;
- regulatory expiry ≠ commercial opportunity by itself;
- source publication time ≠ fact time;
- no date may be silently inferred.

### Opportunity ordering

**Primary order:** action state in time.

1. AGIR AGORA
2. PREPARAR AGORA
3. PRÓXIMA JANELA
4. MONITORAR / VALIDAR

**Within state:** time remaining → consequence of missing window → ADAMA response readiness → evidence freshness/quality → user geography/crop responsibility.

No universal 0–100 score.

---

## 5. Evidence UX

### Above the fold

Evidence must be visible as a **state**, not as a wall of links:

- `AS OF`;
- source count/diversity when meaningful;
- maturity/freshness;
- contradiction/unknown badge if decision-relevant.

### One click away

`OPEN EVIDENCE` opens a contextual drawer/side panel.

Recommended structure:

1. claim being supported;
2. supporting evidence;
3. contrary evidence;
4. source role/type;
5. source/fact time;
6. source/fact location;
7. original URL/document;
8. version/history;
9. coverage/unknown.

### Why drawer instead of page navigation

The user keeps the decision context while checking proof. This mirrors the useful pattern of object/detail panels and entity pivots found in operational/intelligence systems without copying their UI.

### Anti-patterns

- bibliography hero;
- source hidden;
- evidence count treated as quality;
- URL list with no claim mapping;
- confidence derived from number of links;
- source excerpt promoted beyond what it supports.

---

## 6. Uncertainty UX

### Não usar uma confiança única para coisas diferentes

Uma oportunidade pode ter:

- high confidence that a signal exists;
- low confidence that it will intensify;
- high confidence that a product is officially registered;
- unknown confidence that commercial demand will change.

Colapsar isso num único `82%` destrói informação.

### Dimensões recomendadas

**Evidence maturity**  
Emerging / Corroborated / Established — nomes finais a validar.

**Coverage**  
Partial / Adequate / Broad.

**Relation state**  
Supported / Mixed / Contradicted.

**Freshness**  
Current / Stale + last observed.

**Future only**  
Horizon + trigger dependency + strengthening/weaking evidence.

### UNKNOWN

UNKNOWN deve dizer **o que não sabemos** e, quando útil, **o que poderia resolver**.

Exemplo correto:

`UNKNOWN · Observed phenology not available for this region. Window is calendar-based.`

Exemplo incorreto:

`Confidence: 63%` sem explicar objeto, base e calibração.

---

## 7. Geography UX

### Geography chip quase sempre

Quando material, mostrar hierarquia concisa:

`ITALY → VENETO → GRAPES`

### Map only when it changes understanding/action

Mapa recomendado para:
- Opportunity clusters;
- Field Voices clusters;
- Crop Windows regional differences;
- outbreaks/signals cuja distribuição espacial é a pergunta.

Mapa condicional para Market Pulse.

Mapa não recomendado como ornamento em cards onde a geografia já é uma única localidade textual.

---

## 8. Action architecture

### Lei

> **Ação é encaminhamento humano, não decisão automática da ADAMA.**

### Ações comuns

- GENERATE BRIEF
- SHARE
- FOLLOW / WATCH
- ASSIGN / SEND
- REQUEST VALIDATION
- CREATE INVESTIGATION
- OPEN RELATED
- ASK SINTONIA
- OPEN EVIDENCE

### Ações contextuais

**Opportunity**
- Generate Sales/RTV brief
- Assign / Send
- View Portfolio
- View Window
- View Label
- View Competitors
- Request Technical/Market Development validation

**Future**
- Follow
- Create preparation task
- Request validation
- Open Science
- Open contrary evidence

**Science**
- Send to Technical/Market Development
- Follow theme
- Open underlying research
- Create validation question
- Promote candidate to Future only through an explicit governed transition

**Field Voices**
- Open original voices
- Request field validation
- Link to existing signal
- Create investigation

### Primary action rule

Cada card deve ter **uma ação primária**, escolhida pela decisão e pelo papel. O resto é secondary/on-demand.

Cinco botões com o mesmo peso equivalem a nenhuma ação clara.

---

## 9. Follow / Watch

Seguir um objeto é preferível a “alertar tudo”.

A pessoa pode seguir:

- opportunity;
- crop/problem/geography;
- future signal;
- science theme;
- competitor/product;
- label/product;
- market condition.

Follow controla:

- alertas de transição;
- daily digest;
- weekly brief;
- favorites/action inbox.

---

## 10. Alert rules

### Interruptive alert only if

1. a mudança é material;
2. é relevante para o papel/geografia/cultura do usuário;
3. muda `WHAT SHOULD I DO?` ou deadline;
4. não é duplicata de estado já conhecido.

### Exemplos

**SIM**
- Opportunity entra em AGIR AGORA.
- PREPARAR AGORA começa por lead time.
- Label muda e invalida/altera resposta ligada.
- Evidência contrária derruba um Future/Science call.
- Assigned action vence hoje.

**NÃO**
- nova fonte repete o que já se sabia;
- novo paper sem mudança na maturity/implication;
- novo post social isolado;
- atualização cosmética de card;
- valor de mercado mexe sem decisão ADAMA afetada.

---

## 11. Progressive disclosure

### PRIMARY
- call
- where
- time/action state
- why now
- primary action

### SECONDARY
- why it matters
- ADAMA implication/response
- one limitation
- related objects

### ON DEMAND
- evidence
- research list
- long technical detail
- full chronology
- source metadata
- graph/pivots
- export/history

A regra evita cognitive overload sem esconder limites.

---

## 12. Card family: o que compartilhar e o que não compartilhar

### Compartilhar

- typography hierarchy;
- location/time primitives;
- evidence drawer behavior;
- action rail pattern;
- related object links;
- UNKNOWN/contradiction treatment;
- stable object ID/version/as-of.

### Não compartilhar à força

- confidence semantics;
- time semantics;
- maturity semantics;
- required fields;
- primary action;
- severity/priority meaning.

Opportunity, Future e Science podem parecer parentes. Market, Field Voices, Label, Portfolio e Reference surfaces devem ter gramáticas próprias.

---

## 13. Anti-score rule

Não criar:

- Opportunity Score universal;
- Competitor Score universal;
- Future Probability genérica;
- Science Score mágico;
- one confidence number.

Se houver ranking, mostrar os fatores que explicam a posição.

Exemplo:

`AGIR AGORA · 9 dias · janela fechando · resposta ADAMA pronta · evidência corroborada`

é melhor para decisão do que:

`Opportunity Score 87`.

---

## 14. Action log e value loop

Uma ação pode futuramente registrar:

- intelligence product ID/version;
- user role;
- action type;
- assigned to;
- created/due/completed;
- validation outcome;
- decision affected;
- optional business outcome quando houver base.

Não registrar isso para gamificar cliques. Registrar para fechar o ciclo:

`INTELLIGENCE → ACTION → DECISION → OUTCOME / LEARNING`.

---

## 15. Lei final

> **Card bom reduz a distância entre “eu vi” e “eu sei o que preciso decidir ou fazer”, sem reduzir evidência, limitação ou incerteza.**
