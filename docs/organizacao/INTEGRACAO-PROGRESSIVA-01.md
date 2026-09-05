# P0.2 · INTEGRAÇÃO PROGRESSIVA DA CASA · PASSO 01

**Data:** 2026-09-05 · **Branch:** `sintonia/canonical` · **Modo:** integração local, sem deploy,
sem mudança de default branch.

```
CANONICAL_HEAD_BEFORE   = 64e6ad37cca3c759d8059ef8e0716dcaee9d7f07
SELECTED_REF            = claude/retomada-coleta-video-convegni-vz50er
SELECTED_REF_HEAD       = 0cfc18201e3f66e1ae00d4ea09df3d214c94b386
P0_2_STEP_01_VERDICT    = BLOCKED
```

O merge foi tentado, classificado e **abortado**. `HEAD` continua em `64e6ad3`, working tree
limpa. Nada foi perdido, nada foi decidido em silêncio.

---

## 1 · DURABILIDADE — confirmada antes de tocar em nada

`CURRENT_BRANCH` `sintonia/canonical` · `LOCAL_HEAD` = `REMOTE_HEAD` = `64e6ad3` · `MATCH = SIM`.

## 2 · ESCOLHA DO ENXERTO — medida contra o HEAD atual, não herdada

Medi o ganho incremental de **todos os 49 refs** contra `64e6ad3` (uma operação de rede, contagem
local determinística) em vez de reauditar 48 branches. Seis refs já não trazem nada novo.

Os cinco candidatos sugeridos ficaram, de facto, no topo — mas três empataram, e o desempate
exigiu medir o que os separa:

| REF | HEAD | NOVOS | DATA | SCRIPTS | WF | SUBSUME | CONFLITOS |
|---|---|---:|---:|---:|---:|---:|---:|
| **retomada-coleta-video-convegni** | `0cfc182` | **532** | 471 | **44** | 0 | **10** | 3 |
| sprint/vocab-55c2674 | `3a686ba` | 531 | 471 | 43 | 0 | 10 | 3 |
| sprint/verificacao-lote-73c8df0 | `b4a302e` | 531 | 471 | 43 | 0 | 10 | 3 |
| sprint/publicacao-unica-5855cad | `60af3fb` | 530 | 470 | 43 | 0 | 9 | — |
| sprint/fito-lei-560 | `5855cad` | 530 | 470 | 43 | 0 | 9 | — |

**Os três primeiros partilham um núcleo de 530 caminhos e diferem por UM artefacto cada:**

- `retomada` → `IT-ACERVO-MEDICAO-ESTRUTURAL-V1.json` **+ `scripts/it_acervo_medicao_estrutural.py`**
- `vocab` → `IT-VOCAB-REMEDICAO-55c2674-V1.json`
- `verif` → `IT-VERIFICACAO-DO-LOTE-73c8df0-V1.json`

`WHY_THIS_REF` — critério objetivo, não desempate por preferência: é o único que traz **script
junto com o dado** (critério 3, `WORKFLOW_DEPENDENCY_GAIN`), tem o maior ganho bruto, empata no
topo de refs subsumidos, e produz **exatamente os mesmos 3 conflitos** que os outros dois.
`sprint/vocab-55c2674` foi excluído por tocar a autoridade semântica `55c2674`, que a lei herdada
manda não substituir.

## 3 · CONFLITOS

`CONFLICTS_TOTAL = 3` · `MECHANICAL = 0` · `POLICY = 1` · `HISTORICAL_ONLY = 1` · `SEMANTIC = 1` · `UNKNOWN = 0`

### 3.1 · `.gitignore` — COLLECTION_POLICY · **resolvido pela política já canónica**

Os dois lados acrescentam apenas diretórios de cache, em conjuntos **disjuntos**, e **nenhum**
introduz ignore global de RAW. União, com quatro provas mecânicas: as 5 regras canónicas
sobrevivem; as 6 da origem entram; nenhuma regra `data/samples/**/*.gz|raw.json` presente;
`tracked-and-ignored` (método `--no-index`) continua em **1**, o pré-existente.

### 3.2 · `docs/descoberta/CAMADA-DE-VOZ-ESPANHA.md` — HISTORICAL_ONLY · resolúvel

