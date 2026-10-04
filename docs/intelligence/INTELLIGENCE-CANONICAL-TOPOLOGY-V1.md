# TOPOLOGIA CANÓNICA DA INTELLIGENCE — V1

```
MISSAO   C-INT-ARB-01 · 2026-09-13
ESTADO   DESENHO ARBITRADO. NAO IMPLEMENTADO.
```

> A missão entregou este fluxo como **hipótese da Bíblia**, com a ordem de só
> manter cada etapa que sobrevivesse à arbitragem. Sobreviveram todas, com **duas
> correções de forma** e uma etapa reposicionada.

---

## A ESPINHA

```
                    ┌─────────────────────────────┐
                    │   COLLECTION  (outro dono)  │
                    │   RAW → DERIVED → STRUCTURED│
                    │   → ADMISSION → READY       │
                    └──────────────┬──────────────┘
                                   │
                          SALA DE ESPERA
                   data/samples/PRONTO-PARA-INTELIGENCIA/
                                   │
   ════════════════════════════════╪════════════════════════════════
                    A FRONTEIRA — a Intelligence comeca aqui
   ════════════════════════════════╪════════════════════════════════
                                   │
                          INTELLIGENCE_REQUEST
                                   │
                          INTELLIGENCE_RUN
                                   │
              ┌────────────────────┴────────────────────┐
              │  EVIDENCE / SUPPORT / CONTRADICTION     │
              └────────────────────┬────────────────────┘
                                   │
                    DEPENDENCY / INDEPENDENCE
                                   │
                 NORMALIZATION / ENTITY RESOLUTION
                                   │
                              CROSSING
                                   │
                           ANALYTIC_SIGNAL
                                   │
                   HYPOTHESIS / ALTERNATIVES
                                   │
                    FINDING / ANALYTIC_JUDGMENT
                                   │
        OPPORTUNITY / ATTENTION ITEM / FUTURE SIGNAL
                                   │
                       INTELLIGENCE_PACKAGE
                                   │
                       INTELLIGENCE TOOLS
                                   │
                          CASCO / PORTAL
```

E uma seta que sai de lado, e nunca para a frente:

```
   qualquer etapa  ──►  COLLECTION_GAP  ──►  COLLECTION CANONICA
                                             (nunca um coletor directo)
```

---

## AS DUAS CORREÇÕES AO DESENHO PROPOSTO

### 1 · `NORMALIZATION / ENTITY RESOLUTION` sobe para antes de `CROSSING`

O desenho da missão punha-a depois de `DEPENDENCY / INDEPENDENCE` e antes de
`CROSSING` — e está certo, mas por uma razão que precisa de ficar escrita:
`INT-LAW-080` diz «Normalização precede backfill/crossing massivo», e
`INT-LAW-091` diz «Missing join key bloqueia crossing».

```
CRUZAR ANTES DE NORMALIZAR E CRUZAR NOMES, E NAO COISAS.
```

Mantida onde estava, com a lei ao lado.

### 2 · `COLLECTION_GAP` não é uma etapa da espinha

O desenho da missão não a incluía na coluna, e é a decisão certa. Um gap pode
nascer em **qualquer** etapa — falta evidência para suportar, falta chave para
cruzar, falta universo para afirmar zero. Pô-lo na coluna sugeriria um momento
próprio.

```
UM BURACO NAO E UMA ETAPA. E O QUE UMA ETAPA DESCOBRE QUE LHE FALTA.
```

Por isso sai de lado, e retorna pela Collection canónica (`INT-LAW-020`).

---

## O QUE CADA FRONTEIRA PROMETE

