# MISSÃO — FECHAR OS 3 GARGALOS DA BIG COLLECTION 2

**STORAGE → TESTES → HTML JULGÁVEL.** Missão de **estabilização e
aproveitamento do que já foi colhido**. Execução rápida, sem red team
desnecessário.

BANCADA: `C:/Users/London1/orca/workspaces/eame-sintonia/cutover-v2`
BRANCH: `claude/contract-provenance-cutover-v1`

**A Big Collection 2 TERMINOU. Não corras outra.**

---

## 0 · O QUE O COORDENADOR MEDIU AGORA — confirma, não confies

Medido por mim imediatamente antes deste despacho:

```
BRANCH      = claude/contract-provenance-cutover-v1
HEAD        = b4ff70ae4060ec04d718d6e68602c95ba9dc36fa
REMOTE_HEAD = b4ff70ae4060ec04d718d6e68602c95ba9dc36fa   (0/0, sincronizado)
DIRTY       = 0 ficheiros — bancada limpa
```

**Storage, medido no disco:**

```
XX/ (dentro da worktree)                     86 ficheiros · 68 MB
~/sintonia-sala-italia/acervo-coletor-bc2/   93 ficheiros · 77 MB
```

**O defeito, confirmado por mim no código — 4 chamadas, não 3:**

```
tests/test_estagio_atravessa_a_fronteira.py:70    rmtree(RAIZ/"XX", True)
tests/test_estagio_atravessa_a_fronteira.py:367   rmtree(RAIZ/"XX", True)
provas/so_a_colheita_atravessa.py:195             rmtree(RAIZ/"XX")
tests/test_estagio_atravessa_a_fronteira.py:366   rmtree(RAIZ/adapter.BALCAO)
```

⚠️ **`XX/` está DENTRO da worktree e é o `ArmazemLocal(RAIZ)` da porta
canónica.** `ArmazemLocal` é referenciado por ≥10 ficheiros (`coleta/ingresso.py`,
`orquestrador/orquestrador.py`, `guarda/preservar_coleta.py`, e as provas).
Corrigir num sítio só não fecha o defeito.

Estado do fecho anterior (do relatório, a reconfirmar): `READY_NOW = 113/170` ·
`SALA 4→17` · `ADMISSION SIM 13 · NAO_SEI 81 · NAO_SE_APLICA 14 · NAO 4` ·
`DERIVED_NOT_APPLICABLE_HTML = 58` · `NEW_FAILURES = 10` ·
`RECONCILIATION_STRUCTURAL_ERRORS = 0` · `PAID_USD = 0`.

---

## FASE 1–2 · O OWNER DO STORAGE, E A SEPARAÇÃO

Lê Bíblia/Know-how/migrations/persistência e responde:
`OPERATIONAL_STORAGE_OWNER · OPERATIONAL_STORAGE_ROOT · TEST_STORAGE_OWNER ·
TEST_STORAGE_ROOT`.

**Se o owner já existe, USA-O. NÃO inventes um segundo storage.** Se a
arquitetura já deixa o root configurável, usa essa configuração; se não deixa,
implementa a **menor** separação necessária.

> **REGRA: TESTE NUNCA PODE APAGAR STORAGE OPERACIONAL.**

Teste destrutivo só pode correr sobre diretório **criado pelo próprio teste**.
Acrescenta guarda defensiva que **falha fechado** se o alvo da limpeza parecer
storage operacional. Não confies só no nome da pasta se houver forma melhor de
provar o escopo.

## FASE 3 · RESTAURAR E PROVAR

Por cada objeto que deva ter bytes: `STORAGE_ID · PATH · SHA256_DB ·
SHA256_BYTES · STATUS` ∈ `PRESENT_MATCH · PRESENT_MISMATCH · MISSING_EXPECTED ·
NO_BYTES_EXPECTED`.

**NÃO inventes bytes para tentativas falhadas** — os 21 sem documento continuam
`NO_BYTES_EXPECTED`. Meta: `PRESENT_MISMATCH = 0 · MISSING_EXPECTED = 0`. Se
houver missing real, investiga a linhagem antes de continuar.

## FASE 4 · PROVA DE NÃO-DESTRUIÇÃO

