# LINKEDIN-POLICY-01 — QUAIS ROTAS DE CONTEÚDO O SINTONIA PODE USAR

```
LINKEDIN_ROUTE_POLICY = PASS_NO_CONTENT_ROUTE_ALLOWED
                        + PENDING_HUMAN_DECISION em 3 rotas

LINKEDIN_PLATFORM_REQUESTS = 0 · LICDN_REQUESTS = 0
APIFY_RUNS = 0 · PAID_RUNS = 0 · COST_USD = 0,00
POLICY_FILE_CHANGED_BY_THIS_MISSION = NAO
   `leis/social_matriz.py` MUDOU nesta arvore — pela fusao da C10.8B-LIVE,
   que acrescentou `PARTIAL` ao vocabulario e reclassificou `apify:transcricao`
   do YouTube. Nenhuma dessas linhas e desta missao, e nenhuma e de LinkedIn.
CAPABILITY_STATE_CHANGED = NAO
ROTA_NOVA_IMPLEMENTADA = NENHUMA
```

> Esta missão **decide**; não constrói. O veredito curto: **nenhuma rota de
> aquisição de conteúdo de terceiros no LinkedIn está autorizada hoje**, e três
> rotas ficam explicitamente em `PENDING_HUMAN_DECISION` com a pergunta escrita.
> O que fica `ALLOWED_NOW` é identidade fora do LinkedIn e reprocessamento do
> que já foi adquirido.

---

## 0 · REGRA ZERO

```
CURRENT_BRANCH = claude/festive-fermi-1k2mf5
CURRENT_HEAD   = b47295f6  no início desta missão
                 → fundido com cfbb80c2 (C10.8B-LIVE) em b36cb1b5
                 → o commit desta entrega é filho dele
REMOTE_HEAD    = b47295f6 no início; igual ao local no fim
WORKTREE       = LIMPA
```

    O COMMIT DESTA ENTREGA NÃO PODE ESCREVER O PRÓPRIO SHA AQUI — é a mesma
    razão pela qual o mapa não carimba o seu. O que se escreve é o PAI, que é
    verificável, e a impressão da árvore prova o resto.

### A missão anterior, localizada e PROVADA

```
LINKEDIN_BUILD_BRANCH     = claude/festive-fermi-1k2mf5
LINKEDIN_BUILD_FINAL_HEAD = b47295f6c6f32bbc5e1119a1eb25bd8524df8994
REMOTE_HEAD               = b47295f6  (igual, no remoto)
REPORT                    = docs/sintonia-scrap/LINKEDIN-BUILD-01-LOCAL-FIRST.md
COMMIT_QUE_A_INTRODUZIU   = a418f040, e ele está no remoto
LINKEDIN_BUILD_GIT_STATE  = **PROVEN**
```

Provado por três medições independentes, não por memória: o único ramo remoto
que contém o artefato, a linha onde o veredito `LINKEDIN_LOCAL_FIRST = PARTIAL`
vive, e `git branch -r --contains` sobre o commit que o criou.

### E a linha andou outra vez — com evidência que esta missão precisava

`claude/sintonia-scrap-first-paid-route-c10-8b` avançou para `cfbb80c2` com a
**C10.8B-LIVE**: a primeira rota paga REAL desta casa correu. Fundida para cá
antes de decidir qualquer coisa, porque ela responde empiricamente à pergunta
mais difícil desta missão (§7 e §8).

---

## 1 · INVENTÁRIO DAS ROTAS

| | rota | `TECH_POSSIBLE` | `CURRENT_POLICY` | `AUTH` | `3P_CONTENT` | `TERMS_STATUS` | `ROBOTS` | `COST` | `CURRENT_PROOF` | `CANONICAL_OWNER` |
|---|---|---|---|---|---|---|---|---|---|---|
| **R1** | off-LinkedIn identity discovery | **YES** | **ALLOWED** | nenhuma | **NO** — lê o site da organização | fora do §8.2 (não é «the Services») | do site da organização, não do LinkedIn | **0** | `PARTIAL` · 1 de 2 alcançáveis de 7 sentinelas | `linkedin.identity.discovery` |
| **R2** | LinkedIn Official API | YES, restrita | `ROUTE_NOT_ALLOWED` | OAuth + papel de admin | **NO** para terceiros | permitido, mas só para páginas próprias | n/a | partner-gated | doc `li-lms-2026-08` | `social_matriz` |
| **R3** | public unauthenticated LinkedIn | **YES**, medido | **`ROUTE_NOT_ALLOWED`** | nenhuma | **YES** | §8.2(1) alcança | `DISALLOW_ALL` (2026-09-11) | 0 | `PROVEN` histórico, 2026-09-08 | `social_matriz` |
| **R4** | authenticated / Voyager | YES, com sessão | **`NOT_ALLOWED`** | login/cookie | YES | §8.2(1)+(3) | `DISALLOW_ALL` | 0 | documental | `social_rotas` (§23) |
| **R5** | search engine index | YES | **dividida** — ver §6 | nenhuma | **snippet, não post** | §8.2(4) nomeia «search tools» | do buscador | 0 | documental | `social_matriz` |
| **R6** | external paid provider | **YES**, medido | `ROUTE_NOT_ALLOWED` | token do provider | YES | **§8.2(4) nomeia «data aggregators or brokers»** + GTC do provider | n/a | `MEASURED` US$ 4,033/1.000 | `coletor.py` |
| **R7** | reprocessing de RAW já adquirido | **YES** | **ALLOWED** | nenhuma | o conteúdo já está cá | nenhuma nova aquisição | n/a | **0** | `PASS` — 472 itens, LINKEDIN-BUILD-01 | `adaptador_linkedin` |
| **R8** | direct media asset presente em RAW válido | **NO, hoje** | **`BLOCKED_EXPIRED`** | nenhuma | YES | §8.2(1)+(4) para o CDN | `licdn.com` **NUNCA medido** | 0 | os endereços preservados **expiraram** | `adaptador_linkedin` |

