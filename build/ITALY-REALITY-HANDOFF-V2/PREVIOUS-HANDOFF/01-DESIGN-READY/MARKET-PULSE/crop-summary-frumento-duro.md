MARKET PULSE — **FRUMENTO DURO (trigo duro) · ITÁLIA**
Fechado em 02/09/2026. Cada número traz fonte, período, data de publicação, geografia e unidade. Onde a fonte não foi alcançada está escrito NÃO ALCANÇADO — que não é o mesmo que "não existe".

---

## 1. ESTADO CORRENTE — preço por praça

**Camada semanal — a mais fina que consegui.**

`SOURCE`: European Commission — Agri-food Data Portal, API de preços de cereais (`SOURCE_ID` EU-T10-002).
`RESOLVED_URL`: `https://api.tech.ec.europa.eu/agrifood/api/cereal/prices?memberStateCodes=IT&years=2025,2026`
`GEOGRAPHY`: praça nomeada dentro da Itália · `UNIT`: EUR por TONELADA · `PRODUCT`: `DUR|UNKNOWN` e `Durum wheat`
`REFERENCE_PERIOD`: semana de **03/08/2026 a 09/08/2026** (média nacional: 27/07 a 02/08/2026)
`PUBLICATION_DATE`: o arquivo carimba **13/08/2026** (média nacional: 06/08/2026) — o campo se chama `REFERENCE_PERIOD` no arquivo mas o valor cai 4 dias **depois** do fim da semana medida; leio como a data em que a observação foi carimbada. **NÃO SEI** se é a data de publicação oficial.
`CAPTURED_AT`: 2026-09-02 · arquivo: `C:\eame-sintonia\data\samples\IT-MERCADO\EU-AGRIFOOD-cereal-prices-IT.json`

| Praça | Preço | vs semana anterior | vs ano anterior (semana encerrada 03/08/2025) | Estágio comercial declarado pela fonte |
|---|---|---|---|---|
| **Roma** | € 302,50 /t | 0,0 % (era € 302,50) | **+13,1 %** (era € 267,50) | *Departure from farm or from production area — on truck or other transport means* |
| **Grosseto** | € 302,50 /t | 0,0 % (era € 302,50) | −3,5 % (era € 313,33) | *Price at farm gate* |
| **Bologna** | € 257,50 /t | 0,0 % (era € 257,50) | −10,7 % (era € 288,50) | *Deliver to first customer — silo or processing plant* |
| **Milano** | € 257,50 /t | 0,0 % (era € 257,50) | −15,7 % (era € 305,50) | *Deliver to first customer — silo or processing plant* |
| **Foggia** | € 255,50 /t | 0,0 % (era € 255,50) | −12,6 % (era € 292,50) | *Price at farm gate* |
| **Napoli** | € 255,50 /t | 0,0 % (era € 255,50) | −16,9 % (era € 307,50) | *Deliver to first customer — silo or processing plant* |
| **Média Nacional** | € 271,83 /t | 0,0 % (era € 271,83) | **−8,1 %** (era € 295,81) | *National Average — Not Specified* |
| ⛔ **Catania** | € 540,00 /t | −1,8 % (era € 550,00) | sem valor de referência no arquivo | *Departure from farm or from production area* |

### ⛔ Praça com série PARADA
**Catania parou em 2022.** A observação mais recente é a semana de **11/07/2022 a 17/07/2022**, carimbada 21/07/2022, com 185 observações na série. O valor de € 540,00/t **é de 2022 e não pode ser lido como preço de hoje** — nem entrar em média, nem em amplitude, nem em comparação.

