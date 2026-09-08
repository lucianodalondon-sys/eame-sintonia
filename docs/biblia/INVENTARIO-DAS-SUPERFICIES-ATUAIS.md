# INVENTÁRIO DAS SUPERFÍCIES ATUAIS — SINTONIA EAME

```
DOCUMENT_STATUS          DRAFT
DOCUMENT_TYPE            LIVING PRODUCT REGISTRY · MEDIÇÃO
IMPLEMENTATION           NONE
PRODUCTION_TOUCHED       NONE
MEASURED_AT              2026-09-08
SNAPSHOT_IS_TIME_BOUND   SIM — ver §0
```

> **CICATRIZ Nº 1 DESTE FICHEIRO.**
> `CURRENT PORTAL SNAPSHOT IS TIME-BOUND.`
> Um inventário de superfície é uma **fotografia com hora**, nunca um facto permanente.
> Este documento provou-o em 48 horas: o inventário de 06/09
> (`PORTAL-CAPABILITY-INVENTORY.md`) estava correto quando foi medido e estava
> desatualizado quando foi lido. Ambos continuam verdadeiros — em tempos diferentes.

---

## §0 · OS TRÊS TEMPOS, E POR QUE ELES NÃO SE MISTURAM

Este inventário usa três tempos, e cada linha declara o seu:

| tempo | significado | exemplo |
|---|---|---|
| `HISTORICAL` | foi medido, é evidência, **não descreve o portal de hoje** | «12 itens, 11 ao mesmo nível» — medido em `e4f3e8b`, 06/09 |
| `CURRENT_OBSERVED` | medido no código, hoje, com o comando escrito ao lado | «`sources` = 194» — medido em `a4fb6d8`, 08/09 |
| `FUTURE_PROPOSED` | recomendação desta pesquisa; **não é decisão** | «`ARCHIVE` deveria ser `EVIDENCE_EXPLORER`» |

**Nunca misturar.** Uma recomendação impressa ao lado de uma medição, sem rótulo, é a
forma mais barata de um documento mentir sem escrever nada falso.

---

## §1 · O QUE FOI MEDIDO, ONDE, E COM QUE COMANDO

### 1.1 · Repositório

```
REPO          github.com/lucianodalondon-sys/eame-sintonia
WORKTREE      /home/user/eame-sintonia · árvore limpa
HEAD_INICIAL  9d06d94be9758fea4a3147f9d5f156b96fcbeada
              «duas fichas do mesmo caso, e a que a reuniao abre era a pobre»
BRANCH_BASE   claude/integration-acervo-portal-v1
BRANCH_DESTA  research/delivery-bible-v1  (criada a partir de 9d06d94)
```

### 1.2 · A descoberta que obrigou a re-medir

O baseline visual reportado pelo dono em 08/09 (12 superfícies, com
`Opportunity Radar 17`, `Label Intelligence 166`, `Future Radar 44`,
`Source Register 194`) **não corresponde ao código de `9d06d94`**. Medido:

```bash
grep -c "Label Intelligence\|Intelligenza etichette" italia-portale/client/portale.html
# → 0
```

Não é divergência entre screenshot e código: é **outra linhagem**. Medido em
`git ls-remote --heads origin` — 62 refs — e reduzido por procura do termo:

| branch | HEAD | data | contém `etichette` no menu? |
|---|---|---|---|
| `claude/integration-acervo-portal-v1` | `9d06d94` | 2026-09-08 | **NÃO** |
| `claude/label-intelligence-v1-italy` | `6afba2e` | 2026-09-07 01:45 | é a **ferramenta de origem**, não o portal |
| **`claude/visible-intelligence-v1`** | **`a4fb6d8`** | **2026-09-07 21:11** | **SIM** |

**`claude/visible-intelligence-v1` @ `a4fb6d8` é o `CURRENT_OBSERVED` desta medição.**
A sua sequência de três commits:

```
19843ab  2026-09-07 20:31  il badge nuovo non aveva guardiano…
65d0de4  2026-09-07 21:06  Label Intelligence — o motor continua rigoroso, a interface vira ferramenta
a4fb6d8  2026-09-07 21:11  due portoni mi hanno preso: il nome dello strumento…
```

> **DIVERGÊNCIA REGISTADA, NÃO RESOLVIDA.**
> Existem hoje **duas linhagens vivas de portal** que ninguém fundiu:
> `integration-acervo-portal-v1` (a que traz o acervo → pacote) e
> `visible-intelligence-v1` (a que o dono está a ver). A segunda tem Label
> Intelligence e o Radar Futuro no menu; a primeira tem a reconciliação do
> catálogo e as 611 justificações de exclusão. **Nenhum lado foi escolhido aqui.**

### 1.3 · Como os contadores foram medidos

Não foram lidos de um ecrã nem copiados do relato. O modelo foi **montado a sério**
num contexto de VM Node, carregando os 19 ficheiros do cliente pela ordem do
`portale.html`, e as contagens foram lidas de `ITALY_APP_MODEL.counts`:

```bash
git show origin/claude/visible-intelligence-v1:italia-portale/client/<ficheiro> > vi/<ficheiro>
node measure.mjs          # vm.createContext + runInContext × 19 ficheiros
```

**Resultado: 12 de 12 contadores reportados batem com o código.** Nenhuma divergência
numérica. A divergência era de **branch**, não de número.

---

## §2 · A NAVEGAÇÃO MEDIDA — `CURRENT_OBSERVED @ a4fb6d8`

Fonte: `portale.html:5661-5802`. A barra desenha-se em três listas —
`nav`, `navEvidence`, `navIntegrationItems` — sobre `navDef` + `navRadarFuturo`.

```js
const STRUMENTI = ['meeting', 'portfolio'];
const nav          = navDef.filter(n =>  STRUMENTI.includes(n[0]));
const navEvidence  = (navRadarFuturo.count !== '' ? [navRadarFuturo] : [])
                     .concat(navDef.filter(n => !STRUMENTI.includes(n[0])));
const navIntegrationItems = [['field', T.navField, allMessages.length]];
```

| # | grupo UI | nome visível (EN) | contador | fonte do contador (medida) | rota |
|---|---|---|---|---|---|
| 1 | STRUMENTI | Opportunity Radar | **17** | `ADAMA_RELEVANCE.PER_SUPERFICIE.OPPORTUNITA` | `#meeting` |
| 2 | STRUMENTI | Portfolio | **173** | `AM.counts.products` | `#portfolio` |
| 3 | EVIDENCE AND CONTEXT | Future Radar | **44** | `ITALY_CASA.RADAR_FUTURO.RENDERIZAVEIS` | `#radarfuturo` |
| 4 | EVIDENCE AND CONTEXT | Label Intelligence | **166** | `ITALY_LABEL_INTELLIGENCE.products.length` | `#etichette` |
| 5 | EVIDENCE AND CONTEXT | Crop Windows | **29** | `AM.counts.windows` | `#windows` |
| 6 | EVIDENCE AND CONTEXT | Market Pulse | **157** | `AM.counts.marketObservations` | `#market` |
| 7 | EVIDENCE AND CONTEXT | Field Voices | **79** | `AM.counts.voices` | `#voices` |
| 8 | EVIDENCE AND CONTEXT | Competitor Watch | **577** | `AM.counts.competitorActivities` | `#competitors` |
| 9 | EVIDENCE AND CONTEXT | Scientific Intelligence | **88** | `AM.counts.scienceRecords` | `#science` |
| 10 | EVIDENCE AND CONTEXT | Archive | **1114** | `AM.counts.archive` | `#archive` |
| 11 | EVIDENCE AND CONTEXT | Source Register | **194** | `AM.counts.sources` | `#sources` |
| 12 | INTEGRATIONS · DEMO | Field Sales Channel | **18** | `AM.collections.fieldMessages.records.length` | `#field` ⚠️ |

**A ordem impressa é exatamente a ordem reportada pelo dono.** `navEvidence` começa em
`radarfuturo` e continua por `navDef` menos os dois `STRUMENTI` — o que dá
`etichette, windows, market, voices, competitors, science, archive, sources`.

### ⚠️ Divergência 1 · a rota que a barra oferece e o endereço não aceita

```js
const AMMESSE = ['meeting','future','windows','market','voices','competitors',
                 'science','portfolio','archive','sources','radarfuturo','etichette'];
```

`field` **não está em `AMMESSE`**. Consequência medida: o item 12 abre por clique
(`go({view:'field'})`), mas **um recarregamento em `#field` cai em `#meeting`**. O
comentário do código declara a intenção — *«una schermata che nessuna voce di menu
offre, ma che un indirizzo apriva, è una porta di servizio aperta»* — mas a voz de menu
**continua a ser desenhada**. A intenção e o código discordam.

> `SURFACE_REACHABLE_BY_CLICK ≠ SURFACE_REACHABLE_BY_ADDRESS.`
> Uma superfície com voz de menu e sem rota estável é uma superfície que sobrevive à
> primeira visita e não sobrevive a um *refresh*.

### ⚠️ Divergência 2 · a superfície que saiu da barra e não do produto

