# PLANO — C-INT-BC1-READONLY (fase 1 = PREPARAR)

> **Estado: PLANO FECHADO (fase 1), depois da 1.ª onda (BC5, Sala 66 → 69).** Revisto pela
> CORREÇÃO DE ESCOPO do coordenador (24/09) e fechado sobre a prova da onda. Nada foi
> executado: nenhuma leitura da Sala, nenhum banco aberto, nenhum motor corrido, nenhuma
> suite. A fase 1 (ler e planear) é permitida pela trava («medir o que a inteligência futura
> vai esperar da coleta»).

| campo | valor |
|---|---|
| missão | `C-INT-BC1-READONLY` — bot Luciano (delegação do dono), 24/09 ~08:20; escopo corrigido pelo coordenador no mesmo dia |
| árvore | `intelligence-bc1-v1` a partir de `origin/unificacao-v1` @ `98ec8fbf` (a linha instalada) |
| lei | `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md` **V0.3** — `IMPLEMENTATION_AUTHORIZED = SOMENTE_A_PRIMEIRA_MISSAO_DA_SECAO_32_E_SUJEITA_AOS_GATES_UPSTREAM` |
| trava | `docs/operacao/TRAVA-DA-INTELIGENCIA.json` (não editada) — re-medida pelo dono na secção 1 |
| coorte | `C:\bc\COORTE-BIG-COLLECTION.json` — CONGELADA 2026-09-24T03:29:47Z, 18 fontes, 0 T3 |

---

## 0 · O ESCOPO, EM TRÊS LINHAS

```text
FASE 2 (se autorizada)  = a missão da SECÇÃO 32 — 1 item real, 1 INTELLIGENCE_RUN, HARD STOP
AS 5 PERGUNTAS          = PROPOSTA ao dono — exige TRAVA = SIM + autorização. NÃO é execução.
O PILOTO DA SALA        = fica FORA da fase 2 (seria artefato de implementação novo nesta linha)
```

A versão anterior deste plano (commit `ac2d4c8b`) planeava correr o piloto da Sala sobre todo
o delta e responder às 5 perguntas. **Estava fora do escopo que a Bíblia autoriza.** Essa
parte passou para a secção 4, como proposta.

---

## 1 · A TRAVA, RE-MEDIDA PELO DONO (sem editar)

Dono da medição: `system-map/data/estradas-it.generated.json`. **Re-medido depois da 1.ª
onda** (24/09, depois da troca de conta), em quatro linhas — o ficheiro é **o mesmo blob**
(`8be989c7`) em todas, e o do contrato da trava também (`3cf19203`):

| linha | commit | `estradas-it` | último toque |
|---|---|---|---|
| esta árvore | `e73cf8fe` | `8be989c7` | `4ec62114`, 23/09 18:12 −03 |
| `origin/unificacao-v1` | `98ec8fbf` | `8be989c7` | idem |
| `origin/bc4-correcoes-v1` (com a prova da BC5) | `cffaad2d` | `8be989c7` | idem |
| bot instalado | `fca4f2b6` | `8be989c7` | idem |

⚠️ O ficheiro **não foi regenerado depois da onda** em nenhuma linha. A onda não é, por si,
motivo para a trava mudar (18 fontes em rotas já conhecidas), mas isto é o que o dono diz
**em 23/09 18:12**, não uma medição feita depois da onda. Não o regenero: não é desta
missão. Valores:

| grandeza | valor medido | o que a trava pede |
|---|---|---|
| `COLLECTION_FOUNDATION_CLOSED` | **`false`** | `SIM` |
| `ROUTE_CLASSES_MODELED` | 12 | — |
| `ROUTE_CLASSES_ARCHITECTURE_CLOSED` | **0 de 12** (`[]`) | todas as necessárias |
| `ROUTE_CLASSES_REQUIRED_TOTAL` | **`UNKNOWN`** — «23 fonte(s) sem rota conhecida» | deixar de ser `NAO SEI` |
| `ROUTE_CLASSES_OBSERVED` | RC-1, RC-2 | — |
| `ROUTE_CLASSES_DB_TESTED` | RC-5 | — |
| `ROUTE_CLASSES_BLOCKED` | RC-6, RC-7, RC-8 | cada uma com decisão escrita |
| `ROUTE_CLASSES_DEBT` | RC-9 | — |
| `VEREDITOS.M1_CLASSIFICATION_PASS` | `CLOSED` | — |
| `SOURCE_NETWORK_COVERAGE` | `INCOMPLETE` — 7 fontes com rota provada, 47 sem | — |