---

## 2 · O QUE JÁ SE PODE FECHAR

### R1 — `ALLOWED`, e a razão não é conveniência

```
DECISAO: ALLOWED
```

Ela não lê conteúdo do LinkedIn. Lê o site **da própria organização** e devolve
o endereço. O §8.2(4) alcança informação obtida «from the Services, whether
directly or through third parties (such as search tools or data aggregators or
brokers)» — e o site da empresa não é «the Services», nem é um buscador, nem é
um broker.

    IDENTITY != CONTENT. E esta rota fica do lado da identidade por construção:
    o campo `POST_CONTENT` existe no objecto e é sempre `None`.

Limite declarado: devolve **handle**, nunca publicações. E a cobertura é
estreita — 1 de 2 sentinelas alcançáveis, de 7 tentadas, porque cinco sites de
terceiros recusaram este IP de datacenter. **Nenhuma dessas falhas é do
LinkedIn.**

### R7 — `ALLOWED`, e é a rota mais valiosa que esta casa tem hoje

```
DECISAO: ALLOWED
```

    REPROCESSAR O JÁ ADQUIRIDO != FAZER NOVA AQUISIÇÃO.

E a casa já tinha escrito a mesma lei, na C10.8B-LIVE, com outras palavras:
*«RELER O QUE JÁ SE PAGOU NÃO É PAGAR OUTRA VEZ.»* Duas missões chegaram lá
por caminhos diferentes, o que é o sinal de que a lei é real.

O que isto autoriza, medido nos 472 itens preservados: texto, autor, data
exacta, likes, partilhas, contagem de comentários, **agregados de tipo de
reacção (449)**, **endereços de vídeo (56)**, **endereços de documento com
manifesto de transcrição (20)**, **links externos (93)** e imagens.

O que isto **não** autoriza: ir buscar os bytes que esses endereços apontam.
Essa é a R8, e ela é outra rota.

### R8 — `BLOCKED_EXPIRED`, e por dois motivos independentes

```
DECISAO: BLOCKED_EXPIRED  (não é o mesmo que NOT_ALLOWED)
```

1. **Os endereços já não abrem.** `e=1788580800` → 2026-09-05T04:00:00Z para o
   vídeo; `e=1788998400` para o manifesto do documento. Os dois passaram.
2. **O host nunca foi medido.** `dms.licdn.com` e `media.licdn.com` são hosts
   distintos do `linkedin.com`, e esta casa **assume** o robots do segundo para
   os primeiros. Assunção não é medição.

    URL EM RAW ANTIGO NÃO É AUTORIZAÇÃO PERMANENTE. E um endereço assinado que
    expirou não é uma rota bloqueada pela plataforma — é um bilhete fora da
    validade. As duas coisas produzem o mesmo `0` bytes e são diferentes.

---

## 3 · API OFICIAL

Medido contra `li-lms-2026-08`, doc actualizada 2026-05-13.

### Para organização que administramos

```
CAN_READ     = SIM
REQUIREMENTS = OAuth + papel de ADMINISTRATOR / DIRECT_SPONSORED_CONTENT_POSTER
               / CONTENT_ADMIN na organização-alvo
               + aprovação no Partner Program (não é self-service)
```

### Para organização concorrente que NÃO administramos

```
CAN_READ_PUBLIC_POSTS = **NÃO**
CAN_LIST_HISTORY      = **NÃO**
CAN_READ_COMMENTS     = **NÃO**
```

Texto literal da permissão: `r_organization_social` — «Retrieve organizations'
posts, comments, and likes. **Restricted to organizations in which the
authenticated member has one of the following company page roles**: ADMINISTRATOR,
DIRECT_SPONSORED_CONTENT_POSTER, CONTENT_ADMIN». E `r_member_social` — «This
permission is **restricted** and is available to **approved users only**».

```
API EXISTS != API ALLOWS COMPETITOR MONITORING.
```

    CLASSIFICAÇÃO EXPLÍCITA: A API OFICIAL É UMA ROTA DE PÁGINA PRÓPRIA. Para
    o caso de uso do SINTONIA — observar comunicação pública de concorrente —
    ela não é uma rota caríssima nem uma rota que falta pedir. **Ela não existe.**

E isso não muda pagando: relatos de terceiros põem o Marketing Developer
Platform em ~US$ 699/mês e acordos empresariais em US$ 50k–300k/ano. **Nenhum
desses tiers acrescenta leitura de organização de terceiro**, porque o limite é
o papel do membro autenticado, não o preço.

```
NÃO É UM DEGRAU QUE FALTA SUBIR. É UM DEGRAU QUE NÃO EXISTE.
```

---

## 4 · PUBLIC LINKEDIN — a decisão revalidada

Quatro eixos, separados de propósito:

| eixo | estado | evidência |
|---|---|---|
| `PUBLICLY_VIEWABLE` | **YES** | HTTP 200, 395 126 bytes, 11 activity ids, medido 2026-09-08 |
| `ROBOTS_ALLOWED` | **NO** | `User-agent: * → Disallow: /`; só `LinkedInBot` tem `Allow`. Medido 2026-09-11 |
| `TERMS_ALLOWED` | **NO** | §8.2(1) proíbe «scripts, robots … to scrape the Services» |
| `SINTONIA_POLICY_ALLOWED` | **NO** | `social_matriz` marca `FETCH_POST` `PERMITIDA=NAO` nas duas rotas |

