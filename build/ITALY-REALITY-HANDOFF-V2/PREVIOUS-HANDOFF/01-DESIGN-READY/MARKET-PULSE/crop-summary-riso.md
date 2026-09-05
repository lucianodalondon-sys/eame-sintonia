# MARKET PULSE — RISO (arroz) · ITÁLIA
**Data da montagem:** 02/09/2026 · **Fonte-âncora:** European Commission Agri-food Data Portal + Ente Nazionale Risi (ENR) + Eurostat + Camere di Commercio

---

## 0. O QUE FOI ALCANÇADO E O QUE NÃO FOI (leia antes dos números)

**Fato de rota:** o material pré-mapeado desta rodada (ISMEA, cereais, azeite, vinho) **não contém arroz**. Os 3 arquivos gravados em `data/samples/IT-MERCADO/` têm 8 produtos (trigo mole, trigo duro, cevada forrageira, milho forrageiro, azeite, vinho) e **nenhum deles é risone**. Todo o lastro abaixo foi coletado agora, do zero.

| Fonte | Estado | Prova |
|---|---|---|
| EC Agri-food Data Portal — `/agrifood/api/rice/prices` | **ALCANÇADA** | HTTP 200, 6.108.629 bytes, 20.846 registros IT, série de 09/07/2000 a 30/08/2026 |
| EC Agri-food Data Portal — `/agrifood/api/rice/production` | **ALCANÇADA** | HTTP 200, 22.810 bytes, 76 registros IT, 2006–2025 |
| Ente Nazionale Risi (enterisi.it) | **ALCANÇADA** | HTTP 200; notícias até 01/09/2026; PDFs de estoque, import, export |
| Borsa Merci di Vercelli (pno.camcom.it) | **ALCANÇADA** | listino n.30 de 01/09/2026, PDF 291.430 bytes |
| Mercato di Novara (pno.camcom.it) | **ALCANÇADA** | listino n.27 de 27/07/2026, PDF 320.364 bytes |
| Sala Mortara (paviaprezzi.it) | **ALCANÇADA** | CSV oficial, rilevazione 31/07/2026 |
| Eurostat `APRI_PI_INQ` (custo de insumo) | **ALCANÇADA** | HTTP 200; `updated: 2026-08-11` |
| JRC MARS Bulletin | **PARCIAL** | boletim de 24/08/2026 lido; **não nomeia arroz** |
| ISMEA | **NÃO ALCANÇADA** (bloqueio de IP documentado nesta rodada) — e, mesmo se aberta, **não publica setor "Riso"**: a lista de setores do ICF vai de "Cereali" a "Conigli" e não tem arroz |
| ISTAT (API SDMX) | **NÃO ALCANÇADA** — `esploradati.istat.it` → HTTP 000, 0 bytes; `sdmx.istat.it` → 302 para host que não responde. **FONTE NÃO ALCANÇADA ≠ FONTE VAZIA** |
| Piazze de Milano, Mantova, Verona, Bologna, Pavia | **NÃO LIDAS** — o ENR só publica o link para o boletim de cada Camera di Commercio; não abri esses quatro. **NÃO SEI** o preço nelas |

---

## 1. ESTADO CORRENTE — preço por praça e por variedade

### 1.1 A armadilha que precisa ser dita antes de qualquer número

Duas coisas quebram a leitura ingênua desta série, e as duas estão escritas nas próprias fontes:

**(a) A cotação está em pausa de fim de campanha.** No listino de Vercelli n.30 de **01/09/2026**, **todos os risoni estão `n.q.` (non quotato)**. Na semana anterior (25/08/2026), os quatro grupos que aparecem trazem a marca `(1)`, e o rodapé define literalmente: **"(1) nominale"**. Em Novara, o listino de 27/07/2026 traz um asterisco em *toda* a coluna de risoni e o rodapé diz **"* Nominale"**. Preço nominal é preço de referência sem negócio por trás — não é preço realizado.

**(b) A média "Avg" da Comissão muda de cesta.** Em 26/07/2026 a média Japonica (`Paddy | Japonica | Avg`) foi **€441,90** com 11 variedades cotadas; em 23/08/2026 foi **€319,00** com apenas 4 variedades cotadas (337, 300, 339, 300 → média exata 319). **Os -27,8% NÃO são queda de preço: são troca de cesta** — saíram Carnaroli (€721) e Arborio (€577) da média. Nenhuma variedade individual caiu na semana.

### 1.2 Preço por PRAÇA (mercado nomeado), €/tonelada, risone a granel

