# LINKEDIN — A MÍDIA PÚBLICA · V1

> **MEDIDO_EM:** 2026-09-18, de `d915f85a86a7ef0d310859f7380159dbed65b48a`,
> worktree `C:/Users/London1/orca/workspaces/eame-sintonia/linkedin-media-v1`
> (branch `claude/linkedin-media-acquisition-v1`).
> **ESTE FICHEIRO É A PROVA CITADA POR** `coleta/scrap_capacidades.py` →
> `linkedin.public_post.media_resolution` e `linkedin.local_transcript`.
> Ele diz o que foi medido, e diz o que **não** foi.

---

## 1 · O QUE ESTA CAPACIDADE É

```
POST PUBLICO DO LINKEDIN
  → GET da pagina (HTTP 200 a convidado, sem login, sem cookie, sem navegador, sem proxy)
  → atributo <video data-sources>   ← o endereco da midia esta AQUI
  → 3 rendicoes MP4 progressivas em dms.licdn.com (nao HLS, nao DASH)
  → escolha da MENOR rendicao (a pergunta e de fala; a imagem nao entra no transcript)
  → GET dos BYTES
  → ffprobe
  → RAW
```

E o que **não** é: não é coleta de posts. `LINKEDIN/FETCH_POST` continua
`ROUTE_NOT_ALLOWED` nas duas rotas dele, e esta porta **não a contorna** — ela
atravessa outra capacidade grossa, `FETCH_PUBLIC_MEDIA`, declarada com os três
eixos separados.

## 2 · OS TRÊS EIXOS, SEPARADOS (é o ponto, e não um detalhe)

| eixo | valor | prova |
|---|---|---|
| `TECHNICALLY_WORKS` | **YES** | canário real, abaixo |
| `PROJECT_OWNER_AUTHORIZED` | **SIM** — escopo: **posts públicos** | ordem escrita do dono do projeto, 2026-09-18 |
| `PLATFORM_POLICY_STATUS` | **RESTRICTED** | `robots.txt` do linkedin.com (só `LinkedInBot` tem `Allow: /`) e §8.2 do User Agreement |

```
A ORDEM DO DONO É DO PROJETO. ELA NÃO AUTORIZA A PLATAFORMA.
PLATFORM_PERMISSION = YES  — NÃO ESTÁ ESCRITO EM LUGAR NENHUM, E NÃO PODE ESTAR.
```

A cláusula de §8.2 alcança dado obtido «through third parties (such as data
aggregators or brokers)» — e é por isso que um fornecedor pago **não** limpa a
rota. O que a autorização do dono compra é a responsabilidade pelo risco do
projeto, e nada mais.

## 3 · O CANÁRIO — um post público, medido

```
POST_URL          https://www.linkedin.com/posts/cosemar-ozono_…-activity-7475836883001024512-wyDU
POST_NATIVE_ID    7475836883001024512        (activity id — identidade DE OBJETO na plataforma)
PAGINA PUBLICA    HTTP 200 · 120.863 bytes · text/html · <video data-sources> presente
RENDICOES         360p 298.876 bps · 640p 640.268 bps · 720p 852.433 bps
SELECTED          mp4-360p-30fp-crf28        (a de MENOR bitrate declarado)
HEAD_NA_MEDIA     HTTP 200 · video/mp4 · Content-Length 2427559 · Accept-Ranges: bytes
MEDIA_BYTES       2.427.559
RAW_SHA256        e3ff0d54575c06daac5d04f262ce3a4382730995c8fb37d16a7603bb765612c8
FFPROBE           dur 47,81 s · [0] h264 360x640 · [1] aac 44.100 Hz mono
VIDEO_STREAMS = 1   AUDIO_STREAMS = 1   AUDIO_ONLY_AVAILABLE = NO
ASR               faster-whisper 1.2.1 · small · es (DETECTADO, 0.908) · 614 caracteres
CUSTO             APIFY_RUNS = 0 · PAID_USD = 0 · LOGIN = NO · COOKIE = NO · PROXY = NO
```

### O achado que fecha a pergunta «para que serve o fornecedor pago?»

O mesmo post, o mesmo asset (`D4E10AQFPCG4lST76GA`), dois endereços:

```
BRUTO PAGO, preservado 2026-08-29   …/mp4-720p-30fp-crf28/B4EZ7.B9MhIwBo-/0/1782378396722?e=1788580800
PAGINA PUBLICA, hoje                …/mp4-720p-30fp-crf28/B4EZ7.B9MhIwBo-/0/1782378396722?e=2147483647
                                    → MESMO CAMINHO. Difere so a assinatura (t) e o prazo (e).
```

```
PROVIDER_UNIQUE_MEDIA_CAPABILITY = NO   — para RESOLUCAO DE MIDIA deste caminho.

O que isso NÃO diz: que o provedor seja inútil. Ele pode continuar a valer para
keyword discovery, profundidade de historico e outras capacidades.

    MEDIA RESOLUTION  !=  DISCOVERY.
```

