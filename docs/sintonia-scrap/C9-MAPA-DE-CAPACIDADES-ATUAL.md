# C9 · MAPA DE CAPACIDADES ATUAL — o censo datado

```
CENSO_DATADO_EM   = 2026-09-11
HEAD_MEDIDO       = e63c4682f918027896a0bfdf084b67fee93a8c87
C9_CAPABILITY_CENSUS = PASS
```

> **ISTO É UMA FOTOGRAFIA, NÃO UMA LEI.**
> Não é Bíblia, não é contrato, não é MASTER/FINAL concorrente. É o que foi
> medido em 2026-09-11 e nada além disso. Quem ler isto em 2027 está a ler
> história, exatamente como esta missão leu o `BENCHMARK-V1-FINAL.md`.

---

## A · GIT

| campo | medido |
|---|---|
| `CURRENT_BRANCH` | `claude/sintonia-scrap-capability-census-c9` |
| `INITIAL_HEAD` | `e63c4682f918027896a0bfdf084b67fee93a8c87` |
| `origin/claude/sintonia-scrap-convergence-c8` | `e63c4682f918027896a0bfdf084b67fee93a8c87` — **intacta** |
| `origin/claude/sintonia-eame-know-how-v1` | `7f08b004fb6c2fee7e0b92b311f76d9d12ad5c70` — igual ao observado pelo coordenador |
| `origin/main` | `df165da928549d9e3427b4c518bd8d70e7fb9058` |
| `WORKTREE_STATUS` | limpo (0 linhas) antes desta entrega |

A C8 estava intacta. A branch da C9 nasceu dela, sem force push, sem merge
automático, sem cherry-pick.

---

## B · CENSO ESTÁTICO — O SOFTWARE, ANTES DE QUALQUER REDE

Medido por **import real + leitura do `_MAPA` do registo**, não por nome de
ficheiro. Um adaptador que existe e não liga rota nenhuma conta como o que é.

```
ADAPTADORES            6 ficheiros
PLATAFORMAS            8   (o `adaptador_aberto` serve três)
DECLARED_CAPABILITIES  35
WIRED_CAPABILITIES     13   ← têm `executa` OU `rota`
UNWIRED_CAPABILITIES   22   ← declaradas, registadas, SEM caminho
DEAD_OR_RETIRED_ROUTES 0    ← nenhuma rota morta no SCRAP
ASR_OWNERS             1
```

### DECLARED vs WIRED, por plataforma

| plataforma | declaradas | com caminho | sem caminho | adaptador |
|---|---:|---:|---:|---|
| BLUESKY | 2 | 2 | 0 | `adaptador_aberto` |
| MASTODON | 2 | 2 | 0 | `adaptador_aberto` |
| TELEGRAM | 1 | 1 | 0 | `adaptador_aberto` |
| YOUTUBE | 7 | 5 | 2 | `adaptador_youtube` |
| INSTAGRAM | 7 | 3 | 4 | `adaptador_instagram` |
| **LINKEDIN** | **7** | **0** | **7** | `adaptador_linkedin` |
| **X** | **5** | **0** | **5** | `adaptador_x` |
| **FACEBOOK** | **4** | **0** | **4** | `adaptador_facebook` |

### O ZERO DO LINKEDIN, DO X E DO FACEBOOK NÃO É ESQUECIMENTO

Foi a primeira coisa que este censo quis medir, e a resposta muda todo o
ranking: **as 16 capacidades sem caminho dessas três plataformas estão sem
caminho de propósito**, e o próprio código diz porquê. `adaptador_x.py`:

> *«ligar a rota agora seria transformar um teste em producao, que e exatamente
> o que esta missao proibe.»*

`adaptador_linkedin.py`:

> *«Sete capacidades medidas, nenhuma com rota ligada nesta missao. Declarar sem
> executar e honesto; executar sem declarar e que nao e.»*

```
UNWIRED != FALTA DE ENGENHARIA.
```

Nessas três plataformas o degrau que falta é **autorização**, não código.
Ligar a rota é uma decisão de quem coordena; escrever a função é a parte fácil
e não é a parte que está em falta. Um ranking que leia «0 de 7» como «7 tarefas
de engenharia à espera» escolhe o gap errado — e era exatamente onde este
censo ia parar antes de ler os adaptadores.

### Os 10 fornecedores conhecidos, e quem paga

`coleta/scrap_fornecedores.py` conhece dez nomes. **Um** custa dinheiro:

```
PAGOS = (APIFY,)
```

E `ZERO_APIFY != ZERO_PAID_PROVIDER`: a rota oficial do X é paga por recurso
lido e não passa pela Apify. São duas contas diferentes.

### A divergência de tabela que este censo encontrou

`coleta/comunicacao_coleta.py:86` mantém a tabela de atores pagos:

| plataforma | ator | marca no código |
|---|---|---|
| INSTAGRAM | `apify~instagram-scraper` | `NAO_VERIFICADO` |
| FACEBOOK | `apify~facebook-posts-scraper` | `NAO_VERIFICADO` |
| LINKEDIN | `harvestapi~linkedin-post-search` | `JA_RODOU_NESTA_CASA` |

O YouTube saiu dessa tabela na C3 e passou a pedir **capacidade** ao SCRAP
(`CAPACIDADES_SCRAP`, linha 103). As outras três não saíram.

