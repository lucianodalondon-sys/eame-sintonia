# HANDOFF — ÚLTIMO ESTADO · 2026-09-08

> O ficheiro grande é
> [`HANDOFF-EMERGENCIA-COLLECTION-FOUNDATION-2026-09-08.md`](HANDOFF-EMERGENCIA-COLLECTION-FOUNDATION-2026-09-08.md).
> **Este é só o ponteiro para onde o trabalho parou.**

```
WORK_BRANCH   claude/collection-foundation-integration-v1
WORK_HEAD     0552424a          (medir outra vez: git fetch)
WORKTREE      limpa
```

## Checkpoints empurrados

| commit | o que fechou |
|---|---|
| `51a26550` | **M1A** · a trava da inteligência, congelada por espécie |
| `be73768e` | **reconciliação M1** · a trava consome o veredito, não o redefine |
| `a9979c2c` | **O1** · censo dos donos — 7 de 15 conceitos com dono duplicado |
| `6e26e4a7` | **O2** · o contrato da telemetria, sem instalar nada |
| `96cbb2e7` | **O3** · o fluxo no seco — `NOT_RUN` ≠ `ERROR`, provado |
| `ea647d86` | **O4** · relatório do fluxo — 6 corridas, `UNACCOUNTED = 0` |
| `220e0e7a` | **O5** · gestão da coleta — o gestor não chama executor |
| `81dc8662` | **O6** · aprender com a fonte — sem `SOURCE_SCORE` |
| `0593e905` | **O7** · evolução — a porta estreita da promoção |
| `0552424a` | **O8** · o mapa nunca fica verde por silêncio |

## Os estados, separados

```
M1_CLASSIFICATION_PASS        CLOSED       a classificação acabou
SOURCE_NETWORK_COVERAGE       INCOMPLETE   47 fontes sem rota provada
OBSERVABILITY_READY           SIM          há contrato — NÃO é «está a medir»
EVOLUTION_READY               SIM          NÃO é «IA autónoma pronta»
COLLECTION_FOUNDATION_CLOSED  NÃO          0 classes fechadas
```

⚠️ **Podem discordar sem se contradizer.** `ONE QUESTION → ONE OWNER`: a trava
**lê** `leis/fundacao_da_coleta.py`, não recalcula. E o scanner existir não
fecha fundação nenhuma.

## Onde a observabilidade está

```
ARCHITECTURE         MEDIDO
TRACE                MEDIDO      só a RC-9 emite
PERFORMANCE          PARCIAL     duração por corrida, não por etapa
DIAGNOSTIC           NOT_INSTRUMENTED   12 códigos declarados, 0 emissores
EVOLUTION            NOT_MEASURED
COLLECTION_STRATEGY  NOT_MEASURED
```

**A dívida que vem a seguir:** fazer os executores emitirem `STAGE`,
`DIAGNOSTIC_CODE`, `DURATION` e `EXECUTOR`. O contrato já existe; falta quem
emita. E os **7 conceitos com dono duplicado** (`COLLECTION_RUN`, `CHECKPOINT`,
`RAW_ASSET`, `ADMISSION`, `COST`, `COUNTS`, `DURATION`) são onde a telemetria
diverge sem ninguém dar por isso.

## Próximo passo

**Instrumentar UM executor** com o contrato de `leis/telemetria.py`, e ver a
dimensão `DIAGNOSTIC` sair de `NOT_INSTRUMENTED`.

**Ainda não começar a M2.** E continua tudo por fechar em `RC-1`
(`STRUCTURED` + `ADMISSION`) — é a estrada com mais retorno.

## Verificar em seis comandos

```bash
cd /f/eame-sintonia && git fetch origin && git status --porcelain
python system-map/scripts/validate_system_map.py
python system-map/scripts/censo_da_observabilidade.py
python provas/trava_da_inteligencia_morde.py
python provas/fluxo_no_seco.py
python -m unittest discover -s tests -q
```

Esperado: worktree limpa · `SYSTEM_MAP_CHECK=PASS` · `TRAVA_MORDE=PASS` ·
`FLUXO_NO_SECO=PASS` · **71 falhas na suite, que são a linha de base herdada**
(medir com `git stash` antes de culpar uma mudança).

**Zero escritas em produção. Zero rede. Inteligência congelada.**
