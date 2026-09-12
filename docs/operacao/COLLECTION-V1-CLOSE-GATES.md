# OS PORTÕES DA COLLECTION V1

`MEASURE != FIX` na medição. Os fechos abaixo vieram de missões próprias,
cada uma com a sua prova.

## O veredito

```
COLLECTION_CORE_CLOSE = FAIL
BIG_COLLECTION_READY  = FAIL

BLOCKERS            = 0
NON_BLOCKING_DEBT   = 5
ROOT_CAUSES         = 4
MISSÕES ATÉ FECHAR  = 0
```

Este veredito não vem da média das 105 leis. Vem das propriedades que a
coleta grande precisa de ter, e cada falha aponta a propriedade que falta.

## Os dois eixos, que não se inferem

| eixo | natureza | fonte |
|---|---|---|
| `IMPLEMENTATION_STATE` | declarado pela Bíblia | `docs/biblia/leis.json` |
| `CLOSE_GATE` | **medido** | esta linha de missões |

> UMA LEI `PARTIAL` PODE NÃO BLOQUEAR NADA,  
> E UMA LEI PEQUENA PODE BLOQUEAR TUDO.

Medido: **48 leis `PARTIAL`** e **0 blockers**. Nenhum blocker foi derivado
do estado de lei.

## A estrada canónica

| etapa | módulo | aresta | fluxo |
|---|---|---|---|
| `REQUEST` | YES | YES | **YES** |
| `ORCHESTRATOR` | YES | YES | **YES** |
| `EXECUTOR` | YES | YES | **YES** |
| `RUN` | YES | YES | **YES** |
| `RAW_OBSERVATION` | YES | YES | **YES** |
| `STORAGE_OBJECT` | YES | YES | **YES** |
| `DERIVED` | YES | YES | **YES** |
| `STRUCTURED` | YES | YES | **YES** |
| `ADMISSION` | YES | YES | **YES** |
| `READY` | YES | YES | **YES** |
| `WAITING_ROOM` | YES | YES | **YES** |

> MÓDULO EXISTE ≠ ARESTA EXISTE ≠ FLUXO EXECUTADO.

Todas as onze etapas já atravessaram. **E isso não é a estrada.**

> **DUAS METADES PROVADAS NÃO SÃO UMA ESTRADA PROVADA.**
> **ONZE ETAPAS QUE JÁ CORRERAM NÃO SÃO UMA HISTÓRIA.**

Elas atravessam em **duas rotas diferentes**. A do pedido vai de RAW/STORAGE
directo à ADMISSION; a rota forward faz DERIVED e STRUCTURED, mas entra pelo
RAW e não pelo pedido. Por isso o portão deixou de somar `YES` e passou a
exigir a **mesma história**, medida por quem aperta o botão no pedido.

Sem ambiente descartável a medição **não corre**, e isso diz-se: `SKIP != PASS`
e `NOT_MEASURED != PASS`.

## Os blockers

**Nenhum.** E isso **não** quer dizer que o core fechou.

```
COLLECTION_CORE_CLOSE     = FAIL
BLOQUEADO_POR             = []
CANONICAL_E2E             = NOT_PROVEN
CANONICAL_E2E_SAME_STORY  = FAIL
```

> **ZERO BLOCKERS ≠ CORE FECHADO.**

A mesma história parou em `STORAGE -> DERIVED`, medido em
[`provas/o_pedido_atravessa.py`](../../provas/o_pedido_atravessa.py).

## Onde a estrada se parte, e são dois achados

Um pedido real atravessou `REQUEST → ORCHESTRATOR → EXECUTOR → RUN → RAW →
STORAGE` numa história só, com o executor a ir à fonte real. E parou.

```
LAST_PROVEN_STAGE   = STORAGE
FIRST_LOST_EDGE     = STORAGE -> DERIVED
NEXT_EXPECTED_STAGE = DERIVED
```

A ADMISSION corre **depois** do buraco e responde `NAO_SEI`, com razão: o
documento chega sem texto porque ninguém o derivou. Uma etapa que corre depois
do buraco não prova a estrada.

