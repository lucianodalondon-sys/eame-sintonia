# RELATÓRIO — ABRIR A PORTA: CANDIDATAS → SOURCE CURATOR CONTÍNUO (CANDIDATE-FEEDER-V1)

**Base:** `source-curator-supervisor-v1` @ `8bbea01c` · **Bancada:** worktree `candidate-feeder-v1`
**Missão:** [`MISSAO-CANDIDATE-FEEDER-V1.md`](MISSAO-CANDIDATE-FEEDER-V1.md)
**HARD GATE:** `BIG_COLLECTION_ALLOWED = NO` · `SALA_WRITES = 0` · nenhuma promoção a READY fora do gate canónico

Este relatório cresce passo a passo. Cada passo tem a parte medida e, no fim do ficheiro, a parte
em linguagem simples.

---

## PASSO 1 — CONFIRMAR A CADEIA (read-only, sem rede) · 2026-09-21

Corrido em `8bbea01c`, sem escrever, sem enfileirar, sem sair à rede. O único comando fora do
repositório foi `Get-CimInstance Win32_Process`, para medir o processo no sistema operativo.

### 1.1 · A secção 0 da missão, reconfirmada linha a linha

| linha da coordenação | medido | veredito |
|---|---|---|
| `SUPERVISOR_PROCESS_REAL` PID 86172 | 86172 vivo no SO, nascido 02:00:13Z, igual ao lock; worker 69408 vivo, filho dele | BATE |
| `SOURCE_CURATOR_SERVICE` IDLE | `SUPERVISOR-STATE.json` diz **RUNNING**, `WORKER_ALIVE: true`, batimento de 2 em 2 min, 0 tarefas executadas por volta | **DIVERGE NO NOME**: o código só escreve IDLE quando o worker morreu; aqui está vivo a dormir 120 s por volta. Ocioso na prática, RUNNING no estado |
| `QUEUE_DEPTH` 38 (0 elegíveis · 1 BLOCKED · 37 DONE) | 38 · 0 · 1 (`T00010`, `IT-PROVA-RETRY`) · 37 | BATE |
| `CANDIDATES_TOTAL` 241, todas EM_ANALISE, todas IT, 0 URLs repetidas | 241 · 241 · 241 · 0 (e 0 IDs repetidos) | BATE |
| `READY_FOR_COLLECTION` 18 | 18 no livro, 18 no `READY-FOR-COLLECTION-V1` | BATE |

### 1.2 · `CADEIA_CONFIRMADA = SIM`, com duas correções de nome

**(a) O caracterizador não parou a meio.** `caracterizador.py` é biblioteca; quem percorre candidatas é
`amostrar.py`, que só lê as decisões `PROMOTE` de `SOURCE-CURATOR-DECISIONS-V1.json`, e
`consolidar_caracterizacao.py` escreve o ficheiro final. Há um degrau que a secção 0.1 omitiu:

```text
FONTES-CANDIDATAS.json  241
        ▼  correr_lote.py + capturador.py     (missão 02 · universo 172 = 241 − 69 sociais nunca capturadas)
SOURCE-CURATOR-DECISIONS-V1.json  172        PROMOTE 124 · NEEDS_REVIEW 34 · BLOCK 6 · UNKNOWN 6 · ENDPOINT_OF 2
        ▼  amostrar.py                        ← FILTRA PROPOSED_STATE == "PROMOTE"
        ▼  consolidar_caracterizacao.py
SOURCE-CHARACTERIZATION-V1.json  124         124 de 124 PROMOTE — filtro de desenho, não orçamento nem falha
        ▼  emparelhar_com_atlas.py            ← FILTRA ONBOARDING_READY == "YES"
        ▼  atribuir_source_id.py → alimentar_fila.py → supervisor.py → worker.py
```

**(b) O worker sai à rede.** `worker.py` tem 0 imports de rede, mas chama `gate_de_rota.py`
(robots.txt ao vivo) e `canario.py` (abre um documento). `VALIDATE_ROUTE`, `CANARY`, `REVALIDATE`
e `REPAIR` saem à rede; só `BUILD_CONTRACT` é offline. O que está certo: 0 `anthropic`, 0 `api_key`,
0 tokens (`POLITICA-MODELO.json` diz o mesmo).

