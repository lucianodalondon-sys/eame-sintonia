# PROVA DE RECUPERAÇÃO — ANTES DE TOCAR NO LIVE

```
MISSAO             C-RECOVERY-PROOF-BEFORE-LIVE-V1
MEDIDO_EM          2026-09-13T13:03Z
LINHA_FUNCIONAL    claude/raw-observation-identity-3jbwco
INITIAL_HEAD       903e18605e3fb3e66b616974aa80ff07835dc5d8
RAMO_DESTA_MISSAO  claude/recovery-proof-before-live-v1
LIVE_WRITES        0
MIGRATIONS_APLICADAS_NO_LIVE  0
```

> ## ⚠️ LEIA O §12 ANTES DO §2 E DO §8
>
> Depois de esta missão fechar, a coordenação **mediu o LIVE por fora** e a
> linha funcional **avançou**. O `§12 · ADDENDUM` corrige as classificações que
> envelheceram: `SAME_CLASS_RESTORE` deixou de ser `UNKNOWN` e passou a **`NO`**.
> O portão continua `BLOCKED` — a medição nova **apertou** o veredito, não o
> afrouxou. As secções `§2` e `§8` ficam como foram escritas, datadas, e o
> addendum diz o que nelas deixou de valer.

> **Esta missão não aplicou nada em produção, e não é ela quem autoriza aplicar.**
> Ela responde a UMA pergunta: se uma futura aplicação da `028`/`029`/`030`
> correr mal, temos **prova executável** de que conseguimos voltar atrás?

---

## 1 · A PERGUNTA, PARTIDA EM TRÊS

Juntas, as três parecem uma. Separadas, duas delas têm resposta e uma não tem —
e é exactamente isso que a resposta única esconderia.

| # | pergunta | resposta |
|---|---|---|
| 1 | existe fonte real de backup **aplicável ao LIVE**? | **NÃO MEDIDA** |
| 2 | sabemos restaurar **este tipo** de backup? | **SIM, e está executado** |
| 3 | o banco restaurado volta coerente e verificável? | **SIM, e está medido** |

```
BACKUP EXISTE  !=  RESTORE PROVADO
RESTORE PROVADO DE UM MECANISMO  !=  RESTORE PROVADO DO OUTRO
```

O estado do LIVE de onde esta missão parte está em
[`PREFLIGHT-LIVE-READONLY-V1.md`](PREFLIGHT-LIVE-READONLY-V1.md), que é um
**retrato datado** e continua a ser lido como tal — esta missão não o reescreve.
O plano de aplicação vive em
[`PREFLIGHT-LIVE-COLLECTION-V1.md`](PREFLIGHT-LIVE-COLLECTION-V1.md), e o
`BLOCKER = RESTORE_NOT_PROVEN` que ele nomeia é exactamente o que se ataca aqui.
O delta de know-how que sai desta missão viaja em
[`handoff/KNOW-HOW-DELTA-107-RECUPERACAO.md`](../../handoff/KNOW-HOW-DELTA-107-RECUPERACAO.md).

---

## 2 · O BACKUP DO LIVE — O QUE SE PROCUROU, E O QUE SE ACHOU

```
LIVE_BACKUP_MECHANISM   UNKNOWN
LIVE_BACKUP_STATUS      NOT_MEASURED
BACKUP_RETENTION        UNKNOWN
BACKUP_TIMESTAMP        UNKNOWN
BACKUP_SOURCE_FOR_LIVE  NOT_PROVEN
```

Não é «a rede falhou» nem «não sei se procurei». Procurou-se em três sítios, e
os três responderam:

