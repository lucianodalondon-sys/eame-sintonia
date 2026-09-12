# LINKEDIN-OP-01 · LINKEDIN OPERACIONAL V1

> **Pergunta:** o LinkedIn pode ficar operacional no SINTONIA, com a capacidade
> permitida realmente conectada ao fluxo canônico e qualquer capacidade proibida
> realmente impossível de executar por acidente?
>
> **Resposta:** `SIM`, e executavelmente. Um pedido real atravessou a casa inteira
> e trouxe uma identidade LinkedIn **sem tocar o linkedin.com**; o pedido de posts
> termina em `ROUTE_NOT_ALLOWED` antes de qualquer rede paga.

```
REAL_DIRECT_HTTP_REQUESTS = 2   (ambos ao site da organização)
LINKEDIN_HTTP_REQUESTS    = 0
PAID_REQUESTS             = 0
COST_USD                  = 0
```

---

## A · GIT

```
BASE_BRANCH  = claude/sintonia-scrap-canonical-flow-f01
BASE_HEAD    = 84422284eeac731e3fe44ed236f63b91570e194f
C11_HEAD     = 675b749b0473243b641f8224b8785d11dc54bb3e
MERGE_BASE   = 231ffa2c07fd500ae663d2f1a8e38417976370e1
FINAL_BRANCH = claude/sintonia-scrap-linkedin-operational-close-v1
REMOTE       = github.com/lucianodalondon-sys/eame-sintonia
WORKTREE     = limpa
```

**Sem drift.** As três referências do coordenador foram remedidas e as três batem.

### Por que a base é o FLOW-01, e não o C11

Medido, não herdado:

| ficheiro | C11 | FLOW-01 |
|---|---|---|
| `coleta/scrap_colheita.py` | **ausente** | presente |
| `leis/retorno_da_coleta.py` | **ausente** | presente |
| `coleta/ingresso.py` | presente | presente |
| `orquestrador/orquestrador.py` | presente | presente |

O C11 é autoridade de **medição** e não tem o fluxo. Sem `scrap_colheita.py` não
há por onde plugar. Dependency closure conferida: todos os imports do que se
portou existem na base.

**Portado, sem merge geral:** o relatório do censo C11; e da linha LinkedIn as
decisões, as provas, os contratos e o adaptador. A política **não** foi portada —
ela é ancestral e compartilhada (`901255c7`), idêntica nas três linhas.

---

## B · A CAPACIDADE QUE FICOU VIVA

```
linkedin.identity.discovery  →  DISCOVER_ACCOUNT
rota: descoberta-indireta:site-da-organizacao · DIRECT_HTTP · PERMITIDA = SIM
```

Lê o site **da própria organização** e extrai dali o endereço que a organização
publicou. O request HTTP é ao site da organização. Estado `PARTIAL`, e o teto está
medido: das sete sentinelas do C11, duas responderam e uma publicava o handle.

Entrega, por objeto: `DISCOVERY_SOURCE` · `DISCOVERED_URL` · `TARGET_TYPE` ·
`DISCOVERED_AT` · `RAW_SHA256` · e, em claro, `POST_CONTENT = None` /
`CONTENT_ACQUIRED = False` — para que nenhum relatório leia identidade como
publicação.

---

## C · AS CAPACIDADES QUE FICARAM FECHADAS

| capacidade | antes | agora | porquê |
|---|---|---|---|
| `linkedin.recent.discovery` | PROVEN + traduzia `DISCOVER_ACCOUNT` | **BLOCKED**, sem tradução | conteúdo, e sem rota permitida |
| `linkedin.direct_post` | PROVEN | **BLOCKED** | `FETCH_POST` = `ROUTE_NOT_ALLOWED` |
| `linkedin.native_video` | PROVEN | **BLOCKED** | idem |
| `linkedin.native_caption` | PROVEN | **BLOCKED** | idem |
| `linkedin.comments` | UNKNOWN | UNKNOWN | nunca tentado |
| `linkedin.documents` | NOT_EXECUTED | NOT_EXECUTED | — |
| `linkedin.history.discovery` | UNKNOWN | UNKNOWN | — |

