# MARKET PULSE — OLIVO / OLIO DI OLIVA · ITALIA

**Data da montagem:** 02/09/2026 · **Cultura:** olivo / azeite de oliva · **País:** Itália

---

## 0 · O QUE ENTROU NESTA FICHA, E O QUE NÃO ENTROU

| Fonte | Estado | O que dela foi lido |
|---|---|---|
| **European Commission — Agri-food Data Portal** (`SOURCE_ID: EU-T10-002`) | **ALCANÇADA** | `EU-AGRIFOOD-oliveOil-prices-IT.json` — 23.387 registros, 36 pares produto×praça. `CAPTURED_AT: 2026-09-02`. `EVIDENCE_CLASS: OFFICIAL_MARKET_OBSERVATION`. `APIFY_RUNS: 0`, `COST_USD: 0` |
| **ISMEA** | **BLOCKED — fonte ao vivo não alcançada** | Tudo veio de Internet Archive e de espelho de terceiro. A própria ficha declara: *"A FONTE AO VIVO NAO FOI ALCANCADA. Nenhum byte lido veio do servidor da ISMEA"*, com a página de bloqueio ecoando `GEO_IP_BLOCK` e o IP de origem |
| **Consorzio Fitosanitario Provinciale di Modena** (`IT-T3-ER-MODENA`) | **ALCANÇADA** | Sinal de campo de *Bactrocera oleae*, 01/09/2026 — **não é dado de mercado**, entra só na seção 8 |
| **ISTAT · Eurostat · JRC MARS — produção e rendimento de olivo** | **NÃO ALCANÇADAS NESTA RODADA** | Ver seção 2. `EU-T1-001-nuts2-crop-area.json` (Eurostat `apro_cpshr`, capturado 28/08/2026) cobre só 4 códigos de cultura — `C1110`, `C1300`, `C1500`, `R2000` — **nenhum é olivo** |
| **As outras 6 fichas de fonte desta rodada** | **NÃO CHEGARAM LEGÍVEIS** | O bloco de material entregue foi cortado no meio do primeiro item (ISMEA). **NÃO SEI** o que elas continham. Isso é FONTE NÃO ALCANÇADA, não fonte vazia (LEI 3) |

**Defasagem do dado mais fresco:** a última semana cotada no arquivo termina em **02/08/2026** e a captura é de **02/09/2026** — **31 dias de distância**. Não sei se o portal já publicou as semanas de agosto e o arquivo é um retrato anterior, ou se a série pausou. NÃO SEI.

**Aviso de comparabilidade que a própria fonte impõe:** o campo `STAGE` (estágio comercial) vem **`null` em todos os 36 pares**, e o arquivo declara: *"nao e o mesmo estagio comercial entre pracas — ver STAGE"*. Ou seja: comparar Palermo com Cosenza é comparar dois preços cujo estágio a fonte não informa. Está registrado; não está resolvido.

---

## 1 · ESTADO CORRENTE — PREÇO POR PRAÇA

**SOURCE:** European Commission — Agri-food Data Portal · **RESOLVED_URL:** `https://api.tech.ec.europa.eu/agrifood/api/oliveOil/prices?memberStateCodes=IT&years=2025,2026` · **GEOGRAPHY:** Itália, praça nomeada (código NUTS entre parênteses) · **UNIT:** €/100 kg · **REFERENCE_PERIOD:** semana 27/07/2026 a 02/08/2026 · **PUBLICATION_DATE:** NÃO SEI — o arquivo traz `BEGIN`/`END` da semana e `CAPTURED_AT: 2026-09-02`, não a data em que a Comissão publicou · **MARKETING_YEAR declarado:** 2025/2026

**24 dos 36 pares** cotaram nessa semana. **12 pares estão com a série PARADA.**

### 1.1 · Extra virgin olive oil (até 0,8%) — o grau que puxa a receita do olivicultor

