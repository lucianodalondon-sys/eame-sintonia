# C4F · O CANÁRIO DE VÍDEO ITALIANO — três bloqueios medidos, e um conserto

> **A missão não passou, e não passou por três razões medidas.** Nenhuma delas é
> falta de rede, nenhuma é ausência de conteúdo, e nenhuma se conserta com uma
> linha de código.
>
> **O que ela entregou:** o bloqueio nomeado com precisão, e um campo que
> mentia — `EGRESSO = BLOCKED` escrito à mão — transformado em medição.

```
VALID_REAL_VIDEO_REACHED_WAITING_ROOM = NO
ACQUISITION      = ROUTE_NOT_ALLOWED           (e NÃO «rede bloqueada»)
WAITING_ROOM     = NOT_AVAILABLE_ON_THIS_HOST  (PostgreSQL não existe aqui)
VIDEO_CONSUMER   = NO                          (defeito herdado, e por exercitar)
```

---

# A · GIT

| campo | valor |
|---|---|
| `CURRENT_BRANCH` | `claude/local-gpu-on-current-collection-v1` |
| `CURRENT_HEAD` | `f5434f5e39615cb8be48e33f1e76320a7dd097f2` |
| `REMOTE_HEAD` | `f5434f5e…` — **igual** |
| `WORKTREE_CLEAN` | sim, no arranque |

A referência do coordenador bateu com a medição. Nenhuma divergência.

---

# B · A REDE FUNCIONA — E ISSO É METADE DO ACHADO

`§3` mandava medir a saída de internet antes de escolher vídeo. Medido:

```
DNS                 www.youtube.com -> 142.251.152.4 (+2)
HTTPS               example.com     -> HTTP 200 em 3,84 s
YOUTUBE             www.youtube.com -> HTTP 200
robots.txt de ambos os hospedeiros   -> lido, com resposta
```

```
PUBLIC_EGRESS               = OPEN
SOURCE_REACHABLE            = YES
BLOCKED_BY_NETWORK          = NO
```

**E é aqui que estava um defeito.** `provas/o_video_tem_consumidor.py` publicava:

```python
_mede("EGRESSO", "BLOCKED",
      "a politica desta sessao responde 403 CONNECT a todos os hospedeiros …")
```

Um **literal**, escrito à mão, verdadeiro sobre a sessão em que nasceu e falso
nesta máquina. E `VIDEO_TO_WAITING_ROOM` derivava dele:

```
VIDEO_TO_WAITING_ROOM = BLOCKED_BY_REAL_EXTERNAL_CONDITION
                        «sem bytes de video nesta arvore e sem egresso»
```

```
UM AMBIENTE ESCRITO À MÃO ENVELHECE NA PRIMEIRA MÁQUINA DIFERENTE.
UM CAMPO QUE DIZ «BLOCKED» SEM TENTAR NÃO É MEDIÇÃO: É LEMBRANÇA DE OUTRO SÍTIO.
```

E o preço não era cosmético: quem lesse o artefato ia **consertar a rede**, que
não está partida, em vez de olhar para o `robots.txt` e para a credencial
ausente — que é onde a estrada de facto para.

```
ATRIBUIR O BLOQUEIO AO SÍTIO ERRADO CUSTA A MISSÃO SEGUINTE INTEIRA.
```

Agora a prova **tenta**, e o veredito deriva do que ela obteve:

```
EGRESSO                    = OPEN      os 2 hospedeiros responderam
ALCANCE_WWW_YOUTUBE_COM    = ROBOTS_ALLOWS
ALCANCE_WWW_INSTAGRAM_COM  = ROBOTS_DISALLOWS
VIDEO_TO_WAITING_ROOM      = ROUTE_NOT_ALLOWED
```

### Uma correcção à minha própria regra, antes de a publicar

A primeira versão do detector aceitava qualquer capacidade com `VIDEO` no nome —
e apanhou `FETCH_VIDEO_METADATA`, que está **permitida** e traz um título e uma
duração. Com ela na lista, a prova publicava *«há rota permitida para adquirir
vídeo»* quando o que há é rota para saber o **nome** do vídeo.

```
METADADO DO VÍDEO != VÍDEO.
```

Apertado para `MEDIA`/`BYTES`, e ignorando a rota cujo único acto é carimbar a
ausência (`marcar:MEDIA_FETCH_UNAVAILABLE`, `NOT_APPLICABLE`).

