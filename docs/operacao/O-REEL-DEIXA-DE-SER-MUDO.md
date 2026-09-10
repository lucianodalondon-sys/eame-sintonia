# O REEL DEIXA DE SER MUDO

> Missão REELS + TRANSCRIÇÃO V1 · medido em 2026-09-10
> Base: `claude/raw-observation-identity-3jbwco` @ `00a6aa35` (a fundação com B5B)

---

## O BURACO, EM UMA FRASE

Um Reel pode falar noventa segundos sobre pressão de septoriose, produto, estágio de
aplicação e região — e trazer como legenda apenas «Confira nosso dia de campo».

`coleta/comunicacao_classificar.py` lia `TITLE` e `TEXT`. E `TEXT` **é a legenda**.

```
LEGENDA != FALA. São dois textos, de dois atos diferentes do mesmo minuto.
```

Todo o conteúdo técnico falado era invisível para o SINTONIA.

---

## O CASO REAL QUE PROVA O BURACO

Reel `Db5QG2Dk3sF`, conta `@syngenta.es` — uma das autorizadas em `CONTAS-V1.json`.

**O que a legenda diz** (é o que a classificação lia):

> 🗣️ "Syngenta es una empresa de ciencia agrícola" ⁣Nuestro compañero Federico
> González, director de Desarrollo para el Sur de Europa, participa en LA TIERRA
> Podcast…

**O que a fala diz** (112 segundos que ninguém ouvia):

> Syngenta no es una empresa de fertilizantes pero es mucho más que una empresa de
> fitosanitarios, es una empresa de ciencia agrícola y además de las herramientas que
> ya he comentado antes de **escaneo de suelo**, **herramientas digitales** y de
> **agricultura de precisión**, el desarrollo de **microorganismos**…

A legenda é um convite. A fala é o conteúdo.

---

## O QUE PASSOU A EXISTIR

| peça | o que é | por que existe |
|---|---|---|
| `ferramentas/fala_local.py` | o **dono único** do reconhecimento de fala | a mesma lógica vivia DUAS vezes — o cabeçalho de `youtube_transcrever.py` dizia por escrito que copiou de `instagram_transcrever.py`. Duas cópias da mesma lei são duas leis. |
| `ferramentas/reel_transcricao.py` | a **cadeia**: identidade → mídia → RAW → áudio → DERIVED | ligar as peças que já existiam, sem virar dono de nenhuma |
| `provas/reel_fala_qualidade.py` | a prova de que a fala escrita bate com a fala dita | «gerou texto» não é aprovação |
| `fase=transcrever` em T9 | a porta, no orquestrador que já existe | o botão pede; o orquestrador decide como |

E o que **não** nasceu: nenhum reconhecedor novo, nenhuma rota de chave nova, nenhum
contrato de artefato novo, nenhuma migration. `leis/artefato.py` ganhou uma linha —
`SPEECH_TRANSCRIPTION` — e nada mais.

---

## COMO UM REEL ATRAVESSA O SISTEMA

```
    URL de Reel público
      ↓  yt-dlp, endereço direto, grátis
    METADADOS  (legenda, conta, data, duração)
      ↓
    MÍDIA      → data/raw/REEL-MIDIA/<shortcode>.mp4   (FORA do Git)
      ↓
    RAW        artefato com SHA256 e COLLECTED_AT
      ↓  ffmpeg → WAV 16 kHz mono
    ÁUDIO      meio de trabalho, não é artefato
      ↓  faster-whisper `medium`, na própria máquina
    DERIVED    artefato com PARENT_ARTIFACT_ID = o RAW, e os tempos de cada trecho
      ↓
    TRANSCRIPT_TEXT   ao lado de CAPTION_TEXT, nunca por cima
      ↓
    a classificação passa a casar termos nos DOIS, e a dizer em qual casou
```

---

## O QUE FOI PROVADO A CORRER

Dez Reels públicos reais. Nenhum privado, nenhum login, nenhum bypass.

