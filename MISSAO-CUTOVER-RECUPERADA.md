# MISSÃO — CUTOVER DA COLLECTION (RECUPERADA, NÃO REINICIADA)

Esta é a **continuação** de uma missão interrompida porque a sessão anterior do
Hermes morreu. **NÃO recomeces do zero. NÃO faças reset. NÃO descartes a
worktree. NÃO refaças trabalho já feito.**

REPO: lucianodalondon-sys/eame-sintonia
BANCADA: `C:/Users/London1/orca/workspaces/eame-sintonia/cutover-v2`
BRANCH: `claude/contract-provenance-cutover-v1`
HEAD NO DESPACHO: `606974c3c4559c32307b8f68ec7d7eb925379cc6`

**INTELLIGENCE CONTINUA PROIBIDA. PORTAL PROIBIDO.**

---

## 0 · O QUE O COORDENADOR JÁ MEDIU — CONFIRMA, NÃO CONFIES

Tudo abaixo foi medido pelo coordenador **antes** deste despacho. Trata cada
linha como **alegação a reconfirmar**, não como verdade recebida. Se a tua
medição divergir da minha, **a tua medição manda** — e escreve a divergência.

### O que SOBREVIVEU (está no disco, NÃO está commitado)

`git status` da bancada no despacho — 4 entradas, todas trabalho válido:

```
 M coleta/italy_pilot_collect.mjs            (+43 linhas)
 M system-map/scripts/relatorio_do_fluxo.py  (+20 linhas)
?? regras/procedencia_do_contrato.mjs        (6023 bytes, 134 linhas)
?? regras/procedencia_do_contrato_test.mjs   (8613 bytes)
```

Corri `node regras/procedencia_do_contrato_test.mjs` agora: **PASSOU 19 ·
FALHOU 0**, exit 0. Portanto:

```
CONTRACT_VERSIONING            = PASS (19/19)  ·  mas COMMITTED = NO
SOURCE_CONTRACT_VERSION        = italy-contracts-v2
SOURCE_CONTRACT_HASH_IMPLEMENTED = YES (hashDoContrato, determinístico)
CONFIG_HASH_IMPLEMENTED        = YES (hashDaConfiguracao, relógio fora)
CONTRATO_MOTOR_VERSAO_WRITTEN  = YES (importado de motor_de_rota.mjs)
SOURCE_CONTRACT_VERSION != POLICY_VERSION = CORRIGIDO (POLICY_VERSION = NOT_MEASURED)
```

Este trabalho é bom e é teu ponto de partida. **PRESERVA-O.**

### ⚠️ O QUE **NÃO** ACONTECEU — a correção mais importante deste briefing

A última frase visível da sessão morta foi *"Migrando as que cabem — IT-T3-002
e IT-T3-008"*. **Essa migração NUNCA chegou ao disco.** Medido por mim agora,
contrato a contrato, em `regras/italy_contracts.mjs`:

| SOURCE_ID | ACQUISITION | IDENTITY |
|---|---|---|
| IT-T2-002 | NO | NO |
| IT-T2-004 | NO | NO |
| IT-T3-002 | **NO** | **NO** |
| IT-T3-005 | NO | NO |
| IT-T3-008 | **NO** | **NO** |
| IT-T3-010 | NO | NO |
| IT-T4-001 | NO | NO |
| IT-T3-011 | YES | YES  ← a única já declarativa |

```
IT-T3-002_MIGRATION_STATE = NOT_STARTED
IT-T3-008_MIGRATION_STATE = NOT_STARTED
```

O `switch` por SOURCE_ID continua **inteiro**: 7 `case` em `alvosDe()`
(`coleta/italy_pilot_collect.mjs` ~linha 204) e 7 `case` em `identidade()`
(~linha 298). `LEGACY_DISCOVERY_CASES_BEFORE = 7`,
`LEGACY_IDENTITY_CASES_BEFORE = 7`.

**Não acredites na frase da sessão morta. Acredita no ficheiro.**

### O motor declarativo que JÁ EXISTE — usa-o, não escrevas outro

`regras/motor_de_rota.mjs` (244 linhas) já implementa um vocabulário fechado:

```
ACQUISITION.STRATEGY : STATIC_ENDPOINT · TEMPLATE_ENUMERATION · HTML_LINK_DISCOVERY
IDENTITY.STRATEGY    : FILENAME_CAPTURE
```

O despacho já está certo em `alvosDe()`: contrato com `ACQUISITION` vai ao
motor; quem não tem cai no `switch`. **O dispatcher central não conhece
SOURCE_ID e não pode passar a conhecer.**

---

## 1 · PRIMEIRO ATO — SALVA O QUE SOBREVIVEU

Antes de qualquer alteração nova: corre o teste para confirmares o 19/19 com os
teus próprios olhos, e **commita o trabalho recuperado** como checkpoint
próprio, com mensagem que diga que é recuperação de sessão interrompida.

Trabalho não commitado é a única coisa aqui que uma queda destrói.

---

## 2 · CONTINUAR O CUTOVER — uma fonte de cada vez