### A tradução que emprestava uma permissão

`linkedin.recent.discovery` significa **as publicações recentes da página de
empresa**. Ela era quem traduzia para `DISCOVER_ACCOUNT` — e
`pela_matriz('LINKEDIN','DISCOVER_ACCOUNT')` devolvia **ela**. O roteador que
pedia *identidade* encontrava a capacidade de *conteúdo*.

```
    IDENTITY != CONTENT, NA CAMADA DE TRADUÇÃO.
```

Nenhum código explorava isto porque nenhuma das sete tinha rota — a porta estava
destrancada por dentro. Retirar a tradução **não abre rota nenhuma**: devolve a
permissão ao dono que faz exatamente aquilo.

### E quatro capacidades PROVEN prometiam sem poder cumprir

Encontrado por uma sentinela desta missão: as quatro estavam `PROVEN`, logo
`promete_resultado()` respondia **SIM** — para capacidade **sem rota ligada**.

```
    UM ADAPTADOR PODE EXISTIR SEM EXECUTAR NADA.
    NÃO PODE É EXISTIR DIZENDO QUE EXECUTA.
```

`BLOCKED` é literalmente «existe, não dá para usar agora (quota, teto, **termo**)»
— e o termo é o do LinkedIn. A história técnica **não se perde**: vive inteira no
relatório C11, com os 372 posts e as datas.

```
    TECHNICALLY_PROVEN_HISTORY != CURRENT_ALLOWED_ROUTE.
    HISTÓRICO NÃO É CAPACIDADE ATUAL.
```

Hoje **uma** capacidade LinkedIn promete resultado, e é a única com rota.

---

## D · FLUXO OBSERVADO

```
COLLECTION_REQUEST   Pedido(alvo='T9', filtros={fase, site})
→ receitas.resolver  scrap-colheita promovido por serve_fases
→ ORQUESTRADOR       cunha o RUN_ID, monta o comando
→ SCRAP COLHEITA     coleta/scrap_colheita.py · fase identidade-linkedin
→ SOCIAL ROUTER      social_rotas, por PLATAFORMA + CAPACIDADE
→ LINKEDIN ADAPTER   identidade_pelo_site
→ TERMINAL           envelope · SUPORTE[CATALOG] · RAW preservado
```

O pedido não conhece implementação: nem `scrap_colheita.py`, nem `receitas.py`,
nem `orquestrador.py` nomeiam `adaptador_linkedin` ou `identidade_pelo_site`
(sentinela A16).

E em paralelo:

```
fase_posts('LINKEDIN')
→ mz.decisao('LINKEDIN','FETCH_POST') = ROUTE_NOT_ALLOWED
→ return None · APIFY_RUNS=0 · HARVESTAPI_START_POSTS=0 · COST_USD=0
```

### O terminal, lido no contrato e não escolhido

`leis/retorno_da_coleta.py` define `CATALOG` como **«inventário de entidades de
onde se PODE coletar»** — ao lado de `CONTAS-V1` e `UNIVERSO-CONTAS` — e declara
`ENTRAM_NO_INGRESSO = (COLHEITA,)`.

Um endereço de conta é exatamente isso. Logo:

```
    DISCOVER_ACCOUNT → CATALOG → NÃO ATRAVESSA A ADMISSÃO.
```

O contrato já recusava por construção: `conferir_unidade()` reprova qualquer
unidade em `COLHEITA` cuja espécie não seja `COLHEITA`. O que faltava era a fase
**dizer**. Cada fase passou a declarar a sua espécie — o campo que aquela lei
nasceu a dizer que não existia («o "em que forma" não tinha campo nenhum, nem
enum, nem guarda») — e **sem valor por omissão**:

```
    UMA ESPÉCIE POR OMISSÃO É UMA DECISÃO QUE NINGUÉM TOMOU.
```

Empurrar isto para a Sala de Espera completaria uma seta no desenho e ligaria a
mangueira de gasolina na da água. Os 253 itens de falsa colheita que aquela lei
mediu nasceram assim.

