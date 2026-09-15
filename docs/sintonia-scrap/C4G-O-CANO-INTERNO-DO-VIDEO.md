# C4G · O CANO INTERNO DO VÍDEO — o que atravessa, e onde exactamente para

> **O vídeo italiano real atravessou metade da estrada, e a metade que ele
> atravessou foi medida byte a byte.** Vídeo → áudio → transcrição na GPU:
> feito, com o texto certo e a língua detectada.
>
> **A outra metade parou, e agora sabe-se em que linha.** Não numa, em três — e
> este documento dá nome a cada uma.

```
VIDEO_INTERNAL_PIPELINE      = PARTIAL
FULL_VIDEO_TO_WAITING_ROOM   = BLOCKED_NO_DISPOSABLE_POSTGRES
VIDEO_OUTPUT_HAS_CONSUMER    = NO   (e continua, por duas causas nomeadas)
NEW_VIDEO_ACQUISITION        = NO   (nenhum byte novo, nenhuma rede de conteúdo)
```

---

# A · O VÍDEO É LEGÍTIMO E RASTREÁVEL — ATÉ ONDE O REGISTO CHEGA

```
LOCAL_PATH   C:/…/INSTAGRAM-TRANSCRICOES/audio-cache/DcNkh7LCW4u.mp4
BYTES        9 218 753
SHA256       0da99d1ddd4cdcc2410231b98599843d0318b2c76e11c26567bd14a92d95bd60
MEDIA_TYPE   video/mp4  (h264 + aac, medido por `ffprobe`)
DURATION     29,716 s
```

O registo preservado (`TRANSCRICOES.json`, escrito em 2026-09-02) declara:

| campo | valor |
|---|---|
| `ACCOUNT_HANDLE` | **`bayer_italia`** · COMPANY `BAYER` · `COUNTRY_SCOPE = IT` |
| `SOURCE_URL` | `https://www.instagram.com/reel/DcNkh7LCW4u/` |
| `PUBLISHED_AT` · `CAPTURED_AT` | 2026-08-19T10:00:07Z · 2026-09-02T16:01:20Z |
| `MISSION` | `14-COMUNICACAO-PUBLICA-DO-CONCORRENTE` |
| `SOURCE_ID` | `INSTAGRAM-TRANSCRICOES/TRANSCRICOES` |

E `bayer_italia` está em `COMPETITOR-PUBLIC-COMM/CONTAS-V1.json` com
`ACCOUNT_IDENTITY_STATE = PROVED`, evidenciado pelo site oficial italiano da
Bayer declarar o link — primeira parte a falar de si própria, não busca por nome.

### E o que **não** se consegue provar, e fica `UNKNOWN`

```
ORIGINAL_RUN_ID              = UNKNOWN
ORIGINAL_RAW_OBSERVATION_ID  = UNKNOWN
ORIGINAL_STORAGE_OBJECT      = UNKNOWN
RUNNER_NAME                  = NOT_KNOWN   (está assim no próprio registo)
```

O material é anterior ao contrato de identidade da observação (migrações
026–029). Ele tem fonte, tem hora e tem bytes; **não tem corrida nem
observação**, porque na altura não havia onde as escrever.

```
NÃO SE FABRICA. Inventar-lhe um RUN_ID daria uma corrida que nunca existiu.
```

---

# B · O QUE ATRAVESSOU, E FOI MEDIDO

### VÍDEO → ÁUDIO

```
PARENT_VIDEO_SHA256  0da99d1ddd4cdcc2410231b98599843d0318b2c76e11c26567bd14a92d95bd60
AUDIO_SHA256         54063116e7cfbda00464a9fc021e0e5d5353c8b0fe954cc611741edc557c9034
AUDIO_BYTES          947 620       AUDIO_DURATION  29,61 s
EXTRACT_SECONDS      0,19
```

O original **não foi tocado**: lido, nunca reescrito, nunca apagado. Confirmado
depois por varredura — a pasta do acervo continua com os mesmos 16 ficheiros e
nenhum com data de hoje.

### ÁUDIO → TRANSCRIÇÃO, NA PLACA

