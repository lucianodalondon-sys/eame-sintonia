# RELATÓRIO — BIG COLLECTION RELEASE: A PRÓXIMA BIG COLLECTION

```
BANCADA      big-collection-release-v1
BASE         96dcd6bd  (curator-04a-integration, INITIAL_HEAD — medido)
LANE YOUTUBE claude/youtube-canonical-free-route-v1 @ 7857d7b7  (local == origin — medido)
DATA         2026-09-20
MODEL        claude-fable-5-1
```

**Git venceu o briefing onde divergiu, e divergiu pouco.** Cada `MEDIDO` da secção 0
da missão foi reconfirmado antes de agir (§1). A corrida real aconteceu: 181 fontes,
uma por processo, `PAID_USD = 0`, e a Sala cresceu de 29 para 46.

    BAIXAR NÃO É COLHER; COLHER NÃO É ADMITIR.
    872 observações baixadas · 668 derivados · 17 admitidos.

---

## 1 · O QUE CONFIRMEI DA SECÇÃO 0 (e onde o número era outro)

| Medição do coordenador | Reconfirmado | Nota |
|---|---|---|
| `BANCADA_BASE = 96dcd6bd`, limpo | ✅ igual | só `MISSAO-BIG-COLLECTION-RELEASE.md` por rastrear |
| `IT_TRUNK_V1 = 606974c3` ancestral de 96dcd6bd e de 7857d7b7 | ✅ igual | `merge-base --is-ancestor` nos dois |
| `YOUTUBE_HEAD = 7857d7b7`, local == origin | ✅ igual | após `git fetch` |
| `MERGE_BASE(04a, youtube) = 370ce450`, 3 commits de cada lado | ✅ igual | |
| 04A fechou: `HTML_CONTRACTS_INTEGRATED = 18` (105 → 123), `YOUTUBE_READY_INTEGRATED = 0` | ✅ igual | lido da tabela e do carregador: `ONBOARDED 123 · CONTRACT_IDS 136` |
| 6 conflitos no merge: 5 gerados + `CENSO-DAS-LIGACOES-DA-COLLECTION.md` | ✅ igual | `merge-tree` reconfirmou os 6, nem mais nem menos |
| Contradição «50 bloqueadas» × «ROBOTS_GATE = PASS» = duas rotas | ✅ confirmado ao vivo | feed `Disallow`; `/channel/<ID>/videos` e `/watch?v=` permitidos — pelo leitor único da casa, 50/50 (§2) |
| Preflight: `pg_isready 54330` aceita; `SALA_DSN.txt`, `psql.exe`, armazém 78 MB com marcador | ✅ igual | `PAID_ROUTE_ENABLED = NO`; nenhuma `SINTONIA_*` nem `BANCO_DESCARTAVEL_URL` no ambiente da sessão |
| `SALA_BEFORE = 29` | ✅ igual | `select count(*) from sala_de_espera` |
| «os dois canários (IT-T8-001, IT-T7-015) também não estavam na tabela; trabalhe sobre as 50» | ⚠️ **diferente** | IT-T7-015 está nas 50; **IT-T8-001 não está** — é uma 51.ª fonte YouTube com contrato à mão sem bloco executável. Trabalhei sobre as 50 do curator; IT-T8-001 fica registada em §9 |
| lane YouTube: `CUSTOM_ADAPTER`, identidade lida do canal, zero switch por SOURCE_ID, 11 testes | ✅ igual | 11/11 nesta árvore (`node --test`) |

Achado que a missão não previa: o **colector italiano não chama o portão de robots em
tempo de coleta** (`italy_pilot_collect.mjs` usa `curl` directo; `permitido()` só corre em
`scrap_http.buscar`, a rota social). O portão da rota italiana é de *onboarding*. Por isso
o `ROBOTS_GATE` das 50 foi medido por mim, ao vivo, antes da corrida — não herdado.

---

## 2 · INTEGRAÇÃO DA ROTA YOUTUBE (commit `fb45dd5d`)

Merge de `7857d7b7` sobre `96dcd6bd`, sem recriar nada. Os 6 conflitos não se resolveram à
mão: tomou-se o lado `96dcd6bd` e correu-se a cadeia canónica sobre a árvore fundida. O
`CENSO-DAS-LIGACOES-DA-COLLECTION.md` é saída do gerador (diz `COMO_REFAZER` no cabeçalho);
o regenerado carrega os dois factos — «297 bases com ficha» (lado 04A) e `V-YOUTUBE` +
`canario_youtube_canonico.mjs` na peça `C-IT-COLETA` (lado YouTube). Validador: 22/22 PASS.

`data/derivados/O-CENSO-DA-SALA-DE-ESPERA.json`: a lane trazia a versão reescrita pela
suíte dela (resíduo de teste, 04A §7.5); mantida a de `96dcd6bd`. Nenhuma das duas é
medição desta árvore.

O que entrou: `CANAL_PUBLICO_YOUTUBE_V1` no registry canónico
(`coleta/adaptadores_de_aquisicao.mjs`), os 11 testes, o canário canónico. **Nada de
`feeds/videos.xml`, nada de yt-dlp, nada de chave, cookie ou login.**

---

## 3 · ONBOARDING DAS 50 FONTES YOUTUBE (commits `5920d77d`, `f93ee597`)

**Mecanismo único, zero código por SOURCE_ID.** Cada uma das 50 é uma linha em
`regras/italy_contracts_onboarded.json` (lote `LOTE-YOUTUBE-CANAL`): `STRATEGY
CUSTOM_ADAPTER · ADAPTER_ID CANAL_PUBLICO_YOUTUBE_V1 · CHANNEL_ID` (o do contrato do
curator, byte a byte) `· MAX_TARGETS 15` (o do curator) `· OUTPUT_TYPE HTML` (a página
`/watch` é o que se traz). A caracterização do curator chega inteira, com os `NAO SEI`.

**Identidade: a que o curator já declarava.** `videoId` nativo, `PLATFORM_NATIVE_ID`,
`DOCUMENT_ID = <SOURCE_ID>:YT:<videoId>`, lido do endereço do alvo com o vocabulário
`CONTENT_CAPTURE` do motor. Não foi a primeira escolha — ver §3.2.

**Canário canónico pelo motor** (`alvosDoContrato` + registry `ADAPTERS`, 51 pedidos,
`PAID_USD = 0`), robots pelo leitor único da casa, registado em
`data/derivados/YOUTUBE-CANARIO-50-2026-09-20.json`:

```
YOUTUBE_TOTAL = 50   TESTED = 50   PASS = 50   FAIL = 0   READY = 50
ROUTE_RESOLVED 50/50 · ROBOTS_GATE 50/50 PASS · IDENTITY_MATCH 50/50 · TARGETS 5..15
GATE_FEED_XML = (False, «robots.txt do host barra este caminho»)   GATE_WATCH = (True, permite)
SONDA de 1 página /watch: HTTP 200, 1.227.587 bytes, começa por «<!DOCTYPE html>»
```

| SOURCE_ID | CHANNEL_ID | CONTRACT | ROUTE_RESOLVED | ROBOTS_GATE | IDENTITY_MATCH | TARGETS_DISCOVERED | VEREDITO |
|---|---|---|---|---|---|---:|---|
| IT-T2-025 | `UC1vKirvt0hzsqE9zQAs9nTw` | VALID | YES | PASS | YES | 14 | READY_FOR_COLLECTION |
| IT-T2-026 | `UCTK_ULXg3gzn8el_oFk-5eA` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T2-027 | `UCamw8rL1JPLjfa3Bx6ax8Eg` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T2-028 | `UCtBD35n-HE7x_MWnjc1kt7g` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T5-037 | `UCOiX7jy7G-NMPtaA9QaNQrg` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T5-038 | `UC3HdHdHUZomg1l3K_UWv9PQ` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T5-040 | `UCH-UMwlZXbrOb3RrL2GejMA` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T5-042 | `UCm-f74uymvl9TOLWqf6GOpA` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T5-043 | `UCDNXhv9mPzYo5FQKkg_oSWw` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T5-044 | `UCiECZ69Hbfmcsu8O54r3geQ` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T5-045 | `UCUpCShTEkFvbXHCQRiWczjQ` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T5-047 | `UCWD-2QiKuzZIA8WW1SAoH0w` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T5-048 | `UCKdQcnPtPZs3k08e5jrFSNQ` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T5-050 | `UCWRr0vMGqdmyqzdm3bNGY4Q` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-015 | `UCJi1Vrelq8obdmS_UXP3T2g` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-016 | `UCHm8wgnyeNFP2luUq_lMPMg` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-018 | `UCfqqPifpfaZUI30hxiygmJw` | VALID | YES | PASS | YES | 5 | READY_FOR_COLLECTION |
| IT-T7-020 | `UCfYSI-_mzA0BWZwHcPrO0vg` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-022 | `UC_yfE6hgWx4FBDCz1PmLjxw` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-023 | `UCFkdwOroXwCFMXHneVMeYqQ` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-024 | `UCdJ3sb6r1X0pjU6XR9OMdGw` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-025 | `UC0iNaYRRl9AJzjRxOHxIpsQ` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-026 | `UC4LCuwIcRPhrE2mFJ8ZXtLg` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-027 | `UCEgJbey3UogPJPmdlBEAjKQ` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-028 | `UCJbuSrQ57Z-dAYGI7n2VwPg` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-030 | `UCZb5Epldni2gfgoXoN15tGA` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-032 | `UCC19gccUupOm590hcozwdBA` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-034 | `UCFEHyFgwGUYCa2OKHjDUd1g` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-035 | `UCosKzVZGcw6VR3sW9QKGkVw` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-036 | `UC3VPPuduz1p_fouWblztteQ` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-037 | `UCpdWeEtUCU1aHhJnj2TwheA` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T7-039 | `UCmRWXB6nOPLc5x42XXhGrWg` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T8-004 | `UCrCabYjtyqdzu1zXo95o7Jw` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T8-005 | `UCB345okRbU6TqQyWXd8D8oA` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T8-006 | `UCLqKnJJf6VBExBf5qp8N74w` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T9-014 | `UCB3cnpKOvT56elhTKE7cjSg` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T9-016 | `UC84-4aKRmQbIG5eprbIaR9Q` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T9-017 | `UCmPpv0_TilfaF9Df5SzeFiQ` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T10-017 | `UCfdN2DQZBfZo-7VgBqotYuQ` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T10-019 | `UCVc4Edn_BaeH00XULZ0SqgQ` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T11-006 | `UCS-EXLzpmRwcnJNsm9SWJdA` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T11-007 | `UCxqWrxc-sInT6ODtyHUzZRA` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T12-007 | `UCEg22ii3Awy6eyRybNqO-8Q` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T12-008 | `UCpiryXByW32kGxQXTlbnSXA` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T12-010 | `UCH_LCqE9qGb6TvpXwGudNbQ` | VALID | YES | PASS | YES | 13 | READY_FOR_COLLECTION |
| IT-T12-011 | `UCZvge-xP6fg5S5DvUxjNbGQ` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T12-012 | `UCZd755PSrP2Jm8zk38LgtHA` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T12-014 | `UC8fp1anRLt5xmyirKPIE_zg` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T12-015 | `UCxIuSXfCNVnzTLD3EJFcQng` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |
| IT-T12-016 | `UC4wxlAIQauBZe7CDnLXkWqA` | VALID | YES | PASS | YES | 15 | READY_FOR_COLLECTION |

