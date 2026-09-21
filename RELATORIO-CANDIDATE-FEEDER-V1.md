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
