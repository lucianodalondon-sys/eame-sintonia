# C10.8B — A PRIMEIRA ROTA PAGA CANÔNICA

`C10_8B_FIRST_PAID_ROUTE = BLOCKED_PROVIDER_CREDENTIAL`

> A autorização humana foi dada: **US$ 0,10**, uma execução, um POST. A ligação
> foi construída e provada inteira contra a API falsa. O gasto **não aconteceu**,
> e não aconteceu por uma razão que nenhum código pode resolver: não existe
> credencial paga neste ambiente.
>
> ```
> APIFY_TOKEN_POOL   vazio neste container
> PAID_CREDENTIAL    AUSENTE
> READY_TO_SPEND     NO
> GASTO REAL         US$ 0,00
> ```

---

## 1 · A AUTORIZAÇÃO, E O QUE ELA NÃO É

```
AUTHORIZED_MAX_USD       = 0.10   teto TOTAL da execução C10.8B
MAX_PROVIDER_RUNS        = 1
MAX_PROVIDER_START_POSTS = 1
```

Não é US$0,10 por tentativa, por item, por ator nem por etapa. E não foi usada:
o teto ficou intacto porque nenhum POST saiu.

---

## 2 · A PERGUNTA DESTA MISSÃO NÃO É A DA CAPACIDADE

```
CAPABILITY_STATE != ROUTE_STATE.
```

`youtube.native_caption` já estava `PROVEN`. O que estava por provar é a **rota
paga** — `apify:transcricao`, declarada `POSSIBLE_NOT_PROVED` — e ela continua
por provar, porque uma rota só se prova a correr.

```
CAPABILITY_STATE_BEFORE = PROVEN
CAPABILITY_STATE_AFTER  = PROVEN     (intocada, como mandava o briefing)
ROUTE_STATE_BEFORE      = POSSIBLE_NOT_PROVED
ROUTE_STATE_AFTER       = POSSIBLE_NOT_PROVED
POLICY_CHANGED          = NO
```

---

## 3 · O CENSO DA ROTA

As quatro rotas que a matriz declara para `YOUTUBE/FETCH_TRANSCRIPT`:

| rota | classe | permitida | estado |
|---|---|---|---|
| `youtube-data-api-v3:captions.download` | `OFFICIAL_API_FREE` | **NÃO** | `REQUIRES_OWNER_PERMISSION` |
| `youtube-data-api-v3:captions.list` | `OFFICIAL_API_FREE` | **NÃO** | `REQUIRES_AUTHORIZATION` |
| `timedtext` | `DIRECT_HTTP` | **NÃO** | `ROUTE_NOT_ALLOWED` |
| `apify:transcricao` | `APIFY` | CONDICIONAL | `POSSIBLE_NOT_PROVED` |

É por isso que a rota paga é a **padrão** aqui, e é por isso que o motivo
canônico é `ROUTE_NOT_ALLOWED` — as três livres estão fechadas, não caras.

```
PAID_REASON = ROUTE_NOT_ALLOWED   ∈ MOTIVOS_PAGOS   ✔
```

---

## 4 · O CONTRATO DO ATOR, LIDO E NÃO LEMBRADO

```
ACTOR_ID         = pintostudio~youtube-transcript-scraper
ACTOR_OWNER      = regras/sensor_coleta.py :: ATORES['YOUTUBE_TRANSCRIPT']
INPUT_SCHEMA     = {'videoUrl': '<watch url>'}          ← SINGULAR
OUTPUT_SCHEMA    = [ {url, transcript, chars} ]
CAP_FIELD        = maxTotalChargeUsd
COST_FIELD       = usageTotalUsd
RUN_STATUS_FIELD = status
DATASET_FIELD    = defaultDatasetId
```

O relatório da C10.8A-F citava este ator como análogo medido. Ele **é** o ator
declarado — mas o contrato da entrada mudou, e quem o descobriu foi a própria
plataforma:

```
API recusou HTTP 400: invalid-input — Field input.videoUrl is required
```

`videoUrls` (plural, lista) é o que rodou em Espanha e está no `RUN-MANIFEST`.
Hoje o ator exige o singular.

```
ENTRADA PROVADA ONTEM != ENTRADA VÁLIDA HOJE.
```

O `OUTPUT_SCHEMA` não veio de documentação: veio dos **bytes preservados** de
uma corrida anterior deste mesmo ator, em
`data/samples/raw-paid/ES-T8-001-youtube-transcripts.raw.json.gz`. Três campos,
e nenhum deles diz a língua, as marcas de tempo, ou se o texto é legenda do
YouTube ou ASR.

