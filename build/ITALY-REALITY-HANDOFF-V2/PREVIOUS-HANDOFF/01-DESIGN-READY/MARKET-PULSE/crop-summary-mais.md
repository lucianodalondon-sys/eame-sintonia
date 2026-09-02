# MARKET PULSE — MAIS (milho grão) · ITÁLIA

**Cultura:** MAIS / grain maize · **País:** ITÁLIA · **Data de montagem:** 02/09/2026
**Fontes com lastro nesta ficha:** 3 (EU Agri-food Data Portal · Eurostat `apro_cpshr` · ISMEA via Internet Archive)
**Fontes que a ficha precisaria e NÃO alcançou:** ISTAT direto, JRC MARS, índice de custo de insumo italiano corrente

> Regra que vale para a ficha inteira: **"não achei" = NÃO SEI, nunca "não existe".** Onde a fonte não foi alcançada está escrito NÃO ALCANÇADA, e isso não é o mesmo que fonte vazia.

---

## 1. ESTADO CORRENTE — preço por praça

**SOURCE:** European Commission — Agri-food Data Portal (`EU-T10-002`)
**ROTA:** `https://api.tech.ec.europa.eu/agrifood/api/cereal/prices?memberStateCodes=IT&years=2025,2026`
**PRODUTO NA FONTE:** `MAI|FEED` (praças) e `Feed maize` (média nacional)
**GEOGRAPHY:** mercado nomeado dentro da Itália · **UNIT:** EUR/TONELADA
**CAPTURED_AT:** 2026-09-02 · **PUBLICATION_DATE por registro:** NÃO SEI — a fonte carimba `REFERENCE_PERIOD`, que é a data de referência do portal, cerca de 10 dias depois do fim da semana cotada. Uso as duas datas lado a lado.
**EVIDENCE_CLASS:** `OFFICIAL_MARKET_OBSERVATION`
**Base:** 16.193 registros, 40 pares produto × praça no arquivo; 11 deles são milho.

| Praça | Preço | Semana cotada (BEGIN–END) | Ref. do portal | Estágio comercial (STAGE) | vs período anterior | vs ano anterior | Obs. na série |
|---|---|---|---|---|---|---|---|
| **Média nacional** (`Feed maize`) | **€243,39/t** | 27/07–02/08/2026 | 06/08/2026 | National Average – Not Specified | **+€2,50 (+1,04%)** | **−€15,31 (−5,92%)** vs 03/08/2025 (€258,70) | 522 |
| Roma | €284,00/t | 03–09/08/2026 | 13/08/2026 | Departure from farm or from production area | €0,00 (0,00%) | −€5,00 (−1,73%) vs €289,00 | 498 |
| Milano | €252,50/t | 03–09/08/2026 | 13/08/2026 | Deliver to first customer – silo/processing plant | €0,00 (0,00%) | −€20,50 (−7,51%) vs €273,00 | 502 |
| Bologna | €245,00/t | 03–09/08/2026 | 13/08/2026 | Deliver to first customer – silo/processing plant | €0,00 (0,00%) | −€17,00 (−6,49%) vs €262,00 | 510 |
| Mantova | €243,50/t | 17–23/08/2026 | 27/08/2026 | Departure from farm or from production area | €0,00 (0,00%) | −€18,00 (−6,88%) vs €261,50 | 513 |
| Udine | €239,00/t | 03–09/08/2026 | 13/08/2026 | Departure from farm or from production area | **+€2,00 (+0,84%)** | −€7,00 (−2,85%) vs €246,00 | 501 |
| Treviso | €237,00/t | 17–23/08/2026 | 27/08/2026 | Departure from farm or from production area | €0,00 (0,00%) | −€15,00 (−5,95%) vs €252,00 | 494 |
| Reggio Emilia | €234,00/t | 03–09/08/2026 | 13/08/2026 | Departure from farm or from production area | €0,00 (0,00%) | −€19,00 (−7,51%) vs €253,00 | 482 |
| Alessandria ⚠️ | €217,00/t | 06–12/07/2026 | 16/07/2026 | Price at farm gate | €0,00 (0,00%) | −€18,00 (−7,66%) vs €235,00 (13/07/2025) | 387 |
| Perugia | €216,10/t | 03–09/08/2026 | 13/08/2026 | Price at farm gate | €0,00 (0,00%) | −€17,00 (−7,29%) vs €233,10 | 489 |
| **Napoli 🛑 SÉRIE PARADA — 2026** | €221,00/t | **04–10/05/2026** | 14/05/2026 | Deliver to first customer – silo/processing plant | −€51,50 (−18,90%) | **NÃO SEI** (`YEAR_AGO_PRICE_NUM` = null) | 351 |

