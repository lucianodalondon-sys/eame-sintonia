# C4E · A GPU RECONCILIADA COM A COLLECTION ATUAL — a entrega

> **O que esta missão fez:** pegou um conserto provado numa linha que não colhe
> e pô-lo na linha que colhe — só o conserto, medido ficheiro a ficheiro, em
> commits separáveis por categoria.
>
> **O que ela NÃO fez:** não coletou nada, não mudou o padrão do reconhecedor,
> não tocou na Sala, não tocou em LIVE, não empurrou know-how, não fez merge
> cego e não fez force push.

```
GPU_PATCH_ON_CURRENT_COLLECTION = PASS
DEFAULT_DEVICE                  = CPU   (inalterado, e por medição)
GPU_QUALITY_BENCHMARK           = BLOCKED_MISSING_MEDIA
```

---

# A · POR QUE ISTO PRECISOU DE EXISTIR

A prova da GPU nasceu em `claude/sintonia-local-runner-514cdc`, cuja base era a
linha da **Intelligence**. A Collection funcional vive noutra:

```
merge-base das duas                     f888776d
   linha da Intelligence  (a prova)     +31 commits
   linha da Collection    (a que colhe) +25 commits
```

São duas linhas irmãs, não uma à frente da outra. Rebasar 31 commits por cima de
25 seria merge cego — e a maior parte deles não tem nada a ver com transcrição.

```
A PROVA ESTAVA CERTA E NO SÍTIO ERRADO.
PORTAR É ESCOLHER O QUE ATRAVESSA, FICHEIRO A FICHEIRO, E DIZER PORQUÊ.
```

---

# B · O QUE ATRAVESSOU, E O QUE FICOU

Medido com `git ls-tree` na base + `git diff` contra o ponto de partida da prova:

| ficheiro | estado na base | decisão |
|---|---|---|
| `ferramentas/fala_local.py` | idêntico ao ponto de partida | **GPU_FUNCTIONAL_PATCH** |
| `provas/gpu_asr_smoke.py` | idêntico | **GPU_FUNCTIONAL_PATCH** |
| `provas/asr_banco.py` | idêntico | **GPU_FUNCTIONAL_PATCH** |
| `tests/test_c4b_gpu_execucao.py` | idêntico | **GPU_FUNCTIONAL_PATCH** |
| `tests/test_c4d_ferro_negociado.py` | não existia | **GPU_FUNCTIONAL_PATCH** (37 provas) |
| `.github/workflows/scrap-social.yml` | idêntico | **GPU_FUNCTIONAL_PATCH** (tira o pin) |
| `tests/test_c4_gpu_local.py` | idêntico | **UNRELATED_FIXES** · commit próprio |
| `tests/test_scrap_convergencia.py` | idêntico | **UNRELATED_FIXES** · commit próprio |
| `system-map/scripts/generate_system_map.py` | **diferente** (+1478 linhas) | **SYSTEM_MAP_FIXES** · re-aplicado, não portado |
| `system-map/scripts/impressao_da_arvore.py` | **diferente** (+384 linhas) | **SYSTEM_MAP_FIXES** · re-aplicado, não portado |
| `tests/test_atomicidade_da_intelligence.py` | **não existe nesta linha** | **EXCLUÍDO** |
| `SINTONIA-EAME-KNOW-HOW.md` | **não existe nesta linha** | **KNOW_HOW_DELTA** |
| `system-map/data/*` · `italia-portale/client/system-map/*` | gerado | **regenerado**, nunca portado |

> **Uma correcção a uma medição minha.** A primeira varredura usou
> `git cat-file -e "<ref>:<path>"` e declarou que `.github/workflows/scrap-social.yml`
> **não existia** na base. Existe — 24.675 bytes. A segunda varredura, com
> `git ls-tree -r --name-only`, deu a resposta certa, e é ela que está na tabela.
> Uma classificação inteira dependia disso.

### Os dois que foram RE-APLICADOS, e não copiados

`system-map/scripts/*` estão **mais avançados** nesta linha. Copiar o meu
ficheiro por cima apagaria 1.862 linhas de trabalho de outra missão. O que
atravessou foi o **conserto**, escrito de novo dentro da versão daqui — e o
defeito foi re-medido nesta árvore antes de o aplicar:

```
regerar o mapa aqui, sem o conserto:  79.817 linhas de diff
                     das quais conteúdo:      14
```

---

# C · SEPARADO EM TRÊS COMMITS, PARA PODEREM SER DESFEITOS SOZINHOS

```
73cf4b72  GPU_FUNCTIONAL_PATCH   o dono negoceia a aritmética
260b6e9b  UNRELATED_FIXES        a sentinela apitava todos os dias (barra do Windows)
cd701c97  SYSTEM_MAP_FIXES       a lei manda regerar, e regerar aqui estragava
```

O segundo está aqui por uma razão estreita e declarada: as três provas que
reprovavam são exactamente as que guardam o **dono único do reconhecedor** — e
são elas que verificam o primeiro commit.

```
COM ELAS VERMELHAS NÃO HÁ COMO DISTINGUIR «O PATCH RESPEITA O DONO ÚNICO»
DE «O PATCH CRIOU UM SEGUNDO DONO»: AS DUAS LEITURAS DÃO O MESMO VERMELHO.
```

Quem discordar deita fora `260b6e9b` sem tocar no resto.

---

# D · O PADRÃO NÃO MUDOU, E ISSO É A DECISÃO

```
DISPOSITIVO_PADRAO = CPU        COMPUTE_GPU = float16       COMPUTE_CPU = int8
```

