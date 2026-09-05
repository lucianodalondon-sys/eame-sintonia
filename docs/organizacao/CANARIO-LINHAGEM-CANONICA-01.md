# CANÁRIO DA LINHAGEM CANÔNICA · 01

Prova de que o SINTONIA pode ser reunido numa única casa **sem perder coleta, dados,
scripts ou história** — testada com um único enxerto real.

**Data:** 2026-09-05 · **Modo:** integração local, sem push, sem deploy, sem mudança de default branch.

---

## 1 · LINHA DE INTEGRAÇÃO

| | |
|---|---|
| `FUTURE_CANONICAL_BRANCH` | `sintonia/canonical` — **criada** |
| `BASE_COMMIT` | `c88690caf514efb18909abbcb943202e891900cd` |
| `WORKTREE_CLEAN` | **SIM** (antes e depois) |
| `DEFAULT_BRANCH_AT_START` | `claude/sintonia-eame-repo-setup-xccfob` — **não alterada** |

> **Fato que a missão não previa:** o repositório **não tem `main`, `master` nem `develop`**.
> São 48 heads remotos, todos `claude/*` ou `sprint/*`. O `ROOT c88690c` **é** o head da
> default branch atual. Criar `sintonia/canonical` a partir dele é criar a partir da default —
> por isso a operação é aditiva e não desloca nada.

## 2 · ENXERTO — resolução do HEAD

O nome dado na missão não é um ref completo. Resolvido contra `git ls-remote`:

| | |
|---|---|
| ref real | `refs/heads/claude/adama-italia-product-intelligence-deep` |
| `SOURCE_HEAD` | `06a5785b79d9e1d749f773403272663f5b6fb2e2` |
| `merge-base` com a base | `841fb544a250c45eebec4eb4f66f27b9d6dd17dc` |
| divergência | base **+2** commits · source **+122** commits |

Também resolvido, **e não usado nesta missão**: `INTELLIGENCE_SEMANTIC_AUTHORITY
55c2674b785a3a373ef0bad2812c244ed80c31eb` é o head de **duas** branches —
`claude/opportunity-commercial-priority-v1` e `claude/trilha-universal-inteligencia-a5rx9d`.

Merge Git real tentado (`--no-commit --no-ff`). Nenhum ficheiro copiado, nenhum cherry-pick.

## 3 · INVENTÁRIO ANTES DO MERGE

| Métrica | BASE `c88690c` | SOURCE `06a5785` | NOVO no source |
|---|---:|---:|---:|
| `DATA_BLOBS` (`data/**`) | 177 | 371 | **+201** |
| `SCRIPT_PATHS` (`scripts/**`) | 52 | 140 | **+91** |
| `WORKFLOWS` (`.github/workflows/*.yml`) | 10 | 17 | **+8** |
| ficheiros totais | 317 | 1.051 | +745 |

**Só na base (o que o merge tinha de preservar):** 7 data · 3 scripts · 1 workflow · 11 caminhos.

## 4 · CONFLITOS

`CONFLICT_COUNT = 2`

| # | Caminho | Classe | Veredito |
|---|---|---|---|
| 1 | `.gitignore` | **COLLECTION** | **BLOQUEIA** — incompatível como escrito |
| 2 | `data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json` | **MECHANICAL** | resolúvel com prova |

### 4.1 · Conflito 2 — MECHANICAL, com prova

Diff semântico, não textual: as duas versões têm **`ACCOUNTS` idênticos, `EXCLUDED_ACCOUNTS`
idênticos e zero chaves com valor divergente**. A versão da base é **superconjunto estrito**:
acrescenta `CAPTURED_AT` e `CAPTURED_AT_POR_QUE`. Tomar a base não perde nada do source —
toda chave e todo valor do source estão presentes e iguais. Resolução provada, não arbitrada.

### 4.2 · Conflito 1 — COLLECTION, e é aqui que o canário canta

Duas políticas **deliberadas, documentadas e opostas** sobre a mesma coisa.

**Base** ignora apenas diretórios de bruto, e o comentário diz por quê:
> *"A regra é ESCOPADA ao Instagram de propósito. As missões 14 e 15 commitam `.gz` nos
> caminhos delas, e um ignore global as quebraria em silêncio."*

**Source** ignora por glob global:
> *"Daqui para frente o bruto pesado vai para Storage; o Git guarda hash e manifesto."*
> `data/samples/**/*.gz` · `data/samples/**/*.raw.json`

**Por que a união não serve.** A união aplica o glob global — exatamente o que a base
declara que "quebraria em silêncio". Medido:

- **51 `.gz` versionados** em `data/samples/ES-T4-005/` e `data/samples/raw-paid/`, **idênticos nas duas árvores**. Já rastreados, logo intocados pelo ignore — a colisão é sobre o **futuro**.
- `scripts/youtube_janela.py:129` e `scripts/instagram_janela.py:373` escrevem `.html.gz` sob `data/samples/*-JANELA/html-bruto/` — e a base já ignora **esses** caminhos. Logo o `.gz` que a base quer preservar versionável é o das **rotas pagas**, não o do html bruto.
- O comentário do source fala em **"12 blobs .gz existentes"**; a árvore tem **51**. O número está desatualizado em relação à própria árvore onde está escrito.

Escolher qualquer um dos lados anula uma decisão consciente da outra linhagem, em silêncio.
Inventar um terceiro caminho (glob global + negações) seria criar uma política que **nenhuma
das duas linhagens escreveu**. Nenhuma das três coisas é "resolver com prova".

**Merge abortado.** `git merge --abort` · HEAD volta a `c88690c` · working tree limpa.

## 5 · PORTÃO DOS WORKFLOWS

Não há árvore mesclada para medir. Medido **separadamente nas duas linhagens**:

| | `WORKFLOWS_TOTAL` | `WITH_ALL_REFERENCED_SCRIPTS` | `WITH_MISSING_SCRIPT` |
|---|---:|---:|---:|
| BASE | 10 | 7 | **3** |
| SOURCE | 17 | 14 | **3** |

Referências quebradas **já existentes antes de qualquer merge**, nas duas:
`apify-creator-corpus.yml` → `creator_corpus.py`, `creator_corpus_coleta.py` ·
`apify-creators.yml` → `creator_coleta.py` · `linkedin-prova-busca.yml` → `linkedin_prova_busca.py`.

O source **conserta uma**: `scripts/apify_contrato.py` existe nele e falta na base.
Nenhuma quebra seria **causada** pelo merge. Workflows concorrentes não arbitrados, como mandado.

## 6 · PORTÃO DE NÃO PERDA

Sem merge concluído, não há perda a medir — e também não há prova de ausência de perda.

| | |
|---|---|
| `BASE_DATA_LOST` / `BASE_SCRIPTS_LOST` / `BASE_WORKFLOWS_LOST` | **NÃO MEDIDO** — merge não concluído |
| `SOURCE_CONTENT_LOST` | **NÃO MEDIDO** — merge não concluído |
| perda ocorrida no repositório | **0** — nada foi escrito, nada foi apagado |

## 7 · TESTES

| Teste | Resultado |
|---|---|
| `git fsck` | **limpo**, sem erro |
| working tree | **limpa** |
| JSON válido | BASE 116/116 · SOURCE 355/355 |
| YAML de workflow válido | BASE 10/10 · SOURCE 17/17 |
| scripts referenciados existem | ver §5 |
| suíte local existente | BASE: **nenhuma** (só `tests/.gitkeep`) · SOURCE: **suíte real** (`test_canonico.py`, `test_coleta_externa.py`, `test_apify_pool.py`, …) |

A base não tem testes para rodar. Os do source só rodariam sobre a árvore mesclada, que não existe.

## 8 · GANHO

Métricas pós-merge **não medidas**, porque não há merge. O delta abaixo é **projeção do
inventário**, não medição de resultado:

| | valor |
|---|---|
| `DATA_BLOBS_AFTER` / `SCRIPT_PATHS_AFTER` / `WORKFLOWS_AFTER` | **NÃO MEDIDO** |
| ganho projetado de dados | +201 blobs (177 → 378 se nada colidir) |
| ganho projetado de scripts | +91 caminhos (52 → 143) |
| ganho projetado de workflows | +8 (10 → 18) |
| `UNACCOUNTED_DATA` / `UNACCOUNTED_SCRIPTS` antes/depois | **NÃO MEDIDO** — exigiria definir "não contabilizado", o que é auditoria nova, vedada nesta missão |

## 9 · ESTADO

`CANONICAL_LINEAGE_STATE = CANDIDATE_INTEGRATION`
Branch existe e aponta para `c88690c`. Não é `PRODUCTION_CANONICAL`. Default branch inalterada.

---

## VEREDITO

