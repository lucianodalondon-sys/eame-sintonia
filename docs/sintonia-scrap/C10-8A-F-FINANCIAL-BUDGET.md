# C10.8A-F — O TETO DE GASTO

`C10_8AF_FINANCIAL_BUDGET = PASS`

> A C10.8A-R fechou o primeiro teto: quantos **acessos** uma execução pode fazer.
> Este fecha o segundo, e ele mede outra coisa.
>
> ```
> REQUEST COUNT != MONEY.
>
> NETWORK BUDGET   decide SE CABE MAIS UMA IDA.
> FINANCIAL BUDGET decide SE PODEMOS ASSUMIR MAIS EXPOSIÇÃO FINANCEIRA.
> ```

---

## 1 · O CENSO QUE DECIDIU O DONO

A C10.8A-R ensinou a não escolher o dono pelo organograma. O censo desta missão
mediu **quem pode comprometer dinheiro**, e a resposta é diferente da de lá:

```
POST /v2/acts/{ator}/runs        1 ocorrência em toda a casa
                                 coleta/coletor.py :: executar
GET  /v2/acts/{ator}             ferramentas/contrato_ator.py — sem credencial,
                                 leitura de metadados, zero dólares
```

Trinta e cinco capacidades declaradas; **três** têm rota paga por omissão
(`instagram.post.comments`, `x.discovery`, `youtube.native_caption`) e **zero**
têm adaptador. Hoje, pelo SCRAP, a rota paga não é alcançável.

```
COST_CONCEPT_OWNER      = coleta/coletor.py
FINANCIAL_BUDGET_OWNER  = coleta/coletor.py
CHARGING_POINT          = o POST que cria a execução, dentro de coletor.executar
ACTUAL_COST_SOURCE      = usageTotalUsd, da própria Apify
PROVIDER_SIDE_CAP_OWNER = coletor.executar (teto_usd → maxTotalChargeUsd)
```

Na C10.8A-R o dono do conceito e o ponto de cobrança tinham de ser ficheiros
diferentes, porque a rede tem 25 portas. Aqui são o mesmo ficheiro — e isso é
uma **medição**, não uma comodidade:

```
ONE CONCEPT → ONE OWNER. QUANDO HÁ UMA SÓ PORTA, O DONO ESTÁ NELA.
```

---

## 2 · COMO ERA ANTES

```
permitir_pago   social_rotas   «pode usar rota paga?»
motivo_pago     social_rotas   «por quê?» — vocabulário fechado
teto_usd        coletor        → maxTotalChargeUsd, POR EXECUÇÃO DA APIFY
COST_USD        coletor        ← usageTotalUsd, rotulado NOT_SETTLED
COST_USD        social_rotas   inicializado a 0.0 e nunca escrito
```

Três coisas que o antes não tinha:

**Um teto da execução.** `maxTotalChargeUsd` limita **cada** corrida da Apify,
nunca a soma delas. `instagram_coleta.py` declara `TETO = {bio 0.05 · posts 0.20
· reels 0.10 · comentarios 0.15}` **por fase e por conta**: cem contas são
US$50,00 de exposição máxima sem que nenhum número acima de 0,20 apareça em
lado nenhum.

```
PROVIDER CAP != EXECUTION BUDGET.
```

**Duas das três portas pagas não mandam trava nenhuma.**
`regras/sensor_coleta.py` e `coleta/comunicacao_coleta.py` chamam
`coletor.executar` **sem `teto_usd`** — e o primeiro roda um ciclo sobre as
chaves do pool, acendendo uma execução paga por posição.

```
PAID ROUTE WITHOUT FINANCIAL LIMIT = ALLOWED_BY_CURRENT_CONTRACT
```

**Um eixo de conhecimento do custo.** O roteador escrevia `COST_USD: 0.0` no
registo e nunca mais lhe tocava. Zero era a resposta para «não correu», para
«correu e foi de graça» e para «correu, era paga, e ninguém leu quanto custou».

---

## 3 · O CONTRATO

```python
with ct.orcamento_financeiro(1.00) as orcamento:
    ...
# ou, pelo caminho canônico:
sx.COLLECT(..., teto_de_gasto=1.00, teto_de_rede=3)
```

Sete conceitos, e eles não se misturam:

```
AUTHORIZED   FINANCIAL_BUDGET_AUTHORIZED_USD   o que esta execução pode comprometer
COMMITTED    FINANCIAL_BUDGET_COMMITTED_USD    reservado por chamadas em curso
ACTUAL       FINANCIAL_BUDGET_ACTUAL_USD       o que as terminadas custaram (lido)
UNKNOWN      FINANCIAL_BUDGET_UNKNOWN_USD      reservado e nunca esclarecido
REMAINING    FINANCIAL_BUDGET_REMAINING_USD    AUTHORIZED − (ACTUAL+COMMITTED+UNKNOWN)
EXHAUSTED    FINANCIAL_BUDGET_EXHAUSTED        não resta nada
REFUSED      FINANCIAL_CALLS_REFUSED           recusadas antes do provider
PER_EXECUTION                                  sim — threading.local, morre no bloco
```

