# PREPARAÇÃO FUNCIONAL — NOVAS CAPACIDADES EAME

**Data:** 2026-08-30 · **Branch:** `claude/sintonia-eame-portal-baseline`
**Modo:** `PREPARE · MEASURE · MAP · TEST` — **`DO NOT INTEGRATE`**

```
PRODUCT_IMPLEMENTATION_MODE = NOT_ENTERED
FINAL_REFRESH_EXECUTED      = NO
CASCO_V7_MODIFIED           = NO
REAL_DATA_WIRED             = NO
```

> Nada aqui está ligado ao casco. Os adaptadores rodam sobre **fixtures aparadas** de
> artefatos reais, lidos do Git em commit fixado. Nenhuma escrita em Supabase, nenhuma
> alteração de schema canônico, nenhuma branch mesclada, nenhuma superfície criada.

**Onde as coisas estão**

| | |
|---|---|
| adaptadores | [`scripts/functional_prep.py`](../../scripts/functional_prep.py) |
| protótipo isolado | [`scripts/functional_sandbox.py`](../../scripts/functional_sandbox.py) |
| provas | [`tests/test_functional_prep.py`](../../tests/test_functional_prep.py) — **36 provas** |
| fixtures + proveniência | `data/functional-sandbox/fixtures/` |
| medição derivada | `data/functional-sandbox/PREP-MEDICAO.json` |

**Suíte inteira:** `365 testes · OK · 0 falhas`.

---

## 0 · AS TRÊS MEDIÇÕES QUE MUDAM COMO SE LIGA ISTO DEPOIS

Antes das fichas, o que a preparação **mediu** — e que nenhum documento dizia.

### 0.1 · Linha de índice não é entidade — inflação de **2,6×**

O índice do Creator Map lista a mesma pessoa **uma vez por cultura**.

```
LOOKUP_BY_ACTIVATION_STATE.ACTIVATION_READY     26 linhas
                                                10 entidades distintas
                                                 8 PERSON_CREATOR + 2 FARM_BUSINESS
```

Quem ligar a mangueira contando linha publica **26 creators prontos** onde há **10 pessoas
e empresas**. O adaptador deduplica por identidade, e `contar()` **sempre** devolve os dois
números — nunca só um. É a mesma lei que o repositório já pagou em `157 canais / 252 vídeos`.

### 0.2 · Conta local não é empresa

```
22 contas locais provadas    →    5 empresas distintas
ES 10 · IT 8 · FR 4               BAYER 7 · SYNGENTA 8 · NUFARM 3 · BASF 3 · CORTEVA 1
```

Colapsar conta em empresa apagaria exatamente o que a camada mede: **a mesma empresa fala
diferente em países diferentes**. `COMPANY_LOCAL_ACCOUNT ≠ COMPANY`.

### 0.3 · Creator pronto e caso aberto **não coincidem**

Testei os três recortes congelados no protótipo isolado:

| recorte | pessoas prontas | empresas prontas | especialistas | contas locais |
|---|---:|---:|---:|---:|
| `ES-OLIVE-REPILO` | **2** | 0 | 2 | 10 |
| `IT-VINE-FLAVESCENCE` | **0** | 0 | 2 | 8 |
| `FR-CEREAL-SEPTORIA` | **0** | 0 | 2 | 4 |

**Em 2 dos 3 recortes não há creator pronto nenhum.** Isso é medição, não veredito — mas é
o teste que a PASSAGEM 1 pediu para decidir entre *ferramenta própria* e *camada de caso*
(J4). Uma ferramenta de creators alimentada por caso ficaria vazia em dois terços dos casos
congelados; uma ferramenta autônoma teria conteúdo, mas responderia uma pergunta que não é
a do caso. **A decisão pertence à arbitragem.**

---

# A · CREATOR MAP

```
CAPABILITY                  = CREATOR_MAP
SOURCE_HANDOFF              = docs/creators/HANDOFF-INTELLIGENCE-CREATOR-MAP-EAME.md
SOURCE_ARTIFACT             = data/samples/CREATOR-MAP-EAME/CREATOR-CAPABILITY-EAME.json
SOURCE_BRANCH               = claude/eame-agro-creators-map-77c4ld
SOURCE_COMMIT               = 2018c5c8e0bd2c0d63d7ee14af423f158544a4d8
STATE                       = FROZEN_WAITING_FOR_INTELLIGENCE
SAFE_TO_PREPARE_NOW         = YES
```

