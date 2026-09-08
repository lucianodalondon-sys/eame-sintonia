# REGISTO DE PRODUTOS E FERRAMENTAS — DRAFT

```
DOCUMENT_STATUS      DRAFT
DOCUMENT_TYPE        LIVING PRODUCT REGISTRY
REGISTRY_VERSION     R0.1
MEASURED_AT          2026-09-08
PORTAL_HEAD          a4fb6d8 · claude/visible-intelligence-v1
IMPLEMENTATION       NONE
```

> **Este é o ficheiro que MUDA.**
> Mudar aqui **não é** emendar a Constituição. Uma ferramenta pode nascer, mudar de
> classe, fundir-se, ser reclassificada ou aposentada **sem que uma linha da Bíblia se
> altere** — desde que a mudança passe pelo Tool Admission Gate e fique registada.
>
> Toda alteração exige, no mínimo: `WHAT_CHANGED` · `WHY` · `DATE`.
> Toda mudança de ciclo de vida exige, além disso: `FROM_STATE` · `TO_STATE` · `EVIDENCE`.

---

## §1 · REGISTO DE INTELLIGENCE PRODUCTS

Onze produtos identificados. `PRODUCT_ID` é **proposto** — nenhum existe hoje como
identificador no código.

| PRODUCT_ID | o que é | LIFECYCLE | selo | `FORBIDDEN_CLAIMS` escritos? | superfícies que serve |
|---|---|---|---|---|---|
| `LABEL_AUTHORISED_USE` | 166 produtos · 210 objetos · 54 versões · 22 regras · `REGRAS.md@5` | `ACTIVE` | **`CONTENT_SHA256`** | **SIM — 4 famílias + G-01** | S-04 · S-01 · S-02 |
| `COMMERCIAL_PRIORITY_CASE` | 43 casos · classes A–E · `SO_A_PUBLICA` | `ACTIVE` | portão 7/7 + 19 testes | PARCIAL (`nunca SALES OPPORTUNITY`) | S-01 · Home |
| `PRODUCT_PORTFOLIO` | 173 produtos · 5402 relações · `STRENGTH` 4 níveis | `ACTIVE` | não | não | S-02 · S-01 |
| `COMPETITOR_OBSERVATION` | 577 · 5 estados que não se somam · 5º relógio | `ACTIVE` | não | **SIM, no contrato de dado** | S-08 |
| `MARKET_PRICE_SERIES` | 157 observações UE | `ACTIVE` | não | PARCIAL (classe temporal, migration 021 não executada) | S-06 |
| `SOURCE_PROVENANCE` | 194 fontes com estado, **incluindo as bloqueadas** | `ACTIVE` | `DATA-CLOCK-manifest` | não | S-11 · todas |
| `REGULATORY_EXPOSURE` | 163 registos + 47 factos + 28 futuros | `CANDIDATE` — **sem superfície própria** | não | SIM (`vencimento ≠ perda`, `EXPIRED ≠ WITHDRAWN`) | dentro de S-02 |
| `FUTURE_THEME` | 44 temas ITFC · régua 0–5 | `DEGRADED` — 12 de 13 campos não viajam | não | **SIM — `PALAVRAS_PROIBIDAS`** | S-03 · S-13 |
| `CROP_WINDOW` | 29 canónicas · **PROVED 0** · origem não auditável | `DEGRADED` | não | PARCIAL (`WINDOW_OPEN ≠ CURRENT_NEED`) | S-05 |
| `SCIENCE_CORPUS` | **763** no acervo · 88 servidos · 93.933 ch de abstract que não viajam | `DISCOVERED` | não | SIM (`recorrência ≠ autoridade`) | S-09 parcial |
| `FIELD_VOICE_CORPUS` | 79 vozes · 62 canais · **184 transcrições · 5.033.374 ch** | `DISCOVERED` | não | não | S-07 parcial |

```
PRODUTOS COM SELO CRIPTOGRÁFICO ......... 1 / 11
PRODUTOS COM FORBIDDEN_CLAIMS ESCRITOS .. 5 / 11
PRODUTOS EM DISCOVERED (chegam e morrem)  2 / 11
PRODUTOS SEM SUPERFÍCIE PRÓPRIA ......... 1 / 11   REGULATORY_EXPOSURE
```

