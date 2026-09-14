# BASELINE DA ADMISSION DE HOJE — T3 · PRAGA E DOENÇA

> **Isto mede. Não conserta.** Nenhum falso positivo foi corrigido, nenhuma
> palavra foi tocada, nenhum substituto foi proposto.
>
> ```
> CLASSIFIER_BUILT = NO · ADMISSION_CHANGED = NO · KEYWORDS_CHANGED = NO
> REPLACEMENT_PROPOSED = NO
> ```
>
> **Missão:** `C-MEDE-ADMISSION-ATUAL-CONTRA-GABARITO-T3-V1`
> **Artefatos:** `provas/medir_admission_t3_atual.py` ·
> `data/derivados/BASELINE-ADMISSION-T3-V1.json`

---

## 1 · O DONO REAL, PROVADO ELO A ELO

Não basta «o módulo existe». Cada elo abaixo é lido no ficheiro, e um elo que
desapareça derruba a medição.

```
admissao/admissao.py:319   PERGUNTAS_DO_UNIVERSO   a lista de palavras
admissao/admissao.py:241   _do_universo            decide o tema
admissao/admissao.py:345   decidir                 prontidão primeiro, tema depois
orquestrador/orquestrador.py:228        corre a porta sobre a colheita
coleta/rota_forward_documento.py:206    corre a porta no documento
coleta/ingresso.py:143     para_a_porta            o único tradutor de nomes
```

```
CURRENT_THEMATIC_OWNER_FILE      admissao/admissao.py
CURRENT_THEMATIC_OWNER_FUNCTION  _do_universo (via decidir)
CURRENT_T3_RULE_LOCATION         PERGUNTAS_DO_UNIVERSO['T3']
THEMATIC_DECISION_OWNERS         1
PRODUCTION_MECHANISM_CALLABLE    YES
ADMISSION_RULE_VERSION           3
```

Não há mecanismo temático concorrente. Os outros `classificar()` desta árvore
decidem estado de falha, identidade de locutor e tipo de comunicação — eixos
diferentes, nenhum atribui universo.

**A prova não copiou a porta.** Ela chama `admissao.decidir` — a mesma função
que o orquestrador executa — e captura o que vier.

```
COPIED_KEYWORD_IMPLEMENTATION = NO
THIN_ADAPTER_HAS_SEMANTIC_LOGIC = NO
PRODUCTION_WIRING_MUTATION = CAUGHT
```

A ligação foi provada partindo a porta de propósito, três vezes, e exigindo que
a previsão mudasse. Nenhuma mutação ficou commitada.

---

## 2 · OS DOIS PLANOS DE ENTRADA, E POR QUE SÃO DOIS

A porta pergunta **prontidão** antes de tema, e isso é lei (`COL-LAW-042`: «as
que apuram se dá para olhar vêm primeiro, porque não se julga o que não se
leu»).

O registo de artefatos desta árvore diz `SOURCE_ID = "NAO SEI"` nos 30 textos
derivados, e `coleta/ingresso.py` é explícito sobre o que isso vale:

```
A CONFISSÃO DE IGNORÂNCIA NÃO É UM VALOR.
```

Então o item chega à porta sem origem, e a porta para antes do tema. Medir só
isso responderia a pergunta errada. A regra de qual plano é a baseline foi
fixada **antes** de correr.

| plano | o que o item leva | responde |
|---|---|---|
| **CONTRATO** | só o que ele declara de si | a porta chega sequer a decidir tema? |
| **LINHAGEM** | mais o `SOURCE_ID` que o gabarito já declara | como se sai a regra temática? |

**A baseline temática é LINHAGEM** — é o único plano que exercita a regra. O
plano CONTRATO fica publicado ao lado, com o mesmo destaque.

### O plano CONTRATO

```
TP 0 · TN 0 · FP 0 · FN 0 · ABSTAIN 36 · NOT_APPLICABLE 0 · ERROR 0
DECISION_COVERAGE = 0.0
```

