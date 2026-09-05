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

A descoberta aconteceu em **duas levas**. A primeira foi minha, sequencial. A segunda foi
uma varredura paralela de 34 agentes, que devolveu **93 fontes e 95 rejeições** — e da qual
**nada entrou por confiança**: reconferi na mão os 52 hosts que ainda não estavam no
registro e os 17 handles sociais, um a um. Duas admissões da varredura **caíram** na minha
releitura, e estão em §9.

```
SOURCES DISCOVERED   = 221 endpoints sondados com HTTP real (128 na 1ª leva + 93 na 2ª)
SOURCES QUALIFIED    = 90
HIGH RELEVANCE       = 43
MEDIUM               = 47
REJECTED             = 11  no código, com motivo escrito
                     + 95  preservadas em bruto (IT-FONTES-REJEICOES-LOTE2-V1.json)
ROUTES NOT REACHED   = 21  (estado da rede, nunca estado do mundo)
OPEN CONTRADICTIONS  = 1   (duas fontes de autoridade discordam e eu não arbitrei)
CORRECTIONS TO MY OWN MEASUREMENTS = 3
```

**BY AUTHORITY**

```
SCIENTIFIC = 21 · OFFICIAL = 19 · COMPETITOR = 14 · MEDIA = 12
INDUSTRY = 11 · TECHNICAL = 8 · FIELD_VOICE = 5
```

**BY TYPE (leitura da missão)**

```
OFFICIAL / FITOSSANITARIO = 11     AGROMET = 5         SCIENCE / RESEARCHERS = 21
COOPERATIVES / PRODUCERS = 9       TECHNICIANS = 8     MARKET = 7
MEDIA = 12                         COMPETITORS = 14    EVENTOS = 2
SOCIAL (perfis declarados) = 45 em 27 organizações
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
Mintar 90 IDs novos moveria essa régua **em silêncio**. O namespace novo não casa com o
regex do ledger. O caminho de promoção está escrito no Atlas.

**AUTOMATION POTENTIAL**

```
AUTOMATABLE = 52 · PARTIAL = 36 · MANUAL = 2 · BLOCKED = 0
DAILY = 6 · WEEKLY = 25 · MONTHLY = 54 · EVENT_DRIVEN = 3 · DISCOVERY_ONLY = 1
DO_NOT_MONITOR = 1  (um canal de concorrente medido e CONGELADO — ver §9)
COM FEED OU API = 29
```

### As sete que mais mudam o que dá para observar

| ID | fonte | por quê |
|---|---|---|
| `IT-SRCX-003` | UNIBO BIG — rede de trappole de *Halyomorpha halys* | **única série numérica de campo** desta rodada: 177 pontos, por província e por estádio, 2021 → 2026-08-31, API aberta sem chave |
| `IT-SRCX-004` | API Plone dos bollettini do Servizio Fitosanitario ER | o host já estava no acervo, a **rota** não. A página é um SPA e não entrega link nenhum; a API entrega os **150 PDFs de 2026** com título e data |
| `IT-SRCX-028` | ARPAE ERG5 — série **horária** por estação | é a entrada dos modelos que decidem *quando* tratar. Sem ela, "janela" é calendário |
| `IT-SRCX-016` | Agricast — podcast dos Gruppi Operativi da ER | fala técnica longa onde o sinal está **só no áudio** |
| `IT-SRCX-076` | Fitogest — diretório de empresas | **a única rota alcançável** para o catálogo italiano dos concorrentes: Syngenta 136, UPL 116, Corteva 93, Bayer 78, ADAMA 56. Os sites da Syngenta e da Bayer devolvem 403 |
| `IT-SRCX-046` | ISTAT — web service SDMX | superfície e produção **por província**. É o denominador que falta: sem hectare, "pressão em melo na Emilia-Romagna" não tem escala |
| `IT-SRCX-051` | base de Heap — resistência a herbicida | põe **número** na exposição do bloco herbicida: dos 29 casos italianos, 23 caem nos dois grupos onde a ADAMA se concentra |

---

## 3 · SINTONIA SCRAP

Localizei e li o Sintonia Scrap antes de tocar em qualquer coisa:
`scripts/instagram_janela.py` (rota pública pelo navegador), `instagram_coleta.py` (rota
paga Apify), `instagram_transcrever.py` (transcrição **local**), orquestrados por
`.github/workflows/sintonia-scrap.yml`. **Não construí outro scraper.**

```
PROFILES DISCOVERED = 45 perfis declarados por 27 organizações
PROFILES QUALIFIED  = 40 em três lotes congelados (V1 32 · V2 5 · V3 8, sem repetição)

