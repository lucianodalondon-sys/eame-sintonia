# CENSO DOS CONTRATOS DE ARTEFATO — O QUE JÁ EXISTE

> Medido em 07/09/2026, antes de escrever uma linha de contrato novo.
> Regra Zero: **procurar antes de criar. Nunca fazer uma segunda verdade.**

---

## POR QUE ESTE DOCUMENTO EXISTE

A tentação, ao começar uma engenharia nova, é desenhar o contrato dos sonhos e
depois descobrir que metade dele já existia — com outro nome, noutra gaveta, já
testado e com consumidores a depender dele. Aí passam a existir duas verdades
sobre a mesma coisa, e a partir daí ninguém sabe qual delas obedecer.

Por isso: primeiro o censo, depois o contrato.

---

## O QUE FOI PROCURADO E O QUE FOI ENCONTRADO

| termo procurado | ficheiros de código que o usam |
|---|---:|
| `SOURCE_LOCATION` | 51 |
| `FACT_LOCATION` | 52 |
| `SHA256` | 32 |
| `PUBLISHED_AT` | 18 |
| `RUN-MANIFEST` | 11 |
| `FACT_TIME` | 11 |
| `RUN_MANIFEST` | 5 |
| `OBSERVED_AT` | 3 |
| `PRONTO-PARA-INTELIGENCIA` | 1 |
| `LIVRO-DE-DECISOES` | 1 |
| `coleta_id` | 1 |
| `ARTIFACT_ID` | **0** |
| `PARENT_ARTIFACT_ID` | **0** |
| `EXECUTOR_VERSION` | **0** |
| `PIPELINE_VERSION` | **0** |
| `COLLECTED_AT` | **0** |
| `READY_FOR_INTELLIGENCE` | **0** (existe em português) |

Lê-se assim: **tempo, geografia e procedência já são lei madura desta casa.**
O que não existe é a ideia de **artefato com identidade e com pai** — e é
exatamente essa a peça que falta para os executores falarem a mesma língua.

---

## FICHA DE CADA CANDIDATO

### 1 · `regras/proveniencia.py` — `CAMPOS_RUN`

| | |
|---|---|
| **PARA QUE SERVE** | descreve uma corrida: quem correu, quando, com que ator, quanto custou, que prova ficou |
| **CAMPOS** | `RUN_ID` `PLATFORM` `ACTOR` `ACTOR_VERSION` `STARTED_AT` `FINISHED_AT` `INPUT` `COUNTRY` `MISSION` `QUERY` `DATASET_ID` `ITEM_COUNT_RAW` `ITEM_COUNT_NORMALIZED` `COST_USD` `SOURCE_VERSION` `STATUS` `ERROR` `CAPTURE_METHOD` `EVIDENCE_PATH` `RAW_EVIDENCE_PATH` `RAW_EVIDENCE_STATE` `OUTPUT_WRITTEN_AT` |
| **DONO** | `regras/proveniencia.py` |
| **CONSUMIDORES** | 11 ficheiros, incluindo o orquestrador, o coletor e o gerador do mapa |
| **DÁ PARA REUSAR** | **SIM, inteiro** |
| **CONFLITOS** | nenhum |
| **CLASSIFICAÇÃO** | **KEEP + EXTEND** |

`ACTOR` / `ACTOR_VERSION` já são, na prática, `EXECUTOR` / `EXECUTOR_VERSION`.
Não se inventa nome novo: usa-se o que já está.

Repare no comentário que já lá estava sobre `OUTPUT_WRITTEN_AT`:

> *«É medida de verdade, mas NÃO é a hora da execução na plataforma — por isso
> vive em campo próprio e nunca é usada como STARTED_AT/FINISHED_AT.»*

A lei de não confundir tempos já está escrita e já foi paga uma vez.

---

### 2 · `data/samples/RUN-MANIFEST.json` — o recibo

| | |
|---|---|
| **PARA QUE SERVE** | a lista de todas as corridas, uma linha por corrida |
| **DONO** | escrito por `orquestrador.guardar_recibo()`, que **acrescenta e nunca reescreve** |
| **CONSUMIDORES** | cinco regras leem-no |
| **DÁ PARA REUSAR** | **SIM** |
| **CLASSIFICAÇÃO** | **KEEP** |

A corrida de derivação desta missão entra aqui. Não se cria segundo manifesto.

---

### 3 · `admissao/admissao.py` — a porta