```
PUBLIC_LINKEDIN_CONTENT_ROUTE = NOT_ALLOWED
```

**Motivo, e ele é de engenharia e não de advocacia:** três dos quatro eixos
respondem NO, e o eixo que responde YES — a página abre — é o único que não
decide nada.

    UMA PÁGINA PODER SER VISTA SEM LOGIN NÃO SIGNIFICA QUE O SCRAP DEVE
    AUTOMATIZÁ-LA. A casa já tinha escrito a versão geral disto em
    `docs/regras/LIMITES-DE-DADO-PESSOAL-EAME.md`:
    **`PÚBLICO ≠ LÍCITO DE PROCESSAR` · `DISPONÍVEL ≠ AUTORIZADO`.**

⚠️ Uma nuance que esta missão registra e **não** usa para mudar a decisão: a
jurisprudência citada pela comunidade (hiQ, Van Buren, Meta v. Bright Data) põe
a leitura pública deslogada no terreno mais firme, e o terreno frágil na
criação de contas falsas e na automação de sessão autenticada. Isso é contexto,
não permissão — e a `ROBOTS_STATUS` e o `TERMS_STATUS` desta plataforma
continuam ambos NO.

```
ROBOTS NÃO É PARECER JURÍDICO, E TERMS NÃO É CERTEZA JURÍDICA ABSOLUTA.
Cada um entra como UMA linha. Nenhum decide sozinho, e os três juntos decidem.
```

Não implementada. Não sondada.

---

## 5 · AUTHENTICATED / VOYAGER

```
AUTHENTICATED_VOYAGER_ROUTE = NOT_ALLOWED
```

Três razões independentes, e fechar uma não abre a rota:

1. exige sessão autenticada, e `coleta/social_rotas.py` declara por escrito que
   não faz login, não manda cookie e não finge ser navegador de gente;
2. é API **interna**, sem contrato — muda sem aviso e sem versão;
3. §8.2 proíbe «override any security feature or bypass or circumvent any access
   controls».

E uma quarta, que é a mais concreta de todas e vem de fora desta casa: **é
exactamente a fronteira onde os fornecedores perdem.** Ver §7.

Não executada. Nenhum cookie. Nenhuma conta. Nenhum login automatizado.

---

## 6 · SEARCH ENGINE INDEX — a rota que se divide em duas

```
SEARCH_DISCOVERY_ALLOWED         = PENDING_HUMAN_DECISION
SEARCH_CONTENT_SUBSTITUTE_ALLOWED = **NOT_ALLOWED**
```

A segunda fecha-se aqui e agora, sem precisar de ninguém:

    UM SNIPPET NÃO É UM POST. Ele é truncado pelo buscador, não tem data
    exacta, não tem métricas, não tem autor estruturado e não tem mídia. Tratar
    snippet como conteúdo colhido seria escrever no artefato um post que nunca
    existiu naquela forma.

    E `DISCOVER_LINKEDIN_URL != ACQUIRE_LINKEDIN_CONTENT`.

A primeira fica pendente por um conflito real que o documento não pode resolver:
o §8.2(4) nomeia **«search tools»** em claro, ao lado de «data aggregators or
brokers». Descobrir uma URL por buscador é tecnicamente útil e cai dentro de uma
cláusula que o próprio texto escreve. **A casa já tem uma rota de descoberta que
não tem esse conflito — a R1.** Enquanto a R1 cobrir a necessidade, a pergunta
não precisa de ser feita.

---

## 7 · PROVIDER PAGO — a pergunta mais importante, e ela tem resposta

### O que o contrato do fornecedor diz, lido hoje

`docs.apify.com/legal/general-terms-and-conditions`, em vigor **2026-07-09**:

> **§6.2** — «You must use the Services to process only the Customer Data that
> **you are authorized to access** and that is in compliance with all applicable
> laws and regulations.»

> **§11.1** — «Should you use the Services or Actors to extract Customer Data
> from **unauthorized sources**, **you shall be responsible** for compensating
> any damages incurred by and/or any claims of the affected third parties.»

> **§11.1** — «You agree to **indemnify, defend and hold us … harmless** from
> and against any third-party claim … arising out of … your publication or use
> of any Actors.»

> **§10.1–10.2** — nenhuma garantia de que «any Customer Data will be accurate
> or reliable»; sem responsabilidade por «changes to third-party websites».

```
O FORNECEDOR NÃO ASSUME A AUTORIZAÇÃO. ELE DEVOLVE-A AO CLIENTE, POR ESCRITO,
NO PRÓPRIO CONTRATO QUE SE ASSINA AO PAGAR.
```

    ISTO FECHA A PERGUNTA SEM PRECISAR DE ADVOGADO: comprar o Actor não
    transfere a questão da autorização. O contrato do vendedor **confirma que
    ela continua nossa** — e acrescenta que somos nós que indemnizamos.

### O censo dos fornecedores

