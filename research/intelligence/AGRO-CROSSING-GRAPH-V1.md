# GRAFO DE CRUZAMENTOS AGRÍCOLAS — MODELO CANDIDATO V1

```
MISSAO     C-INT-AGRO-BENCH-01
ESPECIE    MODELO CANDIDATO — NAO ESCOLHE TECNOLOGIA, NAO IMPLEMENTA NADA
MEDIDO_EM  2026-09-13
```

> ```
> GRAPH MODEL != GRAPH DATABASE.
> ```
> Esta missão **não escolhe banco de dados**. Um grafo aqui é um modelo de
> relações, e cada relação tem de justificar a sua existência por uma pergunta
> que sem ela não se consegue responder. Relação que não tem pergunta **não
> entra** — «grafo parece moderno» não é um argumento.

---

## 0 · O TESTE A QUE CADA RELAÇÃO FOI SUBMETIDA

```
1. Que pergunta deixa de ter resposta se esta relacao nao existir?
2. Existe chave factual para a instanciar, ou e semelhanca?
3. Ela e DIRIGIDA? (A suporta B nao e B suporta A)
4. Ela pode ser REVERTIDA, e o que a reverte?
5. Um sistema maduro do agro tem o equivalente?
```

Relação que falha em `1` ou `2` foi **eliminada**, e a eliminação está escrita.

---

## 1 · AS RELAÇÕES QUE SOBREVIVERAM

### Relações de evidência (genéricas, mas com corpo agrícola)

| relação | pergunta que só ela responde | chave | reverte quando |
|---|---|---|---|
| `SUPPORTS` | que evidência sustenta este julgamento? | claim_id → finding_id | a evidência é retratada |
| `CONTRADICTS` | o que diz o contrário, e está visível? | claim_id → finding_id | — (é first-class, `INT-LAW-033`) |
| `SAME_ORIGIN` | estas duas evidências são uma só? | trial_id · dataset_id · ONPF · DOI citado | descobre-se a partilha |
| `DEPENDS_ON` | esta conclusão herda um pressuposto de outra? | finding → finding | o pressuposto cai |
| `ABOUT` | de que sujeito isto fala? | EPPO code · registration_id · NUTS | a normalização é revista |
| `OBSERVED_AT` | onde e quando o facto ocorreu? | (AREA, TEMPO) | o lugar é reclassificado |

> **`SAME_ORIGIN` é a relação mais importante do agro científico**, e é a única
> que impede que três papers de um ensaio contem como três evidências. Sem ela,
> a convergência é aritmética de duplicados.

### Relações agronómicas (só existem neste domínio)

| relação | pergunta que só ela responde | chave | autoridade externa |
|---|---|---|---|
| `HAS_ACTIVE_SUBSTANCE` | o que há dentro deste produto? | product → substância (+CAS) | EU Pesticides DB · Banca dati IT |
| `AUTHORIZED_FOR` | este registo autoriza este uso? | registration → `PPP_USE` | **EPPO PP 1/248 (3)** |
| `HAS_LABEL_USE` | que usos tem este rótulo, nesta versão? | (registration, versão) → uso | rótulo oficial |
| `VALID_FOR` | em que país e até quando? | registo → (país, VALID_FROM, VALID_TO) | decreto |
| `AFFECTS` | quem é atingido por esta mudança regulatória? | substância → produtos → usos → (cultura, alvo) | — |
| `HOST_OF` | este organismo ataca esta cultura? | EPPO_pest ↔ EPPO_crop | EPPO GD · CABI |
| `HAS_WINDOW` | quando é que isto ainda se pode fazer? | (cultura, alvo, área) → janela | BBCH ∩ rótulo ∩ infecção |
| `AT_STAGE` | em que fase da cultura isto aconteceu? | observação → BBCH | BBCH |
| `MEASURED_BY` | com que método e escala isto foi medido? | observação → (trait, method, scale) | **Crop Ontology · MIAPPE** |
| `SAMPLED_FROM` | de que população saiu esta amostra? | observação → população-alvo | **EFSA** |

### Relações de promoção

| relação | pergunta | reverte quando |
|---|---|---|
| `SCREENED_BY` | que rastreio deixou isto passar, e com que resposta a cada critério? | um critério muda |
| `PROMOTES_TO` | que portão foi atravessado, com que prova? | a prova cai |
| `DEMOTED_BY` | **o que fez isto andar para trás?** | — (é o registo da reversão) |

> **`DEMOTED_BY` não estava na lista do enunciado, e é obrigatória.** A ISPM 8
> tem `pest records invalid` e `pest no longer present`; sem uma aresta que
> registe a despromoção, uma correcção é indistinguível de um apagamento.

---

## 2 · AS RELAÇÕES QUE FORAM ELIMINADAS, E PORQUÊ

