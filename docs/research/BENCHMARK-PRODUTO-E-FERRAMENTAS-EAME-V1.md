# BENCHMARK DE PRODUTO E FERRAMENTAS — SINTONIA EAME V1

**Status:** RESEARCH ONLY  
**Data:** 2026-09-08  
**Branch:** `research/product-tools-benchmark-v1`  
**Base medida:** `main@df165da928549d9e3427b4c518bd8d70e7fb9058`  
**Implementação:** 0  
**Portal:** 0 alterações  
**Coleta:** 0 alterações  
**Inteligência:** 0 implementação  
**Produção/deploy:** 0

---

## 1. Pergunta de pesquisa

O benchmark não procura um portal para copiar. Procura padrões que explicam como sistemas profissionais fazem a passagem:

`DADO → INTELIGÊNCIA → PRIORIZAÇÃO → CARD → AÇÃO → BRIEF → DECISÃO`

A régua usada em toda a pesquisa foi:

> **Uma ferramenta só tem valor quando melhora uma decisão real, reduz o tempo para entendê-la, ajuda a agir antes ou aumenta a qualidade da preparação. Volume de dados, número de cards, charts, pageviews e tempo no portal não são valor final.**

## 2. Baseline SINTONIA medido antes do benchmark

A inspeção do repositório confirmou uma arquitetura interna que deve ser preservada:

- `italy-app-model.js` funciona como uma única fronteira de ingestão/normalização antes da UI;
- a precedência declarada é `CANONICAL > REAL_SOURCE > REAL_DERIVED > SYNTHETIC_DEMO > DEMO_SCENARIO`;
- ausência de verdade externa vira `NOT_EXTERNALLY_OBSERVABLE` ou estado de conhecimento, não placeholder inventado;
- narrativa bruta de pesquisa não é automaticamente promovida a texto de cliente;
- datas são normalizadas num owner e formatos não reconhecidos não são adivinhados;
- a UI lê coleções normalizadas em vez de contar fixtures por conta própria;
- Brandwell/Design System já é dependência explícita do portal;
- Field Sales Channel aparece na integração inspecionada como `INTEGRAZIONI · DEMO`, com 18 registros sintéticos, e não como verdade operacional.

### Baseline visual reportado pelo dono em 08/09/2026

1. Opportunity Radar — 17  
2. Portfolio — 173  
3. Future Radar — 44  
4. Label Intelligence — 166  
5. Crop Windows — 29  
6. Market Pulse — 157  
7. Field Voices — 79  
8. Competitor Watch — 577  
9. Scientific Intelligence — 88  
10. Archive — 1114  
11. Source Register — 194  
12. Field Sales Channel — 18 · INTEGRATIONS · DEMO

**Achado importante:** esse snapshot exato não está reproduzível em `main@df165da9` nem numa única linha histórica inspecionada. Há estado recente distribuído entre linhas de integração, Opportunity, Label e canonical. Em uma integração anterior, por exemplo, Opportunity havia sido reduzido a 13 casos publicáveis, enquanto outras coleções também tinham contagens diferentes. Portanto:

> **CURRENT VISUAL ≠ CANONICAL TOOL ≠ CURRENT MAIN.**

Isto deve ser resolvido antes de qualquer implementação posterior, mas **não é corrigido nesta missão**.

---

## 3. Sistemas estudados profundamente

Foram estudados **16 sistemas/produtos externos**, com foco em padrões transferíveis, não em identidade visual:

### Decision / intelligence
1. Palantir Foundry
2. Recorded Future
3. Dataminr First Alert
4. AlphaSense
5. Tableau Pulse
6. Feedly Market Intelligence
7. Microsoft Power BI / Copilot delivery
8. OpenCTI

### Agriculture / agronomic DSS
9. Syngenta Cropwise Protector
10. BASF xarvio FIELD MANAGER
11. Bayer Climate FieldView
12. John Deere Operations Center
13. CropX
14. Trapview
15. OneSoil
16. AgroScout

Horta DSS foi estudado como componente agronômico particularmente relevante para xarvio e para frutas/vinhas na Europa, sem ser contado como um 17º sistema profundo independente.

---