Para cada uma das 7 fontes legadas, mede e classifica antes de mexer:

```
SOURCE_ID = · DISCOVERY_LEGACY = · IDENTITY_LEGACY =
ACQUISITION_STRATEGY = · IDENTITY_STRATEGY =
CAN_BE_DECLARATIVE = · NEEDS_FAMILY_ADAPTER = · NEEDS_SOURCE_ADAPTER = · BLOCKED =
```

Ordem de preferência, sem saltar degraus:
**1** capacidade existente → **2** estratégia declarativa simples →
**3** family adapter reutilizável → **4** source adapter → **5** BLOCKED.

Se duas ou mais fontes partilham o mesmo padrão, **uma capacidade partilhada**,
não duas. Estás autorizado a implementar a **menor** capacidade reutilizável
necessária para identidade que depende do conteúdo do documento.

**PROIBIDO:** parser universal · OCR não medido · duplicar o PDF→texto que já
existe (`pdftotext` já está em `identidade()`) · interpretar prosa humana como
programa (`DOCUMENT_ID_RULE_TEXT != IDENTITY_EXECUTABLE_SPEC`).

Para cada migração, prova a equivalência **antes** de remover o `case` antigo:

```
LEGACY_BEHAVIOR_CAPTURED = YES · CONTRACT_BEHAVIOR_PROVEN = YES
DISCOVERY_EQUIVALENT = · IDENTITY_EQUIVALENT =
FACT_TIME_EQUIVALENT = · OUTPUT_EQUIVALENT =
FACT_TIME_FABRICATED = 0 · FACT_LOCATION_FABRICATED = 0
```

⚠️ **Preserva os `FACT_TIME: "UNKNOWN"` que já lá estão.** Vários `case`
declaram honestamente que o documento não data o facto observado. Uma migração
que troque esse UNKNOWN por uma data de publicação **fabrica o tempo do facto** e
reprova a missão inteira. `PUBLICATION_TIME != FACT_TIME`.

⚠️ `IT-T3-008` tem no `case` um *fallback* de rota previsível com
`descoberta_degradada: INDEX_REQUIRES_BROWSER`. Se o migrares, esse sinal de
degradação **tem de sobreviver** — perdê-lo transforma uma descoberta degradada
em descoberta normal, que é mentir no ledger.

Objetivo: `LEGACY_DISCOVERY_CASES_AFTER = 0`, e reduzir corretamente
`LEGACY_IDENTITY_CASES_AFTER`. **Não persigas zero artificial** — adapter
explícito e declarado é resultado aceitável; `BLOCKED` medido também é.

---

## 3 · REGRESSÃO (obrigatória antes de qualquer coleta)

```
CONTRACT_VERSIONING = PASS · HUMAN_PROSE_READ_BY_RUNTIME = 0
FACT_TIME_FABRICATED = 0 · FACT_LOCATION_FABRICATED = 0
REMOTE_CAPABILITIES_WITHOUT_GATE = 0
LINKEDIN_BIG_COLLECTION_ELIGIBLE = 0 · INSTAGRAM_REMOTE_COLLECTION_ALLOWED = 0
YOUTUBE sem regressão · NEW_FAILURES = 0 · SYSTEM_MAP_CHECK = PASS
```

`NEW_FAILURES` compara-se **por nome** contra o baseline em `606974c3`, não por
contagem. Falha em zona que o teu diff nunca tocou é pré-existente — prova-o com
`git log` em vez de a corrigires. Regenera o System Map pela cadeia canónica
(`AGENTS.md` manda) e confere o carimbo **depois** de commitar.

---

## 4 · DEPOIS: censo, contratos novos, e só então BIG COLLECTION 2

Só com o motor estável: recenseia **todas** as fontes italianas de novo
(`TOTAL_IT_SOURCES`), classificando cada uma em `READY_NOW` ·
`NEEDS_CONTRACT_ONLY` · `NEEDS_SMALL_ADAPTATION` · `NEEDS_NEW_CAPABILITY` ·
`BLOCKED_EXTERNAL` · `NOT_COLLECTABLE` · `UNKNOWN`. **Não reutilizes o censo
antigo automaticamente.**

Cria contratos novos em **lotes por padrão** (nunca fonte a fonte quando a
família é a mesma) só para fontes que: usam estratégia já provada · têm endpoint
real · têm identidade provável · **não** exigem credencial nova · **não** exigem
gasto · **não** exigem política nova. Regista `BATCH_ID · SOURCES · STRATEGY ·
IDENTITY_STRATEGY · CONTRACTS_CREATED · CONTRACTS_VALID · CANARIES_PASS`.

Endpoint desatualizado pode ser corrigido quando a rota nova for **provada**
(`OLD_ENDPOINT · NEW_ENDPOINT · PROOF · CONTRACT_UPDATED`). A SOURCE continua a
mesma. Não apagues histórico.

**ORCID/OpenAlex (36):** se a classificação `NORMAL_ACQUISITION` vs
`EXTERNAL_REFERENCE` ainda for decisão real de owner, escreve
`ORCID_36_TOUCHED = NO` e segue. Não deixes as 36 travarem a missão.