**`FEEDER_NOVO_NECESSARIO = NÃO.`** A porta existe e tem dono em cada troço. Um feeder que lesse
`FONTES-CANDIDATAS.json` directo saltaria a captura da missão 02 e a caracterização, e criaria uma
segunda verdade.

### 1.3 · A tabela dos 5 baldes

Calculada por [`curadoria/baldes_das_candidatas.py`](curadoria/baldes_das_candidatas.py) →
[`curadoria/CANDIDATE-BUCKETS-V1.json`](curadoria/CANDIDATE-BUCKETS-V1.json). O script reprova se a
soma não der o universo.

| balde | coordenação | medido | nota |
|---|---|---|---|
| `JA_COM_CONTRATO` | 77 | **77** | bate |
| `COM_SOURCE_ID_SEM_CONTRATO` | 7 | **7** | bate no número, **não na leitura** (1.4) |
| `SEM_TERRITORIO` | 13 | **13** | bate; `NÃO SEI` deliberado |
| `CARACTERIZADAS_NAO_READY` | 27 | **27** | 14 Facebook `CAPABILITY_BLOCK` · 11 HTML `NEEDS_MORE_SAMPLING` · 1 YouTube `SEMANTIC_REVIEW_REQUIRED` · 1 READY que já é `IT-T8-001` no Atlas (CAND-0187) |
| `NUNCA_CARACTERIZADAS` | 117 | **117** | SOCIAL 75 (LinkedIn 44 · Instagram 25 · Facebook 6) · HTML 42 (Org 19 · Base 12 · Imprensa 9 · Ciência 2) |

### 1.4 · O que a secção 0.2 não viu

- **As 7 não estão «prontas a entrar hoje».** Têm `SMALL_ADAPTATION_REQUIRED = "SIM — ramo de índice"`.
  Já passaram pela fila em 2026-09-20 22:52Z (`T00023`…`T00029`, `BUILD_CONTRACT`): o worker reprovou
  o contrato por esquema, e às 22:54Z foram **rectificadas para `CAPABILITY_BLOCK`** com dono
  SCRAP ENGINEER. Hoje `alimentar_fila.py` salta-as (`sid in est`) e `worker.etapa_build_contract`
  devolve BLOCK por desenho, com comentário no código a dizer exactamente isto. Enfileirá-las de
  novo prova o bloqueio, não a cadeia. A coordenação verificou e retirou o PASSO 2 como estava escrito.
- **As 42 HTML não são 42 fontes novas.** Por decisão da missão 02: 34 `NEEDS_REVIEW` (33 com «0 links
  com cara de item», 1 HTTP 403 — CAND-0062), 6 `UNKNOWN` por DNS do egresso de Milão (unaprol.it,
  anga.it, coldiretti.it e 3 regionais — `UNKNOWN ≠ morta`), e **2 endpoints de fontes que já existem**
  (CAND-0006 → `IT-T1-008`, CAND-0017 → `IT-T1-012`, COL-LAW-205). Trabalho novo honesto: **40**, e
  33 delas esbarram na mesma capacidade que trava as 7.
- **Os dois READY já divergem.** Este livro tem 18 READY em 85 fontes. Em `f98f234c` o livro tem
  **160 READY + 18 DEGRADED** em 195 fontes. Base comum `606974c3`; 16 commits deste lado, 45 do outro;
  `f98f234c` não tem `supervisor.py`. São dois livros, não duas contagens. O PASSO 7 separa três coisas.
- **As 7 também não têm contrato em `f98f234c`**, nem estão no livro de lá. O PASSO 6 (gate de
  detalhe, que é a capacidade de descer do índice ao item) vem **antes** do PASSO 2. Nova ordem
  aceite pela coordenação.
- **Universo:** esta árvore tem 241. A bancada `source-discovery-v1` (`56d037b3`) já tem 271. Não entra
  nesta missão, por ordem; fica dito para o 241 não parecer a verdade inteira.

### 1.5 · Bloco de entrega do PASSO 1

