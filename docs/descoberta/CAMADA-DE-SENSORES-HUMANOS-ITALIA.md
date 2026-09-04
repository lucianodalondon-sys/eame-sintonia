# CAMADA DE SENSORES HUMANOS — ITÁLIA

Quem observa o campo italiano, sobre que cultura, que problema, em que região — e quando
voltar para escutá-lo.

**Data:** 2026-09-04 · **País:** Itália · **Missão:** UPSTREAM (nenhum artefato de
portal, APP_MODEL, Vercel ou UI foi tocado)

**Registro:** [`data/samples/IT-HUMAN-SENSORS/REGISTRY.json`](../../data/samples/IT-HUMAN-SENSORS/REGISTRY.json)

| artefato | o que é |
|---|---|
| [`UNIVERSE.json`](../../data/samples/IT-HUMAN-SENSORS/UNIVERSE.json) | o universo ADAMA Itália e a matriz de onde procurar |
| [`REGISTRY.json`](../../data/samples/IT-HUMAN-SENSORS/REGISTRY.json) | os sensores qualificados, os rejeitados com motivo, e a fila de descoberta |
| [`COVERAGE.json`](../../data/samples/IT-HUMAN-SENSORS/COVERAGE.json) | CROP × REGION × SPECIALTY com GOOD / WEAK / NONE |
| [`TOP-20-PRIMARY.json`](../../data/samples/IT-HUMAN-SENSORS/TOP-20-PRIMARY.json) | as 20 origens que cobrem mais matriz, uma por família de origem |
| [`PERSISTENCE-PROOF.json`](../../data/samples/IT-HUMAN-SENSORS/PERSISTENCE-PROOF.json) | 10 sensores reabertos do disco, campo a campo |

Código: `scripts/sensor_descoberta_it.py` · `sensor_epmc_it.py` · `sensor_youtube_it.py` ·
`sensor_instituicoes_it.py` · `sensor_humano.py`

---

## O QUE ESTA CAMADA É — e o que ela não é

**É** a resposta a uma pergunta que o SINTONIA ainda não sabia responder: *quais pessoas
vale a pena escutar, sobre qual assunto, em qual cultura, em qual região, e quando voltar.*

**Não é** uma coleta de influenciadores. `FOLLOWERS != AUTHORITY` continua sendo lei:
`AUDIENCE_SIZE` é gravado como dado descritivo e **não é lido por nenhuma regra de tier**.
Nenhum campo deste registro ordena pessoas.

---

## 1 · O UNIVERSO ADAMA ITÁLIA — de onde a matriz saiu

Fonte primária: **IT-T4-001** — Ministero della Salute, `PROD_FTS_6_20260831.csv`
(17.695 produtos), baixado nesta missão. O nome datado foi **descoberto na página do
dataset**, não chutado — e mudou desde a última captura do repositório (`20260824` →
`20260831`).

| medido | valor |
|---|---|
| autorizações ADAMA em vigor na Itália | **163** |
| titular `ADAMA ITALIA S.R.L.` | 85 |
| substâncias ativas distintas | **53** |
| linhas da matriz `CROP × TARGET` | **27** |
| culturas · alvos · regiões | 12 · 27 · 16 |

**O que o portfólio italiano diz, e que muda a missão:** por atividade declarada, o maior
bloco ADAMA na Itália **não é fungicida — é herbicida**. `DISERBANTE` 26 · `FUNGICIDA` 22 ·
`INSETTICIDA` 15 (titular italiano). Os dois ativos mais repetidos são **CLODINAFOP** e
**CLOQUINTOCET MEXYL**, 10 registros cada; o terceiro é **METAMITRON**, 7 — a base do
GOLTIX em beterraba e do BREVIS em maçã.

### O que NÃO temos, e por quê

> `LABEL_CROP_TARGET_STATE = FAILED_WITH_REASON`
>
> A base que traria **`coltura × avversità` autorizada produto a produto**
> (`fitosanitari.salute.gov.it`) **não é alcançável desta saída**: o TLS falha no proxy e
> `servizi.salute.gov.it` devolve **502**. Medido em 2026-09-04.
>
> **Nenhum par desta matriz afirma "uso autorizado em etiqueta".** A matriz diz onde
> **procurar gente**, e cada linha carrega o ativo ADAMA que a ancora. Confundir as duas
> coisas seria inventar uma permissão regulatória a partir de uma lista de moléculas.