**Hoje, em produção, a Admission não decide T3 em nenhum destes 36
documentos.** Ela para na pergunta da origem, todas as vezes. Isso não é um
defeito da regra temática: é a linhagem que não chega até ela.

---

## 3 · A BASELINE TEMÁTICA — PLANO LINHAGEM

```
DOCUMENT_TOTAL = 36        (14 SIM · 22 NÃO, rótulo humano)

TP  2      TN  4      FP  5      FN  0
ABSTAIN 25 · NOT_APPLICABLE 0 · ERROR 0
2 + 4 + 5 + 0 + 25 + 0 + 0 = 36
```

| métrica | fórmula | valor |
|---|---|---|
| BINARY_DECISIONS | TP+TN+FP+FN | 11 |
| DECISION_COVERAGE | 11 / 36 | 0.3056 |
| EFFECTIVE_ACCURACY | (TP+TN) / 36 | 0.1667 |
| CONDITIONAL_ACCURACY | (TP+TN) / 11 | 0.5455 |
| PRECISION_T3 | TP / (TP+FP) | 0.2857 |
| RECALL_T3 | TP / (TP+FN) | 1.0 |
| SPECIFICITY | TN / (TN+FP) | 0.4444 |
| F1_T3 | | 0.4444 |

**As duas acurácias ficam lado a lado, sempre.** `RECALL = 1.0` parece
perfeito e não é: a porta deu decisão binária a **2** dos 14 positivos humanos.
Acertou os dois e absteve-se nos outros doze. Um recall calculado sobre dois
casos não é uma taxa de acerto; é o tamanho da amostra a esconder-se dentro de
uma fração.

```
COBERTURA BAIXA COM ACURÁCIA CONDICIONAL ALTA
MEDE SÓ OS CASOS EM QUE A PORTA SE ATREVEU.
```

---

## 4 · POR OBSERVAÇÃO INDEPENDENTE

O agrupamento **não foi inventado aqui e não vem das previsões**. Vem dos pares
quase-duplicados que o fecho do gabarito mediu e commitou antes desta missão.

```
GROUPING_SOURCE = T3-GROUND-TRUTH-EVAL-V1.json :: NEAR_DUPLICATES.PARES
CANONICAL_OBSERVATION_GROUPING_FOUND = YES

GROUP_TOTAL 31 · POSITIVE 11 · NEGATIVE 20
GROUP_PASS 6 · GROUP_FAIL 5 · GROUP_NOT_DECIDED 20
GROUP_EFFECTIVE_ACCURACY = 0.1935
MIXED_GROUND_TRUTH_GROUP = 0
```

A regra do grupo foi fixada antes do resultado: um grupo só passa se **todos**
os seus documentos receberem decisão binária certa. Sem voto de maioria, sem
«a melhor edição», sem «a última».

### Estabilidade entre edições

```
GRUPOS COM MAIS DE UM DOCUMENTO       3
SAME_GROUP_SAME_PREDICTION            3
SAME_GROUP_MIXED_PREDICTIONS          0
```

Onde a porta responde, responde o mesmo às edições do mesmo boletim. Isso é
estabilidade — e não é o mesmo que acerto.

---

## 5 · O BUG DO SUBSTRING AINDA EXISTE

```
SUBSTRING_FALSE_MATCH_STILL_EXISTS = YES
```

A porta casa com `palavra in texto` — substring cru. Nos 36 documentos há **34
casamentos em que a palavra nunca aparece sozinha**:

| ocorrências | universo | termo | dentro de |
|---|---|---|---|
| 9 | T9 | `lancio` | `bilancio` |
| 6 | T7 | `revista` | `prevista` |
| 3 | T7 | `tesi` | `sintesi` |
| 3 | T3 | `sintoma` | `sintomatologia` |
| 2 | T7 | `doi` | `ndoi` |
| 2 | T7 | `prova` | `approvazione` |
| 2 | T3 | `parassita` | `parassitario` |
| 1 | T7 | `universita` | `universitario` |
| 1 | T7 | `tesi` | `fotosintesi` |

