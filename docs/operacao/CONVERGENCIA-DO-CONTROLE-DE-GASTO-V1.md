# A CONVERGÊNCIA DO CONTROLE DE GASTO — SCRAP-CV-01

> Duas leis nasceram em branches diferentes, cada uma provada sozinha, e as duas
> falavam do mesmo dólar.
>
> ```
> SR-02      QUEM · POR QUÊ · PARA QUÊ pode gastar
> C10.8A-F   ATÉ QUANTO esta execução pode gastar
> ```
>
> Esta missão pôs as duas na mesma linha técnica sem colapsar nenhuma.

---

## 0 · O QUE ESTE DOCUMENTO NÃO É

Não é um relatório de status e não substitui a Bíblia. É o registro do que a
convergência mediu, do que ela mudou, e do que ela **encontrou por acidente** —
que foi a parte mais cara.

---

## 1 · AS SEIS DISTINÇÕES QUE TINHAM DE SOBREVIVER

```
CREDENTIAL            != AUTHORIZATION
ROUTE_ALLOWED         != SPEND_AUTHORIZED
SPEND_AUTHORIZED      != FINANCIAL_BUDGET
FINANCIAL_BUDGET      != NETWORK_BUDGET
SOURCE_RELEVANCE      != SPEND_AUTHORIZATION
PROVIDER_CAP          != EXECUTION_BUDGET
```

Todas sobreviveram, e cada uma tem prova executável. A convergência **acrescentou
uma sétima**, que não estava no enunciado e que a medição obrigou a escrever:

```
SALDO ESGOTADO != NINGUÉM AUTORIZOU
```

---

## 2 · A ORDEM DOS PORTÕES, E POR QUE É ESTA

```
    coletor.executar(...)
        │
        ├── 1 · ag.conferir(autorizacao, ...)          ← de graça, não queima nada
        │        · a autorização existe, não foi fabricada e cobre ESTA compra
        │        · FINANCIAL_BUDGET.AUTHORIZED <= AUTORIZACAO.max_usd
        │
        ├── 2 · orcamento.reservar(pedido=teto_usd)    ← compromete dinheiro
        │        · PROVIDER_CAP <= EXECUTION_REMAINING  (o teto é REBAIXADO)
        │
        ├── 3 · ag.consumir(autorizacao)               ← a compra ficou comprometida
        │
        └── 4 · POST /v2/acts/{ator}/runs
                 └── dentro do transporte: o teto de ACESSOS, de scrap_http
```

**Um gate barato corre primeiro e não queima nada ao recusar.** Foi por isso que
`conferir()` e `consumir()` são duas funções e não uma: na SR-02 a unidade era
gasta na conferência, que corre antes do dinheiro — uma corrida barrada por falta
de saldo queimava uma execução autorizada para uma compra que nunca aconteceu.

    POST QUE NÃO SAIU != POST QUE SAIU.

E vale nos dois sentidos: quando o teto de **acessos** recusa — o que acontece
*dentro* do transporte, depois do passo 3 — há prova de que nada foi comprado, e
a execução autorizada **volta** (`ag.devolver`). Essa linha nasceu de um ataque
vivo do red team, e não de uma revisão de código.

---

## 3 · O DEFEITO QUE FOI REPRODUZIDO ANTES DE SER CORRIGIDO

```
autorização: max_execucoes = 2 · max_usd = 1.00
duas chamadas com teto_usd = 1.00 cada

chamada 1 · teto aceite = 1.00 · veredito = AUTORIZADO
chamada 2 · teto aceite = 1.00 · veredito = AUTORIZADO

AUTORIZACAO.max_usd           = 1.00   (limite humano)
EXECUÇÕES AUTORIZADAS         = 2
EXPOSIÇÃO MÁXIMA REPRESENTADA = 2.00
DEFEITO = SIM
```

A autorização conferia o teto de **cada** chamada contra `max_usd` e só
decrementava o número de execuções. Um limite humano de um dólar autorizava dois.

    CADA POST GANHAVA O LIMITE INTEIRO OUTRA VEZ.

