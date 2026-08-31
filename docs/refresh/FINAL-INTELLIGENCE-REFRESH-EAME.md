# ONE FINAL INTELLIGENCE REFRESH — SINTONIA EAME

**Data:** 2026-08-31 · **Branch:** `claude/eame-one-final-intelligence-refresh`
**Base funcional:** `1b491217e9a10501963e654e5fcc7622da5ba0b8`

```
MANDATORY_HANDOFFS_ACCEPTED = 4/4
FINAL_REFRESH_EXECUTED      = YES
FINAL_TOOL_SET_DECIDED      = NO
CASCO_V7_MODIFIED           = NO
REAL_DATA_WIRED             = NO
```

> **Rodada de inteligência e produto. Não de coleta.** Nenhuma execução paga, nenhuma
> fonte nova, custo zero. Toda entrada foi lida por `git show` sobre **commit fixo** —
> nunca pela ponta de uma branch.

| artefato | o que é |
|---|---|
| `data/refresh/SIGNAL-DEPENDENCY-GRAPH.json` | quem depende de quem — **vem antes de qualquer convergência** |
| `data/refresh/FINAL-INTELLIGENCE-REFRESH-EAME.json` | o refresh derivado, com os casos |
| `scripts/refresh_final.py` | o gerador — nenhum número digitado à mão |

---

## 0 · A RESPOSTA CURTA, ANTES DA LONGA

Com **4/4 handoffs aceitos**, o acervo sustenta hoje:

```
CASE CANDIDATES com chave completa (país × região × cultura × problema × tempo) ....... 1
   e esse um tem UMA família de sinal independente, não duas .......... SINGLE_SIGNAL
MULTI_SIGNAL_CONVERGENCES ............................................................ 0
PARTIAL_CONVERGENCES ................................................................. 0
recortes territoriais com lastro parcial (falta o problema) .......................... 5
```

E, numa **unidade diferente** que não entra na chave de caso:

```
observações de produto de concorrente com cadeia de três camadas provada
   36 tuplas  ·  29 produtos  ·  ES 22 · IT 10 · FR 4  ·  de 174 candidatas
```

**Zero convergência multi-sinal não é fracasso de coleta.** É o resultado de aplicar o
grafo de dependências antes de contar. Sem ele, este documento teria anunciado três ou
quatro "convergências" que são a mesma evidência vista de ângulos diferentes.

---

## 1 · ENTRADAS FIXADAS POR COMMIT

### As quatro obrigatórias

| # | entrada | commit | estado |
|---|---|---|---|
| 1 | **CREATOR MAP** | `248bd27027506a5f531a117ce50d35eb5304b152` | `ACCEPTED` |
| 2 | **COMPETITOR FORESIGHT** | `dc32ce0` (freeze original `25194e3`) | `ACCEPTED` · linhagem corrigida |
| 3 | **EARLY SIGNAL TERRITORIAL** | dado `11fd7b54…` · handoff `4ea268d0…` | `PARTIAL` · handoff pronto |
| 4 | **META COMPETITOR** | dado `acfd987` · handoff `a2fad2d` | `ACCEPTED` · `PARKED` |

**Sobre o handoff da Meta:** o dado congela em `acfd987`, mas a declaração do freeze só
pôde nomear o próprio commit depois — a versão final do `META-HANDOFF-FREEZE-V1.json` está
em **`a2fad2d`**. Fixei os dois, como a própria missão Foresight fez. Blobs registrados no
JSON do refresh.

### As opcionais

| entrada | commit | estado | consumida? |
|---|---|---|---|
| **CREATOR DEEP CORPUS** | `a509c12` | `READY_WITH_LIMITATIONS` | **sim** |
| **MULTILINGUAL CONTRACT** | `1443f643…` | `ACCEPTED_FROZEN` | sim — como **guardrail**, não sinal |
| **COMPETITOR PUBLIC COMM** | `c25e44b` | identidade congelada, conteúdo `NOT_STARTED` | **não como sinal** — só como rota futura |
| **EXPERT / RESEARCHER** | — | **`NOT_CANONICAL`** | **não** — ver 1.1 |
| **LOCAL ADAMA PORTFOLIO / REGULATORY** | — | canônico por país, mas ver 1.2 | parcialmente |