**`ANALYTICAL_UNIT` — duas, e elas nunca se somam**

```
PERSON                 pessoa física com canal público        8 ACTIVATION_READY
FARM_BUSINESS_ENTITY   empresa agrícola                       2 PARTNER_READY
```

O próprio artefato escreve a lei: *"a soma NUNCA se chama `CREATORS_READY`. Pessoa ≠
empresa."* Tipos `MEDIA_ACCOUNT`, `ORGANIZATION` e `OTHER` **não viram objeto** — forçá-los
numa das duas unidades seria o erro que a fonte proíbe. Há prova disso.

**`DECISION_QUESTION`**
> *Se o Marketing quiser agir para esta cultura neste país/região, quem já tem relevância
> real junto àquele público?* — e a pergunta é **avaliar/chamar**, nunca *contratar*.

**`REAL_FIELDS_AVAILABLE`** (10 preservados por resultado, todos medidos)
`IDENTITY_EVIDENCE` · `CROP_PROOF` · `RECENT_ACTIVITY` (30/90 d, com `AS_OF_DATE`) ·
`PUBLIC_CHANNEL` · `PUBLIC_CONTACT` · `AUDIENCE_FACING` · `BRAND_HISTORY` ·
`COMPETITOR_HISTORY` · `AS_OF_DATE` · `WHAT_IS_NOT_KNOWN`
mais `ENTITY_TYPE`, `ACTIVATION_STATE`, `ACTUAL_FARMER`, `COUNTRY`, `REGION`.

**`MISSING_FIELDS`**
`AUDIENCE_TYPE` (não medida em ninguém fora de um caso) · `REVALIDATION_NEEDED_AFTER`
(`NOT_YET_DEFINED` **de propósito** — cadência varia por pessoa, cultura e estação, e uma
validade arbitrária seria precisão sem lastro) · `PUBLIC_CONTACT` em boa parte das fichas ·
`REGION` em várias.

**`JOIN_KEYS_PROVED`** — declaradas pela própria fonte
`PERSON_ID` · `ENTITY_ID` · `BRAND` · `COUNTRY` · `CROP` · `OBSERVED_AT`

**`JOIN_KEYS_NOT_PROVED`**
`CROP → ISSUE` — o creator prova cultura, **nunca problema de campo** ·
`PERSON ↔ SCIENTIFIC_PERSON` (nenhum ORCID neste artefato) ·
`PERSON ↔ META_AD` — a própria fonte diz que, se a missão Meta achar uma destas pessoas
num anúncio, isso vira `CREATOR_APPEARANCE_OBSERVED`, e **`PAID_CREATOR_RELATION` só sobe
com prova adicional**.

**`EXISTING_SURFACE_CANDIDATE`** · `Radar/Casos` → detalhe do caso (aba `Áreas ADAMA`, rota
de ação de Marketing) · `Acervo` (as fichas são material com proveniência)
**`CASE_LAYER_CANDIDATE`** · **SIM** — camada `AUDIÊNCIA / ATIVAÇÃO` dentro do caso
**`NEW_TOOL_CANDIDATE`** · **`BOTH_POSSIBLE`** — e 0.3 é o dado que decide

**`SEMANTIC_GUARDRAILS`**
```
PERSON_CREATOR != FARM_BUSINESS — a soma nunca se chama CREATORS_READY
ACTIVATION_READY = "o Marketing já consegue avaliar" — nunca "contratar"
FOLLOWERS != AUTHORITY · o artefato não ordena e não pontua
ROW != ENTITY (2,6× de inflação medida)
NOT_ASKED != NOT_READY — recorte ausente do índice não é reprovação
CREATOR não confirma FIELD_PROBLEM, INCIDENCE, MARKET_OPPORTUNITY nem PRODUCT_FIT
```

**`BLOCKED_UNTIL_FINAL_HANDOFF`** · nada. O handoff chegou e está congelado.
**O que ainda não pode ser mostrado:** audiência de ninguém; qualquer ordenação; qualquer
número que some pessoa com empresa.

---

# B · COMPETITOR FORESIGHT

```
CAPABILITY                  = COMPETITOR_FORESIGHT
SOURCE_HANDOFF              = NENHUM
STATE                       = NO_ARTIFACT_IN_REPO
SAFE_TO_PREPARE_NOW         = NO
```

