# BOT DE FONTES V2 — PLANO

> **DOCUMENTO DE PROPOSTA. NÃO É LEI, NÃO É RUNTIME, NÃO ESTÁ LIGADO A NADA.**
>
> Não cria Bíblia, não emenda Bíblia, não altera contrato executável, não toca
> Collection, Admission, Sala, Intelligence nem System Map. Desenha um
> departamento e mede o que já existe para o sustentar.

```
MISSAO      BOT-DE-FONTES-V2-DESENHO
DATA        2026-09-20
TRUNK       claude/it-trunk-v1 @ 606974c3c4559c32307b8f68ec7d7eb925379cc6
BRANCH      claude/bot-de-fontes-v2-plano
WORKTREE    C:/bot-fontes-v2
ESTADO      PROPOSTA · POR DECIDIR PELO DONO
MERGE       NÃO FEITO, E NÃO PEDIDO
```

---

# 0 · O ACHADO QUE MUDOU O DESENHO

O enunciado pedia seis artefactos novos: `SOURCE_FEEDBACK`, `SOURCE_NEED`,
`SCOUT_BRIEF`, `SOURCE_NEED_RESPONSE`, `EXPECTED_YIELD`, `OBSERVED_YIELD`.

Medido antes de escrever: **quatro dos seis já existem com outro nome e com dono
provado.** Criá-los daria dois donos à mesma regra — o que a `INT-LAW-000`
proíbe, e o que a própria Bíblia da Intelligence já recusou uma vez, em texto:

```
UMA BIBLIA QUE CRESCE POR ACUMULACAO DEIXA DE SER LEI E PASSA A SER ARQUIVO.
```

| pedido no enunciado | já existe como | dono medido |
|---|---|---|
| `SOURCE_FEEDBACK` | `SOURCE_COLLECTION_ADVICE` | Bíblia Intelligence §36 · `INT-LAW-290..299`, `302` |
| `SOURCE_NEED` | `COLLECTION_GAP` | Bíblia Intelligence §15 · `INT-LAW-150..153` |
| `EXPECTED_YIELD` / `OBSERVED_YIELD` | `CUSTO_ESPERADO`/`GANHO_ESPERADO` × `CUSTO_REAL`/`GANHO_REAL` | `leis/gestao_da_coleta.py` |
| ciclo de vida da fonte | `CICLO_DE_VIDA` (8 estados) | `leis/aprender_com_a_fonte.py` |
| `SCOUT_BRIEF` | **não existe** (0 ficheiros) | — |
| `SOURCE_NEED_RESPONSE` | **não existe** (0 ficheiros) | — |

**Consequência para o plano:** o Bot de Fontes V2 não nasce inventando
vocabulário. Nasce **ligando contratos que já foram escritos e nunca foram
usados juntos**, e acrescentando só os dois objectos que faltam de facto.

---

# 1 · CURRENT_STATE — o que existe hoje, medido

## 1.1 · CURRENT_SOURCE_MODEL

A fonte já tem um modelo escrito, repartido por sete ficheiros, e nenhum deles
é redundante:

```
docs/fontes/ATLAS-DE-FONTES-EAME.md          dono do SOURCE_ID            (COL-LAW-208)
system-map/data/sources.generated.json       leitura única derivada       (COL-LAW-053)
candidatas/FONTES-CANDIDATAS.json            a fila, antes de ser fonte   (COL-LAW-053, degrau 1)
leis/fonte_do_atlas.py                       leitor/validador do Atlas
leis/territorios.py                          T1..T13, derivado do Atlas
leis/relevancia_da_fonte.py                  o par (FONTE × PROPÓSITO) — a PORTA
leis/aprender_com_a_fonte.py                 ciclo de vida, papéis, rendimentos — a FITA MÉTRICA
```

Leis canónicas que já governam a fonte, na Bíblia da Coleta:

```
COL-LAW-026   circuit breaker — proteção da fonte          IT: ABSENT
COL-LAW-028   a fonte tem saúde (4 estados)                IT: IMPLEMENTED
COL-LAW-029   source drift + controlo negativo (5 estados) IT: IMPLEMENTED
COL-LAW-053   cadastro único e reconciliado · 4 degraus    IT: IMPLEMENTED
COL-LAW-205   a fonte é estável; o endpoint é substituível IT: PARTIAL
COL-LAW-208   o registry é a memória da coleta             IT: PARTIAL
```

E na Bíblia da Intelligence, a jusante:

```
INT-LAW-150..153   COLLECTION_GAP é first-class; Intelligence pede prova, não rota
INT-LAW-290..299   SOURCE PERFORMANCE mede, não decide
INT-LAW-302        `MORE` exige REPROCESSING_CHECKED = SIM
```

## 1.2 · CURRENT_SOURCE_OWNERS

```
IDENTIDADE DA FONTE        docs/fontes/ATLAS-DE-FONTES-EAME.md
LEITURA ÚNICA              system-map/data/sources.generated.json
FILA (pré-fonte)           candidatas/FONTES-CANDIDATAS.json + candidatas/fonte_nova.py
RELEVÂNCIA (porta)         leis/relevancia_da_fonte.py + LIVRO-DE-RELEVANCIA-DE-FONTE.json
CICLO DE VIDA / MEDIDAS    leis/aprender_com_a_fonte.py
NECESSIDADE / DECISÃO      leis/gestao_da_coleta.py
EXPERIÊNCIA / PROMOÇÃO     leis/evolucao.py
TELEMETRIA DA CORRIDA      leis/telemetria.py
SAÚDE MEDIDA              medidas/source_health.py · regras/italy_source_health.mjs
CONTRATO EXECUTÁVEL        regras/italy_contracts.mjs
EXECUTOR (por TERRITÓRIO)  pedido/receitas.py::EXECUTORES
CONTRIBUIÇÃO A JUSANTE     Bíblia Intelligence §36 (desenhada, não implementada)
```

**Não há dono para:** descoberta sistemática, brief de descoberta, resposta a um
gap, e a ligação entre os owners acima. É exactamente esse buraco que o Bot de
Fontes V2 ocupa — e é um buraco de **coordenação**, não de vocabulário.

## 1.3 · CURRENT_SOURCE_LIFECYCLE

Dois ciclos coexistem hoje e **não estão ligados um ao outro**:

```
A ESCADA DE CADASTRO (COL-LAW-053)          O CICLO DE VIDA (aprender_com_a_fonte.py)
1 CANDIDATA                                  DISCOVERED
2 REGISTADA   (exige exemplo real)           SCREENED
3 CONTRATADA                                 TRIAL
4 AUTOMATICA                                 PROBATION
                                             ACTIVE
                                             DEGRADED
                                             QUARANTINED
                                             RETIRED
```

A escada diz **onde a ficha está guardada**. O ciclo diz **em que estado de
confiança a fonte está**. Nenhum código liga os dois: `CICLO_DE_VIDA` é
importado por 4 ficheiros, e **nenhum deles é um writer de registry** —
`leis/relevancia_da_fonte.py`, `system-map/scripts/censo_da_observabilidade.py`
e dois testes.

```
SCHEMA EXISTS != WRITER USES IT
```

## 1.4 · Os números, medidos hoje no trunk

```
SYSTEM_MAP_SOURCE_COUNT            213       (system-map/data/sources.generated.json)
  por país          ITALIA 160 · ESPANHA 34 · EUROPA 13 · FRANCA 6
  por verdict       GREEN 91 · YELLOW 85 · PARCIAL 27 · «NAO SEI» 10
  com contract      5 / 213
  sabe_coletar      5 / 213   (campo subdeclara — ver skill de prontidão)
  update_frequency  «NÃO SEI» 93 + vazio 41 = 134 / 213 sem valor   (com valor: 79)

CANDIDATE_COUNT                    241       (candidatas/FONTES-CANDIDATAS.json)
  estado EM_ANALISE                241 / 241   ← a fila inteira está parada
  estado PROMOVIDA                   0
  estado RECUSADA                    0

CONTRATOS_EXECUTAVEIS_NO_TRUNK      14       (regras/italy_contracts.mjs)
  ROUTE_TYPE  PREDICTABLE 4 · DISCOVERED 3 · APPLICATION 3 · STATIC 2 · BROWSER 2

LEDGER DA COLETA (data/collection-ledger/italy/)
  RUNS                              34
  OBSERVATIONS                     184
  SOURCE_ID DISTINTOS OBSERVADOS     7       ← 7 de 213 fontes já foram tocadas
  HEALTH_STATE                     HEALTHY 153 · FAILED 31
  OBSERVATION_RESULT               SEEN_AGAIN 109 · NEW_DOCUMENT 34 · DISCOVERY_FAILED 19
                                   TRANSPORT_OR_EMPTY 12 · BASELINE_DOCUMENT 10
  CADENCE_STATE                    CADENCE_UNKNOWN 106 · UPDATED 44 · EXPECTED_NO_CHANGE 3 · vazio 31

SALA DE ESPERA
  MORADA_EXISTE                    False
  TOTAL_WAITING_ROOM_RECORDS           0
```

