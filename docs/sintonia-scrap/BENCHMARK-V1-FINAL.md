# SINTONIA SCRAP — BENCHMARK V1 FINAL

> **ESTE DOCUMENTO É O ÍNDICE E O VEREDICTO. NÃO É O ARQUIVO DA PROVA.**
>
> A casa já escreveu que *«uma lei em dois sítios diverge, e a partir daí nenhuma
> das duas vale»*. O mesmo vale para prova. Cada campo abaixo traz **a resposta**
> e **onde está a prova**. A prova longa não é copiada para cá — fica no
> documento que a mediu, e esse documento é citado pelo nome.
>
> **MEDIDO_EM:** 2026-09-10 e 2026-09-11.
> **ONDE:** este contentor — Ubuntu 24.04, Python 3.11.15, Intel Xeon 2.80 GHz,
> **4 núcleos**, **sem GPU**, IP de **datacenter**, **sem login, sem cookies,
> sem Apify, sem browser com rede**.
> **O QUE NÃO FOI TOCADO:** Collection, migrations, banco live, portal, casco,
> Label Intelligence, deploy, Phase 10, Phase 11, `main`.
>
> **NADA AQUI FOI IMPLEMENTADO.** Nenhum actor foi desligado, nenhuma branch foi
> fundida, nenhuma rota entrou em produção.

---

## OS QUATRO DOCUMENTOS DE PROVA

| documento | o que prova |
|---|---|
| `ESTADO-REAL-V1.md` | git, patrimônio, relato anterior reproduzido, LinkedIn, claims de agentes verificados |
| `CONVERGENCIA-DAS-DUAS-LINHAGENS-V1.md` | as duas linhagens, a sombra que um merge dispara, a fronteira, o contrato de executor |
| `CENSO-DOS-ACTORS-E-CUSTO-V1.md` | 13 citados / 8 executados, o custo nas três palavras da lei, matriz ZERO APIFY |
| `AP-DISCOVERY-VS-CAPTURA-V1.md` | descobrir ≠ buscar, por plataforma, e o que só o runner local fecha |

Este documento acrescenta o que faltava: **X/Twitter**, **ASR comparado**,
**tradução**, **prateleira OSS datada**, **custo com fórmula**, **história do
LinkedIn**, **arquitetura**, **ordem de implementação**.

---

# IDENTIDADE DO BENCHMARK

| campo | valor |
|---|---|
| **A. REPO** | `lucianodalondon-sys/eame-sintonia` |
| **B. DATA DO BENCHMARK** | 2026-09-10 → 2026-09-11 |
| **C. BRANCH DE TRABALHO** | `claude/jolly-archimedes-lqpvlf` |
| **D. INITIAL_HEAD** | `9bed1b19` — ponta no arranque do benchmark SCRAP. A frente de Reels, anterior, partiu de `05848ad1` |
| **E. FINAL_HEAD** | o commit que traz este ficheiro. 7 commits de benchmark: `49ebde1a` → este |
| **F. PUSH_STATE** | `PUSHED` para `origin/claude/jolly-archimedes-lqpvlf` |
| **G. WORKTREE** | `/home/user/eame-sintonia`, árvore única, sem worktree paralela |

---

# H. PATRIMÔNIO SCRAP ENCONTRADO

**A correção que abre tudo: o SINTONIA SCRAP já existia.** A frente de Reels
construiu uma segunda cadeia sem saber da primeira. Prova em
`ESTADO-REAL-V1.md §A`.

| módulo | onde | capacidade | estado |
|---|---|---|---|
| `coleta/social_rotas.py` | HEAD | roteador de 9 rotas + portão `robots` | **VIVO** |
| `leis/social_matriz.py` | HEAD | matriz plataforma → rota → `auth_mode` | **VIVO** |
| `guarda/social_sessao.py` | HEAD | `preflight`, `usabilidade`, `automacao_permitida` | **VIVO** |
| `coleta/social_scrap.py` | HEAD, 864 linhas | piloto, vídeo, authmodes, YouTube, portão, ledger | **VIVO** |
| `ferramentas/contrato_ator.py` | HEAD | `portao`, `_preco`, `cheira_a_credencial` | **VIVO** |
| `coleta/story_local.py` | branch SCRAP | Stories por rota local | **NÃO CONTIDO NO HEAD** |
| `ferramentas/story_transcrever.py` | branch SCRAP | terceiro dono de ASR | **NÃO CONTIDO NO HEAD** |
| `ferramentas/fala_local.py` | HEAD (frente Reels) | **dono único de ASR** | **VIVO** |
| `ferramentas/reel_transcricao.py` | HEAD (frente Reels) | cadeia Reel → mídia → fala → prova | **VIVO** |

**Seis branches SCRAP carregam patrimônio que o HEAD não contém.** Nenhuma foi
fundida nesta missão — de propósito.

---

# I. RELATO ANTERIOR REPRODUZIDO

Tabela completa em `ESTADO-REAL-V1.md §B`. Resumo:

```
NENHUMA AFIRMAÇÃO DO RELATO ANTERIOR FOI ACEITE SEM SER REFEITA AQUI.
Duas caíram. Uma delas era minha.
```

| afirmação | veredicto |
|---|---|
| «descoberta do LinkedIn está bloqueada» | **FALSA** — está **rasa**, não bloqueada. Correção minha, em `ESTADO-REAL-V1.md §D`. |
| «duas company pages do LinkedIn devolvem zero» | **FALSA** — eram dois *slugs* errados, e o 404 é honesto (`AP-...§REFINAMENTO`) |
| «`redigir()` não apaga uma DSN» | **GUARD GAP = PROVEN · LIVE PASSWORD LEAK = NOT_REPRODUCED** |
| «80 RAW dizem PRESERVED e não existem» | **CONFIRMADO nos números**, mas é `PROVENANCE/STORAGE CONTRACT GAP`, não perda |
| «gasto histórico US$ 12,81» | **INCOMPLETO** — é **≥ US$ 12,81**; faltavam 25 runs `NOT_PRESERVED` |
| «4 idiomas provados no ASR» | **3 PASS + IT PARTIAL** |

---

# J. PLATAFORMAS ATUAIS ENCONTRADAS

`instagram` · `facebook` · `linkedin` · `youtube` · `x/twitter` — as cinco
aparecem em `leis/social_matriz.py`. O **X/Twitter não tinha benchmark**
nenhum até este documento.

# K. ENGINES EXTERNOS ATUAIS

| engine | papel hoje | pago? |
|---|---|---|
| **Apify** | 13 actors citados, 8 com execução registada | **SIM** |
| **YouTube Data API v3** | única rota que o repo classifica como `PERMITIDA` | quota |
| **yt-dlp** | captura direta e metadados (frente Reels) | não |
| **faster-whisper** | ASR local, dono único `ferramentas/fala_local.py` | não |
| **FFmpeg** | extração de áudio e duração | não |
| **gallery-dl** | usado em medição; **não integrado** | não |
| **Instaloader** | usado em medição; **não integrado** | não |

# L. CAPACIDADES ATUAIS REALMENTE PROVADAS

```
PROVADO = correu aqui, hoje, com comando registado e saída guardada.
```

1. **Captura de Reel do Instagram por URL** — 8 Reels preservados em `data/raw/REEL-MIDIA/`.
2. **Extração de áudio** — FFmpeg, 8/8.
3. **Transcrição local** — `small`/`medium`/`large-v3-turbo`, 4 idiomas, **3 PASS + IT PARTIAL**.
4. **Separação RAW ≠ DERIVED com proveniência** — `leis/artefato.py`, 47 testes.
5. **Descoberta de canal e busca no YouTube** — `yt-dlp` e API oficial.
6. **Legenda nativa e automática do YouTube** — VTT não vazio.
7. **Comentários do YouTube com thread** — `yt-dlp --write-comments`.
8. **Descoberta recente no LinkedIn** — 11/13/10 activity ids em três company pages.
9. **Vídeo nativo do LinkedIn** — 3 MP4 progressivos, URL `LONG_LIVED_OBSERVED`.
10. **Tweet completo com métricas e mídia** — `gallery-dl`, deslogado. **NOVO.**

---

# M. INSTAGRAM

| eixo | estado | prova |
|---|---|---|
| **discovery** | **PARTIAL** | `/api/v1/feed/user/<PK>/` responde, mas esgota em ~8-10 respostas por IP; listagem de perfil dá 302/429 |
| **posts** | **PARTIAL** | só pela rota acima, que é endpoint interno |
| **reels** | **PROVEN** | 8 Reels capturados por URL, `yt-dlp` e **Instaloader** |
| **stories** | **BLOCKED** | nenhuma rota anónima; a branch SCRAP tem `story_local.py`, testado contra `127.0.0.1` |
| **media** | **PROVEN** | DASH separado: vídeo + **áudio m4a 85 kbps** |
| **transcript** | **PROVEN** | **não há legenda nativa** — é aqui que o ASR é indispensável |
| **tradução** | **NÃO EXISTE** | nenhum motor de tradução no repositório (ver **T**) |
| **login/session** | **NÃO USADO** | `LOCAL_SESSION contra TERCEIRO = NOT_USABLE`, lei desta casa |
| **ZERO_APIFY** | **YES na captura · PARTIAL na descoberta** | ver **Z** |

**Dois fornecedores provados para a mesma capacidade.** `yt-dlp` trouxe
`C-63RfHoJTU.mp4` (5.158.474 bytes) e o **Instaloader 4.15.3** trouxe o mesmo
tipo de objeto com o **carimbo temporal original preservado no nome e no
mtime** (`2024-08-21_05-11-25_UTC.mp4`, 4.511.640 bytes). Isso não é
redundância: é o que torna `PROVIDER_REQUESTED ≠ PROVIDER_USED` real em vez de
teórico.

> **A rota interna fica registada como medida, não como recomendada.** A casa já
> escreveu a lei contra ela em `coleta/story_local.py`: *«NÃO PEDIR NADA QUE A
> PÁGINA JÁ NÃO FOSSE PEDIR.»* `HOUSE_POLICY_STATUS = CONTRA LEI ESCRITA`.

---

# N. FACEBOOK

| eixo | estado |
|---|---|
| **discovery** | **PARTIAL** — `gallery-dl` deslogado dá id da Page, fbid, álbuns, URL canónica |
| **posts** | **BLOCKED** — 302 login |
| **reels** | **BLOCKED** |
| **stories** | **BLOCKED** |
| **media** | **BLOCKED** |
| **transcript** | **BLOCKED** (não há de onde) |
| **tradução** | n/a |
| **login/session** | não usado |
| **ZERO_APIFY** | **NO** — e também não há rota paga provada aqui |

```
O FACEBOOK É O ÚNICO ONDE A IDENTIDADE SAI E O CONTEÚDO NÃO SAI NENHUM.
Não foi capturado um único objeto. 302 e 400 em tudo.
```

Granularidade pedida pelo coordenador, para não colapsar «Facebook = BLOCKED»:
**identidade PARTIAL · conteúdo BLOCKED · mídia BLOCKED · métricas BLOCKED.**

---

# O. X/TWITTER — capítulo novo, nunca antes medido

Esta plataforma **não tinha benchmark nenhum**. Tem agora.

| eixo | estado | prova (2026-09-11) |
|---|---|---|
| **discovery** | **UNKNOWN** | não medido — nenhuma listagem de timeline foi tentada |
| **posts** | **PROVEN** | `gallery-dl` deslogado devolveu o tweet completo |
| **media (imagem)** | **PROVEN** | `pbs.twimg.com/media/HKf1bKwWgAAzq9K?format=jpg&name=orig` → **HTTP 200, 208.216 bytes** |
| **media (vídeo)** | **PROVEN** | MP4 de 1.338.520 bytes baixado |
| **transcript** | **PARTIAL** | X serve legenda automática, mas a do vídeo testado diz literalmente *«could not transcribe the audio»* |
| **métricas** | **PROVEN** | `favorite_count`, `retweet_count`, `reply_count`, `quote_count`, `bookmark_count`, **`view_count`** |
| **perfil do autor** | **PROVEN** | seguidores, `statuses_count`, `media_count`, localização, data de criação |
| **login/session** | **não usado** | nada foi autenticado |
| **ZERO_APIFY** | **YES** | nenhum actor de X foi sequer citado no repositório |

