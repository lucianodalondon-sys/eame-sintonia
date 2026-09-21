# RELATÓRIO — SOURCE-CURATOR-INTEGRATION

**Bancada:** `source-curator-integration-v1` · **Base:** `3c0ad4d7` (fim da BIG-COLLECTION-RELEASE)
**Lane integrada:** `claude/source-curator-lifecycle-v1 @ d21e8e43` · **Data:** 2026-09-20

> **INTEGROU-SE O MOTOR. A FOTOGRAFIA FICOU COMO HISTÓRIA.**
> Depois desta missão: **SOURCE CURATOR prepara · COLLECTION coleta.**

---

## 0 · O QUE O COORDENADOR MEDIU — reconfirmado

| medição | coordenador | reconfirmado aqui | veredito |
|---|---|---|---|
| COLLECTION `big-collection-release-v1` HEAD | `3c0ad4d7`, local == remote, dirty 0 | `3c0ad4d7` == `origin/big-collection-release-v1`; 1 ficheiro não rastreado (o despacho desta missão) | ✅ igual |
| SOURCE_CURATOR `claude/source-curator-lifecycle-v1` HEAD | `d21e8e43`, local == origin | `d21e8e43` local == origin | ✅ igual |
| `MERGE_BASE` | `606974c3` → curator 9 · collection 37 | `606974c3` → 9 · 37 | ✅ igual |
| `7857d7b7` (rota YouTube) é ancestral de `d21e8e43`? | FALSO | FALSO | ✅ igual — a lane do curator **não** tem a rota nova |
| `curadoria/` nesta linha | (não medido) | **já existiam 18 ficheiros de registo**, byte a byte iguais aos da lane (incluindo `READY-FOR-COLLECTION-V1.json`, a fotografia) — trazidos pela 04A como registo, sem os `.py` | ⚠️ novo: a fotografia já estava cá; o perigo era o `semear_lifecycle.py` original lê-la |

---

## 1 · O ESTADO REAL, MATERIALIZADO ANTES DO MERGE

`curadoria/estado_actual_das_fontes.mjs` → `curadoria/ESTADO-ACTUAL-DAS-FONTES-V1.json` (derivado, regenera-se). Lê o
registo que a Collection executa (`regras/italy_contracts.mjs`, conferido por `conferirAquisicao` + `conferirIdentidade`), a
ficha no Atlas, o executor do território (`pedido/receitas.py`), o canário mais recente e o resultado da BCR-2026-09-20 lido
do `RUN-MANIFEST.json` e conferido contra a tabela §6.3 do relatório anterior.

```text
CURRENT_SOURCE_IDS   186 contratos (173 na tabela onboarded + 13 à mão) · 242 fichas IT no Atlas · 49 fichas sem contrato
CURRENT_CONTRACTS    182 executáveis · 4 sem bloco executável (IT-T1-001, IT-T7-002, IT-T9-008, IT-T8-001)
CURRENT_ROUTES       50 YouTube = /channel/<CHANNEL_ID>/videos (CUSTOM_ADAPTER CANAL_PUBLICO_YOUTUBE_V1) · 105 HTML_LINK_DISCOVERY
                     · 4 STATIC_ENDPOINT · 1 TEMPLATE_ENUMERATION (entre as READY)
CURRENT_READY        181 pela regra da casa (executável ∧ ficha ∧ executor) — bate com a âncora
CURRENT_LAST_RESULTS BCR-2026-09-20: 181 corridas · SUCCESS 151 · ROUTE_FAILURE 20 · 429 9 · CAPABILITY_GAP 1
                     · 0 divergências com a tabela do relatório anterior (a 1.ª leitura dava 150/21: IT-T3-011 tem 2 itens
                       IDENTITY_FAILED e colheu os outros — avaria de item, não de fonte; regra corrigida e conferida)
GATE_WATCH = True · GATE_FEED_XML = False   (lidos do censo YOUTUBE-CANARIO-50-2026-09-20.json)
```

Todas as âncoras da missão (181 · 50/50 · 151/30 · 20/9/1) reapareceram na medição própria. Nenhuma foi copiada.