| proposta | veredito | razão |
|---|---|---|
| `STRENGTHENS` / `WEAKENS` | **ELIMINADAS** | são `SUPPORTS`/`CONTRADICTS` com um advérbio. A força pertence ao julgamento, não à aresta. Duas arestas para o mesmo facto divergem no dia em que uma mudar |
| `BLOCKS` | **REFORMULADA** | não é uma aresta entre objectos: é o **estado de um portão**. Vive na máquina de promoção, com o motivo e a versão da regra |
| `RELATED_TO` | **NUNCA EXISTIU E NÃO DEVE** | não responde a pergunta nenhuma. É semelhança com gravata |
| `MENTIONS` | **ELIMINADA como aresta de facto** | `PLACE_MENTION != FACT_LOCATION` (`COL-LAW-032`). Pode existir como registo de texto; **não** como relação do grafo de conhecimento |
| `SIMILAR_TO` | **PROIBIDA** | `COL-LAW-034` e `INT-LAW-081`: identidade nunca por similaridade textual. Medido duas vezes nesta casa, com prejuízo |

```
UMA ARESTA QUE NAO MUDA NENHUMA RESPOSTA E PESO MORTO QUE ALGUEM
VAI ACABAR POR LER COMO PROVA.
```

---

## 3 · OS CRUZAMENTOS, UM A UM (`§35`)

Formato do enunciado. `JOIN_KEY` ausente ⇒ o cruzamento **não se faz**
(`INT-LAW-091`).

### `SCIENCE × FIELD`
```
SUBJECT_A  resultado de ensaio          SUBJECT_B  relato de campo
JOIN_KEY   (EPPO_crop, EPPO_target) + area + janela sazonal
SEMANTIC   FRACA — o ensaio mede com metodo; o boletim descreve sem metodo
TEMPORAL   compativel se a janela sazonal for a mesma
GEOGRAPHIC FRACA — local do ensaio != regiao do boletim; e a afiliacao do autor
           nao e nenhum dos dois
DEPENDENCY baixa — origens genuinamente diferentes
REVELA     que a ciencia ja estudou o problema que o campo esta a relatar
NAO PROVA  que o resultado do ensaio se aplica aqui. Solo, variedade, pressao e
           pratica sao outros.
VEREDITO   UTIL, com a limitacao SEMPRE visivel
```

### `SCIENCE × FUTURE`
```
JOIN_KEY   sujeito (EPPO ou substancia) + horizonte
DEPENDENCY ALTA E PERIGOSA — o sinal de horizon scanning muitas vezes E um
           paper. Contar os dois e contar uma vez duas vezes.
REVELA     que um tema emergente tem base cientifica a crescer
NAO PROVA  que vai acontecer
VEREDITO   UTIL, e SO com SAME_ORIGIN aplicado antes
```

### `FIELD × COMPETITOR`
```
JOIN_KEY   (cultura, alvo, area, janela)
SEMANTIC   MUITO FRACA — um e ocorrencia, o outro e comunicacao
REVELA     que o concorrente esta a comunicar sobre um problema que o campo
           relata
NAO PROVA  que o concorrente esta a vender mais, nem que o problema e maior
VEREDITO   UTIL COMO CONTEXTO. NUNCA como medida de mercado.
           IT-T9-008: COMPANY_CLAIM != REGULATORY_FACT
```

### `COMPETITOR × PORTFOLIO`
```
JOIN_KEY   (pais, cultura, alvo) via registo
SEMANTIC   FORTE — os dois lados sao registo, e o registo e autoridade
REVELA     onde o concorrente tem uso autorizado e nos nao
NAO PROVA  quota, preco, presenca em prateleira, nem intencao
VEREDITO   O CRUZAMENTO MAIS SOLIDO QUE DADO PUBLICO PERMITE.
           E o limite esta ja escrito em SQL:
           `resposta_registrada.current_commercial_availability DEFAULT NAO_SEI`
```

### `COMPETITOR × LABEL` · `LABEL × PORTFOLIO`
```
JOIN_KEY   PPP_USE (a tupla de seis) — e e por isso que ela tem de existir
SEMANTIC   FORTE
REVELA     diferenca de uso autorizado ao nivel a que a diferenca importa:
           nao «temos produto para vinha», mas «temos para VINHA x PERONOSPORA
           x aplicacao foliar x uva de mesa x campo aberto»
NAO PROVA  eficacia relativa, nem preferencia do agricultor
VEREDITO   BLOQUEADO HOJE — `registro_uso` tem 4 dos 6 eixos
```

### `LABEL × OPPORTUNITY`
```
JOIN_KEY   PPP_USE + janela
HARD GATE  autorizacao VIGENTE a data da janela — nao a data de hoje
NAO PROVA  disponibilidade comercial
VEREDITO   e a aresta que transforma achado em oportunidade de NIVEL B, e so B
```

