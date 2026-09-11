# C11 · LINKEDIN CAPABILITY DEEP CENSUS

```
CENSO_DATADO_EM     = 2026-09-11
HEAD_MEDIDO         = 231ffa2c07fd500ae663d2f1a8e38417976370e1
C11_LINKEDIN_CENSUS = PASS
LINKEDIN_SPEECH_COVERAGE = EXACT_BLOCKER_KNOWN
```

> Fotografia datada. Não é Bíblia, não é Master, não é Final, não é contrato.
> Esta missão **mede e não integra**. Nenhuma capacidade foi ligada.

---

## A · A RESPOSTA CURTA, ANTES DA TABELA

O LinkedIn é a plataforma onde a casa **já teve** o melhor conteúdo e onde hoje
**não tem rota permitida nenhuma** para conteúdo.

```
LINKEDIN_DECLARED = 7
LINKEDIN_WIRED    = 0
LINKEDIN_OBSERVED = 372 posts + 44 identidades   ← histórico, por rota hoje proibida
LINKEDIN_UNWIRED  = 7
```

E o bloqueador não é técnico.

---

## B · CENSO ESTÁTICO

`coleta/adaptador_linkedin.py`: 60 linhas, **0 funções públicas**. É um módulo de
declaração, não de execução.

| capacidade declarada | estado declarado | caminho | prova citada |
|---|---|---|---|
| `linkedin.recent.discovery` | PROVEN | **nenhum** | `ESTADO-REAL-V1.md` |
| `linkedin.history.discovery` | UNKNOWN | nenhum | `BENCHMARK-V1-FINAL.md` |
| `linkedin.direct_post` | PROVEN | **nenhum** | `ESTADO-REAL-V1.md` |
| `linkedin.native_video` | PROVEN | **nenhum** | `ESTADO-REAL-V1.md` |
| `linkedin.native_caption` | PROVEN | **nenhum** | `BENCHMARK-V1-FINAL.md` |
| `linkedin.comments` | UNKNOWN | nenhum | `BENCHMARK-V1-FINAL.md` |
| `linkedin.documents` | NOT_EXECUTED | nenhum | `BENCHMARK-V1-FINAL.md` |

```
MODULE_EXISTS = YES   ·   EDGE_EXISTS = NO (7 de 7)   ·   FLOW_OBSERVED = YES (histórico)
```

---

## C · O ACHADO QUE O CENSO NÃO PROCURAVA

O benchmark histórico e a C9 descreviam o LinkedIn pela **página de empresa**:
descoberta recente rasa, post direto, vídeo nativo, legenda SRT.

Mas o que está preservado no disco desta casa é **outra coisa**:

```
data/samples/ES-T8-002-posts.json     372 posts LINKEDIN
```

com `TEXT`, `LIKES`, `COMMENTS_COUNT`, `SHARES`, `PUBLICATION_DATE`,
`DECLARED_AUTHOR`, `AUTHOR_URL`, `EXTERNAL_ID` (o activity id), `CAPTURE_DATE =
2026-08-29`, `RUN_ID = ES-T8-002-2026-08-29-a` — e, decisivo:

```
DISCOVERY_QUERY = "Venturia oleaginea"
```

Isto **não é** cronologia de página de empresa. É **busca de posts por palavra-
chave**, e bate com o ator que a matriz nomeia: `harvestapi~linkedin-post-search`.

```
A CAPACIDADE QUE REALMENTE PRODUZIU CONTEÚDO NESTA CASA NÃO É NENHUMA DAS SETE
DECLARADAS.
```

Mais 44 registos de **identidade de canal** LinkedIn em
`data/samples/SENSOR-PILOT/CANAL-IDENTIDADE.json`, com
`CHANNEL_IDENTITY_STATE` e `CHANNEL_IDENTITY_EVIDENCE` — identidade, não conteúdo.

```
IDENTITY DISCOVERY != CONTENT DISCOVERY. E as duas já correram, separadas.
```

---

## D · POLÍTICA — REMEDIDA HOJE

`https://www.linkedin.com/robots.txt`, 120 190 bytes, 77 grupos, lido em
2026-09-11:

```
# Notice: The use of robots or other automated means to access LinkedIn without
# the express permission of LinkedIn is strictly prohibited.

User-agent: *          →  Disallow: /
User-agent: LinkedInBot →  Allow: /
```

Não é interpretação nossa: é o aviso que a própria plataforma põe na primeira
linha do ficheiro. E `LinkedInBot` não somos nós.

`ROBOTS_STATUS = DISALLOW_ALL`

### POLICY_CONFLICT = YES

```
OWNER_A    = leis/social_matriz.py
DECISION_A = apify:harvestapi~linkedin-*  →  PERMITIDA = NAO · ROUTE_NOT_ALLOWED
             nota: «RISCO REGISTRADO, NÃO ENDOSSADO: esta casa JÁ gastou
             US$ 0,484 em 120 perfis por esta rota»

OWNER_B    = coleta/comunicacao_coleta.py:86
DECISION_B = ATORES['LINKEDIN'] = ('harvestapi~linkedin-post-search',
                                   'JA_RODOU_NESTA_CASA')

RUNTIME_REACHABLE = YES
FIRST_BREAK       = falta de token Apify neste ambiente — e SÓ isso
```

