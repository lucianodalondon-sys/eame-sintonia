# BOT DE FONTES V2 — PLANO

> **DOCUMENTO DE PROPOSTA. NÃO É LEI, NÃO É RUNTIME, NÃO ESTÁ LIGADO A NADA.**
>
> Não cria Bíblia, não emenda Bíblia, não altera contrato executável, não toca
> Collection, Admission, Sala, Intelligence nem System Map. Desenha um
> departamento e mede o que já existe para o sustentar.

```
MISSAO      BOT-DE-FONTES-V2-DESENHO
DATA        2026-09-20
BRANCH      claude/bot-de-fontes-v2-plano
WORKTREE    C:/bot-fontes-v2
ESTADO      PROPOSTA · POR DECIDIR PELO DONO
MERGE       NÃO FEITO, E NÃO PEDIDO

V1  medido em  claude/it-trunk-v1 @ 606974c3            (2026-09-20 08:13)
V2  RECONCILIADO com claude/contract-provenance-cutover-v1 @ ffea8dbc
                                                          (2026-09-20, leitura read-only por git show)
```

---

# ⚠️ COMO LER ESTE DOCUMENTO — TRÊS CAMADAS QUE NÃO SE MISTURAM

```
ARCHITECTURE                 desenho do departamento. Não envelhece com uma corrida.
                             §3 · §4 · §5 · §6 · §8..§17 · §19 · §20

CURRENT_OPERATIONAL_SNAPSHOT fotografia datada, com ref e commit. ENVELHECE.
                             §1 · §1B · §2 · §7 · §18 · §24 (reconciliação)

FUTURE_REQUIREMENTS          o que ainda não existe e tem de ser construído.
                             §18 (coluna direita) · §19 · §20
```

> **Um número deste documento sem o carimbo `@ <ref>` não é estado atual.**
> A V1 foi medida num trunk que a missão operacional já ultrapassou, e duas das
> suas conclusões estavam erradas por isso. Estão corrigidas, com o erro à vista,
> em **§24 · RECONCILIAÇÃO**.

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

## 1.4 · Os números — `CURRENT_OPERATIONAL_SNAPSHOT @ claude/it-trunk-v1 606974c3`

> ⚠️ **ESTES NÚMEROS ESTÃO REVOGADOS COMO ESTADO ATUAL.** Foram medidos no
> trunk `606974c3`. A missão operacional avançou para `ffea8dbc` e mudou
> materialmente três deles. **Ver §24 para o snapshot vivo.** Ficam aqui porque
> apagar a medição antiga esconderia o que mudou e quando.

```
SYSTEM_MAP_SOURCE_COUNT            213       (inalterado em ffea8dbc — reconferido)
  por país          ITALIA 160 · ESPANHA 34 · EUROPA 13 · FRANCA 6
  por verdict       GREEN 91 · YELLOW 85 · PARCIAL 27 · «NAO SEI» 10
  com contract      5 / 213                  ← REVOGADO · ver §24
  sabe_coletar      5 / 213                  ← subdeclara; ver skill de prontidão
  update_frequency  «NÃO SEI» 93 + vazio 41 = 134 / 213 sem valor   (com valor: 79)

CANDIDATE_COUNT                    241       (inalterado em ffea8dbc)
  estado EM_ANALISE                241 / 241 ← INTERPRETADO ERRADO · ver §24
  estado PROMOVIDA                   0
  estado RECUSADA                    0

CONTRATOS_EXECUTAVEIS_NO_TRUNK      14       ← REVOGADO · 113 em ffea8dbc

LEDGER DA COLETA (data/collection-ledger/italy/)
  RUNS                              34       ← REVOGADO · 145 em ffea8dbc
  OBSERVATIONS                     184       ← REVOGADO · 300 em ffea8dbc
  SOURCE_ID DISTINTOS OBSERVADOS     7       ← REVOGADO · 110 em ffea8dbc
  HEALTH_STATE                     HEALTHY 153 · FAILED 31
  OBSERVATION_RESULT               SEEN_AGAIN 109 · NEW_DOCUMENT 34 · DISCOVERY_FAILED 19
                                   TRANSPORT_OR_EMPTY 12 · BASELINE_DOCUMENT 10
  CADENCE_STATE                    CADENCE_UNKNOWN 106 · UPDATED 44 · EXPECTED_NO_CHANGE 3 · vazio 31

SALA DE ESPERA
  MORADA_EXISTE                    False     ← lido de um derivado histórico; ver §24
  TOTAL_WAITING_ROOM_RECORDS           0
```