**O objeto medido** — `Syngenta Argentina`, tweet `2064888809154551909`,
2026-06-11, `lang=es`, 832 visualizações, 5 gostos, 3 repostagens, com o texto
do lançamento de `Authence®` e uma imagem 1080×1080.

### E aqui a distinção que o coordenador pediu vale mais do que em qualquer outra plataforma

```
ZERO_APIFY  ≠  ZERO_PAID_PROVIDER
```

No X, o **Apify já é zero** — nunca houve actor. Mas existe uma rota paga
oficial, e ela tem preço de tabela **por recurso lido**:

| item | valor | fonte | data |
|---|---|---|---|
| `Posts: Read` | **US$ 0,005 por recurso** | `docs.x.com` · página de preços | página modificada 2026-07-25, obtida 2026-09-11 |
| `User: Read` | US$ 0,010 por recurso | idem | idem |
| *Owned Reads* | US$ 0,001 por recurso | idem | idem |

E o `robots.txt` do X, no grupo que nos serve:

```
User-agent: *
Disallow: /
Crawl-delay: 1
```

`Allow: /i/api/` existe — mas **apenas no grupo `Googlebot`/`Bingbot`**, que
não somos. Para nós o estado é `ROBOTS_STATUS = DISALLOW_ALL`.
**Isto não é um parecer jurídico.** É um dos cinco documentos de política, e os
outros quatro continuam por levantar.

---

# P. YOUTUBE

Detalhe completo em `CENSO-DOS-ACTORS-E-CUSTO-V1.md`. O essencial:

| eixo | estado |
|---|---|
| **discovery de canal** | **PROVEN** — `yt-dlp --flat-playlist` com `player_client=android` |
| **busca** | **PROVEN** — `ytsearch` e `search.list` |
| **metadados/métricas** | **PROVEN** |
| **comentários com thread** | **PROVEN** — `--write-comments` |
| **legenda manual e automática** | **PROVEN** — VTT não vazio nos dois vídeos testados |
| **bytes de mídia** | **BLOCKED** — 403 deste IP de datacenter |
| **legenda pela API oficial** | **BLOCKED** — `captions.download` exige ser dono do vídeo |
| **ZERO_APIFY** | **YES em capacidade · REQUIRES_REVIEW em produção** |

```
O YOUTUBE É, AO MESMO TEMPO, O MAIOR GASTO (96,2% DO MEDIDO), A PIOR
FIABILIDADE PAGA (17 PARTIAL em 29 · 19 FAILED em 48) E O ÚNICO ROBOTS.TXT
QUE NÃO É BLOQUEIO TOTAL. É onde a decisão vale mais e custa menos.
```

---

# Q. LINKEDIN — CAPÍTULO ESPECIAL

Prova longa em `ESTADO-REAL-V1.md §D`. **Sete capacidades, medidas uma a uma —
e não se escreve «a cadeia LinkedIn inteira» sem dizer qual delas.**

| # | capacidade | `TECHNICAL_CAPABILITY` | primeiro ponto de quebra |
|---|---|---|---|
| 1 | **discovery recente** (company page) | **PROVEN** | profundidade, não acesso |
| 2 | **discovery histórico** | **UNKNOWN** | «Show more» não expõe URL de página seguinte |
| 3 | **post direto por URL** | **PROVEN** | — |
| 4 | **vídeo nativo** | **PROVEN** | — |
| 5 | **áudio / transcrição** | **PROVEN por legenda** | a legenda é de máquina (ver abaixo) |
| 6 | **documentos (carrossel PDF)** | **NOT_EXECUTED** | nunca tentado |
| 7 | **comentários** | **UNKNOWN** | nunca tentado |

**`LINKEDIN_DISCOVERY_RECENT = PROVEN`. `LINKEDIN_DISCOVERY_DEPTH = SHALLOW`.**
Não se volta a escrever `LINKEDIN_DISCOVERY = BLOCKED` — isso foi erro meu,
medido e corrigido.

### Mídia e legenda — com uma correção minha

`MP4 progressivo`, três variantes de qualidade, URL `LONG_LIVED_OBSERVED`
(`e=2147483647`). **Não «permanente»:** observada longa uma vez, numa escala de
quatro valores (`TEMPORARY` · `LONG_LIVED_OBSERVED` · `DOCUMENTED_STABLE` ·
`UNKNOWN`).

> **CORREÇÃO.** Escrevi antes que a legenda do LinkedIn vinha em **WebVTT**.
> Está errado em duas coisas, e as duas importam.
>
> 1. **O formato é SRT**, não WebVTT. Os bytes provam: `1\n00:00:00,220 -->
>    00:00:03,032\n` — numeração de sequência e **vírgula** decimal.
> 2. **A legenda é automática**, não humana. O caminho da URL di-lo em claro:
>    `.../video-auto-caption-srt-acs-singleton/...`
>
> A segunda correção muda a decisão. Uma legenda automática é **ASR de outra
> casa** — está sujeita à mesma classe de erro que o nosso, incluindo trocar
> termo agronómico e nome de marca. Continua a ser texto de graça com marcação
> temporal, e continua a valer a pena. Mas **não é evidência de melhor
> qualidade que a nossa** — é evidência **mais barata**, e isso é outra coisa.

### A pergunta em aberto agora é HISTÓRIA, não acesso

| cenário | o que exigiria | provedor | login | custo | `ZERO_APIFY` |
|---|---|---|---|---|---|
| `RECENT_WINDOW_ONLY` | nada — **já funciona hoje** | próprio (HTTP simples) | NÃO | **US$ 0** | **YES** |
| `30_DAYS` | `UNKNOWN` — depende de quantos posts cabem nos ~11 ids | próprio, talvez | NÃO | 0 | provável |
| `90_DAYS` | paginação além da landing | **não descoberta** | ? | ? | **UNKNOWN** |
| `1_YEAR` | paginação profunda | `harvestapi~linkedin-post-search` correu 1 vez, 472 itens, `COST_USD = NOT_PRESERVED` | ? | **NÃO SEI** | **NO** hoje |
| `FULL_AVAILABLE_HISTORY` | idem, em escala | idem | ? | **NÃO SEI** | **NO** hoje |

```
A JANELA RECENTE JÁ ESTÁ RESOLVIDA E CUSTA ZERO.
A HISTÓRIA NÃO ESTÁ MEDIDA, E O ÚNICO RUN QUE A TOCOU NÃO GUARDOU O PREÇO.
```

**Decisão do coordenador, não minha:** quanta história o SINTONIA precisa. Se a
resposta for `RECENT_WINDOW_ONLY`, o LinkedIn sai do Apify hoje. Se for
`1_YEAR`, há um benchmark inteiro por fazer.

---

# R. PIPELINE DE VÍDEO

Provado ponta a ponta pela frente de Reels, em `O-REEL-DEIXA-DE-SER-MUDO.md`:

```
URL → identidade → mídia (5 fornecedores em degraus) → áudio (FFmpeg)
    → fala (faster-whisper) → artefato DERIVED com pai declarado
    → classificação que separa CAPTION de TRANSCRIPT
```

Cinco fornecedores de captura, em degraus, **e cada degrau registado**:
`CAPTURA_FORNECIDA` → `CAPTURA_JA_PRESERVADA` → `CAPTURA_YTDLP` →
`CAPTURA_EMBED` → `CAPTURA_APIFY`. Cinco estados de mídia:
`MEDIA_OK` · `MEDIA_URL_ABSENT` · `MEDIA_URL_EXPIRED` ·
`MEDIA_DOWNLOAD_FAILED` · `NOT_A_VIDEO`.

**O que este pipeline faz e nenhum actor pago faz:** guarda quem foi o pai do
texto. `PARENT_ARTIFACT_ID`, `PARENT_SHA256`, `DERIVATION_TYPE =
SPEECH_TRANSCRIPTION`. Um transcript sem pai é uma alegação; com pai, é prova.

---

# S. ASR

## S.1 · Dono atual

**`ferramentas/fala_local.py` é o dono único no HEAD.** Confirmado por máquina:
`WhisperModel(` e `BatchedInferencePipeline(` aparecem em **exatamente uma
linha cada**, ambas dentro de `fala_local.py`. Cinco módulos o importam;
nenhum instancia motor próprio. Um teste guarda essa lei
(`tests/test_reel_transcricao.py:430`).

```
UM DONO NO HEAD. MAS TRÊS NO UNIVERSO.
```

O terceiro é `ferramentas/story_transcrever.py`, que vive numa branch SCRAP
não contida no HEAD. **Não foi corrigido — de propósito.** Corrigir era
convergir, e convergir estava proibido nesta missão. Entra na matriz de
convergência como `PORT`.

| constante | valor no HEAD |
|---|---|
| `MODELO_PADRAO` | `small` (env `SINTONIA_ASR_MODELO`) |
| `BEAM` | 1 |
| `LOTE` | 8 |
| `CONFIANCA_MINIMA` | 0.6 |
| `NO_SPEECH_LIMITE` | 0.6 |
| `LOGPROB_LIMITE` | −1.0 |
| **`reel_transcricao.MODELO_PADRAO`** | **`medium`** |

> **Dois padrões, não um.** `fala_local` diz `small`; a cadeia de Reels diz
> `medium`. Não é defeito — é a camada de cima a decidir. Mas **não está escrito
> em lado nenhum que isto é deliberado**, e um leitor futuro vai lê-lo como
> contradição. Fica como dívida de documentação.

## S.2 · `small` vs `medium` vs `large-v3-turbo` — medido aqui

**COMANDO:** `fala_local.modelo(M).transcribe(wav, batch_size=8, beam_size=1,
vad_filter=True, language=…, condition_on_previous_text=False)`
**HARDWARE:** este contentor — `cpu` / `int8` / 4 threads. **Sem GPU.**
**PROVA:** `scratchpad/bench.log`, `scratchpad/bench.json`.

| modelo | carga | IT `rtf` | ES `rtf` | IT `avg_logprob` | ES `avg_logprob` |
|---|---|---|---|---|---|
| `small` | 2,58 s | **6,95×** | **7,66×** | −0,248 | −0,094 |
| `medium` | 11,59 s | 2,73× | 2,56× | −0,094 | −0,066 |
| `deepdml/faster-whisper-large-v3-turbo-ct2` | 8,76 s | 2,89× | 3,05× | **−0,058** | **−0,026** |

`rtf` = segundos de áudio por segundo de máquina. Maior é mais rápido.

## S.3 · Termos agronómicos e marcas — e por que não há vencedor global

Léxico declarado **antes** de medir. IT: `Syngenta · mais · maiscoltori ·
granella · ibridi · Discovery Seeds`. ES: `Syngenta · fitosanitarios ·
bioestimulantes · CSIC · Cristóbal`.

| modelo | idioma | sem hotwords | com hotwords |
|---|---|---|---|
| `small` | IT | **0/6** | **6/6** |
| `medium` | IT | 4/6 | 5/6 |
| `large-v3-turbo` | IT | 4/6 | **6/6** |
| `large-v3-turbo` | ES | 3/5 | **5/5** |

O `small` sozinho é inutilizável para este domínio: escreveu **`MICE`** onde se
diz `mais`, **`Discovery Seats`**, **`disingenta`**, **`mai scoltori`**.
Zero em seis.

