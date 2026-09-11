# C10 · INSTAGRAM AUDIO-ONLY — a lei da C8 ganha a primeira implementação

```
MEDIDO_EM            = 2026-09-11
INSTAGRAM_AUDIO_ONLY = PROVEN
```

> **ISTO É EVIDÊNCIA DE MISSÃO, NÃO BÍBLIA.**
> Não é MASTER, não é FINAL global, não substitui contrato nenhum. É o registo
> de uma capacidade que mudou de estado num dia, com os números que a mudaram.

---

## A · GIT

| campo | medido |
|---|---|
| `SOURCE_BRANCH` | `claude/sintonia-scrap-capability-census-c9` |
| `INITIAL_HEAD` | `d298a6dbb09f70b2a2212ae5f60ad391f8d3a329` — igual ao observado pelo coordenador |
| `WORK_BRANCH` | `claude/sintonia-scrap-instagram-audio-only-c10` |
| `WORKTREE` | limpo no início |
| know-how canônico | `e2786d37d9f1f7c31ae586eadbcdf3bbe837bffa` — **mudou** desde a C9, que tinha medido `7f08b004` |

Três caminhos que o briefing cita não existem com esse nome, e foram medidos em
vez de assumidos: `coleta/scrap_registro.py` é `scrap_registo.py`,
`adaptadores/adaptador_instagram.py` vive em `coleta/`, e `leis/retorno_da_coleta.py`
não existe — quem carrega `COL-LAW-505` é `coleta/ingresso.py`.

---

## B · O PORTÃO DE POLÍTICA — respondido ANTES de escrever código

A pergunta da §4 era: esta missão só reduz bytes de uma capacidade que já é
operacional, ou cria/alarga uma rota que o portão atual proíbe?

```
RESPOSTA = A · SÓ REDUZ BYTES
```

E a prova não é argumentação, é o manifesto de formatos do próprio Reel:

| o que a rota pede | formatos |
|---|---|
| **antes** (padrão do `yt-dlp`, sem seletor) | `dash-…v` **+** `dash-…a` — dois fluxos |
| **depois** (`-f bestaudio`) | `dash-…a` — **um**, e é exatamente o segundo dos dois |

Os dois fluxos saem do mesmo host — `scontent-ord5-2.cdninstagram.com` —
medido no mesmo manifesto.

```
A ROTA NOVA É UM SUBCONJUNTO ESTRITO DA ROTA VELHA.
```

Ela não alcança endereço novo, não alcança host novo, não faz pedido a mais.
Deixa de pedir uma das duas coisas que já pedia. Uma mudança que só subtrai não
pode alargar autorização nenhuma — e é por isso que este portão abriu.

**O que ela continua a NÃO fazer, e continua fora de escopo:** descoberta de
perfil, listagem de publicações, Stories, comentários, crawl, Apify. O escopo
executado foi o autorizado: **uma URL direta de Reel, já conhecida da casa.**

E a dívida estrutural que a C9 registou **não foi resolvida aqui**: a cadeia de
Reel continua a usar `executa` e continua a não atravessar o portão de rotas de
`social_matriz`. Reduzir bytes não é o mesmo que ligar um portão, e esta missão
não fingiu que era.

---

## C · A ROTA, ANTES E DEPOIS

**ANTES** — medido pela C9 e confirmado no código:

```
reel_transcricao.py:432   _ytdlp(['-o', modelo_saida, url])        ← sem seletor
fala_local.py:948         ffmpeg -i <mp4> -vn … → WAV

VIDEO_ACQUISITION + AUDIO_DERIVATION
```

**DEPOIS**:

```
SOURCE  →  yt-dlp -f bestaudio  →  RAW = .m4a  →  WAV (meio de trabalho)  →  ASR  →  DERIVED

AUDIO_ONLY_ACQUISITION + ASR
```

O RAW deixou de ser o vídeo. Não porque alguém renomeou o campo, mas porque os
bytes que chegam ao disco passaram a ser outros — e a ficha do RAW nasce do que
`obter_midia` devolve, que é exatamente onde a mudança foi feita.

```
RAW != VIDEO.  RAW é a observação bruta ADQUIRIDA NESTA ROTA.
```

---

## D · A PROVA, ITEM A ITEM

`provas/instagram_audio_only.py`, corrido em 2026-09-11.

