# IDENTIDADE DA OBSERVAÇÃO RAW — C-PLAN-0

**Decisão contratual · 2026-09-10 · ramo `claude/raw-observation-identity-3jbwco`**

> **Nada foi implementado.** Zero código de runtime, zero migration, zero DDL, zero
> `INSERT`/`UPDATE`/`DELETE`, zero upload, zero alteração de Bíblia, System Map ou
> Collection. Este documento **mede e decide** — não executa.

Esta é a pergunta única, e a única coisa que este documento fecha:

> **O que identifica UMA observação RAW no SINTONIA, e como um retry da mesma
> tentativa deixa de criar uma observação falsa nova?**

Ele **estende** [`IDENTIDADE-DO-ARTEFATO.md`](IDENTIDADE-DO-ARTEFATO.md), que já separou
`CONTENT` · `CAPTURE` · `STORAGE COPY` · `ARTIFACT` · `DERIVED`. O que faltava lá é o que
se fecha aqui: **a espécie `CAPTURE` nunca ganhou um identificador próprio**, e por isso
três chaves diferentes andam a fazer o trabalho dela ao mesmo tempo.

---

## 0 · A CONTRADIÇÃO QUE MOTIVOU A MISSÃO, E O QUE A MEDIÇÃO DISSE

A V1.1 declarou duas coisas que não cabem juntas:

```
RAW_OBSERVATION_ID = (RUN_ID, SOURCE_ID, DOCUMENT_ID, CONTENT_SHA256, CAPTURED_AT)

mesma corrida + mesma fonte + mesmo documento + mesmos bytes + retry = REUSED
```

Se `CAPTURED_AT` muda entre a primeira tentativa e o retry, a chave muda, e o retry
deixa de ser reencontro. **A contradição é real, e foi reproduzida** — não inferida.

Sonda executada contra o banco descartável do próprio repositório
(`guarda/memoria_descartavel.py`), chamando o dono canónico da escrita
(`guarda/preservar_coleta.py::preservar`) sem tocar em produção:

| caso | esperado pela V1.1 | **medido hoje** |
|---|---|---|
| mesma corrida · mesmos bytes · `captured_at` **congelado** | `REUSED` | `REUSED_METADATA = 1` · `RUN_STATE = COMPLETE` ✅ |
| mesma corrida · mesmos bytes · `captured_at` **30 s depois** | `REUSED` | `METADATA_CONFLICT` · `RUN_STATE = PARTIAL` ❌ |
| **nova corrida** · mesma fonte · mesmo documento · mesmos bytes | nova observação | `METADATA_CONFLICT` · `RUN_STATE = PARTIAL` ❌ |
| mesma corrida · mesmo documento · **bytes diferentes** | nova observação | 2 linhas · `COMPLETE` ✅ *(mas por acidente — ver §5)* |

A divergência do retry vem, campo a campo, do próprio relatório da sonda:

```
CAMPO: captured_at   NO_BANCO: 2026-09-08T00:00:00Z   NESTA_CORRIDA: 2026-09-08T00:00:30Z
```

E o porquê está numa linha só, em `guarda/preservar_coleta.py:81`:

```python
IDENTIDADE_DO_OBJETO = ("run_id", "sha256", "bytes", "captured_at", "source_url")
```

> ## O RETRY NÃO CRIA UMA OBSERVAÇÃO FALSA HOJE.
> ## ELE CRIA UM **CONFLITO FALSO**, E A CORRIDA NÃO FECHA.
> A falha é outra; a raiz é a mesma — `CAPTURED_AT` está dentro de uma chave.

---

## 1 · O ESTADO MEDIDO

### 1.1 Ramo e árvore

| | |
|---|---|
| `BRANCH` | `claude/raw-observation-identity-3jbwco` |
| `INITIAL_HEAD` | `572647dce8a38b8835aafa6f9e3e42d2652fbcd9` |
| `WORKTREE` | limpa antes e depois da medição |

> ⚠️ **Correção do estado declarado na missão.** A missão deu
> `BRANCH = claude/collection-plumbing-canonical-v1 @ 572647d`. O ramo de trabalho
> designado, `claude/raw-observation-identity-3jbwco`, tinha nascido de `origin/main`
> (`df165da9`) e **não continha** o trabalho do encanamento — 343 ficheiros de diferença.
> Foi reancorado em `572647dc` **antes** de qualquer medição. O `HEAD` declarado está
> certo; o ramo em que ele vivia é que era outro.

