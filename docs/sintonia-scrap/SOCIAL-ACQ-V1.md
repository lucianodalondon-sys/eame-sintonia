# SOCIAL ACQUISITION V1 — LINKEDIN E INSTAGRAM

> `CAPABILITY_REPORT` da missão SCRAP **SOCIAL-ACQ-V1**.
> Branch isolada. **Nada foi integrado.** A Big Collection não foi tocada.

```
WORKTREE   C:/Users/London1/orca/workspaces/eame-sintonia/social-acq-v1
BRANCH     social-acq-v1          BASE   claude/it-trunk-v1 @ 606974c3
MEDIDO_EM  2026-09-20
PAID_USD   0        APIFY_RUNS 0        POLICY_CHANGED  NO
```

---

## A PERGUNTA, E A RESPOSTA CURTA

A missão pergunta o que se consegue adquirir de LinkedIn e Instagram. A resposta
medida não é uma por plataforma — é **uma por rota**, e é aí que as duas
plataformas deixam de se parecer:

```
LINKEDIN    tem UMA rota permitida, e ela EXECUTOU contra a rede real.
INSTAGRAM   tem QUATRO portas, fechadas por QUATRO motivos diferentes,
            e nenhuma delas saiu — por política, não por falha.
```

---

## REGRA ZERO — o que já existia, e não foi reescrito

O censo veio antes da hipótese, e mudou a missão. A casa **já tinha** tudo isto,
commitado e com provas:

| peça | caminho | último commit |
|---|---|---|
| adaptador do LinkedIn (899 linhas) | `coleta/adaptador_linkedin.py` | `0880b6a8` |
| adaptador do Instagram (497 linhas) | `coleta/adaptador_instagram.py` | `355fa0f8` |
| a lei das rotas sociais | `leis/social_matriz.py` | `7b8d96cc` |
| o roteador | `coleta/social_rotas.py` | `d94b827e` |
| a guarda de sessão | `guarda/social_guarda.py` | `082736db` |
| prova offline do LinkedIn | `provas/linkedin_local_first.py` | — |
| 5 ficheiros de testes | `tests/test_{linkedin,c10_5d,c14c,social}*.py` | — |

**37 adaptadores registados**, 15 deles destas duas plataformas.

```
NEW_CAPABILITIES   = 0
REUSED_CAPABILITIES = 15   (8 LINKEDIN + 7 INSTAGRAM)
```

Esta missão **não escreveu adaptador nenhum**. Escreveu os dois canários que
faltavam — o eixo de **execução**, que nenhuma prova anterior cobria.

---

## O EIXO QUE FALTAVA

`provas/linkedin_local_first.py` já provava a rota do LinkedIn com HTML
injectado. Isso prova a **tradução**, e a matriz dizia-o em claro:

```
LINKEDIN / DISCOVER_ACCOUNT   ESTADO = POSSIBLE_NOT_PROVED
```

`POSSIBLE_NOT_PROVED` significa exactamente o que diz: ninguém a tinha corrido
contra a rede.

```
MECHANISM PROVEN  !=  EXECUTION PROVEN.
```

Os dois canários desta missão fecham o segundo eixo:

| prova | o que mede |
|---|---|
| `provas/social_acq_canario_linkedin.py` | a rota permitida, **contra a rede real**, 8 alvos |
| `provas/social_acq_canario_instagram.py` | o **portão**, por execução, com o socket proibido |

---

## LINKEDIN

### A rota permitida nunca visita o linkedin.com

```
ROTA        descoberta-indireta:site-da-organizacao
CLASSE      DIRECT_HTTP        PERMITIDA  SIM        CUSTO  zero
```

Ela lê o **site da própria organização** (rodapé, «seguici su») e extrai dali o
endereço que a organização publicou de si. O §8.2 do User Agreement do LinkedIn
proíbe raspar o serviço **e** obter informação dele através de terceiros; ler o
site da empresa não é obter informação do LinkedIn — é obter da empresa.

### O que o canário mediu

```
CANARY_PASS = 4/8       IDENTIDADES_COM_HANDLE = 3
LINKEDIN_HTTP_REQUESTS = 0      LICDN_REQUESTS = 0
21/21 asserts            VEREDITO = PASS
```

