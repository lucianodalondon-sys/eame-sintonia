# PREPARAÇÃO FUNCIONAL — NOVAS CAPACIDADES EAME

**Data:** 2026-08-30 · **Branch:** `claude/sintonia-eame-portal-baseline`
**Modo:** `PREPARE · MEASURE · MAP · TEST` — **`DO NOT INTEGRATE`**
**Revisão:** **DELTA REFRESH 2026-08-30** — quatro fatos mudaram desde a primeira passagem.

```
PRODUCT_IMPLEMENTATION_MODE = NOT_ENTERED
FINAL_REFRESH_EXECUTED      = NO
CASCO_V7_MODIFIED           = NO
REAL_DATA_WIRED             = NO
MANDATORY_HANDOFFS_ACCEPTED = 2/4
```

> Nada aqui está ligado ao casco. Os adaptadores rodam sobre **fixtures aparadas** de
> artefatos reais, lidos do Git em commit fixado. Nenhuma escrita em Supabase, nenhuma
> alteração de schema canônico, nenhuma branch mesclada, nenhuma superfície criada.

| | |
|---|---|
| adaptadores | [`scripts/functional_prep.py`](../../scripts/functional_prep.py) |
| protótipo isolado | [`scripts/functional_sandbox.py`](../../scripts/functional_sandbox.py) |
| provas | [`tests/test_functional_prep.py`](../../tests/test_functional_prep.py) — **63 provas** |
| fixtures + proveniência | `data/functional-sandbox/fixtures/` |
| medição derivada | `data/functional-sandbox/PREP-MEDICAO.json` |

**Suíte inteira:** `460 testes · OK · 0 falhas` — o número subiu depois desta rodada, com o
contrato multilíngue. As 63 provas desta bancada continuam as mesmas.

---

## GUARDRAIL ARQUITETURAL HERDADO — contrato multilíngue

```
MULTILINGUAL_CONTRACT_SOURCE_COMMIT = 1443f6435d4297a4563f25d83473142fc12e1f0d
MULTILINGUAL_CONTRACT_STATE         = ACCEPTED_FROZEN
```

Documento: [`docs/arquitetura/CONTRATO-MULTILINGUE-SINTONIA-EAME.md`](../arquitetura/CONTRATO-MULTILINGUE-SINTONIA-EAME.md)
· modelo em `scripts/multilingual_contract.py` · 68 provas em `tests/test_multilingual.py`.

**O funcional consome este contrato como guardrail congelado.** Toda preparação daqui em
diante — schema, adaptador, fixture, teste, sandbox, contrato de UI — respeita:

```
ONE_CANONICAL_CORPUS = YES        SEPARATE_DATABASE_PER_LANGUAGE = NO

SOURCE_LANGUAGE ≠ ARTIFACT_LANGUAGE ≠ UI_LANGUAGE
                ≠ DISPLAY_LANGUAGE ≠ TRANSLATION_TARGET_LANGUAGE

CANONICAL_ID ≠ DISPLAY_LABEL
ORIGINAL_QUOTE ≠ TRANSLATED_QUOTE ≠ SOURCE_REFERENCE
```

**E `NÃO SEI` continua `NÃO SEI`.** Nenhum adaptador pode reinterpretar língua ausente como
português, inglês, multilíngue ou qualquer outra coisa — nem inferi-la a partir da tradução
exibida. O estado legado é `LEGACY_SOURCE_LANGUAGE_INTEGRITY = NOT_PROVED`, medido em
**0 de 5.998** registros com língua de origem declarada.

**O que o guardrail NÃO autoriza**, mesmo estando aceito e congelado:

```
CORPUS_MIGRATION · MASS_TRANSLATION · SEARCH_INDEX_IMPLEMENTATION
DISEASE_ICON_BINDING · REAL_DATA_WIRING · CASCO_V8_IMPLEMENTATION
FINAL_INTELLIGENCE_REFRESH
```

---

## 0 · O QUE MUDOU NESTE DELTA — e o que foi retirado

### 0.1 · Duas afirmações minhas foram retiradas