Nenhum lado removeu ou reescreveu nada: `diff <(head -374 <lado>) BASE` é **vazio nos dois**.
São dois apêndices **disjuntos** na mesma cauda — conflito posicional, não de conteúdo.
Prova de que **relata e não define**: `grep -c "<!--M:"` = **10** nos três lados (nenhum marcador
lido por `metricas_canonicas.py` é criado, removido ou alterado), e a frase que
`tests/test_voz.py:203` exige literalmente sobrevive intacta.

E não são duas medições do mesmo fenómeno: `OURS` mede Espanha/missão 11 (`FACT_LOCATION: ES`,
2026-08-29), `THEIRS` mede Itália/voz (`COUNTRY: IT`, 2026-09-03). **Denominadores diferentes,
não se sintetizam.** Resolução correta: união verbatim dos dois apêndices, 374 + 18 + 72 = 464
linhas, sem uma única linha editada, fundida ou "conciliada".

### 3.3 · `scripts/voz.py` — **INTELLIGENCE_SEMANTIC** · **PARA**

As duas linhagens editaram **a mesma região** — as ~5 linhas do laço de eleição de `CROP` em
`marcar_assunto` — com decisões **opostas, deliberadas e cada uma com prova própria**:

| | o que mudou a partir do ancestral `037b181` |
|---|---|
| **canónica** (`b9a6c16`) | `for … break` (primeiro casamento por ordem do dicionário) → recolhe todos os casamentos e cria o estado canónico **`AMBIGUOUS:<A>+<B>`**. Lei declarada: *"empate não se desempata em silêncio"*. Mais a regra de identidade do dedupe (`SEM_ID_ESTRUTURAL`, `WITHOUT_STRUCTURAL_ID_COUNT`): *"ausência de identidade não é identidade partilhada"* — porque na MISSÃO 10C três vídeos sem `id` colapsavam em um e o portão dizia `PROVED`. |
| **origem** (`809328f`, `ba1c892`) | vocabulários italianos (25 CROP, 28 ISSUE, 32 MOLECULE, 29 LUGAR), vocabulário **injetável**, `ler_transcricao=True` — que **muda o campo lido** de `TITLE+DESCRIPTION` para `TITLE+DESCRIPTION+TRANSCRIPT` — e `MOLECULAS_ADAMA_IT` + `separar_molecula_por_dono()` com `MOLECULE_OWNERSHIP_LAW = 'MOLECULA MARCADA != MOLECULA ADAMA'`. E **preservou o `for … break` de propósito**: `it_inventario.py:77` documenta por escrito que *"`marcar_assunto` do voz.py para no primeiro casamento POR DESENHO"*. |

**A união ingénua não é neutra — medido, não suposto.** Aplicando a regra da canónica ao
vocabulário italiano da origem sobre o corpus real `data/samples/IT-CONVEGNO-V1/falas/*.json`:

> **primeiro-casamento ≠ `AMBIGUOUS` em 17 de 17 registos — 100%.**
> `CYV76yVc98s`: `VITE` → `AMBIGUOUS:CILIEGIO+CUCURBITACEE+FRAGOLA+PERO+PESCO+VITE`.

A justificação da canónica (*"medido em sombra sobre os 252 vídeos: OLD ≠ PROPOSED em 0 registos"*)
**não transfere**: ela só vale porque o `VOCAB_CROP` espanhol tem **uma** chave, onde o empate é
impossível. Com 25 chaves italianas e leitura de transcrição, o empate deixa de ser exceção e
passa a ser a regra. A união reescreveria **100% do campo CROP italiano** sem ninguém ter decidido isso.

**Isto seria regressão introduzida pelo merge, não dívida herdada** — em cada linhagem isolada o
problema não existe. E nenhum dos dois lados sozinho serve: escolher a canónica quebra 4 scripts
italianos (`it_video.py`, `it_audio.py`, `it_inventario.py`, `instagram_sem_navegador.py`);
escolher a origem quebra 4 testes que a canónica escreveu de propósito
(`TestCropNaoDesempataEmSilencio`, `test_registros_sem_id_estrutural_nao_colapsam`).

