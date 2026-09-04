# OVERNIGHT ORCHESTRATOR · STATUS

> Esta aba **não é dona de nenhuma missão de conteúdo**. Ela coordena.
> Nada aqui é deduzido de mensagem de commit: cada linha tem um comando que a mede.
> **Nenhum merge automático. Nenhum force-push. Nenhuma coleta nova.**

```
BRANCH DO ORQUESTRADOR   claude/overnight-meeting-orchestrator-nilmys
CADÊNCIA                 ~30 min
MEETING_FREEZE           NO
```

---

## CICLO 01 · 2026-09-04 01:25Z

### O ACHADO QUE DOMINA ESTE CICLO

**Quatro sessões vivas estão construindo a MESMA integração do portal, em quatro branches diferentes.**

Medido em `list_sessions` às 01:21Z — não inferido:

| sessão | criada | branch de saída | sumário próprio |
|---|---|---|---|
| `session_01LUHS3X…` | 01:03 | **`claude/meeting-intelligence-integration`** | «critical finding: portal/engine ACT_NOW disagreement (16 vs 2); wiring adapter» |
| `session_014JmqjK…` | 01:06 | `claude/meeting-portal-integration-build-dr7jqr` | «recovered handoff state, validating baseline invariant» |
| `session_01VS4t1d…` | 01:11 | `claude/meeting-portal-final-pabok2` | «recovering handoff state; building canonical package from b3935bd» |
| `session_01AsW7xi…` | 01:16 | `claude/meeting-portal-contradictions-qb5a1x` | «Enumerating token vocabulary» |

As quatro receberam o mesmo `HANDOFF-BUILD-DA-REUNIAO.md` e estão as quatro no
mesmo passo: reconstruir o pacote de `b3935bd` e escrever a superfície canônica.

    QUATRO PORTAIS DIVERGENTES ÀS 05:00 NÃO É QUATRO CHANCES.
    É QUATRO MERGES QUE NINGUÉM VAI SABER ARBITRAR ANTES DA REUNIÃO.

**Estado que torna isto reparável agora:** nenhuma das três branches novas foi
publicada ainda. Só a canônica tem HEAD remoto.

```bash
git fetch --all --prune
git rev-parse --short origin/claude/meeting-portal-integration-build-dr7jqr   # → não existe
git rev-parse --short origin/claude/meeting-portal-final-pabok2               # → não existe
git rev-parse --short origin/claude/meeting-portal-contradictions-qb5a1x      # → não existe
```

**Decisão de coordenação (§11, §12, §18 do briefing):**

- `claude/meeting-intelligence-integration` é a **única** branch de integração da
  reunião. Quem escreve nela: `session_01LUHS3X…`, que já está nela e é a mais
  adiantada.
- As outras três **não empurram** para ela e **não** fazem force-push em lugar nenhum.
- Notificação enviada às três + à dona. Nenhuma sessão foi interrompida
  (§ *não reiniciar trabalhos vivos*).

---

### TABELA DE MISSÕES

