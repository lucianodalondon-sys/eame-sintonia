# MARKET PULSE — VITE / VINO — ITÁLIA

**Montado em:** 02/09/2026 · **Geografia-mãe:** ITÁLIA (IT) · **Cultura:** uva para vinho (*uva da vino*) e vinho (*vino*)

**Aviso de leitura, antes de qualquer número:** a série de **preço de mercado por praça** da União Europeia para a Itália **está parada desde julho de 2025**. Tudo o que é "de agora" neste documento vem de outras três portas (Eurostat, Comext e ICQRF/MASAF), não do preço de praça. Onde a porta não abriu, está escrito **NÃO ALCANÇADA** — que não é o mesmo que **não existe**.

---

## 1. ESTADO CORRENTE — preço por praça

**SOURCE:** European Commission — Agri-food Data Portal, endpoint `wine/prices`
**RESOLVED_URL:** `https://api.tech.ec.europa.eu/agrifood/api/wine/prices?memberStateCodes=IT&years=2019...2026` (o host `www.ec.europa.eu` responde 302 para `api.tech.ec.europa.eu`)
**GEOGRAPHY:** praça nomeada dentro da Itália · **UNIT:** € / hectolitro (`"unit": "Euro / HL."`) · **REFERENCE_PERIOD:** semana 30/06/2025–06/07/2025 · **PUBLICATION_DATE:** a API não declara data de publicação; leitura feita em 02/09/2026 (HTTP 200, 45.990 bytes) · **RECORDS:** 775 observações, 10 pares produto × praça

| Praça / tipologia | Preço na última leitura (06/07/2025) | Observação anterior (04/05/2025) | Var. vs anterior | Um ano antes (07/07/2024) | Var. vs ano antes | Situação da série |
|---|---|---|---|---|---|---|
| **Verona** — Vino bianco DOP | € 100,00 /hl | € 100,00 | 0,0 % | € 90,00 | **+11,1 %** | PARADA em 2025 |
| **Lugo** — Vino rosso DOP | € 79,20 /hl | € 79,20 | 0,0 % | € 77,40 | +2,3 % | PARADA em 2025 |
| **Trapani** — Vino bianco s/ DOP-IGP | € 71,88 /hl | € 71,88 | 0,0 % | € 63,13 | **+13,9 %** | PARADA em 2025 |
| **Pescara** — Vino rosso s/ DOP-IGP | € 70,88 /hl | € 70,88 | 0,0 % | € 89,25 | **−20,6 %** | PARADA em 2025 |
| **Pescara** — Vino bianco s/ DOP-IGP | € 61,75 /hl | € 61,75 | 0,0 % | € 80,75 | **−23,5 %** | PARADA em 2025 |
| **Trapani** — Vino rosso s/ DOP-IGP | € 61,00 /hl | € 61,00 | 0,0 % | € 52,50 | **+16,2 %** | PARADA em 2025 |
| **Verona** — Vino rosso s/ DOP-IGP | € 53,50 /hl | € 55,00 | −2,7 % | € 47,80 | **+11,9 %** | PARADA em 2025 |
| **Lugo** — Vino bianco s/ DOP-IGP | € 53,40 /hl | € 54,50 | −2,0 % | € 55,00 | −2,9 % | PARADA em 2025 |
| **Bari** — Vino bianco s/ DOP-IGP | € 50,05 /hl | € 50,05 | 0,0 % | € 51,05 | −2,0 % | PARADA em 2025 |
| **Bari** — Vino rosso s/ DOP-IGP | € 43,70 /hl | € 43,70 | 0,0 % | € 39,43 | **+10,8 %** | PARADA em 2025 |

**AS 10 PRAÇAS ESTÃO PARADAS — todas na mesma data, 06/07/2025.** São 14 meses sem leitura nova até hoje (02/09/2026).

Três coisas que a série obriga a dizer, e que mudam a leitura:

1. **A cadência é MENSAL, não semanal.** O campo `weekNumber` engana. As datas de fim vêm espaçadas de 28 a 35 dias (`05/01/2025, 02/02/2025, 02/03/2025, 06/04/2025, 04/05/2025 …`). Tratar isso como preço semanal seria fazer um dado mensal parecer diário.
2. **Falta o mês de junho de 2025.** Entre 04/05/2025 e 06/07/2025 há um vão de 63 dias. Por isso a coluna "observação anterior" é de **dois meses antes**, não de um.
3. **A parada é da Itália, não da API.** Na mesma consulta, a **França** tem observação até **02/11/2025** (88 registros). A **Espanha** para no mesmo 06/07/2025. Ou seja: a fonte está viva; o dado italiano é que não foi atualizado. **NÃO SEI** por quê — não achei nota da Comissão explicando.