E há um desencontro medido: `leis/social_matriz.py` declara
`apify:harvestapi~linkedin-*` como `PERMITIDA = NAO · ROUTE_NOT_ALLOWED`,
enquanto `ATORES` continua a nomeá-lo como a rota do LinkedIn, alcançável em
`comunicacao_coleta.py:524` → `ap.executar_com_pool`. **Dois donos, duas
respostas.** Esta missão mede e regista; não corrige — corrigir código
operacional para «mostrar trabalho» é o que a §23 proíbe.

### ASR_OWNERS = 1, medido pela AST

Não por nome de ficheiro nem por `grep` de texto — a casa já foi mordida por
sentinelas ancoradas em texto. Quem **instancia** o motor:

```
ferramentas/fala_local.py:608   WhisperModel
ferramentas/fala_local.py:626   WhisperModel
ferramentas/fala_local.py:628   BatchedInferencePipeline
──────────────────────────────────────────────────────
ASR_OWNERS = 1 ficheiro
```

---

## C · LIVE PROBES EXECUTADOS

Sete sondas, todas mínimas, **US$ 0,00 gastos**, `APIFY_RUNS = 0`, nenhum
corpus criado, nenhum objeto admitido, nenhuma relevância julgada.

| # | sonda | rota | resultado |
|---|---|---|---|
| 1 | `robots.txt` × 5 plataformas | `DIRECT_HTTP` | 5 × HTTP 200 |
| 2 | Instagram `yt-dlp -J --skip-download` × 1 Reel preservado | a rota que a cadeia já corre | HTTP OK, 6 formatos |
| 3 | Instagram `-f bestaudio --skip-download --print` × 1 | idem | resolve para faixa **audio-only** |
| 4 | YouTube `oembed` × 1 vídeo | `PUBLIC_NATIVE`, `PERMITIDA=CONDICIONAL` | HTTP 200 |
| 5 | LinkedIn descoberta-indireta × 3 sites de organização | `DIRECT_HTTP`, `PERMITIDA=SIM` | 1 acerto, 2 × HTTP 403 do site |
| 6 | sondas `pronto()` do YouTube × 5 | grátis, lê configuração | `CREDENTIAL_MISSING` × 5 |
| 7 | `ffprobe` sobre os 8 Reels preservados | disco, zero rede | 8/8 lidos |

**O que NÃO foi sondado, e porquê.** Facebook, X, e todo o conteúdo do
LinkedIn: `social_matriz` declara que não existe rota permitida para eles.
Sondar seria a missão a passar por cima da política da casa para produzir um
número. O estado desses é `NOT_RUN`, com motivo nomeado — nunca `BLOCKED` por
comodidade.

```
NOT_RUN != UNKNOWN != BLOCKED.
```

### A credencial, e o que ela não prova

`YOUTUBE_DATA_API_KEY` existe como secret no GitHub e **continua intocada**:
não foi criada, não foi impressa, não foi registada em artefato, não entrou em
RAW. Neste contentor ela não está presente — as cinco sondas gratuitas do
YouTube devolvem `CREDENTIAL_MISSING`.

```
CREDENCIAL AUSENTE NESTE AMBIENTE  !=  PLATAFORMA INCAPAZ.
```

E, mesmo presente, a chave não provaria áudio:

```
YOUTUBE_DATA_API != CAPTION_DOWNLOAD != AUDIO_BYTES != ASR.
```

---

## D · POLÍTICA MEDIDA HOJE — `robots.txt`, grupo `User-agent: *`

Medido em 2026-09-11. É facto sobre um ficheiro, **não é parecer jurídico**.

| plataforma | grupo `*` | leitura |
|---|---|---|
| FACEBOOK | `Disallow: /` | tudo fechado para nós |
| INSTAGRAM | `Disallow: /` | tudo fechado para nós |
| LINKEDIN | `Disallow: /` | tudo fechado para nós |
| X | `Disallow: /` + `Disallow: /i/u` + `Crawl-delay: 1` | tudo fechado para nós |
| YOUTUBE | **lista de caminhos**, não `/` | `/results`, `/feeds/videos.xml`, `/youtubei/`, `/api/`, `/get_video*` fechados; `/watch` e `/oembed` **não** estão na lista |

Quatro das cinco fecham tudo ao nosso agente. O YouTube é a única com
superfície aberta — e é exatamente a única onde a casa já tem rota oficial
ligada. Isto confirma, três dias depois, o que `social_matriz` mediu em
2026-09-08: `UNCHANGED`.

**Uma observação que fica em aberto, de propósito.** Facebook e Instagram
publicam `Sitemap:` no mesmo grupo `*` — incluindo
`profiles_2500_followers.xml.gz`, `profiles_150_followers.xml.gz` e
`ig_seo_profile_sitemap.xml.gz`. Um `Sitemap:` é registo não-agrupado, o que
levanta uma pergunta real sobre descoberta de **identidade**. Esta missão
**não** a foi buscar: seria crawl, e seria uma decisão de política que não me
cabe. Fica registada como o que é — `UNKNOWN`, com o que falta medir escrito.

---

## E · A MATRIZ, CAPACIDADE A CAPACIDADE

Legenda das três colunas que a §7 manda separar:

```
MODULE   existe ficheiro/função         MODULE_EXISTS
EDGE     existe caminho registado       EDGE_EXISTS   (`executa` ou `rota`)
FLOW     bytes atravessaram             FLOW_OBSERVED
```

