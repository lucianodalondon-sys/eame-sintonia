# C2 · YOUTUBE OFFICIAL-FIRST — a entrega

> **O que esta missão provou:** as quatro capacidades-alvo do YouTube atravessam
> a cadeia canônica inteira e falam com a **YouTube Data API v3**, com a chave
> que já existia nos Secrets, sem rota paga, sem `yt-dlp` escondido e sem que o
> segredo apareça em lado nenhum.
>
> **O que ela não fez:** não desligou actor, não encanou a Collection, não
> habilitou GPU, não instalou tradução, não tocou em migrations, portal, casco,
> deploy nem `main`.

---

# A · GIT

| campo | valor |
|---|---|
| **BRANCH** | `claude/sintonia-scrap-youtube-official-c2` |
| **SOURCE_BRANCH** | `claude/sintonia-scrap-convergence-c1` |
| **REFERENCE_HEAD** (coordenador) | `6c95260ef97cc77e626a41c2e854eab21c8bf263` |
| **ACTUAL_INITIAL_HEAD** (medido) | `6c95260ef97cc77e626a41c2e854eab21c8bf263` |
| **FINAL_HEAD** | o commit que traz este documento |
| **PUSH_STATE** | `PUSHED`, sem `force` |
| **WORKTREE** | `/home/user/eame-sintonia`, única e limpa |
| **DRIFT** | **NENHUM nesta branch** — local e `origin` no mesmo commit, árvore limpa |

**Mas houve movimento noutras frentes, e ele fica registado.** O
`git fetch --all --prune` trouxe duas branches adiantadas e duas novas:
`raw-observation-identity-3jbwco` (Phase 10, território proibido para mim),
`sintonia-eame-know-how-v1`, `cards-sensors-census-v1` e
`engineering-standard-v1`. **Nenhuma foi tocada, e nenhuma foi fundida.**

---

# B · API SECRET

| campo | valor |
|---|---|
| **SECRET_NAME** | `YOUTUBE_DATA_API_KEY` |
| **REFERENCE_LOCATION** | `.github/workflows/scrap-social.yml:154` |
| **INJECTED_BY** | o passo `1 · rodar a fase`, e **só ele** |
| **READ_BY** | `coleta/youtube_oficial.py:90` — `ENV_CHAVE` |
| **SECRET_VALUE_EXPOSED** | **NO** |
| **SECRET_WIRING** | **PASS** |

**A ligação já existia e estava certa.** Não foi preciso criar secret, nem
renomear nada, nem pedir a chave a ninguém. O que se mediu:

```
SECRET_REFERENCE_FOUND          YES   um nome só, e o mesmo dos dois lados
SECRET_INJECTED_TO_ENV          YES   entra no passo que precisa, não no job inteiro
APPLICATION_SEES_NONEMPTY_SECRET YES  o CHECK disse CAN=True nas quatro
API_CALL_AUTHENTICATED          YES   quatro métodos responderam OK
```

**A prova de que a chave serve é a chamada funcionar — não a impressão dela.**
Quatro varreduras sobre o log completo da corrida:

| padrão procurado | ocorrências |
|---|---|
| `AIza` | **0** |
| `key=` | **0** |
| `googleapis.com` | **0** |
| `Authorization:` | **0** |

As cinco ocorrências de `***` no log são mascaramento do próprio GitHub sobre o
bloco `env` e o token de checkout. **Nenhuma saiu de código meu.**

> **E não há impressão indireta.** Um teste desta missão proíbe, no corpo dos
> cinco ficheiros do caminho, `len(chave)`, `chave()[:`, `sha256(chave` e os
> `print` equivalentes.
>
> ```
> MEIO SEGREDO NUM LOG É UM SEGREDO NUM LOG. Um comprimento com prefixo
> identifica; um hash de chave curta quebra-se.
> ```

---

# C · LIVE API PROOF

**Corrida `34558827924`, `ubuntu-latest`, 2026-09-11T03:33Z**, na branch desta
missão, pelo workflow canônico.

