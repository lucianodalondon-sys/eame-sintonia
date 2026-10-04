# C10.4B — UMA CAPACIDADE, UM CAMINHO VIVO

    C10_4B_DUPLICATE_PATH = DUPLICATE_REACHABLE

Há duas implementações de «obter fala de Reel do Instagram» neste repositório. A
pergunta desta missão não foi «existem?» — isso a C10.4 já tinha registado. Foi:

> **São as duas OPERACIONALMENTE alcançáveis?**

A resposta é sim, e a segunda porta não aparece em `import` nenhum.

---

## 1. AS DUAS

| | **NOVA** | **VELHA** |
|---|---|---|
| ficheiro | `ferramentas/reel_transcricao.py` | `ferramentas/instagram_transcrever.py` |
| linhas | 1 538 | 394 |
| método | pede `-f bestaudio`; confere os bytes | baixa o MP4 **inteiro** e faz `ffmpeg -vn` |
| corpus que lê | `COMPETITOR-PUBLIC-COMM/POSTS-*.json` | `INSTAGRAM-JANELA` |
| corpus que escreve | `REEL-TRANSCRICOES` | `INSTAGRAM-TRANSCRICOES` |
| chamadores de produção | `adaptador_instagram.py`, `comunicacao_coleta.py` | **nenhum** |
| registada em `scrap_registo` | sim, com `rota=` | não |

A velha é exatamente o que a lei da C8 proíbe:

    TRANSCRIPTION NEED ≠ VIDEO DOWNLOAD.

---

## 2. A PROVA DE ALCANÇABILIDADE

Armadilha nas funções públicas da velha, e seis pedidos pelas entradas
canónicas reais:

| entrada | velha alcançada |
|---|---|
| executor canónico · `instagram.reel.transcribe` | não |
| executor canónico · `instagram.reel.capture` | não |
| executor canónico · `instagram.reel.audio` | não |
| adaptador directo · `capturar_reel` | não |
| a cadeia directa · `transcrever_reel` | não |
| a fase de fala da Collection | não |
| **chamada deliberada** (o contraponto) | **sim** — a armadilha disparou |

    UMA ARMADILHA QUE NUNCA DISPARA SÓ PROVA ALGUMA COISA SE A MESMA ARMADILHA
    DISPARAR QUANDO ALGUÉM A CHAMA DE PROPÓSITO.

Pelo pedido canónico, portanto: `OLD_PATH_RUNTIME_REACHABLE = NO`.

---

## 3. E ENTÃO O CENSO OLHOU PARA FORA DO PYTHON

```
.github/workflows/sintonia-scrap.yml
    fase=transcrever        →  ferramentas/instagram_transcrever.py rodar
    fase=transcrever-alvos  →  ferramentas/instagram_transcrever.py alvos
```

É `workflow_dispatch`. Não é teste, não é histórico, não é comentário, não é
fixture — é **despacho de produção**, e qualquer pessoa com acesso ao repositório
o pode disparar.

    UMA PORTA QUE NENHUM IMPORT MOSTRA CONTINUA A SER UMA PORTA.

E o pipeline é completo e fecha em si mesmo:

1. `fase=janela` → `coleta/instagram_janela.py` escreve `INSTAGRAM-JANELA`
2. o próprio workflow **faz commit** dos caminhos `INSTAGRAM-*` de volta ao repositório
3. `fase=transcrever` → a velha lê esse corpus e baixa o MP4 inteiro de cada alvo

> **Nota de medição.** `INSTAGRAM-JANELA` e `INSTAGRAM-TRANSCRICOES` não existem
> nesta árvore, **não estão em `.gitignore`**, e `git log --all` não encontra um
> único commit que os tenha tocado. A ausência é real, não é gitignore — foi
> conferida, porque esta casa já foi mordida por uma busca que não achou nada num
> sítio ignorado. Mas o produtor do corpus existe e tem fase própria: a ausência
> de dado hoje não é ausência de rota.

Veredito:

```
OLD_PATH_MODULE_EXISTS     = YES
OLD_PATH_EDGE_EXISTS       = NO   pelo pedido canónico
OLD_PATH_RUNTIME_REACHABLE = YES  pelo workflow_dispatch
OLD_PATH_FLOW_OBSERVED     = NO   nesta árvore, por falta do corpus
```

---

## 4. O QUE ISSO FAZIA À DECISÃO HUMANA

A C10.5D fechou:

```
INSTAGRAM_REMOTE_ACQUISITION = NOT_ALLOWED
```

Medido: **nem `instagram_transcrever.py` nem `instagram_janela.py` mencionavam
`social_matriz`, `politica_da_aquisicao` ou `scrap_http`.** Zero, nos dois.

A decisão não alcançava aquela porta.

    UMA DECISÃO QUE UMA PORTA NÃO CONHECE NÃO É UMA DECISÃO. É UM DESEJO.

### O que esta missão fez

Ligou a velha ao **mesmo dono da decisão**, nos seus dois pontos de rede:

```
_baixar()    → pergunta antes de abrir o socket
_url_nova()  → pergunta antes de subir o navegador para o embed
```

