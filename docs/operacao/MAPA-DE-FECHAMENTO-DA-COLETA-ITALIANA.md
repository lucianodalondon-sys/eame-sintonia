# MAPA DE FECHAMENTO DA COLETA ITALIANA

> **Este ficheiro é DERIVADO.** Todo estado sai de
> `system-map/data/estradas-it.generated.json`, produzido por
> `python3 system-map/scripts/censo_das_estradas_it.py`.
> `tests/test_estradas_it.py` falha se algum número aqui divergir de lá.

---

## A — OS DOIS ATALHOS QUE A M1 REMOVEU

### 1 · Grep positivo não é aresta provada

`CONNECTED_TO_ROUTE` era um grep, e `ARCHITECTURE_CLOSED` aceitava o positivo
como ligação suficiente — enquanto o próprio censo escrevia que grep positivo
era frouxo. Reproduzido em `tests/fixtures/ARESTAS/`: um ficheiro cujo único
`derived_artifact` está num docstring devolvia o mesmo veredito de um que
consulta a tabela.

Agora há uma escada, e o degrau é medido por **AST** — não por texto:

| degrau | o que prova |
|---|---|
| `NO_CONNECTION_EVIDENCE` | o dono não menciona o artefato. **Grep negativo é prova.** |
| `CANDIDATE_CONNECTION` | menciona, mas só fora do código executável |
| `CODE_CONNECTED` | o código executável referencia o artefato |
| `TESTED_CONNECTION` | um teste faz o objeto atravessar a aresta |
| `OBSERVED_CONNECTION` | execução real, com recibo |

**`CODE_CONNECTED` é o degrau mínimo que fecha uma aresta.** `OBSERVED` não é
exigido: arquitetura e observação continuam eixos separados.

> Resultado honesto: hoje **nenhuma** aresta do modelo estava apoiada só em grep
> positivo. O conserto era necessário para a coerência do instrumento, e não
> mudou nenhum veredito de hoje.

### 2 · `provadas = 1` era um número escrito à mão

E `desconhecidas` derivava de `ACCESS_METHOD` — o que o **catálogo diz**, não a
rota que a fonte tem. A subtracção ainda supunha que uma fonte pertence a
exactamente uma estrada.

    SOURCE_VERDICT ≠ ACCESS_METHOD ≠ ROUTE_MEMBERSHIP.
    E: SOURCE 1:N ROUTES.

Agora cada pertença é um registro derivado de evidência preservada.

---

## B — A MATRIZ DAS ESTRADAS

Cada célula: `ESTADO·ligação`, onde a ligação é `cod` / `cand` / `sem`.

| ROUTE_CLASS | DISCOVER | FETCH | RAW | RUN | CHECKPOINT | DERIVED | STRUCTURED | ADMISSION | FECHADA | OBSERVAÇÃO | FALTA |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---|---|
| **RC-1 · OFFICIAL_HTTP_DOCUMENT** | Declared | Observed·cod | Observed·cod | Observed·cod | N/A | Observed·cod | Code·sem | Code·sem | **NÃO** | PARTIALLY_OBSERVED | STRUCTURED, ADMISSION |
| **RC-2 · YOUTUBE_OFFICIAL_API** | Observed·cod | Observed·cod | Localtest·cod | Code·sem | Dbtested·cod | N/A | Dbtested·cod | Code·sem | **NÃO** | PARTIALLY_OBSERVED | RUN, ADMISSION |
| **RC-3 · PUBLIC_NATIVE_API** | Localtest·cod | Localtest·cod | Localtest·cod | — | — | N/A | — | — | **NÃO** | NOT_OBSERVED | RUN, CHECKPOINT, STRUCTURED, ADMISSION |
| **RC-4 · SCIENCE_METADATA_API** | Localtest·cod | Localtest·cod | — | — | — | — | — | — | **NÃO** | NOT_OBSERVED | RAW, RUN, CHECKPOINT, DERIVED, STRUCTURED, ADMISSION |
| **RC-5 · REGULATORY_BULK_IMPORT** | — | — | — | Liveschem·cod | N/A | N/A | Liveschem·cod | — | **NÃO** | DB_TESTED | DISCOVER, FETCH, RAW, ADMISSION |
| **RC-10 · OFFICIAL_HTTP_DATASET** | — | — | Code·cod | Code·cod | — | N/A | — | — | **NÃO** | NOT_OBSERVED | DISCOVER, FETCH, CHECKPOINT, STRUCTURED, ADMISSION |
| **RC-11 · OFFICIAL_STATISTICAL_API** | — | — | — | — | — | N/A | — | — | **NÃO** | NOT_OBSERVED | DISCOVER, FETCH, RAW, RUN, CHECKPOINT, STRUCTURED, ADMISSION |