`SINTONIA_ASR_DEVICE=GPU`, com o padrão global intocado em `CPU`:

```
ASR_DEVICE_REQUESTED   GPU     ASR_DEVICE_SELECTED   GPU
ASR_DEVICE_EXECUTION   PROVEN  ASR_DEVICE_USED       GPU
ASR_ACCELERATOR        CUDA    ASR_DEVICE            cuda/int8_float32
ASR_COMPUTE_REQUESTED  float16 -> SELECTED  int8_float32
ASR_WHY_COMPUTE_FALLBACK        COMPUTE_TYPE_UNSUPPORTED
MODEL_REQUESTED = MODEL_USED = small

LANGUAGE           it   ·  LANGUAGE_SOURCE = DETECTED  ·  confiança 0,989
AUDIO_SECONDS      29,61      MACHINE_SECONDS   1,93
MODEL_PREPARE      3,71 s     REALTIME_FACTOR   15,34x
TRANSCRIPT_CHARS   379
TRANSCRIPT_SHA256  9bc69e6fa31ce43fa71cd2a2064d2cbb88a8d39131f965e50c6c1cc50ecd8ef0
```

> «Sapete quale è la magia dell'estati italiane? È il vento caldo che attraversa
> le vie del paese. È la meraviglia di tramonti tra i campi…»

**A língua foi DETECTADA, não assumida.** `it` com 0,989 — e não «é italiano
porque a conta é italiana».

### CAPTION

```
CAPTION_STATUS = NOT_APPLICABLE_PROVEN
```

E é uma prova, não uma suposição: o adaptador do Instagram declara, por escrito,
que `instagram.native_caption` **não existe** na matriz de capacidades — «o
Instagram NÃO serve legenda nativa; o que ele serve é o texto do autor, que é
CAPTION, não TRANSCRIPT». Não houve comparação caption×transcript porque não há
caption a existir, e não porque não se conseguiu ir buscá-la.

---

# C · ONDE PAROU — TRÊS CAUSAS, TODAS MEDIDAS

## C1 · Sem PostgreSQL não há OBSERVAÇÃO, e sem observação não há o que derivar

Corri a porta canónica de verdade — `ing.receber()` — com os bytes reais do
vídeo e `memoria=None`:

```
ACEITE SHA256      0da99d1ddd4cdcc2…    (os bytes certos)
ACEITE BYTES       9 218 753
RECUSAS            []                   (a porta não recusou o vídeo)
FONTE_PROVADA      INSTAGRAM-TRANSCRICOES/TRANSCRICOES
bytes no armazém   1 ficheiro escrito   (o original foi preservado)

MEMORIA            {"TENTADA": false, …, "COMO_FOI_MEDIDO": "NAO MEDIDO"}
RAW_OBSERVATIONS   []
PARA_A_DERIVACAO   []
SEM_BYTES_PARA_DERIVAR  []
```

Os bytes preservam-se sem banco. **A observação não.** `preservar()` lê as
observações DE VOLTA do Postgres depois de escrever; sem `memoria`, a lista
nasce vazia — e `unidades_para_a_derivacao` itera essa lista.

E repare no que isso produz:

```
O VÍDEO NÃO ESTÁ NA LISTA DE DERIVAR, E TAMBÉM NÃO ESTÁ NA DE SALTADOS.
«preservei um e derivei zero» lê-se exactamente como «não preservei nada».
```

```
POSTGRES_DISPOSABLE_AVAILABLE = NO
psql · postgres · pg_ctl · initdb · docker   NENHUM
DATABASE_URL · EAME_TEST_DSN · SINTONIA_SALA_DSN · SUPABASE_DB_URL   AUSENTES
porta 5432   fechada
```

Nada foi instalado, como a missão manda.

## C2 · A espécie do vídeo era apagada à entrada — **e isto foi consertado**

Este é o defeito que **não** dependia de banco nenhum, e estava escondido debaixo
do outro.

O item entrava na porta a declarar `CONTENT_TYPE: video/mp4`. A ficha do contrato
comum saía assim:

```
CONTENT_TYPE = "NAO SEI"
```