| PROVIDER | PRODUCT | WHAT_IT_DELIVERS | HOW_IT_DESCRIBES_SOURCE | TERMS | CUSTOMER_RESP | PROVIDER_RESP | PROVENANCE | NEEDS_OUR_ACCOUNT | NEEDS_OUR_COOKIES | KNOWN_METHOD | POLICY |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Apify** (plataforma) | mercado de Actors | execução | não descreve fonte — é plataforma | **LIDOS** 2026-07-09 | **autorização + indemnização** | nenhuma sobre conteúdo | n/a | não | não | n/a | **é o contrato, não a rota** |
| **HarvestAPI** | `linkedin-post-search` e família | posts, perfis, empresas | «No cookies or account required» | **403 a este IP — NÃO LIDOS** | **UNKNOWN** | **UNKNOWN** | **UNKNOWN** | declara não | declara não | **UNKNOWN** | `ROUTE_NOT_ALLOWED` |
| **apimaestro** | posts, comentários, reações | idem | «No account needed» | não lidos | UNKNOWN | UNKNOWN | UNKNOWN | declara não | declara não | UNKNOWN | `ROUTE_NOT_ALLOWED` |
| **supreme_coder** | `linkedin-post` | posts + transcript de documento | «hybrid backend routing (API-proxy e browser-proxy)» | não lidos | UNKNOWN | UNKNOWN | UNKNOWN | declara não | declara não | **INFERRED: browser** | `ROUTE_NOT_ALLOWED` |
| **capable_cauldron** | comentários | texto de comentário | **pede cookies de sessão exportados** | não lidos | UNKNOWN | UNKNOWN | **a nossa sessão** | não | **SIM** | **`AUTHENTICATED_SESSION`, DOCUMENTED** | **`NOT_ACCEPTABLE`** |
| **s-r** | company finder | handle a partir de domínio | «Google-based search» | não lidos | UNKNOWN | UNKNOWN | índice de busca | não | não | **`SEARCH_ENGINE_INDEX`, DOCUMENTED** | **`NOT_ACCEPTABLE`** |
| **silva95gustavo** | Ad Library | criativos e faixas de impressão | «extrai de linkedin.com/ad-library» | não lidos | UNKNOWN | UNKNOWN | superfície de transparência | não | não | **`PUBLIC_HTML`, DOCUMENTED** | `NOT_DECLARED` |

**`PROVIDER_TERMS_READABLE = NO` para o fornecedor cujos dados esta casa
efectivamente possui.** `harvestapi.io` devolveu **HTTP 403** a este IP nas duas
tentativas. Isso não é um detalhe de infraestrutura: significa que a casa
comprou 472 posts e 202 perfis de um fornecedor cujos termos ela **não
conseguiu ler nesta medição**.

### As três classes

```
A · PROVIDER_ROUTE_ACCEPTABLE          → **NENHUM**
B · PROVIDER_ROUTE_REQUIRES_HUMAN_DECISION
     · HarvestAPI · apimaestro · supreme_coder
     · silva95gustavo (Ad Library — rota distinta, ver §11)
C · PROVIDER_ROUTE_NOT_ACCEPTABLE
     · capable_cauldron   exige a NOSSA sessão — e isso é a R4 comprada
     · s-r                é a R5 comprada, e §8.2(4) nomeia «search tools»
```

    `ACTOR != LEGAL/POLICY STATUS`. Nenhum destes está na classe C por ser
    Apify, e nenhum está na B por ser barato. O `capable_cauldron` cai por
    **pedir o nosso cookie**; o `s-r` cai por **declarar o mecanismo** e o
    mecanismo estar nomeado na cláusula. Os dois foram classificados pelo que
    dizem de si, não pela loja onde vivem.

### O que a evidência de fora acrescenta, e ela é recente

Da própria empresa, no seu anúncio de encerramento
(`nubela.co/blog/goodbye-proxycurl/`, **04 Jul 2025**):

> «In January earlier this year (2025), LinkedIn filed a lawsuit against
> Proxycurl.»

E a razão de não lutar, nas palavras do fundador: a *American Rule* — «even if
we were to win the lawsuit, we would not be able to claim legal fees» — e
«LinkedIn, owned by Microsoft, has more or less an unlimited war chest».

```
PRIMÁRIO (o próprio fornecedor):  processo em Jan 2025 · encerrado 04 Jul 2025
SECUNDÁRIO (blogues do sector):   alegação de contas falsas, N.D. Cal., seis
                                  fundamentos — NÃO confirmado por fonte primária
```

⚠️ **Uma correcção que esta missão fez a si mesma:** o primeiro resumo de busca
datou os dois factos em **2026**. Duas verificações contra as páginas citadas
não reproduziram a alegação, e a fonte primária dá **2025**. O ano estava errado
por um, e a correcção veio de ir ler.

    UM RESUMO DE BUSCA NÃO É EVIDÊNCIA ATÉ ALGUÉM ABRIR A FONTE.

A consequência operacional — e é só esta, sem parecer jurídico: **o maior
fornecedor de dados de LinkedIn do mercado foi processado e desligou-se**, e o
motivo declarado pelo próprio não foram os méritos, foi a assimetria económica.
Um fornecedor cujo **mecanismo é `UNKNOWN`** é um fornecedor sobre o qual a casa
não consegue dizer de que lado daquela linha ele está.

---

## 8 · NÃO COMPRAR BYPASS — a sentinela, corrida

```
SE   DIRECT_ROUTE = NOT_ALLOWED
E    o provider apenas encapsula a MESMA técnica, sem alteração de base
     contratual nem de proveniência
ENTÃO PAID_ROUTE != ALLOWED
```

Aplicada, caso a caso:

| provider | técnica encapsulada | base contratual própria? | veredito |
|---|---|---|---|
| `capable_cauldron` | **R4** (sessão autenticada) — com o **nosso** cookie | não; usa a nossa credencial | **BYPASS COMPRADO → NOT_ALLOWED** |
| `s-r` | **R5** (índice de busca) | não; e §8.2(4) nomeia a técnica | **BYPASS COMPRADO → NOT_ALLOWED** |
| `harvestapi` · `apimaestro` · `supreme_coder` | **UNKNOWN** — pode ser R3, pode ser R4 | **não estabelecida** (§6.2/§11.1 devolvem-na a nós; termos próprios não lidos) | **NÃO SE PODE AFIRMAR QUE NÃO É BYPASS → classe B** |
| `silva95gustavo` | **superfície que a plataforma publica para ser lida** | não estabelecida | rota **distinta** → §11 |

    E O TESTE TEM DE CORRER NOS DOIS SENTIDOS. Mecanismo desconhecido **não**
    é proibido automaticamente, e **não** é permitido automaticamente. Ele é
    `REQUIRES_HUMAN_DECISION`, que é a única resposta que não inventa nada.

---

## 9 · O QUE O SCRAP PODE FAZER HOJE, SEM NOVA DECISÃO

### `ALLOWED_NOW`

```
1. identity discovery off-LinkedIn            R1 · linkedin.identity.discovery
2. reprocessar RAW já adquirido               R7 · 472 itens no disco
3. metadata de documento a partir do RAW      R7 · 20 itens, com transcript URL
4. metadata de vídeo a partir do RAW          R7 · 56 itens
5. agregados de reacção já no RAW             R7 · 449 itens
6. links externos já no RAW                   R7 · 93 itens — descoberta de fonte
7. processamento local de PDF                 executor_texto_de_pdf.py
8. ASR local sobre mídia legitimamente obtida fala_local
```

Os itens 7 e 8 têm uma condição que não é decorativa: **exigem bytes que esta
casa tenha obtido por rota permitida.** Hoje, para o LinkedIn, não existem.

    `LOCAL DERIVATION != ACQUISITION PERMISSION`. Ter um extractor de PDF não
    autoriza ir buscar o PDF.

### `BLOCKED_NOW`

```
· texto de comentário          nenhuma rota permitida
· lista de quem reagiu         nenhuma rota permitida — E não se deve pedir
· bytes de vídeo               R8 expirada; R3/R6 não permitidas
· bytes de documento           idem
· legenda nativa               idem — e nenhum fornecedor pago a entrega
· duração de vídeo             não está em rota nenhuma conhecida
· listagem de posts além do RAW existente   nenhuma rota permitida
· profundidade histórica nova   nenhuma rota permitida
```

---

## 10 · MATRIZ POR CAPABILITY

| capability | `OWN_FREE` | `OFFICIAL` | `PAID_PROVIDER` | `LOCAL_DERIV` | `CURRENT_POLICY` | `CAN_EXECUTE_NOW` | `HUMAN_DECISION` | `FINAL_REASON` |
|---|---|---|---|---|---|---|---|---|
| `linkedin.identity.discovery` | **R1 SIM** | não | não precisa | não | **ALLOWED** | **SIM** | não | única rota permitida; devolve handle, não posts |
| `linkedin.recent.discovery` | R3, não permitida | não | R6, classe B | não | `NOT_DECLARED` | não | **SIM** | a página abre e os três outros eixos dizem NO |
| `linkedin.history.discovery` | nenhuma | não | R6, classe B | não | `NOT_DECLARED` | não | **SIM** | UNKNOWN fala da página de empresa; o eixo de busca é outro e está fora |
| `linkedin.direct_post` | R3, não permitida | não | R6, classe B | não | **`ROUTE_NOT_ALLOWED`** | não | **SIM** | PROVEN tecnicamente, recusada por política |
| `linkedin.native_video` | R8 **expirada** | não | R6, classe B | não | `NOT_DECLARED` | não | **SIM** | endereço em RAW não é bytes, e o `licdn` nunca foi medido |
| `linkedin.native_caption` | R3, não permitida | **não existe** | **nenhum a entrega** | ASR só depois de bytes | `NOT_DECLARED` | não | **SIM** | 0 de 472 na rota paga; a oficial é de escrita e `USER_PROVIDED` |
| `linkedin.comments` | nenhuma | não para terceiros | R6, classe B | não | `NOT_DECLARED` | **contagem SIM, do RAW** | **SIM** para o texto | `COMMENTS COUNT != COMMENTS TEXT`: 335 de contagem, 0 de texto |
| `linkedin.documents` | R8 **expirada** | não | R6, classe B | **PDF→texto SIM** | `NOT_DECLARED` | **metadata SIM, do RAW** | **SIM** para os bytes | endereço observado em 20; bytes nunca pedidos |

```
NENHUM CAPABILITY_STATE FOI ALTERADO NESTA MISSÃO.
NENHUMA LINHA DE `leis/social_matriz.py` FOI ALTERADA NESTA MISSÃO.
```

    `TECHNICAL CAPABILITY STATE` E `POLICY` SÃO DOIS EIXOS, E ESTA MISSÃO
    MEXEU NUM SÓ — o da decisão, e num documento de decisão. Mudar o estado
    de capacidade por causa de uma decisão de política seria escrever que a
    medição mudou porque a permissão mudou.

---

## 11 · DECISÕES HUMANAS NECESSÁRIAS

Três, e só três. Cada uma pára a sua rota em `PENDING_HUMAN_DECISION`.

### `HUMAN_DECISION_REQUIRED · 1`

