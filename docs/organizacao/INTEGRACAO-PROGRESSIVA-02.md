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
| `P0_2_STEP_02` | **PASS** |

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
