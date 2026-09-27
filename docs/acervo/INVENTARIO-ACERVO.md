# INVENTÁRIO DO ACERVO — o que já está no repositório, e o lugar certo de cada coisa

> **GERADO** por `node pacote/acervo_inventario.mjs` — não editar à mão. `--conferir` prova que este ficheiro é o dos dados.

Lei D97: `COLLECTION → SALA → INTELLIGENCE (e INTELLIGENCE TOOLS) → POTE → CASCO`. Dado coletado nunca vai direto do repo para o casco.

## As classes

- **a** — SAIDA_DE_INTELLIGENCE_TOOL — vai ao pote como produto da ferramenta, com a data do snapshot, sem recalcular
- **b** — REFERENCIA_OFICIAL — insumo da Intelligence; no pote so como objeto referenciado/procedencia
- **c** — ITEM_COLETADO — NAO vai ao casco; passa pela Intelligence (ENTRADA-INTELLIGENCE-ACERVO.json)
- **d** — FORA — demo, simulado, CLIENT_SAFE=false, oportunidade nao provada, interpretacao fora da Intelligence
- **NAO_SEI** — nao se sabe; o motivo vai escrito

Conjunto canónico: italia-portale/client/italy-handoff-v21.js (V21-ef6e7e5f37eaa6e6) — o que o portal carrega; copias noutros ficheiros sao DUPLICADO_DE medido pelo ID.

## Contagem por classe

| classe | conjuntos (sem cópias) | registos (sem cópias) | blocos | conjuntos (com cópias) | registos (com cópias) |
|---|---:|---:|---:|---:|---:|
| a | 5 | 555 | 0 | 5 | 555 |
| b | 18 | 9572 | 2 | 35 | 15788 |
| c | 11 | 2080 | 0 | 27 | 3934 |
| d | 68 | 323 | 49 | 71 | 364 |
| NAO_SEI | 9 | 100 | 0 | 9 | 100 |

Itens coletados (classe c, sem cópias) entregues à Intelligence: **2080** em `docs/intelligence/acervo/ENTRADA-INTELLIGENCE-ACERVO.json`.

## Os ficheiros

| ficheiro | global | o portal carrega | datas do ficheiro | sha256 |
|---|---|---|---|---|
| `italy-label-intelligence.js` | `window.ITALY_LABEL_INTELLIGENCE` | sim | BUILT_AT 2026-09-06 · DATA_DATE 20260831 · DATA_SNAPSHOT_ID PROD_FTS_6_20260831 · COLLECTED_AT 2026-09-04 · RUN RUN-2026-09-06-C | `9407742792c1…` |
| `italy-handoff-v21.js` | `window.ITALY_HANDOFF_V21` | sim | buildId V21-ef6e7e5f37eaa6e6 · packageBuiltAt 2026-09-02 · referenceDate 2026-09-02 | `96e0e721a3f7…` |
| `italy-v21.js` | `window.ITALY_HANDOFF_V21` | NÃO | BUILD_ID V21-843baf4229d93598 · BUILT_AT 2026-09-02 · REFERENCE_DATE 2026-09-02 | `ca384ab06c8e…` |
| `italy-ingested.js` | `window.ITALY_INGEST` | sim | BUILT 2026-09-02 | `68191efda3da…` |
| `italy-catalog.js` | `window.ITALY_CATALOG` | sim | BUILT 2026-09-02 | `6c14ee564589…` |
| `italy-real-intelligence.js` | `window.ITALY_REAL` | sim | LAST_CHECKED 2026-09-01 | `2a0d5e092b79…` |
| `italy-demo-data.js` | `window.ITALY_DEMO` | sim | NÃO SEI | `f843629c0bea…` |
| `meeting-intelligence-snapshot.js` | `window.MEETING_INTELLIGENCE` | sim | BUILD_ID V21-ef6e7e5f37eaa6e6 · GENERATED_AT 2026-09-07T19:23:48Z · MEETING_CUTOFF 2026-09-07T19:23:48Z · SOURCE_HEAD fb96f49d | `3c3e0a393954…` |
| `italy-casa.js` | `window.ITALY_CASA` | sim | DATA_DE_REFERENCIA 2026-09-04 | `2f1e9a3f473a…` |
| `italy-canonical-windows.js` | `window.ITALY_CANONICAL` | sim | referenceDate 2026-09-02 · version 1.0 | `883cc83a6b66…` |
| `adama-relevance.js` | `window.ADAMA_RELEVANCE` | sim | BUILD_ID V21-ef6e7e5f37eaa6e6 · SOURCE_HEAD fb96f49d | `212a1128f47d…` |
| `italy-label-verdicts.js` | `window.ITALY_LABEL_VERDICTS` | sim | AUDIT_DATE 2026-09-02 | `af3e39a7acf9…` |

## Os conjuntos

