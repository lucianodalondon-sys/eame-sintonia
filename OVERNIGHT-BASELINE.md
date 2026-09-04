# OVERNIGHT · BASELINE DE PARTIDA

Estado medido **antes** de qualquer alteração desta madrugada. Cada linha tem o
comando que a produz ao lado; nada aqui foi digitado de memória.

```
DATA                  2026-09-04
BRANCH DE TRABALHO    claude/retomada-coleta-video-convegni-vz50er
HEAD_START            e95f6e0e3149dd707fd95f6908b68af0ce4fbe5e
TREE                  CLEAN (1 untracked: scripts/it_futuro_corpus.py, criado nesta sessão)
TESTES                329 passed, 4676 subtests passed
```

## 1 · O conjunto de pares publicado

```
ARQUIVO        data/samples/IT-ROTULOS-V1/IT-ROTULOS-PARES-V3.json
PARSER         it_rotulo_parser/3.1.0
PUBLISHED_PAIRS 2313
DIGEST         326557639f718a03d52be2976e2aff29
ESTADO         PUBLICADO — passou IT-ROTULOS-PORTAO-V1
PORTÃO         precisão 0,965 · recall 0,866 · violações 0 · ambíguos promovidos 0
CONJUNTO ANTIGO data/samples/IT-RADAR-V21/productRelationships.json (2030 pares, PINADO)
```

Testemunha de contêiner novo, rodando de `/` com `env -i`:
`LABEL_PARSER_SURVIVES_NEW_CONTAINER = PASS`, digest idêntico.

## 2 · Os quatro HEADs, e qual deles é produção

Esta é a descoberta que muda o plano da madrugada. **A branch em que trabalho não
contém o portal.**

| papel | branch | HEAD | contém app? |
|---|---|---|---|
| **coleta / inteligência de rótulo** (esta) | `claude/retomada-coleta-video-convegni-vz50er` | `e95f6e0` | **não** |
| **inteligência canônica — as 43** | `claude/opportunity-commercial-priority-v1` | `b3935bd` | não (é o motor) |
| **base visual congelada** | `claude/site-v21-ingest-recovery` | `a14b9e1` | sim |
| **build da reunião** | `claude/meeting-intelligence-integration` | `a15ac4e` | sim (`italia-portale/`) |

Medido nesta árvore:

```bash
find . -maxdepth 3 -name vercel.json -o -name package.json -o -name "next.config*"
# → vazio. Não há aplicação, não há projeto Vercel, não há package.json.
```

O único "portal" desta branch é `prototype/portal/index.html`, e ele carrega o
próprio aviso: `PROTOTYPE_FROZEN = SIM`, «não é base de decisão», congelado em
2026-08-28 porque o trabalho visual foi separado para outra missão.

**Consequência honesta:** as fases 18 a 23 da missão (portal, Preview da Vercel,
gates de browser 1440/390 IT/EN, `PREVIEW_URL`) **não são executáveis a partir
desta branch**. Não existe aqui o que fazer build. Fazer merge da branch da
reunião para cá criaria uma segunda linhagem do portal — exatamente a armadilha
das «duas cópias» que o handoff da reunião documenta — e um Preview servido de
uma branch de coleta não seria a build da reunião, seria um clone dela.

O commit `4f24d90` citado na Lei Zero **não existe nesta árvore**
(`git cat-file -t 4f24d90` → erro). `b3935bd` existe e é o HEAD do motor canônico.

## 3 · O que esta madrugada pode e não pode fazer

| | |
|---|---|
| `PRODUCTION_TOUCHED` | **NO** — não há produção alcançável daqui |
| `MEETING_BUILD_TOUCHED` | **NO** — a branch da reunião não é tocada |
| `FROZEN_SNAPSHOT_TOUCHED` | **NO** |
| worktree da canônica | **somente leitura**, `--detach` em `b3935bd`, sem commit |
| commits/pushes | somente em `claude/retomada-coleta-video-convegni-vz50er` |

## 4 · As 43 oportunidades canônicas — localizadas e reconstruídas

O pacote **não está no git**: `build/ITALY-REALITY-HANDOFF-V2.1/` é ignorado por
política. Ele é reconstruído. Reconstruí-o numa **worktree destacada**, sem tocar
na branch:

```bash
git worktree add --detach /home/user/wt-canonica b3935bd
cd /home/user/wt-canonica && bash scripts/v21_cadeia.sh
# → build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/OPPORTUNITIES.json
#   BUILD_ID V21-358954754db5ea2f · RECORDS 43
```

O `BUILD_ID` bate com o que o handoff da reunião declara. Os contratos do próprio
motor fecharam em zero violações (geografia 6472 registros, procedência 7169).

Com isso a Fase 4 deixa de depender das 3 oportunidades locais e passa a poder
medir o efeito do novo conjunto de pares **sobre as 43 reais**.

## 5 · O universo de 3 versus 43 — resolvido

`data/samples/IT-RADAR-V21/opportunities.json` desta branch tem **3** registros:
é uma **cópia pinada parcial**, feita para sobreviver à troca de contêiner, e não
o universo. O universo são as 43 do motor. A rodada anterior registrou "encontrei
3 e não invento as outras 40" — estava certa em não inventar, e agora as 40
restantes foram **localizadas**, não fabricadas.