**Marcações obrigatórias:**

- 🛑 **Napoli — série PARADA em 2026.** A última cotação de milho de Nápoles é a semana de **04–10/05/2026**, quase quatro meses antes da captura (02/09/2026). O −18,90% é o último movimento gravado *antes* de a série parar — **não é uma queda de agora, e não sabemos se o preço seguiu caindo, subiu ou parou de ser cotado**. `YEAR_AGO_PRICE_NUM` vem `null`: não há comparação anual possível nessa praça.
- ⚠️ **Alessandria — atrasada, não parada.** Última cotação em 06–12/07/2026, cerca de 7 semanas antes da captura. A comparação anual dela usa 13/07/2025, não 03/08/2025 como as demais.
- **Não é falha do arquivo.** A própria fonte declara, literalmente: *"nao e serie continua: praca que nao cotou na semana nao aparece"*.
- **Comparar praça com praça exige olhar o STAGE antes.** As 10 praças de milho usam **três estágios comerciais diferentes** (farm gate, departure from farm, deliver to first customer). O aviso é da fonte, literal: *"nao e o mesmo estagio comercial entre pracas — ver STAGE"* e *"comparar pracas diferentes exige conferir STAGE e UNIT antes"*. Roma (€284,00) e Perugia (€216,10) não estão medindo o mesmo ponto da cadeia.
- **As variações percentuais desta tabela são cálculo do Sintonia** sobre os campos `PRICE_NUM`, `PREV_PRICE_NUM` e `YEAR_AGO_PRICE_NUM`. A fonte publica os preços, não os deltas.
- O preço na fonte é **texto**: *"sim — \"€237,00\". PRICE_RAW preserva o original; PRICE_NUM e a conversao, e vem None quando o formato nao foi reconhecido. Nunca 0."*
- Aviso literal da fonte sobre o que estes números **não** são: *"nao e preco pago pela ADAMA nem por ninguem em particular"*.
- **Sinal de que o dataset carrega séries congeladas de verdade:** no mesmo arquivo, o trigo duro em **Catania** está parado desde a semana de **11–17/07/2022**. Outra cultura, mas serve de alerta: preço "mais recente" no arquivo nem sempre é preço recente.

**Leitura em uma frase:** o milho italiano está **estável de uma semana para a outra** (8 das 10 praças com 0,00% de variação) e **abaixo do ano passado em todas as 9 praças que permitem comparação anual** (−1,73% a −7,66%; média nacional −5,92%).

---

## 2. PRODUÇÃO E RENDIMENTO

### 2.1 Área — Eurostat (dado alcançado e lido)

**SOURCE:** Eurostat `apro_cpshr` — *"Crop production by NUTS 2 region"* (`EU-T1-001`)
**MEASURE:** *"AR_THS_HA (area, mil hectares)"* · **CROP:** `C1500` — *"Grain maize and corn-cob-mix"*
**GEOGRAPHY:** região NUTS2 italiana (soma das 21 regiões) · **UNIT:** mil hectares
**REFERENCE_PERIOD:** anos 2010–2024 · **PUBLICATION_DATE / atualização da fonte:** `2026-05-28T23:00:00+0200` · **CAPTURED_AT:** 2026-08-28

