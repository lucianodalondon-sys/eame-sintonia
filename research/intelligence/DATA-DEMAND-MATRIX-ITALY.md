# MATRIZ DE DEMANDA DE DADOS DA INTELLIGENCE — ITÁLIA

```
MISSAO     C-INT-DATA-DEMAND-IT-01
ESPECIE    ESTUDO MEDIDO — NAO IMPLEMENTA, NAO COLETA, NAO REDESENHA O PORTAL
ESCOPO     ITALIA
MEDIDO_EM  2026-09-14
PACOTE     V21-843baf4229d93598 · data de referencia 2026-09-02
INSTRUMENTO provas/demanda_de_dados_da_italia.py   (le, conta, imprime; nao escreve nada)
```

> **Esta é a lista de compras de dados da Intelligence italiana.** Ela não diz o que
> comprar porque é bonito: diz o que comprar porque, sem isso, uma pergunta que a casa
> já declarou fica sem resposta.

---

## ESTA MISSÃO NÃO CRIOU LEI NENHUMA

Quatro documentos já eram donos de quatro quartos desta pergunta. Nenhum foi duplicado:

| o que já tinha dono | onde vive |
|---|---|
| a lei da Intelligence | [`BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md`](../../BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md) · `CANONICAL` · `V0.2` |
| **o que cada capacidade exige como matéria-prima** | [`AGRO-INTELLIGENCE-INPUT-REQUIREMENTS-V1.md`](AGRO-INTELLIGENCE-INPUT-REQUIREMENTS-V1.md) |
| **quais relações existem e com que chave** | [`AGRO-CROSSING-GRAPH-V1.md`](AGRO-CROSSING-GRAPH-V1.md) |
| **qual o papel arquitetural de cada card** | [`AGRO-INTELLIGENCE-TOOL-ROLES-V1.md`](AGRO-INTELLIGENCE-TOOL-ROLES-V1.md) |
| **o que o produto é** | [`docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md`](../../docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md) |
| **o que já foi pedido à Collection** | [`docs/operacao/COLLECTION-P0-CHANGE-REQUEST.md`](../../docs/operacao/COLLECTION-P0-CHANGE-REQUEST.md) |

```
O QUE FALTAVA NAO ERA MAIS UMA LEI. ERA A MEDICAO DA ITALIA CONTRA AS QUE JA EXISTEM.
```

É isso, e só isso, que este ficheiro acrescenta.

---

## VEREDITO

```
INTELLIGENCE_DATA_DIRECTION = PARTIAL

7.078 registos medidos, em 26 colecoes.
12 cruzamentos testados:   3 POSSIBLE · 3 PARTIAL · 6 NOT_POSSIBLE
E os SEIS impossiveis falham pelo MESMO campo.
```

> **O problema da Itália não é volume. É chave.**

---

## 1 · A DESCOBERTA CENTRAL — UM CAMPO DERRUBA METADE DA MÁQUINA

```
ISSUE_ID normalizado, em todo o pacote V2.1 ......................  24 valores distintos
Nomes de praga e doenca CITADOS em texto livre, so nos boletins ... 172 nomes distintos
                                                                    (483 citacoes)
```

Um único boletim de Modena cita **vinte e tal** pragas e doenças no corpo do texto — e sai
do outro lado com `ISSUE_IDS = ["ISSUE_SCAB"]`. O resto não se perdeu na fonte: **perdeu-se
na normalização.**

Onde `ISSUE_IDS` está preenchido, medido registo a registo:

| coleção | registos | com `ISSUE_IDS` |
|---|---:|---:|
| `products.relationships` | 2.030 | 753 |
| `fieldSignals` | 122 | 58 |
| `resistance` | 34 | 13 |
| `windows` | 7 | 6 |
| `agromet` | 44 | 5 |
| `opportunities` | 3 | 1 |
| **`science`** | 88 | **0** |
| **`competitors`** | 577 | **0** |
| **`voices`** | 79 | **0** |
| **`market`** | 157 | **0** |
| **`news`** | 8 | **0** |
| todas as outras 15 coleções | 4.008 | **0** |

```
836 de 7.078 registos sabem de que problema falam. 11,8 %.
```

