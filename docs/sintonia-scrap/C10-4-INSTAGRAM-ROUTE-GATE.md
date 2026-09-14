# C10.4 — A AQUISIÇÃO DO INSTAGRAM ATRAVESSA O PORTÃO CANÔNICO DE ROTAS

    C10_4_ROUTE_GATE = PASS

A C9 mediu que a cadeia de Reel não passava pelo mesmo portão que as outras
plataformas. A C10 estreitou a aquisição — vídeo inteiro virou só som. Nenhuma
das duas tocou no encanamento: a cadeia continuava a entrar pela porta de
serviço.

    CAPACIDADE PROVADA NÃO É CAPACIDADE AUTORIZADA. Quem prova que CONSEGUE
    não respondeu ainda se PODE, e essas duas perguntas têm donos diferentes.

---

## 1. A DECISÃO DE POLÍTICA, MEDIDA ANTES DE MEXER EM NADA

```
POLICY_OWNER          leis/social_matriz.py
ROUTE                 INSTAGRAM / FETCH_TRANSCRIPT
PROVIDER              LOCAL_EXECUTOR (faster-whisper, dono único em fala_local.py)
CURRENT_DECISION      PERMITIDA = SIM · ESTADO = PROVED · AUTH_MODE = PUBLIC
WHY                   «já medido nesta casa; reusar, não recriar»
RUNTIME_BYPASS_EXISTS YES  (era; deixou de ser nesta missão)
```

A pergunta só fica honesta quando se separa o que a cadeia FAZ do que a matriz
DECLARA. A cadeia faz duas coisas: vai buscar os bytes e reconhece a fala. O
primeiro impulso é procurar `FETCH_VIDEO_BYTES`. Medido:

| capacidade | INSTAGRAM declara? | o portão responde |
|---|---|---|
| `FETCH_TRANSCRIPT` | sim | `ALLOWED` |
| `FETCH_VIDEO_BYTES` | **não** | `NOT_DECLARED` |

E `FETCH_VIDEO_BYTES` é exatamente a capacidade que a C10 provou que esta casa
**não** exerce: `VIDEO_BYTES_DOWNLOADED = 0`. Pedir autorização para o que não
se faz seria alargar a superfície no papel — e superfície no papel é superfície.

### A rota que a política já permitia baixa MAIS do que a nossa

O `ROTA` declarado é `instagram_transcrever.py:faster-whisper`. Esse ficheiro
está vivo, em `ferramentas/`, e o que ele faz é:

```
ferramentas/instagram_transcrever.py:182-183   baixa o MP4 INTEIRO da CDN da Meta
ferramentas/instagram_transcrever.py:225       ffmpeg -vn  →  deita a imagem fora
ferramentas/instagram_transcrever.py:277       transcreve
```

A cadeia da C10 pede `-f bestaudio` e nunca recebe imagem nenhuma. Logo:

    A ROTA QUE A POLÍTICA JÁ PERMITE BAIXA O VÍDEO INTEIRO.
    A ROTA QUE A C10 PROVOU BAIXA SÓ O SOM.

Ligar a cadeia da C10 debaixo de `FETCH_TRANSCRIPT` é **estreitar** o que já
estava autorizado: mesma plataforma, mesma capacidade, mesmo host, estritamente
menos bytes. Um subconjunto não amplia autorização nenhuma.

    ROUTE WIRING != CAPABILITY EXPANSION.

---

## 2. TRÊS PALAVRAS QUE NÃO SÃO SINÓNIMOS

`social_matriz` passou a saber responder à pergunta «pode?» a quem não é o
roteador. A resposta tem três palavras, e nenhuma cobre a outra:

```
NOT_DECLARED       ninguém mediu esta capacidade nesta plataforma.
ROUTE_NOT_ALLOWED  mediram, e nenhuma rota viável sobrou.
ALLOWED            há rota declarada, permitida e viável.
```

As três têm caso vivo na matriz de hoje, medido — não inventado para o exemplo:

| caso | resposta |
|---|---|
| `INSTAGRAM / FETCH_VIDEO_BYTES` | `NOT_DECLARED` |
| `LINKEDIN / FETCH_POST` | `ROUTE_NOT_ALLOWED` |
| `INSTAGRAM / FETCH_TRANSCRIPT` | `ALLOWED` |

Colapsar a primeira na segunda faz a casa dizer «não pode» onde a verdade é
«ninguém sabe». Ao contrário é pior: transforma ausência de medição em
autorização que ninguém deu.

    NÃO DECLARADO NÃO É PROIBIDO, E MUITO MENOS É PERMITIDO.

`decisao()` **lê**. Não escreve `PERMITIDA` nenhuma, e há teste que o prova
chamando-a três vezes e comparando a matriz antes e depois.

---

## 3. O QUE MUDOU — TRÊS FICHEIROS, E O TERCEIRO É UMA PALAVRA

### `coleta/scrap_capacidades.py`

`instagram.reel.transcribe` tinha `MATRIZ = None`. Sem tradução, `pela_matriz`
devolvia `None`, `_rota_executavel` devolvia `None`, e o roteador **nunca**
conseguia despachar a cadeia. Agora traduz para `FETCH_TRANSCRIPT`.

As outras duas — `instagram.reel.capture` e `instagram.reel.audio` — continuam
com `MATRIZ = None`, de propósito. Traduzi-las faria o registo nomear uma rota
que não é a delas.

    UM TRACE QUE NOMEIA A ROTA ERRADA MENTE COM PRECISÃO DE RELOJOEIRO.

### `coleta/adaptador_instagram.py`

O registo de `instagram.reel.transcribe` passou de `executa=` para `rota=`. Na
língua desta casa isso não é cosmética — a docstring de `registar()` já o dizia:

```
executa   nao ha porta a atravessar; a funcao monta o proprio trace.
rota      ha porta; `social_rotas` mede o portao ANTES de chamar seja o que for.
```

Até aqui a nota que justificava `executa` era **verdadeira**: a matriz não
conhecia nenhuma das três. Agora conhece esta.

    UMA PORTA QUE EXISTIA POR NÃO HAVER PORTÃO NÃO SOBREVIVE AO PORTÃO.

E `capturar_reel` — que serve as três capacidades — pergunta à política **antes
do `import` da cadeia**. Não é zelo: `reel_transcricao` traz o `yt-dlp` e o
reconhecedor atrás dele, e perguntar depois de carregar a ferramenta já é ter
decidido que sim.

    O PORTÃO QUE CORRE DEPOIS DA REDE NÃO É UM PORTÃO. É UM RELATÓRIO.

### `leis/social_matriz.py`

Ganhou `decisao()` e as três palavras. **Nenhum `PERMITIDA`, `ESTADO`, `CLASSE`
ou `CUSTO` foi tocado** — há teste que fixa a linha do Instagram exatamente como
estava, e outro que prova por AST que só este ficheiro escreve `PERMITIDA`.

---

## 4. A PROVA NEGATIVA — POLÍTICA DIZ NÃO, E NADA SE MOVE

Com a decisão em `NAO` (andaime de memória; o ficheiro de política não é tocado):

```
OBJETOS            0
RESULT             ROUTE_NOT_ALLOWED
ADAPTER_CALLED     não chega a delegar
NETWORK_TOUCHED    NO   (trava real no socket; sair levanta)
YTDLP_RUNS         0
ASR_RUN            NO
PAID_PROVIDER      false
```

E a recusa diz **qual** das três palavras foi: tirar a linha da matriz devolve
`NOT_DECLARED`, pôr `PERMITIDA = NAO` devolve `ROUTE_NOT_ALLOWED`. A casa não
usa a mesma palavra para «não pode» e para «ninguém mediu».

    ERROR != REJECTED != UNKNOWN != NOT_RUN != ROUTE_NOT_ALLOWED.

A porta de trás também bate no portão: chamar `capturar_reel` diretamente, sem
roteador nenhum, devolve a mesma recusa. Se só o roteador perguntasse, bastava
não usar o roteador para a política deixar de existir.

