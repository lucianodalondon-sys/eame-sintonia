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

---

## AUDITORIA DOS «25 RECORDS CORRECTED» — pronta antes de haver o que auditar

Complemento ao protocolo, 01:55Z. A dona **não foi tocada**. O que ficou pronto é
a ferramenta, para que a auditoria custe segundos no instante em que ela publicar
— e não vinte minutos na hora em que o tempo for mais caro.

```
scripts/audit_adapter_boundary.py        o auditor
MEETING-DECISION-FIELDS-REFERENCE.json   a referência congelada
REFERENCE_DIGEST                         0feb6e3e9ddb4e0d
```

### Duas correções à lista de campos

Medi o esquema real dos 43 casos. Dois nomes do protocolo não existem no snapshot:

| pedido | realidade medida |
|---|---|
| `WHY_THIS_IS_A_COMMERCIAL_OPPORTUNITY` | não existe. São `WHY_COMMERCIAL_IT` · `WHY_COMMERCIAL_EN` · `WHY_COMMERCIAL_CODES` |
| `WINDOW_CONDITION` | atravessa só como `WINDOW_CONDITION__PT_ONLY` (bool). A prosa PT não embarca — é a lei do snapshot, não uma falta |

Os outros 27 existem e entraram. A referência cobre **29 campos decisórios** nos
43 casos, cada caso com digest próprio.

### O que a referência já prova

```
TOTAL_CASES 43 · ACT_NOW 2 · WINDOW_DEFINED=YES 16 · PUBLISHABLE 5 · VALIDATION_REQUIRED 38
```

Medidos por contagem independente, não copiados do handoff — e conferem.

**`PRIMARY_MATCH` é nulo em 26 dos 43.** Esses 26 têm de chegar nulos ao client.
É a maior superfície de risco do §8: `PORTFOLIO_MATCHES[0] → PRIMARY_MATCH` é a
transformação mais natural do mundo para quem está montando um cartão, e é
proibida.

### O auditor foi testado contra as violações, não contra o caminho feliz

Um auditor que só passa em entrada limpa não prova nada. Os cinco casos:

| entrada | esperado | obtido |
|---|---|---|
| snapshot contra si mesmo | PASS | `exit 0` · `CHANGED = 0` |
| os 16 `WINDOW_DEFINED` virando `ACT_NOW` | REJECT | `exit 1` · «*ACT_NOW = 16 … REJECT_CANDIDATE*» |
| `PORTFOLIO_MATCHES[0] → PRIMARY_MATCH` | FAIL | `exit 1` · 14 registros nomeados |
| `WINDOW_OPEN_NOW: UNKNOWN → NO` | FAIL | `exit 1` · 41 campos ofensores |
| renome de chave **declarado** em `--map` | PASS | `exit 0` · renome é apresentação |
| o mesmo renome **não declarado** | FAIL | `exit 1` |

A última linha é o desenho, não um defeito: renomear chave é livre, mas tem de
ser **declarado**. Renome não declarado e recálculo escondido são
indistinguíveis de fora, e o auditor recusa os dois.

### Como rodar quando a dona publicar

```bash
git fetch --all --prune
# MEETING_PREVIOUS_HEAD = a54e287 ; COMMIT_RANGE = a54e287..<NEW_HEAD>
git log --oneline a54e287..origin/claude/meeting-intelligence-integration
git diff --stat a54e287..origin/claude/meeting-intelligence-integration

python3 scripts/audit_adapter_boundary.py <client-model.json> [--map renames.json]
```

O auditor percorre **qualquer** formato de JSON e reconhece um caso por
`OPP_[0-9A-F]+`, então funciona sem saber de antemão a forma que o adapter deu ao
modelo. Devolve o veredito A/B/C/D, os ofensores por registro e por campo, as
cinco testemunhas numéricas e as duas confusões nomeadas.

### A regra que a auditoria serve

    CORRIGIR A UI PARA ENTENDER O ESTADO.
    NUNCA CORRIGIR O ESTADO PARA CABER NA UI.

Se o veredito for **A** ou **B**: `ADAPTER_BOUNDARY = PASS`, **não abrir nova
auditoria**, seguir direto para 43 rendered → D.CASES separados → contradições →
IT/EN → mobile → gates → deploy.

Se for **C** ou **D**: os ofensores saem nomeados, registro e campo, e a
implementação não é aprovada até saírem.

---