---

## 2 · O QUE ENTROU, O QUE FICOU, O QUE MUDOU

**MOTOR (entrou):**

| ficheiro | de `d21e8e43` | como |
|---|---|---|
| `curadoria/lifecycle.py` · `fila.py` · `test_lifecycle.py` · `provar_autonomia.py` | `git checkout d21e8e43 --` | **intactos** |
| `curadoria/worker.py` | adaptado | sem `gate_de_rota`/`canario`: `PORTAO = coleta/scrap_http.permitido` (o único leitor de robots da casa; a guarda `test_so_um_ficheiro_le_o_robots` continua verde), `SONDA = canario_do_motor.mjs`; contratos do estado actual; **RETRY_AFTER → CANARY_PENDING → READY** (ver §6, defeito apanhado pela prova G); relógio injetado chega ao `adiar()` |
| `curadoria/interface_collection.py` | adaptado | a ficha do contrato vem do estado actual, nunca de `italy_contracts_curator.json`; mais três leituras (`estado_actual`, `esta_ready`, `ready_ids`) |
| `curadoria/semear_lifecycle.py` | **reescrito** | lê só `ESTADO-ACTUAL-DAS-FONTES-V1.json`; não lê `STATE` da fotografia para nenhuma fonte do registo (teste) |
| `curadoria/test_interface_collection.py` · `red_team_lifecycle.py` | adaptados | caminho do contrato; ataque 5 passou de «bate com a missão 04» para «bate com o estado actual e nenhuma YouTube parada» |
| `curadoria/evidencia.py` · `canario_do_motor.mjs` · `estado_actual_das_fontes.mjs` · `provar_divisao.py` | novos | um só escritor da prova; canário canónico pela porta do motor para qualquer contrato do registo; o materializador; as sete provas |
| `orquestrador/fontes_prontas.py` + 27 linhas em `orquestrador/orquestrador.py` | novos | o lado da Collection (§5) |

**FERRAMENTA (ficou na lane, de propósito):** `gate_de_rota.py` (2.º leitor de robots), `canario.py` (3.º fetcher), `amostrar.py`,
`atribuir_source_id.py`, `capturador.py`, `caracterizador.py`, `consolidar*.py`, `correr_lote.py`, `emparelhar_com_atlas.py`,
`escrever_*.py`, `manifesto_*.py`, `provar_lifecycle.py` (usava rede real e a fotografia), `validar_contratos.py`,
`veredito_ready.py`, `test_capturador.py`, `test_caracterizador.py`, `test_correr_lote.py`. São a curadoria manual das
missões 02–03; a 04A já tinha decidido «registo sim, ferramenta não», e a razão continua a valer.

**FOTOGRAFIA (não entrou como estado):** `LIFECYCLE-LEDGER-V1.json` (1597 linhas, com as 50 em ROUTE_BLOCKED),
`LIFECYCLE-QUEUE-V1.json`, `LIFECYCLE-EVIDENCE-V1.json`, `READY-SOURCES-V1.json`, `LIFECYCLE-PROOF/AUTONOMY/RED-TEAM-V1.json`
da lane **não foram copiados**. Os ficheiros com esses nomes nesta árvore nasceram aqui, do estado actual. Como história ficam
os 18 registos que a 04A já trouxera (declarados no mapa como `C-CURATOR-REGISTOS`, «história das missões 02 a 04») e a
referência ao commit `d21e8e43` para quem quiser ler o livro antigo.

**DELTA DO KNOW-HOW da lane** (`handoff/KNOW-HOW-DELTA-O-CICLO-DE-VIDA-DA-FONTE.md`): não copiado; as quatro lições estão
absorvidas em **§164** com atribuição ao commit de origem.

Conflitos de merge: nenhum — a integração foi semântica, ficheiro a ficheiro; nenhum ficheiro gerado foi resolvido à mão.

---

## 3 · RECONCILIAÇÃO — recalculada, não copiada

