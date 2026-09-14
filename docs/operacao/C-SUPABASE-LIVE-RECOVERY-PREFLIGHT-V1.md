# PREFLIGHT DE RECUPERAÇÃO DO LIVE — o que se mediu sem a chave

```
MISSAO             C-SUPABASE-LIVE-RECOVERY-PREFLIGHT-V1
MEDIDO_EM          2026-09-14
RAMO_DESTA_MISSAO  claude/supabase-live-recovery-preflight-v1
BASE               7066a9202f5598d12963130feb2f84fa2fee24f7
                   (claude/restore-proof-before-live-v2 — que contem a linha
                    funcional inteira mais os quatro artefactos de recuperacao)
LIVE_READS         2      (GET sem credencial, declarados no §10)
LIVE_WRITES        0
LIVE_DDL           0
```

> Esta missão mede. Não aplica migration, não restaura, não cria projeto,
> não gasta.

---

## 1 · EM PORTUGUÊS FÁCIL

**1. O banco LIVE tem backup?** **Não sabemos deste projeto.** A plataforma
faz backup diário em plano Pro — isso é uma frase sobre o produto. Se está
ligado *aqui*, ninguém viu.

**2. Qual é o backup mais recente?** **Não medido.** Nenhum backup deste
projeto foi listado nem datado.

**3. Tem PITR?** **Não medido — e provavelmente não.** Descoberta desta
missão: **PITR é um add-on pago** (100 USD/mês por 7 dias), não um recurso
do plano. Ninguém o comprou que se saiba.

**4. Conseguimos mandar restaurar pela própria plataforma?** A plataforma
tem o botão — **«Restore to a New Project»**. Se *este* projeto o mostra,
não foi medido.

**5. Temos acesso para isso?** **Não.** Zero credenciais nesta sessão. Mas o
que falta é a **chave**, não o recurso: a API de gestão responde `401`, e
não `404`.

**6. Precisamos pagar para provar?** **Menos do que se pensava.** O
«Restore to a New Project» funciona com o **backup diário** — **não exige
PITR**. O clone é cobrado pelo *compute* que espelha da origem, e o valor
**aparece no ecrã antes de confirmar**. Ver o preço custa **zero**.

**7. O projeto dev serve para teste?** **UNKNOWN.** Ele responde, e é tudo o
que se sabe. Não foi tocado.

**8. O LIVE está em qual migration?** **Não medido hoje.** O retrato datado
diz `001`–`007` e `009`–`027`, mas um retrato não é uma medição.

**9. Faltam 028, 029 e 030?** Do lado do LIVE, não medido. No Git elas
existem, e **aplicam-se todas** sobre o estado `027`.

**10. Podemos aplicar 031 direto?** Tecnicamente **a 031 aplica-se sobre a
027 sem as três** — medido a executar, não a adivinhar. **Mas não se deve**:
o aplicador canónico tem uma ordem só, e um livro-razão com buraco é drift.

**11. O que falta exactamente?** **Uma coisa, e é grátis:** um token de
leitura, e um `GET` aos backups.

**12. Prontos para aplicar?** **Não.**

---

## 2 · A DESCOBERTA QUE MUDA A CONTA

A `C-RESTORE-PROOF-BEFORE-LIVE-V2` fechou a dizer que provar a plataforma
exigiria «um projeto Supabase descartável em plano Pro, ~25 USD/mês» — e foi
honesta a marcar que **não tinha lido os preços**. Esta missão leu-os.

| o que se presumia | o que está medido |
|---|---|
| Pro é ~25 USD/mês **por projeto** | 25 USD/mês **por ORGANIZAÇÃO** — e ela já é Pro |
| é preciso um **projeto novo em Pro** | o **«Restore to a New Project»** cria o clone dentro da organização que já existe |
| provar a plataforma implica **PITR** | **falso** — funciona com o **backup diário físico** |

```
O PITR NAO E PRE-REQUISITO PARA PROVAR A PLATAFORMA.
```

Isto tira **100 USD/mês** do caminho crítico. O custo que resta é o *compute*
do clone, que espelha o da origem — e que a consola mostra **antes** de
confirmar.

---

## 3 · O ALCANCE DESTA SESSÃO — medido, e é a metade que faltava

```
MANAGEMENT_CREDENTIAL_AVAILABLE   NO
MANAGEMENT_READ_CAPABILITY        NO
SUPABASE_ACCESS_TOKEN             AUSENTE
SUPABASE_MANAGEMENT_TOKEN         AUSENTE
SUPABASE_DB_URL                   AUSENTE
```