### Três coisas que a série mostra e que precisam ser ditas
1. **Semana travada.** As seis praças vivas e a média nacional registram **variação zero** contra a observação anterior. No mesmo arquivo, outras culturas se moveram na mesma janela (trigo mole em Perugia +8,00 €/t; em Verona +10,00 €/t). Ou seja: a imobilidade do duro **não** é um defeito do arquivo. Se é preço genuinamente estável ou repetição de cotação anterior pela praça — **NÃO SEI**.
2. **Uma praça anda contra as outras.** Roma sobe +13,1 % no ano enquanto as outras cinco caem entre −3,5 % e −16,9 %. Não sei explicar. Roma cota em estágio *"Departure from farm"*, que é diferente de Grosseto e Foggia (*farm gate*) e de Bologna/Milano/Napoli (*deliver to first customer*).
3. **Comparar praça com praça exige cuidado.** O próprio arquivo avisa, literalmente: *"nao e o mesmo estagio comercial entre pracas — ver STAGE"* e *"comparar pracas diferentes exige conferir STAGE e UNIT antes"*. Existem **três estágios diferentes** entre as seis praças vivas. A distância de € 47,00/t entre a mais baixa (€ 255,50) e a mais alta (€ 302,50) **mistura diferença de mercado com diferença de ponto de entrega** — não é dispersão de mercado limpa.

### Idade do dado
O número mais fresco de trigo duro é da semana encerrada em **09/08/2026** — **24 dias** antes desta leitura. No mesmo arquivo há trigo mole e milho com semanas até **23/08/2026**. O duro está **duas semanas atrás** das culturas mais frescas do mesmo arquivo. Por quê — **NÃO SEI**.

### Camada trimestral — índice de preço do trigo duro (cadência diferente, não misturar)
`SOURCE`: Eurostat `apri_pi_outq` — *"Price indices of agricultural products, output — quarterly data"*, item `AM011200` *"Durum wheat"*
`GEOGRAPHY`: Itália (país) · `UNIT`: número índice, base 2020 = 100 · `REFERENCE_PERIOD`: 2026-Q1 (jan–mar/2026) · `PUBLICATION_DATE`: atualizado pela fonte em **30/07/2026**
arquivo: `C:\eame-sintonia\data\samples\IT-MERCADO\EUROSTAT-apri_pi_outq-output-price-index-IT.json`

| Trimestre | Índice nominal | vs mesmo trimestre do ano anterior | Índice real |
|---|---|---|---|
| 2025-Q1 | 118,7 | −7,55 % | 99,36 |
| 2025-Q2 | 114,4 | −8,04 % | 94,37 |
| 2025-Q3 | 108,8 | −10,38 % | 90,23 |
| 2025-Q4 | 107,1 | −9,08 % | 88,37 |
| **2026-Q1** | **105,8** | **−10,87 %** | **87,36** (−12,08 %) |

Cinco trimestres seguidos de queda no ano contra ano. O índice real está em 87,36 — abaixo de 100, que é o nível de 2020. **Qual deflator o Eurostat usa para o "Real index" eu não li** — reporto o rótulo da fonte, não o método.

---

## 2. PRODUÇÃO E RENDIMENTO

`SOURCE`: European Commission — Agri-food Data Portal, API `cereal/production` (rota descoberta e testada nesta rodada: HTTP 200)
`RESOLVED_URL`: `https://api.tech.ec.europa.eu/agrifood/api/cereal/production?memberStateCodes=IT&years=2020…2026`
`GEOGRAPHY`: Itália (país) · `CAPTURED_AT`: 2026-09-02
arquivo: `C:\eame-sintonia\data\samples\IT-MERCADO\EU-AGRIFOOD-cereal-production-IT.json`

| Ano (`REFERENCE_PERIOD`) | Produção (mil t) | Área (mil ha) | Rendimento (t/ha) |
|---|---|---|---|
| 2020 | 3.885,22 | 1.210,42 | 3,21 |
| 2021 | 4.065,01 | 1.228,50 | 3,31 |
| 2022 | 3.690,03 | 1.237,96 | 2,98 |
| 2023 | 3.688,05 | **1.269,29** ← pico | 2,91 |
| 2024 | 3.500,08 | 1.177,44 | 2,97 |
| 2025 | 3.618,25 | 1.134,23 | 3,19 |
| **2026** | **3.588,31** | **1.131,96** ← mínimo da série | **3,17** |

- **2026 vs 2025**: produção **−0,83 %**, área **−0,20 %**, rendimento **−0,63 %**.
- **2026 vs média 2021-2025**: produção **−3,34 %**, área **−6,41 %**, rendimento **+3,19 %**. Lido em palavras: colhe-se **menos grão em menos terra, com a terra rendendo um pouco mais que a média recente**.
- **Área caiu 137,33 mil hectares desde 2023 (−10,8 % em três anos)**, sem uma única alta no caminho.

