# C10.4C — APOSENTAR A ROTA LEGADA DE TRANSCRIÇÃO DE REEL

`C10_4C_RETIRE_LEGACY = PASS`

> A C10.4B mediu duas portas para o mesmo conceito e travou uma pela política.
> Travar não é aposentar. A C10.4C fechou-as.
>
> ```
> BLOCKED != RETIRED.   DISABLED != RETIRED.
> ONE CONCEPT -> ONE OWNER.
> ```

---

## 1 · O QUE ESTAVA ABERTO

`ferramentas/instagram_transcrever.py` implementava «obter a fala de um Reel»
pelo caminho que a C8 proibiu:

```
baixar o MP4 INTEIRO  ->  ffmpeg -vn  ->  ASR
```

    TRANSCRIPTION NEED != VIDEO DOWNLOAD.

A C10.4B mediu: **zero importadores Python de produção**, **não alcançada pelas
seis entradas canônicas** — e mesmo assim **alcançável**. Nenhum `import` mostrava
a porta.

    UMA PORTA QUE NENHUM IMPORT MOSTRA CONTINUA A SER UMA PORTA.

O censo desta missão encontrou **seis** portas operacionais, não cinco. A sexta
não estava no relatório da C10.4B porque ninguém tinha procurado ali.

| # | porta | o que era | fechada em |
|---|---|---|---|
| 1 | `workflow_dispatch` · opção `transcrever` | despacho de produção | `321a31c3` |
| 2 | `workflow_dispatch` · opção `transcrever-alvos` | despacho de produção | `321a31c3` |
| 3 | `run:` · `instagram_transcrever.py rodar` | o comando | `321a31c3` |
| 4 | `run:` · `instagram_transcrever.py alvos` | o comando | `321a31c3` |
| 5 | `__main__` do próprio ficheiro | CLI operacional | `5fe7be9c` |
| 6 | `coleta/social_scrap.py` **imprimia** «faster-whisper local → `scripts/instagram_transcrever.py`» | instrução operacional | `004e52e1` |

A sexta merece o nome próprio:

    DOCUMENTAÇÃO OPERACIONAL USADA COMO COMANDO É UMA PORTA.

E o caminho que ela imprimia nem existia — `scripts/` virou `ferramentas/` há
muito. Uma instrução operacional errada continua a ser uma instrução.

Havia ainda **duas guardas** que esperavam pela fase: o portão do navegador e o
pré-voo do `ffmpeg` listavam `transcrever` no seu `if:`. Nenhuma era chamada —
com `type: choice` o valor recusado não chega a shell nenhuma. Mas quem lesse o
workflow leria ali que a fase continuava de pé.

    APAGAR A PORTA E DEIXAR O PORTEIRO NÃO FECHA A CASA.

---

## 2 · A JANELA NÃO ERA A MESMA COISA, E FICOU

```
INSTAGRAM_WINDOW_DISTINCT_CAPABILITY = YES
INSTAGRAM_WINDOW_PRESERVED           = YES
```

`coleta/instagram_janela.py` **não foi tocado**. Medido na árvore, não no texto:

| pergunta | medido |
|---|---|
| importa `fala_local`? | não |
| importa `instagram_transcrever`? | não |
| importa `reel_transcricao`? | não |
| monta `ffmpeg`, `-vn`, `bestaudio`, `yt-dlp`? | não |
| instancia `WhisperModel(`? | não |

Ela faz **descoberta, perfil e metadados**. O corpus que produz alimentava a
fila da rota velha — e é a isso que a tentação responde:

    CORPUS DIFERENTE NÃO É CONCEITO DIFERENTE.
    Mas produzir o corpus também não é consumi-lo.

`tests/test_c10_4c_janela_preservada.py` prova a metade permitida **sem tocar no
Instagram**: obediência ao lote congelado (5 contas, e uma delas com
`instagram.com` sem `www.` — as duas formas são reais), o parser de número
arredondado, o resgate de legenda pela etiqueta `og:` com `CAPTION_IS_COMPLETE`
declarado, e o slug de ficheiro. Com armadilha no navegador: se alguma destas
provas tentasse subir Chrome, gritava.