Fixture sentinela no storage operacional → corre a suíte destrutiva → prova que
a sentinela **sobreviveu** e que só o temporário do teste morreu.

```
Gate: TEST_CAN_DELETE_OPERATIONAL_STORAGE = NO
```

---

## FASE 5 · AS 10 EXPECTATIVAS OBSOLETAS

> **NÃO troques `7 → 113` nem outro número mágico.**

Por cada falha: `TEST · OLD_EXPECTATION · WHY_STALE · REAL_INVARIANT`.

Prefere invariantes verdadeiros — *o conjunto contém o item esperado* · *nenhum
SOURCE_ID duplicado* · *o número deriva da fixture* · *o contrato respeita o
schema* · *a relação entre conjuntos está certa* — em vez de `TOTAL == N` quando
`N` depende do acervo. **Contagem fixa só sobrevive quando a própria fixture
define aquele universo.**

⚠️ Uma das 10 é um **conflito de lei antigo** (`SEEN_AGAIN` com `RAW_PATH`), não
um snapshot. Essa resolve-se decidindo qual lei vale, e a decisão fica escrita —
não se resolve ajustando número.

Meta: `NEW_FAILURES = 0` na suíte inteira. Se uma delas exigir decisão de dono,
**declara-a** em vez de a forçar.

## FASE 6 · RECONCILIAR OS CONTADORES

Divergências a explicar (**não a igualar à força**):
`113 attempted vs 111 runs` · `90 succeeded vs 91 healthy` · `23 vs 20 failed` ·
`116 RAW no banco vs 114 no ledger vs 93 raw_objects_created`.

Por métrica: `NAME · OWNER · GRAIN · WHAT_IT_COUNTS · INCLUDES_RETRY? ·
INCLUDES_CANARY? · INCLUDES_NO_DOCUMENT? · INCLUDES_REUSED_STORAGE? ·
INCLUDES_PREEXISTING? · TIME_WINDOW`.

Entrega o quadro canónico: `REQUESTS_SELECTED · SOURCE_REQUESTS_EXECUTED ·
RUNS_CREATED · SOURCES_WITH_SUCCESS · SOURCES_WITH_FAILURE ·
RAW_OBSERVATIONS_CREATED · STORAGE_OBJECTS_CREATED · STORAGE_OBJECTS_REUSED`.

**Grão diferente documenta-se e fica diferente. Bug real corrige-se no owner.**

---

## FASE 7–9 · OS 58 HTML

Primeiro **descobre porquê** — não assumas. Causa ∈ A) RAW já traz texto útil ·
B) falta extractor HTML→texto · C) extractor existe mas a rota não o chama ·
D) Admission lê outra representação · E) HTML é só envelope/navegação · F) outra.

**Antes de escreveres parser:** procura capacidade existente (HTML, DOM, article
extraction, readability, normalização de texto, metadata, JSON-LD). Se existir,
**liga-a ao fluxo canónico**. `NÃO CRIES UM SEGUNDO PARSER.`

Objetivo: HTML com conteúdo útil chega a uma representação que a Admission
consiga julgar (`RAW HTML → DERIVED TEXT/STRUCTURED → Admission`), **respeitando
a arquitetura real** — não tornes DERIVED obrigatório onde não é.

Por documento: `RAW_ID · SOURCE_ID · HTML_KIND · CONTENT_EXTRACTABLE ·
DERIVATION_RESULT · TEXT_BYTES · ADMISSION_INPUT_READY`.

## FASE 10 · A RÉGUA NÃO SE TOCA

**PROIBIDO:** mudar keyword · threshold · universo · regra · transformar
`NAO_SEI` em `SIM` por decreto.

> **A missão é dar à régua material julgável. Depois a régua decide.**

Um `NAO_SEI` que continua `NAO_SEI` depois de o documento ser legível é
resultado honesto.

## FASE 11–12 · CANÁRIO E REPROCESSAMENTO SEM REDE

Canário em amostra real: uma página claramente conteudística, uma complexa, e
uma sem conteúdo útil. Gate `HTML_PIPELINE_CANARY = PASS` antes de aplicar aos 58.

⚠️ **Os HTML JÁ FORAM COLHIDOS. Reprocessa a partir do RAW existente.**

