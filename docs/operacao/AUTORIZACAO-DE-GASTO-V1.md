# AUTORIZAÇÃO DE GASTO — V1 · SCRAP-SR-02

```
MISSAO                SCRAP-SR-02 · nenhuma compra sem autorização
CONTRATO              AUTORIZACAO_DE_GASTO/v1
DONO DA GUARDA        leis/autorizacao_de_gasto.py
FACTO EXTERNO RECEBIDO  SR_01_SOURCE_RELEVANCE_GATE = PARTIAL
ONDE ESTE RELATORIO VIVE  docs/operacao/  — a mesma casa da SR-01
```

---

## A · GIT

```
BASE_HEAD    bf07e43387a415500975dea6731f3ec973735b0b   (SR-01, confirmado)
WORK_BRANCH  claude/magical-ptolemy-bonfgd
WORKTREE     limpa no início e no fim
WORKTREES    uma só: /home/user/eame-sintonia
```

### ⚠️ A SR-01 E O SINTONIA SCRAP VIVEM EM RAMOS DIFERENTES, E ISSO FOI MEDIDO

A missão manda ler `coleta/scrap_executor.py`, `coleta/scrap_fornecedores.py`,
`coleta/scrap_capacidades.py` e os contratos C10.7 / C10.8A-F / C10.8B. **Nenhum
deles existe nesta árvore.**

```
merge-base com claude/sintonia-scrap-first-paid-route-c10-8b   00a6aa35 · 2026-09-10
este ramo, à frente da base                                    67 commits
o ramo do SCRAP, à frente da base                              151 commits
leis/relevancia_da_fonte.py existe no ramo do SCRAP?           NÃO
coleta/coletor.py neste ramo                                   421 linhas
coleta/coletor.py no ramo do SCRAP                             839 linhas
```

O ramo do SCRAP foi atualizado **22 minutos antes** desta missão começar. É uma
missão paralela viva.

**A escolha, e por que ela:** construir aqui.

1. Construir no ramo do SCRAP obrigaria a duplicar `leis/relevancia_da_fonte.py`,
   que é o dono único da relevância. **Um segundo dono é exatamente o que as duas
   missões existem para impedir.**
2. Fazer merge de 151 commits de uma missão em curso tornaria esta entrega
   irrevisável, e resolveria conflitos em código que não é meu.
3. O buraco que a SR-01 mediu é um buraco **desta árvore**. Fechá-lo aqui é
   verificável; fechá-lo noutra não seria.

**O custo, declarado:** `coleta/coletor.py` vai conflitar quando as duas linhas
se encontrarem — 419 linhas de orçamento financeiro lá, a guarda aqui. Os dois
trabalhos são compatíveis em **conceito** (ver C, abaixo) e incompatíveis em
**texto**. Quem fizer o merge precisa de saber disto antes de começar, e é por
isso que está escrito aqui e não descoberto depois.

---

## B · TOPOLOGIA — O MAPA REAL DO DINHEIRO

`py provas/censo_das_portas_de_gasto.py` — segue o grafo de importações real,
não a menção textual, e varre **seis** primitivas de rede (curl, urllib,
requests, httpx, fetch, subprocess), não a palavra «apify».

```
FICHEIROS_VARRIDOS           264
COM_PRIMITIVA_DE_REDE         78
MENCIONAM_APIFY               52
PAID_CREATION_PRIMITIVES       1     ← coleta/coletor.py
PODEM_CRIAR_EXECUCAO_PAGA      6
MENCIONAM APIFY E NAO COMPRAM 47
```

### ⚠️ A SR-01 CONTOU 32, E O NÚMERO RESPONDIA A OUTRA PERGUNTA

A SR-01 escreveu «32 entrypoints que tocam Apify, e nenhum consulta o portão», e
usou esse número para baixar o próprio veredito a `PARTIAL`. A frase era
literalmente verdadeira e o número respondia a «quantos ficheiros mencionam a
plataforma e vão à rede». **Essa não é a pergunta do dinheiro.**

