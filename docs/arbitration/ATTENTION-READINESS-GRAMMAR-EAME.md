# GRAMÁTICA DE ATENÇÃO — SINTONIA EAME

**Data:** 2026-08-31 · artefato executável em `data/arbitration/ATTENTION-STATE-MACHINE.json`

```
MULTI_SIGNAL_REQUIRED_FOR_ATTENTION = NO
```

---

## 1 · POR QUE CONVERGÊNCIA DEIXOU DE SER REQUISITO

Exigir convergência multi-sinal para tudo **mataria o único objeto com decisão de negócio
defensável** do acervo.

Um vencimento regulatório tem, por natureza, **uma** fonte: a autoridade nacional. Não pode
ter duas — e não deveria. Sob a regra antiga, os 155 registros italianos ficariam para
sempre fora da fila, enquanto um caso de campo com uma família também ficaria. **A régua
reprovava tudo, inclusive o que estava certo.**

**Convergência continua valendo — como força adicional, onde for semanticamente
aplicável.** E a regra dela não afrouxou nada:

```
CONVERGENCE_REQUIRES = SAME_PROPOSITION + INDEPENDENT_EVIDENCE
```

---

## 2 · O PORTÃO — cinco requisitos, conjuntivos

Faltando **um**, o objeto não é `ATTENTION_READY`.

| requisito | o que é | falha se |
|---|---|---|
| **`VALID_EVIDENCE`** | evidência preservada, rastreável até a fonte original | só há derivação, ou o corpo não está preservado |
| **`OBJECT_SPECIFIC_TRIGGER`** | o gatilho **daquele** tipo — não um gatilho universal | não há *o que mudou*; captura única não produz gatilho |
| **`TIME_RELEVANCE`** | há tempo organizacional para agir, ou a data é futura e publicada | janela `NOT_READY` **e** sem prazo futuro |
| **`DECISION_QUESTION`** | a pergunta está escrita e é respondível | a pergunta não muda nenhuma decisão |
| **`DECISION_OWNER`** | departamento dono, derivado do caso | nenhum dono defensável → `NO_DEFENSIBLE_ACTION_YET` |

### O gatilho é por tipo — e é aqui que o produto trava hoje

| tipo | gatilho |
|---|---|
| `PHENOMENON_CASE` | observação de campo com as cinco âncoras **no corpo** |
| `REGULATORY_DEADLINE` | prazo futuro publicado pela autoridade |
| `COMPETITOR_IDENTITY_CHAIN` | **mudança** na cadeia entre duas leituras com intervalo real |
| `LONGITUDINAL_FIELD_PRESSURE` | leitura nova que muda a **posição relativa** de uma região |

---

## 3 · OS TRÊS TIPOS DE CONVERGÊNCIA — nunca somam

| tipo | afirma | conta como convergência? |
|---|---|---|
| **`PHENOMENON_CONVERGENCE`** | duas famílias independentes afirmam **o mesmo fenômeno** | **sim** |
| **`IDENTITY_CONVERGENCE`** | duas ou mais fontes sustentam a mesma **identidade** | **sim, para o tipo de identidade** |
| **`CONTEXTUAL_ALIGNMENT`** | uma fonte dá **contexto** à outra | **não** |

**O exemplo que motivou a distinção:**

```
"Fusarium observado em trigo duro em Grosseto"          ← observação de campo
"produto autorizado para trigo duro × Fusarium"          ← registro nacional
```

Parecem duas pernas. **Não são.** O segundo oferece contexto de portfólio — **não confirma
que o fenômeno de campo existe**. Sem esta lei, o caso italiano viraria "2 pernas" no minuto
em que o registro ganhasse cultura × alvo, **sem nenhuma observação nova de campo**.

---

## 4 · A MÁQUINA DE ESTADOS

```
NEEDS_EVIDENCE
      │  VALID_EVIDENCE passa
      ▼
VALID_EVIDENCE_NOT_ATTENTION_READY ◄──────────┐
      │  OBJECT_SPECIFIC_TRIGGER passa        │  a janela fecha, ou o dono
      ▼                                        │  deixa de existir
ATTENTION_CANDIDATE_TEST                       │
      │  TIME_RELEVANCE + DECISION_QUESTION    │
      │  + DECISION_OWNER passam               │
      ▼                                        │
ATTENTION_READY ───────────────────────────────┘
      │  a decisão foi tomada, ou o ciclo passou
      ▼
ARCHIVED_HISTORICAL
```

**E uma transição de volta que já aconteceu de verdade:**
`VALID_EVIDENCE_NOT_ATTENTION_READY → NEEDS_EVIDENCE`, quando um guard derruba a evidência
que sustentava. Foi o que o `SIDEBAR_NOT_BODY` fez com o `DOWNY_MILDEW` de itens franceses:
o termo estava na **barra lateral**, não no corpo.

> **Rebaixar nunca é retrocesso.**

---

## 5 · `VALID_EVIDENCE_NOT_ATTENTION_READY` — um estado com dignidade

**Não é lixo. Não é "quase".** É evidência real, verificada, que ainda não responde *por que
agora*.

Hoje seis objetos estão nele — incluindo o RAIF, que tem 23 safras de série e um backtest
honesto, e a série de recortes territoriais parciais. **Um produto que jogasse isso fora
estaria descartando o material do qual a atenção futura vai nascer.**

---

## 6 · A REGRA DA HOME

```
MOSTRA PRIORITARIAMENTE   ATTENTION_READY
PODE MOSTRAR              ATTENTION_CANDIDATE_TEST, com rótulo explícito de teste
NUNCA MOSTRA              VALID_EVIDENCE_NOT_ATTENTION_READY como se fosse atenção
```

> **Se a fila estiver vazia, dizer que está vazia.** Fila vazia é resultado, não falha de
> interface. Preencher com candidato sem rótulo seria **fabricar atenção** — que é o oposto
> exato do que o produto existe para fazer.

---

## 7 · O ESTADO MEDIDO HOJE

```
ATTENTION_READY ............................ 0
ATTENTION_CANDIDATE_TEST ................... 3
VALID_EVIDENCE_NOT_ATTENTION_READY ......... 6
```

**Por que zero pronto:** nenhum candidato responde `OBJECT_SPECIFIC_TRIGGER`. Nenhuma
camada tem **duas leituras com intervalo real** — a Meta tem uma hora, o territorial tem
captura única, o Foresight tem uma captura, o RAIF tem série anual sem leitura intra-safra.

**O que destrava:** uma segunda leitura com intervalo real em **qualquer** camada. Não é
fonte nova; é ler de novo, depois.

**É a coisa mais importante deste documento.** O produto não está travado por falta de
dado — está travado por falta de **segunda medição no tempo**. E "o que mudou?" é a pergunta
que a atenção inteira depende.