**O conserto não foi dar um ledger à autorização.** Contar dólares gastos,
reservados e desconhecidos é trabalho do `OrcamentoFinanceiro`, e duas peças a
somar o mesmo dinheiro divergem na terceira chamada. O que a lei passou a exigir
é a **relação**:

```
FINANCIAL_BUDGET.AUTHORIZED  <=  AUTORIZACAO.max_usd
```

A guarda recebe um **número** e compara. Nunca sabe quanto já se gastou, quanto
está reservado, nem quanto resta.

A reprodução do defeito **não foi apagada**: vive em
`tests/test_cv01_convergencia.py::ODefeitoDoMaxUsd`.

---

## 4 · A MUDANÇA DE COMPORTAMENTO, DECLARADA

Sem ledger, não se compra.

```
ANTES (C10.8A-F isolada)   modo NORMAL sem orçamento declarado → o POST saía,
                           sem maxTotalChargeUsd nenhum.
DEPOIS (CV-01)             modo NORMAL sem orçamento declarado → zero POST,
                           RESULT = SPEND_NOT_AUTHORIZED.
```

A posição antiga era coerente com a C10.8A-F sozinha: aquela missão instalava um
teto, não fechava a porta a quem não instalasse nenhum. Depois de a SR-02 trazer
o limite humano, ela deixou de ser sustentável — é exatamente o buraco da §3.

    SEM_LEDGER_NÃO_GASTEI.

As duas sentinelas que afirmavam o contrário foram **reescritas com a razão
escrita ao lado**, não apagadas:

- `tests/test_c10_8af_orcamento_financeiro.py::test_28_em_NORMAL_sem_ledger_ja_nao_se_compra`
- `provas/orcamento_financeiro.py` — «sem ledger nenhum, não se compra»

---

## 5 · OS TRÊS ACHADOS QUE A CONVERGÊNCIA ENCONTROU SEM PROCURAR

### 5.1 · A recusa de gasto pedia para ser repetida

`GastoRecusado` herdava de `PermissionError`, que herda de `OSError`. A casa
inteira tem `except OSError` a apanhar túnel caído. Medido: uma compra recusada
por falta de autorização subia pelo executor como `TRANSIENT_NETWORK_ERROR`, cuja
recuperação canônica é `WAIT`.

    UMA RECUSA QUE PEDE PARA SER REPETIDA NÃO É UMA RECUSA.

E era pior do que ler mal no rastro: quem lê `WAIT` chama outra vez, e a segunda
chamada é uma compra.

**Consertado.** `GastoRecusado(RuntimeError)`, como as suas duas irmãs. Estado
canônico próprio `SPEND_NOT_AUTHORIZED`, família `BUDGET_EXHAUSTED`, recuperação
`NO_RETRY`. `social_rotas` deixa passar as **três** recusas em vez de duas.

### 5.2 · Um import reescrevia a porta paga para o processo inteiro

`regras/sensor_coleta.py` faz `coletor._curl = _curl_robusto` **no corpo do
módulo**. Quem importar aquele ficheiro — um teste, um censo, um import
transitivo — troca o transporte da única porta paga desta casa, sem o pedir.

    UM IMPORT QUE REESCREVE A PORTA PAGA É UMA DECISÃO QUE NINGUÉM TOMOU.

Medido na suite completa: com o transporte trocado, uma prova que finge o
`subprocess` deixa de fingir coisa nenhuma — o pedido sai por `urllib` e vai
**mesmo** à rede. A promessa `NETWORK_REAL = 0` de três harnesses desta casa
dependia de ninguém importar aquele ficheiro primeiro.

**Mitigado, não removido.** `coletor._CURL_ORIGINAL` guarda a porta original, e
os três harnesses repõem-na antes de medir. A troca em si continua a existir: a
sua razão (o subprocesso `curl` perdia stdout no runner) continua válida, e
desfazê-la é outra missão.

### 5.3 · O transporte trocado comprava até quatro vezes

Esta é a mais cara das três.

`coletor._curl` deixou de repetir POST em 2026-09-02, com a razão escrita: se o
pedido **chegou** e só a resposta se perdeu, repetir não repete um pedido
perdido — acende uma segunda execução paga, e a primeira fica órfã a gastar.

