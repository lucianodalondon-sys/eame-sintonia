# MATRIZ DO BENCHMARK AGRO — os 20 eixos, sistema a sistema

```
MISSAO     C-INT-AGRO-BENCH-01
ESPECIE    EVIDENCIA DE BENCHMARK
MEDIDO_EM  2026-09-13
```

> Companheiro de [`AGRO-INTELLIGENCE-BENCHMARK-V1.md`](AGRO-INTELLIGENCE-BENCHMARK-V1.md).
> Cada linha tem etiqueta de prova:
> `S` = standard/regulador · `C` = ciência revista por pares ·
> `V` = vendor claim (prova o que o produto **declara**, nada mais) ·
> `I` = inferência nossa, explícita.

---

## 0 · AS FONTES, COM ENDEREÇO

| # | sistema / standard | família | endereço lido |
|---|---|---|---|
| 1 | EPPO Codes | G | `eppo.int/RESOURCES/eppo_databases/eppo_codes` |
| 2 | EPPO PP 1/248 (3) — usos de PPP | D·G | `eppo.int/ACTIVITIES/plant_protection_products/harmonized_classification_uses` · `pp1.eppo.int/standards/PP1-248-3` |
| 3 | EPPO Global Database / Reporting Service | C | `gd.eppo.int` · `gd.eppo.int/reporting/` |
| 4 | ISPM 8 (IPPC) — estado de praga numa área | C | `assets.ippc.int/.../ISPM8.pdf` · `ippc.int/en/publications/determination-pest-status-area/` |
| 5 | EFSA — inquéritos estatisticamente sólidos | C | `efsa.europa.eu/en/supporting/pub/en-9788` (resumo) · EN-1919 (2020) |
| 6 | EFSA — Horizon Scanning + PeMoScoring | C | `efsa.europa.eu/en/topics/horizon-scanning-plant-pests` |
| 7 | Horizon scanning, avaliação 2017-2024 | C | `we.copernicus.org/articles/25/189/2025/` |
| 8 | CABI Plantwise / PlantwisePlus / POMS | C | `cabi.org/plantwiseplus/poms-support/` · relatórios Plantwise |
| 9 | EU Pesticides Database | D | `food.ec.europa.eu/plants/pesticides/eu-pesticides-database_en` |
| 10 | Ministero della Salute — Banca dati fitosanitari | D | `fitosanitari.salute.gov.it/fitosanitariws_new/` |
| 11 | Homologa / Lexagri (FoodChain ID) | D | `homologa.com` · `lexagri.com` |
| 12 | MIAPPE v1.1 | B·G | `miappe.org` · Papoutsoglou et al., *New Phytologist* 2020 |
| 13 | BrAPI | B·G | `brapi.org` |
| 14 | Crop Ontology | B·G | `cropontology.org` · guidelines v2.0 (CGSpace) |
| 15 | Agmatix / Axiom / GUARDS | B | `agmatix.com/agronomic-modeling-technology/` |
| 16 | AGROVOC | G | `agrovoc.fao.org/browse/agrovoc/en/` |
| 17 | BBCH | G | literatura (Hack et al. 1992; JKI/BBA·BSA·IVA) |
| 18 | AgGateway ADAPT | G | `adaptframework.org` |
| 19 | Syngenta Cropwise Protector | A | `help.eu.cropwise.com` · `cropwise.com/protector` |
| 20 | BASF xarvio FIELD MANAGER | A | `ag.xarvio.com/field-manager/crop-protection` |
| 21 | Climate FieldView · John Deere Ops Center · CropX · OneSoil | A | páginas de produto e de integração |
| 22 | JRC MARS Bulletin | E | `joint-research-centre.ec.europa.eu/monitoring-agricultural-resources-mars/jrc-mars-bulletin_en` |
| 23 | EU Market Observatories | E | `agriculture.ec.europa.eu/data-and-analysis/markets/overviews/market-observatories_en` |
| 24 | FAO AMIS | E | `amis-outlook.org` |
| 25 | DTN Farm Intelligence / Ag Hub | F | `dtn.com/agriculture/farm-intelligence/` |
| 26 | Alerta de saúde vegetal — para além da exactidão | C | *Front. Plant Sci.* 2026, 10.3389/fpls.2026.1899310 |
| 27 | EU Code of Conduct — partilha de dados agrícolas | — | COPA-COGECA e co-signatários |

---

## 1 · OBJECT MODEL · IDENTITY MODEL · ONTOLOGIA

