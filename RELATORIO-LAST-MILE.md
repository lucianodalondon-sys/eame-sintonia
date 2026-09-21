# RELATÓRIO — COLLECTION LAST MILE V1

```
CANONICAL_COLLECTION_PROVEN = PARTIAL
```

Dois bloqueios nomeados, os dois **a montante da Sala** e nenhum deles de rede.
Tudo o resto que a missão pediu está provado e medido.

Base: `canonical-micro-v1 @ 4c0c62b3` · branch `last-mile-v1` · 2026-09-21.

---

## 0 · POLÍTICA DE MODELO

```
REQUESTED_MODEL           = claude-opus-5
ACTUAL_LLM_MODEL          = claude-opus-5
MODEL_SELECTION_SUPPORTED = YES
FABLE_USED                = NO
```

**Medido, não declarado.** Não bastava ler o que o meu próprio prompt diz de mim.
O diário desta sessão em `.claude/projects/…/364063e4-….jsonl` — o mesmo
identificador que aparece no caminho onde o sistema escreveu a saída dos meus
testes, e portanto é mesmo esta conversa — carimba o modelo em cada resposta:
**47 respostas, 47 vezes `claude-opus-5`, zero de qualquer outro.**

Para hash, SQL, testes, dedup, comparação, estado Git, fila e incrementalidade:
**não foi usado LLM.** Isso é código, e está nos ficheiros de `medidas/`.

---

## 1 · OS DONOS DA CADEIA

| eixo | dono medido |
|---|---|
| `RUN_OWNER` | `orquestrador/orquestrador.py` cunha o `RUN_ID` → tabela `collection_run` |
| `OBSERVATION_OWNER` | `coleta/italy_pilot_collect.mjs` → `data/collection-ledger/italy/observations.ndjson` (append-only) |
| `RAW_OWNER` | `guarda/preservar_coleta.py::preservar()` → tabela `raw_asset` |
| `STORAGE_OWNER` | `guarda/preservar_coleta.py` → tabela `storage_object` |
| `DERIVED_OWNER` | `coleta/ingresso.py::_DONOS_DA_DERIVACAO` → `executor_texto_de_pdf`, `executor_transcricao_midia` |
| `ADMISSION_OWNER` | `admissao/admissao.py::decidir()` → `data/samples/LIVRO-DE-DECISOES.json` |
| `SALA_OWNER` | `admissao/sala_de_espera.py` → tabela `sala_de_espera` |
| ponte NDJSON → porta | `coleta/italy_executor.py::colher()` (traduz sem correr o coletor) |

**Não foi construída uma segunda cadeia.** Tudo o que correu correu por estes donos.

---

## 2 · F1 — O SOBREVIVENTE, MORTO

```
MUTANT_APPLIED = YES        (provado por git diff, não presumido)
MUTANT_KILLED  = YES
```

`regras/motor_de_rota.mjs:114` · `throw new ContratoInvalido("CONTENT_CAPTURE sem CAPTURES")`

| | resultado |
|---|---|
| baseline, sem mutante | 45 PASSOU · 0 FALHOU |
| **com mutante, antes da prova nova** | **45 PASSOU · 0 FALHOU — SOBREVIVEU** |
| com mutante, depois da prova nova | 46 PASSOU · **1 FALHOU** |
| sem mutante, depois | 47 PASSOU · 0 FALHOU |

### Porque sobrevivia

Havia `assert.throws` para quatro leis vizinhas — `MAGIA`, `STATIC_ENDPOINT` sem
URL, `CUSTOM_ADAPTER` sem `ADAPTER_ID`, `FROM: "TELEPATIA"`. Nenhum para *esta*.
E todas as provas de `CONTENT_CAPTURE` partiam do mesmo molde `ID_URL`, que
**já traz o bloco `CAPTURES` preenchido** — ninguém perguntou o que acontece
quando ele falta.

> **COBRIR OUTRA ESTRATÉGIA NÃO É COBRIR ESTA LEI.**

A prova nova mede as três formas de não ter `CAPTURES`, que não caem no mesmo sítio:

| forma | sem o guarda |
|---|---|
| ausente / `null` | `TypeError` — contrato inválido a parecer avaria do motor |
| `{}` com molde literal | **passa verde**; aqui o `throw` é o único guarda no caminho |

Com **controlo positivo**: `CONTENT_CAPTURE` bem declarado passa e identifica.
Sem ele, a prova seria satisfeita por um motor que recusasse *todo* o
`CONTENT_CAPTURE` — e recusar tudo também mata o mutante sem servir para nada.

---

