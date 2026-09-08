# HANDOFF — BENCHMARK DE PRODUTO SINTONIA EAME V1

**Mission:** research only  
**Date:** 2026-09-08  
**Branch:** `research/product-tools-benchmark-v1`  
**Initial base HEAD:** `df165da928549d9e3427b4c518bd8d70e7fb9058`  
**Implementation:** 0  
**Production:** 0

> Este handoff é input/evidence para a Bíblia da Entrega e partes da Bíblia da Inteligência. Não substitui esses owners.

---

## A. HEAD inicial/final

**Inicial:** `main@df165da928549d9e3427b4c518bd8d70e7fb9058`.  
**Final:** medir a ref remota depois deste commit e registrar na entrega externa; este próprio commit ainda não pode antecipar o seu SHA.

## B. Quantos sistemas externos foram estudados profundamente?

**16.**

## C. Quais?

1. Palantir Foundry
2. Recorded Future
3. Dataminr First Alert
4. AlphaSense
5. Tableau Pulse
6. Feedly Market Intelligence
7. Microsoft Power BI / Copilot delivery
8. OpenCTI
9. Syngenta Cropwise Protector
10. BASF xarvio FIELD MANAGER
11. Bayer Climate FieldView
12. John Deere Operations Center
13. CropX
14. Trapview
15. OneSoil
16. AgroScout

Horta DSS foi estudado como extensão agronômica relevante dentro do benchmark xarvio/EAME.

## D. Quantas fontes primárias?

**26 fontes primárias oficiais de produto/documentação**, registradas com URL, produto, feature, lesson, transferability e copy risk no benchmark principal.

Marketing oficial foi usado apenas como prova de capacidade declarada, não como prova de eficácia. Revisões acadêmicas complementares foram usadas para alert fatigue e uncertainty UX.

## E. Padrões mais importantes para Opportunity Radar

- organizar por **action state + time-to-act**;
- big call simples;
- where/window visíveis;
- why now antes do detalhe;
- ADAMA response defensável e label-linked;
- primary action visível;
- evidence one click away;
- related objects como pivôs;
- role-specific brief;
- no magic score.

## F. Melhor maneira de ordenar oportunidades no tempo

**Por estado de decisão no tempo:**

1. AGIR AGORA
2. PREPARAR AGORA
3. PRÓXIMA JANELA
4. MONITORAR / VALIDAR

Dentro do estado: tempo restante → consequência de perder a janela → prontidão da resposta ADAMA → qualidade/frescor de evidência → responsabilidade geográfica/cultura do usuário.

Os nomes finais precisam de teste. A arquitetura temporal é a recomendação.

## G. Melhor arquitetura para card

**3 seconds / 30 seconds / 3 minutes.**

3s: Call + Where + Time + Why Now + Action State.  
30s: what/why/ADAMA implication/action/limitation/evidence state.  
3min: evidence drawer + claims/sources + history + contradiction + related intelligence.

Opportunity, Future e Science compartilham família, mas não a mesma semântica.

## H. Melhor modelo para evidência sem poluir tela

**Progressive disclosure com claim-linked Evidence Drawer/Side Panel.**

Acima da dobra: evidence state/freshness/unknown.  
Um clique: suporte/contrário/source role/time/location/original/version.  
Archive/Source Register sustentam investigação e governança.

## I. Como adaptar por departamento?

`ONE INTELLIGENCE PRODUCT → N DELIVERY PROJECTIONS`.

Nunca mudam: facts, evidence, source, time, location, limitations, confidence/evidence state, unknown, contradiction.  
Podem mudar: language, emphasis, order, recommended action, context, detail.

Projeções estudadas: RTV, Sales Manager, Marketing, Market Development, Technical, Supply, Regulatory, Leadership e EAME Controller.

## J. PDF é suficiente?

**Não.** PDF é snapshot offline/print/audit/presentation.

## K. Papel recomendado para mobile/share brief

