# PREPARAÇÃO PARA A PRIMEIRA CARGA SOMBRA — SINTONIA EAME

**Data:** 2026-08-31

```
MIGRATION_APPLIED = NO     REAL_DATA_PUBLISHED = NO     V8_WIRED = NO
FIRST_SHADOW_LOAD_EXECUTED = NO     PRODUCTION_DEPLOY = NO
```

---

## 0 · O FATO QUE DECIDE A RODADA

**Não existe instância Supabase.** Verifiquei, sem inventar:

```
SUPABASE_URL · SUPABASE_ANON_KEY · SUPABASE_SERVICE_ROLE_KEY
SUPABASE_DB_URL · DATABASE_URL ............................. todas ausentes
supabase CLI · psql · pg_isready · docker .................. todos ausentes
supabase/config.toml · .env · .env.local ................... nenhum existe
```

`DEV_INSTANCE_AVAILABLE = NO`.

**O que isso muda, e precisa ficar dito:**

- A migration **não foi aplicada** em lugar nenhum.
- As provas `DB_CONSTRAINT_*` verificam que a restrição **está escrita no SQL**. Isso não é
  o mesmo que o banco ter recusado a linha. Verificar texto prova que a lei foi escrita; só
  a execução prova que ela pega.
- Isolamento por país, multilíngue e proveniência foram exercitados sobre **fixture**.
  Provam a lógica, não um banco.

> Chamar qualquer uma dessas de *"testada no banco"* seria mentira, e este produto inteiro
> existe para não fazer isso.

---

## 1 · H2 DEIXOU DE APONTAR PARA BRANCH

Era a única entrada fora da lei de leitura.

```
REPOSITORY ............ lucianodalondon-sys/eame-sintonia
BRANCH_AT_REFERENCE ... origin/claude/sintonia-italy-pilot-b1l401
PATH .................. data/samples/IT-T4-001/IT-T4-001-adama-expiries.json
RESOLVED_COMMIT_SHA ... d7b289425c5e436f3ce68e367b8706e11910f43b
CONTENT_SHA256 ........ ee9d835d2a82470eeb8c84fbc9443d7b7f199311535ebeba4dac601565a6495c
BLOB_SHA .............. 26a645477326d4f0c4bd825487fbe59fdde7049f
```

**Não escolhi o HEAD por conveniência.** Perguntei ao Git quantas versões do artefato
existem na branch: **uma**. Foi criado num commit e nunca mais tocado, e o conteúdo no HEAD
é idêntico ao daquele commit. Não houve escolha a fazer — e se houvesse, o script devolveria
`FAIL_CLOSED` em vez de pegar o mais novo.

**Os outros oito commits estavam abreviados.** Expandi todos para 40 caracteres e verifiquei
que cada um resolve. Um SHA de 7 caracteres é imutável, mas fica ambíguo quando o
repositório cresce.

### Um sub-input que NÃO foi fixado

`IT-T4-001-etichette-manifest.json` tem **três versões** na branch, com `RUN_ID` e tamanhos
diferentes (6,9 KB · 170 KB · 171 KB). São estados diferentes de uma coleta, não reescritas
do mesmo estado. **Escolher uma é decisão de quem sabe qual run é canônica.**

Ele entrou pelo plano de primeira carga que **eu** escrevi, não pelo mapa de mangueiras —
por isso não bloqueia a proveniência de H2. Fica `NOT_PINNED`, com os três candidatos
listados, e a contagem de rótulos vira `NOT_MEASURED`.

---

## 2 · MIGRATION REVISADA — E TRÊS COISAS FALTAVAM

`MIGRATION_REVIEW = PASS`, **depois** de corrigir. A primeira passagem reprovou:

**1 · 86 chaves estrangeiras sem índice.** O Postgres indexa PK e UNIQUE, e **não** a coluna
que aponta para fora. Sem esses índices, todo join do produto varre a tabela inteira — e o
produto é feito de joins. Declarei os 86 no JSON e o gerador os emite.

**2 · 112 chaves estrangeiras sem `ON DELETE` declarado.** O padrão `NO ACTION` não está
errado; está **calado**, e comportamento calado vira surpresa no primeiro `DELETE`.
Declarei uma política em quatro regras, com a primeira vencendo as outras:

```
1  FK para evidence · source · source_snapshot · publish_run · observation ·
   ontology_term · content_entity  →  RESTRICT
   história não se apaga por baixo de quem a cita
2  FK que faz parte da PK  →  CASCADE     a filha não existe sem a raiz
3  FK NOT NULL fora da PK  →  RESTRICT    a linha depende dela
4  FK que aceita nulo      →  SET NULL    o vínculo some, a linha fica
```

