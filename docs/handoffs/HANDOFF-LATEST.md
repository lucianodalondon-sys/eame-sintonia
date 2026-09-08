# HANDOFF — ÚLTIMO ESTADO · 2026-09-08

> O ficheiro grande é
> [`HANDOFF-EMERGENCIA-COLLECTION-FOUNDATION-2026-09-08.md`](HANDOFF-EMERGENCIA-COLLECTION-FOUNDATION-2026-09-08.md).
> **Este é só o ponteiro para onde o trabalho parou.**

```
WORK_BRANCH   claude/collection-foundation-integration-v1
WORK_HEAD     124c6999          (medir outra vez: git fetch)
WORKTREE      limpa
```

⚠️ **Duas sessões trabalham nesta branch ao mesmo tempo.** Já colidimos três
vezes. `git fetch` **antes de começar** e **antes de cada commit**. Nunca
`--force`. Se o remoto andou: preservar o próprio trabalho, rebasear, e ficar
com o melhor por medição.

## Checkpoints empurrados por esta linha

| commit | o que fechou |
|---|---|
| `51a26550` | **M1A** · a trava da inteligência, congelada por espécie |
| `be73768e` | **reconciliação M1** · a trava consome o veredito, não o redefine |
| `a9979c2c` | **O1** · censo dos donos — 7 de 15 conceitos com dono duplicado |
| `6e26e4a7` | **O2** · o contrato da telemetria |
| `96cbb2e7` | **O3** · o fluxo no seco — `NOT_RUN` ≠ `ERROR` |
| `ea647d86` | **O4** · relatório do fluxo |
| `220e0e7a` | **O5** · gestão da coleta |
| `81dc8662` | **O6** · aprender com a fonte, sem `SOURCE_SCORE` |
| `0593e905` | **O7** · evolução — a porta estreita da promoção |
| `0552424a` | **O8** · o mapa nunca fica verde por silêncio |
| `105602f6` | **O8B** · o mapa deixa de dizer que não existe o que existe |
| `124c6999` | **O9** · o primeiro executor real fala a língua comum |

## O que o O8B corrigiu, e por que era maior do que parecia

O mapa publicava — e commitava — que um ficheiro **não existia**, com ele no
disco. E o `SYSTEM_MAP_CHECK` dava `PASS`.

```
EXISTE NO DISCO  ≠  RASTREADO PELO GIT  ≠  NÃO EXISTE
```

`scan_repo.py:148` lista com `git ls-files` — só o que já foi `git add`ado.
**Medido: toda peça nova nascia falsamente partida e curava-se sozinha no commit
seguinte.** Uma mentira que desaparece antes de alguém a investigar.

E a `P4` não apanhava por duas cegueiras: compara o gerado com o gerado, e itera
a lista **resolvida** — que numa peça acusada de inexistente está vazia. Zero
ficheiros iterados, prova passa.

Guarda nova: `P4_NAO_MENTIR_SOBRE_EXISTENCIA`, que parte dos caminhos
**declarados** e pergunta ao **disco**. `provas/o_mapa_nao_mente.py` prova que
morde.

> ⚠️ **Não troquei** `git ls-files` por `--cached --others --exclude-standard`,
> que seria o conserto da causa. Mudaria o significado do inventário para todas
> as outras provas e faria o mapa reprovar em árvore suja. Fica **registado como
> alternativa medida**, não esquecido.

## Onde a observabilidade está

```
ARCHITECTURE         MEDIDO
TRACE                MEDIDO      só a RC-9 emite
DIAGNOSTIC           PARCIAL     1 de 42 executores emite
PERFORMANCE          PARCIAL     duração por corrida, não por etapa
EVOLUTION            NOT_MEASURED
COLLECTION_STRATEGY  NOT_MEASURED
```

`OBSERVABILITY_READY = SIM` · `EVOLUTION_READY = SIM` ·
`COLLECTION_FOUNDATION_CLOSED = NÃO`

> **Contrato pronto ≠ instrumentado ≠ observado.** E **um executor instrumentado
> ≠ sistema instrumentado**: 41 continuam calados, e **calado não é zero**.

## Próximo passo

**Instrumentar o segundo executor** — e aí `PARCIAL` começa a ter denominador
que se compara. Depois `O10` a sério: a matriz por executor × etapa × campo.

`medidas/banco_no_seco.py` já permite emitir sem tocar produção. A migration
`024` **continua por aplicar**, e isso é de propósito.

**Não começar a M2.** A `RC-1` continua sem `STRUCTURED` nem `ADMISSION`.

## Verificar em seis comandos

```bash
cd /f/eame-sintonia && git fetch origin && git status --porcelain
python system-map/scripts/validate_system_map.py
python provas/o_mapa_nao_mente.py
python provas/o_executor_conta_se.py
python provas/trava_da_inteligencia_morde.py
python -m unittest discover -s tests -q
```

Esperado: `SYSTEM_MAP_CHECK=PASS` · `MAPA_NAO_MENTE=PASS` ·
`EXECUTOR_CONTA_SE=PASS` · `TRAVA_MORDE=PASS` · **71 falhas na suite, que são a
linha de base herdada** (medir com `git stash` antes de culpar uma mudança).

**Zero escritas em produção. Zero rede. Inteligência congelada.**