Não é `CONTRACT`: `CAMPOS_VIDEO` é byte-a-byte idêntico ao ancestral nos dois lados. E não é CI:
nenhum workflow referencia `voz.py` — o bloqueio são os testes e os scripts italianos **dentro** do repositório.

## 4 · PORTÕES

O merge foi abortado, então os portões pós-merge **não se aplicam**. O que ficou provado:

| | |
|---|---|
| `CANONICAL_CONTENT_LOST` · `SOURCE_CONTENT_LOST` | **0** — nada foi selado, `HEAD` intacto |
| `NEW_TRACKED_IGNORED` | **0** (mantém-se 1 pré-existente: `data/raw/IT-ROTULOS/_MANIFESTO.json`) |
| `NEW_WORKFLOW_BREAKAGES` | **0** — a ref traz 0 workflows novos |
| `NEW_TEST_REGRESSIONS` | **0 medidas** · mas **≥4 previstas** se o merge fosse selado por qualquer dos lados |
| working tree · `git fsck` | limpa · limpo |

## 5 · GANHO — e uma correção dos meus próprios números

`DATA_BLOBS_AFTER` = `DATA_BLOBS_BEFORE` = **388** (nada mudou; merge abortado).

> **Correção.** O canário anterior publicou "dados 177 → 378". Os valores corretos são
> **187 → 388**. Mesma causa dos `51`-vs-`61` `.gz`: `git ls-tree` sem `-z` aspa nomes com acento
> e um `grep` ingénuo perde 10 ficheiros. A lei 6 desta missão existe por isso — e eu tinha-a
> violado. Os valores de scripts (52 → 143) e workflows (10 → 18) confirmam-se NUL-safe.

**Denominador declarado:** todas as contagens acima são de **CAMINHOS versionados** obtidos com
`git ls-tree -rz` / `git ls-files -z`. Não são blobs, não são registos, não são `ITEM_ID`.

`GLOBAL_*_COVERAGE` e `UNACCOUNTED_VALID_*`: **NÃO MEDIDO**. Exigiriam definir "válido" e
"contabilizado", o que é auditoria nova — e o passo terminou bloqueado antes disso.

## 6 · CLASSIFICAÇÃO DO REF

`REF_CLASSIFICATION = MIXED`

- **CANONICAL_INPUT** — os 530 caminhos do núcleo (471 dados + 44 scripts da camada italiana de
  vídeo/áudio), o `.gitignore` de caches, e o apêndice italiano do documento de voz. Entram assim
  que a decisão D1 existir.
- **INTELLIGENCE_SEMANTIC pendente** — apenas `scripts/voz.py`, e dentro dele apenas a regra de
  eleição de `CROP`. As outras mudanças da origem no mesmo ficheiro (vocabulários, injeção,
  leitura de transcrição, propriedade de molécula) são **disjuntas** das da canónica.

A branch original **não é apagada** e continua a ser a evidência histórica desta linhagem.

---

## VEREDITO

```
CONFLICTS_TOTAL             = 3
MECHANICAL                  = 0
POLICY                      = 1   (resolvido pela POLITICA-CANONICA-DE-RAW)
HISTORICAL_ONLY             = 1   (resolúvel, união verbatim)
SEMANTIC                    = 1   (bloqueia)
UNKNOWN                     = 0

CANONICAL_CONTENT_LOST      = 0
SOURCE_CONTENT_LOST         = 0
NEW_TRACKED_IGNORED         = 0
NEW_WORKFLOW_BREAKAGES      = 0
NEW_TEST_REGRESSIONS        = 0 medidas (≥4 previstas se selado)

P0_2_STEP_01_VERDICT        = BLOCKED
CANONICAL_LINEAGE_STATE     = CANDIDATE_INTEGRATION
DEFAULT_BRANCH_CHANGE_SAFE_NOW = NÃO
```

**A lei do canário funcionou pela segunda vez, e mais cedo.** No primeiro enxerto o bloqueio
apareceu num `.gitignore` — política de armazenamento. Neste, apareceu em 5 linhas de um laço
`for` — política de **significado**. Em ambos os casos a mecânica de junção estava sólida e o que
faltava era uma decisão que nenhuma linhagem pode tomar pela outra.

