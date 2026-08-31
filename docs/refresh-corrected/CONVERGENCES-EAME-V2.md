# CONVERGÊNCIAS — V2

**Data:** 2026-08-31 · derivado de `data/refresh-corrected/SIGNAL-DEPENDENCY-GRAPH-V2.json`

```
CONVERGENCE_REQUIRES = SAME_PROPOSITION + INDEPENDENT_EVIDENCE
```

---

## 0 · TRÊS TIPOS QUE NUNCA SOMAM

O V1 tinha um número só. Ele misturava coisas que não são a mesma coisa:

| tipo | o que afirma | quantidade hoje |
|---|---|---|
| **`PHENOMENON_CONVERGENCE`** | duas famílias independentes afirmam **o mesmo fenômeno** | **0** |
| **`IDENTITY_CONVERGENCE`** | duas ou mais fontes sustentam a mesma **identidade** | **36 tuplas · 29 produtos** |
| **`CONTEXTUAL_ALIGNMENT`** | uma fonte dá **contexto** à outra, sem afirmar a mesma proposição | não contado — ver §2 |

**Somar os três daria "36 convergências" e seria falso.** Nenhuma delas é convergência de
fenômeno.

---

## 1 · O GRAFO TIPADO

```
RELATIONS_TOTAL ......... 17
  DERIVATION_DEPENDENCY .. 3      SOURCE_DEPENDENCY ...... 5
  ENTITY_DEPENDENCY ...... 2      OBSERVATION_DEPENDENCY . 2
  SEMANTIC_DEPENDENCY .... 2      INDEPENDENT_SOURCE ..... 4  (as somas fecham por teste)
```

O red team estimou 12/8/4. O derivado é **17/13/4** — o independente bate, e o dependente
cresceu porque o V2 acrescentou cinco relações que o V1 não via.

### Famílias que podem contar hoje — sete

```
TERRITORIAL · SCIENCE_RESEARCHER · NATIONAL_REGISTRY · TRADEMARK
META_PAID_ADS · CREATOR · FIELD_HISTORICAL     ← esta entrou nesta passagem

NÃO CONTA:  COMPETITOR_PUBLIC_COMM   (22 contas provadas, zero conteúdo)
```

---

## 2 · A LEI NOVA QUE MAIS MUDA CONTAGEM

### `SEMANTIC_MISMATCH_NOT_CORROBORATION`

```
FIELD OBSERVATION      "Fusarium observado em trigo duro em Grosseto"
NATIONAL REGISTRATION  "produto autorizado para trigo duro × Fusarium"
```

Parecem duas pernas do mesmo caso. **Não são.** O segundo oferece
`LOCAL RESPONSE / PORTFOLIO CONTEXT` — **não confirma que o fenômeno de campo existe**.

É `CONTEXTUAL_ALIGNMENT`, e alinhamento contextual **nunca** entra na conta de convergência
de fenômeno. Sem essa lei, o caso italiano teria virado "2 pernas" no minuto em que o
registro italiano ganhasse cultura × alvo — sem nenhuma observação nova de campo.

### `SAME_INDEX ≠ SAME_EVIDENCE`

OpenAlex é infraestrutura de **descoberta**. Dois artigos achados pelo mesmo índice
continuam sendo **dois artigos** — o V1 tratava "ciência e pesquisador saem do mesmo
OpenAlex" como se isso apagasse a evidência.

O que **é** dependência ali é outra coisa: o corpus de pesquisador **herda a identidade**
resolvida pelo diretório. Isso é `ENTITY_DEPENDENCY`, e é mais estreito do que eu disse.

### `SAME_PUBLISHER ≠ INDEPENDENT_OBSERVATION`

O RAIF entrou no escopo — e **também é fonte territorial** (4 itens). Entrar no escopo não
compra perna: `INDEPENDENCE_FROM_TERRITORIAL_RAIF = NOT_PROVED`, porque a linhagem
parcela-a-parcela não está preservada.

---

## 3 · POR RECORTE

| recorte | famílias independentes | classe |
|---|---:|---|
| `IT_DURUM_WHEAT_FUSARIUM` | **1** — TERRITORIAL | `SINGLE_SIGNAL` |
| `FR_VINE_DOWNY_MILDEW` | 0 | `NOT_ENOUGH_EVIDENCE` — falta **localidade** |
| `ES_OLIVE_REPILO` | 0 | `NOT_ENOUGH_EVIDENCE` — falta **problema** |
| `ES_CEREAL_SEPTORIA` | 0 | `NOT_ENOUGH_EVIDENCE` |
| `IT_VINE_FLAVESCENCE` | 0 | `NOT_ENOUGH_EVIDENCE` |
| `FR_CEREAL_SEPTORIA` | 0 | `NOT_ENOUGH_EVIDENCE` |

**`ES_OLIVE_REPILO` agora tem duas camadas — e mesmo assim não converge.**
Territorial (0 itens com o problema no corpo) e `LONGITUDINAL_FIELD_PRESSURE` (série
histórica). Mas as duas **compartilham o publicador RAIF**, e a independência é
`NOT_PROVED`. Duas camadas do mesmo publicador não são duas famílias.

---

## 4 · O QUE FECHARIA UMA CONVERGÊNCIA DE FENÔMENO

Em ordem de custo, e **nenhuma é coleta de fonte nova**:

1. **Localidade nos itens franceses.** Quatro já têm o problema no corpo; sete falham por
   região. É extração, sobre material preservado.
2. **Cultura × alvo do rótulo italiano.** 139 dos 163 PDFs estão no disco.
   ⚠️ E mesmo assim isso daria `CONTEXTUAL_ALIGNMENT`, **não** convergência de fenômeno.
3. **Linhagem parcela-a-parcela do RAIF.** Sem ela, histórico e territorial continuam uma
   família só.
4. **Corpus científico não-espanhol.** Sem ele, expertise de IT e FR fica `NOT_READY` — que
   não é `NOT_PROVED`.

---

## 5 · O NÚMERO, SEM ENFEITE

```
PHENOMENON_CONVERGENCE ....... 0
IDENTITY_CONVERGENCE ......... 36 tuplas · 29 produtos
CONTEXTUAL_ALIGNMENT ......... existe, não é contado como convergência
SINGLE_SIGNAL ................ 1
NOT_ENOUGH_EVIDENCE .......... 5
```

**Zero continua permitido, e continua sendo o resultado.** Mudou o motivo: no V1 era por
dependência entre camadas; no V2 é por **falta de uma segunda proposição igual**, medida
recorte a recorte, com o bloqueador exato de cada um.