## 3 · F2 — A COORTE. O UNIVERSO NÃO É A COORTE

**Correção a uma medição minha.** O primeiro censo mediu 445 observações em 58
corridas desde 14-09. Isso é o **universo**; `205 com bytes` não são «205 dos 85».
A coorte sai agora dos **manifestos** (`medidas/CORRIDA-CANONICA-RUN*.json`), onde
cada corrida declarou fonte a fonte o `RUN_ID` que cunhou — e não de inferência
pela hora do identificador.

| corrida | runs | obs | c/bytes | integridade | `SHA_MISMATCH` | resultados |
|---|---|---|---|---|---|---|
| RUN1 | 6 | 6 | 0 | 0 | 0 | `DISCOVERY_FAILED` 6 |
| RUN1B | 6 | 85 | 0 | 0 | 0 | `IDENTITY_FAILED` 85 |
| RUN1C | 6 | 85 | 85 | 85 | 0 | `NEW_DOCUMENT` 79 · `SEMANTIC_ID_CHANGED_SAME_BYTES` 6 |
| RUN2 | 6 | 85 | 85 | 85 | 0 | `DOCUMENT_CHANGED_IN_PLACE` 83 · `SEEN_AGAIN` 2 |

```
TARGET_OBSERVATIONS        261
TARGET_WITH_BYTES          170
TARGET_BYTES_INTEGRITY_OK  170
SHA_MISMATCH                 0
```

A RUN1B tem **85 sha e zero bytes**: o coletor descarregou, falhou a identidade,
deitou fora os bytes e guardou o hash.

### Os quatro eixos, que não são o mesmo eixo

```
170 OBSERVAÇÕES · 85 DOCUMENTOS · 168 BLOBS · 168 FICHEIROS
```

`RUN ≠ OBSERVATION ≠ CONTENT ≠ STORAGE_OBJECT` ·
`SHA256` identifica bytes, **não** identifica observação · `storage_path` é
endereço, não identidade.

---

## 4 · F3 — OS BYTES JÁ CÁ ESTAVAM

```
EXISTING_BYTES_REUSED          = 170
NETWORK_REQUIRED_FOR_LAST_MILE = NO
```

### Mapeamento provado, do lado do disco

A direcção importa: partir do livro pergunta «as observações têm bytes?»; partir
do disco pergunta «estes bytes são de quem?». Só a segunda mostra ficheiro órfão.

```
FICHEIROS_NO_ARMAZEM              178   (170 html · 7 pdf · 1 csv)
LOCAL_BYTES_MATCHED               178
LOCAL_BYTES_UNMATCHED               0
FICHEIROS_DA_COORTE               168
OBSERVATIONS_WITHOUT_LOCAL_BYTES   91   (6 RUN1 + 85 RUN1B)
```

**`170` não é `2 × 85`.** São 168 ficheiros da coorte — 85 da RUN1C mais 83 novos
da RUN2 (os 2 `SEEN_AGAIN` reusam o ficheiro da RUN1C) — mais 10 de corridas
anteriores que não pertencem a esta população.

Prova: `sha256` do ficheiro `==` `RAW_SHA256` do livro. **Nome e pasta não contam
como prova**: o caminho carrega o `DOCUMENT_ID` e seria fácil «deduzir» o dono,
mas deduzir não é provar que *estes* bytes são daquela observação. Ficheiro sem
identidade provada ficaria `UNMATCHED` — e `UNMATCHED` é resposta, não convite a
adivinhar.

---

## 5 · F4 — PORQUE A SEGUNDA VISITA DESCARREGOU TUDO

### O defeito, na linha

```
italy_pilot_collect.mjs:474   const r = await baixar(alvo.url)      ← DESCARREGA
italy_pilot_collect.mjs:502   const mesmoDoc = anterior.filter(…)   ← e só AQUI
                                                                     pergunta se já conhecia
```

> **REUTILIZAR O ARMAZÉM DEPOIS DO DOWNLOAD NÃO É INCREMENTALIDADE: A REDE JÁ FOI GASTA.**

### Porque comparar bytes não salvava nada

83 dos 85 saíram `DOCUMENT_CHANGED_IN_PLACE`. Diferença real entre as duas
capturas dos **mesmos** artigos: **374 linhas em 86.441 (0,43%), e zero texto
editorial.** As 374 classificadas uma a uma:

| | linhas |
|---|---|
| carimbo de hora / nonce / sessão | 197 |
| marcação de máquina | 55 |
| nonce do WordPress Download Manager | 52 |
| farol de analytics com `hid` aleatório | 52 |
| **contador de visitas da página** (`<div class="views">365</div>` → `367`) | **14** |
| token do Drupal | 6 |

