# RELATÓRIO — RECONCILIAÇÃO CANÓNICA DOS LIVROS DE FONTES (RECONCILIACAO-V1)

Worktree `reconciliacao-v1`, partida de `bridge-feeder-v1` @ `4b5cbf7d`.
Missão: `C:/Users/London1/auditoria-madrugada/MISSAO-RECONCILIACAO.md`.
Data: 2026-09-21. Zero rede para reconciliar: nenhum pedido HTTP foi feito.

```
BASE_HEAD              4b5cbf7d   (234 testes OK, worktree limpa, md5 dos livros medido antes de tudo)
COMMITS_DESTA_MISSAO   da5a72d7 · d942240e · dd602746 · f3393871 · 719af617 · (relatório) · (mapa)
FINAL_HEAD             ver §11 (preenchido depois do mapa e do push)
REMOTE_HEAD            ver §11
```

---

## 0. A medição que a missão pediu para confirmar — confirmada

| livro | onde | fontes | transições | estado final por fonte |
|---|---|---|---|---|
| **A** | `curadoria/LIFECYCLE-LEDGER-V1.json` @ `4b5cbf7d` (esta árvore) | **85** | 263 | RECONCILIATION_REQUIRED 50 · READY 20 · CAPABILITY_BLOCK 10 · CANARY_FAILED 4 · RETRY_AFTER 1 |
| **B** | o mesmo ficheiro @ `f98f234c` (`aquisicao-detalhe-v1`) | **195** | 403 | READY 160 · DEGRADED 18 · CANARY_FAILED 9 · CONTRACT_PENDING 4 · CANARY_PENDING 2 · SEMANTIC_REVIEW 1 · CAPABILITY_BLOCK 1 |
| **B2** | o mesmo ficheiro @ `63b71421` (`candidate-bridge-v1`) | **160** | 312 | POLICY_BLOCK 69 · RECONCILIATION_REQUIRED 50 · CAPABILITY_BLOCK 20 · READY 18 · CANARY_FAILED 2 · RETRY_AFTER 1 |

```
SOURCES_BOOK_A   85        SOURCES_BOOK_B   195       SOURCES_BOOK_B2   160
UNIÃO A∪B        203       COMMON A∩B       77        ONLY_A 8          ONLY_B 118
ONLY_B2 (nem A nem B)  75  = POLICY_BLOCK 69 + CAPABILITY_BLOCK 6
SOURCES_UNION (A∪B∪B2) 278
```

**São três livros, não dois.** As 237 transições de B2 com chave `IT-*` estão, linha a linha,
dentro de A (0 em falta): B2 é o A de então mais 75 linhas que A nunca recebeu, porque o
ledger ficou congelado por ordem da coordenação na integração bridge+feeder. A e B não
partilham **nenhuma** transição (0 de 263 · 0 de 403): foram semeados em separado sobre as
mesmas 77 fontes, A a partir da missão 04 (21:48 de 20/09), B a partir do registo do motor
e da Big Collection (23:11 de 20/09).

Facto que muda a leitura dos 75: **a chave deles no ledger é `CAND-nnnn`, não `IT-Tn-nnn`.**
A ponte (`ponte_candidatas.py`, igual byte a byte em A e B2) declara isso de propósito: as
barradas nunca terão SOURCE_ID. Nenhum dos 75 tem SOURCE_ID atribuído (alocação e
emparelhamento conferidos): 0 identidades partidas.

---

## 1. F1 — OS DONOS DOS LIVROS

Owner lido do que cada ficheiro **declara**, não do nome.

