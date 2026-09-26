# SINAL-PRECOCE-SERIES · as séries de monitorização que JÁ estão no acervo (sem rede, sem resumir)

Ramo **`micro-prova-lote2b-v1`** (por cima de `365842a8`, que desce do vivo `278cd489`; o vivo agora é `dc0de726` — nada
do que aqui se lê mudou com isso: é só leitura do acervo). Feito a 26/09 depois das 17:35. Nada escrito no vivo, na Sala
ou no RAW.

## 0 · O que se leu (tudo o que há de boletim fitossanitário no acervo)

`curadoria/series_sinal_precoce.py` sobre `source-curator-service-v1/data/collection-store` (acervo do vivo, só leitura) e
`C:/Users/London1/sintonia-sala-italia` (as cópias). Um documento conta **uma vez por sha256** (o mesmo PDF em várias pastas).
Dos 53 PDFs distintos do acervo, **são boletim fitossanitário** (medido no texto, não pelo número da fonte): Salerno ×2,
ARIF ×2, APOL ×2, e a secção «Dai Servizi Fitosanitari» dos 8 boletins zonais ARPAV (2 números × 4 zonas). Mais os
**2 HTML** de monitorização da Terre dell'Etruria (o juiz de contagens passou pelas **566 páginas HTML** distintas do acervo:
só esta fonte tem contagem; o único outro «acerto», IT-T10-007 «2026 Uova», é preço de ovos). Os outros PDFs com palavras
parecidas (carta de serviços, tarifário, ISO, relatórios) não são boletim. **16 documentos, 250 linhas extraídas.**

Tudo em `curadoria/SINAL-PRECOCE-SERIES.json` (cada linha com o TRECHO de onde saiu e o sha256 do documento).
**Natureza** (OBSERVAÇÃO / PREVISÃO / RECOMENDAÇÃO) só quando o texto a diz: pelos rótulos do próprio boletim quando os há
(ARIF: «Situazione Fitosanitaria» / «Programma di Difesa»), senão pelos verbos («si riscontrano», «rilevate», «aumento del
numero» → observação; «si prevede», «favoriranno», «possono favorire», «potrebbe» → previsão; «si consiglia», «intervenire»,
«prestare attenzione», «proseguire il monitoraggio» → recomendação). Uma frase de **limiar** («al superamento della soglia…»)
**não** é observação, a não ser que diga que viu.

## 1 · Quantas séries reais

| Fonte | Séries (o mesmo local + organismo em ≥ 2 datas) | Com número nas 2 datas | Onde mudou |
|---|---|---|---|
| **IT-T3-005 Terre dell'Etruria** (Toscana) | **52** pontos | 52 (% infestação ativa) | **20** (ex.: Roccastrada-Montemassi 4% → 7% «Allerta»; Grosseto-poggio al vento 1% → 4%) |
| **IT-T3-002 Salerno** (Campania) | **14** | **11** (capturas) + 2 olivo (texto → «Media catture 3/7») + 1 cinipide (texto) | Ceratitis 4 → 40; Lobesia 3 → 5; Scafoide 3 → 4; Tuta (beringela) 6 → 9; Pammene 5 → 0; Cydia fagiglandana 2 → 0 |
| **IT-T3-010 APOL** (Puglia) | **3** comprensori | 3 (**métrica NAO SEI**: cabeçalho é imagem) | Salentina Nord 5 → 6; Salentina Sud 4 → 6 |
| IT-T3-008 ARIF (Puglia) | **0** numéricas | — | observação escrita; os 2 números têm 32/31 blocos → sem par |
| IT-T2-002 ARPAV (Veneto) | **0** | — | 1 só número com texto (N° 54); o N° 56 corta a secção |
| **Total** | **69** | **66 com número** (52 + 11 + 3) | |

⚠️ Todas as séries têm **2 pontos** (as duas datas que o acervo guardou). É o começo de uma série, não uma série longa.

## 2 · As séries, fonte a fonte (valores tal como vieram)

### 2.1 · IT-T3-002 — Campania, Bollettino fitosanitario Provincia di **Salerno** (N° 25 · 02/09/2026 → N° 27 · 16/09/2026)

Rede de monitorização por **azienda**; coluna «Stato fitosanitario» = **OBSERVAÇÃO** (o boletim diz: «sulla base dei risultati della rete di monitoraggio»). Transcrição à mão, **conferida pela máquina** em cada trecho (EXATO = igual no texto; EM_ORDEM = as palavras por esta ordem em ≤ 120 letras, porque o PDF intercala colunas).

| Cultura | Comune · Località · Azienda | Varietà | Fase | Organismo | 02/09/2026 | 16/09/2026 | Conferência |
|---|---|---|---|---|---|---|---|
| AGRUMI | Angri · Monte Longobardi · Taccaro Gennaro | varie | Accrescimento frutticini | Prays citri | 0 | 0 | EXATO/EXATO |
| AGRUMI | Angri · Monte Longobardi · Taccaro Gennaro | varie | Accrescimento frutticini | Ceratitis capitata | 4 | 40 | EXATO/EXATO |
| VITE | Tramonti · Capitignano · Apicella P. | Piedirosso | Maturazione | Lobesia botrana | 3 | 5 | EXATO/EXATO |
| VITE | Tramonti · Capitignano · Apicella P. | Piedirosso | Maturazione | Cryptoblabes gnidiella | 0 | 0 | EM_ORDEM/EXATO |
| VITE | Tramonti · Capitignano · Apicella P. | Piedirosso | Maturazione | Scaphoideus (Scafoide) | 3 | 4 | EXATO/EXATO |
| CASTAGNO | Tramonti · Frescale · Apicella Gaetano | diverse | Accrescimento riccio | Cydia fagiglandana (Cidia) | 2 | 0 | EXATO/EXATO |
| CASTAGNO | Tramonti · Frescale · Apicella Gaetano | diverse | Accrescimento riccio | Pammene fasciana (Pamena) | 5 | 0 | EXATO/EXATO |
| CASTAGNO | Tramonti · Frescale · Apicella Gaetano | diverse | Accrescimento riccio | Cinipide | Presenza | Presenza | EXATO/EXATO |
| NOCE | Sarno · Quattrofuni · Fasolino | Sorrento | Maturazione frutti | Cydia pomonella | 3 | 3 | EM_ORDEM/EM_ORDEM |
| OLIVO | Campagna / Agropoli (a linha nao se atribui: colunas misturadas no PDF) · — · Reppuccia G. / Cardone F. | Rotondella / Salella-Frantoio-Leccino | Accrescimento del frutto | mosca (linha 1) | Minime cattura di mosca | Media catture 3 / Infestazioni 0 | EM_ORDEM/EXATO |
| OLIVO | Campagna / Agropoli (a linha nao se atribui: colunas misturadas no PDF) · — · Reppuccia G. / Cardone F. | Rotondella / Salella-Frantoio-Leccino | Accrescimento del frutto | mosca (linha 2) | Nulla | Media catture 7 / Infestazioni 0 | EXATO/EXATO |
| POMODORO | Sarno · San Vito · Raimo Aniello | San Marzano | Prosegue la raccolta | Tuta absoluta | 5 | 5 | EM_ORDEM/EXATO |
| POMODORO | Sarno · San Vito · Raimo Aniello | San Marzano | Prosegue la raccolta | Helicoverpa armigera | 0 | 0 | EXATO/EXATO |
| MELANZANA | Capaccio · Paestum Scalo · Mucciolo L. | Diverse | Fase di maturazione commerciale | Tuta absoluta | 6 | 9 | EM_ORDEM/EXATO |
| MELANZANA | Capaccio · Paestum Scalo · Mucciolo L. | Diverse | Fase di maturazione commerciale | cicaline | Presenza | — | EXATO |