```
GET  /v2/acts/{ator}          lê o contrato do ator. Sem credencial. Zero dólares.
GET  /v2/actor-runs/{id}      lê o estado de uma execução que já existe.
GET  /v2/datasets/{id}/items  lê o que já foi colhido e já foi pago.
POST /v2/acts/{ator}/runs     ACENDE UMA EXECUÇÃO. E só isto custa.
```

    TOCAR NA APIFY NÃO É COMPRAR NA APIFY.

Medido: **47 dos 52** ficheiros que mencionam a plataforma só a lêem. O buraco
era real — nenhum dos que podiam comprar consultava a relevância — mas tinha
**5 portas, não 32**. A correção é minha e está aqui porque um número inflado
numa entrega anterior continua a ser um número errado.

E a medição independente confirma-a: o próprio `C10-8A-F-FINANCIAL-BUDGET.md`,
escrito no ramo do SCRAP sem conhecimento desta missão, mediu o mesmo:

```
POST /v2/acts/{ator}/runs     1 ocorrência em toda a casa
                              coleta/coletor.py :: executar
```

### Os workflows

| workflow | orquestrador | alcança criação paga |
|---|---|---|
| `apify-sensores.yml` | não | `regras/sensor_coleta.py` |
| `comunicacao-publica.yml` | **sim** | `coleta/comunicacao_coleta.py` |
| `sintonia-scrap.yml` | não | `coleta/instagram_coleta.py` |
| `system-map.yml` | não | `provas/testa_coleta_canonica.py` |
| `scrap-social.yml` | não | nenhuma (rotas sociais livres) |
| `apify-conexao.yml` | não | nenhuma (só censo de chaves) |

```
WORKFLOWS_PAID = 4 (dos 16 do repositório)
```

---

## C · OWNERS

| conceito | dono | mudou nesta missão? |
|---|---|---|
| `SOURCE_RELEVANCE` | `leis/relevancia_da_fonte.py` | **não** |
| `TOKEN_OWNER` | `ferramentas/apify_pool.py` | **não** |
| `PAID_EXECUTION_OWNER` | `coleta/coletor.py::executar` | ganhou a guarda |
| `PROVIDER_SIDE_CAP_OWNER` | `coleta/coletor.py` (`teto_usd → maxTotalChargeUsd`) | passou a ser **obrigatório** |
| `ROUTE_POLICY_OWNER` | `coleta/social_rotas.py` + `leis/social_matriz.py::MOTIVOS_PAGOS` | **não** |
| **`SPEND_GUARD_OWNER`** | **`leis/autorizacao_de_gasto.py`** | **novo** |

    SOURCE RELEVANCE OWNER != SPEND ENFORCER.
    TOKEN OWNER != SPEND OWNER.

O `apify_pool` continua a ser só o dono da chave: não importa
`relevancia_da_fonte`, não importa `autorizacao_de_gasto`, não decide nada. O
`coletor` não importa `relevancia_da_fonte` e não abre o livro — ele **confere**
uma autorização que outro emitiu. Há teste para as duas coisas.

---

## D · A CONTRADIÇÃO, RESOLVIDA PELO CÓDIGO

```
COLETOR_DECLARED_SINGLE_OWNER  = SIM   («a porta única por onde toda rota paga passa a entrar»)
COLETOR_OBSERVED_SINGLE_OWNER  = SIM   (1 POST de criação em 264 ficheiros)
APIFY_POOL_ROLE                = TOKEN_ROTATION_ONLY
PAID_OWNER_SPLIT               = NÃO
```

A declaração do `coletor.py` estava certa. O que estava errado era a leitura da
SR-01 — e a diferença entre as duas é a diferença entre contar menções e seguir
chamadas.

### E o transporte é trocável; a porta não

`regras/sensor_coleta.py:341` faz `coletor._curl = _curl_robusto` — substitui o
transporte inteiro por urllib, e o próprio ficheiro escreve *«a porta continua a
mesma; o transporte, não»*.

    UMA GUARDA NO `_curl` TERIA SIDO TROCADA JUNTO COM ELE.

Por isso a guarda vive em `executar()`, não no transporte. `RT-28` prova que o
sensor troca o transporte, mantém a porta e leva a autorização.

