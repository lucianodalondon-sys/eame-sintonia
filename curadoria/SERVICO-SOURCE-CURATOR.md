# O SOURCE CURATOR COMO SERVIÇO CONTÍNUO

> Ordem do dono (missão SOURCE-CURATOR-SERVICE-V1): o Source Curator passa a
> **serviço contínuo**, não a missão de Claude. «A fila acabou» não é motivo
> para parar.

O que fica vivo é **SUPERVISOR + FILA + GATILHO**. Os workers acordam quando há
trabalho, fazem uma etapa por tarefa, terminam, e são relançados quando volta a
haver trabalho. Quando a fila baixa, o gatilho realimenta-a (feeder → discovery).

Nenhuma destas ordens cria um serviço do Windows — é arranque à mão ou por um
lançador externo à escolha do dono.

---

## START_SOURCE_CURATOR

```bash
py curadoria/supervisor.py
```

O supervisor, ao arrancar:
- **recupera tarefas órfãs** (IN_PROGRESS de um processo que morreu → PENDING);
- adquire um **lock de instância única** (PID + boot time + token) — não há dois
  supervisores a lutar pela mesma fila;
- lança o worker quando há trabalho elegível, **relança-o se ele morrer**, e
  aciona **discovery pelo low watermark** quando a fila baixa.

Opções úteis: `--pausa` (pausa do worker entre tarefas), `--poll` (intervalo do
supervisor entre voltas).

## STOP_SOURCE_CURATOR — pedir para parar **não** é matar

```bash
echo "motivo da paragem" > curadoria/PARAR.flag
```

O `PARAR.flag` é lido **entre voltas**, no único instante em que não há trabalho
a meio. O worker termina a volta em curso e sai limpo; o supervisor sai a
seguir. Nada fica IN_PROGRESS por corte a meio.

Para voltar a arrancar, **apague a flag** e corra o START outra vez:

```bash
rm curadoria/PARAR.flag
```

Matar o processo (`taskkill`) também funciona — o supervisor recupera as órfãs
no próximo arranque — mas perde a volta em curso. Preferir a flag.

## STATUS_SOURCE_CURATOR — derivado do SO, nunca do JSON

```bash
py curadoria/supervisor.py --estado      # estado do serviço, derivado do SO
py curadoria/status_live.py              # painel completo (fila, lifecycle, discovery)
```

`--estado` responde com a vida **medida no SO no instante da leitura**:
`SUPERVISOR_ALIVE`/`WORKER_ALIVE` vêm de o PID existir agora, não de um campo
gravado. Um `SUPERVISOR-STATE.json` que diga RUNNING com o processo morto é
lido como **STOPPED**; um worker com PID vivo mas sem heartbeat recente é
**STALE**, com o `HEARTBEAT_AGE_S` à vista.

Estados corretos quando **não há trabalho** (isto **não** se chama STOPPED):

```
SUPERVISOR_STATE = RUNNING
WORKER_STATE     = IDLE
QUEUE_ELIGIBLE   = 0
```

---

## OS LIMIARES DO MODO CONTÍNUO (declarados em `gatilho_discovery.py`)

| limiar | valor | porquê (resumo) |
|---|---|---|
| `QUEUE_LOW_WATERMARK` | 10 | colchão para o worker não parar entre esvaziar a fila e o feeder encher outra vez |
| `CANDIDATE_LOW_WATERMARK` | 20 | discovery (rede) só quando o acervo de candidatas está a acabar |
| `DISCOVERY_MIN_INTERVAL_S` | 3600 | não crawlar em rajada; respeita o orçamento de rede |

Limites **duros** de rede por corrida de discovery (não alargar sozinho):
`MAX_PEDIDOS_TOTAIS=250 · MAX_POR_DOMINIO=10 · PROFUNDIDADE=1 · robots ao vivo`.

## O QUE O SERVIÇO **NÃO** FAZ

- **Não promove READY sozinho a partir de QUALIFY.** QUALIFY aloca identidade e
  passa ao contrato; READY só sai de um canário que resolveu.
- **Não aperta o botão da Collection de produção** (`COLLECTION_PRODUCTION_AUTO
  = NO`, `BIG_COLLECTION_ALLOWED = NO`).
- **Não toca** nos 18 READY_LEGACY, no gate de detalhe, na Sala, RAW, DERIVED,
  Intelligence nem no Big Collection.