`PREEXISTING_DEBT` registada e **não corrigida** nesta missão, como mandado:
`scripts/proveniencia.py:175` (`owner` indefinido, 40 `NameError`) e `tests/test_comunicacao.py:222`
(`SystemExit` durante o import mata a coleta do pytest).

`NEXT_SINGLE_STEP` = **decidir D1 — a regra de eleição de `CROP` quando o vocabulário tem N
culturas.** Três saídas, nenhuma derivável da evidência:

- **(a)** `AMBIGUOUS:` vale para todos os países → é preciso decidir antes o que `it_video.py`,
  `it_inventario.py` e o portal fazem com `CROP='AMBIGUOUS:A+B+…+K'` em 100% das falas italianas,
  e reescrever `it_inventario.py:77`, que passa a ser factualmente falso.
- **(b)** `AMBIGUOUS:` só no vocabulário espanhol/injetado, primeiro-casamento no italiano → são
  **duas réguas para o mesmo campo**, e isso tem de ser **declarado**, não improvisado no merge.
- **(c)** Um terceiro critério declarado (ex.: `CROP_ALL` + `CROP_TOP` com peso, no molde de
  `CONTENT_TYPE`/`CONTENT_TYPE_ALL` que já existe no ficheiro) → é desenho novo.

Decidida D1 e registada como política — no molde da `POLITICA-CANONICA-DE-RAW`, que destravou 122
commits — este enxerto entra inteiro. *(Não executado.)*

---
---

# D1 · FECHADA — E O PASSO 01 DESTRAVOU

O bloqueio de §3.3 foi fechado por `docs/regras/POLITICA-CANONICA-DE-CROP.md`
(`RULE_VERSION CROP-D1-2026-09-05`). O mesmo enxerto foi repetido contra o mesmo HEAD e passou.

## A decisão

`CROP_MODEL = CROP_ALL + CROP_PRIMARY` · `MULTI_CROP_SEPARATED_FROM_AMBIGUITY = SIM` ·
`FIRST_MATCH_CANONICAL = NÃO`

As duas linhagens tinham razão sobre metade do problema, e o erro comum era o mesmo:
**tratar pluralidade e incerteza como a mesma coisa.** Agora são campos diferentes.
`AMBIGUOUS` passa a significar apenas ambiguidade **real de mapeamento** — o mesmo trecho de
texto reivindicado por duas culturas. Culturas diferentes em trechos diferentes são
`MULTI` + `RESOLVED`.

## As 17 falas italianas — o mesmo corpus, medido de novo

```
TOTAL = 17
SINGLE = 0    MULTI = 17    NONE = 0
RESOLVED = 17 · AMBIGUOUS = 0 · NO_CROP = 0
CROP_PRIMARY_PROVED = 0
```

A regra anterior marcava estas mesmas 17 falas como **incertas**. Elas nunca foram: são
palestras de convegno que cobrem de 3 a 20 culturas cada, e agora sabemos exatamente quais,
com `MATCHED_TERM` e `EVIDENCE_SPAN` por cultura. `CROP_PRIMARY_PROVED = 0` é honesto e
esperado — não existe ainda regra provada de principalidade, e inventar uma para dar um número
bonito seria o oposto desta política.

## Compatibilidade — medida, não assumida

O campo `CROP` **continua a existir**. Removê-lo faria o consumidor antigo ler a chave ausente
como **ausência de cultura**, que é exatamente o que a §9 proíbe. Valores:

| estado | `CROP` |
|---|---|
| `SINGLE` + `RESOLVED` | o nome da cultura — **idêntico ao anterior** |
| `MULTI` | `MULTI:<A>+<B>+…` — explícito e barulhento, para que quem exige cultura única pare |
| `AMBIGUOUS` | `AMBIGUOUS:<A>+<B>` — o idioma que a casa já usa em `ISSUE` |
| `NONE` | chave ausente, como sempre foi |

> **Camada espanhola: `OLD != NEW` em 0 de 252 vídeos.** `VOCAB_CROP` espanhol tem **uma**
> chave (`OLIVE`), onde o empate é impossível — logo `SINGLE` é sempre o resultado e o campo
> fica byte-a-byte igual. Toda a mudança de comportamento está na camada italiana, onde
> `VOCAB_CROP_IT` tem 25 chaves.