`Signal Archive` (`#future`, **3** registos) **está em `AMMESSE`**, tem vista completa,
está em `CAPABILITY_OF`, e **não tem voz de menu**. É alcançável por três caminhos
declarados: a linha no fundo do radar, a linha da janela colturale, e a pesquisa.

**Portanto o portal tem 13 superfícies navegáveis, não 12.** A 13ª é deliberada e está
documentada — *«uma população que existe para ser explicada não pode ser a primeira coisa
que se vê»*. Está aqui registada porque um inventário que só conta o menu conta o menu,
não o produto.

### ⚠️ Divergência 3 · o menu tem 12 vozes e o modelo tem 59 colecções

```
AM.collections   = 59
AM.counts        = 59 chaves
itens de menu    = 12
```

Nem toda a colecção deve ser um item de menu — é precisamente a **LEI ZERO** deste
repositório. Regista-se o rácio porque ele é o termómetro do defeito inverso:
`DATASET → MENU`. Hoje 12/59 = **20%**. Em 06/09 era 12/59 também, mas com uma
composição diferente.

### ⚠️ Divergência 4 · as vistas de detalhe não são superfícies de menu, e são 12 a mais

`Component.CAPABILITY_OF` mapeia **27 ids de vista** para 12 capacidades. As 15
restantes são detalhes e legados:

```
mcase · case · brief · radar · window · signal · product · theme · company ·
event · cproduct · source · person · search · etichetta
```

`case`, `brief` e `radar` são **LEGACY**: `isRadar` está fixo em `false` e `legacyCaseId`
resolve **0 de 43** (medido em `CHECKPOINT-INTEGRACAO-ACERVO-PORTAL.md §5`).

---

## §3 · AS FICHAS — uma por superfície

Formato fixo. Um campo sem prova escreve `NÃO SEI`, e isso é resposta.
`AUTHORITY` aponta para documento **nomeado e datado**, ou é `UNKNOWN`.
`FUTURE_PROPOSED` é recomendação desta pesquisa, nunca decisão.

---

### S-01 · OPPORTUNITY RADAR

```
SURFACE_ID                    S-01-OPPORTUNITY-RADAR
VISIBLE_NAME                  Opportunity Radar · Radar delle Opportunità
CURRENT_COUNT                 17     (era 13 em 06/09 — a lei mudou, não o dado)
CURRENT_MENU_GROUP            STRUMENTI
ROUTE / VIEW                  #meeting  ·  detalhe: mcase
OWNER (render)                portale.html vista 'meeting' + meeting-surface.js
CURRENT_STATE                 CURRENT
DATA_INPUT                    AM.collections.opportunities (43, CANONICAL, HANDOFF_V21)
INTELLIGENCE_INPUT            MEETING_INTELLIGENCE (istantanea) + ADAMA_RELEVANCE
GENERATOR                     scripts/adama_relevance.py  (a LEI)
                              scripts/it_casa_dados.py    (o transporte)
                              scripts/meeting_snapshot.py (o corte)
DECISION_QUESTION             «onde um problema medido está a ficar mais relevante — e a
                              ADAMA tem resposta registada?»   (ARQUITETURA §MT2)
TARGET_USER                   MARKET DEVELOPMENT (decisor central) · COMMERCIAL ·
                              MARKETING · PORTFOLIO
PRODUCT_CONTRACT              PARCIAL. Existe LEI de elegibilidade
                              (ADAMA-RELEVANCE-LAW-V1, 8 elos da CADEIA_EXIGIDA,
                              5 classes, SO_A_PUBLICA=true) e existe contrato de saída
                              (ARQUITETURA §MT2: 5 campos obrigatórios por região).
                              NÃO existe: freshness contract, empty state, conflict
                              state, rollback, value measurement.
AUTHORITY                     YES — docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md §MT2,
                              2026-08-29, «porta única»
EVIDENCE_CHAIN                caso → EVIDENCE_SCAN (1529 encontradas · 359 usadas ·
                              1170 omitidas) → registo/rótulo/campo → fonte
FRESHNESS                     COMPOSTO e já separado: DATA_DE_REFERENCIA 2026-09-02
                              (pacote V2.1) ≠ MEETING_CUTOFF 2026-09-04T00:52:54Z
                              (corte da istantanea). O portal chamava aos dois a mesma
                              coisa e foi corrigido — ver CASOS-ADVERSARIAIS AD-07.
WHAT_IT_CALCULATES            nada na UI: recebe o veredito
WHAT_UI_CALCULATES            ordenação, filtro, paginação (mShown: 24)
WHAT_BACKEND_CALCULATES       classe A–E, superfície, cadeia de 8 elos, PRIMARY_MATCH
WHAT_SHOULD_NOT_BE_CALCULATED_HERE   relevância, prioridade, likelihood, confiança
UNKNOWN_BEHAVIOR              declarado: classe E = «NÃO SEI, nunca sobe»; classe D =
                              «ligação errada, não publicável»
DUPLICATION                   RESOLVIDA. Havia duas entradas com o mesmo 43
                              («due radar degli stessi 43 sono un radar che non ci si
                              fida»); hoje há uma
OVERLAP                       com S-04 Label Intelligence (o elo «rótulo ministerial» da
                              cadeia é o mesmo facto) e com S-02 Portfolio (o elo
                              «produto ADAMA»)
POTENTIAL_VALUE               ALTO — é a única superfície do portal que publica um
                              JUÍZO com lei escrita, portão executável e classe negada
CURRENT_ROLE                  CANONICAL_TOOL
POSSIBLE_FUTURE_ROLE          CANONICAL_TOOL  (confiança ALTA)
WHAT_IS_STILL_UNKNOWN         · DECISION_PROVED = NÃO (falta piloto com utilizador)
                              · conflito de contrato Linha A × Linha B por resolver
                                (surface-contract.mjs 3/8, ver CHECKPOINT §8)
                              · nome do ecrã ainda diz OPPORTUNITÀ e o contrato manda
                                dizer PRIORITY TO INVESTIGATE
```

---

### S-02 · PORTFOLIO

```
SURFACE_ID                    S-02-PORTFOLIO
VISIBLE_NAME                  Portfolio · Portafoglio
CURRENT_COUNT                 173      (= 163 regulatórios ∪ 51 comerciais, dedup.)
CURRENT_MENU_GROUP            STRUMENTI      ← PROMOVIDO desde 06/09
ROUTE / VIEW                  #portfolio  ·  detalhe: product
OWNER (render)                portale.html vistas 'portfolio' + 'product'
CURRENT_STATE                 CURRENT
DATA_INPUT                    products 173 · productRelationships 5402 ·
                              activeIngredients 53 · productActiveIngredients 203 ·
                              portfolioLinksByCrop 34
INTELLIGENCE_INPUT            AM.STRENGTH (4 níveis: VERIFIED_LABEL_MATCH →
                              RELATED_PORTFOLIO → LABEL_CHECK_NEEDED →
                              NO_CONFIRMED_MATCH_CURRENT_READING)
GENERATOR                     scripts/site_v21_ingest.py ← pacote V2.1
DECISION_QUESTION             DECLARADA NÃO. A porta única dá-lhe MT1 («o que está a
                              mudar ou a chegar, o que isso toca, e quem mais está
                              exposto?») mas o ecrã responde «que produtos temos?», que
                              é uma pergunta de catálogo.
TARGET_USER                   REGULATORY · PORTFOLIO · MARKET DEVELOPMENT
PRODUCT_CONTRACT              NÃO. Existe CAP-007 no atlas de capacidades e §MT1 na
                              arquitetura; nenhum é contrato de ferramenta.
AUTHORITY                     UNKNOWN → **em disputa**. Em 06/09 era UNKNOWN; em 08/09
                              está em STRUMENTI, isto é, tratado como ferramenta
                              principal. NENHUM documento registou essa promoção.
                              É o caso AD-11 dos casos adversariais.
EVIDENCE_CHAIN                produto → registo ministerial (nº, titular, caducidade) →
                              rótulo (PDF com sha) → uso autorizado
FRESHNESS                     AM.compiled = 2026-09-02. Por produto: `expiry` é facto da
                              fonte; `dte` (dias até expirar) é aritmética contra a data
                              de referência — **derivada, não persistida**
WHAT_IT_CALCULATES            junção registo × catálogo comercial
WHAT_UI_CALCULATES            filtros, agrupamento por cultura
WHAT_BACKEND_CALCULATES       dedup 163+51→173; STRENGTH por par
WHAT_SHOULD_NOT_BE_CALCULATED_HERE   disponibilidade comercial (o contrato de design
                              §2.4 obriga COMMERCIAL_CLOCK = NÃO SEI); quota de mercado
UNKNOWN_BEHAVIOR              declarado: NO_CONFIRMED_MATCH_CURRENT_READING é um estado,
                              não um vazio; AM.ABSENCE_RULE = «Absence in this reading
                              is not absence in the world»
DUPLICATION                   aliases no próprio modelo: regulatory=productsRegulatory
                              (163) · commercial=productsCommercial (51) ·
                              regulatoryLinks=productRelationships (5402)
OVERLAP                       S-01 (elo «produto ADAMA»), S-04 (o rótulo é a prova do
                              uso), S-08 (o mesmo registo do lado do concorrente)
POTENTIAL_VALUE               ALTO — é INPUT declarado de MT1 **e** de MT2
CURRENT_ROLE                  tratado como CANONICAL_TOOL; **provado** apenas como
                              REFERENCE_SURFACE
POSSIBLE_FUTURE_ROLE          duas hipóteses, ambas legítimas, nenhuma medida:
                              (a) face de MT1 — vira ferramenta com decision question
                                  regulatória própria («quem está exposto a que prazo?»)
                              (b) REFERENCE_SURFACE + DELIVERY_PROJECTION consumida por
                                  S-01, S-04 e Ask
                              **PRECISA DE MEDIÇÃO ANTES DE DECIDIR**
WHAT_IS_STILL_UNKNOWN         a promoção a STRUMENTI foi decisão de produto ou
                              consequência de desenho de barra? Nenhum documento diz.
```