| canário | alvo | resultado | handle | identidade |
|---|---|---|---|---|
| IT-01 | imagelinenetwork.com | `OK` | `image-line` | `IDENTITY_SELF_DECLARED` |
| IT-02 | confagricoltura.it | `GATE_UNAVAILABLE` | — | robots ilegível |
| IT-03 | coldiretti.it | `GATE_UNAVAILABLE` | — | robots ilegível |
| IT-04 | syngenta.it | `ERROR:RotaBloqueada` | — | **HTTP 403** |
| IT-05 | crea.gov.it | `OK` | `crea-ricerca` | `IDENTITY_SELF_DECLARED` |
| IT-06 | ismea.it | `GATE_UNAVAILABLE` | — | robots ilegível |
| IT-07 | edagricole.it | `OK` | — | site não publica handle |
| IT-08 | freshplaza.it | `OK` | `1602695` | **`IDENTITY_MISMATCH`** |

**A lista não encolheu quando um alvo falhou.** Apagar os 4 que falharam faria a
taxa de sucesso ser uma escolha em vez de um número.

### O que os 4 insucessos são, e o que não são

```
GATE_UNAVAILABLE  o robots.txt do SITE não deu para ler. É uma falha do
                  transporte a um site terceiro — não é recusa do LinkedIn,
                  e não é recusa do site. `PortaoIndisponivel` existe
                  precisamente para não transformar um soluço de rede numa
                  proibição permanente.
HTTP 403          o site da syngenta.it recusou o nosso agente. É uma medição
                  da robustez desta rota, e um número real de fragilidade.
OK com 0 handles  edagricole.it respondeu e simplesmente não publica LinkedIn
                  no HTML da home. Zero resultados é um resultado.
```

### O identity guard apanhou um caso real

`freshplaza.it` publica `linkedin.com/company/1602695` — um ID numérico que não
se parece com «freshplaza». O guard não o promoveu: devolveu
**`IDENTITY_MISMATCH`**, e isso é o comportamento correcto. HTTP 200 não prova
identidade.

Os três estados existem, e nenhum se arredonda para outro:

```
IDENTITY_SELF_DECLARED   o site de X publica o handle de X
IDENTITY_MISMATCH        o site de X publica o handle de OUTRA entidade
IDENTITY_NOT_KNOWN       não dá para decidir por comparação de nome
```

`IDENTITY_NOT_KNOWN` **não é reprovação**. «Este site publicou este endereço»
continua a ser um facto observado; o que não é, é prova de posse.

### Red team, executado

| ataque | resultado |
|---|---|
| `site_url = linkedin.com/company/...` | `RotaNaoPermitida` — **não** «zero resultados» |
| `site_url = ''` | `ValueError: ALVO_AUSENTE_OU_MALFORMADO` |
| redirect para host proibido | recusado pelo transporte, antes de ler robots do destino |
| sentinela de DNS sobre `linkedin.com`/`licdn.com` | **0 resoluções** em toda a corrida |

### O output mínimo, e o que ele recusa inventar

```
PLATFORM      LINKEDIN
NATIVE_ID     image-line
URL           https://www.linkedin.com/company/image-line
CONTENT_TYPE  DISCOVERY            ← nunca POST
ROUTE         descoberta-indireta:site-da-organizacao
RAW_SHA256    36679715da120efc…    ← bruto preservado
COST_USD      0.0
POST_CONTENT  None       CONTENT_ACQUIRED  False
```

Sem `FACT_TIME`. Sem `FACT_LOCATION`. Nem um nem outro é derivável daqui, e o
envelope não os traz.

### Veredito do LinkedIn

```
LINKEDIN_STATUS               PARTIAL_CAPABILITY
LINKEDIN_READY_CAPABILITIES   linkedin.identity.discovery   (DISCOVER_ACCOUNT)
                              = PROVED por execução remota
LINKEDIN_BLOCKED_CAPABILITIES linkedin.direct_post · linkedin.native_video
                              linkedin.native_caption · linkedin.recent.discovery
                              (FETCH_POST = ROUTE_NOT_ALLOWED, §8.2 do ToS)
LINKEDIN_CANARY_PASS          4/8   ·   COM_HANDLE 3
```

**Texto funciona onde vídeo não funciona?** Para o LinkedIn a fronteira medida
não é texto-vs-vídeo — é **identidade vs conteúdo**:

```
IDENTIDADE (quem existe, e o endereço)   PERMITIDA e PROVADA
CONTEÚDO   (o texto do post, o vídeo)    ROUTE_NOT_ALLOWED — os dois
```

