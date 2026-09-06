# MAPA DE FONTES — ITÁLIA

`COUNTRY = IT` · primeira passagem · **estado medido em 2026-08-30**

> ## RECONCILIAÇÃO — P0.2 · PASSO 03 (2026-09-06)
>
> **Este documento é a PRIMEIRA PASSAGEM e continua sendo ela.** O registro canônico de
> fontes é `ATLAS-DE-FONTES-EAME.md`; onde os dois divergirem, vence o atlas — e este bloco
> diz exatamente onde e por quê. **O corpo abaixo não foi reescrito:** uma medição de
> 30/08/2026 é registro, não erro, e apagá-la faria a régua parecer sempre certa.
>
> 1. **`IT-T1-001` (ISTAT) — aqui `NÃO SEI`, hoje `GREEN`.** A rota SDMX foi alcançada
>    depois desta passagem (`sdmx.istat.it`, dataflow `101_1015`), com `scripts/italia_istat.py`,
>    o mapa NUTS 2006→2021 e números de 2024 conferidos contra o Eurostat. A ficha está no
>    atlas, em `T1 · CROP & PRODUCTION — ITALY`. `NOT_REACHED != DOES NOT EXIST` — e a prova
>    é esta linha ter mudado de estado sem ser removida.
>
> 2. **`IT-T3-004` e `IT-T3-006` são a MESMA fonte**, medida duas vezes. Aqui, `IT-T3-004`
>    é o Friuli-VG com «seção existe; nenhum bollettino de milho localizado». Na segunda
>    rodada a mesma fonte — **ERSA, o serviço fitossanitário do Friuli-Venezia Giulia** —
>    devolveu **10 boletins de MILHO em 2026**: o que faltava na primeira era a subpágina
>    `bollettini-2026`, não o dado. **O ID canônico é `IT-T3-006`**, que é o que os dados e o
>    atlas usam. `IT-T3-004` fica como a primeira medição e **não pode ser reemitido** para
>    outra fonte — ID não se recicla.
>
> 3. **Por consequência, a manchete negativa do §3 cai em parte.** «O sistema italiano de
>    boletins de campo é construído para permanentes e hortícolas, não para o milho»
>    continua verdadeira **para Veneto, Lombardia e Piemonte, que foi onde se mediu**. Para o
>    **Friuli-Venezia Giulia é falsa**: há série de milho, semanal, sob difesa integrata
>    obbligatoria. Uma varredura que não achou não é uma fonte que não publica.
>
> 4. **As contagens de boletins do Vêneto desta passagem são as MENORES.** A tabela do §3
>    diz «17 olivícola · 17 hortícola · 16 videira · 15 frutícola»; a matriz regional
>    (`data/samples/IT-FONTES/ITALY-REGIONAL-COVERAGE-MATRIX.json`, mesma data de captura)
>    conta **28 olivo · 25 frutícola · 21 hortícola · 16+ vite**. As duas medições são da
>    mesma rota e do mesmo dia, e a segunda é a que a ficha `IT-T3-OP` do atlas usa ao
>    comparar o Vêneto com a Puglia. **Vale a maior**, e a menor fica registada como a
>    primeira varredura.
>
> 5. **Onde cada ID está documentado.** Têm ficha no atlas canônico: `IT-T4-001`,
>    `IT-T4-001-ETICHETTA`, `IT-T1-001`, `IT-T3-001`, `IT-T3-002`, `IT-T3-006`,
>    `IT-T3-LOTTA-OBBLIGATORIA`, `IT-T3-LAMMA`, `IT-T3-OP`, `IT-T9-001`, `IT-T11-001`,
>    `EU-T1-001`, `EU-T5-001`. Documentados **só aqui**, como primeira passagem e sem ficha
>    canônica: `IT-T4-002`, `IT-T3-003`, `IT-T3-004`, `IT-T3-005`. Documentado só aqui e
>    reconciliado como **recorte** de fonte já fichada: `IT-T5-001` = recorte italiano de
>    `EU-T5-001` (OpenAlex) — **não é fonte nova e não conta duas vezes**.