## 4. O que os melhores sistemas têm em comum

### 4.1 Eles organizam o trabalho em torno de um objeto real

Palantir usa objetos da Ontology e Object Views como hub de contexto, relações e ações. Recorded Future transforma entidade em Intelligence Card e ponto de pivô. OpenCTI navega entidade/relação como grafo. Nos DSS agrícolas, o objeto é campo/cultura/risco/janela.

**Transferência para SINTONIA:** Crop, Problem, Geography, Product, Active Substance, Label Use, Window, Competitor, Claim, Source e Horizon devem ser objetos compartilhados. As ferramentas são projeções e workflows sobre esses objetos; não bancos isolados por menu.

### 4.2 Acima da dobra aparece o que muda a decisão

Os melhores produtos não começam pela bibliografia. Começam por estado, evento, risco, mudança, prazo ou exceção. Detalhe e evidência vêm por drill-down.

**Transferência:** headline + onde + tempo + por que agora + ação. Fonte fica sempre acessível, mas não precisa ser o herói visual.

### 4.3 Priorização profissional é explicável

Cropwise prioriza áreas por severidade e recência de visita/aplicação. xarvio combina estádio, risco, previsão e momento de proteção. OneSoil descreve uma lista ranqueada do que merece atenção hoje. Palantir demonstra um inbox operacional de alertas que deve ser triado e resolvido.

**Transferência:** Opportunity não deve ser ordenado por um `score` mágico. Deve ser ordenado por **estado de ação no tempo** e desempates explicáveis.

### 4.4 Ação vive no mesmo contexto da inteligência

Palantir Actions aparecem dentro de Object Views/Workshop. John Deere fecha o ciclo plan → monitor → analyze. FieldView já conecta decisões agronômicas a execução downstream. OpenCTI transforma investigação em artefato compartilhável.

**Transferência:** cada Intelligence Product relevante deve terminar com um `WHAT CAN I DO?`, sem transformar recomendação em decisão automática.

### 4.5 O portal não é o único canal

Tableau Pulse entrega digests em email/Slack/Teams. AlphaSense salva buscas, alerta e pode entregar Executive Brief. Power BI envia assinaturas e sumários. FieldView compartilha relatórios por canais móveis.

**Transferência:** mobile/share brief é superfície de produto. PDF é derivado congelado, não o sistema de entrega.

### 4.6 Evidência é progressiva

Recorded Future mostra resumo e risk rules, mas permite aprofundar a evidência. AlphaSense conserva citações e caminho da pesquisa. OpenCTI separa conhecimento quente de exploração/contexto e permite pivô investigativo.

**Transferência:** `Evidence Drawer/Side Panel` claim-linked; resumo na frente, fontes e contraditório a um clique.

### 4.7 Alertas bons representam mudança de estado

Dataminr trabalha a evolução de um evento vivo, com corroboration e live brief atualizado. Tableau Pulse permite seguir, favoritar e escolher cadência. Feedly enfatiza redução de ruído, deduplicação e refinamento.

**Transferência:** nova fonte não merece alerta por existir. Alerta deve sinalizar transição que muda o que a pessoa precisa fazer.

---

## 5. Padrão temporal recomendado para Opportunity Radar

A melhor arquitetura encontrada não é `maior score primeiro`; é **time-to-act + estado da janela de decisão**.

### Estado principal recomendado

1. **AGIR AGORA** — a janela de ação/decisão está aberta ou fechando; atraso pode perder a oportunidade.
2. **PREPARAR AGORA** — a janela agronômica ainda não abriu, mas o lead time comercial/técnico/logístico exige preparação já.
3. **PRÓXIMA JANELA** — existe uma janela futura conhecida, mas ainda não há tarefa que precise começar agora.
4. **MONITORAR / VALIDAR** — sinal relevante, mas sem threshold suficiente para ação ou com evidência incompleta.

Os nomes finais precisam ser testados com usuários ADAMA; a estrutura é a recomendação.

### Dentro de cada estado

Desempatar por fatores **visíveis e separados**, não por um número universal:

- `TIME_TO_ACT` / tempo restante;
- consequência de perder a janela;
- relevância ADAMA e prontidão de resposta;
- qualidade/frescor da evidência;
- geografia/cultura de responsabilidade do usuário.

### Lei temporal estrutural

> **COMMERCIAL PREPARATION WINDOW pode abrir antes de AGRONOMIC ACTION WINDOW.**

O SINTONIA deve guardar e mostrar separadamente:

- agronomic window;
- observed phenology, quando houver;
- commercial lead time;
- time to prepare;
- time to act;
- expiry/deadline regulatório;
- as-of / first observed / last observed.

`CALENDAR DATE ≠ OBSERVED PHENOLOGY` e `APPROXIMATE WINDOW ≠ EXACT DATE` permanecem leis.

---

## 6. Arquitetura recomendada para card

### Camada 1 — 3 segundos / acima da dobra

- **BIG CALL** em linguagem simples;
- crop/problem + geography;
- estado temporal (`AGIR/PREPARAR/PRÓXIMA/MONITORAR` ou nomenclatura validada);
- data/janela/time-to-act explícito;
- uma linha `WHY NOW`;
- ação primária visível.

### Camada 2 — 30 segundos

- what is happening;
- why it matters to ADAMA;
- ADAMA response/implication;
- limitation/unknown principal;
- evidence maturity / freshness;
- objetos relacionados: Portfolio, Label, Window, Competitor, Science/Future.

### Camada 3 — 3 minutos

- evidence drawer/side panel;
- claim → citation mapping;
- documento original, versão e data;
- timeline da evidência;
- contrary evidence;
- unknowns e coverage gaps;
- objetos e investigações relacionados.

### Família de card

Opportunity, Future e Scientific podem compartilhar gramática, **não semântica**.

- Opportunity enfatiza `ACTION WINDOW`, ADAMA response e `WHAT TO DO NOW`.
- Future enfatiza `HORIZON`, triggers, `WHAT WOULD STRENGTHEN/WEAKEN` e preparação.
- Scientific enfatiza `MATURITY`, replicação/grupos independentes, contrary evidence e implicação.

Fazer todos parecerem o mesmo card seria apagar diferenças epistemológicas reais.

---

## 7. Evidência sem poluir a tela

Modelo recomendado:

1. sinal compacto acima da dobra: quantidade/diversidade de fontes + `AS OF` + maturity/freshness;
2. **Open Evidence** abre drawer/painel lateral sem destruir o contexto do card;
3. cada afirmação material aponta para evidências específicas;
4. original, data, versão e proveniência continuam disponíveis;
5. contradiction, stale, partial coverage e UNKNOWN aparecem como estados próprios;
6. Archive e Source Register passam a sustentar investigação/governança, não a ocupar a primeira camada da decisão.

**Não recomendado:** esconder fonte, nem transformar URL/bibliografia no conteúdo principal.

---

## 8. Um Intelligence Product → N Delivery Projections

A pesquisa valida fortemente esta arquitetura.

### Nunca muda entre departamentos

- facts;
- evidence;
- source/provenance;
- fact time / observed time;
- fact location / source location;
- limitations;
- confidence/evidence state;
- UNKNOWN;
- contradiction.

### Pode mudar por papel

- linguagem;
- ênfase;
- ordem;
- nível de detalhe;
- contexto do departamento;
- recommended next action.

Isso evita duas doenças: `tool per department` e verdades diferentes para Sales, Technical, Regulatory ou Leadership.

---

## 9. PDF é suficiente?

**Não.**

PDF continua útil como:

- snapshot fixo;
- impressão;
- offline;
- anexo/audit trail;
- apresentação.

Mas o produto de entrega recomendado é um **SHARE BRIEF mobile-first**, com:

- URL/ID estável;
- versão atual e `AS OF`;
- projeção por papel;
- evidence deep-link;
- related intelligence;
- capacidade de gerar PDF congelado;
- texto curto compatível com email/WhatsApp sem duplicar a verdade.

Mobile não deve ser “desktop espremido”; para RTV é um workflow próprio: entender → perguntar → sugerir → mostrar limitação → abrir evidência → compartilhar.

---

## 10. Redefinição das 12 superfícies — síntese