| Ano | Área de milho grão na Itália (soma NUTS2) |
|---|---|
| 2019 | 628,8 mil ha |
| 2020 | 602,9 mil ha |
| 2021 | 588,6 mil ha |
| 2022 | 563,7 mil ha |
| 2023 | 498,5 mil ha |
| **2024** | **495,4 mil ha** |

- **Concentração territorial 2024:** Veneto 122,91 + Lombardia 115,82 + Piemonte 115,75 = **354,48 mil ha, ou 71,6% da área italiana** (cálculo do Sintonia sobre as linhas do arquivo).
- **A série do Eurostat para no ano 2024.** Não há 2025 nem 2026 aqui.
- **Buraco declarado:** 2014 só traz 15 das 21 regiões e 2012 traz 20 — esses dois anos **não são somáveis** com os demais. Não os usei.
- **O Eurostat NUTS2 não tem rendimento.** Literal do arquivo: *"apenas FR/ES/IT, nivel NUTS2. Rendimento (YLD) NAO existe em NUTS2 — so pais."* O arquivo de rendimento por país que existe no acervo (`EU-T1-002`) é de **trigo comum** (`C1110`), não de milho. **Rendimento de milho pelo Eurostat: NÃO SEI — não coletado nesta rodada.**

### 2.2 Área, rendimento e produção 2025 — ISMEA (lido, mas via Internet Archive)

**SOURCE:** ISMEA — comunicado *AgriMercati* 1/2026, *"LA CONGIUNTURA AGROALIMENTARE DEL 3 TRIMESTRE 2025"*
**PUBLICATION_DATE:** 22 de janeiro de 2026 (*"Roma, 22 gennaio 2026"*) · **REFERENCE_PERIOD:** safra 2025; preço de setembro/2025
**GEOGRAPHY:** Itália · **ESTADO DA FONTE:** ⚠️ **NÃO ALCANÇADA AO VIVO** — lida em snapshot do Internet Archive

Citação literal:

> *"mais Italia con superficie a circa 541 mila ettari (+9,2%), rese 10,2 t/ha (+2,5%), produzione 5,5 milioni di tonnellate (+11,9%), prezzo 238,56 euro/ton a settembre 2025 e +6,1% rispetto a settembre 2024 (224,88 euro/ton)"*

| Indicador | Valor 2025 | Variação declarada | UNIT |
|---|---|---|---|
| Superfície | ~541 mil | +9,2% | hectares |
| Rendimento | 10,2 | +2,5% | t/ha |
| Produção | 5,5 | +11,9% | milhões de toneladas |
| Preço set/2025 | 238,56 | +6,1% vs set/2024 (224,88) | EUR/t |

**Verificação de coerência (cálculo do Sintonia, não da fonte):** 495,4 mil ha (Eurostat 2024) × 1,092 = **541,0 mil ha**. Os dois números batem — o "+9,2%" do ISMEA está medido contra uma base igual à soma NUTS2 do Eurostat de 2024. Isso reforça a leitura de que **2025 interrompeu cinco anos seguidos de encolhimento de área**.

**Três ressalvas que não podem cair:**
1. **O preço do ISMEA e o preço do Portal da UE não são o mesmo número.** ISMEA: 238,56 €/t em set/2025, subindo 6,1% no ano. Portal UE: média nacional 243,39 €/t na semana de 27/07–02/08/2026, caindo 5,92% no ano. **Períodos diferentes e definições diferentes de preço — colocá-los na mesma linha do tempo seria erro.**
2. **Superfície e produção não são medição própria do ISMEA.** A própria seção declara: *"In questa sezione pubblichiamo i dati di fonte Istat (http://dati.istat.it/) o di altra fonte ufficiale"*. Para área e produção, a fonte primária é o **ISTAT**; o ISMEA reempacota. **O ISTAT não foi alcançado diretamente nesta rodada.**
3. **Não há dado de safra 2026.** Nem Eurostat (para em 2024), nem ISMEA (para em 2025). Área, rendimento e produção do milho italiano em 2026: **NÃO SEI.**