---

# C · A FONTE ITALIANA EXISTE, E ESTÁ AUTORIZADA

`§4` mandava usar só fonte italiana já cadastrada. Ela existe:

`data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json`

| conta | plataforma | identidade | evidência |
|---|---|---|---|
| `BayerCropScienceIT` | YOUTUBE | **PROVED** | o site oficial italiano da Bayer declara o link |
| `Syngentaitaly` | YOUTUBE | **PROVED** | o site oficial italiano da Syngenta declara o link |
| `bayer_italia` | INSTAGRAM | **PROVED** | idem |
| `syngentaitalia` | INSTAGRAM | **PROVED** | idem |
| *BASF playlist* | YOUTUBE | `REJECTED` | «não é conta: é uma playlist» |
| `basf_global` | INSTAGRAM | PROVED, **mas é global** | `?hl=it` é idioma, não país |

```
AUTHORIZED_ITALIAN_VIDEO_SOURCE = YES
```

E `basf_global` **não** entra: `?hl=it` no endereço é a língua da interface, não
o país da conta. Inferir Itália daí seria o ataque 21 do red team a passar.

---

# D · BLOQUEIO 1 · NÃO HÁ ROTA PERMITIDA QUE ADQUIRA BYTES DE VÍDEO

Varrido o **matriz inteiro** de política de rota, todas as plataformas, à procura
de qualquer rota que traga mídia:

| plataforma | capacidade | rota | permitida | estado |
|---|---|---|---|---|
| YOUTUBE | FETCH_VIDEO_METADATA | `youtube-data-api-v3` | SIM | **CREDENTIAL_MISSING** |
| YOUTUBE | FETCH_VIDEO_METADATA | `youtube:oembed` | CONDICIONAL | PROVED |
| YOUTUBE | FETCH_VIDEO_METADATA | `yt-dlp:extract_info` | **NÃO** | BLOCKED |
| YOUTUBE | FETCH_TRANSCRIPT | `captions.download` | **NÃO** | REQUIRES_OWNER_PERMISSION |
| YOUTUBE | FETCH_TRANSCRIPT | `captions.list` | **NÃO** | REQUIRES_AUTHORIZATION |
| YOUTUBE | FETCH_TRANSCRIPT | `timedtext` | **NÃO** | ROUTE_NOT_ALLOWED |
| YOUTUBE | FETCH_TRANSCRIPT | `apify:transcricao` | CONDICIONAL | PARTIAL — **paga** |
| INSTAGRAM | FETCH_TRANSCRIPT | `instagram_transcrever.py` | **NÃO** | ROUTE_NOT_ALLOWED |
| TIKTOK | FETCH_VIDEO_BYTES | `marcar:MEDIA_FETCH_UNAVAILABLE` | SIM | NOT_APPLICABLE |

`FETCH_VIDEO_BYTES` aparece **uma vez em todo o sistema**, e o que ela faz é
carimbar que a mídia não está disponível.

E `youtube.media`, no registo de capacidades, está declarada **sem executor**:

```
youtube.media -> EXECUTA=None  ROTA=None
nota: «403 de IP de datacenter; so o runner local pode fechar esta medicao»
```

### Por que o IP local não resolve

O motivo da recusa do `yt-dlp` tem **duas** metades, e só uma é o IP:

```
"MEDIDO: «Sign in to confirm you are not a bot» deste IP de datacenter.
 Duplamente fora: bloqueada de facto E em caminho Disallow."
```

Re-medido **hoje, nesta máquina, contra o robots.txt vivo de cada hospedeiro**:

```
www.youtube.com/watch?v=…      PERMITE
www.youtube.com/youtubei/…     RECUSA     ← por onde a mídia é negociada
www.youtube.com/results?…      RECUSA
www.youtube.com/api/timedtext  RECUSA
www.instagram.com/<perfil>/    RECUSA
```

A página do vídeo é permitida; **o canal por onde os bytes passam não é**. O IP
residencial cura a primeira metade e não toca na segunda.

E o Instagram continua exactamente onde a C10.5 o deixou, re-medido agora:
`Disallow: /`. A nota da matriz é explícita sobre o que está recusado — e sobre o
que não está:

> «o motor local continua provado e **os bytes já preservados continuam
> reprocessáveis**; o que está recusado é **SAIR** para buscar mídia nova.»

```
ACQUISITION = ROUTE_NOT_ALLOWED
NÃO é CONTENT_ABSENT. NÃO é falha de rede. NÃO é fonte morta.
```

---

# E · BLOQUEIO 2 · A SALA CANÓNICA NÃO EXISTE NESTA MÁQUINA

`§17` exige a Sala PostgreSQL em ambiente descartável, e proíbe fingir com JSON.
Medido nesta máquina:

```
psql · pg_ctl · postgres · initdb · docker   -> NENHUM instalado
EAME_TEST_DSN · SUPABASE_DB_URL              -> AUSENTES
```

E o dono da Sala recusa-se, de propósito, a improvisar:

> «Pedir `POSTGRES` sem DSN levanta `SalaIndisponivel`. **Não** cai para ficheiro.»

O banco descartável do projeto é um **service container do GitHub Actions**
(`image: postgres:16`, em `.github/workflows/banco-descartavel.yml`). Ele existe
dentro do CI, e não aqui.

```
A SALA CANÓNICA VIVE NO CI. A GPU VIVE NESTA MÁQUINA.
HOJE AS DUAS NÃO SE ENCONTRAM.
```

Instalar um PostgreSQL nesta máquina para fechar o portão seria alterar a máquina
que está a ser medida, e não foi pedido.

---

# F · BLOQUEIO 3 · O VÍDEO AINDA NÃO TEM CONSUMIDOR

`§13` nomeia este como o defeito principal. Medido de novo, e o diagnóstico é
exacto:

```
VIDEO_LARGA_EM_DECLARADO  = YES   a receita nomeia data/samples/REEL-TRANSCRICOES
VIDEO_NO_RETORNO          = NO    nenhum dos 6 alvos de `retorno` está nessa pasta
VIDEO_ESPECIE_ATRAVESSA   = NO    as espécies são CATALOG · PLAN · RUN_RECEIPT,
                                  e só COLHEITA atravessa o ingresso
VIDEO_OUTPUT_HAS_CONSUMER = NO
```

O que falta está escrito: *o dono da transcrição declarar um ENVELOPE com
unidades de espécie COLHEITA, e a receita nomear esse envelope em `retorno`*.

**Não foi escrito aqui, e a razão é a mesma da missão anterior — que continua de
pé depois desta medição.** Com a aquisição recusada e a Sala ausente, escrever a
declaração seria encanamento que ninguém pode correr:

```
CAN DO != DID DO.
UMA ROTA DECLARADA E NUNCA CORRIDA É O DEFEITO QUE A PROVA DE FOGO ENCONTROU
NO WORKFLOW SOCIAL. REPETI-LO COM BOAS INTENÇÕES CONTINUA A SER REPETI-LO.
```

---

# G · O QUE **EXISTE** E NÃO FOI USADO, E POR QUÊ

Há um vídeo italiano real, de fonte autorizada, **já preservado nesta máquina**:

```
SHORTCODE   DcNkh7LCW4u          CONTA  bayer_italia   (identidade PROVED, IT)
MP4         9.218.753 bytes, preservado em 2026-09-02
TEXTO       «Sapete quale è la magia dell'estate italiane? …»   estado OK
```

Reprocessá-lo é **permitido** pela própria nota da matriz. Ele fecharia a metade
do meio da estrada — áudio derivado, transcrição na GPU, comparação CPU×GPU.

**Não foi usado nesta missão, e a razão é honesta:** ele não fecha o `§7`
(`REAL_VIDEO_COLLECTED`, que pede coleta **nesta** corrida) nem chega à Sala
(`§17`, que não existe aqui). Exercitar o meio da estrada e chamar-lhe canário
seria entregar um PASS parcial com nome de PASS inteiro.

```
BYTES PRESERVADOS != COLETA DESTA CORRIDA.
E O CANÁRIO OU ATRAVESSA INTEIRO, OU NÃO É CANÁRIO.
```

Fica **nomeado** como o caminho mais curto para a missão seguinte.

---

# H · O QUE MUDOU NO CÓDIGO

Um ficheiro, uma prova:

```
provas/o_video_tem_consumidor.py
  EGRESSO deixa de ser literal e passa a ser medido, hospedeiro a hospedeiro
  SOCIAL_TO_WAITING_ROOM e VIDEO_TO_WAITING_ROOM derivam da medição
  o detector de rota de mídia deixa de confundir METADATA com BYTES
```

Nenhuma linha de Collection, de Sala, de Admission, de STRUCTURED, de receita ou
de política de rota foi tocada. **A régua não foi afrouxada em lado nenhum.**

```
DEFAULT_DEVICE = CPU  (inalterado)
KNOW_HOW_RECONCILIATION = OUT_OF_SCOPE  (nenhuma das 16 versões foi tocada)
```

---

# I · RED TEAM — os que esta missão pôde exercer

| # | ataque | resultado |
|---|---|---|
| 19 | rede bloqueada virando `CONTENT_ABSENT` | **APANHADO** — era o inverso: `EGRESSO=BLOCKED` literal com a rede aberta |
| 20 | caption inacessível virando `ABSENT` | não atingido — não houve aquisição |
| 21 | vídeo ES/FR entrando como Itália | **PASS** — `basf_global` recusado por `?hl=it` ser língua, não país |
| 22 | GPU virando default sem benchmark | **PASS** — `DISPOSITIVO_PADRAO = CPU`, intocado |
| 9 | `SOURCE_ID` fabricado da URL | **PASS** — nenhum `SOURCE_ID` foi criado |
| 10 | output de vídeo sem consumidor | **MEDIDO E DECLARADO** `NO`, não escondido |
| 15 | Admission especial para vídeo | **PASS** — nenhuma régua tocada |
| — | metadado de vídeo contado como vídeo | **APANHADO NA MINHA PRÓPRIA REGRA** |

Os restantes (1–8, 11–14, 16–18, 23, 24) **não foram exercidos**, e isso fica
dito: sem aquisição e sem Sala, não houve RUN, RAW, STORAGE, STRUCTURED,
ADMISSION nem READY para atacar. Declarar `RED_TEAM_SURVIVORS = 0` sobre ataques
que nunca correram seria a mentira que este documento existe para não contar.

```
RED_TEAM_EXERCIDOS   = 8 de 24
RED_TEAM_SURVIVORS   = 0 dos exercidos
RED_TEAM_NAO_EXERCIDOS = 16 · NOT_EXERCISED, e não PASS
```

---

# J · VEREDITOS

```
ITALY_ONLY                      = YES
AUTHORIZED_ITALIAN_VIDEO_SOURCE = YES
PUBLIC_EGRESS                   = OPEN
SOURCE_REACHABLE                = YES

REAL_VIDEO_COLLECTED            = NO   · ROUTE_NOT_ALLOWED
RUN_CREATED                     = NO
RAW_OBSERVATION_CREATED         = NO
STORAGE_PRESERVED               = NO
DEVICE_USED                     = NOT_RUN
VIDEO_OUTPUT_WRITTEN            = NO
VIDEO_OUTPUT_CONSUMED           = NO
STRUCTURED                      = NO
ADMISSION_EXECUTED              = NO
READY_CREATED                   = NO
WAITING_ROOM_BEFORE             = NOT_MEASURABLE_ON_THIS_HOST
WAITING_ROOM_DELTA              = 0
FULL_REVERSE_LINEAGE            = NOT_EXERCISED
RETRY                           = NOT_EXERCISED

PAID_USD                        = 0,00      APIFY_RUNS = 0
LIVE_TOUCHED                    = NO        SALA_TOUCHED = NO

VALID_REAL_VIDEO_REACHED_WAITING_ROOM = NO
```

### O que destrava, e são três coisas independentes

1. **Aquisição.** Uma rota permitida que traga bytes de vídeo. Hoje não existe
   nenhuma em nenhuma plataforma. As candidatas reais: a chave
   `YOUTUBE_DATA_API_KEY` nesta máquina (destranca metadados e descoberta, não
   mídia), ou uma decisão humana sobre `youtube.media` a partir de IP
   residencial — que continua a passar por caminho `Disallow`.
2. **Sala.** Um PostgreSQL alcançável desta máquina, ou correr a metade final no
   CI onde o banco descartável já existe.
3. **Consumidor.** O ENVELOPE de espécie `COLHEITA` no dono da transcrição — e
   esse só se deve escrever quando houver 1 e 2, para não nascer por exercitar.