Este documento é o **PHASE IT-1** da missão Sintonia Italia: o mapa curto das melhores
portas italianas. Não é lista decorativa e não pretende cobertura nacional. Cada linha
diz o que a fonte **prova** e o que ela **não prova**, porque a segunda coluna é a que
evita afirmação inflada mais tarde.

Regra que organiza tudo o que vem abaixo:

> **API / OPEN DATA / DOWNLOAD OFICIAL primeiro.** Scraping só quando não há rota
> estruturada, e rota paga só depois de alvo definido.

---

## 0 · O QUE FOI REUSADO, E O QUE A ITÁLIA OBRIGOU A CONSTRUIR

A missão manda perguntar, antes de cada passo: *isto é um problema novo da Itália ou já
temos método provado?* O balanço honesto desta rodada:

| Método | Origem | Uso na Itália |
|---|---|---|
| RAW → NORMALIZED → ANALYTICAL, hash, versão de fonte | Brasil/Espanha | **REUSE** integral |
| `SOURCE_LOCATION ≠ FACT_LOCATION` | Espanha | **REUSE** — a sede da empresa é local da EMPRESA |
| `EXPIRY ≠ WITHDRAWAL`, anomalias de vencimento | ES-T4-005 (ROPF) | **REUSE** — e a Itália reproduziu a mesma classe de anomalia |
| Eurostat NUTS 2 para escala de cultura | EU-T1-001 | **REUSE** — a rota já cobria IT |
| OpenAlex dirigido + ORCID + recorrência | ES-T5-002 | **REUSE** integral, com as mesmas cautelas |
| Extração de texto de PDF | `scripts/pdf_text.py` | **REUSE**, com correção nova de fonte deslocada |
| **Rota da etichetta oficial** | — | **NOVO** — a Espanha não tem equivalente |
| **Identidade de titular por sede declarada** | — | **NOVO** — a Itália tem 7 razões sociais do grupo |
| **Prova aritmética de hierarquia de rubricas** | — | **NOVO** |

Três coisas foram construídas porque a Itália realmente as exigiu. Todo o resto é reuso.

---

## 1 · REGULATORY — a porta mais forte da Itália

### `IT-T4-001` · Ministero della Salute — Banca dati dei prodotti fitosanitari

```
LEVEL:              NATIONAL
STRUCTURED_ROUTE:   SIM — CSV, JSON e XML publicados lado a lado
ACCESS:             https://www.dati.salute.gov.it/it/dataset/fitosanitari/
                    /sites/default/files/opendata/PROD_FTS_6_<AAAAMMDD>.{csv,json,xml}
COST:               zero · CC BY 4.0 · sem chave
FRESHNESS:          o NOME DO ARQUIVO é a versão. Observado PROD_FTS_6_20260824.
DEPTH:              1970 → hoje. 17.695 produtos, 576 titulares.
ACCESS_STATUS:      GREEN
```

**PROVA:** número de registro · produto · titular e sede · datas de registro e de
**vencimento** · estado administrativo · substâncias ativas e teor · formulação ·
indicações de perigo · importação paralela · **motivo e datas da revogação**.

**NÃO PROVA:** cultura · alvo · dose · venda · participação de mercado · disponibilidade
comercial. E, medido nesta rodada, **não prova sequer vigência pelo campo de estado** —
ver a anomalia abaixo.

O nome do arquivo muda a cada versão e **precisa ser descoberto na página do dataset**.
Fixar o nome no código quebra na próxima publicação.

### `IT-T4-001-ETICHETTA` · a etichetta autorizada — **rota nova**