```
ROUTE                  R3 · public unauthenticated LinkedIn
WHAT_WOULD_BE_AUTHORIZED  ler a landing pública de página de empresa e a página
                          de post directo, sem login, com o nosso agente
WHAT_DATA              texto, data, métricas, endereço de mídia — 10 a 13 posts
                       por página, sem paginação exposta
WHOSE_DATA             organizações concorrentes (e, incidentalmente, pessoas
                       que comentam ou publicam)
AUTH                   nenhuma
COST_MODEL             US$ 0 · custo de rede e de manutenção quando o HTML mudar
RISK                   robots `Disallow: /` para o nosso agente e §8.2(1)
                       explícito. A jurisprudência citada favorece leitura
                       pública deslogada, e isso é contexto e não licença.
                       Risco de bloqueio técnico (HTTP 999 após ~50–60 pedidos
                       anónimos em 15 min, segundo relato de comunidade).
WHY_NEEDED             é a única rota tecnicamente PROVADA que alcança conteúdo
                       recente sem intermediário e sem dinheiro
ALTERNATIVE            nenhuma para conteúdo. Para identidade, a R1 já cobre.
```

### `HUMAN_DECISION_REQUIRED · 2`

```
ROUTE                  R6 · external paid provider (classe B)
WHAT_WOULD_BE_AUTHORIZED  contratar um fornecedor para entregar listagem de
                          posts, histórico por termo e/ou texto de comentário
WHAT_DATA              posts públicos de organizações; e, se se pedir perfis,
                       DADO PESSOAL de pessoas nomeadas
WHOSE_DATA             concorrentes — e pessoas, no caso dos perfis
AUTH                   token do fornecedor; nenhum login nosso no LinkedIn
COST_MODEL             US$ 1,50/1.000 posts (tabela, 2026-09-12) ·
                       US$ 2,00/1.000 comentários · US$ 4,033/1.000 perfis
                       (MEDIDO nesta casa). E `READ COST != SETTLED COST`:
                       a C10.8B-LIVE leu US$ 0,00 e o estado ficou
                       `READ_NOT_SETTLED`; esta casa já anunciou US$ 0,90 e
                       pagou US$ 5,04.
RISK                   1. §8.2(4) alcança dado obtido «through third parties
                          (such as data aggregators or brokers)» — o
                          intermediário não muda a cláusula;
                       2. o contrato da própria Apify (§6.2, §11.1) devolve-nos
                          a autorização E a indemnização;
                       3. o mecanismo dos três é UNKNOWN — não se consegue dizer
                          se é leitura pública ou sessão autenticada;
                       4. os termos do fornecedor que a casa já usou não são
                          legíveis deste ambiente (HTTP 403);
                       5. precedente: o maior fornecedor do sector foi
                          processado em Jan 2025 e desligou-se em Jul 2025.
WHY_NEEDED             é a única rota que já entregou profundidade histórica
                       (2018-01-09 a 2026-08-28) e a única com caminho para
                       texto de comentário
ALTERNATIVE            reprocessar o RAW que já existe (R7) — cobre o passado
                       já comprado e não cobre nada de novo
```

### `HUMAN_DECISION_REQUIRED · 3`

```
ROUTE                  Ad Library (`linkedin.com/ad-library`)
WHAT_WOULD_BE_AUTHORIZED  ler a superfície de transparência que o próprio
                          LinkedIn publica para cumprir o DSA europeu
WHAT_DATA              anunciante, criativo, datas, CTA, país, FAIXA de
                       impressões e, no EEE, parâmetros de segmentação
WHOSE_DATA             organizações anunciantes. Sem dado pessoal.
AUTH                   nenhuma — aberta sem conta
COST_MODEL             US$ 0 pela superfície. Não há API: só UI.
RISK                   o robots desta rota **NUNCA FOI MEDIDO**, e o §8.2 não
                       abre excepção escrita para ela. Cobertura rasa: desde
                       2023-06-01, cada anúncio fica 1 ano após a última
                       impressão.
WHY_NEEDED             é a comunicação PAGA do concorrente, eixo que esta casa
                       nunca considerou, numa superfície que a plataforma
                       publica para ser lida
ALTERNATIVE            nenhuma. Não é substituível por conteúdo orgânico —
                       responde a outra pergunta.
NOTA                   decidir isto exige 1 pedido ao robots. Esta missão
                       declarou zero, e não o fez.
```

---

## 12 · SEM REDE, SEM DINHEIRO

```
LINKEDIN_PLATFORM_REQUESTS = 0     nenhum pedido a linkedin.com
LICDN_REQUESTS             = 0
APIFY_RUNS                 = 0
PAID_RUNS                  = 0
COST_USD                   = 0,00

Pesquisa feita: Apify GTC (lido) · HarvestAPI (403, NÃO lido) ·
Microsoft Learn `li-lms-2026-08` · anúncio de encerramento do Proxycurl ·
blogues técnicos do sector (secundário, marcado como tal)
```

Nenhum pedido foi feito ao `linkedin.com` — **incluindo** os resultados de busca
que apontavam para lá, que foram deliberadamente não seguidos.

---

## 13 · RED TEAM — 25 ataques