| livro | FILE | OWNER (declaração) | SOURCES | LAST_VALID_PROOF |
|---|---|---|---|---|
| SOURCE REGISTRY | `docs/fontes/ATLAS-DE-FONTES-EAME.md` | o Atlas: «SOURCE_ID vem do Atlas — nunca do onboarding» (`CANDIDATE-TO-SOURCE-MATCH-V1.json` LEI; `atribuir_source_id.py` cabeçalho) | 190 fichas (cabeçalho 2026-09-15); 242 fichas IT medidas em B @3c0ad4d7 | Atlas 2026-09-15; `SOURCE-ID-ALLOCATION-V1.json` BASE_ATLAS 185 |
| SOURCE ID | `curadoria/SOURCE-ID-ALLOCATION-V1.json` + `CANDIDATE-TO-SOURCE-MATCH-V1.json` | executor `atribuir_source_id.py` / `emparelhar_com_atlas.py`; lei do Atlas («a sequência continua e nunca recicla») | 84 NOVAS · 85 MATCHES · 13 sem território | controlo positivo CAND-0187 ↔ IT-T8-001 casado |
| LIFECYCLE | `curadoria/LIFECYCLE-LEDGER-V1.json` | `lifecycle.py`: «este módulo é o DONO do estado de uma fonte dentro do SOURCE CURATOR»; OWNER=SOURCE_CURATOR em 262/263 linhas (1 COLLECTION: READY→DEGRADED, o único verbo dela) | 85 (A) → **278** depois desta missão | `LIFECYCLE-PROOF-V1.json` 5/5 PASS 2026-09-20T21:50; última CANARY 2026-09-21T03:59:21 |
| QUEUE | `curadoria/LIFECYCLE-QUEUE-V1.json` (CONTRATO `SOURCE_CURATOR_QUEUE/v1`) | `fila.py` («o disco é a fila») | 68 tarefas (67 DONE, 1 BLOCKED), PROXIMO_ID 128 | último UPDATED_AT 2026-09-21T03:59:21 |
| READY | `curadoria/READY-SPLIT-V1.json` (régua) · `READY-SOURCES-V1.json` (interface, `CURATOR_COLLECTION_INTERFACE/v1`) · `READY-BATCHES-V1.json` | `lifecycle.py`: «QUEM PROMOVE PARA READY É O CURATOR. SÓ ELE.»; a régua lê-se na evidência (`ready_split.py`) | 20 READY em A → 87 depois (10 CURRENT + 77 LEGACY) | READY-SPLIT regenerado 2026-09-21T15:20 (esta missão) |
| CONTRACT | `curadoria/italy_contracts_curator.json` (cópia do curator) | dono declarado: **`regras/italy_contracts.mjs`** («o dono do contrato continua a ser regras/italy_contracts.mjs», campo COMO_SE_IMPORTA); a tabela do motor `regras/italy_contracts_onboarded.json` (173) existe em B e **não existe nesta árvore** | 81 contratos do curator (50 YouTube + 27 HTML + 4 do feeder) | `CONTRACT-VALIDATION-V1.json` 77/77 válidos; GERADO_EM 2026-09-21T03:57:42 |
| ROUTE | bloco `ACQUISITION` do contrato + `ROUTE_PROVENANCE` (`integrar_gate_de_detalhe.py` → `DETAIL-GATE-INTEGRATION-V1.json`) + `gate_de_rota.py` (robots) | o dono do contrato; rotas corrigidas: 9 no curator (03:04 de 21/09), 21 no motor em B (passo 2) | 9 + 12 rotas novas | `PROVA-DE-LISTAGENS-V1.json` (B) 35/52 provadas 2026-09-21T00:49; `LISTAGENS-PROVADAS-V1.json` (A) 12/47 2026-09-21T04:05 |
| CANARY | `curadoria/LIFECYCLE-EVIDENCE-V1.json` (CONTRATO `SOURCE_CURATOR_WORKER/v1`) + lotes `CANARY-LOTE-*.json` | `canario.py` executado por `worker.py`; «um contrato válido não é um contrato que funciona» | 65 provas (22 CANARY, 22 REVALIDATE, 13 VALIDATE_ROUTE, 7 BUILD_CONTRACT, 1 REPAIR) | EV-IT-T9-019-CANARY-0065 2026-09-21T03:59:21 |
| DETAIL GATE | `retrato_html.py` (GATE_VERSAO `CAPA_NAO_E_MATERIA/v1`) aplicado em `canario.py` | «o gate tem de existir aqui, no dono que promove a READY» = SOURCE_CURATOR; nasceu em B como `coleta/retrato_html.mjs` | 11 provas com DETAIL_GATE_PASSED=True | 2026-09-21T03:25–03:59 |

**Livro canónico:**

```
CANONICAL_SOURCE_BOOK   curadoria/LIFECYCLE-LEDGER-V1.json  (esta árvore, evoluído por acréscimo)
CANONICAL_OWNER         SOURCE_CURATOR  (lifecycle.py; a Collection só escreve READY→DEGRADED)
```