**E nenhum modelo ganha em tudo.** O `large-v3-turbo` é o único que acertou
**`granella`** — o termo agronómico correto, onde `medium` escreveu `garella`.
Mas **regrediu na marca em espanhol**: `medium` escreveu **`Syngenta`** e o
`turbo` escreveu **`Singenta`**.

```
NÃO TROQUE `medium` POR UM MODELO MAIS NOVO SÓ PORQUE ELE É MAIS NOVO.
Nesta medição ele corrige um termo e estraga outro.
```

## S.4 · O achado que muda mais do que o modelo — e o risco que traz

`hotwords` sobe a precisão terminológica em **todos** os casos medidos. Mas:

> **Em espanhol, com `hotwords`, o `large-v3-turbo` derivou para PORTUGUÊS a
> meio da transcrição.** Nove marcas inequívocas na segunda metade: *«que as
> novas técnicas genómicas»*, *«E é fundamental a colaboración com as entidades
> públicas»*, *«essa tecnologia de maneira transparente junto com a
> administração»*. O texto encurtou 43 caracteres. Sem `hotwords`, **zero**
> marcas de português.

E no `small` em italiano o ganho terminológico veio com **dano na frase**:
*«Buongiorno, passio a tutti i mais»* onde se diz *«Buongiorno appassionati di
mais»*.

```
HOTWORDS = PRECISÃO DE TERMO PARA CIMA, INTEGRIDADE DE LÍNGUA EM RISCO.
Medido. Não adotado. Quem adotar tem de guardar o texto dos dois lados.
```

## S.5 · Marcação temporal por palavra

`word_timestamps=True`, no mesmo áudio: **51 palavras com tempo** no `medium`,
**52** no `turbo`, e o texto saiu **idêntico** ao de `word_timestamps=False`
nos dois. O custo foi **nulo ou negativo** (`medium` 12,88 s contra 12,11 s;
`turbo` **9,19 s contra 10,28 s**).

> Legenda com marcação temporal, para alinhar fala com o momento do vídeo,
> **já está disponível e praticamente de graça.** Não está ligada.

## S.6 · O guarda dos `'...'`

O defeito real e o guarda que o cobre estão em `O-REEL-DEIXA-DE-SER-MUDO.md`.
O que importa repetir aqui, porque é desconfortável:

```
O GUARDA DO MODO EM LOTE NÃO TERIA APANHADO O CASO REAL.
```

`faster-whisper 1.2.1` em modo `BatchedInferencePipeline` **não aplica**
`no_speech_threshold`, `log_prob_threshold` nem `compression_ratio_threshold` —
apenas os reporta por segmento. O que apanhou o `'...'` foi `_tem_conteudo()`,
que exige pelo menos uma letra ou dígito. `DISCARDED_OUTPUT` guarda o que foi
recusado. **Isto é `GUARD GAP = PROVEN`.**

## S.7 · Candidatos alternativos

| candidato | estado | porquê |
|---|---|---|
| `deepdml/faster-whisper-large-v3-turbo-ct2` | **MEDIDO** | melhor `avg_logprob`, `rtf` comparável ao `medium`, mas troca um erro por outro |
| `whisper.cpp` | **NOT_EXECUTED** | **não está instalado** neste contentor |
| Whisper de referência (`openai-whisper`) | **NOT_EXECUTED** | exige `torch`, **ausente** aqui |
| ASR pago (Apify `starvibe~`, `pintostudio~`) | **MEDIDO E PIOR** | 5 de 20 itens vieram vazios num artefato pago; 19 de 48 runs `FAILED` |

**LIMITAÇÃO DECLARADA:** tudo isto foi medido em **4 núcleos sem GPU**. O
runner local `eame-sintonia-local-2` tem outro hardware. **A escolha de modelo
não deve ser fechada antes de repetir esta tabela lá.**

---

# T. TRADUÇÃO

## T.1 · O estado, em uma linha

```
A CASA TEM A LEI DA TRADUÇÃO ESCRITA E CONFERIDA. NÃO TEM MOTOR NENHUM.
```

**COMANDO:** `grep -rn "deepl\|googletrans\|translate.google\|argos\|nllb\|m2m100\|opus-mt" --include=*.py .`
**RESULTADO:** **zero ocorrências.** Nem cliente, nem chave, nem chamada.

E, no ambiente: `argostranslate`, `transformers`, `torch`, `sentencepiece` —
**todos ausentes**.

## T.2 · O que existe, e é mais valioso do que um motor

`data/i18n/v21-traducoes.json` — **1.055 traduções** PT→IT+EN, com a chave
sendo **o próprio texto em português**, e cinco proibições declaradas:

```
não acrescentar fato · não fortalecer alegação · não mudar alcance geográfico
não mudar confiança · não remover incerteza
```

E três camadas de conferência já construídas:

| camada | o que faz |
|---|---|
| `motor/v21_traducao_trava.py` | trava mecânica: número, data, negação, incerteza, lugar, ênfase |
| conferente adversarial | um agente por lote tentou **derrubar** cada tradução; **33 frases foram refeitas** |
| `tests/test_v21_traducao_trava.py` | mentiras plantadas de propósito, uma por proibição |

E o que a própria memória confessa que nenhuma das três alcança:

> *«se «autorizza» quer dizer «autoriza». Isso é leitura humana e não foi feita
> frase a frase.»*

## T.3 · O que isto significa para o SCRAP

O SINTONIA hoje **classifica no idioma original** — `comunicacao_classificar.py`
tem tabelas de termos por língua. **Nada é traduzido antes de ser julgado.** Isso
é uma decisão de arquitetura, e é a mais segura: tradução antes do julgamento
introduz um pai a mais entre o fato e a conclusão.

Se algum dia houver motor de tradução, o contrato já está definido pela lei
existente, e tem de carregar:

```
SOURCE_LANGUAGE · ORIGINAL_TEXT · TARGET_LANGUAGE · TRANSLATED_TEXT
PROVIDER · MODEL · VERSION · DATE · PARENT_ARTIFACT_ID · PARENT_SHA256
```

— exatamente o mesmo contrato de `leis/artefato.py`, com
`DERIVATION_TYPE = TRANSLATION`. **Uma tradução é um artefato DERIVED. Não é
uma anotação.**

E para legenda: SRT e VTT **têm de manter a marcação temporal**. Traduzir um SRT
e devolver um parágrafo destrói a única coisa que fazia o SRT valer mais que o
texto corrido.

## T.4 · Preço, se um dia for pago

| provedor | unidade | preço | data da tabela |
|---|---|---|---|
| Google Cloud Translation (NMT) | 1.000.000 de caracteres | **US$ 20,00** | obtida 2026-09-11 |
| Google Cloud Translation (NMT) | primeiros 500.000 car./mês | **grátis** (crédito de US$ 10) | idem |
| Google Cloud Translation (LLM) | 1.000.000 car. entrada + 1.000.000 saída | **US$ 10,00 + US$ 10,00** | idem |
| **DeepL** | — | **NÃO SEI** | página obtida, preço não legível sem JavaScript |

**`NÃO SEI` está escrito de propósito.** A lei da casa proíbe misturar `0`,
`NÃO SEI` e `NOT_PRESERVED`, e não medi o DeepL.

---

# U. PROJETOS OSS APROVADOS PARA TESTE

**MÉTODO:** versão e data de lançamento vieram do **PyPI JSON API**, obtido
2026-09-11. **LIMITAÇÃO DECLARADA:** a atividade no GitHub **não pôde ser
medida** — a API do GitHub nesta sessão está restrita ao repositório da casa e
devolveu *«GitHub access to this repository is not enabled for this session»*
para os oito repositórios consultados. **A data de lançamento no PyPI é o
substituto honesto, não o mesmo dado.**

| projeto | versão | lançamento | licença | plataformas | vídeo | comentários | descoberta | login | risco | útil? |
|---|---|---|---|---|---|---|---|---|---|---|
| **yt-dlp** | `2026.8.19` | 2026-08-19 | Unlicense | IG · YT · X · LI | **SIM** | **SIM** (YT) | SIM (YT) | opcional | **BAIXO** | **JÁ EM USO** |
| **gallery-dl** | `1.32.11` | **2026-09-04** | GPL-2.0-only | X · IG · FB | SIM | não | parcial | opcional | **BAIXO** | **SIM** |
| **Instaloader** | `4.15.3` | instalado aqui | MIT | Instagram | **SIM** | SIM | SIM | opcional | **MÉDIO** | **SIM** |
| **FFmpeg** | `6.1.1` | sistema | LGPL/GPL | — | — | — | — | — | **BAIXO** | **JÁ EM USO** |
| **faster-whisper** | `1.2.1` | instalado aqui | MIT | — | — | — | — | — | **MÉDIO** | **JÁ EM USO** |
| **CTranslate2** | `4.8.2` | instalado aqui | MIT | — | — | — | — | — | BAIXO | **JÁ EM USO** |
| **Playwright** | `1.62.0` | instalado aqui | Apache-2.0 | todas | — | — | SIM | sim | **ALTO** | **NÃO AQUI** |

**Risco `MÉDIO` do faster-whisper** não é abandono: é o defeito medido do modo
em lote (**S.6**), que a casa já contornou com guarda própria.

**Risco `ALTO` do Playwright** é ambiental, não do projeto: **o Chromium deste
contentor não alcança a rede** — `ERR_CONNECTION_RESET` em tudo. Qualquer rota
que precise de browser é `NOT_EXECUTED` aqui e só o runner local decide.

# V. PROJETOS OSS REJEITADOS

| projeto | versão | último lançamento | idade | veredicto |
|---|---|---|---|---|
| **twscrape** | `0.20.1` | **2026-08-25** | 17 dias | **NÃO REJEITADO — mas exige contas** |
| **twikit** | `2.3.3` | 2025-02-07 | **~19 meses** | **REJEITADO** |
| **twitter-api-client** | `0.10.22` | 2024-04-21 | **~29 meses** | **REJEITADO** |
| **snscrape** | `0.7.0.20230622` | 2023-06-22 | **~39 meses** | **REJEITADO** |
| **Nitter** | — | — | — | **NÃO MEDIDO** — instâncias públicas são de terceiros |

# W. MOTIVO DAS REJEIÇÕES

```
UM SCRAPER DE REDE SOCIAL PARADO HÁ UM ANO NÃO É «ESTÁVEL». É ANTIGO.
```

Estas bibliotecas seguem uma API privada que muda sem aviso e sem versão.
Quando param, param em silêncio: devolvem vazio, e vazio lê-se como *«a conta
não publicou nada»*. É exatamente a armadilha que a casa já nomeou como
`SOURCE FAILURE != ZERO`.

**E as três rejeitadas são desnecessárias.** O `gallery-dl`, lançado há **sete
dias**, já entregou o tweet inteiro com métricas e mídia, **deslogado**. Não há
por que adotar uma dependência morta para fazer o que uma viva já faz.

O `twscrape` fica de fora por outro motivo, e não é qualidade: ele exige um
pool de **contas autenticadas**. Isso esbarra em `LOCAL_SESSION contra TERCEIRO
= NOT_USABLE`, lei desta casa, e em `PLATFORM_POLICY_STATUS` que ninguém
levantou. **Decisão de política, não de engenharia.**

> **NÃO REINVENTAR O QUE JÁ ESTÁ MADURO.** `yt-dlp` e `gallery-dl` resolvem
> extração e paginação de mídia melhor do que qualquer coisa que escrevêssemos
> este mês. O que a casa tem de construir é o que **ninguém** vende: a
> proveniência, o roteador de adaptadores e o contrato com a Collection.

---

# X. ACTORS APIFY SUBSTITUÍVEIS

