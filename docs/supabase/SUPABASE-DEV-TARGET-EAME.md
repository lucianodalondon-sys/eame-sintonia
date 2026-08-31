# RESOLUÇÃO DO ALVO DEV — SINTONIA EAME

**Data:** 2026-08-31 · artefato em `data/supabase/SUPABASE-DEV-TARGET.json`

```
MIGRATION_APPLIED_DEV = NO     REAL_DATA_PUBLISHED = NO     V8_WIRED = NO
```

---

## 0 · A CORREÇÃO, E ELA É MINHA

Na rodada anterior eu declarei `DEV_INSTANCE_AVAILABLE = NO`.

**A medição estava certa; o rótulo estava errado.** O que eu medi foi a ausência de
credencial, CLI, `psql` e Docker **nesta máquina**. O que eu declarei foi a inexistência do
banco. São coisas diferentes, e eu conclui uma a partir da outra.

O projeto existe. Passam a ser três coisas separadas:

| | responde | quem mede |
|---|---|---|
| `SUPABASE_PROJECT_EXISTS` | existe projeto na conta? | Luciano, na conta |
| `CLAUDE_LOCAL_SUPABASE_ACCESS` | consigo abrir conexão daqui? | eu |
| `DEV_INSTANCE_AVAILABLE` | existe banco DEV **utilizável**? | o inventário |

**O terceiro não é nenhum dos dois.** Um projeto pode existir, estar saudável, e ainda assim
não ser utilizável como DEV — porque tem dado que alguém precisa.

---

## 1 · O PROJETO

```
NAME ......... eame-sintonia
PROJECT_REF .. odhdwvugikjdvkapbowe
REGION ....... eu-west-1
STATUS ....... ACTIVE_HEALTHY
```

Informado e medido pelo Luciano. **Não verificado por mim** — e o artefato registra isso,
para ninguém confundir depois. Não há credencial nesta máquina, e credencial não é coisa
que eu deva manusear.

---

## 2 · O QUE EU NÃO FIZ, E POR QUÊ

**Não inventariei o projeto.** Não tenho acesso.

E não vou pedir a chave: quem tem acesso roda a consulta. Meu trabalho é entregar a
consulta certa e o julgamento que ela alimenta.

Também **não criei projeto novo** — não foi pedido, e criar um segundo `eame-sintonia`
seria a maneira mais rápida de alguém aplicar migration no lugar errado depois.

---

## 3 · O INVENTÁRIO: UM SQL, SÓ DE LEITURA

`supabase/inventory/0000_readonly_inventory.sql` — gerado, não escrito à mão.

Cola no editor SQL do projeto e devolve **um JSON** com tudo:

```
DATABASE_VERSION · EXISTING_SCHEMAS · EXISTING_TABLES · EXISTING_VIEWS
EXISTING_FUNCTIONS · EXISTING_RLS_POLICIES · EXISTING_USER_DATA
EXISTING_MIGRATION_HISTORY · AUTH_USERS · STORAGE_OBJECTS
```

**Nenhum `CREATE`, `ALTER`, `INSERT`, `UPDATE`, `DROP`, `GRANT`.** Só `SELECT` — e há prova
que varre o arquivo procurando qualquer um desses verbos.

As três últimas consultas usam `to_regclass` porque a tabela pode não existir. **A ausência
dela também é resposta**, e uma consulta que estourasse ali derrubaria o inventário inteiro.

### Duas perguntas que ninguém pediu e que decidem o veredito

```
AUTH_USERS ........ usuário cadastrado é dado de gente
STORAGE_OBJECTS ... arquivo guardado é dado de alguém
```

Um projeto com usuário **não é descartável**, mesmo com todas as tabelas vazias.

---

## 4 · O CLASSIFICADOR

Transforma um inventário em veredito. Está escrito, testado, e roda hoje.

**Bloqueia** (`SAFE_TO_USE_AS_DEV = NO`):

```
usuário em auth.users · objeto em storage · qualquer tabela com linha
```

