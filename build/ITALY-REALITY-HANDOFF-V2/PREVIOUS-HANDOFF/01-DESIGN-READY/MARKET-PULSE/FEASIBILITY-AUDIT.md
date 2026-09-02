# AUDITORIA DE VIABILIDADE — MARKET PULSE ITÁLIA
**Data da auditoria: 02/09/2026** · Critério de `DISPONIVEL`: *"a tela pode mostrar isso hoje, com número lido, data e unidade?"*

**Legenda (leia antes da tabela):**
- **YES** = existe número lido, com período, unidade e geografia, por rota que respondeu **hoje**.
- **PARTIAL** = existe número, mas está **congelado**, ou é de outra granularidade, ou depende de rota bloqueada / de conta nossa declarada.
- **NO** = **nenhuma rota provada nesta auditoria**. Isto NÃO é prova de que a fonte não existe (LEI 3: *fonte não alcançada ≠ fonte vazia*).
- **NOT_MEASURED** = nenhuma fonte pública mede isso; exigiria dado interno.

| METRICA | DISPONIVEL | FONTE | CADENCIA | GEOGRAFIA | ULTIMO PERIODO | LIMITACAO |
|---|---|---|---|---|---|---|
| FARM_GATE_PRICE | YES | EU Agri-food Data Portal (DG AGRI), `api/cereal/prices`, estágio `Price at farm gate` | semanal | PRAÇA (cidade) dentro da Itália | semana 24/08/2026–30/08/2026 (rota respondeu ao vivo hoje, HTTP 200, 16.221 registros IT/2026) | só **11** pares produto×praça trazem o estágio "Price at farm gate"; a fonte avisa: *"nao e serie continua: praca que nao cotou na semana nao aparece"*; preço vem como **texto** — *"PRICE_IS_TEXT_IN_SOURCE: sim — \"€237,00\""* — somar sem converter inventa zero |
| WHOLESALE_PRICE | PARTIAL | DG AGRI (estágios `Deliver to first customer - silo or processing plant` e `Departure from farm or from production area`); ISMEA `BD prezzi ingrosso` | semanal | PRAÇA | DG AGRI 24/08–30/08/2026; ISMEA **NÃO SEI** | estágio de silo/primeiro comprador **não é** o preço de atacado (*ingrosso*) do mercado hortifruti; o banco de atacado da ISMEA aparece no menu mas **nenhum preço foi lido** (host bloqueado por GEO_IP_BLOCK); a fonte DG AGRI avisa *"nao e o mesmo estagio comercial entre pracas — ver STAGE"* |
| PRICE_MOMENTUM | PARTIAL (derivado) | DG AGRI cereal/oliveOil prices — campos do próprio registro: preço da semana, semana anterior, mesma semana do ano anterior | semanal | PRAÇA e média nacional | cereais 24/08–30/08/2026; azeite 27/07–02/08/2026 | a **variação é conta nossa**, não número publicado pela fonte; praça que não cotou repete o valor e faz a variação parecer 0; `weekNumber` é semana de **campanha**, não do calendário (a semana de 24–30/08/2026 vem como `weekNumber: 9`) |
| REGIONAL_PRICE | YES | DG AGRI cereal prices — 17 praças nomeadas (Foggia, Grosseto, Bologna, Milano, Napoli, Roma, Verona, Treviso, Mantova, Catania…) | semanal | PRAÇA | 24/08–30/08/2026 | praça **não é** região NUTS2 nem província administrativa; o estágio comercial muda de praça para praça; há praça **morta** dentro da mesma resposta viva: `DUR|UNKNOWN` em Catania parou em **17/07/2022** |
| PRODUCTION | YES | DG AGRI `api/cereal/production` (IT, 2020–2026); ISMEA para tomate/vinho/azeite | anual | PAÍS | **2026** (cereais) | a API **não declara unidade**: *"UNITS_DECLARED_BY_SOURCE: NAO - a API nao declara unidade em nenhum campo"* — mil t / mil ha foram **inferidos** por aritmética interna e por triangulação com a ISMEA; só cereais; e *"producao NAO e oferta disponivel no mercado - falta estoque, importacao e exportacao"* |
| YIELD | YES | DG AGRI cereal/production (campo `yield`); Eurostat `apro_cpsh1` | anual | PAÍS | 2026 (DG AGRI); 2025 (Eurostat, atualizado 17/08/2026) | **não existe rendimento sub-nacional**: *"Rendimento (YLD) NAO existe em NUTS2 — so pais"*; a série italiana de trigo comum **não tem 2016**; *"rendimento medio nacional NAO e rendimento de lavoura nenhuma em particular"* |
| YIELD_FORECAST | PARTIAL | DG AGRI cereal/production traz linha de 2026 | anual | PAÍS | 2026 | a fonte **não diz** se 2026 é estimativa ou definitivo: *"NAO SEI. A API nao traz campo de status"*; chamar de previsão é afirmar o que a fonte não afirma; o boletim de previsão de safra (JRC MARS) **não foi coletado nem testado** |
| IMPORT | PARTIAL | ISMEA — comunicado AgriMercati 1/2026 e banco *Commercio estero* | trimestral (banco: mensal) | PAÍS | jan–nov/2025 | fonte **não alcançada ao vivo**; número congelado há ~7 meses; **LEI 5** — importação subindo não é demanda subindo (pode ser quebra de safra, arbitragem, reexportação ou estoque de indústria); o agregado exclui *"i dati soggetti a segreto statistico"* |
| EXPORT | PARTIAL | ISMEA AgriMercati / Tendenze | trimestral | PAÍS | primeiros 11 meses de 2025 | mesma defasagem; o relatório **mistura recortes** no mesmo texto (*"primi undici mesi del 2025"*, *"primi nove mesi"*, *"terzo trimestre 2025"*) — LEI 2 proíbe achatar isso num carimbo único |
| STOCK | PARTIAL | ISMEA (*giacenze* de vinho) | campanha/anual | PAÍS | julho de 2025 | só **vinho**; rota programática de estoque testada **hoje** e não publicada: `oliveOil/productionAndStock` → HTTP 404 *"No matching resource found for given API Request"* = **rota não publicada**, não ausência de dado |
| SUPPLY_BALANCE | PARTIAL | ISMEA *Bilanci di approvvigionamento* | anual | PAÍS | *"ultimo aggiornamento: gennaio 2026"* | estrutura, escopo e 13 setores conhecidos; **nenhum valor lido** — o Excel (204,14 KB) está atrás do host bloqueado |
| SELF_SUFFICIENCY | PARTIAL | ISMEA (mesma página do balanço) | anual | PAÍS | jan/2026 | a fórmula é pública (*"Autoapprovvigionamento = produzione / consumo"*), mas **nenhum valor foi lido**, e não dá para calcular só com produção — falta o consumo; mede oferta×consumo, **nunca** área tratada nem demanda de defensivo |
| FARMER_CONFIDENCE | PARTIAL | ISMEA ICF Agricoltura; único valor obtido veio de **imprensa** (Floraviva) citando a ISMEA | trimestral | PAÍS | I trimestre de 2025 (matéria de 01/07/2025); último relatório datado: IV trim/2025, publicado 29/01/2026 | **não é leitura da fonte**, é indício de terceiro; escala **-100 a +100, não é %** (a imprensa já publicou "-1,4%" com sinal indevido); **LEI 4** — ICF de "Cereali" **não é** confiança de trigo duro; os valores correntes moram em 6 XML de gráfico que dão 404 |
| INPUT_COST | YES | Eurostat `apri_pi_inq` (Price indices of the means of agricultural production, input) | **trimestral** | PAÍS | **2026-Q1**, dado atualizado em 11/08/2026; rota reconfirmada hoje (HTTP 200) | *"indice NAO e preco - e numero indice com base 2020=100"*; *"indice de insumo NAO e custo da lavoura de nenhum produtor"*; *"indice nacional NAO desce a regiao nem a praca"*; *"TRIMESTRAL - nao transformar em mensal nem semanal"* |
| FERTILIZER_COST | YES | Eurostat `apri_pi_inq`, item `AM203000 Fertilisers and soil improvers` | trimestral | PAÍS | 2026-Q1 | mesmas 3 ressalvas do INPUT_COST; o agregado esconde movimentos opostos dos sub-itens (N, P, K, compostos, NPK) |
| ENERGY_COST | YES | Eurostat `apri_pi_inq`, item `AM202000 Energy; lubricants` | trimestral | PAÍS | 2026-Q1 | idem; junta eletricidade, combustível de aquecimento, combustível de motor e lubrificantes numa cesta só |
| EU_MARKET_OUTLOOK | NO | — | — | — | — | **NÃO SEI**: o *Short-term outlook* da DG AGRI e os dashboards de mercado **não foram coletados nem testados** nesta auditoria. NO aqui = "não provei", jamais "não existe" (LEI 3) |
| ITALY_SECTOR_OUTLOOK | PARTIAL | ISMEA *Tendenze* + *AgriMercati* | irregular ("campanha") | PAÍS | *Tendenze Ortaggi* 1/2026 (março/2026) lido na íntegra; espelho vivo (assocarni.it) lista publicação ISMEA até **23/07/2026**, não lida | a cadência **tem buracos** — Tendenze Ortaggi saiu em 21/12/2021, 21/12/2022, 10/01/2024, 19/02/2025, março/2026: **nenhum número 1 em 2023**; é texto de análise, não série; a ferramenta não pode prometer atualização trimestral por cultura |
| CROP_PROTECTION_SECTOR_SIZE | NO | — | — | — | — | o que existe é **índice de preço** de defensivo (Eurostat `AM204000`, 125,5 em 2026-Q1) — e **índice de preço não é tamanho de mercado**, não é volume, não é faturamento. A estatística italiana de distribuição de produtos fitossanitários (volume vendido, com quebra regional) **não foi testada** nesta auditoria: NÃO SEI se abre |
| ADAMA_PRODUCT_DEMAND | NOT_MEASURED | dado **interno** ADAMA | — | — | — | nenhuma fonte pública mede demanda por produto de uma empresa. Estimar isso é proibido (LEI 7) |
| ADAMA_SALES | NOT_MEASURED | dado **interno** ADAMA | — | — | — | idem. O acervo já reprovou o atalho: *"We know market share." → contagem de registros ≠ mercado. Vale para ADAMA e para concorrentes* |
| DISTRIBUTOR_STOCK | NOT_MEASURED | dado **interno** ADAMA / canal de distribuição | — | — | — | idem. Nem o estoque de vinho da ISMEA nem o balanço de abastecimento chegam perto disso — medem país, não canal |

