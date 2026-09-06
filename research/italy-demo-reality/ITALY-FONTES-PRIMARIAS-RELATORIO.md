# RELATÓRIO — CAMADA UE × PORTFÓLIO ADAMA ITÁLIA × RESISTÊNCIA GIRE

> **LEITOR — este documento fala dos 90 pares, que NÃO são o leitor canônico da casa.**
> O leitor canônico é `IT-ROTULOS-PARES-V3` (`data/samples/IT-ROTULOS-V1/`), de 2026-09-04:
> `it_rotulo_parser/3.4.0`, portão `IT-ROTULOS-PORTAO-V1 = PASS` contra gabarito de 30
> rótulos lido à mão, **128 rótulos com par** contra os 19 daqui. Os 90 pares de 2026-08-30
> ficam como `LEGACY_READER / HISTORICAL_INPUT`, `CANONICAL_AUTHORITY = NO`.
> `OLDER_SMALLER_READER != CANONICAL_READER`.


**Data do relatório:** 2026-09-02 · **Papel:** crítico de completude da rodada de leitura de fontes primárias

**Fontes usadas, com o que cada uma é:**

| Fonte | O que é | Estado |
|---|---|---|
| CELEX **32026R1826** (28/07/2026) | ato UE, extensão de períodos de aprovação | lido no corpo; **re-buscado e reconferido por mim** em `eur-lex.europa.eu` (HTTP 200, 387.220 bytes) |
| CELEX **32026R1421** (30/06/2026) | ato UE, extensão de períodos de aprovação | lido no corpo; **re-buscado e reconferido por mim** (HTTP 200, 365.704 bytes) |
| CELEX **32024R1206** (29/04/2024) | ato UE, tau-fluvalinate e bupirimate | lido em rodada anterior do acervo; **não reconferido por mim nesta rodada** |
| `C:\eame-sintonia\.wfaudit.json` (= `data/samples/IT-T4-001/ITALY-ADAMA-REGULATORY-INTELLIGENCE.json`) | 163 registros ADAMA Itália, Ministero della Salute, versão `PROD_FTS_6_20260824`, `AS_OF 2026-08-30` | lido e recontado |
| `C:\eame-sintonia\data\samples\IT-REGUA\IT-ADAMA-EU-ACTIVE-SUBSTANCE-V1.json` | cruzamento 53 substâncias × 89 atos UE (título) | lido |
| `C:\eame-sintonia\data\samples\IT-CIENCIA\IT-GIRE-RESISTENCIA-V1.json` | índice GIRE/CNR de espécies com resistência confirmada | lido |
| 9 fichas GIRE por espécie | detalhe com ano e regiões | recebidas nesta rodada (a de *Conyza* chegou truncada) |
| `C:\eame-sintonia\data\samples\PIEMONTE-FD\` (8 PDFs + textos) | lotta obbligatoria flavescenza dorata 2026 | lido |

**Quatro correções que eu produzi nesta rodada, antes das tabelas:**

1. **FOSETYL estava marcado como "sem ato na janela" e tem ato.** O título de 32026R1826 nomeia `fosetyl`, e o Anexo traz: *"in the sixth column, expiration of approval, of row 131, Fosetyl, the date is replaced by '31 January 2028'"*. São **5 registros ADAMA IT** com FOSETYL-ALUMINIUM que estavam fora da leitura. Ressalva: o ato escreve **"Fosetyl"**; o registro italiano escreve **"FOSETYL-ALUMINIUM"**. Se é a mesma entrada do Anexo do Reg. 540/2011 — **NÃO SEI**; casamento de nome não é prova de identidade de substância.
2. **O estado da avaliação de risco de 5 das 6 substâncias do ato 1421 não é o que a leitura afirmou.** A frase que sustenta `NOT_FINALISED` — *"The rapporteur Member State has not finalised the risk assessment pursuant to Article 11"* — **não aparece** no ato 1421 para cymoxanil, clethodim, tebuconazole, metaldehyde nem lambda-cialotrina. Ela aparece, nesse ato, para benzovindiflupyr, cycloxydim, dazomet e metsulfuron-methyl. Detalhe substância a substância na Tabela 1B.
3. **O ato 1826 trata "Metalaxyl" (linha 304 → 30 June 2029). O portfólio ADAMA IT tem METALAXYL-M.** São denominações diferentes, e o cruzamento do acervo casou METALAXYL-M com outros dois atos (32026R1353 e 32024R1718), não lidos. **Não atribuí 30/06/2029 aos 2 produtos ADAMA.**
4. **O arquivo GIRE do acervo declara `ESPECIES_TOTAL: 22` e o array tem 23 espécies.** Qual dos dois bate com o site do GIRE: **NÃO SEI** — não abri o site nesta rodada.

---

## 1 · SUBSTÂNCIAS ATIVAS COM DATA DE EXPIRAÇÃO DA APROVAÇÃO UE

### 1A · Data lida no corpo do ato — ordenada da mais próxima para a mais distante

⚠️ = data anterior a 01/01/2028.

| # | Data UE | Substância | Registros ADAMA IT | Avaliação de risco NÃO FINALIZADA? | Anexo | Ato |
|---|---|---|---|---|---|---|
| 1 | **2027-01-31** ⚠️ | TAU-FLUVALINATE | **7** | **SIM** (fórmula do Art. 11 presente) | Parte A, linha 328 | 32024R1206 |
| 2 | **2027-01-31** ⚠️ | BUPIRIMATE | **5** | **SIM** (mesma lista) | Parte A, linha 330 | 32024R1206 |
| 3 | **2027-07-31** ⚠️ | PIRIMICARB | **6** | NÃO — conclusão da EFSA já adotada em 25/09/2024 | Parte A, linha 124 | 32026R1826 |
| 4 | **2027-09-30** ⚠️ | PHENMEDIPHAM | **2** | NÃO — conclusão atualizada adotada em 30/09/2025 | Parte A, linha 88 | 32026R1826 |
| 5 | **2027-09-30** ⚠️ | FLUDIOXONIL | **1** | NÃO — conclusão adotada em 25/09/2024 | Parte A, linha 161 | 32026R1826 |
| 6 | **2027-11-30** ⚠️ | CYMOXANIL | **6** | NÃO pela fórmula do Art. 11; EFSA esperava concluir até 31/05/2026 | Parte A, linha 263 | 32026R1421 |
| 7 | **2027-12-15** ⚠️ | CLETHODIM | **1** | NÃO pela fórmula do Art. 11; EFSA esperava concluir até 30/06/2026 | Parte A, linha 329 | 32026R1421 |
| 8 | 2028-01-31 | FOSETYL *(ADAMA IT: FOSETYL-ALUMINIUM)* | **5** | NÃO — conclusão atualizada adotada em 13/06/2025; novo mandato à EFSA em 22/04/2026 | Parte A, linha 131 | 32026R1826 |
| 9 | 2028-06-30 | CHLOROTOLURON | **1** | NÃO pela fórmula do Art. 11; informação de desregulação endócrina **pendente do requerente** | Parte A, linha 102 | 32026R1421 |
| 10 | 2028-07-31 | TEBUCONAZOLE | **5** | NÃO pela fórmula do Art. 11; **tabela de comentários pendente do Estado-Membro relator** | Parte A, linha 268 | 32026R1421 |
| 11 | 2028-10-15 | METALDEHYDE | **1** | NÃO pela fórmula do Art. 11; consulta pública estimada para começar em maio/2026 | Parte A, linha 340 | 32026R1421 |
| 12 | 2029-01-31 | LAMBDA-CYHALOTHRIN | **5** | NÃO pela fórmula do Art. 11; **relatório revisto pendente do Estado-Membro relator** | **Parte E**, linha 5 | 32026R1421 |
| 13 | 2029-05-31 | METAZACHLOR | **2** | **SIM** (fórmula do Art. 11 presente) | Parte A, linha 217 | 32026R1826 |

**Somas:** 47 vínculos substância–produto; **44 produtos distintos de 163 (27,0 %)**. Sob as 7 substâncias com data anterior a 2028: **27 produtos distintos**, sendo 12 fungicidas, 5 inseticidas, 4 inseticidas-acaricidas, 3 aficidas e 3 herbicidas.

**Lambda-cialotrina é a única das 13 declarada "candidate for substitution" pela fonte lida** — está na **Parte E** do Anexo, e o ato diz literalmente por quê (citação em 1B). Para as outras 12, "candidate for substitution" **NÃO SEI por estas fontes**: a expressão não aparece nenhuma vez no ato 1826 (0 ocorrências, conferido por mim) e, no ato 1421, aparece 6 vezes, sempre referida a metsulfuron-methyl, lambda-cialotrina e benzovindiflupyr. Tebuconazol e substituição **não aparecem na mesma frase** em 1421 (testado).

### 1B · A frase literal que sustenta cada data e cada estado

| Substância | Citação da DATA (Anexo, verbatim) | Citação do ESTADO (Considerando, verbatim) |
|---|---|---|
| TAU-FLUVALINATE | *"ANEXO, linha 328: a data de expiracao da aprovacao de tau-fluvalinate passa a ser 31 January 2027"* (registro do acervo, ato 2024/1206) | *"the risk assessment pursuant to Article 11 of Implementing Regulation (EU) No 844/2012 has not yet been finalised by the respective rapporteur Member States"* |
| BUPIRIMATE | *"ANEXO, linha 330: bupirimate passa a ser 31 January 2027"* (registro do acervo) | mesma frase acima, mesma lista |
| PIRIMICARB | *"in the sixth column, expiration of approval, of row 124, Pirimicarb, the date is replaced by '31 July 2027'"* | *"On 25 September 2024, the Authority adopted its conclusion and communicated it to the applicant, the Member States and the Commission."* + *"As additional time is necessary to deliver the opinion of that Committee and for the Commission to adopt the ensuing risk management decisions, the duration of the extension of the approval period should be set at 9 months, until 31 July 2027."* |
| PHENMEDIPHAM | *"...of row 88, Phenmedipham, the date is replaced by '30 September 2027'"* | *"On 30 September 2025, the Authority adopted its updated conclusion and communicated it to the applicant, the Member States and the Commission."* |
| FLUDIOXONIL | *"...of row 161, Fludioxonil, the date is replaced by '30 September 2027'"* | *"On 25 September 2024, the Authority adopted its conclusion and communicated it to the applicant, the Member States and the Commission."* |
| CYMOXANIL | *"...of row 263, Cymoxanil, the date is replaced by '30 November 2027'"* | *"The Authority expects to complete the evaluation and to finalise its conclusion for cymoxanil by 31 May 2026, and as the Commission will need time to adopt the ensuing risk management decisions, the duration of the extension of the approval period should be set at 15 months and 15 days, until 30 November 2027."* |
| CLETHODIM | *"...of row 329, Clethodim, the date is replaced by '15 December 2027'"* | *"The Authority expects to complete the evaluation and to finalise its conclusion for clethodim by 30 June 2026..."* |
| FOSETYL | *"...of row 131, Fosetyl, the date is replaced by '31 January 2028'"* | *"on 22 April 2026, the Commission submitted a mandate to the Authority to reevaluate together with the rapporteur Member State some of the information available in the application and to update its conclusion, which is expected by the end of April 2027."* |
| CHLOROTOLURON | *"...of row 102, Chlorotoluron, the date is replaced by '30 June 2028'"* | *"...pursuant to Article 13(3a) ... to be submitted by the applicant by 18 December 2026 and the submission is pending. As the Authority estimates that it will need 120 days after receiving the revised draft renewal assessment report to complete the evaluation..."* |
| TEBUCONAZOLE | *"...of row 268, Tebuconazole, the date is replaced by '31 July 2028'"* | *"The submission of the completed reporting table of the collated comments from the public consultation by the rapporteur Member State is pending."* |
| METALDEHYDE | *"...of row 340, Metaldehyde, the date is replaced by '15 October 2028'"* | *"The rapporteur Member State and the Authority estimate that the public consultation on the draft renewal assessment report will start in May 2026."* |
| LAMBDA-CYHALOTHRIN | *"2. Part E is amended as follows: ... (3) in the sixth column, expiration of approval, of row 5, Lambda-Cyhalothrin, the date is replaced by '31 January 2029'"* | *"Commission Implementing Regulation (EU) 2016/146 renewed the approval of that active substance as a candidate for substitution until 31 March 2023 and included it in Part E of the Annex..."* + *"The submission of the revised draft renewal assessment report by the rapporteur Member State is pending."* |
| METAZACHLOR | *"...of row 217, Metazachlor, the date is replaced by '31 May 2029'"* | *"The rapporteur Member State has not finalised the risk assessments pursuant to Article 11 of Implementing Regulation (EU) No 844/2012 and estimates that it will be able to submit the draft renewal assessment report to the Authority by the end of December 2026."* |

Duas frases valem para blocos inteiros e precisam ficar junto de qualquer data acima:

> **Incerteza declarada pelo próprio legislador** (1826 cons. 21 e 1421 cons. 21, texto idêntico): *"Given that the case-by-case assessment of the time needed to complete each renewal procedure is based on estimates, account should be taken of this degree of uncertainty."*

> **O prazo pode não bastar** — 1421 cons. 42 nomeia **lambda-cialotrina, metaldeído e tebuconazol** (entre outros): *"the Authority, in consultation with the Member States, may still request additional information from the applicants pursuant to Article 13(3a) ... The extension periods proposed for these active substances do not include any additional time that might be necessary to provide and evaluate that information."* O 1826 cons. 39 diz o mesmo e nomeia **metazachlor**.

### 1C · Quais registros dependem de cada substância

| Substância | Registros ADAMA Itália |
|---|---|
| TAU-FLUVALINATE (7) | KLARTAN 20 EW · TAU AL 240 EW · MAVRIK SMART · KLARTAN SMART · MAVRIK EW · EVURE PRO · MAVRIK JET |
| BUPIRIMATE (5) | NIMROD · VERBUM EW · NIMROD 250 EW · TRINEX 250 EW · VINETO |
| PIRIMICARB (6) | PIRIMOR 50 · PIRIMOR 17,5 · APHOX · APHOX 50 · XINTECH 50 · MAVRIK JET |
| PHENMEDIPHAM (2) | CONTATTO 320 · CONTATTO DOUBLE SC |
| FLUDIOXONIL (1) | SEEDRON |
| FOSETYL-ALUMINIUM (5) | MOMENTUM · MOVER · VANGUARD · RIMENSIS · MOMENTUM PFNPE |
| CYMOXANIL (6) | DAUPHIN 45 · BADGER 45% WG · CARSON 45% WG · ANTERLEX · MOXYL MK · VANTEX |
| CLETHODIM (1) | ARRODIM |
| TEBUCONAZOLE (5) | CUSTODIA ULTRA · VINETO · SEEDRON · BLAISE ULTRA · MIRADOR TURBO |
| CHLOROTOLURON (1) | DICURAN PLUS |
| METALDEHYDE (1) | LUMA-KL |
| LAMBDA-CYHALOTHRIN (5) | LAMDEX EXTRA · FORZA · NINJA · DURAVIS · ELTIRA |
| METAZACHLOR (2) | SULTAN · CLORMET |

Dois produtos entram duas vezes por terem duas dessas substâncias: **MAVRIK JET** (tau-fluvalinate + pirimicarb), **VINETO** (bupirimate + tebuconazol) e **SEEDRON** (fludioxonil + tebuconazol).

### 1D · As outras 40 substâncias — data UE = NÃO SEI

**Com ato casado por título, ato NÃO lido (19).** Título casado não é ato lido: o título diz que existe ato, não diz a data nem o resultado.

| Substância | Registros | Ato(s) casado(s) por título |
|---|---|---|
| FOLPET | 13 | 32024R2198 |
| PENDIMETHALIN | 12 | 32024R2221 |
| CLODINAFOP | 10 | 32025R1489 |
| AZOXYSTROBIN | 5 | 32024R2781 |
| PROTHIOCONAZOLE | 5 | 32025R0787 |
| DIFLUFENICAN | 4 | 32025R2316 |
| IMAZAMOX | 4 | 32025R0099 |
| CAPTAN | 3 | 32024R2186 |
| FLUAZINAM | 3 | 32026R0372 · 32024R0324 |
| FLUROXYPYR | 3 | 32024R2781 |
| TEFLUTHRIN | 2 | 32024R2781 |
| DIFENOCONAZOLE | 2 | 32025R2316 |
| TERBUTHYLAZINE | 2 | 32024R2781 |
| PARAFFIN OIL (CAS 97862-82-3) | 2 | 32026R0870 · 32025R0787 |
| METALAXYL-M | 2 | 32026R1353 · 32024R1718 |
| PINOXADEN | 2 | 32026R0372 |
| PLANT OILS / RAPE SEED OIL | 1 | 32024R2221 |
| FLUXAPYROXAD | 1 | 32025R0787 |
| CHLORANTRANILIPROLE | 1 | 32024R2781 |

**Sem ato na janela consultada (21).** A janela foi 2024-01-01 a 2026-12-31, atos com "active substance" no título em inglês, `LIMIT 200` por ano. **Ausência de ato nessa janela não é prova de aprovação estável** — a decisão pode ser anterior a 2024, ou o título pode não conter a expressão procurada.

GLYPHOSATE (11) · CLOQUINTOCET MEXYL (10) · METAMITRON (9) · QUIZALOFOP-P-ETHYL (9) · BIFENOX (7) · PROPAQUIZAFOP (5) · NICOSULFURON (4) · FLORASULAM (3) · TRIBENURON (3) · ETHOFUMESATE (3) · SULCOTRIONE (2) · MESOTRIONE (2) · FLONICAMID (2) · MESOSULFURON-METHYL (2) · FENPROPIDIN (1) · IMAZALIL (1) · DICAMBA (1) · 2,4-D (1) · POTASSIUM PHOSPHONATES (1) · ISOXADIFEN ETHYL (1) · MEFENPYR DIETHYL (1).

---

## 2 · O QUE MUDOU NA LEITURA DE RISCO REGULATÓRIO DO PORTFÓLIO ITALIANO

**O que o acervo dizia, literalmente**, sobre os 6 produtos que nomeiam *Scaphoideus titanus* no rótulo:

> *"EXPIRY 2027-01-31. EXPIRY ≠ WITHDRAWAL: re-registro é rotina e RENEWAL_STATUS = NÃO SEI."*
> (`research/italy-demo-reality/ITALY-REGUA-RESULTADO-V0.md`, linha 395)

**Mudança 1 — a ressalva era verdadeira para uma camada só.** "Re-registro é rotina" descreve o registro **nacional do produto**, sob aprovação **europeia da substância** estável. Onze das 53 substâncias do portfólio italiano estão hoje, com ato lido, em **procedimento de renovação em curso**, e o próprio ato declara: *"the applications for the renewal of their approvals are currently being evaluated pursuant to Article 14 of Regulation (EC) No 1107/2009"* (1826 cons. 1 e 1421 cons. 1, texto igual). Não é o mesmo cenário. Continua valendo que **EXPIRY ≠ WITHDRAWAL** e que o resultado da renovação é **NÃO SEI** — o ato não decide: *"In case the Commission adopts a Regulation providing that the approval ... is not renewed... In case the Commission adopts a Regulation providing for the renewal..."* (1826 cons. 47 e 1421 cons. 44). São hipóteses de um regulamento **futuro**.

**Mudança 2 — a data nacional, em boa parte do portfólio, é a fronteira europeia antiga.** Isto era um caso isolado (tau-fluvalinate, 2027-01-31 nas duas camadas) e agora aparece **23 vezes**. Comparação entre a data anterior citada no considerando e a `EXPIRY` nacional do snapshot de 30/08/2026:

| Substância | Data UE ANTERIOR (citação literal do considerando) | `EXPIRY` nacional dos produtos | Produtos |
|---|---|---|---|
| CYMOXANIL + TEBUCONAZOLE | *"most recently by Commission Implementing Regulation (EU) 2023/1446 until 15 August 2026"* | **2026-08-15** | 8 |
| LAMBDA-CYHALOTHRIN | *"most recently by Implementing Regulation (EU) 2024/324 until 31 August 2026"* | **2026-08-31** | 5 |
| PHENMEDIPHAM | *"most recently by Commission Implementing Regulation (EU) 2025/99 until 30 September 2026"* | **2026-09-30** | 2 |
| FLUDIOXONIL | *"most recently by Commission Implementing Regulation (EU) 2025/787, both until 30 September 2026"* | **2026-09-30** | 1 (SEEDRON) |
| PIRIMICARB | *"most recently by Implementing Regulation (EU) 2025/99 until 31 October 2026"* | **2026-10-31** | 5 |
| METAZACHLOR | *"most recently by Implementing Regulation (EU) 2023/918, both until 31 October 2026"* | **2026-10-31** | 2 |
| FOSETYL | *"most recently by Implementing Regulation (EU) 2025/99, both until 31 October 2026"* | **2026-10-31** | 5 |
| METALDEHYDE / CLETHODIM | *"most recently by Implementing Regulation (EU) 2023/918 until 31 August 2026"* | **2026-08-31** | 2 |

**Por que isso importa em uma frase:** um leitor que só tivesse a coluna nacional veria 15 registros ADAMA IT com data já vencida em 02/09/2026 e leria "atraso administrativo italiano". Os 15 são exatamente produtos de substâncias cuja aprovação europeia foi prorrogada pelo Reg. 2026/1421, de 30/06/2026 — 8 de cymoxanil/tebuconazol (15/08/2026), 5 de lambda-cialotrina, 1 de metaldeído e 1 de cletodim (31/08/2026). **O mecanismo que liga uma data à outra não está escrito em nenhuma fonte que li** — o que eu tenho é a coincidência, contada. E há exceção dentro do próprio conjunto: DICURAN PLUS (clorotolurom) tem `EXPIRY` 2027-08-31 e a data UE anterior do clorotolurom era 15/08/2026. Não é regra fechada.

**Mudança 3 — existe uma terceira camada, regional, que já usa vocabulário da camada europeia.** O Piemonte tornou obrigatório o tratamento contra flavescência dourada em 2026 e listou as substâncias admitidas:

> *"2° TRATTAMENTO con una delle seguenti sostanze attive: ETOFENPROX, DELTAMETRINA, ESFENVALERATE, **LAMBDA-CIALOTRINA**, **TAU-FLUVALINATE**"*
> — *Insetticidi ammessi 2026*, `/web/media/48262/download`

E, no terceiro tratamento eventual:

> *"Non utilizzare sostanza attiva **candidata alla sostituzione**, se già utilizzata in precedenza."*

As duas substâncias ADAMA que aparecem nessa lista são justamente as duas com data UE mais próxima e/ou com condição especial: tau-fluvalinate 31/01/2027 com avaliação de risco não finalizada, e lambda-cialotrina 31/01/2029 **na Parte E, aprovada como candidata à substituição** pelo Reg. 2016/146. Qual é o status de substituição do tau-fluvalinate: **NÃO SEI** — nenhuma das fontes lidas responde.

**O que NÃO mudou:** nada aqui decide renovação; nada aqui fala de venda, de estoque, de disponibilidade ou de recomendação agronômica. O próprio arquivo do portfólio lista o que ele não prova: *"venda", "disponibilidade comercial", "presença no catálogo", "recomendação agronômica", "que a renovação não tenha ocorrido"*.

---

## 3 · LISTA DE RESISTÊNCIA ITALIANA — GIRE (CNR)

Fonte: **GIRE — Gruppo Italiano di lavoro sulla Resistenza agli Erbicidi**, hospedado pelo CNR, lido em `http://gire.mlib.cnr.it` (o host com TLS, `gire.ipsp.cnr.it`, tem certificado expirado e recusa conexão).

