# PACOTE DE REVISAO HUMANA — `T3 = Praga e doenca`

> **Este ficheiro esta a espera de uma pessoa.** Nenhum rotulo aqui foi
> atribuido por maquina, e nenhum sera.
>
> ```
> AUTO_LABELS_ASSIGNED = 0
> HUMAN_REVIEW_REQUIRED = YES
> ```
>
> Isto **nao e** o gabarito de T3. E o pacote que permite construi-lo.

---

## COMO PREENCHER

**A definicao e a que ja existe, e nao se inventa outra:** `T3 = Praga e doenca`
(`pedido/pedido.py :: ALVOS`).

- **`T3_SIM`** — o documento, **pelo proprio conteudo**, apresenta-se ou trata
  substancialmente de praga, doenca, fitossanidade, defesa fitossanitaria ou do
  manejo desse problema.
- **`T3_NAO`** — o documento pertence claramente a outro assunto e so menciona
  praga ou doenca de passagem.
- **`T3_AMBIGUO`** — os dois assuntos sao substanciais. Nao desempate para
  arrumar o numero: ambiguo e um resultado.
- **`EVIDENCIA_INSUFICIENTE`** — o trecho disponivel nao chega para decidir.
  Isto nao e falha do revisor: e informacao sobre o pacote.

Escreva sempre o **MOTIVO** e a **EVIDENCIA USADA** — que trecho, que linha. Um
rotulo sem razao escrita nao serve de gabarito, e esta casa ja mediu porque.


## O QUE ESTE PACOTE ESCONDE DE SI, E PORQUE

Ate voce decidir, este ficheiro **nao lhe mostra**:

- a decisao atual da porta (`PERGUNTAS_DO_UNIVERSO`);
- o territorio declarado pela ficha da fonte;
- quais destes documentos casaram a varredura que os trouxe para aqui.

Tudo isso esta na seccao `AUDIT_AFTER_REVIEW`, **no fim**, para comparar
depois. A ordem de apresentacao e por hash do caminho — nao por
publicador, nao por pasta, e nao por «mais parecido com T3».

```
HUMAN_LABEL NAO PODE NASCER A OLHAR PARA CURRENT_CLASSIFIER_OUTPUT.
```

## TRES ARMADILHAS QUE ESTE CORPUS TEM DE VERDADE

Nao sao hipoteses: foram medidas nesta arvore.

**1 · O NOME DO FICHEIRO NAO E PROVA SOBRE O CONTEUDO.** O campo
`PARENT` mostra o caminho do original porque a procedencia faz parte da
ficha — mas **seis** documentos deste pacote tem no nome
«Fitosanitari», «Agrometeorologico» ou «Meteorologico» e **cinco deles**
nao dizem nada disso na abertura. Decida pelo corpo.

**2 · O MESMO PUBLICADOR PRODUZ ASSUNTOS DIFERENTES.** A ARPAV publica
«Meteo Veneto» e tambem «U.O. Fitosanitario — VITE». Ver o nome da
instituicao nao adianta a resposta.

**3 · HA DOCUMENTOS QUE SAO AS DUAS COISAS.** Alguns abrem com paginas
de analise meteorologica e so depois tratam da praga. Para esses existe
`T3_AMBIGUO`, e usa-lo e a resposta certa — nao uma desistencia.

**Um aviso sobre tabelas.** Ficheiros muito grandes (CSV) aparecem com
as primeiras linhas apenas. Se isso nao chegar, a resposta e
`EVIDENCIA_INSUFICIENTE` — nao um palpite.

**E por isso que sao 46 fichas e nao 27.** O censo achou 27 documentos
que se auto-declaram fitossanitarios, e achou-os com seis frases
literais. Se este pacote levasse so esses 27, todo positivo do gabarito
conteria uma dessas frases — e qualquer classificador baseado nelas
tiraria nota perfeita num gabarito que elas escolheram. Os 27 estao aqui
dentro, **sem marca nenhuma**, no meio dos outros.

---

## ITEM 01 / 46

```
ITEM_ID        RAW-b631f6eecfbc1db0.txt
SOURCE_ID      NAO SEI
PUBLISHER      REGIONE LAZIO
CONTENT_PATH   data/derivados/texto/RAW-b631f6eecfbc1db0.txt
PARENT         data/samples/IT-BOLLETTINI-VPN-2026/pdf/LAZIO_PIANURA_INTERNA_VITERBESE.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 1544
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> Bollettino Fitosanitario

**ABERTURA DO DOCUMENTO**

```text
Bollettino Fitosanitario ZONA PROGETTUALE PIANURA INTERNA VITERBESE AVVERSITA’ Mosca dell’olivo dal Bactrocera oleae al n. 08/2026 01/09/2026 07/09/2026 Fase fenologica: Condizioni meteo: Metodologia: Soglia di intervento: Rilievo infestazione: SVILUPPO DEI FRUTTI (Scala BBCH Olio 75) “Le drupe hanno raggiunto circa il 70% delle dimensioni finali. Indurimento del nocciolo (nocciolo che lignifica mostrando resistenza al taglio)” Temperature superiori a 32°C; elevata percentuale di NON FAVOREVOLI umidità relativa; Schiusa uova: T min 17° C – T max 30°. Voli notte di 16-17 ° C / giorno fino a 35° C Si esaminano 20 olive a pianta su 10 piante scelte a caso per cultivar per ettaro, un totale di 200 olive. Metodo Adulticida Olive da olio: 4-5% di punture fertili o 2 femmine ovigere/trappola/settimana Olive da mensa 1-2% di punture fertili (uova, larve, pupari) Attacco rilevato: 0% PRESCRIZIONE
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…Bollettino Fitosanitario ZONA PROGETTUALE PIANURA INTERNA VITERBESE AVVERSITA’ Mosca…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `ZONA PROGETTUALE PIANURA INTERNA VITERBESE`
- `AVVERSITA’`
- `SVILUPPO DEI FRUTTI`
- `NON FAVOREVOLI`
- `PRESCRIZIONE`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 02 / 46

```
ITEM_ID        RAW-a927e846ba8e78b0.txt
SOURCE_ID      IT-T4-001
PUBLISHER      MINISTERO DELLA SALUTE
CONTENT_PATH   data/derivados/texto/RAW-a927e846ba8e78b0.txt
PARENT         data/samples/IT-SOURCE-SAMPLES/IT-T4-001/ID_6_Dataset_Fitosanitari_v2.0.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 2354
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> Dataset Fitosanitari

**ABERTURA DO DOCUMENTO**

```text
Dataset Fitosanitari Ver. 2.0 Pagina 1 di 2 Intestazione num_registrazione denominazione_prodotto ragione_sociale indirizzo_sede_legale cap_sede_legale comune_sede_legale provincia_sede_legale indirizzo_sede_amministrativa cap_sede_amministrativa comune_sede_amministrativa provincia_sede_amministrativa data_registrazione data_scadenza_autorizzazione indicazioni_di_pericolo attivita codice_formulazione descrizione_formulazione sostanze_attive contenuto_per_100g_di_prodotto importazione_parallela prodotto_piante_ornamentali stato_amministrativo motivo_della revoca data_decreto_revoca data_decorrenza_revoca Descrizione Numero di registrazione del Prodotto Fitosanitario Denominazione commerciale del Prodotto Fitosanitario Ragione sociale dell’Impresa Titolare dell’autorizzazione Indirizzo della sede legale dell’Impresa Codice d’Avviamento Postale della sede legale dell’Impresa Denominazione 
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- NONE

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 03 / 46

```
ITEM_ID        RAW-9a01cc17889e1f40.txt
SOURCE_ID      NAO SEI
PUBLISHER      ARPAV
CONTENT_PATH   data/derivados/texto/RAW-9a01cc17889e1f40.txt
PARENT         data/samples/IT-ARPAV-VENETO/boll_agro_settimanale.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 5337
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> BOLLETTINO AGROMETEOROLOGICO REGIONALE N. 21 del 01.09.2026 Aggiornamento del 02.09.

**ABERTURA DO DOCUMENTO**

```text
BOLLETTINO AGROMETEOROLOGICO REGIONALE N. 21 del 01.09.2026 Aggiornamento del 02.09. MAPPE DI TEMPERATURA E PRECIPITAZIONI - ULTIMA DECADE Temperatura minima - media decadale (°C) Temperatura massima - media decadale (°C) Precipitazione totale decadale (mm) Numero di giorni piovosi (>=1mm) Arpav, Dipartimento per la Sicurezza del Territorio – Unità Organizzativa Meteorologia e Climatologia EVAPOTRASPIRAZIONE POTENZIALE (ETP) Evapotraspirazione media giornaliera (mm) della pianura veneta calcolata con il metodo PenmanMonteith. Dati di evapotraspirazione di singole stazioni possono essere visualizzati sul bollettino Agrometeo Informa selezionando la zona di interesse. Agrometeoinforma SOMME TERMICHE Valori medi di somma termica della pianura veneta. Dati di somma termica di singole stazioni possono essere visualizzati sul bollettino Agrometeo Informa selezionando la zona di interesse. Agro
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `MAPPE DI TEMPERATURA E PRECIPITAZIONI - ULTIMA DECADE`
- `EVAPOTRASPIRAZIONE POTENZIALE (ETP)`
- `PREVISIONI METEOROLOGICHE`
- `BOLLETTINI FITOSANITARI DELLE PRINCIPALI COLTURE AGRARIE`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 04 / 46

```
ITEM_ID        RAW-699a073ace4361ea.txt
SOURCE_ID      NAO SEI
PUBLISHER      ARPAV
CONTENT_PATH   data/derivados/texto/RAW-699a073ace4361ea.txt
PARENT         data/samples/IT-ARPAV-VENETO/lug2026.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 35768
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> Meteo Veneto: luglio 2026 molto caldo, poche piogge ma con grandi differenze territoriali

**ABERTURA DO DOCUMENTO**

```text
Meteo Veneto: luglio 2026 molto caldo, poche piogge ma con grandi differenze territoriali Sintesi Il mese centrale dell’estate meteorologica in Veneto, è risultato molto più caldo e con una piovosità di poco inferiore rispetto alla norma; salvo alcune fasi caratterizzate da condizioni di instabilità atmosferica soprattutto nella seconda decade del mese e in modo più sporadico nella prima e nell’ultima, sono prevalse infatti correnti anticicloniche che hanno portato giornate con tempo in prevalenza stabile, sotto la spinta di espansioni verso il Mediterraneo, da un lato dell’Anticiclone delle Azzorre ma dall’altro, e in modo sempre più frequente nel corso di questa stagione estiva, anche del promontorio di origine nord-africana. In questo mese si registrano altre due ondate di caldo e forte disagio fisico, la prima dal 7 al 18 luglio soprattutto su pianura e costa anche se meno intensa e 
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `REPORT METEOCLIMATICO MENSILE VENETO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 05 / 46

```
ITEM_ID        RAW-7a51732e87f0f319.txt
SOURCE_ID      NAO SEI
PUBLISHER      REGIONE CAMPANIA
CONTENT_PATH   data/derivados/texto/RAW-7a51732e87f0f319.txt
PARENT         data/samples/IT-BOLLETTINI-VPN-2026/pdf/CAMP_AV-26-08.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 39039
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> GIUNTA REGIONALE DELLA CAMPANIA DIREZIONE GENERALE E POLITICHE AGRICOLE, ALIMENTARI E FORESTALI UOS 207.03.03 - DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA

**ABERTURA DO DOCUMENTO**

