# LOCAL DISEASE COLLECTION — ITÁLIA / VENETO
## Pacote de coleta local para a missão de Inteligência

> **O que este documento é.** O registro do que foi realmente coletado neste
> computador físico, com VPN italiana, e que o ambiente remoto não alcançava.
> Cada número foi recontado abrindo os arquivos — e depois **auditado por quatro
> agentes adversariais** que recalcularam tudo por conta própria. Onde eles me
> pegaram errado, o número deles está aqui e o meu está marcado como errado.
>
> **O que este documento NÃO é.** Não há aqui modelo, previsão, classe de
> severidade nem backtest. Essa é a missão da outra aba.

---

## LEI ZERO — como ler este documento

| Estado | Significa |
|---|---|
| `PRESERVED` | os bytes estão em disco, com SHA256 conferido |
| `COLLECTION_FAILED` | a coleta falhou — **não é zero** |
| `NOT_PRESERVED` | não foi preservado — **não é zero** |
| `NOT_KNOWN` | não foi medido — **não é zero** |
| `DISCOVERED` | a URL foi provada existir, **mas o documento não está em mãos** |
| `CATALOG_AVAILABILITY` | a fonte *declara* que existe |
| `ACTUAL_DATA_PRESERVED` | o dado está em disco e foi contado |

**DISCOVERED ≠ COLLECTED.** **Catálogo ≠ dado.** **Ano disponível ≠ ano completo.**
**Menção léxica ≠ ocorrência.** **Tempo ≠ doença.** **Modelo ≠ observação.**

### Como contar sem inflar

```
PRESERVED_COUNTING_RULE =
  preservation == "PRESERVED"  AND  counts_as_preserved_document != false
```

Contar as linhas `PRESERVED` cruas dá **1832** e está **errado**: inclui as 182
capturas falhas em quarentena e conta duas vezes os manifestos que foram
substituídos pela versão verificada. A contagem certa é **1439**.

---

## A · BRANCH / HEAD

```
COLLECTION_ID       = ITALY-VENETO-DISEASE-LOCAL-COLLECTION-2026-09
COLLECTION_BRANCH   = claude/disease-local-collection-italy
CANONICAL_BASE      = origin/sintonia/canonical @ bdb57cf7379a4b8b94b3ef117fb3da469fca0764
WORKTREE            = C:\disease-local-collection-italy
CANONICAL_TOUCHED   = NO
P0_2_TOUCHED        = NO
PORTAL_TOUCHED      = NO
```

Branch criada a partir de `origin/sintonia/canonical` num worktree isolado. O
*upstream* foi desligado de propósito (`git branch --unset-upstream`) para que
nenhum `git push` sem argumento possa mirar o canônico.

---

## B · A COLETA TERMINOU?

| Job | Estado | Resultado |
|---|---|---|
| Série diária ARPAV (1.038 pedidos) | **FINISHED** | ok=1038 fail=0 |
| Inventário do arquivo mensal | **FINISHED** | 72 pastas, 347 arquivos |
| Preservação do arquivo mensal | **FINISHED** | ok=347 fail=0, 347/347 verificados |
| Preservação Annate/FAS/boletim vinha | **FINISHED** | ok=46 fail=0, 46/46 verificados |
| Catálogo de estações com coordenadas | **FINISHED** | 8 respostas, 14/14 estações |
| Frota de reconhecimento (12 batedores) | **PARTIAL — interrompida** | 6 devolveram resultado, 6 cortados |
| Red Team adversarial (4 lentes + 24 verificadores) | **FINISHED** | 28 agentes, 0 erros |

```
BACKGROUND_JOBS_RUNNING  = 0
BACKGROUND_JOBS_FINISHED = 6
BACKGROUND_JOBS_FAILED   = 0
BACKGROUND_JOBS_STOPPED  = 1  (frota de reconhecimento, ao fim da sessão anterior)
```

⚠️ **6 batedores não entregaram resultado estruturado.** Isso é `NOT_COMPLETED`,
**não** é "aquelas frentes estão vazias". Frentes sem relatório: F1e (Wayback),
F2b (Veneto Agricoltura/vite), F3b (catálogo de estações), F4 (open data),
F5 (relatórios anuais), F6 (outras pragas). O material bruto que chegaram a
gravar está inventariado por hash e **foi lido nesta sessão** — e é justamente
lá que estava o desfecho de doença que eu tinha declarado inexistente (seção O).

---

## C · NÚMEROS RECONTADOS E CORREÇÕES

### Disco

```
RAW_FILES_TOTAL_ON_DISK                = 1912
RAW_FILES_SOURCE_DOCUMENTS             = 1674   (exclui scripts e quarentena)
RAW_FILES_TOOLING_SCRIPTS_EXCLUDED     =   56   (.py escritos pelos agentes)
RAW_FILES_QUARANTINED_FAILED_CAPTURES  =  182   (captura falha, ver seção L)
RAW_BYTES_SOURCE_DOCUMENTS             = 706.267.976  (~673,6 MB)
RAW_DISTINCT_BY_SHA256                 = 1644
RAW_DUPLICATE_CONTENT                  =   29
RAW_EMPTY_FILES_NOT_ZERO               =    1
DISTINCT_PRESERVED_ARTIFACTS           = 1439   (1038 diários + 347 mensais + 46 docs + 8 geo)
```

### O que eu disse errado, e o valor certo