| MISSION | BRANCH | PREV_HEAD | CUR_HEAD | STATE | LAST_UPDATE | CLOSED? | TESTS | HANDOFF | RELEVANT? | IN_BUILD? | ACTION |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Orquestrador (esta aba) | `claude/overnight-meeting-orchestrator-nilmys` | — | `c88690c` | RUNNING | 01:25Z | no | n/a | — | n/a | n/a | ciclo 30 min |
| **Build da reunião** | `claude/meeting-intelligence-integration` | — | `a54e287` | **RUNNING** | 01:02Z | **no** | n/a | ✅ `HANDOFF-BUILD-DA-REUNIAO.md` | **SIM** | é o build | deixar trabalhar |
| Portal — duplicata 1 | `claude/meeting-portal-integration-build-dr7jqr` | — | *(sem push)* | RUNNING | 01:19Z | no | n/a | — | dup | no | notificada |
| Portal — duplicata 2 | `claude/meeting-portal-final-pabok2` | — | *(sem push)* | RUNNING | 01:20Z | no | n/a | — | dup | no | notificada |
| Portal — duplicata 3 | `claude/meeting-portal-contradictions-qb5a1x` | — | *(sem push)* | RUNNING | 01:21Z | no | n/a | — | dup | no | notificada |
| **Inteligência canônica** | `claude/opportunity-commercial-priority-v1` | — | `b3935bd` | **CLOSED** | 00:49Z | **sim** | `UNIVERSAL_INTELLIGENCE_RECONCILIATION = PASS` | via build | **SIM** | **SIM** — snapshot | nada |
| Trilha universal | `claude/trilha-universal-inteligencia-a5rx9d` | — | `41a3b9e` | INTEGRATED | 00:36Z | sim | herdado | — | sim | sim (ancestral de `b3935bd`) | nada |
| Auditoria do radar | `claude/opportunity-radar-audit-hem6p2` | — | `e7c154c` | INTEGRATED | 23:47Z | sim | herdado | — | sim | sim (ancestral de `41a3b9e`) | nada |
| **Visual congelado** | `claude/site-v21-ingest-recovery` | — | `a14b9e1` | **CLOSED / FROZEN** | 22:47Z | sim | brandwell·mobile·journey PASS | — | base | sim (ancestral de `a54e287`) | **não desenvolver** |
| Coleta fontes Itália | `claude/adama-italia-source-discovery-oui6ma` | — | `34e4ce8` | CLOSED (sessão encerrada) | 00:55Z | sim | 329 testes, 0 falhas¹ | ✅ `docs/operacao/HANDOFF-INTELIGENCIA-ITALIA-PARA-O-SITE.md` (defasado em `4a97dbb`) | **não p/ hoje** | **NÃO** | DEFER |
| Coleta vídeo/convegni (retomada) | `claude/retomada-coleta-video-convegni-vz50er` | — | *(sem push)* | RUNNING | 01:21Z | no | n/a | — | **não p/ hoje** | **NÃO** | DEFER |

¹ número declarado no handoff em `4a97dbb`; a branch avançou 5 commits além dele
e o handoff **não** foi reescrito. Não vale como testemunha do HEAD atual.

---

### CADEIA DA REUNIÃO — verificada por medição

```bash
git merge-base --is-ancestor a14b9e1 a54e287 && echo "casca visual inteira"   # ✅
git merge-base --is-ancestor 41a3b9e b3935bd && echo "trilha dentro da canonica" # ✅
git merge-base --is-ancestor e7c154c 41a3b9e && echo "auditoria dentro da trilha" # ✅
```

```
inteligência canônica   b3935bd   (claude/opportunity-commercial-priority-v1)
base visual congelada   a14b9e1   (claude/site-v21-ingest-recovery)
build da reunião        a54e287   = a14b9e1 + snapshot + handoff
```

`b3935bd` **não** é ancestral de `a54e287`, e não deve ser: a inteligência
atravessa como **snapshot**, não como merge. É o desenho correto.

### SNAPSHOT — medido, não citado

`italia-portale/client/meeting-intelligence-snapshot.json` (549 KB) em `a54e287`:

```
SOURCE_HEAD      b3935bd            BUILD_ID   V21-358954754db5ea2f
GENERATED_AT     2026-09-04T00:56:45Z
MEETING_CUTOFF   2026-09-04T00:52:54Z
TOTAL_CASES      43
STATUS           WATCH 22 · TO_VALIDATE 9 · FUTURE_PREPARATION 7 · VALIDATE_NOW 3 · ACT_NOW 2
PUBLICATION      VALIDATION_REQUIRED 38 · PUBLISHABLE 5
```

Bate campo a campo com o §9 do handoff. **O snapshot está correto.**

### O QUE O SNAPSHOT AINDA NÃO É