`DECLARADO` é o estado que `scrap_capacidades.py` carrega, com prova citada.
`C9` é o que **esta** missão mediu em 2026-09-11.

### D.1 · INSTAGRAM

| capacidade | MODULE | EDGE | FLOW | fornecedor | auth | custo | política | audio-only | DECLARADO | C9 | prova / primeiro ponto de quebra |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `instagram.reel.capture` | ✔ | ✔ `executa` | ✔ 8 itens | `yt-dlp` | nenhuma | `ZERO` | `DISALLOW_ALL` | — | PROVEN | **PROVEN** | 8 MP4 em `data/raw/REEL-MIDIA`, lidos por `ffprobe` |
| `instagram.reel.audio` | ✔ | ✔ `executa` | ✔ 8 itens | `ffmpeg` | nenhuma | `ZERO` | n/a (local) | **NÃO** | PROVEN | **PROVEN como DERIVAÇÃO** | `fala_local.py:948` — `ffmpeg -i <mp4> -vn` |
| `instagram.reel.transcribe` | ✔ | ✔ `executa` | ✔ 8 itens | `faster-whisper` | nenhuma | `ZERO` | n/a (local) | — | PROVEN | **PROVEN** | `ASR_OWNERS = 1` |
| `instagram.profile.discovery` | ✔ | ✘ | ✘ | — | — | `ZERO` | `DISALLOW_ALL` | — | PARTIAL | `NOT_RUN` | quebra medida antes: 302/429, janela esgota em ~8-10 respostas |
| `instagram.post.comments` | ✔ | ✘ | ✘ | Apify | — | `FORMULA_KNOWN` | `DISALLOW_ALL` | — | BLOCKED | `NOT_RUN` | nenhuma rota anónima provada |
| `instagram.story.capture` | ✔ | ✘ | ✘ | — | sessão | `UNKNOWN` | `DISALLOW_ALL` | — | UNKNOWN | `NOT_RUN` | falta: sessão autorizada; código vive noutra linhagem |
| `instagram.story.transcribe` | ✔ | ✘ | ✘ | — | — | `UNKNOWN` | n/a | — | NOT_EXECUTED | `NOT_RUN` | falta a captura primeiro |

**§12 respondida, e a resposta é a que a lei da C8 temia.**

| pergunta da §12 | medido em 2026-09-11 |
|---|---|
| uma URL direta continua resolvendo? | **SIM** — `yt-dlp -J` devolveu 6 formatos |
| existe stream de áudio separado? | **SIM** — `dash-…a`, `vcodec=none`, `acodec=mp4a.40.5`, `abr=75,941 kbps` |
| conseguimos pedir SOMENTE áudio? | **SIM** — `-f bestaudio` resolve para `m4a`, `vcodec=none` |
| o sistema pede só áudio? | **NÃO** |

`reel_transcricao.py:432` chama `_ytdlp(['-o', modelo_saida, url])` — **sem
seletor de formato**. O `yt-dlp` escolhe então o melhor vídeo + o melhor áudio:

```
dash-…v  2218,712 kbps   +   dash-…a  75,941 kbps   =   2294,653 kbps
```

e depois `fala_local.py:948` faz `ffmpeg -i <mp4> -vn`. Pela definição da §12,
isto tem nome e não é «audio-only»:

```
INSTAGRAM_AUDIO_ONLY_ACQUISITION = ABSENT
O QUE EXISTE                     = VIDEO_ACQUISITION + AUDIO_DERIVATION
```

**Quanto custa a diferença — dois números, duas bases, nenhum escolhido por
conveniência:**

| base | medida | razão |
|---|---:|---|
| os 8 Reels **como foram colhidos** (`ffprobe` sobre o disco) | 37 683 455 B de MP4 para 3 952 028 B de áudio | **9,5×** |
| 1 Reel **remedido hoje**, contra a melhor rendição de hoje | 2294,653 kbps para 75,941 kbps | **30,2×** |

Os dois são verdade e medem coisas diferentes: o primeiro é o que já se gastou,
o segundo é o que se gastaria agora. Nenhum dos dois é «7,58×», o número que o
benchmark histórico trazia — esse foi medido noutra amostra e não se reescreve.

### D.2 · FACEBOOK

| capacidade | MODULE | EDGE | FLOW | fornecedor | auth | custo | política | DECLARADO | C9 | primeiro ponto de quebra |
|---|---|---|---|---|---|---|---|---|---|---|
| `facebook.identity.discovery` | ✔ | ✘ | ✘ | `gallery-dl` | nenhuma | `ZERO` | `DISALLOW_ALL` | PARTIAL | `NOT_RUN` | rota não permitida; o que saía era id da Page, fbid, álbuns, URL canónica |
| `facebook.content` | ✔ | ✘ | ✘ | Graph | App Review | `ZERO` dentro da quota | `DISALLOW_ALL` | BLOCKED | `NOT_RUN` | **302 login** no HTTP; na rota oficial, `CREDENTIAL_MISSING` depois de App Review |
| `facebook.media` | ✔ | ✘ | ✘ | Graph | App Review | idem | `DISALLOW_ALL` | BLOCKED | `NOT_RUN` | 302/400 deste IP |
| `facebook.metrics` | ✔ | ✘ | ✘ | Graph | App Review | idem | `DISALLOW_ALL` | BLOCKED | `NOT_RUN` | sem conteúdo não há métrica |