| Eu disse | Medido / auditado | Como foi pego |
|---|---|---|
| "2 PDFs do boletim peronospora preservados" | eram **cascas de HTML**; refeito, agora são PDFs reais | bytes mágicos |
| "arquivo semanal da vinha não existe" | **existe na Regione del Veneto, 2024–2026** | batedor F1a/F1b |
| "os 2 boletins da vinha são boletins" | são **planilhas de risco de MODELO** (Vitimeteo, experimental) | Red Team L4 |
| "26 temporadas de Annate, 2000-01 a 2025" | **25 temporadas, 2001–2025**; 2005 aparece duas vezes; 2000 não existe | Red Team L1/L4 |
| "17 Rapporti FAS" (implícito: sobre doença) | são relatórios de **VENDA de defensivos**, não de doença | Red Team L4 |
| "`years: 2010-2026`" por variável | é **união entre estações**, não o alcance de nenhuma | Red Team L2/L3 |
| "OUTCOMES_NEW = nenhum" | **errado** — existem 6 arquivos com desfecho numérico real | Red Team L4 |
| "~77 MB de dado diário" | **82.578.751 B** como recebido, **2.651.852 B** em disco (gzip) | era estimativa |
| "13 das 14 estações ≥ 99,3 %" | **correto** para bagnatura sozinha. Mas ver a coluna conjunta abaixo | Red Team L3 |

---

## D · A API ARPAV ENCONTRADA (o achado central)

O formulário oficial entrega CSV **por e-mail**. Mas a própria página da ARPAV
chama, em JavaScript, uma API REST pública. Os endereços não foram adivinhados:
foram lidos do código da própria ARPAV e depois provados com requisição real.

```
EMAIL_REQUIRED_FOR_DAILY_DATA = NO   (para as 5 variáveis abaixo)
DIRECT_API_DAILY_DATA         = YES
AUTH_REQUIRED                 = NO
```

| Endpoint | O que devolve | Provado |
|---|---|---|
| `https://api.arpa.veneto.it/REST/v1/meteo_stazioni_dispenser` | catálogo de estações | 200, 26.168 B |
| `https://api.arpa.veneto.it/REST/v1/meteo_sensori_dispenser` | catálogo de sensores + anos declarados | 200, 379.548 B |
| `https://api.arpa.veneto.it/REST/v1/meteo_storici?coordcd=<tipo>&anno=<ano>` | estações + **lat/lon/altitude/comune** | 200, 8 respostas |
| `https://api.arpa.veneto.it/REST/v1/meteo_storici_tabella?codseq=<sensor>&anno=<ano>` | **dado diário do ano inteiro** | 200, 1.038 respostas |
| `https://api.arpa.veneto.it/REST/v1/meteo_storici_totali?codseq=<sensor>&anno=<ano>` | totais do ano | 200 |
| `https://api.arpa.veneto.it/REST/v1/dispenser_meteo_giorno_sensore` | — | **HTTP 500** com e sem parâmetros: `DIRECT_GET_NOT_PROVED` |

Reconfirmado pelo Red Team com `curl` sem cabeçalho, sem cookie e sem chave:
`http=200 bytes=74176 type=application/json`.

**Limites declarados pela própria fonte:**
- início da série: **1º de janeiro de 2010** (`minDate = 2009-12-31T23:00Z`);
- atualização mensal, no dia 25, incluindo o mês anterior;
- dispenser **horário** existe (`dispenser_meteo_orari_sensore`), desde 2010, **máx. 5 anos por pedido**, por e-mail — `NOT_COLLECTED`;
- ⚠️ a ARPAV avisa: *dias inválidos não são sinalizados — a linha do dia simplesmente falta*.

---

## E · ESTAÇÕES E SENSORES

⚠️ Separação obrigatória:

```
# CATÁLOGO — toda a região do Veneto. NÃO é dado preservado.
ARPAV_CATALOGUE_STATIONS_REGIONWIDE              = 315
ARPAV_CATALOGUE_SENSORS_REGIONWIDE               = 1619
ARPAV_CATALOGUE_LEAF_WETNESS_SENSORS_REGIONWIDE  = 78

# PRESERVADO — subconjunto de Treviso realmente em disco
DAILY_STATIONS_PRESERVED        = 14
DAILY_SENSOR_SERIES_PRESERVED   = 64
DAILY_STATIONS_WITH_COORDINATES = 14  (14/14)
```

**Que fatia do catálogo isto é** (medido pelo Red Team, reproduzido):

```
1038 / 23.586 combinações (sensor, ano) que a ARPAV declara = 4,40 %
1038 / 11.739 restrito às 5 variáveis coletadas             = 8,84 %
 232 /  1.253 anos-sensor de bagnatura fogliare declarados  = 18,5 %
```

Mas **dentro de Treviso a coleta está completa**: o catálogo declara exatamente
14 estações de Treviso com bagnatura fogliare, e as 14 estão preservadas.

As 14 estações, com coordenadas publicadas pela fonte (`manifests/station-geo.json`):

| codseqst | Estação | Comune | lat | lon | alt (m) |
|---|---|---|---|---|---|
| 300000047 | Castelfranco Veneto | CASTELFRANCO VENETO | 45.69492 | 11.94778 | 49 |
| 300000092 | **Conegliano** | CONEGLIANO | 45.88132 | 12.28233 | 90 |
| 300000133 | Volpago del Montello | VOLPAGO DEL MONTELLO | 45.78502 | 12.11305 | 122 |
| 300000134 | Zero Branco | ZERO BRANCO | 45.60991 | 12.12088 | 18 |
| 300000135 | Vazzola - Tezze | VAZZOLA | 45.81169 | 12.34190 | 40 |
| 300000136 | Gaiarine | GAIARINE | 45.89218 | 12.49349 | 17 |
| 300000137 | Roncade | RONCADE | 45.64140 | 12.39589 | 7 |
| 300000138 | Villorba | VILLORBA | 45.74894 | 12.23496 | 41 |
| 300000139 | **Valdobbiadene - Bigolino** | VALDOBBIADENE | 45.88206 | 12.00710 | 225 |
| 300000140 | **Farra di Soligo** | FARRA DI SOLIGO | 45.90212 | 12.10446 | 169 |
| 300000141 | Oderzo | ODERZO | 45.76569 | 12.52427 | 7 |
| 300000142 | Maser | MASER | 45.77892 | 11.94237 | 100 |
| 300000145 | Ponte di Piave | PONTE DI PIAVE | 45.71712 | 12.52394 | 3 |
| 300004120 | Breda di Piave - Via Bovon | BREDA DI PIAVE | 45.72323 | 12.37967 | 17 |