---

## 5 · O ALVO VEIO DO ACERVO

```
TARGET_VIDEO_ID          = EAkcA_2FDN8
TARGET_URL               = https://www.youtube.com/watch?v=EAkcA_2FDN8
TARGET_SOURCE_ARTIFACT   = data/samples/SENSOR-PILOT/TRANSCRICOES-B.json
HISTORICAL_RUN           = SENSOR-TR-B-3-p3  (mesmo ator, v1.0.57, SUCCESS)
HISTORICAL_OUTPUT        = 97.710 caracteres preservados
```

Nenhuma descoberta nova, nenhuma pesquisa no YouTube, nenhum vídeo aleatório. É
a corrida histórica mais longa deste ator no acervo, e serve de base de
comparação para a corrida que ainda não houve.

---

## 6 · A LIGAÇÃO, E OS TRÊS PAPÉIS QUE NÃO SE MISTURAM

```
scrap_executor.COLLECT        o boundary, o CHECK, os dois tetos
    → social_rotas            política, autorização de gasto, motivo canônico
        → adaptador_youtube   sabe o que é um vídeo e como se lê uma legenda
            → coletor         o dono do dinheiro: fala com a Apify, grava o RAW
                → o ator
```

```
ADAPTER != PROVIDER != EXECUTION ENVIRONMENT.
```

`youtube_legenda_paga` não conhece `api.apify.com`, não monta cabeçalho, não lê
`usageTotalUsd` e não sabe o que é `maxTotalChargeUsd`. Ela monta a entrada do
ator, chama o dono pago **uma vez**, e traduz a saída para o envelope canônico.

### Uma chave, e não a rotação

`apify_pool` roda chaves quando uma esgota. Rodar numa rota paga é um **segundo
POST de criação** — e um segundo POST é uma segunda compra, mesmo que o primeiro
não tenha devolvido `run_id`.

```
ROTAÇÃO DE CHAVE É UMA SEGUNDA COMPRA.
```

A rota usa a primeira posição e para. E não tem ator de reserva: o
`YOUTUBE_TRANSCRIPT_ALT` que existe em `sensor_coleta` ficou de fora de
propósito — `SECOND_ACTOR = NO`.

---

## 7 · O TETO DE REDE DE UMA CORRIDA, MEDIDO

Não foi arbitrado. Foi lido em `coletor.executar` e confirmado contra a API
falsa:

```
1   POST /acts/{ator}/runs?waitForFinish=60&maxTotalChargeUsd=…
≤1  GET  /actor-runs/{id}                consulta, só se não terminal aos 60 s
1   GET  /datasets/{id}/items
2   GET  /key-value-stores/{id}/keys + /records/{chave}
─────
C10_8B_NETWORK_BUDGET = 5
```

O que torna o teto **finito** é o `wait`. A plataforma concede 60 s no próprio
POST; tudo acima disso vira consulta, e cada consulta é uma ida à rede. Com
`wait=60` o resto é zero e há no máximo uma consulta; com 120 haveria até treze.

```
UM `wait` MAIOR NÃO É MAIS PACIÊNCIA. É MAIS IDAS À REDE.
```

Medido: corrida terminal → 3 idas. Corrida que não termina aos 60 s → 4. As duas
cabem em 5.

---

## 8 · O ENSAIO OFFLINE PASSOU INTEIRO

`provas/primeira_rota_paga.py`, com a API da Apify falsa e **nada mais** falso.
Os bytes que o falso devolve são os bytes reais de uma corrida preservada do
mesmo ator.

```
EXECUTOR_REACHED             YES   RESULT = OK
ROUTER_REACHED               YES   ROTA = apify:transcricao · CLASSE = APIFY
ADAPTER_REACHED              YES   um envelope canônico
PAID_PROVIDER_OWNER_REACHED  YES   MEDIDA.IMPLEMENTACAO = coleta/coletor.py
NETWORK_BUDGET_ACTIVE        YES   limite 5 · usados 3
FINANCIAL_BUDGET_ACTIVE      YES   autorizado 0.10 · cap enviado 0.10
RAW_CREATED                  YES   PRESERVED, com SHA-256
OUTPUT_CREATED               YES   19.281 caracteres
TRACE_CREATED                YES   provider, rota, classe, motivo, custo
DIRECT_BYPASS                NO
```