| CAPABILITY | API_METHOD | RESULT | ITEM_COUNT | QUOTA | PROVIDER_USED |
|---|---|---|---|---|---|
| `youtube.search` | `search.list` | **OK** | 5 | 1 chamada, balde `SEARCH` | `OFFICIAL_API` |
| `youtube.channel.discovery` | `playlistItems.list` | **OK** | 5 | 1 unidade, balde `GENERAL` | `OFFICIAL_API` |
| `youtube.video.metadata` | `videos.list` | **OK** | 5 | 1 unidade, balde `GENERAL` | `OFFICIAL_API` |
| `youtube.comments` | `commentThreads.list` | **OK** | **25** | 1 unidade, balde `GENERAL` | `OFFICIAL_API` |

`COST_USD = 0.00` · `COST_BASIS = QUOTA_GRATUITA_OFICIAL` · `APIFY_CALLS = 0`.

### Foram precisas quatro corridas, e as três primeiras valem tanto como a quarta

| # | o que deu | o que ensinou |
|---|---|---|
| 1 | 4 de 4 `OK`, mas comentários `ZERO_RESULTS` | a cadeia atravessa |
| 2 | idem, três vídeos tentados | um zero repetido não vira prova por repetição |
| 3 | idem, **e o motivo apareceu**: a API diz `COMMENT_COUNT=0` nos três | o zero era **legítimo** |
| 4 | **25 comentários** | a descoberta passou a alimentar o resto |

```
ZERO LEGÍTIMO NÃO PROVA CAPACIDADE. Prova que aquele vídeo está calado.
```

Eu podia ter fechado na primeira corrida escrevendo «comentários provados: a
chamada atravessa». Atravessar não prova nada sobre trazer comentário. A cadeia
passou a andar como a coleta de verdade anda — **descobrir → medir → só então
perguntar comentário** — e o vídeo escolhido é o que a **própria API** diz ter
268 comentários.

---

# D · CENSO DOS ACTORS

```
CITADO ≠ EXECUTADO ≠ NECESSÁRIO — e esta missão acrescenta a quarta:
NECESSÁRIO PARA A CAPACIDADE ≠ REMOVÍVEL DO CÓDIGO HOJE.
```

| actor | CITED | CALLABLE | EXECUTED | capacidade | SAFE_TO_RETIRE | ACTION |
|---|---|---|---|---|---|---|
| `streamers~youtube-scraper` | SIM, 26 ficheiros | **SIM** | 30 runs · **US$ 4,4720** | busca, canal, metadados | **para A–C: SIM** · **remover hoje: NÃO** | `KEEP CONFIG` |
| `streamers~youtube-comments-scraper` | SIM, 22 ficheiros | **SIM** | 11 runs · **US$ 7,7280** | comentários | **para D: SIM** · **remover hoje: NÃO** | `KEEP CONFIG` |
| `pintostudio~youtube-transcript-scraper` | SIM, 21 ficheiros | **SIM** | 49 runs · US$ 0,1300 + **20 `NOT_PRESERVED`** | legenda | **NÃO** | `KEEP` |
| `starvibe~youtube-video-transcript` | SIM, 3 ficheiros | não medido | **0 runs** | legenda, reserva | n/a — nunca gastou | `HIGIENE, não economia` |

### Por que `SAFE_TO_RETIRE` não é um `YES` simples

Sete critérios foram pedidos. **Seis passam:**

| | critério | estado |
|---|---|---|
| R1 | capacidade coberta oficialmente | **PASS** — secção C |
| R2 | campos consumidos preservados | **PASS** — secção K |
| R3 | prova real com o secret existente | **PASS** — 4 de 4 |
| R4 | testes passam | **PASS** — 1.895, zero falhas novas |
| **R5** | **nenhum caller runtime permanece** | **FAIL** |
| R6 | nenhum fallback silencioso | **PASS** — secção L |
| R7 | erro e quota têm estado explícito | **PASS** — secção O |

**R5 falha, e falha por um motivo que não é meu para resolver nesta missão.**
Restam **três chamadores de runtime**, todos fora do escopo A–D:

| ficheiro | linha | o que faz |
|---|---|---|
| `coleta/comunicacao_coleta.py` | 267 → 308 | `ATORES['YOUTUBE']` alimenta `coletor.executar()` |
| `regras/sensor_coleta.py` | 568 e 699 | `ATORES['YOUTUBE_SEARCH']` idem |
| `regras/sensor_coleta.py` | 894 | `ATORES['YOUTUBE_COMMENTS']` idem |

