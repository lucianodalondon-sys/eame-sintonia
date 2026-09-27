# C10.6 — MORRER A MEIO, E SABER O QUE SOBROU

    C10_6_CRASH_RETRY_PERSISTENCE = PARTIAL

Uma execução pode falhar. A pergunta não é se falha — é o que ela deixa para
trás, e o que a seguinte faz com isso.

    CRASH → PROCESSO NOVO → RECUPERA?

Não «a exceção foi apanhada?», que é uma pergunta sobre a RAM de um processo
ainda vivo. Aqui o processo morre de verdade — `os._exit()`, que não desenrola
pilha, não corre `finally` e não corre `atexit` — e quem responde é **outro
processo**, que só vê o disco.

---

## 1. A PRÉ-CONDIÇÃO, QUE ERA UM DEFEITO

A C10.5D mediu que `guardar=False` impedia a entrega mas **não** o intermédio: o
WAV caía sempre em `data/raw/REEL-MIDIA/`. Uma suíte de crash sujaria o bruto da
casa a cada corrida.

A gaveta e a oficina passaram a ser dois sítios. **Ler** o que já está
preservado é sempre da gaveta — reuso é leitura, e nenhuma corrida deve deixar
de encontrar o que já se pagou. **Escrever** bytes novos vai para a oficina, que
por omissão *é* a gaveta e que uma corrida descartável troca pela sua.

    UMA CORRIDA QUE NÃO GUARDA NÃO PODE SUJAR A GAVETA DE QUEM GUARDA.

```
TEST_DEBRIS_IN_REAL_RAW = 0   (21 ficheiros antes, 21 depois)
```

---

## 2. A MATRIZ DE MORTE — CINCO PONTOS, CINCO PROCESSOS MORTOS

Todos com código de saída 97, que é `os._exit`. Um `raise` apanhado devolveria
0 ou 1 e provaria outra coisa.

| ponto | onde morreu | RAW fichado | WAV | ASR entrou | entrega |
|---|---|---|---|---|---|
| **F0** | antes de qualquer preservação | não | não | não | vazia |
| **F1** | logo depois do RAW ganhar ficha | **sim** | não | não | vazia |
| **F2** | com o WAV escrito, antes do ASR | sim | **sim** | não | vazia |
| **F3** | dentro do ASR | sim | sim | **sim** | vazia |
| **F4** | transcript pronto, antes de fechar o RUN | sim | sim | sim | **`.txt` sem lote** |
| OK | não morreu | sim | sim | sim | `.txt` + lote |

### F4 é o achado da tabela

O texto derivado chega à gaveta de entrega **antes** de o RUN fechar. Quem
lesse a gaveta veria uma transcrição sem registo de corrida por trás dela.

    DERIVED EXISTS ≠ RUN COMPLETED.

### E F3 é a que mais importava

Morte **dentro** do ASR não publicou texto nenhum — nem `.txt`, nem lote.

    TRANSCRIPT PARCIAL NUNCA VIROU TRANSCRIPT FINAL.

---

## 3. O QUE UM PROCESSO NOVO VÊ

```
WHAT_SURVIVES?          os bytes da mídia e o WAV da oficina.
                        No F4, também o .txt na entrega.
WHAT_IS_REPEATED?       tudo o resto: extração do WAV e ASR, sempre.
WHAT_GETS_NEW_ID?       nada. O SHA é do conteúdo. O ARTIFACT_ID sai do SHA.
WHAT_IS_OVERWRITTEN?    o .txt por POST_ID. O lote é FUNDIDO por chave, nunca
                        substituído.
WHAT_STATE_IS_RECORDED? NENHUM, entre processos. Sem attempts, sem last_error,
                        sem replayable, sem checkpoint.  NOT_IMPLEMENTED.
```

A retoma funciona: o processo novo produz `TRANSCRIPT_STATE = OK` com **zero
rede**, reaproveitando os bytes. O que ele não recupera é **estado** — ele não
sabe que houve uma tentativa antes.

---

## 4. O CONFLITO ESTRUTURAL

```
CONFLICT = não existe estado de corrida durável para esta cadeia

WHY      = retomar com juízo exige saber quantas tentativas houve, qual foi o
           último erro e se aquilo é replayable. Nada disso sobrevive ao
           processo. Um crash não só interrompe o trabalho: apaga o facto de
           que ele foi tentado.

EVIDENCE = `coleta/coleta_checkpoint.py` EXISTE e é o dono declarado — o próprio
           `scrap_executor.STATE()` o nomeia como `CHECKPOINT_BACKEND`. Mas:
             · ele fala com Postgres por `psql`, e usá-lo aqui exigiria banco
               vivo, que esta missão está proibida de usar como laboratório;
             · a cadeia de Reel e o adaptador do Instagram importam-no ZERO
               vezes;
             · o próprio executor declara `CURSORS: NOT_IMPLEMENTED`.
           Medido depois da morte em F1: a entrega fica VAZIA. O processo novo
           não vê attempts, nem last_error, nem replayable.

RECOMMENDED_NEXT_STEP =
           decidir, com gente, se o estado de corrida do SCRAP vive no
           checkpoint que já existe (e então o backend de Postgres passa a ser
           requisito desta cadeia) ou se ganha um suporte local. São duas
           arquiteturas diferentes, e escolher uma por conveniência de uma
           missão de robustez seria escolher pelo lado errado.
```

