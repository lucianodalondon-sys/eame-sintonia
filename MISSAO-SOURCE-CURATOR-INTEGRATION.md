# MISSÃO — INTEGRAR O MOTOR DO SOURCE CURATOR NA LINHA PÓS-BIG-COLLECTION

**Bancada:** `source-curator-integration-v1` · **Base:** `3c0ad4d7` (big-collection-release-v1)

> **INTEGRAR O MOTOR, NUNCA A FOTOGRAFIA.**
> Depois desta missão: **SOURCE CURATOR prepara · COLLECTION coleta.**

---

## 0 · O QUE O COORDENADOR MEDIU — **confirmar, não confiar**

Medido por mim às 22:45, antes de abrir esta bancada. Reconfirme; se divergir, o seu
número manda e diga-o.

```text
COLLECTION   big-collection-release-v1  HEAD 3c0ad4d7  LOCAL==REMOTE  DIRTY 0   ✅
SOURCE_CURATOR  claude/source-curator-lifecycle-v1  HEAD d21e8e43  local==origin ✅
                (= o HEAD citado no briefing do dono; não envelheceu)
MERGE_BASE(collection, curator) = 606974c3   → curator 9 commits · collection 37
ACTIVE_WRITERS = 0  (o executor da Big Collection parou: prompt pronto, HARD STOP)
```

### 0.1 · ⚠️ O PERIGO CENTRAL, LOCALIZADO NO COMMIT

Medi e **confirmei** o aviso do dono: a lane do curator **não contém** a rota YouTube nova.

```bash
git merge-base --is-ancestor 7857d7b7 d21e8e43   # → FALSO
```

E o commit que faz o estrago tem nome:

```text
376c0d9b  "gate de rota: 50 fontes YouTube saem de READY — o feed esta em Disallow"
```

Ele está **certo sobre a rota velha** (`/feeds/videos.xml` está em `Disallow`) e
**obsoleto sobre o mundo**: a Big Collection provou depois a rota
`/channel/<CHANNEL_ID>/videos` — **50/50 PASS**, `GATE_WATCH = True`.

```text
FOTOGRAFIA ANTIGA CERTA NO SEU DIA  !=  VERDADE DE HOJE
```

Se `curadoria/READY-FOR-COLLECTION-V1.json` (2198 linhas) entrar como estado vigente,
**as 50 voltam a `ROUTE_BLOCKED` e a missão destrói o que a Big Collection provou.**
Este é o modo de falha nº 1 desta missão.

### 0.2 · MOTOR vs FOTOGRAFIA — a fronteira, medida ficheiro a ficheiro

**MOTOR (integrar) — os `.py` de `ef06d75e`:**
```text
curadoria/lifecycle.py               livro append-only; READY exige canário E evidência
curadoria/fila.py                    fila no disco; 429 adia UMA tarefa (ESPERAR != BLOQUEAR)
curadoria/worker.py                  uma etapa por volta; robots inacessível = RETRY, não bloqueio
curadoria/interface_collection.py    READY_SOURCES derivado do livro; SOURCE_REPAIR_NEEDED
curadoria/semear_lifecycle.py        ← O RESEMEADOR. É a chave da Fase 3.
curadoria/test_lifecycle.py · test_interface_collection.py
curadoria/provar_lifecycle.py · provar_autonomia.py · red_team_lifecycle.py
```

**FOTOGRAFIA (NÃO importar como estado vigente) — os `.json` de `curadoria/`:**
```text
READY-FOR-COLLECTION-V1.json (2198) · LIFECYCLE-LEDGER-V1.json (1597)
LIFECYCLE-QUEUE-V1.json · SOURCE-CURATOR-DECISIONS-V1.json (4195) · ...
```
Traga-os se forem entrada do resemeador ou prova histórica — **mas o estado vigente
recalcula-se** na Fase 3. Diga explicitamente o que trouxe como dado e o que trouxe
como história.

---

## 1 · PRESERVAR O QUE A BIG COLLECTION PROVOU — **antes do merge**

Materialize o estado real atual **primeiro**, para ter contra o que reconciliar:

```text
CURRENT_SOURCE_IDS · CURRENT_CONTRACTS · CURRENT_ROUTES
CURRENT_READY · CURRENT_LAST_RESULTS
```

Âncoras que eu medi e que **nenhuma classificação antiga pode sobrescrever**:

```text
READY_TOTAL = 181  (113 existing + 18 HTML + 50 YouTube)  de 186 contratos
YOUTUBE: TESTED 50 · PASS 50 · FAIL 0 · READY 50
ROTA VIGENTE   /channel/<CHANNEL_ID>/videos   GATE_WATCH = True
ROTA BLOQUEADA /feeds/videos.xml              GATE_FEED_XML = False (continua bloqueada)
BCR-2026-09-20: ATTEMPTED 181 · SUCCESS 151 · FAILED 30
                (ROUTE_FAILURE 20 · POLICY_BLOCK 9 · CAPABILITY_GAP 1)
SALA 29 → 46 (+17)   PAID_USD = 0
```

---

## 2 · INTEGRAR O MOTOR — semanticamente, sem merge cego

Traga de `claude/source-curator-lifecycle-v1` (`d21e8e43`): lifecycle · fila durável ·
worker contínuo · backoff não bloqueante · READY interface · REPAIR interface ·
restart/recovery · testes · declarações arquiteturais.

- **Ficheiros gerados:** regenerar pela cadeia canónica, **nunca** resolver à mão.
- **Conflitos semânticos:** resolver segundo o **estado atual**, não a fotografia.
- `git add` dos ficheiros novos **antes** de correr a cadeia do mapa, senão
  `P1_SEM_DRIFT` reprova com `files_tracked` uma unidade abaixo (lei do `AGENTS.md`).

---

## 3 · RECONCILIAR ESTADOS — recalcular, não copiar

Reconstrua/resemeie o lifecycle a partir do **estado REAL atual**. Para cada `SOURCE_ID`:
identidade atual · contrato atual · rota atual · capacidade atual · canário/prova **mais
recente** · resultado da Big Collection quando aplicável.

Vocabulário canónico existente (não invente termos):
`READY_FOR_COLLECTION · DEGRADED · RETRY_AFTER · POLICY_BLOCK · AUTH_BLOCK ·
CAPABILITY_BLOCK · SEMANTIC_REVIEW`.

> **UNKNOWN continua UNKNOWN.** Nunca vira PASS nem BLOCK por omissão.

⚠️ **Enumere o vocabulário fechado do dono antes de escrever qualquer valor**
(`[x for x in dir(mod) if x.isupper()]` e a tupla que o validador consulta). Preencher
por analogia com o vizinho rebenta em runtime ou — pior — passa num ramo sem teste.

---

## 4 · YOUTUBE — gate obrigatório

```text
YOUTUBE_EXPECTED = 50
YOUTUBE_RECONCILED =    YOUTUBE_READY =    YOUTUBE_DEGRADED =    YOUTUBE_BLOCKED =
```

**Não aceitar que as 50 reapareçam como `ROUTE_BLOCKED` por causa do snapshot antigo.**
Se reaparecerem, é defeito da reconciliação — reporte e não maquilhe.

**IT-T8-001:** registada como possível 51ª fonte (B5 do relatório anterior: contrato à
mão, sem bloco executável). **NÃO incorporar silenciosamente.** Medir e reportar em
linha própria.

---

## 5 · READY INTERFACE REAL

A Collection tem de conseguir perguntar **«quais fontes estão READY agora?»**

```text
READY_TOTAL_CURRENT =     READY_HTML =     READY_YOUTUBE =     READY_OTHER =
```

**Não assuma que continua 181. Meça.** Se mudou, explique por evidência qual fonte
mudou de estado e porquê.

---

## 6 · PROVAR A NOVA DIVISÃO — seis provas isoladas

```text
A. SOURCE CURATOR pode promover fonte após gates.
B. COLLECTION consome lista READY sem onboarding pesado.
C. COLLECTION **NÃO** consegue promover SOURCE para READY.   ← fail-closed
D. fonte READY degradada gera SOURCE_REPAIR_NEEDED (ou canónico equivalente).
E. COLLECTION segue para a próxima fonte SEM iniciar reparo.
F. SOURCE CURATOR recebe o reparo, faz NOVO canário, e só então devolve READY.
```

⚠️ **Toda sonda precisa de um caso que a faça falhar.** Uma prova de que «a Collection
não promove» só vale com contraprova: tente promover e mostre a recusa **pelo nome**.
Fake acima do portão mede o fake — substitua a primitiva mais funda, nunca a camada de cima.

---

## 7 · BACKOFF — reprovar o comportamento

```text
SOURCE A → 429 → RETRY_AFTER
enquanto B, C, D continuam a ser trabalhadas.
```

**Nada de `sleep` bloqueando a fila.** `ESPERAR != BLOQUEAR`. Prove com fila real e
observe que as outras avançam **durante** a espera de A — execução serial não prova
concorrência.

---