---

## E · PROVA REAL

```
REAL_ALLOWED_SENTINEL     = PASS
sentinela                 = imagelinenetwork.com
REAL_DIRECT_HTTP_REQUESTS = 2   (robots.txt + página, ambos do site da organização)
hosts tocados             = imagelinenetwork.com   (e só)
LINKEDIN_HTTP_REQUESTS    = 0
SUBPROCESSOS              = 0
PAID_REQUESTS             = 0
COST_USD                  = 0
DISCOVERED_URL            = https://www.linkedin.com/company/image-line
TARGET_TYPE               = COMPANY
RAW_SHA256                = 9e40b34272e2139fb518af2cf5bd9e9935c19d5339ccd3a85b68fb8b7adba0ba
```

O bruto está preservado e versionado em
`data/samples/SOCIAL-IT/raw-free/LINKEDIN/`, e o SHA acima é o que o envelope
declara — sem os bytes ao lado, `RAW_SHA256` não se confere.

Três execuções reais aconteceram durante a missão (a primeira por descuido, ao
correr o CLI sem transporte falso). As três deixaram bruto na árvore, e três
suites de higiene reprovaram — **corretamente**. Ficou **uma**, de uma corrida
limpa, que é a que este documento cita.

```
    TRÊS CÓPIAS DA MESMA PÁGINA NÃO SÃO TRÊS PROVAS.
```

---

## F · FALLOUT PAGO

```
HARVESTAPI_ACCIDENTAL_PATH = 0
APIFY_START_POSTS          = 0
```

### O gate existia e não era alcançado

`fase_posts()` **já** consultava `leis/social_matriz.py` antes de qualquer rota
paga — a C10.6D pôs a pergunta lá. Mas ela vinha **depois** de
`contas_autorizadas()`. Sem conta LinkedIn cadastrada, a função voltava `None`
dizendo *«nenhuma conta AUTORIZADA»*, e a resposta sobre **permissão** nunca era
alcançada.

```
    AUSÊNCIA DE CONTA NÃO É ROTA NÃO PERMITIDA.
    UM PORTÃO QUE SÓ SE ALCANÇA COM INVENTÁRIO NÃO É UM PORTÃO DE POLÍTICA.
```

O risco era silencioso: no dia em que alguém cadastrasse uma conta LinkedIn, a
proteção passava a depender de um gate que ninguém tinha visto responder. A
pergunta subiu — **sem mudar de dono**. E quem tem capacidade canônica não passa
por ela: o YouTube mede `NOT_DECLARED` em `FETCH_POST` e colhe por outra
capacidade; gatear nisso desligava-o.

### E o ator pago saiu

`ATORES['LINKEDIN'] = ('harvestapi~linkedin-post-search', 'JA_RODOU_NESTA_CASA')`
foi removido, e com ele a entrada de ator pronta (`companyUrls`, `maxItems: 50`).

```
    UMA ENTRADA DE ATOR PRONTA É METADE DE UMA COMPRA.
    CÓDIGO MORTO COM CARA DE ROTA VIVA É PIOR QUE CÓDIGO APAGADO.
```

Mas removê-lo das duas tabelas fazia o LinkedIn desaparecer de `_PLATAFORMAS()` —
e com ele a recusa.

```
    UMA RECUSA QUE NÃO SE ALCANÇA NÃO É UMA RECUSA: É UM SILÊNCIO.
```

Então ele fica numa terceira tabela, `ATENDIDAS_SO_PARA_RECUSAR` — uma tabela, e
não um `if plataforma == 'LINKEDIN'`, que seria um segundo dono da política.

---

## G · IDENTIDADE

```
SOURCE_ID_FABRICATED_FROM_URL = 0
```

Nenhum objeto da rota sai com `SOURCE_ID`. A URL descoberta é `DISCOVERED_URL` e
nada mais. `scrap_colheita` já carregava a lei — «sem o `SOURCE_ID` vindo do
pedido, estas observações são CANDIDATAS… URL NÃO É SOURCE_ID» — e o envelope
desta fase passa `rc.conferir()` com zero violações.