### 2.3 JRC MARS

**NÃO ALCANÇADO nesta rodada.** Não há arquivo do JRC MARS no repositório e a fonte não foi lida. Não é fonte vazia — é fonte não alcançada. Sem boletim MARS, **não tenho previsão de rendimento do milho italiano para 2026 de origem agrometeorológica**.

---

## 3. OFERTA E COMÉRCIO

**NOT AVAILABLE** para o milho italiano nesta rodada.

O que consegui provar é que a **capacidade existe** na ISMEA, mas **nenhum número de milho foi lido**:

- **Bilanci di approvvigionamento** (balanço de abastecimento) — cadência **anual**, *"ultimo aggiornamento: gennaio 2026"*, com série dos últimos 5 anos, e **"Cereali" está entre as culturas cobertas**. Rota: HTML + *"Scarica il file Excel con i dati (204.14 KB)"*. **O Excel não foi baixado — o host da ISMEA está bloqueado por geografia de IP.** Tenho a estrutura e o escopo, não os números. A fórmula publicada é *"Autoapprovvigionamento = produzione / consumo (autosufficienza se >100)"*.
- **Commercio estero agroalimentare** — banco de dados interativo, só por navegador. **Nenhum valor de importação ou exportação de milho lido.** A própria fonte avisa: *"Il totale Agroalimentare e ottenuto dalla aggregazione di voci doganali a 8 digit (NC8) e non comprende i dati soggetti a segreto statistico"*.
- O corte publicado da ISMEA é por **categoria "Cereali"**, não por cultura individual; descer até milho exige o banco interativo, que está atrás do bloqueio.

**Por que a ISMEA não foi alcançada (prova):** quatro rotas independentes falharam. `https://www.ismea.it/` devolveu HTTP 404 com página de WAF cujo texto traz **"GEO_IP_BLOCK"**, IP de origem `179.172.231.127` e assinatura *"Barracuda Networks, Inc."*; a **mesma** página "Blocked" apareceu em **janela gráfica de Chrome real** (event ID `1a0606e9f9c-17bcb58c`) — ou seja, **não é detecção de headless, é bloqueio por geografia**; `https://www.ismeamercati.it/` deu HTTP 000 com *"Failed to connect ... after 21040 ms"*; e o catálogo nacional italiano de dados abertos respondeu HTTP 200 com **`{"count": 0}`** para a busca "ismea".

**Consequência declarada:** **importação de milho subindo, se um dia for lida, não é demanda subindo.** A Itália é importadora estrutural de milho, e um número de importação maior pode significar quebra de safra local, arbitragem de preço, reexportação ou formação de estoque da indústria de ração — cada uma dessas leva a uma conclusão comercial diferente. **Sem o número e sem o contexto, não há conclusão.**

---

## 4. CONFIANÇA DO PRODUTOR

**Nível em que a fonte publica: SETOR, não cultura.** O setor que contém o milho chama-se **"Cereali"**.

- **Métrica:** ICF — *Indice ISMEA del clima di fiducia*, setor **AGRICOLTURA**, recorte **Cereali**
- **Cadência:** trimestral · **GEOGRAPHY:** Itália
- **Último relatório que consegui datar:** *"La congiuntura Agricola - IV trimestre 2025"*, publicado em **29/01/2026** (calendário lido em snapshot de 23/04/2026)
- **VALOR CORRENTE: NÃO SEI.** Não li nenhum número. O valor **não está no HTML** — mora em 6 arquivos XML de gráfico FusionCharts em `/flex/tmp/FlexFCharts/...`, e **os 6 dão HTTP 404 no Internet Archive**.
- Se a ISMEA manteve o ritmo trimestral, o I e o II trimestre de 2026 já saíram até hoje (02/09/2026). **Isso eu não sei** — não há snapshot posterior a abril/2026 dessa lista.

**Duas armadilhas de leitura que precisam ficar registradas:**

