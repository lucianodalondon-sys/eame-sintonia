# RELATÓRIO DO CRÍTICO — RODADA NOTURNA DE COLETA GRATUITA
**Data da rodada:** 02/09/2026 · **IP de saída conferido antes de qualquer conclusão de bloqueio (Lei 2):** `179.172.231.127`, AS26599 Telefônica Brasil (Vivo), linha residencial, Brasil · **País-alvo:** Itália

---

## 0 · AVISO DO CRÍTICO — o que eu conferi no disco antes de escrever

Não aceitei nenhum boletim só porque o coletor disse que leu. Fui ao disco. Três coisas mudam como o resto deve ser lido:

**(a) Uma região inteira foi coletada e NÃO chegou nos boletins que me entregaram.** Há 7 PDFs de boletins do **Friuli-Venezia Giulia (ERSA)** em `C:\eame-sintonia\.tmp\pdf\`, todos com fenologia declarada, seis deles de agosto de 2026. **Eu mesmo os abri e li nesta revisão** — eles entram neste relatório. Sem essa conferência, o pacote perderia a região com a fenologia mais detalhada (BBCH por espécie, semana de levantamento declarada).

**(b) A prova documental de duas coletas não está preservada.** Os 13 PDFs da Emilia-Romagna e os 7 do Piemonte **não estão no disco**. Da Emilia-Romagna sobrou só `C:\eame-sintonia\.tmp\mo27.txt` — e é a extração **ruim**, aquela que o próprio coletor disse ter descartado: o cabeçalho do arquivo declara `CARACTERES_LIMPOS: 396637` e o texto sai quebrado (`"Regi oneE milia - Rom agna"`), enquanto o boletim reporta 166.658 caracteres via `pdftotext -layout`. Ou seja: **as citações da Emilia-Romagna e do Piemonte não podem ser reconferidas nesta máquina.** Elas entram na tabela marcadas como `NÃO RECONFERÍVEL LOCALMENTE`. Isso não as declara falsas — declara que ninguém aqui pode checá-las sem baixar tudo de novo.

**(c) Um arquivo de prova citado no teste de rota não existe.** O teste diz: *"Arquivos de prova salvos: `.tmp\rota\ismea.html` … `.tmp\rota\datiistat.html`"*. Só o primeiro existe (7.891 bytes — bate exato com o declarado). `datiistat.html` **não está lá**. O veredito do teste de rota não depende dele (a prova forte é o check-host.net de fora), mas a lista de arquivos está errada e precisa ser corrigida.

**(d) Detalhe de forma que atrapalha a Lei 5:** as citações italianas que chegaram da Emilia-Romagna e do Piemonte vieram **sem acento** (`"seconda meta di agosto"`, `"non e piu' sensibile"`). Isso é transliteração, não o texto do documento. As citações do FVG e da Lombardia neste relatório saem **com o acento original**, porque eu extraí com `pdftotext -layout -enc UTF-8` a partir do PDF que está no disco.

---

## 1 · FENOLOGIA CORRENTE — a tabela que o pacote não tinha

O pacote declarava `REAL_CURRENT_PHENOLOGY_SIGNALS` = **0** (`00-START-HERE/REALITY-COUNTS.md`). Depois desta rodada há **20 documentos de campo datados de 01/08/2026 ou depois**, cobrindo **4 das 20 regiões italianas**. Um único documento é de setembro: o Modena n.28 de 01/09/2026.

Ordenada da data mais recente para a mais antiga. `Fase` é o que o documento **escreve**, não o que eu interpreto.

| Data do boletim | Cultura | Região / unidade | Fase fenológica declarada (literal) | Boletim | Fonte | Estado da prova |
|---|---|---|---|---|---|---|
| **2026-09-01** | Vite · Pero · Pesco | Emilia-Romagna / **Modena** | «maturazione» nas três | n. 28/2026 | Reg. E-R, Settore Fitosanitario | ⚠️ não reconferível localmente |
| 2026-09-01 | Melo | E-R / Modena | «accrescimento frutti-maturazione» | n. 28/2026 | idem | ⚠️ idem |
| 2026-09-01 | Susino | E-R / Modena | «ingrossamento frutti-maturazione» | n. 28/2026 | idem | ⚠️ idem |
| 2026-09-01 | Kaki · Olivo | E-R / Modena | «accrescimento frutti» · «accrescimento frutto» | n. 28/2026 | idem | ⚠️ idem |
| 2026-09-01 | Barbabietola da zucchero | E-R / Modena | «accrescimento fittone-maturazione» | n. 28/2026 | idem | ⚠️ idem |
| 2026-09-01 | Soia | E-R / Modena | «riempimento semi» | n. 28/2026 | idem | ⚠️ idem |
| 2026-09-01 | Pomodoro da industria | E-R / Modena | «accrescimento- maturazione» | n. 28/2026 | idem | ⚠️ idem |
| **2026-08-28** (capa; listado 01/09) | Mais | **Piemonte** (regional) | colheita iniciada: «hanno avuto inizio le operazioni di raccolta dei primi appezzamenti di mais in asciutta» | Seminativi n. 12/2026 | Reg. Piemonte, Settore Fitosanitario | ⚠️ não reconferível localmente |
| 2026-08-28 (capa; listado 01/09) | Riso | Piemonte (regional) | «I risi si trovano mediamente in fase di maturazione, con le varietà più precoci e seminate presto, prossime alla trebbiatura» | Seminativi n. 12/2026 | idem | ⚠️ idem |
| **2026-08-28** | Actinidia *deliciosa* cv. HAYWARD | **Friuli-Venezia Giulia** | «in fase di accrescimento dei frutti (80% della grandezza finale)» — levantamento da 35ª semana, 24–30/08 | Actinidia n. 12 | ERSA FVG | ✅ PDF no disco |
| 2026-08-28 | Actinidia *chinensis* SORELI · RED · GOLD PASSION | FVG | «accrescimento dei frutti (90% della grandezza finale)» | Actinidia n. 12 | ERSA FVG | ✅ PDF no disco |
| **2026-08-28** | Melo | FVG | «Prosegue l'ingrossamento dei frutti delle varietà medio-tardive. Si sta ultimando la raccolta della varietà Gala» | Melo n. 25 | ERSA FVG | ✅ PDF no disco |
| **2026-08-27** | Pomodoro da mensa (protegido) | FVG | «primo ciclo - fine raccolto, secondo ciclo -inizio raccolta, terzo ciclo -trapianto» | Ortive 27/08 | ERSA FVG | ✅ PDF no disco |
| 2026-08-27 | Pomodoro pieno campo (da industria Nord) | FVG | «ingrossamento frutti sui palchi basali- raccolta» | Ortive 27/08 | ERSA FVG | ✅ PDF no disco |
| 2026-08-27 | Zucchino | FVG | «trapianti estivi /accrescimento frutto – raccolta» | Ortive 27/08 | ERSA FVG | ✅ PDF no disco |
| 2026-08-27 | Fragola | FVG | «inizio dei trapianti sia in pieno campo che tunnel» | Ortive 27/08 | ERSA FVG | ✅ PDF no disco |
| **2026-08-25** | Drupacee (albicocco, ciliegio, pesco, susino) | FVG | BBCH **89 · 89 · 87 · 87**, com os rótulos «Terminata la raccolta» e «Raccolta» — ⚠️ ver ressalva abaixo | Drupacee n. 19 | ERSA FVG | ✅ PDF no disco |
| **2026-08-25** | Patata | FVG | «La coltura è in fase di senescenza o è stata già raccolta.» | Patata 25/08 | ERSA FVG | ✅ PDF no disco |
| **2026-08-21** | Vite | E-R / **Piacenza** | «maturazione - raccolta» + «In corso la raccolta delle uve bianche con raggiungimento del 50% circa delle superfici. Iniziata in settimana anche la raccolta delle uve rosse.» | n. 27/2026 | Reg. E-R | ⚠️ não reconferível |
| 2026-08-21 | Vite | E-R / **Parma** | «maturazione - raccolta» + «In corso la raccolta delle uve bianche.» | n. 27/2026 | Reg. E-R | ⚠️ não reconferível |
| **2026-08-20** | Vite | E-R / **Reggio Emilia** | «maturazione» — sem menção de colheita | n. 27/2026 | Reg. E-R | ⚠️ não reconferível |
| **2026-08-19** | Vite | E-R / **Bologna e Ferrara** | «maturazione-raccolta» | n. 27/2026 | Reg. E-R | ⚠️ não reconferível |
| 2026-08-19 | Vite | E-R / **Forlì-Cesena, Ravenna, Rimini** | «maturazione» | n. 27/2026 | Reg. E-R | ⚠️ não reconferível |
| 2026-08-19 | Noce | E-R / Bologna-Ferrara e Romagna | «maturazione gheriglio» | n. 27/2026 | Reg. E-R | ⚠️ não reconferível |
| **2026-08-18** | Vite | E-R / Modena | «maturazione» | n. 27/2026 | Reg. E-R | ⚠️ não reconferível |
| **2026-08-12** | Mais | **FVG** | «maturazione lattea – maturazione fisiologica … (scala BBCH 65-75). In alcuni comprensori non irrigui sono già iniziate le raccolte.» ⚠️ ver ressalva | Colture erbacee n. 15 | ERSA FVG | ✅ PDF no disco |
| **2026-08-07** | Vite | E-R / Parma e Piacenza | «da invaiatura a maturazione» + «Iniziata la raccolta delle varietà base spumante.» | n. 26/2026 | Reg. E-R | ⚠️ não reconferível |
| **2026-08-06** | Vite | E-R / Reggio Emilia | «invaiatura» | n. 26/2026 | Reg. E-R | ⚠️ não reconferível |
| **2026-08-05** | Vite | E-R / Bologna-Ferrara e Romagna | «invaiatura» · «da invaiatura a maturazione» | n. 26/2026 | Reg. E-R | ⚠️ não reconferível |
| **2026-08-04** | Vite · Mais | E-R / Modena | «invaiatura» · Mais «maturazione cerosa» | n. 26/2026 | Reg. E-R | ⚠️ não reconferível |
| **2026-07-31** | Vite | **FVG** | «Nell'ultima settimana si è registrato un buon avanzamento della maturazione favorito dalle forti escursioni termiche» | Vite n. 33 | ERSA FVG | ✅ PDF no disco |
| **2026-07-31** | Vite | **Lombardia** | bacca bianca p/ espumante **BBCH 85**, ~13 °Babo; bacca rossa **BBCH 83-85** (precoces e áreas quentes) e **BBCH 81-83** (tardias e montanhas) | LA VITE n. 6 | Reg. Lombardia, DGR XI-5836 | ✅ PDF no disco |
| **2026-07-24** | Vite | **Piemonte** | «inizio invaiatura» — **é a edição mais nova da série Vite do Piemonte na bacheca em 02/09/2026** | Vite n. 13 | Reg. Piemonte | ⚠️ não reconferível |
| **2026-07-06** | Melo | **Lombardia** | «in tutti i meleti ci si trova nelle fasi **BBCH 75-77** "accrescimento frutti"» | IL MELO n. 4 | Reg. Lombardia | ✅ PDF no disco |

### Ressalvas de leitura que não podem sumir

- **Drupacee FVG (25/08):** a tabela do PDF sai com as colunas embaralhadas na extração (`SPECIE / BBCH / FASE FENOLOGICA / BAGGIOLINI` intercalados). Os códigos BBCH **89, 89, 87, 87** e os rótulos «Terminata la raccolta» e «Raccolta» estão no documento, mas **a amarração exata de cada rótulo à sua espécie não é segura** nesta extração. Trate como indicativa até alguém abrir o PDF visualmente.
- **Mais FVG (12/08):** o boletim escreve «maturazione lattea – maturazione fisiologica» e, na mesma frase, «(scala BBCH 65-75)`». **A faixa BBCH impressa não corresponde à descrição verbal** (BBCH 65 é floração). Copiei literalmente e registro a inconsistência; **não corrigi o documento**.
- **Emilia-Romagna, 6 unidades territoriais discordam na mesma semana.** Em 19–21/08 a vinha estava em «maturazione - raccolta» com colheita em curso em Parma e Piacenza, e só «maturazione», sem colheita, em Modena e Reggio Emilia. **Lei 4:** uma província não é a região.
- **Número de edição não é semana do ano.** O n.27 tem quatro datas conforme a unidade (18, 19, 20 e 21/08) e houve salto no Ferragosto em Parma e Piacenza: de 07/08 (n.26) direto para 21/08 (n.27), sem edição em 14/08.

