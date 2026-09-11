# AP · DESCOBRIR ≠ BUSCAR — a matriz por plataforma

> **MEDIDO_EM:** 2026-09-10/11, deste runner: Ubuntu 24.04, IP de **datacenter**, sem GPU,
> **sem login, sem cookies, sem Apify, sem browser** (o Chromium não alcança rede aqui).
>
> **A distinção que organiza tudo:**
> **DISCOVERY** = sair de uma conta/consulta e chegar às URLs de conteúdo.
> **DIRECT CAPTURE** = já ter a URL e obter o objeto.
> São capacidades diferentes, quebram em sítios diferentes, e confundi-las foi o erro que
> esta missão passou a semana a desfazer.

---

## O PADRÃO QUE APARECEU EM TRÊS DAS QUATRO

```
DESCOBRIR É O MURO. BUSCAR, NÃO.
```

Instagram, LinkedIn e (parcialmente) Facebook repetem a mesma forma: a **listagem** pede
sessão; o **objeto individual**, com o endereço em mãos, responde a convidado. O YouTube é
o contrário — descobrir é livre e o que barra é o **byte da mídia**.

---

## A MATRIZ

Legenda: **PROVEN** medido hoje · **PARTIAL** funciona com teto · **BLOCKED** medido e
recusado · **UNKNOWN** não medido · **NOT_EXECUTED** não tentado.

| | INSTAGRAM | LINKEDIN | YOUTUBE | FACEBOOK |
|---|---|---|---|---|
| **DISCOVERY** | **PARTIAL** | **PROVEN, raso** | **PROVEN** | **PARTIAL** |
| perfil / página | BLOCKED (302 login · 429) | landing 200, 11 activity ids | canal via `yt-dlp` + API | identidade via `gallery-dl` |
| listagem de posts | via `/api/v1/feed/user/<PK>/` ⚠️ | aba `/posts/` → 302 login | `--flat-playlist` | 302 login |
| busca | UNKNOWN | UNKNOWN | `ytsearch` · `search.list` | BLOCKED |
| paginação / histórico | esgota por IP em ~8-10 respostas | **sem URL de página seguinte** | PROVEN | UNKNOWN |
| **DIRECT CAPTURE** | **PROVEN** | **PROVEN** | **PROVEN** (metadados) | **BLOCKED** |
| post / objeto | `yt-dlp` por URL | HTTP 200 + `<video data-sources>` | `yt-dlp --print` | BLOCKED |
| **MEDIA** | **PROVEN** | **PROVEN** | **BLOCKED (403)** | **BLOCKED** |
| formato | DASH separado: vídeo + **áudio m4a 85k** | **3 MP4 progressivos** | — | — |
| durabilidade da URL | `TEMPORARY` (CDN assinada, morre em horas) | **`LONG_LIVED_OBSERVED`** (`e=2147483647`) | UNKNOWN | UNKNOWN |
| **TRANSCRIPT** | ASR próprio | **legenda nativa WebVTT** | **legenda nativa + automática** | BLOCKED |
| custo do transcript | tempo de máquina | **zero — já vem escrito** | **zero — já vem escrito** | — |
| **CAPTION** (texto do autor) | PROVEN | PROVEN | PROVEN | BLOCKED |
| **COMMENTS** | BLOCKED | UNKNOWN | **PROVEN** (`--write-comments`) | BLOCKED |
| **MÉTRICAS** | likes PROVEN · views UNKNOWN | `like_count` PROVEN | PROVEN | BLOCKED |
| **IDENTIDADE** | shortcode + PK numérico | **`urn:li:activity:<id>`** | videoId / channelId | fbid / album id |
| **STORIES** | BLOCKED (nenhuma rota anónima) | n/a | n/a | n/a |

⚠️ A rota `/api/v1/feed/user/<PK>/` com header `X-IG-App-ID` é um **endpoint interno**. A
própria casa já escreveu a lei contra chamá-lo à mão, em `coleta/story_local.py`:

> *«Endereço interno muda sem aviso e sem versão, e no dia em que mudar, o nosso pedido
> devolve vazio — que se lê como "a conta não tem Story". […] **NÃO PEDIR NADA QUE A PÁGINA
> JÁ NÃO FOSSE PEDIR.**»*

Fica registada como **medida**, não como recomendada: `TECHNICAL_CAPABILITY = PARTIAL`,
`HOUSE_POLICY_STATUS = CONTRA LEI ESCRITA`, `PRODUCTION_AUTHORIZATION = NOT_AUTHORIZED`.

---