```
LEVEL:              NATIONAL (por produto)
STRUCTURED_ROUTE:   NÃO — servlet HTML + PDF
ACCESS:             POST FitosanitariServlet ACTION=cercaProdotti NUMERO_REGISTRAZIONE=<reg>
                    → EtichettaServlet?id=<ID_INTERNO> → PDF
COST:               zero
ACCESS_STATUS:      GREEN COM RESSALVAS OPERACIONAIS
```

**Esta rota derruba uma limitação que o Atlas registrava como fechada.** A ficha anterior
dizia que a Itália *"não sustenta hoje o mesmo cruzamento cultura × alvo que a França
sustenta"*. A premissa continua certa — o CSV não traz cultura nem alvo — mas a conclusão
não: o rótulo autorizado traz `Coltura × Patogeno × Dose × Volumi × Intervallo × N° max
applicazioni`, e é publicado pelo mesmo Ministério. **O dado existia; faltava a rota.**

**PROVA:** o uso autorizado, incluindo cultura, alvo com nome científico, dose, intervalo
entre tratamentos, número máximo de aplicações e intervalo de segurança. Mais a **data do
rótulo**, que vem no nome do arquivo servido (`15232_etichettaCLP_29042022.pdf`).

**NÃO PROVA:** que o produto esteja à venda; que seja recomendado; que a cultura esteja
associada a *todos* os alvos listados — a associação vive numa coluna de tabela que a
extração de PDF perde.

**Três defeitos DA FONTE, medidos.** São ficha de saúde, não motivo de abandono:

1. **Cadeia TLS incompleta.** O host envia só a folha, sem o intermediário
   `TI Trust Technologies OV CA`. `curl` recusa — e recusa **com razão**. A correção não é
   desligar verificação: é buscar o intermediário no campo AIA do próprio certificado.
2. **Cabeçalho `Public-Key-Pins` malformado** (linha partida, sem `:`). `curl` aborta com
   *Header without colon*; o parser do Python tolera. A rota é Python por medição, não
   por estética.
3. **Uma busca por sessão.** Reusar o `JSESSIONID` devolve **vazio**, não erro. Vazio de
   estrangulamento é indistinguível de vazio de inexistência: um laço ingênuo publicaria
   1 achado e 162 ausências falsas. Sessão nova por consulta, com retentativa.
   `READ FAILURE ≠ ZERO`.

### `IT-T4-002` · categoria fitoiatrica (taxonomia oficial)

O servlet publica a lista fechada de categorias (`ACARICIDA`, `DISERBANTE`, `FUNGICIDA`,
`INSETTICIDA`, `MOLLUSCHICIDA`…) e o CSV traz o campo `attivita` por produto. É o
equivalente **regulatório** das categorias comerciais de catálogo — e a distância entre
os dois é justamente o que se quer medir, nunca o que se quer harmonizar.

---

## 2 · PUBLIC AGRICULTURAL DATA / CROP SCALE

### `EU-T1-001` · Eurostat `apro_cpshr` — **reuso, já provado para IT**

```
LEVEL:              NATIONAL + NUTS 2 (21 regiões italianas, todas reportando)
STRUCTURED_ROUTE:   SIM — API REST JSON-stat 2.0, sem chave
FRESHNESS:          anual · fonte declarou 2026-05-28 · último ano completo 2024
DEPTH:              2000–2024
ACCESS_STATUS:      GREEN
```

**PROVA:** área por cultura, nacional e por NUTS 2, com 25 anos de série.

**NÃO PROVA:** rendimento regional — `YLD_HUMD_EU_T_HA` **não existe em NUTS 2**, medido.
E **não cobre culturas permanentes em NUTS 2**: oliveira (`O1000`) e videira (`W1000`) têm
área nacional e **nenhum** recorte regional nesta fonte. Isso é `NÃO SEI`, não zero, e
significa que oliveira e videira **não podem ser regionalizadas por aqui** — exigem ISTAT.