Vocabulário fechado enumerado antes de escrever (`lifecycle.ESTADOS`, 15 valores; `fila.TASK_TYPES`, 8): nenhum termo novo.
Tradução aplicada por `semear_lifecycle.py --recomecar` sobre o estado actual:

| condição medida hoje | estado no livro | n |
|---|---|---:|
| contrato sem bloco executável | `CONTRACT_PENDING` | 4 |
| executável, sem ficha no Atlas (IT-T3-005) | `SEMANTIC_REVIEW` (decisão humana) | 1 |
| executável + ficha + executor, prova PASS (BCR SUCCESS ou canário) → `CANARY_PENDING` → | `READY_FOR_COLLECTION` | 160 |
| … e a BCR viu `ROUTE_FAILURE` → Collection reporta (`OWNER=COLLECTION`, `EVIDENCE_REF=RUN_ID`) + `REPAIR` na fila | `DEGRADED` | 18 |
| … e a BCR viu `CAPABILITY_GAP` (IT-T5-032, `?` na pasta — B1) → DEGRADED → triagem do Curator | `CAPABILITY_BLOCK` | 1 |
| … e a BCR viu 429 (9 YouTube) → **continua READY**; a prova do 429 fica em `LIFECYCLE-EVIDENCE-V1.json` | (dentro dos 160) | 9 |
| READY pela regra, **sem** canário PASS nesta árvore e falha na BCR (IT-T5-002, IT-T7-014) → `CANARY` na fila | `CANARY_PENDING` | 2 |
| só na fotografia (sem contrato no registo), canário FAIL na missão 04 — **história** | `CONTRACTED_CANARY_FAILED` | 9 |
| **total no livro** | | **195** |

`RETRY_AFTER = 0 · POLICY_BLOCK = 0 · AUTH_BLOCK = 0 · UNKNOWN = 0 · CONTRACT_READY_ROUTE_BLOCKED = 0`. 403 transições, todas
com `OWNER`, `VERSION`, `OBSERVED_AT`, `REASON`; 160 promoções a READY com `EVIDENCE_REF` (151 citam a corrida real da BCR,
9 citam o censo YouTube de 18:46Z). Fila: 20 PENDING (18 `REPAIR` prioridade 80, 2 `CANARY` prioridade 50), 0 bloqueadas.

**As 49 fichas do Atlas sem contrato** não entram no livro: o ciclo de vida começa quando há contrato ou canário medido.
Ficam nomeadas em `ESTADO-ACTUAL-DAS-FONTES-V1.json → FICHAS_SEM_CONTRATO`.

**Porquê 160 e não 181.** 181 media «a casa sabe chegar» (regra); o livro mede «a casa provou que chega» (prova). A diferença
são exactamente as 21 fontes que a BCR viu falhar — 18 avariadas à espera de reparo, 1 parada por defeito da casa, 2 sem
nenhuma prova — nenhuma escondida, todas com a corrida citada.

---

## 4 · YOUTUBE — o gate

```text
YOUTUBE_EXPECTED = 50   YOUTUBE_RECONCILED = 50   YOUTUBE_READY = 50   YOUTUBE_DEGRADED = 0   YOUTUBE_BLOCKED = 0
rota vigente no livro: /channel/<CHANNEL_ID>/videos (CANAL_PUBLICO_YOUTUBE_V1) · GATE_WATCH = True · GATE_FEED_XML = False
prova de READY: 41 pela corrida real da BCR, 9 pelo censo YOUTUBE-CANARIO-50 (as 9 que apanharam 429 na coleta)
a fotografia continua a dizer CONTRACT_READY_ROUTE_BLOCKED = 50 — e não venceu (tests T01, T02, red team ataque 5b)
```

**IT-T8-001** (AgroNotizie, a possível 51.ª): `CONTRACT_PENDING` — contrato à mão sem bloco executável, não está nas 50, não
foi incorporada, não foi somada. `canario_do_motor.mjs IT-T8-001` devolve `CLASSE=CONTRACT` sem ir à rede.

---

## 5 · READY INTERFACE REAL