Estes pertencem à frente de **comunicação pública** e à frente do **sensor**.
Apagar o identificador deles daqui deixaria as duas sem rota de YouTube nenhuma
— trocaria um gasto por um buraco.

```
A CAPACIDADE DEIXOU DE PRECISAR DO ACTOR. O CÓDIGO DE OUTRAS FRENTES AINDA
CHAMA. São duas frases verdadeiras ao mesmo tempo, e escrever só a primeira
seria declarar uma economia que ninguém realizou.
```

**Nada foi apagado.** A migração dos três chamadores é a missão seguinte.

---

# E · SEARCH

`search.list`, `q='agricoltura di precisione'`, `maxResults=5`, `type=video`,
`regionCode=IT`, `relevanceLanguage=it`. **5 objetos, `OK`.**

Campos consumidos: `id.videoId`, `snippet.title`, `snippet.description`,
`snippet.publishedAt`, `snippet.channelId`, `snippet.channelTitle`.

**`ytsearch` do `yt-dlp` NÃO foi usado.** Ele está `ROUTE_NOT_ALLOWED` na
matriz, e continua.

> `regionCode` molda o **ranking**, não prova lugar do autor. Por isso o objeto
> sai com `SOURCE_LOCATION = UNKNOWN` mesmo com `regionCode=IT` — em 100% dos
> casos, de propósito.

# F · CHANNEL / INCREMENTAL

`playlistItems.list` sobre a playlist de uploads do canal
`UCUs2Mg7jvUTRt7_MSOFYM5Q`. **5 objetos, `OK`.**

Identidade do canal, ids de vídeo, `publishedAt` e a proveniência da playlist
(`UPLOADS_PLAYLIST_PROVENANCE`) vêm no RAW.

**Não é busca, e a quota sabe disso:** `search.list` cai no balde `SEARCH`,
`playlistItems.list` no `GENERAL`. Um teste desta missão prova que uma busca não
consome o balde do outro.

# G · METADATA

`videos.list`, **5 identificadores numa chamada**, **1 unidade de quota**.

| | |
|---|---|
| `MAX_IDS_PER_CALL` | **50** (limite da API) |
| `QUOTA_PER_CALL` | **1 unidade, independente de quantos ids** |
| campos | `VIEW_COUNT`, `LIKE_COUNT`, `COMMENT_COUNT`, `DURATION`, `TAGS`, `CHANNEL_ID`, `CHANNEL_TITLE` |

```
CINCO CHAMADAS PARA CINCO VÍDEOS GASTARIAM CINCO VEZES O MESMO E DEVOLVERIAM
O MESMO. A diferença entre 1 e 50 é o dia inteiro de quota.
```

Dois testes guardam isto: um exige **uma** chamada para três ids, o outro exige
que o custo de 1 id e o de 10 sejam iguais.

# H · COMMENTS

**É o maior gasto histórico medido — US$ 7,7280 — e agora sai de graça.**

`commentThreads.list` sobre `jZffi5fLH8k`, escolhido porque `videos.list` disse
que tem **268 comentários**. **25 objetos, `OK`.**

Campos no RAW de cada comentário:

```
COMMENT_ID · PARENT_ID · IS_REPLY · VIDEO_ID · CHANNEL_ID
AUTHOR_CHANNEL_ID · AUTHOR_DISPLAY_NAME
TEXT_ORIGINAL · TEXT_DISPLAY · PUBLISHED_AT · UPDATED_AT · LIKE_COUNT
```

`TEXT_ORIGINAL` vem primeiro de propósito: `textDisplay` traz HTML e links
reescritos pela plataforma; `textOriginal` é o que a pessoa digitou.

### Os três estados não se colapsam, e há prova para cada um

| situação | estado | prova |
|---|---|---|
| vídeo com comentários | `OK` | 25 objetos, ao vivo |
| vídeo sem comentários | `ZERO_RESULTS` | corrida 3, com `COMMENT_COUNT=0` a explicar |
| comentários desligados | **`FEATURE_DISABLED`** | teste com `commentsDisabled` injetado |