## Testes

`tests/test_crop_d1.py` — **15 testes**, um por lei. Inclui o que prova a lei ao contrário:
`test_o_legado_SIM_muda_com_a_ordem_e_por_isso_nao_e_canonico` embaralha o vocabulário 30 vezes
e exige que `CROP_LEGACY_FIRST` seja **instável** — é a demonstração viva de por que first-match
não podia ser fato canônico.

Um único teste existente falhou: `TestCropNaoDesempataEmSilencio::test_duas_culturas…_AMBIGUOUS`,
que codificava a política **anterior**. Atualizado preservando a sua intenção original (duas
culturas não viram uma escolhida em silêncio) e passando a exigir os cinco campos novos.

## Portões

```
CANONICAL_CONTENT_LOST     = 0
SOURCE_CONTENT_LOST        = 0
NEW_TRACKED_IGNORED        = 0     (mantém-se 1 pré-existente)
NEW_WORKFLOW_BREAKAGES     = 0     (a ref traz 0 workflows)
NEW_TEST_REGRESSIONS       = 0
UNKNOWN_CONFLICTS          = 0
NEW_SEMANTIC_REGRESSIONS   = 0

DICTIONARY_ORDER_AFFECTS_CANONICAL_CROP = NÃO
FIRST_MATCH_USED_AS_CANONICAL_FACT      = NÃO
MULTI_CROP_COLLAPSED_TO_AMBIGUOUS       = NÃO
```

`NEW_TEST_REGRESSIONS` foi medido por **comparação de nomes de falha** em três árvores, não por
contagem bruta: canónica `2b6e35f` = 50 falhas · origem `0cfc182` = 8 · mesclada = 55. A
diferença de conjuntos é **vazia** — toda falha da mesclada já falhava numa das origens. E o
merge **consertou** `test_branch_vivo_nao_e_alvo_congelado`.

> **Um erro meu, apanhado antes de commitar.** A primeira tentativa de resolver `voz.py`
> reconstruiu o ficheiro a partir do lado da origem e **apagou** a capacidade de identidade da
> canónica (`SEM_ID_ESTRUTURAL`, `WITHOUT_STRUCTURAL_ID_COUNT`, `tem_id_estrutural`). O portão
> de não perda apanhou-o. Refeito resolvendo **apenas o trecho em conflito** sobre o que o git
> já tinha auto-mesclado — as duas capacidades sobrevivem.

## Ganho

| | antes `2b6e35f` | depois `5d3a31c` |
|---|---:|---:|
| `DATA_BLOBS` | 388 | **859** |
| `SCRIPT_PATHS` | 143 | **187** |
| `WORKFLOWS` | 18 | 18 |

**Denominador declarado:** caminhos versionados, `git ls-tree -rz` (NUL-safe).
Contagens históricas preservadas como corrigido: canário `187 → 388` dados, `52 → 143` scripts,
`10 → 18` workflows.

## Classificação do ref

`REF_CLASSIFICATION = CANONICAL_INPUT` — o ref entrou **inteiro**. A parte que estava pendente
(`scripts/voz.py`) deixou de ser conflito semântico porque a pergunta passou a ter um dono e uma
regra. A branch original não é apagada.

`CONSUMERS_REQUIRING_MIGRATION` = nenhum bloqueante medido: a camada espanhola não muda, e a
camada italiana chega junto com os seus próprios scripts. Consumidor que venha a exigir cultura
única diante de `MULTI` deve `BLOCK`/`DEFER`/`UNKNOWN`, nunca escolher o primeiro.

---

```
D1_POLICY            = PASS
MERGE_RETRIED        = SIM
MERGE_VERDICT        = PASS   (5d3a31c, pais 2b6e35f + 0cfc182)
P0_2_STEP_01         = PASS
CANONICAL_LINEAGE_STATE        = CANDIDATE_INTEGRATION
DEFAULT_BRANCH_CHANGE_SAFE_NOW = NÃO
```

`PREEXISTING_DEBT` registada e **não corrigida**: `scripts/proveniencia.py:175` e
`tests/test_comunicacao.py:222`.