Porquê este e não um terceiro: `lifecycle.ESTADOS` desta árvore contém todos os estados
necessários (POLICY_BLOCK, CAPABILITY_BLOCK, UNKNOWN, DEGRADED, RETRY_AFTER,
READY_FOR_COLLECTION, RECONCILIATION_REQUIRED). A versão de B **removeu**
`RECONCILIATION_REQUIRED` e falharia fechado ao ler 50 fontes de A. B2 é igual a A.
READY_CURRENT / READY_LEGACY não são estados do lifecycle: são a régua, lida na evidência da
promoção (`ready_split.py`), como a casa já fazia. `RECONCILIACAO-V1.json` é o **censo**
(F2) e o trilho das decisões (F6) — não é um terceiro livro de estado.

---

## 2. F2 — O CENSO POR SOURCE_ID

`curadoria/RECONCILIACAO-V1.json` · 278 linhas, uma por identidade, com `STATE_A/B/B2`,
`CONTRACT_A/B`, `ROUTE_A/B`, `CANARY_A/B`, `DETAIL_PROOF_A/B`, `POLICY_EVIDENCE`,
`CAPABILITY_EVIDENCE`, `LATEST_VALID_EVIDENCE`, `FINAL_STATE`, `FINAL_REASON`,
`LIFECYCLE_TARGET`, `CHAVES_NOS_LIVROS`, `IDENTITY_KIND`, `REVISAO_HUMANA`.
Gerado por `curadoria/reconciliar_livros.py` (B e B2 lidos por `git show` em commits fixos).

```
POR_ESTADO_FINAL (278)
  READY_CURRENT      10
  READY_LEGACY       77
  RETRY               9
  DEGRADED           18
  POLICY_BLOCK       69
  CAPABILITY_BLOCK   17
  UNKNOWN            34
  NOT_READY          44
SOURCE_ID_DUPLICATES  0   (75 chaves CAND-* sem SOURCE_ID; 0 alias)
IDENTIDADES INVÁLIDAS 1   (IT-PROVA-RETRY: fixture de provar_lifecycle.py gravada no livro real → UNKNOWN)
```

### As leis, como foram aplicadas

| lei | como |
|---|---|
| 1 READY exige evidência atual | READY_CURRENT só com os quatro passos NA evidência da promoção; homepage 200 = NOT_READY |
| 2 POLICY_BLOCK não desaparece | preservado se a porta desta árvore confirma TIPO LinkedIn/Instagram e o host bate |
| 3 CAPABILITY_BLOCK não vira READY por omissão | preservado se tem prova; **cede só** se a própria história da fonte continua com prova posterior (4 casos, §3) |
| 4 UNKNOWN não vira READY | READY sem EVIDENCE_REF, ou com referência que esta árvore não confere = UNKNOWN |
| 5/6 contrato e rota atuais vencem | promoção anterior a `ROUTE_PROVENANCE.INTEGRADO_EM` = LEGACY; medição posterior com prova de A sobre o contrato atual vence o READY antigo de B |
| 7 LISTAGEM_DE_NOTICIAS exige item | a BCR que colheu a própria listagem como documento = NOT_READY |
| 8 BOLETIM_SERIADO MAX_TARGETS=1 pode ser correto | os 5 boletins HAND com matéria colhida = READY_LEGACY, não defeito |
| 9 social sem capability | LinkedIn/Instagram POLICY_BLOCK; Facebook CAPABILITY_BLOCK; YouTube tem adaptador provado em B (não nesta árvore — dito na linha) |
| 10 uma identidade | chave canónica por SOURCE_ID; CAND com alias seria fundida (código e teste RT6); 0 ocorrências |

---

## 3. F3 — OS 75 BLOQUEIOS DO BRIDGE, UM A UM

Verificados contra a porta desta árvore (`candidatas/FONTES-CANDIDATAS.json`): os 75
existem, TIPO e host batem (44 `linkedin.com`, 25 `instagram.com`, 6 `facebook.com`).

```
POLICY_BLOCK_IMPORTED         69   (44 LINKEDIN_POLICY + 25 INSTAGRAM_POLICY, de 63b71421)
CAPABILITY_BLOCK_IMPORTED      7   (6 FACEBOOK de 63b71421 + 1 IT-T5-032 de f98f234c: DOCUMENT_ID com `?` não vira pasta no Windows)
BLOCKS_REJECTED_AS_STALE       0
BLOCKS_SUPERSEDED_BY_LATER_EVIDENCE   4   (não é omissão: a mesma linha de bloqueio está em A e A continua com prova)
   IT-T5-041  CAPABILITY_BLOCK 22:54 de 20/09 → contrato com listagem provada 03:57 → canário 03:58 abriu item real (crpv.it/it/news/difesa-dalle-gelate-primaverili-2026)
   IT-T5-051  idem → canário 03:59, item MIXED/NAO_SEI (fica LEGACY)
   IT-T9-015  idem → canário 03:59 (item «lavora-con-noi», pede olho humano)
   IT-T9-019  idem → canário 03:59 (item «articoli-e-pubblicazioni/», pede olho humano)
```