| Praça | Preço (€/100 kg) | vs semana anterior | vs ano anterior (semana encerrada 03/08/2025) | Obs. na série |
|---|---:|---:|---:|---:|
| **Average national price** | **488,00** | 493,00 → **−1,01%** | 959,00 → **−49,11%** | 1.672 |
| Palermo (ITG12) | 745,00 | 745,00 → **0,00%** | 990,00 → **−24,75%** | 755 |
| Trapani (ITG11) | 745,00 | 750,00 → **−0,67%** | 970,00 → **−23,20%** | 751 |
| Taranto (ITF43) | 480,00 | 480,00 → **0,00%** | 960,00 → **−50,00%** | 787 |
| Bari (ITF42) | 455,00 | 455,00 → **0,00%** | 965,00 → **−52,85%** | 779 |
| Foggia (ITF41) | 455,00 | 455,00 → **0,00%** | 938,00 → **−51,49%** | 789 |
| Cosenza (ITF61) | 405,00 | 415,00 → **−2,41%** | 965,00 → **−58,03%** | 781 |
| Catanzaro (ITF63) | 400,00 | 410,00 → **−2,44%** | 970,00 → **−58,76%** | 783 |
| ⛔ **Salerno (ITF35)** | **630,00** | — | — | 211 |

⛔ **Salerno — SÉRIE PARADA EM 2015.** Última cotação: semana **07/09/2015 a 13/09/2015**, `MARKETING_YEAR: 2014/2015`, €630,00/100 kg. Não é preço corrente de Salerno. É o último preço que existiu.

**Leitura literal do que a tabela mostra:** das 8 praças vivas de EVO, **nenhuma subiu** contra o ano anterior; **3 caíram** na semana e **5 ficaram iguais**. O intervalo entre a praça mais cara e a mais barata é de **400,00 a 745,00 €/100 kg** — a Sicília cota **86% acima** da Calábria — mas com `STAGE` não declarado, **não sei** se é o mesmo estágio comercial.

### 1.2 · Lampante olive oil (2%) — o grau defeituoso, que vai para refino

| Praça | Preço (€/100 kg) | vs semana anterior | vs ano anterior (03/08/2025) | Obs. |
|---|---:|---:|---:|---:|
| **Average national price** | **279,00** | 279,00 → **0,00%** | 229,00 → **+21,83%** | 1.088 |
| Brindisi (ITF44) | 300,00 | 300,00 → **0,00%** | 230,00 → **+30,43%** | 789 |
| Lecce (ITF45) | 300,00 | 300,00 → **0,00%** | 230,00 → **+30,43%** | 790 |
| Taranto (ITF43) | 300,00 | 300,00 → **0,00%** | 230,00 → **+30,43%** | 789 |
| Catanzaro (ITF63) | 275,00 | 275,00 → **0,00%** | 225,00 → **+22,22%** | 745 |
| Gioia Tauro | 250,00 | 250,00 → **0,00%** | 230,00 → **+8,70%** | 774 |
| ⛔ **Bari (ITF42)** | 153,00 | — | — | **1** |

⛔ **Bari lampante — SÉRIE PARADA EM 2011.** Única cotação do par no arquivo inteiro (`OBSERVATIONS_IN_SERIES: 1`): semana **17/01/2011 a 23/01/2011**, €153,00/100 kg.

**O fato aritmético, sem interpretação:** no ano passado o EVO nacional valia **4,19×** o lampante nacional (959 ÷ 229). Nesta semana vale **1,75×** (488 ÷ 279). A distância entre o azeite bom e o azeite defeituoso encolheu.

### 1.3 · Virgin olive oil (até 2%)

