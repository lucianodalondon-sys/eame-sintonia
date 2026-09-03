# MISSÃO — DESCOBERTA DE FONTES · ACERVO PERMANENTE · COLETA DE SINAIS · ITÁLIA

**Data de referência:** 2026-09-03 · **Branch:** `claude/adama-italia-source-discovery-oui6ma`
**Testes:** 329, 0 falhas · **Guardas canônicas:** PASS

---

## 0 · A PRIMEIRA COISA QUE ESTA MISSÃO MEDIU

Antes de procurar uma única fonte nova, li o acervo canônico da Itália e contei o que ele
já observa. O resultado explica a missão inteira:

| camada | o que o acervo canônico tem | o que falta |
|---|---|---|
| regulatório | 163 registros ADAMA, 51 produtos de catálogo, 2.030 pares de rótulo | — |
| campo | 122 `fieldBulletins`, 49 `currentFieldSignals` | **nenhuma série numérica** |
| voz | 79 `publicVoices`, 62 `publicChannels` — **todos YouTube** | **zero Instagram, zero LinkedIn** |
| fontes | 189 `SOURCE`, 121 hosts distintos | Itália forte em oficial, **fraca em voz e em técnico privado** |

E dentro dos 62 canais públicos: uma parte é horticultura doméstica (*Passione Orto*, *Orto
Da Coltivare*, *Piccoli Orti Grandi Raccolti*, *Your Hobby*) e quatro **não são italianos**
(Cornell SIPS, INTA Chubut, Aragón TV, Laderas del Naranco).

> **"62 canais" sugeria 62 canais técnicos italianos. Não era isso.**

---

## 1 · A MATRIZ QUE ORIENTOU A BUSCA

Não veio de conhecimento genérico sobre agricultura italiana. Veio dos 2.030 pares de
rótulo do próprio pacote V2.1 — **35 culturas, 78 alvos canônicos**:

```
BARBABIETOLA 239 · FRUMENTO 176 · MELO 146 · ORZO 131 · MAIS 112 · PATATA 100
BRASSICACEE 100 · VITE 96 · ERBA MEDICA 87 · SEGALE 82 · TRITICALE 71 · LEGUMINOSE 70
CAROTA 63 · CUCURBITACEE 58 · COLZA 56 · FRAGOLA 51 · PESCO 45 · POMODORO 44
CIPOLLA 42 · GIRASOLE 39 · MAIS DOLCE 36 · SOIA 28 · CILIEGIO 27 · TABACCO 26
AGRUMI 17 · ALBICOCCO 16 · RISO 15 · LATTUGA 11 · PERO 11 · ... · OLIVO 1
```

Alvos por peso: `AFIDI 436` · `INFESTANTI 375 não mapeadas` · `TRIPIDI 108` · `NOTTUE 92`
· `OIDIO 37` · `RUGGINE 33` · `PERONOSPORA 27`.

Regiões das 37 oportunidades: Emilia-Romagna · Veneto · Lombardia · Friuli-Venezia Giulia ·
Piemonte · Puglia · Toscana · Sicília · Trentino-Alto Adige.

**A assimetria mais útil da tabela:** OLIVO tem **1** par de rótulo lido e **3**
oportunidades e **5** crop windows. Isso não diz que a ADAMA não tem produto para oliveira.
Diz que **não lemos** — a cobertura de leitura de rótulo é de 102 dos 163 registros (62,6 %).

---

## 2 · SOURCE DISCOVERY

```
SOURCES DISCOVERED   = 128 endpoints sondados com HTTP real
SOURCES QUALIFIED    = 36
HIGH RELEVANCE       = 17
MEDIUM               = 19
REJECTED             = 6   (com motivo escrito)
ROUTES NOT REACHED   = 11  (estado da rede, nunca estado do mundo)
```

**BY AUTHORITY**

```
OFFICIAL = 10 · SCIENTIFIC = 5 · MEDIA = 8 · COMPETITOR = 4
TECHNICAL = 3 · FIELD_VOICE = 3 · INDUSTRY = 3
```

**BY TYPE (leitura da missão)**

```
OFFICIAL / FITOSSANITARIO = 5      AGROMET = 4        SCIENCE / RESEARCHERS = 5
COOPERATIVES = 4                   PRODUCERS / ORGS = 2   TECHNICIANS = 2
MEDIA = 8                          MARKET = 2          COMPETITORS = 4
SOCIAL (perfis declarados) = 34 em 16 organizações
```

**NEW SOURCE REGISTRY**

