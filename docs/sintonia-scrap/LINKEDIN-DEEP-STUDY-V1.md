# LINKEDIN DEEP STUDY V1 — o raio-x profundo, e o que ele corrige

```
ESTUDO_DATADO_EM   = 2026-09-12
HEAD_MEDIDO        = 532e3bed6f8345cc380dcfacd7c2d1560878079b  (C10.8A-F)
LINKEDIN_REAL_REQUESTS = 0
LICDN_REQUESTS         = 0
APIFY_RUNS             = 0
COST_USD               = 0,00
POLICY_CHANGED         = NAO
ADAPTER_CHANGED        = NAO
MATRIZ_CANONICA_CHANGED = NAO
```

> Fotografia datada. Não é Bíblia, não é Master, não é contrato. Esta missão
> **mede e não integra**. Nenhuma rota foi ligada, nenhuma política foi mudada,
> nenhum byte saiu desta máquina em direção ao `linkedin.com` ou ao `licdn.com`.

---

## 0 · REGRA ZERO — o que a árvore diz, medido e não lembrado

```
CURRENT_BRANCH   = claude/festive-fermi-1k2mf5
CURRENT_HEAD     = df165da9  →  reposicionado sobre 532e3bed
REMOTE_HEAD      = origin/main @ df165da9  (2026-09-08)
WORKTREE_STATUS  = LIMPA
SCRAP_HEAD       = 532e3bed  origin/claude/sintonia-scrap-financial-budget-c10-8af
                   2026-09-12 14:43:18 +0000
DISTANCIA        = 320 commits entre origin/main e o HEAD real do SCRAP
```

O ramo de trabalho nasceu apontando para `origin/main`, que está **320 commits
atrás** do desenvolvimento do SCRAP. O estudo foi reposicionado sobre o HEAD
real antes de ler uma única linha.

    LER O SCRAP A PARTIR DE `main` TERIA MEDIDO UMA CASA QUE JÁ NÃO EXISTE.

### O primeiro achado, e ele é de arqueologia de ramo

O censo anterior do LinkedIn — `C11-LINKEDIN-CAPABILITY-DEEP-CENSUS.md`, 710
linhas, o trabalho mais completo que esta casa já fez sobre a plataforma —
**não está contido no HEAD do SCRAP.**

```
C11 vive em     origin/claude/sintonia-scrap-linkedin-deep-census-c11 @ 675b749b
divergiu em     231ffa2c  (C10.2)
contido em      1 ramo, e nenhum deles é a linha do SCRAP
C12 (X)         contido no HEAD.  C11 (LinkedIn)  NÃO.
```

O irmão dele, o censo do X, atravessou. O do LinkedIn ficou. Quem ler
`docs/sintonia-scrap/` no HEAD hoje vê `C12-X-CAPABILITY-DEEP-CENSUS.md` e
**não vê** o do LinkedIn.

    UM CENSO QUE NÃO ESTÁ NA LINHA É UM CENSO QUE A PRÓXIMA MISSÃO REFAZ.

Isto não é uma falha do C11 — é uma falha de topologia, e nomeá-la é metade do
conserto. O estudo abaixo herda o C11 **citando-o**, e corrige-o onde a
medição nova discorda.

---

## 1 · PERGUNTA 1 — O CENSO ATUAL, LIDO DO CÓDIGO

Não herdado. Corrido contra `scrap_capacidades` e `scrap_registo` no HEAD.

| capacidade | `DECLARED_STATE` | `PROOF` | `REGISTERED` | `HAS_EXECUTA` | `HAS_ROUTE` | `CURRENT_POLICY` | `CURRENT_OPERATIONAL` |
|---|---|---|---|---|---|---|---|
| `linkedin.recent.discovery` | **PROVEN** | `ESTADO-REAL-V1.md` | SIM | não | não | — (traduz `DISCOVER_ACCOUNT` → **ALLOWED**, mas por rota indireta) | `DECLARED_WITHOUT_ROUTE` |
| `linkedin.history.discovery` | UNKNOWN | `BENCHMARK-V1-FINAL.md` | SIM | não | não | `NOT_DECLARED` | `PROMISES_NOTHING` |
| `linkedin.direct_post` | **PROVEN** | `ESTADO-REAL-V1.md` | SIM | não | não | **`ROUTE_NOT_ALLOWED`** (`FETCH_POST`) | `DECLARED_WITHOUT_ROUTE` |
| `linkedin.native_video` | **PROVEN** | `ESTADO-REAL-V1.md` | SIM | não | não | `NOT_DECLARED` (`FETCH_VIDEO_BYTES`) | `DECLARED_WITHOUT_ROUTE` |
| `linkedin.native_caption` | **PROVEN** | `BENCHMARK-V1-FINAL.md` | SIM | não | não | `NOT_DECLARED` (`FETCH_TRANSCRIPT`) | `DECLARED_WITHOUT_ROUTE` |
| `linkedin.comments` | UNKNOWN | `BENCHMARK-V1-FINAL.md` | SIM | não | não | `NOT_DECLARED` | `PROMISES_NOTHING` |
| `linkedin.documents` | NOT_EXECUTED | `BENCHMARK-V1-FINAL.md` | SIM | não | não | `NOT_DECLARED` | `PROMISES_NOTHING` |

```
LINKEDIN_DECLARED = 7
LINKEDIN_WIRED    = 0      (0 de 7 têm `executa` OU `rota`)
LINKEDIN_LIVE     = 0
```

O LinkedIn é **a única plataforma da casa com capacidade declarada e nenhuma
executável.** As treze linhas de `reg.executaveis()` no HEAD são de Bluesky,
Instagram, Mastodon, Telegram e YouTube. Nenhuma é do LinkedIn.

### A política, corrida, não lembrada

`social_matriz.decisao('LINKEDIN', …)` para as doze capacidades grossas:

```
DISCOVER_ACCOUNT      ALLOWED             descoberta-indireta:site-da-organizacao
FETCH_POST            ROUTE_NOT_ALLOWED   2 rotas declaradas, nenhuma viável
os outros 10          NOT_DECLARED        nenhuma decisão existe
```

E `gap_apify()` devolve para o LinkedIn uma linha só:
`FETCH_POST · SEM ROTA PERMITIDA · nenhuma rota permitida, Apify inclusive`.

### O que MUDOU desde o C11 — e é uma correção a favor da casa

O C11 nomeou como gap #1 operacional o conflito `ATORES` × `social_matriz`:
havia um caminho de código alcançável (`fase_posts('LINKEDIN')` →
`executar_com_pool`) para uma rota que a política declara fora, e só faltava um
token de Apify para ele correr.

**Está fechado no HEAD.** `coleta/comunicacao_coleta.py` passou a perguntar
`mz.decisao(plataforma, 'FETCH_POST')` **antes** de tocar em `ATORES[…]`:

```
ROTA_NAO_AUTORIZADA=LINKEDIN/FETCH_POST
  decisao   ROUTE_NOT_ALLOWED
  APIFY_RUNS=0 · COST_USD=0 — nada saiu desta máquina.
```

    O PORTÃO DEIXOU DE CONFERIR O BILHETE DEPOIS DA VIAGEM.

`RISCO_RUNTIME_C11 = FECHADO`.

---

## 2 · PERGUNTA 2 — A SUPERFÍCIE PÚBLICA SEM LOGIN

Pesquisa documental. **Nenhum pedido saiu para o `linkedin.com`.** Tudo abaixo
é ou medição histórica preservada nesta casa, ou documentação de terceiros —
e as duas colunas estão separadas de propósito.

| superfície | `PUBLIC_WITHOUT_LOGIN` | `FIELDS` | `RECENT_DEPTH` | `PAGINATION` | `MEDIA` | `COMMENTS` | `REACTIONS` | `TIMESTAMP` | `EXACT_DATE` | `NETWORK_HOSTS` | `EVIDENCE` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| company page (landing) | **SIM** (histórico) | nome, descrição, morada, nº empregados, indústria, sede, ano, especialidades; `urn:li:activity:` no HTML | **10–13 ids** | **não exposta** («Show more» sem URL) | thumbs | não | não | relativo | não | `linkedin.com` | casa, 2026-09-08 |
| company `/posts/` | **NÃO** | — | — | — | — | — | — | — | — | — | casa: **HTTP 302 → `/uas/login`** |
| profile page | **parcial** | JSON-LD `Person`: nome, localidade, cargos, formação, foto | — | — | — | não | não | não | não | `linkedin.com` | Scrapfly, `ld+json` |
| profile posts | **NÃO** | — | — | — | — | — | — | — | — | — | documental |
| direct post URL | **SIM** (histórico) | HTTP 200, 114 KB, `<video data-sources>` | 1 item | n/a | **SIM** | não medido | não medido | sim | sim | `linkedin.com` + `dms.licdn.com` | casa, 2026-09-08 |
| people search | **NÃO** | — | — | — | — | — | — | — | — | — | redirect para `/uas/login` |
| jobs guest endpoint | **SIM** | vagas | paginado | **`?start=` offset, 10/página** | — | — | — | — | — | `linkedin.com/jobs-guest/…` | JobSpy, Scrapfly |
| **Ad Library** | **SIM, sem conta** | anunciante, criativo, datas, CTA, país, **faixa de impressões**, segmentação EEE (DSA) | desde **2023-06-01** | UI, **sem API** | criativo | não | não | sim | sim | `linkedin.com/ad-library` | documental |
| JSON-LD (`application/ld+json`) | **SIM** onde a página abre | `Person` · `Organization` | — | — | — | não | não | — | — | `linkedin.com` | Scrapfly |

### Os três estados de recusa, e eles não são o mesmo

```
302 → /uas/login    AUTHWALL         a porta existe e pede credencial
HTTP 999            REFUSAL/FLAG     código não-padrão do próprio LinkedIn
404                 HONESTO          o slug não existe — já mediu esta casa
```

Comunidade (evidência secundária, nunca prova): após ~50–60 pedidos anónimos de
perfil em 15 minutos, o IP passa a `999` em todos, com ou sem cookie; e o
convidado vê 2–3 perfis antes do authwall.

    999 NÃO É RECUSA DE POLÍTICA E NÃO É AUSÊNCIA DE DADO. É UM TERCEIRO
    ESTADO, E ESCREVÊ-LO COM A PALAVRA DOS OUTROS DOIS PERDE INFORMAÇÃO.

### O achado novo desta pergunta: a Ad Library

A `linkedin.com/ad-library` é uma superfície que **o próprio LinkedIn publica
para transparência**, nascida em 2023 para cumprir o DSA europeu, aberta sem
conta. Ela não serve conteúdo orgânico — serve **a comunicação paga do
concorrente**, com faixa de impressões e, no EEE, os parâmetros de segmentação
declarados.

Para um sistema que observa comunicação de concorrentes no agro europeu, isto é
um eixo que a casa nunca considerou. Não é conteúdo orgânico e não o substitui.

```
AD_LIBRARY_PUBLIC        = SIM, sem conta            (documental)
AD_LIBRARY_API           = NÃO EXISTE                (documental)
AD_LIBRARY_COVERAGE      = anúncios desde 2023-06-01; cada um fica 1 ano após
                           a última impressão
AD_LIBRARY_ROBOTS_STATUS = **NÃO MEDIDO NESTA MISSÃO** — ver PROBE_1
AD_LIBRARY_TERMS_STATUS  = §8.2 do User Agreement não abre exceção escrita
                           para esta superfície. DECISÃO HUMANA.
```

    UMA SUPERFÍCIE QUE A PLATAFORMA PUBLICA PARA SER LIDA POR GENTE NÃO É,
    POR ISSO, UMA SUPERFÍCIE QUE ELA AUTORIZA SER LIDA POR MÁQUINA.

