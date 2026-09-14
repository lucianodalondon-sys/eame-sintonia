# O BACKUP DO LIVE, MEDIDO — a chave existia, e agora sabemos o que ela vê

```
MISSAO             C-SUPABASE-BACKUP-READONLY-MEASURE-V1
MEDIDO_EM          2026-09-14T02:26:28Z
RAMO_DESTA_MISSAO  claude/supabase-backup-readonly-measure-v1
BASE               99e97d9281fb4d4fc3ca7b164ec1f48c39c6cf3b
                   (claude/supabase-live-recovery-preflight-v1)
WORKFLOW_RUN_ID    34799205252   (corrida de registo)
CORRIDA_ANTERIOR   34798372262   (02:11:39Z — mesmos numeros)
LIVE_READS         2      (um GET por corrida, a Management API)
LIVE_WRITES        0
LIVE_DDL           0
```

> Esta missão mede. Não restaura, não cria projeto, não aplica migration,
> não toca no dev, não gasta.

---

## 1 · EM PORTUGUÊS FÁCIL

**1. O token funcionou?** **Sim.** `HTTP 200`. O *scoped token* limitado a
`Database → Backups → Read` foi **suficiente** — nenhum `403`, nenhum pedido
de mais permissão.

**2. O projeto tem backups reais?** **Sim.** Não é política, não é
documentação, não é o plano: são sete backups listados pela API, cada um com
`id`, `status` e data.

**3. Quantos?** **Sete.** Todos `COMPLETED`. Todos **físicos**.

**4. Qual o mais recente?** **2026-09-13 03:05:36 UTC** — tinha **23,3 horas**
na hora da medição.

**5. Qual o mais antigo?** **2026-09-07 03:07:43 UTC**.

**6. Qual a retenção observada?** **Sete backups a cobrir 6,00 dias** entre o
mais antigo e o mais recente. Bate com os 7 dias do plano Pro — mas o que
está **medido** é a janela visível hoje, e não a política.

**7. PITR está ligado?** **NÃO.** E agora é `NO` **medido**, não `UNKNOWN`: a
API devolveu o campo `pitr_enabled` e ele veio `false`. A diferença importa —
campo ausente teria ficado `UNKNOWN`.

**8. Podemos restaurar para um novo projeto no próximo passo?** **A fonte
existe** — sete backups físicos, dentro da janela. Se o botão corre, **não
foi medido**: listar backup não é provar restauro.

**9. Isso exigirá custo?** O clone espelha o *compute* da origem e o valor
aparece no ecrã **antes** de confirmar. **Ver o preço custa zero.** O PITR,
que custava 100 USD/mês, **continua a não ser preciso**.

**10. Tocámos no banco real?** **Não.** Zero SQL, zero conexão PostgreSQL,
zero `service_role`. Um `GET` a uma API de metadados.

**11. Restaurámos alguma coisa?** **Não.** `SAME_PLATFORM_RESTORE = NOT_RUN`.

**12. Prontos para aplicar migrations?** **Não — e de propósito.** A lei em
vigor exige o restauro executado pela plataforma, e ele não correu. Esta
missão serviu para **tirar `UNKNOWN`**, não para mexer no portão.

---

## 2 · A MEDIÇÃO, COMO A API A DEVOLVEU

```
HTTP_STATUS                 200
MANAGEMENT_TOKEN_WORKED     YES
BACKUPS_VISIBLE             YES
BACKUP_COUNT                7
BACKUP_TYPES                ['PHYSICAL']
LATEST_BACKUP_TIMESTAMP     2026-09-13T03:05:36.879+00:00
OLDEST_BACKUP_TIMESTAMP     2026-09-07T03:07:43.374+00:00
BACKUP_RETENTION_OBSERVED   6,00 dias entre o mais antigo e o mais recente
PHYSICAL_BACKUP_OBSERVED    YES
WALG_ENABLED                true
REGION_OBSERVED             eu-west-1
PITR_OBSERVED               YES     (o campo veio na resposta)
PITR_ENABLED                NO      (e o valor dele era false)
BACKUP_SCHEDULE             UNKNOWN (nao ha rota read-only que o devolva)
RESTORE_SOURCE_AVAILABLE    YES
HORAS_SUSPEITAS             []      (nenhum carimbo futuro nem invalido)
CAMPOS_IGNORADOS            []      (a API nao trouxe campo fora da lista branca)
```

