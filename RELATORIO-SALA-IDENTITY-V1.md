# RELATÓRIO — C-SALA-IDENTITY-V1: A SALA PRECISA DE SABER QUEM É CADA ENTREGA

```
BANCADA      sala-identity-v1   (C:/Users/London1/orca/workspaces/eame-sintonia/sala-identity-v1)
BRANCH       sala-identity-v1   (sem upstream; origin/sala-identity-v1 NÃO existe)
BASE         3c0ad4d7a05aa82bd4e4c87fc2a3b25451a6fb13  (tip de big-collection-release-v1, local == origin — medido)
DATA         2026-09-20 → 2026-09-21 (UTC)
MODEL        claude-fable-5-1
REGRAS       Collection NÃO correu · rede NÃO usada · PAID_USD 0 · nenhuma linha apagada nem reescrita
```

**A pergunta central tem resposta medida.** A Sala distingue uma entrega nova de um
derivado já existente **pela chave `(run_id, ordem)` e pela observação
`raw_observation_id`** — as 46 linhas têm 46 chaves e 46 observações distintas. O que
ela **não** distinguia era **pelo nome** (`item_id`): a rota documental do orquestrador
dava ao item o nome do DERIVADO (`derived:<n>`), e o derivado é conteúdo-por-receita —
duas observações dos mesmos bytes reencontram a mesma linha. Resultado: 6 pares de
entregas com o mesmo nome (5 na BCR, 1 anterior). Os 5 «suspeitos» são **reutilização
válida** do derivado com **proveniência intacta**; o defeito era o nome emprestado, e o
nome é por onde `retirar()` endereça e por onde um consumidor cunha `SIGNAL_ID`.

    O DERIVADO É O TEXTO. A ENTREGA É ESTA OBSERVAÇÃO, NESTA CORRIDA.
    COL-LAW-034: ITEM_ID != ARTIFACT_ID.

A correção é uma função no dono da rota (`orquestrador/orquestrador.py::
item_documental_para_a_porta`): o item passa a chamar-se `obs:<RAW_ASSET_ID>`; sem
observação não há nome, e a porta recusa por `identidade`. Nenhuma linha do banco foi
tocada. Bateria nova: 22 testes, 7 reprovam no código antigo.

---

## FASE 0 — REMEDIDO (nada do briefing foi aceite sem medir)

```
REPO            lucianodalondon-sys/eame-sintonia  (origin = https://github.com/lucianodalondon-sys/eame-sintonia.git · ORCA_WORKTREE_ID 21fd565e-b307-4e21-a48a-ae64d3b31330)
BRANCH          sala-identity-v1
HEAD            3c0ad4d7a05aa82bd4e4c87fc2a3b25451a6fb13   (== big-collection-release-v1 == origin/big-collection-release-v1)
REMOTE_HEAD     NONE  — origin/sala-identity-v1 não existe, sem upstream configurado
                (origin/main = f437ff1140fa97484ca9695b341fbe9ca0a9f050 · origin/HEAD → claude/sintonia-eame-repo-setup-xccfob @ c88690ca)
WORKTREE        C:/Users/London1/orca/workspaces/eame-sintonia/sala-identity-v1   (git worktree list: 87 entradas no arranque; o briefing dizia 86)
DIRTY           0 ficheiros modificados · 1 por rastrear (MISSAO-SALA-IDENTITY-V1.md, o próprio briefing)
DB_REACHABLE    YES  — psql 16.4 portátil (orca/pgtmp), DSN lida de %USERPROFILE%\sintonia-sala-italia\SALA_DSN.txt (nunca impressa), 127.0.0.1:54330/sala_italia, 31 migrations
SALA_TOTAL      46   (select count(*) from sala_de_espera)
ACTIVE_WRITERS  1 activo · 1 parado · 1 ambíguo — medido por DUAS amostras de HEAD+status separadas por 8 min:
                  crop-e2e-v1                    HEAD d51ea98a · sujo 6 → 14 · última escrita 29 s antes da 2.ª amostra   → ACTIVO
                  source-curator-integration-v1  HEAD 907ccd70 · sujo 1 → 1 (RELATORIO-SOURCE-CURATOR-INTEGRATION.md) · última escrita 18 min antes → AMBÍGUO/PARADO
                  big-collection-release-v1      HEAD 3c0ad4d7 · limpo · limpo                                              → PARADO
COLISÃO         NENHUMA com o meu escopo. crop-e2e-v1 toca data/derivados/*, provas/o_piloto_da_sala.py, leis/regua_italia.py,
                coleta/executor_secoes_por_cultura.py, tests/test_a_cultura_atravessa.py, docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md.
                Nenhum toca orquestrador/orquestrador.py, admissao/sala_de_espera.py nem supabase/migrations/*.
```

