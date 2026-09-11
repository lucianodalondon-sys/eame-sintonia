# C4 · RUNNER LOCAL + GPU ASR — a entrega

> **O que esta missão provou:** o dono do reconhecedor passou a ter **política
> de ferro** — `AUTO · CPU · GPU`, com detecção real e queda declarada — sem
> criar um segundo motor e sem que nenhum adaptador escolha hardware. E o banco
> de prova mediu, sobre corpus já preservado, que a qualidade que esta casa
> precisa **já cabe no processador**.
>
> **O que ela NÃO conseguiu provar:** a máquina local. Os **dois** runners
> self-hosted não atenderam em nenhuma das três tentativas. Sem máquina não há
> censo de hardware, e sem censo não há GPU provada.
>
> **O que ela não fez:** não aposentou Actor de transcrição, não criou rota de
> mídia, não mudou política de acesso ao YouTube, não encanou Collection, não
> mudou o padrão do reconhecedor.

```
C4 = PARTIAL.

A FUNDAÇÃO DE SOFTWARE FICOU PRONTA E PROVADA.
A FUNDAÇÃO DE HARDWARE NÃO PÔDE SER MEDIDA — E ISSO É UM BLOQUEIO
REGISTADO, NÃO UM RESULTADO.
```

---

# A · GIT

| campo | valor |
|---|---|
| **BRANCH** | `claude/sintonia-scrap-local-gpu-c4` |
| **SOURCE_BRANCH** | `claude/sintonia-scrap-youtube-cutover-c3` |
| **SOURCE_HEAD** (referência do coordenador) | `4c6505d34d03469c76d9d39aaae033dc115e312c` |
| **ACTUAL_INITIAL_HEAD** (medido) | `4c6505d34d03469c76d9d39aaae033dc115e312c` |
| **FINAL_HEAD** | o commit que traz este documento |
| **PUSH_STATE** | `PUSHED` · nenhum `force`, em nenhum empurrão |
| **WORKTREE** | `/home/user/eame-sintonia`, única e limpa |
| **DRIFT** | **NENHUM** — a referência do coordenador bateu com a medição |

**REGRA ZERO cumprida.** O `fetch --all --prune` trouxe uma branch nova de outra
frente (`claude/executor-return-contract-v1`). **Não foi lida nem fundida.**

---

# B · LOCAL RUNNER

```
LOCAL_HARDWARE_STATUS = NOT_MEASURED
MOTIVO                = RUNNER_OFFLINE
```

**Todos os campos que a missão pedia ficam por medir**, e nenhum vai ser
preenchido por especificação de fabricante:

| campo | valor |
|---|---|
| `RUNNER_NAME` · `OS` · `CPU` · `RAM` | `NOT_MEASURED` |
| `GPU_VENDOR` · `GPU_MODEL` · `VRAM` · `GPU_DRIVER` | `NOT_MEASURED` |
| `CUDA_DRIVER_SUPPORT` · `CTRANSLATE2_CUDA_DEVICE_COUNT` | `NOT_MEASURED` |
| `FASTER_WHISPER_VERSION` · `FFMPEG_VERSION` (na máquina local) | `NOT_MEASURED` |

### O que foi medido, e é o que sustenta o bloqueio

| tentativa | runner | despacho | resultado |
|---|---|---|---|
| 1 | `eame-sintonia-local-2` | 09:38Z | `queued` 23 min · cancelada à mão |
| 2 | `eame-sintonia-local` | 09:38Z | `queued` 23 min · cancelada à mão |
| 3 | `eame-sintonia-local-2` | 09:50Z | `queued` 55 min · cancelada à mão |

**Cerca de 80 minutos de fila somada, em duas máquinas, com zero atendimentos.**

### O runner existe, e já atendeu — o que torna isto «offline», não «inexistente»

| corrida | quando | o que diz |
|---|---|---|
| `33335319689` | 2026-08-30 | **success** em `SINTONIA-EAME-LOCAL-2` |
| `34309850267` | 2026-09-09 | **failure** em `SINTONIA-EAME-LOCAL-2`, `runner_id 22` |
| `33745012145` · `33745457833` · `33932433543` | 2026-09-03/05 | **cancelled** às 24 h — nunca atendidas |