A Collection pergunta por `orquestrador/fontes_prontas.py` (três verbos: `ids_ready/lista_ready`, `exigir_ready`,
`reportar_avaria`) e o Curator responde de `curadoria/interface_collection.py::ready_sources()`, derivado do livro a cada
chamada. O orquestrador chama `exigir_ready` antes de a corrida nascer quando o pedido nomeia uma fonte e vai à rede
(`--seco`/`--so-a-porta` não pedem licença); fonte conhecida e não READY → recibo `FONTE_NAO_READY`, executor não chamado,
manifesto não escrito; fonte desconhecida pelo Curator → passa como passava (`CONHECIDA=False`: NÃO SEI ≠ bloqueio).

```text
READY_TOTAL_CURRENT = 160     READY_HTML = 105 (HTML_LINK_DISCOVERY)     READY_YOUTUBE = 50     READY_OTHER = 5 (4 STATIC_ENDPOINT + 1 TEMPLATE_ENUMERATION)
por lote:  LOTE-HTML-ARTIGO 66 · LOTE-YOUTUBE-CANAL 50 · LOTE-PDF-INDICE 33 · à mão 8 · LOTE-PDF-FIXO 3
por território: T1 15 · T2 24 · T3 11 · T4 1 · T5 40 · T7 27 · T8 4 · T9 8 · T10 13 · T11 3 · T12 14
mudou de 181: −18 DEGRADED (ROUTE_FAILURE na BCR: 15 EMPTY_LIST, 1 índice 503, 1 alvo 400, 1 alvo 404) −1 CAPABILITY_BLOCK (IT-T5-032) −2 CANARY_PENDING (IT-T5-002, IT-T7-014)
DEGRADED: IT-T1-004/012/014/015/017/020/023 · IT-T2-018/021/023 · IT-T3-017/021 · IT-T5-021 · IT-T10-002/006/008/014/016
```

Recibo do instante em `curadoria/READY-SOURCES-V1.json` (quem quer a lista viva chama a função).

---

## 6 · AS SEIS PROVAS DA NOVA DIVISÃO (+ backoff) — `curadoria/provar_divisao.py` → `LIFECYCLE-PROOF-V1.json`

Isoladas em tempdir; rede substituída na primitiva mais funda (`worker.PORTAO`, `worker.SONDA`); livro, fila, worker e
interface reais. **Cada prova tem a sua contraprova.** `PASS 7/7`, zero rede, livro da casa intocado.

| | prova | contraprova (a sonda diz «não») |
|---|---|---|
| A | VALIDATE_ROUTE → CANARY → READY com `EVIDENCE_REF` da etapa CANARY; história `[CANARY_PENDING, READY]` | robots barra → `CONTRACT_READY_ROUTE_BLOCKED` e o canário **não é chamado**; canário FAIL → `CONTRACTED_CANARY_FAILED` |
| B | `ready_sources()` devolve só a READY, com rota, capacidade e prova; **zero chamadas de rede durante** | (a lista é derivada: ver D) |
| C | Collection tenta `CANARY_PENDING→READY`, `DEGRADED→READY`, `REPAIRING→READY`: as três recusadas **pelo nome** («a Collection so pode marcar READY_FOR_COLLECTION -> DEGRADED») | controlo positivo: o mesmo guarda deixa o Curator promover |
| D | `source_repair_needed` → `ACEITE`, `DEGRADED` (owner COLLECTION), sai de READY no instante, `REPAIR` PENDING na fila do Curator | reportar fonte que não estava READY → `ACEITE=False`, nenhuma tarefa criada |
| E | a Collection itera 4 READY, B falha → reporta → **segue para a próxima**; 0 canários chamados pela Collection; o REPAIR fica PENDING | (B fica DEGRADED; ninguém a reparou) |
| F | o worker pega o REPAIR, canário novo PASS → `DEGRADED → REPAIRING → READY`, `EVIDENCE_REF` **novo** (etapa REPAIR), e a interface entrega a prova nova | decreto `DEGRADED→READY` recusado («por REPAIRING + canario, nao por decreto»); canário do reparo FAIL → não volta a READY |
| G | 429 em A → `WAITING_RETRY`, `NEXT_ATTEMPT_AT = t0+3600 s`; B, C, D ficam DONE **antes** desse instante, na mesma volta, **0,28 s de parede**; elegíveis aos 59 min: `[]`; aos 61: `[A]`; A volta e passa | (sem `sleep` de retry no worker — teste T07) |