```text
CADEIA_CONFIRMADA = SIM (diverge em: amostrar.py filtra PROMOTE a montante; worker sai à rede no canário)
FEEDER_NOVO_NECESSARIO = NÃO — duplicaria correr_lote → amostrar → consolidar e criaria segunda verdade

CANDIDATES_TOTAL = 241 (esta árvore; 271 em source-discovery-v1, fora do escopo)
  JA_COM_CONTRATO = 77        COM_SOURCE_ID_SEM_CONTRATO = 7 (todas CAPABILITY_BLOCK no livro)
  CARACTERIZADAS_NAO_READY = 27   SEM_TERRITORIO = 13
  NUNCA_CARACTERIZADAS = 117      destas SOCIAL = 75        HTML = 42 (novas 40; 2 são endpoints)

SUPERVISOR_RUNNING_REAL = SIM (PID 86172 e worker 69408 medidos no SO)
BIG_COLLECTION_RUNS = 0     SALA_WRITES = 0     PAID_USD = 0     SONNET_USED = 0
```

---

## ORDEM REVISTA PELA COORDENAÇÃO (depois do PASSO 1)

O PASSO 2 como estava escrito foi retirado (as 7 não eram elegíveis). O PASSO 6 passou à frente,
porque 7 + 33 = 40 fontes esperam a mesma capacidade — descer do índice ao item — e é isso que
`aquisicao-detalhe-v1` provou. A bancada `source-discovery-v1` (56d037b3) tem um motor de descoberta
e 271 candidatas; **não entra nesta missão**, por ordem.

## PASSO 6 — O GATE DE DETALHE, NO DONO CERTO · commit `06f7cfb4`

Integração semântica, sem merge: as duas árvores divergiram em 61 commits a partir de `606974c3` e
`f98f234c` não tem o supervisor. O que entrou, peça a peça:

| peça | onde | o quê |
|---|---|---|
| o juiz | `curadoria/retrato_html.py` | retrato CAPA ≠ MATÉRIA em Python, **mesmos limiares** do coletor da outra linha (800 caracteres em parágrafos · 35% · 40 por ligação) |
| o gate | `curadoria/canario.py` | o canário HTML abre o item, exige texto (`ITEM_SEM_TEXTO`) e reprova capa (`CAPA_NAO_E_MATERIA`); homepage 200 continua a não bastar |
| a régua | `curadoria/worker.py` | a linha do livro diz por que régua promoveu; `DETAIL_GATE_PASSED` na evidência |
| as rotas | `curadoria/integrar_gate_de_detalhe.py` | dos 21 contratos que a outra linha provou (83385fe7), os 9 do curator entram na tabela deste worker com `ROUTE_PROVENANCE`; os 12 do motor ficam no motor. Recusa se o ANTES não bater; idempotente (2.ª corrida: 0 aplicados, 9 iguais); 77/77 válidos |

**Prova por mutação, à mão:** gate calado ⇒ `test_1` e `test_7` vermelhos; exigência de texto
calada ⇒ `test_3` vermelho; reposto ⇒ 126/126 (eram 109). Erro meu registado: na primeira mutação
repus o ficheiro com `git checkout` e apaguei o gate ainda não commitado; refeito, e a reposição
passou a ser por cópia.

**Dívida:** o `SOURCE_CONTRACT_HASH` guardado nos 77 não se recompõe por nenhuma de três fórmulas
(sem HASH; sem HASH+VERSÃO; sem HASH+VERSÃO+ONBOARDED_BY). É carimbo de escrita, não prova de conteúdo.

## PASSO 7 — OS DOIS READY, E O TERCEIRO · commit `c6da8b60` (+ mapa `18b52d1f`)

`curadoria/ready_split.py` lê a régua na evidência da promoção — nada é reescrito.

```text
antes do PASSO 2 revisto:   READY 18 = LEGACY 18 · CURRENT 0 · 9 LEGACY com contrato alterado
depois:                     READY 16 = LEGACY  9 · CURRENT 7 · 2 LEGACY substituídas
SO_NUM_DOS_LIVROS (f98f234c): nos dois 16 · só aqui 0 · só lá 144   ← não é LEGACY nem CURRENT
```