### 1.1 · Expert / Researcher — `OPTIONAL_INPUT_STATE = NOT_CANONICAL`

Procurei handoff aceito posterior que corrigisse a expertise por caso. **Não existe.**
Portanto, e sem exceção:

```
ES × OLIVE × REPILO   CASE_EXPERTISE = NOT_PROVED
```

Os dois pesquisadores originais **não voltam** como especialistas de repilo. A medição que
os derrubou continua valendo: 42 e 27 obras no corpus, **zero** com termo de repilo no
título, e concentração real em Xylella e Verticillium. **Nenhum item de TOP ATTENTION usa
expertise como prova.**

### 1.2 · Portfólio / regulatório local — o que NÃO fiz

Não coletei e não inferi. O que existe por país continua canônico, e **`FR ≠ ES ≠ IT`**:
nenhum produto ou autorização foi herdado entre países. Onde o par cultura × alvo não
existe no dataset nacional, o estado é **`NOT_MEASURED`** — e é o caso de todos os três
para a junção com a camada de concorrente (ver 3.2).

---

## 2 · O GRAFO DE DEPENDÊNCIAS — o passo que veio primeiro

**`2 cards ≠ 2 independent signals`.**

Doze relações mapeadas. **Nove são de dependência**, três são independência real.

### As cinco armadilhas de dupla contagem, e o guard de cada uma

| # | armadilha | guard |
|---|---|---|
| 1 | a cadeia de três camadas do Foresight **contém** o anúncio da Meta | `DERIVED_DEPENDENCY_ON_META` |
| 2 | a perna de registro do Foresight lê **as mesmas bases nacionais** que o regulatório e o portfólio local | `SHARED_REGISTRY_NOT_TWO_FAMILIES` |
| 3 | o Deep Corpus lê o conteúdo das identidades que o **Creator Map** resolveu | `SAME_ENTITY_DIFFERENT_OBSERVATION` |
| 4 | listagem e corpo territorial são **duas leituras do mesmo documento** | `SAME_DATA_DIFFERENT_VIEW` |
| 5 | 22 contas oficiais provadas **sem conteúdo coletado** | `IDENTITY_IS_NOT_SIGNAL` |

E uma sexta, que o próprio handoff da Meta declara: os dois snapshots leem **as mesmas
páginas com cerca de uma hora de distância**. Dois instantes da mesma fonte, não duas
fontes.

### Famílias de sinal — e quais podem contar hoje

```
CONTAM        TERRITORIAL · SCIENCE_RESEARCHER · NATIONAL_REGISTRY · TRADEMARK
              META_PAID_ADS · CREATOR
NÃO CONTA     COMPETITOR_PUBLIC_COMM   (identidade sem conteúdo)
DECLARADA     FIELD_HISTORICAL (RAIF)  — canônica em árvore, fora da lista do coordenador;
                                         declarada, não consumida como prova
```

**`SCIENCE` e `RESEARCHER` são UMA família**, não duas: saem do mesmo OpenAlex.
**`CREATOR_MAP` e `DEEP_CORPUS` são UMA família**, com duas observações da mesma entidade.

---

## 3 · O QUE OS DADOS SUSTENTAM

### 3.1 · Territorial — a chave completa fecha uma vez

```
itens únicos com corpo analisado ........ 22
  com país .............................. 22 / 22
  com localidade ........................ 15 / 22
  com cultura ........................... 21 / 22
  com problema ........................... 5 / 22
  com tempo ............................. 12 / 22
  país + cultura + problema .............. 5 / 22
  país + cultura + problema + tempo ...... 4 / 22
  CHAVE TERRITORIAL COMPLETA ............. 1 / 22
```