O caminho é real e foi traçado: `fase_posts('LINKEDIN')` → LINKEDIN não está em
`CAPACIDADES_SCRAP` → `ator, _ = ATORES['LINKEDIN']` (linha 524) →
`ap.executar_com_pool` (linha 576).

A C9 registou este conflito. **Continua exatamente igual, e continua alcançável.**
Não foi corrigido aqui — não é missão desta.

---

## E · A API OFICIAL — MEDIDA CONTRA A DOCUMENTAÇÃO CORRENTE

Documentação `li-lms-2026-08`, páginas atualizadas em 2026-05-13 e 2026-05-15.

| permissão | o que lê | restrição declarada |
|---|---|---|
| `r_organization_social` | posts, comentários e reações de organizações | **só de organizações onde o membro autenticado é ADMINISTRATOR / DIRECT_SPONSORED_CONTENT_POSTER / CONTENT_ADMIN** |
| `r_member_social` | posts, comentários e reações de um membro | **CLOSED.** *«We're not accepting access requests at this time due to resource constraints»* |

E o produto descreve-se a si próprio como servindo para *«manage LinkedIn
company pages **for clients**»*.

Não há terceira permissão de leitura.

```
NÃO EXISTE, EM NENHUM TIER, ROTA OFICIAL DE LEITURA DO CONTEÚDO DE UMA
ORGANIZAÇÃO QUE ESTA CASA NÃO ADMINISTRA.
```

Isto **não** é «falta pedir acesso». Pedir acesso não produz a capacidade: o
programa inteiro pressupõe que a página é sua ou do seu cliente. E o SINTONIA
existe para observar comunicação pública de **concorrentes** — páginas que a
casa, por definição, não administra.

```
API EXISTS != WE ARE AUTHORIZED.
E aqui é mais forte: AUTHORIZED != CAPABLE OF THIS USE CASE.
```

O que a API oficial **teria** para nós, se a casa entrasse no programa:
`Organization Lookup API` — encontrar organizações por vanity name. Identidade,
não conteúdo. O mesmo eixo que a descoberta indireta já cobre de graça.

Porta de entrada, medida: Development Tier → Standard Tier com screencast, app
dedicada sem outros produtos, organização legal registada, endereço, política de
privacidade, uso comercial, e um «Technical Sign Off» em rollout.

---

## F · A ÚNICA ROTA PERMITIDA, SONDADA

`descoberta-indireta:site-da-organizacao` · `DIRECT_HTTP` · `PERMITIDA = SIM`

Buscar no site **da própria organização** o endereço LinkedIn dela. Nunca
`linkedin.com`, nunca buscador. Sete sentinelas da casa:

| sentinela | HTTP | handle |
|---|---|---|
| `imagelinenetwork.com` | 200 | **`linkedin.com/company/image-line`** |
| `arpa.veneto.it` | 200 | nenhum publicado |
| `cropscience.bayer.it` | 403 | — |
| `adama.com/italia` | 403 | — |
| `letsee.it` | 403 | — |
| `agronotizie.it` | falhou a ligação | — |
| `ismeamercati.it` | falhou a ligação | — |

```
LINKEDIN_IDENTITY_DISCOVERY_INDIRECT = PARTIAL   ·   1 de 2 alcançáveis
```

**Nenhuma destas falhas é do LinkedIn.** Os 403 são o WAF do site da organização
a recusar este IP de datacenter; os dois zeros são a ligação a falhar. Um 200 sem
handle também não é falha: é uma organização que não publica o seu.

E um limite que não se deve esquecer: isto devolve **o handle**, não as
publicações.

### Um defeito da minha própria sonda, encontrado e corrigido

A primeira passagem reportou o handle de `image-line` para dois sites que nem
sequer responderam — porque o ficheiro de saída guardava o conteúdo do site
anterior. Falso positivo fabricado pela ferramenta de medição, não pelos dados.

```
UMA SONDA COM ESTADO RESIDUAL MEDE A SONDA.
```

---

## G · A MATRIZ

`NOT_RUN · ROUTE_NOT_ALLOWED` significa: existe rota técnica conhecida, a
política canônica proíbe-a, e esta missão **não a executou**. Não significa que
a plataforma esteja partida.