---

### S-03 · FUTURE RADAR

```
SURFACE_ID                    S-03-FUTURE-RADAR
VISIBLE_NAME                  Future Radar · Radar Futuro
CURRENT_COUNT                 44   (TOTAL 45 · RENDERIZAVEIS 44 · DERRUBADOS 1)
CURRENT_MENU_GROUP            EVIDENCE AND CONTEXT   ← NOVO desde 07/09
ROUTE / VIEW                  #radarfuturo  (era casa.html#radar-futuro, migrou)
OWNER (render)                portale.html vista 'radarfuturo'  (antes: casa.html)
CURRENT_STATE                 CURRENT
DATA_INPUT                    upstream/IT-FUTURO-HANDOFF-LINHA-B-V1.json (COLLECTION=ITFC)
                              → ITALY_CASA.RADAR_FUTURO.REGISTRO (44 linhas,
                              ITFC-001..ITFC-045)
INTELLIGENCE_INPUT            régua de horizonte: PREPARAR 23 · MONITORAR 21 ·
                              AGIR_AGORA 0 · PORTFOLIO_LIMITED 8 ·
                              ORIZZONTE = PROSSIMA_CAMPAGNA
GENERATOR                     scripts/it_casa_dados.py (linha 349 lê · 503 monta)
DECISION_QUESTION             «o que pode importar depois?»
                              (RADAR-DO-FUTURO-CONTRACT-V1.json, 2026-08-30)
TARGET_USER                   MARKET DEVELOPMENT · R&D · PORTFOLIO · LEADERSHIP
PRODUCT_CONTRACT              **O MAIS COMPLETO DO REPOSITÓRIO — e é de DADO, não de
                              ferramenta.** RADAR-DO-FUTURO-CONTRACT-V1 traz:
                              entidade FUTURE_THEME (9 blocos de campos), régua de
                              maturidade 0–5, regras de momentum (REGRA_ZERO: primeira
                              captura é sempre BASELINE_ESTABLISHED), regras de promoção
                              (cada transição exige evidência NOVA), rebaixamento
                              explícito, PALAVRAS_PROIBIDAS, e a frase
                              «NÃO HÁ UI AQUI».
AUTHORITY                     PARCIAL — o contrato define o motor e **recusa-se a definir
                              a superfície**. A superfície nasceu depois, sem ficha.
EVIDENCE_CHAIN                QUEBRADA E DECLARADA. O handoff declara
                              CAMPOS_OBRIGATORIOS_DO_CARTAO com 13 campos
                              (F_CITACAO_VERBATIM, F_FONTE, F_DATA_DO_FATO, F_REGIAO,
                              F_CULTURA, F_ALVO, T_JANELA_DE_APLICACAO, TRIGGER…).
                              **Nenhum viaja.** Só 3 dos 44 têm conteúdo rico.
FRESHNESS                     NÃO SEI por ficha. O agregado tem a data do pacote.
WHAT_IT_CALCULATES            nada
WHAT_UI_CALCULATES            dobra, agrupamento por horizonte
WHAT_BACKEND_CALCULATES       classificação em 3 horizontes; o abate de 1 dos 45
WHAT_SHOULD_NOT_BE_CALCULATED_HERE   previsão. O contrato proíbe: «nenhum estado deste
                              contrato afirma que algo VAI acontecer»
UNKNOWN_BEHAVIOR              excelente: AGIR_AGORA = 0 vem com a frase
                              «é zero por decisão da regra, não por falta de leitura»
DUPLICATION                   com S-13 Signal Archive (3). Distinção declarada
                              («popolazione distinta») **e agora verificável** — a
                              pastilha liga uma à outra
OVERLAP                       com S-01: a porta entre os dois é declarada e é uma só —
                              CURRENT_FIELD_CONFIRMATION
POTENTIAL_VALUE               ALTO na intenção · BAIXO na entrega de hoje
                              (44 identificadores não são 44 fichas)
CURRENT_ROLE                  EXPLORATORY_TOOL
POSSIBLE_FUTURE_ROLE          CANONICAL_TOOL, **se** os 13 campos passarem a viajar.
                              Tem a melhor decision question e o pior payload.
WHAT_IS_STILL_UNKNOWN         · quem é o dono dos 12 campos que não viajam?
                              · o handoff ITFC pertence à linha B; a Bíblia da
                                Inteligência ainda não o adotou
```

---

### S-04 · LABEL INTELLIGENCE

> **A SUPERFÍCIE MAIS IMPORTANTE DESTA PESQUISA.** Não porque seja a maior, mas porque
> é a **única do portal inteiro que já é, hoje, exatamente o que esta Bíblia vai
> chamar de INTELLIGENCE PRODUCT servido a uma DELIVERY PROJECTION.** Ela existia
> antes do vocabulário. Ver `BIBLIA-DA-ENTREGA-EAME.md §5` e §6.

```
SURFACE_ID                    S-04-LABEL-INTELLIGENCE
VISIBLE_NAME                  Label Intelligence · Intelligenza delle etichette
CURRENT_COUNT                 166 produtos  (+ 210 objects · 54 versions)
CURRENT_MENU_GROUP            EVIDENCE AND CONTEXT
ROUTE / VIEW                  #etichette  ·  detalhe: etichetta
OWNER (dado)                  ferramenta EXTERNA `pilot-label-intelligence`, no ramo
                              claude/label-intelligence-v1-italy, ficheiro
                              v1/dados/CASCO-PAYLOAD.json
OWNER (render)                portale.html vista 'etichette'
CURRENT_STATE                 CURRENT
DATA_INPUT                    italy-label-intelligence.js — payload COPIADO BYTE A BYTE.
                              O cabeçalho do ficheiro diz-o:
                              «COPIAR É MAIS SEGURO DO QUE RESUMIR.»
INTELLIGENCE_INPUT            22 regras nomeadas e versionadas
                              (RULESET_VERSION = v1/inteligencia/REGRAS.md@5):
                              R-10 exclusão · R-10b rotação · R-11 cultura-por-fio ·
                              R-12 teto de dose · R-13 alvo literal ·
                              R-14 par por fios · R-15 herança · R-17 alvo nomeado ·
                              R-18 citação · R-19 vigência · R-20 cobertura por célula ·
                              R-21 cultura nomeada · R-22 banda/fio
GENERATOR                     v1/inteligencia/payload.py
                              MODULE_SHA256  84dbb705…46c6fa4
                              CONTENT_SHA256 d27278de…3227bc4e
                              portão: italia-portale/audit/etichette-gate.mjs recalcula
                              o sha a cada execução
DECISION_QUESTION             **SIM, EXPLÍCITA E ESCRITA NO PRÓPRIO PAYLOAD:**
                              «o que o rótulo oficial ADAMA autoriza, como está
                              estruturado e o que mudou»
TARGET_USER                   REGULATORY (primário) · TECHNICAL/AGRONOMIC · PORTFOLIO ·
                              MARKET DEVELOPMENT (indireto, via S-01)
PRODUCT_CONTRACT              **SIM — O ÚNICO COMPLETO DO PORTAL.** Declara:
                              · o que responde  (1 frase)
                              · o que NÃO responde e não pode ser feito responder por
                                junção: SCIENTIFIC_INTELLIGENCE · DISEASE_INTELLIGENCE ·
                                OPPORTUNITY · COMPETITOR_INTELLIGENCE
                              · FORBIDDEN_CLAIM: «USO AUTORIZADO NÃO É OPORTUNIDADE
                                COMERCIAL»
                              · portão G-01 fechado: «nunca envia nada ao campo sozinha»
                              · 7 coberturas separadas + coverage_note:
                                «cada cobertura conta uma coisa diferente e nenhuma
                                implica a seguinte»
AUTHORITY                     YES por selo, UNKNOWN por documento de produto. Nenhum
                              documento de arquitetura a autoriza como item de menu —
                              e ela é a que **menos precisa** disso, porque o seu
                              contrato faz o trabalho.
EVIDENCE_CHAIN                A MAIS FUNDA DO REPOSITÓRIO:
                              produto → registo ministerial → PDF do rótulo
                              (pdf_sha, pdf_bytes) → texto extraído em 3 modos
                              (pdftotext fluxo · -layout · -raw) → linha da tabela →
                              **fios desenhados do PDF** (célula geométrica) → citação
                              literal com verificação de existência (R-18)
FRESHNESS                     **COMPOSTO E JÁ SEPARADO EM SEIS RELÓGIOS:**
                              DATA_DATE 20260831 (a fonte) · DATA_SNAPSHOT_ID
                              PROD_FTS_6_20260831 · COLLECTED_AT 2026-09-04 ·
                              BUILT_AT 2026-09-06 · RUN RUN-2026-09-06-C ·
                              NEWEST_CHANGE_AT 2026-07-20 · e por produto:
                              label_effective / label_valid_from / label_valid_to /
                              label_validity_state / captured_at
                              **É o modelo de freshness que a Bíblia adota.**
WHAT_IT_CALCULATES            coberturas, vereditos por regra, diffs entre 60 snapshots
WHAT_UI_CALCULATES            nada de substantivo — a interface é leitura do payload
WHAT_BACKEND_CALCULATES       tudo, a montante, com sha selado
WHAT_SHOULD_NOT_BE_CALCULATED_HERE   oportunidade; doença; concorrência; ciência.
                              **Escrito no próprio artefacto.**
UNKNOWN_BEHAVIOR              exemplar. PHI_COVERAGE = 0 **por decisão declarada**:
                              «o extrator de carência está marcado
                              PROTOTYPE_NOT_SHIPPED e nada é publicado».
                              Zero com motivo ≠ zero.
                              by_proof: PROVED 51 · NOT_PROVED 159.
                              by_window: UNKNOWN 159 de 210.
DUPLICATION                   com S-02 Portfolio: 166 produtos de rótulo × 173 do
                              portfólio; **os universos não são o mesmo e ninguém os
                              reconciliou nesta medição**
OVERLAP                       é INPUT do elo «RELAÇÃO produto × alvo (rótulo
                              ministerial)» da cadeia de 8 elos de S-01
POTENTIAL_VALUE               MUITO ALTO. É a única capacidade do repositório com
                              selo criptográfico, ruleset versionado, reconciliação
                              declarada (raw × publicado, delta explicado) e
                              teste de mutação à mão que fez nascer o selo.
CURRENT_ROLE                  classificado pelo código como EVIDÊNCIA
                              («as etichette são evidência, não um terceiro
                              instrumento» — comentário em portale.html:5698)
POSSIBLE_FUTURE_ROLE          **CANONICAL_TOOL + DELIVERY_PROJECTION, em simultâneo.**
                              Tem decision question própria, utilizador próprio
                              (REGULATORY), evidência própria e claim proibido próprio.
                              O facto de alimentar S-01 não a torna menos ferramenta —
                              é exatamente a cardinalidade M:N que a Bíblia consagra.
                              **Confiança: ALTA para tool; a colocação no menu é
                              decisão de produto, não de arquitetura.**
WHAT_IS_STILL_UNKNOWN         · DOSE_COVERAGE 12,9% e PHI_COVERAGE 0% — quanto disso é
                                limite de método e quanto é tempo?
                                (o próprio artefacto responde: PHI é decisão)
                              · os 166 × 173: qual é a relação exata com o Portfolio?
                              · nenhum documento de produto a admitiu ainda
```