### As regiões que NÃO entregaram — elas ficam na tabela, com estado

| Região | Estado | Motivo, literal ou medido |
|---|---|---|
| **Veneto** | `ROTA_INSTAVEL_DAQUI` | `www.regione.veneto.it`: **500** uma vez (corpo real, 49.688 bytes) e **000** cinco vezes. De fora responde 200 (Chipre, Cazaquistão, Turquia). O site está no ar; **a rota daqui não fecha** |
| **Toscana** | `ALCANCADA_SEM_CONTEUDO` | `agroambiente.info.regione.toscana.it` respondeu, mas o que ficou no disco (`.tmp\agro_boll.html`, 17.804 bytes) é **só a casca do Drupal**: "Home · Dati · Bollettini · Modelli · Diagnosi · Irrigazione". Zero boletim. Conteúdo montado por JavaScript, não capturado |
| **Trentino-Alto Adige** (prov. Trento) | `REGULATORIO_LIDO_CAMPO_NAO_LIDO` | ato (det. 5573 de 27/05/2026) e boletim especial de FD (29/05/2026) lidos na fonte. **Nenhuma fenologia de agosto/setembro** |
| **Lombardia** | `SERIE_PAROU_EM_JULHO` | a listagem salva (`.tmp\lomb\boll.html`) mostra, em 02/09/2026, **"Bollettino n 6 del 31 luglio 2026"** (vite) e **"n. 4 del 6 luglio 2026"** (melo) como os mais recentes. Não achei edição de agosto **nessa listagem** — não afirmo que não exista |
| **as outras 12 regiões** (Piemonte, E-R, FVG, Lombardia são as 4 lidas; Veneto, Toscana e Trentino têm estado acima) | `NAO_VARRIDA` | não foram tentadas nesta rodada |