---

## E/F · AS PORTAS, ANTES E DEPOIS

| ficheiro que pode criar execução paga | antes | depois |
|---|---|---|
| `coleta/coletor.py` | compra com um token | exige autorização selada |
| `coleta/comunicacao_coleta.py` | compra com um token | transporta autorização, ou recusa |
| `coleta/instagram_coleta.py` | compra com um token | transporta autorização, ou recusa |
| `regras/sensor_coleta.py` | compra com um token | transporta autorização, ou recusa |
| `provas/testa_coleta_canonica.py` | alcança por import | recusa (sem autorização) |

```
PAID_ENTRYPOINTS_WITHOUT_AUTH   antes = 5     depois = 0
```

E a linha de comando não assina cheques: `RT-34` corre
`coletor.executar(...)` num subprocesso limpo e recebe
`SEM_AUTORIZACAO_NAO_GASTEI`, com `exit != 0`.

---

## G · COLETA NORMAL — A PROVA

Fornecedor fingido **só na fronteira externa**: um espião que conta POST e nunca
abre ligação. A guarda, o portão de relevância, o manifesto e a rotação são o
código real.

| caso | estado da relevância | POST que saíram |
|---|---|---|
| A · `SIM` no propósito certo | `SIM` | **1** |
| B · `NAO` | `NAO` | **0** |
| C · `NAO_SEI` | `NAO_SEI` | **0** |
| D · `ERRO` | `ERRO` | **0** |
| E · `NAO_AVALIADA` | `NAO_AVALIADA` | **0** |
| F · `SIM` em T3, pedido para T9 | `NAO_AVALIADA` em T9 | **0** |

E o caso F fecha nos dois sentidos: a **mesma** decisão compra para T3 e não
compra para T9. A relevância não vaza entre propósitos, e o dinheiro também não.

⚠️ **A recusa não julga a fonte.** `RT-36` exige que a mensagem de recusa **não**
contenha `NOT_RELEVANT` nem «irrelevante», e que carregue o estado real
(`NAO_SEI`, `ERRO`, `NAO_AVALIADA`).

    AUTHORIZATION_MISSING != NOT_RELEVANT.  UNKNOWN != NO.

E não se apresenta como falha da plataforma: a guarda corre **fora** do `try` que
monta o manifesto, porque deixá-la cair no `except` produziria uma corrida
`STATUS: FAILED` para uma execução que nunca existiu — e isso ler-se-ia como «a
Apify recusou», quando quem recusou fomos nós.

---

## H · SOURCE EVALUATION PROBE

```
SUPPORTED              SIM   (motivo PROVA_DE_RELEVANCIA_DA_FONTE)
REQUIRES_HUMAN_AUTH    SIM
MAX_RUNS               obrigatório  (sem ele: SEM_TETO_DE_EXECUCOES)
MAX_USD                obrigatório  (sem ele: SEM_TETO_DE_DOLARES)
STOP_CONDITION         obrigatória  (sem ela: SEM_CONDICAO_DE_PARAGEM)
AUTO_PROMOTES_RELEVANCE  NÃO
```

O probe existe para quebrar um ciclo que, sem ele, trancaria a casa:

```
para gastar é preciso ser relevante
  -> para provar que é relevante é preciso observar
    -> para observar é preciso gastar
```

Por isso ele **não** exige `SIM` — e, em troca, exige tudo o resto. `RT-14` prova
que atravessa com a fonte ainda `NAO_AVALIADA`; e o teste
`test_probe_nao_promove_a_fonte` prova que, depois de gastar, o livro continua
vazio.

    PROBE != RELEVANCE DECISION.

---

## I · CAPABILITY TRIAL

```
SUPPORTED              SIM   (motivo TRIAL_DE_CAPACIDADE)
REQUIRES_HUMAN_AUTH    SIM
USES_EXISTING_TRIAL    o vocabulário `TRIAL` já existe em leis/politica_da_coleta.py::ACOES
                       e em C10.7; o motivo aqui aponta para o mesmo conceito
AUTO_BECOMES_COLLECTION  NÃO
```