> **A conta que definiu a missão do departamento, na V1:** 213 fontes
> registadas, 241 candidatas, e 7 fontes alguma vez observadas.
> **Em `ffea8dbc` são 110.** A frase «o gargalo não é descobrir, é atravessar»
> mantém-se verdadeira — mas a travessia andou muito, e o plano tinha de o dizer.

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
G1  A FILA NÃO ANDA                                 ⚠️ REVOGADO — ver §24.1
    ~~241 candidatas, todas EM_ANALISE, zero PROMOVIDA, zero RECUSADA.
    `candidatas/fonte_nova.py` sabe registar e sabe listar. Ninguém decide.~~
    ERRADO. A fila FOI decidida, em 2026-09-15, por
    `candidatas/decidir_fila_italia.py`. 241/241 têm DECIDIDA_EM, PORQUE,
    EVIDENCIA e O_QUE_FALTA escritos. `EM_ANALISE` é um VEREDITO, não um limbo.
    O gap real é outro: falta o exemplo real do item (G1').

G1' FALTA O EXEMPLO REAL, NÃO A DECISÃO                        (o gap verdadeiro)
    241/241 param no mesmo degrau, e a razão é única: o Atlas exige um ITEM
    aberto e identificado (EXAMPLE_URL · TIPO · HTTP · CONTENT_TYPE · BYTES ·
    SHA256 · DATA_VISÍVEL), e a sonda de 14/09 só provou que o endereço responde.
    → não é SOURCE_GAP nem OWNER_GAP. É EVIDENCE_GAP, e é automatizável.

G2  O CICLO DE VIDA NÃO É ESCRITO EM LADO NENHUM
    `CICLO_DE_VIDA` tem 8 estados e 0 writers. Nenhuma ficha do Atlas nem do
    derivado tem campo de estado de ciclo. O estado de uma fonte hoje é uma
    leitura de prosa (`verdict`, `collection`, `automation`), não um valor.
    CONFIRMADO em ffea8dbc.

G3  O REGISTRY NÃO GUARDA SAÚDE NEM CADÊNCIA
    COL-LAW-208 lista LAST_ATTEMPT · LAST_SUCCESS · LAST_FAILURE · HEALTH ·
    CHANGE_RATE como campos que a ficha PODE ter. Nenhum existe no derivado
    (22 campos, nenhum deles de saúde). A saúde existe — está no LEDGER, por
    observação, e morre lá: ninguém a devolve à fonte.
    CONFIRMADO em ffea8dbc, e agora vale para 110 fontes em vez de 7.

G4  O RUN NÃO DECLARA SOURCE_ID
    0/145 runs têm SOURCE_ID. 300/300 observações têm.
    O elo SOURCE→RUN só é reconstruível por junção via observação.
    CONFIRMADO em ffea8dbc — e é o único gap de linhagem que sobrevive.

G5  DEPOIS DA ADMISSÃO, A LINHAGEM PARA         ⚠️ REVOGADO — ver §24.2
    ~~Sala de Espera: morada não existe, 0 registos. CLAIM/FACT não tem módulo
    de runtime. Logo SOURCE → CLAIM → FINDING é hoje INDEMONSTRÁVEL.~~
    PARCIALMENTE ERRADO. A cadeia SOURCE→…→SALA **está observada**, com 35
    asserções PASS e 0 FAIL, e o `source_id` sobrevive até STRUCTURED
    (`IT-T3-002`). O que continua verdadeiro: CLAIM/FACT não existe, logo
    SOURCE → CLAIM → FINDING permanece indemonstrável.

G6  EXPECTED vs OBSERVED NÃO EXISTE PARA FONTE
    O padrão está escrito para DECISÃO (`CUSTO_ESPERADO` × `CUSTO_REAL` em
    gestao_da_coleta) e nunca foi aplicado a FONTE. CONFIRMADO.

G7  NÃO HÁ DESCOBERTA DIRIGIDA
    Zero ocorrências de SCOUT. CONFIRMADO em ffea8dbc.

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

# 23 · CARIMBOS DA RECONCILIAÇÃO V2

```
MEDIDO_EM            claude/contract-provenance-cutover-v1 @ ffea8dbc   (local == origin)
METODO               READ-ONLY por `git show <ref>:<path>` — a worktree do
                     COORDINATOR (C:/.../cutover-v2) NÃO foi aberta, lida do disco,
                     nem tocada. Nenhum checkout, nenhum fetch destrutivo.
COMMITS NOVOS        5, desde 8983fdb7:
                       084d6d95  arpae: rota do IT-T2-001 provada
                       1fbb1242  bc2: receitas T1/T5/T7/T9/T10/T11/T12
                       fa95b634  bc2: 113 fontes pela porta canonica, Sala 4 -> 17
                       0792e84b  estradas: 9 fontes com rota provada, 22 so candidata
                       ffea8dbc  mapa: regerado sobre a arvore da Big Collection 2
```

---

# 24 · RECONCILIAÇÃO — O QUE MUDOU, E ONDE EU ESTAVA ERRADO

## 24.1 · FASE 1 — OS QUATRO UNIVERSOS, COM O GRÃO PROVADO

> **Não se comparam números antes de provar o grão.** Os quatro universos
> respondem a perguntas diferentes, e é por isso que 170 ≠ 213 ≠ 241.

```
A) ITALY_SOURCE_UNIVERSE        = 170
   owner      data/derivados/CENSO-RAPIDO-IT-2026-09-20.json  (COORDINATOR)
   grão       SOURCE (fonte canónica com SOURCE_ID)
   critério   «as 170 fontes da medição SOURCE-COLLECTION-READINESS-V1 (18/09)»
   composição IT 157 + EU 13     ← NÃO é «só Itália»: inclui as 13 EU-*
   nota       o próprio METODO declara: «nada aqui foi re-sondado fonte a fonte»

B) SYSTEM_MAP_SOURCE_UNIVERSE   = 213
   owner      system-map/data/sources.generated.json  (derivado, COL-LAW-053)
   grão       SOURCE — uma linha por SOURCE_ID, NÃO por endpoint
   escopo     GLOBAL EAME: IT 160 · ES 34 · EU 13 · FR 6
   endpoints  NÃO — o campo `url` é UM endereço; COL-LAW-205 mantém-nos no endpoint
   externas   NÃO — só fichas do Atlas

C) CANDIDATE_UNIVERSE           = 241
   owner      candidatas/FONTES-CANDIDATAS.json  (a FILA, degrau 1)
   grão       MISTO, e é isso que torna a comparação directa inválida:
                CANAL_SOCIAL (YT/LI/IG/FB) .... 149
                ORGANIZAÇÃO / SITE ............  92
   país       IT 241 / 241 — nenhuma de outro país
   SOURCE_ID  0 / 241 preenchido (correcto: o ID nasce na promoção)
   pessoas    NÃO há grão PESSOA/ORCID nesta fila

D) READY_UNIVERSE               = 113
   owner      o mesmo censo (A), campo CLASS = READY_NOW
   como       «contrato executável em regras/italy_contracts.mjs -> READY_NOW»
   ⚠️ É UM PREDICADO DE CONTRATO, NÃO AS SEIS PRONTIDÕES DE §4.2.
      CANARY_PASS e RELEVANCE_READY não entram nesta conta.
```

## 24.2 · FASE 2 — A RELAÇÃO ENTRE 170 / 213 / 241, POR IDENTIDADE

Reconciliação por `SOURCE_ID` (não por URL, não por nome):

```
170 ∩ 213          = 170        → 170 É SUBCONJUNTO PRÓPRIO DE 213.  SIM.
ONLY_IN_170        = 0
ONLY_IN_213        = 43         = ES 34 + FR 6 + 3 fontes IT-T8

os 3 IT-T8 que os 170 excluem:
   IT-T8-001  YouTube  @agronotizietv        verdict GREEN
   IT-T8-002  LinkedIn company/image-line    verdict YELLOW
   IT-T8-003  Instagram @agronotizie         verdict YELLOW
   → T8 = FARMERS & INFLUENCERS. São canais sociais, e o censo de execução
     excluiu-os porque a política os bloqueia. Exclusão correcta e deliberada.

aritmética que fecha:   160 IT − 3 (T8) = 157 · 157 + 13 EU = 170  ✔
```

**As 241 contra as 213** — chave = `plataforma + handle` (não handle sozinho):

```
EXATO_JA_NO_ATLAS                       2      ersaf.lombardia.it · regione.vda.it
SOCIAL_MESMA_PLATAFORMA_HANDLE_NOVO   129
SOCIAL_NOVO                            20
SITE_NOVO                              90
DUPLICATAS INTERNAS (URL repetida)      0      de 241, 95 domínios distintos
```

> **As 2 «exatas» não são duplicatas — são ENDPOINTS.**
> `ersaf.lombardia.it` (raiz) contra `ersaf.lombardia.it/montagna/rifugi/…`
> (IT-T1-008); `regione.vda.it` contra `regione.vda.it/agricoltura` (IT-T1-012).
> Mesmo domínio, endereço diferente. Por `COL-LAW-205` isso é **um endpoint novo
> na mesma fonte**, e a decisão correcta é `DERIVA_DE`, nunca `SOURCE_ID` novo.

**Respostas diretas às perguntas da FASE 2:**

| pergunta | resposta medida |
|---|---|
| 170 é subconjunto dos 213? | **SIM**, 170/170, zero fora |
| 241 inclui os 170? | **NÃO** — universos disjuntos por construção: a fila é degrau 1, o Atlas é degrau 2. `SOURCE_ID` = 0/241 |
| 241 inclui duplicatas? | **NÃO** internamente (0 URLs repetidas). 2 colidem com o Atlas, e são endpoints |
| 241 inclui endpoints da mesma fonte? | **SIM, 2** — exatamente os dois acima |
| 241 inclui fontes de outros países? | **NÃO** — 241/241 são `PAIS = IT` |
| 241 inclui pessoas/ORCID? | **NÃO** — nenhum grão PESSOA na fila |
| 241 inclui já-promovidas com estado antigo? | **NÃO** — 0 com `SOURCE_ID` preenchido |

## 24.3 · ⚠️ FASE 3 — ONDE A V1 DESTE PLANO ESTAVA ERRADA

A V1 escreveu, como gap G1: *«A FILA NÃO ANDA. Ninguém decide.»*
E propôs, como acção mais barata: *«decidir as 241 candidatas paradas»*.

**As duas afirmações estão erradas, e a medição prova-o:**

```
com DECIDIDA_EM ....... 241 / 241      todas na mesma data: 2026-09-15
com PORQUE ............ 241 / 241
com EVIDENCIA ......... 241 / 241
com O_QUE_FALTA ....... 241 / 241
```

O diagnóstico, ponto a ponto:

```
IS_DEFAULT_STATE       = NÃO   fonte_nova.py escreve «CANDIDATA», não «EM_ANALISE»
IS_STALE_QUEUE         = NÃO   decidida há 5 dias, com prova citada linha a linha
IS_WRITER_MISSING      = NÃO   decidir_fila_italia.py::decidir() existe e correu
IS_TRANSITION_MISSING  = NÃO   devolve PROMOVIDA · RECUSADA · EM_ANALISE
IS_OWNER_MISSING       = NÃO   o owner é o mesmo script + o Atlas
```

**`EM_ANALISE` não é limbo — é um veredito, e o próprio código o diz:**

> *«REGRA 3 · O RESTO FICA EM_ANALISE, COM O QUE FALTA ESCRITO. EM_ANALISE não é
> limbo. Cada linha leva a prova que tem e a frase exacta do que falta.»*

E a razão de nenhuma ter sido promovida é **uma só, para as 241**:

```
O_QUE_FALTA = EXEMPLO_REAL_DO_ITEM     241 / 241
```

O script recusa-se a promover de propósito, e escreve porquê:

> *«promover 241 fichas com REAL_EXAMPLE em branco poria no atlas 241 linhas a
> dizer "fonte registada" sem ninguém ter aberto um único item — e com isso a
> palavra REGISTADA deixaria de significar o que significa nas 140 que lá estão.»*

```
A LIÇÃO: UM ESTADO UNIFORME PARECE UMA FILA PARADA
E PODE SER UMA DECISÃO UNIFORME.
A diferença lê-se no campo DECIDIDA_EM, não na contagem por ESTADO.
```

**Quem promove, quem rejeita, e qual a prova exigida:**

```
promove          decidir_fila_italia.py --escrever, quando houver REAL_EXAMPLE
rejeita          o mesmo script, e SÓ com prova de que a fonte NÃO SERVE
                 (REGRA 1: «não li» ≠ «não serve»; 25 recusas de 14/09 foram revogadas)
prova exigida    EXAMPLE_URL · TIPO_ITEM · TITULO · HTTP_STATUS · CONTENT_TYPE ·
                 BYTES_LIDOS · SHA256_DO_QUE_FOI_LIDO · DATA_VISIVEL
a transição      EXISTE. Falta-lhe o insumo, não o código.
```

## 24.4 · ⚠️ FASE 6 — O ACHADO DE SOURCE_ID, REVALIDADO E EM PARTE REVOGADO

A V1 afirmou: *«o writer de RAW não abre o recibo da coleta»*, citando
`WRITER_WRITES = NO` e `0 de 43 artefactos com SOURCE_ID`.

**Erro de método, e vale a pena nomeá-lo:** eu li
`data/derivados/SOURCE-ID-WIRING-GAP-V1.json` — um **derivado histórico** — e
publiquei-o como estado presente. O próprio derivado avisava
(`FORWARD_GAP_EXECUTED_AND_PROVEN = UNKNOWN`), e eu não dei peso ao aviso.

```
RELATÓRIO ANTIGO NUM DERIVADO É HISTÓRIA, NÃO ESTADO.
E o código tinha andado — inclusive JÁ no trunk que eu medi.
```

**O que o código realmente faz, medido agora:**

```
coleta/executor_texto_de_pdf.py::fonte_para_o_bruto(pai, raiz)
    → coleta/italy_executor.py::fonte_do_conteudo(sha256)
    → lê o CAMPO SOURCE_ID que o coletor escreveu na linha do LIVRO
    → replace(pai, SOURCE_ID=achado["SOURCE_ID"])

CHAVE = RAW_SHA256, e é deliberado. O próprio módulo mede porquê:
    RAW_SHA256 presente .... 250/300     RAW_PATH presente .... 139/300
    «juntar por caminho responderia "não sei" a metade do livro»

⚠️ E NÃO É DERIVAR FONTE DO SHA: o sha é a CHAVE que acha a linha;
   a fonte vem do CAMPO. Sem linha → «não sei», nunca o nome do ficheiro.
   E duas fontes para o mesmo conteúdo = ERRO explícito, nunca desempate mudo.
```

**A matriz da FASE 6, medida em `ffea8dbc`:**

| ELO | `SOURCE_ID_PRESENT` | `DERIVABLE` | `PROVENANCE_PRESENT` |
|---|---|---|---|
| `SOURCE → RUN` | **NO** (0/145) | YES — por junção via observação | parcial |
| `RUN → RAW_OBSERVATION` | YES (`RUN_ID` 300/300) | — | YES |
| `SOURCE → RAW_OBSERVATION` | **YES (300/300)** | — | YES |
| `RAW → STORAGE` | YES via livro (sha 250/300) | YES | YES |
| `RAW → DERIVED` | YES (`artefato.py::derivado_de` propaga) | — | YES |
| `DERIVED → ADMISSION` | **YES — observado**, `source_id=IT-T3-002` em STRUCTURED | — | YES |
| `ADMISSION → SALA` | **YES — observado**, 3 itens com `SOURCE_ID` na Sala | — | YES |

Prova da travessia completa (`system-map/data/material-italiano-na-sala.observado.json`):

```
REQUEST · ORCHESTRATOR · EXECUTOR · RUN · RAW · STORAGE ·
DERIVED · STRUCTURED · ADMISSION · READY · WAITING_ROOM
      todos OBSERVED = true          PASSOU = 35   FALHOU = 0

WAITING_ROOM_BEFORE 0 → AFTER 3     SOURCE_ID na Sala: IT-T3-002 · IT-T3-008 · IT-T3-010
```

**Veredito da FASE 6:**

```
SOURCE_LINEAGE_GAP_STILL_EXISTS = SIM, MAS MUITO MENOR DO QUE A V1 DISSE

EXACT_LOCATION   data/collection-ledger/italy/runs.ndjson
                 o registo de RUN não carrega SOURCE_ID (0/145).
                 É o ÚNICO elo com ausência real de campo.
                 (o buraco do writer de RAW está fechado pelo livro)

MINIMAL_FIX_LATER  acrescentar SOURCE_ID (ou SOURCE_IDS[]) ao registo de RUN.
                   `leis/telemetria.py::CAMPOS_DO_RUN` JÁ o lista — o contrato
                   está escrito, só o escritor do ledger não o preenche.
                   Owner: COLLECTION. NÃO implementado por esta missão.

⚠️ O QUE CONTINUA VERDADEIRO DA V1: CLAIM/FACT não existe em runtime.
   Logo SOURCE → CLAIM → FINDING permanece indemonstrável, e toda métrica
   de VALOR continua UNKNOWN por INT-LAW-294. Isso não mudou.
```

## 24.5 · FASE 4 — SIMULAÇÃO DAS 241 (nada foi escrito)

Classificação automática com a evidência que já existe. **Zero transições
gravadas** — o ficheiro da fila não foi tocado.

| `PROPOSED_STATE` | N | porquê |
|---|---|---|
| `BLOCK` | **69** | LinkedIn 44 + Instagram 25. `LINKEDIN_BIG_COLLECTION_ELIGIBLE = 0` e `INSTAGRAM_REMOTE_COLLECTION_ALLOWED = 0`, medido pelo COORDINATOR |
| `NEEDS_REVIEW` | **82** | YouTube 60 + Facebook 20 + 2 endpoints de fonte existente |
| `NEEDS_EVIDENCE` | **90** | site próprio, falta só o exemplo real do item |
| `PROMOTE` | **0** | nenhuma tem `REAL_EXAMPLE`. Promover seria esvaziar a palavra REGISTADA |
| `REJECT` | **0** | e é correcto: «não li» ≠ «não serve» (REGRA 1) |

Por tipo:

```
ORGANIZACAO   46 NEEDS_EVIDENCE      YOUTUBE    60 NEEDS_REVIEW
IMPRENSA      19 NEEDS_EVIDENCE      FACEBOOK   20 NEEDS_REVIEW
BASE_OFICIAL  16 NEEDS_EVIDENCE + 2 NEEDS_REVIEW
CIENCIA        9 NEEDS_EVIDENCE      LINKEDIN   44 BLOCK · INSTAGRAM 25 BLOCK
```

## 24.6 · FASE 5 — O QUE O BOT DECIDE SOZINHO, E O QUE SOBE A HUMANO

O pedido é explícito: **não usar «alguém precisa ler»**. Aplicado às 241:

```
BOT DECIDE SOZINHO (172 = 90 + 82)
    90  NEEDS_EVIDENCE  → capturar 1 item real por fonte. É HTTP + hash +
                          content-type. Determinístico, sem julgamento.
                          Com REAL_EXAMPLE, decidir_fila_italia.py promove sozinho.
    60  YOUTUBE         → capacidade YouTube JÁ existe em T9 (medida, não suposta).
                          Resolver channelId por `channelMetadataRenderer.externalId`
                          e capturar 1 vídeo do feed. Automatizável.
    20  FACEBOOK        → probe de existência com controlo negativo obrigatório.
     2  ENDPOINTS       → DERIVA_DE na ficha existente. Regra mecânica (COL-LAW-205).

SOBE A HUMANO (69, e SÓ por política)
    69  LINKEDIN + INSTAGRAM → POLICY_BLOCK. Não é ambiguidade nem falta de
                               evidência: é uma decisão de política já tomada.
                               O Bot não relaxa policy — bloqueia e segue.
```

```
NEEDS_HUMAN = 69 / 241 = 29%,  e os 69 são UM único assunto:
«a política de plataformas sociais muda ou não?»
É UMA decisão, não 69 leituras.
```

## 24.7 · FASE 8 — O PRIMEIRO BACKLOG REAL DO BOT

```
TOTAL_CANONICAL_SOURCES          213      (Atlas/derivado, global EAME)
TOTAL_CANDIDATES                 241      (fila IT, degrau 1)

ALREADY_READY                    113      contrato executável (≠ as 6 prontidões)
ALREADY_REGISTERED_NOT_READY      57      dos 170: 37 POLICY · 10 CAPABILITY ·
                                          5 UNKNOWN · 4 EXTERNAL · 1 CONTRACT_ONLY
FORA DO CENSO DE EXECUÇÃO         43      ES 34 + FR 6 + 3 IT-T8

CANDIDATE_DUPLICATES               0      (0 URLs repetidas internamente)
CANDIDATE_ALREADY_COVERED          2      endpoints de IT-T1-008 e IT-T1-012

AUTO_PROMOTABLE                    0      hoje — nenhuma tem REAL_EXAMPLE
AUTO_PROMOTABLE_APOS_CAPTURA     172      o que a captura de 1 item desbloqueia
AUTO_REJECTABLE                    0      «não li» ≠ «não serve»
AUTO_BLOCKABLE                    69      LinkedIn 44 + Instagram 25 (política)
NEEDS_HUMAN_REVIEW                69      os mesmos, e é UMA decisão de política
UNKNOWN                            0      toda a fila tem veredito escrito
```

### TOP 10 · AÇÕES DO SOURCE CURATOR
*(ordenadas por fontes desbloqueadas ÷ esforço·risco)*

| # | ação | desbloqueia | esforço | risco | owner |
|---|---|---|---|---|---|
| 1 | **Capturador de `REAL_EXAMPLE`** — 1 item por candidata, gravando os 8 campos do Atlas | **até 172** | médio (1 script) | baixo — só leitura HTTP | BOT |
| 2 | `SOURCE_ID` no registo de RUN — o contrato já o lista em `CAMPOS_DO_RUN` | fecha o **último** elo de linhagem | baixo | baixo | COLLECTION |
| 3 | `LIFECYCLE_STATE` com writer e história | 213 fontes ganham estado real | baixo | nenhum | BOT |
| 4 | Perfil vivo que **lê** o ledger (saúde + cadência) | **110** com dados reais | baixo | nenhum — leitura | BOT |
| 5 | `DERIVA_DE` nos 2 endpoints | 2, e evita 2 IDs a dobrar | trivial | nenhum | BOT |
| 6 | Decisão única de política social | **69** de uma vez | trivial (1 decisão) | político | **HUMANO** |
| 7 | Ligar YouTube (T9) às 60 candidatas YT | 60 | médio | baixo | BOT + SCRAP |
| 8 | `OBSERVED_YIELD` a partir do ledger | 110 medíveis | baixo | nenhum | BOT |
| 9 | Fechar os 57 não-READY por classe de blocker | 10 CAPABILITY são a alavanca | médio | baixo | SCRAP |
| 10 | Cobertura ES (34) e FR (6) com o mesmo método | 40 | alto | baixo | BOT |

> **A acção #1 sozinha vale mais do que descobrir fontes novas.** Ela converte
> uma fila inteira que já foi analisada, já tem dono e já sabe exactamente o que
> lhe falta. E o que lhe falta **não é julgamento — é captura.**

## 24.8 · RED TEAM DESTA RECONCILIAÇÃO

| # | ataque | resposta |
|---|---|---|
| 1 | «aceitou 113 por relato» | não — lido em `CENSO-RAPIDO-IT-2026-09-20.json @ ffea8dbc` |
| 2 | «comparou 170 com 241 sem provar o grão» | grão provado primeiro: SOURCE × SOURCE × MISTO |
| 3 | «113 READY = pronto para coletar» | **não** — é predicado de contrato; as 6 prontidões de §4.2 continuam por medir |
| 4 | «abriu a worktree do COORDINATOR» | não — só `git show <ref>:<path>` |
| 5 | «dedupe por handle sem plataforma» | apanhado no meu próprio red team: o handle sozinho deu 1 falso positivo. Chave corrigida para `plataforma+handle` |
| 6 | «as 2 colisões são duplicatas» | não — endpoints, `COL-LAW-205`, resolvem-se com `DERIVA_DE` |
| 7 | «a fila estava parada» | **era eu que estava errado.** Decidida em 2026-09-15 |
| 8 | «o writer de RAW não anota a fonte» | **era eu que estava errado.** O livro resolve por sha; li um derivado histórico |
| 9 | «a Sala está vazia» | **era eu que estava errado.** 3 itens, com `SOURCE_ID`, 35 PASS / 0 FAIL |
| 10 | «CLAIM/FACT também já existe?» | **não.** Continua ausente, e o gap de VALOR mantém-se inteiro |

```
ERROS DA V1 CORRIGIDOS = 3   (G1 · G5 · elo do writer de RAW)
ACHADOS DA V1 QUE SOBREVIVEM = 6   (G2 G3 G4 G6 G7 G8 + os 4 owners canónicos)
```

## 24.9 · O QUE SOBREVIVE DA V1, INTACTO

A descoberta central **não foi afectada** pela mudança de ref, e foi reconferida
em `ffea8dbc`:

```
SOURCE_COLLECTION_ADVICE   existe    Bíblia INT §36.4 · INT-LAW-290..302
COLLECTION_GAP             existe    Bíblia INT §15   · INT-LAW-150..153
CICLO_DE_VIDA (8 estados)  existe    leis/aprender_com_a_fonte.py
CUSTO_ESPERADO / _REAL     existe    leis/gestao_da_coleta.py

SCOUT_BRIEF                AUSENTE   0 ficheiros — reconferido em ffea8dbc
SOURCE_NEED_RESPONSE       AUSENTE   0 ficheiros — reconferido em ffea8dbc
```

Os dois artefactos novos de §10 e §11 **mantêm-se justificados**.

---

# 25 · EM LINGUAGEM SIMPLES

**O que me pediram desta vez.** O plano que entreguei de manhã foi medido numa
"fotografia" do projeto tirada às 8h. Entretanto a equipa operacional trabalhou
muito. Pediram-me para comparar as duas fotografias e corrigir o plano — sem
acreditar em nada por ouvir dizer.

**E eu estava errado em três coisas. Vale a pena dizê-las primeiro.**

*Erro 1 — «a fila das 241 está parada».* Não está. Foi analisada no dia 15 de
setembro, uma por uma, com o motivo escrito em cada linha. Todas ficaram no
mesmo estado porque **todas têm exatamente o mesmo problema**, e o programa
recusou-se a aprová-las de propósito. Eu vi 241 linhas iguais e concluí
"abandonado"; na verdade era **uma decisão uniforme**.

*Erro 2 — «o programa não anota de que fonte veio cada ficheiro».* Anota. Existe
um "livro" que guarda isso e que encontra a fonte pela **impressão digital do
conteúdo**, não pelo nome da pasta. Eu li um relatório antigo guardado no
projeto e tratei-o como se descrevesse o presente. O relatório até tinha um
aviso a dizer "isto não foi reconfirmado" — e eu não lhe dei o devido peso.

*Erro 3 — «a Sala de Espera está vazia».* Não está. O material já atravessou o
caminho todo até ao fim, com 35 verificações certas e nenhuma errada.

**1. Por que temos 170, 213 e 241.**
São três listas que respondem a perguntas diferentes:

- **213** = todas as fontes registadas, de todos os países (Itália, Espanha, França, Europa).
- **170** = só as que entraram na corrida atual — as italianas mais as europeias. É um subconjunto exato das 213.
- **241** = a *fila de entrada*, que ainda nem são fontes. São pistas à espera de serem confirmadas.

Não se somam, e nenhuma está errada. São a caixa de correio (241), o arquivo (213) e a lista de trabalho de hoje (170).

**2. Quantas das 241 já não precisam existir como candidatas.**
Só **2** — e nem essas são repetições. São duas páginas diferentes de sites que
já temos registados. Resolvem-se com uma anotação a dizer "é a mesma fonte,
outra porta". As outras 239 são todas genuinamente novas.

**3. Quantas o Bot pode decidir sozinho.**
**172 de 241.** E a razão é boa: a todas falta a mesma coisa — abrir **um**
documento e guardar a prova. Isso não exige opinião nem julgamento; exige um
programa que vá buscar, meça e guarde. É trabalho de máquina.

**4. Quantas precisam mesmo de uma pessoa.**
**69** — e são todas o mesmo assunto: páginas de LinkedIn e Instagram, que estão
bloqueadas por regra. Isso não são 69 leituras: é **uma única decisão** —
"mudamos a regra sobre redes sociais, ou não?". Uma pergunta, uma resposta, 69
casos resolvidos.

**5. O próximo passo para o Source Curator virar processo contínuo.**
Construir uma coisa só: **o capturador de exemplos**. Um programa que, para cada
candidata, abre um documento, mede-o e guarda a prova. É isso que destranca até
172 fontes de uma vez — sem descobrir nada de novo, apenas terminando o que já
foi começado.

**E o que ainda trava, de verdade.**
Uma única coisa, e muito menor do que eu disse de manhã: o registo de cada
"corrida" não anota a que fonte pertence. Só que essa informação existe ao lado,
no registo de cada documento — portanto dá para reconstruir. O espaço para a
anotação já está definido no contrato; falta preenchê-lo. É da Collection, não
deste departamento.

Já a parte grande — saber se uma fonte **serviu para alguma coisa** — continua
impossível, porque a camada que liga documentos a conclusões ainda não existe.
Isso não mudou, e não devo fingir que sim.

---

**HARD STOP.** Nada foi integrado ao runtime. Nenhum merge foi feito. Nenhuma
transição foi escrita na fila. A worktree do COORDINATOR não foi aberta nem
tocada — tudo lido por `git show`. Este documento é uma proposta e aguarda
decisão do dono.
