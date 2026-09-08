# P-011 / G-02 — O DADO OPERACIONAL ITALIANO ESTÁ NO GIT

**Censo READ-ONLY** · 2026-09-08 · ramo `claude/italia-biblia-integracao-v1`

> **Nada foi movido, escrito, migrado ou apagado.** Zero `INSERT`, zero `UPDATE`, zero
> upload, zero migration aplicada. Este documento é medição e plano — não execução.
>
> **`LIVE_STATE = UNKNOWN`:** não há credencial de leitura nesta sessão. Tudo o que se diz
> do Supabase vem do **schema versionado**, não do banco real.

---

## A · O QUE ESTÁ NO GIT HOJE

| o quê | ficheiros | tamanho | commits que o tocaram | Git é o sítio certo? |
|---|---:|---:|---:|---|
| `data/collection-store` — **bytes** (PDF, HTML) | 11 | **11,97 MB** | 1 | ❌ **não** |
| `data/derivados` — textos + registo de artefatos | 44 | 0,93 MB | 1 | 🟡 parcial |
| `data/collection-ledger` — recibo + observações IT | 2 | 0,48 MB | 1 | ❌ não |
| `data/samples/LIVRO-DE-DECISOES.json` | 1 | 0,39 MB | **5** | ❌ não |
| `data/samples/RUN-MANIFEST.json` | 1 | 0,02 MB | **7** | ❌ não |

**O `commits que o tocaram` é a medida que importa.** Os três primeiros ainda têm 1 porque
o piloto não entrou em cadência. O manifesto e o livro já vão em 7 e 5 — **e crescem a cada
corrida**. É a curva que dói, não o tamanho de hoje.

> **O Git não esquece.** Um ficheiro apagado continua a pesar em cada clone, para sempre.
> 12 MB hoje, com a ARPAV a publicar 2×/semana a ~12,8 MB por corrida, é o começo de uma
> conta que só sobe.

**O que PODE ficar no Git** (COL-LAW-303): o schema, os contratos, o SQL de importação, as
amostras versionadas de rota não replicável (D-003 + REGRA §14), e a **evidência histórica
já commitada** — que não se apaga.

---

## B · O QUE JÁ EXISTE NO SUPABASE PARA OS RECEBER

Medido no schema versionado (`supabase/migrations/001`), **não no banco vivo**.

### `collection_run` — 22 campos

Já tem `run_id` · `platform` · `actor` · `actor_version` · `input` · `query` · `mission` ·
`source_country` · `started_at` · `finished_at` · `dataset_id` · `item_count_raw` ·
`item_count_normalized` · `cost_usd` · **`cost_method`** · `source_version` · `status` ·
`error` · `capture_method` · `rule_version`.

> **A convergência mais forte deste censo:** a coluna `cost_method` já existe, com a
> constraint `custo_declarado_diz_como_foi_medido`, e o comentário no schema diz o mesmo que
> a corrida passou a dizer esta noite — *«COMO o custo foi obtido faz parte do custo»*. O
> `COST_BASIS` que a estrada agora escreve **cabe nela sem inventar coluna**.

### `raw_asset` — 13 campos

`run_id` · `storage_path` · `media_type` · `bytes` · `sha256` · `captured_at` ·
`source_url` · `preserved` · `not_preserved_reason`.

### Bucket `raw`

Privado, um para o EAME, país no *path*, identidade no `run_id + sha256 + metadata`, com
round-trip provado (`supabase-raw-roundtrip.yml`: Git → Storage → Postgres → download →
hash).

---

## C · FIELD_MAPPING — a RUN nova × `collection_run`

| campo da corrida (hoje) | `collection_run` | veredito |
|---|---|---|
| `RUN_ID` · `STARTED_AT` · `FINISHED_AT` · `STATUS` | iguais | **MATCH** |
| `EXECUTOR_ID` / `EXECUTOR_VERSION` | `actor` / `actor_version` | **MATCH** (nome diferente) |
| `ROUTE` = `LOCAL_EXECUTOR` | `platform` / `capture_method` | **MATCH parcial** — decidir qual dos dois é o dono de ROUTE |
| `COST_USD` + `COST_BASIS` | `cost_usd` + **`cost_method`** | **MATCH** — mas `ROTA_GRATUITA_PROVADA` **não está no enum** (`PLATAFORMA_USAGE_TOTAL`/`DIFERENCA_DE_SALDO`/`TABELA_DE_PRECO`/`NAO_SEI`) |
| `PIPELINE_VERSION` | `rule_version` | **CONFLICT** — `rule_version` é a versão da régua que normalizou, não do pipeline |
| `RUN_STATE` + `COMPLETION_BASIS` | — | **MISSING** |
| `STATE_BEFORE` / `STATE_AFTER` | — | **MISSING** |
| `GIT_COMMIT` · `GIT_TREE_CLEAN` · `BIBLE_VERSION` | — | **MISSING** |
| `PREFLIGHT` | — | **MISSING** |
| `dataset_id` · `input` · `query` | — | **EXTRA** (da rota paga; `NULL` aqui) |