## 4 · LEGENDA NATIVA — existe, e é `WEBVTT`

```
post the-mathworks 7151241570371948544 → data-captions-url presente
HTTP 200 · 4.283 bytes · cabecalho `WEBVTT` · `00:00.000 --> 00:03.240`
sha256 04feb96dbe27421325d0dd24eabb7a19bf5cc4f2e5eb7fc5fd0965072b4fc082
post do canario (cosemar-ozono) → data-captions-url: 0 ocorrencias
```

Existe **por post**, não universalmente. E as espécies não se somam:

```
NATIVE_CAPTION            !=   LOCAL_ASR_TRANSCRIPT
CAPTION_TEXT (o que a plataforma legendou)   !=   TRANSCRIPT_TEXT (o que esta casa ouviu)
```

⚠️ **ACHADO, não corrigido aqui:** o docstring de `coleta/adaptador_linkedin.py`
afirmava «E SRT, nao WebVTT … verificado nos bytes». Os bytes medidos hoje dizem
**WEBVTT**. Onde o documento e os bytes discordam sobre um facto técnico, os
bytes vencem — mas corrigir a prosa do docstring é decisão de outro dono.
A nota do registo da capacidade já carrega o valor medido.

## 5 · AS URLs ASSINADAS EXPIRAM — o bilhete não é o filme

```
56 URLs preservadas do bruto pago: host dms.licdn.com · e=1788580800 (2026-09-05T04:00Z)
HEAD na URL preservada:  HTTP/1.1 403 Forbidden · 22 bytes
HEAD na URL publica de hoje: HTTP/1.1 200 OK · video/mp4 · 2427559 bytes
```

⇒ **reprocessar o RAW preservado para tirar mídia é impossível.** As 56
referências estão vencidas e devolvem 403. Num retry, o endereço **resolve-se de
novo a partir do post público** — e a expiração **não** se chama
`CONTENT_MISSING`: o conteúdo existe, o bilhete é que venceu.

`e=2147483647` é `LONG_LIVED_OBSERVED` — uma observação de hoje, numa amostra.
Não é `DOCUMENTED_STABLE`, e nunca se escreve «permanente».

## 6 · A GUARDA DOS BYTES ENTREGUES

O red team da missão anterior mediu: um ficheiro de **zero bytes** era aceite como
`MEDIA_OK` no degrau da mídia e só reprovava depois, em `ASR_FALHOU`. O fim era
honesto; o degrau mentia. Corrigido em `ferramentas/reel_transcricao.py`
(`_valida_ficheiro_entregue`), com **estados já canónicos** — nenhum vocabulário
novo:

| entrada | estado | por quê |
|---|---|---|
| ficheiro de **0 bytes** | `MEDIA_DOWNLOAD_FAILED` | zero bytes não são mídia |
| **HTML/JSON/PDF** com nome `.mp4` | `NOT_A_VIDEO` | os bytes são markup, não mídia |
| vídeo **sem faixa de som** (medido) | `AUDIO_ONLY_UNAVAILABLE` | pediu-se fala e não há som |
| ficheiro ilegível (`ffprobe` não abre) | **passa** — quem decide é o degrau de baixo | «não consegui ver» ≠ «não tem som» |
| MP4 real (controlo) | `MEDIA_OK` · `TRANSCRIPT_STATE = OK` · 614 caracteres | — |

```
ZERO_BYTE_GUARD = PASS
```

## 7 · O QUE ESTA MISSÃO **NÃO** FECHOU

```
COLLECTION_WIRED = NÃO FECHADO
```

A rota existe, colhe e mede. O que falta é a ponta **canónica** da Collection —
`SOURCE_ID → collection_run → raw_asset → storage_object → DERIVED → ADMISSION →
SALA` — e ela **não** se fecha por código sozinho:

- **`SOURCE_ID` é decisão de governação de fonte**, não de engenharia. A porta
  canónica (`candidatas/fonte_nova.py`) aceita o tipo `LINKEDIN`, mas uma
  candidata nasce com `SOURCE_ID = None` — o id só existe quando a fonte é
  promovida no atlas, e isso diz **qual tier, qual país e para que serve**. Não é
  identidade que se possa derivar de um endereço, e fabricá-la seria o erro que
  esta casa mais proíbe.
- `preservar()` recusa observação sem fonte real (`B5B`), e faz bem: sem
  `SOURCE_ID` não há estado de identidade possível.

O resto da estrada já tem dono e já foi provado noutra missão:
`guarda/preservar_coleta.preservar()` · `coleta/derivacao_forward.correr()` ·
`coleta/executor_transcricao_midia.derivar_um()` (a Ponte de Mídia, que recebe um
caminho e **não sabe de onde o byte veio**) · `admissao/admissao.py` ·
`admissao/sala_de_espera.py`.

## 8 · REPRODUZIR

```bash
cd <worktree> && python -m pytest tests/test_linkedin_media_publica.py -q
python scrap_colheita.py midia-linkedin --run-id=<RUN> --fonte=<SOURCE_ID> \
       --post=<POST_URL>
```