| Praça | Data da rilevazione | Situação | Exemplos literais |
|---|---|---|---|
| **Vercelli** (Borsa Merci specializzata in risi, D.P.R. 11.9.1974 n.651) | **01/09/2026** | **Todos os risoni `n.q.`** | "- Selenio t n.q. n.q." / "- Carnaroli n.q. n.q." |
| **Vercelli** — semana anterior | **25/08/2026** | 4 grupos, **todos nominais** | S. Andrea e similari **270,00–300,00 (1)**; Gloria **270,00–300,00 (1)**; Roma e similari, CL 145 **308,00–337,00 (1)**; Baldo e similari **312,00–339,00 (1)** |
| **Novara** | **27/07/2026** — **SÉRIE PARADA EM 2026** (é o último listino publicado; nenhum posterior existe na página em 01/09/2026) | Todos nominais, **variação 0,00 vs 20/07/2026** | Selenio 425,00–480,00\*; Tipo Ribe 285,00–340,00\*; CL 007 350,00–385,00\*; S.Andrea e similari 290,00–335,00\*; Tipo Baldo 295,00–340,00\*; Tipo Roma 285,00–325,00\*; Arborio-Volano-CL388 529,00–575,00\*; **Carnaroli 670,00–720,00\***; Caravaggio 630,00–675,00\*; Lungo B 300,00–335,00\* |
| **Mortara** (Sala Contrattazione, C.C. Cremona-Mantova-Pavia) | **31/07/2026** — **SÉRIE PARADA EM 2026** (última rilevazione oferecida no seletor) | Quase tudo estável vs 17/07/2026 | Vialone Nano 330,00–400,00 (NOMINALE); Sant'Andrea 260,00–335,00; Gloria 255,00–330,00; Lungo B 325,00–335,00; Arborio 530,00–575,00; Baldo 305,00–350,00; CL145/Roma 320,00–335,00; **Carnaroli 640,00–720,00**; **Caravaggio 630,00–675,00 → 675,00–720,00** (única alta); **Selenio 405,00–480,00 → n.q.** |
| Milano, Mantova, Verona, Bologna, Pavia | — | **NÃO SEI** — não abri esses boletins nesta rodada | — |

`SOURCE`: Camera di Commercio Monte Rosa Laghi Alto Piemonte (Vercelli, Novara) e Camera di Commercio Cremona Mantova Pavia (Mortara) · `UNIT`: €/tonnellata, IVA excluída, mín–máx · `GEOGRAPHY`: praça nomeada · `STAGE`: Vercelli "all'ingrosso... al netto di imposta sul valore aggiunto, mediazione e diritto di contratto E.N.R."; Novara "merce nuda franco azienda di produzione... pagamento 60 gg."; Mortara "merce sfusa, franco partenza, pronta consegna". **As três praças NÃO têm o mesmo estágio comercial — comparar mín/máx entre elas sem olhar o estágio produz número falso.**

### 1.3 Preço NACIONAL oficial (Comissão Europeia) — última semana cotada

`SOURCE`: European Commission, Agri-food Data Portal, `api.tech.ec.europa.eu/agrifood/api/rice/prices` · `GEOGRAPHY`: Itália (nacional — **esta série não tem praça**) · `UNIT`: €/Tonne · `PUBLICATION_DATE`: lido em 02/09/2026

| Estágio | Tipo | Variedade | Preço | `REFERENCE_PERIOD` | vs cotação anterior | vs 364 dias antes (mesma semana) |
|---|---|---|---|---|---|---|
| Paddy | Japonica | Baldo | **€339,00** | 17–23/08/2026 (sem. 51) | €339,00 em 26/07/2026 → **0,0%** | 27/07/2025 €577,00 → **−41,2%** (par 26/07/2026) |
| Paddy | Japonica | Roma E Cl 145 | **€337,00** | 17–23/08/2026 | €337,00 (rótulo "Roma") em 26/07/2026 → **0,0%** | 27/07/2025 €? — ver Roma abaixo |
| Paddy | Japonica | Gloria | **€300,00** | 17–23/08/2026 | €300,00 em 26/07/2026 → **0,0%** | 06/07/2025 €769,00 → **−61,0%** (par 05/07/2026) |
| Paddy | Japonica | S. Andrea | **€300,00** | 17–23/08/2026 | €300,00 em 26/07/2026 → **0,0%** | 06/07/2025 €769,00 → **−61,0%** (par 05/07/2026) |
| Paddy | Japonica | **Avg** | **€319,00** | 17–23/08/2026 | €441,90 em 26/07/2026 → **cesta trocada, não comparar** | 27/07/2025 €578,57 vs 26/07/2026 €441,90 → **−23,6%** |
| Broken | N.A. | Avg / Mezzagrana | **€430,00** | 24–30/08/2026 (sem. 52) | €430,00 desde 28/06/2026 → **0,0%**; era €440,00 em 21/06/2026 | par exato de 364 dias **não existe** (buraco de série); mais próximo 27/07/2025 €510,00, a 35 dias — **comparação suja, não use como y/y** |

**Variação ano contra ano, pares EXATOS de 364 dias (fim de campanha 2024/25 vs fim de campanha 2025/26):**

| Variedade | 26/07/2026 | 27/07/2025 | Δ |
|---|---|---|---|
| Baldo | 339,00 | 577,00 | **−41,2%** |
| Carnaroli | 721,00 | 900,00 | **−19,9%** |
| Arborio | 577,00 | 680,00 | **−15,1%** |
| Caravaggio | 721,00 | 769,00 | **−6,2%** |
| Crono-Sunrose | 307,00 | 432,00 | **−28,9%** |
| CL007 | 365,00 | 355,00 | **+2,8%** |
| Selenio (par 19/07) | 500,00 | 672,00 | **−25,6%** |
| Gloria / S. Andrea (par 05/07) | 300,00 | 769,00 | **−61,0%** |
| Omega / Araldo (par 28/06) | 432,00 | 576,00 | **−25,0%** |
| Centauro (par 21/06) | 432,00 | 576,00 | **−25,0%** |
| **Long B (Indica)** (par 14/06) | 311,00 | 528,00 | **−41,1%** |
| Roma (par 10/05) | 336,00 | 721,00 | **−53,4%** |