| Praça | Preço (€/100 kg) | Semana | vs anterior | vs ano anterior | Obs. |
|---|---:|---|---:|---:|---:|
| **Average national price** | **350,00** | 27/07–02/08/2026 | 350,00 → **0,00%** | 400,00 → **−12,50%** | 1.660 |
| Brindisi (ITF44) | 350,00 | 27/07–02/08/2026 | 350,00 → **0,00%** | 400,00 → **−12,50%** | 789 |
| Lecce (ITF45) | 350,00 | 27/07–02/08/2026 | 350,00 → **0,00%** | 400,00 → **−12,50%** | 790 |
| Taranto (ITF43) | 350,00 | 27/07–02/08/2026 | 350,00 → **0,00%** | 400,00 → **−12,50%** | 789 |
| ⛔ Catanzaro (ITF63) | 590,00 | **16/02–22/02/2026** | 590,00 → 0,00% | 785,00 (02/02/2025) → −24,84% | 561 |
| ⛔ Cosenza (ITF61) | 590,00 | **16/02–22/02/2026** | 590,00 → 0,00% | 795,00 (02/02/2025) → −25,79% | 549 |
| ⛔ Salerno (ITF35) | 255,00 | **21/12–27/12/2020** | 330,00 → −22,73% | — | 215 |
| ⛔ Bari (ITF42) | 352,00 | **25/12–31/12/2017** | 352,00 → 0,00% | 420,00 (04/12/2016) → −16,19% | 348 |

⛔ **Catanzaro e Cosenza pararam em FEVEREIRO DE 2026** — dentro da campanha 2025/2026 corrente. As duas ainda cotam EVO e lampante na semana atual; **só a linha "virgin" parou**. NÃO SEI por quê.

### 1.4 · Graus industriais — refinado e bagaço (NÃO são preço recebido pelo olivicultor)

| Produto · Praça | Preço (€/100 kg) | Semana | vs anterior | vs ano anterior |
|---|---:|---|---:|---:|
| Refined olive oil (0,3%) · **Average national** | 330,00 | 27/07–02/08/2026 | 333,00 → **−0,90%** | 335,00 → **−1,49%** |
| Refined olive oil · Foggia (ITF41) | 343,00 | 27/07–02/08/2026 | 343,00 → **0,00%** | 325,00 → **+5,54%** |
| Refined olive oil · Milano (ITC45) | 322,00 | 27/07–02/08/2026 | 330,00 → **−2,42%** | 340,00 → **−5,29%** |
| ⛔ Refined olive oil · Bari (ITF42) | 356,00 | **25/12–31/12/2017** | — | — |
| Refined olive-pomace (0,3%) · **Average national** | 207,00 | 27/07–02/08/2026 | 207,00 → **0,00%** | 222,00 → **−6,76%** |
| Refined olive-pomace · Foggia (ITF41) | 211,00 | 27/07–02/08/2026 | 211,00 → **0,00%** | 221,00 → **−4,52%** |
| Refined olive-pomace · Milano (ITC45) | 209,00 | 27/07–02/08/2026 | 210,00 → **−0,48%** | 230,00 → **−9,13%** |
| ⛔ Refined olive-pomace · Bari (ITF42) | 226,00 | **25/12–31/12/2017** | — | — |
| ⛔ Olive-pomace oil (1%) · **Average national** | 119,67 | **21/06–27/06/2010** | — | — |
| ⛔ Olive-pomace oil · Milano (ITC45) | 124,00 | **21/06–27/06/2010** | — | — |
| ⛔ Olive-pomace oil · Foggia (ITF41) | 118,00 | **21/06–27/06/2010** | — | — |
| ⛔ Olive-pomace oil · Bari (ITF42) | 117,00 | **21/06–27/06/2010** | — | — |

⛔ **A linha inteira "Olive-pomace oil (up to 1%)" está PARADA EM 2010** — as 4 praças, com `OBSERVATIONS_IN_SERIES: 1` cada. É uma linha morta no arquivo, não um mercado de hoje.

### 1.5 · O outro instrumento de preço — ISMEA, e por que não pode ser subtraído do primeiro

- **Índice ISMEA dos preços na produção — Olio d'oliva: 173,36… não: 321,44** · UNIT: número índice, base 2010=100 · REFERENCE_PERIOD: **julho de 2025** · PUBLICATION_DATE: até 15/09/2025 (data do snapshot no Internet Archive) · GEOGRAPHY: Itália · SOURCE: ISMEA (via Internet Archive; fonte ao vivo BLOCKED).
  Citação literal: **`Olio d'oliva 321,44 -1,3 -10,9`** — isto é, −1,3% sobre junho/2025 e **−10,9% sobre julho/2024**.