Os dois achados são de **espécies diferentes**, e não se misturam — um
resolve-se com código, o outro com uma decisão.

| aresta | tipo | quem resolve |
|---|---|---|
| `STORAGE -> DERIVED` | `WIRING_GAP` | codigo — uma ligacao, no orquestrador |
| `DERIVED -> STRUCTURED` | `CONTRACT_OWNER_GAP` | gente — e uma decisao de arquitetura |

**`STORAGE -> DERIVED` — WIRING_GAP.**
Porquê: a rota do orquestrador vai de RAW/STORAGE direto a ADMISSION: a chamada a derivacao nao esta ligada
Prova: provas/o_pedido_atravessa.py::D1 — a MESMA observacao daquela corrida derivou com PASS quando `derivacao_forward` foi chamada explicitamente

**`DERIVED -> STRUCTURED` — CONTRACT_OWNER_GAP.**
Porquê: `public.conteudo` exige `canal_id`, e `social_persistencia.exigir_canal` recusa quando ele nao existe
Prova: provas/o_pedido_atravessa.py::D2 — a recusa diz, por escrito, QUEM_RESOLVE = «um dono de identidade, fora do executor de coleta», e esse dono nao esta provado hoje

## Os que já fecharam

Ficam na lista com o estado novo. Um gap que some não deixa ver que
existiu, nem por que deixou de existir.

| id | o que mudou |
|---|---|
| `G-E2E-01` | 25 de 25 passam contra PostgreSQL 16 com as migrations 001..027, e a prova da rota devolve ROTA_M2_ATRAVESSA=PASS sobre banco virgem |
| `G-RUN-01` | a fronteira traduz a ausencia para a palavra que o dono de CADA campo entende; `NOT_PRESERVED` continua a valer nos outros |
| `G-RAW-01` | a etapa RAW deixa passagem em `etapa_da_corrida`, e a passagem nomeia a observação que produziu (`raw_asset_id`, migration 028) |
| `G-READY-01` | a rota forward produz READY na mesma corrida: as cinco etapas falam no rastro |
| `G-READY-02` | a sala tem UM dono, escrita atómica, retry idempotente e conflito explícito |

## Quem fala, medido

| etapa | fala? |
|---|---|
| `RAW` | **SIM** |
| `DERIVED` | **SIM** |
| `STRUCTURED` | **SIM** |
| `ADMISSION` | **SIM** |
| `READY` | **SIM** |

Não é uma lista escrita à mão: vem de AST sobre o código de produção — quem
chama `rastro.registrar`, e com que `etapa=`. Um comentário que nomeie uma
etapa não conta.

> UMA ETAPA MUDA PODE ESTAR A CORRER.
> `MUDA != PARADA` — e esse é o problema.

`READY` continua muda porque ninguém a produz: é `G-READY-01`, e não este eixo.

## A dívida que não bloqueia

| id | porque não bloqueia |
|---|---|
| `G-STRUCT-01` | o ledger JA prova STRUCTURED na rota forward por coleta/social_persistencia.py. O gap e de COBERTURA por classe, e nao de ausencia de travessia. |
| `G-ADM-01` | o ledger prova ADMISSION observada na rota forward, com caminho bom e caminho de falha. A infraestrutura ATRAVESSA; o que falta e a cobertura do tipo `derived_artifact`. |
| `G-TEL-01` | nao impede executar nem preservar. Impede LER o que aconteceu, e isso e divida de observabilidade, nao de fecho. |
| `G-TEMA-01` | NAO bloqueia a coleta grande. A funcao da coleta grande e ADQUIRIR e PRESERVAR; admitir bem e a etapa seguinte, e a Admission ja produz decisao auditavel com NAO_SEI de p |
| `G-LEG-01` | nao impede propriedade nenhuma da coleta grande: os 13 estao FORA da Collection operacional por decisao, e o que entra pela frente nao passa por este estado. |

## As causas-raiz

**`RC-A` · a estrada acaba na ADMISSION e READY fica do outro lado**

Sintomas: `G-READY-01`, `G-READY-02`. Dono: admissao/admissao.py + quem decidir o destino.