| actor | capacidade | substituto provado hoje | gasto medido |
|---|---|---|---|
| `streamers~youtube-scraper` | discovery, busca, metadados | `yt-dlp` · API `search.list`/`videos.list` | **US$ 4,4720** |
| `streamers~youtube-comments-scraper` | comentários com thread | `yt-dlp --write-comments` · API `commentThreads` | **US$ 7,7280** |
| `pintostudio~youtube-transcript-scraper` | legenda | `yt-dlp --write-subs` / `--write-auto-subs` | US$ 0,1300 **+ 20 `NOT_PRESERVED`** |
| `starvibe~youtube-video-transcript` | legenda | idem | **nunca correu** |
| `apify~instagram-reel-scraper` | Reel por URL | `yt-dlp` · **Instaloader** | **nunca correu** |
| `apify~instagram-scraper` | posts | — parcial | **nunca correu** |
| `apify~instagram-profile-scraper` | perfil | — parcial | **nunca correu** |
| `scrapesmith~instagram-comments-scraper` | comentários | — **não substituído** | **nunca correu** |
| `apify~facebook-posts-scraper` | posts | — **não substituído** | **nunca correu** |
| `instagram-hashtag-scraper` **(órfão)** | hashtag | — não medido | correu 1×, 60 itens, **não citado no código** |

```
96,2% DO GASTO MEDIDO ESTÁ NOS TRÊS PRIMEIROS. E OS TRÊS TÊM SUBSTITUTO
TÉCNICO PROVADO HOJE, SEM LOGIN, SEM BROWSER E SEM CUSTO.
```

**Os seis que nunca correram não geram poupança.** Aposentá-los é higiene de
código. Não se escreve «economia» onde nunca houve gasto.

# Y. ACTORS / CAPACIDADES AINDA NÃO SUBSTITUÍDOS

| capacidade | estado | por quê |
|---|---|---|
| **bytes de mídia do YouTube** | **BLOCKED** | `403` de IP de datacenter — só o runner local decide |
| **comentários do Instagram** | **NO** | nenhuma rota anónima provada |
| **Stories do Instagram** | **UNKNOWN** | exige sessão; a branch SCRAP tem código, testado contra fixture local |
| **qualquer conteúdo do Facebook** | **NO** | 302/400 em tudo |
| **história profunda do LinkedIn** | **UNKNOWN** | «Show more» não expõe URL de página seguinte |
| **descoberta profunda no Instagram** | **PARTIAL** | a janela esgota em ~8-10 respostas por IP |

# Z. MATRIZ ACTOR → SUBSTITUTO

Matriz de cinco colunas em `CENSO-DOS-ACTORS-E-CUSTO-V1.md`. O resumo, com o X
acrescentado:

| capacidade | `ZERO_APIFY_TECH` | `ZERO_PAID_EXT` | `ZERO_BROWSER` | `ZERO_LOGIN` | `PRODUCTION_READY` |
|---|---|---|---|---|---|
| YouTube · discovery, busca, metadados, comentários, legendas | **YES** | YES | YES | YES | **REQUIRES_REVIEW** |
| YouTube · bytes de mídia | **NO** (403) | NO | UNKNOWN | UNKNOWN | NO |
| LinkedIn · janela recente, post, vídeo, legenda | **YES** | YES | YES | YES | **REQUIRES_REVIEW** |
| LinkedIn · história profunda | **UNKNOWN** | UNKNOWN | UNKNOWN | UNKNOWN | NO |
| Instagram · Reel por URL | **YES** | YES | YES | YES | **PARTIAL** (retry ~1 em 6) |
| Instagram · descoberta de perfil | **PARTIAL** | PARTIAL | NO neste IP | YES | **NO** |
| Instagram · Stories, comentários | **NO / UNKNOWN** | — | — | **NO** | NO |
| **X · post, mídia, métricas** | **YES** *(nunca houve actor)* | **YES** | **YES** | **YES** | **REQUIRES_REVIEW** |
| Facebook · qualquer conteúdo | **NO** | NO | UNKNOWN | UNKNOWN | NO |

> `REQUIRES_REVIEW` em quase toda a coluna de produção **não é hesitação**. É o
> eixo de política, que nenhuma medição técnica resolve. Ver **AQ**.

---

# AA. ZERO_APIFY_FEASIBILITY

```
PARTIAL
```

**YES** para YouTube (discovery, busca, metadados, comentários, legendas),
LinkedIn na janela recente, Instagram Reel por URL e X inteiro. **NO** para
Facebook e comentários do Instagram. **UNKNOWN** para história do LinkedIn e
Stories.

Em dinheiro medido: as capacidades com substituto provado cobrem
**≥ US$ 12,33 dos ≥ US$ 12,81** gastos — **96,2%**.

# AB. LINKEDIN_VIDEO_FEASIBILITY

```
YES
```

MP4 progressivo, três qualidades, sem login, sem browser, sem Apify, com URL
`LONG_LIVED_OBSERVED` e legenda SRT automática servida ao lado.
**É a mídia mais fácil das cinco plataformas.**

# AC. INSTAGRAM_REELS_TRANSCRIPTION_FEASIBILITY

```
YES — e já está feito.
```

8 Reels capturados, áudio extraído, transcritos com pai declarado, texto ligado
à classificação sem se confundir com a legenda do autor. 47 testes.
**3 idiomas PASS + italiano PARTIAL.**

---

# AD. ARQUITETURA RECOMENDADA

## AD.1 · A primeira coisa a dizer é o que a arquitetura NÃO é

```
O SINTONIA SCRAP NÃO É O ORQUESTRADOR DA COLLECTION.
`orquestrador/orquestrador.py` continua a ser o dono único da orquestração,
e está ACIMA do SCRAP. COL-LAW-011.
```

O SCRAP é **um executor**. Dentro dele há um roteador — mas é um **SCRAP
ADAPTER ROUTER**, local, que só escolhe adaptador de plataforma. Não conhece
pedido, não conhece receita, não decide escopo, não fala com a Collection.

## AD.2 · Um produto, adaptadores por plataforma

```
NÃO:  linkedin-scrap/ · instagram-scrap/ · youtube-scrap/     (N produtos)
NÃO:  if platform == 'linkedin': ... elif platform == ...     (monólito)
SIM:  sintonia-scrap/  com  adapters/<plataforma>.py          (um produto)
```

```
                       orquestrador/orquestrador.py          ← DONO ÚNICO
                                    │  CAPABILITIES/CHECK/COLLECT/STATE/OUTPUT/TRACE
                       ┌────────────┴────────────┐
                  SINTONIA SCRAP            outros executores
                       │
              SCRAP ADAPTER ROUTER         ← escolhe ADAPTADOR, nada mais
       ┌────────┬──────┴───┬─────────┬──────────┐
   instagram  linkedin  youtube      x      facebook      ← ADAPTADORES
       │          │         │        │          │
       └──────────┴────┬────┴────────┴──────────┘
                       │  cada adaptador pede PROVIDERS em degraus
             ┌─────────┴──────────┐
        PROVIDERS: yt-dlp · gallery-dl · Instaloader · HTTP próprio · API oficial · Apify
                       │
                       │
                  ┌────┴────┐
              ONLINE      LOCAL              ← AMBIENTE DE EXECUÇÃO, eixo à parte
              RUNNER      RUNNER
                       │
        ── COMPONENTES TRANSVERSAIS (NÃO vivem dentro de adaptador) ──
        ASR (fala_local) · tradução · processamento de mídia (FFmpeg)
        evidência e proveniência (leis/artefato.py) · trace · redação de segredo
```

## AD.5 · O executor é **híbrido**, e isso não são dois produtos

```
NÃO EXISTE «SINTONIA SCRAP ONLINE» E «SINTONIA SCRAP LOCAL».
Existe UM executor que sabe correr em dois ambientes.
```

`PROVIDER` e `EXECUTION_ENVIRONMENT` são **eixos diferentes**, e a confusão
entre eles é o erro que esta arquitetura tem de impedir por construção:

| exemplo | `PROVIDER` | `EXECUTION_ENVIRONMENT` | resultado medido |
|---|---|---|---|
| metadados do YouTube | `yt-dlp` | **ONLINE** | **PROVEN** hoje |
| bytes de mídia do YouTube | `yt-dlp` | **ONLINE** | **BLOCKED** — 403 |
| bytes de mídia do YouTube | `yt-dlp` | **LOCAL** | **UNKNOWN** — nunca tentado lá |

**O mesmo fornecedor, dois ambientes, dois resultados.** Uma matriz que só
tivesse a coluna `PROVIDER` teria escrito «`yt-dlp` não serve para YouTube», o
que é falso.

Quem decide o ambiente **não é o adaptador**. O adaptador declara capacidade e
fornecedor; a **política de execução** escolhe o ambiente, e a regra é uma só:

```
USAR O AMBIENTE MAIS BARATO E MAIS SIMPLES QUE CUMPRA A CAPACIDADE.
Não «social vai para o PC local». Não «sempre fizemos assim».
```

## AD.3 · `ADAPTER ≠ PROVIDER`, e o fallback nunca é silencioso

Um **adaptador** é *«como se fala com o Instagram»*. Um **fornecedor** é *«com
que ferramenta»*. Um adaptador pode ter vários fornecedores em degraus — e a
frente de Reels **já provou isso funcionando**, com cinco degraus registados.

Toda troca de fornecedor **tem de ficar escrita**:

```
PROVIDER_REQUESTED   qual foi pedido
PROVIDER_USED        qual entregou
WHY_FALLBACK         por que o primeiro não serviu
RESULT               o que saiu
```

```
FALLBACK SILENCIOSO É MENTIRA COM OUTRO NOME. Quem lê o resultado tem
de conseguir dizer por que caminho ele veio, sem abrir o código.
```

## AD.4 · O que o SCRAP declara ao orquestrador — `COL-LAW-013`

| verbo | o que o SCRAP responde |
|---|---|
| `CAPABILITIES` | a matriz **Z**, por plataforma **e por capacidade** |
| `CHECK` | *consigo chegar agora, sem gastar?* — `robots`, sessão, disponibilidade do binário |
| `COLLECT` | executa um adaptador e devolve artefato RAW com proveniência |
| `STATE` | **seu** cursor: shortcode, `activity id`, `page token`, `Last-Modified` |
| `OUTPUT` | caminho e forma do que largou |
| `TRACE` | degraus, fornecedores, hora, custo, e as três palavras de `COL-LAW-019` |

**`COL-LAW-016` é respeitada:** o orquestrador só conhece `PONTUAL` ·
`INCREMENTAL` · `TOTAL`. Que o cursor do LinkedIn seja um `urn:li:activity:` e
o do YouTube um `page token` é assunto **interno** do SCRAP.

**`COL-LAW-014` fica honesta:** hoje `pedido/receitas.py` declara 6 dos 12
campos de capacidade. O SCRAP **não conserta isso nesta missão**.

---

# AE. PAPEL DO PC LOCAL

O runner `eame-sintonia-local-2` tem **dois papéis, e são diferentes**.

**Papel 1 — worker de processamento pesado.** É o candidato natural para
download pesado de mídia, FFmpeg, extração de áudio, VAD, ASR, tradução local
se um dia for aprovada, browser real e CDP, e rotas com sessão legítima. O
runner online fica com o que não precisa de máquina: descoberta, HTTP e API,
metadados, agendamento, `CHECK`, coleta leve, checkpoint e controlo, **legenda
nativa**, e captura direta quando ela funciona.

**Papel 2 — o único lugar onde sete medições podem fechar.** Todas estão em `AP-...§O QUE SÓ O RUNNER LOCAL
PODE FECHAR`, com o comando escrito e nenhuma mascarada.

