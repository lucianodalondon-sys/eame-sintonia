# MODELO FINAL DE CADÊNCIA — SINTONIA EAME

**Data:** 2026-08-31 · **nenhum agendamento implementado**

```
DAILY_PRODUCT_CLAIM = NO          SOURCE_SPECIFIC_CADENCE = YES
```

---

## 1 · A DECISÃO

**O produto não se declara diário nem semanal.** Nenhum dos dois é verdade universal, e
declarar qualquer um seria uma promessa que o dado não sustenta.

O modelo é:

```
CADÊNCIA POR FONTE / POR OBJETO   +   MUDANÇA DE ESTADO (event-driven)
```

Um **digest de leitura** pode ser periódico — para caber na rotina de quem lê. Mas o digest
**não define a cadência do dado**, e confundir os dois é o que faz um produto começar a
fabricar sinal para preencher a periodicidade.

> **`COLLECTION CAN RUN DAILY` ≠ `DAILY INTELLIGENCE HAS VALUE`.**

---

## 2 · POR CAMADA

### REGULATÓRIO — **a mais forte, e a única que se aproxima de diária**

```
o que muda        a versão do dataset da autoridade nacional
cadência da fonte periódica, publicada pelo ministério
recomendação      verificar semanalmente a VERSÃO do dataset;
                  agir por MUDANÇA DE ESTADO, não por calendário
valor diário      PARCIAL — só perto de data-limite
```

**Por que é a mais forte:** o vencimento é uma **data pública futura**. A antecipação não
depende de previsão — depende de alguém ter lido a lista. Foi medido: 155 registros ADAMA
em vigor com vencimento futuro na Itália.

### TERRITORIAL — **a cadência da fonte não é o gargalo; a captura é**

```
cadência da fonte boletins semanais na safra
medido            latência de 56 a 172 dias (FR) e 130 dias (IT)
recomendação      leitura semanal na janela da cultura
valor diário      NOT_PROVED
```

⚠️ **O gargalo é a captura, não a publicação.** As fontes publicam semanalmente; o sistema
leu com meses de atraso. Aumentar a cadência de leitura sem consertar isso mediria o
pipeline, não o campo.

### CIÊNCIA — **mensal, e sem pressa**

```
cadência da fonte publicação indexada, ritmo mensal
recomendação      leitura mensal
valor diário      NOT_PROVED — e não vale a pena tentar
```

Um artigo novo não muda uma decisão de campo em 24 horas. Ler diariamente aqui é custo sem
retorno.

### META — **mecanismo provado, cadência não medida**

```
capacidade        SNAPSHOT_CAPABILITY = PROVED
                  TEMPORAL_COMPARISON_MECHANISM = PROVED (60 de 67 recortes)
valor operacional OPERATIONAL_TEMPORAL_SIGNAL_VALUE = NOT_PROVED
janela medida     cerca de UMA HORA entre os dois snapshots
recomendação      NÃO recomendar cadência ainda
```

**Uma janela de uma hora prova que o mecanismo compara. Não prova que a cadência diária
produz sinal útil.** Provar isso exigiria uma terceira coleta com intervalo real — e
declarar cadência antes disso seria inventar.

### CREATOR — **por janela, não por dia**

```
medido            442 materiais · 164 nos últimos 90 dias · 10 alvos
janelas nativas   30 e 90 dias
recomendação      revalidação por JANELA, não por dia
valor diário      NOT_PROVED — audiência não medida em quase ninguém
REVALIDATION_RULE NOT_YET_DEFINED, de propósito
```

**A regra de revalidação continua indefinida por decisão da própria missão:** a cadência de
publicação varia por pessoa, cultura e estação. Um *"vale 90 dias"* seria precisão que nada
sustenta. A ficha entrega o que foi medido e quando; quem usa decide se precisa remedir.

### FIELD HISTORICAL (RAIF) — **anual hoje, intra-safra é o que melhoraria**

```
cadência preservada  média anual por safra
cadência da fonte    a fonte publica semanalmente na safra
recomendação         leitura INTRA-SAFRA
valor diário         NOT_PROVED
```

**O próprio backtest aponta o caminho:** o que melhoraria a antecedência é a leitura
intra-safra — e o campo 1703, de repilo **incubado**, que a série anual não usa.

---

## 3 · QUADRO

| camada | cadência da fonte | leitura recomendada | valor diário |
|---|---|---|---|
| **Regulatório** | periódica | semanal + evento | **PARCIAL** |
| **Territorial** | semanal na safra | semanal na janela | `NOT_PROVED` |
| **Ciência** | mensal | mensal | `NOT_PROVED` |
| **Meta** | contínua | **não recomendar ainda** | `NOT_PROVED` |
| **Creator** | contínua | por janela 30/90d | `NOT_PROVED` |
| **Field Historical** | semanal na safra | intra-safra | `NOT_PROVED` |

```
DAILY_INTELLIGENCE_VALUE = NOT_PROVED em todas, PARCIAL no regulatório
```

---

## 4 · O QUE GOVERNA A FILA: MUDANÇA DE ESTADO

A cadência de leitura enche o acervo. **O que enche a fila de atenção é outra coisa: a
mudança de estado de um objeto.**

```
NEEDS_EVIDENCE → VALID_EVIDENCE_NOT_ATTENTION_READY → ATTENTION_CANDIDATE_TEST
→ ATTENTION_READY
```

Um objeto que não muda de estado **não volta para a fila**, por mais que a coleta rode. É
isso que permite um produto honesto sem sinal diário: **a fila responde a mudança, não a
calendário.**

E é também o motivo de `ATTENTION_READY = 0` hoje: **nenhuma camada tem duas leituras com
intervalo real**, então nada mudou de estado — porque não houve segundo estado para comparar.

---

## 5 · O QUE NÃO SE FAZ

```
não declarar o produto DAILY nem WEEKLY como verdade universal
não deixar o digest de UX definir a cadência do dado
não recomendar cadência para a Meta antes de uma leitura com intervalo real
não aumentar a cadência territorial antes de consertar a captura
não implementar scheduling nesta rodada
```

**`SCHEDULING_IMPLEMENTED = NO`.**