**Dois defeitos do motor apanhados por G, corrigidos antes de entrar:** (a) `RETRY_AFTER → READY` directo — o guarda do
livro recusava e o worker rebentava; agora a espera acaba em `CANARY_PENDING` e só depois READY; (b) o relógio injetado não
chegava ao `adiar()`. Mais `provar_autonomia.py` (processo morto com `os._exit(97)`; 7/7) e `red_team_lifecycle.py`
(0 blockers em 11 ataques, sobre o livro da casa).

---

## 7 · BACKOFF — provado com fila real

`ESPERAR ≠ BLOQUEAR`: a tarefa adiada perde a elegibilidade e o worker pega a seguinte; nada dorme. Prova G acima (fila real,
quatro tarefas, relógio injetado, B/C/D DONE durante a espera de A, A volta sozinha) e teste
`T07_RetryNaoBloqueiaAFila` (afirma `< 5 s` de parede e ausência de `sleep(retry…)` no código).

---

## 8 · O QUE CONTINUA EXISTENTE E NÃO FOI TOCADO

B1–B12 do relatório anterior — todos. Em particular **B3** (34 derived failures / STORAGE_MISSING), os **518 NAO_SEI**, CROP,
LinkedIn, Instagram, Facebook, Portal, Intelligence. B1 foi apenas **citado** como razão do `CAPABILITY_BLOCK` de IT-T5-032;
B9 (os 20 ROUTE_FAILURE) ficou traduzido em 18 `REPAIR` + 2 `CANARY` na fila do Curator — **nenhum executado** (exigiria rede).
Nenhuma Big Collection nova. Zero pedidos de rede nesta missão.

---

## 9 · SYSTEM MAP

Baseline medido na árvore virgem **antes da primeira edição**: `SYSTEM_MAP_CHECK=PASS`, 212 peças (🟢32 🟡172 ⚪8).
Mudança de responsabilidade declarada: `curadoria` entrou em `_gavetas.GAVETAS`; nasceu a zona **`Z-CURADORIA`** (F-COLETA,
entre candidatas e fontes; linha 2b na tabela do `AGENTS.md`) com `C-CURATOR-LIFECYCLE`, `C-CURATOR-ESTADO-ACTUAL`,
`C-CURATOR-INTERFACE`, `C-CURATOR-PROVAS`, `C-CURATOR-REGISTOS`; e `C-PORTA-FONTES-PRONTAS` (gate) em `Z-ORQUESTRADOR`.
Arestas medidas pelo scanner: `C-CURATOR-INTERFACE → C-PORTA-FONTES-PRONTAS` (IMPORTS, PROVEN), `C-PORTA-FONTES-PRONTAS →
C-ORQUESTRADOR` (PROVEN), `C-IT-COLETA → C-CURATOR-LIFECYCLE` (o worker importa o leitor de robots da casa; PROVEN),
`C-IT-CONTRATOS → C-CURATOR-ESTADO-ACTUAL` (PROVEN). A seta de volta `C-PORTA-FONTES-PRONTAS → C-CURATOR-INTERFACE`
(SOURCE_REPAIR_NEEDED) é chamada, não import: declarada e **UNKNOWN** no mapa, que é a verdade do scanner.

Uma reprovação a caminho, corrigida: `P8_UM_DONO` — `tests/test_source_curator_integration.py` declarado em
`C-CURATOR-PROVAS` e reivindicado por `C-TESTES` (regra da casa para `tests/`). Saiu da peça do Curator.

```text
SYSTEM_MAP_CHECK = PASS @ 907ccd70 (218 peças 🟢32 🟡178 🔴0 ⚪8 · 1120 ligações · 0 código órfão)
IMPRESSAO_DO_CARIMBO = IGUAL @ 907ccd70 (2342 ficheiros-fonte)
```