- **Listini médios do EVO italiano** · UNIT: euro/kg · REFERENCE_PERIOD: annata 2025/26 · PUBLICATION_DATE: **22/01/2026** · SOURCE: ISMEA, comunicado AgriMercati.
  Citação literal: *"i listini medi dell'EVO italiano scesi mediamente poco al di sotto di 8 euro/kg"*.

⚠️ **Não calculei variação entre esses €8/kg e os €4,88/kg do portal europeu**, e ninguém deve calcular. São dois instrumentos diferentes — "listino médio" da ISMEA e "Average national price" da Comissão — com estágio comercial não declarado nos dois lados. Colocar um menos o outro fabricaria um número que nenhuma fonte publicou. O que se pode dizer é só isto: **as duas fontes apontam para o mesmo lado, queda**, cada uma no seu próprio período.

---

## 2 · PRODUÇÃO E RENDIMENTO

### ISTAT · Eurostat · JRC MARS — **NÃO ALCANÇADOS NESTA RODADA. NÃO SEI.**

Isto é ausência de coleta, não ausência de dado (LEI 3). O que foi verificado:

- **Eurostat:** o arquivo de área que existe no acervo (`data/samples/EU-T1-001-nuts2-crop-area.json`, Eurostat `apro_cpshr`, capturado em 28/08/2026) cobre **4 códigos de cultura: `C1110` (Common wheat and spelt), `C1300`, `C1500`, `R2000`** — **nenhum é olivo**. O próprio arquivo declara: *"apenas FR/ES/IT, nivel NUTS2. Rendimento (YLD) NAO existe em NUTS2 — so pais."*
- **ISTAT:** não há número de área ou produção de olivo no acervo. O documento `research/italy-demo-reality/ITALY-REGIONAL-CROP-REALITY.md` registra o buraco em texto: *"**Nenhuma fonte** para olivo, barbabietola, patata e girassol, culturas com registro ADAMA"*.
- **JRC MARS:** nenhum boletim lido nesta rodada. NÃO SEI.

### O que existe, e vem só da ISMEA — declarado como reempacotamento, não como medição própria

⚠️ Registro importante da ficha ISMEA: para superfície e produção, *"A pagina diz literalmente: 'In questa sezione pubblichiamo i dati di fonte Istat (http://dati.istat.it/) o di altra fonte ufficiale'"* — ou seja, **a ISMEA é reembaladora; a fonte primária é o ISTAT**, que não foi alcançado.

| Número | Valor | UNIT | REFERENCE_PERIOD | PUBLICATION_DATE | GEOGRAPHY |
|---|---|---|---|---|---|
| Produção italiana de azeite | **248 mil toneladas (−24%)** | mil t | ano de **2024** | **01/08/2025** | Itália |
| Empresas e lagares ativos | **620 mil empresas · mais de 4.240 frantoi** | contagem | 2024 | 01/08/2025 | Itália |

Citação literal (ISMEA, Scheda di settore, 01/08/2025): *"Con una produzione 2024 pari a 248 mila tonnellate (-24%), il settore ha comunque resistito grazie alla struttura diffusa e capillare: 620 mila aziende e oltre 4.240 frantoi attivi"*.

**Rendimento (t/ha) e área plantada (ha) de olivo na Itália: NÃO SEI.** Nenhuma fonte alcançada nesta rodada publicou esses dois números. E sem área, os 248 mil t **não podem** virar produtividade.

**Balanço de abastecimento:** a ISMEA declara publicar "Bilanci di approvvigionamento" com **Olio d'oliva** entre as culturas cobertas, cadência anual, *"ultimo aggiornamento: gennaio 2026"*, série de 5 anos, com fórmula publicada *"Autoapprovvigionamento = produzione / consumo (autosufficienza se >100)"*. **Nenhum número foi lido** — o Excel está atrás do host bloqueado. A capacidade existe; o valor, NÃO SEI.