### 3A · Fichas lidas ficha a ficha (9 de 23 espécies do índice)

| Espécie | Mecanismo, como a ficha nomeia | Cultura declarada | Regiões | 1º caso | Cruzada / múltipla |
|---|---|---|---|---|---|
| *Alisma plantago-aquatica* | **ALS (gruppo B)** | riso | Piemonte, Lombardia | **1994** | **cruzada**: sulfonilureias + triazolopirimidinas |
| *Ammania coccinea* | **ALS (gruppo B)** | riso | Piemonte, Lombardia | **2018** | **cruzada**: sulfonilureias + triazolopirimidinas |
| *Avena sterilis* | **ACCasi (gruppo A)** e, em parte das populações, **ALS** | grano duro e tenero | Basilicata, Puglia, Sicilia + casos esporádicos em Veneto, Emilia Romagna, Marche, Abruzzo, Lazio | **1992** (ano declarado para o bloco; se vale também para a ALS, a ficha não diz) | **MÚLTIPLA — a única do lote com a palavra** |
| *Amaranthus retroflexus* | ficha **não nomeia o mecanismo no corpo**; cita a família química (sulfonilureias, thifensulfuron-methyl). Rótulo do mapa: "ALS" | soia | Veneto, Emilia Romagna, Friuli Venezia Giulia | **2003** | não declarada — NÃO SEI |
| *Amaranthus tuberculatus* | ficha **não nomeia o mecanismo**; sulfonilureias (tifensulfuron-metile) + imidazolinonas (imazamox) | soia | Veneto, Friuli Venezia Giulia, Emilia Romagna | **2010** | **cruzada** |
| *Amaranthus hybridus* | ficha **não nomeia o mecanismo**; sulfonilureias (thifensulfuron-methyl) + imidazolinonas (imazamox) | soia | Veneto, Friuli Venezia Giulia | **2017** | **cruzada** |
| *Amaranthus palmeri* | **ALS (gruppo B)** | soia | Veneto | **2018** (na Itália) | para a Itália, não declarada — NÃO SEI |
| *Chenopodium album* | **Triazine (atrazina), gruppo C1** | **NÃO SEI** — a ficha não declara sistema de cultivo | Piemonte | **1982** | não mencionada — NÃO SEI |
| *Conyza canadensis* | rótulo do mapa: **EPSP**; "Sistema colturale: uliveto" | uliveto (e "colture arboree" na ecologia) | **NÃO SEI** — ficha truncada no material recebido | **NÃO SEI** — truncada | NÃO SEI |