**Medido, não suposto.** Varri **os 13 refs de `origin`** por nome de arquivo contendo
*foresight* e por `git grep`. Resultado: **zero artefatos**. As duas únicas ocorrências
estão dentro de artefato de **outra** missão, e são a fronteira que ela declara:

> *"IP, BRAND, REGULATORY e PRODUCT continuam do Foresight. Esta camada só entrega
> `PUBLIC COMMUNICATION EVENTS` e usa ID de lá quando existir; senão, `NOT_KNOWN`."*
> — `MEDICAO-PRIMEIRO-LOTE-V1.json`, com `READY_FOR_FORESIGHT_JOIN = NO`

**`ANALYTICAL_UNIT`** · desconhecida. Os candidatos plausíveis são unidades **diferentes**
entre si — `TRADEMARK`, `LOCAL_REGISTRATION`, `PRODUCT/BRAND`, `PATENT` — e escolher uma
agora seria desenhar schema a partir do nome da missão.

`adaptar_foresight()` **existe e levanta erro**, com a data e o método da medição na
mensagem. **A falha é a entrega.** Há prova disso.

**`BLOCKED_UNTIL_FINAL_HANDOFF`** · **tudo.**

---

# C · COMPETITOR PUBLIC COMMUNICATION

```
CAPABILITY                  = COMPETITOR_PUBLIC_COMMUNICATION
SOURCE_ARTIFACT             = data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json
SOURCE_BRANCH               = claude/eame-competitor-public-communication
SOURCE_COMMIT               = c25e44ba14d963f45a3381205b2759690fef66b9
STATE                       = IDENTITY FREEZE_READY · CONTENT_COLLECTION_STAGE = NOT_STARTED
SAFE_TO_PREPARE_NOW         = YES — somente a estrutura de identidade
```

**`ANALYTICAL_UNIT` = `COMPANY_LOCAL_ACCOUNT`** — uma conta, numa plataforma, num país.
**Nunca "a empresa".**

**Lote autorizado: 22 contas** (recontei de forma independente e bate)

```
ES 10 · IT 8 · FR 4
BAYER 7 · SYNGENTA 8 · NUFARM 3 · BASF 3 · CORTEVA 1
FACEBOOK 10 · YOUTUBE 7 · INSTAGRAM 5 · LINKEDIN 0 (bloqueado: nenhuma conta local provada)
22 URLs distintas — nenhuma colisão
```

Regra de entrada, escrita pela fonte: `ACCOUNT_IDENTITY_STATE = PROVED` **E**
`COUNTRY_SCOPE = LOCAL_COUNTRY_PROVED` **E** `PAGE_ROLE = COMPANY`.
Funil: 72 tentadas → 44 com link → 32 `PROVED` → **22 autorizadas**.

**`REAL_FIELDS_AVAILABLE`** · `COMPANY` · `COUNTRY` · `PLATFORM` · `ACCOUNT_HANDLE` ·
`ACCOUNT_URL` · `COUNTRY_SCOPE` · `PAGE_ROLE` — cada um com **evidência própria**
(`IDENTITY_EVIDENCE`, `COUNTRY_SCOPE_EVIDENCE`, `PAGE_ROLE_EVIDENCE`).

**`MISSING_FIELDS`** · **o conteúdo inteiro.** Nenhum post, nenhum vídeo, nenhuma data,
nenhum tema. `CONTENT_COLLECTION_STAGE = NOT_STARTED`, e a missão declara por que ainda não
terminou: *"identidade congelada não responde 'sobre o que a empresa está falando' nem 'o
que mudou'."*

**`JOIN_KEYS_PROVED`** · `COUNTRY` · `COMPANY` (para agrupar contas, nunca para colapsá-las)
**`JOIN_KEYS_NOT_PROVED`** · `COMPANY ↔ LOCAL_REGISTRATION` (é do Foresight, que não existe)
· `ACCOUNT ↔ META_PAID_ACTIVITY` (camada separada, nunca somada) ·
`ACCOUNT ↔ CROP/ISSUE` (só o conteúdo diria, e ele não existe)

**`EXISTING_SURFACE_CANDIDATE`** · `Caso` → aba `Convergência` → bloco **Competição como
camada** — que no casco já tem as quatro linhas certas e todas em `NÃO SEI`. Também
`Fontes`, como origem com estado de acesso.
**`CASE_LAYER_CANDIDATE`** · **SIM**
**`NEW_TOOL_CANDIDATE`** · **`CAN_FIT_EXISTING_SURFACE`** — o casco já reservou o lugar; a
decisão canônica de 2026-08-30 é que competição é **camada estrutural**, não aba própria