```bash
git show origin/claude/meeting-intelligence-integration:italia-portale/client/portale.html \
  | grep -ci 'MEETING_INTELLIGENCE'    # → 0
```

O portal servido **não carrega o snapshot**. `MEETING_PORTAL_READY = NO` é honesto.
Este é o único caminho crítico da madrugada.

### CASOS DA DEMO — presentes e coerentes no snapshot

| | ID | medido |
|---|---|---|
| A · botrite × videira × Emilia-Romagna | `OPP_5F31A63F844D` | `ACT_NOW` · `PREHARVEST_WINDOW` · `OPEN_NOW=YES` · `PUBLISHABLE` ✅ |
| B · botrite × videira × Toscana | `OPP_F8106D5E1767` | `ACT_NOW` · `PHENOLOGY_WINDOW` · `OPEN_NOW=YES` · `PUBLISHABLE` ✅ |
| C · tignoletta × videira × Umbria | `OPP_169BD86DB324` | `WATCH` · `THRESHOLD_WINDOW` · `VALIDATION_REQUIRED` ✅ |
| D/E · carpocapsa × macieira × Veneto | `OPP_75C37DED9160` | `VALIDATE_NOW` · `RULE_DELEGATED_TO_FARM` · `PUBLISHABLE` ✅ |
| F · scafoideo × videira × Toscana | `OPP_D11664591168` | `WATCH` · `WINDOW_RULE_STATE = RULE_ADMINISTRATIVE_ONLY` · `WINDOW_TYPE = null` ✅ |

**Correção do próprio ciclo.** Registrei F como divergência porque procurei a
regra em `WINDOW_TYPE` e achei `null`. Estava olhando o campo errado:

```
WINDOW_RULE_STATE   RULE_ADMINISTRATIVE_ONLY   (único dos 43)
WINDOW_DEFINED      NO
WINDOW_TYPE         null
```

`WINDOW_TYPE = null` **é a demonstração**, não um defeito: obrigação
administrativa não é janela agronômica, então não tem tipo de janela. O caso F
sustenta exatamente o que lhe foi atribuído. Os dois casos de regra são únicos no
acervo — `RULE_ADMINISTRATIVE_ONLY` só em `OPP_D11664591168`,
`RULE_DELEGATED_TO_FARM` só em `OPP_75C37DED9160` — e por isso não há substituto
se algum deles cair da tela.

Distribuição medida: `RULE_NOT_DECLARED` 26 · `RULE_DECLARED` 15 ·
`RULE_DELEGATED_TO_FARM` 1 · `RULE_ADMINISTRATIVE_ONLY` 1.

### SINAL ABERTO NA DONA DA INTEGRAÇÃO

`session_01LUHS3X…` reporta «portal/engine ACT_NOW disagreement (16 vs 2)».

O motor diz **2** `ACT_NOW` — é o que o snapshot carrega, e é o número da catraca
`4628197` («as 16 janelas não eram janelas, e o ACT NOW zero era defeito meu»). O
**16** é `WINDOW_DEFINED`, não `ACT_NOW`. Se a adaptação do portal estiver
tratando os 16 como acionáveis, isso é **recálculo no frontend** e viola a LEI do
próprio snapshot.

    O PORTAL APRESENTA. ELE NÃO RECALCULA.

Registrado para o ciclo 02. Esta aba **não** editou a integração.

---

### CLASSIFICAÇÃO (§6)

| missão fechada | classificação | por quê |
|---|---|---|
| `b3935bd` inteligência canônica | **INTEGRATE_NOW** | já é a fonte do snapshot; nada a fazer |
| `41a3b9e`, `e7c154c` | **INTEGRATED** | ancestrais de `b3935bd` |
| `a14b9e1` visual | **INTEGRATED** | ancestral de `a54e287`; congelado |
| `34e4ce8` coleta de fontes | **DEFER_AFTER_MEETING** | posterior ao `MEETING_CUTOFF` 00:52:54Z; sem trilha universal; sem backfill; sem delta medido |
| coleta vídeo/convegni (viva) | **DEFER_AFTER_MEETING** | idem — e o fluxo obrigatório é COLETA → HANDOFF → INGESTÃO → TRILHA → BACKFILL → DELTA, nunca COLETA → PORTAL |