---

## 3 · OFERTA E COMÉRCIO

| Número | Valor | UNIT | REFERENCE_PERIOD | PUBLICATION_DATE | GEOGRAPHY | SOURCE |
|---|---|---|---|---|---|---|
| Exportação italiana de azeite | **303 mil toneladas (+17%)** | mil t | **primeiros nove meses de 2025** | **22/01/2026** | Itália | ISMEA / AgriMercati |
| Exportação italiana de azeite | **344 mil toneladas (+6,8%)**, valor **acima de 3,09 bilhões de euros (+42,6% sobre 2023)** | mil t · bilhões € | **ano de 2024** | **01/08/2025** | Itália | ISMEA / Scheda di settore |

Citações literais: *"nei primi nove mesi 2025 export a 303 mila tonnellate (+17%)"* · *"Nel 2024 l'export ha registrato un aumento del 6,8%, raggiungendo 344 mila tonnellate per un valore superiore a 3,09 miliardi di euro (+42,6% sul 2023)"*.

⚠️ **Duas cadências diferentes na mesma linha** (LEI 2): 303 mil t são **nove meses** de 2025; 344 mil t são **doze meses** de 2024. Não são comparáveis entre si e não devem ser postos lado a lado como se fossem a mesma medida.

⚠️ **O valor de exportação de 2024 subiu 42,6% enquanto o volume subiu 6,8%.** A distância entre os dois é preço, não volume vendido a mais.

**IMPORTAÇÃO italiana de azeite: NÃO SEI.** Nenhum número de importação foi lido. E vale o registro preventivo (LEI 5): se em alguma rodada futura aparecer importação subindo, isso **não** é demanda subindo — pode ser quebra de safra local, arbitragem de preço, reexportação depois de blend, ou formação de estoque da indústria. O banco de comércio exterior da ISMEA, aliás, avisa que *"Il totale Agroalimentare e ottenuto dalla aggregazione di voci doganali a 8 digit (NC8) e non comprende i dati soggetti a segreto statistico"*.

**Estoques de azeite na Itália: NOT AVAILABLE.** Nenhuma fonte alcançada publicou. (Estoque foi lido para **vinho** — 40,6 milhões de hl em julho/2025 — e é de **outra cultura**; não entra aqui.)

---

## 4 · CONFIANÇA DO PRODUTOR

**Qual é o setor:** a ISMEA publica o **Indice ISMEA del clima di fiducia (ICF), setor AGRICOLTURA**, e entre os setores que ela discrimina está literalmente **"Olio d'oliva"** — ao lado de Ortaggi, Frutta, Agrumi, Vino, Cereali, Latte, carnes.

**Valor corrente: NÃO SEI. Nenhum número foi lido.**

Por quê, na letra da ficha: *"NAO CONSEGUI LER NENHUM VALOR CORRENTE. O numero nao esta no HTML: mora em 6 arquivos XML de grafico em /flex/tmp/FlexFCharts/... e todos os 6 dao HTTP 404 no Internet Archive."*

O que se sabe sobre o calendário, e nada além:
- **Cadência:** trimestral · **GEOGRAPHY:** Itália
- **Último relatório datado:** *"La congiuntura Agricola - IV trimestre 2025"*, **publicado em 29/01/2026** (lido em snapshot de 23/04/2026)
- Se a ISMEA manteve o ritmo, o 1º e o 2º trimestre de 2026 já saíram até hoje — **mas isso eu NÃO SEI**: não há snapshot posterior a abril/2026 dessa lista.

**Duas armadilhas de leitura, registradas pela própria ficha:**
1. **A escala vai de −100 a +100 e NÃO é percentual.** A imprensa italiana já publicou *"indice Ismea a -1,4%"* com sinal de porcentagem indevido.
2. O índice **sintetiza duas coisas** — *"l'andamento corrente degli affari della loro azienda"* e *"le attese sull'evoluzione economica della stessa nei prossimi 2-3 anni"* — mas a página pública mostra **só o valor único**. As duas componentes separadas não foram vistas.