As duas visitas que fizeram o contador subir **foram as nossas**.

> **A NOSSA VISITA DEIXA PEGADA NA PÁGINA. COMPARAR SHA DEPOIS DE VISITAR É MEDIR A PRÓPRIA PEGADA.**

Por isso `decidirSobreDetalhe()` **não recebe bytes, nem sha, nem corpo, nem
resposta** — a assinatura é a lei. Há prova que lhe atira os quatro venenos
(incluindo o contador) e a decisão não se mexe.

### A regra — `regras/incrementalidade.mjs`

```
INDEX                          revisita-se sempre
DETAIL nova                    FETCH
DETAIL conhecida com sucesso   SKIP_KNOWN por omissão
```

Revisitar exige **razão nomeada** do vocabulário fechado de cinco, e nenhuma sexta:
`CONTRACT_DECLARES_MUTABLE` · `TTL_EXPIRED` · `PREVIOUS_ATTEMPT_FAILED` ·
`CONDITIONAL_REQUEST_AVAILABLE` · `CANONICAL_EVIDENCE_REQUIRES`.

**Não lê `UPDATE_BEHAVIOR`**, que é prosa (172 dos 186 contratos dizem `"NAO SEI"`,
os outros dizem frases). Lê `RECOLLECTION`, vocabulário fechado, que nenhum
contrato tem hoje — logo todos caem em `UNKNOWN`, que por lei significa SKIP.

---

## 6 · F5 — ETag / LAST-MODIFIED: MEDIDO, E DECLARADO COMO NÃO-SABIDO

```
OBSERVACOES_COM_ETAG_GRAVADO           = 0 de 445
OBSERVACOES_COM_LAST_MODIFIED_GRAVADO  = 0 de 445
CONDITIONAL_REQUEST_IMPLEMENTED        = NO
COLECTOR_PEDE_VALIDADOR                = NO
SOURCES_OFFER_ETAG                     = NÃO SEI
CAPACIDADE_INVENTADA                   = NO
```

As três respostas são diferentes, e só a terceira é verdade aqui:

- «as fontes **não oferecem**» → afirmação sobre a **fonte**
- «**nós** não usamos» → afirmação sobre **nós**
- «**não sei**» → nunca se perguntou ← **é esta**

O coletor nunca enviou `If-None-Match` nem `If-Modified-Since`. Saber se as fontes
oferecem exige um pedido à rede, que esta missão não autoriza. Sem validador
guardado, `CONDITIONAL_REQUEST_AVAILABLE` nunca dispara, e um `REVALIDATE` sem
validador confessa `CONDICIONAL_POSSIVEL = false` em vez de prometer poupança que
não acontece.

---

## 7 · F6 — RUN A E RUN B, POPULAÇÃO REAL, ZERO REDE

Os 85 endereços reais da RUN1C. Transporte **falso** que conta cada chamada e
serve bytes do disco; o módulo não importa `https` nem `fetch`.

| | RUN A | RUN B |
|---|---|---|
| `INDEX_REQUESTS` | 6 | **6** |
| `DETAIL_NEW` | 85 | **0** |
| `DETAIL_SKIPPED_KNOWN` | 0 | **85** |
| `DETAIL_REVALIDATED` | 0 | **0** |
| `DETAIL_REFETCHED` | 0 | **0** |
| `UNNECESSARY_REFETCHES` | 0 | **0** |
| portas batidas (contador) | 85 | **0** |

Coerente: portas batidas `==` `DETAIL_REQUESTS` nas duas corridas.
O coletor de hoje, na mesma população: `DETAIL_REQUESTS_RUN_B = 85`, skip `0`.

---

## 8 · F7/F8 — RAW E STORAGE: PROVADOS

Corrido pela porta canónica, sem rede:

```
py medidas/corrida_sem_rede.py -- --so-a-porta
   --colheita-da-corrida=<RUN_ID> --filtro fonte=<X> --filtro universo=<Tn>
```

6 corridas · 85 itens · todas `CORRIDA SUCCESS` · persistência **OPERACIONAL**
(`127.0.0.1:54330/sala_italia`).

| tabela | antes | depois | delta |
|---|---|---|---|
| `collection_run` | 369 | 376 | +7 |
| `raw_asset` | 1072 | **1159** | **+87** |
| `storage_object` | 938 | **1023** | **+85** |
| `derived_artifact` | 758 | 758 | **+0** |
| `documento_estruturado` | 754 | 754 | +0 |
| `sala_de_espera` | **46** | **46** | **0** |

