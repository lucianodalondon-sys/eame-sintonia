# YOUTUBE — ESTRADA OFICIAL (Data API v3)

> **Estado:** implementado e ligado. **Não executado contra a API** — falta a chave.
> Ver §CREDENCIAL. Nenhuma dependência nova. Nenhum coletor reescrito.

---

## 1 · O DEFEITO CORRIGIDO ANTES DE QUALQUER EXECUÇÃO

`social_sessao.usabilidade()` generalizava: **qualquer** `OFFICIAL_API` saía `ALLOWED`.
Reproduzido antes do conserto, e pior do que o red team descreveu — **os cinco casos
saíam `USABLE`, inclusive uma capacidade que não existe:**

```
YOUTUBE  FETCH_TRANSCRIPT           declarada=True   -> USABLE   (a matriz diz PERMITIDA=NAO)
LINKEDIN FETCH_POST                 declarada=True   -> USABLE   (não há rota OFFICIAL_API)
TIKTOK   SEARCH_KEYWORD             declarada=False  -> USABLE
YOUTUBE  CAPABILITY_QUE_NAO_EXISTE  declarada=False  -> USABLE
```

**Correção:** a política passou a consultar `social_matriz`, que é o **dono único** da
verdade de capacidade. Nada foi duplicado: nasceram `capacidade_declarada()` e
`rota_declarada()` na própria matriz, e a política pergunta a ela.

```
API OFICIAL EXISTIR NÃO É ESTA CAPACIDADE EXISTIR.
```

Depois do conserto — **cinco `NOT_USABLE`, e cada um com um motivo diferente**:

| Caso | ROUTE_STATUS | TECHNICAL_STATUS |
|---|---|---|
| YOUTUBE · FETCH_COMMENTS | `NOT_USABLE` | `CREDENTIAL_MISSING` |
| YOUTUBE · FETCH_TRANSCRIPT | `NOT_USABLE` | `ROUTE_NOT_ALLOWED` |
| LINKEDIN · FETCH_POST | `NOT_USABLE` | `ROUTE_NOT_DECLARED` |
| TIKTOK · SEARCH_KEYWORD | `NOT_USABLE` | `CAPABILITY_NOT_DECLARED` |
| YOUTUBE · capacidade inexistente | `NOT_USABLE` | `CAPABILITY_NOT_DECLARED` |

**Um `NÃO` genérico teria escondido quatro problemas diferentes.**

### A ordem do veredito

```
CAPACIDADE DECLARADA?  ->  ROTA DECLARADA PARA ESTE AUTH MODE?  ->  TERMOS PERMITEM?
->  ROTA SAUDÁVEL?  ->  TEM CREDENCIAL?  ->  CABE NA QUOTA?  ->  SÓ ENTÃO EXECUTE.
```

`UNKNOWN` nunca vira `SIM`.

### Um segundo defeito, achado pelo teste 13

O teste "Apify não é chamada quando a oficial está sã" reprovou por outro motivo:
`_rota_padrao` ordenava **só por preço**, e escolhia `youtube:oembed` —
**`CONDICIONAL`**, e que devolve só título, autor e thumbnail — na frente do
`videos.list` oficial, que é **`SIM`**. Isso contradiz a lei da casa.

Corrigido: `PERMITIDA → BARATA → PROVADA`, nessa ordem.
**Impacto medido em toda a matriz: exatamente 1 rota padrão mudou** — a certa.

---

## 2 · RECUPERAÇÃO — `AUTH_EXPIRED` não é uma coisa só

Medido antes de decidir: **`falhas.rotaciona()` não tem nenhum consumidor em
produção.** Os cinco chamadores reais usam a tupla `ap.ROTACIONAM` direto. Por isso
a correção mínima foi **acrescentar uma coluna, não separar estados** — assim nada
muda de comportamento e a taxonomia não incha.