**Unidade: a API não declara.** Inferi por dois caminhos independentes, e digo os dois porque a inferência é minha, não da fonte:
(a) aritmética interna — produção ÷ área devolve exatamente o campo `yield` (3.618,25 ÷ 1.134,23 = 3,190 = *yield* 3,19);
(b) triangulação com a ISMEA, que para o **milho** de 2025 publica literalmente *"superficie a circa 541 mila ettari (+9,2%), rese 10,2 t/ha (+2,5%), produzione 5,5 milioni di tonnellate (+11,9%)"* — a API devolve 540,95 / 10,19 / 5.511,12 para o mesmo ano e cultura.

**Convergência ISMEA × Comissão para o trigo duro de 2025.** ISMEA, comunicado AgriMercati 1/2026 de **22/01/2026**: *"Cereali - Frumento duro Italia a circa 3,6 milioni di tonnellate (+3,4%), grazie all'aumento delle rese e a un andamento climatico piu favorevole, con un profilo qualitativo complessivamente buono"*. A API devolve 3.618,25 mil t para 2025 e 3.500,08 para 2024 — **+3,38 %**. Dois caminhos, mesmo número.

**O ano de 2026 é definitivo ou estimativa? NÃO SEI.** A API não traz campo de status. O que sei é que 2026 é o último ano com dado: pedindo `years=2027`, a resposta é 404 com a mensagem literal *"No results found for the selected parameter(s)"* — isso é **vazio de dados**, e é diferente do outro 404 que aparece na seção 3.

### ISTAT, Eurostat e JRC MARS — estado de cada um
- **ISTAT** — `NÃO ALCANÇADO NESTA RODADA`. Nenhum byte lido de servidor do ISTAT. A ISMEA declara na própria página que, para superfície e produção, *"In questa sezione pubblichiamo i dati di fonte Istat (http://dati.istat.it/) o di altra fonte ufficiale"* — ou seja, a ISMEA é reempacotadora. Se a Comissão puxa da mesma origem, é plausível, mas **não verifiquei a cadeia** e não afirmo.
- **Eurostat, rendimento** — o acervo tem `EU-T1-002-wheat-yield-country.json` com rendimento italiano até 2025 (5,02 t/ha), **mas a cultura é `C1110` "Common wheat and spelt"**. Isso é **trigo mole, não trigo duro**. Não usei e não deve ser usado aqui.
- **Eurostat, área NUTS2** — `EU-T1-001-nuts2-crop-area.json` cobre só `C1110`, `C1300`, `C1500`, `R2000`. **Não há trigo duro no que foi coletado.** O código `C1120` existe no Eurostat; simplesmente não foi baixado nesta rodada.
- **JRC MARS** — `NÃO ALCANÇADO`. Nenhum arquivo do MARS no acervo, nenhuma rota tentada nesta rodada. Isso é ausência de coleta, não ausência de fonte.

### O que esta seção NÃO diz
Área colhida **não é** área tratada com defensivo. Rendimento médio nacional **não é** o rendimento de nenhuma lavoura. Queda de área **não é** queda de demanda de insumo — pode ser rotação, preço relativo de outra cultura, ou decisão de política agrícola. Nenhuma dessas três foi medida.

---

## 3. OFERTA E COMÉRCIO

**NOT AVAILABLE — para o trigo duro italiano, nesta rodada.**

Não é que não exista. É que nenhuma das rotas chegou lá. Registro cada uma:

| Rota | Estado | Evidência literal |
|---|---|---|
| API da Comissão — comércio/balanço de cereais | **ROTA NÃO PUBLICADA** | 13 caminhos testados (`/trade`, `/trades`, `/tradeData`, `/imports`, `/exports`, `/tradeflow`, `/balance`, `/balanceSheet`, `/balanceSheets`, `/balanceSheetData`, `/supplyBalance`, `/productions`, `/marketPrices`). Todos devolvem HTTP 404 com 128 bytes e a mensagem *"No matching resource found for given API Request"* — o gateway dizendo **este caminho não existe**, que é diferente de *"No results found for the selected parameter(s)"*, a mensagem de dado vazio |
| ISMEA — *Commercio estero agroalimentare* | **BLOQUEADO** | host da ISMEA responde página de WAF com o texto literal `GEO_IP_BLOCK`, inclusive em janela gráfica de Chrome real. Não é detecção de robô: é bloqueio por geografia de IP |
| ISMEA — *Bilanci di approvvigionamento* | **EXISTE, NÃO LIDO** | a estrutura foi lida em snapshot do Internet Archive de 10/05/2026, *"ultimo aggiornamento: gennaio 2026"*. O Excel de 204,14 KB não foi baixado porque o host está bloqueado. E o recorte é **"Cereali"**, setor — **não** trigo duro |
| Estoques / *giacenze* de trigo duro | **NÃO SEI** | nenhuma fonte de estoque de trigo duro italiano foi alcançada nesta rodada |

**Lei 5, dita antes de alguém precisar.** Se em alguma rodada futura aparecer importação italiana de trigo duro subindo, isso **não** é demanda subindo. Pode ser quebra de safra local, arbitragem de preço, reexportação, ou a indústria de massas montando estoque. São quatro leituras diferentes e o número sozinho não separa nenhuma.

---

## 4. CONFIANÇA DO PRODUTOR

**Nível setorial. O setor é `CEREALI` — e CEREAIS não é TRIGO DURO.**

`SOURCE`: ISMEA — *Indice Ismea del clima di fiducia*, setor Agricoltura
`GEOGRAPHY`: Itália · `UNIT`: número índice de **−100 a +100** · `CADÊNCIA`: trimestral
`REFERENCE_PERIOD` do último relatório que consegui datar: **IV trimestre de 2025** · `PUBLICATION_DATE`: **29/01/2026**

**VALOR: NÃO LIDO.** O número não está no HTML da página. Ele mora em 6 arquivos XML de gráfico (FusionCharts) em `/flex/tmp/FlexFCharts/…`, e **todos os 6 devolvem 404 no Internet Archive**. O host vivo da ISMEA está bloqueado por `GEO_IP_BLOCK`.

O que consigo afirmar, então, é só isto: **existe um índice trimestral de confiança para o setor Cereali, o último relatório que datei é do IV trimestre de 2025 publicado em 29/01/2026, e eu não li o valor.** Se saíram os trimestres I e II de 2026 até hoje — **NÃO SEI**; não há snapshot da lista posterior a abril/2026.

**Duas armadilhas registradas para quem for ler esse índice depois:**
1. A escala é de −100 a +100 e **não é percentual**. A imprensa italiana já publicou "indice Ismea a −1,4%" com sinal de porcentagem que não existe ali.
2. **"Cereali" é um setor.** A confiança do setor cereais não é a confiança de quem planta trigo duro, nem de quem planta milho. São culturas com preço, calendário e comprador diferentes dentro do mesmo balde.

---

## 5. PRESSÃO DE CUSTO

`SOURCE`: Eurostat `apri_pi_inq` — *"Price indices of the means of agricultural production, input — quarterly data"*
`GEOGRAPHY`: Itália (país) · `UNIT`: número índice, **base 2020 = 100**, nominal · `REFERENCE_PERIOD`: **2026-Q1 (jan–mar/2026)** · `PUBLICATION_DATE`: atualizado pela fonte em **11/08/2026**
arquivo: `C:\eame-sintonia\data\samples\IT-MERCADO\EUROSTAT-apri_pi_inq-input-price-index-IT.json`

