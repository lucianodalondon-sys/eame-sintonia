# C11 · LINKEDIN CAPABILITY DEEP CENSUS

```
CENSO_DATADO_EM     = 2026-09-11
HEAD_MEDIDO         = 231ffa2c07fd500ae663d2f1a8e38417976370e1
C11_LINKEDIN_CENSUS = PASS
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
ONE_NEXT_LINKEDIN_GAP               = resolver o conflito de política
LINKEDIN_NEEDS_ASR_NOW              = NO
LINKEDIN_PAID_PROVIDER_REQUIRED_NOW = YES para conteúdo — e a rota paga
                                      está declarada ROUTE_NOT_ALLOWED,
                                      então na prática: nenhuma rota
```

O LinkedIn é útil hoje para **saber quem é**, não para **saber o que disse**.

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
