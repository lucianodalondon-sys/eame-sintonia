# META COMPETITOR COVERAGE V1 — o que conseguimos ver de um concorrente, hoje

```
MEDIDO_EM   = 2026-09-12
LOTE        = data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json
FROZEN_AT   = 2026-08-30
PROBES META = 0 · APIFY_RUNS = 0 · COST_USD = 0
```

> Documento irmão de [`META-DEEP-STUDY-V1.md`](META-DEEP-STUDY-V1.md) e de
> [`META-ROUTE-MATRIX-V1.json`](META-ROUTE-MATRIX-V1.json). Aquele mede as rotas;
> este mede **o concorrente**. Nenhum dos três é lei, e nenhum altera política.

---

## 1 · O CONCORRENTE NÃO É FICTÍCIO

A missão pedia um concorrente fixture. Esta casa tem um **lote congelado real**,
com regra de entrada escrita e data de congelamento. Medir contra um fictício
seria inventar um denominador quando já existe um.

```
ACCOUNTS ......... 22      FACEBOOK .. 10    INSTAGRAM .. 5
                          YOUTUBE ... 7     THREADS .... 0
BY_COUNTRY ....... ES 10 · IT 8 · FR 4
BY_COMPANY ....... SYNGENTA 8 · BAYER 7 · NUFARM 3 · BASF 3 · CORTEVA 1

CONTENT_COLLECTION_STAGE = NOT_STARTED
```

```
QUINZE CONTAS META CONGELADAS, ZERO CONTEÚDO COLHIDO, ZERO CONTAS DE THREADS.
```

E a regra do próprio lote diz por que isso importa:

> *«MISSION_IS_NOT_FINISHED_BECAUSE: falta conteúdo real. Identidade congelada
> não responde "sobre o que a empresa está falando" nem "o que mudou".»*

---

## 2 · O DEGRAU ZERO QUE NINGUÉM TINHA VISTO

A Ad Library pesquisa por `search_page_ids`, que pede **IDs numéricos de
Página**. O lote guarda `ACCOUNT_URL` e `ACCOUNT_HANDLE`.

```
campo PAGE_ID no esquema do lote ......... NÃO EXISTE
```

Varridas as dez URLs de Facebook:

| empresa | país | URL | id numérico |
|---|---|---|---|
| BASF | ES | `/BASF.Agro.Espana/` | — |
| BAYER | ES | `/Bayer4CropsES` | — |
| CORTEVA | ES | `/CortevaES` | — |
| SYNGENTA | ES | `/SyngentaES/` | — |
| SYNGENTA | FR | `/SyngentaFrance` | — |
| BAYER | IT | `/BayerCropScienceItalia` | — |
| NUFARM | FR | `/people/Nufarm-France/100088697208474/` | `100088697208474` ⚠️ |
| BASF | IT | `/BASF-Agricultural-Solutions-1741459832625091/` | `1741459832625091` |
| NUFARM | IT | `/Nufarm-Italia-2312073685546312` | `2312073685546312` |
| SYNGENTA | IT | `/Syngenta-2007689772789481` | `2007689772789481` |

```
4 DE 10 TÊM NÚMERO NA URL. 6 DE 10 NÃO TÊM.
```

⚠️ E o de Nufarm França vem de uma URL `/people/`, que aponta para **perfil**,
não Página. Um `page_id` que talvez não seja um `page_id` é pior que nenhum.

    O PRIMEIRO PASSO DE QUALQUER ROTA DE AD LIBRARY É `handle → page_id`, E
    ESTA CASA NÃO O TEM. É o mesmo degrau que a C3 teve de resolver no YouTube,
    e pela mesma razão: o lote guarda endereços, a API pede identificadores.

A alternativa é `search_terms` por nome — 100 caracteres, **sem tradução**, em
italiano para a Itália. Funciona, e é mais fraca: nome de empresa não é
identidade provada, e o lote inteiro existe porque esta casa recusou identidade
por busca de nome.

---

## 3 · A MATRIZ DE COBERTURA

```
FREE      grátis, permitido e executável HOJE
OFFICIAL  a rota oficial existe; falta credencial, aprovação ou identidade
PAID      só por rota paga
BLOCKED   medido e recusado, ou sem rota em nenhum nível de aprovação
UNKNOWN   não documentado — e NÃO DOCUMENTADO não é NÃO
```

| | ADS | ORGANIC | REELS | THREADS | BRANDED | COMMENTS | MEDIA |
|---|---|---|---|---|---|---|---|
| **INSTAGRAM** | — | `OFFICIAL` | `OFFICIAL` | — | `OFFICIAL` | **`BLOCKED`** (texto) · `OFFICIAL` (contagem) | `OFFICIAL` |
| **FACEBOOK** | — | `OFFICIAL` | **`BLOCKED`** | — | `OFFICIAL` | `UNKNOWN` | `OFFICIAL` |
| **THREADS** | — | `OFFICIAL` | `OFFICIAL` | `OFFICIAL` | **`BLOCKED`** | `UNKNOWN` | `OFFICIAL` |
| **AD LIBRARY** | `OFFICIAL` | — | — | — | — | **`BLOCKED`** | **`BLOCKED`** |