Outras culturas do mesmo boletim sem nada a assinalar (ACTINIDIA Eboli, CILIEGIO Nocera Inferiore, FRAGOLA Battipaglia, NOCCIOLO Giffoni Sei Casali, PESCO Eboli): «Nulla» / «Nulla da segnalare» nas duas datas. ⚠️ OLIVO: o PDF põe 2 linhas (Campagna; Agropoli) com as colunas misturadas — **a que localidade pertence cada valor = NAO SEI**; ficam pela ordem.

### 2.2 · IT-T3-010 — **APOL** Puglia, Bollettino Mosca delle Olive (semanal)

Uma linha por comprensorio = **OBSERVAÇÃO** («I monitoraggi territoriali settimanali indicano…»). ⚠️ O cabeçalho da tabela é **imagem**: o que medem as colunas 1–3 = **NAO SEI**.

| Comprensorio | Fase | n.9 · 07–13/09/2026 (col.1 · col.2 · col.3 · tendência · risco) | n.10 · 14–20/09/2026 |
|---|---|---|---|
| BR - COLLINA LITORANEA | INGROSSAMENTO FRUTTI | 7 · 1 · 5% · STAZIONARIO · BASSO | 7 · 1 · 5% · STAZIONARIO · BASSO |
| LE - PIANURA SALENTINA NORD | INGROSSAMENTO FRUTTI | 5 · 1 · 5% · STAZIONARIO · BASSO | 6 · 1 · 5% · STAZIONARIO · BASSO |
| LE - PIANURA SALENTINA SUD | INGROSSAMENTO FRUTTI | 4 · 1 · 5% · STAZIONARIO · BASSO | 6 · 1 · 5% · STAZIONARIO · BASSO |

No texto dos dois números (OBSERVAÇÃO): «non si sono rilevate raggiungimenti o superamenti della soglia di intervento con pochissime punture fertili e ancora un basso numero di individui riscontrati sulle trappole a feromoni installate»; n.9: «punte del 2,0% osservate in zone irrigue costiere di tutti comprensori e su varietà a drupa grossa». PREVISÃO (n.9): «Da metà della prossima settimana si verificherà un cambio meteo… favoriranno la ripresa della mosca dell'olivo». RECOMENDAÇÃO (n.9): «non si ritiene giustificata l'esecuzione di un trattamento fitosanitario».

### 2.3 · IT-T3-005 — **Terre dell'Etruria** (Toscana), mapa de monitorização da mosca da azeitona (HTML)

Por ponto: localidade, coordenadas, **data de campionamento**, «Infestazione attiva» (%) e estado = **OBSERVAÇÃO**. «Catture adulti: Dato per utenti registrati» em todos os pontos → **as capturas estão atrás de login (fora)**. 2 versões da página guardadas (69/69 pontos cada); série = o mesmo ponto em 2 datas de campionamento distintas.