**Armadilha própria da fonte, e ela é séria:** as rubricas **somam-se a si mesmas**.
`C1100` (trigo e espelta, 1697,8 mil ha) **é** `C1110` (520,3) + `C1120` (1177,4). Somar
níveis diferentes conta o mesmo hectare duas vezes. Por isso o ranking italiano é
publicado em **nível commodity**, com a aditividade **provada aritmeticamente** (diferença
0,00) e não assumida.

### `IT-T1-001` · ISTAT — coltivazioni

```
ACCESS_STATUS:      NÃO SEI — permanece não alcançada
```

Não foi reavaliada nesta rodada porque `EU-T1-001` já entregou o que a missão pedia.
Continua sendo **a** porta para regionalizar oliveira e videira, que o Eurostat não dá.
**Não alcançada ≠ avaliada e recusada.**

---

## 3 · REGIONAL FIELD / PHYTOSANITARY

A Itália é fortemente descentralizada: **20 regiões, cada uma com serviço fitossanitário
próprio.** A missão manda não cadastrar as 20 de uma vez, e sim começar pelas que importam
para os casos candidatos. Foram medidas as **três primeiras regiões de milho** —
Veneto, Lombardia, Piemonte — mais Friuli-Venezia Giulia.

| SOURCE_ID | Região | Rota | Estado | O que se mediu |
|---|---|---|---|---|
| `IT-T3-002` | Veneto | HTML + PDF, caminho previsível | **GREEN** | 2026: **17 olivícola · 17 hortícola · 16 videira · 15 frutícola · 2 herbáceas** |
| `IT-T3-003` | Lombardia | HTML + PDF (portal WCM) | **GREEN** | 2026: **6 videira · 4 macieira · 0 herbáceas** |
| `IT-T3-004` | Friuli-VG | HTML, seção "colture erbacee" | **YELLOW — SUPERADA** | seção existe; nenhum bollettino de milho localizado. **Mesma fonte que `IT-T3-006`**: na segunda rodada, pela subpágina `bollettini-2026`, apareceram **10 boletins de milho em 2026**. Ver o bloco de reconciliação no topo. |
| `IT-T3-005` | Piemonte | HTML + PDF | **YELLOW** | *disciplinari* por cultura + decretos de deroga (Art. 53) |
| `IT-T3-001` | Emilia-Romagna | PDF semanal provincial | **YELLOW** (herdado) | não reavaliada nesta rodada |

**O achado desta camada é NEGATIVO, e é dos mais úteis da rodada:**

> **O sistema italiano de boletins de campo é construído para culturas permanentes e
> hortícolas, não para o milho.** Nas duas maiores regiões produtoras de milho do país,
> 2026 produziu **75 boletins de permanentes/hortícolas contra 2 de herbáceas**
> (Vêneto 65, Lombardia 10) — e o único boletim de herbáceas do Veneto que foi aberto
> trata de **beterraba açucareira / *Cercospora beticola***, não de milho.

`SOURCE FAILURE ≠ ZERO` — mas isto **não** é falha de leitura: as três fontes responderam
`HTTP 200` e foram lidas. É **ausência medida de cobertura**, e ela decide qual caso
italiano é demonstrável hoje.

**Distinção que a missão exige e que esta camada torna concreta:**
`ISSUE_KNOWN` (o *disciplinare* diz quais problemas a cultura tem) **≠** `CURRENT_SIGNAL`
(o *bollettino* diz o que está acontecendo agora). O Piemonte publica o primeiro para
milho; nenhuma das regiões medidas publicou o segundo.

---

## 4 · SCIENCE

### `IT-T5-001` · OpenAlex — recorte italiano

```
LEVEL:              NATIONAL (por afiliação de autor)
STRUCTURED_ROUTE:   SIM — API REST, sem chave
ACCESS_STATUS:      GREEN
```

**PROVA:** volume de atenção científica por `cultura × problema`, autores recorrentes,
ORCID, afiliação declarada, última atividade.

