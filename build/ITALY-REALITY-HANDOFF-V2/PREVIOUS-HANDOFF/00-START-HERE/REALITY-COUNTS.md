# CONTAGENS DE REALIDADE — contadas, não estimadas

**Geradas em:** 2026-09-02, lendo os arquivos deste pacote.

| medida | valor |
|---|---:|
| `REAL_ADAMA_PRODUCTS` | **163** |
| `REAL_HERBICIDES` | **91** |
| `REAL_FUNGICIDES` | **46** |
| `REAL_INSECTICIDES` | **23** |
| `REAL_OTHER_PRODUCT_LINES` | **3** |
| `REAL_CROP_TARGET_PRODUCT_LINKS` | **219** |
| `REAL_CROP_TERMS_IN_PORTFOLIO` | **17** |
| `REAL_CROP_WINDOWS` | **7** |
| `REAL_CURRENT_PHENOLOGY_SIGNALS` | **73** |
| `REAL_REGIONS_WITH_CURRENT_BULLETIN` | **6** |
| `REAL_MARKET_SOURCES_MAPPED` | **7** |
| `REAL_MARKET_CAPABILITIES_MAPPED` | **111** |
| `REAL_MARKET_RECORDS` | **195** |
| `REAL_NEWS` | **8** |
| `REAL_META_ADS_REACHING_ITALY` | **414** |
| `REAL_ORGANIC_COMPETITOR_RECORDS` | **147** |
| `REAL_COMPETITOR_COMPANIES` | **14** |
| `REAL_COMPETITOR_PRODUCTS` | **36** |
| `REAL_ITALIAN_CHANNELS` | **62** |
| `REAL_FIELD_VOICES` | **58** |
| `REAL_RESEARCHERS` | **60** |
| `REAL_SCIENTIFIC_RECORDS` | **88** |
| `REAL_RESEARCH_THEMES` | **5** |
| `REAL_HERBICIDE_RESISTANCES` | **34** |
| `REAL_PEOPLE_WITH_ROLE_EVIDENCE` | **15** |
| `REAL_EVENTS` | **18** |
| `REAL_SOURCES` | **31** |
| `REAL_OPPORTUNITY_CANDIDATES` | **3** |
| `REAL_FUTURE_SIGNALS` | **3** |
| `ARCHIVE_POINTERS` | **12** |
| `SYNTHETIC_DEMO_OBJECTS` | **0** |
| `INTERNAL_DATA_REQUIRED_OBJECTS` | **0** |
| `TOTAL_OBJECTS_WITH_ID` | **3773** |

---

## Proveniência de todos os objetos

| classe | objetos |
|---|---:|
| `REAL_FACT` | 1955 |
| `REAL_SOURCE` | 1225 |
| `REAL_DERIVED` | 593 |

⚠️ **`SYNTHETIC_DEMO` = 0.** Este pacote não contém objeto inventado. O que precisa ser sintético (notificação, fluxo, mensagem de Field Sales) é trabalho do Design e vai nascer marcado como tal.

---

## Onde cada número mora

| arquivo | array | objetos |
|---|---|---:|
| `01-DESIGN-READY/ADAMA/adama-crop-problem-product.json` | `LINKS` | 219 |
| `01-DESIGN-READY/ADAMA/adama-italy-crops.json` | `CROPS` | 17 |
| `01-DESIGN-READY/ADAMA/adama-italy-products.json` | `PRODUCTS` | 163 |
| `01-DESIGN-READY/ARCHIVE/archive-index.json` | `DATASETS` | 12 |
| `01-DESIGN-READY/COMPETITOR-WATCH/competitor-activities.json` | `ACTIVITIES` | 561 |
| `01-DESIGN-READY/COMPETITOR-WATCH/competitor-companies.json` | `COMPANIES` | 14 |
| `01-DESIGN-READY/COMPETITOR-WATCH/competitor-products.json` | `PRODUCTS` | 36 |
| `01-DESIGN-READY/CONVERGENCE/convergence.json` | `CONVERGENCE` | 38 |
| `01-DESIGN-READY/CROP-WINDOWS/crop-windows.json` | `WINDOWS` | 7 |
| `01-DESIGN-READY/CROP-WINDOWS/current-phenology.json` | `PHENOLOGY` | 73 |
| `01-DESIGN-READY/CROP-WINDOWS/regional-bulletin-sources.json` | `SOURCES` | 6 |
| `01-DESIGN-READY/EVENTS/events.json` | `EVENTS` | 18 |
| `01-DESIGN-READY/FUTURE-RADAR/future-signals.json` | `SIGNALS` | 3 |
| `01-DESIGN-READY/LABEL-USE/label-term-census.json` | `TERMS` | 17 |
| `01-DESIGN-READY/LABEL-USE/label-use-pairs.json` | `PAIRS` | 2030 |
| `01-DESIGN-READY/MARKET-PULSE/market-capabilities.json` | `CAPABILITIES` | 111 |
| `01-DESIGN-READY/MARKET-PULSE/market-pulse.json` | `PRICES` | 77 |
| `01-DESIGN-READY/MARKET-PULSE/market-sources.json` | `SOURCES` | 7 |
| `01-DESIGN-READY/NEWS/news.json` | `NEWS` | 8 |
| `01-DESIGN-READY/OPPORTUNITIES/opportunities.json` | `OPPORTUNITIES` | 3 |
| `01-DESIGN-READY/PEOPLE/people.json` | `PEOPLE` | 15 |
| `01-DESIGN-READY/SCIENCE/herbicide-resistance.json` | `RESISTANCES` | 34 |
| `01-DESIGN-READY/SCIENCE/research-themes.json` | `THEMES` | 5 |
| `01-DESIGN-READY/SCIENCE/researchers.json` | `RESEARCHERS` | 60 |
| `01-DESIGN-READY/SCIENCE/scientific-records.json` | `RECORDS` | 88 |
| `01-DESIGN-READY/SOURCES/sources.json` | `SOURCES` | 31 |
| `01-DESIGN-READY/VOCI-DAL-CAMPO/field-voices.json` | `VOICES` | 58 |
| `01-DESIGN-READY/VOCI-DAL-CAMPO/italian-channels.json` | `CHANNELS` | 62 |

---

## Dois números que precisam do denominador ao lado

**Vozes de campo italianas: 58** — de **2962** comentários italianos lidos, dentro de **3688** comentários no total. A raridade É o achado: quem apresentar as 58 sem o denominador está mentindo por omissão.

**Ligações cultura × alvo × produto: 219** — mas elas saem de **19 dos 163 produtos (11,7%)**. Os outros 144 não têm linha de uso lida. Isso é cobertura de LEITURA, não ausência de registro.

**Vozes de campo: 58 — mas elas NÃO se somam.** A varredura de 02/09 mediu a plateia do canal de cada fala. Ver `BY_CHANNEL_AUDIENCE` em `VOCI-DAL-CAMPO/field-voices.json`: uma parte vem de canal de HORTA DOMESTICA e fala de roseira e limoeiro. Relato em primeira pessoa sobre um vaso não é voz de lavoura.

**Sinais de fenologia corrente: 73, de 6 regiões.** Esta lacuna estava declarada como a MAIOR do pacote, com valor 0, e foi fechada na varredura noturna de 02/09/2026. O que não mudou: são 6 regiões de 20, e nenhuma fala pelo país.