| afirmação anterior | veredito | por quê |
|---|---|---|
| *"Expert Directory acende em 3 de 3 recortes"* | **RETIRADA** | media **identidade**, não expertise no problema. Identidade acende em 3/3; expertise no problema acende em **0 de 3** |
| *"Creator pronto em 1 de 3; vazio em 2 de 3"* | **REFORMULADA** | o número era **rota de ativação por `COUNTRY + CROP`**, e foi apresentado como se fosse relevância no problema do caso |

### 0.2 · Foresight deixou de ser ausência

A medição anterior — *"`NO_ARTIFACT_IN_REPO`, varredura em 13 refs"* — **era verdadeira
para o snapshot em que foi feita e deixou de ser**. Ela não foi apagada: está marcada
`SUPERSEDED`, com a data em que parou de valer, e há prova disso.

```
NOT_FOUND_AT_SNAPSHOT  ≠  DOES_NOT_EXIST
```

```
FORESIGHT_ARTIFACT_STATE   = EXISTS
FORESIGHT_CANONICAL_FREEZE = ACCEPTED
FORESIGHT_SOURCE_BRANCH    = claude/eame-competitor-foresight
FORESIGHT_SOURCE_COMMIT    = 25194e3
FINAL_REFRESH_INPUT        = NO       (exige 4/4; hoje 2/4)
```

### 0.3 · A Meta continua fora de alcance — mas não por não existir

**Medido:** `git ls-remote --heads origin` devolve **13 heads e nenhuma contém "meta"**.
A branch `claude/eame-meta-competitor` **não está publicada**.

Isso **não** é "Meta nunca testada". A missão Foresight leu a branch da Meta no commit
`4cee050` e publicou a auditoria da junção. **Os números da Meta chegam até aqui em segunda
mão** — 1.111 anúncios observados, 35 cadeias de três camadas provadas, 131 `NOT_KNOWN`.
Todo objeto que os carrega sai com `META_LEG = NOT_VERIFIABLE_FROM_ORIGIN`.

### 0.4 · O Deep Corpus mudou o diagnóstico dos creators

O gap antigo — *"pessoa↔canal 5/13, conteúdo↔pessoa 0"* — **misturava duas capacidades**.
Aquele número é dos **pesquisadores**, e continua valendo para eles. Para os **creators**,
o estado é outro e é melhor:

```
TARGETS ................... 10   (8 PERSON_CREATOR + 2 FARM_BUSINESS)
CONTENT_ROUTES_PROVED ..... 9
CONTENT_ROUTES_NOT_PROVED . 1    Gilles Van Kempen
MATERIAIS COLETADOS ....... 442  (Instagram 399 · YouTube 43)
ÚLTIMOS 90 DIAS ........... 164  · últimos 30 dias 116
```

**Por que a única rota não provada é interessante:** o endereço registrado de Gilles Van
Kempen **é uma busca, não um canal**. Coletar de uma página de resultados atribuiria à
pessoa o que o buscador devolveu. Recusar foi certo.

---

## 1 · AS QUATRO MEDIÇÕES QUE MUDAM COMO SE LIGA ISTO DEPOIS

### 1.1 · Linha de índice não é entidade — inflação de **2,6×**

```
LOOKUP_BY_ACTIVATION_STATE.ACTIVATION_READY   26 linhas → 10 entidades
                                               8 PERSON_CREATOR + 2 FARM_BUSINESS
```
`contar()` devolve **sempre** os dois números. `ROW ≠ ENTITY`.

### 1.2 · Conta local não é empresa

```
22 contas locais provadas → 5 empresas distintas
```

### 1.3 · **`CROP_EXPERTISE ≠ CROP_X_ISSUE_EXPERTISE`** — medido, não herdado

Esta é a correção mais importante do delta, e eu a **medi contra o corpus científico**, não
apenas aceitei o veredito.

O artefato de identidade declara, ele mesmo, que *"a pessoa herda `CROP` e `ISSUE` da
**consulta** que a trouxe, nunca do título"*. Então o campo `ISSUE` não pode provar
expertise. A prova forte exige o termo do problema **no título de um trabalho**.

| pessoa | obras no corpus | `ISSUE=REPILO` pela consulta | **repilo no título** | concentração real |
|---|---:|---:|---:|---|
| **Blanca B. Landa** | 42 | 1 | **0** | XYLELLA 33 · VERTICILLIUM 19 |
| **Jesús Mercado-Blanco** | 27 | 3 | **0** | VERTICILLIUM 26 · XYLELLA 10 |