> **A conta que define a missão do departamento:** 213 fontes registadas,
> 241 candidatas paradas, e **7 fontes alguma vez observadas**. O gargalo não é
> descobrir. É atravessar.

## 1.5 · Vocabulário do enunciado que não existe em ficheiro nenhum

Contagem por `git grep -l -i` na árvore inteira do trunk:

```
EXPECTED_YIELD      0 ficheiros
OBSERVED_YIELD      0 ficheiros
SCOUT_BRIEF         0 ficheiros
SOURCE_FEEDBACK     0 ficheiros
SOURCE_NEED         0 ficheiros
SOURCE_READY        0 ficheiros
SCOUT               0 ficheiros   (os 6 hits são a string «SCOUT» dentro de CSVs de dados)
```

---

# 2 · CURRENT_GAPS

```
G1  A FILA NÃO ANDA
    241 candidatas, todas EM_ANALISE, zero PROMOVIDA, zero RECUSADA.
    `candidatas/fonte_nova.py` sabe registar e sabe listar. Ninguém decide.
    → SOURCE_GAP operacional, não técnico.

G2  O CICLO DE VIDA NÃO É ESCRITO EM LADO NENHUM
    `CICLO_DE_VIDA` tem 8 estados e 0 writers. Nenhuma ficha do Atlas nem do
    derivado tem campo de estado de ciclo. O estado de uma fonte hoje é uma
    leitura de prosa (`verdict`, `collection`, `automation`), não um valor.

G3  O REGISTRY NÃO GUARDA SAÚDE NEM CADÊNCIA
    COL-LAW-208 lista LAST_ATTEMPT · LAST_SUCCESS · LAST_FAILURE · HEALTH ·
    CHANGE_RATE como campos que a ficha PODE ter. Nenhum existe no derivado
    (22 campos, nenhum deles de saúde). A saúde existe — está no LEDGER, por
    observação, e morre lá: ninguém a devolve à fonte.
    → CAPABILITY_GAP de escrita, não de medição.

G4  O RUN NÃO DECLARA SOURCE_ID
    0/34 runs têm SOURCE_ID. 184/184 observações têm.
    O elo SOURCE→RUN só é reconstruível por junção via observação. Funciona
    hoje, com 7 fontes. Não é linhagem durável.

G5  DEPOIS DA ADMISSÃO, A LINHAGEM PARA
    Sala de Espera: morada não existe, 0 registos. CLAIM/FACT não tem módulo
    de runtime. Logo `SOURCE → CLAIM → FINDING` é hoje INDEMONSTRÁVEL, e
    INT-LAW-294 manda dizer exactamente isso: CONTRIBUTION = UNKNOWN.

G6  EXPECTED vs OBSERVED NÃO EXISTE PARA FONTE
    O padrão está escrito para DECISÃO (`CUSTO_ESPERADO` × `CUSTO_REAL` em
    gestao_da_coleta) e nunca foi aplicado a FONTE.

G7  NÃO HÁ DESCOBERTA DIRIGIDA
    Zero ocorrências de SCOUT. A descoberta é feita por missão humana ad-hoc, e
    o que se aprendeu numa não orienta a seguinte.

G8  CADÊNCIA DECLARADA É MAIORITARIAMENTE DESCONHECIDA
    134/213 fontes sem update_frequency com valor (93 «NÃO SEI» + 41 vazio);
    106/184 observações com CADENCE_STATE = CADENCE_UNKNOWN.
    A lei que separa declarada de observada existe. Os dois valores faltam.
```

---

# 3 · FASE 2 — O DONO

```
O BOT DE FONTES É DONO DA FONTE ENQUANTO ELA AINDA NÃO É COLETÁVEL,
E DA MEDIDA DELA DEPOIS DE O SER.

A COLLECTION É DONA DA COLETA, SEMPRE.
```

Ele existe para uma frase só: **a Collection não deve descobrir como ligar uma
fonte no momento em que vai colher.** Hoje descobre — é isso que a fila de
wiring e os 19 `DISCOVERY_FAILED` do ledger dizem.

### O que o Bot de Fontes PODE

descobrir · qualificar · validar existência e identidade · deduplicar ·
classificar (tipo, território, país, idioma) · propor `SOURCE_ID` ao owner do
Atlas · preparar o pacote de relevância para decisão humana · medir saúde,
cadência e rendimento da fonte · manter o perfil vivo · detectar fonte morta,
mudada ou substituída · medir cobertura e gaps · entregar fila de wiring ao
owner correcto · **sugerir** cadência.

### O que o Bot de Fontes NÃO PODE

```
relaxar policy                      → falha fechado, bloqueia, segue para outra fonte
inventar SOURCE_ID ou DOCUMENT_ID   → UNKNOWN, sempre
alterar FACT_TIME / FACT_LOCATION   → não é dono do fato
alterar Admission ou a Sala         → COLLECTION
escrever RESULTADO no livro de relevância por iniciativa própria → DECISÃO HUMANA
comprar serviço / usar credencial nova / abrir rota paga → AUTORIZAÇÃO DE GASTO
escrever o `case` de rota no coletor → SCRAP ENGINEER
executar Big Collection             → COLLECTION
decidir o que a evidência significa → INTELLIGENCE
```

Regra de bloqueio, herdada de `leis/gestao_da_coleta.py`:

```
NEEDS_HUMAN      a política não cobre este caso
DEFER_UNKNOWN    falta medir antes de decidir
```

Nenhum dos dois é uma falha. São os dois estados em que o Bot **para e avança
para a fonte seguinte**, com o motivo escrito.

### A fronteira, em três frases

```
SOURCE CURATOR / BOT   QUAL fonte precisamos, e o que ela rende
SCRAP ENGINEER         COMO se adquire daquela fonte
COLLECTION             EXECUTA, cunha o RUN, preserva RAW, segue até à Sala
```

---

# 4 · PROPOSED_SOURCE_LIFECYCLE

**Não se adoptam os nomes do enunciado.** Adopta-se o `CICLO_DE_VIDA` que já
existe, e mapeia-se o enunciado para ele.

| enunciado | estado canónico reutilizado | porquê |
|---|---|---|
| `DISCOVER` | `DISCOVERED` | igual |
| `QUALIFY` | `SCREENED` | igual |
| `ONBOARD` | `TRIAL` | «está a ser experimentada, com prazo» |
| `CANARY` | `PROBATION` | «já serviu, e ainda não é de confiança» |
| `READY` | **não é um estado** — ver 4.2 | `READY` já significa *item admitido na Sala*. Reusar a palavra criaria dois donos |
| `ACTIVE` | `ACTIVE` | igual |
| `MONITOR` | `ACTIVE` + `DEGRADED` | monitorizar é uma acção contínua, não um estado |
| `REPAIR` | `QUARANTINED` + fila de wiring | reparar é uma decisão escrita, não um estado |

> **`READY` é a colisão mais cara deste desenho.** Nesta casa, `READY` designa
> um item que atravessou a Admission e chegou à Sala de Espera (`COL-LAW-043`).
> Um estado de fonte chamado `READY` far-se-ia ler, seis meses depois, como se a
> fonte tivesse entrado na Sala. O plano usa `SOURCE_COLLECTION_READY`, e nunca
> `READY` sozinho.

## 4.1 · A tabela dos estados

Para cada estado: entrada, saída, dono, acções permitidas, motivos de bloqueio.

### `DISCOVERED`
```
ENTRY      alguém viu que existe. URL ou nome, nada mais.
EXIT       para SCREENED quando alguém abriu e olhou. Para RETIRED se for lixo.
OWNER      BOT DE FONTES
ALLOWED    registar na fila (candidatas/fonte_nova.py), normalizar URL, dedupe
BLOCK      DUPLICATE_IN_QUEUE · DUPLICATE_IN_ATLAS  (dedupe é DOIS degraus)
NOTA       fonte_nova.py não atribui SOURCE_ID, e está certo: o ID nasce na promoção.
```

### `SCREENED`
```
ENTRY      existência e identidade provadas ao vivo; red team passado
           (domínio sequestrado · homónimo · rebranding · loja disfarçada)
EXIT       para TRIAL quando há exemplo real capturado e preservado
OWNER      BOT DE FONTES
ALLOWED    probe leve, classificação, propor território, propor oficialidade
BLOCK      NON_GOV_REQUIRES_EVIDENCE · INSTITUTIONAL_ENTRY_POINT (fica YELLOW)
           BLOCKED / UNREACHABLE — CAPABILITY_GAP, nunca DEAD
```