Outras contagens do banco no arranque: `collection_run 369 · raw_asset 1072 · storage_object 938 ·
derived_artifact 755 · documento_estruturado 754 · schema_migracao 31`.

⚠️ A primeira ligação ao banco **pendurou** (psql com a DSN antes das opções — a memória já
avisava; opções primeiro, DSN por último, e `timeout`). Nada foi escrito.

---

## FASE 1 — CENSO DOS 17

**Fronteira provada, não suposta.** As 29 entregas anteriores têm `pousado_em` ≤
`2026-09-20 14:46:28Z`; as 17 seguintes têm `pousado_em` entre `19:25:20Z` e `19:38:37Z`,
`run_id` com carimbo `2026-09-20-19xxxx`, `collection_run.status = concluida`, e as 17
`Decisao` correspondentes no Livro (`data/samples/LIVRO-DE-DECISOES.json`, `corrida` ∈ os 17
`RUN_ID`) são `SIM · pertence ao universo · v5`. Janela da BCR no relatório dela: 18:59Z →
21:50Z. Não há linha entre 14:46Z e 19:25Z. 29 + 17 = 46 = `SALA_TOTAL`.

`SALA_ROW_ID` é `(run_id, ordem)` — todas com `ordem = 0`. `OBSERVATION_ID = RAW_ASSET_ID =
raw_asset.id`. `ADMISSION_ID`: **não existe** — a rota IT não escreve etapa `ADMISSION` em
`etapa_da_corrida` (BCR §7, B7); a decisão vive no Livro, identificada por
`(corrida, item, universo, quando)`. `CONTENT_SHA` = `raw_asset.sha256` (12 primeiros).
`CREATED_AT` = `raw_asset.captured_at`; `ADMITTED_AT` = `Decisao.quando` (Livro) — a
`sala_de_espera.pousado_em` chega ≤ 1 s depois.

| # | RUN_ID (sufixo) | ITEM_ID | RAW/OBS | DERIVED | SOURCE_ID | CONTENT_SHA | CREATED_AT | ADMITTED_AT |
|---|---|---|---:|---:|---|---|---|---|
| 1 | `IT-T5-…192508-6a134eecf66c22a3` | `derived:56` ⚠ | 289 | 56 (reuso) | IT-T5-015 | 9397764bcf72 | 19:25:15.633Z | 19:25:20Z |
| 2 | `IT-T5-…192532-9aac8c847b3a9086` | `derived:126` | 291 | 126 | IT-T5-017 | 9701b23aab23 | 19:25:38.472Z | 19:25:44Z |
| 3 | `IT-T5-…192653-3059d44865de3771` | `derived:57` ⚠ | 298 | 57 (reuso) | IT-T5-024 | c1e398fde7a7 | 19:27:00.700Z | 19:27:06Z |
| 4 | `IT-T5-…192708-c824dabebd7f3b61` | `derived:128` | 299 | 128 | IT-T5-025 | f74805117746 | 19:27:14.007Z | 19:27:20Z |
| 5 | `IT-T5-…192734-8b9ef001a8833894` | `derived:129` | 301 | 129 | IT-T5-027 | 4d58bc4259b0 | 19:27:43.264Z | 19:27:50Z |
| 6 | `IT-T5-…192753-50b3827b5360b47a` | `derived:60` ⚠ | 302 | 60 (reuso) | IT-T5-028 | 50a45d9eeef8 | 19:27:59.185Z | 19:28:06Z |
| 7 | `IT-T5-…192820-3218c890fbdc53ea` | `derived:130` | 304 | 130 | IT-T5-030 | 96c5c7732d38 | 19:28:27.284Z | 19:28:34Z |
| 8 | `IT-T5-…192843-147a52f842d703b2` | `derived:62` ⚠ | 305 | 62 (reuso) | IT-T5-033 | e0c35dd4255e | 19:28:49.905Z | 19:28:54Z |
| 9 | `IT-T5-…192855-65f932fb8ca2d940` | `derived:131` | 306 | 131 | IT-T5-034 | cc2554fce837 | 19:29:00.145Z | 19:29:05Z |
| 10 | `IT-T5-…192906-7ab07ae1f5ec1c43` | `derived:132` | 307 | 132 | IT-T5-035 | c2feba511e66 | 19:29:11.535Z | 19:29:17Z |
| 11 | `IT-T5-…192919-8e956ede5a0f00ca` | `derived:133` | 308 | 133 | IT-T5-036 | f6dfa2abcb66 | 19:29:24.222Z | 19:29:31Z |
| 12 | `IT-T7-…192932-34df68b28dff931e` | `derived:134` | 309 | 134 | IT-T7-013 | 05342a7aa1d7 | 19:29:37.990Z | 19:29:44Z |
| 13 | `IT-T9-…193058-ff56ab6f5e532dc1` | `derived:66` ⚠ | 313 | 66 (reuso) | IT-T9-011 | b705c4fa2b83 | 19:31:04.970Z | 19:31:09Z |
| 14 | `IT-T5-…193605-e847862f7bea0834` | `derived:142` | 334 | 142 | IT-T5-039 | eeda88322e66 | 19:36:14.786Z | 19:36:29Z |
| 15 | `IT-T5-…193632-9cea5353f98faba7` | `derived:143` | 335 | 143 | IT-T5-049 | a974d5c67774 | 19:36:39.394Z | 19:36:46Z |
| 16 | `IT-T7-…193746-81a5352c4a43f429` | `derived:147` | 339 | 147 | IT-T7-033 | cf6ac17d07ad | 19:37:52.709Z | 19:37:57Z |
| 17 | `IT-T7-…193826-d16655f6c9c2f725` | `derived:149` | 341 | 149 | IT-T7-041 | 948516bf570d | 19:38:32.995Z | 19:38:36Z |