## CICLO 03 · 02:20Z — a primeira candidata publicou, e foi auditada

A dona **continua em `a54e287`** (sem push há 78 min, `RUNNING`). Quem publicou
foi uma candidata:

```
claude/meeting-portal-contradictions-qb5a1x   8f37e36
  61e1089 01:48  o portal consome os 43, e o produto principal deixa de ter dois donos
  7b2f24f 02:02  as duas contradicoes fecham no DOM, e o motor deixou um ponteiro na propria prosa
  8f37e36 02:06  handoff: o estado de agora fica no topo

  meeting-surface.js  +483   meeting-labels.js  +414   portale.html  +464
  meeting-gate.mjs    +409   meeting-browser.mjs +244  audit/checks.mjs +12
```

São os itens **1, 2, 4 e 5** do caminho crítico. **A candidata está à frente da
dona.**

### ADAPTER_BOUNDARY = PASS_DECLARED_SCHEMA_ADAPTATION · IT e EN

Não por leitura de código: o adapter foi **executado** contra o snapshot real
(`scripts/adapter_dump.mjs`, `vm` do node, `build('it')` e `build('en')`) e a
saída foi medida contra a referência congelada.

```
TOTAL_CASES 43 · ACT_NOW 2 · WINDOW_DEFINED_YES 16 · PUBLISHABLE 5 · VALIDATION_REQUIRED 38
DECISION_FIELDS_CHANGED_BY_FRONTEND = 0
FRONTEND_INTELLIGENCE_RECALCULATION = NO
PRIMARY_MATCH_NULL_REFERENCE = 26 · CLIENT_PRIMARY_MATCH_NULL = 26
```

**As seis provas, todas OK:** UNKNOWN permanece UNKNOWN · `WINDOW_DEFINED=YES`
não promove `ACT_NOW` · `PORTFOLIO_MATCHES` não cria `PRIMARY_MATCH` ·
`PUBLICATION_STATE` não é promovido · `ACTION_BY_DEPARTMENT` não é reescrito ·
`WHY_COMMERCIAL` não é reconstruído.

### As cinco transformações, declaradas e provadas

`audit-maps/map-meeting-portal-contradictions.json`

| campo | transformação | prova |
|---|---|---|
| `NEED_DIRECTION` | prefixo `NEED_DIRECTION_` | 43/43 exato, reversível |
| `WINDOW_OPEN_NOW` | prefixo `WINDOW_OPEN_NOW_` | 43/43; `UNKNOWN` segue dizendo UNKNOWN em 41/41 |
| `PRIMARY_MATCH` | join por `PRODUCT_ID` | 17/17 casam; **26/26 nulos continuam nulos** |
| `WHY_COMMERCIAL_CODES` · `WHAT_IS_MISSING` · `WHY_NOW_CODES` | código → rótulo | cardinalidade e ordem preservadas; bijeções 9→9, 12→12, 6→6 em IT **e** EN |

Nenhum código interno (`OPP_` `CROP_` `ISSUE_` `REGION_` `CATPRD_`) na prosa
exibida, nos 43.

### Duas coisas que o auditor aprendeu nesta auditoria

**1 · Campo decisório aninhado escapava da medição.** O modelo do candidato põe a
janela em `window.DEFINED` e o produto em `products.primary`. O auditor só lia o
nível de topo — teria dado PASS sem olhar exatamente onde a violação moraria.
Agora achata dois níveis.

**2 · Cardinalidade não é bijeção.** `[A,B] → [rótuloB, rótuloA]` preserva a
contagem e troca o sentido. O auditor passou a exigir bijeção no acervo inteiro:
o mesmo código nunca vira dois rótulos, e dois códigos nunca colidem num rótulo.
Testado com a lista invertida de propósito — reprova.

    UMA TRANSFORMAÇÃO NÃO DECLARADA É INDISTINGUÍVEL DE RECÁLCULO.
    O AUDITOR RECUSA AS DUAS, E DEIXA O ADAPTER PROVAR QUAL É QUAL.

Foi assim que as cinco transformações acima chegaram a PASS: cada uma reprovou
primeiro, foi medida no acervo inteiro, e só então foi declarada.

### O que ainda NÃO foi medido nesta candidata

`ADAPTER_BOUNDARY` é a fronteira do dado. Falta a tela:

```
43 rendered no DOM · D.CASES separados · IT/EN na tela · desktop/mobile
brandwell · cta-navigation · internal-token · deploy
```