| capability | MODULE | EDGE | FLOW | ROUTE | PROVIDER | AUTH | COST_STATE | DEPTH | POLICY | VERDICT | FIRST_BREAK |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **A · identidade** | ✔ | ✘ | ✔ 44 | site da organização | HTTP próprio | nenhuma | `ZERO` | 1 handle/site | **PERMITIDA** | **PARTIAL** | WAF do site de terceiro, não do LinkedIn |
| **B · discovery recente** | ✔ | ✘ | ✘ | página de empresa | — | nenhuma | `ZERO` | 10–13 ids, medido em 2026-09 | `DISALLOW_ALL` | `NOT_RUN` | `ROUTE_NOT_ALLOWED` |
| **C · discovery histórico** | ✔ | ✘ | ✘ | — | — | — | `UNKNOWN` | **`NOT_RUN`** | `DISALLOW_ALL` | `NOT_RUN` | «Show more» não expõe URL; e a rota está fora |
| **C′ · busca por palavra-chave** | ✘ | ✘ | **✔ 372** | `harvestapi~linkedin-post-search` | Apify | token | `MEASURED` US$ 4,03/1 000 | 372 posts, 1 corrida | **`ROUTE_NOT_ALLOWED`** | **`REQUIRES_AUTHORIZATION`** | política, não técnica |
| **D · post direto** | ✔ | ✘ | ✘ | URL direta | HTTP próprio | nenhuma | `ZERO` | 1 item | `DISALLOW_ALL` | `NOT_RUN` | `ROUTE_NOT_ALLOWED` |
| **E · texto do post** | ✘ | ✘ | ✔ 372 | idem C′ | Apify | token | `MEASURED` | — | `ROUTE_NOT_ALLOWED` | `REQUIRES_AUTHORIZATION` | idem |
| **F · autor/empresa** | ✔ | ✘ | ✔ 372+44 | idem | — | — | `ZERO`/`MEASURED` | — | misto | `PARTIAL` | — |
| **G · tempo de publicação** | ✘ | ✘ | ✔ 372 | idem C′ | Apify | token | `MEASURED` | — | `ROUTE_NOT_ALLOWED` | `REQUIRES_AUTHORIZATION` | idem |
| **H · métricas** | ✘ | ✘ | ✔ 372 | idem C′ | Apify | token | `MEASURED` | likes, comments, shares | `ROUTE_NOT_ALLOWED` | `REQUIRES_AUTHORIZATION` | sem views/impressions: isso é analytics do dono |
| **I · comentários** | ✔ | ✘ | ✘ | — | — | — | `UNKNOWN` | **`NOT_RUN`** | `DISALLOW_ALL` | `NOT_RUN` | nunca tentado **e** rota fora; oficial exige admin |
| **J · imagem** | ✘ | ✘ | ✘ | — | — | — | `UNKNOWN` | — | `DISALLOW_ALL` | `NOT_RUN` | `ROUTE_NOT_ALLOWED` |
| **K · vídeo** | ✔ | ✘ | ✘ | MP4 progressivo | HTTP próprio | nenhuma | `ZERO` | — | `DISALLOW_ALL` | `NOT_RUN` | `ROUTE_NOT_ALLOWED` |
| **L · legenda nativa** | ✔ | ✘ | ✘ | SRT servido ao lado | HTTP próprio | nenhuma | `ZERO` | — | `DISALLOW_ALL` | `NOT_RUN` | `ROUTE_NOT_ALLOWED` |
| **M · documento/carrossel** | ✔ | ✘ | ✘ | — | — | — | `UNKNOWN` | **`NOT_RUN`** | `DISALLOW_ALL` | `NOT_RUN` | nunca tentado **e** rota fora |
| **N · audio-only** | ✘ | ✘ | ✘ | — | — | — | `UNKNOWN` | — | — | **`NOT_NEEDED_FOR_THIS_ROUTE`** | a legenda resolveria antes |
| **O · ASR local** | ✔ | n/a | n/a | `fala_local` | local | nenhuma | `ZERO` | — | n/a | **`ASR_REQUIRED = NO`** | — |

**Profundidade:**

```
RECENT_DISCOVERY_DEPTH     = NOT_RUN nesta missão (10–13 ids medidos em 2026-09, rota hoje fora)
HISTORICAL_DISCOVERY_DEPTH = NOT_RUN
OLDEST_REACHED             = NOT_RUN
PAGINATION                 = NOT_RUN
STOP_REASON                = ROUTE_NOT_ALLOWED — a política, não o limite da plataforma
```

---

## H · A ÁRVORE DO ÁUDIO

```
VIDEO POST → existe legenda nativa utilizável?
             SIM → preservar como CAPTION.  ASR não necessário.
```

Historicamente a legenda existia, servida ao lado, e o endereço dizia
`video-auto-caption-srt-acs-singleton` — **SRT automática**, ASR de outra casa.

```
CAPTION != TRANSCRIPT.  AUTOMATIC_CAPTION != MANUAL_CAPTION.
Mais barata, não melhor.
```

```
LINKEDIN_AUDIO_ONLY  = NOT_NEEDED_FOR_THIS_ROUTE
LINKEDIN_ASR_NEEDED  = NO
ASR_OWNERS           = 1
```

Não se cria trabalho de ASR só porque a casa tem ASR.

---

## I · CUSTO

```
COST_USD                = 0,00   nesta missão
APIFY_RUNS              = 0
HARVESTAPI_PAID_RUNS    = 0
OFFICIAL_API_COST       = NOT_APPLICABLE (sem acesso)
LOCAL_COST              = ZERO
```

Histórico, preservado e **não repetido**: `harvestapi` a US$ 4,03/1 000, com
US$ 0,484 gastos em 120 perfis registados pela própria matriz.