A corrida de 09-09 é a prova de que a máquina é real: ela pegou o job, fez
`checkout`, e falhou num passo com `bash: command not found`.

```
RUNNER QUE NÃO ATENDE ≠ RUNNER QUE NÃO EXISTE ≠ MÁQUINA SEM PLACA.

Três coisas diferentes. Publicar «não há GPU» a partir da primeira seria
inventar uma medição sobre hardware que nunca foi perguntado.
```

### O instrumento ficou pronto, e é o que a próxima tentativa herda

`provas/hardware_local.py` mede tudo o que a secção 6 pediu e corre em segundos.
A fase `hardware` do workflow canônico leva-o à máquina. **A medição está a um
despacho de distância no dia em que o runner acordar.**

---

# C · ASR BEFORE

Censo feito no `ACTUAL_INITIAL_HEAD`, antes de tocar numa linha.

| campo | valor medido |
|---|---|
| `ASR_OWNERS_BEFORE` | **1** — `ferramentas/fala_local.py` |
| `ENGINE` | `faster-whisper` |
| `RUNTIME` | CTranslate2 (implícito, **sem campo próprio**) |
| `DEVICE` | `cpu` — **literal cravado**, `fala_local.py:222` |
| `COMPUTE_TYPE` | `int8` — **literal cravado**, mesma linha |
| `ACCELERATOR` | nenhum, e **sem campo** |
| `DEVICE_DECISIONS_BEFORE` | **1 sítio**, dois literais |

### `MODEL_DECISIONS_BEFORE` — quatro sítios para uma pergunta

```
fala_local            SINTONIA_ASR_MODELO   →  small
reel_transcricao      SINTONIA_REEL_MODELO  →  medium
instagram_transcrever IG_MODELO             →  small
youtube_transcrever   YT_MODELO             →  small
```

Nenhum deles estava **errado**. E esse era o problema:

```
UMA POLÍTICA ESCRITA EM QUATRO SÍTIOS É QUATRO POLÍTICAS A FINGIR QUE SÃO UMA.
Elas concordam por coincidência, e no dia em que o dono aprender alguma coisa,
os outros três continuam a não saber.
```

---

# D · CPU BASELINE

**⚠️ Esta medida é do CONTENTOR, não da máquina local.** Intel Xeon, 4 núcleos
lógicos, 15,7 GiB, sem placa, Ubuntu. A máquina local continua `NOT_MEASURED`, e
estes números **não** se transferem para ela.

Corpus: `data/raw/REEL-MIDIA`, já preservado. **Nenhum byte novo foi baixado.**
Verdade de referência: `QUALIDADE-DA-FALA-V1.json`, que declara cada termo com a
origem dele.

### `small` — o padrão actual dos dois programas de lote

| REEL | língua | áudio (s) | RTF | termos | marca | língua |
|---|---|---|---|---|---|---|
| `C-FanW_CYMz` | IT | 34,11 | 11,64 | **0/2** | **0/1** | STABLE |
| `C2b0GJrIJ8t` | FR | 78,37 | 8,01 | 2/2 | n/a | STABLE |
| `DW6X5lZkU41` | EN | 145,43 | 14,51 | 2/2 | n/a | STABLE |
| `Db5QG2Dk3sF` | ES | 112,62 | 15,14 | **2/3** | n/a | STABLE |

### `medium` — o padrão actual da cadeia de Reel

| REEL | língua | áudio (s) | RTF | termos | marca | língua |
|---|---|---|---|---|---|---|
| `C-FanW_CYMz` | IT | 34,11 | 4,69 | **2/2** | **0/1** | STABLE |
| `C2b0GJrIJ8t` | FR | 78,37 | 2,98 | 2/2 | n/a | STABLE |
| `DW6X5lZkU41` | EN | 145,43 | 4,80 | 2/2 | n/a | STABLE |
| `Db5QG2Dk3sF` | ES | 112,62 | 6,22 | **3/3** | n/a | STABLE |

### Cobertura de língua

```
IT  MEASURED     ES  MEASURED     FR  MEASURED     EN  MEASURED
PT  NOT_MEASURED
```

Não há amostra portuguesa com verdade declarada no corpus preservado. **Nenhum
áudio foi inventado e nenhuma verdade de referência foi fabricada** para encher
a linha.

