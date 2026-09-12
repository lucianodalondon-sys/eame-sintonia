# META-DEEP-01 — RAIO-X PROFUNDO DA META PARA O SINTONIA SCRAP

```
MEDIDO_EM               = 2026-09-12
META_PLATFORM_PROBES    = 0
APIFY_RUNS              = 0
PAID_RUNS               = 0
COST_USD                = 0
ROTAS_IMPLEMENTADAS     = 0
POLICY_ALTERADA         = NAO
```

> **ISTO É EVIDÊNCIA DE MISSÃO, NÃO BÍBLIA.**
> Não é MASTER, não substitui contrato nenhum, e não promove capacidade
> nenhuma. É o mapa do que a família Meta oferece e do que esta casa
> consegue observar dela — medido onde deu para medir, pesquisado onde só
> deu para pesquisar, e `NÃO SEI` onde nenhuma das duas coisas deu.

**A pergunta da missão:**

> QUAL É O MÁXIMO DE ATIVIDADE PÚBLICA DE CONCORRENTES QUE O SINTONIA SCRAP
> CONSEGUE OBSERVAR NA META, USANDO PRIMEIRO ROTAS OFICIAIS, GRATUITAS E
> LOCAIS, E APIFY SOMENTE PARA O QUE REALMENTE NÃO CONSEGUIMOS SUBSTITUIR?

**A resposta curta, e ela é desconfortável:**

```
A MAIOR ROTA OFICIAL, GRATUITA E PERMITIDA DA FAMÍLIA META PARA OBSERVAR
CONCORRENTE — A AD LIBRARY — NÃO EXISTE EM LADO NENHUM DESTE REPOSITÓRIO.
NEM COMO CAPACIDADE, NEM COMO POLÍTICA, NEM COMO PALAVRA.
```

Não está bloqueada. Não foi recusada. Não foi medida e reprovada.
**Nunca foi olhada.** O mesmo vale para BRANDED CONTENT. E o Threads tem
política sem capacidade — o inverso exato do que a C12 encontrou no X.

---

## REGRA ZERO — O ESTADO DO GIT, MEDIDO ANTES DE TUDO

```
CURRENT_BRANCH   claude/wonderful-hamilton-m50ahv
CURRENT_HEAD     5bcc44f54afefba44bfef9d6b1d2cd713b33f369
REMOTE_HEAD      origin/main = df165da928549d9e3427b4c518bd8d70e7fb9058
WORKTREE_STATUS  limpa
```

### O HEAD funcional do SCRAP não é a `main`, e isso foi medido, não assumido

`git fetch --all --prune` trouxe 60+ ramos. O ramo padrão `main` **não carrega
o SINTONIA SCRAP**: `git ls-tree` sobre ele não encontra `coleta/scrap_executor.py`,
`coleta/scrap_capacidades.py` nem `coleta/scrap_registo.py`. O único ficheiro do
SCRAP que a `main` conhece é o workflow `.github/workflows/scrap-social.yml`,
posto lá pelo PR #3 exatamente para ficar registado como dispatcher — e o próprio
commit diz que **isso não promove o SCRAP para a main**.

O HEAD funcional mais recente do SCRAP, medido por data de commit sobre os ramos
que carregam o executor:

| data do commit | ramo | HEAD |
|---|---|---|
| **2026-09-12 15:54** | **`claude/sintonia-scrap-first-paid-route-c10-8b`** | **`5bcc44f5`** |
| 2026-09-12 14:43 | `claude/sintonia-scrap-financial-budget-c10-8af` | `532e3bed` |
| 2026-09-12 13:44 | `claude/sintonia-scrap-trial-network-budget-c10-8ar` | `9c720dfe` |
| 2026-09-12 13:03 | `claude/sintonia-scrap-bluesky-live-trial-c10-8a` | `509d2b59` |

`main` está **1 commit à frente** da base comum e **323 commits atrás** da ponta do
SCRAP. Este trabalho nasce sobre `5bcc44f5`, que é o HEAD funcional, e não sobre a
`main`, que é o dispatcher.

    RAMO PADRÃO NÃO É RAMO FUNCIONAL. Escrever o estudo sobre a `main` seria
    medir uma árvore que não contém o objeto medido.

### Os ficheiros que a missão mandou ler

| pedido | estado | onde |
|---|---|---|
| `coleta/scrap_executor.py` | presente, 811 linhas | lido |
| `coleta/scrap_capacidades.py` | presente, 324 linhas | lido |
| `coleta/scrap_registo.py` | presente, 211 linhas | lido |
| `coleta/social_rotas.py` | presente, 353 linhas | lido |
| `coleta/scrap_http.py` | presente, 425 linhas | lido |
| `coleta/scrap_fornecedores.py` | presente, 230 linhas | lido |
| `coleta/adaptador_instagram.py` | presente, 449 linhas | lido |
| `coleta/adaptador_facebook.py` | presente, **37 linhas** | lido |
| `leis/social_matriz.py` | presente, 829 linhas | lido |
| **adapter de Threads** | **NÃO EXISTE** | — |
| **`SINTONIA-EAME-KNOW-HOW.md`** | **NÃO EXISTE NESTA LINHAGEM** | vive em `claude/sintonia-eame-know-how-v1`, que não carrega o SCRAP |

O know-how canônico e o SCRAP estão em ramos que não se tocam. Isto não é
achado desta missão — a C10 já o tinha registado — mas é o motivo pelo qual
`KNOW_HOW_DELTA` desta missão não pode ser escrito contra um ficheiro que a
árvore de trabalho não contém.

---

## PARTE 1 · O QUE O SCRAP TEM HOJE, NA META

Medido executando o próprio código — `scrap_capacidades`, `scrap_registo`,
`scrap_executor.CHECK` e `social_matriz.decisao` — com zero rede e zero custo.
`CHECK` é, por construção, o verbo que não gasta.

### INSTAGRAM — 7 declaradas, 7 registadas, 4 com caminho

| capacidade | `STATE` | `REGISTERED` | `WIRED` | `CHECK` responde | `POLICY` |
|---|---|---|---|---|---|
| `instagram.profile.discovery` | `PARTIAL` | YES | **`ROTA` (com portão)** | `CAN_COLLECT_NOW` | `ALLOWED` · `instagram_janela.py:grade` |
| `instagram.reel.transcribe` | `PROVEN` | YES | **`ROTA` (com portão)** | `CAN_COLLECT_NOW` | **`ROUTE_NOT_ALLOWED`** |
| `instagram.reel.capture` | `PROVEN` | YES | `EXECUTA` (sem portão) | `CAN_COLLECT_NOW` | — sem tradução na matriz |
| `instagram.reel.audio` | `PROVEN` | YES | `EXECUTA` (sem portão) | `CAN_COLLECT_NOW` | — sem tradução na matriz |
| `instagram.post.comments` | `BLOCKED` | YES | **sem caminho** | `CAPABILITY_STATE_PROMISES_NOTHING` | `ALLOWED` · `apify:comments` |
| `instagram.story.capture` | `UNKNOWN` | YES | **sem caminho** | `CAPABILITY_STATE_PROMISES_NOTHING` | — |
| `instagram.story.transcribe` | `NOT_EXECUTED` | YES | **sem caminho** | `CAPABILITY_STATE_PROMISES_NOTHING` | — |

**A contradição que salta, e é a primeira do relatório:**

```
instagram.reel.transcribe   CHECK = CAN_COLLECT_NOW
                            POLICY = ROUTE_NOT_ALLOWED
```

As duas frases estão certas e dizem coisas diferentes. `CHECK` responde «existe
caminho registado e o estado promete resultado». A política responde «sair para
a plataforma não é permitido». Quem resolve o conflito é o portão que vive no
ponto onde o socket abre, dentro da cadeia — decisão da C10.5D, e correta.

Mas quem chama `CHECK` e para de ler ali **lê um sim onde há um não**.

    UM `CAN_COLLECT_NOW` QUE DEPENDE DE UM PORTÃO MAIS ABAIXO PARA VIRAR NÃO
    É UMA RESPOSTA. É UMA PROMESSA COM LETRA MIÚDA.

### FACEBOOK — 4 declaradas, 4 registadas, **0 com caminho**

| capacidade | `STATE` | `REGISTERED` | `WIRED` | `CHECK` responde | `POLICY` |
|---|---|---|---|---|---|
| `facebook.identity.discovery` | `PARTIAL` | YES | **sem caminho** | `DECLARED_WITHOUT_ROUTE` | `ALLOWED` · `graph:/pages/search` |
| `facebook.content` | `BLOCKED` | YES | sem caminho | `CAPABILITY_STATE_PROMISES_NOTHING` | `ALLOWED` · `graph:/{page-id}/posts` |
| `facebook.media` | `BLOCKED` | YES | sem caminho | `CAPABILITY_STATE_PROMISES_NOTHING` | `ALLOWED` · `graph:/{page-id}/videos` |
| `facebook.metrics` | `BLOCKED` | YES | sem caminho | `CAPABILITY_STATE_PROMISES_NOTHING` | — |

O adaptador de Facebook tem **37 linhas e nenhuma função**. São quatro
`reg.registar(...)` e um docstring. Isso é honesto — o registo aceita declaração
sem execução de propósito — mas o número que interessa é este:

```
FACEBOOK_WIRED = 0 de 4.
```

### THREADS — 0 declaradas, 0 registadas, 0 com caminho, **2 linhas de política**

```
THREADS em scrap_capacidades.DECLARADAS ............ 0
THREADS em scrap_registo._MAPA ..................... 0
adaptador de Threads ............................... NÃO EXISTE
THREADS em leis/social_matriz.MATRIZ ............... 2 capacidades, 2 rotas
THREADS em guarda/social_sessao.py ................. 1 cláusula escrita
```

A matriz declara `SEARCH_KEYWORD` e `SEARCH_HASHTAG` pelo mesmo endpoint
`threads:/v1.0/keyword_search`, `OFFICIAL_API_FREE`, `PERMITIDA = CONDICIONAL`,
`ESTADO = CREDENTIAL_MISSING`. E `social_sessao.py` já escreveu, por extenso,
que este é *«o único endpoint da família desenhado para monitorar conteúdo
público de terceiro»*.

    É A INVERSÃO EXATA DO X. Lá havia capacidade provada sem política. Aqui há
    política declarada sem capacidade nenhuma. Nos dois casos o resultado é o
    mesmo: nada corre.

### E as três famílias que não existem em lado nenhum

Varrido o repositório inteiro por `ads_archive`, `ad_library`, `FETCH_ADS`,
`SEARCH_ADS`, `advertis`, `branded`, `paid_partnership`:

| família | ocorrências em `.py` | veredito |
|---|---|---|
| **ADS / Ad Library** | **0** | não existe como capacidade, rota, política ou palavra |
| **BRANDED CONTENT** | 0 em coleta; 3 em `pacote/` como **rótulo de leitura**, não rota | não existe como aquisição |
| **THREADS (capacidade)** | 0 | política sem capacidade |

E o vocabulário fechado da matriz — as doze capacidades grossas de
`social_matriz.CAPACIDADES` — **não tem nenhuma palavra para anúncio**:

```
DISCOVER_ACCOUNT · DISCOVER_POST · SEARCH_KEYWORD · SEARCH_HASHTAG
FETCH_PROFILE · FETCH_POST · FETCH_VIDEO_METADATA · FETCH_VIDEO_BYTES
FETCH_COMMENTS · FETCH_METRICS · FETCH_TRANSCRIPT · INCREMENTAL
```

    UMA FERRAMENTA DE CONCORRÊNCIA QUE NÃO TEM PALAVRA PARA «ANÚNCIO» NÃO
    ESTÁ ATRASADA NA IMPLEMENTAÇÃO. ESTÁ ATRASADA NO VOCABULÁRIO.

### O que a casa REALMENTE tem da Meta, em ficheiros

| medida | valor |
|---|---|
| objetos com `PLATFORM = INSTAGRAM` preservados | 5 ficheiros |
| objetos com `PLATFORM = FACEBOOK` preservados | 3 ficheiros |
| objetos com `PLATFORM = THREADS` preservados | **0** |
| Reels transcritos no disco | 4 (`REEL-TRANSCRICOES/`) |
| runs pagos de Meta na história desta casa | **1** |
| contas Meta no lote congelado de concorrentes | 15 (10 FB · 5 IG · **0 Threads**) |
| `CONTENT_COLLECTION_STAGE` do lote congelado | **`NOT_STARTED`** |

---

## O ÚNICO RUN PAGO DE META DA HISTÓRIA DESTA CASA

`data/samples/RUN-MANIFEST.json`, run `ES-T8-003-2026-08-29-a`:

```
ACTOR ................... apify/instagram-hashtag-scraper
INPUT ................... hashtags: repilo · olivar · sanidadvegetal   resultsLimit: 20
COUNTRY ................. ES        (não IT, não EAME)
ITEM_COUNT_RAW .......... 60
ITEM_COUNT_NORMALIZED ... 0
COST_USD ................ NOT_PRESERVED
STARTED_AT .............. NOT_PRESERVED
FINISHED_AT ............. NOT_PRESERVED
ACTOR_VERSION ........... NOT_PRESERVED
DATASET_ID .............. NOT_PRESERVED
```

Sessenta itens comprados, **zero normalizados**, custo desconhecido. Pela
`COL-LAW-019`, `NOT_PRESERVED` é confissão — não é zero.

```
SINTONIA_HISTORICAL_ACTUAL_COST (META) = NOT_PRESERVED
```

Este número **não pode** ser substituído pelo preço de tabela de nenhum actor.
São dois eixos, e a missão manda mantê-los separados.

### E o RAW desse run prova duas coisas que a matriz afirma ao contrário

Lido o artefato `data/samples/raw-paid/ES-T8-003-instagram-hashtags.raw.json.gz`,
60 itens, sem tocar na rede:

| campo | medido no RAW |
|---|---|
| `commentsCount` somado | **31** |
| `latestComments` com texto | **0 comentários, em 60 de 60 itens** |
| `paidPartnership = true` | **0 de 60** |
| `productType` | 47 `feed` · 13 `carousel_container` — **zero Reels, zero vídeo** |
| `musicInfo` presente | 60 de 60 |
| métricas presentes | `likesCount` · `commentsCount` — e mais nenhuma |

```
O ÚNICO ARTEFATO PAGO DE INSTAGRAM DESTA CASA TEM A CONTAGEM DE COMENTÁRIOS
E NÃO TEM UM ÚNICO COMENTÁRIO.
```

É exatamente o item 7 do red team — *comments count vira comment text* — e ele
já aconteceu, no nosso próprio disco, antes de esta missão começar.

---
## O ACHADO MAIS CARO DESTA MISSÃO — E ELE ESTAVA EM CASA

`social_matriz.gap_apify()` devolve, para a família Meta, exatamente quatro linhas:

```
["FACEBOOK",  "FETCH_POST",       "APIFY DISPENSÁVEL",  "rota livre cobre: graph:/{page-id}/posts"]
["INSTAGRAM", "FETCH_POST",       "APIFY DISPENSÁVEL",  "rota livre cobre: instagram_janela.py:embed"]
["INSTAGRAM", "FETCH_TRANSCRIPT", "SEM ROTA PERMITIDA", "nenhuma rota permitida, Apify inclusive"]
["INSTAGRAM", "FETCH_COMMENTS",   "APIFY NECESSÁRIA",   "FREE_ROUTE_INSUFFICIENT_CAPABILITY"]
```

Uma só linha diz **APIFY NECESSÁRIA** na Meta inteira, e o motivo declarado é
que a rota grátis dá o número de comentários e nunca o texto. A nota da matriz
escreve-o com todas as letras:

> *«O ÚNICO buraco real medido: a rota grátis dá o NÚMERO de comentários, nunca
> o TEXTO.»*

### Só que o ficheiro que a matriz cita como evidência mede o contrário

A linha cita `scripts/instagram_janela.py`. **Esse caminho não existe** — o
ficheiro vive em `coleta/instagram_janela.py`. E dentro dele, no comentário que
acompanha `JS_COMENTARIOS`, está escrita a medição desta casa:

> *«MEDIDO em 7 posts das 5 contas do lote, deslogado: 18 de 31 comentários
> declarados saíram COM TEXTO — 58%. Em post de 1 comentário, 100%; no de 12,
> metade.»*

```
A ROTA GRÁTIS DESTA CASA JÁ TIROU TEXTO DE COMENTÁRIO. 58%, MEDIDO,
DESLOGADO, EM SETE POSTS REAIS. A MATRIZ DIZ «NUNCA O TEXTO» E CITA COMO
PROVA O FICHEIRO QUE MEDIU O 58%.
```

O que isto **não** autoriza:

- não autoriza chamar a rota grátis de suficiente — 58% não é 100%, e
  `COMMENTS_DECLARED` contra `COMMENTS_COLLECTED` existe justamente para
  impedir que 18 sejam lidos como a audiência inteira;
- não revoga a decisão da C10.5D — `instagram.com/robots.txt` responde
  `Disallow: /` ao agente desta casa, e a rota da janela é `PUBLIC_BROWSER`
  sobre esse mesmo host;
- não promove estado nenhum. `instagram.post.comments` continua `BLOCKED`.

O que ele **muda** é o motivo declarado do gasto. `FREE_ROUTE_INSUFFICIENT_CAPABILITY`
diz «a rota grátis não sabe fazer isto». A medição diz «a rota grátis sabe fazer
isto a 58%, e o que a barra é política, não capacidade».

    SÃO DOIS MOTIVOS DIFERENTES, E O VOCABULÁRIO FECHADO DA CASA JÁ TEM OS DOIS:
    `FREE_ROUTE_INSUFFICIENT_CAPABILITY`  ≠  `ROUTE_NOT_ALLOWED`.
    Pagar pelo primeiro quando o verdadeiro é o segundo é comprar capacidade
    que já se tem para resolver uma autorização que o dinheiro não resolve.

### E as duas linhas «APIFY DISPENSÁVEL» são pior

```
FACEBOOK / FETCH_POST → "APIFY DISPENSÁVEL — rota livre cobre: graph:/{page-id}/posts"
```

A rota que a torna dispensável está `CREDENTIAL_MISSING` e exige **Page Public
Content Access**: App Review mais verificação de negócio. Esta casa não a tem.
Declarar a Apify dispensável porque existe no papel uma rota oficial que não
conseguimos chamar é o item 13 do red team — *official API existence vira
permission granted* — a acontecer dentro do nosso próprio validador.

```
FACEBOOK_FETCH_POST_REAL_STATE = nem grátis, nem paga, nem bloqueada.
                                 NÃO DECIDIDA, com as duas portas fechadas.
```

E o `ESTADO = PROVED` das duas rotas Apify de Instagram na matriz
(`apify:comments` e `apify:instagram-scraper`) cita como evidência o mesmo
caminho inexistente `scripts/instagram_janela.py`, que é o ficheiro da **rota
grátis**. Cruzando com o censo de actors:

| rota declarada `PROVED` na matriz | runs registados na história desta casa |
|---|---|
| `apify:comments` (`scrapesmith~instagram-comments-scraper`) | **0** |
| `apify:instagram-scraper` (`apify~instagram-scraper`) | **0** |

    DOIS `PROVED` SEM UM ÚNICO RUN. É o item 11 do red team —
    *actor marketing vira proof* — com a agravante de o `PROVED` ser nosso.

---

## PARTE 22 · DELTA-FIRST — o que a cana já leva, e a palavra que falta

Medido lendo a cadeia inteira, de ponta a ponta:

```
scrap_executor.COLLECT(*, platform, capability, run_id, scope='PONTUAL',
                       banco=None, modo=NORMAL,
                       teto_de_rede=None, teto_de_gasto=None, **kwargs)
   └─ _despachar(..., kwargs)
        └─ social_rotas.executar(platform=, capability=, run_id=, **kwargs)
             └─ _executar(*, ..., country_scope='IT', **kwargs)
                  └─ fn(run_id=, country_scope=, medida=, **kwargs)   ← a rota
```

```
O CANO JÁ TRANSPORTA QUALQUER PARÂMETRO DE JANELA HOJE, SEM UMA LINHA NOVA.
O QUE NÃO EXISTE É O NOME.
```

Varrido o repositório inteiro por `SINCE`, `LAST_SEEN_ID`, `LAST_SEEN_TIME`,
`KNOWN_IDS`, `MAX_ITEMS`:

```
ocorrências em .py ....... 0
```

O único parâmetro de janela que uma rota Meta aceita hoje é `teto` no
`instagram_janela`, e ele significa *limite por conta*, não *desde quando*.

### E a casa já tem as duas primitivas que um delta precisa

Não é preciso inventá-las — é preciso ligá-las.

| primitiva | onde vive | o que responde |
|---|---|---|
| `coleta_checkpoint.conteudo_persistido(banco, platform=, external_ids=)` | já implementada | **quais destes ids JÁ ESTÃO SALVOS** — a resposta canônica de `KNOWN_IDS` |
| `pode_gastar(...)` → `retomar_de` | já implementada | o cursor de retomada da unidade de trabalho |

E a docstring de `conteudo_persistido` já escreveu a lei certa:

> *««VI NA API» NÃO TORNA UM VÍDEO CONHECIDO.»* — se o processo morrer depois de
> ver e antes de salvar, o id não aparece, e a próxima execução reencontra-o.

    O DELTA DESTA CASA JÁ SABE O QUE É «CONHECIDO». O QUE ELE NÃO SABE É
    PEDIR «SÓ O QUE NÃO É».

### O contrato mínimo proposto — declarar, não implementar

Esta missão **não** implementa. O que ela propõe é o vocabulário fechado que
faltava, para que a missão que implementar não invente cinco nomes:

```
SINCE            ISO-8601 UTC. «não me tragas nada publicado antes disto.»
LAST_SEEN_ID     o id externo mais recente que ESTA casa já salvou.
LAST_SEEN_TIME   o carimbo do objeto de LAST_SEEN_ID. Os dois, porque
                 plataforma que pagina por cursor precisa do id e
                 plataforma que pagina por data precisa da data.
KNOWN_IDS        conjunto de ids externos já persistidos. Enchido por
                 `conteudo_persistido`, NUNCA pelo caller à mão.
MAX_ITEMS        teto duro de itens. É de PROTEÇÃO, não de amostragem.
```

Três leis que o contrato precisa carregar, e nenhuma delas é opcional:

1. **`SINCE` é um pedido, não uma garantia.** Plataforma que não sabe filtrar
   por data devolve tudo e o filtro acontece aqui. O trace tem de dizer qual
   dos dois aconteceu — `WINDOW_ENFORCED_BY = SOURCE | LOCAL` — senão
   «5 objetos» não se distingue de «5 objetos novos».
2. **`KNOWN_IDS` vazio não é «nada conhecido».** É indistinguível de «não
   perguntei». O campo `KNOWN_IDS_SOURCE` tem de dizer `DB | CALLER | NOT_ASKED`.
3. **`MAX_ITEMS` atingido é um resultado, não um fim.** Quem para no teto tem de
   devolver `TRUNCATED_BY_MAX_ITEMS` e o cursor onde parou, ou o delta seguinte
   começa no sítio errado e um buraco abre-se em silêncio.

```
ONTEM VIMOS A,B,C. HOJE QUEREMOS D,E — E QUEREMOS SABER SE F EXISTIU E NÃO VEIO.
UM DELTA QUE NÃO SABE DIZER O SEGUNDO É UMA COLETA COMPLETA MAIS BARATA, NÃO UM DELTA.
```

---

## PARTE 23 · ENRICHMENT ON DEMAND — o verbo que não existe

Os verbos públicos do executor, medidos por `grep '^def [A-Z]'`:

```
CAPABILITIES · CHECK · COLLECT · STATE · OUTPUT · TRACE
```

```
ENRICH = NÃO EXISTE. Ocorrências de `ENRICH` em .py: 0.
```

Hoje `COLLECT` é tudo-ou-nada por capacidade: pedir `instagram.reel.transcribe`
corre a cadeia inteira — mídia, ASR, RAW, derivado. Não há forma de pedir a
listagem barata e adiar o caro, a não ser escolhendo outra capacidade.

### A separação que a ferramenta de concorrentes exige

```
LISTAGEM BARATA (sempre)            ENRIQUECIMENTO CARO (só quando pedido)
──────────────────────────          ────────────────────────────────────
id externo                          texto de comentários
texto / legenda                     bytes de vídeo
data de publicação                  transcrição por ASR
URL canónica                        documentos / PDF
tipo de mídia                       detalhe de reações
métricas básicas                    criativo completo do anúncio
```

E a lei que o separa em duas:

```
SCRAP NÃO DECIDE RELEVÂNCIA. QUEM PEDE `ENRICH_ITEM` É O CALLER.
```

O adaptador de Instagram já tem, sem saber, a forma certa disto: a unidade de
trabalho é o **Reel**, e `capture`, `audio` e `transcribe` são três pedidos sobre
a mesma unidade, com o mesmo checkpoint. O segundo pedido leva
`JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES` quando o primeiro concluiu.

    A CASA JÁ SABE NÃO PAGAR DUAS VEZES PELA MESMA UNIDADE. O QUE FALTA É UM
    VERBO QUE PEÇA A SEGUNDA CAMADA SEM REPETIR A PRIMEIRA.

### O que esta missão NÃO propõe

Não propõe `ENRICH` como verbo novo do executor hoje. A razão é medida: o
executor tem 811 linhas e um boundary com sentinelas que leem o corpo de
`COLLECT` para provar a ordem das etapas. Um verbo novo é uma missão própria.

O que fica declarado é o **requisito**: a ferramenta de concorrentes não pode
existir com um `COLLECT` que enriquece tudo. O item 25 do red team —
*enrichment caro roda em todos os itens* — é hoje o comportamento por omissão,
não um risco futuro.

---

## PARTE 24 · LOCAL-FIRST — o que já é lei, e o que ainda se paga

Esta casa já tem a doutrina escrita e implementada:

```
`scrap_capacidades.py`: PROVIDER (com que ferramenta) ≠ EXECUTION_TARGET (onde corre).
A REGRA DO AMBIENTE É UMA SÓ: USAR O MAIS BARATO E MAIS SIMPLES QUE CUMPRA A CAPACIDADE.
```

E `WHY_LOCAL` é obrigatório quando o alvo é `LOCAL` ou `HYBRID`, com vocabulário
fechado. O validador rebenta ao importar se faltar.

| trabalho | onde tem de acontecer | estado nesta casa |
|---|---|---|
| reconhecimento de fala (ASR) | **LOCAL** — `ferramentas/fala_local.py` | **provado**, 4 Reels no disco |
| extração de áudio de MP4 | **LOCAL** — FFmpeg | provado |
| extração de texto de PDF | **LOCAL** — `coleta/pdf_text.py` | provado |
| OCR | LOCAL | `NOT_EXECUTED` |
| keyframes de vídeo | LOCAL | `NOT_EXECUTED` |
| deteção de idioma | LOCAL | existe fora do SCRAP |

```
NÃO PAGAR ACTOR PARA TRANSCREVER, OCR OU EXTRAIR TEXTO DE PDF QUANDO OS BYTES
JÁ ESTÃO NA NOSSA MÃO.
```

Esta casa já pagou a lição em YouTube e registou-a: o artefato pago
`ES-T8-001-youtube-transcripts.raw.json.gz` tem **20 itens, 5 com transcript
vazio** — 25% de falha, paga, contra uma rota local que devolveu texto nos dois
vídeos testados. **Na Meta a mesma lição ainda não foi paga porque a Meta ainda
não foi colhida** — e é isso que torna este momento o barato para escrever a lei.

E o `LOCAL_HARDWARE_STATUS = NOT_MEASURED` continua de pé: `GPU_REQUIRED` é
recusado pelo validador enquanto ninguém medir a máquina. Qualquer plano de
ASR em volume na Meta esbarra aí primeiro.

---
## PARTE 26 · O CONTRATO DE AQUISIÇÃO DA FERRAMENTA «O QUE OS CONCORRENTES ESTÃO FAZENDO»

Esta secção **não constrói Intelligence**. Ela declara o mínimo que o SCRAP tem
de entregar para que outra camada consiga responder as perguntas de negócio —
e declara, com igual força, o que o SCRAP **não** entrega.

### A fronteira, escrita antes do contrato

| o SCRAP entrega | o SCRAP NUNCA entrega |
|---|---|
| «este anúncio apareceu entre A e B» | «é uma campanha de lançamento» |
| «este anúncio deixou de estar activo» | «recuaram» |
| «o texto mudou de X para Y» | «mudaram de posicionamento» |
| «publicaram 14 vezes em 30 dias, antes eram 4» | «estão a atacar» |
| «esta conta apareceu como parceira» | «fecharam contrato com um influenciador» |

```
SCRAP ENTREGA FACTOS OBSERVADOS, COM IDADE E COM PROVENIÊNCIA.
QUALQUER FRASE COM ADJECTIVO É INTELLIGENCE, E NÃO NASCE AQUI.
```

### As onze perguntas, e o que cada uma exige do SCRAP

| pergunta da camada de cima | o facto que o SCRAP tem de entregar | exige delta? | exige enrich? |
|---|---|---|---|
| `NEW_ADS` | conjunto de `ad_archive_id` observados agora e não antes | **sim** | não |
| `REMOVED_ADS` | ids antes observados `ACTIVE` e agora ausentes ou `INACTIVE` | **sim** | não |
| `NEW_POSTS` | ids de post não presentes em `KNOWN_IDS` | **sim** | não |
| `NEW_REELS` | idem, filtrado por tipo de mídia | **sim** | não |
| `NEW_THREADS` | idem, na plataforma Threads | **sim** | não |
| `NEW_PARTNERSHIPS` | par (marca, criador) observado e não antes | **sim** | não |
| `NEW_CREATORS` | identidade de criador nunca vista neste par | **sim** | não |
| `NEW_VIDEO` | id de mídia de vídeo novo | **sim** | não |
| `MESSAGE_TEXT` | o texto tal como publicado, sem resumo | não | não |
| `MEDIA_ASSETS` | endereço, tipo, duração, **e a durabilidade do endereço** | não | **sim** |
| `PUBLIC_METRICS` | o número **e a hora em que ele foi lido** | não | depende |

### `REMOVED_ADS` é a pergunta que quebra um coletor ingénuo

Quatro maneiras de um id sumir, e só uma delas é «o anúncio acabou»:

```
1. o anúncio parou           → facto do mundo
2. a query mudou             → facto nosso
3. a rota falhou             → SOURCE FAILURE != ZERO, lei já escrita nesta casa
4. o teto cortou a página    → TRUNCATED_BY_MAX_ITEMS
```

    UM COLETOR QUE NÃO SEPARA OS QUATRO TRANSFORMA A PRÓPRIA FALHA NUMA
    NOTÍCIA SOBRE O CONCORRENTE. É a forma mais cara de mentir: parece
    inteligência de mercado.

Por isso o contrato exige que **a ausência venha declarada com o motivo**, e
nunca por subtração feita pela camada de cima.

### Os campos que todo objeto Meta tem de carregar

Sobre os 29 campos que o normalizador de comunicação pública já guarda, o
contrato acrescenta os que a família Meta obriga e que hoje não existem:

| campo | por quê |
|---|---|
| `OBSERVATION_TYPE` | `AD` · `ORGANIC` · `BRANDED` · `THREAD` — um anúncio não é um post, e somá-los é o item 22 do red team |
| `AD_ACTIVE_STATUS` + `AD_STATUS_READ_AT` | «activo» sem hora é uma afirmação sobre o presente que envelhece em silêncio |
| `FIELD_SCOPE` | `GLOBAL` · `EU_ONLY` — campo que só existe para anúncio dirigido à UE **não pode** viajar sem esse rótulo (item 2 do red team) |
| `VALUE_KIND` | `EXACT` · `RANGE` · `NOT_AVAILABLE` — impressões e gasto vêm em faixa, e faixa lida como número é mentira com casas decimais |
| `MEDIA_URL_DURABILITY` | `PERMANENT` · `TEMPORARY` · `SIGNED_TTL` · `NÃO SEI` — item 19 do red team |
| `TEXT_KIND` | `CAPTION` (autor) · `TRANSCRIPT_ASR` · `NATIVE_CAPTION` · `OCR` — a casa já tem esta lei; a Meta torna-a obrigatória porque não serve legenda nativa |
| `COMMENTS_DECLARED` vs `COMMENTS_COLLECTED` | já existe no `instagram_janela`; passa a ser contrato |
| `WINDOW_ENFORCED_BY` | `SOURCE` · `LOCAL` — ver PARTE 22 |
| `SNAPSHOT_IS_NOT_CREATIVE` | um `ad_snapshot_url` é um endereço de página, **não** o criativo (item 4 do red team) |

    O CONTRATO NÃO PEDE MAIS DADO. PEDE QUE CADA DADO DIGA O QUE É E DE QUANDO É.

---
## PARTE 25 · CUSTO REAL — dois números, e eles não se substituem

A missão obriga a separá-los, e a separação não é formalidade:

```
CURRENT_ACTOR_PRICE               o que um actor cobra HOJE, com a data em que se leu
SINTONIA_HISTORICAL_ACTUAL_COST   o que ESTA casa REALMENTE pagou, lido do artefato
```

### O que esta casa realmente pagou pela Meta

```
runs pagos de Meta na história desta casa ............. 1
itens comprados ....................................... 60
itens normalizados .................................... 0
custo registado ....................................... NOT_PRESERVED
SINTONIA_HISTORICAL_ACTUAL_COST (META) ................ NOT_PRESERVED
```

Pela `COL-LAW-019`, `NOT_PRESERVED` é **confissão**: gastou e não guardou. Não é
`0` e não é `NÃO SEI`. E como não há denominador real:

```
NENHUMA PERCENTAGEM DE POUPANÇA PODE SER CALCULADA PARA A META.
Poupança percentual sobre um denominador `NOT_PRESERVED` é aritmética sobre
uma confissão.
```

O preço de referência desta casa — **US$ 1,863 por 1 000 itens**, medido sobre
84 runs pagos reais — é **de YouTube e LinkedIn**. Aplicá-lo à Meta seria
importar um denominador de outra plataforma.

    O NÚMERO DA CASA EXISTE. ELE NÃO É DA META.

### Os actors de Meta que o código cita, e o que eles custaram

| actor citado | versão fixada no código | runs registados | custo registado |
|---|---|---|---|
| `apify~instagram-scraper` | `0.0.776` | **0** | — |
| `apify~instagram-profile-scraper` | `0.0.601` | **0** | — |
| `apify~instagram-reel-scraper` | `0.0.563` | **0** | — |
| `scrapesmith~instagram-comments-scraper` | `0.0.164` | **0** | — |
| `apify~facebook-posts-scraper` | — | **0** | — |
| `apify/instagram-hashtag-scraper` | `NOT_PRESERVED` | **1** | `NOT_PRESERVED` |
| *qualquer actor de Threads* | — | **0** | nenhum citado |
| *qualquer actor de Ad Library* | — | **0** | **nenhum citado** |

```
OS CINCO ACTORS DE META QUE O CÓDIGO CITA NUNCA CORRERAM.
O ÚNICO QUE CORREU NÃO É CITADO POR NENHUM FICHEIRO DO REPOSITÓRIO.
```

Consequência directa, e ela poupa uma conversa inteira:

    NENHUM ACTOR DE META PODE SER «APOSENTADO COM ECONOMIA». Aposentá-los é
    higiene de código. A poupança de Meta nesta casa é, hoje, exactamente
    zero dólares — porque o gasto de Meta nesta casa é, hoje, um run de custo
    desconhecido.

E isto reposiciona a missão inteira:

```
ESTA NÃO É UMA MISSÃO PARA CORTAR CUSTO DE META. É UMA MISSÃO PARA NÃO O
CRIAR. A casa está no único momento em que a escada oficial-primeiro custa
zero para adoptar: antes da primeira coleta.
```

---
## PARTE 8 · BRANDED CONTENT — o achado que inverte a hipótese

A hipótese não vinculante do briefing punha Branded Content no P0 «se existir».
**Existe, e é API pública.**

```
BRANDED_CONTENT_API_AVAILABLE = YES
```

`GET /branded_content_search`, nó do Graph API.
📍 <https://developers.facebook.com/docs/graph-api/reference/branded_content_search/>

> *«returns branded content based on your search. By default we only return
> content that is currently available on Facebook or Instagram, and content
> that was created on or after August 17, 2023.»*

E o Transparency Center confirma que ele pertence à família de acesso da
Ad Library:

> *«Authorized users can also analyze active and public branded content running
> on Facebook and Instagram via the API.»*
> — <https://transparency.meta.com/researchtools/ad-library-tools/>

### A frase que decide tudo

| parâmetro | descrição oficial | obrigatório |
|---|---|---|
| `creation_date_min` | "Search for branded content posted before the date (inclusive) you provide." | **sim** |
| `creation_date_max` | "Search for branded content posted after the date (inclusive) you provide." | **sim** |
| `ig_username` | "Search for an Instagram account that posted branded content **or was a brand partner**." | um dos dois |
| `page_url` | "Search for a Facebook Page that posted branded content **or was a brand partner**." | um dos dois |

```
«OR WAS A BRAND PARTNER» É A FRASE QUE TRANSFORMA UM ENDPOINT DE AUTOCONSULTA
NUMA FERRAMENTA DE DESCOBERTA DE CONCORRENTE.
```

Passa-se o `ig_username` ou o `page_url` da marca rival, e volta a lista de
criadores que ela pagou.

### O que volta, e o que não volta

| campo devolvido | tipo |
|---|---|
| `creation_date` | data UTC da publicação |
| `creator` | `{id, name, url}` — quem publicou |
| `partners` | lista de `{id, name, url}` — quem pagou |
| `type` | Facebook post · Instagram post · Instagram story · Instagram reel |
| `url` | link para o post vivo |

**E o que ele NÃO devolve — e a ausência é metade do achado:**

```
sem legenda · sem mídia · sem país · sem métricas · sem spend
sem marcador de campanha · sem nada anterior a 2023-08-17
sem nada já apagado · sem Threads
```