E o corpus inteiro: **4 documentos de 1.771** têm termo de repilo no título — e **nenhum
dos quatro é assinado por elas**. Os autores que aparecem são outros (Juan Moral em 2 dos
4, entre outros). *Isso é pista, não promoção:* nenhum deles passou pela mesma régua ainda.

```
ES_OLIVE_REPILO_CASE_EXPERTS = NOT_PROVED
```

**Nunca `0 experts exist`** — as duas pessoas existem, têm ORCID resolvido e são
especialistas de olivar. **Nunca `2 experts ready`** — nenhuma sustenta *repilo*.

**A mesma régua para todos.** Thierry C. Marcel tem 2 trabalhos com `ISSUE=SEPTORIA` pela
consulta e **0** com o termo no título. Se 1 REPILO não promove Landa, 2 SEPTORIA não
promove Marcel. Há prova disso.

### 1.4 · O conteúdo dos creators **não** sustenta o problema do caso

Agora que o Deep Corpus existe, dava para testar. Testei:

```
FICHAS COM ISSUE OBSERVADO NO CONTEÚDO ....... 5 de 10
CLASSES OBSERVADAS ........................... WEED · PEST · DISEASE
COBERTURA TOTAL .............................. PEST 16 · WEED 6 · DISEASE 5
```

O corpus classifica problema **no nível da linha ADAMA**, nunca no nível do problema
nomeado. Não existe `REPILO`, `FLAVESCENCE` nem `SEPTORIA` em nenhuma ficha — e há prova
disso, que falha se algum dia aparecer.

```
ISSUE_SPECIFIC_CREATOR_RELEVANCE = NOT_PROVED
```

⚠️ **E isso não reduz o valor do Creator Map.** Ele continua sendo rota de ativação e de
voz pública mesmo sem sustentar o problema do caso — são perguntas diferentes. O próprio
artefato já declara a fronteira: pode acrescentar `ACTIVATION_ROUTE_AVAILABLE` e
`RELEVANT_PUBLIC_VOICE_AVAILABLE`; **não** confirma `FIELD_PROBLEM`, `INCIDENCE`,
`MARKET_OPPORTUNITY` nem `PRODUCT_FIT`.

---

## 2 · OS TRÊS CASOS, CAMADA POR CAMADA

**`OBSERVED_IN_3_TEST_CASES`** — nunca `EAME_COVERAGE_RATE`. Três recortes escolhidos não
são amostra de nada.

| camada | ES · OLIVE × REPILO | IT · VINE × FLAVESCENCE | FR · CEREAL × SEPTORIA |
|---|---|---|---|
| **CREATOR_ACTIVATION_ROUTE** | **PROVED** (2 pessoas) | NOT_PROVED | NOT_PROVED |
| **CREATOR_ISSUE_RELEVANCE** | NOT_PROVED | NOT_PROVED | NOT_PROVED |
| **EXPERT_DIRECTORY_AVAILABILITY** | **PROVED** (2) | **PROVED** (2) | **PROVED** (2) |
| **EXPERT_CASE_EXPERTISE** | **NOT_PROVED** | **NOT_READY** | **NOT_PROVED** |
| **COMPETITOR_PUBLIC_COMM_ACCOUNTS** | PARTIAL (10 contas) | PARTIAL (8) | PARTIAL (4) |
| **FORESIGHT_PROVISIONAL** | PARTIAL | PARTIAL | PARTIAL |
| **META_PROVISIONAL** | NOT_READY | NOT_READY | NOT_READY |
| **TERRITORIAL_PROVISIONAL** | NOT_READY | NOT_READY | NOT_READY |

**A distinção que o booleano escondia.** `NOT_READY` do expert italiano **não** é
`NOT_PROVED`: o corpus científico disponível é espanhol (`institutions.country_code:es`),
e Quaglino e Mori têm **zero obras nele**. Ausência no corpus espanhol **não é ausência de
obra** — é ausência de régua. Dizer `NOT_PROVED` ali seria reprovar duas pessoas por um
recorte de consulta.

