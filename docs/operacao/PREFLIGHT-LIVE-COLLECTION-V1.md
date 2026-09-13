# PRÉ-VOO DO LIVE — COLLECTION V1

> **Esta missão NÃO aplicou nada em produção.** Ela mede, ensaia o caminho
> exacto num banco descartável, e entrega o plano. A aplicação precisa de
> autorização explícita, e essa autorização não existe aqui.
>
> **Missão:** `C-COLLECTION-OPERATIONAL-READINESS-OVERNIGHT-V1`
> **Medido em:** 2026-09-13

---

## 1 · O LIVE NÃO FOI ALCANÇADO, E ISSO TEM UM MOTIVO EXACTO

```
LIVE_DB_REACHABLE = NO
```

Não é «a rede falhou» nem «não sei». **Este ambiente não tem as credenciais.**
Medido, variável a variável:

| variável | estado |
|---|---|
| `SUPABASE_DB_URL` | ausente |
| `SUPABASE_URL` | ausente |
| `SUPABASE_SERVICE_ROLE_KEY` | ausente |
| `SUPABASE_ANON_KEY` | ausente |

Daí decorre, e **nenhum destes se adivinha**:

```
LIVE_SCHEMA_VERSION     UNKNOWN
LIVE_MIGRATIONS_PRESENT UNKNOWN
LIVE_MIGRATIONS_MISSING UNKNOWN
MIGRATION_029_LIVE      UNKNOWN
MIGRATION_030_LIVE      UNKNOWN
```

> **`UNKNOWN` COM MOTIVO NÃO É O MESMO QUE ZERO.**
> Zero manda aplicar tudo; não-medido manda ir ver primeiro.

---

## 2 · O QUE ESTÁ EM GIT, E QUE NÃO É O QUE ESTÁ EM LIVE

```
MIGRATIONS_EM_GIT = 30   (001..030)
APLICADAS NO ENSAIO = 29 (todas menos a 008, que confere e não cria)
```

> **MIGRATION EM GIT NÃO É MIGRATION APLICADA.**

---

## 3 · O CAMINHO DE APLICAÇÃO JÁ EXISTE, E FOI ENSAIADO

O aplicador canónico é `motor/cadeia_canonica.sh`, e **não** se escreveu um
segundo. Ele já tem as três travas que este pré-voo exigiria:

| trava | o que faz |
|---|---|
| livro-razão `public.schema_migracao` | regista versão, resultado e `sha256` de cada migration aplicada |
| detecção de desvio | versão no livro com `sha` diferente do ficheiro → **falha fechada antes de qualquer DDL** |
| `--single-transaction` | uma migration entra inteira ou não entra; o registo no livro viaja na **mesma** transacção |

**Ensaiado esta noite, num PostgreSQL 16 descartável virgem:**

```
primeira passagem   MIGRATION_001..030 = PASS   (29 aplicadas)
segunda passagem    MIGRATION_001..030 = SKIP (já no livro-razão) HASH=MATCH
verificação 008     migrations 001-018 conferidas: 30 tabelas, travas,
                    funções e RLS no lugar
livro-razão         29 linhas · de 001 a 030
```

A segunda passagem é o que importa: **aplicar duas vezes não faz nada na
segunda.**

---

## 4 · O PLANO DE APLICAÇÃO

```
LIVE_READY_FOR_APPLY = NO
```

`NO` por **falta de autorização e de credenciais** — não por falta de caminho.
O caminho está provado. Quando existirem as duas coisas:

### Passo 0 · antes de tocar seja no que for

```bash
# só leitura: o que o livro-razão do LIVE diz que já lá está
psql "$SUPABASE_DB_URL" -tAc \
  "select versao, resultado, left(sha256,12) from public.schema_migracao
   order by versao"
```

Se a tabela **não existir**, o LIVE nunca passou por este aplicador, e isso
muda o risco: as migrations antigas seriam tentadas outra vez. Neste caso
**parar** e decidir com gente — `add column if not exists` passa em silêncio, e
a `015`/`018` têm um caso conhecido de coluna aposentada que ressuscitaria.

### Passo 1 · retrato antes

```bash
psql "$SUPABASE_DB_URL" -tAc \
  "select relname, n_live_tup from pg_stat_user_tables
   where relname in ('raw_asset','storage_object','derived_artifact',
                     'documento_estruturado','participacao_na_derivacao',
                     'collection_run','etapa_da_corrida')
   order by relname"
```

### Passo 2 · aplicar, pelo aplicador canónico e por mais nenhum

```bash
bash motor/cadeia_canonica.sh migrations "$SUPABASE_DB_URL"
```

### Passo 3 · conferência

```bash
psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -q \
  -f supabase/migrations/008_verificacao_pos_aplicacao.sql
```

### Passo 4 · teste pós-aplicação, e é este exactamente

```sql
-- as duas casas novas existem e estão vazias numa aplicação limpa
select 'participacao_na_derivacao' as tabela, count(*) from public.participacao_na_derivacao
union all
select 'documento_estruturado', count(*) from public.documento_estruturado;

-- e as travas de identidade estão lá
select conname from pg_constraint
 where conrelid = 'public.documento_estruturado'::regclass
 order by conname;
```

Esperado: `document_id_nao_e_o_hash`, `documento_declara_a_fonte`,
`hash_texto_tem_formato`.

---

## 5 · O RISCO, MEDIDO E NÃO SUPOSTO

| pergunta | resposta medida |
|---|---|
| risco de `NOT NULL` sobre dados existentes? | **não** — a `029` e a `030` só fazem `create table if not exists`; nenhuma altera tabela existente |
| risco de FK? | as FK novas apontam para `raw_asset`, `derived_artifact` e `collection_run` com `on delete restrict`. Em tabelas **vazias** não há linha para violar |
| conflito com dados existentes? | nenhum: as duas tabelas não existiam |
| tempo esperado | segundos — DDL sobre tabelas vazias |
| locks relevantes | `create table` toma lock só sobre o objecto que cria |
| rollback | cada migration corre em transacção própria: se falhar, nada dela fica. Para desfazer depois de aplicada: `drop table` das duas, que só é seguro enquanto estiverem vazias |
| backup | **NÃO MEDIDO** — a capacidade de backup/restore do LIVE não foi verificada, porque não há acesso |

⚠️ **`backup` ficou `NOT_MEASURED` de propósito.** Escrever «há backup» sem ter
visto seria a única linha perigosa deste documento.

---

## 6 · O QUE NÃO SE FAZ

- **Não se usa o LIVE para descobrir se a migration funciona.** Ela já está
  provada em descartável, e o ensaio está acima.
- **Não se aplica sem autorização explícita para esta mudança.**
- **Não se aplica migration à mão**, fora de `motor/cadeia_canonica.sh` — o
  livro-razão ficaria a mentir sobre o que correu.