Por isso a missão não pôde partir de "51 produtos, 35 culturas de etiqueta, 78 alvos": o
registro italiano público publica **vencimento e substância, não cultura × alvo** — o mesmo
assimetria que o `CASE-014` já tinha registrado entre França e Itália.

---

## 2 · AS ROTAS — o que respondeu e o que não

| rota | estado | resultado |
|---|---|---|
| **Europe PMC** (ciência) | `COLLECTED` — 25/25 recortes | 4.471 autores com afiliação italiana declarada |
| **YouTube busca pública** (canal) | `COLLECTED` — 26/26 consultas | 229 canais, **229 com identidade resolvida** |
| **Páginas institucionais** | `PARTIAL` | **39 de 49** URLs verificadas nesta execução |
| **OpenAlex** | **`FAILED_WITH_REASON`** | orçamento diário zerado |
| **SINTONIA SCRAP** (conteúdo + transcrição) | **`NOT_REACHED — NO_KEY`** | nenhuma variável `APIFY*` neste ambiente |

### A rota gratuita que deixou de ser gratuita

O repositório descreve o OpenAlex como *"rota REST gratuita, sem chave"*. **Essa premissa
morreu**, e a medição está preservada:

```
HTTP 429 · {"error":"Rate limit exceeded",
            "message":"Insufficient budget. This request costs $0.0001 but you only
                       have $0 remaining. Resets at midnight UTC.",
            "retryAfter":49093, "dailyRemainingUsd":0}
```

Não é rajada nem estrangulamento de IP — é **preço por requisição com orçamento diário
zerado**. Os 25 recortes saíram todos `THROTTLED_NOT_EMPTY`, **nenhum com zero**, porque
`SOURCE FAILURE != ZERO`.

A substituta é o **Europe PMC**, e ela entrega algo que o OpenAlex não dava tão
diretamente: **a string de afiliação por autor, com a cidade dentro**. Daí sai `REGION`,
com base declarada `INSTITUTION_ADDRESS_DECLARED_IN_AFFILIATION` — que é o endereço da
instituição do autor e **nada mais**. Não é onde o experimento foi feito, não é onde a
pessoa observa campo, e `FACT_LOCATION` continua `NÃO SEI`.

---

## 3 · O PORTÃO AGRONÔMICO — a armadilha que esta missão pagou

Consulta técnica traz **outra população com cara de sucesso**. O repositório já tinha
medido isso uma vez (`97,3x` no drift espanhol). Aqui a armadilha voltou com outra roupa:
`aflatoxin`, `deoxynivalenol`, `Monilinia` e `fungicide resistance` puxaram para dentro do
corpus italiano:

| afiliação que entrou pela consulta | autores |
|---|---|
| IBD unit — Digestive Disease Center (CeMAD), Policlinico Gemelli IRCCS | 12 |
| Istituto Zooprofilattico Sperimentale dell'Umbria e delle Marche | 8 |
| Human Nutrition Unit, Department of Food and Drug, University of Parma | 8 |
| Department of Veterinary Sciences, University of Messina | 7 |

São autores **reais**, **italianos**, **do assunto** — e **não são sensores agrícolas**.
Gastroenterologia publica sobre micotoxina porque a micotoxina chega ao paciente, não
porque alguém olhou a lavoura.

O portão é **positivo**: a afiliação precisa **declarar** domínio agronômico. Ausência de
marcador não vira "provavelmente agrícola" — vira `NOT_DECLARED`, e a pessoa não é
promovida. **2.480 candidatos foram recusados por este portão.**

### E o portão errou — três vezes, medidas e corrigidas

A primeira versão barrou exatamente três nomes que esta camada existe para achar. O motivo,
em cada caso, foi a **forma** da afiliação, não o domínio:

| nome | afiliação declarada | por que passou a entrar |
|---|---|---|
| **Vittorio Rossi** | *Department of Sustainable **Crop Production**, Università Cattolica, Piacenza* · *Research Center for **Plant Health** Modelling* | termos `crop production` e `plant health` acrescentados — nenhum departamento médico se chama assim |
| **Antonio F. Logrieco** | *Institute of Sciences of Food Production (**ISPA**), CNR, Bari* | sigla `ispa` acrescentada — o instituto de referência italiano em micotoxina de cereal |
| **Nicola Mori** | *Department of **Biotechnology**, University of Verona* | **nenhum** marcador agronômico. Entrou por outra porta — ver abaixo |