```text
GIUNTA REGIONALE DELLA CAMPANIA DIREZIONE GENERALE E POLITICHE AGRICOLE, ALIMENTARI E FORESTALI UOS 207.03.03 - DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI AVELLINO Pubblicazione di orientamento e consulenza per la difesa integrata delle colture che, sulla base dei risultati della rete di monitoraggio, fornisce informazioni sull’applicazione della difesa integrata N. 24 del 26 Agosto 2026 Andamento meteorologico Per la provincia di Avellino sono disponibili i dati delle stazioni della Rete Agrometeorologica Regionale di Flumeri, Greci, Montefredane, Montella, Montemarano, Pietradefusi, Santa Paolina sul sito Portale dell’Agricoltura alla pagina: http://agricoltura.regione.campania.it/meteo/meteo_2026.html Stato fitosanitario delle colture COLTURA Castagno n. UTM Comune Località Varietà Bivio Verdole - 1 Serino Te
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…ANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI AVELLINO Pubblicazione di orientamento e…»
- «…I UOS 207.03.03 - DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DEL…»
- «…one di orientamento e consulenza per la difesa integrata delle colture che, sulla base dei risultati della rete di m…»
- «…ALIMENTARI E FORESTALI UOS 207.03.03 - DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLL…»
- «…sulla base dei risultati della rete di monitoraggio, fornisce informazioni sull’applicazione della difesa integ…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `ALIMENTARE`
- `BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI AVELLINO`
- `CONSIGLI DI DIFESA`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 06 / 46

```
ITEM_ID        RAW-e612807928b5ada9.txt
SOURCE_ID      IT-T3-008
PUBLISHER      ARIF PUGLIA
CONTENT_PATH   data/derivados/texto/RAW-e612807928b5ada9.txt
PARENT         data/collection-store/italy/IT-T3-008/ARIF_SETTIMANALE_2026_N36/v1_e612807928b5/Notiziario_Agrometeorologico_N36_02-09-2026.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 69741
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> Settimanale N. 36 Anno XL

**ABERTURA DO DOCUMENTO**

```text
Settimanale N. 36 Anno XL 02 - 08 settembre 2026 Agenzia regionale per le attività irrigue e forestali Situazione Attuale Il quadro sinottico euro atlantico mostra il ﬂusso perturbato che scorre intorno al 45°N delimitato da una saccatura estesa dalla Groenlandia meridionale, dove è posizionato un primo minimo, ﬁno al nord Atlantico, poi si dirige ondulato verso est sulla penisola scandinava e i paesi Baltici, mentre un secondo minimo è posizionato nel mare del Nord a sud della Norvegia. Scendendo di latitudine, sul Mediterraneo si rileva ancora la presenza del promontorio di matrice sub-tropicale che dall'entroterra del nord Africa si spinge ﬁno all'Anatolia. Sul resto dello scenario, ad ovest, si riscontra un promontorio sul medio Atlantico e un campo di alta pressione ad est sulla Russia centrale. L'Italia in questo contesto rimane interessata direttamente dal promontorio nord african
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `DATA`
- `CIELO`
- `ORE 00:00`
- `ORE 12:00`
- `FOGGIA`
- `SAN NICANDRO GARGANICO`
- `ANDRIA`
- `BARI`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 07 / 46

```
ITEM_ID        RAW-924aabd94168c53a.txt
SOURCE_ID      IT-T5-003
PUBLISHER      GIORNATE FITOPATOLOGICHE
CONTENT_PATH   data/derivados/texto/RAW-924aabd94168c53a.txt
PARENT         data/samples/IT-SOURCE-SAMPLES/IT-T5-003/7_Alesi_olivo-2025_-Bilancio-Fitosanitario-Marche.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 29551
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> Bilancio Fitosanitario

**ABERTURA DO DOCUMENTO**

```text
Bilancio Fitosanitario Olivo 2024 - 2025 Regione : MARCHE Servizio Agrometeorologico Regionale-AMAP Relatore: Alesi Alberto Superficie coltivata Regione: Marche ha 2024 2025 Olivo 9020 8985 di cui Olivo in Biologico 4520 In Corso di definizione Trend In leggero calo In leggero aumento Fonte Regione Marche Destinazione d’uso delle olive prodotte: Quasi totalmente Olio, con la nicchia delle olive Ascolane da mensa Presenti: olio DOP “Cartoceto”, DOP “Oliva Ascolana del Piceno” e olio IGP “Marche” 27 novembre2025 Olivo olio prodotto: il 2024 lo si può considerare un anno record per la produzione di olio nelle Marche, secondo i dati SIAN, le olive molite sono state 36.306 tonnellate con una produzione di 3.905 tonnellate di olio, con una resa piuttosto bassa, poco superiore al 10% Il 2025 invece, ad oggi, sempre secondo dati SIAN, vede una produzione ed una quantità di olive molite pari a 9.
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- NONE

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 08 / 46

```
ITEM_ID        RAW-4e12affad7fedd91.txt
SOURCE_ID      NAO SEI
PUBLISHER      ARPAV
CONTENT_PATH   data/derivados/texto/RAW-4e12affad7fedd91.txt
PARENT         data/samples/IT-ARPAV-VENETO/olivicolo_28_260826.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 3523
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> Pag. 1 di 2

**ABERTURA DO DOCUMENTO**

```text
Pag. 1 di 2 SERVIZIO FITOSANITARIO REGIONE VENETO U.O. Fitosanitario BOLLETTINI FITOSANITARI DIFESA INTEGRATA OLIVO Bollettino n. 28 del 26/08/2026 FENOLOGIA E STATO PRODUTTIVO Ingrossamento/inolizione, le olive hanno ormai raggiunto la pezzatura finale e si avviano verso la fase di indurimento dei tessuti e accumulo oleoso. SITUAZIONE FITOSANITARIA Mosca dell’olivo (Bactrocera oleae): il controllo settimanale evidenzia una pressione sostanzialmente stabile rispetto alla settimana precedente. Il calo termico degli ultimi giorni, accompagnato da un incremento dell’umidità relativa, sta creando una finestra favorevole alla ripresa dell’ovideposizione. Distribuzione regionale della pressione (rilievi + modelli previsionali) • Alto lago di Garda: 3 – 4% • Medio e basso lago di Garda: 3 – 4% • Entroterra gardesano: 3 – 4% • Colline veronesi Nord: 3 – 4% • Colline veronesi Centrali: 3 – 4% • C
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…Pag. 1 di 2 SERVIZIO FITOSANITARIO REGIONE VENETO U.O. Fitosanitario BOLLETTINI FITOSANITARI D…»
- «…2 SERVIZIO FITOSANITARIO REGIONE VENETO U.O. Fitosanitario BOLLETTINI FITOSANITARI DIFESA INTEGRATA OLIVO Bollettino n…»
- «…. Fitosanitario BOLLETTINI FITOSANITARI DIFESA INTEGRATA OLIVO Bollettino n. 28 del 26/08/2026 FENOLOGIA E STATO PRO…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `SERVIZIO FITOSANITARIO REGIONE VENETO`
- `BOLLETTINI FITOSANITARI DIFESA INTEGRATA`
- `OLIVO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 09 / 46

```
ITEM_ID        RAW-420e08ef15bec6e4.txt
SOURCE_ID      IT-T3-002
PUBLISHER      REGIONE CAMPANIA
CONTENT_PATH   data/derivados/texto/RAW-420e08ef15bec6e4.txt
PARENT         data/samples/IT-BOLLETTINI-VPN-2026/pdf/CAMP_SA-26-08.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 26817
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> GIUNTA REGIONALE DELLA CAMPANIA DIREZIONE GENERALE E POLITICHE AGRICOLE, ALIMENTARI E FORESTALI UOS2070303- DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE

**ABERTURA DO DOCUMENTO**

```text
GIUNTA REGIONALE DELLA CAMPANIA DIREZIONE GENERALE E POLITICHE AGRICOLE, ALIMENTARI E FORESTALI UOS2070303- DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI SALERNO Pubblicazione di orientamento e consulenza per la difesa integrata delle colture che, sulla base dei risultati della rete di monitoraggio, fornisce informazioni sull’applicazione della difesa integrata N° 24 del 26/08/2026 Andamento meteorologico Per la provincia di Salerno sono disponibili i dati delle stazioni della Rete Agrometeorologica Regionale di Battipaglia, Capaccio fraz. Gromola, Controne, Eboli, Serre sul sito Portale dell’Agricoltura alla pagina: http://agricoltura.regione.campania.it/meteo/meteo_2026.html Stato fitosanitario delle colture COLTURA N° Comune 1 Eboli ACTINIDIA UTM Località Azienda Pennatone Idea Natura Varietà Stadio fenologico S
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…ANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI SALERNO Pubblicazione di orientamento e…»
- «…STALI UOS2070303- DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DEL…»
- «…one di orientamento e consulenza per la difesa integrata delle colture che, sulla base dei risultati della rete di m…»
- «…OLE, ALIMENTARI E FORESTALI UOS2070303- DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLL…»
- «…sulla base dei risultati della rete di monitoraggio, fornisce informazioni sull’applicazione della difesa integ…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `SICUREZZA ALIMENTARE`
- `BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI SALERNO`
- `ACTINIDIA UTM`
- `CONSIGLI DI DIFESA FITOSANITARIA`
- `AGRUMI`
- `COLTURA`
- `CILIEGIO`
- `TRAMONTI`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 10 / 46

```
ITEM_ID        RAW-5dcfb75ac38390c3.txt
SOURCE_ID      NAO SEI
PUBLISHER      REGIONE PIEMONTE
CONTENT_PATH   data/derivados/texto/RAW-5dcfb75ac38390c3.txt
PARENT         data/samples/PIEMONTE-FD/piano_operativo_2026.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 23003
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> D.D. n. 280 del 16 marzo 2026 - Misure fitosanitarie di emergenza e aggiornamento prescrizioni per il contrasto della Flavescenza Dorata della vite nella Regione Piemonte – Piano operativo Anno 2026

**ABERTURA DO DOCUMENTO**

```text
D.D. n. 280 del 16 marzo 2026 - Misure fitosanitarie di emergenza e aggiornamento prescrizioni per il contrasto della Flavescenza Dorata della vite nella Regione Piemonte – Piano operativo Anno 2026 PIANO OPERATIVO FLAVESCENZA DORATA DELLA VITE - ANNO 2026 PREMESSA L’applicazione dell’Ordinanza n. 4 del Direttore del Servizio Fitosanitario Centrale del 22 giugno 2023 recante “Misure fitosanitarie d'emergenza per il contrasto di Grapevine flavescence dorée phytoplasma atte ad impedirne la diffusione nel territorio della Repubblica italiana”, ha lo scopo di tutelare la viticoltura in tutto il territorio regionale, interessando una superficie che supera i 40 mila ettari. L’accertamento della malattia può svolgersi solo in un periodo limitato di tempo nel corso della stagione vegetativa e pertanto le indagini e i controlli devono essere concentrati in soli quattro mesi. Di conseguenza, vista
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…e dell’Ordinanza n. 4 del Direttore del Servizio Fitosanitario Centrale del 22 giugno 2023 recante “Misure fitosanitarie d…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `PIANO OPERATIVO FLAVESCENZA DORATA DELLA VITE - ANNO 2026`
- `PREMESSA`
- `A) VIGILANZA FITOSANITARIA DI CARATTERE ISPETTIVO SUL TERRITORIO`
- `B) PROGETTI PILOTA TERRITORIALI`
- `C) CAMPAGNA INFORMATIVA`
- `D) SPERIMENTAZIONI E RICERCA`
- `ALLEGATO 3.B`
- `ALLEGATO 3.C`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 11 / 46

```
ITEM_ID        RAW-8c13500d43502e64.txt
SOURCE_ID      IT-T2-002
PUBLISHER      ARPAV
CONTENT_PATH   data/derivados/texto/RAW-8c13500d43502e64.txt
PARENT         data/collection-store/italy/IT-T2-002/ARPAV_Z16_20260903160912/v1_8c13500d4350/agro_16.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 5292
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> Agrometeo… Informa

**ABERTURA DO DOCUMENTO**

```text
Agrometeo… Informa Zona 16 Val d'Illasi Alpone N° 54 03/09/26 Il tempo previsto nei prossimi giorni Evoluzione Generale L'estensione dell'Anticiclone Subtropicale Africano verso le nostre latitudini persisterà almeno fino a lunedì. Le temperature sopra la media anche di molto continueranno ad essere la caratteristica meteorologica saliente; in particolare saranno in aumento fino a domenica mattina e poi in calo. https://meteo.arpa.veneto.it/?page=MV Probabilita' Precipitazioni Venti Temperatura venerdì 4 Mattina Pomeriggio Nulla 0% Deboli/Moderati-Variabili Min  Max  sabato 5 Mattina Pomeriggio domenica 6 Mattina Pomeriggio Nulla 0% Deboli/Moderati-Variabili Min  Max  Nulla 0% Deboli/Moderati-Variabili Min  Max  Informazioni agroclimatiche e territoriali Temperatura aria 2m (°C) ultimi 4 g. 34 32 30 28 26 24 22 20 18 16 14 DOM LUN MAR MER Illasi Colognola ai Colli Umidità rel. aria
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `DOM`
- `LUN`
- `MAR`
- `MER`
- `RIEPILOGO DATI MESE DI AGOSTO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 12 / 46

```
ITEM_ID        RAW-6d12bcb5fa2b0905.txt
SOURCE_ID      NAO SEI
PUBLISHER      ARPAV
CONTENT_PATH   data/derivados/texto/RAW-6d12bcb5fa2b0905.txt
PARENT         data/samples/IT-ARPAV-VENETO/vite_20_270826.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 7891
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> U.O. Fitosanitario