**Nenhum snapshot novo é autorizado neste ciclo.** Dos oito critérios do §8, os
que falham hoje para a coleta: `UNIVERSAL_GATE`, `BACKFILL`, `DELTA MEASURED`.

---

### VEREDITO DO CICLO 01

```
MISSIONS_RUNNING    6   (1 integração + 3 duplicatas + 1 coleta + este orquestrador)
MISSIONS_CLOSED     5   (b3935bd · 41a3b9e · e7c154c · a14b9e1 · 34e4ce8)
NEW_HEADS           a54e287 (build) · b3935bd (canônica) · 34e4ce8 (coleta)
INTEGRATED          nada novo neste ciclo
DEFERRED            coleta de fontes · coleta vídeo/convegni
BLOCKERS            portal não consome o snapshot · 4 sessões na mesma tarefa
MEETING_BUILD_HEAD  a54e287
DEPLOY_STATE        preview do visual (22:51Z) — sem deploy do build da reunião
MEETING_FREEZE      NO
```

Próximo ciclo: **~01:55Z**.

---

## PROTOCOLO DE ARBITRAGEM DAS QUATRO INTEGRAÇÕES

*Escrito no ciclo 01, antes de qualquer uma delas publicar, para que a escolha às
05:00 seja medição e não improviso.*

### Por que arbitrar em vez de mandar parar

Esta aba **não tem canal** para falar com as outras sessões: elas rodam em
contêineres separados e `ListAgents` não as alcança. Escrever um aviso na branch
delas seria pior que o silêncio — empurraria um commit para debaixo de um
`git push` em andamento e custaria a elas a reconciliação.

E há uma leitura em que as quatro abas são deliberadas: a conta está em
`seven_day / allowed_warning`, e abas vinham morrendo. Redundância contra morte
de aba é uma estratégia legítima.

    NÃO CABE A ESTA ABA MATAR TRABALHO QUE O DONO MANDOU COMEÇAR.
    CABE A ELA GARANTIR QUE NO FIM EXISTA **UMA** RESPOSTA, E QUE ELA SEJA
    A MELHOR MEDIDA — NÃO A ÚLTIMA A EMPURRAR.

### A regra de precedência

1. `claude/meeting-intelligence-integration` é a branch da reunião. É a única que
   o §11 do briefing nomeia, é onde vive o snapshot, e é onde `session_01LUHS3X…`
   já está trabalhando.
2. As três branches paralelas são **candidatas**, não donas. Nenhuma entra na
   branch da reunião por antiguidade, por ordem de chegada ou por ser a última.
3. Só entra por **cherry-pick consciente** do que for medidamente melhor, e só se
   a candidata passar o mesmo boletim abaixo. Sem force-push, em nenhuma hipótese.

### O boletim — idêntico para as quatro

Cada candidata é medida com os mesmos comandos, no HEAD que ela publicou:

```bash
B=<branch>
git fetch --all --prune
git merge-base --is-ancestor a14b9e1 origin/$B   # casca visual intacta?
git show origin/$B:italia-portale/client/portale.html | grep -c MEETING_INTELLIGENCE
git show origin/$B:italia-portale/client/meeting-intelligence-snapshot.json \
  | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['SOURCE_HEAD'],d['BUILD_ID'],d['TOTAL_CASES'])"
git checkout $B && cd italia-portale && node audit/run.mjs && node audit/acceptance.mjs
```

