# C4G · A LEGENDA E O ÁUDIO NÃO ABREM — e a cláusula que os fecha tem nome

> **A hipótese desta missão era boa, e está medida: refutada.** A C4F mediu que
> adquirir **vídeo** do YouTube é `ROUTE_NOT_ALLOWED`. Sobrou a pergunta
> razoável — *para transcrever, talvez baste a legenda pública; ou, faltando
> ela, só o áudio*. Não basta, e não porque seja difícil.
>
> **O plano B tem cláusula própria, e ela nomeia o áudio por extenso.**

```
ACQUISITION_POLICY_VERDICT = BLOCKED_NEEDS_AUTHORIZATION
POLICY_DECISION_REQUIRED   = YES

CAPTION_STATUS   = CAPTION_NOT_ACCESSIBLE   (e NÃO «not available»)
AUDIO_STATUS     = ROUTE_NOT_ALLOWED
AUDIO_BYTES      = 0
CAPTION_BYTES    = 0
FULL_VIDEO_FETCHED = NO

NENHUMA ROTA NOVA FOI IMPLEMENTADA. `yt-dlp` NÃO FOI INSTALADO.
NENHUMA FONTE NOVA FOI CRIADA. NENHUM DÓLAR FOI GASTO.
```

---

# A · GIT — e a divergência que veio primeiro

| campo | valor |
|---|---|
| `BRANCH` | `claude/youtube-italia-caption-audio-8b460b` |
| `START_HEAD` (medido) | `f437ff1140fa97484ca9695b341fbe9ca0a9f050` |
| `REFERÊNCIA` do coordenador | `611e7cbf…` em `claude/local-gpu-on-current-collection-v1` |
| `WORKTREE_CLEAN` | sim, no arranque |

**GIT venceu, e o que ele disse mudou onde a missão podia acontecer.** O
`START_HEAD` medido **não era** descendente da referência:

```
611e7cbf NÃO é ancestral de f437ff11
merge-base            56fdb8ca  (Merge pull request #1)
commits em falta      483
commits próprios        9
```

Os 483 em falta traziam **a implementação inteira do YouTube**:
`coleta/adaptador_youtube.py` · `coleta/youtube_oficial.py` ·
`provas/gpu_asr_smoke.py` · os contratos C2–C5 · oito ficheiros de teste.
Nenhum deles existia na árvore montada.

E os 9 commits próprios não compensavam: medido, o único ficheiro que eles
acrescentavam sobre a referência era `.github/workflows/scrap-social.yml` — que
**já existe** na linha do acervo, num blob mais evoluído (`6c33bc21` contra
`9cdaaa24`).

```
UMA BRANCH QUE NÃO TEM O DONO DO CONCEITO NÃO É UM SÍTIO ONDE SE CONSERTA O
CONCEITO: É UM SÍTIO ONDE SE ESCREVE O SEGUNDO.
```

Escrever o adaptador de YouTube ali teria produzido um **segundo dono** —
exactamente o que `COL-LAW-011` e o `§5` do briefing proíbem — e o repositório
já carrega esse defeito noutro sítio (o know-how canônico, em 16 documentos
distintos).

**O que se fez, e o que não se perdeu.** A tag `antes-da-missao-youtube` guarda
`f437ff11`, e a branch foi reposta sobre `611e7cbf`. Nenhum trabalho ficou para
trás: o único conteúdo exclusivo já vivia na linha de destino.

| campo | valor |
|---|---|
| `BASE_ESCOLHIDA` | `611e7cbf406147c0ab057e9ffa7775f6fa11e8a1` |
| `FINAL_HEAD` | o commit que traz este documento |
| `REMOTE_HEAD` | **não existe** — `origin/claude/youtube-italia-caption-audio-8b460b` não estava publicada |

### Por que esta base, e não a mais recente

Quatro branches mais novas também têm o adaptador. Medido:

```
adaptador_youtube.py  ->  b28dc474  nas QUATRO, byte a byte igual
social_matriz.py      ->  3260a718  nas QUATRO, byte a byte igual
```