E cada tentativa: `PROVIDER · ACTOR · ROUTE · MOTIVO_PAGO · PROVIDER_SIDE_CAP ·
OUTCOME · COST_STATE · ACTUAL_COST_USD`.

O dinheiro vive em **micro-dólares inteiros** por dentro: cem reservas de
US$0,01 fecham exactamente em US$1,00, e um teto que erra na sexta casa decimal
é um teto que às vezes deixa passar.

Sem `teto_de_gasto`, nada muda — nem o `maxTotalChargeUsd` enviado, nem o
manifesto, nem o rasto, que não inventa campos de um teto que ninguém pediu.

---

## 4 · O CAP DO PROVIDER CABE NO QUE RESTA

```
LIMIT = 1.00
call A  cap enviado 1.00 · actual 0.25
REMAINING = 0.75
call B  cap enviado 0.75   ← e não 1.00
```

O `teto_usd` que o chamador pede é **rebaixado** ao saldo, nunca elevado. Um
chamador que peça US$5,00 com US$0,30 de saldo manda US$0,30. E um chamador que
não peça nada recebe o saldo inteiro como trava: uma chamada paga sem cap do
lado do provider é exposição sem fim, e um orçamento declarado não permite isso.

```
PROVIDER CAP <= EXECUTION REMAINING.
```

---

## 5 · A MATRIZ, MEDIDA CONTRA O QUE SAIU DE VERDADE

O provider falso substitui `subprocess.run` **dentro** do coletor — por baixo
dos dois tetos. Trocar `_curl` inteiro poria o falso **acima** do gate de rede,
e um teto que o falso contorna nunca seria medido.

```
UM FAKE ACIMA DO GATE MEDE O FAKE.
```

| caso | teto | POSTs | resultado |
|---|---|---|---|
| F0 · limite 0 | 0 | **0** | `FINANCIAL_BUDGET_EXHAUSTED` |
| F1 · uma chamada | 1.00 | 1 | actual 0.25 · remaining 0.75 |
| F2 · segunda chamada | 1.00 | 2 | caps 1.00 e **0.75** |
| F3 · exaustão | 0.30 | **1** | a segunda morre antes do provider |
| F4 · POST perdido | 1.00 | 1 | `UNKNOWN` 1.00 · remaining **0.00** |
| F4b · órfã adotada | 1.00 | 1 | actual **0.12** · unknown 0.00 |
| F5 · provider fura o cap | 1.00 | 1 | `PROVIDER_EXCEEDED_CAP` · excesso 0.35 |
| F6 · rota gratuita | 0 | 0 | colheu · `FREE_ROUTE_BY_POLICY` |
| F7 · reprocessar | 0 | 0 | objetos · rede 0 · gasto 0 |

**Multi-call:** US$0,40 + US$0,30 numa execução dão ACTUAL 0,70 e REMAINING
0,30. O saldo não reinicia entre chamadas.

**Execuções independentes:** teto 1,00 e teto 2,00 correm sem se tocarem, e fora
do bloco não há orçamento nenhum.

---

## 6 · O POST QUE TALVEZ TENHA NASCIDO

`PostTalvezCriado` já existia: o POST não é retentado, porque repetir um POST é
comprar de novo. O que faltava era o que o **dinheiro** faz nesse estado.

```
ACTUAL_COST = UNKNOWN
```

E `UNKNOWN` **não devolve o saldo**. A reserva sai de `COMMITTED` e entra em
`UNKNOWN`, onde fica. Devolvê-la deixaria a execução seguinte gastar outra vez
aquilo que talvez já tenha saído.

```
UNKNOWN COST != ZERO COST.
POTENTIAL COMMITMENT != NOTHING HAPPENED.
```

Há **dois** casos, e só dois, em que o dinheiro volta inteiro — e os dois têm
prova, não ausência de notícia:

- a API respondeu `{"error": ...}` **sem criar execução**;
- o teto de **rede** recusou o pedido, e o POST provadamente não saiu.

Quando a execução órfã é adotada (o comportamento que já existia), o custo passa
a ser legível e a reserva liquida-se com o número real.

---

## 7 · OS TRÊS ESTADOS DO CUSTO NÃO COLAPSAM

```
NOT_RUN            o provider nunca foi chamado
UNKNOWN            foi chamado e não se leu quanto custou
READ_NOT_SETTLED   leu-se `usageTotalUsd` — e a Apify ainda não fechou a conta
SETTLED            reconciliado. Não acontece aqui: acontece em corrigir_custo.py
```