### 3.1 · Remendos genéricos que a tabela exigiu (nenhum conhece SOURCE_ID)

| ficheiro | o quê | porquê |
|---|---|---|
| `regras/italy_contracts.mjs` | `contratoGenerico()` expande linhas `CUSTOM_ADAPTER` (entrada canónica da linha, `DISCOVERY_METHOD` com o nome do adapter, `ROUTE_TYPE APPLICATION_ROUTE`) e honra uma `IDENTITY` declarada na linha, conferida por `conferirIdentidade` | sem isto, `CANONICAL_ENTRY_URL` saía `undefined` e a descoberta dizia «abrir INDEX_URL» |
| `pedido/receitas.py` | o colector italiano passa a servir **T8** (3 canais); entra depois do `scrap-colheita` que T8 partilha com T9; `fonte=` promove-o | sem isto, `colete influenciadores da italia` não tinha executor para a tabela |
| `tests/test_integracao_04a_curator.py` | diz a verdade nova: 173 na tabela; as 50 pelo canal e nunca pelo feed; `PLATFORM_NATIVE_ID` com captura | 17/17 OK |
| `regras/motor_de_rota_test.mjs` | «toda linha genérica tem `IDENTITY_KIND = URL_PATH`» evolui para «`URL_PATH` ou `PLATFORM_NATIVE_ID` declarado, nunca calado», com captura e sem `? * " < > \|` no DOCUMENT_ID | 1/1 PASS |
| `docs/fontes/ATLAS-DE-FONTES-EAME.md` | `ESTADO_BCR:` nas 50 fichas, ao lado do `ESTADO_04A` (que fica) | 50 inserções, 0 remoções |

Resultado no carregador: `CONTRACT_IDS 136 → 186 · ONBOARDED 123 → 173 · executáveis 182`,
todos a passar `conferirAquisicao` + `conferirIdentidade`. `regras/italy_contract_test.mjs`:
94 `FALHA` antes e depois (pré-existente, `RAW_EVIDENCE_STATE`).

### 3.2 · O primeiro teste de fumo falhou — e não foi a fonte

