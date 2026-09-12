# OS PORTÕES DA COLLECTION V1

`MEASURE != FIX`. Nenhum blocker foi corrigido nesta missão.

## O veredito

```
COLLECTION_CORE_CLOSE = FAIL
BIG_COLLECTION_READY  = FAIL

BLOCKERS            = 5
NON_BLOCKING_DEBT   = 5
ROOT_CAUSES         = 4
MISSÕES ATÉ FECHAR  = 3
```

Este veredito não vem da média das 105 leis. Vem das propriedades que a
coleta grande precisa de ter, e cada falha aponta a propriedade que falta.

## Os dois eixos, que não se inferem

| eixo | natureza | fonte |
|---|---|---|
| `IMPLEMENTATION_STATE` | declarado pela Bíblia | `docs/biblia/leis.json` |
| `CLOSE_GATE` | **medido** | esta missão |

> UMA LEI `PARTIAL` PODE NÃO BLOQUEAR NADA,  
> E UMA LEI PEQUENA PODE BLOQUEAR TUDO.

Medido: **48 leis `PARTIAL`** e **5 blockers**. Nenhum blocker foi derivado
do estado de lei.

## A estrada canónica

| etapa | módulo | aresta | fluxo |
|---|---|---|---|
| `REQUEST` | YES | UNKNOWN | **NO** |
| `ORCHESTRATOR` | YES | UNKNOWN | **NO** |
| `EXECUTOR` | YES | UNKNOWN | **NO** |
| `RUN` | YES | UNKNOWN | **NO** |
| `RAW_OBSERVATION` | YES | YES | **YES** |
| `STORAGE_OBJECT` | YES | YES | **YES** |
| `DERIVED` | YES | YES | **YES** |
| `STRUCTURED` | YES | YES | **YES** |
| `ADMISSION` | YES | YES | **YES** |
| `READY` | YES | NO | **NO** |
| `WAITING_ROOM` | NO | NO | **NO** |

Cinco etapas atravessam. As quatro primeiras nunca foram observadas numa
corrida canónica, e as duas últimas não existem como caminho.

> MÓDULO EXISTE ≠ ARESTA EXISTE ≠ FLUXO EXECUTADO.

## Os blockers

| id | severidade | conceito | propriedade que impede |
|---|---|---|---|
| `G-READY-01` | CRITICAL | READY nao e produzido por nenhuma rota | `LEVAR_ATE_READY` |
| `G-READY-02` | CRITICAL | a sala de espera nao tem armazenamento | `LEVAR_A_SALA_DE_ESPERA` |
| `G-E2E-01` | HIGH | a prova da estrada canonica nao corre neste HEAD | `AUDITAR` |
| `G-RUN-01` | HIGH | duas linguas para a ausencia colidem no banco | `PRESERVAR` |
| `G-RAW-01` | HIGH | a etapa RAW corre e nao fala | `RECONCILIAR, MEDIR_PERDA_ERRO_CUSTO` |

## A dívida que não bloqueia

| id | porque não bloqueia |
|---|---|
| `G-STRUCT-01` | o ledger JA prova STRUCTURED na rota forward por coleta/social_persistencia.py. O gap e de COBERTURA por classe, e nao de ausencia de travessia. |
| `G-ADM-01` | o ledger prova ADMISSION observada na rota forward, com caminho bom e caminho de falha. A infraestrutura ATRAVESSA; o que falta e a cobertura do tipo `derived_artifact`. |
| `G-TEL-01` | nao impede executar nem preservar. Impede LER o que aconteceu, e isso e divida de observabilidade, nao de fecho. |
| `G-TEMA-01` | NAO bloqueia a coleta grande. A funcao da coleta grande e ADQUIRIR e PRESERVAR; admitir bem e a etapa seguinte, e a Admission ja produz decisao auditavel com NAO_SEI de p |
| `G-LEG-01` | nao impede propriedade nenhuma da coleta grande: os 13 estao FORA da Collection operacional por decisao, e o que entra pela frente nao passa por este estado. |

O mecanismo temático falhar o portão é o caso que mais custa classificar.
Ele é `HIGH` e **não** bloqueia: a função da coleta grande é adquirir e
preservar. Admitir bem é a etapa seguinte, e a Admission já produz decisão
auditável com `NÃO SEI` de primeira classe.

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

## A fila mínima

**1. `C-FIX-ABSENCE-VOCABULARY-AT-THE-RUN-SEAM-V1`**

> como a ausencia de um campo da corrida atravessa a fronteira sem que o banco a recuse?

nao depende de nada e todo o resto passa por ela: sem isto, qualquer prova E2E nova rebenta no mesmo sitio

**2. `C-RESTORE-CANONICAL-E2E-PROOF-V1`**

> a estrada canonica volta a ter prova que corre, e a etapa RAW passa a falar?

depende de RC-B; e sem ela o portao nao pode fechar, porque FLOW_EXECUTED nao e observavel

**3. `C-CLOSE-THE-READY-EDGE-V1`**

> uma unidade que a porta admite chega a READY e pousa na sala de espera, na mesma corrida?

precisa de uma estrada observavel para se provar ponta a ponta; e a unica com decisao de contrato por tomar — onde pousa

`MINIMUM_MISSIONS_TO_BIG_COLLECTION_READY = UNKNOWN`. depende de quantas capacidades do SCRAP a coleta grande exige, e isso ainda nao foi medido. Contar agora seria feeling com cara de DAG.

## O que ficou `UNKNOWN`

```
MIGRATION_APPLIED_LIVE                    UNKNOWN
COST                                      NOT_INSTRUMENTED
MINIMUM_MISSIONS_TO_BIG_COLLECTION_READY  UNKNOWN
```

`NOT_INSTRUMENTED` não é zero. Produção não é laboratório.

## Onde estão os números

- `data/derivados/COLLECTION-V1-CLOSE-GATES.json` — dono dos números
- `provas/os_portoes_da_collection.py` — a medição
- `tests/test_portoes_da_collection.py` — 16 testes, 12 mutantes, 0 sobreviventes
- `docs/biblia/CONFORMIDADE-ITALIA.md` — o eixo declarado, por lei