Os 10 CAPABILITY_BLOCK que A já tinha ficaram (7 deles contradizem o CANARY_FAILED de B,
que é a foto anterior à retificação de 22:54).

**Pendência encontrada, fora do escopo:** há **20** candidatas Facebook na porta; a ponte só
barrou 6 porque as outras **14 já estavam no curator** (`SOURCE-CHARACTERIZATION-V1.json`),
e a ponte salta o que «já entrou». Essas 14 não têm linha em **nenhum** dos três livros. O
`READY-FOR-COLLECTION-V1.json` conta-as como `FACEBOOK_CAPABILITY_BLOCK: 14` só em texto.
Não escrevi o bloqueio delas: é verbo da ponte, e a ponte não correu nesta missão.

---

## 4. F4 — READY, RECONTADO PELA EVIDÊNCIA

A régua (`ready_split.passos_da_promocao`): `INDEX_URL → DETAIL_LINKS (≥2) → ITEM ABERTO
(HTTP 200, ≠ índice, ≠ homepage) → BODY ÚTIL (CONTENT + MATERIA_PROVAVEL + ≥800 caracteres
em parágrafos)` + contrato atual. Medido: `DETAIL_GATE_PASSED=True` só prova «não parece
capa» (o gate reprova apenas CAPA_PROVAVEL) — um item MIXED/NAO_SEI passa o gate e **não**
prova corpo. Por isso a régua vive agora num só sítio e é mais estrita do que o gate.

**A hipótese da missão («nenhuma prova passa do passo 2») confirma-se para B (35 listagens
provadas param nas ligações) e para as 12 de A em `LISTAGENS-PROVADAS`. Não se confirma
para 11 canários do worker de A (03:25–03:59 de 21/09), que abriram o item e o retrataram.
Desses 11, 10 têm corpo provado; 1 tem corpo NAO_SEI.**

### FINAL_READY = YES (10)

| SOURCE_ID | fonte | ligações | item aberto (parágrafos) | olho humano |
|---|---|---|---|---|
| IT-T10-018 | Myfruit.it | 29 | news/annamaria-medici-in-ortofrutta-vince-il-valore-percepito (5912) | — |
| IT-T10-022 | Zootecnica International | 8 | news/bob-buresh-2026-psa-poultry-industry-award (3676) | — |
| IT-T5-041 | CRPV | 6 | it/news/difesa-dalle-gelate-primaverili-2026 (3542) | — |
| IT-T5-049 | UNICT Di3A | 4 | it/notizie/avvisi-esami-e-prove-itinere (2769) | — |
| IT-T7-017 | Riunite & CIV | 54 | news-e-eventi/beer-food-attraction-rimini-presentazione-prodotti (1080) | — |
| IT-T7-033 | Chianti Classico | 15 | news/27-ottobre-2025-milano-degustazione-chianticlassicodocg (1911) | — |
| IT-T7-042 | Consorzio Aceto Balsamico | 10 | news-blog/a-sostegno-della-filiera-del-vino-italiano (3786) | — |
| IT-T7-043 | Agrofarma Federchimica | 3 | news-ed-eventi/dettaglio-news/2026/06/07/osservatorio-agrofarma… (1472) | — |
| IT-T9-015 | Conserve Italia | 2 | it/lavora-con-noi (1411) | **SIM** — endereço parece página institucional |
| IT-T9-019 | SCAM | 19 | articoli-e-pubblicazioni/ (2773) | **SIM** — endereço parece secção, não item |

O «olho humano» é uma heurística declarada (`_item_parece_seccao`: menos de 4 palavras no
endereço e nenhum dígito). **Não muda o estado**; exclui da micro-colheita sugerida.

### FINAL_READY = NO — os 77 candidatos a READY recusados, por motivo