---

## 2 · AVVERSITÀ CORRENTES — o que os boletins de agosto/setembro dizem estar acontecendo

Só documentos de 01/08/2026 em diante. Cada linha traz a frase que a sustenta.

### VITE

| Região / unidade | Data | Avversità | Citação literal |
|---|---|---|---|
| E-R / Modena | 01/09 | Flavescenza dorata | indicação de inspecionar e arrancar plantas sintomáticas «conforme a Determinazione n. 9818 de 20/05/2026» ⚠️ (paráfrase que chegou do coletor, não citação) |
| E-R / **Pero**, Modena | 01/09 | Maculatura bruna | «I modelli segnalano che a partire dal 22 di agosto in tutta la provincia il rischio di sporulazione e il rischio infettivo si sono portati su livelli elevati fino alla fine di agosto.» |
| E-R / Reggio Emilia | 20/08 | Flavescenza dorata | «Flavescenza dorata : presenza di sintomi in campo. Si raccomanda di ispezionare attentamente i vigneti e di procedere all'estirpo delle piante sintomatiche.» |
| E-R / Bologna-Ferrara | 19/08 | Mal dell'esca | «Mal dell'esca : in progressivo aumento le piante con sintomi.» |
| E-R / Modena | 18/08 | Mal dell'esca | «Mal dell'esca : aumento sintomatologia in campo.» |
| E-R / Modena | 18/08 | Peronospora | «Peronospora: da questa fase il grappolo non e piu' sensibile alla malattia.» |
| E-R / Romagna | 19/08 | Peronospora | «da questa fase visto l'esaurirsi della recettivita del grappolo si consiglia di mantenere le coperture con Prodotti rameici solo sugli impianti in allevamento.» |
| **FVG** | 31/07 ⚠️ julho | Tignoletta (*Lobesia botrana*) | «Tra lo scorso fine settimana e l'inizio della corrente si è registrato l'inizio del **III volo** della Tignoletta nella media bassa pianura. Nell'alta pianura le prime catture sono state rilevate mercoledì e ieri.» |
| FVG | 31/07 ⚠️ julho | *Planococcus ficus* (cocciniglia) | «questa settimana nelle zone della bassa pianura si sono riscontrate le prime neanidi di cocciniglia di **III generazione**.» |
| FVG | 31/07 ⚠️ julho | Botrite e marciume acido | «Al momento, grazie all'andamento meteorologico, **non si segnalano infezioni** sia di botrite che di marciume acido.» |

⚠️ **Não há boletim de vite de agosto no FVG nem na Lombardia no que foi coletado.** O sinal de vite de agosto vem só da Emilia-Romagna e do Piemonte.

### MELO / POMACEE

| Região | Data | Avversità | Citação literal |
|---|---|---|---|
| FVG | 28/08 | Carpocapsa (*Cydia pomonella*) | «Presenza di volo con catture in aumento in alcune località.» |
| FVG | 28/08 | Cimice marmorata asiatica (*Halyomorpha halys*) | «Dal monitoraggio delle trappole si rileva una **riduzione** delle catture di cimice.» |
| FVG | 28/08 | Ticchiolatura | «Si continua a rilevare una bassa sintomatologia negli impianti» ⚠️ frase remontada — a extração embaralha as colunas da tabela; conferir no PDF |
| FVG | 28/08 | Dano abiótico | «non ha raggiunto un'ottimale colorazione della buccia a causa delle condizioni climatiche che hanno causato anche importanti cascole e, a seguito delle piogge della scorsa settimana, significativi **danni da spaccature**.» (Gala) |
| E-R / Modena | 01/09 e 18/08 | Colpo di fuoco, glomerella, marciumi (*Neofabrea vagabunda*) | listados na «Parte Specifica» ⚠️ não reconferível localmente |