**LEI 4, aplicada aqui:** ainda que o setor se chame "Olio d'oliva", ele é **um setor de cadeia inteira**, não o produtor de uma praça. Confiança de setor não é confiança do olivicultor de Cosenza.

---

## 5 · PRESSÃO DE CUSTO

### **NÃO SEI. Nenhum índice de custo foi lido nesta rodada.**

Isto é o buraco mais grave desta ficha, e ele é assimétrico: o lado da **receita** (preço) está medido semana a semana em 24 praças; o lado do **custo** está em branco.

O que foi verificado, item a item:

| Item | Estado | Evidência |
|---|---|---|
| **ISMEA — Indice dei prezzi dei mezzi correnti di produzione** (custo de insumos) | **capacidade existe, valor NÃO LIDO** | A série baixável *"parava em 2024 no snapshot de abril/2026"* — mais de um ano de defasagem contra o índice de preços, que é mensal. E a página dedicada `/dati-agroalimentare/indice-costi` aparecia como **"Pagina non piu disponibile"** no snapshot de 18/11/2025 |
| **Rubrica separada para "prodotti fitosanitari"** dentro das *voci di spesa* | **NÃO SEI** | Ficha literal: *"NAO SEI se existe uma rubrica separada para 'prodotti fitosanitari' dentro das 'voci di spesa'; nao consegui abrir o arquivo"* |
| **Fertilizante — índice de preço, Itália** | **NÃO COLETADO** | Nenhuma fonte alcançada nesta rodada. NÃO SEI |
| **Energia / diesel agrícola — índice, Itália** | **NÃO COLETADO** | Nenhuma fonte alcançada nesta rodada. NÃO SEI |
| **Custo de colheita / mão de obra no olival** | **NÃO COLETADO** | NÃO SEI |

**LEI 6, e ela morde nos dois sentidos:** preço alto de cultura não é lucro do produtor — mas **preço baixo também não é prejuízo comprovado**. Sem o índice de custo, a queda de 49% no EVO nacional é meia conta. Não sei o que aconteceu com o outro lado da subtração, e não vou fingir que sei.

---

## 6 · OUTLOOK — **PROJEÇÃO DE TERCEIRO, NÃO ESTADO CORRENTE**

> **Toda esta seção é avaliação prospectiva feita pela ISMEA e assinada por ela.** Não é medição, não é o estado de hoje, e não é do Sintonia.

**Projeção da ISMEA** · PUBLICATION_DATE: **22/01/2026** · REFERENCE_PERIOD: **annata 2025/26** · GEOGRAPHY: Itália · SOURCE: ISMEA, comunicado AgriMercati 1/2026 (lido via Internet Archive; fonte ao vivo BLOCKED)

Citação literal: *"Olio EVO - Annata 2025/26 di media carica, con produzione in crescita rispetto alla campagna precedente, grazie soprattutto alle regioni del Sud; di conseguenza, i listini medi dell'EVO italiano scesi mediamente poco al di sotto di 8 euro/kg"*.

Em português direto: a ISMEA descreveu a safra 2025/26 como **de carga média, com produção em crescimento sobre a campanha anterior, puxada sobretudo pelas regiões do Sul** — e ligou explicitamente essa maior produção à queda dos listini, com o *"di conseguenza"*.

**Três ressalvas que ficam inteiras:**
1. **A projeção tem 7 meses e 11 dias.** Foi publicada em 22/01/2026; hoje é 02/09/2026. NÃO SEI se a ISMEA a revisou desde então — a fonte ao vivo está bloqueada.
2. **A causalidade é da ISMEA, não minha.** O *"di conseguenza"* é da fonte. Não medi essa relação.
3. **Para a safra 2026/27** — a que será colhida entre outubro e dezembro de 2026, ou seja, a próxima — **nenhuma previsão foi lida. NÃO SEI.** Nem de produção, nem de preço, nem de área.

---

## 7 · TEMPERATURA DE MERCADO

# PRESSURED

