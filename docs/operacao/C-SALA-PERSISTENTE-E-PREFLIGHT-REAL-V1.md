# C-SALA-PERSISTENTE-E-PREFLIGHT-REAL-V1 — RELATÓRIO E PACOTE LIVE

```
MISSAO             C-SALA-PERSISTENTE-E-PREFLIGHT-REAL-V1
RAMO               claude/sala-persistente-preflight-real-v1
BASE               f888776dffd789053fbaf39fc9fe630c74dde3ef  (HEAD funcional)
LIVE_WRITES        0
LIVE_DDL           0
LIVE_MIGRATION_APPLIED   NO
COLETA_REAL        NAO EXECUTADA
```

> **NADA FOI APLICADO NO LIVE, E NADA FOI COLETADO.** Toda a prova correu
> contra PostgreSQL 16 descartável, que nasce e morre com a bateria.

---

## 1 · EM PORTUGUÊS SIMPLES

**1. Qual era o defeito real da Sala?**
Ela escrevia o READY num ficheiro dentro do workspace do runner — e ninguém
guardava esse ficheiro. Nenhum `git add`, nenhum artefato, nenhum dono em banco.
O `checkout` seguinte limpa o que não está versionado. A decisão original
escolheu o **meio** e nunca respondeu à **sobrevivência**.

**2. Onde o READY vai passar a ficar?**
Numa tabela PostgreSQL: `public.sala_de_espera`, criada pela migration `031`.

**3. Por que esse backend foi escolhido?**
Porque a Sala não é um armazém de bytes — é uma **fila com estado**. Precisa de
unicidade, transação, chave estrangeira e consulta. Git está proibido por
`P-011`; o artefato do Actions expira em 30 dias e o próprio workflow já diz que
não é armazém canónico; o Storage guarda bytes e não tem `unique` nem transação;
e o par PostgreSQL+Storage não tem trabalho para o segundo membro, porque o
READY carrega um **ponteiro** e os bytes já têm dono em `raw_asset` →
`storage_object`.

**4. O ficheiro continua a existir?**
Continua, atrás do **mesmo** dono, e declarado **NÃO CANÓNICO**. Serve prova
offline e mais nada. O recibo de cada pouso diz qual backend escreveu
(`CANONICO: true/false`), e pedir o canónico sem DSN **falha alto** em vez de
cair para o disco em silêncio — porque essa queda era a falha original.

**5. Se o runner morrer, o READY sobrevive?**
Sim, e está medido matando o processo de verdade: um processo filho pousa, é
morto, e só então se pergunta ao banco. `READY_PERSISTS_AFTER_PROCESS_EXIT =
PASS`.

**6. Se rodar duas vezes, duplica?**
Não. Mesma corrida com o mesmo conteúdo devolve `REUSED` e o banco continua com
uma linha. Com conteúdo **diferente** levanta `RUN_ID_CONFLICT` e **não escreve
nada**.

**7. Se dois runners escreverem juntos, dá conflito?**
Dá o conflito certo, e não corrupção. Dois escritores da mesma corrida com o
mesmo conteúdo: um pousa, o outro reaproveita. Com conteúdo diferente: um pousa,
o outro é recusado. Duas corridas ao mesmo tempo: as duas pousam, sem se
misturarem. E um leitor a ler durante a escrita nunca vê meio estado.

**8. Como a Intelligence poderá tirar itens da Sala depois?**
`retirar(run_id, item_id, por)` marca `WAITING → CONSUMED`, com hora e autor. O
item deixa de aparecer nos pendentes e **continua na tabela**, auditável. Não há
veredito nenhum: `KEEP`/`TEMP`/`DISCARD` são da Intelligence, e a Intelligence é
outra missão. Existe prova que reprova se uma coluna de relevância aparecer.

**9. Como o sistema prova a VPN italiana antes de coletar?**
O portão de rede que já existia (`superficie/rede.py`) passou a saber responder
`EGRESS_COUNTRY_CODE`, e o workflow chama-o **antes** do passo que adquire.
Qualquer coisa que não seja `IT` fecha a porta — `UNKNOWN` incluído.

**10. O que foi provado em descartável?**
67 casos contra Postgres 16 real (30 ataques de red team, 0 sobreviventes), 34
casos no portão de egresso (10 ataques, 0 sobreviventes), 17 mutantes e 17 mortos, e 60 testes de unidade que correm sem banco nenhum.