Nenhuma coleta muda de comportamento em silêncio. Quem quiser a placa declara:

```
SINTONIA_ASR_DEVICE=AUTO    usa a placa SE ela existir de verdade
SINTONIA_ASR_DEVICE=GPU     pede a placa; a queda aparece no carimbo se não houver
SINTONIA_ASR_DEVICE=CPU     o processador, sempre
```

O motivo de não mudar é **medido**, e não «falta de tempo»: sobre áudio real, o
texto da placa difere do texto do processador em **4 das 6 peças com texto** —
incluindo `agricultora`→`agricultura` e `llegamos`→`llevamos`. Qual está certo é
`NOT_MEASURED`.

---

# E · A PROVA, NESTA ÁRVORE

Sem runner do GitHub e sem variável de ambiente declarada à mão:

```
--device GPU    PASS   ASR_DEVICE cuda/int8_float32   EXECUTION PROVEN   0,71 s
--device CPU    PASS   ASR_DEVICE cpu/int8/16 threads EXECUTION PROVEN   4,01 s
--device AUTO   PASS   escolheu a placa sozinho                          0,70 s

ASR_COMPUTE_REQUESTED  float16 -> ASR_COMPUTE_SELECTED  int8_float32
ASR_WHY_COMPUTE_FALLBACK        COMPUTE_TYPE_UNSUPPORTED
```

---

# F · A QUALIDADE CONTINUA BLOQUEADA, E AGORA SABE-SE PORQUÊ

```
GPU_QUALITY_BENCHMARK = BLOCKED_MISSING_MEDIA
```

E a palavra importa. O **gabarito está cá**:
`data/samples/REEL-TRANSCRICOES/QUALIDADE-DA-FALA-V1.json`, com 4 peças e termos
declarados um a um (`it`, `fr`, `en`, `es`). O que falta é o **áudio**:
`data/raw/REEL-MIDIA` não existe, e uma varredura do disco não encontrou nenhuma
pasta com esse nome nem nenhum dos quatro ficheiros de mídia — só os `.txt` do
texto já produzido.

```
BLOQUEADO POR FALTA DE MÍDIA != BLOQUEADO POR FALTA DE GABARITO.
Baixar mídia só para fechar um portão é adquirir conteúdo por uma rota que
nenhuma missão de hardware autorizou.
```

---

# G · O KNOW-HOW FICOU FORA DO CÓDIGO, E O CONFLITO É MAIOR DO QUE ELE

```
KNOW_HOW_CONFLICT       = YES
NEXT_KNOW_HOW_SECTION   = §121   (medido contra a população inteira, agora)
```

`SINTONIA-EAME-KNOW-HOW.md` **não existe nesta linha**. E medido em
2026-09-14 sobre todas as referências remotas:

```
documentos know-how DISTINTOS : 16, em 20 referências
número mais alto em uso        : §120
§118 tem QUATRO títulos diferentes ao mesmo tempo
```

O §119 canónico chama-se «UM NÚMERO QUE JÁ É DE ALGUÉM» e escreve, sobre
`SOURCE_ID`: *aloca-se contra a população inteira, nunca contra o dono
declarado*. A mesma lei aplica-se ao número da secção dele próprio, e não estava
a ser aplicada.

O aprendizado desta missão vai em
[`handoff/KNOW-HOW-DELTA-O-FERRO-NEGOCIADO.md`](../../handoff/KNOW-HOW-DELTA-O-FERRO-NEGOCIADO.md),
para quem detém o ficheiro canónico aplicar — **medindo o número outra vez**,
porque cinco sessões tocaram nele no mesmo dia.

---

# H · TESTES

```
NEW_FAILURES = 0
```

Com denominador, porque sem ele não vale nada:

```
BASE    56617781, intocada, nesta máquina
        Ran 3696 · failures=105 · errors=51 · skipped=186   -> 156 vermelhos
DEPOIS  Ran 3733 · failures=102 · errors=51 · skipped=186   -> 153 vermelhos
```

A suíte desta casa já reprova **156 testes nesta máquina sem ninguém mexer em
nada** — quase todos de Windows (barra invertida, `import fcntl`, cp1252). Com
esse ruído de fundo, uma falha nova passa despercebida: `NEW_FAILURES` mede-se
contra a base, num worktree descartável, e compara-se **por nome**.

Três reprovações de base ficaram consertadas, e são as sentinelas do dono único
do reconhecedor. `SYSTEM_MAP_CHECK = PASS`.

---

# I · VEREDITOS

```
CURRENT_COLLECTION_HEAD  = 56617781123f0f7ff34da02ba2ba0fe7997f0cb2
OLD_LOCAL_GPU_HEAD       = 162c4b8c44058435d2bd3b690d65246593158a13  (local, preservada)
NEW_GPU_BRANCH           = claude/local-gpu-on-current-collection-v1

DEFAULT_DEVICE           = CPU
GPU_EXPLICIT_MODE        = SINTONIA_ASR_DEVICE = AUTO | GPU | CPU
CPU_FALLBACK             = PASS
GPU_AVAILABLE            = YES     CUDA_FUNCTIONAL = YES
DEVICE_SELECTED          = GPU     DEVICE_USED = GPU   (quando pedido)

GPU_QUALITY_BENCHMARK    = BLOCKED_MISSING_MEDIA
KNOW_HOW_CONFLICT        = YES     NEXT_KNOW_HOW_SECTION = §121
NEW_FAILURES             = 0       SYSTEM_MAP_CHECK = PASS
REAL_COLLECTION_RUNS     = 0       PAID_USD = 0,00
LIVE_TOUCHED             = NO      SALA_TOUCHED = NO
```