Cada camada carrega, separadamente: `ENTITY_AVAILABLE` · `CASE_KEY_MATCH_PROVED` ·
`CASE_ISSUE_MATCH_PROVED` · `CONTENT_AVAILABLE` · `CANONICAL_HANDOFF_AVAILABLE`.

---

# A · CREATOR MAP

```
CAPABILITY          = CREATOR_MAP
SOURCE_ARTIFACT     = data/samples/CREATOR-MAP-EAME/CREATOR-CAPABILITY-EAME.json
SOURCE_COMMIT       = 2018c5c
STATE               = FROZEN_WAITING_FOR_INTELLIGENCE · ACCEPTED (1 de 4)
ANALYTICAL_UNIT     = PERSON · FARM_BUSINESS_ENTITY   (duas, e nunca se somam)
SAFE_TO_PREPARE_NOW = YES
DECISION_QUESTION   = WHO COULD MARKETING EVALUATE/CALL?  — nunca *hire*
```

`REAL_FIELDS_AVAILABLE` · os 10 preservados por resultado + `ENTITY_TYPE`,
`ACTIVATION_STATE`, `ACTUAL_FARMER`, `COUNTRY`, `REGION`.
`MISSING_FIELDS` · `AUDIENCE_TYPE` · `REVALIDATION_NEEDED_AFTER` (`NOT_YET_DEFINED` **de
propósito**) · `PUBLIC_CONTACT` e `REGION` em várias fichas.
`JOIN_KEYS_PROVED` · `PERSON_ID` · `ENTITY_ID` · `BRAND` · `COUNTRY` · `CROP` · `OBSERVED_AT`
`JOIN_KEYS_NOT_PROVED` · `CROP → ISSUE` · `PERSON ↔ SCIENTIFIC_PERSON` · `PERSON ↔ META_AD`
(se a Meta achar uma destas pessoas num anúncio, vira `CREATOR_APPEARANCE_OBSERVED`;
`PAID_CREATOR_RELATION` só sobe com prova adicional)
`EXISTING_SURFACE_CANDIDATE` · `Radar/Casos` → detalhe do caso · `Acervo`
`CASE_LAYER_CANDIDATE` · SIM — camada `AUDIÊNCIA / ATIVAÇÃO`
`NEW_TOOL_CANDIDATE` · **`BOTH_POSSIBLE`**

---

# B · CREATOR DEEP CORPUS — capacidade nova, papel separado

```
CAPABILITY          = CREATOR_DEEP_CORPUS
SOURCE_ARTIFACT     = CORPUS-DELIVERY.json + CREATOR-CORPUS-FICHES.json
SOURCE_COMMIT       = a509c12
STATE               = CORPUS_V1 FROZEN · OPTIONAL_REFRESH_INPUT = READY_WITH_LIMITATIONS
ANALYTICAL_UNIT     = CREATOR_CONTENT_PROFILE   — unidade própria, de propósito
SAFE_TO_PREPARE_NOW = YES
DECISION_QUESTION   = WHAT THE MEASURED PUBLIC CORPUS SHOWS ABOUT THAT ENTITY
```

**Os dois papéis não se fundem.** O Creator Map diz **quem**; o corpus diz **o que o
material público mostra**. Fundi-los faria o corpus responder a pergunta do mapa. O
adaptador usa unidade própria e `juntar()` recusa a mistura — há prova disso.

`REAL_FIELDS_AVAILABLE` · `CHANNEL_STATE` · `N_CONTENT_ITEMS_REVIEWED` ·
`RECENT_ACTIVITY_BY_WINDOW` · `CONTENT_TYPES_OBSERVED` · `TEXT_SUBSTANCE` ·
`CROPS_OBSERVED` · `ISSUES_OBSERVED` · `AUDIENCE_EVIDENCE` · `BRANDS_OBSERVED` ·
`COMPETITOR_RELATIONSHIP_EVIDENCE` · `SPONSORED_CONTENT_EVIDENCE`
`MISSING_FIELDS` · imagem e vídeo **não foram lidos** (só texto) · região do fato não
extraída · `LOCAL_ADAMA_CONTEXT` `NOT_KNOWN` · audiência ainda `NOT_KNOWN` na maioria
`SEMANTIC_GUARDRAILS`
```
IDENTIDADE (mapa) != CONTEÚDO (corpus)
NOT_OBSERVED_IN_CORPUS != NO_RELATIONSHIP
ADAMA_RELEVANCE_SCORE = PROHIBITED_METRIC — somar oito eixos esconde o eixo vazio
FOLLOWERS DESC não é ordem de valor
```

