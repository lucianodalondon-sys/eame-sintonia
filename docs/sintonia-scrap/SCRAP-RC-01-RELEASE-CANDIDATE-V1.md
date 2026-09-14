# SCRAP-RC-01 — A RELEASE CANDIDATE DO SINTONIA SCRAP V1

> **Este documento tem duas partes.** A primeira fechou a Release com a máquina
> provada e três decisões humanas por tomar. A segunda — §14 em diante —
> absorveu o que chegou de fora **depois**: a linha operacional do LinkedIn, as
> propriedades de gasto da `SCRAP-CV-02`, e o caminho lateral que as duas
> juntas tornaram impossível continuar a chamar de risco registado.
>
> **O que mudou de veredito:** a primeira parte declarava a porta paga fechada.
> Ela estava fechada **ao dinheiro**, e aberta à **política** — e essas são
> duas trancas.
>
>     SPEND_AUTHORIZATION != ROUTE_POLICY.

> A pergunta era uma só:
>
> **Existe uma única árvore na qual a superfície operacional escolhida para
> SCRAP V1 entra por REQUEST/ORCHESTRATOR, obedece aos owners canônicos, executa
> somente capacidades permitidas, preserva RAW/retorno corretamente e entrega à
> Collection sem bypass ativo?**
>
> **Existe.** E ela não está operacional, porque falta uma decisão de gente que
> nenhuma máquina pode tomar por ninguém.
>
> ```
> SCRAP_ENGINE_READY       = PASS
> SOURCE_RELEVANCE_READY   = NO
> SCRAP_OPERATIONAL_READY  = NO
> SCRAP_V1                 = READY_PENDING_SOURCE_APPROVAL
> ```
>
> Isto é o **Estado B** da missão. É um resultado técnico aceitável, e não se
> chama operacional.

---

## 1 · A SUPERFÍCIE, MEDIDA NO RUNTIME

`provas/superficie_do_scrap_v1.py` lê as 35 capacidades declaradas e classifica
cada uma pelos cinco estados que a missão nomeia. Nenhuma lista foi escrita à
mão — e essa frase custou duas correções antes de ser verdade.

| estado | quantas |
|---|---|
| `READY` | 8 |
| `READY_PENDING_CREDENTIAL` | 6 |
| `FAIL_CLOSED` | 5 |
| `NOT_IN_V1` | 16 |
| `UNKNOWN` | 0 |

As oito `READY`: `bluesky.account.discovery`, `bluesky.author.incremental`,
`mastodon.hashtag.search`, `telegram.channel.incremental`,
`instagram.profile.discovery` e as três `instagram.reel.*`.

**`FAIL_CLOSED` é um estado válido, e `UNKNOWN` continua `UNKNOWN`.** Nenhuma
capacidade sem prova foi rebaixada a bloqueada para o número ficar mais limpo.

### Duas vezes esta prova mediu o que ela própria imaginou

A primeira versão nomeava quatro plataformas **à mão** e deixava o **Telegram**
de fora — capacidade `PROVEN`, rota ligada, política `ALLOWED`, custo zero. A
lista passou a ser derivada das arestas e da política.

    UMA SUPERFÍCIE ESCRITA À MÃO É A MEMÓRIA DE QUEM A ESCREVEU.

A segunda comparava o `STATE` do `CHECK` com uma lista de palavras que **ela**
achava que significavam sim. `CAN_COLLECT_NOW` não estava na lista, e cinco
capacidades a funcionar apareciam fechadas. Passou a ler o campo `CAN`, que é o
que o dono responde.

    UMA SONDA QUE ADIVINHA O VOCABULÁRIO DE OUTRO DONO
    MEDE O QUE ELA IMAGINOU QUE ELE DIRIA.

---

## 2 · O DELTA DO FLOW-02, PORTADO — E SÓ ELE

As duas linhas já roteavam `janela*` pelo orquestrador. O único delta semântico
real era o **teto de objetos**, que a própria SCRAP-FLOW-01 tinha perdido ao
migrar: `social_scrap.py coletar FASE $TETO` passava-o posicionalmente, e o
pedido não o levava.

    MIGRAR UM CAMINHO É MUDAR POR ONDE ELE PASSA, NÃO O QUE ELE LEVA.

Ele voltou como **filtro nomeado** (`filtros_nomeados` na receita →
`--teto=` na linha de comando), e não como um terceiro posicional — um terceiro
argumento sem nome seria indistinguível da fonte no dia em que alguém omitisse
uma delas.

Nenhum merge, nenhum cherry-pick de bloco. Nada da autorização antiga, nenhum
segundo selector, nenhum segundo envelope, nenhum segundo dono do executor.

---

## 3 · O CANÁRIO — E POR QUE ELE PRECISOU DE UMA ARESTA NOVA

§8 pede uma rota **gratuita, permitida, sem credencial paga, sem navegador
autenticado e sem fornecedor pago**. Medidas as candidatas em vez de assumidas:

| candidata | estado | onde corre | custo |
|---|---|---|---|
| `instagram.profile.discovery` | `PARTIAL` | `LOCAL` · `DATACENTER_BLOCKED` | grátis |
| `bluesky.author.incremental` | `PROVEN` | `ONLINE` | grátis |

E aqui apareceu o achado que decidiu a missão: **a única fase que o caminho
canônico sabia pedir era uma que este ambiente não consegue executar.** As três
fases `janela*` correm `instagram.profile.discovery`, que precisa de máquina
residencial.

    UMA ÁRVORE QUE SÓ SABE PEDIR O QUE NÃO CONSEGUE CORRER
    NÃO SE CONSEGUE PROVAR A CORRER.

Então a fase `canario-bluesky` entrou — **e isto não abre plataforma nenhuma**.
O adaptador (`coleta/adaptador_aberto.py`), o registo da rota, a linha da matriz
e o trial ao vivo de 2026-09-12 existiam todos antes desta missão. O que não
existia era a aresta do pedido até eles.

O alvo desce como filtro nomeado `handle`, ao lado de `--fonte`, porque são
duas coisas:

    HANDLE É O ENDEREÇO DA OBSERVAÇÃO. SOURCE_ID É A IDENTIDADE PROVADA.
    HANDLE NÃO É SOURCE_ID.

E `coleta/scrap_colheita.py::NOMEADOS` declara, **por fase**, que filtros ela
aceita. Um nome fora da lista recusa a corrida em vez de morrer no `**_` do
adaptador:

    UM ARGUMENTO QUE A ROTA ENGOLE SEM USAR NÃO É OPCIONAL: É UMA ARMADILHA.

---

## 4 · A ÁRVORE FINAL CORRE PONTA A PONTA — OFFLINE

`provas/o_canario_do_scrap_v1.py` corre o caminho inteiro numa cópia da árvore.
**O que é falso é `urllib.request.urlopen` — o socket, e nada acima dele.** São
reais o orquestrador, o plano, o adapter, o executor, o portão do `robots`, o
teto de rede, o roteador, a política de rota, o adaptador, a guarda de gasto, o
contrato de retorno, o ingresso e a admissão.

```
CANARY_CAPABILITY    bluesky.author.incremental
CANARY_SOURCE_ID     IT-T9-001            (vindo do PEDIDO)
RUN_ID               IT-T9-2026-09-12-…   (cunhado pelo orquestrador)
RAW_OBSERVATION_ID   at://did:plc:…/app.bsky.feed.post/…   (id nativo)
STORAGE_OBJECT       data/samples/SOCIAL-IT/raw-free/BLUESKY/authorFeed-…
STORAGE_STATE        NOT_PRESERVED  ·  dono: G-42 forward
RETURN_SPECIES       COLHEITA · RUN_RECEIPT
INGRESS_RESULT       PRESERVADOS 1 · RECUSADOS 0
REAL_CANARY          NOT_RUN
MODE                 OFFLINE_FAKE_SOCKET
FALHAS               0
```

`DOCUMENT_ID` sai `NAO SEI` por lei. `RAW_OBSERVATION_ID` é o id nativo e nunca
o SHA nem o `RUN_ID`. O bruto diz que **não** está preservado, e nomeia quem
ainda tem de o receber.

### O falso teve de descer um andar a mais do que na FLOW-01

A primeira versão instalou o mundo falso dentro do driver e mediu **zero** idas
ao mundo. O orquestrador corre o adapter como processo separado, e esse neto
arranca com o `urlopen` verdadeiro. A FLOW-01 já tinha pago esta lição um andar
acima; a RC-01 pagou-a um andar abaixo.

    UM FALSO QUE VIVE NA MEMÓRIA DO PAI NÃO EXISTE PARA O FILHO —
    E O FILHO TAMBÉM TEM FILHOS.

A correção é `sitecustomize` no `PYTHONPATH`: o `site` importa-o **antes** de
qualquer linha da árvore correr, em todo processo da cadeia.

---

## 5 · A RELEVÂNCIA NÃO PARA A MÁQUINA. ELA PARA O GASTO

Este é o achado que muda a leitura de «o livro está vazio». Medido, os quatro
eixos, contra o livro vazio:

| plano | formas de gasto abertas | bloqueia? |
|---|---|---|
| grátis · pontual | nenhuma | **não** |
| grátis · **agendado** | `COLETA_RECORRENTE` | sim |
| **pago** · pontual | `ROTA_PAGA` | sim |
| grátis · escopo **TOTAL** | `COLETA_TOTAL` | sim |

    O PORTÃO GUARDA O GASTO, NÃO A OBSERVAÇÃO.  (COL-LAW-018)

Uma rota gratuita e pontual sobre uma fonte nomeada **corre hoje**, com o livro
vazio, e isso não é um furo: é a lei a funcionar. O que o livro vazio impede é
comprar, repetir sozinho, e varrer tudo.

---

## 6 · AS ENTRADAS DA V1

`provas/entradas_do_scrap_v1.py` varre os 19 workflows, corta a prosa, e segue a
**cadeia declarada** de cada ramo — receita, executor, tabela de fases — até à
capacidade que ele consegue pôr a correr.