E a lei ganhou um uso novo: os argumentos posicionais desta fase **classificam-se
pela forma**, não pela posição. O orquestrador só acrescenta o valor de um filtro
quando ele existe (`if v:`), então a posição depende de quais os anteriores
estarem preenchidos — e ler `resto[1]` como fonte punha o **site** no lugar da
**fonte** sempre que a fonte faltava. Que foi exatamente o caso do pedido real.

```
    UM ARGUMENTO POSICIONAL NUMA LISTA COM BURACOS NÃO TEM POSIÇÃO.
```

Um `SOURCE_ID` nunca tem esquema; um endereço tem sempre. Classificar pela forma
não fabrica identidade — recusa-se a fazê-lo.

---

## H · ZERO ACESSO AO LINKEDIN

A rota aceitava `site_url = https://www.linkedin.com/company/image-line`, **ia
lá**, e devolvia identidade com `RESULT = OK`.

Havia uma defesa em produção — `scrap_http.buscar` chama `permitido()`, que lê o
robots do host — e ela **não serve para este alvo**, por duas razões:

1. ela **pergunta ao LinkedIn** se pode ler o LinkedIn, e a pergunta é ela mesma
   um pedido ao `linkedin.com`. O gate é `= 0`, e zero inclui o robots.txt;
2. `transporte` passa por fora dela, e `transporte` chega à rota vindo do
   `**extra` do `COLLECT`.

```
    UMA PROIBIÇÃO QUE SE CONFIRMA PELA REDE DEPENDE DA REDE.
    ESTA É ESTÁTICA, PORQUE A POLÍTICA JÁ É ESTÁTICA.
```

Agora a rota recusa por lista própria, **antes de qualquer transporte**, e a
recusa é `RotaNaoPermitida` — que `social_rotas` já traduz para
`ROUTE_NOT_ALLOWED`. Nenhum vocabulário novo, nenhum segundo dono. E nunca
`ZERO_RESULTS`:

```
    UM ALVO RECUSADO NÃO É UMA BUSCA VAZIA.
```

### E um salto também é um pedido

`urlopen` seguia 301/302 em silêncio. Um site com `Location: linkedin.com` levava
este pedido ao host proibido sem ninguém perguntar nada.

```
    UM PORTÃO QUE JULGA SÓ O PRIMEIRO ENDEREÇO NÃO JULGA O PEDIDO.
    UM REDIRECIONAMENTO É UM PEDIDO NOVO, E PEDE LICENÇA OUTRA VEZ.
```

O portão passou a valer em **cada salto**, e isso vive no dono do **transporte** —
porque «o portão vale em cada salto» é uma propriedade do transporte, e uma cópia
da regra dentro de um adaptador seria a regra a valer numa rota e a faltar em
todas as outras. A lista de hosts vem de quem a declara; o ponto de cobrança é do
transporte. Dois papéis da mesma trava.

E a recusa acontece **sem ler o robots do destino**:

```
    UMA PROIBIÇÃO QUE PERGUNTA AO PROIBIDO NÃO CHEGOU A ZERO PEDIDOS.
```

Medido no ataque do redirect: `HOSTS TOCADOS = ['127.0.0.1']`.

### E pela terceira vez na mesma cadeia

O `except Exception` de `buscar()` traduzia a recusa do **nosso** portão para
`RotaBloqueada`, que quer dizer «a plataforma nos impediu». O próprio ficheiro já
avisava, por escrito, que isso tinha acontecido duas vezes antes.

```
    QUEM DISSE NÃO TEM NOME, E O NOME NÃO SE TROCA A CAMINHO DE CIMA.
```

A recusa do portão sobe inteira, como a do teto ao lado.

---

## I · RED TEAM

```
ATTACKS   = 20   (A1–A20, mais A14b)
SURVIVORS = 0
```

