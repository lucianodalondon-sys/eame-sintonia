# C13 · YOUTUBE — A AQUISIÇÃO DE ÁUDIO PÚBLICO

**Missão:** provar a aquisição real de áudio de um vídeo público do YouTube, até à
transcrição, pela rota que a casa já tinha.
**Medido em:** 2026-09-18. **Custo:** US$ 0,00. **Execuções pagas:** 0.

Este documento é a **prova própria** de `youtube.public_audio`. Ele existe porque
o §147 desta mesma semana deixou escrito que um estado de capability ancorado no
documento errado diverge em silêncio: quem for conferir abre o papel errado, não
vê contradição nenhuma, e o carimbo errado sobrevive. Aqui, a prova é o documento
que mediu **esta** rota.

---

## 1 · Por que esta capacidade é separada da rota oficial

A execução `youtube-oficial` (GitHub Actions, RUN `35401296232`, trunk
`195bdb7b`) correu **4/4 capacidades pela YouTube Data API v3** — descoberta,
canal, metadata e comentários — com quota gratuita e `APIFY_CALLS = 0`. Foi um
`PASS`, e continua a ser.

Ela **não produziu um único byte de som**, e não podia:

```
captions.list / captions.download   exigem OAUTH, não a chave de API
youtube.media                       não tem rota oficial nenhuma
```

```
DADOS OFICIAIS  !=  ÁUDIO PÚBLICO
API_KEY         !=  OAUTH
```

São duas capacidades, com duas provas e dois documentos. Este é o do áudio.

---

## 2 · A rota usada — a que já existia

`ferramentas/youtube_transcrever.py::_audio(video_id)` — **nenhum descarregador
novo foi construído**. O comando, literal:

```
yt-dlp -f bestaudio/best -x --audio-format wav
       --postprocessor-args '-ac 1 -ar 16000'
       -o <MEDIA>/%(id)s.%(ext)s https://www.youtube.com/watch?v=<VIDEO_ID>
```

E o reconhecedor é o dono canônico da casa, `ferramentas/fala_local.py` — não há
segundo Whisper.

---

## 3 · O canário

```
VIDEO_ID     zaEk8LE6SOQ
SOURCE_URL   https://www.youtube.com/watch?v=zaEk8LE6SOQ
CANAL        Agronotizie - Notizie per l'agricoltura  (@agronotizietv)
TÍTULO       «Flavescenza dorata, la lotta alla cicalina della vite»
VIDEO_PUBLIC YES — conferido ao vivo por `oEmbed` (HTTP 200) antes da aquisição
```

Vídeo público, de terceiro, não live, reproduzível sem login.

---

## 4 · A aquisição — medido nos bytes

```
AUDIO_FETCH_ATTEMPTED  YES
AUDIO_FETCH_RESULT     BAIXADO            em 11,8 s
AUDIO_BYTES            7.809.414
AUDIO_SHA256           0167e22599b5fed72b534c60bc05c728341057b9def4dee7e18a4d7acca2ad95
AUDIO_DURATION         244,04 s
AUDIO_CODEC            pcm_s16le · 16 kHz · mono
STREAMS                1 áudio · 0 vídeo
```

`-f bestaudio` diz o que foi **pedido**; só o `ffprobe` diz o que **chegou**. O
ficheiro traz **um** fluxo de som e **zero** de imagem — medido, não deduzido da
extensão nem do nome do formato.

```
AUDIO_ONLY != VIDEO
```

---

## 5 · A transcrição — pelo dono canônico

```
ASR_ATTEMPTED       YES
TRANSCRIPT_STATE    OK
TRANSCRIPT_CHARS    3010
TRANSCRIPT_LANGUAGE it   (DECLARED · DETECTED it · confiança 1,0)
ASR_ENGINE          faster-whisper 1.2.1 · modelo `small` · CTranslate2 · cpu/int8 · 16 threads
AUDIO_SECONDS       244,04     MACHINE_SECONDS 34,87     (7,0x tempo real)
COST_USD            0
```

Amostra do início — e ela é a prova de que o som é **daquele** vídeo:

> «Buongiorno, sono Paolo Beccari di Agria Centro Studi, mi occupo di prove
> sperimentali su Scafoideus Titanus, insetto che negli ultimi anni è tornato in
> maniera importante nei vigneti del Veneto…»