| campo | medido |
|---|---|
| `TEST_URL` | `https://www.instagram.com/reel/C-FanW_CYMz` |
| `PROVIDER` | `LOCAL_YTDLP` |
| `FORMAT_SELECTED` | `bestaudio` → `dash-1062115465344400a` |
| `AUDIO_CODEC` | `mp4a.40.5` · `abr = 85,372 kbps` |
| `RAW_FICHEIRO` | `C-FanW_CYMz.m4a` |
| `AUDIO_BYTES` | 362 479 |
| `AUDIO_SHA256` | `4fe5e6be5c580c42e8945d958dc8b8b568ff8d2ad4da162e54dc0d4500e54a13` |
| `DURACAO_S` | 34,11 |
| **`VIDEO_STREAMS`** | **0** |
| **`AUDIO_STREAMS`** | **1** |
| **`VIDEO_BYTES_DOWNLOADED`** | **0** |
| `TRANSCRIPT_STATE` | `OK` · 343 caracteres, italiano |
| `DERIVED_PARENT` | `RAW-4fe5e6be5c580c42` — o próprio áudio adquirido |
| `DOWNLOAD_E_ASR_SEGUNDOS` | 26,62 |
| `APIFY_RUNS` | 0 |

As treze verificações da §13 passaram. A nona é a que fecha a porta dos fundos:
não basta o RAW ser áudio, **nenhum ficheiro da gaveta pode ter imagem** — senão
um degrau podia ter baixado um MP4 e deitado fora, e `VIDEO_BYTES > 0` passaria
despercebido.

### O ganho, com as duas bases separadas

| base | valor |
|---|---|
| `FORMAT_ESTIMATE` · padrão (vídeo+áudio) | 416,558 kbps |
| `FORMAT_ESTIMATE` · só áudio | 85,372 kbps |
| **`BYTE_REDUCTION_RATIO` estimado** | **4,9×** |
| `MEASURED_BYTES` · áudio | 362 479 |
| `MEASURED_BYTES` · vídeo | 0 |

O 4,9× é **estimativa de formato**, não byte medido dos dois lados — medir o
outro lado exigiria baixar o vídeo, que é exatamente o que esta missão proíbe.
E não se extrapola: a C9 mediu 9,5× sobre os oito Reels históricos e 30,2× num
terceiro caso. São três números de três amostras, e nenhum deles é «o
Instagram».

---

## E · O QUE ESTA PROVA RECUSA COMO EVIDÊNCIA

Três coisas que parecem prova de aquisição só de áudio, e não são:

1. **a bandeira `-f bestaudio`** — diz o que foi *pedido*;
2. **a extensão `.m4a`** — diz o que alguém escreveu no nome;
3. **o nome do fornecedor** — o `yt-dlp` traz as duas coisas.

```
PEDIR ÁUDIO != TER RECEBIDO SÓ ÁUDIO.
```

Por isso o veredito sai do `ffprobe` sobre os bytes que chegaram. E há um teste
que ataca precisamente isto: um MP4 renomeado para `.m4a` é recusado, e um
fornecedor que «obedece» ao comando e entrega imagem na mesma é recusado com
`MEDIA_KIND_MISMATCH`.

### E por que ela corre numa gaveta vazia

Há oito MP4 no disco desta casa. A cadeia reusa mídia preservada — e bem, porque
rebaixar é pagar duas vezes. Mas:

```
REUSAR != ADQUIRIR.
REUSED_VIDEO + AUDIO_DERIVATION  é o estado ANTIGO com nome novo.
```

Se o MP4 histórico estivesse ao alcance, a prova passaria **sem nunca ter
adquirido nada**. Uma prova que pode passar sem fazer o trabalho não é prova.
Por isso a gaveta é `data/raw/C10-PROVA-AUDIO/`, vazia a cada corrida, dentro do
`.gitignore` — e o registo marca o reuso como `REUSED_NOT_ACQUIRED`, nunca
`PROVEN`.

---

## F · O QUE FOI DESCOBERTO SEM PROCURAR

**Uma publicação que deixa de responder não é uma rota que partiu.** Às 17:42 o
Reel `C-63RfHoJTU` resolvia; às 19:0x do mesmo dia devolvia *«Instagram sent an
empty media response»* enquanto outros três resolviam na mesma máquina, no mesmo
minuto. Meia hora depois, o `DQhloXtjTep` trocou de lado com ele.