### As duas cercas do histórico, e elas são de naturezas diferentes

```
PISO   fixo, declarado:   "created on or after August 17, 2023"
TETO   vivo, declarado:   "only ... content that is currently available"
```

```
ISTO NÃO É UM ARQUIVO. É UM ESPELHO DO QUE ESTÁ NO AR.
```

Consequência dura e directa para a ferramenta de concorrentes: um Story
patrocinado expira em 24 h, portanto **é praticamente invisível
retroactivamente**. Quem quiser a parceria em Story tem de ver hoje o que foi
publicado hoje. É delta obrigatório, não delta opcional.

    O ITEM 5 DO RED TEAM — *branded content vira organic census* — morre aqui
    pela raiz: este índice só conhece o que traz o rótulo de parceria paga, e
    conteúdo orgânico não aparece nele de todo. Somar os dois dá um número que
    não é nem um nem outro.

### Respostas do formulário da PARTE 8

```
API_AVAILABLE            = YES  · GET /branded_content_search
UI_ONLY                  = NO   · há UI (facebook.com/ads/library/branded_content/) E API
SEARCHABLE_BY_BUSINESS   = YES  · ig_username | page_url no papel «brand partner»
SEARCHABLE_BY_CREATOR    = YES  · o mesmo parâmetro, no papel «posted»
HISTORY                  = piso 2023-08-17 · teto «currently available»
EXPORT                   = API: JSON paginado (data + paging). UI: NÃO DOCUMENTADO
AUTH                     = NÃO DOCUMENTADO na página do nó — ver PROBE_2
COVERS                   = FB post · IG post · IG story · IG reel · (Live: NÃO DOCUMENTADO)
NÃO COBRE                = THREADS
```

`AUTH = NÃO DOCUMENTADO` é a resposta honesta, e é uma pergunta de probe, não de
opinião. A página do nó não lista token nem permissão. O contexto da Ad Library
sugere confirmação de identidade mais token com `ads_read`, mas **sugerir não é
documentar**, e esta casa não escreve permissão que não leu.

### E o que a Meta reserva, com todas as letras

A Creator Discovery API parece ser a mesma coisa e não é. A própria doc fecha a
porta:

> *«Non-Branded Content data is shared with all agencies/brands; Branded Content
> data is shared only with the sponsor Brand.»*
> — <https://developers.facebook.com/docs/fb-creator-discovery/>

```
GRAFO DE PARCERIA: PÚBLICO.   DESEMPENHO DA PARCERIA: SÓ DE QUEM PAGOU.
```

---

## PARTE 18 · THREADS — a melhor rota oficial da família, e a porta que a tranca

### As doze permissões, e as doze exigem App Review

Fonte: <https://developers.facebook.com/docs/permissions>

`threads_basic` · `threads_business_basic` · `threads_content_publish` ·
`threads_delete` · `threads_keyword_search` · `threads_location_tagging` ·
`threads_manage_insights` · `threads_manage_mentions` · `threads_manage_replies` ·
**`threads_profile_discovery`** · `threads_read_replies` · `threads_share_to_instagram`

```
APP_REVIEW_REQUIRED = YES, nas doze. Sem excepção.
```

E `threads_profile_discovery` é a permissão que a matriz desta casa **não
conhecia**: *«allows an app to access profiles for public Threads accounts and
public posts of these accounts»*.

### O que o modo de desenvolvimento entrega, medido pela própria doc

Sem App Review a API inteira roda — e devolve quatro contas:

> *«With standard access, only some of the official Meta accounts can be looked
> up. These include @meta, @threads, @instagram, and @facebook.»*
> — <https://developers.facebook.com/documentation/threads/threads-profiles>

> *«If your app has not been approved for the `threads_keyword_search`
> permission, the search will be performed only on posts owned by the
> authenticated user.»*
> — <https://developers.facebook.com/docs/threads/keyword-search/>

```
O SANDBOX SEM REVIEW É UMA MAQUETE. Prova que o código funciona e não entrega
um único dado de concorrente.
```

    ITEM 16 DO RED TEAM — *development-mode app é tratado como production* —
    tem aqui a sua prova documental mais limpa da missão inteira.

### As TRÊS portas para concorrente, e só três

| # | endpoint | permissão | entrega | não entrega |
|---|---|---|---|---|
| **1** | `GET /profile_posts?username=…` | `threads_profile_discovery` | feed público paginado do concorrente, campos completos | `owner`; perfis <100 seguidores; perfis privados |
| **2** | `GET /profile_lookup?username=…` | `threads_profile_discovery` | bio, nome, foto, `follower_count`, `is_verified`, e likes/quotes/reposts/views **dos últimos 7 dias** | métrica por post; histórico >7 dias |
| **3** | `GET /keyword_search?q=…` | `threads_keyword_search` | busca no corpus público **desde 2023-07-05**, filtrável por `author_username`, `media_type`, `since`/`until`, `TOP`/`RECENT` | `owner` (excluído por doc); keywords «sensitive or offensive» devolvem array vazio |

E a porta lateral: webhook `mentions` traz conteúdo público de terceiro — **mas
só o que menciona a nossa conta**. Serve reputação, não vigilância.

### Os números, documentados

```
SEARCH_PUBLIC   = YES, só com threads_keyword_search aprovada
MAX_RESULTS     = limit default 25 · MÁXIMO 100
PAGINATION      = cursor-based (before/after no objeto `paging`)
JANELA          = since >= 1688540400 (2023-07-05, o dia zero do Threads)
RATE_LIMIT      = keyword_search 2 200 queries / 24 h rolantes, POR UTILIZADOR
                  profile_lookup + profile_posts 1 000 requests / 24 h
                  tecto global «Calls within 24 hours = 4800 × Number of Impressions»
                  (mínimo 10 impressões → piso de ~48 000 chamadas/24 h)
COST            = NÃO DOCUMENTADO. Não há página de preço. Ausência de preço
                  não é gratuidade contratual escrita.
```

E a armadilha de janela que esta missão quase engoliu:

```
A JANELA DE 7 DIAS EXISTE — MAS NO `profile_lookup`, NAS MÉTRICAS DE PERFIL.
O `keyword_search` NÃO TEM JANELA DE 7 DIAS: ele busca desde o dia zero.
Trocar as duas é confundir «métrica recente» com «conteúdo recente».
```

### O que NÃO existe para concorrente no Threads

| não existe | evidência |
|---|---|
| insights/métrica **por post** de terceiro | insights são do próprio; `REPOST_FACADE` devolve array vazio «because they are posts made by other users» |
| enumerar as **replies do post** de um terceiro | `threads_read_replies` = «read replies to **a user's** thread»; a doc de moderação é toda sobre «users' own Threads» → **NÃO DOCUMENTADO** |
| perfil com **menos de 100 seguidores** | «Only returns public profiles with at least 100 followers.» |
| lista de **seguidores/seguindo** de terceiro | **NÃO DOCUMENTADO** — não há endpoint |

```
COMMENTS (Threads, terceiro) = NÃO DOCUMENTADO — e NÃO DOCUMENTADO não é NÃO.
É uma pergunta de probe, e está na PARTE 30 como PROBE_5.
```

    ITEM 18 DO RED TEAM — *Threads own-account route vira public competitor
    route* — é o erro mais fácil desta plataforma, porque os endpoints da conta
    própria e os de descoberta partilham a mesma raiz e o mesmo `threads_basic`.
    A separação acima existe para que ninguém os some.

### `media_url` do Threads

```
PUBLIC   = a doc diz só «The post's media URL.»
SIGNED   = NÃO DOCUMENTADO
TTL      = NÃO DOCUMENTADO
```

A documentação **não contém uma única frase** sobre expiração, assinatura ou
refresh de `media_url`. O único TTL que a Meta documenta no Threads é outro: o
container de publicação não publicado, que expira em 24 h.

    ITEM 19 DO RED TEAM — *signed media URL vira permanent* — resolve-se aqui
    pela regra inversa: na ausência de documentação, **tratar como efémero por
    omissão** e ancorar no `permalink`, que a doc declara permanente.

---
## PARTE 19 · CENSO DOS ACTORS APIFY DA META

```
LIDO_EM = 2026-09-12 · NENHUM ACTOR FOI CORRIDO · ZERO DÓLARES
```

A missão pedia no mínimo 15 Instagram, 10 Facebook, 5 Ad Library e 5 Threads.
Foram revistos **47**:

| família | revistos | mínimo pedido |
|---|---|---|
| Instagram | **18** | 15 |
| Facebook | **15** | 10 |
| Ad Library | **7** | 5 |
| Threads / misc | **8** | 5 |

### O achado de método, e ele invalida uma coluna inteira

A data `UPDATED` dos actors oficiais **não mede alteração de código**. Lido pela
API pública da Apify, o campo `modifiedAt` de **todos** os actors `apify/*` de
Instagram devolveu carimbos dentro do mesmo segundo —
`2026-09-11T14:41:08.x` — e os de Facebook, `2026-09-12T03:22:04.x`.

```
SEIS ACTORS COM O MESMO CARIMBO AO MILISSEGUNDO NÃO SÃO SEIS ACTUALIZAÇÕES.
SÃO UM TOQUE DE METADADOS EM LOTE.
```

E há contradição directa entre o que o actor diz de si e o que a plataforma
regista: `curious_coder/facebook-post-scraper` imprime *«Last updated: March
2025»* no README enquanto a plataforma devolve `modifiedAt = 2026-08-22`.

    `UPDATED` DE ACTOR OFICIAL = NÃO SEI. Actors de comunidade têm datas
    dispersas e informativas; os oficiais, não.

### MECANISMO — 7 declaram, ~36 são caixa preta

A missão proíbe adivinhar caixa preta. Cumprido: só classifiquei quem declarou.

| actor | mecanismo declarado | citação |
|---|---|---|
| `memo23/facebook-public-group-posts-scraper` | **INTERNAL_ENDPOINT** (GraphQL, sem navegador) | *«extracting data directly from Facebook's GraphQL API»* · *«directly queries Facebook's backend GraphQL APIs using CheerioCrawler»* |
| `automly/facebook-ad-library-scraper` | **INTERNAL_ENDPOINT** (GraphQL por HTTP) | *«direct HTTP + GraphQL, no headless browser»* |
| `webdatalabs/meta-ad-library-scraper` | **INTERNAL_ENDPOINT** (interceção) | *«uses GraphQL interception to capture the actual API responses»* |
| `whoareyouanas/meta-ad-scraper` | **BROWSER** | *«Puppeteer with stealth plugin»* · *«Scroll-based pagination»* |
| `automation-lab/threads-scraper` | **BROWSER** a capturar respostas de API | *«headless browser … captures the API responses»* · *«uses residential proxy rotation»* |
| `logical_scrapers/threads-post-scraper` | **EMBEDDED_JSON** | *«parses hidden JSON data directly from the post page»* |
| `watcher.data/search-threads-by-keywords` | **INTERNAL_ENDPOINT** nomeado | *«uses the `/threads/search/posts` endpoint»* |

**E o que isto significa para esta casa, que é o que interessa:**

```
DOS 7 QUE DECLARAM, 4 DECLARAM ENDPOINT INTERNO E 2 DECLARAM NAVEGADOR COM
STEALTH E ROTAÇÃO DE PROXY RESIDENCIAL.
```

Esta casa já escreveu a lei contra endpoint interno, em `coleta/story_local.py`:
*«Endereço interno muda sem aviso e sem versão»* e **«NÃO PEDIR NADA QUE A
PÁGINA JÁ NÃO FOSSE PEDIR.»** E `stealth` mais `residential proxy rotation` são
exactamente duas das coisas que esta missão declarou NÃO autorizadas.

    COMPRAR O RESULTADO DE UMA TÉCNICA QUE NÃO PODEMOS USAR NÃO TORNA A
    TÉCNICA PERMITIDA. TORNA-A TERCEIRIZADA.
    Isto é uma pergunta para gente, não para código, e fica declarada — não
    resolvida — nesta missão.

### Os ~36 restantes, e os 20 oficiais estão todos lá

Nenhum dos **20 actors `apify/*`** da família Meta declara mecanismo. A frase que
aparece nas páginas deles — *«Actors are web data automations that power AI and
operations…»* — é **boilerplate de plataforma**, idêntica em actors não
relacionados, e não é declaração de nada.

E dois deles chamam-se «API Scraper» e não dizem que API:
`apify/instagram-api-scraper` e `apify/threads-profile-api-scraper`.

```
A PALAVRA «API» NO NOME DE UM ACTOR TEM PESO PROBATÓRIO ZERO.
```

### Os cinco actors que ESTE repositório cita, com preço lido hoje

| actor citado no código | versão fixada | preço lido 2026-09-12 | runs nesta casa |
|---|---|---|---|
| `apify~instagram-scraper` | `0.0.776` | desde **$1,50 / 1 000** (Business) · **$2,70 / 1 000** (Free) | **0** |
| `apify~instagram-profile-scraper` | `0.0.601` | desde **$1,60 / 1 000 perfis** · Free **$2,60** | **0** |
| `apify~instagram-reel-scraper` | `0.0.563` | desde **$1,00 / 1 000 reels** | **0** |
| `scrapesmith~instagram-comments-scraper` | `0.0.164` | **NÃO ENCONTRADO no store hoje** | **0** |
| `apify~facebook-posts-scraper` | — | desde **$2,00 / 1 000 posts** | **0** |
| `apify/instagram-hashtag-scraper` *(o órfão que correu)* | `NOT_PRESERVED` | desde **$1,90 / 1 000** · Free **$2,60** | **1** |

`scrapesmith~instagram-comments-scraper` não apareceu no censo do store. Isso
**não prova** que desapareceu — prova que não foi encontrado na varredura de
hoje. Fica `NÃO SEI`, e é a rota que a matriz declara `PROVED` para
`INSTAGRAM/FETCH_COMMENTS`.

    A ÚNICA LINHA DA META QUE A MATRIZ DIZ PRECISAR DE APIFY APONTA PARA UM
    ACTOR QUE NUNCA CORREU AQUI E QUE HOJE NÃO FOI ENCONTRADO NO STORE.

### O que o censo confirmou do lado de fora, e que esta casa já tinha medido

```
apify/instagram-profile-scraper  →  DEPTH declarada: «Latest 12 posts», «Latest 12 IGTV videos»
```

**Doze.** O mesmo número que `instagram_janela.py` mediu na rota grátis e
gravou como lei: *«12 itens é o TETO DA ROTA DESLOGADA, medido em duas contas.»*

```
UM ACTOR PAGO DECLARA O MESMO TECTO QUE A NOSSA ROTA GRÁTIS MEDIU.
ISSO EMPURRA O 12 PARA O LADO DA PLATAFORMA, NÃO PARA O LADO DA NOSSA ROTA.
```

Não é prova — é convergência de duas fontes independentes, uma medida e uma
declarada. E é a evidência mais forte desta missão sobre a PARTE 10.

Outros tectos declarados que valem registo:

| actor | tecto declarado |
|---|---|
| `apify/instagram-search-scraper` | **250** resultados por termo de busca |
| `apify/instagram-scraper` | plano Free: **~15 comentários por post**, uma página |
| `apify/instagram-comment-scraper` | recusa dar número: *«There's no one-size-fits-all number»* |
| `webdatalabs/meta-ad-library-scraper` | **«Only current ads visible.»** |
| `curious_coder/facebook-ads-library-scraper` | *«past seven years»* — e isso é política da Meta para anúncios políticos, não capacidade do actor |
| `automation-lab/threads-scraper` | **200** posts por username ou busca |
| `futurizerush/threads-replies-scraper` | **50** replies por post, **20** URLs por run |

### A armadilha do comentário, do lado de fora também

Seis actors anunciam «comments» e devolvem só `commentsCount`:
`apidojo/instagram-scraper`, `apidojo/instagram-scraper-api`,
`cleansyntax/facebook-profile-posts-scraper`, `scrapeforge/facebook-search-posts`,
`scraper_one/facebook-posts-search`, `apify/instagram-profile-scraper`.

```
O ITEM 7 DO RED TEAM NÃO É UM RISCO TEÓRICO. É UM PADRÃO DE MERCADO.
```

E há um limite **estrutural**, não de actor:

```
NENHUM ACTOR DE AD LIBRARY DEVOLVE COMENTÁRIOS OU REACÇÕES. Nenhum dos sete.
Não é falha deles — a superfície da Ad Library não os tem.
```

### Preço, cookies e modelo

