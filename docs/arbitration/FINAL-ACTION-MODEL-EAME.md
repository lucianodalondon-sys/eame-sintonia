# MODELO FINAL DE AÇÃO — SINTONIA EAME

**Data:** 2026-08-31

---

## 1 · TRÊS TIPOS DE AÇÃO

```
BUSINESS_DECISION    o departamento decide algo sobre o MERCADO
SYSTEM_DECISION      alguém decide algo sobre o PRÓPRIO SINTONIA
INVESTIGATION        alguém vai verificar, confirmar ou medir
```

**Por que a separação existe, com o erro que a forçou.** O refresh V1 escreveu:

> *"MARKET DEVELOPMENT — decidir se vale reconstruir cultura × alvo nos três registros"*

Isso **não é ação de negócio de um departamento**. É decisão sobre o desenvolvimento do
produto. E o V1 usou justamente esse tipo de linha para concluir que *"Market Development é
a única área com ação sustentada em todos os itens, o que confirma com dado que ela é o
usuário central"*.

**A conclusão vinha da própria confusão.**

---

## 2 · `CENTRAL_USER_ABSORPTION_GUARD`

> **Market Development é usuário central por decisão arquitetônica — não por contagem de
> linhas.**

Ocupar 100% das linhas de uma tabela **não prova centralidade**. Prova que a tabela absorveu
tudo para o mesmo dono, o que é sintoma de tabela mal separada.

**Há prova disso**, e ela é dura: existe candidato cujo dono **não** é Market Development —
os vencimentos regulatórios, que pertencem a `REGULATÓRIO` e `PORTFÓLIO`. Se MD fosse dono
de tudo, a tabela não estaria medindo nada.

---

## 3 · OS SETE DEPARTAMENTOS

```
MARKET DEVELOPMENT   ·  MARKETING  ·  COMMERCIAL  ·  TECHNICAL / SCIENCE
REGULATORY           ·  PORTFOLIO  ·  SUPPLY
```

**`NO_DEFENSIBLE_ACTION_YET` é uma saída legítima e frequente.** Não se atribui departamento
para completar tabela.

---

## 4 · O MAPA DE AÇÃO POR TIPO DE OBJETO

Cada tipo tem donos naturais. **Nem todo tipo toca todo departamento.**

| tipo | dono primário | dono secundário | quem **não** entra |
|---|---|---|---|
| **PHENOMENON_CASE** | TÉCNICO / AGRONOMIA | MARKET DEVELOPMENT · PORTFÓLIO | Comercial e Supply, até haver resposta local e janela |
| **REGULATORY_DEADLINE** | **REGULATÓRIO** | PORTFÓLIO | Market Development — não é decisão de MD |
| **COMPETITOR_IDENTITY_CHAIN** | MARKET DEVELOPMENT | PORTFÓLIO | Marketing — sem cultura e sem problema, não há mensagem |
| **LONGITUDINAL_FIELD_PRESSURE** | TÉCNICO / CIÊNCIA | MARKET DEVELOPMENT | os demais |

---

## 5 · O ESTADO MEDIDO — e o que ele diz do produto

```
BUSINESS_DECISION ....... 1 candidato    (vencimentos regulatórios IT)
SYSTEM_DECISION ......... 2 candidatos
INVESTIGATION ........... 3 candidatos

CASE_ACT_NOW ............ 0
OBJECT_ACT_NOW .......... 0
REGULATORY_REVIEW ....... 155 registros elegíveis a revisão
```

**Três leituras honestas:**

1. **A única decisão de negócio defensável hoje é regulatória** — e é a mais modesta:
   revisar datas publicadas. O eixo mais forte do projeto continua sendo aquele em que a
   antecipação **não depende de previsão**.
2. **Boa parte do que o produto entrega hoje é `SYSTEM_DECISION`** — decisão sobre o próprio
   produto, não sobre o mercado. É honesto, e é um estágio. Chamar isso de ação
   departamental era o erro do V1.
3. **Marketing e Comercial continuam sem ação**, em três medições seguidas, com quatro
   handoffs aceitos. Um painel que preenchesse essas linhas estaria inventando.

---

## 6 · A REGRA DE VENCIMENTO

**Vencimento não vira `ACT_NOW`.**

```
EXPIRY ≠ WITHDRAWAL          EXPIRY_DATE_REACHED ≠ PRODUCT_DISCONTINUED

AUTORIZA    REVIEW / CONFIRMATION BY REGULATORY
NÃO AUTORIZA "ALERT: PRODUCT WILL DISAPPEAR"
```

E **155 registros não são 155 itens de atenção**. Falta a régua que diz **quais** merecem
revisão — e essa régua é decisão de produto, não medição. É por isso que o objeto está em
`ATTENTION_CANDIDATE_TEST` e não em `ATTENTION_READY`.

---

## 7 · O QUE A AÇÃO NUNCA FAZ

```
não afirma REVENUE · MARGIN · SALES · ROI REALIZED       (não há dado interno, e não haverá)
não transforma vencimento em alarme
não atribui departamento para completar tabela
não usa SYSTEM_DECISION como prova de valor de negócio
não infere centralidade a partir de ocupação de tabela
```