---

## 5. A PROVA POSITIVA — A ARESTA EXISTE E FOI OBSERVADA

Sentinela `DW6X5lZkU41`, bytes já preservados, **zero rede** (trava armada
durante a execução inteira):

```
CHECK.CAN                 true
CHECK.MATRIZ_CAPABILITY   FETCH_TRANSCRIPT
CHECK.ADAPTER             adaptador_instagram
CHECK.COST_TO_CHECK_USD   0.0
ROTA_ESCOLHIDA            instagram_transcrever.py:faster-whisper
CLASSE_DA_ROTA            LOCAL_EXECUTOR
AUTH_MODE                 PUBLIC
RESULT                    OK
OBJETOS                   1
COST_USD                  0.0
PAID_PROVIDER_USED        false
VIDEO_STREAMS             0
AUDIO_STREAMS             1
BYTES                     968 697
TRANSCRIPT_STATE          OK   (2 374 caracteres)
```

`MODULE EXISTS != EDGE EXISTS != FLOW EXISTS` — aqui o fluxo correu, devolveu
objeto, e o objeto tem transcrição.

### O que o registo passou a dizer, e porquê

A matriz chama esta rota `instagram_transcrever.py`. Quem correu foi
`reel_transcricao.py`. São dois ficheiros vivos da **mesma classe permitida**.
Escolher qual deles a matriz deve nomear é decisão de política — logo, de gente.
Até lá o registo diz as duas coisas:

```
ROTA_ESCOLHIDA           o que a política escolheu
MEDIDA.IMPLEMENTACAO     ferramentas/reel_transcricao.py
MEDIDA.ASR_OWNER         ferramentas/fala_local.py
MEDIDA.POLICY_OWNER      leis/social_matriz.py
```

---

## 6. IDENTIDADE E GEOGRAFIA, RECONFERIDAS PELO CAMINHO NOVO

A ficha RAW produzida **através do portão**, não por chamada direta:

```
SOURCE_ID         NAO SEI                                   ← C10.1 intacta
SOURCE_URL        https://www.instagram.com/reel/DW6X5lZkU41/
PUBLISHER         2182500157                                ← conta, campo próprio
NOTES.PLATFORM    INSTAGRAM                                 ← C10.3 intacta
NOTES.POST_ID     DW6X5lZkU41
COUNTRY_SCOPE     NAO SEI
SOURCE_LOCATION   NAO SEI
FACT_LOCATION     NAO SEI
```

O portão de rota não mexeu em nenhum destes conceitos, que é o que se pedia.

---

## 7. RED TEAM — DEZASSETE TENTATIVAS, DEZASSETE QUEDAS

| # | tentativa | medida |
|---|---|---|
| 1 | chamar o adaptador direto e pular o portão | `ROUTE_NOT_ALLOWED`, 0 objetos, 0 rede |
| 2 | portão consultado depois da rede | pergunta na L106, `import` da cadeia na L109 |
| 3 | política negativa ignorada | 0 objetos, 0 chamadas ao `yt-dlp`, 0 rede |
| 4 | queda para vídeo depois do portão | 4 pedidos de mídia, todos `-f bestaudio` |
| 5 | URL de perfil virar descoberta | `POST_ID = NOT_KNOWN` |
| 6 | `SOURCE_URL` virar `SOURCE_ID` | `SOURCE_ID = NAO SEI` |
| 7 | `PLATFORM` virar localização | as duas localizações ficam `NAO SEI` |
| 8 | `COUNTRY_SCOPE` virar localização | `COUNTRY_SCOPE = IT`, `SOURCE_LOCATION = NAO SEI` |
| 9 | portão de rota virar portão temático | nenhuma palavra de juízo no adaptador |
| 10 | o adaptador decidir T3/T9 | nenhum campo de juízo no objeto |
| 11 | Apify aparecer | classe `LOCAL_EXECUTOR`, 0 pagos, custo 0,0 |
| 12 | segundo dono de política nascer | só `leis/social_matriz.py` escreve `PERMITIDA` |
| 13 | segundo dono de ASR nascer | `ASR_OWNERS = 1` |
| 14 | módulo existir sem aresta | rota ligada e traduzida nos dois sentidos |
| 15 | aresta declarada sem fluxo | 1 objeto real, com rota nomeada |
| 16 | teste passar sem atingir o dono real | tirar a linha da matriz muda a resposta |
| 17 | retorno não-COLHEITA entrar em Ingresso | nenhum ficheiro da cadeia de Ingresso tocado |

