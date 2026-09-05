# P0.2 · PASSO 02 — ENXERTO CANÓNICO

Continuação de `INTEGRACAO-PROGRESSIVA-01.md`. Uma ref, medida e integrada.

---

## 1. Cabeçalho

| Campo | Valor |
|---|---|
| `HEAD_BEFORE` | `510d770` |
| `SELECTED_REF` | `claude/eame-agro-creators-map-77c4ld` |
| `SELECTED_REF_HEAD` | `d76a998` |
| `MERGE_BASE` | `2f03d58` |
| `HEAD_AFTER` | `bd3c538` |
| `REMOTE_HEAD` | `bd3c538` |
| `LOCAL_REMOTE_MATCH` | **SIM** |
| `MERGE_ATTEMPTED` | SIM |
| `MERGE_VERDICT` | **PASS** |
| `P0_2_STEP_02` | **PASS** *(estado publicado em 2026-09-05; supersedido — ver §9)* |
| `P0_2_STEP_02_ATUAL` | **REPAIRED_OWNERSHIP · ISOLATION_DEFECT_OPEN** (§9) |

O head final tem dois merges reais encadeados: o enxerto (`2cef8bc`) e a
reconciliação com o head remoto que se moveu durante a medição (`bd3c538`).
Sem squash, sem rebase, sem cherry-pick, sem cópia de ficheiro, sem force.
61 commits entraram na linhagem com história preservada.

---

## 2. Por que esta ref

Três candidatas medidas contra `510d770`:

| Ref | Ganho de dado | Conflitos | Reparos provados |
|---|---|---|---|
| **`eame-agro-creators-map-77c4ld`** | **3,72 MB processado + 2,51 MB RAW** | **4** | 0/6 |
| `adama-it-local-catalog` (candidata obrigatória) | 2,08 MB | 9 | 2/6 |
| `sintonia-italy-pilot-b1l401` | 1,78 MB | 19 (7 add/add em `scripts/`) | 4/6 |

Vence pelo critério 1 (`UNIQUE_VALID_DATA_GAIN`, 1,8× a segunda) e pelo
critério 8 (menor superfície de conflito).

| Campo | Valor |
|---|---|
| `UNIQUE_VALID_DATA_GAIN` | 3,72 MB processado + 2,51 MB RAW |
| `PROVED_EXISTING_READING_GAIN` | **0/6** |
| `NEW_SCRIPTS` | 20 |
| `NEW_WORKFLOWS` | 0 |

`PROVED_EXISTING_READING_GAIN = 0/6` é declarado, não escondido: esta ref traz
dado novo, não capacidade nova de ler o que já havia.

---

## 3. Conflitos — 4, cada um com prova

`UNKNOWN_CONFLICTS = 0` · `INTELLIGENCE_SEMANTIC = 0`

### 3.1 `data/samples/RUN-MANIFEST.json` → **OURS** · CONTRACT

- Os dois lados declaram **exatamente os mesmos 22 RUN_IDs** (nenhum só do THEIRS).
- `DATASET_OWNER` presente em OURS **22/22**, em THEIRS **0/22**.
- Em THEIRS, o carimbo de 3 execuções `FAILED` é hora de escrita apresentada
  como hora de execução — o defeito que `portao.py` documenta.

### 3.2 `.github/workflows/apify-creators.yml` → **THEIRS** · MECHANICAL

- THEIRS é superconjunto: **9 fases contra 5**.
- A linha extra de OURS (`git add data/samples/raw-paid/14-MAPA*`) é **proibida**
  por `tests/test_creators.py:936`.
- A única ocorrência de `14-MAPA` em THEIRS está em comentário (linha 9).
- Os três scripts invocados existem no índice mesclado.

### 3.3 `data/samples/DATA-CLOCK-manifest.json` → **REGERADO** · PROVENANCE

- `python3 scripts/data_clock.py` → 66 fontes / 85 ficheiros, exactamente a união.
- **Efeito colateral declarado:** corrige **8 digests SHA-256 falsos** que OURS
  publicava. Esses digests alimentam o portão `PAID_RAW_POLICY`
  (`portao.py:91-108`) — o portão validava contra hash errado.
- `captured_at` do manifesto passa a `2026-09-05`.

### 3.4 `docs/decisoes/DIARIO-DE-DECISOES.md` → **UNIÃO** · HISTORICAL_ONLY

- Nenhum lado descartado. 901 linhas, 44 entradas `### D-` (13 + 14 + 17).
- Os 14 IDs em colisão (`D-013`…`D-026`) ficam **declarados como colisão**, não
  renumerados: renumerar reescreveria decisão alheia.