```
ACTIVE_V1_ENTRYPOINTS         4     (janela · janela-perfis · janela-objetos · canario-bluesky)
ACTIVE_V1_CANONICAL           4
ACTIVE_V1_BYPASSES            0
ACTIVE_V1_HIDDEN_FALLBACKS    0
NOT_IN_V1                    19
DESVIOS_DECLARADOS_ALCANCAVEIS 4
```

Os quatro desvios vivem em `scrap-social.yml` e são os que
`coleta/social_scrap.py::FASES_QUE_NAO_ATRAVESSAM_O_BOUNDARY` já declara: eles
adquirem, saltam o `COLLECT`, e **dizem-no na saída**.

    UM DESVIO DECLARADO É UMA MEDIÇÃO. UM DESVIO CALADO É UM BURACO.

### Duas vezes esta sonda mediu o nome em vez da coisa

Primeiro derivou «é V1» do **nome da fase** e acusou um bypass que não existe:
`sintonia-scrap.yml` tem uma fase `contratos` que lê o INPUT SCHEMA de um ator, e
`comunicacao-publica` tem outra fase `contratos` que é outra coisa.

    DUAS PORTAS COM O MESMO NOME NÃO SÃO A MESMA PORTA.

Depois ganhou uma lista à mão de «estes ficam de fora», com um motivo por
workflow. Mediu-se o que ela mudava: **nada** — os mesmos 4 canônicos e os
mesmos 19 fora, com ela e sem ela. E um dos motivos estava **errado**: dizia que
`scrap-evidencia.yml` corre `social_scrap.py` para colher, quando o que ele corre
é `evidencia-publicar` e `evidencia-recuperar`, que leem o acervo e não adquirem.

    UMA LISTA À MÃO QUE NÃO MUDA NENHUM NÚMERO NÃO ESTÁ A DECIDIR:
    ESTÁ A LEMBRAR-SE. E LEMBRA-SE MAL.

A lista foi retirada. Decide a travessia.

---

## 7 · A PORTA PAGA, ATACADA NA ÁRVORE FINAL

`provas/red_team_da_release_v1.py` — 28 ataques, **0 sobreviventes**. Os sete
portões da §12, mais os vinte da §14.

```
G1  sem autorização nenhuma          → POSTS=0 · AUTORIZACAO_AUSENTE
G2  autorização fabricada à mão      → AutorizacaoInvalida (nem nasce)
G2b dicionário com a mesma forma     → POSTS=0 · AUTORIZACAO_FABRICADA
G3  autorização esgotada             → POST1=1 · POST2=0 · AUTORIZACAO_ESGOTADA
G4  relevância ausente               → nem autorização nasce
G5  sem teto financeiro em NORMAL    → POSTS=0 · SEM_TETO_NO_FORNECEDOR
G6  teto de rede recusa              → POSTS=0 · SemOrcamentoDeRede
G7  todos os portões passam          → POSTS=1
```

Um ataque sobreviveu na primeira volta — e o defeito era **meu**. `A15 · ERROR
vira REJECTED` pedia que `ROUTE_NOT_ALLOWED` **não** fosse falha.
`leis/falhas.py` diz que é, e é o dono. O ataque verdadeiro era o outro: um host
que cai tem de sair do outro lado como falha, e nunca como «a fonte não tinha
nada».

    ESGOTAR, CAIR E SER RECUSADO NÃO É A FONTE ESTAR VAZIA.

E o `A6` atacava a rota grátis contra um host reservado — o que ele mediu foi uma
resolução de DNS a falhar, que **é** uma ida à rede numa missão que declara
`REDE REAL = 0`. O socket passou a fechar-se antes do primeiro ataque.

---

## 8 · MUTAÇÃO — E DOIS MUTANTES QUE ACUSARAM A DEFESA, NÃO A BATERIA

`provas/mutacao_da_release_v1.py` — **20 mutantes, 0 sobreviventes**, cobrindo as
dez classes que a §15 nomeia. Na primeira volta sobreviveram **nove**, e cada um
apontou uma coisa diferente.

**Sete eram buracos reais da bateria**, e ganharam sentinela:

- `autorizar()` sem livro passou a ser testado direto (`rt39`);
- a `Autorizacao` construída à mão passou a ser testada direto (`rt38`);
- o `CHECK` de uma capacidade não declarada tem de dizer `CAPABILITY_NOT_DECLARED`,
  e não outra razão qualquer (`rt33`);
- um estado que não promete resultado não colhe em `NORMAL` (`rt34`);
- uma capacidade declarada sem rota não pode correr (`rt35`);
- o portão não promove o estado da capacidade (`rt36`);
- o adapter não deriva a fonte do alvo (`rt40`).

**E um era uma tautologia minha.** `rt04` comparava os estados da superfície
contra `sup.READY` — as constantes do próprio módulo. Trocar o **valor** de
`READY` para `FLOW_OBSERVED` deixava a sentinela verde, porque os dois lados
mudavam juntos.

    MEDIR A LEI CONTRA A PRÓPRIA LEI É MEDIR UMA TAUTOLOGIA.