**O dono do YouTube não está bifurcado.** O que diverge à volta dele é trabalho
de *Intelligence* — que o `§0` do briefing proíbe iniciar. `local-gpu-on-current-collection-v1`
contém estritamente `collection-to-waiting-room-v1` (`+0/−5`), é a mais recente
da sua própria linha, e é a que o coordenador nomeou.

---

# B · PRIMEIRO O MODELO MENTAL — QUATRO CAPACIDADES, NÃO UMA

O `§2` mandava responder antes de escrever código. A resposta:

```
FETCH_VIDEO_METADATA  !=  FETCH_PUBLIC_CAPTION
FETCH_PUBLIC_CAPTION  !=  FETCH_AUDIO_STREAM
FETCH_AUDIO_STREAM    !=  FETCH_VIDEO_STREAM
```

**Para a finalidade actual — Intelligence textual — o SINTONIA não precisa dos
bytes do vídeo.** Precisa de `C` (caption) **ou** de `B` (áudio), nunca de `A`.
Isso está certo, e continua certo depois desta missão. O que a missão mediu é
que **estar certo sobre o que se precisa não abre a porta de onde se vai
buscar.**

E a casa já tinha tropeçado nesta distinção, do lado bom: a C4F corrigiu um
detector que aceitava qualquer capacidade com `VIDEO` no nome e apanhava
`FETCH_VIDEO_METADATA` — que é **permitida** e traz um título.

```
METADADO DO VÍDEO != VÍDEO.
E AGORA, A METADE QUE FALTAVA: PRECISAR DE MENOS != PODER MAIS.
```

---

# C · O CENSO — o que existe hoje, por capacidade

`YOUTUBE_OWNER = coleta/adaptador_youtube.py` (um só; o roteador deixou de
conhecer nomes de plataforma na C1).

A matriz declara **cinco** capacidades para o YouTube. Lidas do próprio
`leis/social_matriz.py`, não de memória:

| CAPACIDADE | rota | ESTADO |
|---|---|---|
| `SEARCH_KEYWORD` | `youtube-data-api-v3:search.list` | `CREDENTIAL_MISSING` |
| | `yt-dlp:ytsearch` | `ROUTE_NOT_ALLOWED` |
| `INCREMENTAL` | `youtube-data-api-v3:playlistItems.list` | `CREDENTIAL_MISSING` |
| | `feeds/videos.xml` | `ROUTE_NOT_ALLOWED` |
| `FETCH_VIDEO_METADATA` | `youtube-data-api-v3:videos.list` | `CREDENTIAL_MISSING` |
| | **`youtube:oembed`** | **`PROVED`** |
| | `yt-dlp:extract_info` | `BLOCKED` |
| `FETCH_COMMENTS` | `youtube-data-api-v3:commentThreads.list` | `CREDENTIAL_MISSING` |
| `FETCH_TRANSCRIPT` | `youtube-data-api-v3:captions.download` | `REQUIRES_OWNER_PERMISSION` |
| | `youtube-data-api-v3:captions.list` | `REQUIRES_AUTHORIZATION` |
| | `timedtext` | `ROUTE_NOT_ALLOWED` |
| | `apify:transcricao` | `PARTIAL` (paga) |

```
FETCH_AUDIO_STREAM  ->  NÃO EXISTE NA MATRIZ
FETCH_VIDEO_STREAM  ->  NÃO EXISTE NA MATRIZ
```

**E o silêncio não é a resposta.** `social_matriz.py` escreve-o por extenso:
*«O SILÊNCIO DA MATRIZ NÃO PROÍBE, E TAMBÉM NÃO AUTORIZA.»* Quem fecha a porta
do áudio não é a linha em falta — é a secção `D`.

A única rota livre e `PROVED` de toda a tabela é `youtube:oembed`, e ela devolve
**título, autor e thumbnail**. Nem legenda, nem áudio.

---

# D · A CLÁUSULA QUE FECHA O PLANO B