```
COMENTÁRIO DESLIGADO É UM FATO SOBRE O VÍDEO. Não é ausência de coleta.
Para o FIELD VOICES futuro não é a mesma evidência, e juntar as duas hoje
apagaria a diferença para sempre.
```

# I · TRANSCRIPT

```
YOUTUBE_TRANSCRIPT_ZERO_APIFY = NO
```

**Nada mudou, e a existência da chave não muda nada aqui.** Remedido na matriz:

| rota | classe | permitida | porquê |
|---|---|---|---|
| `captions.download` | `OFFICIAL_API_FREE` | **NÃO** | *«SÓ O DONO DO VÍDEO. A doc exige permission to edit the video. Para canal de terceiro devolve 403.»* |
| `timedtext` | `DIRECT_HTTP` | **NÃO** | não documentado, e `/timedtext_video` está em `Disallow` |
| `apify:transcricao` | **`APIFY`** | `CONDICIONAL` | **única rota restante** para legenda de terceiro |

```
TER A CHAVE DA API NÃO ABRE A LEGENDA DE TERCEIRO. São coisas diferentes, e
usar uma como evidência da outra seria o erro mais fácil desta missão.
```

Um teste desta missão reprova se alguém mudar a rota padrão de `FETCH_TRANSCRIPT`
sem prova.

# J · MEDIA

```
YOUTUBE_MEDIA_ZERO_APIFY = NO
```

`youtube.media` continua **`BLOCKED`**, sem rota registada, com `403` de IP de
datacenter medido no benchmark. **Não foi ampliado, e o runner local não foi
acordado para isto.**

---

# K · OUTPUT COMPATIBILITY

Medido contra o artefato pago real, não contra memória:
`SENSOR-PILOT/VIDEOS-A.json` (221 itens) e `COMENTARIOS-A.json` (577 itens).

### Vídeo

| campo que o actor entregava | a API oficial dá? | onde |
|---|---|---|
| `TITLE` · `DESCRIPTION` · `PUBLISHED_AT` | **SIM** | envelope |
| `VIEWS` → `VIEW_COUNT` | **SIM** | RAW |
| `COMMENTS_COUNT` → `COMMENT_COUNT` | **SIM** | RAW |
| `DURATION` | **SIM** | RAW |
| `CHANNEL` · `CHANNEL_URL` | **SIM** | `CHANNEL_TITLE`, `CHANNEL_ID` |
| `EXTERNAL_ID` · `SOURCE_URL` | **SIM** | `NATIVE_ID`, `URL` |
| `SEARCH_TERM` | **SIM** | `QUERY` |
| **`TRANSCRIPT`** · `TRANSCRIPT_AVAILABLE` | **NÃO** | fora do escopo — secção I |
| `LIKE_COUNT` | **SIM, e o actor não dava** | RAW |
| `CASE_ID` · `LOTE` · `CROP` · `ISSUE` · `COUNTRY_OF_FACT` · `BATCH_ID` | **nossos** | a frente que chama os põe |
| `APIFY_ACTOR` | n/a | deixa de existir quando não há actor |

### Comentário

| campo do actor | a API oficial dá? |
|---|---|
| `COMMENT_ID` · `COMMENT_TEXT_RAW` · `LIKE_COUNT` · `VIDEO_ID` | **SIM** |
| `COMMENTER_NAME` · `COMMENTER_ID` | **SIM** |
| `DATE` | **SIM** — e absoluto |
| **`DATE_RELATIVE`** | **NÃO** — e não faz falta: a API dá o instante, e «há 2 meses» deriva-se dele, não o contrário |
| `COMMENTER_PROFILE_URL` | **derivável** do id do canal |
| **`UPDATED_AT`** | **SIM, e o actor não dava** | 
| **`PARENT_ID` · `IS_REPLY`** | **SIM, e o actor não dava** |

```
MISSING_FIELDS = TRANSCRIPT (fora do escopo) · DATE_RELATIVE (derivável)
EXTRA_FIELDS   = LIKE_COUNT no vídeo · UPDATED_AT · PARENT_ID · IS_REPLY
```

**Nenhum campo realmente consumido desaparece.** O `TRANSCRIPT` não desaparece
porque nem sequer é este actor que o traz.

---

# L · FALLBACK

```
APIFY_FALLBACK = NONE, nas quatro.
```