**Os outros dois eram equivalentes, e isso mediu-se.** Destrancar `permitir_pago`
no roteador não muda nada, porque a linha seguinte recusa pelo motivo de gasto e
escreve o **mesmo** estado. Tirar a aresta do classificador da superfície não
muda nada, porque o `CHECK` já responde `DECLARED_WITHOUT_ROUTE`.

    UM MUTANTE QUE NÃO MUDA NENHUM NÚMERO NÃO ACUSA A BATERIA:
    ACUSA A DEFESA EM PROFUNDIDADE QUE ELE NÃO CONSEGUIU ATRAVESSAR.

Os dois foram movidos para onde a lei realmente morde — a escolha de rota em
`social_matriz._rota_padrao`, e o `tem_caminho` do `CHECK` — e morreram.

---

## 9 · UM BRUTO FABRICADO QUASE ENTROU NO ACERVO

A bateria apontava `social_envelope.RAW_DIR` para um banco temporário **no
import**. Na suíte inteira, outra bateria reaponta-o para o acervo verdadeiro — e
a partir daí esta escrevia lá. Uma observação **inventada**, com um handle que
não existe, dentro de `data/samples/`. Ficou em `git add` antes de ser apanhada.

    UM REDIRECIONAMENTO FEITO NO IMPORT VALE ATÉ ALGUÉM IMPORTAR OUTRA COISA.

A correção: `pinar_o_banco()` corre **antes de cada corrida**, e uma sentinela
confere que o bruto caiu dentro do banco da prova.

---

## 10 · REGRESSÃO E MAPA

```
OLD_FAILURES   = 22
NEW_FAILURES   = 0
FIXED_FAILURES = 1
TESTES NOVOS   = 40   (todos verdes)
```

Comparado **por identidade**, nome a nome, contra `64422049` — porque duas suítes
com o mesmo total podem ter trocado qual delas falha.

    COMPARAR TOTAIS COMPARA O TAMANHO, NÃO O CONTEÚDO.

`SYSTEM_MAP_CHECK = PASS`, cadeia inteira corrida a partir de
`CADEIA-DO-MAPA.json`. O mapa ganhou `C-SUPERFICIE-SCRAP-V1`, em `Z-PROVA`, que
distingue os quatro estados operacionais e diz por que cada um existe.

---

## 11 · O QUE FALTA — EXATAMENTE TRÊS DECISÕES DE GENTE

Nenhuma delas é técnica, e **nenhuma foi fabricada aqui**. O livro de relevância
continua vazio e o atlas continua com 29 fichas, nenhuma delas uma conta em
plataforma aberta.

### DECISÃO 1 — obrigatória para o canário ao vivo

**Nomear uma conta real e ligá-la a um `SOURCE_ID` do atlas.**

Hoje não existe par legítimo `(SOURCE_ID, handle)`: o atlas não tem ficha de
nenhuma conta Bluesky, Mastodon ou Telegram. A prova desta missão usou um
`SOURCE_ID` real com um handle `.invalido` — e é **por isso** que ela não é o
canário ao vivo. Emparelhar `IT-T9-001` com um handle que a ficha nunca declarou
seria fabricar identidade um andar acima.

Forma: estender a ficha `FR/ES/IT-T9-001` para declarar a conta como um dos seus
canais, ou abrir ficha nova.

### DECISÃO 2 — obrigatória para coleta paga, recorrente ou total

**Uma linha no livro de relevância, para o par `(SOURCE_ID, PROPOSITO)`.**

Com os campos que `leis/relevancia_da_fonte.py::CAMPOS_DA_DECISAO` exige, e com
`EVIDENCIA` apontável — um `SIM` sem nada apontável é uma opinião com ar de
medição. **Não é necessária para o canário grátis e pontual.**

### DECISÃO 3 — só se o canário for correr sozinho

**Autorizar a recorrência.**

`acionamento=AGENDADO` abre `COLETA_RECORRENTE`, que é forma de gasto, e aí o
livro volta a ser obrigatório. Um canário disparado à mão não precisa dela.

---

## 12 · O QUE FICA POR SABER

- **Meta e LinkedIn operacionais não existem nesta conta.** Procurados em
  commits e em ramos: `LINKEDIN-OP-01` e `META-OP-01` não têm branch, não têm
  commit, não têm HEAD. Não são linhas em movimento — são linhas que ainda não
  começaram. Nada foi absorvido, e nada devia.
- **A preservação forward continua `NOT_PRESERVED`.** O bruto do canário fica no
  disco do runner com SHA e dono nomeado. O dono forward é o G-42, e não nasceu
  aqui.
- **Quatro desvios declarados continuam alcançáveis** por `scrap-social.yml`.
  Fora da V1, declarados no dono, e a dizerem-no na saída. Fechá-los é fan-out,
  e não era desta missão.