Buscadas na fonte viva em **2026-09-14**, nesta missão, e batem palavra por
palavra com o que a C5 registou em 2026-09-11. Nada mudou em três dias.

**Fonte:** `developers.google.com/youtube/terms/developer-policies`

| secção | texto (verbatim) | o que fecha |
|---|---|---|
| **III.I.7** | «separate, isolate, or modify the audio or video components of any YouTube audiovisual content» | **`FETCH_AUDIO_STREAM`** |
| **III.E.1.a** | «download, import, backup, cache, or store copies of YouTube audiovisual content without YouTube's prior written approval» | **preservar os bytes** |
| **III.I.14** | «use any technology other than YouTube API Services to access or retrieve API Data, including to access any portion of any YouTube audiovisual content» | **`yt-dlp` como adaptador** |

```
A III.I.7 NÃO FALA DE «BAIXAR VÍDEO». FALA DE SEPARAR O ÁUDIO.
E SEPARAR O ÁUDIO ERA, LITERALMENTE, O PLANO B.
```

A esperança implícita do briefing era que o veredito do vídeo fosse largo demais
e que o áudio coubesse por baixo dele. É o contrário: **o áudio tem cláusula
mais específica que o vídeo.** E a III.E.1.a fecha o passo seguinte de qualquer
maneira — mesmo que os bytes chegassem, preservá-los precisa de aprovação
escrita, e preservar é o que o `§9` do briefing exigia como prova.

Esta casa usa a Data API com `YOUTUBE_DATA_API_KEY`, logo é um *API Client* e
está presa a estas políticas, não apenas ao `robots.txt`.

```
QUEM PEGA NA CHAVE PEGA NO CONTRATO QUE VEM COM ELA.
```

### E a legenda, pelo mesmo critério

- **`captions.download`** — «This method is requires the user to have permission
  to edit the video.» Para canal de terceiro **não há rota oficial**. Não é
  limite de chave: é limite de **permissão**, e a chave da porta é do dono do
  vídeo.
- **`captions.list`** — exige OAuth, e *«the API response does not contain the
  actual captions»*. Listar uma faixa nunca foi o mesmo que poder lê-la.
- **`timedtext`** — a `baseUrl` real de `captionTracks` aponta para
  `/api/timedtext`, coberta por `Disallow: /api/`; e os ToS cobrem o acesso
  automatizado independentemente do caminho.

---

# E · O PORTÃO, LIDO AGORA — e ele discrimina

`provas/a_legenda_e_o_audio_do_youtube.py` não herda o veredito: busca o
`robots.txt` **vivo** do hospedeiro, com o `User-Agent` real desta coleta, sobre
os caminhos **reais** de cada rota. Medido nesta máquina, hoje:

| caminho | capacidade | veredito |
|---|---|---|
| `/api/timedtext?v=…` | `FETCH_PUBLIC_CAPTION` | **`ROBOTS_DISALLOWS`** |
| `/watch?v=…` | `FETCH_PUBLIC_CAPTION` | `ROBOTS_ALLOWS` |
| `/youtubei/v1/player` | `FETCH_AUDIO_STREAM` | **`ROBOTS_DISALLOWS`** |
| `/get_video?video_id=…` | `FETCH_AUDIO_STREAM` | **`ROBOTS_DISALLOWS`** |
| `/oembed?url=…` | `FETCH_VIDEO_METADATA` | `ROBOTS_ALLOWS` |

Duas coisas que esta tabela prova e que uma tabela só de recusas não provaria:

1. **A rede está aberta.** Cada linha — recusa inclusive — é uma resposta que
   chegou. `RECUSA É POLÍTICA; AUSÊNCIA DE RESPOSTA É REDE.` Consertam-se em
   sítios diferentes, e a C4F já pagou o preço de os confundir.
2. **O portão discrimina.** Barrou três e deixou passar dois. Um portão que só
   recusa não está a medir nada.

E `/watch` passar **não abre a legenda**: os ToS dependem de *quem* acede, não
de *qual* caminho. A excepção é para motor de busca público; esta casa não é um,
e não tem permissão escrita.