```
RAW_ASSET_BEFORE 1072 · AFTER 1159 · CREATED 87 · REUSED 0 · FAILED 0
STORAGE_CREATED 85 · STORAGE_REUSED 2 · STORAGE_DUPLICATES_PREVENTED 2
SHA_MISMATCH = 0            preserved 87/87
identity_state = FORWARD_IDENTIFIED (87/87) · media_type = text/html (87/87)
```

### A lei provou-se por acidente útil

Corri o envelope de `IT-T7-043` **duas** vezes. `raw_asset +2` e
`storage_object +0`: as observações novas (1075, 1076) apontam para os objectos
que já lá estavam (1073, 1074).

> **NOVA RUN SOBRE OS MESMOS BYTES CRIA OBSERVAÇÃO NOVA SEM STORAGE NOVO.**
> Medido, não afirmado.

### Uma pré-condição que foi preciso resolver, com autorização do dono

A porta recusava os 85: `pedido/receitas.py` declarava `italia-recorrente` em
T2/T3/T4/T6/T9, e os 85 são de **T10/T7/T5**. O plano respondia *«NÃO SEI COMO:
nenhum executor desta casa declara saber percorrer a rota delas»* — e era falso,
porque o mesmo executor tinha acabado de percorrer as seis fontes.

Não é código novo: é a declaração que faltava, o mesmo caso que o registo de T3
já descreve no próprio ficheiro. `filtros_por_omissao` nomeia **uma** fonte
provada por universo; as restantes continuam a exigir `--filtro fonte=`.
`IT-T5-001..005` continuam sem executor, e o aviso que o diz fica inteiro:
**uma fonte provada não apaga cinco por provar.**

---

## 9 · F8 — DERIVED: A CORREÇÃO MAIS IMPORTANTE DESTE RELATÓRIO

### Eu escrevi `NOT_APPLICABLE` no commit `a4e2e25b`. Estava errado

A história não foi reescrita: o commit fica, e a correção vive no commit
seguinte (`1946213e`) e aqui.

O dono desconfiou da palavra e mandou provar ou refutar com código. **Refuta-se.**

`coleta/texto_fonte.py::limpar(dados, ctype)` **já é um extrator de texto de
HTML**, e o docstring dele nomeia o nosso próprio problema:

> *«a ficha do GIRE chega com menu, CSS e **contador de visitas** em volta do
> conteúdo. Este arquivo devolve só o texto.»*

Prova sobre os bytes reais, do disco, sem rede e sem ferramenta externa:

```
100.970 bytes de HTML  →  12.701 caracteres de texto, título à cabeça
nos 85: TEXTO_EXTRAIVEL 85/85 · média 6.328 caracteres · 0 falhas
```

### A distinção, que é o centro da questão

| etiqueta | significado | é esta? |
|---|---|---|
| `NOT_APPLICABLE` | a etapa **não é para este material**, por contrato | ❌ não |
| `NOT_IMPLEMENTED` | a etapa aplica-se, **a capacidade não existe** | ❌ não |
| **`MISSING_ROUTE`** | **a capacidade existe, falta o caminho** | ✅ **sim** |
| `BLOCKED_BY_CONTRACT` | um contrato proíbe | ❌ não |
| `FAILED` | correu e falhou | ❌ não |

```
MATERIAL_CLASS         = text/html
RAW_OWNER              = guarda/preservar_coleta.py::preservar()
DERIVED_APPLICABLE     = YES
WHY_DERIVED_APPLICABLE = o que a derivação produz chama-se TEXT_EXTRACTED,
                         a admissão exige `texto` para responder `legivel`,
                         e o HTML tem texto — provado offline nos 85
ADMISSION_INPUT_TYPE   = RAW (aceite) ou DERIVED
ADMISSION_OWNER        = admissao/admissao.py::decidir()
CANONICAL_PATH         = RAW → [DERIVED em falta] → ADMISSION → SALA
CLASSIFICACAO          = MISSING_ROUTE
```

`coleta/ingresso.py::_DONOS_DA_DERIVACAO` tem dois executores —
`executor_texto_de_pdf` (`application/pdf`) e `executor_transcricao_midia`
(`audio/*`, `video/*`). **Nenhum declara `text/html`**, e por isso
`executor_para('text/html')` devolve `None`.

**O estado atual é defeito**, e diz-se assim.

```
DERIVED_BEFORE 758 · AFTER 758 · CREATED 0 · REUSED 0 · FAILED 0
DERIVED_MISSING_ROUTE 85
```