**Citações literais que sustentam as linhas acima:**

- *Alisma*: *"Tipo di resistenza: popolazioni resistenti agli erbicidi inibitori dell'ALS (gruppo B) con resistenza incrociata alle solfoniluree e alle triazolopirimidine. Primo caso accertato nel 1994. Regioni interessate: Piemonte, Lombardia."*
- *Ammania*: *"popolazioni resistenti agli erbicidi inibitori dell'ALS (gruppo B) con resistenza incrociata alle solfoniluree"* · *"Primo caso accertato nel 2018."*
- *Avena sterilis*: *"Resistenza agli erbicidi inibitori dell'ACCasi (gruppo A)"* · *"Primo caso accertato nel 1992."* · **múltipla:** *"Alcune popolazioni risultano avere resistenza multipla agli inibitori dell'ALS."*
- *A. retroflexus*: *"In Italia sono state segnalate alcune popolazioni resistenti alle solfoniluree (thifensulfuron-methyl). Primo caso accertato nel 2003."* — repare em **"alcune popolazioni"**, não a espécie inteira.
- *A. tuberculatus*: *"popolazioni cross-resistenti alle solfoniluree (tifensulfuron-metile) ed agli imidazolinoni (imazamox)"* · *"Primo caso nel 2010"*.
- *A. hybridus*: *"popolazioni cross-resistenti alle solfoniluree (thifensulfuron-methyl) ed agli imidazolinoni (imazamox). Primo caso 2017."*
- *A. palmeri*: *"Il primo caso di resistenza agli erbicidi inibitori dell'ALS (gruppo B) è stato accertato nel 2018 in Veneto."* ⚠️ **Não confundir países:** a mesma ficha diz *"In America, dove il primo caso di resistenza risale al 1989 ... ha sviluppato resistenza ad erbicidi con diversi meccanismi d'azione"* — 1989 é dos Estados Unidos, e quais mecanismos: NÃO SEI.
- *Chenopodium album*: *"Popolazioni resistenti alle Triazine (atrazina) (gruppo C1). Primi casi accertati: 1982."* — plural, "primi casi", e é o ano mais antigo do conjunto.