Mas a parte que importa, e que nenhuma missão anterior tinha separado:

```
MANAGEMENT_API_ALCANCAVEL     SIM
MANAGEMENT_API_RESPOSTA       401
ENDPOINT_DE_BACKUPS_EXISTE    SIM (401, e nao 404)
```

> **CREDENCIAL AUSENTE NÃO É RECURSO AUSENTE.**
> `401` prova que a rota existe e que a rede lá chega. Se fosse `404`, o
> problema era outro; se fosse *timeout*, era outro ainda. A distinção é a
> diferença entre «falta comprar» e «falta pedir».

### A credencial exacta que falta

```
Supabase Personal Access Token — SO LEITURA
  token de granularidade fina  ->  permissao `backups_read`
  OAuth                        ->  escopo `database:read`
```

Com ela, **um** pedido responde a **todo** o `§5` desta missão:

```
GET https://api.supabase.com/v1/projects/{ref}/database/backups
  -> region · walg_enabled · pitr_enabled
  -> backups[] { id, is_physical_backup, status, inserted_at }
  -> physical_backup_data { earliest_..._unix, latest_..._unix }
```

`walg_enabled` responde «há backup físico ligado?». `pitr_enabled` responde
«há PITR?». `inserted_at` **data** o backup mais recente. `earliest`/`latest`
dão a **janela de retenção real**. Nenhum deles escreve nada.

---

## 4 · OS PROJETOS — o que se mediu sem chave

```
                              LIVE                    DEV
PROJECT_REF                   odhdwvugikjdvkapbowe    xhqebdweltytnghiavew
DNS_RESOLVE                   SIM                     SIM
GATEWAY_HTTP                  401                     401
REF_ECOADO_PELO_GATEWAY       odhdwvugikjdvkapbowe    xhqebdweltytnghiavew
REF_CONFERE                   SIM                     SIM
PROJETO_RESPONDE              SIM                     SIM
```

O gateway **devolve o `ref` que serviu**. Isso mata o ataque «project ref
errado» sem custar nada, e entrou no runbook como conferência de rotina.

E tudo o resto continua por medir, com estes nomes:

```
PROJECT_STATUS · REGION · POSTGRES_MAJOR · POSTGRES_VERSION
ORGANIZATION · PLAN                                  ->  NOT_MEASURED
```

> A região histórica é `eu-west-1` e a versão histórica é `17.6.1.166`. São
> **históricas**, e ficam assim. Um backup **físico** não atravessa *major*
> nenhum — adivinhar a versão seria o pior sítio para adivinhar.

### O projeto dev

```
DEV_PROJECT_CANDIDATE = UNKNOWN
ESCRITAS_NO_DEV       = 0
```

Ele responde, e é tudo. Se é descartável, de quem é, o que tem dentro e se
alguém depende dele — nada disso foi medido, e **nenhuma dessas perguntas se
responde sem gente**. Não foi tocado, resetado nem migrado.

---

## 5 · BACKUP E PITR DESTE PROJETO

```
BACKUP_FEATURE_AVAILABLE                NOT_MEASURED
BACKUP_ENABLED                          NOT_MEASURED
LATEST_BACKUP_TIMESTAMP                 NOT_MEASURED
OLDEST_AVAILABLE_BACKUP                 NOT_MEASURED
BACKUP_RETENTION                        NOT_MEASURED
WALG_ENABLED                            NOT_MEASURED
PITR_AVAILABLE                          NOT_MEASURED
PITR_ENABLED                            NOT_MEASURED
PITR_RETENTION                          NOT_MEASURED
RESTORE_UI_OR_API_AVAILABLE             NOT_MEASURED
RESTORE_TO_SEPARATE_PROJECT_SUPPORTED   NOT_MEASURED
RESTORE_IN_PLACE_SUPPORTED              NOT_MEASURED
```

**Doze campos, doze `NOT_MEASURED`.** Nenhum foi inferido do plano, da
versão ou da documentação — e é por isso que `LIVE_BACKUP_PREFLIGHT` é
`BLOCKED` e não `PARTIAL`.

---

## 6 · A DOCUMENTAÇÃO — noutro campo, de propósito

Lida em 2026-09-14. Vive numa estrutura **separada** da medição, porque um
facto do fornecedor cravado no meio de uma medição passa a parecer medido.