| Rubrica (rótulo literal da fonte) | 2025-Q1 | 2026-Q1 | vs mesmo trimestre do ano anterior |
|---|---|---|---|
| *Goods and services currently consumed in agriculture (Input 1)* | 130,9 | **132,7** | **+1,38 %** |
| *Fertilisers and soil improvers* | 144,4 | **155,4** | **+7,62 %** |
| *Nitrogenous fertilisers* | 150,6 | **168,4** | **+11,82 %** |
| *Energy; lubricants* | 159,3 | **156,8** | **−1,57 %** |
| — *Motor fuels* | 145,3 | 155,7 | **+7,16 %** |
| — *Electricity* | 184,6 | 164,1 | **−11,11 %** |
| *Plant protection products* | 124,4 | **125,5** | **+0,88 %** |
| — *Fungicides and bactericides* | 134,8 | 138,4 | **+2,67 %** |
| — *Herbicides, haulm destructors and moss killers* | 118,4 | 117,0 | **−1,18 %** |
| *Seeds and planting stock* | 141,6 | 146,3 | **+3,32 %** |

**Leitura em palavras.** O custo total do que a lavoura consome subiu pouco (+1,4 %), mas **a média esconde direções opostas dentro dela**: adubo nitrogenado subiu quase 12 %, combustível de máquina subiu 7 %, e energia elétrica caiu 11 %. Defensivo, no conjunto, ficou praticamente parado (+0,9 %), com fungicida subindo 2,7 % e herbicida caindo 1,2 %.

**A tesoura, no mesmo trimestre, na mesma base e no mesmo país.** Em 2026-Q1, o índice de preço do **trigo duro** está em **105,8** e o índice de **custo de insumo** está em **132,7** — ambos base 2020 = 100. Em 2020 os dois valiam 100. Hoje há **26,9 pontos de distância** entre eles. Em oito trimestres (2024-Q1 → 2026-Q1) o preço do duro caiu **−17,6 %** e o custo de insumo subiu **+1,5 %**.

**Lei 6, sem rodeio: isto não é margem, e não é lucro.** É um índice de preço de insumo no país inteiro contra um índice de preço de produto no país inteiro. Não é o orçamento de nenhuma fazenda. **Ninguém mediu o custo de produção de uma lavoura de trigo duro nesta rodada.** A tesoura mostra a direção das duas curvas; não mostra quanto sobra no bolso de ninguém.

**ISMEA, índice de custo — NÃO ALCANÇADO.** A ISMEA publica um *Indice dei prezzi dei mezzi correnti di produzione*, mas a página dedicada aparecia como *"Pagina non piu disponibile"* no snapshot de 18/11/2025, e a série baixável parava em **2024** no snapshot de abril/2026. E **NÃO SEI** se existe rubrica separada para *"prodotti fitosanitari"* dentro das *voci di spesa* — não consegui abrir o arquivo.

**Cadência (Lei 2).** Estes números são **trimestrais** e o mais recente é de **janeiro a março de 2026** — cerca de seis meses atrás. Não podem ser lidos ao lado do preço semanal de agosto como se fossem do mesmo dia.

---

## 6. OUTLOOK — projeção

**NOT AVAILABLE NESTA RODADA.**

Nenhuma projeção de trigo duro italiano foi alcançada. Não há aqui previsão de safra futura, de preço futuro, nem de balanço futuro — de ninguém.

O que existe e ficou de fora, com o motivo:

| Rota candidata | Estado |
|---|---|
| ISMEA — *Tendenze* do comparto **Cereali** | `NÃO LIDO`. A seção existe (o menu do portal lista Cereali entre os compartos de *Tendenze*), o host está bloqueado por `GEO_IP_BLOCK`, e a cadência da própria coleção é irregular — a lista de *Tendenze Ortaggi*, por exemplo, mostra buracos: 21/12/2021, 21/12/2022, 10/01/2024, 19/02/2025, março/2026, **sem nenhum número em 2023** |
| ISMEA — *La congiuntura Agricola*, relatório trimestral em PDF | `NÃO LIDO`. O último que datei é do IV trimestre de 2025, publicado em 29/01/2026 |
| ISMEA — publicações mais recentes | O espelho vivo `assocarni.it` lista publicações ISMEA até **23-07-2026**. Se há AgriMercati ou Tendenze de cereais posterior a janeiro/2026 — **NÃO SEI**, não abri |
| Comissão Europeia — perspectivas de curto prazo | `NÃO TENTADO` nesta rodada |
| JRC MARS — boletim agrometeorológico de rendimento | `NÃO TENTADO` nesta rodada |