| fronteira | promete | lei |
|---|---|---|
| SALA DE ESPERA → REQUEST | a unidade está admitida e tem identidade upstream | `INT-LAW-010` |
| REQUEST → RUN | toda execução tem identidade própria e configuração preservada | `INT-LAW-051`, `052` |
| RUN → EVIDENCE | participar do mesmo run **não** cria edge | `INT-LAW-042` |
| EVIDENCE → DEPENDENCY | mesmo originador não vira múltiplas fontes | `INT-LAW-071` |
| DEPENDENCY → CROSSING | crossing declara a pergunta que responde | `INT-LAW-090` |
| CROSSING → SIGNAL | crossing é relação provada, não semelhança | `INT-LAW-037` |
| SIGNAL → FINDING | SIGNAL ≠ FINDING ≠ OPPORTUNITY | `INT-LAW-036` |
| FINDING → OPPORTUNITY | opportunity é objeto analítico, não card visual | `INT-LAW-039` |
| PACKAGE → PORTAL | o portal não reconstrói Intelligence | `INT-LAW-023` |
| qualquer → GAP | o gap volta pela Collection canónica | `INT-LAW-020` |

---

## O ESTADO REAL DE CADA ETAPA, HOJE

Medido, e não desejado:

| etapa | implementação | estado |
|---|---|---|
| SALA DE ESPERA | `admissao/sala_de_espera.py` | ✅ existe, com dono e travas |
| INTELLIGENCE_REQUEST | — | ❌ não existe |
| INTELLIGENCE_RUN | — | ❌ **0 ficheiros** |
| EVIDENCE / SUPPORT / CONTRADICTION | regras dispersas | ⚠️ parcial |
| DEPENDENCY / INDEPENDENCE | regras em `motor/`, sem grafo | ⚠️ parcial |
| NORMALIZATION | `motor/v21_normalizar.py`, `normalize_*` | ✅ existe |
| CROSSING | `motor/v21_crossings.py` | ✅ dono provado |
| ANALYTIC_SIGNAL | disperso | ⚠️ sem dono único |
| HYPOTHESIS / ALTERNATIVES | — | ❌ não existe |
| FINDING / JUDGMENT | `motor/v21_fechar.py`, sem decision trace | ⚠️ parcial |
| OPPORTUNITY | `motor/v21_oportunidades.py` | ✅ dono provado |
| INTELLIGENCE_PACKAGE | `CANONICAL-PACKAGE-CONTRACT.json` + portões | ✅ runtime provado |
| INTELLIGENCE TOOLS | — | ❌ fora do censo |
| COLLECTION_GAP | — | ❌ **0 ficheiros** |

```
A ESPINHA TEM 14 VERTEBRAS. QUATRO EXISTEM COM DONO PROVADO,
QUATRO NAO EXISTEM DE TODO, E O RESTO ESTA A MEIO.
```

E a vértebra que falta primeiro é a segunda: sem `INTELLIGENCE_RUN` não há a que
pendurar lineage nenhum.

---

## O QUE ESTA TOPOLOGIA PROÍBE

```
INTELLIGENCE  ──✗──►  COLETOR DIRETO
PORTAL        ──✗──►  RECALCULAR JULGAMENTO
INTELLIGENCE  ──✗──►  SEGUNDA IDENTIDADE FACTUAL
ARTEFACTO CONGELADO ──✗──► SER DONO DE CONCEITO
UM MESMO RUN  ──✗──►  PROVAR LIGACAO ENTRE DOIS ARTEFACTOS
```

O primeiro tem um candidato vivo em código: `motor/normalize_agro.py` →
`coleta/eppo_gd.py`. Classificado `KEEP_BUT_BLOCK`, e nenhuma rota o anda hoje.

---

# ANEXO A · CONTRATO CANDIDATO DE `INTELLIGENCE_RUN`

```
IMPLEMENTED    = NO
CONTRACT_READY = YES  (candidato para a PRIMEIRA implementacao)
```

Validado contra `INT-LAW-050..054`, contra o benchmark que a própria Bíblia
regista (OpenLineage `Run/Job/Dataset`; W3C PROV `Activity/Entity/Agent`) e
contra o que a casa já pratica na Collection.