- **Opportunity Radar — IMPROVE:** vira decision/action inbox comercial orientado por `time-to-act`.
- **Portfolio — RETHINK:** memória operacional da capacidade de resposta ADAMA, não catálogo.
- **Future Radar — IMPROVE:** portfólio de hipóteses/sinais monitorados, com triggers e evidência; não previsão.
- **Label Intelligence — SUPPORTING LAYER + REFERENCE SURFACE:** verdade regulatória-operacional + `what changed since last label`.
- **Crop Windows — FOUNDATIONAL LAYER:** relógio agronômico/temporal compartilhado; não simples ferramenta de calendário.
- **Market Pulse — RETHINK:** somente mudanças externas capazes de alterar prioridade/decisão comercial, com `so what` obrigatório.
- **Field Voices — RETHINK:** newswire/sensor de campo curado, deduplicado e contextual; nunca incidência inferida.
- **Competitor Watch — KEEP + IMPROVE:** conservar core; fortalecer taxonomia, relações e evidence links; sem score universal.
- **Scientific Intelligence — IMPROVE:** chamadas de ciência que podem mudar decisão; papers viram evidência subjacente.
- **Archive — RECLASSIFY:** evidence explorer + histórico + audit/investigation.
- **Source Register — SUPPORTING LAYER:** governança/proveniência/coverage health para analistas/admin, não ferramenta comum de usuário.
- **Field Sales Channel — EXPERIMENT / DELIVERY LOOP:** preservar `DEMO`; futuro canal de distribuição + validação de campo, nunca fonte automática de verdade.

---

## 11. Cross-tool graph recomendado

A hipótese linear inicial deve ser rejeitada. A topologia correta é M:N.

### Objetos compartilhados

`CROP ↔ PROBLEM ↔ GEOGRAPHY ↔ WINDOW ↔ PRODUCT ↔ LABEL_USE ↔ ACTIVE_SUBSTANCE ↔ COMPETITOR ↔ CLAIM ↔ SOURCE ↔ HORIZON`

### Sources of truth por pergunta

- **Label:** o que é oficialmente permitido/verdadeiro sobre produto/uso/versão.
- **Crop Windows:** estado temporal agronômico modelado, com incerteza explícita.
- **Portfolio:** o que a ADAMA consegue responder, montado sobre produto + label + contexto.
- **Scientific:** claims científicos e maturity/contrary evidence.
- **Archive/Source Register:** proveniência, histórico e auditabilidade.
- **Opportunity/Future/Market/Field/Competitor:** produtos de inteligência que sintetizam e consomem os owners acima.

### Links de maior valor

- Science ↔ Future;
- Future → Opportunity quando trigger/evidence muda de estado;
- Crop Windows → Opportunity + Portfolio;
- Label → Portfolio + Opportunity;
- Portfolio → Opportunity;
- Field Voices → Future/Opportunity/Science validation;
- Competitor → Opportunity/Portfolio/Future;
- Market → Opportunity/Future;
- Opportunity → briefs/actions;
- toda claim → Evidence/Archive/Source.

---

## 12. Alert architecture

### Merece alert

- entrada em `AGIR AGORA`;
- entrada em `PREPARAR AGORA`;
- janela/deadline materialmente alterada;
- label change com impacto real;
- nova contradição que muda confiança/ação;
- tarefa/validação atribuída;
- watched item muda de decisão.

### Fica no portal

- contexto sem mudança de decisão;
- pesquisa incremental;
- novas fontes redundantes;
- informação exploratória.

### Daily digest

- action inbox do papel;
- transições relevantes nas últimas 24h;
- itens seguidos.

### Weekly brief

- Future;
- Science;
- Market;
- padrões emergentes;
- cobertura/unknowns estratégicos.

---

## 13. Uncertainty UX

Não usar um único percentual de confiança se ele não for calibrado e não disser **confiança em quê**.

Mostrar dimensões independentes:

1. **Evidence maturity:** emergente / corroborada / estabelecida (nomenclatura a validar).
2. **Coverage:** parcial / adequada / ampla.
3. **Relation state:** supported / mixed / contradicted.
4. **Freshness:** current / stale + `LAST OBSERVED`.
5. Para Future: horizon + trigger dependency + o que fortaleceria/enfraqueceria.