O caso Mori é o mais instrutivo. A afiliação dele **realmente** não declara agronomia. Mas
ele já está no `SPEAKER-UNIVERSE-PILOT-V1` com `IDENTITY_PROVED` por ORCID e escopo
`IT-VINE-FLAVESCENCE` congelado por árbitro. Barrá-lo aqui seria **o registro
desconhecendo a própria prova anterior**. A exceção não afrouxa o portão: ela reconhece
prova que já existe nesta casa, e sai marcada como `TECHNICAL_AUTHORITY =
PROVED_BY_CANONICAL_OWNER`.

> **Cobertura que sobe porque o classificador ficou permissivo não é cobertura** — mas
> cobertura que cai porque a regra não conhece o vocabulário da fonte também não é rigor.
> A diferença entre as duas é que a segunda se conserta nomeando o mecanismo, e a primeira
> não se conserta.

---

## 4 · OS QUATRO OUTROS PORTÕES DA ROTA CIENTÍFICA

Nenhum deles **ordena** pessoas. Todos decidem **inclusão** — e a diferença importa,
porque `REGRA-DE-COLETA §6` proíbe authority score.

| portão | regra | recusados |
|---|---|---|
| **ORGANIZAÇÃO RESOLVIDA** | sem `ORGANIZATION_ID` não há família de origem, e sem família não há medida de independência (§11) | 200 |
| **RECÊNCIA** | sem obra no recorte desde 2025 — a pergunta é quem observa **hoje** | 796 |
| **RECORRÊNCIA ≥ 8** | coautoria de passagem não é sensor. **Recorrência não é autoridade** — o número decide se o assunto é a linha de trabalho da pessoa, e não publica posição nenhuma | 920 |
| **ORCID DECLARADO** | `REGRA-DE-COLETA §17`, medido na Espanha: o elo `CIÊNCIA → CANAL PÚBLICO` **não se constrói com nome**, e casar por similaridade produziu falso positivo demonstrável. Sem identificador declarado que atravesse camadas, a pessoa nunca poderá ser ligada a um canal — logo **não pode ser monitorada** | 7 |

---

## 5 · ENTREGA

```
SENSORS DISCOVERED  = 4.749
QUALIFIED           =   224
REJECTED            = 4.525

TIER A = 110      TIER B = 61      TIER C = 53
```

### Por tipo

| bucket | A | B | C | total |
|---|---:|---:|---:|---:|
| RESEARCHERS | 94 | 52 | 13 | **159** |
| TECHNICIANS | 8 | 2 | 11 | **21** |
| AGRONOMISTS | — | — | 17 | **17** |
| COOPERATIVES | 5 | 5 | 4 | **14** |
| PRODUCERS | — | — | 8 | **8** |
| CREATORS | 3 | 2 | — | **5** |

`PERSON` 135 · `ORGANIZATION` 56 · `PERSON_OR_ORGANIZATION_NOT_DECLARED` 33
**Famílias de origem independentes: 116.**

> **A meta da missão era 50–100 qualificados, com 15–30 pesquisadores.** O número de
> pesquisadores passou muito da faixa (159) e o de produtores/creators ficou muito abaixo
> (13). Isso **não** é a rota funcionando bem demais de um lado: é o desenho das rotas
> disponíveis. Ciência tem índice aberto e gratuito; produtor e técnico de campo, não. O
> desequilíbrio é a medida honesta do que **esta** saída alcança, e está registrado como
> lacuna, não como sucesso.

### Por cultura (sensores qualificados)

VINE 128 · WHEAT 118 · TOMATO 99 · MAIZE 83 · STONE_FRUIT 59 · OLIVE 56 · RICE 56 ·
POTATO 51 · APPLE 45 · CEREAL 32 · MULTI 30 · SUGAR_BEET 16

### Por região

EMILIA-ROMAGNA 35 · PIEMONTE 22 · PUGLIA 22 · VENETO 19 · TRENTINO-ALTO ADIGE 18 ·
LOMBARDIA 13 · TOSCANA 11 · UMBRIA 10 · CAMPANIA 8 · LAZIO 6 · MARCHE 5 · SICILIA 5 ·
BASILICATA 2 · CALABRIA 2 · FRIULI-VENEZIA GIULIA 2 · ABRUZZO 1

### Recomendação de monitoramento — guardada, não agendada

`MONTHLY` 154 · `WEEKLY` 37 · `DISCOVERY_ONLY` 31 · `EVENT_DRIVEN` 2