O Facebook é a única das cinco onde **a identidade sai e o conteúdo não sai
nenhum**. Colapsar isso em «Facebook = BLOCKED» seria mais curto e menos
verdadeiro — apagaria o único sítio por onde a plataforma ainda responde.

`FACEBOOK_AUDIO_ONLY = BLOCKED` (não há de onde: sem conteúdo, não há mídia).

### D.3 · LINKEDIN

| capacidade | MODULE | EDGE | FLOW | fornecedor | auth | custo | política | DECLARADO | C9 | primeiro ponto de quebra |
|---|---|---|---|---|---|---|---|---|---|---|
| `linkedin.recent.discovery` | ✔ | ✘ | ✘ | HTTP próprio | nenhuma | `ZERO` | `DISALLOW_ALL` | PROVEN | `NOT_RUN` | rota não permitida; 11/13/10 activity ids medidos antes, sem página seguinte |
| `linkedin.history.discovery` | ✔ | ✘ | ✘ | — | — | `UNKNOWN` | `DISALLOW_ALL` | UNKNOWN | `NOT_RUN` | falta: «Show more» não expõe URL de página seguinte |
| `linkedin.direct_post` | ✔ | ✘ | ✘ | HTTP próprio | nenhuma | `ZERO` | `DISALLOW_ALL` | PROVEN | `NOT_RUN` | rota não permitida |
| `linkedin.native_video` | ✔ | ✘ | ✘ | HTTP próprio | nenhuma | `ZERO` | `DISALLOW_ALL` | PROVEN | `NOT_RUN` | rota não permitida |
| `linkedin.native_caption` | ✔ | ✘ | ✘ | HTTP próprio | nenhuma | `ZERO` | `DISALLOW_ALL` | PROVEN | `NOT_RUN` | rota não permitida |
| `linkedin.comments` | ✔ | ✘ | ✘ | — | — | `UNKNOWN` | `DISALLOW_ALL` | UNKNOWN | `NOT_RUN` | nunca tentado |
| `linkedin.documents` | ✔ | ✘ | ✘ | — | — | `UNKNOWN` | `DISALLOW_ALL` | NOT_EXECUTED | `NOT_RUN` | nunca tentado |

**A única rota do LinkedIn que a matriz permite foi sondada, e saiu do
`POSSIBLE_NOT_PROVED`.** `descoberta-indireta:site-da-organizacao`
(`DIRECT_HTTP`, `PERMITIDA = SIM`) — buscar no site **da própria organização** o
endereço do LinkedIn dela:

```
imagelinenetwork.com   HTTP 200   →   linkedin.com/company/image-line     ACERTO
adama.com/italia       HTTP 403   →   «Access Denied» do WAF do site
adama.com/spain        HTTP 403   →   «Access Denied» do WAF do site
```

```
LINKEDIN_DISCOVERY_INDIRECT = PARTIAL   (1 de 3 sites, 2026-09-11)
```

E os dois 403 são do **site da organização** a recusar este IP de datacenter —
não são do LinkedIn e não são da rota. Falha do ambiente não é incapacidade da
plataforma.

E um limite que importa não esquecer: isto devolve a **identidade** (o handle),
não as publicações.

```
UMA URL DIRETA != DISCOVERY.   IDENTIDADE != CONTEÚDO.
```

`LINKEDIN_AUDIO_ONLY = NOT_NEEDED` — a legenda SRT automática existe servida ao
lado do vídeo, e `CAPTION_FIRST` resolve sem ASR. Mas é legenda de máquina:
*mais barata, não melhor.*

### D.4 · YOUTUBE

| capacidade | MODULE | EDGE | FLOW | fornecedor | auth | custo | política | DECLARADO | C9 | primeiro ponto de quebra |
|---|---|---|---|---|---|---|---|---|---|---|
| `youtube.search` | ✔ | ✔ `rota` | ✘ aqui | API oficial | chave | `FORMULA_KNOWN` 1 un., bucket de 100/dia | `PERMITIDA` | PROVEN | `NOT_RUN` | `CREDENTIAL_MISSING` neste contentor |
| `youtube.channel.discovery` | ✔ | ✔ `rota` | ✘ aqui | API oficial | chave | `FORMULA_KNOWN` 1 un. | `PERMITIDA` | PROVEN | `NOT_RUN` | idem |
| `youtube.video.metadata` | ✔ | ✔ `rota` | ✘ aqui | API oficial | chave | `FORMULA_KNOWN` 1 un. | `PERMITIDA` | PROVEN | **PARTIAL por `oembed`** | `oembed` HTTP 200: título + autor + thumbnail; **sem** data, métricas ou descrição |
| `youtube.comments` | ✔ | ✔ `rota` | ✘ aqui | API oficial | chave | `FORMULA_KNOWN` 1 un./página | `PERMITIDA` | PROVEN | `NOT_RUN` | `CREDENTIAL_MISSING` |
| `youtube.channel.resolve` | ✔ | ✔ `executa` | ✘ aqui | API oficial | chave | `FORMULA_KNOWN` | `PERMITIDA` | PARTIAL | `NOT_RUN` | `CREDENTIAL_MISSING` |
| `youtube.native_caption` | ✔ | **✘** | ✘ | — | OAuth / dono | `FORMULA_KNOWN` 50–200 un. | `NAO` em todas as livres | PROVEN | **`BLOCKED_NEEDS_AUTHORIZATION`** | C5: `captions.download` exige ser dono; `captions.list` exige OAuth e não traz texto; `timedtext` em `Disallow: /api/` |
| `youtube.media` | ✔ | **✘** | ✘ | — | — | `ZERO` | `NAO` | BLOCKED | **BLOCKED** | 403 de IP de datacenter **e** `ROUTE_NOT_ALLOWED` |