- **`instagram.profile.discovery` continua `DATACENTER_BLOCKED`.** As três fases
  `janela*` são V1 e canônicas, e só correm em máquina residencial. Isso não é
  defeito: é o ambiente, medido.

---

## 13 · A LINHA DE FECHO

```
ONE_ORCHESTRATION_OWNER                  = PROVEN
SPEND_AUTH_OWNER_COUNT                   = 1
SOURCE_RELEVANCE_OWNER_COUNT             = 1
ACTIVE_V1_BYPASSES                       = 0
ACTIVE_V1_HIDDEN_FALLBACKS               = 0
FREE_ROUTE_DOES_NOT_REQUIRE_SPEND_AUTH   = PASS
PAID_ROUTE_FAILS_CLOSED                  = PASS
SUPPORTED_CAPABILITIES_HAVE_EDGE         = PASS
UNSUPPORTED_CAPABILITIES_FAIL_CLOSED     = PASS
RETURN_CONTRACT                          = PASS
SCRAP_TO_COLLECTION_INGRESS              = PASS
SURVIVING_ATTACKS                        = 0
SURVIVING_MEANINGFUL_MUTANTS             = 0
NEW_FAILURES                             = 0
SYSTEM_MAP_CHECK                         = PASS

SCRAP_ENGINE_READY      = PASS
SOURCE_RELEVANCE_READY  = NO
REAL_CANARY             = NOT_RUN
SCRAP_OPERATIONAL_READY = NO
SCRAP_V1                = READY_PENDING_SOURCE_APPROVAL

APIFY_RUNS = 0 · PROVIDER_RUNS = 0 · PAID_USD = 0 · REDE REAL = 0
```

A máquina está pronta. Falta dizer-lhe **de quem** ela vai ouvir.

---
---

# PARTE II — O QUE CHEGOU DE FORA, E O QUE ELE ABRIU

## 14 · TRÊS LINHAS EXTERNAS MEDIDAS, DUAS RECUSADAS, UMA ABSORVIDA

A primeira parte declarou que `LINKEDIN-OP-01` e `META-OP-01` **não existiam**.
Essa informação envelheceu enquanto a missão corria. Medido de novo:

| linha | HEAD | base comum | contrato de gasto | veredito |
|---|---|---|---|---|
| LinkedIn operacional | `642be9bc` | `84422284` | v1, sem selo | **ABSORVIDA, por delta** |
| `SCRAP-CV-02` | `a1a78900` | `84422284` | v1, sem selo | **PROPRIEDADES PORTADAS** |
| META-OP-01 | `6a9907e2` | `e90451e1` | v1, sem selo | `PENDING_EXTERNAL_LINE` |

As três nasceram **antes** da convergência da `SCRAP-OWNER-01`, e as três
carregam `AUTORIZACAO_DE_GASTO/v1` com **zero** ocorrências do selo privado —
a autorização que um dicionário conseguia fabricar.

    UM DELTA QUE VEM COM O DONO ANTIGO NÃO É UM DELTA: É UM RETROCESSO
    COM CARA DE PROGRESSO.

**Meta ficou de fora, e a razão é medida, não preferida.** A divergência entre
a Release e a linha Meta é de **241 ficheiros e 94 mil linhas**, e dentro dela
está `tests/test_scrap_sr02_autorizacao.py` (+399) contra
`tests/test_scrap_sr02_autorizacao_de_gasto.py` (−503) — o dono do gasto
anterior, vivo, com outro nome de ficheiro. Portar dali exigiria re-derivar o
trabalho de transporte e token da Meta sobre a base convergida, que é uma
missão de integração Meta, e esta missão tem ordem de não abrir nenhuma.

Nada foi mergeado. Nenhuma das três é ancestral desta linha — medido com
`git merge-base --is-ancestor`, e zero merges desde a base.

---

## 15 · CV-02 — QUATRO PROPRIEDADES QUE FALTAVAM, E QUE NÃO SE VIAM

§3 mandou comparar **propriedade por propriedade**, e não por nome de missão.
Medido na árvore da Release, antes de qualquer alteração:

| propriedade | antes | depois |
|---|---|---|
| `SPEND_AUTH_SEALED` (construção à mão) | PASS | PASS |
| `SPEND_AUTH_CONSUMABLE` | PASS | PASS |
| `SEALED_AGAINST_WRITE` | **FALHA** | PASS |
| `AUTH_COPY_ACCEPTED` | **SIM — a cópia comprava** | NÃO |
| `FINANCIAL_BUDGET_LE_AUTH` | **FALHA** | PASS |
| `ONE_LEDGER_PER_AUTH` | **FALHA** | PASS |

Quatro buracos reais, cada um reproduzido antes de corrigido:

```
a.max_usd = 99.0                       -> ACEITE  (autorização de 0,10)
copy.copy(a)                           -> COMPROU (uma autorização, dois POSTs)
orçamento 99,00 sob autorização 0,10   -> COMPROU
a mesma autorização em dois orçamentos -> COMPROU nos dois
```

### O consumo saiu de dentro da autorização