O post público de organização de terceiro **não tem rota permitida nenhuma**:
nem grátis (o robots barra tudo menos o `LinkedInBot`), nem oficial (a Community
Management API só lê a página que o nosso app administra), nem paga (o §8.2
alcança explicitamente o intermediário). **Isto é uma resposta, não uma
pendência.**

---

## INSTAGRAM

### Quatro portas, quatro motivos, quatro donos

```
FETCH_TRANSCRIPT   ROUTE_NOT_ALLOWED   robots.txt VIVO de instagram.com
                                       responde `Disallow: /` (C10.5D)
INCREMENTAL        ROUTE_NOT_ALLOWED   fail-closed da C14-C:
                                       OWNER_AUTHORIZED = SIM,
                                       PLATFORM_POLICY_STATUS = NOT_MEASURED
FETCH_PROFILE      ALLOWED             graph:business_discovery,
                                       mas CREDENTIAL_MISSING
FETCH_COMMENTS     ALLOWED             apify:comments, mas é PAGA
                                       (esta missão: PAID_USD = 0)
```

```
QUATRO MANEIRAS DE NÃO SAIR NÃO SÃO UM BLOQUEIO SÓ.
«PLATAFORMA BLOQUEADA» APAGA AS QUATRO E NÃO É VERDADE DE NENHUMA.
```

E os três eixos que a C14-C separou continuam separados, cada um com o seu dono:

```
PERMISSÃO   !=   CREDENCIAL   !=   ORÇAMENTO
```

### A prova: a cadeia recusa sozinha, com a rede proibida

```
INSTAGRAM_POLICY_GATE_CANARY = PASS   (35/35 asserts)
INSTAGRAM_REQUESTS = 0 · INSTAGRAM_DNS = 0 · PAID_USD = 0
```

O socket foi proibido em **duas camadas** — `connect` e `getaddrinfo` — antes de
importar a cadeia. Um portão que deixa resolver o nome já conversou com o DNS do
alvo.

E o instrumento verificou-se primeiro: a sentinela foi disparada de propósito
contra um host inventado antes de ser usada para julgar o que quer que seja. Um
espião que não dispara faz qualquer recusa parecer boa.

| `COLLECT(...)` | estado devolvido | sockets | DNS | objetos |
|---|---|---|---|---|
| `FETCH_TRANSCRIPT` | `ROUTE_NOT_ALLOWED` | 0 | 0 | 0 |
| `INCREMENTAL` | `ROUTE_NOT_ALLOWED` | 0 | 0 | 0 |
| `FETCH_PROFILE` | `CREDENTIAL_MISSING` | 0 | 0 | 0 |
| `FETCH_POST` | `UNKNOWN_ERROR` | 0 | 0 | 0 |
| `FETCH_COMMENTS` | `BUDGET_EXHAUSTED` | 0 | 0 | 0 |

Cinco recusas, **cinco estados diferentes**. Nenhuma delas é «falhou».

### REUSAR ≠ ADQUIRIR — e não é contradição

Três capacidades continuam `PROVEN` em `scrap_capacidades.py` enquanto a matriz
diz `ROUTE_NOT_ALLOWED`:

```
instagram.reel.capture       PROVEN
instagram.reel.audio         PROVEN
instagram.reel.transcribe    PROVEN
```

A própria lei antecipa a leitura errada, na linha da decisão: o que está recusado
é **sair para buscar mídia nova**, não processar bytes que já entraram. Dois
eixos, e a matriz escreveu-o antes de alguém perguntar.

```
CAN DO  !=  MAY DO  !=  DID DO.
```

### A ausência que é o achado

`instagram.native_caption` **não existe** em `scrap_capacidades.py`, e isso é
deliberado: o Instagram não serve legenda nativa. O que ele serve é o `caption`,
que é texto que o **autor escreveu**.

```
CAPTION (texto do autor)  !=  TRANSCRIPT (fala reconhecida)  !=  ASR
```

Somar os dois apagaria qual deles sustentou uma classificação — e é a primeira
pergunta que a Intelligence faz.

`FETCH_VIDEO_BYTES` devolve `NOT_DECLARED`: ninguém decidiu esta porta.
**`NOT_DECLARED` não é permissão.**

### Veredito do Instagram