```
NENHUMA CÉLULA É `FREE`.
```

Não há **uma única** capacidade de observação de concorrente na família Meta que
esta casa possa executar hoje, gratuitamente e com permissão. Não é uma questão
de orçamento. É uma questão de credencial.

---

## 4 · AS ONZE PERGUNTAS DE NEGÓCIO, RESPONDIDAS UMA A UMA

### `NEW_ADS` — quais anúncios são novos

```
ROTA        graph:/ads_archive · ad_reached_countries=['IT'] · search_page_ids
COBERTURA   OFFICIAL · US$ 0 · janela de 1 ANO
ID          o campo é `id`, não `ad_archive_id` — esse é o nome do endpoint interno
DELTA       obrigatório. Não há cursor de «mudou desde»; a doc não oferece ordenação
            por data de lançamento. O delta é re-enumeração + diferença local.
PRECISA     handle → page_id para 6 das 10 Páginas
```

### `REMOVED_ADS` — quais deixaram de correr

```
COBERTURA   OFFICIAL, e é a pergunta mais fácil de responder ERRADO
COMO        ausência-na-recolha + carimbo de frescura próprio. A Meta NÃO emite
            sinal de remoção.
ARMADILHA   a API já foi observada a devolver `{"data":[]}` para Páginas cujos
            anúncios estão visíveis na UI.
```

```
«SUMIU DO RESULTADO» NÃO SE LÊ COMO «PAROU DE CORRER».
Uma regra de inactividade construída sobre ausência produz MORTES FALSAS —
e morte falsa de anúncio lê-se, lá em cima, como recuo do concorrente.
```

### `NEW_POSTS` — publicações orgânicas novas

```
INSTAGRAM   OFFICIAL · business_discovery{media} · 3 permissões com App Review
            profundidade: NÃO DOCUMENTADA
FACEBOOK    OFFICIAL · PPCA · ~600 por ano, EM RANKING, ≤100 por chamada
THREADS     OFFICIAL · profile_posts · paginado por cursor, página ≤100
PAREDE REAL não é profundidade. É o rate limit: business_discovery corre sob
            Platform Rate Limit = 200 × utilizadores por HORA. Uma ferramenta
            interna tem 1 utilizador.
```

### `NEW_REELS`

```
INSTAGRAM   OFFICIAL · filtrar por media_product_type=REELS do lado do cliente;
            não há filtro de servidor documentado.
            E vem `view_count` — EXCLUSIVO do Business Discovery.
FACEBOOK    BLOCKED. `/page/video_reels` na secção Reading:
            «You can't perform this operation on this endpoint.»
            → é um gap pago REAL: apify/facebook-reels-scraper, $3,16/1 000
THREADS     OFFICIAL, via profile_posts
```

### `NEW_THREADS`

```
COBERTURA   OFFICIAL — e é a plataforma com as regras mais legíveis da família
LIMITES     2 200 buscas/24 h · 1 000 pedidos de perfil/24 h · página ≤100
            só perfis públicos com ≥100 seguidores
JANELA      keyword_search busca desde 2023-07-05, o dia zero do Threads
LOTE        ZERO contas de Threads no lote congelado
```

    A ROTA OFICIAL MAIS LIMPA DA FAMÍLIA APONTA PARA UMA PLATAFORMA ONDE ESTA
    CASA NÃO SABE SE OS CONCORRENTES SEQUER TÊM CONTA. Descobrir isso não custa
    um pedido à Meta: as contas de Threads herdam o username do Instagram.

### `NEW_PARTNERSHIPS` e `NEW_CREATORS`

```
ROTA        graph:/branded_content_search
BUSCA POR   ig_username OU page_url, «or was a brand partner» → pelo lado da MARCA
DEVOLVE     creator{id,name,url} · partners[] · type · creation_date · url
NÃO DEVOLVE legenda · mídia · país · métricas · spend
HISTÓRICO   piso 2023-08-17 · tecto «currently available»
AUTH        NÃO DOCUMENTADO → PROBE_2
COBRE       FB post · IG post · IG story · IG reel     NÃO COBRE: Threads
```

```
STORY PATROCINADO EXPIRA EM 24 H E O ÍNDICE SÓ GUARDA O QUE ESTÁ NO AR.
→ PARCERIA EM STORY É PRATICAMENTE INVISÍVEL RETROACTIVAMENTE.
```

    É a única das onze perguntas em que o delta diário não é economia: é a
    diferença entre ver e não ver.

### `NEW_VIDEO` e `MEDIA_ASSETS`