| motivo | n | exemplos |
|---|---|---|
| a Big Collection de 20/09 colheu a **capa institucional** como documento (lei 1) | 27 | IT-T12-009, IT-T5-039, IT-T7-031, IT-T2-030 (A) · IT-T1-003, IT-T10-011… (B) |
| colheu a **própria listagem** como documento (lei 7) | 6 | IT-T10-020, IT-T8-008 (A) · IT-T1-002, IT-T2-007, IT-T2-012, IT-T1-021 (B) |
| PDF de papelada a partir da capa; forma NAO_SEI; sem prova de item → **UNKNOWN** | 33 | IT-T1-008, IT-T10-012, IT-T12-003… (LOTE-PDF-INDICE) |
| a corrida real deu **429** → RETRY | 9 | IT-T5-042…050, IT-T7-016, IT-T7-018 (YouTube) |
| canário reprovado no **contrato atual** (A mediu depois de B) | 2 | IT-T12-013, IT-T7-041 |

Lista completa, com `WHY` por fonte: `RECONCILIACAO-V1.json → READY_RECONTADO.CANDIDATOS_READY_RECUSADOS`.

### READY_LEGACY (77) — o que é

| grupo | n |
|---|---|
| YouTube com rota nova `CANAL_PUBLICO_YOUTUBE_V1` provada pela BCR (15 obs cada) — **adaptador em f98f234c, não nesta árvore** | 41 |
| Big Collection colheu matéria com o contrato de hoje, sem gate de detalhe (inclui 5 boletins HAND, lei 8) | 17 |
| rota mudou no passo 2 e a listagem nova está provada até às ligações (PASS_PARCIAL) | 12 |
| corrida real SUCCESS fora do universo do gate (endpoint estático, série com várias observações) | 6 |
| A: gate passou mas corpo NAO_SEI (IT-T5-051) | 1 |

```
STALE_STATES_DISCARDED   147   (estado de um livro contradito pela decisão final)
   B  READY→NOT_READY 35 · READY→UNKNOWN 33 · READY→RETRY 9 · CANARY_FAILED→CAPABILITY_BLOCK 7
   B2 RECONCILIATION_REQUIRED→READY_LEGACY 41 · →RETRY 9 · READY→NOT_READY 8 · CAPABILITY_BLOCK→READY 4 · RETRY_AFTER→UNKNOWN 1
   (as linhas B2 de chave IT-* são o estado de A antes de aplicar: 50 + 6 + 1 = 57 estados de A descartados)
```

---

## 5. F5/F6 — O LIVRO CANÓNICO EVOLUIU, COM TRILHO

`py curadoria/reconciliar_livros.py --aplicar` (commit `dd602746`):

```
LINHAS_ANTES 263 → LINHAS_DEPOIS 754   APENDIDAS 491 = PLANEADAS 491
  324 importadas  (249 de f98f234c · 75 de 63b71421)   campo IMPORTADO_DE {LIVRO, COMMIT, CHAVE_ORIGINAL, OBSERVED_AT_ORIGINAL, MISSAO}
  167 decisões    campo RECONCILIACAO {MISSAO, PREVIOUS_STATE, FINAL_STATE, STATE_A/B/B2, EVIDENCE_SOURCE, EVIDENCE_TIMESTAMP, EVIDENCE_COMMIT, RECONCILIATION_REASON}
CADEIAS_ILEGAIS_NAO_IMPORTADAS  0
as 263 linhas anteriores: byte a byte iguais (conferido contra a cópia em $TEMP)
toda a escrita passou por lifecycle.registar (valida a transição; READY exige EVIDENCE_REF)
SEGUNDA_PASSAGEM_PLANEIA  0   (idempotente)
lifecycle.metricas() depois: READY 87 · CANARY_PENDING 35 · UNKNOWN 34 · POLICY_BLOCK 69 · CAPABILITY_BLOCK 17 · DEGRADED 18 · RETRY_AFTER 9 · CONTRACT_PENDING 4 · CANARY_FAILED 4 · SEMANTIC_REVIEW 1 · SOURCES_TOTAL 278
```

`registar()` ganhou `extra=` (proveniência ao lado das oito chaves canónicas; recusa
sobrescrevê-las). NOT_READY entra no lifecycle como o passo pendente que já lá estava
(CONTRACT_PENDING, CANARY_FAILED, SEMANTIC_REVIEW) ou, quando o que se dizia era READY,
como CANARY_PENDING — remedir pelo gate de detalhe, que é o que `ready_split.remedir` já
fazia nesta casa.