Porque `leis/artefato.raw_do_disco` deduzia a espécie de uma tabela de **quatro
extensões** (`.pdf .txt .json .html`) e **deitava fora** o que o coletor tinha
declarado — `CONTENT_TYPE` nem sequer estava em `ingresso.DO_COLETOR`.

E `NAO SEI` não é neutro. `_quem_deriva_aceita` trata a ausência como «tenta», de
propósito e com razão:

```
_quem_deriva_aceita('NAO SEI')   -> True     ← o vídeo seguiria
_quem_deriva_aceita('video/mp4') -> False
```

Ou seja: o MP4 seria entregue a `executor_texto_de_pdf`, e o `pdftotext` seria
chamado sobre um vídeo. A lei que evita exactamente isso — a porta da espécie —
já existia, já estava certa, e nunca recebia o dado de que precisava.

```
UMA TRAVA DE ESPÉCIE COM A ESPÉCIE APAGADA A MONTANTE NÃO PROTEGE NADA:
ELA SÓ NÃO TEM O QUE LER.
```

### O conserto, e por que **não** foi «acrescentar `.mp4` à tabela»

Esta casa já pagou por confiar na extensão: 46 ficheiros `.pdf` que eram a página
HTML do site, e o registo diz «a extensão também mente». Então a ordem passa a ser:

```
DECLARADO PELO OBSERVADOR  >  DEDUZIDO DO NOME  >  NAO SEI
```

Quem viu os bytes chegarem sabe mais do que o nome do ficheiro. Uma confissão
(`NAO SEI`, `NAO_SE_APLICA`, vazio) **não** vence a extensão — senão um coletor
que preenche o campo por hábito apagaria a dedução que ainda havia.

Provado, com o mesmo ficheiro, antes e depois:

```
sem o coletor declarar   'NAO SEI'    -> deriva? True   ← ia para o pdftotext
com o coletor a declarar 'video/mp4'  -> deriva? False  ← recusa correcta
o PDF continua a passar               -> True
sem declaração, a extensão continua a mandar
SHA256 e BYTES inalterados
```

`tests/test_c4g_a_especie_do_video.py` — 11 provas.

```
⚠️ E ISTO NÃO FECHA O DEFEITO PRINCIPAL.
PARAR DE ENTREGAR AO DONO ERRADO != ENTREGAR AO DONO CERTO.
```

## C3 · A porta da derivação conhece **um** executor, importado pelo nome

```python
def _capacidades_de_derivacao():
    import executor_texto_de_pdf as _ex        # ← um, e só este
    return (_ex.CAPACIDADE,)
```

Não é um registo: é uma lista de um, com forma de registo. E o próprio ficheiro
previu o problema, por escrito, muito antes desta missão:

> «no dia em que entrasse um executor de áudio os dois divergiam em silêncio»

**Nenhum executor de derivação de áudio existe.** Enquanto não existir e não for
declarado ali, `VIDEO_OUTPUT_HAS_CONSUMER` continua `NO`, mesmo com banco e com a
espécie declarada.

**Não foi escrito aqui, e a razão é medida, não preguiça:** `preservar_derivado`
— o dono da escrita do derivado — exige `memoria`, que é o Postgres que não
existe nesta máquina. Um executor novo nasceria sem poder correr uma única vez.

```
CAN DO != DID DO.
UMA ROTA DECLARADA E NUNCA CORRIDA É O DEFEITO QUE A PROVA DE FOGO ENCONTROU
NO WORKFLOW SOCIAL. REPETI-LO COM BOAS INTENÇÕES CONTINUA A SER REPETI-LO.
```

`tests/test_c4g…::T3OQueContinuaEmAberto` é a trava de método: ela **reprova no
dia em que um executor de áudio for declarado à porta**, e a mensagem diz o que
rever. É uma sentinela de estado, não um veredito sobre o executor.

---

# D · REPROCESSAMENTO NÃO DUPLICA — MEDIDO DUAS VEZES

Duas corridas, os mesmos bytes:

```
REPROCESS_RUN_1   REPROCESS-1-f2c4a6b9
REPROCESS_RUN_2   REPROCESS-2-ce62629b     RUNS DIFERENTES = True

ARTIFACT_ID_1 = ARTIFACT_ID_2 = RAW-0da99d1ddd4cdcc2     (iguais)
SHA256 igual nas duas
ficheiros no armazém:  1 depois da 1.ª  ·  1 depois da 2.ª
DUPLICOU O ORIGINAL = False
```

```
NEW RUN != NEW RAW OBSERVATION — e as duas corridas provam-no.
```

### Uma ressalva que não pode faltar

```
RAW_ID_1 = RAW_ID_2 = UNKNOWN
```

Eles são iguais porque **ambos estão ausentes** — não há banco, logo não há
`RAW_OBSERVATION_ID` nenhum. Ler isso como «a identidade foi preservada» seria o
mesmo erro de contar dois vazios como um acordo. O que ficou provado é o que se
pode provar sem banco: **o mesmo conteúdo dá o mesmo `ARTIFACT_ID` e não gera um
segundo original**.

---

# E · A CONTRAPROVA

A prova `o_video_tem_consumidor.py` mede, na mesma corrida:

```
VIDEO_LARGA_EM_DECLARADO  = YES    o ficheiro é escrito, e a receita sabe onde
VIDEO_OUTPUT_HAS_CONSUMER = NO
```

As duas linhas, lado a lado, **são** a contraprova: o ficheiro existe em disco e
o fluxo não existe. Nenhuma prova desta missão passa por o ficheiro estar lá.

```
FILE EXISTS != FLOW EXISTS.
```

---

# F · RED TEAM

| # | ataque | resultado |
|---|---|---|
| 1 | reprocessamento criando RAW novo | **PASS** — 1 ficheiro no armazém depois de 2 corridas |
| 2 | novo RUN confundido com nova observação | **PASS** — RUNs diferentes, `ARTIFACT_ID` igual |
| 3 | SHA usado como RAW_ID | **PASS** — `ARTIFACT_ID` é `RAW-<sha16>`, e `RAW_OBSERVATION_ID` é do banco, declarado `UNKNOWN` |
| 4 | filename usado como DOCUMENT_ID | **PASS** — nenhum `DOCUMENT_ID` criado |
| 5 | transcritor escreve mas consumer não lê | **MEDIDO E DECLARADO `NO`** |
| 7 | COLHEITA declarada sem conteúdo | **PASS** — nenhuma `COLHEITA` foi declarada |
| 8 | transcript sem vídeo pai | **PASS** — `PARENT_VIDEO_SHA256` registado |
| 9 | áudio sem vídeo pai | **PASS** — idem |
| 10 | GPU selecionada mas CPU usada | **PASS** — `EXECUTION = PROVEN` em GPU |
| 11 | compute fallback chamado `GPU_UNAVAILABLE` | **PASS** — saiu `COMPUTE_TYPE_UNSUPPORTED` |
| 12 | caption chamado transcript | **PASS** — `CAPTION_STATUS = NOT_APPLICABLE_PROVEN`, com a razão |
| 13 | tradução substituindo transcript | **PASS** — nenhuma tradução corrida |
| 18 | ficheiro local tratado como nova coleta | **PASS** — `RUN_TYPE = REPROCESS`, `NEW_VIDEO_ACQUISITION = NO` |
| 19 | PostgreSQL ausente tratado como Sala PASS | **PASS** — `BLOCKED_NO_DISPOSABLE_POSTGRES` |
| 20 | JSON tratado como Sala canónica | **PASS** — nenhum JSON fingiu de Sala |
| — | *a espécie apagada mandando vídeo ao extrator de PDF* | **APANHADO E CONSERTADO** |
| — | *escrevi no acervo por engano, ao apontar o armazém para lá* | **APANHADO POR MIM, E REVERTIDO** |

Os que **não** foram exercidos, e ficam ditos: 6, 14, 15, 16, 17 — todos exigem
STRUCTURED e ADMISSION, que exigem banco.