| | |
|---|---|
| **PATH** | `data/samples/IT-FONTES-V1/IT-FONTES-DESCOBERTA-V1.json` |
| **GERADOR** | `scripts/it_fontes.py` |
| **OWNER** | `docs/fontes/ATLAS-DE-FONTES-EAME.md` — **não foi criado segundo dono** |
| **SOURCE DEDUPE** | **PASS** (sem `SOURCE_ID` nem `PRIMARY_URL` repetidos) |

**Por que os IDs são `IT-SRCX-###` e não `IT-T<n>-<seq>`:** `SOURCE_ID_COUNT` é sentinela do
ledger, verificada por `tests/test_handoff.py` contra **36** e contra o prompt de bootstrap.
Mintar 27 IDs novos moveria essa régua **em silêncio**. O namespace novo não casa com o
regex do ledger. O caminho de promoção está escrito no Atlas.

**AUTOMATION POTENTIAL**

```
AUTOMATABLE = 24 · PARTIAL = 11 · MANUAL = 1 · BLOCKED = 0
DAILY = 6 · WEEKLY = 12 · MONTHLY = 17 · EVENT_DRIVEN = 1
```

### As quatro que mais mudam o que dá para observar

| ID | fonte | por quê |
|---|---|---|
| `IT-SRCX-003` | UNIBO BIG — rede de trappole de *Halyomorpha halys* | **única série numérica de campo** desta rodada: 177 pontos, por província e por estádio, 2021 → 2026-08-31, API aberta sem chave |
| `IT-SRCX-004` | API Plone dos bollettini do Servizio Fitosanitario ER | o host já estava no acervo, a **rota** não. A página é um SPA e não entrega link nenhum; a API entrega os **150 PDFs de 2026** com título e data |
| `IT-SRCX-028` | ARPAE ERG5 — série **horária** por estação | é a entrada dos modelos que decidem *quando* tratar. Sem ela, "janela" é calendário |
| `IT-SRCX-016` | Agricast — podcast dos Gruppi Operativi da ER | fala técnica longa onde o sinal está **só no áudio** |

---

## 3 · SINTONIA SCRAP

Localizei e li o Sintonia Scrap antes de tocar em qualquer coisa:
`scripts/instagram_janela.py` (rota pública pelo navegador), `instagram_coleta.py` (rota
paga Apify), `instagram_transcrever.py` (transcrição **local**), orquestrados por
`.github/workflows/sintonia-scrap.yml`. **Não construí outro scraper.**

```
PROFILES DISCOVERED = 34 perfis declarados por 16 organizações
PROFILES QUALIFIED  = 32 (o lote congelado)

CONTENTS            = 0   ← a rota de Instagram não abre desta sessão
VIDEOS              = 0

VIDEOS TRANSCRIBED  = 9 objetos de ÁUDIO (a rota que abriu)
TRANSCRIPTION SUCCESS = 9 / 9
FAILURES            = 0

VIDEO SIGNALS ONLY IN TRANSCRIPT = 6 de 9 objetos
USEFUL VOICES       = 5
```

### Por que zero conteúdo de Instagram, dito com precisão

`ROTA BLOQUEADA PARA ESTA SESSÃO ≠ ROTA INEXISTENTE.`

- O Chrome do `cdp.py` **não atravessa o proxy** desta sessão: `ERR_CONNECTION_RESET` em
  todo host, `google.com` incluído.
- A página de perfil do Instagram devolveu **HTTP 302** para login nas minhas medições e
  **HTTP 429** em 11 de 12 na passagem paralela — com **um 200 de 625.848 bytes**. A rota
  está limitada por taxa e instável, não fechada.
- A rota de **embed de post** respondeu **HTTP 200 com 628 KB** daqui. Falta o *shortcode*,
  que só a passada de perfil entrega.
- A mídia do YouTube é recusada com **HTTP 403** pela política de saída
  (`googlevideo.com`) — os **metadados** voltam normalmente.

**O entregável é o lote congelado**, em
`data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-IT-SOCIAL-BATCH-V1.json`: 32 contas
(19 Instagram, 8 YouTube, 5 LinkedIn), cada uma com o handle **declarado pela própria
organização no site dela** — nunca achado por busca livre. É a regra que reprovou a coleta
espanhola (`ES-T8-003`: 24 de 32 contas não declaravam país).

### A rota de voz que ABRIU, e o que ela custou