```
INSTAGRAM_REQUESTS = 0 · APIFY_RUNS = 0 · PAID_RUNS = 0 · COST_USD = 0
```

---

## 3 · O QUE FICOU NO FICHEIRO APOSENTADO, E PORQUÊ

Ele encolheu de 441 para 132 linhas. Todas as seis funções levantam
`RotaAposentada`. O `__main__` recusa **alto**, com código 2:

Medido em seis formas de argumento — nenhuma, `rodar`, `alvos`, `--help`, `-h`,
e `rodar small 5`. As seis devolvem **código 2**, e em todas o `stderr` abre com
`ROTA_APOSENTADA:` seguido do nome do dono canônico.

    UM SCRIPT QUE SAI 0 SEM FAZER NADA DIZ QUE CORREU.

> Este documento **não escreve a invocação**. O ataque 9 desta mesma missão
> marca uma linha de comando dentro de um documento como porta — e marcou esta,
> quando ela estava aqui em forma de `$ py …`. Que o comando só produza recusa
> não muda a forma: quem procura «como transcrevo um reel» copia o que parece
> um comando.
>
>     UMA DEMONSTRAÇÃO EM FORMA DE INSTRUÇÃO É UMA INSTRUÇÃO.

Saíram três coisas que o faziam **parecer** um dono do conceito:

| saiu | porquê |
|---|---|
| `import fala_local` | um aposentado que carrega o reconhecedor continua a ser contado, por todos os censos, como transcritor |
| `politica_da_aquisicao` | quem não adquire não precisa de autorização para adquirir. Um portão à frente de uma função que levanta é cerimônia — e cerimônia parece capacidade |
| o docstring operacional | as três primeiras linhas eram comandos para copiar |

E o ficheiro **fica**, porque a medição fica. O que ele cronometrou em
2026-09-02 — `tiny` 18,7x, `base` 9,4x, `small` 3,2x, num reel real de 110 s —
está citado em `ferramentas/youtube_transcrever.py`,
`coleta/youtube_relevancia.py` e em seis documentos da casa. Apagar o ficheiro
apagaria a proveniência desses números. Aposentar a rota não pede isso.

**O que a fila dele escolhia** fica registado aqui, porque o código saiu:
`alvos()` aceitava objeto com `IS_VIDEO = YES`, recusava `AUDIO_NAME` de
catálogo (`'riginal' not in audio`) por ser sinal de que não há fala, e exigia
`VIDEO_URL_TEMPORARY` presente. São critérios do caminho de **vídeo inteiro** —
o último deles nem faz sentido para uma rota audio-only. É parte da rota
aposentada, não capacidade à parte. Se o dono canônico vier a precisar de fila,
constrói a dele, com o nome dele.

---

## 4 · O DONO ÚNICO

```
TRANSCRIPTION OWNER = coleta/adaptador_instagram.py -> ferramentas/reel_transcricao.py
ASR_OWNERS          = 1   (ferramentas/fala_local.py)
```

Medido no registo, não na intenção: **uma** entrada registada traduz para
`FETCH_TRANSCRIPT` do Instagram —
`instagram.reel.transcribe` → `adaptador_instagram`. O próprio
`scrap_registo.registar` já recusa dois donos da mesma `(plataforma,
capacidade)`; o que ele não via sozinho era um segundo dono a entrar por outro
nome de capacidade que significasse o mesmo. Agora conta-se pela tradução.

A política **não foi tocada** — `INSTAGRAM/FETCH_TRANSCRIPT` continua
`PERMITIDA = NAO`, `ESTADO = ROUTE_NOT_ALLOWED`, decisão da C10.5D. Esta missão
não pergunta se a rota pode; pergunta quantas rotas existem.

---

