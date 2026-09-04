# HANDOFF · BUILD DA REUNIÃO — onde parou, e o que falta

> Para colar como primeira mensagem numa conta Claude nova.
> **Não confie em nada daqui sem medir.** Cada número tem um comando ao lado.

```
REPOSITÓRIO   lucianodalondon-sys/eame-sintonia
BRANCH         claude/meeting-intelligence-integration
HEAD           a15ac4e
ESTADO         PARCIAL — snapshot pronto, portal ainda NÃO integrado
```

---

## 0 · Os três HEADs, e o que cada um é

| papel | branch | HEAD | o que é |
|---|---|---|---|
| **inteligência canônica** | `claude/opportunity-commercial-priority-v1` | `b3935bd` | o motor, os 43 casos, a catraca. `UNIVERSAL_INTELLIGENCE_RECONCILIATION = PASS` |
| **base visual (congelada)** | `claude/site-v21-ingest-recovery` | `a14b9e1` | BrandWell PASS, mobile PASS, journey PASS. **NÃO REDESENHAR** |
| **build da reunião** | `claude/meeting-intelligence-integration` | `a15ac4e` | criada de `a14b9e1` + o snapshot |

```bash
git fetch --all
git log --oneline -1 b3935bd a14b9e1 origin/claude/meeting-intelligence-integration
git merge-base --is-ancestor a14b9e1 HEAD && echo "a casca visual esta inteira"
```

---

## 1 · A COISA MAIS IMPORTANTE DESTE HANDOFF

O pacote da inteligência **não está no git** — `build/ITALY-REALITY-HANDOFF-V2.1/`
é ignorado. Ele é reconstruído. E ele é construído numa branch e consumido em
outra.

    O PACOTE SOBREVIVE AO `git checkout` PORQUE É IGNORADO.
    É ISSO QUE PERMITE CONSTRUIR NA CANÔNICA E LER NA VISUAL.

**A sequência exata, e ela não é adivinhável:**

```bash
# 1 · construir o pacote na inteligência canônica
git checkout claude/opportunity-commercial-priority-v1     # b3935bd
bash scripts/v21_cadeia.sh                                  # ~40s
python3 -c "import json;d=json.load(open('build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/OPPORTUNITIES.json'));print(d['BUILD_ID'],len(d['RECORDS']))"
# esperado: V21-358954754db5ea2f 43

# 2 · voltar para a branch da reunião — o pacote continua lá
git checkout claude/meeting-intelligence-integration

# 3 · gerar o snapshot, declarando o HEAD da INTELIGÊNCIA
python3 scripts/meeting_snapshot.py --source-head b3935bd --cutoff 2026-09-04T00:52:54Z
```

⚠️ `--source-head` é obrigatório e validado. Sem ele o script para. `git rev-parse
HEAD` na branch da reunião devolveria `a14b9e1`, e o snapshot declararia uma
procedência que não é a sua.

---

## 2 · O QUE JÁ ESTÁ FEITO

### `scripts/meeting_snapshot.py` · o snapshot client-safe ✅

Gera `italia-portale/client/meeting-intelligence-snapshot.{json,js}`
(`window.MEETING_INTELLIGENCE`). Lista de PERMISSÃO campo a campo — copia o que
o motor já decidiu, **não recalcula nada**.

```
SOURCE_HEAD     b3935bd
BUILD_ID        V21-358954754db5ea2f
MEETING_CUTOFF  2026-09-04T00:52:54Z
TOTAL_CASES     43

BY_STATUS               WATCH 22 · TO_VALIDATE 9 · FUTURE_PREPARATION 7
                        VALIDATE_NOW 3 · ACT_NOW 2
BY_COMMERCIAL_PRIORITY  TO_VALIDATE 17 · COMMERCIAL_WATCH 13
                        STRATEGIC_OPPORTUNITY 8 · SALES_READY 5
BY_PUBLICATION_STATE    VALIDATION_REQUIRED 38 · PUBLISHABLE 5
BY_WINDOW_DEFINED       NO 27 · YES 16
BY_WINDOW_OPEN_NOW      UNKNOWN 41 · YES 2
BY_WINDOW_RULE_STATE    NOT_DECLARED 26 · DECLARED 15
                        DELEGATED_TO_FARM 1 · ADMINISTRATIVE_ONLY 1
```