## O QUE CADA PLATAFORMA ENSINA

### YouTube — o inverso de todos os outros

Descobrir, metadados, comentários e **legendas** saíram todos de graça hoje. O que **não**
saiu foi o byte de mídia: `403` deste IP. E é a única das cinco cujo `robots.txt` não é
bloqueio total — barra `/youtubei/`, `/results`, `/comment`, `/get_video`, e deixa `/watch`
e `/channel`.

```
NO YOUTUBE A LEGENDA JÁ EXISTE. Transcrever com ASR o que a plataforma já escreveu
é pagar hora de máquina por texto que estava à mão.
```

### LinkedIn — o melhor material, o teto mais baixo

É a única plataforma onde a mídia é **MP4 progressivo com URL `LONG_LIVED_OBSERVED`** e a
legenda vem em **WebVTT com timestamps**. A cadeia fecha sem login, sem browser e sem
Apify. O teto é a **profundidade**: 11 activity ids na landing e nenhuma URL de página
seguinte.

### Instagram — o único onde o ASR é mesmo necessário

Não há legenda nativa. O `caption` é do autor, não é a fala. Por isso é aqui — e só aqui —
que a cadeia de ASR que a frente anterior construiu é indispensável.

E é aqui que está a poupança medida: a faixa de áudio vem **separada** (DASH `m4a` 85 kbps),
e baixar só ela deu transcrição **idêntica** por **⅕ da banda**.

### Facebook — o muro mais alto

`gallery-dl` deslogado dá **identidade e endereços** (id da Page, fbid, álbuns, URL
canónica). **Todo o conteúdo está bloqueado** deste IP: texto, imagem, vídeo, Reels,
comentários, métricas. Nenhum objeto foi capturado.

---

## O DEFEITO TRANSVERSAL QUE APARECEU AO MEDIR FACEBOOK

O normalizador de comunicação pública guarda **29 campos**, e **nenhuma métrica de
engajamento**:

```
POST_ID · ACCOUNT_ID · ACCOUNT_URL · COMPANY · COUNTRY_SCOPE · ACCOUNT_SCOPE · PLATFORM
PUBLISHED_AT · FIRST_OBSERVED · LAST_OBSERVED · URL · TITLE · TEXT · TEXT_KIND
MEDIA_TYPE · MEDIA_URL_TEMPORARY · MEDIA_DURATION_S · IS_VIDEO
TRANSCRIPT_TEXT · TRANSCRIPT_STATE · COLLECTION_WINDOW_DAYS · COLLECTION_WINDOW_FROM
DATASET_OWNER · COLLECTION_RUN_ID · RAW_REFERENCE · RAW_COMPLETENESS · ACTOR
MISSION · RUNNER_NAME
```

Verificado: `grep` por `LIKE|COMMENT|SHARE|VIEW|PLAY` no normalizador devolve **zero**.

> As rotas pagas devolvem `likeCount`, `videoPlayCount`, `commentCount` — e o normalizador
> **deita-os fora**. Pagamos por campos que não guardamos.

Isto **pode** ser deliberado: o classificador tem a lei *«o que esta camada nunca diz: nem
venda, nem demanda, nem participação de mercado»*. Mas métrica de engajamento não é venda,
e o RAW preservado já as contém. Fica como **pergunta ao coordenador**, não como defeito
declarado: *guardar ou não guardar métricas é decisão de produto, e ninguém a tomou por
escrito.*

---

## O QUE SÓ O RUNNER LOCAL PODE FECHAR

Nenhum destes é contornável com engenharia deste lado. Todos precisam de IP residencial,
Chrome real ou sessão própria — e os dois últimos esbarram em
`LOCAL_SESSION contra TERCEIRO = NOT_USABLE`, que é lei desta casa.

| teste | plataforma | porquê aqui não |
|---|---|---|
| repetir `/api/v1/feed/user/<PK>/` de IP residencial | Instagram | a janela esgota em ~8-10 respostas |
| paginação profunda `?max_id=` | Instagram | nunca devolveu 200; janela já queimada |
| `yt-dlp --write-comments` de IP limpo | Instagram | decide se o actor de comentários morre |
| Stories ao vivo | Instagram | o teste da branch SCRAP bate em `127.0.0.1` com fixture |
| bytes de mídia | YouTube | `403` de IP de datacenter |
| qualquer conteúdo | Facebook | 302/400 em tudo |
| paginação além dos 11 | LinkedIn | «Show more» não expõe URL |

**Nenhum foi mascarado. Todos são `NOT_EXECUTED` com o comando escrito.**