Todo trace nasce em `NOT_RUN`; quem correu sobrescreve. Uma rota **gratuita** que
correu diz `FREE_ROUTE_BY_POLICY` com `ACTUAL_COST_USD = 0.0` — zero por
política é um facto, não um palpite. Uma rota **paga** que correu e não declarou
custo diz `UNKNOWN`, que é o caso perigoso, nunca zero.

E `ACTUAL` nesta casa quer dizer «o que se conseguiu **ler**». Esta casa já
anunciou US$0,90 e pagou US$5,04 por publicar o número lido como se fosse o
final.

```
READ COST != SETTLED COST.
```

---

## 8 · OS DOIS GATES SÃO DOIS

| NETWORK | FINANCIAL | provider | estado |
|---|---|---|---|
| 2 | 0 | **não chamado** | `FINANCIAL_BUDGET_EXHAUSTED` |
| 0 | 1.00 | **não chamado** | `NETWORK_BUDGET_EXHAUSTED` |
| 2 | 1.00 | chamado | `OK` |
| 0 | 0 | **não chamado** | `FINANCIAL_BUDGET_EXHAUSTED` |

A ordem é **financeiro primeiro**: uma chamada recusada pelo dinheiro não gasta
acesso nenhum. E `permitir_pago` continua a não responder «até quanto»:

```
PAID_ROUTE_AUTHORIZATION != FINANCIAL_BUDGET.
```

Sem `permitir_pago`, um teto declarado não autoriza nada. Com `permitir_pago` e
motivo fora do vocabulário canônico, um teto declarado também não salva.

### O defeito que a segunda linha da tabela revelou

O primeiro resultado desta matriz foi `NETWORK = 0 · FINANCIAL = 1.00 → provider
CHAMADO`. O teto de rede da C10.8A-R cobra em `urllib.request.urlopen` e
`socket.create_connection` — e a porta paga **não passa por nenhuma das duas**:
ela lança um processo `curl`.

```
UM TETO COBRADO NA PRIMITIVA NÃO VÊ QUEM SAI POR UM SUBPROCESSO.
```

O censo das 25 portas da C10.8A-R contou funções de Python que abrem ligação, e
por isso não viu esta. `coletor._curl` passou a pedir autorização ao dono da
rede antes de cada `subprocess.run` — o dono do conceito continua a ser
`scrap_http`; este ficheiro não conta nada, pede.

---

## 9 · UM ENSAIO PAGO SEM TETO NÃO COMEÇA

```
modo=TRIAL + rota paga por omissão + sem teto de gasto declarado
    → PAID_TRIAL_WITHOUT_FINANCIAL_BUDGET, antes de qualquer rede
```

Em `NORMAL` nada muda: os caminhos históricos continuam exactamente como
estavam, e quebrá-los em silêncio seria trocar um buraco por outro. Mas um
`TRIAL` é a primeira vez que uma capacidade paga corre, e uma primeira vez sem
teto é um default infinito.

```
NO FINANCIAL LIMIT → NO PAID TRIAL.
```

---

## 10 · A RECUSA CHEGA COM NOME PRÓPRIO

`leis/falhas.py` já tinha `BUDGET_EXHAUSTED` — «teto NOSSO, a fonte não tem nada
a ver com isso», com recuperação `NO_RETRY`. Os dois tetos entram lá como
alias, em vez de nascer um estado novo:

```
FINANCIAL_BUDGET_EXHAUSTED           → BUDGET_EXHAUSTED
NETWORK_BUDGET_EXHAUSTED             → BUDGET_EXHAUSTED   (faltava; caía em UNKNOWN_ERROR)
PAID_TRIAL_WITHOUT_FINANCIAL_BUDGET  → BUDGET_EXHAUSTED
```

E a recusa atravessa inteira o `except Exception` de `executar` — a **terceira**
vez nesta cadeia em que um `except` largo vestia uma recusa nossa com a roupa da
fonte. Sem isso, o manifesto diria `STATUS: FAILED` sobre uma Apify que nunca
foi chamada.

```
UM `except Exception` LARGO NÃO DISTINGUE QUEM DISSE NÃO.
```

---

## 11 · A CONCORRÊNCIA FOI MEDIDA, NÃO PRESUMIDA

Nenhuma das quatro portas pagas arranca execução concorrente: medido na árvore
(`Thread`, `ThreadPoolExecutor`, `Pool`, `Process`, `gather`, `create_task`), e
não na prosa — a primeira versão desta sonda procurava as palavras no ficheiro e
encontrou o comentário que dizia que elas não estavam lá.

