# ARBITRAGEM FINAL DE PRODUTO — SINTONIA EAME

**Data:** 2026-08-31 · **Branch:** `claude/eame-final-product-arbitration`
**Base:** `ad041d7` (refresh corrigido, não alterado)

```
ARBITRATION_COMPLETE = YES
TOP_LEVEL_PRODUCT_UNIT = ATTENTION_OBJECT
V8_IMPLEMENTATION_STARTED = NO    CASCO_V7_MODIFIED = NO    REAL_DATA_WIRED = NO
```

> Este documento **registra** decisões tomadas pelo coordenador. Não reabre inteligência,
> não coleta, não implementa. As decisões viram artefato executável em
> `data/arbitration/`, com **36 provas** que reprovam quem as apagar numa edição futura.

---

## 1 · A DECISÃO ESTRUTURANTE

**A unidade superior do produto deixou de ser o CASO.**

```
ATTENTION_OBJECT
├── PHENOMENON_CASE               país × região × cultura × problema × tempo
├── REGULATORY_DEADLINE           país × registro × produto × prazo
├── COMPETITOR_IDENTITY_CHAIN     competidor × país × produto
└── LONGITUDINAL_FIELD_PRESSURE   país × região × cultura × problema × tempo
```

**Por que isso importa, com o número que forçou a decisão:** o refresh V1 media apenas
`CASE` e publicou `ACT_NOW = 0` como se fosse o estado do produto inteiro. Havia **155
registros com data pública futura** fora daquela medição. O produto tinha quatro unidades e
uma régua só.

**O caso não morreu.** Continua sendo um tipo — e o mais exigente. O que morreu foi a ideia
de que tudo cabe nele.

> **Não inventar `CROP` nem `ISSUE` para objetos cuja unidade não os tem.** Um vencimento
> regulatório não tem cultura: isso é `NOT_APPLICABLE`, um estado de primeira classe — não
> um campo vazio esperando preenchimento.

---

## 2 · A SEGUNDA DECISÃO, E ELA SALVA O PRODUTO

**`MULTI_SIGNAL_REQUIRED_FOR_ATTENTION = NO`.**

Exigir convergência multi-sinal para tudo mataria o **único objeto com decisão de negócio
defensável** do acervo: um vencimento regulatório tem, por natureza, **uma** fonte — e não
pode ter duas.

No lugar, um portão de cinco requisitos conjuntivos:

```
VALID_EVIDENCE  +  OBJECT_SPECIFIC_TRIGGER  +  TIME_RELEVANCE
                +  DECISION_QUESTION  +  DECISION_OWNER
```

**Convergência vira força adicional**, onde for semanticamente aplicável — e a regra dela
não afrouxa:

```
CONVERGENCE_REQUIRES = SAME_PROPOSITION + INDEPENDENT_EVIDENCE
CONTEXTUAL_ALIGNMENT nunca entra na conta
```

---

## 3 · O QUE MUDA NA NAVEGAÇÃO

| superfície V7 | decisão | para onde vai |
|---|---|---|
| **Radar / Casos** | **evolui** | **Radar de Atenção** — abriga os quatro tipos |
| **Radar do Futuro** | **absorvido** | vira **estado/view** do Radar: `FORMING` · `WATCH` · `NEEDS_EVIDENCE` · `FUTURE` |
| **Janelas da Cultura** | **absorvido** | vira **bloco de tempo** dentro do objeto |
| **Análises** | **absorvido** | vira leitura dentro do **Object Detail** |
| **Caso** (detalhe) | **fortalecido** | vira **Object Detail** modular, por tipo |
| Visão Geral · Acervo · Fontes · Relatórios · Camada EAME · Sistema · Config | **permanecem** | — |
| **Creator Map** | **não entra** | `TEST_AS_CAPABILITY`, contextual e buscável |

**Três superfícies somem do menu e nenhuma função se perde.** É o oposto de simplificar
cortando: cada uma vira estado, bloco ou aba de algo que já existia.

**Não se criam quatro radares.** `Radar Regulatório`, `Radar Meta`, `Radar Foresight` e
`Radar Campo` como dashboards separados é exatamente o `ESSENCE_RISK` que o produto combate.

---

## 4 · AS DECISÕES POR CAPACIDADE