O TRIAL mede o **caminho**, não a fonte — por isso não nomeia fonte e não passa
pelo portão de relevância. E não se disfarça: `RT-18` e `RT-19` provam que uma
autorização de TRIAL não compra coleta normal, e que chamar-se TRIAL não dispensa
a autorização de TRIAL.

    TRIAL != COLLECTION.

---

## J · DINHEIRO REAL

```
APIFY_RUNS                 0
PROVIDER_START_POSTS_REAL  0
REAL_COST_USD              0
```

Nenhuma autorização de US$ 0,10 da C10.8B foi renovada. Todo o fornecedor é um
espião local que conta POST e não abre ligação.

---

## K · RED TEAM

```
ATAQUES = 37   MORTOS = 37   VIVOS = 0
```

Os 35 que a missão nomeou, mais dois que o desenho convidava:

```
RT-36  a recusa apresenta-se como fonte irrelevante
RT-37  a recusa apresenta-se como falha da plataforma
```

### Os três que sobreviveram à primeira volta, e o que ensinaram

| ataque | por que sobreviveu |
|---|---|
| `RT-02` | corria **sem token**. Sem chave, `apify_pool.pool()` volta vazio e o trabalho nunca é chamado: não se gastava porque não havia com quê, e a guarda nunca era exercida. **Não ter chave não é ter portão.** Reescrito com uma chave falsa no ambiente e o transporte espiado: `POSTS_QUE_SAIRAM=0`. |
| `RT-25` | procurava `def registar` no texto dos ficheiros — e **apanhou-se a si próprio**, porque a procura escreve a palavra que procura. Reescrito para medir comportamento: quem tem um `registar` que escreve no livro, e se o livro recusa uma linha fora do contrato. |
| `RT-27` | procurava o endereço de criação em texto, e apanhou três ficheiros que apenas o **nomeiam** — `medidas/portao.py` guarda-o como rótulo, e os dois donos descrevem-no nos cabeçalhos. Reescrito para usar o censo (endereço **e** método POST no mesmo ficheiro) e para contar POST reais. |

    PROCURAR UMA PALAVRA NUM FICHEIRO NÃO É MEDIR O QUE ELE FAZ.

É o mesmo defeito que a SR-01 já tinha apanhado no seu `RT-13`, cometido outra
vez e em três sítios. Fica escrito para que a terceira vez seja mais cara de
cometer.

---

## L · MUTATION

```
MUTANTES = 19   SURVIVORS = 0
```

### Os quatro que sobreviveram à primeira volta

**Dois eram mutantes mal escritos** — e um mutante que não muta mede a minha
distração, não a suíte:

```
M1  recibo = {} or ag.conferir_e_consumir(...)     `{}` é falso → avalia a chamada. NO-OP.
M5  autorizacao if not token else autorizacao      os dois ramos iguais. NO-OP.
```

**Dois eram buracos reais da suíte**, e os dois foram tapados com testes novos:

| mutante | o que a suíte não defendia |
|---|---|
| `M9` `autorizacao=None` no sensor | nenhum teste corria `sensor_coleta._rodar`. A suíte provava a guarda e provava a porta, e nunca o **caminho** entre as duas. |
| `M16` `proposito='QUALQUER'` no Instagram | nenhum teste corria `instagram_coleta._rodar`. Um adaptador que declarasse outro propósito compraria fora do autorizado, e a guarda só confere o que lhe dizem. |

    PROVAR A PORTA NÃO É PROVAR QUEM CHEGA A ELA.

---

## M · REGRESSÃO

| medição | falhas | passes | subtestes |
|---|---|---|---|
| ANTES · árvore limpa, sem este código | **22** | 2500 | 12689 |
| DEPOIS · mesma árvore limpa, com este código | **22** | 2542 | 12750 |

```
NEW_FAILURES       = 0
FALHAS QUE SUMIRAM = 0
```

Os dois conjuntos são **idênticos linha a linha**.

### ⚠️ A PRIMEIRA MEDIÇÃO DEU 28, E A CULPA ERA DA SUÍTE — A MINHA