```
ZERO_APIFY != ZERO_PAID_PROVIDER.  E aqui os dois são zero — nesta missão.
```

Credenciais de LinkedIn, Apify ou HarvestAPI neste ambiente: **nenhuma**.

---

## J · DELTA CONTRA O HISTÓRICO

| item | histórico | C11 | classificação |
|---|---|---|---|
| discovery recente | PROVEN | `NOT_RUN` · rota fora | **REGRESSED_IN_AUTHORIZATION** |
| post direto | PROVEN | `NOT_RUN` · rota fora | **REGRESSED_IN_AUTHORIZATION** |
| vídeo nativo | PROVEN | `NOT_RUN` · rota fora | **REGRESSED_IN_AUTHORIZATION** |
| legenda SRT | PROVEN | `NOT_RUN` · rota fora | **REGRESSED_IN_AUTHORIZATION** |
| discovery histórico | UNKNOWN | `NOT_RUN` | UNCHANGED |
| comentários | UNKNOWN | `NOT_RUN`, com first break nomeado | UNCHANGED, mais preciso |
| documentos | NOT_EXECUTED | `NOT_RUN`, com first break nomeado | UNCHANGED, mais preciso |
| **busca por palavra-chave** | não era eixo | **FLOW_OBSERVED, 372 posts** | **NOT_COMPARABLE** — eixo que faltava |
| **API oficial para terceiros** | não medido | **estruturalmente inexistente** | **NOT_COMPARABLE** — achado novo |
| identidade indireta | PARTIAL 1/3 (C9) | PARTIAL 1/2 alcançáveis | UNCHANGED |

Nenhuma capacidade técnica desapareceu. O que mudou foi a casa ter lido a
política e declarado a rota fora.

```
TECHNICALLY_PROVEN ONTEM + ROUTE_NOT_ALLOWED HOJE = REGRESSÃO DE AUTORIZAÇÃO,
não perda de capacidade técnica.
```

---

## K · COMPATIBILIDADE DE SAÍDA

Sem integrar, e só olhando para o que os 372 posts preservados já carregam:

| capability | compatibilidade | porquê |
|---|---|---|
| identidade indireta | **COMPATIBLE** | devolve handle + URL; cabe em `DISCOVER_ACCOUNT` |
| busca por palavra-chave | **NEEDS_ADAPTER_WORK** | os registos preservados têm `SOURCE_ID` de fonte, `EXTERNAL_ID`, `URL`, `TEXT`, métricas e datas separadas — mas nasceram fora do executor SCRAP, sem trace de fornecedor |
| tudo o resto | **UNKNOWN** | não há saída para avaliar |

```
CAN BE COMPATIBLE != IS WIRED.
```

---

## L · RED TEAM — 22 tentativas

| # | ataque | resultado |
|---|---|---|
| 1 | módulo existe mas ninguém chama | **apanhado** — 0 funções públicas, 0 edges |
| 2 | benchmark antigo como atual | **apanhado** — coluna própria, e 4 REGRESSED_IN_AUTHORIZATION |
| 3 | URL direta tratada como discovery | resistiu — linhas separadas |
| 4 | recente tratado como histórico | resistiu — histórico é `NOT_RUN`, não «raso» |
| 5 | identidade tratada como conteúdo | **apanhado** — 44 identidades ≠ 372 posts |
| 6 | caption como transcript | resistiu |
| 7 | caption automática como manual | resistiu — `acs-singleton` diz automática |
| 8 | vídeo acessível como audio-only | resistiu — `NOT_NEEDED_FOR_THIS_ROUTE` |
| 9 | provider configurado como executado | **apanhado** — `ATORES` configura, `APIFY_RUNS = 0` |
| 10 | rota paga como custo zero | resistiu — US$ 4,03/1 000 declarado |
| 11 | zero Apify como custo zero total | resistiu |
| 12 | credencial como autorização | resistiu — nenhuma credencial, e não mudaria a política |
| 13 | API oficial existe = acesso concedido | **apanhado, e vai mais longe**: nem com acesso a API lê terceiros |
| 14 | 403 de site de organização como bloqueio do LinkedIn | **apanhado** — 5 de 7 sentinelas |
| 15 | IP de datacenter como incapacidade da plataforma | **apanhado** — idem |
| 16 | uma sentinela falhou = BLOCKED | **apanhado** — 7 sentinelas, não 1 |
| 17 | política proibiu o teste = plataforma BLOCKED | **apanhado** — vocabulário `NOT_RUN`, nunca `BLOCKED` |
| 18 | `NOT_RUN` como `UNKNOWN` | resistiu |
| 19 | robots como parecer jurídico | resistiu — facto sobre um ficheiro, citado literalmente |
| 20 | SRT automático como fala humana | resistiu |
| 21 | render de documento como RAW original | resistiu — `NOT_RUN`, nada renderizado |
| 22 | capacidade histórica como PROVEN atual | **apanhado** — nenhuma das sete está PROVEN hoje |