```
CANONICAL_BRANCH_CREATED     = SIM  (sintonia/canonical @ c88690c, local)
MERGE_COMPLETED              = NÃO  (abortado no conflito de política de coleta)
SEMANTIC_CONFLICTS           = 0    (nenhum INTELLIGENCE_SEMANTIC; 1 COLLECTION bloqueante)
BASE_CONTENT_LOST            = 0
SOURCE_CONTENT_LOST          = 0
WORKFLOW_REFERENCES_BROKEN   = 0 causadas pelo merge (3 pré-existentes em cada linhagem)
DATA_COVERAGE_GAIN           = NÃO MEDIDO (projeção: +201 blobs)
SCRIPT_COVERAGE_GAIN         = NÃO MEDIDO (projeção: +91 caminhos)

CANARY_VERDICT               = BLOCKED
DEFAULT_BRANCH_CHANGE_SAFE_NOW = NÃO
```

**O canário funcionou.** No primeiro enxerto real, com 122 commits e 745 caminhos novos,
apareceram **2 conflitos** — e apenas **1** exige decisão humana. Não é um sinal de que a
casa única é inviável: é o oposto. A mecânica de junção é sólida (história preservada,
zero perda, zero conflito semântico de inteligência); o que falta é **uma decisão de política
que nenhuma das duas linhagens tem autoridade para tomar sobre a outra**.

`NEXT_SINGLE_STEP` = decidir a política de versionamento de `.gz` e `.raw.json` sob
`data/samples/` — permanecem versionáveis nas rotas pagas (linhagem base) ou passam a
Storage com hash e manifesto no Git (linhagem source)? Registrar a decisão como regra
explícita **antes** de repetir o merge. Um único `.gitignore` acordado destrava os 122 commits.

---
---

# ATUALIZAÇÃO · 2026-09-05 — CANÁRIO DESTRAVADO E EXECUTADO

O bloqueio de §4.2 foi fechado por `docs/regras/POLITICA-CANONICA-DE-RAW.md`. O merge
correu. Os portões correram sobre a árvore integrada. Este bloco substitui o veredito acima.

## Durabilidade primeiro

`sintonia/canonical` empurrada para o remoto — `f38d874`, local = remoto, fast-forward,
sem force. Default branch (`claude/sintonia-eame-repo-setup-xccfob`) **intocada**.

## Como o `.gitignore` foi resolvido — nem `ours`, nem `theirs`, nem união cega

| decisão | o quê |
|---|---|
| **preservado** | regras escopadas da base: `*-JANELA/html-bruto/`, `*-TRANSCRICOES/audio-cache/` |
| **adotado da origem** | `.tmp/`, `italia-portale/audit/.scratch/`, `build/ITALY-REALITY-HANDOFF-V2.1/` — rascunho e build, capacidades compatíveis |
| **deliberadamente omitido** | `data/samples/**/*.gz`, `data/samples/**/*.raw.json` — bloqueado pela política até os quatro gates de Storage passarem |

O texto das duas linhas omitidas fica **preservado como comentário documentado no próprio
ficheiro**, com o motivo e `STORAGE_MIGRATION_STATE = PENDENTE`. Omitir uma regra de ignore
rastreia **mais** ficheiros, nunca menos — por isso a omissão não pode perder nada.

**Contraprova medida:** injetando as duas regras omitidas, os ficheiros rastreados-e-ignorados
saltam de **1 para 62**. O merge **reduziu** a superfície de perda silenciosa, de 62 (estado
da linhagem de origem) para 1 (herdado, pré-existente).

## Portões — árvore integrada `f38d874`

### Não perda · **PASS**

`REESCRITOS: 1` (só o `.gitignore`) · `COM_PERDA: 0` · `VERSIONADOS_AGORA_IGNORADOS: 0`

O teste que importava não era o dos caminhos — era o do **conteúdo**. 306 caminhos existem
nas duas linhagens; **52 divergem**. Análise de três vias contra a merge-base real `841fb54`:
50 são só-a-origem-mudou (fast-forward por ficheiro, nada a perder), 1 é o `.gitignore`,
1 é o `PUBLIC-COMM-FIRST-BATCH-EAME.json` — superconjunto estrito, provado por `json.loads`
dos dois blobs: zero chaves só na origem, zero valores divergentes.

> **O comando que eu prescrevi estava errado, e o portão pegou.** `git check-ignore -q` **não**
> reporta caminhos já rastreados sem `--no-index`: o loop devolvia vazio *por construção* —
> falso negativo. Refeito corretamente, existe **1** rastreado-e-ignorado
> (`data/raw/IT-ROTULOS/_MANIFESTO.json`, regra `data/raw/*`), **pré-existente**: veio inteiro
> da origem, onde já era rastreado-e-ignorado. Causado pelo merge: **0**.