### O que estes números dizem, e é contra-intuitivo

`medium` custa ~2,5x o tempo de `small` e ganha **exactamente onde esta casa
precisa**: o nome da cultura e o nome da marca. E mesmo assim corre entre **3x e
6x mais depressa do que o tempo real, sem placa nenhuma**.

```
A QUALIDADE QUE ESTA CASA PRECISA JÁ CABE NO PROCESSADOR.
A PLACA, SE VIER, É QUESTÃO DE VAZÃO — NÃO DE QUALIDADE.
```

---

# E · GPU MATRIX

```
NÃO EXECUTADA.
```

Nenhuma linha. `faster-whisper + GPU` com `small`, `medium` e `large-v3-turbo`,
em `float16` e `int8_float16`, continua por medir — porque **a máquina não
atendeu**, e não porque a combinação falhou.

```
UMA TABELA VAZIA É HONESTA. UMA TABELA PREENCHIDA COM O QUE A PLACA
«DEVERIA» FAZER SERIA A PIOR COISA QUE ESTA MISSÃO PODIA PRODUZIR.
```

O banco (`provas/asr_banco.py`) aceita `--device GPU` e mede `VRAM_USED_MB`,
`GPU_UTILIZATION_PCT`, `PEAK_RAM_MB`, RTF, termos, marca e estabilidade de
língua. Ele está pronto; falta-lhe a máquina.

---

# F · ITALIAN SENTINEL

O Reel `C-FanW_CYMz` da `@syngentaitalia` continua a ser a peça que separa os
modelos, e continua **`PARTIAL`**:

| termo | origem | `small` | `medium` |
|---|---|---|---|
| `mais` (a cultura) | legenda do post | **NÃO** | SIM |
| `discovery seeds` | legenda do post | **NÃO** | SIM |
| `syngenta` | identidade da conta | **NÃO** | **NÃO** |

`medium` escreve **«singenta»**. O comparador rejeita — e está certo em
rejeitar: um nome de marca escrito de outra maneira não é o nome da marca.

```
IT = PARTIAL, E CONTINUA PARTIAL. Nenhuma configuração nova foi promovida
a padrão global, e nenhuma piorou o italiano.
```

### A armadilha que o comparador evita

`small` escreveu «mai scoltori» onde se disse «maiscoltori». Um `in` cru diria
que acertou, porque a string contém as letras.

```
UMA COMPARAÇÃO FROUXA TRANSFORMA UM ERRO MEDIDO NUM ACERTO PUBLICADO.
```

A fronteira de palavra é o que separa as duas.

---

# G · MODEL DECISION

```
SELECTED_MODEL = NENHUMA MUDANÇA
```

**Nada foi trocado, e a razão não é cautela — é a ordem da secção 25.** A
decisão de modelo depende da matriz GPU, que não existe. Trocar agora seria
decidir antes de medir.

| valor | onde | mudou? |
|---|---|---|
| `medium` | cadeia de Reel | não |
| `small` | `instagram_transcrever` | não |
| `small` | `youtube_transcrever` | não |
| `small` | padrão do dono | não |

**O que mudou foi o DONO da decisão, não a decisão.** A tabela saiu dos quatro
ficheiros e passou a viver em `fala_local.MODELOS_POR_CHAMADOR`. Os chamadores
dizem **quem são**; o dono responde **qual modelo**. As variáveis de ambiente
antigas — `SINTONIA_REEL_MODELO`, `IG_MODELO`, `YT_MODELO` — continuam todas a
valer, cada uma para o seu chamador.

```
CENTRALIZAR A POLÍTICA NÃO AUTORIZA MUDAR OS VALORES DELA
POR BAIXO DE QUEM OS PEDIU.
```

**`REJECTED_ALTERNATIVES`:** `large-v3-turbo` não foi rejeitado — **não foi
testado**, porque depende de VRAM que ninguém mediu.

---

# H · DEVICE POLICY

O dono ganhou três valores, e o do meio é o perigoso:

```
CPU    corre no processador. Sempre possível.
GPU    corre na placa. PEDIDO, nunca promessa.
AUTO   pergunta à biblioteca e usa a placa SE ela existir de verdade.
```

### `AUTO` não finge