| o que só lá fecha | por que aqui não |
|---|---|
| bytes de mídia do YouTube | `403` de IP de datacenter |
| repetir a rota de feed do Instagram | janela esgota em ~8-10 respostas por IP |
| Stories ao vivo | teste bate em `127.0.0.1` com fixture |
| qualquer rota com browser | Chromium sem rede: `ERR_CONNECTION_RESET` |
| qualquer rota com Apify | `APIFY_TOKEN_POOL` é segredo ligado ao runner |
| **escolha final do modelo de ASR** | 4 núcleos sem GPU aqui; lá o hardware é outro |
| `whisper.cpp` como alternativa | **não está instalado** aqui |

```
O PC LOCAL NÃO É ONDE O SISTEMA RODA. É ONDE ELE PODE SER PROVADO.
```

---

# AF. CUSTO

> **Cada projeção abaixo mostra `FÓRMULA` · `PREÇO UNITÁRIO` · `UNIDADE DE
> COBRANÇA` · `DATA DO PREÇO` · `HIPÓTESES`. Sem isso é palpite com casa
> decimal.**

## AF.1 · O que já foi gasto — reproduzido da fonte primária

**FONTE:** `data/samples/SENSOR-PILOT/RUNS-{A..E}.json` + `RUN-MANIFEST.json`
(119 registos). **MÉTODO:** soma programática, não leitura de prosa.

| palavra da lei | significado | runs |
|---|---|---|
| medido | gastou e registou | **US$ 12,8140** |
| `0` medido | não gastou | 55 |
| **`NOT_PRESERVED`** | **gastou e não guardou** | **25** |
| `NÃO SEI` | não medido | 0 |

```
O TOTAL REAL É ≥ US$ 12,81. O QUE PASSA DISSO É «NÃO SEI».
A lei obriga a dizê-lo assim, não a arredondar nem a estimar.
```

## AF.2 · Preço unitário **observado** — não é tabela do fornecedor

**FÓRMULA:** `US$ medido ÷ ITEM_COUNT_RAW`, por actor, sobre os mesmos 119 registos.
**DATA:** runs do piloto de 2026-09.
**HIPÓTESE:** os 25 runs `NOT_PRESERVED` **não entram**, logo todo valor abaixo é **piso**.

| actor | itens | US$ | **US$/item observado** |
|---|---|---|---|
| `streamers~youtube-comments-scraper` | 3.737 | 7,7280 | **0,002068** |
| `streamers~youtube-scraper` | 1.173 | 4,4720 | **0,003812** |
| `harvestapi~linkedin-profile-scraper` | 120 | 0,4840 | **0,004033** |
| `pintostudio~youtube-transcript-scraper` | 28 | 0,1300 | **0,004643** |

## AF.3 · Projeção — transcrever 1.000 Reels por mês

**HIPÓTESES DECLARADAS:** duração média **58,5 s**, que é a média real dos 8
Reels preservados (467,90 s ÷ 8) — **não é um número escolhido**. Hardware:
este contentor, 4 núcleos, sem GPU. Runner próprio, **energia não contabilizada**.

| rota | fórmula | preço unitário | unidade | data | total/mês |
|---|---|---|---|---|---|
| **ASR local, `medium`** | `1000 × 58,5 s ÷ rtf 2,6` | US$ 0 em dinheiro | segundo de CPU | 2026-09-11 | **US$ 0 · ≈ 6 h 15 min de CPU** |
| **ASR local, `small`** | `1000 × 58,5 s ÷ rtf 7,3` | US$ 0 | idem | idem | **US$ 0 · ≈ 2 h 14 min** — mas **0/6 nos termos** |
| **ASR local, `turbo`** | `1000 × 58,5 s ÷ rtf 3,0` | US$ 0 | idem | idem | **US$ 0 · ≈ 5 h 25 min** |
| **actor pago de transcript** | `1000 × US$ 0,004643` | 0,004643 | item | 2026-09 | **US$ 4,64 · com 40% `FAILED` observado** |

```
A COMPARAÇÃO HONESTA NÃO É «GRÁTIS CONTRA 4,64». É «SEIS HORAS DE CPU
NUM COMPUTADOR QUE JÁ É NOSSO» CONTRA «4,64 E DOIS EM CINCO NÃO VOLTA».
```

## AF.4 · Projeção — banda, se só se baixar o áudio

**FÓRMULA:** `duração × 85.000 bits/s ÷ 8` contra os bytes reais dos MP4.
**MEDIDO:** 8 Reels, **467,90 s** de áudio.

| o que se baixa | bytes | razão |
|---|---|---|
| MP4 completo (real, na balança) | **37.683.455** (35,94 MiB) | — |
| faixa `m4a` a 85 kbps (calculada) | **4.971.489** (4,74 MiB) | **7,58×** |

**HIPÓTESE:** os 85 kbps são a faixa DASH observada no Instagram; o número do
áudio é **calculado a partir da duração real**, não de um segundo download.

E a poupança **não custa qualidade**: baixar só o áudio deu transcrição
**idêntica** no teste da frente de Reels.

## AF.5 · Se um dia se pagar o X ou a tradução

| item | preço unitário | unidade | data da tabela |
|---|---|---|---|
| X API · `Posts: Read` | US$ 0,005 | recurso lido | página de 2026-07-25, obtida 2026-09-11 |
| Google Translate NMT | US$ 20,00 | 1.000.000 de caracteres | obtida 2026-09-11 |
| Google Translate LLM | US$ 10,00 + US$ 10,00 | 1M entrada + 1M saída | idem |
| DeepL | **NÃO SEI** | — | não medido |

**FÓRMULA para o X:** `posts × US$ 0,005`. Mil posts por mês = **US$ 5,00**.
O `gallery-dl` fez o mesmo objeto hoje por **US$ 0** — e com `robots.txt` a
dizer `Disallow: /`. **A decisão aqui é de política, não de preço.**

---

# AG. RISCOS

| # | risco | gravidade | evidência |
|---|---|---|---|
| 1 | **Autorização não levantada** em quatro das cinco plataformas | **ALTA** | `robots`, Termos, API oficial, política da casa e autorização do cliente: dos cinco, só `robots` foi medido |
| 2 | **Um merge cego das duas linhagens quebra o ASR** | **ALTA** | `_gavetas.py` põe 16 gavetas no `sys.path`; nome curto colide. Provado em `CONVERGENCIA-...` |
| 3 | **`hotwords` derivam a língua** | **MÉDIA-ALTA** | ES→PT medido em **S.4** |
| 4 | **Rota interna do Instagram muda sem aviso** | **ALTA** | é endpoint privado; a casa já escreveu a lei contra |
| 5 | **`SOURCE FAILURE != ZERO`** | **ALTA** | dois slugs de LinkedIn deram 404 que um contador leria como «não publica» |
| 6 | **25 runs gastaram sem registar quanto** | **MÉDIA** | e `STARTED_AT` também vem `NOT_PRESERVED` em vários |
| 7 | **80 RAW dizem `PRESERVED` e não estão na árvore** | **MÉDIA** | `.gitignore:26` + decisão D-003 — contrato, não perda |
| 8 | **`redigir()` devolve a senha intacta** | **MÉDIA** | `GUARD GAP = PROVEN` · `LIVE PASSWORD LEAK = NOT_REPRODUCED` |
| 9 | **Modo em lote do `faster-whisper` ignora os limiares** | **MÉDIA** | lido no código da versão 1.2.1 |
| 10 | **Dependência de projeto OSS que pare em silêncio** | **MÉDIA** | três bibliotecas de X já pararam: 19, 29 e 39 meses |
| 11 | **Métricas de engajamento são pagas e deitadas fora** | **BAIXA-MÉDIA** | normalizador guarda 29 campos, **nenhum** de engajamento |
| 12 | **Escolha de modelo fechada no hardware errado** | **MÉDIA** | tudo medido em 4 núcleos sem GPU |

---

# AH. O QUE PRECISA SER CONSTRUÍDO POR NÓS

Só o que **ninguém vende** — e é pouco, o que é uma boa notícia:

1. **O SCRAP ADAPTER ROUTER** com `PROVIDER_REQUESTED / PROVIDER_USED / WHY_FALLBACK / RESULT`.
2. **A declaração `COL-LAW-013`** do SCRAP como executor.
3. **O registo de `CAPABILITIES` por capacidade**, não por plataforma.
4. **A ponte de proveniência** entre o que o fornecedor devolve e `leis/artefato.py`.
5. **O contrato de armazenamento do RAW** — resolver `PRESERVED` que não está na árvore.
6. **A redação de segredo que redige mesmo.**
7. **O contrato de tradução**, se e quando houver motor.

# AI. O QUE DEVEMOS REUTILIZAR

| peça | onde já está |
|---|---|
| extração de mídia e paginação | `yt-dlp`, `gallery-dl`, `Instaloader` |
| ASR | `ferramentas/fala_local.py` — **já é dono único no HEAD** |
| cadeia Reel ponta a ponta | `ferramentas/reel_transcricao.py` |
| contrato de artefato | `leis/artefato.py` |
| portão de `robots` | `coleta/social_rotas.py:82-122` |
| matriz de rotas e `auth_mode` | `leis/social_matriz.py` |
| guarda de sessão | `guarda/social_sessao.py` |
| porta do gasto | `ferramentas/contrato_ator.py` · `coleta/coletor.py` |
| lei da tradução | `motor/v21_traducao_trava.py` + as cinco proibições |
| **o orquestrador** | `orquestrador/orquestrador.py` — **e ele não é candidato a ser absorvido** |

# AJ. O QUE DEVE SER REMOVIDO / ARQUIVADO

**Nada foi removido nesta missão.** Proposta, para o coordenador decidir:

| item | ação proposta | justificação |
|---|---|---|
| os **6 actors que nunca correram** | **ARCHIVE** | higiene de código — **não é poupança**, nunca gastaram |
| `instagram-hashtag-scraper` (órfão) | **DECIDIR** | correu, trouxe 60 itens, **não é citado em ficheiro nenhum** |
| `pintostudio~youtube-transcript-scraper` | **REPLACE** | 19/48 `FAILED`, 20 runs sem custo registado, substituto grátis provado |
| `twikit` · `twitter-api-client` · `snscrape` | **NÃO ADOTAR** | 19, 29 e 39 meses parados |
| terceiro dono de ASR (`story_transcrever.py`) | **PORT** | não apagar: a capacidade de Stories é real |

```
NÃO SE APAGA PATRIMÔNIO SEM PROVA. Seis branches carregam código que o HEAD
não tem, e nenhuma foi tocada.
```

---

# AK. CONTRATO DE FRONTEIRA SCRAP → COLLECTION — **PROPOSTA SOMENTE**

```
O ORQUESTRADOR PEDE CAPACIDADE. NUNCA PEDE FERRAMENTA.
```

| o orquestrador **PODE** dizer | o orquestrador **NUNCA** diz |
|---|---|
| «quero comunicação pública da Syngenta Itália» | «corre `yt-dlp`» |
| «escopo `INCREMENTAL`» | «usa o `activity id` 7401…» |
| «teto de custo `0`» | «usa o actor `streamers~`» |
| «preciso de fala, não só legenda» | «usa o modelo `medium`» |

O SCRAP devolve, por corrida:

```
RUN_ID · EXECUTOR_ID · EXECUTOR_VERSION · PIPELINE_VERSION
ADAPTER_USED · PROVIDER_REQUESTED · PROVIDER_USED · WHY_FALLBACK
ARTIFACT_ID · SHA256 · PARENT_ARTIFACT_ID · PARENT_SHA256 · DERIVATION_TYPE
COUNTRY_SCOPE · SOURCE_LOCATION · FACT_LOCATION
FACT_TIME · PUBLISHED_AT · OBSERVED_AT · COLLECTED_AT · DERIVED_AT
STATE · ERROR · COST_USD · COST_STATE · NOTES
```