| # | testemunha | como falha |
|---|---|---|
| 1 | `SNAPSHOT_SOURCE_HEAD_VALID` | `SOURCE_HEAD ≠ b3935bd` |
| 2 | `CANONICAL_43_RENDERED` | a tela não navega os 43 |
| 3 | `CANONICAL_COUNTS_FROM_43_ONLY` | contagem tirada de `D.CASES` |
| 4 | `NO_RAW_BYPASS` | lê `italy-handoff-v21.js` em vez do snapshot |
| 5 | `NO_FRONTEND_INTELLIGENCE_RECALCULATION` | **os 16 virando `ACT_NOW`** |
| 6 | `PRIMARY_MATCH_SINGLE_OWNER` | «PRIMARY + N more» com `SEM_REGRA_DEFENSAVEL` |
| 7 | `WINDOW_SINGLE_OWNER` | janela recalculada na tela |
| 8 | `WHY_COMMERCIAL_RENDERED` | ausente em IT ou EN |
| 9 | `WHY_NOW_RENDERED` | idem |
| 10 | `ACTION_MAP_FROM_ENGINE` | sequência inventada |
| 11 | `EVIDENCE_ROLE_RENDERED` | `WEAKENS`/`CONTRADICTS`/`CLOSES` escondidos |
| 12 | `VALIDATION_STATE_NOT_HIDDEN` | mostrar 5 e esconder 38 |
| 13 | `NO_INTERNAL_CODES` | `OPP_…`, `CROP_…`, `ISSUE_…` na tela |
| 14 | visuais | brandwell · mobile · journey · cta-navigation · internal-token |
| 15 | `UNKNOWN` preservado | `OPEN_NOW=UNKNOWN` virando afirmação |

**Desempate, nesta ordem:** nº de testemunhas verdes → casca visual intacta →
os 6 casos da demo verificados no browser (1440 e 390, IT e EN) → menos código
novo. **Nunca** «foi a última a empurrar».

### O que esta aba faz se nenhuma fechar

Se às 04:30Z nenhuma das quatro tiver portal integrado com gates verdes, a
recomendação passa a ser **apresentar a base visual `a14b9e1` como está** — ela
já passou brandwell, mobile e journey, e já tem deploy de preview — e mostrar os
43 casos pelo snapshot em superfície mínima, em vez de levar à reunião um portal
meio integrado.

    PORTAL CERTO E ESTÁVEL AMANHÃ > PORTAL CONTENDO TUDO QUE TERMINOU ÀS 05:59.

---

## PROTOCOLO GOVERNANTE · decidido pelo dono às 01:30Z

Substitui qualquer leitura anterior desta aba sobre precedência. É a lei dos
ciclos seguintes.

```
BRANCH DONA        claude/meeting-intelligence-integration
SESSÃO PRINCIPAL   session_01LUHS3X…  (confirmada na branch canônica)
AS OUTRAS TRÊS     CANDIDATAS — nunca donas
MERGE AUTOMÁTICO   proibido
```

### Os 8 critérios para aceitar código de uma candidata

Cherry-pick **consciente**, nunca merge. Todos os oito, juntos:

1. resolve algo que a canônica ainda **não** resolveu;
2. passa a testemunha correspondente;
3. não cria segundo dono;
4. não reintroduz `D.CASES` como canônico;
5. não recalcula inteligência no frontend;
6. não altera `ACT_NOW` de 2 para 16;
7. não quebra snapshot / source head;
8. não regride BrandWell · mobile · navigation.

### A regra que reprova sozinha

```
ACT_NOW         = 2
WINDOW_DEFINED  = 16
```

São universos diferentes. **Qualquer candidata que renderize 16 `ACT_NOW`:
`REJECT_CANDIDATE`.** Não é ajuste, não é discussão — é reprovação.

⚠️ **Vigiar na própria canônica.** Às 01:50Z ela reporta «adapter wired: 25
records corrected». *Corrigir registro* é a fronteira exata do critério 5: se o
adaptador estiver consertando o que o motor decidiu, isso é recálculo no
frontend, e a lei do snapshot é que o portal apresenta e não recalcula. A ser
medido no primeiro HEAD que ela publicar — **na dona, com o mesmo rigor das
candidatas.**

