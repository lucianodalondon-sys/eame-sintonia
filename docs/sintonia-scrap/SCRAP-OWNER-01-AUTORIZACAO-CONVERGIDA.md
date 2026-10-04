# SCRAP-OWNER-01 — UMA AUTORIZAÇÃO DE GASTO, UM DONO, UM CONTRATO

`SCRAP_SPEND_AUTH_CONVERGENCE = PASS`

> Duas linhagens escreveram, cada uma por si, a mesma lei — e as duas
> chamavam-se `v1`.
>
> ```
> DUAS IMPLEMENTAÇÕES DO MESMO CONTRATO
> NÃO SÃO DUAS VERSÕES DA VERDADE: SÃO DUAS VERDADES.
> ```

---

## 1 · O DEFEITO NÃO ERA O CÓDIGO DIFERENTE. ERA O NOME IGUAL

```
FLOW  leis/autorizacao_de_gasto.py   9dc6ece2   20.572 bytes   AUTORIZACAO_DE_GASTO/v1
SR02  leis/autorizacao_de_gasto.py   8b3ae924   18.236 bytes   AUTORIZACAO_DE_GASTO/v1
```

Mesmo input, respostas opostas:

| entrada | FLOW | SR-02 |
|---|---|---|
| dicionário escrito à mão pelo chamador | **aceite** | recusado |
| autorização de 1 execução, usada 2 vezes | as duas passam | a 2ª recusada |
| `teto_usd` ausente com `max_usd` definido | passa | recusado |

```
ARE_CURRENT_V1S_BEHAVIORALLY_COMPATIBLE = NO
```

Um manifesto com `CONTRATO: …/v1` deixava de identificar o que o produziu.

---

## 2 · QUEM VENCEU, E POR PROPRIEDADES

| propriedade | FLOW | SR-02 | canônico |
|---|---|---|---|
| objeto | dict validado | dataclass selada | **selada** |
| não fabricável | não | sim | **sim** |
| consumível | não | sim | **sim** |
| teto do fornecedor conferido | não | sim | **sim** |
| liga fonte · propósito · motivo | 2 de 3 | 3 de 3 | **3 de 3** |
| pergunta ao dono da relevância | não (só valida recibo) | sim | **sim** |
| eixo do MODO (`NORMAL/TRIAL/PROBE`) | sim | não | **sim** |

Quatro propriedades num lado, zero exclusivas no outro. O único contributo do
modelo perdedor — o eixo do modo — foi preservado.

```
QUANDO UM DOS DOIS É UM SUPERCONJUNTO,
CONVERGIR NÃO É NEGOCIAR: É ESCOLHER E MIGRAR.
```

**Fase 7:** escolheu-se a **forma B** — o dono do gasto **chama**
`relevancia_da_fonte.portao()` ao conceder. A forma A (validar um recibo
entregue) é precisamente o que não consegue ser não-fabricável.

---

## 3 · O CONTRATO SUBIU PARA v2, POR MEDIÇÃO

`v1` já nomeava dois comportamentos. Mantê-lo criaria um terceiro.

```
CONTRATO                    AUTORIZACAO_DE_GASTO/v2
CONTRATO_AMBIGUO_ANTERIOR   AUTORIZACAO_DE_GASTO/v1   (escrito, para os manifestos antigos)
```

---

## 4 · DOIS EIXOS, UMA TRADUÇÃO

```
MODO     NORMAL · TRIAL · PROBE                    a EXECUÇÃO — vale também para rotas grátis
MOTIVO   COLETA_NORMAL_DA_FONTE ·
         PROVA_DE_RELEVANCIA_DA_FONTE ·
         TRIAL_DE_CAPACIDADE                       o GASTO — só existe quando há dinheiro
```

Correspondem um a um e **não** se fundiram: uma coleta normal de rota gratuita
tem modo e não tem motivo de gasto.

```
UMA ROTA QUE NÃO GASTA NÃO PRECISA DE AUTORIZAÇÃO PARA GASTAR.
```

`MOTIVO_DO_MODO` é o único sítio onde um vira o outro.

---

## 5 · O CENSO DOS CONSUMIDORES

| consumidor | antes | depois |
|---|---|---|
| `coleta/coletor.py` | `pode_comprar` (valida) | `conferir_e_consumir` (consome) |
| `coleta/social_scrap.py` | tabela com a autorização | tabela com o **pedido** |
| `coleta/adaptador_youtube.py` | passa dict | passa objeto + cap |
| `regras/sensor_coleta.py` | não comprava | transporta, e a rotação não cunha |
| `coleta/instagram_coleta.py` | não comprava | transporta |
| `coleta/comunicacao_coleta.py` | não comprava | transporta |

Os três que a SR-02 tinha deixado sem poder comprar passam a transportar a
autorização — **sem a fabricar**.

---

## 6 · O QUE FOI PORTADO, E COMO

`leis/relevancia_da_fonte.py`, **byte a byte**:

```
sha portado = sha na origem = f71788d022a924c6e0f4294499d9d43b04e73a62
```

Duas cópias da mesma lei são duas leis, e a segunda aprende a responder o que a
primeira recusa. `FULL_SR01_MERGE = NO` — 155 commits só numa linha, 68 só na
outra, merge-base `00a6aa35`.

---

## 7 · MEDIDO

```
SPEND_AUTH_OWNER_COUNT       2  →  1
PAID_CREATION_PRIMITIVES     1     (intacto)
CAN_SPEND_WITHOUT_AUTH       0     (intacto)
FREE_ROUTE_REQUIRES_SPEND_AUTH     NO

NÃO FABRICÁVEL   dict · sósia · JSON round-trip  →  AUTORIZACAO_FABRICADA
CONSUMÍVEL       1 autorização · POST 1 passa · POST 2 AUTORIZACAO_ESGOTADA
ROTAÇÃO          não cunha: o saldo vai com a autorização

RED_TEAM 65 · MUTANTS 24 · SURVIVORS 0
BASE 2.704 testes · 20 falhas   →   FINAL 2.721 · 18 falhas   NEW_FAILURES 0
SCRAP_FLOW_01 = PASS · SCRAP_SR_02 = PASS

REAL_NETWORK 0 · APIFY_RUNS 0 · PAID_START_POSTS 0 · COST_USD 0
```

---

## 8 · O QUE A MUTAÇÃO ENSINOU

Cinco de vinte e quatro sobreviveram à primeira volta, e nenhum acusava o
código.

```
UM MUTANTE QUE SOBREVIVE ACUSA A BATERIA, NÃO O CÓDIGO.
```

O mais fino: havia uma sentinela a provar que a **lei** recusa um dicionário. O
mutante punha o ramo permissivo na **porta**, e sobrevivia inteiro.

```
MEDIR A LEI NÃO É MEDIR QUEM A CHAMA.
```

---

## 9 · O QUE NÃO MUDOU

Uma só primitiva de criação paga. A guarda continua antes da reserva financeira
e antes do POST. Os dois tetos, a política de rota, o RAW antes da
normalização, o COL-LAW-505 e o fluxo canônico da SCRAP-FLOW-01 — todos
intactos. Intelligence e Portal não foram tocados.

---

## 10 · RISCO RESTANTE

O `LIVRO-DE-RELEVANCIA` está **vazio** nesta linhagem. Toda a coleta normal
falha fechada, e é a verdade: ninguém avaliou nenhuma fonte aqui. `PROBE` e
`TRIAL` continuam a poder gastar, com autorização humana e tetos.

A outra linhagem continua a existir com o seu próprio ficheiro. Esta missão
convergiu **uma** linha; unificar os ramos é outra decisão, e não foi tomada
aqui.