`IT-T7-015` pela porta canónica: `FAILED · COLHEITA 0 · ERROS [] · PORQUE_ZERO_COLHEITA
null`, e o orquestrador imprimiu como ERRO o aviso do Python desta máquina («Could not
find platform independent libraries»), que a BC2 inteira também tinha nas 113 corridas
SUCCESS. Chamando o colector directamente: **`mkdir ENOENT` em
`…/IT-T7-015_URL_watch?v=f-Up25Lyn9I/…`** — o DOCUMENT_ID genérico é o endereço, e
`pastaDoDocumento()` faz dele o nome da pasta trocando só `: / \`; o `?` é ilegal em
caminho Windows. A saída foi a identidade do curator (acima). O defeito da pasta **não
foi corrigido** (§9, B1) — e mordeu outra vez na corrida (IT-T5-032).

Segundo teste de fumo (`IT-T7-2026-09-20-190507-1de3b5b72cb820f7`): SUCCESS, 15 alvos,
15 preservados, `HEALTHY/NEW_DOCUMENT`, Admissão `NAO_SEI 13 · NAO 2`, 189 s. A primeira
corrida de fumo (`…185934…`, FAILED) fica no `RUN-MANIFEST` como registo; não chegou ao
banco.

---

## 4 · READY REAL — medido no estado integrado (`f93ee597`)

Regra: contrato com bloco executável que passa `conferirAquisicao` + `conferirIdentidade`
∧ ficha no Atlas ∧ território com frase de pedido.

```
READY_EXISTING  = 113   (8 à mão + 105 onboarded de 18/09)
READY_NEW_HTML  =  18   (04A)
READY_YOUTUBE   =  50
READY_TOTAL     = 181   de 186 contratos
FORA (5): IT-T3-005 sem ficha no Atlas · IT-T1-001, IT-T7-002, IT-T9-008, IT-T8-001 sem bloco executável
POR TERRITÓRIO: T1 22 · T2 27 · T3 13 · T4 1 · T5 43 · T7 28 · T8 4 · T9 8 · T10 18 · T11 3 · T12 14
```

**Famílias bloqueadas — medidas, não resolvidas:**

```
LINKEDIN_BLOCKED  = 6 contas (CONTAS-V1.json · ACCOUNTS) + 1 ficha no Atlas   → 0 contratos executáveis
INSTAGRAM_BLOCKED = 7 contas + 1 ficha no Atlas                                → 0 contratos executáveis
FACEBOOK_BLOCKED  = 17 contas                                                  → 0 contratos executáveis
(+ 14 contas YouTube em CONTAS-V1 que NÃO são as 50 do curator — são contas de concorrentes; não tocadas)
```

Nenhuma destas entra na rota `italia-recorrente`; nenhuma foi tocada.

---

## 5 · PREFLIGHT — confirmado

```
SALA_RUNNING = YES  (127.0.0.1:54330 accepting connections)
SINTONIA_SALA_DSN = %USERPROFILE%\sintonia-sala-italia\SALA_DSN.txt (existe; nunca impresso)
SINTONIA_PSQL_EXE = C:/Users/London1/orca/pgtmp/pgsql/bin/psql.exe (existe; declarado no ambiente da corrida)
SINTONIA_ARMAZEM_RAIZ = %USERPROFILE%\sintonia-sala-italia\armazem (78 MB antes · 589 MB depois; marcador presente)
EGRESSO = Milão, IT (Proton AG)     PAID_ROUTE_ENABLED = NO
BACKUP antes da corrida: pg_dump -Fc → backups/sala_italia_antes_BCR_2026-09-20.dump (1.240.724 bytes)
```

---

## 6 · A BIG COLLECTION

```
BIG_COLLECTION_RUN_ID = BCR-2026-09-20   (um RUN_ID por fonte; janela 2026-09-20T18:59:34Z → 21:50:35Z)
DRIVER   %TEMP%\bcr\bcr.py — um pedido por fonte, em processo próprio, saída em out/<SID>.stdout|stderr.txt
PEDIDO   py orquestrador/orquestrador.py "<frase do território>" --filtro pais=IT --filtro fonte=<SID> --filtro universo=<Tn>
ORDEM    113 existentes → 18 HTML 04A → 50 YouTube
SOURCES_SELECTED = 181   SOURCES_ATTEMPTED = 181   SOURCES_SUCCESS = 151   SOURCES_FAILED = 30
TEMPO    7.587 s de fonte (média 41,9 s; máx 189 s) + ~15 min de espera por 429 + pausas de 45 s
PAID_USD = 0   (COST_USD_BCR = 0 no banco; nenhuma rota paga existe para estas fontes)
```

### 6.1 · O limite de taxa do YouTube, e o que se fez

Depois de ~120 páginas `/watch` em 15 min, o YouTube passou a responder `302 →
google.com/sorry → 429` a todas: 8 fontes seguidas com 15/15 alvos em 429 (a descoberta
pelo canal continuava a responder 200). O driver foi parado **entre fontes** às 20:04Z
(a corrida de IT-T7-020 em curso foi interrompida: 10 linhas de observação 429 no ledger
do colector, sem registo de corrida, sem bytes — refeita depois com sucesso), e retomado
às 20:05Z com uma **sonda de 1 pedido** antes de cada fonte YouTube (espera em passos de
5 min, tecto 60 min) e **pausa de 45 s** entre fontes. O 429 aliviou em ~15 min. Não se
trocou de IP nem de UA: fugir a um 429 é contorno. As 9 fontes que caíram no 429 ficam
`POLICY_BLOCK` — uma corrida por fonte, sem repetição.

### 6.2 · Resultado por classe e família

| FAMÍLIA | POLICY_BLOCK | ROUTE_FAILURE | SOURCE_FAILURE_SEM_OBS | SUCCESS | total |
|---|---:|---:|---:|---:|---:|
| EXISTING_HAND | 0 | 0 | 0 | 8 | 8 |
| EXISTING_ONBOARDED | 0 | 20 | 1 | 84 | 105 |
| NEW_HTML_04A | 0 | 0 | 0 | 18 | 18 |
| YOUTUBE | 9 | 0 | 0 | 41 | 50 |
| **total** | 9 | 20 | 1 | 151 | 181 |

`SOURCES_FAILED = 30` = `ROUTE_FAILURE 20` (16 `EMPTY_LIST`, 1 índice 503, 1 reset, 1
alvo 400, 1 alvo 404) + `POLICY_BLOCK 9` (YouTube 429) + **`CAPABILITY_GAP 1`**
(IT-T5-032: a corrida saiu `FAILED` com zero itens e sem razão; medido a chamar o
colector directamente: `mkdir ENOENT` em `…news-studenti?view=elenco…` — o mesmo defeito
de §3.2. O executor não tem ramo para este alvo; o dono é a casa, não a fonte). O medidor
automático tinha-a como `SOURCE_FAILURE_SEM_OBS`; a classe acima é a da regra da missão.

| motivo da falha (primeira observação) | n |
|---|---:|
| EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PATTERN | 16 |
| status 429 / 3404 bytes | 9 |
| status 400 / 155 bytes | 1 |
| status 404 / 362228 bytes | 1 |
| Could not find platform independent libraries <prefix>
 | 1 |
| indice inacessivel: curl: (35) Recv failure: Connection was reset
 | 1 |
| indice inacessivel: 503 | 1 |

### 6.3 · Por fonte (181 linhas — o registo)

`FAMÍLIA`: `EXISTING_HAND` contrato à mão · `EXISTING_ONBOARDED` tabela de 18/09 ·
`NEW_HTML_04A` · `YOUTUBE`. `resultados` = `OBSERVATION_RESULT` do colector; `admissão` =
Livro de Decisões da corrida.

| SOURCE_ID | T | FAMÍLIA | RUN_ID | CLASSE | s | obs | HEALTHY | resultados | admissão (Livro) | motivo (se falha) |
|---|---|---|---|---|---:|---:|---:|---|---|---|
| IT-T1-002 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191235-eb94a10a12884b64` | SUCCESS | 13.4 | 1 | 1 | SEEN_AGAIN=1 | NAO_SE_APLICA=1 |  |
| IT-T1-003 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191247-1dba6f8f941c5b8c` | SUCCESS | 12.6 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SE_APLICA=1 |  |
| IT-T1-004 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191300-0374ba8f59677735` | ROUTE_FAILURE | 8.9 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T1-005 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191308-2f2ccea3aa242d38` | SUCCESS | 15.5 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SE_APLICA=1 |  |
| IT-T1-006 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191324-803240b56549a13a` | SUCCESS | 15.9 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SE_APLICA=1 |  |
| IT-T1-007 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191340-fce6e104e4f4af65` | SUCCESS | 14.1 | 1 | 1 | SEEN_AGAIN=1 | NAO_SE_APLICA=1 |  |
| IT-T1-008 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191354-b5f6f135c505ff87` | SUCCESS | 13.5 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T1-009 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191407-b2ebe9f3986b66c5` | SUCCESS | 13.0 | 1 | 1 | SEEN_AGAIN=1 | NAO_SE_APLICA=1 |  |
| IT-T1-010 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191421-e54aa65268e07164` | SUCCESS | 11.9 | 1 | 1 | SEEN_AGAIN=1 | NAO_SE_APLICA=1 |  |
| IT-T1-011 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191433-1536b525db16df88` | SUCCESS | 14.1 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SE_APLICA=1 |  |
| IT-T1-012 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191447-5c7a1ddd7de5c44a` | ROUTE_FAILURE | 8.1 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T1-013 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191455-05c83e78a2b754cd` | SUCCESS | 11.1 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SE_APLICA=1 |  |
| IT-T1-014 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191506-e479cbc3504800e6` | ROUTE_FAILURE | 8.1 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T1-015 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191514-df2e417b03513734` | ROUTE_FAILURE | 10.7 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T1-016 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191525-bda65292ddf268cd` | SUCCESS | 14.1 | 1 | 1 | SEEN_AGAIN=1 | NAO_SE_APLICA=1 |  |
| IT-T1-017 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191539-34e0ef5fed39407a` | ROUTE_FAILURE | 9.8 | 1 | 0 | TRANSPORT_OR_EMPTY=1 | NAO_SEI=1 | status 400 / 155 bytes |
| IT-T1-018 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191549-1a2fb52953efaa4b` | SUCCESS | 14.3 | 1 | 1 | SEEN_AGAIN=1 | NAO_SE_APLICA=1 |  |
| IT-T1-019 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191603-1321e1bd1b3b98e7` | SUCCESS | 15.7 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T1-020 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191619-b3415351ccad4317` | ROUTE_FAILURE | 9.3 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T1-021 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191628-52120846fd64a5a5` | SUCCESS | 11.3 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SE_APLICA=1 |  |
| IT-T1-022 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191639-403ffcb4c3d3619a` | SUCCESS | 20.5 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SE_APLICA=1 |  |
| IT-T1-023 | T1 | EXISTING_ONBOARDED | `IT-T1-2026-09-20-191659-0b158479b96676a0` | ROUTE_FAILURE | 9.8 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T10-002 | T10 | EXISTING_ONBOARDED | `IT-T10-2026-09-20-193142-c5fd40d5faf505ab` | ROUTE_FAILURE | 7.4 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T10-006 | T10 | EXISTING_ONBOARDED | `IT-T10-2026-09-20-193149-c29ef9fa74a76e74` | ROUTE_FAILURE | 7.1 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T10-007 | T10 | EXISTING_ONBOARDED | `IT-T10-2026-09-20-193156-a06aa070dc4ef38e` | SUCCESS | 17.7 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SE_APLICA=1 |  |
| IT-T10-008 | T10 | EXISTING_ONBOARDED | `IT-T10-2026-09-20-193214-ce1dfbaba93be0af` | ROUTE_FAILURE | 8.1 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T10-009 | T10 | EXISTING_ONBOARDED | `IT-T10-2026-09-20-193222-aee17e0ede6713e6` | SUCCESS | 10.8 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SE_APLICA=1 |  |
| IT-T10-010 | T10 | EXISTING_ONBOARDED | `IT-T10-2026-09-20-193233-ea35142fd47b1e28` | SUCCESS | 8.2 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T10-011 | T10 | EXISTING_ONBOARDED | `IT-T10-2026-09-20-193241-ca803f52619b2920` | SUCCESS | 17.6 | 1 | 1 | SEEN_AGAIN=1 | NAO_SE_APLICA=1 |  |
| IT-T10-012 | T10 | EXISTING_ONBOARDED | `IT-T10-2026-09-20-193259-92e5795fd53fb95f` | SUCCESS | 11.5 | 1 | 1 | SEEN_AGAIN=1 | NAO_SE_APLICA=1 |  |
| IT-T10-013 | T10 | EXISTING_ONBOARDED | `IT-T10-2026-09-20-193310-3ab39d3ab55079e0` | SUCCESS | 12.1 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SE_APLICA=1 |  |
| IT-T10-014 | T10 | EXISTING_ONBOARDED | `IT-T10-2026-09-20-193323-0dc0793e28132e6d` | ROUTE_FAILURE | 24.5 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | indice inacessivel: 503 |
| IT-T10-015 | T10 | EXISTING_ONBOARDED | `IT-T10-2026-09-20-193348-c3850ea3fb2bbf57` | SUCCESS | 18.9 | 1 | 1 | SEEN_AGAIN=1 | NAO_SE_APLICA=1 |  |
| IT-T10-016 | T10 | EXISTING_ONBOARDED | `IT-T10-2026-09-20-193406-ce4313902ce7f8a0` | ROUTE_FAILURE | 9.9 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T10-017 | T10 | YOUTUBE | `IT-T10-2026-09-20-211431-6e543000f0c579f1` | SUCCESS | 172.5 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T10-018 | T10 | NEW_HTML_04A | `IT-T10-2026-09-20-193916-eed8ac88a543c6c8` | SUCCESS | 14.3 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SE_APLICA=1 |  |
| IT-T10-019 | T10 | YOUTUBE | `IT-T10-2026-09-20-211812-3babdf62c9941b36` | SUCCESS | 132.4 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T10-020 | T10 | NEW_HTML_04A | `IT-T10-2026-09-20-193931-9cf1af71c8c52959` | SUCCESS | 18.2 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SE_APLICA=1 |  |
| IT-T10-021 | T10 | NEW_HTML_04A | `IT-T10-2026-09-20-193949-fd0155aa51b02bac` | SUCCESS | 10.3 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SE_APLICA=1 |  |
| IT-T10-022 | T10 | NEW_HTML_04A | `IT-T10-2026-09-20-193959-825e145dd3c5ad40` | SUCCESS | 20.7 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SE_APLICA=1 |  |
| IT-T11-005 | T11 | EXISTING_ONBOARDED | `IT-T11-2026-09-20-193416-a32a1573df372f02` | SUCCESS | 11.6 | 1 | 1 | SEEN_AGAIN=1 | NAO_SE_APLICA=1 |  |
| IT-T11-006 | T11 | YOUTUBE | `IT-T11-2026-09-20-212112-2def310caa927ec4` | SUCCESS | 141.3 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T11-007 | T11 | YOUTUBE | `IT-T11-2026-09-20-212421-98a2f8153561bb2e` | SUCCESS | 128.9 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T12-003 | T12 | EXISTING_ONBOARDED | `IT-T12-2026-09-20-193427-9c7955ad27e6b075` | SUCCESS | 23.0 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T12-004 | T12 | EXISTING_ONBOARDED | `IT-T12-2026-09-20-193451-7781e9732475a4b9` | SUCCESS | 13.4 | 1 | 1 | SEEN_AGAIN=1 | NAO_SE_APLICA=1 |  |
| IT-T12-005 | T12 | EXISTING_ONBOARDED | `IT-T12-2026-09-20-193504-873c2af8b2c30ea2` | SUCCESS | 14.3 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T12-006 | T12 | EXISTING_ONBOARDED | `IT-T12-2026-09-20-193518-be8dd1c3eee2e02e` | SUCCESS | 31.6 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T12-007 | T12 | YOUTUBE | `IT-T12-2026-09-20-212718-027b1c98484eb5db` | SUCCESS | 130.7 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T12-008 | T12 | YOUTUBE | `IT-T12-2026-09-20-213016-74cb11a35bcac6db` | SUCCESS | 145.2 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T12-009 | T12 | NEW_HTML_04A | `IT-T12-2026-09-20-194020-6b4e0b0170a770dd` | SUCCESS | 19.9 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SE_APLICA=1 |  |
| IT-T12-010 | T12 | YOUTUBE | `IT-T12-2026-09-20-213329-ce1143d8fdd408c1` | SUCCESS | 120.2 | 13 | 13 | NEW_DOCUMENT=13 | NAO_SE_APLICA=13 |  |
| IT-T12-011 | T12 | YOUTUBE | `IT-T12-2026-09-20-213618-204fec36f8df6d74` | SUCCESS | 144.1 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T12-012 | T12 | YOUTUBE | `IT-T12-2026-09-20-213929-4de53b036643cc92` | SUCCESS | 122.2 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T12-013 | T12 | NEW_HTML_04A | `IT-T12-2026-09-20-194040-44e86770cded37fb` | SUCCESS | 10.5 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SE_APLICA=1 |  |
| IT-T12-014 | T12 | YOUTUBE | `IT-T12-2026-09-20-214220-11668b73fe94a34c` | SUCCESS | 125.2 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T12-015 | T12 | YOUTUBE | `IT-T12-2026-09-20-214512-631b00b59950219f` | SUCCESS | 120.0 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T12-016 | T12 | YOUTUBE | `IT-T12-2026-09-20-214800-14bd711d6e11e558` | SUCCESS | 155.1 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T2-001 | T2 | EXISTING_HAND | `IT-T2-2026-09-20-190938-7bdaa6931f24d3e1` | SUCCESS | 13.4 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T2-002 | T2 | EXISTING_HAND | `IT-T2-2026-09-20-190951-7f6c58f2c4154617` | SUCCESS | 31.7 | 4 | 4 | SEEN_AGAIN=4 | NAO_SEI=4 |  |
| IT-T2-004 | T2 | EXISTING_HAND | `IT-T2-2026-09-20-191023-ae818916b58ae92b` | SUCCESS | 13.6 | 1 | 1 | SEEN_AGAIN=1 | NAO_SE_APLICA=1 |  |
| IT-T2-006 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-191709-ee11ba28a6ee3d86` | SUCCESS | 11.1 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SE_APLICA=1 |  |
| IT-T2-007 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-191720-fffc269df9127812` | SUCCESS | 28.0 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SE_APLICA=1 |  |
| IT-T2-008 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-191748-54127f65bd58e563` | SUCCESS | 15.1 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SE_APLICA=1 |  |
| IT-T2-009 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-191804-171c387334a865a9` | SUCCESS | 9.8 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T2-010 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-191813-6c145599e540087c` | SUCCESS | 10.1 | 1 | 1 | SEEN_AGAIN=1 | NAO_SE_APLICA=1 |  |
| IT-T2-011 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-191823-c0f415ea0aea1a27` | SUCCESS | 12.5 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T2-012 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-191836-919e3f90602af806` | SUCCESS | 13.1 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SE_APLICA=1 |  |
| IT-T2-013 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-191849-70d5e9e988309dc4` | SUCCESS | 12.5 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SE_APLICA=1 |  |
| IT-T2-014 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-191901-216f97bfbb992658` | SUCCESS | 12.0 | 1 | 1 | SEEN_AGAIN=1 | NAO_SE_APLICA=1 |  |
| IT-T2-015 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-191913-083fce2f9b36d00a` | SUCCESS | 11.8 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T2-016 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-191925-47134303ababe17a` | SUCCESS | 18.0 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T2-017 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-191943-dd3a73f7b3f32397` | SUCCESS | 14.9 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SE_APLICA=1 |  |
| IT-T2-018 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-191958-104d791e1ff0a7d7` | ROUTE_FAILURE | 7.8 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T2-019 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-192006-a06fe19a8aa05635` | SUCCESS | 18.2 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SE_APLICA=1 |  |
| IT-T2-020 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-192025-b5580bb31a33bb29` | SUCCESS | 11.5 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T2-021 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-192035-f2ff213175213475` | ROUTE_FAILURE | 6.4 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T2-022 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-192042-43db4421b595a5c1` | SUCCESS | 12.0 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SE_APLICA=1 |  |
| IT-T2-023 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-192054-428a0fc2bd872d80` | ROUTE_FAILURE | 12.9 | 1 | 0 | TRANSPORT_OR_EMPTY=1 | NAO_SEI=1 | status 404 / 362228 bytes |
| IT-T2-024 | T2 | EXISTING_ONBOARDED | `IT-T2-2026-09-20-192107-cf6ce157affc8110` | SUCCESS | 12.5 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T2-025 | T2 | YOUTUBE | `IT-T2-2026-09-20-194050-455538597dca4500` | SUCCESS | 107.7 | 14 | 14 | NEW_DOCUMENT=14 | NAO_SE_APLICA=14 |  |
| IT-T2-026 | T2 | YOUTUBE | `IT-T2-2026-09-20-194239-4b3bdf2151b93f3c` | SUCCESS | 132.5 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T2-027 | T2 | YOUTUBE | `IT-T2-2026-09-20-194451-2ad93dcd5a479ecc` | SUCCESS | 116.4 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T2-028 | T2 | YOUTUBE | `IT-T2-2026-09-20-194647-78b19842a3d2aab3` | SUCCESS | 135.4 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T2-030 | T2 | NEW_HTML_04A | `IT-T2-2026-09-20-193550-f769be593ed8a5fb` | SUCCESS | 14.7 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SE_APLICA=1 |  |
| IT-T3-002 | T3 | EXISTING_HAND | `IT-T3-2026-09-20-191037-b5e82a9d73b2782e` | SUCCESS | 15.1 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T3-008 | T3 | EXISTING_HAND | `IT-T3-2026-09-20-191052-d2ef01b581d7d551` | SUCCESS | 33.3 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T3-010 | T3 | EXISTING_HAND | `IT-T3-2026-09-20-191125-b882ffecc1f95bbb` | SUCCESS | 19.0 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T3-011 | T3 | EXISTING_HAND | `IT-T3-2026-09-20-191144-2773077f13fae128` | SUCCESS | 29.9 | 3 | 1 | IDENTITY_FAILED=2 SEEN_AGAIN=1 | NAO_SEI=3 |  |
| IT-T3-013 | T3 | EXISTING_ONBOARDED | `IT-T3-2026-09-20-192119-8aa08a635041f2b8` | SUCCESS | 13.8 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO=1 |  |
| IT-T3-014 | T3 | EXISTING_ONBOARDED | `IT-T3-2026-09-20-192133-dce004acfbdd6a1f` | SUCCESS | 17.7 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO=1 |  |
| IT-T3-015 | T3 | EXISTING_ONBOARDED | `IT-T3-2026-09-20-192151-fd4d599532c61de6` | SUCCESS | 13.7 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO=1 |  |
| IT-T3-016 | T3 | EXISTING_ONBOARDED | `IT-T3-2026-09-20-192205-9ef28cde9e906463` | SUCCESS | 14.0 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO=1 |  |
| IT-T3-017 | T3 | EXISTING_ONBOARDED | `IT-T3-2026-09-20-192219-bb11acec8f55fb18` | ROUTE_FAILURE | 6.9 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T3-018 | T3 | EXISTING_ONBOARDED | `IT-T3-2026-09-20-192225-9c8e82d0d6c5a33c` | SUCCESS | 8.8 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T3-019 | T3 | EXISTING_ONBOARDED | `IT-T3-2026-09-20-192234-acb12f3848dacbd3` | SUCCESS | 10.0 | 1 | 1 | SEEN_AGAIN=1 | NAO=1 |  |
| IT-T3-020 | T3 | EXISTING_ONBOARDED | `IT-T3-2026-09-20-192244-c98480cb05ad4fb3` | SUCCESS | 11.8 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T3-021 | T3 | EXISTING_ONBOARDED | `IT-T3-2026-09-20-192256-daac964c52058353` | ROUTE_FAILURE | 7.7 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T4-001 | T4 | EXISTING_HAND | `IT-T4-2026-09-20-191216-de6067c40f5d4097` | SUCCESS | 20.0 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-002 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192304-7a8b6c4fdde51ca6` | ROUTE_FAILURE | 12.2 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T5-006 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192316-0320404b196cf313` | SUCCESS | 10.4 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SEI=1 |  |
| IT-T5-007 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192326-404ba276fec1312e` | SUCCESS | 10.3 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-008 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192337-e58047a9fb30c8ae` | SUCCESS | 13.1 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-009 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192350-8c9ead7e399b416a` | SUCCESS | 11.1 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-010 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192401-aa7b83aa0341733c` | SUCCESS | 14.7 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-011 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192416-4ac43a25dc96719b` | SUCCESS | 10.3 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-012 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192426-7b68be5ac851ce57` | SUCCESS | 14.5 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-013 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192441-7d2927d2fb50c66d` | SUCCESS | 14.0 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-014 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192455-af7a674717b940a9` | SUCCESS | 13.7 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-015 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192508-6a134eecf66c22a3` | SUCCESS | 12.8 | 1 | 1 | SEEN_AGAIN=1 | SIM=1 |  |
| IT-T5-016 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192521-499d7f627375a5c1` | SUCCESS | 10.8 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-017 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192532-9aac8c847b3a9086` | SUCCESS | 13.1 | 1 | 1 | SEEN_AGAIN=1 | SIM=1 |  |
| IT-T5-018 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192545-fb7dc64d6d3e53c1` | SUCCESS | 10.7 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-019 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192556-28f6660efb053984` | SUCCESS | 13.3 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-020 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192609-0b9eb8a12e27b822` | SUCCESS | 10.9 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-021 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192620-6b5325f61adff675` | ROUTE_FAILURE | 8.2 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PA |
| IT-T5-022 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192628-bdc09f811878fd5c` | SUCCESS | 10.9 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-023 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192639-811c2a9f1ddf5820` | SUCCESS | 14.1 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-024 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192653-3059d44865de3771` | SUCCESS | 14.3 | 1 | 1 | SEEN_AGAIN=1 | SIM=1 |  |
| IT-T5-025 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192708-c824dabebd7f3b61` | SUCCESS | 13.6 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | SIM=1 |  |
| IT-T5-026 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192721-3c4f821504d60c1b` | SUCCESS | 12.9 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-027 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192734-8b9ef001a8833894` | SUCCESS | 18.4 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | SIM=1 |  |
| IT-T5-028 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192753-50b3827b5360b47a` | SUCCESS | 14.3 | 1 | 1 | SEEN_AGAIN=1 | SIM=1 |  |
| IT-T5-029 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192807-5c07ae2b2063e408` | SUCCESS | 12.8 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T5-030 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192820-3218c890fbdc53ea` | SUCCESS | 15.5 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | SIM=1 |  |
| IT-T5-032 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192835-071795834987ba7b` | SOURCE_FAILURE_SEM_OBS | 7.3 | 0 | 0 |  | — |  |
| IT-T5-033 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192843-147a52f842d703b2` | SUCCESS | 12.2 | 1 | 1 | SEEN_AGAIN=1 | SIM=1 |  |
| IT-T5-034 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192855-65f932fb8ca2d940` | SUCCESS | 11.1 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | SIM=1 |  |
| IT-T5-035 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192906-7ab07ae1f5ec1c43` | SUCCESS | 12.8 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | SIM=1 |  |
| IT-T5-036 | T5 | EXISTING_ONBOARDED | `IT-T5-2026-09-20-192919-8e956ede5a0f00ca` | SUCCESS | 13.2 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | SIM=1 |  |
| IT-T5-037 | T5 | YOUTUBE | `IT-T5-2026-09-20-194902-0fa02d374fbc43c5` | SUCCESS | 118.3 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |
| IT-T5-038 | T5 | YOUTUBE | `IT-T5-2026-09-20-195101-91178695d8875e2c` | SUCCESS | 137.6 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |
| IT-T5-039 | T5 | NEW_HTML_04A | `IT-T5-2026-09-20-193605-e847862f7bea0834` | SUCCESS | 26.9 | 1 | 1 | NEW_DOCUMENT=1 | SIM=1 |  |
| IT-T5-040 | T5 | YOUTUBE | `IT-T5-2026-09-20-195319-8652f3bb627e2469` | SUCCESS | 131.2 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |
| IT-T5-042 | T5 | YOUTUBE | `IT-T5-2026-09-20-195530-9770fdf3cba4d5da` | POLICY_BLOCK | 57.1 | 15 | 0 | TRANSPORT_OR_EMPTY=15 | NAO_SEI=15 | status 429 / 3404 bytes |
| IT-T5-043 | T5 | YOUTUBE | `IT-T5-2026-09-20-195627-f961b7ed09315bc7` | POLICY_BLOCK | 68.3 | 15 | 0 | TRANSPORT_OR_EMPTY=15 | NAO_SEI=15 | status 429 / 3404 bytes |
| IT-T5-044 | T5 | YOUTUBE | `IT-T5-2026-09-20-195735-0644a2bd0c35f9b8` | POLICY_BLOCK | 61.6 | 15 | 0 | TRANSPORT_OR_EMPTY=15 | NAO_SEI=15 | status 429 / 3404 bytes |
| IT-T5-045 | T5 | YOUTUBE | `IT-T5-2026-09-20-195837-f9e1ba7d6ff68ecb` | POLICY_BLOCK | 56.6 | 15 | 0 | TRANSPORT_OR_EMPTY=15 | NAO_SEI=15 | status 429 / 3404 bytes |
| IT-T5-047 | T5 | YOUTUBE | `IT-T5-2026-09-20-195933-0c5477e1e6494134` | POLICY_BLOCK | 55.5 | 15 | 0 | TRANSPORT_OR_EMPTY=15 | NAO_SEI=15 | status 429 / 3404 bytes |
| IT-T5-048 | T5 | YOUTUBE | `IT-T5-2026-09-20-200029-12fe5c5c474248fb` | POLICY_BLOCK | 59.0 | 15 | 0 | TRANSPORT_OR_EMPTY=15 | NAO_SEI=15 | status 429 / 3404 bytes |
| IT-T5-049 | T5 | NEW_HTML_04A | `IT-T5-2026-09-20-193632-9cea5353f98faba7` | SUCCESS | 15.6 | 1 | 1 | NEW_DOCUMENT=1 | SIM=1 |  |
| IT-T5-050 | T5 | YOUTUBE | `IT-T5-2026-09-20-200128-8d51dada77872f6a` | POLICY_BLOCK | 57.1 | 15 | 0 | TRANSPORT_OR_EMPTY=15 | NAO_SEI=15 | status 429 / 3404 bytes |
| IT-T7-013 | T7 | EXISTING_ONBOARDED | `IT-T7-2026-09-20-192932-34df68b28dff931e` | SUCCESS | 13.3 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | SIM=1 |  |
| IT-T7-014 | T7 | EXISTING_ONBOARDED | `IT-T7-2026-09-20-192945-702930783744b5b0` | ROUTE_FAILURE | 49.2 | 1 | 0 | DISCOVERY_FAILED=1 | NAO_SEI=1 | indice inacessivel: curl: (35) Recv failure: Connection was reset
 |
