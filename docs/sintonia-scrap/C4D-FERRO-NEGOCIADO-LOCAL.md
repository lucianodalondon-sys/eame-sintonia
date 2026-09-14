# C4D · O FERRO NEGOCIADO, E A MÁQUINA LOCAL SEM O RUNNER — a entrega

> **O que esta missão provou:** esta máquina transcreve **na placa**, a partir de
> uma sessão local, **sem o runner do GitHub** e **sem nenhuma variável de
> ambiente declarada à mão**. E mediu, sobre áudio real já preservado, quanto a
> placa acelera — e que o texto dela **não é o mesmo** do processador.
>
> **O que ela NÃO conseguiu provar:** qual dos dois textos está certo. O corpus
> com verdade de referência declarada não está nesta máquina.
>
> **O que ela não fez:** não coletou nada, não gastou um dólar, não tocou LIVE,
> não mudou o padrão do reconhecedor, não criou uma segunda Collection.

```
C4D = PASS.

A CAPACIDADE FECHOU. A DECISAO CONTINUA POR TOMAR — E AGORA POR
MEDICAO, E NAO POR FALTA DE MEDICAO.
```

---

# A · GIT

| campo | valor |
|---|---|
| **BRANCH** | `claude/sintonia-local-runner-514cdc` |
| **BASE_HEAD medido no arranque** | `f437ff11` — **173 commits atrás** da linha canónica |
| **BASE adoptada** | `2b3d58d8` · `claude/control-plane-intelligence-night-v2` |
| **WORKTREE** | `.claude/worktrees/sintonia-local-runner-514cdc`, limpa no arranque |
| **O QUE FOI PRESERVADO** | `backup/local-runner-514cdc-pre-rebase` → `f437ff11` |

### Por que a base mudou, e por que nada se perdeu

O worktree abriu numa linha que **não tinha `BIBLIA-CANONICA-DA-COLETA.md`, nem
`SINTONIA-EAME-KNOW-HOW.md`, nem `ferramentas/fala_local.py`**. Medido:

```text
HEAD ... origin/release/canonical        9 a frente · 173 atras
```

O tronco funcional actual é `2b3d58d8` — o **merge-base das branches vivas mais
recentes**, ou seja o ponto mais avançado em que todas concordam. Construir sobre
ele é o que faz este trabalho entrar limpo em qualquer uma delas.

Os 9 commits locais somavam **um** ficheiro: `.github/workflows/scrap-social.yml`
com 274 linhas. O tronco tem esse mesmo ficheiro com **479**. Nada de único.

```
A BRANCH ANTIGA FICOU EM `backup/local-runner-514cdc-pre-rebase`.
Nenhum `reset` destrutivo: o ponteiro velho continua nomeado.
```

---

# B · O CENSO DA MÁQUINA — medido, nunca lido da ficha

`py provas/hardware_local.py`

| campo | valor medido |
|---|---|
| `OS` · `ARCH` · `PYTHON` | Windows 11 · AMD64 · 3.12.10 |
| `CPU_LOGICAL_CORES` · `RAM_TOTAL_GB` | 16 · 31,9 (14,3 disponíveis) |
| `GPU_VENDOR` · `GPU_MODEL` · `GPU_COUNT` | NVIDIA · GeForce GTX 1080 · 1 |
| `VRAM_TOTAL_MB` | 8192 (6423 livres no momento da medição) |
| `GPU_DRIVER` · `CUDA_DRIVER_SUPPORT` | 581.57 · 13.0 |
| `CUDA toolkit no disco` | v12.8 (`cublas64_12.dll`, `cublasLt64_12.dll`) |
| `FASTER_WHISPER` · `CTRANSLATE2` | 1.2.1 · 4.8.2 |
| `CTRANSLATE2_CUDA_DEVICE_COUNT` | **1** |
| `CTRANSLATE2_COMPUTE_TYPES_CUDA` | `float32` · `int8` · `int8_float32` |
| `FFMPEG` · `FFPROBE` | 9.0 · presente |
| `TORCH` | **ausente, e não é dependência** — o motor é CTranslate2 |