**Caminho dentro da campanha 2025/2026** (média Japonica paddy, cesta estável até julho): €535,92 (05/10/2025) → pico **€565,46 (09/11/2025)** → €417,08 (14/06/2026) → €441,90 (26/07/2026). **Do pico ao fim de julho: −21,9%.**

### 1.4 SÉRIES PARADAS — com o ano em que pararam

| Série (fonte EC) | Última observação | Parou em | Motivo documentado |
|---|---|---|---|
| **Milled non parboiled** (todas as 13 variedades: Carnaroli €2.300, Arborio €2.120, S.Andrea €1.750, Roma €1.650, Baldo €1.560, Selenio €1.460, Avg €1.582…) | 05/01/2025 | **2025** | Vercelli: *"Con delibera n. 18 del 27 febbraio 2025, disposta eliminazione rilevazione prezzi risi lavorati per irrilevanza degli scambi"*. Novara: *"Dal listino n. 11 del 17 marzo 2025 la Giunta camerale ha disposto l'eliminazione della rilevazione dei prezzi dei risi lavorati per l'irrilevanza degli scambi"* |
| **Milled parboiled** (Baldo €1.700, Avg €1.525, Ribe/Long B €1.350) | 05/01/2025 | **2025** | idem |
| **Paddy Indica** (Long B e Avg, €311,00) | 14/06/2026 | **2026** | não declarado |
| Paddy Japonica: Selenio, Roma, Carnaroli, Caravaggio, Arborio, Cl007, Crono-Sunrose | 26/07/2026 | **2026** | pausa de fim de campanha |
| Paddy Japonica: Omega, Araldo | 05/07/2026 | **2026** | — |
| Paddy Japonica: Centauro | 21/06/2026 | **2026** | — |
| Paddy Japonica: Diva Pv | 31/08/2025 | **2025** | — |
| Paddy Japonica: Crono | 23/02/2025 | **2025** | — |
| Paddy Japonica: Tipo Ribe, Loto, Cl 388 | out/2024 | **2024** | — |
| Estágio "Milled" (Rond €760, Thaibonnet €610, Ribe €730) e Broken Japonica | 15/11/2015 | **2015** | — |
| Subproducts (Pula, Lolla, Grana Verde) e Broken "Not informed" | 09/07/2017 | **2017** | — |
| **Praça Novara** | 27/07/2026 | **2026** | pausa sazonal |
| **Praça Mortara** | 31/07/2026 | **2026** | pausa sazonal |

**Preços comunitários comparativos** (`SOURCE`: Commissione europea, via ENR, "PREZZI COMUNITARI RISO", `REFERENCE_PERIOD` 04/08/2026, `UNIT` €/t, risone): Espanha Japonica **451,68** / Indica **344,07**; Bulgária Japonica **505,00**; Portugal, Grécia, Romênia **N.Q.**

**Cotações internacionais** (`SOURCE`: ENR, "Quotazioni internazionali", `REFERENCE_PERIOD` 26/08/2026, `UNIT` **US$/t**): Índia Indica lavorato 5% rott. **365**; Vietnã Indica 5% **440** (era 450 em 19/08); Paquistão Indica 5% **405**; Tailândia Indica 5% **462** (era 449); Brasil risone **340**; Uruguai risone **370** (era 360).

---

## 2. PRODUÇÃO E RENDIMENTO

`SOURCE`: European Commission, Agri-food Data Portal, `/agrifood/api/rice/production` · `GEOGRAPHY`: Itália · `PUBLICATION_DATE`: lido em 02/09/2026 · `REFERENCE_PERIOD`: ano de colheita

| Ano | Área (ha) | Arroz em casca / risone (t) — campo literal `riceHuskQuantity` | Equivalente beneficiado (t) | t/ha |
|---|---|---|---|---|
| **2025** | **234.732** | **1.408.696** | **820.100** | **6,00** |
| 2024 | 226.129 | 1.448.756 | 825.300 | 6,41 |
| 2023 | 210.239 | 1.383.723 | 803.000 | 6,58 |

**2025 vs 2024: área +3,8%, produção −2,8%, rendimento −6,3%.** A safra 2025 cresceu em hectare e encolheu em tonelada.

Detalhe 2025 por grão: Tondo 56.820 ha / 369.332 t / **6,50 t/ha**; Medio 13.091 ha / 66.271 t / **5,06 t/ha**; Lungo A 118.543 ha / 676.913 t / **5,71 t/ha**; Lungo B 46.278 ha / 296.180 t / **6,40 t/ha**.

**Área 2026 — estimativa** · `SOURCE`: Ente Nazionale Risi, *"Superfici coltivate a riso nel 2026"* · `PUBLICATION_DATE`: 22/07/2026 · `REFERENCE_PERIOD`: estimativa em 21/07/2026 · `UNIT`: hectares. Citação literal da folha: **"Stima al 21 luglio sulla base di 2.937 denunce che rappresentano il 79% della superficie del 2025"** — ou seja, **21% da área ainda não estava declarada quando o número saiu**.