Os sete, como a API os listou:

| `id` | `inserted_at` (UTC) | `status` | físico |
|---|---|---|---|
| 1659467399 | 2026-09-13 03:05:36 | `COMPLETED` | sim |
| 1649662801 | 2026-09-12 03:07:35 | `COMPLETED` | sim |
| 1639785447 | 2026-09-11 03:07:01 | `COMPLETED` | sim |
| 1629860455 | 2026-09-10 03:07:49 | `COMPLETED` | sim |
| 1619912022 | 2026-09-09 03:05:14 | `COMPLETED` | sim |
| 1610002858 | 2026-09-08 03:08:54 | `COMPLETED` | sim |
| 1600007469 | 2026-09-07 03:07:43 | `COMPLETED` | sim |

### A cadência é OBSERVADA, e não lida de um agendamento

`BACKUP_SCHEDULE` fica `UNKNOWN` porque **não existe endpoint read-only** que
devolva o agendamento — e não por `403`, e não por falha. Pedir mais escopo
não resolveria.

O que existe é aritmética sobre os sete carimbos acima, e essa diz-se como o
que é:

```
seis intervalos:  24,020 · 23,939 · 24,043 · 23,987 · 24,009 · 23,967  horas
hora do dia:      03:05 a 03:08 UTC
```

> **CADENCIA OBSERVADA != AGENDAMENTO DECLARADO.** Seis intervalos de ~24h
> mostram um backup diário a acontecer. Não provam que alguém o agendou
> assim, nem que continuará.

---

## 3 · O QUE MUDA NO RUNBOOK — e é a linha que custa dados

O `§3` do runbook dizia: *«enquanto `PITR_ENABLED` não for medido, assuma que
se perde até um dia de escritas»*. Era uma **suposição prudente**.

Agora é um **facto medido**:

```
PITR_ENABLED = NO   (medido, 2026-09-14, campo pitr_enabled = false)
```

```
RPO REAL DESTE PROJETO = ATE ~24 HORAS.
```

E há uma precisão que a média esconde: o backup é das **~03:07 UTC**. Uma
perda às 02:00 UTC custa ~23 horas de escritas; uma perda às 04:00 UTC custa
~1 hora. **O RPO não é uniforme ao longo do dia.**

> A armadilha ao contrário continua de pé e agora é relevante: ligar PITR
> **desliga** o backup diário. Não são duas redes empilhadas.

---

## 4 · O QUE ISTO **NÃO** PROVA

Esta é a secção que impede a missão de se sobrevalorizar.

```
RESTORE_SOURCE_AVAILABLE = YES   significa: existe uma FONTE listada.
                                 NAO significa que um restauro corra,
                                 nem que corra neste projeto,
                                 nem que o resultado sirva.
```

```
BACKUP LISTADO != RESTAURO PROVADO.
SETE BACKUPS FISICOS != O BOTAO «RESTORE TO A NEW PROJECT» EXISTE AQUI.
`COMPLETED` NA API   != OS BYTES LEEM-SE.
```

`SAME_PLATFORM_RESTORE` continua `NOT_RUN` **por construção**: esta missão
não restaurou nada, e nenhum número acima o promove.

E o nome do projeto **não foi medido**: vive em `GET /v1/projects`, que exige
escopo de projeto e não de backups. Não foi chamado — esta missão não amplia
escopo por conveniência. O `project_ref` usado é o canónico, e é o único
identificador que esta medição afirma.

---

## 5 · A PORTA, E O QUE ELA NÃO PODE FAZER

`.github/workflows/supabase-backup-readonly.yml` ·
`provas/backup_do_live_medido.py`

```
METODOS_HTTP_USADOS   ['GET']          TOKEN_EM_ARGV        NAO
ESCRITAS              0                TOKEN_EM_FICHEIRO    NAO
DDL                   0                TOKEN_EM_URL         NAO
SQL_NO_LIVE           0                ECHO_DO_TOKEN        NAO
RESTAUROS             0                PERMISSOES           contents: read
```

Não recebe `SUPABASE_SECRET_KEY` nem `SUPABASE_DB_URL`, não chama
`cadeia_canonica.sh`, não abre conexão PostgreSQL. `restore`, `pause`,
`restart` e `create project` são todos `POST`, e `so_get()` fixa
`method="GET"` como única porta de rede do ficheiro. O teste
`NenhumaOutraPortaGanhouPoder` confirma que o conjunto de escritores não
cresceu.