> ⚠️ **ISTO É INTERPRETAÇÃO DO SINTONIA, NÃO FATO OBSERVADO.** É uma palavra que eu escolhi olhando as setas abaixo. Nenhuma fonte publicou a palavra "PRESSURED". As setas, essas sim, são leitura direta dos números citados nas seções 1 a 6.

### « POR QUE »

| Componente | Seta | O que sustenta |
|---|:---:|---|
| **EVO — preço nacional vs ano anterior** | **↓↓** | 488,00 contra 959,00 €/100 kg = **−49,11%** (semanas encerradas em 02/08/2026 e 03/08/2025) |
| **EVO — todas as praças vivas vs ano anterior** | **↓↓** | **8 de 8 caíram. Nenhuma subiu.** Amplitude da queda: de −23,20% (Trapani) a −58,76% (Catanzaro) |
| **EVO — semana contra semana** | **↓ fraca** | 3 praças caíram (−0,67% a −2,44%), 5 ficaram iguais, **0 subiram**. O movimento semanal é pequeno; a queda grande está no eixo anual |
| **Lampante — vs ano anterior** | **↑** | **CONTRA-SINAL.** Nacional +21,83%; Brindisi, Lecce e Taranto +30,43% cada. Sobe enquanto o EVO desaba |
| **Distância EVO ÷ lampante** | **↓↓** | Era **4,19×** há um ano; é **1,75×** agora. O prêmio do azeite bom encolheu |
| **Virgin (até 2%) — vs ano anterior** | **↓** | −12,50% nas 4 praças vivas. Cai, mas muito menos que o EVO |
| **Refinado (industrial) — vs ano anterior** | **↔ / misto** | Nacional −1,49%; Milano −5,29%; **Foggia +5,54%**. Sem direção única |
| **Bagaço refinado — vs ano anterior** | **↓ leve** | Nacional −6,76%; Milano −9,13%; Foggia −4,52% |
| **Oferta (produção)** | **↑** | A ISMEA descreveu a 2025/26 como *"di media carica, con produzione in crescita rispetto alla campagna precedente"* (22/01/2026) — e ligou isso à queda de listini |
| **Comércio (exportação)** | **↑, mas velho** | 303 mil t nos 9 primeiros meses de 2025, +17% — publicado em 22/01/2026. Não sei o que aconteceu depois |
| **Confiança do produtor** | **NÃO SEI** | O setor "Olio d'oliva" existe no ICF da ISMEA; nenhum valor foi lido (6 XMLs em HTTP 404) |
| **Pressão de custo** | **NÃO SEI** | Nenhum índice de insumo, fertilizante ou energia foi lido. Metade da conta de margem está ausente |
| **Saúde da própria série de dados** | **↓** | **12 dos 36 pares estão parados**, e **2 pararam dentro desta campanha** (Catanzaro e Cosenza virgin, fevereiro/2026). O painel está afinando |

**Por que PRESSURED e não outra palavra:** a queda do EVO é o único movimento que aparece em **todas as praças vivas, sem exceção, na mesma direção**, e a fonte que fala de oferta diz que a produção cresceu. As setas para cima existem — lampante e exportação — mas o lampante é um grau inferior, sobre base baixa, e a exportação é um número de janeiro/2026.

**Por que NÃO usei MIXED SIGNALS:** foi a alternativa real. O lampante subindo 30% enquanto o EVO cai 50% é divergência de verdade, e a distância Sicília×Calábria (745 contra 400) é dispersão de verdade. Se alguém ler esta ficha e concluir MIXED SIGNALS, a leitura é defensável com os mesmos números. Escolhi PRESSURED porque a seta do grau que define a receita do olivicultor é unânime. **A escolha é minha e é discutível — está aqui exposta para poder ser contestada.**

---

## 8 · O QUE ISTO NÃO AUTORIZA A DIZER