| Grupo | 2026 (ha) | 2025 (ha) | Δ |
|---|---|---|---|
| **TOTALE** | **233.500** | **234.732** | **−1.232 (−0,5%)** |
| TONDO | 77.550 | 56.820 | **+20.730 (+36,5%)** |
| MEDIO | 6.870 | 13.091 | **−6.221 (−47,5%)** |
| LUNGO A | 109.230 | 118.542 | −9.312 (−7,9%) |
| LUNGO B | 39.850 | 46.278 | −6.428 (−13,9%) |
| ROMA-BALDO e similari | 16.950 | 28.283 | **−11.333 (−40,1%)** |
| VIALONE NANO | 2.650 | 4.408 | −1.758 (−39,9%) |
| CARNAROLI e similari | 29.000 | 24.554 | +4.446 (+18,1%) |
| ARBORIO e similari | 22.200 | 19.336 | +2.864 (+14,8%) |
| RIBE e similari | 32.100 | 35.619 | −3.519 (−9,9%) |
| SELENIO | 15.200 | 14.094 | +1.106 (+7,8%) |
| CENTAURO | 5.700 | 4.659 | +1.041 (+22,3%) |

**Área total praticamente parada; o mapa varietal virou de cabeça para baixo.** O total de 234.732 ha de 2025 na folha do ENR bate **exatamente** com o total de área do dataset da Comissão para 2025 — as duas fontes concordam.

**Rendimento 2026: NÃO SEI.** Nenhuma fonte publicou rendimento da safra 2026 até 02/09/2026 — a colheita italiana ainda não terminou.

**ISTAT: NÃO ALCANÇADO** (API HTTP 000). O dataset da Comissão é a fonte oficial usada aqui; **não é medição do ISTAT reempacotada — é a notificação do Estado-membro à Comissão**.

---

## 3. OFERTA E COMÉRCIO

### 3.1 Estoque na mão do produtor — o número mais duro desta ficha

`SOURCE`: Ente Nazionale Risi, *"TRASFERIMENTI RISONE CONVENZIONALE E BIOLOGICO E RIMANENZE PRESSO I PRODUTTORI"* · `REFERENCE_PERIOD`: **25 de agosto de 2026** · `GEOGRAPHY`: Itália · `UNIT`: toneladas · cadência **semanal**

| Campanha (mesma data) | Disponibilidade vendável | Transferido | % do disponível | **Sobra (rimanenza)** |
|---|---|---|---|---|
| **2025/2026 (25/08/2026)** | **1.439.047** | **1.321.975** | **91,86%** | **117.432** |
| 2024/2025 | 1.416.133 | 1.343.781 | 94,89% | 72.352 |
| 2023/2024 | 1.473.170 | 1.411.897 | 95,84% | 61.273 |
| 2022/2023 | 1.296.966 | 1.181.195 | 91,07% | 115.771 |

**A cinco semanas do fim da campanha, sobra na mão do produtor 117.432 t contra 72.352 t na mesma data de 2025: +45.080 t, +62,3%.** Transferido na semana: 10.970 t (0,76% do disponível). Onde a sobra se concentra: **Lungo A 70.415 t** (90,04% transferido), Baldo-Roma e similari 29.653 t (só **82,33%** transferido), Lungo B 20.179 t, Tondo 15.667 t.

### 3.2 Estoque na indústria

`SOURCE`: ENR, denúncias D5 de riserie, pilerie e comerciantes · `REFERENCE_PERIOD`: **31/07/2026** · atualização 20/08/2026 · `UNIT`: quintais (Q.li) · `GEOGRAPHY`: Itália. Cobertura declarada literalmente: **"dichiarazioni presentate da n. 171 operatori su 266"** — **64% dos operadores. Não é o total do país.**

Greggio em armazém **1.847.283,33 Q.li** (Tondo 385.802,91 · Medio 105.784,42 · **Lungo A 968.796,85** · Lungo B 335.745,36); Riso lavorato 948.937,99 Q.li; Riso semigreggio 286.275,43 Q.li; Rotture 107.557,99 Q.li.

### 3.3 Comércio

| Fluxo | 2025/2026 | 2024/2025 | Δ | Fonte / período |
|---|---|---|---|---|
| **Importação da Itália de países terceiros** | **216.180 t** | 189.378 t | **+26.802 t (+14,2%)** | ENR / MAECI–titoli AGRIM, 1/9/2025–31/8/2026, **PROVVISORIA**, base riso lavorato, risone excluído |
| — dos quais **Lungo B** | 200.661 t | 182.962 t | **+17.699 t** | idem |
| — Tondo | 10.061 t | 2.316 t | +7.745 t | idem |
| **Compras de Estados-membros UE** | 40.889 t | 37.876 t | +3.013 t (+8,0%) | ENR / **ISTAT**, 1/9/2025–**31/5/2026** |
| **Entregas para Estados-membros UE** | **350.838 t** | 383.341 t | **−32.503 t (−8,5%)** | ENR / **ISTAT**, 1/9/2025–**31/5/2026** |
| **Exportação para países terceiros** | 131.915 t | 130.975 t | +940 t (+0,7%) | ENR / Dichiarazioni ENR, 1/9/2025–31/8/2026, **PROVVISORIA** |
| — Turquia | 22.900 t | 13.106 t | **+9.794 t** | idem |
| — Reino Unido | 41.209 t | 48.929 t | −7.720 t | idem |

