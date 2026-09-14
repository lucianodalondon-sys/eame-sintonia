# BURACO DE MATÉRIA-PRIMA, FERRAMENTA POR FERRAMENTA — ITÁLIA

**Data:** 2026-09-14 · **Branch:** `claude/italy-agricultural-sources-discovery-dfba81`
· **Base medida:** `191dbda4` · **Entrega:**
[`ITALY-SOURCE-GAP-BY-TOOL-2026-09-14.xlsx`](ITALY-SOURCE-GAP-BY-TOOL-2026-09-14.xlsx)
(13 folhas)

> **A pergunta:** que informação **bruta** precisa existir **antes** da
> Intelligence para cada ferramenta funcionar bem, e quem na Itália produz
> essa informação?

---

## O QUE MUDOU NA RESPOSTA — leia isto primeiro

Quatro achados mudaram a **resposta**, não acrescentaram fonte. Valem mais do
que as outras dez buscas juntas:

| achado | consequência |
|---|---|
| **Os dados das provas GEP são reservados por lei** — propriedade de quem as encomenda, não são publicados | «ensaio de campo com resultado» **não é gap de fonte, é gap de ACESSO**. Nenhuma coleta o resolve; resolve-se por contrato |
| **O `coeweb.istat.it` fechou em 30/09/2025** e passou para `esploradati.istat.it/coeweb` | o acervo aponta para uma **rota morta**, e rota encerrada devolve página, não erro |
| **A rede de recolha do índice ISMEA foi revista em 01/2025** | os índices mensais **deixam de ser comparáveis** com o ano anterior; a base muda para 2020 em 01/01/2026. A variação 2024→2025 é artefacto de método |
| **Não existe lista central de agrónomos liberais que publiquem boletim próprio** | o buraco de VOICES **não se enche com mais canais sociais**. Quem tem região, papel e data é o boletim técnico assinado — e esse é técnico institucional, não produtor |

---

## A · A PERGUNTA, RESPONDIDA EM UMA LINHA

As 9 ferramentas de Intelligence precisam de **72 matérias-primas distintas**.
O casco tem **15 críticas em falta**. Das 72, **38 têm fonte nomeada que as
entrega**, **18 têm fonte plausível mas campo não visto**, **7 não se fecham com
fonte nenhuma**, **1 é impedimento legal** e **2 têm fonte forte que responde a
outra pergunta**.

## B · AS FERRAMENTAS FORAM MEDIDAS, NÃO COPIADAS DO PEDIDO

O pedido trazia uma lista. Não foi usada como verdade. A medição foi na zona
`Z-TELAS` do System Map:

```
11 telas existem no portal
 -9 são Intelligence          <- as desta missão
 -2 NÃO são: Archivio e Registro delle fonti (ficaram fora, como pedido)
```

E a origem do dado de cada uma, medida:

```
por_origem = MISTURA 6 · NAO SEI 4 · REAL 1
```

**Uma de onze desenha-se só com dado real.** Quatro não têm contrato nenhum.
E os ficheiros de especificação `future`, `signal`, `voci` e `field` **são um
único documento com quatro nomes** (sha256 `10bc784976972a6d`).

| TOOL | tela no portal | matérias-primas | contrato? |
|---|---|---|---|
| `WINDOWS` | Finestre Colturali | 12 | sim |
| `PORTFOLIO` | Portafoglio | 11 | sim |
| `MARKET` | Mercato | 10 | sim |
| `SCIENCE` | Scienza | 8 | sim |
| `COMPETITORS` | Concorrenti | 8 | sim |
| `RADAR` | Opportunity Radar | 8 (todas herdadas) | sim |
| `VOICES` | Voci dal Campo | 7 | não |
| `FUTURE` | Segnali Futuri | 6 | não |
| `FIELD_NET` | Rete di Campo | 2 | não |

## C · AS 15 CRÍTICAS, COM A MEDIÇÃO QUE AS PROVA