**GATE PARA BIG COLLECTION 2** — executa-a **só** se todos verdadeiros:
`CONTRACT_VERSIONING = PASS` · `NEW_FAILURES = 0` · `SYSTEM_MAP_CHECK = PASS` ·
`REMOTE_CAPABILITIES_WITHOUT_GATE = 0` · `FACT_TIME_FABRICATED = 0` ·
`FACT_LOCATION_FABRICATED = 0` · `SOURCE_CONTRACT_HASH_PRESENT = YES` ·
`CONFIG_HASH_PRESENT = YES` · `ALL_SELECTED_SOURCES_HAVE_EXECUTABLE_CONTRACT = YES` ·
`ALL_SELECTED_SOURCES_HAVE_IDENTITY_PATH = YES` · `PAID_USD_PLANNED = 0`.

Se um falhar: **não corras a Big Collection**, reporta qual e porquê.

Na Big Collection 2, não recolhas conteúdo idêntico só para aumentar contagem.
Depois: fluxo canónico de Admission + Sala **sem alterar a régua**, reconciliação
(todos os contadores estruturais a 0) e a medição de tempo/local, preservando
`FACT_TIME != PUBLISHED_AT`, `SOURCE_LOCATION != FACT_LOCATION`,
`PLACE_MENTION != FACT_LOCATION`.

**CLAIM/FACT:** `CLAIM_FACT_LAYER_IMPLEMENTED = NO` e
`COLLECTION_GAP_CLAIM_FACT = YES`. **NÃO implementes.** Só mede outra vez e
preserva o gap.

---

## 5 · COMMITS

Commits pequenos e coerentes por checkpoint: testes → commit → push → continuar.
**NUNCA force-push.** No fim: `LOCAL == REMOTE = YES`, ou explica precisamente
porquê. A branch **não** entra no trunk nesta missão.

## 6 · HARD STOPS

Só páras antes do fim por: risco real de perda de dados · gasto pago ·
credencial obrigatória ausente · política/permissão não medida · decisão
semântica realmente nova de owner · corrupção não reconciliável.
**Problema técnico pequeno: resolve e continua.**

## 7 · ENTREGA

Escreve o relatório final em `RELATORIO-CUTOVER-RECUPERADO.md` na raiz da
bancada (sobrevive à janela do terminal) **e** no teu último turno, com:

`INITIAL_HEAD · FINAL_HEAD · REMOTE_HEAD · WORKTREE · STALL_RECOVERY ·
WORK_RECOVERED · CONTRACT_VERSIONING · LEGACY_DISCOVERY_CASES_BEFORE/AFTER ·
LEGACY_IDENTITY_CASES_BEFORE/AFTER · SOURCES_MIGRATED_LEGACY ·
LEGACY_SOURCES_BLOCKED · TOTAL_IT_SOURCES · READY_BEFORE/AFTER ·
NEW_CONTRACTS_CREATED · NEW_READY_SOURCES · NEW_CAPABILITIES_CREATED ·
SOURCES_UNLOCKED · BIG_COLLECTION_2_RUN_ID · SOURCES_ATTEMPTED/SUCCEEDED/FAILED ·
NEW_SOURCES_ATTEMPTED/SUCCEEDED · RAW_OBSERVATIONS_CREATED · DERIVED_CREATED/REUSED ·
ADMISSION_SIM/NAO_SEI/NAO_SE_APLICA/ERRO · SALA_BEFORE/AFTER/NEW_SALA_ITEMS ·
RECONCILIATION_STRUCTURAL_ERRORS · FACT_TIME_KNOWN/UNKNOWN ·
FACT_LOCATION_KNOWN/UNKNOWN · FACT_TIME_FABRICATED · FACT_LOCATION_FABRICATED ·
LINKEDIN_BIG_COLLECTION_ELIGIBLE · INSTAGRAM_REMOTE_COLLECTION_ALLOWED ·
YOUTUBE_COLLECTION_E2E · CLAIM_FACT_LAYER_IMPLEMENTED · COLLECTION_GAP_CLAIM_FACT ·
PAID_USD · NEW_FAILURES · SYSTEM_MAP_CHECK · COLLECTION_PIPELINE_INTEGRITY ·
COLLECTION_COVERAGE · POST_COLLECTION_RECONCILIATION ·
COVERAGE_READY_PERCENT_BEFORE/AFTER · COMMITS_CREATED · PUSH_STATE ·
KNOW_HOW_DELTA · MODEL_EFFECTIVE · NEXT_5_HIGHEST_LEVERAGE_GAPS`

Valor não medido escreve-se `NOT_MEASURED` ou `UNKNOWN` — **nunca** um número
plausível. Fase que não chegaste a executar declara-se `NOT_REACHED`, e isso é
resultado honesto, não falha.

**Fecha com uma secção em português simples, sem jargão**, para o dono do
projeto, que não é engenheiro: de onde a sessão foi recuperada, quantas fontes
ficaram prontas, quantas foram recolhidas, quanto entrou na Sala, e o que ainda
impede as restantes.