---

## 3 · O ACHADO CENTRAL — O RAW QUE NINGUÉM TINHA ABERTO

Esta é a parte do estudo que corrige a casa, e ela custou zero: está no disco
desde 2026-08-29.

O C11 concluiu, em maiúsculas:

> «O PROVIDER QUE ESTA CASA REALMENTE RODOU NÃO DETECTA VÍDEO — QUANTO MAIS FALA.»

E fundamentou contando **dezanove campos** em `data/samples/ES-T8-002-posts.json`,
onde não há `video`, `media`, `caption`, `thumbnail` nem `duration`.

A contagem está certa. **O ficheiro é que é o errado.** Aquele é o ficheiro
NORMALIZADO. O bruto está ao lado, preservado e comprimido:

```
data/samples/raw-paid/ES-T8-002-linkedin-posts-a.raw.json.gz    84 466 B →  84 itens
data/samples/raw-paid/ES-T8-002-linkedin-posts-b.raw.json.gz   389 678 B → 388 itens
                                                               ─────────   ─────────
                                                               474 144 B    472 itens
```

E o RAW tem **26 campos de topo**, não dezanove. Entre eles:

| campo | posts | o que é |
|---|---:|---|
| `postVideo` | **56** | `{thumbnailUrl, videoUrl}` — **o endereço do MP4** |
| `document` | **20** | PDF, manifesto e **`transcriptManifestUrl`** |
| `article` | **93** | link externo, título, domínio, imagem |
| `newsletterUrl` | 10 | newsletter |
| `postImages` | 472 | imagens com dimensões |
| `engagement.reactions[]` | **449** | **agregado por TIPO de reação** |
| `repost` / `repostId` | 5 | repartilha |
| `shareUrn` / `entityId` | 472 | `urn:li:share:…` e o activity id |
| `query` | 472 | `{search, sortBy, page}` — **os parâmetros da busca** |
| `socialContent` | 472 | flags de ocultação e `shareUrl` |

```
C11_VIDEO_FINDING = CORRIGIDO
O provider DETECTA vídeo, e entrega o endereço dele em 56 dos 472 posts.
O que ele NÃO entrega é LEGENDA — e isso continua verdadeiro.
```

    O C11 MEDIU O FICHEIRO NORMALIZADO E ATRIBUIU A FALTA AO FORNECEDOR.
    A FALTA ERA DA NORMALIZAÇÃO DESTA CASA.

Isto não desqualifica o C11: o método dele estava certo — contar campos em vez
de ler o folheto. Errou o alvo, e o alvo certo estava na mesma pasta.

### O que a normalização deixou cair, item a item

Sobrevivem, renomeados: `content`→`TEXT`, `id`→`EXTERNAL_ID`,
`linkedinUrl`→`URL`, `postedAt`→`PUBLICATION_DATE`, `author`→`DECLARED_AUTHOR`
+`AUTHOR_URL`, `engagement.{likes,comments,shares}`→`LIKES`,`COMMENTS_COUNT`,
`SHARES`.

**Caem inteiros, sem equivalente:** `postVideo` · `document` · `article` ·
`newsletterTitle`/`newsletterUrl` · `postImages` · `engagement.reactions[]` ·
`repost`/`repostId` · `shareUrn` · `entityId` · `query` · `socialContent` ·
`contentAttributes` · `header` · `type`.

E caem 100 itens: 472 RAW → 372 normalizados, por duplicação de `POST_ID` entre
as 18 buscas. Essa parte está declarada no manifesto e é correta.

```
RAW_PRESERVED = YES.  E é por isso que este achado foi possível sem gastar
um cêntimo. A lei de preservar o bruto pagou-se hoje.
```

---

## 4 · PERGUNTA 3 — OS ACTORS, LIDOS EM 2026-09-12

Preço **de tabela**, lido nas páginas dos Actors em `2026-09-12`. Não é preço
pago por esta casa. Onde a casa pagou, está numa linha própria e marcada.

    `MEDIDO` = esta casa pagou e registou.   `TABELA` = lido na página hoje.
    `DOCUMENTED` = a página declara.  `INFERRED` = deduzido.  `UNKNOWN` = não sei.

| # | ACTOR | DEV | LOGIN/COOKIES | PRICE_MODEL | PRICE (tabela 2026-09-12) | DEPTH | COMMENTS | REACTIONS | VIDEO | CAPTIONS | DOCS | SRC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `harvestapi/linkedin-company-posts` | HarvestAPI | **não** | per-event | **US$ 1,50/1.000 posts** | `maxPosts:0` = tudo; `postedLimit`; **`postedLimitDate`** | opção, **cobrado à parte** | opção, à parte | «images, videos, documents with transcription URLs» | não declarado | sim | DOCUMENTED |
| 2 | `harvestapi/linkedin-profile-posts` | HarvestAPI | **não** | per-event | **US$ 1,50/1.000 posts** | idem | à parte | à parte | idem | não declarado | sim | DOCUMENTED |
| 3 | `harvestapi/linkedin-post-search` | HarvestAPI | **não** | per-event | **US$ 1,50/1.000 posts** | `maxPosts:0`; `postedLimit` até `year`; `postedLimitDate`; `startPage`/`scrapePages`; **teto declarado 400–500/consulta** | à parte | à parte | sim | não declarado | sim | DOCUMENTED |
| 4 | `harvestapi/linkedin-post-comments` | HarvestAPI | **não** | per-event | **US$ 2,00/1.000 comentários** | `maxItems:0`=tudo, até 100 páginas | **texto completo** | breakdown por tipo | — | — | — | DOCUMENTED |
| 5 | `harvestapi/linkedin-post-reactions` | HarvestAPI | **não** | per-event | **US$ 2,00/1.000 reações** | `maxItems:0` ≈ 1.218 | — | **lista de PESSOAS** | — | — | — | DOCUMENTED |
| 6 | `harvestapi/linkedin-company` | HarvestAPI | **não** | per-event | **US$ 3,00/1.000 empresas** | n/a | — | — | — | — | — | DOCUMENTED |
| 7 | `harvestapi/linkedin-profile-scraper` *(o que esta casa rodou)* | HarvestAPI | não | per-event | **US$ 4,033/1.000 — `MEDIDO`** (US$ 0,4840 / 120 perfis, 2026-08-29) | n/a | — | — | — | — | — | **MEDIDO** |
| 8 | `harvestapi/linkedin-profile-search` | HarvestAPI | não | per-event | UNKNOWN | — | — | — | — | — | — | UNKNOWN |
| 9 | `harvestapi/linkedin-company-employees` | HarvestAPI | não | per-event | UNKNOWN | — | — | — | — | — | — | UNKNOWN |
| 10 | `supreme_coder/linkedin-post` | supreme_coder | **não** | per-event | **US$ 2,00/1.000 posts** | `limitPerSource`; **`scrapeUntil`** (delta) | `numComments` | `numLikes` (perfis) | sim | não declarado | **`fetchDocumentDetails`: transcript + imagens de página** | DOCUMENTED |
| 11 | `apimaestro/linkedin-company-posts` | API Maestro | **não** | per-event | **US$ 5,00/1.000** | `page_number`, 100/página; **sem filtro de data** | contagem | contagem por tipo | «media attachments» | não | não declarado | DOCUMENTED |
| 12 | `apimaestro/linkedin-posts-search-scraper-no-cookies` | API Maestro | **não** | per-event | **US$ 5,00/1.000** | `page_number`, 50/página; `date_filter` | contagem | por tipo | media | não | não declarado | DOCUMENTED |
| 13 | `apimaestro/linkedin-post-reactions` | API Maestro | **não** | per-event | **US$ 5,00/1.000** | `page_number`, 1–100 | — | **lista de PESSOAS** + filtro por tipo | — | — | — | DOCUMENTED |
| 14 | `apimaestro/linkedin-post-comments-replies-engagements` | API Maestro | não | per-event | UNKNOWN | — | sim | sim | — | — | — | UNKNOWN |
| 15 | `apimaestro/linkedin-profile-posts` · `…-batch-profile-posts` | API Maestro | não | per-event | UNKNOWN | — | — | — | — | — | — | UNKNOWN |
| 16 | `capable_cauldron/linkedin-comment-scraper` | capable_cauldron | **SIM — cookies de sessão** | per-event | US$ 0,001/comentário + US$ 0,01/post | paginação automática | texto + respostas | — | — | — | — | DOCUMENTED |
| 17 | `bytepulselabs/linkedin-video-downloader` | bytepulselabs | não declarado | per-event | **US$ 0,006/arranque + US$ 0,06 por 10 MB** | n/a | — | — | **só o MP4** | **nenhuma** | — | DOCUMENTED |
| 18 | `silva95gustavo/linkedin-ad-library-scraper` | silva95gustavo | não declarado | rental | teste grátis 300 resultados | n/a | — | — | criativo | — | — | DOCUMENTED |
| 19 | `s-r/free-linkedin-company-finder` | s-r | não | per-event | **US$ 4,00/1.000 endereços** | n/a | — | — | — | — | — | DOCUMENTED |
| 20 | `dev_fusion/Linkedin-Profile-Scraper` (63 K users) | dev_fusion | não | per-event | UNKNOWN | — | — | — | — | — | — | UNKNOWN |
| 21–34 | `curious_coder/*`, `valig/*`, `worldunboxer/*`, `caprolok/*`, `anchor/*`, `scraping_solutions/*`, `code_crafter/*`, `get-leads/*` | vários | vários | per-event | UNKNOWN | — | — | — | — | — | — | UNKNOWN |

**34 Actors enumerados na loja; 13 com preço lido hoje; 1 com preço pago por
esta casa.**

### O que o marketing diz, e o que ele não prova

Onze dos treze dizem, em letra grande, «No cookies or account required». Um
deles acrescenta que opera «without … violating platform policies».

    ISSO É UMA AFIRMAÇÃO DO VENDEDOR SOBRE A POLÍTICA DE OUTRA EMPRESA.
    NÃO É UMA LICENÇA, E NÃO VINCULA O LINKEDIN.

`SOURCE_CODE_PUBLIC = NÃO` para todos os 34. `IMPLEMENTATION_DISCLOSED = NÃO`
para todos os 34.

### Mudança estrutural da Apify que afeta orçamento

Documental: a Apify **bloqueou Actors de aluguer novos em 2026-04-01 e retira
o modelo de aluguer em 2026-10-01**, migrando os existentes para
pay-per-usage. O `silva95gustavo/linkedin-ad-library-scraper` é de aluguer —
o preço dele **vai mudar dentro de três semanas**.

---

## 5 · PERGUNTA 4 — COMO OS ACTORS PARECEM FAZER