1. **A escala do ICF vai de −100 a +100 e NÃO é percentual.** A imprensa italiana já publicou "indice Ismea a −1,4%" com sinal de porcentagem indevido. Se algum dia esse número entrar na ferramenta, entra sem o símbolo de %.
2. **⚠️ "Cereali" é um setor, não é milho.** Confiança de CEREAIS não vale como confiança de MILHO, nem de trigo duro. O ICF agrega culturas com calendários, preços e riscos diferentes dentro do mesmo balde. **Publicar "a confiança do produtor de milho está em X" com base no ICF Cereali seria inventar um recorte que a fonte não publica.**

**Componentes separadas (condição corrente vs expectativa):** a fonte declara que o índice sintetiza duas coisas — *"l'andamento corrente degli affari della loro azienda"* e *"le attese sull'evoluzione economica della stessa nei prossimi 2-3 anni"* — mas a página de dados publica **só o valor único**. Não consegui ver as duas componentes separadas, nem a variação contra o trimestre anterior. Se o PDF trimestral as abre: **NÃO SEI**.

---

## 5. PRESSÃO DE CUSTO

**NÃO SEI — nenhum valor de custo de insumo foi lido nesta rodada.** Isto é fonte não alcançada, não fonte vazia.

O que sei sobre a rota, com as limitações declaradas:

| Item | Situação |
|---|---|
| **ISMEA — Indice dei prezzi dei mezzi correnti di produzione** (custo de insumos) | Existe. Cadência **mensal**, Itália. Mas a série baixável **parava em 2024** no snapshot de abril/2026 — mais de **um ano de defasagem** contra o índice de preços, que é mensal. E a página dedicada `/dati-agroalimentare/indice-costi` aparecia como *"Pagina non piu disponibile"* no snapshot de 18/11/2025. **Nenhum valor lido.** |
| **Rubrica separada para fitossanitários** dentro das *voci di spesa* | **NÃO SEI.** Não consegui abrir o arquivo da série. |
| **Fertilizante — índice ou preço, Itália** | **NÃO ALCANÇADO nesta rodada.** Nenhuma fonte de fertilizante foi lida. |
| **Energia — índice ou preço, Itália** | **NÃO ALCANÇADO nesta rodada.** Nenhuma fonte de energia foi lida. |
| **Recorte de custo por cultura (milho)** | **Não existe no corte publicado.** A fonte quebra por produto e por rubrica de gasto, **não por cultura**. |

**A consequência é dura e precisa ser dita:** sem índice de custo, **não é possível afirmar nada sobre a margem do produtor italiano de milho**. Preço de milho caindo ~6% no ano **não é**, sozinho, "produtor perdendo dinheiro" — se o custo caiu mais, a margem pode até ter melhorado; se o custo subiu, piorou muito mais que 6%. **Preço de cultura não é lucro de produtor.** Com metade da conta faltando, a conta não fecha, e a ficha não fecha.

---

## 6. OUTLOOK (projeção — separado do estado corrente)

**Para o milho italiano: NOT AVAILABLE nesta rodada.**

Nenhuma das três fontes que alcancei publica projeção de milho:

- **EU Agri-food Data Portal** — é observação de preço semanal, olha para trás. Não projeta.
- **Eurostat `apro_cpshr`** — série histórica de área, para em 2024. Não projeta.
- **ISMEA / AgriMercati 1/2026** — os números de milho que li (541 mil ha, 10,2 t/ha, 5,5 Mt) são **safra 2025 fechada**, publicados em 22/01/2026. **São estado passado, não projeção.**

**As rotas que produziriam um outlook e que NÃO foram alcançadas:**
- **JRC MARS Bulletin** — previsão de rendimento agrometeorológica por país e cultura. Não lido.
- **ISMEA Tendenze / Schede di settore, comparto Cereali** — a cadência **não é regular**. A própria lista da série *Tendenze* mostra buracos de mais de um ano (no comparto Ortaggi: 21/12/2021, 21/12/2022, 10/01/2024, 19/02/2025, março/2026 — **nenhum número em 2023**). Um comparto pode ficar mais de um ano sem relatório. **A ferramenta não pode prometer atualização trimestral por cultura.**