### 1.2 Os números do livro de observações

Fonte: `data/collection-ledger/italy/observations.ndjson` · `runs.ndjson`.

| medida | valor |
|---|---|
| `RAW_OBSERVATIONS_TOTAL` | **144** em **6** corridas |
| `RUN_ID_PRESENT` | 144 / 144 |
| `SOURCE_ID_PRESENT` | 144 / 144 |
| `DOCUMENT_ID_PRESENT` | 144 / 144 · zero sentinelas (`UNKNOWN`, `""`, `null`) |
| `CONTENT_SHA256_PRESENT` | 144 / 144 · todos com 64 hex |
| `CAPTURED_AT_PRESENT` | 144 / 144 |
| conteúdos distintos | **35** |
| `SAME_RUN_SAME_CONTENT_CASES` | **0** |
| `CROSS_RUN_SAME_CONTENT_CASES` | **35 de 35** — todo conteúdo aparece em mais de uma corrida |
| trios `(RUN_ID, SOURCE_ID, DOCUMENT_ID)` repetidos dentro da mesma corrida | **0** |

E a medida que decide a missão inteira:

```
valores distintos de CAPTURED_AT  =  144
linhas                            =  144
CAPTURED_AT == COLLECTION_RUN_STARTED_AT  em  0  linhas
```

**Cada observação tem um `CAPTURED_AT` só seu.** Ele nunca é a hora da corrida; é uma
leitura de relógio por tentativa.

### 1.3 A cardinalidade que fecha a hipótese antes de a discutir

```
(RUN_ID, SOURCE_ID, DOCUMENT_ID, CONTENT_SHA256)                 →  144 valores distintos
(RUN_ID, SOURCE_ID, DOCUMENT_ID, CONTENT_SHA256, CAPTURED_AT)    →  144 valores distintos
```

> ## `CAPTURED_AT` NÃO ACRESCENTA UM ÚNICO PODER DE DISTINÇÃO.
> Em 144 observações reais ele separa **zero** pares que a chave de quatro campos já não
> separasse. Ele não paga o risco que traz; só o traz.

### 1.4 `RETRY_CASES_PROVABLE` — **NÃO SEI**, e o motivo é estrutural

O coletor faz retry de transporte (`coleta/italy_pilot_collect.mjs:66-88`,
`baixar(url, tentativas = 2)`), e regista `retries: r.tentativas` **apenas no caminho de
falha** (`:292`). No caminho de sucesso (`:369-381`) o número de tentativas é **descartado**.

```
linhas do livro com o campo `retries`   =  0
linhas com HEALTH_STATE = FAILED        =  0
```

Logo: `RETRY_CASES_PROVABLE = NÃO SEI`. Não é que não tenha havido retry — é que **um
retry bem-sucedido não deixa rasto nenhum**. Isto é uma lacuna de telemetria, e entra em
§9 como consequência, não como suposição.

`REUSED_CASES_PROVABLE` em dado de produção = **0**: nenhuma das 6 corridas do piloto
passou por `preservar()` para um banco. O único `REUSED` provado é o do banco descartável
desta sessão (§0).

### 1.5 O banco ao vivo

`SUPABASE_DB_URL` · `SUPABASE_URL` · `SUPABASE_SERVICE_ROLE_KEY` · `DATABASE_URL` · `PGURI`
— **todos ausentes** nesta sessão. Contagem de linhas em `raw_asset` ao vivo = **NÃO SEI**.
Tudo o que se afirma abaixo sobre o esquema vem do esquema **versionado**
(`supabase/migrations/001` e `022`), que esta sessão leu.

---

## 2 · AS QUATRO IDENTIDADES, SEPARADAS

Elas nunca podem ser a mesma coisa em silêncio. Hoje, três delas são — e **nenhuma** é a
identidade da observação.