> **`REGULATORY_EXPOSURE` é o achado mais silencioso deste registo.**
> É o produto que corresponde a **MT1** — a primeira das duas ferramentas principais da
> arquitetura — e **não tem superfície nenhuma**. Vive espalhado dentro do Portfolio.
> `MT1` é hoje uma pergunta sem tela.

---

## §2 · REGISTO DE DELIVERY PROJECTIONS

Seis potes existem. Nenhum se chama pote, e nenhum declara `IS_SOURCE_OF_TRUTH = false`.

| PROJECTION_ID | ficheiro | tamanho | `REBUILD_COMMAND` | `REBUILD_PROOF` | `DROPPED_FIELDS`? |
|---|---|---|---|---|---|
| `PORTAL_MODEL_V21` | `italy-handoff-v21.js` | 11,2 MB | `scripts/site_v21_ingest.py` | **byte-idêntico**, portão de proveniência | ✗ |
| `MEETING_SNAPSHOT` | `meeting-intelligence-snapshot.js` | 509 KB | `scripts/meeting_snapshot.py --source-head --cutoff` | `meeting-gate 23/23` | ✗ |
| `RELEVANCE_VERDICT` | `adama-relevance.js` | 8,8 KB | `adama_relevance.py` (lei) + `it_casa_dados.py` (transporte) | `adama-relevance-gate 7/7` | **✓** — `PER_CLASSE` publica os 26 recusados |
| `CASA_LEDGER` | `italy-casa.js` | 495 KB | `scripts/it_casa_dados.py` | `casa-gate 30/30` | parcial (`DERRUBADOS 1`) |
| `LABEL_PAYLOAD` | `italy-label-intelligence.js` | 3,8 MB | `v1/inteligencia/payload.py`, copiado byte a byte | `etichette-gate.mjs` recalcula o sha | **✓** — 7 coberturas + `coverage_note` |
| `DISPLAY_LAYER` | `italy-i18n.js` + `meeting-labels.js` | 167 KB | 103 regras em `DISPLAY-LAYER-V1.json` | `SEMANTIC_DRIFT_ERRORS = 0` | n/a |

```
PROJEÇÕES COM PROVA DE REGENERAÇÃO ...... 6 / 6    ← excelente
PROJEÇÕES COM DROPPED_FIELDS ............ 2 / 6
PROJEÇÕES COM IS_SOURCE_OF_TRUTH = false  0 / 6    ← a constante não existe
PROJEÇÕES COM AS_OF EXPLÍCITO ........... 2 / 6    MEETING_SNAPSHOT · LABEL_PAYLOAD
```

**Projeções que a Bíblia identifica como necessárias e que não existem:**

| PROJECTION_ID proposto | para quê | quem a pede |
|---|---|---|
| `HOME_QUEUE` | a fila de decisão da Home, com as 5 classes | §11.1 |
| `ASK_INDEX` | o índice consultável, com `FORBIDDEN_CLAIMS` herdados | §11.2 |
| `COMMERCIAL_BRIEF` | o que COM precisa: o que dizer, onde, com que produto | §16 |
| `MARKETING_ACTIVATION` | o que MKT precisa: par + `ACTIVATION_QUESTION` + o que **não** dizer | §16 |
| `CROSS_MARKET_VIEW` | a camada EAME — **hoje 0 relações, e tem de aparecer vazia** | `EAME-RELATIONSHIP-CONTRACT-V1` |

---

## §3 · REGISTO DE SUPERFÍCIES — ciclo de vida