A régua viaja: `interface_collection` (`READY_RULE` por fonte, `READY_LEGACY`/`READY_CURRENT`
nas métricas), `lotes` (por fonte do lote) e `status_live` (ao lado do `READY_TOTAL`).
Dois defeitos apanhados com teste: a interface publicava `CONTRACT_VERSION = "NAO SEI"` nas 18
(lia `CONTRACT_HASH`; a chave é `SOURCE_CONTRACT_HASH`); e o worker promovia a READY directo de
`CONTRACTED_CANARY_FAILED` — o livro recusa e o worker morria. Nunca aconteceu porque 0 das 18
REVALIDATE tinham passado. Passa agora por `CANARY_PENDING`, com a razão escrita.

## PASSO 2 REVISTO — AS 9 LEGACY COM CONTRATO NOVO SÃO O CANÁRIO DA CADEIA · commit `0b57ee7e`

Egresso medido antes de despachar: `205.147.30.6 · Milan · AS208172 Proton AG` (IT, o mesmo da
caracterização). `remedir()` tirou as 9 de READY (o READY antigo fica no livro) e enfileirou
`VALIDATE_ROUTE`. O supervisor **desta árvore** (PID 92692) correu tudo numa volta:

| etapa | tarefas | resultado |
|---|---|---|
| VALIDATE_ROUTE | 9 | 9 OK (robots ao vivo) |
| CANARY com gate | 9 | 7 PASS (item aberto, `MATERIA_PROVAVEL`) · 2 FAIL |
| FAIL pelo gate | IT-T12-013 Piemonte · IT-T7-041 Bonifica Romagna | o primeiro alvo é página de secção (`CAPA_PROVAVEL`, 482 e 54 ligações) |
| `alimentar_fila.py` sozinho | 4 REVALIDATE | 4× canário reprovou de novo (IT-T7-019, IT-T12-013, IT-T5-052, IT-T7-041) |

```text
PASSO2_ENFILEIRADAS = 9 (+4 pelo alimentar_fila)   PROCESSADAS = 22   OK = 16   RETRY = 0   BLOCKED = 0   FAIL = 6
READY_PROMOTED_WITHOUT_CURRENT_GATE = 0
```

## PASSO 5 — IDEMPOTÊNCIA, PROVADA A ATACAR · commit `0b57ee7e`

Ao vivo, com o supervisor desta árvore, e em `curadoria/test_emparelhar_ataques.py` (9 testes):

| # | ataque | o que aconteceu |
|---|---|---|
| 1 | mesma candidata duas vezes | na corrida: a segunda sai `DUPLICADA_NA_CORRIDA` ligada à primeira; na fila: `enfileirar` idempotente por (SOURCE_ID, TASK_TYPE) aberto |
| 2 | URL que já é contrato | casa. O Atlas do coordinator (185) não tem as 84 do curator; compara-se agora com **262** identidades (Atlas + contratos) |
| 3 | URL inválida | `REJEITADA: URL_INVALIDA`, nunca vira número (falha fechada) |
| 4 | mesma organização, canal diferente | `youtube.com/@x` e `x.it` ficam duas (COL-LAW-034); `@x` e `@xTV` ficam uma |
| 5 | worker morto a meio | 03:29:03 `taskkill`; 5 s depois `WORKER_MORTO` + `WORKER_RELANCADO`; as 3 tarefas restantes correram; a interrompida ficou `IN_PROGRESS` (órfã) |
| 6 | fila vazia | worker morto com 0 elegíveis ⇒ `IDLE`, sem relançar, sem morrer |
| 7 | supervisor reiniciado | `PARAR.flag` ⇒ `STOPPED` limpo; religado ⇒ `ORFAS_RECUPERADAS: 1` (relógio da órfã envelhecido 31 min no ficheiro — injeção de tempo, dita pelo nome), `WORKER_RELANCADO`, órfã terminada |