### Por que o portão é um passo separado

O passo que mede sai com `0` sempre que a **medição** aconteceu — e um `401`
é uma medição, com uma causa que vale a pena ler. O passo `4` é que reprova
o job quando o token não leu.

```
JOB_STATUS  = a medicao correu.
HTTP_STATUS = o que ela mediu.
Colapsar os dois e exactamente o que produz «nao funciona».
```

### O `workflow_dispatch` não chegou a disparar, e isso mediu-se

A API de dispatch devolveu `404`. Não era permissão nem atraso: a lista de
workflows do repositório devolveu **22 nomes, todos com `blob/main/`**, e
este não estava lá.

```
workflow_dispatch SO EXISTE PARA FICHEIROS QUE JA VIVEM NO RAMO POR OMISSAO.
```

Fazer merge para `main` só para conseguir disparar seria trocar um problema
de execução por uma alteração de linha funcional sem decisão de gente. O
`push` com `paths` estreito corre a versão **do ramo** — que é a versão que
esta missão precisava de medir — e é o padrão que `supabase-conexao.yml` já
usa. O `workflow_dispatch` fica, para o dia em que o ficheiro chegar a `main`.

---

## 6 · DUAS COISAS QUE O PRÓPRIO CÓDIGO ME APANHOU

### 6.1 · O varredor de vazamento reprovou a prosa que o descreve

A primeira versão de `sem_vazamento()` procurava as **palavras** `sbp_`,
`Bearer` e `Authorization:`. Reprovou o artefacto — e o que lá estava era o
**texto do red team**, que nomeia esses padrões para explicar que os procura.
Nenhum segredo.

```
NOME DO PADRAO != VALOR DO PADRAO.
```

Procura-se agora a **forma** de uma credencial (prefixo mais comprimento
real). Falar de `sbp_` passa; carregar um `sbp_` com corpo não passa.

### 6.2 · Um varredor que nunca pode ficar vermelho é um enfeite

Por isso `autoteste_do_varredor()` alimenta-o com seis iscas falsas e três
textos legítimos **antes** de ele julgar seja o que for. Esse autoteste
apanhou **dois buracos reais** no próprio varredor, ambos no mesmo sítio: o
cabeçalho `Authorization: Bearer <x>` escapava porque `Bearer` tem seis
caracteres e o padrão exigia oito colados aos dois pontos.

### 6.3 · E uma terceira, no shell

```
python3 script | tee   ->  devolve o estado do TEE, nao o do script.
```

O shell por omissão do Actions é `bash -e {0}` — **sem `pipefail`**. Sem a
linha `set -o pipefail`, um script que abortasse por vazamento detectado
daria o passo por **verde**.

---

## 7 · RED TEAM

```
RED_TEAM_ATTACKS    22
RED_TEAM_SURVIVORS  0
```

Os ataques correm **dentro** da prova, contra os valores medidos, e o script
sai com código `1` se algum sobreviver. Os que mais trabalham nesta corrida:

| # | ataque | como foi apanhado |
|---|---|---|
| `A03`–`A05` | `401`, `403` ou `404` chamados de «sem backup» | só um `200` pode escrever `BACKUPS_VISIBLE`; o resto fica `NOT_MEASURED` com a causa noutro campo |
| `A06` | resposta vazia tratada como erro | `200` com lista vazia **é** medição: escreve `BACKUPS_VISIBLE=NO` |
| `A07` | backup diário tratado como PITR | `PITR_ENABLED` só se escreve a partir de `pitr_enabled`; sete backups não lhe tocam |
| `A08` | `PITR UNKNOWN` tratado como `NO` | campo ausente → `UNKNOWN`. Só um `false` explícito vira `NO` — e foi isso que aconteceu |
| `A09` | backup listado tratado como restauro provado | `SAME_PLATFORM_RESTORE` é `NOT_RUN` por construção |
| `A10`/`A11` | carimbo futuro ou inválido aceite | sai do cálculo e entra em `HORAS_SUSPEITAS`; a soma tem de bater com `BACKUP_COUNT` |
| `A13` | token a vazar no artefacto | `§6.1` — e o varredor prova-se a si próprio antes de julgar |
| `A15`/`A16` | projeto dev ou `ref` errado | o `ref` é constante e confere-se contra o do dev antes de gravar |
| `A19` | documentação tratada como resultado da API | esta prova **não carrega documentação nenhuma**: todo campo vem do corpo da resposta ou fica `UNKNOWN` |
| `A20` | artefacto antigo tratado como medição atual | `MEDIDO_EM` é gravado a cada corrida; e o artefacto commitado foi **descarregado da corrida**, com `sha256` conferido contra o digest que o GitHub publicou |