**ABERTURA DO DOCUMENTO**

```text
U.O. Fitosanitario Bollettino n. 20 del 27 agosto 2026 VITE Andamento meteo (in collaborazione col Servizio Meteorologia e Climatologia di Arpav): La settimana è stata interessata da alcune perturbazioni che hanno alternato giornate soleggiate ad eventi piovosi diffusi, con qualche limitato episodio grandinigeno. L’attuale settimana è iniziata con giornate soleggiate e temperature in graduale aumento. Le temperature massime e minime medie rispettivamente sono risultate comprese tra 28-32°C e tra 18-22°C. Le precipitazioni hanno interessato tutto il territorio veneto con cumuli mediamente compresi tra 40-75 mm nella zona centro orientale e tra 20-50 mm nelle restanti zone. MEDIA DELLE TEMPERATURE MASSIME E MINIME DAL 19/08 al 25/08 - ARPAV PRECIPITAZIONI E GIORNI PIOVOSI DAL 19/08 AL 25/08 – ARPAV U.O. Fitosanitario Fase fenologica: Le varietà a media maturazione hanno raggiunto la loro p
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…U.O. Fitosanitario Bollettino n. 20 del 27 agosto 2026 VITE Andamento meteo (i…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `PRECIPITAZIONI E GIORNI PIOVOSI DAL 19/08 AL 25/08 – ARPAV`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 13 / 46

```
ITEM_ID        RAW-99cb44a67f6b4e9a.txt
SOURCE_ID      NAO SEI
PUBLISHER      REGIONE CAMPANIA
CONTENT_PATH   data/derivados/texto/RAW-99cb44a67f6b4e9a.txt
PARENT         data/samples/IT-BOLLETTINI-VPN-2026/pdf/CAMP_NA-26-08.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 27237
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> ASSESSORATO AGRICOLTURA

**ABERTURA DO DOCUMENTO**

```text
ASSESSORATO AGRICOLTURA GIUNTA REGIONALE DELLA CAMPANIA DIREZIONE GENERALE POLITICHE AGRICOLE ALIMENTARI E FORESTALISETTORE 207.03.03 - AMBIENTE, SVILUPPO LOCALE, SISTEMA DELLA CONOSCENZA E DIFESA DELLE COLTURE SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI NAPOLI Areali: Piana Campana (Acerra e San Vitaliano) Piana Flegrea (Giugliano in Campania) Colline Flegree (Bacoli, Calvizzano e Qualiano) Pubblicazione di orientamento e consulenza per la difesa integrata delle colture che, sulla base dei risultati della rete di monitoraggio, fornisce informazioni sull’applicazione della difesa integrata Bollettino N°24 del 26/08/2026 Andamento meteorologico Per la provincia di Napoli sono disponibili i dati delle stazioni della Rete Agrometeorologica di Acerra, Boscotrecase, San Gennaro Vesuviano, Casalnuovo loc. Casarea e Barano d’Ischia sul sito 
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…ANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI NAPOLI Areali: Piana Campana (Acerra e S…»
- «…DELLA CONOSCENZA E DIFESA DELLE COLTURE SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DEL…»
- «…one di orientamento e consulenza per la difesa integrata delle colture che, sulla base dei risultati della rete di m…»
- «…UPPO LOCALE, SISTEMA DELLA CONOSCENZA E DIFESA DELLE COLTURE SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLE…»
- «…sulla base dei risultati della rete di monitoraggio, fornisce informazioni sull’applicazione della difesa integ…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `ASSESSORATO AGRICOLTURA`
- `BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI NAPOLI`
- `COLTURA PESCO NETTARINA`
- `CONSIGLI DI DIFESA FITOSANITARIA`
- `COLTURA NOCCIOLO`
- `COLTURA NOCE`
- `UTM`
- `COLTURA CILIEGIO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 14 / 46

```
ITEM_ID        RAW-3d3c1bc0e96332e8.txt
SOURCE_ID      IT-T2-002
PUBLISHER      ARPAV
CONTENT_PATH   data/derivados/texto/RAW-3d3c1bc0e96332e8.txt
PARENT         data/collection-store/italy/IT-T2-002/ARPAV_Z09_20260902152638/v1_3d3c1bc0e963/agro_09.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 5450
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> Agrometeo… Informa

**ABERTURA DO DOCUMENTO**

```text
Agrometeo… Informa Zona 9 Medio Polesine N° 54 02/09/26 Il tempo previsto nei prossimi giorni Evoluzione Generale Torna ad espandersi un promontorio anticiclonico con aria calda; per il Veneto le condizioni sono generalmente stabili con parecchi spazi di sereno, a fronte di temporanei annuvolamenti più che altro in montagna, ove è possibile qualche locale precipitazione mercoledì dal pomeriggio e a tratti nel fine settimana; temperature in genere ben superiori alla norma. https://meteo.arpa.veneto.it/?page=MV Probabilita' Precipitazioni Venti Temperatura giovedì 3 Mattina Pomeriggio Nulla 0% Deboli Orientali Min = Max  venerdì 4 Mattina Pomeriggio Nulla 0% Deboli Variabili Min  Max  sabato 5 Mattina Pomeriggio Nulla 0% Deboli Variabili Min  Max = Informazioni agroclimatiche e territoriali Temperatura aria 2m (°C) ultimi 4 g. 34 32 30 28 26 24 22 20 18 SAB DOM LUN MAR Villadose Concad
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `SAB`
- `DOM`
- `LUN`
- `MAR`
- `RIEPILOGO DATI MESE DI AGOSTO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 15 / 46

```
ITEM_ID        RAW-2a12cb316622a9a5.txt
SOURCE_ID      IT-T5-003
PUBLISHER      GIORNATE FITOPATOLOGICHE
CONTENT_PATH   data/derivados/texto/RAW-2a12cb316622a9a5.txt
PARENT         data/samples/IT-SOURCE-SAMPLES/IT-T5-003/11_Altieri_Bilancio-Fitosanitario-Olivo-2024-25-Basilicata.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 5914
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> Bilancio Fitosanitario

**ABERTURA DO DOCUMENTO**

```text
Bilancio Fitosanitario Olivo 2024 - 2025 Regione Basilicata Relatrice Antonietta Altieri antonietta.altieri@regione.Basilicata.it a cura di ▪ Ufficio Fitosanitario, Regione Basilicata ▪ Servizi Difesa Integrata, ALSIA ▪ Servizio Agrometereologico Lucano, ALSIA ▪ Laboratorio Fitopatologico, ALSIA ▪ Centro di saggio, ALSIA ▪ Tecnici di Organizzazioni di Produttori ▪ Consulenti fitosanitari 27 novembre 2025 Principali areali olivicoli lucani Superfice coltivata (ettari) Dati ISTAT Regione 2010 2020 Trend Basilicata 28.002 20.997 In calo Matera Potenza 16.129 11.874 12.972 8.025 In calo In calo In provincia di Matera il 62% Numero di aziende Dati ISTAT Regione Basilicata Matera Potenza 2010 32.830 16.459 16.371 2020 23.497 12.460 11.037 La superficie media aziendale < 1,00 ettato 2 Olivo Principali areali olivicoli lucani Su 131 Comuni lucani, 30 aderiscono all’associazione «Città dell’olio»
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…sanitario, Regione Basilicata ▪ Servizi Difesa Integrata, ALSIA ▪ Servizio Agrometereologico Lucano, ALSIA ▪ Laborat…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `OGLIAROLA SALENTINA`
- `MAJATICA DI FERRANDINA`
- `DRITTA 3%`
- `MORAIOLO 3%`
- `JUSTA 5%`
- `CORATINA 5%`
- `FRANTOIO 34%`
- `LECCINO 6%`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 16 / 46

```
ITEM_ID        RAW-ded546686d61dc91.txt
SOURCE_ID      NAO SEI
PUBLISHER      REGIONE PIEMONTE
CONTENT_PATH   data/derivados/texto/RAW-ded546686d61dc91.txt
PARENT         data/samples/PIEMONTE-FD/insetticidi_ammessi_2026.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 4748
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> Settore Fitosanitario e servizi tecnico scientifici

**ABERTURA DO DOCUMENTO**

```text
Settore Fitosanitario e servizi tecnico scientifici FLAVESCENZA DORATA DELLA VITE LOTTA OBBLIGATORIA: INSETTICIDI AMMESSI 2026 AZIENDE BIOLOGICHE TRE trattamenti insetticidi obbligatori SOLO SUI GIOVANI DI SCAFOIDEO. NON ESEGUIRE DURANTE LA FIORITURA  3 trattamenti a distanza di 7-10 giorni con PIRETRO oppure  1° trattamento con SALI POTASSICI DI ACIDI GRASSI o AZADIRACTINA + 2° e 3° trattamento con PIRETRO ATTENZIONE: Per il piretro è necessario garantire la distribuzione di almeno 30 g/ha di principio attivo Se si utilizzano i sali potassici in zone con acque dure si garantisce una migliore azione con l’aggiunta di condizionatori d’acqua utili a evitare precipitazione e flocculazione del prodotto  in aggiunta possono essere effettuati trattamenti con: OLIO DI ARANCIO DOLCE PRODOTTI MICROBIOLOGICI SILICATO DI ALLUMINIO (CAOLINO)* * Prodotto fitosanitario impiegabile con deroga sempli
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `AZIENDE BIOLOGICHE`
- `SOLO SUI GIOVANI DI SCAFOIDEO. NON ESEGUIRE DURANTE LA FIORITURA`
- `MODALITÀ OBBLIGATORIE DI ESECUZIONE DEI TRATTAMENTI INSETTICIDI`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 17 / 46

```
ITEM_ID        RAW-6377ac2f8419d905.txt
SOURCE_ID      NAO SEI
PUBLISHER      ARPAV
CONTENT_PATH   data/derivados/texto/RAW-6377ac2f8419d905.txt
PARENT         data/samples/IT-ARPAV-VENETO/fineestate_310826.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 3422
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> Meteo Veneto. Fine estate tra eventi intensi e ritorno del caldo

**ABERTURA DO DOCUMENTO**

```text
Meteo Veneto. Fine estate tra eventi intensi e ritorno del caldo La scorsa settimana abbiamo osservato un breve ma intenso ritorno del caldo afoso nei giorni centrali, in particolare da mercoledì 26 e fino agli episodi temporaleschi di venerdì 28 agosto che hanno interessato il Veneto e in generale il Nord Italia. Nel corso di venerdì 28 sulla regione si è registrata una significativa intensificazione dei venti dai quadranti meridionali sulle zone montane, specie in quota, e poi una fase di marcata instabilità specie dal pomeriggio con frequenti passaggi temporaleschi anche intensi e organizzati, compatibili con forti grandinate, forti raffiche di vento e forti rovesci che hanno coinvolto soprattutto la pianura (specie centro-occidentale, tra Veronese, Vicentino e Padovano) e parte della fascia pedemontana/prealpina. La rete di stazioni Arpav in occasione dell’evento di venerdì 28, rilev
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- NONE

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 18 / 46

```
ITEM_ID        RAW-144fdb152b1a6ae4.txt
SOURCE_ID      IT-T2-001
PUBLISHER      ARPAE
CONTENT_PATH   data/derivados/texto/RAW-144fdb152b1a6ae4.txt
PARENT         data/samples/IT-SOURCE-SAMPLES/IT-T2-001/35_boll_agro_20260831.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 3232
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> Bollettino AgroMeteorologico Settimanale n. 35/2026 del 31 agosto 2026

**ABERTURA DO DOCUMENTO**