**11. O que ainda NÃO foi aplicado no LIVE?**
A migration `031`. Ela não correu, nem uma vez, contra o banco de produção.

**12. Estamos prontos para a aplicação LIVE?**
**Não**, e o bloqueio não é desta missão: `docs/operacao/PREFLIGHT-LIVE-READONLY-V1.md`
mediu hoje `LIVE_RESTORE_STATUS = NOT_PROVEN`. Enquanto não existir prova de que
se consegue **voltar atrás**, nenhuma alteração estrutural do LIVE é segura.

**13. Depois da aplicação, podemos repetir o canário italiano?**
Sim — os dois blockers que o pararam ficam fechados. Mas só **depois** da
aplicação, e a aplicação depende do ponto 12.

---

## 2 · A DECISÃO, EM NÚMEROS

```
WAITING_ROOM_CANONICAL_BACKEND        POSTGRES · public.sala_de_espera
WAITING_ROOM_CANONICAL_OWNER          admissao/sala_de_espera.py   (o MESMO)
WAITING_ROOM_CANONICAL_IDENTITY       (run_id, ordem)
WAITING_ROOM_CANONICAL_WRITE          pousar(run_id, unidades)
WAITING_ROOM_CANONICAL_READ           ler(run_id) · listar_pendentes(limite)
WAITING_ROOM_CANONICAL_ACK            retirar(run_id, item_id, por)
WAITING_ROOM_CANONICAL_CONFLICT_RULE  impressao diferente -> RUN_ID_CONFLICT
WAITING_ROOM_CANONICAL_RETRY_RULE     impressao igual -> REUSED
WAITING_ROOM_CANONICAL_CRASH_RULE     uma transacao, ou nada
WAITING_ROOM_CANONICAL_CONCURRENCY    pg_advisory_xact_lock por CORRIDA
```

### 2.1 · Os backends, medidos e não preferidos

| | durabilidade | atomicidade | idempotência | concorrência | consulta | crash | auditoria | linhagem | complexidade | custo | um dono | Intelligence | `P-011` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **A** filesystem local | **NÃO** — morre com o job | sim (`os.replace`) | sim | trava que fica presa se o processo morre | não | parcial | sim | por texto | baixa | 0 | sim | não sabe listar pendentes | ok |
| **B** Git | sim | sim | sim | colide | fraca | sim | sim | por texto | alta | 0 | sim | mau | **VIOLA** |
| **C** artefato Actions | **30 dias** | sim | não | não | não | não | fraca | não | baixa | 0 | sim | não | ok |
| **D** Supabase Storage | sim | por objeto | não | **sem `unique`** | não | não | sim | não | média | ~0 | sim | fraca | ok |
| **E** PostgreSQL | **sim** | **sim** | **sim** | **sim** | **sim** | **sim** | **sim** | **FK** | média | ~0 | **sim** | **sim** | ok |
| **F** PG + Storage | sim | sim | sim | sim | sim | sim | sim | FK | **alta** | ~0 | sim | sim | ok |

**F foi recusada por não ter trabalho para o segundo membro.** A Sala não guarda
bytes: guarda um ponteiro (`RAW_OBSERVATION_ID`), e os bytes já têm dono.

```
A MENOR IDENTIDADE QUE FECHA A ESTRADA É A CERTA.
```

### 2.2 · O achado que mudou a chave

A chave da fila ia ser `(run_id, item_id)`. Medi-la matou-a:

```python
ITEM_ID = str(item.get("id") or item.get("url") or "?")
```

`"?"` é alcançável. **Dois itens admitidos sem `id` e sem `url` na mesma corrida
trazem ambos `ITEM_ID = "?"`** — e uma chave primária ali deitaria um deles fora.

```
ITEM_ID NÃO É IDENTIDADE GARANTIDA DENTRO DA CORRIDA.
```

A chave passou a ser `(run_id, ordem)`. `item_id` continua guardado e indexado;
`retirar()` por um `ITEM_ID` ambíguo é **recusado** com nome (`ItemAmbiguo`) em
vez de escolher um à sorte. Está provado nos dois sentidos: os dois itens pousam
sem nenhum se perder, e a retirada por `"?"` é negada.

---

## 3 · O QUE FOI PROVADO

### 3.1 · Contra Postgres 16 descartável — `provas/a_sala_sobrevive_ao_processo.py`