| Ponto (comune, località) | Lat, Lon | 1.ª amostra | 2.ª amostra | Mudou? |
|---|---|---|---|---|
| ALBERESE, Alberese-cimitero | 42.6603, 11.0995 | 2026-09-04: 0% (Sotto trattamento) | 2026-09-07: 3% (Nessuna allerta) | **SIM** |
| Bibbona, Via Dierne | 43.2713, 10.5843 | 2026-09-01: 0% (Nessuna allerta) | 2026-09-07: 0% (Nessuna allerta) | não |
| Calci, Castelmaggiore | 43.733, 10.5142 | 2026-09-01: 1% (Nessuna allerta) | 2026-09-09: 2% (Nessuna allerta) | **SIM** |
| Campagnatico, Arcille - Sticcianese | 42.7941, 11.2761 | 2026-09-01: 0% (Nessuna allerta) | 2026-09-08: 0% (Nessuna allerta) | não |
| Campiglia Marittima, Loc. Cafaggio | 43.0408, 10.6388 | 2026-07-09: 0% (Nessuna allerta) | 2026-08-31: 0% (Nessuna allerta) | não |
| Campiglia Marittima, Palmentello | 43.064, 10.5696 | 2026-09-03: 1% (Nessuna allerta) | 2026-09-09: 1% (Nessuna allerta) | não |
| Capraia e Limite, Casalone | 43.7723, 10.9908 | 2026-08-31: 0% (Nessuna allerta) | 2026-09-07: 0% (Nessuna allerta) | não |
| Carmignano, Verghereto | 43.8021, 11.0065 | 2026-09-01: 0% (Nessuna allerta) | 2026-09-07: 0% (Nessuna allerta) | não |
| Castagneto Carducci , via Bolgherese Az. Di Vaira Dario | 43.2013, 10.6078 | 2026-09-02: 0% (Nessuna allerta) | 2026-09-09: 0% (Nessuna allerta) | não |
| Castagneto LOC. VALLONE, LOC. VALLONE | 43.1767, 10.6159 | 2026-09-03: 1% (Nessuna allerta) | 2026-09-09: 0% (Nessuna allerta) | **SIM** |
| Cecina, Lupina | 43.304, 10.5544 | 2026-09-01: 3% (Nessuna allerta) | 2026-09-07: 2% (Nessuna allerta) | **SIM** |
| Donoratico loc. Cerreta Az.Sarri, Loc. Cerreta | 43.1553, 10.5887 | 2026-09-02: 0% (Nessuna allerta) | 2026-09-09: 0% (Nessuna allerta) | não |
| Donoratico, Campastrello- Casone Ugolino | 43.1662, 10.5827 | 2026-09-03: 4% (Pre allerta) | 2026-09-09: 5% (Pre allerta) | **SIM** |
| Donoratico, PIANETTI | 43.1523, 10.5556 | 2026-09-03: 2% (Nessuna allerta) | 2026-09-09: 2% (Nessuna allerta) | não |
| Empoli, Tartagliana | 43.6911, 10.9738 | 2026-08-31: 0% (Nessuna allerta) | 2026-09-07: 0% (Nessuna allerta) | não |
| Fattoria San Vito, Calci | 43.721, 10.5151 | 2026-09-01: 2% (Nessuna allerta) | 2026-09-09: 2% (Nessuna allerta) | não |
| Grosseto, Braccagni | 42.9122, 11.0777 | 2026-09-01: 0% (Nessuna allerta) | 2026-09-08: 0% (Nessuna allerta) | não |
| Grosseto, poggio al vento | 42.768, 11.181 | 2026-08-31: 1% (Nessuna allerta) | 2026-09-07: 4% (Pre allerta) | **SIM** |
| Grosseto-Istia, draga | 42.7969, 11.2054 | 2026-08-31: 7% (Allerta) | 2026-09-08: 7% (Allerta) | não |
| La California, Calcinaiola | 43.2578, 10.5726 | 2026-08-31: 0% (Nessuna allerta) | 2026-09-07: 0% (Nessuna allerta) | não |
| Lamporecchio, Orbignano | 43.8086, 10.9109 | 2026-09-01: 0% (Nessuna allerta) | 2026-09-08: 0% (Nessuna allerta) | não |
| Larciano , La Maschera | 43.8459, 10.8922 | 2026-09-01: 0% (Nessuna allerta) | 2026-09-07: 0% (Nessuna allerta) | não |
| Lustignano | 43.1741, 10.7986 | 2026-09-02: 0% (Nessuna allerta) | 2026-09-09: 2% (Nessuna allerta) | **SIM** |
| MASSA MARITTIMA VALPIANA FRASCHIERA | 43.0193, 10.835 | 2026-09-04: 1% (Nessuna allerta) | 2026-09-11: 0% (Nessuna allerta) | **SIM** |
| Magliano in Toscana, Sterpeti | 42.6017, 11.2805 | 2026-08-31: 0% (Nessuna allerta) | 2026-09-08: 1% (Nessuna allerta) | **SIM** |
| Manciano, Farniatella-Sgrillozzo | 42.537, 11.4462 | 2026-09-04: 0% (Sotto trattamento) | 2026-09-07: 3% (Nessuna allerta) | **SIM** |
| Massa Marittima, cura nuova 1 | 42.9689, 10.8215 | 2026-09-04: 0% (Nessuna allerta) | 2026-09-11: 1% (Nessuna allerta) | **SIM** |
| Montepulciano, Caggiole | 43.1149, 11.7987 | 2026-09-03: 0% (Nessuna allerta) | 2026-09-11: 0% (Nessuna allerta) | não |
| Montepulciano, Cervognano 2 | 43.0915, 11.8076 | 2026-09-03: 0% (Nessuna allerta) | 2026-09-11: 0% (Nessuna allerta) | não |
| Montepulciano, Sarteano | 43.011, 11.8463 | 2026-09-03: 0% (Nessuna allerta) | 2026-09-11: 0% (Nessuna allerta) | não |
| Montepulciano, Torrita di Siena | 43.1685, 11.7636 | 2026-09-03: 0% (Nessuna allerta) | 2026-09-11: 0% (Nessuna allerta) | não |
| Montiano, Cupi | 42.6623, 11.177 | 2026-09-04: 0% (Sotto trattamento) | 2026-09-08: 2% (Nessuna allerta) | **SIM** |
| Piombino, Asca | 42.956, 10.5238 | 2026-08-31: 6% (Allerta) | 2026-09-07: 0% (Sotto trattamento) | **SIM** |
| Pomarance, Fattoria Bulera | 43.2716, 10.9009 | 2026-09-02: 2% (Nessuna allerta) | 2026-09-09: 2% (Nessuna allerta) | não |
| Rigoli, Mucchieto | 43.7851, 10.4262 | 2026-08-31: 5% (Pre allerta) | 2026-09-09: 5% (Pre allerta) | não |
| Riparbella, Sorbugnano | 43.3572, 10.582 | 2026-09-02: 1% (Nessuna allerta) | 2026-09-09: 0% (Nessuna allerta) | **SIM** |
| Roccastrada, Montemassi | 42.9904, 11.0917 | 2026-08-31: 4% (Pre allerta) | 2026-09-08: 7% (Allerta) | **SIM** |
| San Miniato, Moriolo | 43.6535, 10.8358 | 2026-09-01: 0% (Nessuna allerta) | 2026-09-07: 0% (Nessuna allerta) | não |
| San Vincenzo, Via del Castelluccio - S. Carlo | 43.1012, 10.5736 | 2026-08-31: 4% (Nessuna allerta) | 2026-09-07: 4% (Pre allerta) | não |
| San Vincenzo, Via della Caduta | 43.0556, 10.5569 | 2026-08-31: 1% (Nessuna allerta) | 2026-09-07: 0% (Nessuna allerta) | **SIM** |
| San Vincenzo, via di San Bartolo | 43.0942, 10.5786 | 2026-08-31: 2% (Nessuna allerta) | 2026-09-07: 3% (Nessuna allerta) | **SIM** |
| Santa Luce, Santa Luce | 43.4675, 10.5573 | 2026-09-01: 0% (Sotto trattamento) | 2026-09-08: 0% (Dato non rilevato) | não |
| Scarlino, LE CASE | 42.9295, 10.8528 | 2026-09-04: 0% (Nessuna allerta) | 2026-09-11: 0% (Nessuna allerta) | não |
| Scarlino, Puntone | 42.8938, 10.8026 | 2026-09-04: 3% (Nessuna allerta) | 2026-09-11: 3% (Nessuna allerta) | não |
| Sdriscia, SDRISCIA | 42.9827, 10.5879 | 2026-08-31: 2% (Pre allerta) | 2026-09-07: 0% (Nessuna allerta) | **SIM** |
| Strada Bolgherese, Bibbona | 43.2623, 10.5992 | 2026-09-01: 0% (Nessuna allerta) | 2026-09-07: 0% (Nessuna allerta) | não |
| Suvereto, Forni | 43.0532, 10.7034 | 2026-08-31: 0% (Nessuna allerta) | 2026-09-07: 0% (Nessuna allerta) | não |
| Vada, Cason Vecchio | 43.3648, 10.471 | 2026-09-01: 0% (Nessuna allerta) | 2026-09-08: 0% (Nessuna allerta) | não |
| Vicopisano, Frantoio | 43.7053, 10.5838 | 2026-09-01: 4% (Nessuna allerta) | 2026-09-09: 1% (Nessuna allerta) | **SIM** |
| Vignale, Mortelliccio | 42.9562, 10.6809 | 2026-08-31: 6% (Allerta) | 2026-09-07: 0% (Sotto trattamento) | **SIM** |
| Vinci, Marcello | 43.7764, 10.9415 | 2026-09-02: 0% (Nessuna allerta) | 2026-09-09: 0% (Nessuna allerta) | não |
| Vinci-Vitolini, Marcignana | 43.7826, 10.9599 | 2026-09-01: 0% (Nessuna allerta) | 2026-09-07: 0% (Nessuna allerta) | não |