| capacidade | decisão | a lei que viaja junto |
|---|---|---|
| **Competitor Foresight** | vira `COMPETITOR_IDENTITY_CHAIN`, tipo próprio | `IDENTITY_CONVERGENCE ≠ PHENOMENON_CONVERGENCE`. As 36 tuplas **não entram na Home só por existirem** |
| **Meta** | **sem superfície própria** — é perna de competição | `DO_NOT_BUILD = META_DASHBOARD` |
| **Territorial** | camada `Campo` do `PHENOMENON_CASE` | o par cultura × problema fecha **dentro da passagem** |
| **Longitudinal Field (RAIF)** | tipo válido, `IN_SCOPE` | `INDEPENDENCE_FROM_TERRITORIAL_RAIF = NOT_PROVED` — não conta como segunda perna |
| **Regulatory Deadline** | tipo válido | `EXPIRY ≠ WITHDRAWAL`. Autoriza **revisão**, não alerta. Sem dashboard |
| **Creator Map** | `TEST_AS_CAPABILITY` | `PERSON_CREATOR ≠ FARM_BUSINESS` · rota de ativação ≠ evidência de problema |
| **Expert Directory** | capability contextual | **portão `ISSUE_EXPERTISE_PROVED` obrigatório**. Nunca ranking |
| **Unknown** | estado transversal | nunca ferramenta. Sem audit dashboard |

---

## 5 · O QUE FOI PRESERVADO SEM MUDANÇA

```
CASCO V7 ..................... testemunha byte a byte, SHA-256 a31ea184…87c6a
MULTILINGUAL_CONTRACT_V1 ..... FROZEN em 1443f643 — ATTENTION_OBJECT_ID é neutro de idioma
ADAMA DISEASE ICONS .......... existem no design system; crosswalk NOT_MEASURED
os quatro handoffs ........... ACCEPTED, fixados por commit
REFRESH_V1_WITNESS ........... eb18c87, não reescrito
```

**O V8 herda do V7:** identidade visual, gramática visual e a hierarquia que ainda faz
sentido. **Não herda** a ontologia de um tipo único de caso.

---

## 6 · CADÊNCIA — a decisão de não decidir demais

```
DAILY_PRODUCT_CLAIM = NO        SOURCE_SPECIFIC_CADENCE = YES
```

O produto **não** se declara diário nem semanal como verdade universal. A cadência é por
fonte e por objeto, mais mudança de estado. Um *digest* de leitura pode ser periódico —
**mas não define a cadência do dado**.

Detalhe por camada em [`FINAL-CADENCE-MODEL-EAME.md`](FINAL-CADENCE-MODEL-EAME.md).

---

## 7 · O QUE ESTA ARBITRAGEM **NÃO** DECIDIU

Sendo explícito, para que ninguém leia decisão onde não há:

- **não** decidiu se a fila vazia é aceitável a longo prazo — decidiu que **fila vazia se
  mostra como vazia**;
- **não** decidiu reconstruir cultura × alvo nos registros nacionais — segue sendo a decisão
  de maior alavancagem, e é de sistema, não de negócio;
- **não** promoveu o Creator Map a ferramenta — condicionou a **uso real instrumentado**;
- **não** afirmou valor diário em camada nenhuma.

---

## 8 · ARTEFATOS DESTA RODADA

| | |
|---|---|
| [`FINAL-TOOL-SET-EAME.md`](FINAL-TOOL-SET-EAME.md) | as superfícies finais |
| [`ATTENTION-OBJECT-MODEL-EAME.md`](ATTENTION-OBJECT-MODEL-EAME.md) | os quatro tipos, campo a campo |
| [`ATTENTION-READINESS-GRAMMAR-EAME.md`](ATTENTION-READINESS-GRAMMAR-EAME.md) | o portão e a máquina de estados |
| [`FINAL-ACTION-MODEL-EAME.md`](FINAL-ACTION-MODEL-EAME.md) | tipos de ação e donos |
| [`FINAL-CADENCE-MODEL-EAME.md`](FINAL-CADENCE-MODEL-EAME.md) | cadência por camada |
| [`FINAL-HOSE-MAP-EAME.md`](FINAL-HOSE-MAP-EAME.md) | nove mangueiras, nenhuma ligada |
| [`V8-PRODUCT-SPEC-EAME.md`](V8-PRODUCT-SPEC-EAME.md) | a especificação fechada |
| `data/arbitration/*.json` | schema · máquina de estados · mapa de mangueiras |

**Suíte: 759 provas, 0 falhas.**