**Nenhum agendamento real foi criado.** A arquitetura de agendamento ainda não tem dono, e
a missão manda guardar a recomendação, não executá-la.

---

## 6 · MATRIZ DE COBERTURA — onde ainda estamos cegos

**117 células** `CROP × REGION × SPECIALTY`, derivadas da matriz ADAMA.

| estado | células | regra |
|---|---:|---|
| **GOOD** | 72 | ≥2 sensores Tier A/B em **≥2 famílias de origem** |
| **WEAK** | 29 | ≥1 sensor, ou todos da mesma família |
| **NONE** | 16 | nenhum sensor qualificado |

A exigência de **duas famílias** vem do §11 e é o que impede a cobertura de mentir: uma
célula coberta por cinco nomes do mesmo instituto é **WEAK por construção**, porque três
pessoas do mesmo laboratório não são três fontes independentes.

### O achado — a maior lacuna é exatamente onde o portfólio é mais denso

| cultura | GOOD | WEAK | NONE |
|---|---:|---:|---:|
| VINE | 15 | 1 | 2 |
| MAIZE | 15 | 2 | — |
| WHEAT | 11 | 6 | 2 |
| APPLE | 10 | 1 | — |
| **CEREAL** (ervas, resistência, pulgões) | **0** | **8** | **4** |
| **SUGAR_BEET** | 2 | 2 | **3** |

**`CEREAL` não tem uma única célula GOOD.** E `CEREAL` é onde a ADAMA Itália tem **26
registros de herbicida em vigor**, com `CLODINAFOP` e `CLOQUINTOCET MEXYL` nos dois
primeiros lugares do portfólio. `SUGAR_BEET`, o cultivo do `METAMITRON` (7 registros), tem
três células sem ninguém.

**A causa é da rota, e é medível.** O Europe PMC é um índice de ciências da vida, e a
malherbologia europeia publica noutro lugar:

| recorte | hits |
|---|---:|
| VINE \| FLAVESCENCE_DOREE | 791 |
| TOMATO \| TOMATO_DISEASE | 352 |
| MAIZE \| MYCOTOXIN | 297 |
| … | |
| **MAIZE \| MAIZE_WEEDS** | **24** |
| **CEREAL \| GRASS_WEEDS** | **21** |
| SUGAR_BEET \| CERCOSPORA | 10 |

> Isto **não** significa que a Itália não tem malherbologistas. Significa que **esta rota
> não os alcança**, e que a próxima rodada precisa de outra — sociedade científica de
> malherbologia, atas de congresso, revista técnica — e não de um limiar mais frouxo na
> mesma rota. `FAIL CLOSED`: rota que não alcança **≠** gente que não existe.

### TOP 10 COVERAGE GAPS

| # | cultura | região | especialidade | ativo ADAMA que a ancora |
|---|---|---|---|---|
| 1 | CEREAL | EMILIA-ROMAGNA | HERBICIDE_RESISTANCE | CLODINAFOP \| PINOXADEN (ACCase/ALS) |
| 2 | CEREAL | EMILIA-ROMAGNA | GRASS_WEEDS | CLODINAFOP \| PINOXADEN \| MESOSULFURON |
| 3 | CEREAL | LOMBARDIA | GRASS_WEEDS | idem |
| 4 | CEREAL | EMILIA-ROMAGNA | APHIDS | PIRIMICARB (APHOX) \| FLONICAMID |
| 5 | SUGAR_BEET | LOMBARDIA | BEET_WEEDS | METAMITRON (GOLTIX) |
| 6 | OLIVE | TOSCANA | OLIVE_FRUIT_FLY | LAMBDA-CYHALOTHRIN |
| 7 | OLIVE | LAZIO | OLIVE_FRUIT_FLY | LAMBDA-CYHALOTHRIN |
| 8 | STONE_FRUIT | CAMPANIA | BROWN_ROT | TEBUCONAZOLE \| DIFENOCONAZOLE |
| 9 | STONE_FRUIT | FRIULI-V.G. | BROWN_MARMORATED_STINK_BUG | LAMBDA-CYHALOTHRIN |
| 10 | MULTI | LOMBARDIA | SLUGS | METALDEHYDE (LUMA-KL) |

---

## 7 · TOP 20 PRIMARY SENSORS — seleção por cobertura, não por mérito

**20 origens cobrem 91 das 117 células — 77,8%**, uma família de origem por sensor.