---

## 10 · TESTES — por nome, contra baseline em `3c0ad4d7`

Bateria `py -m unittest discover -s tests -v`, em clones descartáveis (`git clone --local` + `checkout --detach`), uma de
cada vez, com `PYTHONPATH` do PyYAML emprestado e `SINTONIA_ARMAZEM_RAIZ` num tempdir. Comparação pela linha `FAIL:/ERROR:`
inteira (com a classe), deduplicada.

| | baseline @ `3c0ad4d7` | candidato @ `907ccd70` |
|---|---|---|
| TESTS_RUN | 4997 | 5026 |
| FAILED (failures + errors) | 210 = 196 + 14 | 201 = 187 + 14 |
| SKIPPED / expected failures | 190 / 1 | 190 / 1 |
| linhas vermelhas distintas | 210 | 201 |
| **NEW_FAILURES por nome** | — | **2 na suíte inteira @ `907ccd70` → **1** depois de alinhar um teste ao estado novo (ver abaixo): `test_canonico.TestContagens.test_fontes_placar_bate_com_o_declarado`** |
| sumidos por nome | — | 11 (todos de `test_metricas`/`test_canonico` sobre marcadores que o `--sync` fechou) |

**Os dois nomes novos da suíte inteira, e o que são:**

1. `test_integracao_04a_curator.ACuradoriaERegistoNaoFerramenta.test_nenhum_ficheiro_de_codigo_em_curadoria` —
   afirmava «`curadoria/` não tem código». Era a lei da 04A (registo sim, ferramenta não) e esta missão muda-a por
   ordem do dono: `curadoria/` passa a ter o **motor**. Conflito semântico resolvido segundo o estado atual: o teste
   passou a exigir a **lista fechada** dos 13 ficheiros do motor, a ausência das 20 ferramentas manuais da lane e
   nenhum `RobotFileParser` (`test_so_o_motor_e_codigo_em_curadoria` + `test_nenhuma_ferramenta_manual_da_lane_entrou`).
   Re-medido no FINAL_HEAD: módulo 18/18 OK.
2. `test_canonico.TestContagens.test_fontes_placar_bate_com_o_declarado` — **continua vermelho, e é dívida herdada
   exposta, não criada.** O dono da métrica (`--sync`, passo canónico depois de acrescentar testes) moveu o marcador
   `SOURCE_ID_COUNT` do cabeçalho do Atlas de 190 para **277**, que é o número real de `SOURCE_ID` no documento —
   `test_total_de_fontes_bate_com_os_source_ids_reais` **já reprovava na base** com `277 != 190`. O placar escrito à
   mão (linha `Total` = 190, por recorte e veredito) ficou onde estava, e o teste do placar passou a apanhar a
   diferença. Repor 190 no cabeçalho faria o teste passar mentindo.
   `BLOCKER` = placar do Atlas 87 fontes atrás · `OWNER` = dono do Atlas (`docs/fontes/ATLAS-DE-FONTES-EAME.md`) ·
   `MINIMUM_FIX` = recontar o placar por recorte (EUROPE/FRANCE/SPAIN/ITALY) e veredito (GREEN/YELLOW/RED/NÃO SEI)
   para os 277 e mover a data — decisão de veredito por fonte, fora desta missão.

Depois da suíte inteira, o teste 04A foi alinhado (+1 teste) e o dono da métrica re-sincronizado
(`TEST_COUNT_CURRENT 5.035 → 5.036`, `DRIFT = 0` em dois processos). Re-medidos por módulo no FINAL_HEAD:
`test_integracao_04a_curator` 18/18 · `test_source_curator_integration` 29/29 · `test_canonico.TestContagens` 4/6
(os dois vermelhos acima, ambos sobre o mesmo placar; um deles já era da base).

