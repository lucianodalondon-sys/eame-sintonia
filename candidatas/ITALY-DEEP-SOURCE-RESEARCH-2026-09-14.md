# ITALY-DEEP-SOURCE-RESEARCH — 2026-09-14

**A pergunta desta missão:** *quem, em toda a Itália, produz informação agrícola
útil e recorrente que o SINTONIA deveria acompanhar?*

Não é coleta. Nenhum dado de campo foi colhido, nenhuma corrida de coleta foi
criada, nenhum `SOURCE_ID` e nenhum `DOCUMENT_ID` foi fabricado. O que está aqui
são **candidatas**.

| | |
|---|---|
| branch | `claude/italy-agricultural-sources-discovery-dfba81` |
| HEAD inicial | `f437ff1140fa97484ca9695b341fbe9ca0a9f050` |
| worktree | `C:\eame-sintonia\.claude\worktrees\italy-agricultural-sources-discovery-dfba81` |
| remoto | `https://github.com/lucianodalondon-sys/eame-sintonia.git` |
| planilha | [`ITALY-DEEP-SOURCE-RESEARCH-2026-09-14.xlsx`](ITALY-DEEP-SOURCE-RESEARCH-2026-09-14.xlsx) |
| CSV pronto para a porta | [`ITALY-DEEP-SOURCE-IMPORT-READY-2026-09-14.csv`](ITALY-DEEP-SOURCE-IMPORT-READY-2026-09-14.csv) |

---

## 0 · O QUE JÁ EXISTIA, MEDIDO ANTES DE PROCURAR

O prompt mandava carregar quatro ficheiros. **Três deles não existem nesta
branch** — vivem em `claude/italy-source-qualification-v1`, e foram lidos de lá
pelo git, sem trocar de branch. O git de hoje venceu o prompt.

A linha de base saiu de `candidatas/italy_deep_baseline.py`, que varre todo
catálogo de fonte do repositório mais os dois CSV da rodada anterior:

| | |
|---|---|
| `KNOWN_URLS` | **752** |
| `KNOWN_HOSTS` | **349** (240 deles `.it`) |
| `KNOWN_OWNERS` | **138** |
| `KNOWN_NOMES` | **381** |
| `KNOWN_CHANNELS` | YouTube 75 · LinkedIn 55 · Facebook 33 · Instagram 32 · TikTok 1 |

Sem esta medição, a palavra "nova" não significaria nada.

### Colisão de taxonomia, registada e não resolvida

O prompt usa `T1..T12` como *CROP & PRODUCTION · CLIMATE/WATER/SOIL · … ·
POLICY*. O repositório tem **outra** lista com os mesmos códigos em
`system-map/scripts/scan_sources.py:52` e `pedido/pedido.py:68` — ali `T5` é
*Preço e mercado* e `T7` é *Ciência e ensaio*.

Usei a taxonomia do prompt, que é a mesma declarada como `canonical_territories`
em `candidatas/ITALY-SOURCE-MASTER-V1.json`. **Não alterei o código do
repositório** (está guardado por três ficheiros de teste). A dívida fica
registada aqui e continua aberta.

---

## 1 · COMO PROCUREI

### Rodada 1 — o grafo de ligações (sem buscar palavras)

493 sementes: 120 regionais (6 por região × 20 regiões), 104 nacionais,
39 universidades e 257 hosts `.it`/`.eu` do próprio acervo. O rastreador
(`italy_deep_crawl.py`) abriu cada semente e depois as suas páginas de rede
— *link, partner, progetti, bollettini, rete, soci, consorzi*.

```
3.081 páginas lidas (2.872 com HTTP 200) → 2.513 hosts raiz novos
361 MB · ~20 minutos de máquina local · 0 EUR de API
```

**Por que assim:** uma busca por palavra devolve quem paga SEO. O rodapé de um
serviço fitossanitário devolve quem trabalha com ele.

### Rodada 2 — busca por cultura + problema

O grafo não acha pessoas nem contas sociais. 30 consultas em italiano e inglês,
por praga, doença, cultura e região.