**Uma contradição entre donos, encontrada e registada.**
`scrap_capacidades.py` carrega `youtube.native_caption = PROVEN`; a matriz de
rotas declara **todas** as rotas livres de legenda como `PERMITIDA = NAO`, e a
C5 já tinha fechado o portão com `TRANSCRIPT_ROUTE_GATE = CLOSED ·
D · BLOCKED_NEEDS_AUTHORIZATION`. As duas leituras são compatíveis se se
disser a frase inteira, e a frase inteira é:

```
TECNICAMENTE PROVADO  !=  ROTA PERMITIDA.
```

O estado `PROVEN` daquela linha descreve uma medição de 2026-09-08 por uma rota
que a casa entretanto declarou fora. Não o reescrevo aqui — o dono daquela
declaração é `scrap_capacidades.py`, e mudá-lo é missão dele, não deste censo.

```
YOUTUBE_AUDIO_ONLY = BLOCKED   ·   motivo: ROUTE_NOT_ALLOWED + 403 técnico
```

E não se disfarça: baixar o vídeo inteiro para obter o áudio continua proibido,
e é duplamente inútil aqui, porque os bytes de mídia levam 403 na mesma.

### D.5 · X / TWITTER

| capacidade | MODULE | EDGE | FLOW | fornecedor | auth | custo | política | DECLARADO | C9 | primeiro ponto de quebra |
|---|---|---|---|---|---|---|---|---|---|---|
| `x.direct_post` | ✔ | ✘ | ✘ | `gallery-dl` | nenhuma | `ZERO` | `DISALLOW_ALL` | PROVEN | `NOT_RUN` | rota não permitida |
| `x.media` | ✔ | ✘ | ✘ | `gallery-dl` | nenhuma | `ZERO` | `DISALLOW_ALL` | PROVEN | `NOT_RUN` | rota não permitida |
| `x.metrics` | ✔ | ✘ | ✘ | `gallery-dl` | nenhuma | `ZERO` | `DISALLOW_ALL` | PROVEN | `NOT_RUN` | rota não permitida |
| `x.native_caption` | ✔ | ✘ | ✘ | `gallery-dl` | nenhuma | `ZERO` | `DISALLOW_ALL` | PARTIAL | `NOT_RUN` | existia e veio VAZIA: «could not transcribe the audio» |
| `x.discovery` | ✔ | ✘ | ✘ | API oficial paga | chave paga | `FORMULA_KNOWN` US$ 0,005/post | `PERMITIDA=SIM` | UNKNOWN | **`UNKNOWN` — continua** | `CREDENTIAL_MISSING`; nenhuma listagem de cronologia jamais tentada |

`X_AUDIO_ONLY = NOT_RUN` — a legenda nativa existiria primeiro, e nem a legenda
tem rota permitida.

A pergunta de valor da §15 tem resposta: **sim, `x.discovery` continua
`UNKNOWN`.** E continua pelo motivo mais caro de todos — a única rota permitida
é a API oficial paga, e não há credencial.

---

## F · MATRIZ AUDIO-ONLY

A lei da C8 — `TRANSCRIPTION NEED != VIDEO DOWNLOAD` — medida contra o código
que existe hoje:

| plataforma | precisa de ASR? | legenda nativa? | stream de áudio separado? | **pede só áudio?** | veredito |
|---|---|---|---|---|---|
| INSTAGRAM | **SIM, indispensável** | não existe | **SIM**, medido hoje | **NÃO** | `VIDEO_ACQUISITION + AUDIO_DERIVATION` |
| LINKEDIN | não, se a legenda servir | SIM (SRT de máquina) | `UNKNOWN` | n/a | `NOT_NEEDED` · rota não permitida |
| YOUTUBE | sim, sem legenda | sim, mas sem rota permitida | `UNKNOWN` | `NÃO` | **`BLOCKED`** |
| X | sim | existe e veio vazia | `UNKNOWN` | `NÃO` | `NOT_RUN` |
| FACEBOOK | sim | `UNKNOWN` | `UNKNOWN` | `NÃO` | **`BLOCKED`** |

```
IMPLEMENTAÇÕES DA LEI AUDIO-ONLY NO SISTEMA HOJE = 0
```

A C8 escreveu a lei. **Nenhuma plataforma a cumpre.** E na única onde ela é
cumprível hoje — Instagram, rota já em produção, stream separado confirmado,
seletor a uma bandeira de distância — ela não está cumprida.

---

## G · MATRIZ DE ROTA OFICIAL · FORNECEDOR · CUSTO · AUTH