**Superfície de produto de primeira classe**, principalmente para RTV/Sales. Share Brief mobile-first deve carregar versão/as-of, role projection, evidence deep-link e link para a verdade corrente. PDF é um derivado congelado.

## L. O que Portfolio deveria virar?

**Operational Response Memory da ADAMA**, não catálogo.

Pergunta: `O que temos para responder a este problema, nesta cultura, neste país e neste momento, dentro do label?`

## M. Definição recomendada para Future Radar

**Portfólio de sinais/hipóteses monitorados que podem passar a importar e para os quais a ADAMA pode precisar observar, validar ou preparar antes.**

Não é previsão. Precisa de horizon, trigger, evidence maturity, strengthening/weaking evidence, contrary evidence, unknown e owner/preparation.

## N. Como apresentar incerteza futura?

Não um percentual único. Separar:

- evidence maturity;
- coverage;
- supported/mixed/contradicted;
- freshness;
- horizon/trigger dependency;
- what strengthens/weaken;
- explicit UNKNOWN.

## O. Label precisa mudar?

**Não precisa ser reinventada.** Deve ser tratada arquiteturalmente como regulatory truth layer + reference surface. A melhoria de maior valor é `WHAT CHANGED SINCE LAST LABEL` + impactos ligados.

## P. Papel arquitetural de Crop Windows

**Relógio agronômico compartilhado do SINTONIA.** Foundational temporal layer que alimenta Opportunity, Portfolio, RTV/Sales e parte de Future/Field context.

Lei: calendar ≠ observed phenology; approximate window ≠ exact date.

## Q. Definição proposta para Market Pulse

> **Mudança externa de mercado que pode alterar uma decisão/prioridade/preparação/comportamento comercial da ADAMA, com `so what`, user e decision impact explícitos.**

Commodity/trade/weather/production/chart são evidências, não o produto por si.

## R. Formato proposto para Field Voices

**Curated Field Newswire / Signal Sensor.**

Headline + smart summary + why it matters + where/crop/problem + recency + source diversity/role + signal confidence + original voices.

Field voice ≠ incidence.

## S. Competitor precisa de mudança grande?

**Não. KEEP + IMPROVE.** Fortalecer taxonomia, evidence, cross-links e distinção entre registered response, advertising/public communication, technical activity, launch, event e product change. Sem universal Competitor Score.

## T. Proposta para Scientific Intelligence

**Science Calls que podem mudar decisão, não lista de papers.**

Call + what science says + ADAMA implication + maturity + horizon/applicability + independent groups/replication quando medido + contrary evidence + next action + unknown.

## U. Recent Research fica onde?

**Secondary / underlying evidence panel**, timeline ou research explorer sob Scientific Intelligence. Pode ser pesquisável, mas não deve dominar a primeira tela.

## V. Quais ferramentas devem usar a mesma família de card?

**Opportunity, Future e Scientific** — mesma gramática/base de interação, com campos epistemológicos próprios.

## W. Quais NÃO devem ser forçadas nessa família?

Portfolio, Label, Crop Windows, Market, Field Voices, Archive, Source Register e Field Sales Channel. Competitor pode reutilizar componentes, mas sua gramática é Event/Change Card.

## X. Cross-links mais valiosos

- Science ↔ Future;
- Future → Opportunity por promoção governada;
- Crop Windows → Opportunity + Portfolio;
- Label → Portfolio + Opportunity;
- Portfolio → Opportunity;
- Field Voices → Future/Opportunity/Science validation;
- Competitor → Opportunity/Portfolio/Future;
- Market → Opportunity/Future;
- Opportunity → brief/action;
- toda claim → Evidence/Archive/Source.

## Y. Melhor padrão para ação

Uma primary action visível + ações secundárias contextuais:

`GENERATE BRIEF · SHARE · FOLLOW/WATCH · ASSIGN/SEND · REQUEST VALIDATION · CREATE INVESTIGATION · OPEN RELATED · ASK SINTONIA · OPEN EVIDENCE`.