```text
Bollettino AgroMeteorologico Settimanale n. 35/2026 del 31 agosto 2026 24 agosto 2026 - 30 agosto 2026 Diario meteorologico: Temporali con cumulati modesti e temperatura media regionale record. La settimana è stata caratterizzata da temporali avvenuti nelle giornate di Lunedì 24, Martedì 25 e Venerdì 28. Lunedì 24 agosto le precipitazioni sono iniziate in serata e hanno interessato le province di Piacenza, Parma e il crinale centrale della regione, con cumulati massimi di 10 mm. Le precipitazioni di martedi 25 agosto in realtà sono il prosieguo dell’impulso perturbato del giorno 24, che ha attraversato la regione da ovest verso est, con cumulati massimi di 17 mm localizzati nel ferrarese. Il giorno venerdì 28 i temporali si sono manifestati in serata e hanno attraversato la regione da sud ovest verso nord est, con cumulati massimi di 15 mm localizzati lungo l'asta del Po. L’evento è stat
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- NONE

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 19 / 46

```
ITEM_ID        RAW-c6377f6951bfeb2e.txt
SOURCE_ID      NAO SEI
PUBLISHER      ARPAV
CONTENT_PATH   data/derivados/texto/RAW-c6377f6951bfeb2e.txt
PARENT         data/samples/IT-ARPAV-VENETO/olivicolo_29_020926.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 3627
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> Pag. 1 di 2

**ABERTURA DO DOCUMENTO**

```text
Pag. 1 di 2 SERVIZIO FITOSANITARIO REGIONE VENETO U.O. Fitosanitario BOLLETTINI FITOSANITARI DIFESA INTEGRATA Inolizione – inizio invaiatura. OLIVO Bollettino n. 29 del 02/09/2026 FENOLOGIA E STATO PRODUTTIVO SITUAZIONE FITOSANITARIA Mosca dell’olivo (Bactrocera oleae): il monitoraggio della settimana evidenzia una pressione stabile. Le temperature rimangono elevate, ma l’umidità non ha ancora determinato una ripresa significativa dell’ovideposizione. In molti areali non sono state rilevate nuove infestazioni attive. La riduzione della popolazione adulta è coerente con il fatto che numerosi olivicoltori hanno effettuato un trattamento negli ultimi 10 giorni, con esche adulticide o adulticidi, contribuendo a contenere ulteriormente la pressione del fitofago. I dati riportati derivano da osservazioni dirette e da analisi previsionali, tenendo conto della forte variabilità territoriale, i v
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…Pag. 1 di 2 SERVIZIO FITOSANITARIO REGIONE VENETO U.O. Fitosanitario BOLLETTINI FITOSANITARI D…»
- «…2 SERVIZIO FITOSANITARIO REGIONE VENETO U.O. Fitosanitario BOLLETTINI FITOSANITARI DIFESA INTEGRATA Inolizione – inizi…»
- «…. Fitosanitario BOLLETTINI FITOSANITARI DIFESA INTEGRATA Inolizione – inizio invaiatura. OLIVO Bollettino n. 29 del…»
- «…Mosca dell’olivo (Bactrocera oleae): il monitoraggio della settimana evidenzia una pressione stabile. Le tempera…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `SERVIZIO FITOSANITARIO REGIONE VENETO`
- `BOLLETTINI FITOSANITARI DIFESA INTEGRATA`
- `OLIVO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 20 / 46

```
ITEM_ID        RAW-0be2d204c98ad1b1.txt
SOURCE_ID      IT-T2-002
PUBLISHER      ARPAV
CONTENT_PATH   data/derivados/texto/RAW-0be2d204c98ad1b1.txt
PARENT         data/collection-store/italy/IT-T2-002/ARPAV_Z24_20260902152048/v1_0be2d204c98a/agro_24.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 5492
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> Agrometeo… Informa

**ABERTURA DO DOCUMENTO**

```text
Agrometeo… Informa Zona 24 Alto Polesine N° 54 02/09/26 Il tempo previsto nei prossimi giorni Evoluzione Generale Torna ad espandersi un promontorio anticiclonico con aria calda; per il Veneto le condizioni sono generalmente stabili con parecchi spazi di sereno, a fronte di temporanei annuvolamenti più che altro in montagna, ove è possibile qualche locale precipitazione mercoledì dal pomeriggio e a tratti nel fine settimana; temperature in genere ben superiori alla norma. https://meteo.arpa.veneto.it/?page=MV Probabilita' Precipitazioni Venti Temperatura giovedì 3 Mattina Pomeriggio Nulla 0% Deboli Orientali Min = Max  venerdì 4 Mattina Pomeriggio sabato 5 Mattina Pomeriggio Nulla 0% Deboli Variabili Min  Max  Nulla 0% Deboli Variabili Min  Max = Informazioni agroclimatiche e territoriali Temperatura aria 2m (°C) ultimi 4 g. 34 32 30 28 26 24 22 20 18 SAB DOM LUN MAR Bagnolo di Po Ca
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `SAB`
- `DOM`
- `LUN`
- `MAR`
- `RIEPILOGO DATI MESE DI AGOSTO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 21 / 46

```
ITEM_ID        RAW-fe3c922bfdfd7999.txt
SOURCE_ID      NAO SEI
PUBLISHER      ARPAV
CONTENT_PATH   data/derivados/texto/RAW-fe3c922bfdfd7999.txt
PARENT         data/samples/IT-ARPAV-VENETO/orticolo_22_260826.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 5126
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> Pag. 1 di 2

**ABERTURA DO DOCUMENTO**

```text
Pag. 1 di 2 SERVIZIO FITOSANITARIO REGIONE VENETO U.O. Fitosanitario BOLLETTINI FITOSANITARI DIFESA INTEGRATA COLTURE ORTICOLE Bollettino n. 22 del 26/08/2026 ORTICOLE IN PIENO CAMPO POMODORO DA INDUSTRIA Nella settimana dal 17 al 23 agosto si sono verificate precipitazioni sia all'inizio sia alla fine del periodo. L'umidità fogliare prolungata e l'abbassamento termico hanno creato le condizioni ideali per lo sviluppo di nuove infezioni di Peronospora e Alternaria. Si consiglia di eseguire un trattamento con Cimoxanil e Rame nei lotti in cui la raccolta è prevista tra 25-30 giorni. RADICCHIO (LUNGO E VARIEGATO PRECOCE RACCOLTE ENTRO METÀ OTTOBRE, LUNGO TARDIVO RACCOLTA ENTRO METÀ NOVEMBRE) Nei trapianti effettuati nel mese di luglio presenza di larve di nottue e piralidi. Le larve di nottue (Spodoptera spp) e della piralide defogliatrice (Udea ferrugalis) vivono gran parte della loro vit
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…Pag. 1 di 2 SERVIZIO FITOSANITARIO REGIONE VENETO U.O. Fitosanitario BOLLETTINI FITOSANITARI D…»
- «…2 SERVIZIO FITOSANITARIO REGIONE VENETO U.O. Fitosanitario BOLLETTINI FITOSANITARI DIFESA INTEGRATA COLTURE ORTICOLE B…»
- «…. Fitosanitario BOLLETTINI FITOSANITARI DIFESA INTEGRATA COLTURE ORTICOLE Bollettino n. 22 del 26/08/2026 ORTICOLE I…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `SERVIZIO FITOSANITARIO REGIONE VENETO`
- `BOLLETTINI FITOSANITARI DIFESA INTEGRATA`
- `COLTURE ORTICOLE`
- `ORTICOLE IN PIENO CAMPO`
- `CAVOLI (CAVOLI A INFIORESCENZA E CAVOLI A TESTA)`
- `ASPARAGO`
- `ORTICOLE IN SERRA`
- `MELANZANA`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 22 / 46

```
ITEM_ID        RAW-e6ec962a8a730ee4.txt
SOURCE_ID      NAO SEI
PUBLISHER      REGIONE LAZIO
CONTENT_PATH   data/derivados/texto/RAW-e6ec962a8a730ee4.txt
PARENT         data/samples/IT-BOLLETTINI-VPN-2026/pdf/LAZIO_LITORALE_VITERBESE.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 1216
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> Bollettino Fitosanitario

**ABERTURA DO DOCUMENTO**

```text
Bollettino Fitosanitario ZONA PROGETTUALE Litorale Viterbese AVVERSITA’ Mosca dell’olivo dal Bactrocera oleae al n. 08/2026 31/08/2026 06/09/2026 Fase fenologica: Condizioni meteo: Metodologia: Soglia di intervento: Rilievo infestazione: SVILUPPO DEI FRUTTI (Scala BBCH Olio 79) “Le drupe hanno raggiunto circa il 90% delle dimensioni finali.” NON FAVOREVOLI Temperature comprese tra 20 e 35°C; elevata percentuale di umidità relativa; Schiusa uova: T min 17° C – T max 30°. Voli notte di 16-17 ° C / giorno fino a 35° C Si esaminano 20 olive a pianta su 10 piante scelte a caso per cultivar per ettaro, un totale di 200 olive. Metodo Adulticida Olive da olio: 4-5% di punture fertili o 2 femmine ovigere/trappola/settimana Olive da mensa 1-2% di punture fertili (uova, larve, pupari) Attacco rilevato: 0-2% PRESCRIZIONE NON EFFETTUARE TRATTAMENTO Fonte dati climatici ARSIAL (SIARL) OP LATIUM Soc. C
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…Bollettino Fitosanitario ZONA PROGETTUALE Litorale Viterbese AVVERSITA’ Mosca dell’o…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `AVVERSITA’`
- `SVILUPPO DEI FRUTTI`
- `NON FAVOREVOLI`
- `PRESCRIZIONE`
- `NON EFFETTUARE TRATTAMENTO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 23 / 46

```
ITEM_ID        RAW-ec3108a2ed424702.txt
SOURCE_ID      NAO SEI
PUBLISHER      FONDAZIONE EDMUND MACH
CONTENT_PATH   data/derivados/texto/RAW-ec3108a2ed424702.txt
PARENT         data/samples/IT-BOLLETTINI-VPN-2026/pdf/TN_DIB25_28ago2026.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 22365
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> FONDAZIONE EDMUND MACH CENTRO TRASFERIMENTO TECNOLOGICO

**ABERTURA DO DOCUMENTO**

```text
FONDAZIONE EDMUND MACH CENTRO TRASFERIMENTO TECNOLOGICO Bollettino N.25 del 28 agosto 2026 Pag. 1 di 10 BOLLETTINO DIFESA INTEGRATA DI BASE La stagione invernale a cavallo tra il 2025 e il 2026 è stata caratterizzata da un dicembre più asciutto e caldo rispetto alla media climatica, seguito da un gennaio in controtendenza, complessivamente fresco e decisamente piovoso, e da un febbraio eccezionalmente caldo (il secondo più caldo degli ultimi 20 anni, superato solo dal record del 2024). La piovosità dei primi mesi del 2026 è stata invece più alta della media climatica, con eventi di carattere nevoso che si sono registrati anche in alcuni fondovalle. Nel complesso, l’inverno appena trascorso è risultato più caldo della media climatica di quasi 1 °C. Le temperature del mese di marzo sono state superiori alla media, mentre la piovosità inferiore. Nell’ultima parte del mese e nei primi giorni
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…28 agosto 2026 Pag. 1 di 10 BOLLETTINO DIFESA INTEGRATA DI BASE La stagione invernale a cavallo tra il 2025 e il 20…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `FONDAZIONE EDMUND MACH CENTRO TRASFERIMENTO TECNOLOGICO`
- `BOLLETTINO DIFESA INTEGRATA DI BASE`
- `DICEMBRE`
- `GENNAIO`
- `FEBBRAIO`
- `MARZO`
- `APRILE`
- `MAGGIO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 24 / 46

```
ITEM_ID        RAW-e5176df66216dfd0.txt
SOURCE_ID      IT-T3-011
PUBLISHER      AGRIOS
CONTENT_PATH   data/derivados/texto/RAW-e5176df66216dfd0.txt
PARENT         data/samples/IT-SOURCE-SAMPLES/IT-T3-011/0286_26_Agrios_Broschuere_Richtlinien_integrierte_Kernobstbau_IT_WEB.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 169773
LANGUAGE       it (o mesmo documento existe em de)
REVIEWABLE     YES
```

**TITULO**

> Produzione integrata nell’azienda agricola

**ABERTURA DO DOCUMENTO**

```text
Produzione integrata nell’azienda agricola DIRETTIVE PER LA FRUTTICOLTURA INTEGRATA 2026 Produzione integrata nell’azienda agricola 2 DIRETTIVE PER LA FRUTTICOLTURA INTEGRATA 2026 36a edizione Editore: AGRIOS - Gruppo di lavoro per la frutticoltura integrata dell’Alto Adige Casa della mela, Via Jakobi 1A, I-39018 Terlano (BZ) INDICE Definizione ed obiettivi della frutticoltura integrata.............................................pag. 7 PRODUZIONE INTEGRATA NELL’AZIENDA AGRICOLA Agricoltori formati professionalmente e consci dal punto di vista ecologico......................................................................................... pag. 10 Aree di compensazione ecologica e cura dei dintorni del frutteto................. pag. 10 Considerazioni per l’allestimento di un nuovo frutteto..................................... pag. 11 Concimazione.........................................
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…............................ pag. 21 La difesa integrata..................................…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `DIRETTIVE PER LA FRUTTICOLTURA INTEGRATA 2026`
- `INDICE`
- `DEFINIZIONE ED OBIETTIVI DELLA FRUTTICOLTURA INTEGRATA`
- `PRODUZIONE INTEGRATA NELL’AZIENDA AGRICOLA`
- `AREE DI COMPENSAZIONE ECOLOGICA E CURA DEI DINTORNI DEL FRUTTETO`
- `CONSIDERAZIONI PER L’ALLESTIMENTO DI UN NUOVO FRUTTETO`
- `CONCIMAZIONE`
- `A+B`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 25 / 46