Critérios A..N do próprio contrato da trava: **5 de 14 cumpridos** (C, D, F, K, L), medidos em
2026-09-08; não re-medidos aqui, porque o dono deles é o contrato, não esta missão.

```text
TRAVA = NAO   (igual a 2026-09-08 e a 2026-09-14; nada nesta medição a mudou)
```

⚠️ **Consequência que o plano não pode esconder.** A secção 32 da Bíblia diz, na sua própria
caixa, que a missão «continua a não poder correr» por dois gates a montante, e que **nenhum
dos dois é desta Bíblia para abrir**:

| gate da §32 | 2026-09-14 | hoje (sem ler a Sala) |
|---|---|---|
| `TRAVA-DA-INTELIGENCIA.json` | `NAO` | **`NAO`** — medido acima |
| `ONE REAL WAITING_ROOM ITEM` | 0 itens | **aberto por prova escrita, não por leitura minha**: a 1.ª onda pousou **3 SIM** (Sala 66 → 69), todos de `IT-T10-018` (myfruit.it) numa só corrida — `ferramentas/big_collection/BC5-BIG-COLLECTION-1A-ONDA.json` em `origin/bc4-correcoes-v1` @ `e18ce992`. Antes, a BC4d tinha pousado 2 (64 → 66). Ler a Sala continua proibido nesta fase |

Portanto a fase 2 **precisa de uma de duas coisas, escritas pelo dono**, e não sou eu que
escolho:

1. a trava passar a `SIM` pelo seu próprio dono; **ou**
2. uma decisão escrita do dono de que a missão da §32 (1 item, sem sinal, sem pontuação, sem
   Portal) corre com a trava `NAO` — porque a própria trava lista o que impede («ligar
   sinais», «pontuação e recomendação», «alimentar o portal», «desenvolvimento NOVO») e a §32,
   sem código novo, não faz nenhuma destas. **Essa leitura é minha e é interpretação, não
   facto**; a Bíblia diz o contrário na letra («continua a não poder correr»).

---

## 2 · A FASE 2 = A MISSÃO DA SECÇÃO 32 (só com a decisão da secção 1)

Pergunta mínima (Bíblia §32, na letra):

> Qual é o contrato mínimo de entrada/saída e identidade de um `INTELLIGENCE_RUN` consumindo
> **um claim/fato real e admitido** da Sala de Espera, sem produzir Opportunity ainda?

Gate, e depois **HARD STOP**:

```text
ONE REAL WAITING_ROOM ITEM
→ UPSTREAM CLAIM/FACT IDENTITY PRESERVED
→ ONE IDENTIFIED INTELLIGENCE_RUN
→ PROVEN INPUT LINEAGE
→ NO DIRECT COLLECTION
→ NO ANALYTIC JUDGMENT FABRICATION
```

### 2.1 · Um item, e qual — regra escrita ANTES de ver a Sala

A §32 diz **um** item. O coordenador pediu «os itens novos da 1.ª onda». Para não esticar a
lei, a fase 2 corre **um** `INTELLIGENCE_RUN` sobre **um** item; mais itens são outra
autorização. Regra de escolha (fixada no commit `e73cf8fe`, antes de a onda existir):

```text
ITEM_32 = o primeiro (RUN_ID, ORDEM), por ordem crescente, entre as linhas da Sala cujo
          RUN_ID pertence às corridas da 1.ª onda e cujo SOURCE_ID está nas 18 da coorte.
```

**Aplicada à prova da onda (`BC5-BIG-COLLECTION-1A-ONDA.json`, sem ler a Sala):**

| fonte | `RUN_ID` | Admission | Sala |
|---|---|---|---|
| `IT-T10-018` | `IT-T10-2026-09-24-120449-0196c6a5c9db1619` | **SIM 3** | 66 → 69 |
| `IT-T7-021` | `IT-T7-2026-09-24-120737-b9d168ef521cb4d9` | NAO_SEI 1 | 69 → 69 |
| `IT-T7-042` | `IT-T7-2026-09-24-120820-4682d316adbce27d` | NAO 1, NAO_SEI 2 | 69 → 69 |
| `IT-T7-117` | `IT-T7-2026-09-24-120938-51efde19469b3350` | NAO 1 | 69 → 69 |
| `IT-T7-135` | `IT-T7-2026-09-24-121113-bcac8be0b7e36d61` | NAO 1 | 69 → 69 |
| as outras 13 | — | nada admitido | +0 |

Só uma corrida da onda pousou linhas na Sala. Logo:

```text
ITEM_32 = (RUN_ID = IT-T10-2026-09-24-120449-0196c6a5c9db1619, ORDEM = 0)
          SOURCE_ID = IT-T10-018 (myfruit.it, T10 mercado) · critérios C1–C6 PASS na prova
```

As ORDEM 1 e 2 da mesma corrida **não** entram: são o 2.º e o 3.º item, e a §32 é um.
O substituto da versão anterior (o SIM da BC4d) deixa de ser preciso e sai do plano.

Conferências antes de correr (fase 2, passo 2): a corrida devolve **3** itens pelo dono da
Sala (= +3 da prova); `sala_de_espera` = **69** (= `SALA_DEPOIS` da prova). Se não bater →
PARAR: a Sala mudou depois da onda, e a escolha refaz-se pela mesma regra.

A escolha não olha para o conteúdo: escolher o item «mais interessante» seria procurar
card (INT-LAW-014).

### 2.2 · Nenhum código novo

Tudo o que a fase 2 usa **já existe na linha instalada**:

| peça | papel | estado |
|---|---|---|
| `admissao/sala_de_espera.py` → `ler(run_id)` | o **dono** da Sala lê as linhas de uma corrida | existe; só a leitura é chamada — `pousar` e `retirar` **nunca** |
| `motor/corrida_da_inteligencia.py` → `main()` → `correr()` | o `INTELLIGENCE_RUN` mínimo: `INTELLIGENCE_RUN_ID` derivado das entradas, G0, `REQUIREMENT_ID` | existe (C-INT-PILOT-01, escrito para a §32); espécie `MENCAO_FRACA_APENAS` no censo do congelamento — não é artefato congelado, e **não é alterado** |
| `provas/espinha_da_intelligence.py` | vocabulário dos 19 campos do READY | existe; não alterado |
| `tests/test_a_primeira_corrida_da_inteligencia.py` | o teste do motor | existe; **não corrido** nesta fase (RAM) |

O **piloto da Sala** (`provas/o_piloto_da_sala.py`, só em `claude/int-pilot-sala-v1`) **não**
é trazido: nesta linha seria um ficheiro novo de implementação de inteligência, e a trava
(`FREEZE_MANIFEST`) proíbe que apareça artefato novo de espécie `IMPLEMENTATION` enquanto
`NAO`.

### 2.3 · Os passos

| # | passo | escreve em | lê |
|---|---|---|---|
| 0 | conferir: decisão escrita da secção 1; ordem do coordenador; volumes da onda reconciliados; bot/coletor parados; RAM livre | — | — |
| 1 | fotografia `SALA_ANTES` (5 contagens: `sala_de_espera`, `raw_asset`, `storage_object`, `derived_artifact`, `collection_run`) | `data/derivados/BC1-S32/` | Sala, só-leitura |
| 2 | confirmar `ITEM_32` pela regra 2.1 (a corrida tem 3 itens; Sala = 69) | `data/derivados/BC1-S32/` | prova da BC5; Sala, só-leitura |
| 3 | `sala_de_espera.ler(RUN_ID)` com `PGOPTIONS="-c default_transaction_read_only=on"`; guardar só o item de `ITEM_32` (ver nota ORDEM), com o sha256 do ficheiro | `data/derivados/BC1-S32/` | Sala, só-leitura |
| 4 | `py motor/corrida_da_inteligencia.py <item.json> > <livro.json>` — o `main()` **imprime** o livro (não chama `gravar()`); guarda-se a saída tal como sai | `data/derivados/BC1-S32/` | o ficheiro do passo 3 |
| 5 | fotografia `SALA_DEPOIS` — **igual** à do passo 1, ou PARAR | `data/derivados/BC1-S32/` | Sala, só-leitura |
| 6 | relatório; know-how; mapa; commit + push; **HARD STOP** | árvore | — |

**Nota ORDEM (lida no código do dono, não medida).** `ler(run_id)` devolve os itens com as
chaves exactas que o motor lê (incluindo `CORRIDA = run_id`) — **mas sem o campo `ORDEM`**. A
ordem vem da lista: o `select` é `order by ordem`, e o `pousar()` do dono escreve
`ordem = i` (0, 1, 2, …) para a corrida inteira de uma vez. Logo a posição na lista **é** a
`ORDEM`, desde que a corrida tenha pousado pelo dono. Conferência na fase 2: o número de itens
devolvidos = `count(*)` da corrida, e `max(ordem) = n − 1` pela mesma leitura só-leitura. Se
não bater → `ORDEM = NAO SEI` e **PARAR** (a linhagem da §32 precisa dela).