Grátis não é permitido: abrir o embed é tocar a plataforma. Agora, sob a decisão
actual, a velha levanta `PermissionError` e **não escreve ficheiro nenhum**.

Isto **não altera política**. Lê a que já está escrita, no mesmo dono que a
cadeia nova lê. É a mesma capacidade, `INSTAGRAM/FETCH_TRANSCRIPT`, e as duas
implementações declaram-na com a mesma constante.

    UMA DECISÃO, TODAS AS PORTAS.

---

## 5. O QUE ESTA MISSÃO NÃO FEZ, E PORQUÊ

**Não apagou a fase do workflow.** Retirar uma entrada operacional é mudança
externa e difícil de reverter, e o §6 é explícito: não apagar por estética,
censar antes, provar regressão. O censo está feito e está aqui. A decisão de
aposentar a fase `transcrever` do workflow — e com ela o pipeline
`INSTAGRAM-JANELA` — é de gente, e é o bloqueador humano desta missão.

**Não tocou na política.** O §9 é claro: a C10.4B não é missão de política.

---

## 6. MUTAÇÃO OBRIGATÓRIA

Introduzida a queda silenciosa para o caminho velho, em
`midia_por_ytdlp`, logo depois de `AUDIO_ONLY_UNAVAILABLE`:

```
import instagram_transcrever as velho
n = velho._baixar(url, alvo)
```

**Morta por três testes:**

```
tests/test_c10_4b_um_caminho_so · test_a_nova_nao_importa_a_velha_em_lado_nenhum
tests/test_c10_audio_only      · test_sem_formato_de_audio_o_estado_diz_isso_e_nao_baixa_video
tests/test_c10_audio_only      · test_a_rota_de_audio_nao_conhece_rota_paga
```

---

## 7. RED TEAM — DOZE TENTATIVAS, ONZE QUEDAS

| # | tentativa | medida |
|---|---|---|
| 1 | o registo despacha para a velha | nenhuma capacidade aponta para ela |
| 2 | a velha entra por alias | nenhum alias no adaptador |
| 3 | queda para a velha depois de erro | a nova não a importa |
| 4 | queda depois de `AUDIO_ONLY_UNAVAILABLE` | caminho `None`, estado preservado |
| 5 | ajudante de teste usado em produção | importadores só em `tests/` |
| 6 | import lateral evita o roteador | nem a fase de fala nem a cadeia a importam |
| 7 | capacidade velha com outro nome | 7 capacidades Instagram, nenhuma nova |
| 8 | **a matriz nomeia a implementação velha** | **NÃO CAIU** — ver abaixo |
| 9 | o executor chama a velha directamente | `scrap_executor` não a menciona |
| 10 | o mapa esconde a velha | o mapa cita-a; não a esconde |
| 11 | vídeo inteiro num teste positivo | 1 pedido, `-f bestaudio` |
| 12 | «deprecated» em comentário com caminho vivo | a porta está nomeada no ficheiro **e** travada por código |

### RT8, que não caiu

```
INSTAGRAM/FETCH_TRANSCRIPT
  ROTA      = 'instagram_transcrever.py:faster-whisper'
  PERMITIDA = NAO
```

A política **nomeia a implementação velha**. Sob `PERMITIDA = NAO` isso não
autoriza nada — a rota está recusada seja qual for o ficheiro que a sirva — mas
o nome continua a apontar para o lado errado. Corrigi-lo é editar o ficheiro de
política, e o §9 proíbe isso aqui. Fica registado, como já estava desde a C10.4.

---

## 8. VEREDITO

```
NEW_PATH  OWNER = ferramentas/reel_transcricao.py
          ENTRYPOINT = scrap_executor → social_rotas → adaptador_instagram
          RUNTIME_REACHABLE = YES

OLD_PATH  OWNER = ferramentas/instagram_transcrever.py
          ENTRYPOINT = .github/workflows/sintonia-scrap.yml · fase=transcrever
          MODULE_EXISTS = YES
          EDGE_EXISTS = NO (canónico) · YES (workflow)
          RUNTIME_REACHABLE = YES
          FLOW_OBSERVED = NO (corpus ausente nesta árvore)
          CAN_ACQUIRE_NOW = NO (travada pela decisão, desde esta missão)

SAME_CONCEPT = YES — «obter fala de Reel», pelo método que a C8 proíbe
DISTINCT_CONCEPT = NO — corpus diferente não é conceito diferente

TRANSCRIPTION_LIVE_OWNER_COUNT = 2   (1 canónico + 1 por workflow)
VIDEO_FALLBACK = NO
ASR_OWNERS = 1

C10_4B_DUPLICATE_PATH = DUPLICATE_REACHABLE
```

`PASS` exigiria `TRANSCRIPTION_LIVE_OWNER_COUNT = 1`. São dois, e o segundo só
desaparece quando alguém decidir aposentar a fase do workflow.

    O OBJETIVO NÃO É TER MENOS FICHEIROS. É ONE CONCEPT → ONE OWNER.
    E hoje há um conceito com dois donos, um deles travado.

Por isso, e conforme o §12 do briefing: **HARD STOP da linha Instagram.** A C10.5
não começa com duas rotas vivas.