| SURFACE_ID | nome | `SURFACE_CLASS` atual | `LIFECYCLE_STATE` | data de revisão | quem decide |
|---|---|---|---|---|---|
| S-01 | Opportunity Radar | `CANONICAL_TOOL` | `ACTIVE`, `DECISION_PROVED = NÃO` | após o primeiro piloto | dono do produto |
| S-02 | Portfolio | **`UNKNOWN`** — promovido sem registo | `ACTIVE` | **imediata** — AD-05 | dono do produto |
| S-03 | Future Radar | `EXPLORATORY_TOOL` | `ACTIVE` sobre produto `DEGRADED` | quando os 13 campos viajarem | dono do pacote a montante |
| S-04 | Label Intelligence | `CANONICAL_TOOL` *(recomendado)* / evidência *(código)* | `ACTIVE`, admitido como `EXPLORATORY` pelo Gate | 30 dias | dono do produto |
| S-05 | Crop Windows | `UNKNOWN` | `DEGRADED` | **bloqueada até aparecer o gerador** | quem tiver o gerador |
| S-06 | Market Pulse | `CONTEXT_VIEW` *(recomendado)* | `ACTIVE` | após telemetria | dono do produto |
| S-07 | Field Voices | `UNKNOWN` — 3 hipóteses vivas | **`CANDIDATE`** *(reaberto — ver §5)* | após baseline + denominador + GDPR | dono + jurídico |
| S-08 | Competitor Watch | `CROSS-CUTTING LAYER` + `INVESTIGATION_VIEW` | `ACTIVE` com violação de contrato no contador | **imediata** — o `577` | dono do produto |
| S-09 | Scientific Intelligence | `UNKNOWN` | `CANDIDATE` *(reaberto — ver §5)* | após medição de utilizador | dono + jurídico (P-008) |
| S-10 | Archive | `INVESTIGATION_VIEW` **ou** `ADMIN` | `ACTIVE` sem contrato | após nomear o público | dono do produto |
| S-11 | Source Register | `EVIDENCE_EXPLORER` | `ACTIVE` | conflito C-02 a resolver | dono do produto |
| S-12 | Field Sales Channel | `INTEGRATION` | **`EXPERIMENT`** | **`LC-04` exige data e não tem** | dono do produto |
| S-13 | Signal Archive | `SUPPORTING_VIEW` | `ACTIVE`, fora do menu | — | — |

### Superfícies em `RETIRED` que ainda renderizam

| id de vista | estado | evidência | o que falta |
|---|---|---|---|
| `case` | renderiza · lê `D.CASES` = 29 `DEMO_SCENARIO` | `legacyCaseId` null em **43/43** | data de saída |
| `brief` | renderiza · único `[data-download-pdf]` | idem | data de saída |
| `radar` · `mradar` | aliases aceites · `isRadar = false` | — | registo formal de `RETIRED` |

> **`LC-05` · «Deprecated» sem data é «current» com má consciência.**
> Quatro superfícies legadas sem data de saída.

---

## §4 · ESTADO DO TOOL ADMISSION GATE — as 16 perguntas, superfície a superfície

`✓` respondida com prova · `~` parcial · `✗` sem resposta

| # | pergunta | S-01 | S-02 | S-03 | S-04 | S-05 | S-06 | S-07 | S-08 | S-09 | S-10 | S-11 | S-12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | que decisão ajuda? | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ~ | ~ | ✗ | ~ | n/a |
| 2 | quem usa? | ✓ | ~ | ~ | ✗ | ✗ | ✗ | ✗ | ~ | ~ | ✗ | ~ | ~ |
| 3 | que problema distinto? | ✓ | ✗ | ✓ | ~ | ✗ | ✗ | ✗ | ✗ | ~ | ✗ | ✓ | ✓ |
| 4 | que inteligência consome? | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ~ | ✓ | ✗ |
| 5 | que produto entrega? | ✓ | ~ | ~ | ✓ | ✗ | ~ | ✗ | ~ | ~ | ✗ | ~ | ✗ |
| 6 | por que não é uma vista? | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| 7 | que evidência exige? | ✓ | ✓ | ~ | ✓ | ✗ | ✓ | ~ | ✓ | ~ | ✗ | ✓ | n/a |
| 8 | que frescor exige? | ✓ | ~ | ✗ | ✓ | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ | n/a |
| 9 | **que claim é proibido?** | ~ | ✗ | ✓ | **✓** | ~ | ~ | ✗ | ✓ | ✓ | ✗ | ✗ | n/a |
| 10 | como reage a `UNKNOWN`? | ✓ | ✓ | ✓ | ✓ | ✓ | ~ | ✓ | ✓ | ✓ | n/a | ✓ | n/a |
| 11 | como reage a conflito? | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ | n/a |
| 12 | como mede valor? | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| 13 | como corre em pilot? | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ~ |
| 14 | como é promovida? | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| 15 | como é fundida? | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| 16 | como é aposentada? | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| | **respondidas (✓)** | **10** | **3** | **7** | **9** | **1** | **4** | **2** | **7** | **5** | **0** | **8** | **2** |

```
NENHUMA SUPERFÍCIE RESPONDE ÀS 16.
As perguntas 12 a 16 — VALOR, PILOT, PROMOÇÃO, FUSÃO, APOSENTAÇÃO —
estão a ZERO em TODAS as doze.
```

