# RELATÓRIO DE DRIFT — CATÁLOGO COMERCIAL ADAMA ITÁLIA

> **51 medido contra 55 informado.** A pergunta não se resolveu escolhendo um dos
> dois números — resolveu-se medindo. E a medição respondeu uma pergunta mais
> estreita do que a que foi feita: mede **o que se consegue ler**, e o total
> oficial continua `NÃO SEI`.

```
SNAPSHOT_BEFORE   CAT_ADAMA_IT_20260830   observado 2026-08-30
SNAPSHOT_NOW      CAT_ADAMA_IT_20260915   observado 2026-09-15
DIAS ENTRE        16
CASADO POR        PRODUCT-MASTER.IDENTITY_ANCHORS (URL:)
```

---

## A RESPOSTA, EM UMA LINHA — E O QUE ELA **NÃO** DIZ

```
população comparável     COUNT_BEFORE = 51     ADDED   = 0    RENAMED_CAND. = 0
(páginas legíveis)       COUNT_NOW    = 51     REMOVED = 0    UNCHANGED     = 51
```

**Nas 51 páginas que se conseguem ler, nada mexeu em dezasseis dias.** Nem um
produto entrou, nem um saiu, nem um campo mudou. `55_PROVEN = NÃO`.

⚠️ **Isto não diz que o catálogo tem 51.**

```
OBSERVED_READABLE_PRODUCT_COUNT   = 51
CURRENT_OFFICIAL_PORTFOLIO_COUNT  = NÃO SEI
TEMPORAL_DRIFT_IN_OBSERVED_SET    = NOT_OBSERVED
TOTAL_CATALOG_TEMPORAL_DRIFT      = NÃO SEI
```

    PÁGINA LEGÍVEL OBSERVADA  ≠  CATÁLOGO OFICIAL TOTAL

A listagem oficial continua ilegível. Enquanto estiver, pode existir superfície
comercial que estas 51 não enumeram — e um produto que tenha entrado ou saído
**fora** do sitemap não apareceria em nenhuma das duas fotos, deixando a
comparação igual na mesma. O limite do instrumento não é um facto sobre o mundo.

---

## A HIPÓTESE QUE DEIXOU DE EXPLICAR — E QUE NÃO MORREU

O handoff registou-a assim, e ela era razoável:

> *«O snapshot do catálogo é de 30/08/2026; a informação humana é de 15/09.
> Quinze dias chegam para um portfólio mexer.»*

Mediram-se os quinze dias **no que se consegue ler**. Aí não mexeu nada.

```
TEMPORAL_DRIFT_IN_OBSERVED_SET  = NOT_OBSERVED
TOTAL_CATALOG_TEMPORAL_DRIFT    = NÃO SEI
HANDOFF_HYPOTHESIS              = NOT_SUPPORTED_IN_OBSERVED_SET
```

⚠️ **`NOT_SUPPORTED` não é `REFUTED`.** A hipótese continua de pé para a parte do
catálogo que permanece ilegível: o drift podia ter acontecido exactamente onde
não se olhou, e a medição sairia igual.

Isto não é um detalhe de arrumação. Enquanto a explicação temporal parecia
suficiente, a diferença entre 51 e 55 parecia um problema que o tempo resolvia
sozinho — era só voltar a coletar. **Não é.** Recoletar pelo mesmo caminho dá 51
outra vez, porque o caminho é o mesmo.

O que falta não é uma coleta. É uma superfície que se consiga ler.

---

## COMO SE CONTOU — TRÊS CAMINHOS, E UM DELES NÃO ABRE

Listagem não serve de contagem. Por isso contou-se por mais de um caminho.

| # | caminho | páginas legíveis |
|---|---|---:|
| **A** | `sitemap.xml`, a lista que a própria ADAMA publica | **51** |
| **B** | varredura de toda ligação com forma de produto dentro das 51 páginas | **51** |
| **C** | `/italia/it/products/crop-protection` — a listagem oficial | **`NÃO SEI`** |