| onde se procurou | o que se achou |
|---|---|
| credencial de gestão no ambiente | `SUPABASE_ACCESS_TOKEN` · **ausente**; `SUPABASE_MANAGEMENT_TOKEN` · **ausente** |
| segredos que a automação deste repositório usa | `SUPABASE_DB_URL`, `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, `APIFY_TOKEN_POOL`, `YOUTUBE_DATA_API_KEY` — **nenhum fala com a API de gestão** |
| workflow que **produza** backup do LIVE | **nenhum** — `pg_dump`, `pg_basebackup`, `supabase db dump`, `wal-g`, `barman` e `pgbackrest` não aparecem em workflow nenhum |
| registo datado de um restauro do LIVE | **nenhum** — e continua a não haver |

E a casa já sabia disto, em dois sítios que continuam a dizer a verdade:

- `security/security-baseline.json` → `SEC-015` = `UNKNOWN`,
  *«backup, retencao, RPO, RTO e restore nao medidos. Nao inventar numeros.»*
- `security/ACCOES-DE-ADMINISTRADOR.md` §4 → *«Medido hoje: Nada. A API de
  gestao do Supabase nao e alcancavel daqui.»*

> **«O SUPABASE TEM BACKUP» NÃO É UMA MEDIÇÃO.**
> É uma frase sobre um produto. A configuração deste projeto — se há backup
> automático, qual a retenção, se o plano tem PITR, quando foi o último —
> vive num ecrã que ninguém abriu, e continua por abrir.

### Esta medição não se afirma por variável de ambiente

`provas/recuperacao_provada_no_postgres.py` → `mede_backup_do_live()` mede os
três sítios acima **a cada corrida**, e nada no ambiente lhe pode dizer o
contrário. Se amanhã existir credencial de gestão ou um workflow que produza
backup, a resposta dela muda sozinha. Um veredito que obedecesse a quem o corre
não seria um veredito.

---

## 3 · O CORPUS DO LIVE NÃO SAIU, E NÃO IA SAIR

```
LIVE_CORPUS_EXPORTED = NO
```

Copiar produção para fora **também é uma operação de dados**, e esta missão não
tem autorização para a fazer. Não foi feito `pg_dump` do banco real, e a
bancada nunca recebeu uma linha de corpus: os bytes que ela guarda são
sintéticos e estão escritos no próprio ficheiro da prova.

A recusa não é disciplina — é executada. A trava **decompõe** a URL e exige
`hostname` exactamente local **e** nome de banco numa lista curta de permissão.
Oito endereços hostis foram testados (dois deles com a forma real de uma DSN do
Supabase, directa e por *pooler*): **nenhum passou**, nem como origem de backup
nem como destino de restauro.

---

## 4 · A BANCADA — E ELA É DESCARTÁVEL DE VERDADE

```
POSTGRES_VERSION   16.13
PG_DUMP_VERSION    16.13
CONSTRUIDA_POR     motor/cadeia_canonica.sh migrations   (o aplicador canónico,
                                                          e nenhum segundo)
MIGRATIONS_APLICADAS  29   (001–007, 009–030; a 008 confere e não cria)
CONFERENCIA_008       PASS
```

Cliente e servidor medem-se os dois. Um `pg_dump` mais velho que o servidor
recusa-se a correr, e o log diria apenas «falhou» — a prova prefere dizer
porquê.

### As sentinelas

Dados **sintéticos e identificáveis**, com relações suficientes para que
`PK` · `FK` · `UNIQUE` · `CHECK` tenham o que provar depois do restauro:

| sentinela | o que é |
|---|---|
| `RECOVERY_TEST_RUN` | a corrida que **capturou** |
| `RECOVERY_TEST_RUN_DERIV` | a corrida que **derivou** — e não é a mesma, de propósito |
| `RECOVERY_TEST_STORAGE/…` | a cópia, com o sha dos bytes sintéticos |
| `RECOVERY_TEST_RAW` | a observação, `FORWARD_IDENTIFIED`, com chave e base |
| `RECOVERY_TEST_DERIVED/…` | o derivado, ligado ao pai por `id` **e** por `sha` |
| a aresta em `participacao_na_derivacao` | a linhagem da `029` |
| o documento em `documento_estruturado` | a casa da `030` |
| a etapa `RAW` em `etapa_da_corrida` | a passagem da `028`, a nomear a observação |

`SHA_DOS_BYTES_SINTETICOS = b19cb8ebff8b91bf79b13ea87176875e4ac8749467aa7d60108af60d8f8e88de`

### A impressão — sete perguntas, e não uma

Um número só esconderia **qual** secção mudou, e saber qual é metade do
diagnóstico.

| secção | o que sela | linhas |
|---|---|---|
| `TABELAS` | as tabelas de `public` | 70 |
| `LINHAS` | a contagem das oito tabelas da Collection | 8 |
| `LEDGER` | versão, resultado e `sha256` de cada migration | 29 |
| `SENTINELAS` | os IDs sintéticos, os sha e as chaves | 8 |
| `TRAVAS` | `conname` + `contype` + definição | 56 |
| `INDICES` | `indexdef` de cada índice | 37 |
| `SEQUENCIAS` | `last_value` de cada sequência | 64 |

```
IMPRESSAO_ANTES = 041c4dee99742a229fb6d5c74696b53e94e9fc88381f3c47bd5b9b4837a6953a
```

---

## 5 · BACKUP · DESTRUIÇÃO · RESTORE

```
DISPOSABLE_BACKUP_MECHANISM   PG_DUMP  (formato custom, backup LÓGICO)
BACKUP_CREATED                YES
BACKUP_BYTES                  437693
BACKUP_INTEGRITY_CHECK        PASS   (976 entradas no índice do arquivo)