Razão técnica por item, nomeada: `SOURCE_ID`, `OBSERVATION_ID`, `RAW_ASSET_ID` e
`text/html sem executor declarado` — em `medidas/PORQUE-A-SALA-NAO-RECEBEU-V1.json`.
**Nenhum `UNKNOWN` genérico onde há causa conhecida.**

---

## 10 · F9/F10 — ADMISSION: A ROTA EXISTE, E FOI USADA

`admissao/admissao.py:439` aceita `artifact_type` em `("RAW", "DERIVED")` → estágio
`DOCUMENTO`. **A rota RAW → ADMISSION existe e foi usada**: as 85 decisões registam
`"estagio": "DOCUMENTO"`. Não falta rota de admissão — falta o texto.

```
ADMISSION_SIM 0 · NAO 0 · NAO_SEI 85 · NAO_SE_APLICA 0 · ERRO 0
T7 42 · T10 39 · T5 4     regra `legivel`, motivo único nas 85
```

> *«o item veio sem texto nenhum. Sem conteúdo não dá para dizer se serve — e
> "não consegui ver" não é "não serve".»*

A admissão **não reprovou por `FACT_TIME`/`FACT_LOCATION`/`CROP` em `UNKNOWN`**.
Nem chegou lá: parou no primeiro portão. Conforme F9, `UNKNOWN` nesses campos não
impede a entrada de evidência válida — e não impediu.

### O SEGUNDO BLOQUEIO, que só apareceu ao simular a porta inteira

```
admissao.PERGUNTAS_DO_UNIVERSO = T3, T4, T5, T7, T9        ← T10 NÃO está lá
```

Para os 39 itens T10 a porta responde, com todas as letras:

> *«não há regra escrita do que conta como «T10». Sem regra, esta porta não
> inventa uma.»* → `NAO_SE_APLICA`

```
NO_ADMISSION_RULE_FOR_UNIVERSE = T10 (39 itens)
```

### E um erro meu, apanhado no mesmo medidor

A primeira versão do meu simulador chamava só os portões do estágio e deu
**`SIM 85`**. Faltava-lhe o último degrau (`_do_universo`). Trocado pelo dono
único — `admissao.decidir()` — o número honesto é outro:

> **UMA SIMULAÇÃO QUE SALTA UM DEGRAU NÃO SIMULA A PORTA:
> SIMULA A PARTE DA PORTA QUE EU JÁ SABIA RESPONDER.**

```
SE HOUVESSE DERIVADOR DE HTML:  SIM 12 · NAO_SEI 34 · NAO_SE_APLICA 39
```

| fonte | universo | SIM | NAO_SEI | NAO_SE_APLICA |
|---|---|---|---|---|
| `IT-T5-049` | T5 | **4** | — | — |
| `IT-T7-017` | T7 | **4** | 26 | — |
| `IT-T7-042` | T7 | **3** | 7 | — |
| `IT-T7-043` | T7 | **1** | 1 | — |
| `IT-T10-018` | T10 | — | — | 30 |
| `IT-T10-022` | T10 | — | — | 9 |

**Doze documentos entrariam na Sala, e não 85.** O derivador não é o único
bloqueio, e a admissão continua a ser um juízo — não um carimbo.

---

## 11 · F11 — SALA

```
SALA_BEFORE = 46      (remedido no Postgres)
SALA_AFTER  = 46
SALA_DELTA  = 0
```

```
INSERT manual   = 0      SQL ad hoc = 0
fixture         = 0      bypass     = 0
```

Nenhuma linha foi escrita na Sala por fora da cadeia. Cópia de segurança tirada
antes de qualquer escrita:
`sintonia-sala-italia/backups/pre-lastmile-20260921-180518.dump`.

### PARETO DA CAUSA, POR ITEM — `SALA_DELTA = 0`

> **«NÃO ENTROU» NÃO É UMA CAUSA. É A AUSÊNCIA DE UMA.**

| causa próxima | causa raiz | itens | fontes |
|---|---|---|---|
| `ADMISSION_NAO_SEI` | **`MISSING_ROUTE`** | **46** | `IT-T7-017` 30 · `IT-T7-042` 10 · `IT-T5-049` 4 · `IT-T7-043` 2 |
| `ADMISSION_NAO_SEI` | **`NO_ADMISSION_RULE_FOR_UNIVERSE`** | **39** | `IT-T10-018` 30 · `IT-T10-022` 9 |

