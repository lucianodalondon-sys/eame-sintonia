# REGIONE PIEMONTE — LOTTA OBBLIGATORIA FLAVESCENZA DORATA 2026

## 0. O que foi aberto, e o que estava lá

A página oficial abriu (HTTP 200, 207.492 bytes). Na caixa **"Allegati"** do rodapé estão, com esses nomes exatos, os dois anexos pedidos:

- **"Sintesi disposizioni 2026" — File pdf - 449.97 KB** → `https://www.regione.piemonte.it/web/media/12286/download`. O servidor entrega com o nome real `2026_Misure obbligatorie.pdf` (Last-Modified: 31/03/2026). Título interno: **"MISURE FITOSANITARIE OBBLIGATORIE PER LA GESTIONE DELLA FLAVESCENZA DORATA – ANNO 2026"** (é o **Allegato 2** da D.D. 280).
- **"Piano operativo 2026" — File pdf - 203.64 KB** → `https://www.regione.piemonte.it/web/media/12285/download`, nome real `2026_Piano operativo.pdf` (Last-Modified: 31/03/2026). Título interno: **"PIANO OPERATIVO FLAVESCENZA DORATA DELLA VITE - ANNO 2026"** (é o **Allegato 3** da D.D. 280).

Os dois **abriram e vieram com texto extraível**. Li o corpo inteiro dos dois, não só o título.

Aviso operacional importante: **os anexos NÃO se acham filtrando `.pdf` no HTML bruto.** Os links da caixa "Allegati" são rotas do CMS (`/web/media/<id>/download`), sem `.pdf` no href. O filtro por `.pdf` devolve 28 endereços — e nenhum deles é a Sintesi ou o Piano operativo. Quem parar no filtro por `.pdf` conclui erradamente que os anexos não estão na página.

Segundo aviso operacional: `scripts/texto_fonte.py` e `scripts/pdf_text.py` **devolveram lixo** nesses PDFs (fonte em subconjunto sem mapa /ToUnicode utilizável). Quem lesse só por eles diria "PDF ilegível" — e estaria errado. O `pdftotext` que já existe no Git Bash (`/mingw64/bin/pdftotext`, chamado com `-layout -enc UTF-8`) leu tudo limpo.

Também baixei e li, porque completam a resposta: **"Insetticidi ammessi 2026"** (`/web/media/48262/download`, nome real `11_Insetticidi Ammessi_2026_bis.pdf`, Last-Modified **30/04/2026**), o **Allegato 1 — Area delimitata 2026**, a **D.D. 280/2026 na íntegra**, o slide **"Aggiornamento situazione / strategie 2026"** e o slide **"Sintesi monitoraggi Progetti Pilota – anno 2025"**.

Arquivos salvos (PDF + texto extraído) em `C:\eame-sintonia\data\samples\PIEMONTE-FD\`:
`sintesi_disposizioni_2026.pdf` / `_pt.txt`, `piano_operativo_2026.pdf` / `_pt.txt`, `insetticidi_ammessi_2026.pdf` / `_pt.txt`, `area_delimitata_2026.pdf` / `_pt.txt`, `dd_280_2026.pdf` / `_pt.txt`, `aggiornamento_2025_strategie2026.pdf` / `_pt.txt`, `progetti_pilota_2025.pdf` / `_pt.txt`, `locandina_2026.pdf` / `_pt.txt`, `pagina.html`, `pagina.txt`.

O ato-mãe é a **Determinazione Dirigenziale n. 280 de 16 de março de 2026** (publicada no B.U. 12 de 26/03/2026), que "aprova um único ato que compreende tanto as Misure fitosanitarie quanto o Piano operativo para o ano de 2026". Ela substitui a D.D. n. 268 de 26/03/2025.

---

## 1. Janelas de tratamento obrigatório de 2026 — com data exata

**Atenção, e isto é o principal desta seção: os dois anexos NÃO trazem as datas de calendário dos tratamentos.** As datas de cada tratamento são fixadas por área, ao longo da temporada, e publicadas em boletins. O texto literal do anexo Sintesi (§3.1):

> "Devono essere effettuati obbligatoriamente minimo due trattamenti insetticidi all'anno, **da effettuarsi nei giorni indicati nei Bollettini e nei Comunicati** pubblicati sul sito internet ufficiale regionale alla pagina https://www.regione.piemonte.it/web/temi/agricoltura/servizi-fitosanitari-pan/lotte-obbligatorie-flavescenza-dorata – Bacheca dei bollettini."

E na página, em negrito: *"A seguito del rilievo delle forme giovanili dell'insetto, per ciascun Progetto pilota sono stabilite le date dei trattamenti insetticidi obbligatori sul territorio"*.

Tentei ler a Bacheca dei bollettini. Ela redireciona (301) para `https://dashboard01.green-planet.it/`, que responde HTTP 200 com uma única linha: *"Non è possibile accedere a questo sito direttamente"*. Ou seja: **as datas de calendário de 2026 por área existem e estão publicadas, mas ficam num painel externo que bloqueia acesso HTTP direto. Eu NÃO SEI quais são. Isso é um estado de acesso bloqueado, não ausência de datas.**