Ele não lê ficha de fabricante nem variável de ambiente: pergunta ao
`CTranslate2` **quantos dispositivos CUDA ele vê**, que é a única resposta que
conta. Uma prova reprova se a detecção passar a sair de `os.environ`.

```
UM «AUTO» QUE ASSUME GPU NÃO É DETECÇÃO: É UM PALPITE COM CARA DE POLÍTICA.
```

### O trace, e ele existe mesmo quando não há queda

| pedido | usado | `WHY_FALLBACK` | medido |
|---|---|---|---|
| `CPU` | `CPU` | `None` | ✅ |
| `AUTO` | `CPU` | `GPU_UNAVAILABLE` | ✅ neste contentor |
| `GPU` | `CPU` | `GPU_UNAVAILABLE` | ✅ neste contentor |
| `GPU` | `CPU` | `GPU_OOM` | ✅ por injecção |

`None` quer dizer **«não houve queda»**, e nunca «não sei». Colapsar os dois
faria uma queda silenciosa parecer ausência de queda.

```
QUEDA SILENCIOSA É MENTIRA COM OUTRO NOME. Sem o trace, «pedi placa e correu
no processador» fica indistinguível de «pedi processador» — e o texto sai
igual nos dois casos, só que muitas vezes mais devagar sem ninguém perceber.
```

### E o padrão **não** mudou

```
DISPOSITIVO_PADRAO = CPU
```

Esta missão trouxe a **capacidade** de usar a placa. Ela não trouxe a
**decisão** de a usar — isso depende de prova na máquina real. Uma sentinela
reprova se o padrão mudar sem ela.

---

# I · ASR OWNER AFTER

```
ASR_OWNERS_AFTER = 1  ·  ferramentas/fala_local.py
```

Provado por varredura da árvore inteira: `WhisperModel(` e
`BatchedInferencePipeline(` aparecem **num único ficheiro executável**. Nenhum
`gpu_asr.py`, `youtube_gpu.py` ou `instagram_gpu.py` nasceu — e há uma prova que
reprova pelo nome do ficheiro se algum aparecer.

E os chamadores **não escolhem ferro**: nenhum passa `device=` ou
`compute_type=`, nenhum nomeia `cuda`, `float16` ou `nvidia`. Eles passaram a
**reportar** o que o dono decidiu, lendo o trace que ele devolve.

### O carimbo deixou de mentir

`ASR_DEVICE` dizia, sempre, `cpu/int8/N threads` — escrito à mão, ao lado de uma
chamada que também tinha `cpu` escrito à mão.

```
AS DUAS CONCORDAVAM POR COINCIDÊNCIA DE TECLADO, NÃO POR CONSTRUÇÃO.
No dia em que uma mudasse, a outra continuaria a jurar o contrário, e o
artefato levaria a assinatura da errada.
```

Agora o campo vem do trace, e os cinco eixos têm cinco campos:
`ASR_ENGINE` · `ASR_MODEL` · `ASR_RUNTIME` · `ASR_DEVICE_USED` ·
`ASR_ACCELERATOR`. Sem trace, o carimbo **confessa** `NOT_KNOWN` em vez de
adivinhar.

---

# J · WORKFLOW

Uma fase nova no workflow canônico, `hardware`, **em job próprio**. Nenhum
workflow paralelo nasceu.

O job próprio não é estética. Três medições:

1. o job `scrap` declara `shell: bash`, e em 2026-09-09 o runner local 2
   respondeu **`bash: command not found`** ao job inteiro;
2. o passo do guarda chama `python3`, que nessa máquina é o atalho da Microsoft
   Store e falha — ali o interpretador chama-se `py`;
3. o `setup-python` instalaria um Python que **não é o da máquina**.

```
MEDIR A MÁQUINA COM AS FERRAMENTAS DE OUTRA MÁQUINA NÃO É MEDIR.
```

Ele publica runner, motor, modelo, dispositivo, tipo de cálculo e acelerador.
**Não recolhe** utilizador, pasta pessoal, série de disco, MAC nem IP.

### Uma correcção a mim próprio, dentro desta missão

Escrevi `timeout-minutes: 15` a pensar que protegia contra runner offline. **Não
protege.** O relógio do GitHub só começa quando um runner **aceita** o job; um
job à espera de máquina que não atende fica `queued` até às 24 horas.