```
CASOS=67 · PASS=67 · FAIL=0
RED_TEAM_ATTACKS=30 · RED_TEAM_SURVIVORS=0
SALA_SOBREVIVE_AO_PROCESSO=PASS
```

```
READY_PERSISTS_AFTER_PROCESS_EXIT       PASS
READY_PERSISTS_AFTER_NEW_PROCESS        PASS
READY_PERSISTS_AFTER_BACKEND_RECONNECT  PASS
SAME_RUN_SAME_READY                     REUSED
SAME_RUN_DIFFERENT_READY                CONFLICT  (e nada escrito)
PARTIAL_INVISIBLE                       YES
DUPLICATE_READY_APOS_RETRY              0
LOST_UPDATES                            0
DUPLICATES                              0
SILENT_CONFLICTS                        0
DIRTY_READS                             0
CROSS_RUN_CONTAMINATION                 0
READY_WITHOUT_RUN                       0   (chave estrangeira, nao disciplina)
READY_WITHOUT_RAW_EXISTENTE             0   (chave estrangeira)
READY_WITHOUT_STORAGE                   0
READY_FIELDS                            12
```

**Cardinalidade:** 0 admitidos não cria registo nenhum (e a corrida continua a
existir no dono do RUN); 1 e N pousam e leem-se pela ordem em que pousaram;
admitidos e recusados misturados — só o admitido aparece nos pendentes.

**Linhagem, numa consulta só:**
`READY → RAW → STORAGE → bytes` (sha confere) e `READY → RUN → SOURCE`.

⚠️ **E a observação pode ser de OUTRA corrida, de propósito.** Quem ADMITE não é
forçosamente quem CAPTUROU — a `029` e a `030` já o tinham dito sobre a passagem
que estrutura. Uma trava a exigir `raw_asset.run_id = sala.run_id` proibiria um
caso legítimo, e por isso ela **não existe**. O que se exige é que a observação
EXISTA, e isso é a chave estrangeira.

### 3.2 · O portão de egresso — `provas/o_egresso_antes_da_aquisicao.py`

```
CASOS=34 · PASS=34 · FAIL=0
RED_TEAM_ATTACKS=10 · RED_TEAM_SURVIVORS=0
ACQUISITION_STARTED_ON_NON_IT   0
ACQUISITION_STARTED_ON_UNKNOWN  0
REAL_RUNNER_EGRESS              US   (esta sessao — e por isso NAO se declara IT)
```

`it` · ` IT ` · `IT` → o mesmo país. `FR`, `US`, timeout, HTTP 500, JSON
partido, `country` ausente, `country` não-texto, três letras, corpo vazio, lista
em vez de objeto, `null` → `UNKNOWN`, e **todos bloqueiam**.

O IP público, a cidade e a organização **não entram no resultado**: o que fica é
o país, o momento e o checker.

### 3.3 · Mutação — `provas/mutacao_da_sala_duravel.py`

```
MUTANTES=17 · MORTOS=17 · SOBREVIVENTES=0
MUTANTES_MORTOS=ALL
```

⚠️ **A primeira ronda teve 2 sobreviventes, e os dois eram mutantes maus meus.**
Um trocava `if escolhido == POSTGRES:` por `if escolhido == POSTGRES and
_dsn():` — e sem DSN o fluxo caía no ramo final, que **também** falha fechado. O
outro alargava a chave primária de forma que não mudava a unicidade.

```
UM MUTANTE QUE NÃO MUDA O COMPORTAMENTO NÃO MEDE A LEI: MEDE O TEXTO.
```

Foram substituídos por mutantes que constroem mesmo a queda silenciosa e que
matam mesmo a transição da fila. Os dois morreram.

### 3.4 · Sem banco nenhum — `tests/`

```
tests/test_sala_duravel.py + tests/test_preflight_de_egresso.py
60 testes · OK
```

---

## 4 · TRÊS DEFEITOS QUE A PRÓPRIA MISSÃO ENCONTROU EM SI

Nenhum destes foi lido num documento. Todos apareceram a medir.

**(1) `None` a querer dizer duas coisas.** O portão de egresso usava `bruto=None`
para dizer «não me deram corpo, vai medir» — e `None` é também o que o checker
devolve quando não respondeu. A prova do timeout **foi à rede a sério** e voltou
com um país verdadeiro: um caso de red team passou por acidente. Corrigido com
um sentinela próprio.