| # | ataque | resultado |
|---|---|---|
| 1 | página pública → permitida | **apanhado** — 4 eixos separados; 3 dizem NO |
| 2 | sem login → permitida | **apanhado** — `DISPONÍVEL ≠ AUTORIZADO`, lei já da casa |
| 3 | Actor pago → permitido | **apanhado** — o contrato do próprio vendedor devolve a autorização |
| 4 | Actor popular → permitido | **apanhado** — 63 K users não aparece em coluna nenhuma |
| 5 | Actor barato → permitido | **apanhado** — preço não entra na classificação A/B/C |
| 6 | robots → parecer jurídico | **apanhado** — é UMA linha de quatro |
| 7 | terms → certeza absoluta | **apanhado** — e o resumo de busca errado por um ano é a prova |
| 8 | API existe → acesso a concorrente | **apanhado** — `r_organization_social` exige papel de admin |
| 9 | snippet → post | **apanhado** — `SEARCH_CONTENT_SUBSTITUTE = NOT_ALLOWED` |
| 10 | URL discovery → aquisição | **apanhado** — R1 e R3 em linhas diferentes |
| 11 | RAW antigo → permissão nova | **apanhado** — R7 ALLOWED e R8 BLOCKED, separadas |
| 12 | MP4 em RAW antigo → autorização permanente | **apanhado** — `e=` expirado, com data |
| 13 | provider black box → aceitável | **apanhado** — classe B, nunca A |
| 14 | mecanismo desconhecido → proibido automaticamente | **apanhado** — é B, não C |
| 15 | mecanismo desconhecido → permitido automaticamente | **apanhado** — é B, não A |
| 16 | rota autenticada sem prova de cookie | **apanhado** — só `capable_cauldron` o DOCUMENTA |
| 17 | provider que pede o nosso cookie tratado como independente | **apanhado** — classe C, é a R4 comprada |
| 18 | provider com infra própria → automaticamente seguro | **apanhado** — «infra própria» não foi provada por nenhum; e Apify §6.2 devolve a autorização mesmo assim |
| 19 | comments count → comment text | **apanhado** — 335 vs 0, medido |
| 20 | native caption → ASR | **apanhado** — `CAPTION != TRANSCRIPT`, e ASR exige bytes |
| 21 | derivação local → permissão de aquisição | **apanhado** — condição escrita no `ALLOWED_NOW` |
| 22 | estado de capacidade muda política | **apanhado** — nenhum estado tocado |
| 23 | política muda prova de capacidade | **apanhado** — idem, nos dois sentidos |
| 24 | custo muda relevância | **apanhado** — US$ 699/mês não compra leitura de terceiro |
| 25 | aquisição bloqueada vira gap pago | **apanhado** — `BLOCKED_NOW` tem 8 linhas e nenhuma diz «pagar» |

### E três que esta missão virou contra si

| # | ataque | resultado |
|---|---|---|
| 26 | **resumo de busca vira facto datado** | **apanhado, e foi real** — Proxycurl datado em 2026 no primeiro resumo; a fonte primária diz 2025 |
| 27 | **D-013 citado como decisão de LinkedIn** | **apanhado** — D-013 é «inventário de população que muda é derivado». Não existe decisão de LinkedIn no diário; os precedentes reais são **D-016** (portal recusa robô → usar agregador oficial) e **D-019** (a porta abre e a chave não existe → DEMOTED) |
| 28 | **reverter uma regeração porque a anterior era só rótulo** | **apanhado, e foi real** — a fusão trouxe 5 ficheiros, o mapa contava 1 524 contra 1 529, e o carimbo disse `DIFERENTE`. Corrigido com uma regeração a sério |
| 29 | **correr o último passo da cadeia e chamar-lhe a cadeia** | **apanhado, e foi real, duas vezes** — `CADEIA-DO-MAPA.json → REGERAR` tem **sete** passos: seis scanners e o gerador. Eu corria só `generate_system_map.py`. O mapa saía montado sobre medições velhas dos scanners, o `validate` passava, e o carimbo dizia `DIFERENTE` **com a árvore limpa**. Corrigido correndo os sete. *CORRER O ÚLTIMO PASSO DE UMA CADEIA NÃO É CORRER A CADEIA.* |

    O 29 é o mais instrutivo dos três, porque o portão funcionou e eu não o
    acreditei. Ele disse `DIFERENTE` sobre uma árvore que o `git status` dizia
    limpa, e a minha primeira reacção nas duas vezes foi tratá-lo como ruído do
    SHA auto-referencial. Era um facto, e a causa estava escrita num ficheiro
    da casa que eu não tinha aberto.

---

## 14 · KNOW-HOW

O ficheiro canónico vive em `origin/claude/sintonia-eame-know-how-v1`, hoje em
**§85.7**, e **não existe nesta linha**. Esta missão não lhe toca: copiá-lo para
cá criaria a segunda cópia de uma lei, que é exactamente o que a casa proíbe.

```
KNOW_HOW_DELTA = **APLICADO** pela LINKEDIN-POLICY-CLOSE
DESTINO        = origin/claude/sintonia-eame-know-how-v1 · **§89**
HEAD_BEFORE    = 9bdcff05
HEAD_AFTER     = 977b7336
JA REGISTADO   = `PROVIDER REACHED != CAPABILITY DELIVERED` em **§84.4** —
                 **NÃO duplicado**
```

### A dívida que esta linha tinha, e que deixou de existir

Medido antes de a pagar: **três missões seguidas de LinkedIn declararam
`KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA` e nenhuma tinha sido aplicada.**

```
LINKEDIN-DEEP-STUDY-V1.md            declarou   ·  não aplicou
LINKEDIN-BUILD-01-LOCAL-FIRST.md     declarou   ·  não aplicou
LINKEDIN-POLICY-01 (esta)            declarou   ·  não aplicou
LINKEDIN-POLICY-CLOSE                            ·  **APLICOU · §89**
```

    UM DELTA DECLARADO TRÊS VEZES E NUNCA APLICADO NÃO É UM AVISO. É UMA LEI
    QUE NÃO EXISTE, COM TRÊS DOCUMENTOS A DIZER QUE DEVIA EXISTIR.