---

## F · BAGNATURA FOGLIARE — a entrega mais importante

```
LEAF_WETNESS_AVAILABLE               = YES
LEAF_WETNESS_PRESERVED               = YES
LEAF_WETNESS_STATIONS_PRESERVED      = 14
LEAF_WETNESS_SENSOR_SERIES_PRESERVED = 14
LEAF_WETNESS_FILES                   = 232
LEAF_WETNESS_ROWS                    = 82.125
LEAF_WETNESS_UNIT                    = "% T"  (percentual do tempo com folha molhada)
VARIABLE_CODE                        = BFOGL
```

⚠️ **`LEAF_WETNESS_YEARS_MIN/MAX = 2010/2026` é UNIÃO entre estações**, não o
alcance de nenhuma delas em particular. 13 estações cobrem 2010–2026 (17 anos
cada = 221 arquivos); **Breda di Piave começa em 2016** (11 arquivos).
221 + 11 = 232.

⚠️ **82.125 linhas não são 82.125 dias.** São 14 séries paralelas sobre o mesmo
calendário. A união de datas distintas é **6.056 dias**. Os dois números estão
certos e respondem perguntas diferentes.

### Cobertura na janela `2014-03-01 → 2025-10-31` (**4.263 dias**)

`BFOGL` = só bagnatura. `JOINT4` = **bagnatura E temperatura E umidade E chuva
no MESMO dia** — que é o que um modelo de míldio precisa.

| Estação | BFOGL dias | BFOGL % | **JOINT4 dias** | **JOINT4 %** | última T / UR |
|---|---|---|---|---|---|
| Ponte di Piave (204) | 4263 | 100,00 % | **4262** | **99,98 %** | 2026-07-31 |
| Volpago del Montello (183) | 4261 | 99,95 % | **4257** | **99,86 %** | 2026-07-31 |
| Maser (197) | 4263 | 100,00 % | **4256** | **99,84 %** | 2026-07-31 |
| Gaiarine (186) | 4261 | 99,95 % | **4256** | **99,84 %** | 2026-07-31 |
| Zero Branco (184) | 4263 | 100,00 % | **4254** | **99,79 %** | 2026-07-31 |
| Valdobbiadene - Bigolino (189) | 4259 | 99,91 % | **4250** | **99,70 %** | 2026-07-31 |
| **Conegliano (100)** | 4255 | 99,81 % | **4249** | **99,67 %** | 2026-07-31 |
| Vazzola - Tezze (185) | 4249 | 99,67 % | **4248** | **99,65 %** | 2026-07-31 |
| Villorba (188) | 4248 | 99,65 % | **4244** | **99,55 %** | 2026-07-31 |
| Roncade (187) | 4256 | 99,84 % | **4242** | **99,51 %** | 2026-07-31 |
| Farra di Soligo (195) | 4245 | 99,58 % | **4237** | **99,39 %** | 2026-07-31 |
| Castelfranco Veneto (102) | 4236 | 99,37 % | **4227** | **99,16 %** | 2026-07-31 |
| ⚠️ **Oderzo (196)** | 4257 | 99,86 % | **3608** | **84,64 %** | **2024-01-28** |
| ⚠️ Breda di Piave (577) | 3312 | 77,69 % | **3311** | **77,67 %** | 2026-07-31 |

```
LEAF_WETNESS_ALONE_STATIONS_GE_99_4_PCT = 12 de 14
LEAF_WETNESS_ALONE_STATIONS_GE_99_3_PCT = 13 de 14
JOINT4_STATIONS_GE_99_4_PCT             = 10 de 14   ← o número que importa
JOINT4_STATIONS_GE_99_0_PCT             = 12 de 14
```

⚠️ **A armadilha do Oderzo.** Ele anuncia 99,86 % de bagnatura fogliare, o que
parece ótimo — mas **temperatura e umidade pararam em 28/01/2024**. As safras de
2024 e 2025 são inutilizáveis lá para qualquer modelo que precise de T e UR,
mesmo com os arquivos de bagnatura e chuva desses anos em disco.

⚠️ **Breda di Piave não tem 2014–2015**: o sensor começa em 2016 segundo o
próprio catálogo. Os 951 dias que faltam são ausência real da fonte, não falha
de coleta, e **não são zero**.

### Anos incompletos — o que não pode ser lido como ano cheio

Dos 1.038 arquivos, **60 são de 2026 (ano em curso)** e foram reetiquetados
`YEAR_IN_PROGRESS_PUBLICATION_LAG`. Dos 978 restantes (anos fechados):

```
797 têm o ano civil completo
171 faltam de 1 a 19 dias
 10 estão abaixo de 95 %
  7 estão abaixo de 50 %   ← estes não podem entrar como "ano coletado"
```

Os 7 piores, **medidos**:

| Estação | Variável | Ano | Dias | % |
|---|---|---|---|---|
| Oderzo (196) | TARIA2M | 2024 | 28/366 | **7,7 %** |
| Oderzo (196) | UMID2M | 2024 | 28/366 | **7,7 %** |
| Breda di Piave (577) | TARIA2M, UMID2M, BFOGL, RADSOL, PREC | 2016 | 86/366 | **23,5 %** |

✔️ Das linhas preservadas, **366.978 de 366.978 (100 %) carregam um valor** —
nenhuma linha vazia, nenhum nulo escondido dentro dos valores compostos.

---

## G · HISTÓRICO DIÁRIO PRESERVADO

```
DAILY_METEO_AVAILABLE = YES
DAILY_METEO_PRESERVED = YES
DAILY_FILES           = 1038   (estação × sensor × ano)
DAILY_FILES_FAILED    = 0
DAILY_ROWS            = 366.978
DAILY_ROWS_WITH_VALUE = 366.978  (100 %)
DAILY_BYTES_UNCOMPRESSED_AS_RECEIVED = 82.578.751
DAILY_BYTES_ON_DISK_GZIPPED          = 2.651.852
```

