# SCRAP-SR-02 — NENHUMA COMPRA SEM AUTORIZAÇÃO

`SCRAP_PAID_SPEND_ENFORCEMENT = PASS`

> Havia quatro portões à volta da porta paga, e todos funcionavam. Nenhum
> respondia à pergunta anterior a todos eles.
>
> ```
> CAN_SPEND_WITHOUT_AUTH   4  →  0
> APIFY_RUNS = 0 · START_POSTS = 0 · PAID_USD = 0
> ```

---

## 1 · O QUE FALTAVA NÃO ERA UM TETO

| portão | responde |
|---|---|
| teto financeiro | quanto cabe? |
| teto de rede | quantas idas restam? |
| política da rota | este caminho é permitido? |
| cap do provider | no máximo quanto, do lado de lá? |

```
ALGUÉM AUTORIZOU ESTA COMPRA?
```

Nenhum dos quatro. Um sistema que sabe exactamente quanto pode gastar sem saber
se devia gastar gasta com precisão contabilística em coisas que ninguém pediu.

```
CREDENTIAL_PRESENT != SPEND_AUTHORIZED
ROUTE_ALLOWED      != SPEND_AUTHORIZED
BUDGET_PRESENT     != SPEND_AUTHORIZED
TOKEN_OWNER        != SPEND_OWNER
```

---

## 2 · A INTEGRAÇÃO NÃO FOI UM MERGE

As duas linhas divergiram: `merge-base 00a6aa35`, **151** commits só no SCRAP,
**67** só na SR-01, 160 ficheiros e 86.844 inserções de diferença. Um merge
cego traria a Collection inteira para dentro de uma missão de gasto.

```
FULL_SR01_MERGE = NO
```

O que se portou foi **o contrato, e não o motor**: os nomes canónicos que o
`portao()` da SR-01 devolve — `VEREDITO`, `SOURCE_ID`, `PROPOSITO`,
`ESTADO_DA_RELEVANCIA`, `VERSAO_DO_PORTAO`, `CONTRATO` — e a conferência de
`COL-LAW-206` (uma URL não é um `SOURCE_ID`). Zero linhas de classificação.

```
SOURCE_RELEVANCE_OWNER = leis/relevancia_da_fonte.py   (SR-01, fora desta linhagem)
ITEM_RELEVANCE_OWNER   = admissao/admissao.py
SPEND_GUARD_OWNER      = leis/autorizacao_de_gasto.py  (novo)
```

```
O GUARDA CONFERE O BILHETE. ELE NÃO É O DONO DO ESPECTÁCULO.
```

### E o guarda não refaz a tabela do portão

A tentação era ler `RESULTADO` e reaplicar `REGRA_DO_PORTAO`. Seria a mesma lei
escrita duas vezes, e a cópia daria respostas antigas no dia em que o original
mudasse. Fez-se o oposto:

```
EXIGE-SE A ÚNICA COMBINAÇÃO SEM LEITURA DUPLA:
VEREDITO = AUTORIZA  E  ESTADO_DA_RELEVANCIA = SIM.
```

Qualquer outra recusa — inclusive uma que uma versão futura do portão viesse a
autorizar. Quando um contrato atravessa uma fronteira de propriedade, o lado que
obedece deve ser mais estreito que o lado que decide.

---

## 3 · O CENSO, MEDIDO OUTRA VEZ

A SR-01 tinha reportado 40 entrypoints de rede e 32 a tocar Apify. Medido agora,
por **chamada** e não por import:

```
NETWORK_ENTRYPOINTS           124   (ficheiros .py que abrem rede ou subprocesso)
TOCAM_APIFY                    14
PAID_CREATION_PRIMITIVES        1   coleta/coletor.py::executar — o POST
CALLERS_PRODUTIVOS              4
PAID_WORKFLOWS                  4
```

Os números diferem dos da SR-01 porque a pergunta é outra: aquela contou quem
fala com a Apify, esta conta quem **cria execução paga**. Ler corridas não
compra.