---

# C · COMPETITOR FORESIGHT — freeze aceito

```
CAPABILITY          = COMPETITOR_FORESIGHT
SOURCE_HANDOFF      = docs/foresight/HANDOFF-INTELLIGENCE-COMPETITOR-FORESIGHT-EAME.md
SOURCE_BRANCH       = claude/eame-competitor-foresight
SOURCE_COMMIT       = 25194e3
FREEZE              = ACCEPTED
ADAPTER_STATE       = PREPARED (sobre freeze aceito) · FINAL_REFRESH_INPUT = NO
SAFE_TO_PREPARE_NOW = YES
DECISION_QUESTION   = WHAT HAS THIS COMPETITOR REGISTERED AND FILED — WHERE, AND WHEN?
                      NÃO: what is this competitor about to launch?
```

**Duas unidades analíticas, e elas não se somam:**

| unidade | o que é | volume na fixture |
|---|---|---|
| `TRADEMARK_REGISTRATION_LINK` | o **par** marca↔registro | 18 objetos |
| `COMPETITOR_COUNTRY_PRODUCT_TUPLE` | (competidor, país, produto normalizado) | 35 objetos |

Números do artefato: **9.661 marcas** · **1.683 cadeias ligadas** (209 ES · 334 IT ·
1.140 FR) · **126 falsos links recusados e publicados** · taxa de ligação **3,7 %** ·
`PROVED` 209 · `REJECTED_HOLDER_MISMATCH` 9 · `PARTIAL` 24 · `NOT_KNOWN` 5.335.

`MISSING_FIELDS` · **`CROP` e `ISSUE`** — nenhum dos três registros nacionais os traz.
**Sem eles a camada não entra no eixo cultura × praga**, que é o coração da convergência.
Este é o bloqueador estrutural da capacidade, não um detalhe.

`SEMANTIC_GUARDRAILS`
```
SAME_NAME != SAME_COMPETITOR_PRODUCT
NICE_CLASS != AGROCHEMICAL PROOF          (4.496 das 9.661 marcas caem na classe 5;
                                           2.551 são da Bayer, que tem divisão farma)
HISTORICAL_PRECEDENCE != OPERATIONAL_EARLY_WARNING   (mediana de 1.546 dias ≈ 4,2 anos)
NOT_JOINED != NOT_AVAILABLE != ZERO
PATENT_WATCH != REFUTED — uma ROTA foi refutada, não a camada
```

### `URBOLE_GUARD = PASS` — regressão obrigatória, e **exercida**

O portão exige **três concordâncias**: nome normalizado **+** grupo do titular **+** país.

```
URBOLE  marca SYNGENTA  ×  registro ES 24157 da ADAMA   →  REJECTED_HOLDER_MISMATCH
COLLIS  BASF ES         ×  COLLIS BASF IT               →  REJECTED_COUNTRY_MISMATCH
COLLIS  BASF ES         ×  COLLIS BASF ES               →  PROVED
COLLIS                  ×  REVYCARE                     →  NOT_KNOWN  (não é recusa)
```

Um portão sem dentes e um portão com zero recusas dão a mesma tela — por isso a recusa é
**provocada** nos testes, não apenas observada. E o adaptador **re-exerce** o portão sobre
cada par: se a fonte disser `PROVED` e o guard discordar, o objeto sai com o estado do
guard e a divergência declarada.

---

# D · COMPETITOR PUBLIC COMMUNICATION — preservado

```
IDENTITY_STAGE           = FROZEN          AUTHORIZED_ACCOUNTS = 22
MANIFEST_STAGE           = FROZEN          ES = 10 · IT = 8 · FR = 4
CONTENT_COLLECTION_STAGE = NOT_STARTED     ITEMS_COLLECTED = 0
OPTIONAL_REFRESH_INPUT   = NOT_READY
ANALYTICAL_UNIT          = COMPANY_LOCAL_ACCOUNT
```

