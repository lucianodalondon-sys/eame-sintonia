# PILOTO SOCIAL CONTROLADO — 15 canais dos 89

**Data:** 2026-09-04 · **HEAD antes:** `f62e858` · **Branch:** `claude/human-agricultural-sensors-8fv0fw`

```
NEW_ENTITY_DISCOVERY = NO   PORTAL_TOUCHED = NO   DEPLOY_TOUCHED = NO
CANONICAL_INTELLIGENCE_TOUCHED = NO   BRAZIL_TOUCHED = NO
APIFY_USED = NO             NEW_SCRAPER_CREATED = NO
```

Artefatos: [`PILOT-SELECTION.json`](../../data/samples/IT-HUMAN-SENSORS/PILOT-SELECTION.json) ·
[`PILOT-BATCH.json`](../../data/samples/IT-HUMAN-SENSORS/PILOT-BATCH.json) ·
[`PILOT-MEASUREMENT.json`](../../data/samples/IT-HUMAN-SENSORS/PILOT-MEASUREMENT.json)

---

## 1 · O DONO CANÔNICO — declarado antes de executar

> ⚠️ **"SINTONIA SCRAP" não existe como componente no repositório.** O nome aparece
> **apenas em documentos desta branch** — fui eu que o propaguei. O componente real tem
> nome próprio, e registrar isso evita que alguém procure um dono sob um rótulo que não
> existe.

Há **três** implementações, e elas não competem — cobrem etapas da mesma escada:

| implementação | o que é | estado |
|---|---|---|
| **`scripts/youtube_janela.py`** | rota **pública gratuita** de YouTube: fases `canais` · `objetos` · `legendas`. Declara `APIFY_RUNS=0`, `COST_USD=0` no próprio artefato | ⬅️ **dono canônico deste piloto** |
| `scripts/youtube_transcrever.py` | Whisper — só o que a legenda não deu | não acionado |
| `scripts/sensor_coleta.py` + `coletor.py` + `apify_pool.py` | rota **paga** (Apify) | ⛔ exige `APIFY_TOKEN`, ausente |

```
SCRAP_CANONICAL_OWNER      = scripts/youtube_janela.py
SCRAP_VERSION/HEAD         = f62e858 (arquivo pré-existente, não modificado)
SCRAP_SUPPORTED_PLATFORMS  = [YOUTUBE]
SCRAP_UNSUPPORTED_TODAY    = [INSTAGRAM, TIKTOK, LINKEDIN, TWITTER, FACEBOOK]
```

**A ordem é lei, e foi obedecida:**
`LOTE CONGELADO → CANAL → OBJETO → LEGENDA → (só então) WHISPER → (só então) PAGO`

O reúso foi por **injeção**: o lote do piloto e o diretório de saída foram apontados para o
dono canônico, que roda sem alteração. `git status` confirma que os artefatos da missão
anterior (`data/samples/YOUTUBE-JANELA/`) **não foram tocados**.

---

## 2 · SELEÇÃO — registrada ANTES da coleta

```
PILOT_CHANNELS_REQUESTED  = 15
PILOT_CHANNELS_SUPPORTED  = 15   (após substituição)
PILOT_CHANNELS_UNSUPPORTED = 4
SUBSTITUIÇÕES              = 4
FOLLOWERS USADO NA SELEÇÃO = não
```

Regra: **A** (papel provado, com rota) → **B** (todos os pesquisadores com canal
monitorável) → **C** (uma fonte por entidade + sondas de plataforma).

Quatro selecionados não tinham rota (Instagram, TikTok, LinkedIn, Twitter). Foram
substituídos por YouTube preservando a estratificação — e o motivo ficou gravado por canal.

### ⛔ LACUNA DE FAMÍLIA REGISTRADA