```
INSTAGRAM_STATUS               POLICY_BLOCK  (remoto)  +  PROVED (local, reuso)
INSTAGRAM_READY_CAPABILITIES   nenhuma rota REMOTA executável hoje
                               instagram.reel.{capture,audio,transcribe} = PROVEN
                               sobre bytes já preservados
INSTAGRAM_BLOCKED_CAPABILITIES FETCH_TRANSCRIPT (robots) · INCREMENTAL (fail-closed)
INSTAGRAM_PENDING              FETCH_PROFILE  → falta CREDENCIAL (Graph API)
                               FETCH_COMMENTS → falta ORÇAMENTO (Apify)
INSTAGRAM_CANARY_PASS          35/35 asserts do portão
INSTAGRAM_CANARY_FAIL          0
```

### O que este canário NÃO prova, dito em voz alta

Não prova que o Instagram responderia 200, 403 ou 429. Isso exigiria sair, e sair
é exactamente o que a política recusa.

```
PLATFORM_HTTP_BEHAVIOUR = UNKNOWN
ROTA RECUSADA PELA CASA  !=  ROTA BLOQUEADA PELA PLATAFORMA.
```

Escrever `BLOCKED` onde só há `NOT_ATTEMPTED` seria inventar uma medição.

---

## ACHADO — REGISTADO, NÃO CORRIGIDO

```
ACHADO_ID   INSTAGRAM_ALLOWED_SEM_DONO
```

Três capacidades do Instagram estão `ALLOWED` na matriz e **não têm capacidade
declarada que traduza para elas**, logo não têm rota ligada:

```
FETCH_PROFILE   →  declarada = None   →  rota_ligada = False
FETCH_POST      →  declarada = None   →  rota_ligada = False
FETCH_COMMENTS  →  instagram.post.comments  →  rota_ligada = False
```

`INSTAGRAM/FETCH_POST` merece atenção: está `ALLOWED` com rota `PUBLIC_BROWSER`
`PROVED` — a **mesma família de implementação** (`instagram_janela.py`) que a
C14-C fechou em `INCREMENTAL` por fail-closed. Foi exactamente este o padrão do
defeito que a LINKEDIN-BUILD-01 encontrou e fechou: `linkedin.recent.discovery`
pedia emprestada a permissão de `DISCOVER_ACCOUNT`.

**Medido: hoje não é bypass.** Nenhum `COLLECT` chega lá, e o canário prova-o por
execução — `COLLECT(FETCH_POST)` devolve `UNKNOWN_ERROR` com `req=0`.

```
PERMISSÃO SEM DONO NÃO É BYPASS.
MAS TAMBÉM NÃO É UMA DECISÃO COMPLETA: no dia em que alguém lhe ligar um
dono, ela sai sem passar pelos três eixos que a C14-C exigiu da porta vizinha.
```

**Não corrigido nesta missão.** Mexer em `leis/social_matriz.py` é decisão do
dono da política. `SCOPE LEAK = FAIL`.

---

## O CONTRATO — por que não foi preciso inventar um

A missão pede que a capacidade entre por contrato, sem `if SOURCE_ID == ...`. O
motor canónico **já faz isso**, e foi medido a fazê-lo:

```
COLLECT(platform, capability)
  → social_rotas._rota_executavel()
  → scrap_capacidades.pela_matriz(plat, capacidade_grossa)   ← a tradução
  → scrap_registo.rota_de(plat, nome_declarado)              ← o dono único
  → o adaptador
```

A escolha é pelo par `(PLATAFORMA, CAPABILITY)` lido da matriz. **Nenhum
`SOURCE_ID` aparece em lado nenhum deste caminho.** Um contrato novo seria um
segundo motor a fingir-se do primeiro.

O registo devolve, por execução, os campos que a missão pede:

```
ACQUISITION_PROVIDER   coleta/adaptador_linkedin.identidade_pelo_site
ROUTE                  descoberta-indireta:site-da-organizacao
CAPABILITY             LINKEDIN/DISCOVER_ACCOUNT
POLICY_STATE           ALLOWED  ·  POLICY_OWNER  leis/social_matriz.py
COST_STATE             FREE_ROUTE_BY_POLICY   ACTUAL_COST_USD  0.0
```

`COST_STATE` é um eixo próprio ao lado do número, e isso é deliberado: um zero
sozinho não distingue «não correu» de «correu e foi grátis».

```
NOT_RUN != 0.    UNKNOWN != 0.
```

---

## CUSTO

```
PAID_USD          0
APIFY_RUNS        0
CREDENCIAIS USADAS  nenhuma
PEDIDOS HTTP      9 (sites de organizações terceiras, rota gratuita por política)
PEDIDOS A linkedin.com / licdn.com / instagram.com     0
```

Custo conhecido das rotas **não** usadas, lido da matriz:

```
apify:harvestapi~linkedin-*    US$ 4,03 / 1.000   — ROUTE_NOT_ALLOWED (§8.2)
apify:instagram-scraper        por item           — ALLOWED, não executada
referência da casa             US$ 1,86 / 1.000   (84 runs · 6.878 itens · US$ 12,81)
```

---

## PROIBIÇÕES — nenhuma foi tocada

```
login contornado                NÃO
sessão/cookie de terceiro       NÃO
CAPTCHA                         NÃO
controlo de acesso burlado      NÃO
bloqueio deliberado contornado  NÃO
credencial não autorizada       NÃO
evasão de detecção              NÃO
identidade falsificada          NÃO
serviço comprado                NÃO   (PAID_USD = 0)
```

Provado por execução, não por declaração: as sentinelas de socket e de DNS
contam, e as contagens estão acima.

---

## NÃO INTEGRAR

```
BIG COLLECTION TOCADA             NÃO
big-collection-release-v1         outra worktree, outro terminal, não tocada
SALA                              não tocada
PRODUÇÃO CORRIDA                  NÃO
leis/social_matriz.py ALTERADO    NÃO
adaptadores ALTERADOS             NÃO
```

Esta branch acrescenta **três ficheiros novos** e não modifica nenhum existente:

```
provas/social_acq_canario_linkedin.py     NOVO
provas/social_acq_canario_instagram.py    NOVO
docs/sintonia-scrap/SOCIAL-ACQ-V1.md      NOVO  (este)
```

---

## O QUE FICA PARA O COORDINATOR DECIDIR

| # | pergunta | quem decide |
|---|---|---|
| 1 | promover `LINKEDIN/DISCOVER_ACCOUNT` de `POSSIBLE_NOT_PROVED` para `PROVED`? | dono da política — há agora execução remota que o sustenta |
| 2 | `INSTAGRAM_ALLOWED_SEM_DONO`: dar os três eixos da C14-C às três portas órfãs? | dono da política |
| 3 | credencial Graph API (conta Business/Creator + Página) para `FETCH_PROFILE`? | dono do projeto — custo zero dentro da quota |
| 4 | orçamento Apify para `FETCH_COMMENTS`/`FETCH_POST` além dos 12 recentes? | dono do projeto — rota `ALLOWED`, falta dinheiro |
| 5 | medir o `robots.txt` do `instagram.com` para `INCREMENTAL` e fechar o eixo `PLATFORM_POLICY_STATUS`? | missão própria — o dono já autorizou a sua metade |

Nenhuma delas é decisão do SCRAP.

---

## KNOW_HOW_DELTA

```
KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA
```

**O quê:** `POSSIBLE_NOT_PROVED` numa rota da matriz é um convite a um canário
remoto, não um estado terminal. A prova offline com transporte injectado e a
execução contra a rede são **dois eixos**, e a matriz nomeia o eixo que falta.

**Porquê:** a rota do LinkedIn estava completa, blindada e testada há 7 dias, e
continuava por correr. Ninguém tinha errado — o estado dizia a verdade, e a
verdade era «falta o segundo eixo».

**Prova:** `provas/social_acq_canario_linkedin.py`, 21/21, 3 identidades reais.

**Consequência:** ao abrir uma missão de capability, procurar na matriz os
estados `POSSIBLE_NOT_PROVED` — cada um é uma capability a um canário de
distância de mudar de estado.

---

## VEREDITO

```
LINKEDIN_DISCOVERY_REMOTE_CANARY   = PASS    21/21
INSTAGRAM_POLICY_GATE_CANARY       = PASS    35/35

LINKEDIN   linkedin.identity.discovery              PROVED   (execução remota)
           linkedin.direct_post / native_video /
           native_caption / recent.discovery        BLOCKED  (ToS §8.2)
INSTAGRAM  rotas remotas                            POLICY_BLOCK (0 pedidos)
           reel.{capture,audio,transcribe}          REUSED / PROVEN (local)
           FETCH_PROFILE                            AUTH_BLOCK (credencial)
           FETCH_COMMENTS                           CAPABILITY_BLOCK (orçamento)
           comportamento HTTP da plataforma         UNKNOWN

NEW_CAPABILITIES = 0      REUSED_CAPABILITIES = 15
PAID_USD = 0              POLICY_CHANGED = NO
READY_FOR_INTEGRATION_AFTER_BIG_COLLECTION = SIM, para o eixo LINKEDIN DISCOVERY
```

**HARD STOP.**