```
LOCAL_HARDWARE_STATUS = MEASURED
LOCAL_GPU_AVAILABLE   = YES
```

E o que a placa **não** oferece: `float16` não está na lista. É a Pascal a ser
Pascal — e é aqui que começa o defeito que esta missão veio consertar.

---

# C · O DEFEITO — a placa estava lá, e o artefato dizia que não havia placa

A C4B provou a GPU **pelo workflow**, com `SINTONIA_ASR_COMPUTE: int8_float32`
declarado no job. Esta missão correu a mesma coisa **na máquina, à mão**, sem
esse declarado. O que saiu:

```text
CTRANSLATE2_CUDA_DEVICE_COUNT = 1
resolver_dispositivo('GPU')   -> cuda/float16
WhisperModel(...)             -> ValueError: Requested float16 compute type, but
                                 the target device or backend do not support
                                 efficient float16 computation
o apanha-tudo da carga        -> cai para o processador
ASR_DEVICE_SELECTED           = CPU
ASR_WHY_FALLBACK              = GPU_UNAVAILABLE      <- FALSO
```

```
«NAO HA PLACA» E «ESTA PLACA NAO FAZ ESTA ARITMETICA» SAO DIAGNOSTICOS
DIFERENTES. O PRIMEIRO MANDA COMPRAR HARDWARE QUE JA ESTA NA MAQUINA.
```

### O que isto tornava frágil, e não é detalhe

O único caminho configurado para a placa vivia **dentro de um job do GitHub
Actions**, e o runner self-hosted desta casa tem histórico de não atender — 80
minutos de fila somada em duas máquinas, registados na C4. Ou seja: a capacidade
existia e dependia de a peça menos fiável estar de pé.

---

# D · A CORRECÇÃO — no dono, e sem mudar o padrão

`ferramentas/fala_local.py` continua a ser o **único** dono. O que ganhou:

```python
computes_suportados(device)   # PERGUNTA ao CTranslate2. Nao le tabela de placas.
negociar_compute(device, pedido=None)
```

E a regra que decide tudo:

```
UM PEDIDO EXPLICITO E UMA PROMESSA — honra-se ou reporta-se, nunca se troca
por baixo de quem o fez.
UM PADRAO DA CASA E UM PONTO DE PARTIDA — negocia-se contra o que a maquina
declara, e a troca fica escrita.
```

`SINTONIA_ASR_COMPUTE` continua soberano. Quem **não** declara nada recebe o
padrão da casa negociado contra a placa que há.

### O que NÃO mudou, e é decisão

```
COMPUTE_GPU        continua 'float16'
COMPUTE_CPU        continua 'int8'
DISPOSITIVO_PADRAO continua CPU
```

Uma placa não escreve regra para todo o hardware futuro. A C4B tinha razão em
recusar promover uma amostra de um, e essa recusa continua de pé.

### O sexto eixo do carimbo

`ENGINE != MODEL != RUNTIME != DEVICE != ACCELERATOR` — e agora **!= COMPUTE**:

| campo | o que diz |
|---|---|
| `ASR_COMPUTE_REQUESTED` | o que se pediu (ou o padrão da casa) |
| `ASR_COMPUTE_SELECTED` | o que de facto correu |
| `ASR_COMPUTE_SOURCE` | `EXPLICIT` (alguém pediu) ou `HOUSE_DEFAULT` (negociável) |
| `ASR_WHY_COMPUTE_FALLBACK` | `None` = não houve troca. Nunca `NOT_KNOWN` |

E `ASR_DEVICE` deixou de ler as constantes: passa a vir do trace. Sem isso o
carimbo diria `cuda/float16` sobre um texto nascido de `int8_float32` — o defeito
do literal a voltar por uma porta nova.

### Três consertos menores, no caminho