`CONTROLO_POSITIVO_ATLAS_INTACTO = SIM` (`@AgroNotizie` → `IT-T8-001`, teste 0).
**Idempotência da cadeia a montante:** 2.ª e 3.ª corridas de `emparelhar` + `atribuir` devolvem
as 84 NOVAS byte a byte (`JA_ALOCADA_NESTA_LINHA` pelo CANDIDATE_ID, nunca pela URL). Sem isso,
a segunda corrida "casava" as 84 consigo mesmas e o alocador deixava-as cair.
`curadoria/CANDIDATE-LINEAGE-V1.json`: CANDIDATE_ID → SOURCE_ID → TASK_ID → estado → régua
(241 candidatas · 85 com SOURCE_ID · 25 com tarefa); reprova se um número tiver duas candidatas.

## PASSO 8 — GATILHO DE FILA BAIXA · commit `2cb5c477`

`curadoria/nivel_da_fila.py`: backlog = HTML nunca caracterizadas e novas (40) + `NEEDS_MORE_SAMPLING`
(11) = **51**; sociais, bloqueadas e sem território ficam fora porque não são trabalho de ninguém aqui.
`CANDIDATE_LOW_WATERMARK = 20` (uma leva de reserva; escolha com razão escrita).
`DISCOVERY_SIGNAL = DISCOVERY_NOT_NEEDED`, escrito a cada volta em `DISCOVERY-SIGNAL-V1.json`,
apontando o produtor que existe em `source-discovery-v1`. Nenhum motor de descoberta aqui.

## PASSO 9 — O PAINEL PERGUNTA AO SO · commit `2cb5c477`

`supervisor.ler_estado_servico()` mede worker **e** supervisor (PID existe · é Python · batimento
fresco) e distingue `RUNNING · IDLE · STOPPED_FINISHED · STOPPED_BROKEN · BLOCKED · UNKNOWN`,
com `SERVICE_STATE_IN_FILE` visível. Medido: a suíte de testes deixa nesta árvore um
`SUPERVISOR-STATE.json` com `RUNNING` e um PID morto — o painel antigo diria RUNNING; o novo diz
`STOPPED_BROKEN`. Na outra bancada: `IDLE`, supervisor 86172 vivo, sem worker. 7 testes.

## PASSO 4 — LLM

```text
DETERMINISTIC_RESOLVED = todas as etapas    NEEDS_LLM = 0    SONNET_USED = 0    OPUS_ESCALATIONS = 0
LLM_JUSTIFICADO = 0 — nenhuma decisão exigiu semântica que o código não resolvesse: retrato por
contagem, gate por limiar, identidade por chave, rota por listagem contada. O único caso semântico
da cadeia (identidade da ficha ≠ conteúdo, Valagro/Syngenta) já tem estado próprio,
SEMANTIC_REVIEW_REQUIRED, e sobe a humano, não a modelo.
```

## PASSO 3 — DESTRAVAR AS 42 HTML: PROVAR A LISTAGEM

**Porque o caracterizador parou nas 124:** não parou. Leu 124 de 124 PROMOTE. As 117 nunca lhe
chegaram porque a captura da missão 02 não as promoveu (33 com «0 links com cara de item», 1 HTTP
403, 6 DNS, 2 endpoints) ou nunca as capturou (69 sociais). Medido, não suposto (§1.2).

**A capacidade que faltava** é a mesma para as 7 e as 33: descer do índice ao item.
`curadoria/provar_listagem.py` faz isso por fonte, contra a rede, determinístico: robots pela porta
da casa → GET à entrada pela mesma identidade do canário → até 2 secções com vocabulário de notícia
→ contar itens debaixo da secção → abrir **o mesmo item que o canário vai abrir** (ordem alfabética)
e retratá-lo. Cadência 1 s, no máximo 4 pedidos por fonte, controlo positivo primeiro (Chianti
Classico, 15 itens, `MATERIA_PROVAVEL`; à primeira reprovou porque eu abria o item pela ordem do HTML,
um hub, e o canário abre por ordem alfabética; julgar outro item é provar outra coisa).

Duas passadas (a segunda com localizador de secções mais largo e o BOM UTF-8 tratado: o BOM
reprovava como «não é HTML», também no canário; corrigido nos dois com teste):