E um que me apanhou a mim: a sonda de descoberta indireta, na primeira
passagem, herdava o ficheiro do site anterior e inventava dois acertos.

---

## M-bis · LINKEDIN VIDEO / SPEECH COVERAGE

Medido em 2026-09-11, em continuação da mesma missão. Aqui a pergunta é uma só:

> quando uma publicação do LinkedIn tem vídeo, o SINTONIA consegue preservar o
> que foi **falado**, sem baixar o vídeo inteiro?

```
LINKEDIN_SPEECH_COVERAGE = EXACT_BLOCKER_KNOWN
```

### Por que isto não é detalhe

Um post pode dizer «veja a nossa nova solução» e o vídeo explicar três minutos
de doença, molécula, lançamento e manejo. Guardar texto, likes e comentários
guarda a moldura e perde o quadro.

```
POST_CAPTURED != SPEECH_CAPTURED.
```

### O achado que fecha a pergunta antes de ela chegar à rede

Os 372 posts que esta casa preservou por `harvestapi~linkedin-post-search` têm
**dezanove campos**, e nenhum deles é de mídia:

```
AUTHOR_URL · CAPTURE_DATE · COMMENTS_COUNT · CONTENT_ID · DECLARED_AUTHOR
DISCOVERY_QUERY · EXTERNAL_ID · FACT_LOCATION · LIKES · ORIGINALITY
ORIGIN_ID · PLATFORM · PUBLICATION_DATE · RUN_ID · SHARES · SOURCE_ID
SOURCE_LOCATION · TEXT · URL
```

Zero `video`. Zero `media`. Zero `caption`. Zero `thumbnail`. Zero `duration`.
Zero URN de asset.

E **onze desses posts falam de vídeo no próprio texto**. O registo deles é
idêntico ao dos outros: só texto.

```
O PROVIDER QUE ESTA CASA REALMENTE RODOU NÃO DETECTA VÍDEO — QUANTO MAIS FALA.
```

Isto não é leitura da documentação do provider. É o payload que ele devolveu,
preservado no disco, contado campo a campo.

```
PROVIDER_DOCS != CURRENT_PROVEN.  E aqui o PROVEN mediu-se, e deu vazio.
```

### A API oficial de vídeo, medida contra a documentação corrente

`Videos API`, `li-lms-2026-08`, doc atualizada em 2026-03-02.

| pergunta | resposta medida |
|---|---|
| `OFFICIAL_VIDEO_METADATA` | **SIM** — `duration`, `aspectRatio`, `thumbnail`, `status` |
| `OFFICIAL_VIDEO_DOWNLOAD` | **SIM** — `downloadUrl` assinado, com `downloadUrlExpiresAt`; a amostra é `dms.licdn.com/playlist/…/mp4-720p-30fp-crf28/…` |
| `OFFICIAL_CAPTION` | **PARCIAL, e não o que parece** |
| `OFFICIAL_AUDIO_ONLY` | **NÃO EXISTE** |
| `THIRD_PARTY_ORG_ACCESS` | **NÃO** |

Três coisas que só se veem lendo a tabela de permissões inteira:

**1. A Videos API é de ESCRITA.** As permissões listadas são
`w_organization_social`, `w_member_social`, `rw_ads` e `r_ads`. **`r_organization_social`
não aparece.** E a regra de acesso é explícita: *«For videos with company URN
owners, the caller needs to have ADMIN or DSC permissions for the company page»*,
com 403 caso contrário.

**2. O campo `captions` é a legenda QUE VOCÊ SUBIU.** A própria definição:
*«Present if `initializeUploadRequest.uploadCaptions` was true and a caption was
successfully uploaded and processed»*. O formato é SRT, `source: USER_PROVIDED`,
`transcriptType: CLOSED_CAPTION`, e **só inglês**. Não é a legenda automática de
um post de terceiro — é o eco do ficheiro que o próprio parceiro enviou.

**3. Não há representação de áudio em lado nenhum.** O `downloadUrl` é uma
rendição de vídeo. Não existe faixa, manifesto ou variante de áudio.

```
MESMO COM ACESSO TOTAL DE PARCEIRO, A API OFICIAL DÁ:
  · vídeo inteiro da organização que a casa administra
  · a legenda que a casa mesma subiu
NENHUMA DAS DUAS SERVE PARA OBSERVAR UM CONCORRENTE.
```

A rota oficial é inútil aqui por **dois** motivos independentes, e corrigir um
não corrige o outro: dono errado **e** sem áudio separado.

### A árvore de decisão, percorrida até onde a política deixa

```
VIDEO POST
   ↓
CAPTION NATIVA EXISTE E TEM ROTA PERMITIDA?
   └─ NÃO há rota permitida para nenhum conteúdo do linkedin.com
      ↓
ROTA AUDIO-ONLY EXISTE E É PERMITIDA?
   └─ NÃO
      ↓
   REQUIRES_AUTHORIZATION
```

A árvore não chega ao segundo nó por falta de técnica. Chega por falta de porta.

### A MATRIZ VIDEO / SPEECH