---

### S-05 · CROP WINDOWS

```
SURFACE_ID                    S-05-CROP-WINDOWS
VISIBLE_NAME                  Crop Windows · Finestre Colturali
CURRENT_COUNT                 29
CURRENT_MENU_GROUP            EVIDENCE AND CONTEXT
ROUTE / VIEW                  #windows  ·  detalhe: window
OWNER                         portale.html vistas 'windows'/'window' ·
                              italy-canonical-windows.js
CURRENT_STATE                 CURRENT
DATA_INPUT                    AM.collections.cropWindows (29) + windowCalendarRows 29 +
                              windowsByRegion 20 + currentFieldSignals 7
INTELLIGENCE_INPUT            janelas canónicas italianas
GENERATOR                     **AUSENTE.** Medido em `CHECKPOINT-INTEGRACAO §7`: o
                              gerador e o insumo (CANONICAL-CROP-WINDOWS-2026-09-02.json)
                              e o contrato citado (INTELLIGENCE-TO-DESIGN-CONTRACT.md)
                              **estão ausentes de 979 commits de todos os refs**.
                              Origem: um único commit de importação, 9eb598a.
DECISION_QUESTION             NÃO DECLARADA
TARGET_USER                   TECHNICAL/AGRONOMIC · COMMERCIAL · MARKET DEVELOPMENT
PRODUCT_CONTRACT              NÃO. Existe AGRONOMIC-CALENDAR-DESIGN-DATA-CONTRACT-V1,
                              mas: (a) é contrato de DADO — «não diz como desenhar»;
                              (b) FACT_LOCATION = **ES**, e o portal é italiano
AUTHORITY                     UNKNOWN
EVIDENCE_CHAIN                **VAZIA E MEDIDA:** SOURCE_IDS vazio em 29/29 ·
                              o motor declara NOT_EXTERNALLY_OBSERVABLE 29/29 ·
                              LAST_VALIDATED tem UM único valor (2026-09-02) em 29/29,
                              que é carimbo de geração, não de validação
                              PROVED 0 · PARTIAL 2 · UNKNOWN 27 · INVALID 0
                              CROP_WINDOWS_TRUSTED = **NÃO**
FRESHNESS                     CURRENT_STATUS é **aritmética pura de datas** contra
                              2026-09-02 em 29/29. Não é frescor de evidência.
WHAT_IT_CALCULATES            estado aberto/fechado por data
WHAT_UI_CALCULATES            o mesmo — e é aqui que dói: **o cálculo do estado vive na
                              fronteira UI/modelo, não num produto de inteligência**
WHAT_BACKEND_CALCULATES       pouco: as 29 chegam já formadas, sem proveniência
WHAT_SHOULD_NOT_BE_CALCULATED_HERE   necessidade de aplicação.
                              CONTRATO-DE-DESIGN §2.1: `WINDOW_OPEN ≠ CURRENT_NEED`
UNKNOWN_BEHAVIOR              bom: 5 janelas sem data mostram «DATA DA CONFERMARE» —
                              nenhuma data inventada. E a pastilha verde que prometia
                              oportunidade foi removida (6 promessas falsas → 0)
DUPLICATION                   alias windows = cropWindows (ambas 29).
                              **E o par 29 × 7:** as 29 canónicas e as 7 leituras são
                              universos distintos por desenho (os IDs distam um zero) e
                              o check W1 protege-o
OVERLAP                       SEASONAL TIMING é **INPUT declarado de MT2**
POTENTIAL_VALUE               ALTO se ganhar proveniência · nulo enquanto for
                              aritmética sem fonte
CURRENT_ROLE                  SUPPORTING_VIEW a ser mostrada como ferramenta
POSSIBLE_FUTURE_ROLE          CONTEXT_VIEW / componente temporal de S-01 e S-04.
                              **Mas não se aposenta uma ideia por a implementação ter
                              nascido antes do contrato:** a pergunta «ainda existe
                              tempo para agir?» é a 5ª das cinco perguntas da
                              convergência e é a mais difícil. O objeto é bom.
                              A instância atual é que não tem fonte.
WHAT_IS_STILL_UNKNOWN         o gerador. Sem ele, tudo o resto é especulação.
                              **É o UNKNOWN mais caro deste inventário.**
```

---

### S-06 · MARKET PULSE

```
SURFACE_ID                    S-06-MARKET-PULSE
VISIBLE_NAME                  Market Pulse · Polso di Mercato
CURRENT_COUNT                 157
CURRENT_MENU_GROUP            EVIDENCE AND CONTEXT
ROUTE / VIEW                  #market
OWNER                         portale.html vista 'market' · italy-market-pulse.js
CURRENT_STATE                 CURRENT
DATA_INPUT                    marketObservations 157 (CANONICAL) + marketByCrop 14 +
                              marketSummaries 5 + cropEconomics 2978
INTELLIGENCE_INPUT            observações semanais de preço da Comissão Europeia
GENERATOR                     scripts/agrifood_ue.py → pacote
DECISION_QUESTION             NÃO DECLARADA
TARGET_USER                   COMMERCIAL · MARKET DEVELOPMENT · LEADERSHIP · COUNTRY
PRODUCT_CONTRACT              NÃO
AUTHORITY                     **NO.** Dupla prova documental:
                              (a) «market/crop context» está nomeado no SUPPORTING
                                  ENGINE — «por baixo, NÃO NO MENU»
                              (b) DO NOT BUILD inclui «crop pulse genérico»
                              E CAP-019 (preço semanal de cereal) cobre FRANCE e SPAIN;
                              **não cobre a Itália**, que é o país do portal.
EVIDENCE_CHAIN                preço → praça → semana → fonte UE. Sólida no dado.
FRESHNESS                     semanal, com data por observação
WHAT_IT_CALCULATES            séries, variações
WHAT_UI_CALCULATES            gráficos e agregações por cultura
WHAT_BACKEND_CALCULATES       normalização de praça
WHAT_SHOULD_NOT_BE_CALCULATED_HERE   procura, quota, receita.
                              **Cicatriz medida (migration 021):** o demo mostrou azeite
                              de Salerno a €630 como preço corrente; a cotação era de
                              2015. A lei que nasceu: CURRENT / OUTLOOK / HISTORICAL
                              nunca se misturam, e a classe temporal é coluna obrigatória.
UNKNOWN_BEHAVIOR              o badge deixou de contar as 8 abas do fixture (Tomate,
                              Beterraba, Maçã tinham zero linhas reais) e passou a
                              contar só as observações reais. Boa correção.
DUPLICATION                   —
OVERLAP                       cropEconomics 2978 é peso económico de cultura e alimenta
                              S-01 sem passar por aqui
POTENTIAL_VALUE               MÉDIO como contexto · BAIXO como ferramenta autónoma
CURRENT_ROLE                  CONTEXT_VIEW mostrada como ferramenta
POSSIBLE_FUTURE_ROLE          CONTEXT_VIEW / DELIVERY_PROJECTION consumida por S-01 e
                              por Ask. **Confiança MÉDIA-ALTA** — é o caso em que o
                              contrato antigo (2026-08-29) e a medição de hoje
                              concordam, e não há inteligência nova desde então que
                              justifique reabrir.
WHAT_IS_STILL_UNKNOWN         se existe utilizador que abre esta tela para decidir algo.
                              **NÃO MEDIDO. Precisa de telemetria antes de decidir.**
```