Todos: `universo` T5/T7/T9 (13·3·1) · `estagio DOCUMENTO` · `estado_da_fila WAITING` ·
`raw_asset.identity_state FORWARD_IDENTIFIED` com `document_key` real (`<SOURCE_ID>:URL:<caminho>`) ·
`preserved = true` · `derived_artifact.kind TEXT_EXTRACTION`, `producer texto-de-html` (1 `texto-de-pdf`,
#2). Os 17 derivados e as 22 observações (17 + os 5 irmãos antigos) **existem no armazém
operacional** (`%USERPROFILE%\sintonia-sala-italia\armazem`) com `sha256` igual ao do banco — 39/39
conferidos. `derived_artifact.storage_path` é `NAO_SEI/derivados/TEXT_EXTRACTION/…` — o país do
derivado é `NAO_SEI` de propósito (o pai não o prova); é endereço, não identidade.

⚠ = os 5 suspeitos (FASE 2).

---

## FASE 2 — OS 5 SUSPEITOS, UM A UM

Para cada um, medido no banco (`raw_asset`, `derived_artifact`, `participacao_na_derivacao`,
`documento_estruturado`, `etapa_da_corrida`, `sala_de_espera`):

| ITEM_ID | RUN que produziu a observação nova | OBS nova (sha igual à antiga) | OBS antiga → RUN antiga (13:11Z) | DERIVED utilizado (raw_asset_id do derivado) | participação escrita (first_seen_run) | etapa DERIVED | Sala aponta para | storage_object |
|---|---|---:|---|---|---|---|---:|---|
| `derived:56` | `…192508…` | 289 | 164 → `…131125…` | 56 (pai 164) | (289,56) ← run `…192508…` | PASS reused=1 | **289** | 82 reutilizado |
| `derived:57` | `…192653…` | 298 | 165 → `…131130…` | 57 (pai 165) | (298,57) ← run `…192653…` | PASS reused=1 | **298** | **298 novo** (irmão 91) |
| `derived:60` | `…192753…` | 302 | 168 → `…131143…` | 60 (pai 168) | (302,60) ← run `…192753…` | PASS reused=1 | **302** | 95 reutilizado |
| `derived:62` | `…192843…` | 305 | 170 → `…131200…` | 62 (pai 170) | (305,62) ← run `…192843…` | PASS reused=1 | **305** | **305 novo** (irmão 98) |
| `derived:66` | `…193058…` | 313 | 175 → `…131220…` | 66 (pai 175) | (313,66) ← run `…193058…` | PASS reused=1 | **313** | **313 novo** (irmão 106) |

- **Qual RUN produziu a observação:** a corrida da BCR (coluna 2), `concluida`, etapa `RAW:PASS passed=1`.
- **Qual OBSERVATION foi admitida:** a nova (289/298/302/305/313) — é ela que está em `sala_de_espera.raw_observation_id`.
- **Qual DERIVED foi utilizado:** o das 13:11Z (56/57/60/62/66), cujo `raw_asset_id` é a observação **antiga**.
- **Foi reutilizado de corrida anterior?** SIM — `derivacao_e_unica_por_regua` (022) torna isso obrigatório: mesmo `parent_sha256` + mesma receita = UMA linha.
- **A reutilização é permitida?** SIM — é o grão da 022 e a lei da 029; a aresta observação-nova → derivado ficou **escrita** em `participacao_na_derivacao` com a corrida da BCR.
- **A Sala preservou ou perdeu a identidade da nova entrega?** **Preservou** em `(run_id, ordem)` e em `raw_observation_id`; **emprestou** o nome (`item_id`) do derivado.

```
derived:56  VALID_REUSE      derived:57  VALID_REUSE      derived:60  VALID_REUSE
derived:62  VALID_REUSE      derived:66  VALID_REUSE
SUSPECTED_5_VALID = 5   SUSPECTED_5_BROKEN = 0   IDENTITY_COLLISION (no NOME, não na chave) = 5   UNKNOWN = 0
```

**E há um 6.º par, anterior à BCR:** `derived:6` — observações 7 (`XX-T3-…171909`, 18/09) e 26
(`IT-T3-…234958`, 19/09). O padrão nasceu com a rota (`d7d0008d`, 12/09), não com a corrida grande.

**Facto lateral, registado e não corrigido:** em 3 dos 5 pares a observação nova criou um
`storage_object` novo para os mesmos bytes (298, 305, 313), com `storage_path` diferente (o nome do
ficheiro é truncado noutro ponto); em 2 reutilizou (82, 95). `storage_path` é único; `sha256` não — a
tabela permite duas cópias dos mesmos bytes. É o **dono do armazém** quem decide; não é desta missão.

---

## FASE 3 — IDENTIDADES CANÓNICAS (lidas nas migrations 022 · 025 · 026 · 027 · 029 · 030 · 031 · 032 e no código)

```
WHAT_IDENTIFIES_STORAGE_OBJECT       storage_object.id  ·  endereço = storage_path (unique)  ·  conteúdo = sha256 (NÃO unique)
WHAT_IDENTIFIES_CONTENT              sha256 dos bytes. Derivado = conteúdo POR RECEITA:
                                     (parent_sha256, kind, producer, producer_version, parameters_hash, serie_posicao) — unique (022)
WHAT_IDENTIFIES_OBSERVATION          raw_asset.id (bigserial). Identidade forward: (run_id, source_id, document_key, sha256) unique
                                     quando identity_state = FORWARD_IDENTIFIED (026/027). Aponta para a cópia por (storage_object_id, sha256).
WHAT_IDENTIFIES_ADMISSION            a Decisao no Livro: (corrida, item, universo, regra, quando, versao). NÃO há linha ADMISSION
                                     em etapa_da_corrida na rota IT (ETAPA_ADMISSION_ROWS_IT = 0; BCR B7). No banco a admissão
                                     materializa-se como a linha da Sala.
WHAT_IDENTIFIES_WAITING_ROOM_DELIVERY sala_de_espera (run_id, ordem)  — chave primária (031)
                                     + raw_observation_id  — QUAL observação (FK raw_asset, pode ser de outra corrida, de propósito)
                                     + corrida_sha256      — a impressão do CONJUNTO: retry (REUSED) vs outra história (RUN_ID_CONFLICT)
                                     item_id: guardado e indexado; "NÃO é endereço" (031, em letra).
```

Preservado: `RUN ≠ OBSERVATION ≠ CONTENT ≠ STORAGE OBJECT`. `DERIVED_ARTIFACT` **não** vira identidade
de observação nem de entrega — e era exactamente isso que `item_id = derived:<n>` fazia. Nenhuma
segunda ontologia foi criada: a aresta observação→derivado já tem dono (`participacao_na_derivacao`).

---

## FASE 4 — ITEM_ID

```
ITEM_ID_CURRENT_SEMANTICS   (antes) rota documental do orquestrador: "derived:<derived_artifact.id>" = ARTIFACT_ID do NOSSO registo,
                            grão conteúdo-por-receita, partilhado por todas as observações dos mesmos bytes.
                            rota coleta/rota_forward_documento.py (T4/ES, 0 das 46 linhas): id = CONTENT_ID = sha256 do derivado.
                            Lei (COL-LAW-034 · 031): ITEM_ID é a identidade do ITEM — "o nome que a FONTE deu ao item".
ITEM_ID_ACTUAL_USAGE        (a) sala_de_espera.retirar(run_id, item_id): endereça pelo nome dentro da corrida; ItemAmbiguo se repetir.
                            (b) motor/corrida_da_inteligencia.py: SIGNAL_ID = sha(intelligence_run|ITEM_ID); REQUIREMENT_ID idem;
                                referencia_do_item() leva ITEM_ID + RAW_OBSERVATION_ID + CORRIDA.
                            (c) espera.listar_pendentes() devolve (RUN_ID, ORDEM, ITEM_ID).
                            (d) nenhum código lê o prefixo "derived:" (medido por grep em .py/.mjs/.sql).
ITEM_ID_IS_UNIQUE_FOR_DELIVERY  NO entre corridas (6 pares); dentro da corrida foi único nas 46 por acaso do universo
                            (uma observação por corrida) — dois documentos com os mesmos bytes em endereços
                            diferentes na mesma corrida dariam o mesmo nome.
```

**Correção (menor mudança, no dono):** `orquestrador/orquestrador.py::item_documental_para_a_porta` —
`id = "obs:<RAW_ASSET_ID>"` (a observação já viajava como `RAW_OBSERVATION_ID`; COL-LAW-043); sem
`RAW_ASSET_ID` **não há `id`**, a porta responde `NAO_SEI` por `identidade` (COL-LAW-034) e o Livro
guarda o porquê. Sem SHA, sem `storage_path`, sem `derived` como fallback. Guarda literal
`"raw_asset_id": estruturado.get("RAW_ASSET_ID")` mantida (é o que `tests/test_a_linhagem_do_ready.py`
exige). **Zona de fronteira declarada:** `orquestrador/orquestrador.py` é tocado por
`source-curator-integration-v1` no bloco `exigir_ready`; esta mudança fica dentro de uma função, sem
reformatar o ficheiro.

**Não corrigido, declarado:** `coleta/rota_forward_documento.py` (linha 571 → 300) põe o sha256 do
derivado como `id` do item — a mesma classe de defeito. Nenhuma das 46 linhas veio por lá; é a rota
piloto T4/ES, com provas contra Postgres que esta bancada não corre. Fica para o dono da rota.

---

## FASE 5 — IDEMPOTÊNCIA CORRECTA (os dois casos coexistem)

- **CASO A — retry da mesma admissão:** `pousar()` decide no banco, debaixo de `pg_advisory_xact_lock`,
  pela `corrida_sha256` (impressão do conjunto): mesma impressão → `REUSED`, nenhuma linha nova. O nome
  novo (`obs:<n>`) é determinístico por observação, logo o retry produz a mesma impressão. Provado em
  `T1_*` (backend de ficheiro, mesma função `impressao_da_corrida`; e leitura estática do SQL do backend
  canónico: `select corrida_sha256 into ja … elsif ja = {sha}`).
- **CASO B — nova RUN / nova observação sobre conteúdo já conhecido:** observação nova em `raw_asset`
  (mesmo sha), derivado reencontrado (022), aresta escrita (029), entrega nova com nome próprio e
  `raw_observation_id` novo; o texto **não** é duplicado. Provado em `T2_*` e `T3_*`.

---

## FASE 6 — RECONCILIAR OS 17

```
PROVENANCE_RECONCILED = YES — já estava certa nas 17 (e nas 29): raw_observation_id aponta para a
observação NOVA de cada corrida; participacao_na_derivacao liga essa observação ao derivado usado;
documento_estruturado do derivado reutilizado aponta para a corrida ANTIGA (correcto: foi lá que o
texto nasceu). Nenhuma linha alterada, nenhuma apagada.
```

Colisão histórica (os 6 pares de nome): **preservada como evidência**. Reescrever `item_id` mudaria o
conjunto que `corrida_sha256` assinou — fabricava um passado. O que muda é o que entra daqui em diante;
o teste `T7_T8_*` fixa as 46 chaves, as 46 observações e os 46 nomes históricos, e reprova se algum
sumir ou for reescrito.

---

## FASE 7 — OS 41 DERIVADOS: NÃO TOCADOS

Não restaurados, não recoletados, não procurados. O que se mediu, só a ler: os 17 derivados e as 22
observações por trás das 17 entregas **existem** no armazém operacional com sha igual (39/39). Depois
da correção, a identidade da entrega assenta em `(run_id, ordem)` + `raw_observation_id` + `obs:<n>`
— **nenhum destes depende de o ficheiro derivado existir**. (A memória de 21/09 nota que 4 derivados
T3 das 29 antigas não têm ficheiro no armazém; a identidade dessas linhas também não depende disso.)

---

## FASE 8 — CONSUMIDOR INCREMENTAL

```
SAFE_FOR_INCREMENTAL_CONSUMER = YES, com a chave certa — e a chave certa está no contrato:
   JÁ PROCESSADO vs NOVA ENTREGA REAL  ←  (CORRIDA, RAW_OBSERVATION_ID), ou (run_id, ordem) na Sala.
   ITEM_ID passa também a separá-las (obs:164 vs obs:289). derived_id sozinho NUNCA separa (mesmo texto,
   mesmo pai) — e é por isso que não é chave. Provado em T6_* com referencia_do_item() (função pura de
   motor/corrida_da_inteligencia.py; nenhuma corrida da Intelligence foi aberta).
Ressalva honesta: o consumidor que HOJE existe cunha SIGNAL_ID por (intelligence_run|ITEM_ID). Sobre as 46
linhas históricas (nomes derived:<n> repetidos), dois itens do mesmo par no MESMO pedido colidiriam. Não
é desta missão corrigir a Intelligence; fica declarado.
```

---

## FASE 9 — FUTURO `SALA_ITEM_ADMITTED` (não implementado)

```
FUTURE_EVENT_ENTITY_ID     (run_id, ordem)  — a chave da linha da Sala — levando raw_observation_id ao lado
                           (QUAL observação) e source_id. Nunca derived_id, nunca sha, nunca storage_path.
FUTURE_IDEMPOTENCY_KEY     (run_id, ordem, corrida_sha256) — a mesma admissão, mesmo conjunto → o mesmo evento;
                           outra história na mesma corrida não gera evento (a Sala já recusa com RUN_ID_CONFLICT).
SAFE_FOR_SALA_ITEM_ADMITTED_EVENT = YES para linhas novas (nome próprio + chave própria);
                           para as 46 históricas o nome é ambíguo e o evento teria de viajar pela chave, não pelo nome.
```

---

## FASE 10 — TESTES

`tests/test_a_identidade_da_entrega_na_sala.py` — 22 testes, 6 classes sem banco + 1 classe só-leitura
contra a Sala operacional (SKIP à vista sem DSN/psql):

| # exigido | classe | o que prova |
|---|---|---|
| 1 | `T1_RetryDaMesmaAdmissaoNaoDuplica` | retry → REUSED, 1 entrega; mesma impressão; o backend canónico decide pela mesma chave |
| 2 | `T2_NovaObservacaoPreservaIdentidadeNova` | 164 vs 289: nomes diferentes, observações diferentes, duas entregas, impressões diferentes, texto não duplicado |
| 3 | `T3_ReutilizarODerivedNaoRoubaAProveniencia` | a entrega nova aponta para 289, nunca para 164 (o pai do derivado) |
| 4 | `T4_ShaNuncaViraObservationIdNemItemId` | nada com 64 hex em id/ITEM_ID/RAW_OBSERVATION_ID; sem observação → sem id → porta recusa; a porta nunca deriva a observação do sha |
| 5 | `T5_DerivedIdNaoSubstituiAIdentidadeDaEntrega` | `obs:289`, não `derived:`; fonte do orquestrador sem `"derived:%s"`; outra receita sobre a mesma observação = mesma entrega |
| 6 | `T6_ConsumidorIncrementalDistingueVelhoDeNovo` | (CORRIDA, RAW_OBSERVATION_ID) separa; ITEM_ID separa; `referencia_do_item` distinta; derivado sozinho não separa |
| 7 | `T7_T8_NenhumaEntregaLegitimaDesaparece` | as 29 anteriores continuam (chave a chave) |
| 8 | idem | as 17 da BCR continuam; observação e nome histórico de cada uma das 46 não foram reescritos |

Mutação: a bateria copiada para a árvore **antiga** (3c0ad4d7) dá **7 FAIL** (T2, T4-sem-observação,
T5×3, T6×2) e 1 SKIP (classe DB sem `SINTONIA_PSQL_EXE` no ambiente) — os testes mordem o defeito.

Módulos vizinhos nesta árvore (`test_sala_duravel`, `test_a_sala_de_espera_tem_um_dono`,
`test_a_sala_de_espera_nao_tem_morada`, `test_a_ponte_do_derived`, `test_a_linhagem_do_ready`,
`test_a_linhagem_do_ready_e_do_raw_asset`, `test_psql_argv`, `test_fronteira_mede_a_sala_canonica`,
`test_o_censo_da_sala_de_espera`): 165 testes, 11 FAIL + 5 ERROR — **todos anteriores a esta missão**
(fixture de 12 campos contra contrato de 19; `admissao\sala_de_espera.py` com barra do Windows; Livro
vs banco da BCR; censo byte a byte). Confirmado por nome na baseline abaixo.

⚠️ `tests.test_o_censo_da_sala_de_espera` **reescreve** `data/derivados/O-CENSO-DA-SALA-DE-ESPERA.json`
só por correr (ficheiro de outra missão viva): restaurado com `git checkout` antes de commitar.

### Baseline vs. final, por NOME (`py -m unittest discover -s tests -v`, em worktrees descartáveis, uma de cada vez)

```
BASELINE_TREE        3c0ad4d7            FINAL_TREE   __FINAL_TREE__
TESTS_RUN            __B_RUN__           __F_RUN__
FAILURES+ERRORS      __B_FE__            __F_FE__
SKIPPED              __B_SKIP__          __F_SKIP__
NOMES VERMELHOS      __B_NAMES__         __F_NAMES__
NEW_FAILURES         __NEW__
SUMIDOS              __GONE__
ALL_GATES_GREEN      NO  — a suíte já chega vermelha nesta máquina (dívida histórica: PyYAML ausente, fcntl, caminhos Windows,
                     P5/control-plane). NEW_FAILURES = 0 NÃO é ALL_GATES_GREEN = YES, e não se mascara.
```

---

## SYSTEM MAP

`SYSTEM_MAP_CHECK = __MAP__`. A mudança altera a identidade que a Sala recebe (ligação real
orquestrador → admissão → Sala) e acrescenta um teste; a cadeia canónica correu inteira
(`correr_a_cadeia.py REGERAR` + `VALIDAR`), e `impressao_da_arvore.py --conferir-carimbo` depois do
commit. A peça do orquestrador já estava PENDING antes desta missão (121 dos 493 carimbos declarados
diferem da árvore); **não** se recarimbou nada — recarimbar drift alheio seria mentir a favor do verde.

---

## ENTREGA OBRIGATÓRIA

```text
INITIAL_HEAD = 3c0ad4d7a05aa82bd4e4c87fc2a3b25451a6fb13
FINAL_HEAD = __FINAL_HEAD__
REMOTE_HEAD = NONE (origin/sala-identity-v1 não existe; nada foi empurrado)
WORKTREE_CLEAN = __CLEAN__

SALA_BEFORE = 46
SALA_AFTER = 46

BCR_ROWS_AUDITED = 17
BCR_ROWS_VALID = 17
BCR_ROWS_IDENTITY_COLLISION = 5   (colisão de NOME, não de chave nem de proveniência)
BCR_ROWS_UNKNOWN = 0

SUSPECTED_5_VALID = 5
SUSPECTED_5_BROKEN = 0

CURRENT_ITEM_ID_SEMANTICS = (antes) ARTIFACT_ID do derivado, "derived:<n>", partilhado por observações dos mesmos bytes
                            (depois) "obs:<raw_asset.id>" — a observação admitida; sem observação, sem nome, e a porta recusa
CANONICAL_DELIVERY_IDENTITY = sala_de_espera (run_id, ordem) + raw_observation_id (QUAL observação) + corrida_sha256 (retry vs conflito)

PROVENANCE_RECONCILED = YES (já estava certa nas 46; nenhuma linha tocada)

SAFE_FOR_INCREMENTAL_CONSUMER = YES pela chave (CORRIDA, RAW_OBSERVATION_ID) e, daqui em diante, também pelo ITEM_ID;
                                NO se o consumidor chavear por derived_id ou pelo nome histórico das 46
SAFE_FOR_SALA_ITEM_ADMITTED_EVENT = YES para linhas novas, pela entidade (run_id, ordem); NÃO pelo nome das 46 históricas

DATA_DELETED = 0
NEW_COLLECTION_RUNS = 0
NETWORK_REQUESTS = 0
PAID_USD = 0

NEW_FAILURES = __NEW__
ALL_GATES_GREEN = NO
SYSTEM_MAP_CHECK = __MAP__
KNOW_HOW_DELTA = +§164 (SINTONIA-EAME-KNOW-HOW.md)
```

Ficheiros tocados: `orquestrador/orquestrador.py` (1 função) · `tests/test_a_identidade_da_entrega_na_sala.py` (novo) ·
`SINTONIA-EAME-KNOW-HOW.md` (§164) · `RELATORIO-SALA-IDENTITY-V1.md` (este) · `system-map/data/*` e
`italia-portale/client/system-map/*` (regerados). **Não tocados:** `curadoria/`, `orquestrador/fontes_prontas.py`,
`provas/o_piloto_da_sala.py`, `data/derivados/`, `admissao/`, `supabase/migrations/`, `main`, outras worktrees, o banco.

---

## EM PALAVRAS SIMPLES

**1. Por que os 5 apontavam para derivados antigos?** Pense num arquivo de textos digitados. A
máquina só digita um documento uma vez: se o mesmo papel chega outra vez, ela não digita de novo —
aponta para o texto que já digitou. Na corrida grande de 20/09, 5 páginas da internet vieram
exactamente iguais às que já tinham vindo às 13:11 do mesmo dia. A máquina guardou as 5 páginas novas
(são 5 fotografias novas, tiradas noutra hora), mas apontou para os 5 textos já digitados. Por isso os
5 «apontavam para derivados antigos».

**2. Isso era reutilização correcta ou identidade errada?** As duas coisas, em sítios diferentes.
Reaproveitar o texto digitado é **correcto** e está escrito na lei da casa. O que estava **errado** era a
etiqueta: cada entrega na Sala levava como nome «texto n.º 56», e o texto n.º 56 serve para duas
fotografias diferentes. Duas entregas, o mesmo nome. A Sala não se enganou de gaveta (cada entrega tem
a sua chave e a sua fotografia), mas quem chamasse pelo nome podia agarrar a entrega errada.

**3. Qual é a identidade correcta de algo que entra na Sala?** A resposta é: *esta fotografia,
tirada nesta corrida*. Não é o texto (o texto pode ser partilhado), não é o «código de barras» dos
bytes (duas fotografias iguais têm o mesmo), não é o sítio onde o ficheiro ficou guardado (é uma morada,
não um nome). A partir de agora a etiqueta de cada entrega diz o número da fotografia («obs:289»), e se
não houver fotografia não há etiqueta nenhuma — a porta não deixa entrar, e escreve porquê.

**4. Os 17 continuam a ser 17 entregas legítimas?** Sim. Os 17 têm corrida própria terminada,
fotografia própria guardada, texto conferido byte a byte no armazém, e decisão de admissão registada
no Livro. Nenhuma foi apagada, nenhuma foi reescrita. As 29 anteriores também continuam lá: 29 + 17 = 46,
antes e depois desta missão. As 6 etiquetas repetidas (5 da corrida grande e 1 de 18/09) ficam como
estão, de propósito: são a prova do defeito, e apagá-las seria inventar um passado.

**5. A Intelligence conseguirá distinguir item velho de entrega nova?** Sim, se olhar para a coisa
certa: a chave (corrida + fotografia). Isso já estava certo nas 46. Com a correção, também consegue pelo
nome nas entregas que entrarem daqui em diante. O que ela **não** pode fazer é decidir só pelo número do
texto digitado — dois itens diferentes podem ter o mesmo. E uma ressalva: o programa da Intelligence
que existe hoje monta o número do sinal a partir do nome; sobre as 46 antigas, dois itens com o mesmo
nome no mesmo pedido colidiriam. Não mexi na Intelligence; fica dito.

**6. Já é seguro criar futuramente o evento «SALA_ITEM_ADMITTED»?** Sim, desde que o evento viaje
com a chave da entrega (corrida + posição, com o número da fotografia ao lado) e não com o nome nem
com o número do texto. Para as entregas novas, nome e chave já contam a mesma história. Para as 46
antigas, só a chave é de confiança. Não criei o evento — só provei o que ele tem de levar.

**O que pode estar errado nisto.** Medi uma Sala com 46 linhas de um dia; a regra «uma observação
por corrida» que tornou os nomes únicos dentro de cada corrida foi sorte do universo, não garantia. A
outra rota de documentos (a piloto T4/ES) tem o mesmo problema com outra roupa e **não** foi corrigida
aqui. E a suíte de testes desta máquina já chegava vermelha antes de mim: o que garanto é «nenhuma falha
nova por nome», não «tudo verde».