```
RED_TEAM_EXERCIDOS     = 15 de 20
RED_TEAM_SURVIVORS     = 0 dos exercidos
RED_TEAM_NAO_EXERCIDOS = 5 · NOT_EXERCISED, e não PASS
```

### O engano que eu próprio cometi, e fica registado

Na primeira corrida da porta apontei o armazém para a pasta do **acervo** em vez
da temporária, e ela escreveu uma observação lá dentro
(`XX/instagram-transcricoes-transcricoes/OBSERVATION/…json`). Foi detectado na
varredura seguinte e removido; os 16 ficheiros do acervo ficaram intactos e
nenhum tem data de hoje. Fica escrito porque um erro corrigido em silêncio é um
erro que volta.

---

# G · REGRESSÃO

```
BASE    611e7cbf   Ran 3733 · failures=103 · errors=51   -> 154 vermelhos
DEPOIS             Ran 3744 · failures=103 · errors=51   -> 154 vermelhos
                   (+11 = as provas novas · DISAPPEARED_TESTS = 0)

NEW_FAILURES = 0
```

Uma reprovação apareceu na lista comparada — `test_a_suite_nao_deixou_bruto_de
_teste_no_acervo`, a acusar `?? .tmpaudit/`. **Não é minha**, e foi provado:
isolada, ela passa nas DUAS árvores, e `.tmpaudit/` já não existe. É uma corrida
entre testes da mesma suíte — um vê a pasta temporária de outro enquanto ela
ainda está viva. Fica nomeada, e não caladas.

`SYSTEM_MAP_CHECK = PASS`.

---

# H · VEREDITOS

```
RUN_TYPE                      = REPROCESS
NEW_VIDEO_ACQUISITION         = NO      PAID_USD = 0,00    APIFY_RUNS = 0
SOURCE_ID                     = INSTAGRAM-TRANSCRICOES/TRANSCRICOES
ORIGINAL_RUN_ID               = UNKNOWN
ORIGINAL_RAW_OBSERVATION_ID   = UNKNOWN
VIDEO_SHA256                  = 0da99d1ddd4cdcc2410231b98599843d0318b2c76e11c26567bd14a92d95bd60

DEVICE_USED = GPU · EXECUTION = PROVEN · MODEL_USED = small
TRANSCRIPTION_SECONDS = 1,93 · REALTIME_FACTOR = 15,34x · LANGUAGE = it (0,989)

VIDEO_OUTPUT_WRITTEN          = YES  (o transcritor escreve, e sempre escreveu)
VIDEO_OUTPUT_CONSUMED         = NO
CONSUMER                      = NENHUM

STRUCTURED_CREATED            = NO   · bloqueado por C1
ADMISSION_DECISION            = NOT_EXECUTED
POSTGRES_DISPOSABLE_AVAILABLE = NO
READY_CREATED                 = NO   ·  WAITING_ROOM_DELTA = 0

REPROCESS_RAW_ID_PRESERVED    = NOT_APPLICABLE (não há RAW_ID sem banco)
DUPLICATION_ERRORS            = 0

VIDEO_INTERNAL_PIPELINE       = PARTIAL
FULL_VIDEO_TO_WAITING_ROOM    = BLOCKED_NO_DISPOSABLE_POSTGRES

DEFAULT_DEVICE = CPU (intocado)   ·   LIVE_TOUCHED = NO   ·   SALA_TOUCHED = NO
BIBLE_CHANGE = nenhuma
CONTRACT_CHANGE = `CONTENT_TYPE` passa a atravessar a porta (ficha, não conteúdo)
```

### O que destrava, por ordem de dependência

1. **PostgreSQL descartável alcançável desta máquina** — ou correr esta metade no
   CI, onde o `postgres:16` do `banco-descartavel.yml` já existe. Sem isto nada a
   jusante é exercitável, e escrever seria encanamento por correr.
2. **Um executor de derivação de áudio**, na forma de `executor_texto_de_pdf`,
   delegando no dono que já existe (`ferramentas/fala_local.py`), e **declarado à
   porta** — que para isso deixa de importar um nome e passa a ler uma lista.
3. Só então `VIDEO_OUTPUT_CONSUMED` pode ser medido como `YES` com prova.