```
NO_ADMISSION_ROUTE      0   ← a rota RAW→ADMISSION existe e foi usada
CONTRACT_BLOCK          0
NOT_APPLICABLE          0   ← retirado: era MISSING_ROUTE
ADMISSION_NAO           0
ADMISSION_NAO_SEI      85   (causa próxima de todos)
ADMISSION_ERROR         0
MISSING_REQUIRED_FIELD 85   (o campo é `texto`)
```

A causa próxima não é a causa raiz, e reportar só a próxima manda quem lê
consertar o sítio errado.

---

## 12 · F12 — TEMPO, LUGAR, CULTURA: MEDIDOS, NUNCA FABRICADOS

```
FACT_TIME_PROVEN    = 0        FACT_TIME_UNKNOWN    = 85
SOURCE_DATE_ISO presente = 0 de 85
FACT_LOCATION_PROVEN = 0       FACT_LOCATION_UNKNOWN = não medido
REGION_PROVEN        = 0       REGION_UNKNOWN        = não medido
CROP_PROVEN          = 0       CROP_UNKNOWN          = não medido
```

`FACT_TIME` traz a confissão escrita em 85 de 85:
*«UNKNOWN — identidade pelo endereço; a fonte não expõe data do facto»*.

```
FACT_TIME que pareça um instante (fallback de PUBLISHED_AT) = 0
DETAIL_URL que CONTÉM data — a tentação                     = 2
destes que viraram FACT_TIME                                = 0
```

`FACT_LOCATION` / `REGION` / `CROP`: **não medidos**, porque quem os mediria é o
degrau STRUCTURED, que não correu por não haver derivado. Escrever `0/85` daria
por medido o que não foi perguntado. `PUBLISHED_AT ≠ FACT_TIME` ·
`SOURCE_LOCATION ≠ FACT_LOCATION` — nenhum herdou por fallback.

---

## 13 · F13/F14 — AS DUAS LEIS REGISTADAS

```
VALID_EVIDENCE ≠ OPPORTUNITY_ELIGIBLE
```

Intelligence **não** foi implementada e nenhuma Opportunity foi gerada.

```
ROBOTS_DISALLOW ≠ ROBOTS_UNREADABLE
```

Avaliado por visita, nunca propriedade eterna da fonte. Os manifestos das
corridas da coorte registam `ROBOTS_ALLOW` com a hora da leitura
(`LIDO_EM`), fonte a fonte. Nenhuma leitura de robots foi feita nesta missão —
não houve rede.

---

## 14 · F15 — RED TEAM, COMEÇANDO PELO CÓDIGO NOVO

```
MUTANTES_APLICADOS = 22      MORTOS = 22      SURVIVORS = 0
```

**Um sobreviveu à primeira, e era meu.**

`M-INC-08`: tirar `SEEN_AGAIN` de `RESULTADOS_COM_DOCUMENTO` deixava a suite em
22 PASSOU · 0 FALHOU. A causa estava no teste que eu escrevera:

```js
for (const r of RESULTADOS_COM_DOCUMENTO)   // ← LÊ A LISTA QUE ESTÁ A TESTAR
```

> **UMA PROVA QUE LÊ A LISTA SOB ATAQUE NÃO PROVA A LISTA: PROVA QUE O CICLO SABE ANDAR.**

Corrigido com os nove nomes escritos à mão e `deepEqual` contra a lista do módulo
— assim apagar reprova, e acrescentar em silêncio também. Reataque: morto.

| mutante | alvo | resultado |
|---|---|---|
| `M-CAP-01` `CONTENT_CAPTURE` sem `CAPTURES` | motor | MORTO 46·1 |
| `M-INC-01` falha conta como conhecido | regra | MORTO 19·3 |
| `M-INC-02` revisita sempre (DETAIL rebaixado sem justificação) | regra | MORTO 12·10 |
| `M-INC-03` inventa o pedido condicional | regra | MORTO 12·10 |
| `M-INC-04` lê prosa do contrato | regra | MORTO 21·1 |
| `M-INC-05` TTL ilegível expira | regra | MORTO 21·1 |
| `M-INC-06` vocabulário aberto | regra | MORTO 21·1 |
| `M-INC-07` ordem do livro ignorada | regra | MORTO 21·1 |
| `M-INC-08` `SEEN_AGAIN` fora da lista | regra | **SOBREVIVEU → corrigido → MORTO 21·2** |
| `M-INC-08b/c` `BASELINE_DOCUMENT` / `IDENTITY_FAILED` fora | regra | MORTO 22·1 |
| `M-INC-09` índice deixa de se revisitar | regra | MORTO 21·1 |
| `M-INC-10` censo esconde refetch sem razão | regra | MORTO 21·1 |
| `M-INC-11` SKIP passa a bater à porta | regra | MORTO 21·1 |
| `M-INC-12` TTL negativo aceite | regra | MORTO 21·1 |
| `M-MOT-02` `FACT_TIME = PUBLISHED_AT` | motor | MORTO 46·1 |
| `M-MOT-03` SHA/URL vira identidade de observação | motor | MORTO 46·1 |
| `M-MOT-04` a entrada do índice vira matéria (homepage) | motor | MORTO 46·1 |
| `M-MOT-05` activos/paginação/feed viram matéria | motor | MORTO 46·1 |
| `M-MOT-06` `MATCH` fora do vocabulário aceite | motor | MORTO 46·1 |
| `M-MOT-07` `EMPTY_LIST` calado | motor | MORTO (asserção nomeada) |