| Razão nativa | Estado | Recuperação | Máquina resolve? |
|---|---|---|---|
| `TOKEN_INVALID` / `TOKEN_EXHAUSTED` | `AUTH_EXPIRED` / `QUOTA_EXHAUSTED` | `ROTATE_CREDENTIAL` | **sim** |
| `SESSION_EXPIRED` / `LOGIN_WALL` | `AUTH_EXPIRED` | `HUMAN_RELOGIN` | não |
| `MFA_REQUIRED` | `AUTH_EXPIRED` | `HUMAN_MFA` | não |
| `CREDENTIAL_MISSING` | — | `HUMAN_PROVISION_CREDENTIAL` | não |
| `RATE_LIMITED` | — | `WAIT` | sim |
| `BLOCKED` | — | `CHANGE_ROUTE` | sim |
| `PARSER_DRIFT` | — | `NEEDS_HUMAN_FIX` | não |

`HUMAN_PROVISION_CREDENTIAL` é separado de `HUMAN_RELOGIN` porque mandam a pessoa
fazer coisas diferentes: um abre o Chrome, o outro abre o console da plataforma.

---

## 3 · QUOTA — DOIS BUCKETS, E SOMAR OS DOIS É ERRADO

**Correção de 2026-09-08.** A primeira versão deste adapter declarava
`search.list = 100 unidades` e dizia que uma busca custava 100× um
`playlistItems.list`. **Estava desatualizado — e a matriz desta casa já dizia o
contrário**: `social_matriz.py:146` registra *"1 unidade/chamada, bucket próprio de
100 buscas/dia"*.

> **A MATRIZ SABIA E O ADAPTADOR NÃO PERGUNTOU.**
> É o mesmo defeito da missão passada, do outro lado: lá a política decidia sem
> consultar a matriz; aqui o executor copiou um número em vez de ler o dono.