### 3B · Índice completo do GIRE — 23 espécies, mecanismo e cultura do mapa publicado

| Espécie | Cultura do mapa | Mecanismo(s) | Ficha lida? |
|---|---|---|---|
| *Alisma plantago-aquatica* | riso | ALS | sim |
| *Amaranthus hybridus* | — ficha sem mapa publicado | — | sim |
| *Amaranthus palmeri* | — ficha sem mapa publicado | — | sim |
| *Amaranthus retroflexus* | dicotiledoni estive | ALS | sim |
| *Amaranthus tuberculatus* | — ficha sem mapa publicado | — | sim |
| *Ammania coccinea* | — sem mapa | — | sim |
| *Avena sterilis* | frumento | **ACCasi + ALS** | sim |
| *Chenopodium album* | — sem mapa | — | sim |
| *Conyza canadensis* | colture arboree | **EPSP** | parcial |
| *Cyperus difformis* | riso | ALS | **não** |
| *Cyperus esculentus* | — sem mapa | — | **não** |
| *Digitaria sanguinalis* | dicotiledoni estive | ACCasi | **não** |
| *Echinochloa crus-galli* | **mais** | ALS | **não** |
| *Echinochloa crus-galli* | **riso** | **ACCasi + ALS + propanile** | **não** |
| *Eleusine indica* | — sem mapa | — | **não** |
| *Lolium* spp. | frumento | **ACCasi + ALS** | **não** |
| *Lolium* spp. | medica | ACCasi | **não** |
| *Lolium* spp. | colture arboree | **EPSP** | **não** |
| *Oryza sativa* (riso crodo) | riso | ALS | **não** |
| *Panicum dichotomiflorum* | — sem mapa | — | **não** |
| *Papaver rhoeas* | frumento | **ALS + 2,4-D** | **não** |
| *Phalaris paradoxa* | frumento | ACCasi | **não** |
| *Schoenoplectus mucronatus* | riso | ALS | **não** |
| *Sinapis arvensis* | frumento | ALS | **não** |
| *Solanum nigrum* | — sem mapa | — | **não** |
| *Sorghum halepense* | dicotiledoni estive | ACCasi | **não** |