Por isso esta missão **não inventou esquema**. `COL-LAW-027` continua por
cumprir nesta cadeia, e fica dito.

---

## 5. O LAÇO QUE NÃO PERGUNTAVA A NINGUÉM

Medido antes de mudar, com transporte falso:

| erro simulado | tentativas | o dono chama-lhe | retentável? |
|---|---|---|---|
| `403` | **4** | `BLOCKED` | **não** |
| `404` | **4** | `SOURCE_GONE` | **não** |
| formato ausente | **4** | `ITEM_ERROR` | **não** |
| `429` | 4 | `RATE_LIMITED` | sim |
| `500` | 4 | `SOURCE_UNAVAILABLE` | sim |
| timeout | 4 | `TRANSIENT_NETWORK_ERROR` | sim |
| política `NAO` | 0 | `ROUTE_NOT_ALLOWED` | não |

Quatro tentativas para tudo. A casa **já tinha** a resposta certa escrita em
`leis/falhas.py`, e a cadeia não a importava.

    QUATRO TENTATIVAS SOBRE UM NÃO DEFINITIVO NÃO SÃO PERSISTÊNCIA.
    SÃO MARTELADAS, E `COL-LAW-026` EXISTE PARA AS IMPEDIR.

### Depois

| erro | tentativas | parou porque |
|---|---|---|
| `403` · `404` · formato ausente · desconhecido | **1** | `NAO_RETENTAVEL` |
| `429` · `500` · timeout | 4 | `TENTATIVAS_ESGOTADAS` |
| política `NAO` | **0** | o portão, antes do laço |

O vocabulário **não nasceu aqui**. Nasceu em `leis/falhas.py`, que continua o
dono único da taxonomia e da pergunta «repetir adianta?». O que nasceu na cadeia
foi a **tradução** do que o `yt-dlp` escreve — e isso pertence a quem o chama.

E o que não se entende não se repete: erro desconhecido cai em `UNKNOWN_ERROR`,
que o dono classifica como não retentável. Repetir o que não se entendeu é
martelar no escuro.

### O relógio

```
com Retry-After: 7    esperas observadas = [7, 7, 7]
sem Retry-After       esperas observadas = [2, 8, 30]   (limitado, declarado)
```

Ausência de `Retry-After` fica `NÃO SEI`, nunca `0`: «ela não pediu tempo» e
«ela pediu zero» são coisas diferentes. E o relógio vive num sítio só, para que
o teste o troque — nenhuma prova espera minutos reais.

### O erro final não some

```
YTDLP_SEM_MIDIA[SOURCE_GONE] apos 1/4 tentativa(s): ERROR: HTTP Error 404…
```

O estado canónico vem à frente, depois a contagem, depois a frase da
plataforma. E o degrau leva `ATTEMPTS`, `ATTEMPT_LIMIT`, `LAST_ERROR`,
`LAST_ERROR_STATE`, `RETRY_AFTER`, `RETRY_EXHAUSTED`, `RETRYABLE` e
`STOPPED_BECAUSE` até ao artefato.

---

## 6. A CORRIDA QUE APAGAVA UMA OBSERVAÇÃO

Dois processos a fechar o mesmo lote, seis execuções:

```
SAFE · SAFE · RACE_PROVEN · SAFE · RACE_PROVEN · SAFE
```

Em duas delas o `RUN_IDS_SEEN` ficou só com um dos dois. O ficheiro **não
corrompia** — o último a escrever apagava a fusão do outro, e a observação
perdida não deixava rasto nenhum.

    UMA OBSERVAÇÃO QUE ACONTECEU E DESAPARECEU É PIOR QUE UM ERRO:
    UM ERRO DEIXA TESTEMUNHA.

O conserto é o mínimo que fecha a corrida: um cadeado consultivo em volta do
ciclo ler-alterar-escrever, e a troca final por `os.replace`, que é atómica. Sem
fila, sem agendador, sem banco. Depois: **8 em 8 SAFE**.

---

## 7. IDEMPOTÊNCIA

Duas passagens sobre a mesma fixture:

```
itens no lote      1  e  1        (nenhum registo duplicado)
SHA256             55f0120995c053a3  nas duas
ARTIFACT_ID        RAW-55f0120995c053a3  nas duas
RUN_IDS_SEEN       ['C106-1', 'C106-2']  ·  TIMES_OBSERVED = 2
mesma RUN repetida TIMES_OBSERVED = 1    (uma retoma não é uma observação nova)
```