| ACTOR | mecanismo | classificação | base |
|---|---|---|---|
| família `harvestapi/*` | black-box | **UNKNOWN** | nenhuma linha de código pública |
| família `apimaestro/*` | black-box | **UNKNOWN** | idem |
| `supreme_coder/linkedin-post` | «hybrid backend routing (API-proxy e browser-proxy)» | **INFERRED: BROWSER + THIRD_PARTY_API** | frase da própria página, sem código |
| `capable_cauldron/linkedin-comment-scraper` | exige cookies exportados | **AUTHENTICATED_SESSION** | **DOCUMENTED** — a página pede o cookie |
| `bytepulselabs/linkedin-video-downloader` | resolve o post e devolve MP4 | **UNKNOWN** | — |
| `silva95gustavo/linkedin-ad-library-scraper` | «extrai de `linkedin.com/ad-library`» | **PUBLIC_HTML** | **DOCUMENTED** — a própria página nomeia a fonte |
| `s-r/free-linkedin-company-finder` | «Google-based search» + fontes terceiras | **SEARCH_ENGINE_INDEX** | **DOCUMENTED** |

    NÃO SE AFIRMA MECANISMO DE ACTOR BLACK-BOX. Dezasseis dos dezanove com
    preço conhecido ficam `UNKNOWN`, e `UNKNOWN` é a resposta, não a preguiça.

O único indício forte de mecanismo que esta casa tem **não veio da página de
nenhum Actor — veio do payload**. O RAW do `harvestapi~linkedin-post-search`
carrega `postedAgoText: "… • Visible to anyone on or off LinkedIn"` em **472 de
472** itens. É uma frase da interface do LinkedIn, não um campo de API.

```
INFERRED  o fornecedor lê uma superfície que RENDERIZA essa frase.
NÃO PROVA qual, nem com que credencial. Um render pode ser de convidado
          ou de sessão, e o texto é o mesmo nos dois.
```

---

## 6 · PERGUNTA 5 — OPEN SOURCE

| REPO | STARS | LAST_UPDATE | LANG | LOGIN | COOKIE | PUBLIC_ONLY | POSTS | COMPANIES | PROFILES | MEDIA | USEFUL_IDEA | PARTE NÃO PERMITIDA |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|
| `joeyism/linkedin_scraper` | 4 415 | 2026-04 | Python/Playwright | **SIM** | sessão | não | **sim** | sim | sim | não | modela «company posts» como entidade própria | login automatizado |
| `speedyapply/JobSpy` | 4 088 | 2026-02 | Python | **não** | não | **sim** | não | não | não | não | **guest endpoint paginado por `?start=`** — a forma de uma superfície que a plataforma abre de propósito | nenhuma (mas é só vagas) |
| `stickerdaniel/linkedin-mcp-server` | 3 115 | 2026-08 | Python/Patchright | **SIM** | sessão | não | sim | sim | sim | não | 19 ferramentas separadas por capacidade — o mesmo recorte desta casa | browser logado |
| `scrapfly/scrapfly-scrapers` (linkedin) | 1 062 | 2026-02 | Python | **não** | não | **sim** | **não** | sim | sim | não | **`application/ld+json` como superfície estruturada**; e a nota honesta de que o JSON-LD **omite campos** e é preciso ler o HTML ao lado | usa serviço pago de fetch gerido |
| `cullenwatson/StaffSpy` | 324 | 2025-06 | Python/Selenium | **SIM** | sessão | não | não | — | empregados | não | nomeia o endpoint Voyager que usa | **Voyager com sessão** |
| `tomquirk/linkedin-api` e derivados (`EseToni/open-linkedin-api`, `nsandman/*`, `alabarga/*`, `PipesNBottles/li_scrapi`) | — | vários | Python | **SIM** | sessão | não | sim | sim | sim | ? | **arquitetura do Voyager** — ver §7 | **login de credencial pessoal** |
| `josephlimtech/linkedin-profile-scraper-api` | 772 | 2024-04 | — | sim | sim | não | — | — | sim | — | — | abandonado |
| `linkedtales/scrapedin` | 612 | 2023-02 | — | sim | sim | não | — | — | sim | — | — | abandonado |

```
REPOS_REVIEWED = 12+
USEFUL_REPOS   = 2 sem login  (scrapfly · JobSpy)
```

    A IDEIA ÚTIL NÃO É O CÓDIGO. É A OBSERVAÇÃO DE QUE AS ÚNICAS DUAS
    FAMÍLIAS SEM LOGIN LEEM JSON-LD OU UM GUEST ENDPOINT — E NENHUMA DAS
    DUAS ALCANÇA POSTS DE EMPRESA.

Nenhum código foi copiado. Nenhuma licença foi assumida.

---

## 7 · PERGUNTA 6 — VOYAGER, COMO ARQUEOLOGIA DE SCHEMA

O que o frontend do LinkedIn sabe pedir, lido em documentação e em clientes
abertos — **não executado, não sondado**.

```
WHAT_EXISTS   /voyager/api/… com linguagem de consulta Rest-li própria
              (decoration + q=…), conceptualmente próxima de GraphQL.
              Exemplo público documentado, de organização:
              /voyager/api/organization/companies?decoration=(name,groups*~(…))
                &q=universalName&universalName=…
              Clientes abertos nomeiam ainda voyagerIdentityDashProfiles
              (perfis/empregados).

company feed · profile feed · post details · comments · reactions · media ·
documents · pagination
              → EXISTEM no vocabulário do frontend.
              → NENHUM tem endereço documentado por esta missão sem sessão.

REQUIRES_AUTHENTICATED_SESSION = SIM — sem exceção conhecida
CAN_BE_USED_CANONICALLY        = **NÃO**
EXPECTED                       = NO, e nada nesta missão o move
```

Três razões independentes, e fechar uma não abre a rota:

1. exige sessão autenticada, e §23 da casa proíbe login e cookie para contornar
   política;
2. é API **interna**, sem contrato — muda sem aviso e sem versão;
3. o §8.2 do User Agreement proíbe «override any security feature or bypass or
   circumvent any access controls».

    SER OPEN SOURCE NÃO TORNA UMA ROTA PERMITIDA. O CÓDIGO É ABERTO;
    A PORTA NÃO É.

---

## 8 · PERGUNTA 7 — DESCOBERTA SEM TOCAR NO LINKEDIN

Separando, como manda a casa: **descoberta de URL** ≠ **aquisição de conteúdo**.

| rota | `TECHNICALLY_USEFUL` | `CURRENT_POLICY` | `NEEDS_HUMAN_DECISION` |
|---|---|---|---|
| site oficial da organização (rodapé, «seguici su») | **SIM** — mede-se sem tocar no LinkedIn | **ALLOWED**, já declarada, `POSSIBLE_NOT_PROVED` | não |
| **`article.link` dos posts já preservados** | **SIM — 93 links externos no RAW** | conteúdo já colhido; o link é dado derivado | não |
| sitemaps / RSS / press releases da organização | SIM | fora da matriz do LinkedIn; é web aberta | não |
| Google/Bing/outros índices | SIM, tecnicamente | **CONFLITO**: §8.2(4) alcança informação obtida «through third parties (such as **search tools** or data aggregators or brokers)» | **SIM** |
| `s-r/free-linkedin-company-finder` (US$ 4/1.000) | SIM | **mesmo conflito** — a página declara «Google-based search» | **SIM** |
| reposts noutras plataformas | SIM | plataforma de destino decide | não |

    O ACTOR QUE «ENCONTRA O LINKEDIN A PARTIR DE QUALQUER SITE» NÃO É A ROTA
    QUE ESTA CASA PERMITE. A PERMITIDA LÊ O SITE DA ORGANIZAÇÃO. ELE
    PERGUNTA AO GOOGLE. §8.2(4) NOMEIA «SEARCH TOOLS» EM CLARO.

### O achado barato desta pergunta

Os 93 `article.link` no RAW preservado são endereços de **sites de terceiros e
das próprias organizações** — `teatronaturale.it`, `aimplas.es`, domínios de
cooperativas e institutos. São descoberta de fonte **já paga, já no disco, e
nunca usada**. Custo de aproveitá-los: **zero**.

---

## 9 · PERGUNTA 8 — EMPRESA CONHECIDA → POSTS RECENTES

| caminho | `REQUESTS_PER_COMPANY` | `POSTS_PER_REQUEST` | `BYTES_PER_COMPANY` | `USD_PER_1000_POSTS` | política |
|---|---|---|---|---|---|
| company page pública | **1** | **10–13** (medido 2026-09) | ~395 KB (medido, 1 amostra) | **US$ 0** | `DISALLOW_ALL` · `NOT_RUN` |
| post direto por URL | 1 por post | 1 | ~114 KB (medido, 1 amostra) | US$ 0 | `ROUTE_NOT_ALLOWED` |
| índice de busca | UNKNOWN | UNKNOWN | UNKNOWN | US$ 0 | §8.2(4) — **decisão humana** |
| `harvestapi/linkedin-company-posts` | 1 run | até `maxPosts` | **~1 005 B/post gz** (medido no RAW desta casa) | **US$ 1,50** (tabela) | `ROUTE_NOT_ALLOWED` |
| `apimaestro/linkedin-company-posts` | 1 run | 100/página | UNKNOWN | US$ 5,00 (tabela) | `ROUTE_NOT_ALLOWED` |

Os bytes por post são **medidos**, não estimados: 474 144 B comprimidos para
472 posts.

---

## 10 · PERGUNTA 9 — HISTÓRIA PROFUNDA, E A SURPRESA

A casa escreveu, e repetiu, que a maior lacuna do LinkedIn é **profundidade**,
com `linkedin.history.discovery = UNKNOWN` porque «"Show more" não expõe URL».

Isso é verdade **da página de empresa**. E a casa nunca reparou que o eixo que
ela já pagou é **outro**, e esse já alcançou quase nove anos:

```
os 472 posts preservados, por data de publicação:
  MAIS ANTIGO   2018-01-09T10:16:38.800Z
  MAIS RECENTE  2026-08-28T15:00:16.846Z
  JANELA        3 153 dias  =  8 anos e 7 meses
  PAGINAS USADAS  page = 1, em TODAS as 18 buscas
  sortBy          date
  postedLimit     "any"
```

| `DEPTH_SOURCE` | `PAGINATION_MECHANISM` | `LOGIN_REQUIRED` | `PAID_REQUIRED` | `INDEX_BASED` | `REAL_LINKEDIN_REQUEST` |
|---|---|---|---|---|---|
| company page (landing) | **nenhum exposto** — teto 10–13 | não | não | não | **sim** |
| **busca por palavra-chave, paga** | `page` + `sortBy` + `postedLimit` + `postedLimitDate`; teto declarado 400–500/consulta | não (declarado) | **sim** | UNKNOWN | UNKNOWN (black-box) |
| Posts API oficial | `start` + `count` (máx 100) + `sortBy` | **sim** | sim | não | sim — **mas só de organização que a casa administra** |
| Voyager | cursor interno | **sim** | não | não | sim |

```
A PROFUNDIDADE NUNCA FOI O PROBLEMA QUE A CASA PENSAVA.
A página de empresa é rasa. A BUSCA POR PALAVRA-CHAVE não é — e já entregou
8 anos e 7 meses, na página 1, numa corrida de 2026-08-29.
```

    `RECENT` E `HISTORY` NÃO SÃO O MESMO EIXO EM ROTAS DIFERENTES.
    SÃO EIXOS DIFERENTES, E A CASA MEDIU UM E CONCLUIU SOBRE O OUTRO.

O que isto **não** afirma: que a busca por palavra-chave cubra uma empresa
específica. Ela cobre um **termo**. Descobrir tudo o que a `Syngenta` publicou
é uma pergunta de eixo de autor; `postedLimit: any` sobre um termo técnico é
uma pergunta de tema. As duas são úteis, e não se substituem.