| # | ataque | resultado |
|---|---|---|
| A1 | URL do LinkedIn como site da organização (6 variantes) | `ROUTE_NOT_ALLOWED`, zero pedidos |
| A2 | redirect do site para `linkedin.com` | recusado, `HOSTS TOCADOS = 127.0.0.1` |
| A3 | HTML sem LinkedIn | `ZERO_RESULTS` — zero legítimo |
| A4 | dois links LinkedIn | saem os dois |
| A5 | `/feed/`, `/posts/`, `/sharing/` em vez de identidade | não viram identidade |
| A6 | URL malformada / vazia | `ALVO_AUSENTE_OU_MALFORMADO` |
| A7 | URL LinkedIn a tentar virar `SOURCE_ID` | nenhum objeto carrega `SOURCE_ID` |
| A8 | página 403 | **não** é `ZERO_RESULTS` |
| A9 | timeout | **não** é `ZERO_RESULTS` |
| A10 | parser drift (5 formas) | zero, nunca slug adivinhado |
| A11 | `fase_posts('LINKEDIN')` | `ROUTE_NOT_ALLOWED`, com e sem conta |
| A12 | `permitir_pago=True` em 4 capacidades | nenhuma abre |
| A13 | token Apify presente | `ROUTE_NOT_ALLOWED` |
| A14 | ator HarvestAPI na fase de comunicação | ausente, `conferir_atores() = []` |
| A14b | **o outro caminho HarvestAPI** | existe, e está trancado — ver §M |
| A15 | capacidade registada sem função | nenhuma promete |
| A16 | chamada direta ao adapter | ninguém de fora o nomeia |
| A17 | retorno com `SOURCE_ID = URL` | envelope passa `conferir()` com zero |
| A18 | zero handles como «fonte inexistente» | `ZERO_RESULTS`, e não `SOURCE_GONE` |
| A19 | erro de ferramenta como `ZERO_RESULTS` | três erros, três estados |
| A20 | os 372 posts como execução nova | rota do histórico ≠ rota permitida |

---

## J · MUTATION

```
MUTANTS   = 8   (M1–M8)
SURVIVORS = 0
```

| mutante | o que muda | quem morde |
|---|---|---|
| M1 | permitir request ao `linkedin.com` | a lista da rota — e o teste prova que o mutante muda o comportamento antes de repor |
| M2 | reintroduzir o fallback HarvestAPI | `conferir_atores()` reprova |
| M3 | `DISCOVERED_URL` → `SOURCE_ID` | a rota nunca o produz; o contrato mede |
| M4 | bypassar `social_matriz` | cai no portão seguinte — prova que era a matriz que barrava |
| M5 | registar capacidade sem implementação | `promete_resultado()` = False; `COLLECT` recusa |
| M6 | chamar o adapter direto do workflow | nenhum workflow o nomeia |
| M7 | `HTTP_ERROR` → `ZERO_RESULTS` | os dois estados diferem |
| M8 | `ROUTE_NOT_ALLOWED` → `UNKNOWN` | a recusa tem nome próprio |

Três sentinelas estáticas foram **verificadas por mutação real na árvore** (M6,
A16, A11): cada uma reprovou com o mutante aplicado e voltou a verde ao revertê-lo.

```
    UMA SENTINELA QUE NUNCA SE VIU REPROVAR NÃO ESTÁ PROVADA: ESTÁ SUPOSTA.
```

---

## K · REGRESSÃO

```
BASELINE (84422284, mesmo diretório)  PASS=99   FAIL=11
FINAL                                 PASS=101  FAIL=11

OLD_FAILURES   = 11   (as mesmas 11, nome por nome)
NEW_FAILURES   = 0
FIXED_FAILURES = 0
```

O `+2 PASS` são as duas suites que a árvore nova tem e a baseline não
(`test_linkedin_build_01_local_first.py`, portada, e
`test_linkedin_op_01_operacional.py`, desta missão). A lista de falhas é
**idêntica** à da baseline, nome por nome.

A baseline foi medida **no mesmo diretório e no mesmo ramo** — uma worktree em
`/tmp` muda o caminho e a cabeça, e alguns testes desta casa medem os dois.