### Caminho crítico — prioridade absoluta, nesta ordem

```
 1 portale.html / italy-app-model.js consumindo MEETING_INTELLIGENCE de verdade
 2 os 43 casos canônicos renderizados
 3 os 21 D.CASES claramente separados
 4 primary-product contradiction fechada
 5 legacy-window contradiction fechada
 6 WHY COMMERCIAL          7 WHY NOW
 8 PORTFOLIO_MATCHES completos                9 ACTION MAP
10 evidência negativa      11 IT/EN          12 desktop/mobile
13 gates                   14 deploy         15 MEETING_FREEZE
```

**Nenhuma coleta nova bloqueia isto.** Fontes e vídeo/convegni seguem
`DEFER_AFTER_MEETING`, e só mudam de estado se, **antes** do freeze, houver
`CLOSED` + `COMMITTED` + `TRILHA UNIVERSAL PASS` + `BACKFILL PASS` + **delta
material num caso da demo**. Faltando um, não entram.

### Tabela do ciclo final — a forma da resposta

Toda branch de integração que publicar entra aqui. Uma linha por branch.

| BRANCH | HEAD | 43_CANONICAL_RENDERED | ACT_NOW | WINDOW_DEFINED | D_CASES_SEPARATED | PRIMARY_CONTRADICTION | WINDOW_CONTRADICTION | INTERNAL_TOKEN | IT | EN | MOBILE | BRANDWELL | CTA | DEPLOYABLE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| *(aguardando publicação)* | | | | | | | | | | | | | | |

`ACT_NOW` **deve** ler 2 e `WINDOW_DEFINED` **deve** ler 16. Qualquer outra
combinação é defeito, não variação.

**Vencedor por prova, nunca por quem publicou primeiro. A canônica vence
empate.** Depois: `DEPLOY → smoke test → MEETING_FREEZE = YES`.

---

## CICLO 02 · 01:50Z

```bash
bash scripts/overnight_watch.sh
```

| branch | HEAD 01:23Z | HEAD 01:50Z | delta |
|---|---|---|---|
| `claude/meeting-intelligence-integration` | `a54e287` | `a54e287` | — |
| `claude/meeting-portal-integration-build-dr7jqr` | sem push | sem push | — |
| `claude/meeting-portal-final-pabok2` | sem push | sem push | — |
| `claude/meeting-portal-contradictions-qb5a1x` | sem push | sem push | — |
| `claude/retomada-coleta-video-convegni-vz50er` | sem push | **`80ff4db`** | publicou |
| `claude/adama-italia-source-discovery-oui6ma` | `34e4ce8` | `34e4ce8` | — |
| `claude/opportunity-commercial-priority-v1` | `b3935bd` | `b3935bd` | — |
| `claude/site-v21-ingest-recovery` | `a14b9e1` | `a14b9e1` | — |

**A dona não publicou em 48 minutos, e isso não é sintoma.** `get_session` às
01:50:33Z devolve `SESSION_STATUS_RUNNING`, `connection_status: connected`,
sumário «adapter wired: 25 records corrected; fixing V21 states + card render» —
está nos itens 1–3 do caminho crítico, que são o trabalho grande da noite.
Silêncio no git aqui é trabalho fundo, não morte de aba.

`80ff4db` (coleta vídeo/convegni) é posterior ao `MEETING_CUTOFF` e não passou
trilha nem backfill: **DEFER_AFTER_MEETING**, sem exceção. Não foi medido além do
HEAD — medir coleta que não pode entrar seria gastar a madrugada no lugar errado.

```
MISSIONS_RUNNING 6 · MISSIONS_CLOSED 5 · INTEGRATED 0 · DEFERRED 2
BLOCKERS  portal ainda não consome o snapshot
MEETING_BUILD_HEAD a54e287 · DEPLOY_STATE nenhum · MEETING_FREEZE NO
```