⚠️ **Espécie sem mapa publicado não é espécie sem resistência confirmada.** Cinco das nove fichas lidas (*A. hybridus*, *A. palmeri*, *A. tuberculatus*, *Ammania*, *Chenopodium*) estão marcadas "ficha sem mapa publicado" no índice **e declaram resistência com ano e região no corpo da ficha**.

### 3C · Resistências MÚLTIPLAS — o destaque pedido

**Uma única declaração literal de resistência múltipla em todo o material lido:**

> *"Alcune popolazioni risultano avere resistenza multipla agli inibitori dell'ALS."* — ficha *Avena sterilis*, sobre populações já resistentes a ACCasi (gruppo A), em grano duro e tenero. Em qual proporção e em quais regiões: **NÃO SEI**, a ficha não diz.

**Quatro declarações de resistência CRUZADA** (duas famílias químicas, e nas duas primeiras dentro do mesmo mecanismo ALS): *Alisma* e *Ammania* (sulfonilureias + triazolopirimidinas, em arroz); *A. hybridus* e *A. tuberculatus* (sulfonilureias + imidazolinonas, em soja).

**Quatro combinações espécie+cultura com dois ou mais mecanismos no índice de mapas** — *Avena sterilis* frumento (ACCasi+ALS), *Lolium* spp. frumento (ACCasi+ALS), *Echinochloa crus-galli* riso (ACCasi+ALS+propanile), *Papaver rhoeas* frumento (ALS+2,4-D). ⚠️ **Isto é rótulo de mapa, não declaração de múltipla.** Dois mapas para a mesma espécie na mesma cultura significam dois mapas; que a **mesma população** carregue os dois mecanismos, o índice não afirma.