**⚠️ LEI 5 — importação subindo NÃO é demanda subindo.** Os +14,2% de importação são compatíveis com pelo menos quatro histórias diferentes, e os dados desta ficha **não separam qual delas é**: (a) arbitragem de preço — o Indica lavorado 5% da Índia está a **US$365/t** e o do Paquistão a **US$405/t**, e a indústria italiana pode comprar fora mais barato que dentro; (b) substituição de matéria-prima nacional que existe mas está parada no armazém do produtor (117.432 t sobrando); (c) reexportação — a exportação italiana não caiu; (d) formação de estoque industrial. Note que **os dois maiores blocos importados são Lungo B (+17.699 t) e Basmati/Paquistão-Índia**, categorias em que a Itália é estruturalmente deficitária — isso é **oferta**, não é sinal de que o consumo italiano cresceu. Ao mesmo tempo, as **entregas italianas para a UE caíram 8,5%**. Importação subindo + exportação intra-UE caindo + estoque do produtor subindo é um quadro de **pressão de oferta**, não de demanda quente.

**Cadências diferentes no mesmo bloco (LEI 2):** importação/exportação de países terceiros vão até **31/08/2026**; compras/entregas UE (ISTAT) param em **31/05/2026**. **Não some nem compare os quatro como se fossem o mesmo recorte de calendário.**

---

## 4. CONFIANÇA DO PRODUTOR

**Não existe índice de confiança publicado no nível da cultura RISO. NÃO SEI o valor, e não é porque a fonte esteja vazia — é porque o recorte não existe no nível pedido.**

- O único índice de confiança agrícola italiano é o **ICF — Indice ISMEA del clima di fiducia**, `cadência` **trimestral**, `geografia` **ITÁLIA**. A lista de setores publicada pelo ISMEA é: *Agroalimentare, Ortaggi, Frutta, Agrumi, Olio d'oliva, Vino, **Cereali**, Latte e derivati bovini, Latte e deriv. ovicaprini, Carne bovina, Carne suina, Avicoli, Ovicaprini, Conigli.* **Não há setor "Riso".**
- **⚠️ LEI 4 — a confiança do setor CEREAIS não é a confiança de quem planta ARROZ.** Nem para trigo duro, nem para milho, nem para arroz. O ICF "Cereali" mistura culturas com calendários, preços e problemas fitossanitários diferentes.
- Além disso, o ISMEA **não foi alcançado** nesta rodada (bloqueio geográfico de IP documentado). Nenhum valor corrente do ICF foi lido — nem de Cereais.
- O último índice ISMEA de preço ao produtor que existe com número lido é **Cereali 152,36** (base 2010=100, julho de 2025, +1,3% m/m, +3,0% a/a). **Isso não fala de arroz** — a lista de categorias do índice ISMEA (Cereali, Frutta, Olio d'oliva, Ortaggi, Semi oleosi, Tabacco, Vino…) **não tem arroz como categoria própria**.

**O que existe, e é outra coisa — declaração de parte interessada, não índice:**

`SOURCE`: Ente Nazionale Risi · `PUBLICATION_DATE`: **15/06/2026** · autor nomeado: **Natalia Bobba, Presidente do Ente Nazionale Risi** · `GEOGRAPHY`: Itália. Título da nota: *"La risicoltura italiana sta morendo!"*

> **"La crisi che sta stringendo d'assedio le nostre aziende agricole ha raggiunto livelli di guardia non più sostenibili."**

E, no corpo da nota: **"il comparto risicolo sta attraversando una situazione drammatica, segnata in particolare da listini in picchiata nelle principali Borse merci di Vercelli, Novara e Mortara"**; **"Una svalutazione resa ancora più insostenibile dal rincaro superiore al 50% dei costi di produzione (fertilizzanti, carburanti e agrofarmaci)"**; e o alerta de rotação de cultura: **"Se il riso smette di essere remunerativo, gli agricoltori saranno costretti a fare scelte drastiche, virando su colture alternative come mais o soia."**

**Isto é a voz do presidente do órgão nacional do arroz, com nome e data. NÃO é um índice, não tem amostra declarada, não tem metodologia publicada, e não pode ser tratado como medição de confiança.** Ver §5 para o confronto do número dos 50% com o índice medido.

---

## 5. PRESSÃO DE CUSTO

`SOURCE`: Eurostat, `APRI_PI_INQ` — *"Price indices of the means of agricultural production, input - quarterly data"* · `GEOGRAPHY`: **Itália** · `UNIT`: número índice, **2020 = 100**, índice nominal · `PUBLICATION_DATE`: **11/08/2026** (`updated` do dataset) · `REFERENCE_PERIOD`: até **2026-Q1** · cadência **trimestral**

| Rubrica | 2025-Q1 | 2025-Q4 | **2026-Q1** | y/y 2026-Q1 | vs base 2020 |
|---|---|---|---|---|---|
| **Bens e serviços consumidos na agricultura (Input 1)** | 130,9 | 129,6 | **132,7** | **+1,38%** | +32,7% |
| **Fertilizantes e corretivos** | 144,4 | 149,4 | **155,4** | **+7,62%** | **+55,4%** |
| — Fertilizantes nitrogenados | 150,6 | 157,1 | **168,4** | **+11,82%** | **+68,4%** |
| **Energia; lubrificantes** | 159,3 | 146,8 | **156,8** | −1,57% | **+56,8%** |
| — Combustíveis de motor | 145,3 | 136,4 | **155,7** | **+7,16%** | +55,7% |
| — Eletricidade | 184,6 | 164,1 | **164,1** | −11,11% | +64,1% |
| **Produtos fitossanitários (agrofarmaci)** | 124,4 | 122,9 | **125,5** | **+0,88%** | +25,5% |
| — Fungicidas e bactericidas | 134,8 | 133,9 | **138,4** | **+2,67%** | +38,4% |
| — Inseticidas e acaricidas | 122,6 | 123,8 | **125,1** | +2,04% | +25,1% |
| — Herbicidas | 118,4 | 114,8 | **117,0** | **−1,18%** | +17,0% |
| Sementes e material de plantio | 141,6 | 143,6 | **146,3** | +3,32% | +46,3% |

**Confronto honesto com a declaração do ENR:** a Presidente diz **"rincaro superiore al 50% dei costi di produzione (fertilizzanti, carburanti e agrofarmaci)"** sem declarar contra qual período. O índice medido pelo Eurostat é compatível com esse "+50%" **apenas se a base for 2020**: fertilizantes **+55,4%** e energia **+56,8%** contra 2020. **Contra o ano anterior o número é bem menor** (fertilizantes +7,62%, energia −1,57%). E **agrofarmaci não chega a 50% em nenhuma das duas leituras**: +0,88% no ano e +25,5% contra 2020 — dentro dos fitossanitários, quem subiu foi fungicida (+38,4% vs 2020) e quem *caiu* no ano foi herbicida (−1,18%). **Não sei qual base o ENR usou; a declaração não a informa.**

**⚠️ LEI 2:** este bloco é **trimestral e para em 2026-Q1**. Entre o fim do trimestre de referência e hoje (02/09/2026) passaram cinco meses. Não trate 132,7 como "o custo de hoje".

**⚠️ LEI 6 — preço da cultura não é lucro do produtor.** Nesta ficha, o preço do risone caiu entre 15% e 61% no ano conforme a variedade, **e ao mesmo tempo** o índice de insumos subiu 1,38% no ano e está 32,7% acima de 2020, com fertilizante nitrogenado +11,82% no ano. As duas coisas andam juntas e a margem do produtor **não está medida em lugar nenhum aqui** — nem o ENR nem a Comissão nem o Eurostat publicam custo por hectare de risicultura. **Margem: NÃO SEI.**

---

## 6. OUTLOOK — projeções, cada uma com o nome de quem a fez

> **Tudo neste bloco é projeção de terceiro, não é estado corrente. Nenhuma delas é do Sintonia.**

**a) Projeção do Ente Nazionale Risi (área):** `PUBLICATION_DATE` 22/07/2026 · projeção de área da safra 2026 em **233.500 ha (−0,5% vs 2025)**, com o aviso literal da própria folha: *"Stima al 21 luglio sulla base di 2.937 denunce che rappresentano il 79% della superficie del 2025"*. **Projeção sobre 79% de cobertura — pode mover quando os 21% restantes entrarem.**