E como quase toda pergunta útil deste produto une **duas camadas pelo problema**, é este
campo — e não a falta de fontes — que fecha a máquina.

> **A parte que muda a decisão de Collection:** o nome do problema **já está no material
> guardado**. Isto é `INT-LAW-152` — *reprocessar antes de recolher*. Comprar 200 fontes
> novas antes de normalizar o vocabulário compra 200 documentos que também não cruzam.

---

## 2 · OS DOZE CRUZAMENTOS, MEDIDOS

Estado segundo `INT-LAW-091`: `NOT_POSSIBLE` · `PARTIAL` · `POSSIBLE`. Nunca
*closest-match* silencioso.

| CROSSING_ID | pergunta que só ele responde | chaves | estado | linhas que atravessam |
|---|---|---|---|---|
| `X-FIELD-x-PORTFOLIO` | a ADAMA tem resposta registada para o que o campo está a ver? | cultura · problema | **POSSIBLE** | 27 ↔ 116 |
| `X-REGULATORIO-x-PORTFOLIO` | que produtos ADAMA são atingidos por uma decisão de substância? | substância | **POSSIBLE** | 47 ↔ 183 |
| `X-RESISTENCIA-x-PORTFOLIO` | a resistência confirmada toca alguma substância do portfólio? | cultura · problema | **POSSIBLE** | 11 ↔ 15 |
| `X-FIELD-x-JANELA` | o que o campo reporta cai dentro de alguma janela? | cultura · problema · região | PARTIAL | 1 ↔ 5 |
| `X-JANELA-x-PORTFOLIO` | a ADAMA tem uso registado para a janela aberta? | cultura · problema | PARTIAL | 5 ↔ 6 |
| `X-MERCADO-x-CULTURA` | o preço mudou onde o problema está a acontecer? | cultura · região | PARTIAL | 5 ↔ 29 |
| `X-FIELD-x-SCIENCE` | o que a ciência diz do problema que o campo vê? | cultura · problema | **NOT_POSSIBLE** | 0 ↔ 0 |
| `X-FIELD-x-CLIMA` | as condições favoreceram o problema reportado? | região · problema | **NOT_POSSIBLE** | 0 ↔ 0 |
| `X-CONCORRENCIA-x-PORTFOLIO` | quem mais tem resposta registada para este par? | cultura · problema | **NOT_POSSIBLE** | 0 ↔ 0 |
| `X-CONCORRENCIA-x-CAMPO` | a comunicação do concorrente coincide com o campo? | cultura · problema · região | **NOT_POSSIBLE** | 0 ↔ 0 |
| `X-VOZ-x-CAMPO` | a voz pública confirma o boletim oficial? | cultura · problema · região | **NOT_POSSIBLE** | 0 ↔ 0 |
| `X-CIENCIA-x-PORTFOLIO` | há trabalho publicado sobre o alvo que a ADAMA cobre? | cultura · problema | **NOT_POSSIBLE** | 0 ↔ 0 |

**Motivo dos seis:** `ISSUE_IDS` ausente numa das pontas — em cinco deles — e, no sexto
(`X-FIELD-x-CLIMA`), presente nas duas pontas **sem um único valor em comum**: o clima
classifica 5 problemas, o campo classifica 13, e os dois conjuntos não se tocam.

> **`VALOR PARTILHADO ≠ LINHA QUE ATRAVESSA.`** `X-MERCADO-x-CULTURA` partilha 8 culturas
> e 6 regiões — e só **5** linhas de mercado carregam as duas chaves ao mesmo tempo. Foi
> por isso que a medição conta linhas, e não vocabulário.

---

## 3 · AS NOVE SUPERFÍCIES — PAPEL, PERGUNTA, E O BURACO

**A existência de uma tela não prova que ela deva ser uma ferramenta.** A casa já decidiu
isto, e a decisão é dura: *«são duas ferramentas e uma pergunta, com um motor por baixo»*
(`ARQUITETURA-DE-PRODUTO-ATUAL`, que proíbe explicitamente *«desenhar um menu de módulos
independentes»*).