**`SEMANTIC_GUARDRAILS`**
```
COUNTRY_SCOPE != PAGE_ROLE — duas perguntas independentes. A DEKALB France recuperou a
   prova que tinha justamente porque PRODUCT_BRAND deixou de ser um estado de país
OFFICIAL_ACCOUNT != LOCAL_COUNTRY_ACCOUNT
SAME_NAME != SAME_COMPETITOR_PRODUCT
PUBLIC_COMMUNICATION != META_PAID_ACTIVITY — PUBLIC=YES com META=NO_OBSERVED é estado
   válido, não contradição
ZERO hoje = NO_CONTENT_COLLECTION_EXECUTED · NUNCA COMPANY_NOT_COMMUNICATING
```

**`BLOCKED_UNTIL_FINAL_HANDOFF`** · **todo o conteúdo**, e com ele qualquer afirmação sobre
tema, frequência, mudança ou silêncio de concorrente.

---

# D · RESEARCHER / EXPERT DIRECTORY

```
CAPABILITY                  = EXPERT_DIRECTORY
SOURCE_ARTIFACT             = data/samples/SPEAKER-UNIVERSE-PILOT-V1.json  (nesta branch)
                            + data/samples/SENSOR-PILOT/CANAL-IDENTIDADE.json
STATE                       = RESEARCHER_AS_EXPERT_DIRECTORY = STRENGTHENED (veredito da
                              árbitra; ver ressalva abaixo)
                              RESEARCHER_AS_DAILY_PERSON_SENSOR = NOT_PROVED
SAFE_TO_PREPARE_NOW         = YES
```

⚠️ **Ressalva de custódia.** As strings `RESEARCHER_AS_EXPERT_DIRECTORY` e `STRENGTHENED`
**não existem em nenhuma branch** — procurei. São vereditos da aba árbitra, e esta rodada os
respeita como vieram. **A medição que os sustenta existe; o veredito escrito, não.** Mesma
situação dos estados do EARLY SIGNAL, já registrada em `O8` da PASSAGEM 1.

**`ANALYTICAL_UNIT` = `SCIENTIFIC_PERSON`** — e ela **não** é a mesma unidade que `PERSON`
do Creator Map. Um pesquisador com ORCID e um creator com handle são entidades diferentes,
provadas por rotas diferentes. `juntar()` recusa misturá-las.

**Números medidos:** 1.045 candidatos → 476 elegíveis → 13 tentados → **13 com identidade
provada**, distribuídos nos seis recortes congelados (2 por recorte), com ORCID resolvido em
`pub.orcid.org`, instituição declarada e obra em 2024 ou depois.

**`REAL_FIELDS_AVAILABLE`** · `PERSON_ID` (ORCID/OpenAlex) · `NAME` · `INSTITUTION` ·
`ROLE` · `CASE_ID` · `COUNTRY` + `COUNTRY_BASIS` (que diz explicitamente que é afiliação,
não nacionalidade)

**`MISSING_FIELDS`** · `PUBLIC_CHANNEL` não vem deste artefato · `REGION_OF_STUDY` **não
existe no registro** (0 % em 1.771 de 1.771, e está certo) · nenhum conteúdo ligado a
pessoa · cargo e empresa declarados não foram lidos (o modo usado do ator não os devolve)

**`JOIN_KEYS_PROVED`**
`CASE_ID` — a chave que amarra pesquisador a recorte, e a mais valiosa que este artefato tem
`PERSON_ID` (ORCID) · `COUNTRY`

**`JOIN_KEYS_NOT_PROVED`** — e este é o ponto fino
```
PERSON ↔ PUBLIC_CHANNEL     PARCIAL — 7 canais PROVED cobrindo 5 pessoas de 13;
                            12 PLAUSIBLE sem régua de promoção escrita; 25 NOT_PROVED
PUBLIC_CHANNEL ↔ CONTENT    NÃO PROVADO PARA NINGUÉM
SCIENTIFIC_PERSON ↔ PERSON  não testado — são unidades diferentes
```
Enunciado correto, o mesmo da PASSAGEM 1: `IDENTITY_LINKAGE_BARRIER_REDUCED` +
`CAPABILITY_NOW_TESTABLE`. **Não** `SCIENCE_TO_PUBLIC_VOICE_LINK = PROVED`.