Provas próprias, todas verdes nesta árvore: `curadoria/test_lifecycle.py` 19/19 · `test_interface_collection.py` 7/7 ·
`provar_divisao.py` 7/7 · `provar_autonomia.py` 7/7 · `red_team_lifecycle.py` 0 blockers/11 ·
`tests/test_source_curator_integration.py` 29/29 (as doze famílias) · `tests.test_c10_5_collection_flow.OPortaoDeTransporteTemUmDonoSo` 2/2.
`pacote/metricas_canonicas.py`: `TEST_COUNT_CURRENT 5.035`, `DRIFT = 0` em dois processos novos (a base já trazia 19
marcadores em drift — `SOURCE_ID_COUNT 190→277`, `TEST_COUNT 4.759→…` — sincronizados aqui pelo dono da métrica).

---

## 11 · BLOCO DE ENTREGA

```text
INITIAL_HEAD = 3c0ad4d7   FINAL_HEAD = o commit «mapa: regerado…» que se segue a este relatório (SHA na mensagem de entrega)   REMOTE_HEAD = = FINAL_HEAD após push (conferido por rev-parse na entrega)   WORKTREE_CLEAN = medido na entrega
COMMITS = 333174d5 (motor + estado + provas + porta + mapa declarado + §164 + métricas) · 907ccd70 (mapa regerado) · commit deste relatório + teste 04A alinhado + métricas (5.036) · commit do mapa regerado
SOURCE_CURATOR_ENGINE_INTEGRATED = YES  (lifecycle · fila · worker · interface · evidência · resemeador · canário do motor; sem 2.º leitor de robots)
SOURCE_STATE_RECONCILIATION = RECALCULATED_FROM_CURRENT_STATE  (ESTADO-ACTUAL-DAS-FONTES-V1.json; fotografia não lida)
SOURCES_TOTAL = 195 no livro  (186 contratos + 9 candidatas do curator com canário medido; 49 fichas do Atlas sem contrato fora do ciclo)
READY_TOTAL_CURRENT = 160   READY_HTML = 105   READY_YOUTUBE = 50   READY_OTHER = 5
YOUTUBE_RECONCILED = 50   YOUTUBE_READY = 50   YOUTUBE_BLOCKED = 0
IT_T8_001_STATUS = CONTRACT_PENDING  (contrato à mão sem bloco executável; não incorporada; não somada)
RETRY_AFTER = 0  DEGRADED = 18  POLICY_BLOCK = 0  AUTH_BLOCK = 0  CAPABILITY_BLOCK = 1
(mais: CONTRACT_PENDING 4 · SEMANTIC_REVIEW 1 · CONTRACTED_CANARY_FAILED 9 (história) · CANARY_PENDING 2)
COLLECTION_CONSUMES_ONLY_READY = YES  (fontes_prontas.exigir_ready no orquestrador antes da corrida; FONTE_NAO_READY pelo nome; NÃO SEI passa)
COLLECTION_CAN_PROMOTE_READY = NO  (recusado pelo nome em 3 transições; teste T03, prova C, red team ataque 3)
REPAIR_LOOP_PROVED = YES  (READY → DEGRADED (Collection) → REPAIR na fila → REPAIRING → canário novo → READY com prova nova; provas D, E, F; testes T05, T06)
BACKOFF_NON_BLOCKING = YES  (prova G: 0,28 s de parede; B, C, D DONE antes do NEXT_ATTEMPT_AT de A; A volta aos 61 min)
NEW_FAILURES = 1 por nome (test_fontes_placar_bate_com_o_declarado — placar do Atlas desatualizado; BLOCKER/OWNER/MINIMUM_FIX em §10)   SYSTEM_MAP_CHECK = PASS @ 907ccd70 e re-medido no FINAL_HEAD (na entrega)   PAID_USD = 0   NETWORK_REQUESTS = 0
MODEL_EFFECTIVE = claude-fable-5-1
KNOW_HOW_DELTA = §164  (máximo anterior §163, varrido em 94 referências locais e remotas antes de escrever e reconferido antes do commit)
CANARIO_CANONICO_EXECUTADO_CONTRA_A_REDE = NO  (por regra da missão; canario_do_motor.mjs provado só nos ramos sem rede)
```