INSTAGRAM CONTENTS  = 180 objetos em 30 contas (V1 102 · V2 30 · V3 48)
INSTAGRAM VIDEOS    = 51
TRANSCRIBED         = 48 reels, 3.630 + 4.210 caracteres, 0,00 USD
FAILURES            = 3 (REQUESTED_EMPTY: o áudio não tinha fala)

VIDEO SIGNALS ONLY IN TRANSCRIPT = V1 5/28 · V2 2/15 · V3 0/5
```

### A rota de Instagram abriu — e o conteúdo continua não rendendo

Eu havia escrito que a rota de embed "precisa do navegador". **Estava errado, e o erro foi
meu**: o que faltava era o `User-Agent`. Mesma URL, mesmo minuto:

```
UA Chrome desktop ........ HTTP 200 · 625.215 B · contextJSON = 0
UA facebookexternalhit/1.1  HTTP 200 · 262.551 B · contextJSON = 1
```

A rota virou capacidade permanente (`scripts/instagram_sem_navegador.py`) e rodou em três
lotes. E é aqui que a honestidade custa: **a rota abrir não fez o conteúdo aparecer.**

| lote | critério de entrada | assunto na legenda | vídeo | sinal só na fala |
|---|---|---|---|---|
| V1 | site da **organização** | 14/102 = 13,7 % | 29,4 % | 5 de 28 |
| V2 | **voz individual** (hipótese minha) | 5/30 = 16,7 % | 50,0 % | 2 de 15 |
| V3 | organização **já com ficha de fonte** | 9/48 = **18,8 %** | **12,5 %** | 0 de 5 |

**A minha hipótese da V2 falhou** — a taxa caiu, e a causa foi medida: a conta individual de
maior audiência do recorte publica conteúdo de comida, e os dois "sinais" da V2 eram falsos
positivos do meu próprio vocabulário (*"sentiamo un bel pomodoro forte"* é nota de degustação
de azeite).

**A V3 mudou o critério de novo e o resultado é ambíguo, dito com precisão:** ela tem a
**maior** taxa de assunto na legenda e a **menor** taxa de vídeo das três. Escolher a conta
pela relevância já provada da organização melhora a colheita de **legenda** e piora a de
**fala** — instituto de pesquisa publica carrossel, não reel. E com 5 reels transcritos,
**zero sinal só-na-fala não é evidência de ausência**: é denominador pequeno.

> **FRASE PROIBIDA:** *o Instagram italiano não tem voz de campo.*
> **FRASE PERMITIDA:** *nas 30 contas deste acervo, nesta leitura de 2026-09-03, 48 reels
> não produziram um sinal de campo defensável.*

O que ainda precisa do runner: a grade **completa** (esta rota entrega 6 itens por conta, o
Chrome com janela entrega 12) e os **comentários**, que nenhuma rota gratuita entrega — e que
continuam sendo o único motivo real de pagar.

### A rota que resolveu o que o Instagram não resolveu — e o que ela custou

Depois de três lotes de Instagram renderem 5, 2 e 0, abri a camada de **áudio** como rota
permanente (`scripts/it_audio.py`, API pública do Spreaker, sem chave).

```
PROGRAMAS DECLARADOS = 3 vivos  (+ 4 medidos e CONGELADOS, com a data que os reprova)
EPISÓDIOS NA JANELA  = 13 em 90 dias
ÁUDIO                = 19.058 s = 5,3 horas
TRANSCRITO           = 286.395 caracteres · 2.118 s de máquina · 0,00 USD
SINAL SÓ NA FALA     = 11 de 13  (84,6 %)
```

| rota | caracteres por objeto | sinal só na fala |
|---|---|---|
| Instagram V1 | ~1.100 | 5 de 28 = 17,9 % |
| Instagram V2 | ~950 | 2 de 15 = 13,3 % |
| Instagram V3 | ~840 | 0 de 5 |
| **Podcast** | **~22.000** | **11 de 13 = 84,6 %** |

**E a auditoria que eu fiz em cima da minha própria marca derruba a maior parte dela.** Abri
as 11 marcas e li o trecho que produziu cada uma:

- **8 de 11** são *inventário de cultura* — *"coltiviamo mais, frumento, erba medica"*.
  **CULTURA CITADA ≠ SINAL DE CAMPO.**
- **3 de 11** nomeiam *avversità*, que é o que aponta janela.
- **1 é falso positivo do meu próprio vocabulário:** o regex de `FRUMENTO` é `\bgrano\b` e a
  fala diz *"farro, sorgo, miglio e **grano saraceno**"* — trigo sarraceno é *Fagopyrum
  esculentum*, não é trigo. Mesma família de *"sentiamo un bel pomodoro forte"* e de `LIGA`
  vindo de *obbligatorio*.

> **A taxa de 84,6 % é verdadeira e enganosa ao mesmo tempo.** Ela é alta porque o
> denominador é a descrição do episódio, e a descrição do melhor episódio desta leva tem
> **zero caracteres**. A medida certa seria contra **avversità**, não contra cultura — e essa
> é a próxima correção da régua.

**O que a rota entregou de fato:** um cruzamento defensável, `IT-X-2026-007`, por 5,3 horas
de áudio e 35 minutos de máquina. Caro por cruzamento. E ainda assim infinitamente melhor
que os três lotes de Instagram, que entregaram **zero**.

### A primeira rota de voz que abriu, e o que ela custou

| | |
|---|---|
| objetos | 9 |
| áudio | 9.100 s = **151,7 minutos** |
| transcrito | **130.935 caracteres** de agronomia italiana falada |
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
NEW VOCI        = 9 objetos de áudio, 130.935 caracteres de fala
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
NEW CROSSINGS = 7
  por força do elo:  LINHA_DA_TABELA = 4 · SUBSTANCIA_ATIVA = 3
  com evidência que existe SÓ NA FALA = 6 de 7
NÃO CRUZADOS (com o motivo escrito) = 6

SINAIS CANDIDATOS = 45 · TESTADOS ADVERSARIALMENTE = 24
SOBREVIVERAM = 21 · REFUTADOS = 3
  por cultura: MELO 7 · VITE 5 · POMODORO 3 · BARBABIETOLA 2 · PESCO 2 · PERO 1 · ACTINIDIA 1
```