| | o que responde | chave decidida | o que faz esse papel **hoje** |
|---|---|---|---|
| **A · OBSERVATION** | *o que foi observado, e por quem, quando* | **surrogate estável**, criado uma vez | ✖ **não existe** |
| **B · CONTENT** | *quais bytes* | `sha256` dos bytes brutos | `sha256`, e também `ARTIFACT_ID = RAW-<sha16>` |
| **C · STORAGE** | *onde os bytes estão* | `storage_path` — **endereço** | `storage_path`, **`UNIQUE`** — é a identidade de facto |
| **D · ATTEMPT** | *quantas tentativas foram precisas* | **não é entidade** — é telemetria | ✖ descartado no sucesso |

### As três usurpações medidas

**1. O endereço é a identidade.** `supabase/migrations/001:106` —
`storage_path text not null unique`. É a **única** trava natural de `raw_asset`.
`sha256` é índice, não trava (`001:119`), e isso está certo. Mas com `storage_path`
único e mais nada, a pergunta *«é a mesma observação?»* é respondida pelo caminho do
ficheiro. Mover o ficheiro é mudar a identidade.

**2. O conteúdo é a identidade.** `leis/artefato.py:142-144` —

```python
curto = sha256[:16]
if tipo == RAW:
    return f"RAW-{curto}"
```

`ARTIFACT_ID` é função **pura** dos bytes. Duas idas independentes à fonte, em dias
diferentes, por rotas diferentes, recebem o **mesmo** `ARTIFACT_ID`. Medido nos 43
derivados de `data/derivados/REGISTO-DE-ARTEFATOS.json`: 43 de 43 apontam o pai por
`PARENT_ARTIFACT_ID = RAW-<sha16>`, isto é, **pelo conteúdo**.

**3. A hora da tentativa é a identidade.** `guarda/preservar_coleta.py:81`, já citada.

E o esquema **declara** o contrário do que **enforça**. `022_o_derivado_ganha_casa.sql:62`:

> *«Em `raw_asset` o grão é a OCORRÊNCIA, porque duas capturas são DOIS FACTOS SOBRE O
> MUNDO.»*

Grão de ocorrência declarado; grão de caminho enforçado. É a distinção
`DECLARED / CODE / OBSERVED` da COL-LAW-049 a abrir dentro da tabela mais central da coleta.

---

## 3 · A DECISÃO

```
RAW_OBSERVATION_ID   =  SURROGATE ESTÁVEL, atribuído UMA VEZ, nunca recalculado
                        (hoje já existe: raw_asset.id bigserial — não é coluna nova)

IDEMPOTENCY_KEY      =  (RUN_ID, SOURCE_ID, DOCUMENT_KEY, CONTENT_SHA256)

CAPTURED_AT          =  FACTO SOBRE A OBSERVAÇÃO. Nunca chave.
                        Congelado no instante da PRIMEIRA busca bem-sucedida
                        destes bytes dentro desta observação. Escrito uma vez.
                        NUNCA reescrito por retry.

ATTEMPTS             =  telemetria: contador + LAST_ATTEMPT_AT. Nunca chave.
```

### 3.1 Por que `SURROGATE`, e não chave natural composta

`RAW_OBSERVATION_ID_KIND = SURROGATE`. Três razões, todas medidas:

1. **A chave natural tem um campo que pode faltar.** `DOCUMENT_ID` é `null` em quatro
   caminhos do coletor (`:281`, `:292`, `:302`, `:310`). Uma chave primária composta com
   um campo anulável não é uma chave primária.
2. **Um filho não deve carregar o pai inteiro.** `derived_artifact` (migration 022) já
   aponta o pai por `raw_asset_id` + `parent_sha256`. Trocar isso por uma tupla de quatro
   campos espalharia `RUN_ID` e `SOURCE_ID` por todas as tabelas filhas.
3. **A casa já elegeu surrogate e provou que funciona.** `raw_asset.id` é `bigserial`
   desde a 001, e a 022 já se apoia nele (`unique (id, sha256)`).

**Os dois não são a mesma coisa, e não devem ser forçados a ser.** O surrogate é o
**nome** da observação. A chave de idempotência é a **pergunta** *«já vi isto nesta
corrida?»*. Confundi-los é o que faz a hora da tentativa acabar dentro de um `PRIMARY KEY`.

### 3.2 Por que `CAPTURED_AT` sai da chave — e não é opinião