---

## 4. Portão bloqueante de consumidores

`SEMANTIC_CHANGE` = **SIM** — PROVENANCE (DATA-CLOCK) + CONTRACT (RUN-MANIFEST).

Corrido até ao fim, sozinho, sem nenhum trabalho em paralelo, como manda a lei
do passo 01.

**A primeira passagem deu `BLOCKING_REACHABLE_CONSUMERS = 0` com ressalva
explícita:** `scripts/proveniencia.py:169 carregar()` levantava `NameError`, e
portanto a cadeia de consumo estava inalcançável **por defeito, não por
segurança**. Ficou registado como risco, não como prova.

**Durante a medição o defeito foi corrigido** por uma sessão irmã (`86ef144`).
Pela lei, "nenhum bloqueante" não se herda — foi **re-medido com a cadeia viva**.

### 4.1 Contrafactual que valida a escolha de OURS

| | `carregar()` | `carregar('EARLY_SIGNAL_EAME')` |
|---|---|---|
| **OURS** (escolhido) | 22 execuções | **12 execuções** |
| **THEIRS** | 22 execuções | **0 execuções** |

O `FUTURE_MIGRATION_RISK` registado materializou-se em horas. Ter tomado THEIRS
teria **esvaziado em silêncio** toda a proveniência por dono.

### 4.2 Verdicto medido nos dois lados

| | `RUN_MANIFEST` | citados | órfãos | artefatos | `READY_FOR_NEXT_ES_COLLECTION` |
|---|---|---|---|---|---|
| base `15b1ec2` | **BLOCKED** | 110 | 94 | 44 | NO |
| mesclada `bd3c538` | **BLOCKED** | 135 | 119 | 57 | NO |

**Nenhum consumidor passa de PASSA para FALHA.** O único portão bloqueante já
bloqueava, pelo mesmo motivo, antes do enxerto.

`BLOCKING_REACHABLE_CONSUMERS` = **0**
`AGRAVAMENTO_DE_BLOQUEIO_PRE_EXISTENTE` = **+25 RUN_ID órfãos**

### 4.3 O achado que importa

A ref de origem `d76a998`, **medida sozinha**, dava `RUN_MANIFEST` **PROVED**
— "3 RUN_ID citados, 0 órfãos" — e `READY = YES`.

Isso **não era dado mais limpo: era um scanner mais estreito.** Aplicado o
scanner canónico aos mesmos dados, aparecem **24 RUN_ID que nenhum lado do
conflito declarava** (`14-MAPA-DE-CREATORS-EAME-*`,
`15-CREATOR-CONTENT-CORPUS-EAME-*`). O verde da origem era do alcance da régua,
não da qualidade do dado.

> **`SCANNER_REACH != DATA_HEALTH`** — um verde obtido por olhar menos não é
> um verde. Vale para toda ref futura medida em isolamento.

**Não corrigido de propósito:** declarar as 24 execuções exigiria carimbo de
hora de execução que não existe. Inventá-lo é exactamente o defeito que
`portao.py` existe para apanhar. Fica registado, não fabricado.

---

## 5. Regressão

**A primeira medição foi lixo e é declarada como tal.** Corrida com `pytest`,
deu "0 falhas dos dois lados" — porque `tests/test_comunicacao.py` levanta
`SystemExit` no import, o `pytest` morre em `INTERNALERROR` e **não corre teste
nenhum**. Comparar dois ficheiros vazios não prova nada. Refeita com
`unittest`, que é como os workflows da casa correm.

| | base `15b1ec2` | mesclada `bd3c538` |
|---|---|---|
| testes distintos a falhar | 14 | **13** |

`NEW_TEST_REGRESSIONS` = **0** · `TESTES_REPARADOS` = **1**
(`test_branch_vivo_nao_e_alvo_congelado`)

As 4 linhas que a comparação textual mostrava como "novas" são o **mesmo teste
nos mesmos 4 documentos** (`test_todo_numero_publicado_vem_do_dono`). Só muda o
número embutido na mensagem, porque o dono conta a suite viva e o merge trouxe
testes: **727 → 833**. Os documentos publicam `713` e já falhavam na base.

**Não corrigido, por estar fora do enxerto e partido na base:**
`metricas_canonicas.sync()` rebenta com
`ValueError("Cannot specify ',' with 's'")` em `15b1ec2` **e** na mesclada — uma
métrica de texto cai no formato de milhar. A ferramenta da casa para arrumar
esses 4 documentos não funciona. Frente própria.