| | |
|---|---|
| **PARA QUE SERVE** | decide se um item entra: legível? tem origem? tem tempo do fato? pertence ao universo? |
| **RESULTADOS** | `SIM` `NAO` `NAO_SEI` `NAO_SE_APLICA` `ERRO` |
| **O QUE O ITEM PRECISA DE TER** | `texto` (ou `title`/`nome`) · `source_id` (ou `fonte`/`url`) · `fact_time` (ou `data`/`published_at`) |
| **DÁ PARA REUSAR** | **SIM, sem tocar** |
| **CLASSIFICAÇÃO** | **KEEP — não redefinir** |

⚠️ Consequência já visível: um PDF sem data conhecida vai dar **NAO_SEI** na
porta. Isso está **certo**. Não se inventa `fact_time` para o fazer passar.

---

### 4 · `admissao.pronto_para_inteligencia()` — o contrato de saída

| | |
|---|---|
| **CAMPOS** | `ESTADO` `ITEM_ID` `UNIVERSO` `TEXTO` `SOURCE_ID` `SOURCE_LOCATION` `FACT_LOCATION` `FACT_TIME` `CAPTURED_AT` `CORRIDA` `ADMITIDO_POR` |
| **SAI PARA** | `data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json` |
| **DÁ PARA REUSAR** | **SIM** |
| **CLASSIFICAÇÃO** | **KEEP** |

É este o `READY` desta casa. Não se cria um `READY_FOR_INTELLIGENCE` novo em
inglês ao lado de um que já existe em português.

> ⚠️ **CORRIGIDO EM 2026-09-09.** Esta entrada dizia «e já tem consumidor».
> Não tem. Medido por [`provas/a_fronteira_da_coleta.py`](../../provas/a_fronteira_da_coleta.py):
> **2 produtores** (`orquestrador/orquestrador.py`, que é CLI e não corre em
> workflow nenhum, e uma prova), **0 consumidores**, e a pasta de destino
> `data/samples/PRONTO-PARA-INTELIGENCIA/` **não existe na árvore**.
> A classificação `KEEP` mantém-se — o contrato é bom e é único. O que falta
> é alguém entregar nele e alguém recolher dele.
> **DECLARADO ≠ IMPLEMENTADO ≠ PRODUZIDO ≠ CONSUMIDO.**

---

### 5 · `data/samples/LIVRO-DE-DECISOES.json`

| | |
|---|---|
| **PARA QUE SERVE** | guarda **todas** as decisões, não só as que passaram, com regra, versão, motivo e prova |
| **DÁ PARA REUSAR** | **SIM** |
| **CLASSIFICAÇÃO** | **KEEP** |

---

### 6 · Os 6 ficheiros `.txt` ao lado dos PDF

| | |
|---|---|
| **PARA QUE SERVE** | texto tirado de PDF, à mão, sem registo de quem, quando, nem como |
| **CAMPOS** | nenhum. É texto solto num ficheiro |
| **DONO** | ninguém |
| **CONSUMIDORES** | nenhum medido |
| **DÁ PARA REUSAR** | **como conteúdo, sim. Como contrato, não** |
| **CLASSIFICAÇÃO** | **LEGACY** |

Não se apagam. Ganham ficha de derivado legado, com o que se conseguir provar.

---

## O BURACO, EM UMA FRASE

Existe **corrida** (`RUN`). Existe **decisão** (a porta). Existe **entrega**
(pronto para inteligência). Existe **tempo**, **geografia** e **procedência**.

Não existe **artefato**: a coisa em si, com nome próprio, com impressão
digital, e que sabe dizer de que outra coisa nasceu.

Sem isso, o orquestrador teria de adivinhar o que cada executor produziu — e é
por isso que ligar o control plane agora consolidaria o defeito, em vez de o
corrigir.

---

## O QUE ESTA MISSÃO CRIA, E SÓ ISSO

| | |
|---|---|
| **CRIA** | a ficha de artefato: identidade, impressão digital, pai, derivação, versão |
| **REUSA** | corrida, admissão, livro de decisões, pronto-para-inteligência, tempo, geografia, procedência |
| **NÃO TOCA** | entrada, pedido, receita, orquestrador, SINTONIA SCRAP, botões |

---

## DECISÕES CONSTITUCIONAIS EM FALTA

A Bíblia Canônica da Coleta **não está neste HEAD**
(`BIBLE_STATUS = NOT_IN_THIS_HEAD`). Ficam registadas como
`UNKNOWN / DECISION_REQUIRED`:

| | pergunta sem lei escrita |
|---|---|
| 1 | qual a forma canónica de um `ARTIFACT_ID`? Aqui usa-se uma forma técnica determinística, e ela **não** finge ser identidade da fonte |
| 2 | um derivado de derivado herda o avô, ou só o pai? Esta missão só produz filhos de primeiro grau |
| 3 | `NEEDS_OCR` é estado do artefato ou da corrida? Aqui é do artefato, porque é uma propriedade do documento e não de quem o tentou ler |