### Quatro falhas novas apareceram e foram consertadas, não toleradas

- **três** por higiene de acervo: as minhas execuções reais deixaram bruto
  não-rastreado, e três suites reprovaram — **corretamente**. Resolvido
  reduzindo a uma corrida e versionando o bruto dela.
- **uma** por métrica publicada: `TEST_COUNT_CURRENT` passou de 2.707 a **2.790**
  com os testes acrescentados, e oito documentos publicavam o número antigo. A
  casa tem um mecanismo para isso, e ele funcionou.
- E uma sentinela **minha**, da LINKEDIN-BUILD-01, prendia a recusa
  `DECLARED_WITHOUT_ROUTE`. Com a capacidade em `BLOCKED`, a casa recusa **mais
  cedo** (`CAPABILITY_STATE_PROMISES_NOTHING`). A sentinela aceita agora as duas
  recusas, e nenhum `OK`.

```
    DUAS RECUSAS NÃO SÃO A MESMA RECUSA, E A QUE CHEGA PRIMEIRO É A QUE SE LÊ.
    PRENDER A MAIS TARDIA REPROVA O DIA EM QUE A CASA FICA MAIS ESTRITA.
```

---

## L · SYSTEM MAP

```
SYSTEM_MAP_CHECK = PASS
IMPRESSAO_DO_CARIMBO = IGUAL
```

Cadeia lida de `CADEIA-DO-MAPA.json`: **7 passos `REGERAR` + 1 `VALIDAR`**, todos
corridos, mais `publicar_no_deploy.mjs`. Nenhum JSON gerado editado à mão.

Declarado: `provas/linkedin_local_first.py` em `C-PROVA-COLETA` (P9 reprovava). E
`C-SCRAP-COLHEITA` passa a dizer, na própria descrição, o que §17 exige:

```
    LINKEDIN IDENTITY DISCOVERY = WIRED e OBSERVED
    LINKEDIN CONTENT = ROUTE_NOT_ALLOWED
```

**Uma aresta declarada foi revertida.** Declarei
`C-SCRAP-COLHEITA → C-SCRAP-SOCIAL` e ela nasceu `UNKNOWN`: o scanner já prova a
relação na direção contrária, então a minha era a mesma ligação virada ao
contrário.

```
    UMA ARESTA DECLARADA QUE DUPLICA UMA PROVADA NÃO ACRESCENTA UMA LIGAÇÃO.
```

E não há seta para conteúdo. A ausência é a declaração, e está escrita.

---

## M · O ACHADO QUE A MISSÃO NÃO NOMEOU

A missão apontou a dívida em `coleta/comunicacao_coleta.py`. Há outra, maior:

```
regras/sensor_coleta.py
  ATORES['LINKEDIN_SEARCH_BY_NAME'] = 'harvestapi~linkedin-profile-search-by-name'
  ATORES['LINKEDIN_PROFILE_SEARCH'] = 'harvestapi~linkedin-profile-search'
  ATORES['LINKEDIN_PROFILE']        = 'harvestapi~linkedin-profile-scraper'
  ATORES['LINKEDIN_POSTS']          = 'harvestapi~linkedin-post-search'
```

E `grep -c social_matriz regras/sensor_coleta.py` = **0**. A política **nunca** é
consultada ali, e `_rodar()` leva um identificador de ator direto à porta paga.
A fase `canais()` usa isso.

```
    UM CAMINHO QUE NÃO PERGUNTA À POLÍTICA NÃO É PROTEGIDO PELA POLÍTICA.
```

**O que o tranca hoje é outro dono.** Medido com chave no pool — para que a falta
de token não se confunda com uma trava, que é precisamente o que o C11 registou
como `FIRST_BREAK`:

```
SemAutorizacaoDeGasto · «Ter chave, teto e rota permitida não é ter autorização»
POSTS = 0
```