O interlocutor e a praga do título estão ambos no texto reconhecido.

---

## 6 · Linhagem

```
SOURCE_URL          https://www.youtube.com/watch?v=zaEk8LE6SOQ
VIDEO_ID            zaEk8LE6SOQ
CAPTURE_TOOL        yt-dlp 2026.08.19 (via ferramentas/youtube_transcrever.py::_audio)
CAPTURE_TIMESTAMP   2026-09-18 19:38:20 -0300
RAW_AUDIO_PATH      fora do repositório, em pasta de missão
SHA256              0167e225…2ad95
AUDIO_PARENT        VIDEO_ID zaEk8LE6SOQ / SOURCE_URL acima
```

`VIDEO_ID != SOURCE_ID`. Nenhum `SOURCE_ID`, `DOCUMENT_ID` ou `RAW_OBSERVATION_ID`
foi fabricado. O RAW vive **fora** do repositório: o áudio não é arquivo do Git.

---

## 7 · Os três eixos — nenhum se colapsa

```
TECHNICALLY_WORKS          YES
PROJECT_OWNER_AUTHORIZED   YES   (decisão escrita do dono; escopo: só vídeo público)
PLATFORM_POLICY_STATUS     DISALLOWED
```

As cláusulas que fecham a porta, verbatim:

```
Developer Policies III.E.1.a
  «download, import, backup, cache, or store copies of YouTube audiovisual
   content without YouTube's prior written approval»

Developer Policies III.I.7
  «separate, isolate, or modify the audio or video components of any YouTube
   audiovisual content»

ToS §Permissions and Restrictions
  «access the Service using any automated means (such as robots, botnets or
   scrapers)» — salvo motor de busca público conforme robots.txt, ou permissão
   escrita prévia.
```

O dono autoriza o risco do **projeto**; não autoriza a plataforma. As duas frases
sobrevivem lado a lado, e é isso que impede a próxima missão de confundir
«conseguimos» com «podemos».

**O que não foi cruzado:** sem cookie de terceiro, sem conta, sem CAPTCHA, sem
token de sessão, sem login, sem contornar paywall ou acesso privado. Alvo público,
sem autenticação.

---

## 8 · Red team — `RED_TEAM_BLOCKERS = 0`

| ataque | resultado medido |
|---|---|
| vídeo público válido | `BAIXADO` · bytes + SHA · ASR `OK` |
| `VIDEO_ID` inválido (`zzzzzzzzzzz`) | `AUDIO_NAO_OBTIDO` · *This video is unavailable* |
| `VIDEO_ID` inexistente (`aaaaaaaaaaa`) | `AUDIO_NAO_OBTIDO` · idem |
| `ffprobe` sobre HTML renomeado `.wav` | `ASR_FALHOU` · `InvalidDataError` |
| `ffprobe` sobre ficheiro vazio | `ASR_FALHOU` · idem |
| RAW preservado vs WAV do cache | **SHA256 idêntico** |

```
FALHA DE AQUISIÇÃO  !=  VÍDEO SEM FALA  !=  FALHA DO MOTOR
AUDIO_NAO_OBTIDO    !=  REQUESTED_EMPTY !=  ASR_FALHOU
```

Três estados, três causas, três consertos. Colapsá-los apagaria a diferença entre
«não ouvi», «ouvi e não havia nada» e «o reconhecedor partiu».

---

## 9 · O que esta prova NÃO declara

```
youtube.media      continua BLOCKED — AUDIO_ONLY não é aquisição de vídeo
youtube.native_caption  continua PARTIAL — ver o C5; o áudio não a promove
Collection         NOT_RUN — RUN, RAW Observation, Admission e Sala não correram
rota canônica      FECHADA em §10 — ver abaixo
```

---

## 10 · A rota canônica — o edge que faltava (C13 · WIRING)

A §9 dizia `rota canônica NOT_RUN`: a prova de §4 foi feita **chamando a
implementação**, e não pelo `COLLECT`. A matriz sabia pedir (§150) e o executor
não conhecia a porta — `CHECK` respondia `DECLARED_WITHOUT_ROUTE`.