### Rodada 3 — volta dirigida às regiões fracas

Depois de medir a rodada 1, seis regiões tinham zero fonte de classe A. Oito
consultas dirigidas a essas regiões.

### A peneira

`italy_deep_probe.py` abriu cada pista com sonda HTTP real e mediu **seis coisas
em separado** — Itália, sinal agrícola, informação própria, recorrência,
proximidade do facto, identidade. Nenhuma nota única: somar autoridade com
alcance faz um perfil de entretenimento empatar com um serviço fitossanitário.

### Ferramentas: o que usei e o que não usei

| | |
|---|---|
| `LOCAL_MACHINE_USED` | **SIM** — todo o rastreio, sonda e classificação |
| `GPU_USED` | **NÃO** |
| modelo/embedding/classificador | **NÃO** |
| `SINTONIA_SCRAP_USED` | **NÃO** |
| `SEARCH_COST` | `UNKNOWN` — a ferramenta de busca não expõe medidor |
| `API_COST` / `MODEL_COST` | `UNKNOWN` pela mesma razão |
| custo de rede | ~370 MB, medido |

**Nenhuma GPU e nenhum modelo foram usados para classificar fonte.** Foi
escolha: um modelo a dizer *"parece relevante"* não deixa rasto que se possa
auditar. A pré-classe vem de contagem de palavras e de sonda HTTP — as duas
legíveis no código.

---

## 2 · O QUE SAIU

### Contagem (calculada, nunca digitada)

| | |
|---|---|
| **F** `RAW_DISCOVERIES` | **2.813** |
| **G** `UNIQUE_AFTER_DEDUPE` | **2.693** |
| **H** `ALREADY_KNOWN` | **79** |
| **H'** `SAME_OWNER_DIFFERENT_SOURCE` | **103** |
| **I** `TRUE_DUPLICATES` | **1** *(inserido de propósito, como controle)* |
| **J** `NEW_A_EXCELLENT` | **41** linhas · 32 hosts distintos + 4 canais |
| **K** `NEW_B_GOOD` | **176** linhas · 157 hosts distintos |
| **L** `NEW_C_COMPLEMENTARY` | **276** |
| **M** `HOLD` | **468** |
| **N** `UNKNOWN` | **261** |
| **O** `REJECT` | **1.363** |
| **P** `NEW_PEOPLE` | **59** |
| **Q** `NEW_ORGANIZATIONS` | **412** (A+B+C) |
| **R** `NEW_SOCIAL_CHANNELS` | **30** |
| **AR** CSV pronto para a porta | **217 linhas** |

**A+B novas = 217.** Das quais **166 são `PRIMARY`** (donas do facto) e
**41 `NEAR_PRIMARY`**. Recorrência: **69 `HIGH`**, 93 `MEDIUM`, 50 `LOW`,
5 `UNKNOWN`.

### Territórios — novas A/B por território

| | | | | | |
|---|---|---|---|---|---|
| T1 crop | **91** | T5 science | **62** | T9 competitors | **8** |
| T2 clima/água/solo | **34** | T6 researchers | **64 linhas, 44 são pessoas** | T10 mercado | **29** |
| T3 praga/doença | **70** | T7 rede técnica | **84** | T11 eventos | **17** |
| T4 regulatório | **22** | T8 produtores | **37** | T12 política | **74** |

T6 é o território onde o número engana se lido sozinho: os pesquisadores vivem
na folha `PEOPLE`, não na contagem de fontes.

### Regiões — 20 pesquisadas, 20 com pelo menos uma A ou B nova

⚠️ **Como ler esta tabela sem se enganar:** uma fonte multi-regional é contada
em **cada** região que ela cita. `ismeamercati.it` aparece em três; `asipo.it`
em cinco. São 72 linhas multi-regionais no total. A tabela diz *"quantas fontes
fortes falam desta região"*, não *"quantas fontes exclusivas desta região"*.