**Pede decisão** (`NEEDS_DECISION`):

```
schema fora do sistema e fora do sintonia
schema sintonia já existente com tabela — a migration não pode assumir banco limpo
migration já aplicada neste projeto
```

**A regra que mais importa:**

> Nunca devolver `YES` por ausência de informação. *"Não sei o que tem dentro"* é o
> contrário de *"está vazio"*.

E o meu próprio teste pegou uma falha nessa regra: um inventário **incompleto** — um
dicionário sem as chaves obrigatórias — estava passando por limpo e devolvendo `YES`.
Consertei com uma guarda explícita: **chave ausente não é chave vazia.**

**E nome igual não é prova.** O projeto se chamar `eame-sintonia` não prova que é o ambiente
certo nem que está vazio. Só o inventário prova.

---

## 5 · O PORTÃO ANTES DE APLICAR

Recusa por padrão. Quatro condições, todas obrigatórias — e nenhuma delas é *"o nome
bate"*:

```
PODE_APLICAR = false
RECUSAS:
  SAFE_TO_USE_AS_DEV = NEEDS_DECISION
  inventário não executado
  sem acesso local: quem aplica é quem tem credencial
```

Há prova de que **mesmo com um inventário limpo** o portão continua recusando enquanto não
houver acesso. Inventário limpo não basta: quem aplica é quem tem a credencial, e não sou eu.

---

## 6 · SAÍDA

```
SUPABASE_PROJECT_EXISTS = YES  (informado e medido pelo Luciano; não verificado por mim)
PROJECT_REF    = odhdwvugikjdvkapbowe
PROJECT_REGION = eu-west-1
PROJECT_STATUS = ACTIVE_HEALTHY

CLAUDE_LOCAL_SUPABASE_ACCESS = NO
  sem SUPABASE_ACCESS_TOKEN, sem chave, sem URL
  sem supabase CLI, sem psql, sem pg_dump, sem docker

EXISTING_TABLES       = NOT_MEASURED
EXISTING_VIEWS        = NOT_MEASURED
EXISTING_FUNCTIONS    = NOT_MEASURED
EXISTING_RLS_POLICIES = NOT_MEASURED
EXISTING_USER_DATA    = NOT_MEASURED

SAFE_TO_USE_AS_DEV     = NEEDS_DECISION
DEV_INSTANCE_AVAILABLE = NOT_MEASURED

MIGRATION_APPLIED_DEV = NO
REAL_DATA_PUBLISHED   = NO

READY_TO_APPLY_MIGRATION_DEV = NO
READY_FOR_FIRST_SHADOW_LOAD  = NO
```

### Preservado da rodada anterior

```
H2_FIXED_COMMIT = YES
H2_COMMIT_SHA   = d7b289425c5e436f3ce68e367b8706e11910f43b
MIGRATION_REVIEW = PASS      VIEWS_IMPLEMENTED = 13     RPCS_IMPLEMENTED = 4
PUBLISHER_DRY_RUN = PASS     PUBLISHER_IDEMPOTENCY_TEST = PASS
SHADOW_VALIDATOR_READY = YES
FIRST_SHADOW_LOAD_EXECUTED = NO    V8_WIRED = NO    PRODUCTION_DEPLOY = NO
```

### `EXACT_BLOCKERS`

```
1  inventário não executado
   um passo, e não é meu: colar supabase/inventory/0000_readonly_inventory.sql no
   editor SQL do projeto odhdwvugikjdvkapbowe e devolver o JSON. O classificador
   já está escrito e decide na hora.

2  quem aplica a migration é quem tem a credencial
   o portão recusa mesmo com inventário limpo enquanto CLAUDE_LOCAL_SUPABASE_ACCESS
   for NO. A chave vai para um servidor, nunca para o navegador — e não para mim.

3  H3 sem artefato resolvido · manifesto de rótulos de H2 com três versões
   herdados da rodada anterior; não bloqueiam a migration, bloqueiam duas entradas
   da primeira carga
```