O trace de toda execução declara os quatro campos, e o validador **levanta** se
houver troca sem motivo. O esperado e o observado, ao vivo:

```
PROVIDER_REQUESTED = OFFICIAL_API
PROVIDER_USED      = OFFICIAL_API
WHY_FALLBACK       = null
PAID_PROVIDER_USED = false
```

Quando a API recusa, ninguém entrega e o trace di-lo — `PROVIDER_USED = None` —
em vez de outro fornecedor aparecer calado.

---

# M · POLICY

> **Três eixos independentes, e só um deles é engenharia.**

| evidência | estado | fonte |
|---|---|---|
| `ROBOTS_STATUS` | **RESTRICTED** | `/youtubei/`, `/results`, `/comment` e `/get_video` em `Disallow`. **A Data API v3 não passa por nenhum deles.** |
| `TERMS_STATUS` | **NÃO LEVANTADO** | nesta missão ninguém leu os Termos |
| `OFFICIAL_API_STATUS` | **DISPONÍVEL E USADA** | chave presente, quatro métodos responderam |
| `HOUSE_POLICY_STATUS` | **PERMITIDA** | `social_matriz` classifica a Data API v3 como a única rota permitida do YouTube |
| `CLIENT_AUTHORIZATION_STATUS` | **NÃO LEVANTADO** | |

```
A ROTA QUE ESTA MISSÃO USA É A ÚNICA QUE O PRÓPRIO REPOSITÓRIO JÁ CLASSIFICAVA
COMO PERMITIDA. Isso é mais forte do que «não medimos» — e ainda assim não
substitui os Termos, que ninguém leu.
```

---

# N · COST / QUOTA

**Recalculado por máquina sobre 119 registos, não herdado.**

| medida | valor |
|---|---|
| `MEASURED_HISTORICAL_SPEND_TOTAL` | **US$ 12,8140** |
| `MEASURED_YOUTUBE_SPEND` | **US$ 12,3300** — 96,2% do total |
| `MEASURED_SPEND_OF_RETIRED_RUNTIME_ACTORS` | **US$ 12,2000** |
| `MEASURED_SPEND_STILL_ASSOCIATED_WITH_REQUIRED_ACTORS` | US$ 0,1300 (transcript) |
| `NOT_PRESERVED_COST_RUNS` | **25 runs** |
| **`HISTORICAL_MEASURED_SPEND_ELIGIBLE_TO_AVOID`** | **US$ 12,2000** |

```
NÃO SE CHAMA SAVINGS_REALIZED. O futuro ainda não correu, e os três chamadores
de runtime ainda apontam para o actor. Chamar-lhe economia realizada seria
contar dinheiro que ninguém deixou de gastar.
```

E as três palavras continuam separadas: `0` medido, `NÃO SEI` não medido,
`NOT_PRESERVED` gastou e não guardou. **25 runs confessam a terceira.**

### Quota — grátis não é infinita

| método | balde | unidades/chamada | máx. itens/chamada |
|---|---|---|---|
| `search.list` | **`SEARCH`** | 1 chamada | 50 |
| `playlistItems.list` | `GENERAL` | 1 | 50 |
| `videos.list` | `GENERAL` | 1 | **50 ids** |
| `commentThreads.list` | `GENERAL` | 1 | 100 |

Limite do projeto: **100 no balde `SEARCH`**, **10.000 no `GENERAL`**, por dia.
Tetos por execução: 20 e 2.000 — um quinto do dia, de propósito.

```
ZERO_APIFY   ≠   ZERO_PAID_EXTERNAL_PROVIDER   ≠   OFFICIAL_API_QUOTA_USED
US$ 0,00 não quer dizer «à vontade».
```

`SEARCH_CALLS_REMAINING` e `GENERAL_UNITS_REMAINING` saem **`UNKNOWN`**: a API
não devolve saldo, e inventar um daria a alguém a confiança de gastar contra um
número imaginado.

---

# O · RED TEAM

Doze ataques. **Nenhum conseguiu colapsar dois estados num só.**