**`COLETAR ≠ ADMITIR ≠ JULGAR`.** O SCRAP coleta. Não admite e não julga.

---

# AL. PRIMEIRA ORDEM DE IMPLEMENTAÇÃO RECOMENDADA

**Ordem por valor ÷ risco, não por dificuldade.** Ver **AS** para o detalhe.

```
1. YOUTUBE ZERO-APIFY   — 96,2% do gasto medido, substituto provado, robots mais brando
2. O ROTEADOR DE ADAPTADORES — sem ele todo o resto vira monólito
3. LINKEDIN JANELA RECENTE   — melhor mídia das cinco, custo zero, já provado
4. CONTRATO DE ARMAZENAMENTO DO RAW — 80 registos mentem hoje
5. INSTAGRAM SOB O ROTEADOR  — a cadeia existe, falta entrar pela porta certa
```

# AM. READY_FOR_IMPLEMENTATION_PHASE_1

```
YES — para a fase 1, e SOMENTE para ela.
```

**Está pronto:** a capacidade técnica do YouTube está provada; o substituto é
grátis; o gasto a evitar está medido; a arquitetura de adaptadores está
desenhada; o contrato de executor já é lei canónica.

**Não está pronto, e é honesto dizê-lo:**

| bloqueio | eixo |
|---|---|
| `PRODUCTION_AUTHORIZATION_STATUS` não levantado em nenhuma plataforma | **política** |
| `leis/social_matriz.py` não classifica a rota do `yt-dlp` | **código** |
| bytes de mídia do YouTube dão 403 daqui | **ambiente** |
| escolha final do modelo de ASR depende do hardware local | **medição** |

```
CAPACIDADE TÉCNICA PRONTA ≠ AUTORIZAÇÃO PARA PRODUÇÃO.
São dois eixos, e só um deles está fechado.
```

---

# AV. HYBRID EXECUTION MATRIX

> **`EXECUTION_TARGET` é um eixo próprio.** Não se deduz do fornecedor nem da
> plataforma. `WHY_LOCAL` é obrigatório quando o alvo é `LOCAL` ou `HYBRID`, e
> *«sempre fizemos assim»* **não é um valor aceite**.

| plataforma | capacidade | `PROVIDER` | `EXECUTION_TARGET` | `WHY_LOCAL` |
|---|---|---|---|---|
| YouTube | discovery de canal | `yt-dlp` · API | **ONLINE** | — |
| YouTube | busca | `yt-dlp` · API | **ONLINE** | — |
| YouTube | metadados e métricas | `yt-dlp` · API | **ONLINE** | — |
| YouTube | comentários | `yt-dlp` | **ONLINE** | — |
| YouTube | **legenda nativa e automática** | `yt-dlp` | **ONLINE** | — |
| YouTube | **bytes de mídia** | `yt-dlp` | **LOCAL** | `DATACENTER_BLOCKED` (403 medido) |
| LinkedIn | discovery da janela recente | HTTP próprio | **ONLINE** | — |
| LinkedIn | post direto | HTTP próprio | **ONLINE** | — |
| LinkedIn | vídeo nativo MP4 | HTTP próprio | **ONLINE** | — |
| LinkedIn | **legenda SRT automática** | HTTP próprio | **ONLINE** | — |
| LinkedIn | história profunda | **não descoberto** | **UNKNOWN** | — |
| Instagram | Reel por URL | `yt-dlp` · `Instaloader` | **EITHER** | — |
| Instagram | descoberta de perfil | HTTP próprio | **LOCAL** | `DATACENTER_BLOCKED` (302/429 e janela que esgota por IP) |
| Instagram | áudio + ASR | FFmpeg + `fala_local` | **LOCAL** | `HEAVY_MEDIA_PROCESSING` |
| Instagram | Stories | rota própria | **LOCAL** | `AUTHORIZED_LOCAL_SESSION` |
| X | post, mídia, métricas | `gallery-dl` | **ONLINE** | — |
| X | discovery de timeline | **não medido** | **UNKNOWN** | — |
| Facebook | identidade da Page | `gallery-dl` | **ONLINE** | — |
| Facebook | qualquer conteúdo | — | **UNKNOWN** | 302/400 daqui; **nunca tentado no local** |
| transversal | ASR | `fala_local` | **EITHER hoje · LOCAL se houver GPU** | `HEAVY_MEDIA_PROCESSING` |
| transversal | browser real / CDP | Playwright | **LOCAL** | `BROWSER_REAL_REQUIRED` — Chromium sem rede aqui |
| transversal | Apify | `apify_pool` | **LOCAL** | segredo ligado ao runner |

### A cadeia do Reel é híbrida, e isso não a divide em dois produtos

```
ONLINE                                 LOCAL
descoberta · identidade · metadados →  resolução e download da mídia
                                       áudio (FFmpeg) · VAD · ASR
                                       ↓
                                    transcript
```

**Ou corre inteira online, se tecnicamente bastar.** Hoje, neste contentor, a
cadeia do Reel correu **inteira online** — 8 Reels capturados e transcritos sem
tocar no runner local. `EXECUTION_TARGET = EITHER` não é uma dúvida: é a
resposta medida.

---

# AW. LOCAL GPU ASR — ESTADO REAL

## AW.1 · O estado, em uma linha, e ele contraria a suposição herdada

```
A CASA NÃO CORRE ASR EM GPU. NÃO É «NÃO ESTÁ A USAR» — É QUE NÃO EXISTE
CAMINHO DE CÓDIGO QUE POSSA USAR. O DISPOSITIVO ESTÁ CRAVADO EM `cpu`.
```

**COMANDO:** busca literal em todo o `.py` do HEAD, fora de `site-packages`.

| termo procurado | ocorrências |
|---|---|
| `device="cuda"` · `device='cuda'` | **0** |
| `torch.cuda` | **0** |
| `CUDA` | **0** |
| `whisper.cpp` | **0** |
| `openai-whisper` · `openai.audio` · `audio.transcriptions` | **0** |
| `device='cpu'` | **1** — `ferramentas/fala_local.py:222` |
| `compute_type` | **1** — mesma linha |
| `WhisperModel(` | **2** — uma real, uma dentro de um teste que a proíbe |

A linha inteira, que é toda a configuração de hardware do ASR desta casa:

```python
m = WhisperModel(nome, device='cpu', compute_type='int8', cpu_threads=nucleos())
```

**Não há parâmetro de dispositivo. Não há variável de ambiente. Não há
fallback.** `cpu` não é o plano B: é o único plano.

## AW.2 · Os sete campos, separados como pedido

| campo | valor real, medido |
|---|---|
| `ASR_ENGINE` | **faster-whisper** `1.2.1` |
| `ASR_MODEL` | família **Whisper**, pesos `small` / `medium` / (medido) `large-v3-turbo` |
| `ASR_RUNTIME` | **CTranslate2** `4.8.2` |
| `EXECUTION_ENVIRONMENT` | **ONLINE** hoje (este contentor) |
| `ACCELERATOR` | **NENHUM** |
| `DEVICE` | **`cpu`**, cravado |
| `PRECISION` | **`int8`**, cravada |

**E a distinção que o coordenador pediu, escrita em claro:**

```
OpenAI Whisper/API   ≠   modelo da família Whisper   ≠   faster-whisper
                     ≠   whisper.cpp                 ≠   GPU
```

A casa usa **pesos da família Whisper**, servidos pelo **motor faster-whisper**
sobre o **runtime CTranslate2**, em **CPU**. **Não usa a API da OpenAI** —
zero chamadas. **Não usa whisper.cpp** — não está instalado. **Não usa GPU** —
nem sequer sabe pedir uma.

## AW.3 · Census de todos os caminhos mídia → ASR

| `ENTRYPOINT` | `ASR_OWNER` | `LIBRARY` | `MODEL` | `DEVICE` | `PRECISION` | GPU? | lote? | VAD? | idioma | tempos? |
|---|---|---|---|---|---|---|---|---|---|---|
| `ferramentas/fala_local.py` | **ele próprio** | `faster_whisper` | `small` (env) | **`cpu`** | `int8` | **NÃO** | **SIM**, 8 | SIM | **DECLARADO**, detecta se ausente | disponível, **desligado** |
| `ferramentas/reel_transcricao.py` | delega | — | **`medium`** (env) | herda | herda | NÃO | SIM | SIM | declarado | não |
| `ferramentas/instagram_transcrever.py` | delega | — | `small` (`IG_MODELO`) | herda | herda | NÃO | SIM | SIM | declarado | não |
| `ferramentas/youtube_transcrever.py` | delega | — | `small` (`YT_MODELO`) | herda | herda | NÃO | SIM | SIM | país → idioma | não |
| `coleta/comunicacao_coleta.py` | delega | — | via cadeia do Reel | herda | herda | NÃO | SIM | SIM | declarado | não |
| **`ferramentas/story_transcrever.py`** *(fora do HEAD)* | **motor próprio** | `faster_whisper` | `small` (`STORY_MODELO`) | **`cpu`** | `int8` | **NÃO** | **NÃO** — sequencial | SIM | **NUNCA declarado** | não |

`DUPLICATE OWNERS` — **no HEAD: 1.** **No universo: 2.** O segundo vive em
`origin/claude/sintonia-scrap-stories-no-apify-v1` e **não é uma cópia
inofensiva**: usa `beam_size=5` onde o dono usa `1`, corre **sequencial** onde o
dono corre em lote, e **nunca declara o idioma**. Um merge que escolhesse o
ficheiro errado mudaria resultado, custo e tempo de uma vez só.

> **E há um defeito que só apareceu ao ler os dois lados.** `story_transcrever.
> anexar()` exige `objeto_story['MEDIA_DURABILITY'] == 'MEDIA_PRESERVED'` e lê
> `objeto_story['MEDIA_PATH']`. **Esses dois nomes não são escritos por ficheiro
> nenhum da branch** — confirmado por mim, `git grep` na própria branch devolve
> só as duas linhas de dentro do `story_transcrever.py`. A cadeia escreve
> `MEDIA_URL_DURABILITY`, `AUDIO_STATE` e `AUDIO_PATH`.
>
> **Consequência medida por leitura:** `anexar()` devolveria `MEDIA_MISSING` em
> **100%** dos objetos que a própria cadeia produz. O terceiro dono de ASR não
> está só duplicado — está **ligado a um contrato que não existe**.
>
> **NÃO FOI CORRIGIDO.** Corrigir era convergir, e convergir estava proibido.

## AW.4 · Desempenho medido — e onde ele **não** vale

Tabela completa em **S.2**. O essencial: `rtf` entre **2,56× e 7,66×** conforme
o modelo, em **CPU, 4 núcleos, `int8`, sem GPU**.

| medida pedida | estado |
|---|---|
| `real-time factor` | **MEDIDO** — S.2 |
| `seconds processed / second` | **MEDIDO** — é o mesmo número |
| **`VRAM`** | **NOT_MEASURED** — não há GPU aqui |
| `RAM` | **NOT_MEASURED** |
| **`GPU utilization`** | **NOT_MEASURED** — não há GPU aqui |
| `accuracy` · termos agronómicos · nomes próprios | **MEDIDO** — S.3 |
| `timestamps` | **MEDIDO** — S.5, custo nulo ou negativo |
| `language detection` | **PARCIAL** — o dono declara o idioma por omissão; a deteção existe e foi medida como **risco** (S.4) |
| silêncio / música | **MEDIDO** — é o caso do `'...'`, S.6 |
| `batch throughput` | **MEDIDO** — lote 8 contra sequencial |

## AW.5 · `LOCAL_HARDWARE_STATUS`

```
LOCAL_HARDWARE_STATUS = NOT_MEASURED
```

**Nesta missão o runner local nunca foi alcançado.** Não há CPU, RAM, GPU,
VRAM, versão de CUDA, driver, SO nem disco medidos.