```text
FONTES_JULGADAS   47 = 7 (com SOURCE_ID) + 40 (HTML nunca caracterizadas, sem os 2 endpoints)
PEDIDOS_TOTAL     99   (58 + 41)   EGRESSO 205.147.30.6 Milano IT (Proton)
PROVADA           12 = 4 das 7 + 8 das 40
NAO_SEI           25   (200 na entrada e nas secções; nenhuma lista 2+ itens com cara de item)
ROBOTS_BLOCK       4   (CAND-0062, 0169, 0144, 0146: Disallow lido ao vivo; registado, não contornado)
ROBOTS_UNREADABLE  5   (coldiretti.it + 3 regionais, unaprol.it: o mesmo DNS de Milão da missão 02)
UNREACHABLE        1   (anga.it, WinError 10054)
```

**As 7, reavaliadas depois do gate** (a coordenação pediu: se continuarem bloqueadas, dizê-lo):

| SOURCE_ID | fonte | listagem provada | canário com gate | estado no livro |
|---|---|---|---|---|
| IT-T5-041 | CRPV | `/it/news/` · 6 itens | PASS | **READY_CURRENT** |
| IT-T5-051 | UNIRC Agraria | entrada · 62 itens | PASS | **READY_CURRENT** |
| IT-T9-015 | Conserve Italia | entrada · 2 itens | PASS | **READY_CURRENT** |
| IT-T9-019 | SCAM | entrada · 19 itens | PASS | **READY_CURRENT** |
| IT-T7-038 | Valpolicella | nenhuma | não corrido | CAPABILITY_BLOCK (continua) |
| IT-T5-054 | Legacoop Agroalimentare | nenhuma | não corrido | CAPABILITY_BLOCK (continua) |
| IT-T9-020 | Sipcam Italia | nenhuma | não corrido | CAPABILITY_BLOCK (continua) |

As 4 ganharam contrato pelo molde da casa com a rota provada (`ROUTE_PROVENANCE` aponta o provador),
entraram como `CANARY_PENDING`, e o worker desta árvore validou a rota e correu o canário com o gate:
8 tarefas, 8 OK. **Nenhuma promoção fora do gate canónico.**

**As 8 das 40 sem SOURCE_ID** (unibz, italiafruit, agricolturamoderna, noisiamoagricoltura, UIV,
Brunello, Piave, Vinitaly) têm listagem provada em `LISTAGENS-PROVADAS-V1.json`, mas não têm
caracterização nem número. Dar-lhes número exige passar pela captura, caracterização e Atlas, a
cadeia existente, com a listagem provada como entrada. **Não feito aqui**: é a recaptura da missão 02
com outra entrada, e fica registada como próximo passo, não escondida num atalho.

```text
PASSO3_CARACTERIZADAS_NOVAS = 0 (pela cadeia canónica; 12 listagens provadas prontas a alimentá-la)
NAO_SEI = 25    403/POLICY = 4 ROBOTS_BLOCK + 0 HTTP 403 nesta identidade    UNKNOWN = 6 (5 robots ilegível + 1 transporte)
```

---

## 3 · BLOCO DE ENTREGA