> **A família PESQUISADOR COM VOZ PÚBLICA cai inteira.** Os dois pesquisadores com canal
> monitorável publicam em **Twitter** e **LinkedIn**; nenhuma das duas tem rota gratuita, e
> a paga exige o token ausente.
>
> **`RESEARCHER_PUBLIC_CHANNELS_TESTED = 0`.** A pergunta *"o canal público do pesquisador
> acrescenta algo que o Europe PMC não entrega?"* **não pôde ser respondida nesta rodada.**

---

## 3 · PROVA DA CADEIA — fechada num canal

```
SCRAP_CHAIN_PROVED = SIM
```

| # | elo | valor |
|---|---|---|
| 1 | `SOURCE_ID` | `IT-S-000071` |
| 2 | URL | `youtube.com/@agraliastudio` |
| 3 | rota | `scripts/youtube_janela.py` · porta `URLLIB` |
| 4 | objeto | `youtube.com/watch?v=Q5dscL-_ynI` |
| 5 | `DOCUMENT_ID` | `IT-D-Q5dscL-_ynI` |
| 6 | texto | *"AgraliaTech — com'è la situazione del primo vigneto…"* |
| 7 | `SOURCE_ID` preservado | `IT-S-000071` ✅ idêntico à origem |
| 8 | `ENTITY_ID` | `IT-E-000189` → Agralia studio di agronomia |

A junção é determinística: `ACCOUNT_HANDLE` do lote **é** o `SOURCE_ID`. Nenhum casamento
por nome.

---

## 4 · O QUE ENTROU

```
PILOT_CHANNELS = 15    PILOT_ENTITIES = 15    PILOT_DOCUMENTS = 150
YOUTUBE = 15 · LINKEDIN = 0 · INSTAGRAM = 0 · TIKTOK = 0 · OTHER = 0
ROLE_PROVED_SOURCES = 4    ROLE_UNKNOWN_SOURCES = 11
```

| classe | n |
|---|---:|
| **A · FIELD_SIGNAL** | **1** |
| **B · TECHNICAL_INTERPRETATION** | **4** |
| **C · RESEARCH_COMMUNICATION** | **2** |
| **D · MARKET_OR_COMMERCIAL** | **5** |
| **E · GENERAL_AG_CONTENT** | **49** |
| **F · OFF_TOPIC** *(provado)* | **7** |
| **G · NÃO SEI** | **82** |

`AG_RELEVANT = 61` (41%) · `TRANSCRIPTIONS = 0` · `KNOWN_COST = 0 USD` (declarado pela
rota: `APIFY_RUNS=0`, `COST_USD=0`, `EVIDENCE_CLASS=PUBLIC_FREE_ROUTE`).

### ⚠️ O 82 É O RESULTADO PRINCIPAL, E ELE QUASE FOI ESCONDIDO

A **camada de legendas não abriu**: `PORTA_NAO_ABRIU` nos 150 objetos. O `CHROME_EXECUTABLE`
foi declarado e o Chromium encontrado, mas a rota de navegador não completou em >15 min.
`HAS_CAPTION = 0`.

Sem legenda, o único texto é o **título** — mediana de **51 caracteres**.

A primeira versão desta medição classificou **98 documentos como `OFF_TOPIC`**. Estava
errado, e o erro é o mesmo que a casa já nomeou: **tratar ausência de texto como ausência de
assunto**. A prova apareceu nos próprios dados:

> **"Meli in filare agroforestale — Quarto anno — estate"** caiu em `OFF_TOPIC` porque o
> léxico não tinha o plural `meli`. **Meli é macieira.**

Corrigido: `OFF_TOPIC` passou a exigir **marcador positivo de assunto não-agrícola**
(`ricetta`, `bilancio di esercizio`, `assemblea`…) **ou** legenda presente. Sem isso, o
estado é `NÃO SEI`.

```
OFF_TOPIC   98 → 7        NÃO SEI   1 → 82
```

**82 de 150 documentos não puderam ser julgados.** Isso não é ruído — é a medida de que
**o piloto mediu títulos, não conteúdo.**

---

