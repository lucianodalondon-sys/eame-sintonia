# RE-MEDIÇÃO DA TRAVA DA INTELIGÊNCIA — contra a árvore INSTALADA

> **Só medição.** `docs/operacao/TRAVA-DA-INTELIGENCIA.json` **não foi editado**. Nenhuma
> Sala lida, nenhum banco aberto, nenhuma suite corrida, nenhuma rede.

| campo | valor |
|---|---|
| pedido | coordenação, 24/09 — re-medir a trava de 08/09 pelo dono, critério a critério |
| árvore medida | **`origin/egresso-consenso-v1` @ `a310487f`** (produção), num worktree destacado e descartável |
| dono da medição da fundação | `system-map/data/estradas-it.generated.json`, gerado por `system-map/scripts/censo_das_estradas_it.py`; a constante vive em `leis/fundacao_da_coleta.py` |
| contrato dos critérios | `docs/operacao/TRAVA-DA-INTELIGENCIA.json` (`CRITERIOS_PARA_FECHAR` A..N, `CONDICAO_DE_DESTRAVE`) |
| iguais entre esta árvore e a produção | `TRAVA-DA-INTELIGENCIA.json`, `leis/fundacao_da_coleta.py`, `censo_das_estradas_it.py`, `MAPA-DE-FECHAMENTO-DA-COLETA-ITALIANA.md` — `git diff` vazio |

## 0 · O RESULTADO, EM TRÊS LINHAS

```text
COLLECTION_FOUNDATION_CLOSED = NAO        (leis/fundacao_da_coleta.py e o censo concordam)
CRITÉRIOS A..N               = 4 SIM · 8 NAO · 2 NAO_SEI   (a trava dizia 5 SIM · 9 pendentes)
CONDIÇÃO DE DESTRAVE         = 0 de 5 condições cumpridas
```

## 1 · O censo do dono, corrido de novo sobre a produção

```text
py system-map/scripts/censo_das_estradas_it.py     (no worktree de a310487f)

ARCHITECTURE_CLOSED 0 · OBSERVED 2 · DB_TESTED 1 · BLOCKED 3 · DEBT 1
CLASSES SOCIAIS 7 · APIFY default 0 / fallback 5
GIT COMO BANCO: 2 ficheiro(s)
ORQUESTRADOR: EXISTE · alcanca 9 executores
COLLECTION_FOUNDATION_CLOSED = NAO
```

O ficheiro que ele escreveu é **idêntico** ao que está commitado na produção (`git status`
vazio depois de correr; blob `8be989c7`, último toque `4ec62114`, 23/09 18:12 −03). A leitura
de 23/09 é, portanto, a leitura de hoje.

## 2 · ⚠️ O PONTO CEGO DO DONO — mede 54 fontes, a casa coleta noutras

O censo lê **um** catálogo: `candidatas/ITALY-SOURCE-MASTER-V1.json` → **54 fontes**
(`FONTES_IT.TOTAL = 54`). A produção coleta por outro livro:
`regras/italy_contracts_onboarded.json` → **193 fontes** com contrato.

Das fontes da coorte da 1.ª onda (BC5, 18/18 SUCCESS, 3 SIM na Sala), procurei 8 no censo:
**IT-T10-018, IT-T10-021, IT-T10-022, IT-T2-034, IT-T2-051, IT-T5-090, IT-T7-017, IT-T7-121 —
as 8 estão AUSENTES.**

Consequência: o critério **A** («toda fonte IT tem route class conhecida») está a ser medido
sobre um universo que **não inclui** as fontes que a casa de facto coleta. A trava pode ficar
`NAO` ou virar `SIM` por razões que não descrevem a coleta real. **Não corrigi nada**: o censo
tem dono, e decidir o universo é decisão dele, não desta medição.

## 3 · CRITÉRIO A CRITÉRIO