```
DAS NOVE SUPERFICIES ESTUDADAS, UMA E FERRAMENTA PRINCIPAL.
SEIS SAO INTELLIGENCE DE SUPORTE. DUAS SAO CONTEXTO DE EVIDENCIA.
E UMA DELAS NEM SEQUER EXISTE NO PORTAL.
```

| # | superfície | tela hoje | papel canônico |
|---|---|---|---|
| 1 | Opportunity Radar | SIM (`radar` `meeting` `case`) | **PRIMARY_TOOL** |
| 2 | Portfolio | SIM (`portfolio` `product`) | SUPPORTING_INTELLIGENCE |
| 3 | Future Radar | SIM (`future` `signal`) | SUPPORTING_INTELLIGENCE |
| 4 | Label Intelligence | **NÃO** — 0 ocorrências de uma view `label` | SUPPORTING_INTELLIGENCE |
| 5 | Crop Windows | SIM (`windows` `window`) | SUPPORTING_INTELLIGENCE |
| 6 | Market Pulse | SIM (`market`) | EVIDENCE_CONTEXT |
| 7 | Field Voices | SIM (`voices`) | EVIDENCE_CONTEXT |
| 8 | Competitor Watch | SIM (`competitors` `company`) | SUPPORTING_INTELLIGENCE — **e são dois** |
| 9 | Scientific Intelligence | SIM (`science` `theme` `person`) | SUPPORTING_INTELLIGENCE |

E há o contrário, que também é medição: **`MT1 · REGULATORY & EXPIRY EXPOSURE` é ferramenta
principal declarada e não tem superfície própria nenhuma.** Está partida entre Portfolio e
Future Radar. É a única das três ferramentas canônicas cujos cruzamentos estão todos
`POSSIBLE` hoje — e é a que ninguém vê.

---

### A · OPPORTUNITY RADAR — `PRIMARY_TOOL`

```
PERGUNTA       ha convergencia que merece investigacao neste par cultura x problema x
               regiao, e ainda ha tempo de agir?
ROTULO         «CONVERGENCIA QUE MERECE INVESTIGACAO» — nunca «oportunidade»
OBJETO         OPPORTUNITY, nivel A (agronomico) ou B (portfolio registado)
ESTADOS        MATCH · CROP_ONLY · NOT_FOUND · UNKNOWN · MATERIAL_EXISTENTE_NAO_UTILIZAVEL
NAO PODE       nivel C · nivel D · procura · quota · receita · disponibilidade comercial ·
               escrever o proprio nivel (a promocao e do portao, nao do ecra)
```

**O que já temos:** 3 oportunidades reais — e `client_safe = 0` nas três. 122 sinais de
campo, dos quais **40** trazem cultura, problema, região e data ao mesmo tempo.

**O que falta:** quatro dos seis cruzamentos de que ela vive. O card não consegue dizer o
que a ciência, a concorrência ou o clima dizem do mesmo problema — e uma convergência com
uma camada só não é convergência.

**Gap principal:** `GAP-IT-001`.

---

### B · PORTFOLIO — `SUPPORTING_INTELLIGENCE` · *truth layer do registado*

```
PERGUNTA       que usos a ADAMA tem autorizados em Italia, para que cultura e que alvo,
               e ate quando?
FRONTEIRA      REGISTERED != COMMERCIAL != AGRONOMIC RESPONSE != PIPELINE
NAO PODE       catalogo de vendas · disponibilidade comercial · inferir o par cultura x
               alvo quando o rotulo os lista sem os ligar
```

**O que já temos — e é a família mais forte da Itália:** 163 registos com titular ADAMA,
**100 %** com data de caducidade e com URL de rótulo; 53 substâncias ativas; 203 pares
produto × substância; 2.030 relações de rótulo com a força da ligação declarada e a
citação do documento ao lado.

**O que falta:**

```
produtos sem UMA UNICA linha de uso lida .......... 144 de 163
linhas de uso com dose ............................  35 de 219
linhas de uso com intervalo .......................  15 de 219
linhas de uso com numero maximo de aplicacoes .....   0 de 219
linhas de uso com EPOCA ...........................   0 de 219
ISSUE_IDS nos produtos ............................   0 %
```