**HARD STOP.** Parei depois de integração + reconciliação + provas da nova divisão. Não corri Big Collection, não executei
nenhum `REPAIR`/`CANARY` da fila, não toquei B1–B12, Intelligence, Portal, LinkedIn/Instagram/Facebook.

---

## 12 · EM LINGUAGEM SIMPLES

1. **Quantas fontes o Sintonia tem agora?** No livro do ciclo de vida, **195**: 186 com contrato (a receita de como ir buscar)
   e 9 que o curador testou e falharam, ainda sem contrato. Há mais 49 fichas no Atlas sem receita nenhuma — são «conhecidas»,
   não «fontes prontas», e ficam fora do livro até alguém lhes escrever a receita.
2. **Quantas estão realmente prontas?** **160.** Antes dizia-se 181, mas «181» media «temos receita e ficha». «160» mede
   «provámos que chega lá»: das 181, a coleta de ontem viu 18 falharem (o site não mostra documentos com a forma esperada),
   1 falhou por defeito nosso (um `?` no nome de uma pasta no Windows) e 2 nunca tiveram prova nenhuma. Nenhuma sumiu: cada
   uma está escrita com o motivo e a corrida que a viu falhar.
3. **As 50 do YouTube continuam prontas?** **Sim, 50 em 50.** A fotografia antiga do curador ainda diz «bloqueadas» pela
   porta velha (o feed). O livro novo não leu essa fotografia; leu a porta nova (a página do canal), que foi conferida ao
   vivo 50 vezes e colheu em 41. As 9 que apanharam «devagar» (o 429) continuam prontas — o YouTube pediu tempo, não disse
   «não».
4. **Quem agora valida fontes?** O **Source Curator**, e só ele. O livro recusa, pelo nome, qualquer tentativa da Collection
   de marcar uma fonte como pronta — tentámos três vezes, de três estados diferentes, e as três foram recusadas.
5. **O que a Collection passa a fazer?** Pergunta «quais estão prontas agora?», recebe a lista, coleta. Se um pedido nomear
   uma fonte que o curador tem como avariada, a coleta **nem sai para a internet**: devolve «FONTE_NAO_READY» com o estado
   escrito. Se o curador não conhecer a fonte, a coleta segue como seguia — «não sei» não é «proibido».
6. **O que acontece quando uma fonte quebra?** A Collection diz «esta quebrou» (SOURCE_REPAIR_NEEDED), a fonte sai da lista
   de prontas **no mesmo instante**, entra um pedido de reparo na fila do curador, e a Collection passa à fonte seguinte sem
   tentar consertar nada. O curador repara, faz um canário **novo**, e só então a devolve à lista — com a prova nova, não a
   velha. Hoje há 18 reparos e 2 canários à espera nessa fila; nenhum foi executado nesta missão (exigiria internet).
7. **Um 429 ainda consegue parar a fila inteira?** **Não.** Provado com fila real: a fonte A apanhou 429 e foi marcada para
   voltar daí a 1 hora; B, C e D foram trabalhadas logo a seguir, na mesma volta, em 0,28 segundos de relógio; passados 59
   minutos A ainda não era elegível, aos 61 voltou sozinha e passou. Ninguém dormiu.
8. **O Bot de Fontes já pode trabalhar sozinho continuamente?** **Quase, e digo onde falta.** O motor está cá, com fila que
   sobrevive a um processo morto a meio (provado matando o processo de verdade), sem segundo leitor de robots, e com o canário
   pela porta do próprio motor de rota. O que **não** aconteceu: nenhum canário correu contra a internet nesta missão, porque a
   regra proibia. A próxima medição honesta é um `worker --max 1` sobre os 20 itens da fila, numa janela autorizada. Até lá:
   **CAN DO, ainda não DID DO.**

Dois avisos: (a) o número «160 prontas» é «a casa prova que chega», não «a fonte é relevante para a ADAMA» — isso continua a
decidir-se na admissão; (b) 19 números marcados em 12 documentos estavam desatualizados desde antes desta missão (contagem
de fontes e de testes) e foram sincronizados pelo dono da métrica — não por mim à mão.