---

## 11 · PERGUNTA 10 — POST CONHECIDO: O QUE SE OBSERVA

`KNOWN_URL_ENRICHMENT` — medido no RAW preservado, por campo:

| campo | está na listagem? | precisa de chamada extra? |
|---|---|---|
| texto | **SIM** (`content`, 472/472) | não |
| autor (nome, URL, tipo, avatar, cargo) | **SIM** (`author`, 472/472) | não |
| data exata | **SIM** (`postedAt.date` ISO + `timestamp` ms) | não |
| likes · comments **count** · shares | **SIM** (`engagement`) | não |
| **tipos de reação agregados** | **SIM** (`engagement.reactions[]`, 449/472) | **não — já vem grátis na listagem** |
| hashtags | **SIM**, dentro do texto | não |
| link externo | **SIM** (`article`, 93/472) | não |
| imagens | **SIM** (`postImages` com dimensões) | não |
| **URL do vídeo** | **SIM** (`postVideo.videoUrl`, 56/472) | não |
| thumbnail do vídeo | **SIM** | não |
| **PDF do documento + manifesto de transcrição** | **SIM** (`document`, 20/472) | não |
| duração do vídeo | **NÃO** | — nenhuma rota conhecida |
| **legenda / SRT / WebVTT** | **NÃO — zero ocorrências em 472** | **sim, e sem rota permitida** |
| **texto dos comentários** | **NÃO — `comments: []` em 472/472** | **sim** (Actor de comentários, US$ 2/1.000) |
| lista de quem reagiu | **NÃO — `reactionIds: []` em 472/472** | sim (US$ 2–5/1.000) |

```
Termos procurados no RAW inteiro, em 472 posts:
  caption 0 · srt 0 · auto-caption 0 · acs-singleton 0 · audio 0 · duration 0
  ("subtitle" 95× e "transcript" 42× existem, mas são `article.subtitle`
   = o domínio do link, e `document.manifest.transcriptManifestUrl`
   = o texto do PDF. Nenhum dos dois é legenda de vídeo.)
```

    O RAW É GENEROSO EM TUDO MENOS NUMA COISA: FALA. E É EXATAMENTE A COISA
    QUE O SINTONIA MAIS PRECISA.

---

## 12 · PERGUNTA 11 — VÍDEO, A PRIORIDADE

Três observações independentes, **e não se colapsam numa**:

| # | observador | data | o que viu | TTL |
|---|---|---|---|---|
| A | esta casa, página pública | 2026-09-08 | **3 MP4 progressivos** (58/125/143 kbps) em `dms.licdn.com`, «não HLS, não DASH» | `e=2147483647` → **`LONG_LIVED_OBSERVED`** |
| B | **RAW `harvestapi`, preservado** | 2026-08-29 | **1 rendição**, `dms.licdn.com/playlist/vid/v2/<asset>/mp4-720p-30fp-crf28/…` | **`e=1788580800` → 2026-09-05T04:00:00Z, ≈7 dias → `TEMPORARY`** |
| C | artigo de terceiro (`dev.to`) | 2026 | **HLS** com `.m3u8` mestre + filhos por resolução, segmentos `.ts`/`.m4s`, e tokens (bearer estático do bundle JS + guest token via `activate.json`) | — |

```
AS TRÊS PODEM ESTAR CERTAS AO MESMO TEMPO: superfícies diferentes servem
formas diferentes, e o tempo entre elas é de dias.
```

    UMA URL `e=2147483647` NÃO É «PERMANENTE» E NÃO É A REGRA. A OUTRA
    OBSERVAÇÃO, NO MESMO MÊS, DEU SETE DIAS. A ESCALA CONTINUA A SER
    `TEMPORARY · LONG_LIVED_OBSERVED · DOCUMENTED_STABLE · UNKNOWN`, E
    O QUE ESTA MISSÃO ACRESCENTA É QUE **AS DUAS PRIMEIRAS JÁ FORAM VISTAS
    NA MESMA PLATAFORMA, NA MESMA SEMANA.**

Consequência dura para qualquer desenho futuro: **uma URL de mídia do LinkedIn
guardada num artefato pode estar morta em sete dias.** Guardar a URL não é
guardar a mídia.

### A escada conceitual, e onde ela parte hoje

```
1. NATIVE CAPTION          4 283 B medidos (2026-09, página pública)
                           ZERO ocorrências no RAW pago de 472 posts
                           →  a rota que a tem é `ROUTE_NOT_ALLOWED`
                              a rota permitida-em-tese não a entrega

2. AUDIO-ONLY REPRESENTATION   NÃO EXISTE em nenhuma evidência desta missão
                               (ver §14)

3. RANGE / STREAMING       sem manifesto conhecido na rota paga; a rendição
                           é uma só. NÃO MEDIDO.

4. FULL VIDEO              tamanho NUNCA MEDIDO por esta casa.
                           Referência de preço de terceiro:
                           US$ 0,06 por 10 MB baixados.

5. LOCAL ASR               `fala_local` existe e funciona. NÃO É O GARGALO.
```

```
CAPTION_BYTES = 4 283      (medido, 1 amostra, 2026-09, rota hoje fora)
AUDIO_BYTES   = UNKNOWN    (não existe representação separada conhecida)
VIDEO_BYTES   = UNKNOWN    (nenhum MP4 do LinkedIn foi baixado, nunca)
```

    CAPTION != TRANSCRIPT. E O QUE FALTA MEDIR É O DENOMINADOR: SEM
    `VIDEO_BYTES`, «A LEGENDA POUPA 99%» É UMA FRASE BONITA SEM CONTA.

`ASR_BLOCKED_BY_ACQUISITION = YES` — herdado do C11 e **confirmado**. O motor
de fala desta casa está bom e continua a não mover a fala do LinkedIn um
milímetro.

---

## 13 · PERGUNTA 12 — CAPTION-FIRST

```
CAPTION_PUBLIC   = SIM no histórico da página pública (2026-09-08); UNKNOWN hoje
LOGIN_REQUIRED   = não, na observação histórica
SIGNED_URL       = SIM — `e=` e `t=` no endereço
TTL              = UNKNOWN para a legenda (o `e=` da legenda não foi registado)
LANGUAGE         = 1 amostra, idioma não registado
AUTO_OR_HUMAN    = **AUTOMATIC**, por evidência de endereço:
                   `video-auto-caption-srt-acs-singleton`
SRT              = SIM — bytes verificados: `1\n00:00:00,220 --> 00:00:03,032\n`
                   numeração de sequência e VÍRGULA decimal
WEBVTT           = NÃO. A primeira escrita da casa dizia WebVTT e foi corrigida.
BYTES            = 4 283
```

O padrão `video-auto-caption-srt-acs-singleton` **não aparece em nenhum dos 472
posts do RAW pago**, nem em nenhuma página de Actor lida hoje. Ele existe numa
única observação desta casa, de uma superfície hoje declarada fora.

```
A URL HISTÓRICA NÃO PODE SER TESTADA: o `e=` dela não foi preservado, e
o padrão de sete dias visto em (B) torna provável que tenha expirado.
CAPTION_ROUTE_TODAY = **PRECISA MEDIR** — e a medição exige a rota proibida.
```

E a lei que fica, porque é durável:

    SRT AUTOMÁTICA É ASR DE OUTRA CASA. MAIS BARATA, NÃO MELHOR. E O
    ENDEREÇO — NÃO UM CAMPO DECLARADO — É A ÚNICA PROVA DE QUE É AUTOMÁTICA.

E a segunda, que esta missão acrescenta lendo a documentação oficial:

    O CAMPO `captions` DA API OFICIAL DE VÍDEO É A LEGENDA QUE O PRÓPRIO
    PARCEIRO SUBIU (`source: USER_PROVIDED`). ELE NUNCA FOI A LEGENDA
    AUTOMÁTICA DE UM POST DE TERCEIRO. SÃO DUAS COISAS COM O MESMO NOME.

---

## 14 · PERGUNTA 13 — AUDIO-ONLY

```
AUDIO_ONLY_RENDITION_IN_PAID_PAYLOAD = NÃO — `postVideo` tem 2 campos:
                                       `thumbnailUrl` e `videoUrl`. Nada mais.
                                       Zero ocorrências de "audio" em 472 posts.
AUDIO_ONLY_IN_OFFICIAL_API           = NÃO EXISTE (confirmado pelo C11 contra
                                       a Videos API; nada nesta missão o move)
AUDIO_ONLY_IN_PUBLIC_PAGE            = UNKNOWN — não sondado, rota fora
AUDIO_ONLY_NETWORK_ACQUISITION       = **NÃO OBSERVADO EM ROTA NENHUMA**
```

E a conta que a missão pede que não se assuma:

```
Se o MP4 é progressivo e de rendição única, extrair áudio por HTTP Range
exige ler os átomos do contentor espalhados pelo ficheiro. Sem manifesto e
sem índice, o pior caso aproxima-se do ficheiro inteiro.

AUDIO_ONLY_NETWORK_SAVING = **NÃO MEDIDO**, e por isso NÃO SE AFIRMA.
```

    EXTRAIR ÁUDIO LOCALMENTE DE UM RAW QUE JÁ EXISTE É ÚTIL E É OUTRA COISA.
    `LOCAL AUDIO EXTRACTION` != `NETWORK AUDIO-ONLY ACQUISITION`.
    A primeira poupa CPU e disco. A segunda pouparia rede — e ninguém provou
    que ela existe aqui.

---

## 15 · PERGUNTA 14 — COMENTÁRIOS: POR QUE OS ACTORS DISCORDAM

A discordância resolve-se, e a resposta é aborrecida: **eles fazem coisas
diferentes e cobram por isso.**

```
COMMENTS_PUBLIC  = a CONTAGEM sim; o TEXTO, em rota gratuita: NÃO OBSERVADO
CONDITIONS       = o texto é um EVENTO COBRADO À PARTE em todos os Actors
                   que o entregam; nenhum o inclui no preço da listagem
DEPTH            = `maxItems: 0` = tudo, até 100 páginas (harvestapi, tabela);
                   respostas aninhadas até 5 por comentário raiz, ilimitadas
                   se pedidas como item próprio
PAGINATION       = por `maxItems` / `page_number`, conforme o Actor
LOGIN_REQUIRED   = não, em 3 dos 4 Actors de comentários lidos hoje;
                   **SIM** em `capable_cauldron` — esse pede cookie de sessão
EVIDENCE         = payload preservado + páginas dos Actors, 2026-09-12
```

E a medição que fecha a pergunta, nesta casa, sem gastar nada:

```
comments (texto)  : []  em  472 de 472 posts
commentIds        : []  em  472 de 472 posts
engagement.comments (contagem) : soma = 335, distribuída por 95 posts
```

    `COMMENTS_COUNT = 335` E `COMMENTS_TEXT = 0`. O MESMO PAYLOAD DIZ AS
    DUAS COISAS, E QUEM LÊ SÓ A PRIMEIRA COLUNA ESCREVE «TEMOS COMENTÁRIOS».

O motivo pelo qual os Actors «discordam» não é região, nem A/B, nem tipo de
post. É **modelo de preço**: o campo existe sempre; ele vem vazio a menos que
se pague o evento.

---

## 16 · PERGUNTA 15 — REAÇÕES, EM TRÊS COISAS