---

### S-07 · FIELD VOICES

```
SURFACE_ID                    S-07-FIELD-VOICES
VISIBLE_NAME                  Field Voices · Voci dal Campo
CURRENT_COUNT                 79    (58 comentários + 21 vozes)
CURRENT_MENU_GROUP            EVIDENCE AND CONTEXT
ROUTE / VIEW                  #voices
OWNER                         portale.html vista 'voices'
CURRENT_STATE                 CURRENT
DATA_INPUT                    publicVoices 79 · publicChannels 62 · publicPeople 15
                              e, ao lado e invisível: **transcripts 184**
INTELLIGENCE_INPUT            comentários públicos do YouTube; identidade nunca promovida
GENERATOR                     pipeline de coleta ES/IT → pacote V2.1
DECISION_QUESTION             NÃO DECLARADA
TARGET_USER                   MARKETING · MARKET DEVELOPMENT · TECHNICAL
PRODUCT_CONTRACT              NÃO
AUTHORITY                     **NO, mas com uma nota que muda tudo.** A última ficha
                              escrita (CATALOGO, 2026-08-28) diz `CONCEPT — sem fonte de
                              dado`, TECHNICAL_FEASIBILITY BAIXA, ADAMA_ALIGNMENT UNKNOWN.
                              A ARQUITETURA (2026-08-29) diz **`NOT REACHED / NÃO SEI,
                              não KILL`** e acrescenta: «Apify não foi testado (sem
                              credencial). É preciso testar antes de decidir.»
                              → **A recusa era de FONTE, não de IDEIA.**
                                A fonte entretanto chegou: 79 vozes canónicas, 62 canais,
                                184 transcrições, 5.033.374 caracteres de fala no acervo.
                                **Ninguém reabriu a ficha.** Ver AD-02.
EVIDENCE_CHAIN                voz → canal → vídeo → plataforma. Presente.
                              Transcrição → **TRANSCRIPT_USED_AS_EVIDENCE = false em
                              184/184**, e a ficha di-lo em voz alta.
FRESHNESS                     publishedAt por registo
WHAT_IT_CALCULATES            categorização
WHAT_UI_CALCULATES            agrupamento por categoria (catUi)
WHAT_BACKEND_CALCULATES       resolução cultura (missPct 1,3% — a melhor do modelo)
WHAT_SHOULD_NOT_BE_CALCULATED_HERE   sentimento agregado; «buzz»; score de influência
                              (proibidos por nome na home); autoridade de quem fala
                              (RESEARCHER_OUTLOOK: «NÃO é ranking»)
UNKNOWN_BEHAVIOR              a escada de 5 degraus da transcrição é declarada e nenhum
                              degrau implica o seguinte:
                              VIDEO_EXISTS ≠ TRANSCRIPT_EXISTS ≠ TRANSCRIPT_USABLE ≠
                              TRANSCRIPT_USED_AS_EVIDENCE
DUPLICATION                   aliases voices=publicVoices (79) · channels=publicChannels (62)
OVERLAP                       `people` (66) partilhado com S-11 Source Register e com
                              S-09 Scientific Intelligence
POTENTIAL_VALUE               **O MAIOR POTENCIAL NÃO REALIZADO DO REPOSITÓRIO.**
                              5,03 M de caracteres de fala de campo estão no acervo e
                              **zero** entram no pacote. Nenhuma das 43 oportunidades
                              cita voz, canal ou vídeo como evidência.
CURRENT_ROLE                  EVIDENCE_EXPLORER a ser mostrado como ferramenta
POSSIBLE_FUTURE_ROLE          **TRÊS HIPÓTESES, TODAS VIVAS, NENHUMA MEDIDA:**
                              (a) SENSOR — a camada que detecta antes do registo
                              (b) EVIDENCE_EXPLORER — a prova qualitativa de um caso
                              (c) CANONICAL_TOOL — se ganhar decision question própria
                                  («o que o campo está a dizer que a ciência ainda não
                                  publicou e o registo ainda não reflete?»)
                              **Confiança: BAIXA em qualquer das três. PRECISA DE
                              MEDIÇÃO.** É o teste de mudança de papel da §18 da Bíblia.
WHAT_IS_STILL_UNKNOWN         · GDPR: P-008 e P-009 continuam ABERTAS
                              · a fronteira ACERVO→PACOTE é o dono da perda
                              · a régua de ALERTA não abre a porta BASELINE para
                                nenhuma família de conversa pública
```

---

### S-08 · COMPETITOR WATCH

```
SURFACE_ID                    S-08-COMPETITOR-WATCH
VISIBLE_NAME                  Competitor Watch · Concorrenza
CURRENT_COUNT                 577   (PAID 414 · ORGANIC_VIDEO 147 · NOTA 16)
                                    569 publicáveis · 8 retidos (CLIENT_SAFE=false)
                                    27 ATTIVI · 385 históricos · 192 UNKNOWN
CURRENT_MENU_GROUP            EVIDENCE AND CONTEXT
ROUTE / VIEW                  #competitors · detalhes: company, event, cproduct
OWNER                         portale.html 4 vistas
CURRENT_STATE                 CURRENT
DATA_INPUT                    competitorActivities 577 · competitorCompanies 11 ·
                              competitorProducts 36 · competitorMatrix 11 ·
                              competitorCropDensity 8 · competitorIssueDensity 14 ·
                              competitorWindowMoments 29 · communicationAxis 15
INTELLIGENCE_INPUT            registo nacional + comunicação pública + atividade técnica
                              + Meta Ads Library
GENERATOR                     scripts/comunicacao_*.py, concorrente_crosswalk.py,
                              concorrente_paridade.py
DECISION_QUESTION             NÃO DECLARADA como ferramenta. Declarada como CAMADA:
                              «quem tem resposta? quem está a anunciar? quem começou
                              primeiro?»
TARGET_USER                   MARKET DEVELOPMENT (decisor central) · PORTFOLIO ·
                              MARKETING
PRODUCT_CONTRACT              **NÃO — e o contrato de DADO proíbe-o em voz alta.**
                              EAME-COMPETITOR-CONTRACT-V1.json, 2026-08-30:
                              «não é um painel de concorrência, não é um ranking, não é
                              um score de ameaça, **não é uma ferramenta isolada.
                              Não existe tela nem número único saindo daqui**»
                              Reforçado por D-021: «a camada de concorrente é derivada e
                              não vira dona de nada»
AUTHORITY                     **NO, textual.** E a barra imprime `577` — que é,
                              literalmente, o número único que o contrato proíbe.
EVIDENCE_CHAIN                anúncio → canal → empresa → (texto) registo.
                              D-021: `evento_concorrente` só APONTA, nunca cria segunda
                              verdade sobre empresa, registo ou anúncio.
FRESHNESS                     **O QUINTO RELÓGIO, declarado e separado:**
                              COMPETITOR OBSERVATION CLOCK — FIRST_OBSERVED ·
                              LAST_OBSERVED · CHANGE_OBSERVED · SOURCE_DATE · AS_OF_DATE.
                              «Não se funde com os quatro do calendário agronómico, e o
                              frescor continua derivado, nunca persistido.»
                              **DEFEITO MEDIDO:** o acervo tem `last_observed` em
                              414/414; o pacote não os pede; 27 exibem selo ATTIVO
                              **sem a data que o provaria**. ACTIVE_ADS_PROVED = 0.
WHAT_IT_CALCULATES            densidades por cultura e por alvo
WHAT_UI_CALCULATES            feed, filtros por empresa/tipo/período
WHAT_BACKEND_CALCULATES       crosswalk marca ↔ registo (1.683 cadeias, 126 recusadas)
WHAT_SHOULD_NOT_BE_CALCULATED_HERE   **quatro proibições nomeadas na arquitetura:**
                              somar registo + anúncio + comunicação + atividade técnica
                              num indicador; ler anúncio como procura/venda/share;
                              dizer que um concorrente está silencioso (o correto é
                              NO PUBLIC ACTIVITY FOUND IN SEARCHED SOURCES);
                              contagem de registos como quota de mercado
UNKNOWN_BEHAVIOR              cinco estados de ativação que **nunca se somam**, mais
                              NOT_KNOWN sempre disponível. `issueIds` vazio em 577/577 —
                              e a ficha declara que se liga «SÓ por cultura»
DUPLICATION                   —
OVERLAP                       COMPETITOR REGISTERED RESPONSE é INPUT declarado de MT2;
                              partilha o registo com S-02 e S-04
POTENTIAL_VALUE               ALTO como camada · o contrato nega-o como ferramenta
CURRENT_ROLE                  camada transversal apresentada como ferramenta
POSSIBLE_FUTURE_ROLE          **CROSS-CUTTING LAYER + DELIVERY_PROJECTION.**
                              A pergunta que a Bíblia deixa aberta: uma camada
                              transversal pode ter uma superfície de investigação sem
                              virar ferramenta? **Sim** — é um INVESTIGATION_VIEW.
                              O que o contrato proíbe é o **número único** e o
                              **ranking**, não a possibilidade de investigar.
                              **Confiança MÉDIA-ALTA no papel; a forma atual viola o
                              contrato no contador.**
WHAT_IS_STILL_UNKNOWN         · ATIVAÇÃO OBSERVADA continua PLANNED em 3 dos 4 estados
                              · comunicação: rota provada para 1 de 5 majors (403 nos
                                outros 4) — e 403 não é ausência
```