### ACTINIDIA — FVG, 28/08

- Cimice asiatica: «Il caldo di agosto sembra aver ostacolato la presenza di adulti nei frutteti tuttavia negli ultimi giorni con l'abbassamento delle temperature ed il ritorno delle piogge la presenza di adulti nei frutteti è **aumentata** e si sono riscontrate anche ovature e forme giovanili»
- PSA (*Pseudomonas syringae* pv. *actinidiae*): «In questa fase fenologica non si prevedono interventi specifici contro questo patogeno tuttavia in caso di precipitazioni impetuose abbinate a forte vento o eventi grandinigeni è opportuno intervenire con formulati a base di rame o propoli»

### PATATA — FVG, 25/08

> «Le varietà tardive ancora in fase di raccolta presentano un'incidenza maggiore dei danni da **elateridi e marciumi**, localmente possono essere elevati (alcuni casi isolati presentano uno scarto che può arrivare al 50 % in parte mitigato dall'incremento della resa).»

⚠️ **O documento usa a palavra "incidenza" e o número "50 %".** É o técnico descrevendo casos isolados, **sem denominador**: não diz em quantos talhões, nem em que área. Não converta isso em taxa. (Lei 3 e Lei 6.)

### ORTIVE — FVG, 27/08

- Cavoli / peronospora: «Le precipitazioni degli ultimi giorni, associate all'elevata bagnatura della vegetazione, hanno determinato condizioni favorevoli all'avvio delle **prime infezioni di peronospora**, soprattutto sulle piante trapiantate nel mese di luglio.»
- Pomodoro pieno campo: «In generale si riscontra un **anticipo della maturazione** della coltura di circa 15 giorni»
- Cimice verde: «Dai monitoraggi si rileva la presenza di adulti e neanidi e sono visibili le **prime punture trofiche sulle bacche**.»
- Pomodoro protegido / peronospora: «Nelle attuali condizioni climatiche l'insorgenza della malattia è **poco probabile**.»

### MAIS

| Região | Data | Avversità | Citação literal |
|---|---|---|---|
| **Piemonte** | 28/08 | Aflatossinas / micotoxinas | risco declarado médio-alto; «dovrà essere attentamente monitorato durante le operazioni di raccolta e conferimento, considerato il quadro termico particolarmente favorevole allo sviluppo di condizioni predisponenti alla contaminazione da micotossine» ⚠️ não reconferível |
| Piemonte | 28/08 | Estresse hídrico (abiótico) | citado como dano grave «na área della Baraggia» ⚠️ paráfrase do coletor |
| **FVG** | 12/08 | Piralide, 3ª geração | «sia iniziato il volo degli adulti di terza generazione … Nonostante le popolazioni siano più numerose delle precedenti, **non sono in grado di causare danni alla coltura** in quanto le spighe sono per lo più in fase di maturazione avanzata. Fanno eccezione gli appezzamenti seminati tardivamente (giugno) e il mais di secondo raccolto.» |
| FVG | 12/08 | Piralide — **limiar com denominador** | «Qualora si osservassero ovature superiori a **3 ogni 100 piante** e/o presenza di larve superiore al **30-40% su almeno 50-100 spighe osservate**, è giustificato il trattamento stesso.» |

### RISO — Piemonte, 28/08
Brusone tardivo e mal del collo citados; antecipação da maturação estimada **pelo próprio boletim** em cerca de duas semanas em relação à norma. ⚠️ não reconferível localmente.

---

## 3 · O QUE MUDA NO PACOTE — lacuna por lacuna

Referência: `C:\eame-sintonia\build\SINTONIA-ITALY-PILOT-REALITY-HANDOFF\05-GAPS-AND-LIMITS\KNOWN-GAPS.md`.