### `TRIAL`
```
ENTRY      MANIFEST.json com amostra real guardada; ficha no Atlas (degrau 2)
EXIT       para PROBATION quando existe contrato executável e o canário do SHAPE passou
OWNER      BOT DE FONTES (ficha) · SCRAP ENGINEER (contrato) · COLLECTION (canário)
ALLOWED    propor SOURCE_ID ao owner do Atlas · preparar pacote de relevância
BLOCK      NO_SAMPLE · RELEVANCE_NAO_AVALIADA · CONTRATO_AUSENTE
NOTA       ter MANIFEST NÃO prova rota. É história de que alguém, um dia, guardou bytes.
```

### `PROBATION`
```
ENTRY      canário PASS na mesma janela + endereço vivo + portão de relevância AUTORIZA
EXIT       para ACTIVE após N corridas com HEALTH_STATE estável e OBSERVED_YIELD registado
OWNER      BOT DE FONTES mede · COLLECTION corre
ALLOWED    medir EXPECTED vs OBSERVED pela primeira vez
BLOCK      CORRIDA_SUCCESS_COM_ZERO_ITENS (é CATALOG, não colheita)
           DISCOVERY_FAILED (falta o ramo de rota — SCRAP, não a fonte)
NOTA       `N` NÃO SE FIXA AQUI. Fixá-lo sem medição inventaria a medida que falta.
```

### `ACTIVE`
```
ENTRY      saúde medida e estável, rendimento observado, cadência com valor
EXIT       DEGRADED se a saúde cai · QUARANTINED por decisão · RETIRED por fim
OWNER      BOT DE FONTES (perfil) · COLLECTION (corrida)
ALLOWED    sugerir cadência · alimentar o painel · receber SOURCE_COLLECTION_ADVICE
BLOCK      —
```

### `DEGRADED`
```
ENTRY      COL-LAW-028: usável, mas o contrato mudou — campo novo, identidade
           duplicada, volume fora de ±10%
EXIT       ACTIVE se recupera · QUARANTINED se a decisão for suspender
OWNER      BOT DE FONTES
ALLOWED    abrir item na fila de wiring com MISSING_COMPONENT nomeado
BLOCK      —
NOTA       DEGRADED é uma MEDIDA. Não é uma decisão e não é um fim.
```

### `QUARANTINED`
```
ENTRY      decisão escrita, com quem decidiu e porquê. Pode voltar.
EXIT       ACTIVE por decisão · RETIRED por decisão
OWNER      DECISÃO HUMANA, registada
ALLOWED    parar de martelar (COL-LAW-026, circuit breaker)
BLOCK      —
```

### `RETIRED`
```
ENTRY      prova de fim: domínio extinto, entidade encerrada, substituída
EXIT       nenhuma
OWNER      DECISÃO HUMANA
NOTA       RETIRAR NÃO APAGA HISTÓRIA. O que ela trouxe continua a valer.
```

## 4.2 · `SOURCE_COLLECTION_READY` — um predicado, não um estado

O «READY» do enunciado é a **conjunção de cinco prontidões medidas em separado**
mais o canário. Publicar um booleano sem os componentes esconde qual falhou.

```
IDENTITY_READY           ficha + prova nativa reproduzida ao vivo
RESOLVER_READY           sources.generated.json tem FULL_SOURCE_RECORD
SEARCH_CONTRACT_READY    entrada em regras/italy_contracts.mjs
RELEVANCE_READY          leis/relevancia_da_fonte.py → portao() = AUTORIZA
COLLECTION_FEASIBILITY   território ∈ pedido/receitas.py::EXECUTORES e ramo de rota existe
CANARY_PASS              corrida real do SHAPE, na mesma janela

SOURCE_COLLECTION_READY = todas as seis, na mesma janela de medição.
Qualquer subconjunto = HOT_NEEDS_WIRING | WARM | BLOCKED | PENDING_RELEVANCE.
```

```
VERDICT: GREEN no Atlas  é veredito de IDENTIDADE.
NÃO é autorização de coleta.
```

---

# 5 · SOURCE_PROFILE_SCHEMA — o perfil vivo

Um perfil por `SOURCE_ID`. **Referencia; não copia.** A identidade continua no
Atlas; a saúde continua no ledger; a relevância continua no livro. O perfil é a
junção, e declara de onde cada valor veio.

Cada campo traz um selo de proveniência obrigatório:

```
AVAILABLE_NOW                 já é mensurável hoje, com a árvore actual
NEEDS_COLLECTION_TELEMETRY    falta SOURCE_ID no RUN / falta corrida
NEEDS_CLAIM_FACT              falta a camada CLAIM/FACT
NEEDS_INTELLIGENCE            falta a Intelligence a correr
```

## IDENTIDADE — `AVAILABLE_NOW`
```
SOURCE_ID · NAME · PUBLISHER · COUNTRY · TERRITORY · TERRITORY_NAME
LANGUAGE · SOURCE_TYPE · CANONICAL_URL · OFFICIALITY_EVIDENCE
LIFECYCLE_STATE            ← CAMPO NOVO. Hoje não existe em ficheiro nenhum.
LIFECYCLE_CHANGED_AT · LIFECYCLE_CHANGED_BY · LIFECYCLE_REASON
```
> `SOURCE_LOCATION ≠ FACT_LOCATION`. O perfil guarda onde a fonte está
> estabelecida. Nunca deduz daí onde o facto ocorreu.

## FUNÇÃO — `AVAILABLE_NOW` (parcial)
```
PAPEL          EVIDENCE | DISCOVERY | EARLY_WARNING | CORROBORATION | CONTEXT | REFERENCE
               ← reutiliza PAPEIS de leis/aprender_com_a_fonte.py
PROPOSITOS     os pares (SOURCE_ID × PROPÓSITO) já avaliados no livro de relevância
GEOGRAFIA_POTENCIAL · TOPICOS
```
> O papel **muda o que conta como bom**. Uma fonte `DISCOVERY` que se repete
> está a falhar; uma `CORROBORATION` que se repete está a fazer o trabalho dela.

## AQUISIÇÃO — `AVAILABLE_NOW` para 14 fontes, `NEEDS_COLLECTION_TELEMETRY` para as outras 199
```
ENDPOINTS[]                     COL-LAW-205: a fonte tem VÁRIOS, e eles são do ENDPOINT
PREFERRED_ROUTE · FALLBACK_ROUTES
ROUTE_TYPE · RETRIEVAL_METHOD   ← lido do contrato, nunca do Content-Type
SHAPE                           PDF_DIRECT | PDF_DISCOVERY_PAGE | HTML_PUBLIC | JSON_API | BROWSER_PUBLIC
ACCESS_TYPE                     PUBLIC | REQUIRES_AUTH | BROWSER_ONLY | PAID
HAS_EXECUTOR · HAS_ROUTE_BRANCH · CANARY_PROVEN_SHAPE
POLICY_NOTES · COST_NOTES
```
> **Arrumação (COL-LAW-205).** `ETag`, checksum, schema fingerprint e
> `last_successful_route` são do **endpoint**. País, publisher e saúde
> institucional são da **fonte**. A ficha da fonte não é uma lixeira de campos.

## SAÚDE — `AVAILABLE_NOW` no ledger, `NEEDS_COLLECTION_TELEMETRY` para devolver à fonte
```
HEALTH                  HEALTHY | DEGRADED | FAILED | UNKNOWN     (COL-LAW-028)
LAST_ATTEMPT · LAST_SUCCESS · LAST_FAILURE · LAST_CHANGE
LAST_SUCCESSFUL_ROUTE
DRIFT_STATE             BASELINE_ESTABLISHED | NO_NEW_VERSION | NEW_VERSION_IDENTICAL
                        | NEW_VERSION_CHANGED | SOURCE_FAILED                (COL-LAW-029)
ROUTE_HEALTH            ← separado. SAÚDE DA FONTE != SAÚDE DA ROTA
```
> `UNKNOWN` permanece `UNKNOWN`. `VPN_FAILURE ≠ SOURCE_FAILURE`.
> Medido no ledger: 31 observações `FAILED`, e é preciso saber quantas foram do
> egresso e não da fonte antes de qualquer uma manchar um perfil.

## CADÊNCIA — parcialmente `AVAILABLE_NOW` (153/184 observações já a gravam)
```
DECLARED_FREQUENCY      o que a fonte DIZ
OBSERVED_FREQUENCY      o que ela FAZ, medido
CADENCE_STATE           UPDATED | EXPECTED_NO_CHANGE | CADENCE_UNKNOWN
EXPECTED_NEXT_UPDATE
CHANGE_RATE
CURRENT_COLLECTION_CADENCE · BACKFILL_POLICY · WATERMARK
```
> `CADÊNCIA DECLARADA != CADÊNCIA OBSERVADA`. Um portal que promete boletim
> semanal e publica de mês a mês não está avariado — está a mentir na promessa.
> **A diferença entre os dois é informação**, e é a que vai alimentar a cadência
> adaptativa.

