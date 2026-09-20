# MISSÃO — COLLECTION RELEASE: A PRÓXIMA BIG COLLECTION

**Bancada:** `big-collection-release-v1` · **Base:** `96dcd6bd` (curator-04a-integration)
**Objetivo:** integrar a rota YouTube, medir READY real, e CORRER a Big Collection.

> **FOCO ABSOLUTO: FAZER O SISTEMA COLETAR.**
> Não abrir arquitetura nova. Não procurar fontes novas. Não mexer em Portal,
> Intelligence, backup, reboot, Source Curator, Facebook, Instagram, LinkedIn.

---

## 0 · O QUE O COORDENADOR JÁ MEDIU — **confirmar, não confiar**

Estes valores foram medidos por mim antes de abrir esta bancada. **Reconfirme cada
um** antes de os usar; se algum divergir, o seu número manda e diga-o no relatório.

```text
COORDINATOR_MEASURED_AT      2026-09-20 ~15:25 local
BANCADA_BASE                 96dcd6bd  (= curator-04a-integration, LOCAL == REMOTE, clean)
IT_TRUNK_V1                  606974c3  — ancestral de 96dcd6bd E de 7857d7b7
YOUTUBE_BRANCH               claude/youtube-canonical-free-route-v1
YOUTUBE_HEAD                 7857d7b798c36a3e3de7057e177ad31adc1999cf  (local == origin)
MERGE_BASE(04a, youtube)     370ce450   — 3 commits de cada lado, lanes irmãs
```

### 0.1 · A missão 04A FECHOU — verificado por mim

O escritor da `curator-04a-integration` terminou às 15:18 (prompt pronto, HARD STOP
declarado, push provado). **A bancada está livre.** Os números finais dele:

```text
INITIAL_HEAD = 370ce450    FINAL_HEAD = 96dcd6bd    LOCAL == REMOTE = YES
HTML_CONTRACTS_INTEGRATED    = 18   (regras/italy_contracts_onboarded.json: 105 → 123)
ATLAS_FICHAS_INTEGRADAS      = 84
YOUTUBE_READY_INTEGRATED     = 0    (bloqueadas, razão preservada)
DUPLICATE_SOURCE_IDS_CREATED = 0
NEW_FAILURES                 = 0 por nome (124 vermelhos distintos antes e depois)
SYSTEM_MAP_CHECK             = PASS
```

**Não reabra o estudo das 18 fontes.** Elas estão integradas. Confirme o número e siga.

### 0.2 · ⚠️ A CONTRADIÇÃO QUE VOCÊ VAI ENCONTRAR — já resolvida, não a re-investigue

O relatório 04A diz `YOUTUBE_BLOCKED = 50 · BLOCK_REASON = ROBOTS_DISALLOWED_ROUTE`.
O briefing do dono diz `ROBOTS_GATE = PASS`. **As duas afirmações estão certas**, porque
falam de rotas DIFERENTES. Medi o commit `48999d13` da lane YouTube:

```text
ROTA ANTIGA   youtube.com/feeds/videos.xml     → Disallow no robots.txt → 50 despromovidas
ROTA NOVA     /channel/<CHANNEL_ID>/videos     → o MESMO portão APROVA
```

> **UMA ROTA QUE RESPONDE NÃO É UMA ROTA PERMITIDA.**

O bloqueio das 50 é da rota velha. A missão da lane YouTube foi exatamente construir a
rota nova que passa. **É isso que você vai integrar.** Confirme lendo `48999d13`, e
confirme que a rota nova continua a passar no portão vivo — não herde o meu veredito.

### 0.3 · O que a lane YouTube entrega (medido na mensagem do commit `48999d13`)

```text
PROVIDER          CANAL_PUBLICO_YOUTUBE_V1, pelo registry canónico de adapters
TIPO              CUSTOM_ADAPTER — e a razão é medida: a página traz videoIds=30 e
                  href=/watch?v= ZERO. Os endereços vivem no ytInitialData (JSON
                  embutido). Um LINK_PATTERN sobre href encontra zero.
NÃO É yt-dlp      a lei do registry proíbe processo filho; o curl que o motor já
                  injecta em `buscar` chega aos mesmos alvos.
IDENTIDADE        lê-se do CANAL, nunca do item (em yt-dlp --flat-playlist o
                  channel_id do ITEM vem NA — uma fechadura que nunca tranca).
                  Divergência → IDENTITY_MISMATCH e zero alvos.
ZERO switch por SOURCE_ID — o adapter recebe CHANNEL_ID do contrato.
11 testes, mutante da guarda de identidade morto.
```

---

## 1 · INTEGRAR A ROTA YOUTUBE — semanticamente, sem merge cego

Traga `7857d7b7` para esta bancada. **Não recrie a solução.** **Não use
`feeds/videos.xml`.** **Não use yt-dlp.**

Os conflitos que eu previ com `merge-tree` (read-only) — reconfirme:

```text
GERADOS (5) — NÃO resolva à mão, REGENERE pela cadeia canónica:
  system-map/data/architecture.generated.json
  system-map/data/casco.generated.json
  system-map/data/sources.generated.json
  system-map/data/state.generated.json
  italia-portale/client/system-map/state.generated.json

SEMÂNTICO (1) — este exige leitura, é o único que decide conteúdo:
  docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md
```

Regra do AGENTS.md desta árvore: `git add` dos ficheiros novos **antes** de correr a
cadeia do mapa, senão `P1_SEM_DRIFT` reprova com `files_tracked` uma unidade abaixo.

---

## 2 · ONBOARDING DAS 50 FONTES YOUTUBE

⚠️ **Os dois canários já provados (IT-T8-001, IT-T7-015) TAMBÉM não estavam na tabela
onboarded.** Trabalhe sobre as **50**, não sobre «48 + 2 automaticamente».

Use o **MESMO mecanismo** para todas. **ZERO código por SOURCE_ID** — se você se vir a
escrever um `if`/`case` com um SOURCE_ID dentro, parou de integrar e começou a remendar.

Por fonte, medir e registar:

```text
SOURCE_ID · CHANNEL_ID · CONTRACT · ROUTE_RESOLVED · ROBOTS_GATE
IDENTITY_MATCH · TARGETS_DISCOVERED
```

```text
PASS  = ROUTE_RESOLVED=YES ∧ ROBOTS_GATE=PASS ∧ IDENTITY_MATCH=YES ∧ TARGETS_DISCOVERED>0
        → READY_FOR_COLLECTION
FAIL  = registar BLOCK_REASON e SEGUIR. Não investigue fonte individual a fundo.
```

Entregar: `YOUTUBE_TOTAL=50 · TESTED · PASS · FAIL · READY`.

---

## 3 · MEDIR READY REAL — no estado integrado, nunca somando de memória

```text
READY_EXISTING =     READY_NEW_HTML =     READY_YOUTUBE =     READY_TOTAL =
LINKEDIN_BLOCKED =   INSTAGRAM_BLOCKED =  FACEBOOK_BLOCKED =
```

As três famílias bloqueadas: **medir e NÃO resolver**.

---

## 4 · PREFLIGHT — eu já medi, confirme rápido e siga

Não repita a investigação da Sala. Ela está provada (`SALA_RECORDS=29`, read PASS,
write PASS, backup PASS, restore PASS). Confirme apenas:

```text
SALA_RUNNING = YES                    (pg_isready 127.0.0.1:54330 — medi: aceita conexões)
SINTONIA_SALA_DSN     %USERPROFILE%\sintonia-sala-italia\SALA_DSN.txt  (existe)
SINTONIA_PSQL_EXE     C:/Users/London1/orca/pgtmp/pgsql/bin/psql.exe   (existe)
STORAGE operacional   %USERPROFILE%\sintonia-sala-italia\armazem (78 MB, marcador presente)
PAID_ROUTE_ENABLED = NO
```

⚠️ **`SINTONIA_PSQL_EXE` não é opcional.** Medi: com a DSN correta mas sem esta variável,
`exigir_canonica()` falha com «nenhum psql». Declare-a no ambiente da corrida.

---

## 5 · A BIG COLLECTION

UMA corrida real, com TODAS as fontes READY medidas.

```text
SOURCE → COLLECTION → RAW → DERIVED → ADMISSION → SALA
```

**Uma corrida por fonte, em processo próprio**, com a saída de cada uma para ficheiro
próprio. Um lote monolítico faz a primeira falha cancelar as restantes e apaga a duração
individual — que é sinal.

Preservar: `SOURCE_ID · RUN · OBSERVATION · SHA256 · STORAGE · CONTRACT_HASH ·
CONFIG_HASH · PROVENANCE`.

**NÃO fabricar `FACT_TIME` nem `FACT_LOCATION`. UNKNOWN continua UNKNOWN.**
Copiar `source_location` para `fact_location` sem `basis` é inferir geografia da fonte.

### Falha de uma fonte NÃO para a rodada

`SUCCESS · SOURCE_FAILURE · ROUTE_FAILURE · IDENTITY_FAILURE · NETWORK_FAILURE ·
CREDENTIAL_BLOCK · POLICY_BLOCK · UNKNOWN` — registar e continuar.

⚠️ Antes de carimbar `SOURCE_FAILURE`, confirme que o executor TEM ramo para aquela
fonte. Sem ramo, a classe é `CAPABILITY_GAP` e o dono é a casa, não a fonte.

---

## 6 · ADMISSION + SALA — medir no banco, não pelo log

```text
RAW_OBSERVATIONS =
DERIVED_CREATED =   DERIVED_REUSED =   DERIVED_FAILED =
ADMISSION_SIM =  ADMISSION_NAO_SEI =  ADMISSION_NAO =  ADMISSION_NAO_SE_APLICA =  ADMISSION_ERRO =
SALA_BEFORE = 29    SALA_AFTER =    SALA_DELTA =
```

**`NAO` e `NAO_SEI` não se somam num balde de «falhas»:**