Regra usada: **SIM** só com prova de um ficheiro gerado por dono; **NAO** quando a prova
contradiz; **NAO_SEI** quando nenhum dono mede o critério. A coluna «trava 08/09» é o que o
contrato declara (`QUAIS_JA_CUMPRIDOS = C, D, F, K, L`).

| | critério | trava 08/09 | **hoje** | prova (produção `a310487f`) |
|---|---|---|---|---|
| **A** | toda fonte IT tem route class conhecida ou BLOCKED explícito | falta | **NAO** | `estradas-it`: das 54, **7** com rota provada, 24 só candidata, 23 rota desconhecida, 0 BLOCKED. E o universo de 54 não contém as fontes da coleta real (secção 2) |
| **B** | nenhuma fonte depende de writer improvisado | falta | **NAO_SEI** | nenhum ficheiro gerado mede «writer improvisado» (0 ocorrências). Indício, não prova: `executores` — 68 caminhos relevantes, **2** executores provados, 63 `NOT_INSTRUMENTED`, 38 `UNKNOWN` |
| **C** | RAW tem um dono | ✅ cumprido | **NAO** | `donos`: `RAW_ASSET = DONO_DUPLICADO` — 4 escrevem (`guarda/preservar_coleta.py`, `guarda/catalogo_importar.py`, `guarda/memoria_descartavel.py`, uma importação SQL). O censo avisa que é grep grosseiro e que duplicado «pode ser um dono canónico mais um legado» — mas não prova qual é qual |
| **D** | a corrida tem um contrato | ✅ cumprido | **SIM** | `donos`: `RUN_MANIFEST = UM_DONO` (`leis/data_clock.py`), lido por 9. Ressalva: `COLLECTION_RUN` tem 10 escritores (`DONO_DUPLICADO`) — o contrato é um, quem escreve a linha não |
| **E** | o checkpoint tem um dono | falta | **NAO** | `donos`: `CHECKPOINT = DONO_DUPLICADO` — `coleta/coleta_checkpoint.py` + `supabase/tests/regressoes_coleta.sql`; `executores`: `TOTAL_CHECKPOINT_OWNERS = 4` |
| **F** | o derivado tem um dono | ✅ cumprido | **SIM** | `donos`: `DERIVED_ARTIFACT = UM_DONO` (`guarda/preservar_derivado.py`), lido por 19 |
| **G** | persistência estruturada tem dono por espécie | falta | **NAO** | `estradas-it`, etapa `STRUCTURED` por classe: RC-1 `CODE`, RC-2 `DB_TESTED`, RC-5 `LIVE_SCHEMA`, RC-3/4/10/11/12 `UNKNOWN` |
| **H** | a escolha de rota não vive espalhada | falta | **NAO** | `donos`: `ROUTE_MODEL = DONO_DUPLICADO` (6 escrevem); `ORQUESTRADOR = DONO_DUPLICADO` (13); `executores`: 6 orquestradores; o orquestrador alcança 9 executores — «existir não é cobrir» (o próprio censo) |
| **I** | Apify não é rota por omissão | falta | **SIM** | `estradas-it.APIFY`: `DEFAULT 0`, `FALLBACK 5` |
| **J** | o Git não é estado operacional | falta | **NAO** | `estradas-it.GIT_COMO_BANCO_OPERACIONAL`: `data/collection-ledger/italy/observations.ndjson` (521 linhas) e `runs.ndjson` (59) |
| **K** | retry e queda não fabricam sucesso | ✅ cumprido | **NAO_SEI** | nenhum dono mede retry. Há sinais: `fluxo.A_CONTA_FECHA = true` (59 corridas, 521 observações); `executores.FAULT_PATH_PROVED = 2` de 68 caminhos. Dois caminhos de falha provados não provam o critério para a casa |
| **L** | UNKNOWN continua UNKNOWN | ✅ cumprido | **SIM** | `estradas-it`: `ROUTE_CLASSES_REQUIRED_TOTAL = UNKNOWN` mantido; `VEREDITOS.M1_FONTES_SEM_PROXIMA_PROVA = []`; `observabilidade`: `NOT_INSTRUMENTED ≠ NOT_MEASURED ≠ MEDIDO` separados |
| **M** | o System Map representa tudo | falta | **NAO** | `state.COUNTS`: 241 componentes, **202 pendentes**, 8 desconhecidos; 1 231 de 2 809 ficheiros cobertos; 70 papéis `UNKNOWN`, 37 em conflito; `UNCLAIMED_FILES_COUNT = 1578` |
| **N** | a inteligência continua congelada até aqui | falta (só no fim) | **NAO** | ver secção 4 — **16 de 73** artefactos congelados mudaram e **5** novos apareceram |