Nada escreve na Sala, na Admission, no READY, nos livros das fontes ou na Collection. Nada
chama coletor nem abre rede externa.

### 2.4 · As provas que a §32 pede

| elo do gate | como se prova |
|---|---|
| ONE REAL WAITING_ROOM ITEM | a linha lida do dono da Sala, com `(RUN_ID, ORDEM)`, `ESTADO = READY`, e a contagem da Sala igual antes e depois |
| UPSTREAM IDENTITY PRESERVED | `ITEM_ID`, `SOURCE_ID`, `RAW_OBSERVATION_ID` e `CORRIDA` no livro **iguais byte a byte** aos da linha; nenhum cunhado (o motor recusa derivar identidade de SHA) |
| ONE IDENTIFIED INTELLIGENCE_RUN | `INTELLIGENCE_RUN_ID` (`IR-…`) derivado do pedido e das entradas, não do relógio; `RULESET_VERSION G0/v1`; `CODE_VERSION`; `START`/`END` |
| PROVEN INPUT LINEAGE | livro → ficheiro do item (sha256) → linha da Sala `(RUN_ID, ORDEM)` → `RAW_OBSERVATION_ID` → `collection_run` |
| NO DIRECT COLLECTION | o motor não importa coletor nem abre rede (lido no código); nenhum processo de coleta corre durante a fase 2 |
| NO JUDGMENT FABRICATION | saída limitada a `INTAKE_OK` / `NO_ANALYTIC_OUTPUT_YET` / `BLOQUEADO_EM_G0`; 0 FINDING, 0 OPPORTUNITY, 0 pontuação |

### 2.5 · O resultado esperado, declarado antes

O G0 exige `ITEM_ID`, `SOURCE_ID`, `FACT_TIME`, `RAW_OBSERVATION_ID`. Na R2 (20/09),
`FACT_TIME = NAO SEI` em 46/46. Expectativa (não medição):

```text
RESULT = BLOQUEADO_EM_G0, com 1 REQUIREMENT_ID pedindo FACT_TIME à Collection
```

Isso é **sucesso da §32**: a corrida existe, tem identidade, tem linhagem e recusou-se a
fabricar. `NO_DEFENSIBLE_ACTION_YET` (INT-LAW-012). O `REQUIREMENT_ID` fica **escrito, não
despachado** (INT-LAW-020).

---

## 3 · O QUE A VERIFICAÇÃO ESTÁTICA ENCONTROU (sem executar)

- **V1** — a base é `origin/unificacao-v1` @ `98ec8fbf`; a BC4b–BC4d (com os 2 SIM) está em
  `origin/bc4-correcoes-v1` @ `f48ed6ed`, por cima.
- **V2** — o motor da §32 existe nesta linha e não abre a Sala: recebe o item num ficheiro. A
  leitura fica com o dono da Sala (`admissao/sala_de_espera.py`), como o próprio motor manda.
- **V3** — a ligação à Sala é só-leitura **por código**, não **por banco**: a DSN do dono pode
  escrever. Defesa sem mudar código: `PGOPTIONS` só-leitura + fotografia antes/depois.
- **V4** — o piloto da Sala não está nesta linha; trazê-lo seria implementação nova sob trava
  `NAO`. Fica fora.
- **V5** (só relevante para a proposta da secção 4) — o checkpoint `--desde-artefato` do piloto
  guarda só os itens da própria rodada (R1 = 29, R2 = 17): usar o da R2 sozinho reanalisaria os
  29 da R1; e o checkpoint daria também os ~20 itens pré-onda (46 → 66) nunca processados.
- **V6** — as referências ADAMA (`AUTHORIZED-USES.json`, portfólio IT-T4-001) têm o mesmo blob
  na linha do piloto e na instalada.
- **V7** — `motor/cadeia_canonica.sh` escreve num banco e `motor/v21_cadeia.sh` é o pacote do
  Portal: nenhum dos dois entra.

---

## 4 · PROPOSTA AO DONO — NÃO É EXECUÇÃO

```text
ESTADO = PROPOSTA
EXIGE  = TRAVA = SIM  +  autorização escrita do dono
```

Tudo o que está abaixo é **ligar sinais / cruzar / produzir finding ou oportunidade** — o que a
trava impede e a Bíblia ainda não autoriza. Fica escrito para que, no dia em que abrir, não se
invente o método na hora.

### 4.1 · As 5 perguntas