O que os documentos de 2026 **dizem com data exata**, tudo citado literalmente:

| Prazo / janela | Frase literal | Fonte |
|---|---|---|
| Extirpação das plantas sintomáticas | "l'estirpazione dovrà avvenire entro la successiva ripresa vegetativa e **comunque non oltre il 31 marzo**" | Sintesi §1 |
| Prorrogação máxima dos trabalhos prescritos | "In ogni caso le proroghe **non possono essere accordate oltre il 30 aprile**" | Piano operativo, All. 3.B §6 |
| Prescrições enviadas / trabalhos concluídos | "Le prescrizioni sono inviate principalmente **nel periodo novembre-gennaio** di ogni anno e gli interventi devono essere completati **entro il mese di marzo**" | Piano operativo, All. 3.B §6 |
| Vistorias de verificação | "Gli assistenti fitosanitari incaricati effettuano **nei mesi di aprile e maggio** i sopralluoghi di verifica dell'adempimento alle prescrizioni" | Piano operativo, All. 3.B §7 |
| Avisos dos Comuni (extirpação) | "i tempi di esecuzione degli interventi (che devono essere svolti **da metà ottobre ed entro il mese di marzo**)" | Piano operativo, All. 3.B §B |
| Bio — 3 tratamentos | "tre trattamenti fitosanitari sui giovani, **ripetuti ogni 7-10 giorni indicativamente nel mese di giugno**" | Sintesi §3.2 |
| Zonas indenes — 1 tratamento | "deve essere effettuato obbligatoriamente minimo un trattamento insetticida all'anno, **posizionato al più tardi entro la prima decade di luglio**" | Sintesi §3.3 |
| 1º tratamento quando há redução | "Il primo trattamento insetticida deve comunque essere **posizionato al più tardi entro la prima decade di luglio**" | Sintesi §3.5 |
| Pedido de redução de tratamentos | "devono comunicarlo **entro il 30 giugno 2026** via e-mail al Settore Fitosanitario e servizi tecnico-scientifici all'indirizzo virologia@regione.piemonte.it" | Sintesi §3.5 |
| Levantamento das formas jovens | "due campionamenti degli stadi giovanili di S. titanus, il primo **indicativamente a inizio giugno** ed il secondo dopo il primo trattamento" | Sintesi, All. 2.B §1 |
| Armadilhas cromotáticas | "Devono essere posizionate **a fine giugno** e sostituite quando hanno perso la capacità incollante o comunque **ogni 15 giorni** circa" | Sintesi, All. 2.B §3 |
| Denúncia de situação de risco | "le segnalazioni devono pervenire in un periodo utile... e quindi **entro il 15 luglio di ogni anno**" | Piano operativo, All. 3.B §A.3 |
| Vistorias das denúncias | "Gli accertamenti relativi alle segnalazioni si svolgono **indicativamente nel periodo giugno-settembre** di ogni anno" | Piano operativo, All. 3.B |
| Serviço telefônico de dúvidas | "Tale servizio è attivo **solo fino al 31 marzo** in quanto a partire dal mese di aprile iniziano le verifiche in campo" | Piano operativo, All. 3.B §6 |
| Derrogação do **Sulfoxaflor** | "Prodotto fitosanitario impiegabile con deroga semplificata ai Disciplinari di produzione integrata della Regione Piemonte 2026 **dal 1 maggio al 28 agosto**" | Insetticidi ammessi 2026 |
| Derrogação do **caolino** | "Prodotto fitosanitario impiegabile con deroga semplificata ai Disciplinari di produzione integrata della Regione Piemonte 2026 **dal 1 aprile al 29 luglio**" | Insetticidi ammessi 2026 |

O critério biológico do posicionamento (do slide de estratégias 2026): *"→ 1° trattamento : giovani di 3ª età; → 2° trattamento : giovani di 5ª età + primi adulti; [→ 3° trattamento : adulti - LADDOVE NECESSARIO]"*.