`RUN ≠ OBSERVATION ≠ CONTENT`, e o lote sabe a diferença.

---

## 8. RED TEAM — CATORZE TENTATIVAS, TREZE QUEDAS

| # | tentativa | medida |
|---|---|---|
| 1 | a retoma volta a descarregar o RAW | 0 yt-dlp, 0 rede |
| 2 | transcript parcial publicado como final | morte 97, entrega vazia |
| 3 | `403` permanente é martelado | 1 tentativa, `BLOCKED` |
| 4 | política `NAO` é retentada | 0 tentativas, 0 esperas, 0 rede |
| 5 | `429` ignora o `Retry-After` | pedido 7, esperas `[7,7,7]` |
| 6 | o retry cria identidade nova | SHA e `ARTIFACT_ID` iguais |
| 7 | o mesmo RAW gera duas cópias duráveis | 1 item, dois `RUN_ID` |
| 8 | **o estado da corrida vive só na RAM** | **NÃO CAIU** — ver §4 |
| 9 | o processo novo não consegue retomar | retoma deu `OK` sem rede |
| 10 | a prova suja o bruto real | 21 ficheiros antes e depois |
| 11 | o erro final desaparece como `None` | estado + contagem + frase |
| 12 | duas corridas simultâneas corrompem o destino | cadeado e `os.replace` |
| 13 | o teste passa sem atravessar o dono real | `403` 1 tentativa · timeout 4 |
| 14 | a sentinela encontra o próprio texto | não anda a pé pelo repositório |

O nº 13 é o que dá valor aos outros: o mesmo laço, com dois erros diferentes,
para em sítios diferentes — e para porque `leis/falhas.py` o mandou parar.

---

## 9. SCRAP × COLLECTION CANÓNICA

```
COL_LAW_505_CODE_AUTHORITY         = ABSENT_IN_THIS_TECHNICAL_LINE
                                     (`leis/retorno_da_coleta.py` continua a não
                                      existir; re-verificado depois do fetch)
COLHEITA_SEPARADA_DE_SUPORTE       = NOT_EXERCISED_IN_THIS_MISSION
RUN_ID_OWNER                       = quem chama. A cadeia não cunha RUN_ID.
RAW_OWNER                          = `_ficha_raw`, e o ARTIFACT_ID sai do SHA
                                     do conteúdo — nunca do caminho nem da hora
SOURCE_ID_PRESERVATION             = NAO SEI, nunca fabricado
FABRICATED_DOCUMENT_ID             = NO
PARALLEL_RAW_RUN_IDENTITY_MODEL    = NO
THEMATIC_CLASSIFICATION_IN_SCRAPER = NO

MODULE_EXISTS = YES   a cadeia, o dono do erro e o dono do checkpoint existem
EDGE_EXISTS   = YES   a cadeia passou a ler `leis/falhas.py`
                NO    a cadeia continua sem aresta para `coleta_checkpoint.py`
FLOW_EXISTS   = PARCIAL  crash, retoma, retry e idempotência correm e estão
                provados. Persistência de ESTADO de corrida não existe.
```

---

## 10. VEREDITO

```
CRASH_RECOVERY_PROVEN  = YES — o trabalho retoma, com zero rede
RETRY_POLICY_PROVEN    = YES — permanente para em 1, transiente vai ao teto
REPLAY_PROVEN          = YES — bytes preservados, zero aquisição
IDEMPOTENCY_PROVEN     = YES — nenhum registo duplicado, identidade estável
CONCURRENCY_PROVEN     = RACE_PROVEN e depois fechada (2/6 → 0/8)
RUN_STATE_PERSISTENCE  = NOT_IMPLEMENTED  (não é NO: ninguém o construiu)

C10_6_CRASH_RETRY_PERSISTENCE = PARTIAL
```

`PARTIAL` e não `PASS` por uma razão só, e ela está na §4: **não há estado de
corrida durável**. Tudo o resto que a missão pediu está medido e provado. Isso
não se conserta com uma linha, e escolher a arquitetura por conveniência de uma
missão de robustez seria escolher pelo lado errado.

    NOT_MEASURED NÃO SE ARREDONDA PARA NO. E NOT_IMPLEMENTED TAMBÉM NÃO.

---

## 11. O QUE NÃO MUDOU

Nenhuma aquisição do Instagram. Zero pedidos à plataforma, zero Apify, zero
dólares. A política da C10.5D continua `NOT_ALLOWED`, intocada. A C12 e a C11
ficam como estavam. Nenhuma das dívidas listadas foi corrigida — continuam
todas abertas, incluindo `AUDIO_ONLY_LABEL_ON_SUPPLIED_MEDIA` e o conflito de
vocabulário do `LOCAL_EXECUTOR`.