| conjunto | n | classe | data do dado (campo: min → max) | coleta | PROVENANCE | CLIENT_SAFE | cópia de | motivo |
|---|---:|---|---|---|---|---|---|---|
| `italy-label-intelligence.js::products` | 166 | **a** | label_effective: 2016-12-19 → 2026-07-29 (161/166) | captured_at: 2026-09-04 → 2026-09-04 (163/166) | (sem campo) 166 | (sem campo) 166 | — | leitura selada do rotulo oficial pela ferramenta pilot-label-intelligence (selo CONTENT_SHA256 recalculado) |
| `italy-label-intelligence.js::objects` | 210 | **a** | VALID_FROM: 2025-07-21 → 2026-08-31 (51/210) · VALID_FROM sem data em 159 | CAPTURED_AT: 2025-07-21 → 2026-09-04 | (sem campo) 210 | (sem campo) 210 | — | objetos de registro da mesma ferramenta (diferencas entre snapshots oficiais) |
| `italy-label-intelligence.js::versions` | 54 | **a** | date: 2025-07-14 → 2026-08-31 | NÃO SEI | (sem campo) 54 | (sem campo) 54 | — | as versoes do registro oficial que a ferramenta leu — procedencia da propria ferramenta |
| `italy-label-intelligence.js::crop_check_list` | 76 | **a** | NÃO SEI | NÃO SEI | (sem campo) 76 | (sem campo) 76 | — | agregado selado da ferramenta (crop_check) |
| `italy-label-intelligence.js::pair_check_list` | 49 | **a** | NÃO SEI | NÃO SEI | (sem campo) 49 | (sem campo) 49 | — | agregado selado da ferramenta (pair_check) |
| `italy-handoff-v21.js::activeIngredients` | 53 | **b** | REFERENCE_DATE: 2026-09-02 → 2026-09-02 | NÃO SEI | EVIDENCE_SOURCED 53 | true 53 | — | substancias ativas com estado de aprovacao UE (EU pesticides database / CELEX) |
| `italy-handoff-v21.js::agrometConditions` | 44 | **c** | REFERENCE_DATE: 2025-02-20 → 2026-09-02 (39/44) · REFERENCE_DATE sem data em 5 | NÃO SEI | REAL_SOURCE_LAST_MILE 44 | false 30 · true 14 | — | condicoes agrometeorologicas publicadas → **windows** (G0 → condicao agrometeorologica e contexto, nao janela) |
| `italy-handoff-v21.js::clientSafeCrossings` | 19 | **d** | NÃO SEI | NÃO SEI | (sem campo) 19 | false 19 | — | cruzamentos V2.1: CLIENT_SAFE=false em todos (o nome do conjunto nao e o estado dos registos) |
| `italy-handoff-v21.js::competitorActivities` | 577 | **c** | PUBLISHED_AT: 2011-04-29 → 2026-08-11 (147/577) | NÃO SEI | REAL_SOURCE 561 · REAL_SOURCE_LAST_MILE 16 | false 8 · true 569 | — | anuncios/atividade de concorrentes (Meta Ad Library) → **competitors** (G0 → crossing concorrente × produto × cultura (T4_REGISTRATION_EVIDENCE_ID exigido)) |
| `italy-handoff-v21.js::cropEconomics` | 2978 | **b** | REFERENCE_DATE: 2024-01-10 → 2026-12-31 (2976/2978) | NÃO SEI | REAL_DERIVED 981 · REAL_SOURCE_LAST_MILE 1997 | false 2965 · true 13 | — | estatistica oficial (ISTAT/Eurostat) de peso economico da cultura |
| `italy-handoff-v21.js::currentFieldSignals` | 7 | **c** | NÃO SEI | NÃO SEI | REAL_FACT 5 · REAL_SOURCE 2 | true 7 | — | sinais de campo correntes com fonte → **windows** (G0 → sinal de campo com fonte e data) |
| `italy-handoff-v21.js::events` | 40 | **c** | DATE: 2026-02-04 → 2027-04-11 (18/40) | NÃO SEI | REAL_SOURCE 18 · REAL_SOURCE_LAST_MILE 22 | false 14 · true 26 | — | eventos do setor com data e organizador → **future · archive** (G0 → FATO_PRESENTE_SOBRE_O_FUTURO (data do evento ≠ janela)) |
| `italy-handoff-v21.js::fieldBulletins` | 133 | **c** | REFERENCE_DATE: 2018-04-11 → 2026-09-03 (129/133) · REFERENCE_DATE sem data em 4 | NÃO SEI | REAL_SOURCE 73 · REAL_SOURCE_LAST_MILE 60 | false 36 · true 97 | — | boletins fitossanitarios regionais → **windows · archive** (G0 → o mesmo caminho dos boletins T3 que a R7 ja leu (sonda, cruzamentos X2/X3)) |
| `italy-handoff-v21.js::futureEvents` | 14 | **c** | DATE: 2026-11-10 → 2027-04-11 (2/14) | NÃO SEI | REAL_SOURCE 2 · REAL_SOURCE_LAST_MILE 12 | false 7 · true 7 | events (14/14 pelo ID) | RECORTE de events (DOUBLE_COUNT_WARNING do proprio pacote) → **future · archive** (G0 → FATO_PRESENTE_SOBRE_O_FUTURO (data do evento ≠ janela)) |
| `italy-handoff-v21.js::futureSignals` | 3 | **d** | NÃO SEI | NÃO SEI | REAL_DERIVED 2 · REAL_FACT 1 | false 2 · true 1 | — | interpretacao SINTONIA feita fora da Intelligence (SINTONIA_INTERPRETATION) |
| `italy-handoff-v21.js::marketObservations` | 157 | **c** | REFERENCE_PERIOD: 2010-06-21 → 2026-08-17 (77/157) · PUBLICATION_DATE sem data em 40 | NÃO SEI | REAL_SOURCE 77 · REAL_SOURCE_LAST_MILE 80 | false 67 · true 90 | — | observacoes de preco com publicador e periodo → **market** (G0 → CROP_ID/MARKET_PLACE_ID/PERIOD/PRICE/UNIT) |
| `italy-handoff-v21.js::news` | 8 | **c** | DATE: 2021-02-24 → 2026-06-03 (6/8) · DATE sem data em 2 | NÃO SEI | REAL_SOURCE 8 | true 8 | — | noticias da imprensa tecnica → **archive** (G0 → publicacao nao vira fact time) |
| `italy-handoff-v21.js::opportunities` | 43 | **d** | REFERENCE_DATE: 2026-09-02 → 2026-09-02 | NÃO SEI | REAL_DERIVED 43 | false 43 | — | oportunidades do motor V2.1: CLIENT_SAFE=false em todas, nao provadas, nao sao da Intelligence do pote |
| `italy-handoff-v21.js::opportunityEvidence` | 43 | **d** | NÃO SEI | NÃO SEI | (sem campo) 43 | (sem campo) 43 | — | evidencia das 43 oportunidades V2.1 — vai com elas |
| `italy-handoff-v21.js::opportunityRules` | 3 | **d** | NÃO SEI | NÃO SEI | (sem campo) 3 | (sem campo) 3 | — | regras do motor V2.1 (arquetipos, estados) — configuracao, nao dado |
| `italy-handoff-v21.js::productActiveIngredients` | 203 | **b** | REFERENCE_DATE: 2026-09-02 → 2026-09-02 | NÃO SEI | EVIDENCE_DOCUMENTED 203 | true 203 | — | ponte produto × substancia ativa do registro |
| `italy-handoff-v21.js::productRelationships` | 5402 | **b** | REFERENCE_DATE: 2026-08-15 → 2040-10-31 | NÃO SEI | REAL_DERIVED 3517 · REAL_FACT 1885 | false 3517 · true 1885 | — | pares produto × cultura × alvo lidos nos rotulos — o portfolio que os cruzamentos pedem |
| `italy-handoff-v21.js::productsCommercial` | 51 | **b** | REFERENCE_DATE: 2026-09-02 → 2026-09-02 | NÃO SEI | REAL_SOURCE_LAST_MILE 51 | true 51 | — | catalogo comercial ADAMA Italia (51) |
| `italy-handoff-v21.js::productsRegulatory` | 163 | **b** | EXPIRY: 2026-08-15 → 2041-10-31 | NÃO SEI | REAL_FACT 163 | true 163 | — | registro ministerial dos 163 produtos ADAMA (Ministero della Salute) |
| `italy-handoff-v21.js::publicChannels` | 62 | **b** | EXAMPLE_PUBLISHED_AT: 2010-06-11 → 2026-06-23 | NÃO SEI | REAL_SOURCE 62 | true 62 | — | registro de canais publicos — procedencia das vozes, nao voz |
| `italy-handoff-v21.js::publicVoices` | 79 | **c** | REFERENCE_DATE: 2024-06-19 → 2026-09-02 (21/79) · DATE sem data em 58 · REFERENCE_DATE sem data em 58 | NÃO SEI | REAL_SOURCE 58 · REAL_SOURCE_LAST_MILE 21 | false 14 · true 65 | — | vozes publicas com pessoa, canal e data → **voices** (G0 → SPEAKER_ID/QUOTE_OR_TRANSCRIPT/FACT_TIME) |
| `italy-handoff-v21.js::regulatoryFuture` | 28 | **b** | REFERENCE_DATE: 2026-07-01 → 2026-09-02 (17/28) · REFERENCE_DATE sem data em 11 | NÃO SEI | REAL_SOURCE_LAST_MILE 28 | false 22 · true 6 | — | atos regulatorios futuros com fonte oficial; CLIENT_SAFE maioritariamente false: so como procedencia |
| `italy-handoff-v21.js::regulatoryFutureFacts` | 47 | **b** | REFERENCE_DATE: 2026-09-30 → 2039-10-31 | NÃO SEI | EVIDENCE_DOCUMENTED 47 | true 47 | — | datas de expiracao de aprovacao UE por substancia — referencia oficial (data regulatoria nao vira janela) |
| `italy-handoff-v21.js::relationships` | 19 | **d** | NÃO SEI | NÃO SEI | (sem campo) 19 | false 19 | — | ligacoes dos mesmos 19 cruzamentos V2.1, CLIENT_SAFE=false |
| `italy-handoff-v21.js::researchers` | 60 | **b** | LAST_ACTIVITY: 2019-01-02 → 2026-07-30 | NÃO SEI | REAL_SOURCE 60 | true 60 | — | diretorio de investigadores (ORCID/OpenAlex) — entidade de referencia, nao item |
| `italy-handoff-v21.js::resistance` | 34 | **b** | NÃO SEI · REFERENCE_DATE sem data em 12 | NÃO SEI | REAL_FACT 34 | true 34 | — | casos de resistencia com autoridade e citacao (GIRE/HRAC) |
| `italy-handoff-v21.js::scienceCorpus` | 763 | **c** | PUBLISHED_AT: 2019-01-01 → 2026-08-27 | NÃO SEI | REAL_SOURCE 763 | false 181 · true 582 | — | corpus cientifico colhido (OpenAlex); IDs distintos dos 88 scienceRecords → **science** (G0 → DOI/MOLECULE/CROP_ID/ISSUE_ID (ciencia nao vira incidencia de campo)) |
| `italy-handoff-v21.js::scienceRecords` | 88 | **c** | PUBLISHED_AT: 2019-01-01 → 2026-08-14 | NÃO SEI | REAL_SOURCE 88 | true 88 | — | registos de ciencia com DOI/autor/instituicao → **science** (G0 → DOI/MOLECULE/CROP_ID/ISSUE_ID (ciencia nao vira incidencia de campo)) |
| `italy-handoff-v21.js::sources` | 196 | **b** | NÃO SEI | NÃO SEI | REAL_SOURCE 31 · REAL_SOURCE_LAST_MILE 163 · SENTINELA 2 | false 165 · true 31 | — | registro de fontes — procedencia, nao dado |
| `italy-handoff-v21.js::transcripts` | 184 | **c** | PUBLICATION_DATE: 2016-03-31 → 2026-09-03 | OBSERVED_AT: 2026-08-29 → 2026-09-04 | REAL_SOURCE 184 | false 24 · true 160 | — | transcricoes de video (a prova das vozes) → **voices** (G0 → a transcricao e a prova de uma voz, nao uma voz) |
| `italy-v21.js::MANIFEST` | 26 | **d** | NÃO SEI | NÃO SEI | (sem campo) 26 | (sem campo) 26 | — | manifesto de uma build anterior do pacote — nao e dado |
| `italy-v21.js::collections.products.regulatory` | 163 | **b** | EXPIRY: 2026-08-15 → 2041-10-31 | NÃO SEI | REAL_FACT 163 | true 163 | productsRegulatory (163/163 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — registro ministerial dos 163 produtos ADAMA (Ministero della Salute) |
| `italy-v21.js::collections.products.commercial` | 51 | **b** | REFERENCE_DATE: 2026-09-02 → 2026-09-02 | NÃO SEI | REAL_SOURCE_LAST_MILE 51 | true 51 | productsCommercial (51/51 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — catalogo comercial ADAMA Italia (51) |
| `italy-v21.js::collections.products.relationships` | 2030 | **b** | REFERENCE_DATE: 2026-08-15 → 2040-10-31 | NÃO SEI | REAL_DERIVED 518 · REAL_FACT 1512 | false 518 · true 1512 | productRelationships (2030/2030 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — pares produto × cultura × alvo lidos nos rotulos — o portfolio que os cruzamentos pedem |
| `italy-v21.js::collections.activeIngredients` | 53 | **b** | REFERENCE_DATE: 2026-09-02 → 2026-09-02 | NÃO SEI | EVIDENCE_SOURCED 53 | true 53 | activeIngredients (53/53 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — substancias ativas com estado de aprovacao UE (EU pesticides database / CELEX) |
| `italy-v21.js::collections.products.activeIngredients` | 203 | **b** | REFERENCE_DATE: 2026-09-02 → 2026-09-02 | NÃO SEI | EVIDENCE_DOCUMENTED 203 | true 203 | productActiveIngredients (203/203 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — ponte produto × substancia ativa do registro |
| `italy-v21.js::collections.regulatoryFutureFacts` | 47 | **b** | REFERENCE_DATE: 2026-09-30 → 2039-10-31 | NÃO SEI | EVIDENCE_DOCUMENTED 47 | true 47 | regulatoryFutureFacts (47/47 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — datas de expiracao de aprovacao UE por substancia — referencia oficial (data regulatoria nao vira janela) |
| `italy-v21.js::collections.windows` | 7 | **d** | NÃO SEI | NÃO SEI | REAL_FACT 5 · REAL_SOURCE 2 | true 7 | — | build anterior: janelas montadas a mao (mesmas 7 do design pack) — interpretacao fora da Intelligence |
| `italy-v21.js::collections.fieldSignals` | 122 | **c** | REFERENCE_DATE: 2018-04-11 → 2026-09-02 (118/122) | NÃO SEI | REAL_SOURCE 73 · REAL_SOURCE_LAST_MILE 49 | false 36 · true 86 | fieldBulletins (122/122 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — boletins fitossanitarios regionais → **windows · archive** (G0 → o mesmo caminho dos boletins T3 que a R7 ja leu (sonda, cruzamentos X2/X3)) |
| `italy-v21.js::collections.cropEconomicWeight` | 2978 | **b** | REFERENCE_DATE: 2024-01-10 → 2026-12-31 (2976/2978) | NÃO SEI | REAL_DERIVED 981 · REAL_SOURCE_LAST_MILE 1997 | false 2965 · true 13 | cropEconomics (2978/2978 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — estatistica oficial (ISTAT/Eurostat) de peso economico da cultura |
| `italy-v21.js::collections.market` | 157 | **c** | PUBLICATION_DATE: 2022-07-21 → 2026-08-27 (40/157) | NÃO SEI | REAL_SOURCE 77 · REAL_SOURCE_LAST_MILE 80 | false 67 · true 90 | marketObservations (157/157 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — observacoes de preco com publicador e periodo → **market** (G0 → CROP_ID/MARKET_PLACE_ID/PERIOD/PRICE/UNIT) |
| `italy-v21.js::collections.competitors` | 577 | **c** | PUBLISHED_AT: 2011-04-29 → 2026-08-11 (147/577) | NÃO SEI | REAL_SOURCE 561 · REAL_SOURCE_LAST_MILE 16 | false 8 · true 569 | competitorActivities (577/577 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — anuncios/atividade de concorrentes (Meta Ad Library) → **competitors** (G0 → crossing concorrente × produto × cultura (T4_REGISTRATION_EVIDENCE_ID exigido)) |
| `italy-v21.js::collections.science` | 88 | **c** | PUBLISHED_AT: 2019-01-01 → 2026-08-14 | NÃO SEI | REAL_SOURCE 88 | true 88 | scienceRecords (88/88 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — registos de ciencia com DOI/autor/instituicao → **science** (G0 → DOI/MOLECULE/CROP_ID/ISSUE_ID (ciencia nao vira incidencia de campo)) |
| `italy-v21.js::collections.researchers` | 60 | **b** | LAST_ACTIVITY: 2019-01-02 → 2026-07-30 | NÃO SEI | REAL_SOURCE 60 | true 60 | researchers (60/60 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — diretorio de investigadores (ORCID/OpenAlex) — entidade de referencia, nao item |
| `italy-v21.js::collections.resistance` | 34 | **b** | NÃO SEI | NÃO SEI | REAL_FACT 34 | true 34 | resistance (34/34 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — casos de resistencia com autoridade e citacao (GIRE/HRAC) |
| `italy-v21.js::collections.voices` | 79 | **c** | REFERENCE_DATE: 2024-06-19 → 2026-09-02 (21/79) · DATE sem data em 58 · REFERENCE_DATE sem data em 58 | NÃO SEI | REAL_SOURCE 58 · REAL_SOURCE_LAST_MILE 21 | false 14 · true 65 | publicVoices (79/79 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — vozes publicas com pessoa, canal e data → **voices** (G0 → SPEAKER_ID/QUOTE_OR_TRANSCRIPT/FACT_TIME) |
| `italy-v21.js::collections.channels` | 62 | **b** | EXAMPLE_PUBLISHED_AT: 2010-06-11 → 2026-06-23 | NÃO SEI | REAL_SOURCE 62 | true 62 | publicChannels (62/62 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — registro de canais publicos — procedencia das vozes, nao voz |
| `italy-v21.js::collections.regulatoryFuture` | 28 | **b** | REFERENCE_DATE: 2026-07-01 → 2026-09-02 (17/28) | NÃO SEI | REAL_SOURCE_LAST_MILE 28 | false 22 · true 6 | regulatoryFuture (28/28 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — atos regulatorios futuros com fonte oficial; CLIENT_SAFE maioritariamente false: so como procedencia |
| `italy-v21.js::collections.agromet` | 44 | **c** | REFERENCE_DATE: 2025-02-20 → 2026-09-02 (39/44) | NÃO SEI | REAL_SOURCE_LAST_MILE 44 | false 30 · true 14 | agrometConditions (44/44 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — condicoes agrometeorologicas publicadas → **windows** (G0 → condicao agrometeorologica e contexto, nao janela) |
| `italy-v21.js::collections.events` | 40 | **c** | DATE: 2026-02-04 → 2027-04-11 (18/40) | NÃO SEI | REAL_SOURCE 18 · REAL_SOURCE_LAST_MILE 22 | false 14 · true 26 | events (40/40 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — eventos do setor com data e organizador → **future · archive** (G0 → FATO_PRESENTE_SOBRE_O_FUTURO (data do evento ≠ janela)) |
| `italy-v21.js::collections.futureEvents` | 14 | **c** | DATE: 2026-11-10 → 2027-04-11 (2/14) | NÃO SEI | REAL_SOURCE 2 · REAL_SOURCE_LAST_MILE 12 | false 7 · true 7 | futureEvents (14/14 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — RECORTE de events (DOUBLE_COUNT_WARNING do proprio pacote) → **future · archive** (G0 → FATO_PRESENTE_SOBRE_O_FUTURO (data do evento ≠ janela)) |
| `italy-v21.js::collections.opportunities` | 3 | **d** | NÃO SEI | NÃO SEI | REAL_DERIVED 3 | false 3 | opportunities (0/3 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — oportunidades do motor V2.1: CLIENT_SAFE=false em todas, nao provadas, nao sao da Intelligence do pote |
| `italy-v21.js::collections.futureSignals` | 3 | **d** | NÃO SEI | NÃO SEI | REAL_DERIVED 2 · REAL_FACT 1 | false 2 · true 1 | futureSignals (3/3 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — interpretacao SINTONIA feita fora da Intelligence (SINTONIA_INTERPRETATION) |
| `italy-v21.js::collections.sources` | 189 | **b** | NÃO SEI | NÃO SEI | REAL_SOURCE 31 · REAL_SOURCE_LAST_MILE 156 · SENTINELA 2 | false 158 · true 31 | sources (189/189 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — registro de fontes — procedencia, nao dado |
| `italy-v21.js::collections.news` | 8 | **c** | DATE: 2021-02-24 → 2026-06-03 (6/8) · DATE sem data em 1 | NÃO SEI | REAL_SOURCE 8 | true 8 | news (8/8 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — noticias da imprensa tecnica → **archive** (G0 → publicacao nao vira fact time) |
| `italy-v21.js::collections.relationships` | 19 | **d** | NÃO SEI | NÃO SEI | (sem campo) 19 | false 19 | relationships (19/19 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — ligacoes dos mesmos 19 cruzamentos V2.1, CLIENT_SAFE=false |
| `italy-v21.js::collections.crossings` | 19 | **d** | NÃO SEI | NÃO SEI | (sem campo) 19 | false 19 | clientSafeCrossings (19/19 pelo ID) | build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — cruzamentos V2.1: CLIENT_SAFE=false em todos (o nome do conjunto nao e o estado dos registos) |
| `italy-ingested.js::PRODUCTS` | 163 | **b** | expiry: 2026-08-15 → 2041-10-31 | NÃO SEI | REAL_FACT 163 | (sem campo) 163 | productsRegulatory (163/163 pelo reg = REGISTRATION_NUMBER) | registro ministerial (copia do design pack) |
| `italy-ingested.js::LINKS` | 219 | **b** | NÃO SEI | NÃO SEI | REAL_FACT 219 | (sem campo) 219 | — | pares produto × cultura × alvo com dose do rotulo (design pack) |
| `italy-ingested.js::CROPS` | 17 | **b** | NÃO SEI | NÃO SEI | REAL_DERIVED 17 | (sem campo) 17 | — | vocabulario de culturas com contagem de produtos no rotulo |
| `italy-ingested.js::COMP_ACTIVITIES` | 503 | **c** | start: 2019-12-05 → 2026-08-26 (414/503) | NÃO SEI | REAL_SOURCE 503 | (sem campo) 503 | competitorActivities (503/503 pelo ID) | anuncios Meta e videos organicos (copia do design pack) → **competitors** (G0 → crossing concorrente × produto × cultura (T4_REGISTRATION_EVIDENCE_ID exigido)) |
| `italy-ingested.js::COMP_COMPANIES` | 14 | **d** | NÃO SEI | NÃO SEI | REAL_DERIVED 14 | (sem campo) 14 | — | agregado por empresa derivado fora da Intelligence (contagens de anuncios) |
| `italy-ingested.js::COMP_PRODUCTS` | 36 | **d** | NÃO SEI | NÃO SEI | REAL_SOURCE 36 | (sem campo) 36 | — | agregado por produto concorrente derivado fora da Intelligence |
| `italy-ingested.js::SCIENCE` | 88 | **c** | PUBLISHED_AT: 2019-01-01 → 2026-08-14 | NÃO SEI | REAL_SOURCE 88 | (sem campo) 88 | scienceRecords (88/88 pelo ID) | ciencia (copia) → **science** (G0 → DOI/MOLECULE/CROP_ID/ISSUE_ID (ciencia nao vira incidencia de campo)) |
| `italy-ingested.js::RESEARCHERS` | 60 | **b** | LAST_ACTIVITY: 2019-01-02 → 2026-07-30 | NÃO SEI | REAL_SOURCE 60 | (sem campo) 60 | researchers (60/60 pelo ID) | diretorio (copia) |
| `italy-ingested.js::RESISTANCE` | 34 | **b** | NÃO SEI | NÃO SEI | REAL_FACT 34 | (sem campo) 34 | resistance (34/34 pelo ID) | resistencia (copia) |
| `italy-ingested.js::THEMES` | 5 | **d** | NÃO SEI | NÃO SEI | REAL_SOURCE 5 | (sem campo) 5 | — | agregados de tema derivados fora da Intelligence |
| `italy-ingested.js::VOICES` | 17 | **c** | NÃO SEI · DATE sem data em 17 | NÃO SEI | REAL_SOURCE 17 | (sem campo) 17 | publicVoices (17/17 pelo ID) | vozes (copia) → **voices** (G0 → SPEAKER_ID/QUOTE_OR_TRANSCRIPT/FACT_TIME) |
| `italy-ingested.js::CHANNELS` | 30 | **b** | EXAMPLE_PUBLISHED_AT: 2010-06-11 → 2026-04-09 | NÃO SEI | REAL_SOURCE 30 | (sem campo) 30 | publicChannels (30/30 pelo ID) | canais (copia) |
| `italy-ingested.js::SOURCES` | 31 | **b** | NÃO SEI | NÃO SEI | REAL_SOURCE 31 | (sem campo) 31 | sources (31/31 pelo SOURCE_ID = SOURCE_ID) | registro de fontes (copia parcial) |
| `italy-ingested.js::PEOPLE` | 15 | **b** | NÃO SEI | NÃO SEI | REAL_SOURCE 15 | (sem campo) 15 | — | pessoas com evidencia de identidade e papel — entidade de referencia |
| `italy-ingested.js::EVENTS` | 18 | **c** | DATE: 2026-02-04 → 2027-04-11 | NÃO SEI | REAL_SOURCE 18 | (sem campo) 18 | events (18/18 pelo ID) | eventos (copia) → **future · archive** (G0 → FATO_PRESENTE_SOBRE_O_FUTURO (data do evento ≠ janela)) |
| `italy-ingested.js::NEWS` | 8 | **c** | DATE: 2021-02-24 → 2026-06-03 (6/8) · DATE sem data em 1 | NÃO SEI | REAL_SOURCE 8 | (sem campo) 8 | news (8/8 pelo ID) | noticias (copia) → **archive** (G0 → publicacao nao vira fact time) |
| `italy-ingested.js::MARKET` | 77 | **c** | PUBLICATION_DATE: 2022-07-21 → 2026-08-27 (40/77) | NÃO SEI | REAL_SOURCE 77 | (sem campo) 77 | marketObservations (77/77 pelo ID) | precos (copia) → **market** (G0 → CROP_ID/MARKET_PLACE_ID/PERIOD/PRICE/UNIT) |
| `italy-ingested.js::MARKET_SUMMARIES` | 5 | **d** | NÃO SEI | NÃO SEI | (sem campo) 5 | (sem campo) 5 | — | sumarios de texto por cultura — interpretacao fora da Intelligence |
| `italy-ingested.js::CROP_WINDOWS` | 7 | **d** | NÃO SEI | NÃO SEI | REAL_FACT 5 · REAL_SOURCE 2 | (sem campo) 7 | — | janelas montadas a mao a partir de boletins e da norma — interpretacao fora da Intelligence |
| `italy-ingested.js::OPPORTUNITIES` | 3 | **d** | NÃO SEI | NÃO SEI | REAL_DERIVED 3 | (sem campo) 3 | — | tres fichas de oportunidade escritas a mao (LEGACY_CASE_ID IT-HERO) |
| `italy-ingested.js::FUTURE_SIGNALS` | 3 | **d** | NÃO SEI | NÃO SEI | REAL_DERIVED 2 · REAL_FACT 1 | (sem campo) 3 | — | interpretacao fora da Intelligence |
| `italy-catalog.js::ITEMS` | 44 | **b** | expiry: 2026-08-31 → 2041-10-31 (41/44) | NÃO SEI | (sem campo) 44 | (sem campo) 44 | — | catalogo comercial ADAMA Italia com o estado da ligacao ao registro |
| `italy-real-intelligence.js::RESEARCHERS` | 14 | **NAO_SEI** | NÃO SEI | NÃO SEI | REAL_FACT 14 | (sem campo) 14 | — | transcrito a mao do brief (LAST_CHECKED 2026-09-01): sem URL, sem COLLECTED_AT, sem observacao bruta — nao se sabe se e coleta nem de quando |
| `italy-real-intelligence.js::SCIENCE` | 12 | **NAO_SEI** | NÃO SEI | NÃO SEI | REAL_DERIVED 3 · REAL_FACT 9 | (sem campo) 12 | — | idem: transcrito do brief, sem URL nem data de coleta |
| `italy-real-intelligence.js::NEWS` | 9 | **NAO_SEI** | NÃO SEI | NÃO SEI | REAL_FACT 9 | (sem campo) 9 | — | idem: transcrito do brief; datas sem ano («01 Sep») |
| `italy-real-intelligence.js::BULLETINS` | 7 | **NAO_SEI** | NÃO SEI | NÃO SEI | REAL_FACT 7 | (sem campo) 7 | — | idem: contagens de boletins transcritas, sem o boletim |
| `italy-real-intelligence.js::COMPETITOR_REAL` | 19 | **NAO_SEI** | NÃO SEI | NÃO SEI | REAL_DERIVED 11 · REAL_FACT 4 · REAL_SOURCE 4 | (sem campo) 19 | — | idem: REAL_DERIVED do dataset Meta, sem ID do anuncio |
| `italy-real-intelligence.js::EVENTS_EXTRA` | 1 | **NAO_SEI** | NÃO SEI | NÃO SEI | (sem campo) 1 | (sem campo) 1 | — | idem |
| `italy-real-intelligence.js::SOURCES_EXTRA` | 19 | **NAO_SEI** | NÃO SEI | NÃO SEI | (sem campo) 19 | (sem campo) 19 | — | idem |
| `italy-real-intelligence.js::REALITY` | 12 | **d** | NÃO SEI | NÃO SEI | (sem campo) 12 | (sem campo) 12 | — | etiquetas de estado para a demo (REAL_DATA_AVAILABLE...) — nao e dado |
| `italy-demo-data.js::CAT` | 3 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 3 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::STATUS` | 11 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 11 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::DEPT` | 6 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 6 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::REGIONS` | 20 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 20 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::REGION_STATS` | 20 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 20 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::PRODUCTS` | 33 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 33 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::PRODUCT_LIST` | 33 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 33 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::CASES` | 29 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 29 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::SIGNALS` | 56 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 56 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::COMPANIES` | 6 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 6 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::CO_META` | 6 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 6 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::ACTIVITIES` | 53 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 53 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::EVENTS` | 5 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 5 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::CPRODUCTS` | 14 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 14 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::MATRIX` | 6 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 6 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::CROP_COLS` | 6 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 6 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::ISSUE_ROWS` | 12 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 12 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::WHAT_CHANGED` | 6 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 6 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::ATYPE_COLOR` | 6 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 6 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::SCI_THEMES` | 10 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 10 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::RECORDS` | 24 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 24 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::INSTITUTIONS` | 12 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 12 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::PEOPLE` | 25 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 25 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::TSR` | 7 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 7 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::FIELD_MESSAGES` | 18 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 18 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::FIELD_KPI` | 6 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 6 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::NOTIFICATIONS` | 6 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 6 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::WINDOWS` | 29 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 29 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::WINDOW_KPI` | 9 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 9 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::LADDER` | 5 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 5 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::F_COLOR` | 7 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 7 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::GROUP_COLOR` | 11 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 11 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::SOURCES` | 34 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 34 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::ARCHIVE` | 420 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 420 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::KPI` | 25 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 25 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::REAL_STATS` | 4 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 4 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::CROP_CAL` | 8 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 8 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::OBSERVED` | 10 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 10 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `italy-demo-data.js::CAL` | 16 entradas do bloco | **d** | — | — | SYNTHETIC_DEMO (ficheiro inteiro) 16 | — | — | pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco |
| `meeting-intelligence-snapshot.js::CASES` | 43 | **d** | REFERENCE_DATE: 2026-09-02 → 2026-09-02 | NÃO SEI | (sem campo) 43 | (sem campo) 43 | — | os 43 casos do motor V2.1 (07/09): oportunidades nao provadas, nao sao da Intelligence do pote |
| `italy-casa.js::AUTORIZACOES` | 8 chaves do bloco | **b** | DATA_DE_REFERENCIA: 2026-09-04 → 2026-09-04 | — | — | — | — | contagens do registro ministerial feitas por superficie/it_casa_dados.py — referencia; o casco so a mostra via pote |
| `italy-casa.js::COBERTURA` | 5 chaves do bloco | **d** | DATA_DE_REFERENCIA: 2026-09-04 → 2026-09-04 | — | — | — | — | medida de cobertura de uma leitura fora da Intelligence |
| `italy-casa.js::DESTAQUE` | 20 chaves do bloco | **d** | DATA_DE_REFERENCIA: 2026-09-04 → 2026-09-04 | — | — | — | — | destaque montado fora da Intelligence |
| `italy-casa.js::EVIDENCIA` | 3 chaves do bloco | **d** | DATA_DE_REFERENCIA: 2026-09-04 → 2026-09-04 | — | — | — | — | regra de apresentacao |
| `italy-casa.js::FONTES` | 5 chaves do bloco | **d** | DATA_DE_REFERENCIA: 2026-09-04 → 2026-09-04 | — | — | — | — | contagem de fontes da camada humana |
| `italy-casa.js::LABELS` | 324 chaves do bloco | **d** | DATA_DE_REFERENCIA: 2026-09-04 → 2026-09-04 | — | — | — | — | rotulos IT/EN — vocabulario, nao dado |
| `italy-casa.js::OPPORTUNITA_ATTUALI` | 17 chaves do bloco | **d** | DATA_DE_REFERENCIA: 2026-09-04 → 2026-09-04 | — | — | — | — | as 43 oportunidades V2.1 (CLIENT_SAFE=false) |
| `italy-casa.js::RADAR_FUTURO` | 10 chaves do bloco | **d** | DATA_DE_REFERENCIA: 2026-09-04 → 2026-09-04 | — | — | — | — | radar futuro montado sobre o V2.1, fora da Intelligence |
| `italy-casa.js::REVOGADO_X_SCADUTO` | 7 chaves do bloco | **b** | DATA_DE_REFERENCIA: 2026-09-04 → 2026-09-04 | — | — | — | — | estado administrativo do registro (revogado × scaduto) |
| `italy-casa.js::SENSORES` | 4 chaves do bloco | **d** | DATA_DE_REFERENCIA: 2026-09-04 → 2026-09-04 | — | — | — | — | sensores humanos julgados fora da Intelligence |
| `italy-casa.js::SINAIS_DE_CAMPO` | 4 chaves do bloco | **d** | DATA_DE_REFERENCIA: 2026-09-04 → 2026-09-04 | — | — | — | — | cartao de sinais de campo da camada humana |
| `italy-canonical-windows.js::windows` | 29 | **d** | START_DATE: 2026-03-15 → 2027-05-01 (24/29) | NÃO SEI | EXPECTED_NORM 24 · NOT_ESTABLISHED 5 | (sem campo) 29 | — | janelas EXPECTED_NORM montadas fora da Intelligence (nenhuma CONFIRMED, dito no proprio ficheiro) |
| `adama-relevance.js::VERDETTI` | 43 vereditos | **d** | — | — | — | — | — | veredito de relevancia sobre as 43 oportunidades V2.1 — fora com elas |
| `italy-label-verdicts.js::VERIFIED` | 12 | **NAO_SEI** | NÃO SEI | NÃO SEI | (sem campo) 12 | (sem campo) 12 | — | vereditos de uma leitura dos rotulos (02/09) sem selo nem ferramenta nomeada — nao se sabe se e saida de ferramenta |
| `italy-label-verdicts.js::NOT_FOUND` | 7 | **NAO_SEI** | NÃO SEI | NÃO SEI | (sem campo) 7 | (sem campo) 7 | — | idem |

## O caminho dos itens coletados (classe c)

Porta: admissao/admissao.py (a porta de admissao por par item × universo) → Sala → G0. O passo da Intelligence que os lê **não está neste repositório** (motor `a5db06c4`, ramo `int-intake-g0v4-v1`): até lá, nenhum destes itens vai ao casco.