```
COLETOR_IS_ACTUAL_SINGLE_PAID_OWNER = YES
APIFY_POOL_IS_PAID_EXECUTION_OWNER  = NO   (token, pool, rotação, redacção)
PAID_OWNER_SPLIT                    = NO   para a criação
                                    = YES  para a orquestração
```

| chamador | passa autorização |
|---|---|
| `coleta/adaptador_youtube.py:428` | SIM |
| `regras/sensor_coleta.py:545` | NÃO |
| `coleta/comunicacao_coleta.py:679` | NÃO |
| `coleta/instagram_coleta.py:285` | NÃO |

Os três últimos **deixaram de conseguir comprar**, e é o objetivo da missão.
Não estão partidos: estão à espera de que alguém diga para que fonte e que
propósito cada um compra, e essa resposta vive no livro da SR-01.

---

## 4 · A GUARDA VIVE NA PRIMITIVA

Pô-la no roteador guardaria o caminho canónico — e três dos quatro chamadores
não passam por lá.

```
UMA GUARDA QUE VIVE NUM CAMINHO GUARDA UM CAMINHO.
UMA GUARDA QUE VIVE NA PRIMITIVA GUARDA TODOS.
```

Ela corre em `coletor.executar`, **antes** da reserva financeira e antes do
POST. Reservar primeiro comprometeria dinheiro por uma compra impensável, e uma
reserva que ninguém liquidou não volta ao bolso. O parâmetro nasce `None`:

```
FAIL CLOSED. O SILÊNCIO NÃO AUTORIZA.
```

---

## 5 · TRÊS MODOS, COM UM DONO SÓ

```
NORMAL   colher a sério            exige SOURCE_RELEVANCE = SIM para o PAR
PROBE    «esta candidata merece?»  arranca de NAO_AVALIADA, com limites finitos
TRIAL    «esta ROTA consegue?»     mede a rota, não a fonte
```

O PROBE existe para não fechar o ciclo impossível:

```
PARA PROVAR QUE A FONTE SERVE É PRECISO OBSERVÁ-LA,
E PARA A OBSERVAR SERIA PRECISO ELA JÁ SERVIR.
```

O preço de escapar ao portão é ser finito em tudo: `MAX_PROVIDER_RUNS`,
`MAX_START_POSTS`, `MAX_USD`, `MAX_ITEMS`, teto de rede, e uma autorização
humana escrita. Um limite em falta é um limite infinito; zero não é «sem teto»,
é «não pode».

```
PROBE != DECISION. Quem escreve no livro é o dono do livro.
```

As três palavras do eixo mudaram de `coleta/scrap_executor.py` para a lei, e a
razão é de propriedade: o modo diz **que prova é precisa antes de comprar**.

---

## 6 · NORMAL COLLECTION — OITO CASOS, PELO CAMINHO REAL

Só o `subprocess.run` dentro do `coletor` é falso. A guarda, os dois tetos, o
roteador, o adaptador e o registo são os verdadeiros.

| caso | POSTs | estado |
|---|---|---|
| SIM · fonte A · T3 | **1** | `EXECUTOU` |
| SIM T3 usado em T9 | 0 | `AUTHORIZATION_FOR_ANOTHER_PURPOSE` |
| NAO | 0 | `SOURCE_NOT_RELEVANT_FOR_PURPOSE` |
| NAO_SEI | 0 | `SOURCE_RELEVANCE_UNKNOWN` |
| ERRO | 0 | `SOURCE_RELEVANCE_EVALUATION_ERROR` |
| NAO_AVALIADA | 0 | `SOURCE_RELEVANCE_NOT_EVALUATED` |
| autorização fonte A, compra fonte B | 0 | `AUTHORIZATION_FOR_ANOTHER_SOURCE` |
| URL no lugar de `SOURCE_ID` | 0 | `URL_IS_NOT_A_SOURCE_ID` |
| sem autorização nenhuma | 0 | `SPEND_NOT_AUTHORIZED` |

Quatro ausências, quatro nomes. Achatá-las em `NOT_RELEVANT` inventaria um
julgamento que ninguém fez.