**A afirmação mais forte do conjunto**, e é da autoridade nacional do assunto:

> *"Il GIRE conferma la presenza di popolazioni di riso crodo e di giavoni resistenti a tutti gli inibitori dell'ACCasi utilizzati in riso."* — *Il Risicoltore*, 2025, LXVII (6), junho de 2025.
> Em que proporção da área e em quais províncias: **NÃO SEI** — o próprio acervo registra que a fonte não diz.

---

## 4 · ONDE A RESISTÊNCIA TOCA O PORTFÓLIO ADAMA

**Formato único permitido, e nada além dele.** Cada linha é: o que a autoridade publica + quantos registros ADAMA italianos **declaram aquele grupo no rótulo**. Declarar o grupo é um fato de rótulo. Não é eficácia, não é falha, não é oportunidade.

**Contagens-base de rótulo** (163 registros; 70 declaram grupo, 68 não declaram, 25 ficaram ilegíveis por codificação de fonte — **os números abaixo são piso, não total**):

| Grupo declarado no rótulo | Registros ADAMA IT |
|---|---|
| ACCase — "HRAC 1 (A)" (20) + "HRAC 1" (2) | **22** |
| ALS — "HRAC B" (8) + "HRAC 2" (4) + "HRAC 2 (B)" (2) | **14** |
| EPSP — "HRAC G" | **7** (há 11 registros com glifosato; 4 não declaram grupo) |
| PSII/triazinas — "HRAC 5 (C1)" (2) + "HRAC 5" (1) | **3** |

### As frases que este material autoriza

1. A autoridade nacional publica **resistência confirmada ao mecanismo ALS** em *Alisma plantago-aquatica* (1994, Piemonte e Lombardia), *Ammania coccinea* (2018, Piemonte e Lombardia), *Cyperus difformis*, *Schoenoplectus mucronatus*, *Oryza sativa* (riso crodo) e *Echinochloa crus-galli*, **na cultura arroz**; a ADAMA tem **2 registros italianos que declaram o grupo ALS e citam arroz no rótulo** — POSTSCRIPT 80 e POSTSCRIPT 80 XL, ambos "HRAC 2", imazamox.
2. A autoridade nacional publica **resistência confirmada ao mecanismo ACCase** em *Echinochloa crus-galli* **na cultura arroz**, e confirmou em junho/2025 populações de riso crodo e giavoni *"resistenti a tutti gli inibitori dell'ACCasi utilizzati in riso"*; a ADAMA tem **1 registro italiano que declara o grupo ACCase e cita arroz** — HIGHCARD, "HRAC 1 (A)". Há outros 5 registros que citam arroz com graminicida propaquizafop (AGIL, SHOGUN, FALCON MK, ZETROLA, LIGA) cujo rótulo, na leitura, **não declara grupo** — para esses o grupo é NÃO SEI.
3. A autoridade nacional publica **resistência confirmada ao mecanismo ACCase** em *Avena sterilis* (1992; Basilicata, Puglia, Sicilia, e casos esporádicos em cinco outras regiões), *Lolium* spp. e *Phalaris paradoxa*, **na cultura trigo**; a ADAMA tem **13 registros italianos que declaram o grupo ACCase e citam trigo** — 10 de clodinafop (TOPIK 240 EC, TOPIK 80 EC, VIP, TRACE, RAVENAS, VIP 80 EC, CELIO 80 EC, CELIO, HAWK, MAKURI), HIGHCARD, EDAPTIS e MEZAYO.
4. A autoridade nacional publica **resistência confirmada ao mecanismo ALS** em *Lolium* spp., *Papaver rhoeas*, *Sinapis arvensis* e — em parte das populações — *Avena sterilis*, **na cultura trigo**; a ADAMA tem **6 registros italianos que declaram o grupo ALS e citam trigo** — CLEAVE, TRIMMER 50 WG, KORAL 50 WG, KIKKO 50 WG, EDAPTIS, MEZAYO.
5. A autoridade nacional publica **resistência confirmada ao mecanismo EPSP** em *Conyza canadensis* e *Lolium* spp., **em culturas arbóreas** (a ficha de *Conyza* declara "Sistema colturale: uliveto"); a ADAMA tem **7 registros italianos que declaram o grupo EPSP (HRAC G) e citam olival, videira e macieira no rótulo** — GLIPHOGAN TOP CL, TAIFUN MK CL, HERBITOTAL CL e as quatro versões PFNPE.
6. A autoridade nacional publica **resistência confirmada ao mecanismo ALS** em *Echinochloa crus-galli* **na cultura milho**; a ADAMA tem **8 registros italianos que declaram o grupo ALS e citam milho** — NICOGAN V.O., NICAMACK V.O., RENDER V.O., PYXIDES WG, DAVAI, EARLEX, POSTSCRIPT 80, POSTSCRIPT 80 XL.
7. A autoridade nacional publica, nas fichas de **quatro espécies de *Amaranthus***, resistência confirmada a sulfonilureias e/ou imidazolinonas **com "Sistema colturale: soia"** (2003, 2010, 2017 e 2018; Veneto, Emilia Romagna, Friuli Venezia Giulia); a ADAMA tem **2 registros italianos que declaram o grupo ALS e citam soja** — DAVAI e EARLEX (imazamox). Ressalva de nomenclatura: duas dessas fichas nomeiam só a família química, e o mecanismo aparece apenas no rótulo do mapa ("Mappa (dicotiledoni estive) ALS").
8. A autoridade nacional publica **resistência confirmada a triazinas (atrazina, gruppo C1)** em *Chenopodium album* **no Piemonte, primeiros casos em 1982**, e a ficha **não declara em qual cultura**; a ADAMA tem **3 registros italianos que declaram grupo HRAC 5** — SULCOTREK e CHASER-S ("HRAC 5 (C1)", milho) e GOLTIX ("HRAC 5", beterraba). ⚠️ A equivalência entre a notação de letra (C1) do GIRE e a numérica (5) do rótulo **não está escrita em nenhuma das duas fontes** — é conversão minha, e precisa de verificação.