| TOOL | matéria-prima que falta | medição | veredito à mão |
|---|---|---|---|
| WINDOWS | fase fenológica | `CROP_STAGE 0/29` | **STRONG** |
| WINDOWS | rastreabilidade da janela | `SOURCE_IDS 0/29` | não é gap de fonte |
| MARKET | produção, área, rendimento | coluna ausente | **STRONG** |
| PORTFOLIO | carência (PHI) e n.º máx. aplicações | `interval 15/219 (7%)` · `maxApp 0/219` | **STRONG** |
| PORTFOLIO | alteração de autorização | ausente | **STRONG** |
| PORTFOLIO | ligação produto × janela | `PRODUCT_MATCHES 0/29` | não é gap de fonte |
| VOICES | região da voz | `0/17` | **forte, mas troca a voz** |
| VOICES | papel de quem fala | `0/17` | **STRONG** |
| VOICES | data da observação | `0/17` | **forte, mas troca a voz** |
| FUTURE | primeira deteção de praga | ausente | **STRONG** |
| FIELD_NET | relato da rede comercial | 18 registos, todos `SYNTHETIC_DEMO` | não é gap de fonte |
| RADAR ×4 | entradas herdadas | herdado | = ferramenta de origem |

## D · GRAVIDADE SAI DO CAMPO MEDIDO, NUNCA DA CONTAGEM DE CANDIDATAS

```
CRITICAL 15 · HIGH 29 · MEDIUM 19 · LOW 9
```

**Isto foi consertado a meio da missão.** A primeira versão marcava **62 de 72
como `STRONG_SOURCE_EXISTS`**, incluindo «observação de campo» como `LOW`
quando o contrato diz `0/29`. Ter candidata é **promessa**; ter campo é
**capacidade**. Agora a gravidade lê-se no enchimento medido, e o casamento por
palavra só **propõe**.

Prova de que a correção pegou: **4 das 15 críticas têm 5 ou mais donos
propostos e continuam CRITICAL.**

## E · O CASAMENTO AUTOMÁTICO ERRA, E O ERRO ESTÁ ESCRITO AO LADO

A folha `CURRENT_COVERAGE` traz o veredito automático **e** o veredito à mão,
lado a lado, de propósito. Quatro propostas derrubadas:

| matéria-prima | o automático propôs | por que caiu |
|---|---|---|
| fase fenológica | *Données ouvertes du catalogue E-Phy* | registo **francês** de fitossanitários |
| voz de campo (Radar) | *Centro Veterinario San Martino* | clínica **veterinária** |
| mecanismo de ação | *Cassandra Tech – Models for change* | nada a ver |
| registo do concorrente | *CELLAR / EU Publications Office* | repositório de atos jurídicos |

E um defeito de estrutura: **lista de palavras vazia deixava passar toda fonte
do território.** «Datas de início e fim da janela» recebia **67 donos fortes**.
Agora, sem palavra, o matcher **cala-se** e diz por quê — e são três motivos
diferentes que não se juntam: `HERDADO`, `NAO_E_GAP_DE_FONTE`,
`NAO_E_PERGUNTA_DE_PALAVRA`. Depois da correção: **15 donos, todos com palavra
provada; zero candidatas sem prova.**

## F · AS 37 FONTES NOVAS

```
classe A 26 · classe B 10 · REJECT como fonte de dado 1
37 fontes -> 109 ligações -> 48 matérias-primas distintas
```

Classe A exige as dez coisas: identidade, dono, rota, **exemplo real visto**, o
que produz, que necessidade alimenta, que ferramenta serve, âmbito, recorrência
e evidência. Falta uma → B.

### As que fecham crítico