**A única incerteza para a frente que consegui isolar** é a da seção 2: **não sei se o número de 2026 da Comissão (3.588,31 mil t) é definitivo ou uma estimativa de campanha.** A API não rotula. A colheita do duro na Itália termina antes de setembro, o que torna plausível que já seja pós-colheita — mas plausível não é lastro, e eu não confirmei.

---

## 7. TEMPERATURA DE MERCADO

# PRESSURED

> ### ⚠️ Isto é INTERPRETAÇÃO DO SINTONIA, não fato observado.
> A palavra acima **não** está escrita em nenhuma fonte. Ela é a minha leitura de sete componentes medidos por terceiros. Os componentes são fato; a palavra é opinião derivada. Quem discordar da palavra pode discordar sem discordar de nenhum número.

### « POR QUE »

| Componente | Seta | O que foi medido | Cadência / período |
|---|---|---|---|
| Preço semanal vs semana anterior | **→** | 0,0 % em **todas** as 6 praças vivas e na média nacional | semanal · 03–09/08/2026 |
| Preço semanal vs ano anterior | **↓** | −8,1 % na média nacional; −3,5 % a −16,9 % em 5 das 6 praças | semanal · vs 03/08/2025 |
| Preço semanal — praça dissidente | **↑** | **Roma +13,1 %** no ano, sozinha contra as outras cinco | semanal · vs 03/08/2025 |
| Índice de preço do produto (duro) | **↓** | 105,8 nominal, −10,87 % no ano; real 87,36, −12,08 % — **5º trimestre seguido de queda** | trimestral · 2026-Q1 |
| Produção 2026 | **↓** | 3.588,31 mil t: −0,83 % vs 2025, −3,34 % vs média 2021-2025 | anual · 2026 |
| Área 2026 | **↓↓** | 1.131,96 mil ha: mínimo da série, −10,8 % contra 2023 | anual · 2026 |
| Rendimento 2026 | **↑** | 3,17 t/ha: −0,63 % vs 2025, mas **+3,19 % vs a média de 5 anos** | anual · 2026 |
| Custo total de insumo | **↑** | 132,7, +1,38 % no ano | trimestral · 2026-Q1 |
| Fertilizante nitrogenado | **↑↑** | 168,4, **+11,82 %** no ano | trimestral · 2026-Q1 |
| Defensivo (conjunto) | **→** | 125,5, +0,88 % no ano (fungicida +2,67 %; herbicida −1,18 %) | trimestral · 2026-Q1 |
| Energia | **↓** | 156,8, −1,57 % — mas puxada por eletricidade −11,11 % contra combustível +7,16 % | trimestral · 2026-Q1 |
| Confiança do produtor | **?** | **NÃO LIDO.** Existe só no nível do setor Cereali, e o valor está atrás de bloqueio | trimestral · último datado: IV trim 2025 |
| Oferta e comércio | **?** | **NÃO ALCANÇADO.** Rota da Comissão não publicada; ISMEA bloqueada | — |

**Por que PRESSURED e não outra palavra.** As setas que apontam para baixo são as do lado do que o produtor recebe — preço no ano, índice de preço do produto por cinco trimestres seguidos, área e produção. As que apontam para cima são as do lado do que ele paga — insumo total, e adubo nitrogenado com força. Preço caindo com custo subindo é aperto. Não escolhi **COOLING** porque a semana está travada, não esfriando. Não escolhi **VOLATILE** porque não há oscilação: há variação zero na semana. Não escolhi **MIXED SIGNALS** porque as duas discordâncias (Roma no preço, rendimento acima da média) são duas contra dez, e ambas com explicação possível não verificada — Roma cota em estágio comercial diferente das outras.

**Onde esta leitura é frágil, dito na cara:** a confiança do produtor não foi lida, o comércio não foi alcançado, e o número mais fresco de preço tem 24 dias. Se qualquer um dos três entrar, a palavra pode mudar.

---

## 8. O QUE ISTO NÃO AUTORIZA A DIZER