- **Medição:** 144 valores distintos em 144 linhas; poder de distinção adicional = 0 (§1.3).
- **Código:** `const CAPTURED_AT = agora();` (`italy_pilot_collect.mjs:288`) executa
  **depois** de `await baixar(...)` — é o relógio no instante em que a resposta voltou,
  não um marco lógico. `agora()` é `new Date().toISOString()` (`:39`).
- **Lei já escrita.** A COL-LAW-034 já decidiu isto, para o checkpoint:

  > *«A IDENTIDADE DO CHECKPOINT NÃO PODE MUDAR ENTRE EXECUÇÕES. `TOKEN`, `RUN_ID`,
  > `DATASET_ID` e `CAPTURED_AT` **NÃO DEVEM** entrar nela — retomar por outra chave
  > duplicaria a coleta inteira.»*

  A observação RAW não é o checkpoint, mas o raciocínio é idêntico, e a casa já o aceitou
  uma vez. **Esta decisão não abre lei nova; aplica uma que já existe ao vizinho de porta.**

### 3.3 `DOCUMENT_KEY` — como se resolve o campo que pode faltar

`DOCUMENT_ID = UNKNOWN` **não** entra em chave nenhuma. Em Postgres seria pior do que
inútil: `NULL` não colide com `NULL`, e a trava de idempotência deixaria passar exatamente
os duplicados que existe para travar.

A casa **já tem** a regra, escrita e a correr, em `coleta/ingresso.py:191`:

```python
nativo = (item.get("SOURCE_NATIVE_ID") or item.get("ID")
          or item.get("id") or f.SHA256[:16])
```

e o comentário diz o porquê: *«o identificador nativo, quando a fonte não o deu, é o
próprio sha — que é verdade sobre os bytes, e não um nome escolhido por nós.»*

Decisão, sem inventar nada:

```
DOCUMENT_KEY        =  DOCUMENT_ID          quando a fonte dá identidade semântica
                    =  CONTENT_SHA256       quando não dá

DOCUMENT_KEY_BASIS  =  SOURCE_DOCUMENT_ID | CONTENT_DERIVED
```

O `BASIS` ao lado é obrigatório. **Substituição declarada não é o mesmo que campo
preenchido a fingir**, e sem o `BASIS` nenhum leitor futuro sabe qual dos dois está a ler.

**Classes reais medidas:**

| classe | tem identidade semântica de documento? | prova |
|---|---|---|
| documentos regulatórios/agrometeo IT | **sim, 13 de 13** | todo contrato declara `DOCUMENT_ID_RULE` (`regras/italy_contracts.mjs`), e há guarda que o exige (`italy_contract_test.mjs:188`) |
| conteúdo social (vídeo, post) | **sim** | `UNIQUE (canal_id, content_id)` em `003:57` |
| documento de catálogo de fabricante | **sim** | `document_id` em `guarda/catalogo_importar.py:179` |
| ingresso genérico sem id da fonte | **não** | recai em `sha256[:16]` por `ingresso.py:191` |

`CLASSES_MEDIDAS_SEM_DOCUMENT_ID = 0` no dado de hoje. A regra do `BASIS` existe para o
dia em que aparecer uma — e existe porque **o código já a tinha**, não porque este
documento a inventou.

### 3.4 `SOURCE_ID` faz parte da identidade lógica? **SIM**

Evidência, não preferência:

- O próprio coletor já testa reencontro por fonte **e** documento
  (`italy_pilot_collect.mjs:315`): `o.SOURCE_ID === sourceId && o.DOCUMENT_ID === ident.DOCUMENT_ID`.
- 144 / 144 observações carregam `SOURCE_ID`.
- Os `DOCUMENT_ID` reais são **prefixados pela fonte** (`ARPAV:Z01:…`, `TERRETRURIA:…`,
  `SIAS:…`). Esse prefixo é `SOURCE_ID` disfarçado de texto — a prova de que a identidade
  precisa dele mesmo onde a coluna não existe.
- COL-LAW-205 separa `SOURCE` · `ENDPOINT` · `ROUTE`. Sem `SOURCE_ID`, duas fontes que
  publicassem o mesmo documento colidiriam.