Para a vinha: **61 produtos citam a cultura, 1 tem linha de uso lida.**

**Gap principal:** `GAP-IT-003` — e é sobretudo **reprocessamento**, não aquisição: os 163
rótulos já estão guardados, e a fonte já tem contrato `GREEN`.

---

### C · FUTURE RADAR — `SUPPORTING_INTELLIGENCE`

```
PERGUNTA       o que ainda nao e acionavel, e quando volta a mesa?
OBJETO         FUTURE_SIGNAL — PROJECCAO de um FINDING em watch, nunca achado novo
NAO PODE       previsao · vocabulario de estado proprio · sinal sem finding por tras
```

**O que já temos:** 47 `regulatoryFutureFacts` com substância, estado europeu, CELEX e data
oficial — matéria sólida. 3 sinais de futuro.

**O que falta — e não é dado:** a separação entre as duas espécies que hoje partilham o
card. Uma caducidade de registo é **facto presente sobre o futuro**: datado, do regulador.
Um sinal fraco é outra coisa. Misturados, não se mede nenhum dos dois. E a consequência já
foi medida em produção: o card inventou **sete** valores de status que a montante nunca
existiram, e os registos reais têm status nulo em 3 de 3 — as sete fichas de filtro contam
zero.

**Gap principal:** `GAP-IT-008`.

---

### D · LABEL INTELLIGENCE — `SUPPORTING_INTELLIGENCE` · *não existe como tela*

```
PERGUNTA       que usos estao autorizados neste rotulo, para quem, com que dose e em que
               epoca — e como isso se compara com o do concorrente?
MEDIDO         0 ocorrencias de uma view «label» em portale.html
```

```
MATERIAL != FERRAMENTA.
```

**O que já temos:** 2.030 relações de rótulo da ADAMA.

**O que falta:** **zero rótulos de concorrente.** Sem a outra metade não há comparação —
há inventário próprio com nome de comparação.

**Gap principal:** `GAP-IT-004` — e a rota já existe: é a **mesma** Banca dati do Ministero
(`IT-T4-001`, `GREEN`, `P0`) lida **sem o filtro de titular**.

---

### E · CROP WINDOWS — `SUPPORTING_INTELLIGENCE` · *o único card alimentado por real*

```
PERGUNTA       ainda ha tempo de fazer alguma coisa neste par, nesta regiao?
JANELA         fenologia ∩ infeccao ∩ rotulo ∩ preparacao — as quatro
NAO PODE       ACT NOW a partir de norma agronomica
```

**O que já temos:** 7 janelas no pacote e 29 janelas canônicas; 44 registos agroclimáticos,
36 com região real.

**O que falta — e é o defeito mais silencioso do produto:**

```
das 29 janelas canonicas:
   CROP_STAGE_SOURCE ...... nulo em 29/29
   ISSUE_STAGE_SOURCE ..... nulo em 29/29
   REGULATORY_SOURCE ...... nulo em 29/29
   LABEL_SOURCE ........... nulo em 29/29
   SOURCE_IDS ............. vazio em 29/29
   PRODUCT_MATCHES ........ vazio em 29/29
   PROVENANCE ............. EXPECTED_NORM 24 · NOT_ESTABLISHED 5 · CONFIRMED 0
```

O próprio ficheiro escreve: *«No window in this pilot has a CONFIRMED calendar range from
an official current-season source.»*

> **JANELA ESPERADA NÃO É OBSERVAÇÃO.** Uma norma agronómica desenhada com a cor de um
> facto observado é a forma mais barata de mentir num portal.

E como `PRODUCT_MATCHES` está vazio em 29 de 29, o cruzamento janela × portfólio **não tem
onde pousar** — é vazio por construção, não por falta de produtos.

**Gap principal:** `GAP-IT-002`.

---

### F · MARKET PULSE — `EVIDENCE_CONTEXT`

```
PERGUNTA       o contexto economico desta cultura mudou o suficiente para alterar a
               prioridade de olhar para ela?
SO VIRA FINDING COM  CHANGE + MATERIALITY + CONTEXT + DECISION_AFFECTED + ATTRIBUTION_LIMIT
NAO PODE       ler preco como volume, procura, quota ou disponibilidade ·
               ler preco de uma praca como preco nacional
```