`coletor.executar` grava o RAW por omissão (`salvar_raw=True`), e os testes dos
adaptadores não tinham por onde lhe passar outra coisa. Resultado: **seis
ficheiros falsos** em `data/samples/raw-paid/`, com nome de coleta de verdade, e
um artefato em `COMPETITOR-PUBLIC-COMM/`. Na corrida seguinte, **sete testes de
proveniência** sem relação nenhuma com esta missão reprovaram por causa deles.

    UMA SUÍTE QUE ESCREVE NA ÁRVORE MEDE A CORRIDA ANTERIOR, NÃO O CÓDIGO.

Conserto: a morada do RAW muda-se para uma pasta temporária durante a suíte (o
destino, não o contrato), o artefato de saída é desviado, e um `tearDown`
**reprova** se algum ficheiro novo ficar para trás. É a mesma armadilha que a
SR-01 documentou e que eu voltei a pisar — desta vez de dentro.

---

## N · SYSTEM MAP

Cadeia **lida** de `system-map/scripts/CADEIA-DO-MAPA.json` — 7 passos de
`REGERAR`, 1 de `VALIDAR`, não um número suposto — e corrida na ordem declarada.
Nenhum JSON gerado foi editado à mão.

```
SYSTEM_MAP_CHECK  = PASS   ·   21/21 regras
TESTES_SYSTEM_MAP = PASS
NODES = 167 · EDGES = 727
```

A peça nova, declarada em `architecture.declared.json`:

| id | território | kind | ficheiro |
|---|---|---|---|
| `C-AUTORIZACAO-DE-GASTO` | `Z-REGUAS` | `gate` | `leis/autorizacao_de_gasto.py` |

E as arestas, todas derivadas de `import` real e todas `PROVEN`:

```
C-RELEVANCIA-FONTE      -> C-AUTORIZACAO-DE-GASTO   a guarda pergunta ao dono da relevância
C-AUTORIZACAO-DE-GASTO  -> C-COLETA-BASE            a porta paga confere a autorização
```

⚠️ Não há aresta `C-AUTORIZACAO-DE-GASTO → C-APIFY-POOL`, e isso está certo: a
guarda **não toca na credencial**, e o dono da credencial não conhece a guarda.

A peça nasce **`PENDING`, não verde**: `P6_VERDE_TEM_PROVA` exige mais do que o
ficheiro existir.

### O validador fez o trabalho dele

A primeira volta da cadeia **reprovou**:

```
P9_CODIGO_DECLARADO: 3 ficheiro(s) de codigo que o mapa nao conhece
```

Foi por isso que a peça e as três provas foram declaradas. Fica registado em vez
de desaparecer atrás de um PASS final.

---

## O · O QUE FICA ABERTO, NOMEADO

1. **`MODULE CAN'T SPEND != FLOW IS CANONICAL`.** Três dos quatro workflows que
   alcançam criação paga continuam a chamar scripts diretamente, saltando o
   orquestrador — e com ele a admissão, a proveniência e o `RUN-MANIFEST`. Esta
   missão fechou o **dinheiro**, não a orquestração. O buraco arquitetural
   continua aberto e é de outra missão.

2. **O `coletor.py` desta árvore não tem o orçamento financeiro da C10.8A-F.**
   Ele vive no ramo do SCRAP. A guarda aqui exige `teto_usd` (a trava do lado do
   fornecedor) e um teto por autorização; não tem a contabilidade de exposição
   acumulada que a C10.8A-F construiu.

3. **Quem emite a primeira autorização, e por que via.** A guarda existe e é
   inevitável; nenhuma interface de linha de comando a emite ainda, de propósito
   — a linha de comando não assina cheques. Ligar um emissor a uma pessoa real é
   trabalho seguinte.

4. **As 77 fontes continuam sem decisão de relevância.** Esta missão não avaliou
   nenhuma, e por isso **nenhuma coleta normal paga consegue correr hoje**. Isso
   é a porta a funcionar, não a porta partida — mas quem esperar que a coleta
   paga corra amanhã precisa de saber que o passo em falta é humano.