Ficheiros derivados: `READY-SPLIT-V1.json` regenerado (87 = 10 + 77).
`READY-SOURCES-V1.json` e `READY-BATCHES-V1.json` **não** foram regenerados de propósito:
são a entrega à Collection, e o HARD STOP proíbe iniciá-la; quem os regenerar tem de
filtrar por `READY_RULE = DETAIL/v1`, senão entrega 77 LEGACY como se fossem prontas.

---

## 6. GATES

### G-ISO — não contaminar
```
md5 de 38 JSON da curadoria + candidatas/FONTES-CANDIDATAS.json  ANTES de qualquer teste  (guardado em $TEMP)
suite completa corrida 4 vezes (baseline; com os testes novos; depois de aplicar; final)
md5 DEPOIS de cada corrida → IDÊNTICOS (4/4)     git status --porcelain → vazio (4/4)
testes novos isolados (py -m unittest test_reconciliar_livros): 21 OK, md5 idênticos
REAL_SOURCE_BOOKS_UNCHANGED_BY_TESTS = YES
```
A guarda `test_zz_guarda_isolamento.py` passou a cobrir `RECONCILIACAO-V1.json`,
`LISTAGENS-PROVADAS-V1.json`, `SOURCE-ID-ALLOCATION-V1.json`,
`CANDIDATE-TO-SOURCE-MATCH-V1.json`, e exige `LC.LIVRO =` **e** `R.SAIDA =` a quem chama
`R.aplicar`/`R.main` (teste 2d prova que a regra apanha a falta).

### G-RT — red team por mutação (originais em `$TEMP/redteam`, `__pycache__` limpo entre mutantes, mutante confirmado por bytes/`git diff`)

| # | ataque (mutação no reconciliador ou na régua) | entrou | resultado | testes que ficaram vermelhos |
|---|---|---|---|---|
| 1 | só o livro A conta para bloqueios (`for nome in ("A",)`) | sim | **MORTO** | rt1 ×2, capability_cede, aplicar |
| 2 | READY sem EVIDENCE_REF passa (`if False:`) | sim | **MORTO** | rt2_ready_sem_evidencia |
| 3 | homepage vale como item (remover as 3 comparações com índice/homepage) | sim | **MORTO** | rt3_homepage |
| 4a | a primeira linha do ficheiro vence (`setdefault`) | sim | **MORTO** | 4 testes, incl. o censo dos livros reais |
| 4b | READY antigo de B vence sem comparar datas | sim | **MORTO** | rt4_conflito |
| 4c | a decisão devolve sempre A e ignora B | sim | **MORTO** | rt5, reconciliation_required, aplicar |
| 5 | READY com referência mas sem corrida real conferível passa | sim | **MORTO** | rt5, rt2b |
| 6 | dedup por SOURCE_ID neutralizado (`alvo = None`) | sim | **MORTO** | rt6 |

Um primeiro 4b **sobreviveu**: desligava um ramo redundante com o ramo seguinte (decisão
igual por outro caminho). Código redundante é onde um mutante se esconde; o ramo foi
removido e o ataque repetido contra o que ficou. Todos os ficheiros restaurados byte a byte.

```
RED_TEAM_PROVEN = YES   (8 mutantes mortos, 0 sobreviventes, 1 equivalente eliminado)
```

### G-REG
```
TESTS_BEFORE 234 OK     TESTS_AFTER 256 OK (234 + 21 reconciliação + 1 guarda)     NEW_FAILURES 0
```

### G-MAP
```
py system-map/scripts/correr_a_cadeia.py REGERAR   → CADEIA=OK (20/20)
py system-map/scripts/correr_a_cadeia.py VALIDAR   → 22 provas PASS · SYSTEM_MAP_CHECK=PASS
P9_CODIGO_DECLARADO PASS: reconciliar_livros.py, test_reconciliar_livros.py e RECONCILIACAO-V1.json reivindicados
PORTOES_POS_COMMIT → §11
```
Efeito colateral medido: o censo de endereços subiu 439 → 441 porque o scanner apanha
`https://ex.it/news` dos testes sintéticos (URL dentro de `.py`; já acontecia à casa).

---

## 7. GATE FINAL — MICRO-COLLECTION

```
MICRO_COLLECTION_ALLOWED = YES — restrita às 8 READY_CURRENT sem pedido de olho humano
BIG_COLLECTION_ALLOWED   = NO
```

