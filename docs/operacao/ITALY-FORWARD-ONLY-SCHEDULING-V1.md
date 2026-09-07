# AGENDAMENTO FORWARD-ONLY — ITÁLIA V1

**Data:** 2026-09-07 · **Branch de engenharia:** `claude/italy-forward-only-scheduling-v1`
**Branch operacional:** `ops/italy-forward-only-live` · **Worktree operacional:** `C:\eame-sintonia-ops`

Só três fontes entram em operação automática — as que **desaparecem** se não forem preservadas:
`IT-T3-005` Terre dell'Etruria · `IT-T2-002` ARPAV Veneto · `IT-T2-004` SIAS Sicília.

---

## 1 · O host, medido — não inferido

| item | medido |
|---|---|
| `HOST_KIND` | **desktop pessoal do usuário**, não container. `/.dockerenv` ausente |
| `OS` | Windows 11 Pro 10.0.22000 (`MINGW64_NT-10.0-22000`), acessado por Git Bash |
| `HOSTNAME` | `Luciano` |
| `USER` | `London` · `HOME=/c/Users/London1` |
| `TIMEZONE` da máquina | **`E. South America Standard Time`** (Brasil, UTC−3) — **não** é Europe/Rome |
| `SYSTEM_UPTIME` | ligado desde **2026-09-02 02:59** (≈5 dias) |
| `SYSTEMD_AVAILABLE` | **NÃO** — é Windows |
| `CRON_AVAILABLE` | **NÃO** |
| Agendador disponível | **`schtasks` / Agendador de Tarefas do Windows** — presente |
| `HOME_PERSISTENT` | **SIM** — disco local |
| `REPO_PERSISTENT` | **SIM** — `C:\eame-sintonia` em disco local |
| `NETWORK_AVAILABLE_WITHOUT_CLAUDE_SESSION` | **SIM** — máquina própria |
| `VPN_AVAILABLE_WITHOUT_CLAUDE_SESSION` | **SIM, com ressalva** (§2) |

### `PERSISTENT_AFTER_CLAUDE_SESSION = SIM`

O Agendador de Tarefas é do sistema operacional, não da sessão do Claude. A tarefa continua
registrada e disparando depois que o Claude fechar. **Não é cron decorativo.**

### O que pode interromper — declarado, não escondido

1. **A máquina desligada ou dormindo.** É um desktop pessoal, não servidor. Mitigado com
   `StartWhenAvailable = True` (o equivalente Windows do `Persistent=true` do systemd): a
   execução perdida roda assim que a máquina volta. **Mas rodar depois não recupera um documento
   `FORWARD_ONLY` que já foi sobrescrito.**
2. **A VPN.** Ver §2.

---

## 2 · A VPN, medida

```
ProtonVPN Service     Running   StartType = Manual
ProtonVPN WireGuard   Running   StartType = Manual
Autostart             HKCU\...\Run → ProtonVPN.Launcher.exe
```

**A VPN não depende do Claude** — é aplicativo do sistema. Mas o serviço está como *Manual* e o
autostart é por **login do usuário**. Depois de um reinício, a VPN só volta quando o usuário
entra na conta — e só reconecta na Itália se o auto-connect estiver ligado no app.

**Por isso a precondição de VPN é obrigatória a cada execução**, e não uma verificação feita
uma vez. Se o egress não for `IT`:

```
RUN_STATE   = FAILED_PRECONDITION
REASON      = VPN_NOT_ITALY
SOURCE_ATTEMPTED = 0 · SOURCE_DOWNLOADS = 0 · SOURCE_NOT_MEASURED = 3

LEI:  VPN_FAILURE  ≠  SOURCE_FAILURE
```

Terre, ARPAV e SIAS **nunca** são marcadas como falhas porque a nossa VPN caiu.

---

## 3 · Por que Agendador do Windows e não GitHub Actions / Vercel Cron

Não foram usados **por não passarem no teste que a missão exige**:

| exigência | GitHub Actions / Vercel Cron |
|---|---|
| `EGRESS_COUNTRY_IT` | **NÃO** — o runner sai por datacenter dos EUA/Europa, não pela VPN italiana |
| `SOURCE_CONTRACTS_WORK` | **não provado** — toda a coleta validada até aqui foi feita do IP italiano |

A coleta provada pertence a **este** ambiente italiano. Mover para a nuvem por conveniência
invalidaria a única coisa que torna a medição confiável.

---

## 4 · O fuso — a limitação que o Windows impõe

O Agendador de Tarefas do Windows **não tem fuso por tarefa**: usa o horário local da máquina,
que aqui é o do Brasil. Fixar "15:00 local" quebraria em silêncio quando a Itália sair do
horário de verão, no fim de outubro.