## 5 · O MAPA DECLARAVA UMA ARESTA QUE NÃO EXISTIA

Ao regenerar a cadeia completa, o censo da coleta declarou que a rota
**aposentada** chamava `reel_transcricao`, `adaptador_instagram` e
`youtube_transcrever` — e que dois deles corriam no CI.

Nada disso era verdade. A fonte de todas essas arestas era o **docstring** que
explica a aposentadoria e o **comentário** do workflow que a anuncia. O módulo
importa `sys` e mais nada.

    UM NOME DENTRO DE UMA FRASE NÃO É UM ARGV.

`system-map/scripts/censo_da_coleta.py` media `chamado_por` com
`if outro in texto` — o texto inteiro, comentário e docstring incluídos. Passou
a medir três coisas separadas:

| campo | o que é |
|---|---|
| `chamado_por` | `import` medido na árvore, **ou** o caminho numa linha que a máquina executa, **e** só se o ficheiro chegar a lançar processo |
| `citado_por` | o caminho aparece, mas em prosa. **Não é aresta** — e continua registado, porque uma instrução operacional é uma porta, e esta missão fechou uma assim |
| `no_ci` | o caminho aparece numa linha **não-comentário** de um workflow |

O terceiro critério do `chamado_por` é o que resolve o caso: um ficheiro que
nunca lança processo e nunca importa nada não pode estar a correr outro pelo
caminho, por mais vezes que o nomeie.

`orfaos` continua a significar o que significava — ninguém o chama, ninguém o
corre, ninguém sequer o nomeia — porque `citado_por` entra na conta. Ao lado
dele nasceu o número mais apertado, `sem_aresta_medida`: 46 contra 63.

E o censo de derivações declarava `instagram_transcrever.py` como **PRODUTOR**
de transcrição de reel: o mapa a registar um segundo dono. Passa a declarar
`ferramentas/reel_transcricao.py`.

---

## 6 · MUTAÇÃO

```
MUTANTS            = 6
MUTATION_SURVIVORS = 0
```

| # | mutação | quem a matou |
|---|---|---|
| M1 | `transcrever` volta ao `workflow_dispatch` | `test_1…`, `test_a_porta_do_workflow_foi_fechada_na_c10_4c` |
| M2 | `run:` volta a chamar `instagram_transcrever.py` | `test_2…`, `test_a_porta…` |
| M3 | a cadeia canônica ganha fallback para o vídeo inteiro | `test_6…`, `test_a_nova_nao_importa_a_velha…` |
| M4 | `AUDIO_ONLY_UNAVAILABLE` chama a velha — **por `subprocess`, sem `import`** | `test_11_a_cadeia_viva_nao_nomeia_a_rota_velha_em_literal_nenhum` |
| M5 | entrypoint CLI operacional volta ao script velho | `test_4_o_CLI_recusa_alto_seja_qual_for_o_argumento` |
| M6 | dois owners registrados para TRANSCRIPTION | cinco testes, entre eles `test_13…` |

M4 é a que importa medir: uma suíte que só olha para `import` sobrevive a ela.

---

## 7 · RED TEAM

```
ATAQUES                   = 20
PORTAS_OPERACIONAIS_VIVAS = 0
RED_TEAM_RESULT           = PASS
```

Cada ataque diz **o que mediu**, e não só o que não encontrou:

| # | ataque | medido |
|---|---|---|
| 1 | alias da fase velha | 22 opções lidas; o ramo `*)` cai em `instagram_coleta.py`, que não a importa |
| 2 | workflow reutilizável | 0 `workflow_call`, 0 `uses:` locais |
| 3 | outro `workflow_dispatch` | 19 workflows com dispatch |
| 4 | `schedule` | 1 workflow agendado |
| 5 | CLI direto | 6 formas de argumento, todas `rc=2` |
| 6 | shell / make / npm | 167 ficheiros de script |
| 7 | `subprocess` | 104 chamadas de subprocesso inspecionadas |
| 8 | import dinâmico | 9 chamadas dinâmicas |
| 9 | doc operacional como comando | 39 linhas de doc que a nomeiam, 0 executáveis |
| 10 | retry que cai na velha | 11 laços na cadeia |
| 11 | erro da nova que cai na velha | 7 handlers na cadeia |
| 12 | policy negative que cai na velha | 1 ponto de recusa, 21 imports |
| 13 | janela transcrevendo por dentro | 12 imports da janela |
| 14 | teste confundido com produção | 5 testes a citam; 6 ficheiros de produção também, todos em prosa |
| 15 | mapa escondendo edge viva | 7 PRODUTORES declarados |
| 16 | comentário confundido com edge | controlo positivo do filtro: OK |
| 17 | ficheiro existir = owner | 6 funções, 6 levantam |
| 18 | código renomeado, mesmo comportamento | 1 ficheiro corta imagem, 21 trazem mídia; interseção vazia |
| 19 | output diferente como desculpa | 1 dono registrado |
| 20 | corpus diferente como desculpa | a janela produz e não transcreve |

**Três ataques falharam primeiro contra a própria sonda, não contra a casa.**

- **#7** contou *nomes* e achou quatro — a mensagem de recusa do próprio
  aposentado, uma nota de proveniência, e o rótulo da rota na matriz. Passou a
  medir **posição**: o literal só conta dentro de uma chamada de subprocesso.
- **#15** leu o *texto* do censo e apanhou o comentário que explica a troca do
  PRODUTOR. Passou a ler as declarações.
- **#18** marcou qualquer ficheiro com `-vn` e apanhou `fala_local.py`, que
  converte um ficheiro **já em disco**. O comportamento proibido precisa das
  duas metades: trazer da rede **e** cortar. Na primeira correção o filtro de
  rede aceitava `dict.get` e dizia que 171 ficheiros traziam mídia — o número
  era da sonda, não da casa.

```
UMA SONDA QUE ENCONTRA ZERO E DIZ «LIMPO» MEDE A SONDA.
UMA SONDA QUE CONTA NOMES CONTA NOMES, NÃO CHAMADAS.
```

---

## 8 · REGRESSÃO

```
TESTS_BEFORE    = 2293      FAILURES_BEFORE = 23
TESTS_AFTER     = 2321      FAILURES_AFTER  = 21
NEW_FAILURES    = 0
ASR_OWNERS      = 1
```

Baseline corrida em `git worktree` sobre `f896e832`, a mesma suíte, módulo a
módulo. O conjunto de falhas depois é **subconjunto** do de antes.

As duas que desapareceram **não foram reparadas por esta missão** — são
artefatos de correr do caminho do worktree: `test_branch_vivo_nao_e_alvo_congelado`
lê o ramo vivo (o worktree está em HEAD destacado) e
`test_gravar_raw_respeita_o_redirecionamento` compara um caminho relativo que a
profundidade do worktree transforma em `../../../..`. As 21 restantes são as
mesmas de antes, e são anteriores a esta missão.

### As seis sentinelas da C10.4B que esta missão teve de actualizar

Elas mediam a porta **aberta**: exigiam a fase no workflow, o portão de política
na rota velha, e cobertura das suas duas saídas de rede. Era a medição certa
para um mundo onde a porta existia — e a própria C10.4B escreveu, no corpo do
teste, que apagar a entrada era decisão de gente. A C10.4C é essa decisão.

    UMA SENTINELA QUE CONTINUA A MEDIR UM MUNDO QUE ACABOU MEDE O PASSADO.

Nenhuma foi apagada: cada uma passou a medir que a porta **não voltou**, e o que
media antes ficou escrito no seu docstring. A de cobertura de portão virou a
afirmação mais forte — **zero** pontos de rede — e leva controlo positivo sobre
o dono canônico, onde a sonda **tem** de encontrar saída.

E em `tests/test_reel_transcricao.py`, eram três chamadores do reconhecedor; são
dois. Exigir `import fala_local` ao aposentado seria exigir que ele parecesse
vivo.

