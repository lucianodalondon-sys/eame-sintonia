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