| campo | obrigatório | porquê, e de onde vem |
|---|---|---|
| `INTELLIGENCE_RUN_ID` | sim | `INT-LAW-051`. Surrogate cunhado no início. Nunca derivado de conteúdo. |
| `REQUEST_ID` | sim | liga à pergunta. Sem ela, um run não sabe o que respondia. |
| `INPUT_IDENTITIES` | sim | os itens da Sala de Espera **por identidade upstream** — nunca cópia do payload |
| `STARTED_AT` / `FINISHED_AT` | sim | `FINISHED_AT` nulo é run em curso, e isso é um estado |
| `CODE_VERSION` | sim | `INT-LAW-041`: lineage inclui dado **+ lógica + execução** |
| `RULESET_VERSION` | sim | idem |
| `MODEL_VERSION_IF_ANY` | condicional | só existe se houve modelo. Ausente ≠ `NAO SEI` |
| `PARAMETERS` | sim | `INT-LAW-052`: preserva a configuração **efetiva**, não a pedida |
| `OUTPUT_IDENTITIES` | sim | o que este run produziu, por identidade |
| `STATUS` | sim | vocabulário fechado, abaixo |
| `ERROR_STATE` | condicional | preenchido só quando `STATUS = ERROR` |

### O vocabulário de `STATUS`, e por que não é booleano

```
NOT_RUN        nunca comecou            (nao e falha)
RUNNING        em curso
COMPLETED      terminou com resultado
EMPTY_RESULT   correu, e o resultado e vazio  (nao e NO_FINDING)
NO_FINDING     correu, e a resposta e «nao ha achado defensavel»
ERROR          avariou
REUSED         nao correu: reaproveitou um run anterior provado
```

`INT-LAW-053` exige exatamente esta separação, e `INT-LAW-054` exige que
`REUSED` seja **provado**, não assumido.

```
CORREU E NAO ACHOU NAO E O MESMO QUE NAO CORREU.
E NENHUM DOS DOIS E ERRO.
```

### Dois campos que **não** entram, e a razão

```
✗ RAW_OBSERVATION_ID    e identidade da Collection (INT-LAW-002)
✗ CONFIDENCE            e atributo de julgamento, e nao de execucao
```

---

# ANEXO B · CONTRATO CANDIDATO DE `COLLECTION_GAP`

```
IMPLEMENTED    = NO
CONTRACT_READY = YES
```

O que um gap **significa**:

> A Intelligence não consegue sustentar determinada pergunta porque falta
> evidência que precisa de ser adquirida pelo fluxo canónico.

O que ele **não** significa:

> A Intelligence chama um scraper.

| campo | obrigatório | porquê |
|---|---|---|
| `GAP_ID` | sim | identidade própria; um gap é objeto, não mensagem de erro |
| `INTELLIGENCE_RUN_ID` | sim | um gap sem run é uma queixa sem contexto |
| `QUESTION` | sim | a pergunta que ficou por responder, em texto |
| `MISSING_EVIDENCE_CLASS` | sim | **classe**, não URL. Pedir uma morada seria dirigir o coletor |
| `WHY_NEEDED` | sim | o que mudaria no julgamento se a evidência existisse |
| `CURRENT_EVIDENCE` | sim | o que já se tem — separa «não há nada» de «há e não chega» |
| `REQUESTED_SCOPE` | sim | universo, janela temporal e geografia |
| `STATE` | sim | vocabulário abaixo |

### Dois campos acrescentados ao proposto, e porquê

```
+ BLOCKING     este gap impede um judgment, ou apenas enfraquece-o?
+ RAISED_BY    que etapa da espinha o levantou
```

Sem `BLOCKING` não se distingue o gap que para a análise do gap que a limita — e
`INT-LAW-012` diz que `NO_DEFENSIBLE_ACTION_YET` é sucesso epistemológico, o que
só faz sentido se se souber qual gap causou a paragem.

### `STATE`

```
OPEN           levantado, ninguem pegou
ACCEPTED       a Collection aceitou como pedido de aquisicao
REFUSED        a Collection recusou, e a razao fica escrita
SATISFIED      a evidencia chegou pelo fluxo canonico
OBSOLETE       a pergunta mudou, e o gap deixou de importar
```

### A proibição que este contrato carrega

```
UM GAP E UM PEDIDO, E NAO UMA ORDEM.
QUEM DECIDE ADQUIRIR E A COLLECTION.
```

`MISSING_EVIDENCE_CLASS` é deliberadamente uma **classe** e não um endereço: no
momento em que um gap pudesse nomear a URL a raspar, a Intelligence teria passado
a dirigir a coleta por escrito — que é o caminho directo proibido, com outra
roupa.