| fonte | dono | o que entrega |
|---|---|---|
| [`reterurale.it/bollettinofeno`](https://www.reterurale.it/bollettinofeno) | RRN / MASAF | fenologia **BBCH** nacional |
| [ARSAC](https://www.arsacweb.it/bollettino-agrometeorologico-e-fitosanitario-agrumi-olivo-e-vite/) | Regione Calabria | fenologia em **8 áreas climaticamente homogéneas**, validade semanal datada |
| [CAAR Liguria](https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/agrometeo-caar/bollettino-di-olivicoltura.html) | Regione Liguria | BBCH de olivo em **olivais da rede de monitorização**, por província |
| [LaMMA](https://www.lamma.toscana.it/previ/ita/agrometeo/) | Consorzio LaMMA | estado fenológico **por província**, com a heterogeneidade escrita |
| [meteo.regione.marche.it](https://meteo.regione.marche.it/) | ASSAM Marche | **código BBCH numérico**: melo 75-77, pero 76-81, vite 79 |
| [ISTAT `DCSP_COLTIVAZIONI`](https://esploradati.istat.it/SDMXWS/rest/) | ISTAT | superfície, produção e rendimento por região, província e altimetria |
| [Fitogest](https://fitogest.imagelinenetwork.com/it/banca-dati-e-portale/) | Image Line | a mesma população de produtos, **pesquisável por tempo di carenza** |
| [fitosanitari.salute.gov.it](https://www.fitosanitari.salute.gov.it/) | Ministero della Salute | ~16.500 produtos, atualização **diária**, descarga integral |
| [protezionedellepiante.it](https://www.protezionedellepiante.it/) | Servizio Fitosanitario Nazionale | **primeira deteção** oficial, vigilância, barreiras |
| [convegno de Bolonha](https://agricoltura.regione.emilia-romagna.it/fitosanitario/incontri-e-convegni/prodotti-fitosanitari-novita-2026) | Regione Emilia-Romagna + as empresas | alteração de autorização **declarada pelo próprio titular** |
| [SCIA](https://scia.isprambiente.it/dati-e-indicatori/) | ISPRA | série climática por estação, **graus-dia**, grelha interpolada |
| [Arpae ERG5](https://webbook.arpae.it/clima/) | Arpae Emilia-Romagna | **anomalia** de soma de graus-dia, limiar 10 °C, média 2001–2020, grelha 5 km |
| [Forum Fitoiatrico](https://www.condifesatvb.it/forum-fitoiatrico/) | Condifesa Treviso-Belluno | pessoa + papel + empresa + região + data, de uma vez |

## G · UMA SOURCE, VÁRIOS USOS — e onde isso se lê

`NEW_SOURCES` = **uma linha por fonte**. `SOURCE_TO_TOOL` = **uma linha por
ligação**. As 37 fontes produzem **109 ligações (fator 2,9×)**. Quem contar
linhas em `SOURCE_TO_TOOL` e disser «109 fontes novas» conta a mesma fonte até
oito vezes.

A que serve mais ferramentas é o **Forum Fitoiatrico**: 8 matérias-primas em 4
ferramentas.

## H · O OPPORTUNITY RADAR NÃO GANHOU NENHUMA FONTE, E ISSO ESTÁ CERTO

Não se procurou «fonte para o Radar». Ele é **cruzamento** das outras camadas.
A folha `RADAR_INPUTS` tem 8 entradas, cada uma a apontar para a camada que a
produz. **Zero fontes servem só o Radar**, e as 6 entradas verdadeiras estão
todas marcadas `HERDADO`.

**A regra dura: o Radar nunca é melhor do que a sua entrada mais fraca.** E a
mais fraca é VOICES — com `0/17` em região, papel e data, o cruzamento «voz +
janela na mesma região e no mesmo momento» **é impossível por construção**, por
melhor que o Radar esteja escrito.

## I · REGIÃO — e a matriz que mentia

```
COBERTA 14 · FRACA 4 · SEM FONTE REGIONAL 2
```

Sem fonte regional de fenologia: **Basilicata** e **Valle d'Aosta**.
Fracas (uma só): **Abruzzo, Campania, Friuli-Venezia Giulia, Molise**.

**A primeira versão desta folha dizia 20 de 20 cobertas.** Contava as 2 fontes
nacionais como se cobrissem cada região — e a fenologia muda com altitude e
distância ao mar (o próprio Abruzzo mede **~2 semanas de atraso** acima de
400 m ou a mais de 40 km da costa). Agora as duas contas vivem em colunas
separadas, e o estado decide-se pela regional.

Também caiu um inflacionamento herdado: **Lazio passou de 32 para 15** quando a
região deixou de ser lida na prosa e passou a sair só do campo `REGION` medido.
Uma das 32 chamava-se *Toscana Notizie*. **Mencionar o Lazio não é ser do
Lazio.**

## J · CULTURA — cinco das dez ficaram de fora, e a razão é honesta

| cultura | janelas | fontes novas que a nomeiam |
|---|---|---|
| Grapevine | 5 | 8 |
| Olive | 3 | 4 |
| Apple | 3 | 1 |
| Rice | 2 | 1 |
| Sugar Beet | 2 | 1 |
| **Wheat · Durum Wheat · Maize · Soybean · Tomato** | 14 | **0** |

**Isto não é ausência de fonte em Itália — é ausência de busca.** As consultas
foram à vite, ao olivo, aos agrumes e aos frutos de pomo. **14 das 29 janelas
canónicas são de culturas arvenses e de tomate, e nenhuma busca foi dirigida a
elas.** Fica declarado para quem herdar a lista.

E caiu outro número falso: **Maize passou de 6 para 0.** A palavra italiana
para milho é *mais*, e a minha descrição das fontes está em português — «vai
*mais* longe», «*mais* ~300 leituras», «retoma vegetativa *mais* tardia»
contavam como milho. Seis de seis eram falsos.

## K · PESSOAS — por papel, nunca por alcance

| papel | quantas | onde |
|---|---|---|
| técnico de empresa concorrente | **7** | convegno de Bolonha · Forum Fitoiatrico |
| responsável de serviço público | 3 | protezionedellepiante.it · convegno · Forum |
| técnico de associação/sociedade | 2 | convegno · Giornate Fitopatologiche |
| **produtor agrícola com região e data** | **0** | — |

«PESSOA do concorrente» passou de `NO_SOURCE` a **STRONG**: sete pessoas
nomeadas com empresa — Mattia Fumagalli (Syngenta), Sara Ciofini (Corteva),
Mirko Valente (BASF), Silvano Locardi (Bayer), Marco Pravisano (Syngenta),
Marco Grandin (Bayer), Giorgio Fioretti (BASF).

⚠️ **A ADAMA está na lista de participantes do Forum Fitoiatrico.** Ler isso
como «atividade de concorrente» obriga a excluir a própria casa do cálculo.

E a linha que importa é a última: **zero**.

## L · OS 7 GAPS QUE NÃO SE FECHAM COM FONTE NENHUMA

Coletar mais não conserta nenhum destes:

| gap | por que não é de fonte |
|---|---|
| rastreabilidade da janela (`SOURCE_IDS 0/29`) | as fontes existem; **ninguém anotou** qual sustentou qual janela |
| ligação produto × janela (`0/29`) | **join interno** entre 219 produtos e 29 janelas, ambos em casa |
| relato da rede comercial (18 × `SYNTHETIC_DEMO`) | é **dado próprio da ADAMA**. Procurar fora o que está dentro |
| vocabulário único de cultura | o nome chega em **seis vocabulários** que não se falam; qual manda é decisão da casa |
| identidade única de caso | identificador do SINTONIA. Nenhum italiano o publica |
| volume de vozes / volume de sinais | são contagens, não tópicos |

E dois que são de **extração**, não de fonte: dose e momento de aplicação vivem
no **PDF do rótulo** — que o projeto já sabe abrir.

## M · O GAP QUE É LEGAL, NÃO TÉCNICO

Seis centros de saggio GEP italianos identificados — Agrea, Sagea, AgriSearch,
Agro Services, Agritec, Repros. Fazem ensaio oficial de eficácia. **E os dados
são reservados: propriedade da empresa que os encomenda, não são publicados.**

Ficam no acervo como **rede de pessoas (T8)**, não como fonte de resultado. É a
única linha classificada `REJECT_COMO_FONTE_DE_DADO`, e a razão está escrita.

O caminho divulgável: provas demonstrativas dos serviços regionais, atas das
Giornate Fitopatologiche e da AIPP/SIPaV, e a base de rótulos do Ministero.

## N · DUAS COISAS QUE NUNCA SE MISTURAM

**Substância ativa aprovada na UE ≠ produto autorizado em Itália.** A mesma
substância pode estar aprovada e não ter produto nacional. Juntar as duas
colunas inventa um portfólio.

E o mecanismo que torna a base europeia um **sinal de futuro** está na lei:
Reg. (CE) 1107/2009 **art. 15** — o pedido de renovação entra **três anos**
antes de expirar. ⚠️ Mas **o prazo mudou**: o pacote Omnibus altera o **art.
43** — pedido de renovação de *autorização* passa a até **9 meses** antes de
expirar, ou **3 meses** se a substância tiver aprovação limitada. Calcular pela
regra antiga dá a data errada.

## O · CAPACIDADE NÃO É EXISTÊNCIA

O ISMEA **não** faz recolha periódica de existências por região. O que tem é o
**censo de estruturas de armazenamento** de cereais: ~1.200 centros, >11 Mt,
55% silos e 45% armazém. **Isso é capacidade.** Um silo vazio de 10.000 t conta
igual a um cheio.

A fonte certa para giacenze por região é a **declaração obrigatória no registo
telemático** — Cantina Italia (SIAN/CREA-MASAF) para o vinho, registo
telemático do azeite (AGEA/SIAN).

E a rede **Ismea–Unione Seminativi** (23 estações, questionário a peritos) é
**expectativa de perito**, declarada provisória pelo próprio ISMEA. Serve a
ferramenta de **sinal**; usá-la como produção mede opinião e chama-lhe colheita.

## P–S · RED TEAM · 12 ATAQUES, 12 OK

Cada ataque mede **duas** vezes: na entrega (espera PASSA) e numa cópia
deliberadamente estragada (espera FALHA). Sem o segundo, «não achei problema»
pode significar «detetor cego».

| # | ataque | resultado |
|---|---|---|
| 1 | fonte que fala mas não entrega o campo | OK — automático nunca escreve STRONG |
| 2 | contar ligação como fonte | OK — 37 distintas → 109 ligações (2,9×) |
| 3 | Radar com família própria | OK — 0 fontes só-do-Radar, 6 entradas HERDADO |
| 4 | nacional vira cobertura regional | OK — contas em colunas separadas |
| 5 | gravidade vinda da contagem | OK — 4 de 15 CRITICAL têm 5+ donos e continuam CRITICAL |
| 6 | zero falso dentro de outro número | OK — `100%` e `10/163` não lidos como zero |
| 7 | território inventado | OK — 9 códigos, todos no Atlas; T13 e T14 recusados |
| 8 | necessidade órfã | OK — 109 ligações, todas existentes |
| 9 | auditoria incompleta | OK — 72/72 com leitura humana |
| 10 | colisão de língua IT/PT | OK — Maize 6 → 0 |
| 11 | sintético contado como real | OK — FIELD_NET fica NENHUM apesar de 18 registos |
| 12 | **folha diz mais do que foi feito** *(caminho independente)* | OK — 4.163 células lidas do XLSX sem importar nenhum módulo |

**O ataque 12 apanhou a entrega na primeira passagem** — e era falso positivo
do meu próprio detetor. Procurava a palavra «ingerido» e apanhou duas frases
que diziam **«não ingerido»**. Um detetor que não lê a negação mede a palavra,
não a afirmação. Agora exige ausência de negação nos 34 caracteres anteriores,
e tem controle de **duas** faces: apanha «foi ingerido», deixa passar «não
ingerido».

## T–W · REGRESSÃO, MAPA E O TESTE QUE ME APANHOU

```
708 testes · 37 falhas (17 failures + 20 errors)
base 191dbda4: 37 falhas
NEW_FAILURE = 0
```

**Uma falha nova apareceu e era minha.** O teste
`test_nenhum_nome_da_deriva_voltou_ao_codigo_vivo`, que eu próprio escrevi na
missão da taxonomia, apanhou `candidatas/italy_gap_auditoria.py` na linha:

```python
"PORTFOLIO · Substancia ativa do produto": (
```

`'Substancia ativa'` está na lista da deriva porque a **lista errada fazia dela
um território**. Mas a substância ativa existe de verdade: é uma **camada
dentro de T4**, e nomear uma matéria-prima com ela é correto.

Renomear o dado para o teste passar teria **piorado o dado para salvar o
teste**. Afiou-se o teste: agora exige um **código T ligado** ao nome da
deriva, e traz controle positivo dentro de si mesmo — prova que continua a
apanhar `"T4": "Substancia ativa"`, `'T10': 'Preco e mercado'`,
`"T11": "Solo e agua"`, e que deixa passar o uso legítimo. O controle ficou
**dentro** do teste existente, para não mexer na contagem de 708.

**System Map:** regenerado pela cadeia manual (`scan_repo` → `scan_sources` →
`generate`). `MAPA=OK · peças=99 · ligações=331`. Peça nova declarada:
`C-IT-GAP-POR-FERRAMENTA` (zona `Z-CANDIDATAS`), com os 8 ficheiros de código
e a planilha.

Validador: **12 de 13 provas passam.** `P9_CODIGO_DECLARADO` reprova por
`.github/workflows/scrap-social.yml` — que foi commitado em `df165da9` e **já
não estava declarado em `191dbda4`**. `PRE_EXISTING_FAILURE`, não desta missão.

## X–AC · O QUE NÃO SE FEZ, E O QUE ISTO NÃO PROVA

```
COLLECTION_RUNS_CREATED = 0      SOURCE_ID_CREATED     = 0
RAW_CREATED             = 0      DOCUMENT_ID_CREATED   = 0
WAITING_ROOM_DELTA      = 0      INTELLIGENCE_RUNS     = 0
PORTAL_CHANGED          = NO     ATLAS_CHANGED         = NO
TAXONOMIA_NOVA          = NO     ARQUITETURA_NOVA      = NO
```

**O que isto não prova:**

- **nenhuma das 37 rotas novas foi aberta por sonda.** A evidência é de busca
  dirigida. **Rota descrita não é rota lida**;
- **nenhum exemplo de conteúdo foi guardado.** Há endereço e descrição — não há
  ficheiro;
- **nenhuma afiliação de pessoa foi verificada** num perfil institucional. As 12
  pessoas vêm de programas e listas de participantes que as nomeiam;
- **5 das 10 culturas do casco não foram pesquisadas** (§J);
- **as 18 linhas `WEAK`** dizem «fonte plausível, campo não visto» — e é isso
  mesmo que querem dizer;
- o modelo local não foi usado como prova em lugar nenhum. **Modelo não é
  prova; a fonte real continua a ser a prova.**

**Dono da taxonomia:** `docs/fontes/ATLAS-DE-FONTES-EAME.md`, via
`_territorios.py`. Os 9 códigos T usados foram validados contra ele. **T13 não
é canónico e não aparece aqui.**

---

## O QUE PERGUNTARAM, EM PALAVRAS SIMPLES

**1 · Que ferramentas o portal tem hoje, de verdade?**
Onze telas. Nove são de Intelligence; o Arquivo e o Registo de fontes não são —
ficaram fora, como pedido. De onze, **uma só se desenha com dado real**.

**2 · Que informação bruta cada uma precisa antes de pensar?**
Setenta e duas coisas diferentes. A que precisa de mais é a das Janelas de
Cultura: doze.

**3 · O que já temos?**
Trinta e oito das setenta e duas têm fonte com nome, que publica aquilo de
verdade e com regularidade.

**4 · Onde estão os buracos?**
Quinze são graves. Os piores: a casa não sabe **em que fase a planta está**
(zero de vinte e nove janelas), não sabe **de onde veio** cada janela (zero de
vinte e nove), não tem **produção nem área** por cultura, e as dezassete vozes de
campo não dizem **de que região são, quem falou, nem quando** — nenhuma das
três, em nenhuma das dezassete.

**5 · Quem na Itália produz o que falta?**
Trinta e sete fontes novas, todas nascidas de um buraco medido. Para a fase da
planta há quatro que publicam a escala BBCH — uma nacional e três regionais, e a
das Marche escreve o número: melo 75-77, pero 76-81, vite 79.

**6 · Alguma coisa não se resolve procurando fonte?**
Sete. Três exemplos: ligar produto a janela é uma conta entre dois dados que já
estão em casa; o relato da rede comercial é **dado da própria ADAMA**; e a
carência está **dentro do PDF do rótulo**, que a casa já sabe abrir — falta
tirar de lá.

**7 · E o ensaio de campo?**
Esse não se resolve com fonte **nem com trabalho**. Os seis laboratórios
italianos que fazem os ensaios oficiais **não podem publicar**: o dado é de quem
pagou o ensaio. Não é buraco de fonte, é buraco de **permissão** — e resolve-se
com contrato, não com coleta.

**8 · O Radar melhorou?**
Não ganhou fonte nenhuma, e está certo assim: ele **cruza** as outras camadas.
Mas ele nunca é melhor do que a sua entrada mais fraca — e sem região nem data
nas vozes, cruzar «voz» com «janela» **não é possível**, por bem escrito que ele
esteja.

**9 · Que regiões continuam no escuro?**
Duas sem nada: **Basilicata** e **Valle d'Aosta**. Quatro com uma só fonte:
Abruzzo, Campania, Friuli-Venezia Giulia e Molise.

**10 · Em que é que eu não devo confiar nesta entrega?**
Em três coisas, e vale dizê-las claro: **nenhuma das trinta e sete rotas foi
aberta** — foram descritas por busca, e descrever não é ler; **cinco das dez
culturas do casco não foram pesquisadas** (trigo, trigo duro, milho, soja e
tomate — que são quase metade das janelas); e **dezoito linhas dizem «talvez»**,
não «sim».

---

## VEREDITO

```
VEREDITO = PARTIAL
```

**Por que não é COMPLETE.** A pergunta central foi respondida para as nove
ferramentas, com as setenta e duas matérias-primas medidas campo a campo e
auditadas uma a uma. Mas metade das culturas do casco não foi pesquisada,
nenhuma das rotas novas foi aberta por sonda, e o gap mais central de VOICES —
voz de **produtor** com região e data — **não fechou**: o que se achou foi voz
de técnico institucional, que enche três colunas e responde a outra pergunta.

**Por que não é BLOCKED.** Nada ficou sem resposta por falta de autoridade. Os
onze achados que mudaram a resposta são resultado, não desculpa — em especial os
quatro que impedem erros caros: a rota morta do Coeweb, a quebra de série do
ISMEA, a confidencialidade das provas GEP e a mudança de prazo do Omnibus.

**O mais útil desta missão não foram as 37 fontes.** Foi separar três coisas que
pareciam uma: o que falta **coletar**, o que falta **ligar** e o que não se pode
**ter**.

```
HARD STOP
```
