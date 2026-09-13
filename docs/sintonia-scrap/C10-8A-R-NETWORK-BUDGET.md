# C10.8A-R — O TETO DE ACESSOS EXTERNOS

`C10_8AR_NETWORK_BUDGET = PASS`

> A C10.8A declarou `MAX_REAL_HTTP_REQUESTS = 2` e fez sete. O teto existia —
> numa variável de um script de prova. Quando a sonda rebentou e foi preciso
> repetir, o teto repetiu-se com ela, zerado.
>
> ```
> UM TETO QUE VIVE NA PROVA MEDE A PROVA.
> DECLARED BUDGET != ENFORCED BUDGET.
> ```

---

## 1 · A CORREÇÃO DO VEREDITO, SEM APAGAR NADA

```
C10_8A_OLD_VERDICT        PASS_PROVEN
C10_8A_CORRECTED_VERDICT  FAIL
CAPABILITY_VERDICT        bluesky.author.incremental = PROVEN
REQUESTS_ACTUALLY_MADE    7 de capacidade + 1 de diagnóstico
```

O §11 daquele documento sempre contou as sete idas. Contá-las e continuar a
chamar-lhe `PASS` é outra coisa:

```
UMA MISSÃO QUE MEDE O PRÓPRIO EXCESSO E SE DÁ PASS
TRANSFORMOU O GATE NUM COMENTÁRIO.
```

A capacidade **não** foi rebaixada, e isso não é indulgência. Houve rede real,
`HTTP 200`, objeto real, RAW com SHA lido de volta e reprocessamento offline. O
que falhou foi o protocolo da missão, não o objeto capturado.

```
MISSÃO FALHOU O PROTOCOLO != CAPACIDADE NÃO FOI PROVADA.
```

---

## 2 · O CENSO QUE DECIDIU ONDE O TETO TEM DE VIVER

A tentação era contar em `scrap_http.buscar` — o transporte nomeado da casa. O
censo mediu por onde as catorze capacidades ligadas saem de verdade:

| porta | capacidades | passa por `scrap_http`? |
|---|---|---|
| `scrap_http.buscar` | 5 (bluesky ×2, mastodon ×2, telegram) | sim |
| `reel_transcricao.baixar` | 3 (os Reels) | **não** |
| `cdp.abas` / `cdp._handshake` | 1 (a janela) | **não** |
| `youtube_oficial._http` | 5 (YouTube) | **não** |

Vinte e cinco funções da casa abrem ligação directamente.

```
UM TETO QUE COBRE METADE DAS PORTAS NÃO É UM TETO. É UMA SUGESTÃO.
```

O único ponto que **todas** atravessam são as duas primitivas do Python:
`urllib.request.urlopen` e `socket.create_connection`.

```
NETWORK_BUDGET_OWNER = coleta/scrap_http.py
WHY = é o dono do conceito «rede» nesta casa — e o ponto de COBRANÇA é onde a
      ligação abre. As duas coisas não precisam de ser a mesma linha.
```

---

## 3 · O CONTRATO

```python
with http.orcamento_de_rede(2) as orcamento:
    ...
# ou, pelo caminho canônico:
sx.COLLECT(..., teto_de_rede=2)
```

```
LIMIT          quantos acessos esta execução pode fazer
USED           quantos já fez
REMAINING      quantos sobram
EXHAUSTED      não sobra nenhum
REFUSED        quantos foram recusados pelo teto
ATTEMPTS       cada tentativa: TYPE · TARGET · COUNTED · OUTCOME
PER_EXECUTION  sim — `threading.local`, reposto ao sair do bloco
```

Sem `teto_de_rede`, nada muda: produção continua exactamente como estava, e o
rasto não inventa um teto que ninguém pediu.

---

## 4 · O QUE CONTA

```
ROBOTS      conta    GRÁTIS EM DÓLAR != GRÁTIS EM REQUESTS
ROUTE       conta
RETRY       conta
FALLBACK    conta
DIAGNOSTIC  conta    ← foi este o passo que a C10.8A deu por fora do teto
UNCLASSIFIED conta   UM PEDIDO QUE NINGUÉM CLASSIFICOU NÃO É UM QUE NÃO ACONTECEU
```

E um pedido que falhou conta: o 404, o 500 e o timeout gastaram a ida.

O que **não** conta: ler ficheiro local, reprocessar o RAW, o `CHECK`, o
`CAPABILITIES`, a consulta ao registo e à política.

### A retentativa, medida antes de ser afirmada

Não há ciclo de retentativa nenhum no SCRAP. `leis/falhas.py` diz se retentar
**adianta** (`RECOVERY_ACTION = WAIT`) e ninguém no caminho de aquisição age
sobre isso.

```
UMA POLÍTICA QUE NINGUÉM EXECUTA NÃO É UM COMPORTAMENTO.
```

Então o que se prova é o **contrato**: uma retentativa dentro da execução gasta
pedido como qualquer outra e, com o teto esgotado, morre antes do socket. Quando
alguém escrever o ciclo, os dois têm de dizer sim:

```
RETRY_ALLOWED_BY_FAILURE_POLICY  «adianta?»
NETWORK_BUDGET_REMAINING > 0     «cabe?»
```

---

## 5 · A MATRIZ, MEDIDA CONTRA UM CONTADOR INDEPENDENTE

O transporte falso entra **por baixo** do teto e conta o que realmente saiu.

```
UM TETO QUE SE MEDE A SI PRÓPRIO MEDE O ESPELHO.
```

| caso | teto | saíram | objetos |
|---|---|---|---|
| A · limite 0 | 0 | **0** | 0 |
| B · limite 1 | 1 | **1** (só o portão) | 0 |
| C · limite 2 | 2 | **2** | 1 |
| D · limite 2, timeout | 2 | **2** | 0 |
| E · limite 3, timeout | 3 | **2** | 0 |
| F · limite 2, HTTP 500 | 2 | **2** | 0 |
| G · reprocessar RAW | 2 | **0** | 1 |

Multi-host: com teto 2, dois hosts gastam o teto e o terceiro não é tocado. O
teto é da execução, não de cada host.

---

## 6 · O GATE VEM ANTES DA REDE

```
NETWORK_CALL_N_PLUS_1 = 0
```

A tentativa recusada fica no rasto como tentativa, com `COUNTED = False` e
`OUTCOME = REFUSED_BY_BUDGET`. Recusar em silêncio faria a execução parecer que
nunca quis sair.

---

## 7 · O DEFEITO QUE O PRÓPRIO TETO REVELOU

`scrap_http.buscar` tinha um `except Exception` que traduzia tudo para
`RotaBloqueada` — «a plataforma nos impediu». A recusa do teto caía lá dentro.

```
ESGOTAR O ORÇAMENTO NÃO É A PLATAFORMA IMPEDIR.
```

É a **segunda vez** nesta cadeia que um `except` largo veste uma recusa nossa
com a roupa da fonte: na C10.8A, um túnel caído saiu como `ROUTE_NOT_ALLOWED`.
A recusa do teto passa agora por cima do `except`, inteira, e chega ao executor
como `NETWORK_BUDGET_EXHAUSTED`.

```
UM `except Exception` LARGO NÃO DISTINGUE QUEM DISSE NÃO.
```

---

## 8 · OS DOIS EIXOS NÃO SE MISTURAM

```
PAID BUDGET != NETWORK BUDGET.
```

Uma chamada gratuita gasta um pedido e zero dólares. `permitir_pago=True` com
motivo canônico **não** aumenta o teto de rede — medido. E a classe do
orçamento não conhece a palavra `USD`, `custo`, `permitir_pago` nem
`motivo_pago`.

A C10.8B precisará dos dois tetos, e eles continuam a ser dois.

---

## 9 · O HARNESS DA C10.8A USA O CONTRATO REAL

`provas/bluesky_trial_ao_vivo.py` passou a declarar `teto_de_rede=MAX_PEDIDOS`
ao `COLLECT`. O contador local sobrou como **conferente independente**: a prova
compara o número do runtime com o que o transporte viu.

Corrido inteiro a seco, contra o RAW preservado, com o socket trancado de fora:
zero idas à rede, `BLUESKY_TRIAL=PASS`.

---

## 10 · O VOCABULÁRIO DA PRESERVAÇÃO

Três factos, e só o terceiro é o que o contrato forward mede:

```
SCRAP_RAW_CAPTURED              YES
SCRAP_RAW_READ_BACK             YES
CANONICAL_FORWARD_PRESERVATION  NO   (NOT_PRESERVED)
```

Chamar as três de «RAW preservado» seria dizer que o arquivo está guardado
porque o ficheiro existe na máquina de quem o trouxe. O dono forward
(Supabase Storage + `raw_asset`) não foi chamado, e é de outra frente.

---

## 11 · MEDIDO

```
ATTACKS 28 · POSITIVE_FINDINGS 0 · fugas de rede no red team = 0
MUTANTS 12 · SURVIVORS 0
NETWORK_REAL 0 · PAID_RUNS 0 · COST_USD 0
```

## 12 · O QUE NÃO MUDOU

Bluesky continua `PROVEN` com a prova a apontar para o artefato ao vivo. A
política, o registo, os adaptadores e a taxonomia de falha estão intocados. Sem
`teto_de_rede`, o comportamento de produção é bit a bit o de antes. Nada fora do
SCRAP foi tocado.

## 13 · O QUE CONTINUA DESCONHECIDO

- O comportamento sob retentativa real, porque não existe ciclo de retentativa.
- O teto financeiro, que é o outro eixo e é da C10.8B.
- Se algum caminho futuro abrir ligação por uma primitiva que não seja
  `urlopen` nem `create_connection` — hoje as vinte e cinco portas usam uma das
  duas, e um caminho novo que não use precisa de ser medido.