Conferido hoje na documentação oficial
([determine_quota_cost](https://developers.google.com/youtube/v3/determine_quota_cost)):

> *"The `search.list` and `videos.insert` methods have their own quota buckets."*
> *"Projects that enable the YouTube Data API have a default quota allocation of
> 100 `search.list` calls, 100 `videos.insert` calls, and 10,000 units per day
> combined for all other endpoints."*

| Bucket | Padrão do projeto | Métodos |
|---|---|---|
| **SEARCH** | **100 chamadas/dia** | `search.list` |
| **GENERAL** | **10.000 unidades/dia** | `videos.list` · `channels.list` · `playlistItems.list` · `commentThreads.list` · `comments.list` |

```
1 SEARCH CALL NÃO É 100 GENERAL UNITS.
4 buscas + 37 unidades NÃO são 41 de nada — são dois números.
```

**A conclusão prática não mudou, o motivo mudou.** A busca continua sendo o recurso
escasso — mas por serem **100 por dia**, não por serem caras. O `playlistItems.list`
cabe 10.000 vezes.

> **BUSCA DESCOBRE. PLAYLIST DE UPLOADS VIGIA.**

**Dois tetos por execução, independentes:** `YT_TETO_SEARCH_CALLS` (padrão **20** de
100) e `YT_TETO_GENERAL_UNITS` (padrão **2.000** de 10.000) — um quinto do dia.
Estourar um **não** fecha o outro. Uma execução não é o dia inteiro.

**`REMAINING` sai `UNKNOWN`**, sempre. A API não devolve saldo e ninguém leu o
Console. Um saldo inventado daria a alguém confiança para gastar contra um número
imaginado. `QUOTA_MODEL_VERSION = 2026-09-08:two-buckets` existe para que, quando o
Google mudar de novo, se saiba contra qual regra os números antigos foram medidos.

**`videos.insert` também tem bucket próprio, e é irrelevante:** esta casa nunca publica.

---

## 4 · UPLOADS PLAYLIST — ROTA OFICIAL, NÃO PALPITE

A primeira versão derivava `UC…` → `UU…`. Funciona na maioria dos canais, **não é a
rota documentada**, e pode divergir.

Agora: **`channels.list part=contentDetails` →
`contentDetails.relatedPlaylists.uploads`** — 1 unidade do bucket GERAL.

> **HEURÍSTICA NÃO SUBSTITUI A ROTA OFICIAL QUANDO A API JÁ DÁ O DADO CANÔNICO.**

`UC→UU` sobrevive como `uploads_derivado()` — o nome diz o que é — e só entra com
`permitir_derivado=True`, quando a rota oficial não respondeu. Mesmo então o
resultado sai carimbado `PROVENANCE = DERIVED_HINT:UC_TO_UU`, com aviso.
**A procedência viaja para o artefato**, ao lado do ID.

**A economia:** `uploads_playlist()` aceita um `cache` `{channel_id: {...}}`. Canal já
resolvido **não gasta unidade nenhuma**. Descobrir é o custo; vigiar não é. Por isso
descobrir 10 canais uma vez e vigiar todo dia cabe folgado em 10.000 unidades.

Canal pedido e não devolvido levanta `CanalNaoEncontrado` — **não é "canal sem uploads"**.

---

## 5 · O ADAPTER

`scripts/youtube_oficial.py` — **um route executor**, não um motor.

| Capacidade | Método | Bucket | Custo |
|---|---|---|---|
| `SEARCH_KEYWORD` | `search.list` | **SEARCH** | 1 chamada |
| `INCREMENTAL` | `channels.list` (1×/canal) + `playlistItems.list` | GENERAL | 1 unidade |
| `FETCH_VIDEO_METADATA` | `videos.list` | GENERAL | 1 unidade (até 50 IDs) |
| `FETCH_COMMENTS` | `commentThreads.list` + `comments.list` | GENERAL | 1 unidade/página |

`INCREMENTAL` usa `newest → until known`. `FETCH_COMMENTS` completa a thread quando
`totalReplyCount` excede as respostas do envelope, e registra `REPLIES_COMPLETED` e
`REPLIES_MISSING`.

### Três coisas que parecem a mesma e não são

```
FEATURE_DISABLED    o dono desligou os comentários. A fonte respondeu, a rota
                    funcionou, o nosso código funcionou — nada quebrou.
ZERO_RESULTS        respondeu, comentários ligados, ninguém comentou.
<erro canônico>     não conseguimos olhar.
```

**`FEATURE_DISABLED` é novo, e substitui um erro meu.** A versão anterior mapeava
`commentsDisabled → NOT_APPLICABLE`, e isso misturava duas coisas: *"a plataforma
não tem essa capacidade"* com *"tem, e está desligada neste vídeo"*.

Propriedades: **não é falha** · `SOURCE_HEALTH`, `ROUTE_HEALTH` e `EXECUTOR_HEALTH`
todos `HEALTHY` · `DEGRADES_SOURCE = false` · **não retentável** enquanto o dono não
reabrir · `NATIVE_REASON = commentsDisabled`.

> **Para o FIELD VOICES futuro isso não é detalhe.**
> Zero comentários é **ausência de fala observada**.
> Comentários desligados é **ausência de superfície de fala**.
> **Não são a mesma evidência**, e quem juntar as duas hoje apaga a diferença para
> sempre. Há teste que reprova se os dois estados colapsarem.

A API do YouTube devolve **403 para as três coisas mais diferentes que existem** —
quota acabou, chave inválida e comentário desligado. `RAZOES` lê a razão declarada
no corpo, nunca só o código.

## 4 · O COMENTÁRIO É EVIDÊNCIA

O texto vai para o artefato em `textOriginal` — como a pessoa digitou.
**Sem resumo, sem tradução por cima, sem correção, sem tirar gíria, emoji,
abreviação ou dialeto.** Há teste que reprova se qualquer pedaço sumir.

Preservados: `COMMENT_ID`, `PARENT_ID`, `IS_REPLY`, `VIDEO_ID`, `CHANNEL_ID`,
`AUTHOR_CHANNEL_ID`, `AUTHOR_DISPLAY_NAME`, `TEXT_ORIGINAL`, `TEXT_DISPLAY`,
`PUBLISHED_AT`, `UPDATED_AT`, `LIKE_COUNT`, URL, `RUN_ID`, `ROUTE`, `EXECUTOR`,
`COLLECTED_AT`.

`PARENT_ID` distingue topo de resposta — **a thread continua reconstruível sem
recoletar.** `UPDATED_AT` ao lado de `PUBLISHED_AT` é o que permite ver edição.

> **COMO O CAMPO FALA É O DADO. NÃO É RUÍDO.**
> Um dia isso vira FIELD VOICES, e o que faz aquilo valer é exatamente o que uma
> limpeza apagaria. **Nenhuma inteligência foi criada nesta camada.**

### Geografia não se adivinha

`COUNTRY_SCOPE=IT` é o recorte do **pedido**. `AUTHOR_LOCATION` sai `UNKNOWN`,
**sempre** — a API não devolve lugar de quem comentou. `regionCode=IT` molda o
**ranking** da busca e fica no RAW como parâmetro do pedido, nunca como propriedade
do objeto. E `defaultAudioLanguage=it` não vira `SOURCE_LOCATION`:
**italiano se fala fora da Itália.**

---

## 5 · CREDENCIAL E CUSTO

Chave em `YOUTUBE_DATA_API_KEY`, ambiente ou GitHub Secret. **Nunca no código.**
Ausente → `CREDENTIAL_MISSING`, e **isso não autoriza cair para scraping**.

Custo monetário: `COST_USD = 0.0`, com **base declarada**:
`COST_BASIS = QUOTA_GRATUITA_OFICIAL`. Quota gratuita precisa de base, não de silêncio.

`QUOTA_EXHAUSTED` (cota da credencial, **rotaciona**) segue separado de
`BUDGET_EXHAUSTED` (teto nosso, **não rotaciona**). Não há rotação automática de
projeto: seria política nova, e não foi decidida.

---

## 6 · A ECONOMIA, REPRODUZIDA

Recontado do acervo nesta missão — **bate com o informado**:

| Ator | Gasto | Execuções |
|---|---|---|
| `streamers~youtube-comments-scraper` | **US$ 7,73** | 10 |
| `streamers~youtube-scraper` | **US$ 4,47** | 15 |
| `pintostudio~youtube-transcript-scraper` | US$ 0,13 | 13 |
| `harvestapi~linkedin-profile-scraper` | US$ 0,48 | 1 |
| **TOTAL** | **US$ 12,81** | |

**YouTube = US$ 12,33 (96%). Comentários sozinhos = US$ 7,73 (60%).**

### O que esta missão ataca, por capacidade

| Capacidade | Gasto histórico | Rota oficial | Ataca? |
|---|---|---|---|
| COMMENTS | **US$ 7,73** | `commentThreads.list` | **sim** |
| DISCOVERY + METADATA | **US$ 4,47** | `search.list` · `videos.list` | **sim** |
| TRANSCRIPT | US$ 0,13 | **nenhuma permitida** | **não** |

**US$ 12,20 de US$ 12,81 (95%) passam a ter estrada oficial.**

> **Não dizer "o YouTube zerou a Apify".** `FETCH_TRANSCRIPT` continua fora:
> `captions.download` exige permissão de **editar** o vídeo e não serve terceiro,
> e as rotas de biblioteca passam por caminho `Disallow`. **Sem áudio permitido,
> não há transcrição** — e isso é limite de permissão, anterior ao Whisper.

---

## 7 · O PILOTO — O QUE FOI E O QUE NÃO FOI PROVADO

**Não há chave neste ambiente.** `YOUTUBE_DATA_API_KEY` está ausente, e as quatro
capacidades param em `CREDENTIAL_MISSING`. Isso é resultado, não erro.

**Provado de verdade** (`python3 scripts/social_scrap.py youtube`, e 25 testes com
transporte injetado): o caminho de decisão inteiro; a política contra a matriz;
a separação das três saúdes; paginação; completação de thread; parada no conhecido;
dedupe por `COMMENT_ID`; preservação do texto cru; contagem de quota; e que **falta
de chave não vira fallback para rota proibida**.

**Não provado:** volume real, latência, e o comportamento da API viva.
Um número de "comentários coletados" seria invenção — **não há nenhum.**

| Métrica | Valor |
|---|---|
| Comentários coletados | **0** — sem credencial |
| Chamadas à API | **0** |
| SEARCH_CALLS_USED | **0** de 100/dia (padrão do projeto) |
| GENERAL_UNITS_USED | **0** de 10.000/dia (padrão do projeto) |
| REMAINING | **UNKNOWN** — a API não devolve saldo |
| Custo | **US$ 0,00** |
| **Apify chamada** | **NÃO — nenhuma vez** |
| Apify evitada | **0 chamadas nesta execução** (nada foi coletado por nenhuma rota) |

> A economia de US$ 12,20 é **potencial e projetada**, não realizada.
> Ela se realiza na primeira coleta com chave.

---

## 8 · O QUE MUDOU EM 2026-09-08 (segundo red team)

| Achado | Correção |
|---|---|
| **5 declarações independentes de quota**, 2 com o modelo antigo | A regra `MÉTODO → BUCKET → CUSTO → LIMITE PADRÃO` mora agora **só** em `social_matriz` (`QUOTA_METODO`, `LIMITE_PADRAO_PROJETO`, `quota_de()`). O executor guarda a **mecânica** (contar, aplicar teto) e **pergunta ao dono na hora da chamada** — não a um espelho que pode envelhecer |
| `uploads_playlist()` caía para `UC→UU` em **qualquer** `Exception` | **Removido.** Não existe caminho automático até o palpite. Timeout, chave inválida, quota, canal inexistente e a nossa própria `KeyError` sobem como a falha que são |
| O palpite não exigia justificativa | `uploads_hint()` exige `porque` escrito, grava `WHY_DERIVED_HINT_USED`, e **recusa "a API falhou"** — isso descreve a falha, não justifica trocar fato por chute |
| Cache só em RAM | Checkpoint em disco por canal: `UPLOADS_PLAYLIST_ID`, `PROVENANCE`, `VIDEOS_CONHECIDOS`, `CHECKPOINT_ID`. A identidade é `(PLATFORM, CHANNEL_ID, CAPABILITY)` validada por `coleta_checkpoint.identidade_valida` — **a lei vem do módulo canônico, não é reescrita** |
| Handle italiano exigiria busca | `resolver_handle()` usa `channels.list?forHandle` — **1 unidade GERAL, zero busca** |

**Palpite guardado em disco não vira fato:** `cache_de_playlists()` só devolve o que
tem `PROVENANCE == OFICIAL`.

### Sobre o checkpoint — o que ele é e o que não é

`coleta_checkpoint.py` continua sendo o checkpoint canônico da casa, **e fala com
Postgres por `psql`**. A estrada gratuita do YouTube não tem banco no caminho, e
abrir um seria trocar de assunto. Então: **a lei vem de lá** (`identidade_valida`,
`hash_da_entrada`), **o armazenamento é o que o SCRAP já usa**. Quando houver banco,
isto migra sem mudar de semântica. **Não é um motor de checkpoint novo.**

---

## 9 · PRÓXIMO PASSO

1. **Provisionar `YOUTUBE_DATA_API_KEY`** como GitHub Secret. É a única coisa que
   separa este código de coletar. `HUMAN_PROVISION_CREDENTIAL`.
2. Rodar o piloto italiano: 5–10 canais, poucas buscas. Trocar `ESTADO` de
   `CREDENTIAL_MISSING` para `PROVED` na matriz **com evidência**.
3. Ligar `coleta_checkpoint` ao `INCREMENTAL` — hoje a parada no conhecido depende
   de `conhecidos` vir do chamador; o checkpoint é quem deve fornecê-lo.
4. **Depois de comentários, o próximo maior custo é `streamers~youtube-scraper`
   (US$ 4,47): descoberta e metadado.** Mesma chave, mesma missão.