---

## 9 · SYSTEM MAP

Cadeia canônica **completa**, os sete passos de
`system-map/scripts/CADEIA-DO-MAPA.json`, lidos do ficheiro e não de cabeça:

```
scan_repo · scan_sources · scan_casco · censo_da_coleta
pente_fino_da_coleta · censo_dos_buracos · generate_system_map
validate_system_map  ->  SYSTEM_MAP_CHECK=PASS
```

    RODAR DOIS DE SETE NÃO É REGENERAR O MAPA.

O que o mapa passou a dizer sobre a rota aposentada:

| campo | antes | depois |
|---|---|---|
| `linhas` | 441 | 132 |
| `sai_para_fora` | `true` | `false` |
| `descarta` | `true` | `false` |
| `escreve_ficheiro` | `true` | `false` |
| `veiculos` | `HTTP DIRETO`, `INSTAGRAM`, `YOUTUBE` | `INSTAGRAM`, `YOUTUBE` (prosa) |
| `ferramentas` | `APIFY (rota paga)`, `TRANSCRICAO` | `TRANSCRICAO` (prosa) |
| `chamado_por` | `[fala_local]` | `[]` |
| `citado_por` | — | `[fala_local]` |
| `executores_que_saem_para_fora` | 23 | 22 |

---

## 10 · O QUE ESTA MISSÃO NÃO FEZ

- não mexeu em `leis/social_matriz.py` — a decisão da C10.5D é dela;
- não autorizou Instagram remoto, não baixou mídia, não tocou a plataforma;
- não mexeu em Admission, Source Relevance, Intelligence, Portal, Supabase LIVE,
  Vercel, LinkedIn ou X;
- não implementou checkpoint durável (C10.6B), não reabriu a C10.5.

### Dívidas declaradas, não pagas

1. **`leis/social_matriz.py` continua a chamar a rota
   `instagram_transcrever.py:faster-whisper`** e a dizer, em prosa, que esse
   ficheiro «já transcreve local». O rótulo está velho. Mexer na matriz estava
   **fora do escopo** desta missão por instrução explícita — e a matriz é o dono
   da decisão, não um sítio onde se arruma nomenclatura de passagem.
   `mz.decisao()` continua correto: a capacidade é a mesma, a decisão é a mesma,
   e o adaptador canônico atravessa o portão. É o **nome** que mente.
2. **Seis ficheiros de produção citam a rota aposentada em prosa** —
   `adaptador_instagram`, `youtube_janela`, `youtube_relevancia`, `fala_local`,
   `youtube_transcrever`, `social_matriz`. Todas as citações são de
   **proveniência de medição** (o benchmark de 2026-09-02) e nenhuma é uma
   instrução. Ficam.
3. **`fala_local.modelo_de` ainda mapeia `instagram_transcrever → small`.** Uma
   entrada órfã numa tabela de política, sem chamador. Não é uma porta.

---

## 11 · VEREDITO

```
C10_4C_RETIRE_LEGACY                 = PASS
LEGACY_TRANSCRIPTION_ROUTE           = RETIRED
OPERATIONAL_DOORS_BEFORE             = 6
OPERATIONAL_DOORS_AFTER              = 0
TRANSCRIPTION_OWNERS                 = 1
ASR_OWNERS                           = 1
INSTAGRAM_WINDOW_DISTINCT_CAPABILITY = YES
INSTAGRAM_WINDOW_PRESERVED           = YES
MUTANTS                              = 6
MUTATION_SURVIVORS                   = 0
RED_TEAM_RESULT                      = PASS
NEW_FAILURES                         = 0
SYSTEM_MAP_CHECK                     = PASS
POLICY_CHANGED                       = NO
INSTAGRAM_REQUESTS                   = 0
APIFY_RUNS                           = 0
PAID_RUNS                            = 0
COST_USD                             = 0
```

**ONE CONCEPT → ONE OWNER: satisfeito.**
