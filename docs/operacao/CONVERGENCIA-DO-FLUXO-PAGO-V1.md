# A CONVERGÊNCIA DO FLUXO PAGO — SCRAP-CV-02

> Uma linha tinha o fluxo. A outra tinha o dinheiro sob controlo. As duas
> passavam sozinhas.
>
> ```
> FLOW-01   REQUEST → ORQUESTRADOR → SCRAP → ROUTER → ADAPTER → PROVIDER
>           → RAW → ENVELOPE → INGRESSO → ADMISSÃO
> CV-01     quem autoriza · até quanto · quem conta as idas
> ```
>
> Esta missão pôs as duas na mesma linha técnica sem colapsar nenhuma.

---

## 1 · A BASE, ESCOLHIDA POR MEDIÇÃO

```
MERGE_BASE            532e3bed   (o HEAD da C10.8A-F, mãe das duas)
FLOW-01               84422284   18 commits além da base
CV-01                 130f5fae    1 commit além da base
```

A CV-01 é **um** commit; a FLOW-01 são dezoito, e trazem o orquestrador, o
`scrap_colheita`, o `retorno_da_coleta`, o ingresso, as receitas e o workflow.
Portar CV→FLOW move um delta; portar FLOW→CV moveria dezoito.

```
BASE_VERDICT = FLOW-01
```

E a FLOW-01 **já trazia** a guarda de autorização da SR-02, numa implementação
própria: `pode_comprar(modo, autorizacao, ...)`, com `NORMAL · PROBE · TRIAL` e
o veredito do portão de relevância a chegar de fora. Essa é a implementação que
fica. Não se trocou uma semântica por outra: acrescentaram-se-lhe as garantias
que a CV-01 tinha provado e esta não tinha.

    ONE CONCEPT → ONE OWNER. E O OWNER É O QUE JÁ ESTÁ LIGADO AO FLUXO.

---

## 2 · O QUE A BASE DEIXAVA PASSAR, MEDIDO ANTES DE MEXER

Nenhum destes números foi herdado. Todos foram reproduzidos nesta árvore, no
HEAD da FLOW-01, com fornecedor falso.

```
DEFECT_REPRODUCED              = YES
  autorização: MAX_PROVIDER_RUNS = 2 · MAX_USD = 1.00
  duas execuções, cada uma a declarar orçamento de 1.00
  EXPOSIÇÃO REPRESENTADA       = 2.00 sob um limite humano de 1.00

NORMAL_WITHOUT_LEDGER_POSTS    = 1     comprava sem ledger nenhum
AUTHORIZATION_COPY_ACCEPTED    = 1     um `deepcopy` comprava
ROTAÇÃO                        = 5 POSTs com MAX_PROVIDER_RUNS = 2
RESULT da compra não autorizada = UNKNOWN_ERROR
```

O último é o mais silencioso dos cinco. `SemAutorizacaoDeGasto` **já** era um
`RuntimeError` — a armadilha do `OSError` não existia aqui. Mas nem a rota nem o
executor a deixavam subir com nome, e ela caía no balde de «ninguém sabe o que
houve» para a única recusa que sabe exactamente o que houve.

E o fluxo canónico, esse, já corria:

```
CANONICAL_FLOW (baseline) = PASS
```

---

## 3 · O QUE FOI PORTADO, E SÓ ISSO

### 3.1 · A relação entre o limite humano e o ledger

```
FINANCIAL_BUDGET.AUTHORIZED  <=  AUTORIZACAO.MAX_USD
```

A guarda recebe um **número** — quanto esta execução declarou poder comprometer
ao todo — e compara. Nunca soma. Dar-lhe um ledger próprio criaria duas peças a
contar o mesmo dólar.

    LIMITE HUMANO != LEDGER OPERACIONAL.

E `MAX_USD` passou a ser obrigatório também em `NORMAL`, tal como
`MAX_PROVIDER_RUNS`. Uma coleta sem tecto é um cheque em branco, e o motivo do
gasto não muda isso.

### 3.2 · E o ledger tem de ser sempre o mesmo

Isto não estava no enunciado: apareceu quando o red team atacou.