| # | ataque | resultado |
|---|---|---|
| 1 | remover o secret do ambiente | `CHECK` recusa **antes de gastar**: `CREDENTIAL_MISSING` |
| 2 | chave inválida sem imprimir o valor | **`AUTH_EXPIRED`** — distinto de ausente |
| 3 | quota estourada | **`QUOTA_EXHAUSTED`**, sem fallback |
| 4 | erro HTTP 500 | **`SOURCE_UNAVAILABLE`**, nunca `ZERO_RESULTS` |
| 5 | comentários desativados | **`FEATURE_DISABLED`** |
| 6 | resultado vazio legítimo | **`ZERO_RESULTS`**, e diferente do anterior |
| 7 | vídeo apagado | **`SOURCE_GONE`** |
| 8 | vários ids de metadata | **1 chamada, 1 unidade** |
| 9 | paginação de comentários | 25 objetos com `PARENT_ID` e `IS_REPLY` |
| 10 | procurar caller restante | **3 encontrados e nomeados** — secção D |
| 11 | procurar fallback silencioso | **zero**: seis razões, seis estados, `PROVIDER_USED = None` em todas as recusas |
| 12 | procurar segredo em log/artefato | **zero** |

> **O ataque 2 quase passou despercebido, e é o mais instrutivo.** O teto NOSSO
> desta execução (`BUDGET_EXHAUSTED`) e a quota DELES (`QUOTA_EXHAUSTED`) são
> estados diferentes. Chamar ao primeiro «quota» seria culpar o Google por uma
> trava que esta casa pôs.

---

# P · TESTS

```
python3 -m unittest tests.test_c2_youtube_oficial      →  43 testes, OK
método robusto, 77 módulos, sem o `test_comunicacao` que termina o processo
```

| | base `6c95260e` | final |
|---|---|---|
| **TOTAL** | 1.852 | **1.895** |
| **FAILURES** | 20 | **20** |
| **ERRORS** | 1 | **1** |
| **SKIPS** | 175 | 175 |

```
NEW_FAILURES = 0
```

`+43` testes, que são as provas desta missão. As 20 falhas restantes são
anteriores e pertencem a outras frentes.

---

# Q · SYSTEM MAP

```
py system-map/scripts/generate_system_map.py
py system-map/scripts/censo_das_estradas_it.py
py system-map/scripts/validate_system_map.py
```

**Os três, e não só o primeiro.** A C1 provou que `generate_system_map.py` não
chama o censo das estradas, e quem só corresse o gerador não veria uma aresta
mudar de sítio.

Resultado em **S**.

---

# R · C1 DOCUMENT FIX

O campo `C · FINAL_HEAD` da C1 dizia **«oito commits»**. Contado:

```
git rev-list --count 0e999fa1..6c95260e   →   11
```

Eu tinha contado os que nomeei `C1.x` e esquecido as três regenerações do mapa,
que são commits como os outros. **Corrigida essa frase, e só ela.**

```
UMA MISSÃO NOVA NÃO SERVE PARA MELHORAR O RELATÓRIO DA ANTERIOR.
```

---

# S · REGRESSIONS

```
NENHUMA. NEW_FAILURES = 0.
```

Três defeitos foram **encontrados e corrigidos dentro desta missão**, e os três
existiam antes dela:

1. **`COLLECT` não conseguia chamar nenhuma das quatro.** `TypeError` por falta
   de `country_scope`, e o caminho saltava os três portões de `social_rotas`.
2. **Credencial ausente chegava como `UNKNOWN_ERROR`.** A mensagem dizia, por
   extenso, «Isto é `CREDENTIAL_MISSING`»; o estado dizia outra coisa.
3. **A razão declarada pela API perdia-se.** `403` sozinho são três coisas;
   o corpo distingue-as, `estado_do_erro` sabia lê-lo, e o caminho do roteador
   deitava isso fora.

E um quarto, menor: **a sessão injetável morria no adaptador**, o que tornava
quota, vídeo apagado e comentário desativado impossíveis de exercer sem rede.

### E um defeito que eu próprio criei, e quase não vi

Os testes desta missão escrevem bruto porque a cadeia escreve bruto — e faz bem:
`guardar_raw` grava o corpo **antes** de normalizar, para que um normalizador
partido não obrigue a recoletar. Só que num teste o corpo é inventado, e ele caía
em `data/samples/SOCIAL-IT/raw-free/YOUTUBE/`, ao lado do bruto verdadeiro.