```
MODELO         todos os ~47 são PAY_PER_EVENT hoje. Zero rentals mensais.
DISPERSÃO      ~57× entre extremos comparáveis:
               Ad Library  $0,55 (automly)  ·  $17,00 (webdatalabs) / 1 000
               Instagram   $0,47 (apidojo)  ·  $2,70 (apify, Free) / 1 000
COOKIES        apenas 3 actors aceitam credencial, todos de comunidade, todos
               opcional. NENHUM actor `apify/*` aceita cookie ou credencial.
               O input schema do `apify/instagram-scraper` foi conferido campo
               a campo: 8 campos, zero de autenticação.
OPEN_SOURCE    nenhum dos 47 liga repositório. UM declara licença Apache-2.0
               sem dar URL. `OPEN_SOURCE = NÃO SEI` para os 47.
DEPRECATED     o campo `notice` da API do store é `NONE` nos 47.
```

    O PREÇO NÃO ACOMPANHA A LEGIBILIDADE. O mais barato da Ad Library declara
    mecanismo; o mais caro, 30× acima, declara o mesmo mecanismo.

---
## PARTE 3 · META AD LIBRARY — a frase que decide a missão inteira

```
LIDO_EM = 2026-09-12 · FONTE PRIMÁRIA · NENHUMA CHAMADA FEITA
```

A página oficial da Ad Library API responde `403` a leitor automatizado. O texto
foi lido da captura do Internet Archive da **mesma URL**
(`web.archive.org/…/20251005162159/…/ads/library/api`, capturada 2025-10-05) e
**corroborado campo a campo** contra a referência viva do Graph API lida hoje.
Onde as duas divergem, a viva ganha e a divergência está registada.

### A frase de escopo, e ela vale por metade do relatório

> *«The Ad Library API helps you perform customized searches of the Ad Library
> for: **Ads about social issues, election or politics that were delivered
> anywhere in the world during the past 7 years** — **Ads of any type that were
> delivered to the United Kingdom (UK) or European Union during the past
> year**»*
> — <https://www.facebook.com/ads/library/api/>

E o reforço ao nível do parâmetro, na referência viva:

> *«Note: **Ads that did not reach any location in the EU will only return if
> they are about social issues, elections or politics.**»*
> — <https://developers.facebook.com/docs/graph-api/reference/ads_archive/>

```
DOIS CORPUS, DUAS JANELAS, E ELES NÃO SE MISTURAM:

  POLÍTICO      mundo inteiro       7 anos
  COMERCIAL     só UE (e UK)        1 ANO a contar da última impressão
```

    ITEM 3 DO RED TEAM — *current ad vira historical ad* — resolve-se aqui com
    um número: para anúncio comercial italiano a história é **um ano**, não
    sete. Quem escrever «sete anos» num relatório de concorrência comercial
    está a citar a janela do outro corpus.

### E a Itália é exactamente onde isto funciona

```
ad_reached_countries = ['IT']     VÁLIDO — IT está no enum
```

A Itália é membro da UE, portanto **anúncio comercial que entregou em Itália é
retornável pela API**. É a única geografia onde a Meta expõe anúncio não-político
de forma programática — e é a geografia desta casa.

```
A ÚNICA ROTA OFICIAL, GRATUITA E DESENHADA PARA VER ANÚNCIO DE CONCORRENTE
FUNCIONA PRECISAMENTE NO MERCADO DO SINTONIA EAME. E ESTA CASA NÃO A TEM.
```

### A ruptura de 2025 que fecha o corpus político europeu

> *«As of today, political, electoral and social issue adverts are no longer
> able to be delivered in the EU»*
> — <https://about.fb.com/news/2025/07/ending-political-electoral-and-social-issue-advertising-in-the-eu/>

Consequência para esta casa: o corpus político da UE é um **conjunto histórico
fechado**. Não cresce. Para agroquímica isso é quase irrelevante — mas explica
por que os campos de dinheiro nunca aparecerão em Itália (ver PARTE 6).

---

## PARTE 4 · ANÚNCIOS ACTIVOS — o formulário respondido

```
API_CAN_QUERY_BY_PAGE_ID  = SIM — `search_page_ids`, «up to ten IDs, separated by commas»
API_CAN_QUERY_BY_ADVERTISER = SIM — `search_terms`, texto livre, MÁXIMO 100 CARACTERES
                              e «we do not translate your keyword searches»
                              → para Itália, consultar EM ITALIANO
ACTIVE_ONLY               = NÃO. `ad_active_status ∈ {ACTIVE, INACTIVE, ALL}`,
                              **DEFAULT = ACTIVE** — e o default molda o
                              resultado em silêncio
HISTORY                   = comercial UE: 1 ano da última impressão
                              político mundial: 7 anos
MAX_DEPTH                 = NÃO DOCUMENTADO. Não há tecto de resultados publicado
PAGINATION                = por CURSOR. `paging.cursors.before/after` + `next`
                              `limit` NÃO está na tabela de parâmetros, mas a
                              URL `next` do exemplo oficial traz `&limit=25`
COST                      = ZERO DÓLARES. Não há tier pago documentado
AUTH_REQUIRED             = SIM, e é a parte cara: ver abaixo
```

### O parâmetro obrigatório, e é só um

```
ad_reached_countries      REQUIRED — «This parameter is required.»
```

Tudo o resto é opcional. E dois opcionais têm default que decide o resultado:
`ad_type` default `ALL`, `ad_active_status` default `ACTIVE`.

    UM DEFAULT QUE MOLDA O CORPUS É UMA DECISÃO. Um coletor que não o declara
    no trace não sabe dizer se «zero anúncios» significa zero ou significa
    «só perguntei pelos activos».

### AUTH — o custo real não é dinheiro, é identidade

> *«To get authorized to use the API, you'll need a Facebook account.»*
> *«**Step 1: Confirm your identity and location** Go to Facebook.com/ID and
> follow the confirmation process required to run ads about social issues,
> elections or politics. It can take a few days…»*

```
NÃO HÁ CAMINHO COMERCIAL SEM CONFIRMAÇÃO DE IDENTIDADE. A Meta reutiliza o
mesmo controlo de identidade do anunciante político como porta de entrada da
API inteira, e não declara isenção para consulta comercial.
```

O que **não** está documentado, e por isso fica `NÃO SEI`:

```
tipo de documento exigido ........... NÃO DOCUMENTADO
prazo real de confirmação ........... «a few days», sem SLA
países onde a confirmação existe .... NÃO DOCUMENTADO (a FAQ «Where is the API
                                       available?» existe e a resposta é
                                       carregada por JavaScript; ausente do HTML)
scope/permissão do token ............ NÃO DOCUMENTADO — a referência não lista
                                       bloco de permissões para `ads_archive`
```

    TERCEIROS AFIRMAM `ads_read` E `ads_archive` COMO SCOPES. A documentação da
    Meta não lista permissão nenhuma para este nó. Escrever `ads_read` na nossa
    matriz seria copiar um blogue e chamar-lhe lei.

### RATE LIMIT

```
erro 613 «Calls to this api have exceeded the rate limit.» ESTÁ documentado.
O NÚMERO NÃO ESTÁ.
```

A doc genérica de rate limiting manda consultar «the supporting docs for the
specific API you are calling» — e essas docs não trazem número nenhum. É um beco
sem saída na documentação da própria Meta. O «200 chamadas/hora» que circula em
blogues é a fórmula genérica da plataforma mal aplicada.

```
AD_LIBRARY_RATE_LIMIT = NÃO SEI, e é uma pergunta de probe (PROBE_3).
```

---

## PARTE 5 · HISTÓRICO — os quatro números, separados

```
COMMERCIAL_AD_HISTORY (fora da UE) = NENHUMA pela API. O anúncio comercial
                                      não-UE não volta de todo.
COMMERCIAL_AD_HISTORY (UE/Itália)  = 1 ANO a contar da última impressão
POLITICAL_AD_HISTORY (mundo)       = 7 ANOS
EU_HISTORY (político)              = mesmo arquivo de 7 anos, mas SEM INVENTÁRIO
                                      NOVO desde 2025-10-06
CURRENT_ADS                        = `ad_active_status=ACTIVE` (o default)
```

Base legal do um ano, declarada pela própria Meta:

> *«These ads will be **stored in our public Ad Library for a year**, so anyone,
> anywhere, can better understand every ad that's run in the EU.»*
> — <https://about.fb.com/news/2023/08/new-features-and-additional-transparency-measures-as-the-digital-services-act-comes-into-effect/>

### A consequência de desenho, e ela é dura

```
NÃO HÁ CATÁLOGO ANTIGO A RECUPERAR. Um ano é uma janela rolante: o que não for
colhido enquanto está lá, desaparece e não volta.
```

    QUALQUER DESENHO LONGITUDINAL DE ANÚNCIO COMERCIAL NA META TEM DE SER
    COLHEITA ROLANTE, NUNCA CONSULTA RETROSPECTIVA. Isto transforma o delta
    da PARTE 22 de optimização em **requisito de existência**.

### UI ≠ API — o item 1 do red team, com os dois lados medidos

| a UI tem, e a API não | a API tem, e a UI não |
|---|---|
| **anúncio comercial activo no mundo inteiro** — a API não devolve nenhum fora da UE/UK | **28 campos estruturados e tipados**, legíveis por máquina |
| o **criativo renderizado** — imagem, vídeo, carrossel, botão | **`search_page_ids`** — até 10 páginas por consulta |
| a biblioteca de **Branded Content** | **`search_type=KEYWORD_EXACT_PHRASE`** e multi-frase por vírgula |
| **sem confirmação de identidade, sem app, sem token** | `ad_delivery_date_min/max`, `languages`, `media_type`, `publisher_platforms` |
| | **`unmask_removed_content`** — conteúdo removido por violação de normas |
| | paginação por cursor, para varrimento sistemático |

```
A ASSIMETRIA MAIOR: UM ANÚNCIO COMERCIAL BRASILEIRO OU AMERICANO ESTÁ NA UI E
É INALCANÇÁVEL PELA API. Para a Itália, o inverso: a API é estritamente
superior.
```

---

## PARTE 6 · CRIATIVOS E CAMPOS — o que volta, campo a campo

Fonte: <https://developers.facebook.com/docs/graph-api/reference/archived-ad/>

### Existem 28 campos. Só quatro são default.

```
DEFAULT (sem pedir `fields`): ad_delivery_start_time · ad_delivery_stop_time
                              ad_snapshot_url · page_id
```

### Para anúncio COMERCIAL italiano — o que volta

| campo | `AVAILABLE` | `EU_ONLY` | `EXACT_OR_RANGE` |
|---|---|---|---|
| `id` *(a Library ID)* | SIM | não | exacto |
| `page_id` | SIM (default) | não | exacto |
| `page_name` | SIM | não | exacto |
| `ad_creative_bodies` | SIM | não | texto exacto, **lista** |
| `ad_creative_link_titles` | SIM | não | texto exacto, lista |
| `ad_creative_link_descriptions` | SIM | não | texto exacto, lista |
| `ad_creative_link_captions` | SIM | não | texto exacto, lista |
| `ad_snapshot_url` | SIM (default) | não | URL |
| `ad_delivery_start_time` | SIM (default) | não | timestamp UTC exacto |
| `ad_delivery_stop_time` | SIM (default) | não | timestamp UTC, **pode vir vazio** |
| `ad_creation_time` | SIM | não | exacto — **e não é a hora em que correu** |
| `publisher_platforms` | SIM | não | enum: FACEBOOK · INSTAGRAM · AUDIENCE_NETWORK · MESSENGER · WHATSAPP · OCULUS · **THREADS** · STREAMING_SERVICES |
| `languages` | SIM | não | ISO 639-1, lista |
| **`eu_total_reach`** | **SIM** | **SIM** | **inteiro estimado — NÃO é faixa** |
| **`beneficiary_payers`** | **SIM** | **SIM** | estruturado: `beneficiary` · `payer` · `current` |
| `total_reach_by_location` | SIM | UE · BR · UK | inteiro por localização |
| **`target_ages`** | **SIM** | UK+UE | limites exactos, 13 → 65+ |
| **`target_gender`** | **SIM** | UK+UE | enum: Women · Men · All |
| **`target_locations`** | **SIM** | UK+UE | estruturado, com `excluded` e `num_obfuscated` |
| **`age_country_gender_reach_breakdown`** | **SIM** | UK+UE | **contagens inteiras exactas** por país × faixa etária × género |

### Para anúncio COMERCIAL italiano — o que NUNCA volta

| campo | por quê |
|---|---|
| `impressions` | *«Available only for POLITICAL_AND_ISSUE_ADS»* — e é **FAIXA**, nunca número |
| `spend` | idem — **FAIXA** |
| `currency` | idem |
| `estimated_audience_size` | idem — **FAIXA** |
| `demographic_distribution` | idem — **percentagens** |
| `delivery_by_region` | idem — **percentagens** |
| `bylines` | idem |
| `br_total_reach` | só político do Brasil |

```
OS DOIS EIXOS DE EXCLUSIVIDADE SÃO DIFERENTES, E CONFUNDI-LOS É O ITEM 2
DO RED TEAM:

  DINHEIRO E IMPRESSÕES   →  SÓ POLÍTICO, no mundo inteiro, SEMPRE EM FAIXA
  SEGMENTAÇÃO E ALCANCE   →  SÓ UE/UK, para QUALQUER tipo, em NÚMERO EXACTO

E NÃO HÁ CAMPO NENHUM QUE DÊ GASTO COMERCIAL. EM LADO NENHUM.
A Meta nunca publica gasto comercial.
```

    ESTIMAR ORÇAMENTO DE CONCORRENTE ITALIANO A PARTIR DA AD LIBRARY NÃO É UM
    PROBLEMA DIFÍCIL. É UM PROBLEMA QUE A API NÃO TEM FORMA DE RESOLVER.
    Como o político deixou de correr na UE em 2025-10, estes sete campos estão
    **permanentemente vazios** para qualquer dado novo de Itália.

### E o nome do campo que quase todo o mundo escreve errado

```
NÃO EXISTE CAMPO `ad_archive_id` NO NÓ DOCUMENTADO.
O nome canónico é `id` — «The Library ID of the ad object.»
```

`ad_archive_id` é o nome do **endpoint interno não documentado** que a UI chama,
e é o que as bibliotecas de scraping usam. Pôr `ad_archive_id` no nosso esquema
seria carimbar, no nosso próprio contrato, o nome de uma rota que não é a
oficial.

---

## PARTE 7 · CRIATIVO REAL E VÍDEO DE ANÚNCIO

### A pergunta principal da PARTE 6 do briefing, respondida

> «É possível preservar o criativo real sem screenshot/browser?»

```
TEXTO   SIM, e integralmente: bodies, titles, descriptions, captions —
        por CARTÃO de carrossel, porque os quatro campos são LISTAS
IMAGEM  NÃO
VÍDEO   NÃO
CARROSSEL (imagens)  NÃO — o texto vem por cartão, a imagem nunca
```

A API devolve **uma única afordância de mídia**, e é um endereço de renderização:

> *«`ad_snapshot_url` — String with URL link which displays the archived ad.
> **This displays uncompressed images and videos from the ad.** While you
> **cannot currently download a batch of archived ads**, you can download ad
> creative such as images and text for an individual ad. If you do so, it must
> be for analysis and you must comply with the data storage terms in our Terms
> of Service.»*

E a forma real do valor, do exemplo oficial:

```
https://www.facebook.com/ads/archive/render_ad/?id=123&access_token=<ACCESS_TOKEN>
```

```
`ad_snapshot_url` É UM ENDPOINT DE RENDERIZAÇÃO, NÃO UM ENDPOINT DE DADOS.
E TRAZ O TOKEN EMBUTIDO NA QUERY STRING.
```

    ITEM 4 DO RED TEAM — *ad snapshot vira raw creative* — morre na citação:
    o snapshot é a página que desenha o anúncio, não os bytes dele. E o campo
    `SNAPSHOT_IS_NOT_CREATIVE` do contrato da PARTE 26 existe por causa desta
    linha.

E há um aviso de segurança que ninguém pediu e que é desta casa fazer:

```
UM `ad_snapshot_url` CARREGA UM TOKEN. GUARDÁ-LO NUM ARTEFATO É GUARDAR UMA
CREDENCIAL NUM FICHEIRO QUE VAI PARA O GIT.
O contrato tem de guardar `id` e reconstruir a URL na hora, nunca persistir
a URL como veio.
```

### CAPTION FIRST → AUDIO ONLY → FULL VIDEO LAST, aplicado ao anúncio

A escada da C8 aplicada à Ad Library dá um resultado limpo, e é o melhor caso
que esta família tem:

| degrau | disponível no anúncio? | evidência |
|---|---|---|
| **CAPTION FIRST** | **SIM, e é quase tudo** | os quatro campos de texto, por cartão, sem tocar em mídia |
| **AUDIO ONLY** | **NÃO** — não há faixa, não há manifesto, não há endereço | os 28 campos não incluem nenhum endereço de mídia |
| **FULL VIDEO** | **NÃO pela API** | só pelo snapshot renderizado, e o lote está proibido |

```
NO ANÚNCIO, O `CAPTION FIRST` NÃO É UMA ECONOMIA — É A ROTA INTEIRA.
O texto do criativo É o dado, e ele vem sem um único byte de mídia.
```

E o formulário da PARTE 7, respondido sem inventar:

```
Ad Library snapshot   →  caption: NÃO (é HTML renderizado)
                         SRT/WebVTT: NÃO DOCUMENTADO
                         faixa de áudio: NÃO DOCUMENTADO
                         DASH/HLS: NÃO DOCUMENTADO
                         vídeo progressivo: NÃO DOCUMENTADO
Graph payload         →  NENHUM dos cinco. Os 28 campos não têm mídia.
CDN manifest          →  NÃO ALCANÇADO por esta missão — exigiria abrir o
                         snapshot, que é rede Meta real. PROBE_4.

PUBLIC / SIGNED / TTL / BYTES / LOGIN  =  NÃO SEI, para os três.
```

    NENHUM VÍDEO FOI BAIXADO NESTA MISSÃO. `VIDEO_BYTES_DOWNLOADED = 0`.

---
## A LEI QUE GOVERNA TUDO O QUE VEM A SEGUIR

Antes de qualquer rota, a cláusula. Termos de Serviço da Meta, §3.2:

> *«You may not access or collect data from our Products using automated means
> (without our prior permission) or attempt to access data you do not have
> permission to access, **regardless of whether such automated access or
> collection is undertaken while logged-in to a Facebook account.**»*
> — <https://www.facebook.com/legal/terms>

E os Termos de Recolha Automatizada, que fecham a porta dos fundos:

> *«**Acceptance of these Terms alone does not constitute the required written
> permission** to conduct Automated Data Collection; such permission must be
> obtained separately through Meta's formal authorization process.»*
> — <https://www.facebook.com/apps/site_scraping_tos_terms.php>

```
A ORAÇÃO FINAL DO §3.2 É A QUE INTERESSA A ESTA CASA: ESTAR DESLOGADO NÃO É
DEFESA. A rota pública desta casa roda deslogada de propósito — e a Meta
declara, por escrito, que isso não muda nada.
```

    A DECISÃO DA C10.5D ESTAVA CERTA E ESTAVA SUBFUNDAMENTADA. Ela apoiou-se
    no `robots.txt`. A cláusula acima é mais forte que o `robots.txt`, cobre
    Facebook e Instagram ao mesmo tempo, e diz explicitamente que deslogado
    conta. A decisão não muda; a prova dela fica mais dura.

---

## PARTE 9-13 · INSTAGRAM — as rotas oficiais, nos três estados

Legenda: `NO_APPROVAL` = app Live, sem App Review · `DEVELOPMENT` = modo de
desenvolvimento · `APPROVED` = App Review + Business Verification.

E a frase que mata o modo de desenvolvimento como estratégia de concorrência:

> *«The person who holds the admin role for the Page also holds an admin,
> developer, or tester role on the app.»*

```
MODO DE DESENVOLVIMENTO NUNCA ALCANÇA UM CONCORRENTE. Ele alcança contas cujo
administrador aceitou ter um papel no nosso app. Um concorrente não aceita.
```

    ITEM 16 DO RED TEAM, segunda prova documental.

### A matriz

| capacidade sobre CONCORRENTE | `NO_APPROVAL` | `DEVELOPMENT` | `APPROVED` |
|---|---|---|---|
| `business_discovery` — perfil | não | só de conta com papel no app | **SIM** |
| `business_discovery{media}` — publicações | não | idem | **SIM** |
| `like_count` em publicação de terceiro | não | condicional | **SIM, condicional** |
| `view_count` de Reel de terceiro | não | condicional | **SIM — e é exclusivo do Business Discovery** |
| `comments_count` | não | condicional | **SIM** |
| **TEXTO de comentário** | **não** | **não** | **NÃO — em nenhum nível** |
| `shares_count` · `saved_count` | não | não | **NÃO — excluídos por doc** |
| Hashtag Search | não | não | **SIM — exige Instagram Public Content Access** |
| **Stories de terceiro** | **não** | **não** | **NÃO — em nenhum nível** |
| insights (alcance, impressões, saves) | não | não | **NÃO — só conta própria** |
| Instagram Basic Display | **morto desde 2024-12-04** | morto | morto |

### `business_discovery` — a rota, e a sua forma é instrutiva

```
GET /<O_MEU_IG_USER_ID>?fields=business_discovery.username(<CONCORRENTE>){...}
```

```
PERGUNTA-SE AO NOSSO PRÓPRIO NÓ, E O CONCORRENTE É UM PARÂMETRO.
Não existe endpoint `/concorrente`.
```

| eixo | exigência |
|---|---|
| **a minha conta** | Instagram **Business ou Creator**, ligada a uma Página, com papel na Página |
| **permissões** | `instagram_basic` + `instagram_manage_insights` + `pages_read_engagement` — **as três, com App Review** |
| **a conta alvo** | tem de ser **Business ou Creator**. Não precisa de relação nenhuma connosco — **e é essa assimetria que dá valor ao endpoint** |
| **conta pessoal alvo** | *«cannot access Instagram consumer accounts»* — e o erro concreto **NÃO ESTÁ DOCUMENTADO** |
| **conta com restrição de idade** | *«Data about age-gated Instagram Business IG Users will not be returned.»* |

E a correcção que esta pesquisa traz à matriz desta casa:

```
`business_discovery` NÃO exige Instagram Public Content Access.
Essa feature cobre só os quatro endpoints de hashtag. São dois caminhos de
aprovação diferentes, e quase toda a literatura os junta.
```

### Campos do perfil — e o ponto contestado

Marcados **Public** na referência viva do IG User, logo alcançáveis por
expansão de campo: `biography` · `followers_count` · `id` · `media_count` ·
`username` · `website` · `alt_text`.

**NÃO marcados Public:** `follows_count` · `name` · `profile_picture_url` ·
`has_profile_pic` · `is_published`.

```
QUASE TODA A LITERATURA LISTA `follows_count`, `name` E `profile_picture_url`
COMO CAMPOS DO BUSINESS DISCOVERY. A REFERÊNCIA ACTUAL NÃO OS MARCA PUBLIC.
```

    Isto vai para o contrato como `NÃO SEI`, não como campo. Desenhar o
    esquema à volta de `profile_picture_url` seria construir sobre um blogue.

### Campos da publicação de concorrente

| campo | disponível | nota da doc |
|---|---|---|
| `caption` | **SIM** | texto do autor, integral |
| `timestamp` | SIM | ISO 8601 UTC |
| `like_count` | **CONDICIONAL** | *«if queried indirectly through another endpoint or field expansion the `like_count` field is **omitted** if the media owner has hidden like counts»* |
| `comments_count` | SIM | inclui respostas, exclui a legenda |
| `media_type` | SIM | `CAROUSEL_ALBUM` · `IMAGE` · `VIDEO` |
| `media_product_type` | SIM | `AD` · `FEED` · `STORY` · `REELS` |
| `media_url` | SIM | omitido se houver material protegido por direitos |
| `permalink` · `shortcode` | SIM | |
| `thumbnail_url` | SIM | só em `VIDEO` |
| `media_audio_type` | SIM | `MUSIC` · `ORIGINAL_SOUND` |
| **`view_count`** | **SIM** | *«View count for Instagram Reels… **Available for Business Discovery API only.**»* |
| `shares_count` | **NÃO** | *«Not accessible through Business Discovery or hashtag API endpoints.»* |
| `saved_count` | **NÃO** | *«Only accessible by the media owner»* |
| `children` (carrossel) | **NÃO DOCUMENTADO** | é edge, não campo; a doc do business_discovery não diz se expande |

```
`like_count` OMITIDO NÃO É ZERO E NÃO É NULL. É AUSENTE DO JSON.
Código que faça `media.like_count` produz lixo ou rebenta.
```

    O contrato da PARTE 26 tem `VALUE_KIND = EXACT | RANGE | NOT_AVAILABLE`
    exactamente para este caso.

E a descoberta que mais vale para uma ferramenta de concorrência agro:

```
`view_count` DE REEL DE TERCEIRO EXISTE, É OFICIAL, E SÓ EXISTE AQUI.
É a métrica de alcance mais forte que a família Meta dá sobre concorrente,
e não custa dólar nenhum.
```

### PARTE 12 · COMENTÁRIOS DO INSTAGRAM — o formulário respondido

A edge de comentários é do dono, e a doc não deixa margem:

> *«An access token from a User who created the IG Media object…»*

```
FREE_COUNT      = SIM — `comments_count` vem no business_discovery E na
                  rota pública da janela desta casa
FREE_TEXT       = PARCIAL e NÃO PERMITIDO — 58% medido pela janela pública
                  desta casa, sobre superfície que os ToS §3.2 cobrem
OFFICIAL_TEXT   = **NÃO EXISTE. Em nenhum nível de aprovação.**
PAID_TEXT       = existe no mercado. `apify/instagram-comment-scraper`
                  $1,90/1 000 comentários (lido 2026-09-12); plano gratuito
                  limitado a UMA página por post (~15 comentários)
PAGINATION      = paga: por página, com resposta em ranking
COST_PER_1000   = $1,90 (Apify oficial) · $0,47–$2,70 conforme actor e tier
LOGIN           = as rotas pagas declaram-se deslogadas; a Apify oficial não
                  aceita cookie nenhum (input schema conferido)
POLICY          = ToS §3.2 cobre a rota livre. A rota oficial NÃO EXISTE.
                  A rota paga é compra do resultado de uma técnica que os
                  mesmos ToS cobrem.
```

```
NÃO HÁ ROTA OFICIAL PARA TEXTO DE COMENTÁRIO DE TERCEIRO NO INSTAGRAM.
ISTO NÃO É UM BURACO DA NOSSA IMPLEMENTAÇÃO. É UM BURACO DA PLATAFORMA.
```

    E é a resposta à pergunta cara da PARTE 12: *não pagar por texto de
    comentário quando a ferramenta só pediu contagem* deixa de ser conselho e
    passa a ser a única rota oficialmente disponível — porque **a contagem tem
    rota oficial e o texto não tem nenhuma.**

### PARTE 10 e 11 · PROFUNDIDADE — o que se sabe e o que não se sabe

```
RECENT_DEPTH (rota pública deslogada) = 12, medido nesta casa em 2 contas,
                                        e corroborado pelo tecto declarado de
                                        um actor pago («Latest 12 posts»)
PAGINAÇÃO (business_discovery)        = por cursor. A doc avisa: «the response
                                        will not include previous or next
                                        fields… you will have to use the
                                        before and after cursors to construct
                                        [the] query strings manually»
DEPTH LIMIT (business_discovery)      = **NÃO DOCUMENTADO.** Nenhum máximo de
                                        itens, nenhum corte histórico, nenhum
                                        tecto de páginas aparece na doc.
```

    ITEM 8 DO RED TEAM — *12 recent posts vira history* — resolve-se com dois
    factos que não se anulam: a rota pública tem tecto 12; a rota oficial não
    tem tecto documentado. São rotas diferentes, com autorizações diferentes.

**E a evidência de comunidade contradiz o 12 por baixo, não por cima.** Reportes
de setembro de 2026 nos repositórios das ferramentas públicas descrevem `401`,
`403` em GraphQL e **`429` já no primeiro pedido**, reproduzido em rede móvel,
WiFi residencial e VPN.

```
A CONTESTAÇÃO ÚTIL DE 2026 NÃO É «SERÃO MAIS DE 12?». É «SERÃO ZERO?».
```

Isto é evidência secundária, datada, e está registada como tal. Não promove nem
rebaixa estado nenhum — mas desaconselha construir qualquer coisa sobre a rota
pública deslogada, mesmo que a política a permitisse.

### STORIES e o resto

```
INSTAGRAM STORIES DE TERCEIRO:
  OFFICIAL_API   = NÃO EXISTE, em nenhum nível de aprovação
  PUBLIC         = a casa mediu BLOCKED
  LOGIN_REQUIRED = a lei desta casa fecha: LOCAL_SESSION contra TERCEIRO = NOT_USABLE
  PAID_ACTOR     = existem 4 no store; o oficial da Apify marca a capacidade
                   «deprecated»; os dois dedicados são os mais caros do IG
                   ($3,00 e $17,00 por 1 000)
  ARCHIVE        = NÃO
  24H_WINDOW     = sim, por natureza da plataforma
```

```
STORIES CONTINUAM BLOCKED, E AGORA COM PROVA DOCUMENTAL DE QUE NÃO É
LIMITAÇÃO NOSSA: não há endpoint, não há parâmetro, e a busca por hashtag
exclui Stories por escrito.
```

`ig_hashtag_search` está vivo em 2026, e o tecto é declarado:

```
30 hashtags únicas por conta, em janela ROLANTE de 7 dias. Uma hashtag
consultada conta contra o limite durante 7 dias. Sem emoji. Sem Stories.
Exige Instagram Public Content Access: App Review + Business Verification.
```

### RATE LIMIT — e aqui está a parede real

> *«Business Discovery and Hashtag Search endpoints… are subject to **Platform
> Rate limiting**.»* → *«Calls within one hour = **200 × Number of Users**»*

```
UMA FERRAMENTA INTERNA DE CONCORRÊNCIA TEM 1 UTILIZADOR.
→ ~200 CHAMADAS POR HORA. NÃO é o 4800 × impressões que se lê por aí.
```

    Esta é a restrição que decide o desenho da ferramenta, e é mais apertada
    que qualquer tecto de profundidade. Com 15 contas Meta no lote congelado,
    200 chamadas/hora é folgado para vigilância diária e apertado para
    histórico. O delta da PARTE 22 volta a ser requisito, não optimização.

---

## PARTE 15-17 · FACEBOOK — PPCA, PPMA, e a confusão que o red team pediu para desfazer

### A diferença exacta, e a doc resolve-a numa frase

> **PPMA:** *«Analyze engagement with public Pages by viewing Like and follower
> counts» · «Aggregate public-facing 'about' Page information»*
> **E depois:** *«If your app also needs to read the Page Feed edge, or Comments
> on a Page's Posts, request the **Page Public Content Access** feature
> instead.»*

| | **PPMA** | **PPCA** |
|---|---|---|
| campos do nó Page (`about`, `fan_count`, `website`) | SIM | SIM |
| `/pages/search` | SIM | SIM — e a doc diz *«to conduct competitve analysis»* |
| `/{page-id}/feed` — **as publicações** | **NÃO** | **SIM** |
| `/{page-post-id}` | NÃO | SIM |
| `/{page-post-id}/comments` | **NÃO** | **SIM** |
| App Review | exigido | exigido |
| Business Verification | exigido | exigido |

```
PPMA = O PERFIL DA PÁGINA.   PPCA = O CONTEÚDO DA PÁGINA.
Custam a mesma revisão. A doc diz que PPMA é «superseded by» PPCA.
→ PARA CONCORRÊNCIA, PEDIR PPMA SOZINHO NÃO TEM RAZÃO DE SER.
```

    ITEM 15 DO RED TEAM resolvido, e com uma consequência prática: a matriz
    desta casa declara `graph:/pages/search` sob «Page Public Metadata Access».
    Está certo e é insuficiente — a mesma chamada com PPCA é a que a Meta
    nomeia para análise competitiva.

### Os três estados, para uma Página de CONCORRENTE

| capacidade | `NO_APPROVAL` (Live) | `DEVELOPMENT` | `APPROVED` |
|---|---|---|---|
| feed / publicações do concorrente | **NÃO** | **NÃO** | **SIM, com PPCA** |
| comentários em publicação dele | NÃO | NÃO | **SIM com PPCA** — degradado, ver abaixo |
| metadados da Página (`fan_count`, `about`) | **NÃO** | NÃO | SIM — PPCA **ou** PPMA |
| `/pages/search` | NÃO | NÃO | SIM |
| insights da Página dele | NÃO | NÃO | **NÃO — só o dono** |
| **Reels da Página dele** | NÃO | NÃO | **NÃO — em nenhum nível** |

E a frase que fecha o `NO_APPROVAL`:

> *«Once you set your app to live mode, it will not be able to see any Page
> public content without this feature.»*

```
`fan_count` NÃO É CAMPO PÚBLICO GRATUITO. A doc marca-o «Can be read with Page
Public Content Access or Page Public Metadata Access».
```

E a doc **não publica** lista afirmativa de campos de Page legíveis com app
token e zero aprovações.

```
FACEBOOK_PAGE_FIELDS_SEM_APROVACAO = NÃO DOCUMENTADO.
Não desenhar contra um nível gratuito presumido.
```

### PARTE 16 · PROFUNDIDADE E HISTÓRICO DO FEED

Os dois números que a doc dá, e são duros:

> *«The API will return approximately **600 ranked, published posts per year**.»*
> *«You can only read a maximum of **100 feed posts with the `limit` field**.»*

```
FACEBOOK_HISTORY_DEPTH = ~600 publicações por ano, em RANKING — não é «todas»
FACEBOOK_PAGE_SIZE     = máximo 100 por chamada
PAGINATION             = por cursor, before/after
```

E o remédio de rate limit que a própria Meta escreve e quase ninguém lê:

> *«When using the Page Public Content Access feature, use a **system user
> access token** to avoid rate limiting issues.»*

Porque a fórmula de Pages é `4800 × Engaged Users`, e **a Página de um
concorrente não gera utilizador engajado para o nosso app**. O token de system
user é a resposta documentada.

### As três edges, e uma delas já não existe na doc

| edge | estado documental |
|---|---|
| `/{page-id}/feed` | ✅ a canónica. É esta que se usa |
| `/{page-id}/published_posts` | ✅ documentada, mesmos 600/ano e limite 100 |
| `/{page-id}/posts` | ⚠️ **já não tem página de referência própria** — a URL serve a referência do Feed |

```
A DISTINÇÃO CLÁSSICA «/feed traz posts de visitante, /posts só os da Página»
ERA VERDADE EM VERSÕES ANTIGAS. Na doc actual `/posts` não é superfície
documentada. Usar `/feed`.
```

### PARTE 17 · COMENTÁRIOS DO FACEBOOK — e é aqui que a doc se degrada

Duas restrições declaradas, e a primeira é específica do PPCA:

> *«The `id` field for the `/PAGEPOST-ID/comments` endpoint **will no longer be
> returned for apps using the Page Public Content Access feature**»* — salvo se
> o app puder executar a tarefa MODERATE na Página.

> *«Other users' profile information and comments will not be returned when
> accessing user posts… unless authorized by those users.»*

E o achado documental mais incómodo desta pesquisa:

```
NA REFERÊNCIA ACTUAL DO NÓ Comment, A TABELA DE CAMPOS LISTA:
  id · can_comment · can_reply_privately · comment_count · is_private
  like_count · live_broadcast_timestamp · parent · private_reply_conversation
  user_likes

`message`, `from`, `created_time`, `permalink_url` E `attachment` ESTÃO AUSENTES
DESSA TABELA. `message` aparece só como PARÂMETRO de escrita.
```

```
FACEBOOK_COMMENT_TEXT_FOR_COMPETITOR = DOCUMENTADO-AMBÍGUO.
Não é SIM. Não é NÃO. É uma pergunta de probe (PROBE_6).
```

    Escrever `SIM` seria citar prática de mercado como se fosse doc. Escrever
    `NÃO` seria afirmar remoção que a Meta não anunciou. A casa tem a palavra
    certa para isto e é `NÃO SEI`.

Respostas do formulário da PARTE 17:

```
count            → `comment_count` documentado no nó Comment
top comments     → `/page-post/comments` com PPCA
full comments    → paginação por cursor, mas com o `id` removido sob PPCA,
                   deduplicar e retomar fica difícil por desenho
replies          → `comment_count` = «Number of replies to this comment»
reactions        → `like_count` no comentário; no post, `reactions` é descrito
                   como «People who reacted» — lista de IDENTIDADE, que colide
                   com a restrição de informação de perfil acima.
                   → esperar CONTAGEM agregada, não identidade.

CHEAPEST_ROUTE_PER_POST = PPCA (zero dólares, custo em App Review)
FREE_ROUTE              = nenhuma. ToS §3.2 cobre a superfície pública.
PAID_GAP                = `apify/facebook-comments-scraper`, $1,40/1 000
                          comentários (lido 2026-09-12)
```

### E os Reels da Página do concorrente

> `/{page-id}/video_reels`, na secção Reading: *«You can't perform this
> operation on this endpoint.»*
> E a referência de page-post: *«This endpoint does not return Reels.»*

```
FACEBOOK_COMPETITOR_REELS = SEM ROTA, EM NENHUM NÍVEL DE APROVAÇÃO.
```

### META CONTENT LIBRARY — a porta que não é para nós

Cobre tudo o que falta: publicações de Facebook, Instagram **e Threads**,
comentários **com texto**, estatísticas com quebra de reacções.

E a elegibilidade fecha-a:

> *«a not-for-profit institution whose primary purpose or core activity is to
> conduct scientific or public interest research.»*

```
NÃO HÁ TIER COMERCIAL, NÃO HÁ TIER PAGO, NÃO HÁ TIER DE PARCEIRO.
Para o SINTONIA EAME, a Meta Content Library NÃO É UMA OPÇÃO.
```

⚠️ E uma armadilha de fonte: a doc viva da Meta nomeia o **CASD** como revisor e
diz *«There are no fees associated with access or computation»*, enquanto o
anúncio de 2023 e muita cobertura nomeiam o ICPSR com tarifa de US$ 371/mês a
partir de janeiro de 2026. **São caminhos e eras diferentes.** Citar a doc viva.

---
## PARTE 20 · OPEN SOURCE — arquitectura, não bypass

Revistos **28 projectos** em seis categorias. A regra foi a da missão: **`TECHNIQUE`
só foi rotulada quando o README ou o código afirma.** Caso contrário, `NÃO SEI`.

### A descoberta central, e muda uma conta desta casa

```
EM 2026-06-15 A META RETIROU A EXIGÊNCIA DE ACCESS TOKEN DOS ENDPOINTS oEmbed.
Instagram, Facebook E Threads. Sem token, sem app, sem App Review.
Só para conteúdo PÚBLICO e só para POST ÚNICO.
```

Endpoints, declarados no plugin oficial da Meta
(`github.com/facebook/meta-embeds-for-wordpress`, 3 estrelas, activo):

```
graph.facebook.com/v25.0/instagram_oembed
graph.facebook.com/v25.0/oembed_post
graph.facebook.com/v25.0/oembed_video
graph.threads.com/oembed
```

E o repositório oficial de amostras do Threads regista a mudança num commit com
nome próprio: *«oembed-remove-access-token»*.

```
ISTO É UMA SUPERFÍCIE OFICIAL, SEM TOKEN, SEM COOKIE E SEM LOGIN, PARA LER
CONTEÚDO PÚBLICO DE IG, FB E THREADS.
```

**E interessa directamente a esta casa**, porque `instagram_janela.py` já lê a
rota de embed — mas lê-a **pelo HTML de `instagram.com`, com navegador**, que é
a superfície que os ToS §3.2 cobrem. O endpoint oficial `instagram_oembed` é
outra porta para o mesmo dado, e é uma porta que a Meta abriu.

**As ressalvas, declaradas e não menosprezadas:**

```
· só POST ÚNICO — não serve feed, hashtag, conta nem histórico
· rate limits POTENCIALMENTE MENORES que na rota com token
· devolve HTML DE EMBED e metadados, NÃO dado estruturado
· o HTML carrega JavaScript da Meta no navegador do visitante — implicação
  de RGPD para público na UE, que é o nosso público
· a versão de endpoint no registo público do oEmbed (`v16.0`) está atrasada
  face à que a Meta usa (`v25.0`)
· Threads NÃO consta do `providers.json` público do oEmbed — só IG e FB
```

    NÃO É UMA ROTA DE DADOS. É UMA ROTA DE MOLDURA. Mas é a única superfície
    deste censo inteiro que não exige nenhum compromisso NO-GO, e por isso
    entra no P0 como PROBE, não como capacidade.

### Os projectos, e o que cada um ensina

| projecto | estrelas | actualizado | técnica declarada | o que vale aprender | o que é NO-GO |
|---|---|---|---|---|---|
| `facebookresearch/Ad-Library-API-Script-Repository` | 337 | 2025-02 | **API oficial** | paginação por cursor opaco com `last_error_url` + `last_retry_count`: o erro fica ancorado ao ponto do stream, não ao lote | nada. Falta backoff |
| `Paularossi/AdDownloader` | 35 | **2026-07** | API oficial **+ Selenium sobre o snapshot** | **duas fases com estado próprio**: metadados pela API, mídia à parte com planilha de status por item. Falha de mídia não contamina o dataset de metadados | o Selenium sobre `ad_snapshot_url` |
| `favstats/metatargetr` | 43 | **2026-09** | Ad Library Report + **headless Chrome** | **arquivo delta diário** por página, criando série temporal que a API não dá. E um commit recente troca resultado vazio silencioso por excepção | *«to bypass Facebook's JavaScript-based bot detection»* — **evasão declarada** |
| `facebookresearch/Radlibrary` | 73 | **ARQUIVADO 2025-07** | API oficial | *«reliably removes the access token from any downloaded data»* — **saneamento do segredo na borda de saída** | nada. Não é evidência corrente |
| `instaloader/instaloader` | 13,4k | **2026-09** | **endpoint interno** (`i.instagram.com`, `graphql/query`, `x-ig-app-id`) | ver abaixo — as duas melhores ideias do censo | superfície interna + reuso de cookie. **NO-GO integral** |
| `subzeroid/instagrapi` | 6,8k | **2026-09** | **private mobile API**, declarado | honestidade de escopo: *«best suited for testing, research, and controlled internal automation»* | login automatizado, proxies, challenge resolver. **NO-GO integral** |
| `mikf/gallery-dl` | 19,5k | **2026-09** | HTML público + JSON + **manifesto DASH** | **bloqueio como estado nomeado de primeira classe** | reuso de cookie autenticado; sugere VPN na mensagem de bloqueio |
| `kevinzg/facebook-scraper` | 3,3k | **PARADO out/2023** | HTML público | checkpoint de retomada em CSV | cookies `c_user`/`xs`. E **3,3k estrelas não são evidência corrente** |
| `fbsamples/threads_api` | 290 | **2026-03** | **Threads API oficial** | separação de identidade de app por produto | nada. **Única opção viável de Threads** |
| `facebook/meta-embeds-for-wordpress` | **3** | **2026-06** | **oEmbed oficial, sem token** | registo declarativo de providers: nova superfície = uma linha, não um módulo | nada. **A superfície mais limpa do censo** |
| `yt-dlp/yt-dlp` | 191k | contínuo | **misto, declarado no código** | **inventário ≠ aquisição** — ver abaixo | extractor de **Instagram** usa `i.instagram.com`/`api/v1`. O de **Facebook** é HTML público |

### As cinco ideias que valem levar, e nenhuma é uma técnica de acesso

1. **`RateController` por CLASSE de pedido** (instaloader). Orçamentos separados
   em janela deslizante: 200 pedidos/11 min para GraphQL, 75/11 min para
   «outros», 199/30 min para a via iPhone. Não um contador global.
   → Esta casa tem `teto_de_rede` como contador **único**. A lição é que um
   contador por classe de pedido mede o que a plataforma mede.

2. **Marca-d'água de progresso DESACOPLADA do artefato** (instaloader
   `--latest-stamps`). O estado de progresso vive num ficheiro próprio e
   **sobrevive a mover ou apagar a mídia baixada**.
   → É exactamente a lei que o `coleta_checkpoint` desta casa já escreveu ao
   avesso: *«uma gaveta diz o que existe, nunca o que aconteceu»*. Convergência
   independente.

3. **Bloqueio como ESTADO NOMEADO** (gallery-dl). A assinatura
   `{"__dr":"CometErrorRoot.react"}` no corpo da resposta vira uma condição com
   nome e `fallback_retries` configurável, em vez de excepção genérica.
   → É o combustível directo do `NÃO SEI` visível: bloqueio medido não é
   silêncio.

4. **Inventário ≠ aquisição** (yt-dlp `-F`). A lista do que a rede oferece é um
   artefato **separado** do que foi baixado.
   → É o modelo exacto de `SOURCE → EVIDENCE` desta casa, e a casa ainda não o
   tem para mídia.

5. **Saneamento do segredo na borda de saída** (Radlibrary) mais validação de
   tipo **durante** a travessia do JSON, não em `try/except` posterior (yt-dlp
   `traverse_obj` com `{url_or_none}`).
   → Directamente aplicável ao `ad_snapshot_url`, que carrega token.

### E o padrão que fecha a categoria Threads

```
OS TRÊS CLIENTES NÃO-OFICIAIS DE THREADS FORAM DESLIGADOS PELOS PRÓPRIOS
AUTORES ENTRE SETEMBRO E OUTUBRO DE 2023, APÓS CONTACTO DA META.
```

`junhoyeo/threads-api` (1,6k estrelas) tem banner: *«the development … have
been halted and discontinued due to communication received from Meta Platforms,
Inc.»* — último commit: *«Bye 👋»*. `dmytrostriletskyi/threads-net` (424
estrelas) **apagou todo o código** e pôs o aviso da Meta no lugar.

```
NÃO É DECADÊNCIA TÉCNICA. É DECISÃO JURÍDICA.
Qualquer arquitectura de Threads que dependa desse caminho já nasce morta.
```

---

## PARTE 13 (conclusão) · ÁUDIO-ONLY — a correcção que esta missão devia a si própria

A C10 desta casa provou `INSTAGRAM_AUDIO_ONLY = PROVEN` num Reel:
`-f bestaudio` seleccionou `dash-1062115465344400a`, `VIDEO_BYTES_DOWNLOADED = 0`,
362 479 bytes de m4a. **Essa medição continua válida e não é revogada.**

O que esta missão acrescenta, medido em evidência pública de terceiros:

```
ÁUDIO-ONLY PELA REDE NÃO É PROPRIEDADE DA PLATAFORMA.
É PROPRIEDADE DO POST.
```

Três provas independentes de que a Meta serve DASH com áudio separado:

| prova | plataforma | evidência |
|---|---|---|
| tabela `-F` | **Facebook** | `1826790661010186a m4a audio only … mp4a.40.5 66k 44k DASH audio, m4a_dash` · `~231,41 KiB` contra `~3,95 MiB` do vídeo 720p |
| formato seleccionado | **Instagram** | `dash-1150901429362791v+dash-838880814305817ad` — o sufixo `ad` é áudio-only |
| leitura do manifesto | **Facebook** | `gallery-dl` localiza a `BaseURL` do áudio pelo elemento `AudioChannelConfiguration`, que só existe se houver `AdaptationSet` de áudio |

**E o contra-exemplo, que é o achado:**

```
yt-dlp #12394, Instagram, 2025-02-17, fechado como «not planned»:
a tabela -F do item tem CINCO formatos e ZERO linhas «audio only».
Os DASH são todos `video only`, e o único caminho para o som é um dos MP4
muxados — ou seja, baixar tudo e demuxar localmente.
```

E a comunidade reporta o padrão: Reels **com música** costumam expor só vídeo;
Reels de **som original** costumam expor a faixa separada. Isto está `CLAIM`,
não provado.

```
A ÚNICA PROVA FIÁVEL É A LINHA `audio only` NA TABELA DE FORMATOS DAQUELE
ITEM. Estimar banda com «Reel = ~200 KB de áudio» para todo o lote é errado.
```

    ITEM 10 DO RED TEAM — *local audio extraction vira audio-only network* —
    tinha um irmão que a missão não listou e que é mais perigoso:
    **um item audio-only vira a plataforma inteira audio-only.** A C10 mediu UM
    Reel. Um Reel não é um lote.

### CAPTION FIRST — e a assimetria que ninguém pode somar

```
FACEBOOK  serve faixa de legenda. SRT. E DISTINGUE AUTOMÁTICA DE MANUAL.
INSTAGRAM não serve faixa de legenda nenhuma.
```

A prova do lado do Facebook é código mergeado — yt-dlp PR #8296, 2023-11-26,
*«[Facebook] Fix captions not included as subtitles»*. A saída de `--list-subs`
do próprio PR:

```
Language Name                     Formats
en_US    English (Auto-generated) srt
es_LA    Español                  srt
id_ID    Bahasa Indonesia         srt
```

E o campo que separa as duas espécies:

```
`localized_creation_method` PRESENTE  → automatic_captions
`localized_creation_method` AUSENTE   → subtitles (humana)
```

```
O PRÓPRIO JSON DA META JÁ SEPARA «A PLATAFORMA TRANSCREVEU» DE «ALGUÉM
ESCREVEU». Colapsar os dois seria apagar a distinção na origem.
```

    A C6 desta casa — *A ESPÉCIE DO TEXTO* — tem aqui a sua confirmação
    externa. E os itens 20 e 21 do red team (*SRT automática vira human
    caption*, *captions inexistentes viram transcript*) deixam de ser risco
    teórico: o campo que os distingue existe e tem nome.

Do lado do Instagram, a ausência está registada: yt-dlp issue #15874, aberta
2026-02-07 e fechada — `--write-subs`, `--write-auto-subs` e `--list-subs` não
devolvem nada. As «AI captions» do Instagram são **renderizadas no player**, não
servidas como faixa.

```
NO INSTAGRAM, TEXTO FALADO SÓ EXISTE POR ASR SOBRE O ÁUDIO — E O RESULTADO
É `TRANSCRIPT_ASR`, NUNCA `NATIVE_CAPTION`. A casa já o tinha escrito;
agora tem prova externa de que não há alternativa.
```

### A escada final, por superfície

| superfície | CAPTION FIRST | AUDIO ONLY | FULL VIDEO |
|---|---|---|---|
| **Ad Library (anúncio)** | **é a rota inteira** — 4 campos de texto por cartão | não existe | só pelo snapshot; lote proibido |
| **Facebook (orgânico)** | **SRT nativa, auto/manual separadas** | **por item**, quando há DASH com áudio | último recurso |
| **Instagram (orgânico)** | só `caption` do autor — **não é fala** | **por item**, quando há DASH com áudio | quando não há |
| **Threads** | `text` do post | `NÃO DOCUMENTADO` | `NÃO DOCUMENTADO` |

```
FULL_VIDEO_REQUIRED_WHEN = Instagram, item sem faixa DASH de áudio, e a
ferramenta pediu explicitamente a fala. Em mais nenhum caso.
```

---

## PARTE 21 · FÓRUNS E COMUNIDADE — evidência secundária, rotulada

```
TUDO NESTA SECÇÃO É `CLAIM`. Nenhum post de fórum promove estado nenhum.
```

E uma confissão de cobertura que a honestidade obriga:

```
REDDIT NÃO FOI ALCANÇADO. r/webscraping, r/FacebookAds, r/PPC, r/datasets e
r/InstagramMarketing ficaram POR AMOSTRAR. É o maior fórum de praticantes
do tema, e falta-nos.
```

### O que a comunidade confirma, e que já está acima com fonte primária

| afirmação | corrobora |
|---|---|
| a API da Ad Library devolve menos que a UI, e fora da UE/UK só político | a frase de escopo da PARTE 3 |
| ninguém obtém o criativo pela API — todos renderizam o snapshot | a PARTE 7 |
| não há cursor de «mudou desde» — o delta degenera em re-enumeração completa | a PARTE 22 |
| contagem e texto de comentário são produtos diferentes, com preços diferentes | a PARTE 12 |
| os actors são scrapers vestidos de API | a PARTE 19 |

### O que a comunidade acrescenta, e não estava na doc

**1. Tokens de system user NÃO funcionam na Ad Library API.**
Resposta aceite no Stack Overflow, 2026-01-02: cada utilizador precisa de um
**papel explícito no app**. O autor: *«you would have to add developer users,
which defeats the purpose of having a public api»*.

```
ISTO CONTRADIZ O REMÉDIO QUE A PRÓPRIA META DOCUMENTA PARA O PPCA — «use a
system user access token». São dois produtos, dois comportamentos, e confundi-los
custa uma arquitectura.
```

**2. O repositório oficial de amostras da Ad Library está abandonado.**
Issues de 2023, 2024 e 2025 abertas **sem uma única resposta de mantenedor**.

```
ISSO NÃO É EVIDÊNCIA SOBRE A API. É EVIDÊNCIA SOBRE A SUPERFÍCIE DE SUPORTE,
e conta na decisão de adoptar.
```

**3. O Instagram público deslogado está em decadência acentuada em 2026.**
Reportes de Setembro de 2026: `401` em `get_posts()` anónimo; `403` em
`/graphql/query` a aparecer como falso «perfil não existe»; e **`429` já no
primeiro pedido**, reproduzido em rede móvel, WiFi residencial e VPN. E um caso
em que o navegador reproduziu o mesmo resultado — o que exclui impressão digital
do cliente e aponta para mudança do lado da Meta.

```
A ADVERTÊNCIA UNIVERSAL «usa IP residencial» É CONTRADITA POR MEDIÇÃO DE
PRATICANTE. Fica CONTESTADO, e é mais uma razão para não construir ali.
```

**4. A vida da URL assinada da CDN da Meta: ninguém sabe.**
Todos explicam que o parâmetro `oe` é um timestamp Unix em hexadecimal.
**Nenhuma fonte diz a duração.** Único limite encontrado: um feed estático
sobreviveu **menos de duas semanas**.

```
MEDIA_URL_TTL = NÃO SEI.
E a resposta de engenharia certa não é assumir uma constante — é LER o `oe`.
```

    ITEM 19 DO RED TEAM resolvido pela via correcta: o campo
    `MEDIA_URL_DURABILITY` do contrato recebe `SIGNED_TTL` com o valor lido do
    próprio endereço, nunca um número decorado.

**5. A contradição dos números do actor.**
A API pública da Apify devolve, para `apify/instagram-scraper` em 30 dias:
**17 081 345 execuções, 42 618 com timeout, 1 183 falhadas.** A página do actor
anuncia **«100.0% runs succeeded»**.

```
42 618 TIMEOUTS NÃO SÃO 100% DE SUCESSO. O número de marketing é arredondado,
não verdadeiro.
```

    ITEM 11 DO RED TEAM — *actor marketing vira proof* — com números dos dois
    lados, da mesma plataforma, no mesmo dia.

### Delta contra a Meta — como quem o faz a sério, o faz

Duas metodologias de primeira mão, ambas de projectos que espelham a Ad Library:

```
Wesleyan Media Project   checkpoint em `ad_id` + `page_id`
                         + CHECKSUM do ficheiro de mídia, para apanhar
                           criativo reutilizado entre anúncios
                         «já visto» = diferença de conjuntos contra uma lista
                           mestra; só o não-colhido entra na fila
                         corre DIARIAMENTE

Lejo1/facebook_ad_library  acrescenta a peça que falta ao anterior:
                           `_last_updated`, refrescado em cada recolha
                         → é o que separa «continua a correr» de «desapareceu»
```

```
DETECTAR QUE UM ANÚNCIO FICOU INACTIVO FAZ-SE POR AUSÊNCIA-NA-RECOLHA MAIS
CARIMBO DE FRESCURA. A META NÃO EMITE SINAL DE REMOÇÃO.
```

E o aviso que torna isto perigoso, e que já estava na PARTE 26:

```
A API JÁ FOI VISTA A DEVOLVER `{"data":[]}` PARA PÁGINAS CUJOS ANÚNCIOS ESTÃO
VISÍVEIS NA UI. Logo «sumiu do resultado» NÃO se lê como «parou de correr».
Qualquer regra de inactividade construída sobre ausência produz mortes falsas.
```

---
## PARTE 27 · COBERTURA DO CONCORRENTE — contra o lote real, não contra um fictício

A missão pedia um concorrente fictício. **Esta casa tem um lote congelado real**,
`PUBLIC-COMM-FIRST-BATCH-EAME`, `FROZEN_AT = 2026-08-30`. Medi contra ele.

```
ACCOUNTS ........................ 22
  FACEBOOK ...................... 10
  YOUTUBE ....................... 7
  INSTAGRAM ..................... 5
  THREADS ....................... 0
CONTENT_COLLECTION_STAGE ........ NOT_STARTED
campo PAGE_ID no esquema ........ NÃO EXISTE
```

### O buraco que só apareceu ao cruzar o lote com a Ad Library

`search_page_ids` pede **IDs numéricos de Página**. O lote guarda `ACCOUNT_URL` e
`ACCOUNT_HANDLE`. Varridas as 10 URLs de Facebook:

| empresa | país | id numérico na URL |
|---|---|---|
| BASF · BAYER · CORTEVA · SYNGENTA | ES | **nenhum** (4 de 4) |
| SYNGENTA | FR | nenhum |
| NUFARM | FR | `100088697208474` — ⚠️ URL `/people/`, que sugere **perfil**, não Página |
| BAYER | IT | nenhum |
| BASF | IT | `1741459832625091` |
| NUFARM | IT | `2312073685546312` |
| SYNGENTA | IT | `2007689772789481` |

```
4 DE 10 TÊM UM NÚMERO NA URL. E UM DELES PODE NÃO SER UM PAGE ID.
6 DE 10 NÃO TÊM NENHUM.
```

    RESOLVER `handle → page_id` É O PRIMEIRO DEGRAU DA AD LIBRARY, E ESTA CASA
    NÃO O TEM. É o mesmo degrau que a C3 teve de resolver no YouTube
    (`youtube.channel.resolve`), e pela mesma razão: o lote guarda endereços e a
    API pede identificadores.

E a `search_terms` funciona por nome — 100 caracteres, sem tradução, em italiano
para a Itália. É a rota de recurso para as 6 sem número, e é mais fraca: nome de
empresa não é identidade provada.

### A matriz de cobertura, por família

Estados: **FREE** (grátis e permitido, executável) · **OFFICIAL** (rota oficial
existe, exige aprovação/credencial que a casa não tem) · **PAID** (só por rota
paga) · **BLOCKED** (medido e recusado, ou sem rota em nenhum nível) ·
**UNKNOWN**.

| | INSTAGRAM | FACEBOOK | THREADS | ADS (Ad Library) |
|---|---|---|---|---|
| **ADS_COVERAGE** | — | — | — | **OFFICIAL** · grátis em dólar, custa identidade confirmada. **UE/Itália: 1 ano** |
| **ORGANIC_COVERAGE** | **OFFICIAL** · `business_discovery`, 3 permissões com App Review | **OFFICIAL** · PPCA, ~600/ano, ≤100 por chamada | **OFFICIAL** · `profile_posts`, App Review | — |
| **REELS_COVERAGE** | **OFFICIAL** · e com `view_count`, exclusivo do Business Discovery | **BLOCKED** · `/page/video_reels` não suporta leitura | **OFFICIAL** · via `profile_posts` | `publisher_platforms` inclui Reels como superfície, não como objecto |
| **THREADS_COVERAGE** | — | — | **OFFICIAL** · `profile_posts` · `profile_lookup` · `keyword_search` | Threads **está** no enum `publisher_platforms` da Ad Library |
| **BRANDED_CONTENT_COVERAGE** | **OFFICIAL** · `branded_content_search`, IG post · story · reel | **OFFICIAL** · o mesmo endpoint, FB post | **BLOCKED** · o índice não cobre Threads | — |
| **COMMENTS_COVERAGE** | **BLOCKED** (texto) · **OFFICIAL** (contagem) | **UNKNOWN** · PPCA abre a edge, mas o nó `Comment` não documenta `message` | **UNKNOWN** · replies de terceiro não documentadas | **BLOCKED** · a Ad Library não tem comentários, por estrutura |
| **MEDIA_COVERAGE** | **OFFICIAL** · `media_url`, `thumbnail_url` — durabilidade `NÃO SEI` | **OFFICIAL** com PPCA · **e legenda SRT nativa** | **OFFICIAL** · `media_url`, TTL `NÃO DOCUMENTADO` | **BLOCKED** · só `ad_snapshot_url`; lote proibido por escrito |
| **METRICS_COVERAGE** | **OFFICIAL parcial** · `like_count` (condicional) · `comments_count` · `view_count`. **Sem** shares, saves, insights | **OFFICIAL parcial** · `reactions`/`shares` como contagem; identidade não | **OFFICIAL parcial** · `profile_lookup`, agregado de **7 dias**, nunca por post | **OFFICIAL parcial** · `eu_total_reach` exacto. **Gasto e impressões: NUNCA para comercial** |
| **STORIES_COVERAGE** | **BLOCKED** em todos os níveis | n/a | n/a | Branded Content **lista** IG story — mas o índice só guarda o que está no ar, e Story expira em 24 h |

```
NENHUMA CÉLULA DESTA MATRIZ É `FREE`.
Não há uma única capacidade de observação de concorrente na família Meta que
esta casa possa executar hoje, gratuitamente e com permissão.
```

E é essa frase, e não o custo, o verdadeiro veredito da missão.

---

## PARTE 28 · APIFY RESIDUAL — para que é que ela ainda serve

A meta declarada é `APIFY = RESIDUAL GAP PROVIDER`, não `APIFY = META ENGINE`.
Medindo o que sobra depois de esgotadas as rotas oficiais:

### INSTAGRAM

| capacidade | `WHY_FREE_NOT_ENOUGH` | actor | uso esperado | custo lido 2026-09-12 | delta? | só enrich? |
|---|---|---|---|---|---|---|
| **texto de comentário** | **não há rota oficial em nenhum nível de aprovação.** O motivo canónico correcto é `FREE_ROUTE_UNAVAILABLE`, **não** `FREE_ROUTE_INSUFFICIENT_CAPABILITY` | `apify/instagram-comment-scraper` | só sobre post já listado e já escolhido | **$1,90 / 1 000** · plano gratuito: **1 página, ~15 comentários** | sim, por post | **SIM — enrich puro** |
| histórico além do que `business_discovery` pagina | **desconhecido**: a doc não declara tecto. O gap pode não existir | — | — | — | — | — |
| Stories | sem rota oficial; e a rota paga é a mais cara e a menos legível do censo | 4 actors, o oficial marca a capacidade «deprecated» | **nenhum** — recomendado NO-GO | $3,00 e $17,00 / 1 000 | n/a | n/a |

### FACEBOOK

| capacidade | `WHY_FREE_NOT_ENOUGH` | actor | custo | delta? |
|---|---|---|---|---|
| posts da Página | PPCA não obtida. **`AUTHORIZATION_BLOCK`, não falta de capacidade** | `apify/facebook-posts-scraper` | desde **$2,00 / 1 000** | sim |
| texto de comentário | PPCA não obtida **e** a doc do nó `Comment` é ambígua sobre `message` | `apify/facebook-comments-scraper` | **$1,40 / 1 000** | por post |
| **Reels da Página** | **sem rota oficial em nenhum nível** — `/page/video_reels` não lê | `apify/facebook-reels-scraper` | desde **$3,16 / 1 000** | sim |

### THREADS

```
GAP PAGO = NENHUM, HOJE.
Nenhum actor de Threads é citado por este repositório. As três portas oficiais
existem e a única coisa que falta é App Review — que não se compra por item.
```

    PAGAR UM ACTOR DE THREADS SERIA COMPRAR A VOLTA A UMA APROVAÇÃO, NÃO A UMA
    CAPACIDADE EM FALTA. É a distinção que a matriz desta casa já sabe fazer, e
    é a que separa `FREE_ROUTE_UNAVAILABLE` de `AUTHORIZATION_BLOCK`.

### ADS

```
GAP PAGO = NENHUM, E ESTE É O ACHADO QUE MAIS POUPA.
```

Sete actors de Ad Library no store, entre **$0,55** e **$17,00** por 1 000. E a
rota oficial custa **zero dólares**, cobre Itália, e é a fonte que os próprios
actors leem. O que os actors dão a mais é exactamente uma coisa: **o criativo em
pixels**, tirado da página de snapshot por navegador ou por JSON embutido —
rotas que nenhuma documentação garante.

```
COMPRAR AD LIBRARY POR ITEM QUANDO A ROTA OFICIAL É GRATUITA E COBRE A ITÁLIA
É PAGAR PELA DIFERENÇA ENTRE «NÃO TER CONFIRMADO A IDENTIDADE» E «TER».
```

### O quadro da PARTE 25, agora preenchido

| capacidade | rota actual | custo actual | substituto grátis | substituto local | gap pago | rota paga mais barata | poupança esperada |
|---|---|---|---|---|---|---|---|
| anúncios do concorrente | **nenhuma** | 0 | **Ad Library API** | — | **nenhum** | — | **não aplicável — não há gasto a cortar** |
| parcerias com creators | **nenhuma** | 0 | **`branded_content_search`** | — | **nenhum** | — | não aplicável |
| Threads do concorrente | **nenhuma** | 0 | **Threads API** (App Review) | — | **nenhum** | — | não aplicável |
| perfil e posts IG | janela pública, `ROUTE_NOT_ALLOWED` de facto | 0 | `business_discovery` (App Review) | — | histórico: `NÃO SEI` | — | não aplicável |
| texto de comentário IG | nenhuma | 0 | **não existe** | — | **real** | `apify/instagram-comment-scraper` $1,90/1 000 | não aplicável |
| posts e comentários FB | nenhuma | 0 | PPCA (App Review) | — | `AUTHORIZATION_BLOCK` | $1,40–$2,00 / 1 000 | não aplicável |
| Reels FB | nenhuma | 0 | **não existe** | — | **real** | `apify/facebook-reels-scraper` $3,16/1 000 | não aplicável |
| transcrição de Reel | ASR local | tempo de máquina | — | **já é local e provado** | nenhum | — | já poupado |
| legenda de vídeo FB | nenhuma | 0 | **SRT nativa** | — | nenhum | — | evita ASR inteiro |
| OCR · PDF · keyframes | nenhuma | 0 | — | **local** | nenhum | — | evita Actor |

```
A COLUNA «POUPANÇA ESPERADA» ESTÁ VAZIA DE PROPÓSITO, E A LEI DESTA CASA
OBRIGA: só se calcula percentagem quando há denominador real. O denominador
de Meta é `NOT_PRESERVED`.
```

---

## PARTE 29 · PRIORIDADES

### P0 — alto valor, oficial ou grátis, risco baixo

| # | o quê | por quê | o que custa |
|---|---|---|---|
| **P0.1** | **Declarar o vocabulário de ANÚNCIO** na matriz e nas capacidades | hoje a palavra não existe. Sem ela nenhuma rota de Ad Library pode sequer ser registada | uma missão de vocabulário, zero rede |
| **P0.2** | **Corrigir a linha `INSTAGRAM/FETCH_COMMENTS`** da matriz | o motivo declarado (`FREE_ROUTE_INSUFFICIENT_CAPABILITY`) está contradito pela medição da própria casa. O motivo correcto é `FREE_ROUTE_UNAVAILABLE` — não há rota oficial | edição de uma linha e da sua evidência |
| **P0.3** | **Corrigir os caminhos de evidência inexistentes** (`scripts/instagram_janela.py`, `scripts/instagram_transcrever.py`) | a matriz cita ficheiros que não existem, em linhas marcadas `PROVED` | edição |
| **P0.4** | **Rebaixar os dois `PROVED` de Apify do Instagram** | zero runs registados. `PROVED` sem artefato é o item 11 do red team dentro de casa | edição, com a medição citada |
| **P0.5** | **Declarar `THREADS` em `scrap_capacidades.py`** | há política e `NÃO HÁ` capacidade. A inversão do X, e o mesmo remédio | declaração, sem rota |
| **P0.6** | **Acrescentar a cláusula §3.2 dos ToS** à evidência da decisão da C10.5D | a decisão apoia-se no `robots.txt`; a cláusula é mais forte e cobre FB e IG juntos | edição de evidência |
| **P0.7** | **`handle → page_id`** para as 10 Páginas do lote | é o primeiro degrau de qualquer rota de Ad Library, e a casa não o tem | uma missão pequena |

```
OS SETE SÃO DE PAPEL E DE VOCABULÁRIO. NENHUM TOCA A REDE DA META.
NENHUM GASTA. E SEM ELES NENHUMA ROTA PODE SER LIGADA SEM MENTIR.
```

### P1 — alto valor, precisa de prova ao vivo

| # | o quê | o que a prova decide |
|---|---|---|
| **P1.1** | **Ad Library API** — confirmação de identidade, app, token | é a maior rota oficial da família e a casa nunca a tocou |
| **P1.2** | **`branded_content_search`** | descobre parceria de concorrente com creator. **`AUTH` é `NÃO DOCUMENTADO`** e só um probe responde |
| **P1.3** | **Threads `profile_posts` + `keyword_search`** | as três portas oficiais existem; falta App Review, e falta saber se é concedida |
| **P1.4** | **oEmbed sem token** (desde 2026-06-15) | é a única superfície oficial sem token, sem cookie e sem login do censo inteiro |
| **P1.5** | **`business_discovery`** | exige conta Business/Creator própria + 3 permissões com App Review. É a rota oficial de IG |
| **P1.6** | **PPCA** | é a rota oficial de FB, e a comunidade não tem um único relato de concessão em 2025/2026 |

### P2 — pago residual, e é curto

```
P2.1  texto de comentário do Instagram    $1,90 / 1 000, só como ENRICH
P2.2  Reels de Página do Facebook         $3,16 / 1 000, só se PPCA não cobrir
P2.3  posts e comentários de FB           SÓ enquanto PPCA não sair, e com
                                          motivo `AUTHORIZATION_BLOCK` escrito
```

### NO-GO — funciona e não devemos adoptar

| rota | por quê |
|---|---|
| endpoint interno do Instagram (`i.instagram.com`, `/api/v1`, `graphql/query`) | a lei desta casa já o proíbe em `story_local.py`; e os ToS §3.2 cobrem-no |
| qualquer rota com sessão logada contra terceiro | `LOCAL_SESSION contra TERCEIRO = NOT_USABLE`, lei desta casa |
| actors que declaram **stealth**, **fingerprint** ou **rotação de proxy residencial** | a missão listou os três como não autorizados. Comprar o resultado não os autoriza |
| **Selenium sobre `ad_snapshot_url`** para arrancar o criativo | a Meta escreve *«you cannot currently download a batch of archived ads»* |
| `metatargetr` e `scrapfly-scrapers` como dependência | declaram evasão de anti-bot no README |
| clientes não-oficiais de Threads | os três foram desligados pelos autores após contacto da Meta |
| persistir `ad_snapshot_url` como veio | carrega token na query string |

### E a hipótese não vinculante do briefing, medida

```
briefing: «P0 provavelmente deve incluir Meta Ad Library, Branded Content
Search, Threads official search, Instagram cheap recent window»

MEDIDO: as quatro são reais e VALIOSAS. Nenhuma é P0.
As quatro exigem credencial, aprovação ou identidade confirmada que esta casa
NÃO TEM — logo são P1, que é «alto valor, precisa de prova ao vivo».

E a quarta, «Instagram cheap recent window», é a única que a casa JÁ TEM e é
a única que a política desta casa JÁ RECUSOU.
```

    A HIPÓTESE ESTAVA CERTA SOBRE O VALOR E ERRADA SOBRE O DEGRAU. É a
    diferença entre `CAN DO` e `MAY DO`, e é a mesma diferença que esta casa já
    pagou para aprender no YouTube.

---

## PARTE 30 · PROBES — preparadas, nenhuma executada

```
META_PLATFORM_PROBES = 0
APIFY_RUNS = 0 · PAID_RUNS = 0 · COST_USD = 0
```

Esta missão **não tocou em nenhum host da Meta**, nem sequer para ler
`robots.txt`. A C12 considerou a leitura de `robots.txt` legítima e não-probe; a
instrução desta missão é mais apertada e ganha.

Cada probe abaixo tem tecto de rede e tecto de gasto, e os dois já existem no
executor (`teto_de_rede=`, `teto_de_gasto=`), portanto não é promessa.

| # | PROBE | TARGET | REQUESTS | AUTH | EXPECTED_BYTES | MAX_COST | O QUE PROVA |
|---|---|---|---|---|---|---|---|
| **0** | `robots.txt` dos hosts Meta | `facebook.com` · `instagram.com` · `graph.facebook.com` · `graph.threads.net` | **4** | nenhuma | < 40 KB | $0 | se a API oficial vive num host com regra diferente da do site |
| **1** | Ad Library, uma página | `ads_archive` · `ad_reached_countries=['IT']` · `search_page_ids=[1741459832625091]` · `limit=5` | **1** | token após confirmação de identidade | < 200 KB | $0 | **se a rota devolve anúncio comercial italiano de concorrente real** |
| **2** | Branded Content, uma consulta | `branded_content_search` · `ig_username=bayer_italia` · janela de 30 dias | **1** | **`NÃO DOCUMENTADO` — o probe descobre qual** | < 100 KB | $0 | **qual token o nó aceita**, e se a marca aparece como `partner` |
| **3** | Rate limit da Ad Library | o mesmo de PROBE_1, repetido | **até 20** | idem | < 2 MB | $0 | o número que a doc da Meta não publica (erro 613) |
| **4** | Forma do `ad_snapshot_url` | um `ad_snapshot_url` de PROBE_1, **só cabeçalhos** | **1** `HEAD` | token embutido | < 5 KB | $0 | se renderiza sem sessão, e se o token expira com ele. **Nenhum byte de mídia** |
| **5** | Threads, replies de terceiro | `/{media-id}/replies` sobre id vindo de `keyword_search` | **2** | `threads_basic` + App Review | < 100 KB | $0 | a única pergunta de Threads que a doc deixa em aberto |
| **6** | Campo `message` do nó Comment do FB | `/{page-post-id}/comments?fields=message,created_time` | **1** | PPCA | < 50 KB | $0 | resolve o `DOCUMENTADO-AMBÍGUO` da PARTE 17 |
| **7** | oEmbed sem token | `graph.facebook.com/v25.0/instagram_oembed?url=<post público do lote>` | **1** | **nenhuma** | < 20 KB | $0 | se a mudança de 2026-06-15 vale para nós, e o que devolve |
| **8** | Tabela de formatos de Reel, **sem baixar** | `-F` sobre 5 Reels do lote | **5** | nenhuma | < 500 KB | $0 | **quantos dos 5 têm linha `audio only`** — a correcção da PARTE 13 |

```
NENHUMA FOI EXECUTADA. PROBE_1 a PROBE_6 exigem credencial que a casa NÃO TEM.
PROBE_0, PROBE_7 e PROBE_8 são executáveis hoje — e PROBE_8 esbarra na decisão
da C10.5D, que recusa sair para a superfície do Instagram.
```

    E É POR ISSO QUE PROBE_0 É A PRIMEIRA: se `graph.facebook.com` publicar
    regra diferente de `instagram.com`, a distinção entre «a API oficial» e «o
    site» deixa de ser argumento e passa a ser medição.

---

## RED TEAM — os 25 ataques, respondidos

| # | ataque | veredito |
|---|---|---|
| 1 | Ad Library UI ≠ API | **SEPARADO.** UI tem comercial mundial activo; API não devolve nenhum fora da UE/UK. Tabela na PARTE 5 |
| 2 | campo da UE vira global | **SEPARADO.** Dois eixos: dinheiro é só-político mundial; segmentação e alcance são só-UE/UK. Contrato tem `FIELD_SCOPE` |
| 3 | anúncio actual vira histórico | **SEPARADO.** Comercial UE = **1 ano**; político = 7 anos. `ad_active_status` default `ACTIVE` declarado |
| 4 | snapshot vira criativo | **SEPARADO.** `ad_snapshot_url` é endpoint de renderização com token embutido. Contrato tem `SNAPSHOT_IS_NOT_CREATIVE` |
| 5 | branded content vira censo orgânico | **SEPARADO.** O índice só conhece o que traz rótulo de parceria paga |
| 6 | contagem de posts vira posts | **SEPARADO.** `media_count` ≠ itens colhidos. A casa já tinha a lei: «12 de 1.973» |
| 7 | contagem de comentários vira texto | **SEPARADO, e já tinha acontecido aqui**: o único RAW pago tem `commentsCount=31` e zero comentários |
| 8 | 12 recentes vira histórico | **SEPARADO.** 12 é tecto da rota pública; `business_discovery` não tem tecto documentado. **E 2026 contesta por baixo, não por cima** |
| 9 | metadados de Reel viram bytes de Reel | **SEPARADO.** `VIDEO_BYTES_DOWNLOADED = 0` nesta missão |
| 10 | extracção local de áudio vira áudio-only de rede | **SEPARADO — e corrigido.** Áudio-only é propriedade do **post**, não da plataforma. Só a linha `audio only` do `-F` prova |
| 11 | marketing de actor vira prova | **SEPARADO.** «100.0% runs succeeded» contra 42 618 timeouts na API da mesma plataforma |
| 12 | preço de actor sem carimbo | **CARIMBADO.** Todo preço deste documento traz `2026-09-12`. E `UPDATED` de actor oficial é `NÃO SEI` |
| 13 | existência de API oficial vira permissão | **SEPARADO — e apanhado dentro de casa**: `gap_apify()` diz «APIFY DISPENSÁVEL» citando rota que exige PPCA que não temos |
| 14 | App Review ignorado | **NÃO IGNORADO.** Cada rota oficial deste documento traz a sua exigência |
| 15 | PPCA e PPMA confundidos | **SEPARADOS** pela frase da própria doc. Tabela na PARTE 15 |
| 16 | development-mode tratado como produção | **SEPARADO, com duas provas documentais** — a de Threads (@meta, @threads, @instagram, @facebook) e a de FB (o admin da Página tem de ter papel no nosso app) |
| 17 | rota Graph vira acesso a concorrente sem prova | **SEPARADO.** `business_discovery` tem requisito **nos dois lados** e o alvo tem de ser Business/Creator |
| 18 | rota da conta própria do Threads vira rota pública | **SEPARADO.** As três portas de terceiro estão listadas à parte, na PARTE 18 |
| 19 | URL assinada vira permanente | **SEPARADO.** `MEDIA_URL_TTL = NÃO SEI`; a resposta é ler o `oe`, não decorar constante |
| 20 | SRT automática vira legenda humana | **SEPARADO, e a Meta já os separa**: `localized_creation_method` |
| 21 | legenda inexistente vira transcrição | **SEPARADO.** Instagram não serve faixa nenhuma; o resultado de ASR é `TRANSCRIPT_ASR` |
| 22 | API de anúncios vira monitorização orgânica | **SEPARADO.** `OBSERVATION_TYPE` no contrato; e a Ad Library não tem comentários nem reacções, por estrutura |
| 23 | índice de busca vira fonte Meta | **SEPARADO.** Nenhum número deste documento vem de motor de busca. As citações são da doc da Meta, do código, ou estão rotuladas `CLAIM` |
| 24 | varrimento histórico substitui delta | **INVERTIDO.** Com janela de 1 ano e sem cursor de «mudou desde», o delta é **requisito de existência** |
| 25 | enriquecimento caro corre em todos os itens | **É O COMPORTAMENTO ACTUAL.** Não há verbo `ENRICH`; `COLLECT` é tudo-ou-nada. Declarado na PARTE 23 |

---
## ENTREGA — META DEEP STUDY

### A · CURRENT SCRAP

```
INSTAGRAM_DECLARED = 7      INSTAGRAM_WIRED = 4 (2 com portão, 2 sem)
FACEBOOK_DECLARED  = 4      FACEBOOK_WIRED  = 0
THREADS_DECLARED   = 0      THREADS_WIRED   = 0
ADS_DECLARED       = 0      ADS_WIRED       = 0   — a palavra não existe no repositório
BRANDED_DECLARED   = 0      BRANDED_WIRED   = 0
```

### B · ADS

```
AD_LIBRARY_UI         = comercial activo no mundo inteiro, sem token, sem app
AD_LIBRARY_API        = comercial SÓ UE/UK; político mundial
COMMERCIAL_EU_HISTORY = 1 ANO a contar da última impressão
POLITICAL_HISTORY     = 7 anos — e sem inventário novo na UE desde 2025-10-06
ACTIVE_ADS            = `ad_active_status`, default ACTIVE
FIELDS                = 28 documentados, 4 por omissão. Para comercial italiano
                        volta texto de criativo por cartão, identidade da Página,
                        datas, plataformas, línguas, `eu_total_reach` EXACTO,
                        `beneficiary_payers`, `target_ages`, `target_gender`,
                        `target_locations` e `age_country_gender_reach_breakdown`
                        em CONTAGEM INTEIRA
NUNCA PARA COMERCIAL  = spend · impressions · currency · estimated_audience_size
                        demographic_distribution · delivery_by_region · bylines
MEDIA                 = NENHUMA. Só `ad_snapshot_url`, e o lote é proibido por escrito
COST                  = US$ 0. O preço é confirmação de identidade
```

### C · BRANDED CONTENT

```
AVAILABLE                  = SIM — `GET /branded_content_search`
POSTS · REELS · STORIES    = SIM (enum `type`: FB post · IG post · IG story · IG reel)
VIDEOS                     = listado pela Help Center; enum não o nomeia à parte
THREADS                    = NÃO COBERTO
SEARCHABLE_BY_COMPETITOR   = **SIM** — «or was a brand partner»
DEVOLVE                    = creator · partners · type · creation_date · url
NÃO DEVOLVE                = legenda · mídia · país · métricas · spend
HISTORY                    = piso 2023-08-17 · tecto «currently available»
AUTH                       = NÃO DOCUMENTADO → PROBE_2
```

### D · INSTAGRAM

```
PROFILE       = OFICIAL, `business_discovery` (3 permissões, App Review).
                Campos Public: biography · followers_count · id · media_count
                username · website. `follows_count`/`name`/`profile_picture_url`
                NÃO estão marcados Public → NÃO SEI
RECENT_POSTS  = 12 na rota pública (medido aqui, corroborado por tecto de actor).
                Pela rota oficial, sem tecto documentado
HISTORY       = NÃO DOCUMENTADO. O gap pode não existir
REELS         = OFICIAL — e `view_count` é EXCLUSIVO do Business Discovery
STORIES       = BLOCKED em todos os níveis. Não há endpoint
COMMENTS      = contagem SIM · **texto NÃO EXISTE em nenhum nível oficial**
MEDIA         = `media_url`, `thumbnail_url`. Durabilidade NÃO SEI
CAPTIONS      = só `caption` do autor. **Nenhuma faixa de legenda.**
                CAPTION ≠ TRANSCRIPT, e aqui o ASR é indispensável
RATE          = Platform Rate Limit, 200 × utilizadores por hora
```

### E · FACEBOOK

```
PAGE       = OFICIAL com PPCA ou PPMA. `fan_count` NÃO é campo livre
POSTS      = OFICIAL com PPCA. `/feed` é a edge canónica; `/posts` já não
             tem referência própria
HISTORY    = ~600 publicações por ano, EM RANKING. Máximo 100 por chamada
VIDEO      = OFICIAL com PPCA. **Reels da Página: SEM ROTA em nenhum nível**
COMMENTS   = PPCA abre a edge; o `id` é removido sob PPCA; e `message` NÃO
             consta da tabela de campos do nó Comment → DOCUMENTADO-AMBÍGUO
REACTIONS  = contagem provável; identidade barrada pela restrição de perfil
MEDIA      = OFICIAL com PPCA — **e legenda SRT nativa, com auto/manual separadas**
RATE       = 4800 × Engaged Users. A Página do concorrente não gera engajado
             para o nosso app → a doc manda usar token de SYSTEM USER
```

### F · THREADS

```
SEARCH    = `keyword_search`, corpus público desde 2023-07-05, filtrável por
            `author_username`. **Exige App Review de `threads_keyword_search`**
ACCOUNT   = `profile_lookup` — bio, seguidores, verificado, e métricas dos
            ÚLTIMOS 7 DIAS. Só perfis públicos com ≥100 seguidores
POSTS     = `profile_posts`, paginado por cursor, campos completos
MEDIA     = `media_url`. **TTL NÃO DOCUMENTADO** → tratar como efémero,
            ancorar no `permalink`
COMMENTS  = replies de TERCEIRO: NÃO DOCUMENTADO → PROBE_5
COST      = NÃO DOCUMENTADO. Não há página de preço
LIMITES   = 2 200 buscas/24 h · 1 000 pedidos de perfil/24 h · página máx. 100
```

### G · APIFY

```
ACTORS_REVIEWED       = 47   (18 IG · 15 FB · 7 Ad Library · 8 Threads)
MECANISMO DECLARADO   = 7    ·  PARCIAL = 3  ·  RECUSA = 1  ·  CAIXA PRETA = ~36
                             (os 20 oficiais `apify/*` são todos caixa preta)
INSTAGRAM_PAID_GAPS   = texto de comentário (real, e o único)
FACEBOOK_PAID_GAPS    = Reels de Página (real) · posts e comentários
                        (AUTHORIZATION_BLOCK, não falta de capacidade)
THREADS_PAID_GAPS     = NENHUM
ADS_PAID_GAPS         = NENHUM — a rota oficial é grátis e cobre a Itália
```

### H · OPEN SOURCE

```
REPOS_REVIEWED = 28
USEFUL_TECHNIQUES:
  1. RateController por CLASSE de pedido, em janela deslizante
  2. marca-d'água de progresso DESACOPLADA do artefato
  3. bloqueio como ESTADO NOMEADO, com retries configuráveis
  4. inventário ≠ aquisição — a tabela do que existe, à parte do que se baixou
  5. saneamento do segredo na borda de saída + validação de tipo na travessia
NO_GO_PART: endpoint interno, sessão logada, stealth, fingerprint,
            rotação de proxy residencial, Selenium sobre o snapshot
```

### I · VIDEO / AUDIO

```
CAPTION_FIRST            = SIM em toda a família. No ANÚNCIO é a rota inteira.
                           No FACEBOOK há SRT nativa. No INSTAGRAM não há faixa
AUDIO_ONLY               = POR ITEM, nunca por plataforma. Prova = linha
                           `audio only` na tabela de formatos daquele item
AUDIO_ONLY_NETWORK_SAVING= SIM quando o DASH do item traz AdaptationSet de áudio;
                           NÃO quando não traz. Medido nos dois sentidos
FULL_VIDEO_REQUIRED_WHEN = Instagram, item sem faixa DASH de áudio, e a
                           ferramenta pediu a fala. Em mais nenhum caso
BYTES BAIXADOS NESTA MISSÃO = 0
```

### J · COST

```
FREE_REPLACEABLE  = Ad Library · Branded Content · Threads · oEmbed sem token.
                    As quatro custam US$ 0 e nenhuma está ligada
LOCAL_REPLACEABLE = ASR · extracção de áudio · OCR · PDF · keyframes ·
                    detecção de idioma. Nenhuma justifica Actor
PAID_RESIDUAL     = texto de comentário IG ($1,90/1 000) ·
                    Reels de Página FB ($3,16/1 000) ·
                    posts/comentários FB enquanto PPCA não sair
UNKNOWN           = SINTONIA_HISTORICAL_ACTUAL_COST (META) = **NOT_PRESERVED**
                    → nenhuma percentagem de poupança é calculável
```

### K · COMPETITOR COVERAGE

```
ADS           = OFFICIAL (grátis, UE/Itália, 1 ano)
ORGANIC       = OFFICIAL (IG business_discovery · FB PPCA · Threads profile_posts)
REELS         = OFFICIAL no IG e no Threads · **BLOCKED no Facebook**
THREADS       = OFFICIAL, três portas
PARTNERSHIPS  = OFFICIAL — e é o achado da missão
COMMENTS      = BLOCKED no IG (texto) · AMBÍGUO no FB · NÃO DOCUMENTADO no Threads
MEDIA         = OFFICIAL no orgânico · BLOCKED no anúncio

FREE = NENHUMA CÉLULA.
```

### L · A ESCADA META RECOMENDADA

```
1  Ad Library API                    anúncio, criativo em texto, alcance UE exacto
2  branded_content_search            parceria com creator, dos dois lados
3  Threads: profile_posts + keyword_search + profile_lookup
4  Instagram business_discovery      perfil, posts, e `view_count` de Reel
5  Facebook PPCA                     feed, ~600/ano, e SRT nativa de vídeo
6  oEmbed sem token                  moldura de post único, sem credencial
7  ASR LOCAL                         só no Instagram, e só onde não há faixa
8  Apify, por item, com motivo escrito  texto de comentário IG · Reels de Página FB
```

    A ORDEM NÃO É DE FACILIDADE. É DE AUTORIZAÇÃO: do que a Meta publicou para
    ser lido, para o que ela deixa ler com aprovação, para o que ninguém deixa.

### M · PROBES NEEDED

```
PROBE_0  robots.txt dos quatro hosts Meta          4 pedidos · sem auth · $0
PROBE_1  ads_archive, uma página, IT               1 pedido  · identidade · $0
PROBE_2  branded_content_search, uma consulta      1 pedido  · AUTH DESCONHECIDA · $0
PROBE_3  rate limit da Ad Library                  ≤20       · identidade · $0
PROBE_4  HEAD no ad_snapshot_url                   1 HEAD    · token · $0
PROBE_5  replies de terceiro no Threads            2 pedidos · App Review · $0
PROBE_6  campo `message` do nó Comment do FB       1 pedido  · PPCA · $0
PROBE_7  oEmbed sem token                          1 pedido  · SEM AUTH · $0
PROBE_8  tabela de formatos de 5 Reels, sem baixar 5 pedidos · sem auth · $0
```

### N · BACKLOG

```
P0     P0.1 vocabulário de ANÚNCIO · P0.2 corrigir FETCH_COMMENTS ·
       P0.3 corrigir caminhos de evidência inexistentes ·
       P0.4 rebaixar os dois PROVED sem run · P0.5 declarar THREADS ·
       P0.6 juntar os ToS §3.2 à evidência da C10.5D · P0.7 handle → page_id
       — os sete são de papel. Nenhum toca a rede.

P1     Ad Library · Branded Content · Threads · oEmbed sem token ·
       business_discovery · PPCA

P2     comentário IG $1,90/1 000 · Reels FB $3,16/1 000 · FB enquanto não há PPCA

NO-GO  endpoint interno · sessão logada contra terceiro · stealth ·
       fingerprint · rotação de proxy · Selenium sobre snapshot ·
       clientes não-oficiais de Threads · persistir ad_snapshot_url com token
```

### O · APIFY RESIDUAL

| capacidade | por quê | actor | custo esperado |
|---|---|---|---|
| texto de comentário do Instagram | **não há rota oficial em nenhum nível**. Motivo canónico: `FREE_ROUTE_UNAVAILABLE` | `apify/instagram-comment-scraper` | $1,90 / 1 000 · só como ENRICH |
| Reels de Página do Facebook | `/page/video_reels` não suporta leitura em nenhum nível | `apify/facebook-reels-scraper` | $3,16 / 1 000 |
| posts e comentários do Facebook | PPCA não obtida. `AUTHORIZATION_BLOCK` | `apify/facebook-posts-scraper` · `apify/facebook-comments-scraper` | $2,00 e $1,40 / 1 000 |
| **anúncios** | — | **nenhum** | **$0 — a rota oficial cobre** |
| **parcerias** | — | **nenhum** | **$0** |
| **Threads** | — | **nenhum** | **$0** |

### P · O QUE MUDOU

```
1  A AD LIBRARY ENTROU NO MAPA. Antes não existia como palavra neste repositório
2  BRANDED CONTENT SEARCH É API PÚBLICA e busca pelo lado da marca.
   A hipótese do briefing era um talvez; é um facto
3  A JANELA COMERCIAL DA UE É UM ANO, não sete. O delta vira requisito
4  ÁUDIO-ONLY É PROPRIEDADE DO POST, não da plataforma. Corrige a leitura da C10
5  O FACEBOOK SERVE LEGENDA SRT E SEPARA AUTOMÁTICA DE HUMANA. O Instagram não
   serve nenhuma. A C6 ganha confirmação externa
6  O oEmbed DA META FICOU SEM TOKEN em 2026-06-15
7  A LINHA «APIFY NECESSÁRIA» DA NOSSA MATRIZ tem o motivo errado, e o ficheiro
   que ela cita como prova mede o contrário
8  DOIS `PROVED` DE APIFY NO INSTAGRAM não têm um único run
9  O LOTE CONGELADO NÃO TEM PAGE_ID, e a Ad Library pede-o
10 THREADS TEM POLÍTICA E NÃO TEM CAPACIDADE — a inversão exacta do X
11 OS ToS §3.2 DIZEM, POR ESCRITO, QUE ESTAR DESLOGADO NÃO É DEFESA
```

### Q · O QUE ESTÁ PROVADO

```
· o estado do SCRAP na Meta — executando o próprio código, sem rede
· que ADS e BRANDED CONTENT não existem neste repositório — por varredura
· que o único run pago de Meta desta casa trouxe 60 itens, normalizou 0,
  e tem custo NOT_PRESERVED — lido do manifesto
· que esse RAW tem `commentsCount = 31` e ZERO comentários — lido do ficheiro
· que a rota grátis desta casa já tirou 58% do texto de comentário — lido do código
· que a matriz cita dois caminhos de evidência que não existem — verificado
· que os cinco actors de Meta citados no código nunca correram — lido do ledger
· o escopo, os campos, as janelas e os limites da Ad Library, da Threads API,
  do Branded Content Search, do business_discovery e do PPCA/PPMA —
  citados da documentação primária da Meta, com URL
```

### R · O QUE CONTINUA `NÃO SEI`

```
· se a confirmação de identidade da Ad Library é concedida a esta casa, e em
  que países ela existe — a FAQ oficial carrega a resposta por JavaScript
· que token o nó `branded_content_search` aceita
· o número do rate limit da Ad Library — o erro 613 existe, o número não
· a profundidade máxima do `business_discovery` — não documentada
· se `follows_count`, `name` e `profile_picture_url` ainda voltam
· se `message` ainda é legível no nó Comment do Facebook sob PPCA
· se o PPCA ainda é concedido em 2026 — sem um único relato de comunidade
· se replies de terceiro respondem no Threads
· o TTL da URL assinada da CDN da Meta — a resposta é ler o `oe`, não decorar
· quantos Reels do lote têm faixa DASH de áudio separada
· quanto esta casa gastou de facto em Meta — `NOT_PRESERVED`, e é confissão
· o que o Reddit diria — cinco fóruns de praticantes ficaram por amostrar
```

### S · KNOW_HOW_DELTA

```
KNOW_HOW_DELTA = NENHUM
```

`SINTONIA-EAME-KNOW-HOW.md` **não existe nesta linhagem** — vive em
`claude/sintonia-eame-know-how-v1`, que não carrega o SCRAP. Escrever um delta
contra um ficheiro que a árvore de trabalho não contém seria fabricar uma
actualização que ninguém pode ler.

    A CANDIDATA A LEI, SE ALGUÉM A QUISER PROMOVER, É UMA SÓ:
    **UMA ROTA PAGA DECLARADA `PROVED` SEM UM ÚNICO RUN REGISTADO É UMA
    PROMESSA, NÃO UMA MEDIÇÃO.**
    Esta missão encontrou duas, e as duas são nossas.

---

## VEREDITO

```
META_DEEP_STUDY            = COMPLETO
META_PLATFORM_PROBES       = 0
APIFY_RUNS                 = 0
PAID_RUNS                  = 0
COST_USD                   = 0
ROTAS_IMPLEMENTADAS        = 0
POLICY_ALTERADA            = NAO
ADAPTERS_ALTERADOS         = 0
leis/social_matriz.py      = NAO TOCADO
ARTEFATOS                  = 3
```

A pergunta da missão era qual o máximo de actividade pública de concorrentes que
o SINTONIA SCRAP consegue observar na Meta. A resposta medida:

```
HOJE: NENHUMA. Zero capacidades de Meta gratuitas, permitidas e executáveis.
AMANHÃ: MUITO MAIS DO QUE ESTA CASA SUPUNHA — e por rotas que a Meta publicou
        de propósito para serem lidas, nenhuma delas conhecida por este
        repositório até hoje.
```

E a frase que resume o que esta missão realmente descobriu:

```
O SINTONIA NÃO ESTÁ A GASTAR DEMAIS NA META. ESTÁ A OBSERVAR DE MENOS, POR
ROTAS QUE NÃO PODE USAR, ENQUANTO AS QUE PODE USAR ESTÃO FECHADAS NUMA
GAVETA QUE NINGUÉM ABRIU.
```

**HARD STOP.** Nada foi implementado. Nenhuma rota foi ligada. Nenhuma política
foi alterada. Nenhum byte da Meta foi tocado.