| IT-T7-015 | T7 | YOUTUBE | `IT-T7-2026-09-20-190507-1de3b5b72cb820f7` | SUCCESS | 189.1 | 15 | 15 | NEW_DOCUMENT=15 | NAO=2 NAO_SEI=13 |  |
| IT-T7-016 | T7 | YOUTUBE | `IT-T7-2026-09-20-200225-04b77de9788a8abe` | POLICY_BLOCK | 63.1 | 15 | 0 | TRANSPORT_OR_EMPTY=15 | NAO_SEI=15 | status 429 / 3404 bytes |
| IT-T7-017 | T7 | NEW_HTML_04A | `IT-T7-2026-09-20-193647-ade12313c500b54c` | SUCCESS | 21.0 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SEI=1 |  |
| IT-T7-018 | T7 | YOUTUBE | `IT-T7-2026-09-20-200328-07eebfb4476f94f1` | POLICY_BLOCK | 31.2 | 5 | 0 | TRANSPORT_OR_EMPTY=5 | NAO_SEI=5 | status 429 / 3404 bytes |
| IT-T7-020 | T7 | YOUTUBE | `IT-T7-2026-09-20-201606-ad0f226a13a6ec9b` | SUCCESS | 111.9 | 15 | 15 | NEW_DOCUMENT=15 | NAO=1 NAO_SEI=14 |  |
| IT-T7-021 | T7 | NEW_HTML_04A | `IT-T7-2026-09-20-193708-d8b65797a6a744b2` | SUCCESS | 21.1 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SEI=1 |  |
| IT-T7-022 | T7 | YOUTUBE | `IT-T7-2026-09-20-201845-ae18ccdc43c848ff` | SUCCESS | 118.9 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |
| IT-T7-023 | T7 | YOUTUBE | `IT-T7-2026-09-20-202132-f3bc4f423daf6680` | SUCCESS | 118.6 | 15 | 15 | NEW_DOCUMENT=15 | NAO=2 NAO_SEI=13 |  |
| IT-T7-024 | T7 | YOUTUBE | `IT-T7-2026-09-20-202419-42827795e818506f` | SUCCESS | 118.3 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |
| IT-T7-025 | T7 | YOUTUBE | `IT-T7-2026-09-20-202705-897c05bd82c11e5b` | SUCCESS | 115.4 | 15 | 15 | NEW_DOCUMENT=15 | NAO=1 NAO_SEI=14 |  |
| IT-T7-026 | T7 | YOUTUBE | `IT-T7-2026-09-20-202948-362bb576cb62f7dc` | SUCCESS | 117.2 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |
| IT-T7-027 | T7 | YOUTUBE | `IT-T7-2026-09-20-203233-e7bd976820f7fcb1` | SUCCESS | 111.8 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |
| IT-T7-028 | T7 | YOUTUBE | `IT-T7-2026-09-20-203512-ad25fe78f26d1882` | SUCCESS | 126.6 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |
| IT-T7-030 | T7 | YOUTUBE | `IT-T7-2026-09-20-203807-132a21d388680511` | SUCCESS | 123.3 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |
| IT-T7-031 | T7 | NEW_HTML_04A | `IT-T7-2026-09-20-193729-ff9505dfaa9a4440` | SUCCESS | 16.3 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SEI=1 |  |
| IT-T7-032 | T7 | YOUTUBE | `IT-T7-2026-09-20-204058-6b8e21d082e8a8cd` | SUCCESS | 124.4 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |
| IT-T7-033 | T7 | NEW_HTML_04A | `IT-T7-2026-09-20-193746-81a5352c4a43f429` | SUCCESS | 12.0 | 1 | 1 | NEW_DOCUMENT=1 | SIM=1 |  |
| IT-T7-034 | T7 | YOUTUBE | `IT-T7-2026-09-20-204351-a57d6bfb92beea10` | SUCCESS | 126.2 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |
| IT-T7-035 | T7 | YOUTUBE | `IT-T7-2026-09-20-204645-5a50f69c53304327` | SUCCESS | 124.4 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |
| IT-T7-036 | T7 | YOUTUBE | `IT-T7-2026-09-20-204937-e9161b0eee2a5513` | SUCCESS | 125.2 | 15 | 15 | NEW_DOCUMENT=15 | NAO=1 NAO_SEI=14 |  |
| IT-T7-037 | T7 | YOUTUBE | `IT-T7-2026-09-20-205230-4883daad4d79429c` | SUCCESS | 113.8 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |
| IT-T7-039 | T7 | YOUTUBE | `IT-T7-2026-09-20-205511-1922b5256d09507d` | SUCCESS | 110.2 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |
| IT-T7-040 | T7 | NEW_HTML_04A | `IT-T7-2026-09-20-193757-404268163998839b` | SUCCESS | 28.9 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SEI=1 |  |
| IT-T7-041 | T7 | NEW_HTML_04A | `IT-T7-2026-09-20-193826-d16655f6c9c2f725` | SUCCESS | 11.1 | 1 | 1 | NEW_DOCUMENT=1 | SIM=1 |  |
| IT-T7-042 | T7 | NEW_HTML_04A | `IT-T7-2026-09-20-193837-9c12a69ffa7162d6` | SUCCESS | 14.4 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SEI=1 |  |
| IT-T7-043 | T7 | NEW_HTML_04A | `IT-T7-2026-09-20-193852-59f1dd4db82985d2` | SUCCESS | 12.3 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SEI=1 |  |
| IT-T8-004 | T8 | YOUTUBE | `IT-T8-2026-09-20-205750-cab276717c694c6d` | SUCCESS | 111.0 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T8-005 | T8 | YOUTUBE | `IT-T8-2026-09-20-210029-0ba57a1f33613529` | SUCCESS | 113.8 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T8-006 | T8 | YOUTUBE | `IT-T8-2026-09-20-210310-d5c601178eef434c` | SUCCESS | 123.9 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SE_APLICA=15 |  |
| IT-T8-008 | T8 | NEW_HTML_04A | `IT-T8-2026-09-20-193904-6d7a31f62f27260f` | SUCCESS | 12.1 | 1 | 1 | NEW_DOCUMENT=1 | NAO_SE_APLICA=1 |  |
| IT-T9-009 | T9 | EXISTING_ONBOARDED | `IT-T9-2026-09-20-193035-161d1a1a177ee9c5` | SUCCESS | 14.0 | 1 | 1 | DOCUMENT_CHANGED_IN_PLACE=1 | NAO_SEI=1 |  |
| IT-T9-010 | T9 | EXISTING_ONBOARDED | `IT-T9-2026-09-20-193048-12807feada3eb0ff` | SUCCESS | 10.0 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T9-011 | T9 | EXISTING_ONBOARDED | `IT-T9-2026-09-20-193058-ff56ab6f5e532dc1` | SUCCESS | 11.7 | 1 | 1 | SEEN_AGAIN=1 | SIM=1 |  |
| IT-T9-012 | T9 | EXISTING_ONBOARDED | `IT-T9-2026-09-20-193111-907ccf99fecc664f` | SUCCESS | 19.2 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T9-013 | T9 | EXISTING_ONBOARDED | `IT-T9-2026-09-20-193129-ceb8737f50fc7b23` | SUCCESS | 12.4 | 1 | 1 | SEEN_AGAIN=1 | NAO_SEI=1 |  |
| IT-T9-014 | T9 | YOUTUBE | `IT-T9-2026-09-20-210602-f4c184c1659f2066` | SUCCESS | 115.8 | 15 | 15 | NEW_DOCUMENT=15 | NAO=3 NAO_SEI=12 |  |
| IT-T9-016 | T9 | YOUTUBE | `IT-T9-2026-09-20-210845-b9b4bc920d4423bf` | SUCCESS | 115.7 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |
| IT-T9-017 | T9 | YOUTUBE | `IT-T9-2026-09-20-211129-0fdf5d1554aa9631` | SUCCESS | 133.9 | 15 | 15 | NEW_DOCUMENT=15 | NAO_SEI=15 |  |