1. **Uma guarda que era código morto.** `trace['DEVICE_REQUESTED'] == GPU_SEM_MEMORIA`
   nunca podia ser verdade — `DEVICE_REQUESTED` só é `AUTO`, `CPU` ou `GPU`.
   Quem a lesse julgava haver uma trava de reentrada que não existia.
2. **O pedido original sobrevive à queda.** Ao cair para o processador,
   `COMPUTE_REQUESTED` continua a nomear o que se pediu à placa.
3. **O smoke deixou de reprovar o que ele próprio pediu.** `--device CPU` dava
   `RESULT = FAIL` a dizer «faltou dispositivo GPU», numa corrida onde nada
   falhou. O esperado passa a derivar do pedido.

---

# E · A PROVA, NESTA MÁQUINA, SEM O RUNNER

Nenhuma variável de ambiente foi declarada à mão em nenhuma destas corridas.

```text
py provas/gpu_asr_smoke.py --device GPU      RESULT = PASS
  ASR_DEVICE_REQUESTED  GPU     ASR_DEVICE_SELECTED   GPU
  ASR_DEVICE_EXECUTION  PROVEN  ASR_DEVICE_USED       GPU
  ASR_ACCELERATOR       CUDA    ASR_WHY_FALLBACK      None
  ASR_DEVICE            cuda/int8_float32
  ASR_COMPUTE_REQUESTED float16 -> SELECTED int8_float32
  ASR_WHY_COMPUTE_FALLBACK      COMPUTE_TYPE_UNSUPPORTED
  MACHINE_SECONDS       0,68

py provas/gpu_asr_smoke.py --device CPU      RESULT = PASS   (contraprova)
  ASR_DEVICE_USED  CPU   ASR_DEVICE  cpu/int8/16 threads   MACHINE_SECONDS 4,00

py provas/gpu_asr_smoke.py --device AUTO     RESULT = PASS
  escolheu GPU sozinho, e correu nela
```

```
GPU_QUALITY_BENCHMARK = NOT_RUN — e continua.
O audio do smoke e sintetizado nesta maquina e e uma frase so.
```

---

# F · O FERRO A FERRO, SOBRE ÁUDIO REAL JÁ PRESERVADO

`py provas/asr_banco.py --ferro-a-ferro --midia <pasta>`

**Nenhum byte novo foi adquirido.** O corpus são 8 `.wav` que já estavam nesta
máquina, capturados em 2026-09-02. O corpus canónico
(`data/raw/REEL-MIDIA`) **não está aqui** — e por isso a porta que aceita uma
pasta declarada existe, e por isso o que sai dela vem com `QUALITY = NOT_MEASURED`
colado.

```text
PECA             AUDIO_S  CPU_S   GPU_S  GANHO  IGUAL  SEMELHANCA  LINGUA
DcNkh7LCW4u       29,61   13,17    4,05   3,25    NO      0,9486    it/it
DcqdwWGFK58      109,72   20,85    2,37   8,80    NO      0,9754    es/es
Dcs6qdeiuVR       19,62    3,03    0,22  13,77   YES         n/a    en/en
Dctr2-Mj_Gr       58,07   13,20    1,63   8,10    NO      0,9250    es/es
Dcv05pfjC6O       95,62   18,15    2,13   8,52    NO      0,9952    es/es
DcvW56PihqX       46,89   10,13    1,26   8,04   YES      1,0000    es/es
DcxvzgQgo17       29,19    2,87    0,25  11,48   YES         n/a    en/en
DcyZsPNj_la       72,21   13,88    1,62   8,57   YES      1,0000    es/es
------------------------------------------------------------------------
TOTAL            460,90   95,28   13,53   7,04    2/6

RTF   cpu 4,84x tempo real   ·   gpu 34,07x tempo real
VRAM  pico 3045 MiB (delta 1234 MiB sobre a linha de base de 1811)
```

### Uma correcção a uma medição minha, antes de a publicar

A primeira leitura desta tabela dizia `TEXTO IGUAL = 4/8`. **Estava errada**, e o
erro era do tipo que esta casa persegue: duas das quatro «iguais» eram
`REQUESTED_EMPTY` dos **dois** lados.