### Duas ressalvas que mudam a leitura das linhas acima

**a) "Cita a cultura no rótulo" é o vínculo mais fraco que existe.** O próprio arquivo define: `CROP_TERM_PRESENT` = *"a cultura aparece no rótulo; NÃO diz para qual alvo. Ampla e sem ligação."* Só **19 dos 163 registros (11,7 %)** têm alguma linha de uso autorizado extraída, e só 13 dessas 49 linhas trazem dose.

**b) O número "15 registros citam arroz" está contaminado.** A auditoria de pares mostrou que, em 4 dos 15 (GLIPHOGAN TOP CL PFNPE, HERBITOTAL CL PFNPE, SHAMAL MK PLUS CL PFNPE, TAIFUN MK CL PFNPE), a palavra "Riso" veio de **"Riso crodo"** — nome italiano de uma **planta daninha** dentro de uma lista de alvos, com o parêntese aberto antes do trecho guardado. Os registros que eu contei nas linhas 1 e 2 acima (POSTSCRIPT 80, POSTSCRIPT 80 XL, HIGHCARD) **não** são desses quatro. Nota factual e curiosa: o "riso crodo" que contaminou a leitura é exatamente a espécie que o GIRE lista com resistência ALS em arroz, e esses mesmos rótulos declaram como alvos *Lolium* sp., *Sorghum halepense*, *Avena* sp., *Cyperus* sp., *Amaranthus* sp., *Chenopodium* sp. e *Sinapis* sp. — sete gêneros da lista do GIRE. Isso é nível de **alvo declarado em rótulo**, não de cultura autorizada.

---

## 5 · O QUE FALTA

**Atos e camada europeia**
1. **32024R1206 não foi reconferido nesta rodada.** As datas de tau-fluvalinate (linha 328) e bupirimate (linha 330) vêm do registro do acervo, não da minha leitura da fonte. São 12 registros ADAMA IT com a data mais próxima da tabela.
2. **19 substâncias com ato casado por título e ato não lido** (Tabela 1D) — 74 vínculos substância–produto, incluindo os dois maiores blocos do portfólio, FOLPET (13) e PENDIMETHALIN (12).
3. **21 substâncias sem ato na janela** — janela limitada a 2024-2026, `LIMIT 200`/ano, título em inglês contendo "active substance". GLYPHOSATE (11 registros) está aqui: ato anterior a 2024 ou título com outra formulação **não seria encontrado**. Isso é limite de consulta, não ausência de ato.
4. **Identidade FOSETYL vs FOSETYL-ALUMINIUM** e **METALAXYL vs METALAXYL-M** — não verificadas. Os atos 32026R1353 e 32024R1718, que o cruzamento casou com METALAXYL-M, não foram lidos.
5. **Candidatura à substituição de 12 das 13 substâncias** — só lambda-cialotrina está documentada. Falta ler o **Reg. (UE) 2015/408** e a **Parte E do Anexo do Reg. 540/2011**. Sem isso, a regra do Piemonte *"Non utilizzare sostanza attiva candidata alla sostituzione, se già utilizzata in precedenza"* não pode ser aplicada ao portfólio.
6. **Data-calendário de entrada em vigor** — nenhum dos dois atos faz a conta. 1826: *"shall enter into force on the third day following that of its publication"*, publicado em 29.7.2026. 1421: *"on the twentieth day following that of its publication"*, data de publicação não conferida por mim.
7. **Se o registro italiano já atualizou as datas nacionais** depois dos atos de 30/06 e 28/07/2026 — o snapshot é `PROD_FTS_6_20260824`, `AS_OF 2026-08-30`. Não reconsultei o Ministero.
8. **O banco Supabase está atrás desta leitura**: `supabase/importacoes/IT-CAMADAS-2026-09-02.sql` grava, para as 10 substâncias dos dois atos, `expiry_novo = null`, `risk_assessment = 'NAO_SEI'` e `ato_lido = false`, com a citação *"TITULO CASADO, ATO NAO LIDO"*. Precisa ser reescrito com as datas da Tabela 1A **e com os estados corrigidos da Tabela 1B**.

**Resistência**
9. **14 das 23 fichas GIRE não foram lidas** — inclusive as quatro espécies que o índice associa a mais de um mecanismo na mesma cultura (*Echinochloa*, *Lolium*, *Papaver*, e a parte ALS de *Avena*). Ano do primeiro caso e regiões dessas 14: **NÃO SEI**.
10. **A ficha de *Conyza canadensis* chegou truncada** — mecanismo no corpo, ano e regiões não lidos.
11. **Os mapas nacionais em si** (imagem/PDF) — só o rótulo do mapa foi lido.
12. **As "linee guida specifiche"** citadas por *Alisma* (*"Consulta le linee guida specifiche"*), por *Avena sterilis* (idem) e declaradas em preparo por *Ammania* e *A. palmeri* (*"Linee guida specifiche: in fase di preparazione"*) — nenhuma foi aberta. O que o GIRE recomenda: **NÃO SEI**.
13. **Data da última atualização de cada ficha** — não declarada no índice. Não sei se o "primo caso 1982" de *Chenopodium* é a informação corrente de 2026.
14. **`ESPECIES_TOTAL: 22` × 23 espécies no array** — contradição interna do arquivo do acervo, não resolvida.
15. **Nenhuma fonte de resistência a FUNGICIDA ou a INSETICIDA foi lida.** O GIRE é só herbicida. Metade do portfólio italiano (fungicidas e inseticidas, incluindo 12 dos 27 produtos sob data UE anterior a 2028) não tem camada de resistência lida. **Não existe leitura FRAC nem IRAC italiana neste material.**