| região | A | B | as A novas |
|---|---|---|---|
| EMILIA-ROMAGNA | 6 | 18 | fitosanitario.re.it · fitosanitario.pr.it · consorziocer.it · bo.camcom.gov.it · asipo.it |
| PIEMONTE | 3 | 28 | agrion.it · asipo.it · ismeamercati.it |
| LIGURIA | 3 | 6 | flornewsliguria.it · regflor.it · sia.regione.liguria.it |
| SICILIA | 3 | 22 | agrea.it · regione.sicilia.it |
| LAZIO | 3 | 55 | oplatium.it · asipo.it |
| BASILICATA | 3 | 4 | os três canais de Vito Vitelli |
| TRENTINO-ALTO ADIGE | 3 | 4 | ctt.fmach.it · Beratungsring (2 canais) |
| VENETO | 2 | 22 | regione.veneto.it · asipo.it |
| PUGLIA | 2 | 11 | **crsfa.it** · fg.camcom.it |
| ABRUZZO | 1 | 4 | agroambiente.regione.abruzzo.it |
| FRIULI-VENEZIA GIULIA | 1 | 4 | **vivairauscedo.com** |
| LOMBARDIA | 1 | 25 | asipo.it |
| MARCHE | 1 | 4 | amap.marche.it |
| SARDEGNA | 1 | 7 | laore.powerappsportals.com |
| TOSCANA | 1 | 15 | lamma.toscana.it |
| UMBRIA | 1 | 14 | agronomiforestaliumbria.it |
| **CALABRIA** | **0** | 7 | — |
| **CAMPANIA** | **0** | 7 | — |
| **MOLISE** | **0** | 2 | — |
| **VALLE D'AOSTA** | **0** | 1 | — |

**U · `REGIONS_WITH_GAPS` = 4:** Calabria, Campania, Molise e Valle d'Aosta
ficaram sem nenhuma fonte **nova de classe A**. Nenhuma foi preenchida com fonte
fraca para a tabela ficar bonita.

Na Valle d'Aosta a resposta honesta é mais fina: a região tem **uma** fonte forte
(o Institut Agricole Régional), e ela **já estava no acervo**. A região não está
por descobrir — está coberta por uma fonte só, o que é diferente.

---

## 3 · ONDE ESTÁ A INFORMAÇÃO BOA NA ITÁLIA?

Resultado real da medição, em palavras simples.

### O padrão que se repete em quase toda região

Onde há informação boa, há quase sempre **três camadas ligadas**:

```
quem MEDE          → estação agrometeo (ARPA regional, ou serviço próprio)
quem INTERPRETA    → serviço fitossanitário, que vira medida em boletim
quem LEVA AO CAMPO → consórcio, cooperativa, OP ou técnico de associação
```

Onde as três existem e se falam, a região é forte. Onde falta a terceira, o
boletim existe e ninguém o lê.

### Região por região

**EMILIA-ROMAGNA — a mais densa de Itália.** É a única região onde o boletim de
produção integrada é escrito por **consórcios fitossanitários provinciais**
(Piacenza, Parma, Reggio Emilia, Modena) e não só pela região. A medição deu-lhe
14 marcas de informação própria numa página — o valor mais alto de toda a
pesquisa. Some-se o Consorzio CER (dono técnico do conselho de rega IRRINET), a
ARPAE, a Borsa Merci de Bolonha, o CRPV, a RiNova e a Universidade Cattolica em
Piacenza.

**PIEMONTE — a região onde a rede é visível.** O *Osservatorio Cimice Asiatica*
senta à mesma mesa a universidade (DISAFA), o serviço fitossanitário, a
Fondazione Agrion, a Coldiretti de Cuneo e a Ferrero. Não é uma fonte: é uma
rede, e aparece no grafo como tal. Mais: IRES + Ente Nazionale Risi contam
esporos de brusone em campos-espia.

**LOMBARDIA — onde o modelo decide.** Boletim de brusone do arroz **diário**, por
comune, calculado com o modelo WARM pela Cassandra Tech (spin-off da
Universidade de Milão) e pelo CNR-IREA. Também o ERSAF, com as armadilhas de
Popillia japonica.