```
INSTAGRAM   media_url · thumbnail_url. Durabilidade: NÃO SEI — ler o `oe`
FACEBOOK    idem, com PPCA — E COM LEGENDA SRT NATIVA
THREADS     media_url. TTL NÃO DOCUMENTADO → tratar como efémero, ancorar no permalink
ANÚNCIO     BLOCKED. Só `ad_snapshot_url`, e o lote é proibido por escrito
```

### `MESSAGE_TEXT`

```
ANÚNCIO     ad_creative_bodies · link_titles · link_descriptions · link_captions
            — LISTAS, uma entrada por cartão de carrossel. É a rota INTEIRA.
INSTAGRAM   `caption` — do AUTOR. NÃO É FALA. Aqui o ASR é indispensável.
FACEBOOK    `message` do post + legenda SRT nativa do vídeo
THREADS     `text`
```

### `PUBLIC_METRICS`

| | o que volta | o que NUNCA volta |
|---|---|---|
| **ANÚNCIO** | `eu_total_reach` (inteiro exacto) · `age_country_gender_reach_breakdown` (contagens exactas) | **gasto · impressões** — só político, e só em faixa |
| **INSTAGRAM** | `like_count` (omitido se escondido) · `comments_count` · `view_count` de Reel | `shares_count` · `saved_count` · qualquer insight |
| **FACEBOOK** | `reactions` e `shares` como contagem | identidade de quem reagiu · insights |
| **THREADS** | agregados de perfil dos **últimos 7 dias** | métrica por post |

```
`like_count` OMITIDO NÃO É ZERO. É AUSENTE DO JSON.
E MÉTRICA SEM HORA DE LEITURA É UMA AFIRMAÇÃO SOBRE O PRESENTE QUE ENVELHECE
EM SILÊNCIO.
```

### `COMMENTS`

```
INSTAGRAM   contagem: OFFICIAL · texto: NÃO EXISTE ROTA OFICIAL EM NENHUM NÍVEL
            → gap pago REAL: $1,90/1 000, e o motivo canónico é
              FREE_ROUTE_UNAVAILABLE, não FREE_ROUTE_INSUFFICIENT_CAPABILITY
FACEBOOK    PPCA abre a edge — mas o `id` é REMOVIDO sob PPCA, e `message` não
            consta da tabela de campos do nó Comment. DOCUMENTADO-AMBÍGUO
THREADS     replies de terceiro: NÃO DOCUMENTADO
ANÚNCIO     BLOCKED por estrutura — a Ad Library não tem comentários
```

---

## 5 · O QUE UM CONCORRENTE COMPLETO EXIGIRIA

Para uma empresa com Página de Facebook, conta de Instagram, conta de Threads e
um `page_id` de anunciante, a colheita mínima honesta:

| observação | rota | credencial que falta | custo |
|---|---|---|---|
| anúncios activos e retirados | `ads_archive` | identidade confirmada | US$ 0 |
| parcerias com creators | `branded_content_search` | **desconhecida** | US$ 0 |
| posts e Reels do Instagram | `business_discovery` | 3 permissões + App Review | US$ 0 |
| feed do Facebook | `/{page-id}/feed` | PPCA + Business Verification | US$ 0 |
| posts do Threads | `profile_posts` | `threads_profile_discovery` + App Review | US$ 0 |
| legenda de vídeo do Facebook | faixa SRT nativa | a medir | US$ 0 |
| transcrição de Reel do Instagram | ASR **local** | nenhuma | tempo de máquina |
| texto de comentário do Instagram | Apify | nenhuma | $1,90 / 1 000 |
| Reels de Página do Facebook | Apify | nenhuma | $3,16 / 1 000 |

```
SETE DAS NOVE CUSTAM ZERO DÓLARES. AS SETE ESTÃO FECHADAS POR CREDENCIAL.
AS DUAS QUE CUSTAM DINHEIRO SÃO AS DUAS QUE A META NÃO OFERECE DE TODO.
```

    E É ISTO O VEREDITO DA COBERTURA: o custo de observar a Meta não é o preço
    por item. É o trabalho de obter aprovação — e esse trabalho ainda não
    começou.

---

## 6 · O QUE ESTE DOCUMENTO NÃO FAZ

```
· não altera o lote congelado
· não colhe nada
· não liga rota nenhuma
· não altera leis/social_matriz.py
· não toca em Admission, Collection, Intelligence, Portal nem LIVE
· não produz uma única frase com adjectivo sobre um concorrente
```

E a fronteira que o mantém honesto:

```
SCRAP ENTREGA FACTOS OBSERVADOS, COM IDADE E COM PROVENIÊNCIA.
«CAMPANHA DE LANÇAMENTO», «ESTRATÉGIA AGRESSIVA» E «AMEAÇA COMPETITIVA»
SÃO INTELLIGENCE, E NÃO NASCEM AQUI.
```

**HARD STOP.**