A substituição do sensor ficou com o comportamento anterior: **até 4 tentativas,
para qualquer método.** O mesmo POST, pela mesma porta, até 4 compras. E
`maxTotalChargeUsd` não protege disto — ele limita cada execução, nunca a soma
das execuções que ninguém sabe que existem.

    REPETIR UM GET É BARATO. REPETIR UM POST É COMPRAR DE NOVO.

**Consertado.** O transporte substituto agora: (a) pede autorização ao dono da
rede antes de cada ida, como a porta original; (b) envia o POST **uma** vez e
levanta `PostTalvezCriado`.

---

## 6 · O QUE FOI MEDIDO, E NÃO HERDADO

```
PAID_CREATION_PRIMITIVES        = 1      coleta/coletor.py :: executar
WORKFLOWS_TOTAL                 = 18
WORKFLOWS_PAID                  = 5
WORKFLOWS_BYPASS_ORCHESTRATOR   = 4
CHAMAM coletor.executar DIRECTAMENTE = 6
```

«Bypass» aqui não quer dizer «não importa o orquestrador»: quer dizer **chama a
porta paga pelo próprio pé**, e com isso passa ao lado do `scrap_executor.COLLECT`
— e ao lado do teto de rede, do teto de gasto e do checkpoint que ele instala.

**Esta missão não migrou nenhum workflow.** A medição fica escrita para quem
migrar.

---

## 7 · OS DONOS, DEPOIS DA CONVERGÊNCIA

```
SOURCE_RELEVANCE        leis/relevancia_da_fonte.py
SPEND_AUTHORIZATION     leis/autorizacao_de_gasto.py
FINANCIAL_BUDGET        coleta/coletor.py :: OrcamentoFinanceiro
NETWORK_BUDGET          coleta/scrap_http.py
PAID_EXECUTION          coleta/coletor.py :: executar
```

E nenhum deles conhece o outro mais do que precisa:

- `coletor` **não** importa `relevancia_da_fonte` e não abre o livro;
- `autorizacao_de_gasto` **não** expõe `OrcamentoFinanceiro`, `Reserva`,
  `reservar`, `liquidar`, `desconhecer` nem `anular` — ela conta **execuções**,
  nunca dólares;
- `relevancia_da_fonte` não conhece token, pool nem dinheiro;
- `apify_pool` não decide nada dos três;
- `scrap_executor` e `social_rotas` importam **o tipo** da recusa, e nada mais.

---

## 8 · AS PROVAS

```
tests/test_cv01_convergencia.py          a suite da convergência
provas/red_team_da_convergencia.py       35 ataques nomeados
provas/mutacao_da_convergencia.py        os mutantes das duas leis e do transporte
tests/test_c10_8af_orcamento_financeiro.py   as sentinelas do teto de gasto
provas/orcamento_financeiro.py           a prova do teto, ponta a ponta
```

Em todas: o fornecedor é falso **só na fronteira externa** — o espião substitui
`subprocess.run`, o processo `curl` que sai da máquina, e mais nada. Ficam reais e
por cima dele `_curl`, o teto de rede, o orçamento financeiro, `executar`, a
guarda e o portão de relevância.

    SE O FAKE FICAR ACIMA DE UM OWNER, A PROVA É INVÁLIDA.
    UM FAKE QUE JÁ NÃO ESTÁ NO CAMINHO NÃO É UM FAKE. É UM ADORNO.

```
NETWORK_REAL = 0 · APIFY_REAL_RUNS = 0 · PAID_REAL_RUNS = 0 · REAL_COST_USD = 0
```

---

## 9 · O QUE FICA POR FAZER, E ESTÁ POR FAZER DE PROPÓSITO

- **Migrar os quatro workflows** que chamam a porta paga pelo próprio pé para o
  orquestrador. Medido aqui, fora do escopo desta missão.
- **Desfazer a troca de transporte do sensor** em vez de a mitigar. A razão
  original dela continua válida; a forma (reescrever a porta de todos no corpo de
  um import) é que não.
- **Reavaliar as 77 fontes** contra o portão de relevância. Nenhuma foi avaliada
  nesta missão, e `NAO_AVALIADA` continua a ser o estado honesto delas.
- **A emenda à Bíblia** que a D-041 já nomeou. Não se mexe na Bíblia aqui.