| sistema | unidade central | identidade | vocabulário controlado | prova |
|---|---|---|---|---|
| EPPO Codes | táxon / entidade não-taxonómica | **código EPPO** (6 letras praga, 5 planta) — *«quando… um nome científico muda, o código EPPO permanece o mesmo»* | o próprio; 98 500+ espécies, 625 entidades não-taxonómicas | `S` |
| EPPO PP1/248 | **o USO de PPP** | tupla de 6 elementos, cada um com código; não-taxonómicos começam por `3` e terminam em letra de classe (`C`·`O`·`T`·`D`·`L`·`M`) | EPPO | `S` |
| ISPM 8 | **pest record** → estado de praga numa **área** | área + praga + registo | categorias de presença/ausência | `S` |
| Crop Ontology | **variável** = trait × method × scale | `CO_xxx` por ontologia de cultura | trait dictionary por espécie, curador nomeado | `S` |
| MIAPPE | **observation unit** + **observed variable** | Variable ID no ficheiro de definição de traits | remete para Crop Ontology | `S` |
| BrAPI | study · trial · observationUnit · observationVariable · germplasm · location | dbIds por servidor | *«compatible with MCPD, MIAPPE, GA4GH, GeoJSON, Crop Ontology»* | `S` |
| AGROVOC | **conceito SKOS** | URI persistente | 45+ línguas, `skosxl:prefLabel`, broader/narrower | `S` |
| Agmatix GUARDS | parâmetro agronómico num **grafo de conhecimento** | proprietária | ontologia própria + conversor de unidades | `V` |
| EU Pesticides DB | substância activa · MRL · autorização de emergência | número de substância / produto | — | `S` |
| Banca dati IT | **produto autorizado** | **numero di registrazione** + data do decreto | categoria (insetticida, fungicida…) + stato amministrativo | `S` |
| Homologa | produto × país × GAP | proprietária, harmonizada | 350 000 produtos, 90+ países | `V` |
| Cropwise Protector | **observação de scouting** georreferenciada | proprietária | fenómeno + característica | `V` |
| xarvio | **campo** + estádio + risco | proprietária | — | `V` |
| JD Ops / FieldView / ADAPT | **field boundary** + operação | proprietária; ADAPT existe para as traduzir | ADAPT data model | `S`(ADAPT) `V`(resto) |
| JRC MARS | célula de grelha → região | NUTS | — | `S` |
| AMIS | commodity × país × campanha | país + commodity | 4 culturas (trigo, milho, arroz, soja) | `S` |
| DTN | **grower** + campo + operador | proprietária (95 %+ dos agricultores EUA) | — | `V` |

> **O que isto obriga a concluir.** Não há **uma** identidade agrícola. Há
> **cinco famílias** de identidade — organismo, medição, uso regulado, lugar,
> actor — e elas resolvem-se em vocabulários diferentes. `I`

---

## 2 · TIME MODEL · PHENOLOGY

| sistema | tempos que distingue | fenologia |
|---|---|---|
| EPPO Reporting Service | data do artigo ≠ data do registo de praga | — |
| ISPM 8 | o registo tem data; o **estado** é uma conclusão datada e **revisível** (*records invalid*, *no longer present*) | — |
| EFSA surveys | período do inquérito; a conclusão vale **para aquele desenho e aquele período** | risco por fase do hospedeiro |
| MIAPPE | study start/end date, **season**, eventos datados | via observed variable |
| Crop Ontology | — | trait de fase |
| BBCH | — | **código decimal 00–99, 10 estágios principais**, mono e dicotiledóneas |
| Cropwise Protector | data da observação | **estádio fenológico** é campo de scouting `V` |
| xarvio | *«tempo agora, previsões e histórico, à hora»* | **estádio de crescimento** é input e eixo do alerta `V` |
| JRC MARS | mensal; horizonte da campanha | modelo de crescimento por cultura |
| AMIS | 10 edições/ano; campanha comercial | — |

```
NENHUM SISTEMA MADURO DE AGRO DECIDE POR DATA DE CALENDARIO SOZINHA.
OS QUE DECIDEM SOBRE O CAMPO DECIDEM POR FASE.
```

---

## 3 · GEOGRAPHY MODEL

| sistema | granularidade | regra |
|---|---|---|
| ISPM 8 | **área** (país, parte de país, várias) | o estado é *da área*, e a área é declarada |
| EFSA surveys | população-alvo → unidade epidemiológica → unidade de inspecção | a amostra pertence a uma população declarada |
| EPPO GD | país / sub-região, com mapas | distribuição é conjunto de registos, não um facto atómico |
| JRC MARS | grelha meteorológica → **NUTS** → nacional | agregação declarada |
| EU Market Observatories | Estado-Membro | — |
| Cropwise / xarvio / JD Ops / FieldView | **talhão** (field boundary) | o limite do campo é o objecto |
| DTN | campo → operador → território comercial | a ligação campo↔operador é o activo |