| | |
|---|---|
| objetos | 9 |
| áudio | 7.121 s = **118,7 minutos** |
| transcrito | **103.404 caracteres** de agronomia italiana falada |
| motor | `faster-whisper small`, int8, CPU, `beam=1`, **idioma `it` declarado, nunca detectado** |
| velocidade medida | 8,59× a 10,17× tempo real, nesta máquina de 4 núcleos |
| custo | **0,00 USD** — o custo é tempo de máquina |

**Razão legenda : fala** entre **1:11** e **1:23**.

---

## 4 · COLETA

```
NEW FIELD       = 14 boletins oficiais dos últimos 30 dias, 2,3 M caracteres,
                  421 menções de substância ativa ADAMA verificadas com fronteira de palavra
                + 177 pontos de série numérica de captura de cimice, por província e estádio
NEW VOCI        = 9 objetos de áudio, 103.404 caracteres de fala
NEW COMPETITOR  = 4 canais (FMC Itália, Certis Belchim, Nufarm, Gowan)
NEW MARKET      = 5 feeds datados (Terra e Vita, FruitJournal, VVQ, Rivista Orticoltura,
                  Olivo e Olio, FreshPlaza) — todos com item de hoje ou ontem
NEW REGULATORY  = 6 deroghe regionais com data de concessão, e duas com janela declarada
NEW SCIENCE     = 5 (Laimburg, AIPP, UCSC Piacenza, Ri.Nova, Fondazione Agrion)
NEW RESISTANCE  = o teto de intervenções e as "sostanze candidate alla sostituzione"
                  lidos linha a linha nos boletins
```

### O que NÃO passou, e é o achado mais duro da coleta

Procurei os **177 nomes** de produto do universo ADAMA nos 14 boletins.
Por *substring*, quatro pareciam presentes: `LIGA` (378), `FORZA` (90), `SULTAN` (57),
`CINDER` (17).

Com **fronteira de palavra: zero**. `LIGA` vinha de *obbligatorio*; `FORZA` de *causa di
forza maggiore*.

> **Nenhum dos 51 produtos comerciais ADAMA aparece por nome em nenhum dos 14 documentos.**
> O boletim de *produzione integrata* nomeia **substância ativa**, não marca.

E quatro das nove convergências confirmadas têm a sua substância com **zero ocorrências**
em 2,3 M de caracteres: `fenpropidin`, `bupirimate`, `mesotrione`, `florasulam`.
**Zero nesta leitura. Nunca zero no campo.**

---

## 5 · CRUZAMENTOS

```
NEW CROSSINGS = 5
  por força do elo:  LINHA_DA_TABELA = 2 · SUBSTANCIA_ATIVA = 3
  com evidência que existe SÓ NA FALA = 4 de 5
NÃO CRUZADOS (com o motivo escrito) = 3
```

`data/samples/IT-CRUZAMENTO-V1/IT-CRUZAMENTOS-V1.json`

### EXISTING OPPORTUNITIES ENRICHED

**4 enriquecidas · 5 não · 0 mudanças de status · 0 mudanças de score.**

| ID | o que ganhou |
|---|---|
| `OPP_576D71D702F0` | o boletim de **02/09/2026** nomeia **Pirimicarb** com limiar declarado — e marca a substância como candidata à substituição |
| `OPP_88CC35C57C7B` | **Imazamox** ainda posicionado pelo serviço regional em 21/08/2026, 301 dias antes do limite UE |
| `OPP_3965565ACFCC` | **folpet** dentro de um teto compartilhado (`Tra Captano, Folpet e Fluazinam Max 4`) e chamado **duas vezes** em deroga na mesma campanha |
| `OPP_8EA4F5C0D3F4` | o teto `Tra Pyraclostrobin e Azoxystrobin Max 3` — gestão de resistência escrita |

Não enriquecidas: `OPP_2BDE8FC566CE` · `OPP_6E18A133EE14` · `OPP_886307860F79` ·
`OPP_E6200AA0FA63` (fora de janela) · `OPP_AF16E6A6B8B3`.

#### A rota que eu mesmo listei como próximo passo, li — e ela **não** fecha o caso

Listei "ler a *scheda* de cercospora para fechar `OPP_2BDE8FC566CE`" como desbloqueio. Li,
pela API Plone, em 2026-09-03. **A scheda não nomeia fenpropidin, nem difenoconazolo, nem
nenhum fungicida** — a seção *Difesa* remete aos disciplinari e ao modelo.

Uma síntese de motor de busca havia sugerido *"difenoconazolo + fenpropidin"*. **Isso não
estava na página.** Síntese de buscador nunca foi tratada como evidência aqui, e agora está
verificado que não é.

O que a scheda **prova**, e é valioso por outro motivo:

> *"Un utile ausilio alla razionalizzazione dei trattamenti anticercosporici è rappresentato
> dai modelli previsionali **CERCOPRI e CERCODEP** messi a punto dall'**Università Cattolica
> del Sacro Cuore (UCSC) di Piacenza** e **adottati dal Servizio fitosanitario della Regione
> Emilia-Romagna** nell'ambito dell'attività di Previsione e Avvertimento."*

A rota de **timing** da cultura de maior peso de rótulo ADAMA está provada e nomeada, e a
instituição que a assina está no acervo como `IT-SRCX-008`. **A ligação com a molécula desta
oportunidade continua não provada.**

### O achado estrutural sobre as nove, que não estava escrito em lugar nenhum

**Sete das nove são `O5_REGULATORY_PREPARATION` com `GEOGRAPHY = GEO_EU`.** E **nenhuma das
nove** carrega `FIELD_SIGNAL`, `PUBLIC_VOICE` ou `AGROMET` entre as suas `EVIDENCE_FAMILIES`.
As dimensões de score confirmam: `AGRONOMIC = 1` e `CURRENTNESS = 1` em todas as O5.

> **As nove confirmadas são um calendário regulatório, não uma observação de campo.**

Isso é *coerente* com o que o SINTONIA já provou duas vezes — `BETTER TIMING` sobrevive no
vencimento regulatório e **não** sobrevive na voz pública. Mas significa que, hoje, a
resposta de **"o que está acontecendo AGORA"** não vem das nove. É exatamente o buraco que
esta missão atacou.

### NEW TO_VALIDATE

**1 candidato**, e ele não é promovido por esta missão — é proposto ao mesmo método:

`PATATA × ELATERIDI (Agriotes litigiosus, sordidus, brevis) — Emilia-Romagna`
Nenhuma das 37 oportunidades cobre este par. O corpus de rótulo tem apenas 2 pares
`PATATA × ELATERIDI`, e tem `LEBRON 0.5 G` com `ELATERIDI` na **linha da tabela** para
`FRUMENTO`, `BARBABIETOLA`, `SORGO`, `GIRASOLE`, `LEGUMINOSE` e `BRASSICACEE` — as culturas
hospedeiras que o próprio pesquisador nomeia como polífagas.

### NEW VERIFIED

**Nenhuma.** Nenhum dos cinco cruzamentos passou por todos os portões que uma
`OPPORTUNITY_CONFIRMED` exige, e a régua que promove não roda nesta branch.
**Não baixei gate, não alterei score, não promovi à mão.**

---

## 6 · FRIDAY DEMO — TOP 5

### 1 · O boletim recomenda a molécula da ADAMA pelo nome, com limiar — e marca a mesma molécula como candidata à substituição

| | |
|---|---|
| **WHY NOW** | boletim de **02/09/2026**, um dia de idade na data de referência |
| **SOURCES CROSSED** | 3 · Servizio Fitosanitario ER · Agricast (projeto *Riduci*) · rótulo autorizado |
| **VOICE / VIDEO** | áudio de 11/05/2026, 975 s, transcrito localmente |
| **TRANSCRIPT SIGNAL** | *"la progressiva riduzione degli insetticidi ad ampio spettro ha modificato gli equilibri del frutteto … ha reso più evidente il ruolo degli antagonisti naturali, come **Aphelinus mali**, nel contenimento dell'afide lanigero"* — @345 s. **Nada disso está na legenda.** |
| **CROP / TARGET** | MELO × afide lanigero (*Eriosoma lanigerum*) |
| **GEOGRAPHY** | Emilia-Romagna — Forlì-Cesena, Ravenna, Rimini (declarada pelo documento) |
| **ADAMA RELEVANCE** | **LINHA_DA_TABELA** — o elo mais forte. `IT-LBL-024` PIRIMOR 50, `IT-LBL-231` PIRIMOR 17,5, `IT-LBL-992` APHOX, `IT-LBL-1544` APHOX 50, `IT-LBL-1592` XINTECH 50 — todos `MELO × AFIDI × Eriosoma spp` |
| **CROP WINDOW** | aberta; o boletim dá o gatilho operacional, não uma data |
| **ACTION MAP** | SCIENCE_TECHNICAL · MARKET_DEVELOPMENT · **REGULATION_PORTFOLIO** |
| **PROVES** | que em 02/09/2026 o serviço regional mandou intervir com **Pirimicarb** ao ultrapassar **10 colônias vivas em 100 órgãos controlados**; que a ADAMA tem cinco registros com esse par lido na linha da tabela; e que o mesmo documento marca pirimicarb como `Sostanza attiva Candidata alla Sostituzione` |
| **DOES NOT PROVE** | não prova incidência — o próprio boletim diz *"situazione al momento ben controllata"*; não prova incidência italiana; não prova demanda, venda, pedido de revenda nem share; não prova que a substituição vai acontecer nem quando |