⚠️ A coluna conta **páginas que se conseguiram ler**, não produtos do catálogo.
A e B concordam sobre o que é legível; nenhuma das duas mede o total.

**A e B concordam.** Foram obtidos por caminhos que não se conhecem: um lê o que
a ADAMA declara, o outro lê o que as páginas linkam entre si.

**C é a única superfície onde a própria ADAMA publica um número** — e é a que não
abre. O Akamai Bot Manager responde com desafio interstitial de prova-de-trabalho,
e navegar até lá devolve `Access Denied`.

```
DETECÇÃO DE ROBÔ NÃO SE CONTORNA.
```

O desafio **não** foi resolvido. É limite do trabalho, não obstáculo a vencer — e
é por isso que C fica `NÃO SEI` em vez de virar um número arredondado a partir de A.

---

## O QUE A CONTAGEM NÃO VÊ — E TEM NOME

A varredura achou duas rotas com forma de produto fora do sitemap. Nenhuma entra
nos 51, e nenhuma é «nada».

### `antigram-gold` — porta fechada

```
/italia/it/prodotti-adama/erbicidi/antigram-gold
HTTP 403 · "Accesso negato | ADAMA Italia"
ligada a partir de: 1 página (Sulcotrek®)
no registo do Ministero: NENHUMA autorização com este nome
STATE             = LINKED_BUT_NOT_READABLE
PUBLICATION_STATE = UNKNOWN
```

⚠️ **403 não prova despublicado.** Prova que este cliente, neste momento, não teve
acesso — `ERROR ≠ REJECTED`. A rota não entra na contagem porque **não foi
observada**, não porque foi observada ausente.

Estava **igual** nas duas fotos — logo não é drift observado.

### `postscript-80` — ⚠️ o `NÃO SEI` que interessa

```
/italia/it/products/crop-protection/postscript-80
HTTP 200, mas o corpo é o desafio do Akamai — o conteúdo real NÃO foi lido
ligada a partir de: 3 páginas VIVAS (Parleaf · FullPage® · Powerfilm®)
no registo do Ministero: 017585 · POSTSCRIPT 80 · ADAMA AGAN LTD
                         ADMIN_ACTIVE = true · ADAMA_PRODUCT_ID = UNKNOWN
STATE = BLOCKED_BY_BOT_PROTECTION
```

Isto é uma autorização ADAMA **viva** no Ministero, cuja página de catálogo é
citada por três produtos que estão nos 51 — e que está atrás da rota barrada.

**O que isto prova:** existe autorização ADAMA com este nome.
**O que isto NÃO prova:** que a ADAMA o lista no catálogo comercial hoje.

```
REGULATORY_PRODUCT  ≠  CATALOG_PRODUCT
```

Escrevê-lo como 52.º produto seria inventar. Deixá-lo fora sem o nomear seria
esconder. Fica declarado, com número de registo, para a missão que conseguir ler
aquela rota.

> **Nota de tamanho honesto:** `POSTSCRIPT 80` é uma das **560 autorizações sem
> produto de catálogo** que esta casa já declarava. Ela não explica sozinha a
> diferença de 4 unidades entre 51 e 55 — explica que a diferença **pode** ter
> esta forma, e que o caminho para a medir passa pela rota que o Akamai barra.

---

## O BURACO QUE ESTA MISSÃO TAPOU DE CAMINHO

`PORTFOLIO.json` nasceu do catálogo observado em **30/08/2026** — e carregava:

```
PROVENANCE.SNAPSHOT_ID = PROD_FTS_6_20260831
```

Essa é a foto do **Ministero**, de **31/08**, de **outra fonte**. O portfolio
comercial nunca tinha tido data própria: herdara a data do vizinho regulatório.

```
A DATA DO REGISTO NÃO É A DATA DO CATÁLOGO.
```