```
DOIS SIGNIFICADOS NO MESMO VALOR É COMO SE LÊ O ERRADO.
```

**(2) O portão aprovava um ambiente e a aquisição corria noutro.** A primeira
versão declarava `SINTONIA_SALA_BACKEND` só dentro do passo do preflight. Ele
passava — e o passo seguinte, o que adquire de verdade, corria sem a variável e
escrevia o READY no ficheiro efémero. A declaração subiu para o nível do **job**.

```
UM PORTÃO QUE MEDE UM AMBIENTE E DEIXA PASSAR PARA OUTRO NÃO MEDIU NADA.
```

**(3) A prova sujava a árvore que media.** A bateria de mutação corre numa cópia
com `data/` ligado por symlink à árvore real; o mutante que faz a sala cair para
ficheiro escreveu, por esse symlink, um ficheiro dentro do repositório de
verdade — e ele chegou a aparecer no `git add`. A bancada do backend de ficheiro
passou a ser sempre descartável.

```
UMA PROVA QUE SUJA A ÁRVORE QUE MEDE DEIXOU DE SÓ MEDIR.
```

**E um quarto, que o System Map apanhou.** Houve um `motor/preflight_da_coleta.py`
a compor os dois portões. O validador reprovou-o — uma peça nova a morar numa
gaveta que não era a do seu território — e a pergunta seguinte matou-o: para que
serve um terceiro ficheiro se cada dono já responde por si e a ordem mora no
workflow? Foi deitado fora, e há prova que reprova se ele voltar.

```
UM COMPOSITOR QUE SÓ ENCADEIA DOIS DONOS
É UM TERCEIRO SÍTIO ONDE A VERDADE PODE DIVERGIR.
```

---

## 5 · REGRESSÃO

Mesmo ambiente, mesma bateria, antes e depois. O «antes» foi medido na árvore
limpa do HEAD funcional, com as alterações desta missão em `stash`.

```
                  ANTES     DEPOIS
MODULES             152        154
TESTS              3884       3944
FAILURES             18         18
ERRORS               15         15
SKIPS               194        194
LOAD_ERRORS           1          1

NEW_FAILURES          0
DISAPPEARED_TESTS     0
```

⚠️ **E o `0` só é `0` à segunda medição.** A primeira contou **9 falhas novas**, e
nenhuma delas era ruído:

| falha nova | o que era | o que se fez |
|---|---|---|
| `test_migrations::test_nenhuma_migration_foi_executada` | **toda** migration desta casa carrega a marca `NÃO EXECUTADA`, e a `031` não a tinha | a marca entrou, e diz a verdade: provada em descartável, nunca no LIVE |
| `test_a_sala_de_espera_nao_tem_morada::test_nenhuma_migration_deu_MORADA…` | uma sentinela que exigia **zero** tabelas para a Sala | mudou de lado **com a razão escrita no corpo**, e passou a exigir exactamente **uma**, a declarada — que é mais forte do que zero |
| 5 × `test_metricas` (`TEST_COUNT_CURRENT`) | o número de testes é publicado em oito documentos e tem dono | sincronizado pelo dono (`pacote/metricas_canonicas.py --sync`), nunca à mão |
| 2 × «esta missão não tocou em `admissao/`» | comparam `git diff HEAD` | eram o efeito de correr a bateria com a árvore por commitar; passam com o trabalho commitado |

```
UMA REGRESSÃO QUE SE MEDE UMA VEZ SÓ MEDE A SORTE.
```

As 18 falhas e 15 erros são **anteriores a esta missão** e vêm do ambiente —
ficheiros `.gz` que o `.gitignore` não traz, ausência de GPU, amostras de
proveniência que não existem nesta árvore. O `LOAD_ERROR` é `test_comunicacao`,
que chama `sys.exit()` ao ser importado.

```
SKIP != PASS. E NOT_RUN != PASS.
```

---

## 6 · SYSTEM MAP

```
SYSTEM_MAP_BEFORE   FAIL · P1_SEM_DRIFT   (o mapa nao conhecia o codigo novo)
SYSTEM_MAP_AFTER    PASS
```

Regenerado pela cadeia canónica (`generate_system_map.py`), nunca editado à mão.
O que mudou na parte **declarada** — que é a parte de gente — foi o texto da peça
`C-SALA-DE-ESPERA`, que descrevia um backend que já não é o canónico, e a
correcção de «11 campos» na peça da medição.