```
autorização: MAX_PROVIDER_RUNS = 2 · MAX_USD = 1.00
DUAS execuções, cada uma a abrir o SEU orçamento de 1.00
cada compra custa 0.60  →  EXPOSIÇÃO TOTAL = 1.20
```

Cada orçamento sozinho cabia no limite humano. A soma não cabia. Conferir um
limite contra um ledger que muda a meio é o mesmo que não o conferir.

    UM LIMITE CONFERIDO CONTRA UM LEDGER QUE MUDA NÃO FOI CONFERIDO.

A saída **não** foi dar um saldo à lei. Ela guarda um **nome** — a identidade do
orçamento contra o qual o limite foi conferido da primeira vez — e recusa uma
segunda execução sob outro. Uma autorização vale dentro de UMA execução; para
outra, pede-se outra vez, que é o que uma pessoa entende por autorizar.

    UM NOME NÃO É UMA SOMA.

### 3.3 · Conferir não é consumir

```
1 · pode_comprar(...)           de graça, não queima nada
2 · orcamento.reservar(...)     compromete dinheiro, rebaixa o cap
3 · consumir(autorizacao)       a compra está comprometida
4 · POST /v2/acts/{ator}/runs   e lá dentro, o tecto de ACESSOS
```

    UM GATE BARATO CORRE PRIMEIRO, E NÃO QUEIMA NADA AO RECUSAR.
    POST QUE NÃO SAIU != POST QUE SAIU.

Quando o tecto de acessos recusa — o que acontece *dentro* do transporte, depois
do passo 3 — há prova de que nada foi comprado, e a unidade **volta**. Quando o
transporte cai **no meio** do POST, não há prova nenhuma, e ela não volta.

    AUSÊNCIA DE NOTÍCIA NÃO É PROVA DE AUSÊNCIA DE COMPRA.

### 3.4 · A autorização vale por identidade, não por forma

Era um `dict`. Um dicionário com as chaves certas é um formulário preenchido, e
uma cópia de uma autorização verdadeira é o mesmo formulário com melhor
caligrafia.

Ela continua a ser um `dict` por herança — quem a **lê** continua a lê-la. O que
muda é quem a **escreve**: só as instâncias que saíram de `conceder()` valem, e
o objecto fica selado contra escrita depois de concedido.

    UMA AUTORIZAÇÃO QUE O CHAMADOR ESCREVE É UM CAMPO DE FORMULÁRIO.
    COPIAR UMA AUTORIZAÇÃO NÃO É RECEBER UMA AUTORIZAÇÃO.
    UMA AUTORIZAÇÃO QUE MUDA DEPOIS DE CONFERIDA NÃO FOI CONFERIDA.

Medido: `copy.copy` e `copy.deepcopy` nem conseguem construir a cópia, porque
reconstroem o objecto escrevendo chave a chave num objecto já selado. As que se
conseguem construir morrem na porta, por não terem identidade.

### 3.5 · A recusa tem nome próprio

```
SPEND_NOT_AUTHORIZED  →  família BUDGET_EXHAUSTED  →  NO_RETRY
```

E as ausências da relevância mantêm cada uma o seu nome
(`SOURCE_NOT_RELEVANT_FOR_PURPOSE`, `SOURCE_RELEVANCE_NOT_EVALUATED`,
`SOURCE_RELEVANCE_UNKNOWN`, `SOURCE_RELEVANCE_EVALUATION_ERROR`), porque dizer
`NOT_RELEVANT` a uma fonte que ninguém abriu é inventar um julgamento.

`social_rotas` deixa passar as **três** recusas em vez de duas; `scrap_executor`
dá-lhe nome no rasto, com e sem ledger instalado.

    SALDO ESGOTADO != NINGUÉM AUTORIZOU.
    UMA RECUSA QUE PEDE PARA SER REPETIDA NÃO É UMA RECUSA.

### 3.6 · O transporte alternativo