| capability | MODULE | EDGE | FLOW | ROUTE | PROVIDER | AUTH | POLICY | CAPTION_STATE | CAPTION_KIND | AUDIO_STREAM_AVAILABLE | AUDIO_ONLY_REQUESTABLE | AUDIO_ONLY_OBSERVED | ASR_REQUIRED | VERDICT | FIRST_BREAK |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `LINKEDIN_VIDEO_POST_DISCOVERY` | ✘ | ✘ | **✘** | busca paga | HarvestAPI | token | `ROUTE_NOT_ALLOWED` | n/a | n/a | n/a | n/a | n/a | n/a | **`BLOCKED`** | o provider não devolve campo de mídia nenhum — medido em 372 registos |
| `LINKEDIN_VIDEO_ASSET_RESOLUTION` | ✔ decl. | ✘ | ✘ | web pública / API oficial | HTTP próprio / oficial | nenhuma / ADMIN | `DISALLOW_ALL` / restrita | n/a | n/a | `UNKNOWN` | `UNKNOWN` | **NÃO** | n/a | **`NOT_RUN`** | web: `ROUTE_NOT_ALLOWED`. oficial: exige ser dono |
| `LINKEDIN_NATIVE_CAPTION` | ✔ decl. | ✘ | ✘ | web pública | HTTP próprio | nenhuma | `DISALLOW_ALL` | histórico: existia | **`AUTOMATIC`** por evidência de URL (`video-auto-caption-srt-acs-singleton`) | n/a | n/a | ✘ | **NO** se resolver | **`NOT_RUN`** | `ROUTE_NOT_ALLOWED` |
| `LINKEDIN_CAPTION_KIND` | — | — | — | — | — | — | — | — | `AUTOMATIC` histórico · `UNKNOWN` hoje | — | — | — | — | **`PARTIAL`** | a prova de tipo é do endereço, não de um campo declarado |
| `LINKEDIN_AUDIO_ONLY_STREAM` | ✘ | ✘ | ✘ | — | — | — | — | n/a | n/a | **`UNKNOWN` na web · `NÃO` no oficial** | `UNKNOWN` | ✘ | n/a | **`UNKNOWN`** | não sondado: `ROUTE_NOT_ALLOWED`. Oficial não expõe áudio |
| `LINKEDIN_AUDIO_ONLY_ACQUISITION` | ✘ | ✘ | ✘ | — | — | — | — | n/a | n/a | — | — | **✘** | n/a | **`REQUIRES_AUTHORIZATION`** | nenhuma rota permitida alcança mídia do LinkedIn |
| `LINKEDIN_LOCAL_ASR` | ✔ | n/a | n/a | `fala_local` | local | nenhuma | n/a | n/a | n/a | n/a | n/a | n/a | — | **`CAN_RECEIVE_AUDIO = YES`** | não é o gargalo |
| `LINKEDIN_TRANSCRIPT_LINEAGE` | ✔ (desenho) | ✘ | ✘ | — | — | — | — | — | — | — | — | — | — | **`COMPATIBLE, NOT WIRED`** | sem áudio não há pai para o transcript |

### Os três casos obrigatórios

```
CASO A · vídeo COM caption nativa   → NOT_FOUND nesta missão
CASO B · vídeo SEM caption nativa   → NOT_FOUND nesta missão
CASO C · fala bloqueada/autorização → ENCONTRADO, e é o caso de TODOS
```

Não se fabricou A nem B. Para os encontrar seria preciso abrir um post de vídeo
no `linkedin.com` — que é exatamente a rota que a política declara fora. O
caso C não precisou de sentinela: ele é o estado da plataforma inteira para esta
casa.

```
WHAT_WAS_TRIED          os 372 posts preservados (sem mídia); a documentação
                        oficial de Videos, Posts e Community Management; o
                        robots.txt; o ecossistema de bibliotecas não oficiais
FIRST_BREAK             nenhuma rota permitida alcança mídia do linkedin.com
WHAT_IS_REQUIRED        uma decisão de autorização do coordenador — e, mesmo
                        com ela, um provider que devolva ASSET ou CAPTION,
                        que o atual não devolve
```

### O ecossistema não oficial, estudado e não executado

As bibliotecas conhecidas do género `tomquirk/linkedin-api` e derivadas operam
sobre o **Voyager**, a API interna que o site usa, e todas exigem **sessão
autenticada**. Estudá-las como tecnologia é permitido; usá-las não é —
§23 proíbe login e cookie para contornar a política da casa.

```
AUTH_MODEL        = LOGIN_SESSION
MAINTENANCE_RISK  = alto (API interna, sem contrato)
VIDEO_SUPPORT     = UNKNOWN — a busca desta missão não achou prova específica
CAPTION_SUPPORT   = UNKNOWN — idem
```

Este é um `UNKNOWN` honesto e não um `BLOCKED`: a procura foi feita e não
devolveu evidência específica de vídeo/legenda. Não se completa com hipótese.

### RED TEAM DE VÍDEO — 16 tentativas