```
DOIS VAZIOS NAO SAO UM ACORDO. COMPARAR PRECISA DE DUAS COISAS PARA COMPARAR.
```

O instrumento passou a separar `COMPARABLE` de `BOTH_EMPTY`, e a manchete conta
só as peças em que os dois lados escreveram alguma coisa: **2/6**.

### O que difere, palavra a palavra

Vírgulas e maiúsculas na maior parte — e **duas trocas de palavra**:

```text
«agricultora»  ->  «agricultura»        (uma pessoa vira um sector)
«llegamos»     ->  «llevamos»           (chegar vira levar)
```

```
QUAL DOS DOIS ESTA CERTO = NOT_MEASURED.
Estas pecas nao tem verdade de referencia declarada, e
CONCORDAR NAO E ACERTAR: dois ferros podem estar errados os dois.
```

---

# G · MEMÓRIA DA PLACA / OOM

```
GPU_OOM = NO — e medido, nao assumido.
```

O ataque usou o **maior modelo já presente nesta máquina** (nenhum
descarregamento: um banco que baixa 1,5 GB mede a rede, não a placa):

```text
modelo               large-v3-turbo
ASR_DEVICE           cuda/int8_float32
TRANSCRIPT_STATE     OK          ASR_WHY_FALLBACK  None
VRAM pico            3206 MiB    de 8192
REALTIME_FACTOR      19,35x      MODEL_PREPARE  6,71 s
```

A fronteira do OOM está longe: o modelo maior **cabe**, e com folga. O caminho de
queda por memória continua coberto por prova injectada
(`test_c4_gpu_local::test_o_reconhecedor_da_nome_a_memoria_cheia` e
`test_oom_durante_o_reconhecimento_sobe_com_nome`), porque forçar um OOM real
exigiria travar a máquina — que é exactamente o que §13 proíbe.

`MODEL_REQUESTED` e `MODEL_USED` **não podem divergir**: não existe degradação
silenciosa de modelo no dono. Se um dia existir, há prova que reprova até ela ser
registada (`T7OModeloNAOSETROCASOZINHO`).

---

# H · O QUE SAIU DO GIT

```yaml
# .github/workflows/scrap-social.yml, fase `gpu-asr`
-   SINTONIA_ASR_COMPUTE: int8_float32
```

```
UM VALOR QUE SO E VERDADE NUMA MAQUINA NAO PERTENCE AO GIT.
E UM PIN EXPLICITO NAO SE NEGOCEIA: na placa seguinte, que faca `float16`,
ele forcaria a pior das duas.
```

A prova que exigia a presença dessa linha foi **reescrita**, não apagada: passa a
exigir o contrário, e a exigir que a negociação exista — senão tirar o pin
deixaria a placa por usar, em silêncio.

**Nada desta máquina entrou no repositório.** A pasta de áudio é argumento de
linha de comando, nunca constante; os caminhos que saem em relatório passam por
`_sem_o_dono()`; e há prova que varre os cinco ficheiros tocados à procura do
nome do perfil, de caminho absoluto e da pasta desta máquina.

---

# I · UM CONSERTO FORA DO CAMINHO, E POR QUE ELE ERA OBRIGATÓRIO

A lei do projeto manda correr `generate_system_map.py` antes de fechar a tarefa.
Correr isso **nesta máquina** abria um diff de **80.629 linhas** em quatro
ficheiros que não tinham mudado uma vírgula.

Causa medida: `.gitattributes` declara `italia-portale/client/** -text` (o Git
guarda essa pasta byte a byte) e `core.autocrlf` está ligado. O `shutil.copyfile`
levava CRLF para lá dentro, e o `Path.write_text` traduzia `\n` em `\r\n`.

```
UM GERADOR QUE PRODUZ BYTES DIFERENTES EM CADA SISTEMA OPERATIVO NAO E
DETERMINISTICO — E A LEI MANDA CORRE-LO ANTES DE FECHAR.
```