```
ROBOTS.TXT DIZ QUE CAMINHOS UM MOTOR DE BUSCA PODE PERCORRER.
OS TERMOS DIZEM QUEM PODE PERCORRÊ-LOS DE FORMA AUTOMATIZADA.
LER SÓ O PRIMEIRO É LER METADE DA LEI.
```

---

# F · O CANÁRIO — e por que ele não tem `SOURCE_ID`

O `§12` pedia UM vídeo curto de fonte italiana já provada. Ele existe, e é real:
`data/samples/SOCIAL-IT/YOUTUBE-PILOTO-IT.json`, cinco canais resolvidos pela
Data API oficial, 15 `videoId` italianos.

| campo | valor |
|---|---|
| `SOURCE_ID` | **`NÃO SEI`** |
| `SOURCE_NAME` | `Agronotizie - Notizie per l'agricoltura` |
| `PLATFORM_VIDEO_ID` | `MCnd9c2pzd8` |
| `CHANNEL_ID` | `UCUs2Mg7jvUTRt7_MSOFYM5Q` |
| `DOCUMENT_ID` | **`NÃO SEI`** |
| `DOCUMENT_ID_PROVEN` | `NO` |

**O `SOURCE_ID` é `NÃO SEI` por medição, não por preguiça.** O próprio piloto
escreve: `KNOWN_SOURCE = NENHUMA — ONE_SHOT não consulta memória`. Nenhuma das
cinco entradas alocou identidade no registo de fontes.

Derivar um a partir do handle, da URL ou do `CHANNEL_ID` seria fabricar
identidade — `COL-LAW-206` diz que a URL não é uma das três — e o `§11` do
briefing proíbe-o por escrito. E criar a fonte aqui esbarraria no `§12`, que
proíbe criar fonte nova nesta missão.

```
ESTE É UM TERCEIRO BLOQUEIO, INDEPENDENTE DOS OUTROS DOIS.
Mesmo com a política aberta e a credencial presente, o canário não teria
identidade para carregar a linhagem.
```

---

# G · OS TRÊS BLOQUEIOS, E ELES NÃO SE SUBSTITUEM

```
1 · POLÍTICA      III.I.7 · III.E.1.a · III.I.14 · ToS · captions.download
                  fecha CAPTION e fecha AUDIO. Conserta-se com AUTORIZAÇÃO.

2 · CREDENCIAL    YOUTUBE_DATA_API_KEY = AUSENTE nesta máquina.
                  Fecha até a rota PERMITIDA (metadata oficial).
                  Conserta-se com a chave.

3 · IDENTIDADE    nenhum SOURCE_ID italiano de YouTube no registo.
                  Conserta-se com uma missão de fonte, que é de gente.
```

Levantar **um** não abre a estrada. É por isso que os três estão escritos
separados: quem ler «YouTube = bloqueado» vai comprar a chave e descobrir que
não era isso.

---

# H · O SEGUNDO DEFEITO — `VIDEO_OUTPUT_HAS_CONSUMER`

Remedido nesta missão, com `provas/o_video_tem_consumidor.py`. **Continua `NO`,
e agora está localizado com precisão:**

```
VIDEO_LARGA_EM_DECLARADO  = YES   a receita nomeia data/samples/REEL-TRANSCRICOES
VIDEO_NO_RETORNO          = NO    nenhum dos 6 alvos de `retorno` está nessa pasta
VIDEO_ESPECIE_ATRAVESSA   = NO    as espécies são CATALOG/PLAN/RUN_RECEIPT
                                  e só ('COLHEITA',) atravessa
VIDEO_OUTPUT_HAS_CONSUMER = NO
```

`PRODUCER` = `ferramentas/reel_transcricao.py` ·
`CONSUMER` = `orquestrador.a_colheita()` → `retorno_da_coleta.so_o_que_entra()` ·
`SPECIES` exigida = `COLHEITA`, e isso está **provado pelo contrato**
(`ENTRAM_NO_INGRESSO = (COLHEITA,)`), não pelo briefing.