**TRENTINO-ALTO ADIGE — o melhor conselho de campo do país, e é privado.** O
Südtiroler Beratungsring publica ~50 circulares por ano só para a maçã e 15 para
a vinha, mais uma revista mensal, e diz-se a maior organização privada de
consultoria fruti-vitícola do mundo. Ao lado: a Fondazione Edmund Mach (Trento) e
o Versuchszentrum Laimburg (Bolzano) — este último **em alemão**, e foi por isso
que o meu próprio filtro o recusou antes de eu corrigir à mão.

**VENETO — informação que chega por e-mail e SMS desde 2010.** O *Bollettino
Colture Erbacee* da Veneto Agricoltura junta ARPAV, o fitossanitário regional, a
Universidade de Pádua (TeSAF e DAFNAE) e a HORTA srl, e usa a rede das escolas
agrárias do Veneto e do Friuli como pontos de observação.

**FRIULI-VENEZIA GIULIA — onde nasce a videira que o resto plantará.** Os Vivai
Cooperativi Rauscedo: 80 milhões de bacelos por ano, 19 hectares de vinha
experimental com 612 clones, 450 microvinificações anuais. Mais o ERSA, com
boletim por cultura e canal Telegram.

**LIGURIA — a região da flor, e ninguém no acervo a cobria.** Flornews Liguria
(do distrito florovivaístico) publica secções fixas de agrometeo e de avisos
fitossanitários; o CeRSAA de Albenga faz experimentação e autocontrolo; o
Istituto Regionale per la Floricoltura de Sanremo é laboratório **oficial** de
análise fitopatológica.

**TOSCANA — o boletim que chega por WhatsApp.** O portal AgroAmbiente.info do
serviço fitossanitário manda alerta por e-mail, SMS, WhatsApp e Telegram para
mosca da azeitona, tignoletta, peronospora e *Scaphoideus titanus* — e tem
"monitoramento participado", em que o técnico de associação insere dado do campo
pela app. Ao lado, o Consorzio LaMMA para o tempo.

**UMBRIA — a surpresa da pesquisa.** Quem publica boletim de olivo e vite não é
só a região: é **a Federação dos agrónomos**. Uma ordem profissional que produz,
não apenas representa. Classe de fonte que o acervo não tinha.

**MARCHE — agrometeo por província.** O AMAP (ex-ASSAM) escreve notiziario
agrometeorológico personalizado por província, e publica boletim de nitratos e
estimativa de rega. E mantém opúsculos de prova varietal de cereais de três em
três anos.

**LAZIO — a informação vem de uma organização de produtores.** Não da região: da
**OP Latium**, que publica boletim semanal de luta guiada à mosca da azeitona
para ~10.000 sócios, com substância ativa indicada, em parceria com o serviço
fitossanitário, o CREA e a ARSIAL.

**ABRUZZO — boletim com aplicação própria no telemóvel.** O AgroAmbiente Abruzzo
publica boletim de defesa integrada e mostra as capturas das armadilhas dentro
de uma app.

**PUGLIA — onde está a pesquisa que o país inteiro acompanha.** O CRSFA "Basile
Caramia" em Locorotondo e o CNR-IPSP de Bari são o centro da Xylella. A Assoproli
publica **dois** boletins por semana para a azeitona, com dados por comune. E a
Borsa Merci de Foggia cota cereais semanalmente — com uma ressalva que importa: a
cotação do grão duro nacional está **suspensa desde 01/04/2026** por causa da CUN.

**BASILICATA — pouca instituição, uma voz forte.** A ALSIA faz o boletim, o
agrometeo (44 estações) e a revista *Agrifoglio*. E o agrónomo Vito Vitelli, de
Policoro, com 306 vídeos e um blogue vivo de 2013 a 2026, é hoje uma das vozes
técnicas mais ouvidas da fruticultura do Sul.

**CALABRIA — boletim semanal em oito zonas, e duas culturas que mais ninguém
cobre.** A ARSAC divide a região em 8 zonas climáticas e publica para agrumes,
olivo, vinha e kiwi. O Consorzio del Bergamotto (criado por decreto de 1946) faz
assistência técnica para uma cultura que nenhuma outra fonte do acervo toca.