## 5 · O EXPERIMENTO — papel provado melhora a qualidade?

| | ROLE_PROVED | ROLE_UNKNOWN |
|---|---:|---:|
| fontes | 4 | 11 |
| documentos | 40 | 110 |
| `AG_RELEVANCE_RATE` | **0,425** | **0,400** |
| `FIELD_SIGNAL_RATE` | **0,000** | **0,009** |
| `TECHNICAL_RATE` | 0,025 | 0,027 |
| `OFF_TOPIC_RATE` | 0,150 | 0,009 |

> ### A resposta honesta é: **não há diferença mensurável.**
>
> 42,5% contra 40,0% em relevância agrícola, com 40 e 110 documentos, é ruído. E o único
> `FIELD_SIGNAL` do piloto veio de uma fonte **sem papel provado**.
>
> A hipótese de que papel previamente provado melhora o conteúdo como sensor **não se
> sustenta nesta amostra** — e a amostra é pequena, sem legenda, e com 55% dos documentos
> não julgáveis. O correto é `NÃO SEI`, não um "não" definitivo.

---

## 6 · AMOSTRAS — número sem exemplo não vale

### Os melhores

| classe | fonte | trecho | por que vale |
|---|---|---|---|
| **A** | Agralia studio di agronomia · há 1 mês | *"AgraliaTech — **com'è la situazione del primo vigneto**, quello da cui tutto ha avuto inizio"* | **estado de campo declarado em primeira pessoa**, cultura VINE, recente. É exatamente o sinal que a camada existe para achar |
| **B** | AgroNotizie · há 1 mês | *"**Infestanti resistenti**, perché il controllo comincia dopo la raccolta"* | plantas daninhas + resistência + janela de manejo — interpretação técnica com alvo ADAMA |
| **B** | Consorzio Agrario del Nordest | *"Marakas — **grano duro** consigliato anche in biologico \| CATALOGO VARIETALE"* | cultura declarada + recomendação técnica |
| **C** | AgresteTv · há 10 anos | *"Il progetto MYCO.PREV sulla prevenzione e il controllo delle **micotossine nei cereali**"* | comunicação de pesquisa em micotoxina de cereal — alvo ADAMA. ⚠️ Mas **há 10 anos**: recência importa |

### Os medianos — todos do mesmo canal, e isso diz algo

Três fichas de catálogo varietal do Consorzio Agrario (*"Riso Argo, resistente al brusone"*,
*"Mais ibrido MINISTERIO classe 700"*, *"Frumenti duri — CAMPAGNA 2021-2022"*): cultura
declarada, nenhum problema, nenhuma observação. **Agricultura real, sem sinal operacional.**
É `E` por definição — e mostra que um canal de cooperativa é sobretudo **catálogo**.

### Os inúteis — todos com prova, todos da mesma fonte

*"Ricetta Pasta Zafferano e Tonno"* · *"Assemblee Straordinarie Dicembre 2024"* ·
*"Bilancio di esercizio e consolidato al 31/12/2023"* — Terre dell'Etruria, uma cooperativa
cujo canal é **institucional e gastronômico**. Off-topic **provado** por marcador, não por
sobra.

---

## 7 · CUSTO

```
SCRAP_CALLS    = 15 canais + 15 grades + 150 tentativas de legenda
DOCUMENTS      = 150
DOWNLOADS      = 0 (nenhum vídeo baixado)
TRANSCRIPTIONS = 0
KNOWN_COST     = 0 USD — declarado pela rota (APIFY_RUNS=0, COST_USD=0)
```

O custo é **demonstrável e zero** porque a rota é pública. O que **não** é gratuito é a
camada de legenda por navegador, que consome máquina — e ela **não completou**.

---

## 8 · ZEROS OBRIGATÓRIOS