**Solução:** o gatilho dispara **de hora em hora**, e quem decide é o coletor:

```
node coleta/italy_recurrent_collect.mjs --profile forward-only-live --gate-hour
```

O `--gate-hour` compara com `Europe/Rome` explicitamente (via `Intl.DateTimeFormat`), e sai
sem tocar em nenhuma fonte quando não é a hora. Isso sobrevive ao horário de verão dos dois
países, porque o fuso mora no código, não no agendador.

```
OPERATIONAL_COLLECTION_TIME  =  20:00 Europe/Rome
20:00                        ≠  SOURCE_DECLARED_PUBLICATION_TIME
```

Não sabemos a que horas essas fontes publicam. 20:00 é escolha operacional — depois do dia útil
italiano — não conhecimento sobre a fonte.

---

## 5 · A tarefa instalada

```
TaskName            SINTONIA-Italy-ForwardOnly
State               Ready
Enabled             True
Action              C:\eame-sintonia-ops\scripts\italy-forward-only-live.cmd
Repetition          PT1H  (de hora em hora)
StartWhenAvailable  True   ← execução perdida roda quando a máquina voltar
MultipleInstances   IgnoreNew  ← o agendador também recusa segunda instância
ExecutionTimeLimit  30 min
```

**Para remover:**

```bash
schtasks /Delete /TN "SINTONIA-Italy-ForwardOnly" /F
```

O `.cmd` **não contém lógica de coleta** — só aponta para o entrypoint canônico.

---

## 6 · Separação de operação e engenharia

```
C:\eame-sintonia       branch de engenharia   ← pessoas desenvolvem aqui
C:\eame-sintonia-ops   ops/italy-forward-only-live   ← o agendador escreve SÓ aqui
```

O coletor **nunca** faz `cd` no worktree de desenvolvimento e **nunca** faz `git add .`.
Ele adiciona apenas `data/collection-ledger` e `data/collection-store`.
**Nenhum merge automático** para branches de engenharia.

O worktree operacional nasceu limpo: `git status --short` vazio, sem `italia-portale/`, sem
`build/`, sem os arquivos sujos de outras missões.

---

## 7 · ARPAV: 29 zonas, e por quê

Medido antes de decidir:

```
zonas numeradas       32
zonas publicadas      29
não publicadas        17, 18, 19  → HTTP 404 com 564 bytes, consistente
custo por execução    13.373.903 bytes (~12,8 MB) para as 32 tentativas
```

`ARPAV_OPERATIONAL_ZONES = 29`. O contrato já provou que cada zona é uma versão independente
(hashes e `CreationDate` diferentes) e que as URLs são previsíveis. **Com 4 zonas não se pode
dizer "Veneto capturado".**

O 404 das zonas 17–19 é **fato da fonte**, não falha nossa.

**Crescimento:** em dia sem publicação o resultado é `SEEN_AGAIN` e **zero bytes** são guardados.
A ARPAV declara 2×/semana na temporada, então a estimativa é ~13 MB duas vezes por semana —
não por dia.

---

## 8 · Ordem obrigatória de cada execução

```
1 lock · 2 runtime · 3 timezone · 4 VPN Itália · 5 storage · 6 contratos · 7 RUN_ID
8 RAW primeiro · 9 bytes · 10 sha · 11 RAW imutável · 12 ledger · 13 normalizar
14 saúde da fonte · 15 guardas · 16 commit · 17 push · 18 provar remoto · 19 soltar lock
```

Se o parser quebrar depois do passo 11, **o RAW continua preservado**.

Uma fonte falhar **não impede** as outras duas de serem preservadas.

---

## 9 · Saúde do corredor ≠ saúde da fonte

| situação | `RUNNER_HEALTH` | `SOURCE_HEALTH` |
|---|---|---|
| VPN caiu | `FAILED` | `NOT_MEASURED` |
| push falhou | `DEGRADED_STORAGE` | pode seguir `HEALTHY` |
| site devolveu HTML no lugar de PDF | `HEALTHY` | `FAILED` |
| trava ocupada | `HEALTHY` | `NOT_MEASURED` |

---

## 10 · Mensagem automática não mente

```
ops italy forward-only: 3 healthy · 0 new · 0 changed · 31 seen again
```

Quando não houve documento novo, a mensagem diz `0 new`. Nunca "new data collected".

---

## 11 · O que NÃO foi feito

Nenhum alerta (e-mail, Slack, WhatsApp, portal). Nenhuma expansão: Campania, APOL, Puglia e
Ministero **não** foram agendados. Nenhum merge automático. Nenhum deploy.