### Sinal de preço que AINDA está vivo (índice, não preço de praça)

**SOURCE:** Eurostat, `apri_pi_outq` — *Price indices of agricultural products, output — quarterly data* · **UNIT:** número índice, base 2020 = 100, índice nominal · **GEOGRAPHY:** Itália · **PUBLICATION_DATE (updated):** 30/07/2026

| Item (código Eurostat) | 2025-Q1 | 2025-Q4 | **2026-Q1** | vs trimestre anterior | vs mesmo trim. do ano anterior |
|---|---|---|---|---|---|
| **Vino** (AM070000) | 114,7 | 112,7 | **111,3** *(p = provisório)* | −1,2 % | **−3,0 %** |
| Vino DOP e IGP (AM073000) | 113,6 | 111,6 | **110,5** *(p)* | −1,0 % | −2,7 % |
| Vino sem DOP/IGP — *table wine* (AM078000) | 127,7 | 125,3 | **119,9** *(p)* | −4,3 % | **−6,1 %** |

O `p` é da própria fonte: o valor de 2026-Q1 é **provisório** e pode ser revisto. As variações percentuais desta tabela foram **calculadas por mim** a partir dos índices publicados; a Eurostat publica o nível, não a variação.

### Terceiro sinal, e o mais defasado: índice ISMEA

**SOURCE:** ISMEA — *Indice Ismea dei prezzi alla produzione (Base 2010=100)*, lido no **Internet Archive** (a fonte ao vivo respondeu página "Blocked / GEO_IP_BLOCK") · **REFERENCE_PERIOD:** julho de 2025 · **PUBLICATION_DATE:** até 15/09/2025 (data do snapshot) · **GEOGRAPHY:** Itália · **UNIT:** número índice base 2010 = 100

> Citação literal da tabela: **`Vino 170,89 -0,7 -2,4`**
> — isto é: índice 170,89; −0,7 % sobre junho/2025; −2,4 % sobre julho/2024.

**Este número tem 13 meses de idade.** Não é o estado corrente. Está aqui só para mostrar que o sinal ISMEA de preço ao produtor de vinho **existe** e que, na última vez em que foi lido, já apontava para baixo no ano.

### ⚠ Defeito encontrado no arquivo do repositório

O arquivo `C:\eame-sintonia\data\samples\IT-MERCADO\EU-AGRIFOOD-wine-prices-IT.json` declara `"PRODUCT_MARKET_PAIRS": 1` e guarda **uma** linha, com `"PRODUCT": null` e `"MARKET": "Italy"`. A fonte ao vivo tem **10 pares**. E a linha guardada mistura três séries diferentes:

- `PRICE_NUM: 61.75` → é **Pescara Vino bianco senza DOP/IGP**
- `PREV_PRICE_NUM: 70.88` → **não** é o preço anterior de Pescara bianco; é o preço de **Pescara Vino ROSSO** na **mesma** semana
- `YEAR_AGO_PRICE_NUM: 51.05` (`YEAR_AGO_END: 07/07/2024`) → é **Bari Vino bianco**, outra praça

Quem usar esse arquivo como está vai publicar uma variação de −12,9 % que nunca existiu (é a diferença entre um vinho branco e um vinho tinto, na mesma semana, na mesma praça). **Este relatório não usou o arquivo do repositório; usou a fonte ao vivo, relida hoje.**

---

## 2. PRODUÇÃO E RENDIMENTO

### Eurostat — o que abriu

**SOURCE:** Eurostat, `apro_cpnh1` — *Crop production in national humidity* · **CROP:** `W1100 = Grapes for wines` (**uva para vinho — não é vinho**) · **GEOGRAPHY:** Itália · **PUBLICATION_DATE (updated):** **28/08/2026** (cinco dias atrás)

| Ano | Área colhida (mil ha) | Produção colhida (mil t) | Rendimento implícito (t/ha) — *calculado por mim* |
|---|---|---|---|
| 2022 | 658,35 | 7.444,55 | 11,31 |
| 2023 | 661,81 | **5.845,21** | 8,83 |
| 2024 | 664,58 | 6.610,19 | 9,95 |
| **2025** | **672,66** | **6.679,37** | **9,93** |
| 2026 | *sem valor* | *sem valor* | — |

- **Área 2025 vs 2024: +1,2 %.** A área plantada de uva para vinho na Itália **continua subindo**, ano após ano, desde 2019 (646,47 → 672,66 mil ha).
- **Produção 2025 vs 2024: +1,0 %** — praticamente parada. Ainda **−10,3 % abaixo do pico de 2022** e **+14,3 % acima do fundo de 2023**.
- **Rendimento:** a Eurostat publica o campo `YLD_T_HA` **vazio** para a Itália. Os 9,93 t/ha de 2025 são **divisão minha** (produção ÷ área), não número da fonte.
- **Uva sem distinção de destino** (`W1000 = Grapes`): 2025 = 723,68 mil ha e 7.681,20 mil t.
- **Uva para vinho comum, sem DOP/IGP** (`W1190`): a área **encolhe** — 161,7 mil ha em 2019 para **144,18 mil ha em 2025**. É a única categoria em queda de área.