Regra que atravessa todas as janelas: *"i trattamenti non devono comunque essere effettuati durante il periodo di fioritura della vite"* (D.D. 280, premessa) e, no folheto de insetticidas, para o bio: *"SOLO SUI GIOVANI DI SCAFOIDEO. NON ESEGUIRE DURANTE LA FIORITURA"*.

---

## 2. Quantos tratamentos, e a diferença convencional × biológico

**Produção integrada (obrigatória e facultativa) e demais empresas vitícolas — DOIS obrigatórios + um eventual terceiro.**

> "Devono essere effettuati obbligatoriamente minimo due trattamenti insetticidi all'anno" (Sintesi §3.1)

> "Se il livello di popolazione del vettore lo richiede, oppure in caso di elevata incidenza di flavescenza dorata oppure in impianti situati in prossimità di vigneti abbandonati, di incolti o di capezzagne con presenza di viti inselvatichite, **deve essere effettuato un terzo trattamento insetticida** ammesso nei Disciplinari 2026 di Produzione Integrata approvati con Determinazione Dirigenziale del 10 marzo 2026, n. 256" (Sintesi §3.1)

O folheto "Insetticidi ammessi 2026" resume: **"DUE trattamenti insetticidi obbligatori — NEL PERIODO INDICATO DAI BOLLETTINI REGIONALI, DOPO LA FINE DELLA FIORITURA + un TERZO trattamento ove necessario"**.

**Agricultura biológica — TRÊS obrigatórios.**

> "Le aziende viticole in agricoltura biologica **devono effettuare obbligatoriamente tre trattamenti fitosanitari sui giovani**, ripetuti ogni 7-10 giorni indicativamente nel mese di giugno, con piretro naturale (estratto di Chrysanthemum cinerariaefolium) o, in alternativa, il primo trattamento con sali potassici, con aggiunta di condizionatori d'acqua utili a evitare precipitazione e flocculazione del prodotto, oppure il primo trattamento con azadiractina, mantenendo in ogni caso i due successivi trattamenti con piretro naturale" (Sintesi §3.2)

> "In aggiunta ai tre trattamenti obbligatori possono essere effettuati trattamenti contro le forme giovanili dell'insetto con altri prodotti utilizzabili in agricoltura biologica contro Scaphoideus titanus o cicaline" (Sintesi §3.2)

**A diferença de fundo entre os dois regimes**, dita pela própria D.D. 280 na premessa: o bio ataca as formas jovens, e por isso é antecipado e repetido —

> "il piretro, i sali potassici degli acidi grassi e l'azadiractina, che hanno efficacia prevalentemente contro le forme giovanili dell'insetto; **i trattamenti devono essere anticipati rispetto a quelli eseguiti dalle aziende in produzione integrata** e ripetuti ogni 7-10 giorni indicativamente nel mese di giugno"

**Zonas indenes — mínimo UM por ano**, até a primeira década de julho (Sintesi §3.3).

**Viveiros — TRÊS ou QUATRO, sem redução possível.**

> "Nei campi di piante madri per marze devono essere obbligatoriamente eseguiti **tre trattamenti** insetticidi; nei campi di piante madri di portinnesti e nei barbatellai devono invece essere effettuati **quattro trattamenti**. **Non sono possibili riduzioni** del numero dei trattamenti insetticidi obbligatori, previsti nel punto 3.5." (Sintesi §3.7)

**Redução do número de tratamentos — condições numéricas exatas (Sintesi §3.5).**

> "Esclusivamente nelle situazioni in cui non sono presenti piante con sintomi e viene opportunamente documentata l'esiguità di popolazione di Scaphoideus titanus, il numero dei trattamenti obbligatori può essere ridotto. (...) Un risultato di densità **non superiore a 0,02 forme giovanili per pianta**, prima del primo trattamento insetticida 2026, e **massimo 2 catture di insetto adulto complessive**, sul totale delle trappole posizionate in vigneto, e sostituite ogni 15 giorni, nel periodo fine giugno-fine settembre dell'anno precedente."

> "Al superamento della soglia di 0,02 forme giovanili per pianta o di 2 catture complessive di adulti o si rilevino piante con sintomi riconducibili a Flavescenza dorata, **si ritorna all'obbligatorietà** per le aziende viticole in produzione integrata (obbligatoria e facoltativa) di eseguire i due trattamenti insetticidi previsti nel punto 3.1 e per le aziende viticole in agricoltura biologica i tre trattamenti insetticidi previsti nel punto 3.2."