```text
INITIAL_HEAD = 8bbea01c            FINAL_HEAD = o commit deste relatório (git log)
REMOTE_HEAD = igual ao FINAL_HEAD depois do push (git log)        WORKTREE_CLEAN = SIM depois do commit

CADEIA_CONFIRMADA = SIM. Diverge em dois nomes: amostrar.py filtra PROMOTE a montante (o caracterizador
                    leu 124 de 124); o worker sai à rede no canário e no robots (não no BUILD_CONTRACT)
FEEDER_NOVO_NECESSARIO = NÃO. Duplicaria correr_lote, amostrar e consolidar e criaria segunda verdade

CANDIDATES_TOTAL = 241 (esta árvore; 271 em source-discovery-v1, fora do escopo)
  JA_COM_CONTRATO = 81 (era 77)   COM_SOURCE_ID_SEM_CONTRATO = 3 (era 7; todas CAPABILITY_BLOCK)
  CARACTERIZADAS_NAO_READY = 27   SEM_TERRITORIO = 13
  NUNCA_CARACTERIZADAS = 117      destas SOCIAL = 75        HTML = 42 (novas 40; 2 endpoints)

PASSO2_ENFILEIRADAS = 9 (+4 do alimentar_fila, +4 do PASSO 3)   PROCESSADAS = 30   OK = 24   RETRY = 0   BLOCKED = 0   FAIL = 6
PASSO3_CARACTERIZADAS_NOVAS = 0   LISTAGENS_PROVADAS = 12/47   NAO_SEI = 25   403/POLICY = 4   UNKNOWN = 6

DETERMINISTIC_RESOLVED = todas   NEEDS_LLM = 0   SONNET_USED = 0   OPUS_ESCALATIONS = 0
LLM_JUSTIFICADO = 0. Retrato por contagem, gate por limiar, identidade por chave, rota por listagem contada

DEDUP_PROVEN = 7/7 pelo nome (1 duplicada na corrida e fila idempotente · 2 URL que já é contrato casa ·
               3 URL inválida REJEITADA · 4 canal diferente de site · 5 worker morto ao vivo, RELANCADO e
               órfã recuperada · 6 fila vazia, IDLE · 7 PARAR.flag, STOPPED, religado recupera) e cadeia
               a montante idempotente (84 NOVAS byte a byte em 3 corridas)
CONTROLO_POSITIVO_ATLAS_INTACTO = SIM (@AgroNotizie casa IT-T8-001, teste 0)
DETAIL_GATE_INTEGRATED = SIM (retrato_html.py, canario.py, worker.py; 9 contratos corrigidos; mutação à mão)
READY_LEGACY = 9   READY_CURRENT = 11   (READY_TOTAL 20; 2 LEGACY substituídas; 144 só no livro de f98f234c)
READY_PROMOTED_WITHOUT_CURRENT_GATE = 0

SUPERVISOR_RUNNING_REAL = SIM. Outra bancada: PID 86172 vivo (IDLE). Esta bancada: correu (PID 92692, depois 103252) e foi parada limpa
CONTINUOUS_LOOP_PROVEN = SIM (matar worker: RELANCADO em 5 s; fila vazia: IDLE; reinício: ORFAS_RECUPERADAS 1)
CANDIDATE_LOW_WATERMARK = 20   CANDIDATE_BACKLOG = 51   DISCOVERY_NEEDED_EMITIDO = NÃO (DISCOVERY_NOT_NEEDED, escrito)

BIG_COLLECTION_RUNS = 0        SALA_WRITES = 0        PAID_USD = 0
NEW_FAILURES = 0 em curadoria/ (base 109 OK; agora 154 OK). tests/ da raiz NÃO corrido: a suíte apaga XX/ e
               chega vermelha na base (memória do projeto); não é medida desta missão.
SYSTEM_MAP_CHECK = PASS em cada commit (cadeia canónica correr_a_cadeia.py); carimbo IGUAL no HEAD
KNOW_HOW_DELTA = §159 «A porta existia: o que secou foi a fila a montante»
```

**Dívidas registadas, pelo nome:** hash dos 77 contratos não se recompõe (carimbo, não prova) · a suíte
deixa `SUPERVISOR-STATE.json` na árvore com RUNNING e PID morto · CLAUDE.md e AGENTS.md mandam
`generate + validate`, e o gerador não varre: o executor é `correr_a_cadeia.py REGERAR` · o canário da
outra linha bate à porta com outra identidade (`SintoniaScrap` contra navegador) · 8 listagens provadas
sem número esperam a recaptura pela cadeia · 3 CAPABILITY_BLOCK continuam · 75 sociais fora, com dono próprio.

---

## 4 · EM LINGUAGEM SIMPLES

**1. Porque é que as candidatas estavam paradas, e quantas estavam mesmo?**
Não estavam 241 paradas. 77 já tinham sido tratadas. O que estava parado de verdade eram 40 sites
que a máquina nunca chegou a ler, mais 7 que já tinham número mas cujo site não mostra as notícias na
primeira página. A leitura tinha um filtro um degrau acima, que só deixava passar o que a primeira
sonda tinha aprovado; ninguém tinha mandado ler o resto. Isso ainda não conta 75 redes sociais, que
ficaram de fora de propósito.

**2. A porta já existia ou foi preciso abri-la?**
Já existia, inteira, com um dono em cada troço. Construir uma porta nova seria ter duas verdades. O
que faltava era trabalho a chegar à porta. Foi isso que se fez.