**Lei que ele aplica e que não pode ser afrouxada:** prosa de pesquisa em
português **não atravessa como texto**. `WINDOW_CONDITION`, `NEED_EXCERPT`,
`PEST_STAGE_EXCERPT` e `ACTION_RECOMMENDATION_EXCERPT` atravessam só como
`CAMPO__PT_ONLY: true` mais o ID do documento.

    PROSA QUE NÃO EMBARCA NÃO VAZA.

A tela deve dizer «a condição está declarada no documento X» — que é verdade —
em vez de mostrar português a um italiano.

---

## 3 · O ACHADO QUE MUDA O PLANO — leia antes de escrever uma linha

O radar da base visual **não é alimentado pelo motor**. Medido:

```bash
sed -n '136,160p' italia-portale/BASELINE/italy-demo-data.js
grep -n "const opportunities = coll" -A 12 italia-portale/BASELINE/italy-app-model.js
```

`italy-app-model.js` monta `opportunities` a partir de **`D.CASES`** — 21+ casos
de apresentação escritos à mão (`IT-OPP-001…`), com `provenance: DEMO_SCENARIO`
e prosa rica (`happening`, `why`, `know`, `watch`, `timeline`, `primary`,
`products`, `stage`, `signal`, `label`, `evidence{}`). As oportunidades do motor
entram só como `upstreamOpportunities`, uma coleção lateral, e servem apenas para
marcar `isUpstreamReal`.

    O RADAR BONITO QUE PASSOU NOS GATES NÃO MOSTRA OS 43. ELE MOSTRA 21
    CASOS DE APRESENTAÇÃO.

**Consequência para a missão:** trocar a fonte do radar não é «ligar um JSON».
Os campos que os templates leem (`happening`, `know`, `watch`, `timeline`) **não
existem** no snapshot canônico e **não podem ser inventados**. Os que existem
(`WHY_COMMERCIAL_IT/_EN`, `WHY_NOW_CODES`, `PORTFOLIO_MATCHES`,
`ACTION_BY_DEPARTMENT`, `EVIDENCE_ROLES`, `WHAT_IS_MISSING`) não têm lugar nos
templates atuais.

**A decisão que estava tomada quando isto parou** — e que a conta nova deve
confirmar ou derrubar com evidência:

> Construir uma **superfície canônica nova** dentro da mesma casca BrandWell
> (mesmos tokens, mesma linguagem de cartão, categoria dominando a cor), 100%
> alimentada pelo snapshot, e roteá-la como o radar da reunião. O radar de
> demonstração **fica como está** e **não** é apresentado como canônico.
>
> Isso satisfaz: portal consome o snapshot · visual preservado · nada inventado ·
> os 43 casos com os campos novos. E não satisfaz literalmente o §13 do briefing
> («os cards do radar»), porque o card do radar atual pertence a outra fonte.
>
>     MISTURAR 21 CASOS DE DEMONSTRAÇÃO COM 43 CANÔNICOS NA MESMA GRADE
>     É A ÚNICA COISA QUE NÃO SE PODE FAZER.

---

## 4 · O QUE FALTA — na ordem

### 4.1 · `italia-portale/client/meeting-labels.js` (IT + EN) — **não começado**

Nenhum token interno pode aparecer na tela. O inventário completo já foi medido:

```
STATUS                ACT_NOW · VALIDATE_NOW · WATCH · TO_VALIDATE · FUTURE_PREPARATION
COMMERCIAL_PRIORITY   SALES_READY · STRATEGIC_OPPORTUNITY · COMMERCIAL_WATCH · TO_VALIDATE
ARCHETYPE             O1_FIELD_PRESSURE · O2_MARKET_MOMENT · O3_RESISTANCE_MOA
                      O4_COMPETITIVE_OPENING · O5_REGULATORY_PREPARATION · O6_SCIENCE_TO_FIELD
WINDOW_TYPE           PHENOLOGY_WINDOW · PREHARVEST_WINDOW · THRESHOLD_WINDOW
                      PEST_STAGE_WINDOW · WEATHER_TRIGGERED_WINDOW · RULE_DELEGATED_TO_FARM
WINDOW_RULE_STATE     RULE_DECLARED · RULE_ADMINISTRATIVE_ONLY
                      RULE_DELEGATED_TO_FARM · RULE_NOT_DECLARED
OPEN_NOW_METHOD       6 códigos (ver §4.1b)
NEED_DIRECTION        7 estados      PEST_STAGE_STATE 4      ACTION_RECOMMENDATION 7
THRESHOLD_STATE       2              WHY_NOW_CODES 6         WHAT_IS_MISSING 12
WHY_COMMERCIAL_CODES  9              EXTERNAL_BLOCKER 1      PUBLICATION_STATE 2
BRIEF codes           9              EVIDENCE_ROLES 7        WHY_CODE 13
ACTION                12             ACTION_STATE 5          DEPARTAMENTOS 5
PRIMARY_MATCH_REASON  2              FITS do produto 9
CROPS 12 · TARGETS 9 · GEOGRAFIAS 8
```