O contador vivia num campo do objecto, e **uma cópia leva o campo com ela**. A
`deepcopy` já morria no selo, porque reconstrói; a `copy` rasa não reconstrói
nada — copia o `__dict__` inteiro, selo incluído.

    COPIAR UMA AUTORIZAÇÃO NÃO É RECEBER UMA AUTORIZAÇÃO.

O consumo passou a viver num registo do módulo, indexado pela identidade cunhada
na concessão. Uma cópia leva o mesmo nome, e o mesmo nome encontra o mesmo
contador.

    UMA AUTORIZAÇÃO VALE POR IDENTIDADE, E NÃO PELA FORMA.

### E o ledger ganhou um nome — depois de eu lhe ter dado o errado

A primeira tentativa identificou o orçamento por `id(objecto)`. Duas execuções
seguidas receberam **o mesmo número**: o primeiro orçamento morre, o alocador
reaproveita o endereço, e a autorização reconheceu o ledger novo como o antigo.

    UMA IDENTIDADE QUE O ALOCADOR PODE REUTILIZAR NÃO É UMA IDENTIDADE.

Cada `OrcamentoFinanceiro` passou a nascer com identidade própria.

---

## 16 · LINKEDIN — IDENTIDADE ENTRA, CONTEÚDO NÃO

Portado o delta, e **só** ele: o adaptador, a capacidade, a política, as provas
e os testes. O ficheiro da autorização **não** veio junto.

```
linkedin.identity.discovery   READY · DIRECT_HTTP · grátis · FLOW_OBSERVED
linkedin.direct_post          BLOCKED
linkedin.native_video         BLOCKED
linkedin.native_caption       BLOCKED
linkedin.recent.discovery     BLOCKED   (era PROVEN)
```

`PROVEN → BLOCKED` não é um recuo técnico. A rota paga funciona e continua
`PERMITIDA = NAO` nas duas rotas que a matriz declara para `FETCH_POST`.

    TECHNICALLY_PROVEN_HISTORY != CURRENT_ALLOWED_ROUTE.
    UMA ROTA QUE FUNCIONA NÃO É UMA ROTA PERMITIDA.

### A quarta posição de `FASES`, e o que ela impede

Cada fase passou a declarar **que espécie de retorno produz**, obrigatoriamente
e sem valor por omissão.

    UMA ESPÉCIE POR OMISSÃO É UMA DECISÃO QUE NINGUÉM TOMOU.

`identidade-linkedin` declara `CATALOG`, e `ENTRAM_NO_INGRESSO = (COLHEITA,)`.
Provado na árvore da Release: a fase corre, devolve um endereço, e a colheita
sai **zero** — não por falha, mas por espécie.

    IDENTITY != CONTENT. UM ENDEREÇO NÃO É UMA PUBLICAÇÃO.
    UM ZERO QUE VEM DA ESPÉCIE NÃO SE LÊ COMO UM ZERO QUE VEM DA FONTE.

### O mecanismo que ficou foi o desta linha

A `LINKEDIN-OP-01` passava o alvo como **terceiro posicional**. A Release já
tinha filtros nomeados por fase, com recusa de nomes fora da lista. Portou-se o
comportamento, não o mecanismo — e a tradução `site → site_url` mora na tabela,
à vista.

    PORTA-SE O COMPORTAMENTO, NÃO O MECANISMO.
    E O MECANISMO QUE FICA É O QUE RECUSA MAIS CEDO.

---

## 17 · O CAMINHO LATERAL — E POR QUE «É LEGADO» NÃO O FECHAVA

`regras/sensor_coleta.py` configura quatro atores HarvestAPI do LinkedIn e leva
um identificador de ator **direto à porta paga**, sem nunca perguntar à matriz.
A `LINKEDIN-OP-01` mediu-o e registou-o como risco. O que o trancava era a
guarda de **gasto**.

Uma tranca de dinheiro guarda enquanto não houver dinheiro.

    SPEND_AUTHORIZATION != ROUTE_POLICY.
    DINHEIRO AUTORIZADO NÃO TORNA PERMITIDA UMA ROTA PROIBIDA.

E o botão continua lá: `workflow_dispatch`, alcançável à mão, hoje.

    DIZER «É LEGADO» NUM DOCUMENTO NÃO DESLIGA UM BOTÃO.

### A correcção vive na primitiva, e não no caminho

`coleta/coletor.py` — o único sítio onde nasce execução paga — pergunta a
`social_matriz.actor_proibido()` **antes** da guarda de gasto.

    UMA GUARDA QUE VIVE NUM CAMINHO GUARDA UM CAMINHO.
    UMA GUARDA QUE VIVE NA PRIMITIVA GUARDA TODOS.

A polaridade importa, e é fail-closed **só sobre o que está nomeado**: responde
proibido quando a matriz nomeia o ator numa rota `PERMITIDA = NAO` e em nenhuma
permitida. Um ator que a matriz não nomeia não é proibido por omissão — a maior
parte dos atores desta casa é nomeada pela capacidade, não pelo id.

    DECLARADO PROIBIDO != NÃO DECLARADO.
    O SILÊNCIO DA MATRIZ NÃO PROÍBE, E TAMBÉM NÃO AUTORIZA.