**b) Projeção do JRC MARS (JRC, Comissão Europeia):** boletim *Crop monitoring in Europe*, `PUBLICATION_DATE` **24/08/2026**, título **"Exceptionally dry and hot weather threatens summer crops"**. Trechos literais: **"EU yield forecasts for all summer crops have been sharply reduced, falling below the five-year average by up to 14%"**; **"Limited availability of irrigation water and restrictions on its use further aggravated crop stress"**; a lista de regiões afetadas inclui **"northern and central Italy"**. **⚠️ Este boletim NÃO nomeia arroz.** É previsão agregada de "summer crops" no nível **UE**, e a menção ao norte da Itália é geográfica, não por cultura. **Usar o −14% como se fosse previsão de rendimento do arroz italiano seria inventar.**

**c) Sinal agronômico convergente, sem número:** `SOURCE` Ente Nazionale Risi, *"Il Risicoltore"* de setembro de 2026, `PUBLICATION_DATE` 14/08/2026 — a chamada do editorial diz que a edição trata **"il problema della siccità in risaia"**. Seca na lavoura de arroz, declarada pelo próprio órgão do setor. **Sem quantificação de perda.**

**d) Pressão de doença — capacidade ativa, valor não lido:** `SOURCE` Ente Nazionale Risi, `PUBLICATION_DATE` 10/08/2026: **"Dal 22 Giugno 2026 l'Ente Nazionale Risi ha attivato un servizio di emissione di bollettini di rischio di sviluppo del brusone del riso per le principali aree risicole italiane"**, com boletins regionais para Lombardia, Piemonte, Verona/Mantova, Ferrara e Oristano, o do Piemonte em parceria com Regione Piemonte – Settore Fitosanitario, IRES e FAN. **Existe boletim de risco de brusone (Pyricularia) por área. NÃO LI o nível de risco de nenhum deles nesta rodada — NÃO SEI se o risco está alto ou baixo em 2026.**

**e) Projeção de rotação de cultura, feita por parte interessada:** ENR/Natalia Bobba, 15/06/2026 — **"gli agricoltori saranno costretti a fare scelte drastiche, virando su colture alternative come mais o soia"**. É hipótese declarada pelo órgão do setor, **não é medição de intenção de plantio**.

---

## 7. TEMPERATURA DE MERCADO

# PRESSURED