| ROUTE_CLASS | OBSERVAÇÃO | razão |
|---|---|---|
| **RC-6 · PUBLIC_BROWSER** | BLOCKED | robots/termos: zero capabilities permitidas na matriz |
| **RC-7 · LOCAL_SESSION** | BLOCKED | AUTOMATION_NOT_ALLOWED: sessao humana nao autoriza automacao |
| **RC-8 · PAID_FALLBACK** | BLOCKED | APIFY-LAST: zero rotas permitidas hoje na matriz |
| **RC-9 · GIT_LEDGER** | DEBT | estado operacional em Git, contra P-011. Nao e estrada a fechar: e divida a mover. |

| medida | valor |
|---|---:|
| `ROUTE_CLASSES_MODELED` | **11** |
| classes com ao menos uma pertença provada | **2** (RC-1, RC-9) |
| `ARCHITECTURE_CLOSED` | **0** |
| `OBSERVED` | **2** |
| `DB_TESTED` | **1** |
| `BLOCKED` | **3** |
| `DEBT` | **1** |
| `ROUTE_CLASSES_REQUIRED_TOTAL` | **UNKNOWN** |

---

## C — AS FONTES, POR PROVA DE ROTA

| medida | valor |
|---|---:|
| total no catálogo | 54 |
| `SOURCES_WITH_PROVEN_ROUTE` | **7** |
| `SOURCES_WITH_ONLY_CANDIDATE_ROUTE` | **12** |
| `SOURCES_ROUTE_UNKNOWN` | **35** |
| `SOURCES_BLOCKED` | **0** |

Dentro do desconhecido, dois casos diferentes: **26** respondem da Itália mas
não sabemos por onde se busca o documento (`REACHABLE_ROUTE_UNKNOWN`), e **9**
não têm nem isso.

### Pertenças

| medida | valor |
|---|---:|
| `TOTAL_PROVEN_MEMBERSHIPS` | **8** |
| `TOTAL_CANDIDATE_MEMBERSHIPS` | **18** |
| `TOTAL_BLOCKED_MEMBERSHIPS` | **0** |

| ROUTE_CLASS | provadas | candidatas | níveis de evidência |
|---|---:|---:|---|
| RC-1 · OFFICIAL_HTTP_DOCUMENT | 1 | 15 | DECLARED, EXPECTED, HISTORICALLY_OBSERVED, LIVE_FETCH_PROVEN |
| RC-9 · GIT_LEDGER | 7 | 0 | HISTORICALLY_OBSERVED |
| RC-10 · OFFICIAL_HTTP_DATASET | 0 | 2 | EXPECTED, HISTORICALLY_OBSERVED |
| RC-11 · OFFICIAL_STATISTICAL_API | 0 | 1 | DECLARED |

---

## D — ARPAV PROVA QUE UMA FONTE TEM N ESTRADAS

`IT-T2-002` tem **duas** pertenças, ambas provadas:

| estrada | papel | prova |
|---|---|---|
| RC-1 · OFFICIAL_HTTP_DOCUMENT | `PRIMARY` | `LIVE_FETCH_PROVEN` — HTTP 200, `application/pdf`, 463 630 bytes, `raw_asset` → `derived_artifact id=1` (`0feb4967`) |
| RC-9 · GIT_LEDGER | `HISTORICAL` | `HISTORICALLY_OBSERVED` — 124 observações no ledger |

A mesma fonte, colhida por dois caminhos diferentes, em momentos diferentes, com
donos diferentes. Um modelo de uma rota por fonte apagaria uma das duas.

---

## E — A ESCADA DA EVIDÊNCIA, E ONDE ELA PAROU