⚠️ **A coluna "anos" abaixo é UNIÃO entre estações.** Não multiplique
estações × anos: o número real de anos-estação é a coluna "arquivos".

| Variável | código | arquivos | linhas | estações | anos (união) | quantas estações cobrem todo o intervalo |
|---|---|---|---|---|---|---|
| Precipitação | `PREC` | 232 | 82.201 | 14 | 2010-2026 | 13 de 14 |
| Bagnatura fogliare | `BFOGL` | 232 | 82.125 | 14 | 2010-2026 | 13 de 14 |
| Temperatura do ar 2 m | `TARIA2M` | 230 | 81.269 | 14 | 2010-2026 | 12 de 14 |
| Umidade relativa 2 m | `UMID2M` | 230 | 81.207 | 14 | 2010-2026 | 12 de 14 |
| Radiação solar global | `RADSOL` | 114 | 40.176 | 8 | 2010-2026 | 6 de 8 |

### ⚠️ Armadilha de leitura do campo `valore` — leia antes de parsear

O `valore` vem sempre como *texto*, mas em duas formas diferentes:

| código | formato real do `valore` |
|---|---|
| `BFOGL` | escalar — ex. `"0"`, unidade `% T` |
| `PREC` | escalar — ex. `"0.0"`, unidade `mm` |
| `RADSOL` | escalar — ex. `"25.022"`, unidade `MJ/m2` |
| `TARIA2M` | **objeto JSON dentro de uma string**: `"{\"MINIMO\":17.1,\"MEDIO\":25.5,\"MASSIMO\":32.8}"` em °C |
| `UMID2M` | **objeto JSON dentro de uma string**: `"{\"MINIMO\":30,\"MASSIMO\":72}"` em % |

⚠️ **A umidade relativa NÃO tem média diária.** Só `MINIMO` e `MASSIMO`. As
81.207 linhas de umidade são uma faixa, não uma média. Quem ler
"366.978 linhas, 100 % com valor" como 366.978 leituras diárias de cinco
variáveis vai trocar uma média por uma faixa sem perceber.

Os valores foram preservados **crus**. Nenhuma unidade convertida, nenhum campo
reinterpretado.

---

## H · ANNATE AGRARIE — com correção

```
ANNATE_AVAILABLE            = YES
ANNATE_PRESERVED            = YES
ANNATE_FILES_PRESERVED      = 26   (26 sha256 distintos, 0 duplicatas de bytes)
ANNATE_DISTINCT_SEASONS     = 25   ← CORRIGIDO (eu havia dito 26)
ANNATE_SEASON_RANGE         = 2001 … 2025
```

⚠️ **Correção do Red Team, reproduzida.** Os 26 arquivos existem e são
distintos. Mas "26 temporadas, 2000-01 a 2025" contava **rótulos de URL do
gerenciador de conteúdo**, não o que os documentos dizem. Lendo a primeira
página de cada PDF: os cinco títulos com hífen declaram cobrir
**janeiro–novembro do SEGUNDO ano apenas**. Consequência:

- `Annata agraria 2000-01` cobre **2001**, não 2000 → **a safra 2000 não está no pacote**;
- a safra **2005 é coberta por dois documentos** (o titulado `2004-05` e o titulado `2005`).

**Ainda assim isto amplia o que a Inteligência já tinha:** ela tinha 12 anos
(2014–2025); aqui há **25 temporadas desde 2001**.

⚠️ **Conteúdo lido e classificado.** As 26 Annate foram extraídas com
`pdftotext` e varridas:

```
NUMERIC_CANDIDATE           = 0
QUALITATIVE_OR_MENTION_ONLY = 24
NO_DISEASE_TERM             = 2
```

O Red Team abriu as 3 janelas que meu filtro marcou como possíveis e as três são
falso positivo. **Nenhuma Annata agraria publica número de doença.** Um adjetivo
não é medida.

### ⚠️ Os "Rapporti FAS" não são sobre doença

Também preservados: **17 Rapporti FAS (2008–2024)**. Eu os apresentei como
relatórios fitossanitários. **Não são.** O título da capa é *"Vendita di
prodotti fitosanitari nella regione Veneto"*: são as declarações anuais de
**VENDA de defensivos** feitas pelos revendedores do Veneto sob o D.Lgs
150/2012 art. 16. 16 dos 17 não contêm nenhum nome de doença em ~1,4 milhão de
caracteres.

**Composição real dos 46 documentos** (eu havia somado 45 e sobrava 1):

```
26 anuários agroclimáticos (Annate agrarie)
17 relatórios de venda de defensivos (FAS)
 1 análise geográfica das mesmas vendas
 2 planilhas de risco de modelo (ver seção J)
--
46 documentos com desfecho de doença registrado: 0
```

---

## I · ARQUIVO MENSAL AGROMETEOROLÓGICO

```
MONTHLY_ARCHIVE_STATE          = COMPLETE
MONTHLY_BULLETIN_INDEX_YEARS   = 2004 … 2025  (22 anos)
MONTHLY_BULLETINS_DISCOVERED   = 347
MONTHLY_BULLETINS_PRESERVED    = 347
MONTHLY_BULLETINS_FAILED       = 0
MONTHLY_BYTES                  = ~381,3 MB
CONTENT_VERIFIED               = 347/347 CONTENT_OK
```

Raiz: `https://www.arpa.veneto.it/temi-ambientali/agrometeo/file-e-allegati/bollettino-mese/<ano>/`

A recursão que estava travada foi corrigida: a listagem da API não traz o campo
`is_folderish`, então o rastreador não entrava nas pastas de ano. Agora ele
confia também no `@type`. **72 pastas visitadas, nenhuma listagem truncada.**