A candidata trouxe `meeting-gate.mjs` (409 linhas) e `meeting-browser.mjs` (244)
para isso — **não rodados por esta aba neste ciclo**. Rodá-los é o ciclo 04.

### Tabela do ciclo final — primeira linha preenchida

| BRANCH | HEAD | 43_CANONICAL | ACT_NOW | WINDOW_DEFINED | D_CASES_SEP | PRIMARY_CONTRA | WINDOW_CONTRA | INTERNAL_TOKEN | IT | EN | MOBILE | BRANDWELL | CTA | DEPLOYABLE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `meeting-intelligence-integration` (dona) | `a54e287` | — | — | — | — | — | — | — | — | — | — | — | — | — |
| `meeting-portal-contradictions-qb5a1x` | `8f37e36` | **43 ✅** | **2 ✅** | **16 ✅** | ? | ✅ dados | ✅ dados | ✅ dados | ✅ dados | ✅ dados | ? | ? | ? | ? |
| `meeting-portal-integration-build-dr7jqr` | sem push | | | | | | | | | | | | | |
| `meeting-portal-final-pabok2` | sem push | | | | | | | | | | | | | |

`✅ dados` = provado na camada de dados; a coluna só fecha com a tela medida.

```
MEETING_BUILD_HEAD a54e287 · DEPLOY_STATE nenhum · MEETING_FREEZE NO
```

---

## CICLO 04 · 02:29Z — a dona avançou, e eu tinha classificado errado

```
MEETING_PREVIOUS_HEAD  a54e287
MEETING_NEW_HEAD       8f37e36
COMMIT_RANGE           a54e287..8f37e36   (3 commits, fast-forward)
```

**Correção da minha classificação do ciclo 03.** Tratei
`claude/meeting-portal-contradictions-qb5a1x` como CANDIDATA. Não era: partiu de
`a54e287` e acabou de ser aterrissada na branch da dona por fast-forward. Era a
continuação da própria dona numa branch de trabalho.

```bash
git rev-parse origin/claude/meeting-intelligence-integration \
              origin/claude/meeting-portal-contradictions-qb5a1x
# 8f37e365fa3fbb9a27c3227f9c2edfce0d9e2ad5   (o mesmo commit)
git merge-base --is-ancestor a54e287 origin/claude/meeting-intelligence-integration  # ✅
git merge-base --is-ancestor a14b9e1 origin/claude/meeting-intelligence-integration  # ✅
```

Nada foi perdido e a casca visual está inteira. **A auditoria que fiz no ciclo 03
é, portanto, a auditoria da integração da dona** — que era exatamente o que o
protocolo mais queria medir.

```
ADAPTER_BOUNDARY = PASS_DECLARED_SCHEMA_ADAPTATION   (IT e EN)
DECISION_FIELDS_CHANGED_BY_FRONTEND = 0
```

O portal da dona agora carrega `meeting-surface.js` + `meeting-labels.js` +
o snapshot. **Itens 1, 2, 4 e 5 do caminho crítico: feitos.**

### O controle que evitou um relatório falso

`run.mjs` na dona dá **66/71**, com B3 · H3 · W2 · O1 · DS1 vermelhos. Antes de
reportar isso como defeito, medi a base visual congelada:

```bash
git worktree add --detach <tmp> a14b9e1 && cd <tmp>/italia-portale && node audit/run.mjs
# 66/71 passing · 5 failing — B3, H3, W2, O1, DS1 · os mesmos cinco
```

    A BASE CONGELADA, QUE PASSOU BRANDWELL E MOBILE, JÁ FALHAVA ESTES CINCO.
    NENHUM DOS DOIS INTRODUZIU REGRESSÃO.

As cinco dependem do pacote `build/ITALY-REALITY-HANDOFF-V2.1/`, que é ignorado
pelo git e precisa ser reconstruído na canônica. `W2` e `O1` chegam a lançar
exceção por isso. Sem este controle eu teria acusado a dona de quebrar cinco
portões que ela nunca tocou.

Pelo mesmo motivo, `SNAPSHOT_SOURCE_HEAD_VALID` falha no `meeting-gate.mjs` da
dona (19/20) dizendo, com todas as letras, *«package not rebuilt in this tree —
BUILD_ID not reconciled»*. É artefato da minha árvore, não da integração: o
snapshot declara `SOURCE_HEAD b3935bd`, medido.

### A candidata que resta, e o que ela é