---

## 8. DUAS CICATRIZES DE SONDA NESTA MISSÃO

**A sonda que encontrou zero e chamou a isso limpo.** A busca por «quem escreve
`PERMITIDA`» procurava alvo de atribuição e argumento nomeado. Na matriz,
`PERMITIDA` é **chave de dicionário**. A sonda encontrou zero ficheiros —
incluindo o próprio dono — e o teste dizia PASSOU.

    UMA SONDA QUE ENCONTRA ZERO E DIZ «LIMPO» MEDE A SONDA.

O conserto não foi só ver a terceira forma: foi o teste passar a **exigir o dono
na lista**. Se a busca deixar de o ver, falha em vez de aprovar o vazio.

**A trava de rede que reprovou a rota pela própria trava.** A primeira prova
positiva deu `ASR_FALHOU`. Não era a rota: o reconhecedor tem os modelos em
cache local e ainda assim bate na rede para confirmar versão, e a minha trava
bloqueou isso. Com `HF_HUB_OFFLINE=1` a mesma execução dá `TRANSCRIPT_STATE = OK`.
Irmã da cicatriz da C10.

---

## 9. DÍVIDA MEDIDA, NÃO CORRIGIDA AQUI

**`INSTAGRAM_TRANSCRIPT_TWO_IMPLEMENTATIONS = CONFIRMED`** — `instagram_transcrever.py`
e `reel_transcricao.py` fazem a mesma capacidade, e o primeiro **ainda baixa o
vídeo inteiro** antes de deitar a imagem fora. É a lei da C8 viva num segundo
sítio. Só um teste o importa hoje. Escolher o canónico é decisão de política.

**`AUDIO_ONLY_LABEL_ON_SUPPLIED_MEDIA = CONFIRMED`** — `AUDIO_ONLY_ACQUISITION`
sai `REUSED_NOT_ACQUIRED` quando os bytes vêm da gaveta desta casa, mas sai
`PROVEN` quando vêm de `midia_ficheiro=`. Nos dois casos esta execução não
adquiriu nada. A C10 fechou duas das três portas:
`PEDIR AUDIO != TER RECEBIDO SÓ AUDIO != TER ADQUIRIDO`. Por isso este documento
cita fluxos e bytes medidos, e não a etiqueta.

**`MATRIZ_EVIDENCE_PATH_DEBT = CONFIRMED`** — a matriz aponta
`scripts/instagram_janela.py` e `scripts/instagram_transcrever.py`. Os ficheiros
vivem em `coleta/` e `ferramentas/`. Caminho errado, decisão certa.

**`COUNTRY_SCOPE_NOT_FORWARDED = CONFIRMED`** — o executor sabe
`country_scope='IT'` e a ficha RAW sai `NAO SEI`. É ausência honesta, não
fabricação, e por isso não bloqueia nada.

**`PARENT_GATE_DEBT`** e **`SOCIAL_PROVENANCE_MODEL_GAP`** continuam como a C10.2
e a C10.3 as deixaram. Nenhuma foi tocada.

---

## 10. O QUE ESTA MISSÃO NÃO FEZ

Não mudou política. Não integrou a Collection. Não tocou Admission, Sala de
Espera, scheduler, Supabase, portal. Não abriu perfil, descoberta, stories,
comentários, hashtags, busca, seguidores, login, cookies nem navegador. Não
gastou um dólar: `APIFY_RUNS = 0`, `PAID_PROVIDER_RUNS = 0`, `COST_USD = 0,00`.

    CAN RUN THROUGH SCRAP GATE != FULL COLLECTION FLOW PROVEN.
