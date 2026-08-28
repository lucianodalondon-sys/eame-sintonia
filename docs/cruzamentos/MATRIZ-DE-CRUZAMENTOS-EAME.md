# MATRIZ DE CRUZAMENTOS — SINTONIA EAME

O valor do SINTONIA não está em nenhuma fonte isolada: está no que **duas ou mais fontes
juntas** revelam e nenhuma delas revela sozinha.

> **Não afirmar cruzamento apenas porque semanticamente parece interessante.**
> Clima + doença "parece" cruzar. A pergunta real é: **qual chave os une?**

**Estado:** Fase 0 — estrutura pronta, **0 cruzamentos testados**.
**Última atualização:** 2026-08-28

---

## AS DUAS PERGUNTAS

Para cada cruzamento candidato:

1. **A + B realmente podem ser unidos?**
2. **Qual chave permite uni-los?**

Sem chave explícita e verificada, o cruzamento não é COMPROVADO. As chaves candidatas
costumam ser: geografia (região/NUTS/coordenada), tempo (data/janela), cultura, alvo
(praga/doença), substância ativa, produto, organização, pessoa, identificador de documento.

Atenção ao alinhamento das chaves: duas fontes podem ambas ter "região" e mesmo assim não
cruzar, se uma usa NUTS-2 e a outra departamento, ou se uma é semanal e a outra mensal.
**Granularidade incompatível é motivo legítimo de NÃO COMPÕE.**

---

## CLASSIFICAÇÃO

| Classe | Significado |
|---|---|
| **COMPROVADO** | Cruzamento executado sobre dado real, com chave identificada e exemplo preservado. |
| **POSSÍVEL MAS NÃO TESTADO** | Chave plausível e identificada, mas ninguém executou ainda. |
| **NÃO COMPÕE** | Testado e não une — chave ausente, granularidade incompatível, tempos irreconciliáveis. Exige motivo escrito. |
| **NÃO SEI** | Não foi possível avaliar. |

---

## FICHA DO CRUZAMENTO

```
CROSSING_ID:
COMPONENTS:         # A + B (+ C...)
SOURCES:            # SOURCE_IDs envolvidos
KEY:                # a chave que efetivamente une — ou por que não existe
GRANULARITY_MATCH:  # geografias e tempos são compatíveis?
WHAT_IT_REVEALS:    # o que aparece que nenhuma fonte sozinha mostra
REAL_EXAMPLE:
CAPABILITY:         # que capacidade este cruzamento habilita
CLASS:              # COMPROVADO | POSSÍVEL MAS NÃO TESTADO | NÃO COMPÕE | NÃO SEI
```

---

## CRUZAMENTOS CANDIDATOS (do briefing)

Listados como **candidatos a testar**, não como afirmações. Todos partem em `NÃO SEI`.

| ID | Cruzamento | Classe |
|---|---|---|
| X-001 | CLIMATE + REGION + CROP + DISEASE ALERT | NÃO SEI |
| X-002 | RESEARCHER + PAPER + CROP + PROBLEM | NÃO SEI |
| X-003 | COMPETITOR + PRODUCT + CROP + COMMUNICATION | NÃO SEI |
| X-004 | REGULATORY + ADAMA PORTFOLIO + CROP + PEST | NÃO SEI |

> X-004 depende de acesso ao portfólio da ADAMA EAME, que hoje é **NÃO SEI**
> (pergunta pendente P-003 no diário de decisões).

---

## REGISTRO DE CRUZAMENTOS TESTADOS

*(vazio)*

### Placar

| Classe | Quantidade |
|---|---|
| COMPROVADO | 0 |
| POSSÍVEL MAS NÃO TESTADO | 0 |
| NÃO COMPÕE | 0 |
| NÃO SEI | 4 |