Sem isto, quem obedecesse à lei no Windows tinha de escolher entre desobedecer e
empurrar 80 mil linhas de ruído. Agora o publicado sai com `\n` nos dois
sistemas, e binário passa intacto.

```
SYSTEM_MAP_CHECK = PASS · o mapa corresponde ao repositorio
```

---

# J · O QUE ESTA ABA LOCAL É

```
LOCAL_EXECUTION_CAPABILITY = READY
LOCAL_COLLECTION           = NAO EXISTE, E NAO NASCEU AQUI
```

Nenhuma Collection, nenhum SCRAP, nenhum RUN, nenhum RAW, nenhuma fila paralela,
nenhum know-how novo e nenhum fluxo de admissão nasceram nesta missão. A coleta
continua a pertencer ao Orquestrador e à Collection canónica.

O que existe é **uma etapa que esta máquina sabe executar quando o sistema
canónico pedir**, pelo contrato que já existe:

```text
entra   ficheiro de audio + idioma (se conhecido) + modelo + dispositivo
        fl.transcrever(wav, idioma=..., modelo_nome=..., dispositivo=...)

sai     TRANSCRIPT · TRANSCRIPT_STATE · SEGMENTS (com tempos)
        LANGUAGE · LANGUAGE_SOURCE · LANGUAGE_CONFIDENCE
        ASR_DEVICE_REQUESTED · SELECTED · EXECUTION · USED
        ASR_COMPUTE_REQUESTED · SELECTED · SOURCE
        ASR_MODEL · ASR_ENGINE · ASR_ENGINE_VERSION · ASR_RUNTIME
        TRANSCRIBER_ID · TRANSCRIBER_VERSION
        MACHINE_SECONDS · MODEL_PREPARE_SECONDS · REALTIME_FACTOR
        COST_USD = 0
```

`RUN_ID` e `RAW_OBSERVATION_ID` **não** entram aqui, e isso é o desenho: quem os
carrega é o chamador (`youtube_transcrever.py`, `instagram_transcrever.py`,
`reel_transcricao.py`), que já os tem e já os cola ao artefato. Uma fila própria
nesta gaveta seria a segunda Collection que esta missão existe para não criar.

---

# K · RED TEAM

| # | ataque | resultado |
|---|---|---|
| 1 | CUDA existe e é usada | **PASS** — smoke `--device GPU`, `EXECUTION = PROVEN` |
| 2 | CUDA disponível e o transcritor continua CPU | **APANHADO** — era o defeito real; agora `COMPUTE_TYPE_UNSUPPORTED` |
| 3 | CPU fallback funciona | **PASS** — smoke `--device CPU`, `USED = CPU` |
| 4 | GPU ausente não mata a Collection | **PASS** — `AUTO` cai com nome, estado não vira `ASR_FALHOU` |
| 5 | GPU OOM não fabrica sucesso | **PASS** — `GPU_OOM` tem nome próprio; prova injectada |
| 6 | `DEVICE_SELECTED != DEVICE_USED` é detectado | **PASS** — `USED` só nomeia ferro com `EXECUTION = PROVEN` |
| 7 | modelo pedido != modelo usado é registado | **PASS** — não existe troca silenciosa, e há prova que reprova se nascer |
| 8 | caption não vira transcript | **PASS** — rotas separadas; a fila marca `JA_TEM_LEGENDA` |
| 9 | tradução não substitui original | **PASS** — nenhuma chamada passa `task=`; `'translate'` não existe no dono |
| 10 | caminho local não vira identidade | **PASS** — pasta é argumento; `_sem_o_dono()` nos relatórios |
| 11 | segredo não entra no Git | **PASS** — nenhum token, nenhuma chave; guarda da casa corre antes |
| 12 | hostname/perfil pessoal não entra no Git | **PASS** — prova varre os 5 ficheiros tocados |
| 13 | configuração de CUDA não fica hard-coded | **PASS** — pin saiu do workflow; pastas conferidas no disco |
| 14 | fixture não vira RAW real | **PASS** — nada escrito em `data/`; leitura apenas |
| 15 | execução local não cria segunda Collection | **PASS** — nenhum ficheiro de runner/fila/collection nasceu |
| 16 | dois vazios contados como texto igual | **APANHADO NA MINHA PRÓPRIA MEDIÇÃO** — 4/8 corrigido para 2/6 |
| 17 | prova que reprova o que ela própria pediu | **APANHADO** — smoke `--device CPU` dava FAIL |
| 18 | a sentinela do dono único apitava todos os dias | **APANHADO** — barra do Windows; 2 falhas em cada corrida |