**Sobreviver à refutação não promove nada.** Nenhum status e nenhum score foi alterado por
causa dos 21. Um dos 3 refutados caiu pelo motivo mais instrutivo possível: *a citação é
genuína e a fonte está viva, mas a contagem central da observação está errada.*

`data/samples/IT-CRUZAMENTO-V1/IT-CRUZAMENTOS-V1.json`

### EXISTING OPPORTUNITIES ENRICHED

**5 enriquecidas · 4 não · 0 mudanças de status · 0 mudanças de score.**

| ID | o que ganhou |
|---|---|
| `OPP_576D71D702F0` | o boletim de **02/09/2026** nomeia **Pirimicarb** com limiar declarado — e marca a substância como candidata à substituição |
| `OPP_88CC35C57C7B` | **Imazamox** ainda posicionado pelo serviço regional em 21/08/2026, 301 dias antes do limite UE |
| `OPP_3965565ACFCC` | **folpet** dentro de um teto compartilhado (`Tra Captano, Folpet e Fluazinam Max 4`) e chamado **duas vezes** em deroga na mesma campanha |
| `OPP_8EA4F5C0D3F4` | o teto `Tra Pyraclostrobin e Azoxystrobin Max 3` — gestão de resistência escrita |
| `OPP_2BDE8FC566CE` | **enriquecida e ESFRIADA** — ver abaixo |

Não enriquecidas: `OPP_6E18A133EE14` · `OPP_886307860F79` · `OPP_E6200AA0FA63` (fora de
janela) · `OPP_AF16E6A6B8B3`.

#### O melhor achado desta missão ESFRIA um caso em vez de esquentar

`OPP_2BDE8FC566CE` é BARBABIETOLA × CERCOSPORA. Eu havia procurado o elo na palavra
*fenpropidin* e não achado — e registrado a rota como lida e refutada. **A varredura
adversarial achou o elo que eu perdi, e ele não estava na palavra: estava no PAR DE RÓTULO.**