---

### S-09 · SCIENTIFIC INTELLIGENCE

```
SURFACE_ID                    S-09-SCIENTIFIC-INTELLIGENCE
VISIBLE_NAME                  Scientific Intelligence · Intelligence Scientifica
CURRENT_COUNT                 88     (e ao lado, invisível: scienceCorpus 763)
CURRENT_MENU_GROUP            EVIDENCE AND CONTEXT
ROUTE / VIEW                  #science · detalhe: theme
OWNER                         portale.html vistas 'science'/'theme' ·
                              italy-science-business.js
CURRENT_STATE                 CURRENT
DATA_INPUT                    scienceRecords 88 · researchers 60 · resistance 34 ·
                              scienceThemes 5 · scienceInstitutions 6 ·
                              **scienceCorpus 763**
INTELLIGENCE_INPUT            OpenAlex + vocabulário EPPO
GENERATOR                     scripts/corpus_pesquisador.py, pacote_docs.py
DECISION_QUESTION             **PARCIAL — e é a pergunta certa a fazer aqui.**
                              CAP-017 declara: «quem trabalha repetidamente com este
                              problema, neste país, em que instituição e desde quando?»
                              Isso É uma decision question — de R&D e de TECHNICAL.
                              **Mas CAP-017 cobre FRANCE e SPAIN. Não cobre a Itália**,
                              que é o país deste portal.
TARGET_USER                   R&D · TECHNICAL/AGRONOMIC · MARKET DEVELOPMENT
PRODUCT_CONTRACT              NÃO
AUTHORITY                     **NO** — «science · experts» está nomeado no SUPPORTING
                              ENGINE, «por baixo, não no menu».
                              ⚠️ **MAS A CORREÇÃO DE 08/09 OBRIGA A REABRIR:**
                              a instrução é explícita — «não descartar a possibilidade
                              de ela ser uma ferramenta legítima só porque documento
                              antigo a chamou de supporting engine».
                              Reavaliada contra os 6 testes do §7 da Bíblia:
                              1. o contrato antigo ainda é autoridade? SIM para produto,
                                 mas foi escrito antes de 763 e 184 existirem
                              2. a capacidade evoluiu? SIM — 88 → 763 no acervo, e 88/88
                                 ganharam link para o paper
                              3. inteligência nova? SIM — caseAdherence, countryOfFact
                              4. decision question real? CAP-017, mas não para IT
                              5. valor que não existia? SIM — o bloco «Cosa si sa oltre
                                 il caso» liga ciência a caso com luogo del fatto
                              6. o contrato precisa de atualização? **SIM.**
                              → **VEREDITO: NÃO É KILL. É UM CONTRATO POR ESCREVER.**
EVIDENCE_CHAIN                registo → DOI → paper (88/88 com URL real).
                              **Ressalva medida e grave:** CROP/ISSUE dos 88 papers são
                              o **termo da busca**, não o que o texto prova —
                              87/88 batem QUERY_*, só 37/88 e 34/88 batem PROVED_*,
                              e **39/88 são OFF_CASE**.
FRESHNESS                     `year` por registo. Sem relógio de coleta na tela.
WHAT_IT_CALCULATES            recorrência por autor/instituição
WHAT_UI_CALCULATES            filtros, horizonte, agrupamento por tema
WHAT_BACKEND_CALCULATES       caseAdherence (ordena, não filtra), countryOfFact
WHAT_SHOULD_NOT_BE_CALCULATED_HERE   **autoridade.** «Recorrência não é autoridade» —
                              a régua de ferramenta di-lo e o benchmark do Ask B13
                              RECUSA a pergunta «quem é a maior autoridade».
                              E ranking universal: proibido por missão.
UNKNOWN_BEHAVIOR              excelente: publications.withPublications = 1 de 60,
                              com a nota «um investigador sem publicação aqui não tem
                              nenhuma NESTA LEITURA»
DUPLICATION                   `researchers` (60) alimenta esta tela **e** o diretório de
                              pessoas de S-11 (`people` 66 = researchers + publicPeople)
OVERLAP                       ciência é INPUT de S-01 (arquétipo O6 ciência→campo)
POTENTIAL_VALUE               ALTO, e **crescente**: 763 no acervo contra 88 servidos.
                              A limitação declarada é honesta: só 7 pares distintos
                              existem entre as 13 fichas e o corpus foi recolhido sobre
                              outros. `VISIVEL_PARCIAL` é a resposta correta.
CURRENT_ROLE                  UNKNOWN arquiteturalmente
POSSIBLE_FUTURE_ROLE          **CANONICAL_TOOL para R&D/TECHNICAL** é hipótese viva,
                              **não descartada**. Requer: contrato próprio, extensão
                              de CAP-017 à Itália, e resolver o OFF_CASE 39/88.
                              **Confiança: MÉDIA. PRECISA DE MEDIÇÃO — de utilizador,
                              não de dado.**
WHAT_IS_STILL_UNKNOWN         · GDPR P-008: NAMED_RESEARCHER_PUBLIC_SCREEN =
                                BLOCKED_PENDING_LEGAL_REVIEW. **Bloqueio real.**
                              · 39/88 OFF_CASE: defeito de coleta ou de junção?
```

---

### S-10 · ARCHIVE

```
SURFACE_ID                    S-10-ARCHIVE
VISIBLE_NAME                  Archive · Archivio
CURRENT_COUNT                 1114     (20 por página; paginação declarada)
CURRENT_MENU_GROUP            EVIDENCE AND CONTEXT
ROUTE / VIEW                  #archive
OWNER                         portale.html vista 'archive'
CURRENT_STATE                 CURRENT
DATA_INPUT                    AM.collections.archive (1114) — provenance REAL_DERIVED
INTELLIGENCE_INPUT            **NENHUM.** É índice sobre as outras colecções; não traz
                              facto próprio. `provenanceTotals.indexRows = 1114`,
                              contado à parte de real 17.089 e derived 288.
GENERATOR                     derivação dentro de italy-app-model.js
DECISION_QUESTION             **NENHUMA.** Não existe ficha, contrato ou decisão sobre
                              um Arquivo em nenhum documento do repositório.
TARGET_USER                   NÃO SEI
PRODUCT_CONTRACT              NÃO
AUTHORITY                     UNKNOWN — nem aprovado nem recusado. Ausência, não permissão.
EVIDENCE_CHAIN                herda a de cada item indexado
FRESHNESS                     herdada, não própria
WHAT_IT_CALCULATES            um índice
WHAT_UI_CALCULATES            filtro por tipo e plataforma (archivePlatform 1114/1114
                              preenchido — a melhor cobertura de enum do modelo)
WHAT_BACKEND_CALCULATES       a indexação
WHAT_SHOULD_NOT_BE_CALCULATED_HERE   qualquer juízo
UNKNOWN_BEHAVIOR              n/a
DUPLICATION                   **QUÁDRUPLA E MEDIDA.** Existem quatro acervos:
                              Archive 1114 (índice) · Source Register 194 (proveniência)
                              · Signal Archive 3 (sinais — não é um arquivo) ·
                              **searchIndex 1655 em 17 famílias, sem entrada de menu**,
                              que já indexa tudo o que os outros dizem arquivar
OVERLAP                       total com a pesquisa
POTENTIAL_VALUE               MÉDIO como INVESTIGATION_VIEW · nulo como ferramenta
CURRENT_ROLE                  **`1114` é um contador de linhas.** A home proíbe-o pelo
                              nome («contador de linhas»); a barra imprime-o.
POSSIBLE_FUTURE_ROLE          **INVESTIGATION_VIEW ou ADMIN/DIAGNOSTIC.**
                              A distinção é real e importa: um investigador precisa de
                              varrer tudo; um utilizador de negócio não.
                              A recomendação não é apagar — é **nomear o público**.
                              Se o público for interno, é ADMIN/DIAGNOSTIC e não
                              pertence ao mesmo menu que Opportunity Radar.
                              **Confiança MÉDIA-ALTA em «não é ferramenta».
                              BAIXA em qual das duas é.**
WHAT_IS_STILL_UNKNOWN         quem abre esta tela, e para quê. NÃO MEDIDO.
```