**52 pontos com série; em 20 o valor mudou.** Pontos com «Data di campionamento: -» ficam fora.

### 2.4 · IT-T3-008 — **ARIF** Puglia, Notiziario Agrometeorologico & Fitosanitario (N36 · 02/09 e N38 · 16/09/2026)

Blocos com rótulos do próprio boletim: «Situazione Fenologica» (fase) · «Situazione Fitosanitaria» (= **OBSERVAÇÃO**) · «Programma di Difesa» (= **RECOMENDAÇÃO**, com os limiares). Os títulos de cultura/área são imagem → **CULTURA/ÁREA = NAO SEI**. **Sem par entre números:** o N36 tem 32 blocos e o N38 31 (um bloco a mais desloca tudo a partir do 21 — medido); parear por posição poria culturas diferentes lado a lado. Sem números de captura: a observação é escrita.

**N36 · 2026-09-02** (32 blocos)

| Bloco | Fase | Situazione Fitosanitaria (OBSERVAÇÃO, tal como está) | Limiares escritos no Programma di Difesa |
|---|---|---|---|
| 00 | Accrescimento frutti. | Presenza di malattie fungine e rogna - oziorrinco (Otiorhynchus cribricollis). Sporadiche catture di mosca dell'olivo (Bactrocera oleae) nelle trappole a feromoni. | Proseguire il monitoraggio tramite le trappole a feromoni e campionamenti delle olive e nel caso di superamento della soglia di infestazione, 4-5% per le olive da olio e le prime punture per le olive da tavola, si può intervenire con un trattamento insetticida. · - curativi (nei confronti delle larve), al raggiungimento della soglia, intervenire nelle prime fasi di sviluppo della mosca (uova e larva di prima età) utilizzando acetamiprid o ﬂupyradifurone. |
| 01 | Maturazione. | Presenza localizzata di peronospora (Plasmopara viticola) e oidio (Uncinula necator) . | — |
| 02 | Maturazione. | Presenza localizzata di peronospora (Plasmopara viticola) - oidio (Uncinola necator) e mosca della frutta (Ceratitis capitata). | — |
| 03 | Estivazione. | Esiti di attacchi parassitari pregressi. | — |
| 04 | Estivazione. | Esiti di attacchi parassitari pregressi. | — |
| 05 | Nulla da segnalare. | Nulla da segnalare. | — |
| 06 | Trapianto. | Nulla da segnalare. | — |
| 07 | Maturazione. | Esiti di attacchi parassitari pregressi. | — |
| 08 | Accrescimento frutto. | Presenza di mosca dell'olivo e margaronia. | E' utile collocare in campo le trappole per il monitoraggio della mosca dell'olivo e nel caso di superamento della soglia, 4-5% per le olive da olio e le prime punture per le olive da tavola, si può ricorrere ad un intervento insetticida. · - curativi (nei confronti delle larve), al raggiungimento della soglia, intervenire nei confronti delle prime fasi di sviluppo della mosca (uova e larva di prima età) utilizzando acetamiprid o ﬂupyradifurone. |
| 09 | Maturazione. | Catture di anarsia nelle trappole a feromoni. | Contro la cidia al superamento della soglia di intervento, che è di 10 catture per trappola a settimana, e contro l'anarsia, la cui soglia di intervento è di 7 catture per trappola a settimana o di 10 catture per trappola in due settimane, eﬀettuare un intervento con le sostanze attive: Bacillus thuringiensis, spinosad, emamectina, clorantraniliprole, acetamiprid. |
| 10 | Maturazione. | Catture di tignoletta nelle trappole a feromoni. Presenza di mal dell'esca. | — |
| 11 | Invaiatura. | Catture di tignoletta nelle trappole a feromoni. Presenza di mal dell'esca. | — |
| 12 | Nuovi impianti - sviluppo vegetativo. | Nulla da segnalare. | — |
| 13 | Trapianto - sviluppo vegetativo. | Presenza di aﬁdi. | — |
| 14 | Maturazione (raccolta). | Catture di Tuta absoluta nelle trappole a feromoni e danni su foglie e frutto. Presenza di ragnetto rosso. Danni da nottue sulle bacche. Marciume apicale. | — |
| 15 | Sviluppo dei frutti. | Fumaggine. Presenza di aleurodide spinoso (Aleurocanthus spiniferus). Catture di mosca mediterranea della frutta (Ceratitis capitata). Riscontrata nelle trappole a feromone la cocciniglia rossa forte degli agrumi (Aonidiella aurantii). | Per il controllo della cocciniglia rossa forte degli agrumi (Aonidiella aurantii), si consiglia di intervenire al superamento della soglia di intervento del 10% di frutti infestati, utilizzando prodotti a base di olio minerale, olio essenziale di arancio dolce e sali potassici di acidi grassi (sostanze ammesse anche in agricoltura biologica), acetamiprid, pyriproxyfen e altri prodotti autorizzati. |
| 16 | Ingrossamento frutto - invaiatura. | Presenza di rogna. Presenze di punture di ovodeposizione da parte della mosca dell'olivo (Bactrocera oleae). | Nella zona costiera del Gargano si ravvisano catture di adulti nelle trappole a feromone, con contestuale punture di ovodeposizione nelle olive anche se la stessa si attesta dal 2% al 7%. · Date le condizioni meteo, con temperature elevate, si consiglia di tenere sotto controllo la popolazione sia dal punto di vista del numero di catture nelle trappole sia delle punture di ovodeposizione ricordando di intervenire al raggiungimento della soglia del 4-5% di infestazione attiva (sommatoria di uova e larve di prima età). · - curativi (nei confronti delle larve), al raggiungimento della soglia, intervenire nei confronti delle prime fasi di sviluppo della mosca (uova e larva di prima età) utilizzando acetamiprid o ﬂupyradifurone. |
| 17 | Maturazione. | Esiti di infezioni pregresse blande di peronospora e oidio. | — |
| 18 | Accrescimento frutti. Inizio invaiatura impianti in soﬀerenza da stress idrico. | Poche catture, punture fertili di mosca (Bactrocera oleae) ma solo in alcuni contesti ad alta suscettibilità, su cv sensibili, in irriguo e generalmente al disotto delle soglie di intervento. Cascola a causa della Lasioptera berlesiana, predatore delle mosca che, vivendo in simbiosi con un fungo (Camarosporium dalmaticum), infetta le drupe facendole cadere. Purtroppo questo antagonista della mosca, pur nel nobile intento di eliminare le uova, determina un vero e proprio danno. La cascola, comunque, è limitata alle poche situazioni di infestazioni con punture fertili o di solo assaggio. Lo stress idrico e le alte temperature registrate nelle ultime settimane rappresentano comunque condizioni di ostacolo allo sviluppo delle infestazioni. Presenza di rosure di margaronia (Palpita unionalis) soprattutto su piante giovani o piante potate. | Limitare il trattamento chimico ai casi in cui, nonostante ciò, le infestazioni iniziano ad avvicinarsi alle soglie di intervento (4-5% di punture fertili per le olive olio e la sola presenza delle prime punture invece per olive da tavola). |
| 19 | Invaiatura-maturazione cv tardive. | Tignole: Cidia molesta e Anarsia lineatella. Mal bianco (Sphaerotheca pannosa). | — |
| 20 | Maturazione. Per alcune varietà è iniziata la raccolta. | Esiti di infezioni pregresse di peronospora e oidio. Si osservano variazioni cromatiche delle foglie dovute alla presenza di cicalina africana (Jacobisca lybica) ma in minor misura rispetto allo stesso periodo dello scorso anno. In alcuni appezzamenti si notano delle mortiﬁcazioni della vegetazione, ed in alcuni casi anche delle vere e proprie ﬁlloptosi delle foglie. Il fenomeno è stato osservato da alcune settimane e si sta procedendo ad ulteriori approfondimenti diagnostici per accertarne l'agente causale. | — |
| 21 | Trapianto. | Nulla de segnalare. | — |
| 22 | Maturazione- raccolta. | Catture di tignola (Tuta absoluta) e di nottue (Helicoverpa armigera): presenza generalizzata di virosi su cv a bacca lunga. | — |
| 23 | Sviluppo dei frutti. | Riscontrata nelle trappole a feromoni la presenza di cotonello (Planococcus citri), cocciniglia rossa forte degli agrumi (Aonidiella aurantii) e sporadiche catture di mosca mediterranea della frutta (Ceratitis capitata). Sporadica presenza di ragnetto rosso (Tetranychus urticae - Panonychus citri) e minatrice serpentina (Phyllocnistis citrella). | Contro il cotonello (Planococcus citri) intervenire chimicamente solo al raggiungimento della soglia di intervento del 5% di frutti infestati, utilizzando prodotti a base di olio minerale bianco, acetamiprid o altri prodotti autorizzati. · Per il controllo della cocciniglia rossa forte degli agrumi (Aonidiella aurantii), si consiglia di intervenire al superamento della soglia di intervento del 20% di frutti infestati, utilizzando prodotti a base di olio minerale, olio essenziale di arancio dolce e sali potassici di acidi grassi (sostanze ammesse anche in agricoltura biologica), acetamiprid, pyriproxyfen e altri prodotti autorizzati. · In presenza di ragnetto rosso, intervenire: - per Tetranychus urticae, al superamento della soglia del 10% di foglie infestate da forme mobili e del 2% di frutti infestati; · - per Panonychus citri, al superamento del 30% di foglie infestate oppure in presenza di 3 acari per foglia. |
| 24 | Ingrossamento drupe. | Nelle trappole di monitoraggio sono state rilevate sporadiche catture di adulti di mosca (Bactrocera oleae). Presenza di occhio di pavone (Spilocaea oleaginea) e cercosporiosi (Cercospora cladosporioides) e margaronia (Palpita unionalis). | Nei casi di accertata presenza dell'infestazione attiva dell'insetto, si consiglia di intervenire con prodotti a base di acetamiprid o ﬂupyradifurone (utilizzabile una sola volta durante l'anno sulla coltura), attenendosi al raggiungimento della soglia d'intervento: - per le olive da mensa, corrisponde alla comparsa delle prime punture; · - per le olive da olio risulta pari al 4-5% di infestazione attiva (sommatoria di uova e larve). |
| 25 | Maturazione. | Presenza di vecchie infezioni di peronospora (Plasmopara viticola) e oidio (Uncinola necator). Si riscontrano nelle trappole catture di tignola rigata (Cryptoblabes gnidiella) e isolate catture di tignoletta dell'uva (Lobesia botrana). Riscontrata la presenza di cicaline. La sintomatologia prodotta dalle infestazioni di Jacobiasca lybica, in particolare, si distingue per la comparsa sulle foglie di ingiallimenti e necrosi del margine nei vigneti a bacca bianca, invece dall'arrossamento che porta al conseguente disseccamento e la caduta delle foglie nei vigneti a bacca nera. | — |
| 26 | Crescita dei frutti. | Riscontrata nelle trappole la presenza di mosca mediterranea della frutta (Ceratitis capitata). | — |
| 27 | Sviluppo frutti. | Mosca mediterranea della frutta (Ceratitis capitata); cocciniglia rossa forte degli agrumi (Aonidiella aurantii); cotonello (Planococcus citri); minatrice serpentina (Phyllocnistis citrella); ragnetti rossi (Panonychus citri, Tetranychus urticae); Formiche (Linepithema humile, Camponotus nylanderi, Tapinoma erraticum). | Al superamento della soglia del 5% di frutti infestati, intervenire con prodotti a base olio minerale estivo + azadiractina. · Si consiglia di osservare il proprio campo per individuare i primi attacchi e, al superamento della soglia del 10% di foglie infestate, programmare un intervento scegliendo tra i diversi acaricidi disponibili (fenpyroximate, pyridaben, extiazox, tebufenpirad, milbemectina, cyﬂumetofen, acequinocil). |
| 28 | Accrescimento frutti. | Mosca dell'olivo (Bactrocera oleae); margaronia (Palpita unionalis); oziorrinco (Otiorrhynchus cribricollis). | — |
| 29 | Maturazione. | Tignoletta della vite (Lobesia botrana); tignola rigata (Cryptoblabes gnidiella); cocciniglia farinosa (Planococcus ﬁcus); cicalina africana (Jacobiasca lybica); mal dell'esca (Phaeomoniella chlamydospora, Formitiponia mediterranea, Phaeoacremonium aleophilum). | — |
| 30 | Maturazione. | Tignoletta della vite (Lobesia botrana) ; tignola rigata (Cryptoblabes gnidiella); cocciniglia farinosa (Planococcus ﬁcus); cicalina africana (Jacobiasca lybica); mal dell'esca (Phaeomoniella chlamydospora, Formitiponia mediterranea, Phaeoacremonium aleophilum). | — |
| 31 | Maturazione. | Nulla da segnalare. | — |

**N38 · 2026-09-16** (31 blocos)

| Bloco | Fase | Situazione Fitosanitaria (OBSERVAÇÃO, tal como está) | Limiares escritos no Programma di Difesa |
|---|---|---|---|
| 00 | Accrescimento frutti - invaiatura. | Presenza di malattie fungine e rogna - oziorrinco (Otiorhynchus cribricollis). Sporadiche catture di mosca dell'olivo (Bactrocera oleae) nelle trappole a feromoni. | Proseguire il monitoraggio tramite le trappole a feromoni e campionamenti delle olive e nel caso di superamento della soglia di infestazione, 4-5% per le olive da olio e le prime punture per le olive da tavola, si può intervenire con un trattamento insetticida. · - curativi (nei confronti delle larve), al raggiungimento della soglia, intervenire nelle prime fasi di sviluppo della mosca (uova e larva di prima età) utilizzando acetamiprid o ﬂupyradifurone. |
| 01 | Maturazione. | Sono iniziate le operazioni di vendemmia. Presenza localizzata di peronospora (Plasmopara viticola) e oidio (Uncinula necator) . | — |
| 02 | Maturazione. | Presenza localizzata di peronospora (Plasmopara viticola) - oidio (Uncinola necator) e mosca della frutta (Ceratitis capitata). | — |
| 03 | Estivazione. | Esiti di attacchi parassitari pregressi. | — |
| 04 | Estivazione. | Esiti di attacchi parassitari pregressi. | — |
| 05 | Nulla da segnalare. | Nulla da segnalare. | — |
| 06 | Trapianto. | Nulla da segnalare. | — |
| 07 | Maturazione. | Esiti di attacchi parassitari pregressi. | — |
| 08 | Accrescimento frutto. | Presenza di mosca dell'olivo. | E' utile collocare in campo le trappole per il monitoraggio della mosca dell'olivo e nel caso di superamento della soglia, 4-5% per le olive da olio e le prime punture per le olive da tavola, si può ricorrere ad un intervento insetticida. · - curativi (nei confronti delle larve), al raggiungimento della soglia, intervenire nei confronti delle prime fasi di sviluppo della mosca (uova e larva di prima età) utilizzando acetamiprid o ﬂupyradifurone. |
| 09 | Maturazione (raccolta). | Catture di anarsia nelle trappole a feromoni. | — |
| 10 | Maturazione (raccolta). | Catture di tignoletta nelle trappole a feromoni. Presenza di mal dell'esca. | — |
| 11 | Maturazione. | Catture di tignoletta nelle trappole a feromoni. Presenza di mal dell'esca. | — |
| 12 | Nuovi impianti - sviluppo vegetativo. | Nulla da segnalare. | — |
| 13 | Trapianto - sviluppo vegetativo. | Presenza di aﬁdi. | — |
| 14 | Maturazione (raccolta). | Catture di Tuta absoluta nelle trappole a feromoni e danni su foglie e frutto. Presenza di ragnetto rosso. Danni da nottue sulle bacche. Marciume apicale. | — |
| 15 | Sviluppo dei frutti. | Fumaggine. Presenza di aleurodide spinoso (Aleurocanthus spiniferus). Catture di mosca mediterranea della frutta (Ceratitis capitata). Riscontrata nelle trappole a feromone la cocciniglia rossa forte degli agrumi (Aonidiella aurantii). | Per il controllo della cocciniglia rossa forte degli agrumi (Aonidiella aurantii), si consiglia di intervenire al superamento della soglia di intervento del 10% di frutti infestati, utilizzando prodotti a base di olio minerale, olio essenziale di arancio dolce e sali potassici di acidi grassi (sostanze ammesse anche in agricoltura biologica), acetamiprid, pyriproxyfen e altri prodotti autorizzati. |
| 16 | Invaiatura. | Presenza di rogna. Aumento del numero di punture di ovodeposizione da parte della mosca dell'olivo (Bactrocera oleae). Cascola di olive dovute ai fori di sfarfallamento della tignola delle olive (Prays Oleae). | Date le condizioni meteo, con temperature in diminuzione, si consiglia di tenere sotto controllo la popolazione sia dal punto di vista del numero di catture nelle trappole sia delle punture di ovodeposizione ricordando di intervenire al raggiungimento della soglia del 4-5% di infestazione attiva (sommatoria di uova e larve di prima età). · - curativi (nei confronti delle larve), al raggiungimento della soglia, intervenire nei confronti delle prime fasi di sviluppo della mosca (uova e larva di prima età) utilizzando acetamiprid o ﬂupyradifurone. |
| 17 | Maturazione. | Esiti di infezioni pregresse blande di peronospora e oidio. | — |
| 18 | Accrescimento frutti. Inizio invaiatura impianti in soﬀerenza da stress idrico. | Molti oliveti in asciutto sono fortemente stressati dalla perdurante siccità. Pertanto, ancora si registrano poche catture di mosca (Bactrocera oleae), salvo casi isolati in contesti ad alta suscettibilità, su cv sensibili, in irriguo e comunque al disotto delle soglie di intervento. Attenzione, la situazione potrebbe rapidamente cambiare nel caso in cui dovessero arrivare piogge e abbassamenti termici creando condizioni favorevoli allo sviluppo di nuove generazioni. Cascola a causa della Lasioptera berlesiana, predatore delle mosca che, vivendo in simbiosi con un fungo (Camarosporium dalmaticum), infetta le drupe facendole cadere. Purtroppo questo antagonista della mosca, pur nel nobile intento di eliminare le uova, determina un vero e proprio danno. La cascola, comunque, è limitata alle poche situazioni di infestazioni con punture fertili o di solo assaggio. Lo stress idrico e le alte temperature registrate nelle ultime settimane rappresentano comunque condizioni di ostacolo allo sviluppo delle infestazioni. Presenza di rosure di margaronia (Palpita unionalis) soprattutto su piante giovani o piante potate. | Limitare il trattamento chimico ai casi in cui, nonostante ciò, le infestazioni iniziano ad avvicinarsi alle soglie di intervento (4-5% di punture fertili per le olive olio e la sola presenza delle prime punture invece per olive da tavola). |
| 19 | Invaiatura-maturazione cv tardive. | Tignole: Cidia molesta e Anarsia lineatella. Mal bianco (Sphaerotheca pannosa). | — |
| 20 | Maturazione. | Sono iniziate in molte aziende le operazioni di vendemmia. Si registrano esiti di infezioni pregresse di peronospora e oidio e variazioni cromatiche delle foglie dovute alla presenza di cicalina africana (Jacobisca lybica), in minor misura rispetto allo stesso periodo dello scorso anno ma visibili a bordo campo di molte spalliere. In alcuni appezzamenti si notano delle "soﬀerenze" della vegetazione, ed in alcuni casi anche delle vere e proprie ﬁlloptosi delle foglie. Il fenomeno è stato osservato da alcune settimane e si sta procedendo ad ulteriori approfondimenti diagnostici per accertarne l'agente causale. | — |
| 21 | Trapianto, risveglio di carciofaie di secondo anno. | Isolate colonie di aﬁdi . | — |
| 22 | Sviluppo dei frutti. | Presenza di cotonello (Planococcus citri), cocciniglia rossa forte degli agrumi (Aonidiella aurantii). Riscontrate nelle trappole catture di mosca mediterranea della frutta (Ceratitis capitata). Sporadica presenza di ragnetto rosso (Tetranychus urticae - Panonychus citri) e minatrice serpentina (Phyllocnistis citrella). | Contro il cotonello (Planococcus citri) intervenire chimicamente solo al raggiungimento della soglia di intervento del 5% di frutti infestati, utilizzando prodotti a base di olio minerale bianco, acetamiprid o altri prodotti autorizzati. · Per il controllo della cocciniglia rossa forte degli agrumi (Aonidiella aurantii), si consiglia di intervenire al superamento della soglia di intervento del 20% di frutti infestati, utilizzando prodotti a base di olio minerale, olio essenziale di arancio dolce e sali potassici di acidi grassi (sostanze ammesse anche in agricoltura biologica), acetamiprid, pyriproxyfen e altri prodotti autorizzati. · In presenza di ragnetto rosso, intervenire: - per Tetranychus urticae, al superamento della soglia del 10% di foglie infestate da forme mobili e del 2% di frutti infestati; · - per Panonychus citri, al superamento del 30% di foglie infestate oppure in presenza di 3 acari per foglia. |
| 23 | Invaiatura. | Nelle trappole di monitoraggio sono state rilevate sporadiche catture di adulti di mosca (Bactrocera oleae). Presenza di occhio di pavone (Spilocaea oleaginea) e cercosporiosi (Cercospora cladosporioides) e margaronia (Palpita unionalis). | Nei casi di accertata presenza dell'infestazione attiva della mosca (Bactrocera oleae), si consiglia di intervenire con prodotti a base di acetamiprid o ﬂupyradifurone (utilizzabile una sola volta durante l'anno sulla coltura), attenendosi al raggiungimento della soglia d'intervento: - per le olive da mensa, corrisponde alla comparsa delle prime punture; · - per le olive da olio risulta pari al 4-5% di infestazione attiva (sommatoria di uova e larve). |
| 24 | Maturazione. | Presenza di vecchie infezioni di peronospora (Plasmopara viticola) e oidio (Uncinola necator). Si riscontrano nelle trappole catture di tignola rigata (Cryptoblabes gnidiella). Riscontrata la presenza di cicaline. La sintomatologia prodotta dalle infestazioni di Jacobiasca lybica, in particolare, si distingue per la comparsa sulle foglie di ingiallimenti e necrosi del margine nei vigneti a bacca bianca, invece dall'arrossamento che porta al conseguente disseccamento e la caduta delle foglie nei vigneti a bacca nera. | — |
| 25 | Inizio maturazione. | Riscontrata nelle trappole la presenza di mosca mediterranea della frutta (Ceratitis capitata). | — |
| 26 | Sviluppo frutti - invaiatura varietà precoci. | Mosca mediterranea della frutta (Ceratitis capitata); cocciniglia rossa forte degli agrumi (Aonidiella aurantii); aleurodide spinoso (Aleurochantus spiniferus); cotonello (Planococcus citri); minatrice serpentina (Phyllocnistis citrella); ragnetti rossi (Panonychus citri, Tetranychus urticae). | Al superamento della soglia del 5% di frutti infestati, intervenire con prodotti a base olio minerale estivo + azadiractina. · Si consiglia di osservare il proprio campo per individuare i primi attacchi e, al superamento della soglia del 10% di foglie infestate, programmare un intervento scegliendo tra i diversi acaricidi disponibili (fenpyroximate, pyridaben, extiazox, tebufenpirad, milbemectina, cyﬂumetofen, acequinocil). |
| 27 | Accrescimento frutti - invaiatura. | Mosca dell'olivo (Bactrocera oleae); oziorrinco (Otiorrhynchus cribricollis). | — |
| 28 | Maturazione. | Mal dell'esca (Phaeomoniella chlamydospora, Formitiponia mediterranea, Phaeoacremonium aleophilum). | — |
| 29 | Maturazione. | Tignoletta della vite (Lobesia botrana); tignola rigata (Cryptoblabes gnidiella); cocciniglia farinosa (Planococcus ﬁcus); cicalina africana (Jacobiasca lybica); muﬀa grigia (Botrytis cinerea); mal dell'esca (Phaeomoniella chlamydospora, Formitiponia mediterranea, Phaeoacremonium aleophilum). | — |
| 30 | Maturazione. | Nulla da segnalare. | — |