> **A solução recomendada e a molécula sob pressão regulatória são a mesma.**

---

### 2 · A vacância de modo de ação está dita em voz alta, com o ano da revogação e o nome das três espécies

| | |
|---|---|
| **WHY NOW** | a revogação citada é de 2014 e **continua valendo**; a fala é de 23/03/2026 |
| **SOURCES CROSSED** | 2 · Agricast (projeto das OP do setor da batata) · rótulo autorizado |
| **TRANSCRIPT SIGNAL** | *"la revoca o l'inefficacia dei formulati di sintesi disponibili … tre specie di elateridi … **litigiosus, sordidus e brevis** … essendo polifaghe, arrecano danni oltre che alla patata, anche a **cereali, erba medica, barbabietola**"* @61 s · *"nel 2014 … è stato revocato un geoinsetticida a base di **fipronil**, a cui sono seguite altre revoche … anche gli insetticidi di sintesi disponibili a base di **spinosad** o piretrine sintetiche … **non garantiscono un controllo risolutivo**"* @211 s |
| **A LEGENDA** | 681 caracteres. Diz que o projeto "afinou a metodologia de monitoramento" e "estuda as espécies". **Não nomeia Agriotes, não nomeia espécie, não cita revogação, não cita fipronil, não cita spinosad, não diz que o controle disponível não é resolutivo.** |
| **CROP / TARGET** | PATATA × elateridi |
| **GEOGRAPHY** | Emilia-Romagna (declarada pelo pesquisador) |
| **ADAMA RELEVANCE** | a ponte é a **polifagia dita pelo próprio pesquisador**: `LEBRON 0.5 G` tem `ELATERIDI` na linha da tabela para FRUMENTO, BARBABIETOLA, SORGO, GIRASOLE, LEGUMINOSE e BRASSICACEE |
| **ACTION MAP** | SCIENCE_TECHNICAL · MARKET_DEVELOPMENT |
| **PROVES** | que um projeto público declara agravamento do dano, causa regulatória desde 2014, e que os geodisinfestantes disponíveis não dão controle resolutivo |
| **DOES NOT PROVE** | não prova incidência medida, não prova área, não prova que a ADAMA pode usar LEBRON em batata, não prova demanda. **Uma voz não é uma tendência.** |

---

### 3 · A série sobe, o boletim nomeia a substância com teto — e a mesma fala mede o substituto

| | |
|---|---|
| **WHY NOW** | capturas até **31/08/2026**; recomendação de **02/09/2026** |
| **SOURCES CROSSED** | 3 · rede de trappole UNIBO · Servizio Fitosanitario ER · Agricast (projeto *REMUNERA*) |
| **NÚMERO** | semana de 31/08: ninfas II-III em **PC 108** (n=3 armadilhas), **RA 107** (n=6), **MO 175** (n=15); ninfas IV-V em RA passaram de **22 para 52** |
| **TRANSCRIPT SIGNAL** | *"crescente è l'interesse verso quelle anti-insetto, soprattutto dopo la diffusione della cimice asiatica"* @125 s · *"una rete anti-insetto monoblocco che … **permette di ridurre l'apporto di agrofarmaci**, l'investimento iniziale sale intorno a **55.000 euro ettaro**"* @178 s. A legenda fala de *benchmarking de custos*. |
| **CROP / TARGET** | MELO × cimice asiatica, 2ª geração |
| **ADAMA RELEVANCE** | `BLOCO_DA_CULTURA` — KLARTAN 20 EW, TAU AL 240 EW, MAVRIK SMART, KLARTAN SMART trazem `MELO × CIMICE`; **tau-fluvalinate só é a primeira opção nomeada na seção MELO** (em PERO, PESCO e ACTINIDIA o boletim indica outras) |
| **ACTION MAP** | MARKET_DEVELOPMENT · SCIENCE_TECHNICAL · COMPETITOR_WATCH |
| **PROVES** | aumento de ninfas e adultos de 2ª geração até 31/08 nas províncias citadas; recomendação datada de tau-fluvalinate com teto de 2 intervenções |
| **DOES NOT PROVE** | **`n` = armadilhas inspecionadas e ele mexe semana a semana** (RA passou de 13 para 6). Província com `n=0` é observação ausente, **nunca pressão zero**. As parcelas não são amostra aleatória. E os 55.000 €/ha são uma cifra citada num podcast, não um preço medido |