⚠️ Nenhuma peça nova foi criada. A tentativa de criar uma (para o compositor) foi
o que revelou que o compositor não devia existir.

---

## 7 · PACOTE LIVE — PREPARADO, **NÃO APLICADO**

```
LIVE_MIGRATION_REQUIRED   YES
MIGRATION_FILE            supabase/migrations/031_a_sala_de_espera_ganha_dono_duravel.sql
MIGRATION_SHA256          9414b4f7becd81382512ce2af5b5a28f334aa70b6cea127bdb6ff8c52eb306e3
NEXT_MIGRATION_NUMBER     031   (medido: 030 e a ultima no disco, sem numeros repetidos)
```

⚠️ **E ela carrega a marca que TODA migration desta casa carrega: `NÃO
EXECUTADA`.** Não é cerimónia — `tests/test_migrations.py` reprova sem ela, e foi
a bateria que a cobrou. A marca diz o que é verdade: aplicada e atacada em
descartável, nunca contra produção.

```
DESIGNED != DB_TESTED != LIVE.
```

### 7.1 · PREFLIGHT_SQL — somente leitura, antes de qualquer DDL

```sql
-- 1 · o livro-razao conhece ate onde?
select versao, resultado, aplicada_em from public.schema_migracao order by versao;
-- Esperado: 030 presente, 031 AUSENTE.

-- 2 · a tabela ja existe? (nao devia)
select to_regclass('public.sala_de_espera');       -- esperado: NULL

-- 3 · as duas chaves estrangeiras tem alvo?
select to_regclass('public.collection_run'), to_regclass('public.raw_asset');
-- esperado: os dois NAO nulos

-- 4 · ha drift no livro? (a propria cadeia ja recusa, mas confere-se antes)
select versao, sha256 from public.schema_migracao where versao = '031';
-- esperado: zero linhas
```

### 7.2 · APPLY — pelo mecanismo canónico, e só por ele

```bash
bash motor/cadeia_canonica.sh migrations "$SUPABASE_DB_URL"
```

Não há SQL avulso a aplicar à mão. A cadeia: recusa números repetidos, salta o
que já está no livro-razão **conferindo o SHA**, aplica cada migration
`--single-transaction` com o registo no livro **dentro da mesma transação**, e
pára antes de qualquer DDL se uma migration aplicada tiver mudado.

### 7.3 · POST_APPLY_SQL

```sql
select resultado, sha256 from public.schema_migracao where versao = '031';
-- esperado: APLICADA · 9414b4f7...6e3

select count(*) from public.sala_de_espera;                 -- esperado: 0
select count(*) from information_schema.columns
 where table_name = 'sala_de_espera';                       -- esperado: 17
select conname from pg_constraint
 where conrelid = 'public.sala_de_espera'::regclass order by conname;
-- esperado: 5 CHECK + PK + 2 FK
select indexname from pg_indexes
 where tablename = 'sala_de_espera' order by indexname;
-- esperado: sala_de_espera_pkey, sala_pendentes_idx,
--           sala_por_corrida_idx, sala_por_observacao_idx
```

### 7.4 · ROLLBACK / FORWARD RECOVERY

```sql
-- A migration e PURAMENTE ADITIVA: cria UMA tabela e TRES indices, e nao toca
-- em nenhuma tabela existente. O desfazer e simetrico e nao tem passageiros:
begin;
  drop table if exists public.sala_de_espera;
  delete from public.schema_migracao where versao = '031';
commit;
```

⚠️ **Isto desfaz o SCHEMA, e não substitui um restore.** Assim que a Sala tiver
material real, `drop table` **apaga READY**. A partir daí o caminho é forward
recovery, e forward recovery exige o backup que o projeto ainda não provou.

### 7.5 · O que a aplicação muda, e o que ela custa

```
EXPECTED_SCHEMA_DELTA   +1 tabela (public.sala_de_espera, 17 colunas)
                        +3 indices  ·  +2 chaves estrangeiras  ·  +5 CHECK
                        +1 linha em public.schema_migracao
                        0 tabelas alteradas · 0 colunas removidas · 0 dados tocados
EXPECTED_DATA_DELTA     0 linhas. A tabela nasce VAZIA.
LOCK_RISK               BAIXO. `create table` nova nao pega lock em tabela
                        existente. As duas chaves estrangeiras pegam
                        `SHARE ROW EXCLUSIVE` em `collection_run` e `raw_asset`
                        por milissegundos — nao bloqueiam leitura, e bloqueiam
                        escrita apenas durante a criacao.
DOWNTIME_EXPECTED       NENHUM
BACKUP_REQUIREMENT      EXIGIDO ANTES DE APLICAR — e e aqui que esta o bloqueio
RECOVERY_DEPENDENCY     RESTORE_NOT_PROVEN
```