**Hoje `raw_asset` não tem `source_id`.** Ele sobrevive apenas *dentro da string* de
`storage_path` (`PAÍS/FONTE/TIPO/…`, `preservar_coleta.py:222`). É dívida de esquema,
registada em §9. **Esta missão não a corrige.**

---

## 4 · CONTENT IDENTITY — a lei continua correta

```
CONTENT_SHA256  =  identidade dos BYTES              ✅ continua
CONTENT_SHA256  ≠  identidade da OBSERVAÇÃO          ✅ continua
```

E continua **provado no dado**: 144 observações sobre **35** conteúdos, e os 35 aparecem
em mais de uma corrida. `IDENTIDADE-DO-ARTEFATO.md` já tinha medido o mesmo do outro lado —
seis grupos, `6 de 6 INDEPENDENT_CAPTURES_SAME_CONTENT`, com a hora confirmada pelo
cabeçalho `date:` do próprio servidor.

`sha256` **NÃO DEVE** ganhar `UNIQUE` em `raw_asset`, nunca. A trava que faltava nunca
esteve lá, e é bom que não esteja.

Uma correcção de vocabulário fica registada: **`ARTIFACT_ID = RAW-<sha16>` é uma
identidade de conteúdo com nome de identidade de artefato.** Como identificador de bytes
é determinístico e útil. Como identidade de observação colapsaria duas observações
legítimas — o que a missão proíbe em letra. O nome tem de dizer o que ele é (§9).

---

## 5 · STORAGE — o endereço perdeu o direito de ser identidade

```
storage_path  =  ENDEREÇO                      ✅ decidido
storage_path  ≠  identidade semântica          ✅ decidido
```

Hoje é o contrário, e a consequência já é visível sem banco nenhum:

```
RAW_PATH declarados no livro          35
existem em disco nesta árvore         10
ausentes                              25   (todos da corrida PILOT_RUN_20260907155832_cf7519)
```

**25 endereços apontam para o vazio.** Se o endereço fosse a identidade, 25 observações
teriam perdido a identidade por uma decisão de o que se versiona em Git. Elas não perderam
— continuam inteiras no livro, com corrida, fonte, documento, hash e hora. **É a prova
prática de que a identidade nunca esteve no caminho.**

O `CASO C` da §0 só passa hoje porque `caminho_do_objeto()` mete `sha256[:16]` dentro do
caminho (`preservar_coleta.py:222`). Bytes diferentes ⇒ caminho diferente ⇒ duas linhas.
**Funciona por o endereço conter o conteúdo, não por a chave estar certa.** Um esquema de
caminho sem o hash — e o coletor italiano tem exactamente um desses,
`STORE/{sourceId}/{documentId}/{versionId}/{nome}` — não teria essa sorte.

---

## 6 · RETRY — as definições, e os quatro casos

```
RETRY            outra TENTATIVA FÍSICA de completar a MESMA observação lógica.
                 Mesma corrida, mesma fonte, mesmo documento, mesmos bytes.
                 Não acrescenta facto sobre o mundo. Acrescenta esforço.

NEW OBSERVATION  um NOVO FACTO SOBRE O MUNDO: a casa foi à fonte de novo,
                 noutra corrida, ou trouxe outros bytes.
                 Acrescenta facto. Nunca se colapsa.
```

A fronteira é **a corrida**, não o relógio. Duas idas dentro da mesma corrida com os
mesmos bytes são a mesma observação; duas corridas são dois factos, mesmo com bytes
idênticos, porque a segunda **prova que o documento não mudou** entre as duas — e essa
prova morre se a linha for colapsada.