```text
NAO       houve texto e a porta julgou que não serve  → juízo, a porta a funcionar
NAO_SEI   não houve derivado para julgar              → confissão, falta extractor
```

> **NÃO alterar a régua para produzir mais `SIM`.**
> **BAIXAR NÃO É COLHER; COLHER NÃO É ADMITIR.**

Introspecione os nomes de coluna antes de escrever SQL (`information_schema.columns`) —
adivinhar encadeia erros e um `ERRO` no meio do relatório lê-se como zero.

### Red team pós-corrida (SQL) — qualquer resultado ≠ 0 é blocker

RAW órfão de corrida · identidade fabricada na sala (`source_id !~ '^(IT|EU|ES|FR)-T[0-9]+-[0-9]+$'`)
· `estagio` fora de (DOCUMENTO,ITEM,FATO) · `raw_observation_id` nulo · `cost_usd > 0`
· duplicação por retry · **procedência inferida em silêncio** (`fact_location = source_location`
com `fact_location_basis` vazio; idem `fact_time = published_at`) · `status='concluida'` com `error` não vazio.

Fechar com lineage de uma amostra real: sala → `raw_asset` → `storage_object` →
`derived_artifact`, confirmando `raw_observation_id = raw_asset.id`.

---

## 7 · CUSTO

`PAID_USD = 0` esperado. **Qualquer necessidade de gasto: HARD STOP antes.** Não compre.

---

## 8 · GATES FINAIS — só os essenciais

```text
NEW_FAILURES =                        (por NOME, contra baseline @ 96dcd6bd)
RECONCILIATION_STRUCTURAL_ERRORS =
SHA_MISMATCH =
TEST_CAN_DELETE_OPERATIONAL_STORAGE = NO
SYSTEM_MAP_CHECK =                    (se a integração alterou arquitetura declarada)
```

Não abrir outra auditoria depois. RAW novo fica **fora do commit** enquanto não houver
política de retenção: preserve no disco e diga-o.

---

## 9 · BLOCO DE ENTREGA

```text
INITIAL_HEAD =   FINAL_HEAD =   REMOTE_HEAD =   WORKTREE_CLEAN =
HTML_INTEGRATED =
YOUTUBE_TESTED =   YOUTUBE_PASS =   YOUTUBE_FAIL =   YOUTUBE_READY =
READY_EXISTING =   READY_NEW =   READY_TOTAL =
BIG_COLLECTION_RUN_ID =
SOURCES_SELECTED =  SOURCES_ATTEMPTED =  SOURCES_SUCCESS =  SOURCES_FAILED =
RAW_OBSERVATIONS =
DERIVED_CREATED =   DERIVED_FAILED =
ADMISSION_SIM =  ADMISSION_NAO_SEI =  ADMISSION_NAO =  ADMISSION_NAO_SE_APLICA =  ADMISSION_ERRO =
SALA_BEFORE = 29   SALA_AFTER =   SALA_DELTA =
PAID_USD =
NEW_FAILURES =   SYSTEM_MAP_CHECK =
MODEL_EFFECTIVE =
KNOW_HOW_DELTA =
```

Escreva o relatório em `RELATORIO-BIG-COLLECTION-RELEASE.md` na raiz da bancada.

⚠️ **Número de secção do know-how mede-se em TODAS as lanes abertas**, não só nesta —
a 04A usou **§162**. Varra as branches candidatas antes de escolher o seu número.

Feche com uma secção **EM LINGUAGEM SIMPLES**, sem jargão: o dono não é técnico e decide
por ela. Responder lá, e só isto:

1. quantas fontes estavam prontas;
2. quantas realmente coletaram;
3. quantos documentos entraram;
4. quantos foram admitidos;
5. de 29 para quanto a Sala cresceu;
6. quais famílias continuam bloqueadas;
7. se a Collection já está suficientemente operacional para avançarmos mais forte
   em CLAIM/FACT + Intelligence.

---

## 10 · REGRAS QUE NÃO SE NEGOCEIAM

- **Você é o ÚNICO escritor desta bancada.** Auxiliares só leem/auditam.
- **`CAN DO ≠ DID DO`.** Descobrir que um comando existe não é executá-lo.
- **`PRESENTE ≠ PROVADO`.** Se a prova não correu neste HEAD, o estado é `UNKNOWN`.
- **Não corrigir defeito encontrado fora do escopo:** entregue `BLOCKER`, `OWNER`,
  `MINIMUM_FIX` e siga. Corrigir para obter verde é mexer na régua.
- **Não alterar a régua de admissão** para aumentar aprovados.
- Teste verde só conta se a parte alvo executou. `SKIP` não é `PASS`.
- Número parcial vira `NOT_MEASURABLE`, nunca um valor inventado.

## HARD STOP

**PARAR após Big Collection + Admission + Sala.**

NÃO: procurar fontes novas · mexer em backup · configurar reboot · melhorar Source
Curator · resolver Facebook/Instagram/LinkedIn · construir Portal · iniciar arquitetura nova.

**FOCO: COLETAR.**