**O que já temos:** 157 observações de mercado (80 com data) e 2.978 linhas de peso
económico por cultura e região.

**O que falta:** tudo o que não é preço. Só há **preço**, e de dois grupos — cereal e
azeite. Zero volume, zero comércio, zero disponibilidade, zero quota. **Nenhuma observação
de mercado de defensivo.** E 12 das 77 séries do pacote antigo estão **paradas** — uma
desde 2010 — mantendo o último valor e parecendo correntes.

```
PRECO != VOLUME != COMERCIO != DISPONIBILIDADE != QUOTA. Nenhum se infere do outro.
```

**Gap principal:** `GAP-IT-009` · `P2`.

---

### G · FIELD VOICES — `EVIDENCE_CONTEXT` · *sensor com tecto declarado*

```
PERGUNTA       ha gente no campo a falar deste problema, nesta cultura, neste lugar, agora?
TECTO          voz de campo e NIVEL 1 da regua de doenca, e nunca mais do que isso
NAO PODE       incidencia · prevalencia · eficacia · representatividade regional ·
               contar quatro pessoas de um artigo como quatro fontes
```

**O que já temos:** 79 vozes no pacote V2.1; 17 no pacote antigo, cada uma com *o que prova*
e *o que não prova* escrito ao lado — a família mais honesta do conjunto.

**O que falta: quem, onde e quando.**

```
nas 17 vozes do ITALY_INGEST:
   DATE = «NAO SEI» ........................ 17 / 17
   REGION = «NAO SEI» ...................... 17 / 17
   PERSON_IDENTITY_STATE = NAO_ATRIBUIVEL .. 17 / 17
   ROLE = «NAO SEI» ........................ 17 / 17
no pacote V2.1 (79 vozes):
   ISSUE_IDS ...............................  0 %
   regiao real .............................  13 / 79
   data ....................................  21 / 79
```

A rota devolve tempo **relativo** («há 1 ano»), e o próprio dado escreve que converter
inventaria precisão. Uma voz sem quando e sem onde não cruza com coisa nenhuma — foi por
isso que `X-VOZ-x-CAMPO` deu 0 ↔ 0.

**IDENTIDADE ≠ EXPERTISE**, e nem a identidade existe aqui.

**Gap principal:** `GAP-IT-005` — e o estado da frente é **`NOT REACHED`, não `KILL`**.

---

### H · COMPETITOR WATCH — `SUPPORTING_INTELLIGENCE` · *são dois domínios com um nome*

```
PERGUNTA       quem mais tem resposta REGISTADA para este par, e quem esta a comunicar
               sobre ele?
DUAS ESPECIES  REGULATORY_FACT   e   COMPANY_CLAIM   — nunca a mesma contagem
NAO PODE       somar registo, anuncio, comunicacao e atividade tecnica num indicador ·
               dizer que um concorrente esta silencioso ·
               ler AD_REACHED_COUNTRY como AD_TARGETED_COUNTRY
```

**O que já temos:** 577 atividades — **todas** da camada de comunicação. 414 anúncios pagos,
89 vídeos orgânicos.

**O que falta: a camada de registo inteira.**

```
registos de concorrente em Italia ..............   0
das 577 atividades:  ISSUE_IDS 0 % · cultura 27 % · regiao real 4 de 577
fontes de concorrente ..........................   4, das quais 2 BLOCKED (403)
semantica declarada pela propria fonte .........   AD_REACHED_COUNTRY != AD_TARGETED_COUNTRY
                                                   em 414 de 414 anuncios pagos
```

**403 não é ausência de comunicação.** O correto é `NO PUBLIC ACTIVITY FOUND IN SEARCHED
SOURCES`.

**Gaps:** `GAP-IT-004` (registo, `P0`) e `GAP-IT-006` (assunto da comunicação, `P1`).

---

### I · SCIENTIFIC INTELLIGENCE — `SUPPORTING_INTELLIGENCE`