> **O sinal de campo e o sinal de substituição estão no mesmo episódio.**

---

### 4 · Uma janela excepcional com data de abertura e de fechamento — e ela já fechou

| | |
|---|---|
| **WHY NOW** | *"impiego consentito dal **28/04/2026 al 25/08/2026**"* — fechou nove dias antes da data de referência |
| **SOURCES CROSSED** | 2 · deroga regional (via boletim de Parma, 21/08/2026) · portfólio ADAMA |
| **CROP / TARGET** | PERO × maculatura bruna (*Stemphylium vesicarium*) |
| **ADAMA RELEVANCE** | `SUBSTANCIA_ATIVA`. **folpet** é substância ADAMA (FOLPAN 80 WDG, FOLPAN ENERGY e mais 11). **FOLPEC 50 SC e FOLDER 80 WG não são produtos ADAMA** |
| **CROP WINDOW** | **FECHADA.** O valor não é agir agora: a deroga recorre por campanha, e a preparação de 2027 começa antes de abril |
| **ACTION MAP** | REGULATION_PORTFOLIO |
| **PROVES** | que a Emilia-Romagna autorizou uso excepcional de folpet em pera contra *Stemphylium*, numa janela declarada, **através de um produto que não é da ADAMA** |
| **DOES NOT PROVE** | não prova que a ADAMA pode registrar, vender ou pedir a mesma deroga; não prova que se repete em 2027; **produto de concorrente não é produto ADAMA** |

---

### 5 · Uma fonte que explica as outras

`Ri.Nova soc. coop.` apareceu **duas vezes por caminhos independentes**: o nome está
impresso na nota técnica da cimice do Servizio Fitosanitario ER — que pede aos técnicos que
falem com ela para alimentar a rede de armadilhas — e reapareceu na varredura social como a
cooperativa de pesquisa que coordena os *Gruppi Operativi* narrados no Agricast.

> **Uma fonte que explica as outras vale mais que uma fonte a mais.**

Ela amarra, numa só entidade: a série numérica (`IT-SRCX-003`), a voz transcrita
(`IT-SRCX-016`) e as culturas de `OPP_20D89B04F64D`, `OPP_DA4B5954F72A` e
`OPP_75C37DED9160`.

---

## 7 · TOP 3 VIDEO WOW CASES

Os três são **áudio**, não vídeo — e isso torna o caso mais forte, não mais fraco:
**não existe legenda alternativa, o sinal só existe porque alguém transcreveu.**

| # | objeto | legenda → fala | o que só a fala tinha |
|---|---|---|---|
| 1 | *Difesa della patata dagli elateridi* · 23/03/2026 · 729 s | 681 → **9.362** car. (**1:14**) | as 3 espécies de *Agriotes*, a revogação do fipronil em 2014, spinosad sem controle resolutivo, RNAi |
| 2 | *Riduci — ridurre gli input chimici* · 11/05/2026 · 975 s | 751 → **14.214** car. (**1:19**) | *Aphelinus mali*, o mecanismo da redução dos inseticidas de amplo espectro, deriva e resíduos com drone |
| 3 | *REMUNERA — il prezzo delle scelte* · 31/08/2026 · 774 s | 960 → **12.819** car. (**1:13**) | cimice asiática, rede anti-insecto monobloco, **55.000 €/ha**, "reduz o aporte de agrofarmacos" |

Medida agregada: **6 dos 9 objetos** têm termo técnico presente na fala e **ausente** da
legenda. Nos outros 3, a legenda já cobria o vocabulário — e registrar isso é o que dá
sentido ao 6.

---

## 8 · PERSISTENCE — amostra de 10 do registro