**Resumo:** 5 MATCH · 1 MATCH parcial · 1 CONFLICT · 5 MISSING · 3 EXTRA.
**Nenhum bloqueio.** As 5 lacunas são colunas novas ou um `jsonb`; o CONFLICT é de nome.

## D · `raw_asset` × `ARTIFACT` / `OCCURRENCE` / `CONTENT`

⚠️ **Não colapsar os três só porque a tabela se chama `raw_asset`.**

| conceito | `raw_asset` cobre? |
|---|---|
| `CONTENT` (os bytes, `sha256`) | ✅ sim |
| `OCCURRENCE` (o caminho, com procedência própria) | 🟡 `storage_path` é **um** caminho — hoje não representa **duas ocorrências do mesmo conteúdo** |
| `ARTIFACT` derivado (`PARENT_SHA256`, `DERIVATION_TYPE`) | ❌ não há coluna de pai |

**Consequência medida:** os 6 pares de ocorrência do mesmo conteúdo (COL-LAW-501) e os 43
derivados com pai **não cabem no `raw_asset` de hoje**. Ou entra uma tabela de ocorrência, ou
`raw_asset` ganha `parent_sha256` + chave por `(sha256, storage_path)`. **Não decidido aqui.**

---

## E · MIGRAÇÃO — PROJETADA, NÃO EXECUTADA

```
1  congelar o contrato da RUN e do ARTIFACT (feito: G-38 nesta noite)
2  migration ADITIVA: colunas em falta + tabela de ocorrência
3  copiar os bytes para o bucket `raw`
4  CONFERIR SHA256 de cada byte copiado, um a um
5  escrever a metadata (run + occurrence + content + derived)
6  reconciliar contagens: 49 ocorrências · 43 conteúdos · 43 derivados · LOST 0
7  virar os leitores para o banco
8  provar: a mesma pergunta dá o mesmo número nos dois sítios
9  parar as escritas operacionais no Git
10 parar de acrescentar dado operacional novo ao Git
11 PRESERVAR a evidência histórica já commitada — sem reescrever nada
```

**O passo 11 não é opcional.** Apagar o histórico exigiria reescrever o Git, e isso está
proibido (COL-LAW-209). O que sai é o **fluxo futuro**, não o passado.

## F · RISCOS

| risco | mitigação |
|---|---|
| perder byte na cópia | passo 4 confere `sha256` um a um; sem conferência não avança |
| duas verdades durante a transição | escrita dupla só se indispensável, e por tempo declarado |
| `raw_asset` colapsar ocorrência e conteúdo | resolver o modelo **antes** de copiar (secção D) |
| `cost_method` sem valor para rota gratuita | acrescentar ao enum, ou `NAO_SEI` — **decisão do dono** |
| `LIVE_STATE = UNKNOWN` | o banco real pode divergir do schema. **Medir antes de migrar** |

## G · BLOQUEADORES

1. **Modelo de ocorrência × conteúdo** não resolvido no schema (secção D).
2. **`LIVE_STATE = UNKNOWN`** — sem leitura do banco real, o plano assume o schema.
3. **Decisão do dono:** `ROTA_GRATUITA_PROVADA` entra no enum de `cost_method`?

## H · PROVA EXIGIDA ANTES DE MIGRAR

`49` ocorrências e `43` conteúdos contados **no destino** · cada `sha256` conferido após a
cópia · `LOST = 0` medido dos dois lados · nenhum leitor a apontar para o Git · o histórico
commitado intacto.

---

**Nenhuma infraestrutura nova é necessária.** GitHub e Supabase, com os papéis que a
COL-LAW-302 e a COL-LAW-304 já lhes deram, bastam.