## RENDIMENTO — ver §6
## QUALIDADE — `NEEDS_COLLECTION_TELEMETRY`
```
FACT_TIME_COVERAGE · FACT_LOCATION_COVERAGE · JOIN_KEY_COMPLETENESS
ADMISSION_OUTCOME_DISTRIBUTION      READY | REJECTED | ERROR | UNKNOWN | NOT_RUN
```
> Nunca somar `REJECTED` com `ERROR` nem com `NOT_RUN`. São quatro portas
> diferentes, e achatá-las apaga a única informação que diz o que fazer a seguir.

## VALOR PARA A INTELLIGENCE — `NEEDS_CLAIM_FACT` + `NEEDS_INTELLIGENCE`
```
SOURCE_ANALYTIC_CONTRIBUTION[]   arestas provadas de lineage    (Bíblia INT §36.2)
SOURCE_CONTRIBUTION_PROFILE      o agregado contextual
SUPPORT_VALUE · CONTRADICTION_VALUE   ← NUNCA somados num saldo (INT-LAW-295)
LAST_USEFUL_SIGNAL_AT
SAMPLE_SIZE · CONFIDENCE
EXPLORATION_STATE                NEVER_SAMPLED | UNDER_SAMPLED | ESTABLISHED
PROTECTED_CATEGORY               MANDATORY_SOURCE | STRATEGIC_SOURCE | LOW_FREQUENCY_HIGH_IMPORTANCE
```
> **Estado actual honesto:** para 213 de 213 fontes, este bloco inteiro é
> `UNKNOWN` — a Sala está vazia, CLAIM/FACT não existe em runtime, e
> `INT-LAW-294` manda dizer `UNKNOWN`, não zero.

## O QUE O PERFIL RECUSA
```
NÃO CRIAR:  SOURCE_SCORE · RANKING_UNICO · NOTA_DE_0_A_100 · SOURCE_GLOBAL_SCORE
```
> Proibido pelas duas Bíblias ao mesmo tempo — `leis/aprender_com_a_fonte.py`
> (`NAO_CRIAR`) e `INT-LAW-293`. Um número só esconde qual das medidas o
> produziu, e a partir daí ninguém consegue discutir a decisão: só obedecer-lhe
> ou ignorá-la, e as duas coisas são más.

---

# 6 · EXPECTED_YIELD e OBSERVED_YIELD

Não é vocabulário novo — é o padrão `ESPERADO × REAL` de
`leis/gestao_da_coleta.py` (`CUSTO_ESPERADO`/`CUSTO_REAL`,
`GANHO_ESPERADO`/`GANHO_REAL`) aplicado à fonte pela primeira vez.

## EXPECTED_YIELD_MODEL — a estimativa do onboarding
```
SOURCE_ID · ESTIMATED_AT · ESTIMATED_BY · BASIS      ← de onde saiu o número
WINDOW
EXPECTED_ITEMS_PER_RUN · EXPECTED_ITEMS_PER_PERIOD · PERIOD
EXPECTED_BYTES_PER_RUN
EXPECTED_NEW_CONTENT_RATIO
CONFIDENCE          LOW | MEDIUM | HIGH | UNKNOWN
```
`BASIS` é obrigatório e tem vocabulário fechado:
```
SAMPLE_OBSERVED     contámos o que estava na amostra guardada
SOURCE_DECLARED     a fonte diz que publica X por semana
ANALOGOUS_SOURCE    outra fonte do mesmo shape e território rende Y
GUESS               ninguém mediu    ← permitido, desde que dito
```

## OBSERVED_YIELD_MODEL — o que aconteceu
```
SOURCE_ID · RUN_ID · WINDOW_START · WINDOW_END · MEASURED_AT
ITEMS_RETURNED · ITEMS_HARVESTED      ← CATALOG != COLHEITA
NEW_ITEMS · SEEN_AGAIN · CHANGED_IN_PLACE
BYTES
DUPLICATE_RATE · CHANGE_RATE
READY_YIELD                           quanto chegou a ser admitido
UNIQUE_YIELD                          quanto mais ninguém trouxe
SAMPLE_SIZE                           ← obrigatório
```

## As cinco regras que este modelo existe para impor

```
1. AS UNIDADES NÃO SE FUNDEM
   items/run · items/day · items/week · items/month · bytes · new-content ratio
   Não há métrica única. Um PDF que entra e 40 páginas que saem não é 4000% —
   é uma divisão entre dois grãos diferentes (leis/telemetria.py).

2. A ESTIMATIVA NÃO SE REESCREVE
   Append-only. Quando o observado chega, a estimativa passada FICA, com a data.
   Reescrevê-la seria fingir que sempre soubemos o resultado.

3. CORRIDA SUCCESS != ITENS COLHIDOS
   Medido no ledger: 19 DISCOVERY_FAILED e 12 TRANSPORT_OR_EMPTY em 184.
   Um executor pode devolver CATALOG com recibo SUCCESS e zero obra.

4. COLETADO != ADMITIDO
   UNIQUE_YIELD alto com READY_YIELD baixo é uma fonte que dá trabalho e não
   entrega. Um número só não distingue os dois casos.

5. TAXA SEM AMOSTRA É IMPRESSÃO
   2 em 2 e 200 em 200 dão ambos «100%». SAMPLE_SIZE viaja com a taxa, sempre.
```

---

# 7 · SOURCE_TELEMETRY_REQUIRED — a matriz de elos

Cadeia a provar: `SOURCE → RUN → OBSERVATION → ARTIFACT → DERIVED → ADMISSION →
CLAIM/FACT → FINDING → OPPORTUNITY`.

