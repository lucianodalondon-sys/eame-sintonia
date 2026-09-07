# A LEI DE PERTENÇA — codificada, medida, e o que ela mudou

**Data:** 2026-09-06 · **Regra:** `PERTENCA-2026-09-06` · **Somente leitura**
**Fonte da pertença:** decisão do dono, 2026-09-06
**Fonte da granularidade:** `CONTRATO-DO-PASSAPORTE.md §1.5` — **inalterada**

```
PASSPORT_MEMBERSHIP = EXTERNAL_WORLD_INFORMATION
                      AND INDIVIDUALLY_DECIDED_OR_EXECUTED
```

Duas condições, nesta ordem. A **pertença** é nova e vem primeiro. A **granularidade**
continua sendo a de §1.5 e vem depois. Um registro pode satisfazer a granularidade e
ainda assim ficar de fora, se o referente primário dele for o próprio SINTONIA.

---

## 1 · COMO A LEI FOI CODIFICADA

O teste é **o referente primário do registro** — não a pasta, não a tecnologia.

| | nomeia coisa que existe… | exemplos de campo |
|---|---|---|
| `MUNDO_EXTERNO` | **fora** do SINTONIA | `TRANSCRIPT` · `TITLE` · `PUBLISHED_AT` · `AUTHOR` · `ORCID` · `REGISTRATION_ID` · `REFERENCE_PRODUCT` · `CROP` · `COUNTRY_OF_FACT` · `EXTERNAL_ID` · `EVENT_NAME` · `CODICE_STAZIONE` |
| `PROCESSO` | **só porque** o SINTONIA existe | `ACTOR` · `COST_USD` · `DATASET_ID` · `FINISHED_AT` · `HTTP_STATUS` · `QA_*` · `BUILD_*` · `PRESERVATION_*` · `CONTRACT_STATE` · `HUMAN_DECISION` · `ELAPSED_S` |

### O desempate, que é a parte mais importante da lei

> *"O fato de algo ter sido coletado por uma ferramenta NÃO o transforma em metadado
> interno."*

Um vídeo com `RUN_ID`, `APIFY_ACTOR` e `RUNNER_NAME` **continua sendo um vídeo**. Então
**externo vence processo** quando os dois marcadores aparecem no mesmo registro — a menos
que o nome da própria lista declare que o registro é sobre o processo (`RUNS`, `ACTORS`,
`QA`, `BUILDS`…).

```
{EXTERNAL_ID, TITLE, APIFY_ACTOR, RUNNER_NAME}   → EXTERNO   (é um vídeo)
{RUN_ID, ACTOR, COST_USD, DATASET_ID}            → PROCESSO  (é uma execução)
```

### `SOURCE_HEALTH` — separado, como a lei manda

```
CASO A   "o coletor conseguiu acessar", "HTTP 403", "o ator falhou"   → PROCESSO
CASO B   estado público observável da fonte, tratado como informação   → só com contrato
```

**Não promovi o CASO B automaticamente.** Sem contrato declarado, fica `UNKNOWN`. Há teste
que falha se alguém promover.

### Uma coisa que eu completei, e digo abertamente

A primeira passagem deixou **99 arquivos em `UNKNOWN_SCOPE`**, e ao abrir esse balde vi
que ele continha dois grupos claros que o meu vocabulário não nomeava:

- leituras da **ARPAV no Veneto** — `codice_stazione`, `nome_sensore`, `dataora`,
  `precisionefalda`. Estação e sensor **existem no mundo**, não no SINTONIA;
- relatórios da **nossa tentativa** — `elapsed_s`, `stage`, `http`, `error`, `bytes`.

Completei o vocabulário com esses dois grupos **uma vez**, e rodei a medição definitiva.
Isso é completar a implementação da lei, não ajustar a regra para produzir um número —
e a diferença está registrada aqui para que se possa julgar.

---

## 2 · A RECLASSIFICAÇÃO — os 933, e a soma fecha

```
IN_SCOPE_EXTERNAL_WORLD  = 134
OUT_OF_SCOPE_PROCESS     =  16
OUT_OF_SCOPE_OTHER       = 706
UNKNOWN_SCOPE            =  77
                           ───
TOTAL                    = 933   ✓ soma fecha
```

Motivos, e nenhum arquivo sai sem um:

| estado | motivo | n |
|---|---|---:|
| `IN_SCOPE_EXTERNAL_WORLD` | `DECISAO_POR_ITEM` | 90 |
| | `EXECUCAO_PROPRIA` | 44 |
| `OUT_OF_SCOPE_PROCESS` | `REFERENTE_E_O_PROPRIO_SINTONIA` | 13 |
| | `SEM_REGISTROS_E_REFERENTE_E_O_PROCESSO` | 3 |
| `OUT_OF_SCOPE_OTHER` | `NAO_E_JSON` (`.md`, `.csv`, `.txt`) | 452 |
| | `MUNDO_EXTERNO_MAS_SEM_DECISAO_NEM_EXECUCAO_INDIVIDUAL` | 109 |
| | `SEM_REGISTROS` | 85 |
| | `RAW_PAID_TEM_REGRA_DE_DIRETORIO_PROPRIA` | 60 |
| `UNKNOWN_SCOPE` | `REFERENTE_INDETERMINADO_NAO_CHUTAR` | 77 |

> **Os 109 `MUNDO_EXTERNO_MAS_…` são o caso que só existe porque as duas condições são
> independentes:** falam do mundo externo e não têm decisão individual. Ficam fora do
> universo de passaportes **sem** serem chamados de processo — o motivo diz exatamente
> qual das duas condições faltou.

**`UNKNOWN_SCOPE = 77` e não zero.** É a prova de que a incerteza não foi eliminada por
conveniência, e há teste que falha se ela zerar.

---

## 3 · O UNIVERSO DERIVADO, E A DIFERENÇA

```
RULE_DERIVED_FILES       =    134
RULE_DERIVED_RECORDS     = 14.909
RULE_DERIVED_FAMILIES    =     31
RULE_DERIVED_COLLECTIONS =     69
FINGERPRINT              = fb319c428295101180e69bd00cdb6f44308cde507d9649397f575379f4ac5a66

OLD_COVERED              =     21
NEW_RULE_DERIVED         =    134
MISSING_PASSPORT         =    113
COVERED_BUT_OUTSIDE_RULE =      0
```

**A lista histórica não foi gabarito** — a lei foi codificada a partir da decisão do dono
e de §1.5, e depois comparada. Mesmo assim `COVERED_BUT_OUTSIDE_RULE = 0`: **nada do que o
passaporte já cobre é rejeitado pela lei nova.** A lista estava certa no que incluiu, e
curta em 113.

### O que mudou em relação à regra anterior (só granularidade)

| | só §1.5 | com a lei de pertença |
|---|---:|---:|
| dentro | 132 | **134** |
| fora | 801 | 722 |
| desconhecido | 0 | **77** |

A lei **não encolheu** o universo — corrigiu a composição dele:

- **saíram** os registros de processo que a granularidade sozinha deixava entrar
  (`ACTOR-CONTRACTS-CORPUS.json` era o contraexemplo que travou a missão anterior);
- **entraram** leituras de sensor da ARPAV, que a granularidade sozinha não alcançava;
- **apareceram 77 `UNKNOWN`** que antes eram silenciosamente classificados como fora.

O `UNKNOWN` subir de 0 para 77 é melhora, não piora: antes a incerteza estava escondida
dentro de `OUT_OF_SCOPE`.

---

## 4 · OS CONTROLES

**Positivos — entram** (16 controles, todos passando):

```
TRANSCRIPT · SCIENTIFIC_PAPER · PUBLIC_COMMUNICATION · ADVERTISEMENT
REGULATORY_RECORD · FIELD_OBSERVATION · EXTERNAL_EVENT
EXTERNAL_ACTOR_RECORD · SENSOR_READING
```

**Negativos — não entram, e ficam fora *como processo***:

```
ACTOR_CONTRACT · PIPELINE_EXECUTION · QA_RECORD · INGESTION_REPORT
BUILD_MANIFEST · PRESERVATION_MANIFEST · HUMAN_DECISION
SOURCE_HEALTH_DO_PROCESSO · SCHEMA_CONTRACT
```

> Não basta ficar fora: tem de ficar fora **pelo motivo certo**. Há um teste separado só
> para isso — um registro de QA que saísse como `OUT_OF_SCOPE_OTHER` estaria saindo por
> acidente, não pela lei.