O Allegato 2.B esclarece a magnitude da redução no integrado: *"che intendono ridurre il numero degli interventi insetticidi **da 2 a 1**"*. E a premessa da D.D. 280, para o bio: *"i trattamenti potranno essere ridotti a due"*.

---

## 3. Substâncias ativas admitidas, e o critério de rótulo (a parte mais importante)

### 3.1 A resposta direta sobre o critério de rótulo: **SIM, o Piemonte tem critério equivalente ao da Lombardia — e está escrito com todas as letras.**

Frase literal, Sintesi disposizioni 2026, §3.1:

> "**In ogni caso, i formulati commerciali utilizzati nella lotta obbligatoria devono necessariamente indicare in etichetta la registrazione come coltura da difendere la vite e ricondurre all'insetto target Scaphoideus titanus (ad esempio deve riportare come avversità: scafoideo, cicaline, cicadellidi, cicalina della flavescenza dorata).**"

Leitura, sem esticar: o Piemonte exige **duas coisas no rótulo ao mesmo tempo** — (a) a videira registrada como cultura a defender, e (b) uma indicação que remeta ao inseto-alvo *Scaphoideus titanus*. E o próprio texto abre a lista de formas aceitas com "ad esempio" (por exemplo), citando quatro: **scafoideo, cicaline, cicadellidi, cicalina della flavescenza dorata**.

Comparando com o que o briefing informa sobre a Lombardia (rótulo com "cicaline della vite" ou "Scaphoideus titanus"): a exigência é do mesmo tipo — o rótulo tem de amarrar no alvo. A lista piemontesa, como está escrita, é mais larga em vocabulário (aceita "cicadellidi" e "scafoideo") e é declaradamente exemplificativa, não fechada. **Não afirmo que a lista piemontesa seja exaustiva nem que "cicaline della vite" sozinho baste ou não baste no Piemonte — o documento não diz isso, então NÃO SEI.** E não li o ato da Lombardia nesta tarefa; a comparação usa o enunciado do briefing como dado, não como fonte lida.

Duas condições de contorno que andam junto com esse critério, também literais (Sintesi §3.1):

> "È necessaria un'attenta scelta dei formulati commerciali delle sostanze attive ammesse nella lotta allo scafoideo, considerando che i prodotti commerciali possono riportare in etichetta sostanziali differenze in relazione alla composizione, agli insetti bersaglio, alle dosi di impiego, al numero massimo di applicazioni e agli intervalli tra i trattamenti."

> "Occorre, inoltre, considerare che i Disciplinari di Produzione Integrata specificano il numero massimo di applicazioni possibili all'anno per ogni sostanza attiva e il limite complessivo del gruppo chimico, indipendentemente dall'avversità."

### 3.2 As substâncias, listadas

**Produção integrada e demais empresas vitícolas** (Sintesi §3.1 + folheto "Insetticidi ammessi 2026"):

- **1º tratamento — ação sistêmica:** **ACETAMIPRID**, **FLUPYRADIFURONE**. Frase literal: *"il primo trattamento insetticida deve essere effettuato con un insetticida ad azione sistemica, scegliendo tra le seguenti sostanze attive: Acetamiprid e Flupyradifurone."*
- **SULFOXAFLOR**, condicionado. Sintesi: *"La sostanza attiva Sulfoxaflor, **qualora venga rilasciata l'autorizzazione all'impiego** di prodotti fitosanitari, ai sensi del Regolamento (CE) 1107/2009 art. 53, per situazioni di emergenza fitosanitaria (usi eccezionali), sarà inserita nei bollettini regionali di avviso dei trattamenti insetticidi contro scafoideo."* No folheto de 30/04/2026 ele já aparece listado no 1º tratamento com asterisco e a derrogação de **1 de maio a 28 de agosto de 2026**.
- **2º tratamento — ação abatente:** **ETOFENPROX, DELTAMETRINA, ESFENVALERATE, LAMBDA-CIALOTRINA, TAU-FLUVALINATE.** Literal: *"Il secondo trattamento insetticida deve essere effettuato con un insetticida ad azione abbattente scegliendo tra i seguenti principi attivi: Etofenprox, Deltametrina, Esfenvalerate, Lambda-cialotrina, Tau-fluvalinate."*
- **3º tratamento (eventual):** *"Sostanza attiva a scelta tra quelle indicate per i due trattamenti obbligatori. Non utilizzare sostanza attiva candidata alla sostituzione, se già utilizzata in precedenza. Si sconsiglia l'utilizzo di un piretroide, se già utilizzato per il secondo trattamento."*