Quem lesse o portfolio concluía que ele fora observado a 31/08. Foi a 30/08, e
noutro sítio. Agora o catálogo tem o seu próprio registo de fotos,
`CATALOG-SNAPSHOTS.json`, com a fonte `IT-ADAMA-CATALOG` — e **o valor antigo não
se apagou**: vive em `REGULATORY_SNAPSHOT_ID_INHERITED`, ao lado do que o corrige.

---

## O QUE NASCEU, E O QUE NÃO SE TOCOU

| ficheiro | o que guarda |
|---|---|
| `CATALOG-SNAPSHOTS.json` | as duas fotos do catálogo, com fonte e prova próprias |
| `PORTFOLIO-OBSERVATIONS.json` | 102 observações — quem foi visto em cada foto |
| `PORTFOLIO-DRIFT.json` | o diff factual, com a contraprova das três contagens |
| `data/samples/IT-ADAMA-CATALOG/2026-09-15/` | manifesto versionado: 51 páginas com `sha256` |

```
ADAMA_PRODUCT_IDS_CHANGED = 0        PRODUCT-MASTER  não foi escrito
IDENTITY_SEAL             = PASS     PORTFOLIO.json  não foi escrito
CHANGE_ENGINE_CREATED     = NÃO      SNAPSHOTS.json  não foi escrito
PORTAL_CHANGED            = NÃO
```

O bruto das 51 páginas vive em `data/raw/`, que o Git ignora. Por isso os três
campos não se fundem num só:

```
RAW_PRESERVED                 = NÃO
METADATA_PROVENANCE_COMPLETE  = SIM
PAGE_SHA256_VERSIONED         = SIM
```

Dizer só «`PROVENANCE_COMPLETE = SIM`» lê-se como «o bruto está guardado». Não
está. O que está versionado é o `sha256` de cada página e a metadata da captura —
e esse hash chega para provar que a foto é a mesma, não para a reconstruir.

---

## O MECANISMO DE AUSÊNCIA EXISTE ANTES DE SER PRECISO

Hoje ninguém está ausente: `MEMBERSHIP_STATE` é
`PRESENT_IN_CATALOG_SNAPSHOT` nas 102 observações. O estado de ausência já está
definido, fechado e testado:

```
ABSENT_FROM_CATALOG_SNAPSHOT
  NÃO significa descontinuado. NÃO significa apagado.
  Significa: naquele dia, não estava lá.
```

Produto que saia do catálogo **sai da foto, nunca do Product Master**. Há teste
que simula a saída e exige `PRODUCT_MASTER_STATE = PRESERVED_NEVER_DELETED`.

E `RENAMED_CANDIDATE` só sai quando a âncora de identidade é a mesma e o nome
mudou — e sai como **candidato**:

```
NOME IGUAL NÃO PROVA PRODUTO IGUAL.
NOME DIFERENTE NÃO PROVA PRODUTO DIFERENTE.
```

---

## A PERGUNTA QUE FICA ABERTA

```
OBSERVED_READABLE_PRODUCT_COUNT  = 51   (dois caminhos independentes concordam)
CURRENT_OFFICIAL_PORTFOLIO_COUNT = NÃO SEI
HUMAN_REPORT                     = 55   (não provado — e NÃO refutado)
WHY_DIFFERENT                    = NÃO SEI
```

Não se sabe de onde vem o 55. O que se sabe agora, e não se sabia antes:

- **não é do tempo, no que se vê** — dezasseis dias não mexeram uma linha das 51;
- **não é do sitemap nem das ligações internas** — os dois dão as mesmas 51;
- **pode estar** na listagem oficial que não abre, ou numa superfície que ninguém
  nomeou ainda (apresentação comercial, listagem de representante, catálogo
  impresso, ou contagem que inclui autorização sem produto de catálogo).

Saber **qual superfície** produziu o 55 transforma um `NÃO SEI` numa medição de
uma tarde. Sem isso, forçar 51 para 55 apagaria exactamente o sinal que esta casa
está a aprender a ler.