Pergunta aberta, **não decidida**: `ISSUE` continua com `AMBIGUOUS:A+B` para múltiplos achados.
O mesmo raciocínio da D1 provavelmente aplica-se — um texto pode tratar de várias doenças sem
que isso seja incerteza — mas estender a política a outro campo sem pedido seria criar política
escondida.

`NEXT_SINGLE_STEP` = **P0.2 · PASSO 02 — escolher o próximo enxerto.** *(Não executado.)*

---

## CORREÇÃO — o inventário de consumidores chegou depois do commit

O inventário exigido pela §9 (*medir os consumidores antes de alterar*) só terminou **depois**
de eu ter selado e empurrado o merge. Eu não esperei por ele e escrevi
`CONSUMERS_REQUIRING_MIGRATION = nenhum bloqueante` como se fosse medido. **Não era.**

O inventário encontrou **mais de 20 consumidores que exigem cultura única**, vários com falha
silenciosa: `pacote_montar.py:115` (`crop[:4]` — `'MULT'` não casa nada), `v21_normalizar.py:165`
(`crop_id()` devolve `None`, e é o estrangulamento de todo o v21), `catalogo_importar.py:227`
(CROP dentro de chave de tuplo), `it_rotulo_selar_v2.py:55` (CROP como chave de dict alimentando
o gate `NO_CROP_REGRESSION`), `it_rotulo_testemunha.py:27` (**CROP entra num digest sha256**),
`radar_v21.py:271` (`== 'OLIVO'`, e é o KPI impresso do radar).

**A conclusão sobrevive, mas por um motivo que eu não tinha verificado.** Rastreado agora,
caminho a caminho:

| quem produz MULTI | quem consome |
|---|---|
| `marcar_assunto` / `pipeline_video` **só** com vocabulário multi-chave — `it_audio.py:288,290,558` e `it_video.py:477` | grava em `IT-VOZ-AUDIO-V2/` e `IT-VIDEO-V1/` |

Os consumidores sinalizados **não leem esses caminhos**:

- `v21_*`, `radar_v21`, `it_rotulo_*`, `catalogo_importar` leem `IT-ROTULOS-V1/` e
  `IT-RADAR-V21/` — a cadeia de **rótulo e regulatório**, produzida pelo parser de rótulos,
  não por `marcar_assunto`.
- `it_cruzamentos.py` tem os valores de `CROP` **escritos à mão no próprio script** (uma tabela
  curada), incluindo já um MULTI em prosa: `'CROP': 'MELO (e pero, pesco, actinidia)'`.
- `it_inventario.py` **não lê** o campo `CROP` — calcula as suas próprias marcas com
  `marcas(campo, VOCAB_CROP_IT, 'CROP')`.

`CONSUMERS_REQUIRING_MIGRATION = 0 alcançáveis hoje` — mas a lista dos 20+ fica registada,
porque no dia em que um deles passar a ler `IT-VIDEO-V1` recebe `MULTI:` e quebra. O `MULTI:`
explícito é o que faz essa quebra ser **visível** em vez de silenciosa.

Duas coisas mais que o inventário trouxe e que eu tinha deixado passar:

1. **Os campos D1 sobrevivem ao contrato.** `CAMPOS_VIDEO` tem `CROP` entre os 32, mas é um
   **mínimo**, não um filtro: verificado por execução real do `pipeline_video`, o registro sai
   com **46 campos**, incluindo os nove `CROP_*`.
2. **`it_inventario.py:77` ficou factualmente falso.** O comentário dizia que `marcar_assunto`
   *"para no primeiro casamento por desenho"*. Esse desenho acabou. Corrigido — e vale registar
   que a função `marcas()` daquele ficheiro já fazia, como remendo local, exatamente o que a D1
   agora faz na regra canónica. A linhagem italiana tinha chegado à mesma conclusão primeiro.

`territorial_medir.py:98` é o único consumidor da canónica que já normaliza escalar-ou-lista —
mas **não trata o prefixo**, então leria `'MULTI:A+B'` como uma cultura só chamada `MULTI:A+B`.
Não é alcançável hoje pelo mesmo motivo dos outros; fica na lista.