E a recusa tem classe própria. Vesti-la de `GastoRecusado` diria que faltou
autorização — e no dia em que alguém a concedesse, a rota continuaria proibida e
a mensagem mandaria procurar no sítio errado.

Medido, com tudo válido do outro lado:

```
ator HarvestAPI LinkedIn + token válido + autorização válida + orçamento
  -> RotaNaoPermitida · POSTS = 0 · autorização consumida = 0
```

A autorização **nem foi tocada**: a política parou antes do dinheiro.

---

## 18 · AS ENTRADAS, RECONTADAS POR ESTRUTURA

§6 mandou parar de responder isto com grep. Duas correcções:

**O corte de prosa deixou de ter duas implementações.**
`system-map/scripts/censo_da_coleta.py` já o fazia há missões, com a razão
escrita lá. Esta prova passou a chamá-lo.

    DUAS IMPLEMENTAÇÕES DO MESMO CONTRATO NÃO SÃO DUAS VERSÕES DA VERDADE:
    SÃO DUAS VERDADES.

**E as três classes viraram seis**, porque o balde do «legado» juntava coisas
que não são a mesma:

| classe | quantas |
|---|---|
| `CANONICAL_V1` | 5 |
| `ACTIVE_V1_BYPASS` | **0** |
| `MEASUREMENT_ONLY` | 1 |
| `LOCAL_REPROCESSING` | 13 |
| `FAIL_CLOSED` | 0 |
| `LEGACY_NOT_IN_V1` | 5 |
| `UNKNOWN` | 0 |

    NÃO SE CHAMA REPROCESSAMENTO LOCAL DE BYPASS DE AQUISIÇÃO.
    NÃO SE CHAMA FERRAMENTA DE MEDIÇÃO DE ROTA DE PRODUÇÃO.

A primeira versão desta classificação pôs `yt-legenda-paga` em
`LOCAL_REPROCESSING` porque o ficheiro que ele corre não abre socket nenhum
sozinho. Ele colhe pela rota **paga** do YouTube.

    QUEM DELEGA A IDA AO MUNDO CONTINUA A IR AO MUNDO.

E o gate novo mede-se **correndo**, não lendo: chama-se a porta paga com cada
ator que um ramo alcançável configura, e vê-se o que sai.

    LER A ÁRVORE PROVA QUE A PEÇA EXISTE. SÓ CORRER PROVA QUE A ARESTA EXISTE.

```
MANUALLY_TRIGGERABLE_POLICY_BYPASSES = 0
```

---

## 19 · A SUPERFÍCIE, RECONGELADA COM O CAMPO QUE FALTAVA

| estado | antes | depois |
|---|---|---|
| `READY` | 8 | **9** |
| `READY_PENDING_CREDENTIAL` | 6 | 6 |
| `FAIL_CLOSED` | 5 | **12** |
| `NOT_IN_V1` | 16 | **9** |
| `UNKNOWN` | 0 | 0 |

E ganhou `FIRST_BREAK`, que é o campo mais útil da tabela: saber que uma
capacidade não corre vale pouco; saber **onde** ela para diz de quem é a próxima
decisão. Cinco das nove `READY` param em `NO_REQUEST_PATH` — estão prontas e
ninguém no caminho canônico as pede. Não é defeito; é uma lista de trabalho.

`FLOW_OBSERVED` tem três degraus, e nenhum promete o seguinte:

    NO -> WIRED -> OBSERVED.
    EDGE EXISTS != FLOW OBSERVED. Uma aresta lida na árvore não anda.

---

## 20 · O CANÁRIO CORREU A SÉRIO

Bluesky continua o canário: LinkedIn testa LinkedIn, Bluesky testa a máquina.

```
REAL_CANARY            = PASS
CANARY_CAPABILITY      = bluesky.author.incremental
RUN_ID                 = IT-T9-2026-09-13-012809
REAL_REQUESTS          = 1 rota + 1 robots
RESULT                 = OK
COST_STATE             = FREE_ROUTE_BY_POLICY
REAL_COST_USD          = 0
OBSERVADOS             = 1
COLHEITA               = 0
```

Uma requisição, uma conta pública, sem lote, sem paginação, sem provider pago.

**A colheita é zero por LEI, e não por falha.** O pedido não nomeou fonte, e o
adapter declara-o por escrito: sem `SOURCE_ID` vindo do pedido, o que se
observou são **candidatas**, não observações de uma fonte provada.

    URL NÃO É SOURCE_ID. O QUE NÃO SE DECLAROU NÃO ENTRA.

E não se nomeou fonte porque **não há nenhuma para nomear**: as 29 fichas do
atlas não incluem nenhuma conta Bluesky, Mastodon ou Telegram. Emparelhar
`IT-T9-001` com um handle que a ficha dele nunca declarou seria fabricar
identidade um andar acima — exactamente o que a máquina toda existe para
impedir.