**Divergências com a trava de 08/09:** C passou de cumprido para **NAO** e K para **NAO_SEI**;
I passou de pendente para **SIM**. Não é necessariamente regressão — o censo `donos` pode medir
com régua diferente da usada a 08/09. Não sei qual régua a trava usou: ela lista as letras sem
a prova de cada uma.

## 4 · ⚠️ O CRITÉRIO N — o congelamento não está a morder

A trava guarda uma fotografia (`FREEZE_MANIFEST`, `FROZEN_AT_HEAD = 82ef1deb`, 73 artefactos com
`GIT_BLOB_SHA`). Comparei cada um com o blob em `a310487f`:

```text
artefactos congelados na trava   73
mudaram de blob                  16
sumiram                           0
novos (no censo, não na trava)    5
```

Os 16 que mudaram, com a espécie que a trava lhes dá:

| espécie | ficheiro |
|---|---|
| IMPLEMENTATION | `coleta/instagram_coleta.py` |
| PORTAL_UI | `italia-portale/audit/casa-gate.mjs` |
| PORTAL_UI | `italia-portale/audit/casco/release-gate.mjs` |
| PORTAL_UI | `italia-portale/audit/checks.mjs` |
| PORTAL_UI | `italia-portale/audit/meeting-gate.mjs` |
| PORTAL_UI | `italia-portale/client/adama-relevance.js` |
| PORTAL_UI | `italia-portale/client/italy-app-model.js` |
| PORTAL_UI | `italia-portale/client/italy-casa.js` |
| PORTAL_UI | `italia-portale/client/italy-handoff-v21.js` |
| PORTAL_UI | `italia-portale/client/italy-i18n.js` |
| PORTAL_UI | `italia-portale/client/meeting-intelligence-snapshot.js` |
| PORTAL_UI | `italia-portale/client/meeting-surface.js` |
| IMPLEMENTATION | `regras/italy_contracts.mjs` |
| IMPLEMENTATION | `regras/sensor_coleta.py` |
| IMPLEMENTATION | `regras/sensor_medir.py` |
| PORTAL_UI | `superficie/it_casa_dados.py` |

Os 5 novos, com a espécie que o censo lhes dá (as três espécies que a trava proíbe que apareçam):

| espécie | ficheiro |
|---|---|
| CONTRACT | `docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json` |
| CONTRACT | `research/intelligence/DATA-DEMAND-MATRIX-ITALY.json` |
| CONTRACT | `system-map/data/architecture.declared.json` |
| PORTAL_UI | `italia-portale/audit/superficie-visivel.mjs` |
| PORTAL_UI | `italia-portale/client/italy-label-intelligence.js` |

**E o censo do congelamento não o denuncia, por construção.** `congelamento.generated.json`
grava `FROZEN_AT_HEAD = <HEAD do momento>` (`fa17ccdf`, 24/09 16:07) e os blobs **de agora** —
logo compara a árvore consigo mesma e dá **0 diferenças** sempre. Quem compara contra a
fotografia de 08/09 são os testes `test_nenhum_artefato_congelado_mudou` e
`test_nao_apareceu_inteligencia_nova` (`tests/test_trava_da_inteligencia.py`); pela minha
comparação eles falhariam na produção. **Não corri a suite** (proibido: RAM); é a mesma
comparação que eles fazem, feita à mão.