| plataforma | rota oficial existe? | permitida? | credencial aqui | fornecedor em uso | `COST_STATE` | auth |
|---|---|---|---|---|---|---|
| YOUTUBE | **SIM** — Data API v3 | **SIM** | ausente | API oficial | `FORMULA_KNOWN` 1 un./chamada; 100 buscas + 10 000 un./dia | chave |
| INSTAGRAM | sim — Graph `business_discovery` | condicional | ausente | `yt-dlp` (Reels) · Apify (tabela `ATORES`) | `ZERO` na cadeia de Reels · `FORMULA_KNOWN` US$ 1,863/1 000 na Apify | nenhuma / App |
| FACEBOOK | sim — Graph | condicional | ausente | nenhum a correr | `ZERO` dentro da quota, **depois de App Review** | App Review |
| LINKEDIN | sim — Community Management API | **NÃO** | ausente | nenhum a correr | US$ 4,03/1 000 medido no `harvestapi` | programa de parceiro |
| X | sim — API oficial | **SIM** | ausente | nenhum a correr | `FORMULA_KNOWN` US$ 0,005/post lido | chave paga |

**Custo desta missão:**

```
COST_USD      = 0,00
APIFY_RUNS    = 0
PAID_PROVIDER = nenhum
COST_STATE    = ZERO (medido, não estimado)
```

`CAN COST != DID COST`. Nenhum dólar foi inventado e nenhum foi gasto.

---

## H · DECLARED vs WIRED vs OBSERVED

```
DECLARED   35   o que scrap_capacidades.py declara, com prova citada
WIRED      13   o que tem `executa` ou `rota` no registo
OBSERVED    3   o que deixou bytes no disco desta casa
```

As três observadas são a cadeia de Reel do Instagram — `capture`, `audio`,
`transcribe` — com 8 MP4 e 8 WAV em `data/raw/REEL-MIDIA`, lidos por `ffprobe`
nesta missão. O corpus é histórico: prova que a cadeia correu **nesta casa**,
não que correu **neste HEAD**.

```
FLOW_OBSERVED = SIM (corpus histórico)   ·   FLOW_ON_THIS_HEAD = NOT_RUN
```

As cinco do YouTube têm `rota` e não deixaram artefato de fornecedor neste
checkout. Isso **não** é um achado sobre o YouTube: `data/raw/*` está no
`.gitignore` e nenhuma corrida de SCRAP aconteceu neste contentor. O caminho de
persistência existe e está ligado — `scrap_executor.py:271-276` sela o trace,
`comunicacao_coleta.py:477` e `sensor_coleta.py:499` escrevem
`COLLECTION_PROVIDER`.

Registo isto em claro porque foi o item 17 do red team a apanhar-me a mim:
durante meia hora este censo teve um «gap de observabilidade» na lista de
candidatos, construído sobre um `grep` que não achou nada num checkout vazio.
**Falha do ambiente não é incapacidade do sistema.**

---

## I · DELTA CONTRA O BENCHMARK HISTÓRICO

O `BENCHMARK-V1-FINAL.md` **não foi reescrito**. É fotografia, e continua a
sê-lo.

| item | benchmark histórico | C9, 2026-09-11 | classificação |
|---|---|---|---|
| Instagram · reels | PROVEN | PROVEN | `UNCHANGED` |
| Instagram · mídia com áudio separado | PROVEN, «áudio m4a 85 kbps» | **PROVEN, `abr = 75,941 kbps`** medido hoje | `UNCHANGED` no facto, número diferente |
| Instagram · transcript | PROVEN | PROVEN | `UNCHANGED` |
| Instagram · **aquisição audio-only** | não era eixo do benchmark | `ABSENT` | `NOT_COMPARABLE` — eixo novo, criado pela C8 |
| Instagram · discovery | PARTIAL | `NOT_RUN` (rota não permitida) | `NOT_COMPARABLE` |
| Facebook · identidade | PARTIAL | `NOT_RUN` | `NOT_COMPARABLE` |
| Facebook · conteúdo/mídia/métricas | BLOCKED | BLOCKED | `UNCHANGED` |
| LinkedIn · discovery recente | PROVEN | `NOT_RUN` — rota declarada não permitida | **`REGRESSED` em autorização, não em técnica** |
| LinkedIn · descoberta indireta | não era eixo | **PARTIAL, 1/3** | `IMPROVED` — saiu de `POSSIBLE_NOT_PROVED` |
| LinkedIn · vídeo e legenda nativa | PROVEN | `NOT_RUN` | `REGRESSED` em autorização |
| YouTube · busca, metadados, comentários | PROVEN por `yt-dlp` | rota oficial ligada, `CREDENTIAL_MISSING` aqui | **`IMPROVED`** — C2/C3 trocaram rota paga/proibida por oficial |
| YouTube · `oembed` | não era eixo | PROVEN, HTTP 200 | `NOT_COMPARABLE` |
| YouTube · legenda | PROVEN por `yt-dlp` | **`BLOCKED_NEEDS_AUTHORIZATION`** (C5) | **`OLD_CLAIM_INVALID`** — a prova vinha de rota que a casa declarou fora |
| YouTube · bytes de mídia | BLOCKED (403) | BLOCKED (403 **+** `ROUTE_NOT_ALLOWED`) | `UNCHANGED`, com motivo a mais |
| X · post, mídia, métricas | PROVEN por `gallery-dl` | `NOT_RUN` | `REGRESSED` em autorização |
| X · discovery | UNKNOWN | UNKNOWN | `UNCHANGED` |
| ASR local | PROVEN, 3 PASS + IT PARTIAL | PROVEN, `ASR_OWNERS = 1`, GPU provada na C4B | **`IMPROVED`** |

### O que a C1–C8 realmente mudou, dito de uma vez

**Não aumentaram a superfície coletada. Aumentaram a superfície *honesta*.**