| SOURCE_ID | NAME | TYPE | URL | ADAMA RELEVANCE | COLLECTION | LAST CHECK | MONITORING |
|---|---|---|---|---|---|---|---|
| `IT-SRCX-001` | Consorzio Fitosanitario Parma | FITOSANITARY_SERVICE | fitosanitario.pr.it | barbabietola + pomodoro, as duas de maior peso de rótulo | RSS | 2026-09-03 | WEEKLY |
| `IT-SRCX-002` | Consorzio Fitosanitario Piacenza | FITOSANITARY_SERVICE | fitosanitario.pc.it | província dos modelos CERCOPRI/CERCODEP | RSS | 2026-09-03 | WEEKLY |
| `IT-SRCX-003` | UNIBO BIG — trappole *H. halys* | FIELD_MONITORING_NETWORK | big.csr.unibo.it | única série numérica; liga a `OPP_56F19FD9F62B` e ao tau-fluvalinate | POST JSON | 2026-09-03 | WEEKLY |
| `IT-SRCX-004` | API dos bollettini do Serv. Fito. ER | FITOSANITARY_BULLETIN_API | agricoltura.regione.emilia-romagna.it | onde a substância ADAMA aparece com dose e teto | REST + PDF | 2026-09-03 | WEEKLY |
| `IT-SRCX-008` | UCSC Piacenza — CERCOPRI/CERCODEP | UNIVERSITY_GROUP | piacenza.unicatt.it | diz *quando* a cercospora começa na cultura de 239 pares | HTML | 2026-09-03 | MONTHLY |
| `IT-SRCX-010` | Agralia Studio Agronomico | PRIVATE_AGRONOMIC_ADVISORY | agralia.it | voz técnica privada de vite na Lombardia | RSS + IG + YT | 2026-09-03 | WEEKLY |
| `IT-SRCX-014` | OI Pomodoro da Industria Nord Italia | INTERPROFESSIONAL_ORG | oipomodoronorditalia.it | denominador do pomodoro, cultura de 4 das 37 | HTML | 2026-09-03 | MONTHLY |
| `IT-SRCX-016` | Agricast — Gruppi Operativi ER | PODCAST | spreaker.com/podcast/agricast--5971526 | a fala onde está o sinal que a legenda não tem | API + whisper local | 2026-09-03 | MONTHLY |
| `IT-SRCX-028` | ARPAE ERG5 — série horária | AGROMET_OPEN_DATA | dati-simc.arpae.it | entrada dos modelos de janela | HTTP + ZIP | 2026-09-03 | DAILY |
| `IT-SRCX-033` | Ri.Nova soc. coop. | RESEARCH_COOPERATIVE | linkedin.com/company/rinovaricerca | a fonte que explica as outras | LinkedIn + YT + IG | 2026-09-03 | MONTHLY |

Registro completo, com os 30 campos por ficha:
`data/samples/IT-FONTES-V1/IT-FONTES-DESCOBERTA-V1.json`

---

## 9 · REJEIÇÕES — porque uma rejeição com motivo é patrimônio

| fonte | classe | motivo |
|---|---|---|
| `image-line.com` | `WRONG_ENTITY_SAME_NAME` | **está no acervo canônico** como `SRC_IMAGE_LINE_COM`, `TECHNICAL_MEDIA`, `GREEN`, **sem campo `NAME`**. É a **FL Studio**, software musical. A editora agrícola é a Image Line s.r.l. em `imagelinenetwork.com` |
| `sipcamitalia.it` / `sipcam.it` | `WRONG_ENTITY_FOR_THE_GEOGRAPHY` | os dois servem *"Sipcam Agro USA"*. Registrar como concorrente **italiano** seria inventar geografia a partir de um domínio |
| `betaitalia.it` | `WRONG_ENTITY_SAME_NAME` | procurada como a BETA, sociedade de pesquisa da bietola. Responde *"Beta Italia — Cucina, Casa e Giardinaggio"*. **Achado duas vezes, por dois caminhos independentes** |
| Open Data Hub Alto Adige | `STALE_CONTENT_BEHIND_A_LIVE_ENDPOINT` | responde 200 sem autenticação e parece vivo. O valor mais recente da origem SIAG tem `mvalidtime` de **2016-01-26**; a chamada sem filtro devolve série de **2007-12-31** |
| perfis genéricos de `azienda agricola` | `NO_ADAMA_RELEVANCE` | a busca devolveu apicultura, laticínios, horta biológica e agriturismo. Contas reais, **nenhuma observa cultura, alvo, molécula ou região do radar** |
| 62 canais YouTube do acervo | `LOW_RELEVANCE_ALREADY_REGISTERED` | reclassificar, **não apagar**: `RELEVANCE: LOW` e `COUNTRY != IT` onde for o caso |

> **`ENDPOINT VIVO ≠ DADO ATUAL.` `O NOME DE UMA EDITORA TAMBÉM PODE SER O NOME DE UM SOFTWARE.`**

---

## 10 · REDE DE MONITORAMENTO

```
MONITOR_DAILY   =  6   agromet e mídia de alta cadência
MONITOR_WEEKLY  = 12   bollettini, trappole, voz técnica privada
MONITOR_MONTHLY = 17   ciência, cooperativas, mercado, concorrente
EVENT_DRIVEN    =  1   feed de usi di emergenza
DISCOVERY_ONLY  =  0
DO_NOT_MONITOR  =  0
```