Uma sentinela única teria transformado isso num `BLOCKED` da rota. Por isso a
prova tem uma **escada de sentinelas declarada**, e cada tentativa fica escrita.
Sair desses endereços seria descoberta, e descoberta está fora do escopo.

**E um Reel sem fala não é uma rota sem fala.** O `DQhloXtjTep` foi adquirido
limpo — 676 280 bytes, `VIDEO_STREAMS = 0` — e o ASR correu até ao fim e
devolveu `REQUESTED_EMPTY`. Isso é o motor a dizer que não ouviu palavra, não é
falha nenhuma. A prova separa as duas afirmações:

```
A · AQUISIÇÃO   os bytes vieram, e são só áudio       → provável em qualquer Reel
B · CADEIA      o ASR lê, e o texto tem pai declarado → precisa de um Reel falado
```

e salta de sentinela **uma vez só, e só por ausência de fala**. Saltar por
qualquer outra falha seria procurar até passar, que é o contrário de medir.

---

## G · A LEI EXECUTÁVEL

`tests/test_c10_audio_only.py` — 17 testes cuja função é reprovar o regresso ao
comportamento antigo:

```
TRANSCRIPTION_ROUTE_MUST_NOT_DOWNLOAD_VIDEO
```

O que se mede é o **comando que a cadeia monta**, interceptado na fronteira com
o processo — e, onde há bytes, o que o `ffprobe` vê dentro deles. Não é `grep`:

```
UMA SENTINELA ANCORADA NO TEXTO MEDE O TEXTO, NÃO A LEI.
```

Um `grep` por `bestaudio` passaria com a palavra dentro de um comentário a
explicar que ela tinha sido removida.

### As mutações, e todas caem

| # | mutação | resultado |
|---|---|---|
| 1 | tirar o seletor `-f bestaudio` | **FAILED** (2 testes) |
| 2 | o embed volta a servir vídeo quando se pede fala | **FAILED** |
| 3 | remover a conferência nos bytes | **FAILED** |
| 4 | o MP4 reusado passa a chamar-se áudio | **FAILED** |
| 5 | endereço externo volta a ser baixado sem declarar espécie | **FAILED** |

Há também o contraponto que torna o teste do seletor informativo: **sem pedido
de fala, o seletor não entra**. Se ele entrasse sempre, o teste passaria mesmo
com a lei desligada e não mediria nada.

---

## H · SEM QUEDA PARA VÍDEO

Se `bestaudio` não existir, o `yt-dlp` falha e o estado sai
`AUDIO_ONLY_UNAVAILABLE`. Não há segunda tentativa com outro formato, não há
embed, não há Apify.

```
FALHA DE ROTA NÃO É AUTORIZAÇÃO PARA PEDIR MAIS.
```

Os três degraus da escada obedecem ao pedido: o `yt-dlp` pede só áudio e confere
os bytes; um endereço entregue por quem chama só é usado se **declarar**
`MEDIA_KIND = AUDIO`; o embed é saltado, porque o que ele serve é o MP4 inteiro.

Os dois últimos não são zelo a mais. Um endereço de vídeo baixado em silêncio
dentro de uma cadeia de transcrição faria `VIDEO_BYTES > 0` numa rota que jurou
não pedir imagem — e a jura passaria no teste do seletor.

---

## I · IDENTIDADE E LINHAGEM

O transcript responde à cadeia inteira: qual URL, qual RUN, qual RAW, qual
caminho, qual SHA dos bytes de **áudio**, qual fornecedor, qual formato, qual
duração, qual ASR, qual modelo, e o pai declarado.

Dois campos novos viajam colados ao `MEDIA_SHA256`, porque um SHA não diz de que
é: `MEDIA_KIND` e `AUDIO_ONLY_ACQUISITION`. Sem eles, quem ler a ficha daqui a
um ano assume vídeo, porque a cadeia se chama «reel».

### CONFLICT — e ele é anterior a esta missão

```
CONFLICT    = `SOURCE_ID` da ficha RAW leva o URL da publicação
WHY         = é o único identificador que esta cadeia tem em mãos; a Collection
              ainda não atribuiu o canônico
EVIDENCE    = ferramentas/reel_transcricao.py, `_ficha_raw`
NEXT_STEP   = quando a fundação de Collection atribuir `SOURCE_ID` e
              `RAW_OBSERVATION_ID`, esta ficha passa a recebê-los — não é
              trabalho desta missão e não foi feito aqui
```