---

## 6. Portões de perda e integridade

Re-medidos contra `15b1ec2` **e** `d76a998` depois do segundo merge.

| Portão | Valor |
|---|---|
| `CANONICAL_VALID_CONTENT_LOST` | **0** |
| `SOURCE_VALID_CONTENT_LOST` | **0** |
| `NEW_TRACKED_AND_IGNORED` | **0** (1 pré-existente: `data/raw/IT-ROTULOS/_MANIFESTO.json`) |
| `NEW_WORKFLOW_BREAKAGES` | **0** — quebradas 4 na base → 1 na mesclada; o merge reparou `creator_coleta.py`, `creator_corpus.py`, `creator_corpus_coleta.py`; resta `linkedin_prova_busca.py`, pré-existente |
| `DATA_CLOCK_STALE` | **NÃO** (regerar não muda um byte) |
| `PAID_RAW_POLICY` | **PROVED** (0 SHA-256 divergente) |
| `git fsck` | **0 erros** |

`git ls-tree -rz` e `git check-ignore --no-index`, pelas leis 6 e 7.

---

## 7. Registo para frente

| Item | Estado |
|---|---|
| 8 digests SHA-256 falsos em DATA-CLOCK | **corrigidos** por regeneração; alimentavam `portao.py:91-108` |
| 24 RUN_ID órfãos vindos da origem | **registados, não fabricados** — falta hora de execução |
| `metricas_canonicas.sync()` rebenta | pré-existente na base; frente própria |
| 4 documentos publicam `TEST_COUNT_CURRENT = 713` (dono: 833) | pré-existente; depende da correcção acima |
| `linkedin_prova_busca.py` referenciado e ausente | pré-existente |
| `VERIFICACAO_ADVERSARIAL = VERIFICATION_STALE` | pré-existente na base |

---

## 8. Próximo passo

`NEXT_SINGLE_STEP` = **P0.2 · PASSO 03 — medir o próximo enxerto contra o novo
HEAD `bd3c538`**

**NÃO EXECUTADO.** Parado aqui, como mandado.


---

## 9 · LIVRO DE ESTADOS — o que mudou depois de publicar

Esta secção **não corrige o texto acima**. O que ficou escrito em §1–§8 foi o que se
mediu na altura, com o harness da altura, e fica de pé como registo. O que mudou foi o
que se soube depois.

### 9.1 · A linha do tempo, sem apagar nada

```
PASS                            publicado em 70b097e · medido por modulo, harness da casa
  ↓  verificacao independente
PUBLISHED_BUT_HEALTH_GATE_RED   24 execucoes sem DATASET_OWNER; 7 falhas que o baseline
                                pre-enxerto nao tinha, sob corrida de processo unico
  ↓  reparo de proveniencia (este commit)
REPAIRED_OWNERSHIP              portao de dono verde; 2 das 7 falhas curadas
ISOLATION_DEFECT_OPEN           as outras 5 tem outra causa, nomeada em 9.4
```

O `PASS` original **não foi um erro de medição**: com isolamento por processo — que é
como os 18 workflows da casa correm os testes — ele era e continua a ser verdade. O que
faltava era a segunda leitura.

### 9.2 · O que estava mesmo errado

24 execuções entraram no canónico sem `DATASET_OWNER`, campo que `pv.CAMPOS_RUN` exige.
Não era dado sujo: era **uma declaração em falta**. `scripts/creator_corpus.py` já
declarava, desde a origem, `DATASET_OWNER = 'CREATOR_CONTENT_CORPUS_EAME'` e
`MISSION = '15-CREATOR-CONTENT-CORPUS-EAME'`. Faltava a mesma linha em `pv.DONOS`, o mapa
que o portão consulta. Sem ela `dono_da_missao` devolvia `UNDECLARED_OWNER` e o portão
recusava — que é o comportamento **certo**, não o defeito.

### 9.3 · O reparo, e só ele

```
POLITICA   pv.DONOS ganha 'CREATOR_CONTENT_CORPUS_EAME': ('15-CREATOR-CONTENT-CORPUS-EAME',)
BACKFILL    7 runs MISSION=14-MAPA-DE-CREATORS-EAME       -> CREATOR_MAP_EAME
           17 runs MISSION=15-CREATOR-CONTENT-CORPUS-EAME -> CREATOR_CONTENT_CORPUS_EAME
TOTAL      3 ficheiros · 25 insercoes · 0 remocoes
```