⚠️ **A maior armadilha léxica do pacote.** São boletins de *agrometeorologia*.
Eles mencionam peronospora ou oídio **155 vezes**, e exatamente **uma** dessas
menções fica perto de um número — e essa é sobre **trigo**, e a frase diz
explicitamente que as plantas estavam *sem* ataque fúngico e que os 20 % descrevem
crescimento reduzido por causas *"non fitosanitarie ma agronomiche"*.

**155 menções léxicas, 0 medições de doença.** Quem minerar "peronospora" nessa
pasta fabrica 155 observações que não existem.

---

## J · BOLETIM SEMANAL DA VINHA — duas correções

```
WEEKLY_PERONOSPORA_ARCHIVE_ARPAV           = NO
WEEKLY_PERONOSPORA_ARCHIVE_REGIONE_VENETO  = YES, mas só 3 temporadas
```

### Na ARPAV: não é arquivo, e não é observação

A pasta `agrometeo/file-e-allegati/peronospora-vite/` tem **dois arquivos de
posição fixa**, sobrescritos, sem histórico:

| Título no site | bytes | data do próprio PDF |
|---|---|---|
| Bollettino Peronospora vite (`vitimeteo.pdf`) | 44.476 | **2019-06-17** |
| Bollettino Oidio (`vitimeteo2.pdf`) | 44.073 | **2019-07-04** |

A data que o site mostra (2013/2014) é a data do *item* no gerenciador de
conteúdo. A data do documento é **2019** — confirmada três vezes dentro do
arquivo: `/Info CreationDate`, `xmp:CreateDate` e a linha impressa
*"data emissione: lunedì 17 giugno"* (o dia da semana só bate em 2019).

⚠️ **Correção maior, do Red Team.** Eu os chamei de "boletins". **Não são
observação de doença: são saída de MODELO.** A própria capa diz
*"Indicazioni di rischio — percentuali di infezione, modello Vitimeteo —
Plasmopara (versione sperimentale)"*. Uma percentagem de risco de infecção
**simulada a partir de chuva, temperatura e bagnatura fogliare** é um preditor
reescrito, não um registro de que a peronospora ocorreu em algum lugar. Nenhum
dos dois nomeia um vinhedo, uma contagem ou uma lesão observada. São avisos de
uma página que dizem que a atualização recomeça na primavera de 2020.

⚠️ E o rótulo do segundo é contraditório: o site o chama "Bollettino Oidio", mas
o `/Title` interno diz *"Bollettino infezioni peronospora"*. Qual dos dois vale
= `NOT_KNOWN`.

O Internet Archive guarda apenas **6 capturas** de `vitimeteo.pdf` (2 versões
distintas por hash, 2016 e 2018). O boletim decadal regional
(`bollettino_agrometeo_regionale_settimanale.pdf`) **nunca foi arquivado**: a
consulta CDX devolveu `[]`.

### Na Regione del Veneto: existe, mas raso

Índice provado: `https://www.regione.veneto.it/web/fitosanitario/bollettini-fitosanitari`

| Temporada | Forma | Quantidade | Estado |
|---|---|---|---|
| **2026** | PDFs no portal Liferay | 20 boletins vite (N.01 → N.20) | `DISCOVERED`; **4 amostras preservadas** |
| **2025** | PDFs num segundo host Nextcloud (`sharing.regione.veneto.it`) | 20 boletins vite (09/04 → 27/08) | `DISCOVERED`; amostras preservadas |
| **2024** | **HTML inline**, sem nenhum arquivo | 21 boletins vite | `DISCOVERED`; página HTML preservada |
| **≤ 2023** | — | — | **`NOT_KNOWN`** — não achado, e isso **não é zero provado** |

⚠️ **Restrição de robots.txt — por isso não houve coleta em massa.**
`regione.veneto.it/robots.txt` traz `Disallow: /documents/` e `crawl-delay: 10`
para `User-agent: *`; `sharing.regione.veneto.it/robots.txt` traz `Disallow: /`
para o host inteiro. Os PDFs de 2025 e 2026 vivem exatamente nesses caminhos.
**Decisão consciente: não baixar em massa.** As URLs ficam registradas como
`DISCOVERED` em `manifests/recon/F1a-veneto-search.json` e
`manifests/recon/F1b-veneto-fito.json`.

### O que o boletim semanal realmente diz

`pdftotext` (xpdf 4.06, em `/mingw64/bin/`) **lê** esses PDFs — um batedor
relatou extração bloqueada, mas era falta da ferramenta certa, não do texto.

Trecho real, `Bollettino n. 20`, temporada 2025:

> *"Peronospora e Oidio: Nell'ultimo periodo non sono stati notati sviluppi
> infettivi di rilievo di questi due patogeni."*

Temporada 2026:

> *"Patogeni: Nessuna novità di rilievo. Solo sporadiche comparse di macchie
> secondarie di Peronospora…"*

Narrativa qualitativa mais recomendação de tratamento. Sem incidência, sem número
de focos, sem parcelas monitoradas, sem severidade. **Nenhum número.**

---

## K · DEDUP

```
RAW_DISTINCT_BY_SHA256    = 1644  (entre os 1674 documentos de fonte)
RAW_DUPLICATE_CONTENT     =   29   (SAME_CONTENT_DIFFERENT_URL)
RAW_EMPTY_FILES_NOT_ZERO  =    1
DAILY:    1038 sha256 distintos em 1038 arquivos → 0 duplicatas
          (e 1038 distintos também nos payloads descomprimidos)
ANNATE:     26 sha256 distintos em  26 arquivos → 0 duplicatas
MENSAIS:   347 sha256 distintos em 347 arquivos → 0 duplicatas
```

Nenhuma duplicata foi apagada. As 29 estão marcadas
`SAME_CONTENT_DIFFERENT_URL` em `manifests/raw-file-inventory.jsonl`, com o
caminho do original. São, em quase toda parte, o mesmo boletim vite guardado por
4 batedores diferentes e os catálogos ARPAV guardados 3 vezes.

⚠️ **Duas armadilhas de contagem que o Red Team achou e que estão corrigidas:**