Funil: 72 tentadas → 44 com link → 32 `PROVED` → **22 autorizadas**.
Plataformas: FACEBOOK 10 · YOUTUBE 7 · INSTAGRAM 5 · **LINKEDIN 0** (bloqueado: nenhuma
conta local provada). Empresas: SYNGENTA 8 · BAYER 7 · NUFARM 3 · BASF 3 · CORTEVA 1.

```
ACCOUNT != COMPANY
COUNTRY_SCOPE != PAGE_ROLE     (a DEKALB France recuperou a prova que tinha quando
                                PRODUCT_BRAND deixou de ser um estado de país)
ZERO hoje = NO_CONTENT_COLLECTION_EXECUTED · NUNCA COMPANY_NOT_COMMUNICATING
```

---

# E · RESEARCHER / EXPERT DIRECTORY — corrigido

```
CAPABILITY          = EXPERT_DIRECTORY
ANALYTICAL_UNIT     = SCIENTIFIC_PERSON
RESEARCHER_AS_EXPERT_DIRECTORY      = STRENGTHENED   (veredito do coordenador)
RESEARCHER_AS_DAILY_PERSON_SENSOR   = NOT_PROVED
SAFE_TO_PREPARE_NOW = YES
```

**Três degraus, e eles não se substituem:**

| degrau | estado | evidência |
|---|---|---|
| identidade científica | **PROVADA para 13** | ORCID resolvido, instituição declarada, obra em 2024+ |
| `PERSON ↔ PUBLIC_CHANNEL` | **PROVADO para 5 de 13** | 44 candidatos → 7 canais `PROVED`, 12 `PLAUSIBLE`, 25 `NOT_PROVED` |
| `PUBLIC_CONTENT ↔ SAME_PERSON` | **NÃO PROVADO para ninguém** | o modo usado do ator não devolve cargo nem empresa |
| **expertise no problema do caso** | **0 de 6** | ver 1.3 — medido contra o corpus |

```
IDENTITY_LINKAGE_BARRIER_REDUCED = YES
SCIENCE_TO_PUBLIC_VOICE_LINK     = CAPABILITY_NOW_TESTABLE   (não PROVED)
```

**Portão obrigatório antes de contar qualquer especialista dentro de um caso:**
`COUNTRY_MATCH` **+** `CROP_EXPERTISE_PROVED` **+** `ISSUE_EXPERTISE_PROVED`.
Implementado em `expertise_no_caso()`, que devolve os três separados — nunca um booleano.

---

# F · EARLY SIGNAL TERRITORIAL — em voo

```
STATE                = MISSÃO EM CURSO — sem handoff
MEASUREMENT_STATE    = PROVISIONAL_MEASUREMENT
SNAPSHOT             = 841fb54 · data/samples/TERRITORIAL/MEDICAO.json
SAFE_TO_PREPARE_NOW  = NO — nenhum adaptador construído
ANALYTICAL_UNIT      = CASE_SIGNAL (item territorial datado)
```

Medição intermediária, **não** estado final: 22 fontes tentadas · 17 alcançáveis ·
**3 provadas** · 13 itens · `CROP` 100 % · `COUNTRY` 69 % · `REGION` 69 % · **`ISSUE` 15 %**
· chave completa **8 %** · **0 sobreposições entre fontes**.

Sem `ISSUE`, o item não entra num caso `país × cultura × problema`.

---

# G · CLASSIFICAÇÃO — sem decidir nada

| capacidade | classificação | por quê |
|---|---|---|
| **COMPETITOR_PUBLIC_COMMUNICATION** | `CAN_FIT_EXISTING_SURFACE` | o casco já reservou as quatro linhas de competição no caso |
| **COMPETITOR_FORESIGHT** | `CAN_FIT_EXISTING_SURFACE` + `CASE_LAYER_CANDIDATE` | mesma camada de competição; **mas sem `CROP`/`ISSUE` não entra no eixo do caso** |
| **EXPERT_DIRECTORY** | `CASE_LAYER_CANDIDATE` | `CASE_ID` é a chave; **a expertise no problema precisa de portão** |
| **CREATOR_MAP** | **`BOTH_POSSIBLE`** | rota de ativação existe; relevância no problema não |
| **CREATOR_DEEP_CORPUS** | `CASE_LAYER_CANDIDATE` (dentro do creator) | é conteúdo sobre a entidade, não entidade |
| **EARLY_SIGNAL_TERRITORIAL** | `NOT_ENOUGH_EVIDENCE` | missão em curso |
| **META** | `NOT_ENOUGH_EVIDENCE` | branch não publicada em origin |