**`EXISTING_SURFACE_CANDIDATE`** · `Caso` → aba `Ciência e pessoas`
**`CASE_LAYER_CANDIDATE`** · **SIM, e é o encaixe mais natural de todas as capacidades
estudadas** — `CASE_ID` já é a chave, e o protótipo acendeu 2 especialistas em **cada um**
dos três recortes testados. É a única capacidade nova que não deixou recorte vazio.
**`NEW_TOOL_CANDIDATE`** · **`CAN_FIT_EXISTING_SURFACE`**

**`SEMANTIC_GUARDRAILS`**
```
RECURRENCE != AUTHORITY — sem ordem, sem score, sem ranking
AUTHOR AFFILIATION != REGION OF STUDY
IDENTITY_PROVED != PUBLIC_CHANNEL_PROVED != CONTENT_LINKED
IDENTITY_PROVED != ISSUE_EXPERTISE_PROVED
pessoas identificadas exigem tratamento GDPR antes de qualquer exposição
CONTAGEM ALTA NÃO VALIDA IDENTIDADE — 58 organizações contra mediana 2 foi conflação
```

---

# E · EARLY SIGNAL TERRITORIAL — **em voo, não preparado**

```
CAPABILITY                  = EARLY_SIGNAL_TERRITORIAL
SOURCE_ARTIFACT             = data/samples/TERRITORIAL/MEDICAO.json
SOURCE_BRANCH               = claude/sintonia-eame-repo-setup-xccfob (841fb54)
STATE                       = MISSÃO EM CURSO — sem handoff
SAFE_TO_PREPARE_NOW         = NO
```

O artefato existe e é real, mas a missão é **uma das quatro que abrem o refresh final**.
Registro só a forma, para o adaptador não nascer errado depois:

```
ANALYTICAL_UNIT   CASE_SIGNAL (item territorial datado), não pessoa e não conta
22 fontes tentadas · 17 alcançáveis · 3 PROVADAS · 13 itens
CROP 100 % · COUNTRY 69 % · REGION 69 % · ISSUE 15 % · CHAVE COMPLETA 8 %
MULTI_SOURCE_OVERLAPS = 0 · INDEPENDENT_LAYER_OVERLAPS = 0
```

**O número que importa para o produto:** `ISSUE` em **15 %** e chave completa em **8 %**.
Sem `ISSUE`, um item territorial não entra num caso `país × cultura × problema` — ele fica
no Radar do Futuro como sinal solto. **E zero sobreposições entre fontes significa zero
convergência até agora.**

**`BLOCKED_UNTIL_FINAL_HANDOFF`** · tudo. Não preparei adaptador.

---

# F · CLASSIFICAÇÃO — sem decidir nada

| capacidade | classificação | por quê |
|---|---|---|
| **EXPERT_DIRECTORY** | `CAN_FIT_EXISTING_SURFACE` + `CASE_LAYER_CANDIDATE` | `CASE_ID` já é a chave; acendeu em 3 de 3 recortes |
| **COMPETITOR_PUBLIC_COMMUNICATION** | `CAN_FIT_EXISTING_SURFACE` | o casco já reservou as quatro linhas de competição no caso |
| **CREATOR_MAP** | **`BOTH_POSSIBLE`** | acendeu em 1 de 3 recortes: cabe como camada, mas ficaria vazia demais |
| **EARLY_SIGNAL_TERRITORIAL** | `NOT_ENOUGH_EVIDENCE` | missão em curso; `ISSUE` em 15 % |
| **COMPETITOR_FORESIGHT** | `NOT_ENOUGH_EVIDENCE` | não existe artefato |

**Nenhum `FINAL_TOOL` foi escrito.** Essa decisão pertence a
`FINAL REFRESH → RED TEAM → ARBITRATION → FINAL TOOL DEFINITION`.

---

# G · ONDE O CASCO V7 HOJE NÃO COMPORTA

Medido contra as doze superfícies, sem propor mudança:

| # | capacidade | o casco tem lugar? |
|---|---|---|
| G1 | especialista por caso | **sim** — aba `Ciência e pessoas` |
| G2 | competição como camada do caso | **sim** — quatro linhas, todas em `NÃO SEI` |
| G3 | **creator / ativação** | **não.** Zero superfícies, zero blocos, zero campos. É o `P3` da PASSAGEM 1, e continua aberto |
| G4 | **quinto relógio — "quem viu primeiro"** | **não.** O casco tem quatro relógios agronômicos; `COMPETITOR OBSERVATION CLOCK` não existe |
| G5 | **fila do que falta provar** (`MISSING_PROOFS`) | **não.** `Fontes` mostra estado da fonte, não estado da prova |
| G6 | **conta local × país × plataforma** | **parcial.** `Fontes` comporta a origem; não há onde mostrar 22 contas por empresa e país |