| | `PUBLIC` | `EXTRA_REQUEST` | `LOGIN` | `COST` |
|---|---|---|---|---|
| **contagem** (`likes`) | **SIM — já na listagem** | **não** | não | **incluído** |
| **agregado por tipo** | **SIM — já na listagem, 449/472** | **não** | não | **incluído** |
| **lista de pessoas** | sim, por Actor dedicado | **SIM** | não (declarado) | US$ 2,00–5,00/1.000 |

Tipos observados no payload preservado, sem um pedido extra:

```
LIKE 448 · PRAISE 106 · INTEREST 69 · EMPATHY 50 · APPRECIATION 31
```

    O AGREGADO POR TIPO — QUE É O QUE DIZ SE A COMUNICAÇÃO GEROU INTERESSE
    TÉCNICO OU SÓ CORTESIA — JÁ ESTAVA PAGO, JÁ ESTAVA NO DISCO, E A
    NORMALIZAÇÃO DESTA CASA DEITOU-O FORA.

E a regra de negócio que daí sai:

    NÃO SE COLHE GENTE QUANDO O NEGÓCIO PRECISA DE CONTAGEM. A lista de
    pessoas é dado pessoal, custa mais, e responde a uma pergunta que o
    SINTONIA não faz.

---

## 17 · PERGUNTA 16 — DOCUMENTOS E CARROSSÉIS

Aqui está o segundo achado grande, e ele estava no mesmo ficheiro.

A casa declara `linkedin.documents = NOT_EXECUTED · «nunca tentado»`. O payload
preservado traz, em **20 dos 472 posts**, uma estrutura `document` completa:

```
document.title                          o título
document.totalPageCount                 2 a 17 páginas (mediana ~3)
document.transcribedDocumentUrl         .../feedshare-document-sanitized-pdf/...
document.manifestUrl                    .../feedshare-document-master-manifest/...
document.coverPages[].imageUrls[]       imagens de página
document.manifest.asset                 urn:li:digitalmediaAsset:...
document.manifest.transcribedDocumentUrl .../feedshare-document-pdf-analyzed/...
document.manifest.transcriptManifestUrl  .../feedshare-document-transcript/...
document.manifest.perResolutions[]       5 resoluções, cada uma com imageManifestUrl
document.manifest.scanRequiredForDownload = true
```

| eixo | resposta |
|---|---|
| `DIRECT_ASSET` | **SIM** — `transcribedDocumentUrl` aponta a um PDF |
| `PREVIEW_ONLY` | não — há PDF **e** imagens de página **e** manifesto de transcrição |
| `LOGIN_REQUIRED` | não declarado no payload |
| `DOWNLOADABLE` | **NÃO VERIFICADO** — `scanRequiredForDownload: true`, e nenhum byte foi pedido |
| `PAGES` | 2–17, declarado por item |
| `TEXT_EXTRACTABLE_LOCAL` | **SIM, e a casa já tem a cadeia**: `coleta/executor_texto_de_pdf.py` e `golden_path_pdf.py` existem e são o caminho canónico de texto de PDF |
| TTL | **DOIS `e=` diferentes no mesmo objeto**: o externo `e=1788580800` (7 dias) e o do manifesto `e=1788998400` (≈12 dias). Já expiraram os dois. |

```
UM POST DE CARROSSEL DO LINKEDIN É, ESTRUTURALMENTE, UM PDF COM TEXTO —
E ESTA CASA TEM UM EXECUTOR DE TEXTO DE PDF MADURO E PROVADO.
```

    «NUNCA TENTADO» ERA VERDADE SOBRE A REDE. NÃO ERA VERDADE SOBRE O DISCO:
    O ENDEREÇO DO PDF ESTAVA GUARDADO HÁ QUINZE DIAS.

E o limite, dito em voz alta: as URLs preservadas **expiraram**. Saber que o
campo existe não é ter o ficheiro. Para os bytes, é preciso uma corrida nova —
e uma rota permitida, que hoje não existe.

---

## 18 · PERGUNTA 17 — PERFIS, E O PESO QUE ELES TRAZEM

`data/samples/raw-paid/ES-T8-002-linkedin-profiles.raw.json.gz` — 202 itens,
**85 campos distintos**, 4,9 MB descomprimidos.

```
202 itens = 138 PESSOAS + 62 PÁGINAS DE EMPRESA + 2 outros
DISCOVERY_ROUTE: POST_SEARCH 115 · TITLE_SEARCH 87
```

Publicamente observável nesta amostra, por pessoa:

| campo | presente |
|---|---|
| nome, sobrenome, headline, foto, capa | 138/138 |
| localidade (texto + `countryCode` + parsed) | **138/138** |
| `connectionsCount` · `followerCount` | 138/138 |
| `experience` (cargos, empregadores, tipo de vínculo) | **135/138** |
| `education` | **118/138** |
| `skills` · `topSkills` | 121/138 |
| `openToWork` | 7 marcados `true` |
| `interests`, `moreProfiles` (perfis sugeridos) | presentes |
| `emails` | **0/202 não-vazio** — o modo pago corrido foi «no email» |

```
COMPANY MONITORING   ≠   PERSONAL PROFILE COLLECTION
E o que está no disco desta casa é, em 138 dos 202 registos, o SEGUNDO.
```

    GDPR — REGISTADO, NÃO RESOLVIDO. Cargo, empregador, formação, competências,
    localidade e sinal de procura de emprego, de 138 pessoas identificadas, com
    base legal **não declarada em lado nenhum desta árvore**. Isto não é um
    detalhe técnico: é uma pergunta para o responsável, e ela não é desta
    missão. Fica escrita porque calar era pior.

`linkedin.profiles` **não é declarado** em `scrap_capacidades`. O material
existe e a capacidade não. Nenhuma coleta massiva de pessoas foi implementada
aqui, e esta missão recomenda que continue assim.

---

## 19 · PERGUNTA 18 — CUSTO

| CAPABILITY | FREE_ROUTE | FREE_COVERAGE | PAID_GAP | CHEAPEST_ACTOR | USD/1000 | EXTRA_EVENT | LOCAL_REPLACEMENT | EXPECTED_SAVING |
|---|---|---|---|---|---|---|---|---|
| identidade de organização | site da própria organização | handle, quando publicado | nenhum | — | **0** | — | — | 100% |
| descoberta recente | company page | 10–13 ids | profundidade | `harvestapi/company-posts` | 1,50 | — | — | — |
| **história profunda** | **nenhuma** | — | **tudo** | `harvestapi/post-search` | **1,50** | — | — | — |
| post direto | URL pública | 1 item | — | — | 0 | — | — | — |
| texto do post | — | — | tudo | `harvestapi/*-posts` | 1,50 | incluído | — | — |
| métricas (likes/shares/contagem) | — | — | tudo | idem | 1,50 | **incluído** | — | — |
| **tipos de reação agregados** | — | — | tudo | idem | 1,50 | **incluído — já pago** | — | — |
| texto de comentários | — | — | tudo | `harvestapi/post-comments` | **2,00** | evento à parte | — | — |
| lista de quem reagiu | — | — | tudo | `harvestapi/post-reactions` | 2,00 | evento à parte | — | **não colher** |
| URL de vídeo | — | — | tudo | incluído na listagem | 0 extra | — | — | — |
| **bytes de vídeo** | — | — | tudo | `bytepulselabs` | US$ 0,06/10 MB | por arranque 0,006 | — | — |
| **legenda nativa** | — | — | **NENHUM ACTOR A ENTREGA** | — | — | — | ASR local **se** houver áudio | — |
| documento/carrossel | — | — | tudo | incluído na listagem (URL) | 0 extra | — | **`executor_texto_de_pdf.py`** | alto |
| perfis | — | — | tudo | `harvestapi/profile-scraper` | **4,033 MEDIDO** | — | — | — |
| empresas | — | — | tudo | `harvestapi/linkedin-company` | 3,00 | — | — | — |

### Custo histórico real desta casa

```
apify/harvestapi~linkedin-profile-scraper   120 perfis   US$ 0,4840   = 4,033/1.000
apify/harvestapi~linkedin-post-search       472 posts    COST_USD = NOT_PRESERVED
apify/harvestapi~linkedin-profile-search    101 perfis   COST_USD = NOT_PRESERVED
harvestapi~linkedin-profile-search-by-name   12 runs     COST_USD = 0,
                                                         COST_STATE = NOT_RESETTLED_RUN_NOT_LISTED
```

    `COST_USD = 0` COM `COST_STATE = NOT_RESETTLED` NÃO É «FOI GRÁTIS».
    É «NINGUÉM ACERTOU A CONTA». São duas frases, e só uma é verdadeira.

```
LINKEDIN_TOTAL_PAGO_COMPROVADO = US$ 0,4840
LINKEDIN_TOTAL_PAGO_REAL       = **UNKNOWN** — três corridas sem preço preservado
```

E a comparação que salta: a casa pagou **US$ 4,033/1.000** por perfis. A
listagem de posts custa hoje, de tabela, **US$ 1,50/1.000** — e é a listagem
que traz vídeo, documento, artigo e tipos de reação.

---

## 20 · PERGUNTA 19 — DELTA-FIRST

Os campos existem, e estão documentados:

| knob | Actor | o que faz |
|---|---|---|
| **`postedLimitDate`** | `harvestapi/company-posts` · `profile-posts` · `post-search` | ISO date ou timestamp — **só o que é posterior** |
| `postedLimit` | idem | `1h` · `24h` · `week` · `month` · `3months` · `6months` · `year` |
| **`scrapeUntil`** | `supreme_coder/linkedin-post` | data; só posts mais novos |
| `date_filter` | `apimaestro/posts-search` | filtro de data |
| `startPage` / `scrapePages` | `harvestapi/post-search` | janela de páginas |
| — | `apimaestro/company-posts` | **nenhum filtro de data documentado** |

E o checkpoint que a casa já tem no payload, sem inventar nada:

```
postedAt.timestamp   epoch ms, 472/472        → lastSeenTimestamp
id / entityId        o activity id, 472/472   → lastSeenPost
shareUrn             urn:li:share:…, 472/472  → identidade estável
```

```
ECONOMIA POTENCIAL, contada na distribuição real dos 472 posts
(janela medida para trás a partir da captura de 2026-08-29):

    últimos   7 dias .....  16 de 472 =  3,4%
    últimos  30 dias .....  60 de 472 = 12,7%
    últimos  90 dias .....  175 de 472 = 37,1%
    últimos 365 dias .....  452 de 472 = 95,8%

  → uma corrida recorrente SEMANAL com `postedLimitDate` pagaria ~3,4% do
    que a recolha total pagou, para o mesmo conjunto de fontes.
    MENSAL: ~12,7%.
```

E a leitura inversa, que é a que protege: **95,8% dos posts cabem em um ano.**
Quem já correu uma vez sem janela comprou quase toda a história útil daquele
conjunto. Repetir sem `postedLimitDate` é pagar de novo pelo que já está no
disco.

    O CHECKPOINT É CONCEITO DE FORA DO ADAPTER. O QUE ESTE ESTUDO DIZ É SÓ
    QUE **O SCRAP TEM DE CONSEGUIR RECEBER UMA JANELA** — e que a rota paga
    já sabe obedecer a ela. Nada aqui redesenha a Collection.

---

## 21 · PERGUNTA 20 — ENRICHMENT-ON-DEMAND

A listagem já diz onde vale a pena gastar. Medido nos 472:

```
FASE A — listagem barata (US$ 1,50/1.000, tabela)
   traz de graça: texto · autor · data exata · likes · shares ·
                  CONTAGEM de comentários · TIPOS de reação ·
                  URL de vídeo · URL de PDF · link externo · imagens

FASE B — só o item selecionado
   comentários   → 95 dos 472 posts têm ao menos 1   (20,1%)
                   os outros 377 custariam US$ 0 e devolveriam nada
   vídeo         → 56 dos 472                        (11,9%)
   documento     → 20 dos 472                         (4,2%)
```

    O CAMPO `engagement.comments` VEM GRÁTIS NA LISTAGEM E DIZ, ANTES DE
    QUALQUER GASTO, QUAIS DOS 472 POSTS TÊM COMENTÁRIOS. PEDIR TEXTO DE
    COMENTÁRIO PARA OS 472 É PAGAR 377 PERGUNTAS CUJA RESPOSTA JÁ SE SABE
    QUE É VAZIA.

```
custo de comentários, US$ 2,00/1.000 (tabela):
  todos os 335 comentários existentes .................... US$ 0,6700
  só os 50 posts mais comentados (290 = 87% do total) ..... US$ 0,5800
  só os 20 posts mais comentados (240 = 72% do total) ..... US$ 0,4800
```

O SCRAP não decide relevância. Ele respeita `ENRICH_THIS_ITEM` vindo de fora.
O que este estudo acrescenta é que **a listagem já carrega o sinal que torna
essa seleção possível sem uma chamada extra**.

---

## 22 · PERGUNTA 21 — FÓRUNS, COMO EVIDÊNCIA SECUNDÁRIA

Tudo nesta secção é **comunidade**. Nunca substitui prova, e está aqui separado
por isso.

| afirmação da comunidade | o que ela é |
|---|---|
| HTTP `999` é o código de recusa próprio do LinkedIn | consistente entre fontes |
| ~50–60 pedidos anónimos de perfil em 15 min levam o IP a `999` permanente | **um número, uma fonte, não reproduzido aqui** |
| convidado vê 2–3 perfis antes do authwall | repetido, não medido aqui |
| `people search` de convidado redireciona para `/uas/login` | consistente |
| o guest endpoint de vagas responde a anónimo e pagina por `?start=` | consistente, e há código aberto a usá-lo |
| company page de convidado mostra «um recorte público limitado» | consistente com o teto de 10–13 que a casa mediu |
| o LinkedIn muda schema e quebra scrapers com frequência | genérico; **sem cadência medida** |

```
COMMUNITY_EVIDENCE_WEIGHT = SECUNDÁRIA
NENHUMA LINHA DESTA SECÇÃO PROMOVE UM ESTADO DE CAPACIDADE.
```

---

## 23 · PERGUNTA 22 — POLÍTICA E TERMOS

    ISTO NÃO É PARECER JURÍDICO. São factos sobre ficheiros e páginas, citados
    literalmente, cada um na sua linha. Nenhum decide sozinho.

### `robots.txt`

Última medição desta casa: **2026-09-11**, 120 190 bytes, 77 grupos.

```
# Notice: The use of robots or other automated means to access LinkedIn without
# the express permission of LinkedIn is strictly prohibited.

User-agent: *           →  Disallow: /
User-agent: LinkedInBot →  Allow: /
```

`ROBOTS_STATUS = DISALLOW_ALL`. **Não remedido nesta missão** — remedir custa um
pedido real, e esta missão declarou zero. Ver `PROBE_1`.

### User Agreement §8.2 — as três cláusulas que alcançam este caso

1. proíbe «develop, support or use software, devices, scripts, robots or any
   other means or processes (including crawlers, browser plugins and add-ons or
   any other technology) to **scrape the Services** or otherwise copy profiles
   and other data»;
2. §8.2(4) proíbe «**Copy, use, display or distribute any information**
   (including content) obtained from the Services, **whether directly or
   through third parties (such as search tools or data aggregators or
   brokers)**, without the consent of the content owner»;
3. proíbe «**override any security feature or bypass or circumvent any access
   controls** or use limits of the Services».

    A (2) É A QUE MATA O ATALHO. O INTERMEDIÁRIO NÃO MUDA A CLÁUSULA: APIFY,
    HARVESTAPI E GOOGLE ESTÃO TODOS DENTRO DE «THROUGH THIRD PARTIES».

### API oficial — remedido hoje contra `li-lms-2026-08`

Página `posts-api`, `updated_at: 2026-05-13`, `defaultMoniker: li-lms-2026-08`:

| permissão | texto literal | consequência |
|---|---|---|
| `r_organization_social` | «Retrieve organizations' posts, comments, and likes. **Restricted to organizations in which the authenticated member has one of the following company page roles: ADMINISTRATOR, DIRECT_SPONSORED_CONTENT_POSTER, CONTENT_ADMIN**» | lê a Página que a casa administra |
| `r_member_social` | «Retrieve posts, comments, and likes on behalf of an authenticated member. This permission is **restricted** and is available to **approved users only**.» | não é a Página de terceiro |

```
CORREÇÃO AO C11: ele escreveu `r_member_social` = «CLOSED. We're not accepting
access requests at this time». A documentação corrente diz «restricted …
available to approved users only». É mais fraco, e não muda a conclusão:
continua a ser leitura EM NOME DE UM MEMBRO, não de um concorrente.
```

```
NÃO EXISTE, EM NENHUM TIER, ROTA OFICIAL DE LEITURA DO CONTEÚDO DE UMA
ORGANIZAÇÃO QUE ESTA CASA NÃO ADMINISTRA.
Confirmado contra a documentação corrente. Isto não é um degrau que falta
subir — é um degrau que não existe.
```

### A matriz de política, rota a rota

| rota candidata | `TECHNICALLY_POSSIBLE` | `TERMS_STATUS` | `ROBOTS_STATUS` | `CURRENT_SINTONIA_POLICY` | `HUMAN_DECISION_NEEDED` |
|---|---|---|---|---|---|
| site da própria organização | SIM | fora do §8.2 (não é «the Services») | n/a | **ALLOWED** | não |
| `article.link` já preservado | SIM | dado derivado de colheita já feita | n/a | não declarado | **SIM**, baixo risco |
| company page pública | PROVEN histórico | §8.2(1) alcança | `DISALLOW_ALL` | `ROUTE_NOT_ALLOWED` de facto | **SIM** |
| post direto por URL | PROVEN histórico | §8.2(1) | `DISALLOW_ALL` | `ROUTE_NOT_ALLOWED` | **SIM** |
| asset de mídia em `licdn.com` | PROVEN histórico | §8.2(1)+(4) | host distinto, **não medido** | não declarado | **SIM** |
| legenda SRT nativa | PROVEN histórico | idem | idem | não declarado | **SIM** |
| **Ad Library** | UNKNOWN | §8.2 sem exceção escrita | **não medido** | não declarado | **SIM** |
| busca por índice (Google/Bing) | SIM | **§8.2(4) nomeia «search tools»** | n/a | não declarado | **SIM** |
| Actors Apify (todos) | PROVEN histórico | **§8.2(4) nomeia «data aggregators or brokers»** | n/a | `ROUTE_NOT_ALLOWED` | **SIM** |
| Community Management API | SIM, para Página própria | permitido | n/a | `ROUTE_NOT_ALLOWED` | não — **não serve o caso de uso** |
| Voyager | SIM, com sessão | §8.2(1)+(3) | `DISALLOW_ALL` | proibido por §23 da casa | não |

```
POLICY_CHANGED_BY_THIS_MISSION = NÃO. Nenhuma linha acima foi escrita em
`leis/social_matriz.py`. A matriz canónica está intacta.
```

---

## 24 · PERGUNTA 23 — A ESCADA, SAÍDA DA MEDIÇÃO

A ordem abaixo **não** é a ordem conceitual do enunciado. É a que a medição
produz, e ela difere em dois pontos.

```
0. O QUE JÁ ESTÁ NO DISCO E NINGUÉM LEU
   custo ZERO · política NENHUMA (o dado já foi colhido) · risco ZERO
   → 56 URLs de vídeo · 20 PDFs com manifesto de transcrição ·
     93 links externos · 449 agregados de tipo de reação
   Este degrau não existia no enunciado, e é o mais barato de todos.

1. OFF-LINKEDIN DISCOVERY pelo site da própria organização
   a única rota hoje ALLOWED. Devolve o handle, não as publicações.

2. PUBLIC NO-LOGIN SURFACE
   company page rasa e post direto. PROVEN tecnicamente, ROUTE_NOT_ALLOWED
   hoje. Não sobe sem decisão humana.

3. PUBLIC MEDIA / CAPTION ASSET
   a legenda SRT. É o único degrau que compra FALA sem ASR — e é o único
   que nenhum fornecedor pago entrega.

4. LOCAL PROCESSING
   texto de PDF (`executor_texto_de_pdf.py`) e ASR (`fala_local`).
   Os dois existem, os dois funcionam, e nenhum é o gargalo.

5. PAID PROVIDER, mas SÓ para o gap e SÓ com janela
   listagem a US$ 1,50/1.000 com `postedLimitDate`; enriquecimento só do
   item selecionado. Bloqueado pela política hoje.

6. OFFICIAL API
   desceu do quinto para o sexto lugar, e por mérito: ela NÃO SERVE
   este caso de uso em tier nenhum. Manter alto na escada seria fingir
   que há um degrau ali.

7. BLOCKED
   fala de vídeo de terceiro. Nenhuma rota, permitida ou não, a entrega
   hoje — o único caminho conhecido é a legenda nativa da superfície
   pública, e essa está fora.
```

    OS DOIS DESVIOS SÃO: UM DEGRAU ZERO QUE NINGUÉM TINHA CONTADO, E A API
    OFICIAL A CAIR PARA PENÚLTIMA. AMBOS SAÍRAM DA MEDIÇÃO.

---

## 25 · PERGUNTA 24 — QUANTO DA APIFY SE PODE ELIMINAR

```
CURRENT_PAID_NEED   = 0 hoje. A política declara FETCH_POST fora, e o portão
                      recusa. Não há dependência paga ATIVA do LinkedIn.
FREE_REPLACEABLE    = identidade de organização (site próprio)
                      links externos (já no disco)
                      tipos de reação (já no disco)
                      URLs de vídeo e de PDF (já no disco)
LOCAL_REPLACEABLE   = texto de documento/carrossel (PDF → texto)
                      fala, SE alguma vez houver áudio (ASR)
PAID_ONLY           = história profunda por palavra-chave
                      texto de comentários
                      listagem de posts de empresa além dos 10–13
                      lista de quem reagiu  ← e esta NÃO SE DEVE COMPRAR
BLOCKED             = fala de vídeo de terceiro, em qualquer rota
UNKNOWN             = Ad Library · robots do `licdn.com` · TTL real da legenda
                    · bytes de um MP4 · se a legenda ainda é servida
```

E em dinheiro:

```
ESTIMATED_CURRENT_MONTHLY_COST  = **US$ 0,00** — medido, não estimado:
                                  nenhuma rota de LinkedIn corre hoje.
ESTIMATED_AFTER_OPTIMIZATION    = NÃO APLICÁVEL enquanto for zero.
SAVING_PERCENT                  = **UNKNOWN**, e dizer outra coisa seria
                                  inventar uma poupança sobre um gasto que
                                  não existe.
```

    A PERGUNTA «QUANTO DA APIFY PODEMOS ELIMINAR» TEM, NO LINKEDIN, UMA
    RESPOSTA DESCONFORTÁVEL: JÁ ESTÁ TUDO ELIMINADO, E COM ELE A CAPACIDADE.
    O PROBLEMA DESTA PLATAFORMA NÃO É CUSTO. É AUTORIZAÇÃO.

