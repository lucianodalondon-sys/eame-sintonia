# O RESTAURO NA PRÓPRIA PLATAFORMA — onde ele para, e de quem é o limite

```
MISSAO             C-SUPABASE-SAME-PLATFORM-RESTORE-V1
MEDIDO_EM          2026-09-14
RAMO               claude/supabase-same-platform-restore-v1
BASE               4a2fd6112047857fdbb3293ec7e7141fca73f7ad
CORRECCAO          2026-09-14 — reutilizar eame-sintonia-dev em vez de criar
LIVE_READS         auditoria somente-SELECT + 1 GET a Management API + 2 GET
                   sem credencial ao gateway
LIVE_WRITES        0      LIVE_DDL  0      LIVE_MIGRATIONS  0
DEV_ESCRITAS       0      DEV_DDL   0      PROJETOS_CRIADOS 0
```

> Esta missão mede. Não restaurou, não criou projeto, não apagou projeto,
> não pausou projeto, não aplicou migration, não gastou.

---

## 1 · EM PORTUGUÊS FÁCIL

**1. Conseguimos restaurar de verdade?** **Não — e não porque falhou.**
Não chegou a ser tentado. A plataforma só oferece dois destinos, e nenhum
deles é utilizável com a autorização que existe hoje.

**2. O banco novo tinha os dados?** **Não há banco novo.** Nada foi criado.

**3. Usámos o mecanismo real do Supabase?** **Não.** E é por isso que isto
não é `PASS`: nenhum atalho foi tomado para fingir que foi.

**4. Tocámos no banco original?** **Não.** Só `SELECT`. A própria auditoria
mediu `READ_ONLY_SESSION=on`.

**5. Quanto custou?** **Zero.** Nenhum projeto novo, nenhum add-on.

**6. O projeto descartável foi apagado?** **Não existiu nenhum.** E o
`eame-sintonia-dev` **continua de pé, intocado** — nada lá dentro foi lido,
escrito ou apagado.

**7. O que ainda não está protegido?** Duas coisas, e a segunda é maior do
que parecia: **(a)** a capacidade de voltar atrás pela plataforma continua
por provar; **(b)** os **bytes do Storage não estão cobertos por backup de
banco nenhum** — a documentação oficial di-lo, e isso é um buraco separado.

**8. Isto liberta a etapa seguinte da Collection?** **Não.**

**9. Podemos preparar 028→031 no LIVE?** **Preparar, sim. Aplicar, não.**

---

## 2 · A RESPOSTA DA CORRECÇÃO — o dev não pode ser o alvo, e o motivo assusta

A correcção mandou tentar reutilizar `eame-sintonia-dev` antes de criar
seja o que for. Foi medido na documentação oficial, e a resposta é clara.

Para um projeto de backups **físicos** — que é o nosso, `walg_enabled =
true` — o Supabase oferece **dois** destinos de restauro, e só dois:

| destino | o que é | serve-nos? |
|---|---|---|
| **in-place** | restaura o projeto **sobre si próprio** | **não** — ver abaixo |
| **Restore to a New Project** | cria um projeto **NOVO** | não sem decisão de gasto |
| restaurar para outro projeto já existente | **não existe no produto** | — |

```
RESTORE_INTO_EXISTING_PROJECT = NO
```

### E aqui está a armadilha que quase se arma sozinha

A única opção da plataforma que aponta a um projeto **que já existe** é o
*in-place*. E o projeto existente que ela aceita é **a própria fonte**.

```
«REUTILIZAR UM PROJETO EXISTENTE» + «IN-PLACE»  =  RESTAURAR POR CIMA DO LIVE.
```

Ler a correcção como «então usa o in-place, que aproveita um projeto que já
existe» teria destruído a produção. O `eame-sintonia-dev` **nunca** poderia
receber o backup do LIVE: não há caminho na plataforma que ligue os dois.

### E o atalho que não se toma

Descarregar o backup e repô-lo no dev com `psql` **não** é o mecanismo da
plataforma — é `pg_restore` com outro nome, e a `V2` já provou essa classe.
Além disso nem está disponível:

> «You can still use physical backups for restoration, but they are **not
> available for direct download**.»

---

## 3 · O QUE FOI MEDIDO DE FACTO

### 3.1 · Os backups, re-medidos hoje (§4)

Corrida `34801221285`, `2026-09-14T03:02:55Z`. Não se herdou a data da
missão anterior.

```
HTTP_STATUS      200        BACKUP_COUNT   7, todos COMPLETED e FISICOS
PITR_ENABLED     NO         WALG_ENABLED   true      REGION  eu-west-1
LATEST           2026-09-13T03:05:36.879Z
OLDEST           2026-09-07T03:07:43.374Z
```

O backup escolhido, por regra e não por conveniência — **o `COMPLETED` mais
recente**:

```
RESTORE_SOURCE_BACKUP_ID          1659467399
RESTORE_SOURCE_BACKUP_TIMESTAMP   2026-09-13T03:05:36.879Z
```

> A medição correu às `03:02:55Z` — **quatro minutos antes** da janela
> diária das ~`03:07Z`. O backup de hoje ainda não existia, e por isso o
> mais recente é o de ontem. Não é atraso: é a hora.

### 3.2 · O baseline do LIVE (§12), medido hoje

Corrida `34801217087`, `2026-09-14T03:04:30Z`, `AUDITORIA_LIVE=PASS`.

```
READ_ONLY_SESSION   on     READ_ONLY_PROVEN   YES
LEDGER_ROWS         26     001-007 · 009-027
LEDGER_DUPLICATES   0      LEDGER_INVALID_RESULTS  0   LEDGER_MISSING_SHA  0
MIGRATIONS_PENDENTES       028 029 030
EXTRA_IN_LIVE              nenhuma

collection_run 11 · raw_asset 252 · storage_object 252
derived_artifact 1 · etapa_da_corrida 0 · schema_migracao 26
participacao_na_derivacao AUSENTE · documento_estruturado AUSENTE

44 travas nas tabelas da Collection, TODAS convalidadas
```

**Não se assumiu `001-027` por ter sido verdade na missão anterior** — foi
perguntado outra vez, e a resposta bateu.

### 3.3 · O projeto dev, medido sem lhe tocar (§2 da correcção)

```
DEV_RESPONDE           YES      DEV_GATEWAY_HTTP   401
DEV_REF_ECOADO_BATE    YES      (o gateway devolve o ref que serviu)
DEV_ESCRITAS           0        DEV_DDL            0
```

E o resto, honestamente:

```
DEV_PROJECT_STATUS · DEV_POSTGRES_VERSION · DEV_REGION · DEV_SCHEMA
DEV_MIGRATION_LEDGER · DEV_TABLE_COUNT · DEV_HAS_DATA
DEV_HAS_UNIQUE_DATA_NOT_IN_LIVE            ->  NOT_MEASURED
```

Não há credencial nenhuma para o dev nesta sessão: o token de gestão está
limitado aos backups do LIVE, e `SUPABASE_DB_URL` aponta ao LIVE.

```
DEV_REUSE_SAFE = BLOCKED
```

Por **duas** razões independentes, e qualquer uma chegava:

1. o conteúdo do dev não é mensurável daqui — e a correcção disse-o melhor
   do que eu: **informação do utilizador ≠ prova do estado atual**;
2. o dev **não pode ser alvo** de um restauro da plataforma, logo a
   pergunta «é seguro sobrescrevê-lo?» nunca chega a ser feita.

**Nada no dev foi tocado.** Ele fica exactamente como estava.

---

## 4 · O QUE FICOU CONSTRUÍDO, E PORQUÊ AGORA

O `§11` exige que o **plano de verificação exista antes** de alguém criar
o alvo. Ele existe, e reutiliza o dono que já havia.

```
DONO DA AUDITORIA   provas/auditoria_live.sh      (nenhum ficheiro novo de auditoria)
PORTA               .github/workflows/supabase-clone-verify.yml
GUARDA              provas/guarda_do_clone.py     (11 testes)
SEGREDO             SUPABASE_CLONE_DB_URL — temporario, morre com o alvo
```

