# TOP ATTENTION ITEMS — V2

**Data:** 2026-08-31 · derivado de `data/refresh-corrected/ATTENTION-CANDIDATES.json`

```
ATTENTION_READY .............................. 0
ATTENTION_CANDIDATE_TEST ..................... 3
VALID_EVIDENCE_NOT_ATTENTION_READY ........... 6
```

> **Nenhum item foi promovido automaticamente.** RAIF, vencimentos regulatórios e cadeias
> de identidade foram **avaliados** — e nenhum passou para `ATTENTION_READY`.

---

## 0 · POR QUE ZERO PRONTO

`ATTENTION_READY` exigiria as sete respostas cheias: *o que mudou · por que agora · que
decisão muda · quem é dono · ainda há tempo · qual a evidência · o que não está provado*.

**Nenhum candidato responde "o que mudou".** Nenhuma camada tem duas leituras com intervalo
real: a Meta tem uma hora, o territorial tem captura única, o Foresight tem uma captura, o
RAIF tem série anual sem leitura intra-safra.

**Sem "o que mudou", não há "por que agora".** E sem "por que agora", é evidência válida —
não é fila de atenção.

---

## CANDIDATO 1 · `IT × Grosseto × trigo duro × fusarium` — `ATTENTION_CANDIDATE_TEST`

| | |
|---|---|
| **WHAT** | fusariose com sintomas leves em trigo duro, observada no boletim |
| **WHERE** | Toscana · província de Grosseto |
| **WHY_NOW** | **não respondido** — captura única, sem segunda leitura |
| **INDEPENDENT_EVIDENCE** | **1 família** (TERRITORIAL). A citação correta está anexada |
| **TIME_CONTEXT** | estágio **na observação** PROVADO · gatilho **na observação** PROVADO · estágio de hoje `NOT_PROVED` · janela de hoje `NOT_PROVED` · próxima safra `NOT_ENOUGH_TIME_CONTEXT` |
| **ADAMA_LOCAL_CONTEXT** | `NOT_MEASURED` — o registro italiano não tem cultura × alvo reconstruído |
| **COMPETITOR_CONTEXT** | 10 tuplas italianas de identidade, **sem cultura e sem problema** |
| **WHO_OWNS_THE_DECISION** | TÉCNICO / AGRONOMIA (validar) · MARKET DEVELOPMENT (programar) |
| **WHAT_DECISION_COULD_CHANGE** | se o par entra no piloto e se a fonte LAMMA vira rota recorrente |
| **WHAT_REMAINS_UNKNOWN** | segunda família · resposta ADAMA local · se o sinal se repete |

```
IS THERE STILL TIME?   NOT_PROVED
```

**Não é `NO`, como o V1 escreveu.** O V1 concluiu "a floração passou" projetando o
calendário de 2026 sobre 2027 — isso é fabricar janela. O que se sabe: a fonte publicou em
**23/04**, o sistema leu em **31/08**, e o boletim declara gatilho de tratamento **naquela
data**. Sobre hoje, o acervo não diz nada.

---

## CANDIDATO 2 · Vencimentos regulatórios ADAMA na Itália — `ATTENTION_CANDIDATE_TEST`

| | |
|---|---|
| **WHAT** | 155 registros ADAMA em vigor com vencimento futuro |
| **WHERE** | Itália, nacional |
| **CROP / ISSUE** | `NOT_APPLICABLE` — o objeto não é de fenômeno |
| **WHY_NOW** | a data é **pública e futura**: é a única antecipação que não depende de previsão |
| **INDEPENDENT_EVIDENCE** | 1 família (`NATIONAL_REGISTRY`), fonte oficial primária |
| **TIME_CONTEXT** | 20 próximos vencimentos listados no artefato |
| **WHO_OWNS_THE_DECISION** | **REGULATÓRIO** (dono) · PORTFÓLIO |
| **WHAT_DECISION_COULD_CHANGE** | quais registros entram em revisão de renovação, e em que ordem |
| **WHAT_REMAINS_UNKNOWN** | se a renovação já está em curso — **dado interno, que não virá** |

```
IS THERE STILL TIME?   YES — mas para REVISÃO, não para alarme.
EXPIRY ≠ WITHDRAWAL    ·   EXPIRY_DATE_REACHED ≠ PRODUCT_DISCONTINUED
```

**Por que não é `ATTENTION_READY`:** 155 registros não são 155 itens de atenção. Falta a
régua que diz **quais** merecem revisão — e essa régua é decisão de produto, não medição.

---

## CANDIDATO 3 · Cadeias de identidade de concorrente — `ATTENTION_CANDIDATE_TEST`

| | |
|---|---|
| **WHAT** | 36 tuplas com marca + registro local + anúncio observado, mesmo titular e país |
| **WHERE** | ES 22 · IT 10 · FR 4 |
| **CROP / ISSUE** | `NOT_APPLICABLE` |
| **WHY_NOW** | **não respondido** — uma captura, sem série |
| **INDEPENDENT_EVIDENCE** | `IDENTITY_CONVERGENCE`, **não** convergência de fenômeno |
| **WHO_OWNS_THE_DECISION** | MARKET DEVELOPMENT · PORTFÓLIO |
| **WHAT_DECISION_COULD_CHANGE** | se vale reconstruir cultura × alvo para amarrar isto a casos |
| **WHAT_REMAINS_UNKNOWN** | investimento · venda · participação · sucesso · se o produto anunciado está autorizado ali · se a página é daquele país |

```
IS THERE STILL TIME?   NOT_PROVED
```

---

## O QUE FOI AVALIADO E **NÃO** PROMOVIDO

| candidato | estado | por quê |
|---|---|---|
| **RAIF · repilo no olivar** | `VALID_EVIDENCE_NOT_ATTENTION_READY` | o próprio backtest diz: **11 falsos positivos em 14 disparos**, e no melhor caso uma safra de antecedência. Evidência boa, atenção não |
| `FR_VINE_DOWNY_MILDEW` | `VALID_EVIDENCE_NOT_ATTENTION_READY` | o problema **sobrevive em 4 itens**; falta **localidade** em 7 de 11 |
| `ES_OLIVE_REPILO` territorial | `VALID_EVIDENCE_NOT_ATTENTION_READY` | 10 itens, **zero** com o problema no corpo |
| `ES_CEREAL_SEPTORIA` · `IT_VINE_FLAVESCENCE` · `FR_CEREAL_SEPTORIA` | `VALID_EVIDENCE_NOT_ATTENTION_READY` | o problema não fecha no corpo |
| 10 entidades de creator | não é item de atenção | é **oferta**. Vira atenção amarrada a um caso |
| 22 contas de concorrente | não é sinal | identidade congelada, conteúdo `NOT_STARTED` |

**`VALID_EVIDENCE_NOT_ATTENTION_READY` é um estado com dignidade.** Não é lixo, não é
"quase". É evidência real que ainda não responde *por que agora*.

---

## A PERGUNTA, RESPONDIDA SEM ENFEITE

> **Esta inteligência pode mudar uma decisão enquanto ainda existe tempo para agir?**

```
CANDIDATO 1 (fusarium IT) ......... NOT_PROVED
CANDIDATO 2 (vencimentos IT) ...... YES, para revisão regulatória
CANDIDATO 3 (identidade) .......... NOT_PROVED
```

**Um `YES`, e ele é o mais modesto dos três** — porque a data é publicada, não prevista.
Foi o que sobreviveu a duas passagens de correção.