## 8 · NÃO RESOLVER OS BLOCKERS DA BIG COLLECTION

**NÃO** abrir: B1–B12, em especial **B3** (34 derived failures / STORAGE_MISSING),
os **518 NAO_SEI**, CROP, LinkedIn, Instagram, Facebook, Portal, Intelligence automation.

**Apenas registar que continuam existentes.** Serão priorizados depois.

---

## 9 · SYSTEM MAP

Esta missão muda responsabilidade real:
```text
SOURCE CURATOR → READY_FOR_COLLECTION → COLLECTION
COLLECTION     → SOURCE_REPAIR_NEEDED → SOURCE CURATOR
```
Regenerar pela cadeia canónica. Exigir `SYSTEM_MAP_CHECK = PASS` **ou** reportar dívida
herdada com precisão — **nunca fabricar PASS**.

⚠️ Meça o vermelho do mapa na árvore virgem **antes** da primeira edição: sem esse
baseline, falha pré-existente é atribuída à sua mudança.

---

## 10 · TESTES — os doze

```text
 1. estados antigos não vencem evidência atual
 2. as 50 YouTube não são despromovidas pela rota antiga
 3. Source Curator é o ÚNICO promotor de READY
 4. Collection só consome READY
 5. falha da Collection não abre reparo interno
 6. repair volta ao Curator
 7. retry não bloqueia a fila
 8. restart preserva trabalho
 9. SOURCE_ID permanece estável
10. provenance permanece
11. sem duplicação por reinício
12. UNKNOWN não vira PASS/BLOCK por omissão
```

`NEW_FAILURES` **por NOME**, contra baseline medido em `3c0ad4d7`. `SKIP` não é `PASS`.

---

## 11 · BLOCO DE ENTREGA

```text
INITIAL_HEAD =   FINAL_HEAD =   REMOTE_HEAD =   WORKTREE_CLEAN =
SOURCE_CURATOR_ENGINE_INTEGRATED =
SOURCE_STATE_RECONCILIATION =
SOURCES_TOTAL =   READY_TOTAL_CURRENT =
READY_HTML =   READY_YOUTUBE =   READY_OTHER =
YOUTUBE_RECONCILED =   YOUTUBE_READY =   YOUTUBE_BLOCKED =
IT_T8_001_STATUS =                        (em linha própria, nunca somada)
RETRY_AFTER =  DEGRADED =  POLICY_BLOCK =  AUTH_BLOCK =  CAPABILITY_BLOCK =
COLLECTION_CONSUMES_ONLY_READY =
COLLECTION_CAN_PROMOTE_READY = NO
REPAIR_LOOP_PROVED =
NEW_FAILURES =   SYSTEM_MAP_CHECK =   PAID_USD = 0
MODEL_EFFECTIVE =   KNOW_HOW_DELTA =
```

Relatório em `RELATORIO-SOURCE-CURATOR-INTEGRATION.md` na raiz da bancada.

⚠️ **Número de secção do know-how mede-se em TODAS as lanes abertas.** A Big Collection
usou **§163**; a lane do curator tem um delta com «numero atribuido na integracao» —
**é você que o atribui**. Varra todas as branches com o ficheiro antes de escolher.

Feche com **EM LINGUAGEM SIMPLES**, sem jargão — o dono decide por ela. Responder:

1. quantas fontes o Sintonia tem agora;
2. quantas estão realmente prontas;
3. se as 50 do YouTube continuam prontas;
4. quem agora valida fontes;
5. o que a Collection passa a fazer;
6. o que acontece quando uma fonte quebra;
7. se um 429 ainda consegue parar a fila inteira;
8. se o Bot de Fontes já pode trabalhar sozinho continuamente.

---

## 12 · REGRAS QUE NÃO SE NEGOCEIAM

- **Você é o ÚNICO escritor desta bancada.**
- `CAN DO ≠ DID DO` · `PRESENTE ≠ PROVADO` · `DECLARADO ≠ OBSERVADO`
- **Não corrigir defeito fora do escopo:** entregue `BLOCKER`, `OWNER`, `MINIMUM_FIX`.
- Teste verde só conta se a parte alvo executou.
- Número parcial vira `NOT_MEASURABLE`, nunca valor inventado.
- **Não rodar nova Big Collection.** Nada de rede para coletar.

## HARD STOP

**PARAR** após integração + reconciliação + provas da nova divisão.

NÃO: nova Big Collection · resolver B1–B12 · Intelligence · Portal ·
LinkedIn/Instagram/Facebook.

**FOCO: SOURCE CURATOR PREPARA. COLLECTION COLETA.**