**O problema é o gargalo, não a cobertura.** Cultura fecha em 21 de 22; problema, em 5.
E os guards derrubaram parte do que parecia sinal: `SIDEBAR_NOT_BODY` removeu
`DOWNY_MILDEW` de quatro itens franceses — o termo estava na **barra lateral** da página,
não no corpo do boletim. `ORG_NAME_NOT_LOCALITY` removeu uma região que era nome de
organização. `BINARY_NOT_DOCUMENT` descartou um "documento" de 27 milhões de caracteres.

**Sem esses guards, a França teria entrado neste refresh com míldio da videira sustentado
por um menu de navegação.**

### 3.2 · Concorrente — real, e de outra unidade

```
candidatas ......... 174 tuplas (competidor × país × produto normalizado)
provadas ............ 36 tuplas · 29 produtos
recusadas ............ 0
não sabidas ........ 138   (89 sem marca e sem registro · 49 sem registro local provado)
por país ........... ES 22 · IT 10 · FR 4
por empresa ........ BASF 23 · BAYER 7 · CORTEVA 4 · UPL 2
URBOLE_GUARD ....... PASS, exercido por mutação
```

⚠️ **Nada disto entra num caso.** Nenhum dos três registros nacionais traz **cultura ×
alvo** neste dataset. Sem `CROP` e `ISSUE`, a observação não encaixa na chave
`país × região × cultura × problema × tempo`. Ela é verdadeira e é de **outra unidade**.

**Este é o bloqueador estrutural número um do produto.** A camada de concorrente é a mais
rica que o projeto tem — e é a que menos consegue conversar com o caso.

### 3.3 · Meta — mecanismo provado, valor operacional não

```
SNAPSHOT_CAPABILITY .................................... PROVED
TEMPORAL_COMPARISON_MECHANISM .......................... PROVED
TEMPORAL_COMPARISON (recortes comparáveis) ............. PROVED — 60 de 67
OPERATIONAL_TEMPORAL_SIGNAL_VALUE ...................... NOT_PROVED
DAILY_INTELLIGENCE_VALUE ............................... NOT_PROVED
FULL_LIFECYCLE_STATE_CAPABILITY ........................ NOT_PROVED
```

A janela entre os dois snapshots é de **cerca de uma hora**. Isso prova que o mecanismo
compara; **não** prova que a cadência diária produz sinal útil.

E a lei que precisa viajar: **`PAGE_COUNTRY_SCOPE ≠ AD_DELIVERY_COUNTRY`**. Das 23 páginas
provadas, **1** tem escopo de país provado e **22** ficam `NOT_PROVED`. Entrega de anúncio
num país **não** prova nacionalidade da página.

### 3.4 · Creator — rota de ativação, não evidência de problema

```
PERSON_CREATOR_ACTIVATION_READY .......... 8
FARM_BUSINESS_PARTNER_READY .............. 2
MARKETING_CONTACTABLE_ENTITIES_READY .... 10     ← a soma NUNCA se chama CREATORS_READY
corpus profundo ......................... 442 materiais · 280 nos últimos 90 dias
problema observado no conteúdo .......... WEED 6 · PEST 16 · DISEASE 5
```

O corpus classifica problema **na altura da linha de produto**, nunca no problema nomeado.
**Nenhuma ficha sustenta `FUSARIUM`, `REPILO` ou `SEPTORIA`.**

```
CREATOR_ACTIVATION_ROUTE       ≠  CREATOR_ISSUE_EVIDENCE
COUNTRY + CROP CREATOR         ≠  ISSUE-SPECIFIC CREATOR
```

Isso **não** reduz o valor do Creator Map: ele responde *"quem o Marketing pode avaliar?"*,
que é outra pergunta — e responde com dez entidades contactáveis.

---

## 4 · CASE CANDIDATES

**Seis.** Não forcei número: um com chave completa, cinco parciais.

### `REFRESH-CASE-001` · IT × Toscana × TRIGO DURO × FUSARIUM

```
COUNTRY  IT              PROVED        CROP   DURUM_WHEAT   PROVED
REGION   Toscana         PROVED        ISSUE  FUSARIUM      PROVED
TIME     2026-04-23      PROVED
```