**Ambíguo — tem de sair `UNKNOWN_SCOPE`:** um registro sem marcador de mundo externo nem
de processo. E um teste sobre o acervo real que falha se `UNKNOWN` zerar.

---

## 5 · OS PORTÕES

### As cinco condições do dono

| condição | resultado |
|---|---|
| 1 · a condição de pertença está codificada | **SIM** |
| 2 · nenhuma unidade desaparece sem classificação (soma fecha) | **SIM** — 933 de 933 |
| 3 · toda unidade tem estado e motivo | **SIM** |
| 4 · nenhum registro de processo entrou como evidência | **SIM** — 134 de 134 com referente `EXTERNO` |
| 5 · nenhuma externa excluída só por estar em pasta inesperada | **SIM** — 31 famílias no universo |

```
MEMBERSHIP_CONDITION_DECLARED = YES
MEMBERSHIP_RULE_PROVED        = YES
```

### Completude

```
                    ESPERADO      COBERTO
FILES                    134           21
RECORDS               14.909        7.070

MISSING_FILES     = 113
MISSING_RECORDS   = 7.839
MISSING_FAMILIES  = 31
COVERED_BUT_OUTSIDE_RULE = 0

UNIVERSE_COMPLETENESS = FAIL  ·  MISSING_PASSPORT · UNKNOWN_SCOPE_NOT_ZERO
```

**São duas perguntas diferentes, e elas não podem ser fundidas.** A lei está provada; o
universo que ela define não está coberto. A primeira passa com a segunda vermelha, e é
exatamente o estado de hoje.

### Os dois portões já fechados, reexecutados

```
CLAIM_ID_GATE_ACTIVE_STATE = PASS   (55 ids, 0 colisões)
EVIDENCE_STATE_GATE        = PASS   (346 → 0)
REEMISSAO_VERIFICADA       = SIM
```

Nenhum foi reaberto. `EVENTOS.jsonl` e `data/samples` intactos.

---

## ENTREGA

```
MEMBERSHIP_CONDITION_DECLARED = YES
MEMBERSHIP_RULE_PROVED        = YES

RULE_DERIVED_FILES            =    134
RULE_DERIVED_RECORDS          = 14.909
PROCESS_RECORDS_EXCLUDED      =     16
UNKNOWN_SCOPE                 =     77

IN_SCOPE_EXTERNAL_WORLD  134  +  OUT_OF_SCOPE_PROCESS  16
+ OUT_OF_SCOPE_OTHER     706  +  UNKNOWN_SCOPE         77   =  933   ✓

UNIVERSE_COMPLETENESS         = FAIL  ·  MISSING_PASSPORT · UNKNOWN_SCOPE_NOT_ZERO
PASSPORT_READY                = NOT_YET
FULL_BACKFILL_REQUIRED        = YES, para 113 arquivos — NÃO EXECUTADO

CLAIM_ID_GATE       = PASS
EVIDENCE_STATE_GATE = PASS

TESTS = 128/128   (28 leis + 48 CLAIM_ID + 17 universos + 19 regra + 16 pertença)
PORTAL_TOUCHED = NO · DEPLOY = NO · DATA_DESTRUCTIVE_CHANGE = NO
```

### O QUE FALTA PARA O BACKFILL — medido, não executado

```
MISSING_FILES    = 113
MISSING_RECORDS  = 7.839
MISSING_FAMILIES = 31
```

Parei antes do backfill, como mandado. A lista dos 113 e das 31 famílias está em
[`PASSPORT-PERTENCA.json`](PASSPORT-PERTENCA.json), campos `MISSING_FILES` e
`MISSING_FAMILIES`.

### BLOCKERS_REMAINING

1. **113 arquivos pertencem ao universo e não têm passaporte** — 7.839 registros. Custo e
   impacto do backfill ainda não medidos.
2. **77 arquivos em `UNKNOWN_SCOPE`** — referente indeterminado. Cada um precisa de
   decisão ou de um marcador declarado; nenhum será chutado.
3. `UNIVERSE_ACERVO_IT` (141 × 101 × 164) **não tocado** — outra missão.
4. `UNIVERSE_EXECUCOES` **não alterado**; segue como universo distinto de proveniência,
   dono `scripts/proveniencia.py`. Os 16 registros de processo excluídos aqui pertencem
   a ele.
5. Sem `pytest`/`pip`: a suíte antiga do repositório continua `NAO_MEDIDO`.