| Reel | conta | língua | estado | veredito de qualidade |
|---|---|---|---|---|
| `C-FanW_CYMz` | `@syngentaitalia` ✓autorizada | IT | OK | **PARTIAL** 2/3 |
| `Db5QG2Dk3sF` | `@syngenta.es` ✓autorizada | ES | OK | **PASS** 3/3 |
| `C2b0GJrIJ8t` | `@rtl_france` | FR | OK | **PASS** 2/2 |
| `DW6X5lZkU41` | `@syngenta` | EN | OK | **PASS** 2/2 |
| `C6TiLBCCBz8` | `@syngentaus` | EN | REQUESTED_EMPTY | música, sem fala |
| `C-63RfHoJTU` | conta agro FR | FR | REQUESTED_EMPTY | máquina, sem fala |
| `CuU0NGVAO9U` | conta agro FR | FR | REQUESTED_EMPTY | sem fala |
| `DQhloXtjTep` | `@syngenta` LAN | — | REQUESTED_EMPTY | sem fala |
| `DCZQ6A3hvEC` | `@albaughllc` | — | NOT_REQUESTED | falha controlada de mídia |
| `ZZZZZZZZZZZ` | não existe | — | NOT_REQUESTED | falha controlada de identidade |

**467,9 s de áudio em 210,3 s de máquina — 2,23x o tempo real, sem GPU, zero dólares.**

O caso IT é **PARTIAL** e não PASS: mesmo com `medium`, a marca sai «di singenta». Não se
arredonda para cima.

---

## O MODELO SUBIU, E O MOTIVO NÃO É VELOCIDADE

Medido sobre os próprios Reels do corpus, não sobre um teste sintético:

| o que foi dito | `small` escreveu | `medium` escreveu |
|---|---|---|
| **mais** (a cultura) | «MICE» | «mais» |
| maiscoltori | «mai scoltori» | «maiscoltori» |
| Discovery Seeds | «Discovery Seats» | «Discovery Seeds» |
| eventi | «venti» | «eventi» |
| **Syngenta** (ES) | «Singentha» | «Syngenta» |

```
A FRASE ESTAVA CERTA NAS DUAS. O SINAL SÓ ESTAVA NUMA.
```

Num corpus que existe para saber **de que cultura** e **de que marca** o concorrente
fala, «MICE» não é imprecisão de transcrição — é o sinal perdido, em silêncio, com o
texto a parecer normal. `medium` custa ~2,8x mais tempo e continua acima do tempo real.

O padrão da cadeia de Reel subiu para `medium`. `fala_local.MODELO_PADRAO` fica em
`small`: os dois programas de lote que já existiam foram orçados nele.

---

## QUATRO DEFEITOS REAIS, ENCONTRADOS A CORRER

1. **`...` a passar por transcrição.** Sobre música sem fala o reconhecedor devolveu três
   pontos, com estado `OK`. Iam para a classificação como se fossem a fala do vídeo.
   Sem uma letra ou algarismo não é fala escrita, e o que veio fica em
   `DISCARDED_OUTPUT`.

2. **O livro indexado pelo resultado.** A chave do lote era o DERIVADO. Quando a mesma
   publicação corria outra vez e o resultado MUDAVA de estado, a corrida nova caía
   noutra chave e ficavam duas linhas — a antiga a afirmar um texto já sabido lixo.
   A chave passou a ser o CONTEÚDO OBSERVADO (o RAW).

3. **`TRANSCRIPT_STATE = OK` sempre.** `youtube_transcrever.py` escrevia `OK` mesmo com
   texto vazio.

4. **Vídeo a caminho do Git.** `data/samples/` é versionado, e o `audio-cache/` do
   transcritor de Instagram apontava para lá. Um mp4 entra no pack pelo tamanho
   integral, para sempre.

---

## O DEFEITO QUE A PESQUISA ENCONTROU, E QUE FOI CONFERIDO NO CÓDIGO DA BIBLIOTECA

`BatchedInferencePipeline._batched_segments_generator` do `faster-whisper 1.2.1`
**não aplica** `no_speech_threshold`, `log_prob_threshold` nem
`compression_ratio_threshold`. Ele só os *reporta* por trecho. Também fixa
`hallucination_silence_threshold=None` e `temperatures=temperature[:1]`.

```
PASSAR UM PARÂMETRO NÃO É O MESMO QUE ELE SER APLICADO.
```

`fala_local._sem_os_mudos()` passou a aplicar por fora a MESMA conjunção que o caminho
sequencial da biblioteca usa.

**E aqui está a parte honesta:** essa trava, sozinha, **não** teria salvo o caso real.
A alucinação medida — a palavra «Music» sobre dez segundos de música corporativa — saiu
com `no_speech_prob = 0,380` (abaixo do limiar de 0,6) e `avg_logprob = -1,509`.
A conjunção exige as duas, e a primeira não se verificou.

