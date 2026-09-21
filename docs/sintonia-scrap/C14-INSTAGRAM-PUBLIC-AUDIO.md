# C14 · INSTAGRAM PUBLIC AUDIO — o gate que mediu esta rota

```
CAPABILITY        instagram.reel.public_audio
PLATAFORMA        INSTAGRAM
CAPACIDADE GROSSA FETCH_AUDIO_BYTES
LIMITE            PUBLIC_AUDIO_ONLY
DATA DA MEDIÇÃO   2026-09-19
BRANCH            claude/ig-public-audio-v1
BASE              606443c5527982937dc7687446abbe2d8a6f9182
```

---

## 1 · O QUE ESTE DOCUMENTO É

É o gate que mediu **esta** rota — não um censo transversal, não um benchmark
geral. Ele existe porque `coleta/scrap_capacidades.py` exige que todo estado
declarado cite o documento que o mediu, e porque um ponteiro de prova que aponta
para o papel errado diverge em silêncio.

---

## 2 · A AUTORIZAÇÃO — quem decidiu, e com que escopo

A decisão é do dono do projeto, registada por escrito em 2026-09-19:

> «SIM. Autorizo o SINTONIA a adquirir e transcrever áudio de Reels públicos do
> Instagram, sem login, sem cookies de terceiros, sem sessão pessoal, sem bypass
> de acesso, preservando PLATFORM_POLICY_STATUS = DISALLOWED separadamente e com
> limite PUBLIC_AUDIO_ONLY.»

Os três eixos, que **não se derivam uns dos outros**:

```
OWNER_AUTHORIZED         SIM          decisão do PROJETO, com o escopo acima
PLATFORM_POLICY_STATUS   DISALLOWED   evidência da PLATAFORMA, preservada inteira
LIMITE                   PUBLIC_AUDIO_ONLY
```

### O que esta autorização NÃO é

```
UMA AUTORIZAÇÃO DE PROJETO NÃO É UMA AUTORIZAÇÃO DE PLATAFORMA.
```

Em lado nenhum desta árvore se escreve `PLATFORM_PERMISSION = YES`. O dono
autoriza o **risco do projeto** e não pode autorizar em nome da Meta. As duas
frases convivem — é isso que torna a decisão auditável em vez de um bypass.

### A evidência da plataforma, preservada verbatim

O `robots.txt` vivo de `instagram.com`, medido pelo portão desta casa na C10.5
(2026-09-11), 6.256 bytes, traz no bloco que nos serve:

```
User-agent: *
Disallow: /
```

O agente desta coleta não aparece nomeado em lado nenhum do ficheiro. Esse facto
**não foi apagado** por esta missão, e é por isso que `PLATFORM_POLICY_STATUS`
continua `DISALLOWED`.

### A isenção tira o TRAVÃO, não o REGISTO

A autorização do dono levanta a recusa **técnica** da matriz para esta porta
estreita. Não levanta, não reescreve e não esconde o estado da plataforma, que
continua a subir no veredicto de `decisao()` e a viajar no rasto.

---

## 3 · AS PROIBIÇÕES ABSOLUTAS — medidas contra o alvo

A lista não é dispensável, e é ela que decide se a missão é executável:

| proibição | estado nesta rota |
|---|---|
| login / conta | **não usado** — alvo público, sem autenticação |
| cookie de terceiro | **não usado** |
| sessão pessoal | **não usado** |
| CAPTCHA / bypass | **não usado** |
| paywall / acesso privado | **não contornado** |
| identidade falsa | **não usada** |

Alvo elegível é **apenas** o Reel público que qualquer navegador abre sem
autenticação. Se um alvo exigisse cruzar qualquer linha acima, a rota para ali —
e não por causa da cláusula da plataforma, mas por causa desta lista.

---

## 4 · A FRONTEIRA DA ROTA — estreita por desenho

```
É ROTA DE                 bytes de SOM de Reel PÚBLICO
NÃO É ROTA DE VÍDEO       FETCH_VIDEO_BYTES continua NOT_DECLARED
NÃO É ROTA DE LEGENDA     FETCH_TRANSCRIPT continua ROUTE_NOT_ALLOWED
NÃO É ROTA DE STORIES     instagram.story.* não muda
```

A porta antiga **não foi reescrita**. `FETCH_TRANSCRIPT` mantém o `NAO` de
2026-09-11 intacto: a rota que ele recusa baixa o **MP4 inteiro** da CDN da Meta,
e continua recusada. A capacidade nova é uma linha **grossa nova ao lado**, com o
limite que o dono autorizou.

```
AUDIO_ONLY != VIDEO.
UMA LINHA SÓ, COM O VALOR VIRADO, ABRE TUDO O QUE A CAPABILITY COBRE —
QUE É SEMPRE MAIS DO QUE O AUTORIZADO.
```

---

## 5 · O QUE FOI MEDIDO (execução, não leitura)