E o falso é sempre `subprocess.run` **dentro** do coletor — a camada mais funda,
por baixo dos dois tetos.

```
UM FAKE ACIMA DO GATE MEDE O FAKE.
```

---

## 9 · O PORTÃO QUE PAROU A MISSÃO

```
  ok     CAPABILITY_STATE           = PROVEN
  ok     ROUTE_STATE                = POSSIBLE_NOT_PROVED
  ok     POLICY                     = CONDICIONAL
  ok     ACTOR                      = pintostudio~youtube-transcript-scraper
  ok     TARGET_VIDEO_ID            = EAkcA_2FDN8
  ok     MAX_PROVIDER_RUNS          = 1
  ok     MAX_PROVIDER_START_POSTS   = 1
  ok     FINANCIAL_BUDGET           = 0.10
  ok     FINANCIAL_REMAINING        = 0.10
  ok     PROVIDER_SIDE_CAP          = <= 0.10, decidido pelo saldo
  ok     NETWORK_BUDGET             = 5
  ok     PAID_REASON                = ROUTE_NOT_ALLOWED
  ok     WIRING_OFFLINE             = PASS
  NÃO    PAID_CREDENTIAL            = AUSENTE
  NÃO    CHECK.CAN                  = False

  READY_TO_SPEND = NO
  CHECK.STATE    = CREDENTIAL_MISSING
  GASTO          = 0 · nenhum POST foi enviado
```

Treze portões verdes, dois vermelhos, e os dois são o mesmo facto:
`APIFY_TOKEN_POOL` está vazio neste container. A chave existe nos *Secrets* do
GitHub — `.github/workflows/sintonia-scrap.yml` injeta-a — e não chega a uma
sessão que corre fora do workflow.

```
A CHAVE EXISTIR NO COFRE NÃO É A CHAVE CHEGAR AO PROCESSO.
```

Deste lado do processo, «não temos credencial» e «a ligação do segredo está
partida» parecem iguais, e a sonda diz só o que consegue provar:
`CREDENTIAL_MISSING NESTE AMBIENTE`. Quem distingue é o workflow.

E a recusa é canônica, não um acidente: `CREDENTIAL_MISSING` tem recuperação
`HUMAN_PROVISION_CREDENTIAL` — a única falha desta cadeia que pede gente.

---

## 10 · DOIS PORTÕES, E CADA UM SEGURA SOZINHO

A credencial é lida em dois sítios, e não por descuido:

```
credencial_paga_presente()   a sonda GRATUITA do `CHECK` — zero rede, zero dólar
youtube_legenda_paga()       a própria rota, antes de chamar o dono pago
```

```
UM PORTÃO QUE SÓ FUNCIONA PORQUE OUTRO O PRECEDE NÃO É UM PORTÃO.
```

Medido: desligando a sonda, a rota continua a recusar com `CREDENTIAL_MISSING` e
o saldo continua inteiro. Um mutante que removesse o segundo portão sobrevivia à
primeira versão desta bateria — e é por isso que a segunda sentinela existe.

---

## 11 · O DEFEITO QUE O RED TEAM ENCONTROU

Um POST que cai no transporte pode ter criado uma execução paga. O orçamento
sabia disso — segurava os US$0,10 em `UNKNOWN` — mas o **rastro** dizia outra
coisa:

```
antes:  COST_STATE = NOT_RUN      ← a única coisa que aquele momento não foi
depois: COST_STATE = UNKNOWN · ACTUAL = None · UNKNOWN_USD = 0.10 · REMAINING = 0.00
```

Duas metades do mesmo defeito:

- `coletor.executar` só anexava a reserva ao manifesto quando a fechava **ali**;
  no caminho em que ela fechava antes — justamente o pior — o manifesto não
  dizia nada;
- `social_rotas` só levantava o custo do balde no caminho de **sucesso**, e uma
  rota que falhou pode ter gastado na mesma.

```
NOT_RUN != UNKNOWN. UMA COMPRA DUVIDOSA NÃO É UMA COMPRA QUE NÃO HOUVE.
UMA RESERVA QUE NÃO SOBE AO MANIFESTO DEIXA O RASTO DIZER «NÃO CORREU».
```

---

## 12 · A ESPÉCIE DO TEXTO NÃO SE INVENTA

O ator devolve `{url, transcript, chars}`. Não diz a língua, não devolve marcas
de tempo, e não declara se o texto é a legenda que o YouTube publica ou um ASR
que ele próprio fez.