| | cenário | **veredito decidido** | contagem | comportamento **hoje** |
|---|---|---|---|---|
| **A** | mesmo `RUN_ID` · fonte · documento · `sha256` · tentativa 30 s depois | **`REUSED`** — 1 observação, 2 tentativas | 1 obs · 1 conteúdo · 2 attempts | ❌ `METADATA_CONFLICT`, corrida `PARTIAL` |
| **B** | **novo** `RUN_ID` · mesma fonte · documento · `sha256` | **`NEW OBSERVATION`** | 2 obs · 1 conteúdo | ❌ no dono do RAW: `METADATA_CONFLICT`. ✅ no coletor: 109 linhas `SEEN_AGAIN` |
| **C** | mesmo `RUN_ID` · fonte · documento · **`sha256` diferente** | **`NEW OBSERVATION`** do mesmo documento, e evento semântico `DOCUMENT_CHANGED_IN_PLACE` | 2 obs · 2 conteúdos · 1 documento | ✅ 2 linhas — mas por acidente (§5) |
| **D** | mesma corrida · fonte · bytes · **sem `DOCUMENT_ID`** | `DOCUMENT_KEY = sha256`, `BASIS = CONTENT_DERIVED` → recai no **caso A** | 1 obs | ✖ nunca exercido: 0 classes medidas sem `DOCUMENT_ID` |

O nome do caso C não é invenção deste documento: o coletor já o escreve
(`italy_pilot_collect.mjs:324`), ao lado de `SEEN_AGAIN`, `NEW_DOCUMENT`,
`BASELINE_DOCUMENT` e `SEMANTIC_ID_CHANGED_SAME_BYTES`.

> **O caso B é onde as duas metades da casa já se contradizem hoje.** O coletor escreveu
> **109 observações `SEEN_AGAIN`** — a resposta certa. O dono canónico da escrita responde
> `METADATA_CONFLICT` e não fecha a corrida. Não é uma diferença de estilo: uma das duas
> metades apaga história.

---

## 7 · O EXEMPLO OBRIGATÓRIO

```
RUN A · fonte X · documento Y · hash H
        tentativa 1  →  timeout no transporte
        tentativa 2  →  200 OK, bytes com hash H, 30 s depois

RUN B · fonte X · documento Y · hash H   (no dia seguinte)
```

| | quantos | porquê |
|---|---|---|
| **contents** | **1** | um único `sha256 = H`. Duas idas não fabricam bytes novos. |
| **observations** | **2** | uma em `RUN A`, uma em `RUN B`. Duas idas à fonte são dois factos, e a segunda prova que Y não mudou de um dia para o outro. |
| **attempts** | **3** | 2 em `RUN A` (a que falhou e a que trouxe), 1 em `RUN B`. Telemetria — nunca linha de observação. |
| **storage objects** | **1** | os mesmos bytes num endereço. As 2 observações apontam para ele. Movê-lo não muda nenhuma das duas. |

E os campos, um por um:

```
observação 1 :  RAW_OBSERVATION_ID = <surrogate 1>       (atribuído na tentativa 2 de RUN A)
                IDEMPOTENCY_KEY    = (RUN_A, X, Y, H)
                CAPTURED_AT        = hora em que a tentativa 2 trouxe os bytes — CONGELADA
                ATTEMPTS           = 2
                LAST_ATTEMPT_AT    = hora da tentativa 2

observação 2 :  RAW_OBSERVATION_ID = <surrogate 2>       ≠ surrogate 1
                IDEMPOTENCY_KEY    = (RUN_B, X, Y, H)    ≠ chave da observação 1
                CAPTURED_AT        = hora da ida de RUN B
                ATTEMPTS           = 1
```

Se a tentativa 2 de `RUN A` fosse repetida mais uma vez, por qualquer motivo:
`IDEMPOTENCY_KEY` idêntica → `REUSED` → `ATTEMPTS` passa a 3, `LAST_ATTEMPT_AT` avança,
`RAW_OBSERVATION_ID` **não muda**, `CAPTURED_AT` **não muda**, e nenhuma linha nova nasce.

---

## 8 · OS CINCO INVARIANTES

| invariante | decidido | estado **hoje** |
|---|---|---|
| `CONTENT_HASH_IS_NOT_OBSERVATION_ID` | **YES** | ⚠️ violado no vocabulário: `ARTIFACT_ID = RAW-<sha16>` |
| `STORAGE_LOCATOR_IS_NOT_IDENTITY` | **YES** | ❌ violado: `storage_path UNIQUE` é a única trava natural |
| `RETRY_DOES_NOT_CREATE_FALSE_OBSERVATION` | **YES** | ⚠️ não cria observação falsa — cria **conflito falso** e trava a corrida |
| `NEW_RUN_CAN_CREATE_NEW_OBSERVATION_OF_SAME_CONTENT` | **YES** | ❌ bloqueado no dono do RAW · ✅ funciona no coletor (109 casos) |
| `MOVING_BYTES_DOES_NOT_CHANGE_OBSERVATION_IDENTITY` | **YES** | ❌ violado; e 25 de 35 endereços já não resolvem |