ORIGINAL_DATABASE_AVAILABLE   NO     ← o banco foi destruído de propósito
RESTORE_TARGET_EMPTY          YES    ← zero tabelas em `public` antes do restauro

RESTORE_COMMAND_EXIT          0
IMPRESSAO_DEPOIS              041c4dee99742a229fb6d5c74696b53e94e9fc88381f3c47bd5b9b4837a6953a
SECOES_DIFERENTES             NENHUMA
```

> **RESTAURAR POR CIMA DO QUE AINDA EXISTE NÃO PROVA NADA.**
> Se o original continuar de pé, uma tabela que o restauro **não** trouxe
> continua lá, e o verde é do banco antigo em vez de ser do backup. Por isso o
> banco é destruído **antes** e a prova confirma que ele desapareceu.

### O que voltou, medido por pergunta

| | |
|---|---|
| `RESTORE_SCHEMA_COMPLETE` | `PASS` |
| `RESTORE_LEDGER_COMPLETE` | `PASS` |
| `RESTORE_LEDGER_BATE_COM_O_REPO` | `SIM` — cada `sha256` do livro confere com o ficheiro em `supabase/migrations/` |
| `RESTORE_ROW_COUNTS` | `PASS` |
| `RESTORE_SENTINELS` | `PASS` |
| `RESTORE_CONSTRAINTS` | `PASS` |
| `RESTORE_PRIMARY_KEYS` | `PASS` |
| `RESTORE_FOREIGN_KEYS` | `PASS` |
| `RESTORE_UNIQUES` | `PASS` |
| `RESTORE_CHECKS` | `PASS` |
| `RESTORE_SEQUENCIAS` | `PASS` |

### E a conferência não podia ter consertado nada

```
SESSAO_SO_LEITURA_RECUSA_ESCRITA       SIM
REPAROS_MANUAIS_ANTES_DA_CONFERENCIA   0
```

A impressão do banco restaurado é lida dentro de `begin read only`, e a recusa
do servidor é **conferida** antes de se acreditar nela. Sem isto, «não houve
conserto» seria uma promessa; assim é uma medição.

```
PEDIR NAO E OBTER.
```

---

## 6 · O BANCO RESTAURADO **OPERA**

Não basta as tabelas existirem. Quatro perguntas diferentes, e um restauro pode
acertar nas três primeiras e falhar na última:

```
SCHEMA_RESTORED                        YES
DATA_RESTORED                          YES
RELATIONS_RESTORED                     YES
COLLECTION_CAN_OPERATE_AFTER_RESTORE   YES
```

| prova | resultado |
|---|---|
| a cadeia canónica corre **outra vez** sobre o banco restaurado | `EXIT=0`, **29** `SKIP … HASH=MATCH`, **0** reaplicadas |
| a conferência da `008` | `PASS` |
| a linhagem lê-se do derivado até à observação | `RECOVERY-TEST-DOC-1` |
| a corrida da aresta continua a ser a da **derivação** | `RECOVERY_TEST_RUN_DERIV` |
| `CHECK forward_identificado_exige_identidade` | **RECUSOU** |
| `PK participacao_e_unica_por_par` | **RECUSOU** |
| `FK o_pai_por_id_e_o_pai_por_sha` | **RECUSOU** |
| `UNIQUE derivacao_e_unica_por_regua` | **RECUSOU** |
| `FK etapa_nomeia_corrida_existente` | **RECUSOU** |

A segunda passagem da cadeia é a que mais diz: **29 SKIP com `HASH=MATCH` e
zero reaplicações** provam que o livro-razão voltou coerente com os ficheiros
do repositório — e que o aplicador canónico consegue operar o banco restaurado
sem tocar em nada.

> Uma trava que veio no dump mas não recusa nada é um desenho, não uma trava.
> Por isso as cinco são **mordidas**, e não apenas contadas.

---

## 7 · RED TEAM — VINTE ATAQUES, ZERO SOBREVIVENTES

```
ATTACKS = 20
SURVIVORS = 0
```

| # | ataque | como foi apanhado |
|---|---|---|
| A01 | backup inexistente | a conferência de integridade recusa ficheiro que não existe |
| A02 | backup vazio | recusa 0 bytes |
| A03 | backup truncado | arquivo cortado a 60% — `pg_restore --list` recusa |
| A04 | backup de versão PostgreSQL incompatível | o cabeçalho `PGDMP` é **mesmo** alterado para `99.15`; `pg_restore` recusa |
| A05 | schema restaura mas dados não | restauro `--schema-only` sai **0** e a impressão difere em `LEDGER,LINHAS,SENTINELAS,SEQUENCIAS` |
| A06 | dados restauram mas o ledger não | TOC filtrado: o livro volta com **0** linhas e `LEDGER` difere |
| A07 | ledger restaura com SHA divergente | `LEDGER` difere **e** 1 versão deixa de bater com o repositório |
| A08 | FK perdida | `TRAVAS` difere |
| A09 | UNIQUE perdida | `TRAVAS` e `INDICES` diferem |
| A10 | CHECK perdida | `TRAVAS` difere |
| A11 | uma sentinela sumiu | `LINHAS` e `SENTINELAS` diferem |
| A12 | um ID mudou | `SENTINELAS` difere — e `LINHAS` continua igual, que é exactamente o ponto |
| A13 | row count divergiu | `LINHAS` difere |
| A14 | restore parcial devolve exit 0 | `exit=0` **com** impressão diferente — código de saída não é prova |
| A15 | mecanismo descartável diferente do LIVE chamado de equivalente | o portão devolve `BLOCKED` com `SAME_CLASS` em `UNKNOWN` **e** em `NO` |
| A16 | backup existe mas restore nunca foi exercido | o portão devolve `BLOCKED` |
| A17 | restore exercido sobre banco não vazio | a medição de vazio distingue os dois casos, e o restauro só corre depois de ela dar SIM |
| A18 | corpus LIVE copiado sem autorização | 8 URLs hostis, **0** aceites como origem |
| A19 | restore tenta apontar para o LIVE | a trava levanta em todas as 8 |
| A20 | prova depende de conserto manual pós-restore | a conferência corre em `begin read only` e o servidor **recusa** escrita — conserto era impossível, e não apenas não-feito |

Os ataques que sabotam o banco correm numa **arena própria**, restaurada do
mesmo backup e deitada fora a seguir. Sabotar o banco restaurado de verdade
contaminaria o veredito.

---

## 8 · O VEREDITO

```
BACKUP_SOURCE_FOR_LIVE  =  NOT_PROVEN   (medido: NOT_MEASURED na origem)
RESTORE_MECHANISM       =  PROVEN       (pg_dump/pg_restore, exercido)
SAME_CLASS_RESTORE      =  UNKNOWN
DISPOSABLE_RESTORE      =  PASS
LIVE_WRITES_PERFORMED   =  0