**Agora responde outra coisa:**

```
CHECK('YOUTUBE','youtube.public_audio')
  CAN                True
  STATE              CAN_COLLECT_NOW
  PRODUCTION_READY   True
  COST_TO_CHECK_USD  0.0
  MATRIZ_CAPABILITY  FETCH_AUDIO_BYTES
  ADAPTER            adaptador_youtube
```

**A ligação é uma só, e entra pela matriz:**

```
scrap_executor → social_rotas → social_matriz → scrap_registo
              → adaptador_youtube.youtube_audio_publico → youtube_transcrever._audio
```

`rota=`, e não `executa=`: quem tem matriz não contorna o roteador. Uma segunda
rota registada seria uma segunda verdade sobre a mesma aquisição.

**O QUE ESTA LIGAÇÃO NÃO FEZ.** Não criou descarregador: a implementação continua
a ser `ferramentas/youtube_transcrever.py::_audio`, a mesma de §4. Não chama ASR —
reconhecer fala é outra capacidade, com outro dono. Não aceita sessão, cookie,
token nem credencial: o limite continua `PUBLIC_AUDIO_ONLY`.

**A ESPÉCIE DO OBJETO.** `AUDIO_ONLY != VIDEO`. O envelope canônico **não tem**
`AUDIO` em `CONTENT_TYPES`, e mediu-se que o caminho canônico **não obriga** ao
envelope (`social_rotas._executar` usa o retorno da rota directo). O objecto é
próprio da capability:

```
OBJECT_KIND        PUBLIC_AUDIO
MEDIA_KIND         AUDIO
ACQUISITION_STATE  AUDIO_ADQUIRIDO
AUDIO_BYTES        os bytes medidos
AUDIO_SHA256       os mesmos bytes, selados
STREAMS            AUDIO>=1 · VIDEO=0  (medido pelo dono do ffprobe)
PARENT             KIND=VIDEO · VIDEO_ID · SOURCE_URL  ← a linhagem
LIMITE             PUBLIC_AUDIO_ONLY
```

`CONTENT_TYPES` **não foi alargado**. Se o caminho canônico obrigasse ao envelope,
a resposta era `OUTPUT_GRAIN_BLOCKER = YES` e HARD STOP — nunca `MEDIA_KIND=VIDEO`
para ficar verde.

**A FALHA TEM NOME.** O roteador deriva `ESTADO = 'OK' if objetos else
'ZERO_RESULTS'`, portanto devolver `[]` faria uma avaria do `yt-dlp` passar por
«não havia nada». A rota declara o estado em vez disso:

```
yt-dlp falhou (vídeo indisponível)  →  RESULT=SOURCE_GONE          NATIVE_REASON=AUDIO_NAO_OBTIDO
ferramenta partida                  →  RESULT=EXECUTOR_UNAVAILABLE NATIVE_REASON=AUDIO_NAO_OBTIDO
sem VIDEO_ID comprovado             →  RESULT=CONTRACT_DRIFT       NATIVE_REASON=VIDEO_ID_AUSENTE
veio imagem no ficheiro             →  RESULT=CONTRACT_DRIFT       NATIVE_REASON=MEDIA_KIND_MISMATCH
```

Nenhum deles é `ZERO_RESULTS`, e a taxonomia da casa lê o estado declarado em vez
de o reinterpretar (`SOURCE_HEALTH=GONE`, `EXECUTOR_HEALTH=HEALTHY`).

**PROVA.** `tests/test_c13_executor_wiring.py` — 22 testes, todos offline. O
`_audio` é substituído e devolve um WAV real (construído com a biblioteca `wave`),
o que prova **despacho** e não download. Medido: uma volta ao adaptador, uma só
rota registada, `CHECK` sem rede (`socket.connect` proibido) e sem uma única
chamada à aquisição.

**O QUE CONTINUA FORA, e é honesto dizê-lo.** A ligação foi provada com a
implementação **substituída**. A aquisição real, com bytes reais, é a de §4 — o
canário `zaEk8LE6SOQ`. As duas provas são separadas de propósito, e nenhuma herda
o carimbo da outra:

```
DISPATCH PROVADO  !=  DOWNLOAD EXECUTADO NESTA RONDA
```