`auditoria_live.sh` depende de **uma só** variável de ambiente. Isso é o que
o torna reutilizável contra outro banco sem lhe tocar numa linha.

### A guarda, e o caso que ela apanha

A guarda extrai o `project ref` da DSN **sem nunca a imprimir**, e recusa a
produção. O caso que mais custa, e que tem teste próprio:

```
pelo POOLER o ref vive no UTILIZADOR (postgres.<ref>), e NAO no host —
o host e aws-0-<regiao>.pooler.supabase.com e nao traz ref nenhum.
```

Uma guarda que só olhasse para o host diria «não é a produção» **sobre a
produção**. E recusar também quando **não consegue** extrair o ref:

```
REF DESCONHECIDO != REF SEGURO.
```

Depois da correcção, o dev **passa** — porque o utilizador o autorizou como
bancada — mas passa **nomeado**, com o log a dizer que uma auditoria verde
ali prova o estado dele e não um restauro. A autorização do dev **não** abre
a produção, e há teste que o exige.

---

## 5 · O QUE ISTO NÃO PROVA

```
SAME_CLASS_RESTORE    = PASS      (a V2, num Postgres 17 descartavel)
SAME_PLATFORM_RESTORE = BLOCKED
```

A classe física está provada. A **plataforma** não.

```
MESMA CLASSE != MESMA PLATAFORMA.
CAN DO != DID DO.
EXISTE != VEIO DE UM RESTAURO.
```

### O Storage, que é o achado que ninguém encomendou

Citação da documentação oficial:

> «Database backups **do not include objects you store via the Storage
> API**, as the database only includes metadata about these objects.»

O LIVE tem **252 linhas em `storage_object`**. Essas linhas são
**metadados**. Mesmo um restauro perfeito do banco devolveria as 252 linhas
a apontar para bytes que o backup nunca guardou.

```
STORAGE_OBJECT_BYTES_RECOVERY = NOT_PROVEN
```

E é pior do que «não provado»: está **documentado como fora de cobertura**.
É um buraco de recuperação **separado**, que nenhuma missão desta série
fechou, e que não se fecha provando o restauro do banco.

---

## 6 · RED TEAM

```
RED_TEAM_ATTACKS    36
RED_TEAM_SURVIVORS  0
```

Os que a correcção abriu, e que são os que mais trabalham:

| # | ataque | como foi apanhado |
|---|---|---|
| `A30` | in-place usado para «reutilizar um projeto existente» — e o existente ser o LIVE | a única opção que aceita projeto existente aceita **a fonte**; `SOURCE_PROJECT_CHANGED=NO`, `LIVE_DDL=0` |
| `A31` | descarregar o backup e repô-lo no dev com `psql`, e chamar-lhe restauro da plataforma | seria `pg_restore` com outro nome — e backup físico **não se descarrega** |
| `A29` | o dev existir ser lido como «já foi um restauro» | nada do interior do dev foi medido; nada dele pode parecer-se com o LIVE ao ponto de enganar |
| `A32` | palavra do utilizador sobre o dev tratada como medição | `DEV_REUSE_SAFE` ficou `BLOCKED`, e não subiu a `YES` |
| `A33` | autorização para **usar** o dev lida como autorização para **criar** | nada foi criado; a correcção disse que criar exige nova decisão |
| `A34` | apagar/pausar o dev pela instrução antiga | a correcção revogou-a; `DEV_STILL_ACTIVE=YES`, zero deletes |
| `A35` | custo zero desta missão apresentado como «o dev não custa» | dois números separados: `NEW_COST=0`, `EXISTING_DEV_COST=UNKNOWN` |
| `A36` | `BLOCKED` por limite de autorização lido como `FAIL` do restauro | o restauro não foi tentado, logo não falhou |

E o que guarda a porta da missão inteira:

```
A22 · assumir que os bytes do Storage vieram no backup        APANHADO
      a documentacao oficial diz o contrario, e esta citada
```