**Não há dado de 2026.** A colheita está acontecendo agora.

### Quebra regional (NUTS 2)

**NÃO DISPONÍVEL nesta rota.** Consultei `apro_cpnhr` (produção por região NUTS 2) para `W1100` e para `W1000` em Piemonte, Lombardia, Veneto, Friuli, Toscana, Abruzzo, Campania, Puglia e Sicilia: HTTP 200, resposta **vazia** (dimensão de cultura com tamanho 0, nenhum valor). A consulta funcionou; o conteúdo de uva não está lá. **NÃO SEI** se existe por outra chave de cultura.

### ISTAT — FONTE NÃO ALCANÇADA

- `esploradati.istat.it` (portal de dados) e `esploradati.istat.it/SDMXWS/rest/...`: **HTTP 000**, conexão não completou, em duas tentativas.
- `sdmx.istat.it/SDMXWS/rest/dataflow/IT1`: **HTTP 302** para `https://sdmx.istat.it` e depois **timeout**.
- `www.istat.it`: **HTTP 200**, 268.390 bytes — o site institucional responde. A página *"Stima sulla superficie vitivinicola e produzione vinicola"* abriu (108.028 bytes) mas é **só ficha de metadados**, com "Data pubblicazione: 24 Dicembre 2021" e **nenhum número**.

**Portanto: não li nenhum número do ISTAT diretamente.** Isto é FONTE NÃO ALCANÇADA, não fonte vazia.

### JRC MARS

**SOURCE:** JRC MARS Bulletin — Crop monitoring in Europe · **PUBLICATION_DATE:** **24/08/2026** · título literal: *"Exceptionally dry and hot weather threatens summer crops"*. Próximas edições anunciadas na página: 28 de setembro, 26 de outubro, 23 de novembro de 2026.

**O MARS não faz previsão de safra para videira.** As culturas com previsão de rendimento na edição de 24/08/2026 são milho-grão, culturas de verão e cereais de inverno. Nenhuma menção a uva, vinhedo ou vinho.

O que ele diz sobre a Itália, literalmente, e que **vale como clima, não como previsão de uva**:

> *"High temperatures combined with insufficient rainfall strongly affected summer crops, particularly during flowering and yield formation"* — em **"northern and central Italy"**.

---

## 3. OFERTA E COMÉRCIO

### 3.1 Estoque de vinho nas adegas — o dado italiano mais recente que existe

**SOURCE:** MASAF / ICQRF — *Cantina Italia: Report n. 8/2026; dati al 31 luglio 2026 dei Vini, mosti, denominazioni detenuti in Italia* · **REFERENCE_PERIOD:** posição em **31/07/2026** · **PUBLICATION_DATE:** **10/08/2026** · **GEOGRAPHY:** Itália, com quebra por região · **UNIT:** hectolitros
**Rota:** planilha oficial `.ods` anexa ao relatório, cabeçalho literal: **`VINI DOP-IGP presenti in Italia al 31 luglio 2026`** / **`detenuti da soggetti obbligati alla tenuta del registro telematico`**

Somei as 20 regiões da planilha oficial. **A soma é minha; os valores por região são da fonte.**