1. **A extensão do arquivo mentia.** 181 das 224 linhas com `ext == ".pdf"` eram
   cascas de HTML (salvas com nome `.pdf`), e **393 PDFs reais não tinham
   extensão nenhuma** (salvos como `<hash>_file`). Agora cada linha do inventário
   traz `actual_format`, lido dos **bytes mágicos**: 438 PDFs reais, 1038 gzip,
   193 HTML, 140 JSON. Filtre por `actual_format`, nunca por `ext`.
2. **`raw/F3b/bfogl_by_year/`** tem 17 arquivos com nome de ano mas só **7
   conteúdos distintos** — e nenhum deles é medição: são respostas de catálogo de
   estações (sem `dataora`, sem `valore`), guardadas com nome por ano. **Zero
   observações de bagnatura fogliare naquela pasta.**

---

## L · FALHAS E PARCIAIS

### L.1 — A falha que quase entrou no pacote como sucesso

Na primeira tentativa de baixar os PDFs da ARPAV, **os 46 arquivos vieram como
casca de HTML do site**, não como documentos. O site é Plone/Volto: uma URL
terminada em `.pdf` devolve a aplicação, não o arquivo. O endereço certo é
`.../arquivo.pdf/@@download/file`.

Pego pelos **bytes mágicos**: os "PDF" começavam com `<!doctype html>`.

- Os 182 arquivos falhos (46 docs + 136 mensais) foram movidos para
  `raw/_failed-captures/` — **não apagados**.
- Refeito com a URL certa: **46/46 e 347/347 verificados `CONTENT_OK`**.
- Prova do tamanho: as Annate somavam 9,7 MB de casca; somam **110,2 MB** reais.

### L.2 — A quebra da Lei Zero que o Red Team encontrou, e a correção

⚠️ Os manifestos `FAILED-*.jsonl` **ainda diziam `"preservation": "PRESERVED"`**
nas 182 linhas, com `media_type: text/html` e um `raw_path` que apontava para a
pasta boa, onde o arquivo já não estava. Isso é exatamente o que a Lei Zero
proíbe: **uma coleta falha rotulada como preservada.** Quem unisse
`manifests/*.jsonl` filtrando por `PRESERVED` colhia 182 documentos fantasma.

**Corrigido:** as 182 linhas agora dizem `preservation: COLLECTION_FAILED`,
`dedup: NOT_APPLICABLE_FAILED_CAPTURE`, `counts_as_preserved_document: false`,
com o `raw_path` reapontado para a quarentena e o motivo escrito. Os bytes
continuam em disco.

**Corrigido também:** os manifestos pré-verificação
(`arpav-docs-manifest.jsonl`, `arpav-monthly-manifest.jsonl`) ganharam
`superseded_by`, para que a mesma coleta não seja contada duas vezes.

### L.3 — Denominador inventado para 2026, corrigido

Os 60 arquivos de 2026 declaravam `expected_days = 365` e o estado
`PARTIAL_SOURCE_GAP`. A captura rodou em 06/09/2026 e a fonte publicou até
31/07/2026. Ou seja: **117 dos dias "faltantes" ainda não tinham acontecido**, e
chamar o resto de "falha da fonte" nomeia uma causa que não foi estabelecida.

**Corrigido para** `expected_days = dias decorridos até a captura` e o estado
`YEAR_IN_PROGRESS_PUBLICATION_LAG`.

### L.4 — Outras falhas e limites

| Item | Estado | Motivo |
|---|---|---|
| 6 batedores de reconhecimento | `NOT_COMPLETED` | sessão anterior encerrada no meio |
| `dispenser_meteo_giorno_sensore` via GET | `NOT_PROVED` | HTTP 500 com e sem parâmetros |
| Dados **horários** ARPAV | `NOT_COLLECTED` | existe, exige e-mail, máx. 5 anos/pedido |
| Boletins vite da Regione Veneto (36 restantes) | `DISCOVERED_NOT_COLLECTED` | `robots.txt` proíbe; decisão consciente |
| Boletins vite ≤ 2023 | `NOT_KNOWN` | não achado; **não é zero provado** |
| Conteúdo dos 347 boletins mensais | `NOT_CLASSIFIED` além da varredura léxica | preservado, não lido inteiro |
| Acesso **sem** VPN | `NOT_TESTED` | comparação não foi feita |
| **Xylella Puglia: 688.631 registros** | `DISCOVERED, NÃO COLETADO` | é o campo `total` da API CKAN; **5 registros em disco** |
| **Xylella positivo 5.241 / negativo 683.390** | `NOT_PRESERVED` | o arquivo que deveria prová-los é uma **página de bloqueio HTML** do `dati.puglia.it` |
| `venetoagricoltura.org/category/bollettini/` | `ROUTE_DOES_NOT_EXIST` | redireciona para a home; o site virou app Angular ("AVISP") |
| 5 hosts `coldiretti.it` | `BLOCKED` | conexão TCP derrubada |
| `provincia.treviso.it` busca | `BLOCKED` | HTTP 500 — ausência **não** provada |
| 1 arquivo vazio em `raw/F4/` | `EMPTY_FILE_NOT_ZERO` | captura falha, não medição de zero |

As alegações dos batedores que não se sustentaram **não foram apagadas**: a
correção está anexada em `_red_team_corrections` dentro de
`manifests/F6-other-pests.manifest.json`, `F5-annual-reports.json` e
`F2b-vagri-vite.json`. Leia as duas coisas.

---

## M · RED TEAM — resultado

```
LENTES              = 4 (duplicata inflada · catálogo vs dado · ano vs ano completo · tempo vs doença)
AGENTES             = 28 (4 lentes + 24 verificadores independentes)
ERROS DE EXECUÇÃO   = 0
ACHADOS BRUTOS      = 24
```

Cada achado foi entregue a um verificador independente com a instrução de
**refutá-lo**. Veredictos: `CONFIRMED` e `PARTLY_TRUE` na maioria, **4
`REFUTED`/`CANNOT_REPRODUCE`** — inclusive um caso em que o próprio texto do meu
briefing de auditoria estava errado (eu escrevi "≥ 99,4 %" no briefing quando a
entrega dizia "≥ 99,3 %"; a entrega estava certa).

