# MATRIZ DE CONFLITOS — apêndice B da Bíblia

**Data:** 2026-09-07 · **HEAD medido:** `56fdb8c`

> Cada conflito abaixo foi **reproduzido no repositório**, com ficheiro e linha. Nenhum foi
> deduzido de memória. Onde a resolução não sai de uma lei madura já existente, ela fica
> `DECISION_REQUIRED` — e não é decidida em silêncio.

---

## C-001 · `FACT_TIME` pode cair para `published_at`?

| | |
|---|---|
| **CONCEITO** | tempo do fato |
| **FONTE A** | `medidas/fato_local.py:410-411` — `def tempo_do_fato(texto, published_at=None)` com a docstring: *«FACT_TIME só com evidência própria. `published_at` NUNCA o preenche.»* |
| **FONTE B** | `admissao/admissao.py:169` — `q = item.get("fact_time") or item.get("data") or item.get("published_at")`, e a pergunta chama-se «tem tempo do fato» |
| **CONFLITO** | REAL. A porta de admissão aceita `published_at` como resposta à pergunta «quando o fato aconteceu», que é exatamente o que a lei do lugar-e-tempo do fato proíbe. Um item sem `fact_time` mas com data de publicação passa a porta como se tivesse tempo de fato. |
| **PROVA** | as duas linhas acima, no mesmo HEAD |
| **RESOLUÇÃO CANÔNICA** | **A vence.** `AGENTS.md` já lista *«publicação não vira fact time»* entre as leis que o mapa não pode violar, e `medidas/lugar_do_fato.py` a declara no vocabulário do core (`PUBLISHED_AT != FACT_TIME`). Duas leis maduras contra uma linha de fallback. |
| **LEI** | COL-LAW-031 |
| **AÇÃO** | `admissao/admissao.py` deve deixar de aceitar `published_at` nessa pergunta. Item com publicação e sem fato → `NAO_SEI`, não `SIM`. **Não corrigido nesta missão** (§65: a Bíblia não conserta a coleta) — entra como gap G-01. |

---

## C-002 · Existem DOIS contratos de corrida

| | |
|---|---|
| **CONCEITO** | RUN / recibo da corrida |
| **FONTE A** | `data/samples/RUN-MANIFEST.json` — 13 corridas, 22 campos, lido por 5 réguas (`padrao_da_coleta`, `portao`, `proveniencia`, `sensor_coleta`, `contrato_ator`) e assinado por `pedido/orquestrador.py` |
| **FONTE B** | `data/collection-ledger/italy/runs.ndjson` — 6 corridas, 12 campos, escrito por `coleta/italy_recurrent_collect.mjs` |
| **CONFLITO** | REAL. Os dois têm em comum **apenas três campos**: `RUN_ID`, `STARTED_AT`, `FINISHED_AT`. O italiano não tem `COST_USD` nem `STATUS`; o europeu não tem `EGRESS_IP`, `COLLECTOR_VERSION`, `GIT_HEAD`, `SOURCE_CONTRACT_VERSION` nem `IS_BASELINE`. |
| **PROVA** | comparação de chaves dos dois ficheiros no HEAD `56fdb8c` |
| **RESOLUÇÃO CANÔNICA** | **MERGE, e nenhum dos dois é descartado.** O `RUN-MANIFEST` é o contrato canônico (é o que já tem 5 leitores); os cinco campos italianos que faltam nele são **melhores** e sobem para o contrato canônico como obrigatórios quando aplicáveis. Já há precedente medido: `medidas/padrao_da_coleta.py` linhas 247-259 diz literalmente *«o chão que subiu com a coleta italiana»* e já lê os dois ficheiros. |
| **LEI** | COL-LAW-022 |
| **AÇÃO** | gap G-02 — um só formato de corrida, escrito por quem corre. |

---

## C-003 · O sentinela do desconhecido tem CINCO grafias