```
QUATRO ESCADAS, E NENHUMA E TRADUCAO DA OUTRA:
ADMINISTRATIVA · EPIDEMIOLOGICA · DE GRELHA · DE TALHAO.
```

---

## 4 · OBSERVATION · UNIT · SCALE · METHOD · DENOMINATOR

| sistema | o que exige de uma observação |
|---|---|
| **Crop Ontology** | trait **+** method **+** scale. Uma variável nova quando qualquer um muda. `S` |
| **MIAPPE** | observation unit, observed variable, biological material, experimental factor, environment, sample, data file; *«descreve **como** a medição foi feita»* `S` |
| **EFSA** | **população-alvo** (estrutura e dimensão, com factores de risco) · **unidade de inspecção** · **design prevalence** · **sensibilidade do método** = eficácia da amostragem × sensibilidade de diagnóstico · nível de confiança `S` |
| **ISPM 8** | o registo identifica praga, hospedeiro, lugar, data e **fonte**; a fiabilidade do registo é avaliável e o registo pode ser declarado **inválido** `S` |
| **Plantwise / POMS** | quem (plant doctor), onde (clínica), cultura, problema, diagnóstico, recomendação; validação e harmonização feitas por **equipas de peritos** — e a própria CABI regista que *«os dados da clínica são muitas vezes incompletos»* `C` |
| **Cropwise Protector** | **o que** se observa (fenómeno) × **como** se observa (contagem por planta, % de infestação, nível de pressão) + georreferência + estádio + armadilhas + fotos `V` |
| **xarvio** | observação do utilizador entra como **input do modelo** `V` |

> **A convergência mais forte de todo o benchmark.** Três famílias
> independentes exigem a mesma tripla. Ver `C1` no documento principal.

---

## 5 · PROVENANCE · VERSIONS

| sistema | fonte | versão do dado | versão do modelo/regra |
|---|---|---|---|
| EPPO GD | licença aberta | código estável, nome muda | — |
| ISPM 8 | o registo cita a sua fonte | estado revisível | — |
| EFSA HS | artigo + fonte MedISys | newsletter datada | PeMoScoring tem **15 critérios versionados** |
| EU Pesticides DB | *«no legal value»*; o oficial é o **Jornal Oficial** | — | — |
| Banca dati IT | decreto + etiqueta autorizada | **actualizada diariamente**; estado administrativo | — |
| Homologa | fontes públicas **e privadas** + parceiros locais | datas de registo e de caducidade | — |
| MIAPPE/BrAPI | investigação, estudo, ficheiros | versão do trait dictionary | desenho experimental declarado |
| Agmatix | ontologia própria | motor de integridade/anomalia | conversor de unidades `V` |
| JRC MARS | JRC | boletim mensal, volume/número | modelo + **juízo do analista** |

```
QUEM E AUTORIDADE GUARDA O ATO.
QUEM E CONVENIENCIA DIZ QUE E CONVENIENCIA — E A EU PESTICIDES DATABASE DIZ.
```

---

## 6 · EVIDENCE RELATIONS · DEPENDENCY / INDEPENDENCE

| sistema | como trata dependência entre evidências |
|---|---|
| EFSA HS | o mesmo pest reaparecer em artigos **subsequentes** é o sinal de persistência — 392 → 27 `C` |
| ISPM 8 | vários registos podem sustentar **um** estado; registos podem ser inválidos `S` |
| MIAPPE | o **mesmo ensaio** é uma investigação com estudos; réplicas são do desenho, não fontes novas `S` |
| BrAPI | trial → studies → observationUnits: a hierarquia **é** o grafo de dependência `S` |
| Crop Ontology | mesma trait, métodos diferentes = **variáveis diferentes** `S` |
| EPPO GD | distribuição = conjunto de registos com origem citada `S` |

> **Transferível.** `DEPENDENCY GRAPH BEFORE CONVERGENCE` (hipótese SINTONIA)
> sobrevive, e o agro dá-lhe chaves concretas: *mesmo trial* (MIAPPE
> investigation/study), *mesmo grupo* (afiliação), *mesmo dataset* (BrAPI
> trialDbId), *revisão que cita o primário* (DOI do primário). `I`

---

## 7 · UNCERTAINTY · COVERAGE · FRESHNESS