**3. Quantas o canário processou, e no que deram?**
O Bot desta bancada processou 30 tarefas. 24 correram bem e 6 reprovaram. Das 9 fontes cuja rota foi
corrigida, 7 abriram uma notícia a sério; 2 abriram uma página de secção e foram reprovadas por isso.
Das 7 que a coordenação achava prontas, 4 entraram (CRPV, UNIRC, Conserve Italia, SCAM) e 3 continuam
travadas, porque o site delas não lista as notícias em nenhuma secção que se encontre sozinho.
Isto ainda não foi medido com outra abordagem, portanto não sei se essas 3 têm listagem escondida.

**4. Alguma precisou de inteligência artificial? Porquê?**
Nenhuma. Zero gasto. Tudo foi feito a contar: contar ligações, contar parágrafos, comparar endereços,
contar notícias numa lista. O único caso que precisa de juízo humano (uma ficha que diz «Valagro» e um
canal que é da Syngenta) já tinha uma gaveta própria e vai para uma pessoa, não para um modelo.

**5. As fontes novas chegaram mesmo à matéria, ou pararam na capa?**
Chegaram à matéria, e agora há um juiz que verifica isso: abre a notícia e mede se parece texto ou
uma lista de links. Provei que o juiz está ligado desligando-o à mão: dois testes ficaram vermelhos.
E o livro passou a dizer, em cada fonte pronta, por que régua ela passou: 9 pela régua antiga, 11 pela
nova. As duas não se misturam.

**6. O Bot continua sozinho depois do fim do turno?**
Sim. Matei o worker a meio de uma tarefa e o supervisor relançou-o em 5 segundos. Matei-o com a fila
vazia e ele ficou em «ocioso», sem morrer. Pedi-lhe para parar por bandeira e ele parou limpo. Religuei
e ele recuperou a tarefa interrompida. O painel passou a perguntar ao sistema operativo se o processo
existe: um ficheiro velho a dizer «a correr» já não engana ninguém.

**7. O que acontece quando as candidatas acabarem?**
Há um contador do que ainda pode virar trabalho automático: 51 hoje, nível mínimo 20. Quando cair
abaixo, fica escrito «é preciso descoberta», com os números ao lado. O motor de descoberta existe
noutra bancada (já tem 271 candidatas) e não foi ligado aqui, por ordem.

**8. As redes sociais ficaram de fora. Porquê, e o que falta para entrarem?**
LinkedIn, Instagram e Facebook exigem conta, têm regras próprias e não se leem como um site normal.
Tratá-las como HTML seria contornar essas regras. Ficam registadas como dívida, com dono próprio. Para
entrarem falta uma rota que respeite a autenticação de cada uma, e isso é outra missão.

---

## ADENDA — UM TESTE LANÇA UM WORKER REAL SOBRE OS FICHEIROS REAIS

Medido depois do fecho: `READY-BATCH-002` (as 4 READY_CURRENT do PASSO 3) nasceu às 04:01:18Z, dentro
da janela em que a suíte de `curadoria/` correu, e nenhum comando meu fecha lotes. A causa é
pré-existente: `test_supervisor.py` (linha 182) injeta uma tarefa e chama `uma_volta_sup`, que lança
um `ciclo_continuo.py` **real** nesta árvore. Antes de ser terminado pelo teste, esse ciclo faz uma
volta sobre os ficheiros reais: recupera órfãs, corre o worker sobre a fila real (rede, se houver
elegíveis), fecha lote e escreve o estado. Às 04:01Z a fila real tinha 0 elegíveis, por isso só o lote
foi fechado, e foi esse ciclo que deixou o `SUPERVISOR-STATE.json` com RUNNING e um PID morto (§ PASSO 9).
O lote 002 é verdadeiro (as 4 estavam READY e por entregar); a proveniência é que é um teste.
Corrida de confirmação: a suíte, isolada, com 0 elegíveis, não altera o ficheiro de lotes.

```text
DIVIDA: test_supervisor deve redirecionar fila, livro, lotes e estado, ou lançar o worker com um
        cwd descartável. Enquanto não, NÃO correr a suíte com tarefas elegíveis na fila real.
```
