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

## 3 · O ADAPTER

`scripts/youtube_oficial.py` — **um route executor**, não um motor. Não decide se
pode rodar; recebe a permissão e executa, contando quota.

| Capacidade | Método | Quota | Papel |
|---|---|---|---|
| `SEARCH_KEYWORD` | `search.list` | **100** | descoberta — **cara** |
| `INCREMENTAL` | `playlistItems.list` | **1** | vigilância diária |
| `FETCH_VIDEO_METADATA` | `videos.list` | **1** (até 50 IDs) | metadado |
| `FETCH_COMMENTS` | `commentThreads.list` + `comments.list` | **1** por página | **a prioridade** |

> **`search.list` custa 100× `playlistItems.list`.**
> **BUSCA DESCOBRE. PLAYLIST DE UPLOADS VIGIA.**
> Usar busca para vigiar canal conhecido queima a quota do dia em 100 chamadas.

`INCREMENTAL` usa `newest → until known`: para no primeiro vídeo já coletado.
A playlist de uploads é derivada do `channelId` (`UC…` → `UU…`), **sem gastar quota**.

`FETCH_COMMENTS` completa a thread: quando `totalReplyCount` é maior que as respostas
que vieram no envelope, chama `comments.list(parentId=…)` até fechar, e registra
`REPLIES_COMPLETED` e `REPLIES_MISSING`.
**O envelope inicial não garante a conversa inteira.**

### Três coisas que parecem a mesma e não são

```
COMMENTS_DISABLED   o dono desligou. A fonte RESPONDEU — é fato sobre o vídeo.
ZERO_LEGITIMATE     respondeu, comentários ligados, ninguém comentou.
<erro canônico>     não conseguimos olhar.
```

A API devolve **403 para as três coisas mais diferentes que existem**: quota acabou,
chave inválida e comentário desativado. `RAZOES` lê a razão declarada no corpo,
nunca só o código.

---

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
| Quota usada | **0** unidades |
| Custo | **US$ 0,00** |
| **Apify chamada** | **NÃO — nenhuma vez** |
| Apify evitada | **0 chamadas nesta execução** (nada foi coletado por nenhuma rota) |

> A economia de US$ 12,20 é **potencial e projetada**, não realizada.
> Ela se realiza na primeira coleta com chave.

---

## 8 · PRÓXIMO PASSO

1. **Provisionar `YOUTUBE_DATA_API_KEY`** como GitHub Secret. É a única coisa que
   separa este código de coletar. `HUMAN_PROVISION_CREDENTIAL`.
2. Rodar o piloto italiano: 5–10 canais, poucas buscas. Trocar `ESTADO` de
   `CREDENTIAL_MISSING` para `PROVED` na matriz **com evidência**.
3. Ligar `coleta_checkpoint` ao `INCREMENTAL` — hoje a parada no conhecido depende
   de `conhecidos` vir do chamador; o checkpoint é quem deve fornecê-lo.
4. **Depois de comentários, o próximo maior custo é `streamers~youtube-scraper`
   (US$ 4,47): descoberta e metadado.** Mesma chave, mesma missão.