O dono foi derivado **exclusivamente** por `dono_da_missao(MISSION)`, nunca por prefixo de
`RUN_ID` nem por palpite. Nenhum facto histórico foi tocado: `RUN_ID`, `ACTOR`, `INPUT`,
`STARTED_AT`, `FINISHED_AT`, `COST_USD`, `DATASET_ID`, `COUNTRY`, `STATUS` e
`RAW_EVIDENCE_PATH` são byte-a-byte os mesmos, verificados campo a campo antes de escrever.
**Nenhuma hora ausente foi inventada** — o que não estava preservado continua não preservado.

Varridos os 541 JSON da árvore, os mesmos `RUN_ID` aparecem ainda em 5 artefactos derivados
como carimbo (`CREATOR-ACTIVITY`, `CROP-PROOF`, `HUB-DISCOVERED-RESOLVED`, `HUB-EXTRACTION`,
`SEED-IT-RESOLVED`). Esses **não** recebem `DATASET_OWNER`: a casa tem 37 artefactos
derivados equivalentes e **37 de 37** carregam `RUN_ID` sem `DATASET_OWNER`. Seguir a
convenção vale mais do que uniformizar por reflexo. `RUN_ID_OWNER_DIVERGENCES = 0`.

`UNKNOWN_MISSION_STILL_FAILS_CLOSED = SIM` — missão não declarada continua a sair
`UNDECLARED_OWNER`. O fail-closed não foi enfraquecido para conseguir verde.

### 9.4 · O que sobra, e por que não entra aqui

Numa corrida de **processo único** (a suíte toda de uma vez) sobram 5 falhas que o baseline
pré-enxerto não tem. Não são dado doente, e o backfill não as podia curar:

```
scripts/creator_coleta.py:113          pv.MANIFESTO = .../RUN-MANIFEST-CREATORS.json
scripts/creator_corpus_coleta.py:62    pv.MANIFESTO = .../RUN-MANIFEST-CORPUS.json
```

As duas reatribuem um global da casa **no import** e nunca restauram. Tudo o que for
importado depois, no mesmo processo, passa a ler o manifesto da missão em vez do da casa.
`tests/test_dataset_owner.py:45-50` faz exactamente a mesma coisa da maneira certa,
guardando e devolvendo em `setUp`/`tearDown`.

Fica **registado e não escondido**, e fora deste commit por estar fora do escopo autorizado.
`tests/test_creators.py` não foi removido nem ignorado: `TEST_GREEN_BY_LOOKING_LESS !=
HEALTHY_DATA` vale nas duas direcções.

### 9.5 · Medição final, nos dois harnesses

| | baseline pré-enxerto `15b1ec2` | publicado `70b097e` | reparado |
|---|---|---|---|
| por módulo (harness da casa) | 17 F / 6 E | 17 F / 6 E | **17 F / 6 E** |
| processo único (pytest) | 17 falhas | 24 falhas | **22 falhas** |
| execuções sem `DATASET_OWNER` | — | 24 | **0** |

```
NEW_TEST_REGRESSIONS (harness da casa, por modulo) = 0     ← modulos e contagens identicos ao baseline
NEW_TEST_REGRESSIONS (processo unico, pytest)      = 5     ← todas do defeito de 9.4
MISSING_DATASET_OWNER_M14 = 0 · MISSING_DATASET_OWNER_M15 = 0 · UNDECLARED_OWNER_M15 = 0
CANONICAL_VALID_CONTENT_LOST = 0 · SOURCE_VALID_CONTENT_LOST = 0 · UNKNOWN_DIFFERENCES = 0
GITIGNORE_CHANGED = NAO · RAW_CHANGED = NAO · git fsck = 0 erros
```

### 9.6 · Estado, e o que ele bloqueia

```
OWNERSHIP_GATE = PASS
HEALTH_GATE    = PASS no harness da casa · RED sob processo unico
P0_2_STEP_02   = REPAIRED_OWNERSHIP · ISOLATION_DEFECT_OPEN
STEP_03        = BLOCKED
```

**Não declaro `PASS_AFTER_REPAIR`.** A regra é `NEW_TEST_REGRESSIONS = 0`, e há um harness
em que não é. Chamar isto de PASS seria escolher a leitura que convém — exactamente o que
`SCANNER_REACH != DATA_HEALTH` proíbe, na direcção oposta.

O que desbloqueia o PASSO 03 é restaurar `pv.MANIFESTO` nos dois scripts, do modo que
`test_dataset_owner.py` já demonstra. É uma frente própria, pequena e provada.