`regras/sensor_coleta.py` troca `coletor._curl` no corpo do módulo. Nesta linha
a troca **já** pedia autorização ao dono da rede e **já** enviava o POST uma vez
só — a SR-02 tinha consertado isso aqui. O que faltava era mais estreito: uma
prova que finge o `subprocess` deixa de fingir coisa nenhuma quando o transporte
é `urllib`, e a promessa `NETWORK_REAL = 0` passava a depender de ninguém ter
importado aquele ficheiro primeiro.

    UM FAKE QUE JÁ NÃO ESTÁ NO CAMINHO NÃO É UM FAKE. É UM ADORNO.

`coletor._CURL_DA_CASA` já existia e é o que resolve isso; os harnesses repõem a
porta antes de medir, e a suite da convergência activa a troca de propósito —
com `reload`, não com um `import` que não volta a correr — e mede com ela viva.

---

## 4 · O QUE ESTAVA VERMELHO NA BASE E NÃO ERA DESTA MISSÃO

Duas provas do controlo de gasto já não corriam no HEAD da FLOW-01, e a razão é
a mesma: a guarda chegou àquela linha e estes ficheiros continuaram a chamar a
porta paga sem trazer autorização nenhuma.

```
provas/orcamento_financeiro.py    IndexError — nenhum POST chegava a sair
provas/primeira_rota_paga.py      IndexError — idem
```

    DUAS LINHAS PARCIALMENTE CORRECTAS NÃO SÃO UM FLUXO.

Ficaram verdes. E, ao arrumá-las, apareceram duas afirmações que a própria
linhagem tinha tornado falsas e ninguém actualizara:

- a reserva financeira chama-se `MISSAO`, e a prova pedia `MOTIVO_PAGO`;
- `apify:transcricao` passou a `PARTIAL` depois da corrida real, e a prova ainda
  exigia `POSSIBLE_NOT_PROVED`.

---

## 5 · A MUDANÇA DE COMPORTAMENTO, DECLARADA

Sem ledger, não se compra.

```
ANTES   modo NORMAL sem orçamento declarado → o POST saía, sem
        maxTotalChargeUsd nenhum.
DEPOIS  modo NORMAL sem orçamento declarado → zero POST,
        RESULT = SPEND_NOT_AUTHORIZED.
```

Duas sentinelas afirmavam o contrário e foram **reescritas com a razão ao
lado**, não apagadas:

- `tests/test_c10_8af_orcamento_financeiro.py::test_28_em_NORMAL_sem_ledger_ja_nao_se_compra`
- `provas/orcamento_financeiro.py` — «sem ledger nenhum, não se compra»

---

## 6 · OS DONOS, DEPOIS DA CONVERGÊNCIA

```
FLUXO CANÓNICO      orquestrador/orquestrador.py → coleta/scrap_colheita.py
SPEND_AUTHORIZATION leis/autorizacao_de_gasto.py
FINANCIAL_BUDGET    coleta/coletor.py :: OrcamentoFinanceiro
NETWORK_BUDGET      coleta/scrap_http.py
PAID_EXECUTION      coleta/coletor.py :: executar
SOURCE_RELEVANCE    leis/relevancia_da_fonte.py   (noutra linhagem; aqui só se
                                                   recebe o veredito dele)
```

A guarda não expõe `OrcamentoFinanceiro`, `Reserva`, `reservar`, `liquidar`,
`desconhecer` nem `anular`, e não importa `coletor`, `apify_pool` nem
`scrap_http`. Ela conta **execuções**, nunca dólares. O executor e a rota
importam **o tipo** da recusa, e nada mais.

---

## 7 · O QUE NÃO FOI FEITO, E NÃO FOI DE PROPÓSITO

- Nenhum fornecedor pago executado, nenhuma corrida Apify, nenhum cêntimo.
- A C10.8B não correu.
- As 77 fontes não foram reavaliadas.
- Nenhum outro workflow foi migrado para o orquestrador.
- A Bíblia não foi tocada.
- Nenhum merge repo-wide entre as duas linhagens.
- `COL-LAW-505` não foi reaberta: nada nesta convergência esbarrou nela.

```
REAL_NETWORK = 0 · APIFY_REAL_RUNS = 0 · PAID_REAL_RUNS = 0 · REAL_COST_USD = 0
```