**SICILIA — dois observatórios oficiais e uma pesquisa concentrada.** Os
Osservatori per le Malattie delle Piante de Acireale e de Palermo fazem
diagnóstico oficial; o Di3A de Catania concentra a patologia dos citrinos
(mal secco, tristeza); o SIAS faz o agrometeo. E o mensário *Agrisicilia* dá voz
local.

**SARDEGNA — 300 estações e um boletim numa plataforma alugada.** A ARPAS opera
mais de 300 estações e o boletim fenológico; a Laore escreve os notiziari
fitossanitários por balcão territorial. **Aviso:** o boletim agrometeo da Laore
vive num endereço da Microsoft (`powerappsportals.com`) — se o contrato de
plataforma mudar, o endereço morre.

**MOLISE e VALLE D'AOSTA — as duas mais pobres, e por razões diferentes.** No
Molise há o serviço fitossanitário (em Larino) e a ARSARP com agrometeo, mas a
continuidade é frágil: uma avaliação independente de 2023 dava os boletins como
parados em abril de 2022, e a página de 2026 mostra boletins — há divergência, e
ela não está resolvida. Na Valle d'Aosta há **uma** instituição que faz quase
tudo — o Institut Agricole Régional — mais um serviço agrometeo com canal
Telegram e o Consorzio Vini. A flavescência dourada é hoje endémica lá.

---

## 4 · QUEM PODE ALIMENTAR O SINTONIA — por função, não por ranking

Isto **não** é uma classificação universal. É uma lista de quem entrega o quê.

### quem informa sobre praga e doença
Os 20 serviços fitossanitários regionais — e o achado mais eficiente da missão
foi o diretório da Fitogest que dá **uma rota de boletim por região, para as
20 regiões, numa página só**. Acima deles em detalhe: os quatro consórcios
fitossanitários provinciais da Emilia, a ARSAC (8 zonas), o Beratungsring
(50 circulares/ano) e a Agrea (ensaios de eficácia próprios).

### quem informa sobre clima, água e solo
ARPA regionais · o SAR da Sardenha (300+ estações) · o SAL da Basilicata
(44 estações) · o Consorzio LaMMA na Toscana · **a HORTA srl, que declara operar
a maior rede agrometeorológica de Itália** · o IRRIFRAME da ANBI/CER para o
conselho de rega · o Drought Central para a seca.

### quem informa sobre cultura e produção
CSO Italy (monitoramento **semanal** de colheita e de stocks) · Ente Nazionale
Risi · Veneto Agricoltura e AMAP para prova varietal · Vivai Cooperativi Rauscedo
para a variedade que vem · SINAB para o biológico nacional.

### quem informa sobre ciência
CREA (por centro temático) · CNR (IPSP, IBE, ISPA, IREA, IMAA) · CRSFA Basile
Caramia · Fondazione Edmund Mach · Versuchszentrum Laimburg · Agroinnova ·
Universidade Cattolica de Piacenza · SIPaV, SIRFI, AIPP, AIAM, Accademia dei
Georgofili · a base de dados dos Gruppi Operativi no Innovarurale.

### quem informa sobre pesquisadores (T6)
**59 pessoas novas**, com cultura e problema ao lado de cada nome, na folha
`PEOPLE`. Exemplos: Donato Boscia e Maria Saponari (Xylella, CNR-IPSP Bari) ·
Lara Maistrello (cimice asiática, UNIMORE) · Maurizio Sattin e Laura Scarabel
(resistência a herbicidas, GIRE) · Vittorio Rossi e Tito Caffi (modelos de
peronospora, UCSC) · Luciana Tavella e Alberto Alma (DISAFA) · Claudio Ioriatti
e Gianfranco Anfora (FEM/C3A) · Santa Olga Cacciola e Vittoria Catara (citrinos,
Catania) · Lætitia Borgo e Simone Silvestri (brusone, Ente Nazionale Risi).