| | |
|---|---|
| **CONCEITO** | UNKNOWN / NÃO SEI |
| **MEDIDO** | nas gavetas de coleta e inteligência (`.py`): `NAO_SEI` 344 · `NOT_KNOWN` 123 · `UNKNOWN` 95 · `NÃO SEI` 57 · `NAO SEI` 35 |
| **CONFLITO** | PARCIAL, e perigoso. Não são cinco leis diferentes — é **uma lei com cinco escritas**. `pedido/receitas.py::_sabe_o_caminho` já precisa de testar duas variantes (`"NAO SEI"` e `"NÃO SEI"`) para não deixar passar. Qualquer comparação nova que teste só uma das cinco aceita um desconhecido como conhecido, **sem dar erro**. |
| **PROVA** | contagem por `grep` no HEAD; `pedido/receitas.py:131-133` |
| **RESOLUÇÃO CANÔNICA** | **Não há lei madura que escolha uma grafia** — e escolher agora quebraria dados já gravados. `UNKNOWN` é o termo do banco e do mapa; `NÃO SEI` é o termo da fala com o dono. |
| **DECISÃO** | ⚠️ **DECISION_REQUIRED.** A Bíblia declara a lei (COL-LAW-035) sobre o *significado*, e declara explicitamente que a *grafia* está em aberto. Proposta a decidir: `UNKNOWN` como valor gravado, `NÃO SEI` como texto de tela, com uma função única de comparação. Não decidido aqui. |

---

## C-004 · `data/raw/` é cache ou é evidência?

| | |
|---|---|
| **CONCEITO** | preservação do RAW |
| **FONTE A** | decisão **D-003** — `data/raw/` fora do git, porque o bruto é cache reproduzível (`provas/chain.py` refaz) |
| **FONTE B** | `medidas/REGRA-DE-COLETA-EXTERNA-EAME.md` §14 — para rota paga com chave descartável a premissa é falsa: a chave morre e a rota não se replica |
| **CONFLITO** | **JÁ RESOLVIDO, por lei existente.** A §14 não revoga D-003: separa o caso. Rota replicável → cache. Rota não replicável → `data/samples/`, versionado. |
| **LEI** | COL-LAW-044 |
| **AÇÃO** | nenhuma. Registrado para que ninguém «reabra» o conflito. |

---

## C-005 · A rota mais barata vem primeiro — mas ninguém registra que tentou

| | |
|---|---|
| **CONCEITO** | política de rota e escalada paga |
| **FONTE A** | `medidas/REGRA-DE-COLETA-EXTERNA-EAME.md` §21 — fluxo obrigatório `DISCOVERY → TESTE PEQUENO → MEDIÇÃO → ESCOLHA → ESCALA CONTROLADA` |
| **FONTE B** | `pedido/receitas.py:58-105` — `EXECUTORES` é um dicionário fixo com **um executor por alvo**; o campo `custo` é uma frase (`"gratuito"`, `"pago quando passa pela rota Apify"`), não uma ordem de preferência. Não existe campo `WHY_PAID_ROUTE` nem `CHEAPER_ROUTE_ATTEMPTED` em lado nenhum do repositório. |
| **CONFLITO** | NÃO é contradição de lei: é **lei sem implementação**. A §21 manda comparar; o planeador não tem por onde escolher, porque só há um caminho por alvo. |
| **RESOLUÇÃO** | a Bíblia declara COL-LAW-018 e COL-LAW-019 como `LAW = CANONICAL`, e declara a implementação italiana como **`ABSENT`**. Não se afirma que a política já funciona. |
| **AÇÃO** | gap G-04. |

---

## C-006 · Custo `0` quando não se gastou vs. custo `NÃO SEI`