**Quem salvou foi o detector de voz.** Com `vad_filter=True` o mesmo áudio deu zero
trechos. A ordem de defesa é: **(1) VAD**, que foi o que mordeu; (2) a trava de limiares,
que é a rede que o modo em lote não estende sozinho; (3) `_tem_conteudo`, para o `...`.

A trava não foi endurecida para apanhar o «Music»: bastaria descartar por `avg_logprob`
sozinho, e isso deitaria fora fala real gravada ao vento, num trator, no meio de um
campo — que é metade do que este corpus tem.

---

## OS TRÊS CAMINHOS, COMPARADOS

| caminho | captura real | transcrição real | IT | ES | FR | EN | custo | dependência |
|---|---|---|---|---|---|---|---|---|
| **1 · Apify transcript** | NOT_TESTED | NOT_TESTED | — | — | — | — | $0,60 (tabela) | total |
| **2 · Apify captura + ASR local** | NOT_TESTED | PASS | — | — | — | — | $0,82 (tabela) | parcial |
| **3 · Captura local + ASR local** | **PASS** | **PASS** | PARTIAL | PASS | PASS | PASS | **$0,00** | média |

Custos projetados sobre o corpus medido, tier FREE, preço de tabela lido da API pública
da Apify em 2026-09-10 — **não são fatura**.

### O preço da Apify, lido e não presumido

`apify/instagram-reel-scraper`, build 0.0.566, `PAY_PER_EVENT`:

| evento | FREE | BRONZE | DIAMOND | unidade |
|---|---|---|---|---|
| `actor-start` | $0,001 | $0,001 | $0,001 | uma vez por run |
| `reel` | $0,0026 | $0,0023 | $0,0004 | por reel no dataset |
| `transcript` | **$0,048** | $0,041 | $0,010 | **por minuto INICIADO por reel** |
| `video-download` | $0,020 | $0,015 | $0,007 | **por 1 MB INICIADO por reel** |
| `shares-count` | $0,007 | $0,006 | $0,002 | por reel |

«Por minuto INICIADO» não é detalhe: um reel de 61 s paga **dois** minutos. O corpus
medido tem 7,8 minutos de áudio e pagaria **12**.

E o ator que a casa usa hoje — `apify/instagram-scraper`, build 0.0.779 — **não tem**
`includeTranscript` nem `includeDownloadedVideo`. A preço nenhum.

---

## O QUE ESTA CADEIA NUNCA DECIDE

```
FACT_LOCATION = NOT_KNOWN
FACT_TIME     = NOT_KNOWN
```

Ouvir «Puglia» é prova de que alguém disse «Puglia» — não de que o fato aconteceu lá.
Transcrição é evidência para uma camada acima; não é julgamento.

E `RAW_OBSERVATION_ID` continua a ser `raw_asset.id`. O `SHA256` identifica **bytes**,
nunca observação — dois RUNs que tragam o mesmo vídeo têm o mesmo SHA256 e são duas
observações.

---

## O QUE AINDA NÃO SABEMOS

- **A rota paga nunca correu.** `APIFY_TOKEN_POOL` é secret do GitHub e chega aos
  workflows do runner local; não existe no ambiente desta missão. Contrato e preço foram
  lidos pela rota pública, de graça. **Ator existir não é ator ter rodado.**
- **Descobrir não é buscar.** Listar os Reels de um perfil devolve 302 para
  `/accounts/login/` e HTTP 429 no extractor de perfil, de IP de datacenter. Dá para
  baixar um Reel cujo endereço já se tem; não dá para varrer uma conta.
- **A captura não é determinística.** ~1 em cada 6 chamadas devolve «Instagram sent an
  empty media response» sem sinal de limite. Há retry declarado, e uma falha nunca sai
  como «não há vídeo».
- **Não há conta francesa autorizada.** No `CONTAS-V1.json`, `cortevabiologicals` (FR)
  está `COLLECTION_AUTHORIZED = NO`. O francês foi provado com contas públicas fora do
  universo autorizado — a capacidade está provada, a cobertura do corpus não.
- **A precisão por palavra.** Não há transcrição oficial destes Reels. Inventar um
  denominador seria pior do que não medir. O que existe é PASS/PARTIAL/FAIL por caso,
  com os termos esperados e a origem de cada um à vista.