**Agricultura biológica** (folheto "Insetticidi ammessi 2026" + Sintesi §3.2):

- **PIRETRO** (piretro naturale, estratto de *Chrysanthemum cinerariaefolium*) — nos três, ou nos 2º e 3º.
- **SALI POTASSICI DI ACIDI GRASSI** ou **AZADIRACTINA** — alternativas apenas para o 1º.
- Dose citada literalmente: *"Per il piretro è necessario garantire la distribuzione di **almeno 30 g/ha di principio attivo**"*.
- Água dura: *"Se si utilizzano i sali potassici in zone con acque dure si garantisce una migliore azione con l'aggiunta di condizionatori d'acqua utili a evitare precipitazione e flocculazione del prodotto"*.
- **Em acréscimo (facultativos):** **OLIO DI ARANCIO DOLCE, PRODOTTI MICROBIOLOGICI, SILICATO DI ALLUMINIO (CAOLINO)*** — o caolino com derrogação de **1 de abril a 29 de julho de 2026**.

**Uma incerteza que o próprio documento deixa em aberto:** o slide "Aggiornamento situazione e strategie per il 2026" traz, ao lado da estratégia do 1º tratamento, a anotação **"2026? — 1 solo Acetamiprid annuo consentito su vite (etichetta)"**. Está escrito com ponto de interrogação, num slide, e **não** aparece nem na D.D. 280 nem na Sintesi nem no folheto de insetticidas. Registro como pergunta em aberto no material oficial, não como regra. **Se vale ou não para 2026: NÃO SEI.**

**Regra de estratégia anti-resistência**, literal (D.D. 280, premessa): *"attualmente la migliore strategia per il controllo di S. titanus consiste nell'utilizzare per il primo trattamento i prodotti sistemici (Acetamiprid e Flupyradifurone) e per il secondo trattamento i piretroidi e i fenossibenzil eteri (Deltametrina, Esfenvalerate, Lambda-cialotrina, Tau-fluvalinate ed Etofenprox)"*.

**Proibição de alvo:** *"Il trattamento deve essere rivolto al vigneto, anche in prossimità di incolti o capezzagne con presenza di viti inselvatichite: **è vietato trattare con insetticidi gli incolti e le capezzagne**, al fine di evitare danni agli insetti pronubi e alle api."* (Sintesi §3.1)

---

## 4. Zonas delimitadas — e uma correção de vocabulário

**O Piemonte NÃO usa o trio "focolaio / insediamento / indenne" nestes documentos.** Procurei as palavras nos cinco textos extraídos. "insediamento" não aparece nenhuma vez como nome de zona. "focolai" aparece duas vezes, e apenas como descrição solta dentro do modelo de carta do Allegato 3.C (*"un vigneto abbandonato in cui si sviluppano pericolosi focolai di infezione"*), não como categoria de zoneamento. **Se o Piemonte usa esses nomes em algum outro ato que eu não li: NÃO SEI.** O que li usa outra nomenclatura, que é esta:

**Area delimitata = zona infestata + zona cuscinetto.** Literal, Sintesi, abertura:

> "L'area delimitata è costituita dalla **zona infestata**, definita sulla base dei confini amministrativi comunali, e dalla **zona cuscinetto**, fascia di estensione di almeno 500 m di raggio, adiacente e circostante la zona infestata."

E o Allegato 1: *"**Zona cuscinetto**: zona circostante la zona infestata e ricadente in un raggio di 500 m dalla stessa"*.

**O que muda em cada uma:**

- **Dentro da area delimitata (infestata + cuscinetto):** aplica-se o pacote inteiro, e — este é o ponto que muda tudo na prática — **em todo o território municipal**, não só no talhão focal. Literal, Sintesi: *"Le misure fitosanitarie obbligatorie devono essere applicate, sulla base dei confini amministrativi, **su tutto il territorio di competenza comunale dei Comuni ricadenti nell'area delimitata**."* E na D.D. 280, item 2 do dispositivo, com a mesma redação. Isso significa: mínimo **2** tratamentos no integrado (+1 eventual), **3** no bio.
- **Zone indenni:** mínimo **1** tratamento por ano, até a primeira década de julho (Sintesi §3.3).
- **Em qualquer zona, inclusive nas indenes**, vale a obrigação sobre vinhedo abandonado — literal, Sintesi §2.1: *"**In qualunque tipologia di zona del territorio regionale, ivi comprese le zone indenni**, qualora siano presenti superfici vitate in stato di abbandono... è fatto obbligo... di provvedere all'estirpazione di tutte le viti insistenti sull'intero appezzamento"*.
- Os documentos que li **não definem "zona indenne"** com um critério escrito, nem trazem a lista dos comuni indenes. Só a usam por oposição à area delimitata. **A definição formal: NÃO SEI.**