> **⚠️ Isto é INTERPRETAÇÃO DO SINTONIA, não é fato observado.** Nenhuma fonte desta ficha publica uma "temperatura de mercado". A palavra acima é a leitura do Sintonia sobre os componentes abaixo; cada componente é fato com fonte, a síntese em uma palavra é opinião.

### « POR QUE »

| Componente | Seta | O fato que sustenta a seta |
|---|---|---|
| **Preço do risone ao produtor, ano contra ano** | **↓↓** | Pares exatos de 364 dias: Baldo −41,2%, Long B −41,1%, Selenio −25,6%, Carnaroli −19,9%, Arborio −15,1%, Gloria/S.Andrea −61,0%, média Japonica −23,6% (26/07/2026 vs 27/07/2025). Só CL007 subiu (+2,8%) |
| **Preço dentro da campanha 2025/26** | **↓** | Média Japonica de €565,46 (09/11/2025) para €441,90 (26/07/2026): **−21,9%** do pico |
| **Preço semana contra semana** | **→** | Baldo, Gloria, S.Andrea e Roma/CL145 todos a 0,0% entre 26/07/2026 e 23/08/2026; Broken parado em €430,00 desde 28/06/2026 |
| **Liquidez / formação de preço** | **↓↓** | Vercelli 01/09/2026: **todos os risoni `n.q.`**; Vercelli 25/08/2026 e Novara 27/07/2026: **todas as cotações marcadas "nominale"**; Novara e Mortara sem novo listino desde julho; cotação de arroz beneficiado eliminada em Vercelli (delibera 18 de 27/02/2025) e Novara (listino 11 de 17/03/2025) **"per l'irrilevanza degli scambi"** |
| **Estoque na mão do produtor** | **↑↑** | 117.432 t em 25/08/2026 contra 72.352 t na mesma data de 2025 = **+62,3%**; transferido 91,86% contra 94,89% um ano antes |
| **Importação de países terceiros** | **↑** | 216.180 t contra 189.378 t = +14,2%, puxada por Lungo B (+17.699 t) — **oferta somando, não demanda medida** |
| **Entregas para a UE** | **↓** | 350.838 t contra 383.341 t = **−8,5%** (até 31/05/2026) |
| **Exportação para países terceiros** | **→** | 131.915 t contra 130.975 t = +0,7% |
| **Área plantada 2026** | **→** (com o miolo trocado) | Total 233.500 ha, **−0,5%**; mas TONDO **+36,5%**, MEDIO **−47,5%**, ROMA-BALDO **−40,1%**, CARNAROLI **+18,1%** |
| **Rendimento (última safra fechada)** | **↓** | 2025: 6,00 t/ha contra 6,41 t/ha em 2024 = **−6,3%** |
| **Custo de insumo** | **↑** | Input 1 em 132,7 (2026-Q1), **+1,38% a/a**; fertilizante **+7,62% a/a**, nitrogenado **+11,82% a/a**; fitossanitário +0,88% a/a, mas fungicida **+2,67% a/a** |
| **Clima na safra em curso** | **↓** | JRC MARS 24/08/2026: **"Exceptionally dry and hot weather threatens summer crops"**, com "northern and central Italy" na lista e **"Limited availability of irrigation water"** — **projeção da UE para culturas de verão, não para arroz** |
| **Confiança do produtor** | **NÃO MEDIDA** | Não existe ICF para arroz; ISMEA não alcançado; só há declaração nomeada do ENR |
| **Margem do produtor** | **NÃO MEDIDA** | Nenhuma fonte desta ficha publica custo por hectare de risicultura |

**A leitura em uma frase:** preço bem abaixo do ano passado e travado nas últimas semanas, praça sem cotar ou cotando só na base nominal, estoque na mão do produtor 62% maior que um ano atrás, importação subindo e entrega para a UE caindo, custo de fertilizante em alta e clima seco declarado. Todos os componentes medidos apontam para o mesmo lado — por isso **PRESSURED**, e não MIXED SIGNALS. **A palavra é do Sintonia; os treze fatos acima são das fontes.**

---

## 8. O QUE ISTO NÃO AUTORIZA A DIZER