Os cinco ficam **fechados como contrato**. Nenhum fica fechado como implementação — e
isso está dito aqui em vez de ficar por dizer.

---

## 9 · `SCHEMA_IMPACT` — consequências futuras, **sem SQL**

Registo do que a decisão obriga. **Nada disto é para executar nesta missão.**

**`raw_asset` — colunas**
- adicionar `source_id`, com chave estrangeira para o cadastro de fontes. Hoje `SOURCE_ID`
  só existe dentro da string de `storage_path` e do prefixo de `DOCUMENT_ID`.
- adicionar `document_key` **não anulável** e `document_key_basis` (`SOURCE_DOCUMENT_ID` ou
  `CONTENT_DERIVED`). Nunca `UNKNOWN` dentro de chave.
- adicionar `attempts` (inteiro) e `last_attempt_at`. Telemetria, fora de qualquer chave.
- `captured_at` **não muda de tipo**; muda de significado e de comentário: instante da
  primeira busca bem-sucedida, escrito uma vez, imutável por retry.
- `id` continua a ser o `RAW_OBSERVATION_ID`. **Não há coluna de identidade nova.**

**`raw_asset` — travas**
- criar trava única sobre `(run_id, source_id, document_key, sha256)` — a chave de
  idempotência. É ela que colapsa o retry.
- **rebaixar `storage_path` de `unique` para índice simples.** É a única mudança **não
  aditiva** de todo o plano, e só pode acontecer **depois** de a trava composta existir e
  estar povoada — caso contrário a tabela fica um intervalo sem trava natural nenhuma.
- `sha256` continua **sem** `unique`. Fica registado como coisa a defender numa revisão,
  não como coisa a fazer.

**Contratos e código (fora do banco)**
- `guarda/preservar_coleta.py:81` — `captured_at` sai de `IDENTIDADE_DO_OBJETO`; a busca
  prévia deixa de ser por `storage_path` e passa a ser pela chave de idempotência. É o que
  resolve, de uma vez, o caso A **e** o caso B da §6.
- `leis/artefato.py:120-144` — `RAW-<sha16>` precisa de dizer que é identidade de
  **conteúdo**. Enquanto se chamar `ARTIFACT_ID`, o invariante 1 fica violado no nome.
- `coleta/italy_pilot_collect.mjs:369-381` — passar a registar `retries` também no caminho
  de sucesso. Sem isso, `RETRY_CASES_PROVABLE` continua `NÃO SEI` para sempre.
- `guarda/portas_live.py:140-142` (`COLS_OBJ` / `COLS_RAW`) — acompanham as colunas novas.
- Bíblia — a COL-LAW-034 ganha um parágrafo sobre a observação RAW, ou nasce lei própria.
  **Decisão de quem fizer a emenda; esta missão não toca na Bíblia.**

**Migração de dado existente**
- as 144 observações do livro têm `RUN_ID`, `SOURCE_ID`, `DOCUMENT_ID` e `RAW_SHA256`
  completos, e produzem **144 chaves distintas** — nenhuma colide. Nenhuma linha existente
  precisa de ser inventada ou descartada para caber no esquema decidido.

---

## 10 · `UNRESOLVED_IDENTITY_QUESTIONS`

`UNRESOLVED_CRITICAL_IDENTITY_QUESTIONS = 0`

Ficam abertas, e **nenhuma delas bloqueia** a identidade RAW:

1. **`RETRY_CASES_PROVABLE` continua `NÃO SEI`** até o coletor registar tentativas no
   sucesso. Não bloqueia: a decisão de §3 não depende de contar retries passados; ela
   existe para que o próximo tenha para onde ir.
2. **Quantas linhas há em `raw_asset` ao vivo — `NÃO SEI`**, sem credencial nesta sessão.
   Não bloqueia: o esquema versionado é suficiente para decidir contrato.
3. **A ordem exacta da queda do `unique` de `storage_path`** é decisão da migração, não da
   identidade.