> **O que existe é uma afirmação herdada, e ela fica marcada como afirmação.**
> Um comentário em `ferramentas/fala_local.py:32` diz *«na máquina de 16,
> declarar os núcleos deu ~4x»*. Isso indica **16 núcleos de CPU** no runner —
> **não diz nada sobre GPU**. É memória de outra missão, escrita em prosa.
> **Não é medição desta.**

Antes de fechar qualquer escolha de motor ou modelo, medir lá: `CPU · RAM ·
GPU · VRAM · CUDA · driver · SO · disco`.

## AW.6 · Custo de ASR — e local **não** é zero

```
LOCAL_GPU_ASR  ≠  CUSTO ZERO.  É CUSTO QUE NÃO APARECE NA FATURA.
```

| parcela | estado |
|---|---|
| hardware já existente | **já pago** — não entra como custo marginal |
| **energia** | **NOT_MEASURED** — e **não vai ser inventada** |
| tempo de GPU | **NOT_MEASURED** — não há GPU aqui |
| tempo de CPU | **MEDIDO** — ver AF.3 |
| manutenção | **NOT_MEASURED** |
| armazenamento e banda | **MEDIDO em parte** — AF.4 |
| `throughput` | **MEDIDO** — S.2 |

Contra `CLOUD_ASR`: a única rota de nuvem medida é a paga da Apify, que deu
**5 de 20 itens vazios** e **19 de 48 runs `FAILED`**. `US$ 0,004643` por item,
piso.

---

# AX. NATIVE CAPTION VS LOCAL GPU ASR

> **Lei de eficiência candidata, e a palavra `TRUSTWORTHY` faz todo o trabalho:**
>
> ```
> LEGENDA NATIVA CONFIÁVEL E SUFICIENTE  →  USAR
>                     ↓ senão
>                  ÁUDIO  →  ASR PRÓPRIO
> ```

| plataforma | legenda nativa? | qualidade | tempos? | ASR próprio necessário? | porquê |
|---|---|---|---|---|---|
| **YouTube** | **SIM** — manual **e** automática | **NOT_MEASURED** — obtida, não conferida contra o áudio | **SIM** (VTT) | **NÃO**, quando existe | o texto já está escrito; gastar máquina para o reescrever é pagar duas vezes |
| **LinkedIn** | **SIM** — **SRT automática** | **NOT_MEASURED** | **SIM** | **provavelmente NÃO** | mas ver o aviso abaixo |
| **Instagram** | **NÃO** | — | — | **SIM, indispensável** | não há de onde tirar texto de fala |
| **X** | **SIM, mas** | a do vídeo testado diz *«could not transcribe the audio»* | SIM (VTT) | **SIM, como recurso** | a legenda existe e vem **vazia** |
| **Facebook** | **UNKNOWN** | — | — | **UNKNOWN** | nada foi alcançado |

### O aviso que muda a leitura, e é uma correção minha

> Escrevi antes que o LinkedIn servia **WebVTT nativo**. Errado em dois pontos.
> **O formato é SRT** (numeração e vírgula decimal, verificado nos bytes). E a
> URL diz o que ela é: `.../video-auto-caption-srt-acs-singleton/...` —
> **legenda automática**, isto é, **ASR de outra casa**.
>
> Isso não a desqualifica. Torna-a **barata**, não **confiável**. Uma legenda de
> máquina erra nas mesmas coisas onde a nossa erra: termo agronómico e nome de
> marca — exatamente onde o `small` escreveu `MICE` por `mais` e `disingenta`
> por `Syngenta`.

```
«USAR A LEGENDA NATIVA QUANDO ELA FOR BOA» EXIGE MEDIR SE ELA É BOA.
Ninguém mediu ainda. Até lá, a regra correta é: usar, E GUARDAR DE ONDE VEIO.
```

**Teste que fecha isto, e não foi executado:** pegar num vídeo com legenda
automática **e** áudio, transcrever com o ASR da casa, e comparar os dois textos
no léxico agronómico declarado. É barato. Está em **AS**.

E há um campo que o contrato já exige e que resolve o problema sem escolher
lado: `TEXT_KIND`. `CAPTION` é texto do autor. `TRANSCRIPT` é fala reconhecida.
Falta o terceiro valor — **`NATIVE_CAPTION`** — para não misturar o ASR deles
com o nosso.

---

# AY. ONLINE ↔ LOCAL HANDOFF — **PROPOSTA, NÃO IMPLEMENTADA**

O problema: um trabalho começa online (descoberta, identidade, metadados) e
precisa de continuar no runner local (mídia pesada, GPU, browser real) **sem
perder a linha da prova e sem criar um segundo cérebro**.

```
A PASSAGEM NÃO É UMA ORDEM. É UM ENVELOPE.
Quem passa não manda. Quem recebe não decide o que coletar.
```

### O que o envelope carrega — e por que cada campo

| campo | por que não pode faltar |
|---|---|
| `RUN_ID` | as duas metades são **uma corrida**, não duas |
| **`RAW_OBSERVATION_ID`** | é `raw_asset.id` — **a chave da passagem**. Identifica a **observação**, não os bytes |
| `SOURCE_ID` | de onde veio, sem inventar |
| `SHA256` | **integridade dos bytes, e só isso.** Não identifica a observação |
| `storage_path` | endereça o **objeto físico**. Não endereça a observação |
| `PROVENANCE` | `SOURCE_LOCATION` · `FACT_LOCATION` · `FACT_TIME` · `PUBLISHED_AT` · `OBSERVED_AT` · `COLLECTED_AT` |
| `STATE` | onde a metade online parou |
| `TRACE` | degraus, `PROVIDER_REQUESTED`, `PROVIDER_USED`, `WHY_FALLBACK`, hora, custo |

### A forma, em três passos e nenhum cérebro novo

```
1. ONLINE   grava o artefato RAW e um pedido de derivação PENDENTE,
            chaveado por RAW_OBSERVATION_ID. Não escolhe modelo, não escolhe GPU.

2. LOCAL    lê o pendente, faz o trabalho pesado, e grava o DERIVED com
            PARENT_ARTIFACT_ID + PARENT_SHA256 + DERIVATION_TYPE.
            O dono de ASR decide runtime/modelo/dispositivo — o adaptador NÃO.

3. AMBOS    escrevem TRACE sob o MESMO RUN_ID. O orquestrador vê UMA corrida.
```

**Por que isto não cria um segundo orquestrador:** o pendente é **estado do
executor**, e `COL-LAW-016` já diz que estado incremental pertence ao executor.
O orquestrador continua a conhecer três escopos — `PONTUAL` · `INCREMENTAL` ·
`TOTAL` — e mais nada. Ele **não sabe** que houve duas máquinas, e não precisa
de saber.

**O que falha se o desenho estiver errado:** se a chave da passagem fosse o
`SHA256`, dois vídeos idênticos publicados por contas diferentes colapsariam
numa observação só. Se fosse o `storage_path`, mover um ficheiro apagaria a
observação. **É por isso que a chave é `RAW_OBSERVATION_ID`.**

### O que o adaptador pede, e o que ele nunca pede

```
O ADAPTADOR PEDE:    TRANSCRIBE(audio)
O ADAPTADOR NUNCA:   escolhe modelo · escolhe dispositivo · escolhe precisão
```

O dono de ASR decide, por política e configuração medida. **Isto não foi
implementado.** Hoje três pontos de entrada escolhem modelo por conta própria,
via `IG_MODELO`, `YT_MODELO` e `SINTONIA_REEL_MODELO`. Fica na matriz de
convergência como `REFINE`.

---

# AN. MAPA DAS DUAS LINHAGENS

Mapa completo, com comparação `md5` ficheiro a ficheiro, em
`CONVERGENCIA-DAS-DUAS-LINHAGENS-V1.md`. As duas linhagens:

| linhagem | o que trouxe |
|---|---|
| **SCRAP** (6 branches) | roteador de rotas, matriz de plataformas, portão de `robots`, guarda de sessão, Stories, contrato de ator |
| **REELS** (HEAD) | dono único de ASR, cadeia Reel ponta a ponta, contrato de artefato aplicado, 47 testes |

```
A FRENTE DE REELS CONSTRUIU UMA SEGUNDA CADEIA SEM SABER QUE A PRIMEIRA
EXISTIA. Nenhuma das duas está errada. Nenhuma das duas está completa.
```

# AO. CONVERGÊNCIA PROPOSTA — **NENHUMA EXECUTADA**

Seis linhas, com ação declarada, em `CONVERGENCIA-...§AO`:

| linha | ação |
|---|---|
| o que já está resolvido no HEAD | **KEEP** |
| o ASR — um dono, e ele já existe | **PORT** (trazer Stories para o dono) |
| a segurança (`redigir`) | **PORT** |
| o lugar do fato | **REFINE** — resolver **antes** de qualquer merge |
| Stories | **KEEP a capacidade · REFINE o contrato quebrado** (ver AW.3) |
| o roteador | **REFINE** — a cadeia de Reels tem de entrar por ele |

> **E o risco que um merge cego dispara, provado:** `_gavetas.py` põe 16 gavetas
> no `sys.path`. Dois ficheiros com o mesmo nome curto em gavetas diferentes
> colidem, e **quem ganha depende da ordem**. Um merge que traga
> `story_transcrever.py` sem ler isto pode trocar o motor de ASR sem que
> nenhuma linha de `import` mude de aspeto.

# AP. DISCOVERY VS DIRECT CAPTURE

Matriz completa em `AP-DISCOVERY-VS-CAPTURA-V1.md`.

```
DESCOBRIR É O MURO. BUSCAR, NÃO. — em três das quatro plataformas medidas.
No YouTube é ao contrário: descobrir é livre, e o que barra é o byte da mídia.
```

# AQ. TECHNICAL CAPABILITY VS POLICY / AUTHORIZATION

> **Três eixos independentes. Um não decide o outro.**

```
TECHNICAL_CAPABILITY          consegue?           — engenharia responde
PLATFORM_POLICY_STATUS        a plataforma diz o quê?  — leitura de documento
PRODUCTION_AUTHORIZATION      podemos, em produção?    — NÃO É DECISÃO DE ENGENHARIA
```

E **cinco evidências separadas**, que não se somam numa só:

| evidência | estado hoje, em **todas** as plataformas |
|---|---|
| `ROBOTS_STATUS` | **MEDIDO** — `DISALLOW_ALL` em IG, LI, FB, **X**; `RESTRICTED` no YouTube |
| `TERMS_STATUS` | **NÃO LEVANTADO** |
| `OFFICIAL_API_STATUS` | **PARCIAL** — só YouTube e X têm rota oficial identificada |
| `HOUSE_POLICY_STATUS` | **PARCIAL** — existe lei escrita para a rota interna do Instagram |
| `CLIENT_AUTHORIZATION_STATUS` | **NÃO LEVANTADO** |

```
ROBOTS.TXT NÃO É PARECER JURÍDICO. É UM DOS CINCO DOCUMENTOS, E É O ÚNICO
QUE FOI MEDIDO. Transformar um em veredicto foi erro meu, corrigido.
```

Onde houver dúvida, o valor é `REQUIRES_LEGAL/CLIENT_REVIEW` — **não** é
`NO`, e **não** é `YES`.

# AR. MEDIA STRATEGY — `TRANSCRIPTION_ONLY` vs `EVIDENCE_CAPTURE`

Detalhe em `CONVERGENCIA-...§AR`. As duas estratégias, e são **escolha
declarada**, não otimização silenciosa:

| estratégia | o que baixa | banda | serve para | **não** serve para |
|---|---|---|---|---|
| `TRANSCRIPTION_ONLY` | só a faixa de áudio | **7,58× menos** | ouvir, classificar, ligar à inteligência | provar o que estava no ecrã |
| `EVIDENCE_CAPTURE` | o objeto de vídeo | referência | prova visual, auditoria, contraditório | — |