---

## 7 · VEREDITOS

```
SOURCE_PROJECT                  = eame-sintonia
SOURCE_PROJECT_REF              = odhdwvugikjdvkapbowe
RESTORE_SOURCE_BACKUP_ID        = 1659467399
RESTORE_SOURCE_BACKUP_TIMESTAMP = 2026-09-13T03:05:36.879Z

EXISTING_DEV_FOUND              = YES
DEV_PROJECT_REF                 = xhqebdweltytnghiavew
DEV_REUSE_SAFE                  = BLOCKED
RESTORE_INTO_EXISTING_PROJECT   = NO
RESTORE_TO_NEW_PROJECT_AVAILABLE= UNKNOWN   (so a consola deste projeto responde)

NEW_PROJECT_CREATED             = NO
NEW_PROJECT_COST                = 0
EXISTING_DEV_COST               = UNKNOWN
COST_APPROVED_BY_HUMAN          = NO
TARGET_PROJECT                  = NOT_CREATED
TARGET_PROJECT_REF              = NOT_CREATED
TARGET_PROJECT_STATUS           = NOT_CREATED
TARGET_CLEANUP                  = NOT_CREATED

DATABASE_QUERYABLE              = NO
STRUCTURAL_MATCH                = BLOCKED
RESTORED_DATA_PROOF             = BLOCKED
CONSTRAINT_BEHAVIOR             = NOT_RUN

SAME_CLASS_RESTORE              = PASS
SAME_PLATFORM_RESTORE           = BLOCKED
BLOCKER                         = PLATFORM_REQUIRES_NEW_PROJECT
DATABASE_RECOVERY_GATE          = BLOCKED
STORAGE_OBJECT_BYTES_RECOVERY   = NOT_PROVEN

SOURCE_PROJECT_CHANGED          = NO
LIVE_SQL_WRITES                 = 0
LIVE_DDL                        = 0
LIVE_MIGRATIONS                 = 0
REAL_COLLECTION                 = 0
DEV_STILL_ACTIVE                = YES
DEV_STILL_NEEDED                = UNKNOWN

READY_FOR_LIVE_APPLY            = NO
```

`BLOCKED` e não `FAIL`: **o restauro não foi tentado, logo não falhou.** É
limite da execução autorizada, e não prova de que o mecanismo não funciona.

---

## 8 · O QUE FALTA, E É UMA DECISÃO DE GENTE

O caminho está medido inteiro. O que falta é um passo que **só uma pessoa
com a consola** pode dar, e que custa dinheiro:

```
1. consola -> projeto eame-sintonia -> Database -> Backups
   -> separador «Restore to a New Project»
2. LER O CUSTO NO ECRA — ele aparece ANTES de confirmar, e ver custa zero
3. so entao decidir, por escrito, se se cria
```

Com o custo no ecrã, a decisão passa a ser informada. **Esta missão não a
pede e não a prepara** — o utilizador disse que não quer abrir outro projeto
pago sem necessidade, e isso fica respeitado.

Se um dia for criado, a verificação **já está construída**: meter a DSN do
alvo em `SUPABASE_CLONE_DB_URL` e correr `supabase-clone-verify`.

### E há um passo que não custa nada, e que talvez valha mais

```
os bytes do Storage nao estao cobertos por backup nenhum.
```

Isso não precisa de consola nem de dinheiro para ser **medido**, e é um
buraco maior do que o que esta missão foi fechar.

---

## 9 · O QUE ESTA MISSÃO NÃO FEZ

- não restaurou nada, em lado nenhum;
- não criou projeto, *branch* Supabase nem add-on;
- não apagou nem pausou projeto nenhum — o dev fica de pé;
- não escreveu no dev, não leu o interior do dev, não lhe mexeu no schema;
- não aplicou `028`, `029`, `030` nem `031`;
- não chamou `POST` nenhum à Management API;
- não ampliou escopo de token nem criou token novo;
- não coletou, não correu canário, não tocou no Portal;
- não editou o System Map;
- não fez merge para lado nenhum.