4. **Que entidade guarda o cadastro de fontes** a que `source_id` vai apontar — pergunta da
   COL-LAW-053, já aberta antes desta missão.
5. **`SAME_CAPTURE_MULTIPLE_STORAGE_COPIES` continua com 0 casos medidos.** Enquanto for 0,
   não se constrói tabela para ele — REGRA ZERO, como em `IDENTIDADE-DO-ARTEFATO.md` §E.

---

## 11 · EM PALAVRAS FÁCEIS

**1. O que é uma observação RAW?**
Uma ida à fonte, numa corrida, por um documento, que trouxe bytes. É um facto sobre o
mundo: *«nesta corrida, nesta fonte, este documento estava assim.»*

**2. O que identifica os bytes?**
O `sha256`. Só ele, e só os bytes.

**3. O mesmo PDF, outra vez, na mesma corrida, por retry — quantas observações?**
**Uma.** O retry gastou esforço, não trouxe facto novo. Passa a contar como mais uma
tentativa da mesma observação.

**4. O mesmo PDF, amanhã, noutra corrida — quantas observações?**
**Duas.** Um conteúdo, duas observações. A segunda é quem prova que o documento não mudou
de um dia para o outro. Apagá-la seria apagar essa prova.

**5. `CAPTURED_AT` é identidade ou só diz quando?**
**Só diz quando.** Sai de todas as chaves. Congela no instante em que os bytes chegaram
pela primeira vez, e não se reescreve.

**6. Mudar o ficheiro de pasta muda a identidade?**
**Não.** O caminho é endereço. Hoje ainda é a trava do banco, e é isso que tem de cair.

**7. Qual a consequência para o banco?**
`raw_asset` ganha `source_id`, `document_key` + o seu `basis`, e as duas colunas de
tentativa; ganha uma trava única sobre `(run_id, source_id, document_key, sha256)`; e
`storage_path` deixa de ser único, virando índice. O `id` que já lá está continua a ser o
nome da observação — **nenhuma coluna de identidade nova**.

**8. Há decisão crítica ainda aberta?**
**Não.** Há cinco perguntas abertas, listadas em §10, e nenhuma delas impede a
implementação de começar.

---

## 12 · VEREDITO

```
RAW_OBSERVATION_ID    = CLOSED
IDEMPOTENCY_KEY       = CLOSED
CAPTURED_AT_ROLE      = CLOSED
RETRY_SEMANTICS       = CLOSED
CONTENT_IDENTITY      = CLOSED
STORAGE_IDENTITY      = CLOSED

UNRESOLVED_CRITICAL_IDENTITY_QUESTIONS = 0

C-PLAN-0 = PASS
```

```
SOURCE_FILES_CHANGED   = 0
RUNTIME_FILES_CHANGED  = 0
MIGRATIONS_CHANGED     = 0
SYSTEM_MAP_CHANGED     = 0
BIBLE_CHANGED          = 0
PRODUCTION_MUTATIONS   = 0
```

### Nota honesta sobre o validador do System Map

`SYSTEM_MAP_CHECK = FAIL`, com **uma** prova reprovada: `P1_SEM_DRIFT`. A diferença foi
medida e é inteira:

```
.NODES[153].facts[0]
  commitado = branch claude/collection-plumbing-canoni
  regerado  = branch claude/raw-observation-identity-3
```

Regerar o mapa nesta árvore muda **só** o nome do ramo, o `HEAD` e o carimbo de geração.
Filtradas essas três coisas, o diff é **vazio** — `architecture.generated.json`,
`casco.generated.json` e `sources.generated.json` não mudam uma linha, e acrescentar este
documento também não muda nenhuma delas.

Ou seja: **ninguém mexeu na arquitetura.** Comitar o mapa regerado aqui gravaria o nome de
um ramo de decisão dentro da projeção canónica, e violaria `SYSTEM_MAP_CHANGED = 0` desta
missão sem corrigir drift nenhum. O mapa fica como está; a regeneração pertence a quem
integrar isto no ramo canónico.

---

> **HARD STOP.** A identidade RAW está fechada. Nada de Phase A, orquestração, migração de
> esquema, Admission ou READY — mesmo que pareça óbvio.