---

### S-11 · SOURCE REGISTER

```
SURFACE_ID                    S-11-SOURCE-REGISTER
VISIBLE_NAME                  Source Register · Registro delle fonti
                              (era «Archivio fonti V21» em 06/09 — RENOMEADO)
CURRENT_COUNT                 194      (era 189/191 — mudou o dado, não só o nome)
CURRENT_MENU_GROUP            EVIDENCE AND CONTEXT
ROUTE / VIEW                  #sources · detalhes: source, person
OWNER                         portale.html vistas 'sources'/'source'/'person'
CURRENT_STATE                 CURRENT
DATA_INPUT                    sources 194 + people 66 (= researchers 60 + publicPeople 15,
                              deduplicado) + news 8
INTELLIGENCE_INPUT            camada de evidência e proveniência
GENERATOR                     scripts/proveniencia.py + pacote
DECISION_QUESTION             **PARCIAL.** O contrato de navegação
                              (DESIGN-DATA-CONTRACT-V1, nível 2, ordem 4) dá-lhe uma:
                              «de onde vem cada coisa?» — e acrescenta a nota decisiva:
                              «**inclui as fontes BLOQUEADAS, com motivo**».
                              Isso não é admin. É produto: a fonte que falhou é
                              conteúdo de primeira classe neste repositório.
TARGET_USER                   quem audita uma afirmação — TECHNICAL · REGULATORY ·
                              LEADERSHIP quando desconfia · e a própria equipa
PRODUCT_CONTRACT              NÃO
AUTHORITY                     **NO, com duas provas** — é motor de suporte («camada de
                              evidência e proveniência», por baixo) **e** a home proíbe
                              textualmente «contador de fontes».
                              ⚠️ **MAS:** o contrato de design de 30/08 dá-lhe entrada
                              de nível 2 com estados GREEN/PARTIAL/BLOCKED. **Dois
                              documentos, duas respostas.** Ver §4, conflito C-02.
EVIDENCE_CHAIN                é ela própria a cadeia
FRESHNESS                     DATA-CLOCK-manifest.json — versão e data por fonte
WHAT_IT_CALCULATES            estado da fonte
WHAT_UI_CALCULATES            agrupamento (sourceGroup preenchido em 31 de 194 —
                              **missPct 84%**, a pior cobertura de enum do modelo)
WHAT_BACKEND_CALCULATES       version_state (5 estados; só NEW_VERSION_CHANGED autoriza
                              emitir evento)
WHAT_SHOULD_NOT_BE_CALCULATED_HERE   qualidade da inteligência que sai da fonte
UNKNOWN_BEHAVIOR              **o melhor do portal em princípio:** SOURCE_FAILED
                              «jamais apresentar como nada mudou»;
                              BASELINE_ESTABLISHED = NOT ENOUGH VERSIONS, nunca NO_CHANGE
DUPLICATION                   `people` partilhado com S-09 · a palavra «arquivo»
                              partilhada com S-10 e S-13
OVERLAP                       toda superfície devia poder saltar para aqui a partir de
                              qualquer facto — hoje **não medido** se isso acontece
POTENTIAL_VALUE               ALTO — é o que torna qualquer afirmação auditável, e é o
                              que o CONTRATO-DE-DESIGN §7 exige («todo número tem um
                              EvidenceLink»)
CURRENT_ROLE                  EVIDENCE_EXPLORER / PROVENANCE SURFACE
POSSIBLE_FUTURE_ROLE          **EVIDENCE_EXPLORER — e a Bíblia propõe que esta classe
                              exista formalmente, precisamente por causa desta
                              superfície.** Não é ferramenta (não responde a uma decisão
                              de negócio), não é admin (é para o cliente), não é context
                              view (não contextualiza — prova).
                              **Confiança: ALTA.**
                              A proibição da home («contador de fontes») é sobre a HOME,
                              não sobre a existência da superfície. São coisas
                              diferentes e foram lidas como a mesma.
WHAT_IS_STILL_UNKNOWN         sourceGroup em 84% vazio — é lacuna de dado ou o enum
                              está errado?
```

---

### S-12 · FIELD SALES CHANNEL

```
SURFACE_ID                    S-12-FIELD-SALES-CHANNEL
VISIBLE_NAME                  Field Sales Channel · Rete Commerciale di Campo
CURRENT_COUNT                 18
CURRENT_MENU_GROUP            INTEGRATIONS · DEMO      ← honestamente rotulado
ROUTE / VIEW                  #field  ⚠️ **fora de AMMESSE** (ver Divergência 1)
OWNER                         portale.html vista 'field'
CURRENT_STATE                 **DEMO.** provenance = SYNTHETIC_DEMO, real 0, demo 18
DATA_INPUT                    fieldMessages 18 — mensagens fabricadas
INTELLIGENCE_INPUT            **NENHUM**
GENERATOR                     fixture
DECISION_QUESTION             n/a — é uma demonstração de integração
TARGET_USER                   COMMERCIAL (hipotético)
PRODUCT_CONTRACT              NÃO
AUTHORITY                     UNKNOWN
EVIDENCE_CHAIN                **NENHUMA, e é isso que a etiqueta DEMO significa**
FRESHNESS                     n/a
WHAT_SHOULD_NOT_BE_CALCULATED_HERE   tudo
UNKNOWN_BEHAVIOR              n/a
POTENTIAL_VALUE               **ALTO como direção, zero como conteúdo.**
                              É a única superfície que aponta para o problema que o
                              produto ainda não resolve: **como é que a inteligência
                              externa chega a quem está no campo, e como é que o que o
                              campo sabe volta para dentro?** Isso é o passo 15 da
                              missão (DECISION TELEMETRY) e o passo 16 (MARKET
                              DEVELOPMENT) numa tela só.
CURRENT_ROLE                  INTEGRATION · EXPERIMENT
POSSIBLE_FUTURE_ROLE          INTEGRATION. **Continua corretamente DEMO — SIM.**
                              O rótulo está no ecrã, o grupo está separado, a cor é
                              outra (âmbar, não verde), a proveniência é SYNTHETIC_DEMO
                              no modelo e conta-se à parte (`demo: 103` em
                              provenanceTotals). **Quatro camadas de honestidade.**
                              É o contra-exemplo positivo de `DEMO ≠ PRODUCT`.
WHAT_IS_STILL_UNKNOWN         a rota `#field` fora de AMMESSE: intenção ou esquecimento?
                              O comentário diz intenção; o menu diz o contrário.
                              **DIVERGÊNCIA POR RESOLVER.**
```

---

### S-13 · SIGNAL ARCHIVE — a 13ª, fora do menu

```
SURFACE_ID                    S-13-SIGNAL-ARCHIVE
VISIBLE_NAME                  Signal Archive · Archivio segnali
CURRENT_COUNT                 3
CURRENT_MENU_GROUP            **NENHUM — saiu da barra em a4fb6d8, deliberadamente**
ROUTE / VIEW                  #future  (EM AMMESSE · em CAPABILITY_OF · vista completa)
                              3 caminhos: linha no fundo do radar · linha da janela
                              colturale · pesquisa
CURRENT_STATE                 CURRENT, fora do menu
DATA_INPUT                    futureSignals 3 (CANONICAL)
INTELLIGENCE_INPUT            OpenAlex (2 sinais) + CELLAR/atos UE (1 sinal)
DECISION_QUESTION             herda a de S-03
PRODUCT_CONTRACT              RADAR-DO-FUTURO-CONTRACT-V1 (partilhado com S-03)
AUTHORITY                     UNKNOWN
POTENTIAL_VALUE               é a prova de que **retirar da vista ≠ retirar do produto**
CURRENT_ROLE                  SUPPORTING_VIEW de S-03
POSSIBLE_FUTURE_ROLE          SUPPORTING_VIEW. **Confiança ALTA.**
WHAT_IS_STILL_UNKNOWN         —
NOTA                          Esta ficha existe porque **um inventário que só conta o
                              menu conta o menu, não o produto.** É a razão pela qual a
                              matriz da Bíblia distingue SURFACE de MENU ENTRY.