Ressalvas: (1) algumas mudanças podem ser consertos de coleta ou de dados, que a trava permite
(«corrigir um defeito que ameace dados»); isso exige ler cada diff, e não o fiz. (2)
`architecture.declared.json` classificado como CONTRACT de inteligência é decisão do censo; pode
ser falso positivo. **Não há decisão escrita** que eu tenha encontrado a autorizar estes 21.

## 5 · A CONDIÇÃO DE DESTRAVE (as 5, todas ao mesmo tempo)

| condição | hoje |
|---|---|
| os 14 critérios A..N cumpridos | **NAO** — 4 de 14 |
| nenhuma classe NECESSÁRIA em `UNKNOWN` | **NAO** — RC-3, RC-4, RC-10, RC-11, RC-12 têm etapas `UNKNOWN`; e quais são «necessárias» não se sabe |
| nenhuma classe NECESSÁRIA em `OPEN` | **NAO_SEI** — o censo não usa o estado `OPEN`; publica `OBSERVATION_STATE`: RC-1/RC-2 `PARTIALLY_OBSERVED`, RC-3/4/10/11/12 `NOT_OBSERVED`, RC-5 `DB_TESTED`, RC-6/7/8 `BLOCKED`, RC-9 `DEBT`; `ARCHITECTURE_CLOSED = false` nas 12 |
| nenhuma BLOCKED sem decisão escrita | **NAO_SEI** — RC-6/7/8 têm `BLOCKED_REASON` escrito (robots/termos; sessão humana não autoriza automação; APIFY-LAST), mas o contrato pede **quem decidiu**, e o censo não o nomeia. `M1_BLOCKED_SEM_DECISAO_ESCRITA = []` é por fonte |
| `ROUTE_CLASSES_REQUIRED_TOTAL` deixou de ser NAO SEI | **NAO** — `UNKNOWN`: «23 fonte(s) sem rota conhecida» |

## 6 · O QUE FALTA PARA `COLLECTION_FOUNDATION_CLOSED = SIM`

Por ordem de dependência (a lista é medida; a ordem é proposta minha):

1. **Decidir o universo do critério A** — as 54 do catálogo antigo, as 193 com contrato, ou o
   livro do curador. Sem isto, qualquer número de A mede a coisa errada (secção 2).
2. **Fechar `ROUTE_CLASSES_REQUIRED_TOTAL`** — hoje `UNKNOWN` por 23 fontes sem rota.
3. **Um dono por conceito** onde o censo diz duplicado: RAW (C), CHECKPOINT (E), escolha de rota
   (H) — ou decisão escrita de qual é o canónico e qual é legado.
4. **Persistência estruturada** com dono por espécie nas classes em `UNKNOWN` (G).
5. **Tirar o estado operacional do Git** (J): os dois `ndjson` do ledger.
6. **System Map**: 202 componentes pendentes, 1 578 ficheiros sem dono (M).
7. **Medidores que faltam**: writer improvisado (B) e retry/queda (K) não têm quem os meça.
8. **Critério N**: explicar os 16 + 5 artefactos (decisão escrita ou reverter), e fazer o censo
   do congelamento comparar contra a fotografia da trava, não contra a própria árvore.
9. Só então a constante em `leis/fundacao_da_coleta.py` e o contrato, **juntos**, pelo dono.

## 7 · O QUE NÃO FOI MEDIDO

- o conteúdo dos 16 diffs do critério N (se são conserto permitido ou avanço proibido);
- a régua com que a trava declarou C, D, F, K, L cumpridos a 08/09;
- se `NOT_OBSERVED` conta como `OPEN` para a condição de destrave (o contrato e o censo usam vocabulários diferentes);
- a suite `tests/test_trava_da_inteligencia.py` — não corrida.

Worktree de medição: `_medir-trava-producao` (detached em `a310487f`), removido no fim; o único
ficheiro que o censo escreveu ficou byte a byte igual ao commitado.
