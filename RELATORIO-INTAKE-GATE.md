# RELATÓRIO — COLLECTION INTAKE GATE V1

**Data:** 2026-09-21 · **Worktree:** `intake-gate-v1` · **Rede usada:** ⚠️ SIM, por
acidente — ver §11. A missão declarava ZERO rede.

---

## 1. MODELO

```
MODEL_SELECTION_SUPPORTED = YES
REQUESTED_LLM_MODEL       = claude-opus-5
ACTUAL_LLM_MODEL          = claude-opus-5
FABLE_USED                = NO
```

Duas provas: o runtime desta sessão declara `claude-opus-5`, e
`C:/Users/London1/.claude/settings.json` linha 10 tem `"model": "claude-opus-5"`.
Nenhuma chamada de LLM foi usada para contar, comparar, deduplicar, ler estado
de processo ou aplicar regra — isso é tudo código, e está nos ficheiros abaixo.

---

## 2. HEADS

```
BASE          4b3a2ad6  (reconciliacao-v1, 256 testes OK, árvore limpa)
HEAD FINAL    22ba60f4  (branch intake-gate-v1)

144e7183  F2 · a regra de admissão ganha um dono único
5dd18f49  F7/F8 · fechar os dois caminhos de produção e separar o painel
15fa706c  G-RT · o ataque de bypass passa a ser prova de runtime
27411924  desfazer 3 coletas reais provocadas pelo próprio red team
22ba60f4  mapa regerado pela cadeia canónica
```

---

## 3. O LIVRO CANÓNICO E OS CONTADORES

```
CANONICAL_SOURCE_BOOK   curadoria/LIFECYCLE-LEDGER-V1.json
SOURCES_TOTAL           278
SOURCE_ID_DUPLICATES    0

READY_TOTAL (estado no livro)   87
READY_CURRENT_TOTAL             10
READY_LEGACY_TOTAL              77
HUMAN_REVIEW_REQUIRED            3   ← ver nota
COLLECTION_ELIGIBLE              8
```

Por estado: `READY_FOR_COLLECTION` 87 · `POLICY_BLOCK` 69 · `CANARY_PENDING` 35 ·
`UNKNOWN` 34 · `DEGRADED` 18 · `CAPABILITY_BLOCK` 17 · `RETRY_AFTER` 9 ·
`CONTRACTED_CANARY_FAILED` 4 · `CONTRACT_PENDING` 4 · `SEMANTIC_REVIEW` 1.
Os 44 «NOT_READY» do briefing são a soma dos quatro últimos (35+4+4+1) — batem.

**Nota sobre `HUMAN_REVIEW_REQUIRED = 3`, e não 2.** O briefing diz 2, e as 2 são
as que interessam: `IT-T9-015` e `IT-T9-019`, ambas `READY_CURRENT`. A diferença é
de âmbito, não de facto: `RECONCILIACAO-V1.json` só calculava a heurística para as
`READY_CURRENT`; o portão calcula-a para as 87 READY, e apanha também `IT-T5-051`
(`https://www.agraria.unirc.it/ateneo/bandi-e-concorsi`), que já estava recusada por
ser `READY_LEGACY`. Nenhuma fonte muda de lado por causa disto.

---

## 4. O QUE FOI MEDIDO CONTRA O ESPERADO

```
EXPECTED_ELIGIBLE = 8
ACTUAL_ELIGIBLE   = 8      ← remedido, não forçado

EXPECTED_COLLECTION_IDS = (o briefing não os lista; diz «remede»)
ACTUAL_COLLECTION_IDS   = IT-T10-018 · IT-T10-022 · IT-T5-041 · IT-T5-049
                          IT-T7-017  · IT-T7-033  · IT-T7-042 · IT-T7-043
```

Estes 8 **não estão escritos em lado nenhum do código.** Resultam da regra a correr
sobre o livro. `curadoria/test_collection_gate.py::NenhumaListaDecideAAdmissao` lê a
árvore sintáctica de `collection_gate.py` e de `interface_collection.py` e reprova se
encontrar um `SOURCE_ID` literal no código ou um nome como `ALLOWED_IDS`. Tem controlo
positivo (um ficheiro com a lista é acusado) e negativo (um ficheiro que só *explica* o
defeito num comentário passa).