A ADAMA tem **exatamente uma** linha de rótulo `BARBABIETOLA × CERCOSPORA` em todo o radar:
`IT-LBL-409`, **SPYRALE**, registro 009757 — e SPYRALE é *difenoconazolo + fenpropidin*.

E então o caso **esfria**, porque a mesma leitura diz o resto:

- o boletim declara *"presenza della malattia **modesta**"* — pressão **baixa**, dita pela
  própria fonte;
- a recomendação é **rame e zolfo**, não um IBE;
- **SPYRALE não é nomeado em nenhum dos 14 boletins**;
- e SPYRALE é um **registro do Ministero** detido pela ADAMA, **não** um dos 51 produtos do
  catálogo comercial.

> **`PORTFOLIO RELATION ≠ LABEL AUTHORIZATION` e `163 REGISTROS ≠ 51 PRODUTOS`.**
> Achar o elo e ainda assim esfriar o caso é o comportamento correto. Um elo encontrado não
> é um argumento de venda.

#### A rota que eu mesmo listei como próximo passo, li — e ela não fecha o caso *sozinha*

Listei "ler a *scheda* de cercospora para fechar `OPP_2BDE8FC566CE`" como desbloqueio. Li,
pela API Plone, em 2026-09-03. **A scheda não nomeia fenpropidin, nem difenoconazolo, nem
nenhum fungicida** — a seção *Difesa* remete aos disciplinari e ao modelo.

Uma síntese de motor de busca havia sugerido *"difenoconazolo + fenpropidin"*. **Isso não
estava na página.** Síntese de buscador nunca foi tratada como evidência aqui, e agora está
verificado que não é. O elo real veio de outro lugar — do par de rótulo, acima — e a scheda
continua sem nomear fungicida nenhum.

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
| `IT-SRCX-050` | CNR — IPSP | RESEARCH_INSTITUTION | ipsp.cnr.it | dono institucional do GIRE; o teste que decide se ALS ou ACCase ainda funciona | HTTP | 2026-09-03 | MONTHLY |
| `IT-SRCX-051` | base de Heap — resistência a herbicida | SCIENTIFIC_DATABASE | weedscience.org | 23 dos 29 casos italianos caem nos grupos onde a ADAMA se concentra | HTML | 2026-09-03 | MONTHLY |
| `IT-SRCX-076` | Fitogest — diretório de empresas | COMPETITOR_CATALOGUE_DIRECTORY | fitogest.imagelinenetwork.com | a única rota legível para o catálogo italiano de Syngenta e Bayer | HTML | 2026-09-03 | MONTHLY |
| `IT-SRCX-089` | AGRINET4TECH | PODCAST | spreaker.com/podcast/agrinet4tech--7026131 | um território **nomeado** por episódio — geografia declarada, que é o que falta na voz pública | API + whisper local | 2026-09-03 | WEEKLY |

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

| `anicav.it` | `ROUTE_BLOCKED_FOR_AUTOMATION` | **a varredura paralela admitiu como fonte**, tendo lido 81.358 B. Eu li duas vezes, nos dois hosts: 200 com **33.245 B idênticos** e título *"Security Check Required"*. É muro de bot |
| LinkedIn do `CSO Italy` | `HANDLE_NAO_RECONFIRMADO` | a varredura disse que o handle estava declarado na casa do dono. `csoservizi.com` devolve 200 com 50.746 B e **zero** link social. Ver `FIX-02` |
| `sive.it`, `agronomy.it`, `italmopa.com` | `WRONG_ENTITY_SAME_NAME` | três armadilhas de marca a mais, todas apanhadas por **buscar em vez de supor** |
| `anb.it`, `bmti.it` | `MURO_DE_BOT` | `bmti.it` **já estava no acervo canônico** e **mudou de estado**: quem confiar na ficha antiga vai achar que a rota funciona |
| 4 podcasts italianos | `CANAL_CONGELADO` | *Minuti di Riso* (BASF, último 2023-12-07, "28 - Arrivederci"), *Lezioni di Vite* (2023), *La settimana del riso* (2025-07-26), *Just Agronomo* (2024-12-24). Assunto certo, relógio parado |