> **Este é o buraco central da entrega, e ele é do MESMO tipo em toda a linha.**
> O SINTONIA sabe extraordinariamente bem responder «que evidência?», «que frescor?» e
> «como reages ao desconhecido?». **Não sabe responder a nenhuma pergunta de CICLO DE
> VIDA** — porque nunca teve onde a registar. É a razão de ser deste ficheiro.
>
> E as perguntas 12–16 são baratas: são **decisões escritas**, não engenharia.
> A 12 (`VALUE_MEASUREMENT`) é a única que exige construir algo — telemetria.

---

## §5 · FICHAS REABERTAS — as recusas que expiraram

Registo formal das reaberturas decididas na `MATRIZ §3`. **Reabrir não é promover.**

### R-01 · FIELD VOICES

```
FROM_STATE        CONCEPT — sem fonte de dado          (CATALOGO, 2026-08-28)
TO_STATE          CANDIDATE
DATE              2026-09-08
WHY               A recusa era de FONTE, não de ideia. A arquitetura nunca escreveu KILL:
                  escreveu «NOT REACHED / NÃO SEI, não KILL» e «Apify não foi testado.
                  É preciso testar antes de decidir».
EVIDENCE          79 vozes canónicas · 62 canais · 15 pessoas ·
                  184 transcrições · 5.033.374 caracteres de fala no acervo ·
                  resolução de cultura com missPct 1,3%
BLOCKERS          1. BASELINE — a régua de alerta não abre a porta BASELINE em nenhuma
                     família de conversa pública. Sem baseline, «o campo diz» não é
                     comparável com nada
                  2. DENOMINADOR — 79 de quantos? `CENSO E AMOSTRA NÃO SÃO A MESMA
                     AUSÊNCIA`
                  3. GDPR — P-008 e P-009 ABERTAS
NOT_PROMOTED      não sobe a ACTIVE nem entra na Home enquanto os três não fecharem
                  (A-02: uma superfície UNKNOWN não ganha autoridade nova)
```

### R-02 · SCIENTIFIC INTELLIGENCE

```
FROM_STATE        SUPPORTING ENGINE — «por baixo, não no menu»   (2026-08-29)
TO_STATE          CANDIDATE
DATE              2026-09-08
WHY               O contrato foi escrito quando o corpus era 88. É agora 763.
                  CAP-017 É uma decision question — de R&D e de TECHNICAL.
EVIDENCE          88 → 763 no acervo · 88/88 com link para o paper ·
                  `caseAdherence` · `countryOfFact` · o bloco «Cosa si sa oltre il caso»
                  com o luogo del fatto por linha
BLOCKERS          1. CAP-017 cobre FRANCE e SPAIN, **não cobre a ITÁLIA**
                  2. 39/88 são OFF_CASE; 87/88 batem QUERY_*, 37/88 batem PROVED_*
                  3. GDPR P-008: NAMED_RESEARCHER_PUBLIC_SCREEN =
                     BLOCKED_PENDING_LEGAL_REVIEW
NOT_PROMOTED      idem
```

### R-03 · SOURCE REGISTER

```
FROM_STATE        motor de suporte + «contador de fontes» proibido na home
TO_STATE          EVIDENCE_EXPLORER   (classe nova — §10 V-01)
DATE              2026-09-08
WHY               A proibição da HOME não é uma proibição da SUPERFÍCIE. Foram lidas
                  como a mesma coisa e não são.
EVIDENCE          `DESIGN-DATA-CONTRACT-V1` dá-lhe nível 2, ordem 4, com estados
                  GREEN/PARTIAL/BLOCKED e a nota «inclui as fontes BLOQUEADAS, com
                  motivo» — o que é conteúdo de produto, não admin
CONFLICT          C-02 permanece ABERTO: dois contratos da mesma semana discordam
```

### R-04 · COMPETITOR WATCH — releitura, não reabertura

```
FROM_STATE        «não é uma ferramenta isolada; não existe tela nem número único»
TO_STATE          CROSS-CUTTING LAYER + INVESTIGATION_VIEW
DATE              2026-09-08
WHY               O contrato proíbe o NÚMERO ÚNICO e o RANKING. Não proíbe a existência
                  de uma superfície de investigação sobre a camada.
                  Ler «não é ferramenta isolada» como «não pode haver ecrã» é uma leitura
                  MAIS DURA do que o texto.
WHAT VIOLATES     o `577` no menu. É um contador, não uma superfície.
                  E o `577` soma quatro naturezas que a arquitetura manda nunca somar.
ACTION            o contador sai, ou a superfície muda de classe. **Decisão do dono.**
```