**Tamanho da area delimitata 2026** (Allegato 1, 4 páginas de listas nominais de comuni):

- **Zona infestata:** Alessandria 167, Asti 117, Biella 18, Cuneo 89, Novara 22, Torino 79, Vercelli 11 — **503 comuni**, 7 províncias.
- **Zona cuscinetto:** Alessandria 19, Biella 29, Cuneo 68, Novara 24, Torino 125, Vercelli 24 — **289 comuni**, 6 províncias. **A província de Asti não aparece na lista da zona cuscinetto.**

Ressalva honesta: **esses totais são contagem minha**, feita quebrando as listas por vírgula. O PDF **não declara nenhum total**. A ausência de Asti no cuscinetto é o que está escrito na lista; o documento **não explica o porquê**, e eu não vou inventar a explicação.

Escala do território coberto, literal (Piano operativo, premessa): *"tutelare la viticoltura in tutto il territorio regionale, **interessando una superficie che supera i 40 mila ettari**"*.

---

## 5. Obrigações de extirpação de plantas sintomáticas

Frase-mãe, Sintesi §1:

> "**E' sempre obbligatorio** asportare la vegetazione sintomatica oppure capitozzare le piante sintomatiche, **senza necessità di analisi di conferma e senza attendere la vendemmia**; eliminare eventuali ricacci fino al momento dell'estirpazione del ceppo e delle radici; l'estirpazione dovrà avvenire entro la successiva ripresa vegetativa e comunque **non oltre il 31 marzo**. Tali operazioni **devono essere effettuate almeno due volte durante la stagione vegetativa** e preferibilmente dopo ogni trattamento insetticida, al fine di evitare lo spostamento, sulle piante adiacenti, degli scafoidei presenti sulla vegetazione sintomatica da eliminare."

**Limiar dos 20% — extirpação do talhão inteiro** (Sintesi §1.1):

> "Negli appezzamenti di vite in cui **oltre il 20% delle piante vive risulta sintomatico** — percentuale determinata anche solo sulla base di un campione individuato secondo una metodologia statisticamente idonea a garantirne la rappresentatività rispetto all'intero vigneto — **l'intero appezzamento, o parte di esso, deve essere obbligatoriamente estirpato**."

**O que não precisa e o que precisa ser retirado** (Sintesi §1): *"Non è necessario allontanare o bruciare immediatamente la vegetazione eliminata, in quanto le foglie in via di appassimento non sono appetite dal vettore. E', invece, fondamentale rimuovere dalle vicinanze del vigneto **il legno di potatura superiore ai due anni**, al fine di eliminare le eventuali uova di S. titanus presenti."*

**Obrigações de inverno** (Sintesi §1): eliminar e destruir a videira asselvajada nos incultos, bosques, ribanceiras e gerbidos vizinhos; extirpar as plantas que manifestaram sintomas; afastar do vinhedo e destruir os toros extirpados; triturar finamente os resíduos de poda ou retirá-los.

**Consequência do descumprimento** (Sintesi §1): *"in caso di inadempienza verrà inviata comunicazione ai soggetti responsabili e **l'unità vitata sarà bloccata sul fascicolo aziendale e non si potrà procedere alla Dichiarazione di vendemmia**; qualora siano tempestivamente eseguiti gli interventi, si procederà allo sblocco dell'unità vitata."* E: *"si procederà ai sensi della normativa vigente, con applicazione delle sanzioni previste e con **eventuale esecuzione d'ufficio degli interventi a spese degli obbligati**."*

**Vinhedos descuidados / abandonados / videira asselvajada** (Sintesi §2.1 a 2.3): abandonado sem condição de tratar → extirpação de todas as videiras do talhão; descuidado → ou restabelecer as condições normais de cultivo (postes e arames, poda de inverno, roçada da entrelinha, gestão da sublinha, desponta, tratamentos obrigatórios, eliminação da vegetação sintomática) ou extirpar tudo; videira asselvajada em terrenos não agrícolas → eliminação.