---

## 7 · ADMISSION + SALA — medido no banco e no Livro

**Onde cada número vive.** A rota italiana **não escreve linha `ADMISSION` em
`etapa_da_corrida`** (`ETAPA_ADMISSION_ROWS_IT = 0`; as 6 que existem são da rota ES de
18/09). `SIM` mede-se na Sala (`sala_de_espera.pousado_em` na janela); `NAO`, `NAO_SEI`
e `NAO_SE_APLICA` medem-se em `data/samples/LIVRO-DE-DECISOES.json` (campo `corrida` ∈
os 181 RUN_ID). Os dois batem: 17 `SIM` no Livro = 17 itens novos na Sala.

```
RAW_OBSERVATIONS   = 872   (banco: raw_asset criados na janela; 872 preservados, 0 não preservados; 180 fontes distintas)
                     text/html 679 · application/json 147 (observações de falha) · application/pdf 45 · text/csv 1
                     BYTES_COLLECTED = 834.940.787   STORAGE_OBJECTS 815 novos + 57 reutilizados
                     bytes no armazém operacional conferidos por sha256: 815/815 novos + 57/57 reutilizados, 0 em falta
DERIVED_CREATED    = 668   (TEXT_EXTRACTION)     DERIVED_REUSED = 18
DERIVED_FAILED     = 34 etapas / 37 erros  — todas STORAGE_MISSING («a ficha está no banco e o artefato não está no armazém»),
                     em 34 fontes já vistas na BC2 (SEEN_AGAIN); mecanismo NÃO SEI — ver §9 B3
DERIVED_NOT_APPLICABLE = 30 etapas  (DERIVACAO_ESPECIE_NAO_SUPORTADA: JSON de observação, CSV) — NOT_APPLICABLE ≠ FAIL

ADMISSION (Livro, 872 decisões = 1 por observação):
  ADMISSION_SIM = 17   ADMISSION_NAO = 15   ADMISSION_NAO_SEI = 518   ADMISSION_NAO_SE_APLICA = 322   ADMISSION_ERRO = 0

SALA_BEFORE = 29   SALA_AFTER = 46   SALA_DELTA = 17   (estágio DOCUMENTO 17; universos T5 13 · T7 3 · T9 1)
```