### Placar das reaberturas

```
FERRAMENTAS DESCARTADAS SÓ PORQUE UM DOCUMENTO ANTIGO NÃO AS PREVIA ....... 0
TELAS PROMOVIDAS AUTOMATICAMENTE A FERRAMENTA POR EXISTIR DADO ............ 0
RECUSAS CONFIRMADAS APÓS REAVALIAÇÃO ..................................... 1   S-06
```

---

## §6 · REGISTO DE MUDANÇAS — as nove de 06/09 → 08/09, retroativamente registadas

**Nenhuma tem entrada no `DIARIO-DE-DECISOES.md`.** Ficam aqui, no formato que a
Constituição exige, para que o Registo Vivo comece com a história que já aconteceu.

```
RV-001  Opportunity Radar 13 → 17
        TYPE          SUPERSESSION BY LAW CHANGE  (§13 V-02)
        WHAT_CHANGED  a partição passou de 13/21/8/1 para 17/21/4/1
        WHY           a régua deixou de aceitar «alvo escrito no caso sem fonte que o
                      tenha observado» e passou a exigir SUPPORTS_SIGNAL ou
                      SUPPORTS_DIRECTION. Medido na própria lei: TARGET_FIT valia
                      ON_MINISTERIAL_LABEL em 65/65 — uma constante, que não distinguia
                      nada, e sobre a qual 10 dos 21 B subiriam sem nada observado
        EVIDENCE      adama-relevance.js · PER_CLASSE · LEGGE.PREENCHER_NAO_PROMOVE
        NOTE          OS MESMOS 43 CASOS. NENHUM FACTO MUDOU.
        DATE          ≤ 2026-09-07

RV-002  Portfolio → STRUMENTI
        TYPE          SURFACE_CLASS RECLASSIFICATION
        FROM_STATE    item de evidência        TO_STATE  ferramenta principal
        WHY           NÃO REGISTADO EM LADO NENHUM        ← o defeito AD-05
        EVIDENCE      const STRUMENTI = ['meeting', 'portfolio']
        ACTION        exige decisão retroativa do dono

RV-003  Future Radar entra no menu
        TYPE          SURFACE_LISTED: NO → YES
        WHY           VALUE_EXISTS = YES e VISIBLE = NO → NÃO ESTÁ INTEGRADO
        EVIDENCE      ROUTES_TO_FUTURE_RADAR = 0 antes; 44 depois; controlo negativo
                      corrido em worktree sobre 5a5ab60

RV-004  Label Intelligence nasce
        TYPE          TOOL ADMISSION
        TO_STATE      ADMITTED_AS_EXPLORATORY  (9 das 16 respondidas)
        EVIDENCE      CONTENT_SHA256 d27278de…3227bc4e · RULESET REGRAS.md@5 ·
                      FORBIDDEN_CLAIMS escritos no payload · portão G-01 fechado
        NOTE          a única superfície que passaria o Gate hoje

RV-005  Signal Archive sai da barra
        TYPE          SURFACE_LISTED: YES → NO   (SURFACE_EXISTS inalterado)
        WHY           «uma população que existe para ser explicada não pode ser a
                      primeira coisa que se vê»
        EVIDENCE      #future continua em AMMESSE, em CAPABILITY_OF, com 3 caminhos
        NOTE          RETIRAR DA VISTA ≠ RETIRAR DO PRODUTO

RV-006  Archivio fonti V21 → Source Register · 189 → 194
        TYPE          RENAME + POPULATION GROWTH
        WHY           não registado

RV-007  productRelationships 2030 → 5402
        TYPE          POPULATION GROWTH (+166%)
        WHY           não registado; sem PUBLICATION MANIFEST não há onde o declarar

RV-008  casa.html fundida em #radarfuturo
        TYPE          MERGED  (§9)
        WHY           «duas identidades visuais são dois produtos, mesmo quando são o
                      mesmo dado»
        EVIDENCE      o dado não mudou de dono (ITALY_CASA); mudou quem o desenha;
                      casa.html deixou de ser alcançável
        MISSING       FROM_STATE/TO_STATE formais · WHY_CHANGED · manifesto

RV-009  #field sai de AMMESSE, o item de menu fica
        TYPE          DEFECT   (AP-18 · MENU ENTRY WITHOUT ROUTE)
        STATUS        ABERTO
        EVIDENCE      AMMESSE não contém 'field'; navIntegrationItems continua a desenhar
        NOTE          a intenção do comentário e o comportamento do código discordam
```