| # | ataque | resultado |
|---|---|---|
| 1 | thumbnail chamada de video asset | resistiu — o provider não devolve nem thumbnail |
| 2 | URL de vídeo chamada de audio-only | resistiu — `downloadUrl` é rendição `mp4-720p` |
| 3 | caption chamada de transcript | resistiu |
| 4 | auto-caption chamada de manual | **apanhado** — o campo oficial `captions` é `USER_PROVIDED`; a automática vinha do endereço da web |
| 5 | `yt-dlp -x` chamado audio-only sem medir bytes | n/a — nada foi baixado |
| 6 | MP4 baixado e convertido chamado audio-only | n/a — `VIDEO_BYTES_DOWNLOADED = 0` |
| 7 | docs do provider chamadas de PROVEN atual | **apanhado** — mediu-se o payload, não o folheto |
| 8 | signed URL expirada chamada capability BLOCKED | resistiu — nenhuma URL foi pedida |
| 9 | uma sentinela muda chamada plataforma bloqueada | resistiu — o bloqueio é de política, não de sentinela |
| 10 | vídeo sem fala chamado download failure | resistiu — os quatro estados ficam separados |
| 11 | caption ausente chamado audio unavailable | resistiu — linhas próprias na matriz |
| 12 | audio stream no manifesto chamado adquirido | resistiu — `AUDIO_ONLY_OBSERVED = ✘` |
| 13 | browser toca = download permitido | resistiu — tocar não é adquirir, e nem se tocou |
| 14 | acesso oficial a vídeo de página própria extrapolado para concorrentes | **apanhado** — é o erro central que esta secção existe para impedir |
| 15 | rota de metadata chamada de rota de mídia | **apanhado** — a Videos API dá metadata de ASSET PRÓPRIO |
| 16 | ASR local PROVEN a esconder aquisição BLOCKED | **apanhado** — `ASR_BLOCKED_BY_ACQUISITION = YES` |

O 16 é o mais perigoso desta casa, porque o ASR **funciona**. Ter um motor bom
não move a fala do LinkedIn um milímetro para perto.

```
ASR LOCAL PROVEN + AQUISIÇÃO BLOQUEADA = FALA NÃO CAPTURADA.
O motor não é o gargalo. A porta é.
```

### O QUE ISTO MUDA NO RANKING

O gap escolhido antes desta continuação era **resolver o conflito de política**.
Ele continua a ser o próximo passo — mas por um motivo agora maior, e com uma
condição nova que o censo anterior não sabia:

```
AUTORIZAR A ROTA PAGA QUE JÁ EXISTE NÃO COMPRA FALA.
```

O `harvestapi~linkedin-post-search`, como esta casa o rodou, devolve texto e
métricas e **nada de mídia**. Se amanhã o coordenador autorizasse aquela rota,
o SINTONIA continuaria sem saber o que foi dito nos vídeos.

Por isso a decisão de política deixa de ser «ligar ou não ligar o que já existe»
e passa a ser duas perguntas separadas:

1. autorizamos alguma rota para conteúdo do LinkedIn?
2. se sim, **qual rota devolve ASSET ou CAPTION** — porque a que temos não devolve?

Isso não troca o vencedor por inércia. Redefine-o, e o redefinir veio da medição
de vídeo.

```
SPEECH_CAPABILITY = CRITICAL
```

### CUSTO E POLÍTICA DESTA CONTINUAÇÃO

```
PAID_RUNS = 0 · APIFY_RUNS = 0 · HARVESTAPI_PAID_RUNS = 0 · COST_USD = 0,00
FULL_VIDEO_DOWNLOAD_FOR_ASR_TEST = NÃO EXECUTADO (proibido, e não se contornou)
VIDEO_POLICY_STATE = ROUTE_NOT_ALLOWED para toda mídia do linkedin.com
```

---

## M · RANKING DOS GAPS DO LINKEDIN

Escala 0–5; esforço, risco e dependências invertidos.

| # | gap | valor | freq. | EAME | custo | fragil. | rota oficial | esforço⁻¹ | risco⁻¹ | reuso | dep.⁻¹ | total |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **1** | **decisão de autorização sobre a rota de busca por palavra-chave** | 5 | 4 | 5 | 3 | 5 | 1 | 4 | 1 | 3 | 4 | **35** |
| 2 | resolver o conflito `ATORES` × `social_matriz` | 3 | 3 | 3 | 3 | 5 | 5 | 5 | 4 | 4 | 5 | 40 |
| 3 | ligar identidade indireta ao registo | 3 | 3 | 4 | 4 | 2 | 5 | 4 | 5 | 3 | 5 | 38 |
| 4 | discovery histórico de página de empresa | 4 | 2 | 4 | 2 | 2 | 0 | 2 | 0 | 2 | 1 | 19 |
| 5 | documentos/carrosséis | 3 | 2 | 3 | 2 | 1 | 0 | 2 | 0 | 1 | 1 | 15 |

**O ranking bruto põe o #2 à frente, e é por isso que o score não decide
sozinho.** O #2 e o #3 são obras de engenharia que a casa faz sem pedir licença
a ninguém; o #1 é uma decisão que só o coordenador pode tomar — e enquanto ela
não existir, o #2 e o #3 arrumam a casa à volta de uma capacidade que continua
proibida.