Nenhum ficheiro novo de bruto apareceu. O bruto é endereçado por conteúdo, e
esta casa já tinha capturado a mesma conta antes; o mais provável é que o hash
tenha batido e a escrita tenha sido dispensada. **Não o confirmei**, e por isso
não o afirmo.

---

## 21 · OS PORTÕES, NA ÁRVORE FINAL

```
ATTACKS = 43   ·   SURVIVING_ATTACKS = 0
MUTANTS = 30   ·   SURVIVING_MEANINGFUL_MUTANTS = 0
```

Três ataques e um mutante sobreviveram à primeira volta, e **os quatro eram
defeitos das minhas próprias sondas**:

- um contava a classe `NOT_IN_V1`, que a §6 tinha partido em quatro. Contava
  zero e dava-se por satisfeita;
- um perguntava «houve merge bruto?» ao histórico **inteiro** da casa, e
  reprovava por merges de Agosto;
- um fatiava o ficheiro da lei para ler o contrato activo, em vez de perguntar
  ao módulo;
- e o mutante que pôs o conteúdo do LinkedIn de volta em `PROVEN` não fazia a
  máquina correr — mudava só o que a casa **diz**.

    UMA SONDA QUE CONTA UM NOME QUE NINGUÉM ESCREVE MAIS CONTA ZERO
    E CHAMA-LHE PROVA.

    MEDIR A HISTÓRIA INTEIRA PARA JULGAR UMA MISSÃO JULGA AS OUTRAS.

    UM MUTANTE QUE SÓ MUDA O QUE A CASA DIZ AINDA MUDA ALGUMA COISA:
    MUDA AQUILO EM QUE A PRÓXIMA MISSÃO VAI ACREDITAR.

E três âncoras de mutação deixaram de bater porque **eu** tinha mudado as linhas
que elas citavam. A missão já dizia o que fazer com isso: âncora que não bate
conta como sobrevivente.

---

## 22 · O QUE CONTINUA POR DECIDIR

As três decisões da Parte I **continuam de pé**, e a Parte II afinou a primeira:

**DECISÃO 1.** Nomear uma conta real numa plataforma que a máquina colhe, e
ligá-la a um `SOURCE_ID` do atlas. Sem isto, o canário corre e entrega zero —
não por defeito, por lei.

**DECISÃO 2.** Uma linha no livro de relevância para o par
`(SOURCE_ID, PROPOSITO)`. **Não é necessária** para a rota grátis e pontual —
medido, e o contrato não foi alargado para o fingir.

**DECISÃO 3.** Autorizar a recorrência, e só se o canário for correr sozinho.

E uma quarta, que a Parte II abriu e não fechou:

**DECISÃO 4 (não bloqueante).** Cinco capacidades `READY` param em
`NO_REQUEST_PATH`. Decidir quais entram no caminho canônico é trabalho de
release, não de engenharia — e não se faz sozinho.

---

## 23 · A LINHA DE FECHO, DEPOIS DA PARTE II

```
ONE_ORCHESTRATION_OWNER                  = PASS
SPEND_AUTH_OWNER_COUNT                   = 1
SOURCE_RELEVANCE_OWNER_COUNT             = 1
FINANCIAL_BUDGET_LE_AUTH                 = PASS   (novo)
ONE_LEDGER_PER_AUTH                      = PASS   (novo)
FREE_ROUTE_DOES_NOT_REQUIRE_SPEND_AUTH   = PASS
ROUTE_POLICY_CANNOT_BE_OVERRIDDEN_BY_MONEY = PASS (novo)
ACTIVE_V1_BYPASSES                       = 0
MANUALLY_TRIGGERABLE_POLICY_BYPASSES     = 0      (novo)
ACTIVE_V1_HIDDEN_FALLBACKS               = 0
FLOW02_ITEM_CEILING                      = PASS
LINKEDIN_RC_INTEGRATION                  = PASS   (novo)
SUPPORTED_CAPABILITIES_HAVE_EDGE         = PASS
FAIL_CLOSED_CAPABILITIES_REALLY_FAIL_CLOSED = PASS
RETURN_CONTRACT                          = PASS
SCRAP_TO_COLLECTION_BOUNDARY             = PASS
BLUESKY_CANARY_FAKE                      = PASS
SURVIVING_ATTACKS                        = 0
SURVIVING_MEANINGFUL_MUTANTS             = 0
NEW_FAILURES                             = 0
SYSTEM_MAP_CHECK                         = PASS

SCRAP_ENGINE_READY      = PASS
REAL_CANARY             = PASS   (máquina)
SCRAP_OPERATIONAL_READY = NO
SCRAP_V1                = READY_PENDING_SOURCE_APPROVAL
```

O canário real passou **como prova da máquina**: a árvore vai ao mundo, obedece
aos portões, preserva e declara. Não passou como prova de operação, porque
nenhuma fonte aprovada existe para ele colher — e `READY` não se usa com
significado maior do que a prova.

A máquina está pronta. Continua a faltar dizer-lhe **de quem** ela vai ouvir.