### `CROP WINDOW × OPPORTUNITY`
```
JOIN_KEY   (cultura, area) + fenologia
SEMANTIC   e aqui que o agro se separa de tudo o resto: a janela nao e um
           intervalo de calendario, e a INTERSECCAO de quatro:
             fenologia da cultura
           ∩ janela de infeccao do patogeno
           ∩ janela de aplicacao autorizada pelo rotulo (estadio + PHI)
           ∩ janela de preparacao comercial
REVELA     se ainda ha tempo para alguem fazer alguma coisa
NAO PROVA  que alguem vai fazer
VEREDITO   OBRIGATORIO PARA ACIONABILIDADE. Hoje temos a primeira
           aproximadamente (`010_calendario_agronomico`), e as outras tres nao.
```

### `MARKET × OPPORTUNITY`
```
JOIN_KEY   commodity -> cultura -> (area, campanha)
SEMANTIC   FRACA. O preco do trigo e o tratamento de septoriose vivem em
           cadeias causais diferentes.
REVELA     contexto de disposicao a investir
NAO PROVA  NADA sobre a decisao de tratamento
VEREDITO   CONTEXTO. Promove-lo a oportunidade e o erro classico —
           ver ataque 12 do red team.
```

### `MARKET × FUTURE`
```
JOIN_KEY   commodity + horizonte
VEREDITO   UTIL para narrativa; sem valor probatorio. A materialidade tem de
           ser calculada contra base historica, ou nao ha achado.
```

### `REGULATORY × PRODUCT` · `ACTIVE SUBSTANCE × PRODUCT`
```
JOIN_KEY   (pais, registration_id) · nome ISO + CAS
SEMANTIC   FORTE — cadeia de autoridade
REVELA     quem depende de uma substancia em risco, e quanto
NAO PROVA  impacto comercial
VEREDITO   O MAIS FORTE DE TODOS. E o que a casa ja provou conseguir:
           «Bayer com 32 produtos na Franca a depender do protioconazol».
           Note-se: isto e uma contagem de REGISTOS, e diz-se que e.
```

### `PRODUCT × CROP × TARGET`
```
⚠️ ESTE CRUZAMENTO, ESCRITO ASSIM, E UMA ARMADILHA.
JOIN_KEY   nao existe um par (produto, cultura). Existe um USO.
           Ler «produto autorizado para vinha» + «alvo peronospora» como
           «produto autorizado contra peronospora na vinha» e uma inferencia
           NOSSA, nao um facto do rotulo.
           INT-LAW-144 ja o diz: produto para cultura != produto para alvo.
VEREDITO   SUBSTITUIR por `REGISTRATION -> HAS_LABEL_USE -> PPP_USE`.
           O cruzamento nao e triplo: e a leitura de UM objecto.
```

---

## 4 · A REGRA QUE GOVERNA TODOS

```
UM CRUZAMENTO NAO PODE ALEGAR MAIS DO QUE O SEU APOIO MAIS FRACO.
```

Já é lei desta casa (`COL-LAW-032`). No agro ela tem três faces, e as três
mordem:

```
PRECISAO GEOGRAFICA   provincia x regiao  ->  o resultado e REGIAO
PRECISAO TEMPORAL     dia x campanha      ->  o resultado e CAMPANHA
PRECISAO SEMANTICA    especie x grupo     ->  o resultado e GRUPO
```

E a terceira é a que o agro acrescenta, e não existia na lei escrita: cruzar um
uso de rótulo que diz `Cereali a paglia` com uma observação que diz
`Triticum aestivum` produz um resultado ao nível de **grupo**, nunca de espécie
— mesmo que a observação seja mais precisa.

```
O CRUZAMENTO HERDA O PIOR DOS DOIS LADOS. SEMPRE.
E NO AGRO O PIOR LADO E QUASE SEMPRE O ROTULO,
PORQUE O ROTULO FALA EM GRUPOS DE PROPOSITO.
```

---

## 5 · VEREDITO

```
CROSSING_MODEL_DIRECTION = PRONTA
CROSSING_MODEL_INSTANCIAVEL_HOJE = NAO
```

Das 19 relações que sobreviveram, **11 dependem de objectos que não existem**:
`PPP_USE`, variável observada, população-alvo, janela composta. As 8 restantes
— as de evidência e as regulatórias simples — são instanciáveis hoje, e são
exactamente aquelas em que a casa já produziu resultado defensável.

```
COMECAR PELAS OITO QUE FUNCIONAM NAO E MODESTIA: E A UNICA MANEIRA
DE AS ONZE RESTANTES NASCEREM COM CHAVE, EM VEZ DE NASCEREM COM PALPITE.
```