### quem está perto de quem aplica (T7)
Os *Centri Assistenza Agricola* da CIA · as 15 federações regionais da CIA · as
Confagricoltura provinciais · os 43 *Condifesa* do sistema Asnacodi (alguns
publicam boletim) · as OP com serviço técnico real (APOC Salerno: 2.000+ visitas
por ano; Apoconerpo: 1.200 ha de tomate resistente) · a Federação dos agrónomos
da Umbria · o AKIS da Lombardia · o InnovaMarche.

### quem informa sobre produtores e voz de campo (T8)
Vito Vitelli (agrónomo, Basilicata) · Matt The Farmer (Brescia) · Gomiero Farm
(Pádua) · Maria Pezone (130 ha de alface e melão, Campania) · Filips Country
(Verona) · o podcast *Madre Terra* (Radio 24, semanal) · *Terra di Denari*
(AgroNotizie).

### quem informa sobre mercado (T10)
ISMEA e ISMEA Mercati · as 16 Borse Merci camerais (Bolonha na quinta-feira,
Foggia semanal) · a BMTI · o CSO Italy · a Nomisma · a Areté · a Fondazione
Qualivita.

### quem informa sobre concorrentes (T9)
Sipcam (o maior sinal agrícola medido em toda a pesquisa: 32 palavras do ofício
numa página) · Diachem (que mantém podcast próprio) · Ascenza · K-Adriatica ·
ILSA · e o padrão que vale registar: **a comunicação de um concorrente é
informação — sobre ele.** Não foi recusada; foi marcada T9.

---

## 5 · O QUE EU FIZ PARA NÃO ME ENGANAR

### Auditoria manual — 228 decisões à mão

Abri e julguei 228 linhas: **todas** as A da máquina, uma amostra larga de B, os
REJECT com sinal agrícola alto (à procura de falso negativo) e os HOLD com sinal
alto. **Em 62 delas mudei a classe da máquina.** As duas versões ficam na
planilha, separadas pela palavra `LEITURA HUMANA`.

Mais 217 hosts passaram por **varredura por regra escrita** (R1 a R9), cada regra
nascida de um caso que eu tinha visto à mão. Regra é auditável; palpite não. A
marca `AUDITADA_POR_REGRA` distingue as duas coisas.

### Segunda prova — 32 fontes por caminho independente

Não repeti a primeira medição: fui ao **arquivo de boletins**, não à homepage.

```
CONFIRMED  21     DIVERGED  3     UNKNOWN  8
```

As três divergentes perderam A/B, como manda a regra:
`fitosanitario.umbriagricoltura.it` (material mais novo de 2024),
`difesaintegratabasilicata.jimdofree.com` (2020) e `agrometeopuglia.it` (2018 —
e aqui pode ser o endereço errado, não a fonte morta).

**E o teste tem um furo que eu medi.** Declarei dois controles negativos **antes**
de medir — um portal de programação encerrada e uma página de login — e esperava
que falhassem. **Os dois passaram.** Logo o teste prova *"existe uma data recente
nesta página"*, e **não** *"esta fonte publicou recentemente"*: uma data de prazo
ou de rodapé passa igual. Falso positivo nos controles: **2 de 2**. `CONFIRMED`
por este método é evidência **fraca**.

### Red team — 24 ataques, cada um com controle positivo

21 detectores funcionam, 1 está **ausente**, 2 são ressalvas e não filtros.

O controle positivo mais forte: os dois maiores alcances de toda a pesquisa —
Spicy Moustache (4,5 milhões, e é uma horta urbana **em Londres**) e Giovanni
Storti (1 milhão, e é ator de comédia) — estão em **REJECT**. O único canal em A
tem 15 mil seguidores. **300 vezes menos.**

Outros controles que funcionaram: inseri Luciana Tavella **duas vezes** de
propósito e a segunda saiu marcada `TRUE_DUPLICATE` — e foi esse controle que
mostrou que o dedupe de pessoas dentro da própria rodada **faltava**; foi
acrescentado depois.

**O detector ausente:** não sei detetar **domínio reaproveitado**. Isso exigiria
histórico (WHOIS, arquivo da web) e nenhum foi consultado. É um buraco declarado.

