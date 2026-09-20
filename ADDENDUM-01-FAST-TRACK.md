# ADDENDUM-01 — FAST TRACK COLLECTION

**PRECEDÊNCIA: `ADDENDUM-01` > `MISSAO-CUTOVER-RECUPERADA.md`.**
Onde este ficheiro contradiz o briefing original, **este manda**. Tudo o que ele
não menciona continua a valer.

**NÃO reinicies. NÃO abras missão paralela. NÃO faças reset.** Continua de onde
estás, com o contexto que já tens.

---

## DECISÃO DO DONO: PRECISAMOS AVANÇAR AGORA

O objetivo prioritário passa a ser, por esta ordem:

1. terminar o cutover atual (**já está** — ver abaixo)
2. incluir o maior número possível de fontes novas
3. executar BIG COLLECTION 2
4. popular a Sala
5. entregar cobertura real

**A regra nova de alocação do teu tempo:**

```
MEDIR O MÍNIMO NECESSÁRIO → IMPLEMENTAR → CANÁRIO → TESTE NORMAL
→ COMMIT → PUSH → SEGUIR
```

E **não**:

```
MEDIR → RED TEAM → RED TEAM DO RED TEAM → NOVO CENSO → NOVA ARQUITETURA
→ MAIS UMA PROVA → SÓ ENTÃO EXECUTAR
```

Investigação profunda **só** quando houver **FAIL REAL**.

### A escolha, dita explicitamente pelo dono

| entre isto | e isto | escolhe |
|---|---|---|
| mais uma auditoria | libertar 20 fontes e recolhê-las | **a segunda** |
| provar pela quinta vez que o motor funciona | criar contratos para fontes novas | **criar os contratos** |
| esperar resolver 214/214 | correr Big Collection com 60 prontas | **correr com as 60** |

---

## O QUE JÁ ESTÁ PROVADO — NÃO REMEDIR SEM MOTIVO

Medido pelo coordenador em `f1ca99ee`, e pelo teu próprio trabalho:

```
LEGACY_DISCOVERY_CASES  7 → 0        LEGACY_IDENTITY_CASES  7 → 0
grep 'case "IT-' em italy_pilot_collect.mjs = 0
ACQUISITION contracts = 8            IDENTITY contracts = 8
CONTRACT_VERSIONING = PASS 19/19     SOURCE_CONTRACT_VERSION = italy-contracts-v2
CUTOVER = CONCLUÍDO
```

**NÃO refaças o cutover. NÃO repitas os 19 testes se nada relacionado mudou.
NÃO abras novo censo arquitetural da Collection.**

---

## FASE 0 — FECHA O QUE ESTÁ ABERTO E EMPURRA

Estado medido pelo coordenador agora (confirma, não confies):

```
HEAD        = a41ea8b47ba9b479aa79ec4286780614b8105276
REMOTE_HEAD = ad53edfa7c0478b3d52df348bdf610356cc3838f
AHEAD       = 2 commits por empurrar · BEHIND = 0
WORKTREE    = limpa (só o ficheiro da missão, untracked)
```

Estás no carimbo do System Map. **Fecha-o e empurra.** Gate mínimo:

```
NEW_FAILURES = 0        SYSTEM_MAP_CHECK = PASS
```

⚠️ **O `SYSTEM_MAP_CHECK` continua obrigatório** — o dono manteve-o na lista
curta. Mas tem um tecto: se o carimbo não fechar em tempo razoável, **não
escaves a cadeia do mapa indefinidamente**. Regista o estado exacto com o nome
do problema, empurra o que está verde, e segue para a FASE 1. Um carimbo por
fechar não pode consumir a janela inteira.

---

## FASE 1 — CENSO RÁPIDO, ORIENTADO A EXECUÇÃO

Usa o motor novo para classificar todas as fontes italianas. **Não é estudo
longo.** Por fonte, só isto:

`SOURCE_ID · SOURCE_TYPE · ENDPOINT · ROUTE_FAMILY · IDENTITY_FAMILY ·
CONTRACT_STATUS · READY_NOW · BLOCK_REASON`

Classes: `READY_NOW · NEEDS_CONTRACT_ONLY · NEEDS_SMALL_ADAPTATION ·
NEEDS_NEW_CAPABILITY · EXTERNAL_BLOCK · POLICY_BLOCK · UNKNOWN`