**E o conserto não é uma linha na receita.** `pedido/receitas.py` escreve, no
próprio ficheiro, por que o `LEGADO` **não pode** declarar `COLHEITA`: uma
declaração escrita na receita é feita *antes* da corrida e envelhece sozinha. A
única origem legítima de `COLHEITA` é um `ENVELOPE` que a corrida emite.

Logo o conserto é: **o dono da transcrição passar a emitir um envelope
declarando as unidades como `COLHEITA`, e a receita nomear esse envelope em
`retorno`.**

**Não foi escrito, e a razão é a mesma de sempre.** Sem bytes nesta árvore
(`VIDEO_BYTES_NESTA_ARVORE = 0`) e com a aquisição fechada, essa declaração
seria encanamento que ninguém pode exercitar — e uma rota declarada e nunca
corrida é exactamente o defeito que esta linha de missões veio fechar.

```
CAN DO != DID DO.
E CONSERTAR UM DEFEITO COM OUTRO DA MESMA FAMÍLIA NÃO É CONSERTAR.
```

O que **muda** com esta medição: o defeito deixa de ser «o transcritor não tem
consumidor» e passa a ser `COL-LAW-505 · ligar o runtime`, que a própria lei já
declara como missão à parte. É a mesma dívida, agora com dono e nome.

---

# I · RED TEAM — 24 ataques, e o que sobreviveu

Nada foi adquirido, então a maioria dos ataques pergunta: **este documento
comete o erro?**

| # | ataque | resultado |
|---|---|---|
| 1 | metadata confundida com mídia | `oembed` está na tabela como `FETCH_VIDEO_METADATA`, e a secção B separa as quatro capacidades · **MORTO** |
| 2 | URL resolvida confundida com bytes | nenhuma URL foi resolvida; `AUDIO_BYTES = 0` declarado · **MORTO** |
| 3 | manifest confundido com bytes | nenhum manifesto foi pedido · **MORTO** |
| 4 | caption inacessível chamada ausente | `CAPTION_STATUS = CAPTION_NOT_ACCESSIBLE`, nunca `NOT_AVAILABLE` · **MORTO** |
| 5 | automatic caption chamada manual | `CAPTION_KIND = UNKNOWN`, e o porquê está escrito · **MORTO** |
| 6 | caption chamada transcript | a matriz chama a capacidade `FETCH_TRANSCRIPT`; este documento distingue-as na secção D · **MORTO, com ressalva** (o nome da capacidade é herdado e impreciso — registado, não corrigido) |
| 7 | transcript substitui caption | nenhum dos dois existe nesta corrida · **N/A** |
| 8 | áudio chamado vídeo | `ACQUISITION_MEDIA_KIND` não foi declarado porque não houve aquisição · **MORTO** |
| 9 | audio-only sem bytes | `AUDIO_ONLY_FETCHED = NO`, `AUDIO_BYTES = 0` · **MORTO** |
| 10 | stream URL usada como identidade | nenhuma stream URL foi obtida · **MORTO** |
| 11 | `SOURCE_ID` fabricado da URL | `SOURCE_ID = NÃO SEI`, com o motivo medido (secção F) · **MORTO** |
| 12 | `DOCUMENT_ID` fabricado do SHA | `DOCUMENT_ID = NÃO SEI`, `DOCUMENT_ID_PROVEN = NO` · **MORTO** |
| 13 | adapter chamado fora do orquestrador | nenhum adaptador foi chamado · **MORTO** |
| 14 | `yt-dlp` vira segundo orquestrador | `YT_DLP_PRESENTE = NO`; não foi instalado · **MORTO** |
| 15 | RUN nasce depois da aquisição | não houve corrida de aquisição · **N/A** |
| 16 | RAW sem RUN | nenhum RAW criado · **MORTO** |
| 17 | producer escreve e consumer não lê | **VIVO, e é o achado da secção H** — medido, localizado, não consertado |
| 18 | envelope declara ficheiro inexistente | nenhum envelope foi escrito · **MORTO** |
| 19 | COLHEITA sem conteúdo | nenhuma colheita declarada · **MORTO** |
| 20 | GPU selecionada e CPU executa | ASR não correu; `DEVICE_USED = NOT_RUN` · **MORTO** |
| 21 | erro do extractor vira `CONTENT_ABSENT` | não houve extractor; e a secção D separa `NOT_ACCESSIBLE` de `NOT_AVAILABLE` · **MORTO** |
| 22 | retry duplica RAW | não exercitável sem aquisição · **N/A** |
| 23 | Espanha/França entram no canário italiano | o canário é `COUNTRY_SCOPE = IT`; os transcripts de reel em árvore são de outra plataforma e **não** foram usados como prova · **MORTO** |
| 24 | System Map mostra vídeo inteiro quando só áudio foi adquirido | o mapa não ganhou rota nenhuma, porque nada foi adquirido · **MORTO** |