Resultado: **78 RESTRICT · 18 CASCADE · 16 SET NULL**.

**3 · Um falso positivo meu.** O revisor acusou `SERVICE_ROLE_KEY` no SQL — e a ocorrência
está num **comentário que proíbe** o segredo. Confundir a proibição com a coisa proibida é
o mesmo erro de substring de sempre. O verificador passou a procurar **valor** (atribuição
ou string tipo JWT), e ganhou uma prova nova: a proibição tem de continuar escrita.

### Contagens conferidas contra o JSON

```
TABELAS 57 · VIEWS 13 · RPCs 5 (4 + helper) · ENUMS 27
FKs 112 · CHECKS 31 · UNIQUEs 8 · ÍNDICES 86
RLS habilitado em 57 · política de publisher em 57
```

---

## 3 · AS 13 VIEWS E AS 4 RPCs, COM CORPO

Antes eram assinaturas. Agora têm SQL, escrito **dentro do JSON canônico** — editar o `.sql`
criaria uma segunda verdade que a próxima geração apaga sem avisar.

**Regra que atravessa as treze:** onde pode faltar linha, o join é `LEFT`. Nenhuma view
esconde `NOT_PROVED` ou `UNKNOWN` sumindo com a linha.

O que as views **derivam** em vez de guardar:

- `v_convergence_state` — conta famílias distintas entre pernas `INDEPENDENT`. Não existe
  coluna de contador em lugar nenhum.
- `v_action_map` — `is_defensible` sai de **contar linhas** em `action_evidence`, não de um
  campo.
- `v_crop_map_point` — `is_drawable` só com `GEO_RESOLUTION = POINT` **e** geometria.
- `v_issue_expert` — já filtra pelo portão, e **não ordena por nada**.
- `v_object_timeline` — a seta `→` é montada **aqui**; no banco os dois estados são colunas.

As RPCs são `SECURITY INVOKER` **de propósito**: uma RPC `SECURITY DEFINER` contornaria a
política de país.

`resolve_representation` é o único lugar onde mora a política de fallback — uma
implementação, não uma por view. Cadeia `<pedido> → en → pt`, e quando nenhuma existe devolve
`NO_REPRESENTATION_AVAILABLE` com texto nulo. **Nunca dizer FR tendo servido EN.**

E `get_evidence` deixa o original **fora da cadeia**: `ORIGINAL_TEXT` vai na língua da fonte,
sempre.

---

## 4 · RLS: O QUE DÁ PARA FAZER AGORA E O QUE DEPENDE DE DECISÃO

**Feito agora:**

```
RLS habilitado nas 57 tabelas — sem política, acesso negado
publisher_all       em 57 tabelas   o único que escreve inteligência canônica
portal_read_country nas tabelas com country
portal_read_child   nas filhas, herdando o país da raiz
portal_write_telemetry  em entry_path_event — a ÚNICA escrita do portal
```

O helper `allowed_countries()` **nega por padrão**: sem configuração de sessão devolve array
vazio e nenhuma linha passa. Uma política que lesse um claim de JWT com formato ainda não
decidido seria invenção; esta é exercitável hoje e troca de implementação sem mexer nas
políticas.

**`RLS_REQUIRES_AUTH_DECISION`:**

```
1  como o país do usuário chega até o banco (claim? tabela de membership?)
2  multi-tenant — tenant_id não entra antes de existir cliente múltiplo
3  auditoria de acesso — quem leu o quê
```

---

## 5 · PUBLISHER EM DRY RUN — E O QUE ELE PEGOU

Rodou sobre os commits fixos, sem gravar nada, sem conexão.

```
ENTRADAS ................. 9
COM PLANO ................ 8
NÃO RESOLVIDA ............ 1  (H3)
CHAVES DE UPSERT ......... 3.984
SEGUNDA PASSAGEM ......... 3.984  ·  novas entidades: 0  ·  duplicadas: 0
```

**Idempotência provada por cálculo:** a chave deriva de `(commit, caminho, lista, índice)` —
tudo imutável. Título traduzido nunca entra: ele muda por idioma e por revisão.

### Quatro números meus que o dry run derrubou

O verificador comparou o que o plano **declarava** com o que os blobs congelados **contêm**:

| # | eu tinha escrito | o blob mede | virou |
|---|---|---|---|
| **H8** | 22 contas | `CONTAS-V1.json` tem **44** em `ACCOUNTS` e 28 em `NO_LINK_DECLARED` | `NOT_MEASURED` |
| **H6** | 164 creators em 90 dias | 14 · 10 · 442 nas três listas | `NOT_MEASURED` |
| **H5** | 148.964 leituras · 23 safras | os três artefatos são resumos e **não contêm essas listas** | `LEDGER_DERIVED` |
| **H3** | 36 tuplas | nenhum artefato do commit tem 36 de nada (242 pares, 6 na amostra) | `NOT_RESOLVED` |