```
FALTA DE AUTORIZAÇÃO É FALTA DE AUTORIZAÇÃO.
```

---

## 7 · O ACHADO QUE NÃO ESTAVA NO GUIÃO

`regras/sensor_coleta.py` substitui `coletor._curl` **no import**. A troca é
legítima: o proxy deste ambiente derruba conexões, e urllib sobrevive onde o
subprocesso não sobrevive.

O que ela levava consigo não era. Duas leis moravam dentro do `_curl` antigo:

```
o teto de rede        a reserva por ida vivia lá
o POST vai UMA vez    porque repetir um POST é comprar de novo
```

A versão trocada não reservava nada e repetia **quatro vezes, qualquer método**
— incluindo o POST que cria a execução paga. Até quatro execuções por chamada,
órfãs, sem `run_id` e a gastar. Bastava `import sensor_coleta` em qualquer ponto
do processo para as duas leis desaparecerem da porta paga, para toda a gente.

```
UMA TROCA DE TRANSPORTE LEVA COM ELA AS LEIS QUE MORAVAM NO TRANSPORTE.
REPETIR UM GET É BARATO. REPETIR UM POST É COMPRAR DE NOVO.
```

E o `maxTotalChargeUsd` não cobria o buraco: ele limita **cada** execução, nunca
a soma das execuções que ninguém sabe que existem.

As duas voltaram, e `coletor._CURL_DA_CASA` passou a guardar o transporte
original com nome, para que a troca deixe de ser invisível. Três sentinelas
novas reprovam qualquer substituto que não cumpra as duas leis.

---

## 8 · MEDIDO

```
SCRAP_BASE_HEAD              e90451e187cf7680f8df733cfc77e07bb4605def
SR01_HEAD                    bf07e43387a415500975dea6731f3ec973735b0b
MERGE_BASE                   00a6aa35b4a8770a3d48c143e6aa0a47354102a1
COMMITS_ONLY_SCRAP           151
COMMITS_ONLY_SR01            67
FULL_SR01_MERGE              NO

BEFORE_CAN_SPEND_WITHOUT_AUTH   4
AFTER_CAN_SPEND_WITHOUT_AUTH    0

RED_TEAM_ATTACKS             48    SURVIVORS 0
MUTANTS                      23    SURVIVORS 0
TESTS_BEFORE   2.624 · FAILURES_BEFORE 21
TESTS_AFTER    2.673 · FAILURES_AFTER  18   NEW_FAILURES 0

APIFY_RUNS = 0 · OTHER_PAID_RUNS = 0 · START_POSTS = 0 · COST_USD = 0
```

---

## 9 · O QUE NÃO MUDOU

Os dois tetos da C10.8, o `maxTotalChargeUsd`, o POST único, a exposição
`UNKNOWN`, a adopção do POST ambíguo, a ausência de retentativa paga automática,
o RAW antes da normalização, o trace do provider e a transferência de evidência
da C10.8B-R — todos intactos. A autorização fica **antes** deles e não substitui
nenhum.

A rota `apify:transcricao` continua `PARTIAL`. Collection, Admission,
Intelligence e Portal não foram tocados.

```
BIBLE_CHANGE_REQUIRED_FROM_SR01 = YES
BIBLE_CHANGED_IN_THIS_MISSION   = NO
```

---

## 10 · RISCO RESTANTE

Três chamadores produtivos não compram até alguém lhes dar fonte e propósito.
Enquanto isso, `sensor_coleta`, `comunicacao_coleta` e `instagram_coleta` estão
parados na parte paga — e essa é a forma correcta de estarem.

E a distinção que fica escrita para não se perder:

```
SPEND ENFORCEMENT resolvido != CANONICAL ORCHESTRATION resolvida.
MODULE CAN'T SPEND != FLOW IS CANONICAL.
```

Nenhum módulo consegue comprar sem atravessar a guarda. Isso **não** quer dizer
que o fluxo seja canónico: quatro workflows continuam a correr scripts directos,
e convergi-los para o orquestrador é outra missão.