```
RED_TEAM_SURVIVORS = 1   (#17, declarado e não escondido)
```

O sobrevivente é o defeito que a secção H mede. Ele não morre nesta missão
porque matá-lo exige exercitá-lo, e exercitá-lo exige a aquisição que a secção
D fecha.

---

# J · ENTREGA TÉCNICA

```
BRANCH                    = claude/youtube-italia-caption-audio-8b460b
START_HEAD                = f437ff1140fa97484ca9695b341fbe9ca0a9f050
BASE_ESCOLHIDA            = 611e7cbf406147c0ab057e9ffa7775f6fa11e8a1
REMOTE_HEAD               = NÃO EXISTE (branch não publicada)

YOUTUBE_OWNER             = coleta/adaptador_youtube.py
ACQUISITION_POLICY_VERDICT= BLOCKED_NEEDS_AUTHORIZATION
POLICY_DECISION_REQUIRED  = YES

SOURCE_ID                 = NÃO SEI
PUBLIC_URL                = https://www.youtube.com/watch?v=MCnd9c2pzd8
PLATFORM_VIDEO_ID         = MCnd9c2pzd8
DOCUMENT_ID               = NÃO SEI
DOCUMENT_ID_PROVEN        = NO

REQUEST_ID                = NÃO CRIADO
RUN_ID                    = NÃO CRIADO
RAW_OBSERVATION_ID        = NÃO CRIADO
STORAGE_OBJECT            = NÃO CRIADO

CAPTION_ROUTE             = NENHUMA PERMITIDA
CAPTION_STATUS            = CAPTION_NOT_ACCESSIBLE
CAPTION_KIND              = UNKNOWN
CAPTION_LANGUAGE          = UNKNOWN
CAPTION_BYTES             = 0

AUDIO_ONLY_REQUESTED      = NO   (bloqueado antes do pedido, por política)
AUDIO_ONLY_FETCHED        = NO
AUDIO_BYTES               = 0
AUDIO_CODEC               = N/A
AUDIO_DURATION            = N/A
AUDIO_SHA256              = N/A

FULL_VIDEO_FETCHED        = NO      (esperado: NO)

DEVICE_USED               = NOT_RUN
MODEL_USED                = NOT_RUN
TRANSCRIPTION_SECONDS     = NOT_RUN

TRANSCRIPT_OUTPUT_WRITTEN   = NO
TRANSCRIPT_OUTPUT_DECLARED  = NO
TRANSCRIPT_OUTPUT_CONSUMED  = NO
CONSUMER                    = orquestrador.a_colheita() → so_o_que_entra()

STRUCTURED_CREATED        = NO
ADMISSION_DECISION        = NÃO EXECUTADA

PAID_USD                  = 0,00
APIFY_RUNS                = 0

RETRY_DUPLICATION_ERRORS  = N/A (sem aquisição, sem retry)
RED_TEAM_SURVIVORS        = 1 (#17, declarado)
NEW_FAILURES              = 0

SYSTEM_MAP_CHECK          = PASS
LOCAL_YOUTUBE_PIPELINE    = FAIL (por autorização, não por técnica)
READY_TO_TEST_SALA_IN_CI  = NO
```