`UNKNOWN` não é erro de UI; é estado do conhecimento.

---

## 14. Fontes primárias de produto consultadas

**26 fontes primárias oficiais** foram usadas para provar capacidades declaradas dos produtos. Marketing oficial prova que o produto declara/expõe a função; **não prova eficácia**. Evidência acadêmica sobre alert fatigue/uncertainty foi usada separadamente.

| # | Product | Feature | URL | Date | Lesson | Transferability | Copy risk |
|---|---|---|---|---|---|---|---|
|1|Palantir Foundry|Standard Object Views|https://www.palantir.com/docs/foundry/object-views/standard-object-views|access 2026-09-08|object as contextual hub|HIGH|do not copy UI|
|2|Palantir Foundry|Actions in platform|https://www.palantir.com/docs/foundry/action-types/use-actions|access 2026-09-08|action in object workflow|HIGH|avoid automatic business decision|
|3|Palantir Foundry|Workshop alert inbox|https://www.palantir.com/docs/foundry/workshop/getting-started/index.html|access 2026-09-08|prioritize/respond/resolve inbox|HIGH|SINTONIA is not ops platform|
|4|Recorded Future|Intelligence Cards overview|https://support.recordedfuture.com/hc/en-us/articles/115001398928-Overview-of-Intelligence-Cards|access 2026-09-08|entity card = triage + pivot|HIGH|security semantics differ|
|5|Recorded Future|Domain Intelligence Cards|https://support.recordedfuture.com/hc/en-us/articles/115001398988-Domain-Intelligence-Cards|updated 2025-07-11|summary + rules + evidence tabs|MEDIUM-HIGH|do not copy universal risk score|
|6|Dataminr|First Alert|https://www.dataminr.com/products/first-alert/|access 2026-09-08|corroboration + evolving live brief|HIGH|vendor speed/accuracy claims unvalidated here|
|7|Dataminr|Executive awareness|https://www.dataminr.com/use-cases/executive-official-awareness/|access 2026-09-08|role/geography/topic relevance|HIGH|crisis workflow differs|
|8|AlphaSense|Deep Research|https://help.alpha-sense.com/hc/en-us/articles/42391092171795-Deep-Research-Conduct-In-Depth-Multi-Step-Research-Autonomously|updated 2026|short work product backed by citations|HIGH|do not expose chain-of-thought as product|
|9|AlphaSense|Saved searches + alerts|https://help.alpha-sense.com/hc/en-us/articles/41815267178899-Save-Searches-and-Create-Email-Alerts-in-AlphaSense|updated 2026-06-08|monitor without re-running research|HIGH|alert only state change/relevance|
|10|Tableau Pulse|Pulse overview|https://help.tableau.com/current/online/en-gb/pulse_intro.htm|access 2026-09-08|personalized insight around followed metrics|MEDIUM|SINTONIA is not metric BI|
|11|Tableau Pulse|Explore + digest preferences|https://help.tableau.com/current/online/en-us/pulse_explore_metrics.htm|access 2026-09-08|daily/weekly/monthly; email/Slack/Teams|HIGH|do not reduce intelligence to metrics|
|12|Feedly Market Intelligence|AI Feeds guide|https://docs.feedly.com/article/699-guide-to-ai-feeds-market-intel|access 2026-09-08|relevance refinement/noise reduction|HIGH|attention ≠ fact|
|13|Feedly Market Intelligence|Product overview|https://feedly.com/market-intelligence|access 2026-09-08|monitor trends/competitors into work products|MEDIUM-HIGH|avoid source-volume as value|
|14|Power BI|Mobile data alerts|https://learn.microsoft.com/en-us/power-bi/explore-reports/mobile/mobile-set-data-alerts-in-the-mobile-apps|access 2026-09-08|mobile alerting tied to state/threshold|MEDIUM|generic metric thresholds not enough|
|15|Power BI|Copilot summaries in subscriptions|https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-summaries-in-subscriptions|updated 2026-07-23|summary delivered with link/snapshot|HIGH|preview capability; do not depend on feature|
|16|OpenCTI|Knowledge overview|https://docs.opencti.io/latest/usage/overview/|access 2026-09-08|hot vs cold knowledge; entity history|HIGH|cyber ontology differs|
|17|OpenCTI|Pivot and investigate|https://docs.opencti.io/latest/usage/pivoting/|access 2026-09-08|graph investigation + share/export|HIGH|do not make graph the default UI|
|18|Syngenta Cropwise|Protector|https://www.cropwise.com/protector|access 2026-09-08|severity + recency + scouting prioritize work|HIGH|field management not SINTONIA scope|
|19|BASF xarvio|FIELD MANAGER Protection|https://www.xarvio.com/us/en/products/field-manager/protection.html|access 2026-09-08|risk + observations + protection timing|VERY HIGH|no field-specific prescription without data|
|20|BASF xarvio|FIELD MANAGER|https://www.xarvio.com/us/en/products/field-manager.html|access 2026-09-08|growth stage/risk/actionable alerts|VERY HIGH|farm DSS boundary|
|21|Bayer FieldView|Farm information → answers|https://www.bayer.com/en/us/news-stories/fieldview-features|access 2026-09-08|at-a-glance exceptions and field prioritization|HIGH|telemetry/farm data not transferable|
|22|John Deere|Operations Center features|https://www.deere.com/en-us/products-solutions/technology-solutions/precision-ag-technology/operations-center/features|access 2026-09-08|setup → plan → monitor → analyze|MEDIUM-HIGH|machine execution out of scope|
|23|CropX|Disease Control|https://cropx.com/cropx-system/disease-control/|access 2026-09-08|risk map + infection chance + spray conditions|HIGH for time UX|field sensor/model scope differs|
|24|Trapview|Forecast|https://app.trapview.com/trapview_help/html/forecast_mob.html|access 2026-09-08|observation → forecast → development stage|HIGH|forecast must remain model state|
|25|OneSoil|Platform|https://onesoil.ai/en/platform|access 2026-09-08|ranked list of what needs attention today|VERY HIGH|satellite/farm ops not core|
|26|AgroScout|Platform|https://agro-scout.com/|access 2026-09-08|risk/inspection attention workflow|MEDIUM-HIGH|inspection data ≠ external signal|