### Três erros meus, apanhados e corrigidos no meio da missão

1. **A raiz encurtada fazia fonte conhecida parecer nova.** O agrupador cortava
   `agricoltura.regione.emilia-romagna.it` para `emilia-romagna.it`. Corrigido:
   o dedupe passou a comparar URL, **host completo** e só então a raiz.
2. **O filtro de italianidade cegava em alemão e em inglês.** Recusou o
   Versuchszentrum Laimburg (alemão) e o *Italian Journal of Agrometeorology*
   (inglês) — duas fontes italianas de primeira linha. Corrigidas à mão.
3. **A auditoria por host pingava em linhas de pessoa.** Dois dirigentes do
   Consorzio Vini Valle d'Aosta ficaram com a classe de um endereço. Corrigido:
   a chave depende do tipo de registo.

### E um quarto, que eu tentei três vezes e desisti — de propósito

O campo `TIPO` do CSV é a **gaveta** de `fonte_nova.py` (nove valores). Tentei
deduzi-la do texto da página e errei três vezes, cada uma para um lado:

| tentativa | o que a palavra fez | resultado errado |
|---|---|---|
| 1ª | `servizio fitosanitario` **mencionado** na página | a HORTA srl, empresa privada, virou `BASE_OFICIAL` |
| 2ª | `notizie` na página | a SNPA, rede nacional das ARPA, virou `IMPRENSA` |
| 3ª | `università` **citada** | o Consorzio del Bergamotto virou `CIENCIA` |

**A lição:** o texto de uma página diz **de que ela fala**, não **quem ela é**.

Na versão final o `TIPO` sai de três coisas, nesta ordem — (1) o **domínio**,
quando ele prova (um `.gov.it` é de facto público); (2) a **minha leitura
humana**, quando existe; (3) **`OUTRO`**, com a dúvida escrita na coluna `NOTA` e
a lista do que a máquina detetou.

Resultado: **99 das 217 linhas dizem `TIPO = OUTRO`**. Quem registar escolhe a
gaveta. Uma gaveta confiantemente errada é pior do que uma gaveta que diz
"escolha você".

⚠️ Note a assimetria, e ela é deliberada: para a **região** recusei usar o
domínio (`agrisicilia.it` pode ser de Milão); para o **tipo de dono** o domínio é
prova boa. As duas coisas não são a mesma.

---

## 6 · O QUE ESTA MISSÃO **NÃO** PROVOU

Escrito para que ninguém herde estes números como se fossem mais do que são.

- **Nenhuma afiliação de pesquisador foi verificada** num perfil institucional.
  As 60 linhas de pessoas vêm de fontes que as citam — não de uma página da
  própria instituição. Todas carregam a limitação escrita.
- **Nenhum exemplo de conteúdo foi guardado.** Há endereço e prova de que abriu;
  não há ficheiro. Isto é exatamente o degrau que separa *candidata* de *fonte
  registada*, e ele não foi subido.
- **71 linhas de classe B ninguém abriu.** A classe é da máquina, e cada uma diz
  isso na própria linha.
- **1.004 linhas ficaram com `REGION = NÃO SEI`.** Preferi o buraco visível a
  uma coluna cheia e errada.
- **A frescura das A/B apoia-se numa data vista na página**, e o teste que a mede
  tem o furo declarado acima.
- **Domínio reaproveitado não é detetável** por este método.
- **Fonte atrás de registo devolve a porta, não o conteúdo** (Beratungsring,
  ALSIA, consultoria por subscrição).

---

## 7 · PROVA DE QUE NENHUMA COLETA RODOU

| | |
|---|---|
| `COLLECTION_RUNS_CREATED` | **0** |
| `RAW_CREATED` | **0** |
| `DERIVED_CREATED` | **0** |
| `STRUCTURED_CREATED` | **0** |
| `ADMISSION_CREATED` | **0** |
| `WAITING_ROOM_DELTA` | **0** |
| `SOURCE_ID` criados | **0** |
| `DOCUMENT_ID` criados | **0** |
| Atlas alterado | **NÃO** |
| fila `candidatas/FONTES-CANDIDATAS.json` | **0 candidatas — continua vazia** |