```

---

## §4 · O QUE MUDOU ENTRE 06/09 E 08/09 — o primeiro caso real de evolução de produto

Comparação `HISTORICAL (e4f3e8b/9d06d94)` × `CURRENT_OBSERVED (a4fb6d8)`:

| # | mudança medida | classe de evento |
|---|---|---|
| 1 | `Opportunity Radar` **13 → 17** | **A LEI MUDOU, O DADO NÃO.** A partição passou de 13/21/8/1 para 17/21/4/1 sobre os mesmos 43. Causa: a regra de promoção deixou de aceitar «alvo escrito no caso sem fonte que o tenha observado» e passou a exigir `SUPPORTS_SIGNAL` ou `SUPPORTS_DIRECTION`. **É supersessão de produto por mudança de régua** — o caso-escola do §13 da Bíblia |
| 2 | `Portfolio` promovido a **STRUMENTI** | **RECLASSIFICAÇÃO DE SUPERFÍCIE sem registo de decisão** |
| 3 | `Future Radar 44` **entra no menu** | `VALUE_EXISTS = YES e VISIBLE = NO → NÃO ESTÁ INTEGRADO`. Antes: `ROUTES_TO_FUTURE_RADAR = 0`. **Uma superfície com 44 fichas desenhadas e nenhuma porta** |
| 4 | `Label Intelligence 166` **nasce** | **ADMISSÃO DE FERRAMENTA NOVA** — e a única do repositório que chegou com selo, ruleset versionado e claim proibido escrito |
| 5 | `Signal Archive 3` **sai da barra** | **DEMOÇÃO de MENU ENTRY, sem demoção de SURFACE** |
| 6 | `Archivio fonti V21` → **`Source Register`**, 189 → **194** | renomeação + crescimento de população |
| 7 | `productRelationships` **2030 → 5402** | crescimento de 166% no elo mais denso do modelo |
| 8 | `casa.html` deixa de ser alcançável | **FUSÃO DE SUPERFÍCIES**: duas identidades visuais eram dois produtos, mesmo com o mesmo dado |
| 9 | `#field` sai de `AMMESSE`, item de menu fica | **DIVERGÊNCIA NÃO RESOLVIDA** |

> **NENHUMA DESTAS NOVE MUDANÇAS TEM ENTRADA NO `DIARIO-DE-DECISOES.md`.**
> O diário termina em `D-026` (2026-08-30) e numa entrada de 2026-09-02.
> Nove decisões de produto em 48 horas, zero registadas.
> **É o achado mais forte deste inventário, e é o que justifica o Registo Vivo.**

### Conflitos medidos, sem escolher lado

| id | o que existe | o que o contrato diz | por que divergiram | que lei faltava | decisão futura |
|---|---|---|---|---|---|
| **C-01** | 12 vozes de menu | «desenhar um **menu de módulos independentes**» está em O QUE O DESIGN NÃO PODE FAZER | o design agrupou (STRUMENTI × EVIDENZA) sem reclassificar | **SURFACE CLASS** — faltava um vocabulário que distinga ferramenta de vista | a divisão visual atual é boa arquitetura ou navegação temporária? |
| **C-02** | Source Register no menu | (a) SUPPORTING ENGINE «não no menu» + home proíbe «contador de fontes»; (b) DESIGN-DATA-CONTRACT dá-lhe nível 2 ordem 4 | **dois contratos da mesma semana discordam** | precedência entre contratos | qual documento vence? |
| **C-03** | portal só Itália | DESIGN-DATA-CONTRACT: nível 1 é PAÍS (ES·IT·FR) + camada EAME que «aparece mesmo vazia» | o piloto foi de Itália | escopo declarado por build | o `COUNTRY_SELECTOR` é dívida ou decisão? |
| **C-04** | Competitor Watch imprime 577 | «não existe **número único** saindo daqui» | o badge nasceu do padrão do menu | **o menu não é lugar de claim** | o contador sai, ou a superfície muda de classe? |
| **C-05** | 2 linhagens vivas de portal | — | duas missões paralelas tocaram o mesmo casco | **PUBLICATION MANIFEST** — nada declara qual build é o publicado | qual é o portal? |
| **C-06** | S-01 partição 17/21/4/1 | `MEETING_SURFACE_RULE` (Linha A) dá 5/8/13/17 | dois donos, duas leis, ambas testadas | **um dono por juízo** | `surface-contract.mjs` está 3/8 desde `a4508ef` |
| **C-07** | item de menu `#field` | `AMMESSE` não o aceita | correção parcial | rota é parte do contrato de superfície | intenção ou esquecimento? |

---

## §5 · PLACAR

```
CURRENT_OBSERVED @ claude/visible-intelligence-v1 a4fb6d8 · 2026-09-07 21:11 UTC

SUPERFÍCIES NO MENU ................ 12    (2 STRUMENTI · 9 EVIDENCE · 1 DEMO)
SUPERFÍCIES NAVEGÁVEIS ............. 13    (+ Signal Archive, fora do menu)
IDS DE VISTA EM CAPABILITY_OF ...... 27    (12 capacidades + 15 detalhes/legados)
COLECÇÕES NO MODELO ................ 59
RÁCIO MENU / COLECÇÃO .............. 20%

CONTADORES VERIFICADOS ............. 12 / 12   (100%, contra o relato do dono)
DIVERGÊNCIAS DE NÚMERO ............. 0
DIVERGÊNCIAS DE ARQUITETURA ........ 7        (C-01 … C-07)

DECISION QUESTION EXPLÍCITA ........ 4 / 13
    S-01 (MT2) · S-03 (contrato) · S-04 (payload) · S-11 (nível 2, parcial)
    PARCIAL: S-09 (CAP-017, mas não cobre a Itália)

PRODUCT CONTRACT COMPLETO .......... 1 / 13    S-04 Label Intelligence
PRODUCT CONTRACT PARCIAL ........... 2 / 13    S-01 · S-03
SEM PRODUCT CONTRACT ............... 10 / 13

NASCERAM DE DATASET / CAPACIDADE ... 6 / 13
    S-06 Market Pulse · S-07 Field Voices · S-09 Scientific Intelligence ·
    S-10 Archive · S-11 Source Register · S-05 Crop Windows
NASCERAM DE PERGUNTA ............... 3 / 13    S-01 · S-03 · S-04
NASCERAM DE FIXTURE ................ 1 / 13    S-12
INDETERMINADO ...................... 3 / 13    S-02 · S-08 · S-13

AUTHORITY = YES .................... 2 / 13    S-01 · (S-02 por promoção não registada)
AUTHORITY = NO ..................... 4 / 13    S-06 · S-07 · S-08 · S-09
AUTHORITY = UNKNOWN ................ 7 / 13

EVIDENCE CHAIN COMPLETA ............ 3 / 13    S-04 (a mais funda) · S-02 · S-11
EVIDENCE CHAIN VAZIA E MEDIDA ...... 2 / 13    S-05 (29/29 sem SOURCE_ID) · S-12 (demo)

FRESHNESS COMPOSTO E DECLARADO ..... 2 / 13    S-04 (6 relógios) · S-08 (5º relógio)
FRESHNESS = ARITMÉTICA DE DATAS .... 1 / 13    S-05
FRESHNESS NÃO DECLARADO ............ 8 / 13

MUDANÇAS DE PRODUTO EM 48 H ........ 9
REGISTADAS NO DIÁRIO DE DECISÕES ... 0
```

### As três frases que este placar quer dizer

**Primeira.** Das treze superfícies, **uma** tem contrato de produto completo — e é a mais
nova. Label Intelligence chegou a 07/09 com selo criptográfico, 22 regras versionadas,
sete coberturas separadas e a frase «USO AUTORIZADO NÃO É OPORTUNIDADE COMERCIAL» escrita
no próprio payload. **A prática já ultrapassou a doutrina.** A Bíblia não tem de inventar
o padrão: tem de o nomear e de o exigir das outras doze.

**Segunda.** Nove decisões de produto em 48 horas, zero no diário. Não é desleixo — é
**ausência de lugar**. O diário de decisões é para decisões de método; nunca foi desenhado
para receber «Portfolio subiu para STRUMENTI». O Registo Vivo existe para isso.

**Terceira.** O inventário de 06/09 não estava errado. Estava **datado**, e ninguém lhe
tinha posto um relógio. É a cicatriz nº 1, e é a razão pela qual toda linha deste ficheiro
carrega o seu tempo.

---

## §6 · O QUE ESTE INVENTÁRIO NÃO FEZ

Não alterou portal, HTML, CSS, JS, schema, coleta, motor de inteligência, Opportunity,
Field Voices, scoring, sinais ou recomendações. Não fez DDL, escrita em BD, storage,
chamada paga, Apify ou deploy. Não fundiu branches, não escolheu entre as duas linhagens,
não apagou nem renomeou nada.

**Não mediu:**

- se algum utilizador real abre alguma destas telas, e para quê — **não há telemetria**;
- a relação exata entre os 166 rótulos de S-04 e os 173 produtos de S-02;
- se `Source Register` é alcançável a partir de cada facto das outras superfícies;
- o que a linhagem `integration-acervo-portal-v1` (611 justificações de exclusão, 213
  pares reconciliados) perde ao não estar em `visible-intelligence-v1`, e vice-versa;
- o `searchIndex` (1655 entradas, 17 famílias) como superfície;
- as 15 vistas de detalhe, uma a uma.

**`NÃO MEDIDO ≠ NÃO EXISTE`. `NÃO SEI` continua `NÃO SEI`.**
