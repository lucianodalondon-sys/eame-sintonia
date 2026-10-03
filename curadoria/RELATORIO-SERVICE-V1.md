# CHECKPOINT — SOURCE-CURATOR-SERVICE-V1

> Entregar o checkpoint **não** encerra o serviço. Ao fechar este relatório o
> supervisor está vivo no SO e a processar.

## CAMPOS DO CHECKPOINT

```
SOURCE_CURATOR_CONTINUOUS = YES  (supervisor + fila + gatilho, vivo)
SUPERVISOR_PID            = 103316  (confirmado no SO: tasklist -> python.exe)
WORKER_STATE              = WORKING (WORKER_PID vivo; heartbeat fresco, não STALE)
DISCOVERY_ACTIVE          = ligado + gated (só corre abaixo do watermark, com intervalo)
FEEDER_ACTIVE             = YES (provado ao vivo: drena candidatas -> fila)
QUEUE_DEPTH               = 72 QUALIFY (baseline committado; a lane viva já desce)
LOW_WATERMARK             = QUEUE 10 · CANDIDATE 20 · DISCOVERY_INTERVAL 3600s
WHY                       = colchão p/ o worker não parar (QUEUE); discovery de rede
                            só quando o acervo acaba (CANDIDATE); sem rajadas (INTERVAL)
CANDIDATES_PENDING        = 61 candidatas por qualificar (ESTADO=CANDIDATA)
READY_CURRENT             = promovido pelo GATE do canário, nunca por QUALIFY
READY_LEGACY              = 18  (campo SEPARADO; NÃO tocado)
RETRY / POLICY_BLOCK / CAPABILITY_BLOCK / UNKNOWN(SEMANTIC_REVIEW)
                          = medidos ao vivo no lifecycle (ledger)
QUALIFY_IMPLEMENTADO      = YES
TAREFAS_DESBLOQUEADAS     = 19 QUALIFY (guard «sem contrato») + 1 órfã recuperada
PAINEL_DERIVA_DO_SO       = YES (LIVENESS_SOURCE = DERIVED_FROM_OS_AT_READ_TIME)
ORFA_RECUPERADA           = YES (T00135 / CAND-0244, IN_PROGRESS desde 11:11 -> PENDING)
CONTINUOUS_SOURCE_LOOP_PROVEN = YES (provar_ciclo_fonte.py — passos 2..11)
WORKER_RECOVERY_PROVEN        = YES (provar_supervisor.py — 10/10 REAL)
MUTANTES / SURVIVORS      = 10 / 0  (red_team_service.py)
REQUESTED_MODEL = OPUS · ACTUAL_MODEL = claude-opus-4-8 · FABLE_USED = NO
DETERMINISTIC_ENGINE_LLM  = ZERO (git grep só devolve nomes de branch)
COLLECTION_PRODUCTION_AUTO = NO · BIG_COLLECTION_ALLOWED = NO
INITIAL_HEAD = 1e17b38d · FINAL_HEAD = ad66039a · REMOTE_HEAD = (não empurrado; sem merge no trunk)
WORKTREE_CLEAN = SIM no commit; agora suja porque o SERVIÇO VIVO avança a lane
NEW_FAILURES = 0 · ALL_GATES_GREEN = NÃO (P9 pré-existente, ver abaixo)
```

## O QUE MEDI E CONTRADIZ O PAINEL (FASE 0)

O painel do dono descrevia um runtime que já não existia neste worktree:

| facto | painel do dono | medido por mim |
|---|---|---|
| PID 104344 | RUNNING/alive | não existe no SO |
| SUPERVISOR-STATE.json | existe, RUNNING | não existia |
| QUALIFY | 71 BLOCKED | 72 QUALIFY: 52 PENDING + 19 BLOCKED + 1 órfã |
| órfã | T00184/CAND-0175 @14:08 | **T00135/CAND-0244 @11:11** |

O defeito é o mesmo; os números e o ID da órfã diferem. Não fingi que batiam.

## OS TRÊS DEFEITOS