**Não criei agendamento real.** A recomendação fica guardada por ficha, como a missão pediu.

---

## 11 · CLASSIFICAÇÃO PARA SEXTA

| estado | o quê |
|---|---|
| **INGESTIBLE_NOW** | as 36 fichas de fonte · os 5 cruzamentos · o enriquecimento das 4 · o índice dos 150 bollettini · a série da cimice · as 9 transcrições · o lote congelado de 32 contas |
| **NEEDS_VALIDATION** | o candidato `PATATA × ELATERIDI` · a reclassificação dos 62 canais · a correção de `SRC_IMAGE_LINE_COM` |
| **FUTURE** | coleta de Instagram (precisa do runner com navegador) · transcrição de vídeo do YouTube (precisa da rota de mídia) · leitura da *scheda* de cercospora para fechar `OPP_2BDE8FC566CE` |
| **REJECTED** | as 6 da tabela acima |

---

## 12 · FINAL

```
READY TO INGEST  = YES  — para as 36 fichas, os 5 cruzamentos e as 9 transcrições
CANONICAL GUARDS = PASS — 329 testes, 0 falhas
                          DEDUPE de fontes: PASS
                          SOURCE_ID_COUNT: intacto em 36, deliberadamente
                          status e score das 37 oportunidades: intocados
```

**EXACT BLOCKERS**

1. **Instagram** — o Chrome não atravessa o proxy desta sessão; a página de perfil devolve
   302/429. **Desbloqueio:** rodar `sintonia-scrap.yml` fase `janela` no runner
   self-hosted. O lote já está congelado e pronto.
2. **Mídia do YouTube** — `googlevideo.com` devolve 403 pela política de saída. Metadados e
   feeds de canal funcionam. **Desbloqueio:** mesma máquina.
3. **`SRC_IMAGE_LINE_COM`** aponta para a empresa errada no acervo canônico. É uma linha a
   corrigir, e ela está na branch do site.
5. **`OPP_2BDE8FC566CE`** continua sem evidência de campo: a *scheda* de cercospora foi lida
   e **não** nomeia fenpropidin. O desbloqueio agora é outro — o *disciplinare di produzione
   integrata* da barbabietola, que é onde as moléculas estão listadas.
4. **Beta (bietola)** continua `NAO_SEI`: três domínios tentados, nenhum é a instituição.

**NEXT BEST SOURCES TO EXPAND** (máximo 10)

1. `Südtiroler Beratungsring` — o serviço de aconselhamento técnico do Alto Adige para maçã
   e vinha. Não abriu daqui (`beratungsring.org`, `sbr.bz.it`). É a voz técnica de campo que
   mais falta.
2. `Horta s.r.l.` / `vite.net` — o DSS que opera os modelos de janela. Entrou pelo `.it`;
   o produto está atrás de login.
3. `disciplinare di produzione integrata` da barbabietola (ER) — a *scheda* de cercospora já
   foi lida e **não** nomeia moléculas; o disciplinare é onde elas estão.
4. `Ente Nazionale Risi` — resistência de *Echinochloa* e *Alisma* no arroz, direto em
   `OPP_4C39CCC05EEB`. Hoje falha TLS com `DH_KEY_TOO_SMALL`.
5. `GIRE` — mapas nacionais de resistência a herbicidas, para os 26 produtos de erbicidi.
6. `Laimburg` — relatórios anuais sobre maçã e vinha do Alto Adige.
7. `Fondazione Agrion` — a mesma camada, no Piemonte.
8. `CSO Italy` — previsão de produção das pomáceas, o denominador que falta.
9. `Consorzi Agrari d'Italia` — a camada de distribuição, ausente do acervo.
10. `AIPP` — feed, canal de vídeo e Instagram da sociedade italiana de proteção das plantas.

---

## PRINCÍPIO FINAL — as duas perguntas

**1 · O QUE ESTÁ ACONTECENDO AGORA?**
Na Emilia-Romagna, em 02/09/2026: ninfas de cimice asiática de 2ª geração em alta, afide
lanigero em leve aumento sob limiar declarado, e duas moléculas do universo ADAMA
recomendadas por nome — uma delas marcada como candidata à substituição no mesmo parágrafo.

**2 · ONDE DEVE OLHAR NOVAMENTE AMANHÃ?**
Em 36 endereços, com a periodicidade escrita ficha a ficha, o método de coleta declarado e a
data da última verificação — para que a próxima passagem **não tenha de redescobrir a
internet toda**.