| trava | valor |
|---|---:|
| `IDENTITY_ERRORS` | **0** |
| `NEW_ENTITIES_FROM_CONTENT` | **0** (221 antes, 221 depois) |
| `ROLE_FROM_CONTENT` | **0** |
| `DOCUMENT_WITHOUT_SOURCE_ID` | **0** |
| `DOCUMENT_WITHOUT_ENTITY_ID` | **0** |

Nenhuma função deste piloto escreve em `ROLES`. O conteúdo disse **do que** se fala; não
tocou em **quem** a entidade é.

---

## PORTÃO DE ESCALA

```
PILOT_COLLECTION_EXECUTED    = SIM
HUMAN_SOCIAL_CONTENT_HAS_VALUE = NÃO SEI
SCALE_TO_89_CHANNELS         = NÃO
```

**`HAS_VALUE = NÃO SEI`** — e não é evasiva. O piloto encontrou **7 documentos com valor
operacional** (1 A + 4 B + 2 C) em 150, e um deles é exatamente o sinal procurado. Mas
**82 documentos não puderam ser julgados** por falta de legenda. Declarar "tem valor" com
55% do corpus ilegível seria afirmar o que não foi medido; declarar "não tem" seria pior.

**`SCALE_TO_89 = NÃO`**, contra as seis condições:

| # | condição | estado |
|---|---|---|
| 1 | documentos ligados a `SOURCE_ID` | ✅ **SIM** — 150/150, cadeia provada |
| 2 | identidade intacta | ✅ **SIM** — 0 entidades novas, 0 papéis do conteúdo |
| 3 | há conteúdo agrícola útil | ⚠️ **PARCIAL** — 61 relevantes, mas só 7 operacionais |
| 4 | classe operacional além de GENERAL | ✅ **SIM** — A=1, B=4, C=2 existem |
| 5 | custo/desperdício proporcional | ⛔ **NÃO** — **rendimento de 7 em 150 sem a camada que importa** |
| 6 | duplicação com fontes científicas compreendida | ⛔ **NÃO** — a família pesquisador **não foi testada** |

**Duas condições falham.** Escalar para 89 canais agora significaria coletar ~890 títulos e
continuar sem poder julgar metade deles.

> ⚠️ **CORRIGIDO EM 2026-09-04 — `CAMADA-DE-LEGENDAS-DIAGNOSTICO.md`, D-038.**
> Esta seção afirmava que as duas condições falhavam **pela mesma causa: a legenda**. Era
> hipótese, e a medição refuta metade. Dos 89 canais monitoráveis, a família pesquisador tem
> **2 — um no Twitter, um no LinkedIn, ZERO no YouTube**. Legenda é camada de YouTube: não
> alcança quem não está lá. **Só a condição 5 depende da legenda.** A condição 6 continuaria
> bloqueada com a legenda funcionando perfeitamente.

### O que muda o veredito — e é uma coisa só

> **Abrir a camada de legendas.** Ela é gratuita, já existe em `youtube_janela.py`, já vem
> com tempos, e substitui o Whisper. Sem ela o piloto lê capas de livro; com ela lê o texto.
>
> O bloqueio é de **ambiente** (o navegador não completou), não de arquitetura nem de
> crédito. Resolver isso é mais barato que qualquer alternativa — e é pré-requisito para
> que a pergunta "vale manter?" tenha resposta.

> ⚠️ **CORRIGIDO EM 2026-09-04 — `CAMADA-DE-LEGENDAS-DIAGNOSTICO.md`, D-035 e D-037.**
> "O navegador não completou" estava certo pelo motivo errado: o Chromium morria em 0,43 s e
> o código esperava 25 s por um processo morto, para então **afirmar o falso**. Isso está
> consertado — o erro real agora chega em 1 s. Mas **abrir a legenda não é "uma coisa só"**:
> são quatro muros empilhados, e o último (a reputação do IP de saída contra `/watch`, e o
> corpo vazio do `/api/timedtext`) **não é código deste repositório**.

**Parado aqui. Não escalei para 89. Não abri PR. Nada entrou no portal.**