**Ataques da lista que NÃO foram tentados, e porquê** — declarados em vez de
fingidos:

| ataque | razão |
|---|---|
| `READY_LEGACY` entra · `HUMAN_REVIEW` entra · `robots unreadable` vira `disallow` | vivem em `curadoria/`, que o HARD STOP desta missão põe fora de alcance |
| `storage duplica os mesmos bytes` | **coberto por medição ao vivo**: `STORAGE_DUPLICATES_PREVENTED = 2` |
| `RAW salta para a Sala` · `admissão ignorada` | as guardas que os detectariam já chegam vermelhas ao trunk (7 falhas + 5 erros de base), e não servem de detector limpo |
| `FACT_LOCATION = SOURCE_LOCATION` | **não há código a mutar**: a regra existe em prosa nos contratos e nenhum código a executa |

---

## 15 · F16 — ZERO REDE, INSTRUMENTADA

```
NETWORK_ALLOWED  = NO
NETWORK_REQUESTS = 0        em 7 corridas da porta canónica
DNS_LOOKUPS_FORA = 0
```

`medidas/corrida_sem_rede.py` remenda `socket.connect`, `connect_ex`,
`getaddrinfo` e `subprocess.Popen` **dentro do processo da porta** — chamada por
import, não por `subprocess`, para herdar os remendos.

**O instrumento foi provado antes de valer como prova:** uma ligação a
`93.184.216.34:80` foi apanhada e travada; o loopback passou; o DNS ficou
registado. Loopback contado à parte — a bancada não é egresso.

Subprocessos contados (não escondidos): `git log` e `psql`, porque um filho nasce
com interpretador limpo e **não** herda os remendos.

O coletor em prova usa transporte falso injectável. **Não se dependeu do portão
para impedir a rede** — a corrida de prova não tem por onde lá chegar.

---

## 16 · REGRESSÃO E INTEGRIDADE

```
BASELINE_CURADORIA = 279 OK        DEPOIS = 279 OK        NEW_FAILURES = 0
regras/motor_de_rota_test.mjs      45 → 47 PASSOU · 0 FALHOU
regras/incrementalidade_test.mjs   23 PASSOU · 0 FALHOU (novo)
```

Livro e armazém **não se mexeram** durante as medições: md5 de
`observations.ndjson` idêntico antes e depois, 178 ficheiros antes e depois.

---

## 17 · VEREDICTO

| critério | estado |
|---|---|
| `CONTENT_CAPTURE_MUTANT_KILLED` | ✅ YES |
| `INCREMENTALITY_RULE_PROVEN` | ✅ YES (85 → 0) |
| `NETWORK_REQUESTS` | ✅ 0 |
| `RAW_PROVEN` | ✅ YES (+87) |
| `STORAGE_PROVEN` | ✅ YES (+85, 2 dedup) |
| `DERIVED_APPLICABILITY_PROVEN` | ✅ YES — e é `MISSING_ROUTE`, não `NOT_APPLICABLE` |
| `DERIVED_PROVEN` | ❌ NO — rota em falta |
| `ADMISSION_PROVEN` | ✅ YES (85 decisões, `NAO_SEI` justificado) |
| `SALA_CANONICAL_WRITE_PROVEN` | ❌ NO — `SALA_DELTA = 0` por duas causas provadas |
| `LEGACY_LEAK` | ✅ 0 |
| `BYPASS` | ✅ 0 |
| `RED_TEAM_SURVIVORS` | ✅ 0 |
| `NEW_FAILURES` | ✅ 0 |

```
CANONICAL_COLLECTION_PROVEN = PARTIAL
```

**Os dois bloqueios, nomeados:**

1. **`MISSING_ROUTE`** — nenhum executor de derivação declara `text/html`, e a
   peça de conversão **já existe na árvore** (`coleta/texto_fonte.py::limpar`).
   Afecta **46** itens (T7, T5).