1. **72 QUALIFY bloqueadas** — o worker não tinha a etapa QUALIFY e o guard «sem
   contrato» barrava-a (uma candidata nova nunca tem contrato). Implementei
   QUALIFY (lê a ficha, mede o território pela regra do Atlas, aloca o SOURCE_ID
   canónico — ou UNKNOWN, sem fabricar — e reenfileira o degrau seguinte);
   corrigi o guard; desbloqueei as 19. QUALIFY **nunca** promove READY.
2. **Painel lê JSON morto** — reescrevi `ler_estado_servico` para derivar TODA a
   liveness do SO no instante da leitura (PID + heartbeat), com STALE e o delta
   em segundos à vista. IDLE ≠ STOPPED.
3. **Órfã** — o supervisor recupera órfãs no arranque; T00135 recuperada.

## GATE QUE FALHA — REPORTADO, NÃO CORRIGIDO EM SILÊNCIO

`SYSTEM_MAP_CHECK = FAIL` por **uma** prova, e ela é **PRÉ-EXISTENTE**:

```
P9_CODIGO_DECLARADO: regras/motor_de_rota.mjs (+ _test) sem peça no mapa
```

Estes `.mjs` vêm do commit 606974c3 (outra missão), estão em `regras/` e nunca
foram tocados por esta missão. Declará-los exigiria descrever arquitetura alheia
sem a reler — o AGENTS.md chama a isso mentir. `P1_SEM_DRIFT` **passa** (o mapa
foi regenerado e corresponde à árvore, incluindo os ficheiros novos); a impressão
pós-commit é IGUAL.

## EM LINGUAGEM SIMPLES (para quem não é engenheira)

**O bot está vivo?** Sim. Ele tem um número de identidade no computador (o "PID")
que é o 103316 — como a senha do caixa: chamei o número e apareceu a pessoa
certa (o programa Python). Antes o painel dizia "vivo" mostrando um número de
senha (104344) que não tinha ninguém atrás dele. Agora o painel confere no
balcão, na hora, se a pessoa está lá.

**O que ele faz agora?** Pega uma fonte nova da fila, olha o nome, decide a que
"gaveta" (território) ela pertence, dá-lhe um número de identidade e passa-a
para o passo seguinte (montar o contrato e bater à porta do site para ver se
abre). Uma coisa de cada vez.

**Quantas tarefas?** Estavam 72 fontes paradas na fila porque o bot não sabia
fazer o primeiro passo delas — como 72 cartas empilhadas sem ninguém que soubesse
abri-las. Agora sabe, e a pilha está a descer.

**Quantas candidatas esperam?** 61 pistas de fontes ainda por olhar.

**Quantas READY?** As 18 antigas ficam onde estavam, intocadas (são de outra
lane). O bot pode criar READY novas, mas só depois de bater à porta do site e a
porta abrir de verdade — nunca só por ter dado um número à fonte.

**O que acontece quando a fila acaba?** Ele **não morre**. Fica de sentinela
(IDLE). Quando a fila fica baixa, vai buscar mais candidatas ao acervo (rápido,
sem internet); se o acervo também estiver a acabar, aí sim sai à procura de
fontes novas na internet — devagar, com limite, e no máximo uma vez por hora.

**E quando o worker cai?** O supervisor (o "chefe de turno") repara que ele
caiu e chama outro na hora, sem perder a tarefa que estava a meio. Provei isto a
matar o worker de propósito: o número velho ficou morto, apareceu um número novo,
e nada se perdeu.

**Usa o Opus (o modelo caro) quando precisa de pensar?** O trabalho de rotina
(validar endereço, dar número, ler a fila) é **só código, sem nenhum modelo de
IA** — é mais barato e não erra por "achismo". O Opus fica reservado para quando
há dúvida de verdade sobre a identidade de uma fonte. Confirmei que não há
nenhum modelo de IA escondido no motor.

**Confirma que NÃO dispara a Collection?** Sim. O bot acha, testa e valida
fontes, mas **não aperta o botão** que manda coletar em produção. Esse botão
continua desligado de propósito.

## COMO ARRANCAR / PARAR / VER

Está em `curadoria/SERVICO-SOURCE-CURATOR.md`. Resumo: arrancar com
`py curadoria/supervisor.py`; parar com um ficheiro `PARAR.flag` (pedir para
parar ≠ matar); ver estado com `py curadoria/supervisor.py --estado`.