---

## 8 · VEREDITOS

```
LIVE_BACKUP_PREFLIGHT       = PASS
BACKUPS_VISIBLE             = YES
LATEST_BACKUP_TIMESTAMP     = 2026-09-13T03:05:36.879+00:00
OLDEST_BACKUP_TIMESTAMP     = 2026-09-07T03:07:43.374+00:00
PITR_ENABLED                = NO
BACKUP_RETENTION_OBSERVED   = 7 backups fisicos a cobrir 6,00 dias
MANAGEMENT_TOKEN_WORKED     = YES
SAME_PLATFORM_RESTORE       = NOT_RUN
READY_FOR_LIVE_APPLY        = NO
LIVE_WRITES                 = 0
LIVE_DDL                    = 0
REAL_COLLECTION             = 0
```

### A medição correu duas vezes, e isso não foi desperdício

| | `34798372262` | `34799205252` |
|---|---|---|
| às | 02:11:39Z | 02:26:28Z |
| `HTTP_STATUS` | 200 | 200 |
| `BACKUP_COUNT` | 7 | 7 |
| `LATEST` | 2026-09-13 03:05:36 | 2026-09-13 03:05:36 |
| `OLDEST` | 2026-09-07 03:07:43 | 2026-09-07 03:07:43 |
| `PITR_ENABLED` | NO | NO |

A segunda correu porque o *commit* seguinte tocou o script, e não para
insistir. Serve na mesma para duas coisas: os números **não são acaso de uma
chamada**, e o artefacto commitado passa a ser produto do script **tal como
está commitado** — e não de uma versão que já não existe.

> O artefacto em `provas/` foi **descarregado da corrida** e o seu `sha256`
> confere com o digest que o GitHub publicou
> (`62122ebb…`). Não foi regenerado localmente. Ver `A20`.

`PASS` e não `PARTIAL`: os cinco campos críticos do portão
(`BACKUPS_VISIBLE`, `LATEST_BACKUP_TIMESTAMP`, `BACKUP_RETENTION_OBSERVED`,
`PITR_ENABLED`, `RESTORE_SOURCE_AVAILABLE`) estão **todos** medidos.

`READY_FOR_LIVE_APPLY` continua `NO`, e **não por falta de informação**:

```
MEDIR REMOVE UNKNOWN. NAO RELAXA PORTAO.
```

---

## 9 · PRÓXIMO PASSO MÍNIMO

```
1. decidir, com gente, se se executa o «Restore to a New Project»
   a partir do backup 1659467399 (ou do que for o mais recente nesse dia)
   -> e o unico passo que move SAME_PLATFORM_RESTORE de NOT_RUN
   -> o custo aparece no ecra ANTES de confirmar; VER custa zero
   -> NAO exige PITR

2. VERIFY pela impressao de provas/recuperacao_fisica_provada_no_postgres.py

3. DELETE_DISPOSABLE
```

O passo `1` exige **autorização explícita do coordenador e custo aceite por
escrito**. Esta missão não o dá, não o pede e não o prepara.

### Precisamos de ampliar permissão?

**Não para isto.** O *scoped token* de `Backups Read` respondeu a todas as
perguntas desta missão com `200`. Ampliar escopo só se torna pergunta se
alguém quiser medir `PROJECT_STATUS`, `PLAN` ou o **nome** do projeto — e
nenhuma dessas era o bloqueio.

---

## 10 · O QUE ESTA MISSÃO NÃO FEZ

- não restaurou nada, nem in-place nem para projeto novo;
- não criou projeto, *branch* Supabase nem add-on;
- não pagou nada, e não autorizou pagamento;
- não aplicou `028`, `029`, `030` nem `031`;
- não abriu conexão PostgreSQL, não correu SQL, não usou `service_role`;
- não tocou no projeto dev (`xhqebdweltytnghiavew`);
- não coletou, não correu canário, não tocou no Portal;
- não fez merge para lado nenhum.