**Portfólio**
16. **68 dos 163 registros não declaram grupo de mecanismo e 25 ficaram ilegíveis por codificação de fonte.** Todas as contagens da seção 4 são **piso**.
17. **144 dos 163 registros (88,3 %) não têm nenhuma linha de uso autorizado extraída**; em 82 deles há cultura e há alvo no rótulo, sem ligação entre os dois.
18. **27 dos 90 pares cultura × alvo (30 %) são biologicamente incompatíveis** segundo a auditoria, e nenhum deles foi corrigido no arquivo.
19. **Modalidade não rodada:** nenhuma consulta paga (Apify) foi executada — `APIFY_RUNS: 0`, `COST_USD: 0` nas duas fontes de referência.
20. **Bacheca dei bollettini do Piemonte** (datas de calendário dos tratamentos obrigatórios de 2026, por área) redireciona para `dashboard01.green-planet.it`, que responde *"Non è possibile accedere a questo sito direttamente"*. As datas existem e estão publicadas; **eu não sei quais são**. Isso é **acesso bloqueado**, não ausência de datas.

---

## 6 · AFIRMAÇÕES QUE ESTE MATERIAL NÃO AUTORIZA

**Sobre a camada europeia**
1. ❌ "A substância X vai ser proibida." Nenhum ato lido decide proibição. Os dois tratam não renovação como hipótese de regulamento **futuro**.
2. ❌ "A aprovação foi renovada." Nenhum dos atos renova nada. Ambos só trocam a data da sexta coluna do Anexo do Reg. 540/2011.
3. ❌ "A EFSA reprovou / a EFSA aprovou X." Os atos registram que a conclusão **foi adotada e comunicada** (pirimicarb 25/09/2024, phenmedipham 30/09/2025, fludioxonil 25/09/2024, fosetyl 13/06/2025). **O conteúdo dessas conclusões: NÃO SEI.**
4. ❌ "A EFSA precisa de mais tempo" como explicação genérica. Para pirimicarb, phenmedipham e fludioxonil, o motivo declarado é outro: o parecer do Comitê Permanente e as decisões de gestão de risco da Comissão.
5. ❌ "Estas datas são firmes." O próprio ato diz que são estimativas com incerteza declarada, e que o prazo de lambda-cialotrina, metaldeído, tebuconazol e metazachlor **não inclui** o tempo de eventual pedido adicional da EFSA.
6. ❌ "A substância não tem ato / não tem risco regulatório porque não achei ato." Ausência na janela consultada é **NÃO SEI**.
7. ❌ "Fosetyl-aluminium tem aprovação até 31/01/2028." O que está provado é que **"Fosetyl"**, linha 131, foi movido para 31/01/2028. A identidade com o registro italiano não foi verificada.
8. ❌ "Tebuconazol é candidato à substituição." Não está escrito no ato lido. NÃO SEI.

**Sobre o portfólio**
9. ❌ "O produto vai sair do mercado." · ❌ "A ADAMA vai perder o registro." · ❌ "Há risco de desabastecimento." · ❌ "Há risco comercial em N produtos."
10. ❌ "15 produtos estão vencidos, logo não podem ser vendidos." `EXPIRY` é data de registro nacional, e **EXPIRY ≠ WITHDRAWAL**. Venda, disponibilidade comercial e presença em catálogo **não são provadas por este material**.
11. ❌ "A data nacional é fixada pela data europeia." Eu mostrei **coincidência em 23 casos e uma exceção**. O mecanismo não está escrito em nenhuma fonte que li.
12. ❌ "A ADAMA tem 4 produtos com uso lido em arroz (glifosato)." A palavra "Riso" desses quatro veio do nome de uma daninha.

**Sobre resistência**
13. ❌ "O produto X falha." · ❌ "O produto do concorrente falhou." · ❌ "O produto X resolve a resistência Y."
14. ❌ "Há oportunidade comercial nesta resistência."
15. ❌ "A resistência está aumentando." O GIRE publica **onde foi confirmada**, não quanta área tem. Não é mapa de incidência.
16. ❌ "Esta área/província tem resistência." A ficha dá **região**, e o GIRE não declara proporção.
17. ❌ "A espécie inteira é resistente." Três fichas dizem **"alcune popolazioni"**.
18. ❌ "*Amaranthus palmeri* tem resistência múltipla na Itália." O trecho de vários mecanismos é sobre a **América**, com ano **1989**, e sem nomear os mecanismos.
19. ❌ "Há resistência múltipla em *Echinochloa*, *Lolium* e *Papaver*." O índice mostra **mapas** com mais de um mecanismo; a única declaração literal de resistência múltipla no material é a de *Avena sterilis*.
20. ❌ "A espécie sem mapa não tem resistência confirmada." Cinco fichas provam o contrário.
21. ❌ "O GIRE recomenda tal manejo." Nenhuma linha-guia foi aberta.
22. ❌ Qualquer afirmação sobre **resistência a fungicida ou a inseticida na Itália**. Não há fonte lida.

---

### Arquivos relevantes (caminhos absolutos)

- `C:\eame-sintonia\.wfaudit.json` — catálogo ADAMA Itália, 163 registros, snapshot `PROD_FTS_6_20260824`
- `C:\eame-sintonia\data\samples\IT-REGUA\IT-ADAMA-EU-ACTIVE-SUBSTANCE-V1.json` — cruzamento 53 substâncias × atos UE (é onde FOSETYL-ALUMINIUM está marcado `NO_ACT_IN_THIS_WINDOW`, marca que este relatório derruba)
- `C:\eame-sintonia\data\samples\IT-CIENCIA\IT-GIRE-RESISTENCIA-V1.json` — índice GIRE (é onde `ESPECIES_TOTAL: 22` não bate com as 23 espécies do array)
- `C:\eame-sintonia\data\samples\PIEMONTE-FD\insetticidi_ammessi_2026_pt.txt` — lista das substâncias admitidas em 2026, com lambda-cialotrina e tau-fluvalinate no 2º tratamento
- `C:\eame-sintonia\supabase\importacoes\IT-CAMADAS-2026-09-02.sql` — grava `expiry_novo = null` e `ato_lido = false` para as 10 substâncias dos dois atos de 2026; precisa ser reescrito
- `C:\eame-sintonia\research\italy-demo-reality\ITALY-REGUA-RESULTADO-V0.md`, linha 395 — a frase antiga do acervo, *"EXPIRY ≠ WITHDRAWAL: re-registro é rotina"*