**Confirmados com severidade alta, todos já corrigidos acima:**

| # | Achado | Onde ficou |
|---|---|---|
| 1 | 182 capturas falhas rotuladas `PRESERVED` — quebra da Lei Zero | L.2 |
| 2 | Cobertura conjunta: só 10 de 14 estações ≥ 99,4 % com as 4 variáveis | F |
| 3 | 7 arquivos abaixo de 50 % do ano contados como ano coletado | F |
| 4 | Annate: 25 temporadas, não 26; 2005 dobrado, 2000 ausente | H |
| 5 | Os 2 "boletins" da vinha são saída de modelo, não observação | J |
| 6 | Os 17 FAS são relatórios de venda de defensivos | H |
| 7 | Números de Xylella sem prova em disco; arquivo é página de bloqueio | L.4 |
| 8 | Denominador inventado para 2026 | L.3 |
| 9 | `years` por variável é união, não alcance de estação | G |
| 10 | Extensão do arquivo mentia sobre o conteúdo | K |
| 11 | **`OUTCOMES_NEW = nenhum` estava errado** | O |

**O que sobreviveu à auditoria, reproduzido por 3 ou 4 lentes independentes:**

- 1038 arquivos diários, 0 falhas, 1:1 com o plano em ambas as direções;
- 366.978 linhas, 100 % com valor, 0 datas duplicadas, todos os carimbos `T00:00:00`;
- 232 arquivos de bagnatura, 82.125 linhas, 14 estações de Treviso, unidade `% T`;
- 1038 sha256 distintos (também nos payloads descomprimidos);
- a janela 2014-03-01 → 2025-10-31 tem mesmo 4.263 dias;
- **nada que o catálogo ARPAV anunciava dentro do escopo ficou por coletar** — 0 combinações (sensor, ano) faltando;
- os PDFs atuais são mesmo os documentos que dizem ser;
- os números do catálogo regional (315/1619/78) **não** são apresentados como preservados;
- a API pública funciona sem chave, sem cookie e sem e-mail.

Resultado completo: `manifests/red-team-result.json`.

---

## N · READY_FOR_INTELLIGENCE

```
READY_FOR_INTELLIGENCE = PARTIAL
```

✔️ **Os preditores estão prontos e são fortes.** Série diária observada,
2010–2026, 14 estações com coordenadas, incluindo bagnatura fogliare — a
variável que mais importa para peronospora. **10 das 14 estações têm as quatro
variáveis no mesmo dia em ≥ 99,4 % da janela 2014–2025.**

❌ **Não há desfecho de doença que case com esses preditores.** Existem
desfechos numéricos reais no pacote (seção O), mas **nenhum deles cruza ao mesmo
tempo o lugar, o período e o patógeno** da série de bagnatura fogliare.

**Consequência direta:** com este pacote **não é possível fazer backtest de um
modelo de peronospora da vinha em Treviso, 2014–2025, contra observação
medida.** Converter *"sporadiche comparse"* em nota de severidade seria inventar.

---

## O · O QUE É NOVO PARA A INTELIGÊNCIA

### `PREDICTORS_NEW` — novo e provado

| Preditor | Cobertura | Onde |
|---|---|---|
| **Bagnatura fogliare observada** (`% T`, diária) | 14 estações, 2010–2026, 82.125 linhas | `raw/F4-arpav-rest/tabella/` |
| Precipitação de estação observada (`mm`) | 14 estações, 82.201 linhas | idem |
| Temperatura do ar 2 m (min/médio/máx, `°C`) | 14 estações, 81.269 linhas | idem |
| Umidade relativa 2 m (min/máx, `%` — **sem média**) | 14 estações, 81.207 linhas | idem |
| Radiação solar global (`MJ/m²`) | 8 estações, 40.176 linhas | idem |
| Coordenadas/altitude/comune | 14/14 estações | `manifests/station-geo.json` |
| **Cobertura conjunta por estação** | 14 estações | `manifests/joint-coverage.json` |

Isto é **observação de estação**, não reanálise. A bagnatura fogliare **não
existe** em reanálise: é medida por sensor.

### `OUTCOMES_NEW` — ⚠️ correção do que eu disse antes

Eu havia escrito `OUTCOMES_NEW = NENHUM`. **Estava errado.** Minha varredura só
cobriu o manifesto de documentos da ARPAV e nunca abriu as pastas F5/F6 dos
batedores. Reabri as 12 PDFs de lá e **6 têm desfecho numérico real**
(`manifests/disease-outcome-pockets.json`):

| # | Fonte | O que traz | Por que NÃO resolve a pergunta |
|---|---|---|---|
| 1 | **Piemonte, Progetti Pilota FD 2025** (`raw/F6-other-pests/piemonte-fd-progetti-pilota-monitoraggio-2025.pdf`) | **Incidência média de flavescência dourada em vinhedo, por área-piloto, por ano**: Alessandrino 2022 7,7 % · 2023 9,9 % · 2024 7,7 % · 2025 7,2 %; Canavese 3,4 / 5,0 / 2,0 / 2,9 %; Barolo & Barbaresco 6,0 / 2,4 / 1,4 % | **Piemonte, não Veneto.** Flavescência é fitoplasma transmitido por inseto, **não** fungo dirigido pelo tempo. Só 3–4 anos, resolução anual |
| 2 | **Veneto, Relazione annuale 2006–2009** (`raw/F5/`) | Tabelas do Serviço Fitossanitário: plantas-mãe controladas, hectares com giallumi, amostras, positivos FD/BN, focos. Ex. 2008: 392,66 ha controlados · 34,38 ha com giallumi · 95 amostras · 57 positivos FD · 38 BN | **2006–2009 — fora da janela 2014–2025.** E é giallumi/FD em viveiro, não peronospora em vinhedo |
| 3 | Puglia, Xylella (CKAN) | 5 registros individuais com data, espécie, comune, coordenadas e `RISULTATO` Positivo/Negativo | **5 registros preservados**, não 688.631. Puglia, oliveira |
| 4 | ERSA FVG, Halyomorpha halys | tabela semanal de armadilha por sítio | **Inseto**, não doença; Friuli, não Veneto |