---

## 1. O que o Market Pulse pode mostrar HOJE, com dado real

Cada número abaixo sai com os cinco carimbos da LEI 1. Arquivos em `C:\eame-sintonia\data\samples\IT-MERCADO\`.

**a) Preço na porteira, semanal, por praça** — `EU-AGRIFOOD-cereal-prices-IT.json`
- Trigo duro, **Grosseto**, `Price at farm gate`: **€302,50 / TONNES**.
  SOURCE: European Commission — Agri-food Data Portal (`api/cereal/prices`) · REFERENCE_PERIOD: 24/08/2026–30/08/2026 · PUBLICATION_DATE: campo `referencePeriod` da própria API = **03/09/2026** (sim, um dia à frente de hoje — é o que a fonte devolve) · GEOGRAPHY: praça de Grosseto, Itália · UNIT: euro por tonelada.
- Trigo mole (`BLTPAN|PAN`), **Napoli**, entrega em silo: **€267,50/t**; **Verona**, saída da lavoura: **€226,00/t** — mesma semana.

**b) Média nacional semanal e a variação contra o ano passado** — mesmo arquivo
- Trigo duro, média nacional: **€271,83/t** (27/07–02/08/2026) contra **€295,81/t** na semana encerrada em 03/08/2025 → **-8,1%** (conta nossa).
- Milho forrageiro, média nacional: **€243,39/t**, semana anterior **€240,89/t**, um ano antes **€258,70/t**.

**c) Azeite, semanal** — `EU-AGRIFOOD-oliveOil-prices-IT.json`
- Extra virgem (até 0,8%), *Average national price*: **€488,00 / 100 kg** (27/07–02/08/2026), contra **€959,00** na semana encerrada em 03/08/2025 → **queda de 49%**. UNIT declarada pela fonte: `€/100kg`. 1.672 observações na série.

**d) Custo de insumo, trimestral, Itália** — `EUROSTAT-apri_pi_inq-input-price-index-IT.json`
SOURCE: Eurostat `apri_pi_inq` · REFERENCE_PERIOD: **2026-Q1** · PUBLICATION_DATE: **11/08/2026** · GEOGRAPHY: Itália · UNIT: índice nominal, base **2020 = 100**. Rota reconfirmada ao vivo hoje (HTTP 200, `OBS_PERIOD_OVERALL_LATEST: 2026-Q1`).

| item | índice 2026-Q1 | variação sobre 2025-Q1 |
|---|---|---|
| Input total | 130,4 | +1,40% |
| Fertilisers and soil improvers | **155,4** | **+7,62%** |
| Energy; lubricants | **156,8** | **-1,57%** |
| Plant protection products | 125,5 | +0,88% |
| — Fungicides and bactericides | 138,4 | +2,67% |
| — Herbicides | 117,0 | -1,18% |

**e) Produção, área e rendimento de cereais** — `EU-AGRIFOOD-cereal-production-IT.json` (ano 2026, Itália)
Trigo duro **3.588,31 mil t** em **1.131,96 mil ha** (3,17 t/ha) · Milho **4.527,33 mil t** em **539,61 mil ha** (8,39 t/ha) · Trigo mole **2.650,90 mil t** (5,25 t/ha). **Sempre com o aviso de unidade inferida.**

**f) Área por região, histórica** — `C:\eame-sintonia\data\samples\EU-T1-001-nuts2-crop-area.json`
Eurostat `apro_cpshr`, NUTS2, 30 regiões italianas, **só 4 culturas** (trigo comum, cevada, milho grão, beterraba). Último ano: **2024** (atualizado 28/05/2026). Ex.: Piemonte, trigo comum, 2024: **72,71 mil ha**.

---

## 2. O que só pode aparecer com interpretação declarada na tela

1. **PRICE_MOMENTUM.** A variação semanal e anual **não é publicada** — é conta nossa a partir de dois registros. Precisa dizer isso na tela, e precisa tratar o caso da praça que não cotou: o valor repetido vira "0%" e parece estabilidade quando é ausência.
2. **A linha de 2026 da produção.** O número existe; o **status não**. A fonte não tem campo dizendo se é estimativa ou fechado. Rótulo honesto: *"ano 2026 conforme a API da Comissão em 02/09/2026; a fonte não declara se é estimativa ou definitivo"*. O caso mais sensível: milho **8,39 t/ha em 2026** contra **10,19 t/ha em 2025** (-17,7%) — uma queda grande demais para ser mostrada sem esse aviso.
3. **Preço subindo × lucro do produtor (LEI 6).** Dá para mostrar os dois lados, no mesmo trimestre, mesma base, mesma geografia: em **2026-Q1**, o índice de preço recebido pelo produtor de **cereais caiu 10,29%** em 12 meses (119,4) enquanto o **custo de insumo subiu 1,40%** (130,4) e o **adubo subiu 7,62%** (155,4). O que a tela **não pode** dizer é "margem" — são dois índices diferentes, não uma conta de resultado.
4. **Unidade inferida.** mil t / mil ha / t/ha na produção de cereais foram deduzidos, não declarados. A inferência tem duas provas (aritmética interna e batimento com a ISMEA: 540,95 mil ha, 10,19 t/ha, 5.511,12 mil t contra *"541 mila ettari"*, *"10,2 t/ha"*, *"5,5 milioni di tonnellate"*), mas continua sendo inferência.
5. **Praça ≠ região.** 17 praças nomeadas não são 20 regiões italianas. E o estágio comercial muda entre elas — comparar Foggia (porteira) com Milano (silo) é comparar coisas diferentes.
6. **Tudo que vem da ISMEA.** Nenhum byte veio do servidor da ISMEA (bloqueio por geografia de IP, página *"Blocked"* com `GEO_IP_BLOCK`, inclusive em janela gráfica de Chrome real). Cada número dessa fonte precisa da data do *snapshot* na cara, não do dia de hoje.
7. **ICF (confiança).** Se for mostrado, tem que vir com três avisos: veio de imprensa e não da fonte; é escala -100 a +100 e não porcentagem; e é do **primeiro trimestre de 2025** — 18 meses atrás.

---

## 3. O que deve aparecer como NOT AVAILABLE na tela — e por quê isso é melhor

**Devem aparecer vazias, com o motivo escrito:**

| Campo | Texto sugerido para a tela |
|---|---|
| EU_MARKET_OUTLOOK | *Not available — source not tested in this audit (02/09/2026). Absence of route ≠ absence of data.* |
| CROP_PROTECTION_SECTOR_SIZE | *Not available — we hold a price index for plant protection products (Eurostat, 2026-Q1), which is not market size.* |
| ADAMA_PRODUCT_DEMAND · ADAMA_SALES · DISTRIBUTOR_STOCK | *Not available — requires ADAMA internal data. No public route measures it.* |
| SUPPLY_BALANCE · SELF_SUFFICIENCY | *Structure known, values not read — ISMEA host unreachable from this IP (GEO_IP_BLOCK).* |
| STOCK (fora do vinho) | *Route `oliveOil/productionAndStock` returned HTTP 404 "No matching resource found for given API Request" on 02/09/2026 — route not published.* |
| WINE_PRICE (se entrar na tela) | *Last observation 30/06–06/07/2025 (€61,75 / HL) — 14 months old. Not shown as current.* |

**Por que vazio é melhor que valor sintético.** Um número inventado, na tela, é **idêntico** a um número medido: mesma fonte, mesmo tamanho, mesma cor. Quem decide não tem como distinguir. Este projeto já foi mordido por isso — a régua interna proíbe *"We know market share"* justamente porque contagem de registro **não é** mercado, e o acervo tem caso de número que entrou como verdade e depois se descobriu que media outra coisa. Um campo vazio com o motivo escrito faz três coisas que o valor sintético não faz: (1) mostra a fronteira real do produto para quem compra; (2) vira uma lista de tarefas — "destravar IP italiano", "testar o outlook da DG AGRI", "abrir a estatística de distribuição de fitossanitários"; (3) protege as 12 métricas que **são** reais, porque uma única invenção descoberta contamina a leitura de todas as outras.

**O que as três métricas internas destravariam, se um dia forem conectadas:**
- **ADAMA_SALES** (sell-in por SKU/região/mês) permitiria, pela primeira vez, **testar** se os sinais públicos que medimos hoje têm alguma relação com o negócio: preço de trigo duro em Foggia, índice de adubo, área de milho, sinal fitossanitário provincial. Hoje isso é hipótese; com dado interno vira medição — com resultado possivelmente negativo, e isso também seria um resultado.
- **ADAMA_PRODUCT_DEMAND** (demanda por produto) ligaria a curva de custo de defensivo (Eurostat `AM204000`: fungicida +2,67%, herbicida -1,18% em 2026-Q1) ao comportamento real do cliente: preço médio de defensivo subindo com demanda caindo é história diferente de preço subindo com demanda firme.
- **DISTRIBUTOR_STOCK** fecharia o buraco que a própria fonte pública declara: *"producao NAO e oferta disponivel no mercado - falta estoque, importacao e exportacao"*. Sem estoque de canal, não dá para saber se uma queda de venda é queda de uso no campo ou apenas prateleira cheia da campanha anterior.

**Mesmo conectadas, continuam valendo as LEIS 5, 6 e 7:** o dado interno explicaria o passado; **prever** venda, share, estoque de distribuidor ou intenção de compra segue proibido.