O que ganhou: o YouTube saiu da rota paga para a oficial; o ASR ganhou dono
único e prova de dispositivo; a espécie do texto e o lugar do facto ganharam
lei; a legenda deixou de se confundir com transcrição.

O que «piorou» só piorou no papel: cinco capacidades que o benchmark dava como
PROVEN estão hoje `NOT_RUN` porque a casa mediu o `robots.txt` e declarou a
rota fora. **A capacidade técnica não desapareceu — a autorização é que nunca
tinha sido perguntada.** Descobrir que se estava a andar sem licença não é
perder o carro.

---

## J · RANKING DOS GAPS

Escala 0–5. `G`, `H` e `J` estão invertidos de propósito: pontuação alta
significa **menos** esforço, **menos** risco, **menos** dependências.

| # | gap | A valor | B freq. | C EAME | D custo | E fragil. | F rota barata | G esforço⁻¹ | H risco⁻¹ | I reuso | J dep.⁻¹ | **total** |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **1** | **Instagram · aquisição audio-only** | 3 | 5 | 4 | 3 | 3 | 5 | 5 | 5 | 4 | 4 | **41** |
| 2 | LinkedIn · autorização + ligar rota | 5 | 3 | 5 | 4 | 4 | 1 | 3 | 0 | 2 | 1 | 28 |
| 3 | YouTube · legenda de canal de terceiro | 5 | 4 | 5 | 4 | 3 | 0 | 2 | 0 | 2 | 1 | 26 |
| 4 | X · discovery | 4 | 2 | 3 | 2 | 2 | 1 | 2 | 1 | 1 | 1 | 19 |
| 5 | Facebook · conteúdo por Graph | 4 | 2 | 4 | 2 | 1 | 1 | 1 | 1 | 1 | 0 | 17 |

Fora da lista, e porquê: a divergência `ATORES` × `social_matriz` no LinkedIn é
**defeito de coerência**, não gap de capacidade — entra como risco (§X), não
como candidato. E o «gap de observabilidade» foi retirado depois de medido:
não existia.

---

## K · O GAP ESCOLHIDO

```
GAP_VENCEDOR = INSTAGRAM · AQUISIÇÃO AUDIO-ONLY
```

### Por que ele ganhou

1. **É a única lei da casa com zero implementações.** A C8 fechou
   `TRANSCRIPTION NEED != VIDEO DOWNLOAD` e nenhuma plataforma a cumpre. Uma lei
   sem uma única implementação é uma lei a caminho de ser esquecida.
2. **É na única plataforma onde o ASR é indispensável.** O Instagram não serve
   legenda nativa. Não há `CAPTION_FIRST` possível — o áudio é o caminho, e o
   caminho está a puxar o vídeo inteiro atrás de si.
3. **A rota já é nossa e já está em produção.** Nada de novo a autorizar, nada
   de novo a pagar, nenhum fornecedor novo. O seletor `-f bestaudio` foi
   provado hoje contra um Reel real.
4. **A economia está medida, não estimada.** 9,5× sobre o corpus real; 30,2×
   sobre a melhor rendição de hoje.
5. **Reduz a exposição em vez de a aumentar.** É a única entrada do ranking que
   faz a casa pedir **menos** à plataforma. Todas as outras pedem mais.
6. **É pequeno.** O trabalho não é o seletor — é a consequência dele, e a
   consequência cabe numa missão só.

### O que ele NÃO é, para ninguém se enganar

Não é ganho de inteligência: o transcript que sai no fim é o mesmo. É ganho de
**custo, velocidade, superfície e coerência com a própria lei**. Marcar o valor
de inteligência em 3, e não em 5, foi deliberado.

### Por que os outros não ganharam

| gap | o que realmente bloqueia |
|---|---|
| LinkedIn | **autorização, não engenharia.** `robots.txt` diz `Disallow: /` e o texto diz em claro que meio automatizado sem permissão expressa é proibido. As sete funções escrevem-se numa tarde; a permissão não. E o adaptador recusa-se a fingir o contrário — de propósito. |
| YouTube legenda | **a C5 já decidiu e o portão está fechado**: `D · BLOCKED_NEEDS_AUTHORIZATION`. Reabrir sem autorização nova seria refazer a C5 para chegar à mesma conclusão. |
| X discovery | a única rota permitida é a API oficial **paga**, sem credencial. Continuar `UNKNOWN` custa menos do que descobrir por uma porta que a casa não abriu. |
| Facebook | o muro mais alto e a dependência mais longa: App Review antes de qualquer medição. Maior esforço, menor certeza, zero controlo do calendário. |

### A regra da §20, aplicada ao vencedor

O gap vencedor mexe em fala e vídeo, portanto:

```
AUDIO-ONLY FIRST é requisito, não preferência.
VIDEO_DOWNLOAD COMO FALLBACK SILENCIOSO = PROIBIDO.
```

Se a missão seguinte não conseguir áudio separado num item, o estado honesto é
`BLOCKED` para esse item — **não** cair para o vídeo inteiro sem dizer.

---

## L · O QUE ESTA MISSÃO *NÃO* FEZ, E É PROPOSITADO

Não implementou o vencedor. Não tocou em nenhum ficheiro operacional. Não
corrigiu a divergência `ATORES` × `social_matriz`. Não corrigiu o
`youtube.native_caption = PROVEN` que a C5 já contradisse. Não regenerou o
System Map — a arquitetura não mudou. Não abriu a C10.