Reproduza o inventário exato com:

```bash
python3 - <<'PY'
import json
d=json.load(open('italia-portale/client/meeting-intelligence-snapshot.json',encoding='utf-8'))
C=d['CASES']
def uni(f):
    s=set()
    for c in C:
        v=f(c)
        if isinstance(v,(list,tuple,set)): s|={str(x) for x in v}
        elif v is not None: s.add(str(v))
    return sorted(s)
print('STATUS', uni(lambda c:c.get('STATUS')))
print('WINDOW_TYPE', uni(lambda c:c.get('WINDOW_TYPE')))
print('WINDOW_RULE_STATE', uni(lambda c:c.get('WINDOW_RULE_STATE')))
print('OPEN_METHOD', uni(lambda c:c.get('WINDOW_OPEN_NOW_METHOD')))
print('WHAT_IS_MISSING', uni(lambda c:c.get('WHAT_IS_MISSING')))
print('ROLES', sorted({e['ROLE'] for c in C for e in (c.get('EVIDENCE_ROLES') or [])}))
print('ACTION', sorted({v['ACTION'] for c in C for v in (c.get('ACTION_BY_DEPARTMENT') or {}).values()}))
print('WHY_CODE', sorted({v['WHY_CODE'] for c in C for v in (c.get('ACTION_BY_DEPARTMENT') or {}).values()}))
PY
```

#### 4.1b · As frases que o briefing pediu, palavra por palavra

O briefing é explícito sobre a linguagem. Estas não são sugestões:

| token | IT | EN |
|---|---|---|
| `RULE_DELEGATED_TO_FARM` | «La decisione dipende dall'osservazione in campo» | «The decision depends on farm-level observation» |
| `RULE_ADMINISTRATIVE_ONLY` | «Obbligo amministrativo — non è una finestra agronomica» | «Administrative obligation — not an agronomic window» |
| `PHENOLOGY_WINDOW` | «Finestra definita dallo stadio fenologico» | «Window defined by phenological stage» |
| `WINDOW_DEFINED=YES` + `OPEN_NOW=UNKNOWN` | «Condizione nota; stato attuale non ancora misurato» | «Condition known; current state not yet measured» |
| `WHY_NOW` com `CADEIA_COMPLETA` | «Finestra agronomica aperta» | «Agronomic window open» |
| `NEED_DIRECTION` restritiva | «La fonte raccomanda di monitorare, non di attivare» | «The source recommends monitoring, not activating» |
| `WEAKENS` | «Questa evidenza riduce l'urgenza commerciale» | «This evidence lowers the commercial urgency» |
| `CLOSES` | «Il monitoraggio non sostiene un'azione ora» | «Monitoring does not support action now» |

    UNKNOWN NUNCA PODE DESAPARECER ATRÁS DE COPY BONITA.

### 4.2 · A superfície canônica — **não começada**

Onde: `italia-portale/BASELINE/` **e** `italia-portale/client/` (são duas cópias;
ver §6). Carregar `meeting-intelligence-snapshot.js` + `meeting-labels.js`.

**Hero, sem scroll** (§5 do briefing): CROP · TARGET · REGION → STATUS → por que
é oportunidade → por que agora / por que ainda não → **TODOS** os
`PORTFOLIO_MATCHES` → o que falta.

⚠️ `PRIMARY_MATCH` só é principal quando existe regra defensável. Medido no
snapshot: `PRIMARY_MATCH_REASON` é `SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER` na
maioria. **Nesses casos não há principal visual.** Nunca `PRIMARY + N MORE`
quando o snapshot conhece todos.