RECOVERY_GATE           =  BLOCKED
LIVE_READY_FOR_APPLY    =  NO
BLOCKER                 =  LIVE_BACKUP_NOT_MEASURED
```

`BLOCKED` **não** é uma falha desta missão. É o resultado de a ter feito com
honestidade: o mecanismo foi provado, e o que falta é do lado do LIVE.

O portão é uma função (`portao()`), e não uma frase: `PASS` exige as cinco
condições juntas, e `SAME_CLASS_RESTORE` em `UNKNOWN` chega para o fechar. Os
ataques A15 e A16 atacam essa função directamente, e ela aguenta.

> **UM BLOQUEIO MEDIDO HONESTAMENTE NÃO É UMA FALHA DA MISSÃO.**
> **UM VERDE SEM AS CINCO PROVAS É UMA MENTIRA DA MISSÃO.**

### Porque é que `SEC-015` continua `UNKNOWN`

`security/ACCOES-DE-ADMINISTRADOR.md` diz que *«um restauro para uma base
descartavel, uma vez, datado»* transforma `SEC-015` de `UNKNOWN` em `PROVED`.
Essa frase fala de restaurar **um backup do LIVE** numa base descartável —
metade que continua por fazer, porque o backup do LIVE não foi medido.

O que se provou aqui é o **outro lado**: que a ferramenta funciona e que a casa
sabe conduzir um restauro até ao fim sem consertos. Promover `SEC-015` com esta
prova seria exactamente o ataque A15 — chamar de equivalente um mecanismo que
não se mediu. Por isso `security-baseline.json` **não foi tocado**.

---

## 9 · O QUE FALTA, E É POUCO

Um passo, e é de administrador:

**Supabase → Settings → Database → Backups.** Anotar quatro respostas —
*há backup automático? qual a retenção? o plano tem PITR? qual a data do
último?* — e escrevê-las em `SEC-015`.

Com isso, `LIVE_BACKUP_MECHANISM` deixa de ser `UNKNOWN`, e a pergunta seguinte
passa a ter forma:

- se a resposta for **backup do provedor / PITR**, então `SAME_CLASS_RESTORE`
  é `NO` para esta prova, e o que falta é exercer **esse** mecanismo (restaurar
  um snapshot do LIVE para um projeto descartável, uma vez, datado);
- se a resposta for um **dump lógico** com autorização de saída, então
  `SAME_CLASS_RESTORE` passa a `YES` e o portão fecha com o que já está aqui.

Em qualquer dos dois casos, o caminho deixa de ser uma suposição.

---

## 10 · O QUE ESTA MISSÃO NÃO FEZ

- não aplicou `028`, `029` nem `030` — nem no LIVE nem em lado nenhum que
  conte como LIVE;
- não escreveu, criou, apagou nem alterou nada no LIVE (`LIVE_WRITES = 0`);
- não exportou corpus real;
- não criou migration nova, nem tocou em contrato de identidade, Admission,
  Portal, E7, SCRAP ou Intelligence;
- não promoveu `SEC-015`.

**A aplicação pertence à próxima missão, e exige autorização explícita.**

---

## 11 · COMO CORRER ISTO OUTRA VEZ

```bash
psql "$ADMIN_URL" -c 'drop database if exists recuperacao;'
BANCO_DESCARTAVEL_URL=postgresql://postgres:descartavel@localhost:5432/recuperacao \
  python3 provas/recuperacao_provada_no_postgres.py