---

## §7 · REGISTO DE EXPERIÊNCIAS

| id | o que é | estado | `LC-04` data de revisão | risco se ficar |
|---|---|---|---|---|
| `EXP-01` | Field Sales Channel — 18 mensagens `SYNTHETIC_DEMO` | `EXPERIMENT` · rotulado em 4 camadas | **AUSENTE** | inventário permanente por omissão |
| `EXP-02` | `opportunityScenarios` 29 — modo cenário, desligado por omissão | `EXPERIMENT` · não alimenta contador nem evidência | **AUSENTE** | os ids colidem com os reais (`IT-OPP-001..029` × `001..003`) |
| `EXP-03` | `futureScenarios` 56 — `DEMO_SCENARIO` | `EXPERIMENT` | **AUSENTE** | terceira população a usar a palavra «sinal» (3 · 4 · 56) |

> **`LC-04` · Todo estado `EXPERIMENT` carrega uma data de revisão.**
> Três experiências, zero datas. É o *carrying cost* do §14 da pesquisa comparativa:
> sem data de expiração, todo estado temporário torna-se permanente por omissão.

---

## §8 · REGISTO DE CONFLITOS ABERTOS

| id | conflito | estado | quem decide |
|---|---|---|---|
| C-01 | 12 vozes × «não desenhar menu de módulos independentes» | ABERTO — falta `SURFACE_CLASS` aplicado | dono do produto |
| C-02 | Source Register: motor de suporte × nível 2 | ABERTO — dois contratos da mesma semana | dono do produto |
| C-03 | portal só-Itália × nível 1 = país (ES·IT·FR) + camada EAME vazia | ABERTO | dono do produto |
| C-04 | `577` no menu × «não existe número único saindo daqui» | ABERTO | dono do produto |
| C-05 | **duas linhagens vivas de portal** | ABERTO — nada declara qual é o publicado | dono do repositório |
| C-06 | partição 17/21/4/1 (Linha B) × 5/8/13/17 (`MEETING_SURFACE_RULE`, Linha A) | ABERTO — `surface-contract.mjs` **3/8** desde `a4508ef` | dono do pacote |
| C-07 | item de menu `#field` × `AMMESSE` | ABERTO | dono do produto |
| C-08 | 166 rótulos × 173 produtos — universos não reconciliados | ABERTO — nunca medido | dono do pacote |

**C-05 é o que bloqueia mais coisas.** Enquanto não houver `PUBLICATION MANIFEST`, a
frase «o portal» não tem referente único.

---

## §9 · O QUE ESTE REGISTO EXIGE A SEGUIR

Ordenado por custo de não fazer, não por esforço.

| # | ação | porquê | custo |
|---|---|---|---|
| 1 | **`PUBLICATION_MANIFEST` por build** | resolve C-05; sem ele «o portal» não tem referente | baixo — derivar do que os geradores já sabem |
| 2 | **`IS_SOURCE_OF_TRUTH = false` explícito nas 6 projeções** | a constante existe para ser lida | trivial |
| 3 | **`DROPPED_FIELDS` nas 4 projeções que não o têm** | AD-21, o funil sem contador | médio |
| 4 | **Responder às perguntas 13–16 do Gate para as 12** | são decisões escritas, não engenharia | baixo |
| 5 | **`LC-04`: data de revisão para as 3 experiências e as 4 legadas** | inventário sem data é inventário permanente | trivial |
| 6 | **Registar retroativamente RV-002, RV-006, RV-007** | AD-05 | trivial |
| 7 | **Telemetria de decisão** (pergunta 12) | desbloqueia 7 recomendações e todos os `PILOT` | **alto — é o único item de engenharia** |
| 8 | **Encontrar o gerador das 29 janelas** | U-02, o UNKNOWN mais caro | desconhecido |
| 9 | **Reconciliar 166 × 173** | C-08 | médio |
| 10 | **Escrever `FORBIDDEN_CLAIMS` para os 6 produtos que não os têm** | C-01 do Product Contract | baixo |

> **Nove das dez são escrita, não código.**
> A entrega do SINTONIA não está bloqueada por engenharia. Está bloqueada por não ter
> onde registar o que já decidiu.