| # | ELO | CURRENTLY_PROVABLE | MISSING_FIELD | MISSING_OWNER | PHASE_NEEDED |
|---|---|---|---|---|---|
| 1 | `SOURCE → RUN` | **PARCIAL** — 0/34 runs declaram SOURCE_ID; reconstruível por junção via observação | `SOURCE_ID` em `CAMPOS_DO_RUN` (o contrato já o lista; o writer do ledger não o grava) | COLLECTION | STEP 2 |
| 2 | `RUN → OBSERVATION` | **SIM** — 184/184 com RUN_ID; 34/34 RUN_ID resolvem no ledger de runs | — | — | já existe |
| 3 | `SOURCE → OBSERVATION` | **SIM** — 184/184 com SOURCE_ID | — | — | já existe |
| 4 | `OBSERVATION → ARTIFACT (RAW)` | **PARCIAL** — `RAW_PATH` + `RAW_SHA256` presentes; medido: **0 de 43** artefactos do registo têm SOURCE_ID provado | writer de RAW não abre o recibo da coleta (`chama_cego=True`) | COLLECTION · `coleta/executor_texto_de_pdf.py` | STEP 2 |
| 5 | `RAW → DERIVED` | **SIM (aresta)** — `leis/artefato.py::derivado_de` propaga SOURCE_ID do pai | o que propaga já vem vazio | — | STEP 2 (por dependência de #4) |
| 6 | `DERIVED → STRUCTURED` | **NOT_OBSERVED** — nenhum documento da coorte medida atravessou | — | COLLECTION | STEP 2 |
| 7 | `STRUCTURED → ADMISSION` | **SIM (leitura)** — `admissao.py::_tem_origem` lê `item['source_id']` | — | — | já existe |
| 8 | `ADMISSION → READY (Sala)` | **NÃO** — morada não existe, 0 registos | — | COLLECTION | STEP 2 |
| 9 | `READY → CLAIM/FACT` | **NÃO** — sem módulo de runtime | contrato CLAIM/FACT inteiro | INTELLIGENCE | STEP 3 |
| 10 | `CLAIM → INTELLIGENCE_RUN → CROSSING` | **NÃO** | — | INTELLIGENCE | STEP 3 |
| 11 | `CROSSING → SIGNAL/FINDING/OPPORTUNITY` | **NÃO** | — | INTELLIGENCE | STEP 4 |

```
ELOS PROVÁVEIS HOJE           3 de 11
ELOS PARCIAIS                 3 de 11
ELOS AUSENTES                 5 de 11
```

> **O elo #4 é a raiz.** `SCHEMA_VS_RUNTIME` medido no derivado da casa:
> `CAN_STORE = YES` · `WRITER_WRITES = NO`. O esquema sabe guardar `source_id`;
> o escritor não o escreve. E `leis/artefato.py::raw_do_disco` **recusa-se a
> deduzir do nome do ficheiro**, por lei — e essa recusa está certa. O defeito é
> que ninguém lhe passa o recibo.
>
> Enquanto #4 estiver aberto, **toda métrica de VALOR é `UNKNOWN`** por
> `INT-LAW-294`, e `UNKNOWN` não é zero, não é média e não se preenche por
> plausibilidade.

---

# 8 · SOURCE_FEEDBACK_SCHEMA — **REUTILIZADO, NÃO CRIADO**

```
NOME CANÓNICO      SOURCE_COLLECTION_ADVICE
DONO               Bíblia de Engenharia da Intelligence §36.4
LEIS               INT-LAW-290..299 · INT-LAW-302
ESTADO             DESENHADO. NÃO IMPLEMENTADO.
```

O contrato de saída já está escrito e o Bot de Fontes **consome-o tal como está**:

```
SOURCE_ID                      da Collection, LIDO — nunca criado
CONTEXT                        SOURCE · COUNTRY · DATA_FAMILY · CROP · ISSUE ·
                               ANALYTIC_CAPABILITY · QUESTION_CLASS · TIME_WINDOW
EVIDENCE_WINDOW
CONTRIBUTION_PROFILE           componentes visíveis e decomponíveis
SUGGESTED_DIRECTION            REPROCESS_FIRST | MORE | SAME | LESS | INVESTIGATE | UNKNOWN
REPROCESSING_CHECKED           SIM | NAO — obrigatório quando a direção é MORE
REASON                         texto, ligado a lineage
CONFIDENCE · SAMPLE_SIZE · FRESHNESS
EXPLORATION_STATE              NEVER_SAMPLED | UNDER_SAMPLED | ESTABLISHED
PROTECTED_CATEGORY
GENERATED_BY_INTELLIGENCE_RUN · LINEAGE
```

**Os campos do enunciado que não estão aqui, e porquê:**

| enunciado | tratamento |
|---|---|
| `OBSERVATIONS_USED` · `FACTS_USED` · `UNIQUE_FACTS` | entram em `CONTRIBUTION_PROFILE`, decomponível |
| `FINDINGS_SUPPORTED` · `ALERTS_SUPPORTED` · `OPPORTUNITIES_SUPPORTED` | idem — `*_CONTRIBUTION` em §36.3 |
| `DUPLICATION_RATE` · `TEMPORAL_COMPLETENESS` · `GEOGRAPHIC_COMPLETENESS` | idem — famílias UTILIDADE e APTIDÃO |
| `SUGGESTED_ATTENTION` | é `SUGGESTED_DIRECTION`. **Não ganha campo próprio** |
| `REASONS` | é `REASON`, e tem de estar ligado a lineage |

**E os três eixos que o enunciado manda separar já estão separados, com donos
diferentes:**

```
SOURCE_HEALTH        ela responde e a forma é estável?   COLLECTION · COL-LAW-028
SOURCE_RELIABILITY   a rota chega ao fim, e quantas vezes?  COLLECTION · aprender_com_a_fonte.py (SAUDE_DA_ROTA)
SOURCE_VALUE         o que ela produziu, medido a jusante?  INTELLIGENCE · INT-LAW-290..299
```

> `SOURCE PERFORMANCE RECOMMENDS · COLLECTION DECIDES.`
> O Bot de Fontes lê o conselho. Não é obrigado a obedecer-lhe, e o contrato não
> tem campo com o número final da prioridade — **a ausência é deliberada: um
> número atravessaria a fronteira e seria obedecido.**

---

# 9 · SOURCE_NEED_SCHEMA — **REUTILIZADO, NÃO CRIADO**

```
NOME CANÓNICO      COLLECTION_GAP
DONO               Bíblia de Engenharia da Intelligence §15
LEIS               INT-LAW-150 (gap é first-class) · 151 · 152 · 153
```

Campos já canónicos (`INT-LAW-150`):
```
QUESTION_BLOCKED
MISSING_FACT_OR_KEY
WHY_EXISTING_MATERIAL_IS_INSUFFICIENT
REQUIRED_SCOPE
URGENCY
```

Mapeamento do enunciado, **sem criar campo novo onde já há um**:

| enunciado | canónico |
|---|---|
| `NEED_ID` | `GAP_ID` (o padrão `*_ID` já existe em `gestao_da_coleta.py`) |
| `TOPIC` · `GEOGRAPHY` · `TIME_REQUIREMENT` | `REQUIRED_SCOPE` |
| `MISSING_EVIDENCE` | `MISSING_FACT_OR_KEY` + `WHY_EXISTING_MATERIAL_IS_INSUFFICIENT` |
| `FRESHNESS_REQUIRED` | `FRESCURA_EXIGIDA` (`CAMPOS_DA_NECESSIDADE`) |
| `PRIORITY` | `REQUIREMENT_PRIORITY` — **da Collection**, não da Intelligence |
| `PROVENANCE` | `GENERATED_BY_INTELLIGENCE_RUN` + `LINEAGE` |
| `DESIRED_SOURCE_TYPES` | **campo novo legítimo** — é a única coisa que falta |

> **A lei que evita o erro caro.** `INT-LAW-152` + `INT-LAW-302`: antes de pedir
> fonte nova, verificar se o material já está cá e só lhe falta identidade.
> Medido na casa a 2026-09-14: **7.078 registos já recolhidos**, 12 cruzamentos,
> 6 impossíveis — e **os 6 falham todos pelo mesmo campo, `ISSUE_ID`**. Nenhuma
> coleta nova produz um `ISSUE_ID`.
>
> ```
> FALTA DE CHAVE PARECE FALTA DE DADO,
> E A CONFUSAO ENTRE AS DUAS PAGA-SE EM COLETA.
> ```
>
> Um `COLLECTION_GAP` que chegue ao Bot de Fontes com `REPROCESSING_CHECKED =
> NAO` **não abre missão de descoberta**. Devolve-se.

E a fronteira que o enunciado já enuncia bem:

```
«falta pressão recente de míldio no Veneto»
  NÃO significa  → fabrica um facto
  SIGNIFICA      → não tenho evidência suficiente; procura fontes capazes de a observar
```

---

# 10 · SCOUT_BRIEF_SCHEMA — **NOVO** (0 ocorrências na árvore)

O brief ensina o Scout a procurar **características**, não cópias.

```
BRIEF_ID
ISSUED_AT · ISSUED_BY · POLICY_VERSION
ORIGIN                  GUIDED (nasce de COLLECTION_GAP / ADVICE) | OPEN (exploração)
ORIGIN_REF              GAP_ID ou ADVICE_REF quando ORIGIN = GUIDED

LOOK_FOR                o que se procura, em linguagem de característica
HIGH_VALUE_PATTERNS[]   padrões que já renderam, COM a prova de que renderam
GEOGRAPHIES[]           país · região
TOPICS[]
PREFERRED_CHARACTERISTICS[]
FRESHNESS_REQUIRED
PREFERRED_SOURCE_TYPES[] · DEPRIORITIZE[]
EXCLUDE_KNOWN[]         domínios já no Atlas e já na fila (dedupe é DOIS degraus)

EXPECTED_OUTPUT         candidatas na fila — NUNCA fichas no Atlas
NOT_AUTHORIZED          atribuir SOURCE_ID · escrever no Atlas · coletar · gastar
```

Exemplo do que um padrão de alto valor é e do que não é:

```
BOM   «boletim regional técnico com cultura + doença + data + local,
       publicado por serviço fitossanitário regional, PDF previsível»
       → é uma CARACTERÍSTICA. Encontra fontes que ainda não conhecemos.

MAU   «mais fontes iguais à IT-T3-010»
       → é uma CÓPIA. Encontra o vizinho do que já temos.
```

**A regra que protege o brief de si próprio** (`INT-LAW-297`): um
`HIGH_VALUE_PATTERN` só entra com a prova de que rendeu. E enquanto a cadeia
CLAIM/FACT não existir, **essa prova não existe** — logo, até ao STEP 3, todo
`SCOUT_BRIEF` nasce com:

```
HIGH_VALUE_PATTERNS = []   ·   ORIGIN = OPEN   ·   BASIS = NOT_MEASURED
```

Dizer isto em vez de inventar padrões é a diferença entre um scout que aprende e
um que confirma o que já achávamos.

---

# 11 · SOURCE_NEED_RESPONSE_SCHEMA — **NOVO**

A resposta do Bot ao `COLLECTION_GAP`. Existe para que a Intelligence saiba
**quando pode voltar a tentar a análise** — e para que não fique à espera de
algo que está bloqueado.

```
RESPONSE_ID · GAP_ID · RESPONDED_AT · RESPONDED_BY

SOURCES_FOUND            entraram na fila como candidatas
SOURCES_QUALIFIED        passaram SCREENED (existência + identidade + red team)
SOURCES_ONBOARDED        chegaram a TRIAL (ficha + amostra real)
SOURCES_COLLECTION_READY as seis prontidões, na mesma janela

FIRST_COLLECTION_COMPLETED   SIM | NAO | NOT_RUN     ← NOT_RUN != NAO
FIRST_COLLECTION_RUN_IDS[]

COVERAGE_GAINED
    BY_COUNTRY · BY_REGION · BY_TOPIC · BY_TYPE
    ANTES → DEPOIS, com o denominador visível

STATUS                   FILLED | PARTIALLY_FILLED | NOT_FILLED | BLOCKED | UNKNOWN

BLOCKED_BY_POLICY        termos de uso, GDPR, robots — falha fechado
BLOCKED_BY_COST          exige gasto não autorizado
BLOCKED_BY_CREDENTIAL    exige login/chave que não temos
BLOCKED_BY_CAPABILITY    fonte boa, aquisição impossível → SCRAP ENGINEER
BLOCKED_BY_RELEVANCE     par nunca avaliado → DECISÃO HUMANA

REASON · NEXT_MINIMAL_STEP · OWNER_OF_NEXT_STEP
```

```
UM GAP FECHADO POR BLOQUEIO CONTINUA FECHADO PARA A INTELLIGENCE,
E CONTINUA ABERTO PARA QUEM É DONO DO BLOQUEIO.
Os dois estados coexistem, e por isso têm campos diferentes.
```

---

# 12 · GUIDED_SCOUTING vs OPEN_EXPLORATION

Duas filas, **medidas em separado**, e a quota **não se fixa neste documento**.

```
GUIDED_SCOUTING      orientado por COLLECTION_GAP ou SOURCE_COLLECTION_ADVICE
                     ORIGIN = GUIDED · ORIGIN_REF obrigatório

OPEN_EXPLORATION     descoberta independente: território sem cobertura,
                     região sem fonte, tipo ausente, idioma ausente
                     ORIGIN = OPEN · sem ORIGIN_REF
```

## Porque as duas filas existem

`INT-LAW-297`, textualmente: *se só se coleta quem já provou valor, quem nunca
foi amostrado nunca prova nada, e a ausência de prova passa a funcionar como
prova de ausência.* O sistema confirma a si próprio uma medida que nunca fez.

```
SAMPLE_SIZE = 0  →  PERFIL = UNKNOWN,  nunca «fraco»
```

## Porque a quota fica por fixar

Fixar 70/30 hoje seria inventar exactamente a medida que este desenho existe
para exigir. Com 7 de 213 fontes alguma vez observadas, **qualquer número seria
um palpite com ar de política.**

## Como se medirá, quando houver dados

Usando `leis/evolucao.py`, que já existe e já tem a porta certa:

```
BASELINE      a fila como está antes de se mexer — guardado, não lembrado
CHAMPION      a política em uso
CHALLENGER    a alternativa (ex.: mais peso a OPEN)
SHADOW        corre em paralelo e NÃO afecta nada

METRICA_DECIDIDA_ANTES    obrigatório — escolher a métrica depois de ver os
                          números é escolher quem ganha
AMOSTRA_MINIMA            obrigatório
RESULTADOS    CHALLENGER_BETTER | CHAMPION_BETTER | NO_DIFFERENCE
              | INCONCLUSIVE | ABORTED | NOT_RUN
```

```
INCONCLUSIVE != NO_DIFFERENCE.
«Não deu para saber» pede mais dados. «São iguais» fecha a questão.
```

E `PROIBIDO_HOJE = ML_LIVE · BANDIT_LIVE · AUTO_PROMOTION` continua a valer: a
promoção de uma política de scouting é sempre um acto humano com nome, com
`COMO_SE_DESFAZ` escrito **antes**.

---

# 13 · SCOUT_PERFORMANCE

O funil, medido por `SCOUT_STRATEGY` e por `ORIGIN`:

```
SOURCES_DISCOVERED              entraram na fila
SOURCES_QUALIFIED               SCREENED
SOURCES_ONBOARDED               TRIAL
SOURCES_COLLECTION_READY        as seis prontidões
SOURCES_WITH_OBSERVED_YIELD     alguma corrida real devolveu itens
SOURCES_WITH_USEFUL_FACTS       NEEDS_CLAIM_FACT
SOURCES_WITH_HIGH_VALUE_SIGNAL  NEEDS_INTELLIGENCE
```

**Baseline medido hoje, para que o funil tenha de onde partir:**

```
SOURCES_DISCOVERED              241 (fila) + 213 (já fichadas)
SOURCES_QUALIFIED               213     (todas têm ficha e evidência declarada)
SOURCES_ONBOARDED               213
SOURCES_COLLECTION_READY        NOT_MEASURED nesta missão (é a skill de prontidão que mede)
SOURCES_WITH_OBSERVED_YIELD       7     ← o número que interessa
SOURCES_WITH_USEFUL_FACTS         0     UNKNOWN por INT-LAW-294, não zero real
SOURCES_WITH_HIGH_VALUE_SIGNAL    0     idem
```

> **Não se declara vencedor entre estratégias.** Com 7 fontes observadas, toda
> comparação entre `regional phytosanitary bulletin` e `generic agricultural
> news` seria `INCONCLUSIVE` — e dizê-lo é o resultado correcto.

---

# 14 · ADAPTIVE_CADENCE_MODEL

**Só desenho.** Nada corre, nada agenda, e a Intelligence não fixa frequência.

```
BASE_CADENCE                  da política da coleta
+ OBSERVED_SOURCE_FREQUENCY   medido, não declarado
+ SOURCE_CHANGE_RATE          COL-LAW-029
+ SOURCE_VALUE                SOURCE_COLLECTION_ADVICE — direção, nunca número
+ DOMAIN_URGENCY              do COLLECTION_GAP
+ COST_AND_RATE_LIMIT         circuit breaker, COL-LAW-026
= SUGGESTED_COLLECTION_CADENCE
```

As quatro regras que impedem isto de virar um agendador mágico:

```
1. O BOT SUGERE. A COLLECTION DECIDE E AGENDA.
   Coerente com INT-LAW-290 uma camada acima.

2. LOW FREQUENCY != LOW IMPORTANCE        (INT-LAW-296)
   Uma fonte regulatória que publica 4× por ano é rara e decisiva,
   não fraca. PROTECTED_CATEGORY existe para a proteger da fórmula.

3. A ENTRADA `SOURCE_VALUE` É UMA DIREÇÃO, NÃO UM PESO
   REPROCESS_FIRST | MORE | SAME | LESS | INVESTIGATE | UNKNOWN.
   Converter uma direção num coeficiente é fabricar o número que a
   fronteira existe para não deixar passar.

4. `UNKNOWN` NÃO ENTRA NA CONTA
   Uma fonte sem cadência observada (106/184 das observações medidas)
   não recebe cadência sugerida. Recebe uma missão de medição.
```

---

# 15 · EVENTOS ENTRE DEPARTAMENTOS

Semântica e owners. **Não há bus, não há event system, não há fila técnica.**

| evento | de → para | objecto | estado |
|---|---|---|---|
| `SOURCE_COLLECTION_READY` | BOT → COLLECTION | as 6 prontidões + shape + executor | **NOVO** |
| `SOURCE_COLLECTION_RESULT` | COLLECTION → BOT | `RUN_ID` · contadores · `HEALTH_STATE` · `OBSERVATION_RESULT` | **JÁ EXISTE** em `data/collection-ledger/` — falta ser lido de volta |
| `SOURCE_COLLECTION_ADVICE` | INTELLIGENCE → BOT | Bíblia INT §36.4 | **DESENHADO**, não implementado |
| `COLLECTION_GAP` | INTELLIGENCE → BOT | `INT-LAW-150` | **CANÓNICO**, não implementado |
| `SCOUT_BRIEF` | BOT → SCOUT | §10 | **NOVO** |
| `SOURCE_NEED_RESPONSE` | BOT → INTELLIGENCE | §11 | **NOVO** |

Direção obrigatória, e o que cada seta **não** pode carregar:

```
INTELLIGENCE → BOT      carrega NECESSIDADE e MEDIDA.
                        Nunca carrega rota, executor, prioridade numérica ou ordem.

BOT → COLLECTION        carrega FONTE PRONTA e SUGESTÃO de cadência.
                        Nunca carrega RUN, nunca cunha RUN_ID, nunca executa.

COLLECTION → BOT        carrega RESULTADO OBSERVADO.
                        Nunca carrega juízo sobre o valor do conteúdo.
```

> **O ciclo fechado proibido:** `INTELLIGENCE → BOT → coleta directa →
> INTELLIGENCE`. Toda aquisição passa pela Collection, sempre, mesmo quando é
> urgente e mesmo quando é pequena.

---

# 16 · PAINEL FUTURO — métricas e donos

**Nenhuma UI é desenhada aqui.** Só os números e quem os produz.

| métrica | dono | disponível |
|---|---|---|
| `DISCOVERED` · `QUALIFIED` · `ONBOARDING` | BOT | AVAILABLE_NOW |
| `COLLECTION_READY` | BOT | AVAILABLE_NOW (pela skill de prontidão) |
| `ACTIVE` · `DEGRADED` · `QUARANTINED` · `RETIRED` | BOT | NEEDS `LIFECYCLE_STATE` |
| `BLOCKED_BY_*` (5 tipos) | BOT | AVAILABLE_NOW |
| `NEW_READY_24H` · `NEW_READY_7D` | BOT | NEEDS `LIFECYCLE_CHANGED_AT` |
| `COVERAGE_BY_COUNTRY/REGION/TOPIC/TYPE` | BOT | AVAILABLE_NOW |
| `SOURCE_NEEDS_OPEN / IN_PROGRESS / FILLED` | BOT | NEEDS `COLLECTION_GAP` implementado |
| `SOURCES_WITH_OBSERVED_YIELD` | BOT + COLLECTION | AVAILABLE_NOW (**hoje = 7**) |
| `HIGH_VALUE_SOURCES` · `LOW_VALUE_SOURCES` | INTELLIGENCE | NEEDS_CLAIM_FACT |

```
REGRA DO PAINEL: toda contagem traz o denominador.
«91 GREEN» não se publica sozinho. Publica-se «91 GREEN de 213».
E NOT_MEASURED, NOT_APPLICABLE, UNKNOWN e 0 são quatro células diferentes.
```

---

# 17 · COMPATIBILIDADE EAME

Validação conceitual, país a país, contra a base real medida:

| eixo | Itália (160 fontes) | Espanha (34) | França (6) | Europa (13) | reutilizável? |
|---|---|---|---|---|---|
| `SOURCE_ID` | `IT-Tn-nnn` | `ES-Tn-nnn` | `FR-Tn-nnn` | `EU-Tn-nnn` | **SIM** — o prefixo é país-específico, a forma não |
| Territórios T1..T13 | usado | usado | usado | usado | **SIM** — dono único, `leis/territorios.py` |
| Ciclo de vida | — | — | — | — | **SIM** — nada nele é italiano |
| Shapes de aquisição | 5 ROUTE_TYPE | mesmos | mesmos | mesmos | **SIM** |
| `SOURCE_COLLECTION_READY` | as 6 provas | idem | idem | idem | **SIM** |
| Contrato executável | `regras/italy_contracts.mjs` | **não existe** | **não existe** | **não existe** | **NÃO — é o único componente IT-específico** |
| Executor por território | `pedido/receitas.py::EXECUTORES` | parcial | parcial | parcial | **SIM** (a tabela é por território, não por país) |

```
O MODELO OPERACIONAL É REUTILIZÁVEL.
O CONTRATO EXECUTÁVEL É POR PAÍS, E ISSO É CORRECTO —
uma rota italiana não descreve um portal espanhol.
```

**Risco identificado:** se o motor de rota nascer acoplado ao ficheiro italiano,
cada país novo custa um ficheiro novo e uma cópia da lógica. A alavanca é
descoberta **dirigida por contrato**, e isso é recomendação ao SCRAP ENGINEER —
não trabalho deste departamento.

---

# 18 · WHAT_EXISTS_ALREADY / WHAT_MUST_BE_BUILT

## WHAT_EXISTS_ALREADY
```
✔ vocabulário de ciclo de vida (8 estados)         leis/aprender_com_a_fonte.py
✔ vocabulário de papéis e rendimentos              idem
✔ padrão ESPERADO × REAL                           leis/gestao_da_coleta.py
✔ espinha de experiência e promoção                leis/evolucao.py
✔ contrato de telemetria de corrida                leis/telemetria.py
✔ saúde da fonte, 4 estados + controlo negativo    COL-LAW-028/029 · medidas/source_health.py
✔ circuito de drift, 5 palavras                    COL-LAW-029
✔ cadastro único derivado                          COL-LAW-053 · sources.generated.json
✔ escada de 4 degraus                              COL-LAW-053
✔ porta de relevância por par                      leis/relevancia_da_fonte.py
✔ conselho de fonte, contrato completo             Bíblia INT §36.4
✔ gap de coleta first-class                        INT-LAW-150..153
✔ ledger com SOURCE_ID por observação              184/184
```

## WHAT_MUST_BE_BUILT
```
✘ LIFECYCLE_STATE como campo com writer            0 writers hoje
✘ devolver saúde/cadência do ledger para o perfil  o valor existe e morre no ledger
✘ EXPECTED_YIELD / OBSERVED_YIELD append-only      padrão existe, nunca aplicado à fonte
✘ SOURCE_ID no registo de RUN                      0/34
✘ SOURCE_ID escrito pelo writer de RAW             0/43 — a raiz de tudo
✘ SCOUT_BRIEF                                      não existe
✘ SOURCE_NEED_RESPONSE                             não existe
✘ decisão da fila                                  241 paradas em EM_ANALISE
```

---

# 19 · SAFE_TO_BUILD_NOW / BLOQUEADOS

## SAFE_TO_BUILD_NOW — depois da Big Collection, sem esperar por mais nada
```
S1  LIFECYCLE_STATE no perfil, com writer e história
    Depende só de vocabulário que já existe. Não toca runtime de coleta.

S2  Perfil vivo por SOURCE_ID que LÊ o ledger
    Leitura, não escrita. Devolve HEALTH_STATE, CADENCE_STATE,
    DECLARED_FREQUENCY e OBSERVED_FREQUENCY à fonte. Zero risco.

S3  EXPECTED_YIELD no onboarding, com BASIS obrigatório
    Append-only. Mede-se a si próprio quando o observado chegar.

S4  OBSERVED_YIELD a partir do ledger
    Os contadores já lá estão: NEW_DOCUMENTS, SEEN_AGAIN, CHANGED_IN_PLACE.

S5  Painel de cobertura com denominador
    Os 213 e os 241 já são mensuráveis hoje.

S6  Decidir a fila das 241
    Não é código. É leitura e decisão humana — a alavanca mais barata da lista.

S7  SOURCE_NEED_RESPONSE como formato
    Pode existir e ser preenchido à mão antes de haver automação.
```

## BLOCKED_UNTIL_COLLECTION_TELEMETRY
```
B1  SOURCE_ID no RUN                    → COLLECTION
B2  SOURCE_ID escrito no RAW            → COLLECTION (coleta/executor_texto_de_pdf.py)
B3  ADMISSION_OUTCOME_DISTRIBUTION      → precisa da Sala a existir
B4  READY_YIELD real                    → idem
```

## BLOCKED_UNTIL_CLAIM_FACT
```
B5  UNIQUE_YIELD verdadeiro (único vs. repetido entre fontes)
B6  SOURCE_ANALYTIC_CONTRIBUTION
B7  HIGH_VALUE_PATTERNS no SCOUT_BRIEF
B8  qualquer métrica de VALOR          → INT-LAW-294: CONTRIBUTION = UNKNOWN
```

## BLOCKED_UNTIL_INTELLIGENCE
```
B9   SOURCE_COLLECTION_ADVICE a chegar
B10  COLLECTION_GAP a chegar
B11  GUIDED_SCOUTING com origem real
B12  cadência adaptativa com a entrada SOURCE_VALUE preenchida
B13  comparação GUIDED × OPEN           → hoje INCONCLUSIVE por amostra
```

---

# 20 · IMPLEMENTATION_SEQUENCE

Sequência proposta. **A ordem é ditada por dependência medida, não por ambição.**

```
STEP 0 · DECIDIR A FILA                                    SAFE · SEM CÓDIGO
         241 candidatas → PROMOVIDA | RECUSADA | continua EM_ANALISE
         Owner: decisão humana. Alavanca mais barata da lista inteira.

STEP 1 · BOT DE FONTES V2 — PERFIL VIVO                    SAFE
         LIFECYCLE_STATE com writer · perfil que LÊ o ledger ·
         EXPECTED/OBSERVED_YIELD append-only · painel com denominador
         Owner: BOT DE FONTES. Não toca runtime de coleta.

STEP 2 · TELEMETRIA DA COLLECTION POR SOURCE_ID            BLOQUEIA TUDO A JUSANTE
         SOURCE_ID no RUN · SOURCE_ID escrito pelo writer de RAW ·
         Sala com morada real
         Owner: COLLECTION.  ← o elo #4 é a raiz: WRITER_WRITES = NO

STEP 3 · CLAIM / FACT LINEAGE                              INTELLIGENCE
         Sem isto, todo VALOR é UNKNOWN por INT-LAW-294.

STEP 4 · SOURCE_COLLECTION_ADVICE + COLLECTION_GAP a correr
         Os contratos já existem. Falta implementação e fronteira.

STEP 5 · SCOUT_BRIEF                                       depende de STEP 3
         Antes disso, HIGH_VALUE_PATTERNS = [] e ORIGIN = OPEN.

STEP 6 · CADÊNCIA ADAPTATIVA                               sugerida, nunca agendada

STEP 7 · MEDIR GUIDED × OPEN                               via leis/evolucao.py
         Métrica decidida ANTES. Enquanto a amostra for pequena: INCONCLUSIVE.
```

> **O STEP 2 é o verdadeiro gargalo do departamento inteiro.** Não é o
> scouting, não é o brief e não é a Intelligence. É um escritor de RAW que não
> abre o recibo da coleta — e enquanto isso durar, o Bot de Fontes consegue
> medir actividade e nunca consegue medir valor.

---

# 21 · RED TEAM DESTE DESENHO

Ataques ao próprio plano, e a lei que barra cada um.

| # | ataque | barrado por |
|---|---|---|
| 1 | «Criar `SOURCE_FEEDBACK`» | já é `SOURCE_COLLECTION_ADVICE` — `INT-LAW-000`, um conceito um dono |
| 2 | «Criar `SOURCE_NEED`» | já é `COLLECTION_GAP` — `INT-LAW-150` |
| 3 | «Chamar `READY` ao estado da fonte» | `READY` é item na Sala (`COL-LAW-043`) → `SOURCE_COLLECTION_READY` |
| 4 | «Juntar tudo num `SOURCE_SCORE`» | `NAO_CRIAR` em `aprender_com_a_fonte.py` + `INT-LAW-293` |
| 5 | «Fixar quota GUIDED/OPEN em 70/30» | `INT-LAW-297` — a quota não se fixa sem medição |
| 6 | «Fonte nunca amostrada = fonte fraca» | `SAMPLE_SIZE = 0 → UNKNOWN`, nunca «fraco» |
| 7 | «Baixar perfil de fonte que contradiz» | `INT-LAW-295` — contradição é valor |
| 8 | «Fonte que publica 4×/ano é fraca» | `INT-LAW-296` + `PROTECTED_CATEGORY` |
| 9 | «`MORE` porque o cruzamento falhou» | `INT-LAW-302` — `REPROCESSING_CHECKED` obrigatório |
| 10 | «Bot cria SOURCE_ID sozinho» | Atlas é o owner; ID nasce na promoção |
| 11 | «Bot escreve RESULTADO no livro de relevância» | decisão humana; a máquina só recomenda |
| 12 | «MANIFEST guardado = fonte pronta» | ter amostra é história, não rota |
| 13 | «Corrida SUCCESS = fonte rende» | `CATALOG != COLHEITA`; 19 `DISCOVERY_FAILED` medidos |
| 14 | «403 = fonte morta» | `BLOCKED != DEAD`; medir o egresso primeiro |
| 15 | «Fonte nova por cada canal social» | `ORIGIN_ID ≠ CHANNEL_ID` — verificar contrato antes |
| 16 | «Segundo registry para o perfil» | `COL-LAW-053` — cadastro único; o perfil REFERENCIA |
| 17 | «Intelligence manda coletar» | `INT-LAW-024` · `INT-LAW-151` — recomenda, não executa |
| 18 | «Bot escreve o `case` de rota» | SCRAP ENGINEER; Bot entrega fila de wiring |
| 19 | «Este documento é lei» | é proposta; não emenda Bíblia nenhuma |
| 20 | «213 fontes = boa cobertura» | 7 observadas de 213. Cobertura mede-se com denominador |

```
RED_TEAM_BLOCKERS_ENCONTRADOS = 0
(nenhum ataque derruba o desenho; todos são barrados por lei já escrita —
 o que é, em si, a prova de que o desenho reutilizou em vez de inventar)
```

---

# 22 · CARIMBOS DA MISSÃO

```
GIT_HEAD                606974c3c4559c32307b8f68ec7d7eb925379cc6
BRANCH                  claude/bot-de-fontes-v2-plano
WORKTREE                C:/bot-fontes-v2
BASE                    claude/it-trunk-v1 @ 606974c3  (local == origin, medido)
DIRTY_AO_ABRIR          0

FILES_TOUCHED           docs/arquitetura/BOT-DE-FONTES-V2-PLANO.md   (criado)
FILES_MODIFIED          nenhum
RUNTIME_TOUCHED         nenhum
MERGE                   NÃO FEITO

ISOLAMENTO VERIFICADO — a missão ativa (claude/contract-provenance-cutover-v1
@ 8983fdb7) toca 22 ficheiros, entre eles italy_contracts.mjs,
italy_pilot_collect.mjs, motor_de_rota.mjs e os 5 derivados do System Map.
NENHUM deles foi lido para escrita nem alterado por esta missão.

SYSTEM_MAP_REGENERADO   NÃO — e é deliberado: regenerar produziria diff nos
                        mesmos derivados que a missão ativa está a alterar.
                        Dívida declarada, não esquecida.

KNOW_HOW_DELTA          ATUALIZAÇÃO NECESSÁRIA
                        conteúdo: «quatro dos seis artefactos pedidos já
                        existiam com outro nome; medir owner antes de nomear
                        poupou seis contratos concorrentes»
                        destino: handoff/KNOW-HOW-DELTA-*.md  (não escrito
                        nesta missão — escrita não autorizada)

VEREDITO                PROPOSTA ENTREGUE · HARD STOP
```

---

# 23 · EM LINGUAGEM SIMPLES

**1. O que o Bot de Fontes faz hoje.**
Quase nada de forma organizada. Hoje existem pessoas e missões que, de vez em
quando, vão à procura de sites úteis, olham, e escrevem uma ficha. Não há um
departamento. Há esforços soltos.

**2. O que passará a fazer.**
Passa a ser o dono da fonte desde o momento em que alguém descobre que ela
existe até ao momento em que ela está a produzir e alguém consegue dizer se
valeu a pena. Entrega à Collection fontes **prontas** — para a Collection nunca
ter de descobrir, na hora de colher, como é que se chega lá.

**3. Como uma fonte nasce.**
Alguém vê que existe → entra numa fila de candidatas → alguém abre e confirma
que é mesmo quem diz ser (e não um homónimo, um site sequestrado ou uma loja
disfarçada) → guarda-se um exemplo real do que ela entrega → só aí ganha ficha e
número de identidade.

**4. Quando ela fica «pronta».**
Só quando **seis coisas** são verdade ao mesmo tempo: a identidade está provada;
está na lista que o sistema lê; tem um contrato a descrever o caminho; alguém
decidiu que ela é relevante; existe quem a percorra; e uma corrida real de teste
funcionou. Cinco em seis não é pronta — é «falta uma coisa», e diz-se qual.

**5. Como sabemos se ela rende.**
Escreve-se o que se espera dela **antes** de coletar, e mede-se o que ela deu
**depois**. As duas coisas ficam guardadas lado a lado, para sempre. Nunca se
apaga a previsão antiga para fingir que já sabíamos o resultado.

**6. Como a Intelligence o vai ensinar.**
Quando a Intelligence começar a trabalhar, vai poder dizer duas coisas: «esta
fonte rendeu/não rendeu» e «falta-me evidência sobre isto, procura quem a
observe». **Não pode mandar coletar** — só informa. Quem decide é a Collection.
Um detalhe que já custou caro noutra ocasião: antes de pedir fonte nova, é
obrigatório verificar se o material já está cá e só lhe falta uma etiqueta.
Aconteceu: 7.078 registos já recolhidos, seis análises impossíveis, e as seis
falhavam pela **mesma etiqueta em falta** — nenhuma coleta nova resolveria.

**7. Como o Scout vai melhorar.**
Recebendo um «briefing» que descreve **características** («boletins regionais
com cultura, doença, data e local») em vez de cópias («mais sites iguais a
este»). E com duas filas em paralelo: uma orientada pelo que já se sabe, outra
livre. Se só se procurasse o que já funcionou, nunca se descobriria nada novo —
e o sistema acabaria a dar-se razão a si próprio.

**8. O que se pode fazer logo a seguir à Big Collection.**
Sete coisas, todas sem risco: pôr um «estado» em cada fonte; montar o perfil que
lê os dados que já estão guardados; começar a escrever a expectativa e o
resultado; montar o painel de cobertura; e — a mais barata de todas — **decidir
as 241 candidatas paradas**. Isso não precisa de código nenhum, só de alguém
ler e decidir.

**E o número que resume tudo.**
Temos **213 fontes registadas** e **241 à espera**. Destas 213, **7** alguma vez
foram realmente visitadas pelo sistema. O problema deste departamento nunca foi
encontrar fontes. É fazê-las atravessar.

**E o que trava.**
Há um ponto concreto, pequeno e muito escondido: o pedaço de programa que grava
o ficheiro bruto **não anota de que fonte ele veio**. O sítio onde essa anotação
deveria ficar existe e está vazio. Enquanto isso não for corrigido — e é da
Collection, não deste departamento — conseguimos medir **quanto** cada fonte
trouxe, mas nunca **se aquilo serviu para alguma coisa**.

---

**HARD STOP.** Nada foi integrado ao runtime. Nenhum merge foi feito. Nenhum
ficheiro da missão ativa foi tocado. Este documento é uma proposta e aguarda
decisão do dono.