**Classificação usada nas vistorias** (Piano operativo, All. 3.B): TIPO 1A vinhedo produtivo cuidado; **TIPO 1B trascurato**; TIPO 2 abandonado há poucos anos (máx. 5); TIPO 3 abandonado há muitos anos ou extirpação malfeita; TIPO 4 incolto propriamente dito; TIPO 5 em fase de extirpação incompleta.

---

## 6. Quem está obrigado

**Profissional e hobista, lado a lado, sem distinção de dever.** Literal, Sintesi §1: *"Le misure sopra riportate **devono essere eseguite da tutte le aziende viticole e dai conduttori hobbisti**."* E §3: *"**Tutte le aziende viticole e i conduttori hobbisti** sono tenuti a eseguire, o far eseguire, obbligatoriamente i trattamenti insetticidi indicati sulla base delle misure obbligatorie definite dal Settore Fitosanitario."* E §3.6, sobre a proteção às abelhas: *"**Quanto sopra è valido anche per gli hobbisti che operano su proprietà private.**"*

**Terreno incolto e terreno não cultivado.** Sintesi §2.1: *"è fatto obbligo **ai proprietari, conduttori o detentori a qualsiasi titolo dei terreni interessati** di provvedere all'estirpazione di tutte le viti insistenti sull'intero appezzamento; tale obbligo si applica altresì a tutte le piante di vite, **comprese quelle inselvatichite, presenti su terreni non coltivati, incluse le superfici ritirate dalla produzione, nonché le superfici destinate alla conservazione di elementi naturaliformi o alla vegetazione spontanea**."*

**Terreno não agrícola (beira de estrada, rio, ferrovia, rodovia).** Sintesi §2.3: *"sono tenuti a intervenire in tali aree **i soggetti pubblici o privati, responsabili dell'effettuazione degli interventi di manutenzione e di bonifica del territorio o delle reti in esso presenti**."*

**Quem adere a CSR / SQNPI tem dever extra de registro.** Sintesi §3: quem adere ao SRA01-ACA1 (produção integrada), SRA29 (produção biológica) e ao SQNPI *"devono obbligatoriamente seguire le strategie e utilizzare i prodotti fitosanitari indicati nei Bollettini e nei Comunicati... e devono registrare i trattamenti insetticidi indicando le dosi e i volumi di acqua utilizzati... In caso di inosservanza saranno applicate specifiche penalizzazioni e sanzioni."* Os demais podem usar a ficha do Allegato 2.C.

**Revendedores de defensivos.** Sintesi §3.1: *"**I rivenditori di fitofarmaci sono obbligati alla diffusione delle misure obbligatorie** inerenti i trattamenti insetticidi sopra riportate."*

**Comuni.** Sintesi §4.4 e Piano operativo: difundir as medidas inclusive aos hobistas, sinalizar abandono e videira asselvajada, gerir a videira asselvajada nas estradas municipais, apoiar nos casos críticos de "terreni silenti", e **atualizar os Regolamenti di polizia rurale** com as medidas contra a flavescência.

**Sanções citadas nos documentos:** art. 55 do D.Lgs. 2/02/2021 n. 19; suspensão de qualquer contributo econômico agrícola e de desenvolvimento rural até o cumprimento; limitações à potencialidade produtiva das superfícies vitadas; bloqueio do fascicolo aziendale com impedimento da Dichiarazione di vendemmia; extirpação coativa a expensas do infrator; e, especificamente na proteção aos polinizadores, **"la sanzione amministrativa da euro 200,00 ad euro 1.200,00"** (L.R. 1/2019, art. 97 c. 4 a).

---

## 7. Números de monitoramento de 2025

Da própria **D.D. 280/2026**, no corpo do ato (portanto lido, não deduzido do título):

> "La vigilanza sulle segnalazioni di situazioni a rischio per la diffusione della malattia **nell'anno 2025** ha richiesto un notevole impegno del Settore Fitosanitario e servizi tecnico-scientifici, **con il controllo di 674 appezzamenti**."

> "ispezione di tutti i campi di piante madri... e ispezione dei barbatellai di vite (**54 aziende vivaistiche, circa 2300 campi di piante madri**)"

Do **slide "Sintesi monitoraggio Progetti Pilota in Piemonte 2025"** e do slide **"Aggiornamento della situazione e strategie per il 2026"** (documentos separados dos dois anexos pedidos — registro a origem para não misturar):

**Rede de monitoramento, pontos por ano:** 2022 → 450; 2023 → 532; 2024 → 608; **2025 → 616 punti di monitoraggio**, *"con oltre 10.400 trappole monitorate"* (o rodapé do gráfico precisa: **10.496 trappole**). Ressalva do próprio slide: *"Dati elaborati escludendo i valori anomali e i vigneti con meno di 7 trappole consegnate"*.