### 7.6 · O BLOQUEIO, E ELE NÃO É DESTA MISSÃO

`docs/operacao/PREFLIGHT-LIVE-READONLY-V1.md`, medido em **2026-09-13**:

```
LIVE_BACKUP_STATUS    NOT_MEASURED
LIVE_RESTORE_STATUS   NOT_PROVEN
LIVE_READY_FOR_APPLY  NO
BLOCKER               RESTORE_NOT_PROVEN
```

```
BACKUP EXISTE != RESTORE PROVADO.
```

Procurei de novo em `provas/`, `motor/`, `.github/` e `docs/`: **não existe
nenhum ensaio de restore**. Prova é artefacto positivo, e a ausência dele é
ausência de prova.

Por isso, e conforme o `§31` desta missão:

```
READY_FOR_LIVE_APPLY = NO   — mesmo com a implementacao correcta e provada.
```

---

## 8 · VEREDITO

```
SALA_PERSISTENTE_DESIGN          PASS
EGRESS_PREFLIGHT                 PASS
READY_FOR_LIVE_APPLY             NO    (RESTORE_NOT_PROVEN, anterior a esta missao)
READY_FOR_REAL_CANARY_AFTER_LIVE YES
```

---

## 9 · FECHAMENTO

**O QUE MUDOU**
A Sala de Espera ganhou backend durável em PostgreSQL, atrás do **mesmo** dono, e
uma fila com transição auditável. O portão de rede que já existia passou a saber
responder pelo país de egresso, e o workflow chama os dois portões antes de
adquirir.

**QUAL A PROVA**
67 casos contra Postgres 16 real (30 ataques, 0 sobreviventes) · 34 casos no
portão de egresso (10 ataques, 0 sobreviventes) · 17 mutantes, 17 mortos · 60
testes sem banco · regressão com `NEW_FAILURES = 0` · System Map `PASS`.

**O QUE NÃO MUDOU**
O contrato READY (12 campos, `COL-LAW-043`), a Bíblia, o dono da Sala, a API que
o orquestrador e a rota forward chamam, e o LIVE.

**O QUE CONTINUA DESCONHECIDO**
Se o LIVE tem backup, e se um restore funciona. E qual o egresso real do runner
italiano — esta sessão sai por `US`, e declarar `IT` sem medir seria fabricar
ambiente.

**QUAL RISCO RESTOU**
1. `RESTORE_NOT_PROVEN` — o único bloqueio à aplicação.
2. O backend de ficheiro continua a existir. Está declarado não canónico, o
   recibo di-lo, o portão recusa-o e um mutante morre por causa disso — mas ele
   existe, e existe por compatibilidade com as provas offline.
3. A Sala ainda não tem **consumidor**. `listar_pendentes` e `retirar` existem e
   estão provados; ninguém os chama ainda, porque a Intelligence é outra missão.
4. A migration nunca correu contra o LIVE. `DESIGNED != DB_TESTED != LIVE`.

```
KNOW_HOW_DELTA      SIM   (§110 · escrito na branch canonica do know-how)
BIBLE_CHANGE        NENHUMA
CONTRACT_CHANGE     NENHUMA   (READY continua os 12 campos da COL-LAW-043)
ADR_CHANGE          SIM · emenda em docs/decisoes/ADR-SALA-DE-ESPERA-V1.md
                    (o ficheiro da V1, com capitulo novo — NAO um ADR-V2)
SYSTEM_MAP_CHANGE   SIM · regenerado pela cadeia; texto de C-SALA-DE-ESPERA
                    corrigido no ficheiro DECLARADO
LIVE_WRITES         0
NEXT_MINIMUM_STEP   provar RESTORE no LIVE. Sem isso, nenhuma aplicacao
                    estrutural e segura — e o canario italiano continua parado.
```

---

## HARD STOP

Não se coletou. Não se aplicou migration. Não se tocou no portal, no legado
italiano nem na Intelligence. A integração desta branch volta ao coordenador.