| | |
|---|---|
| backup diário | Pro **7 dias** · Team 14 · Enterprise até 30 |
| backup **físico** a partir de | PostgreSQL `15.8.1.079` |
| PITR | **add-on PAGO**. Até ao segundo, RPO ~2 min. **Ligar PITR DESLIGA o backup diário** |
| «Restore to a New Project» | funciona com **backup diário físico**, **não exige PITR**. Planos pagos com backups físicos. Clone fica na **mesma região**. **Um clone não pode ser origem de outro clone**. Custo mostrado **antes** de confirmar |

### Custo, citado e não inventado

```
PRO                    25 USD/mes por ORGANIZACAO
PITR 7 dias           100 USD/mes
PITR 14 dias          200 USD/mes
PITR 28 dias          DISCREPANCIA ENTRE DUAS PAGINAS OFICIAIS:
                      a de backups diz 0,55 USD/h (~400 USD/mes);
                      a de precos diz 300 USD/mes.   NAO RESOLVIDO.
SMALL COMPUTE ADD-ON   15 USD/mes
PITR EXIGE COMPUTE?    a pagina de backups diz que sim; a de precos
                       nao confirma.                 NAO RESOLVIDO.
```

> Duas páginas oficiais do mesmo fornecedor discordam. Escolher a mais
> barata seria optimismo e escolher a mais cara seria teatro. **Fica
> registada como divergência**, para ser resolvida no ecrã de compra — que
> é o único sítio onde o preço é vinculativo.

---

## 7 · A CADEIA ATÉ À 031 — medida a EXECUTAR

`provas/preflight_da_cadeia_ate_031.py` constrói o estado `027` num
PostgreSQL 17 descartável e tenta lá dentro cada migration futura, numa
transacção **sempre desfeita**.

```
CADEIA_ATE_027        exit=0 · 26 no livro-razao · ultima=027 · 008 PASS
```

### A pergunta que ninguém tinha medido

```
A_031_SOBRE_A_027_SEM_AS_TRES     PASS
A_031_DEPENDE_DE_028_029_030      NAO
```

**A 031 não depende da 028, da 029 nem da 030.** Ela referencia
`collection_run` e `raw_asset` — e **as duas nascem na `001`**. As três do
meio mexem em `etapa_da_corrida`, `participacao_na_derivacao` e
`documento_estruturado`, e a 031 **não usa nenhuma delas**.

```
NUMERO MAIOR NAO E DEPENDENCIA.
```

Isto confirma, a executar, o que a `V2` já tinha lido no ficheiro — e evita
o erro inverso: inventar um *blocker* de dependência que não existe.

### E mesmo assim não se salta

```
APLICAR_031_SOZINHA_E_PERMITIDO   NAO
```

Não por dependência — por **contrato do aplicador**. `cadeia_canonica.sh`
aplica tudo o que está na pasta, por ordem numérica, e um livro-razão com
buraco é drift por construção.

```
NAO HA DEPENDENCIA, E CONTINUA A NAO SE SALTAR.
As duas frases sao verdade ao mesmo tempo, e confundi-las erra nos dois sentidos.
```

### As pré-condições, uma a uma

```
PRECONDITION_028   PASS        PRECONDITION_030   PASS
PRECONDITION_029   PASS        PRECONDITION_031   PASS
```

```
CADEIA_COMPLETA   028 PASS · 029 PASS · 030 PASS · 031 PASS
                  livro-razao = 30 · ultima = 031 · sala_de_espera existe
ENSAIOS_NAO_DEIXARAM_RASTO   SIM   (livro-razao continuou em 26)
```

> ⚠️ **Isto mede o estado DECLARADO em `027`, e não o LIVE.**
> `LIVE_MIGRATIONS_APPLIED` continua `NOT_MEASURED`.

---

## 8 · A 031, REVALIDADA SEM SER ALTERADA

```
SHA          9414b4f7becd81382512ce2af5b5a28f334aa70b6cea127bdb6ff8c52eb306e3
REF          origin/claude/sala-persistente-preflight-real-v1
REFERENCIA   collection_run · raw_asset   (e mais nada)
TRAVAS       10        INDICES  4        SO_CRIA  SIM
MIGRATION_031_DEFECT = NO
```

### O caminho para a frente deixou de ser promessa

```
FORWARD_RECOVERY_031_EXECUTADO   SIM
DEVOLVEU_O_ESTADO_030            SIM
LEDGER_DEPOIS                    030
```

`drop table` mais uma linha do livro-razão, **executado** contra o banco
descartável: o estado voltou exactamente ao da `030`. **Rollback não é
restore**, e este é rollback — barato, porque a 031 só cria.

### ⚠️ E A 031 NÃO ESTÁ NA LINHA FUNCIONAL

```
031_NA_LINHA_FUNCIONAL = NAO
```