**Nenhum `FINAL_TOOL` foi escrito.**

---

# H · ONDE O CASCO V7 HOJE NÃO COMPORTA

| # | capacidade | o casco tem lugar? |
|---|---|---|
| G1 | especialista por caso | **sim** — aba `Ciência e pessoas`. Falta o **portão de expertise** |
| G2 | competição como camada do caso | **sim** — quatro linhas, todas em `NÃO SEI` |
| G3 | **creator / ativação** | **não.** Zero superfícies |
| G4 | **quinto relógio — "quem viu primeiro"** | **não** |
| G5 | **fila do que falta provar** | **não** |
| G6 | conta local × país × plataforma | **parcial** |
| **G7** | **marca (`BRAND`) como chave** | **não.** É a chave nova que o Foresight traz, e **não existe em nenhuma camada do casco** |
| **G8** | **conteúdo público de creator** (442 materiais, janelas 30/90 d) | **não** |

---

# I · PERGUNTAS QUE SÓ OS HANDOFFS FINAIS RESPONDEM

1. **O Foresight fecha `CROP`/`ISSUE`?** Sem isso a camada de concorrente não entra no eixo
   cultura × praga — e é o coração da convergência.
2. **A Meta será publicada em `origin`?** Hoje os números dela chegam em segunda mão.
3. **O territorial fecha `ISSUE` acima de 15 %?**
4. **Os 12 canais `PLAUSIBLE` de pesquisadores sobem para `PROVED`?**
5. **Existe corpus científico não-espanhol?** Sem ele, `EXPERT_CASE_EXPERTISE` de IT e FR
   fica `NOT_READY` para sempre — e `NOT_READY` não é `NOT_PROVED`.
6. **Alguém aplica a régua de expertise aos autores que realmente publicam sobre repilo?**
   O corpus os mostra; nenhum passou pelo portão.

---

# ENTREGA

```
PRODUCT_IMPLEMENTATION_MODE = NOT_ENTERED
FINAL_REFRESH_EXECUTED      = NO
CASCO_V7_MODIFIED           = NO
REAL_DATA_WIRED             = NO
MANDATORY_HANDOFFS_ACCEPTED = 2/4

CAPABILITIES_PREPARED  = 5   CREATOR_MAP · CREATOR_DEEP_CORPUS · COMPETITOR_FORESIGHT ·
                             COMPETITOR_PUBLIC_COMMUNICATION · EXPERT_DIRECTORY
CAPABILITIES_REFUSED   = 2   EARLY_SIGNAL_TERRITORIAL (em voo) ·
                             META (branch não publicada em origin)

ADAPTERS_PREPARED      = 6   creator_capability · creator_deep_corpus ·
                             foresight_crosswalk · foresight_three_layer ·
                             public_comm · expert_directory
                             + urbole_guard() · expertise_no_caso() · juntar() · contar()

TESTS_ADDED            = 63  (suíte 329 → 392, OK, 0 falhas)
STRUCTURAL_GAPS_FOUND  = 8   G1..G8 — dois novos neste delta (BRAND, conteúdo de creator)
READY_FOR_FINAL_REFRESH_LATER = YES

EXACT_BLOCKERS
  1  FORESIGHT sem CROP e ISSUE — a camada nao entra no eixo cultura x praga
  2  META: branch claude/eame-meta-competitor NAO publicada em origin (13 heads medidas)
  3  PUBLIC COMM: CONTENT_COLLECTION_STAGE = NOT_STARTED, 0 itens
  4  TERRITORIAL sem handoff; ISSUE em 15 %, chave completa em 8 %
  5  EXPERT: expertise no problema NAO PROVADA em 0 de 6 pessoas dos tres recortes
  6  EXPERT IT e FR: NAO MENSURAVEL — o corpus cientifico disponivel e espanhol
  7  CREATOR: ISSUE do conteudo e classe de linha, nunca problema nomeado
  8  PERSON <-> PUBLIC_CHANNEL de pesquisador provado em 5 de 13; conteudo em ninguem
```