**Sobre venda, cliente e portfólio — proibido em qualquer redação:**
1. **Não autoriza prever venda da ADAMA**, share, estoque de distribuidor ou intenção de compra de ninguém. Nada nesta ficha mede isso, em nenhum grau.
2. **Não autoriza dizer "o produtor vai gastar menos com defensivo"** porque o preço do azeite caiu. Não existe nesta ficha nenhum vínculo medido entre preço da azeitona e compra de insumo.
3. **Não autoriza "oportunidade comercial"**, "mercado quente", nota de 0 a 100, nem qualquer previsão de venda.

**Sobre o preço:**
4. **Preço não é lucro.** O EVO nacional caiu 49,11% em um ano — e o custo do olivicultor **não foi medido**. Sem o outro lado, não se pode dizer que a margem caiu, nem quanto.
5. **Não autoriza comparar praças como se fossem a mesma coisa.** `STAGE` é `null` nos 36 pares. Palermo a 745 e Catanzaro a 400 podem estar em estágios comerciais diferentes.
6. **Não autoriza subtrair a ISMEA da Comissão Europeia.** Os €8/kg da ISMEA (22/01/2026) e os €4,88/kg do portal (semana de 02/08/2026) são instrumentos diferentes, em datas diferentes.
7. **Não autoriza chamar os €488 de "preço de hoje".** É a semana encerrada em **02/08/2026** — **31 dias** antes da captura. E não sei se o portal já publicou agosto.
8. **Não autoriza usar as 12 séries paradas como preço corrente.** Salerno EVO é 2015. Bari lampante é 2011. A linha inteira de olive-pomace oil é 2010.
9. **Não autoriza dizer que uma praça "parou de cotar".** Sei que o arquivo capturado em 02/09/2026 não traz cotação nova. Não sei o motivo, e não sei se voltou. FONTE NÃO ALCANÇADA ≠ FONTE VAZIA.

**Sobre a lacuna de produção:**
10. **Não autoriza afirmar rendimento, produtividade ou área de olivo na Itália.** ISTAT, Eurostat e JRC MARS não foram alcançados. Os 248 mil t de 2024 são **produção de azeite reembalada pela ISMEA a partir do ISTAT**, e sem área não viram t/ha.
11. **Não autoriza dizer que o ISTAT "não tem" o dado.** Não foi consultado nesta rodada.
12. **Não autoriza tratar as outras 6 fichas da rodada como inexistentes.** Elas não chegaram legíveis até mim. NÃO SEI o que continham — pode haver dado de produção, custo ou confiança lá dentro.

**Sobre o único sinal de campo de olivo que existe no acervo:**
13. Há um sinal de **mosca das olivas (*Bactrocera oleae*)** publicado pelo Consorzio Fitosanitario Provinciale di Modena em **01/09/2026**, dizendo que houve *"incremento das capturas em todo o comprensório olivícola"*. **Isso não entra em nenhuma linha deste MARKET PULSE.** A própria ficha do sinal declara: *"captura em armadilha NÃO é dano no fruto"* e *"não prova infestação, não prova perda"*. Não é dado de mercado, não é dado de produção, e não pode ser costurado ao preço para sugerir que a safra 2026/27 está ameaçada. A ficha lista como afirmação proibida, na letra: *"a praga está aumentando na Itália"* e *"há oportunidade comercial"*.

---

### Arquivos e rotas

- Preços lidos: `C:\eame-sintonia\data\samples\IT-MERCADO\EU-AGRIFOOD-oliveOil-prices-IT.json`
- Sinal de campo (fora do pulse, citado só na seção 8): `C:\eame-sintonia\data\samples\IT-CAMPO-ATUAL\IT-SINAIS-CAMPO-SETEMBRO-2026.json`
- Buraco de fonte de olivo registrado em: `C:\eame-sintonia\research\italy-demo-reality\ITALY-REGIONAL-CROP-REALITY.md`
- Área Eurostat verificada e sem olivo: `C:\eame-sintonia\data\samples\EU-T1-001-nuts2-crop-area.json`
- ISMEA: **fonte ao vivo BLOCKED por geografia de IP** (`GEO_IP_BLOCK`). Todo número atribuído à ISMEA nesta ficha veio de snapshot do Internet Archive, com a data do snapshot declarada item a item.