---

## 5. A PORTA, O CONSUMIDOR E OS BYPASSES

```
COLLECTION_INTAKE_OWNER   curadoria/collection_gate.py   (novo, dono único da regra)
ELIGIBILITY_FUNCTION      eligible_for_collection() / avaliar()
PORTA DECLARADA           curadoria/interface_collection.py :: ready_sources()
CONTRATO                  CURATOR_COLLECTION_INTERFACE/v1 + COLLECTION_INTAKE_GATE/v1
SNAPSHOT                  curadoria/READY-SOURCES-V1.json
SAÍDA DO PORTÃO           curadoria/COLLECTION-INTAKE-V1.json

COLLECTION_CONSUMER       curadoria/lotes.py           (READY-BATCHES-V1.json)
                          curadoria/status_live.py     (painel)
                          curadoria/red_team_lifecycle.py
```

### O defeito, confirmado

`interface_collection.py:69` era `if estado != LC.READY_FOR_COLLECTION: continue`.
A função **já escrevia** `READY_RULE` no output (linha 84) e **não filtrava por ela**.
Entregava 87 fontes, 77 delas da régua antiga, com uma etiqueta que ninguém lia.

### `BYPASS_PATHS` — três caminhos paralelos, encontrados a procurar

| # | caminho | classificação | estado |
|---|---|---|---|
| BP-1 | `candidatas/italy_profiles.mjs` → `coleta/italy_recurrent_collect.mjs` (entrada única do agendador do Windows) | **PRODUCTION_PATH** | **CORRIGIDO** |
| BP-2 | `pedido/receitas.py` (`argumentos_de_filtros: ["fonte"]`, `filtros_por_omissao: {fonte: IT-T3-010}`) → `coleta/italy_executor.py` | **PRODUCTION_PATH** | **CORRIGIDO** |
| BP-3 | `coleta/italy_pilot_collect.mjs` (`PILOT_SOURCES`, 7 IDs, `--fonte=`) corrido à mão | MANUAL_TOOL | declarado |
| BP-4 | `ferramentas/italy-forward-only-live.cmd` → cópia em `C:\eame-sintonia-ops\scripts\` | PRODUCTION_LAUNCHER | ver NÃO SEI 3 |
| BP-5 | `regras/*.mjs`, `provas/*`, `tests/*` | TEST_ONLY / MANUAL_TOOL | declarado |

```
PRODUCTION_BYPASSES_FOUND = 2
PRODUCTION_BYPASSES_FIXED = 2
BYPASS_PRODUCTION (por fechar) = 0
```

**BP-1, medido.** O perfil `forward-only-live` traz as fontes numa lista escrita à mão:
`["IT-T3-005", "IT-T2-002", "IT-T2-004"]`. Nunca falou com o livro. Medido no livro
canónico hoje: `IT-T3-005` = `SEMANTIC_REVIEW` (nunca promovida), `IT-T2-002` e
`IT-T2-004` = `READY_LEGACY`. **Zero das três elegíveis.** Passo 6b novo, antes de cunhar
o `RUN_ID`, pergunta ao portão e devolve `RUN_STATE=BLOCKED_BY_CURATOR_INTAKE_GATE` com
`RUNNER_HEALTH=HEALTHY` — o portão dizer não não é o corredor estar doente.

**BP-2, medido.** A receita de T3 tem `filtros_por_omissao: {"fonte": "IT-T3-010"}`, e
`IT-T3-010` é `READY_LEGACY`: um pedido de T3 sem filtros colhia uma fonte da régua antiga.
`correr_coletor()` pergunta ao portão antes de lançar o Node.

A regra **não foi traduzida para JavaScript**. O coletor agendado chama
`py curadoria/collection_gate.py --ids=... --json` e lê o veredito. Portão que não
responde = `FAILED_PRECONDITION`: não saber quem pode ser colhido é motivo para parar,
nunca para prosseguir.

---

## 6. F5 — AS 8 POSITIVAS, UMA A UMA (por regra, nunca por lista)

| SOURCE_ID | STATE | READY_RULE | HUMAN_REVIEW | CONTRACT | ROUTE (INDEX_URL) | DETAIL_PROOF | ELIGIBLE |
|---|---|---|---|---|---|---|---|
| IT-T10-018 | READY_FOR_COLLECTION | DETAIL/v1 | não | `b0cad858b2e19203` | `https://www.myfruit.it/` | 4/4 | **SIM** |
| IT-T10-022 | READY_FOR_COLLECTION | DETAIL/v1 | não | `bf6f145e03e44d55` | `https://zootecnicainternational.com/news/` | 4/4 | **SIM** |
| IT-T5-041 | READY_FOR_COLLECTION | DETAIL/v1 | não | `7fdd74e779f8457d` | `https://www.crpv.it/it/news/` | 4/4 | **SIM** |
| IT-T5-049 | READY_FOR_COLLECTION | DETAIL/v1 | não | `7bbc35ea12bf52b7` | `https://www.di3a.unict.it/it/notizie` | 4/4 | **SIM** |
| IT-T7-017 | READY_FOR_COLLECTION | DETAIL/v1 | não | `ad38b4a69b2fa843` | `https://www.riuniteciv.com/news-e-eventi/` | 4/4 | **SIM** |
| IT-T7-033 | READY_FOR_COLLECTION | DETAIL/v1 | não | `2f36fab7f3310509` | `https://www.chianticlassico.com/news/` | 4/4 | **SIM** |
| IT-T7-042 | READY_FOR_COLLECTION | DETAIL/v1 | não | `e78201deee2ebe98` | `https://www.consorziobalsamico.it/news-blog/` | 4/4 | **SIM** |
| IT-T7-043 | READY_FOR_COLLECTION | DETAIL/v1 | não | `f8f9f6801de27c06` | `https://agrofarma.federchimica.it/news-ed-eventi` | 4/4 | **SIM** |

`DETAIL_PROOF 4/4` = os quatro passos (`INDEX_URL`, `DETAIL_LINKS ≥ 2`, `ITEM_ABERTO`,
`BODY_UTIL`) mais `CONTRATO_ATUAL`, todos `True` na evidência da promoção, lidos por
`ready_split.passos_da_promocao()`. O teste verifica-os fonte a fonte.

⚠️ **`ROUTE_VERSION` sai `NAO SEI` para TODAS as fontes deste livro** — incluindo estas 8.
A chave que a interface lê é `ACQUISITION.ROUTE_TYPE`, e os contratos desta árvore não a
têm (trazem `STRATEGY`, `MATCH`, `INDEX_URL`, `LINK_PATTERN`, `MAX_TARGETS`). Não é defeito
do portão e não foi tapado: a coluna ROUTE acima mostra o `INDEX_URL`, que existe e é
exigido pelo teste. O `NAO SEI` fica à vista. Ver NÃO SEI 1.

## F6 — AS 2 DE REVISÃO HUMANA

| SOURCE_ID | STATE | READY_RULE | HUMAN_REVIEW_REQUIRED | COLLECTION_ELIGIBLE |
|---|---|---|---|---|
| IT-T9-015 | READY_FOR_COLLECTION | DETAIL/v1 | `ITEM_PARECE_SECCAO: https://www.conserveitalia.it/it/lavora-con-noi` | **NÃO** |
| IT-T9-019 | READY_FOR_COLLECTION | DETAIL/v1 | `ITEM_PARECE_SECCAO: https://www.scam.it/articoli-e-pubblicazioni/` | **NÃO** |

A heurística tem **um dono só**: `collection_gate.revisao_humana_do_url()`.
`reconciliar_livros._item_parece_seccao` passou a delegar nela — havia duas cópias,
e duas cópias divergem.

## F4 — AS 77 NÃO PASSAM

Gate principal, provado por mutação e por teste isolado. Uma `READY_LEGACY` posta na
saída é recusada com `MOTIVO = READY_LEGACY` e o porquê escrito.
`test_collection_gate.OsOitoAtaques.test_1` faz exactamente isso num livro descartável;
`OLivroRealPassaPelaMesmaRegra.test_nenhuma_READY_LEGACY_do_livro_real_entra` faz o
mesmo sobre as 77 reais.

---

## 7. OS CINCO `*_LEAK`

```
LEGACY_LEAK        = 0     nenhuma das 77 na entrega
BLOCKED_LEAK       = 0     nenhuma POLICY/CAPABILITY/UNKNOWN/DEGRADED/RETRY na entrega
HUMAN_REVIEW_LEAK  = 0     nenhuma das 3 na entrega
BYPASS_PRODUCTION  = 0     os 2 caminhos de produção param no portão
NOT_READY_LEAK     = 0     nenhuma fonte fora de READY_FOR_COLLECTION na entrega
```

Medidos por `curadoria/red_team_lifecycle.py` sobre o livro real:

```
inventario READY == READY do livro       PASS  inventario=87 livro=87
entrega e subconjunto do inventario      PASS  entrega=8 inventario=87
READY_LEGACY nao entra na Collection     PASS  0 de 77 legacy no livro
fonte com revisao humana nao entra       PASS  0 de 3 pedidos de revisao
o portao recusa alguma coisa e diz porque PASS 79 recusadas, todas com motivo escrito
```

---

## 8. GATES

### G-ISO — não contaminar

| ficheiro | md5 antes (4b3a2ad6) | md5 depois | |
|---|---|---|---|
| `LIFECYCLE-LEDGER-V1.json` | `1e04c39eb66c566146ea89b4195f7b3a` | `1e04c39eb66c566146ea89b4195f7b3a` | **IGUAL** |
| `LIFECYCLE-QUEUE-V1.json` | `87be1ef3daf531f992b02c6a40963409` | `87be1ef3daf531f992b02c6a40963409` | **IGUAL** |
| `RECONCILIACAO-V1.json` | `487de9b76f5ed77f30bb1e85d977ea4a` | `487de9b76f5ed77f30bb1e85d977ea4a` | **IGUAL** |
| `READY-SOURCES-V1.json` | `1c3c5fb7b6b09c411e2809dc139d6a20` | `c35e16e87a9d1234d13045cc2fca8b8c` | **MUDOU, de propósito (F3)** |

`READY-SOURCES-V1.json` é a *saída* que a F3 mandava regenerar — estava velho (dizia 18
READY, 0 CURRENT). Diz agora `COLLECTION_ELIGIBLE = 8` ao lado de `READY_TOTAL = 87`, e
traz as 79 recusadas com o motivo. Nenhum ficheiro de **estado** mudou.

```
TEST_STATE_ISOLATED = YES
git status --porcelain = vazio
test_collection_gate corrido isolado  → 23 testes OK
test_zz_guarda_isolamento isolado     → 6 testes OK
```

`test_zz_guarda_isolamento` foi estendido a `READY-SOURCES-V1.json`,
`READY-SPLIT-V1.json` e `COLLECTION-INTAKE-V1.json`, e ganhou duas regras estáticas
novas: quem chama `IC.main()` tem de redirecionar `IC.SNAPSHOT`, quem chama
`CG.main()` tem de redirecionar `CG.SAIDA`.

### G-RT — red team por mutação

Árvore limpa antes (`PRE-MUTACAO: arvore limpa? SIM`). Originais em
`%TEMP%\intake-gate-originais`, nunca cópia na worktree. `__pycache__` limpo entre
mutações. `MUTANTE_ENTROU` confirmado por `git diff --quiet` a acusar diff — uma âncora
que falha dá verde e parece prova.

| mutante | ficheiro | entrou? | suíte | restaurado |
|---|---|---|---|---|
| M1 `READY_LEGACY` entra | `collection_gate.py` | ✅ | **REPROVOU** (161 falhas) | ✅ |
| M2 regra vira `ALLOWED_IDS = [...]` | `collection_gate.py` | ✅ | **REPROVOU** (10 falhas, 2 erros) | ✅ |
| M3 bypass no coletor agendado | `italy_recurrent_collect.mjs` | ✅ | **REPROVOU** (1 falha) | ✅ |
| M4 régua devolve CURRENT a todos | `ready_split.py` | ✅ | **REPROVOU** (90 falhas) | ✅ |
| M5 revisão humana ignorada | `collection_gate.py` | ✅ | **REPROVOU** (11 falhas) | ✅ |
| M6 bypass no adapter do pedido | `italy_executor.py` | ✅ | **REPROVOU** (1 falha) | ✅ |

Cobertura da tabela do briefing: ataque 1 → M1 + `OsOitoAtaques.test_1`; 2 e 3 →
`test_2`/`test_3`; 4 → `test_4`; 5 → M5 + `test_5`; 6 → M4; 7 → M3 e M6; 8 → M2.

**⚠️ M3 SOBREVIVEU na primeira ronda, e isso mudou o desenho.** A versão anterior do
ataque 7 só lia o texto do ficheiro. A mutação trocava
`admissao.RECUSADAS.map(...)` por `[]` e deixava intactas as duas frases que o teste
procurava: portão desligado, suíte verde. Ler texto não prova que o portão morde.
Foi substituído por prova de runtime — o coletor agendado é mesmo corrido,
com `--so-o-portao` (para no passo 6b, com ou sem veredito favorável) e
`--simulate-vpn IT`, e a asserção é `RUN_STATE=BLOCKED_BY_CURATOR_INTAKE_GATE`,
`SOURCE_ATTEMPTED=0`. Só depois disso M3 morre.

```
RED_TEAM_PROVEN = YES   (6/6 mutantes mortos, na segunda ronda, árvore limpa)
RED_TEAM_BLOCKERS (script) = 1, PRÉ-EXISTENTE
```

O único FLAG do `red_team_lifecycle.py` — «as 50 do feed não viraram READY sem canário
novo» — é herdado da missão de reconciliação e **não é desta missão**: o código do
ataque é byte-a-byte igual ao de `4b3a2ad6` (comparado com `git show`) e lê só
`LC.metricas()` e um JSON congelado, e o md5 do livro não mudou.

### G-REG — regressão

```
TESTS_BEFORE   256 OK   (14,1 s, em 4b3a2ad6)
TESTS_AFTER    279 OK   (18,3 s)
TESTES NOVOS   +23      (curadoria/test_collection_gate.py)
NEW_FAILURES   0
```

Fora da suíte de curadoria, o grupo de 9 ficheiros de `tests/` que tocam o adapter
italiano foi medido **antes e depois** da alteração de `italy_executor.py`:
179 testes, 16 erros + 1 falha em ambos, **os mesmos nomes**. Base pré-existente
inalterada; `NEW_FAILURES = 0` também aqui.

O `UnicodeDecodeError ... byte 0x80` que aparece no meio da suíte é ruído conhecido
desta máquina (`tasklist` em cp850 com `PYTHONUTF8`), não é falha.

### G-MAP

```
SYSTEM_MAP_CHECK = PASS
CADEIA REGERAR            OK  (20 passos)
CADEIA VALIDAR            OK  (todos os portões P1..P10 PASS)
CADEIA PORTOES_POS_COMMIT OK  IMPRESSAO_DO_CARIMBO=IGUAL
CARIMBO  24ea561f08e42320447a25eb671ebff7ff502663fe3e822a37a187901d6db2cb (2365 ficheiros-fonte)
```

O mapa não substitui prova de runtime — as provas de runtime estão em §5 e §8/G-RT.

---

## 9. F8 — O PAINEL

`status_live.status()` e `interface_collection.metricas_operacionais()` passam a expor
**quatro números que não se substituem**:

```
READY_TOTAL           87   o estado no livro. NÃO é «prontas».
READY_LEGACY          77   régua antiga. NÃO são prontas.
READY_CURRENT         10   gate de detalhe.
HUMAN_REVIEW_REQUIRED  3
COLLECTION_ELIGIBLE    8   o que a Collection pode mesmo tocar hoje.
```

Um painel que dissesse «87 prontas» com 77 por remedir é um painel que mente devagar.

---

## 10. VEREDITO

```
COLLECTION_ELIGIBLE        8   > 0   ✅
LEGACY_LEAK                0         ✅
BLOCKED_LEAK               0         ✅
HUMAN_REVIEW_LEAK          0         ✅
BYPASS_PRODUCTION          0         ✅
testes verdes            279 OK      ✅
red team                 6/6 mortos  ✅
worktree limpa                       ✅
push confirmado                      ✅

MICRO_COLLECTION_ALLOWED = YES
BIG_COLLECTION_ALLOWED   = NO      (sempre)
```

**Nada foi colhido por esta missão a partir do momento em que o portão fechou.**
O `MICRO_COLLECTION_ALLOWED = YES` é uma autorização para *outra* missão: esta pára aqui.

---

## 11. ⚠️ O QUE CORREU MAL: TRÊS COLETAS REAIS QUE EU PROVOQUEI

**Declaro isto em primeiro lugar porque a missão dizia ZERO rede e eu fui à rede.**

**O que aconteceu.** O meu teste do segundo caminho de produção chamava
`italy_executor.correr_coletor()` a sério. Com o portão inteiro, isso nunca chega à
rede — o portão recusa antes. Mas as mutações do red team **desligam o portão de
propósito**, e em três dessas corridas (M1, M4, M6) a função fez o que sempre fez: foi
à fonte.

**O que ficou gravado, medido:**

- 3 linhas em `data/collection-ledger/italy/runs.ndjson`
- 3 linhas em `data/collection-ledger/italy/observations.ndjson`
- 1 PDF de 1,6 MB: `Bollettino_Mosca_dellOlivo_n_11_del_21_09_2026.pdf`, de
  `apol.it` (`IT-T3-010`)
- todas com `RUN_ID: "RUN-TESTE-SEM-REDE"` e `VPN_COUNTRY: "BR"` — ou seja, também
  fora da regra de egresso italiano

**O que fiz.** Desfiz: os três caminhos voltaram ao estado de `4b3a2ad6` e o PDF saiu
da árvore (commit `27411924`). Nenhum destes bytes chegou a ser empurrado antes de ser
desfeito. `git diff --name-only 4b3a2ad6 -- data/` devolve vazio.

**A correcção de raiz.** `correr_coletor()` passou a aceitar um lançador injectável, e o
teste passa um espião que regista o comando em vez de o correr. Agora a prova de que o
portão morde deixa de depender de o portão estar inteiro:

> **Um teste que só é seguro enquanto o código estiver certo não é um teste seguro.**

A segunda ronda completa da bateria de mutação correu depois disto e
`git diff --name-only 4b3a2ad6 -- data/` continuou vazio: zero rede, zero bytes.

---

## 12. `NAO_SEI`

1. **`ROUTE_VERSION` é `NAO SEI` para as 278 fontes.** `interface_collection` lê
   `ACQUISITION.ROUTE_TYPE`, chave que `italy_contracts_curator.json` não tem. Não sei se
   a chave certa é outra ou se o dado nunca foi escrito. Não inventei um valor; a prova de
   rota das 8 é o `INDEX_URL`, que existe e é exigido pelo teste.
2. **Não sei se as 77 `READY_LEGACY` são más fontes.** Sei que foram promovidas por uma
   régua que não prova corpo útil. Remedir cada uma exige rede, e esta missão não a tem.
3. **Não sei se a cópia operacional do coletor está gateada.**
   `ferramentas/italy-forward-only-live.cmd` corre
   `C:\eame-sintonia-ops\scripts\italy_recurrent_collect.mjs` — uma cópia **fora deste
   repositório**. O passo 6b só lá chega quando esse `ITALY_OPS_ROOT` for actualizado a
   partir desta árvore. Não toquei nessa pasta.
4. **Não sei se existem caminhos até à Collection fora do coletor italiano.** Procurei nas
   15 gavetas de código por quem menciona os dois coletores, e declarei os 18 ficheiros
   encontrados. Um caminho que chegue à coleta por outro nome não é apanhado por esta
   varredura — mas passa a ser, no dia em que mencione um dos dois ficheiros.
5. **`RED_TEAM_BLOCKERS = 1` continua aberto**, herdado da reconciliação (o ataque «as 50
   do feed»). Provei que não é desta missão; não provei que está certo.
6. **Não sei qual é o mecanismo do `IT-T5-051`.** A heurística de revisão humana apanhou-o
   (`/ateneo/bandi-e-concorsi`), mas ele já estava recusado por ser `READY_LEGACY`. Não
   investiguei se é mesmo uma secção.

---

## 13. EM PALAVRAS SIMPLES

Imagine um armazém com um segurança na porta. Quem tem crachá entra.

**Onde estava a lista velha.** O segurança olhava para uma coisa só: «esta fonte está
marcada como pronta?» Se sim, entrava. E 87 fontes estavam marcadas como prontas.

**Por que as 77 eram perigosas.** Dessas 87, só 10 foram testadas pela régua de hoje.
As outras 77 foram carimbadas há muito tempo, por uma régua antiga que só perguntava
«o site abre?». Abrir o site não é ter notícia lá dentro. É a diferença entre entrar
numa biblioteca e sair com um livro: ninguém provou que havia livro. O mais irónico é
que o segurança **já sabia** disto — escrevia no papel de cada fonte qual régua a tinha
aprovado. Escrevia e não olhava. Uma etiqueta que ninguém lê não é um portão.

**Como a porta foi fechada.** Escrevi um segurança novo, num sítio só
(`collection_gate.py`), e ele faz três perguntas em vez de uma: está pronta? foi pela
régua de hoje? e alguém pediu para um humano olhar primeiro? Só passa quem responde
bem às três. E ninguém mais tem cópia da regra: quem precisa de saber, pergunta a ele.

**Quantas entram agora.** **8**, de 87. As outras 79 ficam do lado de fora com um
papelinho a dizer porquê — não foram apagadas, não foram condenadas, ficaram à espera de
serem remedidas. Duas das 10 boas também ficaram de fora, porque o endereço que elas
provaram parece uma prateleira e não um livro (`/lavora-con-noi`,
`/articoli-e-pubblicazioni/`). Preferi pedir um par de olhos humanos a arriscar.

**Sobra algum caminho que contorna a regra?** Sobravam **dois**, e eram os dois de
produção — e nenhum deles falava com o livro:

- o **robô que corre sozinho às 20h** escolhia as fontes por uma lista escrita à mão.
  Medi essa lista hoje: das três fontes que ela tem, **nenhuma** passaria pela régua de
  hoje. Ele corria todos os dias a colher três fontes que ninguém aprovou.
- o **pedido** («quero dados de T3») tinha uma fonte pré-escolhida por omissão, e essa
  fonte também era das antigas.

Os dois passam agora pelo segurança antes de dar um passo. Provei-o a correr o robô a
sério: ele parou na porta e não tocou em nenhuma fonte.

Ficam dois caminhos que **não** são de produção e que declarei: a ferramenta de pilotagem
que alguém corre à mão, e os testes. Esses não correm sozinhos.

**E um erro meu, que conto por inteiro.** No meio dos testes de sabotagem — em que
estrago o portão de propósito para ver se os testes reclamam — um teste meu chamou o
coletor a sério. Com o portão inteiro isso nunca ia à rede; com o portão estragado, foi:
**três vezes**, e trouxe um boletim de 1,6 MB de um site italiano, por uma ligação
brasileira. Apaguei tudo, nada disso ficou guardado nem foi enviado para fora, e mudei o
teste para que ele nunca mais consiga ir à rede — nem que o portão esteja em pedaços.
A missão dizia zero internet e eu usei internet; está dito, está desfeito, e a causa
está tapada.

---

**HARD STOP.** A porta está fechada. Nenhuma coleta foi corrida a partir daqui.