E a razão pela qual as três primeiras não o aplicaram era real e não era
preguiça: o ficheiro **não vive nesta linha**, e copiá-lo para cá criaria a
segunda cópia de uma lei. O que faltava era ir escrever no ramo que é dono dele
— o que a `LINKEDIN-POLICY-CLOSE` fez, numa worktree própria, sem tocar código
funcional nenhum.

    A LEI VIVE ONDE O DONO DELA VIVE. DECLARAR O DELTA NO DOCUMENTO CERTO E
    NUNCA ATRAVESSAR A FRONTEIRA É DEIXAR A LEI DO LADO DE FORA.

### Lei 1 — `TRANSLATION IS AUTHORIZATION`  ·  **REGISTADA em §89.1–89.4**

```
O QUE        o campo que traduz entre dois vocabulários de capacidade é uma
             SUPERFÍCIE DE PERMISSÃO, não um apelido
POR QUE      `linkedin.recent.discovery` (posts) traduzia para `DISCOVER_ACCOUNT`
             e herdava `ALLOWED`. A única rota debaixo daquela permissão lê o
             site da organização e devolve um handle.
PROVA        `cap.pela_matriz('LINKEDIN','DISCOVER_ACCOUNT')` devolvia a
             capacidade errada; corrigido na LINKEDIN-BUILD-01 (a418f040)
CONSEQUÊNCIA uma tradução errada NÃO REBENTA — ela AUTORIZA. E por isso o campo
             de tradução entra na revisão de política, não só na de código.
```

### Lei 2 — `PAID PROVIDER IS NOT A POLICY OVERRIDE`  ·  **REGISTADA em §89.5–89.8**

```
O QUE        comprar de um fornecedor não transfere a questão da autorização
POR QUE      não é uma opinião nossa: é o contrato do fornecedor. Apify GTC
             §6.2 exige que o cliente só processe dados «that you are
             authorized to access»; §11.1 põe no cliente a responsabilidade por
             extracção «from unauthorized sources» E a indemnização.
PROVA        docs.apify.com/legal/general-terms-and-conditions, em vigor
             2026-07-09, lido em 2026-09-12
CONSEQUÊNCIA a pergunta «esta rota é permitida?» sobrevive intacta à compra. O
             fornecedor resolve CAPACIDADE, nunca PERMISSÃO — e diz isso por
             escrito no momento em que se paga.

             E o corolário, medido pela C10.8B-LIVE:
             `PROVIDER REACHED != CAPABILITY DELIVERED`. Ele pode nem resolver
             a capacidade.
```

---

## 15 · VEREDITO

```
LINKEDIN_ROUTE_POLICY = PASS_NO_CONTENT_ROUTE_ALLOWED
                        + PENDING_HUMAN_DECISION (R3 · R6 · Ad Library)
```

```
ROTAS ALLOWED_NOW      2   R1 identidade off-LinkedIn · R7 reprocessamento
ROTAS NOT_ALLOWED      4   R2 oficial (não serve) · R3 pública · R4 Voyager ·
                           R5 como substituto de conteúdo
ROTAS BLOCKED          1   R8 asset em RAW — expirada
ROTAS PENDENTES        3   R3 · R6 classe B · Ad Library
PROVIDERS CLASSE A     0
PROVIDERS CLASSE B     4
PROVIDERS CLASSE C     2
```

A resposta à pergunta que a LINKEDIN_LOCAL_FIRST deixou aberta:

> **Para aquisição de conteúdo de terceiros no LinkedIn, nenhuma rota está
> autorizada hoje — e a razão mais forte não veio do LinkedIn. Veio do contrato
> do fornecedor pago, que exige por escrito que o cliente já esteja autorizado
> a acessar o dado, e põe no cliente a responsabilidade e a indenização. O
> intermediário não resolve a pergunta: ele devolve-a, assinada.**

E a consequência prática, que é boa notícia e má notícia na mesma frase:

    O QUE O SINTONIA PODE FAZER COM O LINKEDIN HOJE É SABER QUEM EXISTE, E
    RELER O QUE JÁ COMPROU. NENHUMA DAS DUAS PRECISA DE PERMISSÃO NOVA, E
    NENHUMA DAS DUAS CUSTA UM CÊNTIMO.

```
HARD STOP.
Nenhuma rota nova implementada · nenhuma probe executada · nenhum Actor
comprado · nenhum cookie usado · nenhum teste contra o LinkedIn.
```

### E uma precisao sobre o ficheiro da politica

`leis/social_matriz.py` **mudou nesta arvore**, e nao foi esta missao. A fusao
da C10.8B-LIVE acrescentou `PARTIAL` ao vocabulario fechado de estados e
reclassificou `apify:transcricao` — **rota do YouTube**. Nenhuma linha de
LinkedIn foi tocada, por ninguem.

    DIZER «INTACTO» SOBRE UM FICHEIRO QUE UMA FUSAO MEXEU SERIA FALSO, MESMO
    QUANDO A MUDANCA NAO E NOSSA E NAO TOCA O NOSSO ASSUNTO. Medido:
    `git diff b47295f6 HEAD -- leis/social_matriz.py` → 19 insercoes, 3 remocoes,
    todas em YOUTUBE/FETCH_TRANSCRIPT e no vocabulario ESTADOS.

O que esta missao nao mexeu, e isso e verificavel por `git diff`:
`coleta/scrap_capacidades.py` · `coleta/adaptador_linkedin.py` ·
`coleta/social_rotas.py` — **os tres INTACTOS desde b47295f6**.