Para referência histórica, e só isso: `US$ 0,4840` comprovadamente gastos
(120 perfis), mais três corridas com `COST_USD = NOT_PRESERVED`.

---

## 26 · RED TEAM DO ESTUDO — as 20 tentativas do enunciado

| # | ataque | resultado |
|---|---|---|
| 1 | Actor diz no-login, mas o código não prova | **apanhado** — 11 de 13 dizem-no; `SOURCE_CODE_PUBLIC = NÃO` nos 34; fica `DOCUMENTED`, nunca `PROVEN` |
| 2 | marketing vira evidência | **apanhado** — «without violating platform policies» é frase do vendedor sobre a política de outra empresa |
| 3 | rota pública vira permitida | resistiu — §2 e §23 separam `PUBLIC_WITHOUT_LOGIN` de `POLICY_ALLOWED` em colunas distintas |
| 4 | histórico vira current | **apanhado duas vezes** — a legenda de 2026-09 e as URLs de mídia estão as duas marcadas `histórico`; as URLs preservadas **expiraram** |
| 5 | Voyager vira canónico por ser open source | resistiu — `CAN_BE_USED_CANONICALLY = NÃO`, por três razões independentes |
| 6 | search index vira conteúdo do LinkedIn | **apanhado** — o `free-linkedin-company-finder` usa Google e por isso **não** é a rota permitida desta casa |
| 7 | caption vira transcript | resistiu |
| 8 | SRT automática vira legenda humana | resistiu — `acs-singleton` no endereço; e o campo `captions` da API oficial é `USER_PROVIDED`, outra coisa com o mesmo nome |
| 9 | áudio local vira audio-only de rede | resistiu — `LOCAL AUDIO EXTRACTION != NETWORK AUDIO-ONLY ACQUISITION` |
| 10 | Range chamado barato sem medir bytes | **apanhado** — `AUDIO_ONLY_NETWORK_SAVING = NÃO MEDIDO`, e `VIDEO_BYTES = UNKNOWN` |
| 11 | comments count vira comments text | **apanhado com número** — 335 de contagem, **0** de texto, no mesmo payload |
| 12 | recent posts vira history | **apanhado, e ao contrário** — a casa tinha o erro inverso: mediu a página rasa e concluiu que não há história, tendo 8a7m no disco |
| 13 | profile route vira company route | **apanhado** — 138 pessoas e 62 empresas estão contadas em separado, com nota de GDPR |
| 14 | preço sem timestamp vira preço atual | **apanhado** — cada preço carrega `tabela 2026-09-12` ou `MEDIDO`; e a Apify retira o aluguer em 2026-10-01 |
| 15 | custo por resultado ignora compute/proxy | **apanhado** — o modelo é per-event; e `bytepulselabs` cobra **por arranque e por 10 MB**, que é compute e banda em claro |
| 16 | zero resultado vira bloqueio | resistiu — o 404 do LinkedIn já foi medido honesto por esta casa |
| 17 | authwall vira ausência de dado | resistiu — `302 → /uas/login` está numa linha própria |
| 18 | `999` vira recusa de política | **apanhado** — três estados nomeados e separados em §2 |
| 19 | CDN asset vira prova de permissão | **apanhado** — «Visible to anyone on or off LinkedIn» em 472/472 é declaração de visibilidade, **não** de autorização de automação |
| 20 | User Agreement tratado como parecer final | resistiu — §23 abre com a ressalva, e cada eixo entra numa linha |

### E três que esta missão virou contra si mesma

| # | ataque | resultado |
|---|---|---|
| 21 | **o achado do RAW vira capacidade** | **apanhado** — ter o endereço do MP4 não é ter o MP4, e as URLs **expiraram**. `FLOW_OBSERVED != WIRED != ALLOWED` |
| 22 | **corrigir o C11 vira desqualificar o C11** | **apanhado** — o método dele (contar campos, não ler folhetos) é o que tornou este achado possível; errou o ficheiro, não o método |
| 23 | **o censo do C11 tratado como o censo da casa** | **apanhado** — ele não está na linha do SCRAP; quem lê o HEAD não o vê |

---

## 27 · PROVAS AO VIVO NECESSÁRIAS — preparadas, NÃO executadas

```
PROBE_1  robots.txt e a Ad Library
  TARGET        linkedin.com/robots.txt
  REQUESTS      1
  COST          US$ 0
  WHAT_IT_PROVES  se há grupo ou `Allow:` específico para `/ad-library`,
                  e se o texto de 2026-09-11 ainda vale.
  RISCO         é 1 pedido a um ficheiro cuja função é ser lido por robôs.
                Mesmo assim: NÃO EXECUTADO, porque a missão declarou zero.

PROBE_2  robots do host de mídia
  TARGET        dms.licdn.com/robots.txt · media.licdn.com/robots.txt
  REQUESTS      2
  COST          US$ 0
  WHAT_IT_PROVES  o `licdn.com` é host distinto e NUNCA foi medido. A casa
                  assume o robots do `linkedin.com` para ele, e isso é
                  assunção, não medição.

PROBE_3  a legenda nativa ainda é servida?
  TARGET        1 post público de vídeo, já conhecido
  REQUESTS      1 página + 1 asset de legenda
  COST          US$ 0
  WHAT_IT_PROVES  `CAPTION_ROUTE_TODAY`, `TTL` real do `e=` da legenda,
                  e se o padrão `acs-singleton` sobreviveu.
  BLOQUEIO      exige a rota que a política declara fora. DECISÃO HUMANA.

PROBE_4  bytes de um MP4 do LinkedIn
  TARGET        1 asset, só o cabeçalho (HEAD ou Range de 1 byte)
  REQUESTS      1
  COST          US$ 0
  WHAT_IT_PROVES  `VIDEO_BYTES`, que é o denominador que falta à escada
                  inteira. Sem ele, «a legenda poupa 99%» não tem conta.
  BLOQUEIO      idem PROBE_3.

PROBE_5  a listagem de empresa entrega vídeo e documento?
  TARGET        `harvestapi/linkedin-company-posts`, 1 empresa, maxPosts=10
  REQUESTS      1 run
  COST          ≈ US$ 0,015 (10 posts a US$ 1,50/1.000)
  WHAT_IT_PROVES  se o payload de COMPANY-POSTS traz os mesmos campos
                  `postVideo`/`document` que o de POST-SEARCH traz — e se
                  traz LEGENDA, que é a única coisa que falta.
  BLOQUEIO      rota paga, `ROUTE_NOT_ALLOWED`. DECISÃO HUMANA + dinheiro.

PROBE_6  o PDF do carrossel baixa?
  TARGET        1 `transcribedDocumentUrl` NOVO (os preservados expiraram)
  REQUESTS      1
  COST          US$ 0 além da listagem que o traz
  WHAT_IT_PROVES  se `scanRequiredForDownload: true` impede o download por
                  HTTP simples, e se o `feedshare-document-transcript`
                  devolve texto utilizável.
```

```
NENHUMA DAS SEIS FOI EXECUTADA.
TOTAL SE TODAS FOSSEM AUTORIZADAS:  ≈ US$ 0,015  e  7 pedidos.
```

---

## 28 · BACKLOG

### P0 — baixo risco, alto valor, barato, e **sem decisão de política**

| item | CAPABILITY | CURRENT | CANDIDATE_ROUTE | EXPECTED_VALUE | EXPECTED_COST | IMPL_SIZE | POLICY | PROOF_NEEDED |
|---|---|---|---|---|---|---|---|---|
| **P0.1** | preservar o RAW na normalização | 26 campos → 19, **7 conceitos perdidos** | mudar só a normalização, sobre o `.gz` que já existe | recupera vídeo, documento, artigo, tipos de reação, sem rede | **US$ 0** | pequeno | nenhuma — o dado já foi colhido | nenhuma |
| **P0.2** | trazer o C11 para a linha do SCRAP | orfão em 1 ramo | `git` | impede a próxima missão de refazer 710 linhas | 0 | trivial | nenhuma | nenhuma |
| **P0.3** | corrigir o achado de vídeo do C11 | «o provider não detecta vídeo» — **falso** | este documento | impede uma decisão errada de política | 0 | feito aqui | nenhuma | feita |
| **P0.4** | `linkedin.documents`: `NOT_EXECUTED` → o estado real | «nunca tentado» | declarar que o ENDEREÇO foi observado e os bytes não | honestidade de censo | 0 | pequeno | nenhuma | feita |
| **P0.5** | `article.link` como descoberta de fonte | 93 links parados | rota de web aberta que a casa já tem | 93 fontes candidatas grátis | 0 | pequeno | fora do §8.2 | nenhuma |

### P1 — alto valor, precisa de prova ou de decisão

| item | o que | bloqueio |
|---|---|---|
| **P1.1** | `PROBE_2` — robots do `licdn.com` | 2 pedidos, decisão de executar |
| **P1.2** | `PROBE_1` — robots e Ad Library | 1 pedido |
| **P1.3** | declarar a **Ad Library** na matriz, com o veredito que a medição der | precisa de P1.2 |
| **P1.4** | `PROBE_4` — `VIDEO_BYTES`, o denominador que falta | decisão de política |
| **P1.5** | `PROBE_3` — a legenda ainda existe? | decisão de política |
| **P1.6** | capacidade de **janela** (`postedLimitDate`) no pedido do SCRAP | desenho; não redesenha a Collection |

### P2 — nice-to-have

| item | o que |
|---|---|
| **P2.1** | `linkedin.reactions.aggregate` como capacidade declarada própria (vem grátis na listagem) |
| **P2.2** | medir quantas das organizações seguidas publicam o handle no próprio site (a sonda do C11 mediu 1 de 2 alcançáveis, de 7) |
| **P2.3** | ligar `executor_texto_de_pdf.py` a um `document` do LinkedIn, quando houver bytes |

### NO-GO — tecnicamente possível, **não adotar**

| item | por quê |
|---|---|
| **Voyager, em qualquer forma** | exige sessão; §8.2(3); §23 da casa; API interna sem contrato |
| **cookies de terceiro** (`capable_cauldron`) | pede cookie de sessão; §23 |
| **lista de pessoas que reagiram** | dado pessoal que o negócio não precisa; custa 2–5× mais que a contagem, que já vem grátis |
| **coleta massiva de perfis pessoais** | 138 pessoas já no disco sem base legal declarada; não aumentar |
| **`s-r/free-linkedin-company-finder`** e qualquer descoberta por índice | §8.2(4) nomeia «search tools» em claro |
| **stealth, rotação de proxy, derrotar anti-bot** | fora da autorização, e fora do que `social_rotas` faz por desenho |

---

## 29 · ENTREGA

### A · CURRENT SCRAP
```
DECLARED_CAPABILITIES = 7
WIRED_CAPABILITIES    = 0
LIVE_CAPABILITIES     = 0
```