| universo | SIM | NAO | NAO_SEI | NAO_SE_APLICA | ERRO | total |
|---|---:|---:|---:|---:|---:|---:|
| T1 | 0 | 0 | 9 | 13 | 0 | 22 |
| T2 | 0 | 0 | 14 | 71 | 0 | 85 |
| T3 | 0 | 5 | 10 | 0 | 0 | 15 |
| T4 | 0 | 0 | 1 | 0 | 0 | 1 |
| T5 | 13 | 0 | 169 | 0 | 0 | 182 |
| T7 | 3 | 7 | 260 | 0 | 0 | 270 |
| T8 | 0 | 0 | 0 | 46 | 0 | 46 |
| T9 | 1 | 3 | 46 | 0 | 0 | 50 |
| T10 | 0 | 0 | 6 | 40 | 0 | 46 |
| T11 | 0 | 0 | 0 | 31 | 0 | 31 |
| T12 | 0 | 0 | 3 | 121 | 0 | 124 |
| **total** | 17 | 15 | 518 | 322 | 0 | 872 |

| resultado | motivo (Livro) | n |
|---|---|---:|
| NAO_SEI | nao encontrei nada de «T7» — nem de nenhum outro universo. Isso NAO prova que o  | 204 |
| NAO_SEI | o item veio sem texto nenhum. Sem conteudo nao da para dizer se serve — e «nao c | 186 |
| NAO_SEI | nao encontrei nada de «T5» — nem de nenhum outro universo. Isso NAO prova que o  | 46 |
| NAO_SEI | nao encontrei nada de «T9» — nem de nenhum outro universo. Isso NAO prova que o  | 39 |
| NAO_SEI | so uma palavra de «T7» aparece (consorzio), e uma palavra solta pode ser acident | 24 |
| NAO_SEI | so uma palavra de «T7» aparece (agronomi), e uma palavra solta pode ser acidente | 7 |
| NAO | nao fala de «T7», e fala claramente de outro universo (T9: lancio). Isto e um NA | 3 |
| NAO_SEI | so uma palavra de «T7» aparece (soci), e uma palavra solta pode ser acidente de  | 3 |
| NAO | nao fala de «T3», e fala claramente de outro universo (T5: ricerca, universita;  | 2 |
| NAO_SEI | so uma palavra de «T9» aparece (novita), e uma palavra solta pode ser acidente d | 2 |
| NAO | nao fala de «T7», e fala claramente de outro universo (T9: evento). Isto e um NA | 2 |
| NAO | nao fala de «T7», e fala claramente de outro universo (T4: etichetta). Isto e um | 1 |

**`NAO` e `NAO_SEI` não se somam.** Os 15 `NAO` são juízo com prova a favor («fala
claramente de outro universo»). Os 518 `NAO_SEI` dividem-se em dois: «o item veio sem
texto nenhum» (≈ as páginas `/watch` do YouTube: a derivação HTML→texto não alcança o
título e a descrição, que vivem no JSON embutido — **a rota do YouTube colhe RAW, ainda
não colhe texto**; é um extractor em falta, §9 B2) e «não encontrei nada de Tn» (texto
sem vocabulário do universo). Os 322 `NAO_SE_APLICA` são universos **sem régua escrita**
(T1, T2, T8, T10, T12): a porta não inventa uma. **A régua não foi tocada.**

**BANCO (54330/sala_italia) — reconciliação e red team.** Qualquer `RT_* ≠ 0` seria
blocker; todos deram 0.

| medida (banco, 54330/sala_italia) | valor |
|---|---|
| `BCR_RUNS` | 180 |
| `BCR_RUNS_CONCLUIDA` | 180 |
| `BCR_RUNS_NAO_CONCLUIDA` | 0 |
| `BCR_RUNS_STATUS` | concluida=180 |
| `RAW_OBSERVATIONS_CREATED` | 872 |
| `RAW_PRESERVED` | 872 |
| `RAW_NOT_PRESERVED` | 0 |
| `RAW_SOURCES_DISTINTAS` | 180 |
| `BYTES_COLLECTED` | 834940787 |
| `STORAGE_OBJECTS_CREATED` | 815 |
| `STORAGE_OBJECTS_REUSED` | 57 |
| `DERIVED_CREATED` | 668 |
| `DERIVED_REUSED_ETAPA` | 18 |
| `DERIVED_FAILED_ETAPA` | 64 |
| `ETAPAS_NA_JANELA` | DERIVED=180 RAW=180 |
| `ETAPA_ADMISSION_ROWS_IT` | 0 |
| `SALA_TOTAL` | 46 |
| `NEW_SALA_ITEMS` | 17 |
| `NEW_SALA_POR_ESTAGIO` | DOCUMENTO=17 |
| `NEW_SALA_POR_UNIVERSO` | T5=13 T7=3 T9=1 |
| `COST_USD_BCR` | 0 |
| `RT_RAW_SEM_RUN` | 0 |
| `RT_RAW_SEM_SOURCE` | 0 |
| `RT_RAW_SEM_STORAGE` | 0 |
| `RT_ZERO_BYTE_RAW` | 0 |
| `RT_WRONG_MEDIA_TYPE` | 0 |
| `RT_SHA_MISMATCH_RAW_STORAGE` | 0 |
| `RT_MISSING_LINEAGE_DERIVED` | 0 |
| `RT_MISSING_LINEAGE_ESTRUTURADO` | 0 |
| `RT_ORPHAN_SALA` | 0 |
| `RT_SALA_IDENTIDADE_FABRICADA` | 0 |
| `RT_SALA_ESTAGIO_FORA` | 0 |
| `RT_SALA_RAW_OBS_NULO` | 0 |
| `RT_SALA_RAW_OBS_SEM_RAW` | 0 |
| `RT_COST_GT_0` | 0 |
| `RT_DUP_RETRY_SALA` | 0 |
| `RT_DUP_RAW_SHA_MESMA_RUN` | 0 |
| `RT_PROCEDENCIA_LUGAR_INFERIDO` | 0 |
| `RT_PROCEDENCIA_TEMPO_INFERIDO` | 0 |
| `RT_CONCLUIDA_COM_ERRO` | 0 |
| `RT_NAO_SEI_IN_SALA` | 0 |
| `RT_SALA_FACT_TIME_NAO_UNKNOWN_SEM_BASIS` | 0 |
| `RT_SALA_FACT_LOCATION_NAO_UNKNOWN_SEM_BASIS` | 0 |

**Lineage de amostra real** (3 itens mais recentes da Sala, `%TEMP%\bcr\lineage.sql`):
`sala_de_espera.raw_observation_id = raw_asset.id` ✅ (335, 339, 341) →
`storage_object.sha256 = raw_asset.sha256` ✅ → `derived_artifact.raw_asset_id = raw_asset.id`
✅ (derived 143, 147, 149; `TEXT_EXTRACTION`). `fact_time`, `fact_time_basis`,
`fact_location`, `fact_location_basis`, `source_location` = `NAO SEI` nos três — **nada
inferido**; `RT_PROCEDENCIA_* = 0`.

Exemplo: `IT-T5-049` (04A) → run `IT-T5-2026-09-20-193632-9cea5353f98faba7` → raw 335
(`a974d5c6…`, 42.128 bytes, `avvisi-esami-e-prove-itinere`) → storage
`XX/it-t5-049/OBSERVATION/a974d5c67774d3f1-…html` (presente no armazém, sha igual) →
derived 143 (7.003 bytes) → Sala `derived:143`, T5, DOCUMENTO, WAITING.

---

## 8 · CUSTO

`PAID_USD = 0`. Nenhuma rota paga existe para estas 181 fontes; nenhuma foi pedida;
`COST_USD_BCR = 0` no banco; `RT_COST_GT_0 = 0` em todo o histórico.

---

## 9 · FORA DO ESCOPO — documentado, não corrigido

| # | BLOCKER | OWNER | MINIMUM_FIX |
|---|---|---|---|
| B1 | `pastaDoDocumento()` (`coleta/italy_pilot_collect.mjs`) só troca `: / \`; um DOCUMENT_ID com `?` (ou `* " < > \|`) dá `mkdir ENOENT` no Windows, e a camada acima devolve «zero itens, sem razão». Mordeu IT-T7-015 (fumo) e **IT-T5-032** (`news-studenti?view=elenco`, LOTE-HTML-ARTIGO, cujo `LINK_PATTERN` admite query string) | colector italiano | alargar a classe a `[:\/\\?*"<>\|]` (a pasta é endereço de disco, não identidade) e fazer o executor escrever `PORQUE_ZERO_COLHEITA` quando o colector rebenta |
| B2 | Página `/watch` derivada dá «item veio sem texto nenhum» → `NAO_SEI`: título/descrição vivem em `ytInitialPlayerResponse` (JSON), fora do alcance da extracção HTML→texto | derivação (capacidade nova) | um derivador para `text/html` de `youtube.com/watch` que extraia título, descrição, canal, data de publicação (`PUBLICATION_TIME`, nunca `FACT_TIME`) |
| B3 | `DERIVED FAIL · STORAGE_MISSING` em 34 corridas de fontes já vistas na BC2 (57 storage objects reutilizados), embora os 57 ficheiros existam no armazém operacional com sha igual (conferido). Mecanismo **NÃO SEI**; hipótese: a derivação lê o objecto reutilizado por outra raiz que não `SINTONIA_ARMAZEM_RAIZ` | derivação / armazém | medir com que raiz a derivação abre um `storage_object` reutilizado; o teste é 1 corrida `--so-a-porta` sobre uma dessas 34 |
| B4 | Universos sem régua: T1, T2, T8, T10, T12 → 322 `NAO_SE_APLICA` | dono da régua de admissão | escrever a régua (decisão do dono, não desta bancada) |
| B5 | `IT-T8-001` (AgroNotizie, canal YouTube) tem contrato à mão sem bloco executável e não está nas 50 do curator; `OUTPUT_TYPE` à mão é `VIDEO_METADATA + PUBLIC_AUDIO` e sem `EXPECTED_SIGNATURE` o colector reprovaria os bytes | dono do contrato IT-T8-001 | uma linha na tabela (mesmo lote) e `EXPECTED_SIGNATURE "<"` no contrato à mão, ou reescrever o `OUTPUT_TYPE` |
| B6 | O orquestrador imprime `ERRO (nao e rejeicao)` com os primeiros 300 caracteres do stderr — nesta máquina é sempre o aviso do Python, que aparece nas 113 corridas SUCCESS da BC2 — e esconde a causa real | orquestrador | filtrar o aviso ou imprimir o fim do stderr; e `FAILED` com `COLHEITA 0` deve exigir `PORQUE_ZERO_COLHEITA` |
| B7 | A rota italiana não escreve etapa `ADMISSION` em `etapa_da_corrida`; `v_saude_da_rota` e o SQL da BC2 (`ADMISSION_SIM = sum(passed)`) leem 0 | orquestrador / persistência | escrever a etapa com `passed/rejected/unknown/not_run` a partir do Livro |
| B8 | `IT-T3-011`: 2 PDFs (`0286_26_Agrios_Broschuere…`, `rahmenvereinbarung-it.pdf`) sem DOCUMENT_ID pelo padrão à mão → `IDENTITY_FAILED` (a fonte colheu os outros) | dono do contrato | rever `IDENTITY.PATTERN` ou declarar os dois como fora do documento-alvo |
| B9 | 20 `ROUTE_FAILURE` (16 `EMPTY_LIST`: IT-T1-004/012/014/015/020/023, IT-T2-018/021, IT-T3-017/021, IT-T5-002/021, IT-T10-002/006/008/016; IT-T10-014 índice 503; IT-T7-014 reset; IT-T1-017 alvo 400; IT-T2-023 alvo 404) | SOURCE CURATOR / dono de cada contrato | rever `LINK_PATTERN`/`INDEX_URL` fonte a fonte — não investigado aqui, por regra |
| B10 | 9 `POLICY_BLOCK` (429 YouTube: IT-T5-042/043/044/045/047/048/050, IT-T7-016/018); e a corrida interrompida de IT-T7-020 (`…200359…`) deixou 10 linhas 429 no ledger do colector sem registo de corrida | operação | uma passagem de repetição só destas 9, com a sonda e a pausa do driver, noutra janela; não feita aqui (uma corrida por fonte) |
| B11 | RAW do colector desta corrida (154 pastas, 725 ficheiros, 834,9 MB) **fora do Git**, movido de `data/collection-store/italy/` para `%USERPROFILE%\sintonia-sala-italia\acervo-coletor-bcr\` (mapa em `data/collection-ledger/italy/pastas-movidas-2026-09-20-bcr.json`), porque um ficheiro não rastreado move a impressão da árvore e não há política de retenção | dono do armazém | política de retenção + `SINTONIA_ARMAZEM_RAIZ` também para o colector (`ITALY_OPS_ROOT` já existe) |
| B12 | 15 páginas `/watch` do fumo entraram num commit por `git add -A` e saíram por `--amend` antes de qualquer push (`7e47d2db → f93ee597`) | — | já desfeito; fica o aviso no §163 |

---

## 10 · TESTES — baseline vs. depois, por NOME

Bateria `py -m unittest discover -s tests -v`, em worktrees descartáveis (a suíte apaga
`XX/` e escreve resíduo — nunca na árvore da coleta), uma de cada vez.

| | baseline @ 96dcd6bd | final @ f93ee597 (código final) |
|---|---|---|
| TESTS_RUN | 4954 | 4954 |
| FAILED (failures + errors) | 230 = 199 + 31 | 231 = 200 + 31 |
| SKIPPED / expected failures | 190 / 1 | 190 / 1 |
| nomes vermelhos distintos | 112 | 113 |
| **NEW_FAILURES por nome** | — | **1**: `test_M5_o_ponto_fixo_existe_e_esta_alcancado_nesta_arvore` |
| sumidos por nome | — | 0 |

O `M5` é o mapa a dizer «esta árvore não é a do mapa commitado»: o commit `f93ee597` nasceu
de um `--amend` que tirou 15 ficheiros RAW do índice **depois** de o mapa ter sido gerado.
É verdadeiro e é esperado; o commit final «mapa: regerado» fecha-o — resultado medido no
bloco de entrega (`M5_NO_FINAL_HEAD`). `regras/italy_contract_test.mjs` 94 `FALHA` antes e
depois; `motor_de_rota_test.mjs` 1/1; `adaptadores_de_aquisicao_test.mjs` 11/11;
`test_integracao_04a_curator` 17/17.

---

## 11 · GATES FINAIS

```
NEW_FAILURES                          = 1 por nome @ f93ee597 (M5, mapa desfasado pelo amend) → medido de novo no FINAL_HEAD
RECONCILIATION_STRUCTURAL_ERRORS      = 0   (RT_* todos 0; 180 corridas concluídas, 0 com erro)
SHA_MISMATCH                          = 0   (raw ↔ storage no banco: 0; ficheiros do armazém: 872/872 sha igual)
TEST_CAN_DELETE_OPERATIONAL_STORAGE   = NO  (suíte corrida só em worktrees descartáveis; armazém operacional 589 MB intacto; XX/ não existe nesta árvore)
SYSTEM_MAP_CHECK                      = PASS @ 0bbd9892; FINAL_HEAD medido no bloco de entrega
```

---

## 12 · BLOCO DE ENTREGA

```
INITIAL_HEAD = 96dcd6bd   FINAL_HEAD = o commit «mapa: regerado…» que se segue (medido na mensagem de entrega)   REMOTE_HEAD = = FINAL_HEAD após push (medido na entrega por rev-parse)   WORKTREE_CLEAN = medido na entrega
COMMITS = fb45dd5d (merge YouTube) · 5920d77d (50 na tabela) · 0bbd9892 (mapa) · f93ee597 (identidade videoId) · o commit deste relatório (relatório + ledger) · o commit «mapa: regerado…» que se segue (medido na mensagem de entrega) (mapa)
HTML_INTEGRATED = 18 (confirmado: 105 → 123 na tabela; nenhuma reaberta)
YOUTUBE_TESTED = 50   YOUTUBE_PASS = 50   YOUTUBE_FAIL = 0   YOUTUBE_READY = 50
READY_EXISTING = 113   READY_NEW = 68 (18 HTML + 50 YouTube)   READY_TOTAL = 181
BIG_COLLECTION_RUN_ID = BCR-2026-09-20 (181 RUN_ID, um por fonte; janela 18:59:34Z → 21:50:35Z)
SOURCES_SELECTED = 181  SOURCES_ATTEMPTED = 181  SOURCES_SUCCESS = 151  SOURCES_FAILED = 30 (ROUTE_FAILURE 20 · POLICY_BLOCK 9 · CAPABILITY_GAP 1)
RAW_OBSERVATIONS = 872 (872 preservadas · 834.940.787 bytes · 815 storage novos + 57 reutilizados · sha conferido 872/872)
DERIVED_CREATED = 668   DERIVED_REUSED = 18   DERIVED_FAILED = 34 etapas / 37 erros (STORAGE_MISSING)   DERIVED_NOT_APPLICABLE = 30
ADMISSION_SIM = 17  ADMISSION_NAO_SEI = 518  ADMISSION_NAO = 15  ADMISSION_NAO_SE_APLICA = 322  ADMISSION_ERRO = 0
SALA_BEFORE = 29   SALA_AFTER = 46   SALA_DELTA = 17
PAID_USD = 0
NEW_FAILURES = 1 por nome @ f93ee597 (M5) · M5_NO_FINAL_HEAD = medido na entrega, no FINAL_HEAD   SYSTEM_MAP_CHECK = medido na entrega, no FINAL_HEAD
MODEL_EFFECTIVE = claude-fable-5-1
KNOW_HOW_DELTA = §163 (máximo anterior §162, varrido em todas as branches locais e remotas com o ficheiro)
RAW_NOVO_NO_COMMIT = 0 (bytes preservados em %USERPROFILE%\sintonia-sala-italia\acervo-coletor-bcr\ e no armazém operacional)
```

**HARD STOP.** Parei depois de Big Collection + Admission + Sala. Não procurei fontes
novas, não mexi em backup (além de um `pg_dump` antes da corrida), não configurei reboot,
não toquei no Source Curator, Facebook, Instagram, LinkedIn, Portal, nem abri arquitetura.

---

## 13 · EM LINGUAGEM SIMPLES

1. **Quantas fontes estavam prontas?** 181. Antes desta missão eram 131 (113 antigas + 18
   sites que entraram na missão anterior). Entraram mais 50: canais do YouTube. A porta
   que estava fechada para eles (o «feed») continua fechada; encontrou-se a porta da
   frente, a página pública do canal, que o próprio YouTube diz que pode ser lida. Isso foi
   conferido ao vivo, canal a canal, 50 em 50.
2. **Quantas realmente coletaram?** 151 de 181. As outras 30: em 20, o site já não mostra
   documentos com a forma que a receita espera (a receita dessas fontes precisa de revisão);
   em 9, o YouTube disse «devagar» (o código 429, que é o site a pedir para abrandar) e nós
   parámos, esperámos 15 minutos, e seguimos mais devagar — sem trocar de endereço para
   fugir ao aviso; e 1 foi um defeito nosso: um `?` no endereço de um documento faz o
   nosso programa não conseguir criar a pasta no Windows. Esse defeito está anotado com
   dono e conserto mínimo; não foi consertado porque não era desta missão.
3. **Quantos documentos entraram?** 872 observações foram guardadas, 834,9 MB, cada uma
   com a sua impressão digital (o sha256, que é como o CPF do ficheiro) conferida no
   armazém. Dessas 872, 668 viraram texto legível pela máquina.
4. **Quantos foram admitidos?** 17. A porta de admissão olhou para as 872 e disse: 17
   «sim», 15 «não» (o texto fala de outro assunto), 518 «não sei» e 322 «não se aplica».
   Os «não sei» são, na maior parte, as páginas do YouTube: trouxemos a página inteira, mas
   o nosso extractor de texto ainda não sabe tirar dela o título e a descrição — é como
   ter trazido o jornal e não saber ler aquele tipo de letra. Os «não se aplica» são
   assuntos (clima, culturas, mercado, política, influenciadores) para os quais ainda não
   há uma régua escrita do que conta — e a porta não inventa régua. Nada disto foi alterado
   para produzir mais «sim».
5. **De 29 para quanto a Sala cresceu?** De 29 para 46: 17 documentos novos (13 de
   ciência, 3 de cooperativas, 1 de concorrentes). Cada um tem a cadeia inteira provada:
   corrida → ficheiro guardado → texto derivado → Sala. Nenhum tem data ou lugar do facto
   inventados — está «não sei» onde é não sei.
6. **Quais famílias continuam bloqueadas?** LinkedIn (6 contas + 1 ficha), Instagram (7
   contas + 1 ficha) e Facebook (17 contas). Nenhuma tem receita de busca; nenhuma foi
   tocada, como a missão manda.
7. **A Collection já está suficientemente operacional para avançarmos mais forte em
   CLAIM/FACT + Intelligence?** Para **trazer e guardar** documentos, sim: 181 fontes com
   receita, uma corrida inteira sem gastar um dólar, e o armazém e o banco batem certo em
   todas as conferências. Para **alimentar** a Intelligence, ainda não com força: só 17 de
   872 chegaram à Sala, porque faltam duas coisas que não são da coleta — um leitor de
   texto para as páginas do YouTube e réguas de admissão para cinco assuntos. Com essas
   duas, o mesmo material já guardado pode ser re-julgado sem voltar à rede. A minha
   leitura: avançar em CLAIM/FACT com o que há na Sala (46) é possível hoje; avançar
   «mais forte» pede primeiro essas duas peças, que são pequenas e estão anotadas com dono.

Dois avisos honestos: o número de «prontas» mede que a casa sabe *chegar* à fonte, não
que a fonte é relevante para a ADAMA — isso decide-se na admissão e no Livro de
Relevância. E 34 corridas de fontes já vistas antes reprovaram na etapa de derivação com
«artefato não está no armazém», embora o ficheiro exista lá com a impressão certa; não
descobri porquê e não escondi — está em §9, B3.
