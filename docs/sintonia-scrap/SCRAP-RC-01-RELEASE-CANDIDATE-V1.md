# SCRAP-RC-01 — A RELEASE CANDIDATE DO SINTONIA SCRAP V1

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