Por produto (§6): `PRODUCT_NAME` · `ACTIVE_INGREDIENTS` · `MODE_OF_ACTION` ·
`CROP_FIT` · `TARGET_FIT` · `REGULATORY_FIT` · `WINDOW_FIT` · `VALIDATION_STATE`
· `MATCH_REASON` · `RESTRICTIONS`.

Mapa de ação (§10): exatamente `ACTION_BY_DEPARTMENT` — 5 departamentos, cada um
com `ACTION_STATE` · `ACTION` · `WHY_CODE` · `DEPENDENCY` · `NEXT_TRIGGER`.
Sequência QUEM AGE → QUEM VALIDA → QUEM PREPARA → O QUE DESTRAVA. **Não inventar
sequência que a inteligência não dá.**

Inteligência negativa (§12): `EVIDENCE_ROLES` com `WEAKENS` / `CONTRADICTS` /
`CLOSES` de forma clara e elegante — é demonstração de inteligência, não defeito.

### 4.3 · Gates — **não começados**

Rodar os que já existem:
```bash
cd italia-portale && node audit/run.mjs && node audit/acceptance.mjs
node audit/browser.mjs   # precisa de Chromium; ver §7
```
E acrescentar as testemunhas nomeadas no §19 do briefing:
`MEETING_SNAPSHOT_CONTRACT` · `SNAPSHOT_43_CASES` · `NO_RAW_BYPASS` ·
`SNAPSHOT_FROM_b3935bd` · `ALL_PORTFOLIO_MATCHES_RENDERED` ·
`WHY_COMMERCIAL_RENDERED` · `WHY_NOW_RENDERED` · `WINDOW_STATE_RENDERED` ·
`ACTION_MAP_FROM_ENGINE` · `EVIDENCE_ROLE_RENDERED` ·
`VALIDATION_STATE_NOT_HIDDEN` · `NO_INTERNAL_CODES` · `NO_PARTIAL_INPUT_USED`.

### 4.4 · Browser + deploy — **não começados**