Medido por `git status` em `guarda/`, `coleta/`, `admissao/`, `data/samples/` e
`docs/fontes/`: **zero ficheiros alterados** em todas. O CSV está pronto e
**não foi executado**. Ficheiro pronto não é ingestão feita.

### Regressão

| | baseline (`f437ff11`, antes de eu tocar) | agora |
|---|---|---|
| `P1_SEM_DRIFT` | **FAIL** | **PASS** |
| `P9_CODIGO_DECLARADO` | **FAIL** (`.github/workflows/scrap-social.yml`) | **FAIL** — mesmo ficheiro, mesma causa |
| restantes 10 provas | PASS | PASS |
| `test_system_map.py` | — | **PASS** (todas) |

**Nenhuma falha nova.** A falha que resta é **anterior a esta missão** e a causa
não é minha: um workflow (`scrap-social.yml`) que alguém acrescentou sem
declarar. Não o declarei porque não é meu e declarar arquitetura alheia sem
entender o que ela faz é pior do que deixar o portão vermelho a apontar para o
problema real.

Os nove scripts desta missão **estão declarados** no System Map, na peça nova
`C-IT-DESCOBERTA-PROFUNDA`, dentro da zona `Z-CANDIDATAS`.

---

## 8 · PRÓXIMO PASSO — recomendação, não execução

```
217 candidatas A + B
   → revisão final por gente (abrir, olhar, guardar um exemplo real)
      → registar como FONTES no Atlas, com SOURCE_ID
```

Ordem que eu recomendaria, e o motivo:

1. **as 69 com recorrência `HIGH` e proximidade `PRIMARY`** primeiro — são
   boletins e cotações, entregam informação nova toda semana;
2. **os quatro consórcios fitossanitários provinciais da Emilia** — mesma
   família, mesma rota, uma decisão resolve quatro;
3. **a HORTA srl** — porque está no meio do caminho entre a ciência e a decisão
   de milhares de hectares, e não estava no acervo;
4. **as três divergentes** — resolver se o endereço está errado ou a fonte
   parada, antes de decidir;
5. **as quatro regiões sem A** (Calabria, Campania, Molise, Valle d'Aosta) — uma
   rodada dirigida a mais, porque as rodadas 2 e 3 provaram que **ainda há o que
   achar**.

### Saturação — medida, não inventada

| rodada | o que fez | fontes fortes novas |
|---|---|---|
| 1 | grafo de ligações, 493 sementes | a maior parte das 217 |
| 2 | busca por cultura + problema, 30 consultas | ~40, quase todas pessoas e canais |
| 3 | volta dirigida às 6 regiões fracas, 8 consultas | ~25 hosts, **3 deles classe A** |

**As regiões fracas NÃO atingiram saturação.** A terceira rodada ainda devolveu
classe A (CRSFA na Puglia, HORTA nacional, Laimburg no Alto Adige). Conclusão
que vale guardar: **o grafo de ligações é enviesado** para regiões com tecido
institucional denso — zero fonte numa região pequena depois de uma rodada de
grafo **não é sinal de ausência**, é sinal de que falta a rodada dirigida.

---

## VEREDITO

```
VEREDITO = PASS
```

As 20 regiões foram pesquisadas, os 12 territórios cobertos, 217 fontes novas
fortes separadas de 2.813 possibilidades, 228 linhas lidas à mão, 32 verificadas
por caminho independente, 24 ataques de red team executados com controle
positivo — e nenhuma coleta rodou. As fraquezas estão escritas, não escondidas:
a afiliação dos pesquisadores não foi verificada, 71 linhas de B ninguém abriu, e
o teste de frescura falhou nos dois controles negativos que eu próprio declarei.

---

**HARD STOP.** Nada foi registado no Atlas, nenhum `SOURCE_ID` foi criado,
nenhum coletor foi escrito, nenhuma corrida foi aberta, a Sala de Espera não
mudou, a Intelligence não correu, o Portal não foi tocado.