```
ÁUDIO SÓ NÃO É VÍDEO CRU. Transcrição idêntica não significa evidência
equivalente. Quem escolher `TRANSCRIPTION_ONLY` está a decidir que não vai
poder mostrar a imagem depois.
```

# AS. TOP 5 PRÓXIMAS IMPLEMENTAÇÕES — **NENHUMA EXECUTADA**

Ordenadas por **valor ÷ risco**, com dependência e necessidade arquitetural
declaradas.

### 1 · YouTube sem Apify

| | |
|---|---|
| **VALOR** | **≥ US$ 12,33 dos ≥ US$ 12,81** medidos — 96,2% do gasto |
| **RISCO** | **BAIXO** em capacidade · **ABERTO** em política (`robots` `RESTRICTED`) |
| **POUPANÇA** | a maior de todas, e é a única já quantificada |
| **DEPENDÊNCIAS** | classificar a rota `yt-dlp` em `leis/social_matriz.py` |
| **NECESSIDADE ARQUITETURAL** | **não** — é substituição de rota |

### 2 · O SCRAP ADAPTER ROUTER

| | |
|---|---|
| **VALOR** | sem ele, cada plataforma nova vira mais um `if` ou mais um produto |
| **RISCO** | **MÉDIO** — toca código vivo de duas linhagens |
| **POUPANÇA** | indireta: evita o monólito antes de ele nascer |
| **DEPENDÊNCIAS** | decidir a convergência (**AO**) primeiro |
| **NECESSIDADE ARQUITETURAL** | **SIM — é a peça que não dá para adiar** |

### 3 · LinkedIn na janela recente

| | |
|---|---|
| **VALOR** | a melhor mídia das cinco plataformas, a custo **zero**, já provada |
| **RISCO** | **BAIXO** em capacidade · **ABERTO** em política |
| **POUPANÇA** | US$ 0,484 medidos, mas o valor real é o material, não o preço |
| **DEPENDÊNCIAS** | o coordenador decidir **quanta história** o SINTONIA precisa |
| **NECESSIDADE ARQUITETURAL** | não |

### 4 · Contrato de armazenamento do RAW

| | |
|---|---|
| **VALOR** | **80 registos dizem `PRESERVED` e o ficheiro não está na árvore** |
| **RISCO** | **BAIXO** de implementar · **ALTO** de não implementar |
| **POUPANÇA** | nenhuma em dinheiro. Evita perder a prova, que vale mais |
| **DEPENDÊNCIAS** | nenhuma técnica; é decisão de onde o RAW vive |
| **NECESSIDADE ARQUITETURAL** | **SIM** — sem isto o handoff de **AY** não fecha |

### 5 · Medir a legenda nativa contra o nosso ASR

| | |
|---|---|
| **VALOR** | decide se a GPU local é necessária ou desperdício em duas plataformas |
| **RISCO** | **NENHUM** — é medição, não muda código |
| **POUPANÇA** | potencialmente **toda** a hora de máquina de YouTube e LinkedIn |
| **DEPENDÊNCIAS** | um vídeo com legenda automática **e** áudio. Já temos |
| **NECESSIDADE ARQUITETURAL** | não — mas responde à lei de eficiência de **AX** |

```
A NÚMERO 5 É A MAIS BARATA DA LISTA E PODE TORNAR A NÚMERO 1 AINDA MAIOR.
Ninguém a fez porque ninguém perguntou se a legenda deles presta.
```

# AT. CONTRACT DO SINTONIA SCRAP COMO EXECUTOR

`COL-LAW-013`, já canónica. Mapeamento verbo a verbo em **AD.4** e detalhe em
`CONVERGENCIA-...§AT`.

# AU. FRONTEIRA EXPLÍCITA COM O ORQUESTRADOR CANÔNICO

| fica **acima** do SCRAP | fica **dentro** do SCRAP |
|---|---|
| o pedido de coleta | o adaptador de plataforma |
| a receita e a política de rota | o fornecedor e os degraus |
| o escopo `PONTUAL`/`INCREMENTAL`/`TOTAL` | o cursor de cada fonte |
| o teto de custo | o registo do custo gasto |
| a decisão de admitir | a entrega do RAW |
| **a escolha do executor** | **a escolha do ambiente de execução** |

```
`orquestrador/orquestrador.py` NÃO É CANDIDATO A SER ABSORVIDO PELO SCRAP.
Ele está ACIMA do SCRAP. COL-LAW-011, e não se reabre sem contraexemplo.
```

---

# AS 17 DECISÕES QUE O COORDENADOR TEM DE TOMAR

Nenhuma destas é de engenharia. Estão aqui porque medi o suficiente para as
formular, e **não** o suficiente para as responder.

| # | decisão | o que já está medido |
|---|---|---|
| 1 | Levantar `TERMS_STATUS` e `CLIENT_AUTHORIZATION_STATUS`? | zero das cinco plataformas |
| 2 | YouTube sem Apify entra em produção? | capacidade **PROVEN**, `robots` `RESTRICTED` |
| 3 | Quanta **história** de LinkedIn o SINTONIA precisa? | janela recente **PROVEN** e grátis; história **UNKNOWN** |
| 4 | Usar a rota interna do Instagram? | funciona; **contra lei escrita da casa** |
| 5 | `TRANSCRIPTION_ONLY` ou `EVIDENCE_CAPTURE` por plataforma? | 7,58× de banda de diferença |
| 6 | Guardar métricas de engajamento? | pagamos por elas e o normalizador deita-as fora |
| 7 | Onde vive o RAW preservado? | 80 registos dizem `PRESERVED` e não estão na árvore |
| 8 | Aposentar os 6 actors que nunca correram? | higiene, **não** poupança |
| 9 | O que fazer com o actor órfão de hashtag? | correu, 60 itens, **não citado em código nenhum** |
| 10 | Adotar `hotwords`? | **+termos, −integridade de língua** (ES derivou para PT) |
| 11 | Trocar `medium` por `large-v3-turbo`? | corrige `granella`, **estraga** `Syngenta` em ES |
| 12 | Comprar GPU / usar a do runner local? | **a casa não tem código que saiba pedir GPU** |
| 13 | Usar legenda nativa em vez de ASR? | existe em YT, LI e X; **qualidade nunca medida** |
| 14 | Adotar `gallery-dl` para X? | **PROVEN** hoje; `robots` do X é `Disallow: /` |
| 15 | Pagar a API do X? | US$ 0,005 por post; o grátis fez o mesmo hoje |
| 16 | Autorizar sessão local para Stories? | é a única rota; esbarra em lei da casa |
| 17 | Quando convergir as duas linhagens? | **matriz pronta, nada executado** |

---

# FECHAMENTO EM LINGUAGEM SIMPLES

**1. O que já tínhamos funcionando?**
Mais do que se pensava. Já existia um SINTONIA SCRAP com roteador de rotas,
matriz de plataformas e um portão que lê o `robots.txt` antes de bater à porta.
E, em paralelo, uma cadeia nova que pega num Reel, tira o som e escreve o que
foi dito. **As duas existiam ao mesmo tempo e não se conheciam.**

**2. O que dessa auditoria anterior realmente continua funcionando?**
Quase tudo — mas duas afirmações caíram quando as refiz, e **uma delas era
minha**. Eu tinha escrito que a descoberta do LinkedIn estava bloqueada. Não
está. Está **rasa**: vê os posts recentes e não sabe ir mais fundo. E as duas
páginas que «não publicavam nada» eram **dois endereços escritos errados** — o
LinkedIn respondia 404, e quem só contasse posts leria «empresa calada».

**3. O que ainda depende de Apify?**
Facebook inteiro, comentários do Instagram, Stories, e a história antiga do
LinkedIn. **O resto tem substituto grátis já provado.**

**4. Conseguimos tirar Apify do Instagram?**
**Para pegar um Reel pelo endereço, sim** — e com **duas** ferramentas
diferentes, o que é bom: se uma parar, a outra continua. **Para descobrir o que
uma conta publicou, ainda não** deste computador.

**5. Conseguimos pegar e ouvir Reels?**
**Sim, e já está feito.** Oito Reels baixados, ouvidos e escritos, em quatro
idiomas, com registo de quem foi o pai de cada texto.

**6. Conseguimos tirar Apify do LinkedIn?**
**Para o que foi publicado há pouco tempo, sim, e custa zero.** Para a história
antiga, ninguém sabe ainda.

**7. Conseguimos pegar vídeos nativos do LinkedIn?**
**Sim — é o mais fácil das cinco plataformas.** Vídeo normal, três qualidades,
sem entrar em conta nenhuma. E vem com legenda ao lado.

**8. Como esses vídeos serão transcritos e traduzidos?**
Transcritos, já sabemos: o computador ouve e escreve. **Traduzidos, não** — a
casa **não tem tradutor nenhum**. Tem só a **lei** de como uma tradução se
comporta: não inventar número, não tirar a dúvida, não mudar o lugar. A lei
está pronta há muito tempo. A máquina não existe.

**9. O que vai rodar no PC local?**
O trabalho pesado: baixar vídeo grande, tirar o som, ouvir, e as portas que
exigem um navegador de verdade. **O resto fica online, porque é mais barato.**
E uma surpresa: **o computador da casa não sabe usar placa de vídeo.** Não é
que esteja desligada — é que a palavra «GPU» não aparece em lugar nenhum do
código. Está tudo cravado em processador comum.

**10. Quais peças vamos pegar prontas do open source?**
Três, e todas vivas: `yt-dlp` (lançado há 23 dias), `gallery-dl` (há 7) e
`Instaloader`. Mais o `FFmpeg` para o som e o `faster-whisper` para ouvir.

**11. Quais peças teremos que construir?**
Só o que ninguém vende: **o registo de onde cada coisa veio**. Qual ferramenta
foi pedida, qual respondeu, por que a primeira falhou, e quem é o pai de cada
texto. É pouco código e é a parte que faz a diferença entre prova e palpite.

**12. Qual deve ser a ordem da implementação?**
Primeiro o YouTube, que é onde está quase todo o dinheiro. Depois o roteador,
que impede a bagunça de nascer. Depois o LinkedIn recente, que é de graça.
Depois arrumar onde os arquivos ficam guardados. E, antes de comprar qualquer
placa de vídeo, **fazer o teste mais barato da lista**: comparar a legenda que
a plataforma já dá com a que o nosso computador escreve. Se a delas prestar,
metade do trabalho pesado **deixa de existir**.

---

# HARD STOP

```
NADA FOI IMPLEMENTADO.      NENHUMA BRANCH FOI FUNDIDA.
NENHUM ACTOR FOI DESLIGADO. NENHUM MODELO FOI TROCADO.
NENHUM DEFAULT FOI ALTERADO. NENHUM PIPELINE VIVO FOI MEXIDO.
COLLECTION, MIGRATIONS, BANCO LIVE, PORTAL, CASCO E DEPLOY: INTOCADOS.
```

## Nota de procedência sobre os agentes

Dez agentes de medição correram nesta missão. **Nenhum resultado entrou neste
documento como verdade automática.** Cada afirmação carregada para cá foi
refeita por mim contra a fonte primária, e as que não sobreviveram estão
escritas como correção, não apagadas.

> **Um dos dez — o de Instagram — foi assinalado pela plataforma com aviso de
> segurança (`Exfil Scouting`).** Por precaução, **nenhuma conclusão sua foi
> usada**. Tudo o que este documento diz sobre Instagram foi medido por mim:
> os 8 Reels em `data/raw/REEL-MIDIA/`, os 302/429 da listagem de perfil, a
> janela que esgota, e os dois fornecedores de captura.