```
ITEM_ID        PROD_FTS_6_20260907.csv
SOURCE_ID      IT-T4-001
PUBLISHER      MINISTERO DELLA SALUTE
CONTENT_PATH   data/collection-store/italy/IT-T4-001/MINSALUTE_FTS6_20260907/v1_9cd4d156369f/PROD_FTS_6_20260907.csv
PARENT         (o proprio documento e o bruto)
DOCUMENT_TYPE  CSV   BYTES 4594288
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> num_registrazione;denominazione_prodotto;ragione_sociale;indirizzo_sede_legale;cap_sede_legale;comune_sede_legale;provincia_sede_legale;indirizzo_sede_amministrativa;cap_sede_amministrativa;comune_sed

**ABERTURA DO DOCUMENTO**

```text
num_registrazione;denominazione_prodotto;ragione_sociale;indirizzo_sede_legale;cap_sede_legale;comune_sede_legale;provincia_sede_legale;indirizzo_sede_amministrativa;cap_sede_amministrativa;comune_sede_amministrativa;provincia_sede_amministrativa;data_registrazione;data_scadenza_autorizzazione;indicazioni_di_pericolo;attivita;codice_formulazione;descrizione_formulazione;sostanze_attive;contenuto_per_100g_di_prodotto;importazione_parallela;PFnPO;PFnPE;stato_amministrativo;motivo_della revoca;data_decreto_revoca;data_decorrenza_revoca
000001;ENOVIT;SIPCAM S.P.A.;VIA CARROCCIO, 8;20123;MILANO;MILANO;VIA SEMPIONE, 195;20016;PERO;MILANO;14/04/1970;-;-;-;DP;POLVERE;THIOPHANATE-METHYL;-;NO;NO;NO;Revocato;-;-;14/07/1983
000002;CONTRAX STANGE;KEMIO;VIA M. PANTALEONI, 31;00191;ROMA;ROMA;VIA M. PANTALEONI, 31;00191;ROMA;ROMA;21/01/1971;-;-;-;PR;BASTONCINO PER PIANTE;WARFARIN;-;NO;NO;NO;Revocato;REV
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- NONE

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 26 / 46

```
ITEM_ID        RAW-823e18ebb232eb36.txt
SOURCE_ID      NAO SEI
PUBLISHER      REGIONE LAZIO
CONTENT_PATH   data/derivados/texto/RAW-823e18ebb232eb36.txt
PARENT         data/samples/IT-BOLLETTINI-VPN-2026/pdf/LAZIO_ENTROTERRA_TUSCIA.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 1225
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> Bollettino Fitosanitario

**ABERTURA DO DOCUMENTO**

```text
Bollettino Fitosanitario ZONA PROGETTUALE Entroterra Viterbese-Tuscia AVVERSITA’ Mosca dell’olivo dal Bactrocera oleae al n. 08/2026 31/08/2026 06/09/2026 Fase fenologica: Condizioni meteo: Metodologia: Soglia di intervento: Rilievo infestazione: SVILUPPO DEI FRUTTI (Scala BBCH Olio 79) “Le drupe hanno raggiunto circa il 90% delle dimensioni finali.” NON FAVOREVOLI Temperature comprese tra 20 e 35°C; elevata percentuale di umidità relativa; Schiusa uova: T min 17° C – T max 30°. Voli notte di 16-17 ° C / giorno fino a 35° C Si esaminano 20 olive a pianta su 10 piante scelte a caso per cultivar per ettaro, un totale di 200 olive. Metodo Adulticida Olive da olio: 4-5% di punture fertili o 2 femmine ovigere/trappola/settimana Olive da mensa 1-2% di punture fertili (uova, larve, pupari) Attacco rilevato: 0-1% PRESCRIZIONE NON EFFETTUARE TRATTAMENTO Fonte dati climatici ARSIAL (SIARL) OP LATI
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…Bollettino Fitosanitario ZONA PROGETTUALE Entroterra Viterbese-Tuscia AVVERSITA’ Mos…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `AVVERSITA’`
- `SVILUPPO DEI FRUTTI`
- `NON FAVOREVOLI`
- `PRESCRIZIONE`
- `NON EFFETTUARE TRATTAMENTO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 27 / 46

```
ITEM_ID        RAW-59da05274359eff6.txt
SOURCE_ID      IT-T3-010
PUBLISHER      APOL LECCE
CONTENT_PATH   data/derivados/texto/RAW-59da05274359eff6.txt
PARENT         data/collection-store/italy/IT-T3-010/APOL_2026_N9_BR-COLLINA/v1_59da05274359/Bollettino_Mosca_dellOlivo_n_9_del_07_09_2026.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 26083
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> INGROSSAMENTO FRUTTI

**ABERTURA DO DOCUMENTO**

```text
INGROSSAMENTO FRUTTI 7 9 MOSCA DELLE OLIVE 07/09/2026 - 13/09/2026 COMPRENSORIO - BR - COLLINA LITORANEA BRINDISI CAROVIGNO CEGLIE MESSAPICA CELLINO SAN MARCO FASANO FRANCAVILLA FONTANA MESAGNE ORIA OSTUNI SAN DONACI SAN VITO DEI NORMANNI TORCHIAROLO TORRE SANTA SUSANNA VILLA CASTELLI SAN GIORGIO IONICO 1 5% STAZIONARIO BASSO 07/09/2026 08/09/2026 09/09/2026 10/09/2026 11/09/2026 12/09/2026 13/09/2026 I monitoraggi territoriali settimanali indicano una situazione complessivamente sotto controllo; non si sono rilevate raggiungimenti o superamenti della soglia di intervento con pochissime punture fertili e ancora un basso numero di individui riscontrati sulle trappole a feromoni installate. Da metà della prossima settimana si verificherà un cambio meteo a causa di una perturbazione nord-europea che porterà una diminuzione delle temperature sotto i 27-28°C con possibili brevi piogge. Questo
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `INGROSSAMENTO FRUTTI`
- `MOSCA DELLE OLIVE`
- `COMPRENSORIO - BR - COLLINA LITORANEA`
- `STAZIONARIO`
- `BASSO`
- `COMPRENSORIO - LE - PIANURA SALENTINA NORD`
- `NARDO' NOVOLI`
- `SALICE SALENTINO SURBO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 28 / 46

```
ITEM_ID        monitoraggio.html
SOURCE_ID      IT-T3-005
PUBLISHER      TERRE DELL'ETRURIA
CONTENT_PATH   data/collection-store/italy/IT-T3-005/TERRETRURIA_31-08-2026_06-09-2026/v1_2e488a8232ba/monitoraggio.html
PARENT         (o proprio documento e o bruto)
DOCUMENT_TYPE  HTML   BYTES 274247
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> Monitoraggio mosca dell'olivo toscana

**ABERTURA DO DOCUMENTO**

```text
--> Monitoraggio mosca dell'olivo toscana --> Navigazione Veloce --> --> Chiudi Navigazione Home Negozio Online Contatti News Area Riservata CdA --> Soci --> Area Riservata Soci/Clienti Applicazioni Interne Assistenza --> --> Shop Contatti Comunicazioni Lavora con noi Tradizione | Innovazione | Rispetto | Memoria Prendiamo il meglio della tradizione e la rinnoviamo, sempre guidati dal rispetto per il nostro territorio. Vogliamo vivere il presente e preparare il nostro futuro con una importante consapevolezza: il domani sarà migliore se innoveremo, proteggendo la tradizione. --> --> Home Monitoraggio --> Mostra Menu Home La Cooperativa Chi Siamo La Storia Storia per immagini Sede / Contatti Punti Vendita e Magazzini Lavora con noi Bilancio di Sostenibilità Settori Produttivi Olio Vino Ortofrutta Cereali Trasformati Agroforniture Tracciabilità MediaRoom Eventi / News La Cooperativa Informa
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…--> Monitoraggio mosca dell'olivo toscana --> Navigazione Veloce --> --> Chi…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `ACCETTA TUTTI I COOKIE`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 29 / 46

```
ITEM_ID        RAW-48e76a696be6831d.txt
SOURCE_ID      IT-T3-002
PUBLISHER      REGIONE CAMPANIA
CONTENT_PATH   data/derivados/texto/RAW-48e76a696be6831d.txt
PARENT         data/samples/IT-SOURCE-SAMPLES/IT-T3-002/NA-02-09.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 27024
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> ASSESSORATO AGRICOLTURA

**ABERTURA DO DOCUMENTO**

```text
ASSESSORATO AGRICOLTURA GIUNTA REGIONALE DELLA CAMPANIA DIREZIONE GENERALE POLITICHE AGRICOLE ALIMENTARI E FORESTALISETTORE 207.03.03 - AMBIENTE, SVILUPPO LOCALE, SISTEMA DELLA CONOSCENZA E DIFESA DELLE COLTURE SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI NAPOLI Areali: Piana Campana (Acerra e San Vitaliano) Piana Flegrea (Giugliano in Campania) Colline Flegree (Bacoli, Calvizzano e Qualiano) Pubblicazione di orientamento e consulenza per la difesa integrata delle colture che, sulla base dei risultati della rete di monitoraggio, fornisce informazioni sull’applicazione della difesa integrata Bollettino N° 25 del 2/9/2026 Andamento meteorologico Per la provincia di Napoli sono disponibili i dati delle stazioni della Rete Agrometeorologica di Acerra, Boscotrecase, San Gennaro Vesuviano, Casalnuovo loc. Casarea e Barano d’Ischia sul sito P
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…ANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI NAPOLI Areali: Piana Campana (Acerra e S…»
- «…DELLA CONOSCENZA E DIFESA DELLE COLTURE SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DEL…»
- «…one di orientamento e consulenza per la difesa integrata delle colture che, sulla base dei risultati della rete di m…»
- «…UPPO LOCALE, SISTEMA DELLA CONOSCENZA E DIFESA DELLE COLTURE SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLE…»
- «…sulla base dei risultati della rete di monitoraggio, fornisce informazioni sull’applicazione della difesa integ…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `ASSESSORATO AGRICOLTURA`
- `BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI NAPOLI`
- `COLTURA PESCO NETTARINA`
- `CONSIGLI DI DIFESA FITOSANITARIA`
- `COLTURA NOCCIOLO`
- `COLTURA NOCE`
- `UTM`
- `COLTURA CILIEGIO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 30 / 46