`claude/meeting-portal-integration-build-dr7jqr` → `8c316e2` parte de `a54e287` e
**não** contém `8f37e36`. É implementação paralela genuína: a superfície vive
dentro de `portale.html` (+954), não num módulo à parte.

| | dona `8f37e36` | candidata `8c316e2` |
|---|---|---|
| 43 no ecrã | ✅ 43 renderizados | ✅ 43 `cCards`, 43 ids únicos, todos dos 43 |
| gate próprio | 19/20 (a falha é a árvore) | **21/21, exit 0** |
| `run.mjs` | 66/71 = base | 66/71 = base |
| fronteira do dado | **PASS** pelo meu auditor, IT+EN | rótulos bijetivos com os códigos |
| 26 sem produto principal | 26/26 nulos preservados | 0 coroados indevidamente; 17/17 corretos |
| códigos internos no modelo | preserva código + rótulo | **só rótulo** — mais forte em `NO_INTERNAL_CODES` |
| auditável de fora | **sim** — expõe `build()` | não — precisei do harness dela |

Os 12 casos da candidata sem a nota «nenhum principal» são os 12 **sem produto
nenhum**: mostram «nessun prodotto». Correto, não defeito.

### Os gates não são transferíveis — cada um se avaliou com o próprio exame

```
gate da dona rodando na candidata  → TypeError: SURF.build is not defined
gate da candidata rodando na dona  → TypeError: vIT.cCards is undefined
```

Por isso 19/20 e 21/21 **não se comparam**. O único instrumento neutro é
`audit_adapter_boundary.py` contra a referência congelada — e é ele que sustenta
as linhas «fronteira do dado» e «26 sem produto principal» acima.

### O que ainda falta na dona

`meeting-browser.mjs` não foi executado (1440/390, IT/EN) · brandwell · mobile ·
cta-navigation · internal-token na tela · deploy. É o ciclo 05.

```
MEETING_BUILD_HEAD 8f37e36 · DEPLOY_STATE nenhum · MEETING_FREEZE NO
```

---

## CICLO 05 · 03:15Z — a tela, provada num browser de verdade

### 1 · O pacote reconstruído, com proveniência

Worktree próprio em `b3935bd`, `bash scripts/v21_cadeia.sh`, e depois
`git checkout --detach 8f37e36` **no mesmo tree** — o pacote é ignorado pelo git
e sobrevive à troca de HEAD. É o procedimento do handoff, e é o que dá
proveniência: nada foi copiado de outra árvore.

```
BUILD_ID   V21-358954754db5ea2f      (esperado V21-358954754db5ea2f)
RECORDS    43                        (esperado 43)
R2 · CONTRATO DE PROCEDENCIA — 7169 registros checados, VIOLACOES: 0
```

**A cadeia é reprodutível.** Mesmos inputs, mesmo `BUILD_ID`.

### 2 · Os cinco gates antigos, sob condição idêntica

Mesmo tree, mesmo pacote, só o código muda:

| | `a14b9e1` base | `8f37e36` dona |
|---|---|---|
| `run.mjs` | 66/71 | 66/71 |
| B3 · H3 · W2 · O1 · DS1 | 1 · 3 · 1 · 1 · 1 | 1 · 3 · 1 · 1 · 1 |

    IDÊNTICO SOB CONDIÇÃO IDÊNTICA. REGRESSÃO = NENHUMA.

Com o pacote, `W2` e `O1` deixam de lançar exceção e passam a dar valor real — e
ainda assim os dois lados batem. São dívidas anteriores da base congelada, não da
integração da reunião.

### 3 · `meeting-gate.mjs` na dona, com pacote · **20/20**

`SNAPSHOT_SOURCE_HEAD_VALID` passou. A falha do ciclo 04 era mesmo a minha
árvore sem pacote, como estava escrito lá.

Todas as testemunhas obrigatórias do §13 verdes: `CANONICAL_43_RENDERED`
(43 · total 43) · `CANONICAL_COUNTS_FROM_43_ONLY` · `NO_RAW_BYPASS` ·
`NO_FRONTEND_INTELLIGENCE_RECALCULATION` · `PRIMARY_MATCH_SINGLE_OWNER` ·
`NO_PRIMARY_WHEN_UNKNOWN` · `WINDOW_SINGLE_OWNER` ·
`WINDOW_DEFINED_OPEN_SEPARATED` · `ALL_PORTFOLIO_MATCHES_RENDERED` ·
`WHY_COMMERCIAL_RENDERED` · `WHY_NOW_RENDERED` · `ACTION_MAP_FROM_ENGINE` ·
`EVIDENCE_ROLE_RENDERED` · `VALIDATION_STATE_NOT_HIDDEN` ·
`DEEP_NESTED_INTERNAL_TOKEN_FILTER` · `IT_LABELS_COMPLETE` ·
`EN_LABELS_COMPLETE` · `DEMO_AND_CANONICAL_SEPARATED`.