| # | pergunta | como se mediria | o que nunca se faria |
|---|---|---|---|
| 1 | O que é realmente novo? | delta por `(RUN_ID, ORDEM)` da onda; redundância por md5 do texto contra a Sala anterior (NOVO NA FILA ≠ NOVO COMO EVIDÊNCIA) | chamar «novo» à re-observação |
| 2 | Fontes independentes que se apoiam/contradizem? | grafo de dependência primeiro (INT-LAW-070/071): a CIA são 7 das 18 fontes e é **uma** família; apoio/contradição só com tempo e lugar compatíveis — com `NAO SEI`, o estado é `UNKNOWN` | contar 7 páginas da CIA como 7 vozes |
| 3 | Crossings possíveis com tempo, território e chaves provadas? | tentados/possíveis/bloqueados com `JOIN_KEYS_MISSING` (INT-LAW-091). Com 0 T3 na onda, esperado 0 tentados | tirar cultura/região do corpo do texto; correlação virar causa |
| 4 | Algum finding/oportunidade passa todos os gates? | contagem depois de G0 + crossing; esperado `NO_DEFENSIBLE_ACTION_YET` | relaxar gate; procurar card até achar |
| 5 | Que lacunas voltam à Collection? | `REQUIREMENT_ID` do G0 + `FACT_TIME`/`FACT_LOCATION`/`EVIDENCE_CLASS`/`CROP` em `NAO SEI` + ausência de T3 → `COLLECTION_GAP_REQUEST` escritos | chamar coletor; escolher rota |

A pergunta 5 é a única com um pedaço já dentro da §32: o `REQUIREMENT_ID` que o G0 emite
sobre o item da fase 2.

### 4.2 · Métricas propostas

entradas por tipo/idioma/fonte (idioma só o declarado; sem campo → `NAO SEI`) · novidade e
redundância · independência (`INDEPENDENT_SOURCE_COUNT` separado de `EXTERNAL_SIGNAL_COUNT`) ·
suporte/contradição/`UNKNOWN` · crossings tentados/possíveis/bloqueados · `UNKNOWN` por campo ·
findings · oportunidades defensáveis · gaps · estados `NOT_RUN`/`ERROR`/`EMPTY_RESULT`/`NO_FINDING`
separados (INT-LAW-053).

### 4.3 · O que a proposta já sabe que vai dar

Com 0 T3 na coorte: **0 crossings, 0 oportunidades, `NO_DEFENSIBLE_ACTION_YET`**. Um número
diferente seria um achado a medir, não uma boa notícia. E, sem T3: nada de diagnóstico
agronómico, risco de cultura ou recomendação técnica.

---

## 5 · RISCOS

| risco | efeito | defesa |
|---|---|---|
| correr a §32 com trava `NAO` sem decisão escrita | quebrar a letra da Bíblia | passo 0 exige a decisão da secção 1 |
| esticar «um item» para «todos os novos» | a §32 vira a proposta da secção 4 por baixo da porta | 1 item, 1 corrida, HARD STOP |
| escolher o item pelo conteúdo | procurar card | regra 2.1 fixada antes de ver a Sala |
| DSN do dono pode escrever | escrita acidental na Sala | `PGOPTIONS` só-leitura; só `ler()`; fotografia antes/depois |
| os 3 SIM são da mesma fonte e da mesma corrida | nada a ver com a §32: ela prova o contrato, não a diversidade | declarado; diversidade é pergunta da proposta (secção 4) |
| a trava lida é de 23/09, antes da onda | decidir sobre uma medição velha | declarado na secção 1; regenerar é do dono do mapa |
| `IT-T10-022` (avicultura) ser o 1.º por ordem | item fora de foco | a regra não muda; o item corre só pelo G0, sem tema — a §32 não analisa conteúdo |
| RAM partilhada (suite BC5 + coleta) | medição truncada | só com ordem do coordenador e máquina livre |
| os 3 SIM da onda vêm da prova da BC5, não de leitura minha | o gate «item real» pode não estar como dito | o passo 1 conta; o passo 3 lê a linha pelo dono |

---

## 6 · O QUE NÃO FOI VERIFICADO

- o conteúdo real da Sala hoje e os 3 SIM da onda (proibido ler nesta fase) — sei deles pela prova da BC5, não por leitura;
- o `FACT_TIME` dos 3 SIM: o critério C5 da prova só diz que **nenhum** foi fabricado a partir de `CAPTURED_AT`, não quantos são `NAO SEI`;
- se `FACT_TIME` continua `NAO SEI` (expectativa, não facto);
- os critérios A..N da trava depois de 2026-09-08 (dono: o contrato da trava);
- o teste do motor (`test_a_primeira_corrida_da_inteligencia.py`) — não corrido (RAM).