**O caso histórico `lancio` dentro de `bilancio` não só sobreviveu: ele produz
resultado.** Uma das quatro decisões negativas corretas assenta inteiramente
nele.

```
decisões binárias que assentam SÓ num casamento falso   1 de 11
destas, contadas como ACERTO                           1

RAW-445e41701f737d73.txt   humano T3_NAO · porta NAO · termo: ['lancio']
```

A porta respondeu «não é T3, porque fala de lançamento de produto (T9)». O
documento não fala de lançamento nenhum: fala de **balanço fitossanitário**.

```
UM ACERTO QUE VEM DE UM CASAMENTO FALSO
NÃO É O MECANISMO A FUNCIONAR: É A SORTE A ALINHAR-SE.
```

Dos 6 acertos binários, **5 são do mecanismo e 1 é da sorte.**

Esta missão mede e não conserta. Nenhum regex foi escrito.

---

## 6 · ONDE FALHA, POR GRUPO

| publicador | acertos / documentos |
|---|---|
| APOL LECCE | 2/2 |
| ARPAE | 2/2 |
| MINISTERO DELLA SALUTE | 1/1 |
| ARIF PUGLIA | 1/3 |
| ARPAV | **0/12** |
| REGIONE LAZIO | **0/5** |
| GIORNATE FITOPATOLOGICHE | 0/2 |
| AGEA | 0/2 |
| REGIONE PIEMONTE | 0/2 |
| AGRIOS · ISMEA · REGIONE MOLISE · SIAS · TERRE DELL'ETRURIA | 0/1 cada |

```
DOCUMENT_TYPE   HTML 0/3 · OUTRO 0/3 · TEXTO-DERIVADO-DE-PDF 6/30
LANGUAGE        KNOWN 19 · UNKNOWN 17 · it 6/17 · en 0/1
```

`NAO SEI` é separado como **UNKNOWN** e nunca contado como uma categoria de
diversidade.

### Os cinco falsos positivos

Todos com vocabulário de praga bem presente no texto, e todos rotulados `NÃO`
pelo humano — são documentos que **falam** de praga sem **tratar** de praga:
balanços anuais, boletins agrometeorológicos com secção fitossanitária,
diretrizes de produção integrada.

```
RAW-2a12cb316622a9a5.txt   GIORNATE FITOPATOLOGICHE   parassita, malattia
RAW-3ef48aaa830edf3b.txt   ARIF PUGLIA                fungo, sintoma, parassita, …
RAW-924aabd94168c53a.txt   GIORNATE FITOPATOLOGICHE   fungo, malattia, insetto, …
RAW-e5176df66216dfd0.txt   AGRIOS                     parassita, insetto, infestazione
RAW-e612807928b5ada9.txt   ARIF PUGLIA                fungo, sintoma, parassita, …
```

```
MENCIONAR NÃO É TRATAR DE.
UMA LISTA DE PALAVRAS NÃO CONSEGUE VER A DIFERENÇA.
```

Dois deles são «Bilancio Fitosanitario» — o mesmo par de documentos que a
missão do gabarito já tinha marcado como armadilha.

---

## 7 · O QUE ESTE NÚMERO NÃO DIZ

```
PERFORMANCE_GATE_PREDEFINED  = NO
CURRENT_MECHANISM_ACCEPTABLE = NOT_DECIDED
```

Procurou-se limiar canónico de aprovação em `BIBLIA-CANONICA-DA-COLETA.md`,
`README.md`, `AGENTS.md` e no censo. **Não existe.** Sem gate prévio, medir não
aprova nem reprova — e inventar o gate depois de ver o resultado seria desenhar
o alvo à volta da flecha.

O PASS desta missão significa uma coisa só:

```
TEMOS UM BASELINE REPRODUZÍVEL.
```

Não significa que a Admission é boa. Não significa que é ruim.

### E o escopo continua o do gabarito

```
EVALUATION_SCOPE = ITALIAN_AGRO_INSTITUTIONAL_CORPUS
```

36 documentos de instituições italianas. Não autoriza afirmar França, Espanha
nem EAME.