Isto **não é um ranking**. Um "top 20 dos melhores" seria authority score com outro nome. O
critério é operacional: *se eu só pudesse escutar 20 origens continuamente, quais 20 cobrem
mais matriz sem repetir família?* Guloso sobre cobertura marginal, desempate pelo id.

| # | sensor | papel | região | culturas | monitorar | +células |
|---:|---|---|---|---|---|---:|
| 1 | Servizio Fitosanitario **Emilia-Romagna** | PLANT_HEALTH_SERVICE | Emilia-Romagna | WHEAT MAIZE SUGAR_BEET APPLE STONE_FRUIT VINE POTATO | WEEKLY | +14 |
| 2 | U.O. Fitosanitario **Veneto** | PLANT_HEALTH_SERVICE | Veneto | VINE MAIZE WHEAT APPLE SUGAR_BEET | WEEKLY | +12 |
| 3 | Settore Fitosanitario **Piemonte** | PLANT_HEALTH_SERVICE | Piemonte | VINE RICE MAIZE APPLE | WEEKLY | +9 |
| 4 | **Santa Olga Cacciola** | RESEARCHER | Sicilia · Univ. Catania | OLIVE + | MONTHLY | +7 |
| 5 | Servizio Fitosanitario **Lombardia** | PLANT_HEALTH_SERVICE | Lombardia | MAIZE RICE WHEAT VINE | WEEKLY | +6 |
| 6 | **ERSA** Friuli-Venezia Giulia | PLANT_HEALTH_SERVICE | FVG | VINE MAIZE APPLE | WEEKLY | +5 |
| 7 | **Osservatorio Fitosanitario Puglia** | PLANT_HEALTH_SERVICE | Puglia | OLIVE WHEAT TOMATO VINE | WEEKLY | +5 |
| 8 | **Nicola Mori** | RESEARCHER | Veneto · Univ. Verona | VINE + | MONTHLY | +5 |
| 9 | Servizio Fitosanitario **Prov. Trento** (FEM) | PLANT_HEALTH_SERVICE | Trentino-A.A. | APPLE VINE | WEEKLY | +4 |
| 10 | **Massimo Turina** | RESEARCHER | Piemonte · CNR-IPSP | VINE APPLE | MONTHLY | +4 |
| 11 | **Francesco Di Serio** | RESEARCHER | Puglia · CNR | — | MONTHLY | +3 |
| 12 | **Paola Battilani** | RESEARCHER | Emilia-Romagna · UCSC | MAIZE WHEAT | MONTHLY | +3 |
| 13 | Servizio Fitosanitario **Umbria** | PLANT_HEALTH_SERVICE | Umbria | WHEAT OLIVE VINE | WEEKLY | +2 |
| 14 | **Fondazione Agrion** | RESEARCH_CENTRE | Piemonte | APPLE STONE_FRUIT VINE | MONTHLY | +2 |
| 15 | **Univ. Politecnica delle Marche — D3A** | UNIVERSITY | Marche | STONE_FRUIT WHEAT | MONTHLY | +2 |
| 16 | **CREA — Olivicoltura, Frutticoltura** | PUBLIC_RESEARCH | Calabria | OLIVE APPLE STONE_FRUIT | MONTHLY | +2 |
| 17 | **Claudio Pugliesi** | RESEARCHER | Toscana · Univ. Pisa | — | MONTHLY | +2 |
| 18 | **Ciro Gianmaria Amoroso** | RESEARCHER | Campania · Federico II | TOMATO + | MONTHLY | +2 |
| 19 | **AgroNotizie — Image Line** | TECHNICAL_MEDIA | Emilia-Romagna | MULTI | WEEKLY | +1 |
| 20 | **L'Informatore Agrario** | TECHNICAL_MEDIA | Veneto | MULTI | WEEKLY | +1 |

**Os serviços fitossanitários regionais dominam o topo, e a razão é estrutural:** eles
publicam *bollettini* territoriais, multi-alvo e multi-cultura, e por isso cobrem muitas
células de uma vez. É a única classe de origem desta camada com
`FIELD_PROXIMITY = DECLARED_TERRITORIAL_ACTIVITY` — declarada pela própria página, não
presumida do rótulo.

---

## 8 · SINTONIA SCRAP — o que não foi feito, e por quê

```
PROFILES COLLECTED         = 0
CONTENTS                   = 0
VIDEOS                     = 0
TRANSCRIPTS                = 0
USEFUL SIGNALS             = 0
SIGNALS ONLY IN TRANSCRIPT = 0
NEW HUMAN SIGNALS          = 0
CLUSTERS IN MONITORED SOURCES = 0
```