**Nada nesta ficha deve ser lido como projeção.** Se um número aparecer rotulado como outlook de milho italiano em outra parte do material, ele não veio daqui.

---

## 7. TEMPERATURA DE MERCADO

# PRESSURED

> ⚠️ **ISTO É INTERPRETAÇÃO DO SINTONIA, NÃO É FATO OBSERVADO.**
> Nenhuma fonte publica "temperatura de mercado". A palavra acima é uma leitura montada por mim a partir dos componentes abaixo. Os números são da fonte; a palavra é minha.

### « POR QUE »

| Componente | Seta | O que sustenta | Lastro |
|---|---|---|---|
| **Preço vs ano anterior** | ↓↓ | **9 de 9 praças comparáveis caíram**, de −1,73% (Roma) a −7,66% (Alessandria). Média nacional **−5,92%** (€243,39 vs €258,70 em 03/08/2025) | EU Agri-food, semana 27/07–02/08/2026 |
| **Preço vs período anterior** | → | **8 das 10 praças com 0,00%.** Só Udine (+0,84%) e a média nacional (+1,04%) se mexeram | EU Agri-food, mesma semana |
| **Oferta doméstica (última safra fechada)** | ↑↑ | Produção 2025 **+11,9%**, área **+9,2%**, rendimento **+2,5%** — *"produzione 5,5 milioni di tonnellate (+11,9%)"* | ISMEA AgriMercati, publ. 22/01/2026, ref. safra 2025 |
| **Tendência de área de longo prazo** | ↓ (revertida em 2025) | 628,8 → 495,4 mil ha entre 2019 e 2024, **cinco quedas seguidas**; 2025 volta a ~541 mil ha | Eurostat `apro_cpshr` + ISMEA |
| **Custo de insumo (fertilizante, energia, fitossanitário)** | **? DESCONHECIDO** | Série ISMEA para em 2024; página do índice fora do ar; nenhuma fonte de fertilizante ou energia alcançada | seção 5 |
| **Confiança do produtor** | **? DESCONHECIDO** | ICF existe, mas o valor está em XML de gráfico que dá 404. E o recorte publicado é **Cereais**, não milho | seção 4 |
| **Oferta e comércio (import/export)** | **? DESCONHECIDO** | Host da ISMEA bloqueado por GEO_IP_BLOCK; nenhum número de milho lido | seção 3 |
| **Safra 2026** | **? DESCONHECIDO** | Eurostat para em 2024, ISMEA para em 2025, JRC MARS não alcançado | seção 2 |

**O raciocínio, inteiro:** o preço do milho está **abaixo do ano passado em todas as praças que permitem a comparação**, e essa queda vem **depois de uma safra doméstica 11,9% maior**. Mais oferta local com preço menor é a definição de mercado sob pressão de preço. Por isso **PRESSURED**.

**O que enfraquece essa leitura, e precisa aparecer junto:**
- A semana mais recente está **parada, não caindo** — 8 praças em 0,00% e a média nacional levemente **positiva** (+1,04%). A pressão está no eixo anual, **não** na última semana.
- **Três dos oito componentes estão em branco** (custo, confiança, comércio) e um quarto (safra 2026) não existe em lugar nenhum que eu tenha alcançado. **PRESSURED é uma leitura de dois eixos — preço e produção — não dos oito.**
- **Pressão de preço não é pressão de margem.** Sem o índice de custo, não sei se o produtor está espremido ou não.

---

## 8. O QUE ISTO NÃO AUTORIZA A DIZER