```
UM TECTO QUE SÓ CONTA DEPOIS DE COMEÇAR NÃO PROTEGE DE NUNCA COMEÇAR.
```

O comentário do workflow foi corrigido para dizer isso.

---

# K · YOUTUBE MEDIA CENSUS

**Estado, e só estado.** Nenhuma rota foi promovida.

| rota | técnica | política da plataforma | autorização de produção | ambiente |
|---|---|---|---|---|
| `youtube.media` (bytes) | `403` de IP de datacenter | `robots.txt` barra `/get_video` | **não declarada na matriz** | `LOCAL` (`DATACENTER_BLOCKED`) |
| `yt-dlp:extract_info` | funciona para metadados | `robots.txt` barra `/youtubei` | `BLOCKED` | — |
| `youtube:oembed` | `PROVED` | permitido | `CONDICIONAL` | `ONLINE` |
| `youtube.native_caption` | **`PROVED`** | permitido | `SIM` | `ONLINE` |
| `apify:transcricao` | `POSSIBLE_NOT_PROVED` | — | `CONDICIONAL` (paga) | `ONLINE` |

**Não existe capacidade de mídia declarada para o YouTube.** Só o TikTok tem
`FETCH_VIDEO_BYTES` na matriz. O que existe é `youtube.media` em
`scrap_capacidades`, com estado `BLOCKED`.

```
FUNCIONOU TECNICAMENTE ≠ PRODUÇÃO AUTORIZADA.
A matriz diz ROUTE_NOT_ALLOWED, e continua a dizer.
```

### E a distinção que esta missão existe para não deixar borrar

```
CAN TRANSCRIBE  !=  CAN ACQUIRE MEDIA.

GPU ASR resolve  ÁUDIO → TRANSCRIÇÃO.
Ela NÃO resolve  YOUTUBE → ÁUDIO.
```

Há uma prova que reprova se o dono do ASR aprender a adquirir mídia.

---

# L · RED TEAM

| # | ataque | resultado |
|---|---|---|
| RT1 | não existe placa | `GPU_UNAVAILABLE` no trace, texto sai na mesma |
| RT2 | CUDA indisponível | `0` com motivo escrito, nunca excepção |
| RT3 | CTranslate2 não vê CUDA | a detecção **não** pode ler `os.environ` — prova reprova |
| RT4 | tipo de cálculo incompatível | `int8` no processador, `float16` na placa, campos distintos |
| RT5 | modelo não cabe | `GPU_OOM`, com recuperação para o processador |
| RT6 | placa cai a meio da carga | por injecção: cai com nome, e recupera |
| RT6b | queda por DLL em falta | `GPU_UNAVAILABLE`, **não** `GPU_OOM` |
| RT7 | ficheiro de áudio inválido | `ASR_FALHOU`, nunca `REQUESTED_EMPTY` |
| RT8 | transcrição vazia | `REQUESTED_EMPTY` tem estado próprio |
| RT9 | idioma errado | `LANGUAGE_SOURCE` separa declarado de detectado |
| RT10 | adaptador crava modelo/ferro | reprova, por árvore sintática |
| RT11 | segundo `WhisperModel` | reprova, varrendo o repositório |
| RT12 | teste escreve em `data/samples` | reprova |

**RT4, RT6 e RT7 não acontecem num contentor sem placa.** Foram exercidos por
injecção, de propósito:

```
UMA FALHA QUE SÓ SE TESTA QUANDO ACONTECE NÃO ESTÁ TESTADA.
Ela só aparece no dia mau, e no dia mau ninguém está a olhar.
```

E **RT6b existe porque classificar de mais também mente**: nem toda queda da
placa é memória cheia. Uma DLL em falta que saísse como `GPU_OOM` mandaria
alguém trocar de modelo quando o que falta é um ficheiro.

---

# M · RAW TEST SAFETY

```
FAKE_RAW_COMMITTED = NO
TEST_RAW_TARGET    = TEMPORARY
POST_TEST_DEBRIS   = 0
```

O banco de prova **imprime** e não grava — provado por árvore sintática, não por
leitura. O censo da máquina **lê** e não escreve. Os testes que precisam de
ficheiro usam `TemporaryDirectory`.

### Uma correcção a uma prova minha