**Estado: `NOT_REACHED — NO_KEY`.**

O SINTONIA SCRAP existe e **não foi reescrito**: `scripts/sensor_coleta.py`,
`youtube_janela.py`, `youtube_transcrever.py`, `instagram_coleta.py`,
`instagram_transcrever.py` já fazem coleta e transcrição por Apify. Todos exigem
`APIFY_TOKEN`, e **nenhuma variável `APIFY*` existe neste ambiente** (medido 2026-09-04).

`FAIL CLOSED`: chave ausente **≠** canal sem conteúdo. Zero aqui é o estado da rota, não do
campo. E **nenhum sinal foi inventado para preencher a tabela** — que é exatamente o que
`§9` e `§10` da missão proíbem.

**Consequência assumida, e ela é grande:** sem fala coletada, `OBSERVATION_CAPABILITIES`
não pôde ser provada por conteúdo falado para **nenhum** sensor. O que existe hoje é:

| base da capacidade | sensores |
|---|---:|
| `PUBLICATION_IN_SCOPE` — derivada do recorte, com os IDs das obras anexados | 135 |
| `DECLARED_ON_INSTITUTIONAL_PAGE` — termos lidos do HTML buscado | 25 |
| `NOT_ESTABLISHED` — canais de vídeo, sem conteúdo coletado | 64 |

Capacidades hoje sustentadas: `DISEASE_PRESSURE` 138 · `PEST_PRESSURE` 113 ·
`REGULATORY_INTERPRETATION` 80 · `CROP_CONDITION` 76 · `APPLICATION_TIMING` 39 ·
`MARKET_CONCERN` 34 · `RESISTANCE` 21 · `WEED_PRESSURE` 17 · `PRODUCT_USE` 15 ·
`MANAGEMENT_CHANGE` 11 · `PHENOLOGY` 7 · `TECHNICAL_DIFFICULTY` 4.

**Nenhuma delas prova visita a campo.** `FIELD_PROXIMITY` sai `NOT_ESTABLISHED` para
**203 dos 224** sensores — entre eles **todos os 135 pesquisadores-pessoa** — com o motivo
escrito em cada registro: *publicação não prova visita a campo*. Os **21** que escapam são
os serviços e consorzi territoriais, e o que os sustenta é
`DECLARED_TERRITORIAL_ACTIVITY`: a própria página declara *bollettino*, *monitoraggio* ou
*avversità*, lida no HTML que a rota buscou.

---

## 9 · IDENTIDADE — o que a rota de canal mediu

229 canais descobertos, **229 com identidade resolvida pela aba About do próprio canal**.
O papel sai **exclusivamente da descrição que o canal declara** — nunca do nome, nunca do
conteúdo do vídeo.

| país declarado | canais |
|---|---:|
| **IT** | 128 |
| `NOT_DECLARED` | 70 |
| **US** | 17 |
| DE · CA · AU · IE | 2 cada |
| DK · NL · BE · NZ · PK · MD | 1 cada |

> **Idioma não é país, outra vez.** 17 canais que respondem a consultas técnicas em
> italiano declaram **Estados Unidos**. A regra espanhola (`#sanidadvegetal` dominada por
> México e Argentina) reaparece intacta na Itália, e os 17 foram recusados por país
> declarado — não por julgamento de conteúdo.

Recusas da rota de canal: **79** por não declararem papel técnico na própria descrição
(*nome de canal não decide papel*) e os canais de **indústria de defensivos**, que não são
rejeitados por serem ruins — pertencem à camada `COMPETITOR COMMUNICATION`, que já existe
neste repositório.

**A data não foi inventada.** A busca devolve tempo relativo (*"3 mesi fa"*), não data.
`LAST_CONTENT_DATE = NÃO SEI` e `LAST_CONTENT_RELATIVE` preserva o que a fonte disse.

---

## 10 · DONO CANÔNICO — não duplicar quem já existe

Quatro italianos já tinham dono canônico em `SPEAKER-UNIVERSE-PILOT-V1`. **Nenhum segundo
dono foi criado.** O casamento é por **sobrenome idêntico + inicial do prenome**, nunca por
similaridade textual:

| nesta camada | dono canônico | PERSON_ID herdado |
|---|---|---|
| Fabio Quaglino | `F. Quaglino` | `openalex.org/A5057322051` |
| Massimo Blandino | `Massimo Blandino` | `openalex.org/A5061913370` |
| Nicola Mori | `Nicola Mori` | `openalex.org/A5002982424` |
| Antonio F. Logrieco | `Antonio Logrieco` | `openalex.org/A5030669619` |

E a lei que justifica o rigor continua valendo: *a busca por "Pasquale De Vita" no LinkedIn
devolveu o presidente da Unione Petrolifera, um vendedor de esquadrias e um diretor de TI.*
`NAME_MATCH != PERSON`.

---

## 11 · PROVA DE PERSISTÊNCIA

`STATE = PROVED`.

10 sensores foram **reabertos do disco** depois da gravação, campo a campo:

```
IT-P-98ce0e6a98 ID_STABLE Silvia Laura Toffolatti   A  MONTHLY  49/49 campos
IT-P-6134af398c ID_STABLE Giuliana Maddalena        A  MONTHLY  49/49 campos
IT-P-11f66405c9 ID_STABLE Gianfranco Romanazzi      A  MONTHLY  49/49 campos
IT-P-d009bf1a7d ID_STABLE Massimo Turina            A  MONTHLY  49/49 campos
IT-P-6616ab45da ID_STABLE Michele Perazzolli        A  MONTHLY  49/49 campos
IT-P-f3120c875c ID_STABLE Luca Nerva                A  MONTHLY  49/49 campos
IT-P-c1dd4f5b4a ID_STABLE Giovanni Beccari          B  MONTHLY  49/49 campos
IT-P-5704408c3c ID_STABLE Lorenzo Covarelli         B  MONTHLY  49/49 campos
IT-O-a3f66c22ab ID_STABLE Serv. Fitosanitario Tosc. C  WEEKLY   49/49 campos
IT-O-b1d9dc9b02 ID_STABLE Serv. Fitosanitario Camp. C  WEEKLY   49/49 campos
```

A prova **não** é "o arquivo existe". É que os **49 campos obrigatórios** do perfil canônico
sobreviveram à gravação e voltaram legíveis, e que o `SENSOR_ID` — que é **derivado**, não
sorteado — recalculado do zero devolve o mesmo valor (`ID_STABLE`). Um registro que grava e
não reabre é indistinguível de um que nunca gravou.

---

## 12 · RELAÇÃO COM O OPPORTUNITY ENGINE — só IDs, sem promover

Casos já registrados no repositório que **poderiam** ser enriquecidos por esta camada. São
**ponteiros**, não promoções, e nenhum deles muda de estado por causa desta missão:

| caso | por que esta camada toca nele |
|---|---|
| `CASE-003` | calendário de vencimentos ADAMA na Itália — a camada acrescenta **quem** observa as culturas afetadas |
| `CASE-010` | ponte ciência ↔ rede técnica na Itália, em vinha — a camada dá 122 sensores em VINE e o `TOP-20` |
| `CASE-011` | plataforma europeia de cereal dependente do protioconazol — a camada dá 107 sensores em WHEAT |
| `CASE-014` | mesma molécula em dois mercados — a camada é o lado italiano da comparação |

**Nada aqui vira `SALES_READY`, `ACT_NOW`, demanda ou incidência.** Uma voz humana pode
reforçar, antecipar, contextualizar, regionalizar ou sugerir investigação. Não pode sozinha
inventar mercado, e a decisão final pertence ao Commercial Priority Engine.

---

## 13 · O QUE ESTA CAMADA AINDA NÃO PODE DIZER

| não dizer | porque |
|---|---|
| *"temos cobertura humana da Itália"* | 16 células `NONE` e 29 `WEAK` de 117; `CEREAL` sem nenhuma `GOOD` |
| *"estes sensores observam o campo"* | `FIELD_PROXIMITY = NOT_ESTABLISHED` em **203 dos 224**. Publicação não é visita |
| *"a Itália tem poucos malherbologistas"* | a **rota** não os alcança. `FAIL CLOSED` |
| *"os canais italianos são fracos tecnicamente"* | 70 de 229 não declaram país e 79 não declaram papel. Isso é identidade ausente, não qualidade medida |
| *"3 sensores confirmam X"* | se os 3 forem da mesma organização, são **uma** família de origem. A matriz já aplica isso |
| *"este é o top 20 mais importante"* | é o top 20 de **cobertura**. Não existe medida de importância neste registro |

---

## 14 · NEXT 20 SENSORS TO DISCOVER