**Sobre venda, cliente e ADAMA — nada. Zero.**
- ❌ Não autoriza prever venda da ADAMA, share, giro de estoque de distribuidor ou intenção de compra de ninguém. **Nada disso foi medido.** Este documento não contém uma única observação sobre comportamento de compra.
- ❌ Não autoriza dizer "o produtor vai comprar mais fungicida porque o preço do trigo caiu", nem o contrário. A relação entre preço de grão e decisão de tratamento **não foi medida em lugar nenhum aqui**.
- ❌ Não autoriza dizer que a queda de 137 mil hectares de área desde 2023 significa mercado de defensivo menor. Área semeada não é área tratada, e nenhuma das duas foi cruzada com produto.

**Sobre o produtor e o dinheiro dele.**
- ❌ **A tesoura preço-custo não é margem.** São dois índices nacionais em base 2020 = 100. Ninguém mediu o custo de produção de uma lavoura de trigo duro. Preço baixo não prova prejuízo, assim como preço alto não prova lucro.
- ❌ Não autoriza dizer "o produtor italiano de trigo duro está descapitalizado", "sem caixa" ou "vai cortar insumo". Isso é inferência sobre comportamento, e não há dado de comportamento nesta ficha.

**Sobre confiança.**
- ❌ **Não autoriza atribuir nenhum número de confiança ao trigo duro.** O único índice de confiança que existe aqui é setorial (`Cereali`) — e mesmo esse **não foi lido**. Dizer "a confiança do produtor de trigo duro está em X" seria inventar duas coisas ao mesmo tempo: o valor e o recorte.

**Sobre geografia.**
- ❌ Não autoriza descer a região, província ou município. Produção, área, rendimento e todos os índices são **nacionais**. As únicas quebras sub-nacionais são as praças de preço — e elas são **pontos de cotação**, não territórios produtores. Foggia cotar € 255,50 não descreve a Puglia.
- ❌ Não autoriza tratar Catania como informação de hoje. Aquele € 540,00/t é de julho de **2022**.

**Sobre comparação entre praças.**
- ❌ Não autoriza dizer "Roma paga mais que Napoli". São três estágios comerciais diferentes na tabela. O próprio arquivo alerta: *"comparar pracas diferentes exige conferir STAGE e UNIT antes"*.

**Sobre o que não foi alcançado.**
- ❌ Não autoriza escrever "não existe dado de comércio de trigo duro italiano" ou "a ISMEA não publica confiança de cereais". O correto é: **a rota não foi alcançada**. A ISMEA bloqueia por IP (`GEO_IP_BLOCK`), e a rota de comércio da API da Comissão não está publicada nos 13 caminhos que testei. **Fonte não alcançada não é fonte vazia.**

**Sobre cadência.**
- ❌ Não autoriza colar preço semanal de agosto ao lado de índice trimestral de janeiro-março como se fossem a mesma foto. São três relógios diferentes nesta ficha — semanal, trimestral e anual — e cada número tem que carregar o seu.

**Proibido por regra, e nenhum foi usado:** nota de 0 a 100, "mercado quente", "os clientes vão comprar", qualquer previsão de venda.

---

### Arquivos e rotas usados

| Arquivo | Conteúdo |
|---|---|
| `C:\eame-sintonia\data\samples\IT-MERCADO\EU-AGRIFOOD-cereal-prices-IT.json` | preços semanais, 16.193 registros, 40 pares produto × praça (já existia) |
| `C:\eame-sintonia\data\samples\IT-MERCADO\EU-AGRIFOOD-cereal-production-IT.json` | **novo nesta rodada** — produção/área/rendimento IT 2020-2026, 63 linhas, com envelope de proveniência e a lista das 13 rotas que devolveram "rota não publicada" |
| `C:\eame-sintonia\data\samples\IT-MERCADO\EUROSTAT-apri_pi_inq-input-price-index-IT.json` | **novo nesta rodada** — índice trimestral de custo de insumo IT, 57 rubricas, 2024-Q1 a 2026-Q1 |
| `C:\eame-sintonia\data\samples\IT-MERCADO\EUROSTAT-apri_pi_outq-output-price-index-IT.json` | **novo nesta rodada** — índice trimestral de preço de produto IT, 116 itens incluindo `AM011200 Durum wheat` |

Custo desta rodada: **US$ 0,00** — todas as rotas novas são HTTP público sem chave.