```

Corre sozinha em `.github/workflows/banco-descartavel.yml`, passo
`2j · o backup volta, e o banco destruido volta inteiro`.

> **UM PORTÃO QUE NÃO CORRE NÃO É UM PORTÃO.** Uma prova de recuperação que
> dependesse de alguém se lembrar dela envelheceria em silêncio, que é a única
> maneira de uma prova deixar de valer sem ninguém notar.

---

## 12 · ADDENDUM — O QUE MUDOU DEPOIS DO HARD STOP

```
ESCRITO_EM   2026-09-13, depois do fecho da missao
NAO_REABRE   nenhuma migration, nenhum toque no LIVE, nenhum merge na linha
             funcional, nenhuma escrita na linha do know-how
```

### 12.1 · A LINHA FUNCIONAL ANDOU, E A BASE DESTA MISSÃO NÃO

```
RECOVERY_BASE_HEAD                            903e1860
CURRENT_FUNCTIONAL_HEAD                       974e39a6
FUNCTIONAL_HEAD_ADVANCED_AFTER_RECOVERY_START YES
RECOVERY_SCHEMA_PROOF_INVALIDATED_BY_E7       NO
RECOVERY_REGRESSION_IS_CURRENT_FUNCTIONAL_SNAPSHOT  NO
```

`974e39a6` foi **medido localmente**, e não só recebido: `git fetch` seguido de
`git rev-parse origin/claude/raw-observation-identity-3jbwco`. O delta são
quatro commits — a integração do E7.

E a razão de a prova do schema **não** cair com ele é mais forte do que «não
traz migration nova», que foi o que a coordenação disse. Medido aqui:

| pergunta | resposta |
|---|---|
| migrations mexidas no delta | **nenhuma** |
| `motor/cadeia_canonica.sh` mexido | **não** |
| conjunto de ficheiros em `supabase/migrations/` | **idêntico** (30 ↔ 30) |
| bytes de cada migration | **idênticos**, sha a sha, nos dois lados |

```
NAO TRAZ MIGRATION NOVA  <  AS 30 SAO BYTE A BYTE AS MESMAS.
```

A segunda frase é a que fecha a pergunta: a cadeia que a bancada aplicou em
`903e1860` é, ficheiro a ficheiro, a cadeia que existe em `974e39a6`.

**A regressão é outra história, e ela envelheceu.** Os 123 alvos e o
`NEW_FAILURES = 0` do `§`ENTREGA foram medidos em `903e1860` e **não** são o
retrato da linha funcional de hoje. Um número de regressão não se herda por
cima de quatro commits que ninguém correu. Esta branch **não** foi rebasada
nem integrada — de propósito.

### 12.2 · O LIVE FOI MEDIDO POR FORA — E ISSO APERTOU O VEREDITO

```
COORDINATION_MEASURED / LOCAL_NOT_REMEASURED
```

Estes valores **não** foram remedidos aqui: esta sessão continua sem credencial
de gestão, e inventar que os viu seria pior do que não os ter.

| | medido pela coordenação |
|---|---|
| `PROJECT` | `eame-sintonia` |
| `PROJECT_REF` | `odhdwvugikjdvkapbowe` |
| `PLAN` | `PRO` |
| `LIVE_POSTGRES_ENGINE` | `17` |
| `LIVE_POSTGRES_VERSION` | `17.6.1.166` |

Da documentação oficial do Supabase (lida pela coordenação, **não** por esta
sessão): Pro tem backup automático diário com 7 dias de retenção; projetos em
`15.8.1.079` ou acima usam o processo novo, de backup **físico**; com PITR
ligado o físico substitui o diário e junta-lhe o WAL. `17.6.1.166` está acima
do corte.

Os factos vivem em
[`provas/RECUPERACAO-FACTOS-DO-LIVE.json`](../../provas/RECUPERACAO-FACTOS-DO-LIVE.json),
versionados e com proveniência ao lado — e não cravados dentro do código da
prova, onde um facto externo passa a parecer medido.

### 12.3 · A CORREÇÃO, E A LINHA QUE ELA NÃO ATRAVESSA

```
PLATFORM_BACKUP_POLICY   PROVEN      ← isto é NOVO, e é verdade
LIVE_BACKUP_MECHANISM    PROVIDER_BACKUP
LIVE_BACKUP_CLASS        PHYSICAL
BACKUP_RETENTION         7 dias de backups diários (Pro)