**Capturas médias de S. titanus por armadilha:** 2022 → 2,1; 2023 → 1,6; 2024 → 1,3; **2025 → 2,1**. Distribuição 2025 por classe: 8,6% (zero) / 42,9% (0-1) / 17,5% (1-2) / 19,5% (2-5) / **11,5% (>5)**. Frases literais: *"51,5% vigneti con catture medie non superiori a 1 St/trappola"*; *"11,5% vigneti con catture medie superiori a 5 St/trappola"*; *"Nel 2025 **diminuiscono** i vigneti con catture medie non superiori a 1 St/trap (**-15%** rispetto al 2024)"*; *"Nel 2025 **aumentano** i vigneti con catture medie superiori a 5 St/trap (**+7%** rispetto al 2024)"*.

**Curva de voo 2025:** *"Picco di volo **anticipato (seconda metà di luglio)** rispetto al 2024, ad eccezione dell'Alessandrino e del Doglianese. **Secondo picco nella terza settimana di agosto** in Canavese, Gaviese e Valle Belbo."* E: *"Picco di volo 2025 più basso rispetto al 2022 e 2023"*.

**Incidência média de FD.** O slide traz os quatro anos **2022, 2023, 2024, 2025** e os quatro valores **7,01% · 7,76% · 5,22% · 4,87%**. **A extração perdeu o alinhamento da coluna**, então a associação ano↔valor não está garantida pelo texto que eu li. A ordem em que aparecem sugere 2022→7,01%, 2023→7,76%, 2024→5,22%, 2025→4,87%, mas **isso é inferência minha, não leitura**. O que está numa frase corrida, e portanto é firme: *"A livello regionale nel 2025 si è rilevato un andamento analogo dei casi con FD superiore al 20% e FD inferiore al 5% rispetto alla situazione del 2024 ( **<5% → 2025: 71% ; 2024: 70%** )"*. Distribuição 2025 das classes de presença em vinhedo, lida do gráfico: 5% / 9% / 19% / 15% / 32% / 20% — **a associação classe↔valor também se perdeu na extração; NÃO SEI qual valor vai com qual faixa.**

**Projetos-piloto 2025** (slide, tabela parcialmente embaralhada na extração — dou só o que está legível sem ambiguidade): Alessandrino 92 comuni; Canavese & Eporediese 25; Barolo & Barbaresco 15; Doglianese & Monregalese 12; Gaviese 9; Nicese & Val Tiglione 26; Cuneese Area Moscato 16; Valle di Susa 7 comuni, 5 vinhedos bio, 11 convencionais, 16 no total. As demais colunas de vinhedos bio/convencionais/total **saíram desalinhadas na extração e eu não vou pareá-las por chute**. Nota de rodapé do próprio slide: *"* con almeno 7 trappole consegnate nel monitoraggio"*.

Da página (não do PDF): os projetos-piloto *"coinvolgono **oltre 180 comuni**"*.

---

## 8. Onde eu digo NÃO SEI

1. **Datas de calendário dos tratamentos obrigatórios de 2026, por área.** Existem e são publicadas — os documentos mandam consultar a Bacheca dei bollettini. A Bacheca redireciona para um painel externo que responde *"Non è possibile accedere a questo sito direttamente"*. Estado: acesso bloqueado. Não li.
2. **Definição formal de "zona indenne" e lista dos comuni indenes.** Os documentos usam o termo, não o definem nem listam.
3. **Se o Piemonte usa "focolaio/insediamento" como zonas em algum outro ato.** Nestes documentos, não usa.
4. **Se a lista de termos de rótulo ("scafoideo, cicaline, cicadellidi, cicalina della flavescenza dorata") é exaustiva.** O texto abre com "ad esempio", o que indica exemplo, mas o documento não diz o que fica de fora.
5. **A regra "1 solo Acetamiprid annuo consentito su vite (etichetta)".** Aparece só num slide, marcada com "2026?", e não aparece na D.D. 280, na Sintesi nem no folheto de insetticidas.
6. **A associação ano↔valor da incidência média de FD e classe↔valor da distribuição de presença.** Perdidas na extração do gráfico.
7. **Totais oficiais de comuni por zona.** Contei 503 e 289; o PDF não declara total nenhum.

Nada aqui prevê proibição, saída de mercado ou risco comercial de qualquer substância — os documentos listam o que está admitido em 2026 e sob quais condições, e é só isso que está relatado.