| | |
|---|---|
| **CONCEITO** | custo da corrida |
| **FONTE A** | `pedido/orquestrador.py:234-239` — grava `COST_USD = 0` para ensaio seco e rota gratuita, e `"NAO SEI"` no resto; o comentário explica que escrever `NÃO SEI` numa corrida que não abriu ligação seria *inventar dívida* |
| **FONTE B** | `medidas/padrao_da_coleta.py` — a regra `CORRIDA_GUARDA_O_CUSTO` conta como dívida toda corrida cujo `COST_USD` esteja em `('NOT_PRESERVED', None, '', 'NAO SEI')` |
| **CONFLITO** | APARENTE, e as duas estão certas. `0` é medição («não gastou»); `NÃO SEI` é confissão («gastou e não guardei»). |
| **RESOLUÇÃO CANÔNICA** | **as duas ficam**, e a Bíblia escreve a distinção: `0` é um valor medido, `NÃO SEI` é ausência de medição, `NOT_PRESERVED` é confissão de perda. Três coisas, três palavras. |
| **LEI** | COL-LAW-019 · COL-LAW-035 |
| **AÇÃO** | nenhuma. |

---

## C-007 · `ITEM_COUNT_RAW` fica `NÃO SEI` quando o executor corre

| | |
|---|---|
| **CONCEITO** | reconciliação entre portas |
| **FONTE A** | `pedido/orquestrador.py:240-241` — `ITEM_COUNT_RAW` e `ITEM_COUNT_NORMALIZED` nascem `"NAO SEI"` e só são preenchidos **se a colheita for encontrada e passar pela admissão** |
| **FONTE B** | `medidas/REGRA-DE-COLETA-EXTERNA-EAME.md` §14-B e `medidas/portao.py` — a corrida tem de medir rendimento |
| **CONFLITO** | REAL mas honesto. Quando o executor larga o resultado num sítio que o orquestrador não encontra, a corrida diz `COLHEITA_NAO_ENCONTRADA` e o rendimento fica `NÃO SEI` — em vez de dizer zero. Isso está **certo** pela lei do UNKNOWN, e ao mesmo tempo significa que hoje **não há reconciliação `DISCOVERED → EMITTED → RAW_LANDED → READY`** em lado nenhum. |
| **RESOLUÇÃO** | a lei (COL-LAW-023) é canônica; a implementação está `PARTIAL`. `NÃO SEI` continua sendo a resposta certa enquanto a contagem não existir — o defeito é a contagem não existir, não a resposta. |
| **AÇÃO** | gap G-03. |

---

## C-008 · Duas listas de fontes respondendo «que fontes temos»

| | |
|---|---|
| **CONCEITO** | catálogo de fontes |
| **FONTE A** | `docs/fontes/ATLAS-DE-FONTES-EAME.md` — 37 fontes registradas |
| **FONTE B** | `candidatas/ITALY-SOURCE-MASTER-V1.json` — 54 fontes italianas, com campos que o atlas não tem (`WHAT_IT_DOES_NOT_PROVE`) |
| **CONFLITO** | **JÁ RECONHECIDO no próprio mapa.** O componente `C-IT-CATALOGO` em `system-map/data/architecture.declared.json` diz, com todas as letras: *«duas listas a responder "que fontes temos" são duas verdades, e a segunda envelhece calada. O mapa reconcilia as duas, fonte a fonte.»* |
| **RESOLUÇÃO CANÔNICA** | o mapa é o reconciliador declarado; `system-map/data/sources.generated.json` é a leitura única, e é dela que `pedido/receitas.py` lê. Já está certo. |
| **LEI** | COL-LAW-053 |
| **AÇÃO** | nenhuma. |

---

## RESUMO

| resolução | nº |
|---|---|
| resolvidos por lei madura já existente | **5** (C-002, C-004, C-006, C-007, C-008) |
| resolvidos por precedência entre leis maduras | **1** (C-001 — duas leis contra uma linha) |
| lei canônica sem implementação (não é conflito) | **1** (C-005) |
| ⚠️ **exigem decisão futura do dono** | **1** (C-003 — a grafia do desconhecido) |