### Evidência acadêmica complementar

- alert fatigue: systematic/scoping reviews sobre excesso, relevância, papel do usuário e resposta sustentada;
- uncertainty visualization: revisões mostram que não existe uma visualização universalmente superior; contexto, tarefa e carga cognitiva importam.

Conclusão aplicada: **role-specific alerting + state transitions + progressive disclosure** é mais defensável do que “mais alertas” ou “um confidence badge para tudo”.

---

## 15. Limites de transferência

O SINTONIA **não é farm management software**. Portanto não transferir de DSS agrícolas:

- machine telemetry;
- sprayer control;
- farm ERP;
- field prescription engine;
- dose recommendation field-specific sem dados e contrato adequados;
- pretendida precisão de phenology/risk quando só temos inteligência externa regional.

Também não transferir de security intelligence:

- risk score universal;
- severidade de ameaça como se fosse prioridade comercial;
- workflow de incident response literal.

Transferir o **padrão cognitivo**: objeto, estado, tempo, evidência, pivô, ação, owner e atualização.

---

## 16. Conclusão

O benchmark não recomenda aumentar o número de ferramentas. Recomenda reduzir a distância entre inteligência e decisão.

O SINTONIA tem maior chance de gerar valor quando:

1. a home aponta o que precisa de atenção;
2. Opportunity organiza pelo momento de agir/preparar;
3. Portfolio responde o que a ADAMA consegue fazer legal e tecnicamente naquele contexto;
4. Crop Windows funciona como relógio compartilhado;
5. Label funciona como verdade regulatória;
6. Science/Future/Field mantêm fronteiras de evidência e incerteza;
7. cada card termina numa ação humana clara;
8. o mesmo produto de inteligência ganha briefs por papel sem fabricar fatos diferentes;
9. mobile/share entrega inteligência onde Sales/RTV trabalham;
10. valor é medido por decisões/ações melhoradas, não pelo tamanho do portal.