### 2.5 · IT-T2-002 — **ARPAV** Agrometeo Informa (Veneto), secção «Dai Servizi Fitosanitari»

4 boletins zonais por número (Zona 1 Vittorio Veneto-Conegliano, 9 Medio Polesine, 16 Val d'Illasi Alpone, 24 Alto Polesine), **o mesmo texto fitossanitário nas 4 zonas** (texto regional, não por zona). N° 54 (02–03/09/2026) com frases de organismo; N° 56 (16–17/09/2026): o próprio PDF corta a secção («Prime analisi su campioni di olive pervenuti:» e acaba) → **NAO SEI**. Sem números de captura. Frases do N° 54 com a natureza que o texto diz:

- **OBSERVACAO** — Bactrocera: «Mosca delle olive (Bactrocera oleae): il monitoraggio della settimana evidenzia una pressione stabile.»
- **OBSERVACAO** — Halyomorpha: «Cimici: presenza di cimice as. (Halyomorpha halys) e di cimice verde (Nezara viridula), a vari stadi di sviluppo, al momento i livelli di popolazione non giustificano azioni a contrasto.»
- **OBSERVACAO** — Margaronia: «Margaronia (Palpita unionalis): si osservano danni agli apici vegetativi su più oliveti, al mantengono sono sotto delle soglie d’intervento, le eventuali azioni a contrato della mosca ne contengono indirettamente la popolazione.»
- **OBSERVACAO/PREVISAO** — Spilocaea oleaginea: «Parassiti fungini Le precipitazioni della settimana scorsa e l’aumento dell’umidità relativa possono favorire Occhio di pavone (Spilocaea oleaginea), Piombatura dell’olivo (Mycocentrospora cladosporoides), Lebbra dell’olivo (Colletotrichum spp.), soprattutto negli oliveti storicamente sensibili; al momento nessuna recrudescenza significativa è stata rilevata nei campionamenti.… www.arpa.veneto.it/temi-ambientali/agrometeo/file-eallegati/bollettino_agrometeo_regionale_settimanale.pdf Villa do s e»
- **OBSERVACAO/PREVISAO** — Spilocaea oleaginea: «Parassiti fungini Le precipitazioni della settimana scorsa e l’aumento dell’umidità relativa possono favorire Occhio di pavone (Spilocaea oleaginea), Piombatura dell’olivo (Mycocentrospora cladosporoides), Lebbra dell’olivo (Colletotrichum spp.), soprattutto negli oliveti storicamente sensibili; al momento nessuna recrudescenza significativa è stata rilevata nei campionamenti.… www.arpa.veneto.it/temi-ambientali/agrometeo/file-eallegati/bollettino_agrometeo_regionale_settimanale.pdf Bagnolo di Po»

## 3 · Que fontes JÁ cadastradas publicam contagens (medido no acervo)

| Fonte (cadastrada) | Estado no robô (vivo `dc0de726`) | Publica contagens? | O quê, em que forma | Frequência (medida) |
|---|---|---|---|---|
| **IT-T3-002** Campania — Bollettini fitosanitari regionali (Salerno) | READY_FOR_COLLECTION | **SIM** | «n. N catture di <organismo>» **por azienda/località**, em PDF | ~14 dias (N° 25 · 02/09 → N° 27 · 16/09) |
| **IT-T3-005** Terre dell'Etruria | SEMANTIC_REVIEW (sem ficha no Atlas; contrato no `.mjs`) | **SIM (% infestação)** | % de infestação ativa + estado **por ponto** (HTML); **capturas de adultos só para registados** | amostras a cada ~7 dias por ponto |
| **IT-T3-010** APOL Lecce — monitoraggio olivicolo | READY_FOR_COLLECTION | **PROVÁVEL, não provado** | números por comprensorio (PDF), mas **o que cada coluna mede = NAO SEI** (cabeçalho em imagem) | semanal (n.9 · 07/09 → n.10 · 14/09) |
| IT-T3-008 ARIF Puglia | READY_FOR_COLLECTION | **NÃO (números)** — **SIM (observação escrita)** | «Catture di anarsia/tignoletta/Tuta… nelle trappole a feromoni», «Aumento del numero di punture…» + limiares | 14 dias (N36 · 02/09 → N38 · 16/09) |
| IT-T2-002 ARPAV Agrometeo Informa | READY_FOR_COLLECTION | **NÃO** | texto regional (mosca: «pressione stabile»; cimici presentes; danos de margaronia) | semanal (N° 54 → N° 56) |
| IT-T3-027 ERSA FVG | CONTRACTED_CANARY_FAILED | **NAO SEI** | PDF «Monitoraggio Halyomorpha halys 18-agosto-2026» + boletins por cultura — **não estão no acervo** | — (comando pronto: `LOTE-PDF-SERIES`, ronda 1) |
| IT-T3-053 Umbria — Bollettini fitosanitari | READY_FOR_COLLECTION | **NAO SEI** | boletins semanais olivo/vite/nocciolo 2026 em PDF — **não estão no acervo** | semanal pelos nomes (comando pronto: 12 rondas) |

## 4 · O que não se sabe (e porquê)

- **APOL:** o que medem as colunas «7/5/4→6», «1», «5%» — o cabeçalho é imagem. Ver o PDF (ou OCR) antes de usar como número.
- **Salerno, olivo:** a que localidade (Campagna ou Agropoli) pertence cada valor — colunas misturadas no PDF.
- **ARIF:** a cultura e a área de cada bloco (títulos em imagem) e o par entre números (32 vs 31 blocos).
- **ARPAV N° 56:** a secção fitossanitária vem cortada no próprio PDF.
- **Terre dell'Etruria:** as capturas de adultos (atrás de login — fora, por regra).

## EM PALAVRAS SIMPLES

- **Li tudo o que já temos guardado** de boletins de pragas: 16 documentos. Não usei internet.
- **Achei 66 séries com números** — sempre com 2 medidas (as duas datas que guardámos):
  - **52 pontos na Toscana** (Terre dell'Etruria) com a % de azeitonas infestadas; em 20 o número mudou (ex.: um ponto em
    Roccastrada passou de 4% para 7% e ficou em «alerta»).
  - **11 armadilhas em Salerno**, fazenda a fazenda: a mosca-do-mediterrâneo nos citrinos subiu de 4 para 40 capturas em
    duas semanas; a traça da uva de 3 para 5; a tuta da beringela de 6 para 9.
  - **3 zonas na Puglia** (APOL) com números que sobem — mas o título da tabela é uma imagem, então não sei dizer o que cada
    número mede.
- **Outras duas fontes contam em palavras, não em números:** a Puglia (ARIF) escreve «apanhámos traças nas armadilhas» e
  «aumentaram as picadas da mosca»; o Veneto (ARPAV) escreve «pressão estável».
- **Friuli e Úmbria** ainda não estão no nosso arquivo — o comando para os buscar já está pronto (entrega anterior).