```
ITEM_ID        RAW-ccd8ea9c8e9c4caf.txt
SOURCE_ID      NAO SEI
PUBLISHER      FONDAZIONE EDMUND MACH
CONTENT_PATH   data/derivados/texto/RAW-ccd8ea9c8e9c4caf.txt
PARENT         data/samples/IT-BOLLETTINI-VPN-2026/pdf/TN_DIB24_21ago2026.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 20424
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> FONDAZIONE EDMUND MACH CENTRO TRASFERIMENTO TECNOLOGICO

**ABERTURA DO DOCUMENTO**

```text
FONDAZIONE EDMUND MACH CENTRO TRASFERIMENTO TECNOLOGICO Bollettino N.24 del 21 agosto 2026 Pag. 1 di 10 BOLLETTINO DIFESA INTEGRATA DI BASE La stagione invernale a cavallo tra il 2025 e il 2026 è stata caratterizzata da un dicembre più asciutto e caldo rispetto alla media climatica, seguito da un gennaio in controtendenza, complessivamente fresco e decisamente piovoso, e da un febbraio eccezionalmente caldo (il secondo più caldo degli ultimi 20 anni, superato solo dal record del 2024). La piovosità dei primi mesi del 2026 è stata invece più alta della media climatica, con eventi di carattere nevoso che si sono registrati anche in alcuni fondovalle. Nel complesso, l’inverno appena trascorso è risultato più caldo della media climatica di quasi 1 °C. Le temperature del mese di marzo sono state superiori alla media, mentre la piovosità inferiore. Nell’ultima parte del mese e nei primi giorni
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…21 agosto 2026 Pag. 1 di 10 BOLLETTINO DIFESA INTEGRATA DI BASE La stagione invernale a cavallo tra il 2025 e il 20…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `FONDAZIONE EDMUND MACH CENTRO TRASFERIMENTO TECNOLOGICO`
- `BOLLETTINO DIFESA INTEGRATA DI BASE`
- `DICEMBRE`
- `GENNAIO`
- `FEBBRAIO`
- `MARZO`
- `APRILE`
- `MAGGIO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 31 / 46

```
ITEM_ID        RAW-3e941738599367d7.txt
SOURCE_ID      IT-T3-010
PUBLISHER      APOL LECCE
CONTENT_PATH   data/derivados/texto/RAW-3e941738599367d7.txt
PARENT         data/samples/IT-SOURCE-SAMPLES/IT-T3-010/Bollettino_Mosca_dellOlivo_n_8_del_31_08_2026.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 26290
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> INGROSSAMENTO FRUTTI

**ABERTURA DO DOCUMENTO**

```text
INGROSSAMENTO FRUTTI 11 8 MOSCA DELLE OLIVE 31/08/2026 - 06/09/2026 COMPRENSORIO - BR - COLLINA LITORANEA BRINDISI CAROVIGNO CEGLIE MESSAPICA CELLINO SAN MARCO FASANO FRANCAVILLA FONTANA MESAGNE ORIA OSTUNI SAN DONACI SAN VITO DEI NORMANNI TORCHIAROLO TORRE SANTA SUSANNA VILLA CASTELLI SAN GIORGIO IONICO 2 5% STAZIONARIO MEDIO 31/08/2026 01/09/2026 02/09/2026 03/09/2026 04/09/2026 05/09/2026 06/09/2026 Sulla base dei dati osservati dal monitoraggio settimanale sul grado d’infestazione della mosca dell’olivo (bractocera oleae) rileviamo un piccolo aumento delle punture fertili e ancora un basso numero di individui riscontrati sulle trappole a feromoni installate. L’imperversare dell’anticiclone subtropicale causa gravi periodi di siccità con deficit idrico che alterano la consistenza e i componenti chimici della polpa dell'oliva, rendendo la drupa disidratata, dura e priva dei succhi nece
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…/2026 Sulla base dei dati osservati dal monitoraggio settimanale sul grado d’infestazione della mosca dell’olivo…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `INGROSSAMENTO FRUTTI`
- `MOSCA DELLE OLIVE`
- `COMPRENSORIO - BR - COLLINA LITORANEA`
- `STAZIONARIO`
- `MEDIO`
- `COMPRENSORIO - LE - PIANURA SALENTINA NORD`
- `NARDO' NOVOLI`
- `SALICE SALENTINO SURBO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 32 / 46

```
ITEM_ID        RAW-024abdb692be926a.txt
SOURCE_ID      NAO SEI
PUBLISHER      REGIONE MOLISE
CONTENT_PATH   data/derivados/texto/RAW-024abdb692be926a.txt
PARENT         data/samples/IT-BOLLETTINI-VPN-2026/pdf/MOLISE_comunicato_5_2026.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 21561
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> REGIONE MOLISE

**ABERTURA DO DOCUMENTO**

```text
REGIONE MOLISE PRESIDENZA DELLA GIUNTA REGIONALE COORDINAMENTO AREA II SERVIZIO FITOSANITARIO REGIONALE - TUTELA E VALORIZZAZIONE DELLA MONTAGNA E DELLE FORESTE, BIODIVERSITA’ AGRICOLA E GESTIONE FITO-SANITARIA Ufficio Vigilanza Produzioni Biologiche ed Ecosostenibili Prodotti Fitosanitari, Certificazione Materiale Forestale, Ricerca e Sperimentazione in materia di Tartufi Via G. Vico,4- 86100 Campobasso-tel.0874-4291 Via Morrone, 48 Larino (CB) Tel. 0874-824617 regionemolise@cert.regione.molise.it Oggetto: Comunicato fitosanitario 5 Con D.D. 1951/26 e successiva integrazione degli aggiornamenti approvati per l’anno 2026 di cui alla DD n. 2546 del 5 Maggio 2026, si è provveduto alla formale approvazione dei Disciplinari di Produzione Integrata 2026 – Difesa e Tecniche Agronomiche. Per ogni esigenza operativa dei produttori interessati si comunica che, la Regione Molise, aderisce integral
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…GIUNTA REGIONALE COORDINAMENTO AREA II SERVIZIO FITOSANITARIO REGIONALE - TUTELA E VALORIZZAZIONE DELLA MONTAGNA E DELLE…»
- «…e agricole convenzionali, soggette alla Difesa Integrata obbligatoria e che non aderiscono ad alcun Sistema Qualita’…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `REGIONE MOLISE`
- `PRESIDENZA DELLA GIUNTA REGIONALE COORDINAMENTO AREA II`
- `FORESTE, BIODIVERSITA’ AGRICOLA E GESTIONE FITO-SANITARIA`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 33 / 46

```
ITEM_ID        NHEOWL0530_00.html
SOURCE_ID      IT-T2-004
PUBLISHER      SIAS
CONTENT_PATH   data/collection-store/italy/IT-T2-004/SIAS_PRECIPITAZIONE_GIORNALIERA_WINDOW_END_2026-09-05/v1_6c71cc191272/NHEOWL0530_00.html
PARENT         (o proprio documento e o bruto)
DOCUMENT_TYPE  HTML   BYTES 79628
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> Consultazione per grandezza

**ABERTURA DO DOCUMENTO**

```text
Consultazione per grandezza Home &gt; Dati &gt; Consultazione per grandezza &gt; Tutta la regione > Precipitazioni giornaliere Metadati Precipitazioni giornaliere (mm) dal 26/08/2026 al 05/09/2026 Le ore di rilevazione sono espresse secondo l'orario di Greenwich (U.T.C.) L'ora italiana solare (o legale) � l'ora di Greenwich +1 (o +2) Stazioni 26 Ago 2026 27 Ago 2026 28 Ago 2026 29 Ago 2026 30 Ago 2026 31 Ago 2026 01 Set 2026 02 Set 2026 03 Set 2026 04 Set 2026 05 Set 2026 Ultimo giorno piovoso * Precipitazioni cumulate dal 1 gen ** Calatafimi 0 0 0 0 0 0 0 0 0 0 -- 16/08/2026 -- Castellammare del Golfo 0 0 0 0 0 0 0 0 0 0 -- 15/08/2026 -- Castelvetrano 0 0 0 0 0 0 0 0 0 0 -- 15/08/2026 -- Erice 0 0 0 0 0 0 0 0 0 0 -- 03/07/2026 -- Marsala 0 0 0 0 0 0 0 0.2 0 0 -- 25/08/2026 -- Mazara del Vallo 0 0 0 0 0 0 0 0 0 0 -- 15/08/2026 -- Pantelleria 0 0 0 0 0 0 0 0 0 0 -- 27/07/2026 -- Salemi 0 
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- NONE

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 34 / 46

```
ITEM_ID        RAW-178ebe9e0ea7dd83.txt
SOURCE_ID      IT-T3-008
PUBLISHER      ARIF PUGLIA
CONTENT_PATH   data/derivados/texto/RAW-178ebe9e0ea7dd83.txt
PARENT         data/samples/IT-SOURCE-SAMPLES/IT-T3-008/Giornaliero_Meteorologico_N136_07-09-2026.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 11196
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> N. 136 Anno XL

**ABERTURA DO DOCUMENTO**

```text
N. 136 Anno XL Del 07-09-2026 ore 10:00 VVaalliiddiittàà:: 55 ggiioorrnnii Agenzia regionale per le attività irrigue e forestali Situazione Attuale Attualmente la situazione euro atlantica rimane caratterizzata dal ﬂusso principale che scorre sopra il 45°N delimitando due saccature: la prima ad ovest che discende dalla Groenlandia ﬁno al medio Atlantico con il suo minimo posizionato tra le isole britanniche e l'Islanda; la seconda verso est che da Circolo Polare Artico attraversa la Scandinavia e poi si spinge sui Paesi dell'Est sino al Mar Nero. Alle basse latitudini si riscontra la presenza dell'alta pressione dell'anticiclone atlantico ancora caratterizzato da masse di aria calda nei bassi strati che dall'entroterra algerino e tunisino del nord Africa risalgono sul Mediterraneo e su gran parte dell'Italia con conseguenti temperature ben al di sopra della media del periodo e tempo stab
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `DATA`
- `CIELO`
- `ORE 00:00`
- `ORE 12:00`
- `FOGGIA`
- `SAN NICANDRO GARGANICO`
- `ANDRIA`
- `BARI`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 35 / 46

```
ITEM_ID        RAW-3ef48aaa830edf3b.txt
SOURCE_ID      IT-T3-008
PUBLISHER      ARIF PUGLIA
CONTENT_PATH   data/derivados/texto/RAW-3ef48aaa830edf3b.txt
PARENT         data/samples/IT-SOURCE-SAMPLES/IT-T3-008/Notiziario_Agrometeorologico_N35_26-08-2026.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 70625
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> Settimanale N. 35 Anno XL

**ABERTURA DO DOCUMENTO**

```text
Settimanale N. 35 Anno XL 26 - 01 settembre 2026 Agenzia regionale per le attività irrigue e forestali Situazione Attuale La situazione euro atlantica mostra alle latitudini nordiche il ﬂusso perturbato principale delimitato da due saccature di origine polare: la prima discende, in senso meridiano, dal mar del Labrador e la Groenlandia nel medio Atlantico sino al Portogallo, la seconda più ad est interessa invece l'area tra il mare di Barents e la pianura russa. Fra le due aree depressionarie si inserisce un vasto promontorio con il suo massimo posizionato sulla penisola scandinava. Sul resto dello scenario, sul Mediterraneo occidentale è presente il ﬂusso sub-tropicale delimitato da un esteso promontorio nord africano che risale dall'entroterra libico sull'Italia meridionale apportando masse d'aria particolarmente calde con conseguente aumento della temperatura su valori termici molto a
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `DATA`
- `CIELO`
- `VENTO`
- `TEMP. UMID.`
- `ORE 00:00 ORE 12:00`
- `ORE 00:00`
- `FOGGIA`
- `SAN NICANDRO GARGANICO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 36 / 46

```
ITEM_ID        RAW-f88c89d73d6a132a.txt
SOURCE_ID      IT-T2-002
PUBLISHER      ARPAV
CONTENT_PATH   data/derivados/texto/RAW-f88c89d73d6a132a.txt
PARENT         data/collection-store/italy/IT-T2-002/ARPAV_Z01_20260903160930/v1_f88c89d73d6a/agro_01.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 5346
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> Agrometeo… Informa

**ABERTURA DO DOCUMENTO**

```text
Agrometeo… Informa Zona 1 Vittorio Veneto-Conegliano N° 54 03/09/26 Il tempo previsto nei prossimi giorni Evoluzione Generale L'estensione dell'Anticiclone Subtropicale Africano verso le nostre latitudini persisterà almeno fino a lunedì. Le temperature sopra la media anche di molto continueranno ad essere la caratteristica meteorologica saliente; in particolare saranno in aumento fino a domenica mattina e poi in calo. https://meteo.arpa.veneto.it/?page=MV Probabilita' Precipitazioni Venti Temperatura venerdì 4 Mattina Pomeriggio Nulla 0% Deboli/Moderati-Variabili Min  Max  sabato 5 Mattina Pomeriggio domenica 6 Mattina Pomeriggio Nulla 0% Deboli/Moderati-Variabili Min  Max  Nulla 0% Deboli/Moderati-Variabili Min  Max  Informazioni agroclimatiche e territoriali Temperatura aria 2m (°C) ultimi 4 g. 34 32 30 28 26 24 22 20 18 16 DOM LUN MAR MER Conegliano Gaiarine Umidità rel. aria 2m
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `DOM`
- `LUN`
- `MAR`
- `MER`
- `RIEPILOGO DATI MESE DI AGOSTO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 37 / 46

```
ITEM_ID        RAW-0c2723e66201f966.txt
SOURCE_ID      IT-T3-002
PUBLISHER      REGIONE CAMPANIA
CONTENT_PATH   data/derivados/texto/RAW-0c2723e66201f966.txt
PARENT         data/collection-store/italy/IT-T3-002/CAMPANIA_SA_02-09-2026/v1_0c2723e66201/SA-02-09.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 26832
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> GIUNTA REGIONALE DELLA CAMPANIA DIREZIONE GENERALE E POLITICHE AGRICOLE, ALIMENTARI E FORESTALI UOS2070303- DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE

**ABERTURA DO DOCUMENTO**

```text
GIUNTA REGIONALE DELLA CAMPANIA DIREZIONE GENERALE E POLITICHE AGRICOLE, ALIMENTARI E FORESTALI UOS2070303- DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI SALERNO Pubblicazione di orientamento e consulenza per la difesa integrata delle colture che, sulla base dei risultati della rete di monitoraggio, fornisce informazioni sull’applicazione della difesa integrata N° 25 del 02/09/2026 Andamento meteorologico Per la provincia di Salerno sono disponibili i dati delle stazioni della Rete Agrometeorologica Regionale di Battipaglia, Capaccio fraz. Gromola, Controne, Eboli, Serre sul sito Portale dell’Agricoltura alla pagina: http://agricoltura.regione.campania.it/meteo/meteo_2026.html Stato fitosanitario delle colture COLTURA N° Comune 1 Eboli ACTINIDIA UTM Località Azienda Pennatone Idea Natura Varietà Stadio fenologico S
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…ANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI SALERNO Pubblicazione di orientamento e…»
- «…STALI UOS2070303- DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DEL…»
- «…one di orientamento e consulenza per la difesa integrata delle colture che, sulla base dei risultati della rete di m…»
- «…OLE, ALIMENTARI E FORESTALI UOS2070303- DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLL…»
- «…sulla base dei risultati della rete di monitoraggio, fornisce informazioni sull’applicazione della difesa integ…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `SICUREZZA ALIMENTARE`
- `BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI SALERNO`
- `ACTINIDIA UTM`
- `CONSIGLI DI DIFESA FITOSANITARIA`
- `AGRUMI`
- `COLTURA`
- `CILIEGIO`
- `TRAMONTI`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 38 / 46

```
ITEM_ID        RAW-a6515948880d173a.txt
SOURCE_ID      NAO SEI
PUBLISHER      REGIONE LAZIO
CONTENT_PATH   data/derivados/texto/RAW-a6515948880d173a.txt
PARENT         data/samples/IT-BOLLETTINI-VPN-2026/pdf/LAZIO_SABINA.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 1209
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> Bollettino Fitosanitario

**ABERTURA DO DOCUMENTO**

```text
Bollettino Fitosanitario ZONA PROGETTUALE SABINA AVVERSITA’ Mosca dell’olivo dal Bactrocera oleae al n. 09/2026 31/08/2026 06/08/2026 Fase fenologica: Condizioni meteo: Metodologia: Soglia di intervento: Rilievo infestazione: SVILUPPO DEI FRUTTI (Scala BBCH Olio 79) “Le drupe hanno raggiunto circa il 90% delle dimensioni finali.” Temperature comprese tra 20 e 35°C; elevata percentuale di NON FAVOREVOLI umidità relativa; Schiusa uova: T min 17° C – T max 30°. Voli notte di 16-17 ° C / giorno fino a 35° C Si esaminano 20 olive a pianta su 10 piante scelte a caso per cultivar per ettaro, un totale di 200 olive. Metodo Adulticida Olive da olio: 4-5% di punture fertili o 2 femmine ovigere/trappola/settimana Olive da mensa 1-2% di punture fertili (uova, larve, pupari) Attacco rilevato: 0-1% PRESCRIZIONE NON EFFETTUARE TRATTAMENTO Fonte dati climatici ARSIAL (SIARL) OP LATIUM Soc. Coop. Agr. Qu
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…Bollettino Fitosanitario ZONA PROGETTUALE SABINA AVVERSITA’ Mosca dell’olivo dal Bac…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `ZONA PROGETTUALE SABINA`
- `AVVERSITA’`
- `SVILUPPO DEI FRUTTI`
- `NON FAVOREVOLI`
- `PRESCRIZIONE`
- `NON EFFETTUARE TRATTAMENTO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 39 / 46

```
ITEM_ID        RAW-392840d3e13d1b15.txt
SOURCE_ID      NAO SEI
PUBLISHER      REGIONE LAZIO
CONTENT_PATH   data/derivados/texto/RAW-392840d3e13d1b15.txt
PARENT         data/samples/IT-BOLLETTINI-VPN-2026/pdf/LAZIO_BOLSENA.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 1213
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> Bollettino Fitosanitario

**ABERTURA DO DOCUMENTO**

```text
Bollettino Fitosanitario ZONA PROGETTUALE Lago di Bolsena AVVERSITA’ Mosca dell’olivo dal Bactrocera oleae al n. 08/2026 31/08/2026 06/09/2026 Fase fenologica: Condizioni meteo: Metodologia: Soglia di intervento: Rilievo infestazione: SVILUPPO DEI FRUTTI (Scala BBCH Olio 79) “Le drupe hanno raggiunto circa il 90% delle dimensioni finali.” NON FAVOREVOLI Temperature comprese tra 20 e 35°C; elevata percentuale di umidità relativa; Schiusa uova: T min 17° C – T max 30°. Voli notte di 16-17 ° C / giorno fino a 35° C Si esaminano 20 olive a pianta su 10 piante scelte a caso per cultivar per ettaro, un totale di 200 olive. Metodo Adulticida Olive da olio: 4-5% di punture fertili o 2 femmine ovigere/trappola/settimana Olive da mensa 1-2% di punture fertili (uova, larve, pupari) Attacco rilevato: 0-1% PRESCRIZIONE NON EFFETTUARE TRATTAMENTO Fonte dati climatici ARSIAL (SIARL) OP LATIUM Soc. Coop
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…Bollettino Fitosanitario ZONA PROGETTUALE Lago di Bolsena AVVERSITA’ Mosca dell’oliv…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `AVVERSITA’`
- `SVILUPPO DEI FRUTTI`
- `NON FAVOREVOLI`
- `PRESCRIZIONE`
- `NON EFFETTUARE TRATTAMENTO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 40 / 46

```
ITEM_ID        RAW-223510588786a4de.txt
SOURCE_ID      NAO SEI
PUBLISHER      ARPAV
CONTENT_PATH   data/derivados/texto/RAW-223510588786a4de.txt
PARENT         data/samples/IT-ARPAV-VENETO/vite_19_130826.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 12151
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> U.O. Fitosanitario

**ABERTURA DO DOCUMENTO**

```text
U.O. Fitosanitario Bollettino n. 19 del 13 agosto 2026 VITE Andamento meteo (in collaborazione col Servizio Meteorologia e Climatologia di Arpav): Settimana tipicamente estiva con giornate calde e afose con qualche episodio temporalesco sparso sul territorio veneto. Le temperature massime e minime medie rispettivamente sono risultate comprese tra 34-38°C e tra 22-26°C. Le precipitazioni hanno interessato parte del territorio veneto ma mediamente di scarsa entità (< 10 mm), solo localmente in maniera più importante (30-50 mm). Le medie settimanali delle temperature massime e minime rispetto alla media del periodo storico, fanno registrare valori superiori alla norma rispettivamente di 3-5°C e 2-4°C a seconda delle zone. PRECIPITAZIONI E GIORNI PIOVOSI DAL 05/08 AL 11/08 – ARPAV MEDIA DELLE TEMPERATURE MASSIME E MINIME DAL 05/08 al 11/08 - ARPAV SCARTO TEMPERATURE MAX E MIN RISPETTO ALLA N
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…U.O. Fitosanitario Bollettino n. 19 del 13 agosto 2026 VITE Andamento meteo (i…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `VITE`
- `PRECIPITAZIONI E GIORNI PIOVOSI DAL 05/08 AL 11/08 – ARPAV`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 41 / 46

```
ITEM_ID        RAW-df4adcb5d78929e1.txt
SOURCE_ID      NAO SEI
PUBLISHER      REGIONE CAMPANIA
CONTENT_PATH   data/derivados/texto/RAW-df4adcb5d78929e1.txt
PARENT         data/samples/IT-BOLLETTINI-VPN-2026/pdf/CAMP_BN-26-08.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 23291
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> GIUNTA REGIONALE DELLA CAMPANIA DIREZIONE GENERALE E POLITICHE AGRICOLE, ALIMENTARI E FORESTALI UOS 207.03.03 - DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA

**ABERTURA DO DOCUMENTO**

```text
GIUNTA REGIONALE DELLA CAMPANIA DIREZIONE GENERALE E POLITICHE AGRICOLE, ALIMENTARI E FORESTALI UOS 207.03.03 - DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI BENEVENTO Pubblicazione di orientamento e consulenza per la difesa integrata delle colture che, sulla base dei risultati della rete di monitoraggio, fornisce informazioni sull’applicazione della difesa integrata N. 24 del 26 Agosto 2026 Andamento meteorologico Per la provincia di Avellino sono disponibili i dati delle stazioni della Rete Agrometeorologica Regionale di Airola, Apice, Casalduni, Castelvetere in Val Fortore, Faicchio, Guardia Sanframondi Massa di Faicchio, San Lorenzo maggiore, San Marco de Cavoti, Torrecuso sul sito Portale dell’Agricoltura alla pagina: http://agricoltura.regione.campania.it/meteo/meteo_2026.html Stato fitosanitario delle coltur
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…ANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI BENEVENTO Pubblicazione di orientamento…»
- «…I UOS 207.03.03 - DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DEL…»
- «…one di orientamento e consulenza per la difesa integrata delle colture che, sulla base dei risultati della rete di m…»
- «…ALIMENTARI E FORESTALI UOS 207.03.03 - DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLL…»
- «…sulla base dei risultati della rete di monitoraggio, fornisce informazioni sull’applicazione della difesa integ…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `ALIMENTARE`
- `CONSIGLI DI DIFESA`
- `ULTERIORI CRITERI DI INTERVENTO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 42 / 46

```
ITEM_ID        RAW-e9395a7ea894c1d2.txt
SOURCE_ID      NAO SEI
PUBLISHER      REGIONE CAMPANIA
CONTENT_PATH   data/derivados/texto/RAW-e9395a7ea894c1d2.txt
PARENT         data/samples/IT-BOLLETTINI-VPN-2026/pdf/CAMP_CE-26-08.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 37924
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> GIUNTA REGIONALE DELLA CAMPANIA DIREZIONE GENERALE E POLITICHE AGRICOLE, ALIMENTARI E FORESTALI UOS2070303- DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE

**ABERTURA DO DOCUMENTO**

```text
GIUNTA REGIONALE DELLA CAMPANIA DIREZIONE GENERALE E POLITICHE AGRICOLE, ALIMENTARI E FORESTALI UOS2070303- DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI CASERTA Pubblicazione di orientamento e consulenza per la difesa integrata delle colture che, sulla base dei risultati della rete di monitoraggio, fornisce informazioni sull’applicazione della difesa integrata N° 24 del 26/08/2026 Andamento meteorologico Per la provincia di Caserta sono disponibili i dati delle stazioni della Rete Agrometeorologica Regionale di Alife, Carinola, Conca della Campania, Falciano del Massico, Pignataro Maggiore e Vitulazio sul sito Portale dell’Agricoltura alla pagina: http://agricoltura.regione.campania.it/meteo/meteo_2026.html COLTURA N° Comune Francolise 2 Aurunca Sessa Stato fitosanitario delle colture PESCO UTM Località Varietà St
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…ANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI CASERTA Pubblicazione di orientamento e…»
- «…STALI UOS2070303- DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLLETTINO FITOSANITARIO DEL…»
- «…one di orientamento e consulenza per la difesa integrata delle colture che, sulla base dei risultati della rete di m…»
- «…OLE, ALIMENTARI E FORESTALI UOS2070303- DIFESA DELLE COLTURE, SERVIZIO FITOSANITARIO REGIONALE SICUREZZA ALIMENTARE BOLL…»
- «…sulla base dei risultati della rete di monitoraggio, fornisce informazioni sull’applicazione della difesa integ…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `SICUREZZA ALIMENTARE`
- `BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI CASERTA`
- `PESCO`
- `CONSIGLI DI DIFESA FITOSANITARIA`
- `COLTURA`
- `TICCHIOLATURA`
- `CARPOCAPSA`
- `VITE`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 43 / 46