Entrega os totais e passa à frente.

## FASE 2 — CONTRATOS NOVOS EM LOTE

Prioridade máxima às fontes que cabem nas estratégias **já provadas**:
`STATIC_ENDPOINT · TEMPLATE_ENUMERATION · HTML_LINK_DISCOVERY`, com as
estratégias de `IDENTITY` já implementadas.

**Não tratar uma a uma quando há padrão comum.** Agrupa por `DOMAIN ·
SOURCE_TYPE · ROUTE_FAMILY · IDENTITY_FAMILY · OUTPUT_TYPE`. Podes criar
**dezenas** de contratos na mesma etapa se derivarem do mesmo padrão provado.

Por lote: `BATCH_ID · SOURCE_COUNT · CONTRACTS_CREATED · CONTRACTS_VALID`.

## FASE 3 — PROVA MÍNIMA POR LOTE

**Sem red team por fonte. Sem mutation suite nova por lote.**

1. validação determinística de **todos** os contratos do lote;
2. **1 ou 2 canários reais** por padrão;
3. canários verdes + contratos estruturalmente equivalentes → **liberta o lote**.

Gate por lote: `CONTRACT_VALID = YES · IDENTITY_PATH = YES · ROUTE_RESOLVED = YES
· NO_PAID_ROUTE = YES · NO_POLICY_BLOCK = YES`.

## FASE 4 — PEQUENAS ADAPTAÇÕES: AUTORIZADAS

Se uma pequena adaptação libertar **≥ 5 fontes** (ou benefício equivalente
medido), **implementa já, sem pedir aprovação nova**: provider simples · family
adapter · variante de HTML/PDF já existente · leitura de metadata já disponível
· correção de endpoint · identidade reutilizável.

**NÃO criar framework novo.**

## FASE 5 — ENDPOINTS MORTOS

Corrige depressa quando a rota nova for **provável e provada**. Regista
`SOURCE_ID · OLD_ENDPOINT · NEW_ENDPOINT · PROOF · CONTRACT_UPDATED`. A SOURCE
continua a mesma. Casos conhecidos: ARPAE (AGRIOS já corrigido).

## FASE 6 — CASOS DIFÍCEIS NÃO TRAVAM O LOTE

Fonte que exija credencial · pagamento · browser complexo · policy nova ·
capability grande · decisão arquitetural: **classifica e segue.**

> **Não deixes uma fonte bloquear cinquenta.**

## FASE 7 — ORCID/OPENALEX

Se `NORMAL_ACQUISITION` vs `EXTERNAL_REFERENCE` ainda não estiver
inequivocamente resolvido: escreve `ORCID_36_TOUCHED = NO` e **continua**. As
outras fontes têm prioridade. Não gastes a janela nisto.

## FASE 8/9 — LINKEDIN · INSTAGRAM · YOUTUBE

Não desenvolver LinkedIn/Instagram nesta missão. Preserva
`LINKEDIN_BIG_COLLECTION_ELIGIBLE = 0` e
`INSTAGRAM_REMOTE_COLLECTION_ALLOWED = 0` — e **não deixes isso travar a Big
Collection**. YouTube: preserva a rota já provada; se estiver recente, **não
voltes a descarregar o mesmo áudio** — conta como cobertura recente.

---

## FASE 10 — GATE RÁPIDO PARA BIG COLLECTION 2

**Sem red team amplo novo.** Obrigatório apenas:

```
CONTRACT_VERSIONING = PASS          NEW_FAILURES = 0
SYSTEM_MAP_CHECK = PASS             REMOTE_CAPABILITIES_WITHOUT_GATE = 0
ALL_SELECTED_SOURCES_HAVE_EXECUTABLE_CONTRACT = YES
ALL_SELECTED_SOURCES_HAVE_IDENTITY_PATH = YES
FACT_TIME_FABRICATED = 0            FACT_LOCATION_FABRICATED = 0
PAID_USD_PLANNED = 0
```

Se PASS: **RODA.** Não acrescentes gates que o dono não pediu.

## FASE 11 — BIG COLLECTION 2

> **Não esperes chegar a 214. Se 40 estão prontas, recolhe 40. Se 80, recolhe 80.**