### 4 · `meeting-browser.mjs` · **11/11**, 20 percursos

`CONSOLE_ERRORS 0` · `FAILED_REQUESTS 0` · `DEAD_CONTROLS 0` ·
`NO_INTERNAL_TOKEN_ON_SCREEN 0` · `NO_PORTUGUESE_ON_SCREEN 0` ·
`REACHABLE_IT_EN_DESKTOP_MOBILE 0`.

### 5 · Os 43 no DOM — medido por mim, não pelo gate da dona

O gate prova que os casos da demo são alcançáveis. Não prova que os 43 chegam.
Medi separadamente, abrindo o radar e premindo `[data-meeting-more]` até esgotar:

```
1440 it  cards 43 · únicos 43 · faltando 0 · alheios 0 · 1 clique · errors 0
1440 en  cards 43 · únicos 43 · faltando 0 · alheios 0 · 1 clique · errors 0
 390 it  cards 43 · únicos 43 · faltando 0 · alheios 0 · 1 clique · errors 0
 390 en  cards 43 · únicos 43 · faltando 0 · alheios 0 · 1 clique · errors 0
```

    CANONICAL_CASES_RENDERED = 43   ·   ALHEIOS AOS 43 = 0

As 24 do primeiro ecrã são paginação com controlo, não truncagem: um clique
revela os 19 restantes.

### 6 · Os cinco casos da demo, abertos de verdade

```
DEMO_5_NO_BROWSER = PASS   (1440 e 390 × IT e EN = 20 aberturas)
tokens internos 0 · prosa PT 0 · console 0 · requests falhados 0
conteúdo por caso: 4.1 KB a 6.6 KB
```

### 7 · O ACHADO QUE MUDA O QUE SE PODE PROMETER NA REUNIÃO

O §8 pede provar um `WEAKENS` e um `CONTRADICTS`/`CLOSES` na tela. **Não é
possível — e a UI não tem culpa:**

```python
papéis de evidência nos 43:
  SUPPORTS_PRODUCT_MATCH 200 · SUPPORTS_COMMERCIAL_ACTION 61 · BACKGROUND_ONLY 53
  SUPPORTS_SIGNAL 29 · SUPPORTS_DIRECTION 17 · SUPPORTS_WINDOW 12 · SUPPORTS_REGIONAL_CONTEXT 12
  WEAKENS 0 · CONTRADICTS 0 · CLOSES 0
```

**O motor não emite papel de evidência negativo neste snapshot.** A tela não pode
mostrar o que não existe, e inventar seria a violação exata que a madrugada
inteira esteve a impedir.

**Mas a inteligência negativa existe — noutro campo, e é forte:**

| campo | valores que esfriam |
|---|---|
| `NEED_DIRECTION` | `NO_ACTION_RECOMMENDED` 3 · `TREATMENT_PROHIBITED` 2 · `WINDOW_CONCLUDED` 2 · `ACTION_SUSPENDED` 1 |
| `ACTION_RECOMMENDATION_STATE` | `NOT_NEEDED_DECLARED` 3 · `PROHIBITED_DECLARED` 2 · `CONCLUDED_DECLARED` 2 · `SUSPEND_RECOMMENDED` 1 |
| `WHY_COMMERCIAL_CODES` | `NEED_CLOSED` |

E o caso da Umbria é a demonstração perfeita, por quatro campos ao mesmo tempo:

```
OPP_169BD86DB324   NEED_DIRECTION              NO_ACTION_RECOMMENDED
                   ACTION_RECOMMENDATION_STATE NOT_NEEDED_DECLARED
                   PEST_STAGE_STATE            STAGE_DECLINING
                   WHY_COMMERCIAL_CODES        NEED_CLOSED
                   STATUS                      WATCH
```

    NA REUNIÃO, NÃO PROMETER «EVIDÊNCIA QUE CONTRADIZ».
    MOSTRAR «A FONTE DIZ QUE NÃO É PRECISO INTERVIR» — QUE É REAL, E É MAIS FORTE.