Ação não decide automaticamente pela ADAMA.

## Z. Como medir valor de cada ferramenta?

| Surface | Primary value metric |
|---|---|
| Opportunity | intelligence→action lead time; action before window; missed-window rate |
| Portfolio | time to defensible response; label-safe response coverage |
| Future | preparation before trigger; signal→validation; false alarm/kill rate |
| Label | official change detection + propagation latency; outdated decision avoided |
| Crop Windows | projected vs observed calibration; actions in correct timing |
| Market | real investigations/plan changes started; false relevance rate |
| Field Voices | signal→validation; corroboration time; duplicate/noise reduction |
| Competitor | material event→decision/response; taxonomy/provenance completeness |
| Science | science call→validation/decision/Future; contrary evidence coverage |
| Archive | evidence retrieval/audit reconstruction time |
| Source Register | provenance completeness/freshness/coverage gap closure |
| Field Sales Channel | brief-to-field use + feedback/validation loop closure |

Pageviews/clicks/time-on-page são diagnósticos de uso, não valor final.

## AA. Novos TOOL_CANDIDATES

### 1. Decision Inbox / Action Inbox
Pode ser a **home**, não uma 13ª ferramenta. Une Intelligence Products por role/geography/time/action state.

### 2. Validation Queue / Investigation Workspace
Para Market Development/Technical/Regulatory fecharem sinais/unknowns antes de promoção.

Não implementar sem medir workflow real da ADAMA.

## AB. Anti-padrões mais perigosos

1. fake prediction;
2. one magic score;
3. product-on-crop-as-solution;
4. field voice-as-incidence;
5. calendar-as-phenology;
6. source-location-as-fact-location;
7. publication-time-as-fact-time;
8. regulatory-deadline mixing;
9. chart without so-what;
10. everything-is-an-alert;
11. tool-per-dataset;
12. tool-per-department;
13. source hidden / source as hero;
14. brief-as-new-truth;
15. demo-as-canonical;
16. mobile-as-shrunk-desktop.

## AC. Princípios de produto recomendados

1. **DECISION FIRST**
2. **WHY NOW BEFORE DETAIL**
3. **TIME IS FIRST-CLASS**
4. **LOCATION IS FIRST-CLASS WHEN IT CHANGES ACTION**
5. **ACTION VISIBLE**
6. **ONE TRUTH, MANY ROLE PROJECTIONS**
7. **EVIDENCE ONE CLICK AWAY**
8. **UNKNOWN AND CONTRADICTION VISIBLE**
9. **NO MAGIC SCORE**
10. **NO FALSE CERTAINTY / FAKE PREDICTION**
11. **STATE TRANSITIONS, NOT CARD VOLUME, DRIVE ALERTS**
12. **EXTERNAL SIGNAL ≠ FIELD FACT**
13. **LABEL TRUTH GATES RESPONSE**
14. **WINDOW ≠ DATE; PHENOLOGY ≠ CALENDAR**
15. **PRODUCTS ARE RESPONSES, NOT CATALOG ITEMS**
16. **TOOLS SHARE OBJECTS, NOT COPIED DATA**
17. **MOBILE IS DELIVERY, NOT MINI-DESKTOP**
18. **MEASURE DECISION CHANGE, NOT ENGAGEMENT**
19. **THE HUMAN REMAINS THE DECISION OWNER**

## AD. Pulos do gato que mudam a arquitetura

1. Home como Decision Inbox, não dashboard.
2. Opportunity por time-to-act, não score.
3. Commercial prep window abre antes da agronomic window.
4. One Intelligence Product → N Delivery Projections.
5. Cross-tool graph é M:N, não pipeline linear.
6. Future/Science/Field precisam de promoção epistemológica explícita.
7. Portfolio = memória de resposta.
8. Label = truth layer antes de ser menu.
9. Evidence = progressive/claim-linked.
10. Mobile Share Brief = produto; PDF = derivado.
11. Alert = state transition.
12. Field Sales pode fechar feedback loop sem promover anedota a fato.
13. Archive/Source Register podem ser supporting layers.
14. Opportunity = interseção problema × tempo × geografia × resposta ADAMA × label × evidência.
15. Card family não pode apagar diferenças epistemológicas.
16. Market Pulse só existe quando uma decisão pode mudar.