**Seis ficheiros chegaram a entrar num commit desta missão** com nomes como
`videos-aaaaaaaaaaa` e `comments-abc12345678`.

```
BRUTO DE TESTE AO LADO DE BRUTO DE COLETA É PIOR QUE LIXO: é a prova de uma
coleta que nunca aconteceu, com o nome certo e na pasta certa.
```

Removidos do índice e do disco, e a base dos testes passou a escrever numa pasta
temporária que morre com cada teste. A pasta ficou com **zero** ficheiros, o que
diz que os seis eram todos meus — nenhum bruto legítimo foi tocado.

---

# T · UNKNOWNs

| o que não sei | por quê |
|---|---|
| `TERMS_STATUS` e `CLIENT_AUTHORIZATION_STATUS` | não levantados |
| saldo real de quota | a API não o devolve, e ninguém abriu o Console |
| comportamento sob paginação longa | provado com 25 threads; 1.000 não foi tentado |
| `youtube.media` | continua `403` de datacenter; o runner local não foi acordado |
| legenda de terceiro | `captions.download` exige ser dono; nada mudou |
| se as outras frentes migram sem quebrar | os três chamadores não foram tocados |

---

# U · O QUE NÃO MUDOU

```
orquestrador/orquestrador.py · Collection schema · migrations · Admission
Intelligence · portal · deploy · GPU · CUDA · modelo de ASR
Instagram · LinkedIn · Facebook · X · Stories · fila ONLINE→LOCAL
motor de tradução · Phase 10/11 · main
```

E, dentro do YouTube: **nenhum actor foi desligado, apagado ou removido de
config**, e o histórico continua inteiro — `RUN-MANIFEST.json`, os cinco
`RUNS-*.json`, os artefatos pagos e os relatórios do benchmark.

**O roteador continua sem conhecer plataforma nenhuma.** Um teste desta missão
volta a exigi-lo, e acrescenta: ele também não importa `youtube_oficial`.

---

# V · VEREDITOS

| veredito | valor |
|---|---|
| `YOUTUBE_SEARCH_ZERO_APIFY` | **YES** |
| `YOUTUBE_CHANNEL_ZERO_APIFY` | **YES** |
| `YOUTUBE_METADATA_ZERO_APIFY` | **YES** |
| `YOUTUBE_COMMENTS_ZERO_APIFY` | **YES** |
| `YOUTUBE_TRANSCRIPT_ZERO_APIFY` | **NO** |
| `YOUTUBE_MEDIA_ZERO_APIFY` | **NO** |
| **`YOUTUBE_ZERO_APIFY_TOTAL`** | **PARTIAL** |

```
O TOTAL NÃO SE CALCULA POR MAIORIA. Quatro YES e dois NO dão PARTIAL, e
dariam PARTIAL mesmo que fossem cinco contra um.
```

**E `YES` aqui quer dizer uma coisa precisa:** a capacidade não precisa mais do
actor, está provada ao vivo pela API oficial, e não cai para rota paga. **Não
quer dizer que o actor já saiu do código** — secção D diz onde ele ainda está.

---

# W · READY_FOR_NEXT_SCRAP_MISSION

```
YES
```

A missão seguinte tem o alvo escrito e medido: **migrar os três chamadores de
runtime** em `comunicacao_coleta.py:267` e `sensor_coleta.py:568, 699, 894` para
a rota canônica, e só então retirar o identificador do actor da config. Aí, e
só aí, `US$ 12,2000` deixa de ser *elegível a evitar* e passa a ser evitado.

# X · KNOW_HOW_DELTA

```
KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA
```

A fronteira canônica do SCRAP no know-how descreve executor, router, adapters e
providers — e não distingue **`rota`** de **`executa`**, os dois papéis que uma
capacidade pode ter no registo, nem diz que capacidade com rota atravessa os
portões e capacidade sem rota monta o próprio trace. Uma linha resolve, e ela
pertence ao documento do know-how, não a um segundo.

---

```
PAREI AQUI. NENHUM ACTOR DESLIGADO. COLLECTION NÃO ENCANADA. GPU NÃO HABILITADA.
TRADUÇÃO NÃO INSTALADA. NENHUM MERGE EM MAIN.
```