A primeira versão da prova «o censo não grava nada» procurava a string `open(` e
reprovava o `open('/proc/meminfo')` — que é uma **leitura**, e é exactamente o
que o censo tem de fazer.

```
PROIBIR `open` PROIBIU A MEDIÇÃO, NÃO A ESCRITA.
```

Agora a pergunta é feita na árvore: há alguma chamada que **escreva**?

---

# N · TESTS

```
BASE_TOTAL      1941
BASE_FAILURES     20
BASE_ERRORS        1
BASE_SKIPS       175

FINAL_TOTAL     1991
FINAL_FAILURES    20
FINAL_ERRORS       1
FINAL_SKIPS      175

NEW_FAILURES       0
```

**+50 provas.** As 21 vermelhas finais são **as mesmas 21** da base, conjunto
contra conjunto — dívida anterior a esta missão, nenhuma consertada aqui e
nenhuma escondida.

---

# O · SYSTEM MAP

A cadeia canônica, **relida e não herdada de memória** — a C3 aprendeu a perder
um ciclo aqui:

```bash
py system-map/scripts/scan_repo.py
py system-map/scripts/scan_sources.py
py system-map/scripts/generate_system_map.py
py system-map/scripts/censo_das_estradas_it.py
py system-map/scripts/validate_system_map.py
```

O gerador **não re-escaneia** no caminho normal: lê o inventário que
`scan_repo.py` deixou. Um ficheiro novo desde o último scan entra com o SHA
antigo, o gerador diz `MAPA=OK`, `git status` fica limpo — e o validador reprova
por drift.

**Resultado: `PASS`, com árvore limpa.**

---

# P · UNKNOWNs

| pergunta | estado | porquê |
|---|---|---|
| que hardware tem a máquina local? | `NOT_MEASURED` | o runner não atendeu em 80 min |
| há placa nessa máquina? | `NOT_MEASURED` | idem — e **não** é `NO` |
| `float16` ou `int8_float16` nessa placa? | `NOT_MEASURED` | depende da placa |
| `large-v3-turbo` cabe na VRAM? | `NOT_MEASURED` | depende da VRAM |
| quanto a placa acelera? | `NOT_MEASURED` | sem matriz GPU |
| há amostra em PT? | `NOT_MEASURED` | não existe no corpus preservado |
| a legenda nativa substitui o ASR? | `PROVED` como rota, **não ligada** | fora do escopo da C4 |
| porque é que o runner caiu? | `UNKNOWN` | não se liga à máquina para perguntar |

### E o que **não** é desconhecido

O `bash: command not found` de 2026-09-09 sugere que a máquina mudou entre
2026-08-30 (quando um job igual passou) e 09-09. **Isto é uma pista, não uma
medição**, e fica registada como tal.

---

# Q · O QUE NÃO MUDOU

Território proibido, e nenhuma linha entrou nele:

```
orquestrador/orquestrador.py     schema da Collection      migrations
Admission                        Intelligence              portal · deploy · main
retirada de Actor de YouTube     cutover de transcrição    rota de mídia de produção
Instagram · LinkedIn · Facebook · X · Stories              motor de tradução
```

E mais, que não estava proibido e mesmo assim não mudou:

- **nenhum driver, CUDA, BIOS, Windows ou PATH global foi tocado.** A missão
  proibia, e não houve sequer ocasião — a máquina não atendeu;
- **o padrão do reconhecedor** continua `CPU` e `small`;
- **os três valores de modelo** continuam onde estavam;
- **os dois Actors de legenda** continuam ligados, e há prova que reprova se
  saírem.

---

# R · VEREDITOS

```
LOCAL_HARDWARE_STATUS             = NOT_MEASURED  (bloqueio: RUNNER_OFFLINE)
LOCAL_GPU_AVAILABLE               = NOT_MEASURED
LOCAL_GPU_ASR_TECHNICALLY_PROVEN  = NO
LOCAL_GPU_ASR_PRODUCTION_READY    = NO

CPU_FALLBACK_PROVEN               = YES

YOUTUBE_MEDIA_ZERO_APIFY          = NO
YOUTUBE_TRANSCRIPT_ZERO_APIFY     = NO
YOUTUBE_ZERO_APIFY_TOTAL          = PARTIAL
```