| sistema | incerteza | cobertura | frescura |
|---|---|---|---|
| EFSA surveys | **explícita e quantitativa**: nível de confiança para uma design prevalence `S` |
| EFSA PeMo | phi de −1 a +1; perito escolhe *«o resultado intermédio mais plausível, para evitar pressupostos extremos»* `C` |
| ISPM 8 | qualificadores (*at low prevalence*, *transient*) são incerteza nomeada `S` |
| JRC MARS | previsão com juízo de analista; mensal `S` |
| AMIS | países AMIS = **80–90 %** de produção/consumo/comércio das 4 culturas — a cobertura é declarada `S` |
| Banca dati IT | ~17 400 produtos, **diária** `S` |
| Homologa | 33 M de entradas, 350 k produtos, 90+ países `V` |
| xarvio / Cropwise | não publicam calibração `V` — e é exactamente o que a literatura critica `C` |

---

## 8 · HUMAN REVIEW · EXPERT VALIDATION

| sistema | onde a pessoa é obrigatória |
|---|---|
| EFSA HS | **selecção manual** dos artigos; peritos aplicam o PeMo `C` |
| EFSA surveys | desenho do inquérito e escolha da design prevalence são decisão de gestão de risco `S` |
| ISPM 8 | determinar o estado é juízo da ONPF, não uma soma de registos `S` |
| Plantwise | harmonização e validação por **equipas de peritos** `C` |
| Crop Ontology | **curador nomeado pela comunidade** por cultura `S` |
| JRC MARS | analista assina a previsão `S` |
| *Front. Plant Sci.* 2026 | supervisão **em escalões**: baixo risco automático · médio desencadeia recolha · alta consequência escala a perito `C` |

```
NENHUM SISTEMA MADURO DE SAUDE VEGETAL PROMOVE A ACAO SEM GENTE.
E NENHUM TRATA A AUTONOMIA COMO BINARIA.
```

---

## 9 · SIGNAL → HYPOTHESIS → RISK → FINDING → RECOMMENDATION → ACTION

| sistema | a cadeia real |
|---|---|
| **EFSA HS** | monitorizar (3 221 fontes) → seleccionar (perito) → PeMoScoring (15 critérios) → newsletter → pest categorisation → avaliação de risco → PAFF → **gestor decide** `C` |
| **ISPM 8** | registo → avaliação de fiabilidade → **estado da praga** (revisível) `S` |
| **EFSA surveys** | desenho → inquérito → conclusão *com confiança declarada* `S` |
| **xarvio** | meteorologia + estádio + histórico → índice de risco → **spray timer** → documentação da aplicação `V` |
| **Cropwise** | scouting → mapa → tarefa ao técnico `V` |
| **JRC MARS** | modelo + EO → analista → boletim → política `S` |

---

## 10 · OUTCOME / FEEDBACK LOOP

| sistema | o que fecha o ciclo |
|---|---|
| xarvio | **documentação da aplicação** — o que foi pulverizado, quando `V` |
| Cropwise | aplicação registada + indicadores de qualidade/produtividade `V` |
| JD Ops / FieldView | **as-applied** e **yield** sincronizados da máquina `V` |
| Plantwise | prescrição escrita; análise posterior das recomendações `C` |
| *Front. Plant Sci.* 2026 | **conclusão da resposta**, supressão da doença, valor económico, **aprendizagem após a acção** `C` |
| EFSA HS | o sinal voltar a aparecer (392 → 27) `C` |

> **Transferível ao SINTONIA sem fabricar causalidade:** `FOLLOWED` (alguém
> abriu/leu) e `ACTIONED` (alguém declarou ter agido) são mediáveis. `OUTCOME
> OBSERVED` exige dado de campo. `OUTCOME ATTRIBUTABLE` exige desenho
> experimental — e isso é um ensaio, não um dashboard. `I`

---

## 11 · SECURITY · ACCESS · DATA SOVEREIGNTY

| fonte | o que estabelece |
|---|---|
| **EU Code of Conduct** (2018, COPA-COGECA + CEMA + ECPA + …) | voluntário e não vinculativo; *«o agricultor permanece no centro da recolha, tratamento e gestão dos dados agrícolas»*; reconhece ao originador do dado o **direito a beneficiar ou ser compensado** pelo seu uso `S` |
| DTN | o activo é dado proprietário de 95 %+ dos agricultores `V` |
| ADAPT | existe porque **84 %** dos inquiridos acham difícil juntar dados de operações de várias origens `S` |

```
AUTHENTICATION != AUTHORIZATION
READ != DERIVE != WRITE != ACT
E NO AGRO HA UM QUARTO EIXO: DE QUEM E O DADO.
```

---

## 12 · WHAT DATA IS REQUIRED · WHAT MUST NOT BE TRANSFERRED

Sintetizado por capacidade em
[`AGRO-INTELLIGENCE-INPUT-REQUIREMENTS-V1.md`](AGRO-INTELLIGENCE-INPUT-REQUIREMENTS-V1.md).
A lista do que **não** trazer está na §7 do documento principal.
