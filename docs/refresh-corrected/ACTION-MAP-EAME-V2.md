# ACTION MAP — V2

**Data:** 2026-08-31 · derivado de `data/refresh-corrected/ACTION-CANDIDATES.json`

```
ACTION_TYPE ∈ { BUSINESS_DECISION · SYSTEM_DECISION · INVESTIGATION }
```

---

## 0 · A CORREÇÃO QUE MUDA A LEITURA DO V1

O V1 misturou dois tipos de ação e concluiu coisa errada com isso.

**Exemplo do próprio V1:** *"MARKET DEVELOPMENT — decidir se vale reconstruir cultura ×
alvo nos três registros"*. Isso **não é ação de negócio de um departamento**. É decisão
sobre o desenvolvimento do próprio Sintonia — `SYSTEM_DECISION`.

E o V1 usou justamente esse tipo de linha para concluir que *"Market Development é a única
área com ação sustentada em todos os itens, o que confirma com dado que ela é o usuário
central"*.

> **`CENTRAL_USER_ABSORPTION_GUARD`.** Market Development é usuário central **por decisão
> arquitetônica**. Ocupar 100% das linhas de uma tabela não prova centralidade — prova que
> a tabela absorveu tudo para o mesmo dono, que é sintoma de tabela mal separada.

Há prova disso: existe candidato cujo dono **não** é Market Development.

---

## 1 · POR CANDIDATO

### `IT × Grosseto × trigo duro × fusarium`

| área | tipo | ação sustentada |
|---|---|---|
| **TÉCNICO / AGRONOMIA** | `INVESTIGATION` | verificar se o boletim LAMMA é fonte recorrente ou observação isolada — **uma safra não é série** |
| **MARKET DEVELOPMENT** | `INVESTIGATION` | decidir se o par entra no piloto |
| PORTFÓLIO | `NO_DEFENSIBLE_ACTION_YET` | sem cultura × alvo italiano, não se sabe se há resposta registrada |
| REGULATÓRIO · MARKETING · COMERCIAL · SUPPLY | `NO_DEFENSIBLE_ACTION_YET` | — |

**Nenhuma ação de negócio.** Duas de investigação.

### Vencimentos regulatórios ADAMA na Itália — **o único `BUSINESS_DECISION`**

| área | tipo | ação sustentada |
|---|---|---|
| **REGULATÓRIO** *(dono)* | **`BUSINESS_DECISION`** | revisar/confirmar o estado dos 155 registros em vigor com vencimento futuro |
| **PORTFÓLIO** | **`BUSINESS_DECISION`** | confirmar quais desses registros sustentam pares comercialmente relevantes |
| MARKET DEVELOPMENT | `NO_DEFENSIBLE_ACTION_YET` | não é decisão de MD |
| demais | `NO_DEFENSIBLE_ACTION_YET` | — |

**Este é o candidato que quebra a absorção.** O dono não é Market Development — e é
exatamente por isso que ele prova que a tabela do V1 estava concentrando por defeito de
separação, não por centralidade real.

### Cadeias de identidade de concorrente

| área | tipo | ação sustentada |
|---|---|---|
| **MARKET DEVELOPMENT** | `SYSTEM_DECISION` | decidir se vale reconstruir cultura × alvo — **decisão sobre o Sintonia**, não sobre o mercado |
| PORTFÓLIO | `SYSTEM_DECISION` | mesma decisão, do lado do catálogo |
| MARKETING | `NO_DEFENSIBLE_ACTION_YET` | sem cultura e sem problema, não há mensagem |
| demais | `NO_DEFENSIBLE_ACTION_YET` | — |

### RAIF · pressão longitudinal de repilo

| área | tipo | ação sustentada |
|---|---|---|
| **TÉCNICO / CIÊNCIA** | `INVESTIGATION` | avaliar leitura **intra-safra** — o próprio artefato aponta isso como o que melhoraria o backtest |
| MARKET DEVELOPMENT | `NO_DEFENSIBLE_ACTION_YET` | 11 falsos positivos em 14 disparos não sustentam priorização |
| demais | `NO_DEFENSIBLE_ACTION_YET` | — |

### Os cinco recortes sem chave completa

`NO_DEFENSIBLE_ACTION_YET` em **todas** as sete áreas. A única ação existente é
`SYSTEM_DECISION`: extrair localidade dos itens franceses e problema dos espanhóis, sobre
material já preservado.

---

## 2 · O PLACAR, COM O ESCOPO QUE FALTAVA

```
CASE_ACT_NOW ................... 0
OBJECT_ACT_NOW ................. 0
REGULATORY_DEADLINE_REVIEW ..... 155 registros elegíveis a revisão
NOT_EVALUATED_OBJECT_TYPES ..... COMPETITOR_PUBLIC_COMM · CREATOR

BUSINESS_DECISION .............. 1 candidato  (vencimentos IT)
SYSTEM_DECISION ................ 2 candidatos
INVESTIGATION .................. 3 candidatos
```

**`ACT_NOW = 0` continua verdade — e agora tem escopo.** No V1 ele parecia dizer *"o
produto não tem nada"*. Diz outra coisa: **nenhum caso de fenômeno autoriza ação imediata**,
e havia 155 registros com data pública futura **fora** daquela medição.

E vencimento **não vira `ACT_NOW`**. Autoriza revisão. `EXPIRY ≠ WITHDRAWAL`.

---

## 3 · O QUE ISTO REVELA SOBRE O PRODUTO

1. **A única decisão de negócio defensável hoje é regulatória** — e é a mais modesta:
   revisar datas publicadas. O eixo mais forte do projeto continua sendo aquele em que a
   antecipação não depende de previsão.
2. **Market Development aparece muito, quase sempre em `SYSTEM_DECISION`.** Isso não prova
   centralidade; prova que boa parte do que o produto entrega hoje é **decisão sobre o
   próprio produto**, não sobre o mercado. É honesto, e é um estágio.
3. **Marketing e Comercial continuam sem ação** — em duas passagens seguidas, com quatro
   handoffs aceitos. Um painel que preenchesse essas linhas estaria inventando.