**Sobre a ADAMA — nada. Literalmente nada.**
- ❌ Não autoriza prever venda, volume, faturamento ou share da ADAMA na Itália.
- ❌ Não autoriza falar de estoque de distribuidor, sell-in, sell-out ou intenção de compra de quem quer que seja.
- ❌ Não autoriza dizer que o produtor "vai comprar" ou "vai deixar de comprar" defensivo. **Preço de grão não é decisão de compra de insumo.** A cadeia entre um e outro tem custo, crédito, calendário, pressão de praga e agronomia no meio — e nada disso está medido aqui.
- A própria fonte de preço diz, literal: *"nao e preco pago pela ADAMA nem por ninguem em particular"*.

**Sobre o número em si:**
- ❌ Não autoriza somar ou comparar praças sem olhar o `STAGE`. Roma (departure from farm, €284,00) e Perugia (farm gate, €216,10) medem pontos diferentes da cadeia; a diferença de €67,90 **não é só diferença regional**.
- ❌ Não autoriza tratar **Nápoles** como preço corrente. A série parou em maio de 2026. Usar €221,00 como "preço de hoje em Nápoles" seria apresentar um dado de 4 meses atrás como fresco.
- ❌ Não autoriza colar o preço do ISMEA (238,56 €/t, set/2025) na mesma série do Portal da UE (243,39 €/t, ago/2026). Definições e cadências diferentes.
- ❌ Não autoriza transformar dado **anual** (área Eurostat), **de safra** (produção ISMEA) e **semanal** (preço UE) em uma única linha do tempo. **Cada número carrega a cadência da fonte que o produziu.**

**Sobre a confiança e o setor:**
- ❌ Não autoriza dizer "a confiança do produtor de milho italiano está em X". O ICF é **setorial (Cereali)** e, além disso, **nenhum valor foi lido**. São duas negações empilhadas.

**Sobre margem e lucro:**
- ❌ Não autoriza dizer que o produtor italiano de milho está perdendo dinheiro, nem ganhando. **Preço alto ou baixo de cultura não é lucro do produtor** — o custo de insumo entra na conta, e essa metade da conta está em branco (seção 5).

**Sobre comércio:**
- ❌ Não autoriza nenhuma leitura de importação. Não há número. E, se houver um dia, **importação subindo não é demanda subindo**: pode ser quebra de safra local, arbitragem de preço, reexportação ou estoque da indústria.

**Sobre o futuro:**
- ❌ Não autoriza nenhuma projeção de safra, preço ou rendimento para 2026. **Não há dado de 2026 sobre a lavoura em nenhuma das fontes alcançadas.**

**Sobre a própria ficha:**
- ⚠️ Três das quatro fontes citadas têm defeito declarado: a **ISMEA não foi alcançada ao vivo** (bloqueio GEO_IP_BLOCK; tudo veio do Internet Archive, congelado na data do snapshot), o **Eurostat para em 2024**, e o **JRC MARS e o ISTAT não foram alcançados**. Só o **EU Agri-food Data Portal** entregou dado corrente e completo. Uma ficha que ficasse só nele teria preço e mais nada.

---

**Arquivos lidos para montar esta ficha (caminhos absolutos):**
- `C:\eame-sintonia\data\samples\IT-MERCADO\EU-AGRIFOOD-cereal-prices-IT.json` — 16.193 registros, 40 pares; 11 de milho
- `C:\eame-sintonia\data\samples\EU-T1-001-nuts2-crop-area.json` — Eurostat `apro_cpshr`, 5.685 linhas, crop `C1500` para as 21 regiões NUTS2 italianas
- Ficha ISMEA da rodada (via Internet Archive) — usada para safra 2025, ICF e índice de custo

**Arquivos disponíveis e NÃO usados, com motivo:**
- `C:\eame-sintonia\data\samples\IT-MERCADO\EU-AGRIFOOD-oliveOil-prices-IT.json` — azeite, outra cultura
- `C:\eame-sintonia\data\samples\IT-MERCADO\EU-AGRIFOOD-wine-prices-IT.json` — vinho, outra cultura
- `C:\eame-sintonia\data\samples\EU-T1-002-wheat-yield-country.json` — rendimento de **trigo comum** (`C1110`); **não tem milho**