### 8 · Uma coisa a vigiar: o ecrã de demonstração continua contraditório

O gate da dona mede o canônico **e** o legado, e diz:

```
PRIMARY_MATCH_SINGLE_OWNER      real 0 · legacy 14
WINDOW_SINGLE_OWNER             real 0 · legacy 43
WINDOW_DEFINED_OPEN_SEPARATED   real 0 · legacy 48
```

A superfície canônica está limpa. **O ecrã dos 21 casos de demonstração não
está** — mantém as contradições antigas de produto principal e de janela. Estão
separados e não contaminam nenhum número dos 43, que era a exigência. Mas se
alguém abrir o radar de demonstração durante a reunião, verá as contradições que
a superfície nova resolveu.

**Recomendação: apresentar apenas o Radar Canônico.** Não é defeito a corrigir
esta noite — é uma tela a não abrir.

### 9 · Três vezes medi mal antes de medir bem

O meu script dos 43 deu `0 cards` e `3 console errors` enquanto o gate oficial
dava 24 e zero. Não era o portal: era `file://` em vez do servidor HTTP; depois
o rótulo `'RADAR CANONICO'` em vez de `'Radar Canonico'`; depois `openCase` em
vez de `openMeetingCase`. Nas três, o instinto certo foi desconfiar do
instrumento antes do objeto.

    CINCO VEZES ACREDITEI QUE O PORTAL ESTAVA PARTIDO, E ERA EU A MEDIR MAL.
    A FRASE JÁ ESTAVA NO REPOSITÓRIO. AGORA ESTÁ MEDIDA.

### 10 · A candidata `8c316e2` — não substituir

`8f37e36` mantém precedência: está na branch oficial, passou a auditoria contra a
referência congelada, preservou os 29 campos decisórios e os 26 `PRIMARY_MATCH`
nulos, e agora passa 20/20 + 11/11 + os 43 no DOM. **Nenhum defeito concreto do
browser da dona ficou por resolver.** Sem defeito, não há cherry-pick a fazer.

### Estado

```
MEETING_BUILD_HEAD              8f37e36
ADAPTER_BOUNDARY                PASS_DECLARED_SCHEMA_ADAPTATION
DECISION_FIELDS_CHANGED         0
CANONICAL_CASES_RENDERED        43   (1440/390 × IT/EN)
MEETING_GATE                    20/20
MEETING_BROWSER                 11/11
REGRESSION vs a14b9e1           NENHUMA (condição idêntica)
DEMO_5_NO_BROWSER               PASS
NEGATIVE_EVIDENCE_ROLES         0 no motor — usar NEED_DIRECTION
DEPLOY_STATE                    nenhum
MEETING_FREEZE                  NO   ← falta só deploy + smoke test
```

---

## CICLO 06 · 03:20Z — o merge das duas sessões, reauditado

```
MEETING_PREVIOUS_HEAD  8f37e36
MEETING_NEW_HEAD       e927cb9
COMMIT_RANGE           8f37e36..e927cb9   (4 commits)
  43d6109 01:40  lo snapshot diventa la voce: sedici AGIRE ORA erano due
  8d1e502 02:35  i portoni imparano la fonte che lo schermo ha gia cambiato
  8ce2bc1 02:36  gli strumenti di prova escono dal manifesto del deploy
  e927cb9 02:40  merge: due sessioni, la stessa missione — vince l'ecrã che la riunione apre
```

As duas implementações fundiram-se. `meeting-surface.js` saiu (−483),
`meeting-adapter.js` entrou (+426), e a arquitetura mudou: em vez de superfície
separada, o adaptador **enxerta** os 43 no modelo que o portal já usava.

`a14b9e1` e `8f37e36` continuam ancestrais. Sem reescrita.

### O commit que me fez parar tudo

«*sedici AGIRE ORA erano due*» — e o `meeting-intelligence-snapshot.json` aparece
alterado no diff. Era exatamente a regra que reprova sozinha. Medi antes de
qualquer outra coisa:

| | antes | depois |
|---|---|---|
| `SOURCE_HEAD` · `BUILD_ID` · `MEETING_CUTOFF` · `TOTAL_CASES` | — | **inalterados** |
| `GENERATED_AT` | `00:56:45Z` | `01:06:03Z` |
| `STATUS` · `PUBLICATION_STATE` · `WINDOW_DEFINED` · `WINDOW_OPEN_NOW` | — | **contagens idênticas** |
| campos alterados nos 43 casos | — | **NENHUM** |

    ACT_NOW CONTINUA 2. WINDOW_DEFINED CONTINUA 16.
    O COMMIT CORRIGIU NA DIREÇÃO CERTA: TIROU OS 16 DE ONDE APARECIAM COMO ACT_NOW.

O snapshot só foi regerado dez minutos depois. Alarme desarmado por medição.

### `ADAPTER_BOUNDARY = PASS_DECLARED_SCHEMA_ADAPTATION` · IT e EN

```
MEETING_ADAPTER.OK true · FAULTS [] · SOURCE_HEAD b3935bd · TOTAL_CASES 43
counts(): actNow 2 · windowDefined 16 · publishable 5 · validationRequired 38
DECISION_FIELDS_CHANGED_BY_FRONTEND = 0
PRIMARY_MATCH_NULL_REFERENCE = 26 · CLIENT_PRIMARY_MATCH_NULL = 26
```

Uma transformação nova, declarada depois de provada: `WINDOW_DEFINED` atravessa
como **booleano** (`"YES"` → `true`), fiel em 43/43, `true` em exatamente 16. O
auditor aprendeu `value_bool` e a bateria de violações continua reprovando.

### Gates no HEAD merged

| | resultado |
|---|---|
| `meeting-gate.mjs` | **14/14** |
| `browser.mjs` | **7/7** — sem JS fatal, sem `undefined`, sem `[object Object]`, sem português, sem bookkeeping |
| `run.mjs` | **67/71** — B3 · H3 · W2 · DS1 |

**`run.mjs` melhorou:** 66/71 na base e no HEAD anterior, **67/71** agora. `O1`
ficou verde. As quatro que restam são as mesmas da base congelada.

### O que o merge tirou, e que eu tive de provar sozinho

O exame encolheu de **20 para 14 testemunhas**. Saíram:

```
PRIMARY_MATCH_SINGLE_OWNER · NO_PRIMARY_WHEN_UNKNOWN
WINDOW_SINGLE_OWNER · WINDOW_DEFINED_OPEN_SEPARATED · DEMO_AND_CANONICAL_SEPARATED
```

E `meeting-browser.mjs` foi apagado (−244), levando com ele o percurso pelos
casos da demo.

**As propriedades continuam válidas — medi-as por fora:**

```
26/26 PRIMARY_MATCH nulos preservados          (auditor contra a referência)
ITALY_APP_MODEL…opportunities.records = 43     attached: true
cartões no ecrã inicial: 12 · canônicos 12 · legados 0 · tokens internos 0
nav: «RADAR DELLE OPPORTUNITÀ» separado de «AMBIENTE DIMOSTRATIVO»
```

    AS PROPRIEDADES SEGURAM. O EXAME QUE AS GUARDAVA, NÃO.
    QUEM TOCAR NISTO DEPOIS DA REUNIÃO NÃO SERÁ AVISADO PELO PRÓPRIO REPOSITÓRIO.

Não é motivo para bloquear a reunião. É dívida a registar.

### O QUE EU **NÃO** PROVEI NESTE HEAD

No HEAD anterior medi os 43 no DOM nas quatro combinações. **Aqui não consegui:**
a navegação mudou com o merge e os meus seletores não alcançaram o radar cheio.
O que ficou provado é o modelo (43 registros, `attached`) e o ecrã inicial (12
cartões, todos canônicos, zero legados).

Não vou declarar `CANONICAL_CASES_RENDERED = 43` neste HEAD com base no anterior.
**Fica em aberto**, e é a primeira coisa do ciclo 07 — com os seletores da própria
branch, não com os meus.

### Estado

```
MEETING_BUILD_HEAD          e927cb9
ADAPTER_BOUNDARY            PASS_DECLARED_SCHEMA_ADAPTATION (IT e EN)
DECISION_FIELDS_CHANGED     0
SNAPSHOT                    inalterado exceto GENERATED_AT
MEETING_GATE                14/14   (era 20/20 com 20 testemunhas)
BROWSER                     7/7
run.mjs                     67/71   (base: 66/71 — melhorou)
43_NO_DOM                   NÃO PROVADO neste HEAD
DEPLOY_STATE                nenhum
MEETING_FREEZE              NO
```