## AE. O que continua UNKNOWN?

- qual ref é o `CURRENT VISUAL` único que reproduz os 12 counts de 08/09/2026;
- qual branch/commit será declarado canonical/publish owner após integração de Opportunity + Label + System Map;
- commercial lead-time por crop/product/role;
- quais action-state names funcionam melhor para usuários ADAMA Itália;
- owner/régua final de evidence maturity e science maturity;
- volume real de alertas tolerável por role;
- workflow real de Market Development para validation;
- como Supply usa sinais externos antes de private data;
- permissões/identity/canais oficiais para mobile/share/WhatsApp/email;
- causalidade entre SINTONIA e sales outcomes;
- quais windows têm observed phenology suficiente versus calendário/modelo;
- completude atual de Label change diff em todos os 166 itens reportados;
- exact value/cost attribution para EAME Controller;
- quais private systems, se algum dia conectados, terão contrato separado.

## AF. Implementação?

**0.**

## AG. Produção?

**0.**

## AH. Branch pushada?

**SIM.** Todos os artefatos desta missão são commits diretos na branch remota `research/product-tools-benchmark-v1`. Não houve merge.

---

# SYSTEM MAP — recomendação futura, não implementação

O System Map deve distinguir tipos arquiteturais, não desenhar tudo como “ferramenta”:

- **TOOL** — workflow voltado a uma decision question;
- **SURFACE** — forma de visualizar/interagir;
- **INTELLIGENCE PRODUCT** — unidade versionada de inteligência;
- **FOUNDATIONAL / TRUTH LAYER** — ex.: Label, Crop Windows owners;
- **DELIVERY PROJECTION** — role brief/mobile/email/PDF;
- **ACTION** — assign/share/follow/validate/investigate;
- **BRIEF** — projeção de um Intelligence Product;
- **USER ROLE** — Sales/RTV/etc.;
- **VALUE LOOP** — intelligence→action→decision→outcome/learning;
- **EVIDENCE / SOURCE** — proveniência abaixo dos products;
- **RELATION** — M:N entre objetos, com owner e significado.

O mapa deve permitir passar o mouse/clicar e responder:

1. o que este nó produz?
2. o que consome?
3. de quem é source of truth?
4. quem usa?
5. qual decisão melhora?
6. que ações gera?
7. como o valor volta ao sistema?

---

# Em palavras fáceis para Luciano

O maior aprendizado não é “fazer cards mais bonitos”. É **trocar a lógica do portal**.

Opportunity fica melhor quando diz **o que precisa ser feito primeiro no tempo**.  
Portfolio fica melhor quando responde **o que a ADAMA realmente tem para aquele problema agora**.  
Crop Windows vira o relógio que dá contexto às oportunidades.  
Label vira a trava de verdade oficial.  
Future passa a dizer **o que estamos observando e o que teria de acontecer**, sem fingir previsão.  
Science deixa os papers por baixo e coloca a conclusão decisória por cima.  
Field Voices vira um noticiário/sensor curado do campo e nunca chama conversa de incidência.  
Market só sobe algo quando consegue explicar **qual decisão pode mudar**.  
Competitor precisa mais de conexões/taxonomia do que redesign.  
Archive e Source Register continuam fundamentais, mas como sustentação/auditoria.  
Field Sales pode virar o caminho que leva o brief ao RTV e traz validação de volta.

E a home, no futuro, provavelmente deve parar de ser um lugar para escolher ferramentas e virar o lugar que responde:

> **“Luciano, estas são as coisas que merecem atenção agora — estas você age, estas prepara, estas só monitora.”**