| condição | estado |
|---|---|
| existe conjunto READY_CURRENT | 10 (8 limpas + 2 com REVISAO_HUMANA) |
| identidade reconciliada | 278 identidades, 0 duplicados |
| contratos atuais | as 9 com `ROUTE_PROVENANCE` foram canariadas **depois** de 03:04:17; IT-T5-041 contratada 03:57 e canariada 03:58 |
| rotas atuais | INDEX_URL das 10 é a listagem corrigida (não a homepage, exceto myfruit/conserveitalia/scam onde o canário enumerou 29/2/19 ligações) |
| detail gate | 10/10 com DETAIL_GATE_PASSED + CONTENT + MATERIA_PROVAVEL + ≥1080 caracteres em parágrafos |
| policy/capability preservados | 69 + 17, 0 rejeitados |
| testes verdes · red team verde · worktree limpa · push | 256 OK · 8/8 · limpa · §11 |

**As 8 sugeridas para o próximo teste:** IT-T10-018 · IT-T10-022 · IT-T5-041 · IT-T5-049 ·
IT-T7-017 · IT-T7-033 · IT-T7-042 · IT-T7-043. (IT-T9-015 e IT-T9-019 só depois de alguém
abrir o item a olho.) A evidência tem ~12 h; o adaptador YouTube **não** está nesta árvore,
e nenhuma das 8 é YouTube.

---

## 8. NÃO SEI / pendências (nomeadas, não resolvidas aqui)

1. **33 fontes LOTE-PDF-INDICE em UNKNOWN**: a Big Collection colheu PDFs «de papelada» a
   partir da capa; não sei se por trás há itens de publicação. `NEEDS_NETWORK_PROOF`.
2. **41 YouTube READY_LEGACY com adaptador noutra árvore** (`f98f234c:coleta/adaptadores_de_aquisicao.mjs`).
   Uma Collection corrida daqui falharia nelas. A linha do livro diz-o.
3. **14 candidatas Facebook sem linha em nenhum livro** (§3).
4. **IT-T9-015 / IT-T9-019**: o item aberto tem corpo mas o endereço parece institucional/secção. Não abri (zero rede).
5. **IT-PROVA-RETRY** no livro real (fixture de `provar_lifecycle.py`). Marcado UNKNOWN com razão; não se apaga.
6. **A fila** diverge entre A (28 tarefas só aqui) e B2 (70 só lá; 2 TASK_IDs com fonte diferente) — medido no relatório do bridge; não reconciliei a fila, só os livros de estado.
7. **A porta** continua a dizer `EM_ANALISE` para as 75 barradas (B2 diz `RECUSADA`). Mudar o estado da candidata é verbo da ponte (`FN.gravar`); não o usurpei.
8. **`test_lifecycle.py` e `test_interface_collection.py` deixam `LC.LIVRO` redirecionado** para uma pasta descartável já apagada (medido com sonda por módulo). O teste dos livros reais protege-se fixando o caminho; a suíte inteira passa, mas o defeito fica.
9. **`READY-SOURCES-V1.json` está velho** (diz 18 READY, 0 CURRENT). Não regenerado (§5).
10. **IT-T5-035 / IT-T5-036**: `C7_CONTRATO_DUPLICADO` em B (dois contratos, mesmo índice). Ambos NOT_READY (capa). Identidade não fundida: SOURCE_ID diferentes, e não sei qual é a fonte.

---

## 9. O que esta missão NÃO fez (por desenho)

Não correu Collection, Big Collection, Sala, Intelligence nem Portal. Não tocou noutras
worktrees (`cutover-v2` tem agente vivo). Não fez um único pedido de rede. Não escolheu um
livro inteiro. Não usou «o mais recente vence» (a data só corrobora prova; sem prova, não
decide). Não criou terceiro livro de estado.

---

## 10. Ficheiros desta missão

```
curadoria/reconciliar_livros.py           o reconciliador (censo, plano, aplicar, verificação)
curadoria/test_reconciliar_livros.py      21 testes (RT1–RT6 e leis) + censo dos livros reais (só lê)
curadoria/RECONCILIACAO-V1.json           o censo: 278 linhas + contagens + trilho
curadoria/LIFECYCLE-LEDGER-V1.json        263 → 754 linhas (append-only)
curadoria/READY-SPLIT-V1.json             regenerado
curadoria/lifecycle.py                    registar(extra=)
curadoria/ready_split.py                  passos_da_promocao() — a régua de quatro passos
curadoria/test_zz_guarda_isolamento.py    cobre o censo e quem o aplica
RELATORIO-RECONCILIACAO.md                este ficheiro
```