| | |
|---|---|
| **famílias independentes** | **1** — `TERRITORIAL` |
| **evidência** | IT-LAMMA, boletim agrometeo de Grosseto, com o problema no **corpo** |
| **classe** | `SINGLE_SIGNAL` |
| **o que prova** | a única observação territorial de todo o acervo com as cinco âncoras no corpo do documento, e não no índice |
| **o que não prova** | nenhuma segunda família confirma · expertise no problema `NOT_PROVED` · creator específico `NOT_PROVED` · janela agronômica inexistente · resposta ADAMA local `NOT_MEASURED` |

⚠️ **O tempo derruba a acionabilidade.** O boletim é de **23/04/2026**; hoje é **31/08/2026**
— **130 dias**. Fusarium em trigo duro se decide na floração, entre abril e maio. A janela
desta safra passou.

```
WINDOW_STATE = NOT_READY        (não há relógio de lavoura conectado)
TIME_ANSWER  = PLAN_NEXT_CYCLE  (não ACT_NOW, e dizer ACT_NOW seria fabricar)
```

### `REFRESH-PARTIAL-002…006` — os cinco recortes sem problema

`ES_OLIVE_REPILO` · `ES_WHEAT_SEPTORIA` · `IT_VINE_FLAVESCENCE` · `FR_VINE_DOWNY_MILDEW` ·
`FR_WHEAT_SEPTORIA`

Em todos: país, cultura e tempo provados; **problema não sustentado pelo corpo**.
`CONVERGENCE_CLASS = NOT_ENOUGH_EVIDENCE`. O que mudaria isso é uma coisa só: **o problema
nomeado no corpo de um documento**.

---

## 5 · O QUE MUDOU DESDE A PASSAGEM 1

| afirmação da PASSAGEM 1 | agora |
|---|---|
| *"3 convergências fortes / 6 no total"* | **retirada** — foi contada antes do grafo de dependências; a maioria eram famílias dependentes |
| *"IT videira × flavescência: convergência 5/5"* | **rebaixada** — territorial não sustenta o problema; as "5 pernas" incluíam registro e portfólio, que compartilham a mesma base nacional |
| *"ES olivar × repilo: convergence forming"* | **rebaixada** — territorial `PARTIAL`, expertise `NOT_PROVED` |
| *"FR videira × míldio: partial convergence"* | **rebaixada** — o `DOWNY_MILDEW` francês veio de **barra lateral**, e o guard o removeu |
| Meta *"nunca testada"* | **superada** — `ACCEPTED`, com mecanismo provado e valor operacional não provado |

**Cinco das seis afirmações de convergência da primeira passagem não sobreviveram ao grafo
de dependências.** Isso é o grafo funcionando, não o acervo encolhendo.

---

## 6 · ESTADO FINAL

```
CASE_CANDIDATES               = 6
MULTI_SIGNAL_CONVERGENCES     = 0
PARTIAL_CONVERGENCES          = 0
SINGLE_SIGNAL_CASES           = 1
NOT_ENOUGH_EVIDENCE_CASES     = 5

DEPENDENCY_GRAPH              = PASS
DOUBLE_COUNT_GUARDS           = PASS

MULTILINGUAL_CONTRACT_PRESERVED          = YES
ADAMA_DISEASE_ICON_REQUIREMENT_PRESERVED = YES
```

Documentos irmãos: [`CONVERGENCES-EAME.md`](CONVERGENCES-EAME.md) ·
[`TOP-ATTENTION-ITEMS-EAME.md`](TOP-ATTENTION-ITEMS-EAME.md) ·
[`ACTION-MAP-EAME.md`](ACTION-MAP-EAME.md) ·
[`TOOL-CANDIDATES-EAME.md`](TOOL-CANDIDATES-EAME.md) ·
[`CAPABILITIES-THAT-SHOULD-NOT-BECOME-TOOLS.md`](CAPABILITIES-THAT-SHOULD-NOT-BECOME-TOOLS.md) ·
[`RED-TEAM-PACK-SINTONIA-EAME.md`](RED-TEAM-PACK-SINTONIA-EAME.md)