### Imports e caminhos · **PASS**

`COMPILE_FAIL: 0` (165 ficheiros) · `IMPORTS_LOCAIS_QUEBRADOS: 0` (35 módulos locais, 24
`from ... import` conferidos símbolo a símbolo) · `PATHS_AUSENTES: 30` · `NOVOS_PELO_MERGE: 0`

Dos 30 caminhos ausentes: 7 são prosa de relatório, 6 são escrita (criados com `makedirs`),
7 são templates `%s`, 4 são `NÃO SEI` — e **6 são leitura real que não resolve**, porque as
branches citadas no próprio código (`claude/eame-meta-competitor`, `claude/adama-it-local-catalog`)
não existem neste clone. A degradação é explícita: `ler_git` devolve `None` e o script
imprime `NAO_ACHEI_O_REGULATORIO`. Nenhum é causado pelo merge.

Verificação **estática** (`ast`), declarado: os módulos não foram importados de facto porque
vários têm efeito colateral de coleta em nível de módulo.

### Suíte de testes · **PARTIAL — e nenhuma falha é do merge**

```
MESCLADA (f38d874): 678 passed · 56 failed · 5 errors · 16 skipped
ORIGEM   (06a5785): 677 passed · 57 failed · 5 errors · 16 skipped
NOVAS_FALHAS CAUSADAS PELO MERGE: 0
```

A suíte **não passa** — e não passava antes. Três causas, todas anteriores ao merge:

1. **Bug de código real.** `scripts/proveniencia.py:175` — `def carregar():` sem parâmetro,
   mas o corpo faz `if owner is None` e `v.get('DATASET_OWNER') == owner`. **40 ocorrências**
   de `NameError: name 'owner' is not defined`. Introduzido no commit `4724282`
   (*"toda execução passa a ter dono"*), **antes** do merge — `git diff 06a5785 HEAD` do
   ficheiro é **vazio**, byte-idêntico nas duas linhagens.
2. `tests/test_comunicacao.py:222` faz `raise SystemExit(1)` durante o import, o que **aborta
   a coleta inteira do pytest** nas duas árvores. Os números acima excluem esse ficheiro:
   *não existe* um número de "suíte inteira via pytest" para reportar, em nenhuma das duas.
3. 5 `errors` exigem uma ref remota não buscada neste ambiente.

## Correção de um número meu

A política canônica dizia **51** blobs `.gz`. São **61** (60 em `raw-paid/`, 1 em `ES-T4-005/`).
`git ls-tree` aspa nomes com acento e o `grep` que usei perdeu 10. Corrigido na política, com
o método (`git ls-files -z`) registado para não repetir.

## VEREDITO ATUALIZADO

```
RAW_POLICY_CANONICAL           = SIM
CANONICAL_BRANCH_PUSHED        = SIM   (f38d874, local = remoto)
MERGE_COMPLETED                = SIM   (pais 5b6d94b + 06a5785, história preservada)
SEMANTIC_CONFLICTS             = 0
BASE_CONTENT_LOST              = 0
SOURCE_CONTENT_LOST            = 0
WORKFLOW_REFERENCES_BROKEN_NEW = 0     (o merge ainda consertou 1: apify_contrato.py)
TESTS_PASS                     = NÃO   (56 failed / 5 errors — 0 causados pelo merge)

CANARY_VERDICT                 = PASS
DEFAULT_BRANCH_CHANGE_SAFE_NOW = NÃO
CANONICAL_LINEAGE_STATE        = CANDIDATE_INTEGRATION
```

**Por que PASS com a suíte a falhar.** O canário mede **segurança de integração**, não saúde
do repositório. Nesse critério tudo passou: zero perda dos dois lados, zero conflito semântico
de inteligência, zero referência nova quebrada, zero falha nova de teste, e a superfície de
perda silenciosa **diminuiu**. As 56 falhas são dívida herdada das duas linhagens, e agora
estão medidas e localizadas em vez de espalhadas — o que é o objetivo de reunir a casa.

`NEXT_SINGLE_STEP` = iniciar **P0.2 — integração progressiva da casa**. *(Não executado.)*

Dívida registada, fora do escopo deste canário e **não corrigida** aqui:
`scripts/proveniencia.py:175` (`owner` indefinido, 40 testes) e `tests/test_comunicacao.py:222`
(`SystemExit` mata a coleta do pytest). Ambas anteriores ao merge, ambas agora com endereço exato.