Chromium está pré-instalado (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`).
**Nunca** rodar `playwright install`. Testar 1440 e 390, IT e EN, percorrendo
HOME → RADAR → OPORTUNIDADE → WHY COMMERCIAL → PRODUCTS → WHY NOW → ACTION MAP →
EVIDENCE → SOURCE.

Deploy: branch `claude/meeting-intelligence-integration`, diretório
`italia-portale/client/`. **Não declarar READY porque o deploy retornou sucesso
— abrir o domínio servido e comparar com o arquivo local.**

---

## 5 · OS SEIS CASOS DA DEMO, com os IDs já medidos

| | caso | `OPPORTUNITY_ID` | o que ele demonstra |
|---|---|---|---|
| **A** | botrite × videira × Emilia-Romagna | `OPP_5F31A63F844D` | `ACT_NOW` · `PREHARVEST_WINDOW` · `OPEN_NOW=YES` por `ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO` · `PUBLISHABLE` |
| **B** | botrite × videira × Toscana | `OPP_F8106D5E1767` | `ACT_NOW` sustentado; a frase «maggior suscettibilità» prova **um** elo só |
| **C** | tignoletta × videira × Umbria | `OPP_169BD86DB324` | `WATCH` · a fonte diz «non sono necessari interventi» — evidência que esfria |
| **D** | carpocapsa × macieira × Veneto | `OPP_75C37DED9160` | `PEST_STAGE_STATE=STAGE_ENDED` **e** `ACTION_RECOMMENDATION_STATE=CONTINUE_RECOMMENDED` — **sem confundir os dois** |
| **E** | o mesmo `OPP_75C37DED9160` | | `RULE_DELEGATED_TO_FARM` em linguagem humana |
| **F** | escafoide × videira × Toscana | `OPP_D11664591168` | `RULE_ADMINISTRATIVE_ONLY` — obrigação de norma, não janela agronômica |

```bash
python3 - <<'PY'
import json
d=json.load(open('italia-portale/client/meeting-intelligence-snapshot.json',encoding='utf-8'))
ids=('OPP_5F31A63F844D','OPP_F8106D5E1767','OPP_169BD86DB324','OPP_75C37DED9160','OPP_D11664591168')
for c in d['CASES']:
    if c['ID'] in ids:
        print(c['ID'], c['CROP'], c['TARGET'], c['GEOGRAPHY'], c['STATUS'],
              c.get('WINDOW_TYPE'), c.get('WINDOW_OPEN_NOW'), c.get('PUBLICATION_STATE'))
PY
```

---

## 6 · ARMADILHAS QUE VÃO CUSTAR TEMPO SE NINGUÉM AVISAR

1. **Há DUAS cópias do portal.** `italia-portale/BASELINE/` (referência, com os
   relatórios) e `italia-portale/client/` (o que é servido, com `vercel.json`,
   `italy-handoff-v21.js` de 5,9 MB e `italy-pdf.js`). Elas **não** são idênticas
   — `italy-app-model.js` tem 20 KB numa e 283 KB na outra. Editar só uma é a
   forma mais rápida de a tela servida não mudar.

2. **`italy-i18n.js` é o dicionário do portal** (94 KB no client). Labels novas
   deveriam entrar ali ou num arquivo próprio carregado depois — decidir e
   declarar, não espalhar.

3. **O snapshot tem 433 KB de JS.** O `portale.html` do client já carrega 5,9 MB
   de handoff. Medir o custo antes de somar mais.

4. **`build/ITALY-REALITY-HANDOFF-V2/`** (sem o `.1`) **é versionado** e difere
   entre as branches. É a PORTA da coleta. Não confundir com o pacote de saída.

5. **A suíte de Python não roda nesta branch** com os números da canônica — a
   branch da reunião veio de `a14b9e1`, que é anterior. Os gates aqui são os do
   `italia-portale/audit/`, em node.

---

## 7 · O QUE NÃO SE FAZ (do briefing, verbatim)

```
NOVA COLETA = NÃO          PORTAL VISUAL: NÃO REDESENHAR
THRESHOLDS = NÃO ALTERAR   SEGUNDO MOTOR = NÃO CRIAR
PRODUÇÃO = NÃO TOCAR       MERGE EM MAIN = NÃO
```

O portal **não recalcula** `STATUS`, `COMMERCIAL_PRIORITY`, `WHY_NOW`,
`WINDOW_DEFINED`, `WINDOW_OPEN_NOW`, `WINDOW_TYPE`, product match, evidence role,
action map nem `PUBLICATION_STATE`. **Ele só apresenta.**

Fica para depois da reunião: os 14 casos que dependem de medição no pomar ·
arroz × giavone · os 16 registros sem coleção · ISTAT 2026 · a política
`AREA_OFICIAL_ANO` (`DECISION_REQUIRED`, e **nenhum** dos 43 usa área hoje).

`PUBLISHABLE 5 / VALIDATION_REQUIRED 38` **não** vira «mostrar 5 e esconder 38».
Pode-se mostrar os que estão em validação — desde que o estado apareça, e nenhum
`VALIDATION_REQUIRED` seja apresentado como afirmação validada.

---

## 8 · MEETING_FREEZE

Ainda **NÃO**. Declarar só quando: snapshot estável + portal integrado + gates
verdes + casos da demo verificados no browser + deploy aberto e testado.

Depois disso nada novo entra; o que terminar depois entra por BACKFILL.

---

## 9 · A ENTREGA QUE A REUNIÃO ESPERA

```
MEETING_PORTAL_READY = YES / PARTIAL / NO
CANONICAL_INTELLIGENCE_HEAD = b3935bd
VISUAL_BASE_HEAD            = a14b9e1
MEETING_CUTOFF              = 2026-09-04T00:52:54Z
MEETING_SNAPSHOT_BUILD      = V21-358954754db5ea2f
PORTAL_INTEGRATION_HEAD     = ?
DEPLOY_URL                  = ?
TOTAL_CASES 43 · PUBLISHABLE 5 · VALIDATION_REQUIRED 38
ACT_NOW 2 · VALIDATE_NOW 3 · WATCH 22 · TO_VALIDATE 9 · FUTURE_PREPARATION 7
WINDOW_DEFINED 16 · WINDOW_OPEN_NOW 2

PARTIAL_INPUT_CONSUMED = NO   NEW_COLLECTION_STARTED = NO
THRESHOLDS_CHANGED = NO       SECOND_ENGINE_CREATED = NO
VISUAL_REDESIGN = NO          RAW_EVIDENCE_CHANGED = NO
MEETING_FREEZE = ?
```

**Estado honesto neste handoff: `MEETING_PORTAL_READY = NO`.** O snapshot existe
e está correto. O portal ainda não o consome.