É a guarda de gasto da `SCRAP-SR-02`, no único sítio que cria execução paga.
Então `HARVESTAPI_ACCIDENTAL_PATH = 0` é **verdade**, e a razão não é a política.
Registado, com sentinela (A14b) para que a tranca não se perca em silêncio. **Não
consertado nesta missão** — corrigir a consciência de política do
`regras/sensor_coleta.py` inteiro seria expandir.

---

## N · O QUE NÃO FOI FEITO

Nada de: pesquisar APIs, estudar scrapers, comprar HarvestAPI, executar Apify,
login, cookies, Voyager, browser, vídeo, caption, ASR, comentários, carrossel,
reprocessar os 372 posts, portal, Intelligence, nova arquitetura, migrar outras
plataformas, refactor cosmético.

Não foi feito, e é dívida declarada: tornar `regras/sensor_coleta.py`
consciente da política (§M).

---

## O · DESCONHECIDOS

- **A profundidade da descoberta indireta não está medida.** Uma sentinela de
  sete, uma com handle. Quantas organizações do acervo publicam o seu é
  `NOT_MEASURED` — e medi-lo é uma passagem por sites de terceiros, não uma
  decisão de código.
- **Se o handle descoberto corresponde à organização certa** não é verificável por
  esta rota: ela devolve o que o site publica. `PUBLICADO PELA ORGANIZAÇÃO !=
  VERIFICADO`.
- **O que fazer com o catálogo** é decisão de quem coordena. Ele é candidato, e o
  contrato de candidatas/descobertas é quem o recebe — não esta missão.

---

## P · RISCO RESTANTE

1. **`regras/sensor_coleta.py`** está trancado pelo dono do **gasto**, não pelo da
   **política**. Uma autorização de gasto concedida ali abriria quatro atores
   LinkedIn sem a política ser perguntada. É o risco mais alto desta lista.
2. **A rota depende de um site de terceiro**, e cinco das sete sentinelas do C11
   falharam no WAF ou na ligação. Nenhuma falha é do LinkedIn, e nenhuma é
   consertável daqui.
3. **`transporte` é um parâmetro público** que chega pelo `**extra` do `COLLECT`.
   A recusa de host agora é estática e vem antes dele, mas quem passa
   `transporte` continua a poder devolver o que quiser — é a porta dos testes, e
   ela existe de propósito.
4. **Três execuções reais aconteceram** numa missão que planejava uma. A primeira
   foi por correr o CLI sem transporte falso. Zero dólares e zero pedidos ao
   LinkedIn, mas a lição fica: um CLI sem falso injetado **vai à rede**.

---

## Q · FECHO

```
LINKEDIN_ALLOWED_CAPABILITY                = WIRED
COLLECTION_REQUEST_TO_LINKEDIN_EDGE        = PROVEN
LINKEDIN_INDIRECT_DISCOVERY                = EXECUTABLE
LINKEDIN_HTTP_REQUESTS_FROM_ALLOWED_ROUTE  = 0
PAID_LINKEDIN_START_POSTS                  = 0
HARVESTAPI_ACCIDENTAL_PATH                 = 0
LINKEDIN_FETCH_POST                        = ROUTE_NOT_ALLOWED
SOURCE_ID_FABRICATED_FROM_URL              = 0
ERROR_AS_ZERO_RESULTS                      = 0
SURVIVING_ATTACKS                          = 0
SURVIVING_MEANINGFUL_MUTANTS               = 0
NEW_FAILURES                               = 0
SYSTEM_MAP_CHECK                           = PASS

REAL_ALLOWED_SENTINEL                      = PASS

BIBLE_CHANGE_REQUIRED                      = NO
LINKEDIN_V1                                = READY_FOR_COLLECTION_USE
```

E `READY` significa **apenas** isto: o SINTONIA consegue pedir canonicamente a
descoberta permitida de identidade LinkedIn, executar pela rota correta, preservar
a observação e a proveniência, e devolver pelo contrato certo; e qualquer pedido de
conteúdo LinkedIn sem rota permitida é recusado antes de rede paga.

**Não significa** que se consegue colher posts, comentários ou fala.