**`NOT_MEASURED` e `NO` não são a mesma palavra, e a diferença aqui é toda.**
`LOCAL_GPU_AVAILABLE = NO` significaria «perguntei à máquina e ela não tem
placa». A verdade é «a máquina não atendeu», e escrever `NO` mandaria alguém
comprar hardware que pode já estar lá.

**Os três últimos não se mexeram, e não se mexeriam mesmo que a GPU tivesse
funcionado.** GPU resolve áudio→texto; ela não resolve YouTube→áudio, e não
muda política de acesso nenhuma.

### Critérios de PASS

| | critério | |
|---|---|---|
| P1 | hardware local realmente medido | ❌ `RUNNER_OFFLINE` |
| P2 | disponibilidade de GPU realmente medida | ❌ idem |
| P3 | GPU ASR no self-hosted, ou impossibilidade provada | ❌ idem |
| P4 | CPU baseline existe | ✅ (no contentor) |
| P5 | comparação GPU × CPU | ❌ sem GPU |
| P6 | qualidade medida, não só velocidade | ✅ |
| P7 | italiano incluído | ✅ |
| P8 | um único dono de ASR | ✅ |
| P9 | adaptadores não controlam ferro nem modelo | ✅ |
| P10 | fallback explícito | ✅ |
| P11 | nenhuma mídia nova adquirida | ✅ |
| P12 | Actors de transcrição intactos | ✅ |
| P13 | RAW de teste não contaminou o acervo | ✅ |
| P14 | `NEW_FAILURES = 0` | ✅ |
| P15 | System Map `PASS` contra scan actual | ✅ |
| P16 | branch empurrada sem `force` | ✅ |
| P17 | árvore limpa | ✅ |

```
C4 = PARTIAL. Três critérios dependem de uma máquina que não atendeu, e
NENHUM DELES FOI FINGIDO.
```

---

# S · KNOW_HOW_DELTA

```
KNOW_HOW_DELTA = NENHUM

KNOW_HOW_BRANCH       = claude/sintonia-eame-know-how-v1
KNOW_HOW_INITIAL_HEAD = 5836cc23   (medido, nao herdado)
KNOW_HOW_FINAL_HEAD   = 21652176
KNOW_HOW_PUSHED       = YES, sem force
```

A secção **12** do handoff canônico foi escrita nesta missão, em worktree
separada, no ficheiro que já existia. Cinco coisas duráveis nasceram aqui, e
nenhuma depende da GPU ter funcionado:

1. **o relógio do áudio não conta o tempo de preparar a máquina** — um download
   de modelo saía como `TRANSCRIPTION_TIMEOUT`, que é uma afirmação sobre o
   áudio;
2. **`ENGINE != MODEL != RUNTIME != DEVICE != ACCELERATOR`**, agora com cinco
   campos em vez de um literal;
3. **política em quatro sítios é quatro políticas** — a tabela de modelo passou
   para o dono, sem mudar um valor;
4. **`timeout-minutes` não limita a fila** do GitHub Actions, e um runner que
   não atende é uma medição, não uma espera;
5. **a qualidade já cabe no processador** — o que muda a ordem das missões
   seguintes: a GPU deixa de ser pré-requisito de qualidade e passa a ser
   optimização de custo de tempo.

---

# T · READY_FOR_YOUTUBE_TRANSCRIPT_CUTOVER

```
NO
```

E a razão **não** é a GPU. São duas, e a segunda é a que manda:

1. `LOCAL_GPU_ASR_TECHNICALLY_PROVEN = NO` — a fundação local não fechou;
2. **mesmo que tivesse fechado, não bastaria.** O cutover de transcrição precisa
   de `YOUTUBE → ÁUDIO`, e essa rota está `BLOCKED` com `403` de datacenter e
   sem capacidade declarada na matriz.

```
UMA CASA QUE SABE TRANSCREVER E NÃO SABE OBTER O ÁUDIO
NÃO ESTÁ PRONTA PARA DESLIGAR QUEM LHE TRAZ O TEXTO.
```

O caminho que a medição desta missão de facto abre é outro, e mais barato:
`youtube.native_caption` já está **`PROVED`**. No YouTube a legenda existe, e
transcrever com ASR o que a plataforma já escreveu é pagar hora de máquina por
texto que estava à mão. **Isso é missão própria, e não é esta.**