```
RED_TEAM_SURVIVORS = 0
```

---

# L · O QUE NÃO MUDOU

```
orquestrador          schema da Collection      migrations       Supabase LIVE
Admission             Intelligence              Sala             portal · deploy
Apify                 rota de midia             politica de acesso ao YouTube
motor de traducao     Bíblia                    contrato de design
DISPOSITIVO_PADRAO    COMPUTE_GPU               COMPUTE_CPU      MODELOS_POR_CHAMADOR
```

Nenhum driver, CUDA, BIOS, Windows ou PATH global foi tocado. O `PATH` que o dono
altera é o **do processo**, e morre com ele.

```
REAL_COLLECTION_RUNS = 0
PAID_USD             = 0,00
APIFY_RUNS           = 0
```

---

# M · O QUE FICA POR SABER

| pergunta | estado | porquê |
|---|---|---|
| o texto da placa é melhor ou pior que o do processador? | `NOT_MEASURED` | o corpus com verdade declarada não está nesta máquina |
| `float16` noutra placa? | `NOT_MEASURED` | depende da placa, e agora pergunta-se a ela |
| quanto a placa acelera com `medium`? | `NOT_MEASURED` | `medium` não está em cache aqui |
| qual o limite de VRAM desta placa? | `NOT_REACHED` | `large-v3-turbo` coube em 3,2 GB de 8 |
| a Collection já encaminha trabalho para cá? | `NO` | o contrato está pronto; ligar é missão própria |

### O que destrava a decisão do padrão

Uma coisa só, e está nomeada:

```bash
py provas/asr_banco.py --ferro-a-ferro --midia data/raw/REEL-MIDIA
```

Essas peças **têm** verdade de referência declarada em
`data/samples/REEL-TRANSCRICOES/QUALIDADE-DA-FALA-V1.json`. Com elas, «o texto da
placa está certo?» deixa de ser `NOT_MEASURED`.

---

# N · VEREDITOS

```
LOCAL_GIT_BASE_PROVEN            = YES
GPU_MEASURED                     = YES
CUDA_FUNCTIONAL                  = YES
DEVICE_SELECTION_SINGLE_OWNER    = YES  (ferramentas/fala_local.py)
COMPUTE_SELECTION_SINGLE_OWNER   = YES  (o mesmo — e e novo)
CPU_FALLBACK                     = PASS
GPU_TRANSCRIPTION_TEST           = PASS
DEVICE_USED_RECORDED             = YES
COMPUTE_USED_RECORDED            = YES
MODEL_USED_RECORDED              = YES
LINEAGE_PRESERVED                = YES
SECRETS_IN_GIT                   = 0
MACHINE_SPECIFIC_PATHS_IN_GIT    = 0
REAL_COLLECTION_RUNS             = 0
PAID_USD                         = 0
RED_TEAM_SURVIVORS               = 0

LOCAL_EXECUTION_CAPABILITY       = READY
LOCAL_GPU_ASR_PRODUCTION_READY   = NO   (sem benchmark de qualidade)
GPU_QUALITY_BENCHMARK            = NOT_RUN
```

`READY` e `PRODUCTION_READY = NO` não se contradizem. A máquina leva uma
inferência até ao fim na placa, sete vezes mais depressa, e isso repete-se. O que
não está medido é se o texto que ela produz presta no corpus real.