**Resumo honesto:** o pacote tem o preditor na resolução de 4.263 dias e o
desfecho **em nenhuma resolução que case com ele**. Para peronospora/oídio em
Treviso, 2014-03-01 → 2025-10-31: **ZERO observações**.

### `CONTEXT_NEW` — narrativo

| Item | Cobertura | Natureza |
|---|---|---|
| Annate agrarie | 25 temporadas, 2001 → 2025 | narrativa qualitativa, 0 números de doença |
| Boletins agrometeo mensais | 347 arquivos, 2004 → 2025 | agrometeorologia; 155 menções léxicas, 0 medições |
| Boletins vite semanais (amostras) | 2024, 2025, 2026 | narrativa + recomendação |
| Planilhas de risco Vitimeteo | 2 arquivos, 2019 | **saída de modelo experimental** |
| Rapporti FAS | 17, 2008 → 2024 | venda de defensivos |

### `NEGATIVE_FINDINGS`

1. **Não existe série semanal histórica de doença da vinha publicada no Veneto.**
   O portal regional só expõe 3 temporadas (2024–2026); a ARPAV congelou o seu
   arquivo em 2019 e o que há ali é modelo, não observação.
2. **O boletim decadal agrometeo regional nunca foi arquivado** — CDX vazio.
3. **Nenhum documento oficial do Veneto preservado publica número de doença**
   para a janela de interesse. 0 de 43 varridos.
4. **`venetoagricoltura.org/category/bollettini/` não existe mais.** Qualquer
   plano que dependa dessa URL está morto.
5. **A entrega por e-mail da ARPAV é dispensável** para as 5 variáveis diárias.
6. ⚠️ Ausências que **não são zero provado**: boletins vite ≤ 2023; boletim
   agrícola da Provincia di Treviso (busca com erro 500); e as frentes dos 6
   batedores interrompidos.

---

## P · ONDE ESTÁ CADA COISA

```
pilot-disease-local-collection/
├── LOCAL-DISEASE-COLLECTION-HANDOFF.md   ← este documento
├── manifests/                            ← COMITADO
│   ├── collection-manifest.json             o pacote, todos os números
│   ├── daily-series-provenance.jsonl        1 linha por arquivo diário, ficha completa
│   ├── daily-series-recount.json            recontagem abrindo cada arquivo
│   ├── joint-coverage.json                  cobertura CONJUNTA por estação  ← leia antes de escolher estação
│   ├── disease-outcome-pockets.json         os 6 arquivos com desfecho numérico real
│   ├── disease-outcome-scan.json            classificação de desfecho por documento
│   ├── red-team-result.json                 os 24 achados e os 24 veredictos
│   ├── arpav-daily-manifest.jsonl           captura crua das 1.038 respostas
│   ├── arpav-docs-manifest.verified.jsonl   ← AUTORITATIVO (o sem .verified é superseded)
│   ├── arpav-monthly-manifest.verified.jsonl ← AUTORITATIVO
│   ├── station-geo.json                     coordenadas das 14 estações
│   ├── raw-file-inventory.jsonl             sha256 + actual_format de TODO arquivo em raw/
│   ├── recon/                               resultado dos 6 batedores que completaram
│   └── FAILED-*.jsonl                       a primeira tentativa, agora COLLECTION_FAILED
├── tools/                                ← COMITADO (scripts reproduzíveis, inclusive os da auditoria)
└── raw/                                  ← NÃO COMITADO (.gitignore)
    ├── F4-arpav-rest/tabella/*.json.gz      a série diária
    ├── F7-arpav-bollettino-mese/            347 boletins mensais
    ├── F8-arpav-agrometeo-docs/             Annate + FAS + planilhas de risco
    ├── F1*..F6*/                            material dos batedores
    └── _failed-captures/                    182 capturas falhas, em quarentena
```

`RAW_LOCATION = C:\disease-local-collection-italy\pilot-disease-local-collection\raw`
(~673,6 MB de documentos de fonte). O RAW **fica fora do Git**; o que vai para o
Git é o manifesto com URL, SHA256, bytes e caminho de cada item.

---

## Q · MENSAGEM PARA A MISSÃO DE INTELIGÊNCIA

```
LOCAL_COLLECTION_READY_FOR_RECONCILIATION = PARTIAL
```

Em uma frase: **os preditores chegaram inteiros e são melhores do que os que
vocês tinham; o desfecho de doença que casa com eles não existe, e agora está
provado — não é falta de procurar.**

O que fazer com isso:

1. **Usar** a série diária das 14 estações. **Antes de escolher estação, ler
   `manifests/joint-coverage.json`** — a cobertura por variável engana; Oderzo
   anuncia 99,86 % e vale 84,64 %.
2. **Desempacotar** `TARIA2M` e `UMID2M`, que vêm como objeto dentro de texto — e
   lembrar que **a umidade não tem média diária**.
3. **Não** tratar bagnatura fogliare como pressão de doença. É preditor.
4. **Não** usar as planilhas Vitimeteo como observação: são modelo.
5. **Não** converter os adjetivos do boletim vite em classe de severidade.
6. **Decidir conscientemente** sobre os 36 boletins vite de 2025/2026 que estão
   `DISCOVERED` mas bloqueados por `robots.txt`.
7. Se for preciso desfecho numérico, o candidato mais forte do pacote é a
   **flavescência dourada do Piemonte** (incidência anual por área-piloto,
   2022–2025) — outra doença, outra região, resolução anual. A frente que ia
   investigar isso a fundo (F6) **foi interrompida e não entregou relatório**.