os dois sao a mesma falta vista de dois lados: nao ha travessia de ADMISSION para READY, e nao ha onde pousar. Consertar so um entrega zero unidades.

**`RC-B` · duas linguas para a ausencia, e a fronteira nao traduz**

Sintomas: `G-RUN-01`. Dono: coleta/ingresso.py::_corrida_completa.

NOT_PRESERVED e NAO_SEI sao dois donos da mesma pergunta. E a MESMA familia do defeito do SOURCE_ID: um valor honesto de um lado que o outro lado nao aceita.

**`RC-C` · a estrada canonica nao tem prova que corra hoje**

Sintomas: `G-E2E-01`, `G-RAW-01`. Dono: tests/test_m2_rota_forward.py + guarda/preservar_coleta.py.

os dois sao a mesma cegueira: a estrada corre e nao se consegue ver. Um porque o retrato esta velho, o outro porque a etapa e muda. E depende de RC-B: uma prova E2E que corra vai bater no enum assim que a corrida nao declarar pais.

**`RC-D` · o SCRAP ainda nao entrega pelo contrato canonico**

Sintomas: `SCRAP_RAW_NAO_RECEBIDO`. Dono: frente do SCRAP — fora desta medicao.

nao e do core: e a integracao que vem DEPOIS do core fechar. Fica na DAG da coleta grande, e nao na do fecho.

## Missões já fechadas

| missão | fechou |
|---|---|
| `C-FIX-ABSENCE-VOCABULARY-AT-THE-RUN-SEAM-V1` | `G-RUN-01` |
| `C-RESTORE-CANONICAL-E2E-PROOF-V1` | `G-E2E-01` |
| `C-MAKE-RAW-OBSERVABLE-V1` | `G-RAW-01` |
| `C-CLOSE-READY-WITH-CANONICAL-WAITING-ROOM-V1` | `G-READY-01` · `G-READY-02` |

## A fila mínima

**1. `C-CLOSE-THE-READY-EDGE-V1`**

> uma unidade que a porta admite chega a READY e pousa na sala de espera, na mesma corrida?

é a única que resta, e a única com decisão de contrato por tomar — onde a unidade pronta pousa

`MINIMUM_MISSIONS_TO_BIG_COLLECTION_READY = UNKNOWN`. depende de quantas capacidades do SCRAP a coleta grande exige, e isso ainda nao foi medido. Contar agora seria feeling com cara de DAG.

## O que ficou `UNKNOWN`

```
MIGRATION_APPLIED_LIVE                    UNKNOWN
COST                                      NOT_INSTRUMENTED
MINIMUM_MISSIONS_TO_BIG_COLLECTION_READY  UNKNOWN
```

`NOT_INSTRUMENTED` não é zero. Produção não é laboratório.

## A frescura deste retrato

> Um carimbo de commit num ficheiro commitado nasce sempre atrasado: ele nunca
> pode nomear o commit que o contém.

Por isso, ao lado do `MEASURED_HEAD`, o artefato guarda a impressão dos **donos
da medição** — o `sha256` do conteúdo dos ficheiros que decidem este resultado.
Se eles não mudaram, a medição continua a valer por mais commits que passem.
Quem quer saber se este retrato ainda vale compara a impressão, e não o commit.

Os dois números vivem no artefato, e **só lá** — copiados para aqui, envelhecem
a cada medição e passam a mentir:

```bash
py -c "import json;d=json.load(open('data/derivados/COLLECTION-V1-CLOSE-GATES.json'));print(d['MEASURED_HEAD']);print(d['FRESCURA']['IMPRESSAO_DOS_DONOS'])"
```

> **O JSON é o dono. O Markdown explica.**

## Onde estão os números

- `data/derivados/COLLECTION-V1-CLOSE-GATES.json` — dono dos números
- `provas/os_portoes_da_collection.py` — a medição
- `tests/test_portoes_da_collection.py` — a guarda dos dois eixos
- `docs/biblia/CONFORMIDADE-ITALIA.md` — o eixo declarado, por lei