A menor adaptação possível foi aplicada, e ela **não cria mentira nova**: o
registo passa a declarar `SOURCE_ID_KIND = URL_AS_PLACEHOLDER` e a dizer em
claro que aquilo é um endereço a fazer as vezes de um id, não um id atribuído.

```
URL != SOURCE_ID. Nada foi fabricado, e agora nada é silencioso.
```

`RAW_OBSERVATION_ID` continua `NOT_KNOWN` — é `raw_asset.id`, e só existe quando
a Collection o criar. O `SHA256` identifica bytes e nunca observação.

---

## J · SCRAP × COLLECTION CANÔNICA

Nada foi admitido, nada foi julgado, nenhum RUN canônico nasceu, nada subiu a
bucket nenhum. `COL-LAW-505` continua a valer e não foi tocada.

```
COLHEITA != MANIFEST != CATALOG != RUN_RECEIPT != PLAN != UNKNOWN
```

A prova é técnica e descartável, e ficou descartável: a gaveta está no
`.gitignore`, nenhum `raw_asset` foi fabricado, nenhum objeto órfão foi criado.
O `.m4a` adquirido é candidato a COLHEITA **quando esta capacidade for integrada
ao executor** — e essa integração não é desta missão.

---

## K · REGRESSÃO

| momento | testes | resultado |
|---|---:|---|
| baseline, antes de tocar em código | 554 | OK |
| depois, com os 17 novos | 571 | OK |

```
NEW_FAILURES = 0
ASR_OWNERS   = 1   (medido pela AST, e há um teste que o guarda)
```

Os módulos que carregam o entulho conhecido da casa foram medidos à parte e
ficaram idênticos ao que a C9 tinha medido: 21 falhas, distribuídas exatamente
pelos mesmos oito módulos. Entulho anterior, não regressão da C10.

`SYSTEM_MAP_CHECK = PASS`. O mapa foi regenerado pelo dono canônico, nunca
editado à mão — e precisou de **duas passagens**, porque o mapa indexa os
próprios ficheiros gerados e a primeira passagem muda o que a segunda mede.

---

## L · O QUE MUDOU, E O QUE NÃO

**Mudou:** a cadeia de Reel pede áudio; `fala_local` ganhou `fluxos()` e
`so_audio()`, ao lado do `ffprobe` que ele já era dono; `obter_midia` obedece a
`kind` em todos os degraus; o RAW e o derivado dizem que espécie de bytes são;
nasceram uma prova e uma suíte de guarda.

**Não mudou:** o dono do ASR, o modelo, o padrão global, a matriz de rotas, o
executor do SCRAP, o registo, o adaptador, a Collection, o portal, nem a rota do
YouTube, do LinkedIn, do X ou do Facebook. `MODELO_PADRAO` continua `medium` na
cadeia e `small` no motor — a C10 provou **aquisição**, não qualidade.

---

## M · DESCONHECIDO

- se todo Reel serve faixa audio-only, ou só os DASH — medidos 4, todos serviam;
- quanto dura o endereço assinado da faixa de áudio;
- se `m4a` é sempre o contentor, ou se aparece `opus`/`webm` noutras publicações;
- a razão de uma publicação alternar entre responder e não responder no mesmo dia;
- o ganho em bytes reais dos dois lados — só medível baixando o vídeo, que é
  proibido aqui.

---

## N · RISCO RESTANTE

1. **A cadeia continua a não atravessar o portão de rotas.** A C9 registou, a
   C10 não resolveu, e reduzir bytes não resolve.
2. **`SOURCE_ID` continua a ser um URL**, agora declarado como tal.
3. **O reuso de MP4 histórico continua ligado.** É compatibilidade, está
   rotulado, e é por onde uma prova futura pode enganar-se sozinha.
4. **`bestaudio` é vocabulário do `yt-dlp`.** Se o significado dele mudar numa
   versão nova, a conferência nos bytes apanha — mas só depois de baixar.

---

## O · VEREDITO

```
INSTAGRAM_AUDIO_ONLY = PROVEN
POLICY_GATE          = A · só reduz bytes
VIDEO_BYTES_DOWNLOADED = 0
APIFY_RUNS           = 0
NEW_FAILURES         = 0
SYSTEM_MAP_CHECK     = PASS
KNOW_HOW_DELTA       = NENHUM
BÍBLIA/CONTRATO      = NÃO precisa mudar

HARD STOP.
```