**NÃO PROVA:** pressão de campo · demanda · que o problema esteja ocorrendo agora · e,
crucialmente, **não prova a região do fenômeno**: `REGION_OF_STUDY ≠ AUTHOR AFFILIATION`.

Consulta **dirigida**, nunca paginação larga. Denominador só existe junto com o recorte
que o gerou.

---

## 5 · ADAMA — o gêmeo público **não** foi obtido

### `IT-T9-001` · adama.com/italia

```
ACCESS_STATUS:      RED PARA ESTE AMBIENTE — bloqueio de origem
```

`adama.com` devolve **HTTP 403 "Access Denied"** com referência de WAF a todas as rotas
testadas, **inclusive `/robots.txt`**. O bloqueio não vem do proxy desta sessão
(`recentRelayFailures` vazio): é da origem. Duas vias de saída distintas foram testadas.

**Consequência declarada, e ela é uma recusa deliberada:** o enunciado da missão informa
que o site apresenta ~52 produtos em 27 Erbicidi / 14 Fungicidi / 6 Insetticidi /
5 Speciali, e manda **reproduzir na fonte, não copiar sem verificar**. Não foi possível
verificar. Portanto esses números **não entram em nenhum artefato como fato**, e ficam
registrados como `UNVERIFIED_INPUT`.

**O que se perde com isso, nomeado:** `POSITIONING` · `TECHNICAL_CLAIMS` ·
`COMMERCIAL_CLAIMS` · `PACK_SIZES` · `LAUNCH_SIGNALS` · pertencimento ao Catalogo 2026 ·
`PUBLIC_ADAMA_MAIZE_SIGNAL`. Tudo isso é **camada de afirmação do fabricante** e continua
`NOT_COLLECTED`.

**O que NÃO se perde:** a resposta **regulatória** da ADAMA italiana, que é mais forte
para a pergunta da missão e veio inteira pela rota da etichetta.

---

## 6 · COMPETITORS · TECHNICAL MEDIA · COOPERATIVES · SOCIAL

| Categoria | Estado | Motivo |
|---|---|---|
| COMPETITORS | `NOT_STARTED` | A missão restringe a casos prioritários. O caso italiano só se fechou no fim desta rodada. |
| TECHNICAL MEDIA (AgroNotizie/Image Line, Fitogest) | `IDENTIFIED_NOT_COLLECTED` | Existem e são úteis para regulatório/lançamento/evento. `MEDIA_SIGNAL ≠ FIELD_SIGNAL`. |
| COOPERATIVES / PRODUCER ORG. | `NOT_STARTED` | Uma pista real apareceu sozinha: **Co.Pro.B.** opera um DSS de *Cercospora* citado pelo boletim oficial do Veneto — cooperativa que **produz sinal de campo**. |
| SOCIAL / PUBLIC VOICE | `NOT_STARTED` | A missão manda vir depois dos pares. Os pares só ficaram prontos agora. |

**Nenhuma rota paga foi usada. Custo total desta rodada: US$ 0,00.**

---

## 7 · PLACAR

| | |
|---|---|
| Fontes italianas com rota medida nesta rodada | **9** |
| GREEN | 5 (`IT-T4-001`, `IT-T4-001-ETICHETTA`, `EU-T1-001`, `IT-T3-002`, `IT-T3-003`) |
| YELLOW | 3 (`IT-T3-004` — **superada por `IT-T3-006`, GREEN** —, `IT-T3-005`, `IT-T3-001` herdado) |
| RED / bloqueada | 1 (`IT-T9-001`, adama.com) |
| NÃO SEI (não alcançada) | 1 (`IT-T1-001`, ISTAT) — **alcançada depois; hoje GREEN e fichada no atlas** |
| Rotas estruturadas (API/CSV/JSON/XML) | 3 |
| Fontes regionais de campo | 5 regiões |
| Custo | **US$ 0,00** |