```
Gate: NETWORK_ACQUISITION_CALLS_DURING_REPROCESS = 0
```

Mede: `HTML_REPROCESS_ATTEMPTED · HTML_DERIVED_CREATED · HTML_DERIVED_REUSED ·
HTML_STILL_NOT_APPLICABLE · HTML_DERIVED_FAILED`.

## FASE 13–15 · ADMISSION, SALA, RECONCILIAÇÃO

Admission só nos itens afetados, **sem mudar regra**, com contagem antes/depois.
Sala: só `SIM` novos entram — `SIM_WITHOUT_SALA = 0 · SALA_WITHOUT_SIM = 0 ·
NAO_SEI_IN_SALA = 0 · NAO_SE_APLICA_IN_SALA = 0`.

Reconciliação (esperado **0** em todos): `RAW_SEM_RUN · RAW_SEM_SOURCE ·
RAW_SEM_STORAGE · ZERO_BYTE_RAW · MISSING_EXPECTED_BYTES · SHA_MISMATCH ·
ORPHAN_DERIVED · ORPHAN_ADMISSION · ORPHAN_SALA`.

## FASE 16–17 · TESTES E MAPA

Suíte completa: `PRISTINE_FAILURES · FINAL_FAILURES · NEW_FAILURES` (meta **0**),
e **prova outra vez** `TEST_CAN_DELETE_OPERATIONAL_STORAGE = NO`.

Se houve mudança estrutural, regenera pela cadeia canónica →
`SYSTEM_MAP_CHECK = PASS`. Know-how **só** para descobertas duráveis: isolamento
test↔operational storage · proibição de contagem fixa sobre acervo mutável ·
significado canónico dos contadores · tratamento canónico do HTML.

---

## NÃO FAZER

Nova Big Collection · fontes novas · Source Curator · ORCID ·
LinkedIn/Instagram · CLAIM/FACT · **Intelligence** · **Portal**.

## HARD STOP

Só por: gasto · credencial · policy/permissão · risco real de perda ·
regressão real · corrupção · decisão arquitetural nova indispensável.
**HARD STOP ao concluir** — não continues para outra missão.

## ENTREGA

Escreve em `RELATORIO-GARGALOS-BC2.md` na raiz **e** no último turno:
`INITIAL_HEAD · FINAL_HEAD · REMOTE_HEAD · WORKTREE · OPERATIONAL_STORAGE_ROOT ·
TEST_STORAGE_ROOT · OPERATIONAL_BYTES_EXPECTED/PRESENT · MISSING_EXPECTED_BYTES ·
SHA_MISMATCH · TEST_CAN_DELETE_OPERATIONAL_STORAGE · STALE_TESTS_FOUND/FIXED ·
PRISTINE_FAILURES · FINAL_FAILURES · NEW_FAILURES ·
BIG_COLLECTION_METRICS_RECONCILED · METRIC_GRAINS · HTML_NOT_APPLICABLE_BEFORE ·
HTML_REPROCESS_ATTEMPTED · HTML_DERIVED_CREATED/REUSED/FAILED ·
HTML_STILL_NOT_APPLICABLE · ADMISSION_BEFORE/AFTER · NEW_SIM · NEW_SALA_ITEMS ·
NETWORK_ACQUISITION_CALLS_DURING_REPROCESS · RECONCILIATION_STRUCTURAL_ERRORS ·
SYSTEM_MAP_CHECK · COMMITS · PUSH_STATE · KNOW_HOW_DELTA · MODEL_EFFECTIVE`

Não medido = `NOT_MEASURED`. Não alcançado = `NOT_REACHED`. **Nunca um número
plausível.**

Commits pequenos, push frequente, sem force — a sessão da madrugada já caiu uma
vez com trabalho por gravar.

Fecha com a secção em **português simples** para o dono, que não é engenheiro,
respondendo exactamente a isto: (1) onde os documentos ficam guardados agora;
(2) porque é que os testes já não conseguem apagá-los; (3) o que eram as 10
falhas; (4) porque é que 113 e 111 eram números diferentes; (5) quantas das 58
páginas conseguimos finalmente ler; (6) quantas mudaram de veredito depois de
serem realmente lidas.