Ela vive **só** em `claude/sala-persistente-preflight-real-v1`. Antes de
qualquer aplicação, alguém tem de decidir a integração — e isso é uma
decisão de gente, não um passo de runbook.

---

## 9 · O MECANISMO REAL, ESCOLHIDO COM EVIDÊNCIA

```
LIVE_RECOVERY_MECHANISM = SUPABASE_BACKUP_RESTORE
```

Um só, e não dois. É o único que a plataforma oferece **sem add-on pago** e
que **devolve dados**: backup diário físico, restaurado pela consola,
preferencialmente para um projeto novo.

`SUPABASE_PITR` seria mais fino — e **não** está medido como ligado, além de
ser pago. `LOGICAL_BACKUP` não é o plano desta casa. Escolher dois
mecanismos «principais» seria não escolher nenhum.

> **A consequência operacional tem de ser dita ao coordenador:** enquanto
> `PITR_ENABLED` não for medido, **assuma perda de até 24 horas** de
> escritas num restauro. Está escrito no `§3` do runbook.

---

## 10 · AS DUAS LEITURAS DO LIVE, DECLARADAS

```
LIVE_READS = 2 · LIVE_WRITES = 0 · LIVE_DDL = 0
```

Dois `GET` ao gateway público (LIVE e DEV), **sem `apikey` e sem token**,
que devolveram `401`. Nenhum dado foi lido: o que se mediu foi que o projeto
responde e que o `ref` bate.

> Contam-se na mesma. **Uma leitura não declarada é uma leitura escondida**,
> e o número existe para ser auditável, não para ser bonito.

---

## 11 · RED TEAM

```
RED_TEAM_ATTACKS    22
RED_TEAM_SURVIVORS  0
```

Os quatro que mais trabalham:

| # | ataque | como foi apanhado |
|---|---|---|
| `A06` | credencial ausente tratada como recurso ausente | a API responde `401`, e não `404` nem *timeout* |
| `A08` | 031 aplicada a saltar 028-030 | medido que **não há dependência** — e o portão recusa **na mesma**, pelo contrato do aplicador |
| `A09` | número tratado como dependência sem medir conteúdo | a 031 foi **executada** sobre o estado `027` |
| `A20` | custo inventado | preços citados da fonte, divergência registada como divergência, e o custo do clone é `UNKNOWN` |

E o que guarda a porta desta missão:

```
A22 · a classe fisica ja provada usada para dispensar a plataforma   APANHADO
      a V2 provou a CLASSE; o portao continua a exigir a PLATAFORMA
```

---

## 12 · VEREDITOS

```
LIVE_BACKUP_PREFLIGHT     = BLOCKED
LIVE_RECOVERY_CAPABILITY  = NOT_MEASURED
SAME_PLATFORM_RESTORE     = NOT_RUN
MIGRATION_CHAIN_028_031   = PASS
MIGRATION_031_DEFECT      = NO
READY_FOR_LIVE_APPLY      = NO
```

`BLOCKED` e não `PARTIAL`: o portão exige que **algum** campo crítico de
backup esteja medido, e **nenhum** está. Chamar-lhe `PARTIAL` porque se
mediu DNS e um `401` seria contar o alcance como se fosse o resultado.

### `SAME_PLATFORM_RESTORE_NEXT_ACTION`

```
1. obter Personal Access Token de LEITURA
   GET /v1/projects/odhdwvugikjdvkapbowe/database/backups
   -> preenche os 12 campos do §5. CUSTO ZERO. NAO ESCREVE NADA.

2. so entao decidir, com numeros no ecra:
   RESTORE_EXISTING_BACKUP_TO_NEW_PROJECT   (nao exige PITR)

3. VERIFY
   a impressao de provas/recuperacao_fisica_provada_no_postgres.py

4. DELETE_DISPOSABLE
```

O passo **1** é o único que esta casa pode dar já, e é o que transforma
`LIVE_BACKUP_PREFLIGHT` de `BLOCKED` em medido. Os passos 2–4 exigem
autorização explícita do coordenador e **custo aceite por escrito**.

---

## 13 · O QUE ESTA MISSÃO NÃO FEZ

- não aplicou `028`, `029`, `030` nem `031`;
- não escreveu no LIVE (`LIVE_WRITES = 0`, `LIVE_DDL = 0`);
- não restaurou nada;
- não criou projeto, *branch* Supabase, nem add-on;
- não tocou no projeto dev;
- não alterou a `031`;
- não coletou, não correu canário, não tocou no Portal;
- não fez merge para lado nenhum.