**Base da suíte, medida nesta máquina antes e depois:** a falha
`nenhuma casa nasce autorizada` (`tests.test_metricas`) existe **sem** as
alterações desta missão. `NEW_FAILURES = 0` é comparação por nome, não por
contagem.

---

# K · O QUE MUDOU NO CÓDIGO

```
provas/a_legenda_e_o_audio_do_youtube.py        NOVO
system-map/data/youtube-legenda-audio.generated.json  NOVO (gerado)
system-map/data/state.generated.json            regenerado (nome da branch)
```

**Uma prova, e nenhum adaptador.** A prova mede o portão vivo em vez de o
declarar — que é a lição que a C4F pagou para aprender. Sem ela, a resposta
desta missão viraria um literal escrito à mão, e o próximo agente a lê-lo não
saberia se ainda é verdade.

```
UM CAMPO QUE DIZ «BLOQUEADO» SEM TENTAR NÃO É MEDIÇÃO: É LEMBRANÇA DE OUTRO SÍTIO.
```

Ela **falha** no dia em que qualquer rota livre de legenda passar a
`PERMITIDA=SIM`, ou em que nascer uma capacidade de áudio na matriz — e essa
falha é o pedido de actualização deste documento.

`BIBLE_CHANGE = NENHUMA` · `CONTRACT_CHANGE = NENHUMA` · `KNOW_HOW_DELTA = NENHUM`
(o know-how canônico tem 16 documentos distintos e cinco cabeças divergentes;
escrever nele às cegas criaria a sexta).

---

# L · A ROTA DAQUI PARA A FRENTE

**Para YouTube, a única estrada permitida é a Data API v3**, e ela dá quatro
das cinco capacidades — busca, incremental, metadata e comentários. Dá
**zero** de legenda para canal de terceiro, e zero de áudio.

O passo seguinte que **não** depende de autorização do YouTube:

```
1 · provisionar YOUTUBE_DATA_API_KEY
    -> abre SEARCH, INCREMENTAL, METADATA e COMMENTS
       US$ 12,20 de US$ 12,81 do gasto Apify histórico desta casa
       (comments US$ 7,73 + scraper US$ 4,47)
       fonte: docs/operacao/PROXIMA-MISSAO-YOUTUBE.md, que soma COST_USD
       por ator nos manifestos — número herdado, não remedido aqui
2 · alocar SOURCE_ID para os canais italianos do piloto
3 · ligar o runtime da COL-LAW-505 (o envelope de COLHEITA)
```

⚠️ **E os US$ 0,13 de `pintostudio~youtube-transcript-scraper` NÃO entram
nessa conta.** Esses são legenda, e a chave não os abre — a `captions.download`
continua a pedir permissão do dono do vídeo. Somá-los daria 96% e prometeria
uma poupança que a política não entrega.

```
A CHAVE ABRE QUATRO CAPACIDADES DE CINCO.
O QUE SOBRA É JUSTAMENTE O QUE ESTA MISSÃO VEIO BUSCAR.
```

Os passos que **dependem** de decisão de gente, e que esta missão não pode
tomar:

```
CAPTION  -> permissão escrita do YouTube, ou autorização do dono de cada vídeo
AUDIO    -> permissão escrita do YouTube (III.I.7 + III.E.1.a)
```

E há uma terceira via que já existe e não precisa de nenhuma das duas: **a fala
italiana não tem de vir do YouTube.** O `SOURCE_ID` de uma fonte italiana que
publique áudio ou vídeo em superfície própria não carrega nenhuma destas
cláusulas. Medir isso é missão de fonte, não de adaptador.

```
A PERGUNTA «COMO TIRO ÁUDIO DO YOUTUBE» TEM TRÊS AUTORIDADES A DIZER NÃO.
A PERGUNTA «ONDE MAIS ESTÁ ESSA FALA» NÃO FOI FEITA AINDA.
```