```
ITEM_ID        RAW-221ab4a8d6ebec30.txt
SOURCE_ID      NAO SEI
PUBLISHER      FONDAZIONE EDMUND MACH
CONTENT_PATH   data/derivados/texto/RAW-221ab4a8d6ebec30.txt
PARENT         data/samples/IT-BOLLETTINI-VPN-2026/pdf/TN_DIB23_14ago2026.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 21662
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> FONDAZIONE EDMUND MACH CENTRO TRASFERIMENTO TECNOLOGICO

**ABERTURA DO DOCUMENTO**

```text
FONDAZIONE EDMUND MACH CENTRO TRASFERIMENTO TECNOLOGICO Bollettino N.23 del 14 agosto 2026 Pag. 1 di 10 BOLLETTINO DIFESA INTEGRATA DI BASE La stagione invernale a cavallo tra il 2025 e il 2026 è stata caratterizzata da un dicembre più asciutto e caldo rispetto alla media climatica, seguito da un gennaio in controtendenza, complessivamente fresco e decisamente piovoso, e da un febbraio eccezionalmente caldo (il secondo più caldo degli ultimi 20 anni, superato solo dal record del 2024). La piovosità dei primi mesi del 2026 è stata invece più alta della media climatica, con eventi di carattere nevoso che si sono registrati anche in alcuni fondovalle. Nel complesso, l’inverno appena trascorso è risultato più caldo della media climatica di quasi 1 °C. Le temperature del mese di marzo sono state superiori alla media, mentre la piovosità inferiore. Nell’ultima parte del mese e nei primi giorni
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…14 agosto 2026 Pag. 1 di 10 BOLLETTINO DIFESA INTEGRATA DI BASE La stagione invernale a cavallo tra il 2025 e il 20…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `FONDAZIONE EDMUND MACH CENTRO TRASFERIMENTO TECNOLOGICO`
- `BOLLETTINO DIFESA INTEGRATA DI BASE`
- `DICEMBRE`
- `GENNAIO`
- `FEBBRAIO`
- `MARZO`
- `APRILE`
- `MAGGIO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 44 / 46

```
ITEM_ID        RAW-445e41701f737d73.txt
SOURCE_ID      IT-T2-001
PUBLISHER      ARPAE
CONTENT_PATH   data/derivados/texto/RAW-445e41701f737d73.txt
PARENT         data/samples/IT-SOURCE-SAMPLES/IT-T2-001/34_boll_agro_20260824.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 3393
LANGUAGE       it
REVIEWABLE     YES
```

**TITULO**

> Bollettino AgroMeteorologico Settimanale n. 34/2026 del 24 agosto 2026

**ABERTURA DO DOCUMENTO**

```text
Bollettino AgroMeteorologico Settimanale n. 34/2026 del 24 agosto 2026 17 agosto 2026 - 23 agosto 2026 Diario meteorologico: intense precipitazioni e temperature prossime alla media climatica. La settimana è stata caratterizzata da precipitazioni, anche molto intense, soprattutto nelle giornate di lunedì 17, giovedì 20 e venerdì 21. Il 17 agosto si sono verificate precipitazioni localizzate in Romagna e sui rilievi da Piacenza a Reggio Emilia, a carattere fortemente temporalesco e valori localmente superiori ai 50 mm. Giovedì 20 piogge diffuse hanno interessato tutta la regione, con massimi sull’Appennino occidentale, fino a oltre 100 mm, e intensità orarie particolarmente alte sul crinale parmense. Venerdì 21 si sono verificate precipitazioni che a più riprese hanno interessato tutta la regione, molto intense e abbondanti sul crinale centro-occidentale, con cumulate giornaliere che loca
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- NONE

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- NONE

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 45 / 46

```
ITEM_ID        RAW-fd5b5e465457e4d6.txt
SOURCE_ID      NAO SEI
PUBLISHER      FONDAZIONE EDMUND MACH
CONTENT_PATH   data/derivados/texto/RAW-fd5b5e465457e4d6.txt
PARENT         data/samples/IT-BOLLETTINI-VPN-2026/pdf/TN_DIB22_07ago2026.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 22161
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> FONDAZIONE EDMUND MACH CENTRO TRASFERIMENTO TECNOLOGICO

**ABERTURA DO DOCUMENTO**

```text
FONDAZIONE EDMUND MACH CENTRO TRASFERIMENTO TECNOLOGICO Bollettino N.22 del 07 agosto 2026 Pag. 1 di 10 BOLLETTINO DIFESA INTEGRATA DI BASE La stagione invernale a cavallo tra il 2025 e il 2026 è stata caratterizzata da un dicembre più asciutto e caldo rispetto alla media climatica, seguito da un gennaio in controtendenza, complessivamente fresco e decisamente piovoso, e da un febbraio eccezionalmente caldo (il secondo più caldo degli ultimi 20 anni, superato solo dal record del 2024). La piovosità dei primi mesi del 2026 è stata invece più alta della media climatica, con eventi di carattere nevoso che si sono registrati anche in alcuni fondovalle. Nel complesso, l’inverno appena trascorso è risultato più caldo della media climatica di quasi 1 °C. Le temperature del mese di marzo sono state superiori alla media, mentre la piovosità inferiore. Nell’ultima parte del mese e nei primi giorni
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…07 agosto 2026 Pag. 1 di 10 BOLLETTINO DIFESA INTEGRATA DI BASE La stagione invernale a cavallo tra il 2025 e il 20…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `FONDAZIONE EDMUND MACH CENTRO TRASFERIMENTO TECNOLOGICO`
- `BOLLETTINO DIFESA INTEGRATA DI BASE`
- `DICEMBRE`
- `GENNAIO`
- `FEBBRAIO`
- `MARZO`
- `APRILE`
- `MAGGIO`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## ITEM 46 / 46

```
ITEM_ID        RAW-9488589cfc657b95.txt
SOURCE_ID      NAO SEI
PUBLISHER      ARPAV
CONTENT_PATH   data/derivados/texto/RAW-9488589cfc657b95.txt
PARENT         data/samples/IT-ARPAV-VENETO/frutticolo_24_260826.pdf
DOCUMENT_TYPE  TEXTO-DERIVADO-DE-PDF   BYTES 3636
LANGUAGE       NAO SEI
REVIEWABLE     YES
```

**TITULO**

> Pag. 1 di 2

**ABERTURA DO DOCUMENTO**

```text
Pag. 1 di 2 SERVIZIO FITOSANITARIO REGIONE VENETO U.O. Fitosanitario BOLLETTINI FITOSANITARI DIFESA INTEGRATA COLTURE FRUTTICOLE Bollettino n. 24 del 26/08/2026 Per i prossimi giorni sono previste temperature in aumento e assenza di fenomeni temporaleschi. PESCO Fase fenologica: terminata la raccolta Batteriosi: programmare una profilassi attenta, da iniziare in settembre, basata su trattamenti quindicinali, con prodotti rameici a basso dosaggio. SUSINO Fase fenologica: inizio raccolta per le varietà europee come Stanley e Grossa di Felisio. Buona la produzione e la pezzatura in generale, meno la colorazione. Cocciniglia: presenza sporadica. In caso di necessità si potrebbe ancora intervenire, facendo molta attenzione al rispetto dei tempi di carenza, con pyriproxifen. MELO Fase fenologica: terminata la raccolta delle varietà del gruppo Gala GLS/BR: al momento i sintomi in campo sono mol
```

**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)

- «…Pag. 1 di 2 SERVIZIO FITOSANITARIO REGIONE VENETO U.O. Fitosanitario BOLLETTINI FITOSANITARI D…»
- «…2 SERVIZIO FITOSANITARIO REGIONE VENETO U.O. Fitosanitario BOLLETTINI FITOSANITARI DIFESA INTEGRATA COLTURE FRUTTICOLE…»
- «…. Fitosanitario BOLLETTINI FITOSANITARI DIFESA INTEGRATA COLTURE FRUTTICOLE Bollettino n. 24 del 26/08/2026 Per i pr…»

**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)

- `SERVIZIO FITOSANITARIO REGIONE VENETO`
- `BOLLETTINI FITOSANITARI DIFESA INTEGRATA`
- `COLTURE FRUTTICOLE`

**DECISAO HUMANA**

| | REVIEWER_A | REVIEWER_B |
|---|---|---|
| `T3_SIM` | [ ] | [ ] |
| `T3_NAO` | [ ] | [ ] |
| `T3_AMBIGUO` | [ ] | [ ] |
| `EVIDENCIA_INSUFICIENTE` | [ ] | [ ] |

```
MOTIVO_A          ______________________________________________
EVIDENCIA_USADA_A ______________________________________________

MOTIVO_B          ______________________________________________
EVIDENCIA_USADA_B ______________________________________________

AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN
FINAL_LABEL  ____________________  (UNRESOLVED se A != B)
```

---

## AUDIT_AFTER_REVIEW

> **NAO LEIA ANTES DE DECIDIR.** Esta seccao existe para comparar a
> decisao humana com o que a maquina e a ficha da fonte diziam — e essa
> comparacao so vale se a decisao humana nascer primeiro.

| ITEM_ID | casou a varredura | territorio da FICHA DA FONTE | decisao atual da porta para T3 |
|---|:--:|:--:|---|
| `RAW-b631f6eecfbc1db0.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-a927e846ba8e78b0.txt` | nao | T4 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-9a01cc17889e1f40.txt` | nao | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-699a073ace4361ea.txt` | nao | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-7a51732e87f0f319.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-e612807928b5ada9.txt` | nao | T3 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-924aabd94168c53a.txt` | nao | T5 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-4e12affad7fedd91.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-420e08ef15bec6e4.txt` | SIM | T3 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-5dcfb75ac38390c3.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-8c13500d43502e64.txt` | nao | T2 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-6d12bcb5fa2b0905.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-99cb44a67f6b4e9a.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-3d3c1bc0e96332e8.txt` | nao | T2 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-2a12cb316622a9a5.txt` | SIM | T5 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-ded546686d61dc91.txt` | nao | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-6377ac2f8419d905.txt` | nao | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-144fdb152b1a6ae4.txt` | nao | T2 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-c6377f6951bfeb2e.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-0be2d204c98ad1b1.txt` | nao | T2 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-fe3c922bfdfd7999.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-e6ec962a8a730ee4.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-ec3108a2ed424702.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-e5176df66216dfd0.txt` | nao | T3 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `PROD_FTS_6_20260907.csv` | nao | T4 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-823e18ebb232eb36.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-59da05274359eff6.txt` | nao | T3 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `monitoraggio.html` | SIM | T3 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-48e76a696be6831d.txt` | SIM | T3 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-ccd8ea9c8e9c4caf.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-3e941738599367d7.txt` | SIM | T3 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-024abdb692be926a.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `NHEOWL0530_00.html` | nao | T2 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-178ebe9e0ea7dd83.txt` | nao | T3 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-3ef48aaa830edf3b.txt` | nao | T3 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-f88c89d73d6a132a.txt` | nao | T2 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-0c2723e66201f966.txt` | SIM | T3 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-a6515948880d173a.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-392840d3e13d1b15.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-223510588786a4de.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-df4adcb5d78929e1.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-e9395a7ea894c1d2.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-221ab4a8d6ebec30.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-445e41701f737d73.txt` | nao | T2 | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-fd5b5e465457e4d6.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |
| `RAW-9488589cfc657b95.txt` | SIM | NAO SEI | NENHUMA — nao ha decisao de T3 no livro para este item |

Nenhuma destas tres colunas e verdade sobre o documento:

- a **varredura** e uma busca por seis frases;
- o **territorio da ficha** ja foi medido a discordar do documento tres
  vezes (ARPAV publica T2 e T3; `IT-T5-003` declara «Preco e mercado» e
  entrega «Bilancio Fitosanitario»; `IT-T7-002` declara «Ciencia» e
  entrega uma lista administrativa);
- a **decisao da porta** e a saida do mecanismo que se quer substituir.

```
ROTULO EXISTE            != ROTULO CONFIAVEL
KEYWORD_DERIVED          != GABARITO
SOURCE TERRITORY         != DOCUMENT UNIVERSE
```