### 5.1 · Runtime

```
PYTHON                3.12.10   (em 3.11 o ASR devolve (False, numpy cp312))
ASR_DISPONIVEL        (True, '')
ASR_OWNER             ferramentas/fala_local.py     REAL_ASR_OWNER_COUNT = 1
MODELO_DO_REEL        medium    (presente no cache local)
```

O dono do ASR foi contado por **instanciação** do construtor do motor, não por
substring: mencionar o motor não é possuir o motor.

### 5.2 · O elo áudio→texto, com fixture sintética

Entrada gerada localmente com `ffmpeg -f lavfi` (não adquirida de terceiros),
entregue à cadeia da casa:

```
AUDIO_SECONDS        4.0
REALTIME_FACTOR      1.13
LANGUAGE             detectado
TRANSCRIPT_STATE     REQUESTED_EMPTY   (tom puro não tem fala — correto)
COST_USD             0
NETWORK_CALLS        0
```

### 5.3 · O portão, antes da mudança

Com `FETCH_TRANSCRIPT` recusado, a cadeia devolvia:

```
MEDIA_STATE               ROUTE_NOT_ALLOWED
AUDIO_ONLY_ACQUISITION    NOT_ATTEMPTED
NETWORK_CALLS             0
```

A recusa sobe **com o nome dela** — nunca como `ZERO_RESULTS` nem como
`AUDIO_ONLY_UNAVAILABLE`, que seriam mentiras precisas: o áudio existe; o que
faltava era autorização.

---

## 6 · O QUE ESTE GATE NÃO PROVA

Dito em voz alta, porque um gate que guarda só o sucesso transforma uma decisão
de risco numa capacidade autorizada:

```
EXECUTION_AGAINST_INSTAGRAM       NOT_RUN
INSTAGRAM_REQUESTS                0
```

Esta missão **não correu** um canário contra a plataforma. O que está provado é
o **mecanismo e o encaminhamento** — que a lei autoriza a porta estreita, que a
cadeia a atravessa pelo caminho canónico e que o elo até ao texto funciona. A
aquisição real de um Reel público continua por executar, e isso é um degrau
separado, com autorização separada.

```
MECHANISM (lido e encaminhado)  !=  EXECUTION (corrido contra o host)
CAPACIDADE PROVADA              !=  CAPACIDADE EXECUTADA
```

---

## 7 · O QUE A COLLECTION RECEBE

Objeto próprio da capability, sem deformar vocabulário de outra pergunta:

```
MEDIA_KIND            AUDIO       (nunca VIDEO para caber em envelope antigo)
PARENT                o Reel de origem
CAPTION_TEXT          o que o autor escreveu
TRANSCRIPT_TEXT       o que foi falado
```

`CAPTION != TRANSCRIPT` viaja no envelope com a frase da lei ao lado. Somar os
dois apagaria qual deles sustentou uma classificação.

Identidade: `SOURCE_ID` continua governado (`IT-T8-003`), nunca derivado do
handle, da URL ou do hash. `RAW_OBSERVATION_ID = raw_asset.id` — não é o
`ARTIFACT_ID` local nem o `storage_path`.

---

## 8 · RED TEAM

| ataque | resultado |
|---|---|
| pedir VÍDEO por esta porta | recusado — a porta é audio-only |
| `FETCH_TRANSCRIPT` volta a abrir | continua `ROUTE_NOT_ALLOWED` |
| `PLATFORM_POLICY_STATUS` vira `ALLOWED` | não acontece — segue `DISALLOWED` |
| ficheiro vazio / HTML renomeado | ASR **não é chamado** (`ASR_CALLS = 0`) |
| rede durante o CHECK | `NETWORK_CALLS = 0` |
| segundo dono do ASR | `REAL_ASR_OWNER_COUNT = 1` |

### Dívida conhecida, com dono — NÃO consertada aqui

`ferramentas/reel_transcricao.py:1353` escreve
`MEDIA_STATE = MEDIA_OK if raw is not None`: **ter bytes virou prova de mídia
válida**. Medido nesta missão — ficheiro vazio e HTML renomeado para `.mp4`
carimbam `MEDIA_OK` e `MEDIA_KIND_USED = VIDEO`.

O portão do ASR funciona (não desperdiça o motor com lixo); o defeito é o
**carimbo mentir**. Fica registado como achado, com o ficheiro e a linha, e **não
foi corrigido nesta missão**: é contrato de mídia partilhado, tem outro dono, e
consertá-lo aqui seria scope leak.

```
BYTES PRESENTES != MÍDIA VÁLIDA.
```

---

## 9 · CUSTO

```
APIFY_RUNS            0
PAID_USD              0
INSTAGRAM_REQUESTS    0
NETWORK_REQUESTS      0
```

A rota, quando executar, corre em `LOCAL_EXECUTOR`: zero dólar por item, custo em
tempo de máquina (ASR local).
