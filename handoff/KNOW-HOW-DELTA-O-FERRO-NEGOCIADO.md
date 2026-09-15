# DELTA PARA O KNOW-HOW CANÓNICO — ESCOLHER O FERRO NÃO É SÓ ESCOLHER ONDE

```
ORIGEM            C-LOCAL-GPU-ON-CURRENT-COLLECTION-V1
BRANCH            claude/local-gpu-on-current-collection-v1
BASE FUNCIONAL    claude/collection-to-waiting-room-v1 @ 56617781
ORIGEM DA PROVA   claude/sintonia-local-runner-514cdc @ 162c4b8c   (local, não empurrada)
NÚMERO DESTA      **§121** — o primeiro livre medido contra a POPULAÇÃO INTEIRA
KNOW_HOW_CONFLICT **YES**, e é maior do que este delta. Ver a secção 0.
```

> **⚠️ ESTE FICHEIRO NÃO É UM SEGUNDO KNOW-HOW.**
> O know-how canónico é `SINTONIA-EAME-KNOW-HOW.md`, e ele **não existe nesta
> linha**. Trazê-lo para cá criaria a coisa que este projeto passa a vida a
> consertar: dois donos do mesmo conceito. Isto é um DELTA, na forma que
> `handoff/KNOW-HOW-DELTA-A-BASE-DA-AUDITORIA.md` já fixou.

---

# 0 · PRIMEIRO, A MEDIÇÃO QUE MUDA COMO ESTE DELTA SE APLICA

A missão anterior desta linha escreveu «ÚLTIMA SECÇÃO §118, medida agora». Hoje
essa resposta já não serve, e não por ter envelhecido: **a pergunta estava mal
colocada**. Medido em 2026-09-14, com `git rev-parse <ref>:SINTONIA-EAME-KNOW-HOW.md`
sobre todas as referências remotas mais esta árvore:

```
documentos know-how DISTINTOS : 16, espalhados por 20 referências
número mais alto em uso        : §120
```

E os números não são de uma pessoa só:

| secção | quantos títulos DIFERENTES existem |
|---|---|
| §112 · §113 · §114 · §115 · §116 · §117 | **2 cada** |
| **§118** | **4** |
| §119 | **2** |
| §120 | 1 |

O §118 tem quatro significados ao mesmo tempo:

```
A FERRAMENTA PARTIDA MENTE COMO SE FOSSE UM ACHADO     (sintonia-eame-know-how-v1)
CONHECER UMA FONTE E AUTORIZAR UMA FONTE SÃO A MESMA…  (italy-source-isolation)
UM MUNDO FECHADO TORNA INVISÍVEL APAGAR UMA PROIBIÇÃO  (intelligence-object-model)
ESCOLHER O FERRO NÃO É SÓ ESCOLHER ONDE                (esta prova, local)
```

O §119 canónico chama-se, literalmente, **«UM NÚMERO QUE JÁ É DE ALGUÉM»**, e a
lei que ele escreve é sobre `SOURCE_ID`:

```
ALOCA-SE CONTRA A POPULAÇÃO INTEIRA, NUNCA CONTRA O DONO DECLARADO.
```

A mesma lei aplica-se ao número da secção dele próprio, e não estava a ser
aplicada — o documento que a escreve forkou em dezasseis.

```
UM REGISTO QUE NÃO SABE RESPONDER «ESTE NÚMERO JÁ É DE ALGUÉM?»
NÃO É REGISTO: É UMA LISTA COM BOA REPUTAÇÃO.
E UMA LEI EM DEZASSEIS SÍTIOS NÃO É UMA LEI.
```

**§121 é o primeiro livre à hora desta medição.** Quem integrar tem de medir
outra vez: cinco sessões tocaram este ficheiro no mesmo dia, e o número pode já
ser de alguém quando isto for lido.

---

# 1 · O QUE MUDOU

O dono único do reconhecedor (`ferramentas/fala_local.py`) passou a **negociar o
tipo de cálculo** contra o que a biblioteca declara para a placa que existir, em
vez de o afirmar por constante. E a queda ganhou o nome que lhe faltava:

```
GPU_UNAVAILABLE           não há placa, ou a biblioteca não a vê
COMPUTE_TYPE_UNSUPPORTED  há placa, conta-se, e ela não faz ESTA aritmética
GPU_OOM                   há placa, faz a aritmética, e o modelo não coube
```

Três campos novos no carimbo, pela mesma razão que o dispositivo já tinha três:
`ASR_COMPUTE_REQUESTED` · `ASR_COMPUTE_SELECTED` · `ASR_COMPUTE_SOURCE`, mais
`ASR_WHY_COMPUTE_FALLBACK`.

E saiu do Git um valor que só era verdade numa máquina:
`SINTONIA_ASR_COMPUTE: int8_float32`, dentro de `.github/workflows/scrap-social.yml`.

---

# 2 · POR QUÊ — A CAUSA, MEDIDA

A prova durável anterior da GPU correu **pelo workflow**, com aquele override
declarado no job. Correr a mesma coisa **na máquina, à mão**, sem ele:

```
CTRANSLATE2_CUDA_DEVICE_COUNT = 1
resolver_dispositivo('GPU')   -> cuda/float16
WhisperModel(...)             -> ValueError: Requested float16 compute type, but
                                 the target device or backend do not support
                                 efficient float16 computation
o apanha-tudo da carga        -> cai para o processador
o carimbo                     -> ASR_WHY_FALLBACK = GPU_UNAVAILABLE
```

O artefato afirmava que **não havia placa**, com a placa ali, ligada e contada.

```
«NÃO HÁ PLACA» E «ESTA PLACA NÃO FAZ ESTA ARITMÉTICA» SÃO DIAGNÓSTICOS
DIFERENTES. O PRIMEIRO MANDA COMPRAR HARDWARE QUE JÁ ESTÁ NA MÁQUINA;
O SEGUNDO MANDA TROCAR UMA PALAVRA.
```

A correcção **não** foi mudar o padrão. Foi aplicar ao tipo de cálculo o
princípio que já governava o dispositivo:

```
`AUTO` pergunta à biblioteca QUANTAS placas há.
O tipo de cálculo PADRÃO pergunta à biblioteca QUAIS ela suporta.

UM PEDIDO EXPLÍCITO É UMA PROMESSA — honra-se ou reporta-se.
UM PADRÃO DA CASA É UM PONTO DE PARTIDA — negoceia-se, e a troca fica escrita.
```

---

# 3 · PROVA

Corrida local, **sem o runner do GitHub** e **sem variável de ambiente nenhuma
declarada à mão**, nesta árvore:

```
provas/gpu_asr_smoke.py --device GPU    RESULT = PASS   0,71 s
  ASR_DEVICE_SELECTED  GPU      ASR_DEVICE_EXECUTION  PROVEN
  ASR_DEVICE_USED      GPU      ASR_ACCELERATOR       CUDA
  ASR_DEVICE           cuda/int8_float32
  ASR_COMPUTE_REQUESTED float16 -> SELECTED int8_float32
  ASR_WHY_COMPUTE_FALLBACK      COMPUTE_TYPE_UNSUPPORTED

provas/gpu_asr_smoke.py --device CPU    RESULT = PASS   4,01 s  (contraprova)
provas/gpu_asr_smoke.py --device AUTO   RESULT = PASS   0,70 s  (escolheu a placa)
```

Ferro a ferro sobre **460,9 s de áudio real já preservado** (8 peças, ES e IT,
nenhum byte novo adquirido), medido na árvore de origem da prova:

```
CPU  95,28 s   RTF  4,84x
GPU  13,53 s   RTF 34,07x        GANHO 7,04x
```

---

# 4 · CONSEQUÊNCIA — A CAPACIDADE FECHA, A DECISÃO NÃO

`DISPOSITIVO_PADRAO` continua `CPU`, e agora por um motivo **medido**, e não por
falta de medição:

```
O TEXTO DA PLACA NÃO É O TEXTO DO PROCESSADOR.
Em 4 das 6 peças com texto houve diferença — vírgulas, maiúsculas, e duas
trocas de palavra: «agricultora» -> «agricultura», «llegamos» -> «llevamos».

QUAL DOS DOIS ESTÁ CERTO = NOT_MEASURED.
Aquelas peças não têm verdade de referência declarada, e
CONCORDAR NÃO É ACERTAR — dois ferros podem estar errados os dois.
```

```
VELOCIDADE NÃO PROVA QUALIDADE.
```

O que destrava a decisão está nomeado e é uma corrida só:
`provas/asr_banco.py --ferro-a-ferro --midia data/raw/REEL-MIDIA`. O **gabarito**
existe nesta árvore (`QUALIDADE-DA-FALA-V1.json`, 4 peças com termos declarados
em `it`, `fr`, `en`, `es`). A **mídia** não existe em lado nenhum desta máquina —
conferido por varredura. Baixá-la só para fechar o portão seria adquirir
conteúdo por uma rota que nenhuma missão de hardware autorizou.

```
GPU_QUALITY_BENCHMARK = BLOCKED_MISSING_MEDIA
(e não «missing ground truth»: o gabarito está cá, falta o áudio)
```

---

# 5 · AS LEIS QUE ESTE DELTA PROPÕE

```
DEVICE_AVAILABLE != DEVICE_SELECTED != DEVICE_USED
    a placa existir não prova que ela correu. O resolvedor corre ANTES de
    existir uma amostra transcrita: quem decide antes não pode testemunhar
    depois.

COMPUTE TYPE INCOMPATÍVEL != GPU AUSENTE
    e confundi-los é o único erro deste par que manda comprar hardware.

UM PEDIDO EXPLÍCITO É UMA PROMESSA. UM PADRÃO DA CASA É UM PONTO DE PARTIDA.
    o primeiro honra-se ou reporta-se; o segundo negoceia-se contra o que a
    máquina declara — e a troca fica escrita, nunca em silêncio.

CPU E GPU PODEM PRODUZIR TRANSCRIPT DIFERENTE.
VELOCIDADE NÃO PROVA QUALIDADE.
    7x mais depressa e 2/6 de texto idêntico são a mesma medição. Promover a
    primeira metade a decisão é medir depois de decidir.

DOIS VAZIOS NÃO SÃO UM ACORDO.
    de 8 peças, 4 saíam «texto idêntico» — e duas eram REQUESTED_EMPTY dos dois
    lados. Comparar precisa de duas coisas para comparar.

LOCAL EXECUTOR != LOCAL COLLECTION.
    esta máquina executa UMA ETAPA quando o sistema canónico pedir. Nenhuma
    fila, nenhum RUN, nenhum RAW e nenhuma Collection nasceram aqui.

UM VALOR QUE SÓ É VERDADE NUMA MÁQUINA NÃO PERTENCE AO GIT.
    e um pin explícito não se negoceia: na placa seguinte, que faça `float16`,
    ele forçaria a pior das duas.
```

E duas que não são sobre ASR, e saíram do mesmo dia (secção 6):

```
UM GERADOR QUE PRODUZ BYTES DIFERENTES EM CADA SISTEMA OPERATIVO
NÃO É DETERMINÍSTICO — E A LEI MANDA CORRÊ-LO ANTES DE FECHAR.

PERGUNTAR «QUE SHA TERIA ISTO» NÃO É O MESMO QUE PERGUNTAR
«QUE SHA TENS TU GUARDADO PARA ISTO».
```

---

# 6 · O QUE ESTE DELTA **NÃO** REGISTA

```
NÃO regista coleta.      REAL_COLLECTION_RUNS = 0.  PAID_USD = 0.
NÃO regista vídeo → Sala. VIDEO_OUTPUT_HAS_CONSUMER continua NO nesta árvore.
NÃO regista qualidade.   GPU_QUALITY_BENCHMARK = BLOCKED_MISSING_MEDIA.
NÃO regista mudança de padrão. DISPOSITIVO_PADRAO = CPU, e por medição.
NÃO regista LIVE.        Nenhuma migration, nenhuma escrita em produção.
Esta missão portou uma capacidade. Não ligou nada.
```