```
IMPORTAR `threading` NÃO É CORRER EM PARALELO.
UMA SONDA QUE PROCURA A PALAVRA ENCONTRA A FRASE QUE DIZ QUE ELA NÃO EXISTE.
```

Segurança medida, e não presumida: a reserva é atómica. Quatro fios a pedir
US$0,80 de um teto de US$1,00 comprometem **exactamente** US$1,00 — o segundo
não é recusado, é **rebaixado** ao que resta. Não há lock distribuído, porque
não há nada distribuído.

```
COMMITTED <= AUTHORIZED, sob corrida real.
```

---

## 12 · MEDIDO

```
ATTACKS 30 · POSITIVE_FINDINGS 0
MUTANTS 16 · SURVIVORS 0
NETWORK_REAL 0 · APIFY_RUNS 0 · PAID_RUNS 0 · REAL_COST_USD 0
```

---

## 13 · O PACOTE DE DECISÃO HUMANA

### O que a casa já pagou, medido nos manifestos

```
80 execuções com custo numérico · US$ 12,33 · 4.982 itens · US$ 2,475 / 1.000
```

| ator | n | soma | pior corrida | itens | USD/1.000 |
|---|---|---|---|---|---|
| `streamers~youtube-comments-scraper` | 10 | 7,728 | **1,928** | 3.737 | 2,068 |
| `streamers~youtube-scraper` | 29 | 4,472 | 0,400 | 1.173 | 3,812 |
| `pintostudio~youtube-transcript-scraper` | 29 | 0,130 | **0,010** | 28 | 4,643 |
| `harvestapi~linkedin-profile-search-by-name` | 12 | 0,000 | 0,000 | 44 | 0,000 |

E a cicatriz da liquidação: **US$0,90 anunciados, US$5,04 pagos** — um fator de
5,6 entre o valor lido e o valor fechado.

### As três candidatas da C10.8B não têm o mesmo preço

```
youtube.native_caption   apify:transcricao   análogo medido: 29 corridas, pior 0,010
instagram.post.comments  apify:comments      análogo medido: 10 corridas, pior 1,928
x.discovery              OFFICIAL_API_PAID   ZERO histórico de custo nesta casa
```

Um número só para as três seria um palpite com cara de medida.

```
C10_8B_MAX_PROVIDER_CALLS = 1
    uma capacidade, um alvo, sem paginação, sem segundo perfil — a forma da
    C10.8A, que é a única forma de trial que esta casa já correu.

RECOMMENDED_C10_8B_MAX_USD

    youtube.native_caption    US$ 0,10
        pior corrida medida do análogo 0,010 · × 5,6 da liquidação = 0,056
        · margem até 0,10, que é 10× a pior corrida medida

    instagram.post.comments   UNKNOWN_NEEDS_MEASUREMENT
        o custo depende de quantos comentários voltam, e o trial teria de
        declarar um teto de itens antes de haver número. Com teto de 100
        comentários e os US$ 2,068/1.000 do análogo: 0,207 · × 5,6 = 1,16.

    x.discovery               UNKNOWN_NEEDS_MEASUREMENT
        zero corridas pagas desta rota nesta casa. Não há de onde tirar número.
```

A recomendação desta missão é começar por **`youtube.native_caption`**: é a
única das três cujo análogo tem 29 corridas medidas e pior caso abaixo de um
cêntimo.

```
AUTHORIZED_C10_8B_MAX_USD     = NOT_AUTHORIZED
READY_FOR_HUMAN_BUDGET_DECISION = YES
READY_TO_EXECUTE_C10_8B       = NO
```

Recomendação não é autorização. A C10.8B só começa depois de instrução humana
explícita com o valor.

---

## 14 · O QUE NÃO MUDOU

Bluesky continua `PROVEN`. A C10.8A continua com o veredito corrigido para
`FAIL` e as sete idas escritas. A matriz, o registo, os adaptadores e o teto de
rede da C10.8A-R estão intocados no que fazem. Sem `teto_de_gasto`, o
comportamento de produção é o de antes. Nenhuma rota paga ganhou adaptador, e
nada fora do SCRAP foi tocado.

## 15 · O QUE CONTINUA DESCONHECIDO

- O comportamento sob **retentativa real**: não existe ciclo de retentativa no
  SCRAP, e por isso o que se prova é o contrato — cada tentativa futura gasta
  acesso e tem de caber no dinheiro. `RETRY_BEHAVIOR_PROVEN = NO`.
- O custo **liquidado** de qualquer corrida desta missão: não houve corrida.
- O custo de `x.discovery`, que nunca correu.
- `leis/retorno_da_coleta.py` **não existe** nesta linha; `COL-LAW-505` vive em
  documentos e em `coleta/ingresso.py`. O orçamento financeiro não lhe toca.