2. **`NO_ADMISSION_RULE_FOR_UNIVERSE`** — `admissao.PERGUNTAS_DO_UNIVERSO` não tem
   régua para **T10**. Afecta **39** itens.

Resolvidos os dois, **12 documentos** entram na Sala — medido a seco, não estimado.

---

## 18 · EM PALAVRAS SIMPLES

Imagine um armazém que recebe jornais e os arquiva.

**O que já funcionava, e continua.** Os jornais chegaram: **85 páginas de notícia
italianas**, guardadas em disco, cada uma com a sua impressão digital conferida
uma a uma. Nenhuma falta, nenhuma está trocada. E esta semana não foi preciso ir
buscar nenhuma outra vez — tudo o que fiz, fiz com o que já estava na prateleira.

**O primeiro problema, que era caro e ninguém via.** O nosso mensageiro ia ao
jornal, trazia a página, e só depois é que olhava para a prateleira para ver se
já a tinha. **Ele pagava a viagem para descobrir que não precisava dela.** Pior:
ele comparava a página nova com a antiga e concluía que tinha mudado — quando o
que mudava era só o contador de visitas no canto da página, *que subia porque ele
tinha acabado de a visitar*. Ele media a própria pegada e chamava-lhe notícia.
Agora ele olha para a prateleira **primeiro**. Na segunda passagem: **85 viagens
antes, zero agora.**

**O segundo problema — e é aqui que eu me enganei, e o senhor apanhou-me.**
Eu disse-lhe que a máquina de passar o jornal a texto «não se aplica» a estas
páginas. Isso queria dizer *«não é preciso»*. **Estava errado, e a diferença é
enorme:**

- *«não é preciso»* significa: está tudo bem, siga.
- *«ainda não sabemos fazer»* significa: falta trabalho, e alguém tem de o fazer.

A verdade é a terceira, e é a melhor das três: **a máquina já existe. Está
guardada na despensa e ninguém a ligou à linha de montagem.** Está num ficheiro
desta mesma casa, e eu liguei-a à mão para provar: pus-lhe uma página de 100 mil
letras de código e ela devolveu **12.701 letras de notícia limpa, com o título à
cabeça**. Fez isso nas 85 páginas, sem ligar a internet. Só falta uma ligação —
como um aparelho comprado, testado, e que ainda está na caixa ao lado da tomada.

**O terceiro problema, que só apareceu depois.** Sem texto, o porteiro do arquivo
não consegue ler o jornal e diz *«não sei se isto serve»* — e tem toda a razão:
«não consegui ver» não é «não serve». Mas quando eu simulei o que aconteceria
**com** o texto, descobri outra coisa. O porteiro tem uma lista de assuntos que
sabe julgar — pragas, regulamentação, ciência, rede técnica, concorrentes. **Um
dos assuntos destes jornais, mercado, não está na lista dele.** E ele é honesto:
*«não há regra escrita do que conta como mercado. Sem regra, esta porta não
inventa uma.»* São **39 das 85 páginas** paradas por aí.

**Quantas entraram no arquivo? Zero.** As 85 chegaram ao balcão, foram
registadas, os bytes ficaram guardados com a impressão digital — isso ficou
provado e está no sistema. Mas nenhuma passou a porta.

**Quantas entrariam se as duas peças estivessem no sítio? Doze.** Não 85. E isto
também é importante que se diga: mesmo com o texto, o porteiro lê e decide. De
46 páginas que ele consegue julgar, diz «sim» a 12 e «não tenho a certeza» a 34.
**Ele julga, não carimba.** Se eu lhe tivesse dito 85, tinha-lhe vendido uma
promessa em vez de uma medição — e foi isso que quase aconteceu: a minha primeira
simulação saltou um degrau do porteiro e deu 85. Refiz com o porteiro inteiro.

**A Collection pode ir para produção?** Metade dela, sim, e essa metade é
sólida: ir buscar, guardar, não repetir viagem, registar com impressão digital —
está provado contra o sistema a sério, com 87 registos novos. A outra metade —
pôr o material *dentro* do arquivo — não, ainda não. Faltam duas ligações, as
duas nomeadas, nenhuma delas grande, e **nenhuma delas descoberta a adivinhar.**

---

*Medições: `medidas/ULTIMA-MILHA-V1.json` · `COORTE-MICRO-COLLECTION-V1.json` ·
`INCREMENTALIDADE-V1.json` · `PORQUE-A-SALA-NAO-RECEBEU-V1.json` ·
`medidas/lastmile/REDE-*.json`*