---

## 11. FECHO (preenchido depois do mapa e do push)

```
PORTOES_POS_COMMIT      pendente
FINAL_HEAD              pendente
REMOTE_HEAD             pendente
```

---

## EM PALAVRAS SIMPLES

**Porque havia livros a mais.** Imagina três cadernos onde três pessoas anotaram, cada uma
no seu canto, se cada fonte de notícias estava "pronta para ir buscar". O caderno A é o desta
mesa. O caderno B é da mesa ao lado, que fez uma corrida grande de recolha no dia 20 e
escreveu "pronta" em 160 fontes. O caderno B2 é da mesa da ponte, que recebeu 75 fontes de
redes sociais (LinkedIn, Instagram, Facebook) e escreveu "proibido" ou "não sabemos ir lá"
para cada uma — mas esse caderno foi guardado numa gaveta fechada, e a mesa A nunca copiou
essas 75 linhas. Ninguém estava a mentir. Estavam a escrever em cadernos diferentes.

**Quantas fontes realmente diferiam.** Juntando os três cadernos dá 278 fontes. Só 77 estão
nos dois cadernos grandes ao mesmo tempo. Dessas 77, 59 tinham estados diferentes — mas 50
dessas 59 são canais de YouTube em que A dizia "medir de novo com a rota nova" e B tinha
mesmo medido com a rota nova. Não era desacordo: era uma pergunta e a resposta em cadernos
separados.

**Quantas diferenças eram bloqueios, não desacordo sobre prontidão.** 75 das diferenças eram
só isto: o caderno da ponte tinha 69 "proibido pelas regras da plataforma" e 6 "não temos
ferramenta para o Facebook", e os outros dois cadernos não sabiam. Um "proibido" não deixa
de valer porque outro caderno não o copiou. Conferi os 75 contra a lista de candidatas desta
mesa: todos batem. Entraram todos no caderno oficial.

**Qual verdade ficou.** O caderno A passou a ser o único, e cresceu de 263 para 754 linhas
sem apagar nenhuma das antigas: cada linha nova diz de que caderno veio e porquê. O
resultado, fonte a fonte:

- 10 fontes têm a prova completa: fomos à página de índice, encontrámos ligações, abrimos
  uma notícia e ela tinha texto de verdade. Só estas contam como **prontas**.
- 77 estão "quase": a rota funciona, mas ninguém abriu ainda uma notícia com a régua nova
  (41 delas são YouTube, cuja ferramenta está na outra mesa, não nesta).
- 44 **não estão prontas**: quando a recolha grande foi lá, trouxe a capa do site ou a
  página de lista em vez de uma notícia. Isso é o erro que a régua nova existe para apanhar.
- 34 são **não sei**: 33 sites de onde vieram PDFs de burocracia, e 1 linha de teste que
  alguém deixou no caderno real.
- 9 levaram "volte mais tarde" (o YouTube limitou o ritmo), 18 falharam na corrida, 69
  estão proibidas, 17 precisam de ferramenta que não há.

Zero honesto? Não. A missão suspeitava que nenhuma prova chegava ao fim; encontrei 11 que
chegam, e uma delas cai porque o texto da página era meio notícia, meio menu. Ficam 10, e
em 2 dessas o endereço da página aberta parece uma secção ("trabalhe connosco",
"artigos e publicações") — pedi que alguém as veja com os olhos antes de as usar.

**Já se pode fazer a micro-recolha?** Sim, mas pequena e com nome: só nas 8 fontes com prova
completa e sem dúvida. Não com as 77 "quase", não com o YouTube daqui, e a recolha grande
continua proibida. Antes disso, quem for regenerar a lista que se entrega à recolha tem de
filtrar pela régua nova, senão entrega 77 fontes "quase" como se estivessem prontas.

**O que pode partir.** Nada foi apagado; os testes (256) passam; os livros não mudaram
durante os testes (impressão digital igual antes e depois); o mapa do sistema foi regerado
e validado. Se alguém correr a ponte "a sério" nesta árvore, ela vai encontrar os 75 já no
caderno e não os repete — mas vai também enfileirar 72 tarefas de qualificação, e isso é
decisão de quem a correr, não desta missão.
