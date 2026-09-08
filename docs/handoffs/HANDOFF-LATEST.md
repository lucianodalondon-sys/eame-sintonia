# HANDOFF — ÚLTIMO ESTADO · 2026-09-08

> O ficheiro grande é
> [`HANDOFF-EMERGENCIA-COLLECTION-FOUNDATION-2026-09-08.md`](HANDOFF-EMERGENCIA-COLLECTION-FOUNDATION-2026-09-08.md).
> **Este é só o ponteiro para onde o trabalho parou.**

```
WORK_BRANCH   claude/collection-foundation-integration-v1
WORK_HEAD     8e1947d2          (medir outra vez: git fetch)
WORKTREE      limpa
```

⚠️ **Duas sessões trabalham nesta branch ao mesmo tempo.** Já colidimos quatro
vezes — a última no meio desta missão, e correu bem porque a regra foi
cumprida. `git fetch` **antes de começar** e **antes de cada commit**. Nunca
`--force`. Se o remoto andou: **parar de escrever, ler os commits novos, e
integrar por medição** — não por antiguidade.

## Checkpoints empurrados por esta linha

| commit | o que fechou |
|---|---|
| `51a26550` | **M1A** · a trava da inteligência, congelada por espécie |
| `a9979c2c` … `0552424a` | **O1–O8** · o contrato, o fluxo no seco, o mapa que não fica verde por silêncio |
| `105602f6` | **O8B** · o mapa deixa de dizer que não existe o que existe |
| `124c6999` | **O9** · o primeiro executor real fala a língua comum |
| `44e2de1b` | **O9 (fronteira)** · o ciclo da corrida, e a linha que se escreve quando o executor morre |
| `c293be65` | **O10R** · os nomes deixam de prometer mais do que provam |
| `8e1947d2` | **O9R** · o sensor sai do replay e entra na estrada oficial |

## O que mudou em `8e1947d2`, e por que era o que faltava

O `O10R` **mediu** o buraco e escreveu-o com todas as letras no ledger:
`FORWARD_INSTRUMENTED: false`. Não foi preciso descobri-lo outra vez — foi
preciso **fechá-lo**.

```
UM REPLAY DE ARQUIVO PODE PROVAR QUE O SENSOR FUNCIONA
E NÃO PROVAR QUE ELE ESTÁ NA ESTRADA.
```

O executor de PDF tem dois caminhos, e são mesmo dois:

```
LEGADO    correr()      varre os PDF históricos do Git, escreve um JSON
FORWARD   derivar_um()  recebe um raw_asset_id canónico REAL, entrega ao
                        dono da escrita, que escreve a linha do derivado
```

Toda a telemetria estava no primeiro. **`coleta/derivacao_forward.py`** é a
fronteira do segundo — e emite **uma etapa só**, `DERIVED`, de propósito:

- **não** emite `RAW`. Quem escreve `raw_asset` é `guarda/preservar_coleta.py`.
  *Ler a linha de outro não é ter corrido a etapa dele.* Fica como GAP com
  nome: `RAW_FORWARD_NAO_EMITE`.
- **não** emite `STRUCTURED`, `ADMISSION` nem `READY`. E `NOT_RUN` também
  seria mentira: `NOT_RUN` é «fazia parte do plano e não chegou a vez», e
  estas etapas não fazem parte de plano nenhum.

```
STAGE EXISTS IN VOCABULARY  ≠  STAGE RAN.
O caminho forward TERMINA EM DERIVED, e terminar aí é a verdade.
```

## As três perguntas, agora com três nomes

O censo publicava duas e a terceira vivia numa nota — e nota não é campo.

```
TELEMETRY_INFRASTRUCTURE_PROVED   YES   o instrumento aguenta
CANONICAL_FORWARD_PATH_PROVED     YES   a estrada oficial emite      ← nova
M2_ROUTE_OBSERVABILITY_READY      NO    STRUCTURED e ADMISSION nunca
                                        correram em caminho nenhum
```

`M2_ROUTE_OBSERVABILITY_READY` **continua `NO`, e continuar é o certo.**
Instrumentar o forward não torna `STRUCTURED` e `ADMISSION` observados. Há
teste que reprova se alguém o virar `YES` sem essas duas etapas correrem.

`M2_CONSTRUCTION_CAN_BEGIN = YES` · `M2_CANNOT_CLOSE_UNTIL_INSTRUMENTED = True`

## A prova, contra PostgreSQL 16 de verdade

`provas/o_forward_conta_se.py` — **39 factos**, cadeia canónica até à `024`
num banco descartável:

```
collection_run REAL  ·  a chave estrangeira MORDE (run_id inexistente é recusado)
raw_asset_id   REAL  ·  lido com SELECT depois de o dono do bruto escrever
linhagem fecha       ·  raw_asset 1 → derived_artifact 1, parent_sha256 do pai
UNACCOUNTED_INPUT=0  ·  fechada pela coluna GERADA, não por nós
identidade PROVADA   ·  RC-1 do modelo das estradas + IT-T2-002 do catálogo,
                        e os dois batem com o CANÁRIO declarado da estrada
falha injectada      ·  3 entram, 1 passa, 2 erram · ITEM_ERROR + DERIVATION_FAILED
invariância          ·  OUTPUT_FUNCTIONAL_CHANGED = NO
```

⚠️ **`pdftotext` (poppler-utils) tem de estar na máquina.** Sem ele o executor
devolve `FERRAMENTA_AUSENTE` para tudo — e a prova **recusa correr**, em vez de
passar a verde por silêncio.

## A lei do READY, e a quarta cópia do vocabulário

`leis/telemetria.ready_sem_quem_assine` recusa um `READY` que se declare
cumprido sem `ADMISSION` ter acontecido — e `NOT_RUN`, `SKIPPED`,
`NOT_APPLICABLE` e `FAIL` **não** são «aconteceu».

```
DERIVED STORED ≠ READY. Persistir não é julgar.
```

E as nove etapas viviam no **writer**. `telemetria.ETAPAS_DA_COLETA` passa a
ser o dono; `paridade_da_lingua` ganhou `P8` (o enum da `024` bate com o dono)
e `P9` (a lei do READY morde nas duas direcções).

## Três testes que congelavam o número de hoje

```
UM TESTE QUE FIXA O NÚMERO DE HOJE PROÍBE O DE AMANHÃ,
E O DEFEITO QUE ELE APANHA É O CRESCIMENTO.
```

`assertIs(False, FORWARD_INSTRUMENTED)` reprovou o **conserto**;
`assertEqual(54, TOTAL_RELEVANT_PATHS)` reprovou **um ficheiro novo**;
`assertIn('LEGACY_REPLAY', …)` reprovaria a **separação que o próprio teste
pediu**. Os três passaram a medir a relação, e não o literal.

## O que continua aberto, com nome

| gap | quem | o que custa hoje |
|---|---|---|
| `RAW_FORWARD_NAO_EMITE` | `guarda/preservar_coleta.py` | a entrada do `DERIVED` não se cruza com a saída do `RAW` dentro da mesma corrida |
| `TELEMETRY_FAILURE_SEM_POLITICA` | — | a excepção do rastro **sobe**; o artefato fica guardado, mas quem chama perde o recibo. Não há política escrita, e **não se inventou uma para passar no teste** |
| `STRUCTURED` / `ADMISSION` sem dono forward | RC-1 | é a M2 que os vai construir |
| `024` não aplicada em produção | — | de propósito. Aplicar é missão própria, com autorização própria |

## Próximo passo

**A M2: ligar `STRUCTURED` e `ADMISSION` da RC-1 — e nascer instrumentada.**
O padrão está de pé e é copiável: `coleta/derivacao_forward.py` + a prova
contra Postgres descartável. **Não** instrumentar um segundo executor primeiro:
a M2 é a jusante de `DERIVED` na RC-1, e nenhum segundo executor está nesse
caminho.

## Verificar em sete comandos

```bash
cd <repo> && git fetch origin && git status --porcelain
python3 system-map/scripts/validate_system_map.py
python3 provas/o_mapa_nao_mente.py
python3 provas/paridade_da_lingua.py
python3 provas/o_executor_conta_se.py
BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \
    python3 provas/o_forward_conta_se.py
python3 -m unittest discover -s tests -q
```

Esperado: `SYSTEM_MAP_CHECK=PASS` · `MAPA_NAO_MENTE=PASS` · `PARIDADE=PASS` ·
`EXECUTOR_CONTA_SE=PASS` · `FORWARD_CONTA_SE=PASS` · e a suíte em
**1589 · 1399 PASS · 17 FAIL · 20 ERROR · 153 SKIP**, com as **38 falhas
herdadas** medidas em `c293be65` (`NEW_FAILURES = 0`).

⚠️ **O número «71 falhas» do handoff anterior não reproduz.** Medido em
`124c6999`: 1498 testes, 17 FAIL + 20 ERROR = **37** herdadas. Não se sabe de
onde veio o 71, e não se inventou uma explicação para ele.

**Zero escritas em produção. Zero Supabase. Zero rede na coleta. `024` por
aplicar. M2 não começou.**