`DISCOVERY_POOL` tem **1.206 candidatos barrados por um único portão**, cada um com o que
falta escrito na linha. Não são lixo: são a fila da próxima rodada. O arquivo guarda uma
**amostra estratificada — até 30 por motivo**, e não um top-N global: ordenar tudo por
obras e cortar em 120 fazia os 79 canais, que não têm contagem de obras, sumirem do
arquivo embora contados. **Uma categoria que some da amostra é indistinguível de uma
categoria vazia.**

| falta | candidatos | o que resolveria — sem afrouxar regra |
|---|---:|---|
| `RECURRENCE` | 920 | ampliar a janela ou abrir um recorte novo onde a pessoa seja recorrente |
| `ORGANIZATION_VOCABULARY` | 200 | acrescentar a organização a `ORG_CANONICA`, na forma em que ela aparece na afiliação |
| `CHANNEL_ROLE_DECLARATION` | 79 | reler a aba About, ou buscar papel num perfil institucional — **nunca** inferir do vídeo |
| `ORCID` | 7 | resolver o ORCID em `pub.orcid.org` por instituição + sobrenome, e só promover se a fonte responder |

Os 20 primeiros da fila, por obras no recorte — todos barrados por **um** portão só:

Quirico Migheli (15) · Michele Digiaro (14) · Safa Oufensou (14) · **Terenzio Bertuzzi**
(14, falta ORCID) · Toufic Elbeaino (14) · Virgilio Balmas (14) · **Marco Scortichini**
(13, falta ORCID) · Elena Baraldi (11) · Giuliano Bonanomi (10) · Ivana Castello (10) ·
Anna Narduzzo (9) · Alessandra Gentile (8) · Domenico Rizzo (8) · Francesca Vanara (8) ·
Stefano Civolani (8) · **Alberto Alma** (7) · Alessandra Ferrandino (7) ·
Alessandro Infantino (7) · Alessandro Passera (7) · Alessandro Vannozzi (7)

**Quinze deles faltam apenas o vocabulário de organização** — a correção mais barata e de
maior retorno da próxima rodada.

### E as rotas que faltam, que não são de pessoas

1. **Malherbologia** — a lacuna estrutural. Sociedade científica italiana de malherbologia,
   atas, revista técnica. O `Europe PMC` não a alcança.
2. **A base de etiqueta** (`fitosanitari.salute.gov.it`) — sem ela não há `crop × target`
   autorizado, e a matriz continua sendo "onde procurar", não "o que é permitido".
3. **Os 10 sites institucionais que não responderam** — 7 `URLError` e 2 `404`, entre eles
   os **consorzi fitosanitari provinciais** de Reggio Emilia e Modena, que são exatamente o
   nível territorial onde a observação de campo acontece.
4. **Autores de bollettino** — o bollettino sai assinado pelo serviço, e a pessoa que o
   escreveu não está na página. É PDF, e é a rota mais promissora para técnicos nomeados.

---

## VEREDITO

```
HUMAN SENSOR LAYER            = PARTIAL
READY FOR CONTINUOUS MONITORING = NO
```

**PARTIAL, e não PASS**, por três razões nomeadas:

1. **Nenhum conteúdo foi coletado ou transcrito.** Sem `APIFY_TOKEN`, a camada que a missão
   diz ser a mais importante — **a fala** — não existe. `FIELD_PROXIMITY` e
   `OBSERVATION_CAPABILITIES` por fala seguem `NOT_ESTABLISHED` para todos.
2. **A cobertura é desigual de forma estrutural**, e a maior lacuna (`CEREAL`, herbicida)
   coincide com o bloco mais denso do portfólio italiano da ADAMA.
3. **O equilíbrio de tipos não foi alcançado**: 159 no balde RESEARCHERS (135 deles
   pessoas) contra 13 produtores/creators, porque ciência tem índice aberto e campo não
   tem.

**NO para monitoramento contínuo**, e a razão é honesta: as **recomendações** de
monitoramento estão guardadas para os 224 sensores, mas o executor não existe — nem chave
de coleta, nem dono de agendamento. Declarar `YES` aqui seria chamar de capacidade uma
tabela bonita, que é precisamente o que este repositório recusa.

**O que ficou pronto e é permanente:** o registro canônico com 49 campos por sensor, a
matriz ADAMA ancorada em registro primário, a matriz de cobertura com medida de
independência de origem, os 20 primários por cobertura, a fila de descoberta com o motivo
de cada barrado, e a prova de que tudo isso reabre do disco.