```
PERGUNTA       que trabalho publicado sustenta ou contradiz esta hipotese, e quantas
               origens REALMENTE independentes existem?
ARESTA CHAVE   SAME_ORIGIN — a unica que impede tres papers de um ensaio contarem como tres
NAO PODE       conclusao de paper apresentada como facto de campo em Italia ·
               afiliacao do autor lida como local do estudo
```

**O que já temos:** 88 publicações (86 com DOI), 60 investigadores com ORCID, 5 temas, 34
casos de resistência com autoridade citada.

**O que falta:**

```
ISSUE_IDS ..........  0 de 88
REGION_IDS .........  0 de 88   (o unico geografico e COUNTRY_OF_FACT = IT)
trial_id / dataset_id  ausente — e sem ele a aresta SAME_ORIGIN nao se instancia
concentracao .......  45 de 88 em vinha x flavescencia, 40 em trigo duro x fusarium
```

```
SEM SAME_ORIGIN, CONVERGENCIA E ARITMETICA DE DUPLICADOS.
```

Enquanto `trial_id` não atravessar a fronteira, esta família **não pode alimentar contagem
de independência** — e é exatamente para isso que ela existe.

**Gap principal:** `GAP-IT-007`.

---

## 4 · O QUE ESTAMOS A COLETAR DE MAIS, E DE MENOS

### De mais — volume sem chave

| família | registos | por que é excesso |
|---|---:|---|
| `cropEconomicWeight` | 2.978 | **13** passam o gate de cliente. `ISSUE_IDS` 0 %. 2.978 linhas para contextualizar, e a Intelligence precisa de uma por par |
| `competitors` | 577 | camada única (comunicação), `ISSUE_IDS` 0 %, região real em 4. Volume que não cruza |
| `products.relationships` | 2.030 | não é excesso de linhas: é excesso **do mesmo produto**. 2.030 relações para **19** produtos com uso lido |

### De menos — a coluna vertebral

| família | registos | por que é escasso |
|---|---:|---|
| **FIELD OBSERVATIONS** | 122 | a única família que sabe **onde e quando**, e é a menor das grandes. 40 completas |
| **WEATHER / CLIMATE** | 44 | 3 contratos existem (`IT-T2-001/002/004`) e são todos `P1`. Zero valores de problema em comum com o campo |
| **AGRONOMIC WINDOWS** | 7 + 29 | e nenhuma confirmada |
| **COMPETITOR REGISTRATIONS** | **0** | a metade forte da concorrência não existe |
| **COMPETITOR LABELS** | **0** | sem ela, Label Intelligence é inventário |

```
TEMOS 2.978 LINHAS DE PESO ECONOMICO E 122 OBSERVACOES DE CAMPO.
A PROPORCAO ESTA INVERTIDA EM RELACAO AO QUE AS PERGUNTAS PEDEM.
```

---

## 5 · AS PRÓXIMAS 200 FONTES

> **Antes do número: uma condição.** Enquanto `GAP-IT-001` estiver aberto, **fonte nova não
> melhora cruzamento nenhum** — só aumenta o denominador. Duzentos boletins novos, sem
> vocabulário de problema, produzem duzentos documentos que também não atravessam.

```
SE A NORMALIZACAO NAO VIER PRIMEIRO, 200 FONTES NOVAS SAO 200 DOCUMENTOS QUE NAO CRUZAM.
```

A base italiana **contratada** hoje tem **13 fontes**: T3 campo ×5 · T2 clima ×3 ·
T1 produção ×1 · T4 regulatório ×1 · T5 ciência ×1 · T7 organizações ×1 · T9 empresa ×1.