**Nem 44 nem 44−28=16 dão 22.** O número não tem sustentação naquele artefato.

O caso de H5 é diferente e vale distinguir: **23 safras e 148.964 leituras continuam certos**
— o dono é `scripts/metricas_canonicas.py`, que conta o pacote RAIF inteiro. O que não se
pode dizer é que saem *destes três blobs*. Medi e não achei.

E H3 ficou `NOT_RESOLVED` com os quatro candidatos listados: escolher por semelhança de nome
seria inventar proveniência.

---

## 6 · VALIDADOR DE SOMBRA — IMPLEMENTADO E EXERCITADO

Compara **catorze dimensões**, não contagem:

```
row_count · entity_count · ids · types · countries · states · dates
evidence_ids · source_ids · relations · dependency_types · actions
translations · provenance
```

O exercício que importa: um banco com **contagem idêntica** ao freeze, mas com
`AO-IT-001` promovido de `ATTENTION_CANDIDATE_TEST` para `ATTENTION_READY`.

```
CONTAGEM_ERA_IGUAL = true      PUBLISH = FAIL_CLOSED      dimensão que pegou: states
```

Um validador que só contasse deixaria passar, e o objeto apareceria na fila de atenção como
se tivesse atravessado os cinco portões.

**Limite:** a fixture prova que o comparador pega a mudança de semântica. **Não prova nada
sobre um banco real.**

---

## 7 · SAÍDA

```
BRANCH = claude/eame-final-product-arbitration
MERGED = NO

CASCO_RECEPTOR_READY = YES

H2_FIXED_COMMIT = YES
H2_COMMIT_SHA   = d7b289425c5e436f3ce68e367b8706e11910f43b

MIGRATION_REVIEW       = PASS
DEV_INSTANCE_AVAILABLE = NO

MIGRATION_APPLIED_DEV  = NO
MIGRATION_APPLIED_PROD = NO

TABLES_EXPECTED = 57     TABLES_ACTUAL = NOT_APPLIED (não há banco)
VIEWS_EXPECTED  = 13     VIEWS_IMPLEMENTED = 13 (corpo escrito, não executado)
RPCS_EXPECTED   =  4     RPCS_IMPLEMENTED  =  4 (corpo escrito, não executado)

RLS_IMPLEMENTED = políticas escritas: deny-default + publisher + país + telemetria
RLS_BLOCKED_BY_AUTH_DECISION = 3 itens

COUNTRY_ISOLATION_TESTED     = FIXTURE + políticas no SQL
MULTILINGUAL_DB_TESTED       = FIXTURE
PROVENANCE_END_TO_END_TESTED = FIXTURE (8 elos, até o commit)

PUBLISHER_DRY_RUN         = PASS
PUBLISHER_IDEMPOTENCY_TEST = PASS (3.984 chaves, 0 novas na segunda)

SHADOW_VALIDATOR_READY = YES

FIRST_LOAD_INPUTS_TOTAL             = 9
FIRST_LOAD_INPUTS_WITH_FIXED_COMMIT = 9
FIRST_LOAD_INPUTS_WITH_RESOLVED_ARTIFACT = 8
FIRST_LOAD_INPUTS_NOT_MEASURED      = H3 · H5 · H6 · H8

TESTS_TOTAL = 859      TESTS_FAILED = 0

REAL_DATA_PUBLISHED = NO   FIRST_SHADOW_LOAD_EXECUTED = NO
V8_WIRED = NO              PRODUCTION_DEPLOY = NO

READY_FOR_FIRST_SHADOW_LOAD = NO
READY_TO_WIRE_REAL_DATA     = NO
```

### `EXACT_BLOCKERS`

```
1  DEV_INSTANCE_AVAILABLE = NO
   não há projeto Supabase, chave, CLI, psql nem Docker. Uma carga sombra compara o
   freeze com um BANCO; sem banco, não há o que comparar. É o único bloqueador que
   depende de alguém de fora: criar o projeto DEV e entregar a credencial ao servidor.

2  H3 sem artefato resolvido
   o commit está fixo; o arquivo não. Quatro candidatos listados, nenhum com 36 de nada.

3  o manifesto de rótulos de H2 tem três versões
   não bloqueia H2; bloqueia a contagem de rótulos.
```

**O bloqueador 1 é o único que impede a carga.** Os outros dois deixam duas entradas
incompletas — e estão declarados, não escondidos.