```
SPECIES    = NOT_DECLARED_BY_PROVIDER
TIMESTAMPS = NO
LANGUAGE   = UNKNOWN
```

```
CAPTION != TRANSCRIPT != ASR.
O QUE O PROVIDER NÃO DECLARA, A CASA NÃO INVENTA.
```

E um item devolvido com texto vazio continua a ser um item: `pedida e vazia` é
um estado, não uma ausência.

---

## 13 · MEDIDO

```
ATTACKS 34 · POSITIVE_FINDINGS 0   (dois achados encontrados e corrigidos antes)
MUTANTS 16 · SURVIVORS 0
PROVIDER_RUNS 0 · APIFY_RUNS 0 · PAID_RUNS 0 · REAL_COST_USD 0
NETWORK_REAL 0
```

---

## 14 · UMA SENTINELA QUE MUDOU DE LADO

A C10.8A-F escreveu `test_39`: «nenhuma capacidade de rota paga tem adaptador».
Era um **censo** — a foto daquele dia — e esta missão ligou uma de propósito,
com autorização humana e teto declarado.

```
UM CENSO QUE VIRA LEI TRANCA A PORTA QUE ELE SÓ MEDIU.
```

Ela não foi apagada. Passou a guardar o que continua a valer: a lista de rotas
pagas ligadas é **fechada e nomeada**, e cada uma tem sonda gratuita de
prontidão. Uma segunda a nascer em silêncio reprova ali na mesma.

---

## 15 · O QUE NÃO MUDOU

A capacidade continua `PROVEN`. A rota continua `POSSIBLE_NOT_PROVED` e
`CONDICIONAL` — `POLICY_CHANGED = NO`. Os dois tetos, a taxonomia de falha, o
registo e a matriz estão intocados no que decidem. Bluesky, a C10.8A corrigida e
todo o resto da cadeia estão como estavam. Nada fora do SINTONIA SCRAP foi
desenvolvido.

## 16 · O QUE CONTINUA DESCONHECIDO

- Se o ator ainda responde, e com que custo real: **não houve corrida**.
- Se `EAkcA_2FDN8` ainda tem legenda pública hoje.
- O custo liquidado de qualquer coisa desta missão — não há o que liquidar.
- Se o contrato da entrada mudou outra vez desde a última medição.

```
SCRAP_RAW_CAPTURED             = NO   (não houve corrida)
SCRAP_RAW_READ_BACK            = NO
CANONICAL_FORWARD_PRESERVATION = NO   (e é de outra frente)
```

## 17 · O VEREDITO, E POR QUE ELE NÃO ESTÁ NA LISTA

O briefing ofereceu nove vereditos. Nenhum descreve o que aconteceu, e
arredondar para o mais próximo seria dizer uma coisa que não é verdade:

```
PASS_ROUTE_PROVED             não — a rota não correu
PASS_ROUTE_PARTIAL            não — não houve corrida para ser parcial
PAID_RUN_INCONCLUSIVE         não — isto diria que houve corrida e não se soube o fim
BLOCKED_NO_SENTINEL           não — a sentinela existe, com corrida e texto preservados
BLOCKED_PROVIDER_CONTRACT     não — o contrato foi lido e provado offline
BLOCKED_PROVIDER_CAP          não — o `maxTotalChargeUsd` foi enviado e medido
BLOCKED_NETWORK_BOUND_UNKNOWN não — o teto é 5, e está demonstrado
BLOCKED_POLICY                não — a política autoriza a rota com motivo canônico
FAIL                          não — nenhum gate desta missão foi violado
```

O que bloqueou tem nome, e a casa já o tinha no vocabulário:

```
C10_8B_FIRST_PAID_ROUTE = BLOCKED_PROVIDER_CREDENTIAL
CHECK.STATE             = CREDENTIAL_MISSING
RECOVERY_ACTION         = HUMAN_PROVISION_CREDENTIAL
```

Se for preciso um valor da lista original, o mais honesto é ler como um bloqueio
de **pré-condição** — o irmão de `BLOCKED_PROVIDER_CONTRACT`, mas do lado da
credencial e não do esquema. Não é um `FAIL`: a missão parou no portão que
existe para a parar, com o dinheiro intacto.

---

## 18 · RISCO RESTANTE

A ligação está construída e nunca correu contra o provider real. O ensaio
offline mede o **nosso** lado do contrato; o lado do ator só se mede a gastar.
Quando a chave existir, a primeira corrida continua a ser a primeira — com o
mesmo teto, o mesmo alvo e o mesmo POST único.