PITR_ENABLED             UNKNOWN
LATEST_AVAILABLE_BACKUP  UNKNOWN
LATEST_BACKUP_TIMESTAMP  UNKNOWN
LIVE_RECOVERY_EXERCISED  NO
LIVE_BACKUP_STATUS       NOT_MEASURED   ← e isto NÃO mudou
BACKUP_SOURCE_FOR_LIVE   NOT_PROVEN     ← nem isto
```

> **POLÍTICA PROVADA ≠ ARTEFATO PROVADO.**
> «O plano prevê backup diário» não é «este backup existe, e é deste instante».
> Nenhum backup concreto deste projeto foi listado, datado ou restaurado.

Promover `BACKUP_SOURCE_FOR_LIVE` porque o plano é Pro seria o mesmo erro do
`A15`, com outra roupa — e por isso passou a ter ataque próprio:

```
A21 · politica da plataforma promovida a artefato        APANHADO
      politica PROVEN e artefato NOT_MEASURED ao mesmo tempo;
      o portao devolve BLOCKED
ATTACKS = 21    SURVIVORS = 0
```

### 12.4 · A CLASSE, QUE ERA A PERGUNTA CERTA DESDE O INÍCIO

O `§8` publicou `SAME_CLASS_RESTORE = UNKNOWN` porque ninguém sabia a classe
do LIVE. Agora sabe-se, e a resposta é pior — que é o **bom** sentido de uma
medição correr:

```
LIVE_BACKUP_CLASS        PHYSICAL   (snapshot do provedor, + WAL se houver PITR)
DISPOSABLE_BACKUP_CLASS  LOGICAL    (pg_dump formato custom)
SAME_CLASS_RESTORE       NO         (era UNKNOWN)
```

A comparação do portão deixou de ser entre **nomes de ferramenta** e passou a
ser entre **classes** — que era o que `SAME_CLASS_*` sempre quis perguntar. Um
dump lógico e um snapshot físico não se restauram com as mesmas ferramentas
nem falham pelos mesmos motivos.

**O que a prova desta missão continua a valer, com o nome certo:**

```
«RECUPERACAO LOGICA INDEPENDENTE E PORTATIL DA BASE CANONICA» — PROVADA.
```

Não é, e nunca foi, a prova do mecanismo de recuperação do Supabase LIVE.

### 12.5 · O VEREDITO CORRIGIDO

```
PLATFORM_BACKUP_POLICY   PROVEN
LIVE_BACKUP_CLASS        PHYSICAL
PITR_ENABLED             UNKNOWN
LATEST_BACKUP_TIMESTAMP  UNKNOWN
DISPOSABLE_BACKUP_CLASS  LOGICAL
DISPOSABLE_RESTORE       PASS
SAME_CLASS_RESTORE       NO          ← era UNKNOWN
LIVE_RECOVERY_EXERCISED  NO
BACKUP_SOURCE_FOR_LIVE   NOT_PROVEN
RESTORE_MECHANISM        PROVEN      (da classe LÓGICA, e só dela)
LIVE_WRITES_PERFORMED    0
RECOVERY_GATE            BLOCKED
LIVE_READY_FOR_APPLY     NO
```

### 12.6 · EQUIVALÊNCIAS, PARA NÃO NASCER CAMPO A DOBRAR

O complemento nomeou campos que já tinham dono. Registados como equivalência,
e não como campo novo:

| nome no complemento | dono já existente |
|---|---|
| `DISPOSABLE_LOGICAL_RESTORE` | `DISPOSABLE_RESTORE` (= `PASS`) |
| `LATEST_AVAILABLE_BACKUP` | publicado, e igual a `LATEST_BACKUP_TIMESTAMP` enquanto os dois forem `UNKNOWN` |
| `LIVE_RECOVERY_EXERCISED = NO` | é o que sustenta `BACKUP_SOURCE_FOR_LIVE = NOT_PROVEN` |
| `SAME_CLASS_RESTORE = NO / NOT_PROVEN` | `NO` — o vocabulário deste contrato é `YES / NO / UNKNOWN`, e `NO` é o mais forte dos dois |

`PLATFORM_BACKUP_POLICY`, `LIVE_BACKUP_CLASS` e `DISPOSABLE_BACKUP_CLASS` **são**
campos novos, e nascem porque medem coisas que nenhum campo existente media —
a classe já era pressuposta por `SAME_CLASS_*` sem nunca ter sido escrita.

### 12.7 · O QUE FALTA AGORA

Mudou, e ficou mais concreto do que o `§9`:

1. **`PITR_ENABLED`** — um olhar na consola do projeto `odhdwvugikjdvkapbowe`.
   Com PITR, a janela de recuperação é outra e o `RPO` deixa de ser «até 24h».
2. **`LATEST_BACKUP_TIMESTAMP`** — listar os backups e datar o mais recente.
   É o que transforma `LIVE_BACKUP_STATUS` de `NOT_MEASURED` em medido.
3. **Exercer a classe física uma vez** — restaurar um backup do LIVE para um
   projeto **descartável**, datado. Só isso move `SAME_CLASS_RESTORE` e
   `LIVE_RECOVERY_EXERCISED`, e só então o portão pode fechar.

O passo 3 é o único que fecha o gate. Os passos 1 e 2 dizem **de onde** ele
partiria.