| família | gap | cobertura hoje | quantidade desejável | que tipo de produtor de informação procurar | prioridade |
|---|---|---|---|---|---|
| **REGISTO DE CONCORRENTE** | `GAP-IT-004` | **0** | **0 fontes novas** | nenhuma: é recorte da fonte que já temos | **P0** |
| **LABEL — linha de uso** | `GAP-IT-003` | 19 de 163 produtos | **0 fontes novas** | nenhuma: reprocessamento dos rótulos guardados | **P0** |
| **VOCABULÁRIO DE PROBLEMA** | `GAP-IT-001` | 24 de ~172 | **1 autoridade** | registo de nomenclatura com autoridade externa — EPPO Global Database já está registada (`EU-T3-001`) e continua `NÃO SEI` | **P0** |
| **CAMPO — boletins fitossanitários** | `GAP-IT-002` | 5 contratos, ~6 regiões | **NÃO DÁ PARA DETERMINAR AINDA** — ver abaixo | serviços fitossanitários regionais, consórcios provinciais, organizações de produtores que publicam boletim datado com fase fenológica | **P0** |
| **CLIMA / AGROMETEO** | `GAP-IT-002` | 3 contratos, `P1` | proporcional às regiões de campo cobertas | serviços agrometeorológicos regionais (ARPA·), com série e não só captura | P1 |
| **CIÊNCIA — identidade de ensaio** | `GAP-IT-007` | 0 | **NÃO SEI** | repositórios que publicam o dataset e registos de ensaio — não mais índices bibliográficos | P1 |
| **VOZ DE CAMPO com data e lugar** | `GAP-IT-005` | 0 utilizáveis | **NÃO SEI** | cooperativas, consórcios de tutela, assistência técnica regional. **Não** mais plataformas sociais | P1 |
| **MERCADO — volume e comércio** | `GAP-IT-009` | 0 | 1–2 séries | ISTAT e Eurostat, já registadas | P2 |
| **MERCADO DE DEFENSIVO** | `GAP-IT-009` | 0 | **NÃO SEI** | nunca foi procurada fonte pública. Registar como `NÃO SEI`, não como zero | P2 |

### Por que a quantidade de boletins de campo fica em `NÃO DÁ PARA DETERMINAR AINDA`

Determinar «quantos boletins» exige saber **quantos pares cultura × problema × região** o
produto precisa cobrir. Esse recorte não está declarado em lado nenhum desta árvore — e
inventá-lo aqui seria escolher o universo pela facilidade de coletar, exatamente o que
`§12` proíbe.

```
O QUE SE PODE DIZER COM PROVA:
   as 5 fontes T3 contratadas cobrem ~6 regioes das 20 italianas.
   o que NAO se pode dizer e se 20 e a meta — porque ninguem declarou o universo.
   ISSO E UM CONTRATO DE UNIVERSO EM FALTA (INT-LAW-111), NAO UM NUMERO EM FALTA.
```

---

## 6 · DUPLICAÇÃO ENTRE FERRAMENTAS

O mapa completo está em [`INTELLIGENCE-DATA-FLOW-ITALY.md`](INTELLIGENCE-DATA-FLOW-ITALY.md).
O resumo:

| dado recolhido uma vez | alimenta |
|---|---|
| boletim fitossanitário regional | Crop Windows · Opportunity Radar · Competitor Watch · Field Voices · Disease Intelligence |
| rótulo oficial | Portfolio · Label Intelligence · Crop Windows · Opportunity Radar · Competitor Watch |
| registo nacional de produto | Portfolio · Future Radar · Label Intelligence · Competitor Watch |
| publicação científica | Scientific Intelligence · Future Radar · Opportunity Radar |

```
NENHUM DADO DESTA LISTA PRECISA DE SER RECOLHIDO DUAS VEZES.
QUATRO FAMILIAS ALIMENTAM AS NOVE SUPERFICIES.
```

O que impede a partilha **não é a coleta** — é a normalização em falta. O mesmo boletim que
serviria cinco superfícies hoje serve uma, porque o problema que ele nomeia não tem
identidade.

---

## 7 · O QUE FICA EM `NÃO SEI`

```
· o universo-alvo do produto em Italia (quantos pares cultura x problema x regiao)
· se as publicacoes italianas declaram trial_id — nunca foi tentada a extracao
· se existe fonte publica de mercado de defensivo em Italia — nunca foi procurada
· se a familia de voz de campo e alcancavel: NOT REACHED, nao KILL. Apify nunca testado
· quantas fontes de campo sao precisas — falta o contrato de universo, nao o numero
```

`NÃO SEI` aqui é resultado, não lacuna por preguiça: cada linha diz **o que seria preciso
medir** para deixar de ser `NÃO SEI`.