1. **Não autoriza dizer que a confiança do produtor de arroz italiano caiu.** Não existe índice de confiança para a cultura arroz. O ISMEA publica ICF para "Cereali" — e "Cereali" não é arroz (o arroz nem aparece na lista de setores do ISMEA). O que existe é uma declaração do presidente do ENR, com nome e data, que é fala de parte interessada.
2. **Não autoriza dizer "o preço do arroz caiu 27,8% em agosto".** Os −27,8% da média Japonica entre 26/07 e 23/08/2026 são **troca de cesta** (de 11 para 4 variedades cotadas), não movimento de preço. Nenhuma variedade individual mudou de preço nessas semanas.
3. **Não autoriza dizer que o mercado italiano de arroz está "parado" ou "morto" só porque as praças estão `n.q.`.** A ausência de cotação em 01/09/2026 é **pausa de fim de campanha** (a campanha comercial termina em 31/08). Confundir pausa de calendário com colapso de mercado é erro de leitura.
4. **Não autoriza dizer que a importação subindo 14,2% prova que a demanda italiana por arroz cresceu.** Ver §3.3: pelo menos quatro explicações são compatíveis com o mesmo número, e nenhuma foi isolada por esta ficha. O grosso é Lungo B e Basmati, categorias em que a Itália é estruturalmente deficitária.
5. **Não autoriza dizer que o produtor de arroz está perdendo dinheiro, nem quanto.** Preço caindo e custo subindo é o que os índices mostram; **margem por hectare não está medida** em nenhuma fonte desta ficha. Preço baixo de cultura não é prejuízo comprovado do produtor, do mesmo jeito que preço alto não seria lucro.
6. **Não autoriza usar o "−14%" do JRC MARS como previsão de safra de arroz italiano.** É previsão da **UE**, para **"all summer crops"** em agregado, e o boletim **não nomeia arroz**.
7. **Não autoriza usar o "rincaro superiore al 50%" como custo medido.** É declaração sem base declarada; o índice medido dá +1,38% no ano e +32,7% contra 2020 no agregado de insumos, e o item "agrofarmaci" não chega a 50% em nenhuma leitura.
8. **Não autoriza comparar mín/máx entre Vercelli, Novara e Mortara.** Os estágios comerciais são diferentes e estão escritos em cada listino ("franco azienda di produzione, pagamento 60 gg." em Novara; "franco partenza, pronta consegna" em Mortara; "al netto di... mediazione e diritto di contratto E.N.R." em Vercelli).
9. **Não autoriza tratar os quatro fluxos de comércio como o mesmo recorte.** Importação/exportação de terceiros vão a 31/08/2026; compras/entregas UE param em 31/05/2026.
10. **Não autoriza tratar o estoque industrial como total do país.** A folha declara literalmente 171 operadores de 266 — 64% de cobertura.
11. **Não autoriza tratar a área 2026 como número final.** É estimativa sobre 79% da área de 2025.
12. **Não autoriza dizer que os preços de arroz beneficiado italiano "sumiram" ou "estão zerados".** Eles pararam em 05/01/2025 porque duas Camere di Commercio **deliberaram encerrar a coleta** por irrelevância de trocas. Série descontinuada por decisão administrativa ≠ mercado em zero.
13. **Não autoriza nenhuma previsão comercial.** Nada aqui diz o que a ADAMA (ou qualquer empresa) vai vender, que share terá, quanto o distribuidor tem em estoque, nem se o produtor vai comprar defensivo. **Nada nesta ficha mede intenção de compra de insumo.** A única ponte agronômica visível é a existência de boletins de risco de brusone por área — e **o nível de risco de 2026 não foi lido**.
14. **Não autoriza nota de 0 a 100, nem "mercado quente".** A temperatura é uma palavra qualitativa e é interpretação declarada.

---

## Arquivos de evidência gravados nesta rodada

Todos em `C:\eame-sintonia\.tmp\riso\`:

- `C:\eame-sintonia\.tmp\riso\rice_prices_IT.json` — 6.108.629 bytes, 20.846 registros, EC Agri-food Data Portal, `rice/prices`, IT, 09/07/2000 a 30/08/2026
- `C:\eame-sintonia\.tmp\riso\rice_latest.json` — 93 séries (estágio × tipo × variedade) com última cotação, anterior, ano-antes e contagem de observações
- `C:\eame-sintonia\.tmp\riso\probe_production.json` — EC `rice/production`, IT, 2006–2025 (área, risone, equivalente beneficiado)
- `C:\eame-sintonia\.tmp\riso\superfici2026.pdf` — ENR, estimativa de área 2026 por grupo varietal, 22/07/2026
- `C:\eame-sintonia\.tmp\riso\trasferimenti.pdf` — ENR, transferências e sobras junto aos produtores, 25/08/2026
- `C:\eame-sintonia\.tmp\riso\rimanenze_ind.pdf` — ENR, estoques na indústria, dados a 31/07/2026
- `C:\eame-sintonia\.tmp\riso\import_italia.pdf` · `export_terzi.pdf` · `acquisti_ue.pdf` · `consegne_ue.pdf` — ENR, comércio, campanha 2025/2026
- `C:\eame-sintonia\.tmp\riso\vercelli_01set2026.pdf` · `vercelli_25ago2026.pdf` · `novara_27lug2026.pdf` · `mortara.csv` — listini de praça
- `C:\eame-sintonia\.tmp\riso\mk_ue.pdf` (preços comunitários, 04/08/2026) · `mk_intl.pdf` (cotações internacionais, 26/08/2026)
- `C:\eame-sintonia\.tmp\riso\es_inq.json` — Eurostat `APRI_PI_INQ`, Itália, 2024-Q2 a 2026-Q1
- `C:\eame-sintonia\.tmp\riso\news_morendo.html` — ENR, declaração da Presidente, 15/06/2026
- `C:\eame-sintonia\.tmp\riso\build_latest.py` — script que gera `rice_latest.json` (agrupa por estágio × tipo × variedade, ordena por data-fim, calcula anterior e ano-antes)

**Rota programática confirmada e reaplicável:** `https://www.ec.europa.eu/agrifood/api/rice/prices?memberStateCodes=IT` e `.../rice/production?memberStateCodes=IT` respondem HTTP 200 sem chave. **Os endpoints `rice/balance`, `rice/trade`, `rice/tradeImports`, `rice/tradeExports` e `rice/areaYield` retornam HTTP 404** — para balanço e comércio a rota é o ENR (PDF), não a API.