### B · PUBLIC SURFACES
```
COMPANY_PAGE  landing legível como convidado, 10–13 activity ids · aba /posts/ → 302
PROFILE_PAGE  JSON-LD `Person`, parcial · authwall após 2–3
COMPANY_POSTS não expostos além da landing; sem URL de página seguinte
PROFILE_POSTS NÃO
DIRECT_POST   HTTP 200 com `<video data-sources>` (histórico)
MEDIA         MP4 em dms.licdn.com — 3 rendições numa observação, 1 noutra
CAPTIONS      SRT automática, 4 283 B, UMA observação, hoje UNKNOWN
COMMENTS      contagem sim · texto NÃO OBSERVADO em rota gratuita
DOCUMENTS     PDF + manifesto de transcrição — endereço observado, bytes não
```

### C · OPEN SOURCE
```
REPOS_REVIEWED = 12+
USEFUL_REPOS   = 2 sem login (scrapfly · JobSpy)
TECHNIQUES     = application/ld+json · guest endpoint paginado por ?start=
                 · Voyager (NÃO ADOTÁVEL)
```

### D · APIFY
```
ACTORS_REVIEWED         = 34 enumerados · 13 com preço lido em 2026-09-12
CHEAPEST_POST_ACTOR     = harvestapi/linkedin-company-posts · US$ 1,50/1.000
CHEAPEST_COMMENTS_ACTOR = harvestapi/linkedin-post-comments · US$ 2,00/1.000
CHEAPEST_PROFILE_ACTOR  = UNKNOWN (o que a casa pagou custou 4,033 MEDIDO)
CHEAPEST_DETAILS_ACTOR  = harvestapi/linkedin-company · US$ 3,00/1.000
```

### E · VIDEO
```
DIRECT_VIDEO           SIM — URL na listagem paga, 56/472
NATIVE_CAPTION         SIM na página pública (1 obs.) · ZERO em 472 posts pagos
AUDIO_ONLY             NÃO OBSERVADO em rota nenhuma
FULL_VIDEO_NEEDED_WHEN sempre que houver fala e não houver legenda — que é,
                       pela evidência paga, TODAS as vezes
```

### F · COMMENTS
```
COUNT          SIM, grátis na listagem — 335 em 95 de 472 posts
TEXT           NÃO na listagem — 0 de 472
DEPTH          maxItems=0 (tudo, 100 páginas) por tabela; respostas até 5/raiz
CHEAPEST_ROUTE harvestapi/linkedin-post-comments · US$ 2,00/1.000 · rota fora
```

### G · DISCOVERY
```
OFF_LINKEDIN  site da própria organização — a ÚNICA ALLOWED · PARTIAL
SEARCH_INDEX  tecnicamente útil · §8.2(4) nomeia «search tools» · DECISÃO HUMANA
PUBLIC_PAGE   10–13 ids · DISALLOW_ALL
PAID          8 anos e 7 meses medidos · ROUTE_NOT_ALLOWED
```

### H · COST
```
FREE_REPLACEABLE  identidade · links externos · tipos de reação · URLs de asset
LOCAL_REPLACEABLE texto de PDF · ASR (se houver áudio)
PAID_ONLY         história profunda · texto de comentários · listagem além de 13
UNKNOWN           Ad Library · robots do licdn · TTL da legenda · VIDEO_BYTES
```

### I · POLICY
```
ALLOWED_CANDIDATES  descoberta indireta pelo site da organização
                    reaproveitamento do RAW já preservado
CONDITIONAL         Ad Library (pendente de robots) · article.link
NOT_ALLOWED         company page · post direto · mídia · legenda · Apify ·
                    índice de busca · Voyager
HUMAN_DECISIONS     1. autoriza-se alguma rota para conteúdo do linkedin.com?
                    2. autoriza-se a Ad Library, se o robots a permitir?
                    3. qual a base legal dos 138 perfis pessoais no disco?
                    4. a descoberta por índice entra ou fica fora?
```

### J · RECOMMENDED ACQUISITION LADDER
```
0  o que já está no disco e ninguém leu     ← degrau novo, custo zero
1  off-LinkedIn discovery (site da organização)
2  public no-login surface
3  public media / caption asset
4  local processing
5  paid provider, só para o gap e só com janela
6  official API                              ← desceu; não serve este caso
7  blocked
```

### K · PROBES NEEDED
`PROBE_1` robots + Ad Library · `PROBE_2` robots do licdn ·
`PROBE_3` a legenda ainda existe · `PROBE_4` VIDEO_BYTES ·
`PROBE_5` company-posts traz mídia e legenda · `PROBE_6` o PDF baixa
— **nenhuma executada**, total ≈ US$ 0,015 e 7 pedidos.

### L · BACKLOG
`P0` 5 itens, todos sem decisão de política · `P1` 6 · `P2` 3 · `NO-GO` 6.

### M · WHAT CHANGED
```
1. o RAW preservado foi aberto pela primeira vez — e desmente o C11 no vídeo
2. `linkedin.documents` deixa de ser «nunca tentado» sobre o endereço
3. a profundidade histórica deixa de ser UNKNOWN: 8 anos e 7 meses, medidos
4. o conflito de runtime do C11 está FECHADO no HEAD
5. o C11 está órfão da linha do SCRAP, e isso é um facto novo
6. a API oficial desce na escada, por não servir o caso de uso
7. a Ad Library entra como eixo que a casa nunca considerou
```

### N · WHAT IS PROVEN
```
· 7 declaradas, 0 ligadas, 0 vivas                      (corrido no HEAD)
· o portão recusa LINKEDIN/FETCH_POST antes de gastar   (corrido no HEAD)
· 472 posts RAW: 56 com vídeo, 20 com documento, 93 com artigo
· 0 de 472 com legenda, áudio ou duração
· 0 de 472 com texto de comentário; 335 de contagem
· 449 de 472 com agregado de tipo de reação
· janela 2018-01-09 → 2026-08-28, na página 1 de 18 buscas
· 1 005 B por post, comprimido
· US$ 0,4840 é o único custo de LinkedIn comprovado desta casa
· a normalização perde 7 conceitos inteiros
```

### O · WHAT REMAINS UNKNOWN
```
· o robots do linkedin.com HOJE (medido em 2026-09-11, não remedido)
· o robots do licdn.com — NUNCA medido
· a Ad Library: robots, formato, estabilidade
· se a legenda SRT ainda é servida, e com que TTL
· VIDEO_BYTES — nenhum MP4 do LinkedIn foi baixado, nunca
· se `company-posts` traz os mesmos campos de mídia que `post-search`
· se `scanRequiredForDownload: true` impede o download do PDF
· o custo real das 3 corridas com COST_USD = NOT_PRESERVED
· o mecanismo de 16 dos 19 Actors com preço conhecido
· a base legal dos 138 perfis pessoais preservados
```

### P · KNOW_HOW_DELTA
```
KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA
```

O ficheiro `SINTONIA-EAME-KNOW-HOW.md` **não vive na linha do SCRAP** — está em
`origin/claude/sintonia-eame-know-how-v1`, em §80. Esta missão não lhe toca.
O que ele precisa de receber, e por quê:

```
O QUE          medir o artefato NORMALIZADO e atribuir a falta ao FORNECEDOR
POR QUÊ        o C11 contou 19 campos no ficheiro normalizado e concluiu que
               o provider não devolve mídia. O RAW ao lado tinha 26 campos,
               56 vídeos e 20 documentos.
PROVA          data/samples/raw-paid/ES-T8-002-linkedin-posts-{a,b}.raw.json.gz
CONSEQUÊNCIA   antes de declarar que uma fonte NÃO devolve um campo, abrir o
               BRUTO. A normalização é desta casa, e é ela que perde primeiro.

               `PROVIDER_GAP` != `NORMALIZATION_GAP`.

O QUE          um censo que não está na linha canónica é um censo que a
               próxima missão refaz do zero
POR QUÊ        o C11 (710 linhas, LinkedIn) ficou num ramo que não atravessou;
               o C12 (X) atravessou. Quem lê o HEAD vê um e não vê o outro.
CONSEQUÊNCIA   medir custa; perder a medição custa duas vezes.
```

---

## 29-bis · O PORTÃO DO MAPA, CORRIDO — E UMA REPROVAÇÃO HERDADA

A cadeia do `AGENTS.md` foi corrida inteira sobre esta árvore:

```
generate_system_map.py           MAPA=OK · pecas=163 · ligacoes=673
validate_system_map.py           SYSTEM_MAP_CHECK=PASS
test_system_map.py               TESTES_SYSTEM_MAP=PASS
test_freshness.mjs               TESTES_FRESCURA=PASS · 49 provas
test_impressao_da_arvore.py      **FAIL · 1 reprovada**
publicar_no_deploy.mjs           DEPLOY_METADATA=OK · MESMA_ARVORE=SIM · PERTENCE=SIM
```

A reprovação, dita em claro em vez de escondida:

```
nenhum_passo_e_engolido_pelo_erro_do_anterior
  passos sem `if: !cancelled()`:
    mapa: 1 · regerar o mapa a partir desta árvore
    mapa: 1b · o censo da topologia da coleta
    coleta: 4k · a lingua e a mesma no contrato, no ...
    coleta: 4l · a telemetria distingue NAO CORREU d...
```

**Ela é herdada, e isso foi medido, não suposto.** A mesma reprovação, com os
mesmos quatro passos, aparece numa árvore de trabalho limpa em `532e3bed` —
o HEAD do SCRAP, antes de qualquer linha desta missão. E esta missão **não
toca num único ficheiro `.github/`**.

```
CAUSADA_POR_ESTA_MISSAO = NÃO   (provado em worktree limpa de 532e3bed)
FICHEIROS .github/ TOCADOS = 0
```

Não foi consertada aqui de propósito: consertar um workflow é uma alteração
real de infraestrutura, fora do escopo declarado desta missão — que é o
SINTONIA SCRAP, e que é estudo. Fica registada para quem for dono dela.

    UMA REPROVAÇÃO HERDADA E NOMEADA É UMA MEDIÇÃO. UMA REPROVAÇÃO HERDADA
    E CALADA É A PRÓXIMA MISSÃO A DESCOBRI-LA COMO SE FOSSE NOVA.

A outra reprovação que este teste deu na primeira passagem —
`as_duas_leituras_medem_o_mesmo_numero_de_ficheiros`, `disco=1674 indice=1672` —
**era minha**, e era exatamente os dois ficheiros novos desta missão fora do
índice. Passou ao serem adicionados.

---

## 30 · FECHO

```
LINKEDIN_DEEP_STUDY = V1
LINKEDIN_REAL_REQUESTS = 0 · LICDN_REQUESTS = 0
APIFY_RUNS = 0 · COST_USD = 0,00
POLICY_CHANGED = NÃO · ADAPTER_CHANGED = NÃO · MATRIZ_CHANGED = NÃO
NEW_OPERATIONAL_DIFF = 0
ARTEFATOS = LINKEDIN-DEEP-STUDY-V1.md · LINKEDIN-ROUTE-MATRIX-V1.json

HARD STOP.
```

A frase que o estudo inteiro comprime numa linha:

> **O LinkedIn continua a ser útil para saber QUEM É e não para saber O QUE
> DISSE — mas metade do que a casa julgava não ter, ela já tinha comprado,
> preservado e deitado fora na normalização; e a profundidade histórica que
> ela declarava UNKNOWN já lhe tinha sido entregue, oito anos e sete meses
> dela, na página 1.**

E a que fica por cima de todas:

    A ROTA MAIS BARATA QUE ESTE ESTUDO ENCONTROU NÃO É UMA ROTA.
    É UM FICHEIRO `.gz` QUE ESTÁ NO DISCO DESDE 29 DE AGOSTO.