---

# H · PERGUNTAS QUE SÓ OS HANDOFFS FINAIS RESPONDEM

1. **Creator vira camada de caso ou ferramenta própria?** O dado que decide é quantos
   recortes abertos têm creator pronto. Hoje: **1 de 3**. O fechamento do piloto pode mudar.
2. **A camada Meta muda o `PAID_CREATOR_RELATION`?** A fonte já declarou que um creator num
   anúncio vira `CREATOR_APPEARANCE_OBSERVED`, e **não** relação paga.
3. **O Foresight traz `LOCAL_REGISTRATION` como chave?** Sem ela, `COMPANY ↔ REGISTRO` não
   fecha, e a competição fica só com identidade de conta.
4. **A coleta de conteúdo do concorrente sobrevive ao runner?** `MISSION_STATE =
   READY_TO_COLLECT_WHEN_RUNNER_AVAILABLE`.
5. **O territorial fecha `ISSUE` acima de 15 %?** Abaixo disso, sinal territorial não entra
   em caso — fica no Radar do Futuro.
6. **Os 12 canais `PLAUSIBLE` sobem para `PROVED`?** É o que move
   `PERSON ↔ PUBLIC_CHANNEL` de 5/13 para perto de 17/13… ou não move.

---

# ENTREGA

```
PRODUCT_IMPLEMENTATION_MODE = NOT_ENTERED
FINAL_REFRESH_EXECUTED      = NO
CASCO_V7_MODIFIED           = NO
REAL_DATA_WIRED             = NO

CAPABILITIES_PREPARED       = 3   CREATOR_MAP · COMPETITOR_PUBLIC_COMMUNICATION ·
                                  EXPERT_DIRECTORY
CAPABILITIES_REFUSED        = 2   COMPETITOR_FORESIGHT (sem artefato) ·
                                  EARLY_SIGNAL_TERRITORIAL (missão em curso)

ADAPTERS_PREPARED           = 4   adaptar_creator_capability · adaptar_public_comm ·
                                  adaptar_expert_directory · adaptar_foresight (falha
                                  fechado, de propósito)
                                  + juntar() e contar(), que impõem as leis

TESTS_ADDED                 = 36  (suíte: 329 -> 365, OK, 0 falhas)

STRUCTURAL_GAPS_FOUND       = 6   G1..G6 — e três são novos: creator sem superfície,
                                  quinto relógio ausente, fila de provas sem casa

READY_FOR_FINAL_REFRESH_LATER = YES

EXACT_BLOCKERS
  1  COMPETITOR FORESIGHT nao tem artefato em nenhuma das 13 branches de origin
  2  conteudo de comunicacao publica: CONTENT_COLLECTION_STAGE = NOT_STARTED
  3  EARLY SIGNAL TERRITORIAL sem handoff; ISSUE em 15 %, chave completa em 8 %
  4  META COMPETITOR sem entrega — EU-T9-002 continua NAO TESTADO
  5  PERSON <-> PUBLIC_CHANNEL provado para 5 de 13; conteudo ligado a pessoa: ninguem
  6  vereditos da arbitra (EARLY SIGNAL e EXPERT DIRECTORY) sem artefato no repositorio
```

**Notas de execução**

- Os testes ficaram em `tests/test_functional_prep.py`, e **não** em `tests/functional-prep/`
  como o briefing sugeriu: `unittest discover` **não entra** em diretório cujo nome tem
  hífen, e a suíte seria pulada em silêncio. Teste que não roda é pior que teste que falta.
- Adicionar 36 provas mudou `TEST_COUNT_CURRENT` de 329 para 365 e a suíte reprovou seis
  documentos com número velho — que é exatamente o mecanismo funcionando.
  `scripts/metricas_canonicas.py --sync` corrigiu os seis marcadores; o handoff e o prompt
  da nova conta foram atualizados à mão porque a contagem deles vive em prosa, fora de
  marcador. No `PROMPT-PARA-NOVA-CONTA-CLAUDE.md` havia ainda um `TEST_COUNT_CURRENT = 280`
  contradizendo o próprio arquivo três linhas abaixo; foi corrigido junto.