| Posição | DOP (mln hl) | IGP (mln hl) | DOP + IGP (mln hl) |
|---|---|---|---|
| 31/07/**2025** (Report n. 8/2025, publicado 07/08/2025) | 22,388 | 10,033 | **32,421** |
| 30/06/**2026** (Report n. 7/2026, publicado 10/07/2026) | 25,516 | 12,128 | **37,644** |
| **31/07/2026** (Report n. 8/2026) | **23,537** | **10,963** | **34,500** |
| **Var. sobre o mês anterior** | −7,8 % | −9,6 % | **−8,4 %** |
| **Var. sobre o mesmo dia do ano anterior** | +5,1 % | +9,3 % | **+6,4 %** |

**A comparação de um ano é entre dois relatórios da MESMA fonte, com o MESMO recorte (DOP+IGP, 20 regiões, mesma planilha).** A queda de −8,4 % no mês é **sazonal**: fim de campanha, adega esvaziando antes da vendemmia. A alta de **+6,4 % no ano** é que é o sinal.

**Onde o estoque cresceu — quebra regional, 31/07/2025 → 31/07/2026 (DOP+IGP):**

| Região | 2025 (mln hl) | 2026 (mln hl) | Var. |
|---|---|---|---|
| Sicilia | 1,788 | 2,447 | **+36,8 %** |
| Abruzzo | 1,507 | 1,811 | **+20,2 %** |
| Puglia | 2,766 | 3,139 | **+13,5 %** |
| Veneto | 8,693 | 8,936 | +2,8 % |
| Trentino-Alto Adige | 1,759 | 1,785 | +1,5 % |
| Emilia-Romagna | 2,160 | 2,185 | +1,2 % |
| Piemonte | 3,065 | 3,073 | +0,3 % |
| Toscana | 4,987 | 4,988 | +0,0 % |

O Veneto sozinho carrega **25,9 %** de todo o estoque DOP+IGP nacional (8,936 de 34,500 mln hl).

**Número-cabeça (FONTE SECUNDÁRIA, declarada como tal):** o total de vinho — incluindo o que não é DOP nem IGP — não está na planilha que li; está no texto do boletim, cujo PDF não consegui extrair (fonte incorporada sem tabela `ToUnicode`, texto ilegível por máquina). A imprensa especializada, citando o ICQRF, publica: *"negli stabilimenti enologici italiani sono presenti **42,6 milioni di ettolitri di vino, 3,1 milioni di ettolitri di mosti**"*, com **+6,9 %** sobre o ano anterior, **55,9 %** no Norte, **55,4 %** DOP e **25,8 %** IGP (WineNews, 11/08/2026). **Confere com a minha soma:** 23,537 ÷ 42,6 = 55,2 % (DOP) e 10,963 ÷ 42,6 = 25,7 % (IGP). Os dois caminhos batem.

### 3.2 Exportação de vinho — HS 2204

**SOURCE:** Eurostat Comext, `ds-045409` — *EU trade since 1988 by HS2-4-6 and CN8* · **PRODUCT:** `2204` (*"Wine of fresh grapes, incl. fortified wines; grape must…"*) · **FLOW:** EXPORT · **REPORTER:** Itália · **GEOGRAPHY:** Itália → mundo e Itália → EUA · **PUBLICATION_DATE (updated):** **14/08/2026** · **REFERENCE_PERIOD:** mensal, último mês fechado **maio de 2026** · **UNIT:** euros e 100 kg (converti para mil toneladas)

| Acumulado **janeiro–maio** | 2024 | 2025 | **2026** | 2026 vs 2025 |
|---|---|---|---|---|
| **Mundo — valor** (mln €) | 3.209,9 | 3.207,7 | **2.987,5** | **−6,9 %** |
| **Mundo — volume** (mil t) | 870,2 | 852,3 | **809,1** | **−5,1 %** |
| **EUA — valor** (mln €) | 792,4 | 838,7 | **709,1** | **−15,5 %** |
| **EUA — volume** (mil t) | 150,7 | 150,6 | **141,6** | **−6,0 %** |

Valor unitário implícito (**cálculo meu**, valor ÷ volume): mundo **3.692 €/t** em 2026 contra 3.764 em 2025 (**−1,9 %**); **EUA 5.008 €/t** contra 5.569 (**−10,1 %**).

**Como ler isto sem exagerar:** para os EUA o **valor caiu muito mais que o volume**. Isso é consistente com preço médio menor por litro embarcado. **Não prova** o motivo. Pode ser tarifa, câmbio, mudança de mix (menos garrafa cara, mais granel), promoção, ou tudo junto. Eu não medi o motivo. E — pelo mesmo raciocínio da regra das importações — **exportação caindo não é, sozinha, prova de que a demanda caiu**: pode ser estoque de importador, antecipação de embarque, ou preço.

**Ano cheio, para contexto:** 2024 = 8.076,3 mln € e 2025 = 7.777,5 mln € (−3,7 %); volumes 2,14 e 2,10 mln t.

### 3.3 O que NÃO consegui em oferta e comércio

- **Balanço de abastecimento ISMEA** (*Bilanci di approvvigionamento*, com "Vino" entre os setores, "ultimo aggiornamento: gennaio 2026"): a estrutura foi vista em snapshot de arquivo; **o Excel não foi baixado** porque o host da ISMEA está bloqueado por geografia de IP. **NÃO SEI** os valores.
- **Importação de vinho pela Itália:** não consultei. **NÃO SEI.**
- **Consumo interno / compras domésticas:** não consultei nesta rodada. **NÃO SEI.**

---

## 4. CONFIANÇA DO PRODUTOR

**O nível que a fonte publica é SETORIAL. Para vinho, o setor chama-se "Vino".**

**SOURCE:** ISMEA — *Indice Ismea del clima di fiducia (ICF)* · **CADÊNCIA:** trimestral · **GEOGRAPHY:** Itália · **UNIT:** índice de **−100 a +100** (não é porcentagem)

**VALOR: NÃO LIDO.** O portal `ismeamercati.it` não respondeu (HTTP 000, falha de conexão após ~21 s, também direto no IP 2.33.31.187) e `ismea.it` devolveu página de bloqueio da Barracuda com o texto `GEO_IP_BLOCK`, inclusive em **janela gráfica de Chrome real** — ou seja, não é detecção de robô, é bloqueio por país de origem do IP. **FONTE NÃO ALCANÇADA ≠ FONTE VAZIA.**

O que consegui confirmar sobre a capacidade, sem o número:

- O ICF tem seletor de comparto e **"Vino" é um dos compartos** — ao lado de Agroalimentare, Ortaggi, Frutta, Agrumi, Olio d'oliva e Cereali.
- O índice sintetiza duas coisas declaradas pela fonte: *"l'andamento corrente degli affari della loro azienda"* e *"le attese sull'evoluzione economica della stessa nei prossimi 2-3 anni"*. A página pública mostra só o valor único, não as duas componentes.
- O último relatório trimestral que consegui datar é *"La congiuntura Agricola - IV trimestre 2025"*, publicado em **29/01/2026**. Se o ritmo se manteve, o I e o II trimestre de 2026 já saíram — **mas isso eu NÃO SEI**, porque não há snapshot posterior a abril/2026 dessa lista.

**Três coisas que este item NÃO autoriza:**
1. **Confiança do setor "Vino" não é confiança do produtor de uva de uma denominação, nem de uma província.** É um agregado nacional de comparto.
2. O ICF **Agricoltura** (agregado) é outro número, e não pode ser usado como se fosse o do vinho.
3. A escala é −100 a +100. Publicar "índice ISMEA a −1,4 %" com sinal de porcentagem é erro — a imprensa italiana já o cometeu.

**Nenhum outro índice de confiança do produtor de uva/vinho italiano foi alcançado nesta rodada.**

---

## 5. PRESSÃO DE CUSTO

**SOURCE:** Eurostat, `apri_pi_inq` — *Price indices of the means of agricultural production, input — quarterly data* · **UNIT:** número índice, base **2020 = 100**, índice nominal · **GEOGRAPHY:** Itália · **PUBLICATION_DATE (updated):** **11/08/2026** · **REFERENCE_PERIOD:** último trimestre publicado **2026-Q1** (marcado `p` = provisório pela fonte)

| Rubrica (código Eurostat) | 2025-Q1 | 2025-Q4 | **2026-Q1** | vs trim. anterior | vs 2025-Q1 |
|---|---|---|---|---|---|
| **Input total** (AM220000) | 128,6 | 127,8 | **130,4** *(p)* | **+2,0 %** | **+1,4 %** |
| Bens e serviços correntes (AM200000) | 130,9 | 129,6 | **132,7** *(p)* | +2,4 % | +1,4 % |
| **Fertilizantes e corretivos** (AM203000) | 144,4 | 149,4 | **155,4** *(p)* | **+4,0 %** | **+7,6 %** |
| **Energia e lubrificantes** (AM202000) | 159,3 | 146,8 | **156,8** *(p)* | **+6,8 %** | −1,6 % |
| **Defensivos — *plant protection products*** (AM204000) | 124,4 | 122,9 | **125,5** *(p)* | **+2,1 %** | +0,9 % |

*(Variações percentuais calculadas por mim sobre os índices publicados.)*

**Como isso se encaixa com o preço do vinho — e o que isso NÃO é:**

Os dois índices têm a **mesma base (2020 = 100)**, a **mesma geografia** e o **mesmo trimestre**. Em 2026-Q1:

- índice de **preço recebido** pelo vinho: **111,3** — ou seja, +11,3 % acima de 2020
- índice de **custo total de insumo**: **130,4** — ou seja, +30,4 % acima de 2020
- **A distância entre as duas linhas é de 19,1 pontos de índice**, e ela **aumentou** no último ano (em 2025-Q1 era 128,6 − 114,7 = 13,9 pontos).

**Isto é comparação entre dois índices publicados. NÃO é margem, NÃO é lucro e NÃO é resultado de nenhuma fazenda.** Índice de preço médio nacional não conhece o contrato de ninguém, não conhece a produtividade da parcela, não conhece a estrutura de custo de cada adega. Preço de cultura em alta nunca é, sozinho, lucro do produtor — e preço em baixa com custo em alta também não vira, sozinho, prejuízo demonstrado. É um sinal de aperto, e só.

**O que NÃO consegui em custo:** o índice ISMEA de *mezzi correnti di produzione* (custo de insumo italiano de fonte nacional) — a série baixável parava em 2024 no snapshot de abril/2026, e a página dedicada aparecia como *"Pagina non più disponibile"*. **NÃO SEI** se existe rubrica separada para *prodotti fitosanitari* lá dentro.

---

## 6. OUTLOOK — projeções, e de quem elas são

> **Esta seção é PROJEÇÃO DE TERCEIROS. Não é estado corrente. Cada linha traz o nome de quem projetou.**

### 6.1 Projeção da vendemmia 2026 — ELA NÃO EXISTE, e isso é um fato declarado

**QUEM:** Assoenologi, ISMEA e Unione Italiana Vini (UIV), em conjunto · **DATA:** **29/07/2026** · **GEOGRAPHY:** Itália

> *"Assoenologi, Ismea e Uiv hanno deciso di sospendere le previsioni vendemmiali per la campagna vitivinicola 2026"*
> Motivo declarado: *"In un contesto caratterizzato da condizioni climatiche sempre più variabili, le stime effettuate prima della conclusione della raccolta possono risultare soggette a significative variazioni"*

As três entidades cancelaram a coletiva de imprensa que tradicionalmente ocorre na primeira metade de setembro e vão apresentar *"i dati consuntivi al termine della campagna vendemmiale"*, com a declaração de vendemmia pedida para **meados de novembro de 2026**.

**Consequência prática:** hoje, 02/09/2026, **não existe número oficial de safra 2026 para o vinho italiano** — nem estimativa. Quem publicar um está publicando chute ou fonte não-oficial. *(Leitura em askanews, 29/07/2026, reportando a decisão conjunta.)*

### 6.2 Última projeção de campanha que a ISMEA chegou a publicar

**QUEM:** ISMEA, relatório AgriMercati 1/2026 · **PUBLICATION_DATE:** **22/01/2026** · **REFERENCE_PERIOD:** campanha 2025/2026 · **UNIT:** milhões de hectolitros

> *"Vino - Campagna 2025/2026 mondo stimata a 232 milioni di ettolitri (+3%), Italia si conferma leader mondiale con 47 milioni di ettolitri (+8%); giacenze a luglio 2025 pari a 40,6 milioni di ettolitri, di cui 38,2 di vino, stabili sul livello di luglio 2024"*

**Cuidado com esta citação, por três motivos:** (1) é de janeiro de 2026, tem 7 meses; (2) o estoque de 40,6 mln hl (dos quais 38,2 de vinho) que a ISMEA cita para julho/2025 **tem recorte diferente** do ICQRF — **não construa uma variação anual misturando ISMEA e ICQRF**; a variação anual válida está na seção 3.1, calculada dentro do ICQRF; (3) o próprio relatório mistura cadências no mesmo texto ("primi undici mesi del 2025", "terzo trimestre 2025", "a dicembre 2025"), então não existe um carimbo de data único para ele.

### 6.3 Clima — avaliação do JRC MARS

**QUEM:** JRC MARS Bulletin · **PUBLICATION_DATE:** 24/08/2026 · título: *"Exceptionally dry and hot weather threatens summer crops"* · frase sobre a Itália: *"High temperatures combined with insufficient rainfall strongly affected summer crops"* em *"northern and central Italy"*.

**Rótulo obrigatório:** esta é a avaliação do MARS para **culturas de verão** (milho e afins). **O MARS não modela videira.** Usar esta frase é usar contexto de clima regional, não previsão de uva. Próxima edição: 28/09/2026.

### 6.4 Ficou de fora por não ter lastro verificado

Circulam na imprensa italiana números de produção de vinho 2025 (ISTAT ~47,8 mln hl; AGEA/declarações ~44,4 mln hl) e um balanço de 12 meses de tarifa americana atribuído ao Observatório da UIV (−17 % em valor, mais de 340 milhões de euros). **Não li nenhum desses números na fonte primária.** Por isso eles não entram como dado deste relatório — ficam registrados aqui como pista a verificar.

---

## 7. TEMPERATURA DE MERCADO

# PRESSURED

> **⚠ ISTO É INTERPRETAÇÃO DO SINTONIA, NÃO É FATO OBSERVADO.**
> Nenhuma fonte publica uma "temperatura de mercado". A palavra acima é uma leitura minha, montada a partir dos sinais abaixo. Um leitor com os mesmos dados pode chegar a outra palavra. Os dados estão todos acima, com fonte e data, exatamente para permitir isso.

### « POR QUE »

| Componente | Seta | Evidência que sustenta a seta | Fonte / período |
|---|---|---|---|
| **Estoque em adega (DOP+IGP)** | **↑ +6,4 %** no ano | 32,421 → 34,500 mln hl | ICQRF, 31/07/2025 → 31/07/2026 |
| **Estoque — regiões do Sul e Ilhas** | **↑↑** | Sicilia +36,8 %, Abruzzo +20,2 %, Puglia +13,5 % | ICQRF, mesma janela |
| **Exportação, valor (mundo)** | **↓ −6,9 %** | 3.207,7 → 2.987,5 mln € | Comext, jan–mai 2026 vs 2025 |
| **Exportação, valor (EUA)** | **↓↓ −15,5 %** | 838,7 → 709,1 mln € | Comext, jan–mai 2026 vs 2025 |
| **Valor unitário exportado p/ EUA** | **↓ −10,1 %** | 5.569 → 5.008 €/t *(cálculo meu)* | Comext, jan–mai |
| **Índice de preço recebido — vinho** | **↓ −3,0 %** no ano | 114,7 → 111,3 (2020=100), provisório | Eurostat `apri_pi_outq`, 2026-Q1 |
| **Índice de preço — vinho comum** | **↓↓ −6,1 %** no ano | 127,7 → 119,9 | Eurostat, 2026-Q1 |
| **Custo total de insumo** | **↑ +1,4 %** no ano, **+2,0 %** no trimestre | 128,6 → 130,4 | Eurostat `apri_pi_inq`, 2026-Q1 |
| **Fertilizante** | **↑↑ +7,6 %** no ano | 144,4 → 155,4 | Eurostat, 2026-Q1 |
| **Defensivo** | **↑ +0,9 %** no ano, **+2,1 %** no trimestre | 124,4 → 125,5 | Eurostat, 2026-Q1 |
| **Área plantada de uva para vinho** | **↑ +1,2 %** | 664,58 → 672,66 mil ha | Eurostat `apro_cpnh1`, 2025 vs 2024 |
| **Produção de uva para vinho** | **→ +1,0 %** | 6.610,19 → 6.679,37 mil t | Eurostat, 2025 vs 2024 |
| **Preço por praça** | **⛔ CEGO** | 10 de 10 praças paradas desde 06/07/2025 | EU Agri-food Data Portal |
| **Confiança do produtor (setor Vino)** | **⛔ NÃO LIDO** | portal ISMEA bloqueado por geografia de IP | ISMEA ICF |
| **Safra 2026** | **⛔ SEM ESTIMATIVA** | Assoenologi/ISMEA/UIV suspenderam a previsão | declaração de 29/07/2026 |

**A frase em uma linha:** oferta parada em cima (estoque subindo pelo segundo ano, área ainda crescendo), saída travada embaixo (exportação caindo em valor e em volume, e com preço unitário menor nos EUA), preço recebido descendo e custo de insumo subindo no mesmo trimestre — **com três instrumentos de medição apagados ao mesmo tempo** (preço de praça, confiança setorial e estimativa de safra).

**Por que não escolhi outra palavra:** não é `VOLATILE` porque não vi oscilação — vi movimento de mão única. Não é `MIXED SIGNALS` porque os sinais que consegui ler apontam todos para o mesmo lado. Não é `COOLING` porque não é só desaceleração: o estoque acumulado é pressão física, não desaquecimento. **Mas registre-se que a confiança nesta palavra é limitada pelos três instrumentos apagados** — em especial pela cegueira de 14 meses no preço de praça, que é justamente onde a pressão apareceria primeiro.

---

## 8. O QUE ISTO NÃO AUTORIZA A DIZER

1. **Não autoriza dizer qual é o preço do vinho italiano hoje.** A última leitura por praça é de **06/07/2025**. Qualquer preço de praça apresentado como "atual" está 14 meses atrasado.
2. **Não autoriza dizer que o preço parou de existir, ou que a Itália parou de cotar.** A série da UE não foi atualizada; a França, na mesma consulta, tem dado até novembro de 2025. **Não achei ≠ não existe.**
3. **Não autoriza tratar o dado como semanal.** A cadência real é mensal, com o mês de junho de 2025 faltando. Trimestral (Eurostat) é trimestral; anual (área e produção) é anual.
4. **Não autoriza dizer que a confiança do produtor de vinho caiu, subiu ou ficou parada.** O índice ISMEA do setor "Vino" **não foi lido**. E, mesmo se fosse, seria confiança **do setor Vino**, nunca de uma denominação, de uma província ou de um produtor.
5. **Não autoriza transformar exportação em demanda.** Exportação caindo pode ser tarifa, câmbio, mix, estoque no importador ou preço. Eu não medi o motivo. O mesmo vale ao contrário: importação subindo não seria demanda subindo.
6. **Não autoriza dizer que o produtor italiano de uva está perdendo dinheiro** — nem que está ganhando. Os 19,1 pontos de distância entre o índice de preço do vinho e o índice de custo de insumo são **dois índices nacionais**, não uma margem, não um resultado, não a contabilidade de ninguém.
7. **Não autoriza nada sobre a ADAMA.** Nada aqui prevê venda, participação de mercado, estoque de distribuidor, intenção de compra, giro de canal ou resposta a lançamento. Nenhuma fonte deste relatório mede qualquer uma dessas coisas.
8. **Não autoriza previsão de safra 2026.** As três entidades que fazem essa estimativa na Itália **desistiram de fazê-la este ano** e vão publicar só depois da colheita, com declaração pedida para meados de novembro de 2026.
9. **Não autoriza deduzir pressão de praga, área tratada ou número de aplicações.** Nenhum dado deste relatório mede doença, praga, alerta fitossanitário ou calendário de aplicação em videira.
10. **Não autoriza somar ISMEA com ICQRF.** Os dois publicam estoque de vinho com recortes diferentes. A variação anual válida (+6,4 %) foi calculada dentro do ICQRF, entre dois relatórios da mesma série.
11. **Não autoriza usar o arquivo `EU-AGRIFOOD-wine-prices-IT.json` do repositório como está.** Ele colapsou 10 séries em 1 e misturou três praças/tipologias numa única linha (ver seção 1).
12. **Não autoriza nota, score ou "termômetro" numérico de 0 a 100.** A temperatura da seção 7 é uma palavra qualitativa com as setas à mostra, e está rotulada como interpretação.

---

## ANEXO — rotas testadas nesta rodada, com resultado

| Fonte | Rota | Resultado |
|---|---|---|
| EU Agri-food Data Portal — wine/prices | `api.tech.ec.europa.eu/agrifood/api/wine/prices` | **HTTP 200**, 775 registros IT, 10 pares · série IT termina 06/07/2025 |
| EU Agri-food Data Portal — outros endpoints de vinho | `wine/production`, `wine/stocks`, `wine/trade`, `wine/areas` | **HTTP 404** — só existe `prices` |
| Eurostat `apro_cpnh1` (produção) | API de disseminação, JSON-stat | **HTTP 200**, atualizado 28/08/2026, IT até 2025 |
| Eurostat `apro_cpnhr` (NUTS 2) | idem, `W1100` e `W1000` | **HTTP 200 com resposta vazia** para uva na Itália |
| Eurostat `apri_pi_outq` (preço recebido) | idem | **HTTP 200**, atualizado 30/07/2026, até 2026-Q1 (p) |
| Eurostat `apri_pi_inq` (custo de insumo) | idem | **HTTP 200**, atualizado 11/08/2026, até 2026-Q1 (p) |
| Eurostat Comext `ds-045409` | `ec.europa.eu/eurostat/api/comext/dissemination/...` | **HTTP 200**, atualizado 14/08/2026, mensal até maio/2026 |
| Eurostat Comext via API de disseminação normal | `.../statistics/1.0/data/DS-045409` | **HTTP 404** — precisa do caminho `/comext/` |
| MASAF / ICQRF — Cantina Italia | `masaf.gov.it` HTML + anexo `.ods` | **HTTP 200** — planilha oficial lida e somada (jul/2025, jun/2026, jul/2026) |
| MASAF / ICQRF — PDF do boletim | anexo `.pdf` | **HTTP 200 mas ILEGÍVEL por máquina**: fonte incorporada sem tabela `ToUnicode`; nenhum texto confiável extraído |
| ISMEA `ismeamercati.it` | https e http, e direto no IP 2.33.31.187 | **HTTP 000** — conexão não completou (~21 s) |
| ISMEA `ismea.it` | curl e **janela gráfica de Chrome real** | Página **"Blocked"** com `GEO_IP_BLOCK`, assinatura Barracuda Networks |
| ISTAT `esploradati.istat.it` / SDMX | REST SDMX | **HTTP 000** / 302 seguido de timeout |
| ISTAT `www.istat.it` | HTML | **HTTP 200**, mas a página da pesquisa vitivinícola é ficha de metadados de 2021, **sem números** |
| JRC MARS | página do boletim + edição de 24/08/2026 | **HTTP 200** — lido; **não cobre videira** |
| Catálogo nacional italiano de dados abertos | `dati.gov.it/opendata/api/3/action/package_search?q=ismea` | **HTTP 200 com `{"count": 0}`** |

**Custo desta rodada: US$ 0,00.** Nenhuma execução paga de Apify foi usada; todas as leituras foram APIs públicas, HTML público e um arquivo `.ods` público do Ministério italiano.

**Arquivos do repositório relevantes:**
- `C:\eame-sintonia\data\samples\IT-MERCADO\EU-AGRIFOOD-wine-prices-IT.json` — **contém o defeito descrito na seção 1**
- `C:\eame-sintonia\data\samples\IT-MERCADO\EU-AGRIFOOD-cereal-prices-IT.json` e `EU-AGRIFOOD-oliveOil-prices-IT.json` — outras culturas, não usados aqui