| # | Lacuna | Antes | Agora | Veredito |
|---|---|---|---|---|
| **1** | Não há fenologia corrente | `NOT_COLLECTED` · **0 sinais** | **20 documentos** de campo datados de 01/08 em diante, em **4 de 20 regiões**; **1 documento de setembro** (Modena n.28, 01/09) | 🟡 **MUITO REDUZIDA, não fechada** |
| **2** | ISMEA e ISTAT fechadas | ISMEA `BLOCKED`; ISTAT em **`CONFLITO`** (mapeador GREEN × refutador timeout) | ISTAT: **conflito resolvido** — 9 timeouts em 9, `time_connect=0.000`, e o check-host mostra 302 **até de outro IP brasileiro**. Não é bloqueio de país: **é esta linha** | 🟡 **DIAGNOSTICADA** (o estado deixa de ser conflito) |
| **3** | Portas de escuta social | 6 portas `SEM PORTA` | Nenhuma foi aberta. O que houve foi **levantamento de ferramenta**: `.tmp\apify\` traz catálogo de atores do Apify com preço e taxa de sucesso — **zero post italiano coletado** | 🔴 **CONTINUA ABERTA, INTEIRA** |
| **4** | Cobertura de rótulo (19/163 = 11,7%) | 11,7% | Não tocada. Os boletins trazem muita substância ativa, mas isso é **disciplinare e recomendação**, não linha de rótulo | 🔴 **ABERTA** |
| **5** | Colisão cultura × alvo (7 gêneros) | suspeita registrada | Não tocada | 🔴 **ABERTA** |
| **6** | Regiões fracas — as 3 maiores de milho (Veneto, Lombardia, Piemonte = 71,6% da área) sem boletim de milho | 0 de 3 | **Piemonte agora tem** (Seminativi n.12, 28/08). FVG também (n.15, 12/08), mas FVG não estava nas três | 🟡 **REDUZIDA: 1 de 3** |
| **7** | Séries de preço mortas | azeite Salerno parado em 2015; vinho parado desde jul/2025 | **Rota italiana viva encontrada e não reportada:** `.tmp\riso\vercelli_01set2026.pdf` é o listino semanal da Camera di Commercio di Vercelli, **«Martedì, 01 settembre 2026»**, com duas semanas comparáveis lado a lado (25.08 e 01.09). **Não extraí nenhum valor** | 🟡 **PISTA NOVA, não medida** |
| **8** | Dado interno ADAMA | `INTERNAL_DATA_REQUIRED` | Nada muda, e nada pode mudar por rota pública | 🔴 **ABERTA por definição** |
| **9** | Nível 2 do sinal exige duas janelas | `NAO_MEDIDO` | Continua. Os boletins dão n.26 → n.27 → n.28, o que é **evolução dentro de uma fonte**, e não a proporção entre duas janelas comparáveis do corpus | 🔴 **ABERTA** |
| **10a** | 22 mapas GIRE não lidos | a um passo | **FECHADA.** Os 22 abertos, com a causa achada: o link do site aponta para `cl2.agriserv.org`, e **`agriserv.org` inteiro está em NXDOMAIN** (Status 3 autoritativo do TLD, confirmado por 5 resolvedores). A mesma aplicação vive em `agrovoltaico.org`. Dados preservados em `C:\eame-sintonia\.tmp\gire_mapas.json` (22 entradas, conferido) | ✅ **FECHADA** |
| **10b** | Atos europeus lidos por título | 15 na íntegra | **+15 lidos na íntegra**, textos em `C:\eame-sintonia\.tmp\atos2026\`. ⚠️ **O denominador mudou**: o perímetro agora é `scripts/cellar.sh substances 2026` = 20 atos, não os "31" antigos. Não são a mesma conta | 🟡 **REDUZIDA, com denominador trocado** |
| **10c** | Trentino e E-R só por fonte secundária | `CITADO_EM_FONTE_SECUNDARIA` | **FECHADA.** Os dois atos lidos na fonte, PDFs preservados em `C:\eame-sintonia\data\raw\IT\TRENTINO-FD\` e `...\EMILIA-ROMAGNA-FD\`. E uma correção de fundo: **o Bollettino speciale de 29/05 não era o ato** — o ato é a det. 5573 de 27/05 | ✅ **FECHADA + CORREÇÃO** |
| **10d** | 8 comunicados de Modena não abertos | a um passo | **FECHADA.** 8 de 8 abertos, mais 2 PDFs e 3 PNGs em `C:\eame-sintonia\.tmp\modena\` | ✅ **FECHADA** |
| **10e** | Catálogo ADAMA 2026 em PDF (WAF recusa curl) | a um passo | Não tocado nesta rodada | 🔴 **ABERTA** |
| **10f** | 29 eventos «ADAMA in campo», 13 no pacote | a um passo | Não tocado | 🔴 **ABERTA** |

**Lacuna nova, que este relatório abre:** `PROVA_NAO_PRESERVADA`. Duas das quatro coletas de fenologia (Emilia-Romagna e Piemonte) não deixaram arquivo reconferível no disco. Isso precisa entrar no KNOWN-GAPS antes de o pacote ir a qualquer lugar.

---

## 4 · ROTA ISMEA / ISTAT — o veredito, em uma frase

> **O Market Pulse italiano NÃO PODE ter camada ISMEA-ISTAT nativa a partir deste ambiente, e o motivo é X = o IP de saída `179.172.231.127` (Vivo residencial, Brasil) — a ISMEA o rejeita por geografia com `GEO_IP_BLOCK` do Barracuda (a mesma URL devolve 301 normal de Milão, Berlim, Helsinque e Miami, e 404 de Vancouver, igual ao meu), e `esploradati.istat.it`, para onde a ISTAT migrou todo o I.Stat inclusive a API SDMX, não fecha sequer o handshake TCP desta linha em 9 de 9 tentativas embora responda 302 até de outro IP brasileiro — logo é rota, não país; PODE, porém, ter três camadas substitutas alcançadas hoje sem VPN e sem credencial: Eurostat (produção vegetal nacional e por região NUTS-2, com Veneto = ITH3, e venda de defensivos, todos HTTP 200 e com data de atualização em 2026), os boletins fitossanitários regionais (que são o que sustenta a seção 1 deste relatório) e as bolsas de mercadoria locais (listino de Vercelli de 01/09/2026), nenhuma das quais é o mesmo produto que a ISMEA ou o I.Stat.**

Três notas que não podem cair:

1. **Fonte não alcançada não é fonte vazia.** A ISMEA e a ISTAT estão no ar e respondem para outros. Nada aqui autoriza dizer que "não têm dado".
2. **Armadilha do Wayback:** snapshots da ISMEA de 2026 com HTTP 200 e 1.199–1.409 bytes compartilham o digest `6L6WTIRHHRSUXLA6ELGBZJ5ESTT3NN4C` entre HTML, JS e PDF, e um deles contém `captcha` 3×. **O arquivo capturou a página de bloqueio.** Quem contar isso como "página recuperada" está contando bloqueio como dado.
3. **A ISMEA reaparece por dentro.** O boletim de ortive do FVG (27/08/2026) manda o produtor à «Banca dati delle norme di produzione integrata-**ISMEA**» seis vezes, para cavoli, pomodoro e radicchio. Ou seja: **a base nacional do que é permitido em produção integrada mora na ISMEA** — e é justamente o que não abre daqui.

---

## 5 · NOVOS FATOS REGULATÓRIOS

### 5.1 União Europeia — 15 atos lidos na íntegra (perímetro 2026: 20)

**Renovações, com a data velha e a nova lado a lado — para não colar uma na outra:**

| Substância | Ato | Expiração ANTIGA | Expiração NOVA | Linha no Anexo do 540/2011 |
|---|---|---|---|---|
| ácido pelargônico | 2026/1696 | 1 Dec 2026 | **30 Sep 2041** | Parte B, entrada **181** (nova) |
| pirimetanil | 2026/355 | 30 Jun 2026 | **30 Apr 2041** | Parte A 135 apagada → Parte B **179** |
| espinosade | 2026/351 | 31 Oct 2026 | **1 Apr 2041** | Parte A 139 apagada → Parte B **177** |
| maltodextrina | 2026/312 | 28 Feb 2027 | **3 Mar 2041** | Parte B 44 apagada → Parte D **57** |
| **bixlozona** (1ª aprovação, FMC) | 2026/747 | não existe | **21 Apr 2036** | Parte B **178** (nova) |
| hidrazida maleica | 2026/321 | 31 Oct 2032 | **31 Oct 2032 — NÃO MUDA** (muda só condições) | Parte B, linha 117 |

**Supressões — 2026/1154:** metoxifenozida (Parte E, entrada 11), pentiopirade (Parte B, 57) e terpenoid blend QRD 460 (Parte B, 84) **saem da lista**. Motivo, literal: *"no applications for renewal were submitted or applications were submitted but withdrawn"*. **O ato não informa as datas antigas de expiração dessas três** — isso vai para o "não sei".

**Biocidas (Reg. 528/2012, regime diferente, não mexe no 540/2011):** DBNPA aprovado para PT 11, **01/07/2027 a 30/06/2032**, com a razão dos cinco anos escrita no texto — *"is considered as having endocrine-disrupting properties … and thus it is also a candidate for substitution"*; formaldeído RP 1:1 e RP 3:2, ambos **01/06/2027 a 31/05/2032**; dióxido de carbono (Reg. Delegado 2026/447) muda **restrição de uso**, sem data, Anexo I Categoria 6, EC 204-696-9.

**Duas armadilhas registradas:**
- O 2026/1696 também reescreve a **entrada 230, "Fatty acids C7 to C20"**, que **continua com 1 Dec 2026**. São duas linhas diferentes na mesma tabela. Colar 30 Sep 2041 nos ácidos graxos, ou 1 Dec 2026 no ácido pelargônico, é o erro fácil aqui.
- A retificação **2026/1154R(01)** corrige a data de adoção de 29 para **28 May 2026** — mas **o texto consolidado que o CELLAR devolve ainda traz "29 May 2026"**. Quem ler o consolidado lê a data errada.

**Teste de consistência que dá confiança à leitura:** a Parte B recebeu em 2026 as entradas **177 espinosade · 178 bixlozona · 179 pirimetanil · 180 óleo de parafina · 181 ácido pelargônico**. A 180 vem do 2026/870, lido na rodada anterior. **A sequência fecha sem buraco** — nenhum número foi trocado com o do vizinho.

### 5.2 Itália — Flavescenza dorata: os dois atos agora lidos na fonte

| | **Trentino** | **Emilia-Romagna** |
|---|---|---|
| Ato | det. Servizio Agricoltura **n. 5573 de 27/05/2026** | det. Settore Fitosanitario **n. 9818 de 20/05/2026** |
| Publicação | Albi Pretori dos comuni | **BURERT n. 139 de 03/06/2026** |
| Revoga | det. 4769 de 12/05/2025 | det. 9016 de 14/05/2025 |
| Regra de admissão de produto | «prodotti fitosanitari registrati per l'impiego contro **Scaphoideus titanus o le cicaline della vite**» | «prodotti fitosanitari autorizzati sulla vite contro **Scaphoideus titanus o cicaline in genere**» |
| Onde estão datas e substâncias | **fora do ato**, no Bollettino speciale FD (FEM/CTT) | **fora do ato**, nos Bollettini territoriais e em 3 schede regionais |

**A correção de fundo:** no Trentino o acervo tinha registrado o *boletim* como o ato. Ele não é. O próprio boletim diz: *"Il 27 maggio 2026 il Dirigente del Servizio Agricoltura … con la determinazione n. 5573 ha emanato le direttive"*. Os dois documentos **só funcionam juntos**.

**Nenhuma das duas regiões publica lista fechada de substância no ato** — as duas amarram no rótulo. E a fórmula **não é igual**: «le cicaline della vite» (Trentino) restringe à videira; «cicaline in genere» (Emilia-Romagna) não restringe. **O que essa diferença significa na prática de registro eu não sei** — o texto não define o termo.

Substâncias nomeadas (nos boletins/schede, **não** nos atos):
- **Trentino** — lista fechada e nominal: 1º tratamento **acetamiprid** ou **flupyradifurone** ou **piretro**; 2º **etofenprox**. Bio: piretro nas duas. Restrições literais de faixa de respeito e captação de água. **Tau-fluvalinate não aparece.**
- **Emilia-Romagna** — janela **03 a 13/06/2026** (integrada química, sistêmicos: acetamiprid, flupiradifurone, sulfoxaflor) e **03 a 10/06/2026** (com bio); 2º ou 3º golpe com piretroides nomeados: **deltametrina, etofenprox, lambdacialotrina, esfenvalerate, tau-fluvalinate**.
- Aviso: *"Evitare di miscelare Flupyradifurone con Dithianon per possibili danni da fitotossicità."* (Trentino)

### 5.3 Autorização de emergência com produto comercial nomeado — e ela vence amanhã

Nota Técnica n.2 do Settore Fitosanitario da Regione Emilia-Romagna (05/06/2026), retransmitida por Modena:

> «si ricorda che, con Decreto Dirigenziale del 7 maggio 2026, è stato autorizzato l'uso in emergenza del formulato **LASER 120 SC (Spinosad)** su erba medica, trifoglio e leguminose foraggere, contro la cavalletta crociata (*Dociostaurus maroccanus*) e la Cavalletta italiana (*Calliptamus italicus*), per un periodo di **120 giorni (7 maggio - 3 settembre 2026)**.»
> «Tale formulato è impiegabile anche per le aziende che seguono i disciplinari di produzione integrata della Regione Emilia-Romagna (deroga Prot. 22/05/2026.0526372.U).»

**A janela fecha em 03/09/2026 — amanhã.** Este é o único produto de marca comercial nomeado em todo o material desta rodada.

### 5.4 Fronteira regulatória entre regiões — fato novo, do FVG

O boletim de ortive do FVG (27/08/2026) declara, para **pomodoro** e para **radicchio**:

> «Si ricorda che la regione Friuli Venezia Giulia **NON HA UNA SCHEDA COLTURALE** per cui può essere adottata la corrispondente parte del disciplinare della **Regione confinante (VENETO)** previa comunicazione all'indirizzo PEC di ERSA FVG»

Uma região manda o produtor usar o disciplinare de outra. **Isso desmonta qualquer régua que trate "região" como caixa fechada.**

### 5.5 GIRE — a base nacional de resistência é qualitativa por decisão, e parou em 2022

> «La missione del GIRE non é quella di fornire il numero di popolazioni resistenti, ma dare un'indicazione delle aree interessate … Le mappe, pertanto, **non forniscono indicazioni quantitative ma qualitative**, cioé il territorio di un comune é colorato quando é stata confermata la presenza di una popolazione resistente ad almeno un erbicida.»

Data declarada da aplicação: **"Ultimo aggiornamento in data 30/10/2022"**. O campo `numerosita` existe no GML mas **está desligado na interface** — a linha que mostraria "casi osservati" está comentada no `map4agriinfest3.js`. **Recomendo não usar `numerosita` como número**: rótulo em código morto, sem definição publicada e sem período de referência.

E há um mapa que volta **válido e vazio** (Echinochloa / Riso / Propanile, grupo C2): GML de 494 bytes, bounding box `0,0`, legenda em branco. **Isso é um ESTADO, não um zero.** Não sei se a base não tem registro ou se a consulta está quebrada.

---

## 6 · O QUE CONTINUA NÃO SEI

**Sobre fenologia**
1. **Não sei a fenologia de 16 das 20 regiões italianas.** Quatro foram lidas. Doze nem foram tentadas. Veneto e Toscana foram tentadas e não entregaram — cada uma pelo seu motivo, registrado na tabela.
2. **Não sei se existe boletim mais novo do que os que trouxe.** O caso do Modena n.28 é a prova viva: ele existia no portal regional e **ainda não existia** no site do próprio Consorzio de Modena (página no ar, HTTP 200, sem o PDF anexado). Quem só olhasse `fitosanitario.mo.it` concluiria que o n.27 de 18/08 era o mais recente — e erraria.
3. **Não sei se a Lombardia publicou boletim de vite em agosto.** A listagem que li em 02/09 mostra o n.6 de 31/07 como o último. **Não achei ≠ não existe.**
4. **Não sei a fenologia de trigo, cevada, girassol, cítricos, oliveira do Sul, tomate do Sul.** Nenhuma região do Centro-Sul foi varrida. O que existe é do Norte.
5. **Não li os boletins de modelos previsionais da Emilia-Romagna**, que são mais recentes que vários destes: «modelli previsionali patogeni n. 41 del 24 agosto 2026» e «modelli previsionali insetti n. 24 del 27 agosto 2026». Ficam como pista aberta.
6. **Não li a segunda metade dos boletins da Emilia-Romagna**, dedicada à produção **biológica**, com as mesmas culturas e recomendações diferentes.
7. **Não sei o que há nos outros 20 blocos da bacheca do Piemonte.** O relatório que chegou até mim está **truncado no meio de uma citação** («nella ma…») e descreve em detalhe só 2 dos 7 PDFs que diz ter baixado.

**Sobre as fontes fechadas**
8. **Não sei se a ISMEA tem espelho no Eurostat.** Não procurei a fundo.
9. **Não sei se a ISMEA publica em algum outro catálogo.** No `dati.gov.it` a consulta funcionou e devolveu `"count": 0` com organização inexistente sob esse nome. **Fonte alcançada, resultado vazio** — não é o mesmo que "não publica".
10. **Não sei se as rotas 1 a 5 do teste continuam fechadas de outro IP.** Se esta máquina sair por VPN europeia, por runner em nuvem, ou pelo runner local do GitHub em outro link, **tudo tem de ser retestado do zero**.

**Sobre a prova**
11. **Não posso reconferir nenhuma citação da Emilia-Romagna nem do Piemonte.** Os PDFs não estão no disco e as citações chegaram sem acento. Só sei que a extração descartada (`mo27.txt`) bate com o URL e com a data 18/08 declarados.
12. **Não sei ler o gráfico de *Drosophila suzukii* de Modena.** O eixo Y vai de 0,00 a 200,00 e **nada no gráfico diz de quê**. O título diz «triennio 2024-2026» e plota **quatro** séries (2020, 2024, 2025, 2026). Sem unidade e sem tabela por trás, não há número citável.
13. **Não sei o que há dentro do listino de Vercelli de 01/09/2026.** Li só o cabeçalho. Sei que a série está viva e que traz duas semanas comparáveis (25.08 e 01.09).
14. **Não sei a unidade do mapa de capturas de *Popillia japonica* da Lombardia** (`.tmp\lomb\pj2608.pdf`, atualizado 26/08/2026). Os números aparecem ao lado dos nomes de comune sem legenda extraída. Não use.

**Sobre o regulatório**
15. **Não sei as datas antigas de expiração** de metoxifenozida, pentiopirade e terpenoid blend QRD 460. O ato que as apaga não as informa.
16. **Não li o ato da Lombardia sobre flavescenza dorata.** A linha da Lombardia na comparação das três fórmulas de rótulo vem do enunciado do briefing, **usada como dado, não como fonte alcançada**.
17. **Não li as seções normativas dos boletins do FVG:** «AGGIORNAMENTO NORMATIVO - RAME», «AUTORIZZAZIONI ALL'IMPIEGO … EMERGENZA FITOSANITARIA», «DEROGHE AL DISCIPLINARE», «REVOCHE / REVISIONI DEI PRODOTTI». Elas existem, estão nos PDFs no disco, e são exatamente onde moram mudanças de registro.

---

## 7 · AFIRMAÇÕES QUE ESTE MATERIAL NÃO AUTORIZA

1. **Não autoriza afirmar ocorrência, incidência ou severidade de nenhuma doença ou praga.** Quando um boletim escreve «presenza di sintomi in campo», «aumento sintomatologia» ou «in progressivo aumento le piante con sintomi», isso é o técnico do consórcio descrevendo o que viu no território que atende. **Não é área medida, não é porcentagem de plantas, não é número de talhões. Não existe denominador em nenhum destes documentos** — com as duas exceções que eu marquei: o limiar da piralide no FVG («3 ogni 100 piante»; «30-40% su almeno 50-100 spighe») e a colheita de uva branca em Piacenza («50% circa delle superfici»), que são o que são e não valem para outra província nem para outra semana.
2. **Não autoriza afirmar venda, participação de mercado nem demanda por nenhuma substância ativa.** A lista enorme de moléculas (fenhexamid, cyprodinil, fludioxonil, ditianon, captano, spinosad, emamectina, acetamiprid, flupiradifurone, sulfoxaflor, tau-fluvalinate, cobre, *Bacillus subtilis* e dezenas de outras) é o que o disciplinare **autoriza** e o que o boletim **recomenda**. **Não é o que alguém comprou, aplicou ou pagou.** Confundir "permitido" com "usado" é o erro que este acervo já pagou caro uma vez.
3. **Não autoriza afirmar resistência**, com uma única exceção literal e limitada: os boletins da Emilia-Romagna afirmam que boa parte das populações de *Conyza* spp. é resistente ao glifosato. É resistência de uma daninha a um herbicida, dita pelo boletim, e nada mais. **Não há nesta coleta nenhuma afirmação de resistência de fungo ou inseto a fungicida ou inseticida.**
4. **Não autoriza usar o mapa do GIRE como mapa de incidência.** Um comune pintado significa **pelo menos um caso confirmado ali**, por decisão declarada do sistema. Um comune pintado ao lado de um branco **não diz "mais" e "menos"**. E o mapa vazio de Propanile **não é um zero**.
5. **Não autoriza falar pela região a partir de uma província, nem pelo país a partir de uma região (Lei 4).** As 6 unidades da Emilia-Romagna **discordam entre si na mesma semana**: em 19–21/08 a vinha estava sendo colhida em Parma e Piacenza e só em «maturazione» em Modena e Reggio Emilia. E o Norte lido aqui (E-R, Piemonte, FVG, Lombardia) **não fala pela Itália**.
6. **Não autoriza tratar número de edição como semana do ano.** O n.27 tem quatro datas diferentes e houve salto no Ferragosto.
7. **Não autoriza dizer que a ISMEA "não tem dado" ou que a ISTAT "está fora do ar".** As duas estão no ar e respondem para outros IPs. **Fonte não alcançada não é fonte vazia (Lei 1).**
8. **Não autoriza dizer "0 menções no Instagram", "0 no TikTok", "0 no X".** Essas portas nunca foram abertas. Nesta rodada, o que houve foi levantamento de **ferramenta** de coleta, não coleta. `SEM PORTA ≠ RENDEU ZERO`.
9. **Não autoriza contar snapshot do Wayback como página recuperada** sem abrir o corpo. Vários snapshots da ISMEA de 2026, com HTTP 200, são a **página de bloqueio arquivada** — um deles tem `captcha` três vezes.
10. **Não autoriza dizer nada sobre a Regione Veneto além do estado da rota.** Não entrei nela. Não há bloqueio a afirmar nem ausência a declarar.
11. **Não autoriza afirmar nada sobre a ADAMA, sobre concorrentes ou sobre comunicação de mercado a partir dos boletins.** Eles citam substâncias ativas e organismos biológicos. **Nomes comerciais aparecem uma única vez em todo o material**: LASER 120 SC (Spinosad), na autorização de emergência de 120 dias que vence em 03/09/2026 — e isso é um ato administrativo, não um sinal de mercado.
12. **Não autoriza publicar as citações da Emilia-Romagna e do Piemonte como texto literal verificado.** Elas chegaram sem acento e sem arquivo de prova no disco. Antes de irem à tela, precisam ser rebaixadas para o PDF de origem e reextraídas.

---

### Arquivos relevantes, caminhos absolutos

| Caminho | O que é |
|---|---|
| `C:\eame-sintonia\.tmp\pdf\` | **7 boletins do FVG (ERSA)** — vite33, actinidia12, melo25, drupacee19, patata2508, orticolo2708, ersa_mais15. A prova mais sólida da seção 1 |
| `C:\eame-sintonia\.tmp\lomb\vite6.pdf` · `melo4.pdf` · `boll.html` | Lombardia: 2 boletins + a listagem que mostra 31/07 como a última edição de vite |
| `C:\eame-sintonia\.tmp\lomb\pj2608.pdf` | Mapa de capturas de *Popillia japonica*, 26/08/2026 — **sem unidade declarada** |
| `C:\eame-sintonia\.tmp\gire_mapas.json` | 22 mapas do GIRE, conferido: 22 entradas |
| `C:\eame-sintonia\.tmp\atos2026\` | Textos integrais dos atos europeus de 2026 |
| `C:\eame-sintonia\data\raw\IT\TRENTINO-FD\` · `EMILIA-ROMAGNA-FD\` | Atos de flavescenza dorata + 3 schede de substâncias |
| `C:\eame-sintonia\.tmp\modena\` | 2 Notas Técnicas regionais + 3 gráficos de *D. suzukii* |
| `C:\eame-sintonia\.tmp\riso\vercelli_01set2026.pdf` | Listino de preços de Vercelli, **01/09/2026** — série viva, valores não extraídos |
| `C:\eame-sintonia\.tmp\rota\ismea.html` | Corpo do bloqueio da ISMEA, 7.891 bytes — confere com o declarado |
| `C:\eame-sintonia\.tmp\agro_boll.html` | Toscana: só a casca do Drupal, 17.804 bytes, zero boletim |
| `C:\eame-sintonia\.tmp\mo27.txt` | ⚠️ **extração descartada** do Modena n.27 — palavras quebradas. Único resto local da coleta da Emilia-Romagna |
| `C:\eame-sintonia\build\SINTONIA-ITALY-PILOT-REALITY-HANDOFF\05-GAPS-AND-LIMITS\KNOWN-GAPS.md` | O arquivo que a seção 3 audita, e que precisa ser atualizado |