| degrau | o que temos |
|---|---|
| `EXPECTED` | «NÃO SEI — esperado PDF»: 11 fontes. Imaginação do catálogo. |
| `DECLARED` | 3 fontes declaram forma concreta (CSV direto, PDF semanal, HTML) |
| `HISTORICALLY_OBSERVED` | 7 fontes com recibo no ledger — 144 observações |
| `LIVE_METADATA_PROVEN` | 51 fontes responderam ao probe italiano |
| `LIVE_FETCH_PROVEN` | **1** — o canário |

O probe mediu 43 URLs de Milão em 2026-09-07. **Os 33 `ACCESS_OK` devolveram
todos `text/html`**: são páginas iniciais.

    ACCESS_OK É FRONT_DOOR_ACCESS.
    NÃO É HTTP_DOCUMENT_ROUTE.

Por isso a porta aberta não gera pertença nenhuma. Ela move a fonte de
`ROUTE_UNKNOWN` para `REACHABLE_ROUTE_UNKNOWN` — que é mais do que nada e menos
do que uma estrada.

### Zero rede nova

52 das 54 fontes tinham evidência preservada (probe ∪ ledger). **Nenhuma chamada
de rede foi feita nesta missão.**

### `BLOCKED` não é o armário do desconhecido

O probe marcou 4 fontes como `BLOCKED_PARA_CURL`. Isso é impedimento de
**ferramenta**, não de política: a mesma URL pode abrir com um agente comum.
Elas ficam `ROUTE_UNKNOWN`, com a próxima prova mais barata escrita. `BLOCKED` =
**0**.

---

## F — AS DUAS CLASSES QUE A EVIDÊNCIA EXIGIU

| classe | motivo material |
|---|---|
| **RC-10 · OFFICIAL_HTTP_DATASET** | A aquisição é igual à RC-1, mas a cadeia diverge em `DERIVED`: a RC-1 tem um passo **obrigatório e provado** de extração de texto de PDF; um dataset já chega estruturado e não passa por ele. Medido: `IT-T4-001` aparece no ledger com `MIME_ASSINATURA=TEXTO`. Não é formato sozinho — é uma etapa obrigatória de uma classe que na outra não existe. |
| **RC-11 · OFFICIAL_STATISTICAL_API** | SDMX não é documento nem ficheiro único: o `DISCOVER` é um catálogo de dataflows e o `FETCH` é consulta por dimensão. Nenhuma classe modelada tem essas duas etapas. Declarado por `IT-T1-001` (ISTAT) e **não confirmado** — nasce modelada, não provada. |

---

## G — O ORQUESTRADOR

Existe: `orquestrador/orquestrador.py`, alcançando **4** dos 21 executores via
`pedido/receitas.py`. Existir não é cobrir. `SINTONIA SCRAP` continua sendo
`COMPOSITE_EXECUTOR` — coordena rotas de **uma** aquisição, não o calendário.

---

## H — TOP GAPS, RECALCULADOS

Não herdados: o ranking mudou porque a medição mudou.

| # | gap | destrava |
|---:|---|---|
| **G-1** | ligar `STRUCTURED` e `ADMISSION` da RC-1 ao `derived_artifact` | a única classe com pertença provada e arquitetura aberta — e a mais populosa |
| **G-2** | achar o link do documento nas 26 fontes `REACHABLE_ROUTE_UNKNOWN` | 26 fontes, partindo de páginas **já preservadas** |
| **G-3** | tirar o Git do runtime (RC-9 → donos canônicos) | 7 pertenças provadas hoje presas em Git |
| **G-4** | RC-2 ao vivo: `RUN` ligado + operacional | a única cadeia social |
| **G-5** | RC-5: dar `DISCOVER`/`FETCH`/`RAW` ao regulatório | os dados chegam ao importador sem passar por bruto |

---

## I — O QUE ESTE MAPA NÃO PROVA

- **0** estradas com arquitetura fechada.
- `SOURCES_ROUTE_UNKNOWN` = **35**. A M1 não forçou zero, e não devia: quando a
  próxima prova exigiria login, browser especial, download grande ou engenharia
  nova, a fonte parou com `WHAT_IS_MISSING` e `CHEAPEST_NEXT_PROOF` escritos.
- `CODE_CONNECTED` prova que o código **referencia** o artefato. Não prova que
  o referencia **certo** — isso só a execução mostra.
- Zero produção: nenhum DDL, INSERT, UPDATE, DELETE, Storage, API, Apify.

`COLLECTION_FOUNDATION_CLOSED` = **NÃO**.