```
ONE_NEXT_LINKEDIN_GAP = RESOLVER O CONFLITO DE POLÍTICA `ATORES` × `social_matriz`
```

Escolhido porque é o único onde **fazer nada é ativamente perigoso**: há hoje um
caminho de código alcançável (`fase_posts('LINKEDIN')` → `executar_com_pool`)
para uma rota que o dono da política declara `ROUTE_NOT_ALLOWED`. Só falta um
token. Nenhum dos outros quatro tem essa propriedade.

E ele não decide a pergunta grande — apenas garante que a pergunta grande seja
**decidida** em vez de acontecer por acidente.

---

## N · VEREDITO

```
LINKEDIN_CURRENTLY_USEFUL           = PARTIAL
LINKEDIN_BEST_CURRENT_CAPABILITY    = descoberta INDIRETA de identidade,
                                      pelo site da organização
LINKEDIN_BIGGEST_BLOCKER            = autorização, e não técnica.
                                      robots.txt `Disallow: /` para o nosso
                                      agente, e a API oficial estruturalmente
                                      incapaz de ler terceiros
LINKEDIN_SPEECH_COVERAGE            = EXACT_BLOCKER_KNOWN
ONE_NEXT_LINKEDIN_GAP               = resolver o conflito de política — e agora
                                      com a pergunta partida em duas, porque
                                      autorizar a rota que já existe NÃO compra fala
LINKEDIN_NEEDS_ASR_NOW              = NO
ASR_BLOCKED_BY_ACQUISITION          = YES
LINKEDIN_PAID_PROVIDER_REQUIRED_NOW = YES para conteúdo — e a rota paga
                                      está declarada ROUTE_NOT_ALLOWED,
                                      então na prática: nenhuma rota
```

O LinkedIn é útil hoje para **saber quem é**, não para **saber o que disse**.

E a frase que a §32 pede, numa linha:

> **Hoje o SINTONIA NÃO consegue recuperar a fala de vídeos do LinkedIn, em
> condição nenhuma: não há rota permitida que alcance mídia da plataforma; o
> provider pago que esta casa já rodou devolve texto e métricas e nenhum campo
> de mídia, medido em 372 registos preservados; e a API oficial, mesmo com
> acesso total de parceiro, só entrega vídeo de página que a casa administra e
> legenda que a casa mesma subiu, sem qualquer representação de áudio separada.**

`LINKEDIN_CURRENTLY_USEFUL = PARTIAL` e não `YES` exatamente por isso: texto e
identidade têm caminho, fala não tem nenhum.

---

## O · O QUE FICA DESCONHECIDO

Profundidade histórica real, paginação, comentários, documentos/carrosséis,
imagem, e se a legenda SRT continua servida — **todos pelo mesmo motivo**: a
rota que os mediria está declarada fora, e esta missão não a executou.

E uma que é medível sem violar nada: quantas das organizações que a casa segue
publicam o handle no próprio site. Mediu-se 1 de 2 alcançáveis, de 7 tentadas.

---

## P · RISCO RESTANTE

1. **O conflito de política é alcançável em runtime.** Um token de Apify neste
   ambiente e `fase_posts('LINKEDIN')` executa a rota proibida.
2. **372 posts preservados vieram por essa rota.** O material está no disco e é
   histórico; o que não pode é nascer mais por ali sem decisão.
3. **Cinco das sete sentinelas não responderam** — este IP de datacenter vê uma
   fatia estreita da web, e isso limita a própria descoberta indireta.
4. A API oficial pode mudar. A medição é de 2026-09-11, contra `li-lms-2026-08`.

---

## Q · FECHO

```
C11_LINKEDIN_CENSUS = PASS
NEW_OPERATIONAL_DIFF = 0
APIFY_RUNS = 0 · HARVESTAPI_PAID_RUNS = 0 · COST_USD = 0,00
ASR_OWNERS = 1
KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA
BÍBLIA/CONTRATO = NÃO precisa mudar

HARD STOP.
```

`KNOW_HOW_DELTA` não é NENHUM desta vez, e o motivo é um só achado:

```
O QUE          a API oficial do LinkedIn não tem, em nenhum tier, rota de
               leitura do conteúdo de organização que não se administra
POR QUÊ        `r_organization_social` exige papel de admin na organização-alvo;
               `r_member_social` está CLOSED e não aceita pedidos
PROVA          docs `li-lms-2026-08`, atualizadas em 2026-05-13 e 2026-05-15
CONSEQUÊNCIA   «pedir acesso à API» sai do conjunto de opções para sempre.
               Não é um degrau que falta subir: é um degrau que não existe.
```

Isso é limitação estrutural e durável, que é exatamente o critério. As outras
leis desta missão — `CAPTION != TRANSCRIPT`, `IDENTITY != CONTENT`,
`ZERO_APIFY != ZERO_PAID_PROVIDER` — já são canônicas e não se duplicam.