As 95 rejeições da varredura paralela ficam preservadas em bruto:
`data/samples/IT-FONTES-V1/IT-FONTES-REJEICOES-LOTE2-V1.json`. O que muda comportamento
subiu para o código; o resto é evidência.

> **`ENDPOINT VIVO ≠ DADO ATUAL.` `O NOME DE UMA EDITORA TAMBÉM PODE SER O NOME DE UM SOFTWARE.`**
> **`PÁGINA VIVA ≠ CANAL VIVO.` `HTTP 200 COM BYTES ≠ CONTEÚDO.`**

### Uma contradição que eu NÃO resolvi

`IT-CONTRA-001` · resistência a **propanil** (HRAC 5) em *Echinochloa crus-galli* na Itália.

- o **GIRE** declara populações resistentes em Piemonte, Lombardia e Toscana **desde 2000**;
- a base de **Heap** põe a Itália em **zero** sob HRAC 5 — conferido por mim, linha 36.

Nenhum dos dois números é erro de leitura: os dois foram lidos direto da fonte. É divergência
de **critério de admissão** entre dois registros. Fica **aberta, não arbitrada e não
escondida** — porque quem publicar *"a Itália tem 29 casos de resistência"* tratando a tabela
de Heap como censo estará omitindo o propanil que o GIRE certifica.

---

## 10 · REDE DE MONITORAMENTO

```
MONITOR_DAILY   =  6   agromet e mídia de alta cadência
MONITOR_WEEKLY  = 25   bollettini, trappole, voz técnica privada, concorrente que anuncia rótulo
MONITOR_MONTHLY = 54   ciência, repositórios, cooperativas, mercado, catálogo de concorrente
EVENT_DRIVEN    =  3   deroghe, usi di emergenza, bollettino ufficiale regional
DISCOVERY_ONLY  =  1   uma GUI sem rota programática — dito como é
DO_NOT_MONITOR  =  1   um canal de concorrente MEDIDO e congelado desde 2023
```

**Não criei agendamento real.** A recomendação fica guardada por ficha, como a missão pediu.

---

## 11 · CLASSIFICAÇÃO PARA SEXTA

| estado | o quê |
|---|---|
| **INGESTIBLE_NOW** | as **90** fichas de fonte · os 7 cruzamentos · o enriquecimento das 5 · os **21 sinais que sobreviveram à refutação** · o índice dos 150 bollettini · a série da cimice · as transcrições de áudio e de 48 reels · os três lotes sociais congelados |
| **NEEDS_VALIDATION** | o candidato `PATATA × ELATERIDI` · a reclassificação dos 62 canais · a correção de `SRC_IMAGE_LINE_COM` · a contradição `IT-CONTRA-001` |
| **FUTURE** | grade completa de Instagram e comentários (precisam do runner) · mídia do YouTube (403 na saída) · os hosts em `NAO_ALCANCADAS` |
| **REJECTED** | as 11 no código, com motivo, + 95 preservadas em bruto |

---

## 12 · FINAL

```
READY TO INGEST  = YES  — 90 fichas, 7 cruzamentos, 5 enriquecimentos, 21 sinais verificados
CANONICAL GUARDS = PASS — 329 testes, 0 falhas
                          DEDUPE de fontes: PASS
                          SOURCE_ID_COUNT: intacto em 36, deliberadamente
                          status e score das 37 oportunidades: intocados
                          SITE: não tocado · VERCEL: não tocado · PRODUÇÃO: não tocada
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
Em **90 endereços**, com a periodicidade escrita ficha a ficha, o método de coleta declarado
e a data da última verificação — para que a próxima passagem **não tenha de redescobrir a
internet toda**. E em 21 endereços a menos do que poderia: os que estão em `NAO_ALCANCADAS`
e em `REJEITADAS` já custaram o tempo de alguém, e o motivo está escrito para que não custem
de novo.

**E A TERCEIRA PERGUNTA, QUE ESTA MISSÃO APRENDEU A FAZER:**
*O que eu escrevi que não se sustenta?* Três correções minhas estão no registro — o
`User-Agent` do Instagram, a prova de agente que aceitei como prova, e a página viva que
confundi com canal vivo. Um número publicado errado não envelhece sozinho.