Seleciona: fontes novas READY · fontes antes falhadas agora corrigidas · fontes
vencidas pela cadência · backfill seguro · conteúdo novo provável.

Evita descarregar bytes idênticos quando checkpoint/hash já prova frescura.

## FASE 12 — JANELA HISTÓRICA

Não inventes 90 dias globais — mas **não deixes a falta de política histórica
impedir a recolha do presente**. Sem backfill definido: `MODE = CURRENT /
LATEST_AVAILABLE`, `BACKFILL_STATUS = NOT_DEFINED`, e segue. Onde o histórico
for claramente descobrível e barato, podes fazer backfill seguro e registar a
janela real.

## FASES 13–16 — RESULTADO, ADMISSION, SALA, RECONCILIAÇÃO

Admission canónica: **NÃO alteres a régua para aumentar o SIM.** Conta
`SIM · NAO_SEI · NAO_SE_APLICA · ERRO`.

Sala, gate mínimo: `SIM_WITHOUT_SALA = 0 · SALA_WITHOUT_SIM = 0 ·
NAO_SEI_IN_SALA = 0 · NAO_SE_APLICA_IN_SALA = 0`.

Reconciliação: só integridade estrutural essencial (`RAW_SEM_RUN`,
`RAW_SEM_SOURCE`, `RAW_SEM_STORAGE`, `ZERO_BYTE_RAW`, `WRONG_MEDIA_TYPE`,
`MISSING_LINEAGE`, `ORPHAN_ADMISSION`, `ORPHAN_SALA`). **Se der tudo zero, não
faças auditoria adicional.**

## FASE 17–18 — TEMPO, LOCAL, CLAIM/FACT

Mede, **não corrijas artificialmente**. `UNKNOWN` é aceitável e não trava nada.
`FACT_TIME_FABRICATED = 0` e `FACT_LOCATION_FABRICATED = 0` continuam a ser
**linha vermelha**: preservar o UNKNOWN honesto é obrigatório, inventar uma data
para parecer completo reprova a missão.

`CLAIM_FACT_LAYER_IMPLEMENTED = NO` · `COLLECTION_GAP_CLAIM_FACT = YES` — **não
implementes.** Não inicies Intelligence. Não inicies Portal.

## FASE 20 — COMMITS

**Commits pequenos por lote útil. Push frequente. Sem force.** Não esperes o fim
da missão para gravar: a sessão anterior morreu e quase levou o trabalho com ela.

---

## HARD STOP — só estes

risco real de perda de dados · gasto pago · credencial obrigatória ausente ·
policy/permissão não medida · corrupção · **regressão real** · decisão semântica
nova que mude a arquitetura.

**Todo o resto: resolve e continua.**

---

## ENTREGA

Mantém `RELATORIO-CUTOVER-RECUPERADO.md` como ficheiro de entrega (sobrevive à
janela do terminal) e acrescenta-lhe os campos da FASE 21 do addendum:
`TOTAL_IT_SOURCES · READY_BEFORE/AFTER · NEW_CONTRACTS_CREATED ·
NEW_READY_SOURCES · NEW_SMALL_ADAPTATIONS · SOURCES_UNLOCKED_BY_ADAPTATIONS ·
BIG_COLLECTION_2_RUN_ID · SOURCES_SELECTED/ATTEMPTED/SUCCEEDED/FAILED ·
NEW_SOURCES_ATTEMPTED/SUCCEEDED · RAW_OBSERVATIONS_CREATED ·
STORAGE_OBJECTS_CREATED/REUSED · DERIVED_CREATED/REUSED · BYTES_COLLECTED ·
ADMISSION_* · SALA_BEFORE/AFTER/NEW_SALA_ITEMS · RECONCILIATION_STRUCTURAL_ERRORS ·
FACT_TIME_KNOWN/UNKNOWN · FACT_LOCATION_KNOWN/UNKNOWN ·
COVERAGE_READY_PERCENT_BEFORE/AFTER · SOURCES_STILL_BLOCKED · TOP_10_BLOCKERS ·
PAID_USD · COMMITS · PUSH_STATE · KNOW_HOW_DELTA · MODEL_EFFECTIVE`

Valor não medido = `NOT_MEASURED`. Fase não alcançada = `NOT_REACHED`. **Nunca
um número plausível.** Fecha com a secção em português simples para o dono.