```
ESTA MISSÃO TERMINA AQUI.
```

---

## M · SCRAP × COLLECTION CANÔNICA

Nada foi admitido, nada foi julgado, nenhum RUN foi criado, nenhum RAW novo
nasceu. `COL-LAW-505` continua a valer e não foi tocada.

```
COLHEITA != MANIFEST != CATALOG != RUN_RECEIPT != PLAN != UNKNOWN
```

Nenhuma das sondas desta missão produziu COLHEITA. As sondas 2, 3 e 4 pediram
**metadados** e descartaram-nos; a sonda 5 leu HTML público de sites de
organizações e guardou um handle no relatório, não no acervo; a 7 leu bytes que
já estavam preservados. Só COLHEITA cruza o Ingresso, e não houve nenhuma.

---

## N · RED TEAM — as 17 tentativas de derrubar este censo

| # | ataque | resultado |
|---|---|---|
| 1 | código existe mas edge não existe | **apanhado 22 vezes** — é a coluna `EDGE` |
| 2 | edge existe mas nunca correu | **apanhado** — 13 `WIRED`, 3 `OBSERVED` |
| 3 | resultado histórico tratado como atual | **apanhado** — coluna `DECLARADO` separada de `C9` |
| 4 | fallback pago mascarado como zero custo | resistiu — `PAGOS = (APIFY,)` e o X é pago sem Apify |
| 5 | vídeo inteiro baixado para dizer `AUDIO_ONLY` | **apanhado** — é o gap vencedor |
| 6 | legenda automática tratada como transcript humano | resistiu — SRT do LinkedIn marcada como ASR de outra casa |
| 7 | secret tratado como capacidade | **apanhado** — `CREDENTIAL_MISSING` ≠ `BLOCKED`, e a chave não prova áudio |
| 8 | API de metadata tratada como acesso à mídia | **apanhado** — `oembed` PROVEN e `youtube.media` BLOCKED na mesma tabela |
| 9 | login ausente tratado como bloqueio permanente | resistiu — Stories ficam `UNKNOWN`, não `BLOCKED` |
| 10 | uma URL direta tratada como discovery | **apanhado** — a sonda 5 dá identidade, não conteúdo |
| 11 | discovery recente tratado como histórico | resistiu — `DEPTH = SHALLOW` preservado |
| 12 | provider externo tratado como owner | resistiu — `ADAPTER != PROVIDER != AMBIENTE` |
| 13 | Apify zero tratado como custo zero | resistiu — `ZERO_APIFY != ZERO_PAID_PROVIDER` |
| 14 | robots tratado como parecer jurídico | **apanhado no sitemap** — observação registada, não seguida |
| 15 | `UNKNOWN` transformado em `BLOCKED` | resistiu — `x.discovery` continua `UNKNOWN` |
| 16 | `NOT_RUN` transformado em `UNKNOWN` | resistiu — 16 capacidades marcadas `NOT_RUN` com motivo |
| 17 | falha do ambiente virada incapacidade da plataforma | **apanhou-me** — ver §H, e os dois 403 do WAF na sonda 5 |

---

## O · O QUE FICA DESCONHECIDO

| desconhecido | o que falta medir |
|---|---|
| profundidade histórica do LinkedIn | como o «Show more» pagina — e uma autorização para tentar |
| comentários do LinkedIn | nunca tentados |
| `x.discovery` | uma credencial da API oficial paga |
| Stories do Instagram | uma sessão autorizada |
| sitemaps de perfis do Facebook e Instagram | se um `Sitemap:` publicado num grupo `Disallow: /` é rota de identidade utilizável — **pergunta de política, não de técnica** |
| stream de áudio separado em LinkedIn, X e Facebook | só medível depois de rota permitida |
| `FLOW` da cadeia oficial do YouTube | uma corrida com credencial presente |

---

## P · RISCO RESTANTE

1. **`ATORES` × `social_matriz` divergem no LinkedIn.** Uma tabela operacional
   nomeia um ator que o dono da política declara `ROUTE_NOT_ALLOWED`, e o
   caminho até `ap.executar_com_pool` existe. Enquanto as duas discordarem, quem
   ler uma não sabe o que a outra decidiu.
2. **`youtube.native_caption = PROVEN` sobrevive ao portão que a C5 fechou.**
   Estado verdadeiro sobre uma rota que a casa já declarou fora.
3. **A cadeia de Reel do Instagram não atravessa o portão de rotas.** Ela usa
   `executa`, por desenho — e `executa` existe justamente para o que a matriz
   não conhece. O efeito colateral é que a única aquisição de mídia ligada do
   sistema é a única que nenhum portão mede.
4. **`LOCAL_HARDWARE_STATUS = 'NOT_MEASURED'`** em `scrap_capacidades.py`,
   depois de a C4B ter provado execução em GPU no runner real. Conservador, e
   por isso inofensivo — mas é declaração mais velha do que a medição.

---

## Q · VEREDITO

```
C9_CAPABILITY_CENSUS = PASS
GAP_VENCEDOR         = INSTAGRAM · AQUISIÇÃO AUDIO-ONLY
KNOW_HOW_DELTA       = NENHUM
BÍBLIA/CONTRATO      = NÃO precisa mudar
PRÓXIMO PASSO        = uma missão pequena e só dela

HARD STOP.
```
